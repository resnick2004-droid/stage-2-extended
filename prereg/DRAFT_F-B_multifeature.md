# DRAFT F-B: one multi-feature model choosing the side of a fixed post-opening schedule (family B) -- fourth version, not a declaration

**Status: DRAFT, fourth version, 2026-11-16 (TASK_QUEUE Q-56), redrafted from the red team's third read
`docs/reviews/DRAFT_F-B_multifeature_v3_2026-11-16.md` and the lead's ruling on it (E-036). Not pinned, no
F-number.** Nothing of the family is built beyond the feature library it names (`extended/features.py`, Q-11) and
three synthetic tests of its declared rules (`tests/test_family_b_side_rule.py`, `tests/test_family_b_opening_range.py`,
`tests/test_family_b_b2.py`). No bar has been read for it, no label computed, no model fitted on data, no outcome of
anything seen. This file may be edited until the lead pins it; from the pinning row on, nothing in it is edited (a
change is a new family). The family number is **k = the next free (11 if pinned next)**, so the level is one-sided
**0.05 / (k (k + 1))** (0.05 / 132 at k = 11). Seeds are **proposed** in 20261960-20261969 (section 19), checked unique
on 2026-11-16, for the lead to confirm at pinning.

It follows `vendor/stage2/prereg/TEMPLATE.md` and `FAMILY_TEMPLATE.md` as this repository adapts them after E-008 and
E-023 (CHARTER section 3), the Phase 0 audit's sections (`docs/audits/phase0/D_protocol.md` Part 3), CHARTER section
2's journey scorecard (E-014, E-015), E-026's judged-block reader (`extended/reader.py`), E-031's program rules,
**E-035's statistic** (`cons`, `extended/lift_bound.SHIPPED`), and `prereg/DRAFT_F-02_resting_levels.md`'s forms where
the reviews point to them.

---

## 0. In plain words (for the operator)

Stage 2's coin chooses long or short at random on a fixed schedule of trades. This family asks one question: **can a
model that looks only at NQ's recent price and volume choose the side better than the coin, on the same trades, by
enough to be worth money?** The model is a simple, pre-registered one (a regularised logistic regression on 37
measurements of the market, each scaled to the market's own recent volatility or volume). It is trained on 2020-2023
only, frozen, and judged once on 2024-01-02 to 2026-07-16.

**It trades from 10:10 CT on, and no single feature it looks at reads the first half-hour of the US session**
(08:30-09:00 CT), the territory of Stage 2's closed opening-range research. One thing is disclosed: three of its
features together give the price move from just before the open to an hour ago, which at 10:30 is the first hour's net
move. The lead ruled that this is outside the closed research, because those rules needed the opening range's high and
low (E-036). A reading beside the verdict shows the pick's edge with that move taken out.

It passes only if its side beats:

- the coin by more than chance, at the family's strict level, by the program's calibrated test (`cons`), checked
  against slow, persistent side patterns;
- being long in a rising market;
- each of the three follow-the-move rules Stage 2 already found, even at the strength Stage 2 saw them reach in
  2024-2026;

and only if it is worth at least $500 a year at that same strict bound, where its trades are actually used.

Expected in advance: the model will predict **how fast** a trade resolves (a check that the machinery works), but
probably **not which way**. With the opening half-hour out and the strict, persistence-proof test, the family very
likely lacks the power to see a small edge; it is likely to be declared a screen before any lift is read
(section 8). A "no" is a valid close.

## 0.1 What the fourth version corrects

The earlier versions' corrections (the first review's C-1, M-1 to M-6; the second's M2-1 to M2-5 and its minors) stand
except where this table changes them.

| finding | what changed (section) |
|---|---|
| M3-1 C1-f's follow component | **centred at its expectation**, `(g_t - g_r*) f^r_i`; the third version's "recentred by its replicate mean" dropped. **The amplitude is no smaller than the follow lift Stage 2 recorded on 2024-2026** (D-580, D-588, D-590, D-592: a disclosed pre-read). Stage 2's S1/S3 result files are not in the vendored snapshot: they are vendored under a decision row before the pin (E-002), and where they hold no comparable figure the amplitude is three times the choice block's, fixed now. `tests/test_family_b_b2.py` extended to C1-f's boundary null and C2's weighted form under `cons` (12) |
| M3-2 the opening range's net move as a combination | **the lead's ruling (E-036): outside the closed branch**. Disclosed: `d_pdc - gap - ret_60 = (C[t-61] - C[08:29]) / atr14` exactly, at 10:30 the 60-minute opening range's net move; the half-hour's VWAP distance also largely recoverable, its width and position only partly. Tested (`tests/test_family_b_opening_range.py`: the identity, and the R-squared of each opening-range quantity on the 37). Beside the judgement: **the pick's lift with the opening range's net move partialled out of its sides** (2, 13) |
| Q-16 named (E-035) | every line is read by **`cons`** (`extended.lift_bound.SHIPPED`: the trade-weighted session-cluster t on 21-, 42- and 63-session blocks, all three required), with B2's critical value per component. No line of this family is two-sample: C1-d and C1-f are paired on the same offers. Any two-sample reading beside uses `two_sample_bound` with the treated-cluster df (E-035 (2)) (12, 13) |
| E-035 (6) persistence | the side process's persistence stated before the pin, measured at stages B and C, and flagged (12) |
| m3-1 | a refusing per-row as-of rule: every as-of close and the day's first open that a used feature reads at an admitted alert lies outside 08:30-08:59, or the row is dropped and counted; tested on a synthetic post-09:00 gap (3, 20) |
| m3-2 | about 609 judged sessions (the pinned calendars); `cons`'s blocks by `lift_bound.block_index` cover every session, none dropped: 29, 14 and 9 blocks (df 28, 13 and 8). The MDL at those df (8, 13) |
| m3-3 | the lines' per-session values are `lift_bound`'s `(S, N)`: the sum of the line's per-offer values over the session's offers and their count, an empty session `S = N = 0`. The estimand is the per-offer mean, stage B's (13) |
| m3-4 | C2's B2 runs after `stage_C_campaign`, conditional on the realised routing. Why the coupling is second order is stated; C2 priced at design (ii)'s coin-sided routing beside; `a*` per table R (13) |
| m3-5 | a `filter` cell's MDL at its training share at stage A, recomputed beside at the judged share; its K2 and the eligibility margin on 2021-2023 (8, 11) |
| m3-6 | the scorecard's 2021-2023 starts truncated at 2023-12-29, labelled (14) |
| m3-7 | the scratch checks behind section 12, with their printed output, are in the tree: `docs/reviews/scripts/family_b_drafter/` (12) |
| n3-1 | what the reader does not enforce (the order of the purposes, "bars up to each alert") said, and what does (5) |
| n3-2 | the power: at 8 df the one-sided t at 0.05/132 is 5.27; the family is very likely a screen; the MDL ratio computed at stage A (8) |
| n3-3 | stale text removed (E-030 corrected E-019; E-031 (1) wrote the fitted-values row) (2, 22) |
| n3-4 | the prior session after a holiday halt: a definition, not look-ahead, said beside the feature table (7) |
| n3-5 | day kinds: E-029's pinned calendar holds the scheduled early closes in advance; only defect days remain post-alert facts (5) |
| n3-6 | the two amplitudes' directions stated: the drift's `a*` from 2020-2023 is probably conservative, the follow amplitude's choice-block value is not -- hence M3-1's rule (12) |

## 1. Hypothesis (research protocol step 1)

**The mechanism.** Intraday direction on an index future is close to unpredictable, but not exactly. Short-horizon
momentum and the price's position against levels everyone watches (the prior day's range, the overnight range, round
numbers) move the order flow of discretionary and systematic traders. Volume against its usual time-of-day level marks
when informed flow is present. One model reading all of these together might find a small, stable direction signal that
no single rule shows. **Expected:** volatility and resolution speed are predictable (volatility clusters; the handoff
3.3). Direction is hard: Stage 2's OHLC rules against their coin twins found gains of schedule, not direction (D-558),
and a follow-the-move effect real per trade but concentrated in 2024-2026 (D-580, D-588, D-592).

**What would make it worth something.** Not its accuracy, but its lift in win probability over the coin at the same
entries, times how often it is used, times what a win is worth where it is used (`vendor/stage2/results/u_value_map.csv`;
the handoff 2.7).

**Two targets** (the handoff 3.3):

- **resolution speed** (expected predictable) -- the pipeline's **positive control**, and a filter read beside the
  scorecard. It cannot pass: a filter that ignores the side has no lift over the coin by construction.
- **direction** (expected hard) -- the only target the pass line reads.

## 2. Prior exposure (the audit's R-3; P-3, D-2)

What Stage 2 already read of this mechanism, these hours or these entries on NQ 2020-01-02 to 2026-07-16:

| row | what was read | latency | sign and span |
|---|---|---|---|
| D-555, D-557, D-558 (A4) | short-bar momentum rules against their coin-sided copies, P-16's schedule | L = 0 | a genuine but tiny per-trade direction effect; no campaign value beyond the schedule |
| D-578, D-580 (program S, S1) | 15 OHLC side rules on P-16's offers | **L = 0** (D-589 (5)) | 15-minute momentum (`mom15`, at 3R) and the latest 5-minute breakout (`lbrk5`, at 1R and 1.5R), **followed**, survive the per-offer test; both fail the span guard (below P-16 on 2020-2023, above on 2024-2026) |
| D-581, D-582 (S2) | P-16's coin gated by volatility and trend states | L = 0 | no state improves the offers enough |
| D-586, D-588, D-589 (S3) | new event kinds, followed | **L = 0** | the 1-minute 4-bar breakout followed (`lnbar1x4`) passes all four guards, its gain concentrated in 2024-2026 |
| D-590, D-592 (S3 at the latency) | `lnbar1x4` with its side read five minutes early | **L = 5** | fails its campaign guard, but **the per-offer lift over the coin is nearly as large at L = 5 as at L = 0 at every R** ("broad and slow"); recorded as **a lead for unread data** |
| A3 (`config/atlas_a3.yaml`; D-492 (1); D_protocol 1.2) | the 5-, 15- and 30-minute opening-range breakouts (`orb_rth5`, `orb_rth15`, `orb_rth30`) | **five bars late, both side rules** (D-492 (1)) | read over 2020-2026, both blocks; no coin-twin direction effect recorded (D-494 (2), D-500 (3)(a)) |
| D-275, D-277, D-281 (ORB1-ORB6) | the 08:30 NQ opening-range breakout, with trend, gap and VWAP filters in ORB6's scope (D-277) | the hand-traded latency | closed for good; D-281 (3): ORB5's hand-traded stop entry, chased, held a positive funded-leg bound in both eras, and **whether any later hypothesis is genuinely different is the operator's call** |
| program U (nine families); F-01 (withdrawn, E-007); F-02's and F-P's drafts | contract levers; resting orders at pre-session levels; payout policy | -- | no direction read in U; F-01 read nothing; the drafts read nothing yet |

**What follows for this family.**

- **(a) The judged block is late development for direction, not out of sample** (the audit's P-3). The follow effect
  is known to be strong there, so the pass line is joined by conjunctive kill lines the known effects cannot clear
  (section 13): a drift-matched lift, and the lift over each of Stage 2's three follow rules **read at the five-minute
  latency this family trades at**.
- **(b) A new question, not a re-run.** No Stage 2 work fitted a model jointly on normalised features, and a pass must
  beat every recorded follow rule on the same offers.
- **(c) The opening range: the audit's default in substance, and the lead's ruling on what remains** (D_protocol 1.2
  (3); E-024 (5); E-036; D-281 (3)):
  - **What is kept out.** At every admitted alert, **no used feature reads a bar stamped 08:30-08:59 CT of the
    alert's day** (tested; on a day with gaps, with the as-of rule of section 3). So no feature reads the half-hour's
    extremes, the position in it, its path or its VWAP, for any opening range that starts at 08:30 (5, 15, 30 or 60
    minutes).
  - **What remains, disclosed (M3-2).** The net move across the half-hour, as a difference of closes on either side
    of it: **`d_pdc - gap - ret_60 = (C[t-61] - C[08:29]) / atr14` exactly**, on every non-roll day at every alert.
    - Why, from `features.py`: `d_pdc = (c - prior close) / atr14`, `gap = (C[08:29] - prior close) / atr14`, and
      `ret_60 = (c - C[t-61]) / atr14`.
    - At the 10:30 alert it is the 60-minute opening range's net move (from the 08:29 close, within the opening tick
      of the 08:30 open). At 10:05 it is the 30-minute range's net move plus five minutes.
    - A linear model can place it in its score with three coefficients.
  - **How much of each opening-range quantity the 37 carry linearly** (`tests/test_family_b_opening_range.py`, a
    synthetic year; the scratch figures in `docs/reviews/scripts/family_b_drafter/m32_r2.py`):
    - the 60-minute range's net move at 10:30: entirely;
    - the distance of `c` to the half-hour's VWAP: largely, since it is mostly `c`'s move since 08:29;
    - the half-hour's width and the position in it: only partly, through the volatility features.

    The test asserts the first, and that the width and the position stay below an R-squared of 0.9. The VWAP's share
    is disclosed, not asserted.
  - **The lead's ruling (E-036): outside the closed branch.** Stage 2's branch (D-277, D-281, ORB6's scope D-278) is
    trading rules defined on or triggered by the opening range, and a breakout needs the range's extremes, which no
    feature reads. A model whose inputs carry the session's move since the prior close holds the half-hour's net move
    without being such a rule.
  - **What the ruling requires, and this draft does:** the identity disclosed here; and beside the judgement, **the
    pick's lift with the opening range's net move partialled out of its sides** (section 13), so a pass that only
    replicates an opening-range rule is visible.
  - The operator may still rule on D-281 (3) (section 22).

## 3. The population: where the family trades

**What was looked for** (M-1, M-5, M2-1, M2-4). A set of offers inside US regular hours, whose features never read the
08:30-08:59 bars, whose brackets resolve (D-212: at most 5 % to the flatten at every R the table offers, every year),
fixed without reading the judged block.

| option | what it gives | taken? |
|---|---|---|
| P-16's 37.5-point schedule in regular hours | entries 08:35-09:00 only (`rc_width_screen.csv` section `marks`, 150 ticks) | **no:** inside the closed window (D-281 (3)) |
| the second version's schedule from 09:05 | its first alerts read the half-hour (M2-1) | **no:** the opening range would be in the model |
| per-feature masks from 09:05 | each windowed feature blanked at the early marks where it reads the half-hour | **no:** the model's inputs would change by mark until 11:00, and its first trades would still be the session's first ones after the half-hour |
| **the family's own five-minute schedule from 10:10** | every entry mark 10:10-15:05 admitted per stop by D-525 (4)'s rule, per year, on the choice block only | **taken** |
| the 37.5-point stop on that schedule | -- | **no** (M2-4, below) |
| P-15's 25-point schedule | its extent is vendored (marks to 12:00 CT, `rc_width_screen.csv` row `rc_s100_all_nr`); its per-mark list is not, and `mark_resolution` computes it over the whole window | **no:** it would read the judged block (M-5); the family computes its own |
| P-14's breakout offers, Stage 2's 50-point schedule | follow built in / no regular-session mark resolves | **no** |

**The schedule, fixed now.**

- **Alerts:** t in 10:05, 10:10, ..., 15:00 CT (60 a session at most). **Entry marks:** m = t + 5 in 10:10..15:05.
  - Why 10:05: every used feature's window then starts at or after 09:00 (the 60-minute ones read from the bar
    stamped 09:04). An earlier first alert would let some 60-minute window read the half-hour.
- **Stops:** **12.5 and 25 points** (50 and 100 ticks) -- P-14's two rungs (R\* = P-14 trades both), both above the
  45-tick cost floor.
- **The cutoff, per stop** (D-525 (4)'s rule; Stage 2's `resolved_coin.mark_resolution` on this family's own walks,
  kinds only, both sides pooled, sessions 2020-01-02 to 2023-12-29 only):
  - an entry mark is admitted only if its unresolved share is at most 5 % at **every R the table offers** (0.25, 1,
    1.5, 2, 2.5, 3) **in every choice year** (2020, 2021, 2022 and 2023 separately; M2-4);
  - the admitted marks per stop are written to the result file's `supply` section before any direction outcome is
    read, with the offers per session and the expected count per block (the judged block's from its session count in
    the store's manifest `day_list`, no bar read).
- **Sessions:** Stage 2's day kinds `n` or `b` (not FOMC, not an early close, not empty; `atlas_local.close_day`),
  after the store's first `extended.features.HISTORY_DAYS` (22) sessions -- about 1,000 sessions in the choice block,
  and about **609** in the judged block (the pinned calendars, section 13; counted exactly at the build).
  - **The as-of rule (m3-1), refusing, per row.** An admitted (session, alert) row is kept only if every as-of close
    a used feature reads -- as of `s - 1`, `s - 6`, `s - 16`, `s - 31` and `s - 61` -- and the day's first bar lie
    outside 08:30-08:59 of the day. Otherwise the row is dropped and counted in `supply`.
  - Where the bars are complete this never binds. It binds only after a gap with no bar from 09:00 to `s - 61` or
    later: in `tests/test_family_b_opening_range.py` a 25-minute gap after 09:00 flags exactly the five alerts it
    affects, and only there does replacing the half-hour move a used feature.

**What it costs, said in advance.**

- **The opening hour is gone.** v2's 09:05-10:05 entries are lost (13 a session). These are among the session's most
  active minutes and, by Stage 2's whole-window rows, its most resolvable after the open.
  - The funded openings in the scorecard's design move to the first offer after 10:10.
- **The 37.5-point stop is dropped** (M2-4), on a disclosed pre-read (section 5):
  - at 150 ticks Stage 2's walk leaves the first regular-session mark after 09:00 unresolved at R = 3 above the 5 %
    line over 2020-2026, and later marks are worse;
  - the family's fixed walk leaves at least as many unresolved (the move only adds exits);
  - so a 37.5-point cell admitted on the choice block would very likely fail the judged resolution floor.
- **The 25-point stop may be thin or empty.** Stage 2's 25-point US-hours coin (marks 08:30-12:00, `u_hours.csv` rows
  175-208) resolved at R = 3 pooled but not in its worst year, and D-641 (3) capped its offered R at 2.5 for that.
  - This family drops the faster early marks and walks without the move, so at 25 points the per-year cutoff at R = 3
    may admit few marks or none.
  - Capping the table's R as D-641 did is **not taken**: it would remove the funded opening's 3R ask, the place the
    value map prices highest, and make a different design.
  - If no 25-point mark is admitted, the six 25-point cells die at K1 (counted) and **the family is a 12.5-point
    family**.
- **The 12.5-point stop:** costs are a larger share of its risk, and Stage 2's 12.5-point US-hours coin cell was killed
  by its campaign line (D-527 (3)). The pass line is cost-free (both sides of a pair pay the same), so the stop is
  admitted, as F-02 admits it (its section 6.3), but its scorecard starts from a weak base.
- **Not a registered coin's schedule.** Supply comes from a declared schedule (the handoff 3.4's principle), so the
  scorecard compares the design with the same schedule's coin (design (ii), section 14). R\* = P-14 stays the row to
  beat beside.
- **Power.** Fewer offers, fewer features and the stricter test (section 12) may leave the family a screen (section 8
  item 8). That is stated before any read.
- **Sound?** Yes: a test of direction on the post-opening session, narrower and weaker than the first two versions.
  Nothing in the exclusion makes the test invalid.

## 4. Contract fit (step 2) -- the constraints the family lives inside (CHARTER section 4)

| constraint | how the family meets it |
|---|---|
| latency, at least 5 minutes, hand entry (D-266; E-008) | the side at alert t from bars stamped <= t - 1 min only; a market order placed by hand at t + 5, booked at the open of the first bar opening at or after t + 5, its tick charged as a cost (`extended/walker.py` `MARKET`); no automated or API entry |
| one position per firm, 5 minutes flat (D-429) | the pass line reads every offer (the coin twin's form); the scorecard routes by Stage 2's strict rule |
| resolution (D-212, D-308; D-8) | the per-year cutoff (section 3) and K2, at most 5 % overall and in every year |
| realised risk (D-308) | K3, reported (a market entry's stop exit slips adversely: it cannot fail, D-9) |
| stop band and cost floor (`stop_band.csv`) | 50 and 100 ticks, above the 45-tick floor |
| news (D-525, D-533; E-007 (d); n2-5) | entries from 10:10 CT, after every BLS 08:30 ET release and more than an hour after the 10:00 ET (09:00 CT) releases; FOMC days excluded |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (no tight brackets, durations minutes to hours); no maximum size into major news; no copying across accounts (D-157); nothing concealed |
| tier 2 (D-289) | as P-14's table: off in the base case, on beside |
| tier 3 (E-013 (1)) | 0 % denial in the verdict; 10/25/50 % beside |
| firm rules | none loaded by the family; the scorecard runs Stage 2's engine on its verified ledger |

## 5. Data, blocks, the seal and the disclosed pre-reads

- **Data:** Stage 2's NQ 1-minute bars (licensed, uncommitted, `vendor/DATA_MANIFEST_stage2.sha256`), development window
  **2020-01-02 to 2026-07-16** only. Stage 2's walks (`data/atlas`) are not read; labels come from this repository's
  walker (E-011).
- **The choice block:** sessions **2020-01-02 to 2023-12-29** (the cutoff, the fits, the search, every choice). **The
  judged block:** sessions **2024-01-02 to 2026-07-16**, read for the frozen pick only.
- **The seal (R-4, R-5; E-026).** Every bar and walk is read through `extended/reader.py`. The reader:
  - refuses anything from 2026-07-17 outright;
  - refuses any choosing or fitting purpose on the judged block;
  - refuses a judged-block purpose this pinned file does not name on its line below;
  - refuses a judged read outside a clean run of a committed tree, and a second run under the same purpose without a
    `repeat=` row;
  - ledgers every judged read in `results/read_ledger.jsonl` before it reads.

  The family's judged-block purposes, each read once (one clean run of the runner reads all four, in this order):

  - **Judged-block reads:** `stage_C_sides`, `stage_C_judgement`, `stage_C_campaign`, `stage_C_scorecard`

  What each is:
  - `stage_C_sides` -- the judged block's bars up to each alert, for the pinned model's features and sides, the
    filter's selection and the three twins' sides only. They are hashed into the run's manifest before any outcome is
    read; stage B2 runs on them;
  - `stage_C_judgement` -- the bars after each entry, for the labels and pair values at the pick's stop: C1, C1-d,
    C1-f and the readings beside;
  - `stage_C_campaign` -- the engine's gate campaign of designs (i) and (ii) on the judged block: C2's routing and the
    long-run gate floor;
  - `stage_C_scorecard` -- the U1 journey replay and Q-17's adapter on the judged block's starts.

  T-3 (section 20) is the second proof of the seal.

  **What the reader does not enforce (n3-1).** It returns whole sessions, so `stage_C_sides`' "bars up to each alert"
  rests on the library's shift-invariance tests, the twins' build check (section 20 item 5) and the runner, which
  computes every side before it walks any label. Nor does it order the purposes: the runner does (section 13), and
  the ledger's `when` fields record the order.
- **Disclosed pre-reads (m-6, m2-7):** inputs read or fitted over 2020-2026 that T-3 cannot see, each with what it can
  bias.

  | input | what it is | can bias | cannot bias |
  |---|---|---|---|
  | `stop_band.csv` | the cost floor and the stop band | which stops are allowed | any side or lift |
  | `u_value_map.csv` | D-667's solved tables from the registered edge rows | the stage-B ranking and C2's dollars per place (`mean_dv`) | the lift or its bound |
  | `rc_width_screen.csv` section `marks` (150 and 200 ticks) and the cell row `rc_s150_us` | Stage 2's per-mark resolution over 2020-2026; the 37.5-point US cell fails every-R-resolves | the drop of the 37.5-point stop (section 3) | the population (its cutoff is the family's own, on the choice block) and any side |
  | `rc_width_screen.csv` row `rc_s100_all_nr` (P-15's news-safe all-day cell, D-534, D-535) | the 25-point coin's offered marks run to 12:00 CT | the stated 25-point expectation | the population and any side |
  | `u_hours.csv` rows 175-208 and D-641 (3) | the 25- and 37.5-point US coins' worst-year resolution and their R caps | the stated 25-point expectation; the drop of the 37.5-point stop | the population and any side |
  | Stage 2's S1/S3/A4/A3 reads | direction readings on these bars | the design of the kill lines (they are why C1-f exists) | the pick (fixed by stage B on the choice block) |
  | Stage 2's S1/S3 result files (`s1_sided_coin.csv`, `s3_event_kinds.csv`, `s3_latency.csv`; to be vendored, section 22) | the twins' recorded lifts, 2024-2026 among them | B2's follow amplitude (b), so C1-f's critical value, upward only | any side, the pick or the population |

- **Day kinds and post-alert facts (n-4, n3-5).** Scheduled early closes are known in advance from E-029's pinned
  calendar (`config/calendar_early_closes.csv`); only a data-defect day is known from its own bars. Stage 2's FOMC set
  holds the unscheduled statement of 2020-03-03. Both drop whole days, both sides alike; the population follows Stage
  2's day kinds for comparability.

## 6. The offers, the brackets, the walk and the labels

- **Entry:** booked at the open of the first bar opening at or after t + 5; one tick charged as a cost, not in the price
  (n-5). Both sides of every offer enter at the same price, so there is no fill-bar asymmetry and the mirror is a
  realisable market order.
- **Brackets:** stops 50 and 100 ticks; targets at R in {1, 1.5, 3} (the table's three asks), floor(R x S) ticks (Stage
  2's `target_ticks`); pair values at every R the table offers (0.25, 1, 1.5, 2, 2.5, 3) for C2.
- **The walk: fixed barriers** -- `extended.walker.Rules("stage2_fixed", FLAT_ENTRY, "worst_less_two",
  breakeven=False)`:
  - Stage 2's walk end (the bar ending 15:08 CT) and flatten (the worst of the bars ending 15:08-15:10, less two ticks);
  - stop on a touch, target on a trade through, stop first on a two-barrier bar;
  - **no breakeven move** (allowed as made, E-013 (2); its defects are Q-20's; read beside);
  - Stage 2's costs at each stop.
- **The pair** at each offer and bracket: the long's and the short's kind, gross and net R, and the pair value
  `d = (win_long - win_short) / 2` in win probability (`win` = a target exit); net R beside. A side rule with sides
  `s_i` in {+1, -1} has **lift over the coin twin** `mean(s_i d_i)`.
- **The direction target** (per stop, fitted at R = 1 only): `y = 1` if the long's net R at R = 1 exceeds the short's,
  `y = 0` if below, left out of the fit if equal.
- **The resolution target** (per stop): `T` = minutes from the entry bar's open to the first bar touching entry +- S,
  the walk's end when none; `y_res = 1` if `T` is at most the training fold's median of `T`.

## 7. The features and their preparation

**The library:** `extended/features.py`, pinned by its sha256 at the pinning commit. **Family B uses 37 of its 47
features:** every feature that, at an alert from 10:05, reads no bar stamped 08:30-08:59 of the alert's day.
`tests/test_family_b_opening_range.py` holds this list (`FAMILY_B_FEATURES`) to the bars, and to this table. Every
feature reads only bars stamped <= t - 1 minute and earlier sessions' bars; every normaliser is from the past only;
cross-day features are NaN on a roll day; calendars are used only as known in advance. The registry, as
`extended.features.describe()` prints it -- **the 37 this family uses:**

<!-- family-b-features:start -->
| feature | group | formula | window | normaliser | reads | from | cross-day | warm-up | per |
|---|---|---|---|---|---|---|---|---|---|
| `ret_5` | return | (c - close of the last bar stamped <= t-1-5min) / atr14 | 5 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_15` | return | (c - close of the last bar stamped <= t-1-15min) / atr14 | 15 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_30` | return | (c - close of the last bar stamped <= t-1-30min) / atr14 | 30 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_60` | return | (c - close of the last bar stamped <= t-1-60min) / atr14 | 60 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_day` | return | (c - open of the trading day's first bar) / atr14 | 17:00 to t | atr14 | the day's bars stamped <= t-1min | 08:30 | no | 14 | alert |
| `rng_15` | range | (max high - min low of the bars stamped t-15..t-1) / atr14 | 15 min | atr14 | the day's bars stamped t-15..t-1min | 08:30 | no | 14 | alert |
| `rng_60` | range | (max high - min low of the bars stamped t-60..t-1) / atr14 | 60 min | atr14 | the day's bars stamped t-60..t-1min | 08:30 | no | 14 | alert |
| `pos_prior` | position | (c - prior RTH low) / (prior RTH high - prior RTH low) | the prior regular session | the prior session's range | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 1 | alert |
| `d_pdh` | level | (c - prior RTH high) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 14 | alert |
| `d_pdl` | level | (c - prior RTH low) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 14 | alert |
| `d_pdc` | level | (c - prior RTH close: the last close stamped <= 14:59) / atr14 | the prior regular session | atr14 | the prior day's bars stamped <= 14:59; c | 08:30 | yes | 14 | alert |
| `d_onh` | level | (c - overnight high) / atr14; overnight = bars stamped 17:00..08:29, frozen at 08:30 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29; c | 08:30 | no | 14 | alert |
| `d_onl` | level | (c - overnight low) / atr14 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29; c | 08:30 | no | 14 | alert |
| `range_on` | level | (overnight high - overnight low) / atr14 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29 | 08:30 | no | 14 | day |
| `gap` | level | (the last close stamped <= 08:29 - prior RTH close) / atr14 | prior 14:59 to 08:30 | atr14 | the prior day's bars stamped <= 14:59; the day's bars stamped <= 08:29 | 08:30 | yes | 14 | day |
| `d_round` | level | (c - the nearest multiple of 100 index points) / atr14 | the last bar | atr14 | the last bar stamped <= t-1min | 08:30 | no | 14 | alert |
| `vol_5` | volume | log((V5 + 1) / (median V5 + 1)), V5 = volume of the bars stamped t-5..t-1 | 5 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-5..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `vol_30` | volume | log((V30 + 1) / (median V30 + 1)) | 30 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-30..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
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
<!-- family-b-features:end -->

**In the library, not in this family** (each reads the 08:30-08:59 bars at some admitted alert, or is the opening range
itself):

| feature | group | formula | window | normaliser | reads | from | cross-day | warm-up | per |
|---|---|---|---|---|---|---|---|---|---|
| `ret_120` | return | (c - close of the last bar stamped <= t-1-120min) / atr14 | 120 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_rth` | return | (c - open of the first bar stamped >= 08:30) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `range_day` | range | (day high - day low so far) / atr14 | 17:00 to t | atr14 | the day's bars stamped <= t-1min | 08:30 | no | 14 | alert |
| `range_rth` | range | (regular-session high - low so far) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `pos_day` | position | (c - day low) / (day high - day low), so far | 17:00 to t | the day's own range | the day's bars stamped <= t-1min | 08:30 | no | 0 | alert |
| `pos_rth` | position | (c - RTH low) / (RTH high - RTH low), so far | 08:30 to t | the session's own range | the day's bars stamped 08:30..t-1min | 08:35 | no | 0 | alert |
| `d_vwap` | level | (c - RTH VWAP so far: sum((h+l+c)/3 x volume) / sum(volume)) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `or_width` | opening range | (OR high - OR low) / atr14, OR = the bars stamped 08:30..08:59 | 08:30 to 09:00 | atr14 | the day's bars stamped 08:30..08:59 | 09:00 | no | 14 | day |
| `or_pos` | opening range | (c - OR low) / (OR high - OR low) | 08:30 to 09:00 | the OR's own range | the day's bars stamped 08:30..08:59; c | 09:00 | no | 0 | alert |
| `vol_day` | volume | log((Vday + 1) / (median Vday + 1)), Vday = the day's volume stamped <= t-1 | 17:00 to t | its median at the same CT slot over the 20 prior trading days | the day's bars stamped <= t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |

Why each is out:

- `or_width`, `or_pos`: the opening range itself (E-016 (2)).
- `ret_rth`, `range_rth`, `pos_rth`, `d_vwap`: their window starts at 08:30 at every alert, so they read the half-hour
  always (M2-1).
- `range_day`, `pos_day`, `vol_day`: their window is the day so far, from 17:00, which contains the half-hour.
- `ret_120`: its start close is a bar of the half-hour at the alerts 10:35-11:00.

**Not redefined.** A since-09:00 version of the session-so-far features was considered and not taken. It would add new
library features defined after a review. At alerts from 10:05 the 60-minute windows (`rng_60`, `ret_60`, `ext_ma60`,
`vol_accel`, and the 60-minute realised volatility inside `rv_ratio`, `rv_tod` and `rv_atr`) already carry the recent
session. The cost: the model has no session-level VWAP or session range.

**The prior session after a holiday halt (n3-4).** On the day after a halt that ends a session early (MLK, Presidents'
Day and the like), the prior-session features (`pos_prior`, `d_pdh`, `d_pdl`, `d_pdc`, `range_prior`, `ret_prior`,
`gap`) read that partial session (08:30-11:59) as the prior regular session, since early-close days stay in the frame.
This is a definition, the same on both blocks, not look-ahead.

**What `c` and `atr14` are:** `c` = the close of the last bar stamped <= t - 1 min; `atr14` = the mean daily true range
of the 14 prior sessions, the prior close used only within one contract. Two features are level-dependent by design:
`d_round` and `atr_rel`.

**Preparation, every statistic fitted inside the training fold only and applied out of fold** (feature-rules 4):

1. each real feature winsorised at the training fold's 0.5 % and 99.5 % quantiles;
2. standardised by the training fold's mean and standard deviation;
3. `dow` as four indicators (Tuesday-Friday, Monday the reference); the binary flags as they are;
4. one missing indicator, `m_cross` (a roll day: the five cross-day features missing); every remaining missing value
   set to 0 after standardisation (the training mean).

**The design matrix: 41 columns** (37 features, `dow` replaced by four indicators, plus `m_cross`) **and an
unpenalised intercept.** No feature is selected, transformed or dropped by data. A column with zero variance in a
training fold stops the fit (the failure protocol), never silently dropped.

## 8. Stage A: the gates, before any lift is read (choice block)

1. **The dependencies hold** (refusing): the reader (section 5); the identities (section 20).
2. **The cutoff and K1 supply.** The admitted marks per stop (section 3).
   - K1 for a `side` cell: at least 12 offers a year in every calendar year 2020-2023.
   - K1 for a `filter` cell: the same, counted after its out-of-fold filter in 2021, 2022 and 2023 (2020 has no
     out-of-fold prediction).
   - Else the cell is killed.
3. **K2 resolution.** The share flattened unresolved, both sides pooled, at every R in {1, 1.5, 3}, at most 5 % in
   each choice year: implied by the per-year cutoff for a `side` cell, checked for a `filter` cell on its filtered
   offers in 2021, 2022 and 2023 (2020 has no out-of-fold filter; m3-5). Else the cell is killed; nothing is re-cut.
4. **K3 realised risk** (D-308): reported.
5. **The positive control.** The resolution model's out-of-fold AUC on 2021-2023 at each surviving stop, its one-sided
   95 % lower bound by stage B's bootstrap (`default_rng([20261960, 0])`) above 0.5. Else the failure protocol runs
   before stage B, and the family waits for the lead's ruling under a row.
6. **The join assertion (m2-1), refusing.** Every label row's (session, entry mark) equals its feature row's (session,
   alert + 5), and every pair value's session and mark equal its side's. A misaligned join -- for example features of
   session d joined to labels of session d - 1 -- stops the run. Alignment's statistical proof is T-14's driftless
   null and planted size (section 20 item 6), not an AUC: the shifted-label control of the second version is dropped,
   since the prior-session features predict a shifted label.
7. **The null canary.** The whole direction pipeline (folds, search, fit, out-of-fold sides, stage B's statistic) run
   once on the choice block, with the long's and the short's outcomes swapped in every 63-session block a seeded coin
   picks (`[20261961, 0]`).
   - Its maximum studentised lift is set against the 99.9th percentile of `max_c (L*_c - L_c) / SE_c` over 10,000
     **centred** bootstrap draws of its own data, as stage B's `q` is built (`[20261961, 1]`; m2-6). Above it is a
     defect signal, and the failure protocol runs.
   - It reads choice-block direction outcomes inside stage A (flipped, before any lift of the model is read):
     harmless, said so.
   - **What each guard covers (n2-4):**
     - the canary: label-derived leakage and in-sample evaluation;
     - the shift test (`tests/test_features_lookahead.py`) and T-14's driftless null: bar look-ahead;
     - the join assertion: misalignment;
     - stage B2: slow side persistence.
8. **Power on record (R-16), on sessions (n3-2, m3-5).** For each surviving cell, the minimum detectable lift (MDL) at
   the family's level on the judged block, for `cons`: the 80th percentile of `lift_bound.mdl_draws("cons", S, N,
   level)` over nulls.
   - **The nulls:** the choice block's own pair values at the cell's population, signs flipped by 63-session block
     (`[20261960, 2]`), laid on the judged block's calendar (about 609 sessions).
   - **The binding component:** `cons`'s components then have df 28, 13 and 8, and the last binds -- one-sided t at
     0.05/132 is 5.27 there, against z = 3.37.
   - **What it reads:** the choice block's pair values, for their dispersion only, disclosed like B2.
   - **A `filter` cell:** at its training share (about a fifth) at stage A, recomputed beside at the judged share at
     stage C (m3-5).
   - **The screen rule:** the MDL is set against the value bar (`u_value_map.csv` section `bar`: the extra win
     probability for $500 a year at the cell's uses). If it exceeds the bar by more than a factor of 3 at every
     surviving cell, the family is **declared a screen** (section 15).
   - The ratio is written in stage A's result before any lift is read. On the arithmetic above, a screen is the likely
     outcome.

## 9. The model, its search and the walk-forward (R-7)

- **The model:** an **L2-regularised logistic regression**, one per stop and target.
  - It minimises the session-weighted mean log loss `(1/D) sum_d (1/m_d) sum_{i in d} logloss_i + (lambda/2)
    ||beta||^2` (D training sessions, m_d labelled offers in session d; the intercept not penalised).
  - The solver is `scipy.optimize.minimize(method="L-BFGS-B")` with the analytic gradient, from zero, `gtol` 1e-10, at
    most 2,000 iterations; a fit that does not converge is refused. Deterministic, no seed.
  - Implemented in this repository's package after the pin, and held by its tests (section 20).
- **Searched: lambda**, over **seven values `0.25 x 10^(j/2)`, j = -2..4** (0.025 to 25), per stop and target, inside
  the choice block only:
  - **inner walk-forward:** test years 2021, 2022, 2023, each trained on the choice block's population sessions before
    it, less its last 22 sessions. A forward walk needs no embargo; the 22 sessions are kept from the first version
    only because they are harmless (n-2).
  - **criterion:** the session-weighted out-of-fold log loss summed over the three test years; the smallest wins, a
    tie (within 1e-9) to the larger lambda.
  - **the top edge:** under a null or a weak signal the criterion is expected to choose it. Under the centred side the
    edge does not matter for balance (n2-2, section 10), and a pick there is reported as such.
  - every configuration (lambda x stop x target) and its criterion written to the result file and **counted**.
- **The out-of-fold predictions for stage B:** at each stop's chosen lambda, the three inner folds' predictions on
  2021-2023, **each fold's model with its own p~ and its own filter threshold** (section 10).
- **The final model:** refitted at the chosen lambda on all the choice block's population sessions. Serialised to
  canonical JSON and **hashed**, the hash pinned in a decision row before the judged read (R-7; T-7):
  - its coefficients;
  - the in-fold winsorising, standardising and imputing constants;
  - **its p~ and its filter threshold** (both from its own training sample);
  - the resolution model's training median.

  No early stopping, no refits with other seeds, no feature subset, no class weights.
- **The resolution model** (the control): the same pipeline on `y_res`, its own lambda by the same search.

## 10. How a prediction becomes a trade, and the cells

- **Definitions.** `p` is the direction model's probability that the long beats the short. **`p~` is the model's
  session-weighted median of its own fitted p on its training sample**, pinned with it.
- **The side:** long if p > p~, short if p < p~, a seeded coin if exactly equal (`[20261963, 0]`).
- **Why it cannot collapse (n2-2; the proof).** p is a monotone function of the linear score `z = b0 + x . beta`, and a
  weighted median that picks an element commutes with a monotone map. So `sign(p - p~) = sign(x . beta -
  median(x_train . beta))` exactly: the intercept, and with it the training block's base rate, cancels, whatever
  lambda is. `tests/test_family_b_side_rule.py`:
  - asserts the identity (`test_the_intercept_cancels_exactly`);
  - illustrates it on null and weak planted signals.
  - That test cannot show a judged-block imbalance from a level-dependent or trending feature, since it has no
    covariate shift (n2-3). C1-d's 0.9 rule and stage B's long-share report are the guards.
- **Two uses:**
  - `side` -- every offer of the stop's population takes the model's side;
  - `filter` -- only offers with `abs(p - p~)` at or above **the 80th percentile of that model's own session-weighted
    training-sample `abs(p - p~)`** are offered, at the model's side (M2-5). Each inner fold uses its own threshold
    for stage B, the final model its own for stage C. A fixed linear score has the same spread on new offers drawn
    like its training ones, so about a fifth pass; the judged share is reported beside, and the MDL uses it.
- **E-023 (CHARTER section 3).** No cell of this family is a filter that keeps the coin's side. The `filter` cells keep
  the model's side, so E-008's lift over the coin twin on the same filtered offers judges them, and the coin twin
  cancels the selection. The resolution filter read beside the scorecard (section 14) does keep the coin's side. It is
  never judged here; to be carried it would need its own family under E-023's placebo-selection rule.
- **The cells: k_cells = 2 stops x 3 R x 2 uses = 12.** Within a stop and a use the trades and sides are the same at
  every R; R decides the bracket C1 reads and the places the ranking prices.

## 11. Stage B: choose on the choice block (2021-2023, out of fold)

- **The statistic (m-2), one estimator.** For each cell surviving stage A:
  - `L_c` = the **mean over the cell's offers** of `s_i d_i`;
  - its bootstrap: a stationary bootstrap of sessions with **mean block 63** (as the judged lines' dependence),
    2,000 draws (`[20261962, 0]`), each draw recomputing the same offer mean over the resampled sessions' offers;
  - `SE_c` its standard deviation over draws;
  - the family-wise critical value `q` = the 95th percentile over the **centred** draws of `max_c (L*_c - L_c) /
    SE_c` (one-sided 0.05);
  - Benjamini-Hochberg at 10 % beside, never selecting.
- **Kill B:** no cell with `L_c / SE_c > q` -- the family closes and the judged block is not read. Lambda was chosen on
  the same out-of-fold years, outside the maximum, so Kill B is somewhat laxer than one-sided 0.05 (m-3). The judged
  level is unaffected.
- **Reported for every cell, before the pick:** each fold's long share, the run lengths of the out-of-fold sides, and
  the variances of their 21-, 63- and 126-session mean side (sides only).
- **Eligible as the pick** (M2-4's margin): a cell whose population's worst choice year leaves at most 4 % unresolved
  at every R in {1, 1.5, 3} -- one point under the judged floor's 5 %, so the one judged read is not spent at the
  line. For a `filter` cell the worst year is taken over its filtered offers in 2021-2023 (m3-5).
- **The same estimand as stage C (m3-3):** `L_c` is the per-offer mean, `lift_bound`'s `sum(S) / sum(N)`.
- **The pick:** among the eligible cells above `q`, the one with the largest **first-order valued lift** at its lower
  limit `L_c - q SE_c`. This is a ranking that assumes a uniform lift over the cell's offers; C2 decides the money
  (section 13). The formula:
  - `$ a year = lambda_pts x min(u, cap(p, R)) x mean_dv(p) / 100`, maximised over the places that ask the cell's R:
    (b) the evaluation (any R), (c) the funded opening (R = 3 only), (d) funded later (R = 1 and 1.5), (e) paid (any R);
  - `lambda_pts` is the lower limit in percentage points; **u is the cell's offers a year on the choice block**;
  - `mean_dv(p)` and `trades_per_year_forward(p)` come from `u_value_map.csv` section `place_values`;
  - `cap(p, R) = trades_per_year_forward(p) x sigma(p, R)`, with sigma from section `records_leaf` (F-02's rule);
  - **base `p14`** (both stops are P-14's rungs).

## 12. Stage B2: the critical values, conditional on the judged sides (M2-2, M3-1, m2-2, E-035)

**Why it exists.** A model's sides can persist across sessions (its daily and multi-day features), and the pair values
can carry a persistent drift or follow effect. Their product then inflates any session-cluster test's real size: the
spurious-regression case. E-035 found that every single statistic, and even F-01's declared form, exceeds the family's
level on some real null. `cons` holds on every null Q-16 built. B2 adds a check, conditional on this family's actual
judged sides, for the persistence Q-16's nulls may not span.

**The statistic.** Every judging line (C1, C1-d, each C1-f, C2) is read by **`cons`** (`extended.lift_bound`): it
rejects only where all three of `t21w`, `t42w` and `t63w` reject (the trade-weighted per-offer mean with CR1 variance on
21-, 42- and 63-session blocks, df = non-empty blocks - 1), and its bound is their minimum. **Each component's critical
value is the larger of its nominal t and B2's simulated (1 - level) quantile of the same component** -- always, no
tolerance, no pretest.

**B2's null, at stage C, conditional on the pinned model's real judged side series.**

- **The sides.** The model's sides `s`, the filter's selection and the three twins' sides `f^r`, jointly, as read
  under `stage_C_sides` and hashed before any outcome.
- **The pair values.** Each null replicate `d*` is built from the choice block's own session pair-value vectors, at
  every table R, at the pick's stop:
  - resampled by a stationary bootstrap of mean block 63 sessions to the judged block's session count;
  - each judged session's offers take the drawn session's pair values at the same marks (a missing mark dropped);
  - centred (the replicate's grand mean removed);
  - plus **a declared slow drift** `a*(R) x rho_t`: `rho_t` a two-state Markov sign switching with probability 1/250
    per session (random start), and `a*(R)` the largest absolute calendar-year mean of the choice block's pair values
    at that R. This is probably conservative, since 2020-2023 holds 2020's crash and rebound and 2022's fall (n3-6).
- **For C1-f^r, a slow follow component centred at its expectation (M3-1):** `(g_t - g_r*) f^r_i`.
  - `g_t` switches between 0 and `2 g_r*` with probability 1/250 per session (random start), so its expectation is
    `g_r*` and the component's mean is zero. The third version's "recentred by its replicate mean" is dropped: read
    per replicate it made the statistic identically zero, read across replicates it under-represented the tail.
  - **`g_r*` is the largest of:**
    - **(a)** the twin's largest calendar-year lift over the coin on the choice block, at the pick's offers and
      bracket (read in B2: a recorded rule's choice-block outcome, disclosed);
    - **(b) the follow lift Stage 2 itself recorded for the twin on 2024-2026** (D-580, D-588, D-590, D-592), from
      its S1/S3 result files (`results/s1_sided_coin.csv`, `s3_event_kinds.csv`, `s3_latency.csv` with their
      manifests). This is a disclosed pre-read: it can raise the critical value but cannot choose anything;
    - **(c) three times (a)**, fixed now, used where the result files hold no 2024-2026 per-offer lift for the twin
      at a comparable R.
  - **Why the amplitude is taken that way (n3-6).** Stage 2 recorded the follow effect as strongest in 2024-2026, so
    the choice block's amplitude alone would understate the judged block's. The third review's check, and this
    draft's under `cons`, show that correct centring with too small an amplitude still over-rejects. The S1/S3 files
    are **not in the vendored snapshot**: they are added as a new snapshot under a decision row before the pin
    (E-002's rule).
- **Draws.** `default_rng([20261965, j])`, at least **1,000,000 replicates** per line (light in memory; CPU minutes to
  hours).
- **C2's B2 (m3-4)** runs after `stage_C_campaign` (section 13), with the realised routing's weights held fixed and
  `d*` at each trade's table R taking `a*(R_j)`.

**What the tests show** (`tests/test_family_b_b2.py`, synthetic, fixed seeds):

- on the second review's design and a slower stress design, B2 holds the level where the run-length surrogate and
  the nominal t do not (C1's form);
- under `cons`, at C1-f's boundary null (the twin's lift a slow two-state process, the model's equal on average),
  the nominal values over-reject. B2 centred at its expectation with an amplitude no smaller than the judged one holds
  the level; at half the judged amplitude, or with the third version's recentring, it does not;
- C2's dollar-weighted form holds under B2 where `cons`'s nominal values over-reject.

The scratch checks behind this section (the second review's resampling remedies found unable to certify the level from
one realisation; the long-block and stress-drift variants; M3-1 under `cons`; the opening-range recoverability), with
their printed output, are in `docs/reviews/scripts/family_b_drafter/` (m3-7). They are exploratory and select nothing.

**What it cannot see.** A slow drift slower or larger than declared, and a follow effect stronger than both (a) and (b).
The confirmation on unread data carries the decision against both.

**The side process's persistence, stated before the pin (E-035 (6)).**

- **What can make the side persist.** The model's side flips within sessions through its intraday features, and leans
  across sessions through its day-level and multi-day ones: 13 of the 37 are one value a day, the longest windows are
  20 sessions (`ret_20d`, the time-of-day medians) and 14 (`atr14`), and `atr_rel` and `atr_ratio` follow volatility
  regimes that can last months. So the side may lean one way for weeks to months.
- **What it is not.** This is not a regime filter (E-035 (6)'s warning case): the intercept cancels from the side
  (section 10), and nothing in the design holds a side for a quarter.
- **How it is measured.** Stage B reports the out-of-fold sides' run lengths and the variances of their 21-, 63- and
  126-session mean side. Stage C reports the same for the judged sides, before any outcome.
- **The flag.** The judged sides are **flagged regime-like** if the variance of their 126-session mean side exceeds
  half that of their 21-session mean side. The flag decides nothing, because B2 conditions on the real series, but it
  is reported with the verdict, and a regime-like side is said to reach power only with luck.

**The rotation gate (C1-r)** stays beside, deciding nothing. It cannot reach the family's level (its smallest p is about
1/(T - 124) on T judged sessions). On the second review's design it passed most spurious rejections at about twice its
own size. It refuses time-of-day seasonality as evidence (n2-1).

## 13. Stage C: judge the pick once, on the judged block (2024-01-02 to 2026-07-16)

**The order** (one clean run; the reader ledgers each purpose's read before it reads):

1. `stage_C_sides`: the sides, hashed;
2. B2 for C1, C1-d and C1-f;
3. `stage_C_judgement`: the pair values; C1, C1-d, C1-f;
4. `stage_C_campaign`: the gate campaign of designs (i) and (ii);
5. B2 for C2, conditional on the realised routing; C2 and the floors;
6. `stage_C_scorecard`.

The judge's inputs: the pinned model (its hash in the judge's manifest; the judge entry point cannot fit, T-7), the
pick's population (its stop's admitted marks after the as-of rule, section 3), its bracket and its use.

**The judged block's calendar (m3-2).** About **609 sessions** of kinds `n` and `b`, from the pinned calendars: 663
weekdays from 2024-01-02 to 2026-07-16, less 33 holiday or early-close days (`config/calendar_early_closes.csv`), one
defect day with no regular-session bars, and 20 FOMC days. The build counts it exactly from the store's `day_list` and
writes it in the result file. `cons`'s blocks come from `lift_bound.block_index`: G = n // b consecutive blocks covering
**every session, none dropped** -- on 609 sessions, 29 blocks of 21, 14 of 43-44 and 9 of 67-68 sessions (df 28, 13
and 8).

**The per-session values (m3-3).** For each line, the per-offer value `x_i` (below). Per calendar session `S_j` = the
sum of `x_i` over the session's offers and `N_j` = their count, every session counted, an empty one `S_j = N_j = 0`
(`lift_bound.session_sums`). The estimate is the per-offer mean `sum(S) / sum(N)`, stage B's estimand. A `filter` pick's
sessions without a filtered offer are empty sessions; `cons` counts only the non-empty blocks in its df.

**The follow twins.** For the three rules Stage 2 recorded, each read at the alert t (the five-minute latency) by Stage
2's own code imported unchanged (a zero is a tie, `f = 0`):

| twin | Stage 2's rule | read by | recorded at |
|---|---|---|---|
| `lnbar1x4` | the side of the most recent 1-minute 4-bar `nbar` event, followed | `s3_latency.lagged_day_sides` (L = 5) | S3 at L = 0 (D-588); **its lift persisted at L = 5** (D-592) |
| `lbrk5` | the side of the most recent 5-minute `brk` event, followed | `s1_sided_coin.day_sides` at the alert | S1 at L = 0 (D-580) |
| `mom15` | `sign(c[t] - c[t-15])`, followed | `s1_sided_coin.day_sides` at the alert (= `sign(ret_15)`) | S1 at L = 0 (D-580) |

**The design passes only if every line holds; a fail of any closes the family** (its reason in a decision row). Every
line is read by `lift_bound.bound("cons", x, session, n_sessions, level=0.05 / (k (k + 1)))`, with each component's
critical value replaced by the larger of it and B2's (section 12):

- **C1 -- the pass line (CHARTER section 3, E-008):** `x_i = s_i d_i`; the lower bound above zero.
- **C1-d -- drift-matched (D-12):** `x_i = (s_i - s_bar) d_i`, `s_bar` the pick's mean side on the judged block.
  **If `abs(s_bar)` is at least 0.9, C1-d fails.**
- **C1-f -- beyond each known follow effect (M-2):** for each twin r, `x_i = (s_i - f_i^r) d_i`, on the same offers
  (paired, one-sample), the weights the real joint judged sides. Three lines in an intersection-union, so the level
  holds and only power is spent.
- **No line is two-sample.** Every line compares two side rules on the same offers. A two-sample reading beside
  (for example, the lift on each session's first offer against the rest) uses `lift_bound.two_sample_bound` with the
  treated-cluster df (E-035 (2)).
- **C2 -- worth something where it is used, at the family-level bound (M2-3, M-3, m-10, m2-3, m3-4):**
  - **The routing.** The gate campaign of design (i) (section 14) on the judged block's sessions (`stage_C_campaign`;
    500 paths; seed 20261966; the bound arm, as Stage 2's U2 records) records, for every simulated trade j: the offer
    it took `i(j)`, the R the table took `R_j`, and its place `p(j)` -- (b) evaluation, (c) the funded account's first
    trade, (d) funded later before the first payout, (e) paid.
  - **The per-trade dollar value:** `v_j = mean_dv(p(j)) x s_i(j) x d_i(j)(R_j)` (`u_value_map.csv` base `p14`).
  - **The bound.** `cons` on the `v_j` -- each simulated trade on its judged session, so `S_j` is the session's sum of
    `v` over the paths' trades on it and `N_j` their count -- gives a per-trade lower bound at the family's level. It
    uses B2's critical values for this weighted form, the routing weights held fixed.
  - **The line: that bound times design (i)'s routed trades a year, at least $500 a year.** This is CHARTER section
    3's "at that bound", as F-02 prices it. The uses are the design's own routed trades on the judged block. C2 is the
    routed design's value whatever the cell's R; the cell's R decides C1 and the ranking.
  - **The coupling (m3-4).** The routing depends on outcomes: Stage 2's gate walks the judged trades. It does so at
    second order only: the gate draws each path's days independently (`propedge/campaign/gate.py`), so a trade's
    place depends on its own day's outcome only where that day recurs in a path. C2's B2 is therefore conditional on
    the realised routing. **Beside:** C2 priced at the places design (ii)'s coin-sided campaign routes, which do not
    depend on the model's outcomes.
- **The floors** (CHARTER section 3):
  - every offered R resolving on the judged block, at most 5 % in 2024, 2025 and 2026 to 07-16 (a calendar year with
    fewer than 63 sessions pooled with its neighbour, D-604);
  - the long-run gate -- growth on the required bankroll at the bound above zero (Stage 2 D-145) -- from the same
    campaign;
  - every firm rule verified (Stage 2's ledger);
  - conduct tier 1.

**Beside, deciding nothing:**

- **The opening range partialled out (E-036; M3-2).** The pick's lift with the opening range's net move partialled out
  of its sides:
  - the pinned model's score `z` on the choice block is regressed (ordinary least squares, one regression over all
    admitted alerts) on three opening-range quantities, computed from the bars at each alert:
    - the 30-minute range's net move `(C[08:59] - O[08:30]) / atr14`;
    - the 60-minute range's `(C[09:29] - O[08:30]) / atr14`;
    - the distance of `c` to the half-hour's VWAP, in `atr14` units;
  - these three are fitted values of a beside reading, inside the walk-forward on the choice block (E-031 (1)), and
    pinned with the model. They read the half-hour's bars, which no feature does and a reading may;
  - on the judged block, `z_res = z - (fitted combination)` and the partialled side `sign(z_res - median(z_res on the
    choice block))`;
  - reported: its lift over the coin by `cons` at the family's level and at 0.05, the share of offers whose side
    changes, and the lift of the since-open follow rule `sign(d_pdc - gap)` at the alert;
  - **if C1 passes but the partialled lift's 95 % bound is not above zero,** the carrying row says that the pass is
    carried by the opening range's net move.
- the lifts in net R; the lift by calendar year, the year-by-year readings E-031 (2) puts in the reverse walk-forward's
  place; the lift on each session's first offer, and C2's place-by-place parts;
- the judged share through a `filter` pick's threshold and the MDL recomputed at it (m3-5);
- the judged sides' persistence and the regime-like flag (section 12);
- the seeded coin twin (`[20261964, 0]`);
- a model fitted on the three twins' sides alone, on the choice block, applied to the judged block, and the lift over
  it;
- C1-r (section 12);
- the lifts with Stage 2's breakeven move and with Q-20's corrected move;
- the resolution model's judged AUC;
- the denial ladder and the placement on in the scorecard.

**Dropped (E-031 (2)):** the reverse walk-forward.

## 14. The journey scorecard -- beside every judgement, never the pass line (CHARTER section 2; E-008, E-014, E-015)

**The design** (the pick's only; a family closed at Kill B runs none):

- Stage 2's RC runner (`rc_dev_test`: P-14's design -- the no-closure state table, the strict router, five seats, the
  purchase budget, the fees, the R of every trade set by the table), with this family's offers at the pick's stop as
  its cell:
  - **(i) at the model's sides** (a `filter` pick: only the filtered offers);
  - **(ii) the same offers at the coin's sides** (Stage 2's coin, seed 20261102 per date and mark, D-521).
- **The walk (n2-7):** both designs carry **the family's fixed walk** (section 6), so (ii) is the within-walk
  comparison that isolates the side. P-14, read beside, carries Stage 2's breakeven move, so the comparison with R\*
  crosses walks, as the scorecard says.
- **The runs:** the gate campaign at seed 20261966, 500 paths, the verdict arm, payout denial 0 %, the placement off.
  Journeys by the vendored U1 replay and Q-17's adapter (`extended/user_beside.py`).
- **Identity first, refusing:** the runner with P-15's own cell reproduces P-15's registered rows and U1 start rows
  (Q-22, E-026 (1)).

**On which starts (m2-5):**

- **the judged block's starts** (`stage_C_scorecard`), labelled as such;
- beside, 2021-2023's starts at the inner folds' out-of-fold sides, **their journeys truncated at 2023-12-29** and
  labelled so (m3-6) -- a choice-block read; no read for a choice purpose reaches 2024;
- 2020 is not read for it (in-sample).

**Read against R\* = P-14 and against design (ii):**

- **P** and the guarded measures S1, S3a, S3b, S3c (with its components), S4a, S4b, S5a, S5b, S5c; the reported-only
  S2, S3d, S6, Q (`vendor/stage2/docs/USER_MILESTONES.md`);
- **the journey variables (E-014):**
  - sessions and cash to the first pass;
  - sessions and cash to the first payout;
  - **sessions to break-even** (the first session whose cumulative net cash is at or above zero, daily), the share
    reaching it by months 1, 2, 3, 6 and 12, and the share that later fall back below zero;
  - **the path's evenness** -- the share of months with a positive net change, the longest run of months without a
    payout, the spread of monthly net, the deepest fall from the running high after break-even, payouts per month,
    and the largest single month's share of the year's payouts;
- **every measure as a distribution over start days** (median, p10, p90), with its uncertainty from the effective
  number of independent starts and the start day's share of the variance (`user_drivers.csv` section `design_vs_luck`);
- **the frontier** on P, S1, S3a and S5a (`user_drivers.csv` section `frontier`'s form);
- **the menu: E-015's limits, once approved by the operator**, as flags only (a limit never fails a design, E-015 (3));
- **the evenness trade-off curve** beside (E-015 (4));
- **E-007 (e)'s readings:** the denial ladder (10/25/50 %; E-013 (1)), the placement on, the binding Focused Trader
  models, P by month, mean net, CVaR10, P under a bankroll limit, the effective sample size and the minimum detectable
  difference before the read;
- Stage 2 D-621 (3)'s rule against P-14, beside as E-008 keeps it, deciding nothing;
- **not modelled, said wherever the scorecard appears:** a user who stops when their own money runs out, the user's
  time, taxes.

The resolution model as a filter (offers predicted fast, at the coin's side) is a second design read beside -- a supply
and speed reading for the journey, never a pass (E-023: a coin-side filter is judged only by its own family).

## 15. What a pass and a fail mean (m-8, n-7)

- **CARRIED** (every line of stage C and the floors) is a development finding on a late-development block.
  - It takes a registration id, a model card (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`), its registered
    development test through the gatekeeper, the auditor, and **one confirmation** (section 16), which carries the
    decision (D-189).
  - **If the family was declared a screen** (section 8 item 8), a pass is still CARRIED, and the carrying row says the
    development read was a screen at its MDL ratio.
- **CLOSED** at stage A (no cell survives), B (Kill B) or C (any line or floor), the reason in a decision row.
  - A close at B or C reads **"no lift above the MDL at this family's level"**, never "no lift".
  - Where a check (not a kill line) failed, the failure protocol applies.
- **The closure binds** (D-277's boundary; the audit 1.5 (c), R-8). A later family on these features or this population
  (the dropped tree among them):
  - names this closure;
  - says what changed and why it is a different hypothesis;
  - **is not judged on this family's judged block** -- it goes to data this family did not read.

## 16. The confirmation, declared before any development read (M-6; F-02's form)

- **The window.** NQ from **2026-07-17** (`config/windows.yaml`, `reserve`), not on disk, never read until a carried
  candidate is registered.
  - It is **a purchase, the operator's**, and NQ's **fourth** confirmation window, **the operator's decision** (D-107,
    D-461).
  - The reader refuses it outright today; reading it needs the lead's row and the reader's extension when bought.
  - Stage 2's draft P-16 confirmation and F-02's draft target the same window. If any test reads it first, the lead
    records that before registration, and the operator decides.
- **What it tests -- the pick's trades, not P** (every rule, the pinned model and the stop's admitted marks as fixed):
  - C1, C1-d (with its 0.9 rule) and the three C1-f on the window's offers, each **one-sided at the registered 0.05**;
    the bound at 0.05/N beside (D-189's form);
  - **by `cons`'s 21-session component `t21w`** (`lift_bound.bound("t21w", ...)`). On six months `cons`'s 42- and
    63-session components would have three and two blocks. B2's critical value is re-simulated at the window's length
    (`[20261965, 10 + j]`); on the second review's design that form holds the level within Monte Carlo error
    (`tests/test_family_b_b2.py`);
  - C2 at the 95 % bound -- the window is too short for its own campaign, so it is valued with stage C's per-place
    shares and uses -- at least $500 a year;
  - resolution at most 5 % on the window, overall and in every calendar year with at least 63 sessions (a stub year
    pooled, D-604);
  - the rotation reading beside if the window holds at least 224 sessions;
  - draws of a statistic, if any: `[20261967, 1]` (`t21w` draws none).
- **What it cannot test: P.** Six months is about 126 sessions; no interval on P exists there (the red team's M1). The
  scorecard on the window is descriptive, without an interval, never a line.
- **How much data:** at least six months (D-604), and at least the months at which the pick's expected offers reach the
  session count where the confirmation's test, one-sided at 0.05, has 80 % power for a lift equal to **the pick's
  judged lower bound at the family level**.
  - The expected offers are the lower of its two blocks' offers per session x 21 a month.
  - The months are computed when the pick is carried and **written in the carrying row**, before any confirmation data
    exist.
  - If that is more than the operator will buy, no confirmation is registered and the pick stays a development
    finding.

## 17. Parameters: fixed / searched / dropped

| parameter | what it is, in a phrase | class | value | source |
|---|---|---|---|---|
| market, bars | what is traded and read | fixed | NQ 1-minute bars (Databento, raw, one contract a day); MNQ micros sized by the table | E-002; handoff 2.2 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md; `config/windows.yaml` |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | feature-rules 4; CHARTER 3 |
| the excluded window | bars no used feature may read | fixed | 08:30-08:59 CT of the alert's day | E-024 (5); D-281 (3); the audit 1.2 (3) |
| alerts | when a side is computed | fixed | 10:05 .. 15:00 CT every 5 min | section 3 (every window clear of the excluded bars) |
| entry marks | when an order is placed | fixed | t + 5 = 10:10 .. 15:05 CT | D-266 |
| the cutoff | which entry marks are offered | fixed rule, values read on the choice block | D-525 (4) per mark, kinds only, both sides, every table R, **every choice year** | M-5; M2-4 |
| excluded days | not traded | fixed | FOMC, early closes, empty days (Stage 2's day kinds); the first 22 sessions | D-525, D-533; E-029 |
| the as-of rule | a row whose as-of reads fall in the half-hour | fixed | dropped and counted | m3-1 |
| entry | how a trade starts | fixed | market at the open of the first bar at or after t + 5, one tick as a cost, by hand | D-266; E-008 |
| stops | the loss distance | fixed | 12.5 and 25 points (50, 100 ticks) | P-14's rungs; above the cost floor; F-02 6.3 |
| R | target over stop, where read | fixed | 1, 1.5, 3 | handoff 2.5; `records_leaf` |
| training R | the label's bracket | fixed | 1 | section 6 |
| the walk | how a trade ends | fixed | Stage 2's end and flatten, fixed barriers, no breakeven move | section 6; E-011 |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| features | what the model sees | fixed | 37 of `extended/features.py` (sha256 at pinning) | section 7; M2-1 |
| preprocessing | scaling inside the fold | fixed | winsorise 0.5/99.5 %, standardise, `dow` indicators, `m_cross`, impute 0 | feature-rules 4 |
| model | the classifier | fixed | L2 logistic, session-weighted, L-BFGS-B, gtol 1e-10, 2,000 iterations | the brief (one of its two) |
| **lambda** | how hard the coefficients are shrunk | **searched** | 0.25 x 10^(j/2), j = -2..4; inner walk-forward 2021-2023; out-of-fold log loss | R-7; C-1 |
| side rule | prediction to side | fixed | long if p > p~, short if p < p~; p~ the model's own training median | C-1; n2-2 |
| filter | how confident to trade | fixed | abs(p - p~) at or above the model's own training 80th percentile | M2-5 |
| resolution target | speed of resolution | fixed | first touch of entry +- S within the training median | handoff 3.3 |
| stage B | the family-wise screen | fixed | offer-mean lift; stationary bootstrap, mean block 63, 2,000 draws, centred, studentised, one-sided 0.05 | m-2; M2-2 |
| pick eligibility | a margin under the judged floor | fixed | worst choice year at most 4 % unresolved at every R in {1, 1.5, 3} | M2-4 |
| the lines' statistic | how every line is read | fixed | `cons` (`extended/lift_bound.SHIPPED`: `t21w`, `t42w`, `t63w` all required, blocks by `block_index`, no session dropped); `t21w` on the confirmation | E-035; m3-2 |
| stage B2 | the critical values | fixed | per `cons` component, conditional on the judged sides; choice-block pair values in stationary 63-session blocks, centred, plus a 1/250 slow drift at `a*(R)`; for C1-f a follow component `(g_t - g_r*) f`, `g_r*` the largest of the choice block's yearly lift, Stage 2's recorded 2024-2026 lift and three times the former; at least 10^6 replicates; the larger of nominal and simulated, always | M2-2; M3-1 |
| C1 | the pass line | fixed | `mean(s d)` at 0.05 / (k (k + 1)) | E-008 |
| C1-d | against drift | fixed | `(s - s_bar) d`; fails if abs(s_bar) >= 0.9 | D-12; C-1 |
| C1-f | against the known follow effects | fixed | `(s - f) d` for `lnbar1x4`, `lbrk5`, `mom15` at L = 5 | M-2; D-592 |
| C2 | the least worth | fixed | $500 a year at the family-level bound, by `cons` on the per-trade dollar values of design (i)'s routed trades, B2 after the campaign; judged-block uses | M2-3; M-3; m3-4 |
| the partialled reading | the opening range's net move taken out of the sides, beside | fixed | least squares of the score on the 30- and 60-minute ranges' net moves and the VWAP distance, fitted on the choice block | E-036 |
| the regime-like flag | the side's persistence, reported | fixed | the variance of the 126-session mean side above half that of the 21-session | E-035 (6) |
| valuation base | where a win is priced | fixed | `p14` | `u_value_map.csv` |
| MDL factor | when the family is only a screen | fixed | 3 | R-16 |
| judged-block purposes | what the judged block is read for | fixed | `stage_C_sides`, `stage_C_judgement`, `stage_C_campaign`, `stage_C_scorecard`, once each | E-026 |
| the 37.5-point stop | P-16's rung | **dropped** | -- | its R = 3 does not resolve after 09:00 on Stage 2's rows (M2-4) |
| the opening half-hour's bars and every feature reading them (10) | the opening range in substance | **dropped** | -- | M2-1; E-016 (2); D-281 (3) |
| since-09:00 session features | a redefinition | **dropped** | -- | new features after a review; the 60-minute windows carry the recent session |
| per-feature masks from 09:05 | another way to exclude | **dropped** | -- | the inputs would vary by mark; section 3 |
| D-641's R cap | another way to resolve 25 points | **dropped** | -- | removes the funded opening's 3R ask |
| the run-length surrogate; the rotation gate as a line | v2's B2 and C1-r | **dropped** (C1-r beside) | -- | M2-2 |
| the reverse walk-forward | a beside reading | **dropped** | -- | it fits on the judged block, which the reader refuses (E-026) |
| the shifted-label alignment control | v2's m-5 | **dropped** | -- | not a null (m2-1); replaced by the join assertion and T-14 |
| the breakeven move | Stage 2's stop move | **dropped** (beside) | -- | fixed barriers; Q-20's defects |
| gradient-boosted tree | the brief's other model | **dropped** | -- | not installed; more freedoms; a tree is another family |
| R 0.25, 2, 2.5 as cells | the table's other offers | **dropped** | -- | the three asks are where the value map prices; fewer cells |
| resting entries; overnight alerts | other mechanisms and sessions | **dropped** | -- | family A's mechanism (F-02); US hours (handoff 3.1) |
| interactions, feature selection, class weights, early stopping, seed refits, a filter-fraction search | other model freedoms | **dropped** | -- | each a hidden search (the audit's P-5 (a)) |
| rules read off the model (SHAP and the like) | explanations | **dropped** | -- | exploratory, their own family (bootstrap 6.3 B) |

## 18. The count, the family number and the level (R-17's words)

- **Cells:** k_cells = 2 x 3 x 2 = **12**, each counted whether killed or read (the six 25-point cells possibly
  killed at K1, section 3).
- **Searched configurations:** lambda's 7 values x 2 stops x 2 targets = **28**, each evaluated and counted.
- **Recorded in the result file and the trial count:** 12 + 28 = **40**. Not trials, since nothing is chosen from them:
  the controls (the canary, the join assertion, B2's replicates), the twins and the readings beside.
- **The family number:** k = the next free in the program (**11 if pinned next**; F-01 spent k = 10, E-007 (a)). If
  F-02 is pinned first, this family's k is the gatekeeper's count. The level is **0.05 / (k (k + 1))**.
- **One cell reaches judgement;** its lines are an intersection at one level; stage B spends nothing of the program's
  budget.
- **The program's honesty sentence (P-2):** the development level is a screening threshold; the decision is carried by
  one confirmation on unread data (D-189).

## 19. Seeds -- proposed 20261960-20261969, checked unique (T-12), for the lead to confirm at pinning

| seed | what it draws |
|---|---|
| 20261960 | stage A: `[20261960, 0]` the positive control's bootstrap; `[20261960, 2]` the MDL's sign-flip nulls |
| 20261961 | the null canary: `[20261961, 0]` its block swaps, `[20261961, 1]` its 10,000-draw centred bootstrap |
| 20261962 | stage B's bootstrap `[20261962, 0]` |
| 20261963 | a tie p = p~ (the coin) |
| 20261964 | the seeded coin twin beside |
| 20261965 | stage B2's replicates `[20261965, j]`; the confirmation's re-simulation `[20261965, 10 + j]` |
| 20261966 | the gate campaign of designs (i) and (ii): C2's routing, the long-run gate floor, the scorecard; 500 paths |
| 20261967 | draws of a statistic, if any: `[20261967, 0]` stage C, `[20261967, 1]` the confirmation (`cons` itself draws none) |
| 20261968 | the build's tests: `tests/test_family_b_side_rule.py` (`[20261968, 0..3]`), `tests/test_family_b_opening_range.py` (`[20261968, 20..29, 33]`), `tests/test_family_b_b2.py` (`[20261968, 30..32, 40..41, 60..63]`), T-3's synthetic judged block (`[20261968, 50]`), the drafter's scratch check `m32_r2.py` (`[20261968, 70]`) |
| 20261969 | the planted-effect test (T-14) |

**The check.** On 2026-11-16, `grep -rIowh --exclude-dir=.git -E "2026196[0-9]" .` over the whole working tree (the
vendored snapshot and its results included) found these seeds only in this file, its three tests, the drafter's scratch script `m32_r2.py`, and the rows and
review that record the earlier drafts. Family R's draft lists them as F-B's.

- The neighbouring blocks are taken: 20261910-19 (Q-16), 20261920-29 (Q-17, Q-20), 20261930-39 (F-02), 20261940-49
  (F-P), 20261950-59 (Q-18).
- **Inherited, used only as their owners registered them:** 20261102 (Stage 2's coin, design (ii)); 20261131 and
  20261206 (the identities, E-002); 20261700 and 20261600 + i (D-621 (3), beside); Q-16's 20261913 and 20261914
  inside `lift_bound` (unused by `cons`).

## 20. The build's identities and tests (Q-14, after the pin, before any reading)

All of the family's code is committed after its pin (T-9); fast tier unless marked.

1. **The walker:** E-011's identity holds at the build's commit. With the move off, P-16's trades that resolve before
   their first session open after entry are walked identically.
2. **The features:** Q-11's tests pass at the pinned `extended/features.py`, the slow tier's 790-cut shift test
   included (heavy under E-024 (4)'s lock rule). **`tests/test_family_b_opening_range.py` passes:**
   - the 37 read no bar of the half-hour at any admitted alert;
   - the disclosed identity holds;
   - the opening range's width and position are not linearly recoverable;
   - the as-of rule flags exactly the rows that read it.
3. **The as-of rule, refusing (m3-1).** At the feature build, every admitted (session, alert) row is checked: the
   bars the 37 read as of `s - 1`, `s - 6`, `s - 16`, `s - 31` and `s - 61`, and the day's first bar, lie outside
   08:30-08:59. A failing row is dropped and counted in `supply`, never kept. `or_free_rows` in the test file is the
   reference.
4. **The cutoff:** `mark_resolution` called on this family's own walks per choice year, kinds columns only.
5. **The twins:** `lagged_day_sides` and `day_sides` imported unchanged. At L = 0 they reproduce S1's and S3's side
   tables on P-16's marks (Stage 2's `shift_problems`). At the alert they read only bars ending at or before t.
6. **The logistic:** agrees with a Newton solve of the same objective on synthetic data to 1e-8, and recovers a planted
   coefficient. `tests/test_family_b_side_rule.py` passes, the intercept identity included.
7. **A planted effect (T-14) -- the proof of alignment and of size:**
   - on synthetic bars with a direction effect of known size tied to a feature, the whole pipeline (the join
     included) recovers it with the right sign, and `cons`'s bound covers it at its level;
   - C1-f against a twin carrying the same effect does not pass;
   - on a driftless walk the lift is zero within its interval;
   - a planted look-ahead feature fails the shift test;
   - a deliberately misaligned join is refused;
   - a planted opening-range-follow effect (a drift in the direction of the half-hour's net move) is recovered by C1,
     and the partialled reading (section 13) removes it.
8. **Stage B2:** `tests/test_family_b_b2.py` passes -- C1's form on two designs, C1-f's boundary null and C2's
   weighted form under `cons`. The full B2 at the family's level on the second review's design rejects at most the
   level at 10^6 replicates (heavy, under the lock).
9. **The place-recording adapter (C2).** Re-running P-16's registered gate campaign as U2 did (100 paths, the bound
   arm, its seed) records trades by place whose counts reproduce `u_value_map.csv`'s `trades_per_year_records` for
   `p16`, and P-14's for `p14`.
10. **Choice-stage invariance (T-3, heavy, under the run lock):** stages A and B and the final model are byte-identical
    when every judged-block bar is replaced by a seeded synthetic walk (`[20261968, 50]`).
11. **The judge cannot fit (T-7)**, and the reader refuses its fitting or choosing purposes on the judged block (E-026);
    the judge's manifest names the pinned model hash and the sides' hash.
12. **The scorecard's identity:** the runner with P-15's cell reproduces P-15's registered rows and U1 start rows
    (Q-22, E-026 (1)).
13. **The judged calendar:** the session count from the store's `day_list` (kinds `n`, `b`), written in the result
    file, and `cons`'s block counts from `lift_bound.block_index` at it.

## 21. Outputs

- `results/fb_model.csv` (sections `supply`, `resolution`, `controls`, `power`, `search`, `choice`, `sides`, `persistence`,
  `b2`, `judged`, `partialled`, `beside`) and `results/fb_scorecard.csv`.
- Each with its sidecar manifest (`extended.results.write_result`); the pinned model's hash and the judged sides' hash
  in the judged manifest; the reader's ledger lines for each judged purpose.
- Run once from a clean checkout of a named commit (`scripts/run_clean.py`), the heavy steps under the run lock.

## 22. Open before the pin -- the lead's and the operator's

**The operator's** (a ruling, never a research question sent to them; until ruled, the safe default stands):

1. **D-281 (3).** Whether any family may read or trade the 08:30-09:00 half-hour's bars. Default: no. The lead ruled
   this family's residual -- the net move across the half-hour, computable from closes on either side -- outside the
   closed branch (E-036); the operator may still rule otherwise.
2. **E-016 (2), the two opening-range features.** Out until ruled.
3. **NQ from 2026-07-17** as a fourth confirmation window (D-107, D-461), and its purchase -- only once a pick is
   carried.

**The lead's, before the pin:**

4. **Stage 2's S1/S3 result files vendored** (`results/s1_sided_coin.csv`, `s3_event_kinds.csv`, `s3_latency.csv`
   with their manifests), as a new snapshot under a decision row (E-002), for the follow amplitude's part (b)
   (section 12).
5. **Q-55**: Q-16's calibration rerun from a clean checkout (E-035 (4)), before any of its figures is cited -- this
   file cites none.
6. **The place-recording adapter** for C2 (build item 9).
7. **The seeds** (section 19) confirmed unique at pinning.
8. **The family number:** F-02 may be pinned first.
9. **A fourth red-team read** of this version.

(Done since the third version: E-019's sentence on D-281 (3) corrected by E-030; the fitted-values row written by
E-031 (1); Q-16 merged and `cons` adopted by E-035 (n3-3).)

## 23. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and recorded
in its own decision row -- never added to this file once pinned.)*
