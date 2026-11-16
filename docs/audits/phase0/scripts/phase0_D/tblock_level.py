"""Comparison: (a) the moving-block percentile bound on iid data (ma=1); (b) a Student-t bound on non-overlapping
63-session block means (df = blocks - 1) on the MA(63) null series -- synthetic data only."""
import numpy as np
from scipy import stats
from mbb_level import run, series

print("iid:", {round(k, 6): v for k, v in run(reps=4000, ma=1).items()})
rng = np.random.default_rng(7)
levels = (0.05/110, 0.005, 0.025)
for ma in (21, 63):
    rej = {a: 0 for a in levels}
    reps = 20000
    for _ in range(reps):
        x = series(578, rng, ma=ma)
        nb = 578 // 63
        bm = x[: nb * 63].reshape(nb, 63).mean(axis=1)
        t = bm.mean() / (bm.std(ddof=1) / np.sqrt(nb))
        for a in levels:
            if t > stats.t.ppf(1 - a, nb - 1):
                rej[a] += 1
    print("t on block means, ma", ma, {round(a, 6): rej[a] / reps for a in levels})
