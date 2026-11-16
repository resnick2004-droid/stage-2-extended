"""ORB5's data-capture kits (T16 item 3; D-263 to D-266): R105, R106 and R107 re-walk ORB3's three NQ windows (R102-R104,
2009-06 to June 2025, development data under D-237) and record only what ORB3's records lack -- the 0.75R, 1R, 1.25R,
3R, 5R and 8R passages per stop width, the worst price of 15:07-15:10 CT, the bid-ask spread at the fill and flatten minutes, and the entry the
operator can take by hand five minutes after each signal with its passages (`propedge/outcomes/orb5_core.py`). No
hypothesis, nothing selected; only the day records leave (D-120).

ORB1's kit body (`propedge/data/orb_kit.py`) with four named edits: each day writes `day_record5`, which also reads
each minute's spread (`q`, the regime body's ask - bid at the minute's open), encoded by `encode_day5` (a -1 written as
nothing, D-267); a year's records are one '/'-joined stream
cut into order tags of `TAG_CHARS` (a record is longer than a tag, D-266, and no tag longer than ORB1's ever left
QuantConnect); and HEAD's version is 7 (prefix OR5; 5 and 6 were D-264's and D-266's layouts, never run). The kit
embeds `regime_core`, then orb_core's constants and helpers, orb3_core's `passages` and orb5_core, verbatim but for
the modules' docstrings, imports and comments, to fit QuantConnect's editor.
"""
from __future__ import annotations

import ast
import inspect
import io
import tokenize

from propedge.data import orb3_kit as k3
from propedge.data import orb_kit as ok
from propedge.data import regime_kit as rk

ORB5_PREFIX = "OR5"
MARKET = "NQ"
#: each capture run and the ORB3 run whose days it re-walks
ORB5_RUNS = {"R105-orb5-NQ-0914": "R102-orb3-NQ-0914", "R106-orb5-NQ-1519": "R103-orb3-NQ-1519",
             "R107-orb5-NQ-2025": "R104-orb3-NQ-2025"}


def dates(run: str):
    return k3.dates(ORB5_RUNS[run])


def params() -> dict:
    return k3.params()


def _strip(module) -> str:
    src = ok._without_docstring(inspect.getsource(module))
    nodes = [n for n in ast.parse(src).body if isinstance(n, (ast.Import, ast.ImportFrom))]
    lines = src.splitlines(keepends=True)
    keep = [True] * len(lines)
    for n in nodes:
        assert n.module and n.module.startswith("propedge.outcomes"), n.module
        for i in range(n.lineno - 1, n.end_lineno):
            keep[i] = False
    return "".join(ln for ln, k in zip(lines, keep) if k)


def _no_comments(src: str) -> str:
    """`src` without its comments (tokenize's COMMENT tokens, so a '#' inside a string stays) and the lines left empty
    by them: the kit's margin under QuantConnect's 32,000 characters, which might count CRLF line ends (D-267)."""
    cut: dict[int, int] = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            cut[tok.start[0]] = tok.start[1]
    out = []
    for i, ln in enumerate(src.splitlines(keepends=True), start=1):
        if i in cut:
            kept = ln[:cut[i]].rstrip()
            if not kept:
                continue
            ln = kept + "\n"
        out.append(ln)
    return "".join(out)


def _cores() -> str:
    from propedge.outcomes import orb3_core, orb5_core, orb_core

    consts = (f"OR_START, OR_MIN, OR_MINS, PRE_START, NONE = {orb_core.OR_START!r}, {orb_core.OR_MIN!r}, "
              f"{orb_core.OR_MINS!r}, {orb_core.PRE_START!r}, {orb_core.NONE!r}\n"
              "FLAT_ENTRY = FLAT - 2                # 15:08 CT, slot 1328 (orb_core)\n")
    helpers = "\n\n".join(inspect.getsource(getattr(orb_core, f)) for f in k3._ORB_CORE_PARTS)
    return _no_comments(consts + "\n\n" + helpers + "\n\n" + inspect.getsource(orb3_core.passages) + "\n\n"
                        + _strip(orb5_core))


def preamble(run: str) -> str:
    text = k3.preamble(ORB5_RUNS[run])
    head, sep, _ = text.partition("# ---------------------------------------------------------------- orb_core's")
    assert sep, "orb3_kit's preamble changed shape"
    head = head.replace(f'PREFIX = "{k3.ORB3_PREFIX}"', f'PREFIX = "{ORB5_PREFIX}"')
    assert f'PREFIX = "{ORB5_PREFIX}"' in head
    return (head + "# ---------------------------------------------------------------- orb_core's constants and helpers, "
            "orb3_core's passages\n# ---------------------------------------------------------------- and "
            "propedge/outcomes/orb5_core.py (docstrings and imports removed)\n" + _cores()
            + "\n# ---------------------------------------------------------------- end of the embedded cores\n")


_EDITS5 = (
    ('''            rec = day_record(o, h, l, cl, vt, ls, PARAMS, hist)''',
     '''            rec = day_record5(o, h, l, cl, vt, q, ls, PARAMS, hist)   # ORB5: what ORB3's records lack'''),
    ('''    head = (PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)''',
     '''    head = (PREFIX + "|HEAD|v=7|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)'''),
    ('''                self._recs.append(encode_day(d["td"], rec))''',
     '''                self._recs.append(encode_day5(d["td"], rec))   # ORB5: a -1 written as nothing (D-267)'''),
    ('''    chunks, cur = [], ""
    for x in cells:
        if cur and len(cur) + 1 + len(x) > TAG_CHARS:
            chunks.append(cur)
            cur = x
        else:
            cur = x if not cur else cur + "/" + x
    chunks.append(cur)''',
     '''    s = "/".join(cells)                  # ORB5: one stream, cut into tags; the parser joins them back
    chunks = [s[i:i + TAG_CHARS] for i in range(0, len(s), TAG_CHARS)]'''),
)
BODY = ok.BODY
for _old, _new in _EDITS5:
    assert BODY.count(_old) == 1, _old[:60]
    BODY = BODY.replace(_old, _new)
BODY = BODY.replace("# T15, D-249: ORB1's day records at actual prices, on the regime map's body",
                    "# T16, D-264: ORB5's capture records at actual prices, on ORB1's body")


__all__ = ["ORB5_PREFIX", "MARKET", "ORB5_RUNS", "dates", "params", "preamble", "BODY"]
