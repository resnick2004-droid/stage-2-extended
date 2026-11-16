"""ORB6's data-capture records (D-276 to D-278), in plain Python for the repository and the kit.

No hypothesis and no selection: the new runs re-walk ORB3's days (R102-R104, joined to ORB5's captures R105-R107) and
record what ORB6's structural changes need and the earlier records lack:

* **the classic stop**: for the hand-traded entry at `LATENCY` minutes (`orb5_core.hand_entry`, D-266), the stop at
  the range's far side -- one tick beyond its low for a long, its high for a short -- its distance from that entry in
  ticks, and the first bars that stop is reached and `RANGE_RR` times its distance traded through;
* **the retest entry**: the breakout is the operator's alert, so the limit at the broken edge works from the end of the
  breakout's bar + `LATENCY` (the operator's five minutes from an alert to an order, D-278); it fills on the first later
  bar that trades through the level by a tick (never on a touch, D-145 tier 1) -- at the level, or, when that bar
  opens through the level, at its open plus the slip as a marketable limit (the chase's convention, D-266), never worse
  than the level; its bar, at-open flag, the fill's distance from the level, the fill-bar close and adverse excursion,
  15:08 close, 15:07-15:10 worst and the spread at its minute, all from the fill, and from it the first bars each stop
  width of ORB3's grid is reached and `RETEST_RR` times it traded through, and the range stop's passages as above;
* **the unconditional entries** (D-277's per-side drift benchmark): on every day, a long and a short at the open of the
  first bar after each of `BENCH_SLOTS` (08:40 to 11:35 CT), with the 15:08 close and each side's 15:07-15:10 worst,
  and per side one outcome per bracket -- every stop width, then each range's own stop (its range plus a tick, once the
  range has closed and five minutes passed), each at `RETEST_RR` -- read strictly (`outcome_codes`);
* **the filters**, at the signal: the overnight move (the 08:30 open less the session's first open), the gap (the 08:30
  open less the previous session's last close on the same contract) and, per range, its close less the Globex
  session's volume-weighted average price from 17:00 CT to that minute -- in ticks, MISSING6 where there is no value.

Offsets are from the entry's bar, -1 for never by 15:08; prices in ticks from the entry, signed with the trade.
"""
from propedge.outcomes.orb3_core import passages
from propedge.outcomes.orb5_core import LATENCY, MISSING5, _spread, hand_entry, worst_in
from propedge.outcomes.orb_core import (FLAT_ENTRY, NONE, OR_MIN, OR_MINS, OR_START, direction, last_close_by,
                                        trigger, window_stats)

MISSING6 = MISSING5
RANGE_RR = (0.5, 0.75, 1.0, 1.5, 2.0, 3.0)    # targets in multiples of the range stop's distance
RETEST_RR = (1.0, 1.5, 2.0, 3.0)              # targets in multiples of an ATR-width stop, from the retest
FLATTEN_BARS = (FLAT_ENTRY, FLAT_ENTRY + 1, FLAT_ENTRY + 2)
BENCH_SLOTS = (940, 950, 965, 995, 1025, 1055, 1085, 1115)    # 08:40, 08:50, 09:05, 09:35, then every 30 to 11:35
STOP_FIRST, TARGET_FIRST, OPEN, NO_BRACKET = "0", "1", "2", "9"


def session_vwap(h, l, c, v, upto):
    """The volume-weighted average typical price of the bars ending at or before `upto` (None without volume)."""
    num = den = 0.0
    for j in range(1, min(upto, len(c) - 1) + 1):
        if c[j] is None or not v[j]:
            continue
        num += (h[j] + l[j] + c[j]) / 3.0 * v[j]
        den += v[j]
    return num / den if den else None


def retest(o, h, l, d, level, start, end, tick):
    """(bar, at its open) of the first bar after `start` trading back through `level` by a tick against the breakout
    (a long's limit at the range high fills when a bar's low reaches a tick below it); None by 15:07."""
    for j in range(start + 1, end):
        if o[j] is None:
            continue
        if (l[j] <= level - tick) if d > 0 else (h[j] >= level + tick):
            return j, ((o[j] <= level - tick) if d > 0 else (o[j] >= level + tick))
    return None


def range_walk(o, h, l, jl, fill, d, far, end, at_open, t):
    """The range stop from an entry: [its distance in ticks, the first bar it is reached, the first bars RANGE_RR times
    its distance are traded through], offsets from the entry's bar; the stop one tick beyond the range's far side."""
    dist = d * (fill - far)
    if dist <= 0:
        return [NONE] * (2 + len(RANGE_RR))
    a, f = passages(o, h, l, jl, fill, d, [dist], [R * dist for R in RANGE_RR], end, at_open)
    off = lambda s: s - jl if s != NONE else NONE                              # noqa: E731
    return [t(dist)] + [off(a[0])] + [off(x) for x in f]


def outcome_codes(o, h, l, j1, entry, d, dists, end):
    """From an entry at bar j1's open, per stop distance (None: no bracket) and `RETEST_RR`, the bracket's outcome read
    strictly -- the target traded through on an earlier bar than the stop is reached, else the stop if reached, else
    open at 15:08 -- as one digit each."""
    real = [x for x in dists if x is not None]
    nr = len(RETEST_RR)
    a, f = passages(o, h, l, j1, entry, d, real, [R * x for x in real for R in RETEST_RR], end, True)
    codes, i = "", 0
    for x in dists:
        if x is None:
            codes += NO_BRACKET * nr
            continue
        for r in range(nr):
            s, g = a[i], f[i * nr + r]
            codes += (TARGET_FIRST if g != NONE and (s == NONE or g < s) else
                      (STOP_FIRST if s != NONE else OPEN))
        i += 1
    return codes


def bench_day(o, h, l, c, end, stop_ticks, ranges, tick, t):
    """`BENCH_FIELDS` per slot of `BENCH_SLOTS`: the entry's bar, its 15:08 close in ticks (long's sense), the long's
    and the short's worst, then the long's and the short's `outcome_codes` over every stop width and each range's stop
    (`ranges`: per range of OR_MINS (hi, lo) or None), each code string written as an integer after a leading 1."""
    nr = len(RETEST_RR)
    rec = []
    for s in BENCH_SLOTS:
        j1 = next((j for j in range(s + 1, end) if o[j] is not None), None)
        if j1 is None:
            rec += [NONE, 0, MISSING6, MISSING6] + [int("1" + NO_BRACKET * nr * (len(stop_ticks) + len(ranges)))] * 2
            continue
        e = o[j1]
        x = last_close_by(c, end)
        rec += [j1, t(x - e) if x is not None else 0]
        for d in (1, -1):
            w = worst_in(h, l, d, e, FLATTEN_BARS)
            rec.append(t(w) if w is not None else MISSING6)
        dists = [k * tick for k in stop_ticks] + [
            (r[0] - r[1] + tick) if r is not None and OR_START + n + LATENCY <= s else None
            for n, r in zip(OR_MINS, ranges)]
        for d in (1, -1):
            rec.append(int("1" + outcome_codes(o, h, l, j1, e, d, dists, end)))
    return rec


def block6(o, h, l, c, v, q, n, P, stop_ticks, end, t, vwap):
    """One range's part of the record: `BLOCK6_FIELDS`, the hand-traded entry's range walk, the retest's fields
    (`RETEST_FIELDS`), its range walk and, per stop width, its stop's and RETEST_RR's offsets."""
    k = len(stop_ticks)
    nrw = 2 + len(RANGE_RR)
    empty_rt = [0, NONE, 0, 0, 0, 0, 0, MISSING6, NONE] + [NONE] * nrw + [NONE] * ((1 + len(RETEST_RR)) * k)
    empty = [0, NONE, 0, MISSING6] + [NONE] * nrw + empty_rt
    rng = window_stats(o, h, l, c, v, OR_START, n)
    if rng is None or OR_START + n >= end:
        return empty
    first_open, hi, lo, close_n, _ = rng
    d = direction(first_open, close_n)
    tick = P["tick"]
    vw = vwap(OR_START + n)
    head = [d, NONE, t(hi - lo), t(close_n - vw) if vw is not None else MISSING6]
    level = hi if d > 0 else lo
    trig = trigger(o, h, l, level, d, OR_START + n, end - 1) if d else None
    if not trig:
        return head + empty[4:]
    jf, px = trig
    head[1] = jf
    far = (lo - tick) if d > 0 else (hi + tick)
    hand = hand_entry(o, h, l, d, level, jf, px, OR_START + n, end, P["slip"])
    rec = head + (range_walk(o, h, l, hand[1], hand[2], d, far, end, hand[3], t) if hand else [NONE] * nrw)
    rt = retest(o, h, l, d, level, jf + LATENCY, end, tick)
    if rt is None:
        return rec + empty_rt
    jr, r_open = rt
    fill = o[jr] + d * P["slip"] if r_open else level
    if d * (fill - level) > 0:
        fill = level
    x = last_close_by(c, end)
    worst = worst_in(h, l, d, fill, FLATTEN_BARS)
    rec += [1, jr, int(r_open), t(d * (level - fill)), t(d * (c[jr] - fill)) if c[jr] is not None else 0,
            t((fill - l[jr]) if d > 0 else (h[jr] - fill)), t(d * (x - fill)) if x is not None else 0,
            t(worst) if worst is not None else MISSING6, _spread(q, jr, tick)]
    rec += range_walk(o, h, l, jr, fill, d, far, end, r_open, t)
    adverse = [s * tick for s in stop_ticks]
    a, f = passages(o, h, l, jr, fill, d, adverse, [R * a_ for a_ in adverse for R in RETEST_RR], end, r_open)
    off = lambda s: s - jr if s != NONE else NONE                              # noqa: E731
    nr = len(RETEST_RR)
    for i in range(k):
        rec += [off(a[i])] + [off(f[i * nr + r]) for r in range(nr)]
    return rec


def day_record6(o, h, l, c, v, q, last, P, hist):
    """One day's record: `SHARED6_FIELDS`, one block per range of `OR_MINS`, then `bench_day`; None on the days ORB3
    writes none. P as ORB3's ('tick', 'slip', 'stops'); `q` each bar's spread at its open; hist as ORB1's."""
    if last is None or last < OR_START + OR_MIN + 1 or not hist.get("atr"):
        return None
    if window_stats(o, h, l, c, v, OR_START, OR_MIN) is None:
        return None
    tick = P["tick"]
    t = lambda x: int(round(x / tick))                                         # noqa: E731
    stop_ticks = [max(1, int(round(s * hist["atr"] / tick))) for s in P["stops"]]
    end = min(last, FLAT_ENTRY)
    first = next((j for j in range(1, len(o)) if o[j] is not None), None)
    open_830 = next((o[j] for j in range(OR_START + 1, OR_START + OR_MIN + 1) if o[j] is not None), None)
    prev = hist.get("prev_close")
    rec = [t(hist["atr"]), t(open_830 - o[first]) if (first is not None and open_830 is not None) else MISSING6,
           t(open_830 - prev) if (prev is not None and open_830 is not None) else MISSING6]
    cache = {}

    def vwap(upto):
        if upto not in cache:
            cache[upto] = session_vwap(h, l, c, v, upto)
        return cache[upto]
    ranges = []
    for n in OR_MINS:
        rec += block6(o, h, l, c, v, q, n, P, stop_ticks, end, t, vwap)
        w = window_stats(o, h, l, c, v, OR_START, n)
        ranges.append((w[1], w[2]) if w is not None and OR_START + n < end else None)
    return rec + bench_day(o, h, l, c, end, stop_ticks, ranges, tick, t)


#: The record after the date: SHARED6_FIELDS; then per range BLOCK6_FIELDS, the hand-traded entry's range walk
#: (`hand_range_*`: distance, stop, RANGE_RR), RETEST_FIELDS, the retest's range walk and per stop width the retest's
#: stop and RETEST_RR offsets; then per slot of BENCH_SLOTS, BENCH_FIELDS.
SHARED6_FIELDS = ("atr_ticks", "overnight_ticks", "gap_ticks")
BLOCK6_FIELDS = ("dir", "fill_slot", "range_ticks", "vwap_offset_ticks")
RETEST_FIELDS = ("rt_kind", "rt_slot", "rt_at_open", "rt_better_ticks", "rt_fill_bar_close_ticks",
                 "rt_fill_bar_against_ticks", "rt_close_ticks", "rt_worst_ticks", "rt_spread_tenths")
BENCH_FIELDS = ("bench_slot", "bench_close_ticks", "bench_worst_long_ticks", "bench_worst_short_ticks",
                "bench_codes_long", "bench_codes_short")

__all__ = ["MISSING6", "RANGE_RR", "RETEST_RR", "BENCH_SLOTS", "session_vwap", "retest", "range_walk",
           "outcome_codes", "bench_day", "block6", "day_record6", "SHARED6_FIELDS", "BLOCK6_FIELDS", "RETEST_FIELDS",
           "BENCH_FIELDS"]
