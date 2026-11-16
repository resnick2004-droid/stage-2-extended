"""Q-17: the readings beside every user measure -- the pure measures (`extended.user_measures`), on synthetic series.

Each test is the check that would catch the measure being wrong: a hand-computed answer on a small series, the edge
cases (an unreached event, a start never paid, a fall back below zero), and the estimator of the effective number of
starts on series whose answer is known (independent draws; the same value held over blocks).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from extended import user_measures as M


# ------------------------------------------------------------------------------------------------ P and the money


def test_p_by_month_is_the_mean_of_the_three_shares_on_the_same_starts():
    nets = np.array([[10.0, -5.0, 3.0],      # ahead at months 1 and 3
                     [-1.0, -1.0, -1.0],     # never
                     [0.0, 2.0, 2.0]])       # 0 is not ahead (net above zero)
    out = M.p_by_month(nets)
    assert out["share_month_1"] == pytest.approx(1 / 3)
    assert out["share_month_2"] == pytest.approx(1 / 3)
    assert out["share_month_3"] == pytest.approx(2 / 3)
    assert out["P"] == pytest.approx((1 + 1 + 2) / 9)
    assert out["n"] == 3


def test_p_by_month_leaves_out_a_start_without_all_three_nets():
    nets = np.array([[1.0, 1.0, 1.0], [1.0, np.nan, 1.0]])
    out = M.p_by_month(nets)
    assert out["n"] == 1 and out["P"] == pytest.approx(1.0)


def test_cvar10_is_the_mean_of_the_worst_tenth():
    x = np.arange(1.0, 21.0)                 # 20 values: the worst 2 are 1 and 2
    assert M.cvar(x, 0.10) == pytest.approx(1.5)
    x = np.arange(1.0, 12.0)                 # 11 values: ceil(1.1) = 2 worst
    assert M.cvar(x, 0.10) == pytest.approx(1.5)
    assert math.isnan(M.cvar(np.array([np.nan]), 0.10))


def test_bankroll_limit_counts_a_start_that_spent_past_it_as_not_ahead():
    nets = np.array([[5.0, 5.0, 5.0], [5.0, 5.0, 5.0], [-3.0, 4.0, 4.0]])
    spent = np.array([[1500.0] * 3, [2400.0] * 3, [np.nan, 2600.0, 2600.0]])
    out2000 = M.p_by_month(nets, spent=spent, limit=2000.0)
    out2500 = M.p_by_month(nets, spent=spent, limit=2500.0)
    assert out2000["P"] == pytest.approx(3 / 9)      # only the first start is ahead within $2,000
    assert out2500["P"] == pytest.approx(6 / 9)      # the second too; the third spent $2,600
    # the share that passed the limit before its first payout (or had no payout yet and spent past it)
    assert M.share_over_limit(np.array([1500.0, 2400.0, 2600.0, np.nan]), 2000.0) == pytest.approx(2 / 3)


def test_a_start_ahead_without_its_spending_known_refuses():
    with pytest.raises(ValueError):
        M.p_by_month(np.array([[5.0, 5.0, 5.0]]), spent=np.array([[np.nan] * 3]), limit=2000.0)


# ------------------------------------------------------------------------------------------------ n_eff


def test_n_eff_of_independent_draws_is_about_n():
    rng = np.random.default_rng(20261920)
    x = rng.normal(size=4000)
    n = M.n_eff_bartlett(x, 63)
    assert 3000 < n < 5500


def test_n_eff_of_a_value_held_over_blocks_is_about_the_block_count():
    rng = np.random.default_rng(20261920)
    x = np.repeat(rng.normal(size=60), 63)  # 60 independent values, each held for 63 starts
    n = M.n_eff_bartlett(x, 126)
    assert 30 < n < 120                      # Bartlett's taper at L = 2 b: of the order of the 60 blocks
    assert M.n_eff_bartlett(x, 63) < 300


def test_n_eff_of_a_constant_is_blank():
    assert math.isnan(M.n_eff_bartlett(np.ones(100), 63))


# ------------------------------------------------------------------------------------------------ the daily path


def test_break_even_is_the_first_close_at_or_above_zero():
    rel = np.array([-50.0, -100.0, -150.0, 0.0, 200.0, -10.0, 300.0])
    assert M.break_even_day(rel) == 3
    assert M.fell_back(rel, 3) is True
    # the running high after break-even is 200 at close 4; the fall to -10 at close 5 is 210
    assert M.deepest_fall_after(rel, 3) == pytest.approx(210.0)


def test_never_breaking_even_is_blank():
    rel = np.array([-50.0, -100.0, -1e-3])
    assert math.isnan(M.break_even_day(rel))
    assert M.fell_back(rel, float("nan")) is None
    assert math.isnan(M.deepest_fall_after(rel, float("nan")))


def test_close_zero_is_never_the_break_even_day():
    # day 0 is the purchase evening; a start with nothing bought is not "broken even" on it
    assert M.break_even_day(np.array([0.0, -5.0, 1.0])) == 2


def test_a_fall_to_exactly_zero_is_not_a_fall_back():
    rel = np.array([-5.0, 10.0, 0.0, 4.0])
    assert M.break_even_day(rel) == 1
    assert M.fell_back(rel, 1) is False


# ------------------------------------------------------------------------------------------------ evenness


def _twelve(net_months):
    return np.asarray(net_months, float)


def test_evenness_on_a_hand_computed_year():
    nets = _twelve([-100, 50, 50, 300, 300, 250, 400, 400, 400, 400, 900, 900])
    # payouts arrive on days 30 (month 2), 70 and 80 (month 4), 230 (month 11)
    pays = [(30, 200.0), (70, 300.0), (80, 100.0), (230, 600.0)]
    e = M.evenness(nets, pays)
    changes = np.diff(np.concatenate([[0.0], nets]))
    assert e["share_months_positive"] == pytest.approx(float((changes > 0).mean()))
    assert e["sd_monthly_net"] == pytest.approx(float(changes.std(ddof=1)))
    # months with a payout: 2, 4, 11 -> the longest run without: months 5-10, six months
    assert e["longest_months_without_payout"] == 6
    assert e["payouts_per_month"] == pytest.approx(4 / 12)
    assert e["payout_cash_per_month"] == pytest.approx(1200.0 / 12)
    assert e["largest_month_share"] == pytest.approx(600.0 / 1200.0)


def test_evenness_of_a_start_never_paid():
    e = M.evenness(_twelve([-150] * 12), [])
    assert e["longest_months_without_payout"] == 12
    assert e["payouts_per_month"] == 0.0
    assert math.isnan(e["largest_month_share"])


def test_month_boundaries_are_sessions_one_to_twenty_one():
    # a payout on session 21 is month 1's; on session 22 month 2's
    e = M.evenness(_twelve([0] * 12), [(21, 10.0), (22, 30.0)])
    assert e["largest_month_share"] == pytest.approx(0.75)
    assert e["longest_months_without_payout"] == 10


def test_evenness_needs_twelve_months():
    with pytest.raises(ValueError):
        M.evenness(_twelve([0] * 11), [])


# ------------------------------------------------------------------------------------------------ distributions


def test_days_quantile_counts_an_unreached_start_as_beyond():
    first = np.array([5.0, 10.0, np.nan, np.nan])
    assert M.days_quantile(first, 126, 10) == pytest.approx(np.percentile([5, 10, 1e9, 1e9], 10))
    assert math.isnan(M.days_quantile(first, 126, 90))     # beyond the window: blank
    assert M.days_quantile(np.array([3.0, 200.0]), 126, 0) == pytest.approx(3.0)
    assert math.isnan(M.days_quantile(np.array([3.0, 200.0]), 126, 100))  # 200 is past the window: beyond


def test_quantiles_of_finite_values():
    q = M.quantiles(np.array([1.0, 2.0, np.nan, 3.0]))
    assert q == {"p10": pytest.approx(1.2), "p50": pytest.approx(2.0), "p90": pytest.approx(2.8), "n": 3}
    q = M.quantiles(np.array([np.nan]))
    assert q["n"] == 0 and math.isnan(q["p50"])
