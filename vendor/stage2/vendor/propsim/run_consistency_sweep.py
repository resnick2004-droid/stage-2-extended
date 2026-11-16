"""H3 mechanism test: does the interior maximum in r track the consistency rule?
Sweeps consistency_max_day_frac at 1/day; predicted peak r* = frac*3000/R if the ridge is the
largest bet whose single win does not inflate target_eff.  Regenerates results_consistency_sweep.csv."""
import argparse
import numpy as np, pandas as pd
from propsim import Rules, Policy, simulate_combine, simulate_xfa, summarize_combine, summarize_xfa

FRACS = [0.40, 0.55, 0.70, 1.00]           # 1.00 makes the rule inert (best_day <= balance always)
RRS = [1.0, 1.5, 2.0, 3.0]
RISKS = [300, 400, 500, 600, 750, 900, 1000, 1100, 1250, 1500, 1750, 2000]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=15000)
    ap.add_argument("--seed", type=int, default=900)
    a = ap.parse_args()
    base = Rules()
    rows = []
    for i, rr in enumerate(RRS):
        for j, risk in enumerate(RISKS):
            pol = Policy(rr=rr, risk=risk, trades_per_day=1)
            # XFA does not read the consistency fraction: simulate once per (R, r)
            xcash = {}
            for path in ["standard", "consistency"]:
                pol.payout_path = path
                xcash[path] = summarize_xfa(simulate_xfa(base, pol, 0.0, a.n,
                                            np.random.default_rng(a.seed + 100 * i + j), horizon_days=250))["mean_cash"]
            xbest = max(xcash.values())
            for k, frac in enumerate(FRACS):
                rules = Rules(consistency_max_day_frac=frac)
                c = summarize_combine(simulate_combine(rules, pol, 0.0, a.n,
                                      np.random.default_rng(a.seed + 100 * i + j + 5000 * k)))
                ev = c["p_pass"] * (xbest - base.activation) - c["mean_sub_fees"]
                rows.append(dict(frac=frac, rr=rr, risk=risk, p_pass=c["p_pass"], p_pass_se=c["p_pass_se"],
                                 mean_days=c["mean_days"], sub_fees=c["mean_sub_fees"], xfa_cash=xbest, ev=ev,
                                 ev_se=c["p_pass_se"] * abs(xbest - base.activation), predicted_peak=frac * 3000 / rr))
    df = pd.DataFrame(rows)
    df.to_csv("results_consistency_sweep.csv", index=False)
    pd.set_option("display.width", 220)
    for frac in FRACS:
        sub = df[df.frac == frac]
        print(f"\n=== consistency_max_day_frac = {frac} : EV per attempt (N={a.n}) ===")
        print(sub.pivot(index="rr", columns="risk", values="ev").to_string(float_format=lambda v: f"{v:6.0f}"))
        pk = sub.loc[sub.groupby("rr")["ev"].idxmax()][["rr", "risk", "ev", "ev_se", "predicted_peak"]]
        print(pk.rename(columns={"risk": "argmax_r"}).to_string(index=False, float_format=lambda v: f"{v:.0f}"))
    print("\n=== pass probability at frac=0.55 ===")
    print(df[df.frac == 0.55].pivot(index="rr", columns="risk", values="p_pass").to_string(float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
