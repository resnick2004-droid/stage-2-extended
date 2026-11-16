"""Monte-Carlo check of the exact 16/49 result for the recommended zero-edge Combine profile (1:1, $1,500, one trade/day).
Writes results_exact_chain_check.csv. Seeded."""
import numpy as np, pandas as pd
from propsim import Rules, Policy, simulate_combine
if __name__ == "__main__":
    N, seed = 2_000_000, 20260921
    c = simulate_combine(Rules(), Policy(rr=1, risk=1500, trades_per_day=1), 0.0, N, np.random.default_rng(seed), max_days=2000)
    p = c["passed"].mean(); se = np.sqrt(p * (1 - p) / N)
    pd.DataFrame([dict(N=N, seed=seed, exact=16/49, mc_p_pass=p, se=se, z=(p - 16/49) / se, mean_days=c["days"].mean())]).to_csv("results_exact_chain_check.csv", index=False)
    print(f"exact {16/49:.6f}  MC {p:.6f} +/- {se:.6f}  z {(p-16/49)/se:+.2f}  mean days {c['days'].mean():.3f}")
