"""The flip map (config/flip_map.yaml; D-343) in plain Python for the repository and the kit: a fast, time-boxed bracket.

The QuantConnect kit embeds this module's source verbatim and runs `run_day_flip` on each trading day's one-minute bars
inside the cloud, adding each day into `add_day_flip`'s counts; only the counts leave (D-120). No imports; missing bars
are `None`. Self-contained on purpose: the clock and the day's last bar are `propedge/outcomes/resolution_core`'s,
copied here so the embedded source needs nothing else.

**The trading-day clock** is the resolution map's: a slot is a bar's END time in minutes after 17:00 CT of the evening
the trading day starts; the bar ending 15:10 is `FLAT`. A decision at slot t enters at the open of the first bar after
t (on time: the hour start itself) or of the bar after that (`delay` 1: one minute late), one tick adverse.

**The walk.** One width w, 1:1: the target is w in favour, the stop w against. From the entry bar, at most `box` bars
are read (the bar `box` minutes after the entry bar is the last). The bracket is at its stop when a bar opens through
the stop or trades to it (a bar touching both is the stop's), at its target when a bar trades through it first, and
otherwise a SCRATCH: closed at the last bar read's close, one tick adverse, its P&L kept. Minutes are counted from the
entry bar (a resolution on the entry bar is 0). "Within five minutes" is a resolution by the end of the fifth bar from
the entry bar (minutes 0 to 4).
"""
FLAT = 22 * 60 + 10                       # 15:10 CT, minutes after 17:00
OPEN_MIN, MIDNIGHT = 17 * 60, 7 * 60
WITHIN = 5                                # bars from the entry bar counted as "within five minutes"


def slot_of(hour, minute):
    """A bar END time (CT) on the trading-day clock: minutes after 17:00 of the evening the day starts."""
    m = hour * 60 + minute
    return m - OPEN_MIN if m > OPEN_MIN else m + MIDNIGHT


def last_slot(o):
    """The day's last bar at or before 15:10 CT (an early close ends sooner), or None without a bar."""
    for j in range(min(FLAT, len(o) - 1), -1, -1):
        if o[j] is not None:
            return j
    return None


def walk_boxed(o, h, l, c, t, d, widths, slip, last, box, delay):
    """Every width's bracket entered after decision slot t in direction d (+1 long, -1 short), `delay` bars after the
    first bar following t, read for at most `box` bars: per width (entry slot, kind, minutes, scratch P&L in price)
    with kind 't' (target first), 's' (stop first) or 'x' (scratched at the last bar read); None when no entry bar."""
    j0, k = None, 0
    for j in range(t + 1, last + 1):
        if o[j] is not None:
            if k == delay:
                j0 = j
                break
            k += 1
    if j0 is None:
        return None
    entry = o[j0] + d * slip
    stop_px = [entry - d * w for w in widths]
    out = [[j0, None, None, 0.0] for _ in widths]
    live = list(range(len(widths)))
    end = min(last, j0 + box)
    read = j0
    for j in range(j0, end + 1):
        if o[j] is None:
            continue
        read = j
        if not live:
            break
        adv = (entry - l[j]) if d > 0 else (h[j] - entry)
        fav = (h[j] - entry) if d > 0 else (entry - l[j])
        still = []
        for i in live:
            w = widths[i]
            if (j != j0 and ((o[j] <= stop_px[i]) if d > 0 else (o[j] >= stop_px[i]))) or adv >= w - 1e-12:
                out[i][1], out[i][2] = "s", j - j0                # opened through or touched: the stop first
            elif fav > w + 1e-12:
                out[i][1], out[i][2] = "t", j - j0                # traded through the target first
            else:
                still.append(i)
        live = still
    for i in live:                                                # still open at the last bar read: a scratch
        px = c[read] - d * slip
        out[i][1], out[i][2], out[i][3] = "x", read - j0, d * (px - entry)
    return [tuple(x) for x in out]


def run_day_flip(o, h, l, c, P):
    """Every decision of the day: [(ti, wi, dl, d, kind, minutes, scratch P&L)]. P: 'times' (decision slots),
    'widths' (points), 'slip' (one tick, price), 'box' (bars), 'delays' (bars). Prices as given: actual."""
    last = last_slot(o)
    if last is None:
        return []
    rows = []
    for ti, t in enumerate(P["times"]):
        if t >= last:
            continue
        for dl in P["delays"]:
            for d in (1, -1):
                res = walk_boxed(o, h, l, c, t, d, P["widths"], P["slip"], last, P["box"], dl)
                if res is None:
                    continue
                for wi, (j0, kind, minutes, x) in enumerate(res):
                    rows.append((ti, wi, dl, d, kind, minutes, x))
    return rows


def entry_spreads(o, q, P):
    """{ti: the on-time entry bar's bid-ask spread (price) at its open} for every decision with a bar and a quote."""
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


def add_day_flip(acc, year, rows, tick):
    """Add a day's rows into acc[(year, ti, wi, dl)] = [n, target, stop, scratch, minutes to resolution summed,
    targets within five minutes, stops within five minutes, scratch P&L in ticks summed, its absolute value summed]."""
    for ti, wi, dl, d, kind, minutes, x in rows:
        a = acc.setdefault((year, ti, wi, dl), [0, 0, 0, 0, 0, 0, 0, 0, 0])
        a[0] += 1
        if kind == "t":
            a[1] += 1
            a[4] += minutes
            if minutes < WITHIN:
                a[5] += 1
        elif kind == "s":
            a[2] += 1
            a[4] += minutes
            if minutes < WITHIN:
                a[6] += 1
        else:
            a[3] += 1
            ticks = int(round(x / tick))
            a[7] += ticks
            a[8] += abs(ticks)


def add_spreads(acc, year, spreads, tick):
    """acc[(year, ti)] = [count, spread in ticks summed]."""
    for ti, s in spreads.items():
        a = acc.setdefault((year, ti), [0, 0.0])
        a[0] += 1
        a[1] += s / tick


def encode_flip(acc):
    """Counts as 'y,ti,wi,dl,n,t,s,x,m,t5,s5,xs,xa' cells; sorted."""
    return ["%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (y, ti, wi, dl, *a) for (y, ti, wi, dl), a in sorted(acc.items())]


def encode_spreads(acc):
    """Spreads as 'y,ti,count,ticks*100' cells; sorted."""
    return ["%d,%d,%d,%d" % (y, ti, a[0], int(round(a[1] * 100))) for (y, ti), a in sorted(acc.items())]


__all__ = ["FLAT", "WITHIN", "slot_of", "last_slot", "walk_boxed", "run_day_flip", "entry_spreads", "add_day_flip",
           "add_spreads", "encode_flip", "encode_spreads"]
