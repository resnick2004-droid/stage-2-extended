"""FV3's capture outputs into a table: `parse_fv3`.

A kit logs `FV3|HEAD` (version 1) and `FV3|END` and carries its records in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<slice>`: each emit's cells joined by '/' and cut into slices, joined back in order;
in a record a -1 is written as nothing, so an empty field reads as -1 (every field that can never be -1 is
range-checked below):

* `R<yyyymmdd>,<fields>` -- one per day, of variable length: the ATR, the base stop in ticks and the news-day flag,
  then per session of `fv3_core.SESSIONS` its `SESSION_FIELDS`, its signals (`SIGNAL_FIELDS`, the first latency's
  `FULL_HEAD`, its two profiles, `FULL_TAIL`, each other latency's `SHORT_FIELDS`) and its benchmark slots
  (`BENCH_HEAD`, per side `BENCH_SIDE` and two profiles) -- a `day` row, a `fvsession` row per session, a `signal`
  row per signal (offsets turned into slots, -1 kept; the profiles as 'off:ticks;...' text, offsets from the entry
  bar; codes as three digits: 1R, 1.5R, fair value) and a `bench` row per slot and side (`side` +1 long, -1 short);
* `D<year>,...` -- as ORB1's session cells.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields or not version 1, a missing
chunk or emit, chunks that do not add up to HEAD's orders, a malformed record or one whose sessions do not add up to its
length, a day twice, an absent session carrying a field, a signal outside its session's window, out of time order, of
the wrong phase for its time, a continuation not on a break of structure or against the opening candle, with no
trigger, short of the room its phase needs, or more of them than the cap, a re-anchor state out of range, an entry
before its latency, a profile step out of order or before the entry or after 15:08, a malformed outcome code, a
benchmark entry not after its slot, a spread below -1, records or sessions that disagree with HEAD.
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
FV3_PREFIX = "FV3"


def fv3_head(log_path: Path) -> dict[str, str]:
    lines = prefixed_lines(log_path, FV3_PREFIX)
    if not any(l.startswith(FV3_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(FV3_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "1":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 1) in the logs: {head}")
    return head


def fv3_output_matches_kit(log_path: Path, market: str) -> None:
    head = fv3_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def _codes(x: int, where: str) -> str:
    s = str(x)
    if len(s) != 4 or s[0] != "1" or set(s[1:]) - set("0129"):
        raise UnusableRun(f"{where}: a malformed outcome code {x}")
    return s[1:]


def _profile(v: list[int], p: int, where: str, limit: int) -> tuple[str, int]:
    """One profile [n, off, ticks, ...] from position p: ('off:ticks;...', the position after it); offsets and ticks
    strictly rising, offsets within `limit` bars of the entry."""
    if p >= len(v) or v[p] < 0:
        raise UnusableRun(f"{where}: a profile without its length")
    n = v[p]
    if p + 1 + 2 * n > len(v):
        raise UnusableRun(f"{where}: the record ends inside a profile")
    steps = v[p + 1:p + 1 + 2 * n]
    last_o, last_v = -1, 0
    for i in range(0, 2 * n, 2):
        o, x = steps[i], steps[i + 1]
        if o <= last_o or x <= last_v or o > limit:
            raise UnusableRun(f"{where}: a profile step out of order, not rising, or past 15:08 ({o}, {x})")
        last_o, last_v = o, x
    return ";".join(f"{steps[i]}:{steps[i + 1]}" for i in range(0, 2 * n, 2)), p + 1 + 2 * n


def _day_rows(day: date, v: list[int], market: str) -> list[dict]:
    """One record's rows, every field checked."""
    from propedge.outcomes.fv3_core import (AT_OPEN, BENCH, BENCH_HEAD, BENCH_SIDE, CONT_MIN, FULL_HEAD, FULL_TAIL, LATS, MAX_SIGNALS,
                          MISSING_FV, NEWS_ANCHOR, ROOM_MIN_FRAC, SESSION_FIELDS, SESSIONS, SHORT_FIELDS, SIGNAL_FIELDS)
    from propedge.outcomes.orb_core import FLAT_ENTRY, NONE

    where = f"record {day}"
    if len(v) < 3 or v[0] < 1 or v[1] < 1 or v[2] not in (0, 1):
        raise UnusableRun(f"{where}: an ATR, base stop or news flag out of range")
    rows = [{"kind": "day", "market": market, "date": day.isoformat(), "year": day.year, "atr_ticks": v[0],
             "base_stop_ticks": v[1], "news_day": v[2]}]
    p = 3
    base = {"market": market, "date": day.isoformat(), "year": day.year}
    for name, s, window, _ in SESSIONS:
        w = f"{where}, {name}"
        if p + len(SESSION_FIELDS) > len(v):
            raise UnusableRun(f"{w}: the record ends inside a session")
        hd = dict(zip(SESSION_FIELDS, v[p:p + len(SESSION_FIELDS)]))
        p += len(SESSION_FIELDS)
        n = hd["signals"]
        if hd["present"] not in (0, 1) or hd["open_dir"] not in (-1, 0, 1) or not (0 <= n <= MAX_SIGNALS) \
                or hd["signals_beyond_cap"] < 0 or (hd["signals_beyond_cap"] and n < MAX_SIGNALS) \
                or not (AT_OPEN <= hd["state_at_open"] <= NEWS_ANCHOR) or hd["reanchors"] < 0:
            raise UnusableRun(f"{w}: a session header out of range {hd}")
        if not hd["present"] and any(hd.values()):
            raise UnusableRun(f"{w}: an absent session carrying a field")
        if hd["present"] and (hd["stop_ticks"] != v[1] or hd["open_body_ticks"] < 0):
            raise UnusableRun(f"{w}: a stop other than the base stop or a negative opening body")
        rows.append({"kind": "fvsession", **base, "session": name, **hd})
        last = s
        for i in range(n):
            if p + len(SIGNAL_FIELDS) + len(FULL_HEAD) > len(v):
                raise UnusableRun(f"{w}: the record ends inside a signal")
            sig = dict(zip(SIGNAL_FIELDS, v[p:p + len(SIGNAL_FIELDS)]))
            p += len(SIGNAL_FIELDS)
            slot, phase, d = sig["slot"], sig["phase"], sig["dir"]
            if not (last < slot <= s + window and slot < FLAT_ENTRY) or d not in (-1, 1) \
                    or sig["trigger_bits"] not in (1, 2, 3) or phase not in (0, 1):
                raise UnusableRun(f"{w}: a signal out of its window, out of order, without a trigger or phase {sig}")
            if phase == 0 and not (slot <= s + CONT_MIN and d == hd["open_dir"] and sig["trigger_bits"] == 1
                                   and sig["fv_ticks"] == NONE):
                raise UnusableRun(f"{w}: a continuation after the first minutes, against the opening candle, or not "
                                  f"on a break of structure")
            if phase == 1 and not (slot > s + CONT_MIN and sig["fv_ticks"] + 1e-9 >= ROOM_MIN_FRAC * v[1]):
                raise UnusableRun(f"{w}: a reversion in the first minutes or short of its room")
            if not (AT_OPEN <= sig["reanchor"] <= NEWS_ANCHOR) or sig["swing_bars"] < 0 or sig["swing_age"] < 0 \
                    or sig["disp_body_ratio"] < 0:
                raise UnusableRun(f"{w}: a signal attribute out of range {sig}")
            last = slot
            head = dict(zip(FULL_HEAD, v[p:p + len(FULL_HEAD)]))
            p += len(FULL_HEAD)
            row = {"kind": "signal", **base, "session": name, "idx": i, **sig}
            off = head["bar"]
            fav, p = _profile(v, p, w, FLAT_ENTRY)
            adv, p = _profile(v, p, w, FLAT_ENTRY)
            if p + len(FULL_TAIL) > len(v):
                raise UnusableRun(f"{w}: the record ends inside a signal's tail")
            tail = dict(zip(FULL_TAIL, v[p:p + len(FULL_TAIL)]))
            p += len(FULL_TAIL)
            if off == NONE:
                if [head[k] for k in FULL_HEAD] != [NONE, 0, NONE, 0] or fav or adv \
                        or [tail[k] for k in FULL_TAIL] != [0, MISSING_FV, NONE, 0, NONE]:
                    raise UnusableRun(f"{w}: an entry that never filled carrying a field")
                bar = NONE
            else:
                bar = slot + off
                if off < LATS[0] + 1 or bar >= FLAT_ENTRY or head["spread_tenths"] < -1:
                    raise UnusableRun(f"{w}: an entry before its latency, after 15:07 or a spread below -1")
                for k in ("be_open_off", "be_touch_off"):
                    x = tail[k]
                    if x != NONE and not (0 <= x and bar + x <= FLAT_ENTRY):
                        raise UnusableRun(f"{w}: a breakeven bar before the entry or after 15:08")
                if tail["be_touch_off"] != NONE and tail["be_open_off"] == NONE:
                    raise UnusableRun(f"{w}: a breakeven touch without the next session's open")
                limit = FLAT_ENTRY - bar
                for prof in (fav, adv):
                    if prof and max(int(x.split(":")[0]) for x in prof.split(";")) > limit:
                        raise UnusableRun(f"{w}: a profile step after 15:08")
            row.update({"bar": bar, "entry_ticks": head["entry_ticks"], "spread_tenths": head["spread_tenths"],
                        "fv_from_entry_ticks": head["fv_from_entry_ticks"], "fav_profile": fav, "adv_profile": adv,
                        **tail})
            for L in LATS[1:]:
                if p + 2 > len(v):
                    raise UnusableRun(f"{w}: the record ends inside a latency's entry")
                et, cd = v[p], v[p + 1]
                p += 2
                row[f"entry_ticks_l{L}"] = et
                row[f"codes_l{L}"] = _codes(cd, w)
            rows.append(row)
        for slot in BENCH[name]:
            if p + len(BENCH_HEAD) > len(v):
                raise UnusableRun(f"{w}: the record ends inside a benchmark slot")
            j1, close = v[p:p + len(BENCH_HEAD)]
            p += len(BENCH_HEAD)
            for side in (1, -1):
                if p + len(BENCH_SIDE) > len(v):
                    raise UnusableRun(f"{w}: the record ends inside a benchmark side")
                wo, fv = v[p:p + len(BENCH_SIDE)]
                p += len(BENCH_SIDE)
                fav, p = _profile(v, p, w, FLAT_ENTRY)
                adv, p = _profile(v, p, w, FLAT_ENTRY)
                if j1 == NONE:
                    if (close, wo, fv) != (0, MISSING_FV, 0) or fav or adv:
                        raise UnusableRun(f"{w}: an empty benchmark slot carrying a field")
                    continue
                if not (slot < j1 < FLAT_ENTRY):
                    raise UnusableRun(f"{w}: a benchmark entry not after its slot {slot} or after 15:07")
                rows.append({"kind": "bench", **base, "session": name, "bench_after": slot, "side": side,
                             "bench_slot": j1, "bench_close_ticks": side * close, "bench_worst_ticks": wo,
                             "bench_fv_ticks": fv, "fav_profile": fav, "adv_profile": adv})
    if p != len(v):
        raise UnusableRun(f"{where}: {len(v) - p} fields left over after the last session")
    return rows


def parse_fv3(log_path: Path, results_path: Path, *, market: str = "NQ") -> tuple[pd.DataFrame, dict]:
    """(table, facts): `day`, `fvsession`, `signal` and `bench` rows per day record, and the session cells."""
    head = fv3_head(log_path)
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


__all__ = ["FV3_PREFIX", "fv3_head", "fv3_output_matches_kit", "parse_fv3"]
