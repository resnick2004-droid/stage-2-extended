"""Exact Combine outcome distribution for a static one-trade-per-day profile at edge e.

State after each 16:00 lock: (B, F, best_day). One trade per day with dollar risk r and reward W = R*r.
Room c = B - F. If c >= r the trade wins +W with p = (1+e)/(1+R) and loses -r. If c < r the floor is the nearer exit:
it wins +W with p_race(c, W, theta) and otherwise liquidates at the floor (-c, fail). theta is fixed at the trade's own
stop/target (D-06), which reduces to c/(c+W) at e = 0. At the lock: best_day = max(best_day, D);
F = min(0, max(F, B - 2000)) (Combine lock, R-1); pass if B >= max(3000, best_day/0.55).
Probability mass is propagated day by day until the unresolved mass is below `tol`. Balances are kept as exact
rationals-in-dollars rounded to 1e-6 to key the state dictionary.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from propsim import p_race, theta_from_edge

def combine_exact(R, r, e, mll=2000.0, target=3000.0, frac=0.55, sub=49.0, billing=21, tol=1e-13, max_days=20000):
    W = R * r
    p_full = (1.0 + e) / (1.0 + R)
    theta = theta_from_edge(r, W, e)
    key = lambda x: round(x, 6)
    dist = {(0.0, -mll, 0.0): 1.0}
    p_pass = p_fail = e_days = e_sub = 0.0
    day = 0
    while dist and day < max_days:
        day += 1
        fee_if_end = sub * (1 + (day - 1) // billing)      # $49 at day 1 and at the start of every 21-day period
        nxt = {}
        for (B, F, bd), m in dist.items():
            c = B - F
            if c >= r - 1e-9:
                p, loss = p_full, r
            else:
                p, loss = float(p_race(c, W, theta)), c
            # win
            Bw = B + W; bdw = max(bd, W); Fw = min(0.0, max(F, Bw - mll))
            if Bw >= max(target, bdw / frac) - 1e-6:
                p_pass += m * p; e_days += m * p * day; e_sub += m * p * fee_if_end
            else:
                k = (key(Bw), key(Fw), key(bdw)); nxt[k] = nxt.get(k, 0.0) + m * p
            # loss
            Bl = B - loss
            if Bl <= F + 1e-6:
                p_fail += m * (1 - p); e_days += m * (1 - p) * day; e_sub += m * (1 - p) * fee_if_end
            else:
                Fl = min(0.0, max(F, Bl - mll)); k = (key(Bl), key(Fl), key(bd)); nxt[k] = nxt.get(k, 0.0) + m * (1 - p)
        dist = nxt
        if sum(dist.values()) < tol:
            break
    unresolved = sum(dist.values())
    return dict(p_pass=p_pass, p_fail=p_fail, unresolved=unresolved, mean_days=e_days, mean_sub=e_sub, days_run=day)

if __name__ == "__main__":
    x = combine_exact(1.0, 1500.0, 0.0)
    print(x, " 16/49 =", 16 / 49, " diff", x["p_pass"] - 16 / 49)
