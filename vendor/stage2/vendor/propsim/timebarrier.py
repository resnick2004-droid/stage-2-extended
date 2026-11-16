"""
timebarrier.py — Stage-2 question that fixes the XFA number: the 15:10 CT flatten.

The day-one policy risks the whole room above the floor at R:1. Inside a session the trade
is a fair continuous path with three exits: the floor (stop), the target, or the session end
at whatever P&L the trade holds. Timing out is not a loss; the ratchet then moves the floor at
the 16:00 lock and the policy repeats the all-in on the remaining room the next day.

One parameter: session_sigma = standard deviation of the max-size position's P&L over one
session, in dollars. Results are reported against s = session_sigma / cushion so any
instrument / contract-cap combination can be read off once its session sigma is known.

After the first win the harvest phase recovers a measured fraction of the balance (from the
binary engine; ~1.0 without payout frictions). E[net] = 0.9 * harvest_eff * E[balance after
win] * P(win eventually).  Path discretisation: 600 steps/session (barrier overshoot bias is
small at this resolution and biases *against* the policy).

Usage: python timebarrier.py [--n 20000]
"""
import argparse
import numpy as np, pandas as pd
from propsim import Rules
from statepolicy import run_xfa, xfa_build_then_harvest

STEPS = 200   # with the bridge correction the step size only matters for the timeout P&L


def allin_until_resolved(rr, session_sigma, n, rng, cushion=2000.0, max_days=60, lock_at=0.0, mll=2000.0):
    """All-in on the full room at rr:1 every session until the balance reaches `cushion`
    (floor then locked at 0; the harvest recovers the balance) or the account dies.
    Returns (B, resolved, alive, days)."""
    B = np.zeros(n); F = np.full(n, -cushion)
    alive = np.ones(n, bool); won = np.zeros(n, bool); days = np.zeros(n, int)
    dt_sigma = session_sigma / np.sqrt(STEPS)
    for d in range(max_days):
        won = alive & (B >= cushion - 1e-9)
        act = alive & ~won
        if not act.any():
            break
        idx = np.where(act)[0]
        room = (B - F)[idx]
        stop = -room                       # liquidation at the floor
        target = rr * room
        x = np.zeros(len(idx)); done = np.zeros(len(idx), bool); res = np.zeros(len(idx))
        v = dt_sigma ** 2
        for _ in range(STEPS):
            live = ~done
            x0 = x[live].copy()
            x1 = x0 + rng.normal(0.0, dt_sigma, live.sum())
            st, tg = stop[live], target[live]
            # Brownian-bridge crossing probabilities between x0 and x1 (exact for BM)
            p_s = np.where(x1 <= st, 1.0, np.exp(-2.0 * np.clip(x0 - st, 0, None) * np.clip(x1 - st, 0, None) / v))
            p_t = np.where(x1 >= tg, 1.0, np.exp(-2.0 * np.clip(tg - x0, 0, None) * np.clip(tg - x1, 0, None) / v))
            u_s = rng.random(live.sum()); u_t = rng.random(live.sum())
            cs = u_s < p_s; ct = u_t < p_t
            both = cs & ct
            # both crossed within one step: attribute to the nearer barrier from x0 (unbiased on average)
            near_s = (x0 - st) <= (tg - x0)
            cs = cs & ~(both & ~near_s); ct = ct & ~(both & near_s)
            li = np.where(live)[0]
            res[li[cs]] = st[cs]; res[li[ct]] = tg[ct]
            done[li[cs | ct]] = True
            x[li[~(cs | ct)]] = x1[~(cs | ct)]
            if done.all():
                break
        res[~done] = x[~done]             # flattened at 15:10 at current P&L
        B[idx] += res
        days[idx] += 1
        dead = idx[res <= stop + 1e-9]
        alive[dead] = False
        surv = idx[(res > stop + 1e-9)]
        F[surv] = np.minimum(lock_at, np.maximum(F[surv], B[surv] - mll))
    won = alive & (B >= cushion - 1e-9)
    return B, won, alive, days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1234)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    rules = Rules()

    # harvest efficiency from the binary engine: E[paid | start balance b, floor 0] / b
    # measured with the build-then-harvest policy after a day-one win (frictions on/off)
    eff = {}
    for label, rl in [("no frictions", Rules()), ("$30 fee + profit-since-payout", Rules(payout_fee=30.0, require_profit_since_payout=True))]:
        r = run_xfa(rl, xfa_build_then_harvest(3, 2000, 1, 150, 1), 20000, np.random.default_rng(5), 250, "standard")
        # accounts that won day one hold 6000; gross paid on those / 6000
        won = r["gross"] > 0
        eff[label] = (r["cash"][won].mean() / 0.9) / 6000.0
    print("harvest efficiency (fraction of post-win balance eventually paid out):", {k: round(v, 3) for k, v in eff.items()})

    rows = []
    for s in [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]:
        for rr in [1, 2, 3, 5]:
            B, won, alive, days = allin_until_resolved(rr, s * 2000.0, a.n, rng)
            p_win = won.mean()
            gross = (B[won].sum() / a.n) * eff["no frictions"]
            net = 0.9 * gross
            net_fr = 0.9 * (B[won].sum() / a.n) * eff["$30 fee + profit-since-payout"]
            rows.append(dict(sigma_over_cushion=s, rr=rr, p_resolved=p_win, p_unresolved_60d=(alive & ~won).mean(),
                             mean_days=days.mean(),
                             mean_balance_if_win=B[won].mean() if won.any() else np.nan,
                             gross=gross, net=net, net_with_frictions=net_fr,
                             se=0.9 * B[won].std() * np.sqrt(p_win) / np.sqrt(a.n) if won.any() else np.nan,
                             binary_model_net=0.9 * 2000 * rr / (1 + rr)))
    df = pd.DataFrame(rows)
    df.to_csv("results_timebarrier.csv", index=False)
    pd.set_option("display.width", 220)
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
