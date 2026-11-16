"""The resolution map's kit outputs (R071-R080; D-214, D-215) into a table: `parse_rmap`.

A separate module so the pinned parser (`propedge/data/manual_parsers.py`, an `ENGINE_FILES` file) is not touched; it
uses that module's readers. A kit logs `RM1|HEAD` (version 2) and `RM1|END` and carries its counts in order tags
`R|e=<emit>;k=<chunk>;K=<chunks>;x=<cells>`, cells joined by '/':

* `C<year>,<ti>,<si>,<r>,<n>,<t>,<s>,<o>,<minutes>` -- full sessions: brackets at the target first, the stop first and
  still open, and their minutes to resolution summed;
* `E...` -- the same for scheduled or unscheduled early closes (a day whose last bar ends before 15:00 CT; D-215);
* `S<year>,<ti>,<count>,<ticks x 100>` -- the entry bar's two-sided spread in the micro's ticks.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields, a missing chunk or emit, chunks
that do not add up to HEAD's orders, a malformed or out-of-range cell, a cell counted twice, a cell whose outcomes do
not add up, no count at all, or counts that disagree with HEAD's entries.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from propedge.data.manual_parsers import (UnusableRun, _kv, _lean_version, _tag, orders_from_results,
                                          prefixed_lines)

_REC = re.compile(r"R\|e=(\d+);k=(\d+);K=(\d+);x=(.*)$")
HEAD_INTS = ("days", "warm", "entries", "emits", "orders", "switches", "lost", "late", "early", "noref", "bad", "bars",
             "quotes", "wide", "badq")
HEAD_FIELDS = frozenset({"v", "market", *HEAD_INTS})
DAY_TYPES = {"C": "full", "E": "early"}


def rmap_head(log_path: Path) -> dict[str, str]:
    from propedge.data.rmap_kit import RMAP_PREFIX

    lines = prefixed_lines(log_path, RMAP_PREFIX)
    if not any(l.startswith(RMAP_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(RMAP_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "2":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 2) in the logs: {head}")
    return head


def rmap_usability(log_path: Path, min_days: int, limit_hit: str = "none") -> list[str]:
    """D-230: why a run is unusable, judged from its log alone -- no count is parsed: no END or HEAD, an error or a
    time limit in the log or reported by the operator, or HEAD's days below `min_days`. Empty: usable."""
    out = []
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    if re.search(r"runtime error|time ?limit|timed out|exceeded", text, re.IGNORECASE):
        out.append("the log reports an error or a time limit")
    if str(limit_hit).strip().lower() not in ("", "none"):
        out.append(f"the operator reports a limit: {limit_hit}")
    try:
        head = rmap_head(log_path)
    except UnusableRun as exc:
        return out + [str(exc)]
    if int(head.get("days", 0)) < int(min_days):
        out.append(f"HEAD reports {head.get('days')} days, fewer than the {min_days} required")
    return out


def rmap_output_matches_kit(log_path: Path, market: str) -> None:
    """D-131-style check for an attested run: HEAD names the kit's market and version and exactly its fields."""
    head = rmap_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def parse_rmap(log_path: Path, results_path: Path, *, market: str | None = None,
               q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per count cell (`kind` count, `day_type` full or early) and per spread cell. `q` is the
    kit's own parameters (`rmap_kit.confirm_params` for NQB1's confirmation, D-229); its `keep` refuses any cell
    outside the registered brackets."""
    from propedge.data import rmap_kit as rk

    head = rmap_head(log_path)
    mk = market or head["market"]
    q = q or rk.params(mk)
    times, stops, rr = q["p"]["times"], q["stop_dollars"], list(q["p"]["rr"])
    keep = {(int(i), float(r)) for i, r in q.get("keep", [])} or None
    # D-230: a confirmation run's refusals never echo a cell, which carries held-back counts
    show = (lambda c: repr(c)) if keep is None else (lambda c: f"of kind {c[:1]!r}")      # noqa: E731
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
                raise UnusableRun(f"malformed cell {show(cell)}") from exc
            kind = cell[:1]
            if kind in DAY_TYPES and len(v) == 9:
                y, ti, si, ri, n, t, s, o, mins = v
                if not (0 <= ti < len(times) and 0 <= si < len(stops) and 0 <= ri < len(rr)):
                    raise UnusableRun(f"cell {show(cell)}: an index out of range")
                key = (kind, y, ti, si, ri)
                if keep is not None and (si, rr[ri]) not in keep:
                    raise UnusableRun(f"cell {show(cell)}: a bracket outside the registered set (D-229)")
                if n != t + s + o or min(v) < 0:
                    raise UnusableRun(f"cell {show(cell)}: target + stop + open != n")
                row = {"kind": "count", "day_type": DAY_TYPES[kind], "market": mk, "year": y,
                       "decision_slot": times[ti], "decision_ct": _ct(times[ti]), "stop_dollars": stops[si],
                       "R": rr[ri], "n": n, "target": t, "stop": s, "open": o, "minutes_sum": mins,
                       "spread_count": pd.NA, "spread_ticks_mean": pd.NA}
            elif kind == "S" and len(v) == 4:
                y, ti, cnt, t100 = v
                if not 0 <= ti < len(times) or cnt < 0:
                    raise UnusableRun(f"cell {show(cell)}: an index out of range")
                key = ("S", y, ti)
                row = {"kind": "spread", "day_type": pd.NA, "market": mk, "year": y, "decision_slot": times[ti],
                       "decision_ct": _ct(times[ti]), "stop_dollars": pd.NA, "R": pd.NA, "n": pd.NA,
                       "target": pd.NA, "stop": pd.NA, "open": pd.NA, "minutes_sum": pd.NA, "spread_count": cnt,
                       "spread_ticks_mean": (t100 / 100.0 / cnt) if cnt else pd.NA}
            else:
                raise UnusableRun(f"malformed cell {show(cell)}")
            if key in seen:
                raise UnusableRun(f"cell {key} appears twice: a scorer would count it twice")
            seen.add(key)
            rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty or not (df["kind"] == "count").any():
        raise UnusableRun("no count cell in the output.")
    for col in ("n", "target", "stop", "open", "minutes_sum", "spread_count"):
        df[col] = df[col].astype("Int64")
    counts = df[df["kind"] == "count"]
    per_entry = len(keep) // len(stops) if keep else len(rr)              # R counted for each entry and stop
    if int(counts["n"].sum()) != int(head["entries"]) * per_entry:
        raise UnusableRun(f"the cells hold {int(counts['n'].sum())} brackets, HEAD's entries x R = "
                          f"{int(head['entries']) * per_entry}.")
    facts = {"market": mk, **{k: int(head[k]) for k in HEAD_INTS}, "lean_version": _lean_version(log_path, results_path)}
    return df, facts


def _ct(slot: int) -> str:
    m = (17 * 60 + int(slot)) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


__all__ = ["HEAD_FIELDS", "rmap_head", "rmap_output_matches_kit", "parse_rmap"]
