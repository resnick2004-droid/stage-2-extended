# H4: the re-baseline -- the four baselines on the journey scorecard, search years only (a draft)

**Status: a draft, second text (corrective cycle 1), for the red team's re-read.** The first text (wt/wt-h4 f897cd7)
was read in `docs/reviews/H4_DECL_2026-11-20.md` (blocked: B-1 to B-7, seven minors, six notes); the lead's rulings on
it are carried here, and Appendix D maps every finding to its answer. Copied from `prereg/TEMPLATE_family.md`'s form
(sections 0 to 19) and adapted as H3's draft was (`prereg/DRAFT_H3_three_way.md` on wt/wt-three): H4 is a **described
reading** of the baselines, not a family of trades and not a search, so it takes **no k** (CHARTER 3.7: one k per
held-out test; H4 reads no held-out session and judges no design), names no cell that reaches a judgement, and reads
the **search years only**. The design-search template (`prereg/TEMPLATE_design_search.md`, sections 2 and 7) fixes
what H4 is for: its search-year results are the inputs from which the lead sets CHARTER 3.9's limits, bankroll
budgets, weights and the size that matters, by the rule declared before H4 is read (W42-R1). It is pinned by the
sha256 of its LF text in the lead's row only after the red team's read **and after W42-R1's pin**; nothing declared is
edited after that -- a change is a new declaration.

**Which form, and why** (the lead's ruling on the template's scope). The design-search template's second text
(`prereg/TEMPLATE_design_search.md` v2, wt/wt-lit 68436c9, E-247) is the form for a *search*: a declaration with an
F-number, a k at its held-out row, a survey, a pass line. H4 has none of these, so its sections follow
`prereg/TEMPLATE_family.md`'s form, as H3's do. **Where v2 governs what H4 runs, v2 is followed and cited:** its
section 5 (the race, L_fill, R-10's stopped walk and its exit map, m-2 and m-3) for the deciding reading, and its
section 14's held-out line (a declaration that does not spend the market's held-out years carries no judged-block
reads line). Checked against v2 at 68436c9 in this text.

| field | value |
|---|---|
| declaration | H4 (the heavy queue's H4, the restart plan's Wave 4); no family number, **no k** |
| what it reads | the four baselines -- the naive coin, P-14, P-15, P-16 -- on Topstep's $50K, under the zero-edge convention, over J coin seeds, on NQ's search years (2020-01-02 to 2023-12-29) only |
| what it feeds | W42-R1 (`docs/plans/WAVE42_SETTING_RULE.md`, **as pinned**: `<W42-R1's pinning row and its rule text's LF sha256, filled at W42-R1's pin>`), through one collection result; Wave 4.1's measure-structure analysis; H3-D's power gate (the three-way note's 4.3) |
| never read | the held-out years (2024-01-02 to 2026-07-16); the confirmation window (NQ from 2026-07-17) |
| parts | H4-0 (the probe), H4-S (the schedules, gates and identities), H4-A (the as-traded replays), H4-B (the seed-paired readings, one part a baseline), H4-C (the collection); Appendix A |
| seeds | section 15: a block of its own, by role |
| dependencies | Appendix C |

No result number is typed here. Every figure of the run plan and of J is printed by `docs/plans/scripts/h4/h4_plan.py`
from declared constants and the calendar (Appendix A), and `tests/test_h4_draft.py` holds the appendix to the script
line for line and recomputes its figures.

---

## 0. In plain words (for the operator)

Before any new design can be compared with what a user can already run, the four plans already on offer -- a coin
flipped at fixed clock times ("naive coin harvesting") and Stage 2's three registered designs P-14, P-15 and P-16 --
are run through the new journey scorecard: how much bankroll a user needs, how fast and how cheaply they pass and get
paid, how steady the income is, and how often they run out first. Every trade's direction is taken away (each outcome
redrawn by a fair coin at the odds its stop and target give), so what is left is what the firm's rules and the plan's
timing and sizing do to a user, not any market edge. Each plan is run many times with different coins (J coin seeds),
on every start day of 2020 to 2023 only; the years 2024 to mid-2026 stay unread for the final test. Nothing passes or
fails here: H4 **describes**. Its numbers are then fed, by a rule already written down before H4 is read, into the
limits, budgets and weights that every later design must meet. A failure here means a check failed (an identity, the
zero-edge check): the run stops and is diagnosed, never re-run until it passes.

## 1. Hypothesis: what H4 reads, its sources, and the sign stated in advance

- **No hypothesis is tested.** H4 is a described reading; no statistic of it decides a design, and no level is spent.
- **What is fixed in advance (a check, not a hypothesis): the zero-edge oracle.** On the deciding reading every taken
  trade's gross expectation is exactly zero and its net expectation exactly minus its costs (CHARTER 3.2; the race
  with its exit cost, L = min(l, c - x_stop), p = L / (L + g); R-10's stopped walk for a time-limited exit). It is
  checked per trade, exactly, on the trade log (section 9).
- **No sign is predicted for any journey measure.** Under zero edge a baseline's mean net per trade is minus its
  costs, but the contract is convex (payouts, resets, the floor), so a journey measure can sit on either side of zero;
  that is the asymmetry the program studies, and H4 reads it without a prior sign.
- **Sources.** The convention is CHARTER 3.2 and the design-search template's section 5; the race is the driftless
  first exit (gambler's ruin), as Stage 2's `adapter.BinaryDraw` races it (Stage 2 D-150, D-156); the measures are
  `docs/MEASURES.md`'s; the baselines are CHARTER 2's (MEASURES (35), (36)).

## 2. Prior exposure: what has already read these bars, these baselines and this population

- **Stage 2 chose P-14, P-15 and P-16 on the whole development window** (2020 to 2026), so for them "held out" means
  unread *by this program's search* only (E-208); it is said beside every reading of them (MEASURES (36)). They are
  run **as registered**: **whole-window-derived registered comparators**, so labelled beside every reading.
- **Their registered rows** (U1's `results/user_journey.csv` and Q-17's [B] and [BS], MEASURES 1.5) are whole-window
  readings. H4 does not read them: its as-traded reading (H4-A) is made afresh on the search years, block-bounded, on
  the point arm (`user_beside.run_starts(design, "point", ..., journey=True, journey_block="search")`), so no
  registered row's held-out start is opened.
- **Inherited registered constants** (the lead's ruling on B-2, the O-7 precedent under E-247): every whole-window
  statistic a registered builder computes is passed in **as registered**, never re-resolved on the search years --
  P-15's and P-16's offered marks (their cutoffs resolved by Stage 2 on the whole window, D-525 (4)), each registered
  design's busiest-day capacity, and P-14's rung map (a pinned Stage 2 results file). They are read from **the
  registered-constants file** (Appendix C), by its sha256 cited under a decision row; a search-year P-15 or P-16 would
  not be the registered design.
- **This program's reads of the search years:** RD-04's and Q-121's volatility readings, S1's range (E-240), Q-152 and
  Q-169's trigger library, H2's overnight check (E-231). None read a baseline's journey under the convention; H4 is
  the first.
- **The held-out read ledger** (CHARTER 3.6 (b), in RD-04's leak-clause form): every past read of the held-out years
  behind a choice H4 inherits, for the four baselines and the coin's inherited levers. Each entry is "written after
  this reading; no figure cited".

  | read | what it read of 2024-2026 | for which baseline or inherited lever | row |
  |---|---|---|---|
  | Stage 2's choice of P-14, P-15 and P-16 | their whole-window development tests and verdicts | P-14, P-15, P-16 as comparators | Stage 2's registrations; E-208 |
  | P-16's stop, chosen on each block | the stop screens' whole-window rows | P-16; **the coin's stop** (inherited) | Stage 2 D-554 |
  | P-15's and P-16's resolved marks | the cutoff's unresolved shares over the whole window | P-15, P-16 (passed through as registered); the identity I-5's marks | Stage 2 D-525 (4); E-203 S-2 |
  | the no-closure table and the purchase budget | the compliance study's whole-window readings | P-14, P-15, P-16; **the coin's account policy and budget** (inherited) | Stage 2 D-502, D-509 |
  | the busiest-day capacity | each registered cell's whole-window busiest day | P-14, P-15, P-16 (passed through); the coin (inherited through P-16's job) | the registered builders; B-2 |
  | P-14's rung map | the atlas's whole-window rung choice | P-14 | Stage 2's pinned rung file |
  | Q-132's rows | every `judged` and `all` row, the gate, the trades, the verdict bound | P-14, P-15, P-16 | E-211 |
  | Q-16's paired nulls | the paired nulls computed on the held-out years | P-14, P-15, P-16 | E-211 |
  | Q-17's [B] and [BS], and E-201's readings | the firm-response replays over the whole window | P-14, P-15, P-16 | E-201; Q-17 |
  | RD-02, RD-03, RD-04's part (c), RD-05 | their whole-window readings of the registered designs | P-14, P-15, P-16; the coin's levers through P-16's job | their pinning rows |
  | Stage 2's program U | the user milestones and the rows to beat | P-14, P-15, P-16; the coin's shape (below) | Stage 2's program U |
  | **the choice of P-16's shape for the coin** | made by the lead, who has read those designs' whole-window journeys | the coin | the lead's fixed choice (section 7) |

  While this ledger is not empty **the level is nominal** (CHARTER 3.6 (b)): H4 spends none, and the held-out test's
  level is printed nominal beside its verdict.

## 3. Contract fit and conduct (CHARTER section 4, item by item)

| item | H4's answer |
|---|---|
| stops in the stop band, above the cost floor | as registered for P-14, P-15, P-16; the naive coin takes P-16's registered bracket (section 7), inside the band; H4-S checks every baseline's trades against `vendor/stage2/results/stop_band.csv` and reports any outside, counted, beside |
| at least five minutes from alert to order, by hand | P-14 and the naive coin at L = 5 (P-14's registered latency; the lever table's T4 reference); P-15 and P-16 scheduled at their registered marks, latency-free (the template's section 1) |
| one position at a time per firm, five minutes flat between trades | **Stage 2's strict rule for every baseline** (D-409, D-429): one open position across all accounts, five minutes flat, each trade to one account (P-14 built with `one_at_a_time=B.STRICT_GAP`, `customer_journey.py`; P-15 and P-16 through `rc_dev_test.rc_campaign`'s strict gap; the engine's rotation in `propedge/campaign/shared_days.py`); the naive coin through the same registered account policy and the mix router (Q-169); H4-S's overlap count must be 0 |
| at most 5 % of trades reaching the 15:10 CT flatten, overall and in every year | read by H4-S's resolution gate (D-212 as D-308 raised it) on every baseline's schedule before any outcome; a baseline over it is reported, counted, never dropped (it is a comparator); the coin's reading printed beside each limit it sets (n-3) |
| realised risk within 10 % on at least 90 % of trades | H4-S's realised-risk gate (D-212; E-022 (1), E-032's allowance-capped form), reported the same way |
| no entry before 07:35:00 CT on a BLS 08:30 day; FOMC days out | as registered; the naive coin through the void calendar (`extended/day_calendar.py`, Q-166) |
| no entry or fill inside a verified news window; the news-flatten convention | as registered for P-14, P-15, P-16 (P-16's `_nr` cell's news rule); the naive coin under E-223's one convention through the trigger library |
| **conduct tier 1** (no hedging across accounts or firms, no simulator-fill exploitation, no maximum size into major news, no trade copied across accounts, nothing that conceals a pattern) | **held by every baseline**: one open position across all accounts, each trade on one account, so **no trade is copied across accounts** and no two positions are open at once (the strict rule above); no hedging, no opposite positions (the router refuses them), one firm |
| conduct tier 2 modelled and off in the base case; tier 3 priced, 0 % denial in the verdict | the response `off` only (`user_beside.BY_NAME["off"]`): 0 % payout denial, the placement off, the Focused Trader Program off -- the verdict's settings (CHARTER 2) |
| firm rules only from Stage 2's verified ledger or a row verifying them | Topstep's $50K from `vendor/stage2/config/rules.yaml` through the vendored loader, as the registered jobs load it; no other firm |
| no automated or API order entry | H4 is a reading of history; it places no order |

## 4. Data, blocks, the seal and the confirmation window (dates, fixed now)

- **The search years only:** NQ 1-minute bars 2020-01-02 to 2023-12-29, read through `extended/reader.py` (the one
  door) under the purpose `h4_search_years`, a choice-block purpose (no tag is needed there; it names the reading in
  the ledger). Any read whose span reaches 2024-01-02 is refused by the reader before it opens a file.
- **The starts:** every session of the search years is a start, the same set for every baseline, arm and seed (the
  units are paired, MEASURES 1.1). Each start's journey stays inside its block: `user_beside.run_starts(journey=True,
  journey_block="search")` (Wave 3.1, M-3) refuses a start of another block before the pool is reached, and the
  runner's `Plan` refuses any unit whose window holds a session from 2024-01-02 (`HeldOutRefused`; CHARTER 3.6 (e)).
- **Sessions left, uncapped** (the lead's ruling on B-4): each start's sessions left in its block are counted on the
  search-year session list of `extended/day_calendar.py` at ebd5a05 (`load_sources().days`: the bar store manifest's
  day list, search years only, its file's sha256 recorded), **the start session counted** (as
  `user_beside.journey_length` counts before its cap), never capped. `obs` (the run's length) is that count capped at
  252; `E_h` is the starts with at least h sessions left.
- **The windows W = 126 and 252** (the brief): the W-window measures of MEASURES (measures (1) to (3), (5) to (7), (9)
  and (24)) are read at W = 126, W42-R1's window, and at W = 252 beside; the horizon measures at their own horizons
  (Appendix B).
- **The long windows' caveat (the nested cuts).**
  - E_252 holds only starts with 252 sessions left before 2023-12-29, so **no start day of 2023 is read at a
    twelve-month horizon** (MEASURES 1.1's consequence); 2023's sessions enter those readings only as later sessions of
    earlier starts. At W = 126, 2023's starts enter only while 126 sessions remain.
  - H4 reads through the cut (`extended/search_cut.py`, Appendix C), and its causality is checked by **the nested
    cuts** (the O-7 review's remedy 2, widened by the red team's m-4): the day blocks built on the cuts ending
    2022-12-30, 2023-06-30 and 2023-09-29 must each equal those built on the cut ending 2023-12-29, block for block, up
    to their own last day.
  - The checks cover **schedules up to 2023-09-29**. The sessions of a window after the last nested cut rest on the
    longest cut alone; **the share of window sessions after 2023-09-29** is printed beside every reading at W = 252
    and at the twelve-month horizon; no reading is re-weighted or trimmed for it.
- **The seal (CHARTER 3.6 (e)):** H4 computes no held-out output. Were any computed by a defect, it is written sealed
  (its hash recorded, the file unopened) until the held-out test, and the defect is diagnosed.
- **The confirmation window:** NQ from 2026-07-17, never read.
- **Disclosed pre-reads:** section 2.

## 5. Supply: the population, the schedule and the walk (counted before any outcome)

- **The schedules** (H4-S): each baseline's trigger-level trades on the search years -- each trade's session, alert,
  decision, entry and exit times, its bracket in ticks (stop l, target g), its exit reason as run, its account and its
  costs -- built once, before any outcome is read:
  - P-14, P-15 and P-16 from their registered builders through the cut in its pass-through mode (Appendix C: the
    registered constants in, never re-resolved), each **equal to its registered trigger-level trades on the search
    years, path for path** (I-1, section 16), never trades pruned by a real run's account state;
  - the naive coin from the trigger library (`triggers.CoinMarks`, `components.coin_component`,
    `components.schedule_day`, the mix router), its levers fixed in section 7, held by I-5.
- **Counted from the schedules alone, before any outcome**, per baseline and per search year: trades a session (the
  supply), the share of trades reaching a time limit (the 15:10 flatten, a news window, a max hold) and their mean
  R-10 steps, the trades outside the stop band, the realised-risk share, and **the positions open at once** (on the
  run's entry and exit times, the three-way note's N-4 definition), which must be 0. These are H4-S's gates (section
  11) and the cost model's inputs (Appendix A's cut rule).
- **The walk** is the run's own walk on the real bars (the walker, `extended/walker.py`, its identity E-011, and the
  vendored builders for the registered designs); exits, times and costs stay as run (CHARTER 3.2).

## 6. The side, its persistence and the fill intensity

- **No trade-lift line is read** (E-208 retired it); E-035 (6)'s persistence and E-187's band do not apply.
- **The side is the coin's** under the three-way note's keying, choice 3 (its 1.5): one uniform per user and moment, the
  start in every key, no account and no firm index. On the deciding reading the side moves no outcome (the redraw races
  the barriers with direction removed); it is drawn for the as-walked reading beside. For a market entry it is the
  coin choosing the side; every baseline enters at market or at a registered mark, so no resting entry and **no pair
  rule** arises (the template's section 5); were one found in a schedule, H4-S refuses it.
- **The fill intensity:** the schedules' supply as counted (section 5); a missed signal (measure (28)) is the arm
  `missed_0.1`'s draw, keyed apart.

## 7. Parameters: fixed / searched / dropped (every one, with its value)

Nothing is searched: H4 reads four fixed comparators. Every value is a rule cited by its key, a registered value, or a
declared constant with its reason.

| parameter | what it is, in a phrase | class | value or source |
|---|---|---|---|
| the firm and plan | whose rules the journeys run under | fixed | Topstep's $50K, `vendor/stage2/config/rules.yaml`, as the registered jobs load it |
| P-14, P-15, P-16 | the registered designs | fixed, as registered | their registered jobs (`vendor/stage2/scripts/user_journey.py`'s configurations `p14`, `p15`, `p16`), their trades, brackets, sizing, account policy (the strict rule), purchase budget and protocol unchanged; their whole-window statistics passed through from the registered-constants file (section 2) |
| the arm | which of U1's arms carries the journey | fixed | **`arm="point"`** for H4-A and for I-4's reference (E-248; CHARTER 3.10 retires the verdict arm): **the verdict arm is never run** |
| the naive coin's signal | when it trades | fixed | the lever table's T1 `coin`: a moment every `triggers.MARK_STEP` minutes on the clock alone (no bar read to choose one), market entry (T5 `market`), L = 5 (T4's reference), admission T7 `off`, side T8 the coin |
| the naive coin's sessions | where its moments lie | fixed | P-16's registered window `all` (`resolved_coin.WINDOWS`, 17:00 CT to the cutoff): every session the firm allows, each through `components.coin_component`'s rule (from the session's start to the last moment whose order goes live before its end and the firm's last new entry); overnight admitted on the search years (E-231) |
| the naive coin's trade shape and account policy | stop, target, size, accounts, budget | fixed, **the lead's fixed choice** | **P-16's registered job's**: its stop (`rc150_dev_test.STOP`), its target and sizing rule, its account policy (the strict rule), its purchase budget (`a3_brk30_cb20.BUDGET`) and its protocol. The reason: P-16 is a coin design already (Stage 2's family RC), so the comparison isolates timing. The alternatives were P-14's shape (the rung map and its table) or P-15's; the choice was made by a reader of those designs' whole-window journeys, so it is in the held-out read ledger (section 2). The coin differs from P-16 in its schedule (every clock moment against P-16's resolved marks), its latency (L = 5 against P-16's scheduled marks), its news convention (E-223's through the trigger library, against P-16's `_nr` cell) and its void calendar (Q-166); I-5 holds everything else. CHARTER 2 fixes the coin's levers "in the declaration": **this is that declaration**; MEASURES (35) says so, and Wave 5's search declaration restates them by citing this file's pinned sha256 |
| the reading that decides | what W42-R1 reads | fixed | the martingale-outcome reading, as the design-search template v2's section 5 declares it: each trade's outcome redrawn at its bracket's driftless first-exit odds by the race, L = min(l, c - x_stop) **fractional, never rounded** (E-237), p = L / (L + g), g the target as placed (a rule's profit level converted to net ticks after the target-side cost), a win +g less x_target, a loss -L less x_stop, a cushion-bound loss ending exactly on the floor and breaching it; **what happens at the fill decided at the fill** by L_fill = min(l, c - max(x_stop, x_flat)), fractional, against the runner's tolerance `EPS`: L_fill above it, the trade is raced or walked; at or below it where the floor's room binds, **the account is failed at the fill** (taken to the floor, replaced at the close as the engine does); where the daily loss limit's room binds, **the day stops** -- there is no "not taken" state; R-10's stopped walk for a trade ending at a time limit (its last sub-step a driftless two-point race to the fractional barrier; the exit map `three_way_redraw.EXIT_LAW`, any other state refused) |
| the readings beside | never deciding | fixed | the **as-walked** reading (the real path reflected about the fill by the side coin, walked to its exits as run; the path-structure edge is its gap from the deciding reading) and the **as-traded** reading of P-14, P-15, P-16 (their registered sides, unreflected, H4-A, point arm); the naive coin has no as-traded reading (it has no real side) |
| the responses | the firm's responses switched on | fixed | `off` only (0 % denial, the placement off, the Focused Trader Program off) |
| the stress arms | CHARTER 3.8 (c)'s fill and supply stress | fixed | `worse_1` (measure (29)'s +1 tick on every fill: the entry and each exit) and `missed_0.1` (measure (28)'s 10 % of signals missed), each on every baseline alike, on the deciding reading, on the same keys as `off` (`three_way_runner.stress_arms`, selected by name) |
| the +2 tick and 20 % missed arms | measures (28) and (29)'s other levels | **dropped** | the template's pass line reads +1 tick and 10 % only (its section 10 (c)); the runner's `worse_2` arm is not run by H4 (cost); measures (28) and (29) are read at the levels run |
| the denial ladder | measure (33)'s responses | **dropped** | H4's responses are `off` only (the brief); measure (33) is not read (Appendix B) |
| W | the first-payout window | fixed | 126 (W42-R1's `W`; U1's and Q-44's ledger constant) and 252 beside |
| the horizons | where each measure is read | fixed | each measure's own (MEASURES section 4); a month is 21 sessions (CHARTER 2) |
| the exact-length runs | U1's identity on the cut runs (MEASURES 1.1, m-8) | fixed | U1's `EXACT` horizons (the vendored `user_journey.EXACT`, D-620 (3)(f)) on every start of the `off` arm-runs (W3.1's M-2) and on every `user_beside.EXACT_EVERY`-th start of the stress arms; the record each reading read and its differing count in its manifest |
| J | H4's coin seeds | fixed | **`J_H4` of Appendix A**: the smallest power of two at or above the J at which a true gap of W42-R1's `DELTA_MIN` between two baselines clears W42-R1's `RESOLVE_Z` coin standard errors with probability `family_stats.MDL_POWER`, at W42-R1 5.3's worst-case variance (Q = 1 / (J n) at the twelve-month horizon's complete starts, every per-unit difference in [-1, 1]), n from a lower bound of the sessions (the three-way note's 2.5 form with W42-R1's resolution line). **Read at the pinned W42-R1's constants only**: until W42-R1 is pinned the script's `j_h4` refuses and Appendix A prints a provisional reading at 2bde318's constants, for sizing only |
| the seed indices | the coin seeds' indices | fixed | 0 to J - 1 (`three_way_runner.Plan`'s `seed_indices`), the same for every baseline and arm |
| the holiday allowance | the sessions' lower bound for J | fixed | `HOLIDAYS_A_YEAR` of the script: at most that many weekdays a year are not sessions (exchange holidays fall below it), so J is not short |
| the batch | starts run at once in lockstep | fixed | a batch of 21 starts (a month of starts; the script's `BATCH_STARTS`), its lanes against the memory cap in Appendix A |
| the part cap | the cut rule | fixed | 8 hours a part at H4-0's measured cost (`three_way_arith.PART_CAP_H`); at most 2 workers, one BLAS thread |
| positions open at once | overlap | fixed, **none** | every baseline holds one open position across all accounts, each trade on one account (D-409, D-429): no copying, no overlap; H4-S's overlap count must be 0 (refusing), and the firm path refuses any overlap. No joint law is declared here; if Wave 5's designs need one, it is the sequential driftless race on one path (the strong Markov property: exact joint outcomes for any set of intervals containing the fill), never the one-uniform form, which is exact only for nested losses with a common target (the red team's n-2) |
| a t-test | any t as a decision | **dropped** | H4 decides nothing; no t is computed as a line |

- **Fitted values:** none. Nothing is fitted, chosen or tuned on any years; the inherited constants of section 2 are
  Stage 2's, as registered.

## 8. The cells and the count

- **H4 takes no k** and judges no design: no cell reaches a judgement, nothing enters `results/variants.jsonl` as a
  design tried (the baselines are comparators, not variants), and nothing of H4 spends the program's level.
- **The readings, every one reported, none dropped after a look:** 4 baselines x (the deciding `off`, the as-walked
  `off` beside, `worse_1`, `missed_0.1`) on the firm path, and the as-traded reading of the three registered designs
  (H4-A); every measure of Appendix B at each of its horizons and windows, each with MEASURES 1.4's three coin
  readings (the design-level measures readings 1 and 3).
- **The program's honesty sentence:** Stage 2's programs S and U and this repository's F-01 to F-03 read the
  development window; H4 adds no read of the held-out years; the held-out test's level stays nominal while the
  held-out read ledger is not empty (CHARTER 3.6 (b); section 2).

## 9. What H4 hands on, and the floors it must hold

H4 has no deciding line. What it hands on, and the checks that must hold before anything of it is believed:

- **To W42-R1: one collection result** (the lead's ruling on B-4), H4-C, written once from a clean checkout by
  `scripts/h4_collect.py` through `extended.results.write_result`: `results/h4_w42_input.csv` and its manifest, one row
  a baseline, start and seed, every key below a column, on the deciding `off` reading. Its manifest carries the four
  units files' sha256, the declared start list (its count and sha256), each start's **uncapped** sessions left (section
  4, `extended/day_calendar.py` at ebd5a05, the start session counted), the seed indices 0 to J - 1, and the fixed key
  set. **The adapter** `extended/h4_collect.py::w42_readings` builds the four `wave42.BaselineReading`s from that one
  file, block tag `search`, refusing a file whose sha256 differs from its manifest's, any declared start, seed or key
  missing, or readings not paired; its test runs on a synthetic file. The pinning row of CHARTER 3.9 cites the
  collection result's sha256. **The keys**, each the per-unit matrix x[s, c] in MEASURES' never-blank form:
  - `net_month_1` to `net_month_3` and `peak_month_1` to `peak_month_3` (P_B's inputs, measure (13) and MEASURES
    section 2; W42-R1 computes P_B, `run_out` and `not_paid_within_B` at the budgets it sets);
  - **`spent_before_first_payout`** (the per-unit spending before the first
    payout, measures (6) and (24)), `first_payout_days` (measure (5)), `cash_to_first_pass` (measure (2)),
    `peak_oop_12_months` (measure (25)), `share_months_positive` (measure (18));
  - **`orders_max`, `accounts_max` (measure (30)) and `taken_mean` (measure (37)), required now**: the firm path must
    emit them (a build requirement, Appendix C), and the run is refused without them, so W42-R1's three optional
    limits are set, never left to a build.
- **To Wave 4.1:** every per-unit measure's matrix on the deciding `off` reading (the units files), and MEASURES 1.4's
  readings of every reading, for the dimensions, the redundant measures and the trade-off curves (CHARTER 3.9; with
  four baselines the curves come from variation across start days and seeds, not designs).
- **To H3-D:** the per-seed composites' spread of each baseline pair on the search years (the three-way note's 2.5 and
  its 4.3: sigma, and the seed-set replicates of its smaller-J rule), after W42-R1 has set the composite.
- **The floors, each refusing (a failure stops H4 and is diagnosed by the failure protocol):**
  - **the identities** of section 16 hold;
  - **the zero-edge oracle, exactly, per trade:** on the deciding reading's trade log, for every taken trade, the
    race's p g - (1 - p) L is zero and its net expectation minus its costs, in exact fractions from the logged l, g, c
    and x; R-10's walked trades by the walk law's exact terminal distribution; no exit passes the floor (the
    engine's clip never binds), and a floor-side loss lands exactly on the floor and breaches it (E-237's forced-loss
    form). An output outside the oracle is an engine error (the template v2's section 5);
  - **the overlap count** is 0 for every baseline (section 5);
  - **the blank rule:** every per-unit value handed on is finite on its E_h (MEASURES 1.3); a blank refuses the
    reading;
  - **the pairing:** every baseline and arm on one plan's keys (the same role seed, part, starts and seed indices), the
    key guard's sample holding (`three_way_keys.KeyGuard.sampled`).

## 10. Power before the pin: J

- H4 tests nothing, so it has no power gate of its own. Its **seed count J** is set for what it feeds (section 7 and
  Appendix A): enough seeds that W42-R1's resolution of a gap between two baselines, at W42-R1's smallest size that
  matters, is not starved by coin noise, at the twelve-month horizon's complete starts (the strictest, W42-R1's
  dimensions sitting at months 1-3, W and twelve months).
- **What J does not set:** the held-out test's J and m (H3-D's, at delta\* and H4's sigma, the three-way note's 2.2
  (b) and its 2.5), and W42-R1's power forecast (its 5.3 reads the test's J, not H4's).
- **What J's choice moves** (the red team's m-2): W42-R1's delta\* is the smallest *resolved* adjacent gap, and when
  none is resolved a fixed share of the baselines' spread. More of H4's seeds can therefore move delta\* **either
  way**: resolving a small gap lowers it, but resolving one large gap where none was resolved can raise it from the
  spread's share to that gap. Whatever cap W42-R1 as pinned puts on delta\* is the one that holds; H4 cites it at its
  pin. J is fixed here, before any read, and never extended after one.

## 11. The stages and the kill rules

*Kill lines on supply, resolution and realised risk come before any outcome; for comparators they are reported, not
drops.*

- **H4-0 (the probe):** the firm path's cost a lane-trade (the race and R-10's walk terms) and the process's base
  memory on synthetic toys; and **a real read**: the vendored replay's cost a start, timed on P-14's first real
  search-year starts (`user_beside.EXACT_EVERY` of them) on the point arm, **its outputs written sealed** (their hash
  recorded, the file unopened) -- H4-A's replays of the same starts must reproduce that hash.
- **H4-S (the schedules; before any outcome):** the nested cuts (section 4); each baseline's schedule and the identities
  I-1 and I-5; the counts of section 5; the gates -- supply in every search year, resolution (at most 5 % at the
  flatten, overall and in every year), realised risk -- each **reported** for every baseline, a comparator failing one
  kept and labelled. **Kill:** an identity or a nested check failing stops H4; so does an overlap count above 0.
- **The lead's sizing row:** the parts re-declared by size at H4-0's measured cost and H4-S's counted supply (the cut
  rule, Appendix A), before H4-A and H4-B start.
- **H4-A (the as-traded replays):** P-14, P-15, P-16 by `user_beside.run_starts(design, "point", BY_NAME["off"], ...,
  journey=True, journey_block="search")`, every start, every exact run; I-4's reference.
- **H4-B (one part a baseline):** the four arm-runs on the firm path at J seeds; the oracle and the blank rule checked
  as each part writes (section 9). **Kill:** the oracle, the blank rule, or the pairing failing stops H4.
- **H4-C (the collection):** the one result of section 9; its adapter's checks refusing.

## 12. Beside, never deciding

- **Beside each reading** (every one, in its manifest and its rows): the reading's label (deciding, as-walked,
  as-traded) and arm; the record each horizon read (the exact h run or the long run cut at the block's end) and the
  count of starts where they differ (m-8); |E_h| per horizon; MEASURES 1.4's three readings with the two `n_eff`
  values; the share passed and the share paid by W, the censored counts and the strict rule's "at least" flags
  (MEASURES 1.3); the accounts failed at the fill and the days stopped at the fill (L_fill at most `EPS`), counted
  apart, their share beside (v2's section 5); per baseline the time-limited share and mean steps (R-10), the
  news-flatten share and its gap to the as-walked cost (v2's m-4), and the **fill-time law** reading's gap from the
  deciding reading; the **path-structure edge**
  (as-walked less deciding); the share of window sessions after the last nested cut on every twelve-month and W = 252
  reading (section 4); for P-14, P-15, P-16 the label **whole-window-derived registered comparator** ("held out"
  means unread by this search only, E-208); for the coin, its inherited levers' ledger entries (section 2); beside
  each limit W42-R1 sets, the resolution gate's reading of the baseline it came from.
- **Not modelled, said wherever a scorecard appears:** the user's time, taxes.

## 13. The judged block's reads (E-026)

**H4 carries no judged-block reads line** (the design-search template v2's section 14: only the held-out test's
declaration carries one), so the reader authorises no held-out purpose for it. H4 reads no session of the held-out
years in any part; the reader refuses any read reaching 2024-01-02 under its purpose, and the runner's plan refuses any
unit whose window holds one.

## 14. What the reading's completion and a failure mean

- **Complete:** every part ran to its exit from a clean checkout, every identity held, the oracle, the overlap count
  and the blank rule held, the auditor re-derived the outputs (section 16); then the lead applies W42-R1 to H4's
  collection result, once, in the pinning row of CHARTER 3.9, and Wave 4.1 reads the units files.
- **A failure:** an identity, a nested check, the oracle, the overlap count, the blank rule or the pairing failing
  stops H4; it stays on record and is diagnosed by the failure protocol (terminal states, stage decomposition, the
  component alone, replication with seeds fixed before), **never re-run until it passes**. A part re-run after a code
  fix reproduces every finished part byte for byte or all are re-run; nothing of H4 is read by W42-R1 until every part
  is complete.
- **The confirmation:** not H4's; NQ from 2026-07-17 is never read here, and is read for a carried design only, a
  purchase.

## 15. Seeds -- by role, found nowhere else

A block of its own: ten consecutive seeds, one role each. Each seed draws only its role; within a role every draw is a
child keyed by the fixed-length key of its kind (`three_way_keys.seed_key`: the seed, a nonzero tag, exactly the
kind's fields, every word below 2^32), never the seed plus an offset (E-171). **The part is in every key**: H4's parts
take their own part ids in the seed module (`three_way_seeds.PARTS` gains `H4-0` and `H4-B`, Appendix C). The runner
reads its seeds from `extended/three_way_seeds.py` only, as `RoleSeed`s it issues (a literal typed elsewhere, or a value
rebuilt by arithmetic, is refused, `ProvenanceRefused`); the module gains this block with its roles, statuses and
`ROLE_USE`, the spares issued to nothing.

| seed | role | status |
|---|---|---|
| 20264400 | the unit tests: this draft's T-0 and H4's build (synthetic toys only; the `test` kind) | tests |
| 20264401 | H4-0, the probe's synthetic toys (the firm path's cost) | design check |
| 20264402 | H4-B: the coin field on the search years -- every baseline, every arm, every reading; draw kinds the side and reflection coin, the race, R-10's stopped walk, the missed-signal draw (measure (28)); the enforcement kind keyed apart, drawing nothing at `off` | reading |
| 20264403 | spare | spare, drawn by nothing |
| 20264404 | spare | spare, drawn by nothing |
| 20264405 | spare | spare, drawn by nothing |
| 20264406 | spare | spare, drawn by nothing |
| 20264407 | spare | spare, drawn by nothing |
| 20264408 | spare | spare, drawn by nothing |
| 20264409 | spare | spare, drawn by nothing |

- **Inherited seeds, used only as their owners registered them:** the registered jobs' own campaign seeds (Stage 2's,
  in P-14's, P-15's and P-16's jobs, for H4-0's and H4-A's as-traded replays) and Q-17's start seeds
  (`user_beside.start_seed`, from `user_beside.DENIAL_SEED`, Q-17's block), which drive the enforcement stream that
  draws nothing at `off`. None of them draws on the firm path.
- **Not H3's:** H3's block (the three-way note's section 7) is H3's alone; no H4 key carries an H3 role seed, and the
  pairing H3-D needs is with H4's *outputs*, never its keys.
- **For the search:** Wave 5's declaration may inherit this block's coin role only as this file registers it, cited
  with its owner, if it reuses H4's runs; otherwise its survey re-runs the baselines under its own coin seed.
- **The search** (2026-11-20, before the first text was committed; the house search, word-bounded on the block's ten
  values), repeated by the red team over every worktree, the main tree and the run trees (its section 5): no hit but
  this file.
  - `git grep -IlwE` over every branch, remote and tag of the repository: no hit;
  - every line added or removed in every reachable commit (`git log --all -p -G`): no hit;
  - `grep -rIlwE --exclude-dir=.git --exclude-dir=data` over this worktree's working files and the vendored snapshot,
    and over the main tree's working files: no hit before this file.
  - `tests/test_h4_draft.py` repeats the literal scan over every tracked and working file (any suffix, binaries
    skipped), and an arithmetic fold over every tracked `.py` -- the three-way design test's folder, widened to string
    concatenation, f-strings, `int()` and numpy integer calls and `sum` of literals (the red team's m-7) -- allowing the
    block only here, in the seed module and in H4's own result manifests.
- **The scans are a guard, not the defence** (m-7): a construction no static scan can see (a value read from a file, a
  loop that builds it) is refused at run time by the seed module's provenance guard (`ProvenanceRefused`), which is
  the real defence.
- **Trailing zeros and split words** are ruled out by the key form (fixed length per kind, a nonzero tag, every word
  below 2^32), and the guard compares `generate_state`, never the integers.

## 16. The run order -- refusals first

1. **Refusals first**, before anything is read, each refusing: this declaration pinned and unedited
   (`tests/test_declarations_fixed.py`); **W42-R1 pinned before H4 is read** (CHARTER 3.9; E-221), and this file's
   W42-R1 placeholder filled with that pin; the identities on record as holding (`identity/stage2_identity.py`: P-14
   and P-16 reproduced); the registered-constants file on record by its sha256; every dependency of Appendix C merged
   at the commits the go row names; a clean checkout of a named commit (`scripts/run_clean.py`); the run lock held, one
   heavy job on the machine; memory checked.
2. **H4-0**, one heavy slot.
3. **H4-S**, with **the identities**, each before any outcome of the runner is believed:
   - **(I-1) the schedules:** each registered baseline's schedule through the cut's pass-through mode equals its
     registered trigger-level trades dated on or before 2023-12-29 -- times and brackets, path for path -- by the
     **search-year sub-hash** of the registered trades, computed once in the on-record whole-window identity run (E-247
     rm-4's exception), never by H4, and recorded in the registered-constants file: one form for P-14, P-15 and P-16
     (E-248's point-arm start-row identity of P-14 held beside, as the cut's own);
   - **(I-2) the nested cuts** (section 4);
   - **(I-3) the race:** the firm path's race at no cost equals `adapter.BinaryDraw`'s on the same uniforms (the form
     `race_dollars` holds), and its own race step equals the vendored random draw on the same uniforms;
   - **(I-4) the firm path as traded:** with no reflection, the outcomes walked as run and the response `off`, the firm
     path reproduces `user_beside.run_starts(design, "point", ..., journey=True, journey_block="search")` on every
     search-year start of P-14 (and P-15, P-16 in H4-A): every event day equal and each close's `rel` within a
     millionth of a dollar (MEASURES 1.2's tolerance), path for path;
   - **(I-5) the coin's source** (the lead's ruling on B-5): run with its admission restricted to P-16's registered
     offered marks (the registered-constants file), latency-free at those marks, with P-16's news rule, account policy
     and registered sides, it equals P-16's schedule path for path on the search years -- times, brackets, sides and
     the strict rule's routing to accounts; with admission off, its offers equal the clock grid less the void calendar.
4. **The lead's sizing row** (section 11).
5. **H4-A**, then **H4-B**'s parts, then **H4-C**, each one heavy slot, each watched to its exit, each written with its
   manifest (`extended.results.write_result`, `prereg_id` H4, every seed role and parameter, the key kinds, the commit
   of every dependency, the schedules' sha256).
6. **The auditor's re-derivation** (before W42-R1 reads anything): every summary row recomputed from the per-unit
   files; the collection result rebuilt from the units files by the adapter; a declared sample of units -- every
   search year's first start under the first `three_way_keys.SAMPLE_SEEDS` seed indices, every baseline and arm --
   recomputed from the schedules and keys through the firm path, equal bit for bit; the oracle re-checked on the trade
   logs from the logged inputs alone; H4-0's sealed hash against H4-A's same starts; the results' price-level guard
   (`tests/test_results_no_price_levels.py`) on every file.
7. **The collection row** (`/collect`), then W42-R1's application in the pinning row (Wave 4.2), citing the collection
   result's sha256, and Wave 4.1's analysis. A failed check stays on record.

**The outputs** (each from a clean run, with its sidecar manifest, never overwritten; no bar price recoverable from any):
- `results/h4_units_<baseline>.csv`: one row a start, seed and key on the deciding `off` reading -- Wave 4.1's input --
  with the start's date, its uncapped sessions left and its block;
- `results/h4_w42_input.csv`: H4-C's one collection result, W42-R1's only input (section 9);
- `results/h4_readings_<baseline>.csv`: every reading's rows (`journey_readings`' and MEASURES 1.4's), per arm and
  reading, with section 12's beside fields;
- `results/h4_supply.csv`: H4-S's counts and gates, the overlap count among them, per baseline and search year;
- `results/h4_as_traded.csv`: H4-A's rows (`journey_readings.summary` of the replays);
- `results/h4_identities.csv`: each identity's comparison, its counts, its tolerance and its verdict;
- H4-0's sealed file: its hash in the part ledger, the file unopened.

## 17. The build and its tests (after the pin, before any reading)

In this repository's package, nothing vendored edited, every dependency of Appendix C named with its interface:
H4's runner script (`scripts/h4_rebaseline.py`, its parts by name), the collection script and its adapter
(`scripts/h4_collect.py`, `extended/h4_collect.py`), the seed module's H4 block, a baselines-only call of the runner
(`three_way_runner.paired` refuses a design-less call: H4 needs the four baselines on one plan and one guard with no
design), the stress arms by name, and the output writers. Tests, on synthetic data with known answers, each written
before its code: the parts' refusals (a held-out start, a confirmation-window session, a reader span past
2023-12-29); the oracle on planted trade logs (a forced-loss toy that must fail it); the overlap count on a toy with two
positions open at once (it must refuse); the adapter on a synthetic collection file (a missing seed, a missing key, a
changed byte, each refused); the baselines' pairing (every arm on one key set); the outputs' never-blank form; a
held-out row refused before any write.

**T-0** (`tests/test_h4_draft.py`, with this draft): the form; the seed table and its scans; no typed figure; no
held-out window; the dependencies named; every measure of `docs/MEASURES.md` placed in Appendix B; every W42-R1 input
named; Appendix A equal to the script, its figures recomputed; J refused until W42-R1's pin; the sentences that carry
the refusals, the deciding reading, the arm, the nested cuts and the pairing, each held exactly.

## 18. The pin's conditions

- The red team's read answered; the gatekeeper's approval; the seed search repeated at the pin over every worktree.
- **W42-R1 pinned first**, and this file's placeholder for its pinning row and sha256 filled (with J_H4 then printed at
  its constants).
- The three-way runner's correction for RB-1 merged, and the firm path, the cut's pass-through mode, the
  registered-constants file, the `trade_problems` switch-off's row, the collection adapter and the seed module's H4
  block built and merged (Appendix C) -- or this text's interfaces kept as written with any departure re-declared.
- The template's second text (E-247) pinned as read by its red team; any change to its sections 5 or 14 re-checked here.

## 19. Anything chosen after seeing results

*(Empty at the pin.)*

---

## Appendix A. The seed count and the run plan (printed by `docs/plans/scripts/h4/h4_plan.py`)

The sizes are declared; the hours are at the three-way note's assumed costs, never a measurement. Until W42-R1 is
pinned, J is provisional and the plan is sized at it.

<!-- h4_plan: begin -->
```text
H4's seed count J (section 7): a true gap of DELTA_MIN resolved at RESOLVE_Z standard errors with probability POWER, at W42-R1's worst-case variance Q = 1 / (J n)
  J_H4: REFUSED until W42-R1 is pinned (B-6); the lines below are PROVISIONAL, at W42-R1 2bde318's constants, for sizing only
  W42-R1's constants: RESOLVE_Z=2 DELTA_MIN=0.01 POWER=0.8 (z=0.8416); units needed n = ((RESOLVE_Z + z) / DELTA_MIN)^2 = 80749
  search-year sessions: at most 1042 (weekdays 2020-01-02 to 2023-12-29), at least 994 (less 12 a year)
  complete starts at h=63: 932 to 980
  complete starts at h=126: 869 to 917
  complete starts at h=252: 743 to 791
  J_needed = ceil(n / complete starts at h=252, lower) = 109; J (provisional) = the next power of two = 128
  at J (provisional), h=63: gap resolved with probability POWER from 0.0080 to 0.0082
  at J (provisional), h=126: gap resolved with probability POWER from 0.0083 to 0.0085
  at J (provisional), h=252: gap resolved with probability POWER from 0.0089 to 0.0092
  sigma's relative standard error at J (provisional) (a normal sd from J seeds, per start day): 0.0627
H4's heavy slots (at J (provisional)): part | reads | work | hours over 2 workers at the assumed costs 0.05 us, 0.5 us, 5.0 us a lane-trade | c_max (fits 8 h)
  H4-0 probe        | synthetic toys; and P-14's first 21 real search-year starts replayed on the point arm, written sealed (hash recorded, unopened) | 6.451e+05 lane-trades | 0.0  0.0  0.0 | c_max=89285.71 us
  H4-S schedules    | the search years' bars and the registered constants through the cut; the nested cuts 2022-12-30, 2023-06-30, 2023-09-29 against 2023-12-29 | not lane-trades: timed in its log, under the 8 h cap
  H4-A as traded    | p14, p15, p16 by user_beside.run_starts, arm point, journey_block search | 6847 long-run replays | c_max=8.41 s a replay
  H4-B naive_coin   | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.731e+08 lane-trades | 0.0  0.1  0.6 | c_max=65.97 us
  H4-B p14          | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.731e+08 lane-trades | 0.0  0.1  0.6 | c_max=65.97 us
  H4-B p15          | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.731e+08 lane-trades | 0.0  0.1  0.6 | c_max=65.97 us
  H4-B p16          | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.731e+08 lane-trades | 0.0  0.1  0.6 | c_max=65.97 us
  H4-C collection   | the four units files by sha256 into one result for W42-R1 | no lane-trades
memory: cap 2.5 GB over 2 workers, base 0.4 GB assumed (H4-0 measures it), lane 1344 B: at most 632440 lanes a worker; a batch of 21 starts x J = 2688 lanes
the cut rule: a part runs only if H4-0's measured cost (the race's and the walks' terms at H4-S's time-limited share and mean steps) times H4-S's counted supply fits 8 h; otherwise it is split by disjoint start ranges, never by seeds, in the lead's sizing row before it starts
the crash rule: no reading is made until every part completes; a crashed part is re-run whole from its declared seeds, never resumed; each crash is recorded in the part ledger (E-195)
```
<!-- h4_plan: end -->

## Appendix B. The measures (every one of `docs/MEASURES.md`, placed)

Read on every baseline, by the function `docs/MEASURES.md`'s index names, through `extended/journey_measures.py` and
`extended/journey_readings.py`, on the deciding reading (every arm) and the readings beside, with MEASURES 1.4's three
coin readings (the design-level measures readings 1 and 3). "W" is read at W = 126 and at W = 252 beside.

<!-- h4_measures: begin -->
| # | measure | H4 | where | W42-R1 key |
|---|---|---|---|---|
| 1 | Sessions to the first evaluation pass | read | W | — |
| 2 | Cash to the first pass | read | W | `cash_to_first_pass` |
| 3 | Evaluations bought before the first pass | read | W | — |
| 4 | Share of starts passed by session 21 | read | 21 | — |
| 5 | Sessions to the first payout | read | W | `first_payout_days` |
| 6 | Cash spent before the first payout | read | W | `spent_before_first_payout` |
| 7 | The first payout's size | read | W, its share paid beside | — |
| 8 | Share of starts paid by session 21 | read | 21 | — |
| 9 | Sessions to break-even | read | W | — |
| 10 | Share falling back below break-even | read | 252 | — |
| 11 | Deepest fall after break-even | read | 252 | — |
| 12 | Net cash at months 1, 2, 3, 6 and 12 | read | each month | `net_month_1`, `net_month_2`, `net_month_3` |
| 13 | P, and the shares ahead at months 6 and 12 | read; P_B by W42-R1 at its budgets | 63, 126, 252 | `peak_month_1`, `peak_month_2`, `peak_month_3` |
| 14 | Payouts per fee dollar | read, beside (not a dimension, CHARTER 3.9) | 252 | — |
| 15 | Return on money at risk | read | 252 | — |
| 16 | Monthly net in months 4-12 | read | 252 | — |
| 17 | Payouts per month | read | 252 | — |
| 18 | Share of months with a positive net change | read | 252 | `share_months_positive` |
| 19 | Spread of monthly net | read | 252 | — |
| 20 | Longest run of months without a payout | read | 252 | — |
| 21 | The user's longest wait for a payout within 126 sessions | read | 126 | — |
| 22 | Best quarter's share of month-6 net | read, design-level | 126 | — |
| 23 | Largest month's share of the year's payouts | read | 252 | — |
| 24 | Chance of running out before the first payout | its ingredients read; its states at B by W42-R1 | W | `spent_before_first_payout`, `first_payout_days` |
| 25 | Peak out-of-pocket in 12 months | read | 252 | `peak_oop_12_months` |
| 26 | Month-3 net of the unlucky tenth | read | 63 | — |
| 27 | CVaR10 | read, design-level | 63 | — |
| 28 | Headline measures with signals missed | read at 10 % (`missed_0.1`); 20 % not read | each headline's | — |
| 29 | Headline measures at worse fills | read at +1 tick (`worse_1`); +2 not read | each headline's | — |
| 30 | Workload | read; the firm path must emit it | W | `orders_max`, `accounts_max` |
| 31 | Funded-account lifetime | read, design-level | 252 | — |
| 32 | Worst year and highest-volatility period | read by start year, 2023's starts at the horizons they reach | each measure's | — |
| 33 | Break-even denial rate | **not read**: its ladder needs responses beyond `off` | — | — |
| 34 | Luck against design | read (`variance_decomposition` of x[s, c]) | each measure's | — |
| 35 | Naive coin harvesting | the comparator, run | — | — |
| 36 | P-14, P-15 and P-16 | the comparators, run | — | — |
| 37 | Trades available per day, per account and in total | read; the firm path must emit it; from the schedules beside | W | `taken_mean` |
| 38 | Session coverage | read, from the schedules | the search years | — |
| 39 | Longest idle stretch inside the firm's trading day | read, from the schedules | the search years | — |
<!-- h4_measures: end -->

## Appendix C. The dependencies and their interfaces (what H4 needs from each)

<!-- h4_dependencies: begin -->
| dependency | where | status | what H4 needs from it |
|---|---|---|---|
| the seed-paired runner | `extended/three_way_runner.py` on wt/wt-three adedf7f, in its last correction for RB-1 | built; its RB-1 correction to merge | `Plan` (role seed, part, history, starts, seed indices, horizon, the block's sessions, dates, its held-out refusal); one `KeyGuard` over every arm; `stress_arms` selected by name (`worse_1`, `missed_0.1`); a baselines-only call (no design); `matrix`'s never-blank refusal; the redraw's `EXIT_LAW` and R-10's walk (`three_way_redraw`, `three_way_journey`) |
| the firm path | the vendored lockstep with the race as its draw (`vendor/stage2/propedge/campaign/lockstep.py`, imported, never edited) -- the build item after Q-170 | **to build** | a draw class with the engine's draw interface (`settlement = "race"`, called per day and slot with the lanes' cushions, like `adapter.BinaryDraw`), one lane a seed, a batch of starts in lockstep, reading its uniforms from the coin field keyed per user and moment (`three_way_fastkeys`), never a sequential stream; the race L = min(l, c - x_stop) fractional and the take rule L_fill at the fill, so the engine's clip never binds; R-10's walk by `EXIT_LAW`; the strict rule kept (one open position across all accounts, each trade on one account) and **any overlap refused**; the as-walked draw (the reflected path's walked outcome) and the as-traded draw (no reflection) on the same code; the run stopping at the block's last session; per unit (s, c) a journey record of `user_beside.journey_record`'s form (`rel`, `peak_month`, the exact runs' peaks, purchases, accounts' endings and payout closes) so that `journey_measures` reads it unchanged; **required**: the orders a session, the accounts live at once and `taken_d` (measures (30), (37)), so `orders_max`, `accounts_max` and `taken_mean` are emitted for every unit; the per-trade log (l, g, c, x, the law, the outcome, the account) for the oracle and the overlap count; its identities (I-3) and (I-4); its cost a lane-trade and its memory a lane for H4-0 |
| the cut, in its pass-through mode | `extended/search_cut.py` (E-248, built on wt/wt-user); the pass-through mode is **to build**; Q-172's count on P-14 is unaffected | built; pass-through **to build** | for every vendored builder that opens whole-window files (the bars, the atlas, the walk rows): a view cut at a named last day (2023-12-29, and 2022-12-30, 2023-06-30 and 2023-09-29 for the nested cuts), read through the reader under `h4_search_years`, refusing any session from 2024-01-02; **the pass-through mode**: given the registered-constants file (path and sha256, refused on a mismatch), it replaces the statistics a registered builder would compute from the cut rows -- P-15's and P-16's offered marks (`resolved_coin.offered_marks`' result) and each registered design's busiest-day capacity -- by the registered values, wrapping the calls (nothing vendored edited), never re-resolving them; its manifest names every statistic passed through and every one computed from cut rows; the files it opened and their sha256 |
| the registered-constants file | `results/h4_registered_constants.csv` (a name proposed), written once by a script under `identity/` in the on-record whole-window identity run (E-247 rm-4's exception for the parents' registered reproductions) | **to build**, its sha256 cited under the lead's row | P-15's and P-16's offered-mark lists (slots, by rung), each registered design's busiest-day capacity, and the search-year sub-hash of each registered design's trades dated on or before 2023-12-29 (`rc_dev_test.trades_hash`'s form, the same for P-14), all as registered; slots, counts and hashes only, no price |
| the `trade_problems` switch-off | `rc_dev_test.trade_problems`' screen-row and whole-window hash check, for cut rows | **to record** under its own row (the lead's), entered in the cut's `SWITCHED_OFF` | the check replaced, on cut rows only, by I-1's sub-hash comparison; whole-window builds keep it |
| the collection and its adapter | `scripts/h4_collect.py`, `extended/h4_collect.py::w42_readings` | **to build** | section 9's one result from the four units files by their sha256, and the four `wave42.BaselineReading`s from it, with its refusals and its synthetic test |
| the seed module's H4 block | `extended/three_way_seeds.py` (wt/wt-three) | **to build** | section 15's block with its roles, statuses and `ROLE_USE`, the parts `H4-0` and `H4-B`, `issue` refusing the spares; `tests/test_h4_draft.py`'s allowed files include it |
| W42-R1 | `docs/plans/WAVE42_SETTING_RULE.md` and `extended/wave42.py`, **as pinned** (its first text at wt/wt-infra 2bde318 is in its corrective cycle) | built; to pin before H4 | its pinning row and its rule text's sha256 (this file's placeholder); its input form (`BaselineReading`, the keys of `REQUIRED` and `OPTIONAL`, the block tag `search`); its constants `RESOLVE_Z`, `DELTA_MIN`, `POWER_TARGET` and `W`, which H4's J reads |
| the session calendar | `extended/day_calendar.py` at ebd5a05 (Q-166), `load_sources().days` | built | the search-year session list, from which each start's uncapped sessions left are counted, its source file's sha256 |
| the starts and the as-traded replays | `extended/user_beside.py`, `run_starts(design, "point", BY_NAME["off"], ..., journey=True, journey_block="search")` | built (Wave 3.1) | the search-year starts, the block refusal, the exact runs on every start, the as-traded journey records (H4-A) and identity (I-4)'s reference, on the point arm only |
| the measures | `extended/journey_measures.py`, `extended/journey_readings.py` | built (Wave 3.1) | every function `docs/MEASURES.md`'s index names; `coin_readings`, `design_coin_readings`, `variance_decomposition` on x[s, c]; `journey_readings.summary` on the as-traded replays |
| the naive coin's source | `extended/triggers.py` (`CoinMarks`), `extended/components.py` (`coin_component`, `schedule_day`), `extended/router.py` | built (Q-169) | the clock-only schedule over P-16's window, one position at a time, the void calendar, the news convention; an admission restricted to a given mark list, for I-5 |
| the reader | `extended/reader.py` | built | `read_bars` and `authorise_engine_read` under `h4_search_years`, refusing any span reaching 2024-01-02; the ledger lines of a clean run |
<!-- h4_dependencies: end -->

## Appendix D. The red team's read of the first text, answered

<!-- h4_findings: begin -->
| finding | the lead's ruling | where it is answered |
|---|---|---|
| B-1 | the strict rule, one open position across all accounts, each trade on one account; the H3-A4 condition dropped; a refusing overlap count | section 3's one-position and conduct rows; section 7's overlap row; section 12; section 18; sections 5, 9, 11 (the count) |
| B-2 | registered marks inherited by a named file and sha256; I-1 by a search-year sub-hash from the whole-window identity run; the `trade_problems` switch-off under its own row; the cut's pass-through interface | section 2; section 16 (I-1); Appendix C (the cut, the registered-constants file, the switch-off) |
| B-3 | `arm="point"`, asserted in T-0 | section 7's arm row; section 11 (H4-0, H4-A); section 16 (I-4); Appendix C |
| B-4 | one collection result by a named adapter; sessions left uncapped from the day calendar; the three optional keys required | section 4; section 9; section 16's outputs; Appendix C (the firm path, the collection, the calendar) |
| B-5 | I-5: the coin's source at P-16's marks equals P-16's schedule | section 16 (I-5); section 7's coin rows |
| B-6 | H4 cites the pinned W42-R1 by sha256 and pins after it; J refused until then | the header table; section 7's J row; section 16; section 18; the script's `W42_PIN` and `j_h4` |
| B-7 | the held-out read ledger; P-16's shape for the coin labelled the lead's choice | section 2's ledger; section 7's coin row |
| m-1 | the surviving mutants killed | T-0's exact sentences and recomputed figures (`tests/test_h4_draft.py`) |
| m-2 | the text corrected | section 10 |
| m-3 | H4-0 labelled a real read of P-14's starts, its outputs sealed | section 11; Appendix A |
| m-4 | the nested cuts at 2023-06-30 and 2023-09-29 | section 4; section 16 (I-2); Appendix A; Appendix C |
| m-5 | the text corrected | section 7's coin row (the differences listed; I-5 holds the rest) |
| m-6 | MEASURES (35) amended | `docs/MEASURES.md` (35); section 7's coin row |
| m-7 | the scans widened; the runtime guard named the real defence | section 15; T-0 |
| n-1 to n-6 | notes; n-2's law and n-3's print taken | section 7's overlap row (n-2); section 3 and section 12 (n-3) |
| template v2 | the lead's ruling: the family form, v2 wherever it governs | the status paragraph; section 7's deciding row (v2's section 5); section 9's oracle; section 12 (the failed-at-fill count); section 13 (v2's section 14) |
<!-- h4_findings: end -->
