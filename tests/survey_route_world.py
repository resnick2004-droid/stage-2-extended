"""Q-215's synthetic world for `extended/survey_route.py`: the real Topstep $50K lever space with S1 read from a
synthetic range (the loader's reading stood in: the tests' own k ranges, never `results/s1_range.csv`), synthetic NQ
bars (`extended/synthetic_bars.py`) and a synthetic void calendar (every overnight clean, the toys' own last bars). No
bar store, no result file, no held-out day.

Seeds, named by role (searched on 2026-11-27 over every ref, every worktree, the main tree and the vendored snapshot:
no other token of any of them): `SEED_ROUTE_BARS` the toys' bars; `SEED_ROUTE_SHIFT` the shift test's arbitrary values,
the k-th cut taking the k-th child (`numpy.random.SeedSequence(SEED_ROUTE_SHIFT).spawn`);
`SEED_ROUTE_COINS` the race's coin field in the end-to-end check (`survey_route_child.py race`).
"""
from __future__ import annotations

import contextlib
from datetime import date
from typing import Any, Mapping

import numpy as np
import pandas as pd

from extended import day_calendar as DC
from extended import lever_space as LS
from extended import search_space as SS
from extended import synthetic_bars as SB
from extended import triggers as T
from extended import vol_descriptive as V
from extended import walker as W

SEED_ROUTE_BARS = 4215071
SEED_ROUTE_SHIFT = 4215072
SEED_ROUTE_COINS = 4215073
START, END = date(2021, 1, 4), date(2021, 4, 30)          # a roll (03-12) and the US clock change (03-14) inside
#: the tests' stand-in for S1's reading: k ranges per lever session (multiples of the trailing range)
K_RANGES = {"evening": (0.8, 4.0), "asia": (0.3, 2.0), "london": (0.2, 1.5), "ny_am": (0.05, 0.6),
            "ny_pm": (0.05, 0.6)}
SLOTS = {"london": 1, "ny_am": 1, "ny_pm": 1}
RL3_PARAMS = {"kind": "pd", "cutoff": W.slot(14, 30)}
SIDE_RULES = {"p14": "with_breakout", "rl3": "fade"}
FEE = 1.22                                                # a toy fee a micro at any stop
TICK_VALUE = 0.5
ENTRY_TICKS = 1.0
FRESH_RR = 1.5                                            # the engine's combine R in the toys (never a route input)


@contextlib.contextmanager
def s1_loaded(ranges: Mapping[str, tuple[float, float]] = K_RANGES):
    """`lever_space`'s S1 reading stood in by `ranges` (its file and manifest are never read)."""
    det = {"by_session": dict(ranges), "share": 0.95, "n_days": 0, "result": "synthetic", "sha256": "0" * 64,
           "git_commit": "synthetic", "caps": LS.stop_caps(), "unit": "k x the session's trailing range"}
    old = (LS._COMPUTED["S1"], LS._s1_reading)
    LS._COMPUTED["S1"] = lambda: True
    LS._s1_reading = lambda: ({}, det)
    try:
        yield
    finally:
        LS._COMPUTED["S1"], LS._s1_reading = old


def space(slots: Mapping[str, int] = SLOTS, *, with_s1: bool = True) -> SS.Space:
    if not with_s1:
        return SS.from_lever_space(slots=dict(slots))
    with s1_loaded():
        return SS.from_lever_space(slots=dict(slots))


def bars(start: date = START, end: date = END) -> pd.DataFrame:
    return SB.generate(SB.Spec(start=start, end=end, seed=SEED_ROUTE_BARS))


def shift_seed(k: int) -> int:
    return int(np.random.SeedSequence(SEED_ROUTE_SHIFT).spawn(k + 1)[k].generate_state(1)[0])


def fake_sources(b: pd.DataFrame) -> DC.Sources:
    """The toys' void calendar: their days, their last bars (CT), every overnight clean."""
    days = sorted({date.fromisoformat(d) for d in b["day"].astype(str).unique()})
    last = b.groupby("day")["ts"].max()
    ct = pd.to_datetime(last.to_numpy(), unit="s", utc=True).tz_convert(SB.CHICAGO)
    lb = {date.fromisoformat(str(d)): f"{t.hour:02d}:{t.minute:02d}" for d, t in zip(last.index, ct)}
    flags = {d: {"day": d.isoformat(), "verdict": "OK", "void": "", "missing_after_reopen": "0", "special": ""}
             for d in days}
    return DC.Sources(days, {}, frozenset(), frozenset(), lb, frozenset(), frozenset(), flags, None)


def calendar_of(days) -> DC.Sources:
    """A clean void calendar over `days` (ISO dates), every day's last bar 15:59 CT."""
    ds = [date.fromisoformat(d) for d in days]
    flags = {d: {"day": d.isoformat(), "verdict": "OK", "void": "", "missing_after_reopen": "0", "special": ""}
             for d in ds}
    return DC.Sources(ds, {}, frozenset(), frozenset(), {d: "15:59" for d in ds}, frozenset(), frozenset(), flags,
                      None)


def day_kinds(hist: T.History) -> dict[str, str]:
    """The walk's day kind of each day (`vol_descriptive.day_kind` on the walker's 17:01-15:10 arrays), no calendar."""
    return {d: V.day_kind(hist.o[i][:W.C_FLAT + 1], d, (), ()) for i, d in enumerate(hist.days)}


def base_point(sp: SS.Space) -> dict[str, Any]:
    """A point the space admits with every slot off: each design-wide lever at its first cell or its low end, T7
    off, A4 standard and A12 zero (Back2Funded under the No Activation Fee path is refused by the record)."""
    d: dict[str, Any] = {}
    for dim in sp.dims:
        if dim.slot is not None:
            d[dim.name] = SS.OFF if dim.name == SS.slot_dim(dim.slot, "on") else None
        elif dim.kind == SS.CAT:
            d[dim.name] = dim.values[0]
        else:
            d[dim.name] = int(dim.lo) if dim.kind == SS.INT else float(dim.lo)
    d.update({"T7": "off", "A4": "standard", "A12": 0})
    return d


def with_slot(sp: SS.Space, d: Mapping[str, Any], slot: str, **lv: Any) -> dict[str, Any]:
    out = dict(d)
    out[SS.slot_dim(slot, "on")] = SS.ON
    for k, v in lv.items():
        out[SS.slot_dim(slot, k)] = v
    return out


def point(sp: SS.Space) -> dict[str, Any]:
    """The tests' three-component design: London P-14 at market (L 5), NY AM RL3 (pd, fade), NY PM P-14 limit (L 2)."""
    d = base_point(sp)
    d = with_slot(sp, d, "london.0", T1="p14", T4=5, T5="market", first=60, last=300, S1=0.5, S2=1.5)
    d = with_slot(sp, d, "ny_am.0", T1="rl3", T4=None, T5=SS.TICKET, first=30, last=120, S1=0.2, S2=1.0)
    d = with_slot(sp, d, "ny_pm.0", T1="p14", T4=2, T5="limit", first=0, last=120, S1=0.15, S2=2.0)
    for name in sp.names():
        d.setdefault(name, None)
    return d


def ts_of_slot(day: str, slot: int) -> int:
    """The UTC stamp of trading-day slot `slot` (minutes after 17:00 CT the evening before) on trading day `day`."""
    m = (17 * 60 + int(slot)) % 1440
    return SB.ts_of(day, m // 60, m % 60)


def build_kw(hist: T.History, cal: DC.Sources) -> dict[str, Any]:
    return dict(cal=cal, day_kinds=day_kinds(hist), news_windows=None,
                fee_for_stop=lambda s: FEE, tick_value=TICK_VALUE, market_entry_ticks=ENTRY_TICKS)
