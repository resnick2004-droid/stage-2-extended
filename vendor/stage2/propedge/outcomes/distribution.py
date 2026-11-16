"""Outcome draws for the contract engine: empirical (from a trade log) and binary.

The contract engine takes a pluggable draw with the signature

    draw(n, day, slot, cushion) -> np.ndarray of dollars, NaN = "no trade this slot"

(see `propedge.contract.adapter.OutcomeDraw`). Stage one's draw was binary: every trade
resolved at exactly the labelled dollar risk, win `+R*r` or loss `-r`. That is a clean model
and a wrong one for a real strategy, because real trades also end at the 15:10 CT flatten,
somewhere between the stop and the target.

`EmpiricalDraw` replaces the binary assumption with the strategy's own realised outcomes:

* **Resampling is by day, not by trade.** Trades within a day share a regime, a volatility
  state and often a signal; treating them as independent understates variance and flatters
  every downstream interval. The day is the independent unit here and in the bootstrap in
  `propedge.backtest.metrics`, for the same reason.
* **Intra-day ordering is preserved.** The engine applies the floor intraday and the ratchet
  at the 16:00 CT lock, so a day that loses then wins is not the same as one that wins then
  loses: the first can breach the floor and end the account. Shuffling within a day would
  systematically understate failure.
* **The flatten is preserved.** A flattened trade enters the draw at its actual P&L.

`BinaryOutcomeDraw` is the validation limit: it reproduces stage one's draw exactly, so the
extended engine can be shown to reduce to the old one when costs are zero and outcomes are
binary (T3 in NEXT_STEPS.md).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from propedge.outcomes.tradelog import validate_tradelog


@dataclass(frozen=True)
class DayBlock:
    """One trading day's realised trades, in order.

    Attributes:
        pnl: dollar P&L per trade, in intra-day order.
        risked: dollars risked per trade, in the same order.
        exit_reasons: per-trade exit reason, kept so a draw can report the flatten share.
        risk_per_contract: dollars risked per (micro) contract at each trade's stop, or None
            when the log carried no contract count. Needed only by tier sizing
            (`propedge.campaign.sizing`), which sizes a trade in contracts from it.
        mae: each trade's maximum adverse excursion before its exit, in dollars at the trade's
            logged risk (the units of `pnl` and `risked`), positive when adverse; NaN for a trade
            whose MAE is unknown; None when the log carried none. Lets a draw settle a trade that
            risks more than the room exactly (`propedge.outcomes.settlement`, D-156).
    """

    pnl: np.ndarray
    risked: np.ndarray
    exit_reasons: tuple[str, ...]
    risk_per_contract: np.ndarray | None = None
    mae: np.ndarray | None = None
    entry_t: np.ndarray | None = None      # each trade's entry and exit time within its day (any monotone unit, e.g.
    exit_t: np.ndarray | None = None       # minutes CT); lets rotation route a trade only to a flat account (D-159)
    # D-162: each trade's net outcome in R (units of its own stop distance) at several target multiples, and its MAE in
    # R before that bracket's exit, so a draw can read the R an account's state calls for; None when the log has one R.
    r_by_rr: dict[float, np.ndarray] | None = None
    mae_by_rr: dict[float, np.ndarray] | None = None
    # Each trade's market (a trade log's `symbol`), or None when not known. A log whose trades span more than one market
    # can hold positions in several at once, which the account layouts must not stack in one account (audit 2026-09-27,
    # finding 5; `propedge.campaign.shared_days.check_layout`).
    markets: tuple[str, ...] | None = None
    # D-324: each trade's round-turn fee per micro-equivalent, in dollars, already in its outcomes (`pnl`, `r_by_rr`) --
    # priced at the size the log was costed at; a sizing rule with a fee schedule re-prices it at the contracts the
    # trade holds (`propedge.campaign.sizing`). None when the log carries none.
    fee: np.ndarray | None = None
    # D-339: each trade's side (+1 long, -1 short), so rotation can refuse a signal opposite to a position open on
    # another account (the firm's cross-account rule, D-336 (iv)); None when the log carries none.
    sides: np.ndarray | None = None
    # D-349: each trade's exit time at every R of the menu (the bracket's own exit at that target; NaN where the room
    # does not permit it), keyed like `r_by_rr`, so the router holds a position to its exit at the R its account trades
    # -- `exit_t` is the log's single exit (FV3's: the fresh Combine's 1.5R), which closed a 3R position too early for
    # the cross-account rule (run fv3_gf_v1). None when the log carries one exit.
    exit_by_rr: dict[float, np.ndarray] | None = None

    def __len__(self) -> int:
        return len(self.pnl)


def day_blocks(
    df: pd.DataFrame, *, point_value: float | None = None, sessions: Sequence | None = None,
) -> list[DayBlock]:
    """Split a validated trade log into one block per trading session, preserving intra-day order.

    The blocks are a calendar of sessions: a draw resamples them as days and a replay plays them as consecutive days,
    so a session without a trade is an empty block, not a missing one. Each trade belongs to Topstep's trading day of
    its entry (`tradelog.trading_day`, 8284197: "The trading day runs from 5:00 PM CT through 3:10 PM CT the next
    calendar day"), so an entry at or after 17:00 CT is the next session's (audit 2026-09-27, finding 4).

    Args:
        point_value: needed only if the log has no `dollars_risked` column.
        sessions: the trading days to lay the log on (dates, or anything `pd.to_datetime` reads; sorted). None:
            every weekday from the log's first trading day to its last -- exchange holidays included as empty
            sessions, since they are not known here; pass the exchange calendar to leave them out. A trade on a day
            not in `sessions` is refused.

    Every block carries each trade's entry and exit time in minutes since its trading day began (17:00 CT the day
    before), for flat-account routing (D-159), and each trade's market (the log's `symbol`). A trade still open after
    its trading day's 15:10 CT flatten cannot be put in one session and is refused (`tradelog.session_violations`).
    """
    from propedge.outcomes.tradelog import (
        TradeLogError,
        as_ct,
        dollars_risked,
        session_violations,
        trading_day,
    )

    validate_tradelog(df, point_value=point_value, strict=False)
    late, into_break = session_violations(df)
    if late:
        raise TradeLogError(
            f"{late} trades are still open after the 15:10 CT flatten of their trading day ({into_break} of them into "
            "the 16:00-17:00 CT break); such a trade spans two of Topstep's trading days and cannot be laid in one "
            "session (8284206: \"All positions must be closed by 3:10 PM CT every weekday\")"
        )
    day = np.asarray(pd.to_datetime(trading_day(df["timestamp_in"])), dtype="datetime64[D]")
    if sessions is None:
        calendar = (np.arange(day.min(), day.max() + np.timedelta64(1, "D"), dtype="datetime64[D]")
                    if len(day) else np.zeros(0, dtype="datetime64[D]"))
        calendar = calendar[np.is_busday(calendar)]
    else:
        calendar = np.unique(np.asarray(pd.to_datetime(list(sessions)), dtype="datetime64[D]"))
        outside = ~np.isin(day, calendar)
        if outside.any():
            raise TradeLogError(
                f"{int(outside.sum())} trades fall on trading days not in `sessions`, e.g. {day[outside][0]}"
            )
    # Minutes since each trade's trading day began (17:00 CT the calendar day before), in elapsed time.
    start = pd.Series(pd.to_datetime(day - np.timedelta64(1, "D")) + pd.Timedelta(hours=17), index=df.index)
    start = start.dt.tz_localize(as_ct(df["timestamp_in"]).dt.tz)
    entry_min = np.asarray((as_ct(df["timestamp_in"]) - start).dt.total_seconds() / 60.0, dtype=float)
    exit_min = np.asarray((as_ct(df["timestamp_out"]) - start).dt.total_seconds() / 60.0, dtype=float)
    symbols = np.asarray(df["symbol"].astype(str))
    risked = np.asarray(dollars_risked(df, point_value), dtype=float)
    pnl = np.asarray(df["pnl_net"], dtype=float)
    reasons = np.asarray(df["exit_reason"].astype(str).str.lower())
    # Risk per contract, when the log says how many contracts each trade carried. Tier sizing
    # (`propedge.campaign.sizing`) needs it; nothing else reads it.
    rpc: np.ndarray | None = None
    if "contracts" in df.columns:
        contracts = np.asarray(df["contracts"], dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            rpc = np.where(contracts > 0, risked / contracts, np.nan)
    # D-156: each trade's maximum adverse excursion in dollars at its own size, when the log has it.
    mae: np.ndarray | None = None
    if "mae" in df.columns:
        mae = np.asarray(df["mae"], dtype=float)
        if np.any(mae[~np.isnan(mae)] < 0):
            raise ValueError("mae is the adverse excursion in dollars and cannot be negative")
    # D-324: each trade's fee per micro-equivalent already in its outcomes, when the log carries it
    fee = np.asarray(df["fee_per_micro"], dtype=float) if "fee_per_micro" in df.columns else None

    blocks: list[DayBlock] = []
    for d in calendar:
        m = day == d
        blocks.append(
            DayBlock(
                pnl=pnl[m].copy(),
                risked=risked[m].copy(),
                exit_reasons=tuple(reasons[m]),
                risk_per_contract=rpc[m].copy() if rpc is not None else None,
                mae=mae[m].copy() if mae is not None else None,
                entry_t=entry_min[m].copy(),
                exit_t=exit_min[m].copy(),
                markets=tuple(symbols[m]),
                fee=fee[m].copy() if fee is not None else None,
            )
        )
    return blocks


class EmpiricalDraw:
    """Outcome draw resampled by day from a trade log.

    Each simulated account is assigned, for each simulated day, a whole day sampled with
    replacement from the log's days. The account then receives that day's trades in their
    original order, one per trade slot; slots beyond the day's trade count return NaN, which
    the engine reads as "no trade" and which is how a day with fewer trades than
    `trades_per_day` ends early.

    Scaling. The log's trades were taken at whatever dollar risk the strategy used. To value
    a profile at a different risk, pass `scale_to_risk`: each trade's P&L is rescaled by
    `scale_to_risk / trade_dollars_risked`, so the outcome *distribution in units of risk* is
    preserved. This is the right transformation only if the strategy's returns are
    scale-invariant in risk -- true for the price process, false once the position limit or
    liquidity bites. `propedge.execution.instruments.contracts_for_risk` is where that
    assumption is checked; do not use `scale_to_risk` to model a size the limit forbids.

    Settlement (D-156). The engine hands the draw the room above the nearer barrier as
    `cushion`; each trade is settled against it by `settlement` (`propedge.outcomes.settlement`):
    `mae` when every block carries MAE, else `pessimistic`, unless `legacy` is asked for to
    reproduce a pre-D-156 result. The engine's own clip at the floor still applies after.

    Args:
        blocks: per-day blocks, from `day_blocks`.
        n_accounts: how many accounts run in lockstep (the engine's `n`).
        seed: explicit. Required.
        scale_to_risk: rescale every trade to this dollar risk, or None to use raw P&L.
        max_days: how many simulated days to pre-draw. Extended automatically if exceeded.
        settlement: `mae`, `pessimistic` or `legacy`; None picks the default above.
    """

    def __init__(
        self,
        blocks: Sequence[DayBlock],
        n_accounts: int,
        *,
        seed: int,
        scale_to_risk: float | None = None,
        max_days: int = 1024,
        settlement: str | None = None,
    ):
        from propedge.outcomes.settlement import (
            TRADE_LOG_SETTLEMENTS,
            default_trade_log_settlement,
        )

        if not blocks:
            raise ValueError("cannot build an empirical draw from an empty trade log")
        self.blocks = list(blocks)
        self.n_accounts = int(n_accounts)
        self.seed = int(seed)
        self.scale_to_risk = scale_to_risk
        self.settlement = settlement or default_trade_log_settlement(self.blocks)
        if self.settlement not in TRADE_LOG_SETTLEMENTS:
            raise ValueError(f"a trade-log draw settles by one of {TRADE_LOG_SETTLEMENTS}, got {self.settlement!r}")
        self._rng = np.random.default_rng(self.seed)
        self._assign: np.ndarray = np.empty((0, self.n_accounts), dtype=np.int64)
        self._extend(max_days)

        # Pre-scale each block once: P&L, dollars risked and MAE by the same factor.
        self._pnl: list[np.ndarray] = []
        self._risk: list[np.ndarray] = []
        self._mae: list[np.ndarray | None] = []
        for b in self.blocks:
            if scale_to_risk is None:
                factor = np.ones(len(b.pnl))
            else:
                with np.errstate(divide="ignore", invalid="ignore"):
                    factor = np.where(b.risked > 0, scale_to_risk / b.risked, np.nan)
            self._pnl.append(b.pnl if scale_to_risk is None else b.pnl * factor)
            self._risk.append(b.risked * factor)
            self._mae.append(None if b.mae is None else b.mae * factor)

    def _extend(self, upto_day: int) -> None:
        """Draw day assignments out to `upto_day`, keeping earlier ones fixed."""
        have = self._assign.shape[0]
        if upto_day < have:
            return
        extra = self._rng.integers(
            0, len(self.blocks), size=(upto_day - have + 1, self.n_accounts)
        )
        self._assign = (
            extra if have == 0 else np.concatenate([self._assign, extra], axis=0)
        )

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        if n != self.n_accounts:
            raise ValueError(
                f"EmpiricalDraw was built for {self.n_accounts} accounts but the engine "
                f"asked for {n}. Rebuild the draw with n_accounts={n}."
            )
        from propedge.outcomes.settlement import settle

        self._extend(day)
        which = self._assign[day]
        out = np.full(n, np.nan)
        risk = np.full(n, np.nan)
        mae = np.full(n, np.nan)
        # Group by block so each distinct day is handled once rather than per account.
        for b in np.unique(which):
            pnl = self._pnl[b]
            if slot < len(pnl):
                out[which == b] = pnl[slot]
                risk[which == b] = self._risk[b][slot]
                if self._mae[b] is not None:
                    mae[which == b] = self._mae[b][slot]
        return settle(out, risk, mae, np.asarray(cushion, dtype=float), self.settlement)

    @property
    def max_trades_per_day(self) -> int:
        """The engine's `trades_per_day` must be at least this, or trades are dropped."""
        return max(len(b) for b in self.blocks)

    @property
    def flatten_share(self) -> float:
        """Share of logged trades that ended at the 15:10 CT flatten.

        Reported because it is the size of the correction over stage one's binary model: a
        log with no flattened trades is genuinely binary and the two models agree.
        """
        total = sum(len(b) for b in self.blocks)
        flat = sum(sum(1 for r in b.exit_reasons if r == "flatten") for b in self.blocks)
        return flat / total if total else 0.0

    def provenance(self) -> dict:
        return {
            "draw": "EmpiricalDraw",
            "n_days_in_log": len(self.blocks),
            "n_trades_in_log": int(sum(len(b) for b in self.blocks)),
            "max_trades_per_day": self.max_trades_per_day,
            "flatten_share": self.flatten_share,
            "scale_to_risk": self.scale_to_risk,
            "settlement": self.settlement,
            "seed": self.seed,
        }


class BinaryOutcomeDraw:
    """Stage one's binary draw, reimplemented on the same interface for the validation limit.

    Wins `+rr * risk`, loses `-risk`, with `p_win = (1 + edge) / (1 + rr)` -- stage one's edge
    convention (propsim D-01/D-06). One trade per slot, every slot, every day.

    This deliberately does **not** implement the floor barrier race that
    `propsim.RandomDraw(floor_mode="truncate")` performs: it is the plain binary process, used
    to show that the empirical machinery reduces to the binary one. When the goal is to
    reproduce stage one's *numbers*, use `propedge.contract.adapter.BinaryDraw`, which
    delegates to the vendored `RandomDraw` and therefore carries the truncation and the drift
    solve exactly as stage one computed them.

    Args:
        rr: reward multiple R.
        risk: dollar loss per trade.
        edge: expected P&L per trade as a fraction of dollar risk.
        n_accounts: accounts in lockstep.
        seed: explicit. Required.
    """

    def __init__(self, rr: float, risk: float, edge: float, n_accounts: int, *, seed: int,
                 settlement: str = "pessimistic"):
        p = (1.0 + edge) / (1.0 + rr)
        if not 0.0 < p < 1.0:
            raise ValueError(f"p_win={p} out of range for rr={rr}, edge={edge}")
        self.rr = float(rr)
        self.risk = float(risk)
        self.edge = float(edge)
        self.p = p
        self.win = float(rr) * float(risk)
        self.n_accounts = int(n_accounts)
        self.seed = int(seed)
        # D-156: settled like a binary trade log without MAE, so it stays the reference for `EmpiricalDraw`.
        self.settlement = settlement
        self._rng = np.random.default_rng(self.seed)

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        from propedge.outcomes.settlement import settle

        u = self._rng.random(n)
        pnl = np.where(u < self.p, self.win, -self.risk)
        return settle(pnl, self.risk, None, np.asarray(cushion, dtype=float), self.settlement)

    def provenance(self) -> dict:
        return {
            "draw": "BinaryOutcomeDraw",
            "rr": self.rr,
            "risk": self.risk,
            "edge": self.edge,
            "p_win": self.p,
            "seed": self.seed,
        }


def binary_blocks(
    rr: float, risk: float, edge: float, n_days: int, *, seed: int, trades_per_day: int = 1,
    risk_per_contract: float | None = None,
) -> list[DayBlock]:
    """Synthesise day blocks from a binary process.

    Lets `EmpiricalDraw` be driven by a known process, which is how T3 shows the empirical
    machinery reduces to the binary limit: build blocks here, wrap them in `EmpiricalDraw`,
    and check the engine's output against `BinaryOutcomeDraw` on the same profile.

    `risk_per_contract` states the dollars one (micro) contract risks at the trade's stop, for
    tier sizing; None leaves the blocks unsized, as a log without a contract count would.
    """
    rng = np.random.default_rng(seed)
    p = (1.0 + edge) / (1.0 + rr)
    if not 0.0 < p < 1.0:
        raise ValueError(f"p_win={p} out of range for rr={rr}, edge={edge}")
    win = rr * risk
    blocks = []
    for _ in range(n_days):
        u = rng.random(trades_per_day)
        pnl = np.where(u < p, win, -risk)
        blocks.append(
            DayBlock(
                pnl=pnl,
                risked=np.full(trades_per_day, float(risk)),
                exit_reasons=tuple("target" if x > 0 else "stop" for x in pnl),
                risk_per_contract=(
                    None if risk_per_contract is None
                    else np.full(trades_per_day, float(risk_per_contract))
                ),
            )
        )
    return blocks
