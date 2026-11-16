# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M2-2: the same on 21-session blocks (the confirmation's form).

# Stress-calibrated critical value conditional on the real judged sides (scratch, exploratory).
import numpy as np
from scipy import stats
Tj, Tc, m, B = 630, 1000, 24, 21; nb = Tj // B
s_eta, s_eps, p_in = 0.30, 0.35, 0.80
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def tstat(x):
    bm = x[:, :nb * B].reshape(len(x), nb, B).mean(2); return bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb))
def sidx(rng, R, n_out, n_src, L):
    idx = np.empty((R, n_out), dtype=np.int64); idx[:, 0] = rng.integers(0, n_src, R)
    new = rng.random((R, n_out)) < 1.0 / L; fresh = rng.integers(0, n_src, (R, n_out))
    for t in range(1, n_out): idx[:, t] = np.where(new[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n_src)
    return idx
def case(seed, a, q_d, q_s, R=20000):
    rng = np.random.default_rng(seed)
    r = markov(rng, q_s, 1, Tj)[0]; A = (2 * rng.binomial(m, np.where(r > 0, p_in, 1 - p_in)) - m) / m
    noise = lambda n: s_eps / np.sqrt(m) * rng.standard_normal((n, Tj))
    t_true = tstat(A * (a * markov(rng, q_d, R, Tj) + s_eta * rng.standard_normal((R, Tj))) + noise(R))
    base_c = (a * markov(rng, q_d, 1, Tc) + s_eta * rng.standard_normal((1, Tc)))[0]
    a_star = np.max(np.abs(base_c[:1000].reshape(4, 250).mean(1)))          # largest calendar-year mean |d|
    b = base_c[sidx(rng, R, Tj, Tc, 63)]; b = b - b.mean(1, keepdims=True)
    t_st = tstat(A * (b + a_star * markov(rng, 1 / 250, R, Tj)) + noise(R))
    out = []
    for al in (0.01, 0.001):
        c_nom = stats.t.ppf(1 - al, nb - 1); c_st = max(c_nom, np.quantile(t_st, 1 - al))
        out.append("al %g: true rej@nominal %.4f true rej@stress %.4f (a*=%.3f)" % (al, np.mean(t_true > c_nom), np.mean(t_true > c_st), a_star))
    return " | ".join(out)
for seed in (71, 72, 73, 74):
    print("review case ", seed, case(seed, 0.03, 1 / 120, 1 / 60))
for seed in (81, 82, 83, 84):
    print("slower stress", seed, case(seed, 0.03, 1 / 250, 1 / 120))

# Printed (run 2026-11-16):
# review case  71 al 0.01: true rej@nominal 0.0149 true rej@stress 0.0112 (a*=0.014) | al 0.001: true rej@nominal 0.0016 true rej@stress 0.0011 (a*=0.014)
# review case  72 al 0.01: true rej@nominal 0.0140 true rej@stress 0.0046 (a*=0.060) | al 0.001: true rej@nominal 0.0025 true rej@stress 0.0003 (a*=0.060)
# review case  73 al 0.01: true rej@nominal 0.0154 true rej@stress 0.0028 (a*=0.056) | al 0.001: true rej@nominal 0.0019 true rej@stress 0.0001 (a*=0.056)
# review case  74 al 0.01: true rej@nominal 0.0183 true rej@stress 0.0036 (a*=0.039) | al 0.001: true rej@nominal 0.0024 true rej@stress 0.0002 (a*=0.039)
# slower stress 81 al 0.01: true rej@nominal 0.0575 true rej@stress 0.0008 (a*=0.058) | al 0.001: true rej@nominal 0.0145 true rej@stress 0.0000 (a*=0.058)
# slower stress 82 al 0.01: true rej@nominal 0.0221 true rej@stress 0.0024 (a*=0.057) | al 0.001: true rej@nominal 0.0026 true rej@stress 0.0003 (a*=0.057)
# slower stress 83 al 0.01: true rej@nominal 0.0124 true rej@stress 0.0041 (a*=0.051) | al 0.001: true rej@nominal 0.0009 true rej@stress 0.0001 (a*=0.051)
# slower stress 84 al 0.01: true rej@nominal 0.0109 true rej@stress 0.0063 (a*=0.057) | al 0.001: true rej@nominal 0.0012 true rej@stress 0.0010 (a*=0.057)
