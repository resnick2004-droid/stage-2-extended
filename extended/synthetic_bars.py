"""Synthetic NQ 1-minute bars in the bar store's shape (Q-11): for tests of anything that reads bars, never a model of
the market and never a result.

The frame has the columns of Stage 2's store (`vendor/stage2/data/README.md` section 5, `propedge.data.bars.COLUMNS`):
`ts` (int64, the bar's **START**, epoch seconds UTC, a whole minute), `day` (the trading day `YYYY-MM-DD`: a session
opens at 17:00 CT the evening before -- the bar's Chicago time plus seven hours, its date), `contract`, `open`, `high`,
`low`, `close` (raw prices on the 0.25 tick, no back-adjustment) and `volume`. One contract a day; a **roll** changes
the contract and moves every later price by the calendar spread, as the store's raw series does. Clocks are
America/Chicago, so a series spanning the second Sunday of March or the first Sunday of November crosses a **DST
change**: the UTC stamps of 08:30 CT move by an hour while the Chicago times do not.

Realistic enough for the feature tests -- a time-of-day volatility and volume profile (quiet overnight, a burst at the
08:30 CT open, a U-shape through the regular session), a persistent daily volatility regime, minutes without a trade
(no bar) overnight, a few holidays and an early close -- and nothing more. Every draw comes from one
`numpy.random.Generator` seeded by the caller (`seed` is required).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

CHICAGO = ZoneInfo("America/Chicago")
TICK = 0.25
SLOTS_PER_DAY = 1380          # 17:00 CT (slot 0) to the bar stamped 15:59 CT (slot 1379); CME halts 16:00-17:00
SUBSTEPS = 4                  # price steps inside a minute (o, then four steps; h/l/c from the path)

#: holidays skipped in 2021 (no trading day in the frame) -- illustrative, not CME's calendar
HOLIDAYS_2021 = frozenset({date(2021, 1, 1), date(2021, 4, 2), date(2021, 5, 31), date(2021, 7, 5), date(2021, 9, 6),
                           date(2021, 11, 25), date(2021, 12, 24)})
#: early closes (the day's last bar is stamped 12:14 CT; the regular session ends 12:00 CT)
EARLY_CLOSES_2021 = frozenset({date(2021, 11, 26)})
#: quarterly rolls in 2021: the first trading day on which the new contract is charted, and the contract
ROLLS_2021 = ((date(2021, 3, 12), "NQM1"), (date(2021, 6, 11), "NQU1"), (date(2021, 9, 10), "NQZ1"),
              (date(2021, 12, 10), "NQH2"))
FIRST_CONTRACT_2021 = "NQH1"


@dataclass(frozen=True)
class Spec:
    """What to generate. Dates are trading days (weekdays not in `holidays`), inclusive."""
    start: date
    end: date
    seed: int
    base_price: float = 13000.0
    roll_spread: float = 60.0                       # points the new contract trades above the old at a roll
    rolls: tuple[tuple[date, str], ...] = ROLLS_2021
    first_contract: str = FIRST_CONTRACT_2021
    holidays: frozenset[date] = HOLIDAYS_2021
    early_closes: frozenset[date] = EARLY_CLOSES_2021
    overnight_missing: float = 0.03                 # chance a minute 17:00-08:29 CT has no trade (no bar)
    rth_missing: float = 0.001                      # the same, 08:30-15:59 CT
    vol_scale: float = 1.0                          # multiplies every minute's price sd
    volume_profile: str = "realistic"               # or "deterministic": volume a fixed function of the CT minute
    extra: dict = field(default_factory=dict)


def trading_days(spec: Spec) -> list[date]:
    out, d = [], spec.start
    while d <= spec.end:
        if d.weekday() < 5 and d not in spec.holidays:
            out.append(d)
        d += timedelta(days=1)
    return out


def _minute_sd_ticks(slot: np.ndarray) -> np.ndarray:
    """A minute's price sd in ticks by the trading-day slot (minutes after 17:00 CT)."""
    m = (slot + 1020) % 1440                         # CT minute of the day
    sd = np.full(slot.shape, 3.0)                    # Asia
    sd[(m >= 2 * 60) & (m < 8 * 60 + 30)] = 5.0      # London
    sd[(m >= 7 * 60 + 30) & (m < 7 * 60 + 35)] = 12.0   # the 07:30 CT release minute
    sd[(m >= 8 * 60 + 30) & (m < 8 * 60 + 45)] = 16.0   # the open
    sd[(m >= 8 * 60 + 45) & (m < 10 * 60)] = 10.0
    sd[(m >= 10 * 60) & (m < 14 * 60)] = 7.0
    sd[(m >= 14 * 60) & (m < 15 * 60)] = 9.0
    sd[(m >= 15 * 60) & (m < 16 * 60)] = 5.0
    return sd


def _volume_profile(slot: np.ndarray) -> np.ndarray:
    m = (slot + 1020) % 1440
    v = np.full(slot.shape, 60.0)
    v[(m >= 2 * 60) & (m < 8 * 60 + 30)] = 180.0
    v[(m >= 7 * 60 + 30) & (m < 7 * 60 + 35)] = 900.0
    rth = (m >= 8 * 60 + 30) & (m < 15 * 60)
    x = (m[rth] - (8 * 60 + 30)) / 390.0             # 0 at the open, 1 at 15:00
    v[rth] = 700.0 + 2600.0 * np.exp(-x * 18.0) + 900.0 * x ** 4
    v[(m >= 15 * 60) & (m < 16 * 60)] = 250.0
    return v


def _deterministic_volume(slot: np.ndarray) -> np.ndarray:
    """Volume as a fixed function of the CT minute alone, identical every day (for the DST test)."""
    m = (slot + 1020) % 1440
    return 100.0 + 37.0 * (m % 11) + 500.0 * ((m >= 8 * 60 + 30) & (m < 8 * 60 + 35))


def generate(spec: Spec) -> pd.DataFrame:
    """The bars of every trading day of `spec`, sorted by `ts`, in the store's columns."""
    rng = np.random.default_rng(spec.seed)
    days = trading_days(spec)
    rolls = dict(spec.rolls)
    contract = spec.first_contract
    level_offset = 0.0
    price = spec.base_price                           # the underlying (unrolled) price, on the tick grid
    regime = 0.0
    frames = []
    for d in days:
        if d in rolls:
            contract = rolls[d]
            level_offset += spec.roll_spread
        regime = 0.8 * regime + rng.normal(0.0, 0.25)
        day_mult = float(np.exp(regime)) * spec.vol_scale
        last = SLOTS_PER_DAY if d not in spec.early_closes else (12 * 60 + 15 + 420)   # bars up to 12:14 CT
        slots = np.arange(last)
        miss_p = np.where(slots < 930, spec.overnight_missing, spec.rth_missing)
        present = rng.random(last) >= miss_p
        present[0] = True                             # the session's first minute trades
        n = last
        sd = _minute_sd_ticks(slots) * day_mult / np.sqrt(SUBSTEPS)
        steps = np.rint(rng.normal(0.0, 1.0, (n, SUBSTEPS)) * sd[:, None])
        gap = np.where(rng.random(n) < 0.15, rng.choice([-1.0, 1.0], n), 0.0)
        start_ticks = price / TICK
        # one path through the day: each minute opens at the previous close plus a small gap, then SUBSTEPS steps
        incr = np.concatenate([gap[:, None], steps], axis=1).ravel()
        path = start_ticks + np.cumsum(incr)
        path = path.reshape(n, SUBSTEPS + 1)
        o = path[:, 0]
        h = path.max(axis=1)
        l_ = path.min(axis=1)
        c = path[:, -1]
        price = float(c[-1] * TICK)
        if spec.volume_profile == "deterministic":
            vol = _deterministic_volume(slots)
        else:
            vol = _volume_profile(slots) * np.exp(rng.normal(0.0, 0.45, n)) * np.exp(regime * 0.5)
        vol = np.maximum(1, np.rint(vol)).astype(np.int64)
        start_local = datetime(d.year, d.month, d.day, 17, 0) - timedelta(days=1)
        offset = int(start_local.replace(tzinfo=CHICAGO).utcoffset().total_seconds())
        base_epoch = int((start_local - datetime(1970, 1, 1)).total_seconds()) - offset
        keep = present
        frames.append(pd.DataFrame({
            "ts": base_epoch + 60 * slots[keep].astype(np.int64),
            "day": d.isoformat(),
            "contract": contract,
            "open": o[keep] * TICK + level_offset,
            "high": h[keep] * TICK + level_offset,
            "low": l_[keep] * TICK + level_offset,
            "close": c[keep] * TICK + level_offset,
            "volume": vol[keep],
        }))
    out = pd.concat(frames, ignore_index=True)
    out["ts"] = out["ts"].astype(np.int64)
    return out.sort_values("ts", kind="stable").reset_index(drop=True)


def replace_from(bars: pd.DataFrame, cut_ts: int, seed: int, *, relabel_later_days: bool = True) -> pd.DataFrame:
    """A copy of `bars` with every bar stamped at or after `cut_ts` replaced by arbitrary values: a fresh random walk
    (seeded) at a different level and scale, random volumes, and -- for trading days wholly after the cut's day -- a
    different contract label. Stamps are kept (which minutes have a bar does not change)."""
    rng = np.random.default_rng(seed)
    out = bars.copy()
    m = out["ts"].to_numpy() >= cut_ts
    k = int(m.sum())
    if k == 0:
        return out
    walk = 9000.0 + TICK * np.cumsum(np.rint(rng.normal(0.0, 40.0, k)))
    wid = TICK * np.rint(np.abs(rng.normal(0.0, 30.0, (k, 2))))
    o = walk + TICK * np.rint(rng.normal(0.0, 10.0, k))
    c = walk
    out.loc[m, "open"] = o
    out.loc[m, "close"] = c
    out.loc[m, "high"] = np.maximum(o, c) + wid[:, 0]
    out.loc[m, "low"] = np.minimum(o, c) - wid[:, 1]
    out.loc[m, "volume"] = rng.integers(1, 50_000, k)
    if relabel_later_days:
        cut_day = _trading_day_of(cut_ts)
        later = m & (out["day"].to_numpy() > cut_day)
        out.loc[later, "contract"] = "NQZ9"
    return out


def _trading_day_of(ts: int) -> str:
    t = pd.Timestamp(ts, unit="s", tz="UTC").tz_convert(CHICAGO).tz_localize(None) + pd.Timedelta(hours=7)
    return t.date().isoformat()


def ts_of(day: date | str, hour: int, minute: int) -> int:
    """The UTC epoch seconds of CT wall-clock hh:mm on trading day `day` (17:00-23:59 belong to the evening before)."""
    d = date.fromisoformat(day) if isinstance(day, str) else day
    cal = d - timedelta(days=1) if hour >= 17 else d
    local = datetime(cal.year, cal.month, cal.day, hour, minute, tzinfo=CHICAGO)
    return int(local.timestamp())


__all__ = ["Spec", "generate", "replace_from", "trading_days", "ts_of", "CHICAGO", "TICK", "HOLIDAYS_2021",
           "EARLY_CLOSES_2021", "ROLLS_2021"]
