"""EXPLORATORY (D-525): family RC re-declared -- the resolved coin re-entering when flat, offered all session in windows
a customer's hours can fit, on P-14's design, NQ's development span.

    python scripts/rc_reentry_screen.py --check --paths 4                  # identity, walk, cutoff, every cell at 4
                                                                           # paths; no campaign reading, nothing written
    python scripts/rc_reentry_screen.py --check --paths 20 --only rc_s50_all   # one cell's timing
    python scripts/rc_reentry_screen.py --workers 4                         # the screen (500 paths); writes the files

**Why a new script** (D-525 (1)): D-521's fixed-slot rule (`scripts/rc_screen.py`, kept so D-523 reproduces) judged
each slot by its slowest 3R night and never traded the 08:30 open. Here nothing is scheduled:

* **The offers** (`resolved_coin.marks`): a coin entry at every five-minute mark from 17:00 CT, each (date, mark) its
  own fair coin seeded 20261102 (`resolved_coin.coin_table` over the whole grid), entered at the first bar opening after
  the mark (delay 0: an alert at the mark; the operator's five minutes counted from it, D-522 (2)), walked long and
  short by FV3-C's rung walk (`atlas_a3.walk_minutes`) on the 12.5 and 25-point rungs at every quarter R to 3R; FV3's
  cost scheme (`resolved_coin.cell_trades`, A3's arithmetic); a report day's marks before the 07:30 CT cut dropped
  (A3's rule, as P-14).
* **The cutoff** (D-525 (4), D-212; `resolved_coin.mark_resolution`): a mark is offered at a rung only if its
  unresolved share (flattened at 15:08 without a level, both sides pooled) is at most 5 % over the window at EVERY R
  the table offers (`zero_edge_decomposition.policy_rrs` of the no-closure plan) -- read from the walk's kind columns
  alone; the function refuses any other column.
* **Re-entry when flat:** every offered mark is a candidate trade in its day's block; P-14's engine call with the
  strict one-at-a-time rule (`TradeRouter(one_at_a_time=5)`) takes the first candidate at least five minutes after the
  last position's exit at its account's R and refuses the rest (counted `skipped_busy`); the table allows one trade an
  account a session (its leaves' `max_trades`), so at most five a session. The day capacity is P-14's rule (the cell's
  busiest day of candidates, `a3_brk30.capacity`).
* **The windows** (D-525 (3), `resolved_coin.WINDOWS`): `all` 17:00 CT to the cutoff, `asia` 18:00-02:00, `london`
  02:00-08:30, `us` 08:30 to the cutoff; a trade holds to its bracket or the 15:08 flatten. 2 rungs x 4 windows = 8
  cells under `D-525:rc_screen`.

**The money side, P-14's exactly** (`rc_screen.Runner`: `atlas_a3.gate_kwargs` with the no-closure plan, 20 purchases
in 21 days, the strict rule, five Topstep seats, the placement off, 0 % denial; each R's bound over 21-session blocks by
the era rule), campaign seed 20261131, 500 paths. **First, the identity (refused otherwise):** P-14's own trades
through this engine call reproduce the first `--paths` paths of `results/a3_brk30_cb20_gate_paths.csv`.

**Readings per cell** (section `cell`): the marks offered, the candidates (offered trades) and their count a session,
the trades the campaign TOOK a session (mean over paths, point and bound: the supply), every R's unresolved share
(`atlas_a3.resolution`), growth on the required bankroll at the bound (the gate row) and the point, the required
bankroll, the zero-edge twin's growth, the share of payouts exposed, the break-even denial; **the kill line: growth at
the bound not above zero kills the cell**; `carried` marks the surviving `all`-window cell with the higher growth at the
bound (D-525 (6)'s selection rule; the other windows beside it). Section `marks`: every rung x mark's cutoff reading.
Beside: P-14's registered gate rows (read, not rerun) and its trades taken a session (from the identity run).

Written: `results/rc_reentry_screen.csv` and `results/rc_reentry_stop_distribution.csv` (the card's stops: one row per
offered trade and state at the fresh decisions, from the two `all`-window cells -- every window's trades are a subset of
its rung's `all` cell -- on D-526's deterministic subsample: every 10th trading day in date order, all offered trades and
states on those days; the engine always receives the full candidate set), with manifests; EXPLORATORY. D-523's
`results/rc_screen.csv` is untouched.
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

import rc_screen as S  # noqa: E402
from propedge.research import resolved_coin as rc  # noqa: E402

SCRIPT = "scripts/rc_reentry_screen.py"
DECISION = rc.DECISION_REENTRY
RESULT = "rc_reentry_screen"
STOPS_RESULT = "rc_reentry_stop_distribution"
FAMILY_ID = f"{DECISION}:rc_screen"
SEED = S.SEED                              # 20261131, P-14's (D-522 (3), D-525 (5))
N_PATHS = S.N_PATHS
READING = "EXPLORATORY (D-525): family RC's re-entry screen; a kill line at the bound; no verdict"


# ------------------------------------------------------------------------------------------------ the offers


def build(I: dict[str, Any]) -> dict[str, Any]:
    """The walk at every mark on both rungs, the cutoff's reading and each cell's candidate trades."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge.outcomes.collect_core import c_slot

    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    rr_grid = A.rrs(cfg)
    offered_rr = sorted(float(R) for R in zd.policy_rrs(I["plan"]))
    missing = [R for R in offered_rr if R not in {float(x) for x in rr_grid}]
    if missing:
        raise SystemExit(f"REFUSED ({DECISION}): the table offers R {missing} the walk's grid does not carry.")
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    grid = rc.marks()
    days = L["days"].copy()
    days["date"] = days["date"].astype(str)
    mins = S.walked_minutes(days, grid, cut)
    t0 = time.time()
    arrays = A.bar_arrays(cfg, sorted(mins["date"].unique()))
    walks = A.walk_minutes(mins, arrays, rc.DELAY, float(cfg["contract"]["tick"]), rc.RUNGS, rr_grid)
    print(f"  the walk: {len(walks)} walks ({len(mins)} mark-days x 2 sides) at delay {rc.DELAY}, "
          f"{time.time() - t0:.0f} s", flush=True)
    res_cols = ["date", "slot"] + rc.mark_resolution_columns(rc.RUNGS, offered_rr)
    table = rc.mark_resolution(walks[res_cols], rc.RUNGS, offered_rr)       # kind columns only
    coins = rc.coin_table(days["date"].tolist(), grid)
    fees = A.fee_by_stop(fcfg, rc.RUNGS, tv)
    crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
    kinds = dict(zip(days["date"], days["day_kind"].astype(str)))
    keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I["plan"])))
    cells: dict[str, dict[str, Any]] = {}
    for St in rc.RUNGS:
        offered = rc.offered_marks(table, St)
        for win in rc.WINDOWS:
            wm = rc.window_marks(offered, win)
            name = rc.reentry_cell_name(St, win)
            t = (rc.cell_trades(walks, kinds, wm, St, coins, fees, rr_grid=rr_grid, fresh_rr=crr, tick_value=tv,
                                entry_ticks=float(cfg["slip_ticks"]), cut=cut) if wm else pd.DataFrame())
            cells[name] = {"stop_ticks": int(St), "window": win, "marks": wm,
                           "trades": zd.pad(t, keys) if len(t) else None}
    walk_days = sorted(mins["date"].unique())
    return {"table": table, "cells": cells, "days": sorted(days["date"]), "walk_days": walk_days, "rr_grid": rr_grid,
            "offered_rr": offered_rr, "walks": int(len(walks)), "marks_grid": len(grid)}


# ------------------------------------------------------------------------------------------------ the readings


def taken_per_session(sink: list[dict], label: str, shift: str) -> float:
    """The trades the campaign took a session (mean over the run's paths at 0 %): its supply."""
    rows = [r for r in sink if r["run"] == label and r["shift"] == shift and float(r["enforcement_p"]) == 0.0]
    if not rows:
        return float("nan")
    return float(np.mean([float(r["trades"]) / max(1, int(r["days"]) - 1) for r in rows if r["trades"] is not None]))


def cell_row(name: str, c: dict, df: pd.DataFrame, twin: pd.DataFrame, sink: list[dict], days: list[str], rr_grid,
             fcfg: dict) -> dict[str, Any]:
    import a3_brk30 as B
    import atlas_a3 as A

    t = c["trades"]
    res, ok = A.resolution(t, rr_grid)
    at = {s: df[(df["shift"] == s) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0] for s in
          ("point", "lower_bound")}
    tw = twin[twin["shift"] == "point"].iloc[0]
    gb = float(at["lower_bound"]["pf_growth_on_base_p50"])
    lo, hi = rc.WINDOWS[c["window"]]
    return {"section": "cell", "cell": name, "stop_ticks": int(c["stop_ticks"]), "stop_points": c["stop_ticks"] / 4.0,
            "window": c["window"], "window_ct": f"{rc.ct(lo)}-{rc.ct(hi % (24 * 60))}",
            "marks_offered": len(c["marks"]), "first_mark": rc.ct(c["marks"][0]), "last_mark": rc.ct(c["marks"][-1]),
            "candidates": int(len(t)), "days": int(len(days)), "candidates_per_day": float(len(t) / len(days)),
            "busiest_day": int(B.busiest(t)), "capacity": int(B.capacity(t, fcfg)),
            "trades_taken_per_session": taken_per_session(sink, name, "lower_bound"),
            "trades_taken_per_session_point": taken_per_session(sink, name, "point"),
            "long_share": float((t["side"] == "long").mean()), "every_r_resolves": bool(ok), **res,
            "growth_on_required": gb, "growth_on_required_point": float(at["point"]["pf_growth_on_base_p50"]),
            "required_p90": float(at["lower_bound"]["pf_required_p90"]),
            "growth_zero_edge_twin": float(tw["pf_growth_on_base_p50"]),
            "share_payouts_exposed": float(at["lower_bound"].get("share_payouts_exposed", np.nan)),
            "break_even_denial_p50": float(at["lower_bound"].get("pf_break_even_denial_p50", np.nan)),
            "mean_max_combine_purchases_21d": float(at["lower_bound"].get("mean_max_combine_purchases_21d", np.nan)),
            "killed": bool(not gb > 0), "reading": READING}


def carried(rows: list[dict]) -> str | None:
    """D-525 (6): the surviving `all`-window cell with the higher growth on the required bankroll at the bound."""
    alive = [r for r in rows if r.get("window") == "all" and not r.get("killed", True)]
    return max(alive, key=lambda r: float(r["growth_on_required"]))["cell"] if alive else None


SUBSAMPLE = (f"D-526: every {rc.STOPS_EVERY_DAYS}th trading day in date order (day index % {rc.STOPS_EVERY_DAYS} == 0 "
             "over each all-window cell's sorted day set), all offered trades and states on those days, both all-window "
             "cells; the engine receives the full candidate set")


def stop_distribution(cells: dict[str, dict], fcfg: dict) -> pd.DataFrame:
    """The card's stops from the two `all`-window cells (every window's trades are a subset of its rung's), on D-526's
    deterministic subsample of days (`resolved_coin.subsample_days`); the engine is never given this subsample."""
    import a3_brk30 as B

    fr = fcfg["state_policy"]["fresh"]
    parts = []
    for name, c in cells.items():
        if c["window"] == "all" and c["trades"] is not None:
            t = c["trades"]
            keep = set(rc.subsample_days(t["date"].astype(str)))
            t = t[t["date"].astype(str).isin(keep)]
            parts.append(B.stop_distribution(t, float(fr["combine_rr"]), float(fr["funded_rr"])).assign(cell=name))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="identity, walk, cutoff and cells; no reading, nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", default=None, help="with --check: run one cell (a timing seam)")
    a = ap.parse_args(argv)
    if not a.check and (int(a.paths) != N_PATHS or a.only):
        print(f"REFUSED ({DECISION}): the screen runs {N_PATHS} paths on every cell; a smaller run is --check "
              "(writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    print("P-14's inputs and the no-closure plan...", flush=True)
    I = S.inputs()
    R = S.Runner(I, a.workers)
    t0 = time.time()
    bad = S.identity_problems(R, a.paths)
    if bad:
        print(f"REFUSED ({DECISION}): P-14's trades through this engine call are not {S.P14_PATHS} -- "
              + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: P-14's trades = the first {a.paths} paths of {S.P14_PATHS} (gate, 0 %, point and bound; "
          f"{time.time() - t0:.0f} s)", flush=True)
    p14_taken = {s: taken_per_session(R.sink, "p14_identity", s) for s in ("point", "lower_bound")}
    print("the walk at every mark and the cutoff (resolution columns only)...", flush=True)
    b = build(I)
    for St in rc.RUNGS:
        print(f"  {St / 4:g} points: {len(rc.offered_marks(b['table'], St))} of {b['marks_grid']} marks offered",
              flush=True)
    for name, c in b["cells"].items():
        t = c["trades"]
        print(f"  {name}: {len(c['marks'])} marks, {0 if t is None else len(t)} candidates "
              f"({0 if t is None else len(t) / len(b['days']):.1f} a day)", flush=True)
    fcfg = I["L"]["fcfg"]
    rows: list[dict] = []
    timing: dict[str, float] = {}
    for name, c in b["cells"].items():
        if a.only and name != a.only:
            continue
        t = c["trades"]
        if t is None:
            rows.append({"section": "cell", "cell": name, "stop_ticks": c["stop_ticks"], "window": c["window"],
                         "candidates": 0, "killed": True, "note": "no mark the cutoff admits in this window"})
            continue
        t1 = time.time()
        df = R.run(name, t, b["days"], a.paths)
        tw = R.run(f"{name} twin", t, b["days"], a.paths, twin=True)
        timing[name] = time.time() - t1
        if a.check:
            print(f"  {name}: ran at {a.paths} paths (cell and twin) in {timing[name]:.0f} s; trades taken a session "
                  f"{taken_per_session(R.sink, name, 'lower_bound'):.2f} (bound) -- no growth printed", flush=True)
        else:
            rows.append(cell_row(name, c, df, tw, R.sink, b["days"], b["rr_grid"], fcfg))
    sd = stop_distribution(b["cells"], fcfg)
    if a.check:
        print(f"P-14 takes {p14_taken['lower_bound']:.2f} trades a session (bound) for comparison; stop distribution "
              f"{len(sd)} rows (about {len(sd) * 45 / 1e6:.0f} MB as CSV); nothing written (--check). "
              f"{time.time() - t_all:.0f} s")
        return 0
    seconds = time.time() - t_all
    cv = carried(rows)
    for r in rows:
        r["carried"] = (r["cell"] == cv)
    out = [{"section": "identity", "cell": "p14", "holds": True,
            "check": f"P-14's trades through this script's engine call reproduce the first {a.paths} paths of "
                     f"results/{S.P14_PATHS}'s gate run at 0 %, point and bound (zero_edge_decomposition.PATH_COLS)"}]
    out += [{"section": "marks", **r} for r in b["table"].to_dict("records")]
    out += rows + S.p14_beside()
    out += [{"section": "beside", "cell": "p14", "shift": s, "trades_taken_per_session": v,
             "note": "P-14's trades taken a session in this script's identity run"} for s, v in p14_taken.items()]
    res = pd.DataFrame(out)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for name, c in b["cells"].items():
        counter.record(prereg_id=FAMILY_ID, seed=SEED, exploratory=True,
                       params={"study": "family RC's re-entry screen (D-525)", "cell": name,
                               "stop_ticks": int(c["stop_ticks"]), "window": c["window"], "coin_seed": rc.COIN_SEED,
                               "delay": rc.DELAY, "mark_step": rc.MARK_STEP, "budget": list(S.BUDGET),
                               "strict_gap": S.STRICT_GAP, "paths": N_PATHS},
                       label=f"D-525's re-entry coin: {name}")
    params = {"decision": DECISION, "seed": SEED, "coin_seed": rc.COIN_SEED, "delay": rc.DELAY, "paths": N_PATHS,
              "rungs": list(rc.RUNGS), "mark_step": rc.MARK_STEP, "session_end_ct": rc.ct(rc.SESSION_END),
              "windows": {k: [rc.ct(v[0]), rc.ct(v[1] % (24 * 60))] for k, v in rc.WINDOWS.items()},
              "unresolved_mark": rc.UNRESOLVED_MARK, "offered_rr": b["offered_rr"], "budget": list(S.BUDGET),
              "strict_gap": S.STRICT_GAP, "plan": getattr(I["plan"], "id", None), "walks": b["walks"],
              "days": len(b["days"]), "window": [b["days"][0], b["days"][-1]], "carried": cv,
              "kill_line": "growth on the required bankroll at the bound (gate row, 0 %, placement off) <= 0 kills a cell",
              "selection": "the surviving all-window cell with the higher growth at the bound (D-525 (6))",
              "cell_seconds": {k: round(v, 1) for k, v in timing.items()}, "workers": int(a.workers),
              "seconds": round(seconds, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(b["cells"]), parameters=params,
                 notes={"status": READING, "variant_count_rule": f"one per cell, under {FAMILY_ID}",
                        "cutoff": "kind columns only (resolved_coin.mark_resolution refuses others)",
                        "supersedes": "D-523's fixed-slot screen (results/rc_screen.csv) stays on record as D-521's "
                                      "scheduling fault (D-525 (1))"},
                 description="EXPLORATORY (D-525): family RC's re-entry screen -- a seeded coin offered every five "
                             "minutes, admitted by D-212's resolution test at every offered R, taken by P-14's strict "
                             "router when every account is flat, on FV3-C's 12.5 and 25-point rungs in four windows "
                             "(all, asia, london, us), through P-14's engine call; NQ development 2020-01-01..2026-07-16; "
                             "each cell's supply, growth at the bound with the kill line, the zero-edge twin and P-14 "
                             "beside.")
    write_result(sd, STOPS_RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters={"decision": DECISION, "result": f"{RESULT}.csv",
                                                      "cells": "the two all-window cells (every window's trades are a "
                                                               "subset of its rung's)",
                                                      "subsample": SUBSAMPLE, "every_days": rc.STOPS_EVERY_DAYS,
                                                      "exit_mapping": "target at the state's R; flatten at 15:10; stop "
                                                                      "or breakeven -> stop"},
                 notes={"status": "the card's stop distribution (D-525); A3-BRK30's form",
                        "seed": "none: a reading of the walk at the fresh decisions"},
                 description="Family RC's re-entry stops: one row per offered trade and state at the fresh decisions, on "
                             "D-526's subsample of every 10th trading day.")
    pd.set_option("display.width", 250)
    show = [c for c in ("cell", "candidates_per_day", "trades_taken_per_session", "every_r_resolves",
                        "growth_on_required", "growth_on_required_point", "required_p90", "growth_zero_edge_twin",
                        "killed", "carried") if c in res.columns]
    print(res[res["section"] == "cell"][show].to_string(index=False))
    print(f"written: {RESULT}.csv and {STOPS_RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
