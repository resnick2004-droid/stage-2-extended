"""Calendar-time reinvestment simulation: the stage's objective, confirmed (D-02).

`irr.py` gives the rate of one attempt's dated cash flows. This module answers the question
the charter actually asks: starting from a bankroll, buying Combines as cash allows, running
at most N funded accounts at once with further passes on hold, and reinvesting payouts as they
arrive -- **how does cash grow over calendar time, and how often does the bankroll die first?**

The three things a static metric cannot see, and this one must:

* **Latency.** A payout requested on funded-day 8 and received days later is not day-8 cash.
  `payout_lag_days` shifts every inflow. It is read from the verified ledger by payout method
  (`payout_lag_days_aeropay` = 3, `payout_lag_days_ach` = 6 trading days, article 8284233,
  D-24); fee and lag are one joint choice, paired in `propedge.campaign.payout_method`, and
  `simulate_campaign` resolves them when the caller names no lag. Zero is not a default.
* **Activation timing.** The activation fee falls due when the trader activates the account,
  not when the Combine passes (article 8284217, D-21). The two differ only for a pass that
  waits in the hold queue, which is exactly the case the cap creates.
* **The cap.** Passes beyond the firm's limit on active funded accounts go on a **hold queue**
  rather than compounding. The cap is what makes this a bounded-growth problem rather than an
  exponential one, and it is why the protocol comparison is interesting at all.
* **Ruin.** Growth reported without the probability of not surviving to collect it is not a
  result. Ruin here is the campaign reaching a state where it cannot pay the next fee and has
  nothing running that could ever pay it.

Every reported growth number is accompanied by ruin probability, bankroll drawdown and payout
latency -- not in an appendix, in the same record. `CampaignSummary` has no method that
returns growth alone.

Where the payout dates come from
-------------------------------
`propsim.simulate_xfa` returns **aggregates** per account -- total cash, number of payouts, day
of the *first* payout -- not a dated list of every payout, because stage one's objective never
needed dates. Stage two's does.

That gap is now closed by building rather than assuming:
`propedge.contract.funded_dated.simulate_xfa_dated` re-implements the funded day loop over the
same rules and the same draw and records every payout's date, and it reproduces the vendored
engine's aggregates **bit-for-bit** on seeded comparisons (`validate_against_engine`). It is the
default here (`payout_dates="exact"`), so nothing that feeds a ranking rests on a spacing
assumption.

`PayoutSchedule` (EVEN / EARLIEST / LATEST) remains available via `payout_dates="model"` for
**sensitivity analysis only** -- to ask how much the answer would have moved under a given
spacing. A result that feeds a ranking must use the exact dates.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Protocol as TypingProtocol, Sequence

import numpy as np

from propedge.campaign.irr import CashFlow, TRADING_DAYS_PER_YEAR
from propedge.campaign.protocols import Protocol


class PayoutSchedule(str, Enum):
    """How later payouts are spread over the funded account's life.

    The engine gives the first payout's day exactly and the total count; these models fill in
    the rest. Which one is chosen changes IRR but not total cash.

    EVEN:      payouts evenly spaced from the first payout to the account's end. Neutral.
    EARLIEST:  payouts as soon as the eligibility window allows (every `window_days`).
               Optimistic -- flatters IRR.
    LATEST:    payouts bunched at the end. Pessimistic.
    """

    EVEN = "even"
    EARLIEST = "earliest"
    LATEST = "latest"


#: When the activation fee is charged. "on_activation" is the verified rule (article 8284217,
#: D-21): activation is trader-initiated once a slot is free, and the fee falls due then.
#: "on_pass" charges it when the Combine passes; the two differ only for queued passes, so it
#: is kept for reconciliation with the engine's EV per attempt and for sensitivity.
ACTIVATION_ON_ACTIVATION = "on_activation"
ACTIVATION_ON_PASS = "on_pass"
ACTIVATION_TIMINGS = (ACTIVATION_ON_ACTIVATION, ACTIVATION_ON_PASS)


@dataclass(frozen=True)
class AttemptOutcome:
    """One Combine attempt and, if it passed, the funded account that followed.

    All day indices are 0-based. `pass_day`, `combine_end_day` are on the attempt's clock;
    `payout_days` and `funded_end_day` are on the funded account's clock, which starts the day
    after the pass.
    """

    passed: bool
    combine_end_day: int
    pass_day: int | None = None
    payout_days: tuple[int, ...] = ()
    payout_amounts: tuple[float, ...] = ()
    funded_end_day: int | None = None
    funded_closed: bool = False        # breached the floor rather than reaching the horizon

    @property
    def ever_paid(self) -> bool:
        return len(self.payout_days) > 0

    @property
    def total_payout(self) -> float:
        return float(sum(self.payout_amounts))

    @property
    def first_payout_day(self) -> int | None:
        return int(self.payout_days[0]) if self.payout_days else None

    def subscription_days(self, billing_days: int) -> list[int]:
        """Days a Combine subscription is charged: 0, billing_days, ... while running."""
        last = self.pass_day if self.passed and self.pass_day is not None else self.combine_end_day
        return list(range(0, int(last) + 1, int(billing_days)))

    def cash_flows(
        self,
        *,
        subscription: float,
        billing_days: int,
        activation: float,
        payout_lag_days: int = 0,
    ) -> list[CashFlow]:
        """This attempt's dated schedule, for `propedge.campaign.irr`.

        Activation is dated on the pass day. For a single attempt with no cap there is no
        queue, so the pass day and the activation day coincide; the campaign simulation, which
        has a cap, dates the fee on activation (D-21, `simulate_path`).
        """
        flows = [CashFlow(d, -abs(subscription), "subscription")
                 for d in self.subscription_days(billing_days)]
        if self.passed and self.pass_day is not None:
            flows.append(CashFlow(int(self.pass_day), -abs(activation), "activation"))
            base = int(self.pass_day) + 1
            for d, a in zip(self.payout_days, self.payout_amounts):
                flows.append(CashFlow(base + int(d) + int(payout_lag_days), float(a), "payout"))
        return sorted(flows, key=lambda f: f.day)


class AttemptSampler(TypingProtocol):
    """Supplies attempt outcomes to the campaign simulation."""

    def sample(self, n: int, *, seed: int) -> list[AttemptOutcome]: ...


class ScriptedAttempts:
    """A fixed list of outcomes, cycled. Deterministic -- for tests and worked examples."""

    def __init__(self, outcomes: Sequence[AttemptOutcome]):
        if not outcomes:
            raise ValueError("ScriptedAttempts needs at least one outcome")
        self.outcomes = list(outcomes)

    def sample(self, n: int, *, seed: int) -> list[AttemptOutcome]:
        return [self.outcomes[i % len(self.outcomes)] for i in range(n)]


class PooledAttempts:
    """Draws with replacement from a pool of simulated outcomes.

    The pool is normally built once by `outcomes_from_adapter` (an expensive vectorised engine
    run) and then resampled cheaply across campaign paths.
    """

    def __init__(self, pool: Sequence[AttemptOutcome]):
        if not pool:
            raise ValueError("PooledAttempts needs a non-empty pool")
        self.pool = list(pool)

    def sample(self, n: int, *, seed: int) -> list[AttemptOutcome]:
        rng = np.random.default_rng(seed)
        idx = rng.integers(0, len(self.pool), size=n)
        return [self.pool[int(i)] for i in idx]


def outcomes_from_adapter(
    protocol: Protocol,
    edge: float,
    n: int,
    *,
    seed: int,
    rules: Any | None = None,
    funded_horizon_days: int = 504,
    combine_max_days: int = 2000,
    payout_dates: str = "exact",
    schedule: PayoutSchedule = PayoutSchedule.EVEN,
    window_days: int = 10,
    combine_draw_factory: Callable[[int], Any] | None = None,
    funded_draw_factory: Callable[[int], Any] | None = None,
    payout_timing: str | None = None,
) -> list[AttemptOutcome]:
    """Build a pool of attempt outcomes by running the vendored engine.

    Args:
        protocol: supplies both legs' policies.
        edge: per-trade edge in units of risk, **net of costs**. Use the **lower confidence
            bound** for any result that feeds a money decision (D-04). With a draw factory
            supplied for a leg, that leg's outcome process is the draw's own and `edge` is
            recorded for provenance only.
        n: pool size.
        seed: explicit. Required.
        rules: engine `Rules`; stage-one defaults if omitted. A research run passes
            `propedge.contract.adapter.rules_from_ledger()` (or
            `propedge.campaign.payout_method.rules_for_method`) so the verified rules apply.
        funded_horizon_days: trading days each funded account is simulated for.
        payout_dates: **"exact"** (the default) records every payout's real date from
            `propedge.contract.funded_dated.simulate_xfa_dated`, which reproduces the vendored
            engine's aggregates bit-for-bit. **"model"** falls back to the `schedule`
            assumption below; it is kept for sensitivity analysis only and must not be used for
            a result that feeds a ranking.
        schedule: how second-and-later payouts are spaced when `payout_dates="model"`.
        window_days: minimum days between payouts under `EARLIEST`.
        combine_draw_factory / funded_draw_factory: build the outcome draw for a leg from the
            number of accounts that leg runs -- `factory(n_accounts) -> draw`, where the draw
            has the engine's signature `draw(n, day, slot, cushion) -> ndarray` (NaN = no
            trade). Factories rather than draws because the funded leg runs one account per
            pass, a count not known until the Combine leg has run, and
            `propedge.outcomes.distribution.EmpiricalDraw` is built for a fixed `n_accounts`.
            None (the default) uses the binary draw at `edge` for that leg, which is the
            validation limit. This is the seam through which an empirical distribution
            reaches the campaign (D-119, slice 1); each factory owns its own seed.
        payout_timing: when a funded account requests its payout (8284233,
            `propedge.contract.payout_timing`). None (the default) is the vendored engine's
            timing, `REQUEST_4_TO_5PM` -- a request submitted between 4:00 and 5:00 PM CT on the
            eligible day -- because this pool reproduces the engine's EV per attempt exactly.
            `REQUEST_AFTER_5PM` applies the rule for a request made after 5:00 PM CT, as the
            lockstep campaign does by default: the next trading day is the Payout request day and
            is left out of the new cycle. Under `payout_dates="model"` with that timing the
            aggregates come from `simulate_xfa_dated`, the engine's own having no such timing.

    Raises:
        ValueError: `payout_dates` is neither "exact" nor "model".
    """
    from propedge.contract.adapter import Rules, run_combine, run_xfa
    from propedge.contract.payout_timing import ENGINE_PAYOUT_TIMING, check_payout_timing

    if payout_dates not in {"exact", "model"}:
        raise ValueError(
            f"payout_dates must be 'exact' or 'model', got {payout_dates!r}"
        )
    payout_timing = check_payout_timing(ENGINE_PAYOUT_TIMING if payout_timing is None else payout_timing)

    rules = rules or Rules()
    comb = run_combine(
        protocol.combine_policy(), edge, n, seed=seed, rules=rules, max_days=combine_max_days,
        draw=combine_draw_factory(n) if combine_draw_factory is not None else None,
    )
    passed = np.asarray(comb.raw["passed"], dtype=bool)
    pass_day = np.asarray(comb.raw["pass_day"], dtype=int)
    fail_day = np.asarray(comb.raw["fail_day"], dtype=int)
    days = np.asarray(comb.raw["days"], dtype=int)

    m = int(passed.sum())
    dated = None
    if m:
        funded_policy = protocol.funded_policy()
        if payout_dates == "exact" or payout_timing != ENGINE_PAYOUT_TIMING:
            from propedge.contract.funded_dated import simulate_xfa_dated

            dated = simulate_xfa_dated(
                rules, funded_policy, edge, m, seed=seed + 1,
                horizon_days=funded_horizon_days,
                draw=funded_draw_factory(m) if funded_draw_factory is not None else None,
                payout_timing=payout_timing,
            )
            cash = np.asarray(dated.cash, dtype=float)
            n_payouts = np.asarray(dated.n_payouts, dtype=int)
            first_day = np.asarray(dated.first_payout_day, dtype=int)
            fclosed = np.asarray(dated.closed, dtype=bool)
            fdays = np.asarray(dated.days, dtype=int)
            if payout_dates == "model":
                dated = None        # the aggregates only; the schedule below spaces the payouts
        else:
            xfa = run_xfa(
                funded_policy, edge, m, seed=seed + 1, rules=rules,
                horizon_days=funded_horizon_days,
                draw=funded_draw_factory(m) if funded_draw_factory is not None else None,
            )
            cash = np.asarray(xfa.raw["cash"], dtype=float)
            n_payouts = np.asarray(xfa.raw["n_payouts"], dtype=int)
            first_day = np.asarray(xfa.raw["first_payout_day"], dtype=int)
            fclosed = np.asarray(xfa.raw["closed"], dtype=bool)
            fdays = np.asarray(xfa.raw["days"], dtype=int)
    else:
        cash = n_payouts = first_day = fclosed = fdays = np.empty(0)

    out: list[AttemptOutcome] = []
    j = 0
    for i in range(n):
        if not passed[i]:
            end = int(fail_day[i]) if fail_day[i] >= 0 else int(max(days[i] - 1, 0))
            out.append(AttemptOutcome(passed=False, combine_end_day=end))
            continue
        pd_ = int(pass_day[i])
        k = int(n_payouts[j])
        fd = int(fdays[j])
        if dated is not None:
            # Real dates, recorded from the funded day loop. No spacing assumption.
            p_days = tuple(int(x) for x in dated.payout_days[j])
            p_amts = tuple(float(x) for x in dated.payout_cash[j])
        else:
            p_days, p_amts = _payout_schedule(
                n_payouts=k,
                first_day=int(first_day[j]),
                total_cash=float(cash[j]),
                end_day=fd,
                schedule=schedule,
                window_days=window_days,
            )
        out.append(
            AttemptOutcome(
                passed=True,
                combine_end_day=pd_,
                pass_day=pd_,
                payout_days=p_days,
                payout_amounts=p_amts,
                funded_end_day=fd,
                funded_closed=bool(fclosed[j]),
            )
        )
        j += 1
    return out


def _payout_schedule(
    *,
    n_payouts: int,
    first_day: int,
    total_cash: float,
    end_day: int,
    schedule: PayoutSchedule,
    window_days: int,
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    """Spread `total_cash` over `n_payouts` dated payouts. See the module docstring."""
    if n_payouts <= 0 or first_day < 0:
        return (), ()
    amt = total_cash / n_payouts
    if n_payouts == 1:
        return (int(first_day),), (float(total_cash),)

    if schedule is PayoutSchedule.EARLIEST:
        days = [first_day + i * window_days for i in range(n_payouts)]
    elif schedule is PayoutSchedule.LATEST:
        days = [max(first_day, end_day - (n_payouts - 1 - i) * window_days)
                for i in range(n_payouts)]
    else:  # EVEN
        span = max(end_day - first_day, n_payouts - 1)
        step = span / (n_payouts - 1)
        days = [int(round(first_day + i * step)) for i in range(n_payouts)]

    days = [int(min(max(d, first_day), max(end_day, first_day))) for d in days]
    return tuple(days), tuple([float(amt)] * n_payouts)


# ------------------------------------------------------------------ simulation


@dataclass
class _FundedAccount:
    """A running funded account inside a campaign path."""

    payout_days: list[int]          # arrival days on the account's clock (lag already added)
    payout_amounts: list[float]
    end_day: int                    # trading days lived; the slot frees on start_day + end_day
    start_day: int                  # first trading day: the day after activation
    next_idx: int = 0
    paid: bool = False              # a payout has been credited to the campaign

    def due(self, day: int) -> float:
        """Cash arriving today, advancing the payout pointer."""
        got = 0.0
        while (
            self.next_idx < len(self.payout_days)
            and self.start_day + self.payout_days[self.next_idx] <= day
        ):
            got += self.payout_amounts[self.next_idx]
            self.next_idx += 1
        return got

    def remaining(self) -> list[tuple[int, float]]:
        """Payouts not yet delivered, as (campaign day, amount).

        Handed to the campaign when the account ends: a payout still in transit belongs to
        the trader, not to the slot, so the slot frees on time and the cash arrives on its day.
        """
        return [
            (self.start_day + int(d), float(a))
            for d, a in zip(self.payout_days[self.next_idx:], self.payout_amounts[self.next_idx:])
        ]


@dataclass(frozen=True)
class CampaignPath:
    """One simulated campaign. Growth, and everything that must be reported beside it."""

    final_cash: float
    initial_bankroll: float
    cash_series: np.ndarray            # cash at the close of each day
    active_funded_series: np.ndarray   # active funded accounts each day
    ruined: bool
    ruin_day: int | None
    max_drawdown: float                # peak-to-trough of cash, in dollars
    max_drawdown_frac: float
    attempts_started: int
    accounts_funded: int
    accounts_ever_paid: int            # funded accounts credited at least once within the horizon
    days_to_first_payout: int | None
    payout_gaps: tuple[int, ...]       # trading days between successive campaign payouts
    total_fees: float
    total_payouts: float
    peak_queue_length: int
    passes_forfeited: int = 0          # passed, never activated: a slot was free and cash was
                                       # below the activation fee (at the pass under "on_pass";
                                       # at the horizon or at ruin under "on_activation")
    combines_abandoned: int = 0        # running but could not afford the next subscription
    passes_on_hold_at_end: int = 0     # passed, still waiting for a SLOT when the path ended
    # Same-day multi-account loss-limit events (RTP trigger 1, D-30). Only the trade-level
    # lockstep loop can see them; the stage-level loop leaves both at 0 because its accounts
    # never share a day.
    same_day_multi_breach_days: int = 0   # days on which two or more accounts hit the MLL
    max_breaches_in_one_day: int = 0
    # Tier sizing (D-117), filled by the lockstep loop when its draws size trades in
    # contracts; zero from the stage-level loop and from fixed-risk draws.
    trades_sized: int = 0
    trades_at_tier_cap: int = 0          # sized at the headroom cap (RTP trigger 2 metric)
    trades_unsized: int = 0              # the risk did not buy one contract: no trade
    trades_stood_aside: int = 0          # D-272 (1), D-301: the allowance carried too little of the risk or the stop was under the floor: no trade
    trades_need_exits: int = 0           # D-306: Combine trades closed at what the account needed to pass (D-313: or at the day's consistency allowance)
    trades_room_capped: int = 0          # D-313: trades cut to the room above the floor
    combines_out_of_room: int = 0        # D-318: Combine attempts ended because their room bought no trade at their R
    combines_abandoned_by_policy: int = 0   # D-329: Combine attempts the policy cancelled (a slot freed, no breach)
    funded_abandoned: int = 0            # D-329: XFAs the policy closed at the trader's request (nothing credited)
    funded_flips: int = 0                # D-339: flip brackets taken by funded accounts (the flip stream)
    funded_flips_won: int = 0            # D-339: of them, winners
    intended_risk_total: float = 0.0
    intended_capped_risk_total: float = 0.0   # D-306: the intention the allowance could carry (the sizing's fidelity measure, P4)
    realised_risk_total: float = 0.0
    # D-305: executed trades across every account, per engine day (the activity line's input); () from loops that do
    # not count them (the stage-level loop) and from the early return before any day runs.
    trades_by_day: tuple[int, ...] = ()

    @property
    def growth_multiple(self) -> float:
        return self.final_cash / self.initial_bankroll if self.initial_bankroll else float("nan")

    def log_growth(self, *, periods_per_year: float = TRADING_DAYS_PER_YEAR) -> float:
        """Continuously compounded growth rate of the fee bankroll, per year.

        `ln(final / initial) / years`. Returns `-inf` when the bankroll reached zero: the log
        is genuinely undefined there, and `-inf` is the honest order statistic -- a path that
        lost everything ranks below every path that did not. Clamping it to a finite floor
        would let a protocol that wipes out half its paths average its way up a ranking.
        """
        if self.initial_bankroll <= 0:
            return float("nan")
        years = len(self.cash_series) / periods_per_year
        if years <= 0:
            return float("nan")
        if self.final_cash <= 0:
            return float("-inf")
        return float(np.log(self.final_cash / self.initial_bankroll) / years)


@dataclass(frozen=True)
class CampaignSummary:
    """Growth, ruin, drawdown and latency across many paths -- always together.

    There is deliberately no accessor that returns growth on its own. A protocol that grows
    fast and ruins often has not won, and the charter requires the two to be read together.

    **`median_log_growth` is the primary ranking metric** and is the only field any ranking
    helper sorts on. The mean-based fields below it are secondary diagnostics: a mean over
    multiplicative outcomes is dominated by a fat right tail, so it can rank a protocol that
    wipes out most of its paths above one that compounds reliably. The median of the log growth
    rate is the quantity a trader actually experiences on a typical path.
    """

    protocol: str
    edge: float
    initial_bankroll: float
    horizon_days: int
    n_paths: int
    seed: int

    # ---- PRIMARY: the ranking metric -------------------------------------------------
    median_log_growth: float          # median over paths of ln(final/initial) / years
    share_log_growth_undefined: float  # share of paths that reached zero cash (log = -inf)

    # ---- SECONDARY: mean-based diagnostics, never the ranking key --------------------
    mean_final_cash: float
    median_final_cash: float
    p10_final_cash: float
    p90_final_cash: float
    mean_growth_multiple: float
    annualised_growth: float

    ruin_probability: float
    mean_max_drawdown: float
    p90_max_drawdown: float

    mean_days_to_first_payout: float
    median_days_to_first_payout: float
    share_accounts_ever_paid: float
    mean_days_between_payouts: float

    mean_accounts_funded: float
    mean_active_funded: float
    peak_active_funded: int
    mean_peak_queue_length: float
    mean_passes_forfeited: float
    mean_combines_abandoned: float

    payout_lag_days: int
    payout_schedule: str
    max_concurrent_accounts: int
    payout_method: str = "aeropay"          # whose fee-and-lag pair the lag belongs to (D-24)
    activation_timing: str = ACTIVATION_ON_ACTIVATION
    # Same-day multi-account loss-limit events (RTP trigger 1, D-30): visible only to the
    # trade-level lockstep loop; 0 from the stage-level loop, whose accounts never share a day.
    mean_same_day_multi_breach_days: float = 0.0
    share_paths_with_same_day_multi_breach: float = 0.0
    # Tier sizing (D-117): NaN when no draw sized trades in contracts.
    share_trades_at_tier_cap: float = float("nan")     # must stay below one half
    share_trades_unsized: float = float("nan")
    share_trades_stood_aside: float = float("nan")     # D-301: of the trades offered to a sizing draw, those it declined under D-272 (1)
    realised_to_intended_risk: float = float("nan")    # 1.0 when the cap never binds
    realised_to_intended_capped_risk: float = float("nan")   # D-306: against the allowance-capped intention (1.0 but for contract rounding)
    share_trades_need_exits: float = float("nan")      # D-306: of the sized trades, Combine trades closed at the need to pass
    share_trades_room_capped: float = float("nan")     # D-313: of the sized trades, those cut to the room above the floor
    share_combines_out_of_room: float = float("nan")   # D-318: of the Combine attempts started, those ended out of room
    provenance: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        return (
            f"protocol {self.protocol}  edge {self.edge:.4f}  bankroll "
            f"${self.initial_bankroll:,.0f}  {self.horizon_days} trading days  "
            f"{self.n_paths} paths (seed {self.seed})\n"
            f"  PRIMARY  median log growth {self.median_log_growth:+.4f} /yr "
            f"(over {self.horizon_days} trading days from ${self.initial_bankroll:,.0f}); "
            f"paths reaching zero cash {self.share_log_growth_undefined:.1%}\n"
            f"  GROWTH   mean final cash ${self.mean_final_cash:,.0f} "
            f"(median ${self.median_final_cash:,.0f}, p10 ${self.p10_final_cash:,.0f}, "
            f"p90 ${self.p90_final_cash:,.0f}); annualised {self.annualised_growth:.2%}\n"
            f"  RUIN     {self.ruin_probability:.2%}\n"
            f"           (mean-based fields are SECONDARY diagnostics, not the ranking key)\n"
            f"  DRAWDOWN mean ${self.mean_max_drawdown:,.0f}, p90 "
            f"${self.p90_max_drawdown:,.0f}\n"
            f"  LATENCY  days to first payout: mean {self.mean_days_to_first_payout:.1f}, "
            f"median {self.median_days_to_first_payout:.1f}; between payouts "
            f"{self.mean_days_between_payouts:.1f}; share of accounts that ever pay "
            f"{self.share_accounts_ever_paid:.1%}\n"
            f"  ACCOUNTS funded {self.mean_accounts_funded:.2f}, mean active "
            f"{self.mean_active_funded:.2f}, peak {self.peak_active_funded}, "
            f"cap {self.max_concurrent_accounts}, mean peak hold queue "
            f"{self.mean_peak_queue_length:.2f}; forfeited passes "
            f"{self.mean_passes_forfeited:.2f}, abandoned Combines "
            f"{self.mean_combines_abandoned:.2f}\n"
            f"  CONDUCT  same-day multi-account loss-limit days: mean "
            f"{self.mean_same_day_multi_breach_days:.2f} per path, paths with any "
            f"{self.share_paths_with_same_day_multi_breach:.1%} (RTP trigger 1, D-30; "
            f"0 from the stage-level loop, which cannot see them)\n"
            f"  SIZING   trades at the tier cap {self.share_trades_at_tier_cap:.1%} (D-117: "
            f"must stay below one half), unsized {self.share_trades_unsized:.1%}, realised / "
            f"intended risk {self.realised_to_intended_risk:.3f} (NaN when no draw sized in "
            f"contracts)\n"
            f"  ASSUMPTIONS payout lag {self.payout_lag_days} d via {self.payout_method} "
            f"(ledger 8284233, D-24); activation charged "
            + (
                "on activation (D-21)"
                if self.activation_timing == ACTIVATION_ON_ACTIVATION
                else "on the pass (reconciliation and sensitivity only)"
            )
            + f"; payout schedule {self.payout_schedule}"
        )


def simulate_path(
    sampler: AttemptSampler,
    *,
    seed: int,
    initial_bankroll: float,
    horizon_days: int,
    max_concurrent_accounts: int,
    subscription: float,
    billing_days: int,
    activation: float,
    payout_lag_days: int,
    max_concurrent_combines: int = 1,
    reinvest: bool = True,
    max_attempts: int | None = None,
    attempt_pool_size: int = 256,
    stop_buying_when_queued: bool = True,
    activation_timing: str = ACTIVATION_ON_ACTIVATION,
) -> CampaignPath:
    """Simulate one campaign over `horizon_days` trading days.

    Mechanics, per day:

    1. Subscriptions fall due for Combines still running, at the **start** of the day. This
       ordering matters and matches the engine: `propsim.simulate_combine` charges the
       subscription to every account still alive at the start of a billing day, so a Combine
       that resolves *on* a billing day has already paid for it. Billing after resolution
       would quietly undercount fees.
    2. Payouts due today arrive and are added to cash (if `reinvest`, that cash is available
       to buy Combines from the same day).
    3. Combines that resolve today: a pass joins the **hold queue**; a fail simply ends.
    4. Funded accounts that end today free a slot, which the head of the hold queue takes --
       paying the **activation fee at that moment**. That is the verified rule (article
       8284217, D-21): activation is trader-initiated once a slot is free and the fee falls due
       then. A pass that cannot afford it stays on hold; it is never overdrawn and never
       silently dropped.
    5. New Combines are started while cash covers a subscription and a slot is free.
    6. Ruin is checked: nothing running and nothing funded, and the campaign cannot take its
       next step -- a pass on hold it cannot activate (and, under `stop_buying_when_queued`,
       cannot buy past), or an empty queue and cash below a subscription.

    Calendar convention: a Combine bought on day `d` trades from day `d + 1`, its engine day 0,
    exactly as a funded account activated on day `d` starts on `d + 1`. A resolution on engine
    day `p` is therefore recognised on day `d + 1 + p`, and the subscription rebills every
    `billing_days` of the account's own trading days. `propedge.campaign.lockstep` shares the
    convention and reproduces this loop exactly on the same outcome streams.

    Fees are only paid out of money the campaign has. A running Combine that cannot afford its
    next subscription is **abandoned** and counted; a pass that a free slot could not activate
    for want of cash by the end of the path is **forfeited** and counted. Letting cash go
    negative instead would silently model an overdraft and understate ruin -- the failure mode
    that matters most here.

    Args:
        payout_lag_days: trading days between a payout's eligibility and its arrival in the
            bankroll. **No default.** `simulate_campaign` resolves it from the verified ledger
            by payout method (D-24); pass 0 here only in a mechanics test that says so.
        activation_timing: "on_activation" (default; the verified rule, D-21) or "on_pass",
            which charges the fee when the Combine passes and forfeits a pass that cannot pay
            it then. The two differ only for passes that wait in the queue, so "on_pass" is
            kept for reconciliation with the engine's EV per attempt (no cap, no queue) and for
            sensitivity, never for a reported ranking.
        reinvest: if False, only the initial bankroll is ever spent. Payouts still arrive and
            are still counted in the final cash, but they do not fund new Combines. This is
            the control arm -- it isolates the contribution of reinvestment from that of the
            edge.
        max_attempts: stop starting new attempts after this many. Used to measure a fixed
            number of attempts (e.g. to reconcile with EV per attempt).
        attempt_pool_size: how many outcomes to draw from the sampler at a time.
        stop_buying_when_queued: do not start a new Combine while a passed account is already
            waiting for a funded slot. This is the sensible operating policy and the default:
            once the cap is full, another pass buys nothing but fees. Set False to model an
            operator who keeps buying regardless -- worth running once, because it shows how
            much the cap costs a protocol that ignores it.

    Not modelled: a Live Funded Account also blocks activation (8284217). This project runs
    none, so the cap is the count of funded accounts alone.
    """
    if activation_timing not in ACTIVATION_TIMINGS:
        raise ValueError(
            f"activation_timing must be one of {ACTIVATION_TIMINGS}, got {activation_timing!r}"
        )
    on_pass = activation_timing == ACTIVATION_ON_PASS

    rng = np.random.default_rng(seed)
    cash = float(initial_bankroll)
    peak_cash = cash

    pending = list(sampler.sample(attempt_pool_size, seed=int(rng.integers(0, 2**31 - 1))))
    pend_i = 0

    running: list[dict[str, Any]] = []     # Combines in progress
    funded: list[_FundedAccount] = []
    queue: list[AttemptOutcome] = []       # passed, waiting for a slot
    pending_payouts: list[tuple[int, float, _FundedAccount]] = []   # in transit after an account ended

    cash_series = np.zeros(horizon_days, dtype=float)
    active_series = np.zeros(horizon_days, dtype=int)

    ruined = False
    ruin_day: int | None = None
    attempts_started = 0
    accounts_funded = 0
    accounts_ever_paid = 0
    total_fees = 0.0
    total_payouts = 0.0
    peak_queue = 0
    passes_forfeited = 0
    combines_abandoned = 0
    passes_on_hold_at_end = 0
    payout_days_campaign: list[int] = []

    # A campaign that cannot buy its first Combine is ruined before it starts.
    if cash < subscription:
        cash_series[:] = cash
        return CampaignPath(
            final_cash=cash, initial_bankroll=float(initial_bankroll),
            cash_series=cash_series, active_funded_series=active_series,
            ruined=True, ruin_day=0, max_drawdown=0.0, max_drawdown_frac=0.0,
            attempts_started=0, accounts_funded=0, accounts_ever_paid=0,
            days_to_first_payout=None, payout_gaps=(), total_fees=0.0,
            total_payouts=0.0, peak_queue_length=0,
            passes_forfeited=0, combines_abandoned=0,
        )

    max_dd = 0.0

    for day in range(horizon_days):
        # 1. subscriptions due at the START of the day, before anything resolves -- the
        #    engine charges every Combine still alive at the start of a billing day.
        #    A Combine whose next subscription is unaffordable is abandoned, not overdrawn.
        keep: list[dict[str, Any]] = []
        for c in running:
            # Engine day 0 is the day after purchase, so the k-th rebill (engine day
            # k * billing_days) falls on calendar day start + 1 + k * billing_days.
            elapsed = day - c["start"]
            due = 1 + max(0, (elapsed - 1) // billing_days)
            alive = True
            while c["subs_paid"] < due:
                if cash < subscription:
                    alive = False
                    combines_abandoned += 1
                    break
                cash -= subscription
                total_fees += subscription
                c["subs_paid"] += 1
            if alive:
                keep.append(c)
        running = keep

        # 2. payouts arriving today -- from running accounts, and from accounts that have
        #    already ended but whose lagged payouts are still in transit.
        for acc in funded:
            got = acc.due(day)
            if got:
                cash += got
                total_payouts += got
                payout_days_campaign.append(day)
                if not acc.paid:
                    acc.paid = True
                    accounts_ever_paid += 1
        still_pending: list[tuple[int, float, _FundedAccount]] = []
        for arrival, amount, acc in pending_payouts:
            if arrival <= day:
                cash += amount
                total_payouts += amount
                payout_days_campaign.append(day)
                if not acc.paid:
                    acc.paid = True
                    accounts_ever_paid += 1
            else:
                still_pending.append((arrival, amount, acc))
        pending_payouts = still_pending

        # 3. Combines resolving today
        still: list[dict[str, Any]] = []
        for c in running:
            o: AttemptOutcome = c["outcome"]
            # Engine day p is calendar day start + 1 + p (the account trades from the day
            # after purchase), and the resolution is recognised on the day it occurs.
            end = c["start"] + 1 + (o.pass_day if o.passed else o.combine_end_day)
            if day < end:
                still.append(c)
                continue
            if o.passed:
                if on_pass:
                    # Reconciliation/sensitivity arm: the fee at the pass. A pass that cannot
                    # afford it is forfeited, not overdrawn.
                    if cash < activation:
                        passes_forfeited += 1
                        continue
                    cash -= activation
                    total_fees += activation
                queue.append(o)
        running = still

        # 4. funded accounts ending today free their slot. A payout still in transit (lag)
        #    belongs to the campaign, not to the slot: it moves to the pending list and arrives
        #    on its day, while the slot is free at once.
        ending = [a for a in funded if a.start_day + a.end_day <= day]
        for a in ending:
            pending_payouts.extend((d, amt, a) for d, amt in a.remaining())
        funded = [a for a in funded if a.start_day + a.end_day > day]

        # ... and the hold queue fills any free slot. Under the verified rule the activation
        #     fee falls due HERE, when the trader activates the account (8284217, D-21). A pass
        #     that cannot afford it stays at the head of the queue: not overdrawn, not dropped,
        #     and -- because the queue is FIFO -- not overtaken by a later pass.
        while queue and len(funded) < max_concurrent_accounts:
            o = queue[0]
            if not on_pass:
                if cash < activation:
                    break
                cash -= activation
                total_fees += activation
            queue.pop(0)
            acc = _FundedAccount(
                payout_days=[int(d) + int(payout_lag_days) for d in o.payout_days],
                payout_amounts=[float(a) for a in o.payout_amounts],
                end_day=int(o.funded_end_day or 0),
                start_day=day + 1,
            )
            funded.append(acc)
            accounts_funded += 1
        peak_queue = max(peak_queue, len(queue))

        # 5. start new Combines.
        #    With reinvestment off, only the initial bankroll is ever spent -- so the budget is
        #    what is left of it after fees, not current cash (which payouts have topped up).
        spendable = cash if reinvest else min(cash, float(initial_bankroll) - total_fees)
        blocked_by_queue = stop_buying_when_queued and bool(queue)
        while (
            not blocked_by_queue
            and len(running) < max_concurrent_combines
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
        ):
            if pend_i >= len(pending):
                pending = list(
                    sampler.sample(attempt_pool_size, seed=int(rng.integers(0, 2**31 - 1)))
                )
                pend_i = 0
            o = pending[pend_i]
            pend_i += 1
            cash -= subscription
            spendable -= subscription
            total_fees += subscription
            running.append({"outcome": o, "start": day, "subs_paid": 1})
            attempts_started += 1

        # 6. ruin check: nothing is running or funded, and the campaign cannot take its next
        #    step. With a pass on hold the next step is its activation; without one, a
        #    purchase. (Under "on_pass" a queued pass with no funded account cannot occur --
        #    the slot is free and the fee is already paid -- so this reduces to the purchase
        #    test, which is the original definition.)
        if not ruined:
            nothing_live = not running and not funded
            if queue:
                stuck = cash < activation and (stop_buying_when_queued or cash < subscription)
            else:
                stuck = cash < subscription
            if nothing_live and stuck:
                ruined = True
                ruin_day = day

        cash_series[day] = cash
        active_series[day] = len(funded)
        peak_cash = max(peak_cash, cash)
        max_dd = max(max_dd, peak_cash - cash)

    # Passes still on hold when the path ends. With a free slot, only cash stood between them
    # and activation: forfeited under the verified timing. With the cap full they were simply
    # waiting for a slot, which is the queue doing its job, not a loss.
    if queue:
        if len(funded) < max_concurrent_accounts and not on_pass:
            passes_forfeited += len(queue)
        else:
            passes_on_hold_at_end = len(queue)

    gaps = tuple(
        int(b - a) for a, b in zip(payout_days_campaign, payout_days_campaign[1:])
    )
    return CampaignPath(
        final_cash=float(cash),
        initial_bankroll=float(initial_bankroll),
        cash_series=cash_series,
        active_funded_series=active_series,
        ruined=ruined,
        ruin_day=ruin_day,
        max_drawdown=float(max_dd),
        max_drawdown_frac=float(max_dd / peak_cash) if peak_cash else 0.0,
        attempts_started=attempts_started,
        accounts_funded=accounts_funded,
        accounts_ever_paid=accounts_ever_paid,
        days_to_first_payout=payout_days_campaign[0] if payout_days_campaign else None,
        payout_gaps=gaps,
        total_fees=float(total_fees),
        total_payouts=float(total_payouts),
        peak_queue_length=peak_queue,
        passes_forfeited=passes_forfeited,
        combines_abandoned=combines_abandoned,
        passes_on_hold_at_end=passes_on_hold_at_end,
    )


def simulate_campaign(
    sampler: AttemptSampler,
    protocol: Protocol,
    *,
    edge: float,
    seed: int,
    initial_bankroll: float,
    horizon_days: int = 504,
    n_paths: int = 500,
    subscription: float = 49.0,
    billing_days: int = 21,
    activation: float = 149.0,
    payout_lag_days: int | None = None,
    payout_method: str = "aeropay",
    activation_timing: str = ACTIVATION_ON_ACTIVATION,
    payout_schedule: PayoutSchedule = PayoutSchedule.EVEN,
    max_concurrent_accounts: int | None = None,
    max_concurrent_combines: int = 1,
    reinvest: bool = True,
    max_attempts: int | None = None,
    stop_buying_when_queued: bool = True,
    require_verified_cap: bool = True,
    ledger: Any | None = None,
) -> tuple[CampaignSummary, list[CampaignPath]]:
    """Run `n_paths` campaigns and summarise growth, ruin, drawdown and latency together.

    Args:
        max_concurrent_accounts: the cap. If None it is read from the rules ledger
            (`max_active_funded_accounts`, verified at 5, D-21) through the rule gate, which
            raises if the rule is ever not verified -- the campaign model rests entirely on
            this number, so it may not be guessed.
        require_verified_cap: set False only in tests that pass an explicit cap and say so.
        payout_lag_days: trading days from a payout's eligibility to cash in the bankroll.
            None (the default) reads the verified ledger for `payout_method` -- Aeropay 3 days
            at no fee, ACH 6 days at $30 (article 8284233, D-24). Zero is not a default: pass
            it explicitly, and only for a mechanics check that says so.
        payout_method: "aeropay" (the US baseline) or "ach". Fee and lag are one joint choice,
            so the attempt pool for an ACH campaign must be built with the ACH fee inside the
            engine (`propedge.campaign.payout_method.rules_for_method`); this function cannot
            see the pool's fee and does not check it.
        activation_timing: "on_activation" (the verified rule, D-21) or "on_pass"; see
            `simulate_path`.
        edge: recorded for provenance. Use the **lower confidence bound** for any run that
            feeds a money decision (D-04).

    Returns:
        (summary, paths).
    """
    need_ledger = (max_concurrent_accounts is None and require_verified_cap) or (
        payout_lag_days is None
    )
    if need_ledger and ledger is None:
        from propedge.contract.rules import load_rules

        ledger = load_rules()

    if max_concurrent_accounts is None:
        if require_verified_cap:
            max_concurrent_accounts = int(ledger.value("max_active_funded_accounts"))
        else:
            max_concurrent_accounts = protocol.max_concurrent_accounts

    if payout_lag_days is None:
        from propedge.campaign.payout_method import payout_method_terms

        terms = payout_method_terms(payout_method, ledger=ledger)
        payout_lag_days = terms.lag_days
        lag_source = f"ledger {terms.lag_key} (article {terms.article_id})"
    else:
        lag_source = "explicit argument"

    rng = np.random.default_rng(seed)
    paths = [
        simulate_path(
            sampler,
            seed=int(rng.integers(0, 2**31 - 1)),
            initial_bankroll=initial_bankroll,
            horizon_days=horizon_days,
            max_concurrent_accounts=max_concurrent_accounts,
            subscription=subscription,
            billing_days=billing_days,
            activation=activation,
            payout_lag_days=payout_lag_days,
            max_concurrent_combines=max_concurrent_combines,
            reinvest=reinvest,
            max_attempts=max_attempts,
            stop_buying_when_queued=stop_buying_when_queued,
            activation_timing=activation_timing,
        )
        for _ in range(n_paths)
    ]

    summary = summarise_paths(
        paths,
        protocol=protocol, edge=edge, seed=seed, initial_bankroll=initial_bankroll,
        horizon_days=horizon_days, n_paths=n_paths, payout_lag_days=int(payout_lag_days),
        payout_schedule=str(payout_schedule.value),
        max_concurrent_accounts=int(max_concurrent_accounts),
        payout_method=payout_method, activation_timing=activation_timing,
        provenance={
            "simulation": "propedge.campaign.reinvest.simulate_campaign",
            "subscription": subscription,
            "billing_days": billing_days,
            "activation": activation,
            "activation_timing": activation_timing,
            "payout_method": payout_method,
            "payout_lag_source": lag_source,
            "reinvest": reinvest,
            "max_concurrent_combines": max_concurrent_combines,
            "max_attempts": max_attempts,
            "note": (
                "Payout dating depends on how the attempt pool was built: "
                "outcomes_from_adapter(payout_dates='exact') records real dates from "
                "propedge.contract.funded_dated (validated bit-for-bit against the vendored "
                "engine), while payout_dates='model' applies the PayoutSchedule assumption and "
                "is for sensitivity only. The payout_schedule field below is inert under "
                "'exact'."
            ),
        },
    )
    return summary, paths


def summarise_paths(
    paths: Sequence[CampaignPath],
    *,
    protocol: Protocol,
    edge: float,
    seed: int,
    initial_bankroll: float,
    horizon_days: int,
    n_paths: int,
    payout_lag_days: int,
    payout_schedule: str,
    max_concurrent_accounts: int,
    payout_method: str,
    activation_timing: str,
    provenance: dict[str, Any],
) -> CampaignSummary:
    """Growth, ruin, drawdown and latency across `paths` -- one summary, always together.

    Shared by the stage-level campaign here and the trade-level lockstep campaign
    (`propedge.campaign.lockstep`), so the two are summarised by the same arithmetic and a
    ranking never depends on which loop produced the paths.
    """
    paths = list(paths)
    final = np.array([p.final_cash for p in paths])
    dd = np.array([p.max_drawdown for p in paths])
    first = np.array(
        [p.days_to_first_payout for p in paths if p.days_to_first_payout is not None],
        dtype=float,
    )
    gaps = np.array([g for p in paths for g in p.payout_gaps], dtype=float)
    funded_n = np.array([p.accounts_funded for p in paths], dtype=float)
    paid_n = np.array([p.accounts_ever_paid for p in paths], dtype=float)
    active = np.array([p.active_funded_series for p in paths], dtype=float)

    years = horizon_days / TRADING_DAYS_PER_YEAR
    with np.errstate(invalid="ignore", divide="ignore"):
        mult = final / initial_bankroll if initial_bankroll else np.full_like(final, np.nan)
        ann = (
            float(np.nanmean(mult) ** (1.0 / years) - 1.0)
            if years > 0 and np.nanmean(mult) > 0
            else float("nan")
        )

    log_growth = np.array(
        [p.log_growth(periods_per_year=TRADING_DAYS_PER_YEAR) for p in paths], dtype=float
    )
    n_sized = sum(p.trades_sized for p in paths)
    n_stood = sum(p.trades_stood_aside for p in paths)
    intended = sum(p.intended_risk_total for p in paths)
    intended_capped = sum(p.intended_capped_risk_total for p in paths)

    return CampaignSummary(
        protocol=protocol.name,
        edge=float(edge),
        initial_bankroll=float(initial_bankroll),
        horizon_days=int(horizon_days),
        n_paths=int(n_paths),
        seed=int(seed),
        # np.median propagates -inf correctly: if more than half the paths reached zero cash,
        # the median is -inf, which is the right verdict and not a number to be smoothed away.
        median_log_growth=float(np.median(log_growth)),
        share_log_growth_undefined=float(np.mean(~np.isfinite(log_growth))),
        mean_final_cash=float(final.mean()),
        median_final_cash=float(np.median(final)),
        p10_final_cash=float(np.percentile(final, 10)),
        p90_final_cash=float(np.percentile(final, 90)),
        mean_growth_multiple=float(np.nanmean(mult)),
        annualised_growth=ann,
        ruin_probability=float(np.mean([p.ruined for p in paths])),
        mean_max_drawdown=float(dd.mean()),
        p90_max_drawdown=float(np.percentile(dd, 90)),
        mean_days_to_first_payout=float(first.mean()) if len(first) else float("nan"),
        median_days_to_first_payout=float(np.median(first)) if len(first) else float("nan"),
        share_accounts_ever_paid=(
            float(paid_n.sum() / funded_n.sum()) if funded_n.sum() else float("nan")
        ),
        mean_days_between_payouts=float(gaps.mean()) if len(gaps) else float("nan"),
        mean_accounts_funded=float(funded_n.mean()),
        mean_active_funded=float(active.mean()),
        peak_active_funded=int(active.max()) if active.size else 0,
        mean_peak_queue_length=float(np.mean([p.peak_queue_length for p in paths])),
        mean_passes_forfeited=float(np.mean([p.passes_forfeited for p in paths])),
        mean_combines_abandoned=float(np.mean([p.combines_abandoned for p in paths])),
        payout_lag_days=int(payout_lag_days),
        payout_schedule=str(payout_schedule),
        max_concurrent_accounts=int(max_concurrent_accounts),
        payout_method=str(payout_method),
        activation_timing=str(activation_timing),
        mean_same_day_multi_breach_days=float(
            np.mean([p.same_day_multi_breach_days for p in paths])
        ),
        share_paths_with_same_day_multi_breach=float(
            np.mean([p.same_day_multi_breach_days > 0 for p in paths])
        ),
        share_trades_at_tier_cap=(
            float(sum(p.trades_at_tier_cap for p in paths) / n_sized) if n_sized else float("nan")
        ),
        share_trades_unsized=(
            float(sum(p.trades_unsized for p in paths) / n_sized) if n_sized else float("nan")
        ),
        share_trades_stood_aside=(
            float(n_stood / (n_sized + n_stood)) if n_sized + n_stood else float("nan")
        ),
        realised_to_intended_risk=(
            float(sum(p.realised_risk_total for p in paths) / intended)
            if intended > 0 else float("nan")
        ),
        realised_to_intended_capped_risk=(
            float(sum(p.realised_risk_total for p in paths) / intended_capped)
            if intended_capped > 0 else float("nan")
        ),
        share_trades_need_exits=(
            float(sum(p.trades_need_exits for p in paths) / n_sized) if n_sized else float("nan")
        ),
        share_trades_room_capped=(
            float(sum(p.trades_room_capped for p in paths) / n_sized) if n_sized else float("nan")
        ),
        share_combines_out_of_room=(
            float(sum(p.combines_out_of_room for p in paths) / n_att) if (n_att := sum(p.attempts_started for p in paths))
            else float("nan")
        ),
        provenance=dict(provenance),
    )


def rank_protocols(summaries: Sequence[CampaignSummary]) -> list[CampaignSummary]:
    """Rank by **median log growth**, best first. The only sanctioned ranking key.

    Not by mean final cash, not by mean growth multiple, not by annualised growth of the mean:
    all three are means over multiplicative outcomes and are dominated by a fat right tail, so
    they can put a protocol that wipes out most of its paths above one that compounds reliably.

    Comparability is the caller's responsibility: median log growth is defined **per horizon
    and per starting bankroll**, so ranking summaries that differ in either compares different
    quantities. This function refuses that rather than silently producing an ordering.

    Raises:
        ValueError: the summaries do not share a horizon and a starting bankroll.
    """
    summaries = list(summaries)
    if not summaries:
        return []

    horizons = {s.horizon_days for s in summaries}
    bankrolls = {s.initial_bankroll for s in summaries}
    if len(horizons) > 1 or len(bankrolls) > 1:
        raise ValueError(
            "median log growth is defined per horizon and per starting bankroll, so these "
            f"summaries are not comparable: horizons {sorted(horizons)}, bankrolls "
            f"{sorted(bankrolls)}. Rank within a horizon and bankroll, and report the "
            "rankings side by side."
        )

    # -inf sorts last, which is what a wiped-out protocol deserves.
    return sorted(summaries, key=lambda s: s.median_log_growth, reverse=True)
