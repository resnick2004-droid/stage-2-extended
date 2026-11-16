"""EXPLORATORY (D-602): D-536's slower-hands and calendar-year sections on P-16's own cell (`rc_s150_all`, the
37.5-point news-safe coin), beside `rc150_routing.csv`'s fifty coin sequences; selects nothing.

    python scripts/p16_robust.py --check                   # 300 walked days only (the first 150 of 2020-2023 and of
                                                           #   2024-2026): every identity of construction and of the
                                                           #   engine call, every delay's walk and cutoff, the years
                                                           #   present, the beside's runs, at 4 paths; no reading
                                                           #   printed; nothing written
    python scripts/p16_robust.py --workers 1               # the reading (a clean checkout, D-474)

**The declaration** (DECISIONS.md's D-602 row) is pinned by the sha256 of its line and checked phrase by phrase against
this build's constants (`propedge.research.p16_robust.declaration_problems`, as `rc_stop_fine` pins D-594), and the
constants against the earlier studies' (`rc_screen`, `rc150_dev_test`, `rc150_routing`, `rc_robust`). A difference
refuses.

**The cell** is P-16's: `rc_stop_walkforward.walk_stop` at 150 ticks on every development day (every five-minute mark,
`atlas_a3.walk_minutes`), `rc_stop_walkforward.cell` (D-525 (4)'s cutoff from the walk's kind columns only, the coin
`coin_table` at 20261102, D-533's news-safe cut, the fee at the stop), through P-14's engine call (`rc_screen.Runner`,
as `rc150_routing.run_rule` calls it with no routing rule: the no-closure v12 table sized at the trade's stop, 20
purchases and resets in 21 days, the strict one-at-a-time rule, five Topstep seats, the placement off, 0 % denial),
campaign seed 20261131.

**Latency** (D-602 (1), D-536 (3) as `rc_robust.run_latency`): the walk rerun with every entry at the `delay`-th bar with
an open after the mark (`walk_stop(..., delay=d)`, `fast_walk.entry_bar`), delays 0 (the identity), 1, 3 and 5; the
cutoff re-read on that walk's kind columns on every development day (the marks it admits, and those dropped or added
against delay 0, in `latency_marks`); each run's bound by the era rule on its own trades and its own day capacity (the
engine call's defaults, as `rc_robust`'s latency); 500 paths. Readings: growth on the required bankroll at the bound and
the point, the required bankroll, every offered R's unresolved share overall and in its worst year.

**Years** (D-602 (2), D-536 (4) as `rc_robust.run_years`): the delay-0 cell's trades and days in each calendar year
(`fv3d_lever_test.in_period`; 2026 to 2026-07-16) -- the cutoff is the full window's, as `run_years` slices the full
cell -- with the year's own pooled 0.05 bound (`a3_brk30.check_bounds` over the full cell's R), the full cell's day
capacity (`a3_brk30.capacity`), the campaign's 504-session horizon resampling that year's days; 500 paths.

**Beside** (D-602 (3)): the fifty `R0_longest_waiting` G2 rows of `results/rc150_routing.csv` (sha256 pinned; coin
seeds 20261600 + i, 200 paths, seed 20261131): the share growing at the bound and the quantiles; P-16's own coin run
the same way (200 paths, the same call) and its place among them. The file holds no 200-path row of the own coin, so
it is run here, and the comparability is checked by rebuilding coin 20261600 (`rc150_routing.coin_cell`) and
reproducing its G2 row (refusing).

**Identities, refusing** (D-602 (4)): the delay-0 cell built through the latency path (`walk_stop(..., delay=0)` -- the
default every earlier caller uses, so the same walk) has P-16's content hash (`rc150_dev_test.TRADES_SHA256`) and its
run at 500 paths reproduces `rc_width_screen.csv`'s `rc_s150_all` (growth on the required bankroll at the bound and the
point, the required bankroll, to 1e-9); the coin swap at 20261102 (`rc150_routing.coin_cell`) rebuilds the cell; in
--check, this script's engine call equals `rc150_routing.run_rule`'s.

**Resume** (D-540, `rc_robust.Resume`): each finished engine run kept outside the checkout, keyed by commit and path
counts; `--no-resume`, `--resume-dir`; off in --check.

Writes `results/p16_robust.csv` (EXPLORATORY; sections declaration, identity, latency, latency_marks, years,
beside_coins, beside_summary) with its manifest; one variant record per reading family (latency, years) under
`D-602:p16_robust`.
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

import pandas as pd  # noqa: E402

import rc_robust as RR  # noqa: E402
import rc_screen as S  # noqa: E402
from propedge.research import p16_robust as P  # noqa: E402
from propedge.research import resolved_coin as rc  # noqa: E402

SCRIPT = "scripts/p16_robust.py"
DECISION = P.DECISION
RESULT = P.RESULT
CHECK_DAYS = 300                           # the first 150 walked days of 2020-2023 and of 2024-2026
CHECK_PATHS = 4
CHECK_SPANS = (("2020-01-01", "2023-12-31"), ("2024-01-01", P.LAST_DAY))


class Resume(RR.Resume):
    """`rc_robust.Resume` (D-540) under this study's own file name."""

    def __init__(self, folder: Path | None, key: str):
        import json

        self.path = None if folder is None else Path(folder) / f"{RESULT}_{key}.jsonl"
        self.rows = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["row"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)


_cached = RR._cached


def with_reading(out: pd.DataFrame) -> pd.DataFrame:
    """D-602's READING as column 1 of every row (an imported row's own `reading` replaced, D-597's lesson)."""
    out = out.drop(columns=["reading"], errors="ignore")
    out.insert(1, "reading", P.READING)
    return out


# ------------------------------------------------------------------------------------------------ the engine call


def run(I: dict, label: str, t: pd.DataFrame, days: list[str], n_paths: int, workers: int, *, bounds=None,
        capacity: int | None = None) -> dict[str, Any]:
    """P-16's engine call (`rc150_routing.run_rule` with no routing rule and no twin: `rc_screen.Runner.run`, seed
    20261131), with the year's bound and the full cell's capacity when given; the reading at 0 % and trades a session."""
    import rc_reentry_screen as RS

    R = S.Runner(I, workers)
    df = R.run(label, t, days, n_paths, bounds=bounds, capacity=capacity)
    return P.reading(df, RS.taken_per_session(R.sink, label, "lower_bound"))


def cell_facts(t: pd.DataFrame, days: list[str], fcfg: dict, offered_rr) -> dict[str, Any]:
    """A trade set's construction and resolution (no outcome of the engine): candidates, the busiest-day capacity,
    the long share, every offered R's unresolved share overall and in its worst year (`atlas_a3.resolution`, D-212)."""
    import a3_brk30 as B
    import atlas_a3 as A
    import rc_dev_test as D

    res, ok = A.resolution(t, offered_rr)
    return {"candidates": int(len(t)), "candidates_per_day": float(len(t) / max(1, len(days))),
            "capacity_own": int(B.capacity(t, fcfg)), "long_share": float((t["side"] == "long").mean()), **res,
            "every_offered_r_resolves": bool(ok), "cell_trades_sha256": D.trades_hash(t)}


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke on a few days: every identity of construction, every "
                                                         "run's machinery; nothing read, nothing written")
    ap.add_argument("--days", type=int, default=None, help=f"--check: walked days ({CHECK_DAYS})")
    ap.add_argument("--paths", type=int, default=None, help=f"--check: paths a run ({CHECK_PATHS})")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and any(x is not None for x in (a.days, a.paths)):
        print(f"REFUSED ({DECISION}): the reading runs every day at {P.N_PATHS} / {P.BESIDE_PATHS} paths; a smaller "
              "run is --check (writes nothing).")
        return 2
    if not a.check and int(a.workers) != 1:
        print(f"REFUSED ({DECISION}): the reading runs at workers 1.")
        return 2

    import a3_brk30 as B
    import a3_resolution_map as m0
    import fv3d_lever_test as lt
    import rc150_dev_test as R150
    import rc150_payout_screen as PS
    import rc150_routing as RT
    import rc_dev_test as D
    import rc_stop_walkforward as WF

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, sha256_of, write_result

    full = not a.check
    n_paths = P.N_PATHS if full else int(a.paths or CHECK_PATHS)
    b_paths = P.BESIDE_PATHS if full else int(a.paths or CHECK_PATHS)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    timing: dict[str, float] = {}

    # ---- the declaration and the earlier studies' constants
    decl = P.declaration()
    bad = P.declaration_problems(decl)
    fixed = {"campaign seed": (S.SEED, P.CAMPAIGN_SEED), "paths": (S.N_PATHS, P.N_PATHS),
             "P-16's stop": (R150.STOP, P.STOP), "P-16's cell": (R150.CELL, P.CELL),
             "routing stop": (RT.STOP, P.STOP), "routing cell": (RT.CELL, P.CELL),
             "routing reference": (RT.REFERENCE, P.ROUTING_REF), "routing coins": (tuple(RT.COIN_SEEDS),
                                                                                   P.ROUTING_COIN_SEEDS),
             "routing paths": (RT.G2_PATHS, P.BESIDE_PATHS), "coin seed": (rc.COIN_SEED, P.COIN_SEED),
             "entry delay": (rc.DELAY, P.BASE_DELAY), "D-536's delays": (RR.DELAYS, P.DELAYS),
             "D-536's years": (RR.YEARS, P.YEARS), "D-536's last day": (RR.LAST_DAY, P.LAST_DAY),
             "screen file": (PS.SCREEN_FILE, P.SCREEN_FILE)}
    bad += [f"{k}: the engine's {v[0]!r} against D-602's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    shas = {f: sha256_of(RESULTS_DIR / f) for f in (P.SCREEN_FILE, P.ROUTING_FILE)}
    if shas[P.SCREEN_FILE] != R150.SCREEN_SHA256:
        bad.append(f"{P.SCREEN_FILE} is not the file P-16 was registered on")
    if shas[P.ROUTING_FILE] != P.ROUTING_SHA256:
        bad.append(f"{P.ROUTING_FILE} is not the pinned file ({shas[P.ROUTING_FILE][:16]})")
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-602's declaration -- " + "; ".join(bad))
        return 2
    print(f"the declaration HOLDS: {DECISION}'s row (sha256 {decl['sha256'][:16]}); {P.CELL}, delays "
          f"{list(P.DELAYS)}, years {P.YEARS[0]}..{P.YEARS[-1]}", flush=True)
    srow = PS.screen_row(RESULTS_DIR)                       # read through its manifest
    routing = read_result(RESULTS_DIR / P.ROUTING_FILE)
    g2 = routing[(routing["section"].astype(str) == "g2") & (routing["rule"].astype(str) == P.ROUTING_REF)]
    if sorted(g2["coin_seed"].astype(float).astype(int)) != list(P.ROUTING_COIN_SEEDS):
        print(f"REFUSED ({DECISION}): {P.ROUTING_FILE}'s {P.ROUTING_REF} G2 rows are not the fifty declared sequences.")
        return 2
    cmp_row = g2[g2["coin_seed"].astype(float).astype(int) == P.COMPARABLE_SEED].iloc[0]

    # ---- the inputs
    print("P-14's inputs and the no-closure plan...", flush=True)
    I = S.inputs()
    L = I["L"]
    fcfg = L["fcfg"]
    if int(fcfg["gate"]["campaign"]["horizon_days"]) != P.HORIZON:
        print(f"REFUSED ({DECISION}): the campaign's horizon is not {P.HORIZON} sessions.")
        return 2
    if a.check:                                    # a smoke: the first N/2 walked days of each span
        dk = L["days"].copy()
        dk["date"] = dk["date"].astype(str)
        dk = dk.sort_values("date").reset_index(drop=True)
        wk = dk[dk["day_kind"].astype(str).isin(m0.WALK_DAY_KINDS)]
        half = max(int(a.days or CHECK_DAYS) // 2, 1)
        pick = [d for lo, hi in CHECK_SPANS for d in wk[(wk["date"] >= lo) & (wk["date"] <= hi)]["date"][:half]]
        L = {**L, "days": dk[dk["date"].isin(pick)].reset_index(drop=True)}
        I = {**I, "L": L}
    fresh = fcfg["state_policy"]["fresh"]
    crr, frr = float(fresh["combine_rr"]), float(fresh["funded_rr"])
    idents: list[dict] = []

    def ident(name: str, check: str) -> None:
        idents.append({"section": "identity", "identity": name, "holds": True, "check": check})
        print(f"identity ({name}) HOLDS: {check[:120]}", flush=True)

    resume = None
    if full and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{b_paths}")

    # ---- delay 0 through the latency path: P-16's cell, its identities, the beside's trade sets
    t0 = time.time()
    W0 = WF.walk_stop(I, P.STOP, delay=P.BASE_DELAY)
    days = list(W0["days"])
    offered = tuple(float(x) for x in W0["offered_rr"])
    c0 = WF.cell(W0, P.STOP, days)
    t_ref = c0["trades"]
    h_ref = D.trades_hash(t_ref)
    base_marks = list(c0["marks"])
    timing["walk_0"] = time.time() - t0
    if full:
        bad = []
        if int(len(t_ref)) != int(srow["candidates"]):
            bad.append(f"{len(t_ref)} candidates against the screen's {int(srow['candidates'])}")
        if h_ref != R150.TRADES_SHA256:
            bad.append(f"content hash {h_ref[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
        if bad:
            print(f"REFUSED ({DECISION}): the delay-0 cell is not P-16's {P.CELL} -- " + "; ".join(bad))
            return 3
        ident("a", f"the delay-0 cell through the latency path (rc_stop_walkforward.walk_stop(delay=0), cell on every "
                   f"development day): {len(t_ref)} candidates as {P.SCREEN_FILE}'s {P.CELL}; content hash {h_ref} = "
                   "rc150_dev_test.TRADES_SHA256 (P-16's)")
    else:
        print(f"identity (a): the pinned count and content hash are not comparable on a --check subset ({len(days)} "
              "days); the construction identities run on it", flush=True)
    if D.trades_hash(RT.coin_cell(W0, I, P.COIN_SEED, days)) != h_ref:
        print(f"REFUSED ({DECISION}): rc150_routing.coin_cell at seed {P.COIN_SEED} does not rebuild the cell.")
        return 3
    ident("c", f"rc150_routing.coin_cell at the candidate's seed {P.COIN_SEED} rebuilds the delay-0 cell's content hash "
               "(the beside's construction is the cell's)")
    t_cmp = RT.coin_cell(W0, I, P.COMPARABLE_SEED, days)
    del W0

    # ---- the latency family (delay 0 first: identity (b))
    lat_rows: list[dict] = []
    marks_rows: list[dict] = []
    for d in (P.BASE_DELAY, *P.DELAYS):
        t0 = time.time()
        if d == P.BASE_DELAY:
            t, marks = t_ref, base_marks
        else:
            W = WF.walk_stop(I, P.STOP, delay=int(d))
            if list(W["days"]) != days or tuple(float(x) for x in W["offered_rr"]) != offered:
                print(f"REFUSED ({DECISION}): the walk at delay {d} has other days or offered R than delay 0's.")
                return 3
            c = WF.cell(W, P.STOP, days)
            t, marks = c["trades"], list(c["marks"])
            del W, c
            if t is None:
                print(f"REFUSED ({DECISION}): the cutoff admits no mark at delay {d}.")
                return 3
        timing[f"walk_{d}"] = timing.get(f"walk_{d}", 0.0) + time.time() - t0
        facts = cell_facts(t, days, fcfg, offered)
        label = f"latency {int(d)}"
        t0 = time.time()

        def make(t=t, label=label):
            return run(I, label, t, days, n_paths, a.workers)

        r = _cached(resume, label, make)
        timing[f"latency_{d}"] = time.time() - t0
        row = {"section": "latency", "cell": P.CELL, "delay_bars": int(d), "identity_row": bool(d == P.BASE_DELAY),
               "paths": int(n_paths), "marks_admitted": len(marks), **facts, **r}
        if d == P.BASE_DELAY:
            if full:
                prob = P.row_problems(row, srow, what=P.SCREEN_FILE)
                if prob:
                    print(f"REFUSED ({DECISION}): delay 0 through the latency path is not {P.SCREEN_FILE}'s {P.CELL} "
                          "-- " + "; ".join(prob))
                    return 3
                ident("b", f"delay 0 through the latency path at seed {P.CAMPAIGN_SEED}, {P.N_PATHS} paths reproduces "
                           f"{P.SCREEN_FILE}'s {P.CELL} (growth at the bound and point, the required bankroll)")
            else:
                ref = RT.run_rule(I, "run_rule identity", None, t, days, n_paths, a.workers)
                ref.pop("df")
                prob = P.row_problems(row, ref, what="rc150_routing.run_rule")
                if prob:
                    print(f"REFUSED ({DECISION}): this script's engine call is not rc150_routing.run_rule's -- "
                          + "; ".join(prob))
                    return 3
                ident("d", "this script's engine call equals rc150_routing.run_rule's (no rule, no twin) on the delay-0 "
                           f"cell at {n_paths} paths")
        else:
            marks_rows.append({"section": "latency_marks", "cell": P.CELL, "delay_bars": int(d),
                               **P.marks_change(base_marks, marks)})
        lat_rows.append(row)
        print(f"  {label}: done ({timing[f'latency_{d}']:.0f} s)", flush=True)

    # ---- the years family (D-536 (4) as rc_robust.run_years: the full cell sliced)
    yr_rows: list[dict] = []
    cap = B.capacity(t_ref, fcfg)
    keys = B.rrs(t_ref)
    for y in P.YEARS:
        lo, hi = P.year_span(y)
        ty, dy = lt.in_period(t_ref, days, lo, hi)
        if not len(ty):
            if full:
                print(f"REFUSED ({DECISION}): no trade in {y}.")
                return 3
            continue
        ey, lby = B.check_bounds(ty, dy, keys)
        label = f"year {int(y)}"
        t0 = time.time()

        def make(ty=ty, dy=dy, ey=ey, lby=lby, label=label):
            return run(I, label, ty, dy, n_paths, a.workers, bounds=(ey, lby), capacity=cap)

        r = _cached(resume, label, make)
        timing[f"year_{y}"] = time.time() - t0
        facts = cell_facts(ty, dy, fcfg, offered)
        yr_rows.append({"section": "years", "cell": P.CELL, "year": int(y), "span_first": dy[0], "span_last": dy[-1],
                        "sessions": len(dy), "capacity_used": int(cap), "paths": int(n_paths), **facts,
                        "bound": "the year's own pooled 0.05 bound (a3_brk30.check_bounds)",
                        "e_at_fresh_combine_r": float(ey.get(crr, float("nan"))),
                        "lb_at_fresh_combine_r": float(lby.get(crr, float("nan"))),
                        "e_at_fresh_funded_r": float(ey.get(frr, float("nan"))),
                        "lb_at_fresh_funded_r": float(lby.get(frr, float("nan"))), **r})
        print(f"  {label}: done ({timing[f'year_{y}']:.0f} s)", flush=True)

    # ---- beside: the fifty coin sequences, P-16's own coin run the same way
    t0 = time.time()

    def make_cmp():
        return run(I, f"beside {P.COMPARABLE_SEED}", t_cmp, days, b_paths, a.workers)

    rc_cmp = _cached(resume, f"beside {P.COMPARABLE_SEED}", make_cmp)
    if full:
        prob = P.row_problems(rc_cmp, cmp_row, what=f"{P.ROUTING_FILE}'s G2 row")
        if prob:
            print(f"REFUSED ({DECISION}): coin {P.COMPARABLE_SEED} rebuilt here is not {P.ROUTING_FILE}'s "
                  f"{P.ROUTING_REF} G2 row -- " + "; ".join(prob))
            return 3
        ident("e", f"coin {P.COMPARABLE_SEED} rebuilt (rc150_routing.coin_cell) and run here at {P.BESIDE_PATHS} paths "
                   f"reproduces {P.ROUTING_FILE}'s {P.ROUTING_REF} G2 row: P-16's own coin's run is comparable")

    def make_own():
        return run(I, f"beside {P.COIN_SEED}", t_ref, days, b_paths, a.workers)

    rc_own = _cached(resume, f"beside {P.COIN_SEED}", make_own)
    timing["beside"] = time.time() - t0
    beside_rows = [{"section": "beside_coins", "cell": P.CELL, "coin_seed": int(s), "own_coin": bool(s == P.COIN_SEED),
                    "paths": int(b_paths), "source": src, **r}
                   for s, src, r in ((P.COIN_SEED, "run here (no such row in the file)", rc_own),
                                     (P.COMPARABLE_SEED, f"run here; reproduces {P.ROUTING_FILE}'s G2 row", rc_cmp))]
    summary = {"section": "beside_summary", "cell": P.CELL, "source": f"{P.ROUTING_FILE}'s fifty {P.ROUTING_REF} G2 "
               f"rows (coin seeds {P.ROUTING_COIN_SEEDS[0]} + i, {P.BESIDE_PATHS} paths, seed {P.CAMPAIGN_SEED})",
               **P.beside_summary(g2["growth_on_required"].astype(float).tolist(), rc_own["growth_on_required"])}

    seconds = time.time() - t_all
    if a.check:
        print("timings (s): " + ", ".join(f"{k} {v:.0f}" for k, v in timing.items()))
        print(f"--check done: the construction identities and the engine call on {len(days)} days; delays "
              f"{[P.BASE_DELAY, *P.DELAYS]} walked and cut; years {[r['year'] for r in yr_rows]}; the beside's two "
              f"runs; {n_paths} paths; no reading printed; nothing written. {seconds:.0f} s")
        return 0
    decl_row = {"section": "declaration", "holds": True,
                "check": f"DECISIONS.md's {DECISION} row sha256 {decl['sha256']} (LF line); every phrase and constant "
                         f"agrees; {', '.join(f'{k} sha256 {v}' for k, v in shas.items())}"}
    out = with_reading(pd.DataFrame([decl_row] + idents + lat_rows + marks_rows + yr_rows + beside_rows + [summary]))
    counter = VariantCounter(path=rd / "variants.jsonl")
    for fam in P.FAMILIES:
        counter.record(prereg_id=P.FAMILY_ID, seed=P.CAMPAIGN_SEED, exploratory=True,
                       params={"study": "D-602's robustness of P-16's cell", "family": fam, "cell": P.CELL,
                               "coin_seed": P.COIN_SEED, "campaign_seed": P.CAMPAIGN_SEED, "paths": P.N_PATHS,
                               "delays_bars": list(P.DELAYS) if fam == "latency" else None,
                               "years": list(P.YEARS) if fam == "years" else None},
                       label=f"{DECISION}'s robustness reading: {fam} ({P.CELL}; selects nothing)")
    write_result(out, RESULT, script=SCRIPT, seed=P.CAMPAIGN_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(P.FAMILIES),
                 parameters={"decision": DECISION, "family": P.FAMILY_ID, "declaration_sha256": decl["sha256"],
                             "cell": P.CELL, "stop_ticks": P.STOP, "coin_seed": P.COIN_SEED,
                             "campaign_seed": P.CAMPAIGN_SEED, "n_paths": P.N_PATHS, "delays_bars": list(P.DELAYS),
                             "years": list(P.YEARS), "last_day": P.LAST_DAY, "horizon": P.HORIZON,
                             "beside_paths": P.BESIDE_PATHS, "offered_rr": list(offered), "cell_trades_sha256": h_ref,
                             "reference_files_sha256": shas,
                             "latency": "walk_stop(delay=d), the cutoff re-read on each walk; each run's own era bound "
                                        "and day capacity",
                             "years_rule": "the full cell's trades in the year (cutoff from the full window), the "
                                           "year's own pooled bound (a3_brk30.check_bounds), the full cell's day "
                                           "capacity, the 504-session horizon",
                             "timing_seconds": {k: round(v, 1) for k, v in timing.items()},
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": P.READING, "selection": "none -- no delay, year or seed is chosen from this file "
                                                          "(D-602 (5))"},
                 description="EXPLORATORY (D-602): P-16's news-safe all-day 37.5-point coin with entries 1, 3 and 5 "
                             "bars late (the cutoff re-read on each walk) and on each calendar year 2020 .. 2026-07-16 "
                             "alone (its own pooled bound, the cell's capacity), 500 paths; beside, rc150_routing's "
                             "fifty coin sequences and the own coin's place among them; never a gate.")
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
