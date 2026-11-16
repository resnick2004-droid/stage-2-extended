"""The capture walk in numpy (R5, D-460): `collect_core.c_walks` + `t23_core.t_records`' outcome, record for record.

The local screen walks hundreds of event minutes a day across years; the embedded pure-Python walk does that too slowly.
This is the same walk, rule for rule -- the same tolerances, the same first-passage order, the gap of an adverse open,
the scratch at the box's end from the last close at or before it, a tied minute the stop's and marked 'u' (no second
bars locally) -- written over arrays. `tests/test_fast_walk.py` holds it to `collect_core`/`t23_core` on random days.

Arrays: o, h, l, c as float arrays on the trading-day clock (NaN where no bar; index 0 unused).
"""
from __future__ import annotations

import numpy as np

EPS = 1e-9


def last_bar(o: np.ndarray, flat: int) -> int | None:
    """`collect_core.c_last`: the day's last bar at or before `flat`."""
    upto = min(flat, len(o) - 1)
    idx = np.flatnonzero(~np.isnan(o[: upto + 1]))
    return int(idx[-1]) if idx.size else None


def entry_bar(o: np.ndarray, t: int, delay: int, last: int) -> int | None:
    """`collect_core.c_entry`: the `delay`-th bar with an open after slot t, at or before `last`."""
    idx = np.flatnonzero(~np.isnan(o[t + 1: last + 1]))
    return int(idx[delay]) + t + 1 if idx.size > delay else None


def walk(o, h, l, c, j0: int, end: int, d: int, slip: float, levels: np.ndarray):
    """One walk's (entry, fav, adv, gap, mark): the first passage beyond each level in favour (traded through) and
    against (touched, or opened beyond: the gap), and the scratch P&L at `end` (price), as `c_passages` and `c_walks`."""
    entry = o[j0] + d * slip
    hh, ll, oo = h[j0:end + 1], l[j0:end + 1], o[j0:end + 1]
    ok = ~np.isnan(oo)
    f = np.where(ok, (hh - entry) if d > 0 else (entry - ll), -np.inf)
    a = np.where(ok, (entry - ll) if d > 0 else (hh - entry), -np.inf)
    ao = np.where(ok, (entry - oo) if d > 0 else (oo - entry), -np.inf)
    n = len(levels)
    fav = [None] * n
    adv = [None] * n
    gap = [0.0] * n
    for i, L in enumerate(levels):
        hit = np.flatnonzero(f > L + EPS)
        if hit.size:
            fav[i] = int(hit[0]) + j0
        hit = np.flatnonzero(a >= L - EPS)
        if hit.size:
            k = int(hit[0])
            adv[i] = k + j0
            if k != 0 and ao[k] > L + EPS:
                gap[i] = float(ao[k] - L)
    j = end
    while j > j0 and np.isnan(c[j]):
        j -= 1
    mark = d * ((c[j] - d * slip) - entry)
    return entry, fav, adv, gap, mark


def outcomes(j0: int, end: int, fav, adv, gap, mark: float, brackets, tick: float):
    """Each bracket's (kind, minutes, tie mark, gap ticks, end ticks) as `t23_core.t_records` writes them, a tied minute
    settled as the stop's and marked (no second bars)."""
    out = []
    for iT, iS in brackets:
        jt, js = fav[iT], adv[iS]
        t_in = jt is not None and jt <= end
        s_in = js is not None and js <= end
        if t_in and (not s_in or jt < js):
            out.append(("t", jt - j0, False, 0, 0))
        elif s_in and (not t_in or js < jt):
            g = int(round(gap[iS] / tick)) if gap[iS] > 0 else 0
            out.append(("s", js - j0, False, g, 0))
        elif t_in:
            out.append(("s", jt - j0, True, 0, 0))
        else:
            out.append(("f", end - j0, False, 0, int(round(mark / tick))))
    return out


def day_walks(o, h, l, c, slots, delays, levels, brackets, slip: float, tick: float, flat: int, cut: int | None):
    """Every (slot, delay, side) walk of a day with no box (T23's `T_NO_BOX`): [(slot, delay, side, entry bar, outs)]."""
    last = last_bar(o, flat)
    if last is None:
        return []
    lv = np.asarray(levels, dtype=float)
    stop_at_cut = min(last, cut) if cut is not None else last
    rows = []
    for t in slots:
        if t >= last:
            continue
        for dl in delays:
            j0 = entry_bar(o, t, dl, last)
            if j0 is None:
                continue
            end = stop_at_cut if (cut is not None and j0 <= cut) else last
            for d in (1, -1):
                entry, fav, adv, gap, mark = walk(o, h, l, c, j0, end, d, slip, lv)
                rows.append((t, dl, d, j0, outcomes(j0, end, fav, adv, gap, mark, brackets, tick)))
    return rows


__all__ = ["EPS", "last_bar", "entry_bar", "walk", "outcomes", "day_walks"]
