"""F-03 (family O) V3 of the second build read: B2 runs section 11 item 2's two stationary bootstraps (normal days and
report days) and nothing else -- a target session of another kind (FOMC, early close, no bar) is left empty, so a kind
the choice span lacks no longer raises; on normal and report days alone the draws are the former loop's, bit for bit.
Synthetic inputs, seeds `[SEED_TESTS, 1300, ...]` (section 16's test block).
"""
from __future__ import annotations

import numpy as np
import pytest

from extended import opening_stats as ST


def _inputs(rng, judged_kinds, choice_kinds, M=6):
    jk, ck = np.array(judged_kinds), np.array(choice_kinds)
    nj = len(jk)
    exists = rng.random((nj, M)) < 0.8
    group = (jk == "b").astype(np.int64) + 2 * (np.arange(nj) >= nj // 2)
    W1 = (exists & (rng.random((nj, M)) < 0.3)).astype(float)
    return ST.B2Inputs(rng.normal(size=(len(ck), M)), ck, jk, group, exists, W1, exists.astype(float))


def _former(inp, a_star, rng):
    """The loop before V3 (one bootstrap per kind present), for the normal-and-report-only comparison."""
    nj, M = inp.judged_exists.shape
    pi = np.empty(nj, dtype=np.int64)
    for kind in np.unique(inp.judged_kind):
        jrows = np.flatnonzero(inp.judged_kind == kind)
        src = np.flatnonzero(inp.choice_kind == kind)
        pi[jrows] = src[ST.stationary_indices(rng, len(src), len(jrows), ST.B2_MEAN_BLOCK)]
    V = inp.choice_values[pi] + float(a_star) * ST.slow_sign(rng, nj)[:, None]
    ok = inp.judged_exists & np.isfinite(V)
    for g in np.unique(inp.judged_group):
        rows = inp.judged_group == g
        sub, mm = V[rows], ok[rows]
        cnt = mm.sum(axis=0)
        mu = np.where(cnt > 0, np.where(mm, sub, 0.0).sum(axis=0) / np.maximum(cnt, 1), 0.0)
        V[rows] = sub - mu[None, :]
    V = np.where(ok, V, np.nan)
    return ST.session_sums(V, inp.W1) + ST.session_sums(V, inp.W2)


def test_on_normal_and_report_days_the_draws_are_the_former_loops():
    rng = np.random.default_rng([ST.SEED_TESTS, 1300, 0])
    jk = rng.choice(["n", "b"], size=150, p=[0.85, 0.15])
    inp = _inputs(rng, jk, rng.choice(["n", "b"], size=200, p=[0.85, 0.15]))
    for j in range(5):
        got = ST.b2_replicate_sums(inp, 0.1, ST.rng_of(ST.SEED_TESTS, 1300, 1, j))
        want = _former(inp, 0.1, ST.rng_of(ST.SEED_TESTS, 1300, 1, j))
        assert all(np.array_equal(a, b) for a, b in zip(got, want))


def test_a_target_kind_the_source_lacks_is_left_empty_and_never_raises():
    rng = np.random.default_rng([ST.SEED_TESTS, 1300, 2])
    jk = np.array(["n"] * 60 + ["o"] * 3 + ["b"] * 12 + ["e", "x"])
    inp = _inputs(rng, jk, ["n"] * 80 + ["b"] * 20)
    S1, N1, S2, N2 = ST.b2_replicate_sums(inp, 0.0, ST.rng_of(ST.SEED_TESTS, 1300, 3))
    other = ~np.isin(jk, ST.B2_KINDS)
    assert (N1[other] == 0).all() and (N2[other] == 0).all() and (S2[other] == 0).all()
    assert (N2[~other] > 0).any()


def test_a_declared_kind_the_source_lacks_still_refuses():
    rng = np.random.default_rng([ST.SEED_TESTS, 1300, 4])
    inp = _inputs(rng, ["n"] * 20 + ["b"] * 5, ["n"] * 40)
    with pytest.raises(ValueError):
        ST.b2_replicate_sums(inp, 0.0, ST.rng_of(ST.SEED_TESTS, 1300, 5))
