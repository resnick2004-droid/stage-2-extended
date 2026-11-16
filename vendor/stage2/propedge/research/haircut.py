"""The program haircut (D-189): e's lower bound widened to one-sided confidence alpha/N, N the ledger's trial count
(`propedge.research.ledger`), with the deflated Sharpe ratio (Bailey & Lopez de Prado 2014) beside it.

* **The widened bound** is D-197's bound at level alpha/N: the lower of the day-clustered normal bound with
  z = Phi^-1(1 - alpha/N) and the moving-block bootstrap's. A percentile bootstrap cannot resolve a tail of alpha/N --
  it would need about fifty replicates in the tail, 50N/alpha in all -- so the widened bootstrap bound is the
  bootstrap's own standard error times the same z below the mean (`bootstrap_normal_bound`). At N = 1 the normal
  bound is D-197's exactly; the bootstrap half is the standard-error form of it, reported beside the percentile one.
* **The deflated Sharpe ratio** of the daily series the bound is built on (each day of the day set its trades' summed
  R, zero on a day without a trade): the probability that the true Sharpe ratio exceeds the expected maximum of N
  estimates under the null, SR0 = sqrt(V) x ((1 - g) Phi^-1(1 - 1/N) + g Phi^-1(1 - 1/(N e))), g the Euler-Mascheroni
  constant, with the estimate's skewness and kurtosis in the denominator. The trials' own Sharpe ratios are not
  observed -- most are other models on other statistics -- so V is the estimator's variance under the null, 1/(T - 1)
  (D-208). N = 1 gives SR0 = 0, the probabilistic Sharpe ratio against zero.

Reported beside a registered verdict, never replacing it, until a registration binds it (from P-05).
"""
from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np
from scipy.stats import kurtosis, norm, skew

EULER_GAMMA = 0.5772156649015329
ALPHA = 0.05


def bootstrap_means(day_sums: np.ndarray, day_counts: np.ndarray, *, block: int, reps: int, seed: int) -> np.ndarray:
    """The replicate means of the moving-block bootstrap of days -- `fv_score.block_lower_bound`'s resampling exactly
    (same seed, same draws), so its alpha quantile is that function's bound."""
    s, k = np.asarray(day_sums, float), np.asarray(day_counts, float)
    n = len(s)
    if n < 2 or k.sum() < 2:
        return np.full(0, np.nan)
    rng = np.random.default_rng(seed)
    nb = math.ceil(n / block)
    out = np.empty(reps)
    chunk = max(1, min(reps, 4_000_000 // max(n, 1)))
    for lo in range(0, reps, chunk):
        r = min(chunk, reps - lo)
        starts = rng.integers(0, max(n - block + 1, 1), size=(r, nb))
        idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(r, -1)[:, :n]
        idx = np.minimum(idx, n - 1)
        cnt = k[idx].sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[lo:lo + r] = np.where(cnt > 0, s[idx].sum(axis=1) / cnt, np.nan)
    return out


def bootstrap_normal_bound(mean: float, means: np.ndarray, z: float) -> float:
    """mean - z x the bootstrap replicates' standard deviation."""
    m = means[np.isfinite(means)]
    return float(mean - z * m.std(ddof=1)) if len(m) > 1 else float("nan")


def expected_max_sharpe(n_trials: int, variance: float) -> float:
    """Bailey & Lopez de Prado's expected maximum of `n_trials` Sharpe estimates with cross-trial `variance`, under
    the null; 0 for a single trial."""
    if n_trials < 2:
        return 0.0
    return float(math.sqrt(variance) * ((1 - EULER_GAMMA) * norm.ppf(1 - 1 / n_trials)
                                        + EULER_GAMMA * norm.ppf(1 - 1 / (n_trials * math.e))))


def deflated_sharpe(x: np.ndarray, n_trials: int) -> dict[str, float]:
    """The deflated Sharpe ratio of the series `x` (per period, not annualised) after `n_trials` trials."""
    x = np.asarray(x, float)
    t = len(x)
    if t < 3 or not np.isfinite(x).all() or x.std(ddof=1) == 0:
        return {"sr": float("nan"), "T": t, "skew": float("nan"), "kurt": float("nan"), "sr0": float("nan"),
                "dsr": float("nan")}
    sr = float(x.mean() / x.std(ddof=1))
    g3, g4 = float(skew(x)), float(kurtosis(x, fisher=False))
    sr0 = expected_max_sharpe(n_trials, 1.0 / (t - 1))
    denom = 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2
    dsr = float(norm.cdf((sr - sr0) * math.sqrt(t - 1) / math.sqrt(denom))) if denom > 0 else float("nan")
    return {"sr": sr, "T": t, "skew": g3, "kurt": g4, "sr0": sr0, "dsr": dsr}


def widened(r: np.ndarray, idx: np.ndarray, n_days: int, n_trials: int, *, block: int, reps: int, seed: int,
            alpha: float = ALPHA) -> dict[str, Any]:
    """D-189's widened bound for per-trade outcomes `r` on day positions `idx` of an `n_days` day set, with the
    daily series' deflated Sharpe ratio. The bootstrap's 95 % percentile bound is reported too, as the scorer has it."""
    from propedge.backtest.metrics import normal_lower_bound

    r, idx = np.asarray(r, float), np.asarray(idx, int)
    sums = np.bincount(idx, weights=r, minlength=n_days) if len(r) else np.zeros(n_days)
    counts = np.bincount(idx, minlength=n_days) if len(r) else np.zeros(n_days)
    level = alpha / max(int(n_trials), 1)
    z = float(norm.ppf(1 - level))
    means = bootstrap_means(sums, counts, block=block, reps=reps, seed=seed)
    e = float(r.mean()) if len(r) else float("nan")
    lb_boot95 = float(np.nanquantile(means, alpha)) if len(means) else float("nan")
    lb_boot_w = bootstrap_normal_bound(e, means, z)
    lb_norm_w = normal_lower_bound(r, idx, z=z) if len(r) > 1 else float("nan")
    finite = [x for x in (lb_boot_w, lb_norm_w) if np.isfinite(x)]
    return {"N": int(n_trials), "alpha_used": level, "z_used": z, "e": e, "entries": int(len(r)),
            "lb_bootstrap_95": lb_boot95, "lb_bootstrap_widened": lb_boot_w, "lb_normal_widened": lb_norm_w,
            "lb_widened": float(min(finite)) if finite else float("nan"),
            **{f"daily_{k}": v for k, v in deflated_sharpe(sums, n_trials).items()}}


def per_edge_rows(table, days: Sequence[str], n_trials: int, *, R_all: Sequence[int], scales: Sequence[str],
                  col: str = "v", seed: int, block: int, reps: int) -> list[dict[str, Any]]:
    """For an IM2-style entry table (`im2_score.entry_table`): per R and scale, `widened` on the outcomes the scorer's
    `edge` reads (every tradable entry with a walk at the scale, on the day set)."""
    pos = {d: i for i, d in enumerate(days)}
    rows = []
    for scale in scales:
        x = table[table[f"dist_{scale}"].notna() & table["d"].isin(days)]
        idx = x["d"].map(pos).to_numpy(int)
        for R in R_all:
            rows.append({"R": int(R), "scale": scale, "outcome": col,
                         **widened(x[f"{col}{R}_{scale}"].to_numpy(float), idx, len(days), n_trials, block=block,
                                   reps=reps, seed=seed)})
    return rows


__all__ = ["EULER_GAMMA", "ALPHA", "bootstrap_means", "bootstrap_normal_bound", "expected_max_sharpe",
           "deflated_sharpe", "widened", "per_edge_rows"]
