# Family B's drafter (Q-65): a scratch check behind prereg/DRAFT_F-B_multifeature.md (fifth version) -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing. Run with PYTHONPATH set to the
# worktree's root and its tests/ folder (it imports tests/test_family_b_b2.py's helpers).
# What it checks: m4-2: the persistence flag -- the rolling 126/21 variance ratio of the per-session mean side against its permutation null's 95th percentile, on 609 sessions.

# Scratch (exploratory): the persistence flag -- rolling 126/21 variance ratio of the per-session mean side, flagged
# above the 95th percentile of the same ratio over permutations of the sessions (2,000), on 609 sessions.
import numpy as np
T = 609
def markov(rng, q, n):
    sw = rng.random(n) < q; sw[0] = rng.random() < 0.5
    return np.where(np.cumsum(sw) % 2 == 0, 1.0, -1.0)
def ratio(m):
    c = np.concatenate([[0.0], np.cumsum(m)])
    r126 = (c[126:] - c[:-126]) / 126; r21 = (c[21:] - c[:-21]) / 21
    return r126.var() / r21.var()
def flag(rng, m, P=2000):
    obs = ratio(m); null = np.array([ratio(rng.permutation(m)) for _ in range(P)])
    return obs > np.quantile(null, 0.95)
rng = np.random.default_rng(8101)
for lam, q in ((0.0, 1 / 63), (0.1, 1 / 63), (0.2, 1 / 63), (0.3, 1 / 63), (0.3, 1 / 250)):
    hits = [flag(rng, lam * markov(rng, q, T) + 0.3 * rng.standard_normal(T), P=400) for _ in range(300)]
    print("lam %.1f q 1/%d: flagged %.3f" % (lam, round(1 / q), np.mean(hits)))

# Printed (run 2026-11-16):
# lam 0.0 q 1/63: flagged 0.053
# lam 0.1 q 1/63: flagged 0.507
# lam 0.2 q 1/63: flagged 0.703
# lam 0.3 q 1/63: flagged 0.703
# lam 0.3 q 1/250: flagged 0.767
