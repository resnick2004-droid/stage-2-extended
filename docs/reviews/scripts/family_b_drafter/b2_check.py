# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M2-2: the long-block bootstrap of the choice block's pair values against the real judged sides (the review's preferred remedy) -- it does not reproduce the true conditional quantile.

# Scratch (exploratory): does B2 conditioned on the real side series, with a long-block bootstrap of the choice block's
# d, reproduce the conditional null of the 21-session block-means t in the red team's Appendix B design?
import numpy as np
from scipy import stats
Tj, Tc, m, B = 630, 1000, 24, 21; nb = Tj // B
a, q_d, s_eta, s_eps, q_s, p_in = 0.03, 1 / 120, 0.30, 0.35, 1 / 60, 0.80
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def tstat(x):                       # x: (R, T) session values
    bm = x[:, :nb * B].reshape(len(x), nb, B).mean(2)
    return bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb))
def stationary_idx(rng, R, n_out, n_src, mean_block):
    idx = np.empty((R, n_out), dtype=np.int64); idx[:, 0] = rng.integers(0, n_src, R)
    new = rng.random((R, n_out)) < 1.0 / mean_block; fresh = rng.integers(0, n_src, (R, n_out))
    for t in range(1, n_out):
        idx[:, t] = np.where(new[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n_src)
    return idx
for seed in (41, 42, 43):
    rng = np.random.default_rng(seed)
    r = markov(rng, q_s, 1, Tj)[0]
    S = np.where(rng.random((Tj, m)) < np.where(r > 0, p_in, 1 - p_in)[:, None], 1.0, -1.0)   # one judged side series
    A = S.mean(1)                                                     # per-session mean side
    R = 4000
    # true conditional null: fresh d (base_s + eps); x_s = mean_i s_i d_i = A_s base_s + mean_i s_i eps_i
    base = a * markov(rng, q_d, R, Tj) + s_eta * rng.standard_normal((R, Tj))
    x_true = A * base + s_eps / np.sqrt(m) * rng.standard_normal((R, Tj))
    q_true = np.quantile(tstat(x_true), 0.99)
    # B2: one choice-block d realisation, stationary bootstrap of sessions (mean block 63) to Tj, centred
    base_c = (a * markov(rng, q_d, 1, Tc) + s_eta * rng.standard_normal((1, Tc)))[0]
    idx = stationary_idx(rng, R, Tj, Tc, 63)
    bstar = base_c[idx]; bstar = bstar - bstar.mean(1, keepdims=True)
    x_b2 = A * bstar + s_eps / np.sqrt(m) * rng.standard_normal((R, Tj))
    q_b2 = np.quantile(tstat(x_b2), 0.99)
    # block length 21 for comparison
    idx21 = stationary_idx(rng, R, Tj, Tc, 21); b21 = base_c[idx21]; b21 = b21 - b21.mean(1, keepdims=True)
    q_b21 = np.quantile(tstat(A * b21 + s_eps / np.sqrt(m) * rng.standard_normal((R, Tj))), 0.99)
    print(seed, "t_crit %.3f  q_true %.3f  q_B2(63) %.3f  q_B2(21) %.3f  rej_true_at_tcrit %.4f  rej_true_at_B2 %.4f" % (
        stats.t.ppf(0.99, nb - 1), q_true, q_b2, q_b21, np.mean(tstat(x_true) > stats.t.ppf(0.99, nb - 1)),
        np.mean(tstat(x_true) > max(q_b2, stats.t.ppf(0.99, nb - 1)))))

# Printed (run 2026-11-16):
# seed 41 t_crit 2.462  q_true 2.925  q_B2(63) 2.462  q_B2(21) 2.304  rej_true_at_tcrit 0.0240  rej_true_at_B2 0.0240
# seed 42 t_crit 2.462  q_true 2.662  q_B2(63) 2.314  q_B2(21) 2.256  rej_true_at_tcrit 0.0140  rej_true_at_B2 0.0140
# seed 43 t_crit 2.462  q_true 2.540  q_B2(63) 2.408  q_B2(21) 2.397  rej_true_at_tcrit 0.0112  rej_true_at_B2 0.0112
