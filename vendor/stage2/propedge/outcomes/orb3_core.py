"""ORB3's day records (config/orb3_search.yaml; T15 item 9, D-256), in plain Python for the repository and the kit.

ORB1's entry, unchanged (`propedge/outcomes/orb_core.py`: the ranges from 08:30 CT, direction from each range's
candle, a stop order at its edge filled one micro tick beyond or at a gapped bar's open plus the tick), recorded so that
every cell of ORB3's grid is scored from the same runs: for each range and each stop width of the grid (a fraction of
the 14-day ATR), the first bar on which the adverse move from the fill reaches the stop and the first bars on which the
favourable move trades through 1.5 and 2 times it; the 15:08 close; and the fill bar's own close and excursions, so the
scorer can read the fill bar the kit's way or the strict way (D-254).

**The conventions**, as ORB1's walk: a bar whose low (long; high, short) reaches the stop is the stop's; a favourable
level counts once a bar trades through it; a bar doing both is the stop's (the scorer reads equal slots as the stop).
When the fill is at the bar's open the whole bar follows it and is walked; when the fill is inside its bar the order of
its prices is unknown, so the walk starts on the next bar and the fill bar is left to the scorer. A bar that opens
through the stop is the stop's bar; its gap is not recorded (in ORB's hours about one stop in seven thousand gaps,
D-255). Slots are offsets from the fill bar, -1 for never by 15:08.
"""
from propedge.outcomes.orb_core import (FLAT_ENTRY, NONE, OR_MIN, OR_MINS, OR_START, direction, last_close_by,
                                        trigger, window_stats)


def passages(o, h, l, jf, fill, d, adverse, favour, end, at_open):
    """([first slot each adverse distance is reached], [first slot each favourable distance is traded through]), each
    NONE if not by `end`; from the fill bar when `at_open`, else from the next bar. Distances in price."""
    a_first = [NONE] * len(adverse)
    f_first = [NONE] * len(favour)
    left = len(adverse) + len(favour)
    for j in range(jf if at_open else jf + 1, end + 1):
        if o[j] is None:
            continue
        against = (fill - l[j]) if d > 0 else (h[j] - fill)
        towards = (h[j] - fill) if d > 0 else (fill - l[j])
        for k, a in enumerate(adverse):
            if a_first[k] == NONE and against >= a - 1e-12:
                a_first[k] = j
                left -= 1
        for k, x in enumerate(favour):
            if f_first[k] == NONE and towards > x + 1e-12:
                f_first[k] = j
                left -= 1
        if not left:
            break
    return a_first, f_first


def block3(o, h, l, c, v, n, P, or_vol, stop_ticks, end, t):
    """One range's part of the day's record (`BLOCK3_FIELDS`, then per stop width the offsets A, F1.5, F2)."""
    k = len(stop_ticks)
    rng = window_stats(o, h, l, c, v, OR_START, n)
    if rng is None or OR_START + n >= end:
        return [0, NONE, NONE, 0, 0, 0, 0, 0] + [NONE] * (3 * k)
    first_open, hi, lo, close_n, vol = rng
    d = direction(first_open, close_n)
    rv = int(round(100 * vol / or_vol)) if or_vol else NONE
    trig = trigger(o, h, l, hi if d > 0 else lo, d, OR_START + n, end - 1) if d else None
    if not trig:
        return [d, rv, NONE, 0, 0, 0, 0, 0] + [NONE] * (3 * k)
    jf, px = trig
    fill = px + d * P["slip"]
    at_open = px == o[jf]
    tick = P["tick"]
    adverse = [s * tick for s in stop_ticks]
    favour = [R * s * tick for s in stop_ticks for R in P["rr"]]
    a_first, f_first = passages(o, h, l, jf, fill, d, adverse, favour, end, at_open)
    x = last_close_by(c, end)
    rec = [d, rv, jf, int(at_open), t(d * (c[jf] - fill)) if c[jf] is not None else 0,
           t((fill - l[jf]) if d > 0 else (h[jf] - fill)), t((h[jf] - fill) if d > 0 else (fill - l[jf])),
           t(d * (x - fill)) if x is not None else 0]
    off = lambda s: s - jf if s != NONE else NONE                              # noqa: E731
    for i in range(k):
        rec += [off(a_first[i])] + [off(f_first[i * len(P["rr"]) + r]) for r in range(len(P["rr"]))]
    return rec


def day_record3(o, h, l, c, v, last, P, hist):
    """One day's ORB3 record, integers in the micro's ticks: `SHARED3_FIELDS` (the ATR, then each grid width's stop in
    ticks), then one block per range of `OR_MINS`; None without the 5-minute range or the histories. P 'tick', 'slip'
    (price), 'stops' (the grid's fractions of the ATR), 'rr' (the favourable multiples, 1.5 and 2); hist as ORB1's."""
    if last is None or last < OR_START + OR_MIN + 1 or not hist.get("atr"):
        return None
    if window_stats(o, h, l, c, v, OR_START, OR_MIN) is None:
        return None
    tick = P["tick"]
    t = lambda x: int(round(x / tick))                                         # noqa: E731
    stop_ticks = [max(1, int(round(s * hist["atr"] / tick))) for s in P["stops"]]
    end = min(last, FLAT_ENTRY)
    rec = [t(hist["atr"])] + stop_ticks
    or_vol = hist.get("or_vol") or {}
    for n in OR_MINS:
        rec += block3(o, h, l, c, v, n, P, or_vol.get(n), stop_ticks, end, t)
    return rec


#: The record after the date: the ATR, the grid's stops in ticks, then per range of OR_MINS `BLOCK3_FIELDS` and, per
#: stop width, the offsets of its stop (A), and of 1.5 and 2 times it (F15, F2) from the fill bar.
SHARED3_FIELDS = ("atr_ticks",)
BLOCK3_FIELDS = ("dir", "rv100", "fill_slot", "at_open", "fill_bar_close_ticks", "fill_bar_against_ticks",
                 "fill_bar_favour_ticks", "close_ticks")

__all__ = ["passages", "block3", "day_record3", "SHARED3_FIELDS", "BLOCK3_FIELDS"]
