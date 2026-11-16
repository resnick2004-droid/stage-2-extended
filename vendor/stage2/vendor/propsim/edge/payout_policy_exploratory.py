"""EXPLORATORY (post hoc, D-44): does taking only part of each allowed payout raise the funded account's value when the
trader has a genuine edge? Assumption A5 (take the full allowed amount at once) is optimal-neutral at e = 0 but may drain
the buffer that lets an edge compound. Horizon 504 trading days (two years) so deferred cash is not cut off early;
reported per year. Standard path, net-positive rule on, fee-free method. N = 40,000."""
import sys, os, itertools, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from propsim import Rules, Policy, simulate_xfa
PROFILES = [(2.0, 150.0), (2.0, 300.0), (1.5, 500.0), (2.0, 750.0), (1.5, 1000.0)]
EDGES = [0.0, 0.05, 0.10, 0.20]; FRACS = [1.0, 0.5, 0.25]; N, H = 40_000, 504
if __name__ == "__main__":
    rows = []; rules = Rules(payout_fee=0.0, require_profit_since_payout=True)
    for i, ((R, r), e, f) in enumerate(itertools.product(PROFILES, EDGES, FRACS)):
        x = simulate_xfa(rules, Policy(rr=R, risk=r, payout_frac=f), e, N, np.random.default_rng(15000 + i), horizon_days=H)
        rows.append(dict(R=R, risk=r, edge=e, payout_frac=f, cash_per_year=x["cash"].mean() / 2, cash_se=x["cash"].std() / np.sqrt(N) / 2,
                         p_alive_2y=1 - x["closed"].mean(), unrealised_2y=np.where(x["closed"], 0.0, x["B"]).mean(),
                         days_alive=x["days"].mean(), payouts=x["n_payouts"].mean()))
    D = pd.DataFrame(rows); D.to_csv(os.path.join(HERE, "results_payout_policy_exploratory.csv"), index=False)
    D["prof"] = D.R.map("{:g}".format) + ":1 $" + D.risk.map("{:.0f}".format)
    pd.set_option("display.width", 220)
    print(D.pivot_table(index=["prof", "payout_frac"], columns="edge", values="cash_per_year").round(0).to_string())
    print(D.pivot_table(index=["prof", "payout_frac"], columns="edge", values="p_alive_2y").round(3).to_string())
