"""Ruin at large bankrolls, and ruin split into 'never saw a payout' vs 'paid, then went broke', by attempt count.
Uses the per-attempt distribution from bankroll.py (Combine 1:1 $1,500; payout frictions on)."""
import numpy as np, pandas as pd
from bankroll import attempts, ruin

rows, split = [], []
for profile in ["static", "allin3"]:
    df = attempts(profile, True, 400_000, 11)
    for B in [4000, 5000, 6000, 8000, 10000]:
        rows.append(dict(policy=profile + "+fr", bankroll=B, ruin_200=ruin(df, B, 200, 20_000, 5), ruin_500=ruin(df, B, 500, 20_000, 9)))
    for B in [1000, 2000, 3000, 5000]:
        rng = np.random.default_rng(5); P, H = 20000, 300
        idx = rng.integers(0, len(df), size=(P, H))
        sub, act, cash = df["sub"].values[idx], df["act"].values[idx], df["cash"].values[idx]
        bal = np.full(P, float(B)); dead_at = np.full(P, -1); paid = np.zeros(P, bool); paid_first = np.zeros(P, bool)
        for t in range(H):
            for cost in (sub[:, t], act[:, t]):
                alive = dead_at < 0; bal -= np.where(alive, cost, 0); newd = alive & (bal < 0); dead_at[newd] = t; paid_first[newd] = paid[newd]
            alive = dead_at < 0; bal[alive] += cash[alive, t]; paid |= alive & (cash[:, t] > 0)
        ruined = dead_at >= 0
        split.append(dict(policy=profile + "+fr", bankroll=B, ruin_ever=ruined.mean(), ruined_no_payout_first=(ruined & ~paid_first).mean(),
                          ruined_after_a_payout=(ruined & paid_first).mean(), median_attempts_to_ruin=np.median(dead_at[ruined]) + 1,
                          ruin_within_10=(ruined & (dead_at < 10)).mean(), ruin_within_25=(ruined & (dead_at < 25)).mean(), ruin_within_50=(ruined & (dead_at < 50)).mean()))
pd.DataFrame(rows).to_csv("results_ruin_large_bankroll.csv", index=False)
pd.DataFrame(split).to_csv("results_ruin_split.csv", index=False)
print(pd.DataFrame(rows).to_string(index=False)); print(pd.DataFrame(split).to_string(index=False, float_format=lambda v: f"{v:.3f}"))
