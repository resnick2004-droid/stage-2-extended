"""Q-185c: the `b` exit's law, FV3's breakeven move under the move-aware sequential race (`extended/three_way_move.py`).
Synthetic, engine-free, fast.

- the exact law is a law (probabilities sum to one) and its gross expectation is zero exactly, on a grid of barriers on
  and off the lattice, a fractional target (a profit level), a step dividing neither barrier, and walks of 1 to 40
  steps to the move bar;
- the sampler on given uniforms equals this file's own scalar sequential race path for path (the walk's uniforms, then
  one race uniform), and its frequencies match the exact law within four standard errors;
- the move's boundary: a walk exactly `FAVOUR` ticks in favour at the move bar moves its stop; one step short does not;
- all three exits occur.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
import pytest

from extended import three_way_move as MV
from extended import three_way_seeds as S

SEED = S.issue("tests")
GRID = [(Fraction(20), Fraction(10), 2, 5), (Fraction(19, 2), Fraction(37, 3), 3, 8), (Fraction(61), Fraction(41), 7, 40),
        (Fraction(6), Fraction(6), 1, 1), (Fraction(45, 4), Fraction(10), 5, 12)]


@pytest.mark.parametrize("G, L, s, n", GRID)
def test_the_exact_law_is_a_law_with_gross_zero(G, L, s, n):
    law = MV.move_law(G, L, s, n)
    assert sum(law.values()) == 1
    assert MV.move_gross(G, L, s, n) == 0
    assert all(k in ("target", "stop", "breakeven") for k, _ in law)


def _scalar(us, u_race, G, L, s, n, favour=MV.FAVOUR):
    """This file's own sequential race: the walk (two-point last sub-steps at both barriers), then the race."""
    s = Fraction(s)
    u = max(math.ceil(G / s) - 1, 0)
    d = max(math.ceil(L / s) - 1, 0)
    ru, rd = G - u * s, L - d * s
    i = 0
    for x in us[:n]:
        top, bot = i == u, i == -d
        q = rd / (ru + rd) if (top and bot) else s / (s + ru) if top else rd / (s + rd) if bot else Fraction(1, 2)
        up = Fraction(float(x)) < q
        if up and top:
            return MV.TARGET
        if not up and bot:
            return MV.STOP
        i += 1 if up else -1
    v = i * s
    if v >= favour:
        return MV.TARGET if Fraction(float(u_race)) < v / G else MV.BREAKEVEN
    return MV.TARGET if Fraction(float(u_race)) < (v + L) / (G + L) else MV.STOP


@pytest.mark.parametrize("G, L, s, n", GRID[1:3] + [(Fraction(10), Fraction(10), 1, 3)])
def test_the_sampler_is_the_sequential_race_path_for_path_and_matches_the_law(G, L, s, n):
    lanes = 20000 if n <= 12 else 4000
    rng = np.random.default_rng([int(SEED), 31, int(n)])
    U = rng.random((lanes, n))
    ur = rng.random(lanes)

    def read(rows, first, count):
        return U[rows][:, first:first + count]

    gross, kind = MV.move_outcomes(read, lanes, float(G), np.full(lanes, float(L)), s, n, ur)
    check = min(lanes, 1500)
    assert all(int(kind[j]) == _scalar(U[j], ur[j], G, L, s, n) for j in range(check))
    law = {k: float(p) for (k, _), p in MV.move_law(G, L, s, n).items()}
    for name, code in (("target", MV.TARGET), ("stop", MV.STOP), ("breakeven", MV.BREAKEVEN)):
        p = law.get(name, 0.0)
        got = float(np.mean(kind == code))
        assert abs(got - p) <= 4 * math.sqrt(max(p * (1 - p), 1e-12) / lanes) + 1e-12, (name, got, p)
    assert set(np.unique(kind)) == {MV.TARGET, MV.STOP, MV.BREAKEVEN}
    assert np.all(gross[kind == MV.BREAKEVEN] == 0.0)


def test_the_moves_boundary_is_one_tick_in_favour():
    # one step of 1 tick up: the walk stands exactly at +1 at the move bar -> moved (target with 1/G, else breakeven)
    law = MV.move_law(Fraction(10), Fraction(10), 1, 1)
    assert law[("breakeven", 0)] == Fraction(1, 2) * Fraction(9, 10)
    # the target: from +1 moved (1/10), or from -1 the race continuing between -10 and +10 ((-1 + 10) / 20)
    assert law[("target", Fraction(10))] == Fraction(1, 2) * Fraction(1, 10) + Fraction(1, 2) * Fraction(9, 20)
    # at +1 but a favour threshold of 2: not moved -- the race continues between -L and +G from +1
    law2 = MV.move_law(Fraction(10), Fraction(10), 1, 1, favour=2)
    assert ("breakeven", 0) not in law2
    assert law2[("target", Fraction(10))] == Fraction(1, 2) * Fraction(11, 20) + Fraction(1, 2) * Fraction(9, 20)
