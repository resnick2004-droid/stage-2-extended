"""T4 check 2 on propsim: simulate the supremum policy and compare with the pre-registered prediction (PREREG_T4_propsim.md)."""
import numpy as np, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from propsim import Rules
from statepolicy import run_combine
def supremum_policy(s):
    d0 = (s["day"] == 0) & (s["slot"] < 1); d1 = (s["day"] == 1) & (s["slot"] < 1)
    return np.where(d0, 0.825, 0.675), np.where(d0 | d1, 2000.0, 0.0)
if __name__ == "__main__":
    N = 1_000_000; pred = (2000 / 3650) * (2000 / 3350)
    r = run_combine(Rules(), supremum_policy, N, np.random.default_rng(20260921), max_days=5)
    p = r["passed"].mean(); se = np.sqrt(p * (1 - p) / N); z = (p - pred) / se
    print(f"predicted {pred:.6f}  measured {p:.6f} +/- {se:.6f}  z = {z:+.2f}  -> {'PASS' if abs(z) <= 3 else 'FAIL'}")
    print(f"mean days {r['days'].mean():.3f}   passes on day 2 only: {bool(np.all(r['days'][r['passed']] == 2))}")
    with open(os.path.join(HERE, "results_t4_check2_propsim.txt"), "w") as f:
        f.write(f"predicted={pred:.6f} measured={p:.6f} se={se:.6f} z={z:+.2f} N={N} seed=20260921\n")
