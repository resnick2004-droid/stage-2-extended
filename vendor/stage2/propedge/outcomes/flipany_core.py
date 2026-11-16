"""The any-time direction atlas (D-373; config/flip_anytime.yaml), embedded verbatim in kit R143 beside flip_core: the
measures at a slot (ticks, from P = the last close at or before it), the ten-minute range after a slot (the widths'
history), the previous day's summary, and the day's record. No imports; missing bars are None; flip_core's clock."""
ANY_RTH_OPEN = 931            # the bar ending 08:31 CT: its open is the session's 08:30 open
ANY_RTH_CLOSE = 1320          # the bar ending 15:00 CT


def _any_last(a, j):
    for i in range(min(j, len(a) - 1), -1, -1):
        if a[i] is not None:
            return i
    return None


def _any_first(a, lo, hi):
    for i in range(max(lo, 0), min(hi, len(a) - 1) + 1):
        if a[i] is not None:
            return i
    return None


def any_summary(o, c):
    """For the next day: the last close by 15:00 CT and the session's 08:30 open (None without them)."""
    jc = _any_last(c, ANY_RTH_CLOSE)
    jo = _any_first(o, ANY_RTH_OPEN, jc) if jc is not None else None
    return None if jo is None else {"close": c[jc], "rth_open": o[jo]}


def any_measures(o, h, l, c, s, prev, tick):
    """[A1 last bar's body, A2 15-minute move, A3 60-minute move, A4 move since 08:30 (None at or before it), A5 move
    since the day's first open, room to the low so far, room to the high so far, A7 prev session's move]; None without
    a bar by s."""
    jp = _any_last(c, s)
    if jp is None:
        return None
    P = c[jp]

    def t(x):
        return None if x is None else int(round(x / tick))

    j15, j60 = _any_last(c, s - 15), _any_last(c, s - 60)
    jr = _any_first(o, ANY_RTH_OPEN, jp) if s > ANY_RTH_OPEN - 1 else None
    j0 = _any_first(o, 0, jp)
    hs = [h[j] for j in range(0, jp + 1) if h[j] is not None]
    ls = [l[j] for j in range(0, jp + 1) if l[j] is not None]
    return [t(c[jp] - o[jp]) if o[jp] is not None else None,
            t(P - c[j15]) if j15 is not None else None,
            t(P - c[j60]) if j60 is not None else None,
            t(P - o[jr]) if (jr is not None and s >= ANY_RTH_OPEN) else None,
            t(P - o[j0]) if j0 is not None else None,
            t(P - min(ls)) if ls else None, t(max(hs) - P) if hs else None,
            t(prev["close"] - prev["rth_open"]) if prev is not None else None]


def any_range10(h, l, s, tick):
    """The high less low of the ten minute bars after slot s, in ticks; None if fewer than eight of them traded."""
    hs = [h[j] for j in range(s + 1, min(s + 10, len(h) - 1) + 1) if h[j] is not None]
    ls = [l[j] for j in range(s + 1, min(s + 10, len(l) - 1) + 1) if l[j] is not None]
    return None if len(hs) < 8 else int(round((max(hs) - min(ls)) / tick))


def day_outcomes_any(rows, index_of, n_widths, delays, tick):
    """run_day_flip's rows into one character per (width, delay, side: long, short) -- t, s, x, '-' not walked -- and,
    for the first (primary) width on time, [units long, scratch ticks long, units short, scratch ticks short]."""
    got = {}
    for ti, wi, dl, d, kind, units, x in rows:
        got[(index_of[wi], dl, d)] = (kind, units, x)
    s = ""
    for wi in range(n_widths):
        for dl in delays:
            for d in (1, -1):
                r = got.get((wi, dl, d))
                s += r[0] if r is not None else "-"
    ex = []
    for d in (1, -1):
        r = got.get((0, delays[0], d))
        ex += [None, None] if r is None else [int(r[1]), int(round(r[2] / tick)) if r[0] == "x" else 0]
    return s, ex


def any_block(widths, m, outs, ex):
    """One slot's block: the widths in ticks, the measures, the outcome string, the extras; a missing value is empty."""
    def f(v):
        return "" if v is None else str(int(v))
    return ",".join([f(w) for w in widths] + [f(v) for v in (m or [None] * 8)] + [outs] + [f(v) for v in ex])


def any_record(td, early, same, blocks):
    """'D' + yyyymmdd, early, same contract, then the slots' blocks, ':'-separated."""
    return "D" + "%04d%02d%02d" % tuple(td) + "," + str(int(early)) + "," + str(int(same)) + ":" + ":".join(blocks)
