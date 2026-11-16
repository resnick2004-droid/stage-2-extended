"""FV3-S (T22): the account-state tables valued by the certainty equivalent under exponential utility.

FV3-C's tables (`state_policy.FundedDP`, `CombineDP`) value a state by the expected cash still to come, less a rent per
slot-day. Here each day's mixture of outcomes -- the rungs (by their shares), the days an R is not offered (the stay),
the win and the loss -- is valued at its certainty equivalent

    CE = -(1/a) log sum_i w_i exp(-a V_i)

with aversion a per dollar (a = 0: the expectation, the parent's own code path to the bit). Exponential utility is the
one risk-averse objective under which a sure payment passes through unchanged (CE[x + c] = CE[x] + c), so the day
loop stays exact: the payout choice at a close, the abandon action (worth 0), the rules, the tie-breaks and the
rent work as in the parent. The aversion is declared by what it means in dollars (`aversion_for`): the a at which a
fair coin to win or lose `stake` is worth -`loss`.
"""
from __future__ import annotations

import math

import numpy as np

from propedge.campaign import state_policy as sp


def _log_cosh(x: float) -> float:
    x = abs(float(x))
    return x + math.log1p(math.exp(-2.0 * x)) - math.log(2.0)


def coin_ce(a: float, stake: float = 1000.0) -> float:
    """The certainty equivalent of a fair coin to win or lose `stake` at aversion `a` (negative for a > 0)."""
    if a <= 0.0:
        return 0.0
    return -_log_cosh(a * stake) / a


def aversion_for(loss: float, stake: float = 1000.0, tol: float = 1e-12) -> float:
    """The aversion a at which a fair coin to win or lose `stake` is worth -`loss` (0 < loss < stake): bisection on
    `coin_ce`, which falls from 0 toward -stake as a grows."""
    loss, stake = float(loss), float(stake)
    if not 0.0 < loss < stake:
        raise ValueError("the coin's certainty-equivalent loss lies strictly between 0 and the stake")
    lo, hi = 0.0, 1.0 / stake
    while -coin_ce(hi, stake) < loss:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if -coin_ce(mid, stake) < loss:
            lo = mid
        else:
            hi = mid
        if hi - lo <= tol * hi:
            break
    return 0.5 * (lo + hi)


def certainty_equivalent(values: np.ndarray, weights: np.ndarray, a: float) -> np.ndarray:
    """Per column, -(1/a) log sum_i w_i exp(-a V_i) over the rows with positive weight, shifted by the column's least
    value so no exponent overflows; the weights of each column sum to one."""
    V = np.asarray(values, float)
    W = np.asarray(weights, float)
    pos = W > 0.0
    m = np.where(pos, V, np.inf).min(axis=0)
    m = np.where(np.isfinite(m), m, 0.0)
    e = np.where(pos, np.exp(-float(a) * np.where(pos, V - m, 0.0)), 0.0)
    s = (W * e).sum(axis=0)
    return m - np.log(s) / float(a)


class _CertaintyEquivalent:
    """The day's action value by its certainty equivalent: the parent's mixture (`_DP._action_value`) taken over
    exp(-a (V - m)) instead of V, then -(1/a) log of it plus m. The exponentials are computed once a day -- the close
    values `ext` are one array for every action of the day -- shifted by the day's least value m, so no exponent
    overflows and none underflows to zero (a fraction of a dollar's aversion times the table's span of values)."""

    aversion: float = 0.0
    _ce_day: tuple | None = None

    def _ce_exp(self, ext: np.ndarray) -> tuple[float, np.ndarray, np.ndarray | None]:
        day = self._ce_day
        if day is None or day[0] is not ext:
            m = float(np.min(ext))
            E = np.exp(-self.aversion * (ext - m))
            day = (ext, m, E, None if self.stay is None else np.take(E, self.stay))
            self._ce_day = day
        return day[1], day[2], day[3]

    def _action_value(self, a: int, ext: np.ndarray, ext_stay: np.ndarray | None, daily: float) -> np.ndarray:
        if self.aversion <= 0.0:
            return super()._action_value(a, ext, ext_stay, daily)          # type: ignore[misc]
        if a == self.abandon_action:                                     # D-329: the slot freed, worth nothing
            return np.zeros(self.nS)
        m, E, E_stay = self._ce_exp(ext)
        iw, il, p = self.trans[a]
        A = None if self.avail is None else self.avail[a]
        s = np.zeros(self.nS)
        for k in range(self.nR):
            x = p[k] * np.take(E, iw[k]) + (1.0 - p[k]) * np.take(E, il[k])
            if A is not None and A[k] < 1.0:                             # D-318: the R not offered today -- no trade
                x = A[k] * x + (1.0 - A[k]) * E_stay
            s += self.w[k] * x
        return m - np.log(s) / self.aversion - daily

    def solve(self, *args, **kwargs):
        self._ce_day = None
        try:
            return super().solve(*args, **kwargs)                        # type: ignore[misc]
        finally:
            self._ce_day = None


class FundedCE(_CertaintyEquivalent, sp.FundedDP):
    """The XFA's table under exponential utility at `aversion` (0: `FundedDP` exactly)."""

    def __init__(self, *args, aversion: float = 0.0, **kwargs):
        if float(aversion) < 0.0:
            raise ValueError("the aversion is a non-negative number per dollar")
        self.aversion = float(aversion)
        super().__init__(*args, **kwargs)


class CombineCE(_CertaintyEquivalent, sp.CombineDP):
    """The Combine's table under exponential utility at `aversion` (0: `CombineDP` exactly); its pass is worth the
    XFA's certainty equivalent less the activation, as the caller passes it."""

    def __init__(self, *args, aversion: float = 0.0, **kwargs):
        if float(aversion) < 0.0:
            raise ValueError("the aversion is a non-negative number per dollar")
        self.aversion = float(aversion)
        super().__init__(*args, **kwargs)


__all__ = ["coin_ce", "aversion_for", "certainty_equivalent", "FundedCE", "CombineCE"]
