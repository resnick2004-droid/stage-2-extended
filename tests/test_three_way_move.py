"""Q-185c: FV3's breakeven move under the time-limited move-aware sequential race (`extended/three_way_move.py`).
Synthetic, engine-free, fast.

- the exact law is a law (probabilities sum to one) and its gross expectation is zero exactly, on a grid of barriers on
  and off the lattices, a fractional target, steps dividing neither barrier, and phases of 1 to 40 steps;
- the sampler on given uniforms equals this file's own scalar sequential walk path for path (phase 1 on the stream's
  first n1 uniforms, phase 2 on the next n2), and its frequencies match the exact law within four standard errors;
- the move's boundary: a walk exactly `FAVOUR` ticks in favour at the move bar moves its stop; below it does not;
- phase 2 is bounded by the limit: time exits occur after the move bar, moved and not.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
import pytest

from extended import three_way_move as MV
from extended import three_way_seeds as S

SEED = S.issue("tests")
#: (G, L, s1, n1, s2, n2)
GRID = [(Fraction(20), Fraction(10), 2, 5, 3, 4), (Fraction(19, 2), Fraction(37, 3), 3, 8, 2, 6),
        (Fraction(61), Fraction(41), 7, 40, 9, 30), (Fraction(6), Fraction(6), 1, 1, 1, 1),
        (Fraction(45, 4), Fraction(10), 5, 12, 4, 7)]


@pytest.mark.parametrize("G, L, s1, n1, s2, n2", GRID)
def test_the_exact_law_is_a_law_with_gross_zero(G, L, s1, n1, s2, n2):
    law = MV.move_law(G, L, s1, n1, s2, n2)
    assert sum(law.values()) == 1
    assert MV.move_gross(G, L, s1, n1, s2, n2) == 0
    assert {k for k, _ in law} <= {"target", "stop", "breakeven", "time"}


def _walk(us, G, L, s):
    """This file's own stopped walk on given uniforms (two-point last sub-steps at both barriers): (value, kind)."""
    s = Fraction(s)
    u = max(math.ceil(G / s) - 1, 0)
    d = max(math.ceil(L / s) - 1, 0)
    ru, rd = G - u * s, L - d * s
    i = 0
    for x in us:
        top, bot = i == u, i == -d
        q = rd / (ru + rd) if (top and bot) else s / (s + ru) if top else rd / (s + rd) if bot else Fraction(1, 2)
        up = Fraction(float(x)) < q
        if up and top:
            return G, MV.TARGET
        if not up and bot:
            return -L, MV.STOP
        i += 1 if up else -1
    return i * s, MV.TIME


def _scalar(us, G, L, s1, n1, s2, n2, favour=MV.FAVOUR):
    v, k = _walk(us[:n1], G, L, s1)
    if k != MV.TIME:
        return k
    moved = v >= favour
    v2, k2 = _walk(us[n1:n1 + n2], G - v, v if moved else v + L, s2)
    if k2 == MV.STOP:
        return MV.BREAKEVEN if moved else MV.STOP
    return k2


@pytest.mark.parametrize("G, L, s1, n1, s2, n2", [GRID[1], GRID[2], (Fraction(10), Fraction(10), 1, 3, 1, 4)])
def test_the_sampler_is_the_sequential_walk_path_for_path_and_matches_the_law(G, L, s1, n1, s2, n2):
    lanes = 20000 if n1 + n2 <= 20 else 4000
    rng = np.random.default_rng([int(SEED), 31, int(n1), int(n2)])
    U = rng.random((lanes, n1 + n2))

    def read(rows, first, count):
        return U[rows][:, first:first + count]

    gross, kind = MV.move_outcomes(read, lanes, float(G), float(L), s1, n1, s2, n2)
    check = min(lanes, 1500)
    assert all(int(kind[j]) == _scalar(U[j], G, L, s1, n1, s2, n2) for j in range(check))
    law: dict[str, float] = {}
    for (k, _), p in MV.move_law(G, L, s1, n1, s2, n2).items():
        law[k] = law.get(k, 0.0) + float(p)
    for name, code in (("target", MV.TARGET), ("stop", MV.STOP), ("breakeven", MV.BREAKEVEN), ("time", MV.TIME)):
        p = law.get(name, 0.0)
        got = float(np.mean(kind == code))
        assert abs(got - p) <= 4 * math.sqrt(max(p * (1 - p), 1e-12) / lanes) + 1e-12, (name, got, p)
    codes = {"target": MV.TARGET, "stop": MV.STOP, "breakeven": MV.BREAKEVEN, "time": MV.TIME}
    assert {codes[k] for k, p in law.items() if p > 0.001} <= set(np.unique(kind))    # every kind the law weighs
    assert law.get("breakeven", 0) > 0 and law.get("time", 0) > 0
    assert np.all(gross[kind == MV.BREAKEVEN] == 0.0)
    assert abs(float(np.mean(gross))) < 4 * float(np.std(gross)) / math.sqrt(lanes) + 1e-12   # zero mean, sampled


def test_the_moves_boundary_is_one_tick_in_favour():
    # one step of 1 tick: at +1 the stop moves (phase 2 between 0 and +10 for one step), at -1 it does not
    law = MV.move_law(Fraction(10), Fraction(10), 1, 1, 1, 1)
    assert law[("breakeven", 0)] == Fraction(1, 2) * Fraction(1, 2)       # from +1, one step down to 0
    assert law[("time", Fraction(2))] == Fraction(1, 2) * Fraction(1, 2)
    assert law[("time", Fraction(-2))] == Fraction(1, 2) * Fraction(1, 2)  # from -1, unmoved, one step down
    law2 = MV.move_law(Fraction(10), Fraction(10), 1, 1, 1, 1, favour=2)  # +1 below a two-tick threshold: unmoved
    assert ("breakeven", 0) not in law2 and law2[("time", Fraction(0))] == Fraction(1, 2)
