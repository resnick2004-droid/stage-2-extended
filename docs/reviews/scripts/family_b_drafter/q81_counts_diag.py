# Family B's drafter (Q-81): a scratch check behind prereg/DRAFT_F-B_multifeature.md (sixth version) -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing. Run with PYTHONPATH set to the
# worktree's root and its tests/ folder (it imports tests/test_family_b_level_power.py's reference `count_check`).
# What it checks: the diagnosis of the first run of `test_the_fill_intensity_check`, which FAILED (kept on record):
# its one seeded AR(1) 0.98 / sd 1.5 count path (mean 2 a session, 1,000 sessions) was not killed -- rate 0.000300,
# 95 % interval [0.000202, 0.000428] against the level 0.000321. The pass-line review's lax figures for that profile
# are unconditional (a fresh path every replication); the declared check is conditional on the cell's own path.
# Here: ten paths of the same profile (seeds [20261968, 131, i]), the check on each (100,000 replications,
# [20261968, 132, i]), each path's concentration; and the unconditional rate (a fresh path every replication,
# 100,000 replications, [20261968, 133]).

import math

import numpy as np
from scipy import stats

import test_family_b_level_power as P
from extended import lift_bound as LB

PHI, SD, MEAN, N_C, N_J = 0.98, 1.5, 2.0, 1000, 609


def path(rng, n=N_C):
    z = np.empty(n)
    z[0] = SD * rng.standard_normal()
    for t in range(1, n):
        z[t] = PHI * z[t - 1] + SD * math.sqrt(1 - PHI * PHI) * rng.standard_normal()
    return rng.poisson(MEAN * np.exp(z - SD * SD / 2))


def concentration(c):
    top63 = max(c[i:i + 63].sum() for i in range(c.size - 62)) / c.sum()
    srt = np.sort(c)[::-1]
    top5 = srt[: c.size // 20].sum() / c.sum()
    return top63, top5, c.max() / c.sum()


print(f"level {P.LEVEL:.6f}")
for i in range(10):
    c = path(np.random.default_rng([P.SEED, 131, i]))
    r, ci, killed = P.count_check(c, 100_000, np.random.default_rng([P.SEED, 132, i]))
    t63, t5, mx = concentration(c)
    print(f"path {i}: fills {c.sum()}, top-63 share {t63:.2f}, top-5% sessions' share {t5:.2f}, largest session "
          f"{mx:.3f}; rate {r:.6f} ({r / P.LEVEL:.2f}x) CI [{ci[0]:.6f}, {ci[1]:.6f}] killed {killed}")

# unconditional: a fresh path every replication (the review's setting), 609 sessions
rng = np.random.default_rng([P.SEED, 133])
k, n_rep = 0, 100_000
for n in P.chunks(n_rep, 2000):
    z = np.empty((N_J, n))
    z[0] = SD * rng.standard_normal(n)
    for t in range(1, N_J):
        z[t] = PHI * z[t - 1] + SD * math.sqrt(1 - PHI * PHI) * rng.standard_normal(n)
    N = rng.poisson(MEAN * np.exp(z - SD * SD / 2))
    a = math.sqrt(0.35) * rng.standard_normal((N_J, n))
    up = rng.binomial(N, stats.norm.cdf(a / math.sqrt(0.65)))
    S = 0.5 * (2 * up - N)
    rej = np.ones(n, dtype=bool)
    for b in P.COMPONENTS:
        est, se, df = LB.t_stats(S, N.astype(float), block=b, weight="trades")
        with np.errstate(invalid="ignore", divide="ignore"):
            c = stats.t.ppf(1 - P.LEVEL, np.where(df > 0, df, 1))
            rej &= (df > 0) & (se > 0) & (np.nan_to_num(est / se, nan=-np.inf) > c)
    k += int(rej.sum())
lo, hi = LB.clopper_pearson(k, n_rep)
print(f"unconditional (fresh path each replication): rate {k / n_rep:.6f} ({k / n_rep / P.LEVEL:.2f}x) "
      f"CI [{lo:.6f}, {hi:.6f}]")

# Printed (run 2026-11-16, 1 min 50 s, one thread):
# level 0.000321
# path 0: fills 2993, top-63 share 0.18, top-5% sessions' share 0.36, largest session 0.019; rate 0.000610 (1.90x) CI [0.000467, 0.000784] killed True
# path 1: fills 1292, top-63 share 0.20, top-5% sessions' share 0.32, largest session 0.010; rate 0.000120 (0.37x) CI [0.000062, 0.000210] killed False
# path 2: fills 1712, top-63 share 0.22, top-5% sessions' share 0.31, largest session 0.025; rate 0.000140 (0.44x) CI [0.000077, 0.000235] killed False
# path 3: fills 3845, top-63 share 0.36, top-5% sessions' share 0.42, largest session 0.017; rate 0.000960 (3.00x) CI [0.000778, 0.001172] killed True
# path 4: fills 1445, top-63 share 0.50, top-5% sessions' share 0.47, largest session 0.020; rate 0.000700 (2.18x) CI [0.000546, 0.000884] killed True
# path 5: fills 3895, top-63 share 0.37, top-5% sessions' share 0.38, largest session 0.018; rate 0.000940 (2.93x) CI [0.000760, 0.001150] killed True
# path 6: fills 3957, top-63 share 0.27, top-5% sessions' share 0.36, largest session 0.012; rate 0.000530 (1.65x) CI [0.000397, 0.000693] killed True
# path 7: fills 891, top-63 share 0.16, top-5% sessions' share 0.29, largest session 0.011; rate 0.000090 (0.28x) CI [0.000041, 0.000171] killed False
# path 8: fills 1610, top-63 share 0.22, top-5% sessions' share 0.29, largest session 0.010; rate 0.000200 (0.62x) CI [0.000122, 0.000309] killed False
# path 9: fills 2254, top-63 share 0.34, top-5% sessions' share 0.34, largest session 0.014; rate 0.000310 (0.97x) CI [0.000211, 0.000440] killed False
# unconditional (fresh path each replication): rate 0.000780 (2.43x) CI [0.000617, 0.000973]
