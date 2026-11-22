# H4: the re-baseline -- the four baselines on the journey scorecard, search years only (a draft)

**Status: a draft, text 4 -- a re-declaration, for the red team's full read, with its own two corrective cycles.**
H4's first declaration spent its cycles: its first text (wt/wt-h4 f897cd7) was read in
`docs/reviews/H4_DECL_2026-11-20.md` (blocked: B-1 to B-7, seven minors, six notes; Appendix D), its second (228f972) in
`docs/reviews/H4_DECL_c1_2026-11-21.md` (blocked: RB-1 and RB-2, six minors, four notes; Appendix E), its third
(0727615) in `docs/reviews/H4_DECL_c2_2026-11-21.md` (blocked: RC-1 and RC-2, four material and seven minor findings,
five notes; Appendix F). Under the failure protocol this text is a new declaration; the lead's rulings on all three
reads are carried here. **Text 4's corrective cycle 1 of 2** answers the red team's full read of it (297fe1b,
`docs/reviews/H4_DECL_T4_2026-11-22.md`: blocked on F4-1 and F4-2, four material and eight minor findings, three
notes; Appendix G). Copied from `prereg/TEMPLATE_family.md`'s form
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
reads line). Checked against v2 at 68436c9 in this text; **re-checked against the template's third text when v3 is
pinned** (rn-2); v3's section 5 changes (wt/wt-lit 13df998) are adopted now (section 7, rc-13). **Membership**
(rc-7): H4 is not a search and enters no membership (template v3's membership is the set of firms' searches in the
one joint held-out test, fixed at the first go row of any firm's search). H4's values are search-year readings under
E-208's fixed dates; they serve a member search only if that search's hash row cites H4's pin row. H4 completes before
the membership event, since that first go row needs W42-R1's values; v3's own sentence on the re-baseline ("reads the
search years only") matches this text.

| field | value |
|---|---|
| declaration | H4 (the heavy queue's H4, the restart plan's Wave 4); no family number, **no k** |
| what it reads | the four baselines -- the naive coin, P-14, P-15, P-16 -- on Topstep's $50K, under the zero-edge convention, over J coin seeds, on NQ's search years (2020-01-02 to 2023-12-29) only |
| what it feeds | W42-R1 (`docs/plans/WAVE42_SETTING_RULE.md`, **as pinned**: `<W42-R1's pinning row and the LF sha256 of its three files, filled at W42-R1's pin>`), through one collection result; Wave 4.1's measure-structure analysis; H3-D's power gate (the three-way note's 4.3) |
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
  | P-14 fixed as R\* on the whole window | the user readings that chose it | P-14 | Stage 2 D-626 |
  | Stage 2's signal search | the whole-window search that produced the registered designs' triggers | P-14, P-15, P-16 | Stage 2's search programs |
  | RD-01's late-block reads | its firm-contract readings of the registered designs | P-14, P-15, P-16 | RD-01's pinning row |
  | **the ledger constants H4 uses** | W = 126 and the 252-session window, set with the held-out years visible; U1's `EXACT` horizons | every baseline (H4's windows and exact runs) | Stage 2 D-518, D-620 (3)(f); Q-44 |
  | **P-16's window `all`** | a cell of the whole-window screen that fixed it | P-16; **the coin's window** (inherited) | Stage 2 D-525 (3) |
  | the bar store manifest's held-out metadata | its `day_list`, `early_end_days` and `day_bounds` entries after 2023-12-29, dropped before they are parsed (rn-d); no figure | the search calendar; the void calendar | Q-166; Q-197 |
  | **the registered-constants run itself** | the on-record whole-window identity run's existing read (`identity/stage2_identity.py`'s U1 path rebuilding P-14, P-15 and P-16); it copies the registered marks and capacities by sha256 and computes only the search-year sub-hash, no new statistic of the held-out years | P-14, P-15, P-16 | E-247 rm-4; its own row |

  While this ledger is not empty **the level is nominal** (CHARTER 3.6 (b)): H4 spends none, and the held-out test's
  level is printed nominal beside its verdict.

## 3. Contract fit and conduct (CHARTER section 4, item by item)

| item | H4's answer |
|---|---|
| stops in the stop band, above the cost floor | as registered for P-14, P-15, P-16; the naive coin takes P-16's registered bracket (section 7), inside the band; H4-S checks every baseline's trades against `vendor/stage2/results/stop_band.csv` and reports any outside, counted, beside |
| at least five minutes from alert to order, by hand | P-14 and the naive coin at L = 5 (P-14's registered latency; the lever table's T4 reference); P-15 and P-16 scheduled at their registered marks, latency-free (the template's section 1) |
| one position at a time per firm, five minutes flat between trades | **Stage 2's strict rule for every baseline** (D-409, D-429): one open position across all accounts, five minutes flat, each trade to one account (P-14 built with `one_at_a_time=B.STRICT_GAP`, `customer_journey.py`; P-15 and P-16 through `rc_dev_test.rc_campaign`'s strict gap; the engine's rotation in `propedge/campaign/shared_days.py`); **the naive coin's unchained offers through the same vendored routing** (`shared_days.TradeRouter`: the strict rule at each account's own R, with `can_take`); **the per-unit overlap count on the taken-trade log must be 0** (section 7) |
| at most 5 % of trades reaching the 15:10 CT flatten, overall and in every year | read by H4-S's resolution gate (D-212 as D-308 raised it) on every baseline's schedule before any outcome; a baseline over it is reported, counted, never dropped (it is a comparator); the coin's reading printed beside each limit it sets (n-3) |
| realised risk within 10 % on at least 90 % of trades | H4-S's realised-risk gate (D-212; E-022 (1), E-032's allowance-capped form), reported the same way |
| no entry before 07:35:00 CT on a BLS 08:30 day; FOMC days out | as registered; the naive coin through the void calendar (`extended/day_calendar.py`, Q-166) |
| no entry or fill inside a verified news window; the news-flatten convention | as registered for P-14, P-15, P-16 (P-16's `_nr` cell's news rule); the naive coin under E-223's one convention through the trigger library |
| **conduct tier 1** (no hedging across accounts or firms, no simulator-fill exploitation, no maximum size into major news, no trade copied across accounts, nothing that conceals a pattern) | **held by every baseline**: one open position across all accounts, each trade on one account, so **no trade is copied across accounts** and no two positions are open at once (the strict rule above); no hedging, no opposite positions (one position at a time admits none), one firm. **The breakeven move** (FV3's, part of P-14's, P-15's and P-16's registered protocols and so of the coin's): Topstep's article 10305426 ("auto-breakeven to take advantage of favorable SIM fills") was read against the designs' move by E-012 as a reading, not a ruling, and the lever table's S7 makes the move tier 1 for new designs; H4's comparators keep it as registered (rn-e) |
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
- **The search calendar and sessions left, uncapped** (the lead's ruling on B-4; W42-R1's second text, its 1.2):
  the starts and every session count are read from **the pinned search-year calendar H4 and W42-R1 both bind**, Q-197's
  result and its loader (wt/wt-cal, Appendix C), its digest `wave42.calendar_digest` recorded in H4's manifest as
  `calendar_sha256`. **It must equal the cut's A1 day list date for date, or it is refused** (rm-6): H4-A's starts
  are indices into the job's day list, which is the cut's A1 `days` table, and the firm path's are Q-197's. Each
  start's sessions left are the calendar sessions from the start to 2023-12-29, **the start session counted as
  session 1**, never capped; W42-R1 recomputes them from the same calendar and is never handed
  them. `obs` (the run's length) is that count capped at 252; `E_h` is the starts with at least h sessions left.
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
  - **the naive coin's offers** (the lead's ruling on RB-1): every clock moment of P-16's window `all` on
    `resolved_coin.marks()`'s five-minute grid (`resolved_coin.MARK_STEP`), admission T7 off, at L = 5, through
    Q-166's void calendar and E-223's news convention, **unchained** -- an offer every five minutes, re-entering when
    flat, as P-16's are; never `components.schedule_day`'s chain at one R, never Q-169's router -- each offer **walked
    at every R of P-16's table**, as `resolved_coin.cell_trades` writes P-16's, **by P-16's walk**, `walker.STAGE2`,
    FV3's breakeven move on (the lead's ruling on RC-1), never `triggers.JOURNEY`'s move-off walk; each offer's as-run side drawn **once
    per (session, moment) from the coin's schedule-side seed** (section 15), independent of the seed index, so the
    coin's schedule is **one schedule, built once**, as P-16's is with `resolved_coin.coin_table`; the J seeds move
    only the redraw and the as-walked reading's side; held by I-5. The strict rule is applied once, in routing, by
    the vendored routing the registered designs use (section 3).
- **Counted from the schedules alone, before any outcome**, per baseline and per search year: trades a session (the
  supply), the share of trades reaching a time limit (the 15:10 flatten, a news window, a max hold) and their mean
  R-10 steps, the trades outside the stop band, the realised-risk share, **the breakeven exits** (`o_R` of kind `b`,
  at each R) and **the same-bar exits** (an exit bar equal to the fill bar), each share by year. These are H4-S's
  gates (section 11) and the cost model's inputs (Appendix A's cut rule).
- **The schedule-level overlap, beside, never a kill** (the lead's ruling on RB-2): the trigger-level offers falling
  inside another offer's span [fill bar end, exit bar end at the largest R + 5 min) -- the supply the strict rule prunes in
  routing (D-525, D-429) -- counted per baseline and search year and reported. The refusing count is per unit, on the
  taken trades (section 7's overlap row).
- **The supply's one look-ahead, labelled** (rn-3): on a data-defect day whose bars end before the walk's end, the
  coin's void is decided from that day's last bar (`components.py`'s m-3), a same-day look-ahead on supply, small,
  printed beside the coin's supply count.
- **The walk** is the run's own walk on the real bars (the walker, `extended/walker.py`, its identity E-011, and the
  vendored builders for the registered designs); fills, times and costs stay as run (CHARTER 3.2). **Resolution as run
  now holds only for trades without a move bar before their limit** (F4-11): a trade with one is redrawn by the move
  law whatever its kind, so a historical target may be booked as a flatten or as `b`; a trade without one keeps its
  kind's law, **its kind read from the run's terminal state on the as-walked (reflected) path**, as v2 and v3 say,
  never from the as-run side's walk; the time-limited share by move or no move is printed beside.
- **Two trades at one moment** (F4-14) are numbered `sub` = 0, 1, ... in the schedule's index order, and every outcome
  key carries `sub` beside the moment (`three_way_keys.moment(day, decision, sub)`); **they are never refused**; such
  moments are counted in H4-S, per baseline and year. **Several rungs from one alert** follow the CHARTER's
  convention (section 7's multi-rung row; C3-2's shared path withdrawn): each outcome redrawn independently, one side
  per alert keyed at `sub` 0.

## 6. The side, its persistence and the fill intensity

- **No trade-lift line is read** (E-208 retired it); E-035 (6)'s persistence and E-187's band do not apply.
- **The side is the coin's** under the three-way note's keying, choice 3 (its 1.5): one uniform per user and moment, the
  start in every key, no account and no firm index. On the deciding reading the side moves no outcome (the redraw races
  the barriers with direction removed); it is drawn for the as-walked reading beside. For a market entry it is the
  coin choosing the side; every baseline enters at market or at a registered mark, so no resting entry and **no pair
  rule** arises (the template's section 5); were one found in a schedule, H4-S refuses it.
- **The coin's schedule side** (rn-c) is another draw: each of the coin's offers takes its as-run side once per
  (session, moment) from 20264403 (section 15), independent of every seed index and every bar, as P-16's sides come
  from `resolved_coin.coin_table`. It fixes which offers the coin takes and how they resolve; the J seeds then redraw
  the outcomes and the as-walked side.
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
| the naive coin's signal | when it trades | fixed | the lever table's T1 `coin`: an offer at every moment of `resolved_coin.marks()`'s grid, every `resolved_coin.MARK_STEP` minutes on the clock alone (no bar read to choose one), **unchained** (re-entering when flat), market entry (T5 `market`), L = 5 (T4's reference), admission T7 `off`, the as-run side drawn once per (session, moment) from the coin's schedule-side seed (section 15) |
| the naive coin's sessions | where its moments lie | fixed | P-16's registered window `all` (`resolved_coin.WINDOWS`, 17:00 CT to the cutoff), inherited and ledgered (section 2): every session the firm allows; overlong offers whose order would go live after the firm's last new entry dropped; overnight admitted on the search years (E-231) |
| the naive coin's trade shape and account policy | stop, target, size, accounts, budget | fixed, **the lead's fixed choice** | **P-16's registered job's**: its stop (`rc150_dev_test.STOP`), its target and sizing rule, its account policy (the strict rule at each account's own R, with `can_take`, applied by the vendored routing, `shared_days.TradeRouter`), its purchase budget (`a3_brk30_cb20.BUDGET`) and its protocol; each offer carries every R of P-16's table, the account taking it trading at its own R. The reason: P-16 is a coin design already (Stage 2's family RC), so the comparison isolates timing. The alternatives were P-14's shape (the rung map and its table) or P-15's; the choice was made by a reader of those designs' whole-window journeys, so it is in the held-out read ledger (section 2). The coin differs from P-16 in its schedule (every clock moment against P-16's resolved marks), its latency (L = 5 against P-16's scheduled marks), its news convention (E-223's through the trigger library, against P-16's `_nr` cell) and its void calendar (Q-166); it walks as P-16 does (`walker.STAGE2`, the breakeven move on); I-5 holds its offer list against P-16's, and I-4 the routing. CHARTER 2 fixes the coin's levers "in the declaration": **this is that declaration**; MEASURES (35) says so, and Wave 5's search declaration restates them by citing this file's pinned sha256 |
| the coin's walk | how the coin's offers are walked | fixed | **`walker.STAGE2`, P-16's walk, FV3's breakeven move on** (the lead's ruling on RC-1): the coin is P-16's shape with a coin side, so it keeps P-16's protocol; `triggers.JOURNEY`'s move-off walk is never used for it. **The lever table's S7 (the move dropped) governs designs, and does not apply to H4's coin** |
| the reading that decides | what W42-R1 reads | fixed | the martingale-outcome reading, as the design-search template v2's section 5 declares it: each trade's outcome redrawn at its bracket's driftless first-exit odds by the race, L = min(l, c - x_stop) **fractional, never rounded** (E-237), p = L / (L + g), g the target as placed (a rule's profit level converted to net ticks after the target-side cost), a win +g less x_target, a loss -L less x_stop, a cushion-bound loss ending exactly on the floor and breaching it; **what happens at the fill decided at the fill** by L_fill = min(l, c - max(x_stop, x_flat)), fractional, against the runner's tolerance `EPS`: L_fill above it, the trade is raced or walked; at or below it where the floor's room binds, **the account is failed at the fill** (taken to the floor, replaced at the close as the engine does); where the daily loss limit's room binds, **the day stops** -- there is no "not taken" state; R-10's stopped walk for a trade ending at a time limit (its last sub-step a driftless two-point race to the fractional barrier; the exit map `three_way_redraw.EXIT_LAW`, any other state refused), the map gaining the breakeven state below |
| **the breakeven move's law** | **every trade whose move bar comes before its time limit, whatever its historical kind** (the lead's ruling for the firm path's baseline mode, `BUILD_FIRMPATH_c2_2026-11-21`; it replaces text 4's first wording, under which a trade whose move bar opened before a non-`b` exit kept its exit's law) | fixed | **the move-aware sequential race, time-limited, the exact law**, on one driftless path from the fill, its states: **(1) to the move bar**: R-10's stopped walk from the fill to the move bar's open between -L and +g, **its step count taken from the time to the move bar** (T1, the time from the fill bar's open to the move bar's open: s1 = max(1, ceil(sigma sqrt(T1) / sqrt(`WALK_MAX`))) and n1 = round(sigma^2 T1 / s1^2), at the sigma read at the alert); ending at +g it is a target, at -L a stop; **(2) the move arms** at that open if the walked position x is at least one tick in the trade's favour, and **the stop becomes the entry** (zero gross); otherwise the stop stays at -L; **(3) from x to the trade's time limit, bounded by it**: R-10's stopped walk from x between the entry (armed) or -L (not armed) and +g, **its step taken from the time from the move bar to the limit** (T2: s2 = max(1, ceil(sigma sqrt(T2) / sqrt(`WALK_MAX`))), n2 = round(sigma^2 T2 / s2^2), F4-8), to the 15:10 flatten or the trade's other limit -- its outcomes +g, the entry (booked at zero gross less the breakeven exit's own cost, the registered walk's `EXIT_TICKS` for kind `b`), -L, or the walk's value at the limit. Its gross expectation is exactly zero (optional stopping at each stage); the take rule at the fill nets the breakeven exit's cost too, L_fill = min(l, c - max(x_stop, x_flat, x_b)). **The move bar:** `be_open` is the move bar's **end** index, s + 1 on Stage 2's bar-end clock, **s the first FV3 session open strictly after the fill bar's end** (`s > u`, u the fill bar's end index: the first bar whose end is after the fill bar's end, at the session open -- a fill bar ending exactly at a session open takes the next one; F4-13) among 17:00, 19:00, 08:30 and 13:00 CT, carried in the schedule; **the time limit comes from the clock and the pinned calendars** (the 15:10 CT flatten, the verified news windows), **never from the day's last bar**, the trades where the two differ counted beside; a missing bar is voided only by Q-197's pinned calendar, never by data; the trades where the vendored bar differs from s + 1 are counted beside; **a `be_open` at or after the limit means the trade has no move**, and it takes its kind's law, its kind read from the run's terminal state on the as-walked (reflected) path (the terminal-state map; F4-11). **The two-step law departs from v3's one step per trade** (S-1) **and its one T for both s and n** (s-b): it has two (s1, n1 and s2, n2), labelled so; **its exact-fraction test runs before the pin** (section 18). **The arming threshold's lattice bias, beside** (F4-9): the one-tick threshold is resolved on phase 1's lattice, so the armed share carries a small parity bias against a one-tick reference (small relative to the share, its sign by n1's parity, at the red team's assumed sigma); the mean is untouched. **Beside:** both breakeven shares, the redrawn one and FV3's historical one |
| several rungs from one alert | P-14's rungs, on one market at one moment | fixed | **the CHARTER's convention** (the lead withdrew C3-2's shared path: the red team's BUILD_FIRMPATH_c4 confirmed from the vendored `shared_days.py:357-359` that every registered baseline runs with `one_at_a_time` on, so a second rung of an alert is never taken): **each outcome redrawn independently at its bracket's driftless odds**; **one side per alert, keyed at `sub` 0**, so no opposite positions (conduct tier 1); **under the strict rule a lane never books two rungs of one alert, and a run that does is refused**; **the moments where positions overlap on one market (across accounts or alerts) are counted beside, labelled a known limit of the independent-redraw convention, never deciding** |
| the need-aware and consistency-cap exits | the registered protocols' `need_aware_exits` and `consistency_cap_exits`, on | fixed | **a need-bound Combine trade whose move bar comes before its limit takes the move law at the capped target G' = min(G, need) (the cap exit's at its cap level), as the vendored engine and the staged build do, and only a trade with no move bar takes the plain `profit_level` race at G'** (F4-2; G' in net ticks after the target-side cost; this replaces `EXIT_LAW`'s `profit_level` row for H4, template v3 admitting a zero-gross replacement shown by an exact-fraction test before the pin), **both at R = the R the trade was read at** (`lt["rr"]`), **never `rr_used` on that path**: `sizing._need_exit` picks it from the trade's historical net outcome, a look-ahead |
| the fees | what each redrawn trade pays | fixed | **at the contracts held, as the engine charges them** (D-324: the engine's own `fee_paid`, `lt["fee"]`), never linear in the position |
| a trade without an R | a leaf of the registered table with no R | fixed | **refused**: P-16's abandon leaves (risk 0) take no trade; **no `log_rr` fallback** |
| the volatility at the alert | R-10's sigma, every walk's and the move law's step counts | fixed | **read from bars closed at or before the alert only**, never a bar of the trade. The three-way runner's declaration (H3's draft at wt/wt-three 9e371d7) declares the step's rule from sigma at the alert but no real-bar window (its S1 volatility is latent), so **this one is declared** (the lead's ruling on F4-1): **the standard deviation of one-minute close-to-close changes, in ticks per root minute, over the last 60 bars closed at or before the alert**; the window **crosses session breaks** (the daily break, weekends and holidays) into the previous session's bars, **the break's gap return excluded** (the change across a break is never one of the window's changes), so a 17:00 CT alert is never refused; where the store holds fewer bars behind an alert (the first minutes of its first trading day only), the changes there are, and an alert with fewer than two changes behind it takes its trade out of supply, counted beside; the scramble test (every bar at or after the alert scrambled, sigma unchanged) is a build test; `EPS` and `WALK_MAX` are the declared values `three_way_journey.EPS` and `three_way_journey.WALK_MAX`, cited by key |
| template v3's section 5 | the changes the third text makes (wt/wt-lit 13df998), adopted now (rc-13) | fixed | the walk's floor-side barrier **L_race** = min(l, c - x_stop), not L_fill; a new terminal state, **zero contracts at a positive room: the account ends out of room**, counted apart beside the at-the-fill failures; **the lattice step s per trade** (S-1); **T known at the fill for every row**, `other` included; **the both-barriers-in-one-step rule**; **the time exit's clip credit printed beside**; **a daily loss limit at or below e + max(x_stop, x_flat) refused** at construction; re-checked against v3's pinned text |
| the readings beside | never deciding | fixed | the **as-walked** reading (H4's reflected reading -- **not** the staged build's `outcome="as_walked"`, which re-books the historical gross unreflected and is the build's own cost check, N4-1 -- the real path reflected about the fill by the side coin, **at the run's own exit times** -- the real path's exits at each trade's taken R -- so the occupancy and the routing are the deciding reading's on every seed and only the reflected outcome differs, rn-4; **no booked value lies outside the trade's [-(stop + costs), +(target - costs)]** (rc-11): a flipped trade is booked as the walker's mirror walk's terminal state at the run's exit, held within those bounds, a flipped target never booked as -g, labelled "the as-walked reading at the run's exits, bounded"; the path-structure edge is its gap from the deciding reading) and the **as-traded** reading of P-14, P-15, P-16 (their registered sides, unreflected, H4-A, point arm); the naive coin has no as-traded reading (it has no real side) |
| the responses | the firm's responses switched on | fixed | `off` only (0 % denial, the placement off, the Focused Trader Program off) |
| the stress arms | CHARTER 3.8 (c)'s fill and supply stress | fixed | `worse_1` (measure (29)'s +1 tick on every fill: the entry and each exit) and `missed_0.1` (measure (28)'s 10 % of signals missed), each on every baseline alike, on the deciding reading, on the same keys as `off` (`three_way_runner.stress_arms`, selected by name); **in baseline mode a missed signal keeps the vendored router's hold** (N4-2, the lead's ruling): the vendored router assigns trades at `begin_day`, before outcomes, so the account sits idle until the missed trade's historical exit, as built on wt/wt-firmpath -- re-implementing or mutating the vendored router was rejected; **a labelled difference from the playbook**, where a missed signal frees its account at once, and it applies to every baseline alike |
| the +2 tick and 20 % missed arms | measures (28) and (29)'s other levels | **dropped** | the template's pass line reads +1 tick and 10 % only (its section 10 (c)); the runner's `worse_2` arm is not run by H4 (cost); measures (28) and (29) are read at the levels run |
| the denial ladder | measure (33)'s responses | **dropped** | H4's responses are `off` only (the brief); measure (33) is not read (Appendix B) |
| W | the first-payout window | fixed | **126, pinned** (W42-R1's `W`, which its second text requires of H4's manifest, m-9; U1's and Q-44's ledger constant); the readings at W = 252 are beside, in H4's other files, never in W42-R1's input |
| the reading tag | what W42-R1 accepts | fixed | `martingale_outcome` (W42-R1's `READING`), on every reading of the collection result; the block tag `search` |
| the horizons | where each measure is read | fixed | each measure's own (MEASURES section 4); a month is 21 sessions (CHARTER 2) |
| the exact-length runs | U1's identity on the cut runs (MEASURES 1.1, m-8) | fixed | U1's `EXACT` horizons (the vendored `user_journey.EXACT`, D-620 (3)(f)) on every start of the `off` arm-runs (W3.1's M-2) and on every `user_beside.EXACT_EVERY`-th start of the stress arms; the record each reading read and its differing count in its manifest |
| J | H4's coin seeds | fixed | **`J_H4` of Appendix A**: the smallest power of two at or above the J at which a true gap of W42-R1's `DELTA_MIN` between two baselines clears W42-R1's `RESOLVE_Z` coin standard errors with probability `family_stats.MDL_POWER`, at W42-R1 5.3's worst-case variance (Q = 1 / (J n) at the twelve-month horizon's complete starts, every per-unit difference in [-1, 1]), n from a lower bound of the sessions (the three-way note's 2.5 form with W42-R1's resolution line). **at least W42-R1's `H4_MIN_SEEDS`** (the fewest seeds at which W42-R1 lets a gap resolve; Appendix A prints the comparison); **read at the pinned W42-R1's constants only**: until W42-R1 is pinned the script's `j_h4` refuses and Appendix A prints a provisional reading at its constants at wt/wt-infra 34ee968, for sizing only |
| the seed indices | the coin seeds' indices | fixed | 0 to J - 1 (`three_way_runner.Plan`'s `seed_indices`), the same for every baseline and arm |
| the holiday allowance | the sessions' lower bound for J | fixed | `HOLIDAYS_A_YEAR` of the script: at most that many weekdays a year are not sessions (exchange holidays fall below it), so J is not short |
| the audit sample | the units whose full taken-trade log is written (rc-3) | fixed | 1 % of units (start, seed index), every arm, drawn by 20264404 (section 15), one uniform a unit, a unit sampled when it is below the share; its log's rows and bytes printed in Appendix A, the run refused unless twice that size is free on disk |
| the batch | starts a worker task holds at once | fixed | a batch of 21 starts (a month of starts; the script's `BATCH_STARTS`), its lanes against the memory cap in Appendix A |
| the part cap | the cut rule | fixed | 8 hours a part at H4-0's measured cost (`three_way_arith.PART_CAP_H`); at most 2 workers, one BLAS thread; **H4-B sized as the baseline mode runs it** (F4-4): one vendored replay a unit (start, seed index), at the replay cost Appendix A states, its parts by disjoint start ranges so each fits the cap, **never fewer seeds than J** |
| positions open at once | overlap | fixed, **none** | every baseline holds one open position across all accounts, each trade on one account, five minutes flat between (D-409, D-429): no copying, no overlap. **The refusing count is per unit** (start, seed) and per arm, **on the taken trades**: any two taken trades of the user whose spans **[fill bar end, exit bar end at the taken R + 5 min)** intersect, **on Stage 2's bar-end clock** (the trading day and the bar's end minute after 17:00 CT) -- exactly D-429 and the vendored router's rule (`shared_days.py:357-359`: refused while `open_until + one_at_a_time > entry_t`), so a second fill bar ending exactly five minutes after the first's exit bar ends is admitted and counts 0 (RC-2); counted on each trade's own exit at its taken R, never the router's hold to the latest exit at any R (`latest_exit`), so it is laxer than the router and never a false kill, both exits logged (rc-12); D-429's five minutes are four to five minutes of real flat time, the exit falling inside its bar and the fill at its bar's open (rn-a); **the convention beside** (N4-3): each redrawn outcome is booked at the trade's historical exit for routing and for the room of later trades, though the move law's states run to the limit, and trades overlapping in law are drawn independently -- CHARTER 3.2's convention, with no mean effect; it must be 0, **written for every unit**, and **the auditor recomputes it from the sampled units' logs, without the enforcing code**, equal to the code's count on every sampled unit (section 16; rc-3); the schedule-level count is beside, never a kill (section 5); the firm path refuses any overlap. No joint law is declared here; if Wave 5's designs need one, it is the sequential driftless race on one path (the strong Markov property: exact joint outcomes for any set of intervals containing the fill), never the one-uniform form, which is exact only for nested losses with a common target (the red team's n-2) |
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

- **To W42-R1: one collection result** (the lead's ruling on B-4; W42-R1's second text, its 1.1: H4's one output),
  H4-C, written once from a clean checkout by `scripts/h4_collect.py` through `extended.results.write_result`:
  `results/h4_w42_input.csv` and its sidecar, one row a baseline, start and seed, every key below a column, **on the
  deciding `off` reading** (never the as-walked or as-traded reading). **Its sidecar carries every field of W42-R1's
  `H4_MANIFEST_KEYS`** (W42-R1 at 34ee968, and its pre-pin fix when that lands), `sha256` at the sidecar's top level
  (the file's own) and the others under `write_result`'s `parameters`: `block` (`search`), `reading`
  (`martingale_outcome`), `arm` (`off`), `denial` (0), `placement` (`off`), `focused_trader` (`off`), `W` (126, an
  integer), `baselines` (the four, in W42-R1's order), `starts` (every calendar session), `seeds` (the seed indices
  0 to J - 1), `calendar_sha256` (`wave42.calendar_digest` of the search calendar of section 4) and
  `readings_sha256` (`wave42.readings_digest` of the four readings, recorded by H4's collection, H4-C); beside them
  the four units files' sha256 and each start's **uncapped** sessions left (section 4, for the auditor; W42-R1
  recomputes its own). **H4 carries no held-out counts:** `wave42_apply` reads the pinned held-out calendar itself.
  **The sidecar's own sha256** is taken on its bytes with CRLF normalised to LF, W42-R1's pre-pin convention.
  **The adapter** is `extended/h4_collect.py::w42_readings(path, sidecar) -> {name: BaselineReading}` (W42-R1's
  `ADAPTER`), building the four `wave42.BaselineReading`s (name, block, reading, starts, seeds, values) from that one
  file; it refuses a file whose sha256 differs from its sidecar's, any declared start, seed or key missing, readings
  not paired, or a `readings_sha256` its readings do not reproduce; its test runs on a synthetic file. The pinning row of CHARTER 3.9
  cites the collection result's sha256. **The keys**, each the per-unit matrix x[s, c] in MEASURES' never-blank
  form:
  - `net_month_1` to `net_month_3` and `peak_month_1` to `peak_month_3` (P_B's inputs, measure (13) and MEASURES
    section 2; W42-R1 computes P_B, `run_out` and `not_paid_within_B` at the budgets it sets);
  - **`spent_before_first_payout`** (the per-unit spending before the first
    payout, measures (6) and (24)), `first_payout_days` (measure (5)), `first_pass_days` (measure (1), censored at
    W + 1: W42-R1's second text, its B-5), `cash_to_first_pass` (measure (2)),
    `peak_oop_12_months` (measure (25)), `share_months_positive` (measure (18));
  - **`orders_max`, `accounts_max` (measure (30)) and `taken_mean` (measure (37)), required now**: W42-R1's `REQUIRED`
    holds them; the firm path must emit them (a build requirement, Appendix C), and the run is refused without them,
    so W42-R1's three workload and supply limits are set, never left to a build.
- **To Wave 4.1:** every per-unit measure's matrix on the deciding `off` reading (the units files), and MEASURES 1.4's
  readings of every reading, for the dimensions, the redundant measures and the trade-off curves (CHARTER 3.9; with
  four baselines the curves come from variation across start days and seeds, not designs).
- **To H3-D:** the per-seed composites' spread of each baseline pair on the search years (the three-way note's 2.5 and
  its 4.3: sigma, and the seed-set replicates of its smaller-J rule), after W42-R1 has set the composite.
- **The floors, each refusing (a failure stops H4 and is diagnosed by the failure protocol):**
  - **the identities** of section 16 hold;
  - **the zero-edge oracle, exactly, per trade** (F4-5): on the 1 % audit sample, **an independent scalar replay of
    the same uniforms, matched bit for bit** (as the firm path's C1-4 does); on the deciding reading's trade log of
    every sampled unit, for every taken trade, the race's p g - (1 - p) L is zero and its net expectation minus its
    costs, in exact fractions from the logged l, g, c and x; **the walk's and the move law's laws** checked by their
    exact-fraction tests on synthetic cases, **before the pin** (gross zero, net minus costs, every terminal state's
    probability summing to one), each sampled walk or move trade's booked outcome a terminal state of its law at the
    logged parameters, with that state's cost; **the move law's inputs logged**: x, the step counts (s1, n1, s2, n2),
    the barriers (-L, the armed stop at the entry) and G'; no exit passes the floor (the engine's clip never binds), and
    a floor-side loss lands exactly on the floor and breaches it (E-237's forced-loss form). An output outside the
    oracle is an engine error (the template v2's section 5);
  - **the overlap count, per unit, on the taken trades** is 0 for every baseline and arm (section 7's overlap row),
    written for every unit, and recomputed by the auditor from the sampled units' logs alone, equal to the code's count
    on every sampled unit;
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
  (b) and its 2.5), and W42-R1's power forecast (its 5.3 reads the held-out test's seed count, W42-R1's own declared
  `TEST_SEEDS`, not H4's).
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
  search-year starts (`user_beside.EXACT_EVERY` of them) on the point arm, its job **built through the cut in its
  pass-through mode** (rm-5), **its outputs written sealed** (their hash recorded, the file unopened) -- H4-A's
  replays of the same starts must reproduce that hash.
- **H4-S (the schedules; before any outcome):** the nested cuts (section 4); each baseline's schedule and the identities
  I-1 and I-5; the counts of section 5; the gates -- supply in every search year, resolution (at most 5 % at the
  flatten, overall and in every year), realised risk -- each **reported** for every baseline, a comparator failing one
  kept and labelled; the schedule-level overlap reported beside. **Kill:** an identity or a nested check failing stops
  H4.
- **The lead's sizing row:** the parts re-declared by size at H4-0's measured cost and H4-S's counted supply (the cut
  rule, Appendix A), before H4-A and H4-B start.
- **H4-A (the as-traded replays):** P-14, P-15, P-16 by `user_beside.run_starts(design, "point", BY_NAME["off"], ...,
  journey=True, journey_block="search")`, every start, every exact run; I-4's reference; **its jobs built through
  the cut in its pass-through mode** (rm-5): `run_starts`' calendar guard does not see a build, so the runner
  **refuses a job whose calendar does not end on 2023-12-29**.
- **H4-B (one part a baseline):** the four arm-runs on the firm path at J seeds; the oracle and the blank rule checked
  as each part writes (section 9). **Kill:** the oracle, the blank rule, the pairing, or an overlap count above 0 on
  any unit failing stops H4.
- **H4-C (the collection):** the one result of section 9; its adapter's checks refusing.

## 12. Beside, never deciding

- **Beside each reading** (every one, in its manifest and its rows): the reading's label (deciding, as-walked,
  as-traded) and arm; the record each horizon read (the exact h run or the long run cut at the block's end) and the
  count of starts where they differ (m-8); |E_h| per horizon; MEASURES 1.4's three readings with the two `n_eff`
  values; the share passed and the share paid by W, the censored counts and the strict rule's "at least" flags
  (MEASURES 1.3); the accounts failed at the fill, the days stopped at the fill (L_fill at most `EPS`) and **the
  accounts ended out of room** (v3's section 5), each counted apart, their shares beside; per baseline **both breakeven
  shares** (the redrawn one and FV3's historical one), the trades whose vendored move bar differs from s + 1, and the
  same-bar exits' share; per baseline the time-limited share and mean steps (R-10), the
  news-flatten share and its gap to the as-walked cost (v2's m-4), and the **fill-time law** reading's gap from the
  deciding reading; the **path-structure edge**
  (as-walked less deciding); the share of window sessions after the last nested cut on every twelve-month and W = 252
  reading (section 4); for P-14, P-15, P-16 the label **whole-window-derived registered comparator** ("held out"
  means unread by this search only, E-208); for the coin, its inherited levers' ledger entries (section 2); beside
  each limit W42-R1 sets, the resolution gate's reading of the baseline it came from; the schedule-level overlap
  (section 5); beside the coin's supply count, the data-defect void's same-day look-ahead (rn-3).
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
have their own part ids in the seed module, **as registered at wt/wt-three f454d8d**: `PARTS["H4-0"] == 10`,
`PARTS["H4-B"] == 11`, `PARTS["H4-T"] == 12` (H4's tests), `PARTS["H4-S"] == 13` (the coin's schedule side) and
`PARTS["H4-U"] == 14` (the audit sample). The
runner reads its seeds from `extended/three_way_seeds.py` only, as `RoleSeed`s it issues (a literal typed elsewhere, or
a value rebuilt by arithmetic, is refused, `ProvenanceRefused`); the module holds this block in `H4_ROLES`, with its
statuses and `ROLE_USE`, the spares refused by `issue`. Its role names at f454d8d: `h4_tests`, `h4_0_probe`,
`h4b_coins`, `h4s_schedule_side` (status `schedule`), **`h4_sample`** (status `audit sample`: the audit sample's seed,
which took the spare `h4_spare_4`, its `plant` keys in its own part H4-U at history 0 -- never H4-B, so tests and a run never share a part; F4-7) and the spares `h4_spare_5`
to `h4_spare_9`.

| seed | role | status |
|---|---|---|
| 20264400 | `h4_tests`: the unit tests, this draft's T-0 and H4's build (synthetic toys only; the part H4-T) | tests |
| 20264401 | `h4_0_probe`: H4-0, the probe's synthetic toys (the firm path's cost; the part H4-0) | design check |
| 20264402 | `h4b_coins`: H4-B, the coin field on the search years -- every baseline, every arm, every reading; draw kinds the side and reflection coin, the race, R-10's stopped walk, the missed-signal draw (measure (28)); the enforcement kind keyed apart, drawing nothing at `off` | reading |
| 20264403 | `h4s_schedule_side`: H4-S, the coin's schedule side -- one draw a (session, moment) of the coin's offers, the coin kind's fixed fields with the part H4-S, history 0, seed index 0 and start 0 (the schedule is no user's), so independent of every seed index | schedule |
| 20264404 | `h4_sample`: H4-U, the audit sample of units -- one draw a unit (start, seed index), the `plant` kind's fixed fields with the part H4-U, history 0, the start as the plant and the seed index as the replicate, a unit sampled when its draw is below 1 % (section 7) | audit sample |
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
  - `tests/test_h4_draft.py` repeats the literal scan over every file git can commit -- tracked, and untracked files
    not git-ignored, any suffix, binaries skipped; the worker's scratch `.h4_dev/` is git-ignored, so no `git add`
    can commit it (rn-1) -- and an arithmetic fold over every tracked `.py` -- the three-way design test's folder,
    widened to string concatenation, f-strings, `int()` and numpy integer calls and `sum` of literals (the red team's
    m-7) -- allowing the block only here, in the seed module and in the sidecar manifests of H4's declared result
    files (section 16's outputs), whose seed maps record it.
- **The scans are a guard, not the defence** (m-7): a construction no static scan can see (a value read from a file, a
  loop that builds it) is refused at run time by the seed module's provenance guard (`ProvenanceRefused`), which is
  the real defence.
- **Trailing zeros and split words** are ruled out by the key form (fixed length per kind, a nonzero tag, every word
  below 2^32), and the guard compares `generate_state`, never the integers.

## 16. The run order -- refusals first

0. **The order of the pins** (the lead's ruling on F4-3; W42-R1 at 01e896a refuses to run on a commit whose diff from
   its pin touches its `IMPORTED_FILES`): **H4's collection adapter `extended/h4_collect.py`** (built on this text's
   interface and tested on its synthetic file), **Q-194's reader changes and the results writer merge to master
   before W42-R1 is pinned**; **from W42-R1's pin to H4-C no commit touches W42-R1's `IMPORTED_FILES`**
   (`scripts/wave42_apply.py`'s list at 01e896a); a needed fix there is a W42-R1 re-pin under its own row before any
   H4 part runs, never after.
1. **Refusals first**, before anything is read, each refusing: this declaration pinned and unedited
   (`tests/test_declarations_fixed.py`); **W42-R1 pinned before H4 is read** (CHARTER 3.9; E-221), and this file's
   W42-R1 placeholder filled with that pin; the identities on record as holding (`identity/stage2_identity.py`: P-14
   and P-16 reproduced); the registered-constants file on record by its sha256; every dependency of Appendix C merged
   at the commits the go row names; Q-197's calendar equal to the cut's A1 day list (section 4); every job's calendar
   ending on 2023-12-29; a clean checkout of a named commit (`scripts/run_clean.py`); the run lock held, one heavy job
   on the machine; memory checked; free disk at least twice the audit sample's log size Appendix A prints (rc-3); no
   commit since W42-R1's pin touching its `IMPORTED_FILES` (F4-3).
2. **H4-0**, one heavy slot.
3. **H4-S**, with **the identities**, each before any outcome of the runner is believed:
   - **(I-1) the schedules:** each registered baseline's schedule through the cut's pass-through mode equals its
     registered trigger-level trades whose **trading day** (A1's `date` column, never the clock date: the evening session
     opening the trading day 2024-01-02 belongs to it and is excluded) is on or before 2023-12-29 -- times
     and brackets, path for path -- by the
     **search-year sub-hash** of the registered trades, computed once in the on-record whole-window identity run (E-247
     rm-4's exception), never by H4, and recorded in the registered-constants file: one form for P-14, P-15 and P-16
     (E-248's point-arm start-row identity of P-14 held beside, as the cut's own);
   - **(I-2) the nested cuts** (section 4);
   - **(I-3) the race:** the firm path's race at no cost equals `adapter.BinaryDraw`'s on the same uniforms (the form
     `race_dollars` holds), and its own race step equals the vendored random draw on the same uniforms;
   - **(I-4) the firm path as traded:** with no reflection, the outcomes walked as run and the response `off`, the firm
     path reproduces `user_beside.run_starts(design, "point", ..., journey=True, journey_block="search")` on every
     search-year start of P-14 (and P-15, P-16 in H4-A): every event day equal and each close's `rel` within a
     millionth of a dollar (MEASURES 1.2's tolerance), path for path; **its two start sets compared** first -- the
     firm path's (Q-197's calendar) and H4-A's (the cut's A1 day list) -- equal date for date (rm-6);
   - **(I-5) the coin's source** (the lead's ruling on RB-1), **in P-16's mode** (RC-1, rc-6): its unchained offer
     list, built on A1's walked days (kinds `n` and `b`) with Q-166's void calendar off, D-533's cut, at P-16's
     registered offered marks (the registered-constants file), latency 0, with P-16's `coin_table` sides and its `_nr`
     news rule, walked by `walker.STAGE2` (the breakeven move on), and produced by the vendored
     `resolved_coin.cell_trades` -- its columns `date`, `year`, `decision_ct`, `day_kind`, `decision_slot_minutes`, `S`,
     `stop_ticks`, `entry_t`, `side`, `fee_micro_eq`, then at each of `fv3_rung_walk.RR_GRID`'s twelve Rs `r_R`,
     `g_R`, `c_R`, `mae_R`, `exit_t_R` and `o_R`, then `exit_t` and `flat` at `fresh_rr` -- **equals P-16's
     trigger-level trades by `rc_dev_test.trades_hash`** on the search years; with admission off, in the run's mode,
     its offers equal the clock grid less the void calendar (a separate check). The routing needs no identity of its
     own: I-4 holds the firm path's routing to the vendored replay's.
4. **The lead's sizing row** (section 11).
5. **H4-A**, then **H4-B**'s parts, then **H4-C**, each one heavy slot, each watched to its exit, each written with its
   manifest (`extended.results.write_result`, `prereg_id` H4, every seed role and parameter, the key kinds, the commit
   of every dependency, the schedules' sha256).
6. **The auditor's re-derivation** (before W42-R1 reads anything): every summary row recomputed from the per-unit
   files; the collection result rebuilt from the units files by the adapter; a declared sample of units -- every
   search year's first start under the first `three_way_keys.SAMPLE_SEEDS` seed indices, every baseline and arm --
   recomputed from the schedules and keys through the firm path, equal bit for bit; the oracle re-checked on the trade
   logs from the logged inputs alone, for every taken trade of every sampled unit; **the per-unit overlap count
   recomputed from the sampled units' logs alone, without the enforcing code**, equal to the code's count on every
   sampled unit; H4-0's sealed hash against H4-A's same starts; the results' price-level
   guard
   (`tests/test_results_no_price_levels.py`) on every file.
7. **The collection row** (`/collect`), then W42-R1's application in the pinning row (Wave 4.2), citing the collection
   result's sha256, and Wave 4.1's analysis. A failed check stays on record.

**The outputs** (each from a clean run, with its sidecar manifest, never overwritten; no bar price recoverable from any):
- `results/h4_units_<baseline>.csv`: one row a start, seed and key on the deciding `off` reading -- Wave 4.1's input --
  with the start's date, its uncapped sessions left and its block;
- `results/h4_w42_input.csv`: H4-C's one collection result, W42-R1's only input (section 9);
- `results/h4_readings_<baseline>.csv`: every reading's rows (`journey_readings`' and MEASURES 1.4's), per arm and
  reading, with section 12's beside fields;
- `results/h4_supply.csv`: H4-S's counts and gates, the schedule-level overlap beside, per baseline and search year;
- the per-unit overlap counts, every unit and arm, a column of `results/h4_units_<baseline>.csv`;
- `results/h4_trades_<baseline>.csv`: the full taken-trade log **of the audit sample's units only** (rc-3) -- on the
  race arm **`u` and `mae` are not applicable**, never the historical trade's, and any reader refuses them, **and so
  are `at_need`, `rr_used` and `exit_kind`** (F4-10; the race's own need is `race_need`): unit,
  arm, account, the fill and exit bars on Stage 2's bar-end clock with the trading day, the R taken, the exit at the
  taken R and the router's latest exit (rc-12), l, g, c, the exit costs, the law and its states, the move law's x,
  s1, n1, s2, n2, barriers and G' (F4-5), the trade's `sub` (F4-14), the outcome -- the
  oracle's and the overlap count's audit input, ticks and times only, no price;
- `results/h4_as_traded.csv`: H4-A's rows (`journey_readings.summary` of the replays);
- `results/h4_identities.csv`: each identity's comparison, its counts, its tolerance and its verdict;
- H4-0's sealed file: its hash in the part ledger, the file unopened.

## 17. The build and its tests (after the pin, before any reading)

In this repository's package, nothing vendored edited, every dependency of Appendix C named with its interface:
H4's runner script (`scripts/h4_rebaseline.py`, its parts by name), the collection script and its adapter
(`scripts/h4_collect.py`, `extended/h4_collect.py` -- **the adapter built and merged before W42-R1's pin**, section 16's
order), the seed module's H4 block, a baselines-only call of the runner
(`three_way_runner.paired` refuses a design-less call: H4 needs the four baselines on one plan and one guard with no
design), the stress arms by name, and the output writers. Tests, on synthetic data with known answers, each written
before its code: the parts' refusals (a held-out start, a confirmation-window session, a reader span past
2023-12-29); the oracle on planted trade logs (a forced-loss toy that must fail it); the per-unit overlap count on toy logs in Stage 2's
bar-end clock: a second trade whose fill bar ends exactly five minutes after the first's exit bar ends (admitted,
count 0) and one whose fill bar ends four minutes after (count 1, refused), and the vendored router's admitted
boundary pair counting 0 (RC-2); the breakeven law's exact-fraction test (its three states, gross zero, net minus its
costs); the adapter on a synthetic collection file (a missing seed, a missing key, a
changed byte, each refused); the baselines' pairing (every arm on one key set); the outputs' never-blank form; a
held-out row refused before any write.

**T-0** (`tests/test_h4_draft.py`, with this draft): the form; the seed table and its scans; no typed figure; no
held-out window; the dependencies named; every measure of `docs/MEASURES.md` placed in Appendix B; every W42-R1 input
named; Appendix A equal to the script, its figures recomputed; J refused until W42-R1's pin; the sentences that carry
the refusals, the deciding reading, the arm, the nested cuts and the pairing, each held exactly.

## 18. The pin's conditions

- The red team's read answered; the gatekeeper's approval; the seed search repeated at the pin over every worktree.
- **The move law's and the need-capped law's exact-fraction tests passing on synthetic cases** (F4-8, F4-2), and
  `extended/h4_collect.py` merged before W42-R1's pin (F4-3).
- **W42-R1 pinned first**, and this file's placeholder for its pinning row and its three files' sha256 filled (with
  J_H4 then printed at its constants).
- The three-way runner's correction for RB-1 merged, **the firm path (Q-185) corrected for H4's baseline mode at a named
  commit** (Appendix C), and the cut's pass-through mode, the
  registered-constants file, the `trade_problems` switch-off's row, the collection adapter and the seed module's H4
  block built and merged (Appendix C) -- or this text's interfaces kept as written with any departure re-declared.
- The template's second text (E-247) pinned as read by its red team; any change to its sections 5 or 14 re-checked here;
  **this text re-checked against the template's third text when v3 is pinned** (rn-2).

## 19. Anything chosen after seeing results

*(Empty at the pin.)*

---

## Appendix A. The seed count and the run plan (printed by `docs/plans/scripts/h4/h4_plan.py`)

The sizes are declared; the hours are at the three-way note's assumed costs, never a measurement. Until W42-R1 is
pinned, J is provisional and the plan is sized at it.

<!-- h4_plan: begin -->
```text
H4's seed count J (section 7): a true gap of DELTA_MIN resolved at RESOLVE_Z standard errors with probability POWER, at W42-R1's worst-case variance Q = 1 / (J n)
  J_H4: REFUSED until W42-R1 is pinned (B-6); the lines below are PROVISIONAL, at W42-R1 01e896a's constants, for sizing only
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
  W42-R1's floor H4_MIN_SEEDS = 62: J (provisional) = 128 meets it; the held-out test's J is W42-R1's TEST_SEEDS = 1000, not H4's
H4's heavy slots (at J (provisional)): part | reads | work | hours over 2 workers at the assumed costs 0.05 us, 0.5 us, 5.0 us a lane-trade | c_max (fits 8 h)
  H4-0 probe        | synthetic toys; and P-14's first 21 real search-year starts replayed on the point arm, built through the cut, written sealed (hash recorded, unopened) | 6.451e+05 lane-trades | 0.0  0.0  0.0 | c_max=89285.71 us
  H4-S schedules    | the search years' bars and the registered constants through the cut; the coin's unchained offers at every R of P-16's table, one schedule side a (session, moment); the nested cuts 2022-12-30, 2023-06-30, 2023-09-29 against 2023-12-29 | not lane-trades: timed in its log, under the 8 h cap
  H4-A as traded    | p14, p15, p16 by user_beside.run_starts, arm point, journey_block search | 6847 long-run replays | c_max=8.41 s a replay
H4-B as the baseline mode runs it (F4-4): one vendored replay a unit; a replay measured at 0.0378 s on a synthetic campaign (h4_replay_cost.py), sized at x4: 0.1512 s
  H4-B naive_coin   | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.662e+05 long-run replays | 18.2 h over 2 workers | 3 parts of disjoint start ranges, 6.1 h each, every seed in every part
  H4-B p14          | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.662e+05 long-run replays | 18.2 h over 2 workers | 3 parts of disjoint start ranges, 6.1 h each, every seed in every part
  H4-B p15          | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.662e+05 long-run replays | 18.2 h over 2 workers | 3 parts of disjoint start ranges, 6.1 h each, every seed in every part
  H4-B p16          | the firm path, J=128 seeds, 4 arm-runs (off deciding; off as-walked, beside; worse_1 deciding; missed_0.1 deciding) | 8.662e+05 long-run replays | 18.2 h over 2 workers | 3 parts of disjoint start ranges, 6.1 h each, every seed in every part
  the oracle (F4-5): the 1% sample's units replayed by the scalar path at x4 a replay: 0.7 h a baseline, inside its parts
  H4-C collection   | the four units files by sha256 into one result for W42-R1 | no lane-trades
the audit sample's log (rc-3): 1% of units, every arm-run, at most 5377720 rows a baseline at 128 B a row: 2.75 GB over the four baselines; the run is refused unless 2 x that, 5.51 GB, is free on disk
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
| 1 | Sessions to the first evaluation pass | read | W | `first_pass_days` |
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
| the seed-paired runner | `extended/three_way_runner.py` on wt/wt-three adedf7f, in its last correction for RB-1 | built; its RB-1 correction to merge; **the `b` state to build** (RC-1) | `Plan` (role seed, part, history, starts, seed indices, horizon, the block's sessions, dates, its held-out refusal); one `KeyGuard` over every arm; `stress_arms` selected by name (`worse_1`, `missed_0.1`); a baselines-only call (no design); `matrix`'s never-blank refusal; the redraw's `EXIT_LAW` and R-10's walk (`three_way_redraw`, `three_way_journey`); **the breakeven state carried** -- `EXIT_LAW` gains `b` with the time-limited move-aware sequential race for every trade whose move bar is before its limit (section 7), its move bar's end index in each trade, its exact-fraction test |
| the firm path | **Q-185**, `extended/three_way_firm.py` on wt/wt-firmpath de1049e or later (merged as b318b5f), the vendored lockstep with the race as its draw (`vendor/stage2/propedge/campaign/lockstep.py`, imported, never edited) | **built; to correct for H4** (rc-4): **a baseline mode** with routing through the vendored `TradeRouter` (the strict rule at each account's R, `can_take`), never Q-169's router plus refusal; same-bar exits allowed, `entry <= exit` on Stage 2's clock; the `b` state; every R of P-16's table carried; the per-unit overlap counts and the audit sample's log; both exits logged; the bounded as-walked booking -- the lead sends these to its worker | **the baseline mode's interface** (F4-4): wrapped vendored draws (`RaceOver`, `settlement = "race"`, called per day and slot with the account's cushion, like `adapter.BinaryDraw`), **one vendored replay a unit** (start, seed index), reading its uniforms from the coin field keyed per user, moment and `sub` (`three_way_fastkeys`; F4-14, never a duplicate refusal), never a sequential stream; the race L = min(l, c - x_stop) fractional and the take rule L_fill at the fill, so the engine's clip never binds; R-10's walk by `EXIT_LAW`; the strict rule kept (one open position across all accounts, each trade on one account), applied by **the vendored routing the registered designs use** (`shared_days.TradeRouter`, `one_at_a_time` at the account's R, `can_take`, P-16's cap and rule), for the coin's unchained offers too, and **any overlap refused**; the as-walked draw (the reflected path's walked outcome) and the as-traded draw (no reflection) on the same code; the run stopping at the block's last session; per unit (s, c) a journey record of `user_beside.journey_record`'s form (`rel`, `peak_month`, the exact runs' peaks, purchases, accounts' endings and payout closes) so that `journey_measures` reads it unchanged; **required**: the orders a session, the accounts live at once and `taken_d` (measures (30), (37)), so `orders_max`, `accounts_max` and `taken_mean` are emitted for every unit; the per-trade log of every taken trade (unit, arm, account, fill and exit bars, the R taken, l, g, c, x, the law, the outcome) for the oracle and the per-unit overlap count, which the auditor recomputes without this code; **the firm path's baseline-mode laws as `BUILD_FIRMPATH_c2_2026-11-21` rules them**: the time-limited move law for every trade whose move bar is before its limit, phase 1's steps from the time to the move bar, `be_open` the move bar's end index s + 1, need-aware and cap exits at `lt["rr"]`, fees at size (D-324), a trade without an R refused, `u` and `mae` not applicable on the race arm; its identities (I-3) and (I-4); its cost a lane-trade and its memory a lane for H4-0 |
| the cut, in its pass-through mode | `extended/search_cut.py` (E-248, built on wt/wt-user); the pass-through mode is **to build**; Q-172's count on P-14 is unaffected | built; pass-through **to build** | for every vendored builder that opens whole-window files (the bars, the atlas, the walk rows): a view cut at a named last day (2023-12-29, and 2022-12-30, 2023-06-30 and 2023-09-29 for the nested cuts), read through the reader under `h4_search_years`, refusing any session from 2024-01-02; **the pass-through mode**: given the registered-constants file (path and sha256, refused on a mismatch), it replaces the statistics a registered builder would compute from the cut rows -- P-15's and P-16's offered marks (`resolved_coin.offered_marks`' result) and each registered design's busiest-day capacity -- by the registered values, wrapping the calls (nothing vendored edited), never re-resolving them; its manifest names every statistic passed through and every one computed from cut rows; the files it opened and their sha256; **H4-0's and H4-A's jobs built inside it**, each job's calendar ending on 2023-12-29 (rm-5); **its A1 day list equal to Q-197's calendar**, refused otherwise (rm-6) |
| the registered-constants file | `results/h4_registered_constants.csv` (a name proposed), written once by a script under `identity/` in the on-record whole-window identity run (E-247 rm-4's exception for the parents' registered reproductions), its read the identity run's existing one, its own ledger line (section 2) | **to build**, its sha256 cited under the lead's row | **copied, by sha256, from the registered result files**: P-15's and P-16's offered-mark lists (slots, by rung) and each registered design's busiest-day capacity (P-15's and P-16's: the screen rows' `capacity` and `busiest_day`, `rc_dev_test.trade_problems`' fields, from `rc_reentry_screen.csv` and `rc_width_screen.csv` at their registered `SCREEN_SHA256`; **P-14's**: the field `trades_per_day_capacity` of `vendor/stage2/results/a3_brk30_cb20_gate.csv.manifest.json`, sha256 `c9c3356760f33fa3bb5aaff8e59175bff5fd9824d004086398ed529993d003e1`, as `a3_brk30.capacity` recorded it, rc-10); **computed: only** the search-year sub-hash of each registered design's trades whose trading day (A1's `date`) is on or before 2023-12-29 (`rc_dev_test.trades_hash`'s form, the same for P-14); slots, counts and hashes only, no price |
| the `trade_problems` switch-off | `rc_dev_test.trade_problems`' screen-row and whole-window hash check, for cut rows | **to record** under its own row (the lead's), entered in the cut's `SWITCHED_OFF` | the check replaced, on cut rows only, by I-1's sub-hash comparison; whole-window builds keep it |
| the collection and its adapter | `scripts/h4_collect.py`, `extended/h4_collect.py::w42_readings(path, sidecar)` (W42-R1's `ADAPTER`) | **to build** | section 9's one result from the four units files by their sha256, its sidecar with `sha256` at the top level and the binding fields under `parameters`, the sidecar's own sha256 on its LF-normalised bytes, and the four `wave42.BaselineReading`s from it, with its refusals and its synthetic test |
| the seed module's H4 block | `extended/three_way_seeds.py` (wt/wt-three) | **to build** | section 15's block with its roles, statuses and `ROLE_USE`, the parts `H4-0`, `H4-S` and `H4-B`, `issue` refusing the spares; `tests/test_h4_draft.py`'s allowed files include it |
| W42-R1 | `docs/plans/WAVE42_SETTING_RULE.md`, `extended/wave42.py` and `scripts/wave42_apply.py`, **as pinned**, cited by the LF sha256 of all three files (its first text at wt/wt-infra 2bde318; its second at 357a339; its third at 34ee968; **its pre-pin fix at c72526d**, merged as 75ff709; its commit c014d0a, where the public `composite_per_seed`, `limit_estimate` and `null_journeys` landed; **its last pre-pin fix at 01e896a**, where `DO_NOTHING_EPS` and `above_floor` are declared and `scripts/wave42_apply.py`'s commit rule refuses a run whose diff from the pin touches `IMPORTED_FILES`, F4-12, F4-3) | built; to pin before H4 | its pinning row and its three files' sha256 (this file's placeholder); its input form (`BaselineReading` with its `reading` tag, `H4Binding`, `H4_MANIFEST_KEYS` with `arm` and the verdict settings, the keys of `REQUIRED`, `first_pass_days` and the three workload and supply measures among them); `ARM`, `VERDICT`, `COLLECTION_RESULT` and `ADAPTER`; `calendar_digest` and `readings_digest`, which H4's collection records; its constants `RESOLVE_Z`, `DELTA_MIN`, `POWER_TARGET`, `W`, `READING` and `H4_MIN_SEEDS`, which H4's J and manifest read; its `TEST_SEEDS`, the held-out test's J, not H4's |
| the search calendar | Q-197's pinned search-year calendar (`search_calendar.csv`, W42-R1's `SEARCH_CALENDAR`) and its loader (wt/wt-cal), the one calendar H4 and W42-R1 both bind | **to build** (Q-197) | the search years' session dates, 2020-01-02 to 2023-12-29, strictly increasing, by its loader; its result file's sha256 under its row; H4's starts, every session count and `calendar_sha256` read from it, never from another list; **equal to the cut's A1 day list date for date, refused otherwise** (rm-6); **the held-out manifest entries dropped before they are parsed** (rn-d) |
| the starts and the as-traded replays | `extended/user_beside.py`, `run_starts(design, "point", BY_NAME["off"], ..., journey=True, journey_block="search")` | built (Wave 3.1) | the search-year starts, the block refusal, the exact runs on every start, the as-traded journey records (H4-A) and identity (I-4)'s reference, on the point arm only |
| the measures | `extended/journey_measures.py`, `extended/journey_readings.py` | built (Wave 3.1) | every function `docs/MEASURES.md`'s index names; `coin_readings`, `design_coin_readings`, `variance_decomposition` on x[s, c]; `journey_readings.summary` on the as-traded replays |
| the naive coin's source | the trigger library's offers (`extended/triggers.py`, `extended/components.py`), **re-built as an unchained offer list** -- not `schedule_day`'s chain, not `extended/router.py` | **to build** (its unchained form) | every moment of `resolved_coin.marks()`'s grid in P-16's window `all`, unchained, admission T7 off at L = 5, the void calendar and E-223's news convention, each offer walked **by `walker.STAGE2` (the breakeven move on), never `triggers.JOURNEY`**, at every R of P-16's table in `resolved_coin.cell_trades`' columns, its as-run side from the coin's schedule-side seed once per (session, moment); an admission restricted to a given mark list at latency 0 with given sides and news rule, for I-5; the list handed to the firm path's vendored routing |
| the walk | `extended/walker.py`'s `STAGE2` preset (P-16's walk, FV3's breakeven move on, held to `fv3_rung_walk` and P-16's pinned trades by its own identity) | built | the coin's walk and I-5's; the move bar (`be_open`) of every trade carried into the schedule |
| the reader | `extended/reader.py` | built | `read_bars` and `authorise_engine_read` under `h4_search_years`, refusing any span reaching 2024-01-02; the ledger lines of a clean run |
<!-- h4_dependencies: end -->

## Appendix D. The red team's read of the first text, answered

<!-- h4_findings: begin -->
| finding | the lead's ruling | where it is answered |
|---|---|---|
| B-1 | the strict rule, one open position across all accounts, each trade on one account; the H3-A4 condition dropped; a refusing overlap count | section 3's one-position and conduct rows; section 7's overlap row; section 12; section 18; sections 5, 9, 11 (the count) |
| B-2 | registered marks inherited by a named file and sha256; I-1 by a search-year sub-hash from the whole-window identity run; the `trade_problems` switch-off under its own row; the cut's pass-through interface | section 2; section 16 (I-1); Appendix C (the cut, the registered-constants file, the switch-off) |
| B-3 | `arm="point"`, asserted in T-0 | section 7's arm row; section 11 (H4-0, H4-A); section 16 (I-4); Appendix C |
| B-4 | one collection result by a named adapter; sessions left uncapped from the pinned search calendar (Q-197); the three optional keys required | section 4; section 9; section 16's outputs; Appendix C (the firm path, the collection, the calendar) |
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
| W42-R1's second text (357a339) | its obligations on H4: the manifest's `readings_sha256`, `calendar_sha256` and optional measures; W pinned at 126; `first_pass_days`; the reading tagged `martingale_outcome`; at least `H4_MIN_SEEDS` seeds; `TEST_SEEDS` W42-R1's; cited by its two files' sha256 once pinned; Q-197's calendar | the header table; section 4; section 7's W, reading-tag and J rows; section 9; section 10; Appendix A; Appendix B row 1; Appendix C |
| template v2 | the lead's ruling: the family form, v2 wherever it governs | the status paragraph; section 7's deciding row (v2's section 5); section 9's oracle; section 12 (the failed-at-fill count); section 13 (v2's section 14) |
<!-- h4_findings: end -->

## Appendix E. The red team's re-read of the second text, answered

<!-- h4_findings_c2: begin -->
| finding | the lead's ruling | where it is answered |
|---|---|---|
| RB-1 | the coin's offers unchained, walked at every R of P-16's table, its side from one declared schedule-side seed, routed by the vendored registered routing; I-5 a `trades_hash` equality | section 5; section 7's coin rows; section 15 (the schedule-side seed, the part H4-S); section 16 (I-5); Appendix C (the coin's source, the firm path) |
| RB-2 | the refusing count per unit on the taken-trade log, the five minutes flat in its span, recomputed by the auditor; the schedule-level count beside | section 7's overlap row; sections 3, 5, 9, 11, 12, 16 and 17; the outputs' trade logs |
| rm-1 | W42-R1 at 34ee968: `arm`, `denial`, `placement`, `focused_trader`; no `optional_measures`; `readings_sha256` by the collection; three files pinned; `w42_readings(path, sidecar)`; no held-out counts; the sidecar's LF-normalised sha256 | section 9; the header table; section 18; Appendix C; the script's `W42_PIN` |
| rm-2 | the surviving mutants killed, E10 and E21 first | T-0's exact sentences (`tests/test_h4_draft.py`) |
| rm-3 | the missing ledger entries | section 2's ledger |
| rm-4 | the constants copied by sha256, only the sub-hash computed; I-1 on the trading day | section 2's ledger; section 16 (I-1); Appendix C |
| rm-5 | H4-0's and H4-A's jobs through the cut; a job not ending 2023-12-29 refused | section 11; section 16's refusals; Appendix C |
| rm-6 | Q-197's calendar equal to the cut's A1 day list; I-4 compares the start sets | section 4; section 16 (I-4); Appendix C |
| rn-1 | `.h4_dev/` git-ignored; the declared patterns narrowed | `.gitignore`; section 15; T-0 |
| rn-2 | the membership sentence; re-checked at v3's pin | the status paragraph; section 18 |
| rn-3 | the data-defect void's same-day look-ahead labelled | section 5; section 12 |
| rn-4 | the as-walked reading at the run's own exit times | section 7's readings-beside row |
<!-- h4_findings_c2: end -->

## Appendix F. The red team's last read of the third text, answered

<!-- h4_findings_c3: begin -->
| finding | the lead's ruling | where it is answered |
|---|---|---|
| RC-1 | the registered protocols with FV3's breakeven move; a `b` exit's law the move-aware sequential race; the coin on P-16's protocol, move on; I-5 in `STAGE2` mode; S7 governs designs, not H4's coin; the `b` state a runner build item | section 5; section 7's coin-walk and breakeven rows; section 16 (I-5); Appendix C (the runner, the firm path, the coin's source, the walk) |
| RC-2 | the span [fill bar end, exit bar end + 5 min) on Stage 2's bar-end clock, D-429 and the vendored router exactly; the toy test fixed; the router's boundary pair counts 0 | section 7's overlap row; section 17; T-0 |
| rc-3 | per-unit counts for every unit; the full log for a seeded 1 % sample (20264404); the auditor equal on every sampled unit; the sample log's size printed and a disk refusal at twice it | section 7's audit-sample row; section 9; section 15; section 16; Appendix A |
| rc-4 | Q-185 named at de1049e or later, built, to correct for H4's baseline mode | Appendix C; section 18 |
| rc-5 | the eleven survivors killed | T-0's exact sentences |
| rc-6 | I-5 on A1's walked days with Q-166 off; `cell_trades`' columns, twelve Rs | section 16 (I-5) |
| rc-7 | H4 enters no membership; its values serve a member search only by a hash row citing H4's pin row | the status paragraph |
| rc-8 | I-1's example: the evening session opening the trading day 2024-01-02 is excluded | section 16 (I-1) |
| rc-9 | W42-R1 at c72526d; its public functions cited when they land | Appendix C; the script's provisional commit |
| rc-10 | P-14's capacity source file by path and sha256 | Appendix C (the registered-constants file) |
| rc-11 | the as-walked reading bounded within the trade's bracket, labelled | section 7's readings-beside row |
| rc-12 | both the exit at the taken R and the router's latest exit logged | section 7's overlap row; section 16's outputs |
| rc-13 | v3's section 5 changes adopted, "out of room" among them | section 7's v3 row; section 12 |
| rn-a to rn-e | D-429's real flat time; the schedule side in section 6; the metadata dropped before parsing; the breakeven move against conduct tier 1 | section 7's overlap row; section 6; section 2's ledger and Appendix C; section 3 |
<!-- h4_findings_c3: end -->

## Appendix G. The red team's full read of text 4, answered (its corrective cycle 1)

<!-- h4_findings_t4: begin -->
| finding | the lead's ruling | where it is answered |
|---|---|---|
| F4-1 | the estimator declared: the standard deviation of one-minute close changes in ticks per root minute over the last 60 bars by the alert, across session breaks with the gap return excluded; `EPS` and `WALK_MAX` by key | section 7's volatility row |
| F4-2 | a need-bound trade with a move bar takes the move law at G' = min(G, need); only a trade with no move bar the plain `profit_level` race | section 7's need-aware row |
| F4-3 | the adapter, Q-194's reader changes and the results writer merged before W42-R1's pin; no commit on `IMPORTED_FILES` from that pin to H4-C | section 16's order and refusals; section 17; section 18 |
| F4-4 | H4-B sized as the baseline mode runs it, one vendored replay a unit, measured on a synthetic replay; parts to fit the cap, never fewer seeds | section 7's part-cap row; Appendix A; Appendix C; `docs/plans/scripts/h4/h4_replay_cost.py` |
| F4-5 | the oracle an independent scalar replay of the same uniforms on the sample, bit for bit; the laws' exact-fraction tests before the pin; the move law's inputs logged | section 9; section 16's outputs |
| F4-6 | the thirteen survivors killed, the look-ahead ones first | T-0's exact cells |
| F4-7 | `h4_sample` in H4-U at f454d8d | section 15 |
| F4-8 | phase 2's step declared; the two-step departure from v3 labelled; the exact-fraction test before the pin | section 7's breakeven row; section 18 |
| F4-9 | the arming threshold's lattice bias stated beside | section 7's breakeven row |
| F4-10 | `at_need`, `rr_used` and `exit_kind` not applicable on race-arm rows | section 16's outputs |
| F4-11 | the kind of a trade with no move bar read from the reflected path | section 5; section 7's breakeven row |
| F4-12 | W42-R1 cited at 01e896a | Appendix C; the script's provisional commit |
| F4-13 | the move bar's tie rule; the limit from the clock and the calendars | section 7's breakeven row |
| F4-14 | `sub` numbered in index order, in the outcome key, never refused | section 5; Appendix C; section 16's outputs |
| N4-1 to N4-3 | the as-walked reading not the staged `as_walked`; in baseline mode a missed signal keeps the vendored router's hold, a labelled difference from the playbook, every baseline alike; the booking convention beside | section 7's readings-beside, stress and overlap rows |
| C3-2 (the firm path's review), withdrawn | the CHARTER's convention in place of the shared path: each outcome redrawn independently at its bracket's driftless odds; one side per alert keyed at `sub` 0; a lane never books two rungs of one alert under the strict rule, a run that does refused; overlapping-position moments counted beside as a known limit, never deciding | section 7's multi-rung row; section 5 |
<!-- h4_findings_t4: end -->
