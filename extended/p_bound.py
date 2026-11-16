"""Q-16 section 2: a calibrated bound for the user scorecard's P comparison -- a design's paired difference in P from
R* = P-14 over the judged block's start days -- reported BESIDE the trades-first pass line (E-008), never as it.

**The quantity** (Stage 2 D-627 (1)): a start's ahead average `A = (1[net_month_1 > 0] + 1[net_month_2 > 0] +
1[net_month_3 > 0]) / 3` over starts with at least 63 sessions observed; P is the mean of A; the paired series is
`d_t = A_design(t) - A_P14(t)` on the common start dates in date order; the judged block is the starts from 2024-01-02
(595 of them, to 2026-04-21: every family file's `judged` rows).

**The candidates** (`METHODS`):

| name | statistic | critical value |
|---|---|---|
| `d621` | Stage 2 D-621 (3)(i) as coded (`u_select.p_difference`): the `level` percentile of a non-circular moving-block bootstrap (63-start blocks, 2,000 draws, seed 20261700); holds when the difference and that limit are both above zero | -- (the reference; known not to hold its level, E-007 (1)) |
| `bm63`, `bm126` | Student-t on non-overlapping batch means (n // 63 = 9, n // 126 = 4 batches of consecutive starts) | t, df = batches - 1 |
| `obm63`, `obm126` | the mean with the overlapping-batch-means variance (batches of 63 / 126 starts; asymptotically Bartlett's HAC) | fixed-b: simulated for iid normal series of the same n and batch (seed `SEED`) |
| `ft63` | the mean with a flat-top (trapezoid) HAC variance: lags up to 63 starts weighted 1 (a start's month-3 window: no first-order bias from them), tapering linearly to 0 at 126 | fixed-b: simulated for iid normal series of the same n (seed `SEED`); a negative variance never rejects |
| `pcons` | the conservative fallback: carries only where `bm63`, `obm126` and `ft63` all carry; its limit is their minimum | -- |
| `bm63c` | `bm63`'s statistic | calibrated: at each level the largest (1 - level) quantile of bm63's t over the declared real and realistic nulls (the calibration's table, `load_bm63c_critical`); never read without that table |

**No conjunction of lines is offered.** The scorecard reads this one statistic beside the pass line; D-621 (3)'s other
lines ((ii) the guards, (iii) the gate, (iv) the coin, (4)(e) the year rule) are reported beside it, each on its own,
never AND-ed into a carry. (A conjunction with a calibrated line would only reject less often: its level is at most the
line's.)

**The choice** (`SHIPPED`) is in `docs/research/calibration_2026-11-15.md`, from `scripts/q16_calibrate.py --part p`.
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from extended import ROOT

#: the OBM critical values' simulation seed (Q-16's seeds, 20261910-20261919)
SEED = 20261919
#: Stage 2 D-621 (3)(i)'s bootstrap, as `u_select` and `user_journey` code it
STAGE2_BLOCK, STAGE2_DRAWS, STAGE2_SEED = 63, 2000, 20261700
JUDGED_FIRST = "2024-01-02"
HORIZON = 63
JOURNEY_FILE = ROOT / "vendor" / "stage2" / "results" / "user_journey.csv"
BUDGET_FILE = ROOT / "vendor" / "stage2" / "results" / "u_budget.csv"
#: the statistic the scorecard reads beside the pass line (chosen by the calibration, docs/research/
#: calibration_2026-11-15.md section 5.2): the conservative fallback, the only stand-alone candidate at or below its level
#: on every null -- with almost no power; RECOMMENDED holds its level on the declared nulls with usable power, but its
#: critical values are a calibration's table, to be pinned (a clean run and a decision row) before it is read
SHIPPED = "pcons"
RECOMMENDED = "bm63c"
METHODS = ("d621", "bm63", "bm126", "obm63", "obm126", "ft63", "pcons")
#: the flat-top kernel: weight 1 to FLAT lags, linear to 0 at TAPER
FLAT, TAPER = 63, 126


# ------------------------------------------------------------------------------------------------ the data


def load_starts(path: Path = JOURNEY_FILE, configs=("p14", "p16"), arms=("verdict", "point")) -> dict:
    """{(config, arm): the start days' ahead averages, a Series indexed by start date, in date order} from
    `user_journey.csv` section `start` (vendored, read-only)."""
    cols = ["section", "config", "arm", "start_date", "observed", "net_month_1", "net_month_2", "net_month_3"]
    d = pd.read_csv(path, usecols=cols, low_memory=False)
    d = d[(d["section"] == "start") & d["config"].isin(configs) & d["arm"].isin(arms)]
    return {(c, a): ahead_average(g) for (c, a), g in d.groupby(["config", "arm"])}


def ahead_average(st: pd.DataFrame) -> pd.Series:
    """Each eligible start's (observed >= 63 sessions) ahead average over months 1-3, indexed by its date, sorted."""
    s = st[pd.to_numeric(st["observed"]) >= HORIZON]
    a = sum((pd.to_numeric(s[f"net_month_{m}"]) > 0).astype(float) for m in (1, 2, 3)) / 3.0
    out = pd.Series(a.to_numpy(), index=s["start_date"].astype(str).to_numpy())
    return out.sort_index()


def judged(a: pd.Series) -> pd.Series:
    """The judged block's starts (from 2024-01-02)."""
    return a[a.index >= JUDGED_FIRST]


def paired(a: pd.Series, b: pd.Series) -> np.ndarray:
    """d = a - b on their common start dates, date order."""
    common = sorted(set(a.index) & set(b.index))
    return (a.loc[common] - b.loc[common]).to_numpy(float)


def registered_p14_judged(path: Path = BUDGET_FILE) -> float:
    """P-14's judged-block P as every family file records it (`u_budget.csv`, section `judged`, measure P)."""
    d = pd.read_csv(path, low_memory=False)
    v = pd.to_numeric(d[(d["section"] == "judged") & (d["measure"] == "P") & (d["reference"] == "p14")]
                      ["reference_value"]).unique()
    if len(v) != 1:
        raise ValueError(f"u_budget.csv holds {len(v)} judged reference values for P")
    return float(v[0])


def registered_paired_row(path: Path = JOURNEY_FILE) -> pd.Series:
    """`user_journey.csv` section `paired`: P-14 against P-16, verdict arm, `periodic` `share_positive` at 63 sessions,
    all starts (no year)."""
    cols = ["section", "config", "arm", "reference", "group", "measure", "at_days", "year", "n", "lo", "hi", "alpha",
            "block", "draws", "seed"]
    d = pd.read_csv(path, usecols=cols, low_memory=False)
    r = d[(d["section"] == "paired") & (d["config"] == "p14") & (d["arm"] == "verdict") & (d["reference"] == "p16")
          & (d["group"] == "periodic") & (d["measure"] == "share_positive")
          & (pd.to_numeric(d["at_days"]) == HORIZON) & d["year"].isna()]
    if len(r) != 1:
        raise ValueError(f"{len(r)} paired rows match")
    return r.iloc[0]


def paired_row_identity(starts=None, path: Path = JOURNEY_FILE) -> tuple[float, float, int]:
    """The registered paired row's interval re-derived: the share ahead at 63 sessions, P-14 minus P-16 (verdict),
    common eligible starts, the moving-block percentile interval at the row's alpha (Stage 2's bootstrap)."""
    cols = ["section", "config", "arm", "start_date", "observed", "net_month_3"]
    d = pd.read_csv(path, usecols=cols, low_memory=False)
    d = d[(d["section"] == "start") & (d["arm"] == "verdict") & (pd.to_numeric(d["observed"]) >= HORIZON)]
    x = d[d["config"] == "p14"].set_index("start_date")
    y = d[d["config"] == "p16"].set_index("start_date")
    common = sorted(set(x.index) & set(y.index))
    a = (pd.to_numeric(x.loc[common, "net_month_3"]) > 0).astype(float).to_numpy()
    b = (pd.to_numeric(y.loc[common, "net_month_3"]) > 0).astype(float).to_numpy()
    row = registered_paired_row(path)
    idx = stage2_block_indices(len(a), int(row["block"]), draws=int(row["draws"]), seed=int(row["seed"]))
    boot = a[idx].mean(axis=1) - b[idx].mean(axis=1)
    al = float(row["alpha"])
    return float(np.percentile(boot, 100 * al / 2)), float(np.percentile(boot, 100 * (1 - al / 2))), len(a)


# ------------------------------------------------------------------------------------------------ the statistics


def stage2_block_indices(n: int, block: int, *, draws: int = STAGE2_DRAWS, seed: int = STAGE2_SEED) -> np.ndarray:
    """`user_journey.block_indices`, line for line: `draws` rows of ceil(n / block) non-circular blocks laid end to end,
    each block's first start uniform on 0 .. n - block, cut to n."""
    n, b = int(n), int(block)
    rng = np.random.default_rng(int(seed))
    k = -(-n // b)
    first = rng.integers(0, n - b + 1, size=(int(draws), k))
    return (first[:, :, None] + np.arange(b)[None, None, :]).reshape(int(draws), k * b)[:, :n]


@lru_cache(maxsize=4)
def _stage2_weights(n: int) -> np.ndarray:
    idx = stage2_block_indices(n, STAGE2_BLOCK)
    W = np.zeros((STAGE2_DRAWS, n))
    for j in range(STAGE2_DRAWS):
        np.add.at(W[j], idx[j], 1.0)
    return W / n


def stage2_line(D, level: float):
    """(estimate, the line's lower limit) of D-621 (3)(i) per replication: the mean difference and the `level`
    percentile (numpy's linear interpolation, as coded) of the 2,000 moving-block resample means."""
    D = np.asarray(D, dtype=float)
    W = _stage2_weights(D.shape[0])
    boot = W @ D
    return D.mean(axis=0), np.percentile(boot, 100.0 * float(level), axis=0)


def _partition(n: int, batches: int) -> np.ndarray:
    return (np.arange(int(n)) * int(batches)) // int(n)


def batch_t(D, *, batches: int):
    """(estimate, se, df): the mean of the starts, the se from `batches` non-overlapping batch means of consecutive
    starts (sizes differing by at most one), df = batches - 1."""
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    bid = _partition(n, batches)
    starts = np.flatnonzero(np.r_[True, np.diff(bid) != 0])
    cnt = np.diff(np.r_[starts, n]).astype(float)
    shape = (-1,) + (1,) * (D.ndim - 1)
    m = np.add.reduceat(D, starts, axis=0) / cnt.reshape(shape)
    est = D.mean(axis=0)
    se = np.sqrt(((m - est) ** 2).sum(axis=0) / (batches - 1)) / math.sqrt(batches)
    return est, se, int(batches) - 1


def obm(D, m: int):
    """(estimate, se): the mean and the overlapping-batch-means standard error with batches of `m` starts
    (Meketon-Schmeiser: n m / ((n - m + 1)(n - m)) times the sum of squared batch-mean deviations, over n)."""
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    z = np.zeros((1,) + D.shape[1:])
    C = np.concatenate([z, np.cumsum(D, axis=0)], axis=0)
    B = (C[m:] - C[:-m]) / m
    est = C[-1] / n
    var = n * m / ((n - m + 1.0) * (n - m)) * ((B - est) ** 2).sum(axis=0)
    return est, np.sqrt(var / n)


@lru_cache(maxsize=None)
def _obm_null(n: int, m: int, seed: int = SEED) -> np.ndarray:
    """The sorted t = mean / se_OBM of 400,000 iid standard-normal series of length n (the fixed-b reference)."""
    rng = np.random.default_rng([int(seed), int(n), int(m)])
    out = []
    for _ in range(40):
        z = rng.standard_normal((int(n), 10_000))
        e, s = obm(z, int(m))
        out.append(e / s)
    return np.sort(np.concatenate(out))


def obm_critical(n: int, m: int, level: float, seed: int = SEED) -> float:
    """The (1 - level) quantile of the OBM t for iid normal series of length n (400,000 seeded draws, so at least
    50 / level for every level down to 1.25e-4)."""
    t = _obm_null(int(n), int(m), int(seed))
    if float(level) * len(t) < 50:
        raise ValueError(f"level {level} needs more than {len(t)} reference draws")
    return float(np.quantile(t, 1.0 - float(level)))


def flat_top(D, flat: int = FLAT, taper: int = TAPER):
    """(estimate, se): the mean and the flat-top HAC standard error -- autocovariances (divisor n) at lags 1..flat
    weighted 1, at flat < k < taper weighted (taper - k) / (taper - flat); NaN where the long-run variance is not
    positive."""
    D = np.asarray(D, dtype=float)
    one = D.ndim == 1
    X = D[:, None] if one else D
    n = X.shape[0]
    est = X.mean(axis=0)
    out = np.empty(X.shape[1])
    k = np.arange(1, int(taper))
    w = np.where(k <= flat, 1.0, (taper - k) / float(taper - flat))
    nf = 1 << int(math.ceil(math.log2(2 * n)))
    for i in range(0, X.shape[1], 4000):
        Y = X[:, i:i + 4000] - est[i:i + 4000]
        F = np.fft.rfft(Y, n=nf, axis=0)
        g = np.fft.irfft(F * np.conj(F), n=nf, axis=0)[: int(taper)] / n          # autocovariances, lags 0..taper-1
        out[i:i + 4000] = g[0] + 2.0 * (w[:, None] * g[1:]).sum(axis=0)
    with np.errstate(invalid="ignore"):
        se = np.where(out > 0, np.sqrt(np.maximum(out, 0.0) / n), np.nan)
    return (est[0], se[0]) if one else (est, se)


@lru_cache(maxsize=None)
def _ft_null(n: int, flat: int, taper: int, seed: int = SEED) -> np.ndarray:
    """The sorted t = mean / se_flat-top of 400,000 iid standard-normal series of length n (NaN se counted as never
    rejecting: t set to -inf)."""
    rng = np.random.default_rng([int(seed), int(n), int(flat), int(taper)])
    out = []
    for _ in range(40):
        z = rng.standard_normal((int(n), 10_000))
        e, s = flat_top(z, int(flat), int(taper))
        out.append(np.where(np.isfinite(s), e / s, -np.inf))
    return np.sort(np.concatenate(out))


def ft_critical(n: int, level: float, flat: int = FLAT, taper: int = TAPER, seed: int = SEED) -> float:
    t = _ft_null(int(n), int(flat), int(taper), int(seed))
    if float(level) * len(t) < 50:
        raise ValueError(f"level {level} needs more than {len(t)} reference draws")
    return float(np.quantile(t, 1.0 - float(level)))


def _parts(method: str, D, level: float):
    """(estimate, se, critical) per replication; `d621` returns (estimate, None, its lower limit)."""
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    if method == "d621":
        est, lo = stage2_line(D, level)
        return est, None, lo
    if method in ("bm63", "bm126"):
        est, se, df = batch_t(D, batches=n // int(method[2:]))
        return est, se, float(stats.t.ppf(1.0 - float(level), df))
    if method in ("obm63", "obm126"):
        m = int(method[3:])
        est, se = obm(D, m)
        return est, se, obm_critical(n, m, float(level))
    if method == "ft63":
        est, se = flat_top(D)
        return est, se, ft_critical(n, float(level))
    if method == "bm63c":
        raise ValueError("bm63c needs its calibrated table: bm63c_rejects(D, level=..., table=load_bm63c_critical(...))")
    raise ValueError(f"unknown method {method!r}; one of {METHODS}")


PCONS = ("bm63", "obm126", "ft63")


def _est_lower(method: str, D, level: float):
    if method == "pcons":
        parts = [_est_lower(m, D, level) for m in PCONS]
        return parts[0][0], np.minimum.reduce([np.where(np.isfinite(p[1]), p[1], -np.inf) for p in parts])
    est, se, c = _parts(method, D, level)
    lo = c if se is None else est - c * se
    return np.asarray(est), np.where(np.isfinite(lo), lo, -np.inf)


def many_levels(method: str, D, levels) -> tuple[np.ndarray, np.ndarray]:
    """(carries, minimum detectable differences), each (len(levels), reps): `rejects` and `mdd_draws` at several levels
    from one computation of the statistic (the calibration's form)."""
    levels = [float(a) for a in levels]
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    if method == "pcons":
        parts = [many_levels(m, D, levels) for m in PCONS]
        return np.logical_and.reduce([p[0] for p in parts]), np.maximum.reduce([p[1] for p in parts])
    if method == "d621":
        W = _stage2_weights(n)
        boot = W @ D
        est = D.mean(axis=0)
        lows = np.percentile(boot, [100.0 * a for a in levels], axis=0)
    else:
        if method in ("bm63", "bm126"):
            est, se, df = batch_t(D, batches=n // int(method[2:]))
            crit = [float(stats.t.ppf(1.0 - a, df)) for a in levels]
        elif method in ("obm63", "obm126"):
            est, se = obm(D, int(method[3:]))
            crit = [obm_critical(n, int(method[3:]), a) for a in levels]
        elif method == "ft63":
            est, se = flat_top(D)
            crit = [ft_critical(n, a) for a in levels]
        elif method == "bm63c":
            raise ValueError("bm63c needs its calibrated table: bm63c_rejects(D, level=..., table=load_bm63c_critical(...))")
        else:
            raise ValueError(f"unknown method {method!r}; one of {METHODS}")
        lows = np.asarray([est - c * se for c in crit])
    lows = np.where(np.isfinite(lows), lows, -np.inf)
    est = np.asarray(est)
    return (est > 0) & (lows > 0), np.maximum(-est, -lows)


def load_bm63c_critical(path) -> dict[float, float]:
    """`bm63c`'s critical values {level: c} from the calibration's table (`scripts/q16_calibrate.py --part p` writes
    `p_bm63c_critical.csv`; columns `level`, `critical`)."""
    t = pd.read_csv(path)
    return {float(a): float(c) for a, c in zip(t["level"], t["critical"])}


def bm63c_rejects(D, *, level: float, table: dict[float, float]):
    """`bm63c`: the batch-means t (n // 63 batches) against the calibrated critical value at `level` from `table`
    (a level the table does not hold is refused: KeyError)."""
    hit = [v for a, v in table.items() if abs(a - float(level)) <= 1e-12 * max(1.0, abs(a))]
    if not hit:
        raise KeyError(f"the bm63c table holds no critical value at level {level!r}")
    c = hit[0]
    D = np.asarray(D, dtype=float)
    est, se, _ = batch_t(D, batches=D.shape[0] // 63)
    return np.asarray((est > 0) & (est - c * se > 0))


def lower(method: str, D, *, level: float):
    """The one-sided lower limit at `level` per replication (-inf where the statistic cannot be read)."""
    return _est_lower(method, D, level)[1]


def rejects(method: str, D, *, level: float):
    """Whether `method` finds the design above R* at one-sided `level` (difference and lower limit above zero)."""
    est, lo = _est_lower(method, D, level)
    return np.asarray((est > 0) & (lo > 0))


def mdd_draws(method: str, D, *, level: float):
    """Per null replication, the smallest difference added to every start that `method` would carry (the estimate and
    every resample mean shift by it; se and the critical value do not); the 80 % MDD is their 80th percentile."""
    est, lo = _est_lower(method, D, level)
    return np.maximum(-est, -lo)


__all__ = ["SEED", "JUDGED_FIRST", "SHIPPED", "RECOMMENDED", "METHODS", "load_bm63c_critical", "bm63c_rejects", "load_starts", "ahead_average", "judged", "paired",
           "registered_p14_judged", "registered_paired_row", "paired_row_identity", "stage2_block_indices",
           "stage2_line", "batch_t", "obm", "obm_critical", "flat_top", "ft_critical", "lower", "rejects",
           "mdd_draws"]
