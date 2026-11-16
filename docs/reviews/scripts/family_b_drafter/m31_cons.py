# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M3-1: C1-f's boundary null under `cons` (21/42/63) -- nominal, B2 centred at E g, B2 recentred across replicates, at matched and halved amplitudes (seed 91).

# Scratch (exploratory): C1-f's boundary null under cons (21/42/63 trade-weighted CR1 t, all required), with B2.
import sys
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-scout")
import numpy as np
from scipy import stats
from extended import lift_bound as LB
TJ, Q_DIS, SIG, R, ALPHA = 609, 0.4, 0.13, 20000, 0.01
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def x_of(rng, n_rep, g_amp, centre):
    g = g_amp * (1.0 + markov(rng, 1 / 250, n_rep, TJ))
    return -2 * Q_DIS * (g - (g_amp if centre else 0.0)) + SIG * rng.standard_normal((n_rep, TJ))
def comp_t(x, b):                       # x (R, n) session values, N = 1 each
    S = x.T; N = np.ones_like(S)
    est, se, df = LB.t_stats(S, N, block=b, weight="trades"); return est / se, df
def cons_rej(x_true, x_null=None, recentre=False):
    rej = np.ones(x_true.shape[0], dtype=bool)
    for b in (21, 42, 63):
        t, df = comp_t(x_true, b); crit = stats.t.ppf(1 - ALPHA, df[0])
        if x_null is not None:
            tn, _ = comp_t(x_null, b)
            if recentre: tn = tn - tn.mean()
            crit = max(crit, float(np.quantile(tn, 1 - ALPHA)))
        rej &= t > crit
    return rej.mean()
rng = np.random.default_rng(91)
for g_j, g_c in ((0.02, 0.02), (0.02, 0.01), (0.03, 0.03), (0.03, 0.015)):
    xt = x_of(rng, R, g_j, True)
    print("g_J %.3f g_C %.3f | cons nominal %.4f | B2 centred %.4f | B2 across-replicates %.4f" % (
        g_j, g_c, cons_rej(xt), cons_rej(xt, x_of(rng, R, g_c, True)), cons_rej(xt, x_of(rng, R, g_c, False), True)))

# Printed (run 2026-11-16):
# g_J 0.020 g_C 0.020 | cons nominal 0.0607 | B2 centred 0.0042 | B2 across-replicates 0.0107
# g_J 0.020 g_C 0.010 | cons nominal 0.0613 | B2 centred 0.0272 | B2 across-replicates 0.0381
# g_J 0.030 g_C 0.030 | cons nominal 0.1102 | B2 centred 0.0027 | B2 across-replicates 0.0229
# g_J 0.030 g_C 0.015 | cons nominal 0.1100 | B2 centred 0.0437 | B2 across-replicates 0.0659
