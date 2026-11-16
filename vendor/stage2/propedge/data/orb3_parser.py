"""ORB3's kit outputs (R102-R104; T15 item 9, D-256) into a table: `parse_orb3`.

A kit logs `OR3|HEAD` (version 3) and `OR3|END` and carries its records in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<cells>`, cells joined by '/':

* `R<yyyymmdd>,<fields>` -- one per day: the ATR and the grid's stops in ticks, then for each range of
  `orb_core.OR_MINS` `orb3_core.BLOCK3_FIELDS` and, per stop width, the offsets from the fill bar of its stop (A) and of
  1.5 and 2 times it (F15, F2), -1 for never -- a table row per day and range (`or_minutes`), the offsets turned into
  slots (`a_<i>`, `f15_<i>`, `f2_<i>`, -1 kept), the shared fields repeated;
* `D<year>,...` -- as ORB1's session cells.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields or not version 3, a missing
chunk or emit, chunks that do not add up to HEAD's orders, a malformed record, a day twice, a direction outside -1, 0,
1, a fill without a direction or before its range closes, a slot before the fill (or before the next bar when the fill
was inside its bar) or after 15:08, stops that shrink as the grid widens, a wider stop reached before a narrower one or
reached when it was not, the same for the favourable levels, records or sessions that disagree with HEAD.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

from propedge.data.manual_parsers import (UnusableRun, _kv, _lean_version, _tag, orders_from_results,
                                          prefixed_lines)
from propedge.data.regime_parser import HEAD_FIELDS, HEAD_INTS

_REC = re.compile(r"G\|e=(\d+);k=(\d+);K=(\d+);x=(.*)$")


def orb3_head(log_path: Path) -> dict[str, str]:
    from propedge.data.orb3_kit import ORB3_PREFIX

    lines = prefixed_lines(log_path, ORB3_PREFIX)
    if not any(l.startswith(ORB3_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(ORB3_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "3":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 3) in the logs: {head}")
    return head


def orb3_output_matches_kit(log_path: Path, market: str) -> None:
    head = orb3_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def _monotone(slots: list[int]) -> bool:
    """A level further out is reached no earlier than a nearer one, and only if the nearer one is."""
    for a, b in zip(slots, slots[1:]):
        if b != -1 and (a == -1 or b < a):
            return False
    return True


def parse_orb3(log_path: Path, results_path: Path, *, market: str = "NQ",
               stops: tuple[float, ...] | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per day record and range (`kind` day, `or_minutes`) and per session cell (`kind`
    session)."""
    from propedge.data import orb3_kit as k3
    from propedge.outcomes.orb3_core import BLOCK3_FIELDS, SHARED3_FIELDS
    from propedge.outcomes.orb_core import FLAT_ENTRY, OR_MINS, OR_START

    head = orb3_head(log_path)
    K = len(stops or k3.params()["stops"])
    nb = len(BLOCK3_FIELDS) + 3 * K
    width = 1 + len(SHARED3_FIELDS) + K + len(OR_MINS) * nb
    parts: dict[int, dict[int, str]] = {}
    sizes: dict[int, int] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        m = _REC.match(tag)
        if m:
            e, k, n = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if k in parts.get(e, {}):
                raise UnusableRun(f"emit {e} chunk {k} appears twice.")
            parts.setdefault(e, {})[k] = m.group(4)
            sizes[e] = n
    emits = int(head["emits"])
    if sorted(parts) != list(range(1, emits + 1)):
        raise UnusableRun(f"emits {sorted(parts)} but HEAD reports {emits}.")
    for e, ks in parts.items():
        if sorted(ks) != list(range(sizes[e])):
            raise UnusableRun(f"emit {e}: chunks {sorted(ks)} of {sizes[e]}.")
    if sum(sizes.values()) != int(head["orders"]):
        raise UnusableRun(f"the emits hold {sum(sizes.values())} chunks, HEAD reports {head['orders']} orders.")
    days, sessions, seen, noatr, records = [], [], set(), 0, 0
    for e in sorted(parts):
        for cell in "/".join(parts[e][k] for k in range(sizes[e])).split("/"):
            try:
                v = [int(x) for x in cell[1:].split(",")]
            except ValueError as exc:
                raise UnusableRun(f"malformed cell {cell!r}") from exc
            kind = cell[:1]
            if kind == "R" and len(v) == width:
                ymd = v[0]
                try:
                    day = date(ymd // 10000, ymd // 100 % 100, ymd % 100)
                except ValueError as exc:
                    raise UnusableRun(f"record {cell!r}: no such date") from exc
                atr, st = v[1], v[2:2 + K]
                if atr < 1 or min(st) < 1 or st != sorted(st):
                    raise UnusableRun(f"record {cell!r}: an ATR or the grid's stops out of range")
                shared = {"atr_ticks": atr, **{f"stop_ticks_{i}": s for i, s in enumerate(st)}}
                for r, n in enumerate(OR_MINS):
                    a = 2 + K + r * nb
                    row = dict(zip(BLOCK3_FIELDS, v[a:a + len(BLOCK3_FIELDS)]))
                    offs = v[a + len(BLOCK3_FIELDS):a + nb]
                    fs, d, op = row["fill_slot"], row["dir"], row["at_open"]
                    where = f"record {cell!r}, {n}-minute range"
                    if d not in (-1, 0, 1) or (d == 0 and fs != -1) or op not in (0, 1):
                        raise UnusableRun(f"{where}: a direction or fill flag out of range")
                    if fs == -1:
                        if any(x != -1 for x in offs):
                            raise UnusableRun(f"{where}: a passage without a fill")
                    elif not (OR_START + n < fs < FLAT_ENTRY):
                        raise UnusableRun(f"{where}: a fill outside the session")
                    lo = 0 if op else 1
                    if fs != -1 and any(x != -1 and not (lo <= x and fs + x <= FLAT_ENTRY) for x in offs):
                        raise UnusableRun(f"{where}: a passage before the walk starts or after 15:08")
                    a_s, f15, f2 = offs[0::3], offs[1::3], offs[2::3]
                    if not (_monotone(a_s) and _monotone(f15) and _monotone(f2)) or any(
                            y != -1 and (x == -1 or y < x) for x, y in zip(f15, f2)):
                        raise UnusableRun(f"{where}: passages not monotone in the level")
                    slot = lambda x: fs + x if x != -1 else -1                     # noqa: E731
                    row.update({f"a_{i}": slot(a_s[i]) for i in range(K)})
                    row.update({f"f15_{i}": slot(f15[i]) for i in range(K)})
                    row.update({f"f2_{i}": slot(f2[i]) for i in range(K)})
                    days.append({"kind": "day", "market": market, "date": day.isoformat(), "year": day.year,
                                 "or_minutes": n, **shared, **row})
                records += 1
                key = ("R", day)
            elif kind == "D" and len(v) == 6:
                y, nd, rng, vol, rdays, tr = v
                if nd < 1 or rdays > nd or min(v) < 0:
                    raise UnusableRun(f"cell {cell!r}: more days with the histories than days")
                key = ("D", y)
                sessions.append({"kind": "session", "market": market, "year": y, "days": nd,
                                 "range_ticks_sum": rng, "volume": vol, "history_days": rdays})
                noatr += nd - rdays
            else:
                raise UnusableRun(f"malformed cell {cell!r}")
            if key in seen:
                raise UnusableRun(f"cell {key} appears twice")
            seen.add(key)
    if not days:
        raise UnusableRun("no day record in the output.")
    if records != int(head["entries"]):
        raise UnusableRun(f"the output holds {records} day records, HEAD reports {head['entries']} entries.")
    full = int(head["days"]) - int(head["early"]) - int(head["noref"])
    if sum(s["days"] for s in sessions) != full:
        raise UnusableRun(f"the session cells hold {sum(s['days'] for s in sessions)} days, HEAD's full sessions are "
                          f"{full}.")
    if int(head["noatr"]) != noatr:
        raise UnusableRun(f"HEAD reports {head['noatr']} days without the histories, the cells {noatr}.")
    df = pd.concat([pd.DataFrame(days), pd.DataFrame(sessions)], ignore_index=True)
    facts = {"market": market, **{k: int(head[k]) for k in HEAD_INTS},
             "lean_version": _lean_version(log_path, results_path)}
    return df, facts


__all__ = ["orb3_head", "orb3_output_matches_kit", "parse_orb3"]
