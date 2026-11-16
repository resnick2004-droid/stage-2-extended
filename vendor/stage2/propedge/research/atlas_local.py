"""The local walk (R5, D-460): the capture kits' day close, run on the operator's Databento bars from the local store.

QuantConnect's capture kits (`propedge/data/t23_kit.py`, R147-R152) build each trading day's one-minute arrays on the
trading-day clock, classify the day, walk every bracket with `collect_core` and write records with `t23_core`. This
module does the same on `propedge.data.bars.read_bars`' bars, with the same embedded functions imported, and decodes the
records with the T23 parser's own patterns -- so a local walk and a kit's walk are comparable record for record, and
the only differences are the data (Databento against QuantConnect's AlgoSeek bars) and the ties: QuantConnect settles a
minute that reaches a target and a stop together on its one-second bars; locally there are none, so every such minute is
the stop's, marked 'u' (the kits' rule for a minute without second bars) -- the cautious side, counted.

The clock: index j is a bar's END time in minutes after 17:00 CT (1 .. 1330, the bar ending 15:10 CT the last).
Databento stamps a bar at its START (`ts`), so its index is its start's clock minute plus one.
A day is 'x' with no bars, 'e' when its last bar ends more than ten minutes before 15:10 CT (an early close, D-215),
'o' on an FOMC day, 'b' on a BLS 08:30 ET release day (walks cut at 07:30 CT), else 'n'; 'e', 'o' and 'x' days walk
nothing.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Iterable

import numpy as np
import pandas as pd

from propedge.data.t23_parser import _DAY, _OUT, _WALK
from propedge.outcomes.collect_core import C_FLAT, c_last, c_slot, c_tie, c_ties, c_walks
from propedge.outcomes.t23_core import t_a3, t_day, t_records

FLAT_MIN = C_FLAT                       # 1330: the bar ending 15:10 CT
CHICAGO = "America/Chicago"


def day_arrays(bars: pd.DataFrame) -> tuple[list, list, list, list]:
    """One trading day's charted-contract bars as the kits' arrays (o, h, l, c; length FLAT_MIN + 1, None where no bar),
    indexed by each bar's END time on the trading-day clock; bars outside 17:01 .. 15:10 CT are left out, as the kits
    leave them."""
    n = FLAT_MIN + 1
    o, h, l, c = [None] * n, [None] * n, [None] * n, [None] * n
    if bars.empty:
        return o, h, l, c
    end = pd.to_datetime(bars["ts"].astype("int64") + 60, unit="s", utc=True).dt.tz_convert(CHICAGO)
    j = np.array([c_slot(int(hh), int(mm)) for hh, mm in zip(end.dt.hour, end.dt.minute)])
    keep = (j >= 1) & (j <= FLAT_MIN)
    for jj, bo, bh, bl, bc in zip(j[keep], bars["open"].to_numpy()[keep], bars["high"].to_numpy()[keep],
                                  bars["low"].to_numpy()[keep], bars["close"].to_numpy()[keep]):
        if o[jj] is None:
            o[jj], h[jj], l[jj], c[jj] = float(bo), float(bh), float(bl), float(bc)
    return o, h, l, c


def yymmdd(day: str) -> int:
    d = date.fromisoformat(day)
    return (d.year % 100) * 10000 + d.month * 100 + d.day


def close_day(day: str, o, h, l, c, P: dict, *, fomc: set[int], bls: set[int], bls_cut: int,
              a3_slots: list[int]) -> tuple[str, list[str]]:
    """The kit's `_close_day` on one day: (the day's kind, its records -- walks then the day record)."""
    d = date.fromisoformat(day)
    key = yymmdd(day)
    last = c_last(o)
    a3 = t_a3(c, a3_slots)
    recs: list[str] = []
    if last is None:
        kind = "x"
    elif last < C_FLAT - 10:
        kind = "e"
    elif key in fomc:
        kind = "o"
    else:
        cut, kind = None, "n"
        if key in bls:
            cut, kind = bls_cut, "b"
        walks = c_walks(o, h, l, c, P, cut)

        def tie(j, entry, dd, T, S):                     # no second bars locally: the stop's, marked 'u'
            return None

        recs = t_records(walks, P, tie)
        _ = c_ties                                        # (QuantConnect's kits fetch these minutes' second bars)
    recs.append(t_day((d.year, d.month, d.day), kind, a3))
    return kind, recs


def decode(day: str, recs: Iterable[str], slots: list[int], labels: list[str], n_brackets: int) -> list[dict]:
    """The records as the T23 parser's rows (`walk` rows, then the `day` row)."""
    rows = []
    for rec in recs:
        mw = _WALK.match(rec)
        if mw:
            si, dl, side, j0 = int(mw.group(1)), int(mw.group(2)), (1 if mw.group(3) == "+" else -1), int(mw.group(4))
            r = {"kind": "walk", "date": day, "decision_ct": labels[si], "decision_slot_minutes": slots[si],
                 "delay": dl, "side": side, "entry_slot": j0}
            parts = mw.group(5).split(";")
            if len(parts) != n_brackets:
                raise ValueError(f"{day}: a walk with {len(parts)} outcomes, not {n_brackets}")
            for b, p in enumerate(parts):
                mo = _OUT.match(p)
                if not mo:
                    raise ValueError(f"{day}: a malformed outcome {p!r}")
                r.update({f"o{b}": mo.group(1), f"m{b}": int(mo.group(2)), f"u{b}": bool(mo.group(3)),
                          f"g{b}": int(mo.group(4) or 0), f"x{b}": int(mo.group(5)) if mo.group(5) is not None else 0})
            rows.append(r)
            continue
        md = _DAY.match(rec)
        if not md:
            raise ValueError(f"{day}: a malformed record {rec[:60]!r}")
        a3 = {f"a3_{i}": (None if ch == "." else (1 if ch == "+" else (-1 if ch == "-" else 0)))
              for i, ch in enumerate(md.group(3))}
        rows.append({"kind": "day", "date": day, "day_kind": md.group(2), **a3})
    return rows


def walk_store(root: str, days: list[str], q: dict[str, Any], purpose: str, *, prereg: str | None = None,
               store=None, windows=None) -> pd.DataFrame:
    """Every listed trading day of the local store walked as a kit with parameters `q` (a `t23_kit.params_t23`-shaped
    dict: 'p', 'slots', 'slot_labels', 'brackets', 'bls_cut', 'fomc_days', 'bls_days') walks it -- the T23 parser's
    table. The window guard reads the whole span first: nothing is read past a window `purpose` may read."""
    from propedge.data.bars import read_bars
    from propedge.data.windows import WINDOWS_PATH

    if not days:
        return pd.DataFrame()
    kw = {"store": store, "windows": windows or WINDOWS_PATH}
    bars = read_bars(root, min(days), max(days), purpose, prereg=prereg, what="local walk", **kw)
    by_day = dict(tuple(bars.groupby("day", sort=False)))
    fomc, bls = set(int(x) for x in q["fomc_days"]), set(int(x) for x in q["bls_days"])
    rows: list[dict] = []
    nb = len(q["brackets"])
    for day in days:
        b = by_day.get(day, pd.DataFrame(columns=bars.columns))
        o, h, l, c = day_arrays(b)
        _, recs = close_day(day, o, h, l, c, q["p"], fomc=fomc, bls=bls, bls_cut=int(q["bls_cut"]),
                            a3_slots=list(q["slots"]))
        rows.extend(decode(day, recs, list(q["slots"]), list(q["slot_labels"]), nb))
    return pd.DataFrame(rows)


__all__ = ["FLAT_MIN", "day_arrays", "yymmdd", "close_day", "decode", "walk_store"]
