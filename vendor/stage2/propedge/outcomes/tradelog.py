"""The canonical trade-log schema, and a loader that validates against it.

A trade log is the boundary between the backtest and everything downstream: the edge metrics,
the empirical outcome distribution, and the campaign model all read it. So it is validated
once, here, strictly, and every other module can then assume the schema holds.

The schema carries **both** gross and net P&L, because the criterion is on the net figure and
the gross-to-net gap is a reported quantity (how much of the edge costs consume). It carries
`exit_reason` because a trade closed by the 15:10 CT flatten is not a stop or a target and
must not be counted as one -- `vendor/propsim/HANDOFF.md` §3: "trades not resolved by then
are closed at market -- record their actual P&L, do not assume binary."

It carries `stop` and `target` prices so `dollars_risked` can be recomputed and checked rather
than trusted, and `contracts` so cost drag is computable per trade.

Days are Topstep's trading days, not calendar dates (8284197): "The trading day runs from 5:00 PM
CT through 3:10 PM CT the next calendar day." A trade entered at or after 17:00 CT belongs to the
next trading day, and a Sunday-evening entry to Monday's. The strict validator refuses a trade
still open after its trading day's 15:10 CT flatten (8284206: "All positions must be closed by
3:10 PM CT every weekday. You can resume trading at 5:00 PM CT"), which includes any position held
into the 16:00-17:00 CT break (audit 2026-09-27, finding 4).
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

#: The firm's timezone. A naive timestamp is taken to be in it already.
FIRM_TZ = "America/Chicago"
#: A trading day starts at 17:00 CT the calendar day before (8284197).
TRADING_DAY_START_CT = _dt.time(17, 0)
#: Every position is closed by 15:10 CT (8284206), before the 16:00-17:00 CT break.
FLATTEN_CT = _dt.time(15, 10)
BREAK_START_CT = _dt.time(16, 0)

#: Column -> dtype. Order is the canonical column order for any trade-log CSV.
SCHEMA: dict[str, str] = {
    "timestamp_in": "datetime64[ns, America/Chicago]",
    "timestamp_out": "datetime64[ns, America/Chicago]",
    "symbol": "string",
    "side": "string",          # "long" | "short"
    "entry_price": "float64",
    "exit_price": "float64",
    "stop": "float64",         # the stop PRICE as placed
    "target": "float64",       # the target PRICE as placed
    "contracts": "int64",
    "pnl_gross": "float64",    # price move only
    "pnl_net": "float64",      # after commission, exchange fees and slippage
    "exit_reason": "string",   # "target" | "stop" | "flatten" | "other"
}

REQUIRED_COLUMNS: tuple[str, ...] = tuple(SCHEMA)

VALID_SIDES = {"long", "short"}
VALID_EXIT_REASONS = {"target", "stop", "flatten", "other"}

#: Optional columns the loader preserves if present.
OPTIONAL_COLUMNS: tuple[str, ...] = (
    "dollars_risked",   # realised risk of the integer position; recomputed if absent
    "commission",
    "slippage_dollars",
    "fold",             # walk-forward fold id
    "variant",          # variant id from the harness's counter
    "prereg_id",
    "mae",              # D-156: maximum adverse excursion before exit, dollars at this trade's size, >= 0;
                        # lets the campaign settle a trade that risks more than the room exactly
)


class TradeLogError(ValueError):
    """Raised when a trade log violates the schema or an internal consistency check."""


@dataclass(frozen=True)
class TradeLogReport:
    """What the loader found. Written alongside a validated log by the data-integrity agent."""

    path: str | None
    n_trades: int
    n_days: int
    first_timestamp: str | None
    last_timestamp: str | None
    exit_reason_counts: dict[str, int]
    n_flattened: int
    mean_pnl_net: float
    mean_dollars_risked: float
    gross_to_net_dollars: float
    warnings: list[str]

    def summary(self) -> str:
        lines = [
            f"trades           {self.n_trades}",
            f"trading days     {self.n_days}",
            f"period           {self.first_timestamp} .. {self.last_timestamp}",
            f"exit reasons     {self.exit_reason_counts}",
            f"flattened        {self.n_flattened}",
            f"mean net P&L     {self.mean_pnl_net:,.2f}",
            f"mean $ risked    {self.mean_dollars_risked:,.2f}",
            f"gross - net      {self.gross_to_net_dollars:,.2f}  (total cost of trading)",
        ]
        if self.warnings:
            lines.append("warnings:")
            lines += [f"  - {w}" for w in self.warnings]
        return "\n".join(lines)


def empty_tradelog() -> pd.DataFrame:
    """An empty frame with the canonical columns and dtypes."""
    return pd.DataFrame({c: pd.Series(dtype=t) for c, t in SCHEMA.items()})


def as_ct(values: pd.Series | Iterable) -> pd.Series:
    """Timestamps as timezone-aware CT. A naive timestamp is taken to be CT already (as `load_tradelog` assumes); an
    aware one is converted. The index of a Series is kept."""
    s = values if isinstance(values, pd.Series) else pd.Series(list(values))
    t = pd.to_datetime(s, errors="coerce")
    if not pd.api.types.is_datetime64_any_dtype(t):
        t = pd.to_datetime(s, errors="coerce", utc=True)      # mixed offsets: parse through UTC
    if getattr(t.dt, "tz", None) is None:
        return t.dt.tz_localize(FIRM_TZ, ambiguous=np.zeros(len(t), dtype=bool), nonexistent="shift_forward")
    return t.dt.tz_convert(FIRM_TZ)


def trading_day(values: pd.Series | Iterable) -> pd.Series:
    """Topstep's trading day of each timestamp, as a `datetime.date` (8284197: "The trading day runs from 5:00 PM CT
    through 3:10 PM CT the next calendar day"). At or after 17:00 CT is the next day's; a Saturday or Sunday date rolls
    to Monday, so a Sunday-evening entry belongs to Monday's trading day. Exchange holidays are not known here."""
    wall = as_ct(values).dt.tz_localize(None)
    day = wall.dt.normalize() + pd.to_timedelta((wall.dt.hour >= TRADING_DAY_START_CT.hour).astype(int), unit="D")
    wd = day.dt.weekday
    day = day + pd.to_timedelta(np.select([wd == 5, wd == 6], [2, 1], 0), unit="D")
    return day.dt.date


def session_violations(df: pd.DataFrame) -> tuple[int, int]:
    """(trades still open after their trading day's 15:10 CT flatten, of which still open at 16:00 CT, the break).

    A trade's trading day is its entry's (`trading_day`). A trade entered between 15:10 and 17:00 CT is outside every
    trading day and is counted too, since its exit falls after the flatten."""
    if len(df) == 0:
        return 0, 0
    exit_wall = as_ct(df["timestamp_out"]).dt.tz_localize(None)
    day = pd.to_datetime(trading_day(df["timestamp_in"]))
    flatten = day + pd.Timedelta(hours=FLATTEN_CT.hour, minutes=FLATTEN_CT.minute)
    brk = day + pd.Timedelta(hours=BREAK_START_CT.hour, minutes=BREAK_START_CT.minute)
    late = np.asarray(exit_wall > flatten)
    into_break = np.asarray(exit_wall > brk)
    return int(late.sum()), int(into_break.sum())


def dollars_risked(df: pd.DataFrame, point_value: float | None = None) -> pd.Series:
    """Dollars at risk per trade: |entry - stop| x point value x contracts.

    If the log carries a `dollars_risked` column it is returned as-is (the harness writes the
    realised figure, which is authoritative). Otherwise it is recomputed, which needs the
    instrument's point value.
    """
    if "dollars_risked" in df.columns:
        return df["dollars_risked"].astype("float64")
    if point_value is None:
        raise TradeLogError(
            "trade log has no `dollars_risked` column and no point_value was given, so the "
            "dollar risk cannot be recomputed. Pass the instrument's point_value, or write "
            "the realised risk into the log."
        )
    return (df["entry_price"] - df["stop"]).abs() * float(point_value) * df["contracts"]


def validate_tradelog(
    df: pd.DataFrame,
    *,
    point_value: float | None = None,
    strict: bool = True,
) -> TradeLogReport:
    """Validate a trade log in memory. Returns a report; raises on schema violations.

    Checks, in order of how badly each would corrupt what follows:

    1. every required column present;
    2. `side` and `exit_reason` drawn from the allowed vocabularies;
    3. `contracts >= 1` -- a zero-contract trade means sizing rounded to nothing and the
       trade should not be in the log at all;
    4. `timestamp_out >= timestamp_in`;
    5. `pnl_net <= pnl_gross` -- costs cannot be negative. A log that violates this has
       either mis-signed its costs or priced fills the market would not give;
    6. stop on the correct side of entry for the trade's direction;
    7. chronological order;
    8. every trade closed by its trading day's 15:10 CT flatten (8284206), so none is held into
       the 16:00-17:00 CT break or across Topstep's day boundary (`session_violations`).

    Args:
        point_value: needed only if the log has no `dollars_risked` column.
        strict: if False, the softer checks (5, 6, 7, 8) become warnings instead of errors.
            Schema and vocabulary violations always raise.
    """
    warnings: list[str] = []

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise TradeLogError(
            f"trade log is missing required columns: {missing}. "
            f"Canonical schema: {list(SCHEMA)}"
        )

    if len(df) == 0:
        return TradeLogReport(
            path=None, n_trades=0, n_days=0, first_timestamp=None, last_timestamp=None,
            exit_reason_counts={}, n_flattened=0, mean_pnl_net=float("nan"),
            mean_dollars_risked=float("nan"), gross_to_net_dollars=0.0,
            warnings=["trade log is empty"],
        )

    bad_sides = set(df["side"].astype(str).str.lower().unique()) - VALID_SIDES
    if bad_sides:
        raise TradeLogError(f"invalid side values {sorted(bad_sides)}; allowed: {sorted(VALID_SIDES)}")

    bad_reasons = set(df["exit_reason"].astype(str).str.lower().unique()) - VALID_EXIT_REASONS
    if bad_reasons:
        raise TradeLogError(
            f"invalid exit_reason values {sorted(bad_reasons)}; allowed: "
            f"{sorted(VALID_EXIT_REASONS)}. A trade closed by the 15:10 CT flatten is "
            "'flatten', never 'stop' or 'target'."
        )

    if (df["contracts"] < 1).any():
        n = int((df["contracts"] < 1).sum())
        raise TradeLogError(
            f"{n} trades have fewer than 1 contract. Integer sizing rounds down, so a trade "
            "whose dollar risk does not buy one contract is not tradable and must not appear "
            "in the log."
        )

    t_in = pd.to_datetime(df["timestamp_in"], utc=True, errors="coerce")
    t_out = pd.to_datetime(df["timestamp_out"], utc=True, errors="coerce")
    if t_in.isna().any() or t_out.isna().any():
        raise TradeLogError("unparseable timestamps in timestamp_in / timestamp_out")
    if (t_out < t_in).any():
        raise TradeLogError(f"{int((t_out < t_in).sum())} trades exit before they enter")

    # Costs cannot be negative.
    cost = df["pnl_gross"] - df["pnl_net"]
    if (cost < -1e-9).any():
        msg = (
            f"{int((cost < -1e-9).sum())} trades have pnl_net > pnl_gross, i.e. negative "
            "cost. Either the costs are mis-signed, or the fills are better than the market "
            "would give -- which is the SIM-fill problem the conduct guardrails forbid."
        )
        if strict:
            raise TradeLogError(msg)
        warnings.append(msg)

    # Stop on the correct side of entry.
    side = df["side"].astype(str).str.lower()
    long_bad = (side == "long") & (df["stop"] >= df["entry_price"])
    short_bad = (side == "short") & (df["stop"] <= df["entry_price"])
    if bool(long_bad.any() or short_bad.any()):
        msg = (
            f"{int(long_bad.sum() + short_bad.sum())} trades have the stop on the wrong side "
            "of the entry (a long's stop must be below entry, a short's above)"
        )
        if strict:
            raise TradeLogError(msg)
        warnings.append(msg)

    if not t_in.is_monotonic_increasing:
        msg = "trade log is not in chronological order by timestamp_in"
        if strict:
            raise TradeLogError(msg)
        warnings.append(msg)

    late, into_break = session_violations(df)
    if late:
        msg = (
            f"{late} trades are still open after the 15:10 CT flatten of their trading day, {into_break} of them "
            "into the 16:00-17:00 CT break. Topstep: \"All positions must be closed by 3:10 PM CT every weekday\" "
            "(8284206); \"The trading day runs from 5:00 PM CT through 3:10 PM CT the next calendar day\" (8284197)."
        )
        if strict:
            raise TradeLogError(msg)
        warnings.append(msg)

    risked = dollars_risked(df, point_value)
    if (risked <= 0).any():
        warnings.append(
            f"{int((risked <= 0).sum())} trades have non-positive dollars risked; the edge "
            "denominator is undefined for them"
        )

    days = trading_day(df["timestamp_in"])
    counts = df["exit_reason"].astype(str).str.lower().value_counts().to_dict()

    return TradeLogReport(
        path=None,
        n_trades=int(len(df)),
        n_days=int(pd.Series(days).nunique()),
        first_timestamp=str(df["timestamp_in"].iloc[0]),
        last_timestamp=str(df["timestamp_out"].iloc[-1]),
        exit_reason_counts={str(k): int(v) for k, v in counts.items()},
        n_flattened=int(counts.get("flatten", 0)),
        mean_pnl_net=float(df["pnl_net"].mean()),
        mean_dollars_risked=float(risked.mean()),
        gross_to_net_dollars=float(cost.sum()),
        warnings=warnings,
    )


def load_tradelog(
    path: str | Path,
    *,
    point_value: float | None = None,
    strict: bool = True,
    tz: str = "America/Chicago",
) -> tuple[pd.DataFrame, TradeLogReport]:
    """Read and validate a trade-log CSV.

    Timestamps are localised to US/Central (the firm's timezone: 16:00 CT day lock, 15:10 CT
    flatten). A naive timestamp is assumed to be CT already; an offset-aware one is converted.

    Returns:
        (frame, report). The frame has the canonical dtypes and any optional columns present.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"trade log not found: {path}")
    df = pd.read_csv(path)

    for col in ("timestamp_in", "timestamp_out"):
        if col in df.columns:
            s = pd.to_datetime(df[col], errors="coerce")
            try:
                tz_aware = s.dt.tz is not None
            except AttributeError:
                tz_aware = False
            df[col] = s.dt.tz_localize(tz) if not tz_aware else s.dt.tz_convert(tz)

    report = validate_tradelog(df, point_value=point_value, strict=strict)
    return df, TradeLogReport(
        path=str(path),
        n_trades=report.n_trades,
        n_days=report.n_days,
        first_timestamp=report.first_timestamp,
        last_timestamp=report.last_timestamp,
        exit_reason_counts=report.exit_reason_counts,
        n_flattened=report.n_flattened,
        mean_pnl_net=report.mean_pnl_net,
        mean_dollars_risked=report.mean_dollars_risked,
        gross_to_net_dollars=report.gross_to_net_dollars,
        warnings=report.warnings,
    )


def write_tradelog(df: pd.DataFrame, path: str | Path) -> Path:
    """Write a trade log in canonical column order. Validates first."""
    validate_tradelog(df, strict=False)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [c for c in SCHEMA if c in df.columns]
    cols += [c for c in df.columns if c not in cols]
    df[cols].to_csv(path, index=False)
    return path


def day_index(df: pd.DataFrame) -> np.ndarray:
    """0-based trading-day index per trade, preserving order.

    The unit of resampling for the bootstrap in `propedge.backtest.metrics`: trades within a day
    are correlated, so the day is the independent unit, not the trade. The day is Topstep's
    trading day (`trading_day`: an entry at or after 17:00 CT belongs to the next one), not the
    calendar date. The index numbers the trading days that have a trade, in order of first
    appearance -- a cluster label, not a calendar; `distribution.day_blocks` builds the calendar
    of sessions, days without a trade included.
    """
    days = trading_day(df["timestamp_in"])
    codes, _ = pd.factorize(days, sort=False)
    return np.asarray(codes, dtype=np.int64)


def trades_per_day(df: pd.DataFrame) -> pd.Series:
    """Trade count per trading day (Topstep's, 8284197) -- the `trades_per_day` the contract engine needs."""
    days = trading_day(df["timestamp_in"])
    return df.groupby(days.to_numpy()).size()
