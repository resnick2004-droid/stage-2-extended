"""Q-185c (C3-2): the common-path law for rungs of one alert (`extended/three_way_rungs.py`). Synthetic, engine-free.

- **exact marginals for an untimed rung:** on 20,000 paths each rung's target share is its bracket's driftless odds
  L / (L + G) within four standard errors, at fractional barriers and two lattice steps (the step changes no odds);
- **one path, not independent draws:** two rungs (50, 100) and (100, 200) ticks -- the red team's `rungs.py` pair --
  stop together more often than independent draws and their summed ticks spread wider (printed beside: a check of the
  law, not a result);
- **time-limited rungs within the declared tolerance** (`TIMED_TOL`, fixed) of their own single-trade law (R-10's walk
  and the time-limited move at their own step, exact by `walk_law` / `move_law`), on a declared grid;
- **zero gross** for every law on the path, within four standard errors;
- **the refusal** of a rung whose barriers are closer than two steps; the extremes' law at its ends.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
import pytest

from extended import three_way_move as MV
from extended import three_way_redraw as RD
from extended import three_way_rungs as RG
from extended import three_way_seeds as S

SEED = S.issue("tests")
N = 20000


def _paths(n: int, h: float, tag: int) -> list[RG.CommonPath]:
    rng = np.random.default_rng([int(SEED), 197, int(tag)])
    out = []
    for _ in range(n):
        g = np.random.default_rng(rng.integers(0, 2 ** 32 - 1, 2))

        def read(first, count, _g=g, _buf=[]):
            while len(_buf) < first + count:
                _buf.extend(_g.random(256).tolist())
            return np.asarray(_buf[first:first + count])

        out.append(RG.CommonPath(read, float(h)))
    return out


@pytest.mark.parametrize("L, G, h", [(50.0, 100.0, 5.0), (37.3, 61.0, 7.0), (37.3, 61.0, 1.0), (12.5, 80.0, 3.0),
                                     (21.0, 37.5, 10.0)])     # both barriers off a coarse lattice: both extremes read
def test_an_untimed_rungs_odds_are_its_brackets_exactly(L, G, h):
    paths = _paths(N if h > 1 else 4000, h, int(L * 10 + h))
    k = np.array([RG.race(p, L, G)[0] for p in paths])
    p = L / (L + G)
    got = float(np.mean(k == RG.TARGET))
    assert abs(got - p) <= 4 * math.sqrt(p * (1 - p) / len(paths)), (got, p)


def test_two_rungs_on_one_path_are_not_independent():
    paths = _paths(N, 5.0, 5)
    a = np.array([RG.race(p, 50.0, 100.0)[1] for p in paths])
    b = np.array([RG.race(p, 100.0, 200.0)[1] for p in paths])
    both = float(np.mean((a < 0) & (b < 0)))
    pa, pb = float(np.mean(a < 0)), float(np.mean(b < 0))
    sd_common = float(np.std(a + b))
    rng = np.random.default_rng([int(SEED), 198])
    ia = np.where(rng.random(N) < pa, -50.0, 100.0)
    ib = np.where(rng.random(N) < pb, -100.0, 200.0)
    sd_indep = float(np.std(ia + ib))
    print(f"\ncommon path: P(both stopped) {both:.4f}, sd(sum) {sd_common:.1f}; independent: {pa * pb:.4f}, "
          f"{sd_indep:.1f}")
    assert both > pa * pb + 0.05 and sd_common > sd_indep * 1.08
    assert abs(pa - 100.0 / 150.0) < 0.02 and abs(pb - 200.0 / 300.0) < 0.02     # each rung's own odds


def _single_walk(L, G, s, n):
    law = RD.walk_law(Fraction(G), Fraction(L).limit_denominator(10 ** 6), s, n)
    out = {"target": 0.0, "stop": 0.0, "time": 0.0}
    for (k, _), pr in law.items():
        out[k] += float(pr)
    return out


GRID_WALK = [(40.0, 60.0, 1.5, 420.0, 900.0), (37.3, 80.0, 6.0, 300.0, 1000.0), (100.0, 150.0, 6.0, 1000.0, 1000.0)]


@pytest.mark.parametrize("L, G, sigma, T, T_max", GRID_WALK)
def test_a_time_limited_rung_is_within_the_tolerance_of_its_own_law(L, G, sigma, T, T_max):
    s_own = RD.walk_step(sigma, T)
    n_own = RD.walk_steps(sigma, T, s_own)
    h = RD.walk_step(sigma, T_max)
    n = RD.walk_steps(sigma, T, h)
    ref = _single_walk(L, G, s_own, n_own)
    paths = _paths(N, h, int(L + T))
    k = np.array([RG.walk(p, L, G, n)[0] for p in paths])
    for name, code in (("target", RG.TARGET), ("stop", RG.STOP), ("time", RG.TIME)):
        assert abs(float(np.mean(k == code)) - ref[name]) < RG.TIMED_TOL, (name, float(np.mean(k == code)), ref[name])


def test_a_move_rung_is_within_the_tolerance_of_its_own_law_and_its_gross_is_zero():
    L, G, sigma, d1, d2 = 40.0, 60.0, 1.5, 260.0, 129.0
    h = RD.walk_step(sigma, d1 + d2)
    s1, s2 = RD.walk_step(sigma, d1), RD.walk_step(sigma, d2)
    law = MV.move_law(Fraction(G), Fraction(L), s1, RD.walk_steps(sigma, d1, s1), s2, RD.walk_steps(sigma, d2, s2))
    ref = {}
    for (k, _), pr in law.items():
        ref[k] = ref.get(k, 0.0) + float(pr)
    paths = _paths(N, h, 77)
    res = [RG.move(p, L, G, RD.walk_steps(sigma, d1, h), RD.walk_steps(sigma, d2, h)) for p in paths]
    kinds = np.array([r[0] for r in res])
    gross = np.array([r[1] for r in res])
    for name, code in (("target", RG.TARGET), ("stop", RG.STOP), ("breakeven", RG.BREAKEVEN), ("time", RG.TIME)):
        assert abs(float(np.mean(kinds == code)) - ref.get(name, 0.0)) < RG.TIMED_TOL, name
    assert abs(float(np.mean(gross))) < 4 * float(np.std(gross)) / math.sqrt(N)


def test_the_race_and_the_walk_have_zero_gross_on_the_path():
    paths = _paths(N, 4.0, 9)
    g = np.array([RG.race(p, 37.3, 61.0)[1] for p in paths])
    w = np.array([RG.walk(p, 37.3, 61.0, 200)[1] for p in paths])
    for x in (g, w):
        assert abs(float(np.mean(x))) < 4 * float(np.std(x)) / math.sqrt(N)


def test_the_refusals_and_the_extremes_law():
    p = _paths(1, 10.0, 3)[0]
    with pytest.raises(ValueError, match="half a rung"):
        RG.race(p, 5.0, 12.0)                                         # barriers 17 ticks apart, step 10
    p._extend(4000)
    lo, hi, x = np.array(p.lo[1:]), np.array(p.hi[1:]), np.array(p.x)
    up = np.diff(x) > 0
    # every step's range holds its start and its end; the extreme lies strictly within one step on the other side
    assert np.all(lo <= x[:-1] + 1e-12) and np.all(hi >= x[:-1] - 1e-12)
    assert np.all(lo[up] > x[:-1][up] - 10.0) and np.all(hi[~up] < x[:-1][~up] + 10.0)
    # the up steps' minimum: P(m <= x - 5) = (5) / (15) = 1/3, sampled
    share = float(np.mean(lo[up] <= x[:-1][up] - 5.0))
    assert abs(share - 1.0 / 3.0) < 4 * math.sqrt((1 / 3) * (2 / 3) / int(up.sum()))
    # the down steps' maximum mirrors it: P(M >= x + 5) = 1/3
    share = float(np.mean(hi[~up] >= x[:-1][~up] + 5.0))
    assert abs(share - 1.0 / 3.0) < 4 * math.sqrt((1 / 3) * (2 / 3) / int((~up).sum()))
