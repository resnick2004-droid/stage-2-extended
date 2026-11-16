"""EXPLORATORY (D-551): a within-history check of the coin's stop choice -- would D-538's rule, applied to the early
years alone, have picked a stop that also does well on the later years? Selects nothing; read beside P-16 (D-547).

    python scripts/rc_stop_walkforward.py --check --paths 4       # identity, walks, cutoffs and every run; nothing written
    python scripts/rc_stop_walkforward.py --workers 2             # the reading (500 paths); writes the file

**The cells** -- the news-safe all-day coin re-entering when flat (D-525's design with D-533's cut,
`rc_width_screen.build`'s construction) at 25, 37.5 and 50 points (100, 150, 200 MNQ ticks), each built and run on two
spans ALONE: `early` 2020-01-01 .. 2023-12-31 and `late` 2024-01-01 .. 2026-07-16 (the development window's end). On each
span the cutoff (D-212's 5 % for every R the table offers, from the walk's kind columns only,
`resolved_coin.mark_resolution`) is computed on that span's own days, so the marks a span admits use nothing of the
other span. Each span's 0.05 bound is its own (`a3_brk30.check_bounds`, the pooled 21-session-block bound P-15's check
years and `rc_robust`'s years read); the day capacity is the span's own busiest day (`rc_screen.Runner`, the screens'
rule).

**The money side, P-14's exactly** (`rc_screen.Runner`: the no-closure table, the table's own sizing, 20 purchases in 21
days, the strict rule, five Topstep seats, the placement off, 0 % denial), campaign seed 20261131 (the screens'), coin
seed 20261102 (D-521), 500 paths.

**The choice** (`choose_stop`, D-538's rule): on the early span, the stop with the highest growth on the required
bankroll at the bound among the stops whose trades resolve every offered R on that span (`atlas_a3.resolution`); none if
none resolves. Section `choice` reports it, its late-span reading and rank, and the late span's own choice, beside the
full window's choice (37.5 points, D-542/D-544). Nothing is chosen from this file.

**Identity first, refusing:** the 37.5-point all-day news-safe cell built on the full window equals
`rc_width_screen.csv`'s `rc_s150_all` by the pinned content hash (`rc_width_diag.CELL_TRADES_SHA256`).

Writes `results/rc_stop_walkforward.csv` with its manifest (EXPLORATORY; sections `identity`, `early`, `late`, `choice`);
six readings under `D-551:rc_stop_wf`.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any, Sequence

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

SCRIPT = "scripts/rc_stop_walkforward.py"
DECISION = "D-551"
RESULT = "rc_stop_walkforward"
FAMILY_ID = f"{DECISION}:rc_stop_wf"
SEED = S.SEED                              # the screens' campaign seed (D-522 (3), D-538 (3))
N_PATHS = S.N_PATHS
STOPS = (rc.REFERENCE_STOP, *rc.WIDTH_STOPS)        # 25, 37.5, 50 points
SPANS = {"early": ("2020-01-01", "2023-12-31"), "late": ("2024-01-01", "2026-07-16")}
FULL_CHOICE_STOP = 150                     # D-542 / D-544: the full window's choice, read beside
IDENTITY_STOP = 150
READING = "EXPLORATORY (D-551): a within-history check of the coin's stop choice; selects nothing"


# ------------------------------------------------------------------------------------------------ pure parts (tested)


def span_days(days: Sequence[str], lo: str, hi: str) -> list[str]:
    """The trading days inside [lo, hi], sorted (dates as text 'YYYY-MM-DD')."""
    return sorted(str(d) for d in days if lo <= str(d) <= hi)


def check_spans(spans: dict[str, tuple[str, str]], days: Sequence[str]) -> list[str]:
    """The spans must be disjoint, ordered and between them cover every day of the window."""
    out = []
    items = sorted(spans.items(), key=lambda kv: kv[1][0])
    for (a, (_, ahi)), (b, (blo, _)) in zip(items, items[1:]):
        if not ahi < blo:
            out.append(f"spans {a} and {b} overlap")
    covered = set()
    for lo, hi in spans.values():
        covered |= set(span_days(days, lo, hi))
    missing = sorted(set(str(d) for d in days) - covered)
    if missing:
        out.append(f"{len(missing)} days in no span (first {missing[0]})")
    return out


def choose_stop(rows: Sequence[dict]) -> int | None:
    """D-538's rule on one span: the stop with the highest growth on the required bankroll at the bound among the rows
    whose trades resolve every offered R; None when none resolves. Ties go to the narrower stop (fewer choices)."""
    ok = [r for r in rows if bool(r.get("every_r_resolves")) and np.isfinite(float(r.get("growth_on_required", np.nan)))]
    if not ok:
        return None
    best = max(float(r["growth_on_required"]) for r in ok)
    return min(int(r["stop_ticks"]) for r in ok if float(r["growth_on_required"]) >= best - 1e-12)


def rank_of(rows: Sequence[dict], stop: int | None) -> int | None:
    """The stop's rank by growth at the bound among the span's rows (1 = highest), or None."""
    if stop is None:
        return None
    order = sorted(rows, key=lambda r: -float(r["growth_on_required"]))
    for i, r in enumerate(order, 1):
        if int(r["stop_ticks"]) == int(stop):
            return i
    return None


# ------------------------------------------------------------------------------------------------ the cells


def walk_stop(I: dict[str, Any], stop: int, delay: int = rc.DELAY) -> dict[str, Any]:
    """One stop's walk at every mark on every development day (the screens' construction), with what the cells need.
    `delay` (D-602's latency): each entry at the `delay`-th bar with an open after the mark (`fast_walk.entry_bar`);
    the default, `resolved_coin.DELAY` (0), is every earlier caller's walk unchanged."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge.outcomes.collect_core import c_slot

    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    rr_grid = A.rrs(cfg)
    offered_rr = sorted(float(R) for R in zd.policy_rrs(I["plan"]))
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    grid = rc.marks()
    days = L["days"].copy()
    days["date"] = days["date"].astype(str)
    mins = S.walked_minutes(days, grid, cut)
    t0 = time.time()
    arrays = A.bar_arrays(cfg, sorted(mins["date"].unique()))
    walks = A.walk_minutes(mins, arrays, int(delay), float(cfg["contract"]["tick"]), (int(stop),), rr_grid)
    late = "" if int(delay) == rc.DELAY else f" at delay {int(delay)}"
    print(f"  the walk at {stop / 4:g} points{late}: {len(walks)} walks, {time.time() - t0:.0f} s", flush=True)
    return {"walks": walks, "days": sorted(days["date"]), "kinds": dict(zip(days["date"], days["day_kind"].astype(str))),
            "coins": rc.coin_table(days["date"].tolist(), grid), "fees": A.fee_by_stop(fcfg, (int(stop),), tv),
            "rr_grid": rr_grid, "offered_rr": offered_rr, "cut": cut, "clear": c_slot(*rc.RELEASE_CLEAR_CT),
            "crr": float(fcfg["state_policy"]["fresh"]["combine_rr"]), "tv": tv, "slip": float(cfg["slip_ticks"]),
            "keys": sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I["plan"])))}


def cell(W: dict[str, Any], stop: int, days: list[str]) -> dict[str, Any]:
    """The all-day news-safe cell at `stop` on `days` alone: the cutoff read on those days' walks only."""
    import zero_edge_decomposition as zd

    ds = set(days)
    w = W["walks"][W["walks"]["date"].astype(str).isin(ds)]
    cols = ["date", "slot"] + rc.mark_resolution_columns((int(stop),), W["offered_rr"])
    table = rc.mark_resolution(w[cols], (int(stop),), W["offered_rr"])          # kind columns only
    offered = rc.offered_marks(table, int(stop))
    wm = rc.window_marks(offered, "all")
    raw = (rc.cell_trades(w, W["kinds"], wm, int(stop), W["coins"], W["fees"], rr_grid=W["rr_grid"],
                          fresh_rr=W["crr"], tick_value=W["tv"], entry_ticks=W["slip"], cut=W["cut"])
           if wm else pd.DataFrame())
    raw = zd.pad(raw, W["keys"]) if len(raw) else None
    nr = rc.drop_release_minute(raw, W["clear"]) if raw is not None else None
    return {"marks": wm, "trades": nr if (nr is not None and len(nr)) else None,
            "first_mark": rc.ct(wm[0]) if wm else "", "last_mark": rc.ct(wm[-1]) if wm else ""}


def span_row(R: Any, name: str, span: str, stop: int, c: dict[str, Any], days: list[str], n_paths: int,
             rr_grid, bounds: tuple[dict, dict] | None = None) -> dict[str, Any]:
    """`bounds` (D-599's whole-history identity): (e by R, the bound by R) in place of the span's own pooled bound
    (`a3_brk30.check_bounds`); None (every earlier caller) reads the span's own bound as before."""
    import a3_brk30 as B
    import atlas_a3 as A
    import rc_reentry_screen as RS

    t = c["trades"]
    base = {"section": span, "cell": name, "span": span, "span_first": days[0], "span_last": days[-1],
            "sessions": len(days), "stop_ticks": int(stop), "stop_points": stop / 4.0, "marks_offered": len(c["marks"]),
            "first_mark": c["first_mark"], "last_mark": c["last_mark"]}
    if t is None:
        return {**base, "candidates": 0, "every_r_resolves": False, "growth_on_required": float("nan"),
                "killed": True, "note": "no mark the span's cutoff admits"}
    keys = B.rrs(t)
    e_by, lb_by = B.check_bounds(t, days, keys) if bounds is None else (dict(bounds[0]), dict(bounds[1]))
    df = R.run(name, t, days, n_paths, bounds=(e_by, lb_by))
    at = {s: df[(df["shift"] == s) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
          for s in ("point", "lower_bound")}
    res, ok = A.resolution(t, rr_grid)
    gb = float(at["lower_bound"]["pf_growth_on_base_p50"])
    return {**base, "candidates": int(len(t)), "candidates_per_day": float(len(t) / len(days)),
            "capacity": int(B.capacity(t, R.I["L"]["fcfg"])), "every_r_resolves": bool(ok), **res,
            "trades_taken_per_session": RS.taken_per_session(R.sink, name, "lower_bound"),
            "growth_on_required": gb, "growth_on_required_point": float(at["point"]["pf_growth_on_base_p50"]),
            "required_p90": float(at["lower_bound"]["pf_required_p90"]),
            "e_at_fresh_combine_r": float(e_by.get(1.5, np.nan)), "lb_at_fresh_combine_r": float(lb_by.get(1.5, np.nan)),
            "killed": bool(not gb > 0), "reading": READING}


def choice_rows(early: list[dict], late: list[dict]) -> list[dict]:
    pick = choose_stop(early)
    late_pick = choose_stop(late)
    by_late = {int(r["stop_ticks"]): r for r in late}
    lr = by_late.get(pick) if pick is not None else None
    return [{"section": "choice", "early_choice_stop_ticks": pick,
             "early_choice_points": None if pick is None else pick / 4.0,
             "late_growth_of_early_choice": float(lr["growth_on_required"]) if lr else float("nan"),
             "late_resolves_early_choice": bool(lr["every_r_resolves"]) if lr else False,
             "late_rank_of_early_choice": rank_of(late, pick), "late_stops": len(late),
             "late_choice_stop_ticks": late_pick, "full_window_choice_stop_ticks": FULL_CHOICE_STOP,
             "early_choice_equals_late_choice": bool(pick is not None and pick == late_pick),
             "early_choice_equals_full_choice": bool(pick == FULL_CHOICE_STOP),
             "rule": "D-538's: the highest growth on the required bankroll at the bound among stops resolving every "
                     "offered R on the span; ties to the narrower stop",
             "reading": READING}]


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import rc_dev_test as D
    import rc_width_diag as WD

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="identity, walks, cutoffs and every run; nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not a.check and int(a.paths) != N_PATHS:
        print(f"REFUSED ({DECISION}): the reading runs {N_PATHS} paths; a smaller run is --check (writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    print("P-14's inputs and the no-closure plan...", flush=True)
    I = S.inputs()
    R = S.Runner(I, a.workers)
    rows: dict[str, list[dict]] = {"early": [], "late": []}
    idents: list[dict] = []
    span_d: dict[str, list[str]] = {}
    for stop in STOPS:
        W = walk_stop(I, stop)
        if not span_d:
            bad = check_spans(SPANS, W["days"])
            if bad:
                print(f"REFUSED ({DECISION}): " + "; ".join(bad))
                return 3
            span_d = {k: span_days(W["days"], lo, hi) for k, (lo, hi) in SPANS.items()}
        if stop == IDENTITY_STOP:
            full = cell(W, stop, W["days"])
            h = D.trades_hash(full["trades"])
            if h != WD.CELL_TRADES_SHA256:
                print(f"REFUSED ({DECISION}): the 37.5-point full-window cell's content hash {h[:16]} is not the "
                      f"pinned {WD.CELL_TRADES_SHA256[:16]} (rc_width_screen.csv's rc_s150_all)")
                return 3
            print(f"identity HOLDS: the 37.5-point full-window cell = rc_width_screen.csv's rc_s150_all (content hash "
                  f"{h[:16]}; {len(full['trades'])} candidates)", flush=True)
            idents.append({"section": "identity", "cell": "rc_s150_all", "holds": True,
                           "check": "this script's 37.5-point all-day news-safe cell on the full window equals "
                                    "rc_width_screen.csv's rc_s150_all by the pinned content hash "
                                    "(rc_width_diag.CELL_TRADES_SHA256)"})
            del full
        for span, days in span_d.items():
            c = cell(W, stop, days)
            name = f"{rc.reentry_cell_name(stop, 'all')}_{span}"
            t1 = time.time()
            r = span_row(R, name, span, stop, c, days, a.paths, W["rr_grid"])
            rows[span].append(r)
            if a.check:
                print(f"  {name}: {r['candidates']} candidates, {len(c['marks'])} marks "
                      f"({c['first_mark']}..{c['last_mark']}); ran at {a.paths} paths in {time.time() - t1:.0f} s "
                      "-- no growth printed", flush=True)
            else:
                print(f"  {name}: done ({time.time() - t1:.0f} s)", flush=True)
        del W
    if a.check:
        print(f"the identity held; every span x stop ran at {a.paths} paths; nothing written, no reading printed "
              f"(--check). {time.time() - t_all:.0f} s")
        return 0
    ch = choice_rows(rows["early"], rows["late"])
    out = idents + rows["early"] + rows["late"] + ch
    res = pd.DataFrame(out)
    res["reading"] = res["reading"].fillna(READING) if "reading" in res else READING
    counter = VariantCounter(path=rd / "variants.jsonl")
    for span in SPANS:
        for r in rows[span]:
            counter.record(prereg_id=FAMILY_ID, seed=SEED, exploratory=True,
                           params={"study": "D-551's within-history stop check", "cell": r["cell"], "span": span,
                                   "stop_ticks": int(r["stop_ticks"]), "coin_seed": rc.COIN_SEED, "paths": N_PATHS},
                           label=f"D-551's stop check: {r['cell']} (selects nothing)")
    seconds = time.time() - t_all
    params = {"decision": DECISION, "seed": SEED, "coin_seed": rc.COIN_SEED, "paths": N_PATHS, "stops": list(STOPS),
              "spans": {k: list(v) for k, v in SPANS.items()},
              "span_sessions": {k: len(v) for k, v in span_d.items()},
              "cutoff": "D-212's 5 % for every offered R, from the span's own walks' kind columns",
              "bounds": "each span its own pooled 0.05 bound over 21-session blocks (a3_brk30.check_bounds)",
              "capacity": "the span's own busiest day (rc_screen.Runner)", "news_safe": True,
              "choice_rule": "D-538's, on the early span alone; nothing chosen from this file",
              "workers": int(a.workers), "seconds": round(seconds, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=sum(len(v) for v in rows.values()), parameters=params,
                 notes={"status": READING, "variant_count_rule": f"one per span x stop, under {FAMILY_ID}"},
                 description="EXPLORATORY (D-551): the news-safe all-day coin at 25, 37.5 and 50 points on 2020-2023 "
                             "alone and on 2024 to 2026-07-16 alone, each span's own cutoff and bound; D-538's choice "
                             "on the early span and how it reads on the late span; selects nothing.")
    pd.set_option("display.width", 250)
    show = [c for c in ("cell", "candidates_per_day", "trades_taken_per_session", "every_r_resolves",
                        "growth_on_required", "growth_on_required_point", "required_p90", "killed") if c in res.columns]
    print(res[res["section"].isin(["early", "late"])][show].to_string(index=False))
    print(pd.DataFrame(ch).drop(columns=["rule", "reading"]).to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
