"""RECORDED FINDING ONLY (D-24 retired, D-27): funded day-one all-in under a 75 % per-trade risk cap: risk at most $1,500 per trade toward target Y = 2000*R;
if the first bet loses (balance -1,500, floor unratcheted) the next bet risks the remaining $500 toward the same Y."""
import numpy as np, pandas as pd, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from propsim import Rules
from statepolicy import run_xfa, xfa_build_then_harvest
from dll_funded import dll_allin
if __name__ == "__main__":
    rows = []; N = 100_000
    for R in [2, 3, 5]:
        Y = 2000.0 * R
        for label, act in [("100 % all-in (single $2,000 bet)", xfa_build_then_harvest(R, 2000, 1, 150, 1)),
                           ("75 % cap: $1,500 bet, then $500 bet if it loses", dll_allin(Y, dll=1500.0))]:
            x = run_xfa(Rules(), act, N, np.random.default_rng(42), 500, "standard")
            rows.append(dict(R=R, policy=label, net=x["cash"].mean(), se=x["cash"].std()/np.sqrt(N), p_payout=(x["cash"] > 0).mean(),
                             analytic=0.9*2000*R/(1+R), R_first_bet=Y/1500, R_second_bet=(Y+1500)/500))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "results_75pct_cap_funded.csv"), index=False)
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
