"""IM2 (P-04 §3; P-03 §3 before the fidelity audits of 2026-09-27): the paper's noise-band entries, each bracketed at
1, 2 and 3 R, in plain Python for the repository and the kit.

The QuantConnect kit embeds this module's source verbatim and runs `run_day` on each session's one-minute bars inside
the cloud; only the entries, their outcomes and a few integrity numbers leave (D-120). No imports; missing bars are
`None`.

Slots are bar END times counted from the session start: slot 0 is the bar that starts at the session open (it ends one
minute later) and the last slot is the bar ending at the session close. The session open is the open of the first bar
present. A decision at slot t is taken on the close of the bar ending then (a missing bar there: no decision); the
entry fills at the open of the next bar present, one tick of the traded micro adverse.

The rules are P-04 §3's (the bands, VWAP, entries, stop, brackets at 1, 2 and 3 R, the wait to the later of the two
scales' 2:1 exits plus 5 minutes). Two
fill rules there come from the fill audit of 2026-09-27: every resting order and fill on the micro's tick grid at the
scale walked (`on_grid`: stop and target away from the entry, fills against the position), and, in a release minute
(`hot`), market orders at the bar's worst price when that is worse.

Choices P-04 leaves to the implementation, fixed here before any IM2 data is read (the kit's calendar and roll
choices are in `propedge/data/qc_algorithms.py`, above `IM2_PREFIX`):

* **Scales.** Every entry is walked at the reference price (D-106) and at actual prices, and the market's wait runs
  to the later of the two walks' 2:1 exits (P-04), so one set of entries holds at most one position per market at
  either scale. An entry through its stop at actual prices only has no actual walk and is counted (`through_actual`),
  not dropped; its wait is the reference walk's.
* **Sigma before a session's first bar.** A past session whose first bars are missing has nothing to carry forward
  there, so a decision at such a slot has no sigma and is not taken (counted, `no_band`).
* **No bar after the decision.** A signal with no later bar in the session is not an entry (counted, `no_bar`).
* **MAE.** A bracket's MAE is the largest move against the entry fill up to its exit, in units of the stop distance:
  a bar that touches the stop contributes the stop's fill (the price reached the stop first), a bar opening through
  the stop contributes that fill, and every other bar -- the target's bar and the time exit's included, whose order
  inside the bar is unknown -- contributes its whole range against the position; a time exit's fill counts too.
* **The lowest price held** (`mn`, for the price-lock rule, P-04 §3): the lowest low at actual prices from the entry
  bar through the later of the two walks' 2:1 exits (the longest bracket the lifecycle holds).
"""


def session_open(o):
    """The open of the first bar present, or None."""
    return next((x for x in o if x is not None), None)


def complete(o, last_slot, min_cov):
    """A complete session: a bar at the close time and at least `min_cov` of the minutes."""
    if o[last_slot] is None:
        return False
    return sum(1 for x in o if x is not None) / float(len(o)) >= min_cov


def move_profile(o, c):
    """|close / open - 1| at every slot, the close carried forward over a missing minute (None before the first)."""
    ref = session_open(o)
    out, last = [], None
    for x in c:
        if x is not None:
            last = x
        out.append(None if (last is None or not ref) else abs(last / ref - 1.0))
    return out


def sigma_at(profiles, t):
    """The mean of the profiles' values at slot t; None when any is missing."""
    xs = [p[t] for p in profiles]
    if not xs or any(x is None for x in xs):
        return None
    return sum(xs) / len(xs)


def vwap_series(h, l, c, v):
    """VWAP from the session open at every slot: (high + low + close) / 3 weighted by volume, cumulative; a missing
    minute or one with no volume adds nothing; None until the first bar with volume."""
    out, num, den = [], 0.0, 0.0
    for j in range(len(c)):
        if c[j] is not None and v[j]:
            num += (h[j] + l[j] + c[j]) / 3.0 * v[j]
            den += v[j]
        out.append(num / den if den > 0 else None)
    return out


def scaled(o, h, l, c, f):
    """The day's bars multiplied by f (the reference-price rescale, D-106)."""
    return tuple([None if x is None else x * f for x in xs] for xs in (o, h, l, c))


def on_grid(x, g, up):
    """x on the grid of step g (> 0; prices are positive): x itself when within a millionth of a step of a grid price,
    else the next grid price above (`up`) or below."""
    k = x / g
    n = int(round(k))
    if abs(k - n) > 1e-6:
        n = int(k) + (1 if up else 0)
    return round(n * g, 10)


def bracket(o, h, l, c, j0, d, entry, stop, dist, R, F, last_slot, hot=()):
    """One bracket at R on an entry filled at `entry` at the open of bar j0, direction d (+1 long, -1 short), stop
    level `stop` and entry both on the grid F['tick'], stop distance `dist` (> 0); `hot`: the release slots. Returns
    (exit kind, exit slot, R after the fills' ticks, MAE in R): kind 't' target, 's' stop touched, 'g' a bar opened
    through the stop, 'm' the session's last bar."""
    tick = F["tick"]
    tgt = on_grid(entry + d * R * dist, tick, d > 0)                # at least R stop distances away

    def worse(x, j):
        """An exit fill: in a release slot the bar's worst price if that is worse; then onto the grid, adversely."""
        if j in hot:
            x = min(x, l[j]) if d > 0 else max(x, h[j])
        return on_grid(x, tick, d < 0)

    worst = 0.0
    for j in range(j0, last_slot + 1):
        if o[j] is None:
            continue
        if j != j0 and ((o[j] < stop) if d > 0 else (o[j] > stop)):
            x = worse(o[j], j)                                     # opened through: that open, no further tick
            return "g", j, d * (x - entry) / dist, max(worst, d * (entry - x)) / dist
        if (l[j] <= stop) if d > 0 else (h[j] >= stop):
            x = worse(stop - d * F["stop"] * tick, j)              # touched: the stop first, one tick adverse
            return "s", j, d * (x - entry) / dist, max(worst, d * (entry - x)) / dist
        worst = max(worst, (entry - l[j]) if d > 0 else (h[j] - entry))
        if (h[j] > tgt) if d > 0 else (l[j] < tgt):
            return "t", j, d * (tgt - entry) / dist, worst / dist  # a resting limit needs a trade through it
    jl = max(j for j in range(j0, last_slot + 1) if o[j] is not None)
    x = worse(c[jl] - d * F["flatten"] * tick, jl)
    return "m", jl, d * (x - entry) / dist, max(worst, d * (entry - x)) / dist


def run_day(o, h, l, c, v, pc, profiles, P, F, p_ref, hot=()):
    """Every IM2 entry of one session, in decision order.

    o, h, l, c, v: the session's bars at actual prices, one per slot (None missing). pc: the prior close (actual), or
    None. profiles: `move_profile` of past complete sessions, oldest first; the last P['lookback'] are used. P: times
    (decision slots), last_slot, lookback, mult, rr (the brackets' R), seq_rr (the R that keeps the market busy), wait
    (slots after its exit). F: tick (the traded micro's, in price units: the grid), entry, stop, target, flatten
    (ticks). hot: the session's release slots (P-04).

    Returns {'ref', 'signals', 'dropped', 'through', 'through_actual', 'no_bar', 'missing', 'no_band', 'entries'}; each
    entry is {'d', 't', 'j0', 'cl', 'ub', 'lb', 'vw', 'mn', 'walks'}, walks[0] at the reference price and walks[1] at
    actual prices, each {'dist', 'br': [(kind, exit slot, R, MAE) per R in P['rr']]} or None (an entry through its
    stop there)."""
    last = P["last_slot"]
    ref = session_open(o)
    out = {"ref": ref, "signals": 0, "dropped": 0, "through": 0, "through_actual": 0, "no_bar": 0, "missing": 0,
           "no_band": 0, "entries": []}
    if ref is None or pc is None or len(profiles) < P["lookback"]:
        return out
    past = profiles[-P["lookback"]:]
    f = p_ref / ref
    views = ((f, scaled(o, h, l, c, f)), (1.0, (o, h, l, c)))
    vwap = vwap_series(h, l, c, v)
    seq = list(P["rr"]).index(P["seq_rr"])
    tick = F["tick"]
    busy = None
    for t in P["times"]:
        if o[t] is None:
            out["missing"] += 1
            continue
        sig, vw = sigma_at(past, t), vwap[t]
        if sig is None or vw is None:
            out["no_band"] += 1
            continue
        ub = max(ref, pc) * (1.0 + P["mult"] * sig)
        lb = min(ref, pc) * (1.0 - P["mult"] * sig)
        d = 1 if (c[t] > ub and c[t] > vw) else (-1 if (c[t] < lb and c[t] < vw) else 0)
        if d == 0:
            continue
        out["signals"] += 1
        if busy is not None and t < busy + P["wait"]:
            out["dropped"] += 1
            continue
        j0 = next((j for j in range(t + 1, last + 1) if o[j] is not None), None)
        if j0 is None:
            out["no_bar"] += 1
            continue
        stop_raw = lb if d > 0 else ub
        walks = []
        for sf, (so, sh, sl, sc) in views:
            x = so[j0] + d * F["entry"] * tick
            if j0 in hot:
                x = max(x, sh[j0]) if d > 0 else min(x, sl[j0])
            entry = on_grid(x, tick, d > 0)                     # a buy rounds up, a sell down
            stop = on_grid(stop_raw * sf, tick, d < 0)          # away from the entry
            dist = d * (entry - stop)
            if not dist > 0:
                walks.append(None)
                continue
            walks.append({"dist": dist, "br": [bracket(so, sh, sl, sc, j0, d, entry, stop, dist, R, F, last, hot)
                                               for R in P["rr"]]})
        if walks[0] is None:
            out["through"] += 1
            continue
        if walks[1] is None:
            out["through_actual"] += 1
        busy = max(w["br"][seq][1] for w in walks if w is not None)    # the later 2:1 exit of the two scales
        mn = min(l[j] for j in range(j0, busy + 1) if l[j] is not None)
        out["entries"].append({"d": d, "t": t, "j0": j0, "cl": c[t], "ub": ub, "lb": lb, "vw": vw, "mn": mn,
                               "walks": walks})
    return out


def entry_prices(e, ref, p_ref, tick):
    """The entry fill and stop level at each scale, recovered from an exported entry: the stop is the opposite band
    (times the rescale at the reference price) on the grid `tick`, away from the entry; the entry is the stop plus the
    distance."""
    out = []
    for k, w in enumerate(e["walks"]):
        if w is None:
            out.append(None)
            continue
        stop = on_grid((e["lb"] if e["d"] > 0 else e["ub"]) * (p_ref / ref if k == 0 else 1.0), tick, e["d"] < 0)
        out.append((stop + e["d"] * w["dist"], stop))
    return out


__all__ = ["session_open", "complete", "move_profile", "sigma_at", "vwap_series", "scaled", "on_grid", "bracket",
           "run_day", "entry_prices"]
