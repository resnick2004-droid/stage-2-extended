# Family B's drafter (Q-65): a scratch check behind prereg/DRAFT_F-B_multifeature.md (fifth version) -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing. Run with PYTHONPATH set to the
# worktree's root and its tests/ folder (it imports tests/test_family_b_b2.py's helpers).
# What it checks: m4-3: the confirmation's t21w at one-sided 0.05 on 126 and 252 sessions, B2 over the development window, with and without a 1.3 x nominal floor (12 side series per design).

# Scratch (exploratory): the confirmation's t21w at 0.05 with B2 resampling the development window (2020-2026, about
# 1,630 sessions) and a* the largest absolute calendar-year mean over its years; per judged side series.
import sys
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-scout\tests")
import numpy as np
from scipy import stats
import test_family_b_b2 as T
def case(seed, TJ, a, q_d, q_s, alpha=0.05, R=4000, M=24, TD=1630, floor=1.0):
    rng = np.random.default_rng(seed)
    offers = np.where(rng.random((TJ, M)) < np.where(T.markov(rng, q_s, 1, TJ)[0] > 0, T.P_IN, 1 - T.P_IN)[:, None], 1, -1)
    A = offers.mean(1); noise = lambda: T.S_EPS / np.sqrt(M) * rng.standard_normal((R, TJ))
    true_x = A * (a * T.markov(rng, q_d, R, TJ) + T.S_ETA * rng.standard_normal((R, TJ))) + noise()
    dev = (a * T.markov(rng, q_d, 1, TD) + T.S_ETA * rng.standard_normal((1, TD)))[0]
    a_star = np.max(np.abs(dev[: (TD // 252) * 252].reshape(-1, 252).mean(1)))
    d = dev[T.stationary_idx(rng, R, TJ, TD, 63)]; d = d - d.mean(1, keepdims=True) + a_star * T.markov(rng, 1 / 250, R, TJ)
    t_true, nb = T.tstat(true_x, 21); t_b2, _ = T.tstat(A * d + noise(), 21)
    nominal = stats.t.ppf(1 - alpha, nb - 1); crit = max(floor * nominal, float(np.quantile(t_b2, 1 - alpha)))
    return np.mean(t_true > nominal), np.mean(t_true > crit)
for TJ in (126, 252):
    for name, cfg in (("REVIEW", T.REVIEW), ("SLOWER", T.SLOWER)):
        for floor in (1.0, 1.3):
            r = np.array([case([8201, TJ, j, int(name == "SLOWER")], TJ, **cfg, floor=floor) for j in range(12)])
            print(TJ, name, "floor %.1f: nominal %.4f (max %.4f) | B2 %.4f (max %.4f)" % (floor, r[:, 0].mean(), r[:, 0].max(), r[:, 1].mean(), r[:, 1].max()))

# Printed (run 2026-11-16):
# 126 REVIEW floor 1.0: nominal 0.0608 (max 0.0772) | B2 0.0464 (max 0.0767)
# 126 REVIEW floor 1.3: nominal 0.0608 (max 0.0772) | B2 0.0289 (max 0.0423)
# 126 SLOWER floor 1.0: nominal 0.0712 (max 0.1008) | B2 0.0548 (max 0.1008)
# 126 SLOWER floor 1.3: nominal 0.0712 (max 0.1008) | B2 0.0326 (max 0.0517)
# 252 REVIEW floor 1.0: nominal 0.0579 (max 0.0705) | B2 0.0414 (max 0.0525)
# 252 REVIEW floor 1.3: nominal 0.0579 (max 0.0705) | B2 0.0249 (max 0.0285)
# 252 SLOWER floor 1.0: nominal 0.0894 (max 0.1298) | B2 0.0439 (max 0.1017)
# 252 SLOWER floor 1.3: nominal 0.0894 (max 0.1298) | B2 0.0340 (max 0.0607)
