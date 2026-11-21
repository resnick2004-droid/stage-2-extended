"""Q-185c: the firm path's baseline mode (`extended/three_way_baseline.py`). Synthetic; no bar, no result.

In this process (no engine): the trade facts' refusals and admissions (a same-bar fill at the limit, a breakeven kind
without its move bar, an unknown kind), FV3's target rounding, `RaceOver`'s delegation (every attribute and setting the
vendored draw's), a missing fact refused, and the declared log R. In its own process
(`tests/three_way_baseline_checks.py`): the identity -- the vendored P&L passed through equals `customer_slices.replay`
bit for bit, at three starts, the race arm differing -- and the race arm's laws by kind at each account's R, both Rs
used, same-bar exits taken, the strict rule held across accounts.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from extended import three_way_baseline as TB
from extended import three_way_journey as J
from extended import three_way_seeds as S

ROOT = Path(__file__).resolve().parent.parent
SEED = S.issue("tests")


def _facts(**kw):
    base = dict(decision=935, entry=940, stop_ticks=40, tick_value=0.5, kinds={1.5: "t", 2.0: "s"}, limit=1330,
                sigma=1.5)
    base.update(kw)
    return TB.TradeFacts(**base)


def test_the_facts_refuse_and_admit():
    _facts(entry=1330, limit=1330)                                 # a fill at its own limit: a same-bar exit admitted
    with pytest.raises(ValueError, match="at or before its time limit"):
        _facts(entry=1331)
    with pytest.raises(ValueError, match="be_open"):
        _facts(kinds={2.0: "b"})                                   # a breakeven needs its move bar
    with pytest.raises(ValueError, match="be_open"):
        _facts(kinds={2.0: "b"}, be_open=900)                      # ... after its fill
    _facts(kinds={2.0: "b"}, be_open=1201)
    with pytest.raises(ValueError, match="not in"):
        _facts(kinds={2.0: "x"})
    with pytest.raises(ValueError, match="positive"):
        _facts(sigma=0.0)


def test_fv3s_target_rounding():
    assert TB.target_ticks(1.5, 40) == 60 and TB.target_ticks(0.25, 50) == 12 and TB.target_ticks(2.75, 100) == 275


class _Inner:
    settlement = "mae"

    def __init__(self):
        self.last_trade = {"historical_day": 0, "trade_index": 0, "realised_risk": 20.0}
        self.seen = []

    def can_take(self, *a):
        return "inner"

    def __call__(self, n, day, slot, cushion):
        return np.array([5.0])


def test_raceover_is_the_vendored_draw_but_its_pnl():
    inner = _Inner()
    coins = J.CoinLanes(SEED, S.PARTS["tests"], 0, 0, [0], None, False)
    unit = TB._Unit({}, 0, coins, J.ArmSpec(), None)
    w = TB.RaceOver(inner, unit, 0, "vendored", None)
    assert w.settlement == "mae" and w.can_take() == "inner" and w(1, 0, 0, np.array([100.0]))[0] == 5.0
    w.target_risk = 7.0
    assert inner.target_risk == 7.0                                # a setting reaches the vendored draw
    r = TB.RaceOver(inner, unit, 0, "race", None)
    with pytest.raises(ValueError, match="no facts"):
        r(1, 0, 0, np.array([100.0]))                              # a trade without facts is refused
    unit2 = TB._Unit({(0, 0): _facts()}, 0, coins, J.ArmSpec(), None)
    with pytest.raises(ValueError, match="log_rr"):
        TB.RaceOver(inner, unit2, 0, "race", None)(1, 0, 0, np.array([100.0]))   # no R reported, none declared
    out = TB.RaceOver(inner, TB._Unit({(0, 0): _facts()}, 0, coins, J.ArmSpec(), 1.5), 0, "race", None)(
        1, 0, 0, np.array([100.0]))[0]
    # no costs, $0.50 a tick of the position (20 / 40): G = 60 ticks ($30), L = min($20, the room $100) = $20, p = 0.4
    from extended import three_way_keys as K

    u = float(K.uniforms(K.Unit(SEED, S.PARTS["tests"], 0, 0, 0).coin_key(K.moment(0, 935, 0), K.RACE), 1)[0])
    assert out == (30.0 if u < 0.4 else -20.0)


@pytest.fixture(scope="module")
def checks() -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "three_way_baseline_checks.py")], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=850, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_identity_the_vendored_pnl_passed_through_is_customer_slices_replay_bit_for_bit(checks):
    c = checks["identity"]
    assert c["n_diffs"] == 0, c["diffs"]
    assert c["cross_diffs"] > 0 and c["trades"] > 0                # the comparison can fail; trades were made


def test_the_race_arm_books_each_kinds_law_at_its_accounts_r(checks):
    c = checks["race"]
    assert c["bad"] == 0 and c["overlap"] == 0, c
    assert set(c["kinds"]) == {"t", "s", "f", "b"} and {"race", "walk", "move"} <= set(c["laws"]), c
    assert c["rs"] == [1.5, 2.0] and c["same_bar"] > 0, c
    assert c["laws"].get("fill_fail", 0) > 0, c                     # floor-bound lanes occur, each booked the room
