"""EXPLORATORY (D-536): the robustness study of the news-safe coin `rc_s100_all_nr` (D-533 (2), D-535) -- many coins,
worse fills, slower hands, every year. It selects nothing: no coin seed, cost or delay is ever chosen from it; read
beside D-535, never a gate.

    python scripts/rc_robust.py --check --paths 4                 # every section at 4 paths (2 coin seeds, the bisection
                                                                   #   capped); nothing written, no reading printed
    python scripts/rc_robust.py --check --paths 4 --section fills  # one section's smoke
    python scripts/rc_robust.py --workers 3                        # the study, from a clean checkout (D-474)

**The cell** is D-535's exactly: P-15's `rc_s100_all` (the 25-point rung, the all-day window, the coin seeded
20261102, offers every five minutes admitted by D-525 (4)'s cutoff) built here by the same functions in the same order
as `rc_reentry_screen.build` (so its content hash must equal P-15's pinned one -- identity (a)), then
`resolved_coin.drop_release_minute` at 07:35 CT (D-533 (2)). Every run goes through D-535's engine call (`rc_nr_dev.py`'s
`go`): P-14's protocol by `atlas_a3.gate_kwargs` (the no-closure table, 20 purchases in 21 trading days, the strict
rule at five minutes, the day capacity at the trade set's busiest day, the placement off, 0 % denial), P-15's registered
campaign seed (`rc_dev_test.SEED`), each R's 0.05 bound by the era rule (`atlas_a3.bounds`, the bounds `a3_brk30.bounds_at_n`
reads first) recomputed on each run's own trades. Identity (b), full run only: D-535's cell at 500 paths reproduces
`results/rc_nr_dev.csv`'s gate rows (growth at the bound and the point, the required bankroll) to 1e-12.

**Sections** (D-536 (1)-(4)):

* `coins` -- the coin's seed replaced by `COIN_SEEDS` (20261300 + i, i = 0..99; never 20261102), each cell rebuilt from
  the same walk and cutoff (the walk is side-blind: only which side's row is taken changes), the release minute dropped,
  `COIN_PATHS` = 200 paths at P-15's campaign seed; the gate at the bound and the point at 0 %. D-535's own seed is run the same way
  at 200 paths and placed in the distribution (its rank and percentile). A `coins_summary` row: the share of seeds
  growing at the bound and the quantiles. **No seed is ever chosen from this reading.**
* `fills` -- D-535's cell with every trade's cost raised by 1 and by 2 extra ticks a side (`resolved_coin.add_cost_ticks`:
  entry and exit, 2 x ticks / 100 in R at the 25-point rung), 500 paths; then the break-even extra cost by bisection on
  the declared grid 0..6 ticks a side in half-tick steps: the 6-tick end is run first (above zero there: the break-even
  is reported as beyond the grid and nothing more runs), then the half-tick bracket between the highest grid point read
  above zero and the lowest read at or below it is halved until adjacent -- at most 1 + 3 runs beyond the 1 and 2-tick
  runs (the widest bracket, 2..6 ticks, is 8 half-ticks). Growth is assumed to fall as cost rises (each run's reading is
  written, so a reversal shows). The bracket is the reading; no point inside it is interpolated.
* `latency` -- every entry at the `delay`-th bar with an open after the mark (`fast_walk.entry_bar`; delays 1, 3, 5 bars,
  about as many minutes where every minute trades), the walk rerun at that delay, the cutoff's rule unchanged and
  re-read on that walk's kind columns (D-525 (4); its admitted marks reported), the strict rule, the coin and the release
  minute unchanged; 500 paths each.
* `years` -- the gate rows on each calendar year's sessions alone (2020 .. 2026, the last to 2026-07-16), as P-15's
  check years: the year's trades and days (`fv3d_lever_test.in_period`), its own pooled 0.05 bound
  (`a3_brk30.check_bounds`), the cell's day capacity, the campaign's 504-session horizon resampling that year's days;
  500 paths each.

Writes `results/rc_robust.csv` with its manifest (EXPLORATORY; sections `identity`, `coins`, `coins_summary`, `fills`,
`fills_breakeven`, `latency`, `latency_marks`, `years`); one variant record per reading family under `D-536:rc_robust`
(coins, fills, latency, years). Read beside D-535; never a gate; no candidate is chosen from it (D-536 (5)).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/rc_robust.py"
DECISION = "D-536"
RESULT = "rc_robust"
FAMILY_ID = f"{DECISION}:rc_robust"
CELL_STOP = 100                            # the 25-point rung (MNQ ticks)
CELL_WINDOW = "all"
NR_RESULT = "rc_nr_dev.csv"                # D-535's file: identity (b)
COIN_SEEDS = tuple(20261300 + i for i in range(100))     # D-536 (1), fixed before any read
COIN_PATHS = 200
N_PATHS = 500
FILL_TICKS = (1.0, 2.0)                    # D-536 (2)
FILL_GRID = tuple(i * 0.5 for i in range(13))            # 0 .. 6 ticks a side in half ticks
DELAYS = (1, 3, 5)                         # D-536 (3)
YEARS = (2020, 2021, 2022, 2023, 2024, 2025, 2026)
LAST_DAY = "2026-07-16"
SECTIONS = ("coins", "fills", "latency", "years")
TOL = 1e-12
READING = "EXPLORATORY (D-536): beside D-535, never a gate; selects nothing"


# ------------------------------------------------------------------------------------------------ the cell


class Cell:
    """D-535's cell and its parts, built once: P-14's inputs, the walk at a delay, the cutoff, the coin, the trades."""

    def __init__(self) -> None:
        import rc_screen as S

        self.I = S.inputs()
        L = self.I["L"]
        self.cfg, self.fcfg, self.tv = L["cfg"], L["fcfg"], float(L["tv"])
        self.walks: dict[int, dict[str, Any]] = {}

    def walk(self, delay: int) -> dict[str, Any]:
        """The walk at `delay` on both rungs at every mark and the cutoff's reading (kind columns only), as
        `rc_reentry_screen.build` makes them at its delay; cached per delay."""
        if delay in self.walks:
            return self.walks[delay]
        import atlas_a3 as A
        import rc_screen as S
        import zero_edge_decomposition as zd

        from propedge.outcomes.collect_core import c_slot
        from propedge.research import resolved_coin as rc

        rr_grid = A.rrs(self.cfg)
        offered_rr = sorted(float(R) for R in zd.policy_rrs(self.I["plan"]))
        cut = c_slot(*(int(x) for x in str(self.cfg["news"]["bls_cut_ct"]).split(":")))
        grid = rc.marks()
        days = self.I["L"]["days"].copy()
        days["date"] = days["date"].astype(str)
        mins = S.walked_minutes(days, grid, cut)
        t0 = time.time()
        arrays = A.bar_arrays(self.cfg, sorted(mins["date"].unique()))
        walks = A.walk_minutes(mins, arrays, int(delay), float(self.cfg["contract"]["tick"]), rc.RUNGS, rr_grid)
        res_cols = ["date", "slot"] + rc.mark_resolution_columns(rc.RUNGS, offered_rr)
        table = rc.mark_resolution(walks[res_cols], rc.RUNGS, offered_rr)          # kind columns only
        offered = rc.offered_marks(table, CELL_STOP)
        wm = rc.window_marks(offered, CELL_WINDOW)
        print(f"  the walk at delay {delay}: {len(walks)} walks, {len(wm)} marks admitted at the 25-point rung, "
              f"{time.time() - t0:.0f} s", flush=True)
        self.walks[delay] = {"walks": walks, "table": table, "marks": wm, "grid": grid, "cut": cut, "days": days,
                             "rr_grid": rr_grid, "offered_rr": offered_rr}
        return self.walks[delay]

    def trades(self, *, delay: int = 0, coin_seed: int | None = None, release: bool = True) -> pd.DataFrame:
        """The cell's trades at a delay and a coin seed (`rc_reentry_screen.build`'s calls, the same order), padded as
        it pads them; with `release`, D-533 (2)'s release minute dropped."""
        import atlas_a3 as A
        import zero_edge_decomposition as zd

        from propedge.outcomes.collect_core import c_slot
        from propedge.research import resolved_coin as rc

        w = self.walk(delay)
        days = w["days"]
        coins = rc.coin_table(days["date"].tolist(), w["grid"], seed=rc.COIN_SEED if coin_seed is None else int(coin_seed))
        fees = A.fee_by_stop(self.fcfg, rc.RUNGS, self.tv)
        crr = float(self.fcfg["state_policy"]["fresh"]["combine_rr"])
        kinds = dict(zip(days["date"], days["day_kind"].astype(str)))
        keys = sorted(set(float(R) for R in w["rr_grid"]) | set(zd.policy_rrs(self.I["plan"])))
        t = rc.cell_trades(w["walks"], kinds, w["marks"], CELL_STOP, coins, fees, rr_grid=w["rr_grid"], fresh_rr=crr,
                           tick_value=self.tv, entry_ticks=float(self.cfg["slip_ticks"]), cut=w["cut"])
        t = zd.pad(t, keys)
        if release:
            t = rc.drop_release_minute(t, c_slot(*rc.RELEASE_CLEAR_CT))
        return t

    @property
    def days(self) -> list[str]:
        return sorted(self.I["L"]["days"]["date"].astype(str))


# ------------------------------------------------------------------------------------------------ the engine call


class Engine:
    """D-535's engine call (`rc_nr_dev.py`'s `go("gate", ...)`) on any trade set, every path in one sink."""

    def __init__(self, cell: Cell, workers: int):
        import fv3d_lever_test as lt
        import portfolio_stage as ps

        self.c, self.workers = cell, int(workers)
        pcfg = cell.fcfg["portfolio"]
        self.sink: list[dict] = []
        self.inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])},
                                      sink=self.sink)
        self.hook = lt.lever_hook(self.inner)

    def gate(self, label: str, t: pd.DataFrame, days: list[str], n_paths: int, *, bounds=None, capacity=None
             ) -> pd.DataFrame:
        """The gate rows (point and bound, 0 %) of `t` on `days`: each R's 0.05 bound by the era rule on `t` itself
        (`atlas_a3.bounds`) unless `bounds` = (e_by, lb_by) is given; the capacity the trade set's own unless given."""
        import a3_brk30 as B
        import a3_brk30_cb20 as C
        import atlas_a3 as A
        import portfolio_stage as ps
        import rc_dev_test as D
        import score_fv3_grid as gf

        from propedge.campaign import gate

        c = self.c
        keys = B.rrs(t)
        if bounds is None:
            _, e_by, lb_by, _, _ = A.bounds(t, days, keys, c.cfg)
        else:
            e_by, lb_by = bounds
        blocks, n_used = gf.gate_blocks(t, days, c.tv, keys, require_sides=True, require_exits=True)
        if n_used != len(t):
            raise SystemExit("REFUSED: the blocks hold a different number of trades.")
        cap = B.capacity(t, c.fcfg) if capacity is None else int(capacity)
        ps._label(self.inner, label)
        kw = A.gate_kwargs(blocks, c.fcfg, c.tv, c.I["plan"], e_by, lb_by, self.hook, seed=int(D.SEED),
                           n_paths=int(n_paths), horizon=int(c.fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap,
                           levels=(0.0,), rtp=False, one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
        df, _ = gate.run_gate(kw.pop("blocks"), workers=self.workers, **kw)
        df["placement"] = "off"
        df.insert(0, "run", label)
        return df

    def taken(self, label: str, shift: str) -> float:
        """Trades taken a session (mean over the run's paths at 0 %)."""
        import rc_reentry_screen as RS

        return RS.taken_per_session(self.sink, label, shift)


def at(df: pd.DataFrame, shift: str, col: str = "pf_growth_on_base_p50") -> float:
    r = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)]
    return float(r.iloc[0][col]) if len(r) else float("nan")


def gate_row(section: str, df: pd.DataFrame, eng: Engine, label: str, **extra) -> dict[str, Any]:
    """One reading row: growth at the bound and the point, the required bankroll, trades taken a session."""
    return {"section": section, **extra, "growth_bound": at(df, "lower_bound"), "growth_point": at(df, "point"),
            "required_p90_bound": at(df, "lower_bound", "pf_required_p90"),
            "required_p90_point": at(df, "point", "pf_required_p90"),
            "grows_at_bound": bool(at(df, "lower_bound") > 0),
            "taken_per_session_bound": eng.taken(label, "lower_bound"),
            "paths": int(df["paths"].iloc[0]) if "paths" in df.columns else None}


# ------------------------------------------------------------------------------------------------ the identities


def identity_hash(cell: Cell) -> tuple[list[str], pd.DataFrame]:
    """(a): the cell before the release minute is P-15's `rc_s100_all` (the pinned content hash)."""
    import rc_dev_test as D

    t15 = cell.trades(release=False)
    h = D.trades_hash(t15)
    return ([] if h == D.TRADES_SHA256 else [f"the cell's content hash {h[:12]} is not P-15's {D.TRADES_SHA256[:12]}"]), t15


def identity_nr(rd: Path, df: pd.DataFrame) -> list[str]:
    """(b): D-535's cell at 500 paths against `results/rc_nr_dev.csv`'s gate rows (manifest verified)."""
    import a3_brk30 as B

    ref = B._exact(Path(rd) / NR_RESULT)
    ref = ref[(ref["section"].astype(str) == "gate") & np.isclose(ref["enforcement_p"].astype(float), 0.0)]
    out = []
    for shift in ("point", "lower_bound"):
        r = ref[ref["shift"].astype(str) == shift]
        if len(r) != 1:
            out.append(f"{NR_RESULT}: {len(r)} gate rows at {shift}")
            continue
        for col in ("pf_growth_on_base_p50", "pf_required_p90"):
            mine, want = at(df, shift, col), float(r.iloc[0][col])
            if not np.isclose(mine, want, rtol=TOL, atol=TOL):
                out.append(f"{shift} {col}: {mine!r} against {NR_RESULT}'s {want!r}")
    return out


# ------------------------------------------------------------------------------------------------ the sections


class Resume:
    """D-540: each finished run's row kept outside the checkout (an untracked file inside it would stamp the result
    -dirty), keyed by the code's commit and the path counts, so a run killed by the machine (memory) resumes instead of
    restarting. Every run is deterministic at its seeds, so a cached row is the row the run would write again; the file
    is never read under a different commit or path count. Off with `--no-resume` and always off in --check."""

    def __init__(self, folder: Path | None, key: str):
        self.path = None if folder is None else Path(folder) / f"{RESULT}_{key}.jsonl"
        self.rows: dict[str, dict] = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["row"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)

    def get(self, label: str) -> dict | None:
        return self.rows.get(label)

    def put(self, label: str, row: dict) -> None:
        self.rows[label] = row
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"_label": label, "row": row}, default=_jsonable) + "\n")


def _jsonable(x: Any) -> Any:
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return str(x)


def _cached(resume: "Resume | None", label: str, make) -> dict:
    """The run's row from the resume file, or made now and kept (as it reads back from JSON, so a resumed and a fresh
    run write the same values)."""
    row = resume.get(label) if resume is not None else None
    if row is None:
        row = json.loads(json.dumps(make(), default=_jsonable))
        if resume is not None:
            resume.put(label, row)
    return row


def run_coins(cell: Cell, eng: Engine, days: list[str], n_paths: int, seeds, resume: "Resume | None" = None
              ) -> list[dict]:
    from propedge.research import resolved_coin as rc

    rows = []
    for s in [rc.COIN_SEED, *seeds]:
        label = f"coin {int(s)}"

        def make(s=s, label=label):
            t = cell.trades(coin_seed=int(s))
            df = eng.gate(label, t, days, n_paths)
            return gate_row("coins", df, eng, label, coin_seed=int(s), own_seed=bool(int(s) == rc.COIN_SEED),
                            candidates=int(len(t)), long_share=float((t["side"] == "long").mean()))

        rows.append(_cached(resume, label, make))
        print(f"  {label}: done ({len(rows)}/{1 + len(seeds)})", flush=True)
    return rows


def coins_summary(rows: list[dict]) -> dict[str, Any]:
    others = [r for r in rows if not r["own_seed"]]
    own = next(r for r in rows if r["own_seed"])
    g = np.array([r["growth_bound"] for r in others], float)
    q = {f"growth_bound_p{p}": float(np.percentile(g, p)) for p in (5, 10, 25, 50, 75, 90, 95)} if len(g) else {}
    return {"section": "coins_summary", "seeds": int(len(g)), "share_growing_at_bound": float(np.mean(g > 0)) if len(g)
            else float("nan"), "growth_bound_min": float(g.min()) if len(g) else float("nan"),
            "growth_bound_max": float(g.max()) if len(g) else float("nan"), **q,
            "own_seed_growth_bound": own["growth_bound"],
            "own_seed_share_of_seeds_below": float(np.mean(g < own["growth_bound"])) if len(g) else float("nan"),
            "own_seed_rank": int(np.sum(g < own["growth_bound"])) + 1 if len(g) else None,
            "reading": "the distribution over coin seeds; no seed is chosen from it (D-536 (1))"}


def bisect_plan(read: dict[float, float], grid=FILL_GRID) -> float | None:
    """The next grid point to run, or None when the bracket is adjacent (or the end is above zero): `read` maps an
    extra cost in ticks a side to the growth at the bound read there."""
    grid = tuple(float(x) for x in grid)
    pos = [x for x in grid if x in read and read[x] > 0]
    neg = [x for x in grid if x in read and read[x] <= 0]
    if not neg:                                    # nothing at or below zero yet: the grid's end first, once
        return None if grid[-1] in read else grid[-1]
    lo = max(pos) if pos else None
    above = [x for x in neg if lo is None or x > lo]
    if not above:                                  # a reversal: every non-positive point lies below a positive one
        return None
    hi_i = grid.index(min(above))
    lo_i = -1 if lo is None else grid.index(lo)
    if hi_i - lo_i <= 1:
        return None
    return grid[(lo_i + hi_i) // 2] if lo_i >= 0 else grid[hi_i // 2]


def breakeven(read: dict[float, float], grid=FILL_GRID) -> dict[str, Any]:
    if read.get(grid[-1], -1.0) > 0:
        return {"section": "fills_breakeven", "breakeven_beyond_grid": True, "last_positive_ticks": float(grid[-1]),
                "first_nonpositive_ticks": float("nan"), "runs": len(read)}
    pos = [x for x in read if read[x] > 0]
    neg = [x for x in read if read[x] <= 0]
    lo = max(pos) if pos else float("nan")
    hi = min(x for x in neg if not pos or x > lo) if neg else float("nan")
    monotone = all(read[a] >= read[b] - 1e-12 for a in sorted(read) for b in sorted(read) if a < b)
    return {"section": "fills_breakeven", "breakeven_beyond_grid": False, "last_positive_ticks": lo,
            "first_nonpositive_ticks": hi, "runs": len(read), "monotone_as_read": bool(monotone),
            "reading": "the bracket in ticks a side (entry and exit) between the last grid point growing at the bound "
                       "and the first that does not; nothing interpolated (D-536 (2))"}


def run_fills(cell: Cell, eng: Engine, t: pd.DataFrame, days: list[str], n_paths: int, base_bound: float,
              max_runs: int | None = None, resume: "Resume | None" = None) -> tuple[list[dict], dict]:
    from propedge.research import resolved_coin as rc

    rows, read = [], {0.0: float(base_bound)}

    def one(x: float) -> None:
        label = f"fills +{x:g}"

        def make():
            df = eng.gate(label, rc.add_cost_ticks(t, x), days, n_paths)
            return gate_row("fills", df, eng, label, extra_ticks_a_side=float(x),
                            extra_cost_r=float(2.0 * x / CELL_STOP), part="declared" if x in FILL_TICKS else "bisection")

        r = _cached(resume, label, make)
        rows.append(r)
        read[float(x)] = r["growth_bound"]
        print(f"  {label}: done", flush=True)

    for x in FILL_TICKS:
        one(float(x))
    runs = 0
    while (nxt := bisect_plan(read)) is not None:
        if max_runs is not None and runs >= max_runs:
            break
        one(nxt)
        runs += 1
    return rows, breakeven(read)


def run_latency(cell: Cell, eng: Engine, days: list[str], n_paths: int, delays=DELAYS, resume: "Resume | None" = None
                ) -> tuple[list[dict], list[dict]]:
    from propedge.research import resolved_coin as rc

    rows, marks_rows = [], []
    base = cell.walk(0)["marks"]
    for d in delays:
        t = cell.trades(delay=int(d))
        wm = cell.walk(int(d))["marks"]
        label = f"latency {int(d)}"

        def make(t=t, wm=wm, d=d, label=label):
            df = eng.gate(label, t, days, n_paths)
            return gate_row("latency", df, eng, label, delay_bars=int(d), candidates=int(len(t)),
                            marks_admitted=int(len(wm)))

        rows.append(_cached(resume, label, make))
        marks_rows.append({"section": "latency_marks", "delay_bars": int(d), "marks_admitted": int(len(wm)),
                           "marks_dropped_vs_delay0": " ".join(rc.ct(m) for m in sorted(set(base) - set(wm))),
                           "marks_added_vs_delay0": " ".join(rc.ct(m) for m in sorted(set(wm) - set(base)))})
        cell.walks.pop(int(d), None)                    # free the walk (each about the delay-0 walk's size)
        print(f"  {label}: done", flush=True)
    return rows, marks_rows


def run_years(cell: Cell, eng: Engine, t: pd.DataFrame, days: list[str], n_paths: int, years=YEARS,
              resume: "Resume | None" = None) -> list[dict]:
    import a3_brk30 as B
    import fv3d_lever_test as lt

    rows = []
    cap = B.capacity(t, cell.fcfg)
    keys = B.rrs(t)
    for y in years:
        hi = LAST_DAY if int(y) == 2026 else f"{int(y)}-12-31"
        ty, dy = lt.in_period(t, days, f"{int(y)}-01-01", hi)
        if not len(ty):
            continue
        ey, lby = B.check_bounds(ty, dy, keys)
        label = f"year {int(y)}"

        def make(ty=ty, dy=dy, ey=ey, lby=lby, y=y, label=label):
            df = eng.gate(label, ty, dy, n_paths, bounds=(ey, lby), capacity=cap)
            return gate_row("years", df, eng, label, year=int(y), sessions=int(len(dy)), candidates=int(len(ty)),
                            e_at_fresh_combine_r=float(ey.get(1.5, float("nan"))),
                            lb_at_fresh_combine_r=float(lby.get(1.5, float("nan"))))

        rows.append(_cached(resume, label, make))
        print(f"  {label}: done", flush=True)
    return rows


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every section at --paths; nothing written, no reading printed")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=None, help="test seam (with --check): paths a run")
    ap.add_argument("--section", choices=SECTIONS, default=None, help="test seam (with --check): one section")
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and (a.paths is not None or a.section is not None):
        print(f"REFUSED ({DECISION}): a reading runs every section at the declared paths; use --check for a smoke.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    n_paths = N_PATHS if a.paths is None else int(a.paths)
    coin_paths = COIN_PATHS if a.paths is None else int(a.paths)
    seeds = COIN_SEEDS if not a.check else COIN_SEEDS[:2]
    todo = SECTIONS if a.section is None else (a.section,)
    t_all = time.time()
    print("D-535's cell (P-14's inputs, the walk at delay 0, the cutoff, the coin)...", flush=True)
    cell = Cell()
    bad, t15 = identity_hash(cell)
    if bad:
        print(f"REFUSED ({DECISION}): " + "; ".join(bad))
        return 3
    import rc_dev_test as D

    print(f"identity HOLDS: the cell before the release minute = P-15's rc_s100_all (content hash "
          f"{D.TRADES_SHA256[:16]})", flush=True)
    t = cell.trades()
    days = cell.days
    eng = Engine(cell, a.workers)
    base = eng.gate("d535", t, days, n_paths)
    idents = [{"section": "identity", "check": "the cell before the release minute equals P-15's rc_s100_all "
               "(rc_dev_test.TRADES_SHA256)", "holds": True}]
    if n_paths == N_PATHS:
        bad = identity_nr(rd, base)
        if bad:
            print(f"REFUSED ({DECISION}): D-535's cell is not {NR_RESULT}'s -- " + "; ".join(bad))
            return 3
        print(f"identity HOLDS: D-535's cell at {N_PATHS} paths = {NR_RESULT}'s gate rows", flush=True)
        idents.append({"section": "identity", "check": f"D-535's cell at {N_PATHS} paths and seed {D.SEED} reproduces "
                       f"results/{NR_RESULT}'s gate rows (growth at the bound and point, required bankroll)",
                       "holds": True})
    else:
        print(f"identity (b) needs {N_PATHS} paths; not compared at {n_paths}", flush=True)
    rows: list[dict] = []
    timing: dict[str, float] = {}
    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{coin_paths}")
    if "coins" in todo:
        t0 = time.time()
        c_rows = run_coins(cell, eng, days, coin_paths, seeds, resume)
        rows += c_rows + [coins_summary(c_rows)]
        timing["coins"] = time.time() - t0
    if "fills" in todo:
        t0 = time.time()
        f_rows, be = run_fills(cell, eng, t, days, n_paths, at(base, "lower_bound"),
                               max_runs=1 if a.check else None, resume=resume)
        rows += f_rows + [be]
        timing["fills"] = time.time() - t0
    if "latency" in todo:
        t0 = time.time()
        l_rows, m_rows = run_latency(cell, eng, days, n_paths, DELAYS[:1] if a.check else DELAYS, resume)
        rows += l_rows + m_rows
        timing["latency"] = time.time() - t0
    if "years" in todo:
        t0 = time.time()
        rows += run_years(cell, eng, t, days, n_paths, YEARS[-1:] if a.check else YEARS, resume)
        timing["years"] = time.time() - t0
    secs = time.time() - t_all
    if a.check:
        print(f"every identity holds; sections {list(todo)} ran at {n_paths} paths (coins at {coin_paths}, "
              f"{len(seeds)} seeds); nothing written, no reading printed (--check). {secs:.0f} s; by section "
              + ", ".join(f"{k} {v:.0f} s" for k, v in timing.items()))
        return 0
    base_row = gate_row("base", base, eng, "d535")
    res = pd.DataFrame(idents + [base_row] + rows)
    res["reading"] = res["reading"].fillna(READING) if "reading" in res else READING
    counter = VariantCounter(path=rd / "variants.jsonl")
    for fam in SECTIONS:
        counter.record(prereg_id=FAMILY_ID, seed=int(D.SEED), exploratory=True,
                       params={"study": "D-536's robustness of rc_s100_all_nr", "family": fam,
                               "coin_seeds": [COIN_SEEDS[0], COIN_SEEDS[-1]] if fam == "coins" else None,
                               "paths": COIN_PATHS if fam == "coins" else N_PATHS},
                       label=f"{DECISION}'s robustness reading: {fam} (rc_s100_all_nr; selects nothing)")
    params = {"decision": DECISION, "cell": "rc_s100_all_nr (D-535)", "campaign_seed": int(D.SEED),
              "coin_seed_candidate": 20261102, "coin_seeds": [COIN_SEEDS[0], COIN_SEEDS[-1]], "coin_paths": COIN_PATHS,
              "n_paths": N_PATHS, "fill_ticks": list(FILL_TICKS), "fill_grid": list(FILL_GRID),
              "fill_rule": "extra ticks at entry and at exit, 2 x ticks / 100 in R at the 25-point rung "
                           "(resolved_coin.add_cost_ticks)", "delays_bars": list(DELAYS), "years": list(YEARS),
              "last_day": LAST_DAY, "bounds": "each run's own 0.05 bound by the era rule (atlas_a3.bounds); a year "
              "its own pooled bound (a3_brk30.check_bounds)", "timing_seconds": {k: round(v, 1) for k, v in timing.items()},
              "workers": int(a.workers), "seconds": round(secs, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=int(D.SEED), exploratory=True, results_dir=results_dir,
                 variant_count=len(SECTIONS), parameters=params,
                 notes={"status": READING, "selection": "none -- no coin seed, cost or delay is chosen from this file"},
                 description="EXPLORATORY (D-536): the news-safe coin rc_s100_all_nr under 100 other coin seeds (200 "
                             "paths each), worse fills (1 and 2 extra ticks a side and the break-even bracket), slower "
                             "entries (1, 3, 5 bars) and each calendar year alone; beside D-535, never a gate.")
    print(f"written: {RESULT}.csv ({secs:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
