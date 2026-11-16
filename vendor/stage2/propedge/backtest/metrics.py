"""Edge metrics and the pre-registered criterion.

The criterion, fixed by stage one (propsim D-47) and carried into this stage's charter:

    pursue a candidate only if  e >= 0.10  AND  the one-sided 95 % lower bound >= 0.05

where **e = mean P&L per trade / dollars risked per trade, net of costs**, measured out of
sample. Both halves must hold. A point estimate of 0.14 with a lower bound of 0.01 fails: it
says the strategy might be excellent and might be worthless, which is not a basis for putting
money on it.

Two interval methods are computed and **both** reported:

* **Bootstrap over days** (primary). Trades within a day are correlated, so the day is the
  independent unit. Resampling days preserves that correlation; resampling trades would
  understate the spread and inflate the lower bound -- in the optimistic direction, which is
  the one that matters.
* **Normal approximation** (secondary). Fast, and a check on the bootstrap. When the two
  disagree materially the sample is too small or too skewed for either to be trusted, and
  that disagreement is itself the finding.

The sample-size formula is stage one's (`vendor/propsim/edge/results_sample_size.csv`):

    n >= (1.645 * sd / (e / 2))^2

the trades needed for the one-sided 95 % lower bound to exceed half the true edge. At R = 1.5
and e = 0.10 that is ~1,667 trades -- 6.6 years at one trade a day. This is the constraint
that forces long historical tests (T2), and the reason a short live record cannot close this
stage.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
from scipy.stats import norm

Z_95_ONE_SIDED = 1.6448536269514722  # scipy.stats.norm.ppf(0.95)

#: The pre-registered criterion. Do not change these without a DECISIONS.md entry that
#: supersedes propsim D-47 -- moving a criterion after seeing results is the failure mode the
#: whole pre-registration discipline exists to prevent.
CRITERION_EDGE_MIN = 0.10
CRITERION_LOWER_BOUND_MIN = 0.05

#: Family-wise one-sided level for the criterion.
DEFAULT_ALPHA = 0.05


def bonferroni_z(k: int, alpha: float = 0.05) -> float:
    """One-sided z for `k` comparisons at family-wise `alpha`: `ppf(1 - alpha/k)`.

    Used when a variant is **selected** and then tested on the same data, with no held-out
    confirmation period. Selecting the best of `k` and reporting its unadjusted bound inflates
    the pass rate by roughly `k`; splitting `alpha` restores the family-wise level.

    `k = 1` returns `Z_95_ONE_SIDED` exactly, so the default path is unchanged.
    """
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    return float(norm.ppf(1.0 - alpha / k))


def z_for_alpha(alpha: float) -> float:
    """One-sided z at level `alpha`. `z_for_alpha(0.05) == Z_95_ONE_SIDED`."""
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    return float(norm.ppf(1.0 - alpha))


@dataclass(frozen=True)
class EdgeEstimate:
    """The edge, its intervals, and the criterion verdict."""

    edge: float
    sd_per_trade: float
    n_trades: int
    n_days: int
    lower_bound_bootstrap: float
    lower_bound_normal: float
    lower_bound: float          # the one used for decisions: the more conservative of the two
    bootstrap_replicates: int
    seed: int
    passes_criterion: bool
    criterion_edge_min: float = CRITERION_EDGE_MIN
    criterion_lower_bound_min: float = CRITERION_LOWER_BOUND_MIN
    alpha: float = DEFAULT_ALPHA
    z: float = Z_95_ONE_SIDED

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        verdict = "PASS" if self.passes_criterion else "FAIL"
        return (
            f"e = {self.edge:.4f}  (n = {self.n_trades} trades over {self.n_days} days, "
            f"sd = {self.sd_per_trade:.3f})\n"
            f"one-sided 95 % lower bound: bootstrap {self.lower_bound_bootstrap:.4f}, "
            f"normal {self.lower_bound_normal:.4f}  -> using {self.lower_bound:.4f}\n"
            f"criterion e >= {self.criterion_edge_min} and lower bound >= "
            f"{self.criterion_lower_bound_min}: {verdict}"
        )


def per_trade_returns(pnl: np.ndarray, risked: np.ndarray) -> np.ndarray:
    """P&L in units of risk, per trade. The quantity `e` is the mean of.

    Trades with non-positive risk are dropped: the ratio is undefined and keeping them as
    zeros would bias `e` toward zero.
    """
    pnl = np.asarray(pnl, dtype=float)
    risked = np.asarray(risked, dtype=float)
    if pnl.shape != risked.shape:
        raise ValueError(f"pnl shape {pnl.shape} != risked shape {risked.shape}")
    ok = risked > 0
    if not ok.all():
        pnl, risked = pnl[ok], risked[ok]
    return pnl / risked


def net_edge(pnl: np.ndarray, risked: np.ndarray) -> float:
    """e = mean P&L per trade / dollars risked per trade.

    Note this is the mean of the per-trade *ratios*, matching stage one's convention
    (`p_win = (1 + e) / (1 + R)` is a per-trade statement). With a constant dollar risk it
    coincides with `sum(pnl) / sum(risked)`; with varying risk it does not, and the per-trade
    mean is the one the criterion and the sample-size formula are written in.
    """
    r = per_trade_returns(pnl, risked)
    if len(r) == 0:
        return float("nan")
    return float(r.mean())


def bootstrap_lower_bound(
    returns: np.ndarray,
    days: np.ndarray,
    *,
    seed: int,
    replicates: int = 10_000,
    alpha: float = 0.05,
) -> float:
    """One-sided lower bound by resampling **days** with replacement.

    Args:
        returns: per-trade returns in units of risk.
        days: 0-based day index per trade (`propedge.outcomes.tradelog.day_index`).
        seed: explicit. Required.
        replicates: bootstrap replicates.
        alpha: 0.05 gives the 95 % one-sided lower bound.

    Returns the `alpha` quantile of the resampled means -- the percentile bootstrap. Each
    replicate resamples whole days, so a day's trades travel together and their correlation
    is preserved.
    """
    returns = np.asarray(returns, dtype=float)
    days = np.asarray(days, dtype=np.int64)
    if returns.shape != days.shape:
        raise ValueError("returns and days must be the same length")
    if len(returns) == 0:
        return float("nan")

    uniq = np.unique(days)
    n_days = len(uniq)
    if n_days < 2:
        return float("nan")

    # Per-day sums and counts; a resampled mean is sum(sums) / sum(counts).
    order = np.argsort(days, kind="stable")
    sorted_days, sorted_ret = days[order], returns[order]
    starts = np.searchsorted(sorted_days, uniq, side="left")
    ends = np.searchsorted(sorted_days, uniq, side="right")
    day_sums = np.add.reduceat(sorted_ret, starts) if len(sorted_ret) else np.zeros(0)
    day_counts = (ends - starts).astype(float)

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n_days, size=(replicates, n_days))
    sums = day_sums[idx].sum(axis=1)
    counts = day_counts[idx].sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        means = np.where(counts > 0, sums / counts, np.nan)
    return float(np.nanquantile(means, alpha))


def normal_lower_bound(
    returns: np.ndarray, days: np.ndarray | None = None, *, z: float = Z_95_ONE_SIDED
) -> float:
    """One-sided lower bound from the normal approximation: `mean - z * se`.

    If `days` is given, the standard error is computed on **daily means** and scaled to the
    per-trade mean, so intra-day correlation is not ignored. Without `days` it is the naive
    per-trade standard error, which is optimistic whenever a day holds more than one trade.

    `z` defaults to the single-test one-sided 95 % value. Pass `bonferroni_z(k)` when a variant
    was selected from `k` candidates with no held-out confirmation period.
    """
    returns = np.asarray(returns, dtype=float)
    n = len(returns)
    if n < 2:
        return float("nan")
    mean = returns.mean()

    if days is None:
        se = returns.std(ddof=1) / np.sqrt(n)
        return float(mean - z * se)

    days = np.asarray(days, dtype=np.int64)
    uniq = np.unique(days)
    if len(uniq) < 2:
        return float("nan")
    day_means = np.array([returns[days == d].mean() for d in uniq])
    se = day_means.std(ddof=1) / np.sqrt(len(uniq))
    return float(mean - z * se)


def sample_size_required(
    edge: float,
    sd: float,
    *,
    fraction: float = 0.5,
    z: float = Z_95_ONE_SIDED,
    cluster_factor: float = 1.0,
) -> float:
    """Trades needed for the one-sided lower bound to exceed `fraction` x the true edge.

    Stage one's formula generalised:

        n >= cluster_factor * (z * sd / (e * fraction))^2

    At the defaults (`z = 1.645`, `cluster_factor = 1.0`) this is exactly stage one's
    `n >= (1.645 * sd / (e/2))^2` and reproduces
    `vendor/propsim/edge/results_sample_size.csv` — see `tests/test_metrics.py`.

    Args:
        edge: the true (or hypothesised) edge, in units of risk.
        sd: per-trade standard deviation in units of risk. **Supply the pre-registered value
            with its source.** Stage one's 1.23-1.79 is the frictionless binary floor
            `(1 + R) * sqrt(p(1-p))` and understates a real log, which also carries flattened
            trades, gapped stops and varying realised risk.
        fraction: how far above zero the bound must sit, as a share of the edge.
        z: one-sided critical value. Pass `bonferroni_z(k)` when a variant was selected from
            `k` candidates with no held-out confirmation period. The requirement scales with
            `z^2`, so `k = 10` costs about 2.5x the trades.
        cluster_factor: the ratio of nominal to effective sample size. Trades within a day are
            correlated, so the effective sample size is `n / cluster_factor`; a day of `m`
            perfectly correlated trades has `cluster_factor = m`. 1.0 treats every trade as
            independent, which is what stage one's table assumes and which understates the
            requirement whenever a day holds more than one trade.

    All three of `sd`, `z` and `cluster_factor` move the answer **up** from stage one's
    published figures. Those figures are a floor, not the requirement.
    """
    if edge <= 0:
        return float("inf")
    if sd <= 0:
        raise ValueError(f"sd must be positive, got {sd}")
    if cluster_factor <= 0:
        raise ValueError(f"cluster_factor must be positive, got {cluster_factor}")
    return float(cluster_factor * (z * sd / (edge * fraction)) ** 2)


def binary_sd(rr: float, edge: float = 0.0) -> float:
    """Per-trade sd in units of risk for a clean binary bracket: `(1 + R) * sqrt(p(1-p))`."""
    p = (1.0 + edge) / (1.0 + rr)
    if not 0.0 < p < 1.0:
        raise ValueError(f"p_win={p} out of range for rr={rr}, edge={edge}")
    return float((1.0 + rr) * np.sqrt(p * (1.0 - p)))


def meets_criterion(edge: float, lower_bound: float) -> bool:
    """The pre-registered criterion: `e >= 0.10` **and** `lower bound >= 0.05`.

    NaN fails. An estimate that could not be computed is not a pass.
    """
    if not np.isfinite(edge) or not np.isfinite(lower_bound):
        return False
    return bool(edge >= CRITERION_EDGE_MIN and lower_bound >= CRITERION_LOWER_BOUND_MIN)


def estimate_edge(
    pnl: np.ndarray,
    risked: np.ndarray,
    days: np.ndarray,
    *,
    seed: int,
    replicates: int = 10_000,
    alpha: float = DEFAULT_ALPHA,
) -> EdgeEstimate:
    """The full estimate: edge, both lower bounds, and the criterion verdict.

    `lower_bound` -- the one decisions use -- is the **more conservative** of the bootstrap
    and normal bounds. Taking the more favourable of two methods after seeing both is
    choosing a result, which D-04 and the working discipline forbid.

    Args:
        pnl: net P&L per trade, in dollars.
        risked: dollars risked per trade.
        days: 0-based day index per trade.
        seed: explicit. Required -- the bootstrap is random.
        replicates: bootstrap replicates.
        alpha: one-sided level for **both** bounds. The default 0.05 gives
            `z = Z_95_ONE_SIDED` exactly, so the default path is unchanged. A single `alpha`
            rather than a separate `z` means the bootstrap quantile and the normal critical
            value cannot drift apart; pass `alpha / k` for a Bonferroni-adjusted bound, or use
            `criterion_test`, which does that for you.
    """
    returns = per_trade_returns(pnl, risked)
    ok = np.asarray(risked, dtype=float) > 0
    days_ok = np.asarray(days, dtype=np.int64)[ok] if len(ok) == len(days) else np.asarray(days)

    z = z_for_alpha(alpha)
    e = float(returns.mean()) if len(returns) else float("nan")
    sd = float(returns.std(ddof=1)) if len(returns) > 1 else float("nan")
    lb_boot = bootstrap_lower_bound(
        returns, days_ok, seed=seed, replicates=replicates, alpha=alpha
    )
    lb_norm = normal_lower_bound(returns, days_ok, z=z)

    finite = [x for x in (lb_boot, lb_norm) if np.isfinite(x)]
    lb = min(finite) if finite else float("nan")

    return EdgeEstimate(
        edge=e,
        sd_per_trade=sd,
        n_trades=int(len(returns)),
        n_days=int(len(np.unique(days_ok))) if len(days_ok) else 0,
        lower_bound_bootstrap=lb_boot,
        lower_bound_normal=lb_norm,
        lower_bound=lb,
        bootstrap_replicates=replicates,
        seed=int(seed),
        passes_criterion=meets_criterion(e, lb),
        alpha=float(alpha),
        z=z,
    )


@dataclass(frozen=True)
class CriterionVerdict:
    """The criterion applied under an explicit multiplicity plan.

    Attributes:
        estimate: the adjusted estimate whose `lower_bound` the verdict rests on.
        k: how many variants were declared in advance.
        has_confirmation_period: True if the log supplied is a **held-out confirmation**
            period never used in development.
        alpha_family / alpha_used: the family-wise level and the level actually applied.
        z_used: the critical value applied.
        passes: the decision-bearing verdict.
        is_exploratory: True when the verdict cannot be treated as confirmatory.
        reason: why, in words fit for a report.
        unadjusted: the unadjusted estimate, present only when it differs. Reporting *its*
            bound on a selected variant is exploratory by D-13, so it is carried separately
            and never used for `passes`.
    """

    estimate: EdgeEstimate
    k: int
    has_confirmation_period: bool
    alpha_family: float
    alpha_used: float
    z_used: float
    passes: bool
    is_exploratory: bool
    reason: str
    unadjusted: EdgeEstimate | None = None

    @property
    def edge(self) -> float:
        return self.estimate.edge

    @property
    def lower_bound(self) -> float:
        return self.estimate.lower_bound

    def summary(self) -> str:
        head = "PASS" if self.passes else "FAIL"
        if self.is_exploratory:
            head += " (EXPLORATORY -- not a confirmatory result)"
        lines = [
            f"criterion: {head}",
            f"  e = {self.estimate.edge:.4f}, one-sided lower bound "
            f"{self.estimate.lower_bound:.4f} at alpha {self.alpha_used:g} "
            f"(z = {self.z_used:.4f})",
            f"  k = {self.k} declared in advance; held-out confirmation period: "
            f"{'yes' if self.has_confirmation_period else 'NO'}",
            f"  thresholds: e >= {CRITERION_EDGE_MIN}, bound >= {CRITERION_LOWER_BOUND_MIN}",
            f"  {self.reason}",
        ]
        if self.unadjusted is not None:
            lines.append(
                f"  unadjusted bound (EXPLORATORY, not decision-bearing): "
                f"{self.unadjusted.lower_bound:.4f}"
            )
        return "\n".join(lines)


def criterion_test(
    pnl: np.ndarray,
    risked: np.ndarray,
    days: np.ndarray,
    *,
    seed: int,
    k: int = 1,
    has_confirmation_period: bool = True,
    alpha: float = DEFAULT_ALPHA,
    replicates: int = 10_000,
) -> CriterionVerdict:
    """Apply the criterion to a **confirmation-period** trade log under a multiplicity plan.

    The plan this implements:

    * **With a held-out confirmation period** (`has_confirmation_period=True`): selection
      happened on a development period, the single selected variant is tested **once** here,
      so this is one test and `alpha` is not split however large `k` was. This is the intended
      route, and the only one that yields a confirmatory verdict.
    * **Without one** (`has_confirmation_period=False`): the variant was selected on the same
      data it is now judged on, so the level is split -- Bonferroni at one-sided `alpha / k`.
      The unadjusted bound is computed too, carried on `unadjusted`, and marked exploratory;
      it is never used for `passes`.

    Args:
        pnl, risked, days: the confirmation-period trade log.
        seed: explicit. Required.
        k: variants declared in advance. Must be >= 1. `k = 1` with no confirmation period is
          a single pre-registered test and needs no adjustment.
        has_confirmation_period: whether this log is a held-out confirmation period.
        alpha: family-wise one-sided level.
        replicates: bootstrap replicates.

    Raises:
        ValueError: `k < 1`.
    """
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")

    if has_confirmation_period:
        alpha_used = alpha
        reason = (
            f"single test on a held-out confirmation period; selection over k = {k} happened "
            "on the development period, so the level is not split"
        )
        exploratory = False
        unadjusted = None
    elif k == 1:
        alpha_used = alpha
        reason = (
            "no held-out confirmation period, but k = 1: a single pre-registered test needs "
            "no multiplicity adjustment"
        )
        exploratory = False
        unadjusted = None
    else:
        alpha_used = alpha / k
        reason = (
            f"no held-out confirmation period and k = {k}: Bonferroni at one-sided "
            f"{alpha:g}/{k} = {alpha_used:g}. The unadjusted bound on a selected variant is "
            "exploratory and is reported separately, never as the verdict"
        )
        exploratory = False
        unadjusted = estimate_edge(
            pnl, risked, days, seed=seed, replicates=replicates, alpha=alpha
        )

    estimate = estimate_edge(
        pnl, risked, days, seed=seed, replicates=replicates, alpha=alpha_used
    )

    return CriterionVerdict(
        estimate=estimate,
        k=int(k),
        has_confirmation_period=bool(has_confirmation_period),
        alpha_family=float(alpha),
        alpha_used=float(alpha_used),
        z_used=z_for_alpha(alpha_used),
        passes=estimate.passes_criterion,
        is_exploratory=exploratory,
        reason=reason,
        unadjusted=unadjusted,
    )
