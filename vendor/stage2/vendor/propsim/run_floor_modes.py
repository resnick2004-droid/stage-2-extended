"""Regenerates results_floor_mode_504.csv: none / truncate / resize on a 504-day
continuous lifecycle, with standard errors.  Usage: python run_floor_modes.py [--n 20000]"""
import argparse
import numpy as np, pandas as pd
from propsim import Rules, Policy, simulate_lifecycle

CELLS = [(1.0, 1500, 1, False), (0.5, 1000, 3, False), (1.0, 1500, 3, True), (2.0, 750, 1, False),
         (1.5, 1000, 1, False), (1.0, 500, 1, False), (2.0, 300, 1, False), (1.0, 300, 6, False),
         (0.5, 500, 6, False)]
MODES = ["none", "truncate", "resize"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--days", type=int, default=504)
    ap.add_argument("--seed", type=int, default=100)
    a = ap.parse_args()
    rows = []
    for i, (rr, risk, tpd, sw) in enumerate(CELLS):
        for mode in MODES:
            best = None
            for path in ["standard", "consistency"]:
                pol = Policy(rr=rr, risk=risk, trades_per_day=tpd, stop_day_on_win=sw, payout_path=path)
                L = simulate_lifecycle(Rules(floor_mode=mode), pol, 0.0, a.n,
                                       np.random.default_rng(a.seed + i), total_days=a.days)
                if best is None or L["mean_net"] > best["mean_net"]:
                    best = dict(L, path=path)
            net = best["net"]
            rows.append(dict(rr=rr, risk=risk, day_rule=f"{tpd}/day" + (" stopW" if sw else ""), mode=mode,
                             path=best["path"], p_pass=best["p_pass"],
                             p_pass_se=np.sqrt(best["p_pass"] * (1 - best["p_pass"]) / a.n),
                             p_payout=best["p_payout"], cash_per_attempt=best["mean_cash"],
                             net_per_attempt=best["mean_net"], net_se=net.std(ddof=1) / np.sqrt(a.n),
                             p_net_pos=best["p_net_pos"],
                             p_net_pos_se=np.sqrt(best["p_net_pos"] * (1 - best["p_net_pos"]) / a.n),
                             n=a.n, total_days=a.days, seed=a.seed + i))
    df = pd.DataFrame(rows)
    df.to_csv("results_floor_mode_504.csv", index=False)
    pd.set_option("display.width", 220)
    print(df.drop(columns=["n", "total_days", "seed"]).to_string(index=False, float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
