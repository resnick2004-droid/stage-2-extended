"""IRR of dated cash flows.

Stage one's EV per attempt values a dollar paid on day 8 and a dollar paid on day 400
identically. The objective change (D-02) is to stop doing that. An attempt is a schedule:

    day 0    -$49    Combine subscription
    day 21   -$49    second subscription (if still running)
    day 34   -$149   activation, on passing
    day 61   +$1,800 first payout
    day 103  +$900   second payout

and its return is the rate that discounts that schedule to zero.

**Attempts with no payout have no IRR.** Every flow is negative, so no rate sets the NPV to
zero. This is not an edge case to paper over: at e = 0.05 the great majority of attempts never
pay out, and averaging IRRs over only the attempts that did would report the return of a
strategy nobody can follow. `portfolio_irr` -- one schedule over all attempts -- is the
honest aggregate, and `IRRSummary.share_undefined` is reported beside it every time.

**Per-attempt IRR is a badly behaved statistic here, and that is a property of the business,
not of this code.** The capital at risk in one attempt is a few hundred dollars of fees; the
payout is thousands, weeks later. A $198 outlay returning $1,800 after 31 trading days
annualises to an internal rate in the tens of millions of percent -- arithmetically correct and
economically meaningless, because the rate assumes the whole cycle can be repeated
instantaneously at that scale, which the 5-account cap and the calendar forbid. Such a rate
lies outside the solver's bracket and is reported as **undefined with a reason**, never
silently clipped to the bracket edge.

This is exactly why the charter makes the reinvestment simulation the confirming instrument
(D-02) rather than the per-attempt IRR: `propedge.campaign.reinvest` cannot produce an absurd
number, because it has to actually spend the cash on something. Use per-attempt IRR to rank
the *timing* of comparable schedules; use `portfolio_irr` and the reinvestment simulation to
say what a protocol is worth.

Rates are per **year** by default, from day counts in **trading days** (252/year), because
every day index the contract engine produces is a trading-day index.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

TRADING_DAYS_PER_YEAR = 252.0


@dataclass(frozen=True)
class CashFlow:
    """One dated cash flow. Negative is money out, positive is money in.

    `day` is a trading-day index from the start of the attempt (day 0 = the first day of the
    Combine).
    """

    day: int
    amount: float
    kind: str = ""   # "subscription" | "activation" | "payout" | "reset" | ...

    def __post_init__(self) -> None:
        if self.day < 0:
            raise ValueError(f"cash flow day must be >= 0, got {self.day}")


@dataclass(frozen=True)
class IRRResult:
    """An IRR, or a documented reason there isn't one."""

    irr: float                 # annualised; NaN when undefined
    defined: bool
    reason: str                # why undefined, when it is
    npv_at_zero: float         # sum of flows -- the undiscounted total
    n_flows: int
    first_inflow_day: int | None
    total_out: float
    total_in: float

    @property
    def multiple(self) -> float:
        """Money in / money out. Defined whenever anything was spent; 0 if nothing came in."""
        return self.total_in / self.total_out if self.total_out > 0 else float("nan")


def npv(flows: Sequence[CashFlow], rate: float, *, periods_per_year: float = TRADING_DAYS_PER_YEAR) -> float:
    """Net present value at an annualised `rate`.

    Discounting is `(1 + rate) ** (-day / periods_per_year)`, i.e. annual compounding applied
    to a fractional year. Rates at or below -100 % are rejected rather than returned as inf.
    """
    if rate <= -1.0:
        raise ValueError(f"rate {rate} <= -100 % has no discount factor")
    return float(
        sum(f.amount * (1.0 + rate) ** (-f.day / periods_per_year) for f in flows)
    )


def irr(
    flows: Sequence[CashFlow],
    *,
    periods_per_year: float = TRADING_DAYS_PER_YEAR,
    lo: float = -0.999999,
    hi: float = 1e6,
    tol: float = 1e-10,
    max_iter: int = 400,
) -> IRRResult:
    """IRR of one attempt's dated cash flows.

    Solved by bisection on NPV, which is monotone in the rate for a **conventional** schedule
    (outflows first, then inflows). Bisection rather than Newton because it cannot diverge and
    the bracket is known; the schedules here are small and speed is irrelevant.

    Undefined, and reported as such rather than fudged, when:
      * there are no flows;
      * nothing was ever paid out (every flow <= 0) -- the common case at low edge;
      * nothing was ever paid in (no outflow), so there is no investment to earn a return on;
      * the NPV does not change sign across the bracket. Two quite different situations both
        land here, and the reason string distinguishes them: a non-conventional schedule
        (inflows before a later outflow) that may have zero or several roots, and -- far more
        common in this stage -- a small fee outlay returning a large payout quickly, whose
        annualised rate exceeds `hi`. The second is reported as undefined rather than clipped
        to `hi`, because a rate of 10^6 and a rate of 10^8 are equally uninformative and
        pretending to distinguish them would invite ranking protocols by an artefact of the
        bracket.
    """
    flows = list(flows)
    if not flows:
        return IRRResult(np.nan, False, "no cash flows", 0.0, 0, None, 0.0, 0.0)

    total_out = -sum(f.amount for f in flows if f.amount < 0)
    total_in = sum(f.amount for f in flows if f.amount > 0)
    inflow_days = [f.day for f in flows if f.amount > 0]
    first_in = min(inflow_days) if inflow_days else None
    total = float(sum(f.amount for f in flows))

    if total_in <= 0:
        return IRRResult(
            np.nan, False,
            "no inflow: the attempt never paid out, so no rate discounts the schedule to "
            "zero. Report it in the share of attempts with undefined IRR, and use "
            "portfolio_irr for an aggregate.",
            total, len(flows), None, total_out, 0.0,
        )
    if total_out <= 0:
        return IRRResult(
            np.nan, False,
            "no outflow: nothing was invested, so there is no rate of return on it.",
            total, len(flows), first_in, 0.0, total_in,
        )

    f_lo, f_hi = npv(flows, lo, periods_per_year=periods_per_year), npv(flows, hi, periods_per_year=periods_per_year)
    if f_lo * f_hi > 0:
        if f_hi > 0:
            why = (
                f"the IRR exceeds the solver bracket ({hi:g}): NPV is still {f_hi:.4g} at "
                f"that rate. A small fee outlay (${total_out:,.2f}) returning ${total_in:,.2f} "
                f"after {first_in} trading days annualises to a rate that is arithmetically "
                "correct and economically meaningless -- it assumes the cycle repeats "
                "instantaneously at scale, which the account cap and the calendar forbid. Use "
                "portfolio_irr and the reinvestment simulation for this attempt."
            )
        else:
            why = (
                f"NPV does not change sign on [{lo:g}, {hi:g}] (NPV {f_lo:.4g} .. {f_hi:.4g}); "
                "the schedule is non-conventional and may have zero or several roots."
            )
        return IRRResult(
            np.nan, False, why, total, len(flows), first_in, total_out, total_in,
        )

    a, b = lo, hi
    for _ in range(max_iter):
        mid = 0.5 * (a + b)
        fm = npv(flows, mid, periods_per_year=periods_per_year)
        if abs(fm) < tol or (b - a) < tol:
            break
        if fm * f_lo > 0:
            a, f_lo = mid, fm
        else:
            b = mid
    rate = 0.5 * (a + b)

    return IRRResult(
        irr=float(rate), defined=True, reason="", npv_at_zero=total,
        n_flows=len(flows), first_inflow_day=first_in,
        total_out=total_out, total_in=total_in,
    )


@dataclass(frozen=True)
class IRRSummary:
    """IRR across many attempts, with the undefined ones visible."""

    n_attempts: int
    n_defined: int
    share_undefined: float
    median_irr_defined: float
    mean_irr_defined: float
    portfolio_irr: float
    portfolio_defined: bool
    portfolio_reason: str
    mean_net_cash: float

    def summary(self) -> str:
        return (
            f"attempts            {self.n_attempts}\n"
            f"IRR defined         {self.n_defined} "
            f"({1 - self.share_undefined:.1%}); undefined {self.share_undefined:.1%} "
            f"(never paid out)\n"
            f"median IRR (defined){self.median_irr_defined:>10.2%}\n"
            f"portfolio IRR       {self.portfolio_irr:>10.2%}"
            + ("" if self.portfolio_defined else f"  (undefined: {self.portfolio_reason})")
            + f"\nmean net cash       {self.mean_net_cash:>10,.2f}"
        )


def portfolio_irr(
    attempts: Iterable[Sequence[CashFlow]],
    *,
    stagger_days: int = 0,
    periods_per_year: float = TRADING_DAYS_PER_YEAR,
) -> IRRResult:
    """IRR of all attempts merged into one schedule.

    The honest aggregate: an attempt that never pays out contributes its fees as real
    outflows, instead of being dropped for having no IRR of its own. This is what a trader
    running the protocol repeatedly actually experiences.

    Args:
        stagger_days: trading days between successive attempts' start dates. 0 runs them all
            from day 0 (simultaneous); a positive value runs them in sequence, which is what
            a single-slot campaign looks like.
    """
    merged: list[CashFlow] = []
    for i, flows in enumerate(attempts):
        offset = i * stagger_days
        merged.extend(CashFlow(f.day + offset, f.amount, f.kind) for f in flows)
    return irr(merged, periods_per_year=periods_per_year)


def summarize_irr(
    attempts: Sequence[Sequence[CashFlow]],
    *,
    stagger_days: int = 0,
    periods_per_year: float = TRADING_DAYS_PER_YEAR,
) -> IRRSummary:
    """Per-attempt IRRs plus the portfolio IRR, with the undefined share reported."""
    results = [irr(f, periods_per_year=periods_per_year) for f in attempts]
    defined = [r.irr for r in results if r.defined]
    pf = portfolio_irr(attempts, stagger_days=stagger_days, periods_per_year=periods_per_year)
    net = [float(sum(x.amount for x in f)) for f in attempts]
    n = len(results)
    return IRRSummary(
        n_attempts=n,
        n_defined=len(defined),
        share_undefined=(1.0 - len(defined) / n) if n else float("nan"),
        median_irr_defined=float(np.median(defined)) if defined else float("nan"),
        mean_irr_defined=float(np.mean(defined)) if defined else float("nan"),
        portfolio_irr=pf.irr,
        portfolio_defined=pf.defined,
        portfolio_reason=pf.reason,
        mean_net_cash=float(np.mean(net)) if net else float("nan"),
    )


def attempt_cash_flows(
    *,
    pass_day: int | None,
    payout_days: Sequence[int],
    payout_amounts: Sequence[float],
    subscription: float,
    billing_days: int,
    activation: float,
    end_day: int,
    payout_lag_days: int = 0,
) -> list[CashFlow]:
    """Build one attempt's dated schedule from a simulated outcome.

    Args:
        pass_day: 0-based day the Combine passed, or None if it never did.
        payout_days: 0-based days payouts were *requested*, measured from the start of the
            funded account.
        payout_amounts: net cash per payout, after the profit split and any fee.
        subscription / billing_days / activation: fees, from the rules ledger.
        end_day: last day of the attempt (the Combine's fail day, or the funded horizon).
        payout_lag_days: trading days between requesting a payout and receiving the cash.
            **Unverified** (`payout_methods_and_fees` in config/rules.yaml). It shifts every
            inflow later and so lowers every IRR; leaving it at 0 is the optimistic
            assumption and must be stated wherever a result uses it.

    Payout days are given relative to the funded account's start and are shifted by
    `pass_day + 1` here, so the returned schedule is on the attempt's own clock.
    """
    flows: list[CashFlow] = []

    # Subscriptions at the start of days 0, billing_days, 2*billing_days, ... while running.
    last_sub_day = pass_day if pass_day is not None else end_day
    d = 0
    while d <= last_sub_day:
        flows.append(CashFlow(d, -abs(subscription), "subscription"))
        d += billing_days

    if pass_day is not None:
        flows.append(CashFlow(pass_day, -abs(activation), "activation"))
        base = pass_day + 1
        for day, amt in zip(payout_days, payout_amounts):
            if amt == 0:
                continue
            flows.append(CashFlow(base + int(day) + int(payout_lag_days), float(amt), "payout"))

    return sorted(flows, key=lambda f: f.day)
