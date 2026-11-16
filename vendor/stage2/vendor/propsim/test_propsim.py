"""Golden-path tests for the Gate-1 engine. Run: python -m pytest test_propsim.py -q"""
import numpy as np
import pytest
from propsim import (Rules, Policy, ScriptedDraw, simulate_combine, simulate_xfa,
                     summarize_combine, summarize_xfa)

R = Rules()


def combine(script, **pol):
    p = Policy(rr=1, risk=1, trades_per_day=max(len(d) for d in script), **pol)
    return simulate_combine(R, p, 0.0, 1, draw=ScriptedDraw(script), max_days=len(script))


def xfa(script, path="standard", **pol):
    p = Policy(rr=1, risk=1, trades_per_day=max(len(d) for d in script), payout_path=path, **pol)
    return simulate_xfa(R, p, 0.0, 1, draw=ScriptedDraw(script), horizon_days=len(script))


# ---------- Combine ----------

def test_two_day_minimal_pass():
    # +1650 then +1350: best day 1650 -> target_eff = 1650/0.55 = 3000 exactly -> pass
    r = combine([[1650], [1350]])
    assert r["passed"][0] and r["pass_day"][0] == 1
    # floor after day-1 lock = 1650 - 2000 = -350; after day-2 lock min(0, 1000) = 0 (official lock)
    assert r["F"][0] == pytest.approx(0)


def test_single_day_3000_does_not_pass():
    r = combine([[3000]])
    assert not r["passed"][0]
    # target_eff = 3000/0.55 = 5454.54...; floor ratchets to min(0, +1000) = 0
    assert r["F"][0] == pytest.approx(0)


def test_best_day_trap_needs_5455():
    r = combine([[3000], [1000], [1000], [400]])
    assert not r["passed"][0]          # B = 5400 < 5454.5
    r = combine([[3000], [1000], [1000], [500]])
    assert r["passed"][0] and r["pass_day"][0] == 3   # B = 5500 >= 5454.5


def test_three_days_1000_passes_at_3000():
    r = combine([[1000], [1000], [1000]])
    assert r["passed"][0] and r["pass_day"][0] == 2


def test_trailing_floor_kills_at_zero():
    # +2000 -> floor ratchets to 0 at lock; next day -2000 -> B=0 <= F=0 -> fail
    r = combine([[2000], [-2000]])
    assert r["failed"][0] and r["fail_day"][0] == 1


def test_intraday_breach_before_lock():
    # day 1: -1000, -1000 -> B=-2000 <= -2000 -> fail on second trade of day 0
    r = combine([[-1000, -1000]])
    assert r["failed"][0] and r["fail_day"][0] == 0 and r["trades"][0] == 2


def test_no_ratchet_intraday():
    # +2000 then -1500 same day: floor is still -2000 at that moment -> survive
    r = combine([[2000, -1500]])
    assert not r["failed"][0]
    assert r["F"][0] == pytest.approx(500 - 2000)  # lock: max(-2000, 500-2000) = -1500


def test_subscription_billing():
    script = [[0.0]] * 22   # 22 flat days
    r = combine(script)
    assert r["sub_fees"][0] == pytest.approx(98)   # day 0 and day 21


def test_stop_day_on_win():
    p = Policy(rr=1, risk=100, trades_per_day=3, stop_day_on_win=True)
    r = simulate_combine(R, p, 0.0, 1, draw=ScriptedDraw([[100, -100, -100]]), max_days=1)
    assert r["trades"][0] == 1 and r["B"][0] == pytest.approx(100)


# ---------- XFA ----------

def test_xfa_standard_first_payout_and_floor_jump():
    r = xfa([[300]] * 5 + [[-750]])
    # after 5 winning days: B=1500, allowed=min(750, 2000)=750 -> paid at day 4 lock
    assert r["first_payout_day"][0] == 4
    assert r["gross_paid"][0] == pytest.approx(750)
    assert r["cash"][0] == pytest.approx(675)
    # floor -> 0, balance 750; day 5: -750 -> B=0 <= 0 -> closed
    assert r["closed"][0]


def test_xfa_standard_ratchet_before_payout():
    r = xfa([[300]] * 4)
    assert r["F"][0] == pytest.approx(1200 - 2000)   # -800
    assert r["gross_paid"][0] == 0


def test_xfa_winning_day_threshold():
    r = xfa([[149]] * 6)
    assert r["gross_paid"][0] == 0                 # 149 < 150 -> not winning days
    r = xfa([[150]] * 5)
    assert r["gross_paid"][0] == pytest.approx(375)  # B=750 -> 375 allowed >= 125


def test_xfa_payout_min_blocks_small_balance():
    r = xfa([[150]] * 5 + [[-600]] * 0)
    assert r["gross_paid"][0] == pytest.approx(375)
    # 5 winning days of +150 with prior loss: B too small -> no payout
    r = xfa([[-600]] + [[150]] * 5)
    assert r["gross_paid"][0] == 0                  # B=150 -> allowed 75 < 125


def test_xfa_standard_cap():
    r = xfa([[1000]] * 5)
    assert r["gross_paid"][0] == pytest.approx(2000)   # min(2500, cap 2000)


def test_xfa_consistency_path():
    r = xfa([[400]] * 3, path="consistency")
    # window profit 1200, best 400 = 0.333 <= 0.4, days 3 -> allowed min(600, 3000)
    assert r["first_payout_day"][0] == 2 and r["gross_paid"][0] == pytest.approx(600)
    r = xfa([[1000], [100], [100]], path="consistency")
    assert r["gross_paid"][0] == 0                 # best 1000/1200 > 0.4


def test_xfa_window_restarts_after_payout():
    r = xfa([[300]] * 10)
    assert r["n_payouts"][0] == 2                   # payouts at day 4 and day 9
    assert r["F"][0] == 0


def test_xfa_floor_locks_at_zero_without_payout():
    r = xfa([[1000]] * 3)                           # B=3000, but 3 winning days only
    assert r["F"][0] == pytest.approx(0)            # min(0, 3000-2000) = 0


# ---------- Martingale / optional-stopping bounds at zero edge ----------

def test_combine_pass_rate_bound_and_martingale():
    rng = np.random.default_rng(1)
    for rr, risk in [(1, 250), (2, 100), (0.5, 500), (1, 1000)]:
        p = Policy(rr=rr, risk=risk, trades_per_day=2)
        s = summarize_combine(simulate_combine(R, p, 0.0, 20000, rng))
        assert s["p_unresolved"] == 0
        assert s["p_pass"] <= 0.40 + 4 * s["p_pass_se"], (rr, risk, s["p_pass"])
        assert abs(s["mean_B_final"]) < 60, (rr, risk, s["mean_B_final"])


def test_xfa_fatou_bound():
    rng = np.random.default_rng(2)
    for rr, risk, path in [(1, 300, "standard"), (2, 150, "consistency"), (0.5, 400, "standard")]:
        p = Policy(rr=rr, risk=risk, trades_per_day=2, payout_path=path)
        s = summarize_xfa(simulate_xfa(R, p, 0.0, 20000, rng, horizon_days=250))
        assert s["mean_gross"] <= 2000
        assert s["mean_T"] <= 80, (rr, risk, path, s["mean_T"])


def test_floor_truncation_fixes_overshoot():
    rng = np.random.default_rng(5)
    p = Policy(rr=1, risk=1500, trades_per_day=1)
    r = simulate_combine(Rules(), p, 0.0, 50000, rng)
    assert r["B"][r["failed"]].min() >= -2000 - 1e-6
    s = summarize_combine(r)
    assert s["p_pass"] <= 0.40 + 4 * s["p_pass_se"]
    # gate-1.8 no-MAE variant reproduces the 4/9 artifact
    r2 = simulate_combine(Rules(floor_mode="none"), p, 0.0, 50000, rng)
    assert abs(r2["passed"].mean() - 4/9) < 0.01


def test_resize_mode_bounds():
    rng = np.random.default_rng(9)
    p = Policy(rr=1, risk=1500, trades_per_day=1)
    r = simulate_combine(Rules(floor_mode="resize"), p, 0.0, 50000, rng)  # resize still bounded
    assert r["B"][r["failed"]].min() >= -2000 - 1e-6
    s = summarize_combine(r)
    assert s["p_pass"] <= 0.40 + 4 * s["p_pass_se"] and abs(s["mean_B_final"]) < 60


def test_lifecycle_horizon_binds():
    from propsim import simulate_lifecycle
    rng = np.random.default_rng(11)
    p = Policy(rr=1, risk=100, trades_per_day=1)
    L = simulate_lifecycle(Rules(), p, 0.0, 2000, rng, total_days=30)
    assert L["p_unresolved"] > 0.5          # $100 1/day cannot resolve in 30 days
    assert L["mean_sub_fees"] <= 98 + 1e-9  # days 0 and 21 only


def test_mae_law_reproduces_truncation():
    """Generator-side MAE sampling must give P(win | room c) = c/(c+W)."""
    from propsim import sample_mae_given_win, mae_survival_given_win
    rng = np.random.default_rng(21)
    r, W, n = 1500.0, 1500.0, 400000
    win = rng.random(n) < r / (r + W)                 # untruncated fair coin
    mae = np.where(win, sample_mae_given_win(rng, n, r, W), r)
    for c in [100.0, 500.0, 1000.0, 1500.0]:
        p_win_room = (win & (mae < c)).mean()
        assert abs(p_win_room - c / (c + W)) < 0.004, (c, p_win_room)
    # closed form sanity at the ends
    assert mae_survival_given_win(0.0, r, W) == 1.0 and mae_survival_given_win(r, r, W) == 0.0


def test_drift_convention_matches_edge_definition_at_own_stop():
    from propsim import theta_from_edge, p_race
    for rr, risk, e in [(1, 1500, 0.05), (3, 500, 0.02), (0.5, 1000, -0.05), (2, 300, -0.10)]:
        W = rr * risk
        th = theta_from_edge(risk, W, e)
        assert abs(float(p_race(risk, W, th)) - (1 + e) / (1 + rr)) < 1e-10


def test_drift_vs_linear_agree_to_second_order():
    from propsim import theta_from_edge, p_race
    worst = 0.0
    for rr in [0.5, 1, 1.5, 2, 3]:
        for e in [-0.10, -0.05, 0.02, 0.05]:
            risk, W = 1000.0, rr * 1000.0
            th = theta_from_edge(risk, W, e)
            for c in [50.0, 200.0, 500.0, 900.0]:
                worst = max(worst, abs(float(p_race(c, W, th)) - (1 + e) * c / (c + W)))
    assert worst < 2e-3, worst   # far inside Monte-Carlo noise at N = 1e4


def test_mae_law_with_drift_reproduces_race():
    from propsim import theta_from_edge, p_race, sample_mae_given_win
    rng = np.random.default_rng(31)
    r, W, e, n = 1500.0, 1500.0, 0.05, 400000
    th = theta_from_edge(r, W, e)
    win = rng.random(n) < (1 + e) / 2
    mae = np.where(win, sample_mae_given_win(rng, n, r, W, th), r)
    for c in [100.0, 500.0, 1000.0]:
        assert abs((win & (mae < c)).mean() - float(p_race(c, W, th))) < 0.004


def test_liquidation_identity_closed_form():
    """P(win) * P(MAE < c | win) == p_race(c, W, theta) exactly, for all theta, r, W, c."""
    from propsim import mae_survival_given_win, p_race
    worst = 0.0
    for r in [300.0, 1000.0, 1500.0]:
        for R in [0.5, 1.0, 2.0, 3.0]:
            W = R * r
            for theta in [-3e-4, -5e-5, 0.0, 5e-5, 3e-4]:
                c = np.linspace(1.0, r - 1.0, 25)
                lhs = float(p_race(r, W, theta)) * (1.0 - mae_survival_given_win(c, r, W, theta))
                rhs = p_race(c, W, theta)
                worst = max(worst, float(np.max(np.abs(lhs - rhs))))
    assert worst < 1e-12, worst


def test_theta_solver_raises_on_bad_edge_and_is_stable_at_large_r():
    from propsim import theta_from_edge, p_race
    import pytest
    with pytest.raises(ValueError):
        theta_from_edge(1000.0, 1000.0, 1.5)        # p would exceed 1
    th = theta_from_edge(1500.0, 4500.0, 0.05)
    assert abs(th - 2.1987e-5) < 2e-8                # side-session spot check
    assert abs(float(p_race(1500.0, 4500.0, th)) - 1.05 / 4) < 1e-12


def test_combine_floor_locks_at_zero():
    # +3000 in one day: target inflates to 5454.5; official rule locks the floor at 0, not +1000
    r = combine([[3000]])
    assert r["F"][0] == pytest.approx(0.0)
    r = simulate_combine(Rules(combine_mll_lock_at=None), Policy(rr=1, risk=1, trades_per_day=1), 0.0, 1,
                         draw=ScriptedDraw([[3000]]), max_days=1)
    assert r["F"][0] == pytest.approx(1000.0)


def test_combine_1500_exact_markov_chain():
    """Static 1:1 $1,500, 1 trade/day, truncate, zero edge. Reachable states before pass:
    a=(0,-2000) b=(1500,-500) c=(0,-500) d=(-1500,-2000).
    b = 1/2 + c/2, c = b/4, d = a/4, a = b/2 + d/2  ->  a = 16/49."""
    rng = np.random.default_rng(77)
    r = simulate_combine(Rules(), Policy(rr=1, risk=1500, trades_per_day=1), 0.0, 200000, rng)
    p = r["passed"].mean()
    assert abs(p - 16 / 49) < 3 * np.sqrt(p * (1 - p) / 200000)


def test_xfa_payout_fee_and_profit_since_payout():
    rules = Rules(payout_fee=30.0, require_profit_since_payout=True)
    p = Policy(rr=1, risk=1, trades_per_day=1, payout_path="standard")
    # 5 winning days -> payout 750 (cash 675-30). Then 5 more winning days but net since payout
    # is negative (one -900 day in between) -> no second payout until profitable since payout.
    script = [[500]] * 5 + [[-1000]] + [[150]] * 5
    # payout 1250 at day 4 (cash 1125 - 30); then -1000, then +750: net since payout = -250 -> blocked
    r = simulate_xfa(rules, p, 0.0, 1, draw=ScriptedDraw(script), horizon_days=len(script))
    assert r["n_payouts"][0] == 1 and r["cash"][0] == pytest.approx(1095.0)
    r2 = simulate_xfa(Rules(payout_fee=30.0), p, 0.0, 1, draw=ScriptedDraw(script), horizon_days=len(script))
    assert r2["n_payouts"][0] == 2


# ---------- R-9 (RECONCILIATION.md): payout request day is excluded from the next cycle ----------

def test_r9_payout_day_not_counted_in_next_cycle():
    # Payout requested at the lock of the 5th winning day (day index 4). That day must not count toward the next 5.
    r = xfa([[300]] * 9)                            # days 5..8 = only 4 new winning days
    assert r["first_payout_day"][0] == 4
    assert r["n_payouts"][0] == 1
    r = xfa([[300]] * 10)                           # day 9 is the 5th new winning day -> second payout
    assert r["n_payouts"][0] == 2
    # Convention: propsim requests at the 16:00 CT lock of the eligibility day, i.e. before 17:00 CT,
    # so the "after 5 PM belongs to the next trading day" case (8284233) never arises in this engine.


# ---------- keep_balance payout policy (D-45) ----------

def test_keep_balance_caps_request_and_defers_first_payout():
    # 5 x +300: B = 1500 at day 4, allowed = 750. With a $1,000 buffer the request is min(750, 1500 - 1000) = 500.
    r = xfa([[300]] * 5, keep_balance=1000.0)
    assert r["first_payout_day"][0] == 4
    assert r["gross_paid"][0] == pytest.approx(500)
    assert r["B"][0] == pytest.approx(1000)
    # With a $1,400 buffer the request would be 100 < $125 minimum -> no payout yet (deferred)
    r = xfa([[300]] * 5, keep_balance=1400.0)
    assert r["gross_paid"][0] == 0
    # Default (0) leaves the original behaviour untouched
    r = xfa([[300]] * 5)
    assert r["gross_paid"][0] == pytest.approx(750)
