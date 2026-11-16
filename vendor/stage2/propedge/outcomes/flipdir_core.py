"""The flip-direction atlas (D-371; config/flip_direction.yaml), embedded verbatim in kit R142 beside flip_core: the
measures known before 08:30 CT (ticks, from P = the last close at or before the bar ending 08:30), the day's summary
for the next day, the widths, and the day's record. No imports; missing bars are None; flip_core's slot clock."""
DIR_PRE = 930                 # the bar ending 08:30 CT
DIR_M60 = 870                 # ... 07:30 CT
DIR_M15 = 915                 # ... 08:15 CT
DIR_RTH_OPEN = 931            # ... 08:31 CT: its open is the session's 08:30 open
DIR_RTH_CLOSE = 1320          # ... 15:00 CT
DIR_MEASURES = ("p", "gap", "on", "m60", "m15", "b1", "onhi", "onlo", "prth", "prhi", "prlo")
DIR_SIDES = (1, -1)


def _last_at_or_before(a, j):
    for i in range(min(j, len(a) - 1), -1, -1):
        if a[i] is not None:
            return i
    return None


def _first_in(a, lo, hi):
    for i in range(max(lo, 0), min(hi, len(a) - 1) + 1):
        if a[i] is not None:
            return i
    return None


def day_summary(o, h, l, c):
    """For the next day: the last close by 15:00, the session's 08:30 open, high and low to it, the day's high and low."""
    jc = _last_at_or_before(c, DIR_RTH_CLOSE)
    if jc is None:
        return None
    hs = [x for x in h if x is not None]
    ls = [x for x in l if x is not None]
    jo = _first_in(o, DIR_RTH_OPEN, jc)
    rh = [h[j] for j in range(DIR_RTH_OPEN, jc + 1) if h[j] is not None] if jo is not None else []
    rl = [l[j] for j in range(DIR_RTH_OPEN, jc + 1) if l[j] is not None] if jo is not None else []
    return {"close": c[jc], "rth_open": o[jo] if jo is not None else None,
            "rth_hi": max(rh) if rh else None, "rth_lo": min(rl) if rl else None,
            "hi": max(hs) if hs else None, "lo": min(ls) if ls else None}


def day_measures(o, h, l, c, prev, tick):
    """P; the gap from `prev`'s close; the move since the day's first open, over 60 and 15 minutes; the last bar's body;
    the room to the day's high and low; `prev`'s session move and its close's room to that session's high and low.
    `prev`: the previous day's summary on the same contract, or None."""
    jp = _last_at_or_before(c, DIR_PRE)
    if jp is None:
        return None
    P = c[jp]

    def t(x):
        return None if x is None else int(round(x / tick))

    j0 = _first_in(o, 0, jp)
    j60 = _last_at_or_before(c, DIR_M60)
    j15 = _last_at_or_before(c, DIR_M15)
    hs = [h[j] for j in range(0, jp + 1) if h[j] is not None]
    ls = [l[j] for j in range(0, jp + 1) if l[j] is not None]
    out = {"p": t(P), "gap": None, "on": t(P - o[j0]) if j0 is not None else None,
           "m60": t(P - c[j60]) if j60 is not None else None,
           "m15": t(P - c[j15]) if j15 is not None else None,
           "b1": t(c[jp] - o[jp]) if o[jp] is not None else None,
           "onhi": t(max(hs) - P) if hs else None, "onlo": t(P - min(ls)) if ls else None,
           "prth": None, "prhi": None, "prlo": None}
    if prev is not None:
        out["gap"] = t(P - prev["close"])
        if prev["rth_open"] is not None and prev["rth_hi"] is not None and prev["rth_lo"] is not None:
            out["prth"] = t(prev["close"] - prev["rth_open"])
            out["prhi"] = t(prev["rth_hi"] - prev["close"])
            out["prlo"] = t(prev["close"] - prev["rth_lo"])
    return out


def day_widths(atr_ticks, fractions, fixed_ticks, min_ticks):
    """Widths in ticks: each fraction of ATR20 (at least min_ticks; None without ATR20), then the fixed ones."""
    out = []
    for f in fractions:
        out.append(None if not atr_ticks else max(int(min_ticks), int(round(f * atr_ticks))))
    for k in fixed_ticks:
        out.append(int(k))
    return out


def day_outcomes(rows, index_of, n_widths, delays, tick, extra_widths):
    """run_day_flip's rows into one character per (width, delay, side): t, s, x, or '-' not walked; and per extra width
    (on time, long then short) the units to resolution and the scratch's ticks. index_of: walked width -> all widths."""
    got = {}
    for ti, wi, dl, d, kind, units, x in rows:
        got[(index_of[wi], dl, d)] = (kind, units, x)
    s = ""
    for wi in range(n_widths):
        for dl in delays:
            for d in DIR_SIDES:
                r = got.get((wi, dl, d))
                s += r[0] if r is not None else "-"
    ex = []
    for wi in extra_widths:
        for d in DIR_SIDES:
            r = got.get((wi, delays[0], d))
            if r is None:
                ex += [None, None]
            else:
                ex += [int(r[1]), int(round(r[2] / tick)) if r[0] == "x" else 0]
    return s, ex


def encode_day(td, early, same, atr_ticks, res, m, widths_ticks, outcomes, extras):
    """'D' + yyyymmdd, early, same contract, ATR20, resolution (1 s, 2 min, 0 none), measures, widths, outcomes, extras."""
    def f(v):
        return "" if v is None else str(int(v))
    vals = ["%04d%02d%02d" % tuple(td), f(early), f(same), f(atr_ticks), f(res)]
    vals += [f(m.get(k)) if m is not None else "" for k in DIR_MEASURES]
    vals += [f(w) for w in widths_ticks]
    vals += [outcomes]
    vals += [f(v) for v in extras]
    return "D" + ",".join(vals)
