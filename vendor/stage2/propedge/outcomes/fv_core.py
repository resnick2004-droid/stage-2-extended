"""FV1, the fair-value two-phase model (config/model_fv.yaml, D-142), in plain Python for the repository and the kit.

The QuantConnect kit embeds this module's source verbatim and runs `run_day` on each day's one-minute bars inside
the cloud; only trade records leave (D-120). No imports beyond `math`; missing bars are `None`.

Slots are bar END times counted in minutes from the recording's first bar (slot 0 ends at `recording.first`). A
signal is decided at the close of bar t; the order fills at the open of the next bar that exists (D-123). The anchor
("fair value") is the OPEN of the bar that starts at the anchor time, i.e. the bar ending one minute later.
"""
import math


# ---------------------------------------------------------------------------------------------------- structure

def ffill(xs):
    out, last = [], None
    for x in xs:
        if x is not None:
            last = x
        out.append(last)
    return out


def swings(h, l, n):
    """Williams fractals, two bars each side, all five bars present; a swing at i is usable from bar i + 2."""
    out = {"high": [], "low": []}
    for i in range(2, n - 2):
        wh, wl = h[i - 2:i + 3], l[i - 2:i + 3]
        if any(v is None for v in wh) or any(v is None for v in wl):
            continue
        if all(h[i] > h[k] for k in (i - 2, i - 1, i + 1, i + 2)):
            out["high"].append((i, h[i]))
        if all(l[i] < l[k] for k in (i - 2, i - 1, i + 1, i + 2)):
            out["low"].append((i, l[i]))
    return out


def usable(sw, kind, t, since=0):
    return [s for s in sw[kind] if s[0] + 2 <= t and s[0] >= since]


def displacement(o, h, l, c, t, d, w):
    """A bar closing decisively in direction d: body that way, counter-wick <= w x (extreme - open)."""
    if o[t] is None or c[t] is None:
        return False
    if d > 0:
        span = h[t] - o[t]
        return c[t] > o[t] and span > 0 and (h[t] - c[t]) <= w * span + 1e-12
    span = o[t] - l[t]
    return c[t] < o[t] and span > 0 and (c[t] - l[t]) <= w * span + 1e-12


def breaks(c, t, d, sw):
    """The close at t is beyond the most recent confirmed swing in direction d (BOS or MSB, by context)."""
    s = usable(sw, "high" if d > 0 else "low", t)
    if not s or c[t] is None:
        return False
    return c[t] > s[-1][1] if d > 0 else c[t] < s[-1][1]


def atr_pct(o, h, l, c, t, n=14, min_bars=10):
    """Mean true range of the last n bars ending at t, as a percent of the close at t; None if too few bars."""
    trs, j, prev = [], t, None
    while j >= 0 and len(trs) < n:
        if o[j] is not None:
            k = j - 1
            while k >= 0 and c[k] is None:
                k -= 1
            prev = c[k] if k >= 0 else None
            hi, lo = h[j], l[j]
            if prev is not None:
                hi, lo = max(hi, prev), min(lo, prev)
            trs.append(hi - lo)
        j -= 1
    if len(trs) < min_bars or not c[t]:
        return None
    return 100.0 * (sum(trs) / len(trs)) / c[t]


def band_stop_pct(atr, bands):
    """JJ's three volatility bands (config: atr_bands) -> the stop as a percent of price, and the band index."""
    if atr >= bands["hi"]:
        return bands["stop_hi"], 2
    if atr >= bands["lo"]:
        return bands["stop_mid"], 1
    return bands["stop_lo"], 0


# ---------------------------------------------------------------------------------------------------- one trade

def simulate(o, h, l, c, t, d, stop_px_fn, fills, last_slot, floor_ticks, rr):
    """Fill at the next bar's open after t, place the stop (stop_px_fn(entry) -> stop price, or a distance in
    ticks via fills) and a 1.5R target, walk to the exit. Returns a record or {'reason': ...}."""
    tick = fills["tick"]
    j0 = next((j for j in range(t + 1, last_slot + 1) if o[j] is not None), None)
    if j0 is None:
        return {"reason": "no_next_bar"}
    entry = o[j0] + d * fills["entry"] * tick
    raw_entry = o[j0]
    stop_px = stop_px_fn(entry)
    if stop_px is None:
        return {"reason": "no_stop"}
    if (stop_px - entry) * d >= 0:
        return {"reason": "stop_through_entry"}
    stop_ticks = max(int(round(abs(entry - stop_px) / tick)), floor_ticks)
    stop_px = entry - d * stop_ticks * tick
    tgt = entry + d * rr * stop_ticks * tick
    mfe = mae = 0.0
    raw_exit, kind, j_exit = None, "", None          # the exit before slippage; the cost is applied below
    for j in range(j0, last_slot + 1):
        if o[j] is None:
            continue
        if j != j0 and ((o[j] <= stop_px) if d > 0 else (o[j] >= stop_px)):
            raw_exit, kind, j_exit = o[j], "g", j   # the bar opened through the stop
            break
        fav = (h[j] - entry) if d > 0 else (entry - l[j])
        adv = (entry - l[j]) if d > 0 else (h[j] - entry)
        mfe, mae = max(mfe, fav), max(mae, adv)
        if (l[j] <= stop_px) if d > 0 else (h[j] >= stop_px):
            raw_exit, kind, j_exit = stop_px, "s", j  # stop first when a bar touches both (conservative)
            break
        if (h[j] > tgt) if d > 0 else (l[j] < tgt):
            raw_exit, kind, j_exit = tgt, "t", j      # a resting limit needs a trade through it
            break
    if raw_exit is None:
        raw_exit, kind, j_exit = ffill(c)[last_slot], "m", last_slot
    slip = {"g": fills["stop"], "s": fills["stop"], "t": fills["target"], "m": fills["flatten"]}[kind]
    exit_px = raw_exit - d * slip * tick
    risk_px = stop_ticks * tick
    r_price = d * (raw_exit - raw_entry) / risk_px    # zero-cost R: no slippage, no commission
    pnl = d * (exit_px - entry) * fills["point_value"] - fills["round_turn"]
    return {"reason": "", "t": t, "j0": j0, "j_exit": j_exit, "d": d, "entry": entry, "exit": exit_px,
            "stop_ticks": stop_ticks, "exit_kind": kind, "r_net": pnl / (stop_ticks * fills["tick_value"]),
            "r_price": r_price, "mfe": mfe / risk_px, "mae": mae / risk_px}


# ---------------------------------------------------------------------------------------------------- one day

def run_day(o, h, l, c, P, family, fills):
    """Every FV1 trade of the day for one stop family ('atr_bands' or 'structural'), sessions in order.

    P: slots and settings -- sessions: list of dicts {name, anchor, first, cont_until, last}; last_slot (the time
    exit); floor_ticks; w (displacement); rr (1.5); attempts (per phase per session); max_losses (daily stop);
    bands (atr_bands thresholds and stops, percent)."""
    n = len(o)
    sw = swings(h, l, n)
    trades, losses, busy_until = [], 0, -1
    for S in P["sessions"]:
        a = S["anchor"]
        fv = o[a] if a < n else None
        if fv is None:
            continue
        taken = {"c": 0, "r": 0}
        touched = False
        for t in range(S["first"], S["last"] + 1):
            if t <= busy_until or losses >= P["max_losses"]:
                if t <= busy_until and h[t] is not None and l[t] <= fv <= h[t]:
                    touched = True
                continue
            if o[t] is None or c[t] is None:
                continue
            if t > a and l[t] <= fv <= h[t]:
                touched = True
            phase = "c" if t <= S["cont_until"] else "r"
            if taken[phase] >= P["attempts"]:
                continue
            side = 1 if c[t] > fv else (-1 if c[t] < fv else 0)
            if side == 0:
                continue
            cand = []
            if phase == "c":
                cand.append(("cont", side))
            else:
                cand.append(("rev", -side))
                if touched:
                    cand.append(("recont", side))
            for tag, d in cand:
                if not (displacement(o, h, l, c, t, d, P["w"]) and breaks(c, t, d, sw)):
                    continue
                if family == "atr_bands":
                    atr = atr_pct(o, h, l, c, t)
                    if atr is None:
                        continue
                    pct, band = band_stop_pct(atr, P["bands"])
                    stop_fn = (lambda e, pct=pct, d=d: e - d * e * pct / 100.0)
                else:
                    band = -1
                    if tag == "rev":
                        ext = usable(sw, "low" if d > 0 else "high", t, since=a)
                        ext = (min(s[1] for s in ext) if d > 0 else max(s[1] for s in ext)) if ext else None
                        if ext is None:
                            last_opp = usable(sw, "low" if d > 0 else "high", t)
                            ext = last_opp[-1][1] if last_opp else None
                    else:
                        last_opp = usable(sw, "low" if d > 0 else "high", t)
                        ext = last_opp[-1][1] if last_opp else None
                    tick = fills["tick"]
                    stop_fn = (lambda e, ext=ext, d=d, tick=tick: None if ext is None else ext - d * tick)
                r = simulate(o, h, l, c, t, d, stop_fn, fills, P["last_slot"], P["floor_ticks"], P["rr"])
                if r["reason"]:
                    continue
                if tag == "rev" and ((d > 0 and r["entry"] >= fv) or (d < 0 and r["entry"] <= fv)):
                    continue                                 # a reversion fill already past fair value
                r.update({"session": S["name"], "tag": tag, "band": band})
                trades.append(r)
                taken[phase] += 1
                busy_until = r["j_exit"]
                if r["r_net"] < 0:
                    losses += 1
                break
    return trades


def scaled(o, h, l, c, ref, scale_to):
    """The day's bars at actual prices (scale_to None) or rescaled so `ref` maps to `scale_to` (D-106)."""
    f = 1.0 if (scale_to is None or not ref) else scale_to / ref
    return tuple([None if x is None else x * f for x in xs] for xs in (o, h, l, c))
