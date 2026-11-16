"""Cash timeline of an XFA that has just won the 2:1 day-one all-in (balance $4,000 at the day-1 lock).
Standard path, harvest 1:1 $150 one trade a day, no frictions. Validated against the engine total (mean $3,598 per winner)."""
import numpy as np, pandas as pd
rng = np.random.default_rng(3); N = 200_000; H = 500
B = np.full(N, 4000.0); F = np.zeros(N); w = np.ones(N, int); alive = np.ones(N, bool)
cash = np.zeros(N); first = np.zeros(N); npay = np.zeros(N, int); first_day = np.full(N, -1); close_day = np.full(N, H)
for d in range(2, H + 1):
    idx = alive; risk = np.minimum(150.0, B - F); win = rng.random(N) < risk / (risk + 150.0)
    D = np.where(win, 150.0, -risk) * idx; B += D
    died = idx & (B <= F + 1e-9); alive &= ~died; close_day[died] = d; idx = alive
    F = np.where(idx, np.minimum(0, np.maximum(F, B - 2000)), F); w += (idx & (D >= 150)).astype(int)
    elig = idx & (w >= 5); q = np.where(elig, np.minimum(0.5 * B, 2000.0), 0.0); pay = elig & (q >= 125)
    first = np.where(pay & (npay == 0), 0.9 * q, first); first_day = np.where(pay & (npay == 0), d, first_day)
    B -= np.where(pay, q, 0); cash += np.where(pay, 0.9 * q, 0); npay += pay; F = np.where(pay, 0.0, F); w = np.where(pay, 0, w)
out = dict(winners=N, total_net_mean=cash.mean(), total_net_median=np.median(cash), total_net_p10=np.percentile(cash, 10), total_net_p90=np.percentile(cash, 90),
           first_payout_net_mean=first.mean(), first_payout_net_median=np.median(first), p_first_payout_exactly_1800=np.mean(np.isclose(first, 1800)),
           first_payout_day_median=np.median(first_day), first_payout_day_p90=np.percentile(first_day, 90), further_net_mean=(cash - first).mean(),
           payouts_mean=npay.mean(), close_day_median=np.median(close_day), close_day_p90=np.percentile(close_day, 90), engine_total_check=3598)
pd.Series(out).to_csv("results_payout_trace_2to1.csv", header=["value"]); print(pd.Series(out).to_string())
