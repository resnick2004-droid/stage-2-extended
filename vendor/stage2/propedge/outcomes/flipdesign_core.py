"""The flip design map (D-375; config/flip_design.yaml), embedded verbatim in kit R144 beside flip_core and
flipdir_core: per width and side the outcome and seconds to resolution, the marks at the shorter boxes' ends, and the
day's record. No imports; missing bars are None."""


def design_entry(o, t, delay):
    """The entry bar's index: the `delay`-th bar with an open after slot t (flip_core's walk), or None."""
    k = 0
    for j in range(t + 1, len(o)):
        if o[j] is not None:
            if k == delay:
                return j
            k += 1
    return None


def design_marks(o, c, j0, marks, tick):
    """For each m in marks: the last close at or before j0 + m less the entry bar's open, in ticks (None without one)."""
    out = []
    for m in marks:
        v = None
        for j in range(min(j0 + m, len(c) - 1), j0 - 1, -1):
            if c[j] is not None:
                v = int(round((c[j] - o[j0]) / tick))
                break
        out.append(v)
    return out


def design_outcomes(rows, n_widths, delays):
    """run_day_flip's rows into one character per (width, delay, side: long, short) -- t, s, x, '-' not walked -- and per
    width and side on time the units to resolution (None unless resolved)."""
    got = {(wi, dl, d): (kind, units) for ti, wi, dl, d, kind, units, x in rows}
    s = ""
    for wi in range(n_widths):
        for dl in delays:
            for d in (1, -1):
                r = got.get((wi, dl, d))
                s += r[0] if r is not None else "-"
    units = []
    for wi in range(n_widths):
        for d in (1, -1):
            r = got.get((wi, delays[0], d))
            units.append(r[1] if (r is not None and r[0] != "x") else None)
    return s, units


def design_record(td, early, same, m, keys, outs, units, marks):
    """'D' + yyyymmdd, early, same contract, the measures in `keys` order, the outcomes, the units, the marks."""
    def f(v):
        return "" if v is None else str(int(v))
    vals = ["%04d%02d%02d" % tuple(td), f(early), f(same)]
    vals += [f(m.get(k)) if m is not None else "" for k in keys]
    vals += [outs] + [f(u) for u in units] + [f(v) for v in marks]
    return "D" + ",".join(vals)
