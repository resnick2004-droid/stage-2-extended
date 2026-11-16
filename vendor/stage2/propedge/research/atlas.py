"""Statistics for the effect atlas screen (D-126): Newey-West slope and mean tests, the Benjamini-
Hochberg false-discovery correction, a block-bootstrap check, calendar flags and the day filter.

Every definition follows `config/effect_atlas.yaml`, fixed before any bar was read.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

NW_LAGS = 5


def ols_nw(X: np.ndarray, y: np.ndarray, lags: int = NW_LAGS) -> tuple[np.ndarray, np.ndarray]:
    """OLS coefficients and Newey-West (Bartlett) standard errors."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n = len(y)
    xtx_inv = np.linalg.inv(X.T @ X)
    beta = xtx_inv @ X.T @ y
    u = y - X @ beta
    xu = X * u[:, None]
    S = xu.T @ xu
    for L in range(1, min(lags, n - 1) + 1):
        w = 1.0 - L / (lags + 1.0)
        G = xu[L:].T @ xu[:-L]
        S += w * (G + G.T)
    V = xtx_inv @ S @ xtx_inv
    return beta, np.sqrt(np.diag(V))


def _result(est, se, n, sd_x=None) -> dict:
    t = est / se if se > 0 else float("nan")
    p = float(2 * stats.norm.sf(abs(t))) if np.isfinite(t) else float("nan")
    return {"est": float(est), "se": float(se), "t": float(t), "p": p, "n": int(n),
            "size_pct": float(est * sd_x) if sd_x is not None else float(est)}


def slope_test(x, y) -> dict:
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 10:
        return {"est": float("nan"), "se": float("nan"), "t": float("nan"), "p": float("nan"), "n": len(x),
                "size_pct": float("nan")}
    b, se = ols_nw(np.column_stack([np.ones(len(x)), x]), y)
    return _result(b[1], se[1], len(x), sd_x=float(x.std(ddof=1)))


def mean_test(y) -> dict:
    y = np.asarray(y, float)
    y = y[np.isfinite(y)]
    if len(y) < 10:
        return {"est": float("nan"), "se": float("nan"), "t": float("nan"), "p": float("nan"), "n": len(y),
                "size_pct": float("nan")}
    b, se = ols_nw(np.ones((len(y), 1)), y)
    return _result(b[0], se[0], len(y))


#: D-129: a regime test with fewer days than this in either regime is reported as not computable
MIN_PER_REGIME = 10


def _nan_result(n) -> dict:
    return {"est": float("nan"), "se": float("nan"), "t": float("nan"), "p": float("nan"), "n": int(n),
            "size_pct": float("nan")}


def interaction_test(x, y, hi) -> dict:
    """Coefficient d in y = a + b x + c hi + d (x hi): the slope difference, high minus low regime."""
    x, y, hi = (np.asarray(v, float) for v in (x, y, hi))
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(hi)
    x, y, hi = x[ok], y[ok], hi[ok]
    n_hi = int((hi == 1).sum())
    if len(x) < 20 or min(n_hi, len(x) - n_hi) < MIN_PER_REGIME:
        return _nan_result(len(x))
    try:
        b, se = ols_nw(np.column_stack([np.ones(len(x)), x, hi, x * hi]), y)
    except np.linalg.LinAlgError:
        return _nan_result(len(x))
    return _result(b[3], se[3], len(x), sd_x=float(x.std(ddof=1)))


def partial_slope_test(x, z, y) -> dict:
    """Coefficient b in y = a + b x + c z (D-128's risk family): x's effect with the control z held fixed."""
    x, z, y = (np.asarray(v, float) for v in (x, z, y))
    ok = np.isfinite(x) & np.isfinite(z) & np.isfinite(y)
    x, z, y = x[ok], z[ok], y[ok]
    if len(x) < 20 or (np.unique(x).size == 2 and min((x == v).sum() for v in np.unique(x)) < MIN_PER_REGIME):
        return _nan_result(len(x))
    try:
        b, se = ols_nw(np.column_stack([np.ones(len(x)), x, z]), y)
    except np.linalg.LinAlgError:
        return _nan_result(len(x))
    return _result(b[1], se[1], len(x), sd_x=float(x.std(ddof=1)))


def block_bootstrap_p(fn, arrays: list[np.ndarray], *, block: int = 20, reps: int = 2000, seed: int) -> float:
    """Two-sided p that the statistic `fn(*arrays)` is zero, from a moving-block bootstrap of days."""
    n = len(arrays[0])
    if n < 2 * block:
        return float("nan")
    rng = np.random.default_rng(seed)
    k = math.ceil(n / block)
    vals = np.empty(reps)
    for r in range(reps):
        starts = rng.integers(0, n - block + 1, size=k)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]
        vals[r] = fn(*(a[idx] for a in arrays))
    vals = vals[np.isfinite(vals)]
    if not len(vals):
        return float("nan")
    return float(min(1.0, 2 * min((vals <= 0).mean(), (vals >= 0).mean())))


def benjamini_hochberg(p: np.ndarray, q: float) -> np.ndarray:
    """True where a p-value is a discovery at false-discovery rate q (NaN is never one)."""
    p = np.asarray(p, float)
    out = np.zeros(len(p), bool)
    ok = np.flatnonzero(np.isfinite(p))
    if not len(ok):
        return out
    order = ok[np.argsort(p[ok])]
    m = len(ok)
    thresh = q * np.arange(1, m + 1) / m
    passed = np.flatnonzero(p[order] <= thresh)
    if len(passed):
        out[order[: passed.max() + 1]] = True
    return out


def p_touch(on_abs, rvd) -> np.ndarray:
    """A driftless random walk's chance of touching a level |r_on| away within the day (sd = sqrt(rvd))."""
    on_abs, rvd = np.asarray(on_abs, float), np.asarray(rvd, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 2.0 * stats.norm.sf(on_abs / np.sqrt(rvd))


def calendar_flags(days: pd.DataFrame) -> pd.DataFrame:
    """Weekday, month ends, third Fridays and the next session, the roll window; from recorded dates."""
    d = days.sort_values("date").reset_index(drop=True).copy()
    d["weekday"] = d["date"].dt.day_name()
    ym = d["date"].dt.to_period("M")
    d["month_last"] = d["date"] == d.groupby(ym)["date"].transform("max")
    d["month_first"] = d["date"] == d.groupby(ym)["date"].transform("min")
    third_fri = (d["date"].dt.weekday == 4) & d["date"].dt.day.between(15, 21)
    d["third_friday"] = third_fri
    d["after_third_friday"] = third_fri.shift(1, fill_value=False)
    switch = d["sym"] != d["sym"].shift(1)
    switch.iloc[0] = False
    roll = np.zeros(len(d), bool)
    for i in np.flatnonzero(switch.to_numpy()):
        roll[max(0, i - 5):i] = True
    d["roll_window"] = roll
    return d


def scoreable(days: pd.DataFrame) -> pd.Series:
    """The declared day filter: no kit skip; settled; open bar; >= 90 % coverage; the reference is the
    previous recorded day and that day settled."""
    d = days.sort_values("date").reset_index(drop=True)
    num = lambda s: pd.to_numeric(s, errors="coerce")        # noqa: E731
    pst = np.where(num(d["pst"]).isna(), "", num(d["pst"]).fillna(0).astype("int64").astype(str))
    ds = d["date"].dt.strftime("%Y%m%d").to_numpy()
    prev_d = np.concatenate([[""], ds[:-1]])
    prev_st = np.concatenate([[0.0], d["st"].to_numpy()[:-1]])
    ok = ((d["sk"].fillna("").astype(str) == "").to_numpy() & (d["st"].to_numpy() == 1)
          & (d["op"].to_numpy() == 1) & (d["cov"].to_numpy() >= 0.9) & (pst == prev_d) & (prev_st == 1))
    return pd.Series(ok, index=d.index)
