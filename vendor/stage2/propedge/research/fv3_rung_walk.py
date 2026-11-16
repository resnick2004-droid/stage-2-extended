"""Family A3's walk, step 0 (D-490): A1's mechanical events walked on FV3-C's rungs with FV3's own settlement.

D-490 (1): A1's events -- their minutes, A1's five-bar delay (`fast_walk.entry_bar`, the kits' `c_entry`), the side
rules, the news cut and the development window unchanged -- walked on FV3-C's ladder (`config/fv3_corrected_portfolio.yaml`
`ladder.stops_ticks`: 50 / 100 / 200 ticks, 12.5 / 25 / 50 points) at every quarter R to 3R, each target rounded as
FV3's scorer rounds it (`score_fv3_grid.Signals3.outcome`: floor(R x stop + 1e-9) ticks), and settled as FV3 settles
a trade:

* **The walk** is `fv3_core.profiles`' (the kit's): from the entry bar's open (`e = o[je]`, no slip in the walk -- FV3
  charges the entry's spread and the exit's ticks as costs, `EXIT_TICKS`) to the bar ending 15:08 CT
  (`end = min(last, orb_core.FLAT_ENTRY)`), every bar with an open, the fill bar counted; excursions in whole ticks
  (`int(round(x / tick))`).
* **The bracket** is `fv3_core.settle`'s: a target must be traded through (an excursion beyond it), a stop reached; the
  stop wins a bar on which both happen; the adverse excursion before the exit (MAE) is the stop on a stop, the running
  maximum to the exit bar on a target, the whole walk's on an open trade.
* **Breakeven** is `score_fv3_grid.Signals3.outcome`'s (FV3's rule; the capture's be_* fields, `fv3_core.entry`):
  the next FV3 session open after the entry bar (`fv3_core.next_open`: the first session of `fv3_core.SESSIONS` --
  17:00, 19:00, 08:30, 13:00 CT -- opening after the entry bar, its first bar within five minutes), its open in the
  trade's favour by at least a tick and the trade not exited before that bar: the stop moves to the entry, so the trade
  exits there ('b', booked at zero gross and a tick of cost) on the first bar from that open whose low (long; high,
  short) touches the entry, unless the target is traded through on an earlier bar.
* **The 15:10 flatten** is FV3-C's (`execution.flatten`, config/fv3_corrected_portfolio.yaml): an open trade closes at
  the worst of the bars ending 15:08-15:10 CT (`fv3_core.FLATTEN_BARS`) less two ticks, or the last close by 15:08
  where none of those bars was recorded; its exit bar is `FLAT_ENTRY`, as the scorer writes it.

The kinds are the scorer's codes: 0 stop, 1 target, 2 flatten (unresolved), 3 breakeven. `tests/test_fv3_rung_walk.py`
holds this walk record for record to FV3's own code -- `fv3_core.entry`'s fields fed to `Signals3.outcome` -- on random
synthetic days and on real days.

This module never edits nor re-implements A1's walk (`atlas_core`, `fast_walk`, `atlas_local`, `atlas_walk.walk_days`),
whose source digest pins A1's walk cache and P-11's and P-12's identities; it imports `fast_walk.entry_bar` and
`fast_walk.last_bar` unchanged.
"""
from __future__ import annotations

import math

import numpy as np

from propedge.outcomes.collect_core import C_FLAT
from propedge.outcomes.fv3_core import FLATTEN_BARS, SESSIONS
from propedge.outcomes.orb_core import FLAT_ENTRY, NONE
from propedge.research import fast_walk

#: FV3-C's rungs in ticks (config/fv3_corrected_portfolio.yaml `ladder.stops_ticks`: half, full, double)
STOPS_TICKS = (50, 100, 200)
#: every quarter R to 3R (FV3-C's `fidelity.rr_menu`)
RR_GRID = tuple(0.25 * k for k in range(1, 13))
#: FV3's exit ticks by kind (`score_fv3_grid`: a tick on a stop or a breakeven, none at a target, two on the flatten)
STOP_SLIP_TICKS, FLATTEN_SLIP_TICKS = 1, 2
EXIT_TICKS = {0: STOP_SLIP_TICKS, 1: 0, 2: FLATTEN_SLIP_TICKS, 3: STOP_SLIP_TICKS}
STOP, TARGET, FLATTEN, BREAKEVEN = 0, 1, 2, 3
SESSION_OPENS = tuple(s for _, s, _, _ in SESSIONS)


def target_ticks(R: float, stop: int) -> int:
    """The target in ticks as FV3's scorer rounds it: floor(R x stop + 1e-9)."""
    return int(math.floor(R * stop + 1e-9))


def brackets(stops=STOPS_TICKS, rrs=RR_GRID) -> list[tuple[int, float, int]]:
    """[(stop ticks, R, target ticks)], stop by stop, R ascending."""
    return [(S, float(R), target_ticks(R, S)) for S in stops for R in rrs]


BRACKETS = brackets()


def _t(x: np.ndarray, tick: float) -> np.ndarray:
    """`int(round(x / tick))` elementwise (half to even, as Python's round)."""
    return np.round(x / tick)


def entries(o: np.ndarray, slots, delay: int) -> list[tuple[int, int, int]]:
    """[(event slot, side, entry bar)] for each slot and both sides: A1's entry (`fast_walk.entry_bar`, the `delay`-th
    bar with an open after the slot, at or before the day's last bar; no entry from a slot at or after it) that FV3 can
    fill (before the bar ending 15:08 CT, `fv3_core.entry`'s range)."""
    last = fast_walk.last_bar(o, C_FLAT)
    if last is None:
        return []
    end = min(last, FLAT_ENTRY)
    out = []
    for t in slots:
        t = int(t)
        if t >= last:
            continue
        j0 = fast_walk.entry_bar(o, t, int(delay), last)
        if j0 is None or j0 >= end:
            continue
        out += [(t, 1, j0), (t, -1, j0)]
    return out


def walk(o, h, l, c, sides, entry_bars, tick: float, bracket_list=None) -> dict[str, np.ndarray]:
    """Every given entry (side, entry bar) walked and settled at every bracket of `bracket_list` (default `BRACKETS`).

    Arrays o, h, l, c: one trading day on the trading-day clock (index j = a bar's END minute after 17:00 CT, NaN where
    no bar). Returns 'kind', 'exit' (bar), 'mae' (ticks), 'gross' (ticks) of shape (walks, brackets), and per walk
    'be_open' (the next session's open bar or NONE), 'be_favour' (ticks), 'be_touch' (bar or NONE), 'worst' (ticks or
    NaN), 'close' (ticks)."""
    bl = BRACKETS if bracket_list is None else bracket_list
    o, h, l, c = (np.asarray(x, dtype=float) for x in (o, h, l, c))
    d = np.asarray(sides, dtype=float)
    je = np.asarray(entry_bars, dtype=int)
    W, B, n = len(je), len(bl), len(o)
    out = {k: np.zeros((W, B), dtype=np.int32) for k in ("kind", "exit", "mae", "gross")}
    if W == 0:
        for k in ("be_open", "be_favour", "be_touch", "close"):
            out[k] = np.zeros(0, dtype=np.int64)
        out["worst"] = np.zeros(0)
        return out
    last = fast_walk.last_bar(o, C_FLAT)
    if last is None:
        raise ValueError("a day with no bar has no entry")
    end = min(last, FLAT_ENTRY)
    if (je >= end).any() or np.isnan(o[je]).any():
        raise ValueError("an entry at or after 15:08 CT, or on a bar with no open")
    e = o[je]
    J = np.arange(n)
    present = ~np.isnan(o)
    live = present[None, :] & (J[None, :] >= je[:, None]) & (J[None, :] <= end)
    long = d[:, None] > 0
    with np.errstate(invalid="ignore"):
        fav = np.where(long, h[None, :] - e[:, None], e[:, None] - l[None, :])
        adv = np.where(long, e[:, None] - l[None, :], h[None, :] - e[:, None])
    fav = np.where(live, _t(fav, tick), -np.inf)
    adv = np.where(live, _t(adv, tick), -np.inf)
    rmf = np.maximum.accumulate(fav, axis=1)
    rma = np.maximum.accumulate(adv, axis=1)
    rows = np.arange(W)

    def first(rm: np.ndarray, thr: float, strict: bool) -> np.ndarray:
        m = rm > thr if strict else rm >= thr
        k = m.argmax(axis=1)
        return np.where(m[rows, k], k, NONE)

    def mae_at(j: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, rma[rows, np.where(j >= 0, j, n - 1)])

    # breakeven: the next session's open bar (fv3_core.next_open), its open against the entry, the first touch from it
    jn = np.full(W, NONE)
    for u in np.unique(je):
        s = next((s for s in SESSION_OPENS if s > u), None)
        if s is None:
            continue
        xs = [x for x in range(s + 1, min(s + 6, end + 1)) if present[x]]
        if xs:
            jn[je == u] = xs[0]
    has_jn = jn != NONE
    with np.errstate(invalid="ignore"):
        be_fav = np.where(has_jn, _t(d * (o[np.where(has_jn, jn, 0)] - e), tick), 0.0)
        touch_m = present[None, :] & (J[None, :] >= jn[:, None]) & (J[None, :] <= end) & has_jn[:, None] & np.where(
            long, l[None, :] <= e[:, None], h[None, :] >= e[:, None])
    k = touch_m.argmax(axis=1)
    touch = np.where(touch_m[rows, k], k, NONE)
    # the flatten: the worst of 15:07-15:10 less two ticks, else the last close by 15:08
    fb = [j for j in FLATTEN_BARS if j < n]
    with np.errstate(invalid="ignore"):
        wv = np.stack([np.where(d > 0, l[j] - e, e - h[j]) for j in fb], axis=1) if fb else np.full((W, 1), np.nan)
    has_w = ~np.isnan(wv).all(axis=1)
    worst = np.where(has_w, _t(np.nanmin(np.where(np.isnan(wv), np.inf, wv), axis=1), tick), np.nan)
    jc = next((j for j in range(min(end, n - 1), 0, -1) if not np.isnan(c[j])), None)
    close = _t(d * (c[jc] - e), tick) if jc is not None else np.zeros(W)
    flat_move = np.where(has_w, worst - FLATTEN_SLIP_TICKS, close)
    be_ok = has_jn & (be_fav > 0)
    mae_all = mae_at(np.full(W, n - 1))

    cache_s: dict[int, np.ndarray] = {}
    cache_t: dict[int, np.ndarray] = {}
    for b, (S, _R, T) in enumerate(bl):
        if S not in cache_s:
            cache_s[S] = first(rma, S, strict=False)
        if T not in cache_t:
            cache_t[T] = first(rmf, T, strict=True)
        ja, js = cache_s[S], cache_t[T]
        stop = (ja != NONE) & ((js == NONE) | (ja <= js))
        tgt = ~stop & (js != NONE)
        off = np.where(stop, ja, np.where(tgt, js, NONE))
        kind = np.where(stop, STOP, np.where(tgt, TARGET, FLATTEN))
        ex = np.where(off != NONE, off, FLAT_ENTRY)
        mae = np.where(stop, float(S), np.where(tgt, mae_at(js), mae_all))
        # the breakeven move: open at the next session's open, that open in favour -> the stop at the entry
        app = be_ok & ((off == NONE) | (jn < off))
        bt = app & (touch != NONE) & ((js == NONE) | (touch < js))
        btg = app & ~bt & (js != NONE)
        bop = app & ~bt & ~btg
        kind = np.where(bt, BREAKEVEN, np.where(btg, TARGET, np.where(bop, FLATTEN, kind)))
        ex = np.where(bt, touch, np.where(btg, js, np.where(bop, FLAT_ENTRY, ex)))
        mae = np.where(bt, mae_at(touch), np.where(btg, mae_at(js), np.where(bop, mae_all, mae)))
        gross = np.select([kind == STOP, kind == TARGET, kind == BREAKEVEN], [-float(S), float(T), 0.0], flat_move)
        out["kind"][:, b] = kind
        out["exit"][:, b] = ex
        out["mae"][:, b] = mae
        out["gross"][:, b] = gross
    out.update({"be_open": jn, "be_favour": be_fav.astype(np.int64), "be_touch": touch, "worst": worst,
                "close": np.asarray(close, dtype=np.int64)})
    return out


def day_walks(o, h, l, c, slots, delay: int, tick: float, bracket_list=None):
    """(the entries [(slot, side, entry bar)], `walk`'s arrays) for one day's event slots, both sides, at A1's delay."""
    ent = entries(np.asarray(o, dtype=float), slots, delay)
    res = walk(o, h, l, c, [x[1] for x in ent], [x[2] for x in ent], tick, bracket_list)
    return ent, res


__all__ = ["STOPS_TICKS", "RR_GRID", "STOP_SLIP_TICKS", "FLATTEN_SLIP_TICKS", "EXIT_TICKS", "STOP", "TARGET",
           "FLATTEN", "BREAKEVEN", "SESSION_OPENS", "BRACKETS", "target_ticks", "brackets", "entries", "walk",
           "day_walks"]
