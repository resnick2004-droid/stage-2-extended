"""Q-82 (E-052; the red team's M1, `docs/reviews/PASS_LINE_CODE_2026-11-16.md`): **count-persistent nulls** -- the
number of trades a session takes persists across sessions -- drawn without reading any outcome, for the pass line's
fresh-seed validation (`scripts/q82_validation.py`).

**Why.** Q-16's nulls hold each session's trade count fixed (P-16's streams; its `thinN` subsets, drawn once) or draw it
iid across sessions (the synthetic Poisson and negative-binomial counts). When a few stretches of the block carry most
of the trades, the trade-weighted mean is mostly those stretches and the session-cluster t's effective number of
clusters falls below its df; the red team found `cons` reaching or exceeding its level there on synthetic nulls. These
generators let the counts persist.

**The intensity profiles** (`PROFILES`, the note's M1 parameters): a multiplier `m[j, r]` per session `j` of the block and
replication `r`, mean one:

| name | profile |
|---|---|
| `flat` | 1: a fresh uniform thinning every replication (the reference; Q-16's `thinN` were one fixed subset) |
| `trend2x`, `trend3x` | the rate rises linearly across the block, the last session's 2 or 3 times the first's, normalised to mean 1 |
| `ar98s07`, `ar98s10`, `ar98s15`, `ar995s10` | log-intensity AR(1) across sessions, `phi` 0.98 or 0.995, stationary sd 0.7, 1.0 or 1.5, started stationary; `m = exp(h - sd^2 / 2)` |
| `burst10x` | one 63-session quarter at a uniformly random phase at 10 times the rest's rate, normalised to mean 1 within each replication |

**Thinning a real stream (outcome-independent by construction).** Every offer of session `j` is kept independently with
probability `min(1, c m[j, r])`, `c = target / offers`, so the expected count is the target (less where the cap binds).
The draws that decide how many trades a session keeps -- the intensity and the binomial counts `K ~ Binomial(M_j,
min(1, c m))` -- take the sessions' offer counts and the rates only; no function here that draws them is given an
outcome, and a caller draws them (and any side flips) **before** anything that reads an outcome, so a session's kept
count is the same, draw for draw, whatever the outcomes are (`tests/test_count_nulls.py` asserts it). The kept set is
then a uniform `K`-subset of the session's offers -- for outcomes taking a few values, drawn exactly as a multivariate
hypergeometric on the session's category counts (`subset_sums`, which also draws disjoint subsets in turn: C1''s level
and placebo fills); for a continuous outcome, offer by offer (`bernoulli_keep`, which never sees an outcome either).

**The synthetic nulls** (`synthetic_counts`, `cluster_sums`, `cluster_two_sample`): the red team's Appendix A exactly --
counts with mean `m` a session (`iid` and `burst10x` negative binomial of size 1 given the rate, the trend and AR
profiles Poisson given it); each trade `1/2 sign(a_j + e)`, `a_j` the session effect (Q-16's `cluster`, icc 0.35), so the
null is exact and sides reset daily; the two-sample form shares the profile and the day's effect between its level
(`m1`) and placebo (`5 m1`) trades.

Every function that draws takes the generator (`numpy.random.Generator`) from its caller; the seeds are the caller's
(Q-82's map in `scripts/q82_validation.py`, E-052's block 20262010-20262019).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

#: the intensity profiles (the red team's M1 parameters)
PROFILES: dict[str, dict] = {
    "flat": {"kind": "flat"},
    "trend2x": {"kind": "trend", "ratio": 2.0},
    "trend3x": {"kind": "trend", "ratio": 3.0},
    "ar98s07": {"kind": "ar", "phi": 0.98, "sd": 0.7},
    "ar98s10": {"kind": "ar", "phi": 0.98, "sd": 1.0},
    "ar98s15": {"kind": "ar", "phi": 0.98, "sd": 1.5},
    "ar995s10": {"kind": "ar", "phi": 0.995, "sd": 1.0},
    "burst10x": {"kind": "burst", "length": 63, "factor": 10.0},
}
#: the synthetic count models: Q-16's iid negative binomial (the reference) and the profiles above
SYNTHETIC_PROFILES = ("iid",) + tuple(p for p in PROFILES if p != "flat")
#: Q-16's `cluster`: the latent session effect's share of a trade's latent variance
ICC = 0.35
#: the block length the busiest-stretch share is read on (a quarter)
TOP_BLOCK = 63


def intensity(profile: str, n: int, reps: int, rng: np.random.Generator) -> np.ndarray:
    """(n, reps): each session's rate multiplier, mean one (see `PROFILES`). `flat` and the trends draw nothing and are
    returned as read-only broadcast views."""
    if profile not in PROFILES:
        raise ValueError(f"unknown intensity profile {profile!r}; one of {tuple(PROFILES)}")
    p = PROFILES[profile]
    n, reps = int(n), int(reps)
    if p["kind"] == "flat":
        return np.broadcast_to(np.ones((n, 1)), (n, reps))
    if p["kind"] == "trend":
        w = 1.0 + (float(p["ratio"]) - 1.0) * np.arange(n) / (n - 1)
        return np.broadcast_to((w / w.mean())[:, None], (n, reps))
    if p["kind"] == "burst":
        L, f = int(p["length"]), float(p["factor"])
        if L >= n:
            raise ValueError(f"a {L}-session burst needs a calendar longer than {n} sessions")
        phase = rng.integers(0, n - L + 1, size=reps)
        j = np.arange(n)[:, None]
        inb = (j >= phase[None, :]) & (j < phase[None, :] + L)
        base = n / (n - L + f * L)
        return np.where(inb, f * base, base)
    phi, sd = float(p["phi"]), float(p["sd"])
    h = np.empty((n, reps))
    h[0] = rng.standard_normal(reps) * sd
    inn = sd * math.sqrt(1.0 - phi * phi)
    for t in range(1, n):
        h[t] = phi * h[t - 1] + inn * rng.standard_normal(reps)
    h -= sd * sd / 2.0
    return np.exp(h, out=h)


def keep_rates(mult: np.ndarray, c: float) -> np.ndarray:
    """Each offer's keep probability, `min(1, c m)`."""
    if not (c > 0):
        raise ValueError(f"the base keep rate must be positive, not {c!r}")
    return np.minimum(1.0, float(c) * np.asarray(mult, dtype=float))


def thin_counts(offers: np.ndarray, rate: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """(n, reps) int64: each session's kept count, `Binomial(M_j, rate[j, r])` -- the sessions' offer counts `offers`
    (n,) and the rates only; no outcome is an argument."""
    M = np.asarray(offers)
    if M.ndim != 1 or not np.issubdtype(M.dtype, np.integer) or (M < 0).any():
        raise ValueError("offers is one non-negative integer count per session")
    rate = np.asarray(rate, dtype=float)
    if rate.shape[0] != M.shape[0]:
        raise ValueError("one rate row per session")
    return rng.binomial(M[:, None].astype(np.int64), rate).astype(np.int64)


def split_counts(offers: np.ndarray, rate_total: np.ndarray, share_first: float, rng: np.random.Generator
                 ) -> tuple[np.ndarray, np.ndarray]:
    """Two disjoint thinnings of the same offers: each offer kept with probability `rate_total`, and a kept offer goes
    to the first sample with probability `share_first`, else to the second (C1''s level and placebo fills: the same
    intensity, the placebo `(1 - share_first) / share_first` times the level's in expectation). Returns `(K1, K2)`;
    offer counts and rates only."""
    if not (0.0 < share_first < 1.0):
        raise ValueError("share_first is in (0, 1)")
    M = np.asarray(offers)
    rate_total = np.asarray(rate_total, dtype=float)
    p1 = rate_total * float(share_first)
    K1 = thin_counts(M, p1, rng)
    with np.errstate(invalid="ignore", divide="ignore"):
        p2 = np.where(p1 < 1.0, (rate_total - p1) / (1.0 - p1), 0.0)
    K2 = rng.binomial(M[:, None].astype(np.int64) - K1, np.clip(p2, 0.0, 1.0)).astype(np.int64)
    return K1, K2


def category_counts(session: np.ndarray, codes: np.ndarray, n: int, k: int) -> np.ndarray:
    """(n, k) int64: per session, how many offers fall in each outcome category `0 .. k-1` (the input to
    `subset_sums`)."""
    s = np.asarray(session)
    c = np.asarray(codes)
    if s.shape != c.shape or not np.issubdtype(s.dtype, np.integer) or not np.issubdtype(c.dtype, np.integer):
        raise ValueError("session and codes are integer arrays of the same shape")
    if len(c) and (c.min() < 0 or c.max() >= k):
        raise ValueError(f"a category code is outside 0..{k - 1}")
    return np.bincount(s * k + c, minlength=int(n) * k).reshape(int(n), k).astype(np.int64)


def subset_sums(cats: np.ndarray, values, sizes, rng: np.random.Generator) -> list[np.ndarray]:
    """For each `K` in `sizes` (each (n, reps), drawn in turn, disjointly): the sum of the outcome over a uniform
    `K`-subset of each session's offers not already taken by an earlier subset -- exactly, as sequential hypergeometric
    draws over the session's category counts `cats` (n, k) whose values are `values` (k). Returns one (n, reps) float
    array a subset. A session's subset sizes are the caller's (drawn before this, from counts only)."""
    C = np.asarray(cats, dtype=np.int64)
    vals = [float(v) for v in values]
    if C.ndim != 2 or C.shape[1] != len(vals):
        raise ValueError("cats is (sessions, categories) with one value a category")
    if (C < 0).any():
        raise ValueError("negative category counts")
    Ks = [np.asarray(K, dtype=np.int64) for K in sizes]
    if not Ks:
        return []
    shape = Ks[0].shape
    M = C.sum(axis=1)[:, None]
    tot = sum(Ks)
    if any(K.shape != shape for K in Ks) or (np.asarray(tot) > M).any() or any((K < 0).any() for K in Ks):
        raise ValueError("each subset size is (sessions, reps), non-negative, and together at most the session's offers")
    rem = [K.copy() for K in Ks]                       # what each subset still has to draw
    out = [np.zeros(shape) for _ in Ks]
    k = C.shape[1]
    for j in range(k):
        cj = C[:, j][:, None]                          # category j's offers
        rest = M - C[:, :j + 1].sum(axis=1)[:, None]   # offers in later categories
        avail_j = np.broadcast_to(cj, shape).copy()    # category j not yet taken by an earlier subset
        avail_rest = np.broadcast_to(rest, shape).copy()
        for i in range(len(Ks)):
            # the subsets drawn before i took (avail_j0 - avail_j) of category j and (rem_later) of the later ones;
            # what is left for subset i: avail_j of category j, avail_rest of the later categories
            if j == k - 1:
                d = rem[i]                             # the last category takes whatever is left to draw
            else:
                d = rng.hypergeometric(avail_j, avail_rest, rem[i])
            if vals[j] != 0.0:
                out[i] += vals[j] * d
            # subset i's remaining draws come from later categories; they leave later offers for the next subset
            later_i = rem[i] - d
            avail_j = avail_j - d
            avail_rest = avail_rest - later_i
            rem[i] = later_i
    if any((r != 0).any() for r in rem):
        raise AssertionError("subset draws did not exhaust their sizes")
    return out


def bernoulli_keep(session: np.ndarray, rate: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """(offers, reps) bool: each offer kept with its session's rate, independently -- session ordinals and rates only
    (for an outcome too continuous for `subset_sums`). float32 uniforms; a rate is compared in float32."""
    s = np.asarray(session)
    if s.ndim != 1 or not np.issubdtype(s.dtype, np.integer):
        raise ValueError("session is one integer ordinal an offer")
    r = np.asarray(rate, dtype=np.float32)
    u = rng.random((len(s), r.shape[1]), dtype=np.float32)
    return u < r[s]


def top_share(N: np.ndarray, block: int = TOP_BLOCK) -> np.ndarray:
    """(reps,): the busiest `block`-session block's share of the trades (blocks as `extended.lift_bound.block_index`
    cuts them); 0 where a replication has no trade."""
    from extended.lift_bound import block_index

    N = np.asarray(N, dtype=float)
    bid, _ = block_index(N.shape[0], block)
    starts = np.flatnonzero(np.r_[True, np.diff(bid) != 0])
    BN = np.add.reduceat(N, starts, axis=0)
    tot = BN.sum(axis=0)
    return np.where(tot > 0, BN.max(axis=0) / np.where(tot > 0, tot, 1.0), 0.0)


# ------------------------------------------------------------------------------------------------ the synthetic nulls


def synthetic_counts(profile: str, m: float, n: int, reps: int, rng: np.random.Generator) -> np.ndarray:
    """(n, reps) float: trades a session with mean `m` -- `iid` negative binomial of size 1 (Q-16's form), `burst10x`
    negative binomial of size 1 given its rate, the trend and AR profiles Poisson given theirs (the red team's
    `intensity.py` / `intensity2.py`)."""
    if profile == "iid":
        return rng.negative_binomial(1.0, 1.0 / (1.0 + float(m)), size=(int(n), int(reps))).astype(float)
    if profile not in PROFILES or profile == "flat":
        raise ValueError(f"unknown synthetic count profile {profile!r}; one of {SYNTHETIC_PROFILES}")
    lam = float(m) * intensity(profile, n, reps, rng)
    if PROFILES[profile]["kind"] == "burst":
        return rng.negative_binomial(1.0, 1.0 / (1.0 + lam)).astype(float)
    return rng.poisson(lam).astype(float)


def cluster_sums(N: np.ndarray, rng: np.random.Generator, icc: float = ICC) -> np.ndarray:
    """(n, reps): the session sums of `N` trades each `1/2 sign(a_j + e)`, `a_j ~ N(0, icc)`, `e ~ N(0, 1 - icc)` --
    Q-16's `cluster` outcome (a probit session effect; mean zero, so the null is exact)."""
    N = np.asarray(N)
    a = rng.standard_normal(N.shape) * math.sqrt(icc)
    p = stats.norm.cdf(a / math.sqrt(1.0 - icc))
    up = rng.binomial(N.astype(np.int64), p)
    return 0.5 * (2 * up - N)


def cluster_two_sample(N1: np.ndarray, N2: np.ndarray, rng: np.random.Generator, icc: float = ICC
                       ) -> tuple[np.ndarray, np.ndarray]:
    """The two samples' session sums, each trade `1/2 sign(a_j + e)` with the day's effect `a_j` shared (the C1'
    null: equal means, a common day effect)."""
    N1, N2 = np.asarray(N1), np.asarray(N2)
    a = rng.standard_normal(N1.shape) * math.sqrt(icc)
    p = stats.norm.cdf(a / math.sqrt(1.0 - icc))
    u1 = rng.binomial(N1.astype(np.int64), p)
    u2 = rng.binomial(N2.astype(np.int64), p)
    return 0.5 * (2 * u1 - N1), 0.5 * (2 * u2 - N2)


__all__ = ["PROFILES", "SYNTHETIC_PROFILES", "ICC", "TOP_BLOCK", "intensity", "keep_rates", "thin_counts",
           "split_counts", "category_counts", "subset_sums", "bernoulli_keep", "top_share", "synthetic_counts",
           "cluster_sums", "cluster_two_sample"]
