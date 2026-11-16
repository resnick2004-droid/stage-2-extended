"""Q-16: P-16's coin-twin pairs -- both sides of every offered mark of `rc_s150_all_nr` -- for the calibration's
real-dependence null. Reads the development bars (2020-01-02 to 2026-07-16 only) through the vendored engine; writes
nothing under `results/`.

    python scripts/q16_p16_pairs.py --out <dir> [--smoke-days N]

**What it builds.** P-16's own trades (Stage 2 D-544, D-546): `rc150_dev_test.build_cells()`'s cell `rc_s150_all`
exactly -- Stage 2's walk (`atlas_a3.walk_minutes`, FV3-C's rung walk) at the 150-tick stop at every five-minute mark,
the cutoff (`resolved_coin.mark_resolution`, kind columns only), the coin seeded 20261102 per (date, mark), FV3's costs,
D-533's report-day cut -- but walked a chunk of days at a time so the process stays small (the vendored build holds
every day's bars and walks at once). Each day's walk reads that day's bars only, so the chunked walk is the vendored
walk row for row.

**Identities, each refusing (exit 3, nothing written):** (a) the cutoff's table at 150 ticks equals
`vendor/stage2/results/rc_width_screen.csv` section `marks` (walks, every unresolved share, `offered`) -- that file's
sha256 first; (b) the cell's candidates, long share, candidates a day, busiest day and every R's unresolved share
(overall and worst year) equal the file's `rc_s150_all` row; (c) the trades' content hash (`rc_dev_test.trades_hash`,
computed row-wise chunk by chunk) equals `rc150_dev_test.TRADES_SHA256`, pinned by Stage 2 D-543. `--smoke-days` skips
(a)-(c) (a partial day set cannot match) and writes nothing either; it prints timings only.

**What it writes** (`<dir>/p16_pairs.parquet`, one row per offered (date, mark) with both sides walked; the coin's side
and its mirror): `date`, `day_kind`, `slot`, `entry_slot`, `coin` (+1 long, -1 short), and for each R of the grid
`kl_R`/`ks_R` (the long's and the short's exit kind: 0 stop, 1 target, 2 flatten, 3 breakeven), `rl_R`/`rs_R` (net R
after FV3's costs, `resolved_coin.cell_trades`' arithmetic), `xl_R`/`xs_R` (exit bar). Only marks that are P-16
trades are kept (after D-533's cut); the long and short rows are the same two walks the trade and its mirror are.
Plus `<dir>/p16_pairs.json`: the identities' outcome, the sources' sha256 and the parquet's sha256.

These are Stage 2's coin's outcomes on development data, read by Stage 2 already (D-547); this script reads no new
design's outcome. The output is a scratch input to `scripts/q16_calibrate.py`, never a result file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

STOP = 150
CHUNK_DAYS = 40
#: Q-55: Stage 2's engine reads the bars and A1's tables here, so the read is authorised through `extended.reader`
#: first (E-037's purpose for re-reading Stage 2's registered designs -- P-16 here -- under the row naming it, E-035);
#: a refusal ends the run before anything is read (exit 3)
READ_PURPOSE = "registered_design"
READ_ROW = "E-035"
READ_FILES = ("data/atlas/A1/events.parquet", "data/atlas/A1/days.parquet", "data/bars/NQ/bars.parquet")


class CoinArray:
    """`resolved_coin.coin_table`'s coins as an array lookup (the same rng, the same order: dates sorted, slots
    ascending, `u < 0.5` long) -- a Mapping-like `[(date, slot)]` without a 450,000-entry dict."""

    def __init__(self, dates, slots, seed: int):
        self.ds = sorted(str(d) for d in dates)
        self.ss = sorted(int(s) for s in slots)
        self.di = {d: i for i, d in enumerate(self.ds)}
        self.si = {s: j for j, s in enumerate(self.ss)}
        u = np.random.default_rng(int(seed)).random(len(self.ds) * len(self.ss))
        self.side = np.where(u < 0.5, 1, -1).astype(np.int8)

    def __getitem__(self, key):
        d, s = key
        return int(self.side[self.di[str(d)] * len(self.ss) + self.si[int(s)]])


def _rss_mb(peak: bool = False) -> float:
    from extended.procmem import working_set_mb
    return working_set_mb(peak)


def _authorise(a) -> int | None:
    """The reader's verdict on the engine's read (before anything is read): None to go on, else the exit code."""
    from extended import VENDOR_STAGE2, reader

    files = [VENDOR_STAGE2 / f for f in READ_FILES]
    end = reader.JUDGED_END
    if a.smoke_days is not None:                         # a smoke reads the first development days only
        import pandas as _pd
        d = _pd.read_parquet(VENDOR_STAGE2 / "data" / "atlas" / "A1" / "days.parquet",  # one-door-exempt: E-052 -- A1's days.parquet, Stage 2's atlas table: its dates only here
                             columns=["date"])["date"].astype(str).sort_values()
        end = d.iloc[min(int(a.smoke_days), len(d)) - 1]
    print(f"reader: purpose={READ_PURPOSE} declaration={READ_ROW} span {reader.CHOICE_START} to {end} files "
          + ", ".join(f"vendor/stage2/{f}" for f in READ_FILES), flush=True)
    try:
        reader.authorise_engine_read(reader.CHOICE_START, end, purpose=READ_PURPOSE, declaration=READ_ROW, design="P-16",
                                     files=files, what=f"{READ_ROW}: P-16's registered pairs (scripts/q16_p16_pairs.py)")
    except (reader.ReadRefused, FileNotFoundError, ValueError) as exc:
        text = str(exc)
        print(text if text.startswith("REFUSED") else f"REFUSED: {type(exc).__name__}: {text}", flush=True)
        print("REFUSED: the read needs the reader to admit the purpose 'registered_design' under E-035 (E-037; "
              "TASK_QUEUE Q-58); nothing was read", flush=True)
        return 3
    print("reader: AUTHORISED", flush=True)
    return 0 if a.check_read else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--smoke-days", type=int, default=None)
    ap.add_argument("--check-read", action="store_true",
                    help="ask the reader whether the read is authorised, print its verdict, read and write nothing")
    a = ap.parse_args(argv)

    rc = _authorise(a)
    if rc is not None:
        return rc

    import a3_brk30 as B
    import a3_brk30_cb20 as Cb
    import a3_resolution_map as m0
    import atlas_a3 as A
    import rc150_dev_test as P16
    import rc_dev_test as D
    import rc_screen as S
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.outcomes.collect_core import c_slot
    from propedge.research import resolved_coin as rc

    t0 = time.time()
    screen = Path(RESULTS_DIR) / P16.SCREEN_FILE
    screen_sha = hashlib.sha256(screen.read_bytes()).hexdigest()
    if screen_sha != P16.SCREEN_SHA256:
        print(f"REFUSED: {screen} is not the file P-16 pinned ({screen_sha[:12]})")
        return 3
    cfg = A.config(A.FAMILY)
    _, events, days, _ = m0.load_a1()
    del events
    fcfg = A.fv3_config(cfg)
    tv = float(A.TICK_VALUE)
    plan = Cb.noclose_plan(Path(RESULTS_DIR))
    rr_grid = A.rrs(cfg)
    offered_rr = sorted(float(R) for R in zd.policy_rrs(plan))
    keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(plan)))
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    clear = c_slot(*rc.RELEASE_CLEAR_CT)
    grid = rc.marks()
    days = days.copy()
    days["date"] = days["date"].astype(str)
    all_dates = sorted(days["date"])
    coins = CoinArray(all_dates, grid, rc.COIN_SEED)
    fees = A.fee_by_stop(fcfg, (STOP,), tv)
    crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
    kinds = dict(zip(days["date"], days["day_kind"].astype(str)))
    if a.smoke_days is not None:
        days = days.sort_values("date").head(int(a.smoke_days))
    mins = S.walked_minutes(days, grid, cut)
    walk_dates = sorted(mins["date"].unique())
    print(f"inputs read: {len(all_dates)} days, {len(walk_dates)} walked, {len(grid)} marks, R grid {list(rr_grid)}, "
          f"offered R {offered_rr}; {time.time() - t0:.0f} s, rss {_rss_mb():.0f} MB", flush=True)

    # pass 1: walk every chunk; keep the cutoff's kind columns at every mark, and the full walk at the marks the
    # screen offered only (memory); identity (a) then checks the cutoff offers exactly those marks
    s = B._exact(screen)
    mk = s[(s["section"] == "marks") & (pd.to_numeric(s["stop_ticks"], errors="coerce") == STOP)]
    file_offered = sorted(int(x) for x, f in zip(pd.to_numeric(mk["slot"]), mk["offered"]) if str(f) == "True")
    res_cols = ["date", "slot"] + rc.mark_resolution_columns((STOP,), offered_rr)
    res_parts, walk_parts = [], []
    tick = float(cfg["contract"]["tick"])
    for i in range(0, len(walk_dates), CHUNK_DAYS):
        chunk = walk_dates[i:i + CHUNK_DAYS]
        arrays = A.bar_arrays(cfg, chunk)
        w = A.walk_minutes(mins[mins["date"].isin(chunk)], arrays, rc.DELAY, tick, (STOP,), rr_grid)
        del arrays
        res_parts.append(w[res_cols].copy())
        walk_parts.append(w[w["slot"].astype(int).isin(file_offered)].reset_index(drop=True))
        del w
        print(f"  walked {min(i + CHUNK_DAYS, len(walk_dates))}/{len(walk_dates)} days, {time.time() - t0:.0f} s, "
              f"rss {_rss_mb():.0f} MB", flush=True)
    res = pd.concat(res_parts, ignore_index=True)
    del res_parts
    table = rc.mark_resolution(res, (STOP,), offered_rr)
    del res
    offered = rc.offered_marks(table, STOP)
    wm = rc.window_marks(offered, "all")
    problems: list[str] = []
    smoke = a.smoke_days is not None
    if not smoke:                                       # identity (a): the cutoff's table
        if wm != file_offered:
            problems.append("the cutoff's offered marks are not the screen's")
        mk = mk.set_index(pd.to_numeric(mk["slot"]).astype(int))
        tb = table.set_index(table["slot"].astype(int))
        if sorted(mk.index) != sorted(tb.index):
            problems.append("the cutoff's marks are not the screen's")
        else:
            cols = ["walks", "unresolved_worst_r"] + [f"unresolved_{R:g}" for R in offered_rr]
            for slot in tb.index:
                for c in cols:
                    if not B._same(float(tb.loc[slot, c]), float(mk.loc[slot, c])):
                        problems.append(f"mark {slot} {c}: {tb.loc[slot, c]!r} against {mk.loc[slot, c]!r}")
                if bool(tb.loc[slot, "offered"]) != (str(mk.loc[slot, "offered"]) == "True"):
                    problems.append(f"mark {slot} offered differs")
    print(f"cutoff: {len(offered)} marks offered at {STOP} ticks; identity (a) "
          f"{'skipped (smoke)' if smoke else ('HOLDS' if not problems else 'FAILS')}", flush=True)

    # pass 2: the cell's trades chunk by chunk (row hashes kept for the content hash), and the pairs
    hashes, cols_seen, pair_parts = [], None, []
    n_tr, n_long, by_day, fl_n, fl_y = 0, 0, {}, {}, {}
    for w in walk_parts:
        w = w[w["slot"].astype(int).isin(wm)]
        if w.empty:
            continue
        raw = rc.cell_trades(w, kinds, wm, STOP, coins, fees, rr_grid=rr_grid, fresh_rr=crr, tick_value=tv,
                             entry_ticks=float(cfg["slip_ticks"]), cut=cut)
        if raw is None or not len(raw):
            continue
        raw = zd.pad(raw, keys)
        t = rc.drop_release_minute(raw, clear)
        cols = sorted(t.columns)
        if cols_seen is None:
            cols_seen = cols
        elif cols != cols_seen:
            problems.append("a chunk's trades have other columns")
        hashes.append(pd.util.hash_pandas_object(t[cols].reset_index(drop=True), index=False).to_numpy())
        n_tr += len(t)
        n_long += int((t["side"] == "long").sum())
        for d, n in t.groupby("date").size().items():
            by_day[d] = int(n)
        for R in rr_grid:
            o = t[f"o_{R:g}"].astype(str)
            m = o != ""
            f = (o[m] == "f")
            fl_n.setdefault(R, [0, 0])
            fl_n[R][0] += int(f.sum())
            fl_n[R][1] += int(m.sum())
            for y, g in f.groupby(t.loc[m, "year"]):
                fl_y.setdefault((R, int(y)), [0, 0])
                fl_y[(R, int(y))][0] += int(g.sum())
                fl_y[(R, int(y))][1] += int(len(g))
        # the pairs: both sides at the trade's (date, mark), the trade's own walk and its mirror's
        keep = t[["date", "decision_slot_minutes"]].rename(columns={"decision_slot_minutes": "slot"})
        ww = w.assign(date=w["date"].astype(str), slot=w["slot"].astype(int))
        lo = ww[ww["side"].astype(int) > 0].merge(keep, on=["date", "slot"], how="inner")
        sh = ww[ww["side"].astype(int) < 0].merge(keep, on=["date", "slot"], how="inner")
        if len(lo) != len(keep) or len(sh) != len(keep):
            problems.append("a trade without both sides walked")
            continue
        lo = lo.sort_values(["date", "slot"]).reset_index(drop=True)
        sh = sh.sort_values(["date", "slot"]).reset_index(drop=True)
        if not (lo["entry_slot"].to_numpy() == sh["entry_slot"].to_numpy()).all():
            problems.append("a pair's two sides enter at different bars")
        pr = pd.DataFrame({"date": lo["date"], "day_kind": lo["date"].map(kinds), "slot": lo["slot"].astype(np.int16),
                           "entry_slot": lo["entry_slot"].astype(np.int16)})
        pr["coin"] = np.array([coins[(d, s_)] for d, s_ in zip(pr["date"], pr["slot"])], dtype=np.int8)
        from propedge.research.fv3_rung_walk import EXIT_TICKS
        fee = float(fees[STOP])
        for R in rr_grid:
            for tag, side in (("l", lo), ("s", sh)):
                k = side[f"k{STOP}_{float(R):g}"].astype(int).to_numpy()
                g = side[f"g{STOP}_{float(R):g}"].astype(float).to_numpy()
                cost = (float(cfg["slip_ticks"]) * tv + fee + np.array([float(EXIT_TICKS[int(x)]) for x in k]) * tv) \
                    / (STOP * tv)
                pr[f"k{tag}_{R:g}"] = k.astype(np.int8)
                pr[f"r{tag}_{R:g}"] = (g / STOP - cost).astype(np.float32)
                pr[f"x{tag}_{R:g}"] = side[f"x{STOP}_{float(R):g}"].astype(np.int16).to_numpy()
        # check: the coin side's net R is the trade's own r_R (the pairs are the trades)
        tt = t.sort_values(["date", "decision_slot_minutes"]).reset_index(drop=True)
        for R in (1.0, 3.0):
            mine = np.where(pr["coin"].to_numpy() > 0, pr[f"rl_{R:g}"], pr[f"rs_{R:g}"]).astype(float)
            if not np.allclose(mine, tt[f"r_{R:g}"].astype(float).to_numpy(), atol=1e-5):
                problems.append(f"the pairs' coin side is not the trade at R {R:g}")
        pair_parts.append(pr)
    walk_parts.clear()
    pairs = pd.concat(pair_parts, ignore_index=True) if pair_parts else pd.DataFrame()
    h = np.concatenate(hashes) if hashes else np.array([], dtype=np.uint64)
    sha = hashlib.sha256(h.tobytes() + "|".join(cols_seen or []).encode()).hexdigest()
    print(f"trades: {n_tr} ({len(pairs)} pairs), long share {n_long / max(n_tr, 1):.6f}, content hash {sha[:12]}; "
          f"{time.time() - t0:.0f} s, rss {_rss_mb():.0f} MB", flush=True)

    if not smoke:                                       # identities (b) and (c)
        row = s[(s["section"] == "cell") & (s["cell"].astype(str) == P16.CELL)].iloc[0]
        mine = {"candidates": n_tr, "long_share": n_long / n_tr, "candidates_per_day": n_tr / len(all_dates),
                "busiest_day": max(by_day.values())}
        for R in rr_grid:
            f, m = fl_n[R]
            if m:
                mine[f"unresolved_{R:g}"] = f / m
                mine[f"unresolved_worst_year_{R:g}"] = max(v[0] / v[1] for (r_, _), v in fl_y.items() if r_ == R)
        for k_, v in mine.items():
            if k_ in row.index and not B._same(v, row[k_]):
                problems.append(f"{k_}: {v!r} against the screen's {row[k_]!r}")
        if sha != P16.TRADES_SHA256:
            problems.append(f"the trades' content hash {sha[:12]} is not the pinned {P16.TRADES_SHA256[:12]}")
        if D.trades_hash.__doc__ is None:
            problems.append("rc_dev_test.trades_hash is not the vendored one")
    if problems:
        print("REFUSED: " + "; ".join(problems[:10]))
        return 3
    if smoke:
        print(f"smoke: nothing written; peak working set {_rss_mb(peak=True):.0f} MB")
        return 0
    a.out.mkdir(parents=True, exist_ok=True)
    pq = a.out / "p16_pairs.parquet"
    pairs.to_parquet(pq, index=False)
    meta = {"script": "scripts/q16_p16_pairs.py", "cell": P16.CELL, "stop_ticks": STOP, "pairs": int(len(pairs)),
            "identity": "HOLDS: (a) the cutoff's marks, (b) the screen's cell row, (c) TRADES_SHA256",
            "trades_sha256": sha, "screen_sha256": screen_sha, "rr_grid": list(map(float, rr_grid)),
            "offered_marks": len(offered), "first_date": str(pairs["date"].min()), "last_date": str(pairs["date"].max()),
            "parquet_sha256": hashlib.sha256(pq.read_bytes()).hexdigest(), "seconds": round(time.time() - t0, 1),
            "peak_working_set_mb": round(_rss_mb(peak=True), 1)}
    (a.out / "p16_pairs.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print("IDENTITY HOLDS: (a) the cutoff's marks, (b) the screen's cell row, (c) TRADES_SHA256")
    print(f"wrote {pq} ({len(pairs)} pairs); peak working set {_rss_mb(peak=True):.0f} MB; EXIT 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
