"""Q-82: `extended/count_nulls.py` -- the count-persistent nulls' generators, on synthetic inputs only.

What is asserted:
- every intensity profile has mean one and the shape it is declared with (the trends' end ratio, the burst's one
  63-session quarter at 10x, the AR profiles' stationary sd and lag-1 autocorrelation);
- **the thinning never reads an outcome**: no function that decides how many trades a session keeps takes an outcome
  argument, and the kept counts are the same, draw for draw, whatever the outcomes are;
- the kept set is a uniform subset: `subset_sums`' compositions follow the multivariate hypergeometric law exactly,
  for one subset and for two disjoint ones drawn in turn (C1''s level and placebo fills); and the offer-by-offer engine
  for continuous outcomes agrees with it in distribution;
- the two-sample split keeps the declared ratio, the busiest-quarter share is computed as stated, the synthetic nulls
  are mean zero.
Seeds: 20262010 (Q-82's tests seed, E-052's block), sub-streams by test.
"""
from __future__ import annotations

import inspect
import math

import numpy as np
import pytest

from extended import count_nulls as CN
from extended import lift_bound as LB

SEED = 20262010


def rng(i: int) -> np.random.Generator:
    return np.random.default_rng([SEED, 100 + i])


# ------------------------------------------------------------------------------------------------ profiles


def test_flat_and_trends_are_deterministic_with_mean_one():
    n = 657
    f = CN.intensity("flat", n, 3, rng(0))
    assert f.shape == (n, 3) and np.all(f == 1.0)
    for name, r in (("trend2x", 2.0), ("trend3x", 3.0)):
        m = CN.intensity(name, n, 4, rng(1))
        assert m.shape == (n, 4)
        assert np.allclose(m.mean(axis=0), 1.0, atol=1e-12)
        assert np.allclose(m[-1] / m[0], r, atol=1e-12)
        assert np.all(np.diff(m[:, 0]) > 0)


def test_burst_is_one_quarter_at_ten_times_the_rest_with_mean_one():
    n, reps = 657, 500
    m = CN.intensity("burst10x", n, reps, rng(2))
    assert np.allclose(m.mean(axis=0), 1.0, atol=1e-12)
    hi = m > m.min(axis=0)[None, :]
    assert np.all(hi.sum(axis=0) == 63)
    for r in range(reps):
        idx = np.flatnonzero(hi[:, r])
        assert idx[-1] - idx[0] == 62                              # one contiguous quarter
        assert math.isclose(m[idx[0], r] / m[0 if idx[0] > 0 else -1, r], 10.0, rel_tol=1e-12)
    phases = np.argmax(hi, axis=0)
    assert phases.min() < 60 and phases.max() > n - 63 - 60         # the phase is spread over the block


@pytest.mark.parametrize("name,phi,sd", [("ar98s07", 0.98, 0.7), ("ar98s10", 0.98, 1.0), ("ar98s15", 0.98, 1.5),
                                         ("ar995s10", 0.995, 1.0)])
def test_ar_profiles_are_stationary_with_the_declared_persistence(name, phi, sd):
    n, reps = 657, 3000
    m = CN.intensity(name, n, reps, rng(3))
    h = np.log(m) + sd * sd / 2
    assert abs(h.std() - sd) < 0.05 * sd + 0.03                    # started stationary: sd the same at every session
    assert abs(h[0].std() - sd) < 0.1 * sd and abs(h[-1].std() - sd) < 0.1 * sd
    r1 = float(np.mean(h[1:] * h[:-1]) / np.mean(h * h))
    assert abs(r1 - phi) < 0.004
    assert abs(m.mean() - 1.0) < 0.12                              # mean one (a lognormal's heavy tail: loose)


def test_unknown_profiles_are_refused():
    with pytest.raises(ValueError):
        CN.intensity("ar99", 657, 2, rng(4))
    with pytest.raises(ValueError):
        CN.synthetic_counts("flat", 0.3, 657, 2, rng(4))
    with pytest.raises(ValueError):
        CN.keep_rates(np.ones((3, 2)), 0.0)


# ------------------------------------------------------------------------------------------------ outcome-independence

#: the arguments a count-deciding function may take: sessions, offer counts, rates, profiles, the generator
COUNT_ARGS = {"profile", "n", "reps", "rng", "offers", "rate", "rate_total", "share_first", "session", "mult", "c"}


@pytest.mark.parametrize("fn", [CN.intensity, CN.keep_rates, CN.thin_counts, CN.split_counts, CN.bernoulli_keep])
def test_no_count_deciding_function_takes_an_outcome(fn):
    params = set(inspect.signature(fn).parameters)
    assert params <= COUNT_ARGS, f"{fn.__name__} takes {sorted(params - COUNT_ARGS)}"


def test_kept_counts_are_the_same_whatever_the_outcomes():
    """The composition a caller uses (intensity, counts, then the outcome's subset sums): the same seed with two
    unrelated outcome arrays gives identical kept counts and different sums."""
    n, reps = 657, 200
    g = np.random.default_rng([SEED, 200])
    M = g.integers(5, 30, size=n)
    s = np.repeat(np.arange(n), M)
    codes_a = g.integers(0, 3, size=len(s))
    codes_b = np.where(np.arange(len(s)) % 2 == 0, 0, 2)          # a different outcome altogether
    outs = []
    for codes in (codes_a, codes_b):
        r = np.random.default_rng([SEED, 201])
        mult = CN.intensity("ar98s15", n, reps, r)
        K = CN.thin_counts(M, CN.keep_rates(mult, 0.2), r)
        cats = CN.category_counts(s, codes, n, 3)
        S = CN.subset_sums(cats, (0.5, 0.0, -0.5), [K], r)[0]
        outs.append((K, S))
    assert np.array_equal(outs[0][0], outs[1][0])
    assert not np.array_equal(outs[0][1], outs[1][1])
    r1, r2 = np.random.default_rng([SEED, 202]), np.random.default_rng([SEED, 202])
    rate = CN.keep_rates(CN.intensity("burst10x", n, 7, r1), 0.1)
    assert np.array_equal(CN.bernoulli_keep(s, rate, r1),
                          CN.bernoulli_keep(s, CN.keep_rates(CN.intensity("burst10x", n, 7, r2), 0.1), r2))


# ------------------------------------------------------------------------------------------------ uniform subsets


def _mvhg(C, d):
    return math.prod(math.comb(c, x) for c, x in zip(C, d)) / math.comb(sum(C), sum(d))


def test_one_subset_follows_the_multivariate_hypergeometric_law():
    C = (3, 2, 4)
    K, reps = 5, 200_000
    cats = np.array([C])
    S = CN.subset_sums(cats, (1.0, 10.0, 100.0), [np.full((1, reps), K)], rng(5))[0][0].astype(int)
    a, b, c = S % 10, (S // 10) % 10, S // 100
    assert np.all(a + b + c == K)
    worst = 0.0
    for x in range(4):
        for y in range(3):
            z = K - x - y
            if 0 <= z <= 4:
                emp = float(np.mean((a == x) & (b == y)))
                worst = max(worst, abs(emp - _mvhg(C, (x, y, z))))
    assert worst < 0.005


def test_two_disjoint_subsets_follow_their_joint_law():
    C = (3, 2, 4)
    K1, K2, reps = 3, 4, 200_000
    S1, S2 = CN.subset_sums(np.array([C]), (1.0, 10.0, 100.0), [np.full((1, reps), K1), np.full((1, reps), K2)],
                            rng(6))
    S1, S2 = S1[0].astype(int), S2[0].astype(int)
    d1 = np.stack([S1 % 10, (S1 // 10) % 10, S1 // 100])
    d2 = np.stack([S2 % 10, (S2 // 10) % 10, S2 // 100])
    assert np.all(d1.sum(axis=0) == K1) and np.all(d2.sum(axis=0) == K2)
    assert np.all(d1 + d2 <= np.array(C)[:, None])                # disjoint: never more of a category than exist
    key = ((d1[0] * 3 + d1[1]) * 5 + d1[2]) * 100 + (d2[0] * 3 + d2[1]) * 5 + d2[2]
    vals, cnt = np.unique(key, return_counts=True)
    worst = 0.0
    seen = 0.0
    for v, k in zip(vals, cnt):
        hi, lo = divmod(int(v), 100)
        a1, r1 = divmod(hi, 15)
        b1, c1 = divmod(r1, 5)
        a2, r2 = divmod(lo, 15)
        b2, c2 = divmod(r2, 5)
        p = _mvhg(C, (a1, b1, c1)) * _mvhg((C[0] - a1, C[1] - b1, C[2] - c1), (a2, b2, c2))
        seen += p
        worst = max(worst, abs(k / reps - p))
    assert worst < 0.005 and seen > 0.999                         # every likely composition appears, at its rate


def test_subset_sizes_beyond_the_offers_are_refused():
    with pytest.raises(ValueError):
        CN.subset_sums(np.array([[2, 1]]), (1.0, 0.0), [np.array([[2]]), np.array([[2]])], rng(7))


def test_the_offer_by_offer_engine_agrees_with_the_hypergeometric_one():
    n, reps = 6, 60_000
    g = np.random.default_rng([SEED, 300])
    M = np.array([0, 3, 12, 20, 7, 15])
    s = np.repeat(np.arange(n), M)
    codes = g.integers(0, 3, size=len(s))
    v = np.array([0.5, 0.0, -0.5])[codes]
    rate = np.array([0.0, 0.9, 0.3, 0.05, 0.6, 0.2])[:, None] * np.ones((1, reps))
    r = np.random.default_rng([SEED, 301])
    K = CN.thin_counts(M, rate, r)
    Sh = CN.subset_sums(CN.category_counts(s, codes, n, 3), (0.5, 0.0, -0.5), [K], r)[0]
    keep = CN.bernoulli_keep(s, rate, np.random.default_rng([SEED, 302]))
    Nb = np.zeros((n, reps))
    Sb = np.zeros((n, reps))
    np.add.at(Nb, s, keep.astype(float))
    np.add.at(Sb, s, keep * v[:, None])
    for a, b in ((K.astype(float), Nb), (Sh, Sb)):
        se = np.sqrt((a.var(axis=1) + b.var(axis=1)) / reps) + 1e-12
        assert np.all(np.abs(a.mean(axis=1) - b.mean(axis=1)) < 5 * se + 1e-9)
        assert np.allclose(a.var(axis=1), b.var(axis=1), rtol=0.05, atol=1e-9)
    assert np.all(K[0] == 0) and np.all(Nb[0] == 0)


def test_split_counts_keep_the_ratio_and_stay_disjoint():
    n, reps = 50, 4000
    M = np.full(n, 40)
    rate = np.full((n, reps), 0.3)
    K1, K2 = CN.split_counts(M, rate, 1.0 / 6.0, rng(8))
    assert np.all(K1 + K2 <= M[:, None])
    assert abs(K1.mean() - 40 * 0.3 / 6) < 0.05 and abs(K2.mean() - 40 * 0.3 * 5 / 6) < 0.1
    full = np.ones((n, 10))
    K1, K2 = CN.split_counts(M, full, 1.0 / 6.0, rng(9))
    assert np.all(K1 + K2 == 40)                                   # a rate of one keeps every offer


def test_top_share_and_the_synthetic_nulls():
    N = np.zeros((657, 2))
    N[:, 0] = 1.0
    N[:65, 1] = 4.0
    N[65:, 1] = 0.0
    ts = CN.top_share(N)
    bid, G = LB.block_index(657, 63)
    assert math.isclose(ts[0], np.bincount(bid).max() / 657) and ts[1] == 1.0
    r = rng(10)
    iid = CN.synthetic_counts("iid", 2.0, 657, 2000, r)
    burst = CN.synthetic_counts("burst10x", 2.0, 657, 2000, r)
    ar = CN.synthetic_counts("ar98s15", 2.0, 657, 2000, r)
    assert abs(iid.mean() - 2.0) < 0.03 and abs(burst.mean() - 2.0) < 0.05 and abs(ar.mean() - 2.0) < 0.3
    assert np.median(CN.top_share(iid)) < 0.15 < 0.3 < np.median(CN.top_share(burst))
    assert np.median(CN.top_share(ar)) > 0.2
    S = CN.cluster_sums(burst, r)
    assert abs(S.sum() / burst.sum()) < 0.01                       # mean zero (an exact null)
    S1, S2 = CN.cluster_two_sample(iid, 5 * iid, r)
    assert abs(S1.sum() / iid.sum()) < 0.02 and abs(S2.sum() / (5 * iid).sum()) < 0.02
    assert np.all(np.abs(S1) <= iid / 2 + 1e-12)
