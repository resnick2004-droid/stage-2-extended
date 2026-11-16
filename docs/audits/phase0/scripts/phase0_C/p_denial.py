"""Audit estimate (track C), not a result: P re-derived from results/user_journey.csv start rows, then read under
two stated payout-denial models with NO random draws (exact binomial probabilities):
  (a) haircut: every payout received is cut by p (expected value of a per-payout denial; closure ignored)
  (b) thinning: each payout received by month k is denied independently with probability p; payouts of one
      start in a month are taken as equal-sized (the file holds only their count and total); closure ignored
  (c) all-or-nothing per trader: with probability p the firm denies every payout of the user (ToU s.27 reading);
      ahead share = (1 - p) x the base share (a denied user is down by fees)
Both (a) and (b) ignore the account closure a denial causes and the extra purchases after it, so they are
upper bounds on P under per-payout denial."""
import math
import sys

import numpy as np
import pandas as pd

R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
use = ["section", "config", "arm", "cell", "start_day", "start_date", "observed", "pay_days", "payouts"] + \
      [f"net_month_{k}" for k in (1, 2, 3)] + [f"fees_month_{k}" for k in (1, 2, 3)]
df = pd.read_csv(f"{R}\\user_journey.csv", usecols=lambda c: c in use, low_memory=False)
st = df[df["section"] == "start"].copy()


def binom_sf_gt(n: int, q: float, thresh: float) -> float:
    """P(Bin(n, q) * 1 > thresh) for real thresh."""
    kmin = int(math.floor(thresh)) + 1
    if kmin <= 0:
        return 1.0
    return float(sum(math.comb(n, j) * q ** j * (1 - q) ** (n - j) for j in range(kmin, n + 1)))


levels = (0.0, 0.10, 0.25, 0.50)
rows = []
for cfg in ("p14", "p15", "p16"):
    d = st[(st["config"] == cfg) & (st["arm"] == "verdict")]
    d = d[d["observed"] >= 63]
    for p in levels:
        hair, thin = [], []
        for k in (1, 2, 3):
            net = d[f"net_month_{k}"].to_numpy(float)
            fee = d[f"fees_month_{k}"].to_numpy(float)
            paid = net + fee
            hair.append(np.mean((1 - p) * paid - fee > 1e-9))
            pr = []
            for pdays, tot, f in zip(d["pay_days"], paid, fee):
                days = [int(x) for x in str(pdays).split()] if isinstance(pdays, str) and pdays.strip() else []
                n = sum(1 for x in days if x <= 21 * k)
                if n == 0 or tot <= 0:
                    pr.append(1.0 if -f > 0 else 0.0)
                    continue
                a = tot / n
                pr.append(binom_sf_gt(n, 1 - p, f / a + 1e-12))
            thin.append(np.mean(pr))
        base = np.mean([np.mean(d[f"net_month_{k}"].to_numpy(float) > 0) for k in (1, 2, 3)])
        rows.append({"config": cfg, "denial_p": p, "n_starts": len(d), "P_base": base,
                     "P_haircut": float(np.mean(hair)), "P_thinning": float(np.mean(thin)),
                     "P_all_or_nothing": (1 - p) * base,
                     "m1_haircut": hair[0], "m3_haircut": hair[2]})
out = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(out.round(4).to_string(index=False))
# check the count of payouts by month 3 equals what the totals imply (sanity)
d = st[(st["config"] == "p14") & (st["arm"] == "verdict") & (st["observed"] >= 63)]
print("p14 starts with >=63:", len(d), " median payouts by m3:",
      np.median([sum(1 for x in str(s).split() if int(x) <= 63) if isinstance(s, str) else 0 for s in d["pay_days"]]))
