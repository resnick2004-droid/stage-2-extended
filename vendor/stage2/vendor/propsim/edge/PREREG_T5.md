# Pre-registration — T5 value-of-edge table (written 2026-09-21, before any run)

## Question
For a trader with a genuine, demonstrated edge e, trading within the conduct constraints (D-36), what is the contract worth —
per attempt and per year of one account slot — and which admissible profile should they use?

## Profiles
- **Admissible (D-36):** winners larger than losers (R > 1), risk per position ≤ $1,000 (≤ 50 % of the $2,000 drawdown),
  one trade per day, static on both stages (no single position that decides the account):
  R ∈ {1.5, 2, 3} × risk ∈ {$500, $750, $1,000} → 9 profiles.
- **Reference only (not admissible):** 1:1 $1,500 — to measure what the constraints cost. Not eligible for "best".
- Combine and XFA profiles are chosen independently; the stages are independent given a pass, so any pair is composed
  exactly from stage-level results.

## Edges
e ∈ {0, 0.02, 0.05, 0.10, 0.15, 0.20} (expected P&L per trade as a fraction of $ risked, after costs; drift convention D-06).
e = 0 is reported as a reference point only (D-34).

## Stage computations
- **Combine:** exact forward Markov chain over (B, F, best day) with truncate floor, drift convention, Combine lock at $0,
  55 % consistency, one trade per day → P(pass), E[trading days], E[subscription $] (21-trading-day billing, D-31).
  Monte Carlo (N = 200,000 per cell) run alongside as the validator.
- **XFA:** Monte Carlo, N = 50,000 per cell, horizon 252 trading days (one year), Standard path and Consistency path
  (the Consistency path is the Responsible Trading Program scenario — RTP places new XFAs on it; official 13620045).
  Frictions on: net-positive-since-payout rule; payout fee $0 (fee-free methods exist, 8284233).
  Reports: net cash within the year, P(closed), trading days alive, days to first payout, payouts, unrealised balance at the horizon.

## Composed outputs (per Combine profile c, XFA profile x, path, edge)
- EV per attempt = P_pass(c) · (cash_1y(x) − 149) − E[sub](c)
- Cycle length L = E[days](c) + P_pass(c) · E[days alive](x)   (an XFA still alive at 252 days ends the cycle; its balance is *not* counted — conservative)
- Value of one account slot per year = 252 · EV / L   (renewal-reward rate)
- Best admissible pair per (edge, path) by value per year; edge at which the best pair changes.

## Validation criteria (fixed now)
- **V1 — exact vs Monte Carlo, Combine:** for every admissible and reference profile at every edge, P(pass) and E[days]
  from the chain must agree with Monte Carlo within 3 SE. 120 comparisons: about 0.3 exceedances expected by chance.
  More than 2 exceedances, or any beyond 4 SE, = systematic failure → stop and diagnose (D-40).
- **V2 — reproduction:** at e = 0 the chain's P(pass) for 1:1 $1,500 equals 16/49 to 1e-9, and for every admissible profile
  lies within 3 SE of the stored 160-cell grid (results_grid_edge0.csv).
- **V3 — XFA bounds and monotonicity:** at e = 0 mean gross payouts ≤ $2,000 + 3 SE and mean (B + Q) at closure-or-horizon
  ≤ 0 + 3 SE; for every profile and path, net cash is non-decreasing in e (a drop larger than 3 SE between adjacent edges = failure).
- Any failure is kept on record with its diagnosis (D-40); no rerun-until-pass.
