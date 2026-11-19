"""Wave 3.1: the journey measures `docs/MEASURES.md` marks "to build" (`extended/journey_measures.py`) and the changed
pure measures (`extended/user_measures.py`), each on synthetic per-start paths with known answers -- the check that
would catch the measure being wrong (m-13). Pure numpy: no engine, no data, no draw.

The red team's cases (`docs/reviews/MEASURES_2026-11-18.md`, `MEASURES_v2_2026-11-18.md`) are here by name:
* `test_red_team_the_user_2600_below_after_a_small_payout` (B-2): the peak through the month close, not the spending
  before the first payout, decides `P_B`; (24)'s peak form sees the fall;
* `test_red_team_a_single_payout_at_session_120` (B-6): the wait from day 0 is 120, not "no gap";
* `test_red_team_the_censored_p90` (N-1): a censored lower bound below, or at an interpolation point of, the p90 makes
  it "at least".
"""
from __future__ import annotations

import math
from datetime import date

import numpy as np
import pytest

from extended import journey_measures as J
from extended import user_measures as M


# ------------------------------------------------------------------------------------------------ helpers


def path(n: int, steps: dict[int, float], start: float = -500.0) -> np.ndarray:
    """A unit's net at closes 0 .. n: `start` at close 0, then the net changes by `steps[k]` at close k."""
    rel = np.full(n + 1, float(start))
    for k in range(1, n + 1):
        rel[k] = rel[k - 1] + float(steps.get(k, 0.0))
    return rel


def the_2600_user() -> tuple[np.ndarray, list[tuple[int, float]]]:
    """B-2's user: $500 of fees on day 0, a $100 payout at close 30, then fees down to $2,600 below the start by close
    50, a $3,000 payout at close 62 -- ahead at month 3 -- and flat to close 252."""
    steps = {30: 100.0, **{k: -110.0 for k in range(31, 51)}, 62: 3000.0}
    rel = path(252, steps)
    return rel, [(30, 100.0), (62, 3000.0)]


# ------------------------------------------------------------------------------------------------ user_measures


def test_ahead_is_above_a_millionth_in_both_ahead_tests():
    """m-11: a net of a float residue above zero is not ahead, in `p_by_month` (line 64) and `months_ahead` (line 82)
    alike, so the two agree."""
    nets = np.array([[5e-7, 2.0, 3.0], [1e-6, 1e-6 + 1e-9, 0.0]])
    p = M.p_by_month(nets)
    assert p["share_month_1"] == 0.0 and p["share_month_2"] == 1.0 and p["share_month_3"] == 0.5
    assert p["P"] == pytest.approx(3 / 6)
    assert list(M.months_ahead(nets)) == [2.0, 1.0]
    assert M.months_ahead(nets).sum() / (3 * len(nets)) == p["P"]


def test_the_censored_days_percentile_is_never_blank_and_stage2s_form_stays_beside():
    first = np.array([5.0, 10.0, np.nan, 200.0])
    assert list(M.censored_days(first, 126)) == [5.0, 10.0, 127.0, 127.0]
    assert M.days_quantile(first, 126, 50, censored=True) == pytest.approx(68.5)
    assert M.days_quantile(first, 126, 90, censored=True) == 127.0
    assert math.isnan(M.days_quantile(first, 126, 50))                 # Stage 2's form blanks beyond the window
    assert M.days_quantile(first, 126, 10) == M.days_quantile(first, 126, 10, censored=True)
    assert M.BEYOND == 1e9


def test_the_peak_through_a_close_includes_it_and_spent_before_does_not():
    rel = np.array([-100.0, -300.0, -50.0, -700.0, 200.0])
    assert M.spent_before(rel, 3) == 300.0 and M.peak_through(rel, 3) == 700.0
    assert M.spent_before(rel, 0) == 0.0 and M.peak_through(rel, 0) == 100.0
    with pytest.raises(ValueError):
        M.peak_through(rel, 5)
    pk = M.peak_by_month(path(70, {10: -200.0, 50: -100.0}))
    assert pk[:3] == [700.0, 700.0, 800.0] and all(math.isnan(x) for x in pk[3:])


# ------------------------------------------------------------------------------------------------ the strict rule


def test_red_team_the_censored_p90():
    """N-1: nine paid units at $100 .. $900 and one unpaid unit."""
    paid = [100.0 * i for i in range(1, 10)]
    # (a) the unpaid unit's lower bound ($500) lies below the p90: "at least"
    q = J.strict_quantiles(paid + [500.0], [False] * 9 + [True])
    assert q["p90"] == pytest.approx(float(np.percentile(paid + [500.0], 90)))
    assert q["p90_exact"] is False and q["p10_exact"] is True
    # (b) the bound ($5,000) lies above the p90, but the p90 interpolates toward it: it moves with the true value, so
    # it is "at least" (the rule's "only if", read strictly; the module docstring)
    q = J.strict_quantiles(paid + [5000.0], [False] * 9 + [True])
    assert q["p90"] < 5000.0 and q["p90_exact"] is False and q["p50_exact"] is True
    # (c) with twenty paid units the p90 no longer touches the censored one: exact
    paid20 = [50.0 * i for i in range(1, 21)]
    q = J.strict_quantiles(paid20 + [5000.0], [False] * 20 + [True])
    assert q["p90_exact"] is True
    # and a censored bound tied with the percentile is never above it: "at least"
    q = J.strict_quantiles([1.0, 1.0, 1.0], [True, False, False])
    assert q["p50"] == 1.0 and q["p50_exact"] is False
    assert J.strict_quantiles([1.0, 2.0], [False, False])["p90_exact"] is True


def test_the_strict_rule_refuses_a_blank():
    with pytest.raises(ValueError):
        J.strict_quantiles([1.0, np.nan], [False, True])


# ------------------------------------------------------------------------------------------------ (2), (3), (6)


def test_cash_to_an_event_is_exact_when_reached_and_a_censored_bound_otherwise():
    rel = path(130, {**{k: -49.0 for k in (31, 62, 93, 124)}, 40: -149.0})
    assert J.spent_to_event(rel, 35, 126) == (549.0, False)              # closes 0 .. 34
    assert J.spent_to_event(rel, None, 126) == (500.0 + 49 * 4 + 149, True)
    assert J.spent_to_event(rel, 128, 126) == (500.0 + 49 * 4 + 149, True)  # after the window: not reached
    with pytest.raises(ValueError):
        J.spent_to_event(rel[:100], 35, 126)                               # not in E_126


def test_evaluations_before_the_first_pass():
    assert J.evaluations_to_first_pass([0, 5, 10, 20], 10, 126) == (2.0, False)
    assert J.evaluations_to_first_pass([0, 5, 10, 20], None, 15) == (3.0, True)


# ------------------------------------------------------------------------------------------------ P and P_B


def test_red_team_the_user_2600_below_after_a_small_payout():
    rel, arr = the_2600_user()
    assert rel[50] == -2600.0 and rel[63] == 400.0
    # P counts month 3
    assert J.months_ahead_under(rel) == 1
    # P_B at $2,500: the peak through the month-3 close is $2,600 -- the user has quit; at $3,000 within it
    assert J.months_ahead_under(rel, 2500.0) == 0 and J.months_ahead_under(rel, 3000.0) == 1
    assert J.months_ahead_under(rel, 2600.0) == 1                       # spending exactly B is within it
    # the sub-reading "before the first payout" (Q-17's) sees only the $500 before the first payout
    assert J.months_ahead_under(rel, 2500.0, before_first_payout=True, arrivals=arr) == 1
    # the same through user_measures.p_by_month, passing the peak field (user_readings' path)
    pk = np.array([M.peak_by_month(rel)[:3]])
    assert M.p_by_month(np.array([[rel[21], rel[42], rel[63]]]), spent=pk, limit=2500.0)["P"] == 0.0
    # (24): paid within B (the first payout came after $500), but the peak form sees the fall
    st = J.bankroll_stop([rel], [30], 126, [2000.0, 2500.0, 3000.0])
    assert st[2500.0]["share_paid_within"] == 1.0 and st[2500.0]["share_peak_over"] == 1.0
    assert st[3000.0]["share_peak_over"] == 0.0
    # (25) and (15)
    assert J.peak_oop(rel) == 2600.0
    assert J.return_on_money_at_risk(rel) == pytest.approx(400.0 / 2600.0)


def test_p_bankroll_over_units_and_the_peak_field_agree():
    """`p_bankroll` (the formula's spending before the month close) and `p_by_month` with the inclusive peak field give
    the same `P_B` on every unit: at a close where the unit is ahead the close itself is above zero."""
    rng = np.random.default_rng(7)                    # a test's own fixture seed; nothing declared reads it
    rels = []
    for _ in range(60):
        steps = {int(k): float(v) for k, v in zip(rng.integers(1, 64, 12), rng.normal(0, 900, 12))}
        rels.append(path(63, steps, start=-float(rng.integers(100, 900))))
    nets = np.array([[r[21], r[42], r[63]] for r in rels])
    peaks = np.array([M.peak_by_month(r)[:3] for r in rels])
    for b in (300.0, 1000.0, 2500.0):
        a = J.p_bankroll(rels, b)
        c = M.p_by_month(nets, spent=peaks, limit=b)
        assert a["P"] == c["P"] and all(a[f"share_month_{m}"] == c[f"share_month_{m}"] for m in (1, 2, 3))
    assert J.p_bankroll(rels)["P"] == M.p_by_month(nets)["P"]


def test_shares_ahead_at_months_6_and_12_read_above_a_millionth():
    a = path(252, {100: 500.0 + 1e-7})
    b = path(252, {100: 600.0})
    assert J.share_ahead_at([a, b], 126) == {"share": 0.5, "n": 2}
    with pytest.raises(ValueError):
        J.share_ahead_at([a[:200]], 252)


# ------------------------------------------------------------------------------------------------ (16), (21)


def test_the_monthly_net_in_months_4_to_12_is_the_median_with_the_mean_beside():
    """m-1: nine flat months and one lump read 0 by the median, 1,000 a month by the mean."""
    rel = path(252, {240: 9000.0})
    d = J.monthly_changes(rel)
    assert d[0] == -500.0 and d[11] == 9000.0 and (d[1:11] == 0).all()
    assert J.monthly_net_4_12(rel) == {"median": 0.0, "mean": 1000.0}


def test_red_team_a_single_payout_at_session_120():
    """B-6: a lone payout at 120 waits 120 sessions from day 0 -- Stage 2's S5b (gaps after the first payout) sees no
    gap at all; a unit paid every 21 sessions waits 21; an unpaid unit is censored at 127."""
    assert J.longest_wait([120]) == (120.0, False)
    assert J.longest_wait([21, 42, 63, 84, 105, 126]) == (21.0, False)
    assert J.longest_wait([5, 6]) == (120.0, False)                     # the wait to the window's end counts
    assert J.longest_wait([]) == (127.0, True) and J.longest_wait([130]) == (127.0, True)
    waits = [J.longest_wait(a)[0] for a in ([120], [21, 42, 63, 84, 105, 126], [])]
    r = J.days_reading([w if w <= 126 else np.nan for w in waits], 126)
    assert r["p50"] == 120.0 and r["n_censored"] == 1 and r["share_by"] == pytest.approx(2 / 3)


# ------------------------------------------------------------------------------------------------ (24)


def test_the_bankroll_stops_three_states():
    paid_cheap = path(126, {20: 1000.0})                               # paid at 20 after $500
    run_out_paid = path(126, {10: -2500.0, 60: 4000.0})                # $3,000 spent before its payout at 60
    run_out_unpaid = path(126, {10: -2600.0})
    still = path(126, {10: -400.0})                                    # $900 spent, never paid
    rels = [paid_cheap, run_out_paid, run_out_unpaid, still]
    fy = [20, 60, None, None]
    assert [J.bankroll_state(r, f, 126, 2000.0) for r, f in zip(rels, fy)] == \
        ["paid_within", "run_out", "run_out", "censored"]
    st = J.bankroll_stop(rels, fy, 126, [2000.0, 5000.0])[2000.0]
    assert (st["share_paid_within"], st["share_run_out"], st["share_censored"]) == (0.25, 0.5, 0.25)
    assert st["share_not_paid_within"] == 0.75 and st["share_peak_over"] == 0.5 and st["n"] == 4
    big = J.bankroll_stop(rels, fy, 126, [5000.0])[5000.0]
    assert (big["share_paid_within"], big["share_run_out"], big["share_censored"]) == (0.5, 0.0, 0.5)


# ------------------------------------------------------------------------------------------------ (31)


def test_how_a_funded_account_ends():
    base = {"activation_day": 10, "arrivals": ()}
    assert J.account_ending({**base, "ended_on": None}, 126) == "window"
    assert J.account_ending({**base, "ended_on": 200, "closed": True}, 126) == "window"
    assert J.account_ending({**base, "ended_on": 50, "closed": True}, 126) == "breach"
    assert J.account_ending({**base, "ended_on": 50, "closed": True, "denied": 1}, 126) == "denied"
    assert J.account_ending({**base, "ended_on": 50, "closed": True, "abandoned": True}, 126) == "policy"
    assert J.account_ending({**base, "ended_on": 50, "household_closed": True}, 126) == "live"
    assert J.account_ending({**base, "ended_on": 50, "ftp_closed": True}, 126) == "ftp"
    assert J.account_ending({**base, "ended_on": 50}, 126) == "horizon"
    assert J.account_ending({**base, "ended_on": 50, "ending": "cap"}, 126) == "cap"
    with pytest.raises(ValueError):
        J.account_ending({**base, "ending": "stolen"}, 126)


def test_a_lifetime_counts_the_payouts_arrived_before_the_end():
    acc = {"activation_day": 10, "ended_on": 60, "closed": True, "arrivals": (30, 45, 60, 70)}
    assert J.account_lifetime(acc, 126) == {"ending": "breach", "lost": True, "payouts": 2, "sessions": 50}
    open_ = {"activation_day": 10, "ended_on": None, "arrivals": (30, 126, 127)}
    assert J.account_lifetime(open_, 126) == {"ending": "window", "lost": False, "payouts": 2, "sessions": 116}


def test_kaplan_meier_by_hand_from_the_definition():
    """(31), from MEASURES.md's definition (B-2, corrective cycle 1): S(k) is the chance an account reaches its k-th
    payout before loss, and censored accounts leave the risk set at their count -- the step k -> k + 1's risk set is
    the accounts with more than k payouts plus those lost at k. Lost at 0, lost at 1, censored at 1, lost at 2,
    censored at 3:
    * step 0: 4 above 0 and 1 lost at 0 at risk, 1 lost -> S(1) = 4/5;
    * step 1: 2 above 1 (2, 3) and 1 lost at 1, 1 lost -> S(2) = 4/5 x 2/3 = 8/15 (the censored account at 1 is out);
    * step 2: 1 above 2 and 1 lost at 2, 1 lost -> S(3) = 4/15; step 3: none at risk -> S(4) = 4/15.
    The median is 2 (S(3) <= 1/2 < S(2)), the p10 0, the p90 beyond. The rule before the fix (a censored account in
    the risk set of its own step) gives S(2) = 0.6 here and fails this test."""
    curve = J.km_survival([0, 1, 1, 2, 3], [True, True, False, True, False])
    s = dict(curve)
    assert s[0] == 1.0 and s[1] == pytest.approx(4 / 5) and s[2] == pytest.approx(8 / 15)
    assert s[3] == pytest.approx(4 / 15) and s[4] == pytest.approx(4 / 15)
    assert J.km_quantile(curve, 0.5) == 2.0 and J.km_quantile(curve, 0.1) == 0.0
    assert math.isnan(J.km_quantile(curve, 0.9))


def test_red_team_the_twelve_accounts():
    """B-2's failing input: 4 lost with 0 payouts, 4 still open with 0, 2 lost with 1, 2 open with 1 (equal weights).
    Step 0's risk set is the 4 above 0 and the 4 lost at 0 -- the 4 open at 0 are out -- so S(1) = 1/2 and the median
    is 0 payouts (the rule before the fix: S(1) = 2/3, median 1). Through `funded_lifetime` too, one unit an account."""
    t = [0] * 4 + [0] * 4 + [1] * 2 + [1] * 2
    e = [True] * 4 + [False] * 4 + [True] * 2 + [False] * 2
    curve = J.km_survival(t, e)
    assert dict(curve)[1] == pytest.approx(0.5) and J.km_quantile(curve, 0.5) == 0.0
    lost0 = {"activation_day": 1, "ended_on": 5, "closed": True, "arrivals": ()}
    open0 = {"activation_day": 1, "ended_on": None, "arrivals": ()}
    lost1 = {"activation_day": 1, "ended_on": 9, "closed": True, "arrivals": (4,)}
    open1 = {"activation_day": 1, "ended_on": None, "arrivals": (4,)}
    units = [[lost0]] * 4 + [[open0]] * 4 + [[lost1]] * 2 + [[open1]] * 2
    r = J.funded_lifetime(units, 126)
    assert dict(r["curve_payouts"])[1] == pytest.approx(0.5) and r["p50"] == 0.0


def test_the_sessions_curve_keeps_the_clock_tie_rule():
    """(31)'s reading beside, in sessions alive, is a time on a clock: a censoring at t outlives an event at t (the
    usual convention, stated in `km_survival`). On the hand case that is S(2) = 4/5 x 3/4 = 0.6."""
    curve = J.km_survival([0, 1, 1, 2, 3], [True, True, False, True, False], censored_leave_at_count=False)
    s = dict(curve)
    assert s[1] == pytest.approx(0.8) and s[2] == pytest.approx(0.6) and s[3] == pytest.approx(0.3)
    a = {"activation_day": 0, "ended_on": 10, "closed": True, "arrivals": ()}
    b = {"activation_day": 0, "ended_on": None, "arrivals": ()}
    r = J.funded_lifetime([[a], [b]], 10)                  # both 10 sessions alive: the censored one outlives the loss
    assert dict(r["curve_sessions"])[11] == pytest.approx(0.5)


def test_the_lifetime_weights_each_unit_equally_and_names_every_censored_ending():
    """Unit A holds two accounts, both lost before a payout; unit B one, still open with five: each unit weighs one,
    so S(1) = 1/2 (not 1/3, the accounts' count)."""
    a = [{"activation_day": 1, "ended_on": 5, "closed": True, "arrivals": ()}] * 2
    b = [{"activation_day": 1, "ended_on": None, "arrivals": (10, 20, 30, 40, 50)}]
    r = J.funded_lifetime([a, b], 126)
    assert dict(r["curve_payouts"])[1] == pytest.approx(0.5)
    assert r["p50"] == 0.0 and math.isnan(r["p90"]) and r["p90_beyond"]
    assert (r["n_accounts"], r["n_units"], r["n_lost"], r["n_censored"]) == (3, 2, 2, 1)
    assert r["share_censored"] == pytest.approx(1 / 3) and r["share_censored_weighted"] == pytest.approx(0.5)
    assert r["censored_by_kind"] == {"policy": 0, "live": 0, "cap": 0, "window": 1, "horizon": 0}
    assert r["lost_by_kind"] == {"breach": 2, "denied": 0, "ftp": 0}
    late = [{"activation_day": 130, "ended_on": None, "arrivals": ()}]
    assert J.funded_lifetime([late], 126)["n_accounts"] == 0       # activated after the window: not the unit's


# ------------------------------------------------------------------------------------------------ (30), (37) - (39)


DAYS = [
    {"accounts": 3, "taken": ((100.0, 130.0), (120.0, 160.0)), "offered": (100.0, 120.0, 800.0),
     "news": ((900.0, 930.0),)},
    {"accounts": 0, "taken": (), "offered": (700.0,)},
]


def test_workload():
    w = J.workload(DAYS, latency=5.0)
    # day 1: [95, 130] u [115, 160] = 65 minutes; two orders; three accounts. Day 2: nothing.
    assert w == {"orders_mean": 1.0, "orders_max": 2.0, "accounts_mean": 1.5, "accounts_max": 3.0,
                 "screen_hours_mean": pytest.approx(65 / 120), "screen_hours_max": pytest.approx(65 / 60)}
    with pytest.raises(ValueError):
        J.workload([{"accounts": 0, "taken": ((1.0, 2.0),)}], 5.0)


def test_supply():
    s = J.supply(DAYS)
    assert s == {"offered_mean": 2.0, "taken_mean": 1.0, "taken_per_account_mean": pytest.approx(2 / 3),
                 "sessions_without_account": 1}


def test_coverage():
    c = J.coverage(DAYS, {"early": (0.0, 600.0), "late": (600.0, 1330.0)})
    assert c == {"taken_early": 0.5, "offered_early": 0.5, "taken_late": 0.0, "offered_late": 1.0}


def test_idle():
    r = J.idle(DAYS, 1330.0)
    # day 1: positions [100, 160] -> idle 1170 (160 .. 1330); with the news window out: 740 (160 .. 900); signals at
    # 100, 120, 800 -> 680 (120 .. 800). Day 2: no trade -> 1330; signal at 700 -> 700.
    assert (r["idle_max"], r["idle_median"]) == (1330.0, (1170.0 + 1330.0) / 2)
    assert r["idle_tradeable_max"] == 1330.0 and r["idle_tradeable_median"] == (740.0 + 1330.0) / 2
    assert r["no_signal_median"] == (680.0 + 700.0) / 2 and r["no_signal_max"] == 700.0


def test_the_trading_day_opens_the_evening_before():
    assert J.trading_day_of(date(2024, 3, 4), 18 * 60, 1020, 1330) == (date(2024, 3, 5), 60.0)
    assert J.trading_day_of("2024-03-05", 9 * 60 + 30, 1020, 1330) == (date(2024, 3, 5), 990.0)
    with pytest.raises(ValueError):
        J.trading_day_of("2024-03-05", 16 * 60, 1020, 1330)            # between the flat and the reopen


def test_the_firms_day_comes_from_its_verified_rules():
    d = J.firm_day()
    assert (d["reopen"], d["flat"], d["length"]) == (17 * 60, 15 * 60 + 10, 22 * 60 + 10)


# ------------------------------------------------------------------------------------------------ 1.4, (34)


def test_the_three_coin_readings_by_hand():
    x = np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0]])
    r = J.coin_readings(x, lag=1)
    assert r["r1_p50"] == 2.5
    assert r["r2_median_day_p10"] == pytest.approx(2.1) and r["r2_median_day_p90"] == pytest.approx(2.9)
    assert r["r2_spread_p10"] == pytest.approx(0.8) and r["r2_spread_p90"] == pytest.approx(0.8)
    assert (r["r3_p10"], r["r3_p50"], r["r3_p90"]) == (pytest.approx(2.1), 2.5, pytest.approx(2.9))
    s = J.coin_readings(np.array([[1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]), share=True, lag=1)
    assert s["r1_share"] == 0.5 and s["r2_q_p50"] == 0.5 and s["r3_p50"] == 0.5
    with pytest.raises(ValueError):
        J.coin_readings(np.array([[0.5, 1.0]]), share=True)
    d = J.design_coin_readings(x, np.mean)
    assert d["r1"] == 2.5 and d["r3_p50"] == 2.5 and "r2_median_day_p10" not in d


def test_the_variance_decomposition_by_hand():
    v = J.variance_decomposition(np.array([[1.0, 3.0], [5.0, 7.0]]))
    assert v["within"] == 2.0 and v["between"] == 7.0 and v["share_start_day"] == pytest.approx(7 / 9)
    flat = J.variance_decomposition(np.array([[0.0, 2.0], [2.0, 0.0]]))
    assert flat["between"] < 0 and flat["share_start_day"] == 0.0 and flat["share_start_day_raw"] < 0


# ------------------------------------------------------------------------------------------------ (32), (33)


def test_the_worst_year_on_one_year_set():
    r = J.by_year([1.0, 2.0, -3.0, 5.0], [2020, 2020, 2021, 2022], np.mean, bad="low")
    assert r["worst"] == -3.0 and r["worst_year"] == 2021 and r["years"] == [2020, 2021, 2022]
    assert J.by_year([1.0, 2.0], [2020, 2021], np.mean, bad="high", year_set=[2020])["worst_year"] == 2020
    assert J.subset_reading([1.0, 2.0, 3.0], [True, False, True], np.mean) == {"value": 2.0, "n": 2}


def test_the_break_even_denial_rate():
    g = [0.0, 0.10, 0.25, 0.50]
    assert J.break_even_denial_rate(g, [0.7, 0.6, 0.4, 0.3]) == {"p_star": pytest.approx(0.175), "status": "crossed"}
    assert J.break_even_denial_rate(g, [0.5, 0.6, 0.7, 0.8]) == {"p_star": 0.0, "status": "at_zero"}
    un = J.break_even_denial_rate(g, [0.9, 0.8, 0.7, 0.6])
    assert un["status"] == "untested" and math.isnan(un["p_star"])
    # not monotone: the first crossing in grid order
    assert J.break_even_denial_rate(g, [0.7, 0.4, 0.6, 0.3])["p_star"] == pytest.approx(0.1 * 0.2 / 0.3)
    assert J.exposed_share([4, 6], [1, 1]) == 0.2 and math.isnan(J.exposed_share([0], [0]))
