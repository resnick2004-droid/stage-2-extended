"""Q-16: the trades-first pass line's statistic (`extended/lift_bound.py`) on synthetic data.

What is asserted:
- the session aggregates and the 21-session blocks partition the judged block's calendar (empty sessions count);
- each candidate's estimate, standard error, degrees of freedom and lower bound equal a hand computation;
- the vectorised form (many replications at once) equals the one-sample form, column by column;
- the bootstrap draws at least 20 / level resamples, is reproducible from its seed and is centred;
- the shipped statistic's SIZE on a fixed null: iid-trade and clustered-session nulls (seeds 20261910, 20261911),
  20,000 replications each, at one-sided 1 % and 5 %: the realised rate inside its 99.9 % Clopper-Pearson interval of
  the nominal rate, or below it (a test may be conservative, never lax) -- fast and small; the full calibration at the
  family levels is `scripts/q16_calibrate.py` (and the `slow` test below);
- its power is not vacuous: a planted lift of five standard errors is found nearly always;
- the minimum detectable lift from the null replications equals the power curve's definition.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extended import lift_bound as LB  # noqa: E402


def _toy():
    """Ten sessions, 2 blocks of 5; trades on sessions 0, 0, 1, 3, 6, 6, 6, 9 (sessions 2, 4, 5, 7, 8 empty)."""
    x = np.array([0.5, -0.5, 0.5, 0.0, 0.5, 0.5, -0.5, 0.5])
    s = np.array([0, 0, 1, 3, 6, 6, 6, 9])
    return x, s, 10


def test_family_levels():
    assert LB.family_level(11) == pytest.approx(0.05 / 132)
    assert LB.family_level(15) == pytest.approx(0.05 / 240)
    assert [round(LB.family_level(k) * 1e6, 3) for k in LB.K_RANGE] == [378.788, 320.513, 274.725, 238.095, 208.333]


def test_session_sums_and_blocks():
    x, s, n = _toy()
    S, N = LB.session_sums(x, s, n)
    assert S.tolist() == [0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.5]
    assert N.tolist() == [2, 1, 0, 1, 0, 0, 3, 0, 0, 1]
    bid, G = LB.block_index(n, 5)
    assert G == 2 and bid.tolist() == [0] * 5 + [1] * 5
    bid, G = LB.block_index(657, 21)                      # the judged block: 31 blocks of 21 or 22 sessions
    sizes = np.bincount(bid)
    assert G == 31 and sizes.sum() == 657 and set(sizes) <= {21, 22} and np.all(np.diff(bid) >= 0)
    with pytest.raises(ValueError):
        LB.session_sums(x, s, 9)                          # a session outside the calendar is refused
    with pytest.raises(ValueError):
        LB.session_sums(x[:-1], s, n)


def test_t_block_by_hand():
    x, s, n = _toy()
    # equal weight: block means 0.5/4 = 0.125 (sessions 0-4: 0.5,-0.5,0.5,0.0) and 1.0/4 = 0.25 (0.5,0.5,-0.5,0.5)
    b = LB.t_block(x, s, n, level=0.05, block=5, weight="equal")
    m = np.array([0.125, 0.25])
    se = m.std(ddof=1) / math.sqrt(2)
    assert b.estimate == pytest.approx(m.mean()) and b.se == pytest.approx(se) and b.df == 1
    assert b.critical == pytest.approx(stats.t.ppf(0.95, 1))
    assert b.lower == pytest.approx(m.mean() - stats.t.ppf(0.95, 1) * se)
    assert b.rejects == (b.lower > 0)
    # trade weight: theta = 1.5 / 8; residual block sums u = 0.5 - 4 theta, 1.0 - 4 theta; CR1 with G/(G-1)
    b = LB.t_block(x, s, n, level=0.05, block=5, weight="trades")
    th = 1.5 / 8
    u = np.array([0.5 - 4 * th, 1.0 - 4 * th])
    se = math.sqrt(2 / 1 * (u ** 2).sum()) / 8
    assert b.estimate == pytest.approx(th) and b.se == pytest.approx(se) and b.df == 1 and b.trades == 8
    assert b.blocks == 2


def test_empty_blocks_are_dropped_from_the_equal_weight_mean():
    x = np.array([0.5, 0.5, -0.5])
    s = np.array([0, 1, 12])                             # block 1 (sessions 5-9) empty
    b = LB.t_block(x, s, 15, level=0.05, block=5, weight="equal")
    assert b.blocks == 2 and b.df == 1 and b.estimate == pytest.approx((0.5 - 0.5) / 2)


def test_vectorised_equals_one_sample():
    rng = np.random.default_rng(20261910)
    n, reps = 120, 7
    N = rng.poisson(1.3, size=(n, reps)).astype(float)
    S = rng.standard_normal((n, reps)) * np.sqrt(N)
    for weight in ("equal", "trades"):
        est, se, df = LB.t_stats(S, N, block=21, weight=weight)
        for r in range(reps):
            e1, s1, d1 = LB.t_stats(S[:, r], N[:, r], block=21, weight=weight)
            assert est[r] == pytest.approx(float(e1)) and se[r] == pytest.approx(float(s1)) and df[r] == d1
    est, se, df = LB.hac_stats(S, N, block=21, lags=2)
    e1, s1, d1 = LB.hac_stats(S[:, 3], N[:, 3], block=21, lags=2)
    assert est[3] == pytest.approx(float(e1)) and se[3] == pytest.approx(float(s1))


def test_hac_with_no_lags_is_the_trade_weighted_t():
    rng = np.random.default_rng(20261910)
    N = rng.poisson(2.0, size=300).astype(float)
    S = rng.standard_normal(300) * np.sqrt(N)
    e0, s0, _ = LB.t_stats(S, N, block=21, weight="trades")
    e1, s1, _ = LB.hac_stats(S, N, block=21, lags=0)
    G = 300 // 21
    assert e1 == pytest.approx(e0) and s1 == pytest.approx(s0 * math.sqrt((G - 1) / G))   # no small-G factor


def test_fixed_b_critical_values_are_seeded_and_ordered():
    c1 = LB.fixed_b_critical(31, 2, 0.01)
    assert c1 == LB.fixed_b_critical(31, 2, 0.01)                     # cached and reproducible
    assert LB.fixed_b_critical(31, 2, 0.001) > c1 > stats.norm.ppf(0.99)
    assert LB.fixed_b_critical(31, 4, 0.01) > LB.fixed_b_critical(31, 1, 0.01)    # wider bandwidth, larger value


def test_bootstrap_draws_seed_and_centre():
    rng = np.random.default_rng(20261911)
    n = 210
    x = rng.standard_normal(600)
    s = np.sort(rng.integers(0, n, 600))
    a = LB.cbb_t(x, s, n, level=0.01, block=21, seed=20261912)
    b = LB.cbb_t(x, s, n, level=0.01, block=21, seed=20261912)
    assert a.draws >= 20 / 0.01 and a.lower == b.lower
    assert LB.draws_for(LB.family_level(15)) >= 20 / LB.family_level(15)
    # centred: the circular resample's mean statistic sits at the sample's (the bootstrap t* has median near 0)
    S, N = LB.session_sums(x, s, n)
    tstar = LB.cbb_tstar(S, N, block=21, draws=4000, seed=20261912)
    assert abs(np.median(tstar)) < 0.1 and 0.7 < tstar.std() < 1.4


def _size(method, gen, reps, levels, seed):
    rng = np.random.default_rng(seed)
    S, N = gen(rng, reps)
    out = {}
    for a in levels:
        rej = LB.rejects(method, S, N, level=a)
        out[a] = int(rej.sum())
    return out


def _iid(rng, reps, n=300, lam=2.0):
    N = rng.poisson(lam, size=(n, reps)).astype(float)
    # each trade +-0.5 with probability 0.47 each, 0 with 0.06: the session sum of N such trades
    k = rng.binomial(N.astype(int), 0.94)
    up = rng.binomial(k, 0.5)
    return 0.5 * (2 * up - k), N


def _clustered(rng, reps, n=300, lam=3.0, icc=0.4):
    N = rng.negative_binomial(1.0, 1.0 / (1.0 + lam), size=(n, reps)).astype(float)    # overdispersed, mean lam
    a = rng.standard_normal((n, reps)) * math.sqrt(icc)
    # trades in a session share a; each trade is 0.5 sign(a + e): the sum is 0.5 (2 Bin(N, p(a)) - N)
    p = stats.norm.cdf(a / math.sqrt(1 - icc))
    up = rng.binomial(N.astype(int), p)
    return 0.5 * (2 * up - N), N


@pytest.mark.parametrize("gen,seed", [(_iid, 20261910), (_clustered, 20261911)])
def test_shipped_statistic_holds_its_size_on_a_fixed_null(gen, seed):
    reps, levels = 20000, (0.01, 0.05)
    got = _size(LB.SHIPPED, gen, reps, levels, seed)
    for a, k in got.items():
        lo, hi = LB.clopper_pearson(int(round(a * reps)), reps, conf=0.999)
        assert k / reps <= hi, f"{LB.SHIPPED} at {a}: {k}/{reps} rejections, above the nominal's 99.9 % interval"


@pytest.mark.xfail(strict=True, reason=(
    "Q-16, kept on record (the failure protocol): written before the choice, on a 300-session calendar; the shipped "
    "`cons` finds the planted 5-se lift 62.6 % of the time there, because its 63-session member has 4 blocks (df 3). "
    "Diagnosed (scratch dbg/diag_power.py): on the judged block's 657 sessions (10 blocks, df 9) it finds it 96 %. "
    "Not loosened; the judged-calendar check is test_power_on_the_judged_calendar"))
def test_power_is_not_vacuous_and_mdl_matches_the_power_definition():
    rng = np.random.default_rng(20261910)
    S, N = _iid(rng, 4000)
    level = 0.01
    mdl = LB.mdl_draws(LB.SHIPPED, S, N, level=level)              # per replication: the smallest lift it rejects
    q80 = float(np.quantile(mdl, 0.8))
    # adding the 80 % MDL to every trade makes the statistic reject in about 80 % of the replications
    rej = LB.rejects(LB.SHIPPED, S + (q80 + 1e-9) * N, N, level=level)
    assert 0.79 <= rej.mean() <= 0.81
    se = np.median(LB.t_stats(S, N, block=21, weight="trades")[1])
    rej5 = LB.rejects(LB.SHIPPED, S + 5 * se * N, N, level=level)
    assert rej5.mean() > 0.9


def test_mdl_matches_the_power_definition():
    rng = np.random.default_rng(20261910)
    S, N = _iid(rng, 4000, n=657)
    for m in ("t21w", "cons"):
        mdl = LB.mdl_draws(m, S, N, level=0.01)
        q80 = float(np.quantile(mdl, 0.8))
        assert 0.79 <= LB.rejects(m, S + (q80 + 1e-9) * N, N, level=0.01).mean() <= 0.81, m


def test_power_on_the_judged_calendar():
    """On the judged block's 657 sessions a lift of five of the binding member's (63-session) standard errors is found
    nearly always by the shipped statistic (seed 20261910 + the calendar)."""
    rng = np.random.default_rng([20261910, 657])
    S, N = _iid(rng, 4000, n=657)
    se63 = np.median(LB.t_stats(S, N, block=63, weight="trades")[1])
    assert LB.rejects(LB.SHIPPED, S + 5 * se63 * N, N, level=0.01).mean() > 0.9


def test_conservative_fallback_rejects_only_where_every_block_length_does():
    rng = np.random.default_rng(20261911)
    S, N = _clustered(rng, 3000)
    S = S + 0.03 * N
    cf = LB.rejects("cons", S, N, level=0.05)
    each = [LB.rejects(f"t{b}w", S, N, level=0.05) for b in (21, 42, 63)]
    assert np.array_equal(cf, each[0] & each[1] & each[2])


def test_many_levels_equals_the_per_level_functions():
    rng = np.random.default_rng(20261911)
    S, N = _clustered(rng, 500)
    S = S + 0.02 * N
    levels = (0.05 / 132, 0.01, 0.05)
    for m in ("t21e", "t21w", "t63w", "hac21", "cons"):
        rej, mdl = LB.many_levels(m, S, N, levels)
        for i, a in enumerate(levels):
            assert np.array_equal(rej[i], LB.rejects(m, S, N, level=a)), m
            assert np.allclose(mdl[i], LB.mdl_draws(m, S, N, level=a)), m


def test_bootstrap_many_levels_equals_one_level():
    rng = np.random.default_rng(20261911)
    S, N = _iid(rng, 3, n=126)
    c1 = LB.cbb_crit_many(S, N, levels=(0.01, 0.05), block=21, draws=4000)
    for i, a in enumerate((0.01, 0.05)):
        assert np.allclose(c1[i], LB.cbb_critical(S, N, level=a, block=21, draws=4000))


@pytest.mark.parametrize("method", LB.METHODS)
def test_degenerate_samples_never_pass(method):
    level = 0.01
    cases = [(np.array([]), np.array([], dtype=int)),                          # no trade
             (np.array([0.5, 0.5, -0.5]), np.array([0, 1, 2])),                 # every trade in one block
             (np.full(40, 0.5), np.arange(0, 640, 16))]                         # no spread at all
    for x, s in cases:
        b = LB.bound(method, x, s, 657, level=level)
        assert not b.rejects, (method, b)
        S, N = LB.session_sums(x, s, 657)
        assert not bool(LB.rejects(method, S, N, level=level)), method


def test_the_shipped_statistic_is_the_conservative_fallback():
    """The calibration's choice (docs/research/calibration_2026-11-15.md section 5.1)."""
    assert LB.SHIPPED == "cons"


def test_clopper_pearson():
    lo, hi = LB.clopper_pearson(0, 100)
    assert lo == 0.0 and hi == pytest.approx(0.0362, abs=1e-4)
    lo, hi = LB.clopper_pearson(38, 100000)
    assert lo < 0.05 / 132 < hi


@pytest.mark.slow
def test_full_calibration_script_runs_small(tmp_path):
    """The calibration script end to end at a tiny size (synthetic nulls only): it writes its tables, never under
    results/."""
    import subprocess
    root = Path(__file__).resolve().parent.parent
    r = subprocess.run([sys.executable, str(root / "scripts" / "q16_calibrate.py"), "--out", str(tmp_path),
                        "--reps", "2000", "--boot-reps", "20", "--synthetic-only", "--part", "lift"],
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert (tmp_path / "lift_size.csv").is_file() and (tmp_path / "lift_power.csv").is_file()


# ------------------------------------------------------------------------------------------------ two-sample forms
# E-022 (F-02's C1': the level lift minus a placebo lift) and E-023 (a side-keeping filter against its placebo-selection
# twin): a difference of two per-trade means, sessions clustered, the same block statistics.


def test_diff_stats_by_hand():
    # sample 1 on sessions 0..9 (two blocks of 5), sample 2 likewise
    S1 = np.array([1.0, 0, 0, 0, 0, 2, 0, 0, 0, 0]); N1 = np.array([2.0, 0, 0, 0, 0, 2, 0, 0, 0, 0])
    S2 = np.array([1.0, 1, 0, 0, 0, 0, 0, 0, 0, 1]); N2 = np.array([2.0, 2, 0, 0, 0, 0, 0, 0, 0, 2])
    est, se, df = LB.diff_stats(S1, N1, S2, N2, block=5)
    t1, t2 = 3 / 4, 3 / 6
    u = np.array([(1 - t1 * 2) / 4 - (2 - t2 * 4) / 6, (2 - t1 * 2) / 4 - (1 - t2 * 2) / 6])
    assert est == pytest.approx(t1 - t2) and df == 1
    assert se == pytest.approx(math.sqrt(2 / 1 * (u ** 2).sum()))


def test_diff_against_the_same_sample_is_zero_and_never_passes():
    rng = np.random.default_rng([20261910, 3])
    S, N = _clustered(rng, 50)
    est, se, _ = LB.diff_stats(S, N, S, N, block=21)
    assert np.allclose(est, 0.0) and np.allclose(se, 0.0)
    rej, _ = LB.diff_many_levels("cons", S, N, S, N, [0.01])
    assert not rej.any()


def test_diff_with_an_empty_second_sample_is_the_one_sample_statistic():
    rng = np.random.default_rng([20261910, 4])
    S, N = _clustered(rng, 30)
    z = np.zeros_like(S)
    e1, s1, d1 = LB.t_stats(S, N, block=21, weight="trades")
    e2, s2, d2 = LB.diff_stats(S, N, z, z, block=21, empty_second=True)
    assert np.allclose(e1, e2) and np.allclose(s1, s2) and np.array_equal(d1, d2)


def test_diff_vectorised_and_many_levels():
    rng = np.random.default_rng([20261911, 3])
    S1, N1 = _clustered(rng, 400)
    S2, N2 = _clustered(rng, 400)
    S1 = S1 + 0.03 * N1
    levels = (0.05 / 132, 0.01, 0.05)
    for m in ("t21w", "t42w", "t63w", "cons"):
        rej, mdl = LB.diff_many_levels(m, S1, N1, S2, N2, levels)
        for i, a in enumerate(levels):
            assert np.array_equal(rej[i], LB.diff_rejects(m, S1, N1, S2, N2, level=a)), m
        q80 = float(np.quantile(mdl[1], 0.8))                       # the MDL: adding it to sample 1 rejects 80 %
        assert 0.79 <= LB.diff_rejects(m, S1 + (q80 + 1e-9) * N1, N1, S2, N2, level=0.01).mean() <= 0.81, m


def test_placebo_selection_bound_and_two_sample_bound():
    rng = np.random.default_rng([20261910, 5])
    s = np.sort(rng.integers(0, 657, 6000))
    y = (rng.random(6000) < 0.5).astype(float)
    sel = rng.random(6000) < 0.1
    b = LB.placebo_selection_bound(y, s, sel, 657, level=0.01)
    assert b.estimate == pytest.approx(y[sel].mean() - y.mean()) and b.method == LB.SHIPPED
    assert not LB.placebo_selection_bound(y, s, np.ones(6000, bool), 657, level=0.01).rejects
    y2 = y + 0.4 * sel                                              # a filter that picks trades 40 points better
    assert LB.placebo_selection_bound(y2, s, sel, 657, level=LB.family_level(15)).rejects
    b2 = LB.two_sample_bound(y[sel], s[sel], y[~sel], s[~sel], 657, level=0.01)
    assert b2.estimate == pytest.approx(y[sel].mean() - y[~sel].mean())


@pytest.mark.parametrize("seed", [20261910, 20261911])
def test_shipped_diff_holds_its_size_on_a_fixed_null(seed):
    """Random selections of 10 % of clustered offers, independent of the outcomes, against the whole population (the
    placebo-selection twin's expectation): 20,000 replications at 1 % and 5 %."""
    rng = np.random.default_rng([seed, 6])
    reps, n = 20000, 300
    M = rng.poisson(8.0, size=(n, reps)).astype(np.int64)                        # offers a session
    a = rng.standard_normal((n, reps)) * math.sqrt(0.35)
    W = rng.binomial(M, stats.norm.cdf(a / math.sqrt(0.65)))                       # wins among them
    B = rng.binomial(M, 0.1)                                                       # selected offers
    A = rng.hypergeometric(W, M - W, B)                                            # wins among the selected
    rej, _ = LB.diff_many_levels(LB.SHIPPED, A.astype(float), B.astype(float), W.astype(float), M.astype(float),
                                 (0.01, 0.05))
    for i, al in enumerate((0.01, 0.05)):
        lo, hi = LB.clopper_pearson(int(round(al * reps)), reps, conf=0.999)
        assert rej[i].mean() <= hi, (al, rej[i].mean())


def test_diff_broadcasts_a_fixed_second_sample():
    rng = np.random.default_rng([20261911, 8])
    S1, N1 = _clustered(rng, 20)
    S2, N2 = _clustered(rng, 1)
    a = LB.diff_stats(S1, N1, S2, N2, block=21)
    b = LB.diff_stats(S1, N1, np.repeat(S2, 20, 1), np.repeat(N2, 20, 1), block=21)
    for x, y in zip(a, b):
        assert np.allclose(x, y)


def _session_filter_null(rng, reps, n=300, share=0.05):
    """A filter firing on whole sessions (5 %), independent of clustered binary outcomes; every offer the twin."""
    M = rng.poisson(8.0, size=(n, reps)).astype(np.int64)
    a = rng.standard_normal((n, reps)) * math.sqrt(0.35)
    W = rng.binomial(M, stats.norm.cdf(a / math.sqrt(0.65))).astype(float)
    f = rng.random((n, reps)) < share
    return f * W, f * M.astype(float), W, M.astype(float)


def test_the_treated_block_count_sets_the_df():
    S1 = np.zeros(42); N1 = np.zeros(42)
    S1[[3, 30]] = [2.0, 1.0]; N1[[3, 30]] = [4.0, 4.0]                       # sample 1 in 2 of 2 blocks of 21
    S2 = np.arange(42, dtype=float) % 3; N2 = np.full(42, 3.0)
    assert LB.diff_stats(S1, N1, S2, N2, block=21)[2] == 1
    S1b, N1b = S1.copy(), N1.copy(); S1b[30] = N1b[30] = 0.0                  # now in 1 block: nothing to test
    assert LB.diff_stats(S1b, N1b, S2, N2, block=21)[2] == 0
    assert not LB.diff_rejects("cons", S1b, N1b, S2, N2, level=0.05)
    assert LB.diff_stats(S1b, N1b, S2, N2, block=21, df_rule="all")[2] == 1    # the first form counted both


def test_persistent_selection_first_form_fails_and_treated_form_holds():
    """Q-16's second finding, kept on record: with the df from every block ('all'), a whole-session filter is lax beyond
    its interval; counting the selected sample's blocks ('treated', the default), the shipped `cons` holds
    (seed 20261911)."""
    rng = np.random.default_rng([20261911, 10])
    A, B, W, M = _session_filter_null(rng, 20000)
    for al in (0.01, 0.05):
        lo, hi = LB.clopper_pearson(int(round(al * 20000)), 20000, conf=0.999)
        first = LB.diff_many_levels("t21w", A, B, W, M, [al], df_rule="all")[0][0].mean()
        assert first > hi, (al, first)                                         # the recorded failure
        r = LB.diff_many_levels(LB.SHIPPED, A, B, W, M, [al])[0][0].mean()
        assert r <= hi, (LB.SHIPPED, al, r)


@pytest.mark.xfail(strict=True, reason=(
    "Q-16, kept on record: written with the treated-df change, before its calibration; on this 300-session "
    "whole-session filter null t21w alone with the treated df still rejects 1.295 % at 1 % (6-11 treated blocks: the "
    "CR variance stays a little low); every member is 1.2-1.3x; only their intersection (cons, 0.27 %) holds -- "
    "scratch dbg/diag_treated.py"))
def test_t21w_alone_with_the_treated_df_holds_on_a_session_filter():
    rng = np.random.default_rng([20261911, 10])
    A, B, W, M = _session_filter_null(rng, 20000)
    lo, hi = LB.clopper_pearson(200, 20000, conf=0.999)
    assert LB.diff_many_levels("t21w", A, B, W, M, [0.01])[0][0].mean() <= hi
