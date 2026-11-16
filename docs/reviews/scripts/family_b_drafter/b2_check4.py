# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M2-2: 63-session blocks at half the level, on the review's design and a slower stress design.

import numpy as np
from scipy import stats
Tj, m = 630, 24
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def run(seed, a, q_d, q_s, p_in=0.8, s_eta=0.30, s_eps=0.35, R=40000, B=63):
    rng = np.random.default_rng(seed); nb = Tj // B; acc = np.zeros(4); al = (0.01, 0.005, 0.001, 0.0005)
    for _ in range(R // 4000):
        n = 4000
        r = markov(rng, q_s, n, Tj); A = (2 * rng.binomial(m, np.where(r > 0, p_in, 1 - p_in)) - m) / m
        x = A * (a * markov(rng, q_d, n, Tj) + s_eta * rng.standard_normal((n, Tj))) + s_eps / np.sqrt(m) * rng.standard_normal((n, Tj))
        bm = x[:, :nb * B].reshape(n, nb, B).mean(2); t = bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb))
        acc += np.array([np.mean(t > stats.t.ppf(1 - x_, nb - 1)) for x_ in al]) * n
    return dict(zip(al, (acc / R).round(5)))
print("review case (a .03, drift 1/120, side 1/60), 63-blocks:", run(61, 0.03, 1/120, 1/60))
print("slower stress (a .03, drift 1/250, side 1/120), 63-blocks:", run(62, 0.03, 1/250, 1/120))
print("slower stress, 21-blocks:", run(63, 0.03, 1/250, 1/120, B=21))
print("t crit df 9 at 0.05/132 and half:", round(stats.t.ppf(1 - 0.05/132, 9), 2), round(stats.t.ppf(1 - 0.025/132, 9), 2))

# Printed (run 2026-11-16):
# review case (a .03, drift 1/120, side 1/60), 63-blocks: {0.01: 0.01088, 0.005: 0.00572, 0.001: 0.0012, 0.0005: 0.0006}
# slower stress (a .03, drift 1/250, side 1/120), 63-blocks: {0.01: 0.01787, 0.005: 0.0095, 0.001: 0.00198, 0.0005: 0.0012}
# slower stress, 21-blocks: {0.01: 0.02568, 0.005: 0.0151, 0.001: 0.0043, 0.0005: 0.00252}
# t crit df 9 at 0.05/132 and half: 4.98 5.5
