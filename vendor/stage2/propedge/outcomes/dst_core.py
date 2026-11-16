"""The clock check across daylight-saving changes (config/dst_check.yaml; D-386 (7)): per trading day, the high less
low of six one-minute bars on the kits' trading-day clock, in ticks. The kit (R146) embeds this source verbatim (no
imports; missing bars None). A bar STARTING at a CT minute is the bar whose END is one minute later on the clock
(flip_core's convention: a slot is a bar's END time in minutes after 17:00 CT of the evening the day starts)."""


def dst_end_slot(hour, minute):
    """The clock slot of the bar STARTING at hour:minute CT (its END one minute later)."""
    m = hour * 60 + minute + 1
    return m - 1020 if m > 1020 else m + 420


def dst_ranges(h, l, slots, tick):
    """Each slot's bar's high less low in whole ticks, None where the bar is missing."""
    out = []
    for j in slots:
        if 0 <= j < len(h) and h[j] is not None and l[j] is not None:
            out.append(int(round((h[j] - l[j]) / tick)))
        else:
            out.append(None)
    return out


def dst_record(td, ranges):
    """'D' + yyyymmdd and the ranges (an empty field for a missing bar)."""
    return "D" + ",".join(["%04d%02d%02d" % tuple(td)] + ["" if r is None else str(int(r)) for r in ranges])


__all__ = ["dst_end_slot", "dst_ranges", "dst_record"]
