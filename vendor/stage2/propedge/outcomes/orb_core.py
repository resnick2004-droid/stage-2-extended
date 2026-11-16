"""ORB1, the opening-range breakout on NQ and ES (config/orb_model.yaml; T15 item 9, D-249, D-250), in plain Python for
the repository and the kit -- the paper's 5-minute range, and its 15-, 30- and 60-minute ranges (its Table 3) on the
same rules, each with its own relative volume (the range's volume over the previous 14 days' mean for that range).

The rules are Zarattini, Barbon & Aziz (2024), "A Profitable Day Trading Strategy For The U.S. Equity Market" (SSRN
4729284, section 2.1 and section 4), read from the paper: the opening range is the first 5 minutes of the cash session
(08:30-08:35 CT); a bullish first candle (close above open) allows only a long, a bearish one only a short, a doji
neither; a stop order at the range's high (long) or low (short); the stop loss 10 % of the 14-day ATR from the fill;
no profit target, the position closed at the session's end if not stopped -- here the last bar at or before 15:08 CT,
when Topstep's Risk Managers begin flattening (8284206, D-247). Relative volume is the opening range's volume over the
mean of the previous 14 days' (the paper's formula); the paper trades it at 100 % or more.

The QuantConnect kit embeds `regime_core` and then this module verbatim (its one import line removed) and records one
line per day; only those records leave (D-120). Missing bars are `None`. A slot is a bar's END time in minutes after
17:00 (regime_core's clock): the bar ending 08:31 CT is slot 931, the bar ending 15:08 is slot 1328.

**The fill and the walk, stated so they can be judged.** The entry triggers on the first bar after the range whose high
reaches the level (long; the low for a short), up to the bar ending 15:07; it fills at the level plus one micro tick
adverse, or at the bar's open plus the tick when the bar opens at or beyond the level (a gap). When the fill is at the
bar's open the whole bar follows it and is walked like any later bar; when the fill is inside the bar the order of its
prices is unknown, so there the stop counts only if the bar CLOSES at or beyond it and no target counts -- and the
fill bar's excursions against and for the fill are recorded, so the strict reading can be computed afterwards (the
pre-run review, 2026-10-03). From the next bar on, a bar opening through the stop is the stop's (its gap the
overshoot), a bar whose low (high for a short) reaches it is the stop's, a favourable level counts once a bar trades
through it, and a bar touching both is the stop's.

**The ATR** is the simple mean of the previous 14 full sessions' true ranges -- Topstep's 17:00-15:10 session's high
less its low, widened to the previous session's last close on the same contract -- not Wilder's smoothing; wider than a
regular-session ATR, so the stop is too. **Relative volume** sums every contract's volume in the minute, so a roll's
split volume does not read as a quiet open.
"""
from propedge.outcomes.regime_core import FLAT

OR_START, OR_MIN = 930, 5            # 08:30 CT, five minutes: bars ending 08:31 to 08:35 (slots 931-935)
OR_MINS = (5, 15, 30, 60)            # the paper's ranges (its Table 3); 5 the primary
PRE_START = 870                      # 07:30 CT: the pre-open, when the 08:30 ET (07:30 CT) releases land
FLAT_ENTRY = FLAT - 2                # 15:08 CT, slot 1328: the last bar a position is held to, and none opened after
HORIZONS = (965, 995, 1055)          # 09:05, 09:35, 10:35 CT: 30, 60 and 120 minutes after the 5-minute range
STEPS = (30, 60, 120)                # the drift horizons, minutes after each range closes
NONE = -1
MISSING = -999999                    # a signed field with no value (a gap or a move can be -1 tick)


def _bars(xs, a, b):
    return [xs[j] for j in range(a + 1, b + 1) if xs[j] is not None]


def window_stats(o, h, l, c, v, s, n):
    """(first open, high, low, last close, volume) of the bars ending in (s, s + n]; None without one."""
    js = [j for j in range(s + 1, s + n + 1) if o[j] is not None]
    if not js:
        return None
    return (o[js[0]], max(h[j] for j in js), min(l[j] for j in js), c[js[-1]],
            sum((v[j] or 0) for j in js))


def direction(first_open, last_close):
    """+1 a bullish range (closed above its open), -1 bearish, 0 a doji (no trade)."""
    return 1 if last_close > first_open else (-1 if last_close < first_open else 0)


def last_close_by(c, t):
    """The last close at or before slot t, or None."""
    for j in range(min(t, len(c) - 1), 0, -1):
        if c[j] is not None:
            return c[j]
    return None


def trigger(o, h, l, level, d, start, end):
    """(slot, fill before slippage) of the first bar in (start, end] reaching `level` in direction d, or None. A bar
    opening beyond the level fills at its open."""
    for j in range(start + 1, end + 1):
        if o[j] is None:
            continue
        if d > 0 and h[j] >= level:
            return j, max(level, o[j])
        if d < 0 and l[j] <= level:
            return j, min(level, o[j])
    return None


def walk(o, h, l, c, jf, fill, d, stop, levels, end, at_open=False):
    """From the fill bar `jf` to `end`: (stop slot or NONE, overshoot past the stop (price, 0 unless a bar opened
    through it), [first slot each favourable `levels` distance is traded through before the stop, or NONE]). `at_open`:
    the fill was at the fill bar's open, so the whole bar follows it."""
    stop_px = fill - d * stop
    first = [NONE] * len(levels)
    if not at_open and c[jf] is not None and ((c[jf] <= stop_px) if d > 0 else (c[jf] >= stop_px)):
        return jf, 0.0, first                                    # the fill bar closed beyond the stop
    for j in range(jf if at_open else jf + 1, end + 1):
        if o[j] is None:
            continue
        if j != jf and ((o[j] <= stop_px) if d > 0 else (o[j] >= stop_px)):
            return j, (stop_px - o[j]) if d > 0 else (o[j] - stop_px), first
        if ((l[j] <= stop_px) if d > 0 else (h[j] >= stop_px)):
            return j, 0.0, first                                 # touched: the stop's, before any target on the bar
        fav = (h[j] - fill) if d > 0 else (fill - l[j])
        for k, x in enumerate(levels):
            if first[k] == NONE and fav > x + 1e-12:
                first[k] = j
    return NONE, 0.0, first


def true_range(h, l, last, prev_close):
    """The day's true range: the session's high less its low, widened to the previous close; None without a bar."""
    hs = _bars(h, 0, last)
    ls = _bars(l, 0, last)
    if not hs or not ls:
        return None
    hi, lo = max(hs), min(ls)
    if prev_close is not None:
        hi, lo = max(hi, prev_close), min(lo, prev_close)
    return hi - lo


def or_block(o, h, l, c, v, n, P, or_vol, stop, end, t):
    """One range's part of the day's record: the range of the first `n` minutes, its direction, size and relative
    volume, the signed drift 30, 60 and 120 minutes after it closes and at 15:08, and its trade."""
    empty = [0, 0, NONE, 0, 0, 0, 0, NONE, 0, NONE, 0, 0, 0, 0] + [NONE] * len(P["rr"])
    rng = window_stats(o, h, l, c, v, OR_START, n)
    if rng is None or OR_START + n >= end:
        return empty
    first_open, hi, lo, close_n, vol = rng
    d = direction(first_open, close_n)
    rv = int(round(100 * vol / or_vol)) if or_vol else NONE
    drift = []
    for hz in tuple(OR_START + n + m for m in STEPS) + (end,):
        x = last_close_by(c, min(hz, end))
        drift.append(t(d * (x - close_n)) if (x is not None and d) else 0)
    block = [d, t(hi - lo), rv] + drift
    trig = trigger(o, h, l, hi if d > 0 else lo, d, OR_START + n, end - 1) if d else None
    if not trig:
        return block + [NONE, 0, NONE, 0, 0, 0, 0] + [NONE] * len(P["rr"])
    jf, px = trig
    fill = px + d * P["slip"]
    at_open = px == o[jf]
    js, over, first = walk(o, h, l, c, jf, fill, d, stop, [R * stop for R in P["rr"]], end, at_open)
    x = last_close_by(c, end)
    close_off = t(d * (x - fill)) if x is not None else 0
    against = t((fill - l[jf]) if d > 0 else (h[jf] - fill))     # the fill bar's excursions, for the strict reading
    favour = t((h[jf] - fill) if d > 0 else (fill - l[jf]))
    return block + [jf, t(d * (fill - (hi if d > 0 else lo))), js, int(round(over / P["tick"] * 10)), close_off,
                    against, favour] + first


def day_record(o, h, l, c, v, last, P, hist):
    """One day's record, as integers in the micro's ticks (overshoot in tenths), or None without the 5-minute range or
    the histories: the shared fields (`SHARED_FIELDS`) then one block per range of `OR_MINS` (`BLOCK_FIELDS`, then one
    first-touch slot per R of P['rr']). P 'tick', 'slip' (price), 'stop_atr' (0.10), 'rr'; hist 'atr' (the previous 14
    true ranges' mean, price), 'or_vol' ({minutes: the previous 14 days' mean volume of that range}), 'pre_vol', and
    'prev_close' (the previous session's last close on this contract, or None)."""
    if last is None or last < OR_START + OR_MIN + 1 or not hist.get("atr"):
        return None
    rng = window_stats(o, h, l, c, v, OR_START, OR_MIN)
    if rng is None:
        return None
    tick = P["tick"]
    t = lambda x: int(round(x / tick))                                       # noqa: E731
    first_open = rng[0]
    pre = window_stats(o, h, l, c, v, PRE_START, 5)
    pre_rv = int(round(100 * pre[4] / hist["pre_vol"])) if (pre and hist.get("pre_vol")) else NONE
    gap = t(first_open - hist["prev_close"]) if hist.get("prev_close") is not None else MISSING
    pre_move = t(first_open - pre[0]) if pre else MISSING       # 07:30 open to 08:30 open: the pre-open hour
    stop = max(1, int(round(P["stop_atr"] * hist["atr"] / tick))) * tick
    end = min(last, FLAT_ENTRY)
    rec = [t(hist["atr"]), gap, pre_move, pre_rv, t(stop)]
    or_vol = hist.get("or_vol") or {}
    for n in OR_MINS:
        rec += or_block(o, h, l, c, v, n, P, or_vol.get(n), stop, end, t)
    return rec


def encode_day(td, rec):
    """'yyyymmdd,v1,v2,...' for one day's record."""
    return "%04d%02d%02d," % td + ",".join(str(int(x)) for x in rec)


#: The record after the date: the shared fields, then per range of OR_MINS the block's fields and one first-touch
#: slot per R of `P['rr']`.
SHARED_FIELDS = ("atr_ticks", "gap_ticks", "pre_move_ticks", "pre_rv100", "stop_ticks")
BLOCK_FIELDS = ("dir", "or_ticks", "rv100", "drift_30", "drift_60", "drift_120", "drift_flat", "fill_slot",
                "fill_beyond_ticks", "stop_slot", "overshoot_tenths", "close_ticks", "fill_bar_against_ticks",
                "fill_bar_favour_ticks")

__all__ = ["OR_START", "OR_MIN", "OR_MINS", "PRE_START", "FLAT_ENTRY", "HORIZONS", "STEPS", "NONE", "MISSING",
           "window_stats", "direction", "last_close_by", "trigger", "walk", "true_range", "or_block", "day_record",
           "encode_day", "SHARED_FIELDS", "BLOCK_FIELDS"]
