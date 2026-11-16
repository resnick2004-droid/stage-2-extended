"""Q-108 plan (m8). Scratch timing (synthetic, seed 10810803): exact enumeration of Q-16's flip null at L = 42 for one subset of 5,000
synthetic trades -- the three CR1 members, their margins, the CR2/BM members (fixed df), t63e and the SN statistic --
to size the plan's exact part. Prints seconds only."""
import time
import numpy as np
from scipy import stats
n = 657
rng = np.random.default_rng(10810803)
N = np.bincount(rng.integers(0, n, 5000), minlength=n).astype(float)
V = 0.5 * (rng.binomial(N.astype(int), 0.52) * 2 - N)
def bidx(b):
    G = n // b
    return (np.arange(n) * G) // n, G
TB = {b: bidx(b) for b in (21, 42, 63)}
lev = [0.05 / (k * (k + 1)) for k in range(13, 21)]
def run(L):
    t0 = time.time()
    Nt = N.sum()
    BNs = {b: np.bincount(bid, weights=N, minlength=G) for b, (bid, G) in TB.items()}
    cnt = 0
    for p in range(L):
        fid = (np.arange(n) + p) // L
        B = int(fid[-1]) + 1
        P = (((np.arange(2 ** B)[:, None] >> np.arange(B)[None, :]) & 1) * 2.0 - 1.0)
        est = P @ np.bincount(fid, weights=V, minlength=B) / Nt
        keep = est > 0                       # only a positive estimate can reject (one-sided)
        Pk = P[keep]
        ok = np.ones(Pk.shape[0], bool)
        for b, (bid, G) in TB.items():
            M = np.zeros((B, G)); np.add.at(M, (fid, bid), V)
            BS = Pk @ M
            e = BS.sum(1) / Nt
            u = BS - e[:, None] * BNs[b][None, :]
            g = int((BNs[b] > 0).sum())
            se1 = np.sqrt(g / (g - 1) * (u * u).sum(1)) / Nt
            pg = BNs[b] / Nt; w = 1 / (1 - pg)
            se2 = np.sqrt((w * u * u).sum(1)) / Nt
            t1 = e / se1; t2 = e / se2
            for a in lev:
                c = stats.t.isf(a, g - 1)
                ok &= t1 > 1.25 * c        # stand-in for the candidates' comparisons
            bm = (BS / np.where(BNs[b] > 0, BNs[b], 1)).mean(1)
        # SN: U_t linear in the pattern: D (B x n), quadratic form
        C = np.cumsum(N); D = np.zeros((B, n))
        for f in range(B):
            vf = np.where(fid == f, V, 0.0)
            D[f] = np.cumsum(vf) - (vf.sum() / Nt) * C
        Q = D @ D.T
        q = np.einsum("ij,jk,ik->i", Pk, Q, Pk)
        T = (Pk @ np.bincount(fid, weights=V, minlength=B)) / np.sqrt(q / n)
        cnt += Pk.shape[0]
    return time.time() - t0, cnt
for L in (63, 55, 42):
    s, c = run(L)
    print(f"L={L}: {s:.1f} s for {c} positive-estimate patterns", flush=True)
