"""Funded side under the $1,000 DLL (official, 50K): day-one all-in toward target Y = 2000*R, risking at most $1,000 per day
(a flattened day leaves B = -1,000 with the floor unratcheted; the next day races -2,000 vs Y). Harvest 1:1 $150, one trade/day.
Compared at Standard cap $2,000 (no DLL) and $4,000 (DLL elected at Combine checkout), with and without payout frictions."""
import numpy as np, pandas as pd, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from propsim import Rules
from statepolicy import run_xfa, xfa_build_then_harvest

def dll_allin(Y, dll=1000.0, r2=150.0):
    def act(s):
        n = len(s["B"]); F = s["B"] - s["room"]
        build = (s["B"] < Y - 1e-9) & (F < -1e-9)   # build only until the target has been reached once (floor then locks at 0)
        risk_b = np.minimum(s["room"], dll); rr_b = (Y - s["B"]) / np.maximum(risk_b, 1e-9)
        slot_ok_b = s["slot"] < 1
        rr = np.where(build, rr_b, 1.0)
        risk = np.where(build, np.where(slot_ok_b, risk_b, 0.0), np.where(s["slot"] < 1, r2, 0.0))
        return rr, risk
    return act

if __name__ == "__main__":
    rows = []; N = 100_000
    for R in [1, 2, 3, 5]:
        Y = 2000.0 * R
        for cap in [2000.0, 4000.0]:
            for fr in [False, True]:
                rules = Rules(std_cap=cap, payout_fee=30.0 if fr else 0.0, require_profit_since_payout=fr)
                for label, act in [("single bet, no DLL", xfa_build_then_harvest(R, 2000, 1, 150, 1)), ("DLL-capped all-in", dll_allin(Y))]:
                    if label == "single bet, no DLL" and cap == 4000.0: continue   # the higher cap requires the DLL
                    x = run_xfa(rules, act, N, np.random.default_rng(42), 500, "standard")
                    rows.append(dict(R=R, policy=label, cap=int(cap), frictions=fr, net=x["cash"].mean(), se=x["cash"].std() / np.sqrt(N),
                                     p_payout=(x["cash"] > 0).mean(), payouts=x["n_payouts"].mean(), analytic=0.9 * 2000 * R / (1 + R)))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_dll_funded.csv"), index=False)
    pd.set_option("display.width", 200); print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
