"""D-402: the steadiness measures (NEXT_STEPS T22) -- how even a campaign's cash is month to month, read from each
resampled path's own bookkeeping.

A path's days are resampled from a period's days, not a calendar, so its month is the run's 21-session block
(`portfolio.BLOCK_DAYS`): month j holds days 21j to 21j + 20, and its net cash is the close of its last day less the
close of the day before it (the starting bankroll before day 0) -- every fee out and every payout in on the day it
arrives, as the engine books them (`CampaignPath.cash_series`). A trailing part-month is left out. Every month counts,
the first included.

Per path: the share of red months (net cash below zero), the months' standard deviation (n - 1), median, worst and
best; the payouts that arrive per month; the longest run of days below the running peak (the start the first peak);
the deepest drawdown (`portfolio.max_drawdown`). Across a run's paths (`measures`): the median of each, its mean
(D-403: continuous, where a path's share moves in steps of a month) and the stated tail of each beside -- columns
`st_*`.
"""
from __future__ import annotations

from typing import Any, Callable, Sequence

import numpy as np

from propedge.campaign.portfolio import BLOCK_DAYS, _pct, max_drawdown

#: D-402 (3): each per-path measure's tail reported beside its median -- (column suffix, percentile)
TAILS = {"red_share": ("p90", 90), "month_sd": ("p90", 90), "worst_month": ("p05", 5), "best_month": ("p95", 95),
         "underwater_days": ("p95", 95), "max_drawdown": ("p95", 95)}
MEASURES = ("red_share", "month_sd", "month_median", "worst_month", "best_month", "payouts_per_month",
            "underwater_days", "max_drawdown")


def monthly_net(cash: Sequence[float], start: float, block: int = BLOCK_DAYS) -> np.ndarray:
    """Each whole month's net cash: the close of its last day less the close before it (`start` before day 0)."""
    c = np.asarray(cash, dtype=float)
    n = len(c) // int(block)
    if n == 0:
        return np.zeros(0)
    ends = c[int(block) - 1:n * int(block):int(block)]
    before = np.concatenate([[float(start)], ends[:-1]])
    return ends - before


def underwater_days(cash: Sequence[float], start: float) -> int:
    """The longest run of consecutive days whose close is below the running peak (the start the first peak)."""
    c = np.asarray(cash, dtype=float)
    if not len(c):
        return 0
    peak = np.maximum.accumulate(np.concatenate([[float(start)], c]))[1:]
    longest = run = 0
    for below in c < peak:
        run = run + 1 if below else 0
        longest = max(longest, run)
    return int(longest)


def payouts_arrived(path: Any) -> int:
    """The payouts that reach the path's cash: the first and one per gap after it (`CampaignPath`)."""
    if getattr(path, "days_to_first_payout", None) is None:
        return 0
    return 1 + len(tuple(getattr(path, "payout_gaps", ()) or ()))


def path_steadiness(cash: Sequence[float], start: float, n_payouts: int, block: int = BLOCK_DAYS) -> dict[str, float]:
    """One path's measures (D-402 (2))."""
    m = monthly_net(cash, start, block)
    nan = float("nan")
    return {"red_share": float(np.mean(m < 0.0)) if m.size else nan,
            "month_sd": float(np.std(m, ddof=1)) if m.size > 1 else nan,
            "month_median": float(np.median(m)) if m.size else nan,
            "worst_month": float(m.min()) if m.size else nan,
            "best_month": float(m.max()) if m.size else nan,
            "payouts_per_month": float(n_payouts) / m.size if m.size else nan,
            "underwater_days": float(underwater_days(cash, start)),
            "max_drawdown": float(max_drawdown(cash, start)) if len(cash) else nan,
            "months": float(m.size)}


def measures(paths: Sequence[Any], block: int = BLOCK_DAYS) -> dict[str, float]:
    """A run's columns (D-402 (3)) from its `LockstepPath`s (`.path.cash_series`, `.path.initial_bankroll`)."""
    per = [path_steadiness(x.path.cash_series, x.path.initial_bankroll, payouts_arrived(x.path), block) for x in paths]
    out: dict[str, float] = {}
    for k in MEASURES:
        v = [p[k] for p in per]
        out[f"st_{k}_p50"] = _pct(v, 50)
        f = [x for x in v if x == x]                              # D-403: the mean beside, NaN left out
        out[f"st_{k}_mean"] = float(np.mean(f)) if f else float("nan")
        if k in TAILS:
            suffix, q = TAILS[k]
            out[f"st_{k}_{suffix}"] = _pct(v, q)
    out["st_months"] = float(per[0]["months"]) if per else float("nan")
    return out


def columns() -> tuple[str, ...]:
    """The columns `measures` writes, in order."""
    out = []
    for k in MEASURES:
        out += [f"st_{k}_p50", f"st_{k}_mean"]
        if k in TAILS:
            out.append(f"st_{k}_{TAILS[k][0]}")
    return (*out, "st_months")


def hook(block: int = BLOCK_DAYS) -> Callable[[str, float, Sequence[Any]], dict[str, float]]:
    """A `path_hook` piece: the steadiness columns of each run's paths."""
    def _hook(shift: str, enforcement_p: float, paths: Sequence[Any]) -> dict[str, float]:
        return measures(paths, block)
    return _hook


__all__ = ["TAILS", "MEASURES", "monthly_net", "underwater_days", "payouts_arrived", "path_steadiness", "measures",
           "columns", "hook"]
