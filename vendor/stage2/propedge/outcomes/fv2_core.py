"""FV2's data-capture records (D-279, D-282, D-283), in plain Python for the repository and the kit.

No hypothesis and no selection: the six runs re-walk ORB3's days (R102-R104, each window in two) and record, per
session, what JJ Simon's own rules need (`docs/candidates/fv2/JJ_SIMON_PRACTICE.md`) -- the session's fair value, every
trigger his rules allow, each traded by hand at the operator's latencies, and the unconditional entries D-277's drift
benchmark needs:

* **Sessions** (`SESSIONS`, slots after 17:00 CT): the evening reopen (6 PM ET; fair value its first bar's open), the
  Asian open (his 8 PM ET, held at 19:00 CT year-round -- a fixed clock: in US standard time Tokyo opens an hour
  earlier; fair value the evening's), New York AM (fair value the body of the 08:29-08:30 CT bar) and New York PM (fair
  value the AM's) -- each with its signal window from its open. The evening's first bar has no previous bar (the daily
  halt), so its triggers start at its second bar.
* **Structure**: a swing high (low) is a bar whose high (low) is beyond both neighbours', confirmed when the next bar
  closes; the latest confirmed swing formed at most `SWING_LOOKBACK` minutes before the open.
* **Triggers** at a bar's close, in a direction: a break of structure (a close beyond the latest confirmed swing that
  way after a close not beyond it -- so a swing re-crossed can trigger again) and a displacement candle (its body that
  way, larger than the previous bar's body, closing beyond the previous bar's wick) -- recorded as bits.
* **Phases**: in the first `CONT_MIN` minutes a trigger in the opening candle's direction (continuation); after them a
  trigger toward fair value while the close is beyond it (reversion), with its distance to fair value's near edge.
* **Entries**: at each of `LATS` minutes after the signal bar's close, a market order filled at the next bar's open,
  walked on the session's stop -- `STOP_ATR` x the 14-day ATR, doubled when the session's opening candle's body (not
  its range) exceeds it -- with its first bars reaching the stop and trading through 1R, 1.5R and fair value's near
  edge; for the first latency also its spread, 15:08 close and 15:07-15:10 worst; the reported latencies keep only
  their entry and each bracket's outcome code.
* **The unconditional entries**: per session at `BENCH` slots -- the first at the session's first minute, so a
  continuation has one before it -- a long and a short at the next bar's open, each bracket's outcome
  (`outcome_codes`) at 1R, 1.5R and fair value, read strictly.

Up to `MAX_SIGNALS` triggers per session are recorded, in time order, with the count beyond it. Offsets from the
entry's bar, -1 for never by 15:08; prices in ticks, signed with the trade.
"""
from propedge.outcomes.orb3_core import passages
from propedge.outcomes.orb5_core import MISSING5, _spread, worst_in
from propedge.outcomes.orb_core import FLAT_ENTRY, NONE, OR_MIN, OR_START, last_close_by, window_stats

MISSING_FV = MISSING5
FLATTEN_BARS = (FLAT_ENTRY, FLAT_ENTRY + 1, FLAT_ENTRY + 2)
STOP_ATR = 25.0 / 381.25             # his 25 points over NQ's median 14-day ATR of July 2024 to June 2025 (D-283),
                                      # recomputed from results/manual_R104_orb3_NQ_2025.csv by tests/test_fv2_kit.py
CONT_MIN, SWING_LOOKBACK, MAX_SIGNALS = 5, 30, 32
ROOM_MIN = 0.8                        # his "80 % of my trade" before fair value, at the smallest target (1R)
LATS = (2, 0, 5)                      # the verdict's latency (D-282) first, then L = 0 and D-266's 5 (reported)
TARGET_RR = (1.0, 1.5)
#: (name, open slot, signal window in minutes, fair value: 'open' its first bar's open, 'body' the body of the bar
#: ending at the open, or another session's)
SESSIONS = (("eve", 0, 90, "open"), ("asia", 120, 90, "eve"), ("am", 930, 90, "body"), ("pm", 1200, 60, "am"))
BENCH = {"eve": (1, 10, 30, 60), "asia": (121, 130, 150, 180), "am": (931, 940, 950, 965, 995),
         "pm": (1201, 1210, 1230)}
STOP_FIRST, TARGET_FIRST, OPEN, NO_BRACKET = "0", "1", "2", "9"


def fair_value(o, c, s, rule, done):
    """The session's fair-value zone (low, high) or None."""
    if rule == "open":
        j = next((j for j in range(s + 1, s + 6) if o[j] is not None), None)
        return None if j is None else (o[j], o[j])
    if rule == "body":
        return None if o[s] is None or c[s] is None else (min(o[s], c[s]), max(o[s], c[s]))
    return done.get(rule)


def swing_marks(h, l, n):
    """Per bar, +1 a swing high, -1 a swing low, 2 both, 0 neither (the bars on both sides present)."""
    out = [0] * n
    for k in range(1, n - 1):
        if h[k] is None or h[k - 1] is None or h[k + 1] is None:
            continue
        hi, lo = h[k] > h[k - 1] and h[k] > h[k + 1], l[k] < l[k - 1] and l[k] < l[k + 1]
        out[k] = 2 if hi and lo else (1 if hi else (-1 if lo else 0))
    return out


def triggers(o, h, l, c, j, d, swing):
    """The trigger bits at bar j's close in direction d: 1 a break of structure past `swing` (the latest confirmed
    swing that way, or None), 2 a displacement candle."""
    p = j - 1
    if o[j] is None or o[p] is None:
        return 0
    bits = 0
    if swing is not None and d * c[j] > d * swing and d * c[p] <= d * swing:
        bits |= 1
    body = c[j] - o[j]
    if d * body > 0 and abs(body) > abs(c[p] - o[p]) and d * c[j] > d * (h[p] if d > 0 else l[p]):
        bits |= 2
    return bits


def walk(o, h, l, je, e, d, stop, dfe, end, tick):
    """From an entry at bar je's open: the offsets of the first bars reaching the stop and trading through 1R, 1.5R and
    fair value's near edge (`dfe` ticks ahead; none if not ahead)."""
    fav = [R * stop * tick for R in TARGET_RR] + ([dfe * tick] if dfe > 0 else [])
    a, f = passages(o, h, l, je, e, d, [stop * tick], fav, end, True)
    off = lambda s: s - je if s != NONE else NONE                              # noqa: E731
    return [off(a[0])] + [off(x) for x in f[:len(TARGET_RR)]] + [off(f[-1]) if dfe > 0 else NONE]


def entry(o, h, l, c, q, j, d, L, zone, stop, end, tick, t, full):
    """The trade of a signal at bar j entered L minutes after its close: `full` -- [bar offset, entry less the signal's
    close, spread, ticks to fair value, stop and target offsets, 15:08 close, worst] -- or, for the reported latencies,
    [entry less the signal's close, `outcome_codes` as an integer after a leading 1] (an open trade is valued from the
    full entry's close and worst, shifted by the two entries' difference)."""
    je = next((x for x in range(j + L + 1, end) if o[x] is not None), None)
    if je is None:
        return [NONE, 0, NONE, 0, NONE, NONE, NONE, NONE, 0, MISSING_FV] if full else [0, int("1" + NO_BRACKET * 3)]
    e = o[je]
    near = zone[0] if d > 0 else zone[1]
    dfe = t(d * (near - e))
    if not full:
        return [t(d * (e - c[j])), int("1" + outcome_codes(o, h, l, je, e, d, stop, dfe, end, tick))]
    w = walk(o, h, l, je, e, d, stop, dfe, end, tick)
    x = last_close_by(c, end)
    wo = worst_in(h, l, d, e, FLATTEN_BARS)
    return [je - j, t(d * (e - c[j])), _spread(q, je, tick), dfe] + w + [
        t(d * (x - e)) if x is not None else 0, t(wo) if wo is not None else MISSING_FV]


def outcome_codes(o, h, l, j1, e, d, stop, dfe, end, tick):
    """An entry at bar j1's open: its outcome per target of 1R, 1.5R and fair value, read strictly -- 1 the target
    traded through on an earlier bar than the stop is reached, 0 the stop, 2 neither by 15:08, 9 no bracket."""
    w = walk(o, h, l, j1, e, d, stop, dfe, end, tick)
    out = ""
    for k, g in enumerate(w[1:]):
        if k == len(TARGET_RR) and dfe <= 0:
            out += NO_BRACKET
            continue
        out += (TARGET_FIRST if g != NONE and (w[0] == NONE or g < w[0]) else
                (STOP_FIRST if w[0] != NONE else OPEN))
    return out


def bench(o, h, l, c, slots, zone, stop, end, tick, t):
    """Per slot: [bar, 15:08 close in ticks (long's sense), the long's and short's worst, ticks to fair value for the
    long and the short, their outcome codes written as integers after a leading 1]."""
    rec = []
    for s in slots:
        j1 = next((j for j in range(s + 1, end) if o[j] is not None), None) if zone is not None else None
        if j1 is None:
            rec += [NONE, 0, MISSING_FV, MISSING_FV, 0, 0, int("1" + NO_BRACKET * 3), int("1" + NO_BRACKET * 3)]
            continue
        e = o[j1]
        x = last_close_by(c, end)
        rec += [j1, t(x - e) if x is not None else 0]
        for d in (1, -1):
            w = worst_in(h, l, d, e, FLATTEN_BARS)
            rec.append(t(w) if w is not None else MISSING_FV)
        dfes = [t(d * ((zone[0] if d > 0 else zone[1]) - e)) for d in (1, -1)]
        rec += dfes
        for d, dfe in zip((1, -1), dfes):
            rec.append(int("1" + outcome_codes(o, h, l, j1, e, d, stop, dfe, end, tick)))
    return rec


def session(o, h, l, c, q, s, window, zone, base, marks, end, tick, t, slots):
    """One session's part: [present, opening direction, opening body in ticks, the stop in ticks, signals recorded,
    signals beyond the cap], then per signal [slot, phase (0 continuation, 1 reversion), direction, trigger bits, ticks
    to fair value] with its entries at `LATS`, then `bench`."""
    first = s + 1
    if zone is None or first >= end or o[first] is None:
        return [0, 0, 0, 0, 0, 0] + bench(o, h, l, c, slots, None, 1, end, tick, t)
    d0 = 1 if c[first] > o[first] else (-1 if c[first] < o[first] else 0)
    body = t(abs(c[first] - o[first]))
    stop = base * 2 if body > base else base
    sig, extra = [], 0
    sh = sl = None                                  # the latest confirmed swing high and low
    for k in range(max(1, s - SWING_LOOKBACK), first - 1):
        if marks[k] in (1, 2):
            sh = h[k]
        if marks[k] in (-1, 2):
            sl = l[k]
    for j in range(first, min(s + window, end - 1) + 1):
        k = j - 2                                   # a swing at j - 2 is confirmed by j - 1's close
        if k >= max(1, s - SWING_LOOKBACK):
            if marks[k] in (1, 2):
                sh = h[k]
            if marks[k] in (-1, 2):
                sl = l[k]
        if o[j] is None:
            continue
        if j <= s + CONT_MIN:
            d, phase = d0, 0
        elif c[j] > zone[1]:
            d, phase = -1, 1
        elif c[j] < zone[0]:
            d, phase = 1, 1
        else:
            continue
        if not d:
            continue
        bits = triggers(o, h, l, c, j, d, sh if d > 0 else sl)
        if not bits:
            continue
        near = zone[0] if d > 0 else zone[1]
        room = t(d * (near - c[j]))
        if phase == 1 and room < ROOM_MIN * stop:       # no cell's room rule can take it (its smallest target, 1R)
            continue
        if len(sig) >= MAX_SIGNALS:
            extra += 1
            continue
        rec = [j, phase, d, bits, room]
        for i, L in enumerate(LATS):
            rec += entry(o, h, l, c, q, j, d, L, zone, stop, end, tick, t, i == 0)
        sig.append(rec)
    out = [1, d0, body, stop, len(sig), extra]
    for r in sig:
        out += r
    return out + bench(o, h, l, c, slots, zone, stop, end, tick, t)


def day_record_fv2(o, h, l, c, v, q, last, P, hist):
    """One day's record: [ATR in ticks, the base stop in ticks], then per session of `SESSIONS` its `session` part;
    None on the days ORB3 writes none (the join, D-265)."""
    if last is None or last < OR_START + OR_MIN + 1 or not hist.get("atr"):
        return None
    if window_stats(o, h, l, c, v, OR_START, OR_MIN) is None:
        return None
    tick = P["tick"]
    t = lambda x: int(round(x / tick))                                         # noqa: E731
    base = max(1, int(round(STOP_ATR * hist["atr"] / tick)))
    end = min(last, FLAT_ENTRY)
    marks = swing_marks(h, l, len(o))
    rec = [t(hist["atr"]), base]
    done = {}
    for name, s, window, rule in SESSIONS:
        zone = fair_value(o, c, s, rule, done)
        done[name] = zone
        rec += session(o, h, l, c, q, s, window, zone, base, marks, end, tick, t, BENCH[name])
    return rec


#: a signal's fields: SIGNAL_FIELDS, then per latency of LATS its entry (the first FULL_FIELDS, the others SHORT_FIELDS)
SESSION_FIELDS = ("present", "open_dir", "open_body_ticks", "stop_ticks", "signals", "signals_beyond_cap")
SIGNAL_FIELDS = ("slot", "phase", "dir", "trigger_bits", "fv_ticks")
FULL_FIELDS = ("bar", "entry_ticks", "spread_tenths", "fv_from_entry_ticks", "a", "f1", "f15", "ffv", "close_ticks",
               "worst_ticks")
SHORT_FIELDS = ("entry_ticks", "codes")
BENCH_FIELDS = ("bench_slot", "bench_close_ticks", "bench_worst_long_ticks", "bench_worst_short_ticks",
                "bench_fv_long_ticks", "bench_fv_short_ticks", "bench_codes_long", "bench_codes_short")

__all__ = ["MISSING_FV", "STOP_ATR", "CONT_MIN", "ROOM_MIN", "SWING_LOOKBACK", "MAX_SIGNALS", "LATS", "TARGET_RR", "SESSIONS",
           "BENCH", "fair_value", "swing_marks", "triggers", "walk", "entry", "outcome_codes", "bench", "session",
           "day_record_fv2", "SESSION_FIELDS", "SIGNAL_FIELDS", "FULL_FIELDS", "SHORT_FIELDS", "BENCH_FIELDS"]
