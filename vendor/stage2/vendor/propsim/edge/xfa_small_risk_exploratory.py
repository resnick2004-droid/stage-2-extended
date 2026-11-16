"""EXPLORATORY (post hoc, not pre-registered — see PREREG_T5.md and D-44): funded-side profiles with small risk per trade.
Motivation found in the pre-registered results: with $500-$1,000 funded risk the XFA dies within ~1-2 months even at a
20 % edge; a trader with a genuine edge wants the account to survive so the edge compounds. Same settings as the XFA stage:
N = 50,000, 252-day horizon, net-positive rule on, fee-free payout method, both paths."""
import sys, os, itertools, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from propsim import Rules, Policy, simulate_xfa
SMALL = [(R, r) for R in (1.5, 2.0, 3.0) for r in (100.0, 150.0, 200.0, 300.0)]
EDGES = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20]; N, H = 50_000, 252
if __name__ == "__main__":
    rows = []; rules = Rules(payout_fee=0.0, require_profit_since_payout=True)
    for i, ((R, r), path, e) in enumerate(itertools.product(SMALL, ["standard", "consistency"], EDGES)):
        x = simulate_xfa(rules, Policy(rr=R, risk=r, payout_path=path), e, N, np.random.default_rng(12000 + i), horizon_days=H)
        fp = x["first_payout_day"]; got = fp >= 0
        rows.append(dict(R=R, risk=r, path=path, edge=e, admissible=True, exploratory=True,
                         cash=x["cash"].mean(), cash_se=x["cash"].std() / np.sqrt(N), gross=x["gross_paid"].mean(),
                         gross_se=x["gross_paid"].std() / np.sqrt(N), T=(x["B"] + x["gross_paid"]).mean(),
                         T_se=(x["B"] + x["gross_paid"]).std() / np.sqrt(N), p_payout=got.mean(),
                         days_to_first_payout=(np.median(fp[got]) + 1) if got.any() else np.nan, payouts=x["n_payouts"].mean(),
                         p_closed=x["closed"].mean(), days_alive=x["days"].mean(), unrealised=np.where(x["closed"], 0.0, x["B"]).mean()))
    X = pd.DataFrame(rows); X.to_csv(os.path.join(HERE, "results_xfa_edge_exploratory.csv"), index=False)
    x0 = X[X.edge == 0]
    print("bounds at e=0 (same V3 criteria):", bool((x0.gross <= 2000 + 3 * x0.gross_se).all()), bool((x0["T"] <= 3 * x0.T_se).all()))
