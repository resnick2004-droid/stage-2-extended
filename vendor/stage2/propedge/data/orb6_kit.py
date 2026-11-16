"""ORB6's data-capture kits (D-276 to D-278): R108, R109 and R110 re-walk ORB3's three NQ windows (R102-R104, 2009-06 to
June 2025, development data under D-237) and record what ORB6's structural changes need -- the classic stop at the
range's far side from the hand-traded entry, the retest (limit) entry at the broken edge with its passages, and the
overnight, gap and VWAP readings at the signal (`propedge/outcomes/orb6_core.py`). No hypothesis, nothing selected;
only the day records leave (D-120).

ORB1's kit body (`propedge/data/orb_kit.py`) with ORB5's named edits re-pointed at ORB6 (the record call, HEAD's version,
the encoding with a -1 written as nothing, the record stream cut into tags) and prefix OR6. The kit embeds orb_core's
constants and helpers, orb3_core's `passages`, the four pieces of orb5_core it uses and orb6_core, without docstrings,
imports or comments, to fit QuantConnect's editor.
"""
from __future__ import annotations

import ast
import inspect
import re

from propedge.data import orb3_kit as k3
from propedge.data import orb5_kit as k5
from propedge.data import orb_kit as ok

ORB6_PREFIX = "OR6"
MARKET = "NQ"
#: each capture run and the ORB3 run whose days it re-walks (ORB5's capture of the same days beside it)
ORB6_RUNS = {"R108-orb6-NQ-0914": "R102-orb3-NQ-0914", "R109-orb6-NQ-1519": "R103-orb3-NQ-1519",
             "R110-orb6-NQ-2025": "R104-orb3-NQ-2025"}
ORB6_CAPTURES = {"R108-orb6-NQ-0914": "R105-orb5-NQ-0914", "R109-orb6-NQ-1519": "R106-orb5-NQ-1519",
                 "R110-orb6-NQ-2025": "R107-orb5-NQ-2025"}


def dates(run: str):
    return k3.dates(ORB6_RUNS[run])


def params() -> dict:
    return k3.params()


def _orb5_parts() -> str:
    from propedge.outcomes import orb5_core as o5

    consts = (f"MISSING5 = {o5.MISSING5!r}\nLATENCY = {o5.LATENCY!r}\n"
              f"SAME, CHASE, LATE_STOP = {o5.SAME!r}, {o5.CHASE!r}, {o5.LATE_STOP!r}\n")
    return consts + "\n\n".join(inspect.getsource(getattr(o5, f)) for f in ("worst_in", "_spread", "hand_entry",
                                                                             "encode_day5"))


def _no_docstrings(src: str) -> str:
    """`src` without its functions' docstrings: the kit's margin under QuantConnect's 32,000 characters counted with
    CRLF line ends (D-267); the code is unchanged, every function keeps a statement after its docstring."""
    cut: set[int] = set()
    for f in ast.walk(ast.parse(src)):
        if isinstance(f, ast.FunctionDef) and isinstance(f.body[0], ast.Expr) \
                and isinstance(f.body[0].value, ast.Constant) and isinstance(f.body[0].value.value, str):
            assert len(f.body) > 1, f.name
            cut.update(range(f.body[0].lineno, f.body[0].end_lineno + 1))
    return "".join(ln for i, ln in enumerate(src.splitlines(keepends=True), start=1) if i not in cut)


def _cores() -> str:
    from propedge.outcomes import orb3_core, orb6_core, orb_core

    consts = (f"OR_START, OR_MIN, OR_MINS, PRE_START, NONE = {orb_core.OR_START!r}, {orb_core.OR_MIN!r}, "
              f"{orb_core.OR_MINS!r}, {orb_core.PRE_START!r}, {orb_core.NONE!r}\n"
              "FLAT_ENTRY = FLAT - 2\n")
    helpers = "\n\n".join(inspect.getsource(getattr(orb_core, f)) for f in k3._ORB_CORE_PARTS)
    return _no_docstrings(k5._no_comments(consts + "\n\n" + helpers + "\n\n" + inspect.getsource(orb3_core.passages)
                                          + "\n\n" + _orb5_parts() + "\n\n" + k5._strip(orb6_core)))


def _drop_unused(text: str, body: str) -> str:
    """`text` without the top-level functions that neither it nor `body` calls and without any a later one of the same
    name replaces, to the fixpoint: the kit's margin under QuantConnect's 32,000 characters with CRLF line ends
    (D-267); nothing that runs is removed (the fake run executes the kit)."""
    while True:
        defs = [n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)]
        used = {n.id if isinstance(n, ast.Name) else n.attr for n in ast.walk(ast.parse(text + "\n" + body))
                if isinstance(n, (ast.Name, ast.Attribute))}
        last = {f.name: f for f in defs}
        dead = [f for f in defs if last[f.name] is not f or f.name not in used]
        if not dead:
            return re.sub(r"\n{4,}", "\n\n\n", text)
        cut = {i for f in dead for i in range(f.lineno, f.end_lineno + 1)}
        text = "".join(ln for i, ln in enumerate(text.splitlines(keepends=True), start=1) if i not in cut)


def preamble(run: str) -> str:
    text = k3.preamble(ORB6_RUNS[run])
    head, sep, _ = text.partition("# ---------------------------------------------------------------- orb_core's")
    assert sep, "orb3_kit's preamble changed shape"
    head = head.replace(f'PREFIX = "{k3.ORB3_PREFIX}"', f'PREFIX = "{ORB6_PREFIX}"')
    assert f'PREFIX = "{ORB6_PREFIX}"' in head and head.count("regime_core.py (its docstring removed)") == 1
    head = head.replace("regime_core.py (its docstring removed)",
                        "regime_core.py (its docstring and what this kit never calls removed)")
    return _drop_unused(head + "# ---------------------------------------------------------------- the embedded cores "
                        "(orb_core, orb3_core, orb5_core, orb6_core; no docstrings, imports, comments or uncalled "
                        "functions)\n" + _cores()
                        + "\n# ---------------------------------------------------------------- end of the embedded "
                        "cores\n", BODY)


_EDITS6 = (
    ('''            rec = day_record(o, h, l, cl, vt, ls, PARAMS, hist)''',
     '''            rec = day_record6(o, h, l, cl, vt, q, ls, PARAMS, hist)   # ORB6: what ORB6's changes need'''),
    ('''    head = (PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)''',
     '''    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)'''),
    ('''                self._recs.append(encode_day(d["td"], rec))''',
     '''                self._recs.append(encode_day5(d["td"], rec))   # a -1 written as nothing (D-267)'''),
    k5._EDITS5[3],
)
BODY = ok.BODY
for _old, _new in _EDITS6:
    assert BODY.count(_old) == 1, _old[:60]
    BODY = BODY.replace(_old, _new)
BODY = BODY.replace("# T15, D-249: ORB1's day records at actual prices, on the regime map's body",
                    "# T16, D-278: ORB6's capture records at actual prices, on ORB1's body")


__all__ = ["ORB6_PREFIX", "MARKET", "ORB6_RUNS", "ORB6_CAPTURES", "dates", "params", "preamble", "BODY"]
