# Handoff to the research stage

This repository answers: what does the Topstep 50K contract do to a trading process, which uses of it are permitted, and
what is a genuine edge worth within those limits. The next stage must find a trading process with a **demonstrated edge**.
This file tells it what that means, how much edge is worth pursuing, and how to value a candidate with this engine.
All numbers below are generated from result files in `edge/` (see `edge/T5_RESULTS.md`).

## 1. What cannot be used
- **The zero-edge campaign is prohibited** (account stacking; "not a viable strategy"; D-34). Structural value that exists at
  e = 0 is not a source of income for this project.
- No ranking or redesign by detectability (D-35). No cross-account hedging. No reliance on simulator fills that would not
  happen live (Prohibited Trading Strategies: "exploiting the relative lack of slippage in SIM to achieve impossible
  stop-loss execution").

## 2. Conduct constraints on any candidate (D-36)
Winners larger than losers (R > 1); risk per position well below the maximum (tested: ≤ $1,000 = 50 % of the $2,000
drawdown); no single position that decides the account; one account at a time; no fail-and-repurchase campaign.

## 3. Definition of a demonstrated edge
- **e** = mean P&L per trade ÷ $ risked per trade, **net of commissions and slippage**, with realistic fills (stops filled at
  the price the market would give, not at the stop).
- Measured on the trade structure the account will use: a fixed bracket (stop r, target R·r), R between 1.5 and 3, and the
  15:10 CT flatten applied (trades not resolved by then are closed at market — record their actual P&L, do not assume binary).
- **Out of sample**: rules fixed before the test period; walk-forward or a held-out period; no re-tuning on the test data.
- **Decision criterion (pre-registered here):** pursue a candidate only if the point estimate is e ≥ 0.10 **and** the one-sided
  95 % lower bound is ≥ 0.05. Below that, the edge is not distinguishable from the structural value (§4).

## 4. How much edge is worth pursuing
From `edge/T5_RESULTS.md` (pre-registered set, take-the-maximum payouts, 1-year funded horizon, standard path):

| e | share of EV per attempt that comes from the edge | failed Combines per year (one slot, continuous) |
|---|---|---|
| 0.02 | 25 % | 22 |
| 0.05 | 51 % | 19 |
| 0.10 | 80 % | 8 |
| 0.20 | 95 % | 4 |

Below e ≈ 0.05 most of the value is the structural (prohibited) component and the churn is high. At e ≥ 0.10 the edge
dominates and churn falls to a normal level. With the best funded payout policy found (exploratory, §6), EV per Combine
attempt is about $563 at e = 0.05, $1,757 at e = 0.10 and $8,464 at e = 0.20.

## 5. How much data a demonstrated edge needs (`edge/results_sample_size.csv`)
Per-trade SD in units of risk is ≈ (1+R)·√(p(1−p)): 1.23–1.83 across the brackets. Trades needed for the one-sided 95 %
lower bound to exceed half the true edge:

| R | e = 0.05 | e = 0.10 | e = 0.20 |
|---|---|---|---|
| 1.5 | 6,592 trades (26 yrs at 1/day) | 1,667 (6.6 yrs) | 423 (1.7 yrs) |
| 2 | 8,865 (35 yrs) | 2,263 (9 yrs) | 585 (2.3 yrs) |
| 3 | 13,412 (53 yrs) | 3,453 (14 yrs) | 910 (3.6 yrs) |

**Consequence:** an edge of the size that matters (≈ 0.10) cannot be demonstrated from a short live record at one trade a
day. The research stage must test on long historical data with realistic costs, and treat any short live or paper record as a
check on execution, not as proof of edge. Lower R needs fewer trades.

## 6. Funded-account payout policy (exploratory finding, D-45)
Any payout moves the floor to $0, so an early first payout leaves the account protected only by its own small balance. At
positive edge, **keep a buffer**: request only what leaves the balance at or above a threshold (engine: `Policy(keep_balance=…)`).
Best found: 1.5:1 at $500 with an $8,000 buffer — realised cash per funded account per year $1,006 / $2,411 / $8,313 at
e = 0.05 / 0.10 / 0.20, against $686 / $1,262 / $4,075 when taking the maximum at once. Coarse grid; treat as a direction,
and re-optimise for the actual edge and bracket.

## 7. How to value a candidate with this engine
```python
from propsim import Rules, Policy, simulate_xfa
from edge.combine_exact import combine_exact
R, r, e = 1.5, 500.0, 0.10                       # from the candidate's out-of-sample trade log (net of costs)
c = combine_exact(R, r, e)                        # exact: p_pass, mean_days, mean_sub
x = simulate_xfa(Rules(payout_fee=0.0, require_profit_since_payout=True),
                 Policy(rr=R, risk=r, keep_balance=8000.0), e, 50_000, horizon_days=504)
ev_per_attempt = c["p_pass"] * (x["cash"].mean() - 149.0) - c["mean_sub"]
```
Use the lower confidence bound of e, not the point estimate, for any sizing or money decision. If the candidate's trades are
not a clean two-outcome bracket (e.g. many flattened at 15:10), replace the binary draw with the empirical outcome
distribution before trusting the numbers.

## 8. Open limitations carried forward
One trade per day; fixed dollar risk; no scaling-plan contract limits; drift convention for edge inside truncated trades;
Responsible Trading Program placement would move new funded accounts to the Consistency path (values about 10–20 % lower,
`edge/T5_RESULTS.md` §2b) and add a Daily Loss Limit.
