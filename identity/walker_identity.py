"""Q-10's identity (F-01 section 7 item 1): this repository's bracket walker (`extended/walker.py`) is Stage 2's walk.

    python identity/walker_identity.py --synthetic        # light, no bars: synthetic days against Stage 2's walk,
                                                          #   its walk frame and its cost columns (seconds)
    python identity/walker_identity.py --smoke-days 10    # P-16's entries on the first 10 development days of real
                                                          #   bars, frame for frame against Stage 2's walk
    python identity/walker_identity.py --substitution     # light, no bars: the full run's substitution touches
                                                          #   P-16's walk only (A3's cache key unchanged)
    python identity/walker_identity.py                    # HEAVY (every development bar; the run lock): P-16's cell
                                                          #   rebuilt with this walker -> its content hash

**The full identity.** P-16's cell (Stage 2 D-544/D-547, `rc_s150_all` with D-533's news-safe cut) is built as P-16's
own builder, `rc150_dev_test.build_cells()`, builds it -- its two lines, `rc_screen.inputs()` (P-14's inputs, A3's
cached walk among them) then `rc_width_screen.build(I, (150,))`: every five-minute mark of every walked day
(`resolved_coin.marks`, `rc_screen.walked_minutes`), the cutoff from the walk's kind columns
(`resolved_coin.mark_resolution`), the coin's side (`coin_table`, seed 20261102), the trades (`resolved_coin.cell_trades`),
padded (`zero_edge_decomposition.pad`) and cut (`drop_release_minute`) -- with ONE substitution, around the second line
only (`build_p16`): `atlas_a3.walk_minutes`, Stage 2's walk of every (date, mark, side), is replaced by `walk_minutes`
below, which places a market order on each side live at the mark and walks it with `extended.walker` under `STAGE2`.
The inputs load under Stage 2's walk, because A3's cache is keyed on that function's source read at call time
(`atlas_a3.walk_inputs`; corrective cycle 1: the lead's first full run refused at A3's cache when the substitution
covered `build_cells()` whole). The runner refuses if the vendored `build_cells` is not those two lines. Every other
line is Stage 2's, vendored and unedited. Market entries fill at a bar's open, so neither fill-bar mode nor the mirror's booking mode
enters (both sides are walked from the same open, as Stage 2 walks them). Then:

1. **the content hash** of the cell's trades (`rc_dev_test.trades_hash`: every column, sorted, row order as built) must
   equal the hash P-16 pinned (`rc150_dev_test.TRADES_SHA256`) exactly -- so this walker's entries, kinds, exits, MAE and
   gross at all twelve R reproduce P-16's, and so does every cutoff decision read from its kind columns. The columns the
   walker does not produce (date, year, decision time, day kind, side label, fee, the log's exit and flatten flag) are
   built from the same inputs by Stage 2's own `cell_trades`, unchanged;
2. **the costs**: this repository's `net_r` and `cost_r` (`Costs` at `atlas_a3.fee_by_stop`'s fee at 150 ticks, MNQ's
   tick value, the config's one entry tick) recompute every trade's `r_<R>` and `c_<R>` column bit for bit from its kind
   and gross, and the fee column is that fee.

On a hash mismatch the cell is rebuilt with Stage 2's own walk and the first differing trade and column are printed
(the failure protocol's first step); nothing is ever loosened. Nothing is written; nothing but counts, timings and
equality is printed. The last line is `EXIT <code>` (0 holds, 3 refused).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
VENDOR = HERE / "vendor" / "stage2"
P16_TRADES_SHA256 = "17bcc29bc0c61296c872eaf04c3d49942649dcddca782836916bebdf29c9635f"   # rc150_dev_test (checked)
SYNTH_SEED = 20261117                     # the synthetic days' seed, used nowhere else
SYNTH_DAYS = 40
SYNTH_STOPS = (50, 100, 150, 200)
SYNTH_FEE = 1.2345                        # an arbitrary fee for the synthetic cost check (the arithmetic is compared)


def _setup() -> None:
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):  # one BLAS thread (Stage 2 D-464 (5))
        os.environ.setdefault(k, "1")
    sys.path.insert(0, str(VENDOR))
    sys.path.insert(0, str(VENDOR / "scripts"))
    sys.path.insert(0, str(HERE))
    sys.dont_write_bytecode = True


def peak_gb() -> float | None:
    """This process's peak working set in GB (Windows), else the max RSS, or None."""
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]
            m = PMC()
            m.cb = ctypes.sizeof(PMC)
            k32 = ctypes.WinDLL("kernel32")
            psapi = ctypes.WinDLL("psapi")
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            if psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(m), m.cb):
                return m.PeakWorkingSetSize / 2**30
            return None
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20
    except Exception:                                                  # noqa: BLE001 -- a reading, never a failure
        return None


# ------------------------------------------------------------------------------------------------ the substitution


def walk_minutes(minutes, arrays, delay: int, tick: float, rungs, rr_grid):
    """`atlas_a3.walk_minutes`' frame from this repository's walker: each (date, mark) a market order on each side, live
    at the mark (`delay` 0, Stage 2's coin, `resolved_coin.DELAY`), filled at the open of the first bar opening at or
    after it before the bar ending 15:08 CT, walked under `STAGE2` at every (stop, R); one row a (date, slot, side) with
    `delay`, `entry_slot` and per (S, R) the kind `k`, exit bar `x`, MAE `a` and gross `g` in ticks -- the same columns,
    types and order as Stage 2's."""
    import numpy as np
    import pandas as pd

    from extended import walker as W

    if int(delay) != 0:
        raise ValueError("the walker's market order is live at the mark: delay 0 only")
    bl = W.brackets(tuple(int(S) for S in rungs), tuple(float(R) for R in rr_grid))
    cols = []
    for S in rungs:
        for R in rr_grid:
            cols += [f"k{S}_{R:g}", f"x{S}_{R:g}", f"a{S}_{R:g}", f"g{S}_{R:g}"]
    parts = []
    for day, g in minutes.groupby("date", sort=True):
        o, h, l, c = (np.asarray(x, dtype=float) for x in arrays(str(day)))
        slots = g["slot"].astype(int).tolist()
        fb = W.market_fill_bars(o, slots, rules=W.STAGE2)
        ent = [(s, side, int(j)) for s, j in zip(slots, fb) if j != W.NONE for side in (1, -1)]
        if not ent:
            continue
        bars = [x[2] for x in ent]
        res = W.walk(o, h, l, c, bars, o[bars], [x[1] for x in ent], False, bl, tick=float(tick), rules=W.STAGE2)
        head = pd.DataFrame(ent, columns=["slot", "side", "entry_slot"]).assign(date=str(day), delay=int(delay))
        body = np.empty((len(ent), 4 * len(bl)), dtype=np.int32)
        body[:, 0::4], body[:, 1::4] = res["kind"], res["exit"]
        body[:, 2::4], body[:, 3::4] = res["mae"], res["gross"]
        parts.append(pd.concat([head, pd.DataFrame(body, columns=cols)], axis=1))
    lead = ["date", "slot", "delay", "side", "entry_slot"]
    if not parts:
        return pd.DataFrame(columns=lead + cols)
    w = pd.concat(parts, ignore_index=True)[lead + cols]
    w = w.astype({"slot": "int16", "delay": "int8", "side": "int8", "entry_slot": "int16",
                  **{c: ("int8" if c.startswith("k") else "int32") for c in cols}})
    return w.sort_values(["date", "slot", "side"], kind="stable").reset_index(drop=True)


def frame_problems(mine, theirs, keys=("date", "slot", "side")) -> list[str]:
    """Exact equality of two walk frames: columns, types, and every value; the first differing row by its keys."""
    import numpy as np

    if list(mine.columns) != list(theirs.columns):
        return [f"columns differ: {list(mine.columns)[:8]}... != {list(theirs.columns)[:8]}..."]
    bad = [f"{c}: {mine[c].dtype} != {theirs[c].dtype}" for c in mine.columns if mine[c].dtype != theirs[c].dtype]
    if bad:
        return ["types differ -- " + "; ".join(bad[:6])]
    if len(mine) != len(theirs):
        return [f"{len(mine)} walks != Stage 2's {len(theirs)}"]
    out = []
    for c in mine.columns:
        a, b = mine[c].to_numpy(), theirs[c].to_numpy()
        diff = np.flatnonzero(a != b)
        if diff.size:
            i = int(diff[0])
            k = ", ".join(f"{x}={theirs[x].iloc[i]}" for x in keys if x in theirs.columns)
            out.append(f"{c}: {diff.size} rows differ, first at ({k}): {a[i]} != Stage 2's {b[i]}")
    return out


def cost_problems(t, stop: int, fee: float, tick_value: float, entry_ticks: float, rr_grid) -> list[str]:
    """This repository's `net_r` / `cost_r` against a trades frame's `r_<R>` / `c_<R>` (bit for bit), from its kinds
    (`o_<R>`) and gross (`g_<R>` x S, exact)."""
    import numpy as np

    from extended import walker as W

    code = {v: k for k, v in W.KIND_CODE.items()}
    costs = W.Costs(fee_micro_eq=float(fee), tick_value=float(tick_value))
    out = []
    if "fee_micro_eq" in t and not (t["fee_micro_eq"].astype(float) == float(fee)).all():
        out.append("fee_micro_eq is not the fee at the stop")
    for R in rr_grid:
        o = t[f"o_{float(R):g}"].astype(str)
        m = (o != "").to_numpy()
        if not m.any():
            continue
        kind = np.array([code[x] for x in o[m]])
        g = t[f"g_{float(R):g}"].to_numpy(float)[m]
        gt = np.round(g * int(stop))
        if not np.array_equal(gt / int(stop), g):
            out.append(f"R {R:g}: the gross does not recover whole ticks")
            continue
        r = W.net_r(gt, kind, int(stop), entry_ticks=entry_ticks, costs=costs)
        c = W.cost_r(kind, int(stop), entry_ticks=entry_ticks, costs=costs)
        for name, mine, col in (("net R", r, f"r_{float(R):g}"), ("cost", c, f"c_{float(R):g}")):
            theirs = t[col].to_numpy(float)[m]
            if not np.array_equal(mine, theirs):
                i = int(np.flatnonzero(mine != theirs)[0])
                out.append(f"R {R:g} {name}: {int((mine != theirs).sum())} differ, first {mine[i]!r} != {theirs[i]!r}")
    return out


# ------------------------------------------------------------------------------------------------ --synthetic


def synthetic_days(seed: int, n_days: int):
    """{date: (o, h, l, c)}: random-walk days on the trading-day clock at 8 to 60 ticks a minute (10 steps a minute),
    with missing bars (3 %), jumps between bars (2 % of bars, sd 40 ticks), on some days a missing block at a session
    open (19:00, 08:30 or 13:00 CT), missing flatten bars, or an early last bar; prices on the tick grid."""
    import numpy as np

    from extended import walker as W

    rng = np.random.default_rng(seed)
    n = W.C_FLAT + 1
    out = {}
    for i in range(n_days):
        sig = float(rng.uniform(8, 60))
        steps = rng.normal(0, sig / np.sqrt(10), size=(n - 1) * 10)
        jumps = np.zeros((n - 1) * 10)
        at = rng.random(n - 1) < 0.02
        jumps[np.flatnonzero(at) * 10] = rng.normal(0, 40, size=int(at.sum()))
        p = (80000 + np.round(np.cumsum(steps + jumps))).reshape(n - 1, 10)
        close = p[:, -1]
        opens = np.concatenate([[80000.0], close[:-1]])
        jump_open = np.flatnonzero(at)
        opens[jump_open] = p[jump_open, 0]                       # a jump between bars: the bar opens away from the close
        hi, lo = np.maximum(p.max(axis=1), opens), np.minimum(p.min(axis=1), opens)
        o, h, l, c = (np.concatenate([[np.nan], x]) * W.TICK for x in (opens, hi, lo, close))
        drop = np.flatnonzero(rng.random(n) < 0.03)
        if rng.random() < 0.4:
            s = int(rng.choice([120, 930, 1200]))
            drop = np.concatenate([drop, np.arange(s + 1, s + 1 + int(rng.integers(1, 7)))])
        if rng.random() < 0.3:
            drop = np.concatenate([drop, rng.choice(np.array(W.FLATTEN_BARS), size=int(rng.integers(1, 4)),
                                                    replace=False)])
        if rng.random() < 0.2:
            drop = np.concatenate([drop, np.arange(int(rng.integers(1200, 1328)), n)])
        drop = drop[(drop >= 1) & (drop < n)]
        for x in (o, h, l, c):
            x[drop] = np.nan
        out[f"2099-01-{i + 1:02d}" if i < 28 else f"2099-02-{i - 27:02d}"] = (o, h, l, c)
    return out


def synthetic() -> list[str]:
    import numpy as np
    import pandas as pd
    import yaml

    import atlas_a3 as A
    import rc_dev_test as D
    from propedge.outcomes import collect_core, fv3_core, orb_core
    from propedge.research import fast_walk
    from propedge.research import fv3_rung_walk as RW
    from propedge.research import resolved_coin as rc

    from extended import walker as W

    bad: list[str] = []
    # the clock and the constants
    for hh in range(24):
        for mm in range(60):
            if (hh, mm) != (17, 0) and W.slot(hh, mm) != collect_core.c_slot(hh, mm):
                bad.append(f"slot({hh}, {mm}) = {W.slot(hh, mm)} != c_slot's {collect_core.c_slot(hh, mm)}")
    stage2_kinds = (W.STOP, W.TARGET, W.FLATTEN, W.BREAKEVEN)          # the walker adds AMBIGUOUS (the pair rule)
    pairs = [("C_FLAT", W.C_FLAT, collect_core.C_FLAT), ("FLAT_ENTRY", W.FLAT_ENTRY, orb_core.FLAT_ENTRY),
             ("FLATTEN_BARS", W.FLATTEN_BARS, tuple(fv3_core.FLATTEN_BARS)),
             ("SESSION_OPENS", W.SESSION_OPENS, tuple(RW.SESSION_OPENS)), ("NONE", W.NONE, orb_core.NONE),
             ("kinds", stage2_kinds, (RW.STOP, RW.TARGET, RW.FLATTEN, RW.BREAKEVEN)),
             ("EXIT_TICKS", {k: W.EXIT_TICKS[k] for k in stage2_kinds}, dict(RW.EXIT_TICKS)),
             ("KIND_CODE", {k: W.KIND_CODE[k] for k in stage2_kinds}, dict(A.KIND_CODE)),
             ("brackets", W.brackets(SYNTH_STOPS, RW.RR_GRID), RW.brackets(SYNTH_STOPS, RW.RR_GRID))]
    cfg = yaml.safe_load((VENDOR / "config" / "atlas_a3.yaml").read_text(encoding="utf-8"))
    pairs += [("SLIP_TICKS", float(W.SLIP_TICKS), float(cfg["slip_ticks"])),
              ("TICK", W.TICK, float(cfg["contract"]["tick"])), ("delay", rc.DELAY, 0)]
    bad += [f"{name}: {a} != Stage 2's {b}" for name, a, b in pairs if a != b]
    days = synthetic_days(SYNTH_SEED, SYNTH_DAYS)
    marks = rc.marks()
    bl = RW.brackets(SYNTH_STOPS, RW.RR_GRID)
    n_walks = 0
    for day, (o, h, l, c) in days.items():
        if W.last_bar(o) != fast_walk.last_bar(o, collect_core.C_FLAT):
            bad.append(f"{day}: last bar differs")
        ent, res = RW.day_walks(o, h, l, c, marks, 0, W.TICK, bl)
        fb = W.market_fill_bars(o, marks, rules=W.STAGE2)
        mine = [(s, side, int(j)) for s, j in zip(marks, fb) if j != W.NONE for side in (1, -1)]
        if [tuple(int(v) for v in x) for x in ent] != mine:
            bad.append(f"{day}: entries differ ({len(mine)} != Stage 2's {len(ent)})")
            continue
        if not mine:
            continue
        bars = [x[2] for x in mine]
        got = W.walk(o, h, l, c, bars, o[bars], [x[1] for x in mine], False, bl, rules=W.STAGE2)
        n_walks += len(mine)
        for k in ("kind", "exit", "mae", "gross"):
            if not np.array_equal(got[k], np.asarray(res[k])):
                i, b = (int(v[0]) for v in np.nonzero(got[k] != np.asarray(res[k])))
                bad.append(f"{day} {k}: walk {mine[i]} bracket {bl[b]}: {got[k][i, b]} != Stage 2's {res[k][i, b]}")
        for side in (1, -1):        # a single order through fill_order is the vectorised fill
            for s in marks[::13]:
                f = W.fill_order(W.Order(W.MARKET, side, s), o, h, l, c, rules=W.STAGE2)
                if (f.bar if f.status == "filled" else W.NONE) != int(fb[marks.index(s)]):
                    bad.append(f"{day}: fill_order and market_fill_bars differ at mark {s}")
    # the frame, and the costs through Stage 2's cell_trades
    mins = pd.DataFrame([(d, s, "n") for d in days for s in marks], columns=["date", "slot", "day_kind"])
    arr = lambda d: days[d]                                                      # noqa: E731
    theirs = A.walk_minutes(mins, arr, 0, W.TICK, SYNTH_STOPS, RW.RR_GRID)
    mine = walk_minutes(mins, arr, 0, W.TICK, SYNTH_STOPS, RW.RR_GRID)
    bad += frame_problems(mine, theirs)
    if not bad and D.trades_hash(mine) != D.trades_hash(theirs):
        bad.append("the frames' content hashes differ")
    coins = rc.coin_table(sorted(days), marks)
    for S in SYNTH_STOPS:
        t = rc.cell_trades(theirs, {d: "n" for d in days}, marks, S, coins, {S: SYNTH_FEE}, rr_grid=RW.RR_GRID,
                           fresh_rr=1.5, tick_value=0.5, entry_ticks=float(cfg["slip_ticks"]), cut=870)
        bad += [f"stop {S}: {x}" for x in cost_problems(t, S, SYNTH_FEE, 0.5, float(cfg["slip_ticks"]), RW.RR_GRID)]
    if not bad:
        print(f"synthetic identity HOLDS: {len(days)} days, {n_walks} walks x {len(bl)} brackets equal Stage 2's "
              f"fv3_rung_walk; the walk frame ({len(mine)} rows) equals atlas_a3.walk_minutes' column for column; "
              f"net R and cost equal resolved_coin.cell_trades' bit for bit at {SYNTH_STOPS}; the clock and constants "
              "are Stage 2's")
    return bad


# ------------------------------------------------------------------------------------------------ --smoke-days


def smoke(n_days: int) -> list[str]:
    import a3_resolution_map as m0
    import atlas_a3 as A
    import rc_screen as S
    from propedge.outcomes.collect_core import c_slot
    from propedge.research import resolved_coin as rc

    cfg = A.config()
    _, _, days, _ = m0.load_a1()
    days = days.copy()
    days["date"] = days["date"].astype(str)
    days = days.sort_values("date").head(int(n_days))
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    mins = S.walked_minutes(days, rc.marks(), cut)
    arrays = A.bar_arrays(cfg, sorted(mins["date"].unique()))
    rr = A.rrs(cfg)
    theirs = A.walk_minutes(mins, arrays, rc.DELAY, float(cfg["contract"]["tick"]), (150,), rr)
    mine = walk_minutes(mins, arrays, rc.DELAY, float(cfg["contract"]["tick"]), (150,), rr)
    bad = frame_problems(mine, theirs)
    if not bad:
        print(f"smoke identity HOLDS: P-16's entries on the first {mins['date'].nunique()} development days "
              f"({len(mine)} walks at 150 ticks x {len(rr)} R) equal atlas_a3.walk_minutes' column for column")
    return bad


# ------------------------------------------------------------------------------------------------ the full identity


@contextmanager
def substituted_walk(walk):
    """`atlas_a3.walk_minutes` replaced by `walk` inside the block, Stage 2's restored on leaving it (also on an error).
    Kept as narrow as one call: A3's cache is keyed on `inspect.getsource(walk_minutes)` read at call time
    (`atlas_a3.walk_inputs`), so a substitution in force while P-14's inputs load makes A3's cached walk look stale
    (the lead's run of 2026-11-16, refused at `atlas_a3.cached_walk`)."""
    import atlas_a3 as A

    stage2 = A.walk_minutes
    A.walk_minutes = walk
    try:
        yield
    finally:
        A.walk_minutes = stage2


BUILD_CELLS_LINES = ("I = S.inputs()", "return I, W.build(I, (STOP,))")


def build_p16(walk=None):
    """P-16's cell as `rc150_dev_test.build_cells()` builds it -- its two lines, `rc_screen.inputs()` then
    `rc_width_screen.build(I, (STOP,))` -- with `walk` (None: Stage 2's) substituted for the second line only, the one
    call that walks P-16's marks; the inputs (P-14's, A3's cached walk among them) load under Stage 2's walk. Refused if
    the vendored `build_cells` is not those two lines."""
    import inspect

    import rc150_dev_test as P
    import rc_screen as S
    import rc_width_screen as Wd

    src = inspect.getsource(P.build_cells)
    if not all(x in src for x in BUILD_CELLS_LINES):
        raise RuntimeError("REFUSED: rc150_dev_test.build_cells is not the two lines this runner reproduces")
    I = S.inputs()
    if walk is None:
        return I, Wd.build(I, (P.STOP,))
    with substituted_walk(walk):
        b = Wd.build(I, (P.STOP,))
    return I, b


def substitution_problems() -> list[str]:
    """`--substitution` (light, no bars): `build_p16`'s substitution leaves A3's cache key Stage 2's while the inputs
    load, is in force while P-16's marks are walked, and is undone after -- with `rc_screen.inputs` and
    `rc_width_screen.build` replaced by probes that record what they see; then, when the atlas is present, A3's own
    manifest key matches under Stage 2's walk and would not under the substitution (the defect this guards)."""
    import json

    import atlas_a3 as A
    import rc_screen as S
    import rc_width_screen as Wd

    cfg = A.config()
    probe_inputs = {"probe": "a1 inputs"}
    stage2 = A.walk_minutes
    key0 = A.walk_inputs(cfg, probe_inputs)
    seen: dict = {}

    def fake_inputs():
        seen["inputs_key"] = A.walk_inputs(cfg, probe_inputs)
        seen["inputs_walk"] = A.walk_minutes
        return {"probe": True}

    def fake_build(I, stops):
        seen["build_walk"], seen["build_stops"] = A.walk_minutes, tuple(stops)
        if seen.get("raise"):
            raise KeyError("probe")
        return {"probe": True}

    bad = []
    real_inputs, real_build = S.inputs, Wd.build
    S.inputs, Wd.build = fake_inputs, fake_build
    try:
        build_p16(walk_minutes)
        if seen.get("inputs_key") != key0 or seen.get("inputs_walk") is not stage2:
            bad.append("the inputs loaded under the substitution: A3's cache key would not be Stage 2's")
        if seen.get("build_walk") is not walk_minutes or seen.get("build_stops") != (150,):
            bad.append("P-16's walk (rc_width_screen.build at 150 ticks) did not run under the substitution")
        if A.walk_minutes is not stage2 or A.walk_inputs(cfg, probe_inputs) != key0:
            bad.append("the substitution was not undone")
        seen["raise"] = True
        try:
            build_p16(walk_minutes)
        except KeyError:
            pass
        if A.walk_minutes is not stage2:
            bad.append("the substitution was not undone after an error")
        with substituted_walk(walk_minutes):
            moved = A.walk_inputs(cfg, probe_inputs) != key0
        if not moved:
            bad.append("the key does not see the substitution: this check could not catch the defect")
    finally:
        S.inputs, Wd.build = real_inputs, real_build
    man = VENDOR / "data" / "atlas" / "A3" / "manifest.json"
    note = "A3's manifest absent: the probe check only"
    if man.is_file():
        inp = json.loads(man.read_text(encoding="utf-8"))["inputs"]
        if A.walk_inputs(cfg, inp["a1_cache"]) != inp:
            bad.append("A3's cache manifest does not match Stage 2's walk key (the cache itself is stale)")
        with substituted_walk(walk_minutes):
            if A.walk_inputs(cfg, inp["a1_cache"]) == inp:
                bad.append("A3's manifest key unexpectedly matches under the substitution")
        note = "A3's own manifest key matches under Stage 2's walk and would not under the substitution"
    if not bad:
        print("substitution check HOLDS: the inputs load under Stage 2's walk (A3's cache key unchanged), P-16's "
              f"150-tick walk runs under this walker, Stage 2's walk is restored after, also on an error; {note}")
    return bad


def full() -> list[str]:
    import atlas_a3 as A
    import rc150_dev_test as P
    import rc_dev_test as D
    import rc_width_screen as Wd

    if P.TRADES_SHA256 != P16_TRADES_SHA256 or int(P.STOP) != 150:
        return [f"the vendored P-16 pins {P.TRADES_SHA256} at {P.STOP} ticks, not {P16_TRADES_SHA256} at 150"]
    t0 = time.time()
    I, b = build_p16(walk_minutes)                 # the one substitution: P-16's walk only
    L = I["L"]
    t = b["cells"][P.CELL]["trades"]
    th = D.trades_hash(t)
    print(f"  P-16's cell rebuilt with this walker: {b['walks']} walks, {len(t)} trades, {len(b['days'])} days "
          f"({time.time() - t0:.0f} s; peak {peak_gb() or float('nan'):.2f} GB so far)", flush=True)
    bad = []
    if th != P.TRADES_SHA256:
        bad.append(f"the trades' content hash {th} is not P-16's pinned {P.TRADES_SHA256}")
    fee = A.fee_by_stop(L["fcfg"], (int(P.STOP),), float(L["tv"]))[int(P.STOP)]
    bad += cost_problems(t, int(P.STOP), fee, float(L["tv"]), float(L["cfg"]["slip_ticks"]), b["rr_grid"])
    if bad and th != P.TRADES_SHA256:
        print("  diagnosing: the cell rebuilt with Stage 2's own walk, compared trade by trade...", flush=True)
        b2 = Wd.build(I, (P.STOP,))                # the same inputs, Stage 2's walk
        t2 = b2["cells"][P.CELL]["trades"]
        if D.trades_hash(t2) != P.TRADES_SHA256:
            bad.append("Stage 2's own build does not reproduce its pin either (the data or the snapshot changed)")
        elif len(t) != len(t2):
            bad.append(f"{len(t)} trades != Stage 2's {len(t2)}")
        else:
            for c in sorted(set(t.columns) | set(t2.columns)):
                if c not in t or c not in t2:
                    bad.append(f"column {c} only in {'mine' if c in t else 'theirs'}")
                    continue
                a, z = t[c].reset_index(drop=True), t2[c].reset_index(drop=True)
                ne = ~((a == z) | (a.isna() & z.isna()))
                if ne.any():
                    i = int(ne.to_numpy().nonzero()[0][0])
                    bad.append(f"{c}: {int(ne.sum())} trades differ, first at row {i} ({t2['date'].iloc[i]} "
                               f"{t2['decision_ct'].iloc[i]} {t2['side'].iloc[i]}): {a.iloc[i]!r} != {z.iloc[i]!r}")
    if not bad:
        print(f"identity HOLDS: P-16's cell rebuilt with this walker in Stage 2's walk's place has P-16's pinned content "
              f"hash ({th[:16]}...; {len(t)} trades, every column); its net R and cost columns at all {len(b['rr_grid'])} "
              f"R equal this repository's costs bit for bit (fee {fee!r} a micro-equivalent at {P.STOP} ticks)")
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--synthetic", action="store_true", help="synthetic days against Stage 2's walk (light, no bars)")
    g.add_argument("--smoke-days", type=int, default=None, help="P-16's entries on the first N development days")
    g.add_argument("--substitution", action="store_true", help="the full run's substitution touches P-16's walk only "
                   "(light, no bars)")
    a = ap.parse_args(argv)
    if not (VENDOR / "propedge").is_dir():
        print(f"REFUSED: {VENDOR} holds no Stage 2 engine")
        print("EXIT 3")
        return 3
    _setup()
    t0 = time.time()
    if a.synthetic:
        bad = synthetic()
    elif a.substitution:
        bad = substitution_problems()
    else:
        if not (VENDOR / "data" / "bars").is_dir():
            print(f"REFUSED: {VENDOR / 'data'} has no bars (scripts/vendor_stage2.py --data)")
            print("EXIT 3")
            return 3
        bad = smoke(a.smoke_days) if a.smoke_days is not None else full()
    pk = peak_gb()
    print(f"{time.time() - t0:.0f} s; peak working set {pk:.2f} GB" if pk is not None else f"{time.time() - t0:.0f} s")
    if bad:
        print("REFUSED (the walker is not Stage 2's walk): " + " | ".join(bad[:12]))
        print("EXIT 3")
        return 3
    print("EXIT 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
