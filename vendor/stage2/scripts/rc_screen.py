"""EXPLORATORY (D-521): family RC's cheap screen -- the resolved coin on P-14's design, NQ's development span.

    python scripts/rc_screen.py --check --paths 4      # the identity, the walk, the slot rule and the cells at 4 paths;
                                                       # prints no campaign reading, writes nothing
    python scripts/rc_screen.py --workers 4            # the screen (500 paths); writes results/rc_screen.csv

**The family** (`propedge/research/resolved_coin.py`, D-521): at each scheduled clock slot one trade, its side a coin
seeded 20261102, entered at the first bar opening after the slot, walked by FV3-C's rung walk; the slots of each rung
chosen by D-515's resolution rule from the walk's kind and exit columns only. Two cells -- FV3-C's 12.5 and 25-point
rungs (`rc_s50`, `rc_s100`) -- nothing else searched.

**The money side, P-14's exactly** (`scripts/a3_brk30_cb20.py`): `atlas_a3.gate_kwargs` -- FV3-C's engine call, the day
capacity at the cell's busiest day (D-469) -- with the no-closure plan (`a3_brk30_cb20.noclose_plan`, D-502), a budget
of 20 Combine purchases and resets in 21 trading days, the strict rule (5 minutes), the placement off and 0 % denial;
each R's bound over 21-session blocks with the era rule (`atlas_a3.bounds`, P-11's convention); 500 paths; the campaign
seed `SEED` = 20261131 -- P-14's, fixed in this file before any run, so a cell and P-14 draw the same day sequences
(common random numbers: the lift over the coin is read pair-wise).

**First, the identity (refused otherwise):** P-14's own trades (A3-BRK30, `a3_brk30.cell_trades`) through this
script's engine call reproduce the first `--paths` paths of `results/a3_brk30_cb20_gate_paths.csv` (its `gate` run at
0 %, point and bound, `zero_edge_decomposition.PATH_COLS`).

**Readings per cell** (section `cell`): the trades, trades a day, the busiest day, the capacity, the schedule, the long
share, every R's unresolved share overall and in its worst year (`atlas_a3.resolution`), growth on the required
bankroll at the bound (the gate row) and at the point, the required bankroll, the zero-edge twin's growth (beside),
the share of payouts exposed and the break-even denial; **the kill line: growth on the required bankroll at the bound
not above zero kills the cell** (D-521 (5)); the family continues if a cell survives. Beside: P-14's own gate rows
(`results/a3_brk30_cb20_gate.csv`, read, not rerun). Sections `resolution` (every rung x slot) and `choice` (each
rung's qualifying slots and schedule) carry the slot rule's reading.

Written: `results/rc_screen.csv` and `results/rc_stop_distribution.csv` (the card's stops: one row per trade and state
at the fresh decisions, A3-BRK30's form), with manifests; EXPLORATORY, the two cells under `D-521:rc_screen`.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.research import resolved_coin as rc  # noqa: E402

SCRIPT = "scripts/rc_screen.py"
DECISION = rc.DECISION
RESULT = "rc_screen"
STOPS_RESULT = "rc_stop_distribution"
FAMILY_ID = f"{DECISION}:rc_screen"
SEED = 20261131                            # P-14's campaign seed (D-512), fixed here before any run of this screen
N_PATHS = 500
BUDGET = (20, 21)                          # P-14's (a3_brk30_cb20.BUDGET, checked)
STRICT_GAP = 5.0                           # P-14's (a3_brk30_cb20.STRICT_GAP, checked)
P14_PATHS = "a3_brk30_cb20_gate_paths.csv"
P14_GATE = "a3_brk30_cb20_gate.csv"
READING = "EXPLORATORY (D-521): family RC's cheap screen; a kill line at the bound; no verdict"


# ------------------------------------------------------------------------------------------------ the inputs


def inputs() -> dict[str, Any]:
    """P-14's inputs (`a3_brk30.inputs`: A1's days, A3's config, FV3-C's config, the tick value), the no-closure plan
    and P-14's constants, checked."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C

    from propedge import RESULTS_DIR

    if tuple(C.BUDGET) != BUDGET or float(C.STRICT_GAP) != STRICT_GAP or int(C.SEED) != SEED:
        raise SystemExit("REFUSED: P-14's budget, strict rule or seed are not the ones this screen declares.")
    L = B.inputs()
    nc = C.noclose_plan(RESULTS_DIR)
    return {"L": L, "plan": nc}


def walked_minutes(days: pd.DataFrame, slots: list[int], cut: int) -> pd.DataFrame:
    """Every T24 slot on every walked day (normal and report days), a report day's slots before the cut dropped
    (`a3_resolution_map.pool_events`' rule): date, slot, day_kind."""
    import a3_resolution_map as m0

    d = days[days["day_kind"].astype(str).isin(m0.WALK_DAY_KINDS)][["date", "day_kind"]].copy()
    d["date"] = d["date"].astype(str)
    m = d.merge(pd.DataFrame({"slot": [int(s) for s in slots]}), how="cross")
    m = m[~((m["day_kind"] == "b") & (m["slot"].astype(int) < int(cut)))]
    return m.sort_values(["date", "slot"], kind="stable").reset_index(drop=True)


def build(I: dict[str, Any]) -> dict[str, Any]:
    """The walk at delay 0 on both rungs, the slot rule's reading and choice, and each cell's trades."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge.outcomes.collect_core import c_slot
    from propedge.research.atlas_walk import t24_slots

    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    rr_grid = A.rrs(cfg)
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    slots = sorted(int(s) for s in t24_slots())
    days = L["days"].copy()
    days["date"] = days["date"].astype(str)
    mins = walked_minutes(days, slots, cut)
    t0 = time.time()
    arrays = A.bar_arrays(cfg, sorted(mins["date"].unique()))
    walks = A.walk_minutes(mins, arrays, rc.DELAY, float(cfg["contract"]["tick"]), rc.RUNGS, rr_grid)
    print(f"  the walk: {len(walks)} walks ({len(mins)} slot-days x 2 sides) at delay {rc.DELAY}, "
          f"{time.time() - t0:.0f} s", flush=True)
    res_cols = ["date", "slot"] + rc.resolution_columns(rc.RUNGS, rr_grid)
    table = rc.resolution_table(walks[res_cols], rc.RUNGS, rr_grid)          # resolution columns only
    years = sorted({int(d[:4]) for d in mins["date"]})
    choice = rc.choose(table, years)
    coins = rc.coin_table(days["date"].tolist(), slots)
    fees = A.fee_by_stop(fcfg, rc.RUNGS, tv)
    crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
    kinds = dict(zip(days["date"], days["day_kind"].astype(str)))
    keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I["plan"])))
    cells = {}
    for S in rc.RUNGS:
        sched = choice[S]["schedule"]
        if not sched:
            cells[S] = None
            continue
        t = rc.cell_trades(walks, kinds, sched, S, coins, fees, rr_grid=rr_grid, fresh_rr=crr, tick_value=tv,
                           entry_ticks=float(cfg["slip_ticks"]), cut=cut)
        cells[S] = zd.pad(t, keys) if len(t) else None
    return {"table": table, "choice": choice, "cells": cells, "days": sorted(days["date"]), "years": years,
            "rr_grid": rr_grid, "walks": int(len(walks)), "coins": coins}


# ------------------------------------------------------------------------------------------------ the engine call


class Runner:
    """P-14's engine call on any trade set, every path recorded in one sink (`portfolio_stage.composed_hook`)."""

    def __init__(self, I: dict[str, Any], workers: int):
        import fv3d_lever_test as lt
        import portfolio_stage as ps

        self.I, self.workers = I, int(workers)
        fcfg = I["L"]["fcfg"]
        self.sink: list[dict] = []
        self.inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                                       "block_days": int(fcfg["portfolio"]["block_days"])}, sink=self.sink)
        self.hook = lt.lever_hook(self.inner)

    def run(self, label: str, t: pd.DataFrame, days: list[str], n_paths: int, *, twin: bool = False,
            sizing: Any = None, bounds: tuple[dict, dict] | None = None, protocol_fields: dict | None = None,
            payout_timing: str | None = None, routing_rule: str | None = None,
            capacity: int | None = None) -> pd.DataFrame:
        """`sizing` (D-542's diagnostic): a `SizingRule` in place of the gate's own; None (every earlier caller) passes
        the gate's call unchanged. `bounds` (D-551's spans): (e by R, the bound by R) in place of the era rule's
        (`atlas_a3.bounds`); None (every earlier caller) reads the era rule as before. `protocol_fields` (D-564's
        payout screen): fields of the gate's `Protocol` replaced (`dataclasses.replace`); `payout_timing`: passed to
        `gate.run_gate`; None for either (every earlier caller) leaves the gate's call unchanged. `capacity` (D-602's
        years, D-536 (4)'s construction): the day capacity in place of the trade set's own (`a3_brk30.capacity`); None
        (every earlier caller) reads the trade set's own as before."""
        import a3_brk30 as B
        import atlas_a3 as A
        import portfolio_stage as ps
        import score_fv3_grid as gf

        from propedge.campaign import gate

        L = self.I["L"]
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        keys = B.rrs(t)
        if bounds is None:
            _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
        else:
            e_by, lb_by = dict(bounds[0]), dict(bounds[1])
        blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
        if n_used != len(t):
            raise SystemExit("REFUSED: the blocks hold a different number of trades.")
        cap = B.capacity(t, fcfg) if capacity is None else int(capacity)
        horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
        if twin:
            fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
            blocks = ps.zero_edge_blocks(blocks, e_by, fr)
            e_by = lb_by = {k: 0.0 for k in e_by}
        ps._label(self.inner, label)
        kw = A.gate_kwargs(blocks, fcfg, tv, self.I["plan"], e_by, lb_by, self.hook, seed=SEED, n_paths=int(n_paths),
                           horizon=horizon, capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=STRICT_GAP,
                           purchase_budget=BUDGET)
        if sizing is not None:
            kw["sizing"] = sizing
        if protocol_fields:
            from dataclasses import replace as _replace

            kw["protocol"] = _replace(kw["protocol"], **protocol_fields)
        if payout_timing is not None:
            kw["payout_timing"] = payout_timing
        if routing_rule is not None:                  # D-568: a routing rule; None leaves the gate's call unchanged
            kw["routing_rule"] = routing_rule
        df, _ = gate.run_gate(kw.pop("blocks"), workers=self.workers, **kw)
        df.insert(0, "run", label)
        return df


def identity_problems(R: Runner, n: int) -> list[str]:
    """P-14's own trades through this engine call against the first `n` paths of P-14's `gate` run, both shifts."""
    import a3_brk30 as B
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    t, days = B.cell_trades(R.I["L"])
    R.run("p14_identity", t, days, n)
    ref = read_result(RESULTS_DIR / P14_PATHS)
    return zd.path_problems(R.sink, ref, [("p14_identity", s, "gate", s) for s in ("point", "lower_bound")], int(n))


def p14_beside() -> list[dict]:
    """P-14's own gate rows at 0 % (read, not rerun)."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    d = read_result(RESULTS_DIR / P14_GATE)
    g = d[(d["section"].astype(str) == "gate") & np.isclose(d["enforcement_p"].astype(float), 0.0)]
    return [{"section": "beside", "cell": "p14", "shift": str(r["shift"]),
             "growth_on_required": float(r["pf_growth_on_base_p50"]), "required_p90": float(r["pf_required_p90"]),
             "note": f"P-14's registered gate row (results/{P14_GATE}), read beside, never rerun"}
            for _, r in g.iterrows()]


# ------------------------------------------------------------------------------------------------ the readings


def cell_row(S: int, t: pd.DataFrame, choice: dict, df: pd.DataFrame, twin: pd.DataFrame, days: list[str],
             rr_grid, fcfg: dict) -> dict[str, Any]:
    import a3_brk30 as B
    import atlas_a3 as A

    res, ok = A.resolution(t, rr_grid)
    at = {s: df[(df["shift"] == s) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0] for s in
          ("point", "lower_bound")}
    tw = twin[twin["shift"] == "point"].iloc[0]
    gb = float(at["lower_bound"]["pf_growth_on_base_p50"])
    return {"section": "cell", "cell": rc.cell_name(S), "stop_ticks": int(S), "stop_points": S / 4.0,
            "schedule": " ".join(rc.ct(s) for s in choice["schedule"]), "slots": len(choice["schedule"]),
            "qualifying": len(choice["qualifying_slots"]), "trades": int(len(t)), "days": int(len(days)),
            "trades_per_day": float(len(t) / len(days)), "busiest_day": int(B.busiest(t)),
            "capacity": int(B.capacity(t, fcfg)), "long_share": float((t["side"] == "long").mean()),
            "every_r_resolves": bool(ok), **res,
            "growth_on_required": gb, "growth_on_required_point": float(at["point"]["pf_growth_on_base_p50"]),
            "required_p90": float(at["lower_bound"]["pf_required_p90"]),
            "growth_zero_edge_twin": float(tw["pf_growth_on_base_p50"]),
            "share_payouts_exposed": float(at["lower_bound"].get("share_payouts_exposed", np.nan)),
            "break_even_denial_p50": float(at["lower_bound"].get("pf_break_even_denial_p50", np.nan)),
            "mean_max_combine_purchases_21d": float(at["lower_bound"].get("mean_max_combine_purchases_21d", np.nan)),
            "killed": bool(not gb > 0), "reading": READING}


def stop_distribution(cells: dict[int, pd.DataFrame | None], fcfg: dict) -> pd.DataFrame:
    """The card's stops (A3-BRK30's form, `a3_brk30.stop_distribution`): every cell's trades at the fresh decisions."""
    import a3_brk30 as B

    fr = fcfg["state_policy"]["fresh"]
    parts = []
    for S, t in cells.items():
        if t is not None:
            parts.append(B.stop_distribution(t, float(fr["combine_rr"]), float(fr["funded_rr"])).assign(
                cell=rc.cell_name(S)))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="identity, walk, rule and cells; no reading, nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not a.check and int(a.paths) != N_PATHS:
        print(f"REFUSED ({DECISION}): the screen runs {N_PATHS} paths; a smaller run is --check (writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    print("P-14's inputs and the no-closure plan...", flush=True)
    I = inputs()
    R = Runner(I, a.workers)
    bad = identity_problems(R, a.paths)
    if bad:
        print(f"REFUSED ({DECISION}): P-14's trades through this engine call are not {P14_PATHS} -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: P-14's trades = the first {a.paths} paths of {P14_PATHS} (gate, 0 %, point and bound)",
          flush=True)
    print("the walk at delay 0 and the slot rule (resolution columns only)...", flush=True)
    b = build(I)
    for S in rc.RUNGS:
        ch = b["choice"][S]
        t = b["cells"][S]
        print(f"  {rc.cell_name(S)}: {len(ch['qualifying_slots'])} qualifying slots, schedule "
              f"{[rc.ct(s) for s in ch['schedule']]}, {0 if t is None else len(t)} trades "
              f"({0 if t is None else len(t) / len(b['days']):.3f} a day)", flush=True)
    fcfg = I["L"]["fcfg"]
    rows: list[dict] = []
    for S in rc.RUNGS:
        t = b["cells"][S]
        if t is None:
            rows.append({"section": "cell", "cell": rc.cell_name(S), "stop_ticks": int(S), "trades": 0,
                         "killed": True, "note": "no qualifying slot under the declared rule"})
            continue
        df = R.run(rc.cell_name(S), t, b["days"], a.paths)
        tw = R.run(f"{rc.cell_name(S)} twin", t, b["days"], a.paths, twin=True)
        if not a.check:
            rows.append(cell_row(S, t, b["choice"][S], df, tw, b["days"], b["rr_grid"], fcfg))
    sd = stop_distribution(b["cells"], fcfg)
    if a.check:
        print(f"the cells ran at {a.paths} paths (no reading printed); stop distribution {len(sd)} rows; nothing "
              f"written (--check). {time.time() - t_all:.0f} s")
        return 0
    seconds = time.time() - t_all
    out = [{"section": "identity", "cell": "p14", "holds": True,
            "check": f"P-14's trades through this script's engine call reproduce the first {a.paths} paths of "
                     f"results/{P14_PATHS}'s gate run at 0 %, point and bound (zero_edge_decomposition.PATH_COLS)"}]
    out += [{"section": "resolution", **r} for r in b["table"].to_dict("records")]
    out += [{"section": "choice", "cell": rc.cell_name(S), "stop_ticks": int(S),
             "qualifying": " ".join(rc.ct(s) for s in b["choice"][S]["qualifying_slots"]),
             "schedule": " ".join(rc.ct(s) for s in b["choice"][S]["schedule"])} for S in rc.RUNGS]
    out += rows + p14_beside()
    res = pd.DataFrame(out)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for S in rc.RUNGS:
        counter.record(prereg_id=FAMILY_ID, seed=SEED, exploratory=True,
                       params={"study": "family RC's cheap screen (D-521)", "cell": rc.cell_name(S),
                               "stop_ticks": int(S), "coin_seed": rc.COIN_SEED, "delay": rc.DELAY,
                               "budget": list(BUDGET), "strict_gap": STRICT_GAP, "paths": N_PATHS},
                       label=f"D-521's resolved coin: {rc.cell_name(S)}")
    params = {"decision": DECISION, "seed": SEED, "coin_seed": rc.COIN_SEED, "delay": rc.DELAY, "paths": N_PATHS,
              "rungs": list(rc.RUNGS), "r_resolve": rc.R_RESOLVE, "unresolved_overall": rc.UNRESOLVED_OVERALL,
              "unresolved_year": rc.UNRESOLVED_YEAR, "spacing_q": rc.SPACING_Q, "gap_minutes": rc.GAP_MINUTES,
              "max_slots": rc.MAX_SLOTS, "budget": list(BUDGET), "strict_gap": STRICT_GAP,
              "plan": getattr(I["plan"], "id", None), "walks": b["walks"], "days": len(b["days"]),
              "years": b["years"], "window": [b["days"][0], b["days"][-1]],
              "kill_line": "growth on the required bankroll at the bound (gate row, 0 %, placement off) <= 0 kills a cell",
              "workers": int(a.workers), "seconds": round(seconds, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(rc.RUNGS), parameters=params,
                 notes={"status": READING, "variant_count_rule": f"one per cell, under {FAMILY_ID}",
                        "slot_rule": "resolution columns only (resolved_coin.resolution_table refuses others)"},
                 description="EXPLORATORY (D-521): family RC's cheap screen -- a seeded coin at clock slots chosen by "
                             "D-515's resolution rule on FV3-C's 12.5 and 25-point rungs, through P-14's engine call "
                             "(no-closure table, 20-purchase budget, strict rule), NQ development 2020-01-01..2026-07-16; "
                             "the slot rule's reading, each cell's growth at the bound with the kill line, the zero-edge "
                             "twin and P-14's row beside.")
    write_result(sd, STOPS_RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters={"decision": DECISION, "result": f"{RESULT}.csv",
                                                      "exit_mapping": "target at the state's R; flatten at 15:10; stop "
                                                                      "or breakeven -> stop"},
                 notes={"status": "the card's stop distribution (D-521); A3-BRK30's form",
                        "seed": "none: a reading of the walk at the fresh decisions"},
                 description="Family RC's stops: one row per trade and state at the fresh decisions, per cell.")
    pd.set_option("display.width", 250)
    show = [c for c in ("cell", "trades_per_day", "every_r_resolves", "growth_on_required", "growth_on_required_point",
                        "required_p90", "growth_zero_edge_twin", "killed") if c in res.columns]
    print(res[res["section"].isin(["cell", "beside"])][show + (["shift"] if "shift" in res.columns else [])]
          .to_string(index=False))
    print(f"written: {RESULT}.csv and {STOPS_RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
