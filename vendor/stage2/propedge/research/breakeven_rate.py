"""The break-even hit rate, printed beside every screen and verdict (D-201 (1)).

For a set of bracket trades at R, per market and all together:

* **c**, the cost drag in stop units, per contract: the round turn plus the fill model's slippage for a trade that
  ends at its stop (entry and stop ticks), over the stop distance in dollars. Per-contract costs make it independent
  of the contract count. Its mean over the trades is reported.
* **p\\* = (1 + c) / (1 + r)**, the hit rate at which a bracket that wins r - c and loses 1 + c breaks even, at the
  mean c. p\\* is linear in c, so this is also the mean of each trade's p\\*.
* **The hit rate**: the share of trades that reached the target, with its lower bound by the repository's definition
  (D-197): the lower of the 20-day moving-block bootstrap over the day set and the day-clustered normal bound, on the
  hit indicator.
* Beside it, because p\\* is exact only for trades that end at the target or the stop: the share of time exits, the
  hit rate among the trades that did not exit on time (the subset p\\* compares with cleanly), and the mean net R of
  the time exits (the P&L the hit rate hides).

The gate's edge test is unchanged; this is a readable companion to it, never a verdict.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd

from propedge.backtest.metrics import normal_lower_bound
from propedge.research.fv_score import block_lower_bound

BOOT_LEN, REPS = 20, 10_000
TARGET, TIME_EXIT = "t", "m"          # exit kinds: t target, s stop touched, g gapped through the stop, m time exit


def hit_lower_bound(hit: np.ndarray, day_idx: np.ndarray, n_days: int, *, seed: int, boot_len: int = BOOT_LEN,
                    reps: int = REPS) -> float:
    """D-197's lower bound on the hit indicator: the lower of the moving-block bootstrap over `n_days` days (days
    without a trade included) and the day-clustered normal bound."""
    hit = np.asarray(hit, float)
    if len(hit) < 2:
        return float("nan")
    sums = np.bincount(day_idx, weights=hit, minlength=n_days)
    counts = np.bincount(day_idx, minlength=n_days)
    lbs = [block_lower_bound(sums, counts, block=boot_len, reps=reps, seed=seed), normal_lower_bound(hit, day_idx)]
    return float(np.nanmin(lbs)) if np.isfinite(lbs).any() else float("nan")


def breakeven_row(kinds: Sequence[str], r_net: np.ndarray, cost: np.ndarray, day_idx: np.ndarray, n_days: int, *,
                  R: float, seed: int, boot_len: int = BOOT_LEN, reps: int = REPS) -> dict[str, Any]:
    """One row: trades at R with exit kinds `kinds`, net outcomes in R, per-trade cost drag `cost` in stop units and
    day index `day_idx` into a day set of `n_days` days."""
    kinds = np.asarray(kinds, dtype=object)
    r_net, cost = np.asarray(r_net, float), np.asarray(cost, float)
    n = len(kinds)
    hit = (kinds == TARGET).astype(float)
    timed = kinds == TIME_EXIT
    c = float(cost.mean()) if n else float("nan")
    return {"R": R, "trades": n, "cost_drag_c": c, "breakeven_hit_rate": (1.0 + c) / (1.0 + R) if n else float("nan"),
            "hit_rate": float(hit.mean()) if n else float("nan"),
            "hit_rate_lb": hit_lower_bound(hit, day_idx, n_days, seed=seed, boot_len=boot_len, reps=reps),
            "share_time_exits": float(timed.mean()) if n else float("nan"),
            "hit_rate_non_time_exits": float(hit[~timed].mean()) if (~timed).any() else float("nan"),
            "mean_r_time_exits": float(r_net[timed].mean()) if timed.any() else float("nan")}


def im2_rows(table: pd.DataFrame, days: Sequence[str], scale: str, *, fills: dict[str, dict], tick_values: dict,
             round_turns: dict, seed: int, rr: Sequence[int] = (1, 2, 3), col: str = "v",
             boot_len: int = BOOT_LEN, reps: int = REPS) -> list[dict[str, Any]]:
    """Per market and all together, per R: `breakeven_row` on an IM2 entry table (`im2_score.entry_table`) at
    `scale`. The cost per trade is the micro's round turn plus its entry and stop slippage ticks (`fills[market]`,
    `im2_params`' fills) at the micro's tick value, over the trade's risk per micro (`rpc_<scale>`)."""
    x = table[table[f"dist_{scale}"].notna() & table["d"].isin(days)].copy()
    pos = {d: i for i, d in enumerate(days)}
    x["_day"] = x["d"].map(pos)
    x["_cost"] = [(round_turns[m] + (fills[m]["entry"] + fills[m]["stop"]) * tick_values[m]) / rpc
                  for m, rpc in zip(x["market"], x[f"rpc_{scale}"])]
    rows = []
    for market, y in [("all", x), *((m, x[x["market"] == m]) for m in sorted(x["market"].unique()))]:
        for R in rr:
            rows.append({"market": market, "scale": scale, "outcome": col,
                         **breakeven_row(y[f"kind{R}_{scale}"].to_numpy(), y[f"{col}{R}_{scale}"].to_numpy(float),
                                         y["_cost"].to_numpy(float), y["_day"].to_numpy(int), len(days), R=R,
                                         seed=seed, boot_len=boot_len, reps=reps)})
    return rows


__all__ = ["BOOT_LEN", "REPS", "hit_lower_bound", "breakeven_row", "im2_rows"]
