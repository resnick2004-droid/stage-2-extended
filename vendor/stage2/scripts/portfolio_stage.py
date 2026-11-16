"""D-304 and D-305's portfolio stage for a screen's gate: the twins, the portfolio walk-forward and the kill lines on
the campaign's cash. Used by a scorer whose config carries a `portfolio` block; a config without one runs as before.

    portfolio:
      fixed_legs: {combine_rr: 1.0, combine_risk: 1500, funded_rr: 1.5, funded_risk: 1000}   # stage one's geometry
      walkforward_paths: 200             # resampled paths per test year (P1)
      margin: 49.0                       # one Combine's subscription: the required bankroll is the deepest loss plus it
      block_days: 21
      break_even_denial_min: 0.25        # P3
      gate_denial_still_positive: 0.10   # P3: the gate's median log growth above zero at this denial rate too
      realised_to_intended_min: 0.9      # P4
      day_set_start: "2020-01-01"        # P4: no day before it in the day set

The lines (D-304, D-305), every number per resampled path and read as the median across paths:

* P1 -- the portfolio walk-forward: each test year's out-of-sample trades, under the full protocol, resampled within
  the year; the one-sided 95 % t bound of the yearly median log growth above zero; and the activity line in every
  year -- the median path's Wilson bound of its share of days traded above one half, and no path whose campaign
  Sharpe changes sign when its idle 21-day blocks are left out;
* P2 -- the D-145 gate as it stands: the gate row's median log growth above zero;
* P3 -- fragility: the median path's break-even denial rate at least the config's, and the gate's lower-bound arm
  still above zero at the stated denial rate;
* P4 -- fidelity: realised risk at least the config's share of intended across the gate's paths, and the day set
  starting no earlier than declared.

The twins ride beside: the zero-edge twin (the same policy on the same trades with every R's outcomes shifted so the
per-trade edge is zero -- what the contract pays anyone) and the fixed-legs twin (the same trades under the fixed
legs -- the state policy's contribution), each as traded, placement off, 0 % denial.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import score_fv3_grid as gf  # noqa: E402
import score_orb5_grid as g5  # noqa: E402
from propedge.campaign import gate, portfolio as pf  # noqa: E402
from propedge.campaign.gate import shifted_blocks  # noqa: E402
from propedge.campaign.payout_method import rules_for_method  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy  # noqa: E402

def composed_hook(pcfg: dict, trial_sharpes: Sequence[float] | None = None, sink: list | None = None) -> Callable:
    """The portfolio measures as gate-row columns, plus realised over intended risk across the run's paths -- against
    the raw intention and (D-306) against the allowance-capped one -- and the share of sized trades closed at the
    Combine's need to pass. With `sink` (D-310) every path of every run is appended to it: its cash, fees, payouts,
    ruin, drawdown, trades and `portfolio.path_measures` on the run's capital base, labelled by `hook.state["label"]`
    (the caller names each run), so the measures and the lines can be re-derived from the record."""
    margin = float(pcfg.get("margin", pf.DEFAULT_MARGIN))
    block = int(pcfg.get("block_days", pf.BLOCK_DAYS))
    base = pf.hook(margin=margin, block=block, trial_sharpes=trial_sharpes)
    state = {"label": ""}

    def _hook(shift: str, p: float, paths: Sequence[Any]) -> dict[str, float]:
        out = base(shift, p, paths)
        intended = float(sum(x.path.intended_risk_total for x in paths))
        capped = float(sum(getattr(x.path, "intended_capped_risk_total", 0.0) for x in paths))
        realised = float(sum(x.path.realised_risk_total for x in paths))
        sized = int(sum(x.path.trades_sized for x in paths))
        out["pf_realised_to_intended"] = realised / intended if intended > 0 else float("nan")
        out["pf_realised_to_intended_capped"] = realised / capped if capped > 0 else float("nan")
        out["pf_share_need_exits"] = (float(sum(getattr(x.path, "trades_need_exits", 0) for x in paths)) / sized
                                      if sized else float("nan"))
        # D-339: the flip stream's brackets per path, so the lines' record carries both streams' counts
        out["pf_funded_flips"] = (float(np.mean([getattr(x.path, "funded_flips", 0) for x in paths])) if len(paths)
                                  else float("nan"))
        # D-329: the efficiency measures -- cash per slot-day and the slot-days each account kind consumed, with the
        # shares the policy abandoned -- from each path's account records (on the LockstepPath `x`, not its summary
        # `x.path`), so the rent the table charges (lambda*) is checked against what the campaign did
        eff = [slot_use(x) for x in paths]
        sd = np.array([e["slot_days"] for e in eff], float)
        net = np.array([float(x.path.final_cash) - float(x.path.initial_bankroll) for x in paths])
        rate = np.where(sd > 0, net / np.where(sd > 0, sd, 1.0), np.nan)
        out["pf_cash_per_slot_day_mean"] = float(np.nanmean(rate)) if np.isfinite(rate).any() else float("nan")
        out["pf_cash_per_slot_day_p50"] = float(np.nanmedian(rate)) if np.isfinite(rate).any() else float("nan")
        att = float(sum(e["combine_attempts"] for e in eff))
        nx = float(sum(e["xfas"] for e in eff))
        out["pf_slot_days_per_attempt"] = float(sum(e["combine_slot_days"] for e in eff)) / att if att else float("nan")
        out["pf_slot_days_per_xfa"] = float(sum(e["xfa_slot_days"] for e in eff)) / nx if nx else float("nan")
        out["pf_share_combines_abandoned"] = float(sum(e["combines_abandoned"] for e in eff)) / att if att else float("nan")
        out["pf_share_xfa_abandoned"] = float(sum(e["xfas_abandoned"] for e in eff)) / nx if nx else float("nan")
        if sink is not None:
            cap = pf.required_bankroll(paths, margin)["required_p90"]
            if not np.isfinite(cap) or not cap > 0:
                cap = max(margin, 1.0)
            for i, x in enumerate(paths):
                pth = x.path
                tbd = getattr(pth, "trades_by_day", ())
                m = pf.path_measures(pth.cash_series, pth.initial_bankroll, cap, pth.total_fees, pth.total_payouts,
                                     tbd if len(tbd) else None, block)
                sink.append({"run": state["label"], "shift": shift, "enforcement_p": float(p), "path": i, "base": float(cap),
                             "initial_bankroll": float(pth.initial_bankroll), "final_cash": float(pth.final_cash),
                             "fees": float(pth.total_fees), "payouts": float(pth.total_payouts), "ruined": bool(pth.ruined),
                             "ruin_day": pth.ruin_day, "days": int(len(pth.cash_series)),
                             "trades": int(sum(tbd)) if len(tbd) else None, "trades_sized": int(pth.trades_sized),
                             "trades_need_exits": int(getattr(pth, "trades_need_exits", 0)),
                             "funded_flips": int(getattr(pth, "funded_flips", 0)),              # D-339
                             "funded_flips_won": int(getattr(pth, "funded_flips_won", 0)),
                             "intended_risk": float(pth.intended_risk_total),
                             "intended_capped_risk": float(getattr(pth, "intended_capped_risk_total", 0.0)),
                             "realised_risk": float(pth.realised_risk_total), "accounts_funded": int(pth.accounts_funded),
                             "attempts_started": int(pth.attempts_started), "days_to_first_payout": pth.days_to_first_payout,
                             **eff[i],                                             # D-329: the slot use per path
                             **{k: v for k, v in m.items() if not isinstance(v, np.ndarray)}})
        return out
    _hook.state = state                      # type: ignore[attr-defined]
    return _hook


slot_use = pf.slot_use                   # D-329: lives in propedge.campaign.portfolio (the Studio reads it too)


def _label(hook: Callable | None, text: str) -> None:
    """Name the next run in the per-path record (a hook without a sink ignores it)."""
    if hook is not None and hasattr(hook, "state"):
        hook.state["label"] = text


def protocol_of(cfg: dict) -> Protocol:
    camp, fresh = cfg["gate"]["campaign"], cfg["state_policy"]["fresh"]
    return Protocol(name="fv3", combine_rr=float(fresh["combine_rr"]), combine_risk=float(fresh["combine_risk"]),
                    funded_rr=float(fresh["funded_rr"]), funded_risk=float(fresh["funded_risk"]),
                    trades_per_day=gf.MAX_PER_DAY, payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                    max_concurrent_accounts=int(camp["accounts"]), family="fv3", source="config/fv3_grid.yaml",
                    note="the portfolio stage (D-304)",
                    params=gf.protocol_params(cfg))                    # D-306, D-313


def _by(stats: dict, key: str) -> dict[float, float]:
    return {float(k): float(v[key]) for k, v in stats.items()}


def fixed_legs_policy(pcfg: dict) -> RiskPolicy:
    f = pcfg["fixed_legs"]
    return RiskPolicy(id="fixed_legs_twin", description="stage one's fixed legs (D-304's fixed-legs twin)", root=Phase(
        combine=Leaf(f"combine ${float(f['combine_risk']):,.0f} {float(f['combine_rr']):g}R", risk=float(f["combine_risk"]),
                     rr=float(f["combine_rr"]), max_trades=1),
        funded=Leaf(f"funded ${float(f['funded_risk']):,.0f} {float(f['funded_rr']):g}R", risk=float(f["funded_risk"]),
                    rr=float(f["funded_rr"]), max_trades=1)))


def zero_edge_blocks(blocks: Sequence[Any], e_by: dict[float, float], funded_rr: float) -> list[Any]:
    """Every R's outcomes shifted so the per-trade edge is exactly zero (the block P&L by the funded R's edge)."""
    return shifted_blocks(blocks, -float(e_by[float(funded_rr)]), {k: -float(e_by[k]) for k in e_by})


def run_campaign(blocks: Sequence[Any], cfg: dict, seed: int, tick_value: float, policy: Any, *, e: float, lb: float,
                 e_by: dict[float, float], lb_by: dict[float, float], levels: Sequence[float], n_paths: int,
                 horizon: int, hook: Callable | None, rtp: bool = False) -> pd.DataFrame:
    camp = cfg["gate"]["campaign"]
    df, _ = gate.run_gate(
        list(blocks), e=e, lb=lb, protocol=protocol_of(cfg), bankroll=gf.bankroll_of(cfg), horizon_days=int(horizon),
        n_paths=int(n_paths), seed=int(seed), accounts=int(camp["accounts"]), sizing=gf.sizing_rule(cfg, tick_value),
        rules=rules_for_method(camp["payout_method"]), mode=camp["mode"], settlement=camp["settlement"],
        combines=int(camp["combines"]), total_accounts=int(camp["accounts"]), risk_policy=policy,
        e_by_rr=e_by, lb_by_rr=lb_by, levels=tuple(levels), path_hook=hook, rtp=rtp,
        routing=gf.fidelity_of(cfg)["routing"],                         # D-318
        cross_account=bool(gf.fidelity_of(cfg).get("cross_account_rule", False)),   # D-339: the firm's rule, declared
        flip=gf.flip_spec_of(cfg),                                      # D-339: the flip stream, declared
        hold_to_own_exit=bool(gf.fidelity_of(cfg).get("hold_to_own_exit", False)))   # D-351
    df["placement"] = "on" if rtp else "off"
    return df


def twins(blocks: Sequence[Any], stats: dict, cfg: dict, seed: int, tick_value: float, policy: Any,
          hook: Callable | None) -> list[dict]:
    """The zero-edge and fixed-legs twins, as traded (the point arm), placement off, 0 % denial."""
    camp = cfg["gate"]["campaign"]
    fr = float(cfg["state_policy"]["fresh"]["funded_rr"])
    e_by, lb_by = _by(stats, "e"), _by(stats, "lb")
    rows = []
    zero = {k: 0.0 for k in e_by}
    for name, blk, pol, eb, lbb in (("zero_edge", zero_edge_blocks(blocks, e_by, fr), policy, zero, zero),
                                    ("fixed_legs", list(blocks), fixed_legs_policy(cfg["portfolio"]), e_by, lb_by)):
        _label(hook, f"twin {name}")
        df = run_campaign(blk, cfg, seed, tick_value, pol, e=eb[fr], lb=lbb[fr], e_by=eb, lb_by=lbb, levels=(0.0,),
                          n_paths=int(camp["n_paths"]), horizon=int(camp["horizon_days"]), hook=hook)
        r = df[df["shift"] == "point"].iloc[0]
        rows.append({"section": "twin", "twin": name, **{k: v for k, v in r.items() if not isinstance(v, (list, dict))},
                     "is_gate_row": False})
    return rows


def walkforward_campaigns(t: pd.DataFrame, ses: pd.DataFrame, cfg: dict, seed: int, tick_value: float, policy: Any,
                          stats: dict, hook: Callable | None) -> list[dict]:
    """P1: each test year's out-of-sample trades as their own campaign, resampled within the year (point arm)."""
    fr = float(cfg["state_policy"]["fresh"]["funded_rr"])
    e_by, lb_by = _by(stats, "e"), _by(stats, "lb")
    n_paths = int(cfg["portfolio"].get("walkforward_paths", 200))
    rows = []
    all_days = sorted(set(ses["date"].astype(str)))
    for y in sorted(set(int(v) for v in t["year"])):
        days = [d for d in all_days if int(d[:4]) == y]
        ty = t[t["year"] == y]
        if not days or not len(ty):
            rows.append({"section": "portfolio_walkforward", "test_year": y, "median_log_growth": float("nan")})
            continue
        blocks, _ = gf.gate_blocks(ty, days, tick_value, list(e_by),
                                   require_sides=bool(gf.fidelity_of(cfg).get("cross_account_rule", False)),   # D-348
                                   require_exits=bool(gf.fidelity_of(cfg).get("hold_to_own_exit", False)))     # D-351
        _label(hook, f"walkforward {y}")
        df = run_campaign(blocks, cfg, seed, tick_value, policy, e=e_by[fr], lb=lb_by[fr], e_by=e_by, lb_by=lb_by,
                          levels=(0.0,), n_paths=n_paths, horizon=len(days), hook=hook)
        r = df[df["shift"] == "point"].iloc[0]
        rows.append({"section": "portfolio_walkforward", "test_year": y, "days": len(days), "trades": int(len(ty)),
                     **{k: v for k, v in r.items() if not isinstance(v, (list, dict))}, "is_gate_row": False})
    return rows


def kill_lines(gate_df: pd.DataFrame, wf_rows: list[dict], cfg: dict, day_set_first: str,
               idle_years: Sequence[int] = ()) -> tuple[dict[str, bool], dict[str, float]]:
    """P1 to P4 from the gate rows (both placements) and the portfolio walk-forward rows; the values beside. P4 reads
    realised over the raw intention, or (D-306: `fidelity.intended: capped`) over the allowance-capped one, with the
    other reported beside; `idle_years` (D-310, D-304's 'no idle years'): the years of the gate's day set with no gate
    trade, any of which fails P4."""
    pcfg = cfg["portfolio"]
    idle = sorted(int(y) for y in idle_years)
    capped = gf.fidelity_of(cfg)["intended"] == "capped"
    off = gate_df[gate_df["placement"].astype(str) == "off"]
    g = off[off["is_gate_row"].astype(str) == "True"].iloc[0]
    d10 = float(pcfg.get("gate_denial_still_positive", 0.10))
    g10 = off[(off["shift"] == "lower_bound") & (np.isclose(off["enforcement_p"].astype(float), d10))]
    wf = pd.DataFrame(wf_rows)
    # D-312: with the bankroll an output, every growth line reads the median path's growth on the bankroll the run itself
    # needed (its required bankroll at p90, a year's rate); with a stated bankroll, the campaign's median log growth
    out_mode = gf.bankroll_output(cfg)
    gcol = "pf_growth_on_base_p50" if out_mode else "median_log_growth"
    growth = wf[gcol].astype(float) if gcol in wf else pd.Series(dtype=float)
    p1_bound = g5.bound(growth) if len(growth) else float("nan")
    act = wf["pf_activity_bound_p50"].astype(float) if "pf_activity_bound_p50" in wf else pd.Series(dtype=float)
    flips = wf["pf_share_sharpe_sign_changed_without_idle"].astype(float) if "pf_share_sharpe_sign_changed_without_idle" in wf else pd.Series(dtype=float)
    values = {
        "growth_basis": "the required bankroll at p90 (D-312)" if out_mode else "the stated bankroll",
        "P1_bound": float(p1_bound), "P1_years": int(len(growth)), "P1_years_positive": int((growth > 0).sum()) if len(growth) else 0,
        "P1_activity_min_bound": float(act.min()) if len(act) else float("nan"),
        "P1_idle_flip_share_max": float(flips.max()) if len(flips) else float("nan"),
        "P2_median_log_growth": float(g.get(gcol, float("nan"))),
        "P2_ruin": float("nan") if out_mode else float(g["ruin_probability"]),
        "P2_required_p50": float(g.get("pf_required_p50", float("nan"))),
        "P2_required_p90": float(g.get("pf_required_p90", float("nan"))),
        "P2_required_p99": float(g.get("pf_required_p99", float("nan"))),
        "P2_required_worst": float(g.get("pf_required_worst", float("nan"))),
        "P3_break_even_denial": float(g.get("pf_break_even_denial_p50", float("nan"))),
        "P3_gate_at_denial": float(g10[gcol].iloc[0]) if len(g10) and gcol in g10 else float("nan"),
        "P4_realised_to_intended": float(g.get("pf_realised_to_intended_capped" if capped else "pf_realised_to_intended",
                                               float("nan"))),
        "P4_intended": "capped" if capped else "raw",
        "P4_realised_to_intended_raw": float(g.get("pf_realised_to_intended", float("nan"))),
        "P4_realised_to_intended_capped": float(g.get("pf_realised_to_intended_capped", float("nan"))),
        "P4_share_need_exits": float(g.get("pf_share_need_exits", float("nan"))),
        "P4_day_set_first": day_set_first,
        "P4_idle_years": ",".join(str(y) for y in idle),
    }
    lines = {
        "P1": bool(np.isfinite(p1_bound) and p1_bound > 0 and len(act) and (act > 0.5).all() and (flips == 0).all()),
        "P2": bool(np.isfinite(values["P2_median_log_growth"]) and values["P2_median_log_growth"] > 0),
        "P3": bool(np.isfinite(values["P3_break_even_denial"]) and values["P3_break_even_denial"] >= float(pcfg["break_even_denial_min"])
                   and np.isfinite(values["P3_gate_at_denial"]) and values["P3_gate_at_denial"] > 0),
        "P4": bool(np.isfinite(values["P4_realised_to_intended"]) and values["P4_realised_to_intended"] >= float(pcfg["realised_to_intended_min"])
                   and str(day_set_first) >= str(pcfg["day_set_start"]) and not idle),
    }
    return lines, values


__all__ = ["composed_hook", "protocol_of", "fixed_legs_policy", "zero_edge_blocks", "run_campaign", "twins",
           "walkforward_campaigns", "kill_lines"]
