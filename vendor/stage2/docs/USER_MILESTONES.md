# The user's milestones: definitions (program U; D-620, D-621)

The gate (`docs/SUCCESS_CRITERIA.md`) ranks a design by the median two-year path's growth on its required bankroll.
This file defines what a *user* sees, for a user who starts on any day. It holds definitions only; every value is in a
result file (`results/user_journey.csv` once U1 is read). Nothing here changes the gate.

## The unit

A **unit** is one user: one trading day of a design's development window taken as a fresh start (fresh bankroll, fresh
accounts), the design's own trades replayed in historical order (D-508's machinery). Day 0 is the purchase evening; day
k closes the k-th session; a **month** is 21 sessions. A reading at h sessions is read only on starts with at least h
sessions left. Two arms: `verdict` (every R shifted to the bound the design's gate read) and `point`; the scorecard is
read on `verdict`. Percentiles are numpy's linear; an unreached unit counts as beyond, and a percentile beyond the
observed days is blank (D-518 (3)).

Neighbouring start days share almost all their sessions. The number of windows that do not overlap is the number of
start days divided by the horizon, so a one-month reading rests on many more independent windows than a twelve-month
one. Everyone who starts on the same day gets the same trades: "across users" here means across start days.

## The six milestones

| # | milestone | measure | engine fields | direction |
|---|---|---|---|---|
| 1 | Starting bankroll | The deepest cash below the start over the closes before the day the first payout's cash arrives: p50, p90, p95 over units paid by session 126, with the share not paid by then beside. Kept apart from `pf_required_p90`, which covers the whole two-year path | `cash_series`, `initial_bankroll`, the pay days; `customer_journey.spent_before` | lower |
| 2 | First evaluation pass | Sessions to the first pass (share by 5, 10, 21, 42; p50, p90); cash spent before it (p50, p90, p95); the chance that N evaluations in a row all fail (resampled paths) | `combines[].passed`, `.resolved_on`; `chance_no_pass_in_N_combines` | lower |
| 3 | First payout | Sessions to the day its cash arrives (share by 21, 30, 42, 63, 90, 126; p50, p90, p95); the first payout's cash (p10, p50, p90); payouts received per dollar of fees at months 1, 3, 6, 12 | `days_to_first_payout`, `payout_gaps`; `payout_days`, `payout_cash`; `total_payouts`, `total_fees` | sooner; more per dollar |
| 4 | Periodic results | At months 1, 2, 3, 6, 9, 12: the share of units with net cash above zero, and the net's p5, p10, p25, p50, p75, p90. Net cash is payouts received less every fee | `cash_series` at month ends | higher |
| 5 | Consistency across users | The share with no payout by months 1, 2, 3, 6; the longest gap after the first payout within 126 and 252 sessions (p50, p90, longest); the share of later months with no payout; the concentration at months 3, 6, 12: the net summed over the best quarter of units over the net summed over all (blank when the total is not positive) | the pay days; the month-end nets | lower gaps, lower concentration |
| 6 | Execution variance | The standard deviation of the net across units inside a design against the standard deviation of the designs' means; the share paid by session 21 by start year; per unit, the mean over the standard deviation of its twelve monthly changes; the same design under other coin sequences and seeds | the month-end nets; `p16_robust.csv`'s form | reported, never selected on |

## The quit rules (assumptions, not measurements)

- **Q1.** A unit with no payout by session 21 stops and keeps its 21-session net; otherwise it keeps its 126-session
  net. Read also at sessions 30 and 42 as a sensitivity.
- **Q2.** Q1, and a unit not ahead at session 63 stops there and keeps its 63-session net.

There is no user data behind either rule.

## The scorecard (D-621)

| key | measure | direction | role |
|---|---|---|---|
| P | The mean of the shares of units ahead at months 1, 2 and 3 | higher | **primary** |
| S1 | Cash spent before the first payout, p90 | lower | guarded |
| S2 | Sessions to the first pass, p90; cash spent before it, p90 | lower | reported |
| S3a | Share paid by session 21 | higher | guarded |
| S3b | Sessions to the first payout, p90 | lower | guarded |
| S3c | Payouts received per dollar of fees at month 3, pooled over units | higher | guarded |
| S3d | The first payout's cash, p50 | higher | reported |
| S4a | Share ahead at month 6 | higher | guarded |
| S4b | Share ahead at month 12 | higher | guarded |
| S5a | Net cash at month 3, p10 | higher | guarded |
| S5b | Longest gap after the first payout within 126 sessions, p90 | lower | guarded |
| S5c | Concentration at month 6 | lower | guarded |
| S6 | Luck against design | none | reported |
| Q | Mean value under Q1 and Q2 | higher | reported |

The row to beat on each key, the selection rule, the tolerances and the guards are in D-621.

## What was already modelled (pointers; readings are in the files)

| item | decision rows | result file | milestones |
|---|---|---|---|
| Customer slices: 21, 63, 126 sessions per start | D-508, D-510 | `customer_slices.csv` | 4, 5 |
| Consistency lines; P-14, P-15, P-16 slice lines | D-509, D-513, D-532, D-547 | each gate file and its `_slices.csv` | 4, 5 |
| Customer journey (11 configurations; no P-15, P-16) | D-518 to D-520 | `customer_journey.csv`, `_paths.csv` | 1 to 5 |
| Payout policy: buffer, half requests | D-564 to D-566 | `rc150_payout_screen.csv` | 3, 5 |
| Sizing table re-solved; risk-averse sizing | D-559 to D-563; D-405 to D-408 | `rc150_table_screen.csv`; `fv3s_screen.csv` | 4, 5 |
| Routing between accounts | D-568, D-576 | `rc150_routing.csv` | 3 |
| Stop width | D-538 to D-544, D-594 to D-598 | `rc_width_screen.csv`, `rc_width_diag.csv`, `rc_stop_fine.csv` | 3 |
| Slippage, entry delay, single years, coin sequences | D-583 to D-585, D-602 to D-605 | `p16_slip_stress.csv`, `p16_robust.csv` | 6 |
| Purchase budget and no closure | D-501 to D-506 | `a3_compliance.csv`, `fv3c_compliance.csv` | 1, 4 |
| Focused Trader Program | D-495 to D-498 | `ftp_sweep.csv`; the ftp rows of each gate file | firm discretion |
| Seat counts, seat splits, Lucid | D-365, D-366, D-567 to D-577, D-593, D-601 | `fv3d_levers_accounts_*.csv`, `rc150_firm_split*.csv`, `rc150_added_lucid.csv` | 1, 3, 5 |
| Trading-hours windows | D-525, D-527, D-538, D-618 | the window rows of `rc_s100_all_gate.csv`, `rc_s150_all_gate.csv` | 3, 4 |
| Funded-risk cap | D-542, D-544 | `rc_width_diag.csv`; the funded-cap rows of `rc_s150_all_gate.csv` | 1, 3 |
| A funded account's time budget | D-364 | `fv3c_xfa_time_budget.csv` | 2, 3 |
| Collect phase, second trade, SPEED, SPEED-2 (FV3-C) | D-368 to D-370, D-381, D-390 to D-397 | `fv3d_levers_*.csv`, `fv3d_speed_first_2x_full.csv` | 3 |
| Steadiness columns | D-402 | the `st_` columns of each gate file | 4, 6 |
| Hypothetical hedge and mirror (context only, prohibited) | D-514 to D-517, D-619 | `hypo_*.csv`, `hedge_cycle.csv` | none |

## What no file holds before U1

A start-day reading past 126 sessions; month 2 for P-15 and P-16; the first payout's cash; the 95th-percentile cash
before the first payout for P-15 and P-16; the concentration as a stored field; any start-day journey for the
funded-capped, four-seat, added-Lucid or single-window cells.
