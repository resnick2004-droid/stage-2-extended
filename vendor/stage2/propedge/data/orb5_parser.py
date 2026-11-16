"""ORB5's capture outputs (R105-R107; T16 item 3, D-264 to D-266) into a table: `parse_orb5`.

A kit logs `OR5|HEAD` (version 7) and `OR5|END` and carries its records in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<slice>`: each emit's cells joined by '/' and cut into slices, joined back in order
(D-266); in a record a -1 is written as nothing (D-267), so an empty field reads as -1 anywhere -- a field that can
never be -1 is range-checked below, and a new field must be too, or a lost value would pass as "never":

* `R<yyyymmdd>,<fields>` -- one per day: `orb5_core.SHARED5_FIELDS` (the ATR in ticks and the day's spreads at 15:07,
  15:08 and 15:09), then for each range of `orb_core.OR_MINS` `orb5_core.BLOCK5_FIELDS`, per stop width of the grid
  the offsets of 0.75, 1, 1.25, 3, 5 and 8 times the stop from the fill bar, `orb5_core.LAT_FIELDS` (the hand-traded
  entry, D-266) and, per stop width, that entry's offsets of its own stop and of 0.75, 1, 1.25, 1.5, 2, 3, 5 and 8
  times it from its bar (-1 for never) -- a table row per day and range (`or_minutes`), the offsets turned into slots
  (`f075_<i>`, `f1_<i>`, `f125_<i>`, `f3_<i>`, `f5_<i>`, `f8_<i>`, `lat_a_<i>`, `lat_f075_<i>` ... `lat_f8_<i>`, -1
  kept).
  `worst_flat_ticks` and `lat_worst_ticks` are signed distances from their fills, negative when against the trade
  (MISSING5 without a bar); spreads are in tenths of the micro's tick, -1 where none was recorded;
* `D<year>,...` -- as ORB1's session cells.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields or not version 7, a missing chunk
or emit, chunks that do not add up to HEAD's orders, a malformed record, a day twice, a direction outside -1, 0, 1, a fill
without a direction or before its range closes, an at-open flag other than 0 or 1, a passage before the walk starts (the
fill bar itself only when the fill was at its open) or after 15:08, a farther level reached before a nearer one (across
R or across stop widths), a spread below -1, an unfilled block carrying a close, a worst price or a spread, records or
sessions that disagree with HEAD; a hand-traded entry of an unknown kind, without the original fill, missing when the
original fill comes after the order works, the same entry on another bar or disagreeing with the original's record, a chase not at its bar's open, a chase or late stop before the
order could work, or its passages before the walk starts, after 15:08 or out of order.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

from propedge.data.manual_parsers import (UnusableRun, _kv, _lean_version, _tag, orders_from_results,
                                          prefixed_lines)
from propedge.data.orb3_parser import _monotone
from propedge.data.regime_parser import HEAD_FIELDS, HEAD_INTS

_REC = re.compile(r"G\|e=(\d+);k=(\d+);K=(\d+);x=(.*)$")


def orb5_head(log_path: Path) -> dict[str, str]:
    from propedge.data.orb5_kit import ORB5_PREFIX

    lines = prefixed_lines(log_path, ORB5_PREFIX)
    if not any(l.startswith(ORB5_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(ORB5_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "7":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 7) in the logs: {head}")
    return head


def orb5_output_matches_kit(log_path: Path, market: str) -> None:
    head = orb5_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def parse_orb5(log_path: Path, results_path: Path, *, market: str = "NQ",
               stops: tuple[float, ...] | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per day record and range (`kind` day, `or_minutes`) and per session cell (`kind`
    session)."""
    from propedge.data import orb5_kit as k5
    from propedge.outcomes.orb5_core import (ADD_RR, BLOCK5_FIELDS, CHASE, LAT_FIELDS, LAT_RR, LATE_STOP, LATENCY,
                                             MISSING5, NONE, SAME, SHARED5_FIELDS, rr_name)
    from propedge.outcomes.orb_core import FLAT_ENTRY, OR_MINS, OR_START

    head = orb5_head(log_path)
    K = len(stops or k5.params()["stops"])
    nr = len(ADD_RR)
    same_at = [1 + LAT_RR.index(R) for R in ADD_RR]           # where the original's passages sit in the hand walk
    nl = 1 + len(LAT_RR)
    nb = len(BLOCK5_FIELDS) + nr * K + len(LAT_FIELDS) + nl * K
    lat_empty = [NONE, NONE, 0, 0, 0, MISSING5, 0, 0, NONE, NONE]
    ns = len(SHARED5_FIELDS)
    width = 1 + ns + len(OR_MINS) * nb
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
        for cell in "".join(parts[e][k] for k in range(sizes[e])).split("/"):
            try:
                v = [int(x) if x else NONE for x in cell[1:].split(",")]
            except ValueError as exc:
                raise UnusableRun(f"malformed cell {cell!r}") from exc
            kind = cell[:1]
            if kind == "R" and len(v) == width:
                ymd = v[0]
                try:
                    day = date(ymd // 10000, ymd // 100 % 100, ymd % 100)
                except ValueError as exc:
                    raise UnusableRun(f"record {cell!r}: no such date") from exc
                shared = dict(zip(SHARED5_FIELDS, v[1:1 + ns]))
                if shared["atr_ticks"] < 1 or any(x < -1 for x in v[2:1 + ns]):
                    raise UnusableRun(f"record {cell!r}: an ATR or a spread out of range")
                for r, n in enumerate(OR_MINS):
                    a = 1 + ns + r * nb
                    row = dict(zip(BLOCK5_FIELDS, v[a:a + len(BLOCK5_FIELDS)]))
                    offs = v[a + len(BLOCK5_FIELDS):a + len(BLOCK5_FIELDS) + nr * K]
                    b = a + len(BLOCK5_FIELDS) + nr * K
                    lat = dict(zip(LAT_FIELDS, v[b:b + len(LAT_FIELDS)]))
                    loffs = v[b + len(LAT_FIELDS):a + nb]
                    fs, d, op = row["fill_slot"], row["dir"], row["at_open"]
                    where = f"record {cell!r}, {n}-minute range"
                    if d not in (-1, 0, 1) or (d == 0 and fs != -1) or op not in (0, 1):
                        raise UnusableRun(f"{where}: a direction or at-open flag out of range")
                    if fs == -1:
                        if any(x != -1 for x in offs) or op or row["close_ticks"] or row["worst_flat_ticks"] != \
                                MISSING5 or row["spread_fill_tenths"] != -1 or row["spread_after_fill_tenths"] != -1:
                            raise UnusableRun(f"{where}: an unfilled block carrying a passage, close, worst or spread")
                    elif not (OR_START + n < fs < FLAT_ENTRY):
                        raise UnusableRun(f"{where}: a fill outside the session")
                    lo = 0 if op else 1
                    if fs != -1 and any(x != -1 and not (lo <= x and fs + x <= FLAT_ENTRY) for x in offs):
                        raise UnusableRun(f"{where}: a passage before the walk starts or after 15:08")
                    if row["spread_fill_tenths"] < -1 or row["spread_after_fill_tenths"] < -1:
                        raise UnusableRun(f"{where}: a negative spread")
                    per = [offs[i * nr:(i + 1) * nr] for i in range(K)]          # per stop width, `ADD_RR`
                    if not all(_monotone(p) for p in per) or not all(_monotone([p[j] for p in per])
                                                                     for j in range(nr)):
                        raise UnusableRun(f"{where}: passages not monotone in the level")
                    lk, ls, lop = lat["lat_kind"], lat["lat_slot"], lat["lat_at_open"]
                    live = OR_START + n + LATENCY                              # the order works from this bar's end
                    lper = [loffs[i * nl:(i + 1) * nl] for i in range(K)]      # per width: A, then `LAT_RR`
                    if lk not in (-1, SAME, CHASE, LATE_STOP) or lop not in (0, 1) or (lk != -1 and fs == -1):
                        raise UnusableRun(f"{where}: a hand-traded entry of an unknown kind or without a fill")
                    if lat["lat_spread_fill_tenths"] < -1 or lat["lat_spread_after_fill_tenths"] < -1:
                        raise UnusableRun(f"{where}: a negative spread")
                    if lk == -1:
                        if fs > live:
                            raise UnusableRun(f"{where}: no hand-traded entry though the original fills after the "
                                              "order works")
                        if v[b:b + len(LAT_FIELDS)] != lat_empty or any(x != -1 for x in loffs):
                            raise UnusableRun(f"{where}: a hand-traded passage or field without the entry")
                    elif lk == SAME:
                        if not (fs > live and ls == fs and lop == op and lat["lat_gap_ticks"] == 0
                                and lat["lat_close_ticks"] == row["close_ticks"]
                                and lat["lat_worst_ticks"] == row["worst_flat_ticks"]
                                and lat["lat_spread_fill_tenths"] == row["spread_fill_tenths"]
                                and lat["lat_spread_after_fill_tenths"] == row["spread_after_fill_tenths"]
                                and all([p[j] for j in same_at] == q for p, q in zip(lper, per))):
                            raise UnusableRun(f"{where}: a hand-traded entry 'the same' that is not the original")
                    elif not (fs <= live < ls < FLAT_ENTRY) or (lk == CHASE and not lop):
                        raise UnusableRun(f"{where}: a chase or late stop on the wrong bar")
                    llo = 0 if lop else 1
                    if lk != -1 and any(x != -1 and not (llo <= x and ls + x <= FLAT_ENTRY) for x in loffs):
                        raise UnusableRun(f"{where}: a hand-traded passage before its walk starts or after 15:08")
                    if not all(_monotone(p[1:]) for p in lper) or not all(
                            _monotone([p[j] for p in lper]) for j in range(nl)):
                        raise UnusableRun(f"{where}: the hand-traded passages not monotone in the level")
                    slot = lambda x: fs + x if x != -1 else -1                     # noqa: E731
                    for i in range(K):
                        for j, R in enumerate(ADD_RR):
                            row[f"{rr_name(R)}_{i}"] = slot(per[i][j])
                    row.update(lat)
                    names = ["a"] + [rr_name(R) for R in LAT_RR]
                    for i in range(K):
                        for name, x in zip(names, lper[i]):
                            row[f"lat_{name}_{i}"] = ls + x if x != -1 else -1
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


__all__ = ["orb5_head", "orb5_output_matches_kit", "parse_orb5"]
