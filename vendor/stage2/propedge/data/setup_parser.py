"""The session-setup screen's kit outputs (R097, R098; T15 item 8, D-245) into a table: `parse_setups`.

A kit logs `SS1|HEAD` (version 1) and `SS1|END` and carries its counts in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<cells>`, cells joined by '/':

* `C<year>,<wi>,<ri>,<di>,<si>,<n>,<gapped>,<overshoot>,<max>,<stop>,<inverse>,<quotes>,<spread>` then per R
  `<target>,<stop>,<minutes>` -- per window, rule, direction (0 long, 1 short) and stop: trades; stops that opened
  through (overshoot and its maximum in tenths of the micro's tick); the stop's size in ticks summed and 1e6 / it
  summed; entries with a quote and their spread in ticks x 100 summed; per R the targets first, the stops first and the
  minutes to resolution summed;
* `D<year>,<days>,<range>,<volume>,<range days>,<trailing range>` -- as the regime map's.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields, a missing chunk or emit, chunks
that do not add up to HEAD's orders, a malformed or out-of-range cell, a cell counted twice, outcomes that do not add up
or are not monotone in R, more gapped stops than stops or more quotes than trades, no count at all, or counts that
disagree with HEAD.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from propedge.data.manual_parsers import (UnusableRun, _kv, _lean_version, _tag, orders_from_results,
                                          prefixed_lines)
from propedge.data.regime_parser import HEAD_FIELDS, HEAD_INTS

_REC = re.compile(r"G\|e=(\d+);k=(\d+);K=(\d+);x=(.*)$")
COLUMNS = ("kind", "market", "year", "window", "window_start_ct", "rule", "direction", "stop_index", "stop_multiple",
           "R", "n", "target", "stop", "open", "minutes_sum", "gapped", "overshoot_ticks_sum", "overshoot_ticks_max",
           "stop_ticks_sum", "inv_stop_sum", "quotes", "spread_ticks_sum", "days", "range_ticks_sum", "volume",
           "range_days", "trailing_range_ticks_sum")
INT_COLUMNS = ("stop_index", "n", "target", "stop", "open", "minutes_sum", "gapped", "stop_ticks_sum", "quotes", "days",
               "range_ticks_sum", "volume", "range_days", "trailing_range_ticks_sum")


def setup_head(log_path: Path) -> dict[str, str]:
    from propedge.data.setup_kit import SETUP_PREFIX

    lines = prefixed_lines(log_path, SETUP_PREFIX)
    if not any(l.startswith(SETUP_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(SETUP_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "1":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 1) in the logs: {head}")
    return head


def setup_output_matches_kit(log_path: Path, market: str) -> None:
    """D-131-style check for an attested run: HEAD names the kit's market and version and exactly its fields."""
    head = setup_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def _ct(slot: int) -> str:
    m = (17 * 60 + int(slot)) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def _row(**kw) -> dict:
    return {c: kw.get(c, pd.NA) for c in COLUMNS}


def parse_setups(log_path: Path, results_path: Path, *, market: str | None = None,
                 q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per count cell and R (`kind` count) and per session cell. `q` the kit's grid
    (`setup_kit.params`, or the kit's own from its kit.json)."""
    from propedge.data import setup_kit as sk

    head = setup_head(log_path)
    mk = market or head["market"]
    q = q or sk.params(mk)
    windows, names, rules, mults, rr = q["windows"], q["window_names"], q["rules"], q["range_multiples"], list(q["rr"])
    width = 13 + 3 * len(rr)
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
    rows, seen, entries, sessions, noatr = [], set(), 0, 0, 0
    for e in sorted(parts):
        for cell in "/".join(parts[e][k] for k in range(sizes[e])).split("/"):
            try:
                v = [int(x) for x in cell[1:].split(",")]
            except ValueError as exc:
                raise UnusableRun(f"malformed cell {cell!r}") from exc
            kind = cell[:1]
            if min(v, default=0) < 0:
                raise UnusableRun(f"cell {cell!r}: a negative count")
            if kind == "C" and len(v) == width:
                y, wi, ri, di, si, n, gp, gs, gm, ss, inv, qn, q100 = v[:13]
                out = [tuple(v[13 + 3 * k: 16 + 3 * k]) for k in range(len(rr))]
                if not (0 <= wi < len(windows) and 0 <= ri < len(rules) and di in (0, 1) and 0 <= si < len(mults)) \
                        or n < 1:
                    raise UnusableRun(f"cell {cell!r}: an index out of range or no trade")
                ts, sp = [t for t, _, _ in out], [s for _, s, _ in out]
                if any(t + s > n for t, s, _ in out):
                    raise UnusableRun(f"cell {cell!r}: target + stop > n")
                if ts != sorted(ts, reverse=True) or sp != sorted(sp):
                    raise UnusableRun(f"cell {cell!r}: outcomes not monotone in R")
                if gp > sp[-1] or gm > gs or (gp == 0 and gs > 0) or qn > n or ss < n:
                    raise UnusableRun(f"cell {cell!r}: gaps, quotes or stops do not add up")
                key = ("C", y, wi, ri, di, si)
                entries += n
                for k, R in enumerate(rr):
                    t, s, mins = out[k]
                    rows.append(_row(kind="count", market=mk, year=y, window=names[wi],
                                     window_start_ct=_ct(windows[wi][0]), rule=rules[ri],
                                     direction=("long", "short")[di], stop_index=si, stop_multiple=mults[si], R=R, n=n,
                                     target=t, stop=s, open=n - t - s, minutes_sum=mins, gapped=gp,
                                     overshoot_ticks_sum=gs / 10.0, overshoot_ticks_max=gm / 10.0, stop_ticks_sum=ss,
                                     inv_stop_sum=inv / 1e6, quotes=qn, spread_ticks_sum=q100 / 100.0))
            elif kind == "D" and len(v) == 6:
                y, days, rng, vol, rdays, tr = v
                if days < 1 or rdays > days:
                    raise UnusableRun(f"cell {cell!r}: more days with a trailing range than days")
                key = ("D", y)
                sessions += days
                noatr += days - rdays
                rows.append(_row(kind="session", market=mk, year=y, days=days, range_ticks_sum=rng, volume=vol,
                                 range_days=rdays, trailing_range_ticks_sum=tr))
            else:
                raise UnusableRun(f"malformed cell {cell!r}")
            if key in seen:
                raise UnusableRun(f"cell {key} appears twice: a scorer would count it twice")
            seen.add(key)
    df = pd.DataFrame(rows, columns=list(COLUMNS))
    if df.empty or not (df["kind"] == "count").any():
        raise UnusableRun("no count cell in the output.")
    for col in INT_COLUMNS:
        df[col] = df[col].astype("Int64")
    if entries != int(head["entries"]):
        raise UnusableRun(f"the cells hold {entries} trades, HEAD reports {head['entries']} entries.")
    full = int(head["days"]) - int(head["early"]) - int(head["noref"])
    if sessions != full:
        raise UnusableRun(f"the session cells hold {sessions} days, HEAD's full sessions are {full}.")
    if int(head["noatr"]) != noatr:
        raise UnusableRun(f"HEAD reports {head['noatr']} days without a trailing range, the cells {noatr}.")
    facts = {"market": mk, **{k: int(head[k]) for k in HEAD_INTS}, "lean_version": _lean_version(log_path, results_path)}
    return df, facts


def kit_grid(kit: dict) -> dict:
    """The grid a kit was generated with, from its kit.json, so a later edit of the config cannot relabel a run."""
    return {"windows": [tuple(int(x) for x in w) for w in kit["windows"]], "window_names": list(kit["window_names"]),
            "rules": list(kit["rules"]), "range_multiples": [float(x) for x in kit["range_multiples"]],
            "rr": tuple(float(r) for r in kit["rr"])}


__all__ = ["COLUMNS", "setup_head", "setup_output_matches_kit", "parse_setups", "kit_grid"]
