# Phase 0 audit, track A: every figure in the handoff re-derived from its cited file

Audited: `vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` (the snapshot of Stage 2 f1b42e2). Read-only; no engine,
no simulation, no `data/bars` or `data/atlas` read. Every value below was re-read by scratch scripts (pandas, `usecols`
or section filters; one process at a time) from `vendor/stage2/results/*.csv` and their manifests, plus
`vendor/stage2/config/rules.yaml`, `vendor/stage2/DECISIONS.md`, `vendor/stage2/prereg/` and
`vendor/stage2/vendor/propsim/DECISIONS.md`. The live Stage 2 repository was **not** read: every file the handoff
cites is in the snapshot.

**Counts** (one figure = one number or one numeric claim; a rule value or design parameter counts when the handoff
attaches a source to it): **205 figures: 191 MATCH, 7 DIFFERS, 3 NOT FOUND, 0 AMBIGUOUS, 4 NO SOURCE.** Every cited
result file's sha256 equals its manifest (33 of 33).

---

## 1. Summary of findings, by severity

### CHANGES-A-CONCLUSION
None. Every headline number re-derives exactly at the precision shown. That covers the drivers of P, the 1.3 table,
the menu, the funded-account life table, the value map, the nine families' judged P values and the 76-cell count.
The between-design rank correlations and the regression were also recomputed independently from `design_table`
(Spearman on ranks, standardised OLS), and they reproduce the file to 1e-6.

### MATERIAL
None found.

### MINOR
1. **D-212 and D-308 are cross-cited (handoff 2.4).**
   - "At most 5 % reach the 15:10 CT flatten (D-212)": D-212 (2) says **2 %**. The 5 % comes from D-308 (3), which
     amended it.
   - "At least 90 % of trades realise at least 90 % of intended risk (D-308)": D-308 holds no realised-risk rule.
     That rule is D-212 (1).
   - The rule values are right; the citations are swapped.
   - The swap is carried into this repository: `CHARTER.md` section 4 ("realised risk matching intended (Stage 2
     D-308)"), E-003 ("K3 realised risk (Stage 2 D-308)") and `prereg/F-01` section 2 and kill line K3.
2. **"The 12.5-point stop loses to costs (D-527)" overstates D-527 (handoff 2.2).**
   - What D-527 (3) says: at the 12.5-point rung "costs are a larger share of the risk: the all-day, Asia and London
     cells clear the line far below P-14, and the US-hours cell is killed". The stop is worse; it does not lose.
   - R\* = P-14 itself trades the 12.5/25-point rungs (REGISTRY P-14; handoff 1.3).
   - Carried into E-003 (c) and F-01 section 2 as the reason the 12.5-point stop is not offered. F-01 is pinned, so a
     correction can only be a reading in a later row.
3. **The evaluation's sizing (handoff 2.5) is not in the cited file.** `u_xfa_day_budget.csv` has no evaluation sizing
   rows; its `opening_trade` rows are funded only.
   - The ask ("1.5R at $2,000 fresh") is confirmed elsewhere: `a3_brk30_cb20_gate.csv` and `rc_s150_all_gate.csv`,
     section `policy_fresh`, phase `combine`: `policy_risk` 2000, `policy_rr` 1.5. The same leaf appears in
     `u_value_map.csv` `records_leaf`.
   - "Realised about $1,000 (P-14) and $1,500 (P-16), the size limit binding" is in no snapshot file. These are
     exactly the **funded opening's** `realised_risk_p50` (1000 / 1000 / 1500).
   - Arithmetic from `stop_band.csv`'s combine cap (37 micros) also argues against the size limit binding for P-16:
     a $2,000 ask at 37.5 points sizes 26 micros (about $1,950). This needs the engine's records to settle.
4. **The stop-band table (handoff 2.2) does not describe P-14's or P-16's sizing.** The values match `stop_band.csv`.
   But the description beside them does not:
   - "Risk the table uses": the risks are stage one's lifecycle family. The `stop_band.py` docstring gives "static
     1:1 $1500" and "build 2:1 $1000 -> harvest 1:1 $300 @B>=2000". They are not P-14's or P-16's state table, which
     asks $2,000 at the evaluation and at the funded opening (handoff 2.5).
   - "Micro cap": this is the engine's headroom cap, 0.75 x the firm allowance (`sizing.cap_micros`: 37 = floor(0.75
     x 50), 15 = floor(0.75 x 20)). It is not the firm limit in handoff 2.1.
   - The funded opening of P-14, P-15 and P-16 trades 20 micros (`u_xfa_day_budget.csv` `opening_trade`
     `contracts_p50`), above the band's 15.
5. **"Stops under 45 ticks are eaten by costs" (2.2) overstates the cost floor.** The floor is the stop at which cost
   drag equals **0.10** of the stop (`stop_band.csv` manifest `cost_drag_floor` 0.1; the docstring says "costs eat a
   tenth of it").
6. **"The router uses only a few percent of what it is offered" (2.6).** True of the coins (P-15 0.022, P-16 0.026);
   P-14 routes 0.149 (`signal_supply`, router, `share_routed`). The claim it supports ("signals are not the limit")
   still holds.
7. **Wrong propsim row for the contract ceilings (2.3).** The handoff cites "propsim D-08, D-47". D-47 is the
   research criterion (e at least 0.10). The ceilings are propsim D-02 (2/5; $2,000) and D-15 (0.327131); D-08 is
   right for 16/49.
8. **Two result manifests were written from a dirty tree:** `stop_band.csv` (commit `f00738a...-dirty`, regenerated
   under D-645) and `scoreboard.csv`. That conflicts with the handoff's own "results come only from a clean, detached
   checkout" (4.3). `stop_band.csv` is cited by the handoff, `CHARTER.md` and F-01. Its NQ rows re-derive by
   arithmetic: cap stop = ceil(risk / (cap x $0.50)), wide edge = risk / $0.50.

### NOTE
- **The "rank correlations" are genuine Spearman correlations,** but over fewer than 61 designs for some measures:
  S1 over 60, S3b over 53. The regression's n is 60.
  - The 61 include 6 Lucid upper-bound cells. Without them (`without_lucid`), S3c is 0.750 (0.271 to 0.948) and the
    conclusion stands.
  - S5a's correlation, 0.813, is higher than S3c's. The file flags it `mechanical`, and the handoff leaves it out.
- **"Speed and bankroll barely do" (1.2).** In the regression beside, S3a's standardised weight is 0.136 and its
  family-bootstrap interval is 0.058 to 0.639, which excludes zero (0.214, 0.151 to 0.709 without Lucid). Speed has
  a small, interval-positive weight.
- **Within design (1.2),** the largest correlate of the month-1 net is payouts per fee dollar, 0.994. It is close to
  an identity with net, and the handoff omits it. Bankroll, -0.320, is larger than the two "hardly matter" figures.
- **"The best designs on file for a user" (1.3)** lists P-14 first at P 0.671. In the same file, section and block,
  four family cells score higher: `nobudget_p14` 0.692, `budget15_p14` 0.678, `budget30_p14` 0.678, `budget15` 0.674.
  They are exploratory and uncarried; `nobudget_p14` reappears in the 1.4 menu.
- **"Of those, reach the payout" (2.5)** reads `share_requested_first_payout`, a request, not a payout received.
- **"Sessions from opening to fifth winning day, median" (2.5)** does not name its group. Only
  `in_profit_after_opening` gives 8 / 9 / 10; `lost_opening_and_lived` gives 9 / 9 / 11 and `all_opened` 9 / 9 / 10.
  It sits under "of those", so the group is inferable.
- **"FV3-C does [depend on the order of days]" (1.3).** In `v1_validation_a1` its growth at the bound stays above
  zero at every mean block, though it falls from 0.991 to 0.674. It reaches zero only inside B2's declared shifts at
  block 21 (`v1_validation_b2`, break-even shift -0.132). D-665 says the same.
- **The lowest-cost menu pick, `seats1_p14`, is off the frontier.** `wallet1000` and `wallet1000_p14` dominate it,
  but they fail the S4b floor at 0.667 and 0.708. The menu rule is applied correctly; I re-ran it from
  `design_table`, and the 6 eligible designs for `balanced` and the 38 for `best_result` (44 less the 6 Lucid cells)
  match.
- **Program counts inside the family manifests are not cumulative** (`u_entry` lists only itself; `u_seats` omits
  entry; `u_consistency` omits firms). D-651 records this ("the file's own count ... was taken at its commit"). The
  final 76 is right.
- **"136 strategies against their coin twins (D-558)" (3.2).** 136 is D-550/D-553's A4 count. D-558's schedule
  control covers the 13 strategies that survived the lift test.
- **"Hedge pairs under a fifth of signals" (3.1).** `u_firms.csv` `deal.share_dealt_signals_paired` peaks at 0.2026
  (`l5_day0_hedged`); the other 11 hedged cells are at most 0.199.
- **"An output outside a ceiling is an engine error" (2.3).** `setups_per_day.csv`'s Monte Carlo P(pass) at 0.1 setups
  a day, zero edge, $1,500 1:1 is 0.3345, above the supremum 0.327131. That is within about one standard error at
  2,000 Combines. A simulated output needs a tolerance before this rule can refuse it.
- **"Five or more signals a session per firm" and "about one decisive trade per account per day" (2.6)** are not in
  D-452's or D-154's row text. Stage 2's `CLAUDE.md` states them and attributes them to D-452's reset handoff section 4
  (`docs/HANDOFF_RESET_2026-10-29.md`, not in the snapshot).
- **For F-01's red team (track D),** K3's "intended risk" is undefined for a screen with no sizing. D-212 (1) defines
  it as capped: contracts = min(floor(risk / stop), cap). P-16's funded opening realises $1,500 of a $2,000 ask.
- **`u_value_map.csv`'s manifest timestamp is 2026-11-16T05:51Z,** which is 2026-11-15 23:51 CT. That is consistent
  with "copied on 2026-11-15" in local time.

---

## 2. Figure-by-figure table

R = `vendor/stage2/results/`. "verdict" is the U files' bound arm: every R at its one-sided 0.05 bound. The
`user_journey.csv` and `u_xfa_day_budget.csv` manifests confirm this, so it matches the handoff's "bound / verdict arm".

### Section 1.1 and 1.2 -- `R/user_drivers.csv`

| # | handoff (section) | file, section, filter | my value | status |
|---|---|---|---|---|
| 1 | a month = 21 sessions (1.1) | manifest `parameters.month_sessions`; `definitions` subject `month` | 21 | MATCH |
| 2 | S1..S5c definitions (1.1 table) | `definitions`, column `meaning`, subjects P, S1..S5c | same meanings | MATCH |
| 3 | 61 designs (1.2) | manifest `cells.in_the_table`; `design_table` verdict/all rows | 61 (58 family + 3 rows to beat) | MATCH (S1 n 60, S3b n 53) |
| 4-5 | S3c 0.76 (0.37 to 0.93) | `between_designs`, subject `all_cells`, `spearman.S3c` | 0.764550 (0.367036, 0.933942) | MATCH |
| 6-7 | S3a 0.19 (-0.45 to 0.87) | same, `spearman.S3a` | 0.186115 (-0.451772, 0.874509) | MATCH |
| 8-9 | S1 0.09 (-0.46 to 0.55) | same, `spearman.S1` | 0.089706 (-0.464704, 0.554047), n 60 | MATCH |
| 10-11 | S3b 0.07 (-0.67 to 0.60) | same, `spearman.S3b` | 0.070627 (-0.667112, 0.599629), n 53 | MATCH |
| 12 | S3c weight 0.88 | same, `beta.S3c` | 0.875010 | MATCH |
| 13 | R squared 0.92 | same, `r2` | 0.917498, n 60 | MATCH |
| 14 | sessions to first payout -0.74 | `within_design`, subject p14, arm verdict, month 1, `spearman.net.sessions_to_first_payout` | -0.741558 | MATCH |
| 15 | paid by the month 0.70 | same, `spearman.net.paid_by_month` | 0.698202 | MATCH |
| 16 | first payout dollars 0.68 | same, `spearman.net.first_payout_dollars` | 0.684117 | MATCH |
| 17 | cash before first pass -0.10 | same, `spearman.net.cash_before_first_pass` | -0.096604 | MATCH |
| 18 | sessions to first pass -0.12 | same, `spearman.net.sessions_to_first_pass` | -0.118142 | MATCH |
| 19 | spread share 0.99, month 1, P-14 | `accounting`, p14, verdict, month 1, `spread_share_payouts` | 0.991523 | MATCH |
| 20 | nine configurations | `design_vs_luck`, `u1_configurations`, `designs` | 9 | MATCH |
| 21-25 | design 0.075 / 0.032 / 0.041 / 0.092 / 0.195 | `design_vs_luck`, `u1_configurations`, verdict, `design_share`, months 1/2/3/6/12 | 0.074508 / 0.031659 / 0.041413 / 0.091922 / 0.194904 | MATCH |
| 26-30 | three best 0.016 / 0.002 / 0.016 / 0.058 / 0.141 | same, subject `rows_to_beat` (p14, p15, p16) | 0.015526 / 0.002484 / 0.015621 / 0.058030 / 0.140808 | MATCH |

### Section 1.3 -- `R/u_budget.csv` section `cell`, block `all`, arm verdict; registry; V1

| # | handoff | filter | my value | status |
|---|---|---|---|---|
| 31-36 | P-14: 0.671, $3,003, 0.795, 1.85, 0.985, -$769 | cell `p14` | 0.671168, 3003.0, 0.794734, 1.851329, 0.984674, -768.712628 | MATCH |
| 37-42 | P-15: 0.642, $3,003, 0.768, 1.74, 0.966, -$1,146 | cell `p15` | 0.642112, 3003.0, 0.768402, 1.743135, 0.966156, -1146.457852 | MATCH |
| 43-48 | P-16: 0.620, $3,450, 0.595, 2.08, 0.977, -$1,162 | cell `p16` | 0.620012, 3450.0, 0.594853, 2.079778, 0.977011, -1161.930635 | MATCH |
| 49 | P-14 at most 20 purchases in 21 sessions | `prereg/REGISTRY.md` P-14 row | "a budget of 20 Combine purchases in 21 trading days" | MATCH |
| 50 | P-14 PASS at 0.05/370 | REGISTRY P-14 row; `scoreboard.csv` verdict | "grows at 0.05/370"; PASS | MATCH |
| 51 | P-15 PASS at 0.05/403 | `prereg/P-15_rc-s100-all.md`; D-532; scoreboard | 0.05/403; PASS | MATCH |
| 52 | P-16 PASS at 0.05/414 | `prereg/P-16_rc-s150-all-nr.md`; D-547; scoreboard | 0.05/414; PASS | MATCH |
| 53 | P-16 holds at 5, 21, 63-session blocks; missed trades and sessions; every declared shift | `v1_validation_a1` (S1, verdict (0.05/414), mean block 1/5/21/63: growth 1.424 / 1.384 / 1.457 / 1.443, all above zero); `_c1` `c1_summary` (trade 0.10 and 0.25, session 0.10: every realisation above zero); `_b2` `b2_curve` (shifts to -0.16: all above zero) | as stated | MATCH (see the FV3-C note) |

### Section 1.4 -- `R/user_drivers.csv` section `menu` (arm verdict)

| # | handoff | filter | my value | status |
|---|---|---|---|---|
| 54-56 | lowest cost, P-14 on one account: 0.460, $1,774, 0.211 | `lowest_cost`, picked `seats1_p14` | 0.460405, 1774.0, 0.211251 | MATCH |
| 57-59 | balanced, budget 10: 0.645, $2,355, 0.615 | `balanced`, `budget10_p14` | 0.645181, 2355.4, 0.614602 | MATCH |
| 60-62 | best, no budget: 0.692, $3,405, 0.819 | `best_result`, `nobudget_p14` | 0.692040, 3405.0, 0.818671 | MATCH |
| 63-65 | limits $2,000 / $2,500; floor 95 % at month 12 | `limit`, `floor`; manifest `menu.floor_measure` S4b | 2000 / 2500; 0.95 on S4b | MATCH |

### Section 2.1 -- `vendor/stage2/config/rules.yaml` (values and article ids)

| # | handoff | rules.yaml key(s) | value / article | status |
|---|---|---|---|---|
| 66 | target $3,000 (8284208) | `combine_profit_target` | 3000, 8284208 | MATCH |
| 67-69 | MLL $2,000 trailing, locks at start balance (8284204) | `combine_mll`, `combine_mll_lock_at` | 2000; 0.0; 8284204 | MATCH |
| 70-71 | XFA starts -$2,000; $0 after first payout | `xfa_mll_start`, `xfa_lock_at` (note: "After your first Payout ... MLL is set to $0") | -2000; 0.0 | MATCH (the XFA MLL also locks at $0 once the balance reaches $2,000; not stated in the handoff) |
| 72-74 | best day 55 % ($1,650); Consistency 40 % | `combine_consistency_max_day_frac`, `xfa_cons_max_day_frac` | 0.55 (x 3000 = 1650); 0.4; 8284208 | MATCH |
| 75-77 | 5 minis (50 micros); scaling 2 / 3 / 5 from $0 / $1,500 / $2,000 (8284197, 8284223) | `combine_position_size_limit`, `funded_scaling_plan` | 5; "0:2,1500:3,2000:5"; 8284197, 8284223 | MATCH |
| 78-80 | Standard 5 days of at least $150; Consistency 3 days | `xfa_std_winning_days`, `xfa_std_winning_day_min`, `xfa_cons_min_days` | 5; 150; 3 | MATCH |
| 81-85 | payout 50 %; caps $2,000 / $3,000; 90 %; minimum $125 (8284233) | `payout_max_frac_of_balance`, `xfa_std_cap`, `xfa_cons_cap`, `profit_split`, `payout_min` | 0.5; 2000; 3000; 0.9; 125; 8284233 | MATCH |
| 86-88 | $49 a month, $49 reset (14289835); $149 activation (8284217) | `subscription_fee`, `reset_fee`, `activation_fee` | 49; 49; 149 | MATCH |
| 89 | at most 5 funded, shared across sizes (8284215) | `max_active_funded_accounts`, `xfa_cap_shared_across_sizes` | 5; true | MATCH |

### Section 2.2 -- `R/stop_band.csv`, market NQ

| # | handoff | row (state) | file value | status |
|---|---|---|---|---|
| 90-93 | evaluation: $1,500, 37 micros, 82 ticks (20.5 points) | `combine`: risk, cap_micros, cap_stop_ticks | 1500, 37, 82 (x 0.25 = 20.5) | MATCH (meaning: MINOR 4) |
| 94-97 | funded below $2,000: $1,000, 15, 134 (33.5) | `funded_below_2000` | 1000, 15, 134 (33.5) | MATCH |
| 98-101 | funded at or above $2,000: $300, 37, 17 (4.25) | `funded_at_or_above_2000` | 300, 37, 17 (4.25) | MATCH |
| 102-103 | cost floor 45 ticks (11.25 points) | `cost_drag_floor_ticks` | 45 (11.25) | MATCH (meaning: MINOR 5) |
| 104 | the 12.5-point stop loses to costs (D-527) | D-527 (3) | the cells clear the line far below P-14; US hours killed | **DIFFERS** (MINOR 2) |
| 105 | fixed 20-point brackets lose (D-423) | D-423 | net edge negative at the bound; FAIL | MATCH |
| 106 | 37.5 best; 40 and 50 worse or unresolved (D-542, D-598) | D-542 (2), D-598 | 50 fails resolution; 40 grows less; 37.5 stays best | MATCH |

### Section 2.3 -- the contract ceilings

| # | handoff | source checked | value | status |
|---|---|---|---|---|
| 107 | P(pass) at most 2/5 | Stage 2 `CLAUDE.md`; propsim D-02 | 2/5 | MATCH |
| 108 | supremum 0.327131 | propsim D-15; `state_policy_v12_noclose.csv` `oracle` bound | 0.327131 | MATCH |
| 109 | 1:1 at $1,500 passes 16/49 | propsim D-08; same file, `p_pass_1to1_1500_zero_edge_no_fees` | 16/49 (0.326531) | MATCH |
| 110 | E[gross] at most $2,000 | propsim D-02; same file oracle bound | 2000 | MATCH |
| 111 | cited "propsim D-08, D-47" | propsim D-47 | the research criterion, no ceiling | **DIFFERS** (MINOR 7) |

### Section 2.4 -- execution rules (decision rows)

| # | handoff | row | what it holds | status |
|---|---|---|---|---|
| 112 | at least 5 minutes, alert to order (D-266) | D-266 (1) | L = 5 minutes; verdict at L | MATCH |
| 113 | one position across a firm's accounts, 5 minutes flat (D-429) | D-429 (1) | strict rule, D-160's five-minute gap | MATCH |
| 114 | at most 5 % to the 15:10 flatten; no time stops (D-212) | D-212 (2) | 2 %, raised to 5 % by D-308 (3); no time stop | **DIFFERS** (citation; MINOR 1) |
| 115 | at least 90 % realise at least 90 % (D-308) | D-308 | no such rule; it is D-212 (1) | **DIFFERS** (citation; MINOR 1) |
| 116 | none before 07:35 CT on a BLS 08:30 day; FOMC out (D-525, D-533) | D-533 | "no entry ... before 07:35 CT"; "FOMC days ... as declared"; D-525's text has neither | MATCH (via D-533) |
| 117 | each account its own trades (D-157) | D-157 | rotation; copying is not a candidate layout | MATCH |

### Section 2.5 -- `R/u_xfa_day_budget.csv`, arm verdict

| # | handoff | filter | my value | status |
|---|---|---|---|---|
| 118 | evaluation asks 1.5R at $2,000 | the cited file has no evaluation sizing rows | found instead in `a3_brk30_cb20_gate.csv` / `rc_s150_all_gate.csv` `policy_fresh`, combine: 2000, 1.5 | **NOT FOUND** in the cited file (value confirmed elsewhere) |
| 119-120 | evaluation realised about $1,000 (P-14) and $1,500 (P-16) | no file in the snapshot | -- (these equal the funded opening's) | **NOT FOUND** (MINOR 3) |
| 121-122 | funded opening asks 3R at $2,000 | `opening_trade`, `opened`, `policy_risk_p50`, `policy_rr_p50` | 2000, 3.0 (all three) | MATCH |
| 123 | realised $1,000 to $1,500 | same, `realised_risk_p50` | 1000 / 1000 / 1500 | MATCH |
| 124 | mostly $250 at 1R; paid $250 to $500 at 1R to 2.5R | `table_leaves`, `share_of_funded_days` | P-14: funded $250 1R 0.244 (the largest non-opening funded leaf); paid leaves $250 to $500, 1R to 2.5R; the same shape for P-15 and P-16 | MATCH |
| 125-127 | win the opening 0.251 / 0.219 / 0.225 | `opening_trade`, `opened`, `share_won_it` | 0.250827 / 0.219015 / 0.224617 | MATCH |
| 128-130 | of those, reach the payout 0.939 / 0.922 / 0.963 | `after_opening`, `in_profit_after_opening`, `share_requested_first_payout` | 0.939127 / 0.922438 / 0.963326 | MATCH (a request) |
| 131-133 | lose it and live 0.749 / 0.781 / 0.775 | `opening_trade`, `share_lost_it_and_lived` | 0.749173 / 0.780985 / 0.775192 | MATCH |
| 134-136 | of those, ever paid 0.199 / 0.193 / 0.110 | `opening_trade`, `lost_opening_and_lived`, `share_ever_paid` | 0.198936 / 0.192653 / 0.110466 | MATCH |
| 137-139 | their share of pre-payout account-days 0.610 / 0.649 / 0.574 | `budget_before_first_payout`, `lost_opening_and_lived`, `share_of_account_days` | 0.610047 / 0.649034 / 0.574069 | MATCH |
| 140-142 | median sessions, opening to fifth winning day, 8 / 9 / 10 | `after_opening`, `in_profit_after_opening`, `sessions_after_opening_to_fifth_winning_day_p50` | 8 / 9 / 10 | MATCH (group inferred; see NOTE) |
| 143-145 | funded trades per live account-day 0.920 / 0.931 / 0.841 | `signal_supply`, `funded`, `trades_per_account_day` | 0.919940 / 0.930572 / 0.840894 | MATCH |
| 146-148 | share of offers routed 0.149 / 0.022 / 0.026 | `signal_supply`, `router`, `share_routed` | 0.149140 / 0.022082 / 0.025795 | MATCH |

### Section 2.6 -- supply

| # | handoff | source | value | status |
|---|---|---|---|---|
| 149-150 | about one decisive trade per account per day; five or more signals a session per firm (D-452, D-154) | D-452 and D-154 row texts | neither number is there | **NO SOURCE** (design targets; Stage 2 `CLAUDE.md` states them) |
| 151 | the router uses only a few percent | row 146-148 | P-14 0.149 | **DIFFERS** (MINOR 6) |
| 152-154 | one $1,500 1:1 setup a day passes as often as any frequency; median 2 days; more than one a day lowers the pass rate | `setups_per_day.csv`, rr 1, risk 1500, edge 0 | p_pass 0.3245 at 1 a day (0.2950 to 0.3345 at 0.1 to 0.5); median 2 days; 0.1880 at 2, 0.1170 at 8; `best_setups_per_day_for_passes` 1 | MATCH |

### Section 2.7 -- `R/u_value_map.csv` (edge set `bound`, five seats)

| # | handoff | filter | my value | status |
|---|---|---|---|---|
| 155-164 | P-14 value of a win, $/yr per +1 point: (b) $225, $914; (c) $1,426, $1,073; (d) $629, $2,109; (e) $665, $2,442; (a) $553, $6,538 | `place_values`, base p14, `mean_dv`, `dollars_per_year_forward` | 225.42, 914.09; 1426.34, 1073.48; 629.35, 2108.84; 664.63, 2441.62; 552.57, 6538.04 | MATCH |
| 165-174 | P-16: (b) $287, $1,224; (c) $2,277, $1,766; (d) $571, $1,526; (e) $639, $3,071; (a) $606, $7,587 | base p16, same measures | 286.54, 1224.41; 2276.95, 1765.85; 571.36, 1526.44; 638.60, 3070.66; 605.60, 7587.36 | MATCH |
| 175 | five-seat campaign, forward basis | manifest `parameters.seats` | 5 | MATCH |
| 176-178 | P-16 openings: 1.83 at 12, 0.61 at 36, 0.42 at 52 | `bar`, p16, `forward|best_place|N=..|target=500` | 1.829936, 0.609979, 0.422293 | MATCH |
| 179 | capped by about 50 to 78 openings a year | same rows at N = 104 / 250, the `n` column | 52.20 (records), 77.55 (forward) | MATCH |
| 180-184 | every trade: 6.88 at 12, 2.29 at 36, 1.59 at 52, 0.79 at 104, 0.33 at 250 | `bar`, p16, `forward|every_trade|N=..|target=500` | 6.880193, 2.293398, 1.587737, 0.793868, 0.330249 | MATCH |

### Section 3 -- the families and the levers

| # | handoff | file, filter | my value | status |
|---|---|---|---|---|
| 185 | P-14's judged P 0.719 | each family file, `judged`, measure P, `reference_value` | 0.719328 (the same in all nine) | MATCH |
| 186-194 | picks' judged P: 0.654, 0.618, 0.668, 0.670, 0.621, 0.001, 0.482, 0.514, 0.683 | `judged`, measure P, `value`: `u_budget` budget15; `u_entry` pause1; `u_seats` seats3; `u_hours` us25; `u_firms` l1_day0; `u_consistency` cons_cap1of3; `u_plan` flat1000_cons; `u_limit` flat1500_cons; `u_resolve` resolve3_p14 | 0.654342, 0.617927, 0.667787, 0.670028, 0.621289, 0.000560, 0.482353, 0.513725, 0.682913; every verdict CLOSED at (3)(i) | MATCH |
| 195 | level 0.05 / (k (k+1)) | each manifest's `k` and `level` | k 1..9: 0.025 ... 0.000556 | MATCH |
| 196-197 | 18 to 41 % less back per fee dollar | `u_size_fit.csv`, `rule`, bound, `ratio_to_50k` | P-14: 0.8248 (100K), 0.5944 (150K); P-16: 0.8199, 0.6573, i.e. 17.5 % to 40.6 % less | MATCH |
| 198-199 | 76 cells in nine families | `u_resolve.csv` manifest `program_cells`, `program_by_family`; the sum of the nine `variant_count`s | 76; 9 families; 8+14+8+6+18+4+12+2+4 = 76 | MATCH |
| 200 | hedge pairs under a fifth of signals | `u_firms.csv` `cell`, `deal.share_dealt_signals_paired` | 0.012 to 0.2026 (max `l5_day0_hedged`) | **DIFFERS** (marginally; NOTE) |
| 201 | 136 strategies ... (D-558) | D-558; D-550 / D-553 | 136 in D-550/D-553; D-558 is about 13 | **DIFFERS** (citation scope; NOTE) |
| 202 | rows D-580, D-592, D-275, D-423, D-616, D-617, D-655 as described (3.2) | the decision rows | as described | MATCH (qualitative) |
| 203 | about 2 % power on six years (3.3, "the operator") | no file | -- | **NO SOURCE** |
| 204 | closure at request unverified (3.3) | rules.yaml `xfa_closure_at_request` status | `unverified_human_input_required` | MATCH |
| 205 | QuantConnect's free NQ/ES from 2009 (3.4) | no file | -- | **NO SOURCE** (an external fact, not a result) |

Section 4's numbers (block 21, 40 of 50 coin sequences, 5/21/63 blocks, 0.05 / (k (k+1))) are protocol parameters. They
agree with the manifests (`u_budget.csv` `coin_guard`: 50 sequences, `wins_needed` 40; bootstrap block 63) and are
not counted as figures.

---

## 3. Decision-row spot-checks (41 Stage 2 rows, 2 propsim rows)

All 62 D-ids the handoff cites exist in `vendor/stage2/DECISIONS.md` (only D-118 has two rows, and it is not cited).

| row | the handoff attributes | the row says | verdict |
|---|---|---|---|
| D-532 | P-15 PASS at 0.05/403 | the same, clean checkout 8f9644f | holds |
| D-547 | P-16 PASS at 0.05/414 | the same, clean checkout b7e6077 | holds |
| D-628 | the margin for a user is inside the noise | "R\* = P-14 is ... not a separated lead"; months 2 and 3 level within intervals | holds |
| D-527 | the 12.5-point stop loses to costs | the 12.5-point cells clear the kill line far below P-14; only US hours killed | **overstated** |
| D-423 | fixed 20-point brackets lose | P-07 FAILS; the 20-point bracket's costs make the net edge negative | holds |
| D-542 | 37.5 points best; 50 does not resolve | the same | holds |
| D-598 | 40 points worse | 40 grows less; 43.75 and 47.5 fail resolution; 37.5 stays best | holds |
| D-266 | at least 5 minutes of latency | L = 5 minutes; the verdict at L | holds |
| D-429 | one position at a time, 5 minutes flat | the strict rule, the five-minute gap | holds |
| D-212 | at most 5 % to the flatten; no time stops | **2 %** (amended later); no time stops; also holds the 90/90 rule | **number from a later row** |
| D-308 | the 90/90 realised-risk rule | raises D-212 (2)'s flatten ceiling from 2 % to 5 %; no realised-risk rule | **wrong row** |
| D-525 | BLS 07:35 and FOMC rules | re-declares family RC as a coin re-entering when flat; neither rule in its text | **does not hold it** (D-533 does) |
| D-533 | BLS 07:35 and FOMC rules | "no entry ... before 07:35 CT"; FOMC days as declared | holds |
| D-157 | each account its own trades | rotation; copying is not a candidate layout | holds |
| D-154 | supply | the minimum setups a day derived from the contract; no "five a session" | partial |
| D-452 | supply targets | the rescoping (contract shape; executions over win rate); no numbers | partial |
| D-558 | 136 strategies' gains are schedules | 13 surviving strategies' gains are schedules; 136 is D-550/D-553 | partial |
| D-580 | the follow-momentum lift fails the span guard | the same | holds |
| D-592 | the rule that passed at no delay dies at 5 minutes | S3's candidate fails at L = 5 | holds |
| D-275 | ORB5 closed | killed by all four kill lines | holds |
| D-616 | P&F closed | S4: no (rule, sign) survives | holds |
| D-617 | P&F (natural bracket) closed | loses money per trade at the only surviving box | holds |
| D-655 | Consistency beats Standard at equal size; the flat plan pays sooner but less | "with a plan of equal days the Consistency rule is the better rule"; "pay too little" | holds |
| D-665 | V1: P-16 order-independent, FV3-C not | the same, with FV3-C reaching zero inside B2 at block 21 | holds |
| D-651 | firms family closed; hedged cells hypothetical | the same | holds |
| D-648 | Consistency family closed | the same | holds |
| D-664 | resolving crippled accounts ends more than it rescues | "the table's small trades ... recover enough accounts to be worth the seat" | holds |
| D-652 | U2's funded-life reading | the same | holds |
| D-668 | U5 value map declared | the same | holds |
| D-666 | U4 size fit declared | the same | holds |
| D-623 | larger sizes verified; lock balance unstated | the same | holds |
| D-645 | rules applied | the rules patch applied; the stop band regenerated (explains its dirty manifest) | holds |
| D-561 | Lucid verified except fees | 28 of 32 rows match; 4 fees unverifiable | holds |
| D-575 | Lucid priced except funded monthly and payout fees | those charged at zero, labelled upper bound | holds |
| D-656 / D-657 | U3 declared / read | the same | holds |
| D-620 / D-621 | program U, its rule and budget | the same | holds |
| D-145 | three conduct tiers | the same | holds |
| D-155 | the eight-step protocol | the same | holds |
| D-663 | V1 declared | the same | holds |
| propsim D-08 | 16/49 | "P(pass) = 16/49 exact" | holds |
| propsim D-47 | the contract ceilings | the research criterion e at least 0.10, bound at least 0.05 | **wrong row** (D-02, D-15) |

---

## 4. Manifest checks

- **sha256:** every result file in `vendor/stage2/results/` was hashed with `hashlib`. **33 of 33 equal** their
  manifest's `sha256`, and every manifest's `rows` equals the file's row count. The two `*_policies.json` files have
  no manifest of their own; `u_value_map.csv`'s manifest pins `state_policy_v12_noclose_policies.json`, and it
  matches.
- **Cross-references:** every sha256 a manifest records for another file present in the snapshot (the `references`,
  `read_files_sha256` and `provenance.sources` maps) matches that file. That covers `user_drivers.csv` to its 9
  present sources, the family files to the gate files and `user_journey.csv`, and `u_value_map.csv` to 9 files.
- **Absent inputs:** `user_scoreboard.csv` (a source of `user_drivers.csv`), the `*_gate_slices.csv` files,
  `customer_journey.csv`, `rc150_table_screen.csv` and `rc_s100_all_gate_paths.csv` are not in the snapshot. The cited
  outputs can be re-read, but not re-derived from their own inputs.
- **Dirty trees:** `stop_band.csv` (`git_commit` `f00738a...-dirty`, `git_dirty` true, 2026-11-15T00:53Z) and
  `scoreboard.csv` (`git_dirty` true). Every other cited file is `git_dirty: false`.
- **Exploratory labels:** every U file and V1 file is `exploratory: true` with `prereg_id` null. The gate files carry
  P-14, P-15 and P-16. This is consistent with the handoff's "exploratory readings".

## 5. This repository's documents (typed result numbers)

- **`CHARTER.md`:** no result number typed. Its claims ("pays back per fee dollar ... moves P"; "first quarter is
  mostly the day they start"; "a won trade is worth most on the funded account's opening trade") are qualitative and
  cite their files. All three re-read true. Line 84 carries the D-308 mis-citation (MINOR 1).
- **`DECISIONS.md` E-001 to E-004:** no result number typed. The numbers there are parameters, seeds, hashes, counts
  of files or families, kill-line thresholds and the k/level arithmetic.
  - E-003 (c) carries D-527's overstated reading, and E-003 cites D-308 for K3 (MINOR 1, 2).
  - E-004 records "identity HOLDS" from a console run with no result file. That is a check outcome, not a number, but
    nothing on disk traces it.
  - The file now also holds E-005, outside this track's range. Its one figure, about 1.7 GB of free memory, is a
    machine fact.
- **`prereg/F-01_resting_order_level_atlas.md`:** no result number typed ("both above the cost floor" compares
  without typing it).
  - It carries D-527 and D-308 as above.
  - It describes R = 1 as the table's ask "on later funded and paid trades". On paid accounts, 1.5R is about as common
    as 1R for P-14 (`table_leaves`: paid $500 1.5R 0.194, paid $250 1R 0.192), so this is a simplification (NOTE).

## 6. What I could not verify, and why

- **The evaluation's realised risk (handoff 2.5):** no snapshot file holds it, and settling it needs the engine's
  trade records, which this track does not run.
- **The supply targets (2.6):** in no cited row. Their stated origin, `docs/HANDOFF_RESET_2026-10-29.md`, is not in
  the snapshot, and it is not cited by the handoff, so the live Stage 2 repository was not read for it.
- **"About 2 % power" (3.3) and "QuantConnect ... from 2009" (3.4):** no file is cited.
- **The firm rules:** checked against `rules.yaml` only, not re-read on the help centre (no web access in this track).
- **The U files' derivation from their inputs:** the inputs are absent (section 4); only the cited outputs were
  re-read.
- **Decision rows not individually read:** D-629, D-630, D-634, D-635, D-637, D-638, D-639, D-642, D-643, D-644,
  D-646, D-653, D-654, D-658, D-659, D-661, D-662, D-667 and D-669. All exist, and their families' verdicts were
  read from the files.
- **Not checked:** the Campaign Studio (SD-95) and the literature review's content. Its file exists.
