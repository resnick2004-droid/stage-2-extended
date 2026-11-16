"""Q-16 (E-008): the one-sided bound on a design's lift over its coin twin -- the trades-first pass line's statistic --
and the candidates it was chosen from, all on the same session aggregates.

**The quantity.** Per trade `i` the pair difference `x_i = (outcome(rule side) - outcome(mirror)) / 2` at the same
bracket (in win probability: `x` in {-1/2, 0, 1/2}; in net R beside). The lift is its mean per trade over the judged
block (2024-01-02 to 2026-07-16). The pass line needs its one-sided lower bound at the family's level
`0.05 / (k (k + 1))` (k = 11 to 15 next) above zero.

**The unit of dependence is the session.** Trades are first summed per session of the judged block's calendar --
`S_j` (the sum of `x` over the session's trades) and `N_j` (their count), every session counted, an empty one with
`S_j = N_j = 0` -- and every statistic here is a function of `(S, N)`. Sessions are then cut into `G = n // b` blocks of
`b` or `b + 1` consecutive sessions (`block_index`: session `j` is in block `floor(j G / n)`), so a block is a fixed
stretch of the calendar, never a count of trades.

**The candidates** (method names as `rejects` takes them):

| name | statistic | critical value |
|---|---|---|
| `t21e` | Student-t on 21-session block means, each non-empty block weighted equally (F-01's stage C form) | t, df = blocks - 1 |
| `t21w`, `t42w`, `t63w` | the per-trade mean (sum over count) with a cluster-robust variance on b-session blocks (CR1: G / (G - 1)) | t, df = G - 1 |
| `hac21` | the per-trade mean; its variance a Bartlett-weighted sum over 21-session blocks and their neighbours up to 2 blocks away | fixed-b: simulated for iid normal blocks of equal weight at the same G and bandwidth |
| `cbb21` | the studentised circular block bootstrap: 21-session blocks, the resample's own CR1 variance, centred | the resample's (1 - level) quantile of t*; draws at least 20 / level |
| `cons` | the conservative fallback: rejects only where `t21w`, `t42w` and `t63w` all reject; its bound is their minimum | -- |

**The choice** (`SHIPPED`) and why are in `docs/research/calibration_2026-11-15.md`, from `scripts/q16_calibrate.py`.

Every random draw takes an explicit seed (the bootstrap's resample matrix and the fixed-b table's simulation); the
seeds are this item's (20261910-20261919): `FIXED_B_SEED`, `BOOT_SEED`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy import stats

#: the next families' numbers (E-007 (a): F-01 spent k = 10)
K_RANGE = (11, 12, 13, 14, 15)
#: F-01's block (stage C): 21 sessions, a trading month
BLOCK = 21
#: the fixed-b critical values' simulation seed, and the default seed of the bootstrap's resample matrix (Q-16 seeds)
FIXED_B_SEED = 20261913
BOOT_SEED = 20261914
#: the statistic the pass line uses -- chosen by the calibration (docs/research/calibration_2026-11-15.md)
SHIPPED = "t21w"

METHODS = ("t21e", "t21w", "t42w", "t63w", "hac21", "cbb21", "cons")


def family_level(k: int) -> float:
    """The one-sided level of family number `k` (CHARTER section 3): 0.05 / (k (k + 1))."""
    return 0.05 / (int(k) * (int(k) + 1))


def clopper_pearson(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    """The exact (Clopper-Pearson) two-sided interval for a binomial proportion k / n."""
    a = (1.0 - float(conf)) / 2.0
    lo = 0.0 if k <= 0 else float(stats.beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k >= n else float(stats.beta.ppf(1.0 - a, k + 1, n - k))
    return lo, hi


# ------------------------------------------------------------------------------------------------ aggregates


def session_sums(x, session, n_sessions: int) -> tuple[np.ndarray, np.ndarray]:
    """(S, N): per session of the calendar `0 .. n_sessions - 1`, the sum of the trades' `x` and their count. A trade's
    `session` is its session's ordinal in the judged block's calendar (every trading session counted, with or without a
    trade)."""
    x = np.asarray(x, dtype=float)
    s = np.asarray(session)
    if x.shape != s.shape or x.ndim != 1:
        raise ValueError("x and session must be one-dimensional and of the same length")
    if not np.issubdtype(s.dtype, np.integer):
        raise ValueError("session must be integer ordinals")
    if len(s) and (s.min() < 0 or s.max() >= int(n_sessions)):
        raise ValueError(f"a session ordinal is outside the calendar 0..{int(n_sessions) - 1}")
    if not np.all(np.isfinite(x)):
        raise ValueError("x holds a NaN or an infinity")
    S = np.bincount(s, weights=x, minlength=int(n_sessions)).astype(float)
    N = np.bincount(s, minlength=int(n_sessions)).astype(float)
    return S, N


def block_index(n_sessions: int, block: int) -> tuple[np.ndarray, int]:
    """(each session's block, the number of blocks G = n // block): G consecutive blocks of `block` or `block + 1`
    sessions covering the whole calendar."""
    n = int(n_sessions)
    G = max(1, n // int(block))
    return (np.arange(n) * G) // n, G


def _block_sums(S, N, block: int):
    S = np.asarray(S, dtype=float)
    N = np.asarray(N, dtype=float)
    bid, G = block_index(S.shape[0], block)
    starts = np.flatnonzero(np.r_[True, np.diff(bid) != 0])
    return np.add.reduceat(S, starts, axis=0), np.add.reduceat(N, starts, axis=0), G


# ------------------------------------------------------------------------------------------------ the t family


def t_stats(S, N, *, block: int = BLOCK, weight: str = "trades"):
    """(estimate, standard error, df) of the lift from session sums -- vectorised: `S`, `N` of shape (n,) or
    (n, replications). `weight='equal'`: the mean of the non-empty blocks' means, se = their sd / sqrt(G'), df = G' - 1.
    `weight='trades'`: the per-trade mean sum(S) / sum(N), se from the residual block sums u_g = BS_g - est BN_g with
    CR1's G' / (G' - 1), df = G' - 1 (G' the non-empty blocks)."""
    BS, BN, _ = _block_sums(S, N, block)
    with np.errstate(invalid="ignore", divide="ignore"):
        if weight == "equal":
            ok = BN > 0
            m = np.where(ok, BS / np.where(ok, BN, 1.0), np.nan)
            Gp = ok.sum(axis=0)
            est = np.nanmean(m, axis=0) if m.ndim > 1 else (np.nanmean(m) if Gp else np.nan)
            sd = np.sqrt(np.nansum((m - est) ** 2, axis=0) / (Gp - 1))
            se = sd / np.sqrt(Gp)
        elif weight == "trades":
            tot = BN.sum(axis=0)
            est = BS.sum(axis=0) / tot
            u = BS - est * BN
            Gp = (BN > 0).sum(axis=0)
            se = np.sqrt(Gp / (Gp - 1) * (u ** 2).sum(axis=0)) / tot
        else:
            raise ValueError(f"weight is 'equal' or 'trades', not {weight!r}")
    df = Gp - 1
    return est, se, df


def hac_stats(S, N, *, block: int = BLOCK, lags: int = 2):
    """(estimate, standard error, G) of the per-trade lift with a Bartlett-weighted variance over the residual block
    sums and their neighbours up to `lags` blocks away (empty blocks kept in order, their residual zero); no small-G
    factor -- the fixed-b critical value carries it."""
    BS, BN, G = _block_sums(S, N, block)
    with np.errstate(invalid="ignore", divide="ignore"):
        tot = BN.sum(axis=0)
        est = BS.sum(axis=0) / tot
        u = BS - est * BN
        lrv = (u ** 2).sum(axis=0)
        for L in range(1, int(lags) + 1):
            lrv = lrv + 2.0 * (1.0 - L / (lags + 1.0)) * (u[L:] * u[:-L]).sum(axis=0)
        se = np.sqrt(np.maximum(lrv, 0.0)) / tot
    return est, se, G


@lru_cache(maxsize=None)
def fixed_b_critical(G: int, lags: int, level: float, seed: int = FIXED_B_SEED) -> float:
    """The (1 - level) quantile of `hac_stats`' t for G iid standard-normal blocks of equal weight (the fixed-b
    reference), from max(200,000, 50 / level) seeded draws -- exact for iid normal blocks, by simulation."""
    reps = int(max(200_000, math.ceil(50.0 / float(level))))
    rng = np.random.default_rng(int(seed) + 1000 * int(G) + int(lags))
    out = []
    for i in range(0, reps, 50_000):
        z = rng.standard_normal((int(G), min(50_000, reps - i)))
        est, se, _ = hac_stats(z, np.ones_like(z), block=1, lags=int(lags))
        out.append(est / se)
    t = np.concatenate(out)
    return float(np.quantile(t, 1.0 - float(level)))


# ------------------------------------------------------------------------------------------------ the bootstrap


def draws_for(level: float) -> int:
    """At least 20 / level bootstrap draws (so the tail quantile is read inside the draws, never interpolated past the
    last one), in thousands, at least 2,000."""
    return int(max(2000, math.ceil(20.0 / float(level) / 1000.0) * 1000))


def _circular(S, N, block: int):
    """Each circular start's block sums of S and N (n starts)."""
    S = np.asarray(S, dtype=float)
    N = np.asarray(N, dtype=float)
    n = S.shape[0]
    idx = (np.arange(n)[:, None] + np.arange(int(block))[None, :]) % n
    return S[idx].sum(axis=1), N[idx].sum(axis=1)


@lru_cache(maxsize=8)
def _resample_counts(n: int, G: int, draws: int, seed: int):
    """The bootstrap's resample matrix as a sparse (draws x n) count matrix: each draw picks G circular block starts."""
    from scipy import sparse

    rng = np.random.default_rng(int(seed))
    starts = rng.integers(0, int(n), size=(int(draws), int(G)))
    rows = np.repeat(np.arange(int(draws)), int(G))
    return sparse.csr_matrix((np.ones(starts.size), (rows, starts.ravel())), shape=(int(draws), int(n)))


def cbb_tstar(S, N, *, block: int = BLOCK, draws: int, seed: int = BOOT_SEED) -> np.ndarray:
    """The studentised circular block bootstrap's t* = (est* - est) / se* for one sample's session sums (or for many,
    `S`, `N` of shape (n, reps): returned (draws, reps)): each draw takes G = n // block circular blocks of `block`
    sessions; est* the resample's per-trade mean, se* its CR1 standard error on its own G blocks. Centred: each session
    enters the circular blocks equally, so the resamples' centre is the sample's estimate."""
    S = np.asarray(S, dtype=float)
    N = np.asarray(N, dtype=float)
    one = S.ndim == 1
    if one:
        S, N = S[:, None], N[:, None]
    n = S.shape[0]
    _, G = block_index(n, block)
    C = _resample_counts(n, G, int(draws), int(seed))
    CS, CN = _circular(S, N, block)
    Q = np.concatenate([CS, CN, CS * CS, CS * CN, CN * CN], axis=1)          # (n, 5 reps)
    R = S.shape[1]
    M = np.asarray(C @ Q)                                                      # (draws, 5 reps)
    sS, sN, sSS, sSN, sNN = (M[:, i * R:(i + 1) * R] for i in range(5))
    est = S.sum(axis=0) / N.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        th = sS / sN
        var = G / (G - 1.0) * (sSS - 2.0 * th * sSN + th * th * sNN) / (sN * sN)
        t = (th - est[None, :]) / np.sqrt(np.maximum(var, 0.0))
    return t[:, 0] if one else t


def cbb_critical(S, N, *, level: float, block: int = BLOCK, draws: int | None = None, seed: int = BOOT_SEED):
    """The bootstrap's critical value(s): the (1 - level) quantile of t*, NaN draws dropped (a resample with no trade)."""
    d = draws_for(level) if draws is None else int(draws)
    t = cbb_tstar(S, N, block=block, draws=d, seed=seed)
    return np.nanquantile(t, 1.0 - float(level), axis=0, method="higher")


def cbb_crit_many(S, N, *, levels, block: int = BLOCK, draws: int, seed: int = BOOT_SEED) -> np.ndarray:
    """(len(levels), reps): the bootstrap's critical values at several levels from one set of draws (calibration)."""
    t = cbb_tstar(S, N, block=block, draws=draws, seed=seed)
    t = np.where(np.isfinite(t), t, -np.inf)                                   # a failed resample never sets the tail
    out = []
    for a in levels:
        k = int(math.ceil(float(a) * t.shape[0]))                              # the k-th largest t*
        out.append(-np.partition(-t, k - 1, axis=0)[k - 1])
    return np.vstack(out)


# ------------------------------------------------------------------------------------------------ the decisions


@dataclass(frozen=True)
class Bound:
    """One statistic's reading on one sample."""
    method: str
    estimate: float
    se: float
    critical: float
    lower: float
    level: float
    df: float
    blocks: int
    trades: int
    draws: int = 0

    @property
    def rejects(self) -> bool:
        """The pass line's test: the one-sided lower bound above zero."""
        return bool(np.isfinite(self.lower) and self.lower > 0.0)


def _parts(method: str, S, N, level: float, *, seed: int = BOOT_SEED, draws: int | None = None):
    """(estimate, se, critical) for `method` (vectorised over replications)."""
    if method in ("t21e", "t21w", "t42w", "t63w"):
        b = int(method[1:3])
        est, se, df = t_stats(S, N, block=b, weight="equal" if method.endswith("e") else "trades")
        with np.errstate(invalid="ignore"):
            crit = np.where(df >= 1, stats.t.ppf(1.0 - level, np.maximum(df, 1)), np.nan)
        return est, se, crit
    if method == "hac21":
        est, se, G = hac_stats(S, N, block=21, lags=2)
        return est, se, np.full(np.shape(est), fixed_b_critical(int(G), 2, float(level)))
    if method == "cbb21":
        est, se, _ = t_stats(S, N, block=21, weight="trades")
        return est, se, cbb_critical(S, N, level=level, block=21, draws=draws, seed=seed)
    raise ValueError(f"unknown method {method!r}; one of {METHODS}")


def rejects(method: str, S, N, *, level: float, seed: int = BOOT_SEED, draws: int | None = None):
    """Whether `method` rejects a zero lift at one-sided `level` (the lower bound above zero), per replication."""
    if method == "cons":
        out = None
        for m in ("t21w", "t42w", "t63w"):
            r = rejects(m, S, N, level=level)
            out = r if out is None else (out & r)
        return out
    est, se, crit = _parts(method, S, N, level, seed=seed, draws=draws)
    with np.errstate(invalid="ignore"):
        return np.asarray((est - crit * se) > 0.0) & np.isfinite(se) & (np.asarray(se) > 0)


def mdl_draws(method: str, S, N, *, level: float, seed: int = BOOT_SEED, draws: int | None = None):
    """Per null replication, the smallest lift added to every trade that `method` rejects: crit x se - estimate (the
    estimate shifts by the lift, the se and the critical value do not). Power at a lift d is the share of replications
    whose value is below d; the 80 % minimum detectable lift is their 80th percentile."""
    if method == "cons":
        return np.maximum.reduce([mdl_draws(m, S, N, level=level) for m in ("t21w", "t42w", "t63w")])
    est, se, crit = _parts(method, S, N, level, seed=seed, draws=draws)
    with np.errstate(invalid="ignore"):
        return np.where(np.isfinite(se) & (np.asarray(se) > 0), crit * se - est, np.inf)


def bound(method: str, x, session, n_sessions: int, *, level: float, seed: int = BOOT_SEED) -> Bound:
    """One sample's reading by `method`: the trades' pair differences `x` and their sessions' ordinals."""
    S, N = session_sums(x, session, n_sessions)
    if method == "cons":
        parts = [bound(m, x, session, n_sessions, level=level) for m in ("t21w", "t42w", "t63w")]
        low = min(parts, key=lambda p: p.lower if np.isfinite(p.lower) else -np.inf)
        return Bound("cons", low.estimate, low.se, low.critical, low.lower, float(level), low.df, low.blocks,
                     low.trades)
    est, se, crit = _parts(method, S, N, float(level), seed=seed)
    b = 21 if method in ("hac21", "cbb21") else int(method[1:3])
    BS, BN, G = _block_sums(S, N, b)
    if method in ("t21e", "t21w", "t42w", "t63w"):
        df = float(t_stats(S, N, block=b, weight="equal" if method.endswith("e") else "trades")[2])
    else:
        df = float("nan")
    est, se, crit = float(est), float(se), float(crit)
    return Bound(method, est, se, crit, est - crit * se, float(level), df, int((BN > 0).sum()), int(N.sum()),
                 draws_for(level) if method == "cbb21" else 0)


def t_block(x, session, n_sessions: int, *, level: float, block: int = BLOCK, weight: str = "trades") -> Bound:
    """The Student-t bound on `block`-session blocks (`weight` 'equal': F-01's block means; 'trades': per trade)."""
    if block not in (21, 42, 63):
        S, N = session_sums(x, session, n_sessions)
        est, se, df = t_stats(S, N, block=block, weight=weight)
        crit = float(stats.t.ppf(1.0 - level, df))
        BS, BN, _ = _block_sums(S, N, block)
        return Bound(f"t{block}{'e' if weight == 'equal' else 'w'}", float(est), float(se), crit,
                     float(est) - crit * float(se), float(level), float(df), int((BN > 0).sum()), int(N.sum()))
    return bound(f"t{block}{'e' if weight == 'equal' else 'w'}", x, session, n_sessions, level=level)


def cbb_t(x, session, n_sessions: int, *, level: float, block: int = BLOCK, seed: int = BOOT_SEED) -> Bound:
    """The studentised circular block bootstrap's bound (draws at least 20 / level)."""
    if block != 21:
        raise ValueError("the bootstrap candidate is declared at 21-session blocks")
    return bound("cbb21", x, session, n_sessions, level=level, seed=seed)


__all__ = ["K_RANGE", "BLOCK", "SHIPPED", "METHODS", "FIXED_B_SEED", "BOOT_SEED", "family_level", "clopper_pearson",
           "session_sums", "block_index", "t_stats", "hac_stats", "fixed_b_critical", "draws_for", "cbb_tstar",
           "cbb_critical", "cbb_crit_many", "Bound", "rejects", "mdl_draws", "bound", "t_block", "cbb_t"]
