"""T7's label identity (Q-195, the audit's C1; feature-rules section 3: a new labeller reproduces the walk before it
labels anything new): on a declared small set of search-year days, at every five-minute mark of `t7_forecast.MARKS`,
T7's entry, its excursions, its open label at fixed point stops and its IV equal this repository's walker
(`extended/walker.py`, held to Stage 2's own walk by `identity/walker_identity.py`) on Stage 2's own day arrays
(`atlas_local.day_arrays`), under the walker's rules where the definitions coincide: a market entry, the walk's last bar
the bar ending 15:08 CT, **no breakeven move** (`RULES`; Stage 2's A3 walks carry the move, so they are not the
comparison).

    python identity/t7_label_identity.py --synthetic      # light: synthetic days (a roll and a DST change), no bar read
    python identity/t7_label_identity.py                  # reads the declared DAYS' bars (six days): under the lock

**What is compared**, each refusing (exit 4 on any difference; counts and the first differing day and mark printed,
never a value):

1. **entry** -- `window_stats`' `entry_slot` + 1 equals the walker's market fill bar (`market_fill_bars` at the mark,
   indexed by END minute) at every mark the walker fills; where the walker has no fill (no bar opening at or after the
   mark before the bar ending 15:08) T7 has no entry either, or its entry is the bar stamped 15:07 (T7 admits an entry
   on the walk's last bar, the walker never opens a position on it -- counted, not a difference);
2. **excursions** -- at a stop and target too wide to reach (`WIDE`), every walk is a flatten, and the walker's MAE of
   the long equals T7's `dn` and of the short T7's `up`, in ticks, exactly;
3. **the label** -- at each stop of `STOPS_TICKS` (10, 25 and 50 points) and each w of `t7_forecast.W_GRID` (the
   walker's target floor(w S) ticks, exact on this grid), the number of the two sides the walker flattens equals
   `t7_forecast.open_counts` on T7's excursions (stop on a touch, target on a trade through by a tick);
4. **IV** -- T7's `iv` equals the sum of squared one-minute changes recomputed from Stage 2's day arrays (the entry
   bar's close less its open, then each present bar's close less the previous present bar's, to the bar ending 15:08),
   relative 1e-12.

**The read** (the default mode): the declared `DAYS` (fixed before any read, all inside the search years; ordinary
weekdays, with both 2020 March extremes, the US daylight changes of 2021 and one day of each other year), one day a
read through `extended.reader` under the purpose `t7_label_identity_search_years` and E-221 (a choice-block read: not
ledgered). Nothing is written.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any, Callable

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import t7_forecast as T7  # noqa: E402
from extended import walker as W  # noqa: E402

PURPOSE = "t7_label_identity_search_years"
READ_ROW = T7.READ_ROW
#: the declared days (fixed before any read)
DAYS = ("2020-02-03", "2020-03-16", "2021-03-15", "2021-11-08", "2022-06-14", "2023-08-21")
STOPS_TICKS = (40, 100, 200)
WIDE = 10 ** 7
RULES = W.Rules("t7_label", W.FLAT_ENTRY, "close", False)
BAR_COLUMNS = ["ts", "day", "contract", "open", "high", "low", "close", "volume"]
IV_TOL = 1e-12
SYNTH_SEED = 4737
SYNTH_SPAN = ("2021-03-08", "2021-03-19")


def _floats(a) -> np.ndarray:
    return np.array([np.nan if x is None else float(x) for x in a], dtype=float)


def vendored_day_arrays() -> Callable[[pd.DataFrame], tuple]:
    from propedge.research.atlas_local import day_arrays

    return day_arrays


def compare_day(bars: pd.DataFrame, day_arrays: Callable[[pd.DataFrame], tuple], mod: Any = T7) -> dict[str, Any]:
    """One trading day's bars: every comparison of the docstring. Returns the counts and the problems."""
    days, O, H, L, C = mod.day_grid(bars)
    if len(days) != 1:
        raise ValueError("compare_day takes one trading day's bars")
    st = mod.window_stats(O, H, L, C)
    o, h, l, c = (_floats(a) for a in day_arrays(bars)[:4])
    marks = np.asarray(mod.MARKS, dtype=int)
    je = W.market_fill_bars(o, marks, rules=RULES)
    es = np.asarray(st["entry_slot"][0], dtype=int)
    out: dict[str, Any] = {"day": days[0].isoformat(), "marks": len(marks), "problems": []}
    filled = je != W.NONE
    bad_entry = filled & (es + 1 != je)
    unfilled_ok = ~filled & ((es == -1) | (es == mod.WALK_LAST_STAMP))
    out["filled"] = int(filled.sum())
    out["t7_only_last_bar"] = int((~filled & (es == mod.WALK_LAST_STAMP)).sum())
    bad_unfilled = ~filled & ~unfilled_ok
    if bad_entry.any() or bad_unfilled.any():
        k = int(np.flatnonzero(bad_entry | bad_unfilled)[0])
        out["problems"].append(f"entry: {int(bad_entry.sum() + bad_unfilled.sum())} marks differ "
                               f"(first mark slot {int(marks[k])})")
    if not filled.any():
        out["problems"].append("no mark filled")
        return out
    k_ix = np.flatnonzero(filled)
    fb, fp = je[k_ix], o[je[k_ix]]
    up, dn, iv = (np.asarray(st[x][0], dtype=float)[k_ix] for x in ("up", "dn", "iv"))
    tick = W.TICK
    wl = W.walk(o, h, l, c, fb, fp, np.ones(len(k_ix)), False, [(WIDE, 1.0, WIDE)], rules=RULES)
    ws = W.walk(o, h, l, c, fb, fp, -np.ones(len(k_ix)), False, [(WIDE, 1.0, WIDE)], rules=RULES)
    if not ((wl["kind"] == W.FLATTEN).all() and (ws["kind"] == W.FLATTEN).all()):
        out["problems"].append("excursions: a wide walk did not flatten")
    for name, mae, mine in (("dn (the long's MAE)", wl["mae"][:, 0], dn),
                            ("up (the short's MAE)", ws["mae"][:, 0], up)):
        diff = ~np.isclose(mae * tick, mine, rtol=0.0, atol=1e-9)
        if diff.any():
            out["problems"].append(f"excursions {name}: {int(diff.sum())} marks differ (first mark slot "
                                   f"{int(marks[k_ix[np.flatnonzero(diff)[0]]])})")
    bl = W.brackets(STOPS_TICKS, mod.W_GRID)
    kl = W.walk(o, h, l, c, fb, fp, np.ones(len(k_ix)), False, bl, rules=RULES)["kind"]
    ks = W.walk(o, h, l, c, fb, fp, -np.ones(len(k_ix)), False, bl, rules=RULES)["kind"]
    n_open = 0
    for j, (S, R, Tt) in enumerate(bl):
        walker_open = (kl[:, j] == W.FLATTEN).astype(int) + (ks[:, j] == W.FLATTEN).astype(int)
        mine = mod.open_counts(up, dn, np.full(len(up), tick), S * tick, Tt / S)
        diff = walker_open != mine
        n_open += int(walker_open.sum())
        if diff.any():
            out["problems"].append(f"label S={S} ticks w={R:g}: {int(diff.sum())} marks differ (first mark slot "
                                   f"{int(marks[k_ix[np.flatnonzero(diff)[0]]])})")
    out["open_sides"] = n_open
    end = W.walk_end(o, RULES)
    pres = ~np.isnan(o)
    want = np.empty(len(k_ix))
    for i, j0 in enumerate(fb):
        js = [j for j in range(int(j0), end + 1) if pres[j]]
        want[i] = (c[js[0]] - o[js[0]]) ** 2 + sum((c[b] - c[a]) ** 2 for a, b in zip(js, js[1:]))
    diff = ~np.isclose(iv, want, rtol=IV_TOL, atol=0.0)
    if diff.any():
        out["problems"].append(f"iv: {int(diff.sum())} marks differ (first mark slot "
                               f"{int(marks[k_ix[np.flatnonzero(diff)[0]]])})")
    out["brackets"] = len(bl)
    return out


def synthetic_days() -> list[pd.DataFrame]:
    from extended import synthetic_bars as SB

    bars = SB.generate(SB.Spec(start=date.fromisoformat(SYNTH_SPAN[0]), end=date.fromisoformat(SYNTH_SPAN[1]),
                               seed=SYNTH_SEED))
    return [g.reset_index(drop=True) for _, g in bars.groupby("day", sort=True)]


def real_days() -> list[pd.DataFrame]:
    from extended import reader

    out = []
    for d in DAYS:
        T7.check_span(d, d)
        out.append(reader.read_bars(d, d, purpose=PURPOSE, declaration=READ_ROW, columns=BAR_COLUMNS,
                                    what=f"T7's label identity: the bars of {d}"))
    return out


def run(day_frames: list[pd.DataFrame], day_arrays: Callable[[pd.DataFrame], tuple], mod: Any = T7) -> list[dict]:
    return [compare_day(b, day_arrays, mod) for b in day_frames]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--synthetic", action="store_true", help="synthetic days only; no bar read")
    a = ap.parse_args(argv)
    t0 = time.time()
    frames = synthetic_days() if a.synthetic else real_days()
    res = run(frames, vendored_day_arrays())
    problems = [f"{r['day']}: {p}" for r in res for p in r["problems"]]
    for r in res:
        print(f"  {r['day']}: {r['marks']} marks, {r.get('filled', 0)} filled, {r.get('brackets', 0)} brackets, "
              f"{r.get('open_sides', 0)} open sides, {r.get('t7_only_last_bar', 0)} T7-only entries on the walk's "
              "last bar -- "
              f"{'HELD' if not r['problems'] else 'FAILED'}", flush=True)
    for p in problems:
        print(f"  {p}")
    print(f"  identity t7_label ({'synthetic' if a.synthetic else 'declared days'}): {len(res)} days -- "
          f"{'HELD' if not problems else 'FAILED'}; {time.time() - t0:.1f} s")
    code = 0 if not problems else 4
    print(f"EXIT {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
