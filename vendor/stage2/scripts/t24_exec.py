"""T24 (D-432): the execution-model screen -- EXPLORATORY. Coin-flip trades from T24's capture (R149-R151, D-428),
five bars after each fixed time, each at the bracket its time can resolve, strictly one trade at a time, through five
accounts under the operator's growth-then-flip plans and FV3-C's table, in the campaign engine at the point and the bound.

    python scripts/t24_exec.py --all

**Which bracket at which time** (D-432 (2)): a bracket (stop, R) is eligible at a fixed time when its trades from that
time leave at most 5 % unresolved on normal days, overall and in every year (D-212's ceiling as the operator keeps it).
Each time trades one stop -- the widest of 20, 40 and 60 points at which 1:1 is eligible, up to the map's widest -- and
offers each R eligible there (an R not offered is no trade for an account wanting it: the router passes it on, D-318).
On a BLS report day no trade is entered before the 07:30 CT cut. Two maps: `m40` (stops to 40 points) and `m60` (to 60).

**The plans** (D-432 (3)): `gf2` and `gf15` -- the operator's growth then flip (2026-10-25): the Combine 1:1 at $1,600,
one a session, closed once the room cannot carry another; a funded account at or below its start one growth trade a
session at $1,600 and R 2 (gf2) or 1.5 (gf15), closed once the room cannot carry another; above its start a $240 1:1 flip
a session (D-325: no more than $500 at risk above the start); `table` -- FV3-C's solver re-solved for the map's stops,
shares and offered R. The kill line: the campaign's median growth on the required bankroll above zero at each R's
one-sided 95 % bound over 21-session blocks, 0 % denial, the placement off, and every offered R resolving overall and
in every year (the trades as taken, report days included).
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/t24_exec.py"
DECISION = "D-432"
SEED = 20261028                            # the campaign's resampling
STOPS = (20, 40, 60)
RRS = (1.0, 1.5, 2.0, 3.0)
CUT = 870                                  # 07:30 CT on the trading-day clock (minutes from 17:00)
UNRESOLVED_MAX = 0.05
MAPS = {"m40": 40, "m60": 60}
FAMILIES = ("gf2", "gf15", "table")
GROWTH = {"gf2": 2.0, "gf15": 1.5}
TWO_SHOT, GROWTH_RISK, FLIP = 1600.0, 1600.0, (240.0, 1.0)
MENU_RISKS = (200.0, 400.0, 800.0, 1200.0, 1600.0, 2000.0)
WORKERS = 6


# ------------------------------------------------------------------------------------------------ the brackets


def _coin_trades(rd: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    import t24_wide as tw

    walks, days = tw.load(rd)
    base = walks[walks["delay"].astype(int) == tw.DELAY].copy()
    base["coin"] = tw.coin(base)
    t = base[base["side"].astype(int) == base["coin"]].copy()
    kind = dict(zip(days["date"].astype(str), days["day_kind"].astype(str)))
    t["day_kind"] = t["date"].astype(str).map(kind)
    return t, days


def eligibility(t: pd.DataFrame, bix: dict) -> tuple[dict, list[dict]]:
    """(time, stop, R) -> eligible: unresolved at most UNRESOLVED_MAX on normal days, overall and in every year."""
    n = t[t["day_kind"].astype(str) == "n"]
    elig, rows = {}, []
    for ct, g in n.groupby(n["decision_ct"].astype(str)):
        for S in STOPS:
            for R in RRS:
                f = g[f"o{bix[(R * S, float(S))]}"].astype(str) == "f"
                worst = float(f.groupby(g["year"]).mean().max())
                ok = bool(f.mean() <= UNRESOLVED_MAX and worst <= UNRESOLVED_MAX)
                elig[(ct, S, R)] = ok
                rows.append({"section": "eligibility", "decision_ct": ct, "stop": S, "rr": R,
                             "unresolved": float(f.mean()), "unresolved_worst_year": worst, "eligible": ok})
    return elig, rows


def stop_map(elig: dict, top: int) -> dict[str, int]:
    """Each time's stop: the widest of STOPS up to `top` at which 1:1 is eligible; a time with none trades nothing."""
    out = {}
    for ct in sorted({k[0] for k in elig}):
        for S in sorted(STOPS, reverse=True):
            if S <= top and elig.get((ct, S, 1.0)):
                out[ct] = S
                break
    return out


def trades(rd: Path, top: int) -> tuple[pd.DataFrame, list[str], list[dict]]:
    """The coin's trades at the map's stops: each R's net R, gross, cost, outcome and exit where offered (NaN where not),
    the report days' trades before the cut dropped; the day set; the eligibility and map rows."""
    import t23_choose as tc
    import t24_wide as tw

    from propedge.reporting.results import read_result

    bix = tw.bracket_index("R149-t24-NQ-2021")
    t, days = _coin_trades(rd)
    elig, rows = eligibility(t, bix)
    smap = stop_map(elig, top)
    rows += [{"section": "map", "map": f"m{top}", "decision_ct": ct, "stop": S,
              "offered": ",".join(f"{R:g}" for R in RRS if elig[(ct, S, R)])} for ct, S in smap.items()]
    t = t[t["decision_ct"].astype(str).isin(smap)].copy()
    t = t[~((t["day_kind"].astype(str) == "b") & (t["decision_slot_minutes"].astype(int) < CUT))]
    t["S"] = t["decision_ct"].astype(str).map(smap).astype(int)
    sp = read_result(rd / Path(tc.R137).name)
    sp = sp[sp["kind"] == "spread"]
    spread = {(str(r.decision_ct), int(r.year)): float(r.spread_ticks_mean) for r in sp.itertuples() if float(r.quotes) > 0}
    t["entry_t"] = t["entry_slot"].astype(float)
    parts = []
    for S, g in t.groupby("S"):
        g = g.copy()
        for R in RRS:
            b = bix[(R * S, float(S))]
            offered = np.array([elig[(ct, S, R)] for ct in g["decision_ct"].astype(str)])
            r = tc.trade_r(g, b, R * S, float(S), spread, tw.FEE_MICRO)
            gr, co = tc.trade_parts(g, b, R * S, float(S), spread, tw.FEE_MICRO)
            g[f"r_{R:g}"] = np.where(offered, r, np.nan)
            g[f"g_{R:g}"] = np.where(offered, gr, np.nan)
            g[f"c_{R:g}"] = np.where(offered, co, np.nan)
            g[f"o_{R:g}"] = np.where(offered, g[f"o{b}"].astype(str), "")
            g[f"exit_t_{R:g}"] = np.where(offered, g["entry_t"] + g[f"m{b}"].astype(float), np.nan)
            g[f"mae_{R:g}"] = np.nan
        g["stop_ticks"] = int(round(S / 0.25))
        parts.append(g)
    t = pd.concat(parts).sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)
    t["exit_t"] = t[[f"exit_t_{R:g}" for R in RRS]].max(axis=1)
    t["flat"] = t["o_1"] == "f"
    t["fee_micro_eq"] = tw.FEE_MICRO
    t["side"] = np.where(t["side"].astype(int) > 0, "long", "short")
    t["date"] = t["date"].astype(str)
    cols = ["date", "year", "decision_ct", "day_kind", "S", "entry_t", "exit_t", "side", "stop_ticks", "flat",
            "fee_micro_eq", *[c for R in RRS for c in (f"r_{R:g}", f"g_{R:g}", f"c_{R:g}", f"o_{R:g}", f"exit_t_{R:g}",
                                                       f"mae_{R:g}")]]
    return t[cols], sorted(days["date"].astype(str)), rows


def resolution_rows(t: pd.DataFrame) -> list[dict]:
    """Each offered R's unresolved share in the trades as taken (report days included), overall and its worst year."""
    out = []
    for R in RRS:
        o = t[f"o_{R:g}"].astype(str)
        m = o != ""
        if not m.any():
            continue
        f = (o[m] == "f")
        worst = float(f.groupby(t.loc[m, "year"]).mean().max())
        out.append({"section": "resolution", "rr": R, "offered": int(m.sum()), "unresolved": float(f.mean()),
                    "unresolved_worst_year": worst,
                    "resolves": bool(f.mean() <= UNRESOLVED_MAX and worst <= UNRESOLVED_MAX)})
    return out


# ------------------------------------------------------------------------------------------------ the plans


def fixed_policy(family: str):
    """The operator's growth then flip (module docstring)."""
    import t24_screen as ts

    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers

    G = GROWTH[family]
    combine = ts._closing(Leaf("two-shot 1:1", TWO_SHOT, 1.0, max_trades=1), TWO_SHOT)
    growth = ts._closing(Leaf(f"growth 1:{G:g}", GROWTH_RISK, G, max_trades=1), GROWTH_RISK)
    funded = Tiers(on="balance", name="the start",
                   tiers=((-1e12, growth), (0.01, Leaf("flip 1:1", FLIP[0], FLIP[1], max_trades=1))))
    p = RiskPolicy(id=f"t24_exec_{family}", root=Phase(combine=combine, funded=funded),
                   description=f"T24 (D-432): growth 1:{G:g} then flips")
    p.validate()
    return p


def table_policy(t: pd.DataFrame, e: float, label: str):
    """FV3-C's table (`config/state_policy_v12.yaml`'s rules, rent and export) on the map's stops: one rung a stop, its
    share of the trades, each R's availability the share of the rung's trades offering it; the oracles first."""
    import state_policy_dp as dp

    from propedge.campaign import state_policy as sp
    from propedge.campaign.payout_method import rules_for_method

    present = sorted(int(s) for s in t["S"].unique())
    rpc = tuple(float(s) / 0.25 * 0.5 for s in present)
    shares = tuple(float((t["S"] == s).mean()) for s in present)
    avail = tuple(tuple((R, float(np.isfinite(t.loc[t["S"] == s, f"r_{R:g}"]).mean())) for R in RRS) for s in present)
    rungs = sp.Rungs(risk_per_contract=rpc, shares=shares, combine_cap=50,
                     funded_caps=((0.0, 20), (1500.0, 30), (2000.0, 50)), exit_grid=tuple(RRS), availability=avail)
    menu = sp.Menu(risks=MENU_RISKS, rrs=tuple(RRS), skip=True, step=50.0, rungs=rungs, abandon=True)
    cfg = copy.deepcopy(dp.config(ROOT / "config" / "state_policy_v12.yaml"))
    cfg.pop("rungs", None)
    cfg["menu"] = {"step": 50.0, "risks": list(MENU_RISKS), "rrs": list(RRS), "skip": True}
    cfg["combine_menu"] = {"risks": list(MENU_RISKS), "rrs": list(RRS), "min_rr": 1.0}
    rules = rules_for_method("aeropay")
    rows, ok = dp.oracles(cfg, rules, menu)
    rows = [{**r, "map": label} for r in rows]
    if not ok:
        import t24_wide as tw
        raise tw.OracleRefused("REFUSED: an oracle failed; the table is wrong, not the contract.", rows)
    lam, (f, fsol, ff, c, csol, cf), rounds = dp.solve_rent(cfg, rules, float(e), menu,
                                                            float(cfg["rent_fixed_point"]["start"]))
    cash, days, rate = dp.cycle_rate(rules, ff, cf)
    rows.append({"section": "table", "map": label, "edge": e, "rent": lam, "rate": rate, "cycle_cash": cash,
                 "cycle_slot_days": days, "value_attempt": csol.value - rules.subscription, "p_pass": cf["p_pass"],
                 "combine_p_abandon": cf.get("p_abandon", 0.0), "xfa_p_abandoned": ff.get("p_abandoned", 0.0),
                 "xfa_mean_cash": ff["mean_cash"], "rounds": len(rounds), "rung_stops": ",".join(map(str, present)),
                 "rung_shares": ",".join(f"{x:.4f}" for x in shares)})
    pol, _ = sp.export_policy(f"t24_exec_table_{label}_e{e:+.3f}_lamstar", c, cf["visitation"], f, ff["visitation"],
                              float(cfg["export"]["balance_band"]), float(cfg["export"]["cushion_band"]), version=12,
                              c_pol0=csol.policy[0], f_pol0=fsol.policy[0],
                              description=f"T24 (D-432): FV3-C's table on the {label} map's stops {present}, at edge "
                                          f"{e:+.3f}, slot rent ${lam:.2f}/day")
    return pol, rows


# ------------------------------------------------------------------------------------------------ the campaign


def run_config(blocks, e_by, lb_by, hook, policy) -> pd.DataFrame:
    import score_fv3_grid as gf
    import t24_wide as tw

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    df, _ = gate.run_gate(list(blocks), e=e_by[1.0], lb=lb_by[1.0], protocol=tw.protocol(), bankroll=gf.UNBOUND_BANKROLL,
                          horizon_days=tw.HORIZON, n_paths=tw.N_PATHS, seed=SEED, accounts=tw.ACCOUNTS,
                          sizing=tw.sizing(), rules=rules_for_method("aeropay"), mode="rotation",
                          settlement="pessimistic", combines=tw.ACCOUNTS, total_accounts=tw.ACCOUNTS,
                          risk_policy=policy, e_by_rr=e_by, lb_by_rr=lb_by, levels=(0.0,), path_hook=hook, rtp=False,
                          routing="able", cross_account=True, hold_to_own_exit=True, one_at_a_time=tw.GAP)
    return df


def screen_config(rd: Path, label: str, family: str) -> dict:
    """One (map, plan): computed and returned, nothing written; the parent writes (D-430)."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t24_wide as tw

    t, days, rows = trades(rd, MAPS[label])
    menu = list(RRS)
    stats = cf.edge_stats(t, menu, days, tw.BLOCK, None)
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    blocks, n_used = gf.gate_blocks(t, days, 0.25 * 2.0, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    pol_dict = None
    if family == "table":
        pol, trows = table_policy(t, tw.edge_cell(lb_by), label)
        rows += trows
        pol_dict = pol.as_dict()
    else:
        pol = fixed_policy(family)
    hook = lt.lever_hook(ps.composed_hook({"margin": tw.MARGIN, "block_days": tw.BLOCK}))
    df = run_config(blocks, e_by, lb_by, hook, pol)
    df.insert(0, "family", family)
    df.insert(0, "map", label)
    df.insert(0, "section", "campaign")
    res_rows = resolution_rows(t)
    resolves = all(r["resolves"] for r in res_rows)
    g = float(df[df["shift"] == "lower_bound"].iloc[0]["pf_growth_on_base_p50"])
    gp = float(df[df["shift"] == "point"].iloc[0]["pf_growth_on_base_p50"])
    screen = {"section": "screen", "map": label, "family": family, "growth_at_point": gp, "growth_at_bound": g,
              "resolves": resolves, "continues": bool(g > 0 and resolves)}
    print(f"{label} {family}: growth {gp:+.4f} at the point, {g:+.4f} at the bound; resolves {resolves}", flush=True)
    edge = [{"section": "edge", "map": label, "rr": R, "e": stats[R]["e"], "lb": stats[R]["lb"], "n": stats[R]["n"],
             "gross_r": float(np.nanmean(t[f"g_{R:g}"])), "cost_r": float(np.nanmean(t[f"c_{R:g}"]))} for R in menu]
    return {"map": label, "family": family, "rows": rows + edge + res_rows, "campaign": df, "screen": screen,
            "policy": pol_dict, "trades": len(t)}


def _job(args: tuple) -> dict:
    """A configuration in a worker; a refusal or an error comes back as a value (D-430)."""
    import t24_wide as tw

    rd, label, family = args
    try:
        return screen_config(rd, label, family)
    except tw.OracleRefused as exc:
        return {"map": label, "family": family, "refused": str(exc), "rows": exc.rows}
    except BaseException:                                        # noqa: B036 -- returned to the parent, never lost
        import traceback

        return {"map": label, "family": family, "error": traceback.format_exc()}


def write_map(label: str, outs: list[dict], rd: Path, results_dir: Path | None) -> None:
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import note_written, write_result

    frames, screens, base = [], [], None
    vc = VariantCounter(path=rd / "variants.jsonl")
    for o in outs:
        if "refused" in o:
            frames.append(pd.DataFrame(o["rows"]))
            screens.append({"section": "screen", "map": label, "family": o["family"], "refused": o["refused"],
                            "continues": False})
            continue
        if base is None:
            base = pd.DataFrame(o["rows"])
            frames.append(base)
        elif o["family"] == "table":
            frames.append(pd.DataFrame([r for r in o["rows"] if r.get("section") in ("oracle", "table")]))
        frames.append(o["campaign"])
        screens.append(o["screen"])
        vc.record(prereg_id=f"{DECISION}:t24_exec", seed=SEED, exploratory=True,
                  params={"study": "T24 execution screen", "map": label, "family": o["family"]},
                  label=f"T24 exec {label} {o['family']}")
        if o.get("policy") is not None:
            side = rd / f"t24_exec_{label}_table_policy.json"
            side.write_text(json.dumps(o["policy"]), encoding="utf-8")
            note_written(side)
    frames.append(pd.DataFrame(screens))
    write_result(pd.concat(frames, ignore_index=True), f"t24_exec_{label}", script=SCRIPT, seed=SEED, exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": DECISION, "map": label, "widest_stop": MAPS[label], "rrs": list(RRS),
                             "families": list(FAMILIES), "growth": GROWTH, "two_shot": TWO_SHOT,
                             "growth_risk": GROWTH_RISK, "flip": list(FLIP), "unresolved_max": UNRESOLVED_MAX,
                             "cut": CUT, "rule": "strict, five minutes"},
                 notes={"status": "EXPLORATORY screen (D-432); the kill line at the bound with resolution, never a verdict"},
                 description=f"T24's execution screen (D-432), the {label} map: coin trades at the bracket each time "
                             "resolves, the operator's growth-then-flip plans and the table, strictly one at a time.")


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)
    if not a.all:
        ap.error("--all")
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if not bool(read_result(rd / "t24_identity.csv").iloc[0]["identity_holds"]):
        print("REFUSED: the identity against R147/R148 does not hold (D-428 (4)).")
        return 3
    jobs = [(rd, m, f) for m in MAPS for f in FAMILIES]
    if WORKERS > 1:
        from multiprocessing import Pool

        with Pool(min(WORKERS, len(jobs))) as pool:
            outs = pool.map(_job, jobs)
    else:
        outs = [_job(j) for j in jobs]
    errors = [o for o in outs if "error" in o]
    for m in MAPS:
        write_map(m, [o for o in outs if o["map"] == m and "error" not in o], rd, results_dir)
    for o in errors:
        print(f"ERROR at {o['map']} {o['family']} (nothing written for it):\n{o['error']}", flush=True)
    return 4 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
