# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M2-2: both resampling remedies (pair values in long blocks; sides in 63- and 126-session blocks) against the target quantile, four seeds -- the spread brackets the target both ways.

import numpy as np
from scipy import stats
Tj, Tc, m, B = 630, 1000, 24, 21; nb = Tj // B
a, q_d, s_eta, s_eps, q_s, p_in = 0.03, 1 / 120, 0.30, 0.35, 1 / 60, 0.80
tcrit = stats.t.ppf(0.99, nb - 1)
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def tstat(x):
    bm = x[:, :nb * B].reshape(len(x), nb, B).mean(2)
    return bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb))
def stationary_idx(rng, R, n_out, n_src, mean_block):
    idx = np.empty((R, n_out), dtype=np.int64); idx[:, 0] = rng.integers(0, n_src, R)
    new = rng.random((R, n_out)) < 1.0 / mean_block; fresh = rng.integers(0, n_src, (R, n_out))
    for t in range(1, n_out):
        idx[:, t] = np.where(new[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n_src)
    return idx
def side_means(rng, R, n):              # per-session mean side of the real-type process
    r = markov(rng, q_s, R, n)
    k = rng.binomial(m, np.where(r > 0, p_in, 1 - p_in))
    return (2 * k - m) / m
R = 4000
print("t_crit %.3f" % tcrit)
for seed in (41, 42, 43, 44):
    rng = np.random.default_rng(seed)
    A = side_means(rng, 1, Tj)[0]                                     # the judged side series (per-session mean)
    base_j = (a * markov(rng, q_d, 1, Tj) + s_eta * rng.standard_normal((1, Tj)))[0]   # the judged d (session part)
    base_c = (a * markov(rng, q_d, 1, Tc) + s_eta * rng.standard_normal((1, Tc)))[0]   # the choice block's d
    A_c = side_means(rng, 1, 750)[0]                                  # out-of-fold sides on the choice block
    noise = lambda: s_eps / np.sqrt(m) * rng.standard_normal((R, Tj))
    # unconditional null quantile (fresh sides and fresh d): the target
    q_unc = np.quantile(tstat(side_means(rng, R, Tj) * (a * markov(rng, q_d, R, Tj) + s_eta * rng.standard_normal((R, Tj))) + noise()), 0.99)
    # conditional on the judged sides (fresh d)
    q_cs = np.quantile(tstat(A * (a * markov(rng, q_d, R, Tj) + s_eta * rng.standard_normal((R, Tj))) + noise()), 0.99)
    out = ["seed %d q_unc %.3f q_cond_s %.3f" % (seed, q_unc, q_cs)]
    for L in (63, 126, 252):
        b = base_c[stationary_idx(rng, R, Tj, Tc, L)]; b = b - b.mean(1, keepdims=True)
        out.append("V2(d*,L=%d) %.3f" % (L, np.quantile(tstat(A * b + noise()), 0.99)))
    for L in (63, 126):
        s_star = A_c[stationary_idx(rng, R, Tj, 750, L)]
        out.append("V1(s*,L=%d) %.3f" % (L, np.quantile(tstat(s_star * base_j + noise()), 0.99)))
    print("  ".join(out))

# Printed (run 2026-11-16):
# t_crit 2.462
# seed 41 q_unc 2.681 q_cond_s 2.873  V2(d*,L=63) 2.529  V2(d*,L=126) 2.442  V2(d*,L=252) 2.606  V1(s*,L=63) 2.511  V1(s*,L=126) 2.382
# seed 42 q_unc 2.624 q_cond_s 2.859  V2(d*,L=63) 2.727  V2(d*,L=126) 2.756  V2(d*,L=252) 2.757  V1(s*,L=63) 2.852  V1(s*,L=126) 2.662
# seed 43 q_unc 2.672 q_cond_s 2.514  V2(d*,L=63) 2.398  V2(d*,L=126) 2.355  V2(d*,L=252) 2.515  V1(s*,L=63) 2.506  V1(s*,L=126) 2.425
# seed 44 q_unc 2.584 q_cond_s 2.720  V2(d*,L=63) 2.476  V2(d*,L=126) 2.736  V2(d*,L=252) 2.916  V1(s*,L=63) 2.440  V1(s*,L=126) 2.349
