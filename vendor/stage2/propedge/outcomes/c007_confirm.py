"""The C-007 confirmation test: frozen forecast, pooled criterion, 2B's attached checks.

Written before any confirmation data exists and pinned by the pre-registration. Nothing here may
change once the test is registered; a change after that is a new pre-registration.

1. **The forecast is frozen.** The panel log-HAR (D-100's form) is fitted ONCE on every
   development day and its coefficients are applied unchanged to the confirmation window (Stage
   2B C-007: "estimated on development data only"). Lags at the start of the window come from
   the development evidence's last days, which are development data.
2. **The evidence** for each leg comes from two cloud parts that overlap by a few warm-up days;
   each part owns a fixed date range, the overlap is only compared, never used twice.
3. **The trade** is D-100's (`time_exit_sd.trades`): stop, size, the `assumed` fill profile.
4. **The verdict** is the pooled criterion (`metrics.criterion_test`, one test on a held-out
   window) AND each of C-007's pass/fail checks: at least 2 of 4 legs with a positive point
   estimate; the pooled criterion still met without the best leg; Cochran's Q homogeneity not
   rejected at 5 %. The per-leg lower bounds are reported, never claimed.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from scipy import stats

from propedge.backtest.metrics import criterion_test
from propedge.outcomes import time_exit_sd as tx

HOMOGENEITY_ALPHA = 0.05
MIN_POSITIVE_LEGS = 2


# ------------------------------------------------------------------ 1. the frozen forecast

def fit_frozen_har(dev: pd.DataFrame, *, lags=(1, 5, 22), min_fit: int = 60) -> dict:
    """One fit on all development rows with complete regressors. Returns the coefficients."""
    d = tx._har_design(dev, lags)
    xs = [f"x{L}" for L in lags]
    d = d[d[xs].notna().all(axis=1)]
    counts = d["market"].value_counts()
    short = sorted(m for m in d["market"].unique() if counts[m] < min_fit)
    if short:
        raise ValueError(f"fewer than {min_fit} development days to fit: {short}")
    markets = sorted(d["market"].unique())
    X = np.column_stack([(d["market"] == m).to_numpy(float) for m in markets] +
                        [d[x].to_numpy() for x in xs])
    beta, *_ = np.linalg.lstsq(X, d["y"].to_numpy(), rcond=None)
    resid = d["y"].to_numpy() - X @ beta
    s2 = float(resid @ resid) / (len(resid) - X.shape[1])
    return {"markets": markets, "lags": list(lags), "beta": [float(b) for b in beta], "s2": s2,
            "n_fit": int(len(d)), "last_fit_date": str(d["date"].max().date())}


def apply_frozen_har(panel: pd.DataFrame, fit: dict) -> pd.Series:
    """RV-hat for every row whose lags exist, from the frozen coefficients."""
    lags = fit["lags"]
    d = tx._har_design(panel, lags)
    xs = [f"x{L}" for L in lags]
    unknown = set(d["market"]) - set(fit["markets"])
    if unknown:
        raise ValueError(f"no fitted intercept for {sorted(unknown)}")
    X = np.column_stack([(d["market"] == m).to_numpy(float) for m in fit["markets"]] +
                        [d[x].to_numpy() for x in xs])
    rvhat = pd.Series(np.exp(X @ np.asarray(fit["beta"]) + fit["s2"] / 2.0), index=d.index)
    return rvhat.reindex(panel.index)


# ------------------------------------------------------------------ 2. the evidence

def assemble_parts(parts: list[tuple[pd.DataFrame, date, date]]) -> tuple[pd.DataFrame, dict]:
    """Join a leg's cloud parts; each keeps only the days it owns (inclusive dates).

    Returns the joined frame and an overlap report: days recorded by two parts, and how many of
    them disagree on any recorded field (the comparison is reported, never used to choose).
    """
    kept, frames = [], []
    for df, own_from, own_to in parts:
        d = pd.to_datetime(df["d"].astype(str))
        frames.append(df.assign(_date=d))
        kept.append(df[(d >= pd.Timestamp(own_from)) & (d <= pd.Timestamp(own_to))])
    out = pd.concat(kept, ignore_index=True)
    if out["d"].astype(str).duplicated().any():
        raise ValueError("owned date ranges overlap")
    fields = [c for c in ("e", "x", "h", "l", "dir", "rvw", "c") if c in out.columns]
    overlap, disagree = 0, 0
    for a, b in zip(frames, frames[1:]):
        both = a.merge(b, on="d", suffixes=("_a", "_b"))
        overlap += len(both)
        for f in fields:
            disagree += int((both[f + "_a"].astype(str) != both[f + "_b"].astype(str)).sum())
    return out.reset_index(drop=True), {"overlap_days": overlap, "overlap_field_mismatches": disagree}


# ------------------------------------------------------------------ 4. the verdict

def cochran_q(e: np.ndarray, se: np.ndarray) -> tuple[float, float]:
    """Cochran's Q across legs and its chi-square p-value (df = legs - 1)."""
    e, se = np.asarray(e, float), np.asarray(se, float)
    w = 1.0 / se ** 2
    pooled = float((w * e).sum() / w.sum())
    q = float((w * (e - pooled) ** 2).sum())
    return q, float(stats.chi2.sf(q, len(e) - 1))


def _criterion(t: pd.DataFrame, *, seed: int, k: int, replicates: int):
    days = pd.factorize(t["date"], sort=True)[0]
    return criterion_test(t["u"].to_numpy(), np.ones(len(t)), days, seed=seed, k=k,
                          has_confirmation_period=True, replicates=replicates)


def verdict(traded: pd.DataFrame, *, seed: int, k: int, replicates: int = 10_000) -> dict:
    """`traded`: one row per trade with `market`, `date`, `u`. The whole decision, in one place."""
    pooled = _criterion(traded, seed=seed, k=k, replicates=replicates)
    legs = {}
    for i, (m, g) in enumerate(sorted(traded.groupby("market"))):
        est = _criterion(g, seed=seed + 1 + i, k=k, replicates=replicates)
        legs[m] = {"n": est.estimate.n_trades, "e": est.estimate.edge,
                   "sd": est.estimate.sd_per_trade, "lower_bound": est.estimate.lower_bound}
    e = np.array([v["e"] for v in legs.values()])
    se = np.array([v["sd"] / np.sqrt(v["n"]) for v in legs.values()])
    q, p = cochran_q(e, se)
    best = max(legs, key=lambda m: legs[m]["e"])
    loo = _criterion(traded[traded["market"] != best], seed=seed + 10, k=k, replicates=replicates)
    checks = {
        "pooled_criterion": bool(pooled.passes),
        "min_positive_legs": bool((e > 0).sum() >= MIN_POSITIVE_LEGS),
        "leave_one_out": bool(loo.passes),
        "homogeneity": bool(p >= HOMOGENEITY_ALPHA),
    }
    return {"pooled": {"n": pooled.estimate.n_trades, "days": pooled.estimate.n_days,
                       "e": pooled.estimate.edge, "sd": pooled.estimate.sd_per_trade,
                       "lower_bound": pooled.estimate.lower_bound,
                       "lower_bound_bootstrap": pooled.estimate.lower_bound_bootstrap,
                       "lower_bound_normal": pooled.estimate.lower_bound_normal},
            "legs": legs, "best_leg": best,
            "leave_one_out": {"e": loo.estimate.edge, "lower_bound": loo.estimate.lower_bound},
            "cochran_q": q, "cochran_p": p, "checks": checks,
            "passes": all(checks.values())}
