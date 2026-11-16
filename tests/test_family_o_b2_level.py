"""F-03 (family O, `prereg/F-03_opening_timing.md`) T-10, slow tier (an hour or more per setting, the second read's
n2-6): B2's machinery (`extended.opening_stats`) on synthetic data at declared levels (the first read's m7) -- a
synthetic population with a planted slow component and a clustered daily selection independent of it; the per-member
larger-of rule under `cons` at one-sided 1 % and 5 %; 2,000 outer replications, each B2 quantile from 20,000 inner
replicates. Outer replication j draws its judged block from `[20261988, 200, j, 0]` and its inner replicates from
`[20261988, 200, j, 1, i]` (section 16's test block, `[20261988, 200, j]`). **Failure rule:** the test fails if a
level's rejection rate has its 95 % Clopper-Pearson interval wholly above the nominal; a failure is kept on record and
runs the failure protocol, never a rerun to pass. The family's level rests on the larger-of rule at the family's
level, not on this test.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from extended import lift_bound as LB
from extended import opening_stats as ST

pytestmark = pytest.mark.slow

SEED = 20261988
OUTER, INNER = 2000, 20_000
LEVELS = (0.01, 0.05)
N_C, N_J, MARKS = 250, 250, 24


def synthetic(rng, n: int, slow_amp: float):
    sessions = [str(d.date()) for d in pd.bdate_range("2021-01-04", periods=n)]
    kinds = np.where(rng.random(n) < 0.15, "b", "n")
    rho = ST.slow_sign(rng, n)
    rows = []
    for i, s in enumerate(sessions):
        common = slow_amp * rho[i] + rng.normal(0, 0.25)
        for m in range(MARKS):
            rows.append((s, 5 * m, kinds[i], int(s[:4]), True, common + rng.normal(0, 0.8)))
    pop = pd.DataFrame(rows, columns=["date", "slot", "day_kind", "year", "population", "c"])
    return pop, sessions


def daily_selection(rng, n: int, run: float = 21.0, share: float = 1 / 3) -> np.ndarray:
    stay, enter = 1 - 1 / run, (1 / run) * share / (1 - share)
    s = np.zeros(n, bool)
    s[0] = rng.random() < share
    u = rng.random(n)
    for t in range(1, n):
        s[t] = (u[t] < stay) if s[t - 1] else (u[t] < enter)
    return s


@pytest.mark.parametrize("level", LEVELS)
def test_t10_the_larger_of_rule_holds_its_level_on_a_planted_slow_component(level):
    rej = 0
    for j in range(OUTER):
        rng = ST.rng_of(SEED, 200, j, 0)
        popc, sc = synthetic(rng, N_C, 0.15)
        Lc = ST.layout(popc, sc, values=("c",))
        yc = ST.centred(Lc, "c")
        popj, sj = synthetic(rng, N_J, 0.15)
        Lj = ST.layout(popj, sj, values=("c",))
        yj = ST.centred(Lj, "c")
        sel = daily_selection(rng, N_J)[:, None] & Lj.population
        inp = ST.B2Inputs(yc, Lc.kind, Lj.kind, Lj.group, Lj.exists, sel.astype(float), Lj.population.astype(float))
        a = ST.amplitude_a(Lc, yc, Lc.population)
        q, _ = ST.b2_quantiles(inp, a, level, 0, replicates=INNER, prefix=(SEED, 200, j, 1))
        rej += int(ST.c1_line(Lj, yj, sel, level, b2=q).passes)
    lo, hi = LB.clopper_pearson(rej, OUTER)
    print(f"\nT-10 at {level:.0%}: {rej} of {OUTER} rejected, rate {rej / OUTER:.4f} [{lo:.4f}, {hi:.4f}]")
    assert not lo > level
