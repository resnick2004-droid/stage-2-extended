"""Q-108 plan (m8). Scratch, synthetic (seed 10810802, outside the program's 2026 space): runs R of the daily majority
side, and the effective count E = (sum of run lengths)^2 / (sum of squared run lengths), for block-constant fair-coin
sides at persistence L (Q-16's flip model, random phase, 80 % of sessions traded), on the judged block's 657 sessions
(threshold 13) and a choice block of 1,006 (threshold 18). Prints how often each passes, how often R passes together
with the floor E >= 4 (the third text's admission), and E / R. Sessions with no trade are dropped; this model has no
tied sessions."""
import numpy as np

rng = np.random.default_rng(10810802)


def runs(m):
    m = m[m != 0]
    if len(m) == 0:
        return 0, 0.0
    cut = np.flatnonzero(np.r_[True, m[1:] != m[:-1], True])
    lens = np.diff(cut)
    return len(lens), float(lens.sum() ** 2 / (lens ** 2).sum())


for n, thr in ((657, 13), (1006, 18)):
    for L in (1, 5, 21, 30, 42, 63):
        R, E = [], []
        for r in range(4000):
            ph = rng.integers(0, L)
            nb = (n + L) // L + 1
            s = rng.choice([-1, 1], size=nb)[(np.arange(n) + ph) // L]
            s = np.where(rng.random(n) < 0.8, s, 0)
            a, b = runs(s)
            R.append(a)
            E.append(b)
        R, E = np.array(R), np.array(E)
        print(f"n={n} L={L}: runs median {np.median(R):.0f}, max {R.max()}, P(R >= {thr}) = {np.mean(R >= thr):.3f}; "
              f"E median {np.median(E):.1f}, P(E >= {thr - 0.5}) = {np.mean(E >= thr - 0.5):.3f}, "
              f"P(R >= {thr} and E >= 4) = {np.mean((R >= thr) & (E >= 4)):.3f}, "
              f"median E/R {np.median(E / np.maximum(R, 1)):.2f}")
