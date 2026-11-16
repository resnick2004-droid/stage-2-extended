"""EXPLORATORY (D-363): where FV3-C's accounts spend their time -- the Combine and XFA funnels and each XFA's days --
measured on the development campaign before any change is chosen (the operator, 2026-10-13: "the flip days are costing
tons of time issues with the XFAs, that's the #1 priority").

    python scripts/fv3_xfa_time_budget.py [--paths 100]

FV3-C's development gate campaign (`config/fv3_corrected_portfolio.yaml`, the run `results/fv3_corrected_v1.csv`) is
rebuilt exactly as the scorer built it -- the captures R127-R136, the walk-forward's trades of the one cell, each R's
edge and yearly bound (checked equal to the run's `gate_inputs`), the exported policy at the cell the run read -- and its
point arm (the outcomes as traded; placement off; 0 % denial) re-run through the campaign engine with the engine's own
per-trade ledger and daily account recorder switched on. **Identity first:** each re-run path's final cash, fees,
payouts, funded accounts, Combine attempts, XFAs and trades must equal `results/fv3_corrected_v1_paths.csv`'s row for
the same path (the first `--paths` paths of the run's seed sequence), or nothing is written.

Then, from the records:

* **the Combine funnel** -- attempts, passed, failed at the loss limit, closed by the policy, open at the end; days and
  trades per attempt;
* **the XFA funnel** -- activations; reached payout eligibility (5 winning days of $150+, 8284233); paid at least once;
  payouts per XFA and each payout against the $2,000 cap; how each XFA ended (loss limit, closed by the policy, open at
  the end);
* **each XFA's trading days** -- no signal routed to it; sat out by the policy (a leaf allowing no trade); a losing day;
  a winning day under $150; a qualifying winning day ($150+) -- overall and for XFAs paid and never paid;
* **accrual against survival** -- by day since activation, the share of XFAs still alive, the share that reached
  eligibility, the share paid;
* **signal supply** -- trades routed per live account-day, by account kind; the policy's leaves by share of XFA days.

It selects nothing and changes no rule: a description of the frozen candidate on development data, the input to
FV3-D's choice of levers (D-363). Writes results/fv3c_xfa_time_budget.csv with its manifest.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/fv3_xfa_time_budget.py"
CONFIG = ROOT / "config" / "fv3_corrected_portfolio.yaml"
RUN = "fv3_corrected_v1"
RESULT = "fv3c_xfa_time_budget"
DAY_CLASSES = ("no_signal", "sat_out", "losing", "win_under_min", "qualifying_win")
SINCE = (5, 10, 15, 20, 30, 40, 60, 90)
IDENTITY = ("final_cash", "fees", "payouts", "accounts_funded", "combine_attempts", "xfas", "trades")


# ------------------------------------------------------------------------------------------------- the records

def leaf_trade_caps(policy_dict: Any) -> dict[str, int | None]:
    """{leaf name: its max_trades} from a policy's `as_dict()`, walking every nested leaf (a dict with `name` and
    `risk`); a name carried by leaves with different caps maps to None (ambiguous)."""
    out: dict[str, int | None] = {}
    seen: dict[str, set] = defaultdict(set)

    def walk(o: Any) -> None:
        if isinstance(o, dict):
            if "name" in o and "risk" in o:
                seen[str(o["name"])].add(o.get("max_trades"))
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
    walk(policy_dict)
    for name, caps in seen.items():
        out[name] = next(iter(caps)) if len(caps) == 1 else None
    return out


def leaf_of(regime: Any) -> str:
    """The leaf's name from a decision's regime (`RiskPolicy.decide` joins the tree's path with ' / ', the leaf last)."""
    return str(regime).rsplit(" / ", 1)[-1]


def classify_day(traded: bool, day_pnl: float, cap: int | None, win_min: float) -> str:
    """One XFA trading day: no trade -> sat out (the policy's leaf allows none) or no signal routed; a trade -> losing,
    a win under the winning-day minimum, or a qualifying win."""
    if not traded:
        return "sat_out" if cap == 0 else "no_signal"
    if day_pnl < 0:
        return "losing"
    return "qualifying_win" if day_pnl >= win_min - 1e-9 else "win_under_min"


def xfa_rows(paths: Iterable[Any], caps: dict[str, int | None], win_min: float) -> pd.DataFrame:
    """One row per XFA of every path: its life, its days by class, when it first became eligible and was first paid,
    its payouts and how it ended."""
    rows = []
    for p, x in enumerate(paths):
        traded = {(int(r["index"]), int(r["day"])) for r in x.trades if r.get("kind") == "funded"}
        days_by = defaultdict(list)
        for r in x.account_days:
            if r.get("kind") == "funded":
                days_by[int(r["index"])].append(r)
        for f in x.funded:
            ds = sorted(days_by.get(int(f.index), []), key=lambda r: int(r["day"]))
            classes = Counter(classify_day((int(f.index), int(r["day"])) in traded, float(r["day_pnl"]),
                                           caps.get(leaf_of(r["regime"])), win_min) for r in ds)
            # trading days since the account's first day, that day counted 1: the first eligible day's position in its
            # day rows; the first payout from the engine's own count (`first_payout_day` is the day relative to the
            # account's start, 0 on its first day)
            elig = next((k + 1 for k, r in enumerate(ds) if r.get("eligible")), None)
            a = int(f.activation_day)
            end = ("open_at_end" if f.ended_on is None else "closed_by_policy" if f.abandoned
                   else "loss_limit" if f.closed else "other")
            rows.append({"path": p, "index": int(f.index), "activation_day": a,
                         "life_days": len(ds), "trades": int(f.trades), "n_payouts": int(f.n_payouts),
                         "first_eligible_after": float(elig) if elig is not None else np.nan,
                         "first_paid_after": float(int(f.first_payout_day) + 1) if int(f.n_payouts) > 0 else np.nan,
                         "payout_cash": tuple(float(c) for c in f.payout_cash), "end": end,
                         **{c: int(classes.get(c, 0)) for c in DAY_CLASSES}})
    return pd.DataFrame(rows)


def combine_rows(paths: Iterable[Any]) -> pd.DataFrame:
    rows = []
    for p, x in enumerate(paths):
        for c in x.combines:
            end = ("passed" if c.passed else "closed_by_policy" if getattr(c, "abandoned_by_policy", False)
                   else "loss_limit" if c.failed else "open_at_end")
            rows.append({"path": p, "index": int(c.index), "days": int(c.days), "trades": int(c.trades), "end": end})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------- the tables

def summarise(x: pd.DataFrame, cmb: pd.DataFrame, paths: list, cap: float) -> list[dict]:
    n_paths = len(paths)
    out: list[dict] = []
    att = len(cmb)
    for end in ("passed", "loss_limit", "closed_by_policy", "open_at_end"):
        k = cmb[cmb["end"] == end]
        out.append({"section": "combine_funnel", "measure": end, "per_path": len(k) / n_paths,
                    "share": len(k) / att if att else np.nan,
                    "days_median": float(k["days"].median()) if len(k) else np.nan,
                    "trades_median": float(k["trades"].median()) if len(k) else np.nan})
    out.append({"section": "combine_funnel", "measure": "attempts", "per_path": att / n_paths, "share": 1.0,
                "days_median": float(cmb["days"].median()) if att else np.nan,
                "trades_median": float(cmb["trades"].median()) if att else np.nan})
    nx = len(x)
    elig, paid = x["first_eligible_after"].notna(), x["n_payouts"] > 0
    for name, mask in (("activated", np.ones(nx, bool)), ("reached_eligibility", elig.to_numpy()),
                       ("paid_at_least_once", paid.to_numpy())):
        k = x[mask]
        out.append({"section": "xfa_funnel", "measure": name, "per_path": len(k) / n_paths,
                    "share": len(k) / nx if nx else np.nan,
                    "days_median": float(k["life_days"].median()) if len(k) else np.nan})
    for end in ("loss_limit", "closed_by_policy", "open_at_end", "other"):
        k = x[x["end"] == end]
        out.append({"section": "xfa_end", "measure": end, "per_path": len(k) / n_paths,
                    "share": len(k) / nx if nx else np.nan,
                    "days_median": float(k["life_days"].median()) if len(k) else np.nan,
                    "share_paid": float((k["n_payouts"] > 0).mean()) if len(k) else np.nan})
    for name, mask in (("all", np.ones(nx, bool)), ("paid", paid.to_numpy()), ("never_paid", ~paid.to_numpy())):
        k = x[mask]
        tot = float(k[list(DAY_CLASSES)].to_numpy().sum())
        row = {"section": "xfa_days", "measure": name, "xfas": int(len(k)), "days": tot,
               "days_per_xfa": tot / len(k) if len(k) else np.nan}
        for c in DAY_CLASSES:
            row[f"share_{c}"] = float(k[c].sum()) / tot if tot else np.nan
        out.append(row)
    for name, col in (("first_eligible_after", "first_eligible_after"), ("first_paid_after", "first_paid_after")):
        v = x[col].dropna()
        out.append({"section": "xfa_timing", "measure": name, "n": int(len(v)),
                    "p10": float(v.quantile(0.1)) if len(v) else np.nan,
                    "median": float(v.median()) if len(v) else np.nan,
                    "p90": float(v.quantile(0.9)) if len(v) else np.nan})
    for k_ in SINCE:
        out.append({"section": "accrual", "measure": f"day {k_}", "since_activation": k_,
                    "share_alive": float((x["life_days"] >= k_).mean()) if nx else np.nan,
                    "share_eligible_by": float((x["first_eligible_after"] <= k_).mean()) if nx else np.nan,
                    "share_paid_by": float((x["first_paid_after"] <= k_).mean()) if nx else np.nan})
    pays = np.array([c for t in x["payout_cash"] for c in t], float)
    out.append({"section": "payouts", "measure": "all", "n": int(len(pays)),
                "per_paid_xfa": float(len(pays) / paid.sum()) if paid.sum() else np.nan,
                "median": float(np.median(pays)) if len(pays) else np.nan,
                "mean": float(pays.mean()) if len(pays) else np.nan,
                "share_at_cap": float((pays >= cap - 0.5).mean()) if len(pays) else np.nan, "cap": cap})
    for kind in ("combine", "funded"):
        live = sum(1 for xx in paths for r in xx.account_days if r.get("kind") == kind)
        tr = sum(1 for xx in paths for r in xx.trades if r.get("kind") == kind)
        out.append({"section": "signal_supply", "measure": kind, "account_days": live, "trades": tr,
                    "trades_per_account_day": tr / live if live else np.nan})
    leaves = Counter(leaf_of(r["regime"]) for xx in paths for r in xx.account_days if r.get("kind") == "funded")
    tot = sum(leaves.values())
    for name, n in leaves.most_common(12):
        out.append({"section": "xfa_leaves", "measure": name, "days": n, "share": n / tot if tot else np.nan})
    multi = [int((np.asarray(xx.breaches_per_day) >= 2).sum()) for xx in paths]
    out.append({"section": "clusters", "measure": "days_with_2plus_loss_limits", "per_path": float(np.mean(multi))})
    return out


# ------------------------------------------------------------------------------------------------------ main

def rebuild_trades(cfg: dict):
    """(the gate's trades, its day set, the micro's tick value) exactly as `score_fv3_grid.main` built them, each R's
    edge, yearly bound and count checked equal to the run's `gate_inputs` (D-365 uses it per period)."""
    t, days, tv, _ = _rebuild(cfg)
    return t, days, tv


def rebuild(cfg: dict):
    """The development gate's blocks, stats and policy exactly as `score_fv3_grid.main` built them."""
    import score_fv3_grid as gf

    t, days, tv, stats = _rebuild(cfg)
    menu = [float(R) for R in gf.rr_menu(cfg)]
    f = gf.fidelity_of(cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, menu, require_sides=bool(f.get("cross_account_rule", False)),
                                    require_exits=bool(f.get("hold_to_own_exit", False)))
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    policy, _, pid = gf.policy_for_edge(cfg, stats[float(cfg["state_policy"]["fresh"]["funded_rr"])]["lb"])
    run = read_result(RESULTS_DIR / f"{RUN}.csv")
    if set(run[run["section"] == "gate"]["policy_id"].astype(str)) != {pid}:
        raise SystemExit(f"REFUSED: the policy cell {pid} is not {RUN}.csv's.")
    return blocks, stats, policy, tv


def _rebuild(cfg: dict):
    from propedge import RESULTS_DIR
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    import score_fv3_grid as gf
    import score_orb5_grid as g5

    sig, ses, _, sessions = gf.load(RESULTS_DIR, ROOT / "runs", cfg)
    fm, q = FillModel.load("assumed"), params("NQ")
    tv = q["micro_tick"] * q["micro_point_value"]
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]), tv,
                    cfg["ladder"])
    fresh = cfg["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    ev = gf.EvaluatedFV3(S, ses, cfg, sessions, read_result(BAND_FILE), float(need))
    wf_first = int(cfg["selection"]["walkforward"].get("first_test_year", gf.WF_FIRST))
    sels = {int(T): ev.select(ev.years < T)[0] for T in ev.years if T >= wf_first}
    kf, _ = ev.select(np.ones(len(ev.years), bool))
    t = gf.gate_trades(S, ev, sels, ev.cells[kf])
    menu = [float(R) for R in gf.rr_menu(cfg)]
    stats = {}
    for R in menu:
        v = t[f"r_{R:g}"].dropna()
        by = v.groupby(t.loc[v.index, "year"]).mean()
        stats[R] = {"e": float(v.mean()), "lb": g5.bound(by), "n": int(len(v))}
    run = read_result(RESULTS_DIR / f"{RUN}.csv")
    gi = run[run["section"] == "gate_inputs"]
    for R in menu:
        r = gi[gi["rr"].astype(float) == R].iloc[0]
        if stats[R]["n"] != int(float(r["oos_trades"])) or not np.isclose(stats[R]["e"], float(r["e"]), atol=1e-9) \
                or not np.isclose(stats[R]["lb"], float(r["lb"]), atol=1e-9):
            raise SystemExit(f"REFUSED: the rebuilt trades at R = {R:g} differ from {RUN}.csv's gate inputs.")
    days = sorted(d for d in set(ses["date"]) if int(d[:4]) >= wf_first)
    return t, days, tv, stats


def campaign(cfg: dict, blocks, stats, policy, tv: float, n_paths: int):
    """The gate's point arm at 0 % denial, placement off, as `gate.run_gate` runs it -- with the engine's records on."""
    from propedge.campaign.lockstep import ConductModel, simulate_lockstep_campaign
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.protocols import Protocol
    from propedge.campaign.shared_days import SharedDayDraws
    from propedge.contract.payout_timing import DEFAULT_PAYOUT_TIMING

    import score_fv3_grid as gf

    camp, fresh, f = cfg["gate"]["campaign"], cfg["state_policy"]["fresh"], gf.fidelity_of(cfg)
    protocol = Protocol(name="fv3", combine_rr=float(fresh["combine_rr"]), combine_risk=float(fresh["combine_risk"]),
                        funded_rr=float(fresh["funded_rr"]), funded_risk=float(fresh["funded_risk"]),
                        trades_per_day=gf.MAX_PER_DAY, payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                        max_concurrent_accounts=int(camp["accounts"]), family="fv3", source="config/fv3_grid.yaml",
                        note="FV3's gate under the state policy (D-290)", params=gf.protocol_params(cfg))
    sizing = gf.sizing_rule(cfg, tv)

    def draws(s):
        sd = SharedDayDraws({0: list(blocks)}, protocol=protocol, seed=s, mode=camp["mode"], sizing=sizing,
                            settlement=camp["settlement"], markets=None, route_able=(f["routing"] == "able"),
                            cross_account=bool(f.get("cross_account_rule", False)), flip=None,
                            hold_to_own_exit=bool(f.get("hold_to_own_exit", False)))
        return tuple(sd.lockstep_kwargs().values())

    _, paths = simulate_lockstep_campaign(
        protocol, edge=0.0, seed=int(cfg["seeds"]["gate"]), rules=rules_for_method(camp["payout_method"]),
        initial_bankroll=gf.bankroll_of(cfg), horizon_days=int(camp["horizon_days"]), n_paths=int(n_paths),
        payout_method="aeropay", max_concurrent_accounts=int(camp["accounts"]),
        max_concurrent_combines=int(camp["combines"]), max_total_accounts=int(camp["accounts"]),
        require_verified_cap=False, ledger=None, conduct=ConductModel(rtp=False, enforcement_p=0.0),
        risk_policy=policy, draw_factories_for_path=draws, payout_timing=DEFAULT_PAYOUT_TIMING,
        record_trades=True, record_days=True)
    return paths


def identity(paths: list, recorded: pd.DataFrame) -> pd.DataFrame:
    """Each re-run path against the run's recorded path of the same index (the point arm, 0 %, placement off)."""
    from propedge.campaign.portfolio import slot_use

    rec = recorded[(recorded["run"] == "gate placement off") & (recorded["shift"] == "point")
                   & np.isclose(recorded["enforcement_p"].astype(float), 0.0)].set_index("path")
    rows = []
    for i, x in enumerate(paths):
        p, su = x.path, slot_use(x)
        tbd = getattr(p, "trades_by_day", ())
        mine = {"final_cash": float(p.final_cash), "fees": float(p.total_fees), "payouts": float(p.total_payouts),
                "accounts_funded": int(p.accounts_funded), "combine_attempts": int(su["combine_attempts"]),
                "xfas": int(su["xfas"]), "trades": int(sum(tbd)) if len(tbd) else None}
        r = rec.loc[i]
        rows.append({"path": i, **{f"{k}_rerun": v for k, v in mine.items()},
                     "equal": all(np.isclose(float(mine[k]), float(r[k]), rtol=0, atol=0.005) for k in IDENTITY)})
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.contract.rules import load_rules
    from propedge.reporting.results import read_result, write_result

    import score_fv3_grid as gf

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=100, help="the first N paths of the run's seed sequence (memory)")
    a = ap.parse_args(argv)
    cfg = gf.config(CONFIG)
    print("rebuilding the development gate...")
    blocks, stats, policy, tv = rebuild(cfg)
    print(f"re-running {a.paths} paths with the engine's records on...")
    paths = campaign(cfg, blocks, stats, policy, tv, a.paths)
    idt = identity(paths, read_result(RESULTS_DIR / f"{RUN}_paths.csv"))
    if not idt["equal"].all():
        bad = idt[~idt["equal"]]["path"].tolist()
        raise SystemExit(f"REFUSED: the re-run differs from {RUN}_paths.csv on paths {bad[:10]}; nothing written.")
    led = load_rules()
    win_min, cap = float(led.value("xfa_std_winning_day_min")), float(led.value("xfa_std_cap"))
    caps = leaf_trade_caps(policy.as_dict())
    x, cmb = xfa_rows(paths, caps, win_min), combine_rows(paths)
    rows = [{"section": "identity", "measure": "paths_equal", "n": int(len(idt)), "per_path": float(idt["equal"].mean()),
             "fields": ",".join(IDENTITY)}] + summarise(x, cmb, paths, cap)
    ambiguous = sorted(k for k, v in caps.items() if v is None)
    rows.append({"section": "notes", "measure": "leaf_caps",
                 "fields": f"{len(caps)} leaves; ambiguous names {ambiguous[:5]}" if ambiguous else f"{len(caps)} leaves"})
    out = pd.DataFrame(rows)
    write_result(out, RESULT, script=SCRIPT, seed=int(cfg["seeds"]["gate"]), exploratory=True, results_dir=results_dir,
                 parameters={"config": "config/fv3_corrected_portfolio.yaml", "run": f"results/{RUN}.csv",
                             "arm": "point, enforcement 0, placement off", "paths": int(a.paths),
                             "winning_day_min": win_min, "payout_cap": cap, "decision": "D-363"},
                 notes={"status": "EXPLORATORY: a description of the frozen candidate on development data; selects "
                                  "nothing (D-363)"},
                 description="EXPLORATORY: FV3-C's development campaign, re-run identically with the engine's records "
                             "on -- the Combine and XFA funnels, each XFA's days by class, accrual against survival, "
                             "payouts against the cap, signal supply (D-363).")
    pd.set_option("display.width", 220)
    print(out.dropna(axis=1, how="all").to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
