"""ORB1's kit outputs (R099, R100; T15 item 9, D-249, D-250) into a table: `parse_orb`.

A kit logs `OR1|HEAD` (version 2, the four ranges' layout, D-250) and `OR1|END` and carries its records in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<cells>`, cells joined by '/':

* `R<yyyymmdd>,<fields>` -- one per day: `orb_core.SHARED_FIELDS`, then for each range of `orb_core.OR_MINS` its
  `BLOCK_FIELDS` and the first slot each bracket target (R of the kit's grid) was traded through before the stop, -1
  for none -- a table row per day and range (`or_minutes`), the shared fields repeated;
* `D<year>,<days>,<range>,<volume>,<range days>,<trailing range>` -- as the regime map's, the "range days" here the
  days with both 14-day histories.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields, a missing chunk or emit, chunks
that do not add up to HEAD's orders, a malformed record, a day twice, a direction outside -1, 0, 1, a fill without a
direction, a fill before its range closes, a fill or stop or target slot outside the session or out of order (a target
may share the fill's bar: a fill at the bar's open walks its own bar), a longer range narrower than a shorter one (the
windows are nested), records or sessions that disagree with HEAD.
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


def orb_head(log_path: Path) -> dict[str, str]:
    from propedge.data.orb_kit import ORB_PREFIX

    lines = prefixed_lines(log_path, ORB_PREFIX)
    if not any(l.startswith(ORB_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(ORB_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "2":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 2) in the logs: {head}")
    return head


def orb_output_matches_kit(log_path: Path, market: str) -> None:
    head = orb_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def parse_orb(log_path: Path, results_path: Path, *, market: str | None = None,
              rr: tuple[float, ...] | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per day record and range (`kind` day, `or_minutes`) and per session cell (`kind`
    session)."""
    from propedge.data import orb_kit as ok
    from propedge.outcomes.orb_core import BLOCK_FIELDS, FLAT_ENTRY, OR_MINS, OR_START, SHARED_FIELDS

    head = orb_head(log_path)
    mk = market or head["market"]
    rr = tuple(rr or ok.params(mk)["rr"])
    tcols = [f"target_{R:g}_slot" for R in rr]
    block = len(BLOCK_FIELDS) + len(rr)
    width = 1 + len(SHARED_FIELDS) + len(OR_MINS) * block
    parts: dict[int, dict[int, str]] = {}
    sizes: dict[int, int] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        m = _REC.match(tag)
        if m:
            e, k, K = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if k in parts.get(e, {}):
                raise UnusableRun(f"emit {e} chunk {k} appears twice.")
            parts.setdefault(e, {})[k] = m.group(4)
            sizes[e] = K
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
                shared = dict(zip(SHARED_FIELDS, v[1:1 + len(SHARED_FIELDS)]))
                if shared["stop_ticks"] < 1 or shared["atr_ticks"] < 1:
                    raise UnusableRun(f"record {cell!r}: a stop or ATR out of range")
                for i, n in enumerate(OR_MINS):
                    a = 1 + len(SHARED_FIELDS) + i * block
                    row = dict(zip(BLOCK_FIELDS, v[a:a + len(BLOCK_FIELDS)]))
                    row.update(dict(zip(tcols, v[a + len(BLOCK_FIELDS):a + block])))
                    fs, ss = row["fill_slot"], row["stop_slot"]
                    if row["dir"] not in (-1, 0, 1) or (row["dir"] == 0 and fs != -1):
                        raise UnusableRun(f"record {cell!r}, {n}-minute range: a direction out of range")
                    if fs != -1 and not (OR_START + n < fs < FLAT_ENTRY):
                        raise UnusableRun(f"record {cell!r}, {n}-minute range: a fill outside the session")
                    if fs == -1 and (ss != -1 or any(row[t] != -1 for t in tcols)):
                        raise UnusableRun(f"record {cell!r}, {n}-minute range: a stop or target without a fill")
                    if ss != -1 and not (fs <= ss <= FLAT_ENTRY):
                        raise UnusableRun(f"record {cell!r}, {n}-minute range: a stop out of order")
                    tv = [row[t] for t in tcols]
                    if any(t != -1 and not (fs <= t <= FLAT_ENTRY and (ss == -1 or t < ss)) for t in tv):
                        raise UnusableRun(f"record {cell!r}, {n}-minute range: a target out of order")
                    hit = [t for t in tv if t != -1]
                    if hit != sorted(hit) or any(x == -1 and y != -1 for x, y in zip(tv, tv[1:])):
                        raise UnusableRun(f"record {cell!r}, {n}-minute range: targets not monotone in R")
                    days.append({"kind": "day", "market": mk, "date": day.isoformat(), "year": day.year,
                                 "or_minutes": n, **shared, **row})
                widths = [r["or_ticks"] for r in days[-len(OR_MINS):] if r["rv100"] != -1]   # -1: no range
                if widths != sorted(widths):
                    raise UnusableRun(f"record {cell!r}: a longer range narrower than a shorter one")
                records += 1
                key = ("R", day)
            elif kind == "D" and len(v) == 6:
                y, nd, rng, vol, rdays, tr = v
                if nd < 1 or rdays > nd or min(v) < 0:
                    raise UnusableRun(f"cell {cell!r}: more days with the histories than days")
                key = ("D", y)
                sessions.append({"kind": "session", "market": mk, "year": y, "days": nd, "range_ticks_sum": rng,
                                 "volume": vol, "history_days": rdays})
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
    facts = {"market": mk, **{k: int(head[k]) for k in HEAD_INTS}, "lean_version": _lean_version(log_path, results_path)}
    return df, facts


__all__ = ["orb_head", "orb_output_matches_kit", "parse_orb"]
