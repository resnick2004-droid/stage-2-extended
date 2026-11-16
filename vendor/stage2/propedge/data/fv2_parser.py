"""FV2's capture outputs (R111-R116; D-283) into a table: `parse_fv2`.

A kit logs `FV2|HEAD` (version 1) and `FV2|END` and carries its records in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<slice>`: each emit's cells joined by '/' and cut into slices, joined back in order;
in a record a -1 is written as nothing, so an empty field reads as -1 (every field that can never be -1 is
range-checked below):

* `R<yyyymmdd>,<fields>` -- one per day, of variable length: the ATR and the base stop in ticks, then per session of
  `fv2_core.SESSIONS` its `SESSION_FIELDS`, its signals (`SIGNAL_FIELDS`, the first latency's `FULL_FIELDS`, each other
  latency's `SHORT_FIELDS`) and its benchmark slots (`BENCH_FIELDS`) -- a `day` row, a `fvsession` row per session, a
  `signal` row per signal (offsets turned into slots, -1 kept; codes as three digits: 1R, 1.5R, fair value) and a
  `bench` row per slot and side (`side` +1 long, -1 short);
* `D<year>,...` -- as ORB1's session cells.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields or not version 1, a missing
chunk or emit, chunks that do not add up to HEAD's orders, a malformed record or one whose sessions do not add up to its
length, a day twice, an absent session carrying a field, a signal outside its session's window, out of time order, of
the wrong phase for its time, a continuation against the opening candle (a reversion's direction needs the zone, which
the record does not carry), with no trigger, short of the room its phase needs, or more of them than the cap, an entry
before its latency or a passage before it or after 15:08, targets out of order, a malformed outcome code,
a benchmark entry not after its slot, a spread below -1, records or sessions that disagree with HEAD.
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


def fv2_head(log_path: Path) -> dict[str, str]:
    from propedge.data.fv2_kit import FV2_PREFIX

    lines = prefixed_lines(log_path, FV2_PREFIX)
    if not any(l.startswith(FV2_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(FV2_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "1":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 1) in the logs: {head}")
    return head


def fv2_output_matches_kit(log_path: Path, market: str) -> None:
    head = fv2_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def _codes(x: int, where: str) -> str:
    s = str(x)
    if len(s) != 4 or s[0] != "1" or set(s[1:]) - set("0129"):
        raise UnusableRun(f"{where}: a malformed outcome code {x}")
    return s[1:]


def _day_rows(day: date, v: list[int], market: str) -> list[dict]:
    """One record's rows, every field checked."""
    from propedge.outcomes.fv2_core import (BENCH, CONT_MIN, FULL_FIELDS, LATS, MAX_SIGNALS, MISSING_FV, ROOM_MIN,
                                            SESSION_FIELDS, SESSIONS, SHORT_FIELDS, SIGNAL_FIELDS)
    from propedge.outcomes.orb_core import FLAT_ENTRY, NONE

    where = f"record {day}"
    nf, ns_ = len(FULL_FIELDS), len(SHORT_FIELDS)
    nsig = len(SIGNAL_FIELDS) + nf + ns_ * (len(LATS) - 1)
    if len(v) < 2 or v[0] < 1 or v[1] < 1:
        raise UnusableRun(f"{where}: an ATR or base stop out of range")
    rows = [{"kind": "day", "market": market, "date": day.isoformat(), "year": day.year, "atr_ticks": v[0],
             "base_stop_ticks": v[1]}]
    p = 2
    base = {"market": market, "date": day.isoformat(), "year": day.year}
    for name, s, window, _ in SESSIONS:
        w = f"{where}, {name}"
        if p + len(SESSION_FIELDS) > len(v):
            raise UnusableRun(f"{w}: the record ends inside a session")
        hd = dict(zip(SESSION_FIELDS, v[p:p + len(SESSION_FIELDS)]))
        p += len(SESSION_FIELDS)
        n = hd["signals"]
        if hd["present"] not in (0, 1) or hd["open_dir"] not in (-1, 0, 1) or not (0 <= n <= MAX_SIGNALS) \
                or hd["signals_beyond_cap"] < 0 or (hd["signals_beyond_cap"] and n < MAX_SIGNALS):
            raise UnusableRun(f"{w}: a session header out of range {hd}")
        if not hd["present"] and any(hd.values()):
            raise UnusableRun(f"{w}: an absent session carrying a field")
        if hd["present"] and (hd["stop_ticks"] < v[1] or hd["open_body_ticks"] < 0):
            raise UnusableRun(f"{w}: a stop below the base stop or a negative opening body")
        rows.append({"kind": "fvsession", **base, "session": name, **hd})
        last = s
        for i in range(n):
            if p + nsig > len(v):
                raise UnusableRun(f"{w}: the record ends inside a signal")
            g = v[p:p + nsig]
            p += nsig
            sig = dict(zip(SIGNAL_FIELDS, g[:len(SIGNAL_FIELDS)]))
            slot, phase, d = sig["slot"], sig["phase"], sig["dir"]
            if not (last < slot <= s + window and slot < FLAT_ENTRY) or d not in (-1, 1) \
                    or sig["trigger_bits"] not in (1, 2, 3):
                raise UnusableRun(f"{w}: a signal out of its window, out of order, or without a trigger {sig}")
            if phase == 0 and not (slot <= s + CONT_MIN and d == hd["open_dir"]):
                raise UnusableRun(f"{w}: a continuation after the first minutes or against the opening candle")
            if phase == 1 and not (slot > s + CONT_MIN and sig["fv_ticks"] + 1e-9 >= ROOM_MIN * hd["stop_ticks"]):
                raise UnusableRun(f"{w}: a reversion in the first minutes or short of its room")
            if phase not in (0, 1):
                raise UnusableRun(f"{w}: a phase out of range")
            last = slot
            full = dict(zip(FULL_FIELDS, g[len(SIGNAL_FIELDS):len(SIGNAL_FIELDS) + nf]))
            row = {"kind": "signal", **base, "session": name, "idx": i, **sig}
            off = full["bar"]
            if off == NONE:
                if [full[k] for k in FULL_FIELDS] != [NONE, 0, NONE, 0, NONE, NONE, NONE, NONE, 0, MISSING_FV]:
                    raise UnusableRun(f"{w}: an entry that never filled carrying a field")
                bar = NONE
            else:
                bar = slot + off
                if off < LATS[0] + 1 or bar >= FLAT_ENTRY or full["spread_tenths"] < -1:
                    raise UnusableRun(f"{w}: an entry before its latency, after 15:07 or a spread below -1")
                for k in ("a", "f1", "f15", "ffv"):
                    x = full[k]
                    if x != NONE and not (0 <= x and bar + x <= FLAT_ENTRY):
                        raise UnusableRun(f"{w}: a passage before its entry or after 15:08")
                if full["f1"] != NONE and full["f15"] != NONE and full["f15"] < full["f1"]:
                    raise UnusableRun(f"{w}: 1.5R traded through before 1R")
                if full["f1"] == NONE and full["f15"] != NONE:
                    raise UnusableRun(f"{w}: 1.5R traded through but not 1R")
                if full["fv_from_entry_ticks"] <= 0 and full["ffv"] != NONE:
                    raise UnusableRun(f"{w}: a fair-value passage with fair value behind the entry")
            row.update({"bar": bar, "entry_ticks": full["entry_ticks"], "spread_tenths": full["spread_tenths"],
                        "fv_from_entry_ticks": full["fv_from_entry_ticks"], "close_ticks": full["close_ticks"],
                        "worst_ticks": full["worst_ticks"]})
            for k in ("a", "f1", "f15", "ffv"):
                row[k] = bar + full[k] if bar != NONE and full[k] != NONE else NONE
            q = len(SIGNAL_FIELDS) + nf
            for L in LATS[1:]:
                et, cd = g[q], g[q + 1]
                q += ns_
                row[f"entry_ticks_l{L}"] = et
                row[f"codes_l{L}"] = _codes(cd, w)
            rows.append(row)
        for slot in BENCH[name]:
            if p + 8 > len(v):
                raise UnusableRun(f"{w}: the record ends inside a benchmark slot")
            j1, close, wl, ws, fl, fs, cl, cs = v[p:p + 8]
            p += 8
            cl_, cs_ = _codes(cl, w), _codes(cs, w)
            if j1 == NONE:
                if (close, wl, ws, fl, fs) != (0, MISSING_FV, MISSING_FV, 0, 0) or cl_ != "999" or cs_ != "999":
                    raise UnusableRun(f"{w}: an empty benchmark slot carrying a field")
                continue
            if not (slot < j1 < FLAT_ENTRY):
                raise UnusableRun(f"{w}: a benchmark entry not after its slot {slot} or after 15:07")
            for side, wo, fv, cd in ((1, wl, fl, cl_), (-1, ws, fs, cs_)):
                if "9" in cd[:2] or (cd[2] == "9") != (fv <= 0):
                    raise UnusableRun(f"{w}: benchmark codes with a bracket missing or one where there is none")
                rows.append({"kind": "bench", **base, "session": name, "bench_after": slot, "side": side,
                             "bench_slot": j1, "bench_close_ticks": side * close, "bench_worst_ticks": wo,
                             "bench_fv_ticks": fv, "c_1": int(cd[0]), "c_15": int(cd[1]), "c_fv": int(cd[2])})
    if p != len(v):
        raise UnusableRun(f"{where}: {len(v) - p} fields left over after the last session")
    return rows


def parse_fv2(log_path: Path, results_path: Path, *, market: str = "NQ") -> tuple[pd.DataFrame, dict]:
    """(table, facts): `day`, `fvsession`, `signal` and `bench` rows per day record, and the session cells."""
    head = fv2_head(log_path)
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
    rows, sessions, seen, noatr, records = [], [], set(), 0, 0
    for e in sorted(parts):
        for cell in "".join(parts[e][k] for k in range(sizes[e])).split("/"):
            try:
                v = [int(x) if x else -1 for x in cell[1:].split(",")]
            except ValueError as exc:
                raise UnusableRun(f"malformed cell {cell[:60]!r}") from exc
            kind = cell[:1]
            if kind == "R":
                ymd = v[0]
                try:
                    day = date(ymd // 10000, ymd // 100 % 100, ymd % 100)
                except ValueError as exc:
                    raise UnusableRun(f"record {cell[:40]!r}: no such date") from exc
                rows += _day_rows(day, v[1:], market)
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
                raise UnusableRun(f"malformed cell {cell[:60]!r}")
            if key in seen:
                raise UnusableRun(f"cell {key} appears twice")
            seen.add(key)
    if not records:
        raise UnusableRun("no day record in the output.")
    if records != int(head["entries"]):
        raise UnusableRun(f"the output holds {records} day records, HEAD reports {head['entries']} entries.")
    full = int(head["days"]) - int(head["early"]) - int(head["noref"])
    if sum(s["days"] for s in sessions) != full:
        raise UnusableRun(f"the session cells hold {sum(s['days'] for s in sessions)} days, HEAD's full sessions are "
                          f"{full}.")
    if int(head["noatr"]) != noatr:
        raise UnusableRun(f"HEAD reports {head['noatr']} days without the histories, the cells {noatr}.")
    df = pd.concat([pd.DataFrame(rows), pd.DataFrame(sessions)], ignore_index=True)
    facts = {"market": market, **{k: int(head[k]) for k in HEAD_INTS},
             "lean_version": _lean_version(log_path, results_path)}
    return df, facts


__all__ = ["fv2_head", "fv2_output_matches_kit", "parse_fv2"]
