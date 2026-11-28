# F-XX: the Topstep $50K design survey on NQ (Q-190, Wave 5), declared

**Status: declared (text 2, answering the red team's read (docs/reviews/F-13_DRAFT_REDTEAM_2026-11-27.md) and the
gatekeeper's form read (docs/reviews/F-13_DRAFT_FORM_2026-11-27.md), both in the main tree), drafted on
`prereg/TEMPLATE_design_search.md` text v3, whose LF sha256 `876be096402fc7d024037a9a81a2bef1fd2852f7ba1714c3389c23007b4ddc09`
E-284 pins.** The task is Q-214 (the declaration of Q-190, the Wave 5 Topstep survey over the lever space). The id
`F-XX` is the gatekeeper's to replace at the pin; the search takes no k (E-204): the held-out test's declaration takes
the one k of NQ's joint test, k = 13 the next (CHARTER 3.7). Its scope is frozen at this round (E-294 (5)).

**Declaration kind: design search.** This file keeps this line. It carries no `Judged-block reads:` line; the
held-out test's declaration, drafted on `prereg/TEMPLATE_heldout_test.md` (LF sha256
`33034aee9ca357b523780070996cc1242f09a4b1008b9cdd84fa47d660ab3b00`, E-284), carries it.

**Awaiting W42-R2's application (Q-189), and what else stands before the pin.** Every value below is left as the
template's placeholder `<...>` until its source exists; none is invented. **The setting rule is W42-R2** (E-296): W42-R1
with one added limit, a floor on the median 12-month net cash, and a headroom that counts both noises; W42-R1 is never
applied. W42-R2 is `docs/plans/WAVE42_SETTING_RULE_R2.md`, `extended/wave42_r2.py` and `scripts/wave42_r2_apply.py`
(on wt/wt-w42r2 at `db3cc27`, its second fix pass), its pin file `config/w42_r2_pin.json` and its one output
`results/w42_r2_values.csv`. When W42-R2 has been applied once to H4's collection result and the lead's pinning row
cites that output's sha256 (Q-189), each value is copied from the output's key named beside it, never typed from a
reading, and the red team checks the diff (section 14 step 1).

- **From W42-R2's applied output (Q-189):**
  1. the seven limits' values (`limits`, each limit's `values`), section 7 row 1;
  2. the bankroll budgets of measure (24) and B\* (`budgets`, its `primary`), section 7 row 2;
  3. the dimensions' caps lo and hi (`dimensions`), section 7 row 3;
  4. the weights (`weights`), section 7 row 4;
  5. the form, the composite or the fallback (`form`), section 7 row 5;
  6. delta\*, the size that matters (`delta_star`), section 7 row 6;
  7. the no-harm margin, declared here as delta\* (section 7 row 10), so its value is item 6's;
  8. the do-nothing floor's value (`null_journeys`, its `floor`), section 7 row 11;
  9. the decision row that pins the values file (`values_row` and `margin_row` of the survey-spec block, section 6).
- **From H3-D's declaration** (`prereg/H3_three_way_deciding.md`, the file H3's text names for it, E-279, written later
  under its own row): **the H3-D placeholder** of section 9 -- its pinning row and LF sha256, and its replicate counts.
  H3-D needs delta\*, so it follows Q-189; it reads H4 only through W42-R2's output.
- **The build before the pin** (E-297 (2), (3); section 14 step 2), each item built, reviewed and merged before the
  hash row, its files on the deciding-files line (section 1):
  1. **W42-R2 merged and pinned** (wt/wt-w42r2 after its fix pass, its red-team read, its pinning row before H4 is
     read, E-296), and the survey's objective moved to it: `survey.W42_RULE` and `load_objective` read W42-R2's rule id,
     module and output, and the limits come only from `extended.wave42_r2` -- `limit_estimate`, `limit_check` and
     `limit_per_seed_sd` imported from it, never from `extended.wave42` -- whose headroom uses sd\*, the largest
     per-seed sd of the four baselines, for both the test's and the search's noise;
  2. **the parts**, `extended/survey_parts.py`: the space (T1 narrowed to the declared triggers, `p14` and `rl3`, by
     its `sources` parameter, and T7 held at `off`), the gate, the schedule builder, the design runner over Q-215's
     real-bar route `extended/survey_route.py` (wt/wt-survey `d64aced`, under its red team) and
     `extended/design_trades.py` (E-291), with its identities B-I1 to B-I3, and the playbook writer; the route refuses
     `coin` and `p16` by name (`trigger_sides.NO_SIDE`), `rl3` without its declared level kind and cutoff, and any T7
     but `off`;
  3. **the runner's calls to the route's boundary checks** (the route's re-read, m-1): on every cell the runner calls
     `survey_route.check_policy_reads` (as corrected under that read's B-1) before it builds the job,
     `survey_route.check_taken_rr` on every lane's log (`three_way_baseline.simulate(log=True)`, or a per-lane
     assertion with the same keys) and `survey_route.own_rr`, reads facts only through `survey_route.facts` (never
     `design_trades.facts_for` directly, so `masked_problems` runs), and reads outcomes only per R (`set_risk(risk,
     w)`), its identity never using `outcome="vendored"` on a table without w = 1; **it enforces
     `survey_route.PNL_READERS`** (the route's c3 read, `docs/reviews/BUILD_Q215_ROUTE_c3_2026-11-28.md` m-7): no route
     table reaches `gate.shifted_blocks`, `gate.mean_r`, `SharedDayDraw`, `EmpiricalDraw` or `outcome="vendored"`, and
     the runner reaches the engine only through `survey_route.facts` and `survey_route.route_simulate`, never
     `three_way_baseline.simulate` directly; a refusal stops the run; the runner's build has its own red team, which
     checks these calls and readers, and a mutant runner dropping any of these calls fails a test, as does one bypassing the route. **The two
     reading sizes** in the engine and the runner (section 6), with a refusing test for each code point named
     there;
  4. **the keep rule at the point estimate** in `survey.beats_baselines` (section 7), the one-sided check beside;
  5. **the stress arms** of measures (28) and (29) in the design runner, as H4's runner reads them (section 10 (c)),
     brought forward from Q-224;
  6. **S1's file in clean runs** (E-297 (3)): `scripts/run_clean.py` supplies `results/s1_range.csv` read in place from
     the main tree's verified copy, `s1_range.load_range` refusing unless its raw sha256 equals the one cited in section
     3 and its manifest verifies, and a clean checkout without it refusing, never falling back to `NotComputed`;
  7. **the major-news floor** (section 4): its refusing count on the taken-trade log, with a planted violation that
     fails it, and BEA's GDP release calendar, which exists in neither this repository nor the vendored tree: built from
     BEA's published schedules and verified under its own row (none is invented here);
  8. **this search's seed block** in `extended/three_way_seeds.py` (section 12);
  9. **the power gate's whole-pipeline simulation** (section 9);
  10. **the m-8 experiment** on record (section 5).

  The survey-spec block's part, engine and objective-code sha256s, the space's built digest (computed with S1 active),
  the protocol's sha256 and the plateau steps and tolerance computed from the loaded bounds are the build's, left as
  placeholders in the block until it exists (section 6).
- **The gatekeeper's:** the F-number in place of `F-XX`.

## 0. In plain words (for the operator)

This is the first search for a way of running Topstep $50K Combine and Express Funded accounts that gives a user a
better journey than the four plans already known (the naive coin, P-14, P-15 and P-16), traded by hand on NQ minis and
micros. A design is a schedule of up to five components, one in each session the firm allows (the evening, Asia,
London, NY AM, NY PM), each with its own trigger, latency, entry type and bracket, plus the account policy (how many
evaluations and funded seats, steady or flip, the daily stop, the price and payout paths, purchases, payout requests).
The search reads **only 2020 to 2023**: first a spread-out sample of 512 designs, then 8 rounds of 32 designs each
chosen by a model of what the first readings showed (the sample and the first 4 rounds read cheaply, on a quarter
of the start days and 4 coin seeds of their own; the best 32 of them and the last 4 rounds at full size, on other seeds), then a re-read of the best few on fresh coin seeds and a check
that their neighbours do as well. Every trade's outcome is redrawn with direction removed, so nothing here rewards
predicting the market; what can win is timing, bracket shape and how the firm's fees and payouts reward an account
policy.

What a user would do with a finalist: follow its one-page playbook (which session, which trigger, which side, which
bracket, which account takes the trade), entering every order by hand at least L minutes after its alert.

What counts as a pass: a finalist is carried only if, later, on 2024 to mid-2026 (read once, by the separate held-out
test of every firm's finalists), it beats each of the four baselines on the composite W42-R2 pins, inside every limit
at its point estimate, with every floor held (conduct, the do-nothing floor, the long-run gate, the stresses). **What a
fail means:** the search closes with a closing row; nothing of it is rerun; it spends no k; a new question is a new
declaration citing this one.

## 1. The question, the firm and the baselines

- **The market:** NQ -- the one market this search reads, its 1-minute bars through `extended/reader.py` only
- **The firm and account:** Topstep, combine50k -- the $50K Combine and its Express Funded Account, one firm only
- Its rules are the verified ones only (CHARTER 3.1): Stage 2's ledger (`vendor/stage2/config/rules.yaml`) and this
  repository's record (`config/rules_extended.yaml`), read through `extended/firm_terms.py` by
  `extended/lever_space.py`, this repository's record first where it holds a key. **Every key the search reads, with
  its status at this commit** (`lever_space.rule_status`; the loader refuses any key not `verified`, so a refused
  key's lever is out of the space):

  | key | where verified | status | the levers that read it |
  |---|---|---|---|
  | `trading_hours` | Stage 2's ledger | verified | T2, T2b, T3 (and the dropped S6) |
  | `combine_mll` | Stage 2's ledger | verified | S1, S3, A1, A17 |
  | `combine_position_size_limit` | Stage 2's ledger | verified | S3, S5 |
  | `combine_profit_target` | Stage 2's ledger | verified | A1, A3, A17 |
  | `combine_consistency_max_day_frac` | Stage 2's ledger | verified | A1, A3 |
  | `combine_count_limit` | Stage 2's ledger | verified | A7 |
  | `combine_cancellation` | this repository's record | verified | A10 |
  | `account_start_rate_limit` | Stage 2's ledger | verified | A11 |
  | `xfa_mll_start` | Stage 2's ledger | verified | S1, S4, A2, A17 |
  | `funded_scaling_plan` | Stage 2's ledger | verified | S4, S5 |
  | `xfa_payout_path_choice` | Stage 2's ledger | verified | A5 |
  | `xfa_std_cap`, `xfa_cons_cap` | Stage 2's ledger | verified | A2, A5 (and `xfa_std_cap` the refused A19) |
  | `xfa_std_winning_days`, `xfa_std_winning_day_min` | Stage 2's ledger | verified | A2, A5, A18 |
  | `xfa_cons_min_days`, `xfa_cons_max_day_frac` | Stage 2's ledger | verified | A2, A3, A5 |
  | `xfa_lock_at` | Stage 2's ledger | verified | A18 |
  | `payout_min`, `payout_max_frac_of_balance` | Stage 2's ledger | verified | A2, A18 (and the refused A19) |
  | `max_active_funded_accounts` | Stage 2's ledger | verified | A6 |
  | `hold_queue_behaviour` | Stage 2's ledger | verified | A8 |
  | `subscription_fee`, `activation_fee` | Stage 2's ledger | verified | A4 |
  | `subscription_fee_naf_50k`, `activation_fee_naf_50k` | this repository's record | verified | A4 |
  | `back2funded_max_reactivations`, `back2funded_reactivation_fee_50k`, `back2funded_window_days`, `back2funded_eligibility`, `back2funded_seat_count` | this repository's record | verified | A12 |
  | `require_profit_since_payout` | Stage 2's ledger | verified | A20 |
  | `payout_lag_days_aeropay`, `payout_fee`, `payout_lag_days_ach`, `payout_fee_ach` | Stage 2's ledger | verified | A21 |
  | `cross_account_opposite_positions`, `cross_account_hedging` | Stage 2's ledger | verified | the conduct floor (section 4) |
  | `prohibited_strategy_max_size_into_major_news`, `prohibited_strategy_auto_breakeven_sim_fills` | this repository's record | verified | the conduct floor; S7's drop |
  | `hold_expiry_days` | this repository's record | **unstated: refused** | A9 (its two readings, section 3) |
  | `payout_request_amount_choice` | this repository's record | **unstated: refused** | A19 (held at `max`, section 3) |
  | `back2funded_fee_by_pricing_path` | this repository's record | **unstated: refused** | the combination A4 `naf` with A12 above zero (section 3) |
  | `tier1_news_events_restriction`, `economic_releases_list` | this repository's record | **changed: refused** | not read: no verified news window reaches Topstep's accounts (`extended/modes_news.py`); the major-news floor is section 4's declared list |
  | `reset_rebill_push`, `dll_offer_status` | this repository's record; Stage 2's ledger | verified | the dropped A13, A14 (read only to drop them) |

- **The deciding files:** `extended/reader.py`, `extended/survey.py`, `scripts/survey_run.py`, `extended/survey_parts.py`, `extended/survey_route.py`, `extended/wave42_r2.py`, `scripts/wave42_r2_apply.py`, `scripts/wave42_apply.py`, `scripts/run_clean.py`, `identity/h4_registered_constants.py`, `extended/__init__.py`, `extended/calendar_early_closes.py`, `extended/calendar_fomc_minutes.py`, `extended/campaign.py`, `extended/components.py`, `extended/day_calendar.py`, `extended/design_trades.py`, `extended/family_stats.py`, `extended/features.py`, `extended/firm_terms.py`, `extended/gate.py`, `extended/h4_coin_source.py`, `extended/journey_measures.py`, `extended/lever_space.py`, `extended/lever_space_firms.py`, `extended/levers_path.py`, `extended/lift_bound.py`, `extended/lock_guard.py`, `extended/modes_rules.py`, `extended/modes_terms.py`, `extended/openings.py`, `extended/payout_policy.py`, `extended/pin_order.py`, `extended/place_fields.py`, `extended/place_records.py`, `extended/plateau.py`, `extended/playbook.py`, `extended/price_levels.py`, `extended/proposer.py`, `extended/replay_records.py`, `extended/results.py`, `extended/router.py`, `extended/s1_range.py`, `extended/search_calendar.py`, `extended/search_cut.py`, `extended/search_space.py`, `extended/surrogate.py`, `extended/t7_forecast.py`, `extended/three_way_baseline.py`, `extended/three_way_fastkeys.py`, `extended/three_way_firm.py`, `extended/three_way_journey.py`, `extended/three_way_keys.py`, `extended/three_way_move.py`, `extended/three_way_redraw.py`, `extended/three_way_runner.py`, `extended/three_way_s1.py`, `extended/three_way_seeds.py`, `extended/three_way_stats.py`, `extended/trigger_sides.py`, `extended/triggers.py`, `extended/user_beside.py`, `extended/user_measures.py`, `extended/vol_descriptive.py`, `extended/walker.py`, `extended/wave42.py`, `config/rules_extended.yaml`, `config/calendar_fomc_minutes.csv`, `config/calendar_early_closes.csv`, `vendor/stage2/config/rules.yaml`, `vendor/stage2/config/fills.yaml`, `vendor/stage2/config/instruments.yaml`, `vendor/stage2/config/fv3_corrected_portfolio.yaml`, `vendor/stage2/config/atlas_a3.yaml`, `vendor/stage2/data/release_days_0830_2009_2025.csv`, `vendor/stage2/config/sources/fomc_statements.csv`, `vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv`
- **How the line is made:** the static import closure (`survey.closure_files`, the binding's own function) of every
  `extended` module the survey, its parts and their readings use -- the survey and its engine, the design route
  `extended/design_trades.py`, the three-way runner and its statistics, the power gate's synthetic histories
  (`extended/three_way_s1.py`), the firm path, the lever space with S1's and T7's loaders, the features, the naive
  coin's builder, W42-R1's module (which W42-R2 runs) and the calendars -- with the entry scripts, the identity of the
  registered constants, and the configuration and calendar files they read. `tests/test_f13_draft.py` recomputes the
  closure of every listed `extended` module and refuses a missing one. `extended/survey_parts.py`,
  `extended/survey_route.py`, `extended/wave42_r2.py` and `scripts/wave42_r2_apply.py` are written by the build before the pin (the head's list,
  items 1 and 2; the last two on wt/wt-w42r2 now), and the build's closure is re-checked against this line before the
  hash row; every other file of the line exists at this commit. The reader's `go_row_present` holds each
  file byte-identical at HEAD and at the go row's runner commit and unchanged in the working tree (U-1; section 14
  step 4).
- **Its own execution protocol** (E-202; never another firm's reused): Topstep's $50K lever table,
  `docs/plans/LEVER_TABLE_topstep50k.md` at blob `5c7d18b` (Q-151, E-211; its per-date session rows E-261), loaded by
  `extended/lever_space.py`, with RD-05 part B's sizing (`extended/modes_rules.py`) and the trigger library
  (`extended/triggers.py`, `extended/components.py`, the mix router `extended/router.py`). MFFU's and Lucid's tables are
  their own searches' and are not read here.
- **The baselines** (CHARTER 2, 3.8 (b)): naive coin harvesting and Stage 2's P-14, P-15 and P-16
  (`survey.BASELINES`, the survey-spec block's `baselines.names`, in that order). **The naive coin's levers are fixed by
  H4's declaration** (`prereg/H4_rebaseline.md`, LF sha256
  `a2c1408e8f22a3d4926248a3bf53f311f65234ce1e15399dc378ed35d4aa913c`, E-287, its section 7, MEASURES (35)): an offer at
  every moment of `resolved_coin.marks()`'s grid in P-16's window `all`, unchained, market entry, L = 5, admission T7
  off, P-16's registered shape, sizing, account policy and purchase budget, walked by `walker.STAGE2` with FV3's
  breakeven move on. **Each baseline runs under the design's convention** -- the reflection and the martingale-outcome
  reading under the same seed keying, the same fill and cost mechanics, no arm shift, the same verdict settings --
  **at its registered latency** (P-14 at five minutes; P-15 and P-16 scheduled at their registered marks, latency-free,
  their latency variants dropped, E-203 B-2; the coin at L = 5), through the firm path's baseline mode
  (`extended/three_way_baseline.py`, E-281) exactly as H4 runs them.
- **The same convention, and the one difference declared** (CHARTER 3.8; the route's re-read, m-4): the baselines
  keep their registered plans, so H4-B's readings and the early look read each trade at an R set by the account's
  state (the registered plans' leaves), while a design is read at its one w in every state. **The convention CHARTER
  3.8 asks for is the same:** the reflection, the martingale-outcome redraw, the seed keying, the fill and cost
  mechanics, the arms and the verdict settings are one for designs and baselines. **The R schedule is not part of the
  convention but of each plan:** a baseline re-read at one w would no longer be the registered baseline that B-I1 to
  B-I3 reproduce. **The difference does not favour the designs:** under the martingale-outcome reading every trade's
  gross is zero at any R, so the R schedule moves no expectation, only the spread of outcomes through the contract;
  and the designs are held to one w across every state while the baselines may vary theirs, so the designs' options
  are the narrower, which can make beating a baseline only harder.
- **Each baseline's runner identity** (the survey's design runner, CLAUDE.md: every new runner has its own identity),
  each refusing, each on the search years only:
  - **(B-I1) the schedules:** each registered baseline's schedule equals its registered trigger-level trades on the
    trading days to 2023-12-29 -- times and brackets, path for path -- by the search-year sub-hash recorded in
    `results/h4_registered_constants.csv` (raw sha256 `7c3884f5445f37be09a09dd838150d34ff468636775a24f96e894e76de1dc413`,
    E-287), compared exactly (H4's I-1);
  - **(B-I2) the naive coin's offers** equal H4's I-5 source (its unchained offer list by `rc_dev_test.trades_hash`),
    compared exactly;
  - **(B-I3) the readings:** the runner's baseline arms, run at H4-B's own keys (the role `h4b_coins` in the part
    H4-B, used only as H4 registers it, section 12), reproduce `results/h4_units_<baseline>.csv` (H4's per-unit
    deciding readings, written by H4's clean runs) on every search-year start and every H4 seed index, every key of
    `wave42_r2.REQUIRED` (W42-R1's keys, which W42-R2 carries, and `net_month_12`) in its columns: counts, shares and day counts equal exactly, a dollar key within a millionth of a
    dollar (MEASURES 1.2's tolerance). A start set that differs from H4's refuses before any comparison.
  - **Each baseline's runner identity reads the search years only; it has no held-out part** (L-1; E-259). The
    registered rows are reported beside.
- **The measures** are `docs/MEASURES.md`'s, every one by the function that file names, each a distribution over
  start days (median, p10, p90) and over coin seeds, read on the common start set `E_h` at its horizon (MEASURES.md
  1.1). The composite's six dimensions are W42-R1's (`docs/plans/WAVE42_SETTING_RULE.md` section 4.1, LF sha256
  `2179ff4a366d7ba61ecd425674dab8fd361d80a1713d4b8630943c5683662441`, E-283), carried unchanged by W42-R2 (not in its
  `OVERRIDES`); the seven limits are W42-R2's (`docs/plans/WAVE42_SETTING_RULE_R2.md` section 3.1, E-296): W42-R1's six
  and `net_month_12_p50`. This search defines no measure of its own.
- **What is new here** against every earlier search, family and RD map: this is the first design search of the
  program. Stage 2's families and F-01 to F-03 searched trades for lift; RD-01 to RD-05 mapped firm levers on the whole
  window (superseded by RD-06 to RD-10, search years only, E-268 to E-272); F-04's grid and RL3 were recast into this
  lever space and its NY AM component (E-208); H4 read the four baselines only, with nothing searched. Here every lever
  of the table is surveyed together, on the search years only, under the zero-edge convention and the journey
  objective, so no earlier reading is repeated: the overlap is the baselines (H4's, reproduced by B-I3) and the
  trigger sources (P-14's breakout, RL3's tickets), whose reads are in section 2's ledger.
- **One search-year read of a cell in this space already exists, and is declared here:** Q-213's exploratory early
  look (E-291; job `q213-early-look`, clean checkout of `514f6ad`; `results/early_look_rl3_pd_fade.csv`, exploratory,
  deciding nothing). Its one cell is RL3's draft base cell -- `rl3` with the side `fade` at the prior session's levels,
  NY AM, latency-free, Topstep 50K, zero edge, search years only -- read through `extended/design_trades.py`, this
  survey's design route; that cell lies in this space (T1 `rl3`, T8's `fade` rule). P-14's H4-B readings were placed
  beside it. **No value in this file comes from it.** Section 2's search-year ledger lists the read and who saw it,
  section 16 dates every choice against it, and section 13 counts its cell beside the count.

## 2. Years, the held-out read ledger and the confirmation window

- **Development:** NQ 1-minute bars 2020-01-02 to 2026-07-16 only, through `extended/reader.py` (the one door); this
  search touches its search years only, and the reader refuses it any session of the held-out years.
- **The search years** (E-208): 2020-01-02 to 2023-12-29. The search, its lever ranges, volatility units, regime
  thresholds, schedules, limits, budgets and weights read these years only. Its starts and every sessions-left count
  come from the pinned search calendar, `results/search_calendar.csv` (raw sha256
  `dfd75dadb697349eea547fc88c1bb18b50828a2e60ac6496366e0e5f4da9a3ba`, E-266), through
  `extended/search_calendar.py`, as W42-R1 (so W42-R2) and H4 bind it.
- **The held-out years** (E-208): 2024-01-02 to 2026-07-16, never read by this search, on the pinned calendar
  `results/q82_judged_sessions.csv` (its session count and sha256 asserted by the held-out runner). "Held out" means
  **unread by the search's code and unused by any choice in this declaration** (CHARTER 3.6 (a)). They are read by the
  held-out test only, once (section 14).
- **The horizon embargo** (CHARTER 3.6 (d); MEASURES.md 1.1): a start is read at horizon h only if h sessions remain
  in its own years; a held-out start reads only held-out sessions for its outcomes; causal look-backs into the search
  years are allowed. The longest horizon read here: **504 sessions**, D-145's horizon, for the long-run gate's
  search-year history-block reading beside (section 10); the composite's longest is 252 (the dimensions W42-R2 carries, `bankroll` and
  `steady`). The strip it purges at the end of the search years: the last 504 sessions for the gate's reading, the
  last 252 for the twelve-month dimensions, each start's own sessions left on the pinned calendar deciding.
- **The re-baseline (H4)** reads the search years only, its runner refusing held-out sessions (CHARTER 3.6
  (e)), so it computes no held-out output and CHARTER 3.6 (e)'s sealed case cannot arise here (n-2).
- **Single use per market** (CHARTER 3.6 (c); E-221, O-1): every model is
  built, tuned and chosen on the search years only (any number of internal time splits there). No firm's search spends
  NQ's held-out years alone: they are held until every **member search** -- the one design search of each of
Topstep, My Funded Futures and Lucid with a hash row before **the membership event, the first go-row token of an NQ
design search of Topstep, My Funded Futures or Lucid** (H-1'; E-257; E-259), at most one per firm, a second hash row
for a firm before the event refused by the gatekeeper at its pin and by the reader at the go row (n2) -- has a
finalists' row or a closing row, a firm with no hash row before the event being in state (c) of
`prereg/TEMPLATE_heldout_test.md`, fixed at that moment; and every finalist across the firms is then tested in
**one joint fixed-sequence test** at the full level of the one k it spends, the one use per market. That test is
**the held-out test's declaration**, one declaration of its own (E-238): it lists every firm's finalists (each by its
search declaration's hash and finalists' row), fixes the joint order, takes the k, and is
the one family that reads NQ's held-out window, so Q-158's rule (one family per market) holds unchanged. This search's
finalists enter it through this file's finalists' row
only if this search is a member (its hash row before the membership event): **Topstep's; a member if its hash row
comes before the membership event, which no go row has yet set (no design search is pinned at this commit); the
held-out test's declaration does not exist yet** and is drafted on `prereg/TEMPLATE_heldout_test.md` once every member
search is terminal. A search pinned after the membership event, or a successor of a
closed search, is never a member of this F-HT; its candidates are tested only on data this line has never read (a
later purchase), under its own k; the confirmation window (NQ from 2026-07-17) is read once, only for this F-HT's
carried designs (CW-1; E-259). **Data this line has never read** is NQ bars after the confirmation window's end, or
another underlying's bars that no declaration of this repository has read (NQ and MNQ are one underlying); never NQ's
search years, held-out years or confirmation window (CW-2; B-2; finding 7). A successor search on another underlying
first needs a new decision row and a reader rule that extends the market allow-list; until both exist, its go row is a
refused problem (F9). A member's finalists are never voided. A later search on the same bars reads NQ's held-out years
and F-HT's results as a description only, after F-HT's verdict row (reader rule 4; n4), or moves its held-out years to
data not yet read (a purchase or the operator's setup).
- **The held-out read ledger** (CHARTER 3.6 (b)). Every past read of the held-out years for this search's comparators
  and trigger families, each in RD-04's leak-clause form: **written after this reading; no figure cited**. CHARTER 3.6
  (b)'s list is the floor, E-211 added Q-132 and Q-16's paired nulls, and H4's ledger (its section 2) is carried whole;
  this declaration completes it:

  | read | what it read of 2024-2026 | for which comparator or trigger | row |
  |---|---|---|---|
  | Stage 2's choice of P-14, P-15 and P-16 | their whole-window development tests and verdicts | P-14, P-15, P-16 as comparators; P-14's breakout and P-16's marks as the sources T1 `p14` and `p16` | Stage 2's registrations; E-208 |
  | P-14 fixed as R\* from the whole window | the user readings that chose it | P-14 | Stage 2 D-626 |
  | P-14's rung map and P-16's mark cutoff | resolved on the whole window | P-14, P-16; the source `p14` | E-203 S-2 |
  | P-16's stop, chosen on each block | the stop screens' whole-window rows | P-16; the naive coin's stop (inherited) | Stage 2 D-554 |
  | P-15's and P-16's resolved marks | the cutoff's unresolved shares over the whole window | P-15, P-16 (passed through as registered) | Stage 2 D-525 (4) |
  | P-16's window `all` | a cell of the whole-window screen | P-16; the naive coin's window | Stage 2 D-525 (3) |
  | the no-closure table and the purchase budget | the compliance study's whole-window readings | the baselines; the naive coin's account policy | Stage 2 D-502, D-509 |
  | RD-04 (c): P-14 and P-16 on the late block | declared, not run (superseded by RD-10, E-272) | P-14, P-16 | RD-04's pinning row |
  | RD-05: the late block read as late development | its whole-window readings of the registered designs | the baselines; the levers A1 to A5 (RD-05 part A, 2.6) | RD-05's pinning row |
  | Q-17 and E-201: every user measure beside the baselines | the firm-response replays over the whole window | the baselines | E-201 |
  | Stage 2's signal search | the whole-window search that produced the registered triggers | the sources `p14`, `p16` | Stage 2's search programs |
  | RD-03's whole-window lever readings | its readings of A7, A8, A10 and the dropped A13, A14 | the account-policy levers A7 to A14 | RD-03's pinning row |
  | Stage 2's program U | P on the late block against P-14 for its nine families | the baselines | RD-02 records it |
  | RD-02's late-block menu of payout policy | its late-block readings of the payout levers | A18 to A21 | RD-02's pinning row |
  | RD-01's late-block reads | its firm-contract readings | the baselines | RD-01's pinning row |
  | Q-132's rows | every `judged` and `all` row for P-14, P-15 and P-16 | the baselines | E-211 |
  | Q-16's paired nulls | computed on the held-out years | the baselines | E-211 |
  | RL3's level choice and E-204's recast | the resting-level atlas, Stage 2's whole-window construction of its levels | the source `rl3` (NY AM) | E-204, E-208 |
  | S2's grid | RD-05 2.6's reward-to-risk grid, citing Stage 2 D-429's reference ratios; whether that screen read 2024 to 2026 is not on record, so it is entered | S2 | the lever table, section 6 |
  | the stop floor | the registered stand-aside floor, a Stage 2 constant; whether its derivation read 2024 to 2026 is not on record, so it is entered | S1's lower cap | Stage 2 D-271 (3), D-272 |
  | F-04's parameter table and RL3's declared values | written by researchers who had read the whole window | T5, T6, S5, A3 (F-04 6.1; RL3 6.1) | E-208 |
  | the ledger constants | W = 126 and the 252-session window, set with the held-out years visible; the 21-session month; U1's `EXACT` horizons | every dimension and limit of W42-R2; every baseline's windows and exact runs | Stage 2 D-518, D-620 (3)(f); Q-44 |
  | W42-R1's own entry, which W42-R2 carries unchanged | the held-out session calendar's dates only, to count complete starts | the power forecast | E-283; E-296 |
  | the lead's choice of P-16's shape for the coin | made by a reader of those designs' whole-window journeys | the naive coin | H4's section 7 (E-287) |
  | the busiest-day capacity | each registered cell's whole-window busiest day | P-14, P-15, P-16 (passed through); the naive coin (through P-16's job) | the registered builders; H4's B-2 |
  | the bar store manifest's held-out metadata | its `day_list`, `early_end_days` and `day_bounds` entries after 2023-12-29, dropped before they are parsed; no figure | the search calendar; the void calendar | Q-166; Q-197 |
  | the registered-constants run itself | the on-record whole-window identity run's existing read; it copies the registered marks and capacities by sha256 and computes only the search-year sub-hash | P-14, P-15, P-16 | E-247 rm-4; E-286 |
  | the identity reads of `results/read_ledger.jsonl` | the registered designs rebuilt over the whole window by `identity/stage2_identity.py` and its routes | P-14, P-15, P-16 | E-010, E-024, E-028, E-055, E-068, E-135, E-205, E-286 |
  | the `registered_design` reads of `results/read_ledger.jsonl` | the registered designs' whole-window trades and readings | P-14 and P-16 (E-021), P-14, P-15 and P-16 (E-024), P-14 (E-026), P-16 (E-035) | E-021, E-024, E-026, E-035 |

  **The search-year reads before the pin** (no held-out session; listed because they were seen by those who set this
  search's rules, E-207 (2)):

  | read | what it read | who saw it | row |
  |---|---|---|---|
  | Q-213's exploratory early look | RL3's base cell (`rl3`, `fade`, prior-session levels, NY AM) on the search years, at zero edge, Topstep 50K; `results/early_look_rl3_pd_fade.csv` | the lead and the operator | E-290 (4), E-291 |
  | P-14's H4-B readings beside the look | P-14's 12-month figures on the search years, from H4-B's held readings, unpaired | the lead and the operator (recorded in W42-R2's own text, its section 9) | E-291; E-296 |
  | H4-S's schedules and identities | the four baselines' search-year schedules, supply counts and identities, no journey outcome | the lead | E-288 |

  No range of this search is drawn from a whole-window reading: S1's range is Q-171's search-year reading
  (`results/s1_range.csv`, E-240, E-245), T7's forecast is fitted on the search years (`results/t7_forecast.csv`,
  E-253), T2b, A15, A16 and A17 read no bar (E-261). While the ledger is not empty, **the level is printed nominal**
  beside the verdict (E-203 S-2's form). For Stage 2's baselines "held out" means unread by this search only (E-208),
  stated beside every comparison with them.
- **No held-out result is ever written where a later search can read it** -- not in the lever map, not in
  `results/variants.jsonl` (CHARTER 3.3 (f)). The survey's `variant_rows` refuses any variants row naming the
  held-out years (`survey.heldout_problems`, `HeldOutRow`), and its `read_design` refuses a held-out reading before the
  report is read (`survey._held_out_first`); **a build requirement** of the design runner, with a test that a held-out
  row is refused before the survey runs.
- **The confirmation window:** NQ from 2026-07-17 to the last session in the purchase order's stated range, never read
  from bars, recorded in the first `heldout-window: NQ 2026-07-17 to <last> -- <text>` row, which states that it
  opens the confirmation window, not a second held-out test, and governs; any later NQ or MNQ window row from
  2026-07-17 on is refused by the reader (`extended/reader.py`; n1), this repository's `_cw_problems` only a
  cross-check; the purchase and that row come before the first finalists' row of any member (C-5; finding
  5), declared now, never read until a carried design is registered, and a purchase, the operator's (section 15); it
  is read once, only for F-HT's carried designs, and a non-member search's candidates never use it (CW-1; E-259).

## 3. The lever space

- **The lever table:** `docs/plans/LEVER_TABLE_topstep50k.md` (Q-151, E-211) at blob `5c7d18b`, loaded by
  `extended/lever_space.py` (`bounds`, `check_design`), the space built by `search_space.from_lever_space` through
  this search's space factory. Every lever of the search is a row of that table. No range is retyped: each is read by
  the loader at the run's commit, and the space's built digest is bound in the survey-spec block (section 6).
- **Every lever classed fixed / searched / dropped, with its value or range and its source kind** (the table's
  section 1). The class column is `lever_space.LEVERS`' (`declared` there is fixed here); one range is narrowed by this
  declaration (T1, below) and three searched rows are held (A15, A17 by the loader; A19 by its refused key):

  | lever | layer (trigger / trade shape / account policy) | what it is, in a phrase | fixed / searched / dropped | value or range | unit | source kind and source |
  |---|---|---|---|---|---|---|
  | T1 | trigger | the signal source of a component | searched | **narrowed here** to the sources with a playbook side: `p14` in every session, and `rl3` in NY AM, **by the lead's ruling on this text's first read (E-297 (2))**: the table's `coin` and `p16` are not offered, because no design holding one can be carried (`trigger_sides.NO_SIDE`; `survey.no_harm` fails any design whose side source is not the trigger's), so the survey spends no cell on them | categorical | declared: the table's T1, E-221 O-4, `extended/trigger_sides.py` |
  | T2 | trigger | the session of a component | searched (one slot a session, on or off) | `evening`, `asia`, `london`, `ny_am`, `ny_pm`, anchored per date | a session | arithmetic: `trading_hours`, E-231 (3) |
  | T2b | trigger | the NY AM / NY PM boundary | fixed | noon New York, `lever_space.ny_boundary` | a wall-clock time | declared: E-261 |
  | T3 | trigger | a component's offer window inside its session | searched | from its session's anchored start to its shortest span over the search years' weekdays, on the five-minute mark grid | marks after the session start | arithmetic: `trading_hours` and its note |
  | T4 | trigger | the latency L, alert to order | searched | 5 (the reference), 3, 2 minutes for `p14`; one latency-free cell for `rl3` (`lever_space.latency_cells`) | clock minutes | declared: E-202 (2)(c) |
  | T5 | trigger | the entry type | searched | `market`, `limit` (the source's offered cells) | order type | declared: E-202 (2)(d) |
  | T6 | trigger | how long a limit works | fixed | the table's T6 | minutes | declared: F-04 6.1 |
  | T7 | trigger | admission by forecast resolution | searched in the table, **held at `off` in this search** | `off` only: the space loads `off` and `admit` (`results/t7_forecast.csv` is present), but the route maps only `off` (`survey_route.T7_MAPPED`) because no admission forecast is wired into it; wiring admission is a later item, not this search | a probability's line | a search-year reading: `results/t7_forecast.csv` (E-253), D-212's line by key |
  | T8 | trigger | the side rule | fixed | in the evaluation the coin side (CHARTER 3.2); in the playbook the trigger's side by `trigger_sides.trigger_side` under the rules fixed in section 4 | side rule | declared: CHARTER 3.5, E-221 O-4 |
  | S1 | trade shape | the stop width, a multiple k of the trailing range | searched (per component) | each session's k range from `results/s1_range.csv` (raw sha256 `a9fb2b6ff616de4c9b1036ee016774313c684e6a7d8d4e26dbe04f9525feffe6`, E-240, E-245), loaded only after `s1_range.load_range` checks its manifest; **the stop in whole ticks:** the caps are checked on the unrounded k x T(d), T(d) the day's `trail20_range_pts`, and the stop is then rounded half up to whole ticks, at least one, by `vol_descriptive.band_ticks` (RD-04's and Q-121's rule for a range-scaled bracket, as the route applies it); **searched in every run** (E-297 (3)): the file is git-ignored (it carries price levels, E-245), so `scripts/run_clean.py` supplies it to each clean checkout read in place from the main tree's verified copy, `s1_range.load_range` refusing unless its raw sha256 equals the one cited here and its manifest verifies, and a clean checkout without it refuses, never falling back to `NotComputed` (the head's build item 6); the space's built digest bound in the survey-spec block is computed with S1 active | multiple of `trail20_range_pts` | a search-year reading (Q-171) |
  | S2 | trade shape | the reward-to-risk w | searched, **one w per design** (design-wide: every component takes the design's one w) | RD-05 2.6's grid ends, continuous; **why one w per design** (the route's re-read, `docs/reviews/BUILD_Q215_ROUTE_c2_2026-11-28.md` m-4, option (b)): the own-w rule refuses every design whose components' w differ (`survey_route.check_policy_reads`), and the first such design would stop the whole survey; a reader that takes each trade's own w would be new code beyond this search's frozen scope (E-294 (5)), so the space carries one design-wide S2 dimension in place of one a slot -- four dimensions fewer, the survey's and rounds' cell counts unchanged (512 + 8 x 32), the plateau's largest neighbourhood eight neighbours fewer (section 7's k_max), and no several-w design in the space; **flip under one w:** not in this search -- A1 and A2 are held at `steady` (their rows), so every leaf is a steady one read at the design's w; flip would change a trade's dollar risk, r_flip = the mode's goal / (k x w) (`lever_space._policy_eval`, `r_flip_by_w`), never its reward-to-risk, and until a flip stream is wired the runner refuses a flip leaf by name (so the runner refuses a flip leaf at any other R too); **one rule for S2 onto the engine's R** (the Q-215 route's red team, `docs/reviews/BUILD_Q215_ROUTE_2026-11-28.md` B-1): each trade is read only at its own component's w, its outcomes at every other w of the engine's grid are masked, and the runner refuses a taken trade whose R differs from its own w (the route enforces it, a build item of the head's item 2) | ratio | declared: RD-05 2.6 |
  | S3 | trade shape | dollar risk per trade, evaluation | searched | one micro at the floor stop to `combine_mll`'s room | dollars at the stop | arithmetic: `combine_mll`, `combine_position_size_limit` |
  | S4 | trade shape | dollar risk per trade, funded | searched | one micro at the floor stop to `xfa_mll_start`'s room | dollars at the stop | arithmetic: `xfa_mll_start`, `funded_scaling_plan` |
  | S5 | trade shape | the instrument mix | searched | `MNQ`, `mixed` | categorical | declared: F-04 6.1 |
  | S6 | trade shape | a maximum hold (a time stop) | dropped | none: CHARTER 4 bans time stops | -- | declared: CHARTER 4 |
  | S7 | trade shape | the breakeven stop move | dropped | off for every design (the baselines keep theirs, as registered) | -- | declared: `prohibited_strategy_auto_breakeven_sim_fills` |
  | S8 | trade shape | partial exits, scaling in | dropped | none | -- | declared: F-04 6.1 |
  | S9 | trade shape | contracts | dropped (derived) | from S1, S3 or S4, S5 by `modes_rules.size` | -- | arithmetic: RD-05 part B |
  | A1 | account policy | steady or flip, evaluation | searched in the table, **held at `steady` in this search** (the route's c3 read, m-5) | `steady` only: the baseline-mode race reads no flip stream (`three_way_baseline.replay` refuses one, and the vendored lockstep raises at the first funded flip decision with no flip draw), so a flip policy cannot run through the route; supplying the flip stream end to end is new code beyond this search's frozen scope (E-294 (5)), a later item | policy | arithmetic: RD-05 part A |
  | A2 | account policy | steady or flip, funded | searched in the table, **held at `steady` in this search** (the route's c3 read, m-5) | `steady` only: the baseline-mode race reads no flip stream (`three_way_baseline.replay` refuses one, and the vendored lockstep raises at the first funded flip decision with no flip draw), so a flip policy cannot run through the route; supplying the flip stream end to end is new code beyond this search's frozen scope (E-294 (5)), a later item; **the cells removed:** of the four (A1, A2) policy cells, the three holding a `flip` (half of each lever's declared `policies`), so two dimensions fewer; the survey's and rounds' cell counts unchanged (512 + 8 x 32) | policy | arithmetic: RD-05 part A |
  | A3 | account policy | the session rule q, when to stop | searched | `one`, `all`, `cap` | categorical | declared: F-04 6.1, the allowance by rule |
  | A4 | account policy | the price path | searched | `standard`, `naf` | categorical | rule |
  | A5 | account policy | the payout path | searched | `standard`, `consistency` | categorical | rule |
  | A6 | account policy | funded seats held at once | searched | one to `max_active_funded_accounts` | accounts | rule |
  | A7 | account policy | evaluations running at once | searched | the table's A7 range | accounts | declared: RD-03 2.2 |
  | A8 | account policy | banking while a pass waits | searched | `on`, `off` | categorical | declared: RD-03 2.2 |
  | A9 | account policy | the hold's expiry | fixed (two readings) | U-1's `exp_none` as the deciding reading, `exp_30` beside, never chosen: `exp_none` decides because it is the vendored engine's reading (a held pass waits, `extended/levers_readings.py`), which every baseline reads through the firm path as H4 runs them, so design and baselines read one expiry; its key `hold_expiry_days` is unstated, so the loader refuses the row and the runner applies this declared rule | reading | declared: RD-03 U-1 |
  | A10 | account policy | the evaluation-purchase rule | searched | `replace`, `house_stop`, `house_zero` | categorical | declared: RD-03 2.3 |
  | A11 | account policy | the evaluation-purchase budget | searched | the table's A11 range | purchases a month | declared: Stage 2 D-501 |
  | A12 | account policy | Back2Funded reactivations | searched | zero to `back2funded_max_reactivations` | reactivations | rule |
  | A13 | account policy | resets | dropped | none: no adapter for `reset_rebill_push` | -- | declared: RD-03 2.5 |
  | A14 | account policy | the daily-loss-limit election | dropped | none: a different account | -- | declared: RD-05 2.3 |
  | A15 | account policy | routing, which account takes a trade | searched, **held until wired** | held at `longest_waiting` (`lever_space.HELD_UNTIL_WIRED`) until Q-203 wires it; a wiring merged before the pin is a new space digest, cited then | rotation | declared: E-261 |
  | A16 | account policy | the signal mix's shares and assignment | fixed | `dealt` (`lever_space.deal_pools`) | shares | declared: E-261 |
  | A17 | account policy | the state rule, sizing by distance to the floor or target | searched, **held until wired** | held at `none` until Q-203 wires it, as A15 | rule on dollars at the stop | declared: E-261 |
  | A18 | account policy | the first payout request | searched | `elig`, `lock` | rule | declared: RD-02 6.1 |
  | A19 | account policy | the request amount | searched, **held by its refused key** | held at `max`; `half` beside under RD-02's labelled assumption, never chosen | share of the maximum | declared: RD-02 6.1; `payout_request_amount_choice` unstated (E-034) |
  | A20 | account policy | the request cadence | fixed | every eligible close | -- | declared: RD-02 6.1 |
  | A21 | account policy | the payout method | fixed | Aeropay, checked undominated by key | -- | declared: RD-02 7.1 |

- **Volatility units** (RD-04): the stop S1 as a multiple of `trail20_range_pts`, the trailing mean session range over
  the 20 prior walked sessions, read from bars closed at or before the alert; its multiple's range read on the search
  years only (Q-171, E-240); dollar caps from the verified rules (E-211's classing, E-157). The normaliser is
  `extended/features.py`'s, under `feature-rules` in full (bars closed at or before the alert, normalised, a
  shift-invariance test). R-10's sigma is section 5's.
- **The latency L is a searched lever** (CHARTER 3.3 (g), E-202 (2)(c)): its values, five minutes the reference and
  three and two counted variants, are declared here before any read, every L tried counted in the variants ledger and
  the multiplicity, nothing chosen after a look; each finalist tested at its own L; **the five-minute cell** (each
  finalist with every `p14` component at L = 5) reported beside every finalist and read in the held-out test, reported,
  not tested. RL3 is latency-free (E-204): its latency cells collapse to one.
- **Signal sources are a lever** (CHARTER 3.4): `p14` and `rl3`, one source a component (T1), the shares derived from
  the schedule and the accounts dealt to components (A16) under the held routing (A15). A signal source is judged by
  what it adds to the mix. **Hard rule:** never opposing positions at once across accounts or firms (conduct tier 1);
  one position at a time across a firm (Stage 2 D-429).
- **Room cuts and the out-of-room rule (C-1).** S3's and S4's whole-micro room cut (Stage 2 D-313) can size a trade to
  zero contracts at a positive room; A1's flip cut could, but A1 is held at `steady`, and A17 could, but is held at
  `none`. Section 5's out-of-room rule ends that account. This search searches S3 and S4, so it applies.
- **Combinations refused** (the table's section 4, `check_design`): A4 `naf` with A12 above zero, until
  `back2funded_fee_by_pricing_path` is verified; a latency on a latency-free source; any NY boundary but T2b's; and,
  from the space, a design whose components' windows collide in a session, an overlap mode other than `refused`, and a
  firm count other than one (`Space.check`'s `tier1`, `invalid`, `collision`, `session` and `rule` classes).
- **Fixed for every design** (the table's section 5: floors, not levers): restated by reference, never searched.

## 4. The component schedule across sessions, and the contract fit

- **Sessions in the search:** every session the firm allows -- the evening, Asia, London, NY AM and NY PM -- with
  their boundaries read from the verified `trading_hours` and the per-date anchors (E-231 (3), E-261) (**Any hour**:
  no cap on trading hours, E-202 (2)(b); workload (30) reported, and W42-R2's two workload limits (W42-R1's, carried), `orders_max_p90`
  and `accounts_max_p90`, are the only workload ceilings, E-221). The overnight sessions enter under H2's row, E-231,
  which admitted the overnight bars (`triggers.overnight_allowed`).
- **Each component:** one slot a session (the survey-spec block's space parameter `slots`), on or off; its trigger
  (scheduled times, or resting orders at levels known in advance), its window, its trade shape, and its **schedule
  across sessions** -- components' windows scheduled not to collide (one position at a time across the firm). A trigger
  that reads bars obeys `feature-rules` in full (bars closed at or before the alert, normalised, a shift-invariance
  test).

  | component | session and window | trigger, and when it is known | entry type | trade shape | latency L | its source row |
  |---|---|---|---|---|---|---|
  | evening | the evening window, offsets T3 from its anchored start | `p14`: P-14's breakout of the previous completed reference bar, known at that bar's close; the order goes in L minutes after | T5 | S1, S2; S3 or S4 by mode; S5 | T4 | the table's T1 to T5, S1 to S5 |
  | asia | Asia, offsets T3 from 09:00 Tokyo | `p14`, as above | T5 | as above | T4 | as above |
  | london | London, offsets T3 from 08:00 London | `p14`, as above | T5 | as above | T4 | as above |
  | ny_am | NY AM, from 09:30 New York to T2b | `p14`, as above; or `rl3`: RL3's pre-session tickets at levels published at the 08:30 CT alert, live at 09:00 CT (E-208, E-204), **its level kind `pd` (the prior regular session's high and low) and its cutoff 14:30 CT, fixed, not searched**: RL3's draft base cell (`prereg/DRAFT_F-RL3_resting_levels.md`, LF sha256 `a09c1e1fd3887e7ce559e72e47e48bae8f5a38263abfe8539a3ffc401992d431`; `pd` the first kind it lists, 14:30 CT the latest cutoff of `triggers.RL3_CUTOFFS`), the values Q-213's early look used; the two tickets one-cancels-other | T5 (RL3's own order pairing) | as above | T4; RL3 latency-free | as above; E-204 |
  | ny_pm | NY PM, from T2b to `trading_hours`' last new entry | `p14`, as above | T5 | as above | T4 | as above |

- **Triggers judged on their properties, not their accuracy:** supply, timing, resolution speed for a given shape,
  clustering, how differently timed from other components, hand-executable. Each is judged by what it adds to the whole
  design.
- **The side rule** (part of every design; **ruled, E-221, O-4**). **The coin is the evaluation's device, not the
  playbook's** (section 5). In the playbook each design's side comes from **its own trigger**, held by **the
  no-harm floor** against the coin on the real path (CHARTER 3.5; E-221, E-230):
  its composite on the search years is not below the coin side's by more than the margin pinned in section 7
  (the no-harm margin), decided at the point estimate over the search-year coin role's deciding indices, paired on the same fills, as O-5 rules for
  limits (E-230) -- never by a test that fails only on evidence of harm; its held-out reading is reported beside,
  never judged. **A trigger whose side fails the
  no-harm floor offers no playbook side; that design is not carried.** The floor is read on the search years,
  before the finalists' row; a failing design is removed from the finalists' list then, so the fixed sequence's order
  is never set after a held-out read (section 10 (c)). A resting trigger traded as its real order clears the same
  floor. **The playbook side rules, fixed here** (`trigger_sides.RULES`): `p14` takes `with_breakout` (the side of the
  break); `rl3` takes `fade` at every level of its kind (a limit resting at the level, against the level's role). These
  are fixed, not searched: under the martingale-outcome reading a side moves no deciding outcome, so searching it would
  only choose a direction on the real path, which the no-harm floor exists to bound. **Accounts alternate:** different
  accounts take different trades at different moments, the rotation a lever
  of the search, because copying one trade to every account correlates their failures and defeats the fee asymmetry.
  **The one hard rule** (conduct tier 1): no two of the user's accounts or firms hold opposite positions at once --
  while any position is open a new trade takes that position's side or is skipped, and the scheduler refuses a
  same-moment opposite side (R-12: a conduct rule, not a lever; its supply cost reported with (37)). In the evaluation
  the side coin's key carries no account or firm index and **the per-start keying is kept** (section 8); that means
  only the refusal above, never that every account copies every trade.
- **The output is a playbook:** each finalist written as a one-page set of rules (triggers, side rule, shapes, account
  policy, schedule) with the exact alert format, hand-executable, by `extended/playbook.py` through the playbook part.
- **The contract fit (CHARTER section 4), item by item:**

  | item | the search's answer |
  |---|---|
  | stops in the stop band, above the cost floor (`vendor/stage2/results/stop_band.csv`) | S1's lower cap is the registered stand-aside floor and its upper cap the room arithmetic (`lever_space.stop_caps`); the gate checks every scheduled trade against the band and refuses a design with any trade outside it |
  | at least L minutes from alert to order, by hand; a resting ticket live L minutes after it is published | T4 for `p14` (5, 3 or 2 minutes); RL3's tickets published at 08:30 CT and live at 09:00 CT; the schedule builder refuses an order earlier than its alert plus L |
  | one position at a time per firm, five minutes flat between trades | Stage 2 D-429's strict rule through the router (`extended/router.py`) and the firm path; the per-unit overlap count on the taken-trade log must be zero, refusing |
  | every trade resolving: at most 5 % reach the 15:10 CT flatten (D-212 as D-308 raised it); no time stops | the gate's resolution check (section 6) on every design, overall and in every search year; S6 dropped |
  | realised risk within 10 % on at least 90 % of trades, in its allowance-capped form (E-022 (1), E-032) | the gate's realised-risk check on every design |
  | no entry before 07:35:00 CT on a BLS 08:30 release day; FOMC days out | the void calendar, `extended/day_calendar.py` (Q-166), in the schedule builder, from the BLS 08:30 ET release days (`vendor/stage2/data/release_days_0830_2009_2025.csv`) and the scheduled FOMC statement days (`vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv`) as `features.load_calendars` reads them; **the schedule builder reads `day_calendar.day_context` for designs and baselines alike**, pairing with H4's coin source, and the share of offers removed for a research-only reason (`day_calendar.RESEARCH_ONLY`, known only after the alert) is reported beside per reading class; the playbook's live alerts use `alert_context` |
  | no entry and no fill inside a verified news window; a position open at its start flattened (E-202 (2)(a), E-200 R-1); limits cancelled at its start; the closed 08:30-08:59 window for every source (E-223 M-8); **the one news-flatten convention** (E-223 M-4), every source: the flatten books at the adverse extreme of the window's first bar less two ticks, or at the position's resting stop instead if that extreme reaches it (as a stop exit) -- the as-walked and as-traded readings' convention; the deciding reading takes R-10's stopped walk to the window's start | **no verified news window reaches Topstep's accounts** (`tier1_news_events_restriction` and `economic_releases_list` are `changed`, `extended/modes_news.py` reaches no Topstep account), so R-10's news-window row arises for none; what holds is the BLS and FOMC exclusions of the row above, which are Topstep's enforcement here, the closed window `triggers.CLOSED_FIRST` to `CLOSED_LAST` refused at sampling (`Space.check`'s `session` class), and E-223 M-4's convention in the walk; the deciding reading by R-10 (section 5) |
  | **conduct tier 1** (no hedging across accounts or firms, no simulator-fill exploitation, no maximum size into major news, no trade copied across accounts, nothing that conceals a pattern) | one firm; one position at a time, each trade on one account, so none is copied and no two are open at once; the space's fixed `overlap` (`refused`) and `firms` (one); S7 dropped; a flip trade never at the full allowance (RD-05 2.6); nothing in any design conceals a pattern. **No maximum size into major news** (`prohibited_strategy_max_size_into_major_news`, whose page names no list): **the declared reading of "a scheduled major news event"** is every BLS 08:30 ET release in `vendor/stage2/data/release_days_0830_2009_2025.csv` at its release minute (a stricter reading than `features.BLS_MAJOR_RELEASES`), every scheduled FOMC statement in `vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv` at its statement minute, and BEA's GDP releases, whose calendar exists in neither this repository nor the vendored tree and is a build item before the pin (the head's item 7), never invented here; **its check** is a refusing count on the taken-trade log -- no position at the full maximum position size of its account's state open across any declared release minute, computed from the calendars, not from the accounts a rule reaches -- built with a planted violation that fails it |
  | conduct tier 2 modelled and off in the base case (D-289); tier 3 priced, 0 % denial in the verdict | the verdict settings `wave42.VERDICT` (0 % denial, the placement off, the Focused Trader Program off); the denial ladder beside (section 11) |
  | firm rules only verified (section 1) | every key in section 1's table through the loader, which refuses any key not `verified` |
  | no automated or API order entry; designs for one user's own accounts | the output is a hand-executable playbook; nothing here places an order |

## 5. The zero-edge convention

- **The fill** -- its time, price and supply -- comes from the real order.
- **Direction removed:** after the fill the path is reflected about the fill price with probability one half, by the
  coin of the declared seed (for a market entry, exactly a fair coin choosing the side; for a resting entry, the
  reflection, since a coin on the resting side does not remove direction, E-203 B-1, E-204 NB-1). RL3's same-bar pair
  is one realisable case (E-204).
- **The martingale-outcome reading decides** (every deciding reading of sections 8-10, except the no-harm and
  as-traded floors, read on the real path, N-1). Each trade's outcome is redrawn at the driftless first-exit odds of
  its own bracket, keyed by the declared seed; fills, timing, costs and resolution stay as run.
- **The race against the nearer barrier, with its exit cost:** adopted as the template's section 5 states it, word for
  word in force through its pinned hash (E-284), and as the firm path builds it (`extended/three_way_firm.py`,
  `extended/three_way_redraw.py`, E-281): l the stop, g the target as placed (a rule's profit level converted to net
  ticks after the target-side cost, g' = min(g, level / (tick value x contracts) + x_target)), c the room after the
  entry cost, x_stop and x_target the exit costs of `vendor/stage2/config/fills.yaml`'s profile in use; **the loss
  barrier L = min(l, c - x_stop), fractional, never rounded** (E-237); p = L / (L + g); a win gains g and pays
  x_target, a loss loses L and pays x_stop; so the clip never binds and every trade's gross expectation is exactly zero
  and its net exactly minus its costs, at every cushion. **What happens at the fill is decided at the fill** by R-10's
  L_fill; **there is no "not taken" state.** `adapter.BinaryDraw` is the cost-free special case (x = 0), held on the
  same uniforms by the firm path's identity (H4's I-3), the uniforms drawn from the coin field keyed per unit and
  moment, never from BinaryDraw's sequential stream.
- **m-2 (E-210): trades open at once on one instrument are redrawn jointly, from one seeded driftless path.** **This
  search: overlap refused.** The joint law of the design note's 1.6 is not adopted here, so the runner refuses any
  design that can hold two positions of the user at once (two accounts in a position at once, a second component
  entering while the first is open) and the sampler refuses to propose one: the space fixes `overlap` at `refused` and `firms` at one
  (`search_space.from_lever_space`), one position at a time across the firm holds by the strict rule, and the per-unit
  overlap count on the taken-trade log must be zero, refusing. Overlap across different underlyings does not arise
  (one market).
- **m-3 (E-210): a redrawn loss carries the run's stop-fill convention**, as the template states it: a loss booked as a
  stop exit at `stop_slippage_ticks` with the per-contract costs at the stop, a win at the target as a limit
  (`target_slippage_ticks`), a loss at the cushion as a stop; the same for designs and baselines; the +1 and +2 tick
  stresses (measure 29) add to it.
- **R-10: the redraw for a trade that ends at a time limit** -- **the house form, unreplaced**, as the template's
  section 5 states it (L_fill = min(l, c - max(x_stop, x_flat)) decided at the fill, the at-the-fill failure where the
  floor's room binds, the stopped day where the daily loss limit's binds, the refused daily loss limit at construction,
  the out-of-room end at a zero-contract slot, the per-trade lattice step, the exhaustive terminal-state map
  `three_way_redraw.EXIT_LAW`, the stopped walk with its driftless two-point last sub-step and its both-barriers rule,
  and the fill-time law beside). Its declared inputs:
  - **`EPS`** (the tolerance of the L_fill > 0 comparison, in dollars): `three_way_journey.EPS`, cited by key, as H4
    declares it (U-1);
  - **`WALK_MAX`** (the walk's step limit): `three_way_journey.WALK_MAX`, cited by key (U-1);
  - **sigma, the declared volatility estimator** (its window and unit): H4's, section 7's volatility row of
    `prereg/H4_rebaseline.md` (LF sha256 above): the standard deviation of one-minute close-to-close changes, in ticks
    per root minute, over the last 60 bars closed at or before the alert, across session breaks with the break's gap
    return excluded; an alert with fewer than two changes behind it takes its trade out of supply, counted beside; the
    scramble test is a build test.
  - **No breakeven move** for any design (S7 dropped), so no design trade takes H4's move law; the baselines keep it as
    H4 runs them (B-I3).
  - **Their size read before the pin:** the light synthetic experiment of the full read's m-8 (three arms: the B-2
    rule only, with the out-of-room rule, the vendored engine's handling) is a condition of the pin (section 14 step
    2), its result file or exploratory record cited in the pinning row; it chooses no lever.
- **The pair rule** (`feature-rules` section 3; the Phase 0 audit's D-1, D-13). Wherever a reading compares a resting
  entry with its reflection on the real path -- the no-harm floor, the as-traded floor, the path-structure gap -- a
  pair whose fill bar touches either leg's stop or target **contributes zero lift**: both legs are booked at the
  as-walked leg's settled outcome for that pair, each with its own (equal) costs, so the pair's difference is exactly
  zero by construction. The pair is counted, its share reported and **capped at 5 % of each resting component's fills
  on the search years** (F-02's and RL3's K5 cap, D-212's ceiling by analogy; it buys measurability, not an error
  rate): a design whose resting component exceeds it fails the gate, counted, its measures not read. Without it the
  stop-first fill-bar rule favours the real resting side by construction.
- **Beside, never credited:** the as-walked (reflected) result and its gap from the martingale-outcome result, the
  design's **path-structure edge**; the **as-traded** result (the real resting side, unreflected) with E-204's
  decomposition, as a stress.
- **The oracles** (CHARTER section 4, amended E-210): stage one's zero-edge ceilings are read on the martingale-outcome
  reading, where an output outside them is an engine error; an as-walked result outside them is the path-structure
  edge, reported beside, never "fixed". The cost-aware oracle (the loss barrier min(l, c - x_stop), net = -(costs), no
  exit past the floor) runs on every audited design's trade log.

## 6. The survey, the surrogate and the rounds

*Every number here is fixed before the survey and never extended after a look.*

- **The gates read before any outcome**, per surveyed design, each refusing (the gate part, its declared keys in the
  survey-spec block): supply (trades per session in every search year, counted; a design with no scheduled trade in
  some search year cannot be read there and fails; the supply floor that ranks is W42-R2's `taken_mean_p10` limit),
  resolution (the unresolved share at most 5 % overall and in every year, D-212), realised risk (D-212,
  D-308), the stop band (section 4), and the pair rule's cap (section 5). **A point the route refuses** (`survey_route.RouteRefused`: a refused source, a missing side rule or RL3 parameter, a T7 other than `off`, a point the space refuses) **is recorded as a refused cell with its reason and never scored**: it is never given an infeasible reading, so it never reaches the surrogate or a limit's surrogate as one (the route's red team, m-3). A design that fails a gate is counted and its
  measures are not read.
- **The sizes are declared here and in the survey-spec block, final at the hash** (the form read's B-5; never left to
  the pinning row): the survey's 512 designs, 8 rounds of 32, the screen's 4 seed indices on every 4th start, the
  deciding size's 16 seed indices on every start, the 64 re-read indices, the promotion of 32 and the 4 candidates.
  **They are sized from compute cost only, never from any reading of an outcome.** H4-B's measured cost per unit is
  not yet a collected file on master, so the cost is declared as a formula, printed by the build from H4-B's collected
  manifests in the pin row's citation of the build: the survey's wall-clock T = c U / w, where c is the measured
  seconds of one unit (one start and one seed index) of one design with its four paired baselines and every arm the
  reading carries, w = 2 workers (H4's count, E-294 (2)), and U the units read -- the screen's (512 plus 4 times 32
  readings, each on 4 seed indices times a quarter of the starts), the deciding size's (32 promoted plus 4 times 32
  readings, each on 16 seed indices times every start), and the re-reads' (the 4 candidates, their at most 4
  five-minute twins and their plateau neighbours, at most 4 times k_max, each on 64 indices times every start). The
  survey runs in clean parts split by disjoint start ranges, each part within the house's 8 h cap at 2 workers (E-287's
  cut rule, E-288 (3)). **The sizes never move after the hash:** were T unacceptable, the search is re-declared before
  its pin, never re-sized at the pin row.
- **The screen and the deciding size** (E-292 (4), E-297 (2); neither the template nor the survey runner fixes them:
  the engine reads every survey and round cell on one ledger protocol, and the finalists on the re-read seeds,
  `search_space.CellLedger.protocol_for`). Declared before any read, every index a seed index of the search-year coin
  role (section 12), **the three ranges disjoint** (the red team's B-3: a promoted cell must not keep its screen luck):
  - **the screen size**, for the survey and rounds 1 to 4: the seed indices **80 to 83** (4 indices of its own, above
    the re-read range) and **every 4th start** of the pinned search calendar (`results/search_calendar.csv`), its
    starts taken in calendar order from the first (start stride 4, offset 0), each start read at its own horizons on
    W42-R1's sessions-left rule, which W42-R2 carries; starts may overlap the deciding size's, since the history is
    common to every design and only the coin draws carry selection luck;
  - **the deciding size**, for rounds 5 to 8, the promotion's re-read and every finalist rule: the seed indices **0 to
    15** (16 indices) and **every start** (stride 1); the candidates' re-read stays at the 64 re-read indices **16 to
    79**, every start;
  - **the promotion**, between round 4 and round 5: the **32** screened cells with the best screen composite among
    those passing the floors on their screen reading (section 7's floors) are re-read at the deciding size, counted as
    readings of existing cells, never new designs. **Its edge cases:** fewer than 32 passers promote every passer;
    none closes the search by `every-design-failed-a-gate` (the held-out template's closed list); the rounds 5 to 8
    surrogate needs at least one deciding-size reading, which one promoted cell gives, and is fitted on those readings
    only;
  - **what each size feeds:** the surrogate of rounds 1 to 4 is fitted on screen readings only; the surrogate of rounds
    5 to 8 on deciding-size readings only (the promoted cells and rounds 5 to 8); **the finalist candidates are ranked
    only among deciding-size readings**, so no screen reading is ever compared with a deciding one, and no deciding
    reading reuses a screen index. **The floors that decide** -- the no-harm floor, the `not_paid_within_B` limit and the
    do-nothing floor -- **are applied on the deciding-size reading before ranking** (section 7); the screen reading's
    floors decide only the promotion;
  - **the precision each size gives**, declared now as formulas on calendar counts and a priori bounds, never on a
    reading: for two designs read paired on n units (a unit a start and a seed index), every per-unit composite
    difference lies in [-1, 1], so its coin-noise standard deviation sigma is at most one, and the smallest composite
    difference resolvable at power `wave42.POWER_TARGET` (W42-R1's, carried unchanged by W42-R2) by a one-sided
    comparison at level 0.05 is MDE(n) = (z_0.95 + z_power) sigma / sqrt(n). The screen's n is 4 seed indices times a
    quarter of the starts, the deciding size's 16 times every start, so **the screen's MDE is four times the deciding
    size's** at every horizon (the square root of 16 over 1, against 4 over 4). **The keep rule's power** (section 7's
    point-estimate rule) at a true gap of delta\* against one baseline is Phi(delta\* sqrt(n_r) / sigma), n_r the
    re-read's 64 indices times every start, and against the four at least one less the sum of the four misses. The
    build prints both MDEs and the keep rule's power at sigma = 1 (the a priori bound) and at H4-B's search-year sigma
    (W42-R2's output, `power`) from the pinned calendar's E_h counts, beside delta\*, in the pinning row's citation of
    the build; a screen that cannot resolve delta\* only screens, and the deciding size, not the screen, ranks the
    candidates;
  - **a build requirement** (the head's item 3): the engine and the runner read a cell on the protocol of its role (the
    screen's for the survey and rounds 1 to 4, the deciding one after), each protocol bound in the declaration's
    protocol sha256; the survey-spec block's `screen` key is refused by today's `survey.load_spec` (its keys are
    `survey.SPEC_KEYS` exactly). **The code points today's runner gets wrong for two sizes, each a refusing test of the
    build** (the red team's m-2): `survey._keep`'s `ctx.selection.setdefault` and `survey.finalist_candidates`'s
    `seen.setdefault` keep a cell's first reading, which is a promoted cell's screen reading (the deciding one must
    govern); `survey.run_rounds` passes every reading to `propose`, mixing the sizes; `survey.read_design`'s memo key,
    the design id and the seeds, omits the start stride; and the ledger declares one protocol, on which
    `search_space.admit_one` and `plateau.check` read.
- **The survey:** the survey size **512 designs**, a **space-filling** sample of the lever space: a scrambled Sobol
  sequence (`search_space.Sampler`, `method="sobol"`, power-of-two blocks used in order), seeded by S0 (section 12),
  on the search years only; **each design is read at the screen size** on every measure of section 1; at most
  64 x 512 = 32768 proposals, every proposal counted, the refused ones included (the engine's default cap, written
  out). The size is a power of two (the Sobol sequence's balance) near ten points a dimension of the space at this
  commit (one slot a session in five sessions, with S1's slot dimension; the build prints the dimension count beside),
  the computer-experiment rule of thumb for a Gaussian-process start.
- **The surrogate:** `extended/surrogate.py`'s Gaussian process, a **fixed procedure** named so (the red team's n-4 on
  Wave 3.4): the Matern 5/2 kernel with one length-scale a continuous lever times a categorical-overlap kernel, the
  SAAS prior (`surrogate.PRIOR_TAU`), the constant mean's prior variance (`surrogate.MEAN_VAR`), its bounds and start
  (`surrogate.BOUNDS`, `surrogate.START`) as merged at the engine commit `3452952` (E-281), and 4 restarts from S2's fit
  stream; one surrogate for the composite and one for each of W42-R2's seven limits, every one fitted through the one
  door (`search_space.admit`). It predicts every measure the rounds need from the levers; which levers move which
  measures and where the ruin chance jumps are reported beside from its length-scales and the readings.
- **The rounds:** **8 rounds of 32 designs each**, proposed **inside the limits** by `extended/proposer.py`: expected
  improvement below the incumbent multiplied by the probability that every limit holds (`acquisition="ei"`, `xi` 0, the
  improvement's offset), the batch by the kriging believer, from a Sobol pool of 4096 points (`pool`) and 64 local
  perturbations (`local`, scale 0.05 on the unit cube, `local_scale`) around each of the 4 read designs with the lowest
  predicted composite (`centres`), seeded by S2. `kappa`, the lower confidence bound's width, and `p_feasible`, its
  feasibility threshold, are the `lcb` acquisition's: unused under `ei` and written because `proposer.RoundSpec`
  requires them. **A departure from CHARTER 3.3 (d)'s "constrained, multi-objective" form, stated** (the form read's
  m-4), as Wave 3.4's m-10 remedy allows: the composite is optimised, the seven limits are constraints by probability of
  feasibility on the same protocol, and the frontier over every measure is reported from the readings (section 11).
  **The number of rounds is fixed here and never extended after a look**; there is no stopping rule: every round runs.
  A pool with fewer valid candidates than the batch refuses its round (the budget is never shrunk after a look), and
  the survey closes with that refusal on record.
- **The protocol's horizon is 0 sessions** past its one block, which ends on the search years' last session, so no
  outcome reads past 2023-12-29; each start's own horizons come from its sessions left on the pinned calendar
  (W42-R1's rule, which W42-R2 carries).
- **The plateau rule** (CHARTER 3.3 (e)): a finalist's neighbours must also do well -- its metric and radius pinned in
  section 7.
- **The finalist order rule:** declared before the survey and pinned in section 7 (`survey.finalist_candidates` and
  `survey.choose_finalists`, with the keep rule rebuilt as the head's item 4); the list itself pinned in the lead's
  row before the held-out read (section 14).
- **Every design tried** is logged in `results/variants.jsonl` with its manifest (CHARTER 3.3 (f)), through the
  vendored `VariantCounter`, only by the clean run; the map and the ledger persist for the next firm, lever or model.
  **No held-out result** is written to either.
- **The reverse reading** (choose on the held-out years, judge on the search years) is not run before the held-out
  test; afterwards only as a described reading (CHARTER 3.6 (g)).
- **The survey-spec block** -- the survey runner's one input (`extended/survey.py`'s `load_spec`; nothing is injected,
  F-2). Its keys are `survey.SPEC_KEYS` and the `screen` key the build adds (the head's item 3). A value written
  `<...>` is one of the list at the head of this file (W42-R2's application, or the build's hashes); until each is
  filled the block is not JSON the runner accepts (`SpecRefused`), which is the refusal intended. The seeds in it are
  section 12's, by role.

```survey-spec
{
  "prereg_id": "F-XX",
  "survey": {"n": 512, "method": "sobol", "seed": 20264511, "max_proposals": 32768},
  "screen": {"seeds": [80, 81, 82, 83], "start_stride": 4, "start_offset": 0,
             "roles": ["survey", "round-1", "round-2", "round-3", "round-4"], "promote": 32},
  "rounds": {"count": 8, "seed": 20264513, "batch": 32, "pool": 4096, "acquisition": "ei", "kappa": 2.0,
             "xi": 0.0, "centres": 4, "local": 64, "local_scale": 0.05, "restarts": 4, "p_feasible": 0.5},
  "protocol": {"measure": "composite", "blocks": [["2020-01-02", "2023-12-29"]],
               "seeds": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "horizon": 0,
               "sha256": "<...> the build's: search_space.protocol_sha256 of this protocol, the re-read seeds, the screen and the seven limit measures"},
  "objective": {"rule_id": "W42-R2", "values_row": "<...> W42-R2's application row (Q-189)",
                "code_sha256": "<...> the build's: survey.objective_code_sha at the runner commit"},
  "baselines": {"names": ["naive_coin", "p14", "p15", "p16"], "seed": 20264512},
  "finalists": {"candidates": 4,
                "reread_seeds": [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                                 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
                                 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
                                 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
                "z": 2.0},
  "no_harm": {"margin": "<...> delta_star of W42-R2's output (Q-189)", "margin_row": "<...> W42-R2's application row (Q-189)"},
  "plateau": {"rule": {"steps": "<...> the build's: one sixteenth of each real lever's loaded range, one step of each integer lever, cells for each categorical",
                       "radius": 1, "tolerance_se": "<...> the build's: plateau.critical_value(0.05, 75, 64)",
                       "margin": "delta_star", "side": "worse", "min_share": 1.0, "min_neighbours": 4,
                       "min_per_lever": 1, "neighbourhood": "axes", "draws": 0},
              "seed": 20264514, "box_seed": null},
  "parts": {
    "space": {"id": "extended.survey_parts:make_space",
              "params": {"slots": {"evening": 1, "asia": 1, "london": 1, "ny_am": 1, "ny_pm": 1},
                         "sources": {"evening": ["p14"], "asia": ["p14"], "london": ["p14"], "ny_am": ["p14", "rl3"], "ny_pm": ["p14"]},
                         "held": {"T7": "off", "A1": "steady", "A2": "steady"}, "design_wide": ["S2"]},
              "data": "<...> the build's: results/s1_range.csv and results/t7_forecast.csv by sha256",
              "sha256": "<...> the build's", "digest": "<...> the build's"},
    "gate": {"id": "extended.survey_parts:make_gate", "params": {"pair_cap": 0.05},
             "keys": ["supply", "unresolved_share", "realised_risk", "stop_band", "pair_share"],
             "data": "<...> the build's: vendor/stage2/results/stop_band.csv by sha256", "sha256": "<...> the build's"},
    "schedule_builder": {"id": "extended.survey_parts:make_schedule", "params": {},
                         "data": "<...> the build's", "sha256": "<...> the build's"},
    "runner": {"id": "extended.survey_parts:make_runner",
               "params": {"coin_role": "survey_topstep_coins", "side_rules": {"p14": "with_breakout", "rl3": "fade"},
                          "source_params": {"rl3": {"kind": "pd", "cutoff_ct": "14:30"}}},
               "data": "<...> the build's: results/search_calendar.csv and results/h4_registered_constants.csv by sha256",
               "sha256": "<...> the build's"},
    "playbook": {"id": "extended.survey_parts:make_playbook", "params": {}, "data": "<...> the build's",
                 "sha256": "<...> the build's"},
    "engine": {"id": "extended.search_space", "sha256": "<...> the build's: survey.engine_sha at the runner commit"}
  }
}
```

## 7. The pinning row: every input of 3.8 and 3.9, in one row, before the survey

*Every input below is set from **the search years only** (H4's search-year outputs through W42-R2, the lever table, the
verified rules), in one lead's row, **before the survey** runs; none is changed after a search-year result except by
re-declaring the search. This section is **never pinned alone**: the whole renamed file is frozen by its LF sha256 at
the pin (section 14), with this table filled, and every later row cites that one hash. A constant cited as
`wave42.<NAME>` is W42-R1's, carried unchanged by W42-R2 (not in `wave42_r2.OVERRIDES`).*

| input | value | its direction or form | source (search years only) and row |
|---|---|---|---|
| **the limits**, each a floor or a ceiling, and any workload ceiling | <...> (awaiting W42-R2's application, Q-189: the output's `limits`, each limit's value). The seven are W42-R2's (`wave42_r2.LIMITS`), by name: `not_paid_within_B` (ceiling, mean, horizon 126), `peak_oop_12_months_p90` (ceiling, p90, 252), `first_payout_days_p50` (ceiling, p50, 126), `orders_max_p90` and `accounts_max_p90` (the workload ceilings, p90, 126), `taken_mean_p10` (the supply floor, p10, 126), and `net_month_12_p50` (measure (12) at month 12, a floor, p50, 252) | each limit's direction as W42-R2 section 3.1 and W42-R1 section 6 write it; the point estimate governs (E-221, the lead's O-5 ruling, E-230): a design passes the limit when its point estimate is inside it, fails it when outside, never a second margin; the one-sided check's level, reported beside each limit, never deciding: `wave42.LIMIT_CHECK_LEVEL` | the lead's, from H4's search-year results by a rule declared before H4 is read (E-221): W42-R2 (E-296), applied once (Q-189) |
| **the bankroll budgets** of measure (24) | <...> (awaiting W42-R2's application, Q-189: the output's `budgets`, B\* its `primary`) | in fee units of `subscription_fee`, rounded up to the fee lattice (W42-R1 section 3, carried by W42-R2); B\* the budget of P_B, ruin and `not_paid_within_B` | the lead's, as the limits (E-221): W42-R2 |
| the **dimension** definitions, their normalisers or loadings, and their **caps** (lo, hi) with the cap margin | the six dimensions of W42-R1 section 4.1 (money, bankroll, speed, cost, steady, ruin), carried by W42-R2, the caps' rule of its 4.2 (`wave42.CAP_QUANTILES`, `wave42.CAP_MARGIN`); the caps' values <...> (awaiting W42-R2's application, Q-189: the output's `dimensions`, each `lo` and `hi`) | the composite is clipped to [0, 1] (the design note's 1.3) | H4's measure-structure analysis (Wave 4.1) through W42-R2 |
| **the weights** | <...> (awaiting W42-R2's application, Q-189: the output's `weights`; equal over the kept dimensions by W42-R1 section 4.3, carried by W42-R2) | non-negative, summing to one | the lead's, from H4's search-year results by a rule declared before H4 is read (E-221): W42-R2 |
| **the composite** or **the fallback** -- **one, never both** | <...> (awaiting W42-R2's application, Q-189: the output's `form`, `composite` or `fallback`, decided by W42-R1 section 4.4's rule, carried by W42-R2, before the survey) | the fallback is P under the bankroll stop (`P_B`, MEASURES.md section 2), pinned in place of the composite, never tried after it | W42-R2 |
| **the size that matters** (O-3) and the **power target** | delta\* <...> (awaiting W42-R2's application, Q-189: the output's `delta_star`); the power target `wave42.POWER_TARGET` (`family_stats.MDL_POWER`) | on the composite's scale: the smallest difference that would change which design a user should run, with the power reported (the output's `power`) | the lead's, from the baselines' search-year results (E-221): W42-R2 |
| the **regimes** (the volatility threshold's rule) and **most years** (n_Y) with the minimum group size | regimes: v(t) the start's `trail20_range_pts` (the lever table's S1 unit, RD-04's), read on bars closed before the start's first decision moment; **v\* the median of v over the search-year starts of the pinned search calendar**, computed by the build from the search years and printed in the pinning row's citation of the build, never read on a held-out bar; most years: **n_Y = all of Y_ok** and **n_min = 21** (a month of starts, the design note's 3.4 proposal) | (Y) every start-year group with at least n_min complete starts positive; (R) every regime with at least n_min complete starts positive; a condition of stated size at least one half labelled vacuous | a rule fixed in advance on the search years (CHARTER 3.6 (f) (ii)); the design note 3.4 |
| the **finalist order rule** and the **plateau rule** (metric, radius) | **the order rule:** the floors first (`survey.passes_floors`: the no-harm floor, the `not_paid_within_B` limit, the do-nothing floor, in that order, on each cell's deciding-size reading; a cell failing one recorded and never ranked); then the deciding-size cells (the promoted cells and rounds 5 to 8; never a screen reading, section 6) by their selection composite, best first, ties by cell id; the first 4 are candidates; each re-read on the 64 fresh re-read seed indices and **kept only if its re-read point estimate beats each baseline on the composite** (CHARTER 2's convention: the point estimate governs; the one-sided check of the gap, at z = `wave42.RESOLVE_Z`, printed beside and never deciding; the held-out test, not the search, bounds coin luck), every limit's re-read point estimate inside, both floors again, and the plateau accepting it; **the finalists are the kept candidates in their selection order**. The keep rule replaces today's `survey.beats_baselines` (delta\* plus about two standard errors, the red team's B-2), rebuilt before the pin (the head's item 4). **The plateau rule:** `extended/plateau.py`'s paired re-read form, the axes neighbourhood at radius one step (one sixteenth of a real lever's loaded range, one step of an integer lever, every other cell of a categorical), every active lever stepped; side `worse`; margin delta\*; a neighbour holds when its z is at most `plateau.critical_value(0.05, 75, 64)`, where **k_max = 75**, the most neighbours a design of this space can have (the account and shape levers left searched -- A1 and A2 held -- and the design-wide S2 giving 24 neighbours, four `p14`-only slots giving 10 each, the NY AM slot 11 with its second source: 24 + 4 x 10 + 11 = 75; the build recomputes it from the loaded space with S2 design-wide and A1 and A2 held, and refuses another value); accepted when every neighbour read holds, at least 4 are read and every steppable lever has one; **the build prints** the tolerance, `size_bound` and the plateau's power against a spike of twice delta\* at these 64 indices (the red team's m-9) | the order is fixed by this rule before the survey and pinned in the finalists' row before any held-out read | the survey runner (E-281) and Wave 3.4's plateau check (E-251, E-281) |
| **the gate's quantile** and the **minimum count of held-out starts** complete over its horizon | the quantile **0.05** over coin seeds (D-145's one-sided 95 % form carried); the minimum **21** held-out starts complete over D-145's horizon of 504 sessions (n_min's calendar rule) | over coin seeds on the held-out years; the search years' history-block reading beside, as a consistency condition (CHARTER 3.8 (c); E-221, O-6) | declared here; the design note's 4.4; Stage 2 D-145 |
| the **no-harm margin** for the playbook's trigger sides (E-221) and for as-traded resting triggers (one margin for both, unless two are named) | **one margin for both: delta\***, so its value is <...> (awaiting W42-R2's application, Q-189: the output's `delta_star`) | a design's trigger-side (or as-traded) composite on the search years not below its coin-side (reflected) composite by more than the margin, at the point estimate over the search-year coin role's deciding indices (`survey.no_harm`) | the lead's (E-221), ruled delta\* (E-297 (2)): a side worse by less than a difference a user would act on does no harm a user would see |
| **the do-nothing floor** (E-255) | W42-R1's do-nothing composite and `wave42.DO_NOTHING_EPS`, carried unchanged by W42-R2, at W42-R2's pinning row; its value <...> (awaiting W42-R2's application, Q-189: the output's `null_journeys`, its `floor`) | a design's search-year composite on its deciding-size reading above it by more than `DO_NOTHING_EPS`, applied before ranking (and on the screen reading for the promotion only); a design not above it is no finalist; the finalist's held-out composite above it by the same margin at the verdict | E-255; W42-R2 at its pinning row |
| **the L values** in the lever space | 5, 3 and 2 minutes for `p14`; one latency-free cell for `rl3` | five the reference; three and two counted | E-202 (2)(c) |
| the deciding bound's form, J (seed sets) and m (seeds per set), and the seed keying | **2.2 (a)**, McDiarmid's bound over every start-seed term, which admits W42-R2's composite and its fallback by construction (each dimension an unconditional mean of a clipped per-unit value over its E_h, W42-R1 section 4.1); **J = `wave42.TEST_SEEDS`**; m does not arise under 2.2 (a) (each seed's units are the terms); a composite with a dimension 2.2 (a) does not admit is refused, never switched to 2.2 (b); the keying is the design note's choice 3 (section 8) | by the composite's form (section 8) | the design note's 2.2, 2.5; W42-R1 section 5.3, carried by W42-R2 |

## 8. The three-way test

The design is the three-way test's design note, `docs/plans/THREE_WAY_TEST_design.md` at `181eb44` (Q-153, after
three red-team reads; merged, E-213), in the text H3 copies (its LF sha256 as `prereg/H3_three_way.md` records it,
E-279). **This declaration departs from it at one point only:** its 1.6 (the joint law for overlapping positions) is not
adopted, because this search refuses overlap (section 5).

- **(i) The coin-seed leg carries the level** (E-208). Each finalist and each baseline run **paired** -- the same seeds,
  the same start days, the same keying -- on the held-out years; the replicates are disjoint coin-seed sets on the
  fixed held-out history. The hypothesis, per baseline: on the held-out years the design beats it in expectation over
  coin draws. The statistic, fixed here: **the 2.2 (a) lower limit**, LB = Delta-hat - sqrt(ln(1/alpha) x (the sum of
  c_u^2 over every unit) / 2), McDiarmid's bounded differences over every start-seed term of the composite (or the
  fallback), H0 rejected when LB > 0; no t decides. **c_u**, the design note's 2.2 (a) item 4: changing one unit u's
  coin field moves the composite difference by at most c_u = the sum over the dimensions d of 1[u in E_{h_d}] times
  w_d times 2 r_d / ((hi_d - lo_d) times J times |E_{h_d}|), w_d the pinned weight, [lo_d, hi_d] the pinned caps, r_d
  the per-unit range (one for the clipped z) and |E_{h_d}| the held-out complete starts at the dimension's horizon; for
  the fallback, c_u = 2 / (J |E_63|). **The level bounds coin luck given the held-out history; it does
  not bound a favourable history**: the history null's false-pass rate is read for that (section 9).
- **(ii) The time leg, a declared consistency condition**, not a test at the level: the difference holds in **most
  years** (n_Y, section 7) and in both volatility regimes (threshold from the search years), with start-year groups and
  regimes as the design note's 3.4 writes them; a regime absent from the held-out years is reported beside. Each
  condition's stated size, with the overlap counted, is printed beside the verdict.
- **(iii) The held-out leg:** (i) and (ii) read on the held-out years only; the runner refuses any other start or
  outcome session (a scope condition).
- **The seed keying** (the design note's 1.5, choice 3): every random element of a journey a fixed function of the coin
  field; keys of fixed length per kind (`three_way_keys.seed_key`); the side coin's key carries no account and no firm
  index; each start its own draws; this search's parts carry part ids of their own in `extended/three_way_seeds.py`.
  J fixed here (section 7) and never extended after the read.
- The coin-seed spread is reported: it is the user's payout variance.

## 9. Calibration and the power gate

*The deciding calibration and the power gate run after this whole file is pinned (section 14) and before the go row;
they read only what this file fixed. H3's earlier runs are design checks only.*

- **Their inputs, fixed in this file before the pin:** the seeds: **H3's deciding block, cited with its owner** -- the
  roles `h3d_histories`, `h3d_coins`, `h3d2_history_null` and `h3d3_plants` of `extended/three_way_seeds.py` (H3's
  declaration, E-279, section 15), used only as H3-D's declaration registers them; the R-10 estimator, `EPS` and
  `WALK_MAX` (section 5); the deciding statistic (section 8); J and m (section 7); the plants' grid, the synthetic
  generator and its fitted parameters' source (search years only, H4 read only through W42-R2's output), and the
  replicate counts: **H3-D's, by its declaration** <...> (**the H3-D placeholder**, awaiting H3-D's declaration, `prereg/H3_three_way_deciding.md`, and its pinning row: its LF
  sha256 cited here before this file's pin). Nothing of them is chosen after a calibration or gate output.
- **Their outputs, pinned afterwards in E-115's calibration-plan form:** each run's result file with its manifest, and
  a record `docs/calibration/<F-NN>_calibration.md` citing those files' sha256 and the verdict, pinned by its own
  sha256 in a decision row (`tests/test_declarations_fixed.py` holds it). A failed calibration or gate is that
  record's verdict; it is never re-run with another seed. **A declaration that follows one closed by a failed
  calibration or power gate cites that record, reports it beside, and uses a fresh seed block**; a failed seed block
  is never reused. **A failed limit clause or power gate is never a free retry** (M-5 (c);
  E-258 (the lead's CHARTER 3.7 reading row)): W42-R2's limits, bankroll budgets, weights and size that matters are
  never changed for any search of the line -- every search, of any firm, whose section 7 applies W42-R2 -- after any
  calibration or gate that read them; a defect found in them goes through the failure protocol as a defect on record,
  and a corrected rule is a new rule under a new row whose searches never enter this F-HT. A successor search inherits
  them unchanged, changes only what the failure's diagnosis names, citing the record, with a fresh seed block, and
  never enters this F-HT (its candidates are tested only on data this line has never read, a later purchase, under its
  own k); every closed attempt of the line is counted and printed beside the verdict. **W42-R2 replaced W42-R1 before
  any calibration or gate read W42-R1's values** (E-296: W42-R1 is never applied), so M-5 (c)'s "a corrected rule ...
  whose searches never enter this F-HT" does not reach this search, whose membership is unaffected; M-5 (c) binds
  W42-R2's limits, budgets, weights and delta\* from here.
- **The whole pinned rule is calibrated as a whole** (E-007 (f)): the composite or the fallback, the limit checks, the
  time leg's conditions and the floors, all on the martingale-outcome reading.
- **Same-design nulls:** a design against its **antithetic twin** (every coin draw u replaced by 1 - u, for the
  reflection and the redraw alike), and the same design on two **disjoint seed sets**. The rule rejects them no more
  often than its level.
- **The history null:** distinct designs equal in expectation across histories, unequal on any one -- **the design
  note's 2.7 construction**: two components on synthetic paths carrying NQ's dependence, exchangeable under the
  generator's symmetry (the same law in two sessions, or mirrored schedules); the whole rule's pass rate on them
  across synthetic and history-block-resampled histories is **the history-level false-pass rate**, printed beside
  every verdict. History blocks are at least as long as the composite's longest horizon (252 sessions; 504 for the
  long-run gate's reading).
- **The power gate**, before the go row: the whole pass line's power at the level it assumes, **the do-nothing floor
  included: a planted design not above the floor, at the search-year deciding-size screen or at the held-out verdict (section 10
  (c)'s two points), counts as a fail and never leaves the count** (E-255; section 7; B-1; n6)
  -- F-HT's level 0.05 / (k (k + 1)) with k = 13 next, the
  power at every k from 14 to 20 reported beside, so a re-statement at another k is a lookup, never a new run (m-e;
  K-2), and a k beyond 20 needs a re-statement run of the gate, from the go row's runner commit at the gate's pinned
  seeds -- a re-statement only, closing nothing, exit (B) citing it; without it the pass line is refused (n-c) -- on
  synthetic paths carrying NQ's dependence, with design pairs drawn from H4's baselines and from synthetic plants, at
  a planted improvement of **the size that matters** (the lead's, from the baselines' search-year results; E-221,
  O-3), at the **power target**, under the horizon embargo. **The gate simulates the whole selection pipeline** (the
  red team's B-2; the head's item 9): on synthetic worlds, the planted design (the best baseline plus delta\*) among
  synthetic designs equal to the best baseline in expectation, at the survey's declared counts, goes through every
  declared search-year stage -- the screen at its size with its floors, the promotion, the deciding size, the top-4
  cut, the point-estimate keep rule and the plateau -- and then the held-out pass line; **the power reported is that
  whole pipeline's**, per stage and in all, no stage left unmodelled, and the go row requires the power target on it.
  In the same run, on the same route, a design equal to the best baseline on every limit passes every limit check, in
  the form in force, with at least the power target (E-015's condition); and
  **the count of held-out starts complete over D-145's horizon** reaches its pinned minimum. If any fails, **the
  search goes no further** -- no go row, no survey: CHARTER 3.7's "the search does not pin" read on this template's
  order, the file closed by a row, its k unspent (it is assigned only at a held-out row) -- and exit (B) states the
  line's power from this gate.
- **The data decision** (E-007 (2); held, E-221): more history (QuantConnect's free NQ/ES from 2009, the operator's
  setup; or older bars bought, stated, never authorised) is not added -- the operator held the purchase. The power
  gate's result is reported with the size that matters and the power (the lead's, Wave 4.2); a purchase stays the
  operator's, never asked for after a failure.

## 10. The pass line

*A finalist passes, in its place in the fixed sequence, when (a), (b) and (c) all hold, every deciding reading the
martingale-outcome reading for the finalist and every baseline alike.*

- **(a) Limits** (E-221, the lead's O-5 ruling, E-230; it replaces E-207's limit wording).
  **The point estimate governs:** the finalist passes a limit when its point estimate is inside it, and
  fails it when the estimate is outside -- never a second margin; the limits carry none of their own. A one-sided
  check of crossing (the red team's B-10 form), at the level pinned in section 7, is reported beside each limit and
  never decides (section 11).
- **(b) Each baseline beaten:** the composite (or the pinned fallback) above **each** baseline's, an
  **intersection-union** test with every comparison at the full level of F-HT's k, by the calibrated coin-seed
  leg on the held-out years, the time leg's conditions met. Every comparison states the finalist's L and each
  baseline's L.
- **(c) The floors:** verified rules; **conduct tier 1**; CHARTER section 4's constraints, every trade resolving among
  them; **the do-nothing floor** (E-255; W42-R2 at its pinning row): on the search years on the deciding-size
  reading (section 6), before ranking and before the finalists' row, a design's composite above the do-nothing
  composite (W42-R1's, carried by W42-R2) by more than
  `DO_NOTHING_EPS` (a design not above it is no finalist), and on the held-out years at the verdict, the finalist's
  held-out composite above it by the same margin (else a fail at its place, whatever its test statistic, the held-out
  template's section 8); hand entry at least L minutes from alert to order; **the zero-edge long-run gate** -- the
  median log growth of the required bankroll over D-145's horizon (Stage 2 D-14) above zero at the pinned lower
  quantile **over coin seeds on the held-out years**, the search years' history-block reading beside as a
  consistency condition (CHARTER 3.8 (c); E-221, O-6), on the martingale-outcome reading, with fees, payout latency,
  the tier-2 consequences and D-145's tier-3 denial applied (the 0 % reading beside), on starts complete under the
  horizon embargo whose count reaches the pinned minimum; **the fill and supply stress** -- at **+1 tick** of worse
  fills (29) and with **10 % of signals missed** (28) the finalist still beats each baseline on the composite at the
  point estimate, both under the same stress, inside every limit in the form in force -- **the stress defined now**:
  the arms `worse_1` and `missed_0.1`, `three_way_journey.ArmSpec(worse_ticks=1)` and `ArmSpec(missed_q=0.10)`, exactly
  as H4's runner reads them (`scripts/h4_rebaseline.py`), the missed draw keyed apart under the coin role; **their code
  is built, reviewed and merged before the pin** in the design runner (`extended/survey_parts.py`, the head's item 5,
  brought forward from Q-224), so it is on the deciding-files line and bound at the go row; the search-year stress
  readings decide nothing, and the held-out stress floor runs this bound code; **the playbook side's no-harm
  floor** (CHARTER 3.5; E-221, E-230): the trigger side's composite on the search years not below the coin side's by
  more than the pinned margin, read before the finalists' row -- a trigger whose side fails it offers no playbook side
  and that design is not carried; **the as-traded floors** for resting triggers traded as their real orders -- **the
  no-harm floor** on the search years, and **the as-traded floor** on the held-out years (the finalist's as-traded
  composite ahead of each baseline's as-walked composite at the point estimate). The no-harm and as-traded floors are
  read on the real path, with no redraw (N-1).
- **The verdict** is read on the martingale-outcome reading, at **0 % payout denial**, the Responsible Trading
  Program's placement off and the **Focused Trader Program off** (E-008 (2); E-007 (3); Stage 2 D-234, D-289). The
  level is printed **nominal** while the held-out read ledger is not empty, and **the history-level false-pass rate**
  is printed beside it.
- **O-6, ruled (E-221): option (a).** The held-out years hold only one disjoint block of D-145's horizon, so no
  history resample can be formed on them (the design note's 4.4). The gate's quantile is therefore over coin seeds on
  the held-out years, and the search years' history-block reading is read beside it as a consistency condition: it
  is printed beside the verdict, and a failure of it is reported with the verdict.
- **The fixed sequence over finalists** (CHARTER 3.7; E-203 S-1; E-221, O-1): every firm's ordered finalists enter
  the **one joint fixed-sequence test** of section 2, in the joint order by the rule fixed in
  `prereg/TEMPLATE_heldout_test.md` (M-1) -- run under the held-out test's declaration, one declaration of
  its own (E-238), which fixes the order across the firms before the held-out read -- each finalist at the full
  level of the one k, stopping at the first failure -- one k for the joint sequence.

## 11. Beside, never deciding

- The denial ladder; the break-even denial rate (33); the placement on; the binding Focused Trader models.
- P by month; mean net; CVaR10; P under a bankroll limit; the effective sample size (E-007 (e)).
- The frontier over every measure and a menu under the limits; every measure of `docs/MEASURES.md`.
- The as-walked result and the path-structure edge, never credited; the as-traded stress of resting triggers.
- Per component: the share of time-limited trades and the fill-time law reading's gap from the deciding reading
  (section 5, R-10); the share of pairs the pair rule settled.
- The playbook trigger side's held-out reading (E-221, O-4; its search-year no-harm floor decides, section 10 (c));
  each limit's one-sided check of crossing, limit by limit, beside its point estimate, which decides -- the
  point estimate governs, never a second margin (E-221, E-230, O-5); the long-run gate's search-year history-block
  reading (E-221, O-6).
- The five-minute cell beside every finalist; the registered rows of the baselines; the coin-seed spread.
- Per year and per regime, each difference with its coin-noise standard error; each time-leg condition's stated size.
- A9's `exp_30` reading and A19's `half` reading beside every finalist, each labelled with its unstated key.
- W42-R2's `inactivity_guards` and each limit's vacuous flag, beside the candidates.
- **E-294 (4)'s reporting, deciding nothing:** every finalist and every baseline in three columns -- **contract-only**
  (the bracket's driftless odds alone, no path), **martingale-outcome** (the deciding reading) and **as-traded** (the
  real side, unreflected) -- with the gaps labelled; the as-traded gap read in both periods, the search years here and
  the held-out years under F-HT's `heldout_stress`; the **edge-sensitivity reading** beside; measures (28) and (29)'s
  stress arms on the finalists (section 10 (c)'s definition); and an **execution-fit block** on each finalist's
  playbook page. Ordering passing finalists by an as-traded statistic is not adopted here (E-294 (4)).
- W42-R2's disclosure beside the verdict: the operator and the lead saw P-14's early-look 12-month figures (section 2's
  search-year ledger), and W42-R2 chose nothing from them (its section 9).
- Not modelled, said wherever a scorecard appears: the user's time, taxes.

## 12. Seeds -- by role, found nowhere else

| seed | its role: what it draws, by draw kind |
|---|---|
| 20264510 | the unit tests of this search's build (synthetic toys only), in a part of their own |
| 20264511 | `S0`: the survey's space-filling sample (the Sobol scramble, `search_space.Sampler`) |
| 20264512 | `S1`: the search-year coin role (not the stop-width lever S1) -- the reflection coin, the race, R-10's stopped walk, missed-signal draws (28) -- one draw kind each, for every design and every baseline alike, at three disjoint ranges of seed indices: the deciding indices 0 to 15, the re-read indices 16 to 79 and the screen indices 80 to 83; one role, the pairing: the cell ledger's baseline role is begun under it because the baselines read this same coin field |
| 20264513 | `S2`: the surrogate's fitting and the round proposer's optimiser (the fit starts, the Sobol pool, the local perturbations) |
| 20264514 | `S3`: the plateau rule's ledger seed; the axes neighbourhood draws nothing |
| 20264515 | `S4`: proposed for the held-out test's coin field, which F-HT owns (it is joint over the firms, E-238) and may adopt, checking it disjoint from every member's search-year roles, this search's screen indices included; drawn by nothing in this search |
| H3's deciding roles | `S5`: the deciding calibration and the power gate -- not this block: H3's `h3d_histories`, `h3d_coins`, `h3d2_history_null`, `h3d3_plants` (owner: `prereg/H3_three_way.md`, E-279, its section 15; registered by H3-D's declaration) |
| 20264516 | `S6`: spare, drawn by nothing |
| 20264517 | spare, drawn by nothing |
| 20264518 | spare, drawn by nothing |
| 20264519 | spare, drawn by nothing |

- Every seed an integer written here before any run, **one role each**, a block never used before in Stage 2 or here,
  **found nowhere else**: checked by the house search with the licensed data excluded on 2026-11-27, before this
  file's first text was committed, word-bounded on the block's ten values: `git grep -IlwE` over every branch, remote
  and tag of the repository -- no hit; `git log --all -G` over every line added or removed in every reachable commit
  -- no hit; `grep -rIlwE --exclude-dir=.git --exclude-dir=data` over every worktree under
  `%LOCALAPPDATA%\stage2-extended-wt` (the vendored snapshot inside each) and over the main tree -- no hit; and by an
  arithmetic fold over every tracked `.py` (the design note's section 7), in `tests/test_f13_draft.py`, which also
  refuses the block's literal in any other tracked or committable file.
- **Keys of fixed length per draw kind**, passed to a counter-based generator (the design note's 1.5; numpy reads
  `default_rng([a, b])` and `default_rng([a, b, 0, 0])` as one stream); other streams are children of a named seed,
  never the seed plus an offset (E-171). The build adds this block to `extended/three_way_seeds.py` with its roles
  (the runner's coin role is named `survey_topstep_coins` in the survey-spec block, a name that does not depend on the F-number), statuses,
  `ROLE_USE` and part ids of its own, as H4's block was added, so a literal typed elsewhere cannot draw
  (`ProvenanceRefused`).
- The design and every baseline read the same keys (the pairing). A seed chosen after a result is a variant. Inherited
  seeds are used only as their owners registered them, named here with their owners: **H4's coin role `h4b_coins`**
  (owner `prereg/H4_rebaseline.md`, E-287), for the identity B-I3 only, in H4's part H4-B, reproducing H4's readings;
  **H3's deciding roles** for S5; the registered jobs' own campaign seeds (Stage 2's) wherever the vendored replays
  are run, as H4 uses them.

## 13. The count

- **One k per held-out test** at **0.05 / (k (k + 1))**; the one joint fixed-sequence test of every firm's finalists
  spends one k (E-221, O-1), taken by the held-out test's declaration, one declaration of its own (E-238), not by
  this search; the confirmation spends none (CHARTER 3.7). The program's numbering continues Stage 2's
  program U (E-001): **k = 13** is the next.
- **F-HT's k is assigned at its held-out row** (E-204): the held-out test's declaration is not counted by the
  gatekeeper's k rule until that row exists. That row comes before the held-out run, so E-204's repeat clause (another
  declaration taking a k between a run and its row) cannot arise. If another declaration takes a k first, F-HT's k is
  the next free one and each finalist's place power is re-stated at the new level before the held-out run
  (a lookup in each gate's output at k = 14 to 20, section 9) (exit (B) cites it); a k beyond 20 needs a re-statement
  run of the gate, from the go row's runner commit at the gate's pinned seeds -- a re-statement only, closing nothing,
  exit (B) citing it; without it the pass line is refused (n-c). F-HT withdrawn after its held-out row still spends
  its k (E-005 (d)); **a search's withdrawal before F-HT's held-out row spends nothing** -- no search holds a k.
- **Every design tried is counted** in `results/variants.jsonl`: the survey's N, every round's batch, every L, every
  failed-gate design. Each design is one cell carrying its components' latencies (T4 is a dimension of each slot, so
  every L tried is inside the count, recorded per active component by the cell ledger). Written as a product and a
  number:
  - the survey and the rounds: the rounds' 8 x 32 = 256 designs, so `k_cells` = 512 + 256 = 768 designs read;
  - the promotion: 32 screened cells re-read at the deciding size (readings of counted cells, no new design);
  - the five-minute twins of the candidates, read beside: at most 4 more cells;
  - the plateau checks: at most 4 candidates' neighbourhoods, each at most k_max = 75 cells (section 7), so at most
    4 x 75 = 300 cells, counted by the ledger under `plateau:<id>` as they are proposed;
  - **the bound on every design cell of this search:** 768 + 4 + 300 = 1072;
  - the survey's refused proposals: at most 64 x 512 = 32768 proposals in all, every refusal counted with its class;
  - the baselines: 4, read once each on the protocol, not designs;
  - **beside the count, the early look's one cell** (Q-213, E-291; section 1): read on the search years before this
    file's pin, exploratory, under its own seed block and its own manifest (`exploratory: true`), never a cell of this
    search's ledger; it is counted here so that the reads of this space on these years are all on record.
- The program's honesty sentence: Stage 2's programs read these bars over the whole window -- its signal search, the
  registered designs' choice and nine families of program U, each on the late block -- and this repository's RD-01 to
  RD-05, Q-17, the identity runs and the `registered_design` reads read parts of 2024-2026 for the baselines and levers
  this search inherits (section 2's ledger, row by row). F-01 (withdrawn, E-007) and F-03 (closed with its judged block
  not read, E-192) spent their ks without reading the held-out years: no line of `results/read_ledger.jsonl` is
  either's, so neither has a ledger row. The level is nominal while the ledger is not empty, and the decision is carried by one
  confirmation on unread data (section 15).

## 14. The run order -- refusals first

1. **The reads of the draft, before anything is pinned:** the scout's challenger brief (Q-150), the red team and the
   gatekeeper read the final text with section 7's values filled in; every blocking finding answered. A value filled
   in after a read is a change: the red team checks its diff, or re-reads the draft if the value bears on a blocking
   finding. After the pin a change is a new declaration.
2. **The pin**: after H4 and Wave 4.2's inputs (the lead's, E-221) are written into section 7 -- W42-R2 applied once
   to H4's collection result (Q-189) -- and after **H3-D's declaration is pinned** (section 9) and **every item of the
   head's build list is built, reviewed and merged** (E-297 (2), (3): the spec binds code hashes, and the pin row
   cites them; the list's items 1 to 10, W42-R2's merge and pin first), so that the survey-spec block's hashes can be
   filled and the deciding-files line re-checked against the built closure, the lead's row pins **the whole renamed file** by its LF sha256 (the gatekeeper renames and
   replaces `F-XX` first, then hashes). Section 7 is never pinned alone; the calibration's and gate's inputs are inside
   the frozen file. Q-158, the reader's held-out guard, is merged (E-222). **No search pins before E-258 (the lead's
   CHARTER 3.7 reading row) exists** in `DECISIONS.md`, its bolded title beginning `CHARTER's "pin" read`
   (`tests/test_design_search_template.py` refuses a pinned search that cites any other row, a bare number, or none).
   **A search pinned after the membership event is never a member of this F-HT** (H-1';
   E-257). **At most one member search per firm:** a second hash row for a firm before the membership event is
   refused at its pin, whether or not the first is closed (R-1; E-259); after the event a further search of the firm
   may pin, outside this F-HT, unless the no-new-pin bar holds. Refusing before it:
   the identities on record as holding (`identity/stage2_identity.py`, every baseline's runner identity B-I1 to B-I3,
   the search runner's own).
3. **The calibration and the power gate** (section 9), each from a **clean checkout** of a named commit
   (`scripts/run_clean.py`) under **run.lock** (one heavy run on the machine, skill `run-lock`); their outputs pinned
   in E-115's form; the data question to the operator.
4. **The go row**: its third cell's first text is the token
   `go: F-NN @ <its LF sha256> -- runner <the runner commit, 40 hex> -- <text>` (G-1, C-3; E-259), counted only
   outside any fenced block, in that exact form, at its declaration's pinned sha256, in a row strictly after that
   declaration's hash row (G-2); a go-like row that is not exactly the token is a hygiene problem that refuses every
   membership reading until a later `heldout-void: E-NNN -- <reason>` row voids it, a void of a valid row being a
   no-op, fences and voids read by the reader's own rules; so are a go row for a closed search and a second go row for
   one declaration; an HTML comment in `DECISIONS.md` is read exactly as `extended/reader.py` reads it, with no rule
   of its own (n-d) (the reader's `go_problems`, `extended/reader.py` at the run's commit (pinned at its template pin
   row), n-a); it cites the
   calibration record's hash and names, in its `runner <40 hex>` sub-form, the runner commit the calibration ran on --
   **the survey and every round run on that runner commit, bound by its sha; a change to deciding code after it is a
   new declaration** (U-1); the survey reads its own checkout's log, at a commit after the go row, bound as the reader
   binds it: HEAD descends from (or is) the runner commit, and every file of section 1's `- **The deciding files:**`
   line is byte-identical at HEAD and at the runner commit and unchanged in the working tree (the reader's `go_runner`
   and `go_row_present`; finding 2; Q-212); from here the survey may run. The lead freezes the event in the row right
   after the first counted go row, `membership: F-NN @ <its LF sha256> -- E-NNN` (the first go row's declaration, its
   pin's LF sha256, then the go row's id), which the reader enforces (F3). Under this template
   (E-258 (the lead's CHARTER 3.7 reading row)) CHARTER 3.7's "the search's pin", "does not pin" and
   "before any search is pinned", and CHARTER 3.8 (a)'s "a pinning row ... does not pin", each mean **this go row**;
   the reader's pin and every "newer than the pin" mean **the hash row** of step 2.
   A search closed by a failed calibration, limit clause or power gate gets a closing row,
   `heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>` (`prereg/TEMPLATE_heldout_test.md`'s closed list;
   `withdrawn` only before the membership event, W-1; `defect-on-record` only with a failed check on record at or
   before the membership event's commit (or the search's own declared refusal or identity), failing when run at the
   search's go-row runner commit, and the auditor's note that it cannot be fixed without changing a declared input,
   every such close counted (C-4), D-1; E-259); no search holds a k. The data question goes to the operator with the
   gate's result before the go row. Refusing at every later step: this file still hashing to its pin
   (`tests/test_declarations_fixed.py`), the go row present (checked by code: the survey runner refuses to start
   unless the reader's `go_row_present` (`extended/reader.py` at the run's commit (pinned at its template pin row))
   holds for this file's pinned sha256; it is False once this search has a finalists' or closing row), a clean
   checkout, the run lock held -- **Refusals first**, each refusing.
5. **The survey** on the search years only (one clean run, from the go row's runner commit,
   `python scripts/survey_run.py prereg/F-NN_topstep_survey.md` exactly); its gates before its measures; logged.
6. **The rounds**, each one clean run from the go row's runner commit, collected (`/collect`), never extended.
7. **The finalists' row**: the ordered finalists, their playbooks' rules and every fitted model's hash, written as a
   finalists' list file outside `prereg/` before the row, and the row in Q-158's token form,
   `heldout-finalists: F-NN @ <sha> list <sha>` -- this file's LF sha256, then the list file's -- as the first text
   of its third cell; written before any held-out read; the scout's challenger brief and the red team on the
   finalists.
8. **The held-out row** (k assigned, E-204), written as soon as, after the membership event, every member search has a
   finalists' row or a closing row (H-1'; E-257; E-221, O-1), for the held-out test's declaration --
   one declaration of its own (E-238), drafted on `prereg/TEMPLATE_heldout_test.md` (M-1), with its own F-number, pin
   and hash. It lists every member firm's finalists by each member search declaration's hash and finalists' row, in a
   joint list file that cites each search's finalists' list by its sha256; it fixes the joint order and takes the k;
   it carries the `Judged-block reads:` line; and it is the one family that reads NQ's held-out window. Its own
   finalists' row **is its held-out row** (m-3):
   `heldout-finalists: F-HT @ <its LF sha256> list <the joint list's sha256>`, F-HT its F-number, which Q-158's rule 1
   needs, so the reader enforces "after the held-out row". The joint order alternates by rank across the firms (H-2;
   E-257), by the held-out template's rule. Then **the held-out test**, the one joint fixed-sequence test, once, from
   a clean checkout of that row's commit, in the fixed sequence; the auditor on its result.
9. **The verdict row**; a carried design's registration and the confirmation's criterion declared there.

Each run once, watched to its exit, its file written with its manifest (`extended.results.write_result`, the
declaration's id, the design count, every seed and parameter). A failed check stays on record and is diagnosed by the
failure protocol, never rerun until it passes.

**The held-out reads (E-221, O-1; E-238).** **This search carries no `Judged-block reads:` line; the held-out
test's declaration carries it.** `extended/reader.py` (Q-158, merged at E-222) honours a held-out purpose only for a
pinned declaration that names it on its own `Judged-block reads:` line (a purpose named in prose authorises nothing)
and, by rule 1, only after a finalists' token row for that declaration's own hash, newer than its pin; by rule 2 the
first family whose judged read is ledgered holds the market's window. With no line in any search, no single search can
read NQ's held-out years, even with its own finalists' token from step 7, and the held-out test's declaration -- the
one family -- reads them once. Q-158 checks the finalists' token, not the held-out row, so the held-out-row condition is
held by the declaration and the auditor. The rules, binding whatever the code does:
- a held-out read is made **only after every finalists' row and the held-out row**, all citing their declarations'
  sha256s;
- the held-out years are read **once per market**, across declarations: a re-declared search gets no fresh read; the
  market's held-out test spends them (CHARTER 3.6 (c));
- an RD declaration never reads them before the market's verdict row, and no `registered_design` read of them (of
  P-14, P-15, P-16) is made before F-HT's verdict row (L-1; E-259).

What the held-out test's declaration reads, under its own line's two house purposes: `heldout_test` reads the
finalists and every baseline on the deciding reading, the time leg's groups and regimes, the long-run gate, and the
held-out readings section 11 puts beside -- the five-minute cell, the as-walked result and the path-structure edge,
the denial ladder, the playbook trigger side's held-out reading and the fill-time law; `heldout_stress` reads the
+1 tick and 10 %-missed stresses and the as-traded floor. Nothing of this search reads the held-out years.

## 15. What a pass and what a fail mean; the confirmation

- **A pass:** the finalist is **carried** -- it takes a registration id, its playbook, the auditor's read; its one
  confirmation is read against **a criterion declared at its registration, before the read** (CHARTER 5 (A)): at least,
  on the martingale-outcome reading, ahead of each baseline on the composite at the point estimate and inside every
  limit in the form in force; at the point estimate, the as-traded floor read on the real path, and ahead of each
  baseline at +1 tick of worse fills.
- **A fail -- what a fail means:** the search closes (a closing row, its cause from the held-out template's closed
  list); it spends no k; nothing of it is rerun; a new question is a new declaration citing this one, with a fresh seed
  block; exit (B) states the line's power from the power gate.
- **The confirmation:** NQ from 2026-07-17 to the last session in the purchase order's stated range, never read from
  bars, recorded in the first `heldout-window: NQ 2026-07-17 to <last> -- <text>` row, which states that it
  opens the confirmation window, not a second held-out test, and governs; any later NQ or MNQ window row from
  2026-07-17 on is refused by the reader (`extended/reader.py`; n1), this repository's `_cw_problems` only a
  cross-check; the purchase and that row come before the first finalists' row of any member (C-5; finding 5), read
  once, only for F-HT's carried designs; a non-member search's candidates never use it (CW-1, CW-2; E-259);
  **a purchase**, the operator's.

## 16. Anything chosen after seeing results

*(Nothing of this search's own readings: none exists. One search-year read of a cell in this space precedes the pin,
and is disclosed here, as the red team's B-4 and the form read's B-3 ask; anything added after a reading of this
search is exploratory, reported apart, `exploratory=True` in its manifest, recorded in its own decision row, and never
added to this file once pinned.)*

**The read:** Q-213's exploratory early look (E-290 (4), E-291): RL3's base cell, `rl3` with the side `fade` at the
prior session's levels, NY AM, latency-free, Topstep 50K, zero edge, on the search years, its result file
`results/early_look_rl3_pd_fade.csv` written at the timestamp its manifest records (2026-11-27T14:13:43 UTC), P-14's
H4-B readings beside it; seen by the lead and the operator (section 2's search-year ledger). **No value in this file
is taken from it.** Every choice it could touch, dated against it:

| choice | fixed by, and when | before the look's result | labelled |
|---|---|---|---|
| RL3's level kinds, its ticket times (published 08:30 CT, live 09:00 CT) and its NY AM component | E-204, E-208 (2026-11-18) | yes | no |
| the `rl3` side rule `fade` (`trigger_sides.RULES`) | commit `457f577` (2026-11-20); this file's text 1 | yes | no |
| T1 narrowed to `p14` and `rl3` | proposed in this file's text 1, handed back to the lead before the look's result was written; accepted after it (E-297 (2)) | proposed before, ruled after | **yes: the accepting ruling came after the look and could have been informed by it** |
| the no-harm margin set to delta\* | proposed in text 1; ruled after the look (E-297 (2)) | proposed before, ruled after | **yes, the same** |
| the screen, its seed indices and stride, the promotion and every size of section 6 | added after the look (E-292 (4), E-297 (2)); the sizes from compute arithmetic only (section 6) | no | **yes: declared after the look; no figure of it enters them** |
| W42-R2's added limit `net_month_12_p50` | ruled after the operator and the lead saw P-14's early-look 12-month figures (E-296); W42-R2 records that it chose nothing from them (its section 9) | no | **yes, with W42-R2's own disclosure beside the verdict (section 11)** |
| this text 2's fixes: W42-R2 throughout, the point-estimate keep rule, the screen's own indices, S1 in every run, the major-news list and check, the deciding-files closure, the ledger rows, the stress arms before the pin | the two reads of text 1 (both 2026-11-27), after the look | no | **yes: made after the look, each answering a review finding, none using the look's figures** |
| RL3's level kind `pd` and cutoff 14:30 CT fixed for this search, T7 held at `off`, S1's whole-tick rule, S2 design-wide, A1 and A2 held at `steady` | Q-215's route's findings, after the look; the values are RL3's draft base cell (2026-11-18) and the route's rules, taken by rule | no | **yes: fixed after the look, at the cell the look read; no figure of it enters them** |
| every other choice of this file | text 1 | yes | no |

---

*Sources: `CHARTER.md` sections 2-5 (E-210); `prereg/TEMPLATE_design_search.md` text v3 (E-284);
`prereg/TEMPLATE_heldout_test.md` (E-284); `docs/MEASURES.md`; `docs/plans/LEVER_TABLE_topstep50k.md`;
`docs/plans/WAVE42_SETTING_RULE.md` (E-283); W42-R2 (E-296); `docs/plans/THREE_WAY_TEST_design.md`; `prereg/H3_three_way.md` (E-279);
`prereg/H4_rebaseline.md` (E-287); `extended/survey.py` and the Wave 3.4 engine (E-281); E-204, E-208, E-211, E-221,
E-230, E-255, E-257, E-258, E-259, E-290, E-291, E-292, E-294, E-296, E-297.*
