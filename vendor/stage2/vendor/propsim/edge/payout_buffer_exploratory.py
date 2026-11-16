"""EXPLORATORY (post hoc, D-45): keep-a-buffer payout rule. Request only what leaves at least `keep_balance` in the account
(so the first payout waits until the balance clears the buffer). Horizon 504 trading days; realised cash reported per year
(conservative: balance still in the account at the horizon is shown separately, not counted). Standard path, net-positive
rule on, fee-free method. N = 40,000."""
import sys, os, itertools, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from propsim import Rules, Policy, simulate_xfa
PROFILES = [(2.0, 150.0), (2.0, 300.0), (1.5, 500.0), (2.0, 750.0), (1.5, 1000.0)]
EDGES = [0.0, 0.05, 0.10, 0.20]; KEEP = [0.0, 1000.0, 2000.0, 3000.0, 5000.0]; N, H = 40_000, 504
if __name__ == "__main__":
    rows = []; rules = Rules(payout_fee=0.0, require_profit_since_payout=True)
    for i, ((R, r), e, k) in enumerate(itertools.product(PROFILES, EDGES, KEEP)):
        x = simulate_xfa(rules, Policy(rr=R, risk=r, keep_balance=k), e, N, np.random.default_rng(18000 + i), horizon_days=H)
        unreal = np.where(x["closed"], 0.0, x["B"])
        rows.append(dict(R=R, risk=r, edge=e, keep_balance=k, cash_per_year=x["cash"].mean() / 2, cash_se=x["cash"].std() / np.sqrt(N) / 2,
                         p_alive_2y=1 - x["closed"].mean(), unrealised_2y=unreal.mean(), gross=x["gross_paid"].mean(),
                         T=(x["B"] + x["gross_paid"]).mean(), T_se=(x["B"] + x["gross_paid"]).std() / np.sqrt(N),
                         first_payout_day_median=np.median(x["first_payout_day"][x["first_payout_day"] >= 0]) + 1 if (x["first_payout_day"] >= 0).any() else np.nan))
    D = pd.DataFrame(rows); D.to_csv(os.path.join(HERE, "results_payout_buffer_exploratory.csv"), index=False)
    z0 = D[D.edge == 0]
    print("e=0 checks: gross <= 2000:", bool((z0.gross <= 2000 + 3 * 40).all()), " E[B+Q] <= 0:", bool((z0["T"] <= 3 * z0.T_se).all()))
    D["prof"] = D.R.map("{:g}".format) + ":1 $" + D.risk.map("{:.0f}".format)
    pd.set_option("display.width", 220)
    print("realised cash per year:"); print(D.pivot_table(index=["prof", "keep_balance"], columns="edge", values="cash_per_year").round(0).to_string())
    print("P(alive at 2 years):"); print(D.pivot_table(index=["prof", "keep_balance"], columns="edge", values="p_alive_2y").round(2).to_string())
