"""The open-reversion trade, in plain Python, shared by this repository and the QuantConnect kit.

Test 1's scorer (`propedge/outcomes/open_reversion.py`) is numpy-based and runs on a local panel.
D-120 keeps raw bars in the cloud, so a re-score must run inside QuantConnect. To make sure the
cloud computes exactly what Test 1 computed, the kit embeds THIS module's source verbatim
(`propedge/data/qc_algorithms.openrev_preamble`), and `tests/test_openrev_core.py` shows it equals
the numpy scorer bar for bar in `close` fill mode. The only new behaviour is `fill="next_open"`
(D-122): the signal is decided at the close of bar t exactly as before (same trigger, same
reward-to-risk filter), and the market order fills at the open of the next bar that exists.

No imports beyond `math`; missing bars are `None`. Prices are floats on the tick grid.
"""
import math

TICK = 0.25


def ffill(xs):
    out, last = [], None
    for x in xs:
        if x is not None:
            last = x
        out.append(last)
    return out


def swing_levels(h, l, kind, start, upto):
    """Williams fractals, two bars each side, all five bars present, i in [start+2, upto-2]."""
    out = []
    for i in range(start + 2, upto - 1):
        wh, wl = h[i - 2:i + 3], l[i - 2:i + 3]
        if any(v is None for v in wh) or any(v is None for v in wl):
            continue
        if kind == "low" and all(l[i] < l[k] for k in (i - 2, i - 1, i + 1, i + 2)):
            out.append((i, l[i]))
        elif kind == "high" and all(h[i] > h[k] for k in (i - 2, i - 1, i + 1, i + 2)):
            out.append((i, h[i]))
    return out


def swing_table(h, l, swing_from, upto):
    """Every confirmed swing up to bar `upto`, computed once per day. A swing at i is usable at bar
    t when i + 2 <= t -- exactly the set `swing_levels(h, l, kind, swing_from, t)` returns."""
    return {"low": swing_levels(h, l, "low", swing_from, upto),
            "high": swing_levels(h, l, "high", swing_from, upto)}


def _usable(sw, kind, t):
    return [s for s in sw[kind] if s[0] + 2 <= t]


def is_structural_trigger(o, h, l, c, t, d, w, swing_from, sw=None):
    if c[t] is None or o[t] is None:
        return False
    if sw is None:
        sw = swing_table(h, l, swing_from, t)
    swings = _usable(sw, "low" if d < 0 else "high", t)
    if not swings:
        return False
    level = swings[-1][1]
    if d < 0:
        return (c[t] < level and c[t] < o[t] and (o[t] - l[t]) > 0
                and (c[t] - l[t]) <= w * (o[t] - l[t]) + 1e-12)
    return (c[t] > level and c[t] > o[t] and (h[t] - o[t]) > 0
            and (h[t] - c[t]) <= w * (h[t] - o[t]) + 1e-12)


def far_side_anchor(o, h, l, c, t, d, kind, swing_from, sw=None):
    if kind == "trigger_bar":
        return h[t] if d < 0 else l[t]
    if sw is None:
        sw = swing_table(h, l, swing_from, t)
    swings = [s[1] for s in _usable(sw, "high" if d < 0 else "low", t)]
    if not swings:
        return None
    return max(swings) if d < 0 else min(swings)


def _walk(o, h, l, c, d, entry, stop_px, tgt, j_from, cutoff, fills, entry_bar=None):
    """Exit search from bar j_from to the cutoff. On `entry_bar` the position was opened at that
    bar's open, so no gap-through is possible there; its range is still checked, stop first."""
    for j in range(j_from, cutoff + 1):
        if o[j] is None:
            continue
        if j != entry_bar and ((o[j] >= stop_px) if d < 0 else (o[j] <= stop_px)):
            return o[j], "stop_gap", j
        stop_hit = h[j] >= stop_px if d < 0 else l[j] <= stop_px
        tgt_hit = l[j] < tgt if d < 0 else h[j] > tgt
        if stop_hit:
            return stop_px - d * fills["stop"] * TICK, "stop", j
        if tgt_hit:
            return tgt - d * fills["target"] * TICK, "target", j
    cc = ffill(c)
    return cc[cutoff] - d * fills["flatten"] * TICK, "time", cutoff


def score_trade(o, h, l, c, t, d, fv, anchor, r_min, floor_ticks, fills, cutoff, swing_from,
                flip=False, fill="close", sw=None):
    """One trade toward fair value decided at the close of bar t. `fills` is a dict with entry,
    stop, target, flatten (adverse ticks), round_turn, tick_value, point_value."""
    a = far_side_anchor(o, h, l, c, t, d, anchor, swing_from, sw)
    if a is None:
        return {"reason": "no_swing_anchor"}
    entry = c[t] + d * fills["entry"] * TICK
    if (d < 0 and entry <= fv) or (d > 0 and entry >= fv):
        return {"reason": "past_fair_value"}
    anchor_stop = a - d * TICK
    stop_ticks = max(int(round(abs(anchor_stop - entry) / TICK)), floor_ticks)
    reward = abs(fv - entry)
    R = reward / (stop_ticks * TICK)
    if R < r_min - 1e-12:
        return {"reason": "r_below_min", "R_at_entry": R}
    j_from, entry_bar = t + 1, None
    if fill == "next_open":
        # D-122: the decision above is unchanged; the order fills at the next existing bar's open,
        # and the geometry is re-placed from that fill with the same rules.
        j0 = next((j for j in range(t + 1, cutoff + 1) if o[j] is not None), None)
        if j0 is None:
            return {"reason": "no_next_bar"}
        entry = o[j0] + d * fills["entry"] * TICK
        if (d < 0 and entry <= fv) or (d > 0 and entry >= fv):
            return {"reason": "filled_past_fair_value"}
        stop_ticks = max(int(round(abs(anchor_stop - entry) / TICK)), floor_ticks)
        reward = abs(fv - entry)
        R = reward / (stop_ticks * TICK)
        j_from, entry_bar = j0, j0
    if flip:
        d = -d
        entry = (c[t] if fill == "close" else o[j_from]) + d * fills["entry"] * TICK
    stop_px = entry - d * stop_ticks * TICK
    tgt = fv if not flip else entry + d * reward
    exit_px, kind, j_exit = _walk(o, h, l, c, d, entry, stop_px, tgt, j_from, cutoff, fills, entry_bar)
    pnl_gross = d * (exit_px - entry) * fills["point_value"]
    pnl_net = pnl_gross - fills["round_turn"]
    risk = stop_ticks * fills["tick_value"]
    return {"reason": "", "t": t, "stop_ticks": stop_ticks, "floor_bound": stop_ticks == floor_ticks,
            "R_at_entry": R, "entry": entry, "exit": exit_px, "exit_kind": kind, "minutes": j_exit - t,
            "u": pnl_net / risk, "u_gross": pnl_gross / risk}


def scaled(o, h, l, c, ps, scale_to):
    """The day's bars at the actual price level (scale_to None) or rescaled to `scale_to` (D-106)."""
    f = 1.0 if scale_to is None else scale_to / ps
    return tuple([None if x is None else x * f for x in xs] for xs in (o, h, l, c))


def score_day(o, h, l, c, ps, anchor, r_min, baseline, fills, p, scale_to=None, flip=False,
              fill="close", pre=None):
    """The first qualifying bar in the window toward fair value, and its trade. `p` holds the slot
    indices (first, last, cutoff, swing_from), `w` and `floor_ticks`. `pre` = (o, h, l, c, sw)
    already scaled, with its swing table, so a day scored many times computes them once."""
    if pre is None:
        o, h, l, c = scaled(o, h, l, c, ps, scale_to)
        sw = swing_table(h, l, p["swing_from"], p["last"])
    else:
        o, h, l, c, sw = pre
    fv = o[p["swing_from"]]
    if fv is None:
        return {"reason": "no_open"}
    last_reason = "no_trigger"
    for t in range(p["first"], p["last"] + 1):
        if c[t] is None:
            continue
        d = -1 if c[t] > fv else (1 if c[t] < fv else 0)
        if d == 0:
            continue
        if not baseline and not is_structural_trigger(o, h, l, c, t, d, p["w"], p["swing_from"], sw):
            continue
        r = score_trade(o, h, l, c, t, d, fv, anchor, r_min, p["floor_ticks"], fills, p["cutoff"],
                        p["swing_from"], flip=flip, fill=fill, sw=sw)
        if r["reason"] == "":
            r["direction"] = -d if flip else d
            return r
        last_reason = r["reason"]
        if not baseline:
            break
    return {"reason": last_reason}
