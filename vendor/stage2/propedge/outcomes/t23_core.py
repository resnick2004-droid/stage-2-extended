"""T23's capture (D-416): per-trade records of brackets at fixed times -- the collect map's walk (`collect_core`, D-381)
with no box: a bracket runs to its target, its stop or the day's end (15:10 CT, or the last bar before a BLS release),
D-212's no time stop. The kit (R147, R148) embeds this source and `collect_core` verbatim -- no imports, missing bars
None -- and on each trading day runs `c_walks` with the one box `T_NO_BOX`, fetches the second bars of the minutes
`c_ties` names, and writes one record per walk with `t_records`, and one day record with `t_day`; only records leave.

A walk is (slot, delay, side); for each bracket (target, stop) in points its outcome is the target, the stop or the
end ('t', 's', 'f'), with the minutes from the entry bar to the exit bar. A minute that first reaches a bracket's target
and its stop is settled on its second bars ('t' or 's'); a second reaching both, or a minute without second bars, is
the stop's, marked 'u' (counted). A stop filled at an open beyond it carries the gap in ticks ('g'); an end carries its
P&L in ticks at the end bar's close, one tick adverse ('x'), as the collect map's scratch.
"""
T_NO_BOX = 10000            # longer than any trading day: the walk's box ends at the day's last bar or the cut


def t_a3(c, slots):
    """Per slot the sign of the last sixty minutes' move at the slot's bar (+1, -1, 0; None without both closes) --
    A3 (D-374), the side rule's input."""
    out = []
    for t in slots:
        a, b = (c[t] if 0 <= t < len(c) else None), (c[t - 60] if 0 <= t - 60 < len(c) else None)
        if a is None or b is None:
            out.append(None)
        else:
            out.append(1 if a > b else (-1 if a < b else 0))
    return out


def t_day(td, kind, a3):
    """The day record: 'D' yymmdd, the day's kind (n normal, b BLS-cut, o FOMC, e early close, x no bars) and the A3
    signs per slot (+, -, 0 or . for none)."""
    sym = "".join("." if x is None else ("+" if x > 0 else ("-" if x < 0 else "0")) for x in a3)
    return "D%02d%02d%02d,%s,%s" % (td[0] % 100, td[1], td[2], kind, sym)


def t_records(walks, P, tie):
    """One record per walk: 'W' slot index, delay, side (+/-), the entry bar on the trading-day clock, then per bracket
    of P['brackets'] (target, stop level indices) its outcome and minutes -- 't12', 's3', 's3u', 's1g2', 'f300x-14'."""
    lv, tick = P["levels"], P["tick"]
    out = []
    for si, dl, d, j0, entry, fav, adv, gap, ends, marks, cutb in walks:
        e = ends[0]
        parts = []
        for iT, iS in P["brackets"]:
            jt, js = fav[iT], adv[iS]
            t_in = jt is not None and jt <= e
            s_in = js is not None and js <= e
            if t_in and (not s_in or jt < js):
                parts.append("t%d" % (jt - j0))
            elif s_in and (not t_in or js < jt):
                g = int(round(gap[iS] / tick)) if gap[iS] > 0 else 0
                parts.append("s%d" % (js - j0) + ("g%d" % g if g else ""))
            elif t_in:
                r = tie(jt, entry, d, lv[iT], lv[iS])
                parts.append(("t%d" % (jt - j0)) if r == "t" else ("s%d" % (jt - j0) + ("" if r == "s" else "u")))
            else:
                parts.append("f%dx%d" % (e - j0, int(round(marks[0] / tick))))
        out.append("W%d,%d,%s,%d:%s" % (si, dl, "+" if d > 0 else "-", j0, ";".join(parts)))
    return out


__all__ = ["T_NO_BOX", "t_a3", "t_day", "t_records"]
