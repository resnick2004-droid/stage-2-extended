"""Red team: the realised level of D-621 (3)(i) as coded, with the rule's OWN fixed resample matrix (seed 20261700,
n = 595, block 63, 2,000 draws -- the matrix every judged comparison at n = 595 actually uses), on three nulls:
  iid   -- iid Gaussian start differences;
  ar    -- AR(1) 0.5 Gaussian;
  path  -- a structural null: two exchangeable designs' daily P&L (common + own shocks, common volatility
           clustering), each start 'ahead' at month m when cumulative P&L over 21m sessions beats a fee offset,
           A = mean over m = 1..3, d = A_x - A_y. Mean zero by exchangeability; the dependence comes from the
           overlapping 21/42/63-session windows, as in the real series.
Also: a fresh matrix per batch (seed varied) to see whether the fixed matrix matters.
Usage: python rt_cal.py <null> <batches> <batch_size> [fresh]"""
import sys
import numpy as np
from scipy import stats

N, B, DRAWS = 595, 63, 2000
TAU = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
LEVELS = (0.05 / 110, 0.05 / 132, 0.05 / 420, 0.005, 0.025)


def boot_idx(n, b, draws=DRAWS, seed=20261700):
    rng = np.random.default_rng(seed)
    k = -(-n // b)
    first = rng.integers(0, n - b + 1, size=(draws, k))
    return (first[:, :, None] + np.arange(b)[None, None, :]).reshape(draws, k * b)[:, :n]


def weight_matrix(seed):
    idx = boot_idx(N, B, seed=seed)
    W = np.zeros((DRAWS, N))
    for j in range(DRAWS):
        np.add.at(W[j], idx[j], 1.0)
    return W / N


def gen(null, rng, m):
    if null == "iid":
        return rng.standard_normal((N, m))
    if null == "ar":
        e = rng.standard_normal((N + 200, m))
        x = np.empty_like(e)
        x[0] = e[0]
        for t in range(1, len(e)):
            x[t] = 0.5 * x[t - 1] + e[t]
        return x[200:]
    if null == "path":
        T = N + 63
        h = np.empty((T + 100, m))
        h[0] = 0
        eta = rng.standard_normal((T + 100, m))
        for t in range(1, T + 100):
            h[t] = 0.97 * h[t - 1] + 0.25 * eta[t]
        vol = np.exp(h[100:] / 2)
        com = rng.standard_normal((T, m))
        own = rng.standard_normal((2, T, m))
        mu, F = 0.21, 4.98
        out = []
        for i in range(2):
            pnl = mu + vol * (np.sqrt(0.3) * com + np.sqrt(0.7) * own[i])
            c = np.vstack([np.zeros((1, m)), np.cumsum(pnl, axis=0)])
            s = np.arange(N)
            a = sum(((c[s + 21 * k] - c[s]) - F + TAU * rng.standard_normal((N, m)) > 0).astype(float)
                    for k in (1, 2, 3)) / 3.0
            out.append(a)
        return out[0] - out[1]
    raise ValueError(null)


def main():
    null, batches, m = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    fresh = len(sys.argv) > 4 and sys.argv[4] == "fresh"
    rng = np.random.default_rng(424242)
    W = weight_matrix(20261700)
    rej = {a: 0 for a in LEVELS}
    rej_min = 0
    rej_t = {a: 0 for a in LEVELS}
    rej_z = 0
    tot = 0
    acf1 = []
    nb = N // B
    for bi in range(batches):
        if fresh:
            W = weight_matrix(1000 + bi)
        d = gen(null, rng, m)
        xbar = d.mean(0)
        boot = W @ d
        bs = np.sort(boot, axis=0)
        for a in LEVELS:
            q = np.percentile(boot, 100 * a, axis=0)
            rej[a] += int(((xbar > 0) & (q > 0)).sum())
        rej_min += int(((xbar > 0) & (bs[0] > 0)).sum())
        bm = d[: nb * B].reshape(nb, B, m).mean(1)
        t = bm.mean(0) / (bm.std(0, ddof=1) / np.sqrt(nb))
        for a in LEVELS:
            rej_t[a] += int((t > stats.t.ppf(1 - a, nb - 1)).sum())
        z = xbar / boot.std(0, ddof=1)
        rej_z += int((z > stats.norm.ppf(1 - LEVELS[0])).sum())
        dc = d - xbar
        acf1.append([((dc[:-L] * dc[L:]).sum(0) / (dc * dc).sum(0)).mean() for L in (1, 5, 21, 42, 63)])
        tot += m
    print(f"null={null} reps={tot} fresh_matrix={fresh} mean acf lags 1,5,21,42,63={np.round(np.mean(acf1, 0), 3)}")
    for a in LEVELS:
        r = rej[a] / tot
        print(f"  level {a:.6f}: rule realised {r:.5f} (x{r / a:.1f}, se {np.sqrt(r * (1 - r) / tot):.5f});"
              f"  t on {nb} batch means {rej_t[a] / tot:.5f}")
    print(f"  limit at the minimum draw (k -> infinity floor): {rej_min / tot:.5f}")
    print(f"  normal z with the bootstrap's sd at 0.05/110: {rej_z / tot:.5f}")


if __name__ == "__main__":
    main()
