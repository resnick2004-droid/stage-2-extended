# DRAFT F-B: one multi-feature model choosing the side of a fixed regular-session schedule (family B) -- redrafted, not a declaration

**Status: DRAFT, second version, 2026-11-16 (TASK_QUEUE Q-29), redrafted from the red team's review
`docs/reviews/DRAFT_F-B_multifeature_2026-11-15.md` (verdict: must be redrafted). Not pinned, no F-number.** Nothing
of the family is built beyond the feature library it names (`extended/features.py`, Q-11, synthetic bars only) and one
synthetic test of its side rule (`tests/test_family_b_side_rule.py`); no bar has been read for it, no label computed,
no model fitted on data, no outcome of anything seen. This file may be edited until the lead pins it; from the pinning
row on, nothing in it is edited (a change is a new family). The family number is **k = the next free (11 if pinned
next)**, so the level is one-sided **0.05 / (k (k + 1))** (0.05 / 132 at k = 11). Seeds are **proposed** in
20261960-20261969 (section 19), checked unique on 2026-11-16, for the lead to confirm at pinning.

It follows `vendor/stage2/prereg/TEMPLATE.md` and `FAMILY_TEMPLATE.md` as this repository adapts them after E-008 (the
pass line is the trades' calibrated lift over the coin twin; the user scorecard beside), the Phase 0 audit's sections
(`docs/audits/phase0/D_protocol.md` Part 3), CHARTER section 2's journey scorecard (E-014, E-015), and
`prereg/DRAFT_F-02_resting_levels.md`'s forms where the review points to them (the confirmation, the valuation caps,
the seeds).

---

## 0. In plain words (for the operator)

Stage 2's coin chooses long or short at random on a fixed schedule of trades. This family asks one question: **can a
model that looks only at NQ's recent price and volume choose the side better than the coin, on the same trades, by
enough to be worth money?** The model is a simple, pre-registered one (a regularised logistic regression on 45
measurements of the market, each scaled to the market's own recent volatility or volume). It is trained on 2020-2023
only, frozen, and judged once on 2024-01-02 to 2026-07-16. **It trades from 09:05 CT on, never in the first half-hour
of the US session** -- the half-hour is the territory of Stage 2's closed opening-range research, whose reopening is
the operator's decision. It passes only if its side beats the coin's by more than chance at the family's strict level,
also beats being long in a rising market and each of the three follow-the-move rules Stage 2 already found, holds up
when its sides are slid against the outcomes in time, and is worth at least $500 a year where its trades are actually
used. Expected in advance: the model will predict **how fast** a trade resolves (a check that the machinery works), but
probably **not which way**. A "no" is a valid close.

## 0.1 What this redraft corrects

| finding | what changed (section) |
|---|---|
| C-1 the side collapses into the majority side | side `sign(p - p~)` and filter `abs(p - p~)`, p~ the training fold's session-weighted median of its own fitted p, pinned; the lambda grid extended upward with the top edge's meaning stated; each fold's long share reported; C1-d fails if the judged mean side is within 0.1 of +1 or -1 (95 % of offers one way); a synthetic test of the rule (`tests/test_family_b_side_rule.py`) (9, 10, 13) |
| M-1 the 37.5-point population is P-16's first half-hour | the population is moved out of the opening window: the family's own five-minute schedule from 09:05 CT, admitted per stop by D-525 (4)'s resolution rule read on the choice block only, at P-14's 12.5- and 25-point rungs and P-16's 37.5; the options considered and their costs written down; the opening window left to the operator; the prior-exposure table completed (A3's `orb_rth*`, D-281 (3)'s baseline); the MDL on sessions (2, 3, 8) |
| M-2 the wrong follow twin | C1-f against each of Stage 2's three recorded follow rules at the five-minute latency -- `lnbar1x4` (the one D-592 found persisting), `lbrk5` and `mom15` -- by Stage 2's own code; the table's rows say which latency each was read at (2, 13) |
| M-3 C2 values a lift the places do not trade | C2 priced trade by trade on the routed trades of the design's own campaign, by the place each trade is in, uses on the judged block; the stage-B ranking keeps a first-order value with records-leaf caps and says it assumes a uniform lift (11, 13) |
| M-4 the level not calibrated for persistent sides | stage B2: every judging line's test calibrated at the family's level on this population's own choice-block pairs with synthetic sides as persistent as the out-of-fold sides, a simulated critical value if it over-rejects; a rotation gate C1-r on the judged block (12, 13) |
| M-5 P-15's marks read the judged block | no Stage 2 schedule is used for the population: the family's cutoff is computed on the choice block only, kinds only, so T-3 holds by construction (3, 8, 20) |
| M-6 the confirmation undeclared | section 16, in F-02's form: C1, C1-d, C1-f, C2 and resolution on the window at the registered 0.05, its length from Q-16's power at the pick's judged bound, written in the carrying row |
| m-1 | 45 features (`or_width`, `or_pos` out, E-016 (2)); `m_rth` and `m_or` gone (no alert before 09:00); 49 columns (7, 9) |
| m-2 | one estimator (the offer mean) in the statistic and its bootstrap; the canary's critical value defined (8, 11) |
| m-3 | Kill B's laxity from lambda's choice on the same predictions stated (11) |
| m-4 | the filter's threshold from the inner folds' out-of-fold predictions; K1/K2 years named (8, 10) |
| m-5 | a negative control for alignment (labels from the previous session at the same mark) and T-14 named (8, 20) |
| m-6 | the whole-window inputs listed as disclosed pre-reads, each with what it can and cannot bias (5) |
| m-7 | stage A waits for a purpose-tagged reader and a read ledger; the gap named (5, 22) |
| m-8 | what a screen's pass is (15) |
| m-9 | the row the lead must write (fitted values inside the walk-forward) named (22) |
| m-10 | C2's uses are the judged block's; the ranking's the choice block's (11, 13) |
| n-1 .. n-7 | readings: seeds proposed now (19); the embargo's reason (9); no breakeven move now (6); day kinds' post-alert facts (5); "one tick adverse" is a cost (6); the canary reads choice-block outcomes in stage A (8); a later family on this population and these features is not judged on this judged block (15) |

## 1. Hypothesis (research protocol step 1)

**The mechanism.** Intraday direction on an index future is close to unpredictable, but not exactly: short-horizon
momentum and the session's position against levels everyone watches (the prior day's range, the overnight range, VWAP,
round numbers) move the order flow of discretionary and systematic traders, and volume against its usual time-of-day
level marks when informed flow is present. One model reading all of these together might find a small, stable direction
signal that no single rule shows. **Expected:** volatility and resolution speed are predictable (volatility clusters;
the handoff 3.3); direction hard -- Stage 2's OHLC rules against their coin twins found gains of schedule, not direction
(D-558), and a follow-the-move effect real per trade but concentrated in 2024-2026 (D-580, D-588, D-592).

**What would make it worth something.** Not its accuracy: its lift in win probability over the coin at the same
entries, times how often it is used, times what a win is worth where it is used (`vendor/stage2/results/u_value_map.csv`;
the handoff 2.7).

**Two targets** (the handoff 3.3): **resolution speed** (expected predictable) -- the pipeline's **positive control**,
and a filter read beside the scorecard; it cannot pass, because a filter that ignores the side has no lift over the coin
by construction -- and **direction** (expected hard), the only target the pass line reads.

## 2. Prior exposure (the audit's R-3; P-3, D-2)

What Stage 2 already read of this mechanism, these hours or these entries on NQ 2020-01-02 to 2026-07-16:

| row | what was read | latency | sign and span |
|---|---|---|---|
| D-555, D-557, D-558 (A4) | short-bar momentum rules against their coin-sided copies, P-16's schedule | L = 0 | a genuine but tiny per-trade direction effect; no campaign value beyond the schedule |
| D-578, D-580 (program S, S1) | 15 OHLC side rules on P-16's offers | **L = 0** (D-589 (5): S1's and S2's rules shared S3's assumption) | 15-minute momentum (`mom15`, at 3R) and the latest 5-minute breakout (`lbrk5`, at 1R and 1.5R), **followed**, survive the per-offer test; both fail the span guard (below P-16 on 2020-2023, above on 2024-2026) |
| D-581, D-582 (S2) | P-16's coin gated by volatility and trend states | L = 0 | no state improves the offers enough |
| D-586, D-588, D-589 (S3) | new event kinds, followed | **L = 0** | the 1-minute 4-bar breakout followed (`lnbar1x4`) passes all four guards, its gain concentrated in 2024-2026 |
| D-590, D-592 (S3 at the latency) | `lnbar1x4` with its side read five minutes early | **L = 5** | the candidate fails its campaign guard, but **the per-offer lift over the coin is nearly as large at L = 5 as at L = 0 at every R** -- "broad and slow"; recorded as **a lead for unread data** |
| A3 (`config/atlas_a3.yaml`; D_protocol 1.2) | the 5-, 15- and 30-minute opening-range breakouts (`orb_rth5`, `orb_rth15`, `orb_rth30`), followed and faded | as A3 walked them (not re-checked here) | read over 2020-2026, both blocks |
| D-275, D-277, D-281 (ORB1-ORB6) | the 08:30 NQ opening-range breakout | the hand-traded latency | closed for good; D-281 (3): ORB5's hand-traded stop entry, chased, held a positive funded-leg bound in both eras, and **whether any later hypothesis is genuinely different is the operator's call** |
| program U (nine families); F-01 (E-003, withdrawn E-007); F-02's draft (E-017) | contract levers; resting orders at pre-session levels | -- | no direction read in U; F-01 read nothing; F-02 reads nothing yet |

**What follows for this family.**

- **(a) The judged block is late development for direction, not out of sample** (the audit's P-3): the follow effect
  is known to be strong there. So the pass line is joined by conjunctive kill lines that the known effects cannot clear
  (section 13): a drift-matched lift, the lift over each of Stage 2's three follow rules **read at the five-minute
  latency this family trades at**, and a rotation gate.
- **(b) A new question, not a re-run:** no Stage 2 work fitted a model jointly on normalised features, and a pass must
  beat every recorded follow rule on the same offers.
- **(c) The opening window and D-281 (3).** The first version's 37.5-point population was P-16's six regular-session
  marks, entries 08:35-09:00 -- inside the 08:30-09:00 window of Stage 2's closed branch, with sides read from the
  session's first minutes (the review's M-1). **This version trades no entry before 09:05 CT, uses no opening-range
  feature, and enters on a fixed schedule that no range triggers** (section 3). This draft's reading: that is outside
  the closed specification. Two questions stay **the operator's**: whether the opening window may ever be traded by a
  family like this one (D-281 (3)); and, if the lead or the red team holds that a model reading the session's range so
  far is still inside the branch, whether this population may be (section 22).

## 3. The population: where the family trades (M-1, M-5)

**What was looked for:** a set of offers inside US regular hours, outside the 08:30-09:00 window, whose brackets
resolve (D-212: at most 5 % to the flatten at every R the table offers), fixed without reading the judged block.

| option | what it gives | why taken or not |
|---|---|---|
| P-16's 37.5-point schedule inside regular hours | entries 08:35-09:00 only (`rc_width_screen.csv` section `marks`, `stop_ticks` 150: no later regular-session mark is offered, because R = 3 does not resolve) | **not taken:** inside the closed opening window (D-281 (3), the operator's); kept out by default (D_protocol 1.2 (3)) |
| Stage 2's 50-point schedule | no regular-session mark offered (`rc_width_screen.csv`, `stop_ticks` 200) | not taken: empty |
| P-15's 25-point schedule | not vendored; `mark_resolution` computes it over the whole window | not taken: it reads the judged block (M-5) |
| P-14's breakout offers | direction already chosen by a breakout followed (the follow effect built in); its 30-minute bars at the open overlap A3's `orb_rth30` | not taken: no clean test of a side |
| **the family's own five-minute schedule from 09:05** | every five-minute entry mark 09:05..15:05 CT admitted per stop by D-525 (4)'s rule **on the choice block only** | **taken** |

**The schedule, fixed now.**

- **Alerts** t in 09:00, 09:05, ..., 15:00 CT (`extended.features.ALERT_MARKS` from 09:00; at most 73 a session);
  **entry marks** m = t + 5 in 09:05..15:05.
- **Stops:** 12.5, 25 and 37.5 points (50, 100, 150 ticks) -- P-14's two rungs (R\* = P-14 trades both) and P-16's.
- **The cutoff, per stop** (D-525 (4)'s rule, Stage 2's `resolved_coin.mark_resolution` applied to this family's own
  walks, **kinds only, both sides pooled, sessions 2020-01-02 to 2023-12-29 only**): an entry mark is admitted if its
  unresolved share is at most 5 % at **every R the table offers** (0.25, 1, 1.5, 2, 2.5, 3 -- so the table's 3R ask
  resolves on every offer the design can make). The admitted marks per stop are written to the result file's `supply`
  section before any direction outcome is read, with the offers per session and the expected count per block (the
  judged block's from its session count in the store's manifest `day_list`, no bar read).
- **Sessions:** Stage 2's day kinds `n` or `b` (not FOMC, not an early close, not empty; `atlas_local.close_day`),
  after the store's first `extended.features.HISTORY_DAYS` (22) sessions -- about 1,000 sessions in the choice block
  and about 630 in the judged block.

**What it costs, said in advance.**

- **The 37.5-point stop will probably contribute nothing.** Stage 2's whole-window read (disclosed, section 5) found no
  regular-session mark after 09:00 resolving at R = 3 at 150 ticks. If the choice block agrees, its six cells are
  killed at K1 (counted). The family is then a 12.5- and 25-point family, valued on P-14's base.
- **It is no registered coin's schedule.** Supply comes from a declared schedule (the handoff 3.4's principle) but not
  P-16's marks, so the scorecard compares the design with the same schedule's coin (design (ii), section 14), not with
  a registered row; R\* = P-14 stays the row to beat beside.
- **The 12.5-point stop:** costs are a larger share of the risk, and Stage 2's 12.5-point US-hours coin cell was killed
  by its campaign line (D-527 (3)). The pass line is cost-free (both sides of a pair pay the same), so the stop is
  admitted, as F-02 admits it (its section 6.3), but its scorecard starts from a weak base.
- **Per-R populations are not used.** At 37.5 points R = 1 and 1.5 resolve later into the morning than R = 3 (the same
  pre-read), but the table asks 3R at the funded opening, and an offer whose 3R trade does not resolve breaks D-212 for
  the design.
- **Resolution near the line.** The cutoff is read over the whole choice block, and K2 also binds each year: a mark
  admitted on the block can still fail a year (expected at the cutoff's edge; the cell is then killed, not re-cut).

## 4. Contract fit (step 2) -- the constraints the family lives inside (CHARTER section 4)

| constraint | how the family meets it |
|---|---|
| latency, at least 5 minutes, hand entry (D-266; E-008) | the side at alert t from bars stamped <= t - 1 min only; a market order placed by hand at t + 5, booked at the open of the first bar opening at or after t + 5, its tick charged as a cost (`extended/walker.py` `MARKET`); no automated or API entry |
| one position per firm, 5 minutes flat (D-429) | the pass line reads every offer (the coin twin's form); the scorecard routes by Stage 2's strict rule |
| resolution (D-212, D-308; D-8) | the cutoff (section 3) and K2, at most 5 % overall and in every year |
| realised risk (D-308) | K3, reported (a market entry's stop exit slips adversely: it cannot fail, D-9) |
| stop band and cost floor (`stop_band.csv`) | 50, 100 and 150 ticks, all above the 45-tick floor |
| news (D-525, D-533; E-007 (d)) | entries from 09:05 CT, after every BLS 08:30 ET release; FOMC days excluded |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (no tight brackets, durations minutes to hours); no maximum size into major news; no copying across accounts (D-157); nothing concealed |
| tier 2 (D-289) | as P-14's table: off in the base case, on beside |
| tier 3 (E-013 (1)) | 0 % denial in the verdict; 10/25/50 % beside |
| firm rules | none loaded by the family; the scorecard runs Stage 2's engine on its verified ledger |

## 5. Data, blocks, the seal and the disclosed pre-reads

- **Data:** Stage 2's NQ 1-minute bars (licensed, uncommitted, `vendor/DATA_MANIFEST_stage2.sha256`), development window
  **2020-01-02 to 2026-07-16** only. Stage 2's walks (`data/atlas`) are not read; labels come from this repository's
  walker (E-011).
- **The choice block:** sessions **2020-01-02 to 2023-12-29** (the cutoff, the fits, the search, every choice). **The
  judged block:** sessions **2024-01-02 to 2026-07-16** (one read of the frozen pick).
- **The seal (R-4, R-5; m-7).** Today the seal would rest on T-3 alone: **no purpose-tagged bar reader, read ledger or
  H-2 hook exists** in `extended/` or `scripts/`. This family **depends on them before stage A**: its runner reads bars
  only through a reader that refuses judged-block dates to the purposes `choose` and `fit` and appends every read to a
  committed ledger; T-3 (section 20) is the second proof.
- **Disclosed pre-reads (m-6):** inputs fitted or read over 2020-2026 that T-3 cannot see, each with what it can bias.

  | input | what it is | can bias | cannot bias |
  |---|---|---|---|
  | `stop_band.csv` | the cost floor and stop band | which stops are allowed (all three are registered rungs) | any side or lift |
  | `u_value_map.csv` | D-667's solved tables from the registered edge rows | the stage-B ranking and C2's dollars per place (`mean_dv`) | the lift or its bound |
  | `rc_width_screen.csv` section `marks` (150 and 200 ticks) | Stage 2's per-mark resolution over 2020-2026 | the stated expectation that 37.5 points adds nothing (section 3) | the population (the family's cutoff is its own, on the choice block) |
  | Stage 2's S1/S3/A4/A3 reads | direction readings on these bars | the design of the kill lines (they are why C1-f exists) | the pick (fixed by stage B on the choice block) |

- **Day kinds use post-alert facts (n-4):** an early close is known from the day's own last bar, and Stage 2's FOMC set
  holds the unscheduled statement of 2020-03-03 (10:00 ET, after that day's first alerts). Both drop whole days, both
  sides alike; the population follows Stage 2's day kinds for comparability.

## 6. The offers, the brackets, the walk and the labels

- **Entry:** booked at the open of the first bar opening at or after t + 5; one tick charged as a cost, not in the price
  (n-5). Both sides of every offer enter at the same price, so there is no fill-bar asymmetry (the audit's D-1 needs a
  resting entry) and the mirror is a realisable market order.
- **Brackets:** stops 50, 100, 150 ticks; targets at R in {1, 1.5, 3} (the table's three asks), floor(R x S) ticks
  (Stage 2's `target_ticks`).
- **The walk: fixed barriers** -- `extended.walker.Rules("stage2_fixed", FLAT_ENTRY, "worst_less_two",
  breakeven=False)`: Stage 2's walk end (the bar ending 15:08 CT) and flatten (the worst of the bars ending 15:08-15:10
  less two ticks), stop on a touch, target on a trade through, stop first on a two-barrier bar, **no breakeven move**;
  Stage 2's costs at each stop (`atlas_a3.fee_by_stop`, `config/fills.yaml`). Why: the population is no longer P-16's
  trades, so the move (allowed as made, E-013 (2)) is not needed for an identity; direction is measured cleanly at fixed
  barriers (feature-rules 3; as F-02 does); and the move's two modelling defects are open (Q-20). The move is read
  beside (n-3's point is then moot).
- **The pair at each offer and bracket:** the long's and the short's kind, gross and net R, and the pair value
  `d = (win_long - win_short) / 2` in win probability (`win` = a target exit), net R beside. A side rule with sides
  `s_i` in {+1, -1} has **lift over the coin twin** `mean(s_i d_i)` (the coin's expectation at the same entries without
  its noise).
- **The direction target** (per stop, fitted at R = 1 only, where the two sides' barriers are symmetric): `y = 1` if
  the long's net R at R = 1 exceeds the short's, `y = 0` if below, left out of the fit if equal.
- **The resolution target** (per stop): `T` = minutes from the entry bar's open to the first bar touching entry +- S
  (side-free), the walk's end when none; `y_res = 1` if `T` is at most the training fold's median of `T`.

## 7. The features and their preparation

**The library:** `extended/features.py`, pinned by its sha256 at the pinning commit. **Family B uses 45 of its 47
features** -- all but the two opening-range ones, kept in the library and out of this family until the operator rules
(E-016 (2); E-007 (b); D-281 (3)). Every feature at t reads only bars stamped <= t - 1 minute and earlier sessions'
bars; every normaliser is from the past only; cross-day features are NaN on a roll day; calendars only as known in
advance (the proof: `tests/test_features.py`, `tests/test_features_lookahead.py`, the red team's "what I tried that found
nothing"). The registry, as `extended.features.describe()` prints it -- **the 45 this family uses:**

| feature | group | formula | window | normaliser | reads | from | cross-day | warm-up | per |
|---|---|---|---|---|---|---|---|---|---|
| `ret_5` | return | (c - close of the last bar stamped <= t-1-5min) / atr14 | 5 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_15` | return | (c - close of the last bar stamped <= t-1-15min) / atr14 | 15 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_30` | return | (c - close of the last bar stamped <= t-1-30min) / atr14 | 30 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_60` | return | (c - close of the last bar stamped <= t-1-60min) / atr14 | 60 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_120` | return | (c - close of the last bar stamped <= t-1-120min) / atr14 | 120 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_rth` | return | (c - open of the first bar stamped >= 08:30) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `ret_day` | return | (c - open of the trading day's first bar) / atr14 | 17:00 to t | atr14 | the day's bars stamped <= t-1min | 08:30 | no | 14 | alert |
| `rng_15` | range | (max high - min low of the bars stamped t-15..t-1) / atr14 | 15 min | atr14 | the day's bars stamped t-15..t-1min | 08:30 | no | 14 | alert |
| `rng_60` | range | (max high - min low of the bars stamped t-60..t-1) / atr14 | 60 min | atr14 | the day's bars stamped t-60..t-1min | 08:30 | no | 14 | alert |
| `range_day` | range | (day high - day low so far) / atr14 | 17:00 to t | atr14 | the day's bars stamped <= t-1min | 08:30 | no | 14 | alert |
| `range_rth` | range | (regular-session high - low so far) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `pos_day` | position | (c - day low) / (day high - day low), so far | 17:00 to t | the day's own range | the day's bars stamped <= t-1min | 08:30 | no | 0 | alert |
| `pos_rth` | position | (c - RTH low) / (RTH high - RTH low), so far | 08:30 to t | the session's own range | the day's bars stamped 08:30..t-1min | 08:35 | no | 0 | alert |
| `pos_prior` | position | (c - prior RTH low) / (prior RTH high - prior RTH low) | the prior regular session | the prior session's range | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 1 | alert |
| `d_pdh` | level | (c - prior RTH high) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 14 | alert |
| `d_pdl` | level | (c - prior RTH low) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 14 | alert |
| `d_pdc` | level | (c - prior RTH close: the last close stamped <= 14:59) / atr14 | the prior regular session | atr14 | the prior day's bars stamped <= 14:59; c | 08:30 | yes | 14 | alert |
| `d_onh` | level | (c - overnight high) / atr14; overnight = bars stamped 17:00..08:29, frozen at 08:30 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29; c | 08:30 | no | 14 | alert |
| `d_onl` | level | (c - overnight low) / atr14 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29; c | 08:30 | no | 14 | alert |
| `range_on` | level | (overnight high - overnight low) / atr14 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29 | 08:30 | no | 14 | day |
| `gap` | level | (the last close stamped <= 08:29 - prior RTH close) / atr14 | prior 14:59 to 08:30 | atr14 | the prior day's bars stamped <= 14:59; the day's bars stamped <= 08:29 | 08:30 | yes | 14 | day |
| `d_vwap` | level | (c - RTH VWAP so far: sum((h+l+c)/3 x volume) / sum(volume)) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `d_round` | level | (c - the nearest multiple of 100 index points) / atr14 | the last bar | atr14 | the last bar stamped <= t-1min | 08:30 | no | 14 | alert |
| `vol_5` | volume | log((V5 + 1) / (median V5 + 1)), V5 = volume of the bars stamped t-5..t-1 | 5 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-5..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `vol_30` | volume | log((V30 + 1) / (median V30 + 1)) | 30 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-30..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `vol_day` | volume | log((Vday + 1) / (median Vday + 1)), Vday = the day's volume stamped <= t-1 | 17:00 to t | its median at the same CT slot over the 20 prior trading days | the day's bars stamped <= t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `vol_accel` | volume | log((V5 / 5 + 1) / (V60 / 60 + 1)) | 5 vs 60 min | the trailing hour's own rate | the day's bars stamped t-60..t-1min | 08:30 | no | 0 | alert |
| `rv_ratio` | volatility | rv_15 / rv_60 | 15 vs 60 min | the trailing hour's own rv | the day's bars stamped t-61..t-1min | 08:30 | no | 0 | alert |
| `rv_tod` | volatility | log(rv_60 / median rv_60) | 60 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-61..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `rv_atr` | volatility | rv_60 / atr14 | 60 min | atr14 | the day's bars stamped t-61..t-1min | 08:30 | no | 14 | alert |
| `atr_ratio` | volatility | atr5 / atr14 | 5 vs 14 days | atr14 | the 14 prior trading days | 08:30 | no | 14 | day |
| `range_prior` | volatility | (prior RTH high - prior RTH low) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59 | 08:30 | no | 14 | day |
| `atr_rel` | volatility | atr14 / c x 10,000 (basis points of the price) | 14 days | the price level | the 14 prior trading days; c | 08:30 | no | 14 | alert |
| `ret_prior` | trend | (prior RTH close - prior RTH open) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59 | 08:30 | no | 14 | day |
| `ret_5d` | trend | sum of the 5 prior days' changes (C_d - C_{d-1}; C_d - O_d on a roll day) / atr14 | 5 days | atr14 | the 6 prior trading days' first and last bars | 08:30 | no | 14 | day |
| `ret_20d` | trend | sum of the 20 prior days' changes, chained within the contract / atr14 | 20 days | atr14 | the 21 prior trading days' first and last bars | 08:30 | no | 20 | day |
| `ext_ma60` | trend | (c - mean close of the bars stamped t-60..t-1) / atr14 | 60 min | atr14 | the day's bars stamped t-60..t-1min | 08:30 | no | 14 | alert |
| `up_share_30` | trend | share of rising 1-minute close changes among those of the bars stamped t-30..t-1 | 30 min | a share | the day's bars stamped t-31..t-1min | 08:30 | no | 0 | alert |
| `eff_30` | trend | \|c - close as of t-31\| / sum \|1-minute close changes\| over t-30..t-1 | 30 min | the path's own length | the day's bars stamped t-31..t-1min | 08:30 | no | 0 | alert |
| `tod` | calendar | (t - 08:30 CT) in hours | -- | -- | none (the alert's CT time) | 08:30 | no | 0 | alert |
| `dow` | calendar | the trading day's weekday, 0 Monday .. 4 Friday | -- | -- | none (the date) | 08:30 | no | 0 | day |
| `bls_day` | calendar | 1 if the trading day has a BLS 08:30 ET release, else 0 | -- | -- | the BLS schedule (published the year before) | 08:30 | no | 0 | day |
| `bls_major` | calendar | 1 if it releases the Employment Situation or the CPI, else 0 | -- | -- | the BLS schedule | 08:30 | no | 0 | day |
| `days_to_fomc` | calendar | calendar days to the next scheduled FOMC statement day (0 on one), capped 30 | -- | -- | the FOMC schedule as known on the day | 08:30 | no | 0 | day |
| `days_since_fomc` | calendar | calendar days since the last FOMC statement before the day, capped 30 | -- | -- | the FOMC statements already made | 08:30 | no | 0 | day |

**In the library, not in this family** (E-016 (2)):

| feature | group | formula | window | normaliser | reads | from | cross-day | warm-up | per |
|---|---|---|---|---|---|---|---|---|---|
| `or_width` | opening range | (OR high - OR low) / atr14, OR = the bars stamped 08:30..08:59 | 08:30 to 09:00 | atr14 | the day's bars stamped 08:30..08:59 | 09:00 | no | 14 | day |
| `or_pos` | opening range | (c - OR low) / (OR high - OR low) | 08:30 to 09:00 | the OR's own range | the day's bars stamped 08:30..08:59; c | 09:00 | no | 0 | alert |

(`c` = the close of the last bar stamped <= t - 1 min; `atr14` = the mean daily true range of the 14 prior sessions, the
prior close used only within one contract. Two are level-dependent by design: `d_round`, `atr_rel`. At alerts from
09:00 every regular-session feature exists: `available_from` is 08:35 for the latest of them.)

**Preparation, every statistic fitted inside the training fold only and applied out of fold** (feature-rules 4):
(1) each real feature winsorised at the training fold's 0.5 % and 99.5 % quantiles; (2) standardised by the training
fold's mean and standard deviation; (3) `dow` as four indicators (Tuesday-Friday, Monday the reference); the binary
flags as they are; (4) **one** missing indicator, `m_cross` (a roll day: the five cross-day features missing), and
every remaining missing value set to 0 after standardisation (the training mean). The first version's `m_rth` and
`m_or` are gone: no alert precedes 09:00 (m-1). **The design matrix: 49 columns** (45 features, `dow` replaced by four
indicators, plus `m_cross`) **and an unpenalised intercept.** No feature is selected, transformed or dropped by data. A
column with zero variance in a training fold (none is expected) stops the fit (the failure protocol), never silently
dropped.

## 8. Stage A: the gates, before any lift is read (choice block)

1. **The dependencies hold** (refusing): the purpose-tagged reader and read ledger (section 5); the identities
   (section 20).
2. **The cutoff and K1 supply.** The admitted marks per stop (section 3). K1: at least 12 offers a year in every
   calendar year 2020-2023 for a `side` cell; for a `filter` cell, counted after its out-of-fold filter in 2021, 2022
   and 2023 (2020 has no out-of-fold prediction; m-4). Else the cell is killed.
3. **K2 resolution.** The share flattened unresolved, both sides pooled, at every R in {1, 1.5, 3}, at most 5 % over
   2020-2023 and in each of 2020, 2021, 2022 and 2023 (a `filter` cell: on its filtered offers, 2021-2023). Else the
   cell is killed; nothing is re-cut.
4. **K3 realised risk** (D-308): reported.
5. **The positive control.** The resolution model's out-of-fold AUC on 2021-2023 at each surviving stop, its one-sided
   95 % lower bound by stage B's bootstrap (seed `default_rng([20261960, 0])`) above 0.5. Else the failure protocol
   (terminal states, stage decomposition, the component in isolation, replication) runs before stage B, and the family
   waits for the lead's ruling under a row.
6. **The alignment control (m-5).** The same pipeline with each resolution label replaced by the previous session's at
   the same mark: the aligned AUC minus this shifted AUC, its one-sided 95 % lower bound (`[20261960, 1]`), above 0.
   Volatility clusters, so the shifted AUC can exceed 0.5; only the drop shows features and labels line up. Else the
   failure protocol. The planted-effect test (T-14, section 20) is the alignment's second proof.
7. **The null canary.** The whole direction pipeline (folds, search, fit, out-of-fold sides, stage B's statistic) run
   once on the choice block with the long's and the short's outcomes swapped in every 21-session block a seeded coin
   picks (`[20261961, 0]`), so the label and `d` both flip there. Its maximum studentised lift (section 11's statistic)
   is set against the 99.9th percentile of the same maximum over 10,000 bootstrap draws of its own data
   (`[20261961, 1]`); above it, a defect signal, and the failure protocol runs. This reads choice-block direction
   outcomes inside stage A -- flipped, before any lift of the model is read; harmless, said so (n-6). It cannot see slow
   side persistence (its flips are 21 sessions long); stage B2 does that.
8. **Power on record (R-16), from counts only, on sessions** (M-1). For each surviving cell, the minimum detectable lift
   (MDL) at the family's level on the judged block from Q-16's power function **[Q-16: its name, module and commit]** at
   the judged block's session count and the cell's offers per session (offers in a session overlap, so the effective
   sample is about the sessions). Set against the value bar (`u_value_map.csv` section `bar`: the extra win probability
   for $500 a year at the cell's uses). If the MDL exceeds the bar by more than a factor of 3 at every surviving cell,
   the family is **declared a screen** (section 15 says what its pass is).

## 9. The model, its search and the walk-forward (R-7)

- **The model:** an **L2-regularised logistic regression**, one per stop and target: minimise the session-weighted mean
  log loss `(1/D) sum_d (1/m_d) sum_{i in d} logloss_i + (lambda/2) ||beta||^2` (D training sessions, m_d labelled offers
  in session d; the intercept not penalised) by `scipy.optimize.minimize(method="L-BFGS-B")` with the analytic gradient,
  from zero, `gtol` 1e-10, at most 2,000 iterations, refusing a fit that does not converge. Deterministic, no seed.
  Implemented in this repository's package after the pin (neither scikit-learn nor LightGBM is installed; the logistic
  needs neither) and held by its tests (section 20).
- **Searched: lambda**, over **seven values `0.25 x 10^(j/2)`, j = -2..4** (0.025 to 25; with standardised features
  near p~ the coefficients shrink by about `0.25 / (0.25 + lambda)`), per stop and target, inside the choice block only:
  - **inner walk-forward:** test years 2021, 2022, 2023, each trained on the choice block's population sessions before
    it, less its last 22 sessions. (A forward walk needs no embargo: no training label resolves in a test session, and
    a test feature reading training sessions is not leakage (n-2). The 22 sessions are kept from the first version only
    because they are harmless.)
  - **criterion:** the session-weighted out-of-fold log loss summed over the three test years; the smallest wins, a tie
    (within 1e-9) to the larger lambda;
  - **the top edge (C-1):** the grid now reaches heavy shrinkage. Under a null or a weak signal the criterion is
    expected to choose the top edge. With the centred side (section 10) a pick at the top edge is still a
    feature-driven side -- as lambda grows the coefficients' direction tends to each feature's covariance with the label
    -- so the family still puts its question to the data. A pick at the top edge is reported as such in stage B, and the
    grid is not extended after any read.
  - every configuration (lambda x stop x target) and its criterion written to the result file and **counted**.
- **The out-of-fold predictions for stage B:** at each stop's chosen lambda, the three inner folds' predictions on
  2021-2023, **each fold's model with its own p~ and threshold** (section 10).
- **The final model:** refitted at the chosen lambda on all the choice block's population sessions; its coefficients,
  the in-fold winsorising, standardising and imputing constants, **its p~** and **the filter threshold**, and the
  resolution model's training median, serialised to canonical JSON and **hashed; the hash pinned in a decision row
  before the judged read** (R-7; T-7). No early stopping, no refits with other seeds, no feature subset, no class weights.
- **The resolution model** (the control): the same pipeline on `y_res`, its own lambda by the same search.

## 10. How a prediction becomes a trade (C-1), and the cells

`p` is the direction model's probability that the long beats the short. **`p~` is the training fold's session-weighted
median of the model's own fitted p** (each training session weighing the same), pinned with the model. **The side is
long if p > p~ and short if p < p~**, a seeded coin if exactly equal (`[20261963, 0]`). Centring on the training median
cannot collapse into the majority side: an intercept that only fits the training block's base rate moves p and p~
together (`tests/test_family_b_side_rule.py`: on a null signal at base rates 0.53 and 0.51 the centred sides are
balanced at every lambda of the grid, while `sign(p - 0.5)` goes long on almost every offer at the top of the grid; a
weak planted signal is recovered with balanced sides). Two uses:

- `side` -- every offer of the stop's population takes the model's side;
- `filter` -- only offers with `abs(p - p~)` at or above **the 80th percentile of the inner folds' out-of-fold
  `abs(p - p~)`** on 2021-2023 (pooled; each fold with its own p~) are offered, at the model's side; the threshold
  pinned with the model (m-4: out-of-fold, so about a fifth pass out of fold).

**The cells: k_cells = 3 stops x 3 R x 2 uses = 18.** Within a stop and a use the trades and sides are the same at
every R; R decides the bracket the lift is read at and the places that price it.

## 11. Stage B: choose on the choice block (2021-2023, out of fold)

- **The statistic (m-2), one estimator:** for each cell surviving stage A, `L_c` = the **mean over the cell's offers**
  of `s_i d_i`. Its bootstrap: circular moving blocks of 21 sessions, 2,000 draws (`[20261962, 0]`), each draw
  recomputing the same offer mean over the resampled sessions' offers; `SE_c` its standard deviation over draws; the
  family-wise critical value `q` = the 95th percentile over draws of `max_c (L*_c - L_c) / SE_c` (one-sided 0.05).
  Benjamini-Hochberg at 10 % beside, never selecting.
- **Kill B:** no cell with `L_c / SE_c > q` -- the family closes; the judged block is not read. *Said so (m-3):* lambda
  was chosen on the same 2021-2023 out-of-fold years, outside the maximum, so Kill B is somewhat laxer than one-sided
  0.05. The judged level is unaffected: the judged block decides.
- **Reported for every cell, before the pick:** each fold's long share and the run lengths of the out-of-fold sides
  (stage B2's input; sides only, no outcome).
- **The pick:** among the cells above `q`, the one with the largest **first-order valued lift** at its lower limit
  `L_c - q SE_c`, **a ranking that assumes a uniform lift over the cell's offers** (the money is decided by C2 on routed
  trades, section 13; M-3): `$ a year = lambda_pts x min(u, cap(p, R)) x mean_dv(p) / 100`, maximised over the places
  that ask the cell's R -- (b) the evaluation (any R), (c) the funded opening (R = 3 only), (d) funded later (R = 1 and
  1.5), (e) paid (any R) -- with `lambda_pts` the lower limit in percentage points, **u the cell's offers a year on the
  choice block** (m-10), `mean_dv(p)` and `trades_per_year_forward(p)` from `u_value_map.csv` section `place_values`,
  and `cap(p, R) = trades_per_year_forward(p) x sigma(p, R)`, sigma the share of the place's phase's recorded trading
  leaf-days whose leaf R is the cell's R (section `records_leaf`; F-02's rule, its section 10). **Base `p14` for 50 and
  100 ticks** (P-14's rungs), `p16` for 150 ticks.

## 12. Stage B2: the level calibrated for this family (M-4), before any judged read

- **What it checks:** that each judging line's test (C1, C1-d and the three C1-f, section 13) delivers the family's
  level 0.05 / (k (k + 1)) **on this population's dependence with sides as persistent as the model's** -- the classic
  spurious-regression case the review's Appendix B shows a 21-session test missing.
- **The null data:** the choice block's own pair values `d` at the pick's bracket (side-free values, the block's drift
  their mean -- read here for their dependence only, disclosed like the canary) multiplied by **synthetic weight
  processes independent of `d`** with the values and persistence of each line's weights: C1 `s*`; C1-d `s* - mean(s*)`;
  C1-f `s* - f*`, where `s*` alternates sign with run lengths resampled from the pick's out-of-fold sides on 2021-2023
  (random start) and `f*` likewise from the twin's own sides; for a `filter` pick the selection pattern resampled the
  same way. Draws `default_rng([20261965, j])`, at least **1,000,000 replications per line** (enough that the Monte Carlo
  interval tells the level from 1.5 times it).
- **The rule:** a line's test **holds** if the upper 95 % Monte Carlo limit of its rejection rate at the family's level
  is at most 1.5 times the level (T-6's tolerance). If a line's test does not hold, that line is read in stage C with
  **its simulated critical value** (the null statistic's (1 - level) quantile from these replications) instead of the
  test's own. Fixed now, never after a read.
- **What it cannot see:** a judged block whose dependence differs from the choice block's. That is the rotation gate's
  job (C1-r).
- Cost: light in memory; CPU minutes to hours.

## 13. Stage C: judge the pick once, on the judged block (2024-01-02 to 2026-07-16)

The pinned model (its hash in the judge's manifest; the judge entry point cannot fit, T-7), the pick's population (its
stop's admitted marks), its bracket and use. Per offer `i`: `d_i`, the model's side `s_i`, and the **follow twins'**
sides `f_i^r` for the three rules Stage 2 recorded, each **read at the alert t, i.e. at the five-minute latency** this
family trades at, by Stage 2's own code imported unchanged (a zero is a tie, `f = 0`):

| twin | Stage 2's rule | read by | recorded at |
|---|---|---|---|
| `lnbar1x4` | the side of the most recent 1-minute 4-bar `nbar` event, followed | `s3_latency.lagged_day_sides` (L = 5) | S3 at L = 0 (D-588); **its lift persisted at L = 5** (D-592) |
| `lbrk5` | the side of the most recent 5-minute `brk` event, followed | `s1_sided_coin.day_sides` at the alert | S1 at L = 0 (D-580) |
| `mom15` | `sign(c[t] - c[t-15])`, followed | `s1_sided_coin.day_sides` at the alert (= `sign(ret_15)`) | S1 at L = 0 (D-580) |

**The design passes only if every line holds. A fail of any closes the family**, its reason in a decision row.

- **C1 -- the pass line (CHARTER section 3, E-008):** `mean(s_i d_i)`, its one-sided lower bound at **0.05 / (k (k +
  1))** by **Q-16's calibrated lift test [Q-16: its name, module and commit]** (or its simulated critical value, stage
  B2), above zero. This file is not pinned until Q-16 is merged.
- **C1-d -- drift-matched (D-12):** the same on `(s_i - s_bar) d_i`, `s_bar` the pick's mean side on the judged block,
  above zero at the same level. **If `abs(s_bar)` is at least 0.9, C1-d fails** (a side that is almost always one way is
  a drift bet, and the statistic degenerates; C-1).
- **C1-f -- beyond each known follow effect (M-2):** for each twin r, the same on `(s_i - f_i^r) d_i`, above zero at the
  same level: three lines. An intersection-union test, so the level holds and only power is spent.
- **C1-r -- the rotation gate (M-4):** the pinned side series (with the filter's selection), indexed by session and
  mark, circularly shifted against `d` by every shift of 63 to T - 63 sessions (T the judged block's sessions; a shifted
  offer missing from a session is dropped); the observed `mean(s d)`'s rank p-value `(1 + #{shifts at or above it}) /
  (1 + #shifts)` at most **0.01** -- a conjunctive gate at the level its few hundred shifts can resolve, never the claim.
- **C2 -- worth something, where it is used (M-3, m-10):** the gate campaign of design (i) (section 14) on the judged
  block's sessions (500 paths, the bound arm as Stage 2's U2 records, seed 20261966) records, for every simulated trade
  j, the offer it took `i(j)`, the R the table took `R_j`, and its place `p(j)` -- (b) evaluation, (c) the funded
  account's first trade, (d) funded later before the first payout, (e) paid. Per judged session s,
  `z_s = sum over trades j on session s of mean_dv(p(j)) x s_i(j) x d_i(j)(R_j) / (paths x years per path)`; the valued
  lift is `V = sum_s z_s` dollars a year (**uses: the design's own routed trades on the judged block**). **C2: V's
  one-sided 95 % lower bound -- the session count times the lower bound of mean(z_s) by Q-16's statistic, the routing
  weights held fixed -- at least $500 a year.**
- **The floors** (CHARTER section 3): every offered R resolving on the judged block (K2's lines, in 2024, 2025 and
  2026 to 07-16; a calendar year with fewer than 63 sessions pooled with its neighbour, D-604); the long-run gate --
  growth on the required bankroll at the bound above zero (Stage 2 D-145) -- from the same campaign of design (i);
  every firm rule verified (Stage 2's ledger); conduct tier 1.

**Beside, deciding nothing:** the lifts in net R; the lift by calendar year (P-3 (5)); the lift on each session's first
offer (the funded opening's usual trade) and C2's place-by-place parts; the reverse walk-forward (the same pipeline and
lambda fitted on the judged block, read on 2021-2023, its bootstrap `[20261962, 1]`); the seeded coin twin
(`[20261964, 0]`); a model fitted on the three twins' sides alone, and the lift over it (the review's optional fourth
line, beside to keep power); the lifts with Stage 2's breakeven move and with Q-20's corrected move; the resolution
model's judged AUC; the denial ladder and the placement on in the scorecard.

## 14. The journey scorecard -- beside every judgement, never the pass line (CHARTER section 2; E-008, E-014, E-015)

**The design** (the pick's only; a family closed at Kill B runs none): Stage 2's RC runner (`rc_dev_test`: P-14's design
-- the no-closure state table, the strict router, five seats, the purchase budget, the fees, the R of every trade set by
the table) with this family's offers at the pick's stop as its cell, **(i) at the model's sides** (a `filter` pick: only
the filtered offers) and **(ii) the same offers at the coin's sides** (Stage 2's coin, seed 20261102 per date and mark,
D-521) -- the comparison within one trade stream that isolates the side. Its gate campaign: seed 20261966, 500 paths,
the verdict arm (every R's outcome at the one-sided 95 % bound of its edge), payout denial 0 %, the placement off.
Journeys by the vendored U1 replay and Q-17's adapter. **Identity first, refusing:** the runner with P-15's own cell
reproduces P-15's registered rows and U1 start rows (Q-22).

**Read against R\* = P-14 and against design (ii):**

- **P** and the guarded measures S1, S3a, S3b, S3c (with its components), S4a, S4b, S5a, S5b, S5c; the reported-only S2,
  S3d, S6, Q (`vendor/stage2/docs/USER_MILESTONES.md`);
- **the journey variables (E-014):** sessions and cash to the first pass; sessions and cash to the first payout;
  **sessions to break-even** (the first session whose cumulative net cash is at or above zero, daily), the share of
  starts reaching it by months 1, 2, 3, 6 and 12, and the share that later fall back below zero; **the path's
  evenness** -- the share of months with a positive net change, the longest run of months without a payout, the spread
  of monthly net, the deepest fall of cumulative net from its running high after break-even, payouts per month, and the
  largest single month's share of the year's payouts;
- **every measure as a distribution over start days** (median, p10, p90), on all starts and on the judged block's
  starts, with its uncertainty from the effective number of independent starts and the start day's share of the
  variance (`user_drivers.csv` section `design_vs_luck`);
- **the frontier** on P, S1, S3a and S5a (`user_drivers.csv` section `frontier`'s form);
- **the menu: E-015's limits, once approved by the operator**, as **flags only** -- a design crossing one is shown with
  which limit and by how much; **a limit never fails a design** (E-015 (3));
- **the evenness trade-off curve** beside (E-015 (4));
- **E-007 (e)'s readings:** the denial ladder (10/25/50 %; E-013 (1)), the placement on, the binding Focused Trader
  models, P by month, mean net, CVaR10, P under a bankroll limit, the effective sample size and the minimum detectable
  difference before the read;
- Stage 2 D-621 (3)'s rule against P-14, beside as E-008 keeps it, deciding nothing;
- **not modelled, said wherever the scorecard appears:** a user who stops when their own money runs out, the user's
  time, taxes.

The resolution model as a filter (offers predicted fast, at the coin's side) is a second design read beside -- a supply
and speed reading for the journey, never a pass.

## 15. What a pass and a fail mean (m-8, n-7)

- **CARRIED** (every line of stage C and the floors): a development finding on a late-development block. It takes a
  registration id, a model card (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`), its registered development test through
  the gatekeeper, the auditor, and **one confirmation** (section 16), which carries the decision (D-189). **If the family
  was declared a screen (section 8 item 8), a pass is still CARRIED**, and the carrying row says that the development
  read was a screen at its MDL ratio: the confirmation alone is evidence of an edge.
- **CLOSED** at stage A (no cell survives), B (Kill B) or C (any line or floor): the reason in a decision row. A close at
  B or C reads **"no lift above the MDL at this family's level"**, never "no lift"; where a check (not a kill line)
  failed, the failure protocol.
- **The closure binds** (D-277's boundary; the audit 1.5 (c), R-8): a later family on these features or this population
  (the dropped tree among them) names this closure, says what changed and why it is a different hypothesis, and **is
  not judged on this family's judged block** -- it goes to data this family did not read.

## 16. The confirmation, declared before any development read (M-6; F-02's form)

- **The window:** NQ from **2026-07-17** (`config/windows.yaml`, `reserve`), not on disk, never read until a carried
  candidate is registered; **a purchase, the operator's**. It would be NQ's **fourth** confirmation window, **the
  operator's decision** (D-107: NQ's three were spent by P-05, P-06, P-10; D-461). Stage 2's draft P-16 confirmation and
  F-02's draft target the same window; if any test reads it first, the lead records it before registration and the
  operator decides whether it can still confirm this pick.
- **What it tests -- the pick's trades, not P** (every rule, the pinned model, the stop's admitted marks as fixed):
  C1, C1-d (with its 0.9 rule) and the three C1-f on the window's offers, each **one-sided at the registered 0.05** by
  Q-16's statistic (with stage B2's simulated critical value where B2 required it, re-simulated at the window's length,
  draws `[20261965, 10 + j]`), the bound at 0.05/N beside (D-189's form); C2 at the 95 % bound -- the window too short for
  its own campaign, so valued with stage C's per-place shares and uses -- at least $500 a year; resolution at most 5 % on
  the window, overall and in every calendar year with at least 63 sessions (a stub year pooled, D-604). The rotation gate
  is reported if the window holds at least 224 sessions (99 shifts of 63 to T - 63), else not computed. Draws of Q-16's statistic, if
  any, `[20261967, 1]`.
- **What it cannot test: P.** Six months is about 126 sessions, about 63 starts with a month-3 horizon left -- no
  interval on P exists there (the red team's M1). The scorecard on the window is descriptive, without an interval, never
  a line.
- **How much data:** at least six months (D-604), and at least the months at which the pick's expected offers -- the
  lower of its two blocks' offers per session x 21 a month -- reach the session count at which Q-16's statistic,
  one-sided at 0.05, has 80 % power for a lift equal to **the pick's judged lower bound at the family level**, computed
  when the pick is carried and **written in the carrying row**, before any confirmation data exist. If that is more than
  the operator will buy, no confirmation is registered and the pick stays a development finding.

## 17. Parameters: fixed / searched / dropped

| parameter | what it is, in a phrase | class | value | source |
|---|---|---|---|---|
| market, bars | what is traded and read | fixed | NQ 1-minute bars (Databento, raw, one contract a day); MNQ micros sized by the table | E-002; handoff 2.2 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md; `config/windows.yaml` |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | feature-rules 4; CHARTER 3 |
| alerts | when a side is computed | fixed | 09:00 .. 15:00 CT every 5 min | section 3 (out of the opening window) |
| entry marks | when an order is placed | fixed | t + 5 = 09:05 .. 15:05 CT | D-266 |
| the cutoff | which entry marks are offered | fixed rule, values read on the choice block | D-525 (4) per mark, kinds only, both sides, every table R, 2020-2023 | section 3; M-5 |
| excluded days | not traded | fixed | FOMC, early closes, empty days (Stage 2's day kinds); the first 22 sessions | D-525, D-533; the library's warm-up |
| entry | how a trade starts | fixed | market at the open of the first bar at or after t + 5, one tick as a cost, by hand | D-266; E-008 |
| stops | the loss distance | fixed | 12.5, 25, 37.5 points (50, 100, 150 ticks) | P-14's rungs, P-16's; above the cost floor; F-02 6.3 |
| R | target over stop, where read | fixed | 1, 1.5, 3 | handoff 2.5; `records_leaf` |
| training R | the label's bracket | fixed | 1 | section 6 |
| the walk | how a trade ends | fixed | Stage 2's end and flatten, fixed barriers, no breakeven move | section 6; E-011 |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| features | what the model sees | fixed | 45 of `extended/features.py` (sha256 at pinning) | Q-11; E-016 (2) |
| preprocessing | scaling inside the fold | fixed | winsorise 0.5/99.5 %, standardise, `dow` indicators, `m_cross`, impute 0 | feature-rules 4 |
| model | the classifier | fixed | L2 logistic, session-weighted, L-BFGS-B, gtol 1e-10, 2,000 iterations | the brief (one of its two) |
| **lambda** | how hard the coefficients are shrunk | **searched** | 0.25 x 10^(j/2), j = -2..4; inner walk-forward 2021-2023; out-of-fold log loss | R-7; C-1 |
| side rule | prediction to side | fixed | long if p > p~, short if p < p~; p~ the training fold's session-weighted median | C-1 |
| filter | how confident to trade | fixed | abs(p - p~) at or above the inner folds' out-of-fold 80th percentile | m-4 (not searched) |
| resolution target | speed of resolution | fixed | first touch of entry +- S within the training median | handoff 3.3 |
| stage B | the family-wise screen | fixed | offer-mean lift; circular 21-session blocks, 2,000 draws, studentised, one-sided 0.05 | m-2 |
| stage B2 | the level's calibration | fixed | 1,000,000 replications a line; persistent synthetic sides; 1.5 x level tolerance; simulated critical value otherwise | M-4 |
| C1 | the pass line's test | fixed | Q-16's calibrated test at 0.05 / (k (k + 1)) | E-008 |
| C1-d | against drift | fixed | `(s - s_bar) d`; fails if abs(s_bar) >= 0.9 | D-12; C-1 |
| C1-f | against the known follow effects | fixed | `(s - f) d` for `lnbar1x4`, `lbrk5`, `mom15` at L = 5 | M-2; D-592 |
| C1-r | the rotation gate | fixed | shifts 63 .. T - 63 sessions; rank p at most 0.01 | M-4 |
| C2 | the least worth | fixed | $500 a year at the 95 % bound, on design (i)'s routed trades by place, judged-block uses | M-3; `u_value_map.csv` |
| valuation bases | where a win is priced | fixed | `p14` for 50 and 100 ticks, `p16` for 150 | `u_value_map.csv` |
| MDL factor | when the family is only a screen | fixed | 3 | R-16 |
| P-16's 37.5-point opening-window schedule | the first version's population | **dropped** | -- | inside D-281 (3)'s closed window (the operator's) |
| per-R populations | longer windows at R = 1, 1.5 | **dropped** | -- | the table's 3R ask must resolve on every offer (D-212) |
| P-15's schedule | a registered 25-point schedule | **dropped** | -- | not vendored; reads the judged block (M-5) |
| `or_width`, `or_pos` | the opening range | **dropped** | -- | E-016 (2); D-281 (3) |
| the breakeven move | Stage 2's stop move | **dropped** (beside) | -- | fixed barriers; Q-20's defects open |
| gradient-boosted tree | the brief's other model | **dropped** | -- | not installed; more freedoms; a tree is another family |
| 50-point stop | a wider stop | **dropped** | -- | no regular-session mark resolves (`rc_width_screen.csv`, 200 ticks) |
| R 0.25, 2, 2.5 | the table's other offers | **dropped** | -- | the three asks are where the value map prices; fewer cells |
| resting entries | stop or limit orders | **dropped** | -- | family A's mechanism (F-02) |
| overnight alerts | other sessions | **dropped** | -- | US hours (handoff 3.1, program U family 4) |
| interactions, feature selection, class weights, early stopping, seed refits, a filter-fraction search | other model freedoms | **dropped** | -- | each a hidden search (the audit's P-5 (a)) |
| rules read off the model (SHAP and the like) | explanations | **dropped** | -- | exploratory, their own family (bootstrap 6.3 B) |

## 18. The count, the family number and the level (R-17's words)

- **Cells:** k_cells = 3 x 3 x 2 = **18**, each counted whether killed or read (the six 37.5-point cells expected killed
  at K1, section 3).
- **Searched configurations:** lambda's 7 values x 3 stops x 2 targets = **42**, each evaluated and counted.
- **Recorded in the result file and the trial count:** 18 + 42 = **60**. Controls (the canary, the alignment control,
  stage B2's replications), the twins and the readings beside are not trials: nothing is chosen from them.
- **The family number:** k = the next free in the program (**11 if pinned next**; F-01 spent k = 10, E-007 (a); F-02's
  draft may take 11 first, and then this family's k is the gatekeeper's count), the level **0.05 / (k (k + 1))**. One
  cell reaches judgement; its lines are an intersection at one level; stage B spends nothing of the program's budget.
- **The program's honesty sentence (P-2):** the development level is a screening threshold; the decision is carried by
  one confirmation on unread data (D-189).

## 19. Seeds -- proposed 20261960-20261969, checked unique (T-12), for the lead to confirm at pinning

| seed | what it draws |
|---|---|
| 20261960 | stage A's controls: `[20261960, 0]` the positive control's bootstrap, `[20261960, 1]` the alignment control's |
| 20261961 | the null canary: `[20261961, 0]` its block swaps, `[20261961, 1]` its 10,000-draw bootstrap |
| 20261962 | stage B's bootstrap `[20261962, 0]`; the reverse walk-forward's beside `[20261962, 1]` |
| 20261963 | a tie p = p~ (the coin) |
| 20261964 | the seeded coin twin beside |
| 20261965 | stage B2's replications `[20261965, j]`; the confirmation's re-simulation `[20261965, 10 + j]` |
| 20261966 | the gate campaign of designs (i) and (ii): C2's routing, the long-run gate floor, the scorecard; 500 paths |
| 20261967 | Q-16's statistic's draws, if any: `[20261967, 0]` stage C, `[20261967, 1]` the confirmation |
| 20261968 | the build's tests: `tests/test_family_b_side_rule.py` (`[20261968, 0..2]`), T-3's synthetic judged block (`[20261968, 10]`) |
| 20261969 | the planted-effect test (T-14) |

**The check:** on 2026-11-16, `grep -rIowh --exclude-dir=.git -E "2026196[0-9]" .` over the whole working tree (the
vendored snapshot and its results included) found these seeds only in this file and its test. The neighbouring blocks
are taken: 20261910-19 (Q-16), 20261920-29 (Q-17), 20261930-39 (F-02), 20261940-49 (Q-25), 20261950-59 (Q-18).
**Inherited, used only as their owners registered them:** 20261102 (Stage 2's coin, design (ii)); 20261131 and 20261206
(the identities, E-002); 20261700 and 20261600 + i (D-621 (3), beside).

## 20. The build's identities and tests (Q-14, after the pin, before any reading)

All of the family's code is committed after its pin (T-9); fast tier unless marked.

1. **The walker:** E-011's identity holds at the build's commit; with the move off, P-16's trades that resolve before
   their first session open after entry are walked identically (the move never touched them).
2. **The features:** Q-11's tests pass at the pinned `extended/features.py`, the slow tier's 790-cut shift test
   included; the family's 45-feature list equals the registry less `or_width` and `or_pos`.
3. **The cutoff:** `mark_resolution` called on this family's own walks over 2020-2023 only, kinds columns only (Stage 2's
   function refuses any P&L column).
4. **The twins:** `lagged_day_sides` and `day_sides` imported unchanged; at L = 0 they reproduce S1's and S3's side
   tables on P-16's marks (Stage 2's own `shift_problems`); at the alert they read only bars ending at or before t.
5. **The logistic:** agrees with a Newton solve of the same objective on synthetic data to 1e-8; recovers a planted
   coefficient; the centred side rule's synthetic test (`tests/test_family_b_side_rule.py`) passes.
6. **A planted effect (T-14):** on synthetic bars with a direction effect of known size tied to a feature, the whole
   pipeline recovers it with the right sign, C1's bound covers it at its level, and C1-f against a twin that carries the
   same effect does not pass; on a driftless walk the lift is zero within its interval; a planted look-ahead feature
   fails the shift test.
7. **Stage B2's machinery:** on synthetic iid sides its rejection rate is the nominal one; on the review's Appendix B
   design it reproduces the over-rejection of a 21-session block-means test and its simulated critical value removes it.
8. **The place-recording adapter (C2):** re-running P-16's registered gate campaign as U2 did (100 paths, the bound arm,
   its seed) records trades by place whose counts reproduce `u_value_map.csv`'s `trades_per_year_records` for `p16`
   (and P-14's for `p14`).
9. **Choice-stage invariance (T-3, heavy, under the run lock):** stages A, B and B2 and the final model byte-identical
   when every judged-block bar is replaced by a seeded synthetic walk (`[20261968, 10]`) -- true by construction of the
   cutoff (M-5).
10. **The judge cannot fit (T-7)**; its manifest names the pinned model hash.
11. **The scorecard's identity:** the runner with P-15's cell reproduces P-15's registered rows and U1 start rows (Q-22).

## 21. Outputs

`results/fb_model.csv` (sections `supply`, `resolution`, `controls`, `power`, `search`, `choice`, `calibration`,
`judged`, `beside`) and `results/fb_scorecard.csv`, each with its sidecar manifest (`extended.results.write_result`), the
pinned model's hash in the judged manifest; run once from a clean checkout of a named commit (`scripts/run_clean.py`), the
heavy steps under the run lock.

## 22. Open before the pin -- the lead's and the operator's

**The operator's (a ruling, never a research question sent to them; until ruled, the safe default stands):**

1. **D-281 (3), the opening window.** Whether a family like this one may trade the 08:30-09:00 window (P-16's
   37.5-point schedule). Default: no; this version trades from 09:05.
2. **D-281 (3), the session so far.** Only if the lead or the red team holds that a model reading the session's range
   so far (from 09:00) is still inside the closed branch: whether this population may be traded. This draft's reading:
   it is outside (no entry in the window, none triggered by a range, no opening-range input).
3. **E-016 (2), the two opening-range features.** Out until ruled.
4. **NQ from 2026-07-17** as a fourth confirmation window (D-107, D-461), and its purchase -- only once a pick is carried.

**The lead's, before the pin:**

5. **The row Stage 2 D-621 (4)(d) needs (m-9):** D-621 (4)(d) says "no fitted values" and the gatekeeper's item 3
   repeats it; the audit (1.5 (a)) says family B needs its own row. The lead writes a row admitting fitted
   coefficients, a fitted centre (p~) and threshold, and one searched penalty, inside the declared walk-forward only.
6. **Q-16 merged**, its name, module and commit written where this file says **[Q-16]**; its power function for section
   8 item 8.
7. **The purpose-tagged reader and read ledger** (R-4, R-5, H-2) built before stage A (section 5).
8. **Q-22** (P-15's U1 identity) for the scorecard's runner; **Q-17's adapter** for the journey variables.
9. **The seeds** (section 19) confirmed unique at pinning.
10. **The family number:** F-02's draft may be pinned first.

## 23. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and recorded
in its own decision row -- never added to this file once pinned.)*
