"""ORB6's capture outputs (R108-R110; D-276 to D-278) into a table: `parse_orb6`.

A kit logs `OR6|HEAD` (version 1) and `OR6|END` and carries its records in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<slice>`: each emit's cells joined by '/' and cut into slices, joined back in order;
in a record a -1 is written as nothing, so an empty field reads as -1 (every field that can never be -1 is
range-checked below):

* `R<yyyymmdd>,<fields>` -- one per day: `orb6_core.SHARED6_FIELDS`; per range of `orb_core.OR_MINS`
  `BLOCK6_FIELDS`, the hand-traded entry's range walk (`hand_range_dist_ticks`, then the offsets of its stop and of
  `RANGE_RR` times its distance), `RETEST_FIELDS`, the retest's range walk and per stop width of the grid the retest's
  stop and `RETEST_RR` offsets -- a `day` row per day and range, the retest's offsets turned into slots (-1 kept; the
  hand-traded entry's stay offsets from ORB5's `lat_slot`, which the ingest joins and checks); then per slot of
  `BENCH_SLOTS`, `BENCH_FIELDS` -- a `bench` row per day, slot and side (`side` +1 long, -1 short), its codes one column
  per bracket (`c_w<i>_<R>` per stop width i, `c_r<minutes>_<R>` per range's stop: 0 stop, 1 target, 2 open, 9 none);
* `D<year>,...` -- as ORB1's session cells.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields or not version 1, a missing
chunk or emit, chunks that do not add up to HEAD's orders, a malformed record, a day twice, a direction outside -1, 0, 1,
a fill without a direction or outside the session, a negative range, a range walk with a distance of none but
passages, a non-positive distance, a retest's passage before its entry or after 15:08, a farther level reached before
a nearer one, a retest of an unknown kind, before its order could work (the breakout's bar + the latency) or not
through the level by a tick, a retest's fill beyond the level or better than it without opening through it, an empty
retest carrying a field, an unconditional entry not after its slot or after 15:07, an empty one carrying a field,
outcome codes of the wrong length, outside 0, 1, 2 and 9, or a 9 where a bracket exists (or none where it does not), a
spread below -1, records or sessions that disagree with HEAD.
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


def orb6_head(log_path: Path) -> dict[str, str]:
    from propedge.data.orb6_kit import ORB6_PREFIX

    lines = prefixed_lines(log_path, ORB6_PREFIX)
    if not any(l.startswith(ORB6_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(ORB6_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "1":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 1) in the logs: {head}")
    return head


def orb6_output_matches_kit(log_path: Path, market: str) -> None:
    head = orb6_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def _rr_name(R: float) -> str:
    return f"f{R:g}".replace(".", "")


def _walk(vals: list[int], base: int, lo: int, where: str, what: str) -> list[int]:
    """Offsets from `base` (an entry's bar) checked and turned into slots: each -1 or at least `lo` and no later than
    15:08."""
    from propedge.outcomes.orb_core import FLAT_ENTRY

    if any(x != -1 and not (lo <= x and base + x <= FLAT_ENTRY) for x in vals):
        raise UnusableRun(f"{where}: a {what} passage before its entry or after 15:08")
    return [base + x if x != -1 else -1 for x in vals]


def _bench_rows(day: date, b: list[int], K: int, where: str, market: str) -> list[dict]:
    """A day's unconditional entries (`BENCH_FIELDS` per slot) checked and turned into rows, one per slot and side:
    every stop width has its brackets; a range's are none before its close + the latency, and after it all or none
    (a day without that range), the same for both sides."""
    from propedge.outcomes.orb5_core import LATENCY
    from propedge.outcomes.orb6_core import BENCH_FIELDS, BENCH_SLOTS, MISSING6, RETEST_RR
    from propedge.outcomes.orb_core import FLAT_ENTRY, NONE, OR_MINS, OR_START

    nr = len(RETEST_RR)
    width = nr * (K + len(OR_MINS))
    names = [f"c_w{i}_{_rr_name(R)[1:]}" for i in range(K) for R in RETEST_RR] + [
        f"c_r{n}_{_rr_name(R)[1:]}" for n in OR_MINS for R in RETEST_RR]
    rows, nf = [], len(BENCH_FIELDS)
    for i, s in enumerate(BENCH_SLOTS):
        f = dict(zip(BENCH_FIELDS, b[i * nf:(i + 1) * nf]))
        codes = []
        for side in ("long", "short"):
            x = str(f[f"bench_codes_{side}"])
            if len(x) != 1 + width or x[0] != "1" or set(x[1:]) - set("0129"):
                raise UnusableRun(f"{where}: the unconditional outcome codes at slot {s} are malformed")
            codes.append(x[1:])
        j1 = f["bench_slot"]
        if j1 == NONE:
            if (f["bench_close_ticks"], f["bench_worst_long_ticks"], f["bench_worst_short_ticks"]) != (
                    0, MISSING6, MISSING6) or any(set(x) != {"9"} for x in codes):
                raise UnusableRun(f"{where}: an empty unconditional entry at slot {s} carrying a field")
            continue
        if not (s < j1 < FLAT_ENTRY):
            raise UnusableRun(f"{where}: an unconditional entry for slot {s} not after it or after 15:07")
        for k in range(K + len(OR_MINS)):
            ch = [x[k * nr:(k + 1) * nr] for x in codes]
            none = [c == "9" * nr for c in ch]
            due = k < K or OR_START + OR_MINS[k - K] + LATENCY <= s       # a width always; a range once it can trade
            if any("9" in c and not w for c, w in zip(ch, none)) or none[0] != none[1] \
                    or (k < K and none[0]) or (not due and not none[0]):
                raise UnusableRun(f"{where}: unconditional outcome codes at slot {s} with a bracket missing or "
                                  "one where there is none")
        for side, d, x in (("long", 1, codes[0]), ("short", -1, codes[1])):
            rows.append({"kind": "bench", "market": market, "date": day.isoformat(), "year": day.year,
                         "bench_after": s, "side": d, "bench_slot": j1,
                         "bench_close_ticks": d * f["bench_close_ticks"],
                         "bench_worst_ticks": f[f"bench_worst_{side}_ticks"],
                         **{nm: int(c) for nm, c in zip(names, x)}})
    return rows


def parse_orb6(log_path: Path, results_path: Path, *, market: str = "NQ",
               stops: tuple[float, ...] | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per day record and range (`kind` day, `or_minutes`), per day, benchmark slot and side
    (`kind` bench) and per session cell."""
    from propedge.data import orb6_kit as k6
    from propedge.outcomes.orb5_core import LATENCY
    from propedge.outcomes.orb6_core import (BENCH_FIELDS, BENCH_SLOTS, BLOCK6_FIELDS, MISSING6, RANGE_RR,
                                             RETEST_FIELDS, RETEST_RR, SHARED6_FIELDS)
    from propedge.outcomes.orb_core import FLAT_ENTRY, NONE, OR_MINS, OR_START

    head = orb6_head(log_path)
    K = len(stops or k6.params()["stops"])
    nrw = 2 + len(RANGE_RR)
    nrt = 1 + len(RETEST_RR)
    nb = len(BLOCK6_FIELDS) + nrw + len(RETEST_FIELDS) + nrw + nrt * K
    ns = len(SHARED6_FIELDS)
    nbench = len(BENCH_FIELDS) * len(BENCH_SLOTS)
    width = 1 + ns + len(OR_MINS) * nb + nbench
    empty_rt = [0, NONE, 0, 0, 0, 0, 0, MISSING6, NONE]
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
    days, benches, sessions, seen, noatr, records = [], [], [], set(), 0, 0
    names_rw = ["dist_ticks", "a"] + [_rr_name(R) for R in RANGE_RR]
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
                    raise UnusableRun(f"record {cell[:40]!r}...: no such date") from exc
                shared = dict(zip(SHARED6_FIELDS, v[1:1 + ns]))
                if shared["atr_ticks"] < 1:
                    raise UnusableRun(f"record {day}: an ATR out of range")
                for r, n in enumerate(OR_MINS):
                    a = 1 + ns + r * nb
                    blk = v[a:a + nb]
                    row = dict(zip(BLOCK6_FIELDS, blk[:len(BLOCK6_FIELDS)]))
                    p = len(BLOCK6_FIELDS)
                    hand_rw, p = blk[p:p + nrw], p + nrw
                    rt = dict(zip(RETEST_FIELDS, blk[p:p + len(RETEST_FIELDS)]))
                    p += len(RETEST_FIELDS)
                    rt_rw, p = blk[p:p + nrw], p + nrw
                    rt_atr = blk[p:p + nrt * K]
                    fs, d = row["fill_slot"], row["dir"]
                    where = f"record {day}, {n}-minute range"
                    if d not in (-1, 0, 1) or (d == 0 and fs != -1) or row["range_ticks"] < 0:
                        raise UnusableRun(f"{where}: a direction or range out of range")
                    if fs != -1 and not (OR_START + n < fs < FLAT_ENTRY):
                        raise UnusableRun(f"{where}: a fill outside the session")
                    for label, rw in (("hand", hand_rw), ("retest", rt_rw)):
                        if rw[0] == NONE:
                            if any(x != NONE for x in rw[1:]):
                                raise UnusableRun(f"{where}: a {label} range walk without its distance")
                            continue
                        if rw[0] <= 0 or fs == -1:
                            raise UnusableRun(f"{where}: a {label} range stop at or beyond its entry, or no fill")
                        if not _monotone(rw[2:]):
                            raise UnusableRun(f"{where}: the {label} range targets not monotone")
                    k_rt = rt["rt_kind"]
                    if k_rt not in (0, 1) or rt["rt_spread_tenths"] < -1:
                        raise UnusableRun(f"{where}: a retest of an unknown kind or a negative spread")
                    if k_rt == 0:
                        if blk[len(BLOCK6_FIELDS) + nrw:len(BLOCK6_FIELDS) + nrw + len(RETEST_FIELDS)] != empty_rt \
                                or any(x != NONE for x in rt_rw + rt_atr):
                            raise UnusableRun(f"{where}: an empty retest carrying a field")
                    else:
                        ls = rt["rt_slot"]
                        if fs == -1 or not (fs + LATENCY < ls < FLAT_ENTRY) or rt["rt_at_open"] not in (0, 1) \
                                or rt["rt_fill_bar_against_ticks"] < 1:
                            raise UnusableRun(f"{where}: a retest before its order works, after 15:07 or not "
                                              "through the level by a tick")
                        if rt["rt_better_ticks"] < 0 or (rt["rt_better_ticks"] > 0 and not rt["rt_at_open"]):
                            raise UnusableRun(f"{where}: a retest filled beyond the level, or better than it "
                                              "without opening through it")
                        per = [rt_atr[i * nrt:(i + 1) * nrt] for i in range(K)]
                        if not all(_monotone(x[1:]) for x in per) or not all(
                                _monotone([x[j] for x in per]) for j in range(nrt)):
                            raise UnusableRun(f"{where}: the retest passages not monotone in the level")
                    out = {**row}
                    out.update({f"hand_range_{nm}": x for nm, x in zip(names_rw, hand_rw)})
                    out.update(rt)
                    lo = 0 if rt["rt_at_open"] else 1
                    base = rt["rt_slot"]
                    if k_rt == 1:
                        rw_slots = rt_rw if rt_rw[0] == NONE else [rt_rw[0]] + _walk(rt_rw[1:], base, lo, where,
                                                                                     "retest range")
                        atr_slots = _walk(rt_atr, base, lo, where, "retest")
                    else:
                        rw_slots, atr_slots = rt_rw, rt_atr
                    out.update({f"rt_range_{nm}": x for nm, x in zip(names_rw, rw_slots)})
                    for i in range(K):
                        for nm, x in zip(["a"] + [_rr_name(R) for R in RETEST_RR], atr_slots[i * nrt:(i + 1) * nrt]):
                            out[f"rt_{nm}_{i}"] = x
                    days.append({"kind": "day", "market": market, "date": day.isoformat(), "year": day.year,
                                 "or_minutes": n, **shared, **out})
                benches += _bench_rows(day, v[1 + ns + len(OR_MINS) * nb:], K, f"record {day}", market)
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
    df = pd.concat([pd.DataFrame(days), pd.DataFrame(benches), pd.DataFrame(sessions)], ignore_index=True)
    facts = {"market": market, **{k: int(head[k]) for k in HEAD_INTS},
             "lean_version": _lean_version(log_path, results_path)}
    return df, facts


__all__ = ["orb6_head", "orb6_output_matches_kit", "parse_orb6"]
