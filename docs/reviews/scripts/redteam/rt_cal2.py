"""Red team: why the rule over-rejects -- the bootstrap sd against the true sd of the mean, the centring offset, and
how far below the mean the coded limit sits, in true standard errors; plus the degenerate short-sample case."""
import sys
import numpy as np
sys.argv = ["x", "path", "1", "1", "no", "6"]
import rt_cal as C

rng = np.random.default_rng(777)
W = C.weight_matrix(20261700)
for null in ("iid", "ar", "path"):
    xs, bsd, cen, gap = [], [], [], []
    for _ in range(10):
        d = C.gen(null, rng, 1000)
        xbar = d.mean(0)
        boot = W @ d
        xs.append(xbar)
        bsd.append(boot.std(0, ddof=1))
        cen.append(boot.mean(0) - xbar)
        gap.append(xbar - np.percentile(boot, 100 * 0.05 / 110, axis=0))
    xs, bsd, cen, gap = (np.concatenate(v) for v in (xs, bsd, cen, gap))
    sd = xs.std()
    print(f"{null}: true sd of mean {sd:.4f}; bootstrap sd median {np.median(bsd):.4f} (ratio {np.median(bsd) / sd:.2f}, "
          f"10-90% {np.percentile(bsd, 10) / sd:.2f}-{np.percentile(bsd, 90) / sd:.2f}); centring offset sd "
          f"{cen.std() / sd:.2f} true se; limit sits median {np.median(gap) / sd:.2f} true se below the mean "
          f"(10-90% {np.percentile(gap, 10) / sd:.2f}-{np.percentile(gap, 90) / sd:.2f}); needed 3.32")

# the degenerate case: a short block of starts (e.g. a six-month confirmation: about 63 starts with 63 sessions left)
for n in (63, 70, 90, 126):
    idx = C.boot_idx(n, 63)
    x = np.random.default_rng(1).standard_normal(n) * 0.44 + 0.0
    bt = x[idx].mean(1)
    print(f"n={n}: distinct block starts {n - 63 + 1}; boot sd {bt.std():.4f} vs iid se {x.std(ddof=1) / np.sqrt(n):.4f}; "
          f"limit at 0.05/110 {np.percentile(bt, 100 * 0.05 / 110):+.4f} vs mean {x.mean():+.4f}")
