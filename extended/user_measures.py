"""Q-17 (E-007 (e); the operator's scope of 2026-11-15): the measures read beside every user reading -- pure functions on
a start's records, numpy only (no engine, no draw; safe to import in any process).

A *start* is U1's unit (Stage 2 D-620, `vendor/stage2/propedge/research/user_journey.py`): one development trading day
as a fresh start, the design's trades replayed in historical order; day 0 the purchase evening, day k the k-th
session's close, a month 21 sessions. `rel[k]` is the cash at close k less the starting bankroll -- the cumulative net
cash (payouts received less every fee paid; the bankroll never binds).

E-007 (e)'s extra measures:

* **P by month** (`p_by_month`): the shares of starts ahead at months 1, 2 and 3 and their mean P, on the starts
  holding all three nets -- U1's / D-621's P (`u_select.p_of`: the months ahead summed over three a start), except that
  **ahead is a net above `TOL`** (`docs/MEASURES.md` 1.2, m-11; Wave 3.1): a path whose payouts equal its fees is not
  ahead by float residue. Stage 2's card (`u_select`, `> 0`) is read beside under Stage 2's tolerance.
  With `spent` and `limit`: **P under a bankroll limit** -- a start counts as ahead at a month only if its `spent` at
  that month is at most the limit. MEASURES.md section 2's `P_B` passes **the peak out-of-pocket through each month
  close** (`peak_by_month`); its named sub-reading "before the first payout" passes U1's
  `spent_before_first_payout` (Q-17's reading). The user who quits keeps no payout (the replay's own path, not a
  re-run with a wallet).
* **CVaR10** (`cvar`): the mean of the worst ceil(0.10 n) values.
* **n_eff** (`n_eff_bartlett`): n times the series' variance over its Bartlett-tapered long-run variance at lag L --
  the effective number of independent starts behind a mean over consecutive start days (the Phase 0 audit B's
  estimator, `docs/audits/phase0/B_objective.md`). A description, not a calibrated test (TASK_QUEUE Q-16 owns that).

The operator's path measures (the journey as a collective of variables, not one lump sum):

* **Break-even** (`break_even_day`): the first close k >= 1 with `rel[k]` at or above zero (to the millionth of a
  dollar, as U1's fee arithmetic); whether a start that broke even later closes below zero (`fell_back`); the deepest
  fall of `rel` from its running high from the break-even close on (`deepest_fall_after`). Daily resolution: the
  replay's own close-by-close cash (`CampaignPath.cash_series`).
* **Evenness over months 1-12** (`evenness`): the share of months whose net change is positive (month 1's from zero),
  the longest run of months without a payout arriving, the standard deviation of the monthly net changes (ddof 1),
  payouts per month (count and dollars), and the largest single month's share of the twelve months' payout dollars
  (the lump-sum detector; blank with no payout). A payout belongs to the month its cash arrives in: sessions
  21 (m - 1) + 1 .. 21 m are month m.

Distributions over starts (`quantiles`, `days_quantile`): numpy's linear percentiles. For days to an event within a
window W, **the headline is the censored form** (`days_quantile(..., censored=True)`, `censored_days`; MEASURES.md 1.3):
an unreached start is censored at W + 1, and the percentile is never blank (W + 1 reads "beyond the window"). Stage 2's
form -- an unreached start beyond (`BEYOND`) and a percentile beyond the window blank (U1's
`customer_journey._days_q`, D-518 (3)) -- is the default, kept beside.

The peak out-of-pocket (Wave 3.1; MEASURES.md 1.2, B-2): `peak_through(rel, k)` is the deepest the net goes below zero
over closes 0 .. k, `peak_by_month(rel)` that through each month close 21 m (m = 1 .. 12) inside the observed closes.
`spent_before(rel, k)` is U1's `customer_journey.spent_before`: over the closes before k.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Sequence

import numpy as np

MONTH = 21
MONTHS = 12
P_MONTHS = (1, 2, 3)
#: a net "at or above zero" to the millionth of a dollar (U1's `fees_paid` rounds to it)
TOL = 1e-6
#: an unreached start in Stage 2's days percentile (beyond any window); the censored form uses W + 1 instead
BEYOND = 1e9
#: the operator's percentiles of every distribution over starts
PERCENTILES = (10, 50, 90)
NAN = float("nan")


# ------------------------------------------------------------------------------------------------ P and the money


def p_by_month(nets: np.ndarray, *, spent: np.ndarray | None = None, limit: float | None = None) -> dict[str, Any]:
    """The shares ahead (a net above `TOL`) at months 1, 2, 3 and P on the starts holding all three nets. `nets`:
    (n, 3), each start's net at months 1, 2, 3 (as U1's reading at that month reads it). With `spent` (n, 3: what each
    month's reading holds against the limit -- the peak out-of-pocket through the month close for `P_B`, the cash spent
    before the first payout for its sub-reading) and `limit`: a start is ahead at a month only within the limit
    (spending exactly the limit is within it)."""
    x = np.asarray(nets, float).reshape(-1, len(P_MONTHS))
    ok = np.isfinite(x).all(axis=1)
    ahead = x[ok] > TOL
    if limit is not None:
        if spent is None:
            raise ValueError("a bankroll limit needs the spending each month's reading holds against it")
        s = np.asarray(spent, float).reshape(-1, len(P_MONTHS))[ok]
        if (ahead & ~np.isfinite(s)).any():
            raise ValueError("a start ahead has no spending before its first payout: the record is inconsistent")
        ahead = ahead & (np.where(np.isfinite(s), s, np.inf) <= float(limit))
    n = int(ok.sum())
    out: dict[str, Any] = {f"share_month_{m}": (float(ahead[:, i].mean()) if n else NAN) for i, m in enumerate(P_MONTHS)}
    out["P"] = float(ahead.sum() / (len(P_MONTHS) * n)) if n else NAN
    out["n"] = n
    return out


def months_ahead(nets: np.ndarray) -> np.ndarray:
    """Each start's months ahead (a net above `TOL`, as `p_by_month`) among 1, 2, 3 (0 .. 3); blank where a net is
    missing."""
    x = np.asarray(nets, float).reshape(-1, len(P_MONTHS))
    c = (x > TOL).sum(axis=1).astype(float)
    return np.where(np.isfinite(x).all(axis=1), c, NAN)


def share_over_limit(spent: np.ndarray, limit: float) -> float:
    """The share of starts (with a finite spending before a first payout) that spent more than `limit` before it."""
    s = np.asarray(spent, float)
    s = s[np.isfinite(s)]
    return float((s > float(limit)).mean()) if len(s) else NAN


def cvar(x: np.ndarray, q: float = 0.10) -> float:
    """The mean of the worst ceil(q n) finite values (the lower tail's expectation)."""
    v = np.sort(np.asarray(x, float)[np.isfinite(np.asarray(x, float))])
    if not len(v):
        return NAN
    k = max(1, int(math.ceil(float(q) * len(v) - 1e-12)))
    return float(v[:k].mean())


def n_eff_bartlett(x: np.ndarray, lag: int = 63) -> float:
    """n times the variance over the Bartlett-tapered long-run variance at `lag` (weights 1 - k / (lag + 1)); the
    series in start order, blanks dropped. Blank for a constant series or a non-positive long-run variance."""
    v = np.asarray(x, float)
    v = v[np.isfinite(v)]
    n = len(v)
    if n < 2:
        return NAN
    d = v - v.mean()
    g0 = float(d @ d) / n
    if g0 <= 0:
        return NAN
    lrv = g0
    for k in range(1, min(int(lag), n - 1) + 1):
        lrv += 2.0 * (1.0 - k / (int(lag) + 1.0)) * float(d[:-k] @ d[k:]) / n
    return float(n * g0 / lrv) if lrv > 0 else NAN


# ------------------------------------------------------------------------------------------------ the daily path


def break_even_day(rel: np.ndarray) -> float:
    """The first close k >= 1 whose cumulative net is at or above zero; blank if none."""
    r = np.asarray(rel, float)
    hit = np.nonzero(r[1:] >= -TOL)[0]
    return float(hit[0] + 1) if len(hit) else NAN


def fell_back(rel: np.ndarray, be: float) -> bool | None:
    """Whether a close after the break-even close is below zero; None when there was no break-even."""
    if not np.isfinite(be):
        return None
    r = np.asarray(rel, float)
    return bool((r[int(be) + 1:] < -TOL).any())


def deepest_fall_after(rel: np.ndarray, be: float) -> float:
    """The deepest fall of the cumulative net from its running high, from the break-even close on; blank without one."""
    if not np.isfinite(be):
        return NAN
    r = np.asarray(rel, float)[int(be):]
    return float((np.maximum.accumulate(r) - r).max())


def daily(rel: np.ndarray) -> dict[str, Any]:
    """A start's daily path measures from its closes `rel[0 .. observed]`."""
    be = break_even_day(rel)
    fb = fell_back(rel, be)
    return {"break_even_day": be, "fell_back": NAN if fb is None else float(fb),
            "deepest_fall_after_break_even": deepest_fall_after(rel, be)}


# ------------------------------------------------------------------------------------------------ evenness


def month_of(day: int) -> int:
    """The month a session belongs to: sessions 1 .. 21 are month 1 (day 0, the purchase evening, has no payout)."""
    return (int(day) - 1) // MONTH + 1


def evenness(net_month: Sequence[float], payouts: Iterable[tuple[int, float]]) -> dict[str, Any]:
    """A start's evenness over months 1-12 from its twelve month-end nets and its payouts' (arrival day, cash)."""
    nets = np.asarray(net_month, float)
    if len(nets) != MONTHS or not np.isfinite(nets).all():
        raise ValueError("evenness reads a start with all twelve month-end nets")
    ch = np.diff(np.concatenate([[0.0], nets]))
    count = np.zeros(MONTHS)
    cash = np.zeros(MONTHS)
    for d, c in payouts:
        m = month_of(int(d))
        if 1 <= m <= MONTHS:
            count[m - 1] += 1
            cash[m - 1] += float(c)
    run = best = 0
    for k in count:
        run = run + 1 if k == 0 else 0
        best = max(best, run)
    total = float(cash.sum())
    return {"share_months_positive": float((ch > 0).mean()), "longest_months_without_payout": int(best),
            "sd_monthly_net": float(ch.std(ddof=1)), "payouts_per_month": float(count.sum() / MONTHS),
            "payout_cash_per_month": total / MONTHS,
            "largest_month_share": float(cash.max() / total) if total > 0 else NAN}


# ------------------------------------------------------------------------------------------------ distributions


def quantiles(x: np.ndarray, pcts: Sequence[int] = PERCENTILES) -> dict[str, Any]:
    """numpy's linear percentiles of the finite values, and their count."""
    v = np.asarray(x, float)
    v = v[np.isfinite(v)]
    out: dict[str, Any] = {f"p{p}": (float(np.percentile(v, p)) if len(v) else NAN) for p in pcts}
    out["n"] = int(len(v))
    return out


def censored_days(first: np.ndarray, window: int) -> np.ndarray:
    """Each start's days to an event within `window` in the censored form (MEASURES.md 1.3): the day where it came by
    the window's close, else (blank, or past the window) `window + 1`, "beyond"."""
    f = np.asarray(first, float)
    return np.where(np.isfinite(f) & (f <= int(window)), f, float(int(window) + 1))


def days_quantile(first: np.ndarray, window: int, p: float, *, censored: bool = False) -> float:
    """A percentile of the days to an event over starts observed `window` sessions. Stage 2's form (the default, kept
    beside): an unreached start (blank, or past the window) beyond; blank when the percentile falls beyond the window
    (U1's `_days_q`). `censored=True`, the headline (MEASURES.md 1.3): an unreached start at `window + 1`
    (`censored_days`), the percentile never blank on a non-empty set; `window + 1` reads "beyond the window"."""
    if censored:
        v = censored_days(first, window)
        return float(np.percentile(v, p)) if len(v) else NAN
    f = np.asarray(first, float)
    v = np.where(np.isfinite(f) & (f <= int(window)), f, BEYOND)
    if not len(v):
        return NAN
    q = float(np.percentile(v, p))
    return q if q <= int(window) else NAN


# ------------------------------------------------------------------------------------------------ the peak out of pocket


def spent_before(rel: np.ndarray, k: int) -> float:
    """U1's `customer_journey.spent_before`: the deepest net below zero over the closes before close `k`,
    `max(0, -min rel[0 .. k - 1])` (0 when there are none)."""
    r = np.asarray(rel, float)
    k = int(k)
    if k < 0 or k > len(r):
        raise ValueError(f"close {k} is outside the {len(r)} closes held")
    return float(max(0.0, -float(np.min(r[:k])))) if k > 0 else 0.0


def peak_through(rel: np.ndarray, k: int) -> float:
    """The peak out-of-pocket through close `k` (MEASURES.md 1.2): `max(0, -min rel[0 .. k])`, close k included."""
    r = np.asarray(rel, float)
    k = int(k)
    if k < 0 or k >= len(r):
        raise ValueError(f"close {k} is not among the {len(r)} closes held")
    return float(max(0.0, -float(np.min(r[:k + 1]))))


def peak_by_month(rel: np.ndarray) -> list[float]:
    """The peak out-of-pocket through each month close 21 m, m = 1 .. 12, from the closes held (blank where the
    month's close is not held). Wave 3.1's field (MEASURES.md section 6, B-2): `P_B` and (24)'s peak form pass it."""
    r = np.asarray(rel, float)
    return [peak_through(r, MONTH * m) if MONTH * m < len(r) else NAN for m in range(1, MONTHS + 1)]


__all__ = ["MONTH", "MONTHS", "P_MONTHS", "TOL", "PERCENTILES", "p_by_month", "months_ahead", "share_over_limit", "cvar",
           "n_eff_bartlett", "break_even_day", "fell_back", "deepest_fall_after", "daily", "month_of", "evenness",
           "quantiles", "days_quantile", "censored_days", "spent_before", "peak_through", "peak_by_month", "BEYOND"]
