"""Per-event measurements for the pre-release drift family K (D-164; 2B F-032), in plain Python, shared by
the repository and the kits.

`config/effect_atlas.yaml` (amendment_d164) fixes the definitions. The QuantConnect kits embed this module's
source verbatim (`propedge/data/qc_algorithms.release_preamble`); tests compute the same numbers on synthetic
bars. Only these per-event numbers leave the cloud (D-120).

A release at clock minute r (Chicago, the data's time zone). Bars are keyed by the minute of day at which they
END. The pre-release return runs from the bar ending at r - PRE_MIN to the bar ending at r - PRE_END_MIN, the
last bar that closes strictly before the release; the post-release return runs from that bar to the bar ending
at r + POST_MIN. When the exact bar is missing, the latest earlier bar within GRACE minutes is used and the
offset is reported (a, b, e), so the screen can exclude events that leaned on a substitute.
"""
from math import log as _ln   # natural log; aliased so it is never mistaken for a log call

PRE_MIN = 30        # the pre-release window starts at the bar ending r - 30 (Kurov et al. 2018: [t-30 min, ...])
PRE_END_MIN = 1     # ... and ends at the bar ending r - 1, the last close strictly before the release second
POST_MIN = 5        # the release move: to the bar ending r + 5 (their [t - 5 s, t + 5 min])
GRACE = 3           # a missing bar may be replaced by the latest earlier one within this many minutes
KEYS = ("prd", "post", "nb", "a", "b", "e", "p")


def _pick(closes, target):
    """The close of the bar ending at `target`, else the latest earlier bar within GRACE minutes.
    Returns (close, offset) or (None, None)."""
    for off in range(0, GRACE + 1):
        c = closes.get(target - off)
        if c is not None:
            return c, off
    return None, None


def event_measures(closes, r):
    """`closes`: {minute of day at which the bar ENDS: close} for one contract on the event day; `r`: the release
    minute of day. Returns the per-event dict: prd and post in percent (100 x ln ratio), nb = bars present in
    [r - PRE_MIN, r + POST_MIN], the offsets a, b, e (minutes early of the three closes used), p = the pre-end
    close (the price level, for tick conversion)."""
    out = {"prd": None, "post": None, "nb": 0, "a": None, "b": None, "e": None, "p": None}
    lo, hi = r - PRE_MIN, r + POST_MIN
    out["nb"] = sum(1 for m in closes if lo <= m <= hi)
    c0, a = _pick(closes, r - PRE_MIN)
    c1, b = _pick(closes, r - PRE_END_MIN)
    c2, e = _pick(closes, r + POST_MIN)
    out["a"], out["b"], out["e"] = a, b, e
    if c1 is not None and c1 > 0:
        out["p"] = c1
    if c0 is not None and c1 is not None and c0 > 0 and c1 > 0:
        out["prd"] = 100.0 * _ln(c1 / c0)
    if c1 is not None and c2 is not None and c1 > 0 and c2 > 0:
        out["post"] = 100.0 * _ln(c2 / c1)
    return out
