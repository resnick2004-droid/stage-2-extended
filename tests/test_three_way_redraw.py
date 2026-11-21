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
    for s, l, g, c, n_steps in itertools.product((1, 2, 3), (4, 6, 8), (2, 4, 6), CUSHIONS[::2], (1, 3, 8)):
        for e, xt, xs, xf in itertools.product(COSTS[:3], COSTS[:2], COSTS[:3], COSTS[1:3]):
            r = RD.walk_net(l, g, c, n_steps, s, e, xt, xs, xf)
            if r is None:
                continue
            G, L = RD.walk_barriers(l, g, c - e, xs, xf, s)
            assert L == min(Fraction(l), c - e - xs) and G == g          # the race's barrier, fractional (RB-1)
            assert min(Fraction(l), c - e - max(xs, xf)) > 0             # taken only when L_fill > 0 (m-1)
            law = RD.walk_law(G, L, Fraction(s), n_steps)
            assert sum(law.values()) == 1
            assert all(v == -L for (k, v) in law if k == "stop")       # the barrier reached exactly
            gross, net, worst = r
            assert gross == 0, (s, l, g, c, n_steps)
            cost = sum(pr * {"target": xt, "stop": xs, "time": xf}[k] for (k, v), pr in law.items())
            # every exit's change clipped at the floor; only a flatten can reach it, by at most x_flat - x_stop
            clip = sum(pr * max(Fraction(0), -c - (-e + v - {"target": xt, "stop": xs, "time": xf}[k]))
                       for (k, v), pr in law.items())
            assert net == -(e + cost) + clip, (s, l, g, c, n_steps, e, xt, xs, xf)
            p_time = sum(pr for (k, v), pr in law.items() if k == "time")
            assert clip <= p_time * max(Fraction(0), xf - xs)
            if L < l:                                                  # a cushion-bound stop ends on the floor
                assert -e - L - xs == -c
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
        law = RD.walk_law(Fraction(10 * s), L, Fraction(s), 1)
        assert sum(pr * v for (k, v), pr in law.items()) == 0
        if d == 0:
            assert law[("stop", -L)] == Fraction(s) / (s + rho)
    law = RD.walk_law(Fraction(20), Fraction(1, 3), Fraction(2), 1)       # room below one step: still raced
    assert set(law) == {("stop", Fraction(-1, 3)), ("time", 2)}


def test_m2_a_fractional_target_in_the_walk_is_raced_exactly() -> None:
    """A rule's profit level makes the walk's target fractional (G = min(g, level)): its last lattice step below G is a
    two-point race to G, so gross stays exactly zero at every G, L, step and length, and the target is reached at G;
    both ends within one step of the fill make the walk the race itself (p = L / (L + G))."""
    for G, L, s, n in itertools.product((Fraction(7, 2), Fraction(9), Fraction(1, 3), Fraction(25, 4)),
                                        (Fraction(37, 3), Fraction(5, 2), Fraction(1, 5)), (Fraction(2), Fraction(4)),
                                        (1, 3, 9)):
        law = RD.walk_law(G, L, s, n)
        assert sum(law.values()) == 1 and sum(pr * v for (k, v), pr in law.items()) == 0, (G, L, s, n)
        assert all(v == G for (k, v) in law if k == "target") and all(v == -L for (k, v) in law if k == "stop")
    one = RD.walk_law(Fraction(1, 3), Fraction(1, 5), Fraction(2), 1)
    assert one == {("target", Fraction(1, 3)): Fraction(3, 8), ("stop", Fraction(-1, 5)): Fraction(5, 8)}
    G, L = RD.walk_barriers(8, 8, Fraction(40), Fraction(1, 2), Fraction(3, 4), 2, g_cap=Fraction(7, 2))
    assert G == Fraction(7, 2) and L == 8
    r = RD.walk_net(8, 8, Fraction(40), 5, 2, Fraction(1, 4), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4),
                    g_cap=Fraction(7, 2))
    assert r[0] == 0


def test_the_walk_on_lanes_is_the_scalar_walk_and_the_law() -> None:
    from extended import three_way_keys as K
    from extended import three_way_seeds as S

    unit = K.Unit(S.issue("tests"), 1, 0, 0, 0)
    U = np.array([K.uniforms(unit.coin_key(m, K.WALK), 12) for m in range(400)])
    Ut = np.array([K.uniforms(unit.coin_key(m, K.WALK), 12, twin=True) for m in range(400)])
    for G, L in ((6.0, 7.0), (6.0, 6.5), (6.0, 0.4), (3.5, 6.5), (0.3, 0.4)):
        val, kind = RD.walk_outcomes(U, G, np.full(400, L), 2)
        for j in range(400):
            v, k = RD.walk_outcome(U[j], G, L, 2)
            assert v == val[j] and {"target": 1, "stop": -1, "time": 0}[k] == kind[j]
    steps, steps_t = np.where(U < 0.5, 1, -1), np.where(Ut < 0.5, 1, -1)
    assert np.array_equal(steps, -steps_t)                            # every plain step reversed: the mirror
    rng = np.random.default_rng(K.seed_key(S.issue("tests"), "test", test=S.TEST_IDS["walk_oracle"], replicate=0))
    Ur = rng.random((40000, 6))
    val, kind = RD.walk_outcomes(Ur, 2.0, np.full(40000, 2.5), 1)
    law = RD.walk_law(2.0, 2.5, 1, 6)
    for (k, v), pr in law.items():
        code = {"target": 1, "stop": -1, "time": 0}[k]
        f = float(np.mean((kind == code) & np.isclose(val, float(v))))
        assert abs(f - pr) < 5 * np.sqrt(pr * (1 - pr) / 40000) + 1e-12, (k, v, f, pr)
    assert RD.walk_steps(1.0, 2.5, 1.0) == 3 and RD.walk_steps(1.0, 0.1, 1.0) == 1 and RD.walk_steps(2.0, 1.0, 2.0) == 1


def test_the_exit_state_map_is_r10s_and_refuses_any_other() -> None:
    assert set(RD.EXIT_LAW) == {"target", "stop", "stop_gap", "floor", "flatten", "news", "max_hold",
                                "profit_level", "other"}
    assert {k for k, v in RD.EXIT_LAW.items() if v == "race"} == {"target", "stop", "stop_gap", "floor", "profit_level"}
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
    assert got["clip_equal"] and got["clip_n"] >= 1000, got              # RB-1: the failed lane is the engine's loss



def test_s_c_the_walks_step_by_the_governing_rule() -> None:
    """s-c: s = max(1, ceil(sigma sqrt(T) / sqrt(1024))) ticks, so n = round(sigma^2 T / s^2) <= 1024, at the formula's
    cases; never a refusal because of the step (a bracket the step does not divide is walked)."""
    cases = ((1.0, 1.0, 1), (6.0, 90.0, 2), (8.0, 90.0, 3), (12.0, 90.0, 4), (32.0, 1.0, 1), (32.0, 1.0001, 2),
             (20.0, 400.0, 13), (0.5, 4000.0, 1))
    for sigma, T, want in cases:
        s = RD.walk_step(sigma, T)
        assert s == want, (sigma, T, s)
        assert RD.walk_steps(sigma, T, s) <= 1024, (sigma, T)
        if s > 1:
            assert RD.walk_steps(sigma, T, s - 1) > 1024 or sigma * sigma * T / (s - 1) ** 2 > 1024
    from extended import three_way_journey as J

    try:                                                    # a step dividing neither barrier is walked, never refused
        assert RD.walk_barriers(37, 55, Fraction(500), 0, 0, 3) == (Fraction(55), Fraction(37))
        J.Trade(session=0, decision=700, entry=705, exit=760, exit_reason="max_hold", g=55, l=37, tick_value=5.0,
                walk_step=3, walk_n=640)
    except ValueError as exc:
        pytest.fail(f"a trade refused because of its step: {exc}")


def test_s_c_a_coprime_bracket_matches_the_one_tick_lattice() -> None:
    """s-c: a 37 / 55 bracket at the coarse step its walk takes (sigma 8 ticks per sqrt minute; T 90: s = 3, n = 640;
    T 30: s = 2, n = 480), its barriers off the lattice and reached by the two-point last sub-step: P(stop) agrees with
    the one-tick lattice's (s = 1, n = sigma^2 T) within a tolerance of 1e-3, which is below the gap that rounding the
    barriers to the nearest lattice points (36 / 54 at s = 3, 36 / 56 at s = 2) would cause."""
    tol = 1e-3

    def p_stop(G, L, step, steps):
        law = RD.walk_law(float(G), float(L), step, steps)
        return sum(pr for (k, v), pr in law.items() if k == "stop")

    for T, want, rounded in ((90.0, (3, 640), (54, 36)), (30.0, (2, 480), (56, 36))):
        s = RD.walk_step(8.0, T)
        n = RD.walk_steps(8.0, T, s)
        assert (s, n) == want
        fine = p_stop(55, 37, 1, RD.walk_steps(8.0, T, 1))
        coarse = p_stop(55, 37, s, n)
        gap = abs(p_stop(*rounded, s, n) - fine)
        assert abs(coarse - fine) < tol < gap, (T, coarse, fine, gap)
