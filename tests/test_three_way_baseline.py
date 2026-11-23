"""Q-185c: the firm path's baseline mode (`extended/three_way_baseline.py`). Synthetic; no bar, no result.

In this process (no engine): the facts' refusals and admissions (a same-bar fill at its limit; a move bar at the fill
refused; a move bar at or after the limit no move, C2-10); FV3's target rounding; the wrapper's delegation; the refusals
of a trade without an R (C2-6), a fact that does not match the trade handed out (C2-8), a trade with no fee to charge (C2-2), a stretch exit; a need-aware exit raced at the as-placed target at the
state's R, never `rr_used` (C2-1); the fee taken from the engine at size (C2-2); the ledger's historical fields marked
not applicable (C2-7); the volatility at the alert unchanged by any bar after it (N-6); two trades at one moment
drawing independent outcomes (the lead's amendment to C2-9); the rungs of one alert each on its own law, one side,
a second on a lane refused, and overlapping positions counted beside (the lead's ruling on C3-2). In its own process
(`tests/three_way_baseline_checks.py`): the vendored identity through passes and funded accounts, the rebooked
identity, the reflected as-walked reading, the independent oracle re-booking every race-arm row, the daily loss limit's day end, the counts beside.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from extended import three_way_baseline as TB
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_seeds as S

ROOT = Path(__file__).resolve().parent.parent
SEED = S.issue("tests")
PART = S.PARTS["tests"]


def _facts(**kw):
    base = dict(decision=935, entry=940, stop_ticks=40, tick_value=0.5, kinds={1.5: "t", 2.0: "s"}, limit=1330,
                sigma=1.5, fee_per_contract=0.0)
    base.update(kw)
    return TB.TradeFacts(**base)


def test_the_facts_refuse_and_admit():
    _facts(entry=1330, limit=1330)                                 # a fill at its own limit: a same-bar exit admitted
    with pytest.raises(ValueError, match="in order"):
        _facts(entry=1331)
    with pytest.raises(ValueError, match="in order"):
        _facts(decision=941)                                       # the alert after the fill
    with pytest.raises(ValueError, match="move bar comes after"):
        _facts(be_open=940)                                        # C2-3's B14: a move bar at the fill
    with pytest.raises(ValueError, match="historical breakeven"):
        _facts(kinds={2.0: "b"})                                   # a breakeven needs its move bar
    with pytest.raises(ValueError, match="historical breakeven"):
        _facts(kinds={2.0: "b"}, be_open=1201, limit=1201)         # C2-10: at the limit is no move
    assert not _facts(be_open=1201, limit=1150).has_move and not _facts(be_open=1201, limit=1201).has_move
    assert _facts(kinds={2.0: "b"}, be_open=1201).has_move
    with pytest.raises(ValueError, match="not in"):
        _facts(kinds={2.0: "x"})


def test_fv3s_target_rounding():
    assert TB.target_ticks(1.5, 40) == 60 and TB.target_ticks(0.25, 50) == 12 and TB.target_ticks(2.75, 100) == 275


class _Inner:
    settlement = "mae"

    def __init__(self, **lt):
        self.last_trade = {"historical_day": 0, "trade_index": 0, "realised_risk": 20.0, "rr": 1.5, "contracts": 1,
                           "risk_per_contract": 20.0, "u": 0.7, "mae": 0.2, **lt}
        self.key = ("combine", 0)

    def can_take(self, *a):
        return "inner"

    def __call__(self, n, day, slot, cushion, **kw):
        self.kw = kw
        return np.array([5.0])


class _Block:
    entry_t = np.array([940.0, 940.0])


def _unit(facts, arm=J.ArmSpec()):
    coins = J.CoinLanes(SEED, PART, 0, 0, [0], None, False)
    return TB._Unit(facts, [_Block()], 0, coins, arm)


def _u_race(decision=935):
    return float(K.uniforms(K.Unit(SEED, PART, 0, 0, 0).coin_key(K.moment(0, decision, 0), K.RACE), 1)[0])


def test_raceover_is_the_vendored_draw_but_its_pnl():
    inner = _Inner()
    w = TB.RaceOver(inner, None, 0, "vendored", None, None)
    assert w.settlement == "mae" and w.can_take() == "inner" and w(1, 0, 0, np.array([100.0]))[0] == 5.0
    w.target_risk = 7.0
    assert inner.target_risk == 7.0                                # a setting reaches the vendored draw
    with pytest.raises(ValueError, match="no facts"):
        TB.RaceOver(_Inner(), _unit({}), 0, "race", None, None)(1, 0, 0, np.array([100.0]))
    # no costs, $0.50 a tick of the position (20 / 40): G = 60 ticks ($30), L = min($20, the room $100) = $20, p = 0.4
    inner = _Inner()
    out = TB.RaceOver(inner, _unit({(0, 0): _facts()}), 0, "race", None, None)(1, 0, 0, np.array([100.0]))[0]
    assert out == (30.0 if _u_race() < 0.4 else -20.0)
    lt = inner.last_trade                                          # C2-7: the historical fields not applicable
    assert lt["u"] is None and lt["mae"] is None and lt["race_law"] == "race" and lt["race_R"] == 1.5


def test_the_refusals():
    with pytest.raises(ValueError, match="C2-6"):                  # no R: refused, no fallback
        TB.RaceOver(_Inner(rr=None), _unit({(0, 0): _facts()}), 0, "race", None, None)(1, 0, 0, np.array([100.0]))
    with pytest.raises(ValueError, match="C2-8"):                  # the stop is not the trade's
        TB.RaceOver(_Inner(risk_per_contract=25.0), _unit({(0, 0): _facts()}), 0, "race", None, None)(
            1, 0, 0, np.array([100.0]))
    with pytest.raises(ValueError, match="C2-8"):                  # the fill is not the trade's
        TB.RaceOver(_Inner(), _unit({(0, 0): _facts(entry=941, decision=936)}), 0, "race", None, None)(
            1, 0, 0, np.array([100.0]))
    with pytest.raises(ValueError, match="C2-2"):                  # no fee reported and none a contract
        TB.RaceOver(_Inner(), _unit({(0, 0): _facts(fee_per_contract=None)}), 0, "race", None, None)(
            1, 0, 0, np.array([100.0]))
    with pytest.raises(ValueError, match="stretch"):
        TB.RaceOver(_Inner(), _unit({(0, 0): _facts()}), 0, "race", None, None)(
            1, 0, 0, np.array([100.0]), need=5.0, stretch=True)


def test_two_trades_at_one_moment_draw_independent_outcomes():
    """The lead's amendment to C2-9: P-14's two rungs from one alert take sub 0 and 1 in index order, so each reads its
    own uniform -- here on 64 lanes the two trades' race uniforms differ lane for lane and are not one stream."""
    facts = {(0, 0): _facts(), (0, 1): _facts()}                       # one alert, one fill: one moment
    lanes = 64
    coins = J.CoinLanes(SEED, PART, 0, 0, range(lanes), None, False)
    unit = TB._Unit(facts, [_Block()], 0, coins, J.ArmSpec())
    assert unit.subs == {(0, 0): 0, (0, 1): 1}
    lt = {"risk_per_contract": 20.0}
    k0, k1 = unit.key(0, 0, lt)[0], unit.key(0, 1, lt)[0]
    assert k0.moment != k1.moment and k1.moment == K.moment(0, 935, 1)
    u0 = np.array([unit.uniform(k0, K.RACE, j) for j in range(lanes)])
    u1 = np.array([unit.uniform(k1, K.RACE, j) for j in range(lanes)])
    assert not np.any(u0 == u1)
    assert abs(float(np.corrcoef(u0, u1)[0, 1])) < 0.5                # no shared stream
    w0 = u0 < 0.4
    w1 = u1 < 0.4
    assert np.any(w0 != w1)                                            # the outcomes differ on some lanes


def test_a_need_that_does_not_bind_races_at_the_states_r_never_rr_used():
    """C3-1: the state's R 2.0, the history's rr_used 1.5, kinds that differ in law at the two Rs; a need of $100 does not
    bind (its target (100 + 0 + 0) / 0.5 = 200 ticks lies beyond 2.0's 80): G is 80, the law the race, p = 20 / (20 + 40)."""
    inner = _Inner(rr=2.0, rr_used=1.5, need=100.0, at_need=False)
    log: list = []
    w = TB.RaceOver(inner, _unit({(0, 0): _facts(kinds={1.5: "f", 2.0: "t"})}), 0, "race", log, None)
    out = w(1, 0, 0, np.array([100.0]), need=100.0)[0]
    r = log[0]
    assert r["G"] == 80.0 and r["law"] == "race" and abs(r["p"] - 1.0 / 3.0) < 1e-12
    assert out == (40.0 if _u_race() < 1.0 / 3.0 else -20.0)
    assert inner.last_trade["rr_used"] is None and inner.last_trade["at_need"] is False    # C3-3


def test_a_need_at_or_below_zero_caps_nothing():
    """C3-4: as the engine treats it (`_need_exit` at need <= 0): no cap, the plain race at the state's R."""
    for need in (0.0, -0.5, -5.0):
        log: list = []
        TB.RaceOver(_Inner(need=need), _unit({(0, 0): _facts()}), 0, "race", log, None)(
            1, 0, 0, np.array([100.0]), need=need)
        assert log[0]["G"] == 60.0 and abs(log[0]["p"] - 0.4) < 1e-12, (need, log[0])


def test_the_move_bar_is_s_plus_one():
    """C3-10: be_open is the next FV3 open's end index (s + 1), or None for a walk with no move; refused otherwise."""
    assert TB.move_bar(940) == 1201 and TB.move_bar(10) == 121 and TB.move_bar(1200) is None
    _facts(be_open=1201)
    with pytest.raises(ValueError, match="C3-10"):
        _facts(be_open=1202)                                       # the vendored "first recorded bar": refused
    with pytest.raises(ValueError, match="C3-10"):
        _facts(be_open=1200)                                       # the open itself, one minute short
    _facts(be_open=None)


def test_rungs_of_one_alert_book_alone_on_one_side_and_a_second_on_a_lane_is_refused():
    """The lead's ruling on C3-2: an alert is (block day, alert minute, market), the market the key's underlying code
    (NQ and MNQ are one; N-2); every rung books on its own single-trade law at its own sub; the side at the alert's
    sub 0; a lane handed a second rung of one alert is refused, never booked."""
    facts = {(0, 0): _facts(), (0, 1): _facts(stop_ticks=80, underlying="MNQ")}
    coins = J.CoinLanes(SEED, PART, 0, 0, [0], None, False)
    unit = TB._Unit(facts, [_Block()], 0, coins, J.ArmSpec())
    assert unit.alerts == {(0, 935, 1): [(0, 0), (0, 1)]} and unit.rung_alerts(0, 1) == 1 and unit.rung_alerts(1, 5) == 0
    assert unit.alert_key(0, facts[(0, 1)]).moment == unit.alert_key(0, facts[(0, 0)]).moment == K.moment(0, 935, 0)
    with pytest.raises(ValueError, match="no key code"):
        TB._Unit({(0, 0): _facts(underlying="ES")}, [_Block()], 0, coins, J.ArmSpec())
    # each rung alone on a lane: its own single-trade race at its own sub (rung 1: d = 20 / 80, G 120 ticks = $30, p 0.4)
    log: list = []
    out0 = TB.RaceOver(_Inner(), unit, 0, "race", log, None)(1, 0, 0, np.array([100.0]))[0]
    out1 = TB.RaceOver(_Inner(trade_index=1, risk_per_contract=40.0), unit, 0, "race", log, None)(
        1, 0, 0, np.array([100.0]))[0]
    u1 = float(K.uniforms(K.Unit(SEED, PART, 0, 0, 0).coin_key(K.moment(0, 935, 1), K.RACE), 1)[0])
    assert out0 == (30.0 if _u_race() < 0.4 else -20.0) and out1 == (30.0 if u1 < 0.4 else -20.0)
    assert [r["law"] for r in log] == ["race", "race"] and abs(log[1]["p"] - 0.4) < 1e-12
    # one lane's two accounts share its book: the second rung is refused before anything is booked
    for mode in ("race", "as_walked", "rebooked", "vendored"):
        book: dict = {"alerts": set(), "held": {}}
        log = []
        f2 = {k: TB.TradeFacts(**{**v.__dict__, "walked": {1.5: 10.0, 2.0: 10.0}}) for k, v in facts.items()}
        u2 = TB._Unit(f2, [_Block()], 0, coins, J.ArmSpec())
        TB.RaceOver(_Inner(), u2, 0, mode, log, None, book)(1, 0, 0, np.array([100.0]))
        with pytest.raises(ValueError, match="second rung"):
            TB.RaceOver(_Inner(trade_index=1, risk_per_contract=40.0), u2, 0, mode, log, None, book)(
                1, 0, 0, np.array([100.0]))
        assert len(log) == (0 if mode == "vendored" else 1), (mode, log)
    # the second rung alone on a lane takes the alert's one side: the SIDE coin at sub 0, never its own sub's
    log = []
    f2 = {k: TB.TradeFacts(**{**v.__dict__, "walked": {1.5: 10.0, 2.0: 10.0}}) for k, v in facts.items()}
    TB.RaceOver(_Inner(trade_index=1, risk_per_contract=40.0), TB._Unit(f2, [_Block()], 0, coins, J.ArmSpec()), 0,
                "as_walked", log, None)(1, 0, 0, np.array([100.0]))
    us = [float(K.uniforms(K.Unit(SEED, PART, 0, 0, 0).coin_key(K.moment(0, 935, b), K.SIDE), 1)[0]) for b in (0, 1)]
    assert (us[0] < 0.5) != (us[1] < 0.5)                          # the fixture's two subs draw opposite sides
    assert log[0]["side"] == (1.0 if us[0] < 0.5 else -1.0)


class _Held:
    entry_t = np.array([940.0, 950.0, 1000.0])
    exit_by_rr = {1.5: np.array([980.0, 1001.0, 1010.0])}


def test_overlapping_positions_are_counted_beside():
    """N-5: per lane, a booked position entered on a market while another of the lane's there is held (to its
    historical exit at its R) is counted; one entered after every other's exit is not."""
    facts = {(0, 0): _facts(), (0, 1): _facts(decision=945, entry=950), (0, 2): _facts(decision=995, entry=1000)}
    coins = J.CoinLanes(SEED, PART, 0, 0, [0], None, False)
    unit = TB._Unit(facts, [_Held()], 0, coins, J.ArmSpec())
    assert unit.rung_alerts(0, 1) == 0                              # three alerts of one trade each
    for mode in ("race", "vendored"):
        book: dict = {"alerts": set(), "held": {}}
        counts: dict = {}
        seen = []
        for j in range(3):
            TB.RaceOver(_Inner(trade_index=j), unit, 0, mode, None, counts, book)(1, 0, 0, np.array([100.0]))
            seen.append(counts.get("overlaps", 0))
        assert seen == [0, 1, 2], mode           # 950 inside (940, 980); 1000 inside (950, 1001)
        counts, book = {}, {"alerts": set(), "held": {}}             # the engine's order is not the fills' order
        for j in (2, 0, 1):
            TB.RaceOver(_Inner(trade_index=j), unit, 0, mode, None, counts, book)(1, 0, 0, np.array([100.0]))
        assert counts["overlaps"] == 2, (mode, counts)
    # a trade the race leaves untaken (a missed signal) holds no position: nothing counted
    missed = TB._Unit(facts, [_Held()], 0, coins, J.ArmSpec(missed_q=0.999999))
    counts, book, log = {}, {"alerts": set(), "held": {}}, []
    for j in range(3):
        TB.RaceOver(_Inner(trade_index=j), missed, 0, "race", log, counts, book)(1, 0, 0, np.array([100.0]))
    assert [r["law"] for r in log] == ["missed"] * 3 and counts.get("overlaps", 0) == 0, (log, counts)
    assert unit.hold(0, 2, facts[(0, 2)], 1.5) == (1000.0, 1010.0)


def test_a_need_aware_exit_races_at_the_as_placed_target_at_the_states_r():
    # the state's R 2.0 (G 80 ticks) but rr_used 1.5 chosen by the historical outcomes: the race reads rr, and the need
    # of $12 caps the target at (12 + 0 + 0) / 0.5 = 24 ticks
    inner = _Inner(rr=2.0, rr_used=1.5, need=12.0, at_need=True)
    w = TB.RaceOver(inner, _unit({(0, 0): _facts(kinds={1.5: "s", 2.0: "t"})}), 0, "race", [], None)
    out = w(1, 0, 0, np.array([100.0]), need=12.0)[0]
    assert inner.kw == {"need": 12.0}                              # the engine's keyword reaches the vendored draw
    p = 20.0 / (20.0 + 12.0)
    assert out == (12.0 if _u_race() < p else -20.0)               # a win nets exactly the need
    assert inner.last_trade["race_R"] == 2.0 and inner.last_trade["race_need"] == (out == 12.0)


def test_the_fee_is_the_engines_at_size():
    inner = _Inner(fee=3.78, contracts=10)
    log: list = []
    TB.RaceOver(inner, _unit({(0, 0): _facts(e_ticks=1.0)}), 0, "race", log, None)(1, 0, 0, np.array([100.0]))
    assert log[0]["fee"] == 3.78                                    # never 10 x a micro's fee


def test_the_volatility_at_the_alert_reads_no_bar_after_it():
    rng = np.random.default_rng([int(SEED), 46])
    end = np.arange(900, 1000)
    close = np.cumsum(rng.normal(0, 2.0, end.size))
    a = TB.alert_sigma(end, close, 950, 30, 0.25)
    for _ in range(5):
        c2 = close.copy()
        c2[end > 950] = rng.normal(0, 50.0, int((end > 950).sum()))   # every bar after the alert scrambled
        assert TB.alert_sigma(end, c2, 950, 30, 0.25) == a
    c3 = close.copy()
    c3[end == 950] += 7.0                                          # the bar closing at the alert is read
    assert TB.alert_sigma(end, c3, 950, 30, 0.25) != a


@pytest.fixture(scope="module")
def checks() -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "three_way_baseline_checks.py")], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=1500, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_identity_the_vendored_pnl_passed_through_is_customer_slices_replay_bit_for_bit(checks):
    c = checks["identity"]
    assert c["n_diffs"] == 0, c["diffs"]
    assert c["cross_diffs"] > 0 and c["passes"] > 0 and c["funded"] > 0, c    # through passes and funded accounts


def test_rebooked_the_race_arms_costs_rebook_the_vendored_pnl(checks):
    c = checks["rebooked"]
    assert c["compared"] > 50 and c["bad"] == 0, c


def test_as_walked_is_the_reflected_path_on_each_units_side_coin(checks):
    c = checks["as_walked"]
    assert c["rows"] > 100 and c["bad"] == 0, c
    assert c["lanes_differ"] > 0 and 0 < c["long_share"] < 1, c         # it moves with the seed: a reflection


def test_an_independent_oracle_rebooks_every_race_arm_row(checks):
    assert checks["opens"]                                  # FV3_OPENS is the vendored SESSION_OPENS (C3-10)
    for name in ("race", "race_rr2"):
        c = checks[name]
        assert c["rows"] > 200 and c["bad"] == 0 and c["unchecked"] == 0, (name, c)
        assert {"race", "walk", "move", "fill_fail"} <= set(c["laws"]) and c["needs"] > 0, (name, c)
        assert c["hist_fields"] == 0 and c["count_bad"] == 0 and c["overlap"] == 0, (name, c)
        assert c["overlaps"] == 0 == c["held_overlaps"] and c["per_alert_max"] == 1, (name, c)   # the strict rule
        assert c["inputs_bad"] == 0 and c["need_stat_bad"] == 0, (name, c)   # G, L, the move's, the need (C3-5, 8)
        assert c["need_hits"] > 0, (name, c)
    assert {"move", "walk"} <= set(checks["race"]["need_by_law"]) or {"move", "walk"} <= set(
        checks["race_rr2"]["need_by_law"]), checks["race"]["need_by_law"]   # the need hit under the move and walk
    assert checks["race_rr2"]["rr_differs"] > 0             # C3-1: the history's rr_used differs, the race reads rr
    c = checks["race"]
    assert c["be_unrecorded"] > 0 and c["be_differs"] > 0   # C3-10, N-1: counted apart
    assert c["move_trades"] > 0 and c["b_redrawn"] > 0 and c["b_historical"] > 0, c    # C2-4's shares beside


def test_rungs_under_the_strict_rule_book_one_a_lane_each_on_its_own_law(checks):
    """The lead's ruling on C3-2: under the strict rule the router takes at most one rung of an alert on a lane, and the
    oracle re-books every row on its own single-trade law; with the strict rule off the second rung is refused."""
    c = checks["rungs_strict"]
    assert c["rung_alerts"] > 0 and c["per_alert_max"] == 1, c
    assert c["rows"] > 100 and c["bad"] == 0 and c["inputs_bad"] == 0 and c["unchecked"] == 0, c
    assert c["overlaps"] == 0 and c["held_overlaps"] == 0, c
    assert "second rung" in checks["rung_refused"], checks["rung_refused"]


def test_overlapping_positions_off_the_strict_rule_are_counted_beside(checks):
    c = checks["overlap"]
    assert c["overlaps"] > 0 and c["overlaps"] == c["held_overlaps"], c       # N-5: this file's own count
    assert c["rows"] > 100 and c["bad"] == 0 and c["unchecked"] == 0 and c["per_alert_max"] == 1, c


def test_p16s_windows_are_held_before_its_table_loads(checks):
    c = checks["p16_hold"]
    assert "N-d" in c["late"] and c["late_built"] == 0, c                     # N-4: refused before the builder
    assert "not the search calendar" in c["misaligned"] and c["misaligned_built"] == 1, c


def test_a_daily_loss_limit_ends_the_day_at_the_take(checks):
    c = checks["dll"]
    assert c["day_ends"] > 0 and c["later"] == 0 and c["count_bad"] == 0, c


def test_firm_reading_refuses_a_historical_outcome_on_a_race_arm_row(checks):
    c = checks["reading"]
    assert c["rows"] > 0 and c["clean"] == 0 and c["planted"] == 1, c
    assert c["planted_rr_used"] == 1 and c["planted_at_need"] == 1, c           # C3-3: the history's rr_used, at_need


@pytest.mark.slow
@pytest.mark.heavy         # N-5: reads P-16's walk table (the atlas): the lead's, under run.lock
def test_p16s_own_job_vendored_identity():
    data = ROOT / "vendor" / "stage2" / "data"
    if not ((data / "bars").is_dir() and (data / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "three_way_baseline_checks.py"), "p16"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=3600, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    c = json.loads(r.stdout.strip().splitlines()[-1])["p16"]
    for arm, v in c.items():
        assert v["n_diffs"] == 0 and v["funded"] > 0 and v["payouts"] > 0, (arm, v)
