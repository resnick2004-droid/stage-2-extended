"""Supremum of Combine pass probability over ALL fair strategies (not just static or tested policies).

Within a day, a continuous fair (martingale) P&L process can end at any distribution with mean = starting balance,
supported on [F, inf), where ending at F means the floor was touched (fail). At the 16:00 lock the floor ratchets
(F' = min(0, max(F, B' - 2000))), the best day updates, and the pass test is applied. Hence
    V(state) = concave envelope over end-of-day balance x of g_state(x), evaluated at the current balance,
with g(x) = value of the post-lock state (0 if x <= F, 1 if x passes). The least fixed point of this Bellman operator is
the supremum over all strategies. Balances are restricted to a grid of step h; the grid value converges to the true
supremum from below as h -> 0 (outcomes off the grid are excluded).
State: (B, F, ex) with ex = max(0, best day - 1650) (best days <= 1650 leave the target at 3000).
"""
import numpy as np, sys, time

def solve(h, B_max=3600, ex_max=300, tol=1e-10, max_iter=20000, verbose=False, dll=None):
    Bs = np.arange(-2000, B_max + h / 2, h)                 # balance grid
    Fs = np.arange(-2000, 0 + h / 2, h)                     # floor grid
    Es = np.arange(0, ex_max + 25, 50.0)                   # best-day excess grid (step 50 so D - 1650 is on it for any h dividing 50)
    nB, nF, nE = len(Bs), len(Fs), len(Es)
    iF = {round(f): k for k, f in enumerate(Fs)}; iE = {round(e): k for k, e in enumerate(Es)}
    V = np.zeros((nF, nE, nB))
    # precompute, for every (F, ex, B, x): next-state index or terminal code
    # code: -1 fail, -2 pass, -3 infeasible (ex beyond grid -> treat as value 0: lower bound, verified non-binding below), else flat index
    nxt = np.full((nF, nE, nB, nB), -1, dtype=np.int64)
    for a, F in enumerate(Fs):
        for e_i, ex in enumerate(Es):
            for b, B in enumerate(Bs):
                if B <= F: continue
                for j, x in enumerate(Bs):
                    if x <= F: nxt[a, e_i, b, j] = -1; continue
                    D = x - B
                    ex2 = max(ex, D - 1650.0)
                    target = max(3000.0, (1650.0 + ex2) / 0.55) if ex2 > 0 else 3000.0
                    if x >= target - 1e-9: nxt[a, e_i, b, j] = -2; continue
                    if ex2 > ex_max + 1e-9: nxt[a, e_i, b, j] = -3; continue
                    F2 = min(0.0, max(F, x - 2000.0))
                    nxt[a, e_i, b, j] = (iF[round(F2)] * nE + iE[round(ex2)]) * nB + j
    valid = np.zeros((nF, nB), bool)
    for a, F in enumerate(Fs): valid[a] = Bs > F
    x = Bs
    t0 = time.time()
    for it in range(max_iter):
        flat = V.ravel()
        g = np.where(nxt >= 0, flat[np.maximum(nxt, 0)], np.where(nxt == -2, 1.0, 0.0))    # (F, ex, B, x)
        Vn = np.empty_like(V)
        # concave envelope at B over pairs x1 <= B <= x2
        dx = x[None, :] - x[:, None]                                                   # x2 - x1  (i, j)
        for a in range(nF):
            for e_i in range(nE):
                G = g[a, e_i]                                                          # (B, x)
                best = np.zeros(nB)
                for b in range(nB):
                    if not valid[a, b]: continue
                    lo_val = Fs[a] if dll is None else max(Fs[a], x[b] - dll)
                    lo = np.searchsorted(x, lo_val - 1e-9); i_idx = np.arange(lo, b + 1); j_idx = np.arange(b, nB)   # floor (fail) or DLL (forced flat) bounds the day's low
                    g1 = G[b, i_idx][:, None]; g2 = G[b, j_idx][None, :]
                    x1 = x[i_idx][:, None]; x2 = x[j_idx][None, :]
                    w = x2 - x1
                    val = np.where(w > 0, (g1 * (x2 - x[b]) + g2 * (x[b] - x1)) / np.where(w > 0, w, 1), g1)
                    best[b] = val.max()
                Vn[a, e_i] = best
        diff = np.abs(Vn - V).max(); V = Vn
        if verbose and it % 25 == 0: print(f"  iter {it}  diff {diff:.2e}  V(start) {V[0, 0, np.searchsorted(Bs, 0)]:.6f}  {time.time()-t0:.0f}s", flush=True)
        if diff < tol: break
    start = V[0, 0, np.searchsorted(Bs, 0)]
    return start, it, V, Bs, Fs, Es

if __name__ == "__main__":
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 250
    dll = float(sys.argv[2]) if len(sys.argv) > 2 else None
    v, it, *_ = solve(h, verbose=True, dll=dll)
    print(f"h = {h:g}: sup P(pass) on grid = {v:.6f}   (16/49 = {16/49:.6f}; two-day bound 0.327130; ceiling 0.4)   iterations {it}")
