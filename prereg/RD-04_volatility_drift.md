# RD-04: volatility drift -- the whole-window descriptive and a calm-regime replay of P-14 and P-16 (reading VD) -- a described reading, unnumbered (E-023 (1))

**Status: declared before anything of it is built or read.** It is pinned by the sha256 of its LF text in its decision
row. Nothing declared is edited: a change is a new declaration under a new row. It takes no program family number
(E-023 (1)).

**Its text's history.** The first text, drafted as `prereg/DRAFT_RD-04_volatility_drift.md` (TASK_QUEUE Q-123, E-157, E-158;
on wt/wt-scout, master merged at df95e3d), from the scout's note `docs/research/volatility_drift_2026-11-17.md` (Q-120,
merged under E-157): its sections 3.2 (the scorecard's exposure), 4 (a) (the descriptive), 4 (c) (the calm-regime
replay) and 7 (what is unknown). At the pin the file is renamed `prereg/RD-04_volatility_drift.md` and nothing else
changes; the pinning row names the commit and the sha256 it pins. **The second text** (Q-123b, E-164) answers the red
team's read of the first (Q-123r, `docs/reviews/DRAFT_RD-04_2026-11-17.md`; the first text at 7b98230, LF sha256
`a2eedbbb19bab3fca0ce1bf4cf298bd3c1a32e95f8d2a89b170c644579cbb3eb`), every finding as the lead adopted it; section 0.3
maps each finding to its change, and Appendix C lists every choice the drafter made where the note, the brief, the
review or the rules left the text open. **The third text** (Q-123c, E-167) answers the red team's re-read of the
second (Q-123r2, `docs/reviews/DRAFT_RD-04_v2_2026-11-17.md`; the second text at bd0ab26, LF sha256
`d7144bcd8ff731da44cc544a4e0fa428a6b8455ea2c1235be0e8b98f7cd96eb6`), as the lead ruled on it; section 0.4 maps each
finding to its change. It goes to the gatekeeper before any pin.

**What E-023 (1) makes of it, as E-157 (c) classes it.** E-157 (c) decided this reading a described reading under
E-023 (1). Neither part is a design, a lever or a filter:

- **(a2)** reads the bars only -- session ranges and the side-free first-exit times of fixed bands -- and no trade,
  side, outcome or design;
- **(c)** replays P-14's and P-16's own registered offers, sides, state table and protocol on a market whose movement in
  points is turned down. It adds or removes no offered trade, chooses nothing, and computes no lift over a coin twin.

So this file is a **described reading**:

- it takes **no program family number** and spends **nothing** of the multiplicity budget (the next numbered family's
  k is unchanged by it);
- **nothing in it can carry, pass or fail**: there is no pass line, no level, no pick and no menu;
- it is declared and pinned before its run, by its own decision row with its sha256, so nothing in it is chosen after a
  look.

**When this text was written (2026-11-17), nothing of it had been built, no bar had been read for it, and no replay or
gate had been run for it. No figure of the gate files' `period` or `drift` rows, or of any outcome, had been read.
Q-121's choice-block file had not been made.** Q-121 was built and merged (E-163). E-164 held its run until its module
took an optional authorisation; Q-121b merged that at 4b72ef2, and the run was re-queued there (E-166). So
every convention this text fixes on Q-121's rows was fixed before any of their values existed: the population, the
statistic, the year, the reference years and the blank-trailing rule (4.2). The pinning row states whether Q-121's file
had been made by the pin, and whether anyone had opened it. Anything chosen after a reading is exploratory and reported
apart (section 15).

| field | value |
|---|---|
| reading | VD: volatility drift in points against a contract fixed in dollars -- (a0) the two registered gate files' `period` and `drift` rows; (a2) the bars-only descriptive on the whole development window; (c) a calm-regime replay of P-14 and P-16 |
| id | RD-04 (`prereg/RD-04_volatility_drift.md` at the pin); every result's `prereg_id` is `RD-04` (section 13) |
| kind | a **described reading** (E-023 (1), as E-157 (c) classes it): never carried; it describes and decides nothing |
| program family number | **none**; the next numbered family's k is unchanged by this file |
| level, pass line, pick, menu | **none** |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16; (a2) reads them through `extended/reader.py`; (c) has Stage 2's engine read them inside P-14's and P-16's registered builders, authorised by `extended.reader.authorise_engine_read` (section 5) |
| the unit | (a2) the session (the walker's day, 17:00 to 15:10 CT, `atlas_local.day_arrays`); (c) one start day as U1 replays it, and one gate path |
| blocks | (a2): the whole window, reported by calendar year and quarter; (c): all starts the headline, the early block (purged per measure) and the late block from 2024-01-02 beside, start years beside (section 5) |
| cells | (a2): one pass over the window. (c): **2 references (identities) and 8 new cells, every one run** -- 2 designs x 2 scale factors (the year factor, the trailing-range factor) x 2 cost readings (actual; the tick costs scaled by the factor, the fee as charged; Stage 2 D-122) (section 6); a beside piece that cannot be built stops its own cells only (4.6) |
| beside | (c): the denial ladder and the placement on for every new cell; the ten binding Focused Trader models for the four actual-cost cells (`yr_act`, `tr_act` on each design), the gap named on the other four; the long-run gate for every new cell; each cell's own per-R edge and bound by the registered rule, its edge used only to centre the cell's zero-edge twin (4.4), its bound never used (section 9) |
| judged-block reads | (a2): one purpose, `volatility_descriptive`, on the line of section 5 item 6, for its bars and A1's `days` table in one run. (c): the purpose `registered_design` (E-037) under the pinning row, which names P-14 and P-16 -- never under this file's line -- from `scripts/rd04_replay.py`, inside a clean run, ledgered, and only while this file hashes to its pin (5 item 6). The identity under `identity` from `identity/rd04_identity.py` and its own row |
| seeds | this reading's block of ten, section 11's table: three in use, seven reserved; P-14's and P-16's gate seeds, P-16's coin seed, the registered era seed, Q-17's ladder start seeds and U1's replay seeds inherited (section 11) |
| confirmation | none: nothing is carried (section 10) |
| `confirmation_tests_on_this_market` | 3: NQ's three of Stage 2 D-107's three are spent (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`, `held_back_2025`); this reading adds none and reads no NQ from 2026-07-17 |

---

## 0. What each part changes, stated truly

### 0.1 (a2) changes nothing

It is a property of the bars: per session, how far NQ moved in points and in percent, and how long a band of fixed
points (or of a fixed share of the trailing range) took to be left, both sides pooled. No sign, no target-against-stop
split, no win share, no trade of any design.

### 0.2 (c) changes only the market's amplitude in points

Per session d, every bar's open, high, low and close is drawn toward the session's first open O_d by a factor k at most
one and put back on the tick grid (section 4.1). **What stays fixed:**

- the brackets in points (P-14's 12.5- and 25-point rungs, P-16's 150-tick stop) and every R the state table offers;
- the whole micros at each state's fixed dollar risk, so every trade risks the same dollars;
- the contract's dollar limits: the Combine's $3,000 target (`combine_profit_target`, 8284208), its $2,000 trailing loss
  limit (`combine_mll`, 8284204), the funded account's -$2,000 floor (`xfa_mll_start`, 8284204), the $150 winning day
  (`xfa_std_winning_day_min`, 8284233);
- the offers: P-14's event minutes and sides, P-16's admitted marks and coin sides, the day kinds, the report-day cuts;
- the frozen choices: P-14's rung by hour, P-16's admitted marks, the state table, the verdict arm's per-R shift, the
  day capacity (section 4.4);
- the protocol: seats, purchase budget, routing under the strict one-position rule, payout rule, fees, conduct model.

**What changes:** every offer's walked outcome -- its kind (target, stop, breakeven, flatten), exit bar, MAE and gross
ticks. From that, everything downstream changes and is rebuilt: which offers the router takes, when each account
resolves, the gate's paths and every start's journey.

This is the operator's counterfactual (E-155): **today's market moving as little in points as the calm reference years,
with the contract unchanged.** It is not a replay of 2020-2021: volume, spreads, the intraday clock, news and market
structure stay as they were (pitfall 5, section 4.5).

### 0.3 What changed from the first text (Q-123r's findings, as E-164 adopted them)

| finding | the first text | this text | where |
|---|---|---|---|
| **M1** | `sc` multiplied "each per-trade cost", the fee included, which the engine's re-pricing at size undoes; a piece that could not be built stopped all of (c) | `sc` scales **the tick costs only**; the round-turn fee stays as the engine charges it at size and `fee_micro_eq` is never altered; T-4 gains a toy engine campaign at k < 1; a piece of a beside cell that cannot be built stops that cell alone, never `k1` or `yr_act` | 4.3; 4.6; 6.2; 7; 8.1 item 6; 9.1 item 8; 10; 12.1 A-2; T-4; Appendix C 8, 25 |
| **M2** | the zero-edge twin of a new cell shifted by `k1`'s e, so not zero-edge | each new cell's twin centred on **its own e**; the arms' `e`, `lb`, `e_by_rr`, `lb_by_rr` `k1`'s; an oracle holds the twin's mean at zero to 1e-12 | 4.4; 6.2; 7; 8.3; 9.1 item 7; 12.1 A-3; T-7; Appendix C 6 |
| **M3** | the once rule read the ledger only; a worktree run was admitted unledgered; RD-04's hash unchecked | `scripts/rd04_replay.py` refuses outside a clean run, refuses an unledgered authorisation, and refuses unless RD-04 hashes to its pin; the build's smoke and timing runs on synthetic bars only | header table; 5 item 6; 11; 13.2; T-12 |
| **M4** | Q-121's names by role (and wrong); "the median" over "the sessions"; `k_trail` in `session`; Q-121's refusal unanswered | Q-121's real names; its module through the optional `authorised` keyword Q-121b adds; the inverted-CDF median of `trail20_range_pts` over the walked sessions with a finite value, by the trading day's year; L_y for 2020-2023 held to Q-121's `range` rows; `k_trail` and `k_year` in `factor`; (a2)'s read of A1's `days` table under its purpose, Q-121's two identities over the whole window | header table; 2; 3.2; 4.2; 5 item 6; 7; 8.2; 8.3; 13.1; 13.3; 14 item 2; T-2; T-10; Appendix C 4, 11, 13, 21, 26, 27, 33 |
| **M5** | `band_mark` written for the judged years; the leak clause bound nothing | no `band_mark` row of the judged block; the clause adopted by the pinning row as the lead's program rule from step 2's first run, binding later declarations and parameter-fixing rows; the step-2 row's token; the leak-clause test `tests/test_rd04_leak_clause.py` (T-15), built with T-0 | 1; 3.2; 9.3; 13.1; 13.2 step 2; 13.3; 14 item 4; T-10; T-15; Appendix C 26, 28 |
| m1 | T-2's shift invariance over every factor, false inside the reference span | L_ref a declared constant, passed in; invariance of L_d and k_d given L_ref | 4.2; T-2 |
| m2 | the year factor's non-causality and the compressed reference year left to inference | both said; every `yr` row labelled | 4.2; pitfall 9; 9.1 item 8 |
| m3 | "the tick grid's bounce not removed" | "the tick-scale bounce is compressed with the path; a real calm market keeps it; neither reading restores it" | 4.3; pitfall 1; 9.1 item 8 |
| m4 | the Focused Trader models on the two headline cells | on the four actual-cost cells (`tr_act` added): 40 replays, 72 beside in all | header table; 6.4; 7; 9.1 item 6; 13.2; Appendix C 9 |
| m5 | T-0's seed clause impossible after the build | RD-03's `DECLARED_USES` form; the block named by reference in the lead's rows; T-0 built with this text | header table; 11; T-0; Appendix C 32 |
| m6 | four gaps in the k = 1 identity | the map applied at every k (a call count); the actual prices checked on the grid; each session's applied k its `factor` row's; P-16's e and bound held to the registered | 4.1; 8.1 item 3; 8.3; 12.1 A-1; T-1; T-7 |
| m7 | the reference years cited to E-155, which names none; the header true only at drafting | the years classed as the lead's choice with E-155's description as the reason; the header states what was true when written, and the pinning row the pin-time facts | header; 7; 14 item 5; Appendix C 34 |
| n1 | the classification cited to E-134 (1) | E-157 (c) with E-023 (1) | header |
| n3 | the gate's pairing claimed, not traced | traced through the gate's `counters` argument where it can be, else labelled | 5 item 4; 8.3; 12.1 A-3; Appendix C 30 |
| n4 | the step-shaped paired series unlabelled | labelled on every paired row with any start identical | 9.1 item 5; T-13; Appendix C 31 |
| n5 | the second reference dropped as unasked | dropped on cost, its relevance to selection said | 7 |
| n6 | RD-04's `vd_` prefix overlapping Q-121's `tests/vd_synthetic.py` | RD-04's files renamed to `rd04_` | throughout; 12.1; Appendix C 29 |
| n2, n7 | -- | recorded as the review found them: the pinning row a standing `registered_design` licence (as E-024 and E-026), RD-04's own use confined by M3; (a0)'s "not read before step 2" a record, not a lock | -- |

### 0.4 What changed from the second text (Q-123r2's findings, as E-167 ruled on them)

| finding | the second text | this text | where |
|---|---|---|---|
| **M1** | T-15 scoped pins strictly after the step-2 row, anchored on that row alone; three routes failed open (a pin inside the row; a pin between the run and the row; a mistyped row, which disabled the test silently) | scope **in or after** the step-2 row, **and** every pin in a row absent from `DECISIONS.md` at the read's commit; once the read ledger holds RD-04's `volatility_descriptive` line, the test fails unless a step-2 row exists; a synthetic case for each route, each shown to pass silently under the second text's test | 9.3; T-15; Appendix C 35 |
| m1 | the interface as three functions, `band_mark` "the judged years among them", Q-121b owed, the run "queued (E-163)" | the merged interface: the keyword on five functions, `summarise` passed it, the module's checks and its 2026-07-16 cap, `band_mark` choice-block-only in both modes; Q-121b met at 4b72ef2 and the run re-queued there (E-166); the drop of `band_mark` kept as a second lock, its reason corrected | header; 3.2; 13.3; 14 item 2; Appendix C 26 |
| m2 | the pairing traced through the gate's `counters` argument | struck; the pairing a fact by the vendored `SharedDayTable`, with an oracle holding each cell's block dates and order to `k1`'s | 5 item 4; 8.3; 12.1 A-3; Appendix C 30 |
| m3 | Q-121's file "made at a commit whose module carries the keyword" | (a2) refuses unless its imported module hashes to the one at the commit in Q-121's manifest | 3.2; 13.1; 13.3; T-10; Appendix C 33 |
| m4 | T-0 checked the functions exist | T-0 asserts the keyword-only `authorised` on the five functions and the four constants | 12.2 T-0; 14 item 2 |
| m5 | a pre-read draft pinned after the read had no true sentence | the lead's ruling: the pinning row may carry `` `written before RD-04 was read, unchanged since <commit>: <path>` ``, checked against git by T-15 | 9.3 item 1; T-15; Appendix C 36, 37 |
| n1 | -- | the order `authorise`, `read_bars`, the module; no `Authorisation` built by hand (a T-10 scan); `ledgered` read as "will be ledgered" | 3.2; 5 item 6; 12.1 A-4; T-10 |
| n4 | A-4 and Appendix C 29 named `tests/vd_synthetic.py` | renamed `tests/q121_synthetic.py` (E-166) | 12.1 A-4; Appendix C 29 |
| n5 | -- | 4.6's failure scope decided at build time; a mid-run failure is 13.2's | 4.6 |
| n7 | the twin oracle "over the cell's trades" | over the trades with a finite `r_R`, as `edge_stats` takes them, on the blocks | 8.3; Appendix C 38 |
| n10 | 8.2 left every `block` row uncompared | `band_mark`'s block row compared too | 8.2; Appendix C 39 |
| n11, n12 | -- | recorded as readings: the pooled `band` rows' residual leak, accepted; T-15's phrase check lexical | 9.3 |
| n2, n3, n6, n8, n9 | -- | as the re-read found them (sound, or covered by m1 and m2) | -- |

## 1. What this reading is, and what it is not

**Its job.**

- **(a2)** answers the factual question the record leaves open (the note's section 7): NQ's session range in points and
  in percent by year and quarter over 2020-2026, and the resolution time of fixed brackets by year -- whether the rise
  is price level or percent volatility.
- **(a0)** puts beside it what Stage 2's registered gate files already hold: P-14's and P-16's trades per day by era and
  their trade counts by year.
- **(c)** shows how much of P-14's and P-16's journey scorecard, gate and supply is points volatility: the same designs,
  the same contract, a calmer market.

**What it is not.** A test, a claim of an edge, a candidate, a registered design, a correction applied to any other
reading, or a choice of any parameter. It carries nothing; no rule changes because of it.

**Why described rather than tested** (E-023 (1)). There is nothing to judge: (a2) has no outcome, and (c) is a
counterfactual of designs already judged in Stage 2 (E-037's reasoning). Its value is the description.

**The leak, stated first (section 9.3).** (a2) and (c) read the judged block's volatility and the registered designs'
supply in it. A figure from them could steer a later declaration -- for example toward a stop that resolves in
2024-2026. **Every later declaration states that it was written after this reading's run, and none cites a figure of
it as the reason for a parameter.** The pinning row adopts this as the lead's program rule, and a fast test refuses a
later pinned declaration that lacks the line (9.3). (a2) writes no by-mark row of the judged block (3.2).

## 2. Prior exposure: what has already read this, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| Stage 2 D-106, D-121 (2), D-122 (1) | development prices rescaled to the era; the remedy corrected | ES 2009-2014 | "No era-matching method removes it [the one-tick bounce relative to the stop] ...; it is bounded by reporting actual and rescaled prices side by side" | the cost readings of (c) (pitfall 1) |
| Stage 2 D-225, D-226 | NQ rescaled to today's price level | 2009-2019 | an exploratory proxy, never a result | rescaling's standing: a counterfactual, labelled |
| Stage 2 D-238, D-239 (`results/regime_then_now.csv`, **not vendored**) | the regime map: fixed stops in points and range-scaled stops, per market, decision, stop and R, by era; beside resolution, "per window and year, volume and range" and "the session range" | QuantConnect's AlgoSeek bars, 2009-06-01 to 2025-06-30 | in words only here: range-scaled brackets era-stable, fixed-point ones not; NQ moved "several times further a day in 2020-2025" | **D-238 measured range by window and year over 2020 to June 2025 on other bars; the file is not in the snapshot and its values were never read here.** (a2) is the first such reading on this repository's Databento bars and to 2026-07-16 |
| Stage 2 D-240 | range stops dropped from the no-edge campaign | 2020-2025 | "their dollars per trade move with the trailing range, which D-212 forbids" | why (c) keeps the brackets in points and scales the market instead |
| Stage 2 D-212, D-308 | the resolution floor: at most 5 % flattened overall and in each year | -- | a rule | (c)'s per-year resolution reading; a failure there is a finding (pitfall 4) |
| Stage 2 D-271, D-420, D-437 | the era rule on mean gross R; the per-era report beside | 2020-2022 against 2023 to 2026-07-16 | eras flagged for P-13; the lower era's bounds read | the verdict arm's shift that (c) holds fixed (4.4) |
| Stage 2 D-292 | range per half-hour window | 2020 to June 2025 | time of day, in words | not by year |
| Stage 2 D-300 to D-307 | ATR-scaled stops, then fixed points with exact dollars | 2013-2026 | ATR stops broke the dollar sizing | why (c) scales the market, not the bracket |
| Stage 2 D-554 | P-16's stop chosen on 2020-2023 alone and on 2024-2026 alone | both spans | the 50-point stop fails resolution early and resolves late | **knowledge of resolution drift across the blocks already on record** (9.3) |
| Stage 2 D-578, D-580, D-581, D-582, D-604, D-605 | the span guard; S1's momentum sides; S2's volatility thirds; P-16's money "from supply"; the money by year in words | both blocks | supply depends on the regime; 2020-2021 the weakest years for growth, in words | the direction (c) is expected to show is partly on record |
| This repository: E-024, E-030, the red team's M2-4 on F-B (`docs/reviews/DRAFT_F-B_multifeature_v2_2026-11-16.md`) | pooled and worst-year resolution shares from Stage 2's files | both blocks | far apart; the 37.5-point stop dropped from F-B | prior knowledge of the drift's effect on resolution (9.3) |
| U1 (Stage 2 D-620), Q-05 (E-010), program U's nine families | P-14's and P-16's journeys, every start; P on the late block | both blocks | the reference rows; all nine families closed | the late block has been read for P many times: late development, not out of sample |
| Q-121 (E-157, E-163), built and merged, its run queued, at this text | (a1): the same descriptive on the choice block only | 2020-01-02 to 2023-12-29 | nothing yet: its file not made | L_ref's source (4.2) and (a2)'s identity (8.2) |

**The gate files' `period` and `drift` rows** (`vendor/stage2/results/a3_brk30_cb20_gate.csv`,
`vendor/stage2/results/rc_s150_all_gate.csv`) are Stage 2's registered designs' own rows, already judged in Stage 2.
Only their section and column names are on record here (the note's section 2, end); **no value of them has been read in
this repository**, and none is read before step 2 of this reading's run (section 13). The pinning row records that.

**The drafter's own reads (disclosed).** The scout's note (whole); the briefs Q-121 and Q-123; `DECISIONS.md` E-007,
E-008, E-021, E-023, E-025, E-026, E-037, E-053, E-104, E-117, E-125, E-134, E-146, E-152, E-155, E-156, E-157 and E-158
(the first draft read E-157 from the lead's working copy before it was committed); Stage 2's rows D-106, D-121, D-122, D-212,
D-238, D-239, D-240, D-308, D-554; `prereg/RD-03_contract_levers.md` (whole, for form); `vendor/stage2/prereg/P-14_a3-brk30-cb20.md`
lines 180-240 and `P-16_rc-s150-all-nr.md` lines 150-200; code only: `extended/reader.py` (whole),
`vendor/stage2/scripts/atlas_a3.py` (header, lines 140-260, `bounds`), `rc_screen.build`, `rc_width_screen.build` and
`cutoff_reading`, `rc150_dev_test.build_cells`, `rc_dev_test.trades_hash` and `build_cells`,
`user_journey._rc_campaign` and `build_p16`'s header, `a3_brk30_cb20.py` lines 280-330 and 423-445,
`customer_slices.arm_blocks`, the gate's column names in `extended/gate.py`, `extended.user_measures.cvar`'s line, `atlas_local`'s header and
`day_arrays`, the headers of `extended/replay_records.py`, `identity/user_beside_identity.py` and
`identity/gate_identity.py`, the function names of `extended/user_beside.py`, `extended/gate.py` and
`extended/pp_reading.py`. **No result file of either repository was opened**; the vendored results folder was not
listed. The seed search of section 11.

**The second text's drafter read, in addition:** the red team's note (whole); `DECISIONS.md` E-163 (and E-155,
E-157, E-158 again); Q-121's code as merged at a83db31 (`extended/vol_descriptive.py` whole, `scripts/vol_descriptive.py`
whole); `extended/reader.py`'s `Authorisation`, `authorise`, `_family`, `_registered`, `_clean_run` and `_once` again;
`extended/gate.py`'s `run_gate` (its arms and its `counters` wrap); the vendored `propedge/campaign/sizing.py`
(`SizingRule.fee_schedule`, `fee_dollars`), `scripts/portfolio_stage.py` (`zero_edge_blocks`), `scripts/atlas_a3.py`
(the cost line of `cell_trades`) and `scripts/score_fv3_grid.py` (the `fee_micro_eq` lines); `tests/test_rd03_draft.py`
and `tests/test_declarations_fixed.py` (for T-0's form and the leak-clause test). **Q-121's file did not exist and was
not opened; no result file was opened.** The seed search of section 11, again.

**The third text's drafter read, in addition:** the red team's re-read (whole); E-164 to E-166 (E-166 from the lead's
working copy); Q-121b as merged at 4b72ef2 (`extended/vol_descriptive.py`'s interface, `summarise` and
`output_problems`); `extended/reader.py`'s ledger record (`_record`); `extended/gate.py`'s `counters` lines; the
read ledger's field names (one line opened for its format, not a figure). **No result file was opened.**

**What is already known of the direction (disclosed).** NQ's movement in points rose from 2009-2019 to 2020-2025
(D-239); a wider fixed stop resolved late and not early (D-554); P-16's money is supply (D-582); 2020 and 2021 were the
weakest years for growth (D-605, in words). Nothing is known of (c)'s quantities: no replay at a reduced amplitude has
been run in either repository.

## 3. (a0) and (a2): the descriptive

### 3.1 (a0): the gate files' existing rows, read as they stand

From each of `vendor/stage2/results/a3_brk30_cb20_gate.csv` (P-14) and `vendor/stage2/results/rc_s150_all_gate.csv`
(P-16), each checked first against `vendor/MANIFEST_stage2.sha256` (refusing):

- section `period`: every row (periods `2020-2022`, `2023-2026`, `all`, `check`), every column, as text;
- section `drift`: every row (years `2020` to `2026`), every column, as text.

Copied into `results/rd04_descriptive.csv` section `a0` with the source file and its sha256. Nothing is computed from them
and nothing else of either file is read.

### 3.2 (a2): the bars-only descriptive on the whole window

**The code is Q-121's**, imported, never copied or edited: `extended/vol_descriptive.py` (Q-121's build, E-157, E-163;
with **its optional reader authorisation, Q-121b, merged at 4b72ef2**, E-166), run on every development session from
2020-01-02 to 2026-07-16.

**The authorisation, as merged (Q-121b at 4b72ef2; the re-read's m1).** **Five** functions take a keyword-only
`authorised` (an `extended.reader.Authorisation`, default none): `check_span`, `check_days`, `describe`, `summarise`
and `output_problems`. The module's constants are `AUTHORISED_PURPOSE` `"volatility_descriptive"`, `AUTHORISED_KIND`
`"described_reading"`, `AUTHORISED_DECLARATION` `"prereg/RD-04_volatility_drift.md"` and `AUTHORISED_LAST_DAY` the
reader's `JUDGED_END` (2026-07-16). T-0 holds the four constants and the five keywords.

- **Absent**, the last day is `CHOICE_END` (2023-12-29), as at a83db31. Q-121's refusal and its tests stand, and its
  toy file is byte-identical to the frozen a0cb1ce module's (E-166). **`summarise` without `authorised` refuses every
  judged day**, so (a2) passes the authorisation to `summarise` as well as to the others.
- **Present**, `check_authorisation` runs before any input is touched. The module refuses unless every one of these
  holds:
  - the authorisation is a real `Authorisation`;
  - `judged` is true, with `"judged"` among its blocks;
  - its `kind`, `purpose` and `declaration` are the three constants;
  - `ledgered` is true;
  - its `declaration_sha256` has 64 characters;
  - its span starts on or after 2020-01-02 and does not reach 2026-07-17.

  Days then run from the authorisation's start to its end, capped at 2026-07-16. For a reader-made authorisation that
  is exactly the reader's span.
- **`band_mark` is built from choice-block sessions only, in both modes.** `output_problems` refuses a `band_mark` row
  reaching 2024, and under an authorisation it does not require the `band_mark` section.
- Q-121's script exposes no such argument, and its command line is unchanged. The reader stays the real lock; the
  module's check is a second one.

**How (a2) uses it (the re-read's n1).** (a2)'s script (`scripts/rd04_descriptive.py`) calls, in this order:
1. `extended.reader.authorise`, with the arguments of the `read_bars` call that follows;
2. `read_bars`;
3. `describe`, `summarise` and `output_problems`, each with that `Authorisation`.

It calls `check_span` with the authorisation or not at all. An authorisation whose `read_bars` raised is never used.

**No `Authorisation` is ever built by hand** in RD-04's files. The dataclass is frozen, but it could be constructed
with every field right, so "only the reader's authorisation opens the module" holds by this rule. T-10 scans the
`rd04_` files for a direct `Authorisation(` construction. The module's `ledgered` check means "will be ledgered": the
ledger line itself is written inside `read_bars`.

(a2) never copies Q-121's functions and never edits them.

**The module (a2) imports is the one that made Q-121's file (the re-read's m3).** Before any authorisation, (a2)
refuses unless its imported `extended/vol_descriptive.py` has the same LF sha256 as that file at the commit named in
Q-121's result manifest (`results/q121_vol_descriptive_a1.csv.manifest.json`, its `git_commit`, read with `git show`).
8.2's identity exercises only the absent mode; this check ties the authorised mode to the same bytes. T-10 holds the
refusal.

**Per session** (Q-121's definitions, its docstring's, unchanged):

- `range_pts`, the high-low range in points, and `range_pct`, that range in percent of the session's first open;
- `trail20_range_pts` and `trail20_range_pct`, the mean of the same measure over the **20 most recent prior walked
  sessions** (day kind 'n' or 'b'; `trailing_means`), the session itself never read; **blank when fewer than 20 walked
  sessions precede it**. FOMC days ('o'), early closes ('e') and bar-less days ('x') never count toward a trailing mean,
  and an 'o' or 'e' session has a trailing value of its own;
- at P-16's five-minute marks (delay 0) and P-14's hour starts 17:00 to 14:00 CT (delay 5), on the walked sessions, the
  side-free first-exit time of a band of 12.5, 25 and 37.5 points (50, 100, 150 ticks) and of 0.10 and 0.25 of the
  trailing range (D-238's scale-free reading), at every quarter R to 3R, both walks pooled, and the share still open at
  15:08 CT.

**Reported** by Q-121's `summarise`, by block, calendar year and quarter: the median, p10 and p90 of every quantity --
each the **inverted empirical CDF** (`value_quantiles` and `quantiles`: the smallest value with at least the share q of
the sample at or below it, no interpolation) -- with the counts. 2026 is a part year (to 2026-07-16), labelled.

**What (a2) writes of it (M5): the sections `session`, `range` and `band` (pooled over every mark of a set), whole
window, never `band_mark`.** The merged module already writes no `band_mark` row from 2024-01-02: under the
authorisation, `summarise`'s `band_mark` rows are the choice block's alone. (a2):
1. runs `output_problems(frame, authorised=...)` on the frame as `summarise` returns it;
2. compares the frame's `band_mark` rows in memory (8.2);
3. drops them before anything is printed or written;
4. adds its own sections after that.

**The drop is a second lock.** The module already writes none from 2024-01-02, and the drop keeps Q-121's choice-block
rows in Q-121's file alone. Every row is in Q-121's `COLUMNS`, unchanged: (a2) adds no column to Q-121's sections.

**Q-121's two identities over the whole window.** The days identity (`kind_problems`) and the walk identity
(`walk_problems`) of `scripts/vol_descriptive.py` are imported by the file's path, never copied, and its `main` is never
called. Each runs over every session, refusing, before anything is summarised. The days identity reads A1's `days` table
(`vendor/stage2/data/atlas/A1/days.parquet`, `date` and `day_kind`) to 2026-07-16 through `extended.reader.read_walks`.
That read is made under `volatility_descriptive` and this declaration, in the same run as the bars (5 item 6). The day
kinds feed the walked set, so they feed the trailing means and the factors.

**And the factors for (c)** (section 4.2), computed from (a2)'s own `session` rows, are written in (a2)'s own section
`factor`. It holds L_ref with its source; per session, `date`, `k_trail` and `k_year`; per year, L_y, k_y, the count of
sessions in L_y's population, and the trailing factor's p10, p50 and p90 with the count of sessions left unscaled.

## 4. (c): the calm-regime replay

### 4.1 The map

For each session d (the walker's day, 17:00 to 15:10 CT, as `atlas_local.day_arrays` builds it) and its factor k_d in
(0, 1]:

- O_d is the session's first open: the open of the first bar present in the day's arrays;
- each of a bar's open, high, low and close p (not missing) maps to

  `p' = O_d + 0.25 x round(k_d x (p - O_d) / 0.25)`,

  `round` being numpy's round half to even, 0.25 points the MNQ and NQ tick (`vendor/stage2/config/instruments.yaml`
  lines 73-78); a missing bar stays missing.

Since O_d and p lie on the tick grid and rounding to the nearest is non-decreasing, the map keeps every bar's order: the
high stays the highest, the low the lowest, and no bar's range grows. At k_d = 1 it returns p exactly (an exact
multiple of the tick divided by the tick is an exact integer in binary floating point), so the identity of section 8.1
is bit for bit.

**The map is applied at every k, 1 included**: the wrapper never short-circuits a session whose factor is 1, so 8.1's
identity exercises the map's arithmetic on every session (T-1 holds this by a call count). **That every actual price
lies on the 0.25 grid is checked, not assumed**: before a session is mapped, every present open, high, low and close is
checked to be an exact multiple of 0.25 (8.3). A session that fails stops the step as an adapter or data error, with its
date, so an off-grid price is diagnosed and never snapped silently.

Prices relative to any entry inside the session scale by the same factor: p' - e' = k_d x (p - e), up to rounding of
half a tick at each. **So a bracket of fixed points, entered anywhere in the session, faces moves k_d times as large.**

### 4.2 The factors

- **The trailing range.** For each session, `trail20_range_pts`: the mean session range in points over the 20 most
  recent prior walked sessions, blank with fewer than 20 before it (3.2). This is the `session` column of (a2), the same
  column as in Q-121's file.
- **The population and the statistic, fixed now.** Every median of this section is Q-121's
  `value_quantiles(...)["median"]`: the inverted empirical CDF, the k-th smallest value with k = ceil(n / 2), and never
  numpy's interpolating median. It is taken over the `session` rows with **`walked` true** and a **finite
  `trail20_range_pts`**. The year of a session is **the trading day's year**: the year of its `date`, the walker's day,
  which runs from 17:00 CT the evening before.
- **L_ref, the calm reference:** that median over the rows dated 2020-01-02 to 2021-12-31, both years in the choice
  block. **Read from Q-121's choice-block file**: `results/q121_vol_descriptive_a1.csv`, section `session`, columns
  `date`, `walked` and `trail20_range_pts`. The file is checked first against its sidecar manifest and against the
  decision row that records its run (13.3). (a2)'s choice-block rows must equal that file's (8.2), so the same median is
  also computed from (a2)'s rows and checked equal, refusing.
- **The year factor (the headline):** for each calendar year y, L_y is the same median over year y's rows (2026's to
  2026-07-16), and

  `k_y = min(1, L_ref / L_y)`,

  one constant for every session of the year, whatever its kind. A year whose L_y is at or below L_ref is left unscaled
  (k_y = 1). **For 2020 to 2023, L_y also equals Q-121's own `range` row** (`period_kind` `year`, `period` y, `measure`
  `trail20_range_pts`, column `median`), which uses the same population and statistic. This is a free cross-check,
  refusing.
- **The trailing factor (beside):** for each session d, `k_d = min(1, L_ref / L_d)`, L_d being d's own
  `trail20_range_pts`. **A session with a blank `trail20_range_pts`** -- fewer than 20 walked sessions before it, which
  covers more than the window's first 20 sessions -- is left unscaled (k_d = 1), counted.

**"Causal", stated exactly (m1).** L_d is prior-only: it reads only sessions before d. L_ref is **a declared constant**
over the reference span 2020-01-02 to 2021-12-31, an input to every factor and not recomputed per session. So T-2
holds L_ref fixed, passed in, and asserts that L_d and k_d given L_ref do not change when any session from d on is
changed. A change inside the reference span moves L_ref, and so moves every factor, earlier ones included; that is
the constant's definition, not a look-ahead.

**The year factor is not causal (m2).** k_y uses every session of year y, so a January session's path depends on
December's trailing ranges. That is acceptable here: no quantity of (c) that offers, sides, routes, sizes or settles a
trade reads k (4.4); k shapes the replayed path and decides nothing. Every `yr` row is labelled "the year factor uses
the year's own later sessions: a counterfactual's scale, not a rule a user could follow".

Only compressions: every factor is at most one, so (c) turns volatility down and never up. **The day's own range is
never used** (pitfall 2).

### 4.3 The two cost readings (Stage 2 D-122 (1))

Compressing the path by k at the actual tick costs is the same as the real path with the brackets and the tick costs
both divided by k: costs per unit of movement rise by 1/k. That is realistic for a calm market but cannot be removed
(D-122 (1)), so it is bounded by two readings side by side:

- **`act` -- actual costs:** every per-trade cost as the registered builders charge it: the entry tick, the tick on a
  stop or breakeven exit, the two ticks on the flatten, the round-turn fee at the contracts held (P-14's and P-16's
  §3, FV3-C's `Signals3.outcome`, `atlas_a3.fee_by_stop`, D-324). **The headline.**
- **`sc` -- tick costs scaled by the factor (M1):** **the tick costs only** -- the entry tick, the tick on a stop or
  breakeven exit, and the two ticks on the flatten -- each multiplied by the session's k (fractional ticks allowed), so
  the tick cost per unit of movement is today's. In the cost of `atlas_a3.cell_trades`,
  `(entry ticks x tick + fee + exit ticks x tick) / (S x tick)`, `sc` multiplies the two tick terms by k and leaves
  `fee` as it is. **The round-turn fee is not scaled in either reading.** It stays as the engine charges it at the
  contracts held. Under `costs: per_trade_at_size` (Stage 2 D-324, `config/fv3_corrected_portfolio.yaml`) the sizing
  replaces the trade record's micro-equivalent fee (`fee_micro_eq`) with `SizingRule.fee_dollars(contracts)`
  (`propedge/campaign/sizing.py`). So `fee_micro_eq` is never altered: scaling it would be undone by that re-pricing,
  and scaling the cost column alone would be over-credited by it. The fee is dollars per contract, the contract's,
  held fixed like the subscriptions and activations, which are not trade costs and are not scaled either. **Beside.**

The tick grid of the prices is kept in both (it is the market's). **The tick-scale bounce is compressed with the path
(m3).** The map rounds each price's offset from O_d, so a real one-tick move becomes 0 or 1 tick, about k ticks on
average. A real calm market at the same contract keeps a one-tick bounce, and neither reading restores it. Every row of
(c) carries that label.

### 4.4 What is frozen, never recomputed on the rescaled bars

Each from the registered build on the actual bars (the k = 1 build of section 8.1, which must equal the registered):

| frozen | value | why |
|---|---|---|
| P-14's offers | A1's event minutes and sides on the 'n' and 'b' days, a 'b' day's events before the 07:30 CT cut dropped (`atlas_a3.pool_minutes`, A1's cache read only) | the entries are the design's; pitfall 3 |
| P-14's rung by hour | the 25-point rung from 17:00 to the 12:00 hour, the 12.5-point rung at 13:00 and 14:00, and the R offered at each, from `results/a3_resolution_map.csv` as pinned in P-14's config (P-14 §3) | pitfall 4 |
| P-16's offers | the five-minute marks the cutoff admits at the 150-tick stop on the actual bars (`resolved_coin.mark_resolution`, kind columns only, at most 5 % unresolved over the window at every offered R), the report-day cuts, D-533's release-minute removal, the coin sides at seed 20261102 | pitfall 4; P-16 §3 |
| the state table | `state_dp_e-0.050_lamstar_noclose`, checked against `a3_brk30_cb20.NOCLOSE_POLICIES_SHA256` | the designs' sizing |
| the verdict arm's shift | each R's `lb - e` from the k = 1 build (`atlas_a3.bounds`, the era rule at its registered seed), applied to the rescaled blocks by `customer_slices.arm_blocks` and the gate's `shifted_blocks`; **the gate's `e`, `lb`, `e_by_rr` and `lb_by_rr` for the point and bound arms are `k1`'s** (M2) | the registered pessimism held fixed, only the amplitude moved |
| the day capacity | each design's busiest day's offers (D-469) | the offers are unchanged, so it is unchanged (asserted, 8.3) |

**The zero-edge twin of every new cell is shifted by the cell's own e (M2).** The twin is
`portfolio_stage.zero_edge_blocks(blocks, e_by, fr)`, which shifts each R by `-e_by[R]`. With `k1`'s e passed in, a
rescaled cell's twin would keep a mean of e_cell - e_k1 per trade and would not be a zero-edge twin. So each new cell's
twin takes **the cell's own e per R**, computed on its rescaled trades by the registered rule (`atlas_a3.bounds`'s
e). **This is the only use of the cell's own e**; the arms keep `k1`'s (the table above), and an oracle holds the twin's
mean at zero (8.3). `k1`'s twin is the registered one, as 8.1 item 4 reproduces it.

**The rescaled walk's own readings are printed beside, never used to decide:** how many of P-16's frozen marks, and of
P-14's frozen hour-rung pairs, would fail the 5 % cutoff on the rescaled walk; and each R's e and bound recomputed on
the cell's own trades by the registered rule (`atlas_a3.bounds`, the registered era seed), section `bounds_beside` --
the e used only to centre the twin, the bound never used.

### 4.5 The pitfalls (the note's 4 (c)), each answered here

1. **The tick grid does not shrink** (D-122 (1)). Answered by the two cost readings side by side (4.3), `sc` scaling
   the tick costs and never the fee. The tick-scale bounce is compressed with the path; a real calm market keeps it;
   neither reading restores it. That is named on every row.
2. **One factor per year, not the day's own range.** Rescaling each day by its own range would erase clustering and
   news days and would use the day's future range. The headline is the year factor; the trailing factor (prior
   sessions only) is the causal alternative beside; the day's own range enters no factor.
3. **Drift is scaled too.** Net moves shrink by k, so drift relative to volatility is kept. The entries do not move:
   P-14's events and P-16's marks are taken from the registered build on the actual bars (4.4), never re-detected on
   the rescaled bars. (An affine map about the open preserves a break of the 30-minute bar up to ties made by the
   rounding, so re-detection would differ only there; it is not done.)
4. **Frozen choices stay frozen.** P-14's rung by hour and P-16's admitted marks are kept (4.4). The replay's
   unresolved shares are reported by year and R against D-212's 5 % (D-308), and **a D-212 failure there is a
   finding, recorded and read, never a trigger to rerun, re-freeze or drop a cell.**
5. **Only amplitude changes.** Volume, spreads, the intraday clock and market structure stay as they were. Every row of
   (c) is labelled **"today's market with its points volatility turned down, not a replay of 2020-2021"**.
6. **Session gaps are not rescaled.** Every session is anchored at its own first open; every position is flat by 15:10
   CT, so none crosses a gap. No input of either design crosses sessions on the rescaled bars: P-14's events and
   P-16's marks are frozen, and the trailing factor is computed on the actual bars.
7. **Nothing is written to the data junction.** The rescaled arrays and walks live in memory in the clean run;
   `atlas_a3.cached_walk` is never called with `write=True` on rescaled arrays, A1's and A3's caches are read only, and a
   test holds that no file under `vendor/stage2/data` is written or touched (T-5).
8. **It changes the trade sequence.** Fewer trades resolve, exits come later, more trades flatten, and the router takes
   a different set of offers. So the gate and U1 are rerun for every cell, from the rescaled trades; nothing of the
   registered runs is reused except the frozen inputs of 4.4.

**Two more, the drafter's.**

9. **The early years may be unchanged, and a reference year may not be (m2).** Under the year factor a year at or
   below the reference is left as it was, so many early-block starts can be identical to the reference. Such starts
   are printed as "identical", and every paired reading prints its share of starts differing at all (9.1 item 5). L_ref
   is the pooled median of 2020 and 2021, so unless the two years' medians tie with it, **the reference year whose own
   median is above the pooled one is compressed to the pooled level**, and the other is left unscaled. Its rows say so.
10. **The rounding can create ties.** Two distinct prices can round to the same tick, so a minute can reach a target
    and a stop together more or less often than before; the local walk gives every such minute to the stop (the
    cautious side, `atlas_local`'s header). Counted per cell (8.3).

### 4.6 How it is built without touching `vendor/`

- **The seam.** `atlas_a3.walk_minutes` takes the day's arrays through a callable, `arrays: Callable[[str], tuple]`
  (`vendor/stage2/scripts/atlas_a3.py:160-170`). The adapter wraps the callable the vendored `atlas_a3.bar_arrays`
  returns, applying 4.1's map with the session's factor, and nothing else.
- **The builders that call it internally.** P-16's `rc_width_screen.build` and P-14's builder (as
  `identity/gate_identity.py` makes P-14's call: `rc_screen.inputs()`, A3-BRK30's cell trades) call `bar_arrays` or
  read A3's cache themselves, and P-16's recomputes its cutoff from its own walk. So the adapter **re-composes** each
  builder in Q-71's pattern (`extended/campaign.py`): the vendored function's text copied verbatim under a guard that
  refuses unless its LF source hashes to its pin, a proof that the copy with its marked lines removed parses to the
  vendored function statement for statement, and **marked additions only**: (a) the wrapped arrays; (b) the frozen
  offers, rungs and shift of 4.4 passed in from the k = 1 build; (c) the scaled tick costs of 4.3 (the fee never
  touched); (d) no cache write.
- **Never** a substituted vendored attribute during a call (E-011, Q-47), never an edit of `vendor/`, and **no file a
  shared identity covers is edited** (E-104, E-117): the adapter is new modules only (12.1).
- **What a piece that cannot be built stops (M1), a declared failure scope, not a fallback.** A piece is something
  that cannot be built that way: a builder that cannot be re-composed, a cost that cannot be scaled through arguments
  or a re-composed copy, a shared file that would need an edit. **If such a piece serves only beside cells**
  (`yr_sc`, `tr_act`, `tr_sc`: the scaled tick costs, the trailing factor), **it stops those cells alone**, each named
  and recorded in the build's hand-back and in the run's manifest as "not built: <the piece>". It never stops `k1` or
  `yr_act`, and nothing replaces it. **If the piece serves `k1` or `yr_act`** (the map, the year factor, the
  re-composed builders at actual costs, the frozen inputs), **the build stops and reports**, and (c) does not run.
  **This scope is decided at build time, before step 1** (the re-read's n5), in the build's hand-back and its red-team
  read. A failure while a step runs on real bars is 13.2's (the step stops), never 4.6's: a beside cell that fails
  mid-run is not "not built".
- Downstream, the rescaled trades go through this repository's adapters unchanged: the gate through
  `extended/gate.py` (Q-47, held by Q-80, E-049) and the replay through `extended.user_beside.run_starts` (Q-17), with
  Q-94's recorder (`extended/replay_records.py`).

## 5. Data, blocks, the unit and the horizons

1. **(a2)'s unit** is the session; its summaries by calendar year and quarter, whole window.
2. **(c)'s unit** is U1's: one development start day, a fresh (unbound) bankroll and fresh accounts, the cell's trades
   replayed in historical order, a long replay of up to 252 sessions plus U1's exact-length runs (21, 63, 90, 126)
   (`vendor/stage2/scripts/user_journey.py`, `customer_slices.replay`), through Q-17's adapter. `USER_MILESTONES.md`'s
   definitions unchanged; a month is 21 sessions. **The starts:** every start U1 reads for `p14` and `p16`
   (`vendor/stage2/results/user_journey.csv`, section `start`), each reading on the starts with its horizon h left.
   And the gate's 500 paths over 504 sessions at each design's registered seed.
3. **The arms.** `verdict` (every R shifted by 4.4's frozen `lb - e`) the headline; `point` beside.
4. **Pairing.** Each new cell and its design's `k1` reference on the same start days and the same arm; in the gate, on
   the same seed and so the same resampled day indices (the rescaled day set has the same days). **The vendored code
   makes that a fact (the re-read's m2).** The gate's `_GateDraws` (`propedge/campaign/gate.py`) builds
   `SharedDayDraws({0: blocks}, seed=s)` for each path seed s. Its table is `SharedDayTable(n_history,
   seed=child_seed(s, 0, 0))` with `n_history = len(blocks)` (`propedge/campaign/shared_days.py`), and it draws from
   its own generator. **A path's day indices are therefore a function of its seed and the number of day blocks
   alone**, never of trade content. The gate's 504-session horizon lies inside the days the table draws at
   construction. So the pairing holds if each cell's day blocks carry the same dates, in the same order, as its
   design's `k1` blocks under both arms (`shifted_blocks` keeps the length). That is the oracle of 8.3. (The second
   text's route through the gate's `counters` argument is struck: that channel records RD-02's account counters, not
   day indices, and refuses the registered accounts.)
5. **The blocks, per measure** (RD-03 section 5 item 4, carried): **all starts** with h sessions left
   (`u_select.block(records, None, h)`), the headline; **the early block** (`u_select.block(records, "early", h)`); **the
   late block** (`u_select.block(records, "late", h)`, from 2024-01-02); by start year, means only, not purged,
   labelled. Each measure at its horizon h as RD-03's section 5 table fixes it (`u_select.MEASURES`; P and the shares
   ahead at months 1-3 at 63; S1, S3b and the month-6 net at 126; the month-12 net and S4b at 252). **The factor of a
   start's later sessions is their own year's**, so an early start's journey can run into a scaled year; no purge
   removes that, and it is labelled.
6. **The judged block's seal (E-026, E-041, E-037).**

   - **Judged-block reads:** `volatility_descriptive`

   - `volatility_descriptive`: (a2)'s reads from 2020-01-02 to 2026-07-16, **two in one run**: the bars through
     `extended.reader.read_bars`, and A1's `days` table (`date`, `day_kind`) through `extended.reader.read_walks` for
     Q-121's days identity (3.2, M4). Each is ledgered; both are made from a clean checkout of a committed commit, once
     (a further run only with `repeat=` under a row naming this file). It is not a choosing or fitting purpose (the
     reader's `CHOICE_WORDS`, `extended/reader.py:125`). The `Authorisation` the reader returns for it, in the order
     of 3.2, is the one passed to Q-121's module. None is built by hand (T-10's scan), so no other opens that module
     past 2023-12-29.
   - **(c) is not on that line.** Its engine reads are authorised by `extended.reader.authorise_engine_read` under the
     purpose `registered_design` (E-037), `design=["P-14", "P-16"]`, the declaration **the pinning row**, which names
     both designs (`extended.reader.names_design`), from `scripts/rd04_replay.py`, inside a clean run, ledgered. The
     reader admits `registered_design` outside a clean run without a ledger line, and it never checks this file's hash
     for that purpose. So **the replay's script refuses, before any authorisation and before any engine call (M3)**:
     1. unless `S2X_CLEAN_RUN` and `S2X_RUN_ID` are both set -- and, once the reader has returned, unless the returned
        `Authorisation.ledgered` is true (else it stops before the engine runs);
     2. unless `prereg/RD-04_volatility_drift.md` hashes (its LF sha256) to the pin the pinning row carries for it,
        read as `tests/test_declarations_fixed.py` reads pins (`` `prereg/RD-04_volatility_drift.md` sha256 `<hex>` ``
        in that row);
     3. **and by its own once rule, per part**, since the reader does not limit `registered_design` to one run. The
        script runs one part a run, `--part scorecard` (step 3) or `--part beside` (step 4), the part written into the
        ledger line's description. It refuses to start if `results/read_ledger.jsonl` holds a `registered_design` line
        from `scripts/rd04_replay.py` under the same row for the same part by another run id, unless `--repeat E-NNN`
        names a row that names this file.

     T-12 holds all three. **No build-time run of (c) touches real bars:** the build's smoke and timing runs use
     synthetic bars only (section 11's toy seed and its measuring seed). `identity/rd04_identity.py` is unaffected: at
     k = 1 it reveals nothing beyond the registered files.
   - **The identity** runs from `identity/rd04_identity.py` under the purpose `identity` and its own row, never under
     either of the above.
   - (a0) reads two vendored result files, not bars: no purpose; the step and its file hashes are recorded in the
     result's manifest.
7. **No NQ from 2026-07-17** is on disk or read.

## 6. The cells and the runs

### 6.1 (a2)

One pass over every development session (one bar read under `volatility_descriptive`), after its early-block identity
(8.2). No cell, no variant.

### 6.2 (c)'s grid

| cell | factor | costs | on P-14 | on P-16 |
|---|---|---|---|---|
| `k1` | 1 for every session | actual | reference (identity) | reference (identity) |
| `yr_act` | the year factor k_y | actual | new, **the headline** | new, **the headline** |
| `yr_sc` | the year factor k_y | tick costs scaled by k_y | new | new |
| `tr_act` | the trailing factor k_d | actual | new | new |
| `tr_sc` | the trailing factor k_d | tick costs scaled by k_d | new | new |

Each new cell: its walk (one rescaled walk per design and factor, shared by its two cost readings -- **four rescaled
walks**), its trades, U1's replay on both arms over every start with the exact-length runs, and its gate (500 paths,
point and bound, `k1`'s e and bound, with its zero-edge twin centred on the cell's own e, 4.4). **Every cell runs**,
except as 4.6's failure scope names: a beside piece that cannot be built stops its own cells, recorded.

### 6.3 The comparisons read (all paired, none a pick)

- each new cell against its design's `k1`: the headline `yr_act`; beside `yr_sc`, `tr_act`, `tr_sc`;
- `yr_sc` against `yr_act` and `tr_sc` against `tr_act`: the cost reading alone;
- `tr_act` against `yr_act`: the factor alone.

### 6.4 Counting

1. **No program family number and no level** (E-023 (1)).
2. **(a2):** one descriptive pass; **(a0):** two files' rows.
3. **(c) at 0 % with the placement off, both arms, every one run:** 2 references (identities) + 8 new cells = **10
   replays on two arms; 8 new cells**; **8 gates** for the new cells (the references' gates are 8.1's identities).
4. **Beside, verdict arm:** the denial ladder (`denial_10`, `denial_25`, `denial_50`) and the placement on (`rtp`) for
   every new cell: 4 x 8 = **32 replays**; the ten binding Focused Trader models (`extended.user_beside.FTP_BINDING`)
   for the four actual-cost cells (`yr_act` and `tr_act` on each design; m4): 10 x 4 = **40 replays**, not read for
   the four scaled-cost cells (40 replays not run, the gap named, Appendix C item 9); `k1`'s fourteen responses on each
   design checked against Q-44's per-start file: **28 reference checks**.
5. **Every block read** is recorded as read for volatility description (10, the binding).
6. **Nothing is selected.**

**In all:** one descriptive pass; two files' rows; 10 replays on two arms (2 references, 8 new cells); 8 gates; 72
replays beside (32 ladder and placement, 40 Focused Trader) and 28 reference checks; four rescaled walks; the honesty
series synthetic.

## 7. Parameters: fixed, beside, dropped

"Beside" means every value listed is run and read and none is chosen; there is no menu. **Searched: none.**

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| designs | what is replayed | fixed | P-14 and P-16 as registered | E-037; E-157 (c) |
| the map | how a price is drawn toward the open | fixed | `O_d + 0.25 x round(k x (p - O_d) / 0.25)`, half to even | 4.1; the note's 4 (c) |
| the anchor | the price each session is scaled about | fixed | the session's first open | the note's 4 (c); pitfall 6 |
| the trailing window | sessions in the trailing mean range | fixed | the 20 most recent prior walked ('n', 'b') sessions, Q-121's `trailing_means` | the note's 4 (a), (c); Stage 2 D-238's 20 sessions; Q-121 (E-163) |
| the reference years | the calm reference for L_ref | fixed: **the lead's choice** (m7) | 2020-01-02 to 2021-12-31 | the operator described the early years as calm (E-155: NQ's daily range in points has grown over the years while the contract stays fixed in dollars); the lead names 2020-2021, inside the choice block (E-157 (c); the note's 4 (c)), before any value of Q-121's or (a2)'s files existed. E-155 names no years |
| the reference statistic | how L_ref and L_y summarise | fixed | the inverted-CDF median (Q-121's `value_quantiles`) of `trail20_range_pts` over the walked sessions with a finite value, by the trading day's year | the note's 4 (c); Q-121's convention (M4), fixed before its values existed |
| **the factor** | one per year, or one per session | **beside** | `yr` (the year's, the headline), `tr` (the session's trailing, beside) | pitfall 2 |
| **the cost reading** | trade costs as charged, or the tick costs scaled | **beside** | `act` (the headline), `sc` (tick costs only; the fee as the engine charges it) | D-122 (1); D-324; pitfall 1; M1 |
| the cap on k | no amplification | fixed | k at most 1 | the question is a calmer market (E-155) |
| unscaled sessions | a blank `trail20_range_pts` (fewer than 20 prior walked sessions) | fixed | k_d = 1, counted | 4.2 |
| the twin's centre | the per-R edge the zero-edge twin removes | fixed | the cell's own e (the registered rule); the arms `k1`'s e and bound | 4.4; M2 |
| frozen inputs | offers, rungs, marks, table, shift, capacity | fixed | the k = 1 build's | 4.4 |
| arms | outcome shift | fixed | `verdict` the headline, `point` beside | CHARTER section 2 |
| denial, placement | firm discretion | fixed | 0 % and the placement off in the headline; the ladder and `rtp` beside | E-008; Stage 2 D-234, D-289 |
| Focused Trader models | beside | fixed | Q-17's ten, on the four actual-cost cells | E-007 (e); Appendix C item 9; m4 |
| horizons, blocks | replay length; starts read | fixed | U1's; RD-03's section 5 table; all, early, late | Stage 2 D-620 |
| the interval | uncertainty on paired readings | fixed | 9.2 | RD-02 section 9.2; E-058 (5) |

**Dropped, and why.**

- A second reference (the choice block's median, the note's "possibly"): one reference, the calm years; a second
  doubles the heavy cells. **Its relevance is to selection, said plainly (n5):** a replay scaled to the choice block's
  own level is the one that speaks to E-155's selection exposure (the judged block busier than the block a design is
  chosen on). It is dropped on cost, not on relevance; a later reading may add it, citing this one.
- Amplification (k above one, a busier market): not the question.
- Rescaling by the day's own range: pitfall 2.
- Re-detecting events or re-admitting marks on the rescaled bars: pitfalls 3 and 4.
- A range-scaled design: it needs a classification row first (E-157; the note's section 5), and it is a design, not a
  replay.
- P-15: not asked (E-157 names P-14 and P-16).

## 8. Before any reading: identities, oracles, mechanics

### 8.1 (c)'s identity, refusing (E-004, E-010; whole-window identities only from `identity/*.py`, E-026, E-041)

**Shared, owed by other items; this reading waits for each.** A wait is met only by a decision row whose third cell
begins with the positional token of E-104's form (`identity-holds: <id> @ <sha>`, parsed by
`extended/identity_tokens.py`), at the run's commit or an ancestor, with the identity's cover unchanged since
(`extended/identity_cover.py`'s `cover(id)`, never less):

- Q-05 (E-010): U1's start rows reproduced (`identity/stage2_identity.py`);
- Q-80 (E-049): `extended/gate.py` through the re-composed campaign, P-14's and P-16's registered gate paths at 500
  paths;
- Q-93 with Q-100 (E-059 (1)): U1's start rows through Q-17's adapter;
- Q-101 (E-068): U1's start rows with the replay recorder on.

**This reading's own, run first from `identity/rd04_identity.py` (label `rd04_identity`)**, from a clean checkout of the
reading's commit, under the purpose `identity` and the row that registers it (the lead's). **The script runs the
reference only:** the factor is the constant 1 for every session and the cost reading the constant `act`; no argument
selects a factor, a cost reading or a cell; before its first session it asserts both and refuses otherwise (T-11). It
must reproduce, through this reading's path (12.1 A-1 to A-3) at k = 1:

1. **The wrapper is the identity:** on every development session the wrapped callable's four arrays equal the vendored
   `atlas_a3.bar_arrays` callable's, bit for bit, missing positions included.
2. **P-14's walk and trades:** the walk built through A-2 equals the vendored A3 cache's rows
   (`vendor/stage2/data/atlas/A3/walks.parquet`) at every minute it walks, row for row, every column, exactly, and walks
   every minute P-14's trades are drawn from; the trades equal those the
   registered builder makes in the same process, every column, exactly; each R's e and bound equal the registered
   builder's.
3. **P-16's trades and marks:** the trades' content hash (`rc_dev_test.trades_hash`) equals
   `rc150_dev_test.TRADES_SHA256`; P-16's identity (b) holds as P-16 §3 states it (`rc_dev_test.trade_problems` with
   `rc150_dev_test.SPEC`); the admitted marks equal those the vendored `rc_width_screen.build` admits at 150 ticks in
   the same process; **each R's e and bound equal the registered builder's** (m6), as item 2 states for P-14. These are
   the frozen shift's source (4.4), so both designs' are checked.
4. **The gates:** P-14's registered gate paths, `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, `gate` run, 0 %
   denial, point and bound, through `extended/gate.py`, every `zero_edge_decomposition.PATH_COLS` column to 1e-6, all
   500 paths, at seed 20261131; **and P-16's**, `vendor/stage2/results/rc_s150_all_gate_paths.csv`, at seed 20261206.
5. **U1's start rows for P-14 and P-16**, through `extended.user_beside.run_starts` with the response `off` and the
   recorder on: `vendor/stage2/results/user_journey.csv` section `start`, configs `p14` and `p16`, both arms, every
   start, every column as E-010 compared them (money and the ratio to 1e-6; counts, days, dates and text exactly), with
   U1's own checks of every run's payouts and fees against the engine's totals.
6. **The scaled-cost path at k = 1:** P-14's and P-16's trades built with `sc` at k = 1 equal those built with `act`,
   bit for bit (trades only, no campaign; multiplication by 1.0 is exact). This is meaningful only with 4.3's
   definition of `sc` (the tick costs, never `fee_micro_eq`) and with T-4's toy campaign at k < 1 through the engine,
   which holds the fee charged equal to `SizingRule.fee_dollars(contracts)` under both readings (M1).

**Its cover, declared under Q-111's rule** (`extended/identity_cover.py`, E-119): `BASE` -- `extended/__init__.py`, the
folder `config/` whole (E-117), `vendor/MANIFEST_stage2.sha256` and `vendor/DATA_MANIFEST_stage2.sha256` -- plus
`identity/rd04_identity.py` and every repository file it imports, directly or transitively, as
`identity_cover.imports(script)` computes it. A change to any covered file after its token re-requires it.

**Inside (c)'s own run (no further read):** `k1`'s start rows equal U1's again (item 5's comparison, refusing), before
any new cell is read.

**A failure of `rd04_identity` stops (c)**: nothing of a new cell is computed, written or printed; the failure protocol
applies; nothing is rerun until it passes, and a rerun is a further read under `--repeat` (13). (a2) does not depend on
it. E-010's negative controls (the verdict rows against the point rows; a 2e-6 nudge) show that the comparisons are not
vacuous.

### 8.2 (a2)'s identity, refusing, before the judged block is read

Inside step 2 (section 13), **before the read under `volatility_descriptive` is authorised**: (a2)'s code run on the
choice block alone (2020-01-02 to 2023-12-29, a read that needs no purpose, Q-121's module without `authorised`)
reproduces Q-121's file `results/q121_vol_descriptive_a1.csv` -- every row of its four sections (`session`, `range`,
`band`, `band_mark`), every column of Q-121's `COLUMNS`, as text at the file's precision. This comparison is made in
memory; the `identity` section records only its counts. Then comes the whole-window run, with the reader's
authorisation. Its rows of the choice block must equal the choice-block run's again, refusing: the `session` rows dated
to 2023-12-29, the `range` and `band` rows of the years 2020 to 2023 and of their quarters, and **every** `band_mark` row,
its `block` row included (the re-read's n10: under the authorisation `band_mark` spans choice-block sessions only, with
Q-121's labels). These are compared in memory before they are dropped (3.2), and show the trailing means do not look
ahead. The `block` rows of `range` and `band` differ by definition, since they span different windows, and are not
compared. **A failure of the first
comparison stops (a2) before any judged-block bar is read; a failure of the second, or of Q-121's days or walk identity
over the whole window (3.2), stops (a2) before anything is summarised, printed or written. Either stops (c)**, whose
factors come from (a2)'s rows.

### 8.3 Oracles (an output outside them is an engine or adapter error, never a finding; each stops its step)

- **The actual prices, before the map (m6):** every present open, high, low and close of every session an exact
  multiple of 0.25, checked before the session is mapped; a failure names its date.
- **The map:** on every rescaled session and bar, low <= min(open, close) <= max(open, close) <= high; every price on the
  0.25 grid; |p' - O_d| <= |p - O_d|; the session's rescaled range within one tick of k times its range; missing bars
  in the same positions; every factor in (0, 1].
- **The frozen inputs:** every new cell's offers -- (date, slot or mark, side, stop in ticks) -- equal its design's
  `k1` offers, one for one; the day capacity equal; the per-R shift and the gate's `e`, `lb`, `e_by_rr` and `lb_by_rr`
  equal to `k1`'s; the state table's hash the registered.
- **The factors:** section `factor`'s L_ref equals the median recomputed from Q-121's file, and every k_y and k_d
  recomputed in step 3 from (a2)'s session rows equals the file's; for 2020 to 2023 each L_y equals Q-121's `range` row
  (4.2).
- **The factor applied is the session's own (m6):** for every session the wrapper maps, the k it applies equals the
  `factor` section's `k_year` (under `yr`) or `k_trail` (under `tr`) for the same `date`, the walker's day as
  `atlas_local.day_arrays` keys it. A session with no `factor` row is refused. This catches a trading-day against
  calendar-day key error, which the range oracle above cannot see, since it reads the k actually used.
- **The twin's mean is zero (M2):** on every new cell and every offered R, the mean of the R its zero-edge twin's
  blocks carry is zero to 1e-12. The mean is taken over **the trades with a finite `r_R`**, as
  `confirm_fv3.edge_stats` takes them for e (the re-read's n7), and on the blocks, not on the engine's realised R. The
  engine's fee re-pricing at size moves the realised mean off zero, as it does for the registered twin.
- **The gate's zero-edge twin:** the mean gross payouts per funded account do not exceed $2,000 beyond its Monte Carlo
  interval; the pass rate per evaluation does not exceed 2/5 beyond its interval (propsim D-02).
- **The gate's pairing (n3, m2):** every new cell's day blocks carry the same dates, in the same order, as its
  design's `k1` blocks, under both arms. Their count is then equal, so by the vendored `SharedDayTable` (5 item 4)
  every path draws the same day indices.
- Every payout request at most min(50 % of the balance, $2,000) and at least $125, paid at 90 % less the method's fee
  (`payout_max_frac_of_balance`, `xfa_std_cap`, `payout_min`, `profit_split`, Stage 2's verified ledger).
- **No write under `vendor/stage2/data`** during the run: the data folder's file list, sizes and modification times
  equal before and after each step.

### 8.4 The mechanics, printed first

For each new cell beside its `k1`, before any scorecard measure. They describe where the amplitude binds; each names its
source (the walk's kind columns; Q-94's recorder; the gate's rows):

- **resolution (D-212):** per year and offered R, the share of offers unresolved at 15:08 (both sides pooled, kind
  columns only), against D-212's 5 % (D-308), each failing year and R flagged **"fails D-212 here: a finding"**; for
  P-14 also by hour and rung, as the rung map reads it; the count of frozen marks and hour-rung pairs that would fail
  the cutoff on the rescaled walk (4.4);
- **supply:** per year, the trades the router takes per session (median, p10, p90), the share of sessions at the
  router's five, the median minutes from entry to exit of taken trades, the share of taken trades flattened, the
  minutes reaching a target and a stop together (pitfall 10);
- **the gate's pooled columns:** trades per day, `share_trades_skipped_busy`, `share_trades_at_tier_cap`;
- **the journey's counts:** evaluations bought, passes, funded accounts activated and lost, payouts, by start year;
- **not read, named:** how often the Combine's consistency cap and the 45-tick stand-aside bind by year -- no record
  this reading's path carries holds them (the note's section 7 asks; a later reading with a counters channel can).

A cell identical to its `k1` on every start (every factor 1) is reported as **"no change at this amplitude"**.

## 9. The reading (CHARTER sections 2-3; E-008, E-014, E-023, E-134 (2))

### 9.1 What is read

**(a0) and (a2):** the rows of sections 3.1 and 3.2, by year and quarter, as described quantities. No interval, no
test, no trend fitted.

**(c):** every cell and its `k1`, both arms (the verdict arm the headline), every block of section 5:

1. **The scorecard.** P, S1 to S5c, S2, S3d, S6 and Q, as `USER_MILESTONES.md` defines them; sessions and cash to the
   first pass and to the first payout; payouts per fee dollar (S3c, comparable within a design only, E-008).
2. **The guard row (E-134 (2)), printed with every P.** The mean net at months 1, 2 and 3; the month-6 and month-12 net
   (mean, p10, p50, p90); CVaR10 (`extended.user_measures.cvar`) of the month-3, month-6 and month-12 net; the long-run
   gate's growth on the required bankroll at the bound with its ruin probability (item 7) -- the gate entry Stage 2
   D-312's `pf_growth_on_base_p50` of the bound arm, as E-158 (M1) fixed it for RD-03, never `median_log_growth`;
   `k1`'s entry from its design's registered gate row; no P printed beside a missing guard value (E-158 (M2)).
3. **E-014's journey variables:** sessions to break-even and the share reaching it by months 1, 2, 3, 6 and 12; the
   share that later falls back; the share of months with a positive net change; the longest run of months without a
   payout; payouts per month.
4. **Each measure as a distribution over start days** (median, p10, p90), with 9.2's uncertainty on every paired
   difference.
5. **The paired readings, by month:** for every measure of items 1 to 3, cell less `k1` (and 6.3's other comparisons):
   the per-start difference (p10, p50, p90); the share of starts differing at all; the shares better, equal and worse at
   months 1, 2, 3, 6, 9 and 12 (for the share ahead: ahead under the cell and not the reference, under both, under
   neither, under the reference and not the cell); the mean difference with 9.2's interval, its window count and its
   minimum detectable difference. **The step-shaped series (n4):** where a cell leaves some starts identical to `k1`
   (under `yr`, the early starts of an unscaled year), the paired series is zero there and nonzero later, so it is not
   zero-mean around a common mean as 9.2's honesty shapes are. Every paired row whose share of starts differing is
   below one carries "some starts identical: the interval describes the average over windows, not a common effect".
6. **E-007 (e)'s readings beside**, through Q-17's adapter, verdict arm, U1's exact-length runs on every 21st start
   index (`EXACT_EVERY`): the denial ladder and the placement on for every new cell, the ten binding Focused Trader
   models for `yr_act` and `tr_act` on each design (m4; the gap named on the four `sc` cells: "Focused Trader models
   read on the actual-cost cells only"); on every beside row the full guard row, its gate entry the cell's 0 % gate,
   labelled; P by month, P under a bankroll limit, the effective sample size and the MDD.
7. **The long-run gate, every new cell:** at its design's registered seed (P-14's 20261131, P-16's 20261206), 500
   paths, point and bound at `k1`'s e and bound, with its zero-edge twin centred on the cell's own e (4.4), paired with
   the registered paths: growth on the required bankroll, the required bankroll, the ruin probability, payouts a
   month, days to the first payout, purchases a year. **Nothing is a floor: nothing is carried.**
8. **The labels, on every row of (c):** "described, not carried"; "today's market with its points volatility turned
   down, not a replay of 2020-2021" (pitfall 5); "first-order: offers, rungs, marks, table and shift fixed" (4.4); "the
   tick-scale bounce is compressed with the path; a real calm market keeps it; neither reading restores it" (pitfall 1,
   m3); on `sc` rows "tick costs scaled by the factor (D-122); the fee as the engine charges it"; on `yr` rows "the
   year factor uses the year's own later sessions: a counterfactual's scale, not a rule a user could follow" (m2); on
   `tr` rows "the trailing factor (beside)".
9. **Not modelled, said wherever (c) appears:** a calmer market's other changes (pitfall 5); the consistency cap's and
   the stand-aside's binding by year (8.4); a user who stops when their money runs out; taxes; payouts unavailable in
   holiday hours; the move to a Live Funded Account; Topstep's unstated news rules (E-034).

**How many intervals, and what chance alone gives.** (c)'s output prints the number of 90 % intervals it shows, that
each is marginal and none simultaneous, and the count expected to exclude zero by chance alone were there no effect
anywhere -- a tenth of them. A count, not a level.

### 9.2 The uncertainty on each paired reading (fixed now)

Descriptions, not tests: nothing is compared with a critical value to decide anything, and no reading has a level
(E-023 (1), E-025). **The method is reading PP's section 9.2, items 1 to 7, unchanged** (`prereg/RD-02_payout_policy.md`,
pinned; built in `extended/pp_reading.py`, imported, never copied), with this reading's own seed for its honesty series:

1. **The windows (E-058 (5)):** at horizon h on a block, the starts in order cut into consecutive windows of h starts
   from the block's first (a last incomplete window dropped), every other window kept from the first; n_w printed with
   every reading.
2. **The interval:** two-sided 90 %, Student t on the kept windows' means, n_w - 1 degrees of freedom, printed only
   when n_w is at least 4 and the means are not all equal; else "too few separated windows for an interval".
3. **The window sign count**, always printed.
4. **The effective sample size**, Bartlett, lag window h (`extended.user_measures.n_eff_bartlett`), beside.
5. **The minimum detectable difference:** (t(0.95; n_w - 1) + t(0.80; n_w - 1)) times the kept windows' standard error,
   printed beside each mean and before it.
6. **A series zero on every start** prints "identical"; one whose kept means are all equal prints its sign count alone.
7. **The interval's honesty, beside, on overlapping series:** RD-02 9.2 item 7's 21 shapes and construction, 20,000
   series per setting, at every (h, n_w) at which this reading prints an interval; **seed 20262310**, each setting
   drawing from `numpy.random.default_rng([20262310, 1, shape, h, n_w])` (`extended.pp_reading.honesty_rng`'s keys),
   the build's test from `[20262310, 0, ...]`, never these keys. The label "under-covers at this window count" where the
   lowest coverage of gauss, ahead and paired at its (h, n_w) is below 0.88; beside every interval, without a
   threshold, the lowest lumpy or persistent coverage, its shape and its misses above and below.

**The gate** is read as two sets of 500 paths on the same seed: each row's two values side by side, no interval.

### 9.3 The leak clause (E-157; the note's 4 (a), "The leak, stated")

(a0), (a2) and (c) describe the judged block's volatility and P-14's and P-16's supply in it. (a2) writes no by-mark
row of the judged block (3.2, M5): `band_mark` -- the side-free open share and first-exit times at every P-16 mark and
P-14 slot, by year -- is the quantity Stage 2's `mark_resolution` admits marks by, and D-212's per-year resolution line
is a floor a family must clear on the judged block (CHARTER section 2). Its judged years would foretell that floor, so
they are never written. The pooled `band` rows remain, and the clause below governs them. **A residual leak, accepted
and recorded (the re-read's n11):** the judged years' `band` rows, pooled over all 266 P-16 marks or all 22 P-14 slots
at the fixed bands, are close to an every-mark design's resolution by year. They are not reopened; items 2 and 3 govern
them, read by the red team and the auditor.

**The clause is the lead's program rule (M5).** A described reading's text cannot bind another declaration; only a
decision row can. So **the pinning row adopts items 1 to 3 as the lead's program rule**, binding every later
declaration **and every decision row that fixes a parameter**. It holds **from the commit of step 2's first run**
(13.2), whatever that run's outcome. Step 1 reveals nothing beyond the registered files, so the rule does not start
there. The lead's row recording step 2's first run **begins its third cell** with the literal token
`` `RD-04 read: step 2` `` (E-104's positional form, so a row that only quotes the token is not it) and is written
before any later declaration is pinned. Under the rule:

1. **Every later declaration** -- a family file, a described reading, a calibration plan, or any registration's text
   -- **states in its header that it was written after RD-04 was read**, naming the rows that recorded RD-04's steps
   (at least the step-2 row). **A text written before the read and unchanged since (the lead's ruling on the re-read's
   m5)** need not be re-drafted. Instead, the row that first pins it carries the literal form
   `` `written before RD-04 was read, unchanged since <commit>: <path>` ``, which the test checks against git: the
   file at `<commit>`, under its path or its draft name, has the pinned LF sha256, and `<commit>` is older than (an
   ancestor of, and not) the read's commit and the step-2 row's commit. The form sits in the pinning row, not in the
   file, because a file cannot name a commit at which it was already byte-identical to itself with that name inside
   it.
2. **None cites a figure of RD-04's result files** (`results/rd04_descriptive.csv`, `results/rd04_replay.csv`,
   `results/rd04_replay_gate.csv`, `results/rd04_replay_beside.csv`) **as the reason for any parameter**: its value, its class, its range or its grid. A
   parameter whose reason is such a figure was chosen after a look at the judged block: exploratory, reported apart, in
   its own row, `exploratory=True`. A later declaration may cite RD-04 as the reason a *question* is asked (for example,
   why a range-scaled family is declared at all), never as the reason for a *value*.
3. **The choice block stays the only source of a family's choices** (feature-rules section 4). Q-121's (a1),
   `results/q121_vol_descriptive_a1.csv`, which reads the choice block only, may be cited as a reason; its rows equal
   (a2)'s rows there (8.2), and only the choice-block rows of (a2) may be cited, by their Q-121 source.
4. **The red team's read of every later declaration checks 1 to 3, and so does the auditor's read of a row that fixes
   a parameter.** The lead's family template carries the line (section 14 item 4).
5. **Knowledge already on record is disclosed, not cleansed:** D-554, D-580, D-582, D-605 and the red team's M2-4
   (section 2) carried part of this before RD-04; a later declaration that leans on them says so as it would anyway.
6. **Each later declaration's "drafter's own reads" disclosure lists RD-04's result files if its drafter opened any**,
   as this text's section 2 lists what its drafter read.

**The leak-clause test, declared now and built with T-0, before the pin: `tests/test_rd04_leak_clause.py`** (fast
tier). It fails closed (the re-read's M1). On `DECISIONS.md` and the read ledger as they stand:

- **two anchors.**
  - *The step-2 row* is the first decision row, in the log's order, whose third cell begins with the token
    `` `RD-04 read: step 2` ``.
  - *The read* is the first line of `results/read_ledger.jsonl` whose `declaration.ref` is
    `prereg/RD-04_volatility_drift.md` and whose purpose is `volatility_descriptive`. The ledger is append-only, and
    that line is written before the bars are read, so it exists from step 2's first run on.
  - **Once the read exists, the test fails unless a step-2 row exists.** A missing or mistyped row can never switch
    the rule off.
  - With neither anchor present, the test binds nothing on the real log; its synthetic cases still run.
- **in scope**, RD-04's own file excepted: every declaration -- a `` `prereg/F-..md` `` or `` `prereg/RD-..md` `` pin as
  `tests/test_declarations_fixed.py` reads them, or a `` `docs/calibration/...md` `` pin -- whose path is **first**
  pinned in either of two places:
  - (a) **in or after the step-2 row**, the row itself included;
  - (b) **in a row absent from `DECISIONS.md` at the read's commit**: the ledger line's `who.commit`, the run's own
    commit, which precedes the read, read with `git show`. A `DECISIONS.md` that cannot be read there fails the test.

  A file first pinned earlier and cited again later is exempt.
- **each such file** must satisfy one of two forms, or it fails the suite, and so the pre-commit hook:
  - its header -- the text before its first line beginning `## `, whitespace collapsed -- holds the words "written
    after RD-04 was read" and the step-2 row's id;
  - or the row that first pins it carries item 1's pre-read form, and that form holds against git.
- **it is not vacuous.** Synthetic logs and files exercise each rule. The cases include the re-read's three
  fail-open routes, and each of those three was shown to pass silently under the second text's test:
  - a pin inside the step-2 row;
  - a pin after the run but before the step-2 row, on a synthetic git history;
  - a ledger read with a mistyped step-2 row.

  The pre-read form is admitted for an unchanged earlier draft, and refused in three cases: a text changed since, a
  commit not older than the read, and a commit that does not exist.

The test enforces item 1 mechanically. **Its phrase check is lexical (the re-read's n12):** a header saying "not
written after RD-04 was read" passes. That, and items 2 and 3, are the red team's and the auditor's reads (item 4): no
test can tell a reason from a figure.

**The binding.** The judged block's bars are recorded as read for volatility description (`volatility_descriptive`),
and P-14's and P-16's whole window as read for a calm-regime replay. A later reading of these measures names this one,
states what changed, and reads no block of it as fresh.

## 10. What the reading delivers, and what each outcome means

- **It delivers** (a0)'s rows, (a2)'s description by year and quarter, and (c)'s replay of P-14 and P-16 at a calmer
  amplitude, each beside its reference.
- **It does not deliver** a carried design, a registration id, a confirmation, a claim at a level, a correction of any
  other result, or a parameter for any later design (9.3).
- **No outcome passes or fails.** What follows from each, fixed now:
  - (a2)'s identity fails (8.2): (a2) stops before any judged-block bar is read, and (c) does not run (its factors come
    from (a2)); the failure protocol applies;
  - `rd04_identity` fails (8.1), or a shared identity's wait is unmet: (c) stops; (a0) and (a2) stand;
  - an oracle of 8.3 is breached: an engine or adapter error; its step stops and the failure protocol applies;
  - a piece of a beside cell cannot be built (4.6): that cell alone is not run, named and recorded; `k1` and `yr_act`
    run; nothing replaces it;
  - **a replay cell fails D-212's resolution line in some year and R: a finding**, flagged on its rows and read; no
    cell is rerun, re-frozen, dropped or re-admitted because of it;
  - a cell identical to its reference: "no change at this amplitude";
  - the headline shows a large fall in P or in supply: a description of how much of the registered scorecard is points
    volatility; it changes no rule, no design and no verdict. **What the lead may do with it** is declare a new
    question (section 9.3 item 2: a question, not a value) -- for example the classification row for range-scaled
    brackets (E-157);
  - the cost readings straddle the reference: printed side by side; neither is chosen.
- **No confirmation.** Nothing is carried; NQ from 2026-07-17 is not touched.

## 11. Seeds, fixed now and checked

| seed | status | what it draws |
|---|---|---|
| 20262310 | in use | 9.2 item 7's honesty series (keys `[20262310, 1, shape, h, n_w]`) and the build's test of it (keys `[20262310, 0, ...]`) |
| 20262311 | in use | the build's synthetic bars and toy campaigns (T-1 to T-7, T-10, T-12 to T-14), T-4's toy campaign at k < 1 included, and every smoke run of (c)'s path during the build (5 item 6) |
| 20262312 | in use | the synthetic bars and campaigns of the window's length on which the run's time and memory are measured before step 2 and before step 3 (13) |
| 20262313 | reserved, unused | -- |
| 20262314 | reserved, unused | -- |
| 20262315 | reserved, unused | -- |
| 20262316 | reserved, unused | -- |
| 20262317 | reserved, unused | -- |
| 20262318 | reserved, unused | -- |
| 20262319 | reserved, unused | -- |

**What draws randomness, stage by stage:**

- **step 1, the identity:** the gates at P-14's 20261131 and P-16's 20261206 (inherited, as registered); U1's replays at
  0 % draw nothing (the path seed feeds only the enforcement stream, `identity/user_beside_identity.py` (1));
- **step 2, (a0) and (a2):** nothing;
- **step 3, (c):** the rescaling draws nothing; P-16's sides are its registered coin at seed 20261102 and P-14's its
  registered event sides, unchanged by the map; the gates at the same two registered seeds, so their paths pair with
  the registered ones; U1's replays at 0 % draw nothing; the beside bounds' era bootstrap at the registered era seed
  (`config/atlas_a3.yaml`, `bounds.era_seed`, as `atlas_a3.bounds` reads it), never used; the honesty series at
  20262310;
- **step 4, the readings beside:** the denial ladder's start seeds, Q-17's `lockstep.child_seed(20261920, 0,
  start_day)` (`extended.user_beside.start_seed`, E-024), as `run_starts` draws them -- no keyword takes another seed,
  so `k1`'s ladder rows reproduce Q-44's.

**The check, 2026-11-17 (the machine clock), on the first text.** Two word-bounded searches for `2026231[0-9]`, every
file type, code and tests included, the licensed data excluded:

- `git grep -IwnoE "2026231[0-9]" <ref>` on every local and remote ref of the repository (22 refs), the vendored
  snapshot and its results included;
- `grep -rIownE --exclude-dir=.git --exclude-dir=data "2026231[0-9]"` on the working files of the main tree, of every
  worktree under `%LOCALAPPDATA%\stage2-extended-wt\` and of everything under `%LOCALAPPDATA%\stage2-extended-runs\`,
  before this file was written.

They found the block nowhere. **Repeated on 2026-11-17 for the second text, before T-0 was written** (`git grep -IlwE`
on all 23 local and remote refs; `grep -rIlwE` with the same exclusions on the same working trees, the red team's
uncommitted note in the main tree included): the block was found in this file alone, on the refs carrying it.

**What T-0 holds (m5, RD-03's `DECLARED_USES` form).** Section 11's table lists the block's ten seeds once each, three
in use and seven reserved; other mentions in this text of a seed in use are uses, not rows. **No other declaration
under `prereg/`, no vendored file (the licensed data excepted) and no review's or audit's scratch (`docs/reviews/`,
`docs/audits/`) holds a seed of the block.** In the code and tests (`extended/`, `identity/`, `scripts/`, `tests/`) a
seed of the block appears only in the files `DECLARED_USES` names. That is T-0's own file until the build adds its
files, and the build's T-9 holds each added file to the uses this section declares. T-0 passes on the text pinned
(E-152's precedent). **The lead's rows name the block by reference** ("RD-04's section 11 block"), never by number,
since a row is no use. The block lies outside the range 20262000 to 20262199 that Q-82's and Q-108's tests scan, and
outside RD-03's own block of ten (its section 12, named here by reference only: RD-03's T-0 refuses its seeds in any
other declaration).

## 12. The build: adapters and tests

### 12.1 The adapters (in `extended/`, never in `vendor/`)

| id | adapter | what it adds |
|---|---|---|
| A-1 | the map and the factors (`extended/rd04_rescale.py`) | 4.1's map as a wrapper of an `arrays` callable, with a factor per session, **applied at every k, 1 included** (no short-circuit, m6), each session's actual prices checked on the 0.25 grid before mapping, and each applied k checked against the `factor` section's row for its `date`; 4.2's L_ref, L_y, k_y and k_d from a `session` table by Q-121's `value_quantiles`, L_ref passed in as a constant; no bar read of its own |
| A-2 | the builders re-composed (`extended/rd04_replay.py`) | P-14's and P-16's trade builders copied verbatim in Q-71's pattern (a hash guard on each vendored source; the statement-for-statement proof), with marked additions only: the wrapped arrays (A-1); the frozen offers, rungs, marks and shift passed in (4.4); the scaled tick costs (4.3: the two tick terms times k, `fee` and `fee_micro_eq` never touched); no cache write; the vendored walk, cutoff, coin and bounds functions imported, never copied |
| A-3 | the cells, the gates and the replays (`extended/rd04_replay.py`) | each cell's campaign from its trades with the frozen shift and capacity, the gate's `e`, `lb`, `e_by_rr` and `lb_by_rr` `k1`'s, the zero-edge twin centred on the cell's own e (4.4, M2), through `extended/gate.py` (each cell's day blocks held to `k1`'s dates and order, 5 item 4, 8.3) and `extended.user_beside.run_starts` with Q-94's recorder, unchanged; nothing in a shared covered file edited |
| A-4 | the reading (`extended/rd04_reading.py`, `scripts/rd04_descriptive.py`, `scripts/rd04_replay.py`, `identity/rd04_identity.py`) | sections 3, 8 and 9 in section 13's order; (a2) through Q-121's module with the reader's `Authorisation` (3.2) and Q-121's two identities imported from its script; 9.2 by RD-02's functions (`extended/pp_reading.py`, imported); (c)'s three refusals and its once rule (5 item 6); the waits by `extended/identity_tokens.py` and `extended/identity_cover.py`. this reading's files carry the prefix `rd04_` (n6; Q-121's synthetic helper is now `tests/q121_synthetic.py`, E-166); no `Authorisation` built by hand; (a2)'s module-sha refusal (3.2) |

### 12.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 (before the pin; **built with the second text**, extended with the third) | `tests/test_rd04_draft.py`, in RD-03's form: exactly one RD-04 declaration under either name, every check passing on a copy under the pinned name; the pin-time form (the title, the `id` and `confirmation_tests_on_this_market` rows, a status that is not a draft's); **the hash pin-readiness** -- the text copied under the pinned name into a temporary tree whose `DECISIONS.md` pins its LF sha256 is admitted by the reader's declaration check (`extended.reader._family`) for `volatility_descriptive`, refused for a purpose not on its line and refused once one byte changes; **one `Judged-block reads:` line**, its one purpose `volatility_descriptive`, not choosing, not `identity` or `registered_design`; **the seed block** -- section 11's table lists the ten once each, three in use and seven reserved, and no other declaration, vendored file, review or audit holds one, nor any code or test outside `DECLARED_USES` (m5); the counts of 6.4 recomputed from 6.2's grid; **Q-121's names and interface** -- the file, columns, sections and functions the text gives Q-121 exist in its merged code, `authorised` is a keyword-only parameter of `check_span`, `check_days`, `describe`, `summarise` and `output_problems`, and the module's `AUTHORISED_PURPOSE`, `AUTHORISED_KIND`, `AUTHORISED_DECLARATION` and `AUTHORISED_LAST_DAY` are `volatility_descriptive`, `described_reading`, `prereg/RD-04_volatility_drift.md` and the reader's `JUDGED_END` (the re-read's m4, so 14 item 2's trigger is mechanical); the identity's cover declared under Q-111's rule; Appendix C's rows numbered and filled; **the leak-clause test's declaration** -- 9.3 names `tests/test_rd04_leak_clause.py`, its token, its phrase, its pre-read form and its ledger anchor, and that file exists and checks the same |
| T-1 | A-1's map on synthetic bars (seed 20262311): every price on the grid; the bar order kept; the anchor at the first open; |p' - O_d| at most |p - O_d|; the range within one tick of k times the range; missing bars kept; at k = 1 bit for bit; **the map called on every session at k = 1, by a call count** (m6); an off-grid actual price refused before mapping; a factor outside (0, 1] refused |
| T-2 | A-1's factors: L_y and L_ref Q-121's inverted-CDF medians of `trail20_range_pts` over the walked sessions with a finite value, by the trading day's year, and not numpy's interpolating median (an even-count toy where the two differ); k_y = min(1, L_ref / L_y); **with L_ref held fixed and passed in** (m1), L_d and k_d unchanged when any session from d on is changed (skill feature-rules); a session with a blank trailing value unscaled and counted |
| T-3 | the frozen inputs: on a toy where the rescaled walk would admit fewer marks or another rung, the cell's offers are still the reference's; the shift and the capacity the reference's; P-14's rung map read from its pinned file only |
| T-4 | the cost readings (M1): under `sc` the entry, stop or breakeven and flatten ticks multiplied by k and `fee` and `fee_micro_eq` untouched, under `act` nothing touched; account fees untouched under both; at k = 1 the two equal bit for bit; **and a toy campaign at k < 1 through the engine's sizing under `per_trade_at_size`** (seed 20262311): the fee charged equals `SizingRule.fee_dollars(contracts)` under both readings, and the tick costs differ by exactly (1 - k) of their sum |
| T-5 | no write under the data folder: the replay path on toy bars in a temporary tree whose data folder is listed before and after (names, sizes, times) and must be unchanged; `cached_walk` never called with `write=True` on wrapped arrays |
| T-6 | 9.2 on RD-02's functions with this seed: the kept windows, the interval from four kept windows with a spread, the sign count, the zero-series rule, the MDD's formula, and the honesty series' keys `[20262310, 0, ...]` drawn only by the test |
| T-7 | 8.3's oracles on toys, each shown to fire on a hand-broken case: the off-grid price, the map, the frozen inputs, the factors, the session's own factor (a calendar-day key), the twin's mean (a twin centred on `k1`'s e), the payout rules, the pairing |
| T-8 (`slow`, `heavy`) | 8.1 items 1 to 6 at 4 paths and 4 starts per design and arm, through `identity/rd04_identity.py` |
| T-9 | section 11's seeds appear nowhere in the build's commit outside the uses section 11 declares |
| T-10 | (a2)'s order and its reads: the whole-window read is not authorised before the early-block identity holds; the identity fires on a nudged cell of a toy Q-121 file; the early rows re-checked after the whole-window run; Q-121's module refuses a judged day without `authorised` and with an `Authorisation` of another purpose, kind or declaration or a choice-block one, and accepts RD-04's; **no `band_mark` row in the written file and none printed** (M5); Q-121's `COLUMNS` unchanged in its sections; `k_trail` and `k_year` only in `factor`; the days identity's A1 read made under `volatility_descriptive`; **`summarise` called with the authorisation**; **refused when the imported `extended/vol_descriptive.py` does not hash to its blob at the commit in Q-121's manifest** (m3); **no `Authorisation(` constructed directly in any `rd04_` file**, by a scan (n1) |
| T-11 | `identity/rd04_identity.py` runs the reference only: the factor 1 and the cost reading `act` constants; no argument naming a factor, a cost reading or a cell; any flipped refuses before the first session |
| T-12 | (c)'s refusals on a toy tree and ledger (M3): refused without `S2X_CLEAN_RUN` or `S2X_RUN_ID`; refused when the returned `Authorisation.ledgered` is false; refused when `prereg/RD-04_volatility_drift.md` does not hash to the pinning row's pin, or the row carries none; then the once rule: a second run of the same part under the same row refused, the other part allowed; allowed with `--repeat` naming a row that names this file, once; a row not naming this file refused |
| T-13 | the labels of 9.1 item 8 on every (c) row, and 9.1 item 5's step-shape label on every paired row whose share differing is below one (n4); D-212 failures flagged and never filtered; no P printed without its guard row; the count of intervals and the tenth expected by chance printed |
| T-14 | A-3 with the factor 1 and `act`: every gate row, replay and recorder row equals the path without A-1 and A-2, bit for bit, on toy campaigns |
| T-15 (before the pin; **built with the second text, rebuilt with the third**) | `tests/test_rd04_leak_clause.py`, the leak-clause test of 9.3, failing closed: once the read ledger holds RD-04's `volatility_descriptive` line, a step-2 row must exist; every declaration first pinned in or after the step-2 row, or in a row absent from `DECISIONS.md` at the read's commit, holds "written after RD-04 was read" and the step-2 row's id in its header, or its pinning row's pre-read form holds against git; on synthetic logs and synthetic git histories it refuses, admits, exempts and binds nothing as 9.3 says, the re-read's three fail-open routes among them |

## 13. Outputs and the run

### 13.1 Files

Each written with its sidecar manifest through `extended.results.write_result`:

- **`results/rd04_descriptive.csv`** (step 2), sections:
  - `identity` -- (a2)'s comparisons with Q-121's file (8.2) and Q-121's days and walk identities over the whole
    window: `check`, `holds`, `compared`, `differing`, `problems`;
  - `a0` -- the gate files' rows as read: `source`, `source_sha256`, `gate_section` (`period` or `drift`), then every
    column of the source row, as text;
  - `session`, `range`, `band` -- **Q-121's sections as its `summarise` writes them, in Q-121's `COLUMNS` unchanged**
    (M4): `session` one row a session of any kind with a bar (`date`, `day_kind`, `bars`, `walked`, `range_pts`,
    `range_pct`, `trail20_range_pts`, `trail20_range_pct`, `band_ticks_010`, `band_ticks_025`); `range` by
    `period_kind` (`block`, `year`, `quarter`) and `measure` over the walked sessions (`n`, `median`, `p10`, `p90`);
    `band` by period, `set`, `band` and `rr`, pooled over the set's marks (`n`, `open_share`, `median`, `p10`, `p90`).
    **No `band_mark` section** (M5, 3.2);
  - `factor` -- (a2)'s own: one row `l_ref` (`l_ref_pts`, `source`, `source_sha256`, `sessions`); per session (`date`,
    `k_trail`, `k_year`); per year (`year`, `l_year_pts`, `k_year`, `sessions`, `k_trail_p10`, `k_trail_p50`,
    `k_trail_p90`, `sessions_unscaled`).

  The file's columns are `section`, then Q-121's `COLUMNS` after its own `section`, then (a2)'s own columns; each
  section fills its own and leaves the rest blank.
- **`results/rd04_replay.csv`** (step 3), sections `identity`, `oracle`, `frozen`, `mechanics`, `resolution`,
  `bounds_beside`, `scorecard`, `guard`, `paired`, `coverage`; every row keyed by `design`
  (`p14`, `p16`), `cell` (`k1`, `yr_act`, `yr_sc`, `tr_act`, `tr_sc`), `arm`, `block` and, where it applies, `measure`,
  `h`, `year`, `rr`, `response`; the scorecard's columns `n_starts`, `mean`, `p10`, `p50`, `p90`; the paired columns
  `diff_mean`, `diff_p10`, `diff_p50`, `diff_p90`, `share_differing`, `better`, `equal`, `worse`, `n_w`, `ci_lo`,
  `ci_hi`, `sign_pos`, `sign_neg`, `n_eff`, `mdd`, `under_covers`; the resolution columns `offers`,
  `unresolved_share`, `d212_line`, `fails_d212`; and the labels of 9.1 item 8 in a `labels` column.
- **`results/rd04_replay_gate.csv`** (step 3) -- the gate rows: `design`, `cell`, `shift` (point, bound), `twin`, the
  gate's own columns as `extended/gate.py` writes them.
- **`results/rd04_replay_beside.csv`** (step 4), sections `reference_checks` (`k1`'s fourteen responses against Q-44's
  per-start file: `design`, `response`, `holds`, `compared`, `differing`, `problems`), `ladder`, `rtp`, `ftp`, each
  beside row with the scorecard's and the paired columns above, its full guard row and its gate entry labelled "the
  gate at 0 %". Step 4 writes its own file: no result file is written twice or overwritten.

**Each manifest carries:** `prereg_id` `RD-04` and its pinning row; the rows under which `rd04_identity`, Q-05, Q-80, Q-93
with Q-100 and Q-101 held, each with its sha and the run's head (none for step 2); Q-121's file, its sha256, its row and
the LF sha256 of the `extended/vol_descriptive.py` (a2) imported, **checked equal to that file's at the commit in Q-121's manifest before any authorisation** (3.2, m3); any beside cell not built (4.6), with its piece;
the cell and run counts (6.4, as run); each cell's trades' content hash (`rc_dev_test.trades_hash`'s form) and its
walk's row count; every seed, the inherited ones named; every parameter of section 7 with its class; the commit and blob ids of every adapter run; the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`, checked
before the first read; `exploratory=False` (nothing is chosen after a look), every row labelled "described, not
carried".

### 13.2 The run, in four steps

Each from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock (`run.lock`, skill
`run-lock`), one heavy job on the machine, watched to its exit; **each step only after the lead's row records the one
before**:

1. **the identity:** `identity/rd04_identity.py`, under the purpose `identity` and its own row. **A failure stops (c)**;
   step 2 does not depend on it and runs once the lead's row has recorded step 1, whatever its outcome.
2. **(a0) and (a2)** (`scripts/rd04_descriptive.py`): (a) (a0)'s two files' rows, each file checked against the vendored
   manifest first; (b) (a2)'s early-block identity (8.2), refusing, before any authorisation; (c) the reads under
   `volatility_descriptive` (the bars and A1's `days` table), Q-121's days and walk identities over the whole window,
   the whole-window computation through Q-121's module with the reader's `Authorisation`, its choice-block rows
   re-checked, every `band_mark` row dropped; (d) the factors; (e) `results/rd04_descriptive.csv`. **The lead's row
   recording this step's first run, whatever its outcome, begins its third cell with `` `RD-04 read: step 2` ``**
   (9.3).
3. **(c)** (`scripts/rd04_replay.py --part scorecard`, purpose `registered_design`, the pinning row, P-14 and P-16; its
   three refusals of 5 item 6 first):
   (a) the factors recomputed from step 2's file and checked; (b) `k1` on P-14 then P-16, both arms, the recorder on,
   its start rows against U1's again; (c) each new cell, P-14 then P-16, in the order `yr_act`, `yr_sc`, `tr_act`,
   `tr_sc`, each checked under 8.3 before anything of it is read; (d) the gates in the same order; (e) the mechanics,
   then the reading; (f) `results/rd04_replay.csv` and `results/rd04_replay_gate.csv`.
4. **The readings beside** (`scripts/rd04_replay.py --part beside`, the same purpose and row; its refusals first; the
   cells' trades rebuilt as step 3 built them and their hashes checked equal to step 3's manifest): `k1`'s fourteen
   responses against Q-44's per-start file first, refusing; then the ladder and the placement on every new cell in step
   3's order; then the Focused Trader models on the `yr_act` and `tr_act` cells of each design; then
   `results/rd04_replay_beside.csv`.

**On any failure, nothing more of the failed step's own run is computed, written or printed**: that step's run stops
at the failed check, and its log and the check's own lines are all it leaves. A failure in step 1 or 3 stops (c); a
failure in step 2 stops (a2) and (c); a failure in step 4 stops the beside readings, and steps 2 and 3's files stand.

- **weight: heavy.** Four rescaled walks over the window (built again in step 4, its trades held to step 3's hashes),
  ten replays on two arms over every start, eight gates of 500 paths, seventy-two replays beside; (a2)'s one pass over
  the bars. Measured on synthetic bars and campaigns of the window's length (seed 20262312) before step 2 and before
  step 3 (E-117's form), and stated in the lead's row with its memory; two workers at most. **No measurement, smoke or
  timing run reads a real bar** (5 item 6, M3).
- **A restart or a rerun (E-053).** Each step allows one clean run; a restart, a rerun after a fix, or the failure
  protocol's replication is a further read: `repeat='E-NNN'` for (a2) and `--repeat E-NNN` for (c), a row naming this
  file. Only the first complete run of each step is read.

### 13.3 Waits, all before step 1 unless stated

- the pinning row, naming P-14 and P-16 (it admits (c)'s `registered_design` reads);
- **Q-121b on master: met** at 4b72ef2 (E-166), the interface of 3.2;
- **Q-121's file on master** (`results/q121_vol_descriptive_a1.csv`) from its own clean run, with its row (before step
  2). Its run is queued at 4b72ef2 (E-166). The wait is met only when the file exists **and** the
  `extended/vol_descriptive.py` (a2) imports hashes to that file at its manifest's `git_commit` (3.2, m3);
- **the leak-clause test** (`tests/test_rd04_leak_clause.py`, T-15) on master (before the pin);
- every shared identity of 8.1 held at a commit whose covers are unchanged at the run's commit (the build edits no
  shared covered file, 4.6);
- **Q-44's per-start file on master** (`results/user_beside_starts.csv`), for step 4's reference checks (before step 4);
- the adapters built with T-1 to T-14 (T-0 and T-15 already built), and the red team's read of the build;
- step 1's `rd04_identity` held (before step 3); step 2 recorded (before step 3).

## 14. Open before the pin

**The lead's:**

1. **The gatekeeper's read of this text** (the red team's re-read done, Q-123r2); and **T-0** (`tests/test_rd04_draft.py`) and
   **T-15** (`tests/test_rd04_leak_clause.py`), both built with this text, which must pass on the text pinned.
2. **Q-121's names and Q-121b's interface: closed, met at 4b72ef2 (E-166).** This text writes the real names (the
   file `results/q121_vol_descriptive_a1.csv`, the sections, `trail20_range_pts`, `walked`, `value_quantiles`,
   `COLUMNS`, `kind_problems`, `walk_problems`) and the merged interface (3.2: the keyword on five functions, the
   module's four constants). T-0 holds them mechanically. If either changes on master before the pin, T-0 fails and
   this text is re-drafted; nothing here is read as covering another interface.
3. **The pinning row names P-14 and P-16**, so it can serve as (c)'s `registered_design` declaration (5 item 6); or the
   lead names another row here before the pin.
4. **The leak clause as the lead's program rule** (9.3): the pinning row adopts items 1 to 3, binding every later
   declaration and every row that fixes a parameter, from step 2's first run; the step-2 row carries the token; the
   line in the family template (9.3 item 4) is the lead's, with Q-122's template work (E-157 (b)).
5. **The pin-time facts the pinning row states** (m7): whether Q-121's file had been made by the pin, and whether anyone
   had opened it; the reference years classed as the lead's choice (section 7); the seed block named by reference only
   (section 11).
6. **(a0)'s home, settled.** E-157 (a1) listed the gate files' `period` and `drift` rows under Q-121; E-158 corrected
   it (their rows span the judged block, so they are read under this reading), as Q-121's and Q-123's briefs say. Nothing
   open; recorded for the red team.

**The operator's:** none before the run. After it: nothing to choose -- (c) is a description. Pre-2020 bars stay the
operator's purchase decision (E-008), not proposed here.

## 15. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*

---

## Appendix C -- the drafter's choices, each with its reason

Every choice made where the note, the brief, the red team's note or the rules left the text open. Rows 4, 6, 8, 9,
11, 13 and 21 are the second text's revisions of the first's; rows 25 to 34 are the second text's own; rows 26, 29, 30
and 33 are corrected by the third, and rows 35 to 39 are the third's own.

| # | choice | where | reason |
|---|---|---|---|
| 1 | (c)'s judged reads under `registered_design` by the pinning row, not on the `Judged-block reads:` line | 5 item 6 | the brief and E-157; the reader admits `registered_design` only under a decision row naming the designs, never under a declaration's file, whatever its line says (`extended/reader.py:36-41`, `_registered`) |
| 2 | a once rule for (c) enforced by its own script | 5 item 6; T-12 | the reader never limits `registered_design` to one run; a declared reading is read once (E-053) |
| 3 | the map rounds half to even, about the session's first open | 4.1 | the note's map made exact; half to even is numpy's default and non-decreasing, so bar order is kept; exact at k = 1 |
| 4 | L_ref and L_y as Q-121's inverted-CDF medians of `trail20_range_pts` over the walked sessions with a finite value, by the trading day's year; a blank trailing value unscaled | 4.2 | the note's definitions, made exact in Q-121's terms (M4): one population and one statistic two builders cannot read differently, fixed before Q-121's values existed |
| 5 | the trailing factor uses the actual bars' trailing range, a session without one unscaled | 4.2 | causal, and independent of the map; scaling by a factor computed on rescaled bars would feed the map into itself |
| 6 | the arms' shift, e and bound frozen at `k1`'s; the cell's own bound printed beside, unused; the cell's own e used only to centre its zero-edge twin | 4.4 | the edge assumption held fixed so only the amplitude moves; a twin is zero-edge only about its own trades' e (M2) |
| 7 | the 2 x 2 grid of factor and cost reading, every cell run | 6.2 | the brief names both factors and both cost readings; a full grid lets each be read alone (6.3) |
| 8 | `sc` scales the tick costs only (entry, stop or breakeven, flatten); the round-turn fee and the account fees are never scaled | 4.3 | the fee is dollars per contract, the contract's, held fixed like the subscriptions; the engine re-prices `fee_micro_eq` at size (D-324), so a scaled fee would be undone (M1); pitfall 1's object is the tick grid |
| 9 | the ten Focused Trader models on the four actual-cost cells (`yr_act`, `tr_act`), the gap named on the four `sc` cells | 6.4; 9.1 item 6 | E-007 (e) asks for them beside every user reading; they bind on payout and purchase patterns, which compression changes, and `tr_act` is the only causal variant (m4); the `sc` cells differ from their `act` cells only in the tick costs, which 6.3's cost comparison reads on the scorecard; 40 more heavy replays for them is a cost the lead may still choose to pay |
| 10 | the ladder and the placement on every new cell | 6.4 | E-007 (e); cheap beside the walks |
| 11 | (a2) imports Q-121's module through an optional reader authorisation, its early rows its identity | 3.2; 8.2 | one code path for (a1) and (a2); Q-121's refusal kept when the keyword is absent; the identity is free and comes before the judged read (M4) |
| 12 | (c)'s factors computed from (a2)'s file, so (a2) runs first | 13.2 | one source for L_y; (a2)'s identity then covers (c)'s inputs |
| 13 | L_ref read from Q-121's file and also recomputed from (a2)'s rows, both required equal; L_y for 2020 to 2023 also held to Q-121's `range` rows | 4.2; 8.3 | the brief: L_ref from Q-121's file, named by path; the `range` row is the same statistic on the same population, a free cross-check (M4) |
| 14 | the frozen marks' and rungs' would-fail counts printed beside | 4.4; 8.4 | the note's pitfall 4 says the unresolved shares are reported; the counts say how far the frozen admission is from what the rescaled walk would admit, without acting on it |
| 15 | the consistency cap's and the stand-aside's binding by year named as not read | 8.4 | no record this reading's path carries holds them (the gate files carry pooled columns only); a counters channel would edit a shared covered file (RD-03's A-1 (d) is on an unmerged branch) |
| 16 | a second reference (the choice block's median) dropped | 7 | the note's "possibly"; doubles the heavy cells for an unasked variant |
| 17 | the leak clause extended from (a2) to (a0) and (c) | 9.3 | all three describe the judged block; a question may cite them, a value may not |
| 18 | the uncertainty method RD-02's 9.2 unchanged, with this reading's own honesty seed | 9.2 | the program's corrected method (E-058 (5)), built and tested; a new seed so no seed changes meaning |
| 19 | (a0) recorded in the result's manifest, not the read ledger | 5 item 6 | the reader ledgers bar, walk and engine reads only; the gate files are vendored results |
| 20 | no shared covered file edited; new modules only | 4.6; 12.1 | keeps every shared identity's token valid (E-104, E-117), unlike RD-03's build (E-156) |
| 21 | Q-121's real names written (file, sections, columns, functions), as merged at a83db31 | 3.2; 4.2; 13.1 | Q-121 is built and merged; the first text named them by role (M4) |
| 22 | Q-44's per-start file a wait before step 4, `k1`'s fourteen responses checked against it | 8.1; 13.3 | RD-03's form (its 9.1 item 6): the beside readings' reference is the program's own, not recomputed unchecked |
| 23 | `k1` replayed inside step 3 and held to U1's rows, the pairs read against that replay | 8.1; 9.1 | the paired readings need U1's records in this repository's form; the comparison keeps them U1's |
| 24 | step 4 rebuilds the cells' trades and holds them to step 3's hashes, writing no intermediate file | 13.2 | a result is written only through `write_result` from a clean run; an untracked cache of rescaled trades would be neither |
| 25 | a piece of a beside cell that cannot be built stops that cell alone; a piece of `k1` or `yr_act` stops (c) | 4.6; 10 | M1's remedy 3: a declared failure scope, so a beside arm's plumbing never halts the headline, and nothing replaces what is not built |
| 26 | (a2) runs `output_problems` on `summarise`'s frame, compares its `band_mark` rows in memory, then drops every `band_mark` row before anything is printed or written | 3.2; 8.2 | a second lock (the re-read's m1): the merged module already writes no `band_mark` row from 2024-01-02; the drop keeps Q-121's choice-block rows in Q-121's file alone, and the in-memory comparison keeps 8.2's identity whole |
| 27 | Q-121's days and walk identities re-run over the whole window, imported from Q-121's script by its path, `main` never called; A1's `days` read under `volatility_descriptive` in the same run | 3.2; 5 item 6 | M4's remedy 8, the red team's recommendation: the day kinds feed the walked set and so the factors |
| 28 | the leak-clause test: the token `` `RD-04 read: step 2` `` in the lead's step-2 row; in scope every `prereg/F-`, `prereg/RD-` or `docs/calibration/` file first pinned in a later row; the header the text before the first `## ` line, whitespace collapsed | 9.3; T-15 | M5's remedy 3 made mechanical: a token the lead writes is unambiguous where a date is not (several rows share a date); a file's first pin decides, so a re-cited old pin is never caught; a calibration plan is a declaration too |
| 29 | this reading's files carry the prefix `rd04_` (`extended/rd04_*.py`, `scripts/rd04_*.py`, `identity/rd04_identity.py`, `results/rd04_*.csv`) | 12.1; 13.1 | n6: RD-04's names were unbuilt, so they were the ones to change (Q-121b has since renamed Q-121's helper `tests/q121_synthetic.py`, E-166); `rd04_` matches T-0's and T-15's files |
| 30 | the gate's pairing made a fact by the vendored `SharedDayTable` (a path's day indices a function of its seed and the number of day blocks alone) and an oracle holding each cell's block dates and order to `k1`'s | 5 item 4; 8.3 | the re-read's m2: the second text's `counters` route does not exist (that channel records RD-02's account counters and refuses the registered accounts); the code settles n3 |
| 31 | the step-shape label on every paired row whose share of starts differing is below one | 9.1 item 5 | n4 asks for a label "where `share_differing` is low"; any identical start makes the series step-shaped, and a threshold would be a choice with no basis |
| 32 | T-0's hash pin-readiness through the reader's declaration check (`_family`) on a temporary tree, not the whole `authorise` | 12.2 | `authorise` also needs a clean run's checkout and a ledger, which a fast test cannot be; `_family` is the part that reads the pin, the hash and the purpose line |
| 33 | (a2) refuses unless its imported module hashes to the one at the commit in Q-121's manifest | 3.2; 13.3 | M4's remedy 3 made exact (the re-read's m3): "carries the keyword" was met by any later commit; the sha equality ties both modes to the bytes that made Q-121's file |
| 34 | the reference years classed as the lead's choice, the operator's description of the early years as calm its reason | 7 | m7: E-155 names no years; the lead names 2020-2021 inside the choice block |
| 35 | T-15's scope: first pins in or after the step-2 row, and in rows absent from `DECISIONS.md` at the read's commit; a ledger read without a step-2 row fails | 9.3; T-15 | the re-read's M1, remedies 1 to 3, all adopted as the lead ruled; the optional third closes the run-to-row window entirely, and failing on a missing row closes the silent-off route |
| 36 | the pre-read form carried by the pinning row, as a literal token naming the commit and the path, not by the file's header | 9.3 item 1; T-15 | the lead's ruling on m5 made checkable: a file cannot name a commit at which it was already byte-identical to itself with that name inside it; the draft name is accepted because a pin renames the file and changes nothing else |
| 37 | the pre-read commit must be older than both the read's commit and the step-2 row's commit (with neither committed, in HEAD's history) | 9.3 item 1; T-15 | the lead's "older than the step-2 row's commit", plus the read's commit when the ledger holds it: older than the read is what "written before RD-04 was read" means, and it implies the lead's condition |
| 38 | the twin oracle over the trades with a finite `r_R`, on the blocks | 8.3 | the re-read's n7: that is `edge_stats`' population for e, so the tolerance is achievable; the engine's realised R carries the fee re-pricing |
| 39 | 8.2 compares every `band_mark` row, its `block` row included | 8.2 | the re-read's n10: under the authorisation `band_mark` spans the choice block only, so its block row is comparable at no cost |
