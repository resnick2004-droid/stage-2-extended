"""The whole-day regime map (config/regime_map.yaml; T15, D-237, D-238) in plain Python for the repository and the kit.

The QuantConnect kit embeds this module's source verbatim and runs `run_day` on each full trading day's one-minute bars
inside the cloud, adding each day into the accumulators below; only the counts leave (D-120). No imports; missing bars
are `None`.

**The clock** is the resolution map's (D-214): a slot is a bar's END time in minutes after 17:00 of the evening the
trading day starts -- the bar ending 17:01 is slot 1, midnight is slot 420, the bar ending 15:10 CT is `FLAT` = 1330.
A decision at slot t enters at the open of the first bar after t, one micro tick adverse.

**The walk** is the resolution map's, at actual prices: per entry, direction and stop, the bracket at R resolves at its
target when a bar trades through `R x stop` in its favour before any bar touches the stop (a bar touching both is the
stop's; a bar opening through the stop is the stop's), at its stop when the stop comes first, and is **open** when
neither happens by the day's last bar at or before 15:10. Added here, the stop's **overshoot**: when a bar after the
entry bar opens through the stop, the distance from the stop to that open -- a stop order fills no better than the
open. A stop touched inside a bar is taken at the stop (its slippage is the cost model's, D-95), so the overshoot is the
gap's alone. The walk follows each stop until its stop or its largest target, so a stop event is the stop reached
before the largest target: their count is the largest R's stop count.

**Stops** are fixed distances in points, and multiples of the trailing range -- the mean of the previous full
sessions' ranges (highest high less lowest low) -- rounded to the micro's tick, at least one tick.
"""
FLAT = 22 * 60 + 10                       # 15:10 CT, minutes after 17:00
OPEN_MIN, MIDNIGHT = 17 * 60, 7 * 60
WINDOW_MIN = 30                           # the volume and range windows: 30 minutes, w = (slot - 1) // 30


def slot_of(hour, minute):
    """A bar END time (CT) on the trading-day clock: minutes after 17:00 of the evening the day starts."""
    m = hour * 60 + minute
    return m - OPEN_MIN if m > OPEN_MIN else m + MIDNIGHT


def decision_slots(every, last, open_slot, step, span):
    """Every `every` minutes from slot 0 to `last`, and every `step` minutes from `open_slot` to `open_slot + span`;
    sorted, each once, none after `last`."""
    s = set(range(0, last + 1, every)) | set(range(open_slot, open_slot + span + 1, step))
    return sorted(x for x in s if 0 <= x <= last)


def walk_all(o, h, l, t, d, stops, slip, last, rr):
    """Every stop's bracket entered after decision slot t in direction d (+1 long, -1 short), in one pass over the
    bars: [(entry slot, stop slot or None, overshoot (price; 0 unless a bar opened through the stop),
    {R: target slot or None})] per stop; None when no bar follows t by `last`. `rr` ascending."""
    j0 = None
    for j in range(t + 1, last + 1):
        if o[j] is not None:
            j0 = j
            break
    if j0 is None:
        return None
    entry = o[j0] + d * slip
    stop_px = [entry - d * s for s in stops]
    out = [[j0, None, 0.0, {R: None for R in rr}] for _ in stops]
    live = list(range(len(stops)))
    for j in range(j0, last + 1):
        if not live:
            break
        if o[j] is None:
            continue
        adv = (entry - l[j]) if d > 0 else (h[j] - entry)
        fav = (h[j] - entry) if d > 0 else (entry - l[j])
        still = []
        for i in live:
            s = stops[i]
            if j != j0 and ((o[j] <= stop_px[i]) if d > 0 else (o[j] >= stop_px[i])):
                out[i][1] = j                                     # opened through the stop: the gap is the overshoot
                out[i][2] = (stop_px[i] - o[j]) if d > 0 else (o[j] - stop_px[i])
                continue
            if adv >= s - 1e-12:
                out[i][1] = j                                     # touched: the stop first, taken at the stop
                continue
            hit = out[i][3]
            for R in rr:
                if hit[R] is None and fav > R * s + 1e-12:
                    hit[R] = j
            if hit[rr[-1]] is None:
                still.append(i)
        live = still
    return [tuple(x) for x in out]


def outcome(res, R):
    """('t', minutes) target first, ('s', minutes) stop first, or ('o', None) open at the day's last bar."""
    j0, js, _, hit = res
    if hit[R] is not None:
        return "t", hit[R] - j0
    if js is not None:
        return "s", js - j0
    return "o", None


def last_slot(o):
    """The day's last bar at or before 15:10 CT (an early close ends sooner), or None without a bar."""
    for j in range(min(FLAT, len(o) - 1), -1, -1):
        if o[j] is not None:
            return j
    return None


def session_range(h, l, last):
    """The day's highest high less its lowest low, bars 1 to `last`; None without a bar."""
    hs = [x for x in h[1:last + 1] if x is not None]
    ls = [x for x in l[1:last + 1] if x is not None]
    if not hs or not ls:
        return None
    return max(hs) - min(ls)


def range_stops(avg_range, multiples, tick):
    """Stops at `multiples` of the trailing range, rounded to `tick`, at least one tick; [] without a range."""
    if not avg_range or avg_range <= 0:
        return []
    return [max(1, int(round(k * avg_range / tick))) * tick for k in multiples]


def run_day(o, h, l, P, stops):
    """Every decision of the day: [(ti, si, d, walk result)]. P: 'times' (decision slots), 'slip' (one micro tick,
    price), 'rr' (ascending); `stops` this day's stop distances (price): the fixed ones, then the range ones."""
    last = last_slot(o)
    if last is None:
        return []
    rows = []
    for ti, t in enumerate(P["times"]):
        if t >= last:
            continue
        for d in (1, -1):
            res = walk_all(o, h, l, t, d, stops, P["slip"], last, P["rr"])
            if res is None:
                continue
            for si, r in enumerate(res):
                rows.append((ti, si, d, r))
    return rows


def entry_spreads(o, q, P):
    """{ti: the entry bar's bid-ask spread (price) at its open} for every decision with an entry bar and a quote."""
    last = last_slot(o)
    out = {}
    if last is None:
        return out
    for ti, t in enumerate(P["times"]):
        for j in range(t + 1, last + 1):
            if o[j] is not None:
                if q[j] is not None:
                    out[ti] = q[j]
                break
    return out


def window_stats(h, l, v, last):
    """{w: (bars, volume, range)} for each 30-minute window of the day with a bar, bars 1 to `last`."""
    acc = {}
    for j in range(1, last + 1):
        if h[j] is None or l[j] is None:
            continue
        w = (j - 1) // WINDOW_MIN
        a = acc.get(w)
        vol = v[j] or 0
        if a is None:
            acc[w] = [1, vol, h[j], l[j]]
        else:
            a[0] += 1
            a[1] += vol
            if h[j] > a[2]:
                a[2] = h[j]
            if l[j] < a[3]:
                a[3] = l[j]
    return {w: (a[0], a[1], a[2] - a[3]) for w, a in acc.items()}


def add_day(acc, year, rows, stops, rr, tick):
    """Add a day's rows into acc[(year, ti, si)] = [n, gapped, overshoot (tenths of a tick) summed, its maximum,
    stop (ticks) summed, 1e6 / stop (ticks) summed, then per R: target, stop, minutes to resolution summed]."""
    for ti, si, d, res in rows:
        a = acc.get((year, ti, si))
        if a is None:
            a = acc[(year, ti, si)] = [0] * (6 + 3 * len(rr))
        st = int(round(stops[si] / tick))
        a[0] += 1
        a[4] += st
        a[5] += int(round(1e6 / st))
        if res[1] is not None and res[2] > 1e-12:
            g = int(round(res[2] / tick * 10))
            a[1] += 1
            a[2] += g
            if g > a[3]:
                a[3] = g
        for k, R in enumerate(rr):
            kind, minutes = outcome(res, R)
            if kind == "t":
                a[6 + 3 * k] += 1
            elif kind == "s":
                a[7 + 3 * k] += 1
            if minutes is not None:
                a[8 + 3 * k] += minutes


def add_spreads(acc, year, spreads, tick):
    """acc[(year, ti)] = [count, spread in ticks summed]."""
    for ti, s in spreads.items():
        a = acc.setdefault((year, ti), [0, 0.0])
        a[0] += 1
        a[1] += s / tick


def add_windows(acc, year, stats, tick):
    """acc[(year, w)] = [days, bars, volume, range (ticks) summed]."""
    for w, (bars, vol, rng) in stats.items():
        a = acc.setdefault((year, w), [0, 0, 0, 0])
        a[0] += 1
        a[1] += bars
        a[2] += int(round(vol))
        a[3] += int(round(rng / tick))


def add_session(acc, year, rng, vol, avg_range, tick):
    """acc[year] = [days, session range (ticks) summed, volume summed, days with a trailing range, it (ticks) summed]."""
    a = acc.setdefault(year, [0, 0, 0, 0, 0])
    a[0] += 1
    a[1] += int(round((rng or 0) / tick))
    a[2] += int(round(vol))
    if avg_range:
        a[3] += 1
        a[4] += int(round(avg_range / tick))


def encode_counts(acc):
    """'y,ti,si,n,gapped,overshoot,max,stops,inverse,t,s,m...' cells; sorted."""
    return [",".join(str(x) for x in (y, ti, si, *a)) for (y, ti, si), a in sorted(acc.items())]


def encode_spreads(acc):
    """'y,ti,count,ticks*100' cells; sorted."""
    return ["%d,%d,%d,%d" % (y, ti, a[0], int(round(a[1] * 100))) for (y, ti), a in sorted(acc.items())]


def encode_windows(acc):
    """'y,w,days,bars,volume,range' cells; sorted."""
    return [",".join(str(x) for x in (y, w, *a)) for (y, w), a in sorted(acc.items())]


def encode_sessions(acc):
    """'y,days,range,volume,range days,trailing range' cells; sorted."""
    return [",".join(str(x) for x in (y, *a)) for y, a in sorted(acc.items())]


__all__ = ["FLAT", "WINDOW_MIN", "slot_of", "decision_slots", "walk_all", "outcome", "last_slot", "session_range",
           "range_stops", "run_day", "entry_spreads", "window_stats", "add_day", "add_spreads", "add_windows",
           "add_session", "encode_counts", "encode_spreads", "encode_windows", "encode_sessions"]
