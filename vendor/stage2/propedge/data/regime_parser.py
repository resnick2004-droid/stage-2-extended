"""The regime map's kit outputs (R090-R094; T15, D-238) into a table: `parse_regime`.

A separate module so the pinned parser (`propedge/data/manual_parsers.py`, an `ENGINE_FILES` file) is not touched; it
uses that module's readers. A kit logs `RG1|HEAD` (version 1) and `RG1|END` and carries its counts in order tags
`G|e=<emit>;k=<chunk>;K=<chunks>;x=<cells>`, cells joined by '/':

* `C<year>,<ti>,<si>,<n>,<gapped>,<overshoot>,<max>,<stop>,<inverse>` then per R `<target>,<stop>,<minutes>` --
  brackets; stops that opened through (overshoot and its maximum in tenths of the micro's tick); the stop's size in
  ticks summed and 1e6 / it summed; per R the targets first, the stops first and the minutes to resolution summed;
* `S<year>,<ti>,<count>,<ticks x 100>` -- the entry bar's two-sided spread in the micro's ticks;
* `W<year>,<w>,<days>,<bars>,<volume>,<range>` -- per 30-minute window (w = 0 from 17:00): days with a bar, bars,
  volume, and the window's range in ticks, summed;
* `D<year>,<days>,<range>,<volume>,<range days>,<trailing range>` -- full sessions: their range (ticks) and volume
  summed, and the trailing range the range stops were cut from (ticks) summed over the days that had one.

Refused (`UnusableRun`): a missing END or HEAD, a HEAD without exactly the kit's fields, a missing chunk or emit, chunks
that do not add up to HEAD's orders, a malformed or out-of-range cell, a cell counted twice, a cell whose outcomes do
not add up or are not monotone in R (a farther target is hit no more often, a stop no less), more gapped stops than
stops, a fixed stop whose size is not its own, no count at all, or counts that disagree with HEAD.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from propedge.data.manual_parsers import (UnusableRun, _kv, _lean_version, _tag, orders_from_results,
                                          prefixed_lines)

_REC = re.compile(r"G\|e=(\d+);k=(\d+);K=(\d+);x=(.*)$")
HEAD_INTS = ("days", "warm", "entries", "emits", "orders", "switches", "lost", "late", "early", "noref", "noatr", "bad",
             "bars", "quotes", "wide", "badq")
HEAD_FIELDS = frozenset({"v", "market", *HEAD_INTS})
N_WINDOWS = 45                       # 30-minute windows from 17:00; the last is 15:00-15:10
COLUMNS = ("kind", "market", "year", "decision_slot", "decision_ct", "window", "window_ct", "stop_index", "stop_kind",
           "stop_value", "R", "n", "target", "stop", "open", "minutes_sum", "gapped", "overshoot_ticks_sum",
           "overshoot_ticks_max", "stop_ticks_sum", "inv_stop_sum", "spread_count", "spread_ticks_mean", "days", "bars",
           "volume", "range_ticks_sum", "range_days", "trailing_range_ticks_sum")
INT_COLUMNS = ("decision_slot", "window", "stop_index", "n", "target", "stop", "open", "minutes_sum", "gapped",
               "stop_ticks_sum", "spread_count", "days", "bars", "volume", "range_ticks_sum", "range_days",
               "trailing_range_ticks_sum")


def regime_head(log_path: Path) -> dict[str, str]:
    from propedge.data.regime_kit import REGIME_PREFIX

    lines = prefixed_lines(log_path, REGIME_PREFIX)
    if not any(l.startswith(REGIME_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(REGIME_PREFIX + "|HEAD|")), None)
    if head is None or set(head) != HEAD_FIELDS or head.get("v") != "1":
        raise UnusableRun(f"no HEAD line with exactly the kit's fields (version 1) in the logs: {head}")
    return head


def regime_output_matches_kit(log_path: Path, market: str) -> None:
    """D-131-style check for an attested run: HEAD names the kit's market and version and exactly its fields."""
    head = regime_head(log_path)
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}, the kit is {market!r}.")


def kit_grid(kit: dict) -> dict:
    """The grid a kit was generated with, from its kit.json, so a later edit of the config cannot relabel a run."""
    return {"times": [int(t) for t in kit["times"]], "rr": tuple(float(r) for r in kit["rr"]),
            "micro_tick": float(kit["micro_tick"]), "stops_points": [float(x) for x in kit["stops_points"]],
            "range_multiples": [float(x) for x in kit["range_multiples"]]}


def _ct(slot: int) -> str:
    m = (17 * 60 + int(slot)) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def _row(**kw) -> dict:
    return {c: kw.get(c, pd.NA) for c in COLUMNS}


def parse_regime(log_path: Path, results_path: Path, *, market: str | None = None,
                 q: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """(table, facts): one row per bracket cell and R (`kind` count), per spread, window and session cell. `q` is the
    grid the kit was generated with (`kit_grid(kit.json)`); without it, the config's."""
    from propedge.data import regime_kit as rk

    head = regime_head(log_path)
    mk = market or head["market"]
    q = q or rk.params(mk)
    times, rr, tick = q["times"], list(q["rr"]), q["micro_tick"]
    fixed, mults = q["stops_points"], q["range_multiples"]
    n_stops, width = len(fixed) + len(mults), 9 + 3 * len(rr)
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
    rows, seen, entries, sessions, noatr_max = [], set(), 0, 0, 0
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
                y, ti, si, n, gp, gs, gm, ss, inv = v[:9]
                out = [tuple(v[9 + 3 * k: 12 + 3 * k]) for k in range(len(rr))]
                if not (0 <= ti < len(times) and 0 <= si < n_stops) or n < 1:
                    raise UnusableRun(f"cell {cell!r}: an index out of range or no bracket")
                key = ("C", y, ti, si)
                ts = [t for t, _, _ in out]
                sp = [s for _, s, _ in out]
                if any(t + s > n for t, s, _ in out):
                    raise UnusableRun(f"cell {cell!r}: target + stop > n")
                if ts != sorted(ts, reverse=True) or sp != sorted(sp):
                    raise UnusableRun(f"cell {cell!r}: outcomes not monotone in R")
                if gp > sp[-1] or gm > gs or (gp == 0 and gs > 0):    # a gap under a twentieth of a tick rounds to 0
                    raise UnusableRun(f"cell {cell!r}: gapped stops do not add up")
                if si < len(fixed):
                    st = int(round(fixed[si] / tick))
                    if ss != n * st:
                        raise UnusableRun(f"cell {cell!r}: a fixed stop of {st} ticks summed to {ss} over {n}")
                    sk, sv = "points", fixed[si]
                else:
                    sk, sv = "range", mults[si - len(fixed)]
                entries += n
                for k, R in enumerate(rr):
                    t, s, mins = out[k]
                    rows.append(_row(kind="count", market=mk, year=y, decision_slot=times[ti],
                                     decision_ct=_ct(times[ti]), stop_index=si, stop_kind=sk, stop_value=sv, R=R, n=n,
                                     target=t, stop=s, open=n - t - s, minutes_sum=mins, gapped=gp,
                                     overshoot_ticks_sum=gs / 10.0, overshoot_ticks_max=gm / 10.0, stop_ticks_sum=ss,
                                     inv_stop_sum=inv / 1e6))
            elif kind == "S" and len(v) == 4:
                y, ti, cnt, t100 = v
                if not 0 <= ti < len(times):
                    raise UnusableRun(f"cell {cell!r}: an index out of range")
                key = ("S", y, ti)
                rows.append(_row(kind="spread", market=mk, year=y, decision_slot=times[ti], decision_ct=_ct(times[ti]),
                                 spread_count=cnt, spread_ticks_mean=(t100 / 100.0 / cnt) if cnt else pd.NA))
            elif kind == "W" and len(v) == 6:
                y, w, days, bars, vol, rng = v
                if not 0 <= w < N_WINDOWS or days < 1 or bars < days:
                    raise UnusableRun(f"cell {cell!r}: an index out of range or no bar")
                key = ("W", y, w)
                rows.append(_row(kind="window", market=mk, year=y, window=w, window_ct=_ct(30 * w), days=days,
                                 bars=bars, volume=vol, range_ticks_sum=rng))
            elif kind == "D" and len(v) == 6:
                y, days, rng, vol, rdays, tr = v
                if days < 1 or rdays > days:
                    raise UnusableRun(f"cell {cell!r}: more days with a trailing range than days")
                key = ("D", y)
                sessions += days
                noatr_max += days - rdays
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
        raise UnusableRun(f"the cells hold {entries} brackets, HEAD reports {head['entries']} entries.")
    full = int(head["days"]) - int(head["early"]) - int(head["noref"])
    if sessions != full:
        raise UnusableRun(f"the session cells hold {sessions} days, HEAD's full sessions are {full}.")
    if int(head["noatr"]) != noatr_max:
        raise UnusableRun(f"HEAD reports {head['noatr']} days without a trailing range, the cells {noatr_max}.")
    facts = {"market": mk, **{k: int(head[k]) for k in HEAD_INTS}, "lean_version": _lean_version(log_path, results_path)}
    return df, facts


def regime_usability(log_path: Path, min_days: int, limit_hit: str = "none") -> list[str]:
    """D-230's single test for a confirmation run (D-242), judged from its log alone -- no count is parsed: no END or
    HEAD, an error or a time limit in the log or reported by the operator, or HEAD's days below `min_days`. Empty:
    usable."""
    out = []
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    if re.search(r"runtime error|time ?limit|timed out|exceeded", text, re.IGNORECASE):
        out.append("the log reports an error or a time limit")
    if str(limit_hit).strip().lower() not in ("", "none"):
        out.append(f"the operator reports a limit: {limit_hit}")
    try:
        head = regime_head(log_path)
    except UnusableRun as exc:
        return out + [str(exc)]
    if int(head.get("days", 0)) < int(min_days):
        out.append(f"HEAD reports {head.get('days')} days, fewer than the {min_days} required")
    return out


def parse_regime_confirm(log_path: Path, results_path: Path, q: dict, months: list[str]) -> tuple[pd.DataFrame, dict]:
    """NQB2's confirmation (D-242): (table, facts), one row per month, slot and leg (`kind` count) and per month and
    slot (`kind` spread). `q` is `regime_kit.confirm_params`; `months` the registered 'YYYY-MM' blocks. Any cell outside
    the registered legs, slots and months -- or any window, range or volume cell -- is refused, and a refusal never
    echoes a cell, which carries held-back counts."""
    head = regime_head(log_path)
    times, keep, tick = q["times"], [tuple(k) for k in q["keep"]], q["micro_tick"]
    blocks = {int(m.replace("-", "")) for m in months}
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
    rows, seen, entries, sessions = [], set(), 0, 0
    for e in sorted(parts):
        for cell in "/".join(parts[e][k] for k in range(sizes[e])).split("/"):
            kind = cell[:1]
            try:
                v = [int(x) for x in cell[1:].split(",")]
            except ValueError as exc:
                raise UnusableRun(f"a malformed cell of kind {kind!r}") from exc
            if min(v, default=0) < 0 or not v or v[0] not in blocks:
                raise UnusableRun(f"a cell of kind {kind!r} with a negative count or outside the registered months")
            if kind == "C" and len(v) == 12:
                b, ti, leg, n, gp, gs, gm, ss, inv, t, s, mins = v
                if not (0 <= ti < len(times) and 0 <= leg < len(keep)) or n < 1:
                    raise UnusableRun("a count cell outside the registered slots or legs (D-242)")
                stop, R = keep[leg]
                if t + s > n or gp > s or gm > gs or (gp == 0 and gs > 0):
                    raise UnusableRun("a count cell whose outcomes or gaps do not add up")
                if ss != n * int(round(stop / tick)):
                    raise UnusableRun("a count cell whose stop is not its leg's")
                key = ("C", b, ti, leg)
                entries += n
                rows.append({"kind": "count", "month": f"{b // 100}-{b % 100:02d}", "year": b // 100,
                             "decision_slot": times[ti], "leg": ("combine", "funded")[leg], "stop_points": stop, "R": R,
                             "n": n, "target": t, "stop": s, "open": n - t - s, "minutes_sum": mins, "gapped": gp,
                             "overshoot_ticks_sum": gs / 10.0, "overshoot_ticks_max": gm / 10.0,
                             "spread_count": pd.NA, "spread_ticks_mean": pd.NA, "days": pd.NA})
            elif kind == "S" and len(v) == 4:
                b, ti, cnt, t100 = v
                if not 0 <= ti < len(times):
                    raise UnusableRun("a spread cell outside the registered slots")
                key = ("S", b, ti)
                rows.append({"kind": "spread", "month": f"{b // 100}-{b % 100:02d}", "year": b // 100,
                             "decision_slot": times[ti], "leg": pd.NA, "stop_points": pd.NA, "R": pd.NA, "n": pd.NA,
                             "target": pd.NA, "stop": pd.NA, "open": pd.NA, "minutes_sum": pd.NA, "gapped": pd.NA,
                             "overshoot_ticks_sum": pd.NA, "overshoot_ticks_max": pd.NA, "spread_count": cnt,
                             "spread_ticks_mean": (t100 / 100.0 / cnt) if cnt else pd.NA, "days": pd.NA})
            elif kind == "D" and len(v) == 6:
                b, days, rng, vol, rdays, tr = v
                if days < 1 or rng or vol or rdays or tr:
                    raise UnusableRun("a session cell carrying more than its day count (D-242)")
                key = ("D", b)
                sessions += days
                rows.append({"kind": "session", "month": f"{b // 100}-{b % 100:02d}", "year": b // 100,
                             "days": days})
            else:
                raise UnusableRun(f"a cell of kind {kind!r} the confirmation does not count (D-242)")
            if key in seen:
                raise UnusableRun(f"a cell of kind {kind!r} appears twice: a scorer would count it twice")
            seen.add(key)
    df = pd.DataFrame(rows)
    if df.empty or not (df["kind"] == "count").any():
        raise UnusableRun("no count cell in the output.")
    for col in ("decision_slot", "n", "target", "stop", "open", "minutes_sum", "gapped", "spread_count", "days"):
        df[col] = df[col].astype("Int64")
    if entries != int(head["entries"]):
        raise UnusableRun("the count cells' brackets disagree with HEAD's entries.")
    if sessions != int(head["days"]) - int(head["early"]) - int(head["noref"]):
        raise UnusableRun("the session cells' days disagree with HEAD's full sessions.")
    if int(head["noatr"]) != 0:
        raise UnusableRun("HEAD reports days without a trailing range; the confirmation counts no range stop.")
    facts = {"market": head["market"], **{k: int(head[k]) for k in HEAD_INTS},
             "lean_version": _lean_version(log_path, results_path)}
    return df, facts


__all__ = ["HEAD_FIELDS", "COLUMNS", "regime_head", "regime_output_matches_kit", "kit_grid", "parse_regime",
           "regime_usability", "parse_regime_confirm"]
