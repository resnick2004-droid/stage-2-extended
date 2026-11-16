# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M2-2: the size of Student-t on 21-, 63- and 126-session block means on the review's persistent design (40,000 replications).

import numpy as np
from scipy import stats
Tj, m = 630, 24
a, q_d, s_eta, s_eps, q_s, p_in = 0.03, 1 / 120, 0.30, 0.35, 1 / 60, 0.80
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def side_means(rng, R, n):
    r = markov(rng, q_s, R, n); k = rng.binomial(m, np.where(r > 0, p_in, 1 - p_in)); return (2 * k - m) / m
def rej(x, B, alphas):
    nb = x.shape[1] // B; bm = x[:, :nb * B].reshape(len(x), nb, B).mean(2)
    t = bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb))
    return [np.mean(t > stats.t.ppf(1 - al, nb - 1)) for al in alphas]
rng = np.random.default_rng(51)
R, tot = 40000, {}
for case in ("iid", "real"):
    acc = {B: np.zeros(2) for B in (21, 63, 126)}
    for _ in range(R // 4000):
        n = 4000
        A = rng.binomial(m, 0.5, (n, Tj)) * 2 / m - 1 if case == "iid" else side_means(rng, n, Tj)
        x = A * (a * markov(rng, q_d, n, Tj) + s_eta * rng.standard_normal((n, Tj))) + s_eps / np.sqrt(m) * rng.standard_normal((n, Tj))
        for B in acc: acc[B] += np.array(rej(x, B, (0.01, 0.001))) * n
    print(case, {B: (acc[B] / R).round(4).tolist() for B in acc})
for B in (21, 63, 126):
    nb = Tj // B; print("block", B, "df", nb - 1, "t crit at 0.05/132:", round(stats.t.ppf(1 - 0.05 / 132, nb - 1), 2))

# Printed (run 2026-11-16):
# iid {21: [0.0093, 0.0012], 63: [0.0093, 0.001], 126: [0.0101, 0.0009]}
# real {21: [0.0156, 0.002], 63: [0.0117, 0.0012], 126: [0.0103, 0.0009]}
# block 21 df 29 t crit at 0.05/132: 3.76
# block 63 df 9 t crit at 0.05/132: 4.98
# block 126 df 4 t crit at 0.05/132: 9.26
