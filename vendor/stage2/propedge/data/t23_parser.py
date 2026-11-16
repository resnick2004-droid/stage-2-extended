"""T23's capture output (R147, R148; D-416) into a table: one `walk` row per (day, slot, delay, side) with each
bracket's outcome ('t', 's', 'f'), minutes from the entry bar, the stop's gap in ticks, the tie mark and the end's P&L in
ticks; one `day` row per trading day with its kind and the A3 sign per slot.

Refused (`UnusableRun`): anything `flip_head` / `_chunks` refuse of the HEAD and the chunks; a malformed record; an index
out of range; a walk without exactly one outcome per bracket; a walk before its day record's day; a day twice; counts
that disagree with HEAD's `entries`, `records` or `dayrecs`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from propedge.data.flip_parser import HEAD_INTS, _chunks, flip_head
from propedge.data.manual_parsers import UnusableRun, _lean_version

_DAY = re.compile(r"^D(\d{6}),([nboex]),([+\-0.]*)$")
_WALK = re.compile(r"^W(\d+),(\d+),([+\-]),(\d+):(.*)$")
_OUT = re.compile(r"^(t|s|f)(\d+)(?:(u)|g(\d+)|x(-?\d+))?$")


def parse_t23(log_path: Path, results_path: Path, q: dict) -> tuple[pd.DataFrame, dict]:
    head = flip_head(log_path, q)
    slots, labels, delays = q["slots"], q["slot_labels"], q["delays"]
    nb = len(q["brackets"])
    rows, days, day = [], set(), None
    pending: list[tuple] = []

    def flush(td: str) -> None:
        for si, dl, side, j0, outs in pending:
            r = {"kind": "walk", "date": td, "decision_ct": labels[si], "decision_slot_minutes": slots[si], "delay": dl,
                 "side": side, "entry_slot": j0}
            for b, (k, m, u, g, x) in enumerate(outs):
                r.update({f"o{b}": k, f"m{b}": m, f"u{b}": u, f"g{b}": g, f"x{b}": x})
            rows.append(r)
        pending.clear()

    for blob in _chunks(results_path, head):
        for rec in blob.split("/"):
            mw = _WALK.match(rec)
            if mw:
                si, dl, side, j0 = int(mw.group(1)), int(mw.group(2)), (1 if mw.group(3) == "+" else -1), int(mw.group(4))
                if not (0 <= si < len(slots) and dl in delays):
                    raise UnusableRun(f"walk {rec[:60]!r}: an index out of range")
                parts = mw.group(5).split(";")
                if len(parts) != nb:
                    raise UnusableRun(f"walk {rec[:60]!r}: {len(parts)} outcomes, not {nb}")
                outs = []
                for p in parts:
                    mo = _OUT.match(p)
                    if not mo:
                        raise UnusableRun(f"walk {rec[:60]!r}: a malformed outcome {p!r}")
                    k, m = mo.group(1), int(mo.group(2))
                    if (mo.group(3) and k != "s") or (mo.group(4) and k != "s") or (mo.group(5) is not None and k != "f") \
                            or (k == "f" and mo.group(5) is None):
                        raise UnusableRun(f"walk {rec[:60]!r}: an outcome's marks do not fit it ({p!r})")
                    outs.append((k, m, bool(mo.group(3)), int(mo.group(4) or 0),
                                 int(mo.group(5)) if mo.group(5) is not None else 0))
                pending.append((si, dl, side, j0, outs))
                continue
            md = _DAY.match(rec)
            if not md:
                raise UnusableRun(f"malformed record {rec[:60]!r}")
            ymd = md.group(1)
            td = f"20{ymd[:2]}-{ymd[2:4]}-{ymd[4:]}"
            if td in days:
                raise UnusableRun(f"the day {td} twice")
            if len(md.group(3)) != len(slots):
                raise UnusableRun(f"day {td}: {len(md.group(3))} A3 signs, not {len(slots)}")
            if md.group(2) in "oex" and pending:
                raise UnusableRun(f"day {td} ({md.group(2)}) carries walks")
            days.add(td)
            flush(td)
            a3 = {f"a3_{i}": (None if ch == "." else (1 if ch == "+" else (-1 if ch == "-" else 0)))
                  for i, ch in enumerate(md.group(3))}
            rows.append({"kind": "day", "date": td, "day_kind": md.group(2), **a3})
    if pending:
        raise UnusableRun("walks after the last day record")
    df = pd.DataFrame(rows)
    walks = int((df["kind"] == "walk").sum()) if len(df) else 0
    nday = int((df["kind"] == "day").sum()) if len(df) else 0
    for name, got in (("entries", walks), ("records", walks), ("dayrecs", nday)):
        if int(head[name]) != got:
            raise UnusableRun(f"HEAD's {name} is {head[name]}; the output holds {got}.")
    if not walks:
        raise UnusableRun("no walk record in the output.")
    ints = tuple(HEAD_INTS) + tuple(q.get("head_extra") or ())
    facts = {k: int(head[k]) for k in ints}
    facts.update({k: str(head[k]) for k in (q.get("head_text") or ())})
    facts.update({"market": head["market"], "version": int(head["v"]), "time_unit": "minute",
                  "lean_version": _lean_version(log_path, results_path)})
    return df, facts


__all__ = ["parse_t23"]
