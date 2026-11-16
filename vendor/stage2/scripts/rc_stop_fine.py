"""EXPLORATORY (D-594): a finer stop-width screen of P-16's coin -- 40, 43.75 and 47.5 points (160, 175 and 190 MNQ
ticks) against P-16's 37.5-point cell, each cell P-16's except the stop; D-594's four guards in order, the first failure
ending the cell; selects nothing by itself.

    python scripts/rc_stop_fine.py --check                 # 300 walked days only (the first 150 of each span): the
                                                           #   construction identities, the sizing and the cap, every
                                                           #   guard's and every beside's machinery on every cell at
                                                           #   4 paths, 2 coins, 2 journey starts; no reading printed;
                                                           #   nothing written
    python scripts/rc_stop_fine.py --workers 1             # the reading (a clean checkout, D-474)

**The declaration** (DECISIONS.md's D-594 row) is pinned by the sha256 of its line and checked phrase by phrase against
this build's constants (`propedge.research.rc_stop_fine.declaration_problems`, as `s3_latency` pins D-590), with the
engine's constants as the earlier screens carry them (`rc_screen`, `rc150_routing`, `rc_stop_walkforward`). A
difference refuses.

**Each cell** (`rc_stop_walkforward.walk_stop` / `cell` at the cell's stop on every development day -- the walk at
every five-minute mark through `atlas_a3.walk_minutes` as `rc_width_screen.build` walks it, the cutoff
`resolved_coin.mark_resolution` at that stop from the walk's kind columns only, the coin `coin_table` seeded 20261102,
D-533's news-safe cut, the fee `atlas_a3.fee_by_stop` at the stop) through P-14's engine call (`rc_screen.Runner`: the
no-closure v12 table sized by the engine's `SizingRule` at the trade's stop in whole micros, 20 purchases and resets in
21 days, the strict one-at-a-time rule, five Topstep seats, the placement off, 0 % denial). Section `sizing`
(`resolved_coin.width_sizing`) reads what every trading leaf of the table buys at each stop and allowance tier, and
flags any leaf a stop cannot size (reported, never re-solved: D-538 (2)).

**Identities, refusing** (D-594 (4)): the 150-tick cell's trades are P-16's -- its count as `rc_width_screen.csv`'s
`rc_s150_all` and its content hash `rc150_dev_test.TRADES_SHA256` -- and its paired run at seed 20261131, 500 paths
reproduces that row (growth on the required bankroll at the bound and point, the required bankroll); its span rows equal
`rc_stop_walkforward.csv`'s `rc_s150_all_early` / `_late` (D-551's own file; `rc150_routing.csv`'s R0 G3 rows carry the
same values and are checked too); its coin-sequence rows equal `rc150_routing.csv`'s R0 G2 rows; at every stop the coin
swap at the candidate's seed rebuilds the cell's content hash (guard (d)'s construction is the cell's).

**Guards, in D-594's order** (`rc_stop_fine.GUARDS`): (a) every offered R resolves (`atlas_a3.resolution` on the
table's offered R: at most 5 % unresolved overall and in the worst year); (b) paired growth at the bound above the
150-tick cell's by more than 0.05; (c) not below it on 2020-2023 or on 2024-01-01 .. 2026-07-16 alone, each span's own
cutoff and bound (`rc_stop_walkforward.span_row`); (d) at least 40 of 50 coin sequences (20261600 + i, 200 paths) won
against the 150-tick cell under the same sequence. The first failing guard ends the cell; the rest are `not_run`.

**Beside, deciding nothing** (D-594 (3)), for every cell that reaches guard (b): the cell with its funded leg capped to
the 150-tick cell's dollars (`resolved_coin.funded_cap_rule` at 150 / stop, and its zero-edge twin under the same cap,
D-542's form); e and its bound at the fresh Combine's R (1.5) and the fresh funded R (3); the cost in R by exit kind
(each stop's arithmetic for every stop, and the cell's realised costs at the two fresh R); the trades taken a session;
D-518's journey on the verdict arm and D-509's four slice lines against FV3-C (`rc150_routing.journey_and_lines`; FV3-C's
slices read from `customer_slices.csv`, pinned, never rerun). The 150-tick cell's e, bound and costs are written beside
it; its journey is `rc150_routing.csv`'s R0 rows (never rerun).

**Resume** (D-540, `rc_robust.Resume`): each finished engine run kept outside the checkout, keyed by commit and counts;
`--no-resume`, `--resume-dir`; off in --check.

Writes `results/rc_stop_fine.csv` (EXPLORATORY; sections declaration, identity, sizing, funded_sizing,
funded_cap_rounding, cost, marks, g1, edge, cost_by_kind, capped, journey, slice_lines, g3, g2, g2_summary, guard,
verdict) with its manifest; three variants under `D-594:rc_stop_fine`.
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

import rc_robust as RR  # noqa: E402
import rc_screen as S  # noqa: E402
from propedge.research import rc_stop_fine as F  # noqa: E402
from propedge.research import resolved_coin as rc  # noqa: E402

SCRIPT = "scripts/rc_stop_fine.py"
DECISION = F.DECISION
RESULT = F.RESULT
FAMILY_ID = F.FAMILY_ID
REF = F.REF_CELL
CHECK_DAYS = 300                           # each span's first 150: the 126-day slices exist (the four lines)
CHECK_STARTS = 2
READING = ("EXPLORATORY (D-594): P-16's coin at 40, 43.75 and 47.5 points against the 37.5-point cell -- D-594's four "
           "guards in order, the first failure ending the cell; selects nothing by itself")


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


# ------------------------------------------------------------------------------------------------ the cells


def coin_trades(W: dict, I: dict, stop: int, seed: int, days: list[str]) -> pd.DataFrame | None:
    """The cell's trades at `stop` with the coin's seed replaced -- `rc150_routing.coin_cell` at any stop: the same
    walk, `resolved_coin.coin_table` re-drawn over the development days and every mark."""
    import rc_stop_walkforward as WF

    dd = I["L"]["days"]["date"].astype(str).tolist()
    return WF.cell({**W, "coins": rc.coin_table(dd, rc.marks(), seed=int(seed))}, int(stop), days)["trades"]


def marks_table(W: dict, stop: int) -> pd.DataFrame:
    """The cutoff's reading at the stop on the walk's days (kind columns only, `resolved_coin.mark_resolution`)."""
    cols = ["date", "slot"] + rc.mark_resolution_columns((int(stop),), W["offered_rr"])
    return rc.mark_resolution(W["walks"][cols], (int(stop),), W["offered_rr"])


def supply_row(name: str, stop: int, c: dict, days: list[str], fcfg: dict, h: str, res_off: dict, ok_off: bool,
               ok_grid: bool) -> dict[str, Any]:
    """A cell's construction and supply (no outcome): marks, candidates, the busiest day, the capacity, the long share,
    each offered R's unresolved share overall and in its worst year, the trades' content hash."""
    import a3_brk30 as B

    t = c["trades"]
    base = {"section": "g1", "cell": name, "stop_ticks": int(stop), "stop_points": int(stop) / 4.0,
            "window": F.WINDOW, "marks_offered": len(c["marks"]), "first_mark": c["first_mark"],
            "last_mark": c["last_mark"], "days": len(days)}
    if t is None:
        return {**base, "candidates": 0, "every_offered_r_resolves": False, "every_grid_r_resolves": False,
                "note": "no mark the cutoff admits"}
    return {**base, "candidates": int(len(t)), "candidates_per_day": float(len(t) / len(days)),
            "busiest_day": int(B.busiest(t)), "capacity": int(B.capacity(t, fcfg)),
            "long_share": float((t["side"] == "long").mean()), **res_off, "every_offered_r_resolves": bool(ok_off),
            "every_grid_r_resolves": bool(ok_grid), "cell_trades_sha256": h}


def edge_and_costs(I: dict, name: str, t: pd.DataFrame, days: list[str]) -> list[dict[str, Any]]:
    """Beside: e and its bound at the fresh Combine's and funded R (the era rule's reading, `atlas_a3.bounds`, the one
    the engine shifts by) and the cell's realised cost in R by exit kind at those two R."""
    import a3_brk30 as B
    import atlas_a3 as A

    L = I["L"]
    fresh = L["fcfg"]["state_policy"]["fresh"]
    crr, frr = float(fresh["combine_rr"]), float(fresh["funded_rr"])
    _, e_by, lb_by, _, _ = A.bounds(t, days, B.rrs(t), L["cfg"])
    out = [{"section": "edge", "cell": name, **F.edge_row(e_by, lb_by, crr, frr)}]
    for R in (crr, frr):
        out += [{"section": "cost_by_kind", "cell": name, **r} for r in F.cost_by_kind(t, R)]
    return out


# ------------------------------------------------------------------------------------------------ main


def with_reading(out: pd.DataFrame) -> pd.DataFrame:
    """This study's READING as column 1 of every row. Rows built by imported helpers (the journey, the slice lines,
    the paired readings) may already carry another study's `reading` column; this file is D-594's, so every row is
    labelled with D-594's text (D-597: the full run's write step failed on the duplicate column)."""
    out = out.drop(columns=["reading"], errors="ignore")
    out.insert(1, "reading", READING)
    return out


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke on a few days: every identity of construction, every "
                                                         "guard's and beside's machinery; nothing read, nothing written")
    ap.add_argument("--days", type=int, default=None,
                    help=f"--check: walk only N walked days, the first N/2 of each span ({CHECK_DAYS})")
    ap.add_argument("--paths", type=int, default=None, help="--check: G1, capped and span paths (4)")
    ap.add_argument("--g2-paths", type=int, default=None, help="--check: coin-sequence paths (4)")
    ap.add_argument("--coins", type=int, default=None, help="--check: the first coin sequences (2)")
    ap.add_argument("--starts", type=int, default=None, help=f"--check: the journey's first starts ({CHECK_STARTS})")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and any(x is not None for x in (a.days, a.paths, a.g2_paths, a.coins, a.starts)):
        print(f"REFUSED ({DECISION}): the reading runs every day, {F.N_PATHS} / {F.G2_PATHS} paths, "
              f"{len(F.COIN_SEEDS)} coins and every start; a smaller run is --check (writes nothing).")
        return 2
    if not a.check and int(a.workers) != 1:
        print(f"REFUSED ({DECISION}): the reading runs at workers 1.")
        return 2

    import a3_brk30 as B
    import a3_resolution_map as m0
    import atlas_a3 as A
    import rc150_dev_test as R150
    import rc150_payout_screen as PS
    import rc150_routing as RT
    import rc_dev_test as D
    import rc_stop_walkforward as WF
    import rc_width_screen as WS
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_manifest, read_result, write_result

    full = not a.check
    n_paths = (a.paths or 4) if a.check else F.N_PATHS
    g2_paths = (a.g2_paths or 4) if a.check else F.G2_PATHS
    n_coins = (a.coins or 2) if a.check else len(F.COIN_SEEDS)
    starts = (a.starts or CHECK_STARTS) if a.check else None
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    timing: dict[str, float] = {}

    # ---- the declaration and the engine's constants
    decl = F.declaration()
    bad = F.declaration_problems(decl)
    fixed = {"campaign seed": (S.SEED, F.CAMPAIGN_SEED), "paths": (S.N_PATHS, F.N_PATHS),
             "coin seeds": (tuple(RT.COIN_SEEDS), tuple(F.COIN_SEEDS)), "g2 paths": (RT.G2_PATHS, F.G2_PATHS),
             "g2 wins": (RT.G2_WINS, F.G2_WINS), "margin": (RT.MARGIN, F.MARGIN),
             "spans": ({k: tuple(v) for k, v in WF.SPANS.items()}, {k: tuple(v) for k, v in F.SPANS.items()}),
             "reference stop": (RT.STOP, F.REFERENCE_STOP), "reference cell": (RT.CELL, REF),
             "P-16's stop": (R150.STOP, F.REFERENCE_STOP), "P-16's cell": (R150.CELL, REF),
             "coin seed": (rc.COIN_SEED, F.COIN_SEED), "mark step": (rc.MARK_STEP, 5),
             "unresolved line": (A.UNRESOLVED_MAX, F.UNRESOLVED_MAX), "screen file": (PS.SCREEN_FILE, F.SCREEN_FILE)}
    bad += [f"{k}: the engine's {v[0]!r} against D-594's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-594's declaration -- " + "; ".join(bad))
        return 2
    print(f"the declaration HOLDS: {DECISION}'s row (sha256 {decl['sha256'][:16]}); cells {list(F.STOPS)} ticks "
          f"against {F.REFERENCE_STOP}", flush=True)

    # ---- the files the reference must reproduce (each read through its manifest)
    srow = PS.screen_row(RESULTS_DIR)
    wf_rows = read_result(RESULTS_DIR / F.WALKFORWARD_FILE)
    routing = read_result(RESULTS_DIR / F.ROUTING_FILE)
    shas = {f: read_manifest(RESULTS_DIR / f).sha256 for f in (F.SCREEN_FILE, F.WALKFORWARD_FILE, F.ROUTING_FILE)}
    if shas[F.SCREEN_FILE] != R150.SCREEN_SHA256:
        print(f"REFUSED ({DECISION}): {F.SCREEN_FILE} is not the file P-16 was registered on "
              f"({shas[F.SCREEN_FILE][:16]} against {R150.SCREEN_SHA256[:16]})")
        return 2

    def wf_row(span: str) -> pd.Series:
        r = wf_rows[(wf_rows["section"].astype(str) == span) & (wf_rows["cell"].astype(str) == f"{REF}_{span}")]
        if len(r) != 1:
            raise SystemExit(f"REFUSED ({DECISION}): {F.WALKFORWARD_FILE} holds {len(r)} {REF}_{span} rows")
        return r.iloc[0]

    def routing_row(section: str, **match) -> pd.Series:
        r = routing[(routing["section"].astype(str) == section) & (routing["rule"].astype(str) == F.ROUTING_REF)]
        for k, v in match.items():
            r = r[r[k].astype(float).astype(int) == int(v)] if k == "coin_seed" else r[r[k].astype(str) == str(v)]
        if len(r) != 1:
            raise SystemExit(f"REFUSED ({DECISION}): {F.ROUTING_FILE} holds {len(r)} {F.ROUTING_REF} {section} rows "
                             f"for {match}")
        return r.iloc[0]

    # ---- the inputs
    print("P-14's inputs and the no-closure plan...", flush=True)
    I = S.inputs()
    L = I["L"]
    fcfg, tv = L["fcfg"], float(L["tv"])
    offered = tuple(sorted(float(R) for R in zd.policy_rrs(I["plan"])))
    if a.check:                                    # a smoke: the first N/2 walked days of each span, nothing else walked
        dk = L["days"].copy()
        dk["date"] = dk["date"].astype(str)
        dk = dk.sort_values("date").reset_index(drop=True)
        wk = dk[dk["day_kind"].astype(str).isin(m0.WALK_DAY_KINDS)]
        half = max(int(a.days or CHECK_DAYS) // 2, 1)
        pick = [d for lo, hi in F.SPANS.values() for d in wk[(wk["date"] >= lo) & (wk["date"] <= hi)]["date"][:half]]
        L = {**L, "days": dk[dk["date"].isin(pick)].reset_index(drop=True)}
        I = {**I, "L": L}
    idents: list[dict] = []

    def ident(name: str, check: str) -> None:
        idents.append({"section": "identity", "identity": name, "holds": True, "check": check})
        print(f"identity ({name}) HOLDS: {check[:120]}", flush=True)

    # ---- the sizing at every stop (the engine's own arithmetic; reported, never re-solved: D-538 (2))
    base_rule = gf.sizing_rule(fcfg, tv)
    leaves = WS.policy_leaves(I["plan"])
    all_stops = (F.REFERENCE_STOP, *F.STOPS)
    sizing = rc.width_sizing(base_rule, leaves, all_stops, tv)
    cannot = sizing[sizing["cannot_size"].astype(bool)]
    print(f"  sizing: {len(sizing)} (stop, leaf, tier) rows at {list(all_stops)} ticks; {len(cannot)} a stop cannot "
          f"size {sorted({(int(s), k) for s, k in zip(cannot['stop_ticks'], cannot['kind'])})}", flush=True)
    capped_rules, fund_rows, round_rows = {}, [], []
    for St in F.STOPS:
        fs = rc.funded_cap_sizing(base_rule, leaves, F.REFERENCE_STOP, St, tv)
        prob = F.funded_cap_problems(fs)
        if prob:
            print(f"REFUSED ({DECISION}): at {St} ticks the funded cap does not hold the 150-tick cell's dollars -- "
                  + "; ".join(prob[:4]))
            return 3
        capped_rules[St] = rc.funded_cap_rule(base_rule, F.REFERENCE_STOP, St)
        fund_rows += fs.to_dict("records")
        round_rows.append({"section": "funded_cap_rounding", "stop_ticks": int(St),
                           "funded_scale": F.REFERENCE_STOP / St, **F.funded_cap_rounding(fs)})
    print(f"  funded cap (D-542's diagnostic at {F.REFERENCE_STOP} / stop): every state the cap binds at "
          f"{F.REFERENCE_STOP} ticks at or below its {F.REFERENCE_STOP}-tick dollars, none unsized", flush=True)
    fees = A.fee_by_stop(fcfg, all_stops, tv)
    slip = float(L["cfg"]["slip_ticks"])
    cost_rows = [{"section": "cost", "stop_ticks": int(St), "stop_points": St / 4.0, "fee_micro_eq": float(fees[St]),
                  "entry_ticks": slip, **{f"cost_r_{k}": v for k, v in F.exit_cost_r(St, fees[St], slip, tv).items()}}
                 for St in all_stops]

    # ---- the reference: P-16's cell and identity (D-594 (4))
    t0 = time.time()
    W0 = WF.walk_stop(I, F.REFERENCE_STOP)
    days = list(W0["days"])
    if tuple(float(x) for x in W0["offered_rr"]) != offered:
        print(f"REFUSED ({DECISION}): the walk's offered R {W0['offered_rr']} are not the table's {offered}.")
        return 3
    c0 = WF.cell(W0, F.REFERENCE_STOP, days)
    t_ref = c0["trades"]
    h_ref = D.trades_hash(t_ref)
    timing["walk_and_cell_150"] = time.time() - t0
    if full:
        bad = []
        if int(len(t_ref)) != int(srow["candidates"]):
            bad.append(f"{len(t_ref)} candidates against the screen's {int(srow['candidates'])}")
        if h_ref != R150.TRADES_SHA256:
            bad.append(f"content hash {h_ref[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
        if bad:
            print(f"REFUSED ({DECISION}): the 150-tick cell is not P-16's {REF} -- " + "; ".join(bad))
            return 3
        ident("a", f"the 150-tick cell (rc_stop_walkforward.cell on every development day): {len(t_ref)} candidates as "
                   f"{F.SCREEN_FILE}'s {REF}; content hash {h_ref} = rc150_dev_test.TRADES_SHA256 (P-16's)")
    else:
        print(f"identity (a): the pinned count and content hash are not comparable on a --check subset ({len(days)} "
              f"days, {len(t_ref)} candidates); the construction identities run on it", flush=True)
    if D.trades_hash(coin_trades(W0, I, F.REFERENCE_STOP, F.COIN_SEED, days)) != h_ref:
        print(f"REFUSED ({DECISION}): the coin swap at seed {F.COIN_SEED} does not rebuild the 150-tick cell.")
        return 3
    if D.trades_hash(RT.coin_cell(W0, I, F.COIN_SEED, days)) != h_ref:
        print(f"REFUSED ({DECISION}): rc150_routing.coin_cell at seed {F.COIN_SEED} does not rebuild the 150-tick cell.")
        return 3
    ident("e", f"the coin swap at the candidate's seed {F.COIN_SEED} (this script's coin_trades and "
               "rc150_routing.coin_cell) rebuilds the 150-tick cell's content hash")
    marks_rows = [{"section": "marks", **r} for r in marks_table(W0, F.REFERENCE_STOP).to_dict("records")]
    res_off0, ok_off0 = A.resolution(t_ref, W0["offered_rr"])
    _, ok_grid0 = A.resolution(t_ref, W0["rr_grid"])
    ref_supply = supply_row(REF, F.REFERENCE_STOP, c0, days, fcfg, h_ref, res_off0, ok_off0, ok_grid0)

    resume = None
    if full and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{g2_paths}")

    # ---- the reference's paired run (guard (b)'s comparison) and identity (b)
    t0 = time.time()

    def make_ref():
        r = RT.run_rule(I, REF, None, t_ref, days, n_paths, a.workers, twin=True)
        df = r.pop("df")
        if full:
            prob = PS.growth_problems(df, srow)
            if prob:
                raise SystemExit(f"REFUSED ({DECISION}): the 150-tick cell's paired run is not {F.SCREEN_FILE}'s {REF} "
                                 "-- " + "; ".join(prob))
        return {**ref_supply, "reference": True, **r}

    ref_g1 = _cached(resume, f"g1 {REF}", make_ref)
    timing["g1_150"] = time.time() - t0
    if full:
        prob = F.row_problems(ref_g1, srow, what=F.SCREEN_FILE)
        if prob:
            print(f"REFUSED ({DECISION}): the 150-tick cell's paired row is not {F.SCREEN_FILE}'s {REF} -- "
                  + "; ".join(prob))
            return 3
        ident("b", f"the 150-tick cell's paired run at seed {S.SEED}, {F.N_PATHS} paths reproduces {F.SCREEN_FILE}'s "
                   f"{REF} (growth at the bound and point, the required bankroll)")
    ref_growth = float(ref_g1["growth_on_required"])
    beside_ref = edge_and_costs(I, REF, t_ref, days)

    # ---- the reference's spans (guard (c)'s comparison) and identity (c)
    t0 = time.time()
    span_ref: dict[str, float] = {}
    g3_rows: list[dict] = []
    for span, (lo, hi) in F.SPANS.items():
        sd = WF.span_days(days, lo, hi)

        def make_span(span=span, sd=sd):
            c = WF.cell(W0, F.REFERENCE_STOP, sd)
            return WF.span_row(S.Runner(I, a.workers), f"{REF}_{span}", span, F.REFERENCE_STOP, c, sd, n_paths,
                               W0["rr_grid"])

        row = {**_cached(resume, f"g3 {span} {REF}", make_span), "section": "g3", "arm": REF}
        if full:
            prob = (F.row_problems(row, wf_row(span), what=F.WALKFORWARD_FILE)
                    + F.row_problems(row, routing_row("g3", span=span), what=F.ROUTING_FILE))
            if prob:
                print(f"REFUSED ({DECISION}): the 150-tick cell on {span} alone is not {F.WALKFORWARD_FILE}'s "
                      f"{REF}_{span} / {F.ROUTING_FILE}'s {F.ROUTING_REF} -- " + "; ".join(prob))
                return 3
        g3_rows.append(row)
        span_ref[span] = float(row["growth_on_required"])
    timing["g3_150"] = time.time() - t0
    if full:
        ident("c", f"the 150-tick cell on each span alone (its own cutoff and bound, {F.N_PATHS} paths) equals "
                   f"{F.WALKFORWARD_FILE}'s {REF}_early / {REF}_late rows and {F.ROUTING_FILE}'s {F.ROUTING_REF} G3 "
                   "rows")

    # ---- the reference's coin sequences (guard (d)'s comparison), run when a cell first reaches guard (d)
    g2_ref: dict[int, dict] = {}
    g2_ident = {"done": False}

    def ref_coin(s: int) -> dict:
        if int(s) not in g2_ref:
            def make(s=s):
                ts = coin_trades(W0, I, F.REFERENCE_STOP, s, days)
                r = RT.run_rule(I, f"g2 {s} {REF}", None, ts, days, g2_paths, a.workers)
                r.pop("df")
                return {"section": "g2", "coin_seed": int(s), "arm": REF, **r}

            row = _cached(resume, f"g2 {s} {REF}", make)
            if full:
                prob = F.row_problems(row, routing_row("g2", coin_seed=int(s)), what=F.ROUTING_FILE)
                if prob:
                    raise SystemExit(f"REFUSED ({DECISION}): the 150-tick cell on coin {s} is not {F.ROUTING_FILE}'s "
                                     f"{F.ROUTING_REF} G2 row -- " + "; ".join(prob))
            g2_ref[int(s)] = row
        return g2_ref[int(s)]

    # ---- the cells
    fsl = PS.fv3c_slices(RESULTS_DIR)
    g1_rows = [ref_g1]
    beside: list[dict] = list(beside_ref)
    g2_rows: list[dict] = []
    g2s_rows: list[dict] = []
    guard_out: list[dict] = []
    verdicts: list[dict] = []
    hashes = {REF: h_ref}
    nan = float("nan")
    for name, St in F.grid():
        t_cell = time.time()
        t0 = time.time()
        W = WF.walk_stop(I, St)
        if list(W["days"]) != days or tuple(float(x) for x in W["offered_rr"]) != offered:
            print(f"REFUSED ({DECISION}): the {St}-tick walk's days or offered R are not the reference's.")
            return 3
        c = WF.cell(W, St, days)
        t = c["trades"]
        tab = marks_table(W, St)
        if rc.window_marks(rc.offered_marks(tab, St), F.WINDOW) != list(c["marks"]):
            print(f"REFUSED ({DECISION}): the {St}-tick cell's marks are not its cutoff's.")
            return 3
        marks_rows += [{"section": "marks", **r} for r in tab.to_dict("records")]
        timing[f"walk_and_cell_{St}"] = time.time() - t0
        h = D.trades_hash(t) if t is not None else ""
        hashes[name] = h
        if t is not None and D.trades_hash(coin_trades(W, I, St, F.COIN_SEED, days)) != h:
            print(f"REFUSED ({DECISION}): the coin swap at seed {F.COIN_SEED} does not rebuild the {St}-tick cell.")
            return 3
        if t is not None:
            ident("e", f"the coin swap at the candidate's seed rebuilds the {St}-tick cell's content hash")
        res_off, ok_off = A.resolution(t, W["offered_rr"]) if t is not None else ({}, False)
        ok_grid = A.resolution(t, W["rr_grid"])[1] if t is not None else False
        supply = supply_row(name, St, c, days, fcfg, h, res_off, ok_off, ok_grid)
        done: list[dict] = [{"guard": "a_resolution", "passes": bool(ok_off), **res_off,
                             "every_grid_r_resolves": bool(ok_grid),
                             "needed": f"every offered R unresolved at most {F.UNRESOLVED_MAX:.0%} overall and in its "
                                       "worst year (D-212)"}]

        def due(g: str) -> bool:
            return t is not None and (a.check or F.next_guard(done) == g)

        g1 = None
        # (b) the paired run, and the beside readings (every cell reaching (b))
        if due("b_paired"):
            t0 = time.time()

            def make_g1(name=name, t=t, supply=supply):
                r = RT.run_rule(I, name, None, t, days, n_paths, a.workers, twin=True)
                r.pop("df")
                return {**supply, "reference": False, **r}

            g1 = _cached(resume, f"g1 {name}", make_g1)
            g1["growth_minus_reference"] = float(g1["growth_on_required"]) - ref_growth
            g1_rows.append(g1)
            timing[f"g1_{St}"] = time.time() - t0
            v = F.verdict(name, float(g1["growth_on_required"]), ref_growth, bool(ok_off), None, {}, {})
            done.append({"guard": "b_paired", "passes": F.guard_check("b_paired", v),
                         "value": float(g1["growth_on_required"]), "reference_value": ref_growth,
                         "difference": float(g1["growth_on_required"]) - ref_growth,
                         "needed": f"difference > {F.MARGIN:g}"})
            t0 = time.time()

            def make_cap(name=name, t=t, St=St):
                R = S.Runner(I, a.workers)
                lab = f"{name}_fcap"
                df = R.run(lab, t, days, n_paths, sizing=capped_rules[St])
                tw = R.run(f"{lab} twin", t, days, n_paths, twin=True, sizing=capped_rules[St])
                return {"section": "capped", "cell": name, "stop_ticks": int(St),
                        "funded_cap": f"funded micro cap x {F.REFERENCE_STOP}/{St} (floor)",
                        **PS.gate_reading(lab, df, tw, R.sink)}

            beside.append(_cached(resume, f"capped {name}", make_cap))
            timing[f"capped_{St}"] = time.time() - t0
            beside += edge_and_costs(I, name, t, days)
            t0 = time.time()

            def make_journey(name=name, t=t):
                try:
                    jl = RT.journey_and_lines(I, t, days, None, name, fsl, a.workers, starts)
                except ValueError as e:                # only a --check smoke shorter than the 126-day slices
                    if full or "summary rows" not in str(e):
                        raise
                    print(f"  {name}: the journey replay ran; the slice lines need 126-day slices ({len(days)} "
                          "days in this smoke)", flush=True)
                    jl = {"journey": [], "lines": [], "lines_hold": False}
                fix = (lambda r: {**{k: x for k, x in r.items() if k != "rule"}, "cell": name})
                return {"journey": [fix(r) for r in jl["journey"]], "lines": [fix(r) for r in jl["lines"]],
                        "lines_hold": bool(jl["lines_hold"])}

            jl = _cached(resume, f"journey {name}", make_journey)
            beside += jl["journey"] + jl["lines"]
            g1["slice_lines_hold"] = bool(jl["lines_hold"])
            timing[f"journey_{St}"] = time.time() - t0
        # (c) the spans alone
        span_g: dict[str, float] = {}
        if due("c_spans"):
            t0 = time.time()
            for span, (lo, hi) in F.SPANS.items():
                sd = WF.span_days(days, lo, hi)

                def make_span(span=span, sd=sd, name=name, St=St, W=W):
                    cs = WF.cell(W, St, sd)
                    return WF.span_row(S.Runner(I, a.workers), f"{name}_{span}", span, St, cs, sd, n_paths,
                                       W["rr_grid"])

                row = {**_cached(resume, f"g3 {span} {name}", make_span), "section": "g3", "arm": name}
                g3_rows.append(row)
                span_g[span] = float(row["growth_on_required"])
            v = F.verdict(name, nan, ref_growth, bool(ok_off), None, span_g, span_ref)
            done.append({"guard": "c_spans", "passes": F.guard_check("c_spans", v),
                         **{f"{k}_difference": float(span_g.get(k, nan)) - float(span_ref.get(k, nan))
                            for k in F.SPANS},
                         "needed": f"not below the {F.REFERENCE_STOP}-tick cell on either span alone"})
            timing[f"g3_{St}"] = time.time() - t0
        # (d) the coin sequences
        g2s = None
        if due("d_coins"):
            t0 = time.time()
            rows_here: list[dict] = []
            for s in F.COIN_SEEDS[:n_coins]:
                rows_here.append(ref_coin(s))

                def make_g2(s=s, name=name, St=St, W=W):
                    ts = coin_trades(W, I, St, s, days)
                    r = RT.run_rule(I, f"g2 {s} {name}", None, ts, days, g2_paths, a.workers)
                    r.pop("df")
                    return {"section": "g2", "coin_seed": int(s), "arm": name, **r}

                rows_here.append(_cached(resume, f"g2 {s} {name}", make_g2))
            if full and not g2_ident["done"]:
                ident("d", f"the 150-tick cell on every coin sequence ({len(F.COIN_SEEDS)} seeds, {F.G2_PATHS} paths) "
                           f"equals {F.ROUTING_FILE}'s {F.ROUTING_REF} G2 row")
                g2_ident["done"] = True
            g2_rows += [r for r in rows_here if r["arm"] == name]
            g2s = F.g2_summary(rows_here, name)
            g2s_rows.append({**g2s, "cell": name})
            v = F.verdict(name, nan, ref_growth, bool(ok_off), g2s, {}, {})
            done.append({"guard": "d_coins", "passes": F.guard_check("d_coins", v), "value": int(g2s["wins"]),
                         "coins": int(g2s["coins"]), "needed": f"wins >= {F.G2_WINS} of {len(F.COIN_SEEDS)}"})
            timing[f"g2_{St}"] = time.time() - t0
        if g1 is None:
            g1_rows.append({**supply, "reference": False, "note": "guard (a) failed: no paired run (D-594 (2))"})
        # the staged verdict
        counted = F.staged(done)
        rows_g, ver = F.guard_rows(name, counted)
        if len(counted) == len(F.GUARDS):
            v = F.verdict(name, float(g1["growth_on_required"]), ref_growth, bool(ok_off), g2s, span_g, span_ref)
            if not F.verdict_agrees(ver, v):
                print(f"REFUSED ({DECISION}): the staged verdict is not the four guards' verdict for {name}.")
                return 3
            ver.update({k: v[k] for k in ("growth_minus_reference", "early_growth_minus_reference",
                                           "late_growth_minus_reference")})
        guard_out += rows_g
        verdicts.append(ver)
        timing[f"cell_{St}"] = time.time() - t_cell
        print(f"  {name}: done ({timing[f'cell_{St}']:.0f} s)", flush=True)
        del W, c, t
    del W0

    seconds = time.time() - t_all
    if a.check:
        print("timings (s): " + ", ".join(f"{k} {v:.0f}" for k, v in timing.items()))
        print(f"--check done: the construction identities on {len(days)} days; the sizing and the funded cap at "
              f"{list(F.STOPS)}; every guard's and every beside's machinery on every cell (G1, capped and spans at "
              f"{n_paths} paths, coins at {g2_paths} paths on {n_coins} sequences, the journey on {starts} starts); "
              f"no reading printed; nothing written. {seconds:.0f} s")
        return 0
    decl_row = {"section": "declaration", "holds": True,
                "check": f"DECISIONS.md's {DECISION} row sha256 {decl['sha256']} (LF line); every phrase and constant "
                         f"agrees; {', '.join(f'{k} sha256 {v}' for k, v in shas.items())}"}
    out = pd.DataFrame([decl_row] + idents + sizing.to_dict("records") + fund_rows + round_rows + cost_rows
                       + marks_rows + g1_rows + beside + g3_rows + g2_rows + g2s_rows + guard_out + verdicts)
    out = with_reading(out)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for name, St in F.grid():
        counter.record(prereg_id=FAMILY_ID, seed=F.CAMPAIGN_SEED, exploratory=True,
                       params={"study": "D-594's finer stop-width screen of P-16's coin", "cell": name,
                               "stop_ticks": int(St), "reference": REF, "coin_seed": F.COIN_SEED,
                               "campaign_seed": F.CAMPAIGN_SEED, "paths": F.N_PATHS, "news_safe": True,
                               "window": F.WINDOW},
                       label=f"D-594's finer stop: {name} ({St / 4:g} points)")
    write_result(out, RESULT, script=SCRIPT, seed=F.CAMPAIGN_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=F.N_VARIANTS,
                 parameters={"decision": DECISION, "family": FAMILY_ID, "declaration_sha256": decl["sha256"],
                             "stops": list(F.STOPS), "reference_stop": F.REFERENCE_STOP, "reference_cell": REF,
                             "campaign_seed": F.CAMPAIGN_SEED, "coin_seed": F.COIN_SEED, "g1_paths": F.N_PATHS,
                             "g2_coin_seeds": [F.COIN_SEEDS[0], F.COIN_SEEDS[-1]], "g2_paths": F.G2_PATHS,
                             "g2_wins_needed": F.G2_WINS, "spans": {k: list(v) for k, v in F.SPANS.items()},
                             "margin": F.MARGIN, "guards": list(F.GUARDS), "offered_rr": list(offered),
                             "cell_trades_sha256": hashes, "reference_files_sha256": shas,
                             "funded_cap": f"resolved_coin.funded_cap_rule at {F.REFERENCE_STOP} / stop (floor)",
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "timing_seconds": {k: round(v, 1) for k, v in timing.items()},
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "none: a cell passing all four guards is a candidate for its "
                                                        "own registered development test (D-594 (2))"},
                 description="EXPLORATORY (D-594): P-16's news-safe all-day coin at 40, 43.75 and 47.5-point stops "
                             "against the 37.5-point cell -- D-594's four guards in order (every offered R resolves, "
                             "paired growth at the bound by more than 0.05, both spans alone, 40 of 50 coin "
                             "sequences), the first failure ending the cell; beside: the funded leg capped to the "
                             "37.5-point dollars, e and its bound, cost by exit kind, the journey and slice lines.")
    pd.set_option("display.width", 250)
    print(pd.DataFrame(guard_out)[["cell", "order", "guard", "status"]].to_string(index=False))
    print(f"candidates: {[v['cell'] for v in verdicts if v['candidate']] or 'none'}; written: {RESULT}.csv "
          f"({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
