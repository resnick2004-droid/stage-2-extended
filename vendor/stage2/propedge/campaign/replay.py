"""As-happened replay of a trade log through the prop campaign, with the brokerage curve
beside it (D-130).

The question the replay interface asks: the trades a QuantConnect backtest produced on one
brokerage account -- what would the same trades, in the same order, have done inside the
firm's contract, across up to five accounts that each carry their own state? The engine
answers it from the log's day blocks (`propedge.outcomes.distribution.day_blocks`), scaled or
sized per account, played in the log's own order once (`shared_days.ReplayTable`) under one
of the allocation modes:

* `copier`   -- every account takes every trade (the firm's copier);
* `rotation` -- each trade goes to the next live account in turn;
* `partitioned` -- several strategies aligned by date, one per group.

What can and cannot vary by account state: the dollar risk (contracts) can, through the
sizing rule; whether an account takes a trade can, through routing; the trade's RR cannot,
because it was fixed when the stop and target were placed. A different RR is a different log.

One replay is one path. The distribution -- ruin probability, the spread of outcomes -- comes
from the resampled tables (`replay=False`), which reorder the same days.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from propedge.campaign.lockstep import LockstepPath, simulate_lockstep_path
from propedge.campaign.protocols import Protocol
from propedge.campaign.reinvest import ACTIVATION_ON_ACTIVATION
from propedge.campaign.shared_days import COPIER, INDEPENDENT, SharedDayDraws
from propedge.campaign.sizing import SizingRule
from propedge.outcomes.distribution import DayBlock


def brokerage_curve(blocks: Sequence[DayBlock], risk_per_trade: float) -> np.ndarray:
    """Cumulative dollar P&L at each day's close with every trade at `risk_per_trade`.

    The single-account curve the campaign is compared against: the same trades, one account,
    no floor, no target, no fees, a fixed dollar risk. Day `d` of the result is the close of
    the log's day `d`.
    """
    if risk_per_trade <= 0:
        raise ValueError("risk_per_trade must be positive")
    daily = np.zeros(len(blocks))
    for d, b in enumerate(blocks):
        with np.errstate(divide="ignore", invalid="ignore"):
            u = np.where(b.risked > 0, b.pnl / b.risked, np.nan)
        daily[d] = float(np.nansum(u) * risk_per_trade)
    return np.cumsum(daily)


def log_summary(blocks: Sequence[DayBlock]) -> dict[str, Any]:
    """What a log is, before anything is replayed: days, trades, the busiest day, the mean of
    `u` and its sd, the share of days with no trade, whether risk per contract is present."""
    n_trades = int(sum(len(b) for b in blocks))
    us = np.concatenate([
        np.where(b.risked > 0, b.pnl / b.risked, np.nan) for b in blocks if len(b)
    ]) if n_trades else np.zeros(0)
    us = us[~np.isnan(us)]
    return {
        "n_days": int(len(blocks)),
        "n_trades": n_trades,
        "busiest_day": int(max((len(b) for b in blocks), default=0)),
        "share_days_without_a_trade": float(np.mean([len(b) == 0 for b in blocks])) if blocks else float("nan"),
        "mean_u": float(us.mean()) if us.size else float("nan"),
        "sd_u": float(us.std(ddof=1)) if us.size > 1 else float("nan"),
        "has_risk_per_contract": all(b.risk_per_contract is not None for b in blocks),
    }


def replay_log(
    blocks: Sequence[DayBlock],
    protocol: Protocol,
    *,
    rules: Any,
    initial_bankroll: float,
    max_concurrent_accounts: int,
    payout_lag_days: int,
    mode: str = COPIER,
    sizing: SizingRule | None = None,
    subscription: float | None = None,
    billing_days: int | None = None,
    activation: float | None = None,
    max_concurrent_combines: int = 1,
    stop_buying_when_queued: bool = True,
    activation_timing: str = ACTIVATION_ON_ACTIVATION,
    combine_max_days: int = 2000,
    funded_horizon_days: int = 100_000,
    horizon_days: int | None = None,
    seed: int = 0,
    record_trades: bool = True,
    settlement: str | None = None,
) -> LockstepPath:
    """Play the log once, in its own order, through the campaign. Returns the path with its
    per-trade ledger.

    `horizon_days` defaults to the log's length plus the purchase day, so the replay ends when
    the log does. `funded_horizon_days` defaults to "never": a replayed funded account lives
    as long as the log, unlike the pool's fixed horizon. `seed` only matters for the default
    binary draws, which a replay does not use; it is recorded for provenance. `settlement` is how a trade that
    risks more than the room settles (D-156, `propedge.outcomes.settlement`); None: `mae` when every block
    carries MAE, else `pessimistic`.
    """
    if mode == INDEPENDENT:
        raise ValueError("an as-happened replay has one calendar; choose copier, rotation or partitioned")
    shared = SharedDayDraws(
        {0: list(blocks)}, protocol=protocol, seed=seed, mode=mode, sizing=sizing, replay=True,
        settlement=settlement,
    )
    horizon = int(horizon_days) if horizon_days is not None else len(blocks) + 1
    return simulate_lockstep_path(
        protocol,
        edge=0.0, seed=seed, rules=rules,
        initial_bankroll=initial_bankroll, horizon_days=horizon,
        max_concurrent_accounts=max_concurrent_accounts,
        subscription=float(rules.subscription if subscription is None else subscription),
        billing_days=int(rules.billing_days if billing_days is None else billing_days),
        activation=float(rules.activation if activation is None else activation),
        payout_lag_days=int(payout_lag_days),
        max_concurrent_combines=max_concurrent_combines,
        stop_buying_when_queued=stop_buying_when_queued,
        activation_timing=activation_timing,
        combine_max_days=combine_max_days, funded_horizon_days=funded_horizon_days,
        record_trades=record_trades,
        **shared.lockstep_kwargs(),
    )


__all__ = ["brokerage_curve", "log_summary", "replay_log"]
