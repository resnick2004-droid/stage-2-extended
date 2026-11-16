"""Edge ladder under both edge conventions ("drift" exact vs "linear" first-order), truncate mode.
Regenerates results_edge_convention.csv with standard errors.  Usage: python run_edge_convention.py [--n 10000]"""
import argparse
import numpy as np, pandas as pd
from propsim import Rules, Policy, simulate_lifecycle

CELLS = [(1.0, 1500, 1, False), (0.5, 1000, 3, False), (2.0, 750, 1, False), (3.0, 500, 1, False), (1.0, 300, 6, False)]
EDGES = [-0.10, -0.05, -0.02, 0.0, 0.02, 0.05]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--days", type=int, default=504)
    ap.add_argument("--seed", type=int, default=500)
    a = ap.parse_args()
    rows = []
    for i, (rr, risk, tpd, sw) in enumerate(CELLS):
        for j, e in enumerate(EDGES):
            for mode in ["drift", "linear"]:
                best = None
                for path in ["standard", "consistency"]:
                    pol = Policy(rr=rr, risk=risk, trades_per_day=tpd, stop_day_on_win=sw, payout_path=path)
                    L = simulate_lifecycle(Rules(floor_mode="truncate", edge_mode=mode), pol, e, a.n,
                                           np.random.default_rng(a.seed + 10 * i + j), total_days=a.days)
                    if best is None or L["mean_net"] > best["mean_net"]:
                        best = L
                rows.append(dict(rr=rr, risk=risk, day_rule=f"{tpd}/day", edge=e, edge_mode=mode,
                                 net_per_attempt=best["mean_net"], net_se=best["net"].std(ddof=1) / np.sqrt(a.n),
                                 p_pass=best["p_pass"], n=a.n, seed=a.seed + 10 * i + j))
    df = pd.DataFrame(rows)
    df.to_csv("results_edge_convention.csv", index=False)
    piv = df.pivot_table(index=["rr", "risk", "day_rule", "edge"], columns="edge_mode", values="net_per_attempt")
    piv["diff"] = piv["drift"] - piv["linear"]
    se = df.pivot_table(index=["rr", "risk", "day_rule", "edge"], columns="edge_mode", values="net_se")
    piv["diff_in_SE"] = piv["diff"] / np.sqrt(se["drift"] ** 2 + se["linear"] ** 2)
    pd.set_option("display.width", 200)
    print(piv.to_string(float_format=lambda v: f"{v:.1f}"))


if __name__ == "__main__":
    main()
