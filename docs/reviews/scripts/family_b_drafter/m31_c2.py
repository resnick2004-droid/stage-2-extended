# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M3-1: C2's dollar-weighted per-trade mean under `cons`, with and without B2 (seeds 95-97).

# Scratch (exploratory): C2's dollar-weighted per-trade mean under cons, persistent sides x persistent drift, with B2.
import sys
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-scout")
import numpy as np
from scipy import stats
from extended import lift_bound as LB
TJ, TC, M, R, ALPHA = 609, 1000, 24, 4000, 0.01
S_ETA, S_EPS, P_IN = 0.30, 0.35, 0.80
DV, PROB = np.array([225.0, 1426.0, 629.0, 665.0]), np.array([0.40, 0.05, 0.30, 0.25])
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def sidx(rng, n_rep, n_out, n_src, L):
    idx = np.empty((n_rep, n_out), dtype=np.int64); idx[:, 0] = rng.integers(0, n_src, n_rep)
    new = rng.random((n_rep, n_out)) < 1.0 / L; fresh = rng.integers(0, n_src, (n_rep, n_out))
    for t in range(1, n_out): idx[:, t] = np.where(new[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n_src)
    return idx
def cons_rej(S_true, N, S_null=None):
    rej = np.ones(S_true.shape[1], dtype=bool)
    for b in (21, 42, 63):
        est, se, df = LB.t_stats(S_true, N, block=b); crit = stats.t.ppf(1 - ALPHA, df[0])
        if S_null is not None:
            e2, s2, _ = LB.t_stats(S_null, N[:, :S_null.shape[1]], block=b); crit = max(crit, float(np.quantile(e2 / s2, 1 - ALPHA)))
        rej &= est / se > crit
    return rej.mean()
for seed, (a, q_d, q_s) in ((95, (0.03, 1 / 120, 1 / 60)), (96, (0.03, 1 / 120, 1 / 60)), (97, (0.03, 1 / 250, 1 / 120))):
    rng = np.random.default_rng(seed)
    s = np.where(rng.random((TJ, M)) < np.where(markov(rng, q_s, 1, TJ)[0] > 0, P_IN, 1 - P_IN)[:, None], 1.0, -1.0)
    w = DV[rng.choice(4, size=(TJ, M), p=PROB)]
    aw = (w * s).sum(1); nw = S_EPS * np.sqrt((w ** 2).sum(1))           # S_s = base_s aw_s + noise
    N = np.full((TJ, R), float(M))
    true_S = (aw * (a * markov(rng, q_d, R, TJ) + S_ETA * rng.standard_normal((R, TJ))) + nw * rng.standard_normal((R, TJ))).T
    choice = (a * markov(rng, q_d, 1, TC) + S_ETA * rng.standard_normal((1, TC)))[0]
    a_star = np.max(np.abs(choice[:1000].reshape(4, 250).mean(1)))
    d = choice[sidx(rng, R, TJ, TC, 63)]; d = d - d.mean(1, keepdims=True) + a_star * markov(rng, 1 / 250, R, TJ)
    null_S = (aw * d + nw * rng.standard_normal((R, TJ))).T
    print(seed, "cons nominal %.4f | cons with B2 %.4f" % (cons_rej(true_S, N), cons_rej(true_S, N, null_S)))

# Printed (run 2026-11-16):
# 95 cons nominal 0.0043 | cons with B2 0.0015
# 96 cons nominal 0.0067 | cons with B2 0.0040
# 97 cons nominal 0.0198 | cons with B2 0.0027
