"""FV3's data-capture records (T17 item 3; the card `docs/candidates/cards/drafts/FV3.md`), in plain Python for the
repository and the kit.

No hypothesis and no selection: the runs re-walk ORB3's NQ days and record, per session, what JJ Simon's own rules
need and what the mechanics report and the later rounds read -- the fair price and its re-anchoring, every trigger his
rules allow with its attributes (the component ledger), each traded by hand at the operator's latencies, with the
profiles that settle any bracket exactly, and the unconditional entries of D-277's drift benchmark:

* **Sessions** (`SESSIONS`, slots after 17:00 CT): the 6 PM ET reopen, the Asian open (19:00 CT, his 8 PM ET), New
  York 9:30 ET (08:30 CT) and the PM open (13:00 CT), each with its signal window.
* **Fair price**: the 6 PM's is its first bar's open -- or, when that open gaps from the previous 15:10 close by more
  than the base stop, the previous close (the bias is to fill the gap; no continuation against the fill); Asia's is its
  open -- or the 6 PM's once price has traded to it within `ASIA_SWITCH_MIN` minutes of the Asian open; the AM's is the
  body of the bar ending at the open -- or, on a day in `NEWS_DAYS` (the BLS 08:30 ET releases), the open of the 8:30
  ET candle; the PM's is the AM's. Once a session, a break of structure away from fair followed within
  `REANCHOR_BARS` bars by a displacement away moves fair to the midpoint of the last `CONSOL_BARS` bars' range.
* **Structure**: a swing is a bar whose high (low) is beyond both neighbours', confirmed when the next bar closes; its
  strength is the most bars (to `SWING_MAX`) on each side it is beyond.
* **Triggers** at a bar's close, in a direction: a break of structure (bit 1) and a displacement candle (bit 2), each
  with its attributes -- the broken swing's strength and age and the break's depth; the displacement's body ratio and
  its close beyond the previous wick.
* **Phases**: in the first `CONT_MIN` minutes a break of structure in the opening candle's direction (continuation,
  none against a gap's fill); after them a trigger toward fair while the close is beyond it, with at least
  `ROOM_MIN_FRAC` x the base stop of room to fair's near edge (his 15 points at a 25-point base).
* **Entries** at each of `LATS` minutes after the signal bar's close, filled at the next bar's open. The first
  latency's entry carries its spread, its distance to fair's near edge, its **favourable and adverse profiles** -- the
  running maximum excursion from the entry, each as (bar offset, ticks) steps, from which any stop and target of the
  ladder settles exactly and the true adverse excursion before any exit is read -- its 15:08 close, its 15:07-15:10
  worst, and the breakeven fields (the next session's open bar, the open there against the entry, and the first bar
  from it that touched the entry). The other latencies keep their entry and the base stop's outcome codes.
* **The unconditional entries**: per session at `BENCH` slots, a long and a short at the next bar's open, each with
  its distance to fair and its two profiles.

Up to `MAX_SIGNALS` triggers per session are recorded, in time order, with the count beyond it. Offsets from the
entry's bar, -1 for never by 15:08; prices in ticks, signed with the trade.
"""
from propedge.outcomes.orb5_core import MISSING5, _spread, worst_in
from propedge.outcomes.orb_core import FLAT_ENTRY, NONE, OR_MIN, OR_START, last_close_by, window_stats

MISSING_FV = MISSING5
FLATTEN_BARS = (FLAT_ENTRY, FLAT_ENTRY + 1, FLAT_ENTRY + 2)
STOP_ATR = 25.0 / 381.25             # his 25 points over NQ's median 14-day ATR of July 2024 to June 2025 (D-283)
CONT_MIN, SWING_LOOKBACK, MAX_SIGNALS = 5, 30, 32
SWING_MAX = 3                         # swing strength recorded to three bars each side
ROOM_MIN_FRAC = 0.6                   # his 15 points at a 25-point base stop
ASIA_SWITCH_MIN = 30                  # "Asia opened and went straight to six"
REANCHOR_BARS, CONSOL_BARS = 5, 10    # a break of structure away, a displacement away within 5 bars: fair = the last 10 bars' midpoint
LATS = (2, 0, 5)                      # the verdict's latency (D-282) first, then L = 0 and D-266's 5 (reported)
TARGET_RR = (1.0, 1.5)                # the other latencies' outcome codes, at the base stop
NEWS_SLOT = 871                       # the bar ending 07:31 CT opens at 07:30 CT = 8:30 ET: the release candle
#: (name, open slot, signal window in minutes, fair value: 'open' its first bar's open, 'body' the body of the bar
#: ending at the open, or another session's)
SESSIONS = (("eve", 0, 90, "open"), ("asia", 120, 90, "open"), ("am", 930, 90, "body"), ("pm", 1200, 60, "am"))
BENCH = {"eve": (1, 10, 30), "asia": (121, 130, 150), "am": (931, 940, 965), "pm": (1201, 1210, 1230)}
STOP_FIRST, TARGET_FIRST, OPEN, NO_BRACKET = "0", "1", "2", "9"
#: the re-anchor states a signal carries
AT_OPEN, GAP_FILL, ASIA_TO_EVE, CONSOLIDATION, NEWS_ANCHOR = 0, 1, 2, 3, 4
#: the BLS 08:30 ET release days (data/release_days_0830_2009_2025.csv) as a bitmask per year over the day of the year,
#: bit 0 the first of January; written by scripts/make_fv3_news.py, checked against the file by the tests
NEWS = {
    2009: 0x3103000310304010c0040006205000234408000c404000c40c000070c080018410001881800700182000e100,
    2010: 0x1881400182182000e100000e00300011a204001c004000e006000610608080c008001c00c003800c10086080,
    2011: 0x3800a000c20c100c40800003801800381102000e100000310300001a304001a004000e006000e00608003840,
    2012: 0x1c280000c2070002304000038500000c50900046080000382100008c182000e100000e140000d00340061020,
    2013: 0x6608001c608060c000000008c180000f0028001182000118280000e00680023040000386000c0820c000c408,
    2014: 0x4305000a206080408408000c40c00046081804180080008c140000704280011820001183000610304000e200,
    2015: 0x1182800112304000c2040004305000434408002c004001060c002030a0800488100400c1810108182000e100,
    2016: 0x3811000380182008c100000e00300011a204001c200000e044000230508001c008000c40c002840c10086080,
    2017: 0xe280000e0068002304000218208000470810046080000380900000e182000e10000031c0000310340021820,
    2018: 0x7180000610380001c200001c3000006304800038400001c108000070c1000388000038a00007001c0000e10,
    2019: 0x7880000702180000d100000e1800007102800118200000e3000002306800038400001c600003810c000c408,
    2020: 0x2344000230608001c008000460c00007881000188080000e1800007181000118200001c3000218304000e200,
    2021: 0x1891000083182000e100000310300001e204000e0040006106000038608000c408000450c001810c10007080,
    2022: 0xc508000c20c10007080000380180000f102000e100000310300001c304000e0040006106000610608003840,
    2023: 0xe280000e0068000384000038208000460c10007080000380180000e182000e1000007101000d00340021820,
    2024: 0xf100000e083000218200001c300000e0070002304000038600001c00d0000708000068c00006801c0010c10,
    2025: 0xa0810118000001000000000430c000068418003800800086180000d082800118200010c300001c304000e200,
}
CUM_DAYS = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def news_day(y, m, d):
    """Whether (y, m, d) is a scheduled 08:30 ET release day."""
    leap = 1 if (m > 2 and y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 0
    return (NEWS.get(y, 0) >> (CUM_DAYS[m - 1] + d - 1 + leap)) & 1 == 1


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


def swing_strength(h, l, k, d):
    """How many bars each side (to `SWING_MAX`) the swing at bar k is beyond: a high for d > 0, a low for d < 0."""
    n = 0
    while n < SWING_MAX:
        i = n + 1
        if k - i < 0 or k + i >= len(h) or h[k - i] is None or h[k + i] is None:
            break
        if d > 0 and not (h[k] > h[k - i] and h[k] > h[k + i]):
            break
        if d < 0 and not (l[k] < l[k - i] and l[k] < l[k + i]):
            break
        n = i
    return n


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


def attributes(o, h, l, c, j, d, swing, swing_bar, bits, t):
    """[swing strength, swing age, break depth, displacement body ratio in hundredths, close beyond the previous
    wick] for a trigger at bar j in direction d; 0 where the trigger of that kind did not fire."""
    p = j - 1
    out = [0, 0, 0, 0, 0]
    if bits & 1 and swing is not None and swing_bar is not None:
        out[0] = swing_strength(h, l, swing_bar, d)
        out[1] = j - swing_bar
        out[2] = t(d * (c[j] - swing))
    if bits & 2:
        body, prev = abs(c[j] - o[j]), abs(c[p] - o[p])
        out[3] = min(999, int(round(100.0 * body / prev))) if prev > 0 else 999
        out[4] = t(d * (c[j] - (h[p] if d > 0 else l[p])))
    return out


def profiles(o, h, l, je, e, d, end, t):
    """From an entry at bar je's open: the favourable and adverse running maxima as step lists [n, off, ticks, ...],
    a step recorded whenever the maximum rises; the fill bar counts; ticks from the entry, never below zero."""
    fav, adv = [], []
    mf = ma = 0
    for j in range(je, end + 1):
        if o[j] is None:
            continue
        f = t((h[j] - e) if d > 0 else (e - l[j]))
        a = t((e - l[j]) if d > 0 else (h[j] - e))
        if f > mf:
            mf = f
            fav += [j - je, f]
        if a > ma:
            ma = a
            adv += [j - je, a]
    return [len(fav) // 2] + fav + [len(adv) // 2] + adv


def settle(fav, adv, stop, target):
    """From two profiles: (exit offset, 'stop' | 'target' | 'open', the adverse excursion before the exit). A target
    must be traded through (beyond it), a stop reached, as `orb3_core.passages` reads them; the stop wins a bar on
    which both happen; an open trade's excursion is the whole adverse profile's."""
    js = next((fav[i] for i in range(0, len(fav), 2) if fav[i + 1] > target), NONE) if target is not None else NONE
    ja = next((adv[i] for i in range(0, len(adv), 2) if adv[i + 1] >= stop), NONE)
    if ja != NONE and (js == NONE or ja <= js):
        return ja, "stop", stop
    if js != NONE:
        mae = max([adv[i + 1] for i in range(0, len(adv), 2) if adv[i] <= js] or [0])
        return js, "target", mae
    return NONE, "open", max([adv[i + 1] for i in range(0, len(adv), 2)] or [0])


def outcome_codes(fav, adv, stop, dfe):
    """The base stop's codes from the profiles: per target of 1R, 1.5R and fair value -- 1 the target traded through
    on an earlier bar than the stop is reached, 0 the stop, 2 neither by 15:08, 9 no bracket."""
    out = ""
    for tgt in [R * stop for R in TARGET_RR] + [dfe if dfe > 0 else None]:
        if tgt is None:
            out += NO_BRACKET
            continue
        _, kind, _ = settle(fav, adv, stop, tgt)
        out += TARGET_FIRST if kind == "target" else (STOP_FIRST if kind == "stop" else OPEN)
    return out


def _profile_lists(rec):
    """Split a profiles record [n, off, v, ..., m, off, v, ...] into (fav, adv) flat lists."""
    n = rec[0]
    fav = rec[1:1 + 2 * n]
    m = rec[1 + 2 * n]
    adv = rec[2 + 2 * n:2 + 2 * n + 2 * m]
    return fav, adv


def next_open(je, end, o):
    """The next session's open bar after je: (slot of its first bar, or None)."""
    for _, s, _, _ in SESSIONS:
        if s > je:
            j = next((x for x in range(s + 1, min(s + 6, end + 1)) if o[x] is not None), None)
            return j
    return None


def entry(o, h, l, c, q, j, d, L, zone, stop, end, tick, t, full):
    """The trade of a signal at bar j entered L minutes after its close: `full` -- [bar offset, entry less the
    signal's close, spread, ticks to fair, the profiles, 15:08 close, worst, breakeven open offset, the open there
    against the entry, the touch offset] -- or, for the reported latencies, [entry less the signal's close, the base
    stop's `outcome_codes` as an integer after a leading 1]."""
    je = next((x for x in range(j + L + 1, end) if o[x] is not None), None)
    if je is None:
        return ([NONE, 0, NONE, 0, 0, 0, 0, MISSING_FV, NONE, 0, NONE] if full else [0, int("1" + NO_BRACKET * 3)])
    e = o[je]
    near = zone[0] if d > 0 else zone[1]
    dfe = t(d * (near - e))
    prof = profiles(o, h, l, je, e, d, end, t)
    if not full:
        fav, adv = _profile_lists(prof)
        return [t(d * (e - c[j])), int("1" + outcome_codes(fav, adv, stop, dfe))]
    x = last_close_by(c, end)
    wo = worst_in(h, l, d, e, FLATTEN_BARS)
    jn = next_open(je, end, o)
    be = [NONE, 0, NONE]
    if jn is not None:
        be[0] = jn - je
        be[1] = t(d * (o[jn] - e))
        touch = next((x for x in range(jn, end + 1) if o[x] is not None and ((l[x] <= e) if d > 0 else (h[x] >= e))), None)
        be[2] = touch - je if touch is not None else NONE
    return [je - j, t(d * (e - c[j])), _spread(q, je, tick), dfe] + prof + [
        t(d * (x - e)) if x is not None else 0, t(wo) if wo is not None else MISSING_FV] + be


def bench(o, h, l, c, slots, zone, end, tick, t):
    """Per slot: [bar, 15:08 close in ticks (long's sense)], then per side [worst, ticks to fair, the profiles]."""
    rec = []
    for s in slots:
        j1 = next((j for j in range(s + 1, end) if o[j] is not None), None) if zone is not None else None
        if j1 is None:
            rec += [NONE, 0] + [MISSING_FV, 0, 0, 0] * 2
            continue
        e = o[j1]
        x = last_close_by(c, end)
        rec += [j1, t(x - e) if x is not None else 0]
        for d in (1, -1):
            w = worst_in(h, l, d, e, FLATTEN_BARS)
            rec.append(t(w) if w is not None else MISSING_FV)
            rec.append(t(d * ((zone[0] if d > 0 else zone[1]) - e)))
            rec += profiles(o, h, l, j1, e, d, end, t)
    return rec


def session(o, h, l, c, q, name, s, window, zone, state, base, marks, end, tick, t, slots, gap_dir, eve_zone):
    """One session's part: [present, opening direction, opening body in ticks, the base stop, re-anchor state at the
    open, gap in ticks, signals recorded, signals beyond the cap, re-anchors made], then per signal [slot, phase,
    direction, trigger bits, room, re-anchor state, the five attributes] with its entries at `LATS`, then `bench`."""
    first = s + 1
    if zone is None or first >= end or o[first] is None:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0] + bench(o, h, l, c, slots, None, end, tick, t)
    d0 = 1 if c[first] > o[first] else (-1 if c[first] < o[first] else 0)
    body = t(abs(c[first] - o[first]))
    gap = t(gap_dir[1]) if gap_dir is not None else 0
    state0 = state
    sig, extra, reanchors = [], 0, 0
    sh = sl = None                                  # the latest confirmed swing high and low, and their bars
    shb = slb = None
    for k in range(max(1, s - SWING_LOOKBACK), first - 1):
        if marks[k] in (1, 2):
            sh, shb = h[k], k
        if marks[k] in (-1, 2):
            sl, slb = l[k], k
    away_bos_bar = None                             # a break of structure away from fair, awaiting a displacement
    for j in range(first, min(s + window, end - 1) + 1):
        k = j - 2                                   # a swing at j - 2 is confirmed by j - 1's close
        if k >= max(1, s - SWING_LOOKBACK):
            if marks[k] in (1, 2):
                sh, shb = h[k], k
            if marks[k] in (-1, 2):
                sl, slb = l[k], k
        if o[j] is None:
            continue
        # Asia: once price trades to the 6 PM fair price in the first minutes, that is fair
        if name == "asia" and state == AT_OPEN and eve_zone is not None and j <= s + ASIA_SWITCH_MIN \
                and l[j] <= eve_zone[1] and h[j] >= eve_zone[0]:
            zone, state = eve_zone, ASIA_TO_EVE
            reanchors += 1
        # the consolidation re-anchor, once: a break of structure away from fair, then a displacement away
        if j > s + CONT_MIN and state != CONSOLIDATION:
            mid = 0.5 * (zone[0] + zone[1])
            d_away = 1 if c[j] > mid else (-1 if c[j] < mid else 0)
            if d_away:
                bits_away = triggers(o, h, l, c, j, d_away, sh if d_away > 0 else sl)
                if bits_away & 1:
                    away_bos_bar = j
                if bits_away & 2 and away_bos_bar is not None and 0 < j - away_bos_bar <= REANCHOR_BARS:
                    bars = [x for x in range(max(first, j - CONSOL_BARS + 1), j + 1) if o[x] is not None]
                    m = 0.5 * (max(h[x] for x in bars) + min(l[x] for x in bars))
                    zone, state = (m, m), CONSOLIDATION
                    reanchors += 1
                    away_bos_bar = None
        if j <= s + CONT_MIN:
            d, phase = d0, 0
            if gap_dir is not None and d == gap_dir[0]:
                continue                            # no continuation against the gap's fill
        elif c[j] > zone[1]:
            d, phase = -1, 1
        elif c[j] < zone[0]:
            d, phase = 1, 1
        else:
            continue
        if not d:
            continue
        swing, swing_bar = (sh, shb) if d > 0 else (sl, slb)
        bits = triggers(o, h, l, c, j, d, swing)
        if phase == 0:
            bits &= 1                               # a continuation only on a break of structure
        if not bits:
            continue
        near = zone[0] if d > 0 else zone[1]
        room = t(d * (near - c[j])) if phase == 1 else NONE
        if phase == 1 and room < ROOM_MIN_FRAC * base:
            continue
        if len(sig) >= MAX_SIGNALS:
            extra += 1
            continue
        rec = [j, phase, d, bits, room, state] + attributes(o, h, l, c, j, d, swing, swing_bar, bits, t)
        for i, L in enumerate(LATS):
            rec += entry(o, h, l, c, q, j, d, L, zone, base, end, tick, t, i == 0)
        sig.append(rec)
    out = [1, d0, body, base, state0, gap, len(sig), extra, reanchors]
    for r in sig:
        out += r
    return out + bench(o, h, l, c, slots, zone, end, tick, t)


def day_record_fv3(o, h, l, c, v, q, last, P, hist, td):
    """One day's record: [ATR in ticks, the base stop in ticks, news day], then per session of `SESSIONS` its
    `session` part; None on the days ORB3 writes none (the join, D-265). `td` the trading day as (y, m, d)."""
    if last is None or last < OR_START + OR_MIN + 1 or not hist.get("atr"):
        return None
    if window_stats(o, h, l, c, v, OR_START, OR_MIN) is None:
        return None
    tick = P["tick"]
    t = lambda x: int(round(x / tick))                                         # noqa: E731
    base = max(1, int(round(STOP_ATR * hist["atr"] / tick)))
    end = min(last, FLAT_ENTRY)
    marks = swing_marks(h, l, len(o))
    news = news_day(td[0], td[1], td[2])
    rec = [t(hist["atr"]), base, 1 if news else 0]
    done, states = {}, {}
    prev = hist.get("prev_close")
    for name, s, window, rule in SESSIONS:
        zone = fair_value(o, c, s, rule, done)
        state, gap_dir = AT_OPEN, None
        if name == "eve" and zone is not None and prev is not None and abs(zone[0] - prev) > base * tick:
            gap_dir = (1 if zone[0] > prev else -1, zone[0] - prev)
            zone, state = (prev, prev), GAP_FILL
        elif name == "am" and news and o[NEWS_SLOT] is not None:
            zone, state = (o[NEWS_SLOT], o[NEWS_SLOT]), NEWS_ANCHOR
        elif rule not in ("open", "body"):
            state = states.get(rule, AT_OPEN)
        done[name] = zone
        states[name] = state
        rec += session(o, h, l, c, q, name, s, window, zone, state, base, marks, end, tick, t, BENCH[name], gap_dir,
                       done.get("eve"))
    return rec


#: a signal's fields: SIGNAL_FIELDS, then per latency of LATS its entry (the first FULL_HEAD, the profiles, FULL_TAIL;
#: the others SHORT_FIELDS)
SESSION_FIELDS = ("present", "open_dir", "open_body_ticks", "stop_ticks", "state_at_open", "gap_ticks", "signals",
                  "signals_beyond_cap", "reanchors")
SIGNAL_FIELDS = ("slot", "phase", "dir", "trigger_bits", "fv_ticks", "reanchor", "swing_bars", "swing_age",
                 "break_ticks", "disp_body_ratio", "disp_beyond_ticks")
FULL_HEAD = ("bar", "entry_ticks", "spread_tenths", "fv_from_entry_ticks")
FULL_TAIL = ("close_ticks", "worst_ticks", "be_open_off", "be_favour_ticks", "be_touch_off")
SHORT_FIELDS = ("entry_ticks", "codes")
BENCH_HEAD = ("bench_slot", "bench_close_ticks")
BENCH_SIDE = ("bench_worst_ticks", "bench_fv_ticks")

__all__ = ["MISSING_FV", "STOP_ATR", "CONT_MIN", "SWING_LOOKBACK", "MAX_SIGNALS", "SWING_MAX", "ROOM_MIN_FRAC",
           "ASIA_SWITCH_MIN", "REANCHOR_BARS", "CONSOL_BARS", "LATS", "TARGET_RR", "NEWS_SLOT", "SESSIONS", "BENCH",
           "AT_OPEN", "GAP_FILL", "ASIA_TO_EVE", "CONSOLIDATION", "NEWS_ANCHOR", "NEWS", "CUM_DAYS", "news_day",
           "fair_value", "swing_marks",
           "swing_strength", "triggers", "attributes", "profiles", "settle", "outcome_codes", "next_open", "entry",
           "bench", "session", "day_record_fv3", "SESSION_FIELDS", "SIGNAL_FIELDS", "FULL_HEAD", "FULL_TAIL",
           "SHORT_FIELDS", "BENCH_HEAD", "BENCH_SIDE"]
