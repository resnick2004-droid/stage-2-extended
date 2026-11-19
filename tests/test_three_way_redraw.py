"""Wave 3.2: the martingale-outcome reading's redraw (`extended/three_way_redraw.py`) -- exact fractions, no engine in
this process, no bar; fast.

- **the race's oracles** (B-1, N-5, M-4) -- over a grid of (l, g, c, entry, x_target, x_stop) with fractional cushions
  and unequal exit costs, at the declared lattice and with none: gross expectation exactly zero; net exactly
  -(entry + p x_target + (1 - p) x_stop); the worst change never past the floor; no room, no trade; the note's
  reference law (`three_way_arith.race_redraw`) at one exit cost and no rounding;
- **R-10's stopped walk** -- its law sums to one; gross exactly zero; net exactly minus its expected costs; never past
  the floor, over (g, l, c, x, s, n) with fractional cushions and unequal costs; the lanes' walk equals the scalar one;
  the twin's steps are the mirror; the step count rounds halves up and takes at least one step;
- **the exit-state map** is R-10's table and refuses any other state;
- **the worse-fill stress** (measure 29) adds k ticks to the entry and to every exit, and its net stays exactly minus
  its costs; its arms are counted;
- **the vendored draw at no cost** -- `race_dollars` with no cost and no lattice equals the vendored
  `RandomDraw(edge=0, truncate, drift)` on the same uniforms (in a process of its own: `tests/three_way_vendored_draw.py`).
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


def check_race_oracles(lattices=(RD.LATTICE, None)) -> int:
    """Every race on the grid: gross zero, net minus its costs, never past the floor; returns the count checked."""
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
            n += 1
    return n


def test_the_race_oracles() -> None:
    assert check_race_oracles() > 1000


def test_the_race_is_the_notes_reference_law() -> None:
    spec = importlib.util.spec_from_file_location("three_way_arith_for_redraw", ARITH)
    arith = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arith)
    for l, g, c, x in itertools.product(range(1, 30, 4), range(1, 30, 5), CUSHIONS, COSTS):
        mine = RD.race(l, g, c, x, None)
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
            up, down = RD.walk_barriers(l, g, c - e, xs, xf, s)
            law = RD.walk_law(up, down, n_steps)
            assert sum(law.values()) == 1
            gross, net, worst = r
            assert gross == 0, (s, l, g, c, n_steps)
            cost = sum(pr * (xt if x >= up else xs if x <= -down else xf) for x, pr in law.items())
            assert net == -(e + cost), (s, l, g, c, n_steps, e, xt, xs, xf)
            assert worst >= -c, (s, l, g, c, n_steps, e, xt, xs, xf)
            n += 1
    return n


def test_the_stopped_walk_oracles() -> None:
    assert check_walk_oracles() > 500


def test_the_walk_on_lanes_is_the_scalar_walk_and_its_twin_is_the_mirror() -> None:
    from extended import three_way_keys as K
    from extended import three_way_seeds as S

    unit = K.Unit(S.issue("tests"), 1, 0, 0, 0)
    U = np.array([K.uniforms(unit.coin_key(m, K.WALK), 12) for m in range(200)])
    Ut = np.array([K.uniforms(unit.coin_key(m, K.WALK), 12, twin=True) for m in range(200)])
    up, dn = np.full(200, 3), np.full(200, 4)
    pos, kind = RD.walk_outcomes(U, up, dn)
    for j in range(200):
        x, k = RD.walk_outcome(U[j], 3, 4)
        assert x == pos[j] and {"target": 1, "stop": -1, "time": 0}[k] == kind[j]
    steps, steps_t = np.where(U < 0.5, 1, -1), np.where(Ut < 0.5, 1, -1)
    assert np.array_equal(steps, -steps_t)                            # every step reversed: the mirrored path
    assert RD.walk_steps(1.0, 2.5, 1.0) == 3 and RD.walk_steps(1.0, 0.1, 1.0) == 1 and RD.walk_steps(2.0, 1.0, 2.0) == 1


def test_the_exit_state_map_is_r10s_and_refuses_any_other() -> None:
    assert set(RD.EXIT_LAW) == {"target", "stop", "stop_gap", "floor", "flatten", "news", "max_hold", "other"}
    assert {k for k, v in RD.EXIT_LAW.items() if v == "race"} == {"target", "stop", "stop_gap", "floor"}
    with pytest.raises(ValueError):
        RD.law_of("expired")


def test_the_worse_fill_stress_keeps_net_minus_its_costs_and_is_counted() -> None:
    for k, (l, g, c) in itertools.product(RD.WORSE_FILL_TICKS, ((10, 10, 40), (20, 10, 12), (8, 16, Fraction(37, 4)))):
        e, xt, xs, xf = RD.worse_fill(0.25, 0.25, 0.5, 0.75, k, 1.0)
        assert (e, xt, xs, xf) == (0.25 + k, 0.25 + k, 0.5 + k, 0.75 + k)
        r = RD.race_net(l, g, c, Fraction(e), Fraction(xt), Fraction(xs))
        if r is None:
            continue
        p, _, _ = RD.race(l, g, c - Fraction(e), Fraction(xs))
        assert r[1] == -(Fraction(e) + p * Fraction(xt) + (1 - p) * Fraction(xs)) and r[2] >= -c
    assert RD.WORSE_FILL_TICKS == (1, 2) and RD.stress_cells(5) == 10


def test_race_dollars_is_the_vendored_draw_at_no_cost() -> None:
    """In a process of its own (CLAUDE.md: anything importing the vendored tree runs apart)."""
    out = subprocess.run([sys.executable, str(ROOT / "tests" / "three_way_vendored_draw.py")], capture_output=True,
                         text=True, timeout=300, cwd=ROOT)
    assert out.returncode == 0, out.stderr[-2000:]
    got = json.loads(out.stdout.strip().splitlines()[-1])
    assert got["equal"] and got["n"] >= 1000, got
