"""Null rejection rate of D-621 (3)(i)'s one-sided moving-block percentile bound (re-implemented from
vendor/stage2/propedge/research/user_journey.py block_indices / paired_interval: non-circular moving blocks,
ceil(n/b) blocks cut to n, np.percentile at 100*level, 2,000 draws) on synthetic autocorrelated null series.
Synthetic data only; no repository data read."""
import sys
import numpy as np

def block_indices(n, b, draws, rng):
    k = -(-n // b)
    first = rng.integers(0, n - b + 1, size=(draws, k))
    return (first[:, :, None] + np.arange(b)[None, None, :]).reshape(draws, k * b)[:, :n]

def series(n, rng, ma=63, noise=0.3):
    e = rng.standard_normal(n + ma - 1)
    x = np.convolve(e, np.ones(ma) / ma, mode="valid")[:n]
    return x / x.std() + noise * rng.standard_normal(n)

def run(n=578, b=63, draws=2000, reps=3000, levels=(0.05/110, 0.05/132, 0.05/90, 0.005, 0.025), seed=1, ma=63):
    rng = np.random.default_rng(seed)
    rej = {a: 0 for a in levels}
    for _ in range(reps):
        x = series(n, rng, ma=ma)
        m = x.mean()
        idx = block_indices(n, b, draws, rng)
        boot = x[idx].mean(axis=1)
        for a in levels:
            lo = np.percentile(boot, 100.0 * a)
            if m > 0 and lo > 0:
                rej[a] += 1
    return {a: rej[a] / reps for a in levels}

if __name__ == "__main__":
    ma = int(sys.argv[1]) if len(sys.argv) > 1 else 63
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    out = run(reps=reps, ma=ma)
    for a, r in out.items():
        print(f"ma={ma} nominal={a:.6f} realised={r:.5f} ratio={r / a:.1f}")
