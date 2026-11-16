"""EXPLORATORY (D-538): the stop-width screen of the news-safe coin -- the coin's one structural choice -- at 37.5 and
50-point stops (150 and 200 MNQ ticks), each in the four customer windows, beside the 25-point cell.

    python scripts/rc_width_screen.py --check --paths 4 --smoke-days 40   # a smoke on the first 40 days: P-14's
                                                                           # identity, the walk, the cutoff, the sizing
                                                                           # and every cell at 4 paths; nothing written
    python scripts/rc_width_screen.py --check --paths 4                   # the same on every day, with identity (b)
    python scripts/rc_width_screen.py --workers 3                         # the screen (500 paths); writes the file

**Why** (D-538): the 12.5-point rung lost to its costs (D-523, D-527) and the 25-point rung did not; the cost share of
the risk falls as the stop widens, while resolution and supply worsen. The grid is contract arithmetic, fixed by D-538
before anything was read; nothing here is chosen from a reading.

**Each cell is D-525's design at its stop, with D-533's cut** (`rc_reentry_screen`'s construction, the stop a
parameter): a coin offered every five minutes from 17:00 CT (`resolved_coin.marks`), its own fair coin per (date, mark)
seeded 20261102 (`coin_table`), entered at the first bar opening after the mark, walked long and short by FV3-C's rung
walk (`atlas_a3.walk_minutes`, any stop in ticks) at every quarter R to 3R with FV3's costs (`fee_by_stop` at the stop);
the cutoff at D-212's 5 % for every R the table offers, read from the walk's kind columns only (`mark_resolution`); a
report day's marks before 07:30 CT dropped (A3's rule) and then every report-day entry before 07:35 CT
(`drop_release_minute`, D-533 (2)); the four windows (`resolved_coin.WINDOWS`). 2 stops x 4 windows = 8 cells under
`D-538:rc_width`.

**The sizing is the engine's** (D-538 (2)): the gate's `SizingRule` turns each leaf's dollar risk into whole micros at
the trade's stop (floor, capped at the phase's allowance); nothing is re-solved. Section `sizing`
(`resolved_coin.width_sizing`) reads, for the 25, 37.5 and 50-point stops, what every trading leaf of the no-closure table
buys at each allowance tier, and flags any leaf the stop cannot size (unsized, or refused by D-272's stand-aside).

**The money side, P-14's exactly** (`rc_screen.Runner`: the no-closure table, 20 purchases in 21 days, the strict rule,
five Topstep seats, the placement off, 0 % denial, each R's bound over 21-session blocks by the era rule), the screen's
seed 20261131 (D-522 (3)), 500 paths; the kill line (growth on the required bankroll at the bound not above zero); each
cell's zero-edge twin; the trades taken a session.

**Identities first, each refusing:** (a) P-14's trades reproduce `results/a3_brk30_cb20_gate_paths.csv`; (b) this
script's builder at the 25-point stop, without D-533's cut, gives P-15's `rc_s100_all` exactly (the screen's row and the
pinned content hash, `rc_dev_test.trade_problems`); (c) at 500 paths that cell at 20261131 reproduces
`results/rc_reentry_screen.csv`'s growth and required bankroll (`rc_dev_test.screen_growth_problems`).

**The reference for D-538's comparison** -- "grows more at the bound than `rc_s100_all_nr` at the same seed" -- is the
25-point news-safe cell run here at 20261131 (section `reference`); D-535's own rows (`results/rc_nr_dev.csv`, at P-15's
registered seed) are read beside, never rerun. `beats_reference` marks each all-window wider cell that grows more at the
bound than the reference; such a cell would be a new candidate with its own registered test (D-538 (4)).

Writes `results/rc_width_screen.csv` with its manifest (EXPLORATORY; sections `identity`, `marks`, `sizing`, `cell`,
`reference`, `beside`).
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

SCRIPT = "scripts/rc_width_screen.py"
DECISION = rc.DECISION_WIDTH
RESULT = "rc_width_screen"
FAMILY_ID = f"{DECISION}:rc_width"
SEED = S.SEED                              # the screen's seed (D-522 (3), D-538 (3))
N_PATHS = S.N_PATHS
REF_CELL = "rc_s100_all"                   # P-15's cell (identity (b) and (c))
REF_NR = "rc_s100_all_nr"                  # D-535's candidate: the reference, run here at the screen's seed
NR_FILE = "rc_nr_dev.csv"                  # D-535's file, read beside, never rerun
SIZING_STOPS = (rc.REFERENCE_STOP, *rc.WIDTH_STOPS)
READING = "EXPLORATORY (D-538): the coin's stop-width screen; a kill line at the bound; no verdict"


# ------------------------------------------------------------------------------------------------ the cells


def policy_leaves(plan) -> list[tuple[str, str, float, float | None]]:
    """Every trading leaf of the table, once: (kind 'combine' or 'funded', name, dollar risk, R). Abandon leaves and
    no-trade leaves (risk 0 or `max_trades` 0) trade nothing and are left out."""
    from propedge.campaign.risk_policy import PHASES

    out, seen = [], set()
    for leaf, phases in plan.root.leaves(frozenset(PHASES)):
        if leaf.abandon or not float(leaf.risk) > 0 or (leaf.max_trades is not None and int(leaf.max_trades) == 0):
            continue
        kind = "combine" if "combine" in phases else "funded"
        key = (kind, str(leaf.name), float(leaf.risk), None if leaf.rr is None else float(leaf.rr))
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def build(I: dict[str, Any], stops, *, smoke_days: int | None = None) -> dict[str, Any]:
    """`rc_reentry_screen.build` with the stops a parameter: the walk at every mark at `stops`, the cutoff's reading and
    each (stop, window) cell's trades -- `raw` as D-525 built them (the 07:30 CT report-day cut only) and `trades` with
    D-533's cut (no report-day entry before 07:35 CT). `smoke_days` (a --check seam) keeps the first N days only."""
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
    clear = c_slot(*rc.RELEASE_CLEAR_CT)
    grid = rc.marks()
    days = L["days"].copy()
    days["date"] = days["date"].astype(str)
    if smoke_days is not None:
        days = days.sort_values("date").head(int(smoke_days))
    mins = S.walked_minutes(days, grid, cut)
    stops = tuple(int(x) for x in stops)
    t0 = time.time()
    arrays = A.bar_arrays(cfg, sorted(mins["date"].unique()))
    walks = A.walk_minutes(mins, arrays, rc.DELAY, float(cfg["contract"]["tick"]), stops, rr_grid)
    print(f"  the walk at {[s / 4 for s in stops]} points: {len(walks)} walks ({len(mins)} mark-days x 2 sides), "
          f"{time.time() - t0:.0f} s", flush=True)
    res_cols = ["date", "slot"] + rc.mark_resolution_columns(stops, offered_rr)
    table = rc.mark_resolution(walks[res_cols], stops, offered_rr)          # kind columns only
    coins = rc.coin_table(days["date"].tolist(), grid)
    fees = A.fee_by_stop(fcfg, stops, tv)
    crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
    kinds = dict(zip(days["date"], days["day_kind"].astype(str)))
    keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I["plan"])))
    cells: dict[str, dict[str, Any]] = {}
    for St in stops:
        offered = rc.offered_marks(table, St)
        for win in rc.WINDOWS:
            wm = rc.window_marks(offered, win)
            name = rc.reentry_cell_name(St, win)
            raw = (rc.cell_trades(walks, kinds, wm, St, coins, fees, rr_grid=rr_grid, fresh_rr=crr, tick_value=tv,
                                  entry_ticks=float(cfg["slip_ticks"]), cut=cut) if wm else pd.DataFrame())
            raw = zd.pad(raw, keys) if len(raw) else None
            nr = rc.drop_release_minute(raw, clear) if raw is not None else None
            cells[name] = {"stop_ticks": St, "window": win, "marks": wm, "raw": raw,
                           "trades": nr if (nr is not None and len(nr)) else None,
                           "removed_release": 0 if raw is None else int(len(raw) - (0 if nr is None else len(nr)))}
    return {"table": table, "cells": cells, "days": sorted(days["date"]), "rr_grid": rr_grid, "offered_rr": offered_rr,
            "walks": int(len(walks)), "marks_grid": len(grid)}


def cutoff_reading(I: dict[str, Any], stop: int) -> pd.DataFrame:
    """The cutoff's reading at one stop on every day (a --cutoff-only seam: resolution columns only, one rung's walk at a
    time to keep memory low; no trade, no campaign)."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge.outcomes.collect_core import c_slot

    L = I["L"]
    cfg = L["cfg"]
    rr_grid = A.rrs(cfg)
    offered_rr = sorted(float(R) for R in zd.policy_rrs(I["plan"]))
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    days = L["days"].copy()
    days["date"] = days["date"].astype(str)
    mins = S.walked_minutes(days, rc.marks(), cut)
    arrays = A.bar_arrays(cfg, sorted(mins["date"].unique()))
    walks = A.walk_minutes(mins, arrays, rc.DELAY, float(cfg["contract"]["tick"]), (int(stop),), rr_grid)
    cols = ["date", "slot"] + rc.mark_resolution_columns((int(stop),), offered_rr)
    return rc.mark_resolution(walks[cols], (int(stop),), offered_rr)


def beats(row: dict, ref_growth: float) -> bool:
    """D-538 (4): an all-window cell that clears the kill line and grows more at the bound than the reference."""
    return bool(row.get("window") == "all" and not row.get("killed", True)
                and float(row["growth_on_required"]) > float(ref_growth))


def nr_beside(rd: Path) -> list[dict]:
    """D-535's rows (`results/rc_nr_dev.csv`, at P-15's registered seed; manifest verified), never rerun."""
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / NR_FILE)
    sec = d["section"].astype(str)
    zero = pd.to_numeric(d.get("enforcement_p"), errors="coerce").fillna(0.0) == 0.0
    g = d[(sec.isin(["gate", "gate_at_ledger_n", "zero_edge_twin"])) & zero]
    return [{"section": "beside", "cell": REF_NR, "source": f"results/{NR_FILE} (D-535, P-15's seed; never rerun)",
             "shift": str(r["shift"]), "row": str(r["section"]), "growth_on_required": float(r["pf_growth_on_base_p50"]),
             "required_p90": float(r["pf_required_p90"])} for _, r in g.iterrows()]


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import rc_dev_test as D
    import rc_reentry_screen as RS
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="identities, walk, cutoff, sizing and cells; nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", default=None, help="with --check: run one wider cell (a timing seam)")
    ap.add_argument("--smoke-days", type=int, default=None, help="with --check: the first N days only (skips (b), (c))")
    ap.add_argument("--cutoff-only", action="store_true", help="the cutoff's reading at each wider stop on every day "
                    "(resolution columns only, no trade, no campaign); nothing written")
    a = ap.parse_args(argv)
    if a.cutoff_only:
        I = S.inputs()
        for St in (rc.REFERENCE_STOP, *rc.WIDTH_STOPS):
            tab = cutoff_reading(I, St)
            off = rc.offered_marks(tab, St)
            rcols = [c for c in tab.columns if c.startswith("unresolved_") and c != "unresolved_worst_r"]
            binding = tab[rcols].idxmax(axis=1).str.replace("unresolved_", "R ").value_counts().to_dict()
            print(f"{St / 4:g} points: {len(off)} of {len(tab)} marks offered; by window "
                  f"{ {w: len(rc.window_marks(off, w)) for w in rc.WINDOWS} }; median worst-R unresolved "
                  f"{tab['unresolved_worst_r'].median():.3f}; the R that binds most often {binding}", flush=True)
            if off:
                print(f"  offered from {rc.ct(off[0])} to {rc.ct(off[-1])} CT", flush=True)
        print("nothing written (--cutoff-only).")
        return 0
    if not a.check and (int(a.paths) != N_PATHS or a.only or a.smoke_days is not None):
        print(f"REFUSED ({DECISION}): the screen runs {N_PATHS} paths on every cell and day; a smaller run is --check "
              "(writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    print("P-14's inputs and the no-closure plan...", flush=True)
    I = S.inputs()
    L = I["L"]
    fcfg, tv = L["fcfg"], float(L["tv"])
    R = S.Runner(I, a.workers)
    # (a) P-14's trades through this engine call
    bad = S.identity_problems(R, a.paths)
    if bad:
        print(f"REFUSED ({DECISION}): P-14's trades are not {S.P14_PATHS} -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: P-14's trades = the first {a.paths} paths of {S.P14_PATHS}", flush=True)
    idents = [{"section": "identity", "cell": "p14", "holds": True,
               "check": f"P-14's trades through this engine call reproduce the first {a.paths} paths of "
                        f"results/{S.P14_PATHS} (gate, 0 %, point and bound)"}]
    # (b) the builder at the 25-point stop is P-15's cell
    print("the walk at the 25-point stop (identity (b), the reference)...", flush=True)
    b0 = build(I, (rc.REFERENCE_STOP,), smoke_days=a.smoke_days)
    raw = b0["cells"][REF_CELL]["raw"]
    if a.smoke_days is None:
        bad = D.trade_problems(RESULTS_DIR, {"cells": {D.CELL: {"trades": raw}}, "days": b0["days"],
                                             "rr_grid": b0["rr_grid"]}, fcfg)
        if bad:
            print(f"REFUSED ({DECISION}): this builder's 25-point cell is not P-15's {D.CELL} -- " + "; ".join(bad[:8]))
            return 3
        print(f"identity HOLDS: this builder's 25-point all-day cell = P-15's {D.CELL} (content hash "
              f"{D.trades_hash(raw)[:16]})", flush=True)
        idents.append({"section": "identity", "cell": REF_CELL, "holds": True,
                       "check": f"this script's builder at {rc.REFERENCE_STOP} ticks without D-533's cut reproduces "
                                f"results/{D.SCREEN_FILE}'s {D.CELL} row and the pinned content hash"})
    else:
        print(f"  identity (b) skipped: --smoke-days {a.smoke_days}", flush=True)
    # (c) that cell at the screen's seed reproduces the screen's growth (500 paths only: growth reads every path)
    df_id = R.run(f"{REF_CELL} identity", raw, b0["days"], a.paths)
    if a.smoke_days is None and int(a.paths) == N_PATHS:
        bad = D.screen_growth_problems(RESULTS_DIR, df_id)
        if bad:
            print(f"REFUSED ({DECISION}): {REF_CELL} at {SEED} is not the screen's -- " + "; ".join(bad[:8]))
            return 3
        print(f"identity HOLDS: {REF_CELL} at {SEED} = {D.SCREEN_FILE}'s growth and required bankroll", flush=True)
        idents.append({"section": "identity", "cell": REF_CELL, "holds": True,
                       "check": f"{REF_CELL} at seed {SEED}, 500 paths, reproduces results/{D.SCREEN_FILE}'s growth at "
                                "the bound and point and its required bankroll"})
    # the reference: the 25-point news-safe cell at the screen's seed
    ref_c = b0["cells"][REF_CELL]
    df_ref = R.run(REF_NR, ref_c["trades"], b0["days"], a.paths)
    tw_ref = R.run(f"{REF_NR} twin", ref_c["trades"], b0["days"], a.paths, twin=True)
    ref_row = RS.cell_row(REF_NR, ref_c, df_ref, tw_ref, R.sink, b0["days"], b0["rr_grid"], fcfg)
    ref_row.update({"section": "reference", "cell": REF_NR, "removed_release": ref_c["removed_release"],
                    "killed": bool(not float(ref_row["growth_on_required"]) > 0)})
    del b0
    # the sizing (the engine's own arithmetic, D-538 (2))
    sizing = rc.width_sizing(gf.sizing_rule(fcfg, tv), policy_leaves(I["plan"]), SIZING_STOPS, tv)
    cannot = sizing[sizing["cannot_size"]]
    print(f"  sizing: {len(sizing)} (stop, leaf, tier) rows; {len(cannot)} the stop cannot size "
          f"({sorted({(int(s), k) for s, k in zip(cannot['stop_ticks'], cannot['kind'])})})", flush=True)
    # the wider cells
    print("the walk at the wider stops and the cutoff (resolution columns only)...", flush=True)
    bw = build(I, rc.WIDTH_STOPS, smoke_days=a.smoke_days)
    for St in rc.WIDTH_STOPS:
        print(f"  {St / 4:g} points: {len(rc.offered_marks(bw['table'], St))} of {bw['marks_grid']} marks offered",
              flush=True)
    for name, c in bw["cells"].items():
        t = c["trades"]
        print(f"  {name}: {len(c['marks'])} marks, {0 if t is None else len(t)} candidates "
              f"({0 if t is None else len(t) / len(bw['days']):.1f} a day; {c['removed_release']} release-minute "
              "entries removed)", flush=True)
    rows: list[dict] = []
    timing: dict[str, float] = {}
    for name, c in bw["cells"].items():
        if a.only and name != a.only:
            continue
        t = c["trades"]
        if t is None:
            rows.append({"section": "cell", "cell": name, "stop_ticks": c["stop_ticks"], "window": c["window"],
                         "candidates": 0, "killed": True, "note": "no mark the cutoff admits in this window"})
            continue
        t1 = time.time()
        df = R.run(name, t, bw["days"], a.paths)
        tw = R.run(f"{name} twin", t, bw["days"], a.paths, twin=True)
        timing[name] = time.time() - t1
        if a.check:
            print(f"  {name}: ran at {a.paths} paths (cell and twin) in {timing[name]:.0f} s; trades taken a session "
                  f"{RS.taken_per_session(R.sink, name, 'lower_bound'):.2f} (bound) -- no growth printed", flush=True)
            continue
        r = RS.cell_row(name, c, df, tw, R.sink, bw["days"], bw["rr_grid"], fcfg)
        r["removed_release"] = c["removed_release"]
        rows.append(r)
    if a.check:
        print(f"every identity run held{' (b, c skipped: smoke)' if a.smoke_days else ''}; every cell ran at "
              f"{a.paths} paths; nothing written, no reading printed (--check). {time.time() - t_all:.0f} s")
        return 0
    rg = float(ref_row["growth_on_required"])
    for r in rows:
        r["beats_reference"] = beats(r, rg) if r.get("window") == "all" else False
    seconds = time.time() - t_all
    out = idents + [{"section": "marks", **r} for r in bw["table"].to_dict("records")]
    out += sizing.to_dict("records") + rows + [ref_row] + nr_beside(rd) + S.p14_beside()
    res = pd.DataFrame(out)
    res["reading"] = res["reading"].fillna(READING) if "reading" in res else READING
    counter = VariantCounter(path=rd / "variants.jsonl")
    for name, c in bw["cells"].items():
        counter.record(prereg_id=FAMILY_ID, seed=SEED, exploratory=True,
                       params={"study": "family RC's stop-width screen (D-538)", "cell": name,
                               "stop_ticks": int(c["stop_ticks"]), "window": c["window"], "coin_seed": rc.COIN_SEED,
                               "news_safe": True, "budget": list(S.BUDGET), "strict_gap": S.STRICT_GAP,
                               "paths": N_PATHS},
                       label=f"D-538's wider coin: {name}")
    params = {"decision": DECISION, "seed": SEED, "coin_seed": rc.COIN_SEED, "paths": N_PATHS,
              "stops": list(rc.WIDTH_STOPS), "reference_stop": rc.REFERENCE_STOP, "mark_step": rc.MARK_STEP,
              "windows": {k: [rc.ct(v[0]), rc.ct(v[1] % (24 * 60))] for k, v in rc.WINDOWS.items()},
              "unresolved_mark": rc.UNRESOLVED_MARK, "offered_rr": bw["offered_rr"],
              "release_clear_ct": list(rc.RELEASE_CLEAR_CT), "budget": list(S.BUDGET), "strict_gap": S.STRICT_GAP,
              "plan": getattr(I["plan"], "id", None), "walks": bw["walks"], "days": len(bw["days"]),
              "window": [bw["days"][0], bw["days"][-1]], "reference": {"cell": REF_NR, "seed": SEED,
                                                                       "growth_on_required": rg},
              "kill_line": "growth on the required bankroll at the bound (gate row, 0 %, placement off) <= 0 kills a cell",
              "selection": "none here: an all-window wider cell that clears the kill line and grows more at the bound "
                           "than the 25-point news-safe cell at the same seed is marked beats_reference -- a new "
                           "candidate with its own registered test (D-538 (4))",
              "sizing": "the engine's (gf.sizing_rule, campaign.sizing.size_trade); cannot_size = unsized or refused by "
                        "D-272's stand-aside at that tier",
              "cell_seconds": {k: round(v, 1) for k, v in timing.items()}, "workers": int(a.workers),
              "seconds": round(seconds, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(bw["cells"]), parameters=params,
                 notes={"status": READING, "variant_count_rule": f"one per wider cell, under {FAMILY_ID}; the "
                        "reference is D-535's candidate at the screen's seed, not a variant",
                        "cutoff": "kind columns only (resolved_coin.mark_resolution refuses others)"},
                 description="EXPLORATORY (D-538): the news-safe coin re-entering when flat at 37.5 and 50-point stops "
                             "in four windows, through P-14's engine call at the screen's seed; each cell's supply, "
                             "growth at the bound with the kill line and the zero-edge twin; the 25-point news-safe "
                             "reference at the same seed; the engine's sizing at each stop; D-535's and P-14's rows "
                             "beside.")
    pd.set_option("display.width", 250)
    show = [c for c in ("cell", "candidates_per_day", "trades_taken_per_session", "every_r_resolves",
                        "growth_on_required", "growth_on_required_point", "required_p90", "growth_zero_edge_twin",
                        "killed", "beats_reference") if c in res.columns]
    print(res[res["section"].isin(["cell", "reference"])][show].to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
