"""Final profiles at high N with standard errors, edge ladder, and payout frictions.
Regenerates results_final.csv.  Usage: python run_final.py [--n 100000]"""
import argparse
import numpy as np, pandas as pd
from propsim import Rules, Policy, simulate_combine, simulate_xfa, summarize_combine, summarize_xfa
from statepolicy import run_xfa, xfa_build_then_harvest, static, run_combine

EDGES = [-0.10, -0.05, -0.02, 0.0, 0.02, 0.05]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    rows = []
    for e in EDGES:
        rng = np.random.default_rng(a.seed + int(1000 * (e + 1)))
        # --- Combine profile: static 1:1 $1,500, 1/day (official floor lock on) ---
        c = summarize_combine(simulate_combine(Rules(), Policy(rr=1, risk=1500, trades_per_day=1), e, a.n, rng))
        # --- XFA option A: best static, 2:1 $750 1/day ---
        pA = Policy(rr=2, risk=750, trades_per_day=1, payout_path="standard")
        xA = summarize_xfa(simulate_xfa(Rules(), pA, e, a.n, rng, horizon_days=250))
        xA_fr = summarize_xfa(simulate_xfa(Rules(payout_fee=30, require_profit_since_payout=True), pA, e, a.n, rng, horizon_days=250))
        row = dict(edge=e, c_p_pass=c["p_pass"], c_p_pass_se=c["p_pass_se"], c_mean_days=c["mean_days"], c_sub=c["mean_sub_fees"],
                   xfa_static_net=xA["mean_cash"], xfa_static_net_frictions=xA_fr["mean_cash"])
        rows.append(row)
    df = pd.DataFrame(rows)

    # --- XFA option B: day-one all-in (binary limit, zero edge only: edge on a single trade is
    #     p = (1+e)/(1+R); reported analytically below) ---
    rng = np.random.default_rng(a.seed + 99)
    allin = {}
    for rr in [1, 2, 3, 5]:
        for label, rl in [("", Rules()), ("_frictions", Rules(payout_fee=30, require_profit_since_payout=True))]:
            r = run_xfa(rl, xfa_build_then_harvest(rr, 2000, 1, 150, 1), a.n, rng, 250, "standard")
            allin[f"allin_{rr}to1{label}"] = r["cash"].mean()
            allin[f"allin_{rr}to1{label}_se"] = r["cash"].std() / np.sqrt(a.n)
    for k, v in allin.items():
        df[k] = v if k.endswith("_se") else np.nan
    df.loc[df.edge == 0.0, [k for k in allin if not k.endswith("_se")]] = [allin[k] for k in allin if not k.endswith("_se")]
    act = Rules().activation
    df["ev_attempt_static"] = df.c_p_pass * (df.xfa_static_net - act) - df.c_sub
    df["ev_attempt_static_frictions"] = df.c_p_pass * (df.xfa_static_net_frictions - act) - df.c_sub
    z = df.edge == 0.0
    for rr in [1, 2, 3, 5]:
        df.loc[z, f"ev_attempt_allin_{rr}to1"] = df.c_p_pass * (df[f"allin_{rr}to1"] - act) - df.c_sub
        df.loc[z, f"ev_attempt_allin_{rr}to1_frictions"] = df.c_p_pass * (df[f"allin_{rr}to1_frictions"] - act) - df.c_sub
    df.to_csv("results_final.csv", index=False)
    pd.set_option("display.width", 250)
    print(df[["edge", "c_p_pass", "c_p_pass_se", "c_mean_days", "c_sub", "xfa_static_net", "xfa_static_net_frictions",
              "ev_attempt_static", "ev_attempt_static_frictions"]].to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("\nzero-edge day-one all-in (net per XFA, then per attempt):")
    for rr in [1, 2, 3, 5]:
        print(f"  {rr}:1  net {allin[f'allin_{rr}to1']:.0f} ± {allin[f'allin_{rr}to1_se']:.0f}  (frictions {allin[f'allin_{rr}to1_frictions']:.0f})"
              f"   analytic 0.9*2000*R/(1+R) = {0.9*2000*rr/(1+rr):.0f}"
              f"   per attempt {float(df.loc[z, f'ev_attempt_allin_{rr}to1'].iloc[0]):.0f} (frictions {float(df.loc[z, f'ev_attempt_allin_{rr}to1_frictions'].iloc[0]):.0f})")
    print(f"\nexact Markov P(pass) for 1:1 $1,500 at zero edge = 16/49 = {16/49:.4f}")


if __name__ == "__main__":
    main()
