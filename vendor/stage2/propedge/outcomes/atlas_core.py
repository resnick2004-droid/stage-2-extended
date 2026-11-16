"""The signal atlas's patterns (R5, D-460): simple mechanical OHLC events, found by a script, never by a person.

A kit embeds this source verbatim beside `collect_core` and `t23_core` (no imports; a missing minute is None), and the
local screen imports the same module (`propedge.research.atlas_screen_local`), so a day's events and walks are the same
code on QuantConnect's bars and on the operator's Databento bars.

**The clock** is collect_core's: index j is a one-minute bar's END time in minutes after 17:00 CT of the evening the
trading day starts (1 .. 1330, the bar ending 15:10 CT the last). An event at slot t is known when the bar ending at t
closes; its trade enters at the open of a later bar (`collect_core.c_entry`, on time or late).

**The patterns** (`P['patterns']`, each a dict with `kind` and its parameters; ids are their positions):

* ``brk``  -- k-minute bar breakout: the first one-minute close above the previous completed k-minute bar's high (long)
  or below its low (short), each side at most once per reference bar. k = 15 is the operator's example (D-452).
* ``inside`` -- inside-bar break: the previous completed k-minute bar lies inside the one before it; the first close
  beyond the inside bar's high or low, each side once per inside bar.
* ``nbar`` -- n-bar break: the first close above the highest high (below the lowest low) of the last n completed
  k-minute bars, each side once per reference window.
* ``orb``  -- opening-range break: the range of the m minutes after a session opens at `open_ct`; the first close
  above it and the first below it, once each a day.
* ``pdhl`` -- prior day's high/low break: the first close above the previous trading day's regular-session high
  (08:30-15:10 CT) or below its low, once each a day (the caller hands the previous day's range in `P['prior']`).
* ``engulf`` -- engulfing k-minute bar: a completed bar whose body covers the previous bar's body and closes the other
  way; the event at its close, in its direction.
* ``clock`` -- the fixed decision slots of T24's capture (R149-R151), both sides: the null family and the identity.

Events are kept from slot `P['first_slot']` to `P['last_slot']` (the last decision, 14:00 CT by default: a 40 to
60-point bracket needs the afternoon to resolve, D-212). The k-minute bars are aligned to the clock: bar b covers the
minutes ending (k*b, k*b + k], its slot k*b + k.
"""


def a_bars(o, h, l, c, k, upto):
    """The k-minute bars completed by slot `upto`: [(slot, open, high, low, close)], a bar with no minute left out."""
    out = []
    b = 0
    while (b + 1) * k <= upto:
        bo = bh = bl = bc = None
        for j in range(b * k + 1, (b + 1) * k + 1):
            if j >= len(o) or o[j] is None:
                continue
            if bo is None:
                bo, bh, bl = o[j], h[j], l[j]
            else:
                bh, bl = max(bh, h[j]), min(bl, l[j])
            bc = c[j]
        if bo is not None:
            out.append(((b + 1) * k, bo, bh, bl, bc))
        b += 1
    return out


def _first_cross(c, j_from, j_to, above, below):
    """The first minute in [j_from, j_to] whose close is above `above` (long) and the first below `below` (short)."""
    up = dn = None
    for j in range(j_from, j_to + 1):
        if j >= len(c) or c[j] is None:
            continue
        if up is None and above is not None and c[j] > above:
            up = j
        if dn is None and below is not None and c[j] < below:
            dn = j
        if up is not None and dn is not None:
            break
    return up, dn


def a_events(o, h, l, c, P):
    """Every event of the day: [(pattern id, slot, side)], sorted by slot then pattern then side (+1 before -1)."""
    first, last = P["first_slot"], P["last_slot"]
    n = len(o) - 1
    ev = []
    for pid, pat in enumerate(P["patterns"]):
        kind = pat["kind"]
        if kind in ("brk", "inside", "nbar", "engulf"):
            k = pat["k"]
            bars = a_bars(o, h, l, c, k, n)
            for i, (s, bo, bh, bl, bc) in enumerate(bars):
                j0, j1 = s + 1, min(s + k, n)
                if kind == "brk":
                    up, dn = _first_cross(c, j0, j1, bh, bl)
                elif kind == "inside":
                    if i == 0:
                        continue
                    ph, pl = bars[i - 1][2], bars[i - 1][3]
                    if not (bh <= ph and bl >= pl):
                        continue
                    up, dn = _first_cross(c, j0, j1, bh, bl)
                elif kind == "nbar":
                    m = pat["n"]
                    if i + 1 < m:
                        continue
                    win = bars[i + 1 - m:i + 1]
                    up, dn = _first_cross(c, j0, j1, max(x[2] for x in win), min(x[3] for x in win))
                else:                                                      # engulf: the event is the bar's own close
                    if i == 0:
                        continue
                    po, pc = bars[i - 1][1], bars[i - 1][4]
                    if bc > bo and pc < po and bo <= pc and bc >= po:
                        up, dn = s, None
                    elif bc < bo and pc > po and bo >= pc and bc <= po:
                        up, dn = None, s
                    else:
                        up = dn = None
                for j, d in ((up, 1), (dn, -1)):
                    if j is not None and first <= j <= last:
                        ev.append((pid, j, d))
        elif kind == "orb":
            t0 = pat["open_slot"]
            m = pat["m"]
            hi = lo = None
            for j in range(t0 + 1, t0 + m + 1):
                if j < len(o) and o[j] is not None:
                    hi = h[j] if hi is None else max(hi, h[j])
                    lo = l[j] if lo is None else min(lo, l[j])
            if hi is None:
                continue
            up, dn = _first_cross(c, t0 + m + 1, min(last, n), hi, lo)
            for j, d in ((up, 1), (dn, -1)):
                if j is not None and first <= j <= last:
                    ev.append((pid, j, d))
        elif kind == "pdhl":
            prior = P.get("prior")
            if not prior:
                continue
            up, dn = _first_cross(c, max(first, 1), min(last, n), prior[0], prior[1])
            for j, d in ((up, 1), (dn, -1)):
                if j is not None:
                    ev.append((pid, j, d))
        elif kind == "clock":
            for t in pat["slots"]:
                if first <= t <= last and t < len(o):
                    ev.append((pid, t, 1))
                    ev.append((pid, t, -1))
    ev.sort(key=lambda x: (x[1], x[0], -x[2]))
    return ev


def a_rth_range(o, h, l, open_slot, flat):
    """The day's regular-session high and low (minutes ending after `open_slot` up to `flat`), or None."""
    hi = lo = None
    for j in range(open_slot + 1, min(flat, len(o) - 1) + 1):
        if o[j] is not None:
            hi = h[j] if hi is None else max(hi, h[j])
            lo = l[j] if lo is None else min(lo, l[j])
    return None if hi is None else (hi, lo)


def a_event_records(ev):
    """One record per event: 'E' pattern id, slot, side (+/-)."""
    return ["E%d,%d,%s" % (p, t, "+" if d > 0 else "-") for p, t, d in ev]


__all__ = ["a_bars", "a_events", "a_rth_range", "a_event_records"]
