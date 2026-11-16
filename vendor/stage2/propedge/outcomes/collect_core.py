"""The collect map (config/collect_map.yaml; D-381): uneven brackets whose target alone makes a winning day, at every hour
of Topstep's trading day, walked on minute bars with every tied minute settled on its one-second bars.

The kit (R145) embeds this source verbatim -- no imports, missing bars None -- and on each trading day runs `c_walks`,
fetches the second bars of the minutes `c_ties` names, and adds the day with `c_count`; only counts leave (D-120).
The clock is flip_core's: a slot is a bar's END time in minutes after 17:00 CT of the evening the trading day starts;
the bar ending 15:10 CT is `C_FLAT`. A decision at slot t enters at the open of the first bar after t (on time) or of
the bar after that (one minute late), one tick adverse.

A bracket in direction d (+1 long, -1 short) has its target T points in favour and its stop S points against. The
target is reached when a bar trades THROUGH it (a resting limit's fill); the stop when a bar touches it or opens beyond
it (filled at that open: the gap beyond the stop, counted per stop level). A bracket is read from its entry bar to its
box's last bar -- the box's length, the day's last bar, or `cut` (the last bar before a scheduled release), whichever
comes first -- and is a SCRATCH if it reaches neither: closed at that bar's close, one tick adverse, its P&L kept.
When the target and the stop are first reached in the same minute, that minute's second bars decide (`c_tie`); a second
reaching both, or a minute without second bars, is the stop's (counted).
"""
C_FLAT = 22 * 60 + 10


def c_slot(hour, minute):
    """A bar END time (CT) on the trading-day clock."""
    m = hour * 60 + minute
    return m - 1020 if m > 1020 else m + 420


def c_last(o):
    """The day's last bar at or before 15:10 CT, or None."""
    for j in range(min(C_FLAT, len(o) - 1), -1, -1):
        if o[j] is not None:
            return j
    return None


def c_entry(o, t, delay, last):
    """The entry bar: the `delay`-th bar with an open after slot t, at or before `last`; None without one."""
    k = 0
    for j in range(t + 1, last + 1):
        if o[j] is not None:
            if k == delay:
                return j
            k += 1
    return None


def c_passages(o, h, l, j0, end, entry, d, levels):
    """For ascending distances `levels`: the first bar from j0 to end trading through entry + d*L (fav) and the first
    touching or opening beyond entry - d*L (adv), and an adverse open's gap beyond L (a bar after j0)."""
    n = len(levels)
    fav, adv, gap = [None] * n, [None] * n, [0.0] * n
    pf = pa = 0
    for j in range(j0, end + 1):
        if o[j] is None:
            continue
        f = (h[j] - entry) if d > 0 else (entry - l[j])
        a = (entry - l[j]) if d > 0 else (h[j] - entry)
        ao = (entry - o[j]) if d > 0 else (o[j] - entry)
        while pf < n and f > levels[pf] + 1e-9:
            fav[pf] = j
            pf += 1
        while pa < n and a >= levels[pa] - 1e-9:
            adv[pa] = j
            if j != j0 and ao > levels[pa] + 1e-9:
                gap[pa] = ao - levels[pa]
            pa += 1
        if pf == n and pa == n:
            break
    return fav, adv, gap


def c_tie(so, sh, sl, entry, d, T, S):
    """A tied minute's second bars in order: 't' (target traded through first), 's' (stop touched first), or None (a
    second reaching both, or neither reached)."""
    for k in range(len(so)):
        if so[k] is None:
            continue
        hit_t = ((sh[k] - entry) if d > 0 else (entry - sl[k])) > T + 1e-9
        hit_s = ((entry - sl[k]) if d > 0 else (sh[k] - entry)) >= S - 1e-9
        if hit_t and hit_s:
            return None
        if hit_s:
            return "s"
        if hit_t:
            return "t"
    return None


def c_walks(o, h, l, c, P, cut):
    """Every walk of the day: per slot, delay and side (si, dl, d, j0, entry, fav, adv, gap, ends, marks, cutb) -- the
    entry, the passages to P['levels'], each box's last bar, its scratch P&L (price) and whether the cut shortened it.
    P: 'slots', 'delays', 'boxes' (ascending, bars), 'levels' (ascending, price), 'slip' (price)."""
    last = c_last(o)
    if last is None:
        return []
    out = []
    for si, t in enumerate(P["slots"]):
        if t >= last:
            continue
        for dl in P["delays"]:
            j0 = c_entry(o, t, dl, last)
            if j0 is None:
                continue
            stop_at = min(last, cut) if (cut is not None and j0 <= cut) else last
            ends = [min(j0 + b, stop_at) for b in P["boxes"]]
            cutb = [1 if (stop_at < last and stop_at < j0 + b) else 0 for b in P["boxes"]]
            for d in (1, -1):
                entry = o[j0] + d * P["slip"]
                fav, adv, gap = c_passages(o, h, l, j0, ends[-1], entry, d, P["levels"])
                marks = []
                for e in ends:
                    j = e
                    while j > j0 and c[j] is None:
                        j -= 1
                    marks.append(d * ((c[j] - d * P["slip"]) - entry))
                out.append((si, dl, d, j0, entry, fav, adv, gap, ends, marks, cutb))
    return out


def c_ties(walks, P):
    """The bars at which some bracket's target and stop are first reached together inside its longest box."""
    need = set()
    for w in walks:
        fav, adv, e = w[5], w[6], w[8][-1]
        for row in P["pairs"]:
            for iT, iS in row:
                if fav[iT] is not None and fav[iT] == adv[iS] and fav[iT] <= e:
                    need.add(fav[iT])
    return need


def c_count(walks, P, tie, acc, aux, y):
    """Settle every bracket in every box and add it in: acc[(y, si, ni, ki, bi, dl)] = [target, stop, scratch, minutes
    to resolution summed, scratch ticks summed]; aux[('T', y, si)] = ties [target, stop, unsettled];
    aux[('G', y, si, li)] = [stops reached, gapped, gap ticks] per level; aux[('B', y, si, bi)] = [walks, cut short].
    `tie(j, entry, d, T, S)` settles a tied minute ('t', 's' or None). P['pairs'][ni][ki] = (target, stop) level indices."""
    lv, tick = P["levels"], P["tick"]
    for si, dl, d, j0, entry, fav, adv, gap, ends, marks, cutb in walks:
        for bi in range(len(ends)):
            b = aux.setdefault(("B", y, si, bi), [0, 0])
            b[0] += 1
            b[1] += cutb[bi]
        for li in range(len(lv)):
            if adv[li] is not None and adv[li] <= ends[-1]:
                g = aux.setdefault(("G", y, si, li), [0, 0, 0])
                g[0] += 1
                if gap[li] > 0:
                    g[1] += 1
                    g[2] += int(round(gap[li] / tick))
        for ni, row in enumerate(P["pairs"]):
            for ki, (iT, iS) in enumerate(row):
                jt, js, settled = fav[iT], adv[iS], None
                for bi, e in enumerate(ends):
                    t_in = jt is not None and jt <= e
                    s_in = js is not None and js <= e
                    if t_in and (not s_in or jt < js):
                        kind, j = 0, jt
                    elif s_in and (not t_in or js < jt):
                        kind, j = 1, js
                    elif t_in:
                        if settled is None:
                            r = tie(jt, entry, d, lv[iT], lv[iS])
                            settled = 0 if r == "t" else 1
                            a = aux.setdefault(("T", y, si), [0, 0, 0])
                            a[0 if r == "t" else (1 if r == "s" else 2)] += 1
                        kind, j = settled, jt
                    else:
                        kind, j = 2, e
                    a = acc.setdefault((y, si, ni, ki, bi, dl), [0, 0, 0, 0, 0])
                    a[kind] += 1
                    if kind == 2:
                        a[4] += int(round(marks[bi] / tick))
                    else:
                        a[3] += j - j0


def c_encode(acc, aux, y0):
    """Cells: 'C' y-y0,si,ni,ki,bi,dl,t,s,x,m,xs; 'T' y-y0,si,t,s,v; 'G' y-y0,si,li,n,g,gt; 'B' y-y0,si,bi,n,cut."""
    out = ["C%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % ((k[0] - y0,) + k[1:] + tuple(v)) for k, v in sorted(acc.items())]
    for k, v in sorted(aux.items()):
        out.append(k[0] + ",".join(str(x) for x in ((k[1] - y0,) + k[2:] + tuple(v))))
    return out


__all__ = ["C_FLAT", "c_slot", "c_last", "c_entry", "c_passages", "c_tie", "c_walks", "c_ties", "c_count", "c_encode"]
