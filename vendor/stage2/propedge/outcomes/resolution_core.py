"""The resolution map (config/resolution_map.yaml; D-213 part 2, D-214) in plain Python for the repository and the kit.

The QuantConnect kit embeds this module's source verbatim and runs `run_day` on each trading day's one-minute bars
inside the cloud, adding each day into `add_day`'s counts; only the counts leave (D-120). No imports beyond `math`;
missing bars are `None`.

**The trading-day clock.** Topstep's day resumes at 17:00 CT and is flat by 15:10 CT (8284206). A slot is a bar's END
time in minutes after 17:00 of the evening the trading day starts: the bar ending 17:01 is slot 1, midnight is slot
420, and the bar ending 15:10 is slot `FLAT` = 1330. A decision at slot t enters at the open of the first bar after t,
one tick adverse.

**The walk.** Per entry, direction and stop distance, the bracket at R resolves at its target when a bar trades
through `R x stop` in its favour before any bar touches the stop (a bar touching both is the stop's; a bar opening
through the stop is the stop's), at its stop when the stop comes first, and is **open** when neither happens by the
day's last bar at or before 15:10 -- the flatten D-212 allows on at most 2 % of trades. The minutes to resolution are
counted from the entry bar.
"""
FLAT = 22 * 60 + 10                       # 15:10 CT, minutes after 17:00
OPEN_MIN, MIDNIGHT = 17 * 60, 7 * 60


def slot_of(hour, minute):
    """A bar END time (CT) on the trading-day clock: minutes after 17:00 of the evening the day starts."""
    m = hour * 60 + minute
    return m - OPEN_MIN if m > OPEN_MIN else m + MIDNIGHT


def walk(o, h, l, t, d, stop, slip, last, rr):
    """One bracket entered after decision slot t in direction d (+1 long, -1 short) with a stop `stop` away (price):
    (entry slot, stop slot or None, {R: target slot or None}); None when no bar follows t by `last`."""
    j0 = None
    for j in range(t + 1, last + 1):
        if o[j] is not None:
            j0 = j
            break
    if j0 is None:
        return None
    entry = o[j0] + d * slip
    stop_px = entry - d * stop
    hit = {R: None for R in rr}
    for j in range(j0, last + 1):
        if o[j] is None:
            continue
        if j != j0 and ((o[j] <= stop_px) if d > 0 else (o[j] >= stop_px)):
            return j0, j, hit                                     # opened through the stop
        adv = (entry - l[j]) if d > 0 else (h[j] - entry)
        if adv >= stop - 1e-12:
            return j0, j, hit                                     # touched: the stop first
        fav = (h[j] - entry) if d > 0 else (entry - l[j])
        for R in rr:
            if hit[R] is None and fav > R * stop + 1e-12:
                hit[R] = j
        if all(v is not None for v in hit.values()):
            return j0, None, hit                                  # every target first; a later stop is not theirs
    return j0, None, hit


def walk_all(o, h, l, t, d, stops, slip, last, rr):
    """`walk` for every stop at once, in one pass over the bars (the kit's speed): [walk(..., stop, ...) per stop],
    each (entry slot, stop slot or None, {R: target slot or None}); None when no bar follows t by `last`."""
    j0 = None
    for j in range(t + 1, last + 1):
        if o[j] is not None:
            j0 = j
            break
    if j0 is None:
        return None
    entry = o[j0] + d * slip
    stop_px = [entry - d * s for s in stops]
    out = [[j0, None, {R: None for R in rr}] for _ in stops]
    live = list(range(len(stops)))
    for j in range(j0, last + 1):
        if not live or o[j] is None:
            if not live:
                break
            continue
        adv = (entry - l[j]) if d > 0 else (h[j] - entry)
        fav = (h[j] - entry) if d > 0 else (entry - l[j])
        still = []
        for i in live:
            s = stops[i]
            if (j != j0 and ((o[j] <= stop_px[i]) if d > 0 else (o[j] >= stop_px[i]))) or adv >= s - 1e-12:
                out[i][1] = j                                     # opened through or touched: the stop first
                continue
            hit = out[i][2]
            for R in rr:
                if hit[R] is None and fav > R * s + 1e-12:
                    hit[R] = j
            if any(v is None for v in hit.values()):
                still.append(i)
        live = still
    return [tuple(x) for x in out]


def outcome(res, R):
    """('t', minutes) target first, ('s', minutes) stop first, or ('o', None) open at the day's last bar."""
    j0, js, hit = res
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


def run_day(o, h, l, P):
    """Every decision of the day: [(ti, si, d, {R: (kind, minutes)})]. P: 'times' (decision slots), 'stops' (price
    distances, in the bars' scale), 'slip' (one tick, price), 'rr'. Prices as given (rescale first, D-106)."""
    last = last_slot(o)
    if last is None:
        return []
    rows = []
    for ti, t in enumerate(P["times"]):
        if t >= last:
            continue
        for d in (1, -1):
            res = walk_all(o, h, l, t, d, P["stops"], P["slip"], last, P["rr"])
            if res is None:
                continue
            for si, r in enumerate(res):
                rows.append((ti, si, d, {R: outcome(r, R) for R in P["rr"]}))
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


def add_day(acc, year, rows):
    """Add a day's rows into acc[(year, ti, si, R)] = [n, target, stop, open, minutes to resolution summed]."""
    for ti, si, d, outs in rows:
        for R, (kind, minutes) in outs.items():
            a = acc.setdefault((year, ti, si, R), [0, 0, 0, 0, 0])
            a[0] += 1
            if kind == "t":
                a[1] += 1
            elif kind == "s":
                a[2] += 1
            else:
                a[3] += 1
            if minutes is not None:
                a[4] += minutes


def add_spreads(acc, year, spreads, tick):
    """acc[(year, ti)] = [count, spread in ticks summed]."""
    for ti, s in spreads.items():
        a = acc.setdefault((year, ti), [0, 0.0])
        a[0] += 1
        a[1] += s / tick


def scaled(o, h, l, ref, scale_to):
    """The day's bars rescaled so `ref` maps to `scale_to` (D-106)."""
    f = 1.0 if (scale_to is None or not ref) else scale_to / ref
    return tuple([None if x is None else x * f for x in xs] for xs in (o, h, l))


def encode_counts(acc, rr):
    """Counts as 'y,ti,si,r,n,t,s,o,m' cells, R written as its index in rr; sorted."""
    return ["%d,%d,%d,%d,%d,%d,%d,%d,%d" % (y, ti, si, rr.index(R), *a) for (y, ti, si, R), a in sorted(acc.items())]


def encode_spreads(acc):
    """Spreads as 'y,ti,count,ticks*100' cells; sorted."""
    return ["%d,%d,%d,%d" % (y, ti, a[0], int(round(a[1] * 100))) for (y, ti), a in sorted(acc.items())]


__all__ = ["FLAT", "slot_of", "walk", "walk_all", "outcome", "last_slot", "run_day", "entry_spreads", "add_day", "add_spreads",
           "scaled", "encode_counts", "encode_spreads"]
