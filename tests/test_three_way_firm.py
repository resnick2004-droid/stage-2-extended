"""Q-185: the three-way runner's firm path (`extended/three_way_firm.py`): the journey through Stage 2's vendored lockstep
with the runner's race as the engine's outcome draw. Synthetic schedules only; no bar, no result.

In this process (no engine imported): the search years' guard (undated only under a synthetic role's seed; dated
windows against the search years' calendar and `search_cut`), the refusals, the daily loss limit's day end and the
floor's fill failure on the draw itself, the router's one account a trade, `P_B`'s count. In their own process
(`tests/three_way_firm_checks.py`, which imports the engine): the two identities against the vendored path (bit for
bit) with the records tied to the engine's own, zero edge against this file's own arithmetic and walk law, RB-1's
floor-bound lanes, the pairing and keys against the toy path lane for lane (deep and floor-reaching), two seats, and
the measured cost per lane-trade.

The runner (Wave 3.2, `extended/three_way_journey.py` and its modules) is imported hard: on a tree without it this
file fails, it never skips (the red team's F4).
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

from extended import three_way_firm as TF
from extended import three_way_journey as J
from extended import three_way_seeds as S

ROOT = Path(__file__).resolve().parent.parent
SEED = S.issue("tests")
PART = S.PARTS["tests"]


def _toy(n: int = 30, per_day: int = 1) -> J.Schedule:
    return J.Schedule("toy", tuple(J.Trade(session=s, decision=d, entry=d + 5, exit=d + 50, exit_reason="target", g=20,
                                           l=10, tick_value=5.0) for s in range(n)
                                   for d in (600, 700, 800)[:per_day]))


def _call(**kw):
    base = dict(schedule=_toy(), firm=None, plan=TF.AccountPlan(), start=0, seed_indices=range(2), horizon=21,
                seed=SEED, part=PART, history=0, block_sessions=30)
    base.update(kw)
    return TF.simulate(base.pop("schedule"), base.pop("firm"), base.pop("plan"), base.pop("start"),
                       base.pop("seed_indices"), base.pop("horizon"), **base)


def _weekdays(first: date, n: int) -> list[date]:
    out, d = [], first
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


# ------------------------------------------------------------------------------------------------ in process


def test_search_years_only_an_undated_run_needs_a_synthetic_role():
    TF.check_dates(None, 0, 21, 30, seed=SEED)                          # the tests' role: synthetic by declaration
    with pytest.raises(ValueError, match="synthetic role|synthetic history"):
        TF.check_dates(None, 0, 21, 30, seed=S.issue("h3d_coins"))      # a deciding role names its dates
    with pytest.raises(ValueError, match="synthetic history"):
        TF.check_dates(None, 0, 21, 30, seed=int(SEED))                 # an unissued seed
    with pytest.raises(ValueError, match="not a label"):
        TF.check_dates("synthetic", 0, 21, 30, seed=SEED)


def test_search_years_only_the_dates_are_checked_against_the_calendar():
    days = _weekdays(date(2023, 11, 27), 30)                            # ends past 2023-12-29
    cal = frozenset(d for d in days if d <= date(2023, 12, 29))
    with pytest.raises(ValueError, match="past the search years"):
        TF.check_dates(days, 9, 21, 30, seed=SEED, calendar=cal)
    with pytest.raises(ValueError, match="past the search years"):
        _call(dates=days, start=9, calendar=cal)
    early = _weekdays(date(2021, 1, 4), 31)
    with pytest.raises(ValueError, match="do not equal the search years' calendar"):
        TF.check_dates(early[:30], 0, 21, 30, seed=SEED, calendar=frozenset(early[:20]))   # dates off the calendar
    with pytest.raises(ValueError, match="do not equal the search years' calendar"):
        TF.check_dates(early[1:], 0, 21, 30, seed=SEED, calendar=frozenset(early))   # real sessions, shifted by one
    with pytest.raises(ValueError, match="schedule's own dates"):
        TF.check_dates(early[:30], 0, 21, 30, seed=SEED, calendar=frozenset(early), schedule_dates=early[1:])
    early = early[:30]
    with pytest.raises(ValueError, match="not in order"):
        TF.check_dates(early[::-1], 0, 21, 30, seed=SEED, calendar=frozenset(early))
    with pytest.raises(ValueError, match="sessions but"):
        TF.check_dates(early[:5], 0, 3, 30, seed=SEED, calendar=frozenset(early))
    with pytest.raises(ValueError):
        _call(start=10, horizon=21)                                     # the window reads past the block's end


def test_search_years_only_the_cut_is_searched_or_the_stub_refuses():
    early = _weekdays(date(2021, 1, 4), 30)
    try:
        import extended.search_cut  # noqa: F401
    except ImportError:
        with pytest.raises(RuntimeError, match="Q-172"):
            TF.check_dates(early, 0, 21, 30, seed=SEED, calendar=frozenset(early))
    else:
        TF.check_dates(early, 0, 21, 30, seed=SEED, calendar=frozenset(early))


@pytest.mark.heavy         # Q-134: names the bars' manifest under the licensed data (metadata, but the data's tree)
def test_the_search_calendar_is_derived_from_the_manifest():
    if not TF.MANIFEST.is_file():
        pytest.skip("no bars manifest on this tree (licensed data, linked by junction)")
    cal = TF.search_calendar()
    assert cal and max(cal) <= date(2023, 12, 29) and min(cal) >= date(2020, 1, 2)


def test_refusals_before_the_engine():
    with pytest.raises(ValueError, match="denial ladder"):
        _call(arm=J.ArmSpec(enforcement_q=0.1))
    with pytest.raises(ValueError, match="outcome"):
        _call(outcome="binary")
    with pytest.raises(ValueError, match="explicit seed"):
        _call(outcome="engine_binary")
    with pytest.raises(ValueError, match="seed index repeats"):
        _call(seed_indices=(0, 1, 1))
    with pytest.raises(ValueError, match="slots"):
        _call(schedule=_toy(per_day=3), plan=TF.AccountPlan(trades_per_day=2))
    with pytest.raises(NotImplementedError, match="Topstep"):
        TF.firm_for("LU")
    with pytest.raises(ValueError):
        TF.AccountPlan(rotation="every_account")                       # not one of A15's declared values


def test_every_money_carrying_choice_is_labelled():
    ch = TF.AccountPlan().choices()
    for k in ("seat_frees", "initial_bankroll", "payout_path", "payout_frac", "keep_balance", "rotation", "seats",
              "strict_gap", "latency"):
        assert ch[k]["class"] == "fixed" and ch[k]["source"], k
    firm = TF.Firm(name="TS", rules=None, subscription=0.0, billing_days=21, activation=0.0, payout_lag_days=1,
                   max_concurrent_accounts=5, payout_method="aeropay", source="the verified ledger")
    assert TF.AccountPlan().choices(firm)["payout_method"] == {"value": "aeropay", "class": "fixed",
                                                                "source": "the verified ledger"}


def _lane(schedule: J.Schedule, plan: TF.AccountPlan) -> TF.Lane:
    coins = J.CoinLanes(SEED, PART, 0, 0, [0], None, False)
    return TF.Lane(TF._Start(schedule, plan, 0, J.ArmSpec(), coins, True), 0)


def test_a_binding_daily_loss_limit_ends_the_day_and_a_binding_floor_fails_at_the_fill():
    costly = J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="target", g=20, l=10, tick_value=5.0,
                     entry_cost=6.0, x_stop=6.0)
    cheap = J.Trade(session=0, decision=700, entry=705, exit=750, exit_reason="target", g=20, l=10, tick_value=5.0)
    sch = J.Schedule("dll", (costly, cheap))
    lane = _lane(sch, TF.AccountPlan(trades_per_day=2))
    lane.day_hook(1, [("combine", 0)])
    d = TF.LaneDraw(lane, ("combine", 0), 0)
    d.begin_session(balance=0.0, floor=-2000.0)                         # the floor is far: the limit's room binds
    assert math.isnan(d(1, 0, 0, np.array([5.0]))[0])                   # not taken: the day ends ...
    assert math.isnan(d(1, 0, 1, np.array([5.0]))[0])                   # ... so the cheap trade is not offered
    assert [r[6] for r in lane.log.rows] == ["day_end", "day_end"] and lane.fill_failures == 0
    lane = _lane(sch, TF.AccountPlan(trades_per_day=2))
    lane.day_hook(1, [("combine", 0)])
    d = TF.LaneDraw(lane, ("combine", 0), 0)
    d.begin_session(balance=0.0, floor=-5.0)                            # the floor binds
    assert d(1, 0, 0, np.array([5.0]))[0] == -5.0 and lane.fill_failures == 1


def test_the_router_deals_each_trade_to_one_account_and_they_alternate():
    lane = _lane(_toy(per_day=3), TF.AccountPlan(trades_per_day=2, max_total_accounts=2))
    lane.day_hook(1, [("funded", 0), ("combine", 1)])
    got = lane.dealt[1]
    assert sorted(len(v) for v in got.values()) == [1, 2]
    moments = [t.moment for v in got.values() for t in v]
    assert len(moments) == len(set(moments)) == 3
    lane.day_hook(2, [("funded", 0), ("combine", 1)])
    assert all(len(v) >= 1 for v in lane.dealt[2].values())             # both accounts take a trade
    lane.day_hook(0, [("combine", 0)])
    assert lane.dealt[0] == {"combine:0": []}                           # the purchase evening trades nothing


def test_months_ahead_is_the_toy_paths_count():
    from extended import journey_measures as JM

    rng = np.random.default_rng([int(SEED), 3])
    for _ in range(200):
        rel = np.round(np.cumsum(rng.normal(0, 40, 64)) - 50, 2)
        for b in (None, 60.0, 200.0):
            assert TF.months_ahead(rel, 63, b) == JM.months_ahead_under(rel, b)


def _close_pair() -> J.Schedule:
    """Two trades on one session, the second entering 2 minutes after the first's exit: no overlap (the schedule
    admits it), but inside Stage 2's five-minute gap."""
    return J.Schedule("close", (
        J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="target", g=20, l=10, tick_value=5.0),
        J.Trade(session=0, decision=647, entry=652, exit=700, exit_reason="target", g=20, l=10, tick_value=5.0)))


def test_one_open_position_across_all_accounts_the_strict_gap_is_refused():
    for gap, refused in ((5.0, True), (0.0, False)):
        lane = _lane(_close_pair(), TF.AccountPlan(trades_per_day=1, max_total_accounts=2, strict_gap=gap))
        lane.day_hook(1, [("combine", 0), ("combine", 1)])                 # the router: one trade to each account
        owner = {v[0].entry: n for n, v in lane.dealt[1].items() if v}
        assert set(owner) == {605, 652} and owner[605] != owner[652]       # two accounts, one trade each
        draws = {n: TF.LaneDraw(lane, ("combine", int(n[-1])), 0) for n in ("combine:0", "combine:1")}
        for d in draws.values():
            d.begin_session(balance=0.0, floor=-2000.0)
        draws[owner[605]](1, 0, 0, np.array([2000.0]))
        if refused:                                                        # the second account, 2 minutes later
            with pytest.raises(RuntimeError, match="D-429"):
                draws[owner[652]](1, 0, 0, np.array([2000.0]))
        else:
            assert not math.isnan(draws[owner[652]](1, 0, 0, np.array([2000.0]))[0])
    lane = _lane(_close_pair(), TF.AccountPlan(trades_per_day=2))
    lane.day_hook(1, [("combine", 0)])
    d = TF.LaneDraw(lane, ("combine", 0), 0)
    d.begin_session(balance=0.0, floor=-2000.0)
    d(1, 0, 0, np.array([2000.0]))
    with pytest.raises(RuntimeError, match="D-429"):                       # on one account too
        d(1, 0, 1, np.array([2000.0]))
    assert lane.days(1) == [{"accounts": 1, "taken": ((605, 650),), "offered": (605.0, 652.0)}]


def test_the_strict_gap_admits_an_entry_exactly_the_gap_after_a_close():
    """C1-N1: the boundary is the vendored D-429's (`open_until + gap > t` refuses): an entry exactly `strict_gap`
    minutes after a close is admitted, one minute sooner is refused, on one account and across two."""
    for entry, ok in ((655, True), (654, False)):
        sch = J.Schedule("edge", (
            J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="target", g=20, l=10, tick_value=5.0),
            J.Trade(session=0, decision=entry - 5, entry=entry, exit=700, exit_reason="target", g=20, l=10,
                    tick_value=5.0)))
        for seats in (1, 2):
            lane = _lane(sch, TF.AccountPlan(trades_per_day=2, max_total_accounts=seats))
            keys = [("combine", i) for i in range(seats)]
            lane.day_hook(1, keys)
            draws = {TF._name(k): TF.LaneDraw(lane, k, 0) for k in keys}
            for d in draws.values():
                d.begin_session(balance=0.0, floor=-2000.0)
            order = [(n, i) for n, v in lane.dealt[1].items() for i, _ in enumerate(v)]
            order.sort(key=lambda x: lane.dealt[1][x[0]][x[1]].entry)
            draws[order[0][0]](1, 0, order[0][1], np.array([2000.0]))
            if ok:
                assert not math.isnan(draws[order[1][0]](1, 0, order[1][1], np.array([2000.0]))[0])
            else:
                with pytest.raises(RuntimeError, match="D-429"):
                    draws[order[1][0]](1, 0, order[1][1], np.array([2000.0]))


def test_the_baselines_ran_under_stage_2s_strict_rule_at_the_plans_gap():
    """P-14, P-15 and P-16's registered gate manifests record `one_at_a_time` (D-429's gap) as the plan's default."""
    res = ROOT / "vendor" / "stage2" / "results"
    for f in ("a3_brk30_cb20_gate.csv", "rc_s100_all_gate.csv", "rc_s150_all_gate.csv"):
        m = json.loads((res / f"{f}.manifest.json").read_text(encoding="utf-8"))
        assert float(m["parameters"]["one_at_a_time"]) == TF.AccountPlan().strict_gap, f


# ------------------------------------------------------------------------------------------------ in its own process


@pytest.fixture(scope="module")
def checks() -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "three_way_firm_checks.py")], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=850, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_identity_the_binary_arm_is_the_vendored_path_bit_for_bit(checks):
    c = checks["identity_binary"]
    assert c["n_diffs"] == 0, c["diffs"]
    assert c["cross_diffs"] > 0                             # the comparison can fail
    assert c["passes"] > 0 and c["fails"] > 0              # the identity walks through passes and failures


def test_identity_the_race_is_the_vendored_random_draw_bit_for_bit(checks):
    c = checks["identity_race"]
    assert c["n_diffs"] == 0, c["diffs"]
    assert c["cross_diffs"] > 0                             # the comparison can fail
    assert c["bad"] == {"rel": 0, "arrivals": 0, "first_pass": 0, "first_pay": 0, "accounts": 0}, c["bad"]
    assert c["passes"] > 0 and c["lanes_paid"] > 0 and c["accounts_max"] > 0     # through passes and arrivals


def test_zero_edge_under_the_race(checks):
    c = checks["zero_edge"]
    assert c["trades"] > 1000 and c["bad"] == 0, c
    assert c["kinds"].get("walk", 0) > 500 and c["walk_laws"] > 1
    assert c["walks_replayed"] == c["kinds"]["walk"] and c["walk_replay_bad"] == 0, c    # C1-4: path for path
    assert c["walks_off_lattice"] > 100, c                  # the floor-side residual step is read
    for z in ("z", "race_z", "walk_target_z", "walk_stop_z"):
        assert abs(c[z]) < 4.0, (z, c)


def test_rb1_a_floor_bound_lane_fails_at_the_fill(checks):
    c = checks["rb1"]
    for name in ("race", "walk"):
        assert c[name]["bound"] > 10 and c[name]["fill_failures"] == c[name]["bound"], (name, c[name])
        assert c[name]["total_fill_failures"] == c[name]["bound"] and c[name]["bad"] == 0, (name, c[name])
    f = c["flatten"]
    assert f["bound"] > 10 and f["engine_clipped"] > 0 and f["total_fill_failures"] == 0 and f["bad"] == 0, f


def test_the_keys_and_the_pairing_carry_over_from_the_toy_path(checks):
    c = checks["pairing"]
    for arm in ("base", "twin", "missed", "worse", "plant", "as_walked", "floor", "rb1_race", "rb1_walk",
                "rb1_flatten", "dll"):
        a = c[arm]
        assert a["keys_equal"] and a["n_keys"] > 0, (arm, a)
        assert a["max_balance_diff"] < 1e-6 and a["spread"] > 0, (arm, a)
        assert a["accounts_equal"] and a["fill_failures_equal"], (arm, a)
    assert c["floor"]["fill_failures"] > 0 and c["floor"]["accounts"] > 0      # the floor is reached and replaced
    assert c["rb1_race"]["fill_failures"] > 0 and c["rb1_walk"]["fill_failures"] > 0
    assert c["dll"]["day_ends"] > 0                                    # C1-N4: the limit's day end, through the engine
    assert c["starts_disjoint"] and c["keys_carry_start"]


def test_two_seats_alternate_one_account_a_trade(checks):
    c = checks["seats"]
    assert c["day0_combines"] == 2 and c["copied"] == 0
    assert c["days_with_two_accounts"] > 0 and c["lanes_two_accounts_traded"] == c["lanes"]


def test_h4s_three_outputs_are_the_engines_own_counts(checks):
    c = checks["h4"]
    for name, accounts in (("one_seat", 1.0), ("two_seats", 2.0), ("idle", 1.0)):
        assert c[name]["bad"] == 0, (name, c[name])
        assert c[name]["accounts_max"] == accounts and c[name]["orders_max"] >= 1 and c[name]["taken_mean"] > 0, c
    assert c["one_seat"]["full"] and c["idle"]["full"]                       # (30) and (37) compared in full
    assert c["idle"]["funded_breached"] > 0 and c["idle"]["sessions_without_account"] > 0   # idle sessions counted


def test_the_cost_per_lane_trade_is_measured(checks):
    c = checks["cost"]
    assert c["lane_trades"] > 0 and c["seconds"] > 0
    print(json.dumps(c))


# ------------------------------------------------------------------------------------------------ the registered rows

IDENTITY = ROOT / "identity" / "three_way_firm_identity.py"
DATA = ROOT / "vendor" / "stage2" / "data"


def _identity(*args: str, timeout: int) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, str(IDENTITY), *args], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", timeout=timeout, env=env)


def test_the_firm_paths_runner_through_the_gate_equals_the_vendored_gate_on_synthetic_blocks():
    r = _identity("--synthetic", timeout=850)
    out = r.stdout + r.stderr
    assert r.returncode == 0 and "synthetic identity HOLDS" in r.stdout, out[-4000:]


@pytest.mark.slow
@pytest.mark.heavy         # reads A1 and A3 (the atlas): the lead's, under run.lock (F7)
def test_the_firm_path_reproduces_p14s_registered_gate_paths_at_four_paths():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = _identity("--paths", "4", timeout=3600)
    out = r.stdout + r.stderr
    assert r.returncode == 0 and "identity HOLDS: P-14 through the firm path's runner" in r.stdout, out[-4000:]
