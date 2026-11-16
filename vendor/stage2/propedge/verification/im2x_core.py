"""IM2's noise band and signals, the second implementation (D-200; docs/verification/im2_second_implementation.md).

Pure Python, standard library only. Embedded verbatim in the IM2X kit (im2x_kit.py) and imported by the tests.
A bar is (end_minute, open, high, low, close, volume), end_minute the bar's END time in minutes after midnight US
Central. The rules are the brief's section 3.1 and 3.2 (P-04 section 3, "Market rules" and "Entry").
"""
import bisect
import math


def _imx_session_bars(bars, params):
    """The session's bars, one per end minute, in time order: open < end minute <= close (brief 3.1).

    The caller passes only such bars; anything outside the session is dropped, and a repeated minute keeps its last
    bar, so neither can count twice in coverage or VWAP.
    """
    lo = params["open"]
    hi = params["close"]
    by_minute = {}
    for b in bars:
        m = int(b[0])
        if lo < m <= hi:
            by_minute[m] = b
    return [by_minute[m] for m in sorted(by_minute)]


def _imx_decision_minutes(params):
    """Every :00 and :30 mark from the first at least `decision_margin` after the open to the last at least
    `decision_margin` before the close (brief 3.2): ES 09:00-14:30, CL and NG 08:30-13:00, 6E 08:00-13:30."""
    step = int(params["decision_every"])
    margin = int(params["decision_margin"])
    first = params["open"] + margin
    first = ((first + step - 1) // step) * step
    last = params["close"] - margin
    return list(range(first, last + 1, step))


def _imx_profile(bars, minutes):
    """A past session's move profile |C(T) / O - 1| at each minute T (brief 3.2).

    O is the session's open (the open of its earliest bar); C(T) the close of its bar ending at T or, when that is
    missing, of its latest earlier bar (carried forward). None where the session has no bar at or before T.
    """
    if not bars:
        return [None] * len(minutes)
    o = bars[0][1]
    ends = [b[0] for b in bars]
    out = []
    for t in minutes:
        i = bisect.bisect_right(ends, t) - 1
        if i < 0 or not o:
            out.append(None)
        else:
            out.append(abs(bars[i][4] / o - 1.0))
    return out


def evaluate_session(bars, prior_close, past, params):
    """One session's integrity fields and signals (brief section 2; the rules of 3.1 and 3.2).

    bars: this session's bars; prior_close: a float or None; past: the lookback store's sessions, oldest first (the
    last params["lookback"] are used); params: open, close, lookback, multiplier, decision_every, decision_margin,
    min_coverage.

    Integrity (3.1): open is the open of the earliest bar; cov the bars present over close - open; st 1 when a bar
    ends at the close; full 1 when settled with cov at least min_coverage. No decision is evaluated when
    prior_close is None, the session has no bar, or past holds fewer than lookback sessions.

    Decisions (3.2): at each decision minute T, a missing bar ending at T counts in mis; a present bar with sigma or
    VWAP undefined counts in nbd; otherwise the signal is long (+1) if the bar's close is above both the upper band
    and VWAP, short (-1) if below both the lower band and VWAP. Each signal is (T, side, close, ub, lb, vwap).
    """
    sb = _imx_session_bars(bars, params)
    length = params["close"] - params["open"]
    n = len(sb)
    cov = (n / float(length)) if length > 0 else 0.0
    st = 1 if (n and sb[-1][0] == params["close"]) else 0
    full = 1 if (st and cov >= params["min_coverage"]) else 0
    out = {"open": (float(sb[0][1]) if n else None), "st": st, "full": full, "cov": cov,
           "sig": 0, "mis": 0, "nbd": 0, "signals": []}
    lookback = int(params["lookback"])
    if prior_close is None or not n or lookback < 1 or len(past) < lookback:
        return out

    minutes = _imx_decision_minutes(params)
    stored = [_imx_session_bars(p, params) for p in past[len(past) - lookback:]]
    profiles = [_imx_profile(p, minutes) for p in stored]

    o = float(sb[0][1])
    pc = float(prior_close)
    up_anchor = max(o, pc)
    lo_anchor = min(o, pc)
    mult = params["multiplier"]

    num = 0.0   # sum of (high + low + close) / 3 x volume through T
    den = 0.0   # sum of volume through T
    i = 0
    mis = 0
    nbd = 0
    signals = []
    for j, t in enumerate(minutes):
        while i < n and sb[i][0] <= t:
            _, _, h, l, c, v = sb[i]
            if v > 0:                       # a zero-volume bar adds nothing (3.2)
                num += (h + l + c) / 3.0 * v
                den += v
            i += 1
        if i == 0 or sb[i - 1][0] != t:     # no bar ends at T: the decision is not taken (3.2)
            mis += 1
            continue
        col = [p[j] for p in profiles]
        if not col or any(x is None for x in col) or den <= 0:
            nbd += 1                        # sigma or VWAP undefined (3.2)
            continue
        sigma = math.fsum(col) / len(col)
        ub = up_anchor * (1.0 + mult * sigma)
        lb = lo_anchor * (1.0 - mult * sigma)
        vwap = num / den
        close = float(sb[i - 1][4])
        if close > ub and close > vwap:
            signals.append((t, 1, close, ub, lb, vwap))
        elif close < lb and close < vwap:
            signals.append((t, -1, close, ub, lb, vwap))
    out["sig"] = len(signals)
    out["mis"] = mis
    out["nbd"] = nbd
    out["signals"] = signals
    return out
