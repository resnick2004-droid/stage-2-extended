"""RECORD ONLY (D-34): this models the fee bankroll of the zero-edge fail-and-repurchase campaign, which the firm prohibits as account stacking. Not a plan."""
"""Bankroll / risk-of-ruin model for the zero-edge prop-contract policy.
Own cash only: fees out, 0.9*payouts in. Attempts are i.i.d. draws from the engine."""
import numpy as np, pandas as pd, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from propsim import Rules, Policy, simulate_combine
from statepolicy import run_xfa, static, xfa_build_then_harvest
from scipy.optimize import brentq

def attempts(profile, frictions, n, seed):
    R = Rules(payout_fee=30.0 if frictions else 0.0, require_profit_since_payout=frictions)
    rng = np.random.default_rng(seed)
    c = simulate_combine(R, Policy(rr=1, risk=1500, trades_per_day=1), 0.0, n, rng)
    sub = c["sub_fees"].astype(float); passed = c["passed"].astype(bool); m = int(passed.sum())
    act = static(2, 750) if profile == "static" else xfa_build_then_harvest(3, 2000, 1, 150, 1)
    x = run_xfa(R, act, m, rng, 250, "standard")
    cash = np.zeros(n); cash[passed] = x["cash"]
    return pd.DataFrame(dict(sub=sub, act=np.where(passed, 149.0, 0.0), cash=cash, passed=passed,
                             net=cash - sub - np.where(passed, 149.0, 0.0)))

def adjustment_coef(net):
    f = lambda r: np.mean(np.exp(-r * net)) - 1.0      # Lundberg: E[e^{-r X}] = 1
    hi = 1e-3
    while f(hi) < 0: hi *= 2
    return brentq(f, 1e-9, hi)

def ruin(df, bankroll, horizon, paths, seed):
    rng = np.random.default_rng(seed); idx = rng.integers(0, len(df), size=(paths, horizon))
    sub, act, cash = df["sub"].values[idx], df["act"].values[idx], df["cash"].values[idx]
    bal = np.full(paths, float(bankroll)); dead = np.zeros(paths, bool)
    for t in range(horizon):              # fees are paid before that attempt's payouts arrive
        bal -= sub[:, t]; dead |= bal < 0
        bal -= act[:, t]; dead |= bal < 0
        bal += cash[:, t]
    return dead.mean()

def drawdown(df, horizon, paths, seed):
    rng = np.random.default_rng(seed); idx = rng.integers(0, len(df), size=(paths, horizon))
    # worst intra-attempt point: after fees, before cash
    cost = (df["sub"].values + df["act"].values)[idx]; cash = df["cash"].values[idx]
    cum_after = np.cumsum(cash - cost, axis=1); cum_before = np.hstack([np.zeros((paths, 1)), cum_after[:, :-1]]) - cost
    lows = np.minimum(cum_before, cum_after); peak = np.maximum.accumulate(np.maximum(cum_after, 0), axis=1)
    peak_before = np.hstack([np.zeros((paths, 1)), peak[:, :-1]])
    dd = np.max(peak_before - lows, axis=1)
    first_pos = np.argmax(cum_after > 0, axis=1).astype(float); first_pos[~(cum_after > 0).any(axis=1)] = np.nan
    return dd, cum_after[:, -1], first_pos

if __name__ == "__main__":
    rows, rr, dd_rows = [], [], []
    for profile in ["static", "allin3"]:
        for fr in [False, True]:
            df = attempts(profile, fr, 400_000, 11)
            x = df.net.values; r = adjustment_coef(x)
            tag = f"{profile}{'+fr' if fr else ''}"
            rows.append(dict(policy=tag, mean=x.mean(), sd=x.std(), p_pass=df.passed.mean(), p_pos=(x > 0).mean(),
                             mean_cost=(df["sub"] + df["act"]).mean(), adj_coef=r, B_1pct_lundberg=np.log(100) / r))
            for B in [100, 200, 300, 500, 750, 1000, 1500, 2000, 3000]:
                rr.append(dict(policy=tag, bankroll=B, ruin_200_attempts=ruin(df, B, 200, 40_000, 5), lundberg_bound=np.exp(-r * B)))
            for H in [10, 25, 50, 100]:
                dd, fin, fp = drawdown(df, H, 40_000, 7)
                dd_rows.append(dict(policy=tag, attempts=H, dd_p50=np.percentile(dd, 50), dd_p90=np.percentile(dd, 90), dd_p99=np.percentile(dd, 99),
                                    p_net_negative=(fin < 0).mean(), p5_net=np.percentile(fin, 5), median_net=np.median(fin),
                                    median_attempts_to_first_positive=np.nanmedian(fp) + 1, p_never_positive=np.isnan(fp).mean()))
    S = pd.DataFrame(rows); RU = pd.DataFrame(rr); DD = pd.DataFrame(dd_rows)
    S.to_csv("results_bankroll_summary.csv", index=False); RU.to_csv("results_ruin.csv", index=False); DD.to_csv("results_drawdown.csv", index=False)
    pd.set_option("display.width", 200)
    print(S.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print(RU.pivot(index="bankroll", columns="policy", values="ruin_200_attempts").to_string(float_format=lambda v: f"{v:.3f}"))
    print(RU.pivot(index="bankroll", columns="policy", values="lundberg_bound").to_string(float_format=lambda v: f"{v:.3f}"))
    print(DD.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
