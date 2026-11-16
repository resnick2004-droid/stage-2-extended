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
