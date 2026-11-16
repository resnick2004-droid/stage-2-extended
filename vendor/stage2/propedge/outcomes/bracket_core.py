"""The bracket outcome map (config/bracket_map.yaml, D-149) in plain Python for the repository and the kit.

The QuantConnect kit embeds this module's source verbatim and runs `run_day` on each day's one-minute bars inside the
cloud; only the per-entry path summaries, a few per-day measurements and bucketed features leave (D-120). No imports
beyond `math`; missing bars are `None`.

Slots are bar END times counted in minutes from 08:00 CT (slot 0 ends at 08:00), as in FV1. The session anchor is the
OPEN of the bar starting 08:30 (slot 31); from 13:05 the afternoon anchor is the open of the bar starting 13:00
(slot 301). A decision is taken at the close of the bar ending at the decision time; the entry fills at the next
existing bar's open, one tick adverse.

Per entry, side and stop width the walk records three numbers, from which every target multiple follows:

* `mfe` -- the largest favourable excursion, in R, over the bars BEFORE the stop was touched (a bar touching the stop
  is the stop's: stop first when a bar touches both). A target of k R fills iff `mfe > k` (a resting limit needs a
  trade through it). Recorded floored to hundredths and capped at 5.05, so a recorded tie is not a fill.
* `hit` -- 0 the stop was never touched; 1 touched (exit at the stop); 2 a bar opened through it (exit at that open).
* `exit` -- the R at which the trade ends when no target fills first: -1 at a touched stop, the gap open's R, or the
  R at the 15:00 CT close. Before exit costs; the scorer applies them per exit kind (D-95).

So the outcome at target k is `+k` if `mfe > k`, else `exit`; the stop width fixes R's size in price.
"""
import math

#: Bucket edges for the signed distances, in units of D: < -0.5, -0.5..-0.2, -0.2..0, 0..0.2, 0.2..0.5, >= 0.5.
SIGNED_EDGES = (-0.5, -0.2, 0.0, 0.2, 0.5)
#: Bucket edges for today's range so far, in units of D: < 0.3, 0.3..0.6, 0.6..1, >= 1.
RANGE_EDGES = (0.3, 0.6, 1.0)
#: Previous close location: terciles of (close - low) / (high - low).
CLV_EDGES = (1.0 / 3.0, 2.0 / 3.0)
MFE_CAP = 5.05
ANCHOR_AM, ANCHOR_PM, PM_FROM = 31, 301, 305


def bucket(x, edges):
    """The index of the bucket x falls in (the number of edges at or below it); 9 when x is unknown."""
    if x is None:
        return 9
    return sum(1 for e in edges if x >= e)


def ffill_at(xs, j):
    """The last non-missing value at or before slot j, or None."""
    while j >= 0 and xs[j] is None:
        j -= 1
    return xs[j] if j >= 0 else None


def session_range_pct(o, h, l, last_slot):
    """(high - low) over the session, as a percent of the 08:30 open; None without the open or any bar."""
    ref = o[ANCHOR_AM]
    hs = [h[j] for j in range(ANCHOR_AM, last_slot + 1) if h[j] is not None]
    ls = [l[j] for j in range(ANCHOR_AM, last_slot + 1) if l[j] is not None]
    if not ref or not hs:
        return None
    return 100.0 * (max(hs) - min(ls)) / ref


def stop_ticks_for(D, ref, width, tick, floor_ticks):
    """The stop distance for a width (a fraction of D, a percent of price) at this day's anchor price, in ticks,
    never inside the cost floor."""
    return max(int(round(width * D / 100.0 * ref / tick)), int(floor_ticks))


def walk(o, h, l, c, t, d, stop_ticks, tick, entry_slip, last_slot):
    """One entry after the decision bar t in direction d (+1 long, -1 short): (mfe, hit, exit) in R, or None when no
    bar follows t before the time exit."""
    j0 = next((j for j in range(t + 1, last_slot + 1) if o[j] is not None), None)
    if j0 is None:
        return None
    entry = o[j0] + d * entry_slip * tick
    risk = stop_ticks * tick
    stop = entry - d * risk
    mfe = 0.0
    for j in range(j0, last_slot + 1):
        if o[j] is None:
            continue
        if j != j0 and ((o[j] <= stop) if d > 0 else (o[j] >= stop)):
            return mfe / risk, 2, d * (o[j] - entry) / risk          # opened through the stop
        adv = (entry - l[j]) if d > 0 else (h[j] - entry)
        if adv >= risk - 1e-12:
            return mfe / risk, 1, -1.0                                 # touched: the stop first
        fav = (h[j] - entry) if d > 0 else (entry - l[j])
        if fav > mfe:
            mfe = fav
    return mfe / risk, 0, d * (ffill_at(c, last_slot) - entry) / risk


def features(o, h, l, c, v, t, D):
    """The bucketed pre-entry features at decision bar t (config: features), all in units of D."""
    ref = o[ANCHOR_AM]
    if not ref or not D or c[t] is None:
        return None
    unit = D / 100.0 * ref
    anchor = o[ANCHOR_PM] if (t >= PM_FROM and o[ANCHOR_PM] is not None) else ref
    num = den = 0.0
    for j in range(ANCHOR_AM, t + 1):
        if o[j] is not None and v[j]:
            num += (h[j] + l[j] + c[j]) / 3.0 * v[j]
            den += v[j]
    vwap = num / den if den > 0 else None
    past = ffill_at(c, t - 30)
    hs = [h[j] for j in range(ANCHOR_AM, t + 1) if h[j] is not None]
    ls = [l[j] for j in range(ANCHOR_AM, t + 1) if l[j] is not None]
    return (bucket((c[t] - anchor) / unit, SIGNED_EDGES),
            bucket(None if vwap is None else (c[t] - vwap) / unit, SIGNED_EDGES),
            bucket(None if past is None else (c[t] - past) / unit, SIGNED_EDGES),
            bucket((max(hs) - min(ls)) / unit if hs else None, RANGE_EDGES))


def day_features(o, D, prev):
    """Per-day features: the gap against the previous settlement and the previous close location (None-safe).
    `prev` is {'close', 'high', 'low', 'same_contract'} or None."""
    ref = o[ANCHOR_AM]
    gap = clv = None
    if prev and ref and D:
        if prev.get("same_contract"):
            gap = (ref - prev["close"]) / (D / 100.0 * ref)
        if prev["high"] > prev["low"]:
            clv = (prev["close"] - prev["low"]) / (prev["high"] - prev["low"])
    return bucket(gap, SIGNED_EDGES), bucket(clv, CLV_EDGES)


def run_day(o, h, l, c, v, P, fills, D, prev):
    """Every decision of the day: {'sk': stop ticks per width, 'gap', 'clv', 'rows': [(t, feats, {(d, wi): (mfe, hit,
    exit)})]}. P: times (decision slots), widths, last_slot, floor_ticks. Prices as given (rescale first, D-106)."""
    ref = o[ANCHOR_AM]
    if not ref or not D:
        return None
    tick = fills["tick"]
    sk = [stop_ticks_for(D, ref, w, tick, P["floor_ticks"]) for w in P["widths"]]
    gap, clv = day_features(o, D, prev)
    rows = []
    for t in P["times"]:
        f = features(o, h, l, c, v, t, D)
        if f is None:
            continue
        out = {}
        for d in (1, -1):
            for wi, s in enumerate(sk):
                r = walk(o, h, l, c, t, d, s, tick, fills["entry"], P["last_slot"])
                if r is not None:
                    out[(d, wi)] = r
        if out:
            rows.append((t, f, out))
    return {"sk": sk, "gap": gap, "clv": clv, "rows": rows}


def encode(r):
    """(mfe, hit, exit) -> 'mfe:hit:exit' in hundredths; mfe floored and capped (a recorded tie is not a fill)."""
    mfe, hit, ex = r
    return (str(int(math.floor(min(mfe, MFE_CAP) * 100.0 + 1e-9))) + ":" + str(hit) + ":"
            + str(int(round(ex * 100.0))))


def scaled(o, h, l, c, ref, scale_to):
    """The day's bars rescaled so `ref` maps to `scale_to` (D-106); volume is not a price and is not rescaled."""
    f = 1.0 if (scale_to is None or not ref) else scale_to / ref
    return tuple([None if x is None else x * f for x in xs] for xs in (o, h, l, c))
