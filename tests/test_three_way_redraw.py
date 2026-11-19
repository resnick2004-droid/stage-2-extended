"""Wave 3.2 (corrective cycle 1): the martingale-outcome reading's redraw (`extended/three_way_redraw.py`) -- exact
fractions, no engine in this process, no bar; fast.

- **the race's oracles** (B-1, N-5, M-4) -- over a grid of (l, g, c, entry, x_target, x_stop) with fractional cushions
  and unequal exit costs: gross expectation exactly zero; net exactly -(entry + p x_target + (1 - p) x_stop); the worst
  change never past the floor; **fractional: a cushion-bound loss ends exactly on the floor** (the lead's ruling on the
  red team's B-1); no room, no trade; the note's reference law (`three_way_arith.race_redraw`) exactly; the `lattice`
  argument (kept for N-4's shared path) rounds inward and keeps the oracles;
- **R-10's stopped walk with its residual step** -- the law sums to one; gross exactly zero; net exactly minus its
  expected costs; never past the floor; the barrier fractional and reached exactly (no stranded account), over
  (g, l, c, x, s, n) with fractional cushions and unequal costs; the lanes' walk equals the scalar one and the exact law
  (40000 lanes against its probabilities); the twin's plain steps are the mirror; the step count rounds halves up and
  takes at least one step;
- **the exit-state map** is R-10's table and refuses any other state;
- **the worse-fill stress** (measure 29) adds k ticks to the entry and to every exit, its net exactly minus its costs;
- **the vendored draw at no cost** -- `race_dollars` and **the journey's own race step** (`_trade_mc`) equal the vendored
  `RandomDraw(edge=0, truncate, drift)` on the same uniforms (in a process of its own: `tests/three_way_vendored_draw.py`;
  the red team's n-4).
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from extended import three_way_redraw as RD

ROOT = Path(__file__).resolve().parent.parent
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
COSTS = (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 2))
CUSHIONS = tuple(Fraction(k, 4) for k in range(1, 161, 7))


def check_race_oracles(lattices=(None, 1)) -> int:
    """Every race on the grid: gross zero, net minus its costs, never past the floor, and (fractional) a cushion-bound
    loss exactly on the floor; returns the count checked."""
    n = 0
    for lat, l, g, c in itertools.product(lattices, range(1, 41, 6), range(1, 41, 7), CUSHIONS):
        for e, xt, xs in itertools.product(COSTS, COSTS, COSTS):
            r = RD.race_net(l, g, c, e, xt, xs, lat)
            room = c - e - xs
            if r is None:
                assert RD.inward(min(Fraction(l), room), lat) <= 0, (l, g, c, e, xt, xs, lat)
                continue
            gross, net, worst = r
            rr = RD.race(l, g, c - e, xs, lat)
            assert rr is not None, (l, g, c, e, xt, xs, lat)
            p, win, loss = rr
            assert gross == 0, (l, g, c, e, xt, xs, lat)
            assert net == -(e + p * xt + (1 - p) * xs), (l, g, c, e, xt, xs, lat)
            assert worst >= -c, (l, g, c, e, xt, xs, lat)
            assert loss <= l and (lat is None or loss.denominator == 1)
            if lat is None and room < l:
                assert worst == -c, (l, g, c, e, xt, xs)            # B-1: on the floor exactly, the account fails
            n += 1
    return n


def test_the_race_oracles() -> None:
    assert RD.LATTICE is None
    assert check_race_oracles() > 1000


def test_the_race_is_the_notes_reference_law() -> None:
    spec = importlib.util.spec_from_file_location("three_way_arith_for_redraw", ARITH)
    arith = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arith)
    for l, g, c, x in itertools.product(range(1, 30, 4), range(1, 30, 5), CUSHIONS, COSTS):
        mine = RD.race(l, g, c, x)
        try:
            ref = arith.race_redraw(l, g, c, x)
        except ValueError:
            assert mine is None
            continue
        assert mine == ref


def check_walk_oracles() -> int:
    n = 0
    for s, l, g, c, n_steps in itertools.product((1, 2), (4, 6, 8), (2, 4, 6), CUSHIONS[::2], (1, 3, 8)):
        if l % s or g % s:
            continue
        for e, xt, xs, xf in itertools.product(COSTS[:3], COSTS[:2], COSTS[:3], COSTS[1:3]):
            r = RD.walk_net(l, g, c, n_steps, s, e, xt, xs, xf)
            if r is None:
                continue
            up, L = RD.walk_barriers(l, g, c - e, xs, xf, s)
            assert L == min(Fraction(l), c - e - max(xs, xf))          # fractional, never rounded
            law = RD.walk_law(up, L, s, n_steps)
            assert sum(law.values()) == 1
            assert all(v == -L for (k, v) in law if k == "stop")       # the barrier reached exactly: no stranding
            gross, net, worst = r
            assert gross == 0, (s, l, g, c, n_steps)
            cost = sum(pr * {"target": xt, "stop": xs, "time": xf}[k] for (k, v), pr in law.items())
            assert net == -(e + cost), (s, l, g, c, n_steps, e, xt, xs, xf)
            assert worst >= -c, (s, l, g, c, n_steps, e, xt, xs, xf)
            n += 1
    return n


def test_the_stopped_walk_oracles() -> None:
    assert check_walk_oracles() > 500


def test_the_residual_step_is_a_driftless_two_point_race() -> None:
    """At the last lattice point above the barrier (rho below it), the step goes to the barrier with probability
    s / (s + rho), else up one step: a martingale move; an account whose room is below one step is still raced."""
    for s, L in ((2, Fraction(7, 2)), (2, Fraction(1, 3)), (4, Fraction(9)), (2, Fraction(4))):
        d, rho = RD._bottom(L, s)
        assert 0 < rho <= s and L == d * s + rho
        law = RD.walk_law(10, L, s, 1)
        assert sum(pr * v for (k, v), pr in law.items()) == 0
        if d == 0:
            assert law[("stop", -L)] == Fraction(s) / (s + rho)
    law = RD.walk_law(10, Fraction(1, 3), 2, 1)                         # room below one step: still raced
    assert set(law) == {("stop", Fraction(-1, 3)), ("time", 2)}


def test_the_walk_on_lanes_is_the_scalar_walk_and_the_law() -> None:
    from extended import three_way_keys as K
    from extended import three_way_seeds as S

    unit = K.Unit(S.issue("tests"), 1, 0, 0, 0)
    U = np.array([K.uniforms(unit.coin_key(m, K.WALK), 12) for m in range(400)])
    Ut = np.array([K.uniforms(unit.coin_key(m, K.WALK), 12, twin=True) for m in range(400)])
    for L in (7.0, 6.5, 0.4):
        val, kind = RD.walk_outcomes(U, 3, np.full(400, L), 2)
        for j in range(400):
            v, k = RD.walk_outcome(U[j], 3, L, 2)
            assert v == val[j] and {"target": 1, "stop": -1, "time": 0}[k] == kind[j]
    steps, steps_t = np.where(U < 0.5, 1, -1), np.where(Ut < 0.5, 1, -1)
    assert np.array_equal(steps, -steps_t)                            # every plain step reversed: the mirror
    rng = np.random.default_rng(K.seed_key(S.issue("tests"), "test", test=S.TEST_IDS["walk_oracle"], replicate=0))
    Ur = rng.random((40000, 6))
    val, kind = RD.walk_outcomes(Ur, 2, np.full(40000, 2.5), 1)
    law = RD.walk_law(2, 2.5, 1, 6)
    for (k, v), pr in law.items():
        code = {"target": 1, "stop": -1, "time": 0}[k]
        f = float(np.mean((kind == code) & np.isclose(val, float(v))))
        assert abs(f - pr) < 5 * np.sqrt(pr * (1 - pr) / 40000) + 1e-12, (k, v, f, pr)
    assert RD.walk_steps(1.0, 2.5, 1.0) == 3 and RD.walk_steps(1.0, 0.1, 1.0) == 1 and RD.walk_steps(2.0, 1.0, 2.0) == 1


def test_the_exit_state_map_is_r10s_and_refuses_any_other() -> None:
    assert set(RD.EXIT_LAW) == {"target", "stop", "stop_gap", "floor", "flatten", "news", "max_hold", "other"}
    assert {k for k, v in RD.EXIT_LAW.items() if v == "race"} == {"target", "stop", "stop_gap", "floor"}
    with pytest.raises(ValueError):
        RD.law_of("expired")


def test_the_worse_fill_stress_keeps_net_minus_its_costs() -> None:
    for k, (l, g, c) in itertools.product(RD.WORSE_FILL_TICKS, ((10, 10, 40), (20, 10, 12), (8, 16, Fraction(37, 4)))):
        e, xt, xs, xf = RD.worse_fill(0.25, 0.25, 0.5, 0.75, k, 1.0)
        assert (e, xt, xs, xf) == (0.25 + k, 0.25 + k, 0.5 + k, 0.75 + k)
        r = RD.race_net(l, g, c, Fraction(e), Fraction(xt), Fraction(xs))
        if r is None:
            continue
        p, _, _ = RD.race(l, g, c - Fraction(e), Fraction(xs))
        assert r[1] == -(Fraction(e) + p * Fraction(xt) + (1 - p) * Fraction(xs)) and r[2] >= -c
    assert RD.WORSE_FILL_TICKS == (1, 2)


def test_the_race_and_the_journeys_race_are_the_vendored_draw_at_no_cost() -> None:
    """In a process of its own (CLAUDE.md: anything importing the vendored tree runs apart)."""
    out = subprocess.run([sys.executable, str(ROOT / "tests" / "three_way_vendored_draw.py")], capture_output=True,
                         text=True, timeout=300, cwd=ROOT)
    assert out.returncode == 0, out.stderr[-2000:]
    got = json.loads(out.stdout.strip().splitlines()[-1])
    assert got["equal"] and got["n"] >= 1000, got
    assert got["journey_equal"] and got["journey_n"] >= 1000, got
