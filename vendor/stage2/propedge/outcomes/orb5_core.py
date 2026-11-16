"""ORB5's data-capture records (T16 item 3; D-263 to D-266), in plain Python for the repository and the kit.

No hypothesis and no selection: the new runs (R105-R107) re-walk ORB3's days (R102-R104, the same entries, stops and
windows) and record only what those records lack, so that ORB5's grid can be declared on them:

* for each range and each stop width of ORB3's grid, the first bar the favourable move from the fill trades through
  0.75, 1 and 1.25 times the stop (the Combine's $1,500 target at a risk of $2,000, $1,500 or $1,200, D-267) and 3, 5
  and 8 times it (the review's ">= 5R target", D-263) -- the same convention as ORB3's 1.5R and 2R passages
  (`propedge/outcomes/orb3_core.py`: a level counts once a bar trades through it; the fill bar walked only when the
  fill is at its open);
* the worst price against the trade over the bars covering 15:07 to 15:10 CT (ending 15:08, 15:09, 15:10), as a signed
  distance from the fill in ticks, negative when against the trade -- the price a direction-style trade still open is
  flattened at, plus 2 ticks, from ORB5 (D-263);
* the bid-ask spread in tenths of the micro's tick: at the open of the fill minute and of the minute after it (the fill
  falls inside its minute on most trades, so the two bracket it), and once a day at 15:07, 15:08 and 15:09 (the opens
  of the bars ending 15:08 to 15:10). It is NQ's quote -- the kit trades NQ's data, and MNQ did not exist before May
  2019 -- so a proxy, and likely a lower bound, for MNQ's (D-265). The regime body records ask - bid at the quote bar's
  open only when the quote is two-sided, not crossed and at most 50 micro ticks wide (`badq` counts the rest); a locked
  quote is 0; NONE where none was recorded;
* **the hand-traded entry** (D-266): the operator places every order by hand and needs about `LATENCY` minutes from the
  signal (the range's close) to a working order. If the stop order would have triggered after that, the entry is the
  same; if it would have triggered sooner and the next bar opens beyond the level, the operator buys (sells) at that
  open plus a tick -- the chase; if the price is back inside the range, the stop order rests at the level and fills when
  it next trades through (the late stop). For that entry: its kind, bar, at-open flag, distance from the original fill,
  15:08 close, 15:07-15:10 worst, its own fill bar's close and adverse excursion (the scorer's two readings, D-254), the
  spreads at its fill minute and the next, and at every stop width of the grid -- the stop now measured from this entry
  -- the first bars its stop is reached and 0.75, 1, 1.25, 1.5, 2, 3, 5 and 8 times it traded through (`LAT_RR`), so
  every cell ORB5 can declare is scored at the latency too.

Each block repeats ORB3's direction, fill bar, at-open flag and 15:08 close, so ORB5's ingest and scorer join it to
ORB3's record of the same day and range and catch a mismatch (D-265). Offsets are from the fill bar (the hand-traded
entry's from its own bar), -1 for never by 15:08. In the kit's output a -1 is written as nothing (`encode_day5`), which
keeps the order tags few (D-267).
"""
from propedge.outcomes.orb3_core import passages
from propedge.outcomes.orb_core import (FLAT_ENTRY, NONE, OR_MIN, OR_MINS, OR_START, direction, last_close_by,
                                        trigger, window_stats)

MISSING5 = -999999                       # no bar in the 15:07-15:10 window (a signed field, so not -1)
ADD_RR = (0.75, 1.0, 1.25, 3.0, 5.0, 8.0)   # the targets the new records add, beside ORB3's 1.5R and 2R
FLATTEN_BARS = (FLAT_ENTRY, FLAT_ENTRY + 1, FLAT_ENTRY + 2)   # bars ending 15:08, 15:09, 15:10 CT
LATENCY = 5                              # D-266: minutes from the signal to the operator's working order
LAT_RR = tuple(sorted(ADD_RR + (1.5, 2.0)))   # the hand-traded entry's targets: ORB3's and the new ones
#: the hand-traded entry's kind
SAME, CHASE, LATE_STOP = 0, 1, 2


def worst_in(h, l, d, fill, bars):
    """The worst price against a trade over `bars`, as a signed distance from the fill (<= 0 when adverse); None
    without a bar."""
    xs = [(l[j] - fill) if d > 0 else (fill - h[j]) for j in bars if j < len(l) and l[j] is not None]
    return min(xs) if xs else None


def _spread(q, j, tick):
    return int(round(q[j] / tick * 10)) if (0 <= j < len(q) and q[j] is not None) else NONE


def hand_entry(o, h, l, d, level, jf, px, signal, end, slip):
    """(kind, bar, fill price, at its bar's open) of the operator's entry when the order works only from the end of bar
    `signal + LATENCY`; None if there is none by 15:07."""
    live = signal + LATENCY
    if jf > live:
        return SAME, jf, px + d * slip, px == o[jf]
    j1 = next((j for j in range(live + 1, end) if o[j] is not None), None)
    if j1 is None:
        return None
    if (o[j1] > level) if d > 0 else (o[j1] < level):
        return CHASE, j1, o[j1] + d * slip, True
    trig = trigger(o, h, l, level, d, live, end - 1)
    if not trig:
        return None
    j, p = trig
    return LATE_STOP, j, p + d * slip, p == o[j]


def block5(o, h, l, c, v, q, n, P, stop_ticks, end, t):
    """One range's part of the capture record: `BLOCK5_FIELDS`, then per stop width the offsets of `ADD_RR` times it,
    then `LAT_FIELDS` and, per stop width, the hand-traded entry's offsets of its stop and of `LAT_RR` times it."""
    k = len(stop_ticks)
    nr = len(LAT_RR)
    lat_none = [NONE, NONE, 0, 0, 0, MISSING5, 0, 0, NONE, NONE] + [NONE] * ((1 + nr) * k)
    empty = [0, NONE, 0, 0, MISSING5, NONE, NONE] + [NONE] * (len(ADD_RR) * k) + lat_none
    rng = window_stats(o, h, l, c, v, OR_START, n)
    if rng is None or OR_START + n >= end:
        return empty
    first_open, hi, lo, close_n, _ = rng
    d = direction(first_open, close_n)
    level = hi if d > 0 else lo
    trig = trigger(o, h, l, level, d, OR_START + n, end - 1) if d else None
    if not trig:
        return [d] + empty[1:]
    jf, px = trig
    fill = px + d * P["slip"]
    tick = P["tick"]
    at_open = px == o[jf]
    favour = [R * s * tick for s in stop_ticks for R in ADD_RR]
    _, f_first = passages(o, h, l, jf, fill, d, [], favour, end, at_open)
    worst = worst_in(h, l, d, fill, FLATTEN_BARS)
    x = last_close_by(c, end)
    rec = [d, jf, int(at_open), t(d * (x - fill)) if x is not None else 0,
           t(worst) if worst is not None else MISSING5, _spread(q, jf, tick), _spread(q, jf + 1, tick)]
    rec += [s - jf if s != NONE else NONE for s in f_first]
    hand = hand_entry(o, h, l, d, level, jf, px, OR_START + n, end, P["slip"])
    if hand is None:
        return rec + lat_none
    kind, jl, lfill, l_open = hand
    adverse = [s * tick for s in stop_ticks]
    a_first, f_first = passages(o, h, l, jl, lfill, d, adverse, [R * a for a in adverse for R in LAT_RR], end, l_open)
    lworst = worst_in(h, l, d, lfill, FLATTEN_BARS)
    rec += [kind, jl, int(l_open), t(d * (lfill - fill)), t(d * (x - lfill)) if x is not None else 0,
            t(lworst) if lworst is not None else MISSING5, t(d * (c[jl] - lfill)),
            t((lfill - l[jl]) if d > 0 else (h[jl] - lfill)), _spread(q, jl, tick), _spread(q, jl + 1, tick)]
    off = lambda s: s - jl if s != NONE else NONE                              # noqa: E731
    for i in range(k):
        rec += [off(a_first[i])] + [off(f_first[i * nr + r]) for r in range(nr)]
    return rec


def day_record5(o, h, l, c, v, q, last, P, hist):
    """One day's capture record, integers: `SHARED5_FIELDS` (the ATR in ticks, the join check, and the day's spreads at
    15:07, 15:08, 15:09), then one block per range of `OR_MINS`; None on the days ORB3 writes none. P as ORB3's
    ('tick', 'slip', 'stops'); `q` each bar's bid-ask spread at its open (price)."""
    if last is None or last < OR_START + OR_MIN + 1 or not hist.get("atr"):
        return None
    if window_stats(o, h, l, c, v, OR_START, OR_MIN) is None:
        return None
    tick = P["tick"]
    t = lambda x: int(round(x / tick))                                         # noqa: E731
    stop_ticks = [max(1, int(round(s * hist["atr"] / tick))) for s in P["stops"]]
    end = min(last, FLAT_ENTRY)
    rec = [t(hist["atr"])] + [_spread(q, j, tick) for j in FLATTEN_BARS]
    for n in OR_MINS:
        rec += block5(o, h, l, c, v, q, n, P, stop_ticks, end, t)
    return rec


def encode_day5(td, rec):
    """'yyyymmdd,v1,v2,...' for one day's record, a -1 (never, none) written as nothing (D-267)."""
    return "%04d%02d%02d," % td + ",".join("" if x == NONE else str(int(x)) for x in rec)


def rr_name(R):
    """A passage's column stem: 0.75 -> 'f075', 1.0 -> 'f1', 1.5 -> 'f15' (ORB3's naming)."""
    return f"f{R:g}".replace(".", "")


#: The record after the date: `SHARED5_FIELDS`, then per range `BLOCK5_FIELDS`; per stop width the offsets of 0.75, 1,
#: 1.25, 3, 5 and 8 times the stop from the fill bar; `LAT_FIELDS`; per stop width the hand-traded entry's offsets of its
#: stop and of 0.75, 1, 1.25, 1.5, 2, 3, 5 and 8 times it from its own bar. `worst_flat_ticks` and `lat_worst_ticks` are signed, negative when against
#: the trade; `lat_gap_ticks` is how much worse (positive) the hand-traded entry is than the original fill.
SHARED5_FIELDS = ("atr_ticks", "spread_1507_tenths", "spread_1508_tenths", "spread_1509_tenths")
BLOCK5_FIELDS = ("dir", "fill_slot", "at_open", "close_ticks", "worst_flat_ticks", "spread_fill_tenths",
                 "spread_after_fill_tenths")
LAT_FIELDS = ("lat_kind", "lat_slot", "lat_at_open", "lat_gap_ticks", "lat_close_ticks", "lat_worst_ticks",
              "lat_fill_bar_close_ticks", "lat_fill_bar_against_ticks", "lat_spread_fill_tenths",
              "lat_spread_after_fill_tenths")

__all__ = ["MISSING5", "ADD_RR", "FLATTEN_BARS", "LATENCY", "LAT_RR", "SAME", "CHASE", "LATE_STOP",
           "worst_in", "hand_entry", "block5", "day_record5", "encode_day5", "rr_name", "SHARED5_FIELDS",
           "BLOCK5_FIELDS", "LAT_FIELDS"]
