"""The session-setup screen SS1 (config/session_setups.yaml; T15 item 8, D-245) in plain Python for the repository and
the kit.

The QuantConnect kit embeds `propedge/outcomes/regime_core.py` and then this module verbatim -- the one import line
below removed -- and runs `run_day` on each full trading day's one-minute bars inside the cloud; only counts leave
(D-120). Missing bars are `None`. The clock, the walk and the trailing-range stops are the regime map's (D-238).

**Signals** are judged on completed bars: a rule fires on the bar whose close meets it, and the bracket enters at the
open of the next bar, one micro tick adverse (`walk_all` with the signal's slot as the decision). Per window and rule,
only the window's first signal trades. A window is its start slot and the minutes after it in which a signal may come.

* `orb_N`: the window's first N minutes set a range (bars ending in (start, start + N]); the first later bar closing
  above it goes long, below it short.
* `fade_N`: the same range; after a bar closes outside it, the first later bar closing back inside it trades back
  toward the range (short after an upside break, long after a downside one).
* `prior_break`: the prior range -- the trading day's bars before the window (17:00 to its start), or the previous full
  session for a window starting at 17:00 -- the first bar closing above it goes long, below it short.
* `prior_reject`: the first bar that trades above the prior range's high and closes back inside it goes short; one that
  trades below its low and closes back inside it goes long (a bar doing both is the short).
* `momo_N`: at N minutes after the start, the move from the window's first open to the last close by then: up goes
  long, down goes short; none, no trade.
"""
from propedge.outcomes.regime_core import FLAT, last_slot, outcome, walk_all

RULES = ("orb_5", "orb_15", "orb_30", "fade_5", "fade_15", "fade_30", "prior_break", "prior_reject", "momo_5",
         "momo_15", "momo_30")


def session_hilo(h, l, last):
    """(highest high, lowest low) of bars 1 to `last`; None without a bar."""
    hs = [x for x in h[1:last + 1] if x is not None]
    ls = [x for x in l[1:last + 1] if x is not None]
    if not hs or not ls:
        return None
    return max(hs), min(ls)


def _range(h, l, a, b):
    """(high, low) of the bars ending in (a, b]; None without one."""
    hs = [h[j] for j in range(a + 1, b + 1) if h[j] is not None]
    ls = [l[j] for j in range(a + 1, b + 1) if l[j] is not None]
    if not hs or not ls:
        return None
    return max(hs), min(ls)


def signal(rule, o, h, l, c, s, e, prev):
    """(slot, direction) of `rule`'s first signal in the window starting at slot `s` with signals up to slot `e`, or
    None. `prev` is the previous full session's (high, low), for a window starting at 17:00."""
    kind, _, n = rule.partition("_")
    if kind in ("orb", "fade"):
        n = int(n)
        rng = _range(h, l, s, s + n)
        if rng is None:
            return None
        hi, lo = rng
        broke = 0
        for j in range(s + n + 1, e + 1):
            if c[j] is None:
                continue
            if kind == "orb":
                if c[j] > hi:
                    return j, 1
                if c[j] < lo:
                    return j, -1
            elif broke == 0:
                broke = 1 if c[j] > hi else (-1 if c[j] < lo else 0)
            elif lo <= c[j] <= hi:
                return j, -broke
        return None
    if kind == "prior":
        pr = prev if s == 0 else _range(h, l, 0, s)
        if pr is None:
            return None
        hi, lo = pr
        for j in range(s + 1, e + 1):
            if c[j] is None:
                continue
            if n == "break":
                if c[j] > hi:
                    return j, 1
                if c[j] < lo:
                    return j, -1
            else:                                             # traded beyond it and closed back inside it
                if h[j] > hi and lo <= c[j] < hi:
                    return j, -1
                if l[j] < lo and lo < c[j] <= hi:
                    return j, 1
        return None
    if kind == "momo":
        n = int(n)
        if s + n > e:
            return None
        first = next((j for j in range(s + 1, s + n + 1) if o[j] is not None), None)
        lastc = next((j for j in range(s + n, s, -1) if c[j] is not None), None)
        if first is None or lastc is None or lastc < first:
            return None
        move = c[lastc] - o[first]
        if move > 0:
            return s + n, 1
        if move < 0:
            return s + n, -1
        return None
    raise ValueError("unknown rule " + repr(rule))


def run_day(o, h, l, c, P, stops, prev):
    """Every signal of the day and its bracket at each stop: [(wi, ri, di, si, walk result)], di 0 long and 1 short.
    P: 'windows' [(start slot, span minutes)], 'rules', 'slip' (one micro tick, price), 'rr' (ascending)."""
    last = last_slot(o)
    if last is None or not stops:
        return []
    rows = []
    for wi, (s, span) in enumerate(P["windows"]):
        e = min(s + span, last - 1)
        if e <= s:
            continue
        for ri, rule in enumerate(P["rules"]):
            sig = signal(rule, o, h, l, c, s, e, prev)
            if sig is None:
                continue
            t, d = sig
            res = walk_all(o, h, l, t, d, stops, P["slip"], last, P["rr"])
            if res is None:
                continue
            for si, r in enumerate(res):
                rows.append((wi, ri, 0 if d > 0 else 1, si, r))
    return rows


def add_trades(acc, year, rows, stops, rr, tick, q):
    """Add a day's rows into acc[(year, wi, ri, di, si)] = [n, gapped, overshoot (tenths of a tick) summed, its
    maximum, stop (ticks) summed, 1e6 / stop (ticks) summed, entry quotes, entry spread (ticks x 100) summed, then per
    R: target, stop, minutes to resolution summed]. `q` the day's quoted spreads (price) per slot."""
    for wi, ri, di, si, res in rows:
        a = acc.get((year, wi, ri, di, si))
        if a is None:
            a = acc[(year, wi, ri, di, si)] = [0] * (8 + 3 * len(rr))
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
        qs = q[res[0]] if res[0] < len(q) else None
        if qs is not None:
            a[6] += 1
            a[7] += int(round(qs / tick * 100))
        for k, R in enumerate(rr):
            kind, minutes = outcome(res, R)
            if kind == "t":
                a[8 + 3 * k] += 1
            elif kind == "s":
                a[9 + 3 * k] += 1
            if minutes is not None:
                a[10 + 3 * k] += minutes


def encode_trades(acc):
    """'y,wi,ri,di,si,n,gapped,overshoot,max,stops,inverse,quotes,spread,t,s,m...' cells; sorted."""
    return [",".join(str(x) for x in (y, wi, ri, di, si, *a)) for (y, wi, ri, di, si), a in sorted(acc.items())]


__all__ = ["RULES", "FLAT", "session_hilo", "signal", "run_day", "add_trades", "encode_trades"]
