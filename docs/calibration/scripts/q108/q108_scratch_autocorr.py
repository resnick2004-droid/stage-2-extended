"""Q-108 plan (m8). Scratch, synthetic (seed 10810801, outside the program's 2026 space): the admission statistic rho-bar's spread for
block-constant +-1 sides of persistence L at random phase, every session traded, plus a share p of sessions with no
trade; on 657 sessions (the judged block) and 1006 (the choice block)."""
import numpy as np
rng = np.random.default_rng(10810801)
def rhobar(d, traded):
    x = np.where(traded, d, np.nan)
    m = np.nanmean(x); v = np.nanmean((x - m) ** 2)
    if not v > 0: return np.nan
    out = []
    for k in range(22, 64):
        a, b = x[:-k] - m, x[k:] - m
        ok = ~np.isnan(a) & ~np.isnan(b)
        out.append(np.mean(a[ok] * b[ok]) / v)
    return float(np.mean(out))
for n in (657, 1006):
    for L in (1, 21, 42, 63):
        vals = []
        for r in range(2000):
            ph = rng.integers(0, L)
            nb = (n + L) // L + 1
            s = rng.choice([-1.0, 1.0], size=nb)[(np.arange(n) + ph) // L]
            traded = rng.random(n) < 0.8
            vals.append(rhobar(s, traded))
        v = np.array(vals)
        print(f"n={n} L={L}: P(rho-bar <= 0.10) = {np.mean(v <= 0.10):.3f}; median {np.median(v):.3f}; p10 {np.quantile(v,0.1):.3f} p90 {np.quantile(v,0.9):.3f}", flush=True)
