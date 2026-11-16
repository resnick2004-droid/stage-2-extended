"""Funded-account simulation that records **when** each payout happens.

Why this exists. `propsim.simulate_xfa` returns aggregates per account -- total cash, payout
count, and the day of the *first* payout -- because stage one's objective never needed dates.
Stage two's objective is time-aware, so it does: a payout on funded day 20 and one on day 400
are different cash flows, and under reinvestment the first compounds and the second may not.

Until now `propedge.campaign.reinvest` filled the gap with `PayoutSchedule`, an explicit
assumption about how second-and-later payouts are spaced. An assumption is the wrong foundation
for the stage's headline ranking, so this module removes it: the funded day loop is
re-implemented here, over the same rules and the same outcome draw, recording every payout's
date and amount.

**The engine is not touched** (D-01). What is re-implemented is the *loop*; the contract rules
come from `propsim.Rules`, the outcome process from the same pluggable draw, `EPS` from the
engine itself. That makes the re-implementation checkable, and `validate_against_engine` below
checks it: driven by the same seed it must reproduce `simulate_xfa`'s aggregates **exactly**,
not merely within noise, because it is the same arithmetic in the same order. Exact agreement is
the whole point -- it is what licenses using the dated output in place of the aggregates.

The control flow deliberately mirrors `simulate_xfa` line for line, including the two `break`
conditions. Those breaks skip draw calls, so departing from them would consume the random stream
differently and destroy the exact agreement that makes this module trustworthy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from propedge.contract.adapter import BinaryDraw, Policy, Rules
from propedge.contract.payout_timing import ENGINE_PAYOUT_TIMING, request_day_excluded

# Imported, not redefined: the engine's own floor-comparison epsilon.
from propsim import EPS  # noqa: E402


@dataclass(frozen=True)
class DatedXfaResult:
    """Per-account funded outcome, with every payout dated.

    `payout_days[i]` are 0-based funded-account days on which account `i` was paid, in order;
    `payout_cash[i]` the net cash received for each (after the profit split and any per-payout
    fee); `payout_gross[i]` the gross request. The remaining arrays match
    `propsim.simulate_xfa`'s returns field for field, so this result is a drop-in replacement.
    """

    payout_days: tuple[tuple[int, ...], ...]
    payout_cash: tuple[tuple[float, ...], ...]
    payout_gross: tuple[tuple[float, ...], ...]
    cash: np.ndarray
    gross_paid: np.ndarray
    n_payouts: np.ndarray
    first_payout_day: np.ndarray
    closed: np.ndarray
    alive: np.ndarray
    days: np.ndarray
    trades: np.ndarray
    B: np.ndarray
    F: np.ndarray
    n: int
    seed: int
    provenance: dict[str, Any] = field(default_factory=dict)

    def payout_gaps(self, i: int) -> tuple[int, ...]:
        """Trading days between successive payouts for account `i`."""
        d = self.payout_days[i]
        return tuple(int(b - a) for a, b in zip(d, d[1:]))

    def as_dated_flows(self, i: int, *, payout_lag_days: int = 0) -> list[tuple[int, float]]:
        """`(day, net cash)` for account `i`, with a processing lag.

        `payout_lag_days` shifts every inflow later. The verified value is per payout method
        (`config/rules.yaml`: `payout_lag_days_aeropay` = 3, `payout_lag_days_ach` = 6 trading
        days, article 8284233, D-24) and `propedge.campaign.payout_method` pairs it with the
        method's fee. The default of 0 here is a mechanics-only value for tests; a reported
        result must state the method and use its lag.
        """
        return [
            (int(d) + int(payout_lag_days), float(c))
            for d, c in zip(self.payout_days[i], self.payout_cash[i])
        ]


def simulate_xfa_dated(
    rules: Rules,
    policy: Policy,
    edge: float,
    n: int,
    *,
    seed: int,
    draw: Any | None = None,
    horizon_days: int = 250,
    horizon_per_account: np.ndarray | None = None,
    payout_timing: str = ENGINE_PAYOUT_TIMING,
) -> DatedXfaResult:
    """Run `n` funded accounts, recording every payout's day and amount.

    Mirrors `propsim.simulate_xfa` exactly and adds the payout ledger. Arguments match
    `propedge.contract.adapter.run_xfa`, plus `payout_timing` (8284233,
    `propedge.contract.payout_timing`). Its default here is the vendored engine's timing,
    `REQUEST_4_TO_5PM` -- a request submitted between 4:00 and 5:00 PM CT on the eligible day, so
    the next day counts toward the new cycle -- because reproducing the engine exactly is what
    this function is for. `REQUEST_AFTER_5PM` applies the rule for a request made after 5:00 PM
    CT, as the lockstep campaign does by default: the next trading day is the Payout request day
    and is left out of the new cycle.

    Args:
        rules: contract rules.
        policy: funded profile, carrying `keep_balance` / `payout_frac` / `payout_path`.
        edge: per-trade edge in units of risk, net of costs. Used only to build the default
            binary draw; an empirical draw carries its own outcome process.
        n: accounts simulated in lockstep.
        seed: explicit. Required.
        draw: outcome source; defaults to `BinaryDraw`, matching the engine's default when it
            is handed an `rng` built from the same seed.
        horizon_days / horizon_per_account: as the engine.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    exclude_request_day = request_day_excluded(payout_timing)

    draw = draw if draw is not None else BinaryDraw(policy, edge, seed, rules)
    hz = (
        np.full(n, horizon_days)
        if horizon_per_account is None
        else np.asarray(horizon_per_account)
    )
    cap = rules.std_cap if policy.payout_path == "standard" else rules.cons_cap

    B = np.zeros(n)
    F = np.full(n, rules.xfa_mll_start)
    alive = np.ones(n, bool)
    closed = np.zeros(n, bool)
    days = np.zeros(n, int)
    trades = np.zeros(n, int)
    cash = np.zeros(n)
    gross_paid = np.zeros(n)
    n_payouts = np.zeros(n, int)
    first_payout_day = np.full(n, -1)

    win_days = np.zeros(n, int)
    w_days = np.zeros(n, int)
    w_profit = np.zeros(n)
    w_best = np.zeros(n)
    since_pay = np.zeros(n)
    paid_once = np.zeros(n, bool)
    request_next = np.zeros(n, bool)   # the next session is the Payout request day (REQUEST_AFTER_5PM only)

    # The ledger this module exists for: one record per payout event, assembled per account
    # at the end. Recording (day, indices, amounts) per event keeps the hot loop vectorised.
    events: list[tuple[int, np.ndarray, np.ndarray, np.ndarray]] = []

    for d in range(int(hz.max())):
        trading = alive & (d < hz)
        if not trading.any():
            break
        alive_at_start = trading.copy()
        active = trading.copy()
        day_pnl = np.zeros(n)
        traded = np.zeros(n, bool)

        for t in range(policy.trades_per_day):
            if not active.any():
                break
            cushion = B - F
            pnl = draw(n, d, t, cushion)
            if rules.liquidate_at_floor:
                pnl = np.maximum(pnl, -cushion)
            act = active & ~np.isnan(pnl)
            B[act] += pnl[act]
            day_pnl[act] += pnl[act]
            trades[act] += 1
            traded |= act
            breach = act & (B <= F + EPS)
            closed |= breach
            alive &= ~breach
            active &= ~breach
            if policy.stop_day_on_win:
                active &= ~(act & (pnl > 0))
            if policy.stop_day_on_loss:
                active &= ~(act & (pnl < 0))

        # 16:00 CT lock (only accounts that traded today)
        days[alive_at_start] += 1
        lk = alive & alive_at_start
        F[lk] = np.minimum(rules.xfa_lock_at, np.maximum(F[lk], B[lk] - rules.mll))

        # A request made after 5:00 PM CT makes the next trading day the Payout request day, "excluded from the new
        # cycle" (8284233): it counts toward the profit since the payout, not the cycle. Under the engine's timing no
        # day is excluded and `cnt` is `lk`, so the arithmetic below is the engine's, unchanged.
        cnt = lk & ~request_next
        request_next[alive_at_start] = False

        # The Consistency path's minimum counts "3 trading days with at least 1 trade per day" (8284208, D-152): a
        # day without a trade does not count. Stage one's engine counts every locked day; its binary draws trade
        # every day, so the two agree wherever stage one could be reproduced.
        w_days[cnt & traded] += 1
        w_profit[cnt] += day_pnl[cnt]
        w_best[cnt] = np.maximum(w_best[cnt], day_pnl[cnt])
        since_pay[lk] += day_pnl[lk]
        wd = cnt & (day_pnl >= rules.std_winning_day_min - EPS)
        win_days[wd] += 1

        if policy.payout_path == "standard":
            elig = lk & (win_days >= rules.std_winning_days)
            if rules.require_profit_since_payout:
                elig &= ~paid_once | (since_pay > EPS)
        else:
            elig = (
                lk
                & (w_days >= rules.cons_min_days)
                & (w_profit > 0)
                & (w_best <= rules.cons_max_day_frac * w_profit + EPS)
            )

        allowed = np.minimum(rules.payout_max_frac_of_balance * B, cap)
        req = policy.payout_frac * allowed
        if policy.keep_balance > 0:
            req = np.minimum(req, np.maximum(B - policy.keep_balance, 0.0))
        do = elig & (req >= rules.payout_min - EPS)

        if do.any():
            idx = np.flatnonzero(do)
            q = req[do]
            net = rules.profit_split * q - rules.payout_fee
            events.append((d, idx, net.copy(), q.copy()))

            B[do] -= q
            gross_paid[do] += q
            cash[do] += net
            n_payouts[do] += 1
            since_pay[do] = 0.0
            paid_once[do] = True
            first = do & (first_payout_day < 0)
            first_payout_day[first] = d
            F[do] = rules.xfa_lock_at
            win_days[do] = 0
            w_days[do] = 0
            w_profit[do] = 0.0
            w_best[do] = 0.0
            if exclude_request_day:
                request_next[do] = True

    # Assemble the per-account ledger. Events are appended in day order, so each account's
    # payouts come out chronologically without sorting.
    per_days: list[list[int]] = [[] for _ in range(n)]
    per_cash: list[list[float]] = [[] for _ in range(n)]
    per_gross: list[list[float]] = [[] for _ in range(n)]
    for day, idx, net, gross in events:
        for j, acc in enumerate(idx):
            per_days[acc].append(int(day))
            per_cash[acc].append(float(net[j]))
            per_gross[acc].append(float(gross[j]))

    return DatedXfaResult(
        payout_days=tuple(tuple(x) for x in per_days),
        payout_cash=tuple(tuple(x) for x in per_cash),
        payout_gross=tuple(tuple(x) for x in per_gross),
        cash=cash,
        gross_paid=gross_paid,
        n_payouts=n_payouts,
        first_payout_day=first_payout_day,
        closed=closed,
        alive=alive,
        days=days,
        trades=trades,
        B=B,
        F=F,
        n=int(n),
        seed=int(seed),
        provenance={
            "simulation": "propedge.contract.funded_dated.simulate_xfa_dated",
            "payout_dates": "exact (recorded from the day loop)",
            "horizon_days": int(horizon_days),
            "policy": policy.label,
            "keep_balance": policy.keep_balance,
            "payout_path": policy.payout_path,
            "payout_timing": payout_timing,
            "edge": float(edge),
            "seed": int(seed),
        },
    )


@dataclass(frozen=True)
class ValidationRow:
    """One (profile, edge, keep_balance) comparison against the vendored engine."""

    label: str
    edge: float
    keep_balance: float
    n: int
    seed: int
    engine_cash: float
    dated_cash: float
    engine_payouts: float
    dated_payouts: float
    engine_first_payout_day: float
    dated_first_payout_day: float
    exact: bool

    @property
    def cash_abs_diff(self) -> float:
        return abs(self.dated_cash - self.engine_cash)

    def summary(self) -> str:
        mark = "EXACT" if self.exact else "DIFFERS"
        return (
            f"{self.label:<28} e={self.edge:<5} keep=${self.keep_balance:<7,.0f} "
            f"cash {self.dated_cash:>10,.2f} vs {self.engine_cash:>10,.2f}  "
            f"payouts {self.dated_payouts:>6.3f} vs {self.engine_payouts:>6.3f}  "
            f"first-day {self.dated_first_payout_day:>7.2f} vs "
            f"{self.engine_first_payout_day:>7.2f}  [{mark}]"
        )


def validate_against_engine(
    combos: list[tuple[float, float, float, float]] | None = None,
    *,
    n: int = 20_000,
    horizon_days: int = 252,
    seed: int = 4242,
    rules: Rules | None = None,
    payout_path: str = "standard",
) -> list[ValidationRow]:
    """Compare the dated simulation with `propsim.simulate_xfa` on several combinations.

    Args:
        combos: `(rr, risk, edge, keep_balance)` tuples. Defaults to three that exercise
            different parts of the payout logic: take-the-maximum, a moderate buffer, and a
            large buffer at a higher edge (which delays the first payout and changes the number
            of payouts, so the ledger is not trivially a single event).
        n: accounts per combination.
        horizon_days: funded horizon.
        seed: base seed; combination `i` uses `seed + i`.
        rules: engine rules; stage-one defaults if omitted.
        payout_path: "standard" or "consistency".

    Returns one `ValidationRow` per combination. Agreement is expected to be **exact**.
    """
    from propedge.contract.adapter import keep_balance_policy, run_xfa

    rules = rules or Rules()
    combos = combos or [
        (1.5, 500.0, 0.10, 0.0),
        (1.5, 500.0, 0.10, 2_000.0),
        (2.0, 750.0, 0.05, 8_000.0),
    ]

    rows: list[ValidationRow] = []
    for i, (rr, risk, edge, keep) in enumerate(combos):
        s = seed + i
        policy = keep_balance_policy(rr, risk, keep, payout_path=payout_path)

        engine = run_xfa(
            policy, edge, n, seed=s, rules=rules, horizon_days=horizon_days
        )
        dated = simulate_xfa_dated(
            rules, policy, edge, n, seed=s, horizon_days=horizon_days
        )

        got_e = engine.raw["first_payout_day"] >= 0
        got_d = dated.first_payout_day >= 0
        e_first = (
            float(engine.raw["first_payout_day"][got_e].mean()) if got_e.any() else float("nan")
        )
        d_first = (
            float(dated.first_payout_day[got_d].mean()) if got_d.any() else float("nan")
        )

        exact = bool(
            np.array_equal(dated.cash, engine.raw["cash"])
            and np.array_equal(dated.n_payouts, engine.raw["n_payouts"])
            and np.array_equal(dated.first_payout_day, engine.raw["first_payout_day"])
            and np.array_equal(dated.gross_paid, engine.raw["gross_paid"])
            and np.array_equal(dated.closed, engine.raw["closed"])
            and np.array_equal(dated.days, engine.raw["days"])
        )

        rows.append(
            ValidationRow(
                label=policy.label,
                edge=edge,
                keep_balance=keep,
                n=n,
                seed=s,
                engine_cash=float(engine.raw["cash"].mean()),
                dated_cash=float(dated.cash.mean()),
                engine_payouts=float(engine.raw["n_payouts"].mean()),
                dated_payouts=float(dated.n_payouts.mean()),
                engine_first_payout_day=e_first,
                dated_first_payout_day=d_first,
                exact=exact,
            )
        )
    return rows
