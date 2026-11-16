"""The flip map's kit output (R137-flipmap-NQ, D-343; R138-flipmap-NQ-seconds, D-344) into a table: `parse_flip`.

A kit logs `<prefix>|HEAD` (version 1) and `<prefix>|END` -- `FM1` for the minute kit, `FM2` for the second-resolution
kit, whose HEAD adds `secbars`, `nosec` and `short` -- and carries its counts in order tags
`F|e=<emit>;k=<chunk>;K=<chunks>;x=<cells>`, cells joined by '/':

* `C<year>,<ti>,<wi>,<dl>,<n>,<t>,<s>,<x>,<m>,<t5>,<s5>,<xs>,<xa>` -- full sessions: brackets at the target first, the
  stop first and scratched at the box, the units to resolution summed over the resolved (a unit is the kit's bar: a
  minute or a second), the targets and stops within five minutes, the scratches' P&L in ticks summed (signed) and in
  absolute value;
* `E...` -- the same for early closes (D-215);
* `S<year>,<ti>,<count>,<ticks x 100>` -- the on-time entry bar's two-sided spread in the contract's ticks (the minute kit).

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields, a missing chunk or emit, chunks
that do not add up to HEAD's orders, a malformed or out-of-range cell, a cell counted twice, a cell whose outcomes do
not add up, no count at all, or counts that disagree with HEAD's entries.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from propedge.data.manual_parsers import UnusableRun, _kv, _lean_version, _tag, orders_from_results, prefixed_lines

_REC = re.compile(r"F\|e=(\d+);k=(\d+);K=(\d+);x=(.*)$")
HEAD_INTS = ("days", "warm", "entries", "emits", "orders", "switches", "lost", "late", "early", "noref", "bad", "bars",
             "quotes", "wide", "badq")
HEAD_FIELDS = frozenset({"v", "market", *HEAD_INTS})
DAY_TYPES = {"C": "full", "E": "early"}


def _ct(slot: int) -> str:
    m = (17 * 60 + int(slot)) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def _kit(q: dict | None):
    """(parameters, prefix, HEAD integer fields, HEAD text fields) for the kit `q` describes: the minute kit by default."""
    from propedge.data import flip_kit as fk

    q = q or fk.params()
    prefix = str(q.get("prefix", fk.FLIP_PREFIX))
    ints = tuple(HEAD_INTS) + tuple(q.get("head_extra") or ())
    texts = tuple(q.get("head_text") or ())
    return q, prefix, ints, texts


def flip_head(log_path: Path, q: dict | None = None) -> dict[str, str]:
    _, prefix, ints, texts = _kit(q)
    fields = frozenset({"v", "market", *ints, *texts})
    lines = prefixed_lines(log_path, prefix)
    if not any(l.startswith(prefix + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(prefix + "|HEAD|")), None)
    if head is None or set(head) != fields or head.get("v") != "1":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 1) in the logs: {head}")
    return head


def flip_output_matches_kit(log_path: Path, market: str, q: dict | None = None) -> None:
    """D-131-style check for an attested run: HEAD names the kit's market and version and exactly its fields."""
    head = flip_head(log_path, q)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def parse_flip(log_path: Path, results_path: Path, q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per count cell (`kind` count, `day_type` full or early) and per spread cell. `q` is the
    kit's parameters (`flip_kit.params()` for the minute kit, `flip_kit.params_seconds()` for the second-resolution
    kit); the slot's clock label comes from `q["slot_labels"]` when the kit carries them, else from the trading-day
    clock. The `minutes` column holds the kit's units (minutes or seconds)."""
    q, prefix, ints, texts = _kit(q)
    head = flip_head(log_path, q)
    times, widths, delays = q["p"]["times"], q["widths_points"], q["delays"]
    labels = q.get("slot_labels")

    def ct(ti: int) -> str:
        return str(labels[ti]) if labels else _ct(times[ti])

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
    rows, seen = [], set()
    for e in sorted(parts):
        for cell in "/".join(parts[e][k] for k in range(sizes[e])).split("/"):
            try:
                v = [int(x) for x in cell[1:].split(",")]
            except ValueError as exc:
                raise UnusableRun(f"malformed cell {cell!r}") from exc
            kind = cell[:1]
            if kind in DAY_TYPES and len(v) == 13:
                y, ti, wi, dl, n, t, s, x, mins, t5, s5, xs, xa = v
                if not (0 <= ti < len(times) and 0 <= wi < len(widths) and dl in delays):
                    raise UnusableRun(f"cell {cell!r}: an index out of range")
                key = (kind, y, ti, wi, dl)
                if n != t + s + x or min(v[:8] + [mins, t5, s5, xa]) < 0 or t5 > t or s5 > s or xa < abs(xs):
                    raise UnusableRun(f"cell {cell!r}: its outcomes do not add up")
                row = {"kind": "count", "day_type": DAY_TYPES[kind], "market": head["market"], "year": y,
                       "decision_slot": times[ti], "decision_ct": ct(ti), "width_points": widths[wi],
                       "delay_min": dl, "n": n, "target": t, "stop": s, "scratch": x, "minutes": mins,
                       "target_within_5": t5, "stop_within_5": s5, "scratch_ticks": xs, "scratch_abs_ticks": xa}
            elif kind == "S" and len(v) == 4:
                y, ti, cnt, ticks100 = v
                if not 0 <= ti < len(times) or cnt < 0 or ticks100 < 0:
                    raise UnusableRun(f"cell {cell!r}: an index out of range")
                key = (kind, y, ti)
                row = {"kind": "spread", "day_type": "full", "market": head["market"], "year": y,
                       "decision_slot": times[ti], "decision_ct": ct(ti), "quotes": cnt,
                       "spread_ticks_mean": (ticks100 / 100.0 / cnt) if cnt else float("nan")}
            else:
                raise UnusableRun(f"malformed cell {cell!r}")
            if key in seen:
                raise UnusableRun(f"cell {cell!r} counted twice")
            seen.add(key)
            rows.append(row)
    df = pd.DataFrame(rows)
    if not len(df) or not (df["kind"] == "count").any():
        raise UnusableRun("no count cell in the output.")
    counted = int(df.loc[df["kind"] == "count", "n"].sum())
    if counted != int(head["entries"]):
        raise UnusableRun(f"the cells count {counted} brackets, HEAD reports {head['entries']} entries.")
    facts = {k: int(head[k]) for k in ints}
    facts.update({k: str(head[k]) for k in texts})
    facts.update({"market": head["market"], "version": int(head["v"]), "time_unit": str(q.get("time_unit", "minute")),
                  "lean_version": _lean_version(log_path, results_path)})
    return df, facts


def _chunks(results_path: Path, head: dict[str, str]) -> list[str]:
    """Every emit's chunks joined in order, the emits and chunks checked against HEAD."""
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
    return ["/".join(parts[e][k] for k in range(sizes[e])) for e in sorted(parts)]


def parse_flipdir(log_path: Path, results_path: Path, q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """The flip-direction atlas's output (R142-flipdir-NQ, D-371) into one row per trading day: the date, early close,
    same contract as the previous day, ATR20, the walk's resolution (`res`: 1 seconds, 2 minutes, 0 not walked), the measures (`flipdir_core.DIR_MEASURES`, ticks), each width in ticks
    (`w_<label>`), each bracket's outcome (`o_<label>_d<delay>_<L|S>`: t, s, x or '-'), and for the extra widths the
    seconds to resolution and the scratch's ticks (`u_<label>_<L|S>`, `xs_<label>_<L|S>`). Refused: anything
    `parse_flip` refuses of the HEAD and the chunks, a record of the wrong shape, an outcome outside 't', 's', 'x', '-',
    a day twice or out of order, records that disagree with HEAD's `records`, walked brackets that disagree with HEAD's
    `entries`."""
    from propedge.data import flip_kit as fk
    from propedge.outcomes.flipdir_core import DIR_MEASURES

    q = q or fk.params_direction()
    head = flip_head(log_path, q)
    labels, delays = list(q["width_labels"]), list(q["delays"])
    extras = list(q["extra_widths"])
    n_out = len(labels) * len(delays) * 2
    n_fields = 5 + len(DIR_MEASURES) + len(labels) + 1 + 4 * len(extras)
    out_cols = [f"o_{lab}_d{dl}_{s}" for lab in labels for dl in delays for s in ("L", "S")]
    ex_cols = [c for wi in extras for s in ("L", "S") for c in (f"u_{labels[wi]}_{s}", f"xs_{labels[wi]}_{s}")]

    def num(x: str, cell: str):
        if x == "":
            return None
        try:
            return int(x)
        except ValueError as exc:
            raise UnusableRun(f"malformed record {cell[:60]!r}") from exc

    rows, last = [], None
    for blob in _chunks(results_path, head):
        for cell in blob.split("/"):
            if not cell.startswith("D"):
                raise UnusableRun(f"malformed record {cell[:60]!r}")
            v = cell[1:].split(",")
            if len(v) != n_fields:
                raise UnusableRun(f"record {cell[:60]!r}: {len(v)} fields, the kit writes {n_fields}")
            day = v[0]
            if len(day) != 8 or not day.isdigit():
                raise UnusableRun(f"record {cell[:60]!r}: a malformed date")
            iso = f"{day[:4]}-{day[4:6]}-{day[6:]}"
            if last is not None and iso <= last:
                raise UnusableRun(f"day {iso} twice or out of order")
            last = iso
            k = 5 + len(DIR_MEASURES) + len(labels)
            outs = v[k]
            if len(outs) != n_out or set(outs) - set("tsx-"):
                raise UnusableRun(f"record {cell[:60]!r}: a malformed outcome string")
            row = {"date": iso, "year": int(day[:4]), "early": num(v[1], cell), "same": num(v[2], cell),
                   "atr": num(v[3], cell), "res": num(v[4], cell)}
            row.update({m: num(x, cell) for m, x in zip(DIR_MEASURES, v[5:5 + len(DIR_MEASURES)])})
            row.update({f"w_{lab}": num(x, cell) for lab, x in zip(labels, v[5 + len(DIR_MEASURES):k])})
            row.update(dict(zip(out_cols, outs)))
            row.update({c: num(x, cell) for c, x in zip(ex_cols, v[k + 1:])})
            rows.append(row)
    df = pd.DataFrame(rows)
    if not len(df):
        raise UnusableRun("no record in the output.")
    if len(df) != int(head["records"]):
        raise UnusableRun(f"{len(df)} records, HEAD reports {head['records']}.")
    walked = int(sum((df[c] != "-").sum() for c in out_cols))
    if walked != int(head["entries"]):
        raise UnusableRun(f"the records hold {walked} brackets, HEAD reports {head['entries']} entries.")
    ints = tuple(HEAD_INTS) + tuple(q.get("head_extra") or ())
    texts = tuple(q.get("head_text") or ())
    facts = {k2: int(head[k2]) for k2 in ints}
    facts.update({k2: str(head[k2]) for k2 in texts})
    facts.update({"market": head["market"], "version": int(head["v"]), "time_unit": str(q.get("time_unit", "second")),
                  "lean_version": _lean_version(log_path, results_path)})
    return df, facts


ANY_MEASURES = ("a1_last1", "a2_last15", "a3_last60", "a4_since_rth_open", "a5_since_day_open", "rlo", "rhi",
                "a7_prior_rth")


def parse_flipany(log_path: Path, results_path: Path, q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """The any-time direction atlas's output (R143-flipany-NQ, D-373) into one row per trading day and slot: the date,
    early close, same contract as the previous day, the slot (its CT label and index), each width in ticks
    (`w_<label>`), the measures (`ANY_MEASURES`, ticks), each bracket's outcome (`o_<label>_d<delay>_<L|S>`: t, s, x or
    '-'), and for the primary width on time the seconds to resolution and the scratch's ticks (`u_L`, `xs_L`, `u_S`,
    `xs_S`). Refused: anything `parse_flip` refuses of the HEAD and the chunks, a record without one block a slot, a
    block of the wrong shape, an outcome outside 't', 's', 'x', '-', a day twice or out of order, and records, walked
    slot-days or brackets that disagree with HEAD."""
    from propedge.data import flip_kit as fk

    q = q or fk.params_anytime()
    head = flip_head(log_path, q)
    labels, delays, slots = list(q["width_labels"]), list(q["delays"]), list(q["slot_labels"])
    out_cols = [f"o_{lab}_d{dl}_{s}" for lab in labels for dl in delays for s in ("L", "S")]
    n_block = len(labels) + len(ANY_MEASURES) + 1 + 4

    def num(x: str, cell: str):
        if x == "":
            return None
        try:
            return int(x)
        except ValueError as exc:
            raise UnusableRun(f"malformed record {cell[:60]!r}") from exc

    rows, last, n_days, walked_days = [], None, 0, 0
    for blob in _chunks(results_path, head):
        for cell in blob.split("/"):
            parts = cell.split(":")
            lead = parts[0]
            if not lead.startswith("D") or len(parts) != 1 + len(slots):
                raise UnusableRun(f"malformed record {cell[:60]!r}")
            v = lead[1:].split(",")
            if len(v) != 3 or len(v[0]) != 8 or not v[0].isdigit():
                raise UnusableRun(f"record {cell[:60]!r}: a malformed head")
            iso = f"{v[0][:4]}-{v[0][4:6]}-{v[0][6:]}"
            if last is not None and iso <= last:
                raise UnusableRun(f"day {iso} twice or out of order")
            last = iso
            n_days += 1
            for si, block in enumerate(parts[1:]):
                b = block.split(",")
                if len(b) != n_block:
                    raise UnusableRun(f"record {iso} slot {slots[si]}: {len(b)} fields, the kit writes {n_block}")
                k = len(labels) + len(ANY_MEASURES)
                outs = b[k]
                if len(outs) != len(out_cols) or set(outs) - set("tsx-"):
                    raise UnusableRun(f"record {iso} slot {slots[si]}: a malformed outcome string")
                walked_days += int(outs != "-" * len(out_cols))
                row = {"date": iso, "year": int(v[0][:4]), "early": num(v[1], cell), "same": num(v[2], cell),
                       "slot": slots[si], "slot_index": si}
                row.update({f"w_{lab}": num(x, cell) for lab, x in zip(labels, b[:len(labels)])})
                row.update({m: num(x, cell) for m, x in zip(ANY_MEASURES, b[len(labels):k])})
                row.update(dict(zip(out_cols, outs)))
                row.update({c: num(x, cell) for c, x in zip(("u_L", "xs_L", "u_S", "xs_S"), b[k + 1:])})
                rows.append(row)
    df = pd.DataFrame(rows)
    if not len(df):
        raise UnusableRun("no record in the output.")
    if n_days != int(head["records"]):
        raise UnusableRun(f"{n_days} records, HEAD reports {head['records']}.")
    if walked_days != int(head["walked"]):
        raise UnusableRun(f"{walked_days} walked slot-days, HEAD reports {head['walked']}.")
    entered = int(sum((df[c] != "-").sum() for c in out_cols))
    if entered != int(head["entries"]):
        raise UnusableRun(f"the records hold {entered} brackets, HEAD reports {head['entries']} entries.")
    ints = tuple(HEAD_INTS) + tuple(q.get("head_extra") or ())
    texts = tuple(q.get("head_text") or ())
    facts = {k2: int(head[k2]) for k2 in ints}
    facts.update({k2: str(head[k2]) for k2 in texts})
    facts.update({"market": head["market"], "version": int(head["v"]), "time_unit": "second",
                  "lean_version": _lean_version(log_path, results_path)})
    return df, facts


def parse_flipdesign(log_path: Path, results_path: Path, q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """The flip design map's output (R144-flipdesign-NQ, D-375) into one row per trading day: the date, early close,
    same contract as the previous day, D-371's measures (`flipdir_core.DIR_MEASURES`, ticks), each bracket's outcome
    (`o_w<width>_d<delay>_<L|S>`: t, s, x or '-'), each on-time bracket's seconds to resolution (`u_w<width>_<L|S>`,
    empty unless resolved) and the marks (`mark_<seconds>`: the price that long after the entry less the entry bar's
    open, ticks). Refused as `parse_flipdir` refuses."""
    from propedge.data import flip_kit as fk
    from propedge.outcomes.flipdir_core import DIR_MEASURES

    q = q or fk.params_design()
    head = flip_head(log_path, q)
    labels = [f"w{w:g}" for w in q["widths_points"]]
    delays, marks = list(q["delays"]), list(q["marks"])
    out_cols = [f"o_{lab}_d{dl}_{s}" for lab in labels for dl in delays for s in ("L", "S")]
    unit_cols = [f"u_{lab}_{s}" for lab in labels for s in ("L", "S")]
    mark_cols = [f"mark_{m}" for m in marks]
    n_fields = 3 + len(DIR_MEASURES) + 1 + len(unit_cols) + len(mark_cols)

    def num(x: str, cell: str):
        if x == "":
            return None
        try:
            return int(x)
        except ValueError as exc:
            raise UnusableRun(f"malformed record {cell[:60]!r}") from exc

    rows, last = [], None
    for blob in _chunks(results_path, head):
        for cell in blob.split("/"):
            if not cell.startswith("D"):
                raise UnusableRun(f"malformed record {cell[:60]!r}")
            v = cell[1:].split(",")
            if len(v) != n_fields:
                raise UnusableRun(f"record {cell[:60]!r}: {len(v)} fields, the kit writes {n_fields}")
            day = v[0]
            if len(day) != 8 or not day.isdigit():
                raise UnusableRun(f"record {cell[:60]!r}: a malformed date")
            iso = f"{day[:4]}-{day[4:6]}-{day[6:]}"
            if last is not None and iso <= last:
                raise UnusableRun(f"day {iso} twice or out of order")
            last = iso
            k = 3 + len(DIR_MEASURES)
            outs = v[k]
            if len(outs) != len(out_cols) or set(outs) - set("tsx-"):
                raise UnusableRun(f"record {cell[:60]!r}: a malformed outcome string")
            row = {"date": iso, "year": int(day[:4]), "early": num(v[1], cell), "same": num(v[2], cell)}
            row.update({m: num(x, cell) for m, x in zip(DIR_MEASURES, v[3:k])})
            row.update(dict(zip(out_cols, outs)))
            row.update({c: num(x, cell) for c, x in zip(unit_cols, v[k + 1:k + 1 + len(unit_cols)])})
            row.update({c: num(x, cell) for c, x in zip(mark_cols, v[k + 1 + len(unit_cols):])})
            rows.append(row)
    df = pd.DataFrame(rows)
    if not len(df):
        raise UnusableRun("no record in the output.")
    if len(df) != int(head["records"]):
        raise UnusableRun(f"{len(df)} records, HEAD reports {head['records']}.")
    walked = int(sum((df[c] != "-").sum() for c in out_cols))
    if walked != int(head["entries"]):
        raise UnusableRun(f"the records hold {walked} brackets, HEAD reports {head['entries']} entries.")
    ints = tuple(HEAD_INTS) + tuple(q.get("head_extra") or ())
    texts = tuple(q.get("head_text") or ())
    facts = {k2: int(head[k2]) for k2 in ints}
    facts.update({k2: str(head[k2]) for k2 in texts})
    facts.update({"market": head["market"], "version": int(head["v"]), "time_unit": "second",
                  "lean_version": _lean_version(log_path, results_path)})
    return df, facts


def parse_collect(log_path: Path, results_path: Path, q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """The collect map's output (R145-collect-NQ, D-381) into rows by `kind`: `count` (year, slot, micros, stop
    multiple, box, delay: brackets at the target, the stop and scratched, both sides pooled; minutes to resolution
    summed over the resolved; the scratches' P&L in ticks summed), `tie` (year, slot: tied minutes settled to the
    target, to the stop, and unsettled -- the stop's), `gap` (year, slot, stop distance: stops reached inside the
    longest box, those an open passed, their ticks beyond the stop) and `box` (year, slot, box: walks and those a BLS
    cut shortened). Refused: anything `parse_flip` refuses of the HEAD and the chunks, a malformed or out-of-range cell,
    a cell twice, counts below zero, gaps or cuts above their walks, or counts that disagree with HEAD's entries."""
    from propedge.data import flip_kit as fk

    q = q or fk.params_collect()
    head = flip_head(log_path, q)
    labels, slots, y0 = q["slot_labels"], q["slots"], int(q["y0"])
    ns, ms, boxes, delays = q["contracts"], q["stop_multiples"], q["boxes"], q["delays"]
    levels = q["p"]["levels"]
    shape = {"C": 11, "T": 5, "G": 6, "B": 5}
    rows, seen = [], set()
    for blob in _chunks(results_path, head):
        for cell in blob.split("/"):
            kind = cell[:1]
            try:
                v = [int(x) for x in cell[1:].split(",")]
            except ValueError as exc:
                raise UnusableRun(f"malformed cell {cell[:60]!r}") from exc
            if kind not in shape or len(v) != shape[kind]:
                raise UnusableRun(f"malformed cell {cell[:60]!r}")
            yo, si = v[0], v[1]
            if not (0 <= yo <= 99 and 0 <= si < len(slots)):
                raise UnusableRun(f"cell {cell[:60]!r}: an index out of range")
            key = (kind, *v[:{"C": 6, "T": 2, "G": 3, "B": 3}[kind]])
            if key in seen:
                raise UnusableRun(f"cell {cell[:60]!r} counted twice")
            seen.add(key)
            base = {"market": head["market"], "year": y0 + yo, "decision_ct": labels[si], "decision_slot_minutes": slots[si]}
            if kind == "C":
                ni, ki, bi, dl, t, s, x, mins, xs = v[2:]
                if not (0 <= ni < len(ns) and 0 <= ki < len(ms) and 0 <= bi < len(boxes) and dl in delays):
                    raise UnusableRun(f"cell {cell[:60]!r}: an index out of range")
                if min(t, s, x, mins) < 0:
                    raise UnusableRun(f"cell {cell[:60]!r}: a count below zero")
                rows.append({**base, "kind": "count", "contracts": ns[ni], "target_points": q["targets_points"][ni],
                             "stop_multiple": ms[ki], "stop_points": q["stops_points"][ni][ki], "box_minutes": boxes[bi],
                             "delay_min": dl, "n": t + s + x, "target": t, "stop": s, "scratch": x, "minutes": mins,
                             "scratch_ticks": xs})
            elif kind == "T":
                t, s, u = v[2:]
                if min(t, s, u) < 0:
                    raise UnusableRun(f"cell {cell[:60]!r}: a count below zero")
                rows.append({**base, "kind": "tie", "tie_target": t, "tie_stop": s, "tie_unsettled": u})
            elif kind == "G":
                li, n, g, gt = v[2:]
                if not 0 <= li < len(levels) or min(n, g, gt) < 0 or g > n:
                    raise UnusableRun(f"cell {cell[:60]!r}: out of range or more gaps than stops")
                rows.append({**base, "kind": "gap", "level_points": levels[li], "stops_reached": n, "gapped": g,
                             "gap_ticks": gt})
            else:
                bi, n, cut = v[2:]
                if not 0 <= bi < len(boxes) or min(n, cut) < 0 or cut > n:
                    raise UnusableRun(f"cell {cell[:60]!r}: out of range or more cuts than walks")
                rows.append({**base, "kind": "box", "box_minutes": boxes[bi], "walks": n, "cut_short": cut})
    df = pd.DataFrame(rows)
    if not len(df) or not (df["kind"] == "count").any():
        raise UnusableRun("no count cell in the output.")
    entries = int(head["entries"])
    per_walk = len(ns) * len(ms) * len(boxes)
    if int(df.loc[df["kind"] == "count", "n"].sum()) != entries * per_walk:
        raise UnusableRun(f"the count cells hold {int(df.loc[df['kind'] == 'count', 'n'].sum())} brackets; HEAD's "
                          f"{entries} walks make {entries * per_walk}.")
    if int(df.loc[df["kind"] == "box", "walks"].sum()) != entries * len(boxes):
        raise UnusableRun("the box cells disagree with HEAD's entries.")
    ints = tuple(HEAD_INTS) + tuple(q.get("head_extra") or ())
    texts = tuple(q.get("head_text") or ())
    facts = {k2: int(head[k2]) for k2 in ints}
    facts.update({k2: str(head[k2]) for k2 in texts})
    facts.update({"market": head["market"], "version": int(head["v"]), "time_unit": "minute",
                  "lean_version": _lean_version(log_path, results_path)})
    return df, facts


def parse_dst(log_path: Path, results_path: Path, q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """The clock check's output (R146-dst-NQ, D-386 (7)) into one row per trading day: the date and the six bars'
    ranges in ticks (`r_<HHMM>`, the bar's start time CT; empty for a missing bar). Refused: anything `parse_flip`
    refuses of the HEAD and the chunks, a record of the wrong shape, a negative range, a day twice or out of order, or
    records and bars that disagree with HEAD's `records` and `entries`."""
    from propedge.data import flip_kit as fk

    q = q or fk.params_dst()
    head = flip_head(log_path, q)
    cols = [f"r_{x.replace(':', '')}" for x in q["bar_labels"]]
    rows, last = [], None
    for blob in _chunks(results_path, head):
        for cell in blob.split("/"):
            if not cell.startswith("D"):
                raise UnusableRun(f"malformed record {cell[:60]!r}")
            v = cell[1:].split(",")
            if len(v) != 1 + len(cols):
                raise UnusableRun(f"record {cell[:60]!r}: {len(v)} fields, the kit writes {1 + len(cols)}")
            day = v[0]
            if len(day) != 8 or not day.isdigit():
                raise UnusableRun(f"record {cell[:60]!r}: a malformed date")
            iso = f"{day[:4]}-{day[4:6]}-{day[6:]}"
            if last is not None and iso <= last:
                raise UnusableRun(f"day {iso} twice or out of order")
            last = iso
            try:
                vals = [None if x == "" else int(x) for x in v[1:]]
            except ValueError as exc:
                raise UnusableRun(f"malformed record {cell[:60]!r}") from exc
            if any(x is not None and x < 0 for x in vals):
                raise UnusableRun(f"record {cell[:60]!r}: a negative range")
            rows.append({"date": iso, "year": int(day[:4]), **dict(zip(cols, vals))})
    df = pd.DataFrame(rows)
    if not len(df):
        raise UnusableRun("no record in the output.")
    if len(df) != int(head["records"]):
        raise UnusableRun(f"{len(df)} records, HEAD reports {head['records']}.")
    if int(df[cols].notna().to_numpy().sum()) != int(head["entries"]):
        raise UnusableRun("the records' bars disagree with HEAD's entries.")
    ints = tuple(HEAD_INTS) + tuple(q.get("head_extra") or ())
    facts = {k2: int(head[k2]) for k2 in ints}
    facts.update({"market": head["market"], "version": int(head["v"]), "time_unit": "minute",
                  "lean_version": _lean_version(log_path, results_path)})
    return df, facts


__all__ = ["HEAD_FIELDS", "DAY_TYPES", "ANY_MEASURES", "flip_head", "flip_output_matches_kit", "parse_flip",
           "parse_flipdir", "parse_flipany", "parse_flipdesign", "parse_collect", "parse_dst"]
