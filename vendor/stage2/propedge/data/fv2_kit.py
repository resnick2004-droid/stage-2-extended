"""FV2's data-capture kits (D-279, D-282, D-283): R111 to R116 re-walk ORB3's three NQ windows (R102-R104, 2009-06 to
June 2025, development data under D-237), each in two so no run nears QuantConnect's 10,000 orders, and record what JJ
Simon's own rules need -- per session its fair value, every trigger with its entries at the operator's latencies, and
the unconditional entries of D-277's drift benchmark (`propedge/outcomes/fv2_core.py`). No hypothesis, nothing
selected; only the day records leave (D-120).

ORB1's kit body (`propedge/data/orb_kit.py`) with ORB6's named edits re-pointed at FV2 (the record call, HEAD's version,
the encoding with a -1 written as nothing, the record stream cut into tags), ORB3's preamble with the run's own window,
and prefix FV2. The kit embeds orb_core's constants and helpers, orb3_core's `passages`, the pieces of orb5_core it uses
and fv2_core, without docstrings, imports, comments or the functions it never calls.
"""
from __future__ import annotations

from datetime import date

from propedge.data import orb3_kit as k3
from propedge.data import orb5_kit as k5
from propedge.data import orb6_kit as k6
from propedge.data import orb_kit as ok

FV2_PREFIX = "FV2"
MARKET = "NQ"
#: each run: the ORB3 run whose days it re-walks, and its warm-up, start and end
FV2_RUNS = {
    "R111-fv2-NQ-0911": ("R102-orb3-NQ-0914", "2009-04-20", "2009-06-01", "2011-12-31"),
    "R112-fv2-NQ-1214": ("R102-orb3-NQ-0914", "2011-11-14", "2012-01-01", "2014-12-31"),
    "R113-fv2-NQ-1517": ("R103-orb3-NQ-1519", "2014-11-17", "2015-01-01", "2017-12-31"),
    "R114-fv2-NQ-1819": ("R103-orb3-NQ-1519", "2017-11-13", "2018-01-01", "2019-12-31"),
    "R115-fv2-NQ-2022": ("R104-orb3-NQ-2025", "2019-11-18", "2020-01-01", "2022-12-31"),
    "R116-fv2-NQ-2325": ("R104-orb3-NQ-2025", "2022-11-14", "2023-01-01", "2025-06-30"),
}


def dates(run: str) -> tuple[date, date, date]:
    return tuple(date.fromisoformat(x) for x in FV2_RUNS[run][1:])


def params() -> dict:
    return k3.params()


def _orb5_parts() -> str:
    from propedge.outcomes import orb5_core as o5

    import inspect

    return f"MISSING5 = {o5.MISSING5!r}\n" + "\n\n".join(inspect.getsource(getattr(o5, f))
                                                         for f in ("worst_in", "_spread", "encode_day5"))


def _cores() -> str:
    import inspect

    from propedge.outcomes import fv2_core, orb3_core, orb_core

    consts = (f"OR_START, OR_MIN, OR_MINS, PRE_START, NONE = {orb_core.OR_START!r}, {orb_core.OR_MIN!r}, "
              f"{orb_core.OR_MINS!r}, {orb_core.PRE_START!r}, {orb_core.NONE!r}\n"
              "FLAT_ENTRY = FLAT - 2\n")
    helpers = "\n\n".join(inspect.getsource(getattr(orb_core, f)) for f in k3._ORB_CORE_PARTS)
    return k6._no_docstrings(k5._no_comments(consts + "\n\n" + helpers + "\n\n" + inspect.getsource(orb3_core.passages)
                                             + "\n\n" + _orb5_parts() + "\n\n" + k5._strip(fv2_core)))


def preamble(run: str) -> str:
    orb3, _, start, end = FV2_RUNS[run]
    text = k3.preamble(orb3)
    head, sep, _ = text.partition("# ---------------------------------------------------------------- orb_core's")
    assert sep, "orb3_kit's preamble changed shape"
    _, w0, w1 = k3.dates(orb3)
    s0, s1 = date.fromisoformat(start), date.fromisoformat(end)
    for old, new in ((f'PREFIX = "{k3.ORB3_PREFIX}"', f'PREFIX = "{FV2_PREFIX}"'),
                     (f"WIN_START = ({w0.year}, {w0.month}, {w0.day})", f"WIN_START = ({s0.year}, {s0.month}, {s0.day})"),
                     (f"WIN_END = ({w1.year}, {w1.month}, {w1.day})", f"WIN_END = ({s1.year}, {s1.month}, {s1.day})"),
                     ("regime_core.py (its docstring removed)",
                      "regime_core.py (its docstring and what this kit never calls removed)")):
        assert head.count(old) == 1, old
        head = head.replace(old, new)
    return k6._drop_unused(head + "# ---------------------------------------------------------------- the embedded cores "
                           "(orb_core, orb3_core, orb5_core, fv2_core; no docstrings, imports, comments or uncalled "
                           "functions)\n" + _cores()
                           + "\n# ---------------------------------------------------------------- end of the embedded "
                           "cores\n", BODY)


_EDITS_FV2 = (
    ('''            rec = day_record(o, h, l, cl, vt, ls, PARAMS, hist)''',
     '''            rec = day_record_fv2(o, h, l, cl, vt, q, ls, PARAMS, hist)   # FV2: JJ Simon's own rules'''),
    ('''    head = (PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)''',
     '''    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)'''),
    ('''                self._recs.append(encode_day(d["td"], rec))''',
     '''                self._recs.append(encode_day5(d["td"], rec))   # a -1 written as nothing (D-267)'''),
    k5._EDITS5[3],
)
BODY = ok.BODY
for _old, _new in _EDITS_FV2:
    assert BODY.count(_old) == 1, _old[:60]
    BODY = BODY.replace(_old, _new)
BODY = BODY.replace("# T15, D-249: ORB1's day records at actual prices, on the regime map's body",
                    "# T16, D-283: FV2's capture records at actual prices, on ORB1's body")


__all__ = ["FV2_PREFIX", "MARKET", "FV2_RUNS", "dates", "params", "preamble", "BODY"]
