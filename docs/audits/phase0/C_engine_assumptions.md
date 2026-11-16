# Phase 0 audit, track C: the engine's assumptions that carry the money

Track C of the Phase 0 audit, 2026-11-15. Independent and read-only. Subject: Stage 2's engine as vendored at
`vendor/stage2/` (snapshot f1b42e2), its configuration, its decision log and the 34 vendored result files.

**What was done.** I read code, configuration, decision rows and result CSVs. I ran no engine, campaign or simulation,
and I read nothing under `vendor/stage2/data/`. I made two scratch readings of result CSVs (pandas, one process):
(1) I extracted the rows of the three registered gate files; (2) for finding C-1 I re-read U1's start rows under
stated payout-denial models. Reading (2) uses no random draws: it is an exact binomial probability and a direct
haircut. Its figures are labelled **AUDIT ESTIMATE** wherever they appear. They are not results and have no manifest,
so no document may quote them as results. The formula is given in section 1, so anyone can re-derive them from the
file.

**How numbers are cited.** Each figure gives its file, its section, its filter and its column. Abbreviations:
- **G14**, **G15**, **G16**: `vendor/stage2/results/a3_brk30_cb20_gate.csv` (P-14), `rc_s100_all_gate.csv` (P-15),
  `rc_s150_all_gate.csv` (P-16).
- **bound row**: section `gate`, shift `lower_bound`, enforcement_p 0.
- **point row**: section `gate`, shift `point`, enforcement_p 0.
- **growth**: the column `pf_growth_on_base_p50`, growth on the required bankroll, the gate's measure (D-312).
- The gate files run 500 paths over 504 sessions (column `paths`, `horizon_days`).
- **UJ**: `vendor/stage2/results/user_journey.csv`.
- **UB**: `vendor/stage2/results/u_budget.csv`.
- Decision rows are Stage 2's (D-nnn).

---

## Summary: findings by severity

### CHANGES-A-CONCLUSION

**C-1. Every user measure is read with all three firm responses switched off.** The user measures are P, S1, S3c and
the rest. The three responses are the Responsible Trading Program placement (D-289), payout denial (D-234) and the
Focused Trader Program. The designs show the patterns those rules name on nearly every payout. The gate reports what
the responses cost, beside its verdict. The user scorecard reports none of it, and the user scorecard is this
repository's objective.

How often the patterns occur, on the bound rows:
- 98.7-99.9 % of payouts are "exposed" (they come from a campaign with two or more MLL breaches in 21 days).
- Two or more MLL breaches fall on the same day on 85-107 of 504 sessions.
- About 380-430 evaluation purchases are made per 504 sessions.

What the responses cost on the gate:
- With the placement on, all three designs lose money. Growth at the bound is -0.39, -0.54 and -0.46.
- At 50 % denial, P-14 and P-15 fail.
- Under the Focused Trader models, payouts per path fall by about three quarters, though growth stays positive.

On the user measure, read from UJ's start rows (AUDIT ESTIMATE):
- P-14's P falls from 0.671 to about 0.50-0.54 at 25 % denial and to about 0.27-0.34 at 50 %.
- With the placement on, P is inferred to be near zero. P-14's table on the Consistency path has P = 0.000 (UB's
  sister file `u_consistency.csv`, cell `cons_p14`).

"The money comes from contract shape" is true inside the engine: the zero-edge twins grow at least as much as the
strategies. But it is conditional. The shape pays only if the firm pays a pattern that its verified pages call
"Account Stacking" and "Excessive purchases of Trading Combines". It must be stated with that condition, and the user
measures must carry the denial, placement and Focused Trader readings beside them (section 1, 2).

### MATERIAL

**M-1. "P-14 is the row to beat" is not robust to the denial level or to the measure.**
- At 50 % per-payout denial, P-16's P exceeds P-14's (AUDIT ESTIMATE: 0.311 against 0.269 under the haircut; 0.324
  against 0.297 under thinning).
- On the gate's growth, P-16 is ahead of P-14 at every denial level and under every Focused Trader model that binds.
- At 50 % denial P-14 fails and P-16 passes.
- P-14's lead on P was already inside the noise at 0 % (D-628).
- None of this is reported beside P (section 1).

**M-2. The engine's denial model is milder in its tail than the verified terms.**
- In the engine, each exposed payout is denied by its own coin, and only that account is closed
  (`lockstep.py:1926-1936`, `645-660`).
- The verified terms are heavier and correlated:
  - Terms of Use s.27 forfeits withdrawals "from any other account".
  - The Focused Trader Corrective Path denies "any pending payouts".
  - Every payout is reviewed against Prohibited Trading Strategies (`config/rules.yaml` `prohibited_conduct`,
    `focused_trader_program`, `payout_after_request_survives_mll_breach`).
- The exposure trigger saturates (more than 98.7 % of payouts are exposed). So the 10/25/50 % ladder is in effect a
  uniform haircut, not the all-or-nothing event per trader that the pages describe (section 1).

**M-3. P-14, the row to beat, has none of D-663's stress readings.**
- The missing readings are block-resampled days, real-order against resampled bankroll, the break-even shift margin,
  missed trades and sessions, and the bound's coverage. P-14 also has no slippage stress.
- They were run on P-16 and FV3-C only.
- FV3-C, the other signal-driven design, loses about a third of its growth at the bound under 63-session blocks.
- The gate floor (iii) that every challenger must clear is read on independent days (section 6).

### MINOR

- **m-1. Seat refill.** The same-evening seat refill (`seat_frees = same_evening` on all three gates) rests on an
  unverified ledger row, `xfa_seat_frees_at`. Its direction is optimistic, by at most one session for each funded
  ending (section 7).
- **m-2. Stop fills and slippage.**
  - Stops fill at the stop price plus one tick. Nothing models a bar that opens through the stop, although
    `config/fills.yaml` declares `gap_through_stop: next_price`.
  - Slippage is assumed, not measured (D-95).
  - Per tick, P-14's 12.5-point rung is three times as sensitive as P-16's 37.5-point rung, and only P-16 was stressed
    (section 3).
- **m-3. The state table** (all three designs) was solved once, at e = -0.05, under an independent binary-trade model.
  It is then evaluated frozen on the empirical trades. That evaluation is not itself optimistic. But R*'s level is
  in-sample: P-14 is rank 1 of a screen run on data that includes the judged block (section 4).
- **m-4. Breach bookkeeping.**
  - The conduct tallies count MLL breaches but not policy abandons just above the floor.
  - The bound's uniform shift turns stop-outs sized to the full room into breaches. P-16 has 9.7 multi-breach days at
    the point and 85.3 at the bound; it abandons 255 evaluations at the point and 15 at the bound.
  - The placement-on reading swings with this: P-16's growth is -0.03 at the point and -0.46 at the bound
    (section 2, 7).
- **m-5. The value map** that F-01 uses to value lift (`u_value_map.csv`) values a table re-solved at each R's bound
  under the solver's model. That is not the table P-14 trades, and it is not the campaign (section 4).
- **m-6. FV3's breakeven move.** The stop moves to the entry at the next session open, and this rule sits inside every
  P-14, P-15 and P-16 trade. Article 10305426 names "auto-breakeven to take advantage of favorable SIM fills" among
  the prohibited strategies. It is probably not that practice: it is a manual move at a session open, booked with a
  tick of cost. But this repository declares it nowhere (section 8).

### NOTE

- **n-1. "The 1:1 lock assumption"** is the label `lock_assumed_1to1`. It sits on the $100K and $150K rows of the
  closed account-size fit and nowhere else. At $50K the engine's trail and lock match the verified pages exactly
  (section 5).
- **n-2. Seat cap and one position.**
  - The joint cap of five accounts including evaluations (D-34) is stricter than the firm (Combines unlimited).
  - The strict rule of one position at a time (D-429) is stricter than the firm's rule against opposite positions.
  - The activation fee is charged at activation, which matches 8284217.
  - The hold queue cannot be reached by construction (section 7).
- **n-3. Exit rules are conservative.** On a bar where both are touched, the stop wins; a target needs a trade-through;
  the flatten takes the worst of the 15:07-15:10 bars less two ticks. Unresolved trades are at most 0.4 % of P-14's
  trades at 3R (section 3).
- **n-4. The replay's bankroll never binds** (`propedge/research/user_journey.py:11-12`). P counts a user who would have
  run out of cash as still buying. S1 and the quit rules Q1 and Q2 are reported beside it (section 8).
- **n-5. `is_gate_row` is also True on other sections.** It is True on the rows of sections `placement_on`,
  `gf15b_twin`, `check_years` and `gate_at_ledger_n`, besides `gate`. Read the gate files by section, never by that
  flag alone (section 2).
- **n-6. The five accounts share the day but not a copied trade.** No trade is copied and no two positions overlap
  (D-157, D-429). Their joint breaches matter mainly as conduct exposure, not as P&L correlation (section 7).

---

## 1. Payout denial at 0 % in the verdict (tier 3, D-234)

**(a) Where it lives and which rows adopted it.**

The gate:
- `propedge/campaign/gate.py:27-28`: `GATE_ENFORCEMENT_P = 0.0`, `ENFORCEMENT_LEVELS = (0.0, 0.10, 0.25, 0.50)`.
- `gate.py:351`: the gate row is the bound row at 0 %.

The mechanism (`propedge/campaign/lockstep.py`):
- `ConductModel` (`lockstep.py:97-158`): `pattern_breaches = 2`, `pattern_window_days = 21`.
- The exposure test and one uniform draw per exposed payout are at `lockstep.py:1926-1936`.
- `FundedAccount.deny_last_payout` (`lockstep.py:645-660`) undoes the payout and closes that one account.

Adoption:
- D-234 sets the rule; it replaced D-145's 25 %. SUCCESS_CRITERIA section 4 reports 10, 25 and 50 % and the
  break-even denial beside the verdict.
- The user journey replay hard-codes 0 %: `scripts/customer_slices.py:232`
  `ConductModel(rtp=..., enforcement_p=0.0)`; `scripts/user_journey.py:369` filters `enforcement_p == 0`.

**(b) What would break the conclusion.**

The verified conduct pages name this design's pattern.

Account Stacking (10305426):
- "Repeatedly trading aggressively, hitting the Maximum Loss Limit (MLL) in one account, then switching to another
  account and repeating. The goal is to run high-risk attempts until a large win occurs."

Prohibited Conduct (10296582):
- It lists "Excessive purchases of Trading Combines or Resets".
- Its responses include "Delay or denial of a Payout request" and "Permanent account closure".
- Terms of Use s.27: "you will not be entitled to receive any withdrawals from any other account".

The payout review (8284233) checks "Prohibited Trading Strategies" before every payout. All of these are quoted in
`config/rules.yaml` (`prohibited_trading_strategies`, `prohibited_conduct`,
`payout_after_request_survives_mll_breach`).

The registered designs match those words:

| reading (bound row unless stated) | P-14 (G14) | P-15 (G15) | P-16 (G16) |
|---|---|---|---|
| `share_payouts_exposed` | 0.9983 | 0.9986 | 0.9869 |
| `mean_same_day_multi_breach_days` (of 504 sessions) | 102.4 | 106.5 | 85.3 |
| `mean_max_mll_breaches_21d` | 24.3 | 24.4 | 23.8 |
| `mean_combine_purchases` | 419.8 | 429.2 | 380.8 |
| `mean_accounts_funded` | 117.4 | 115.5 | 104.9 |
| `share_paid_xfa_closed` (paid funded accounts that end closed) | 0.963 | 0.971 | 0.944 |

The funded opening:
- The opening trade is the full allowance, 20 micros, at 3R (`u_xfa_day_budget.csv` section `opening_trade`, design
  p14, arm verdict, group opened: `contracts_p10` = `p50` = `p90` = 20; `policy_rr_p50` 3; `realised_risk_p50`
  $1,000).
- The table's own export flags its regime "funded $1,500 3R" as "risk $1,500 above half the $2,000 drawdown, an
  account-deciding position (Responsible Trading Program)" (`state_policy_v12_noclose.csv` section `dp`, column
  `conduct_flags`).

The denial ladder on the gate (growth at the bound, section `gate`, shift `lower_bound`):

| enforcement_p | P-14 | P-15 | P-16 |
|---|---|---|---|
| 0 | 1.456 | 1.315 | 1.500 |
| 0.10 | 1.278 | 1.097 | 1.320 |
| 0.25 | 0.849 | 0.700 | 0.940 |
| 0.50 | **-0.138** | **-0.232** | 0.076 |
| break-even denial (`pf_break_even_denial_p50`, bound row) | 0.610 | 0.564 | 0.673 |

The verdict rows of G14, G15 and G16 (section `verdict`, `growth_bound_denial_10/25/50`) carry the same figures.

On the user measure no file holds a reading.

**AUDIT ESTIMATE.** I computed it from UJ section `start`, config p14 / p15 / p16, arm `verdict`, on starts with
`observed` ≥ 63 (1,629 starts each). Script: scratchpad `phase0_C/p_denial.py`, not kept in the repository.
- **The identity first.** P re-derives exactly as 0.6712 / 0.6421 / 0.6200, matching UB section `cell`, block `all`,
  measure P.
- **Haircut.** Every payout received by month k is cut by p; a start is ahead if (1-p)(net_k + fees_k) - fees_k > 0.
- **Thinning.** Each payout received by month k (counted from `pay_days` ≤ 21k) is denied with probability p,
  independently. Within a month a start's payouts are taken as equal-sized, because the file holds only their count
  and their total. The probability of being ahead is P(Bin(n_k, 1-p) > fees_k / payout size), computed exactly.
- **All or nothing.** The firm denies every payout of the user with probability p, so P becomes (1-p) P.
- Neither haircut nor thinning includes the closure a denial causes or the purchases after it. Both are therefore
  upper bounds on P under per-payout denial.

| p | P-14 haircut / thinning / all-or-nothing | P-15 | P-16 |
|---|---|---|---|
| 0 | 0.671 / 0.671 / 0.671 | 0.642 / 0.642 / 0.642 | 0.620 / 0.620 / 0.620 |
| 0.10 | 0.634 / 0.618 / 0.604 | 0.596 / 0.585 / 0.578 | 0.568 / 0.577 / 0.558 |
| 0.25 | 0.542 / 0.517 / 0.503 | 0.493 / 0.481 / 0.482 | 0.511 / 0.498 / 0.465 |
| 0.50 | 0.269 / 0.297 / 0.336 | 0.234 / 0.271 / 0.321 | **0.311 / 0.324** / 0.310 |

What this means:
- Denial moves P by about 0.13-0.15 for every 25 % of denial. That is more than twice the whole spread between the
  three registered designs at 0 % (0.671 against 0.620, UB section `cell`, block all, measure P).
- Under per-payout denial, P-16 overtakes P-14 somewhere between 25 % and 50 %.
- Under the all-or-nothing reading the order does not change, but P is scaled by the chance the firm honours the
  pattern.
- The level, not the design, is what the 0 % rule carries.

**(c) Reported today?**
- On the gate: yes. Every verdict row carries the ladder and the break-even denial.
- On the user measures: no. UJ, UB and `user_drivers.csv` contain no denial reading; their identity rows state "at
  0 %".

**How to report it in the new repository:**
- Beside every P, S1, S3a, S3c and S5a, report the per-payout ladder (10, 25, 50 %) using the engine's own model run
  through the replay. This needs an adapter that passes `enforcement_p`; the vendored replay call hard-codes 0.
- Report the all-or-nothing reading per trader beside it, as the s.27 reading.
- Report each design's own break-even denial on P (the p at which P falls to R*'s P, or to 0.5).
- Add a sentence in CHARTER section 1: the contract shape pays only while the firm pays this pattern.
- Do not change the verdict rule (it is the operator's, D-234). Record the condition under a decision row.

## 2. The Responsible Trading Program's placement off in the base case (D-289)

**(a) Where it lives and which rows adopted it.**

The code:
- `gate.py:136`: the default is `rtp=True`. A scorer passes its declared value, and every row records `rtp`.
- The triggers and consequences are `ConductModel` (`lockstep.py:97-158`) and its use at `lockstep.py:1937-...`. On
  the first trigger day, under the strictest reading (`rtp_warnings = 0`), placement starts the next session and lasts
  to the end of the path.
- After placement, every new evaluation and every new funded account gets a $1,000 daily loss limit, and every
  funded account from an evaluation bought or reset after placement is Consistency-only (13620045, verified).
- The trigger "multiple accounts hit the MLL in one day" is counted as two or more accounts of either kind in one
  engine day (`lockstep.py:1914-1919`). That is a declared assumption: the page defines no count (`rules.yaml`
  `responsible_trading_program`, "TRIGGER 1 IS NOT DEFINED").

Adoption:
- D-289 is the operator's rule. SUCCESS_CRITERIA section 4 reports the placement-on reading beside the verdict.
- The user journey: "the placement off" appears in UJ section `identity` and in UB's and `u_xfa_day_budget.csv`'s
  identity rows.

**(b) What would break the conclusion.**

The gate's placement-on rows (section `placement_on`, enforcement_p 0):

| reading | P-14 point / bound | P-15 point / bound | P-16 point / bound |
|---|---|---|---|
| growth | -0.279 / **-0.388** | -0.465 / **-0.535** | -0.035 / **-0.459** |
| `mean_payouts_per_path` (base case, bound row) | 4.46 / 3.45 (81.87) | 3.15 / 2.73 (73.34) | 10.37 / 2.12 (75.14) |
| `share_paths_rtp_placed` | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 |
| `pf_required_p90` | $14,282 / $16,450 | $18,717 / $19,115 | $10,935 / $14,172 |

The same bound figures are in each verdict row's `growth_placement_on`.

What this means:
- Every path is placed. Every design then loses money on the gate's own measure.
- No user-measure reading exists. The nearest one on file is the Consistency path chosen for every funded account:
  `u_consistency.csv` section `cell`, arm verdict, block all, measure P gives `cons_p14` 0.000 and `cons` (P-16)
  0.000; S3c is 0.000 and 0.0007. That reading has no daily loss limit, and evaluations bought before placement could
  still activate on the Standard path. So it is a near analogue, not a measurement.
- **Reasoned estimate (labelled):** with the placement on, P falls to near zero for every design.

Two qualifications:
- **The engine's reading is the strictest one.** It places the trader the day after a single trigger day. The page
  says warnings "will often be sent out first" and placement follows a Risk Team review (`rules.yaml`
  `responsible_trading_program`, "NEW 4"). No result file holds a softer reading (`rtp_warnings` above 0, D-220).
- **The trigger count is sensitive to how an ending is booked** (finding m-4). On P-16 the point row has 9.7
  multi-breach days and the bound row 85.3 (G16 point and bound rows, `mean_same_day_multi_breach_days`). The
  placement-on point and bound growths differ by 0.42 for the same reason.

**(c) Reported today?**
- On the gate: yes (`placement_on` rows; verdict row `growth_placement_on`).
- On the user measures: no.

**How to report it in the new repository:**
- Beside every user reading, report the placement-on reading through the replay, with the adapter passing
  `rtp=True`.
- Report it at `rtp_warnings` 0 (the strictest reading) and at a softer declared reading.
- Report the day of placement in each start, as a distribution.
- Name the placement in CHARTER section 4 as a verified consequence that the base case switches off by the operator's
  rule.
- n-5: `is_gate_row` is True on the bound row of section `placement_on` in G14, G15 and G16 (and on `gf15b_twin`,
  `check_years` and `gate_at_ledger_n`). This repository's readers must select by section.

**The Focused Trader Program (10551016, verified)** belongs with this assumption.
- Its Slowdown and Corrective paths name "Excessive Resets and Trading Combine purchases", "Activating and losing many
  Express Funded Accounts in a short period of time" and "Excessive recycling of Trading Combines® or XFAs". The page
  publishes no thresholds.
- The gate files' `ftp` section sweeps declared thresholds.
- At the bound, P-14 is placed on day 2 at "slowdown purchases ≥ 10/21d" and on day 10 at "≥ 20/21d"
  (`ftp_first_placed_day_p50`). Payouts per path fall from 81.87 to 18.74 at the latter.
- Growth stays positive: the minimum is 0.345 (P-14), 0.479 (P-15) and 0.685 (P-16) (verdict rows,
  `ftp_growth_bound_min`).
- The budget of 20 evaluation purchases per 21 sessions reaches its own limit on every path
  (`tier3_mean_max_combine_purchases_21d` = 20.0 on all three).
- A user placed in their first fortnight loses most of months 1 to 3, and that is exactly the window P measures.
  No user reading exists.

## 3. Modelled fills: settlement, same-bar ties, costs and slippage, the 15:10 flatten

**(a) Where it lives and which rows adopted it.**

- **Settlement (D-156).** All three gates settle `mae` (G14, G15, G16, column `settlement`).
  - The engine clips at the floor (`lockstep.py:475-478`, `729-732`) after the draw has settled against the room.
  - The trade's MAE comes from the rung walk (`propedge/research/fv3_rung_walk.py` docstring): the stop on a stop,
    the running maximum to the exit bar on a target, the whole walk on an open trade.
  - `legacy` (pre-D-156, above stage one's ceiling) is reproduction-only. `pessimistic` is not read for these designs.
- **Bracket.** `propedge/outcomes/fv3_core.py:174-185`.
  - A target must be traded through.
  - A stop needs only to be reached. On a bar where both happen, the stop wins.
  - A stop is booked at the stop distance (`fv3_core.py:181`), however far the bar went past it.
- **Costs.**
  - Ticks by exit kind, from `fv3_rung_walk.py:50-51` `EXIT_TICKS`: 1 on a stop or a breakeven, 0 at a target,
    2 on the flatten.
  - One tick at entry (`config/atlas_a3.yaml:29` `slip_ticks: 1`).
  - The fee at the contracts held: as many NQ minis as fit, the rest MNQ (`propedge/campaign/sizing.py:180-187`,
    `792-798`; D-324; `atlas_a3.yaml:102-105` "fidelity.costs per_trade_at_size").
  - Cost in R: `resolved_coin.py:191`, `scripts/atlas_a3.py:285-288`.
- **Fee and slippage sources.**
  - Round-turn fees are the published schedule: MNQ $1.22, NQ $3.78 (`config/fills.yaml:58-67`, article 8284213,
    verified). They are not measured fills.
  - Slippage is ASSUMED (`fills.yaml:188-229`, D-95). Nothing is measured.
- **Flatten.** The worst of the bars ending 15:07 to 15:10 CT, less 2 ticks (`fv3_rung_walk.py` docstring).

**(b) What would break the conclusion.**

- **Settlement and ties** are exact or conservative at 1-minute resolution. Stop-first and trade-through bias against
  the strategy. The MAE on a target includes the exit bar's adverse extreme.
- **Gap-through.** `fills.yaml:208-211` declares `next_price` ("realistic") and calls `exact` optimistic. The walk books
  the stop at the stop. That disagrees with the repository's own declared fill model, and it is optimistic, but only
  when a 1-minute bar opens or trades fast through the stop.
  - The release minute is cut on BLS days: no entry before 07:35 CT (D-533). That cut exists because the audit of the
    registered P-15 found its release-minute entries at "most of the maximum size", with "its one-tick fill
    optimistic".
  - FOMC days are excluded.
  - What remains is ordinary fast tape.
  - **Reasoned estimate (labelled):** small for the money, because a stop loss is a $1,000-1,500 event with 20-30
    micros and a few extra ticks cost tens of dollars. But it is not measured anywhere.
- **Slippage level.**
  - P-16's growth at the bound holds at every declared slippage level (D-585, `p16_slip_stress.csv`; that file is not
    vendored).
  - FV3-C's holds too (`v1_validation_c2.csv`).
  - P-14 has no slippage stress in any vendored file. One extra tick a side costs 2/50 = 0.04 R on P-14's 12.5-point
    rung (50 MNQ ticks) against 2/150 = 0.013 R on P-16's rung.
  - P-16's shift curve gives the scale (`v1_validation_b2.csv` section `b2_curve`, subject S1, scheme independent).
    Growth goes from 1.440 to 1.372 at -0.02 R and to 1.231 at -0.04 R, and stays positive to -0.16 R (0.610).
  - **Reasoned estimate (labelled):** one tick a side on P-14 moves its growth by 5-15 % and P by a few points. It
    does not reverse the gate, and on R* it is inside the noise. This needs P-14's own run.
- **Contract shape against costs.** The zero-edge twins (`growth_zero_edge_twin`, verdict rows) are 1.643, 1.437 and
  1.566, against the point rows' 1.585, 1.352 and 1.544. Costs and edge move growth by less than 0.1. The money is the
  shape, as stated.
- **Flatten.** It is negligible for P-14: unresolved at 3R is 0.0038 overall and 0.0132 in the worst year (G14 section
  `resolution`, rr 3). It is conservative (2 ticks plus the worst bar). It agrees with Topstep's rule to be flat by
  3:10 PM CT (8284206, `rules.yaml` `trading_hours`).

**(c) Reported today?**
- Settlement is on every gate row.
- Slippage stress exists for P-16 and FV3-C, not for P-14.
- Gap-through is reported nowhere.

**How to report it in the new repository:**
- Report the fill profile's status (`ASSUMED`) beside every result.
- Run D-663 C2's two families on P-14 before it is used as R* in a judged comparison (proposal E2).
- Measure the stop bar's overshoot from the walk profiles (E4).
- F-01, the resting orders, must declare its own limit-fill rule. Its trade-through-by-a-tick rule is already the
  conservative one.

## 4. The state table solved at one edge and then evaluated

**(a) Where it lives and which rows adopted it.**

- **The same table everywhere.** All three registered designs trade `state_dp_e-0.050_lamstar_noclose` (G14, G15, G16
  column `risk_policy`; verdict rows `risk_policy_id`). That is v12's table with the funded abandon off (D-502).
- **The solve** (`config/state_policy_v12.yaml:12-14`, `propedge/campaign/state_policy.py`):
  - Stage one's binary process: p = (1+e)/(1+R), the same e at every R, trades independent.
  - Solved on the grid `edges: [-0.05, -0.025, 0.0, 0.025, 0.05, 0.10]` (D-290).
  - The table is the one at e = -0.050: `state_policy_v12_noclose.csv` section `rent_round`, table noclose, edge -0.05,
    converged at round 2, `p_pass` 0.2395.
  - It was solved for FV3-C's rungs (12.5 and 25 points, which are also P-14's), with rung shares and availability
    from FV3's 2020-2021 records (`state_policy_v12.yaml` `rungs`).
- **The oracles hold** (same file, section `oracle`): `p_pass_1to1_1500` 0.326531 = 16/49; maximum P(pass) 0.326531 ≤
  0.327131; maximum gross payouts $1,230.82 ≤ $2,000.
- **Evaluation.** The table is evaluated frozen. The campaign runs it on the empirical trades at the point arm (mean R
  used: -0.0237, -0.0278, -0.0212 on G14, G15, G16 point rows, column `mean_r_used`) and at the bound arm (-0.0847,
  -0.0529, -0.0604). The 0.05/N verdict arm reads -0.1252, -0.0859, -0.1046 (section `gate_at_ledger_n`).
- **The value map** (`u_value_map.csv`, the U5 source this repository's F-01 uses to value lift) is a different
  solve. Section `identity` row `d667_table_on_file` shows the file can reproduce the traded table. But section
  `solve` reads D-667's "$50K bound solve" at each R's registered bound (P-14 `lambda_star` 34.46 against the traded
  table's rent of 30.12). `exported_table_sha256` ad6e0260... is not the registered table's tree.

**(b) Is it a source of optimism?** I see four channels.

1. **Evaluating a policy optimised for another edge: not optimistic.**
   - The campaign evaluates a fixed policy faithfully. A policy solved for e = -0.05 and run where the trades' edge is
     lower (the bound arm) is at most suboptimal there, which biases growth down, not up.
   - D-563 re-solved the table for P-16's own trades and found growth "only a little more at the bound", inside its
     0.05 line.
   - B2 reads the margin "for the table as frozen" (D-663). So the mismatch is a conservative approximation.
   - One caveat: e = -0.05 is the lowest edge on the grid, so the table cannot be re-solved at P-14's bound arm. It sits
     between the arms rather than at either.
2. **The solver model against the trades' R structure.**
   - P-14's empirical edge rises with R. At the point it is -0.0358 at 0.25 R and -0.0028 at 3 R (G14 section `edge`,
     column `e`).
   - The table's funded opening is 3R. The uniform-e model neither knows nor exploits this. The campaign reads the
     real structure, and the bound arm shifts each R by its own gap (`gate.py:31-49`).
   - P-14's era test flags 2.5-3 R, where the later era is better (G14 section `eras`, `flagged` True at rr 2.5, 2.75,
     3.0). The bound uses "the lower era's" (verdict row `bounds_read`), so the high-R edge in the bound arm is not
     flattered.
   - No optimism found.
3. **The data it was chosen on: optimistic for R*'s level, conservative for any challenger.**
   - The table (versions v3 to v12, the leaves, the tie-breaks, the no-closure leaf) was developed through campaign
     readings on the same 2020-2026-07-16 development data.
   - P-14's signal is rank 1 of A3's screen on a window ending 2026-07-16 (`config/atlas_a3.yaml:18-20`). That window
     includes the judged block (starts from 2024) on which CHARTER section 3 compares challengers.
   - So R*'s P (UB section `judged`) is in-sample for P-14.
   - That makes R* harder to beat: it is a conservative benchmark for selection, but it is not a promise to a user.
   - The registered verdict's 0.05/370 covers the edge's bound, not the table's selection.
4. **The value map is the solver's model, not the traded table or the campaign.** It is first-order with the table held
   fixed (section `definitions`, "first-order, the table held fixed"), and it is read at a re-solved per-R bound
   table.
   - **Reasoned estimate (labelled):** dv on the funded opening (P-14 $1,426: section `place_values`, c_funded_opening,
     `mean_dv`) is roughly right in sign and order.
   - Its use in F-01's stage B to rank a cell's dollar value is a model reading, and it must be labelled so (m-5).

**(c) Reported today?**
- The policy id is on every row, and the solve's edge appears in its name.
- That R*'s P is in-sample is not stated in CHARTER section 3.
- The value map's table is not the traded table, and that is not stated in F-01.

**How to report it in the new repository:**
- State "table frozen at e = -0.05, i.i.d. binary model" beside every result.
- Label R*'s P as in-sample.
- Label F-01's dollar values "solver model, re-solved bound table".

## 5. "The 1:1 lock assumption"

**How I identified it.** I searched the whole vendored tree for "1:1" and "lock" near each other, and for "1to1",
"lock_assumed" and "lock assumption" (code, markdown, yaml, csv; `data/` excluded). It returned exactly one label tied
to the engine:
- `lock_assumed_1to1`, on 277 rows of `results/u_size_fit.csv` (column `label`).
- `scripts/u_size_fit.py:264-265` refuses a size whose funded floor is not "the solver's 1:1 trail (start at minus the
  loss limit, lock at 0)".
- D-666 (5): "the funded lock balance of a $100K or $150K account is stated on no page (D-623) -- the solver's 1:1
  trail is applied, locking at the starting balance as at $50K".
- D-667 (4): "every larger-size figure carries `lock_assumed_1to1`".

The other hits were two "1:1" things that are not locks:
- Stage one's reference policy `s1_1to1_1500`, 16/49 (the `baselines` and `oracles` of `config/state_policy*.yaml`).
- `blusky_eval_lock`, another firm's evaluation lock, in `vendor/stage2/vendor/propfirms/results/t4_validation.csv`.

I take "the 1:1 lock assumption" to be the first. I also checked the $50K trail and lock it is copied from.

**(a) Where it lives and which rows adopted it.**

At $50K, the engine implements the verified rows exactly:
- **The evaluation.** The floor trails the end-of-day balance at B - $2,000 and locks at the starting balance
  (`lockstep.py:511-515`). 8284204: "It rises as your end-of-day balance grows"; "Once it reaches your starting
  balance, it locks permanently".
- **The funded account.**
  - The floor is F = min(0, max(F, B - 2,000)) at the close (`lockstep.py:784`), starting at -$2,000
    (`xfa_mll_start`), with breach in real time through the room and MAE settlement.
  - F = $0 after any payout (`lockstep.py:832`). 8284204: "Once your balance reaches $2,000, the MLL locks at $0
    permanently"; "After your first Payout: Your MLL is set to $0 regardless of where it was before". 8284233: "After
    each Payout: Your Maximum Loss Limit (MLL) resets to $0 permanently".
  - `RULES_LEDGER.md:233`: "MLL trails end-of-day balance; breach real-time incl. unrealised" -- matches.
- **The assumed part** is only the $100K and $150K funded lock balance (`rules.yaml` `xfa_lock_at` note:
  "NOT STATED for 100K and 150K"). The page says only "trails upward as your balance grows and locks at $0 once
  reached, same as a brand new XFA".

**(b) What would break the conclusion.**
- The 1:1 trail is the natural reading of that sentence: the MLL reaches $0 when the balance has risen by the MLL.
- The account-size family closed by a wide margin. Payouts per fee dollar at the bound, against $50K's, are 0.825
  ($100K) and 0.594 ($150K) on P-14, and 0.820 and 0.657 on P-16 (`u_size_fit.csv` section `rule`, measure
  `ratio_to_50k`). D-666 (3)'s line is 1.10.
- A lock that came later would widen the gap. A lock that came earlier contradicts "same as a brand new XFA".
- The assumption cannot reverse the size closure, and it does not touch P-14 or P-16, which are $50K designs.

**(c) Reported today?** Yes: every larger-size row carries the label.

**How to report it in the new repository:** carry the label unchanged if a size cell is ever read. Nothing more is
needed.

## 6. The outcome draw: independent days (D-663) and block-resampled days (D-665)

**(a) Where it lives and which rows adopted it.**
- **The gate.** Each path's calendar draws one historical day per calendar day, independently and with replacement
  (`shared_days.py:78-101` `SharedDayTable`). Within a day the trades are that day's real sequence, routed in time
  order (`shared_days.py:337-397`).
- **The stationary bootstrap.** `shared_days.py:104-141` `StationaryDayTable` is opt-in (`gate.py:150`, `211-215`,
  `267-273`). It is refused on the replay, and it never makes a gate row (`gate.py:362-364`).
- **The user measures** come from the as-happened replay (`shared_days.py:144-163` `ReplayTable`;
  `user_journey.py:1-6`: "No engine, no draw").
- **The bound of e** is a Student-t on 21-session block means (CLAUDE.md of Stage 2; D-11).

**(b) What independence does to each measure.**

- **The bound.** The bound does not assume independent days: its unit is a 21-session block.
  - For P-16 (`v1_validation_b1.csv` section `b1`, subject S1), the pooled bound at 0.05 is near nominal
    (`share_exceed` 0.047-0.052 across R at mean block 1).
  - The registered era rule is strongly conservative (`ratio_to_nominal` 0.03-0.06 at 0.05; 0.000 at 0.05/414).
  - P-14 was not read.
- **Gate growth and the required bankroll.**
  - P-16 does not depend on the order of days (`v1_validation_a1.csv` section `a1`, subject S1, arm verdict
    (0.05/414)). Growth is 1.440 independent, then 1.424, 1.384, 1.457 and 1.443 at mean blocks 1, 5, 21 and 63
    (`growth_se` 0.016-0.027). `pf_required_p90` runs from $3,797 to $3,648-4,148.
  - FV3-C does depend on it (subject S2, arm bound (0.05)). Growth falls 0.991 → 0.964 → 0.824 → 0.720 → 0.674 and
    `pf_required_p90` rises from $6,204 to $7,809 at 63.
  - FV3-C's break-even margin under 21-session blocks is 0.132 R, inside the declared 0.16 (`v1_validation_b2.csv`
    section `b2`, S2, stationary mean block 21, `margin`).
  - Day-level dependence for P-16 (`v1_validation_a0.csv`, S1): `day_r` lag-1 autocorrelation -0.022; `abs_day_r`
    0.113, Ljung-Box p(5) < 0.001. Size clusters; sign does not.
  - **P-14 was never read under D-663.** It is a signal design like FV3-C, with an era flag. Its gate floor and its
    resampled bankroll are therefore untested against the order of days.
- **The bankroll's tail.** For P-16, real-order starts exceed the independent draw's 90th-percentile required bankroll
  in 0.145 of 69 starts, against an expected 0.10 (`v1_validation_a2.csv` section `a2`, S1, verdict, independent,
  `share_required_above_p90`). The share is 0.116 at blocks of 5 and 21 and 0.087 at 63. The independent draw
  understates the bankroll tail a little. The starts overlap, so no interval exists (D-663).
- **The user measures.**
  - Independence does not enter P, S1 or S3c: they replay real order.
  - But they rest on one history. P's 1,629 starts (UB section `cell`, `n`) overlap. A 63-session reading has about
    1,691/63 ≈ 27 windows that do not overlap.
  - D-628 recorded that P-14's lead "is never to be reported as P-14 being ahead over the first three months".
  - The coin designs' P rests on one coin sequence, which G4's 40-of-50 guard addresses.
  - The carry rule's moving-block bootstrap (63-session blocks) is the right tool for this. It was set before any
    reading (D-621).

**(c) Reported today?**
- For P-16 and FV3-C: yes (V1 files).
- For P-14: no.
- The gate floor of CHARTER section 3 (iii) is read on the independent draw.

**How to report it in the new repository:**
- Before any judged comparison, run V1's A1, A2, B2 and C1 on P-14 (E2).
- Read the floor (iii) beside its block-63 reading for every challenger, which D-663 already requires of every
  pre-registration.
- Report P with its block-bootstrap interval, never bare.

## 7. Five seats, one position per firm, queue and activation timing

**(a) Where it lives and which rows adopted it.**

The caps (all three gates: `accounts`, `combines` and `total_accounts` are each 5):
- `gate.py:231-232` refuses more than five funded accounts (D-21, 8284215, verified).
- The joint cap of five accounts including evaluations is a self-imposed policy (D-34). The verified rule allows
  unlimited evaluations (`rules.yaml` `combine_count_limit`).
- Under D-34 the hold queue cannot be reached (`rules.yaml` `hold_expiry_days`).

Routing:
- Rotation (D-157, `shared_days.py:166-397`): each trade goes to one account, the one that has waited longest and can
  take it (`routing` `able`, D-318).
- The firm's opposite-position rule (`shared_days.py:353-356`, D-339, verified 13747047 and 10296582).
- The operator's strict rule: no trade while any account holds a position, or within 5 minutes of one closing
  (`shared_days.py:357-360`, D-429; `one_at_a_time` 5 on all gates).

Activation:
- The activation fee is charged when the seat is filled, at activation (`lockstep.py:2066-2075`; the default
  `ACTIVATION_ON_ACTIVATION`, `lockstep.py:1249`). This matches 8284217's activation flow. D-21's mismatch was the old
  `reinvest.py` pass-day charge, which is not the lockstep default.

The seat:
- `seat_frees = same_evening` on all three gates (`lockstep.py:1432-1435`, `2063`; D-339, D-353). The seat frees at
  the close the account ends with, and the waiting pass activates that evening.

**(b) What would break the conclusion.**

- **The caps and the strict rule are conservative against the firm.**
  - The firm allows five funded accounts plus any number of evaluations, and forbids only opposite positions. The
    engine allows five accounts in all and one position at a time.
  - The strict rule costs P-14 0.152 of growth at the bound (verdict row `strict_rule_cost_bound`); it costs P-15
    0.048 and P-16 0.160.
  - Supply is not the limit. For P-14, 0.149 of offered signals are routed (`u_xfa_day_budget.csv` design p14, arm
    verdict, section `signal_supply`, group router, `share_routed`); 0.187 are refused because an account is in
    position, 0.136 because they are opposite, and 0.528 because no account is flat.
- **The seat timing is optimistic and rests on an unverified row.** `rules.yaml` `xfa_seat_frees_at` reads
  `unverified_human_input_required`: "None says when a closure at request takes effect or when the activation button
  returns".
  - Same-evening is "the fastest reading these pages allow for a breach" (D-446). The engine's own default, the next
    session, is one session slower.
  - P-14 uses the no-closure table, so funded endings are breaches. For those, "closed at the end of the day" plus
    "minutes after paying the Activation Fee" makes same-evening plausible.
  - **Upper bound (labelled):** about 117 funded endings per path (`mean_accounts_funded` 117.4, P-14 bound row) of
    2,520 seat-sessions. At most about 4.6 % of seat capacity is in question.
  - D-353 recorded that FV3's money sat "in the refilled seats". No vendored file prices the difference for P-14 (P-09's
    audit replication RC is not vendored).
  - The new repository's CLAUDE.md requires every firm rule used to come from the verified ledger. This is an engine
    convention that rests on an unverified reading. It should be declared under a decision row, or priced (E3).
- **Correlation of accounts.**
  - No trade is copied and no two positions are open at once. But all accounts on a calendar day trade the same
    historical day in sequence. A day that defeats the signal defeats every account that trades it.
  - The visible measure is joint breaches: two or more on 85-107 of 504 sessions (section 1). Some is size clustering
    (P-16's `abs_day_r` autocorrelation, section 6).
  - Correlation of outcomes between accounts within a day is not measured anywhere (E6).
  - For the money this mostly matters as conduct exposure: it is RTP trigger 1 and the stacking pattern. The P&L of
    five accounts that receive different sequential trades is close to five separate bets, with shared volatility.
- **Breach against abandon bookkeeping (m-4).**
  - The trigger counts evaluations that failed by breach and funded accounts closed by breach. It excludes
    out-of-room failures and policy abandons (`lockstep.py:1914-1916`).
  - On P-16 the point arm abandons 255.4 evaluations per path, the bound arm 15.2 (`rc_s150_all_gate_paths.csv`, run
    `gate`, enforcement_p 0, mean `combines_abandoned`). The multi-breach days go 9.7 → 85.3.
  - P-14's abandons are flat (4.0 against 3.9 in `a3_brk30_cb20_gate_paths.csv`).
  - Hypothesis, not settled: P-16's evaluation trade is sized close to the whole room. At the point a full stop leaves
    the account a few dollars above the floor, and the table cancels it. At the bound, the uniform shift of each loss
    by (lb - e) times the risk (`gate.py:38-39`) carries the same stop through the floor.
  - Economically the two are the same pattern. So the point arm's conduct tallies for P-16 understate it, and the bound
    arm's figures mix in an artefact of the shift.

**(c) Reported today?**
- The caps, the rule, the seat timing and the refused shares are on every gate row.
- The seat timing's unverified status is reported nowhere beside a result.
- The breach-against-abandon effect is not reported.

**How to report it in the new repository:**
- Declare `same_evening` as an assumption under a decision row. Price it once (E3).
- Count policy abandons within a declared distance of the floor as MLL-equivalent in the conduct tallies, beside the
  engine's count.
- Report the share of seat capacity used.

## 8. Other assumptions found that carry money

- **FV3's breakeven move (m-6).**
  - Every walk moves the stop to the entry at the next session open: 17:00, 19:00, 08:30 or 13:00 CT. It does so when
    that open is in the trade's favour by a tick, and books the exit at zero gross plus a tick (`fv3_rung_walk.py`
    docstring, "Breakeven").
  - Breakeven exits are 0.042 of 1R walks and 0.119 of 3R walks at 25 points, and 0.012 and 0.045 at 12.5 points
    (`a3_resolution_map.csv` section `map`, the mean of the hourly `share_breakeven` rows; not trade-weighted).
  - 10305426 lists "Using tight brackets or auto-breakeven to take advantage of favorable SIM fills" as a prohibited
    strategy (`rules.yaml` `prohibited_trading_strategies`).
  - A manual move at a session open with a tick of cost is not obviously that practice. But it is a trade-management
    rule inside R* that this repository has not declared. A breakeven stop's real fill in fast tape is also not
    measured.
  - Declare it, or remove it, in F-01's walk.
- **The replay's bankroll never binds (n-4).**
  - `user_journey.py:11-12`. The gate's bankroll is $100,000,000 (G14 column `bankroll`).
  - A start that would have spent beyond a real user's cash keeps buying, and is counted ahead if it later gets
    paid.
  - S1 reports the cash spent (P-14 $3,003 at p90), and Q1 and Q2 are beside it. But P itself is the share ahead for an
    unlimited wallet.
  - More purchases raise P: `nobudget_p14` 0.692 against P-14's 0.671 (UB section `cell`, block all, measure P). So
    the lever that most raises P is the one most exposed under section 1.
  - Report P at a declared wallet (E7).
- **The engine reads Topstep support's silence as permission.**
  - The ledger's two unverified rows touch nothing P-14 uses except the seat timing: `xfa_closure_at_request` (the
    no-closure table avoids it) and `xfa_seat_frees_at` (section 7).
  - Payouts pending at a breach are credited (`payout_after_request_survives_mll_breach`, verified).

## Engine against the verified rules: where they disagree

| point | engine (as P-14/P-16 run it) | verified ledger / article | direction |
|---|---|---|---|
| payout denial | per-payout draw, that account closed; 0 % in every user reading | ToU s.27: withdrawals from every account forfeited; FTP Corrective: pending payouts denied; each payout reviewed for Prohibited Trading Strategies | engine milder in the tail; off by rule |
| RTP placement | off by the operator's rule (D-289) | triggers and consequences verified (13620045) | a verified consequence omitted by rule |
| Focused Trader Program | not in the base case; swept beside the gate only | verified (10551016), no thresholds published | omitted by rule |
| funded seat refill | same evening | `xfa_seat_frees_at` unverified | fastest reading |
| RTP trigger 1 | two or more accounts of either kind in one engine day; breaches only | "multiple accounts", no count, no day definition | assumption, sensitive to bookkeeping (m-4) |
| stop gap-through | booked at the stop plus a tick | `fills.yaml` declares `next_price` (the repository's own model) | walk optimistic against its own declaration |
| flatten | worst 15:07-15:10 bar less 2 ticks | `fills.yaml` 1 tick; Topstep flat by 3:10 PM CT | walk stricter |
| account cap | five accounts including evaluations (D-34) | five funded, evaluations unlimited (8284215, 8284121) | engine stricter |
| one position | strict, 5 minutes flat (D-429) | no opposite positions across accounts | engine stricter |
| MLL trail, lock, payout floor | end-of-day trail, real-time breach, lock at 0, $0 after a payout | 8284204, 8284233 | match |
| activation fee | at activation | 8284217 activation flow | match |
| $100K/$150K funded lock | 1:1 trail assumed, labelled | not stated | labelled assumption, closed family |

## Proposed experiments

None was run. Each is light unless marked **heavy**. A heavy run takes the run lock and runs from a clean checkout.
Costs are my estimates. Cost references:
- V1 ran 76 engine runs of 500 paths for two subjects, workers 1, in one process. Both D-663 and D-665 are dated
  2026-11-15, so a 500-path gate run without an FTP sweep takes minutes to tens of minutes.
- D-502's runs, which carried a 16-model FTP sweep, took about 1.8 h per 500-path variant.
- U1's replay cost is not recorded in the vendored files.

- **E1 (heavy; first).** The user scorecard under the firm's responses.
  - An adapter in this repository's package calls the vendored `simulate_lockstep_path` replay with
    `ConductModel(rtp=True, rtp_warnings ∈ {0, 3})`, with `enforcement_p ∈ {0.10, 0.25, 0.50}`, and with the gate
    files' binding FTP models (slowdown and corrective at purchases ≥ 20/21d and lost ≥ 3/21d). The vendored replay
    call hard-codes `enforcement_p=0.0` at `scripts/customer_slices.py:232`, so the adapter is needed; no vendor
    edit.
  - Add an all-or-nothing forfeiture arm (a new adapter: at the first denied payout every account closes and pending
    payouts are denied).
  - Read P, S1, S3a, S3c and S5a for P-14, P-15 and P-16 on the verdict arm, with the start-day placement distribution.
  - About 3 designs × 10 arms = 30 replays, each about the cost of one U1 configuration-arm.
  - The identity first: with everything off, UJ's start rows are reproduced. Q-05 builds that identity.
- **E2 (heavy).** D-663's V1 on P-14: A1 (mean blocks 1, 5, 21, 63), A2, B2 (eight steps of 0.02 R), C1, and C2's
  two slippage families at P-14's 50- and 100-tick rungs. About 37 gate runs at 500 paths plus A2's five replay
  sets. That is about half of V1's 76 runs: on V1's evidence, under a day of run time at workers 1. This settles M-3
  and m-2.
- **E3 (heavy, small).** P-14's gate and its UJ replay with `seat_frees = next_session`, on both arms at 0 %. One gate
  call (both arms) plus two replays, an hour or two. This prices m-1.
- **E4 (light, read-only, local data).** From P-14's and P-16's rung walks (`data/atlas`, licensed, local): the
  distribution of how far the stop bar goes past the stop, by hour, and on BLS and non-BLS days. Then re-cost the
  trades with `next_price` and re-read e and its bound. No engine.
- **E5 (light).** Re-tally the conduct measures on P-16's and P-14's recorded paths, counting a policy abandon within
  one stop-cost of the floor as a breach. Count the bound arm's breaches that the shift alone creates (stop-outs whose
  point-arm twin survived), from an engine ledger of 20 paths. This settles m-4.
- **E6 (light).** The correlation of outcomes between accounts within a day: from an engine ledger of 20 bound paths
  of P-14, the correlation of the net R of consecutive routed trades on the same day across accounts, against the
  same quantity with days shuffled.
- **E7 (heavy, small).** The UJ replay of P-14 and P-16 with a finite wallet at S1's p50 and p90 (fees refused beyond
  it, D-8's rule). P for a user who stops when out of cash.
- **E8 (documentation, no run).** One decision row to record:
  - the condition on "contract shape" (C-1);
  - the in-sample status of R* (m-3);
  - the same-evening seat assumption (m-1);
  - the breakeven move (m-6);
  - that the value map is a model reading (m-5);
  - and a CHARTER section 2 rule that every user reading carries the denial ladder, the placement-on reading and the
    FTP minimum beside it.

## What I could not settle

- **P under placement on.** It is inferred near zero from `cons_p14` (P 0.000) and from the gate's payouts per path
  (3.45 against 81.87). The first placement day for each start, and what evaluations bought before placement still
  return in months 1-3, need E1.
- **P under denial with closures.** My AUDIT ESTIMATE ignores the closure a denial causes and the purchases after it.
  It is an upper bound on P under per-payout denial. Equal sizing of payouts within a month is an approximation.
- **Whether P-14's gate floor and bankroll hold under block-resampled days.** No vendored file reads it (E2).
- **The size of stop gap-through and of real slippage** on P-14's 12.5-point rung (E2, E4).
- **The mechanism behind P-16's point-against-bound gap** in multi-breach days and abandons (9.7 against 85.3; 255
  against 15). My hypothesis is in section 7 (E5).
- **Which bound UJ's `verdict` arm uses for P-14:** the 0.05 arm (mean R -0.0847) or the 0.05/N arm (-0.1252). D-620
  says "the bound the design's gate read". I did not trace the replay builder far enough to say which, so the solve
  edge's position between the arms is stated against both.
- **How much the value map's re-solved table differs from the traded table** in dv per place. Only the identity that
  the traded table can be reproduced is on file.
- **Whether a softer RTP reading** (warnings first, `rtp_warnings` > 0) **leaves P-14 positive.** No file holds one.
