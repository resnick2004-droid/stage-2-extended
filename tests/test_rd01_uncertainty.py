"""RD-01 T-9 (`prereg/RD-01_firm_contracts.md` 10.2, 14.3): the uncertainty on each paired reading -- every other
h-start window kept, the 90 % t-interval from 4 kept windows only, the window sign count, the zero-series rule, the
minimum detectable difference, and the interval's coverage on one small fixed overlapping setting (seed 20261991), with
the 0.88 label. Pure numpy and scipy: no engine, no bar."""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats

from extended import firm_uncertainty as U

#: m2: T-9's draws are children of section 12's seed for T-9 (20261991), none other
KIDS = np.random.SeedSequence(U.SEED).spawn(4)


def test_every_other_window_is_kept_and_no_two_kept_windows_share_a_session():
    h = 5
    x = np.arange(53, dtype=float)                       # 10 whole windows of 5 starts, 3 starts dropped
    kept = U.kept_windows(x, h)
    assert [list(w) for w in kept] == [list(range(0, 5)), list(range(10, 15)), list(range(20, 25)),
                                       list(range(30, 35)), list(range(40, 45))]
    # a start's measure at h reads sessions s..s+h-1: the kept windows' sessions never overlap
    sessions = [set(range(int(w[0]), int(w[-1]) + h)) for w in kept]
    for a, b in zip(sessions, sessions[1:]):
        assert not a & b
    assert U.n_windows(53, h) == 5 and U.n_windows(4, h) == 0 and U.n_windows(10, h) == 1


def test_the_interval_needs_four_kept_windows():
    h = 3
    rng = np.random.default_rng(KIDS[0])
    six = rng.normal(size=6 * h * 2)                     # 12 windows -> 6 kept
    r = U.paired_reading(six, h)
    assert r["n_w"] == 6 and r["interval"] is not None
    three = rng.normal(size=6 * h)                       # 6 windows -> 3 kept
    r3 = U.paired_reading(three, h)
    assert r3["n_w"] == 3 and r3["interval"] is None and r3["mdd"] is None
    assert r3["note"] == "too few independent windows for an interval"
    assert sum(r3["signs"].values()) == 3


def test_the_interval_and_mdd_are_the_declared_t_forms():
    h = 2
    x = np.array([1.0, 3.0, 9.0, 9.0, 2.0, 2.0, 9.0, 9.0, 4.0, 6.0, 9.0, 9.0, 0.0, 2.0, 9.0, 9.0])
    r = U.paired_reading(x, h)
    means = np.array([2.0, 2.0, 5.0, 1.0])               # the kept windows' means
    se = means.std(ddof=1) / math.sqrt(4)
    lo, hi = means.mean() - stats.t.ppf(0.95, 3) * se, means.mean() + stats.t.ppf(0.95, 3) * se
    assert r["mean"] == pytest.approx(means.mean())
    assert r["interval"] == pytest.approx((lo, hi))
    assert r["mdd"] == pytest.approx((stats.t.ppf(0.95, 3) + stats.t.ppf(0.80, 3)) * se)
    assert r["signs"] == {"above": 4, "equal": 0, "below": 0}


def test_a_series_zero_on_every_kept_window_is_identical():
    x = np.zeros(40)
    x[5] = 3.0                                           # inside a dropped (odd) window only
    r = U.paired_reading(x, 5)
    assert r["note"] == "identical on these trades" and r["interval"] is None and r["mdd"] is None


def test_the_effective_sample_size_is_audit_bs_form():
    from extended.user_measures import n_eff_bartlett

    x = np.random.default_rng(KIDS[1]).normal(size=200)
    assert U.paired_reading(x, 21)["n_eff"] == pytest.approx(n_eff_bartlett(x, lag=21))


def test_the_coverage_on_one_small_overlapping_setting_and_the_label():
    shapes = U.coverage_shapes()
    assert {"gauss", "ahead", "paired"} <= set(shapes) and any(k.startswith("lumpy") for k in shapes)
    assert any(k.startswith("persistent") for k in shapes)
    cov = U.coverage("gauss", h=5, n_w=4, n_series=400, seed=U.SEED)
    again = U.coverage("gauss", h=5, n_w=4, n_series=400, seed=U.SEED)
    assert cov == again and 0.80 < cov <= 1.0            # seeded, reproducible; near nominal on kept windows
    assert U.SEED == 20261991
    assert U.coverage_label(0.87) == "interval below its coverage (0.870)"
    assert U.coverage_label(0.88) is None and U.coverage_label(0.95) is None


def test_overlapping_series_are_built_as_the_readings_measures_are():
    rng = np.random.default_rng(KIDS[2])
    sess = rng.normal(size=30)
    y = U.per_start_sums(sess, 5, 20)
    assert len(y) == 20 and y[3] == pytest.approx(sess[3:8].sum())


def test_identical_reads_the_values_not_the_window_means():
    # m3: a 0 / +-1 paired series whose kept windows each hold equal helps and hurts is not "identical"
    h = 2
    x = np.array([1.0, -1.0, 0.0, 0.0] * 4)                # kept windows [1, -1] each: means zero, values not
    r = U.paired_reading(x, h)
    assert r["note"] != U.IDENTICAL
    assert U.paired_reading(np.zeros(16), h)["note"] == U.IDENTICAL
