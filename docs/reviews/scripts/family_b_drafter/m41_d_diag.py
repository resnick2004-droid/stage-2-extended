# Family B's drafter (Q-65): a scratch check behind prereg/DRAFT_F-B_multifeature.md (fifth version) -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing. Run with PYTHONPATH set to the
# worktree's root and its tests/ folder (it imports tests/test_family_b_b2.py's helpers).
# What it checks: M4-1: the diagnosis of the first run of the judged-block amplitude test -- the twin's term (d) alone fails where the twin's lift sat low through every judged year (kept on record: the test's first form failed, 0.0395 at 0.01).

import numpy as np
from scipy import stats
import test_family_b_b2 as T
# the (d) test, step by step
rng = np.random.default_rng([T.SEED, 65])
g_judged, a_choice = 0.03, 0.002
g_pre = 3 * a_choice
grid = np.round(np.arange(0.004, 0.0801, 0.004), 4)
q = T.follow_null_quantiles(rng, np.r_[g_pre, grid], T.R)
gt = g_judged * (1.0 + T.markov(rng, 1 / 250, T.R, T.FOLLOW_N))
truth = -2 * T.FOLLOW_Q_DIS * (gt - g_judged) + T.FOLLOW_SIG * rng.standard_normal((T.R, T.FOLLOW_N))
twin_obs = gt + T.FOLLOW_SIG * rng.standard_normal((T.R, T.FOLLOW_N))
years = (slice(0, 252), slice(252, 504), slice(504, T.FOLLOW_N))
d_term = np.max(np.abs(np.stack([twin_obs[:, y].mean(1) for y in years], 1)), 1)
t_by_b = T.component_t(truth)
nominal = np.array([stats.t.ppf(1 - T.ALPHA, t_by_b[b][1]) for b in T.COMPONENTS])
print("nominal", nominal.round(3), "pre", [round(q[g_pre][b], 3) for b in T.COMPONENTS])
print("d_term quantiles", np.quantile(d_term, [0.05, 0.25, 0.5, 0.75, 0.95]).round(4))
for g in (0.012, 0.02, 0.028, 0.032, 0.04, 0.06, 0.08):
    print(" q at", g, [round(q[g][b], 3) for b in T.COMPONENTS])
rows_v4 = np.tile(np.maximum(nominal, [q[g_pre][b] for b in T.COMPONENTS]), (T.R, 1))
g_post = np.maximum(g_pre, d_term)
idx = np.minimum(np.searchsorted(grid, g_post - 1e-12), len(grid) - 1)
post = np.array([[q[grid[i]][b] for b in T.COMPONENTS] for i in idx])
rows_v5 = np.maximum(np.maximum(nominal, [q[g_pre][b] for b in T.COMPONENTS]), post)
print("v4 rate", T._rate(t_by_b, rows_v4), "v5 rate", T._rate(t_by_b, rows_v5))
# rejections by d_term quartile under v5
rej = np.ones(T.R, dtype=bool)
for k, b in enumerate(T.COMPONENTS): rej &= t_by_b[b][0] > rows_v5[:, k]
for lo, hi in ((0, 0.02), (0.02, 0.03), (0.03, 0.045), (0.045, 1)):
    m = (d_term >= lo) & (d_term < hi); print("  d in [%.3f,%.3f): n %d rej %.4f" % (lo, hi, m.sum(), rej[m].mean() if m.any() else np.nan))
# the symmetric test
rng = np.random.default_rng([T.SEED, 66]); g = 0.03
gt = g * (1.0 + T.markov(rng, 1 / 250, T.R, T.FOLLOW_N)); ht = g * (1.0 + T.markov(rng, 1 / 250, T.R, T.FOLLOW_N))
truth = 2 * T.FOLLOW_Q_DIS * ((ht - g) - (gt - g)) + T.FOLLOW_SIG * rng.standard_normal((T.R, T.FOLLOW_N))
tb = T.component_t(truth)
nom = np.array([stats.t.ppf(1 - T.ALPHA, tb[b][1]) for b in T.COMPONENTS])
for sym in (False, True):
    qq = T.follow_null_quantiles(rng, [g], T.R, symmetric=sym)[g]
    print("sym", sym, "q", [round(qq[b], 3) for b in T.COMPONENTS], "rate", T._rate(tb, np.tile(np.maximum(nom, [qq[b] for b in T.COMPONENTS]), (T.R, 1))))
print("nominal-only rate", T._rate(tb, np.tile(nom, (T.R, 1))))

# Printed (run 2026-11-16):
# nominal [2.467 2.65  2.896] pre [2.741, 2.94, 3.133]
# d_term quantiles [0.012  0.0364 0.054  0.0641 0.0753]
# v4 rate 0.09425 v5 rate 0.0395
#   d in [0.000,0.020): n 432 rej 0.3426
#   d in [0.020,0.030): n 313 rej 0.0319
#   d in [0.030,0.045): n 671 rej 0.0000
#   d in [0.045,1.000): n 2584 rej 0.0000
# sym False q [5.934, 6.469, 6.896] rate 0.01275
# sym True q [7.894, 7.538, 7.689] rate 0.00625
# nominal-only rate 0.1135
