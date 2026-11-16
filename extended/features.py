"""The feature library (Q-11; bootstrap 6.2; `.claude/skills/feature-rules`): normalised OHLCV features of NQ at the
alert marks of US regular hours, each computed only from bars closed by the alert.

    from extended import features as F
    X = F.compute(bars)                    # one row per (trading day, alert mark); F.REGISTRY documents every column
    print(F.describe())                    # the registry as a table: formula, window, normaliser, the bars it reads

**Input.** Bars in the bar store's shape (`vendor/stage2/data/README.md` section 5; `propedge.data.bars.read_bars`
returns them): `ts` (int64, the bar's **OPEN** time, epoch seconds UTC, a whole minute), `contract`, `open`, `high`,
`low`, `close`, `volume`, and optionally `day` (checked against `ts`). Nothing here reads a file of bars: the caller
passes them, through the window guard, so this module can never read NQ from 2026-07-17 on its own.

**The clock.** A trading day opens at 17:00 CT the evening before (the bar's Chicago time plus seven hours, its date --
the store's rule). A **slot** is minutes after that 17:00 (`slot(8, 30)` = 930); Chicago wall-clock time throughout,
so a DST change moves the UTC stamps, never the slots. A bar stamped hh:mm covers hh:mm:00-hh:mm:59 and closes at
hh:mm + 1. **At an alert at slot s the readable bars are those stamped at slots <= s - 1 of the day, and every bar of an
earlier trading day** (feature-rules section 1) -- that is the only access pattern below: every per-alert quantity is a
slice `[..., :s]` or a prefix sum ending at `s - 1`; every day-level quantity used on day d is built from days before
d, or from the day's own bars before a level's freeze slot <= s - 1.

**The alert marks** (`ALERT_MARKS`): every five minutes from 08:30 to 15:00 CT (79 marks), the regular session's. An
entry at the open of the bar stamped t + 5 (Stage 2 D-266) is the caller's; this module only describes the market at t.

**The normalisers** -- every one from the past only (feature-rules section 2):

* `atr14` -- the mean daily true range of the **14 trading days before** the alert's day: TR_d = max(H_d, C_{d-1}) -
  min(L_d, C_{d-1}) over the whole trading day's bars (17:00-16:00), the previous day's close used only when the
  previous day in the frame charted the same contract, else TR_d = H_d - L_d (a roll's calendar spread is not a
  range). `atr5` the same over 5 days. NaN until 14 (5) earlier days exist in the frame.
* **time-of-day medians** -- the median of the same quantity at the same CT slot over the **20 trading days before**
  the alert's day (at least 10 of them with a value, else NaN).
* the session's own range (positions in a range), the trailing hour (`vol_accel`), the trailing window itself
  (`up_share_30`, `eff_30`, `rv_ratio`).

Price levels never enter raw: every price is inside a difference, divided by `atr14` or by a range, or (the two level
features, `d_round`, `atr_rel`) explicitly a function of the level, flagged `level_dependent`.

**Rolls and missing history.** The store charts one contract a day and never back-adjusts, so a level of the previous
day is the old contract's price on a roll day. Every feature that differences prices **across trading days**
(`cross_day`) is NaN on a day whose previous frame day charted another contract (or does not exist); ranges and
returns of the previous day alone are within one contract and stay. Multi-day returns chain each day's change within
its contract (C_d - C_{d-1}, or C_d - O_d on a roll day). A minute without a trade has no bar; windows read whatever
bars are present.

**Calendars** (`load_calendars`; feature-rules section 1: only as published in advance): BLS 08:30 ET release days
from Stage 2's schedule-page parses (`vendor/stage2/data/release_days_0830_*.csv`, provenance beside them); FOMC
statement days from Stage 2's statement lists (`vendor/stage2/config/sources/fomc_statements*.csv`) -- the **scheduled**
meetings only for `days_to_fomc` (unscheduled meetings, notation votes and conference calls were not known in advance;
the meeting of 17-18 March 2020, scheduled and then cancelled on 15 March 2020, counts as scheduled until the last
trading day before its cancellation), every statement already made for `days_since_fomc` and for the population's FOMC
exclusion (`fomc_statements`, Stage 2's day set).

The look-ahead proof is the tests, not this text: `tests/test_features_lookahead.py` replaces (and separately deletes)
every bar stamped at or after a cut and asserts every feature and every normaliser at every alert up to the cut is
unchanged, across sessions, the first minutes, a roll and a DST change; `tests/test_features.py` holds each formula to
a direct, timestamp-filtered reference and to the registry's documentation.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

CHICAGO = ZoneInfo("America/Chicago")
N_SLOTS = 1440                                   # a trading day's minutes from 17:00 CT (the store's bars use 0..1379)


def slot(hour: int, minute: int) -> int:
    """CT wall-clock hh:mm on the trading-day clock: minutes after 17:00 CT of the evening the day opens."""
    m = int(hour) * 60 + int(minute)
    return m - 1020 if m >= 1020 else m + 420


def slot_label(s: int) -> str:
    m = (int(s) + 1020) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


RTH_OPEN = slot(8, 30)                           # 930: the first regular-session bar is stamped 08:30
OR_END = slot(9, 0)                              # 960: the opening range is the bars stamped 08:30-08:59
RTH_END = slot(15, 0)                            # 1320: the regular session's bars are stamped 08:30-14:59
ALERT_MARKS: tuple[int, ...] = tuple(range(RTH_OPEN, RTH_END + 1, 5))      # 08:30, 08:35, ..., 15:00 CT (79)

ATR_DAYS, ATR_SHORT_DAYS = 14, 5
TOD_DAYS, TOD_MIN_DAYS = 20, 10
FOMC_CAP = 30                                    # days_to_fomc / days_since_fomc are capped at 30 calendar days
ROUND_STEP = 100.0                               # d_round: the nearest multiple of 100 index points

# ------------------------------------------------------------------------------------------------------------ registry


@dataclass(frozen=True)
class Feature:
    """One feature's documentation. `available_from`: the earliest alert slot at which it has a value on a day with
    its bars and history; `cross_day`: it differences prices across trading days (NaN on a roll day); `warmup`: the
    trading days of history before the alert's day that it needs; `level_dependent`: a function of the price level
    itself (not translation-invariant across a roll); `daily`: one value a trading day (frozen before its first alert,
    or at `available_from`), the same at every later alert of the day."""
    name: str
    group: str
    formula: str
    window: str
    normaliser: str
    reads: str
    available_from: int = RTH_OPEN
    cross_day: bool = False
    warmup: int = 0
    level_dependent: bool = False
    kind: str = "real"
    daily: bool = False


_C = "c = the close of the last bar stamped <= t-1"
_A = "atr14"
_TOD = "its median at the same CT slot over the 20 prior trading days"

REGISTRY: tuple[Feature, ...] = (
    # returns over several windows, ATR units, within the trading day
    *(Feature(f"ret_{w}", "return", f"(c - close of the last bar stamped <= t-1-{w}min) / atr14", f"{w} min", _A,
              f"the day's bars stamped <= t-1min; atr14's 14 prior days", warmup=ATR_DAYS) for w in (5, 15, 30, 60, 120)),
    Feature("ret_rth", "return", "(c - open of the first bar stamped >= 08:30) / atr14", "08:30 to t", _A,
            "the day's bars stamped 08:30..t-1min", available_from=RTH_OPEN + 5, warmup=ATR_DAYS),
    Feature("ret_day", "return", "(c - open of the trading day's first bar) / atr14", "17:00 to t", _A,
            "the day's bars stamped <= t-1min", warmup=ATR_DAYS),
    # ranges
    Feature("rng_15", "range", "(max high - min low of the bars stamped t-15..t-1) / atr14", "15 min", _A,
            "the day's bars stamped t-15..t-1min", warmup=ATR_DAYS),
    Feature("rng_60", "range", "(max high - min low of the bars stamped t-60..t-1) / atr14", "60 min", _A,
            "the day's bars stamped t-60..t-1min", warmup=ATR_DAYS),
    Feature("range_day", "range", "(day high - day low so far) / atr14", "17:00 to t", _A,
            "the day's bars stamped <= t-1min", warmup=ATR_DAYS),
    Feature("range_rth", "range", "(regular-session high - low so far) / atr14", "08:30 to t", _A,
            "the day's bars stamped 08:30..t-1min", available_from=RTH_OPEN + 5, warmup=ATR_DAYS),
    # positions in ranges (self-normalised)
    Feature("pos_day", "position", "(c - day low) / (day high - day low), so far", "17:00 to t", "the day's own range",
            "the day's bars stamped <= t-1min"),
    Feature("pos_rth", "position", "(c - RTH low) / (RTH high - RTH low), so far", "08:30 to t",
            "the session's own range", "the day's bars stamped 08:30..t-1min", available_from=RTH_OPEN + 5),
    Feature("pos_prior", "position", "(c - prior RTH low) / (prior RTH high - prior RTH low)",
            "the prior regular session", "the prior session's range",
            "the prior day's bars stamped 08:30..14:59; c", cross_day=True, warmup=1),
    # distances to frozen levels, ATR units
    Feature("d_pdh", "level", "(c - prior RTH high) / atr14", "the prior regular session", _A,
            "the prior day's bars stamped 08:30..14:59; c", cross_day=True, warmup=ATR_DAYS),
    Feature("d_pdl", "level", "(c - prior RTH low) / atr14", "the prior regular session", _A,
            "the prior day's bars stamped 08:30..14:59; c", cross_day=True, warmup=ATR_DAYS),
    Feature("d_pdc", "level", "(c - prior RTH close: the last close stamped <= 14:59) / atr14",
            "the prior regular session", _A, "the prior day's bars stamped <= 14:59; c", cross_day=True,
            warmup=ATR_DAYS),
    Feature("d_onh", "level", "(c - overnight high) / atr14; overnight = bars stamped 17:00..08:29, frozen at 08:30",
            "17:00 to 08:30", _A, "the day's bars stamped 17:00..08:29; c", warmup=ATR_DAYS),
    Feature("d_onl", "level", "(c - overnight low) / atr14", "17:00 to 08:30", _A,
            "the day's bars stamped 17:00..08:29; c", warmup=ATR_DAYS),
    Feature("range_on", "level", "(overnight high - overnight low) / atr14", "17:00 to 08:30", _A,
            "the day's bars stamped 17:00..08:29", warmup=ATR_DAYS, daily=True),
    Feature("gap", "level", "(the last close stamped <= 08:29 - prior RTH close) / atr14", "prior 14:59 to 08:30",
            _A, "the prior day's bars stamped <= 14:59; the day's bars stamped <= 08:29", cross_day=True,
            warmup=ATR_DAYS, daily=True),
    Feature("d_vwap", "level", "(c - RTH VWAP so far: sum((h+l+c)/3 x volume) / sum(volume)) / atr14", "08:30 to t",
            _A, "the day's bars stamped 08:30..t-1min", available_from=RTH_OPEN + 5, warmup=ATR_DAYS),
    Feature("d_round", "level", "(c - the nearest multiple of 100 index points) / atr14", "the last bar", _A,
            "the last bar stamped <= t-1min", warmup=ATR_DAYS, level_dependent=True),
    # the opening range (bars stamped 08:30-08:59, frozen when the 08:59 bar closes at 09:00)
    Feature("or_width", "opening range", "(OR high - OR low) / atr14, OR = the bars stamped 08:30..08:59",
            "08:30 to 09:00", _A, "the day's bars stamped 08:30..08:59", available_from=OR_END, warmup=ATR_DAYS,
            daily=True),
    Feature("or_pos", "opening range", "(c - OR low) / (OR high - OR low)", "08:30 to 09:00", "the OR's own range",
            "the day's bars stamped 08:30..08:59; c", available_from=OR_END),
    # volume against its time-of-day median (log ratios)
    Feature("vol_5", "volume", "log((V5 + 1) / (median V5 + 1)), V5 = volume of the bars stamped t-5..t-1", "5 min",
            _TOD, "the day's bars stamped t-5..t-1min; the same slots of the 20 prior days", warmup=TOD_MIN_DAYS),
    Feature("vol_30", "volume", "log((V30 + 1) / (median V30 + 1))", "30 min", _TOD,
            "the day's bars stamped t-30..t-1min; the same slots of the 20 prior days", warmup=TOD_MIN_DAYS),
    Feature("vol_day", "volume", "log((Vday + 1) / (median Vday + 1)), Vday = the day's volume stamped <= t-1",
            "17:00 to t", _TOD, "the day's bars stamped <= t-1min; the same slots of the 20 prior days",
            warmup=TOD_MIN_DAYS),
    Feature("vol_accel", "volume", "log((V5 / 5 + 1) / (V60 / 60 + 1))", "5 vs 60 min", "the trailing hour's own rate",
            "the day's bars stamped t-60..t-1min"),
    # realised volatility (rv_w = root mean square of 1-minute close changes, consecutive bars of the day)
    Feature("rv_ratio", "volatility", "rv_15 / rv_60", "15 vs 60 min", "the trailing hour's own rv",
            "the day's bars stamped t-61..t-1min"),
    Feature("rv_tod", "volatility", "log(rv_60 / median rv_60)", "60 min", _TOD,
            "the day's bars stamped t-61..t-1min; the same slots of the 20 prior days", warmup=TOD_MIN_DAYS),
    Feature("rv_atr", "volatility", "rv_60 / atr14", "60 min", _A, "the day's bars stamped t-61..t-1min",
            warmup=ATR_DAYS),
    Feature("atr_ratio", "volatility", "atr5 / atr14", "5 vs 14 days", "atr14", "the 14 prior trading days",
            warmup=ATR_DAYS, daily=True),
    Feature("range_prior", "volatility", "(prior RTH high - prior RTH low) / atr14", "the prior regular session", _A,
            "the prior day's bars stamped 08:30..14:59", warmup=ATR_DAYS, daily=True),
    Feature("atr_rel", "volatility", "atr14 / c x 10,000 (basis points of the price)", "14 days", "the price level",
            "the 14 prior trading days; c", warmup=ATR_DAYS, level_dependent=True),
    # trend and path shape
    Feature("ret_prior", "trend", "(prior RTH close - prior RTH open) / atr14", "the prior regular session", _A,
            "the prior day's bars stamped 08:30..14:59", warmup=ATR_DAYS, daily=True),
    Feature("ret_5d", "trend", "sum of the 5 prior days' changes (C_d - C_{d-1}; C_d - O_d on a roll day) / atr14",
            "5 days", _A, "the 6 prior trading days' first and last bars", warmup=ATR_DAYS, daily=True),
    Feature("ret_20d", "trend", "sum of the 20 prior days' changes, chained within the contract / atr14", "20 days",
            _A, "the 21 prior trading days' first and last bars", warmup=20, daily=True),
    Feature("ext_ma60", "trend", "(c - mean close of the bars stamped t-60..t-1) / atr14", "60 min", _A,
            "the day's bars stamped t-60..t-1min", warmup=ATR_DAYS),
    Feature("up_share_30", "trend", "share of rising 1-minute close changes among those of the bars stamped t-30..t-1",
            "30 min", "a share", "the day's bars stamped t-31..t-1min"),
    Feature("eff_30", "trend", "|c - close as of t-31| / sum |1-minute close changes| over t-30..t-1", "30 min",
            "the path's own length", "the day's bars stamped t-31..t-1min"),
    # time and calendar (known in advance)
    Feature("tod", "calendar", "(t - 08:30 CT) in hours", "--", "--", "none (the alert's CT time)"),
    Feature("dow", "calendar", "the trading day's weekday, 0 Monday .. 4 Friday", "--", "--", "none (the date)",
            kind="integer", daily=True),
    Feature("bls_day", "calendar", "1 if the trading day has a BLS 08:30 ET release, else 0", "--", "--",
            "the BLS schedule (published the year before)", kind="binary", daily=True),
    Feature("bls_major", "calendar", "1 if it releases the Employment Situation or the CPI, else 0", "--", "--",
            "the BLS schedule", kind="binary", daily=True),
    Feature("days_to_fomc", "calendar", "calendar days to the next scheduled FOMC statement day (0 on one), capped 30",
            "--", "--", "the FOMC schedule as known on the day", kind="integer", daily=True),
    Feature("days_since_fomc", "calendar", "calendar days since the last FOMC statement before the day, capped 30",
            "--", "--", "the FOMC statements already made", kind="integer", daily=True),
)

NAMES: tuple[str, ...] = tuple(f.name for f in REGISTRY)
BY_NAME = {f.name: f for f in REGISTRY}

#: the normalisers, written beside the features when `compute(..., normalisers=True)` (each from the past only)
NORMALISERS: tuple[tuple[str, str], ...] = (
    ("norm_atr14", "mean daily true range of the 14 prior trading days (roll-safe)"),
    ("norm_atr5", "the same over 5 days"),
    ("norm_v5_med", "median over the 20 prior days of the volume of the bars stamped t-5..t-1 (same slots)"),
    ("norm_v30_med", "the same for t-30..t-1"),
    ("norm_vday_med", "the same for the day's volume stamped <= t-1"),
    ("norm_rv60_med", "median over the 20 prior days of rv_60 at the same slot"),
)
META: tuple[str, ...] = ("day", "alert", "slot", "alert_ts", "contract", "prior_ok")


def describe() -> str:
    """The registry as a markdown table (one line per feature: formula, window, normaliser, the bars it reads)."""
    rows = ["| feature | group | formula | window | normaliser | reads | from | cross-day | warm-up | per |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for f in REGISTRY:
        rows.append(f"| `{f.name}` | {f.group} | {f.formula} | {f.window} | {f.normaliser} | {f.reads} | "
                    f"{slot_label(f.available_from)} | {'yes' if f.cross_day else 'no'} | {f.warmup} | "
                    f"{'day' if f.daily else 'alert'} |")
    return "\n".join(rows)


# ----------------------------------------------------------------------------------------------------------- calendars


@dataclass(frozen=True)
class Calendars:
    """Release calendars as known in advance. `fomc_scheduled`: (statement day, the last trading day on which it was
    still scheduled -- None if it was held)."""
    bls: frozenset[date]
    bls_major: frozenset[date]
    fomc_statements: tuple[date, ...]
    fomc_scheduled: tuple[tuple[date, date | None], ...]


#: scheduled FOMC meetings cancelled after they were announced: statement day -> the last trading day before the
#: cancellation. 17-18 March 2020: cancelled with the unscheduled statement of Sunday 15 March 2020, 17:00 EDT (before
#: the 17:00 CT open of trading day 2020-03-16) -- `config/sources/fomc_statements_2020_2024q1.csv`'s header: "Left
#: out: March 17-18 (cancelled, no statement)".
FOMC_CANCELLED: dict[date, date] = {date(2020, 3, 18): date(2020, 3, 13)}
_NOT_SCHEDULED = ("unscheduled", "notation", "conference call")
BLS_MAJOR_RELEASES = ("Employment Situation", "Consumer Price Index")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(line for line in fh if not line.startswith("#")))


@lru_cache(maxsize=4)
def load_calendars(root: str | None = None) -> Calendars:
    """The calendars from the vendored Stage 2 tree (`root`, default `extended.VENDOR_STAGE2`); read-only."""
    from extended import VENDOR_STAGE2
    base = Path(root) if root else VENDOR_STAGE2
    bls, major = set(), set()
    for name in ("release_days_0830_2009_2025.csv", "release_days_0830_2026.csv"):
        for r in _rows(base / "data" / name):
            d = date.fromisoformat(r["date"])
            bls.add(d)
            if any(k in r["releases"] for k in BLS_MAJOR_RELEASES):
                major.add(d)
    statements: set[date] = set()
    scheduled: dict[date, date | None] = {}
    for name in ("fomc_statements.csv", "fomc_statements_2020_2024q1.csv", "fomc_statements_2026q3.csv"):
        for r in _rows(base / "config" / "sources" / name):
            d = date.fromisoformat(r["date"])
            statements.add(d)
            if not any(k in r["meeting"].lower() for k in _NOT_SCHEDULED):
                scheduled[d] = None
    for d, until in FOMC_CANCELLED.items():
        scheduled[d] = until
    return Calendars(frozenset(bls), frozenset(major), tuple(sorted(statements)), tuple(sorted(scheduled.items())))


def _days_to_fomc(days: Sequence[date], cal: Calendars) -> np.ndarray:
    """Calendar days from each day to the first scheduled statement day on or after it that was still scheduled on
    that day (a cancelled meeting stops counting after its `until`), capped at FOMC_CAP."""
    out = np.full(len(days), float(FOMC_CAP))
    sched = cal.fomc_scheduled
    for i, d in enumerate(days):
        for f, until in sched:                     # sorted by statement day
            if f < d or (until is not None and d > until):
                continue
            out[i] = min(FOMC_CAP, (f - d).days)
            break
    return out


def _days_since_fomc(days: Sequence[date], cal: Calendars) -> np.ndarray:
    st = np.array([np.datetime64(x) for x in cal.fomc_statements], dtype="datetime64[D]")
    dv = np.array([np.datetime64(x) for x in days], dtype="datetime64[D]")
    j = np.searchsorted(st, dv, side="left") - 1          # the last statement strictly before the day
    out = np.full(len(days), float(FOMC_CAP))
    ok = j >= 0
    out[ok] = np.minimum(FOMC_CAP, (dv[ok] - st[j[ok]]).astype(int))
    return out


# ---------------------------------------------------------------------------------------------------------------- grid


@dataclass
class Grid:
    """A frame's bars as [trading day, slot] arrays (NaN where no bar), days sorted."""
    days: list[date]
    contract: np.ndarray
    O: np.ndarray
    H: np.ndarray
    L: np.ndarray
    C: np.ndarray
    V: np.ndarray


def grid(bars: pd.DataFrame) -> Grid:
    ts = bars["ts"].to_numpy(np.int64)
    if len(ts) == 0:
        raise ValueError("no bars")
    if (ts % 60).any():
        raise ValueError("a bar's ts is not a whole minute")
    shifted = (pd.to_datetime(ts, unit="s", utc=True).tz_convert(CHICAGO).tz_localize(None)
               + pd.Timedelta(hours=7))
    dayv = shifted.normalize()
    slotv = (shifted.hour * 60 + shifted.minute).to_numpy(np.int64)
    dkey = dayv.to_numpy().astype("datetime64[D]")
    if "day" in bars.columns:
        given = bars["day"].astype(str).to_numpy()
        if not np.array_equal(given, np.datetime_as_string(dkey, unit="D")):
            raise ValueError("the bars' `day` disagrees with their ts (trading day = Chicago time + 7 hours, its date)")
    uniq, di = np.unique(dkey, return_inverse=True)
    n = len(uniq)
    flat = di * N_SLOTS + slotv
    if len(np.unique(flat)) != len(flat):
        raise ValueError("two bars share a trading day and minute")
    arrs = []
    for col in ("open", "high", "low", "close", "volume"):
        a = np.full(n * N_SLOTS, np.nan)
        a[flat] = bars[col].to_numpy(dtype=float)
        arrs.append(a.reshape(n, N_SLOTS))
    codes, labels = pd.factorize(bars["contract"].astype(str), sort=False)
    order = np.lexsort((slotv, di))
    first = order[np.searchsorted(di[order], np.arange(n))]
    lo = np.full(n, np.iinfo(np.int64).max)
    hi = np.full(n, -1)
    np.minimum.at(lo, di, codes)
    np.maximum.at(hi, di, codes)
    if (lo != hi).any():
        raise ValueError("a trading day holds two contracts (the store charts one a day)")
    contract = np.asarray(labels)[codes[first]]
    days = [pd.Timestamp(x).date() for x in uniq]
    return Grid(days, contract, *arrs)


# ------------------------------------------------------------------------------------------------------------- helpers


def _ffill_close(C: np.ndarray) -> np.ndarray:
    """The close as of each slot: the close of the last bar stamped at or before it (NaN before the day's first)."""
    idx = np.where(~np.isnan(C), np.arange(C.shape[1]), -1)
    np.maximum.accumulate(idx, axis=1, out=idx)
    out = np.take_along_axis(C, np.maximum(idx, 0), axis=1)
    out[idx < 0] = np.nan
    return out


def _first_open(O: np.ndarray, lo: int, hi: int) -> tuple[np.ndarray, np.ndarray]:
    """(the open of the first bar stamped in slots lo..hi-1, its slot) per day; NaN / -1 when none."""
    sub = ~np.isnan(O[:, lo:hi])
    has = sub.any(axis=1)
    j = np.argmax(sub, axis=1) + lo
    val = np.where(has, O[np.arange(O.shape[0]), j], np.nan)
    return val, np.where(has, j, -1)


def _prior_mean(x: np.ndarray, k: int) -> np.ndarray:
    """out[d] = mean of x[d-k..d-1] (NaN until k earlier values exist, or if any is NaN)."""
    out = np.full(len(x), np.nan)
    if len(x) > k:
        w = np.lib.stride_tricks.sliding_window_view(x, k)[:-1]          # w[i] = x[i..i+k-1] -> for d = i + k
        out[k:] = w.mean(axis=1)
    return out


def _prior_sum(x: np.ndarray, k: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) > k:
        w = np.lib.stride_tricks.sliding_window_view(x, k)[:-1]
        out[k:] = w.sum(axis=1)
    return out


def _prior_median(X: np.ndarray, k: int = TOD_DAYS, min_count: int = TOD_MIN_DAYS) -> np.ndarray:
    """med[d, j] = the median of X[d-k..d-1, j] over its non-NaN values (NaN if fewer than min_count)."""
    n, m = X.shape
    pad = np.vstack([np.full((k, m), np.nan), X])
    W = np.lib.stride_tricks.sliding_window_view(pad, k, axis=0)[:n]   # W[d, j, :] = X[d-k..d-1, j]
    S = np.sort(W, axis=-1)                                            # NaN sorts last
    cnt = (~np.isnan(W)).sum(axis=-1)
    lo_i = np.clip((cnt - 1) // 2, 0, k - 1)
    hi_i = np.clip(cnt // 2, 0, k - 1)
    med = 0.5 * (np.take_along_axis(S, lo_i[..., None], -1)[..., 0] + np.take_along_axis(S, hi_i[..., None], -1)[..., 0])
    med[cnt < min_count] = np.nan
    return med


def _win_sum(cs: np.ndarray, s: int, w: int) -> np.ndarray:
    """sum over slots s-w..s-1 from a prefix sum along slots (cs[:, i] = sum of slots 0..i)."""
    hi = cs[:, s - 1]
    return hi - cs[:, s - 1 - w] if s - 1 - w >= 0 else hi.copy()


# ------------------------------------------------------------------------------------------------------------- compute


def compute(bars: pd.DataFrame, marks: Iterable[int] = ALERT_MARKS, calendars: Calendars | None = None, *,
            normalisers: bool = False) -> pd.DataFrame:
    """Every feature of `REGISTRY` at every (trading day, alert mark) of `bars`: one row each, the meta columns
    `META` first (`prior_ok`: the previous frame day exists and charted the same contract), then the features in
    registry order, then -- if asked -- the normalisers `NORMALISERS`."""
    marks = np.asarray(list(marks), dtype=np.int64)
    if marks.size == 0 or marks.min() < RTH_OPEN or marks.max() > RTH_END:
        raise ValueError("alert marks must lie in 08:30..15:00 CT (slots 930..1320)")
    cal = calendars if calendars is not None else load_calendars()
    g = grid(bars)
    n, K = len(g.days), len(marks)
    O, H, L, C, V = g.O, g.H, g.L, g.C, g.V
    rows = np.arange(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        Cff = _ffill_close(C)
        Cprev = np.concatenate([np.full((n, 1), np.nan), Cff[:, :-1]], axis=1)
        dC = C - Cprev                                               # NaN where no bar or no earlier bar in the day
        okd = ~np.isnan(dC)
        cs_d2 = np.cumsum(np.where(okd, dC * dC, 0.0), axis=1)
        cs_dn = np.cumsum(okd, axis=1, dtype=np.int64)
        cs_up = np.cumsum(okd & (dC > 0), axis=1, dtype=np.int64)
        cs_abs = np.cumsum(np.where(okd, np.abs(dC), 0.0), axis=1)
        okc = ~np.isnan(C)
        cs_c = np.cumsum(np.where(okc, C, 0.0), axis=1)
        cs_cn = np.cumsum(okc, axis=1, dtype=np.int64)
        Vz = np.where(np.isnan(V), 0.0, V)
        cs_v = np.cumsum(Vz, axis=1)
        Hcum = np.fmax.accumulate(H, axis=1)
        Lcum = np.fmin.accumulate(L, axis=1)
        rth = slice(RTH_OPEN, RTH_END)
        Hr = np.fmax.accumulate(H[:, rth], axis=1)
        Lr = np.fmin.accumulate(L[:, rth], axis=1)
        tp = (H[:, rth] + L[:, rth] + C[:, rth]) / 3.0
        cs_pv = np.cumsum(np.where(np.isnan(tp), 0.0, tp * Vz[:, rth]), axis=1)
        cs_vr = np.cumsum(Vz[:, rth], axis=1)

        # ---- day-level quantities (each used on day d only through days before d, or frozen before the alert)
        O_day, f_day = _first_open(O, 0, N_SLOTS)
        C_last = Cff[:, -1]
        H_full = np.fmax.reduce(H, axis=1)
        L_full = np.fmin.reduce(L, axis=1)
        same = np.zeros(n, dtype=bool)
        same[1:] = g.contract[1:] == g.contract[:-1]
        prevC = np.concatenate([[np.nan], C_last[:-1]])
        TR = np.where(same, np.fmax(H_full, prevC) - np.fmin(L_full, prevC), H_full - L_full)
        A = _prior_mean(TR, ATR_DAYS)
        A5 = _prior_mean(TR, ATR_SHORT_DAYS)
        chg = np.where(same, C_last - prevC, C_last - O_day)
        sum5, sum20 = _prior_sum(chg, 5), _prior_sum(chg, 20)
        H_rth = np.fmax.reduce(H[:, rth], axis=1)
        L_rth = np.fmin.reduce(L[:, rth], axis=1)
        O_rth, f_rth = _first_open(O, RTH_OPEN, RTH_END)
        has_rth = f_rth >= 0
        C_rth = np.where(has_rth, Cff[:, RTH_END - 1], np.nan)        # the last close stamped <= 14:59
        sh = lambda x: np.concatenate([[np.nan], x[:-1]])             # noqa: E731 -- the previous frame day's value
        pH, pL, pC, pO = sh(H_rth), sh(L_rth), sh(C_rth), sh(O_rth)
        cross = np.where(same, 1.0, np.nan)                           # NaN on a roll day or the frame's first day
        H_on = np.fmax.reduce(H[:, :RTH_OPEN], axis=1)
        L_on = np.fmin.reduce(L[:, :RTH_OPEN], axis=1)
        C_on = Cff[:, RTH_OPEN - 1]
        H_or = np.fmax.reduce(H[:, RTH_OPEN:OR_END], axis=1)
        L_or = np.fmin.reduce(L[:, RTH_OPEN:OR_END], axis=1)

        F = {name: np.full((n, K), np.nan) for name in NAMES}
        V5, V30, Vd, RV60 = (np.full((n, K), np.nan) for _ in range(4))
        for k, s in enumerate(marks):
            s = int(s)
            c = Cff[:, s - 1]
            for w in (5, 15, 30, 60, 120):
                F[f"ret_{w}"][:, k] = (c - Cff[:, s - 1 - w]) / A
            if s > RTH_OPEN:
                ok_r = (f_rth >= 0) & (f_rth <= s - 1)
                F["ret_rth"][:, k] = np.where(ok_r, (c - O_rth) / A, np.nan)
                hr, lr = Hr[:, s - 1 - RTH_OPEN], Lr[:, s - 1 - RTH_OPEN]
                F["range_rth"][:, k] = (hr - lr) / A
                F["pos_rth"][:, k] = (c - lr) / (hr - lr)
                vv = cs_vr[:, s - 1 - RTH_OPEN]
                F["d_vwap"][:, k] = np.where(vv > 0, (c - cs_pv[:, s - 1 - RTH_OPEN] / vv) / A, np.nan)
            ok_d = (f_day >= 0) & (f_day <= s - 1)
            F["ret_day"][:, k] = np.where(ok_d, (c - O_day) / A, np.nan)
            for w in (15, 60):
                F[f"rng_{w}"][:, k] = (np.fmax.reduce(H[:, s - w:s], axis=1) - np.fmin.reduce(L[:, s - w:s], axis=1)) / A
            hd, ld = Hcum[:, s - 1], Lcum[:, s - 1]
            F["range_day"][:, k] = (hd - ld) / A
            F["pos_day"][:, k] = (c - ld) / (hd - ld)
            F["pos_prior"][:, k] = cross * (c - pL) / (pH - pL)
            F["d_pdh"][:, k] = cross * (c - pH) / A
            F["d_pdl"][:, k] = cross * (c - pL) / A
            F["d_pdc"][:, k] = cross * (c - pC) / A
            F["d_onh"][:, k] = (c - H_on) / A
            F["d_onl"][:, k] = (c - L_on) / A
            F["range_on"][:, k] = (H_on - L_on) / A
            F["gap"][:, k] = cross * (C_on - pC) / A
            F["d_round"][:, k] = (c - ROUND_STEP * np.round(c / ROUND_STEP)) / A
            if s >= OR_END:
                F["or_width"][:, k] = (H_or - L_or) / A
                F["or_pos"][:, k] = (c - L_or) / (H_or - L_or)
            v5, v30, v60 = _win_sum(cs_v, s, 5), _win_sum(cs_v, s, 30), _win_sum(cs_v, s, 60)
            V5[:, k], V30[:, k], Vd[:, k] = v5, v30, cs_v[:, s - 1]
            F["vol_accel"][:, k] = np.log((v5 / 5.0 + 1.0) / (v60 / 60.0 + 1.0))
            n15, n60 = _win_sum(cs_dn, s, 15), _win_sum(cs_dn, s, 60)
            rv15 = np.where(n15 >= 2, np.sqrt(_win_sum(cs_d2, s, 15) / n15), np.nan)
            rv60 = np.where(n60 >= 2, np.sqrt(_win_sum(cs_d2, s, 60) / n60), np.nan)
            RV60[:, k] = rv60
            F["rv_ratio"][:, k] = rv15 / rv60
            F["rv_atr"][:, k] = rv60 / A
            F["atr_ratio"][:, k] = A5 / A
            F["range_prior"][:, k] = (pH - pL) / A
            F["atr_rel"][:, k] = A / c * 1e4
            F["ret_prior"][:, k] = (pC - pO) / A
            F["ret_5d"][:, k] = sum5 / A
            F["ret_20d"][:, k] = sum20 / A
            nc = _win_sum(cs_cn, s, 60)
            F["ext_ma60"][:, k] = np.where(nc > 0, (c - _win_sum(cs_c, s, 60) / nc) / A, np.nan)
            n30 = _win_sum(cs_dn, s, 30)
            F["up_share_30"][:, k] = np.where(n30 > 0, _win_sum(cs_up, s, 30) / n30, np.nan)
            path = _win_sum(cs_abs, s, 30)
            F["eff_30"][:, k] = np.where(path > 0, np.abs(c - Cff[:, s - 31]) / path, np.nan)
            F["tod"][:, k] = (s - RTH_OPEN) / 60.0

        m5, m30, mday, mrv = _prior_median(V5), _prior_median(V30), _prior_median(Vd), _prior_median(RV60)
        F["vol_5"] = np.log((V5 + 1.0) / (m5 + 1.0))
        F["vol_30"] = np.log((V30 + 1.0) / (m30 + 1.0))
        F["vol_day"] = np.log((Vd + 1.0) / (mday + 1.0))
        F["rv_tod"] = np.log(RV60 / mrv)

        dates = g.days
        F["dow"][:] = np.array([d.weekday() for d in dates], dtype=float)[:, None]
        F["bls_day"][:] = np.array([d in cal.bls for d in dates], dtype=float)[:, None]
        F["bls_major"][:] = np.array([d in cal.bls_major for d in dates], dtype=float)[:, None]
        F["days_to_fomc"][:] = _days_to_fomc(dates, cal)[:, None]
        F["days_since_fomc"][:] = _days_since_fomc(dates, cal)[:, None]

    start = pd.DatetimeIndex([pd.Timestamp(d - timedelta(days=1)) + pd.Timedelta(hours=17) for d in dates])
    start_ts = start.tz_localize(CHICAGO).as_unit("s").asi8
    out: dict[str, object] = {
        "day": np.repeat(np.array([d.isoformat() for d in dates], dtype=object), K),
        "alert": np.tile(np.array([slot_label(s) for s in marks], dtype=object), n),
        "slot": np.tile(marks, n),
        "alert_ts": (start_ts[:, None] + 60 * marks[None, :]).ravel(),
        "contract": np.repeat(g.contract.astype(object), K),
        "prior_ok": np.repeat(same, K),
    }
    for name in NAMES:
        out[name] = F[name].ravel()
    if normalisers:
        out["norm_atr14"] = np.repeat(A, K)
        out["norm_atr5"] = np.repeat(A5, K)
        out["norm_v5_med"] = m5.ravel()
        out["norm_v30_med"] = m30.ravel()
        out["norm_vday_med"] = mday.ravel()
        out["norm_rv60_med"] = mrv.ravel()
    return pd.DataFrame(out)


#: the trading days of history a day's features need: ret_20d's 20 changes and the close before them (21), plus one
HISTORY_DAYS = 22


def compute_chunked(bars: pd.DataFrame, marks: Iterable[int] = ALERT_MARKS, calendars: Calendars | None = None, *,
                    normalisers: bool = False, chunk_days: int = 250) -> pd.DataFrame:
    """`compute` in chunks of `chunk_days` trading days, each computed with the `HISTORY_DAYS` days before it and only
    its own rows kept -- the same result bit for bit (`tests/test_features_perf.py`), at a fraction of the memory on
    the full development window. The frame's first `HISTORY_DAYS` days have the same warm-up NaNs as in `compute`."""
    ts = bars["ts"].to_numpy(np.int64)
    shifted = (pd.to_datetime(ts, unit="s", utc=True).tz_convert(CHICAGO).tz_localize(None) + pd.Timedelta(hours=7))
    dkey = shifted.normalize().to_numpy().astype("datetime64[D]")
    days = np.unique(dkey)
    parts = []
    for lo in range(0, len(days), chunk_days):
        hi = min(lo + chunk_days, len(days))
        first = days[max(0, lo - HISTORY_DAYS)]
        sel = (dkey >= first) & (dkey <= days[hi - 1])
        X = compute(bars.loc[sel], marks, calendars, normalisers=normalisers)
        keep = X["day"].to_numpy() >= np.datetime_as_string(days[lo], unit="D")
        parts.append(X.loc[keep])
    return pd.concat(parts, ignore_index=True)


__all__ = ["ALERT_MARKS", "BY_NAME", "Calendars", "Feature", "HISTORY_DAYS", "META", "NAMES", "NORMALISERS",
           "REGISTRY", "RTH_OPEN", "OR_END", "RTH_END", "compute", "compute_chunked", "describe", "grid",
           "load_calendars", "slot", "slot_label"]
