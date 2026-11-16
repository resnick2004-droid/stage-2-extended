# F-03: a side-free timing filter for the funded account's 3R opening (family O)

**Status: declared before anything of it is built or read.** It is pinned by the sha256 of its LF text in its decision
row. Nothing declared is edited: a change is a new family under a new row. No bar, walk, trade or result value has been
read for it, no state computed, nothing fitted and no outcome of any trade computed. The code it carries is synthetic
tests: `tests/test_family_o_persistence.py` (T-1) and `tests/test_family_o_toys.py` (slow tier, T-15; 18.3).

**Its text's history.** It was drafted and reviewed as `prereg/DRAFT_F-O_opening_timing.md`:
- commits a39a80a (Q-37, E-039), cd2cbe7 (Q-63, E-046), 0ae90d5 (Q-87, E-071) and this text (Q-87c);
- two red-team reads (`docs/reviews/DRAFT_F-O_opening_timing_2026-11-16.md`,
  `docs/reviews/DRAFT_F-O_opening_timing_v2_2026-11-16.md`) and the prereg-gatekeeper's refusal of the third text
  (E-073), each answered in section 0 (0.2, 0.3, 0.4).

At the pin the file is renamed `prereg/F-NN_opening_timing.md` (NN the F-number the gatekeeper assigns; the reader's
`DECLARATION_PATH`) and `F-XX` becomes `F-NN`; nothing else changes. **This file writes no program family number k:**
the pinning row names k (k >= 12), the commit and the sha256 it pins, and the cells 6.6's drop rule drops.

**Its rules come from the operator's ruling of 2026-11-16 (E-023; `CHARTER.md` section 3, "Levers that do not choose a
side").** The filter keeps the coin's side and chooses *when* a newly funded account takes its opening, so E-008's lift
over the coin twin is zero by construction (E-021 (1)). It is a filter of E-023 (2): tested at the trade level against
a **placebo-selection twin**, one-sided at the family's level by the calibrated statistic E-035 (2) adopted, valued at
that bound, with section 3's floors and the journey scorecard beside. It can be carried.

**The pin's conditions -- external only (E-052 (2); E-073 item 1).** It is pinned only if all three hold:
1. **Q-55's clean rerun** of Q-16's calibration (E-035 (4)) reproduces `cons`, and the treated two-sample `cons`,
   holding on the selection nulls; and **6.6's drop rule is applied to its result file by the lead at the pin**, the
   dropped cells recorded in the pinning row (no figure of Q-16 is cited before that rerun, or typed into this file);
2. **Q-83's fresh-seed validation HOLDS** on E-052 (2)'s criterion (its fresh seeds are that row's, not written out here,
   as that run checks them unused before it starts): at every k in 11..15, no real or realistic null's 95 % interval
   lies wholly above nominal;
3. **the family number** is assigned.

**The withdrawal clause (m2-8; E-052; E-054 (2)).** If Q-55's clean rerun does not reproduce `cons` and the treated
two-sample `cons` holding, or if Q-83 does not hold by E-052 (2)'s criterion, this text is **withdrawn before any read**,
to be re-declared under a new row, and nothing of it runs. **The pass-line code is pinned by git blob id:**
`extended/lift_bound.py` `984f3467a4a05aa790d3ea43e94ac7761f0725b2` and `extended/p_bound.py`
`f5b29710e243f97a2795e57f6458512fea99199b` (E-052; the same bytes since Q-16, merged 4d3e503); every run of this family
refuses a commit whose blobs of those two files differ (A1). A changed module is a new row and a new family.

**Before run 1, not before the pin (the pre-run conditions; E-073 item 1, the lead's choice).** Declare before
building: nothing of this family is built or run before the pin. After the pin and before run 1, in this order, each
refusing: **the infrastructure identities** -- Q-89 (Q-70's place records at 100 paths), Q-93 (Q-76's class on the U1
replay), Q-101 (Q-94's replay recorder, E-068) and Q-80 (the gate's 500-path identities, E-049) -- on record as holding;
then **this family's build** (the seam and its tests, 18); then **A0**, the whole-window identities in
`identity/family_o_identity.py` under their own identity row; then run 1, which opens with A1 (9, 19.2).

Where the funded openings fall (Q-35; its script merged, E-051 (2)) is not needed before the pin: it is counted in stage
A, on the choice block, in history's order (5.5).

| field | value |
|---|---|
| family | O: a side-free timing filter for a newly funded account's 3R opening -- the opening keeps P-16's coin side and waits, at most W sessions, for a state that predicts persistent moves |
| id | F-03 (`prereg/F-NN_opening_timing.md` at the pin) |
| program family number k | **written in the pinning row only: the next free at the pin, k >= 12** -- F-01 spent 10 (E-007 (a)); F-02 holds 11 (E-045 (4)); family B's draft is ahead of this one; family R's draft is held unpinned (E-028 (2)); described readings take none (E-023 (1)) |
| level | one-sided **0.05 / (k (k + 1))** at the pinning row's k: 0.05 / 156 at k = 12, 0.05 / 182 at k = 13, 0.05 / 210 at k = 14, 0.05 / 240 at k = 15 |
| the pass-line code | `extended/lift_bound.py` blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2`, `extended/p_bound.py` blob `f5b29710e243f97a2795e57f6458512fea99199b` (E-052) |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16 only, read through `extended/reader.py` (E-026 (2)) |
| base | P-16 (`rc_s150_all_nr`, `vendor/stage2/prereg/P-16_rc-s150-all-nr.md`) as registered, its report-day 07:35 entry kept (E-039 (1)); R\* = P-14 beside |
| population | P-16's offers at the marks 17:00-08:25 CT of its walked sessions (on a BLS report day 07:40-08:25: the entries this family chooses are strictly after 07:35:00, E-007 (d), E-039 (1)), each walked long and short at 3R (section 5.2) |
| choice block | sessions 2020-01-02 to 2023-12-29. Stages A and B read 2021-01-04 to 2023-12-29; 2020 is the states' warm-up and u3's first training fold |
| judged block | sessions 2024-01-02 to 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`config/windows.yaml`, `reserve`); not on disk, a purchase (section 15) |
| cells (`k_cells`) | **4**: s1, s2, s3, u3 -- each at R = 3, the 150-tick stop, place (c), W = 5 sessions: 4 x 1 x 1 x 1 = 4, each counted whether dropped at the pin (6.6), killed or read |
| judged | one cell: stage B's pick |
| pass line | E-023 (2), every line by **`cons`** with the treated-cluster df (`extended.lift_bound`, E-035 (2)) and each member's critical value the larger of its t and stage B2's: **C1**, the offer-level lift of the in-state offers' stratum-centred side-symmetric 3R value over the twin (`placebo_selection_bound`); **C1-close**, the same under the `close` flatten convention; **C2**, the per-opening difference between the design's openings and the twin design's (`two_sample_bound`), on the U1 replay in history's order, priced at place (c) at the design's openings a year, at least $500 a year; **C3**, both sides' halves above zero; section 3's floors; the scorecard beside. **Before any of them, K0** (E-052 (1)): `cons`'s size at the family's level on a sign null built with each cell's own counts, a cell lax by it killed, a pass on lax judged counts not claimed (9, A11; 12) |
| the wait W | 5 sessions, fixed (section 5.4) |
| seeds | proposed 20261980 to 20261989, checked unique (section 16) |
| model card | only if u3 is the pick (its forecast's 11 coefficients, section 6.5); none otherwise |

---

## 0. In plain words (for the operator)

**Where a win is worth most.** A newly funded account's first trade -- its opening -- is where one more win is worth the
most to a user (Stage 2's value map, `vendor/stage2/results/u_value_map.csv`, section `place_values`, place (c)). P-16
takes it at the first offer the router hands the account, with the coin's side and a target three times the stop (3R).

**What this family changes.** Only *when* the opening is taken. A newly funded account waits -- for at most five
sessions -- for a moment when the market's moves tend to keep going rather than turn back. If no such moment comes in
five sessions, it takes its next offer, as P-16 does. The side is still the coin's. Nothing else changes.

**Why waiting could help, and only at 3R.** On a market without memory, a coin-sided trade with a target three times
its stop wins one time in four, however busy the market is. Busier markets only make it finish sooner. But if moves
persist, a trade that starts moving the coin's way tends to reach the far target, and the coin wins more than one time
in four. At a target equal to the stop (1R) persistence cannot help the trade's gross result: the long and the short of
the same path are mirror images. So persistence matters most at the opening's 3R.

**The four moments it can wait for** (each a separate, counted test, chosen from published work before any data):

- **(s1)** the night has been busier than its forecast (an unexpected rise in volatility);
- **(s2)** the night has already moved far in one direction against its expected range (a trending night);
- **(s3)** the day is forecast calm (low predictable volatility);
- **(u3)** family R's "fast" moment, a forecast that the trade will finish quickly. **Stated now: this one is expected to
  win less, not more**, because markets that are predictably busy tend to turn back (the "LeBaron effect").

Some of these moments last for weeks (a calm spell); others come and go within a night. A moment that lasts weeks gives
too few independent tries on the data we have to be judged at all, so the file says, for each, how long it is expected
to last and whether the data can judge it, before anything is read (section 6.6).

**How it is judged (the operator's rule, E-023).** The waiting account's choice is compared with a *random* choice of
the same number of offers at the same times of day, on the same kinds of day, in the same years. The family passes
only if:

- the chosen offers do better than random ones by more than chance, at the family's strict level, and still do when the
  model's cautious price for a trade cut off at the close is replaced by the close itself;
- the openings the design actually takes do better than the openings a random waiting rule takes, replayed day by day in
  history's order, by enough to be worth at least $500 a year;
- both the long side and the short side do better (so a market rising for years cannot pass it by itself);
- every floor holds: trades resolve, the long-run gate, verified rules, conduct.

**Expected.** The published evidence is on the S&P 500 and at other time scales; nobody has shown it on NQ at a
bracket held for hours. The honest prior is no effect, and the data may only be enough for a screen (section 9, A9). A
"no" is a valid close. What a user would feel (the wait, the journey) is shown beside, never as the pass line.

## 0.1 Where the brief's items are answered (Q-37's brief)

| the brief's item | where |
|---|---|
| the opening keeps P-16's coin side and waits at most W sessions (declared) | 5.4 |
| the states s1-s3 and family R's (u3), its sign stated in advance, each a counted cell | 1 (iv), 6.3, 17 |
| judged against the placebo-selection twin | 7, 11, 12 |
| valued at place (c) on the openings' own offers | 7.4, 10 item 4, 12 (C2) |
| the journey scorecard beside | 13 |
| prior exposure: Stage 2's S2, the effect atlas's O and R families, S1 and S3 | 2 |
| features only from bars closed by the alert; the library where it serves; no 08:30-08:59 bar of the alert's day (E-030; E-036 M3-2) | 6.1, 6.2, 6.5, 18 (T-2) |
| fitted values only inside the choice-block walk-forward (E-031 (1)) | 6.5 (u3's forecast, the only fitted values) |
| no reverse walk-forward (E-031 (2)) | 8 (dropped), 12 (the year-by-year readings beside instead) |
| the `Judged-block reads:` line (E-026), checked with `extended.reader.declared_purposes` | 19.1; T-1 |
| seeds proposed in 20261980-20261989, checked unique | 16 |
| k the next free | header; 17 |
| where the funded openings fall: counted in stage A, direction-free, on the choice block; what changes if they mostly fall in the opening window | 5.5, 9 (A2) |

## 0.2 What the second version corrects (the red team's first read; Q-63's brief)

| finding | what changed | where |
|---|---|---|
| **F1** the pass line's statistic | C1 and C1-close by `cons` through `extended.lift_bound.placebo_selection_bound` with the treated-cluster df, on the **stratum-centred** values c - mu_g (the function has no strata; every population offer is sample 2, so the twin's expectation is the population mean of the centred values, zero); C2 by `cons` in the module's two-sample form, `two_sample_bound` (its non-nested case, the same statistic E-035 (2) adopts); 7.2's raw session series z_s dropped as a variance series; **B2's critical value defined per member** (t21w, t42w, t63w each at the larger of its t and its B2 quantile; `cons` passes only if all three do); **what Q-16 calibrated** (the coin side's own outcome, not the side-symmetric value) and what follows: the level on c rests on B2 and is checked by a new choice-span control (A10); a synthetic test of the centring identity (T-1) | header, 7.2, 7.4, 9 (A10), 11, 12 |
| **F2** the wait's calendar | stage A's counts, K5, V_B and V are read on **the U1 replay in history's order** (Q-17's adapter), never on the gate's independent-day table; the gate is kept for A1's identities and floor (iii) only; which calendar each reading uses is a table (4 item 5); a synthetic test of the difference (T-1) | 4, 5.5, 7.4, 9, 10, 12 |
| **F3** V not differenced | **C2's value line is the design's openings against the twin design's openings** (two twin draws pooled), both from paired U1 replays; V(P-16), the base's own routing deviation, and V(design) undifferenced beside; **the fallbacks' values defined**: every P-16 mark is labelled (both sides at 3R) as labels only, so an opening at 08:30-09:00 or at the report-day 07:35 mark has its own stratum mean | 5.2, 5.3, 7.4, 11, 12 |
| **F4** persistence and power before the pin | each cell's persistence class stated with its reason (6.6); its power read from Q-55's Table 9 (the fourth text states the rule whole, 0.4); a cell that cannot reach power in its class is dropped at the pin, counted; Q-55 a prerequisite; an optional bars-only run-length count named as the lead's call | 6.6, 9 (A9), 20 |
| m1 the 17:30 start | one rule: s1 and s2 start at the 17:30 mark, half an hour of the night, a declared choice; the 15-bar minimum is a separate missing-bars rule | 6.2, 6.3, 8 |
| **m2 (the lead's ruling, E-039 (1))** | the non-opening trades and the fallback openings are P-16's registered trades and keep its 07:35 report-day entry; **the openings this family places obey 07:40**; stage A counts every design's trades and openings at the report-day 07:35:00 entry, reported beside the verdict | 3, 5.1, 5.2, 9 (A2) |
| m3 the flatten convention | **C1-close** is a further line of the same intersection: C1 under the `close` flatten convention | 12 |
| m4 identities that bite | two refusing identities added: the state **never on** (every waiting opening falls on its sixth live session) and the state **equal to the drawn placebo set** (every in-wait opening's offer is in the set); T-5 run through the vendored router and lockstep loop; the off-by-one of "first W live sessions" pinned against `FundedAccount.days`; Q-17's adapter refuses a path already carrying `funded_account_cls`, so its extension is declared and held to Q-17's identity | 5.4, 9 (A1), 18 |
| m5 the news readings | E-034 cited (it decided Q-39's question); its unstated news rules carried in the scorecard's "not modelled" note; the ISM/GDP-day share of openings stated as unknown | 3, 13 |
| m6 B2's slow amplitude | no smaller than the follow lift Stage 2 recorded (the S1 and S3 result files, now vendored, E-040; Q-61, 905eb19), and no smaller than three times the choice span's, E-036's precedent | 11 |
| m7 T-10 | its levels, replications and failure rule declared; the family's level rests on B2's larger-of rule, not on T-10 | 18.2 |
| m8 the per-year share | "a third by construction" corrected: a third over the long run, per year it follows the state's persistence; per-year shares beside K1; W's rationale moved off the iid argument | 5.4, 6.4, 9 (A5) |
| n1-n8 | readings: E-036 M3-2 answers the open question on H and IV; E-035 answers the twin's form; the 1R mirror holds for gross only; x3's frame named and T-2's cuts extended; V is gross of the wait's cost; Q-35's ordering recorded; A4's default declared (u3 closed, counted); V's conversion first-order and its price uncalibrated | 1, 6.1, 6.5, 7.4, 9, 12, 20 |

## 0.3 What the third version corrects (the red team's second read; E-052, E-054, E-055; Q-87's brief)

Nothing else moves: the cells, the twin's estimand in C1, the level, the reads line and the seeds (one reserved seed
put to K0's use).

| item | what changed | where |
|---|---|---|
| **m2-1** C2's residual | "removes it" corrected to **"removes it to first order"**; the residual (the state's clustering against the placebo's, at the router) stated beside C2 as an assumption that carries the value; **the twin designs now draw a clustered placebo** -- the state's own in-state indicator shifted circularly by a seeded offset within each (calendar year, day kind) sequence of sessions, all marks of a session together -- which keeps every stratum's count and the state's runs, so the waits and routing positions match; C1's twin, the exact expectation, unchanged | 7.1, 7.4, 12, 13 |
| **m2-2** the seal and the whole-window identities | the identities against whole-window registered objects (P-16's trades, gate paths, U1 rows, Q-51's) move to **`identity/family_o_identity.py`** under its own identity row, run and held under the lock before run 1 (A0); run 1 builds the population on the choice block only; T-3 compares run 1's sections other than `identity` | 4, 9 (A0, A1), 18, 19.2 |
| **m2-3** B2's slow amplitude (**E-051's ruling, E-054 (2)**) | the deciding lines' null is **the realised judged population** (the twin's exact expectation on the judged block), B2's slow components **centred within the block** (shaping dependence, not the mean); the case of "a state that sat in one regime throughout the judged block" named and left to the confirmation; a\* the largest of (a) the choice span's, (b) Stage 2's recorded follow lift, and **(d) the judged block's out-of-state offers only, each centred by its own stratum's out-of-state mean -- no term from the design's own lift**; the unsourced "three times (a)" **dropped** (E-051: "the 3 dropped unless sourced"); the level and power of (d) at the family's level shown on toys | 11, 18.3 |
| **m2-4** A10's consequence | relabelled "`cons` lax on c in this class"; if so in a surviving cell's class, **the deciding rule itself** runs on the same replications as a pseudo-judged split (B2 from 2021-2022, the statistic on 2023); **if it is lax too, the cell is closed, counted**, before stage B reads any lift; its chance of closing a cell whose rule holds shown exactly (T-1) | 9 (A10), 18 |
| **m2-5** the confirmation's value line | always C1's bound x **the design's in-wait openings** a start-year x mean_dv(c) / 4, at least $500, with C2 on the window's replays beside; the window sized for this line as for C1; B2's source named (the development window's values, both blocks); the in-wait count also in 12's beside valuation | 12, 15 |
| **m2-6** the P statistic | **`pcons`** (`extended/p_bound.SHIPPED`, E-035 (3)) for the paired P differences, beside, one-sided at 0.05, never a line; `bm63c` beside once its table is pinned; D-621 (3)'s line (i) labelled as not holding its level (E-007 (1)) | 13 |
| **m2-7** C1-close's walk | the named instance **`Rules("fo_stage2_close", FLAT_ENTRY, "close", True)`**: STAGE2's walk end (15:08) and every other rule, the flatten priced at the close of the bar ending 15:08; a test that it differs from STAGE2 only at a flattened trade's price | 5.3, 8, T-1 |
| **m2-8** Q-55's failure branch; blob ids (**E-052, E-054 (2)**) | the withdrawal clause (Q-55 or Q-83 not holding); the two modules pinned by blob id, a run refusing other blobs | header, 9 (A1), 20 |
| **m2-9** the drop rule's column | **k >= 12**; Table 9's **k = 15 column** (stricter than any k from 12 to 15); the drop **mechanical** -- the lead records it, no confirmation | header, 6.6 |
| **m2-10** the forfeiture collision | the waiting class **composed with Q-17's `ForfeitFundedAccount`** for the forfeiture responses, held to Q-17's forfeiture rows with the wait switched off; what is needed from Q-76's declared keyword named | 5.4, 13, 18.1 |
| **m2-11** B2's day kind | B2 draws **within day kind**: two stationary bootstraps of mean block 63, normal days and report days, each judged session filled from its own kind's sequence | 11 |
| **E-052 (1)** fill intensity | the openings-per-session (and in-state-offers-per-session) persistence stated beside the side persistence; **K0**, outcome-free, before stage B: `cons`'s size at the family's level on a sign null built with each cell's own choice-block counts (seed 20261989), a cell whose 95 % interval lies wholly above nominal killed; the same check on the pick's judged counts before any outcome is read, a pass not claimed above nominal; its level and power on toys | 6.6, 9 (A11), 12, 16, 18.3 |
| **E-055** the place records | Q-70's adapter cited at family B's section 20 **item 10**; its identities relied on named (P-16 at 4 paths on `PATH_COLS`; P-16 and P-14 at 100 paths against `trades_per_year_records`, Q-89); **recording on the U1 replay** -- listed in the third text as this family's build item, **built since by Q-94** (E-068: `extended/replay_records.py`'s `ReplayRecorder`, passed as `user_beside.run_starts(..., recorder=)`; its heavy identity Q-101), what it leaves to this family named (the fallback flag, the joins by offer id, the restricted replay job); **declined offers are counted by the gating wrapper**, not the recorder | 9 (A1), 18 |
| **E-059** Q-76 merged | the family's class reaches the U1 replay through Q-76's keyword, forfeiture composed over it; **E-007 (e)'s readings reported without the ten Focused Trader models, labelled so** (the engine refuses them for any funded class but the vendored one, `lockstep.py` 1403-1408); a re-composed path admitting them is a separate build under its own row, not now | 5.4, 13, 18.1 |
| n2-1..n2-10 | readings: the drafter's four questions answered; S2's pre-read reworded; Q-51 HOLDS (E-044 (3)); the seed check excludes the data junctions; T-10's runtime; "inside Table 9's grid" means 40 standard errors; K5's censored waits reported; floor (iii)'s gate waits less than the traded design; the stage-B pick inherits m2-1; the module's variance under stratum-varying shares conservative | 4, 6.6, 9, 10, 12, 16, 18 |

## 0.4 What the fourth text corrects (the prereg-gatekeeper's refusal of the third, E-073)

The design and every ruling the third text applied stand; seven text items, as one edit. Nothing else moves.

| item | what changed | where |
|---|---|---|
| 1 the pin's conditions | the pin waits only on external conditions -- Q-55 (with the drop rule applied), Q-83, the family number; A0, the seam and the family's own identities run **after the pin and before run 1**, refusing; the infrastructure identities (Q-89, Q-93, Q-101, Q-80) are **pre-run conditions** | header, 9 (A0), 19.2, 20 |
| 2 the drop rule whole | the result file and section (`results/calibration_power.csv`, its placebo-selection power rows), the `cons` k = 15 column, the value row (`net3`, and why), **one** deciding class per cell (s1 `window`, and why), the share (0.25: the grid's nearest to the states' one third); applied by the lead at the pin, the dropped cells recorded in the pinning row; no figure typed in, no placeholder for Q-55's figures left | 6.6, 8 |
| 3 the fixed values | W = 5, K5 at one half, the 250-session third, the 17:30 start, two twin draws, K0's 200,000 replications are the file's values; the sentence that let the text be edited until the pin struck | header, 20 |
| 4 the pin-time form | the title and status as they read when pinned; the pin changes only the file name and `F-XX`; k in the pinning row only | header |
| 5 tier 2 | each of `conduct.py`'s four patterns stated for the openings and for the base's trades, off in the base case (D-289), on beside | 3 |
| 6 the readings beside floor (iii) | the break-even denial, the zero-edge twin, e and its bound, stage one's D-47 criterion -- the last three P-16's by construction, said so | 12 |
| 7 Q-94 merged | `extended/replay_records.py`, `run_starts(..., recorder=)` and its heavy identity Q-101 cited | 0.3, 9 (A1), 18, 20 |

## 1. Hypothesis: the mechanism, its sources, and each state's sign stated in advance

**(i) Bracket geometry is textbook probability** (Karlin & Taylor 1975, ch. 7; the scout's note
`docs/research/mechanisms_2026-11-15.md` section 3.1):

- for a driftless price, a bracket with stop a and target b = R a reaches its target first with probability
  1 / (1 + R), on either side, at any volatility; volatility sets only the time to resolve (a b / sigma^2);
- **a side-free filter cannot lift a coin-sided bracket's gross on a price without memory or drift**: whatever days it
  picks, the coin wins 1 / (1 + R) there too (what costs can do is (v) (c));
- **persistence lifts the 3R coin's gross; it cannot lift the 1R coin's.** With moves that persist, the far target is
  reached more often when the side matches the move, so the side-symmetric 3R win rate rises above 1/4; with moves that
  revert it falls below. At R = 1 the long's and the short's **gross** outcomes on one resolved path are exact
  opposites, so their side-symmetric value is zero whatever the path's memory. *Reading (the review's n3):* with P-16's
  breakeven move, the flatten and kind-dependent costs a 1R path's side-symmetric **net** value is not identically zero,
  and at 1.5R persistence acts; this weakens the reason given for V_other being small (7.4), which is beside;
- **a fixed drift moves the two sides apart at first order and their mean only at second order** (gambler's ruin with
  drift).

`tests/test_family_o_persistence.py` (T-1) holds all four on exact chains and seeded walks. In passing it shows, as an
illustration and not a result, that persistence at a scale much shorter than the bracket moves a bracket many steps wide
only a little. **The mechanism needs persistence at the bracket's own scale** -- a 37.5-point stop and a 112.5-point
target, held for hours.

**(ii) The literature linking persistence to observable state** (the scout's 5.1; every figure the paper's own, on the
paper's sample, none at our bracket's scale or on NQ):

- **unexpected against predictable volatility.** Intraday serial correlation of S&P 500 futures is related to realised
  volatility only through its unexpected part, and "the impact of predictable volatility is instead found to be
  negative (LeBaron effect)" (Bianco & Renò 2009, *Quantitative Finance* 9(4) [abstract only]); "a similar but more
  pronounced effect" with intraday measures after the daily effect attenuated (Bianco, Corsi & Renò 2009, *PNAS*
  106(28) [abstract only]); the daily effect is LeBaron 1992 (*J. Business* 65(2) [abstract only]);
- **day-scale persistence.** The first half-hour predicts the last, more strongly on volatile and news days (Gao, Han,
  Li & Zhou 2018); the rest of the day predicts the last 30 minutes, much more strongly on negative dealer-gamma days
  (Baltussen, Da, Lammers & Martens 2021); the always-on version fails out of sample while a threshold version does
  better (Rosa 2022) -- a filter, which is this family's form (all as the review cites them,
  `vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md` lines 165-192);
- **dealer gamma.** Momentum with a negative gamma imbalance and reversal with a positive one (Barbon & Buraschi 2021
  [abstract only]); higher net gamma predicting a stronger intraday reversal in E-mini order flow (Adams et al.,
  SSRN 5641974 [secondary]). Gamma data are S&P-only and a purchase; this family uses only bar-based proxies of the
  states the literature links to it.

**(iii) The hypothesis.** On P-16's overnight offers, the 3R coin's side-symmetric net outcome is higher, in a declared
ex-ante state, than at a random offer of the same mark, day kind and year; and a newly funded account that waits for the
state takes openings worth more than the openings a random waiting rule takes, where the openings are actually taken.

**(iv) Each state's sign, stated in advance** (section 6.3 defines them):

| cell | state | sign stated now | why |
|---|---|---|---|
| s1 | unexpected volatility: the night's range above its forecast | **positive** | Bianco & Renò: serial correlation rises with the unexpected part of volatility |
| s2 | a night already trending against its forecast range | **positive** | Gao et al., Baltussen et al.: day-scale persistence, stronger on active days |
| s3 | low predictable volatility | **positive** | LeBaron; Bianco & Renò: predictable volatility lowers serial correlation, so its low third should persist more |
| u3 | family R's (u3): the offer forecast fast | **negative** | family R's draft section 0.1: "by the LeBaron effect, a predictably fast market is less persistent, so a 3R coin opening there should win less". Its forecast also carries today's surprise so far (x3), which by Bianco & Renò pulls the other way, so the prior is weakly negative; **the stated sign is negative** |

s3 and u3 read predictable volatility from opposite ends: their two signs are one prediction. Every cell is still judged
one-sided for a positive lift (a design is used only if it lifts); section 14 says what a u3 pass would mean against its
stated sign.

**(v) What the trade-level lift can contain, stated before anything is read.** The lift (section 7) is a difference of
net R at 3R between in-state offers and random offers of the same strata. It can contain:

- **(a) persistence** -- the gross effect above, the hypothesis;
- **(b) a drift's second order** -- a state that picks days with a larger drift in either direction raises the
  side-symmetric 3R mean (that is persistence at the day's scale, and counts); a state aligned with a **fixed** drift
  direction (for example calm days in a rising market) raises one side and lowers the other at first order -- C3
  refuses a lift carried by one side;
- **(c) the cost composition** -- Stage 2's walk charges an exit by its kind (`extended.walker.STAGE2`; E-010 (3)): a
  target none, a stop and a breakeven exit one tick, a flatten two ticks **and** the worst of the bars ending
  15:08-15:10 less two ticks. A state that picks fast days (s1, u3) avoids flattens and gains a little from that alone
  (family R's mechanism, its draft section 1 (iv); E-028 (2) records family R's drafter expecting that much of such a
  lift is Stage 2's conservative flatten convention); a state that picks calm days (s3) flattens more and loses a
  little. C3 cannot catch this (a cost avoided raises both halves), so **C1 must also hold under the `close` flatten
  convention** (C1-close, section 12);
- **(d) the breakeven move** -- P-16's walk moves the stop to the entry at the next session open when in favour
  (FV3's move). It is a stopping rule: on a martingale it adds no expected gross (optional stopping), so it cannot make a
  lift by itself beyond its exit tick; Q-20's corrected moves are read beside (`STAGE2_BE_BOTH`, merged b7232ba).

**(vi) Why it could matter for a user.** The value of a won opening over a lost one is the largest of any place
(`u_value_map.csv`, `place_values`, `mean_dv` at `c_funded_opening`, base `p16`). A filter delays openings and does not
drop them: the openings' yearly supply is set by passes, not by the filter.

**(vii) Whose accounts and how.** One user's own five Topstep seats, each with its own trades, one position at a time
across the firm (Stage 2 D-157, D-429; E-012 (3)). Every trade is placed by hand at least five minutes after its alert
(E-008). The wait is a decision the user makes before each offer, from bars already closed; nothing is automated.

## 2. Prior exposure: what has already read these bars, this population and this mechanism

A judged reading is worth only what the judged block's freshness allows. Every row below is Stage 2's unless marked.

| row | what was read | data | what it recorded | bearing here |
|---|---|---|---|---|
| D-136, D-137 (the effect atlas, **O family**) | O01: Baltussen et al.'s negative-gamma intraday momentum; O02: an opening-continuation variant; O03: gamma's link to rest-of-day volatility | 2012-2014 (QuantConnect), short | O01 survived and passed its check on NQ narrowly; O02 failed on both markets; O03 passed on both; D-137: O01 not pursued (no translation reaches the criterion; its conditioning is S&P-only) | **outside this repository's window**: independent prior evidence that intraday persistence on NQ is state-dependent, from options data this family does not use; no 2020-2026 bar read |
| D-136 (the effect atlas, **R family**) | R01-R03: the VIX, range compression, a volume surge as predictors of the day's or rest of the day's realised variance | 2009-2014 | VIX and compression predict variance; "sizing and survival inputs, never edge" | outside the window: predictable volatility is predictable on these markets -- the premise of s3 and u3 |
| **D-578 (3), D-580 (S1)** | the sided coin on P-16's schedule: momentum over 1-120 minutes, the move since 17:00, the prior session, range positions, breakouts -- followed and faded, per offer, against the coin twin, at every offered R | 2020-2026, **both spans** | 15-minute momentum and the latest 5-minute breakout, followed, survive the family-wise lift test; both fail the span guard (below P-16 on 2020-2023, above on 2024-2026) | **the sided reading of the same persistence, seen on the judged block.** This family is its side-free counterpart. A sided effect that differs by era warns that a side-free one may too: C3, B2's amplitude (11) and the year-by-year readings beside |
| **D-586-D-592 (S3)** | the sided coin on new event kinds; `lnbar1x4` followed passed D-578's guards at L = 0 and failed at the operator's 5-minute latency | 2020-2026, both spans | "the follow-the-breakout effect is broad and slow"; recorded as a lead for unread data (D-592) | the follow effect has been read three times on this window, both blocks: **the judged block is not fresh for persistence at the bracket's scale**, only for this side-free, state-conditioned, 3R-only question |
| S1's and S3's result files, **now vendored** (E-040; Q-61, merged 905eb19) | `s1_sided_coin.csv`, `s3_event_kinds.csv`, `s3_latency.csv` | as the rows above | the follow rules' per-offer lifts by R over the whole window (section `lift`); the span split only for campaign growth (section `g3`) | **read by this file for B2's slow amplitude only (11), at run time, upward only**: a disclosed pre-read that can raise a critical value and choose nothing. The drafter read their column, section and rule names, never a value |
| **D-578 (4), D-581, D-582 (S2)** | P-16's coin gated by an ex-ante state: the last 30 bars' range in thirds against the same mark's 20 prior sessions; the distance from the 17:00 open above or at-or-below its trailing median | 2020-2026, both spans; **campaign growth over every trade** | no candidate; the high-volatility cell closest to P-16, the trend cell just below; low and mid volatility failed resolution at the longest offered R in their worst year | **the nearest prior: those states and their campaign readings are seen.** S2 read the whole trade stream's campaign growth (mostly 1R-1.5R trades), removed offers from every account rather than timing one place, and had no placebo. s1 and s2 are relatives of S2's volatility and trend cells and s3 of its low-volatility cell, redefined here from the literature (HAR forecasts, a year's thirds, 3R only, side-symmetric, offer level); **S2's resolution failure is why K2 is a kill before any lift** |
| **E-035 (Q-16's calibration)** | random selections independent of the outcomes, firing on 2 % to 50 % of P-16's judged offers, in six persistence classes; **the coin side's own win at 1R and net R at 3R** of those offers (calibration note 2.4) | **the judged block's P-16 offers** -- this family's judged population among them | `cons` (treated df) holds its level on every selection null; power by persistence class (Table 9) | **a disclosed pre-read of the judged population's outcomes**: their dispersion and dependence under random selection were computed, program-wide, to choose the statistic. No state and no selection of this family was read. It can bias the choice of statistic (adopted for every family), not this family's selection. Its figures stay uncited until Q-55 (E-035 (4)) |
| D-525 (4), D-538, D-542, D-618 (3) | P-16's cutoff per mark (unresolved share at most 5 % at every offered R, kind columns); the stop-width screen | the whole development window, both blocks | P-16's offered marks, none after 09:00 CT at 150 ticks | the population's marks were fixed on both blocks: their average resolution at 3R has been seen, mark by mark |
| P-16's registration; D-605 (by calendar year); D-606 (its draft confirmation) | P-16's gate, journeys and robustness | both blocks | P-16 registered; robust to every single year | the base's own readings over both blocks |
| D-652 (U2), D-667-D-669 (U5) | `u_xfa_day_budget.csv` sections `opening_trade`, `after_opening`, `signal_supply`; `u_value_map.csv` sections `place_values`, `bar`, `records_leaf` | P-16's registered campaign, both blocks pooled, the bound arm | the base's funded opening (the share that won it, its realised risk), what follows it, and the value of a win by place | **the drafter has seen the handoff's tables of these** (sections 2.5 and 2.7; values not typed here): the base opening's won share at 3R, pooled over both blocks and not by any state, is the quantity this family tries to raise. It can bias the decision to propose the family, not the selection |
| E-021; the scout's note section 5.1 | the states s1-s3 proposed from the literature | none | -- | the design, adapted to E-023 |
| family R's draft (Q-38, E-028) | the HAR-type forecast u3 restates (section 6.5) | none | -- | u3's definition; nothing read |
| **Q-35** (its script merged, E-051 (2): `extended/openings.py`, `scripts/q35_openings.py`; its run in the heavy chain's third leg) | where P-14's and P-16's funded openings fall, by mark, hour, entry delay, the 08:30-09:00 window, report day, FOMC day, weekday, year and stop; no outcome column | both blocks, when it runs | -- | **if it runs before the pin, its counts over both blocks are a disclosed pre-read** (direction-free); this file's rules use stage A's choice-block count only (5.5; the first read's n6) |
| this repository | F-02's and family B's drafts (nothing read); Q-17, Q-18, Q-20, Q-22 when run (P-16's journeys and readings on both blocks) | -- | -- | the scorecard's base readings, beside |

**The drafter's own reads (disclosed).** Code, configuration, decision rows, the review, the calibration note's text
(sections 1.3, 2.4, 7.3, 7.4; no table value), and the column, section, measure and rule names of five result files --
no result value was opened beyond what the rows above and the handoff's tables state:

- `vendor/stage2/propedge/campaign/shared_days.py` (the router: `TradeRouter.begin_day`, `able`, the strict rule, the
  new account's stamp; `ReplayTable`), `sizing.py` (`TierSizedDraw.can_take`), `lockstep.py` (`FundedAccount`);
- `vendor/stage2/config/fv3_corrected_portfolio.yaml` (`routing: able`), `vendor/stage2/scripts/rc150_dev_test.py`
  (header), `atlas_a3.py` (`gate_kwargs`), `vendor/stage2/propedge/research/u_value_map.py` (header);
- `extended/features.py`, `extended/walker.py` (presets), `extended/gate.py`, `extended/user_beside.py`,
  `extended/reader.py`, `extended/lift_bound.py`;
- the names (never the values) in `u_value_map.csv`, `u_xfa_day_budget.csv`, `s1_sided_coin.csv`,
  `s3_event_kinds.csv` and `s3_latency.csv`.

**What follows.**

- (a) **The judged block is late development for persistence**: the sided follow effect has been read on it (S1, S3),
  the base opening's won share at 3R pooled, and the coin-side 3R outcomes' dispersion under random selections (Q-16).
- (b) **What is new** is the side-symmetric 3R lift of an ex-ante state over a placebo selection at the offer level, and
  the value of a waiting rule's openings against a random waiting rule's in history's order. Neither has been read.
- (c) S2 is the nearest prior; this family names it and differs from it in the outcome read (3R per offer, not
  campaign growth over every trade), the selection (one place timed, not every account's offers removed) and the
  comparison (a placebo of the same strata).

## 3. Contract fit and conduct: the constraints every cell lives inside (CHARTER section 4)

| constraint | how the family meets it |
|---|---|
| latency, at least 5 minutes, hand entry (D-266; E-008) | **a state at mark m is an alert at t = m - 5 and reads only bars stamped at or before m - 6** (closed by t; feature-rules 1). The entry is P-16's: market at the first bar opening at or after the mark, one tick adverse. No automated or API entry |
| one position per firm, five minutes flat (D-429) | the engine's strict router, as P-16's, unchanged |
| one trade an account a session | P-16's (its registration section 3), unchanged |
| resolution (D-212, D-308) | K2 on the choice block (a kill), floor (i) on the judged block, at 3R, overall and every year |
| realised risk (D-212 (1), D-308) | the stop is P-16's 150 ticks and the opening's size the table's; read in its allowance-capped form (E-022 (1), E-032) |
| stop band and cost floor (`stop_band.csv`; D-271 (3)) | 150 ticks, above the 45-tick floor |
| report days (D-525, D-533; E-007 (d); **E-039 (1)**) | **The lead's ruling (E-039 (1)):** P-16's registered trades keep their registered report-day entries whenever they are re-read, and new families enter strictly after 07:35:00 CT. So: **the openings this family places -- an in-wait opening at an in-state offer -- start at the 07:40 mark on a report day**; the non-opening trades and the fallback openings are P-16's registered trades and keep P-16's 07:35 mark (which enters at 07:35:00, on the stated end of Topstep's Tier 1 window, 07:25-07:35 CT; the audit's U7 (a), `docs/audits/phase0/E_rules_currency.md`). **Stage A counts each design's trades and openings at the report-day 07:35:00 entry** (A2), reported beside the verdict. FOMC days are excluded |
| report days and the selection | on a report day the population starts at 07:40, so s1 can pick a mark after the 07:30 release -- **the twin's strata include the day kind, so the selection cannot win by choosing report days** (7.1); A2 reports the share of in-wait openings on report days |
| ISM (09:00 CT), GDP (07:30 CT) and "maximum size into major news" (**E-034**) | E-034 decided it (Q-39 read): which events count, and whether holding an open position through one counts, are **unstated** on Topstep's pages; the GDP release minute is unstated; the full-size funded opening held through an unnamed release stays as it is, and these unstated rules are listed in every scorecard's "not modelled" note (13). No state reads a release (every state reads bars before its alert). A selection that moves openings toward post-release mornings can change the share of openings held through ISM; with no ISM or GDP calendar on disk that share is **unknown**, and said so beside the verdict |
| the 08:30-09:00 window (Stage 2 D-281 (3); E-030; E-036 M3-2) | **no entry of this family's choosing falls there** (the population ends at the 08:25 mark), and **no state reads a bar of the alert's day stamped 08:30-08:59** (the latest alert is 08:20; 6.1, T-2). A fallback opening (after W) may be a window offer, as P-16's own are |
| no time stops (D-212 (2)) | none. The wait chooses an entry; it never ends a trade |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (37.5-point brackets held hours); no maximum size into major news as E-034 reads it (above); no copying across accounts (D-157); nothing concealed: the rule is a published state on closed bars |
| conduct, tier 2 (Stage 2 D-145; `vendor/stage2/propedge/campaign/conduct.py`) | each pattern is **modelled off in the base case (D-289) and on beside**: in the scorecard's placement-on reading (Q-17's `rtp` response, 13) and beside floor (iii)'s campaign (12). **(1) R at or below 1** (`conduct.MIN_RR`): not the openings, which are 3R; it applies to the base's own trades -- the table's 1R leaves after the opening and in the paid phase, and Combine trades the engine's need-aware exits close below 1R -- as P-16 registered them; the wait changes none of them. **(2) Maximum position on most trades:** applies to the openings -- a fresh funded account's 3R opening is sized by the table at its allowance, 20 micros at 150 ticks (P-16's registration section 3), so every opening, in-wait or fallback, is at its account's maximum position; and to the base's trades wherever their table sizes at the allowance, as registered. **(3) An account-deciding position** (`MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN`: a funded position risking more than half the $2,000 drawdown): applies to every opening -- 20 micros x 150 ticks x $0.50 = $1,500, above the half, $1,000 -- P-16's openings and the design's alike, since the wait moves an opening and never its size; the base's later funded trades as their table sizes them, as registered. **(4) Several accounts at the MLL in one day:** a campaign pattern, not one trade's -- the wait moves openings in time and can bunch them with the base's trades, so the share of such days is reported beside for the design, its twin and P-16 (the gate's same-day multi-breach columns, as P-16's registration reports `share_paths_with_same_day_multi_breach`) |
| conduct tier 3 (E-013 (1)) | the opening's size is already priced under Terms of Use s.8; 0 % denial in the verdict, 10, 25 and 50 % beside (Q-17's adapter) |
| firm rules | none loaded by the family; the engine runs Stage 2's verified ledger as P-16 does. No inactivity rule for a waiting XFA is on the verified ledger as read (the review's last open point); none is modelled |
| the breakeven move (E-013 (2)) | allowed as made; P-16's walk; Q-20's corrected moves beside |

## 4. Data, blocks, the seal, the calendars and the disclosed pre-reads

1. **Data:** Stage 2's NQ 1-minute bars (licensed, uncommitted, `vendor/DATA_MANIFEST_stage2.sha256`), 2020-01-02 to
   2026-07-16 only. Labels from this repository's walker (`extended/walker.py`, E-011), not Stage 2's `data/atlas`.
2. **The blocks:** choice 2020-01-02 to 2023-12-29; judged 2024-01-02 to 2026-07-16. Stages A and B read
   2021-01-04 to 2023-12-29: 2020 serves the states' warm-up (22 sessions for the HAR terms, at least 120 for the
   thirds) and u3's first training fold; **no lift is read on 2020**.
3. **The seal (E-026 (2)).** Every bar and walk read goes through `extended/reader.py`. The judged block is read only
   under the purposes on section 19.1's line, from a clean run of a committed tree, once each; each read appends to
   `results/read_ledger.jsonl` first. Choice-block reads need no tag; this file names them anyway: `fit_forecast`
   (u3's fit), `stage_A_supply`, `stage_B_choice`. The reader refuses any choosing or fitting purpose on the judged block
   whatever this file says. **Run 1 builds the population, the states and every replay on the choice block only**; the
   identities that compare whole-window registered objects run apart, in `identity/family_o_identity.py` under their
   own identity row (A0; the second read's m2-2), as the reader admits a whole-window read only from an identity
   script. T-3 is the second proof: run 1's sections other than `identity` are unchanged when the judged block is
   replaced.
4. **Disclosed pre-reads** -- inputs fixed or read over 2020-2026 that T-3 cannot see:

   | input | what it is | can bias | cannot bias |
   |---|---|---|---|
   | P-16's offered marks (D-525 (4), whole window) | the population's marks | that the population is "marks whose 3R walks resolve on average" -- common to every arm | the state's selection within a stratum |
   | P-16's per-R bounds (the bound arm's shift), estimated over both blocks | a constant per R | the level of every replay and campaign number, design and twin alike | the lift (computed on net R before any shift) |
   | `u_value_map.csv` (D-668) | `mean_dv` at place (c) | C2's dollars and stage B's ranking | the lift or its bound |
   | `u_xfa_day_budget.csv` `opening_trade` (via the handoff) | the base opening's won share, pooled | the decision to propose the family | the state's selection |
   | S2's readings (D-582) | volatility and trend gates on P-16's marks | **which hypotheses are tested**: the states were proposed knowing that S2's high-volatility and trend cells read close to, or just below, P-16 over both blocks, so the choice leans toward relatives that looked good on the judged block, and so toward a higher chance of a pass (the second read's n2-2; the honesty sentence, 17 item 4) | the computation of the lift, the pick |
   | Q-16's calibration (E-035) on P-16's judged offers | coin-side outcomes under random selections | the statistic (program-wide) | this family's selection |
   | S1's and S3's vendored lifts (11) | follow lifts by R, whole window | B2's amplitude, upward only | any selection, the pick |
   | Q-35's counts, if run before the pin | where the base's openings fall, both blocks | nothing of the lift (counts only) | -- |

5. **Which calendar each reading uses (the review's F2).** The gate's day table (`SharedDayTable`, the default of
   `extended.gate.run_gate` and of the vendored gate) draws every calendar day independently, which destroys the states'
   runs across days; so **every reading of the wait, the openings and their value is on the U1 replay in history's
   order** (Q-17's `extended/user_beside.py` over the vendored `customer_slices.replay`, whose `ReplayTable` plays a
   start's days in their own order).

   | reading | calendar |
   |---|---|
   | A0's whole-window identities against P-16's registered gate paths (and Q-51's) | the gate, as registered (seed 20261206), in the identity script |
   | A0's identities against P-16's U1 start rows | the U1 replay, whole window, in the identity script |
   | A1's never-on, placebo-set and restricted-replay identities | the U1 replay of choice-block starts, in run 1 |
   | K0's counts (A11) | the choice span's population (C1's form) and the choice-block replays (C2's form) |
   | A2's counts, A7's K5, the waits, A9's u_c, stage B's V_B | the U1 replay of every choice-block start from 2021-01-04, each start's history ending at 2023-12-29 |
   | C1, C1-close, C3, K1, K2 | none: offer-level, on the population's walks |
   | C2's V, V(P-16), V(design), the openings' counts on the judged block | the U1 replay of every judged-block start, U1's own start set and horizon rule |
   | floor (iii), the long-run gate | the gate, the design's own campaign (seed 20261983), as the gate is defined (E-022 (2)); on its independent days the design waits less than it does traded in history's order, said beside the floor (the second read's n2-8) |
   | the scorecard (13) | the U1 replay, as U1 is defined |

6. **No NQ from 2026-07-17** is on disk or read (section 15).

## 5. The base, the population, the walk and the design

### 5.1 The base

P-16 exactly, as registered and as this repository's identities reproduce it (E-004's gate paths; E-010's U1 start
rows):

- the coin `rc_s150_all_nr`: one fair coin per (date, mark), seeded 20261102 (`resolved_coin.coin_table`);
- the stop 150 ticks, every quarter R to 3R walked, Stage 2's costs (`fee_by_stop`);
- a report day's marks before 07:30 CT dropped, then every report-day entry before 07:35 CT (D-533 (2)) -- **kept for
  P-16's registered trades** (E-039 (1));
- the day kinds `n` and `b` (FOMC days, early closes and empty days out);
- P-14's money side: the no-closure table, 20 purchases in 21 sessions, the strict router at five minutes, five seats,
  **routing `able`** (D-318: each trade to the longest-waiting account that can take it,
  `vendor/stage2/config/fv3_corrected_portfolio.yaml`), one trade an account a session;
- the registered trades' content hash `rc150_dev_test.TRADES_SHA256`.

### 5.2 The population: P-16's overnight offers, and the labels at every mark

- **Marks:** every five-minute grid mark P-16 offers from **17:00 to 08:25 CT**, on a report day from **07:40**: the
  entries this family chooses are strictly after 07:35:00 (E-007 (d), E-039 (1)); P-16's report-day 07:35 mark, which
  enters at 07:35:00, is never chosen here (a fallback opening may still take it, as P-16 does). Every P-16 mark before
  its opening-window marks, fixed as a time range and P-16's admitted set (D-525 (4)), not re-read from any table; T-4
  checks it against the builder.
- **Sessions:** P-16's walked sessions, after the warm-up (4 item 2).
- **The offer:** at mark m of day d, P-16's market entry at the first bar opening at or after m, one tick adverse; its
  side for the design the registered coin's at (d, m); **walked long and short** for the estimand.
- **Not in the population** (never chosen by any state): the marks 08:30-09:00 (P-16's own, inside D-281 (3)'s window);
  the report-day 07:35 mark; the marks from 09:05 (refused by P-16's cutoff; family R's population).
- **Per cell**, an offer at a mark where the cell's state is not defined (s1 and s2 before the 17:30 mark; any offer
  without enough history or bars) is not in state.
- **The strata** g = (mark, day kind, calendar year): what the twin matches (7.1).
- **The labels at every P-16 mark (the review's F3).** So that an opening the router hands a waiting account after W --
  a fallback -- has a value wherever it falls, **every P-16 offer is walked long and short at 3R and at every table R**,
  the 08:30-09:00 marks and the report-day 07:35 mark included, **as labels only**: their strata (mark, day kind, year)
  have their own means; no state is defined or read there; no rule reads them before stage B.

### 5.3 The walk and the labels

- **The walker:** `extended/walker.py`, preset **`STAGE2`** (E-011): P-16's own walk -- FV3's rung walk, a stop on a
  touch, a target on a trade through, stop first on a two-barrier bar, the breakeven move, the walk's end the bar ending
  15:08 CT and the flatten at the worst of the bars ending 15:08-15:10 less two ticks, Stage 2's costs.
- **The `close` convention, in C1-close and beside (the second read's m2-7): the named instance
  `extended.walker.Rules("fo_stage2_close", FLAT_ENTRY, "close", True)`** -- STAGE2's walk end (the bar ending 15:08),
  its breakeven move and every other rule, the flatten priced at the close of the bar ending 15:08 instead of the worst of
  the bars ending 15:08-15:10 less two ticks. The walk's end is STAGE2's, so every trade's kind, exit bar and MAE are the
  same under both and only a flattened trade's price differs (by at least the two slipped ticks): the line isolates the
  flatten convention and nothing else (T-1's `test_the_close_instance_differs_from_stage2_only_at_the_flatten_price`).
  `DECLARED_F01`'s 15:10 walk end is not used: it would also let stops and targets fill on the bars ending 15:09 and
  15:10.
- **Kinds:** stop, target, flatten (unresolved), breakeven. "Unresolved" means the flatten kind.
- **The values at R = 3** for offer i: the long's net R l_i, the short's net R r_i, and the **side-symmetric value**
  **c_i = (l_i + r_i) / 2**: the coin's expected net outcome at offer i without its noise (F-01's convention for a twin's
  expectation; family R's draft 5.3); **its stratum-centred value y_i = c_i - mu_g(i)** (7.2).
- **Only R = 3 is read** for any cell's lift: the opening's ask (the table's fresh funded state, handoff 2.5). V_other,
  beside, uses each trade's own R (7.4).

### 5.4 The design: the waiting opening

- **Who waits.** A funded account (XFA) from its first live session until its first trade (its opening). Combines and
  funded accounts that have traded are P-16's in every respect.
- **The rule.** During its first **W = 5** live sessions, a waiting account takes **only an offer in the cell's state**.
  Under P-16's `able` routing the router asks the draw registered under each account's key, in its order, whether it
  can take a trade (`TierSizedDraw.can_take`, `vendor/stage2/propedge/campaign/sizing.py`; the router's check in
  `shared_days.py` `TradeRouter.begin_day`); a waiting account answers "no" to an offer out of state, and the router
  hands the offer to the next account in its order, exactly as it does for any account that cannot take a trade.
- **"Its first W live sessions"** is pinned against the engine's count: the sessions at whose routing the account's
  `FundedAccount.days` is 0 to W - 1 (T-5 checks the off-by-one through the vendored loop).
- **The fallback.** From its sixth live session, a still-waiting account takes its next routed offer as P-16 does,
  whatever the state. A fallback is a P-16 registered trade, so on a report day it may be the 07:35 mark (E-039 (1)).
- **What is unchanged:** the side (the registered coin's), the R and size (the table's), the router's order (the
  longest-waiting account first; a new account is stamped as of its first day, so accounts that last traded before it
  go first), the strict one-position rule, one trade an account a session, every other account's behaviour.
- **Why W = 5** (a declared choice, its consequences read, not argued). A trading week, a quarter of a month (21
  sessions): long enough for a state that comes and goes within nights to fire, short enough that a delay of the opening
  stays small against the journey's month. *Corrected (the review's m8 and F2):* the first version argued from "a third
  of offers by construction"; that holds only over the long run, and per year a persistent state's share follows its
  persistence. How often the wait binds for each cell is **read on the U1 replay in history's order** (A7, K5), where a
  calm spell of weeks can outlast W; it is not assumed. Other values of W are variants and are dropped (8).
- **The twin design.** The same rule with the cell's **clustered placebo** (7.1) in place of the state: the state's own
  in-state indicator shifted by a seeded offset, so the twin designs wait and reach offers as the design does
  (the second read's m2-1).
- **The seam** (18.1). The gating answer wraps the vendored draw's `can_take`, registered with the router under the
  account's key by a `FundedAccount` subclass (Q-47's `funded_account_cls` seam in `extended/gate.py`) and held strongly
  by the account (the router keeps draws weakly). `can_take` receives neither the calendar day nor the account's age,
  so the wrapper carries its account's wait counter and the (historical day, trade index) to (date, mark) lookup of
  the states. **The wrapper also counts every offer it declines** (account, historical day, trade index, the account's
  wait session): a declined offer is not a trade, so Q-70's place recorder never sees it (`extended/place_records.py`,
  its "Not here"; E-055 (4)). Q-17's adapter refuses a path that already carries `funded_account_cls`
  (`base_problems`), and its forfeiture responses set that same slot; so the family's class goes through **Q-76's
  declared keyword** (`run_starts(..., funded_account_cls=C)`, merged, E-059), which for every `forfeit_*` response
  **composes** forfeiture over it (`forfeit_class(C)`: the forfeiture's household rule raised by a denial over C; a
  class with a household rule of its own is refused, and the waiting class has none), held to Q-17's forfeiture rows
  with the wait switched off (the second read's m2-10; 18.1 item 3). **The engine refuses the ten Focused Trader models
  for any funded class but the vendored `FundedAccount`** (`lockstep.py` 1403-1408; E-059), so this family's scorecard
  reports E-007 (e)'s readings without them (13).
  Never an edit of a vendored file or a substituted vendored attribute (E-002; the lesson of E-011's first run).
- **The identities that bite** (A1, refusing; the first read's m4): with the state always on, or W = 0, the design is
  P-16 bit for bit; with the state **never on**, every waiting account's opening falls on its sixth live session; with
  the state **equal to the drawn placebo set**, every in-wait opening's (date, mark) is in the set, and every offer the
  wrapper declined was out of the set (from the wrapper's own count).

### 5.5 Where the funded openings fall: counted in stage A; what changes if they mostly fall at 08:30-09:00

**Unknown now.** No vendored file holds the marks, hours or day kinds of P-16's funded openings
(`u_xfa_day_budget.csv` section `opening_trade` has no time column; the scout's unknown 1; TASK_QUEUE Q-35, heavy,
queued). This file does not wait for Q-35; stage A's choice-block count is its substitute (the review's n6: E-021 (2)
had queued this family after Q-35; the lead records that the substitute is accepted, 20).

**Counted in stage A (A2), direction-free, on the choice block, in history's order:**

- From **P-16's U1 replay** of every choice-block start from 2021-01-04 (Q-17's adapter, the verdict arm, each start's
  history ending at 2023-12-29 so that no judged session is read), the place-recording adapter (18.1) records every
  funded opening: its (date, mark), hour, day kind, whether it is at 08:30-09:00, whether at the report-day 07:35:00
  entry, the sessions from activation, and whether the offer is in each cell's state.
- The same record for each cell's design and its two twin designs (7.1) on the same starts, plus each opening's wait
  and whether it was a fallback; and every trade at the report-day 07:35:00 entry (E-039 (1); the review's m2).
- **Counts only:** no net R, gross, won share, growth or any outcome is read or written. The replays compute outcomes
  internally to evolve the accounts; nothing of them leaves the run except the routing records.
- Each opening is counted once per start in whose replay it falls (a start is one user's journey).
- Written to the result file's `openings` section before stage B reads any outcome.
- If Q-35 has run before the pin, its counts over both blocks are a disclosed pre-read (4 item 4); **the rules here use
  stage A's count only**.

**What changes if most of P-16's choice-block openings fall at 08:30-09:00** (more than half: the trigger for the
record, not for any rule):

1. **No rule of this file changes.** The cells, the twin, C1 (offer-level, on the overnight population) and C2 (the
   design's openings against the twin design's) are fixed now; the count can move nothing.
2. **The design moves most openings out of the window into the overnight.** That is a change of schedule. The twin
   design shares it (its openings are overnight too), so it is not credited to the selection (E-023: "supply and
   schedule cancel"). The twin design against P-16 on the scorecard (13) shows the move's own effect on a user, and the
   stage-A record shows how far the openings moved.
3. **Reach.** Openings in the window would mean the overnight offers mostly go to longer-waiting accounts first (a new
   account is stamped as of its first day). A waiting account would then be offered few overnight offers, its wait
   would lengthen and **K5 (the fallback share, A7) decides** whether the cell is the declared rule at all. Fallback
   openings may themselves fall in the window, as P-16's do; their values are the labels of 5.2.
4. **The value.** C2 prices the design's own openings against the twin design's, so a window-heavy base changes nothing
   in its rule. But `mean_dv` at (c) is the map's average over P-16's openings wherever they fell; it does not know the
   mark. If those were mostly window openings, the design's overnight openings are priced by a value learnt on window
   openings -- **an assumption that carries money, reported beside the verdict**.
5. **Resolution and the slot.** An overnight 3R opening has hours more to resolve than one entered at 08:30-09:00, so K2
   and the floor are not harder; but it holds the firm's single position slot through the night and morning (D-429),
   which the scorecard's supply reading shows (the minutes the slot is held by openings, other accounts' sessions
   without a trade).
6. **The question it would raise, which this family does not ask.** The window would then be where a timing filter has
   most of its uses, and acting there is inside Stage 2 D-281 (3)'s closed branch, reserved to the operator. A family
   timing openings at 08:30-09:00 (its states frozen at the 08:25 alert, so that no window bar is read) is a
   **different family**, needing the operator's D-281 (3) ruling first. The lead records the count and that question
   under a row. This family runs as declared whatever the answer.

**If most fall overnight,** the design times openings within their own hours, the move is small, and the comparison
with the twin is mostly the selection. **On report days**, s1 is expected to fire after the 07:30 release; the count
reports the share of each design's openings on report days.

## 6. The states: the cells

### 6.1 The clock, and what a state may read

- A trading day opens at 17:00 CT the evening before (the store's rule); a slot is minutes after that 17:00
  (`extended.features.slot`); Chicago wall clock throughout, so a DST change moves no slot.
- A bar stamped hh:mm covers hh:mm:00-hh:mm:59 and closes at hh:mm + 1. **At mark m the alert is t = m - 5, and a state
  reads only the day's bars stamped at or before m - 6 and the bars of earlier sessions** (feature-rules 1).
- **The latest alert is 08:20** (the 08:25 mark): no state reads a bar of the alert's day stamped 08:30 or later, so the
  window E-030 keeps out of family B is unreachable here (T-1 shows the clock; T-2 proves it on the code).
- **Earlier sessions' bars, their 08:30-08:59 included, enter only the daily volatility terms** (H in s2 and s3, IV in
  u3). *Answered (the review's n1):* E-036 M3-2, the lead's ruling, defines Stage 2's closed opening-range branch as
  "trading rules defined on or triggered by the opening range"; whole-day ranges of earlier sessions are no such rule,
  so H and IV stand as declared.
- **The frame (the review's n4).** Every trailing window and median here runs over **P-16's walked sessions**: the
  states' module is handed the bars of P-16's walked sessions only, so the library's trailing median (its 20 prior days
  of the frame) is over 20 prior walked sessions. Every window over the day's bars is bounded at the day's first bar, as
  the library's `_win_sum` is; no negative-index slicing is used at overnight slots (it would wrap to the end of the
  same day, the future).
- **The library where it serves.** `extended/features.py` computes its features at RTH alerts only (08:30-15:00; its
  `compute` refuses others), so none of its columns is used as is. Reused, never copied: its `grid` (the bars as day x
  slot arrays), `slot`, its trailing-median helper (for x3's slot median), and `rv_tod`'s formula, which x3 extends to
  overnight alerts (T-2 asserts the equality at RTH alerts, where the library computes it).

### 6.2 Common quantities

Every quantity is a log ratio of prices **within one trading day**, so it is scale-free (feature-rules 2: no raw level)
and never differences prices across a roll.

| quantity | formula | reads |
|---|---|---|
| LR(d) | ln(max high / min low) over day d's bars (17:00-15:59) | day d's bars; used only on later days |
| LRS(d, m) | ln(max high / min low) over day d's bars stamped 17:00 .. m - 6; **missing if fewer than 15 bars are present** (a thin night: a missing-bars rule, not the start mark) | day d's bars up to m - 6 |
| DIS(d, m) | abs(ln(close of the last bar stamped at or before m - 6 / open of day d's first bar)) | day d's bars up to m - 6 |
| har(x)(d) | (x(d-1) + mean of x over d-5..d-1 + mean of x over d-22..d-1) / 3: an **unfitted** HAR-type mean (Corsi 2009's daily, weekly and monthly terms, equal weights -- the scout's "HAR-type mean"); defined with 22 prior values | the 22 prior walked sessions |
| H(d) | har(LR)(d): the day's forecast range | the 22 prior walked sessions' whole days |
| HS(d, m) | har(LRS(., m))(d): the forecast of the range so far at mark m | the 22 prior walked sessions' same window |

### 6.3 The four states

| cell | state | quantity X | in state when X's share (6.4) is | defined from | reads (all closed by the alert) | sign (1 (iv)) |
|---|---|---|---|---|---|---|
| **s1** | unexpected volatility | U(d, m) = ln(LRS(d, m) / HS(d, m)) | **above 2/3** | the 17:30 mark | day d's bars 17:00 .. m - 6; the same window of the 22 prior sessions; U at m over the 250 prior | positive |
| **s2** | a night already trending | T(d, m) = DIS(d, m) / H(d) | **above 2/3** | the 17:30 mark | day d's first open and its close at m - 6; the 22 prior whole days; T at m over the 250 prior | positive |
| **s3** | low predictable volatility | H(d) (a daily state: every mark of the day alike) | **below 1/3** | 17:00 | the 22 prior whole days; H over the 250 prior | positive |
| **u3** | the offer forecast fast (family R's (u3)) | y_hat(d, m), section 6.5 | **above 2/3** | 17:00 | 6.5 | negative |

Notes, each a disclosure or a recorded interpretation:

- **The 17:30 start of s1 and s2 (the review's m1).** One rule: a "night so far" quantity is read only after half an
  hour of the night, so the 17:30 mark (alert 17:25, bars stamped 17:00-17:24) is the first. It is a declared choice;
  LRS's 15-bar minimum is a separate rule for thin nights, not its reason.
- **s1 against the scout.** The scout's forecast was the same mark's median over the 20 prior sessions. Here it is the
  HAR mean of the same window (1, 5 and 22 sessions), so a rise over the last few days counts as predictable, not as a
  surprise. That is closer to Bianco & Renò's split of realised volatility into its expected and unexpected parts.
- **s2 against the scout.** "Above a declared multiple" is replaced by the mark's top third: DIS grows with the time
  since 17:00, so any fixed multiple would fire mostly late in the night and make the state a clock. The twin cancels
  the clock anyway; the third keeps the firing share even across marks over the long run.
- **s2 and s1 against S2 (D-581).** S2's trend state compared abs(c[t] - session open) with its trailing 20-session
  median at the mark; s2 normalises it by the day's forecast range and ranks it over a year, top third. S2's volatility
  cells ranked the last 30 bars' range; s1 ranks the whole night's range against its forecast. Relatives, redefined;
  S2's readings are seen (2).
- **s3.** Calm days resolve slowly: S2's low-volatility cell failed resolution at the longest offered R in its worst year
  (D-582 (2)). K2 kills s3 on resolution before any lift is read. s3 is also the cell whose persistence most threatens
  its power (6.6).
- **u3.** The mirror of s3 in its predictable part, with today's surprise so far added (x3). In-state and out-of-state
  deviations sum to zero within a stratum, so s3's and u3's lifts are related; both are counted, and stage B's
  selection device is computed jointly (10).
- **No state reads a side, an outcome, a calendar beyond P-16's day kinds, or a price level.**

### 6.4 The rolling third

- For a quantity X at mark m (or daily, for s3), its **share** p(d, m) = (the number of the 250 prior walked sessions'
  values of X at m that are below X(d, m), plus half the equal ones) / their count -- S2's mid-rank rule (D-581 (6))
  over a year instead of a month. At least 120 prior values, else undefined (not in state).
- "Above 2/3" and "below 1/3" are strict.
- **Why 250.** A year's reference: "low" in s3 means low for the past year, not for a calm quarter. For the ratios of
  s1, s2 and u3 the window matters less.
- **It is a past-only normaliser** (feature-rules 2: "rolling or expanding windows ending at t - 1 min"), computed the
  same way at every session from bars alone. No value of it is chosen from data or read from an outcome. On the judged
  block its reference reaches back into 2023: that is the past, not a fit.
- **What its share is (corrected, the review's m8).** On an iid quantity the state fires on about a third of offers
  every year (T-1 shows it). On a persistent quantity it fires on about a third **over the long run**, but per year its
  share follows the quantity's persistence and can be far from a third, a few sessions in one year and most of another.
  So the supply per year is read in stage A beside K1 (A5), and no rule here assumes a third per year.

### 6.5 u3's forecast: the only fitted values, inside the choice-block walk-forward (E-031 (1))

Restated from family R's draft (section 6) so that this file stands alone; family R's draft is unreviewed (E-028 (2)),
so u3's forecast is reviewed here as restated. If family R is pinned first, the two procedures must be the same code
(T-7).

- **The target** (a label, used only for fitting, never as a feature): IV(d, m) = the sum of squared one-minute price
  changes, in points^2, over day d's bars from the entry bar (stamped m) to the bar ending 15:08 CT (the first change
  that bar's close less its open, then each present bar's close less the previous present bar's close); M(d, m) = the
  mean of IV(d', m) over the 22 prior walked sessions with a value; y = ln(IV(d, m) / M(d, m)). Points^2 enter only as a
  ratio across days.
- **The regressors**, each closed by the alert:
  - x1 = ln(IV(d - 1, m) / M(d, m)), yesterday's same window;
  - x2 = ln(mean of IV over the 5 prior sessions / M(d, m)), last week's;
  - x3 = 2 x `rv_tod` at the alert t = m - 5: ln((rv_60 / its median over the 20 prior walked sessions at the same
    slot)^2), rv_60 the root mean square of one-minute close changes over the bars of the day stamped t - 61 .. t - 1,
    the window bounded at the day's first bar (at the `asia` band's first marks it reaches back to 17:00 and no
    further); at least 10 sessions for the median, else missing.
- **Bands** (family R's 6.3, the overnight ones): `evening` 17:00-17:55 (x1, x2: under an hour of the day's bars);
  `asia` 18:00-01:55 and `london` 02:00-08:25 (x1, x2, x3). Family R's `open` and `day` bands are not used (no population
  mark lies there).
- **The fit:** ordinary least squares of y on an intercept and the band's terms, one observation per (session, mark),
  weight one: 3 + 4 + 4 = **11 coefficients**. Deterministic; refused if a band's design matrix is rank-deficient (the
  failure protocol).
- **The walk-forward, inside the choice block only:** test years 2021, 2022 and 2023, each fitted on the choice block's
  sessions before it less the last 22 (expanding; the first fold trains on 2020 after its warm-up). A forward walk needs
  no purge: every IV ends at 15:08 of its own day. Out-of-fold forecasts feed stages A and B.
- **The final fit:** every choice-block session with a value. Its coefficients are serialised to canonical JSON and
  hashed; **the hash is pinned in a decision row before the judged block is read**; the judge's entry point cannot fit
  (T-9). Nothing is fitted, chosen or tuned on the judged block.
- **y_hat's share** (6.4): the 250 prior sessions' y_hat at the same mark, each computed with the same fit as day d's (in
  a test year that fold's; on the judged block the final fit). Every input precedes d.
- **No calibration** (family R's 6.4 maps the forecast to a probability; here only its rank matters), so the 10
  calibration values family R fits are not fitted here.

### 6.6 Each cell's persistence, fill intensity and the drop rule (E-035 (6); E-052 (1); the reviews' F4, m2-9; E-073 item 2)

Q-16's calibration found that a placebo-selection test's power depends far more on how persistent the filter is than on
its firing share, and that a filter persistent for a quarter cannot be tested on the judged block (calibration note
7.3). Its Table 9 gives the detectable difference by persistence class (`offer`, `window`, `session`, `block5`,
`block21`, `block63`) and firing share. Its figures are exploratory until Q-55's clean rerun (E-035 (4)); none is cited
or typed here, and the drop rule below reads them from Q-55's file at the pin.

**Fill intensity (E-052 (1)).** Beside the selection's persistence, E-052 (1) asks for the persistence of the **counts**
each line's statistic weights: here the in-state offers per session (C1, C1-close) and the openings per session (C2).
When a few blocks hold most of the counts, the cluster-robust variance has fewer effective clusters than its df says
(the pass-line review's M1); none of Q-16's nulls let counts persist across sessions. **This family's counts move with its
states**, so they persist exactly as the states do: K0 (A11) checks `cons`'s size on each cell's own counts before
stage B, and on the pick's judged counts before any outcome is read.

| cell | what can make it persist | deciding class (one) | why that class | fill intensity: in-state offers a session (C1) and openings a session (C2) |
|---|---|---|---|---|
| **s1** | the range so far only grows through the night, so once a night runs ahead of its forecast it tends to stay ahead for the rest of it; the next day's HAR forecast absorbs the surprise, so the clustering across nights is short (volatility surprises bunch for a few nights) | **`window`** | its selection is a run of offers within a night, which is Q-16's `window` model (a contiguous run of offers in each session at a random start); `block5` selects whole sessions for five sessions together, which s1 never does -- it fires on part of a night and its run across nights is a few nights, not a fixed week. The cross-night bunching that `window` leaves out is K0's and A9's to read on the cell's own counts and pattern | a share of each night, varying night to night, bunched over a few nights; C2: openings spread over nights, bunched where surprises bunch |
| **s2** | a night's displacement from its open changes slowly through the night; across nights, trending nights are close to independent (daily returns carry little autocorrelation), normalised by the forecast range | **`window`** | a run of offers within a night, near-independent across nights: Q-16's `window` model | a share of each night, close to independent across nights; C2: spread |
| **s3** | a daily state; the HAR forecast's 22-session term and the 250-session reference make calm spells last weeks to months | **`block21`** | a daily state, every offer of a session together, its runs set by the HAR forecast's 22-session term, about a month; `block63` would be the quarter-long regime, which the state's own threshold crossings break up more often | **all or nothing a session, in runs of weeks to months** -- the most count-persistent cell; C2: openings bunched in the calm spells |
| **u3** | its daily terms are ratios to the trailing month, which revert within weeks; x3 moves within the night | **`block5`** | its daily terms hold for days, about a week, while `session` (whole sessions drawn independently) has no persistence across sessions at all | mostly all or nothing a session, in runs of days; C2: bunched in fast spells |

**The drop rule, stated whole (applied by the lead at the pin; no figure typed into this file):**

- **The file:** Q-55's `results/calibration_power.csv`, written with its manifest by `scripts/q55_calibration.py` from a
  clean checkout (E-035 (4)).
- **The rows:** `part` = `two_sample`, `df_rule` = `treated`, `form` = `placebo-selection` (the placebo-selection twin's
  power rows, Table 9's) with `method` = `cons` and **`k` = 15** -- Table 9 carries `cons` at k = 11 and 15 only, and
  this family's k is 12 to 15, so k = 15 is the strictest it can face (the second read's m2-9).
- **The value row: `value` = `net3`** -- Table 9's other row, `win1`, is the coin's win at 1R, another bracket in another
  unit; `net3` is net R at 3R, this family's bracket and its lines' unit. It is the coin side's own net R, not the
  side-symmetric c (whose direction noise is removed), so it is an upper guide to c's detectable difference, the
  conservative direction for a rule that keeps a cell.
- **The class:** the cell's one deciding class (the table above) as `model`.
- **The share: `share` = 0.25** -- each state fires on about a third of its offers over the long run, by the rolling
  third's construction (6.4); of Table 9's grid of shares (0.02, 0.05, 0.10, 0.25, 0.50) the nearest to one third is
  0.25 (one third less 0.25 is a twelfth; 0.50 less one third is a sixth).
- **The test:** if that one row's `difference80` is empty -- 80 % power not reached inside the grid of shifts, which
  reaches 40 median standard errors (`scripts/q16_calibrate.py`'s grid; the second read's n2-7) -- **the cell is
  dropped at the pin and counted** (E-035 (6): a cell the block cannot judge spends nothing by being run, and is
  still counted). Otherwise it stays. A cell with no such row is dropped and counted too.
- **Who applies it:** the lead, mechanically, at the pin, recording the dropped cells in the pinning row -- no
  confirmation, no discretion, nothing written into this file. The drafter expects s3 to be dropped by it.

Readings beside the rule, deciding nothing:

- **"Inside Table 9's grid" is a weak condition** (40 median standard errors), so power against the money bar is A9's
  job, not the drop rule's.
- **What the toys show (18.3), as an illustration, not a result:** in the nested two-sample form, sample 2 (every offer)
  holds the selected offers, so a lift on a clustered selection also raises the between-block spread of the population's
  mean, and the standard error grows with the lift. For a whole-session selection in runs of weeks the t statistic
  then rises toward a ceiling set by how unevenly the selection fills the blocks, and power at the family's level can
  stay well short of one however large the lift; a within-night window selection does not have this ceiling. This is
  the shape of Table 9's "--" for its block classes (Q-16's power code shifts both samples, as here).
- **At run time:** stage A reports each cell's run lengths on 2021-2023 and stage C the pick's on the judged block,
  before any outcome, with the class they imply -- beside, never moving a cell's deciding class.

## 7. The twin and the estimands

### 7.1 The twin (E-023 (2))

- **The placebo-selection twin:** a random filter that fires on **the same number of population offers as the cell's
  state in each stratum g = (mark, day kind, calendar year)**, drawn uniformly without replacement, seeded
  `default_rng([20261982, c, b, d])` (c the cell's index, 0 to 3 in the order s1, s2, s3, u3; b the block: 0 judged, 1
  choice, 2 the confirmation; d the draw: 0 and 1).
- So the time of day, the report days and the year cancel, as supply and schedule do, and **only the state's choice of
  day within a mark is measured**.
- **In C1 the twin enters as its exact expectation**, the population mean of each stratum: *answered (the review's
  n2):* that is the form Q-16 calibrated ("carries no placebo noise", calibration note 7.3). A seeded draw is reported
  beside (draw 0).
- **In C2, V_B and the scorecard the twin is a design, and its placebo is clustered (the second read's m2-1).** The
  waiting rule with **the state's own in-state indicator shifted circularly**, within each (calendar year, day kind)
  sequence of sessions, by a seeded uniform offset (`[20261982, c, b, d]`, d = 0, 1), all marks of a session moved
  together: offer (session j, mark m) is in the twin's selection when the state held at (session j + offset, mark m)
  of the same sequence. It keeps each stratum's count exactly (a shift permutes the sessions of a sequence) and the
  state's runs (up to the wrap), so the twin designs wait and reach offers at the same routing positions as the design;
  its expectation over the offset is the stratum's share, so its offers are the stratum mean in expectation, as the
  exact twin's are. Two draws (d = 0, 1) pooled for C2 and V_B; draw 0 for the scorecard.
- **What the clustered twin still does not match:** which particular sessions are in state -- the state's alignment
  with the night's own routing (how fast earlier trades exit). That residual is stated beside C2 (7.4). The per-offer
  placebo, which matched neither the runs nor the waits, is no longer used for any design.

### 7.2 C1's estimand: the lift over the twin at the offer level

    L_c = (1 / N_F) x sum over the cell's in-state offers i of ( c_i - mu_g(i) )

- mu_g is the mean of c over **all** population offers of stratum g -- the placebo's exact expectation; mu_g(i) is that
  of offer i's stratum; N_F the number of in-state offers. (s names a session throughout, g a stratum.)
- **The call (the review's F1):** `extended.lift_bound.placebo_selection_bound(y, session, selected, n_sessions,
  level=0.05 / (k (k + 1)))` with `y = c - mu_g` for **every population offer** (sample 2), `selected` the in-state flag,
  `session` the offer's ordinal in the block's calendar (every trading session counted), at the module's
  `SHIPPED = "cons"` and `DIFF_DF_RULE = "treated"` (E-035 (2); the module at blob
  `984f3467a4a05aa790d3ea43e94ac7761f0725b2`, E-052). The runner asserts the level equal to `family_level(k)` for the
  pinned k, and `n_sessions` and the session list equal to Q-83's judged-block count and sha256 (E-052 (3)'s
  assertions, carried here).
  - **The strata enter by the centring.** The function compares the selected offers' mean with every offer's mean and
    has no strata. On y the second mean is zero by construction and the estimate is exactly L_c; on the raw c it would
    add the strata-composition term -- the in-state offers' mean stratum mean less the population mean -- which a firing
    share that differs by year makes non-zero with no selection effect at all (T-1 holds both identities; the review's
    check 1).
  - **The variance** is the module's: cluster-robust on 21-, 42- and 63-session blocks from the linearised residual
    block sums of the two samples, the block count and df those of the sample occupying fewer blocks (the treated
    rule). The first version's raw in-state session sums z_s are **dropped as a variance series**: they carry each
    session's offer count, and a variance of them is not L_c's (the calibration note's 1.3 correction for F-02).
  - **The critical value** is section 11's: each member's at the larger of its t and B2's.
- **C1-close:** the same with c and mu_g from the `close` flatten convention (5.3).
- The seeded draw beside (`[20261982, c, 0, 0]` on the judged block) is a comparison of two random subsets: it is read
  by `two_sample_bound`, never in a line.

### 7.3 The halves

- L_c^long on l_i with its strata means, L_c^short on r_i likewise; L_c = (L_c^long + L_c^short) / 2.
- Persistence raises both. A drift aligned with the state raises one and lowers the other at first order (1 (i), T-1).
  **C3 requires both above zero** (point estimates).

### 7.4 The value line: the design's openings against the twin design's (place (c); the review's F3)

**Why a difference.** The offer a waiting account opens at is selected by the router: under the one-position rule it
is the first offer after earlier trades on that night have exited, so it depends on how fast that night resolves, its
kind mix and its persistence. So the deviation at a reached offer is not mean-zero even for P-16, which has no state
(the first read's check 5, a toy). The twin designs' openings carry the same routing selection; **the difference
removes it to first order** (the second read's m2-1). With the clustered twin (7.1) the twin designs wait and reach
offers as the design does, which removes most of what remains; what still remains -- the state's own alignment with
the night's routing, which the shifted twin does not share -- is **not in B2's null for C2** (B2 holds the uses fixed
and draws values from other sessions, so its D\* is centred at zero by construction). It is stated beside C2 with the
verdict, as **an assumption that carries the value**, and stage B's pick by V_B inherits it (the second read's n2-9;
mean_dv(c) is a common positive factor across cells, so the value map cannot move the pick).

- **The samples.** On the paired U1 replays in history's order (4 item 5) -- the design and its two twin designs on the
  same starts -- every funded opening j of a start (in-wait or fallback) is one use: its offer i(j), its value
  y_j = c_i(j) - mu_g(i(j)) at 3R, and its session. Sample 1: the design's openings; sample 2: the twin designs'
  openings, both draws pooled. A historical offer opened in several starts' replays is several uses; their dependence is
  carried by the session clustering.
- **The fallbacks' values.** A fallback can open at any P-16 mark, the 08:30-09:00 marks and the report-day 07:35 mark
  included; its y is that mark's label against its own stratum (5.2). Fallbacks enter both samples at their own values.
- **The per-opening difference** D = mean of y over sample 1 - mean of y over sample 2, by `cons` in the module's
  two-sample form, `extended.lift_bound.two_sample_bound(y_1, s_1, y_2, s_2, n_sessions, level=...)` (the treated-
  cluster df; E-035 (2) adopts the same statistic for both two-sample forms; `placebo_selection_bound` is its nested
  case, and here the samples are two designs' openings), each member at the larger of its t and B2's critical value.
- **The value:** **V_line = u_d x mean_dv(c) x D / (1 + 3)** dollars a year of a five-seat campaign, with u_d the
  design's openings per start-year in its replays and mean_dv(c) = `u_value_map.csv`, section `place_values`, base
  `p16`, place `c_funded_opening`, measure `mean_dv` (a win over a loss); to first order a lift of lambda R at 3R is
  lambda / 4 of win probability (the map's definitions). C2 reads V_line at D's lower bound.
- **Beside, deciding nothing:**
  - **V(P-16)**: u_P16 x mean_dv(c) x (mean of y over P-16's openings) / 4 -- the base's own routing deviation, so its
    size is seen;
  - **V(design)** undifferenced, and V(design) - V(twin design) in dollars at each design's own uses (it also carries
    the difference in uses, which is schedule, not selection);
  - V's in-state and fallback parts;
  - **V_other**: the same difference over the designs' trades at places (b), (d) and (e), each at its own R and against
    its own stratum's mean at that R. *Reading (the review's n3):* the reason it was called "expected small" -- that
    persistence cannot act at 1R -- holds for gross only; at 1.5R persistence acts, and costs differ by kind. It stays
    beside: an assumption that carries money, said with the verdict.
- **What V is not** (readings, the review's n5 and n8): it is **gross of the wait's own cost** -- the waiting XFA's idle
  sessions and the solver's slot rent for a seat that waits are not netted (the scorecard shows the wait); and it is
  **first-order**: it turns an R difference into win probability at 1/4 and prices it by the solver's binary `mean_dv`,
  while a difference made of kind mix or breakeven exits is not a change in win probability. The value-map price at the
  bound is not calibrated (calibration note 7.4 item 10).

## 8. Parameters: fixed, fitted, searched, dropped

| parameter | what it is, in a phrase | class | value | source or reason |
|---|---|---|---|---|
| market, bars | what is traded and read | fixed | NQ 1-minute bars; MNQ micros sized by the table | E-002 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md; `config/windows.yaml` |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | feature-rules 4; CHARTER 3 |
| stages A and B's span | where the choice block's lifts and gates are read | fixed | 2021-01-04 .. 2023-12-29 | warm-up and u3's first fold (4 item 2) |
| base | the design the filter acts on | fixed | P-16 as registered (5.1), its report-day 07:35 entry kept | E-004, E-010, E-039 (1) |
| stop | the loss distance | fixed | 150 ticks (37.5 points) | P-16 |
| R | the bracket the lift is read at | fixed | 3 | the opening's ask; persistence cannot act on the 1R gross (1 (i)) |
| population | the offers a state may pick | fixed | P-16's marks 17:00 .. 08:25 CT (report days 07:40 ..) | 5.2; D-281 (3); E-007 (d); E-039 (1) |
| labels | values for fallbacks | fixed | every P-16 mark, both sides, every table R, labels only | 5.2; the review's F3 |
| entry | how a trade starts | fixed | P-16's: market at the first bar at or after the mark, one tick adverse; by hand; the alert at m - 5 | D-266; E-008 |
| walk | how a trade ends | fixed | `extended.walker.STAGE2`; for C1-close `Rules("fo_stage2_close", FLAT_ENTRY, "close", True)` (5.3) | E-011; the second read's m2-7 |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| the states' formulas | what each cell waits for | fixed | 6.2, 6.3 | the literature (1 (ii)); the scout's 5.1 |
| first defined mark | when s1 and s2 exist | fixed | 17:30: half an hour of the night | 6.3 (the review's m1) |
| thin-night rule | a missing LRS | fixed | fewer than 15 bars present by m - 6 | 6.2 |
| HAR terms | daily, weekly, monthly | fixed | 1, 5 and 22 prior walked sessions, equal weights (s1-s3) | Corsi 2009 |
| the rolling third | the state's threshold | fixed | the 250 prior walked sessions' mid-rank share, at least 120; above 2/3 (s1, s2, u3), below 1/3 (s3) | 6.4; S2's rule over a year |
| u3's forecast | the fast forecast | fixed form, **fitted in-fold** | 11 coefficients by least squares, three folds and the final fit | 6.5; E-031 (1) |
| u3's so-far term | today's surprise | fixed | 2 x `rv_tod` at m - 5 (60 minutes, bounded at the day's first bar; 20-session slot median, at least 10) | `extended/features.py`; family R |
| W | the longest wait | fixed | 5 live sessions (`FundedAccount.days` 0 to 4 at routing) | 5.4 |
| the fallback | after W | fixed | the next routed offer, a P-16 registered trade | the scout's rule; E-039 (1) |
| routing | who gets an offer | fixed | P-16's, unchanged | 5.4 |
| strata | what the twin matches | fixed | (mark, day kind, calendar year) | E-023 (2); 3 (report days) |
| the twin's form | C1's comparison | fixed | the exact expectation (the population mean of the centred values); one seeded draw beside | E-035; calibration 7.3 (the review's n2) |
| the twin designs | C2's, V_B's and the scorecard's comparison | fixed | the clustered placebo: the state's indicator shifted by a seeded offset within each (year, day kind) sequence; two draws pooled (draw 0 for the scorecard) | 7.1, 7.4; the second read's m2-1 |
| the pass statistic | every line's test | fixed | `cons` (`extended.lift_bound.SHIPPED`), treated-cluster df (`DIFF_DF_RULE`); `placebo_selection_bound` on y for C1 and C1-close, `two_sample_bound` for C2; the modules at blobs `984f3467...` and `f5b29710...` | E-035 (2); E-052 |
| each member's critical value | t21w, t42w, t63w | fixed | the larger of its t (its treated df) and B2's (1 - level) quantile of the same member | 11 |
| B2 | the conditional null | fixed | section 11: the realised judged population as the null, slow components centred within the block; stationary bootstraps of mean block 63 within day kind; a slow sign switching 1/63 per session, its amplitude the largest of (a), (b) and (d); exactly 1,000,000 replicates per line | family B's form (E-030, E-040); E-051; the second read's m2-3, m2-11 |
| the calendar for the wait and value | where waits and openings are read | fixed | the U1 replay in history's order | 4 item 5 (the review's F2) |
| C2's bar | the least worth | fixed | $500 a year at the family's level, on V_line | `u_value_map.csv` section `bar` (`target=500`); F-02, F-B |
| valuation base | where a win is priced | fixed | `p16`, place (c) | `u_value_map.csv` |
| K1 | the least supply | fixed | 21 sessions holding an in-state offer in each of 2021, 2022, 2023 | a month of sessions |
| K2 | resolution | fixed | at most 5 % unresolved at 3R among in-state offers, overall and every year; 4 % in the worst year to be eligible as the pick | D-212; family B's M2-4 margin |
| K5 | the wait binding | fixed | at most one half of a design's openings taken as fallbacks, on the choice-block replays | the scout's K5; 4 item 5 |
| the drop rule | a cell the block cannot judge | fixed | 6.6: Q-55's `calibration_power.csv`, placebo-selection rows, `cons`, k = 15, `net3`, the cell's one deciding class (s1 `window`, s2 `window`, s3 `block21`, u3 `block5`), share 0.25; dropped if `difference80` is empty; applied by the lead at the pin | E-035 (6); the second read's m2-9; E-073 item 2 |
| K0 | the counts' persistence | fixed | `cons`'s size at the family's level on the sign null with each cell's own counts, 200,000 replications; killed if the 95 % interval lies wholly above nominal (A11); at stage C, a pass not claimed | E-052 (1) |
| A10's consequence | `cons` lax on c | fixed | the deciding rule on a pseudo-judged split; lax too: the cell closed, counted (A10) | the second read's m2-4 |
| A4's default | if u3's forecast has no skill | fixed | u3 closed, counted | the review's n7 |
| MDL factor | when the family is only a screen | fixed | 3 | family B 8 item 8; family R |
| campaign | floor (iii) only | fixed | the design's gate campaign, 500 paths, seed 20261983 | E-022 (2) |
| other W (1, 2, 3, 10 sessions) | a shorter or longer wait | **dropped** | -- | each a variant; W is the rule |
| other thresholds (quarters, fifths) or a combined state (s1 and s2) | finer or joint states | **dropped** | -- | each a variant; S2's lesson (D-582: no post-hoc finer cut) |
| a sided cell (follow, fade) | a direction rule | **dropped** | -- | S1 and S3 read it (2); a direction family, judged by the coin twin |
| the 25-point US cell, 09:00-12:00 at R 2.5 | the scout's optional US-hours cells | **dropped** | -- | P-15's base and US hours; its identity is not reproduced here; a later family |
| the opening-window marks 08:30-09:00 | where P-16's openings may fall | **out of the population** (labels only) | -- | D-281 (3); 5.5 item 6 |
| window offers passed through during the wait | taking 08:30-09:00 offers unfiltered | **dropped** | -- | dilutes the filter by the window's share; a variant |
| an opening-first routing priority | giving a waiting account the in-state offers first | **dropped** | -- | changes every other account's trades; a different design |
| the gate's independent-day table for the wait or the value | `SharedDayTable` | **dropped** | -- | destroys the states' runs (4 item 5; the review's F2) |
| VIX or VXN states | implied volatility | **dropped** | -- | not on disk; whether Cboe's history is free without sign-up is unverified (the scout's unknown 6); the atlas read it on 2009-2014 |
| dealer gamma | the mechanism's own variable | **dropped** | -- | S&P-only options data, a purchase (D-137) |
| family R's calibration | the forecast to a probability | **dropped** | -- | u3 uses the forecast's rank only |
| ISM and GDP day exclusions | release days not on disk | **dropped** | -- | no calendar on disk; E-034 decided the hold (3) |
| the reverse walk-forward | choose late, judge early | **dropped** | -- | E-031 (2): it would make the judged block choose or fit; the year-by-year readings go beside (12) |

**Searched: nothing.** The trial count is the four cells.

## 9. Stage A: the gates, before any outcome (2021-01-04 to 2023-12-29)

Stage A reads **bars** (the states, u3's forecast), the walks' **kind columns** (resolution, side-free, as D-525 (4)
does), the U1 replays' **routing records** (where openings fall) and the counts K0 reads, and, for A9 and A10 only,
**the population's centred values' dispersion under random selections** -- never a cell's in-state mean. It reads no lift
of any cell. Every kill is counted and recorded.

**A0. The whole-window identities, after the pin and before run 1 (refusing; the second read's m2-2; E-073 item 1).**
The identities that compare whole-window registered objects need the judged block's bars and walks, which the reader
admits only from an identity script. So they run in **`identity/family_o_identity.py`**, under its own identity row,
from a clean run under the lock, **after the pin, after the infrastructure identities (header) and the family's build,
and before run 1**, and are held there as Q-22's and Q-51's are:

1. the population builder's P-16 cell gives P-16's trades, `TRADES_SHA256` exactly; the labels at every P-16 mark (5.2)
   reproduce the cell's coin-side columns at those marks;
2. **the design with the state always on** (every offer in state): through the family's gate call
   (`extended.gate.run_gate(funded_account_cls=...)`), P-16's gate paths, 500 paths at seed 20261206, every `PATH_COLS`
   column to 1e-6 (E-004's comparison); and through Q-17's adapter with the family's class (through Q-76's keyword,
   5.4), P-16's U1 start rows `p16`, both arms, every start (E-010's comparison);
3. **the design with W = 0**: the same two comparisons;
4. **Q-51 HOLDS** (E-044 (3): P-14's and P-16's registered gate runs at 500 paths through `extended/gate.py`, with no
   class and with the pass-through class) is cited, not re-run; and Q-17's adapter identity
   (`identity/user_beside_identity.py`) is re-run with the family's class passed and switched off, the forfeiture rows
   with the composed class (5.4) and the wait switched off among them.

**A1. Identities in run 1 (refusing).** Any failure stops the family; the failure protocol applies.

1. **The pass-line code's blobs:** `git rev-parse HEAD:extended/lift_bound.py` is
   `984f3467a4a05aa790d3ea43e94ac7761f0725b2` and `HEAD:extended/p_bound.py` is
   `f5b29710e243f97a2795e57f6458512fea99199b` at the run's commit, else the run refuses (m2-8; E-052). Run 2 checks
   the same.
2. E-011's walker identity holds at the build's commit.
3. A0's identity row exists and records every A0 item as held.
4. **The state never on** (the first read's m4): on the U1 replay of P-16's choice-block starts, every waiting account's
   opening falls on its sixth live session (its first routed offer once `FundedAccount.days` reaches 5), and from there
   on the path is P-16's routing with every opening so delayed.
5. **The state equal to the drawn placebo set** (m4): every in-wait opening's (date, mark), read by the place-recording
   adapter, is in the placebo's set; and every offer routed to a waiting account and out of the set was declined -- read
   from **the gating wrapper's own count of declined offers** (5.4): a declined offer is not a trade, so the place
   recorder does not see it (E-055 (4)).
6. **The restricted replay:** with each start's history ending at 2023-12-29, the replay's start rows equal U1's on
   every start whose horizon ends inside the choice block.
7. The place records' identities, **cited as pre-run conditions** (header): Q-70's (E-055) -- **P-16 at 4 paths**,
   every `PATH_COLS` column and row with recording on equal to the same call with it off, and **P-16 and P-14 at 100
   paths, the bound arm, U2's seed**, whose recorded counts by place reproduce `u_value_map.csv`'s
   `trades_per_year_records` for `p16` and `p14` (`identity/place_records_identity.py`, Q-89) -- and Q-94's (E-068) on
   the U1 replay: `extended/replay_records.py`'s `ReplayRecorder` through `user_beside.run_starts(..., recorder=)`,
   recording on equal to off bit for bit and the recorded openings the replay ledger's (its 19 synthetic tests), and
   U1's start rows for P-16 and P-14 with recording on, every start (`identity/replay_records_identity.py --u1-starts
   all --row E-068`, Q-101). In run 1, this family's own on top of them, at 4 choice-block starts: with the recorder and
   the family's class both given and the wait switched off, every start's row equals the unrecorded vendored-class
   replay's; the fallback flags, the joins by offer id and the declined-offer counts (18.1 item 4) reproduce a
   hand-checked start.

**A2. Where the openings fall (5.5), on the U1 replay in history's order.** The counts for P-16, each cell's design and
its two twin designs, written to the `openings` section: by mark, hour, day kind, the 08:30-09:00 share, the report-day
share, **the trades and openings at the report-day 07:35:00 entry** (E-039 (1)), the sessions from activation, the
in-state share of P-16's own openings, each design's wait distribution and fallback share. Counts only.

**A3. No look-ahead (refusing).** The states' and u3's shift-invariance test (T-2): every bar stamped at or after
m - 5 is replaced by a seeded random walk (`[20261981, j]`), and separately deleted; every state at (d, m) and every
y_hat must be unchanged, at no fewer than 200 (session, mark) cuts including the first marks after 17:00, the 17:30
mark, **the `asia` band's first marks 18:00 and 18:05** (where rv_60's window reaches back to 17:00; the review's n4), a
roll day and a DST change; replacing the alert day's 08:30-08:59 bars changes no state (E-030). No state all-undefined
or constant.

**A4. u3's forecast skill (a control).** On 2021-2023 out of fold, per band: the per-session mean squared error of y
under the HAR against under y = 0. The improvement's one-sided 95 % lower bound must be above zero, by circular
21-session blocks, 2,000 draws (`[20261980, 0]`), in every band. **Default, declared now (the review's n7): if it fails,
u3 is closed, counted**, and the failure protocol runs on the build (a defect, or a market without the stylised fact);
no other cell is affected.

**A5. Supply (K1, a kill).** For each cell: in-state offers per session, **by year**, hour and day kind; the in-state
share per stratum and **per year** (m8: about a third only over the long run). **A cell with fewer than 21 sessions
holding an in-state offer in any of 2021, 2022 and 2023 is killed.**

**A6. Resolution (K2, a kill).** Among each cell's in-state offers, both sides pooled, the unresolved (flatten-kind)
share at R = 3 must be **at most 5 % overall and in each of 2021, 2022 and 2023**. Else the cell is **killed**. Reported
beside: the same for the whole population, and each cell's worst year (stage B's 4 % eligibility margin).

**A7. The wait (K5, a kill), on the U1 replay in history's order.** **A cell whose design takes more than one half of
its openings as fallbacks is killed**: it is not the declared rule. Reported: the wait distribution, the twin designs'
waits and fallback shares (the clustered twin should wait about as the design does, 7.1), each cell's in-state run
lengths (6.6), and **the censored waits** -- accounts still waiting when a start's truncated choice-block history ends,
which are the long waits K5's share cannot count -- beside K5 (the second read's n2-8).

**A8. Realised risk.** The openings' realised risk against intended in P-14's registered allowance-capped form (E-022
(1), E-032). A build check: the table's sizing is unchanged.

**A9. Power on record.**

- For each surviving cell: the minimum detectable lift (MDL) of C1 at the family's level on the judged block, at 80 %
  power, from section 11's machinery at the judged block's session count, with the cell's choice-span in-state pattern
  and the population's centred values on the choice span (their dispersion and dependence; never the in-state mean,
  which stage B reads first), beside 6.6's Table 9 figure.
- The bar in net R: lambda_bar = 4 x $500 / (mean_dv(c) x u_c), u_c the cell's design's openings a start-year on the
  choice-block replays (A2).
- **If the MDL exceeds 3 x lambda_bar at every surviving cell, the family is declared a screen** (section 14 says what
  its pass means). Written before stage B reads any lift.

**A10. The level on the side-symmetric value (a control; the review's F1).** Q-16 calibrated `cons` on the coin side's
own outcome (11 item 5). On the choice span's population, random selections independent of the outcomes are drawn in
Table 9's six persistence classes at shares 0.25 and 0.5, 2,000 per class and share (`[20261984, class, share, j]`),
and `cons` with the treated df is applied to y = c - mu_g through `placebo_selection_bound` at one-sided 1 % and 5 %.
A class whose rejection rate's 95 % Clopper-Pearson interval lies wholly above the nominal (the calibration's own
criterion) is recorded as **"`cons` lax on c in this class"** (the second read's m2-4: an interval wholly above shows
it lax). A10 reads the population's values under random selections, not any cell's selection.

**A10's consequence, declared now (m2-4).** If A10 records `cons` lax on c, at 1 % or 5 %, in a surviving cell's class,
**the deciding rule itself** -- each member at the larger of its t and B2's quantile (11) -- is run on the same A10
replications as a **pseudo-judged split**: B2 built from 2021-2022's values, the random selections and the statistic on
2023, at the same levels. **If the deciding rule is lax there too (its interval wholly above nominal), that cell is
closed, counted, before stage B reads any lift.** If the deciding rule holds there, the cell stays and the verdict says
"`cons` lax on c in this class; the larger-of rule held on the pseudo-judged split". A cell whose rule holds is closed
by this at most as often as A10's first check flags a holding `cons`, which the binomial bounds exactly at 2.5 % or
less per (class, level) (T-1 prints the exact probabilities at 1 % and 5 % over 2,000 selections). It is a check at 1 %
and 5 %, a proxy: the family's level cannot be checked by a choice-span control of this size, and the consequence can
only remove cells, so it cannot raise the family's size. Cost: the A10 replications times a B2 of 20,000 inner draws
on about 250 sessions, CPU hours, light in memory.

**A11. K0: the counts' persistence (a kill, outcome-free; E-052 (1)).** For each surviving cell and each of its two
count forms -- **C1's** (the in-state offers per session within the population's offers per session, on the choice
span) and **C2's** (the design's openings per session against its two twin designs' openings per session, uses counted
per start, on the choice-block replays) -- `cons`'s size at the family's level 0.05 / (k (k + 1)), the pinned k, on
**the sign null of Q-16's `cluster` form**: each offer or use 1/2 sign(a_s + e), the session effect a_s shared by every
offer of the session and by both samples (icc 0.35), so the null is exact; each replication takes the judged block's
length of sessions from the cell's choice-span count series at a seeded uniform circular offset
(`[20261989, cell, form, j]`, form 0 C1's, 1 C2's); 200,000 replications; C1's form by `placebo_selection_bound`'s
nested two-sample statistic, C2's by `two_sample_bound`'s. **A cell whose 95 % Clopper-Pearson interval lies wholly
above nominal in either form is killed**, counted, before stage B. It reads counts only -- no value of an offer -- so it
carries no direction (the pass-line review's M1 remedy, adopted as E-052 (1)). K0 changes no statistic: a cell it keeps
keeps `cons`'s level and power, and a cell it kills had a size above its level (18.3 shows it on toy count patterns of
this family's classes). Cost: about a minute and well under 200 MB a cell and form.

## 10. Stage B: choose on the choice block (2021-01-04 to 2023-12-29)

1. **The ranking statistic.** For each cell surviving stage A, L_c (7.2: `placebo_selection_bound`'s estimate on y) on
   the span, strata (mark, day kind, year) within it, u3 with its out-of-fold forecast.
   - Its bootstrap: a stationary bootstrap of sessions, **mean block 63**, 2,000 draws (`[20261980, 1]`), each draw
     recomputing L_c, the strata means included, on the resampled sessions; SE_c its standard deviation over draws.
   - q_B: the 95th percentile over the centred draws of max over cells of (L\*_c - L_c) / SE_c.
   - **Stage B's bootstrap and max-T are an uncalibrated selection device that decides no level** (as F-02's, E-039):
     the level is stage C's alone. Benjamini-Hochberg at 10 % beside, never selecting.
2. **Kill B:** no eligible cell with L_c / SE_c > q_B. The family **closes** and the judged block is not read.
3. **Eligible as the pick:**
   - K2's margin: at most 4 % unresolved at 3R among its in-state offers in its worst year;
   - **both halves positive on the span** (C3's choice-block form: L_c^long > 0 and L_c^short > 0);
   - **C1-close's form positive on the span** (L_c under the `close` convention above zero);
   - K1, K5 and K0 (A11) passed; A10's consequence passed; not dropped by 6.6.
4. **The pick:** among the eligible cells above q_B, the largest lower limit of **V_B**, the choice-block form of
   V_line (7.4) on the choice-block replays (the design's openings against its two twin designs'): V_B's per-opening
   difference D_B less q_B x SE(D_B), priced as V_line, its SE from the same bootstrap with the uses held fixed
   (`[20261980, 2]`). Ties go to the cell listed first (s1, s2, s3, u3).
5. **Reported for every cell before the pick:** L_c and its halves, by year; the kind shares of the in-state offers
   against their strata; L_c under the `close` flatten convention; V_B's in-state and fallback parts; V_B(P-16).
6. **What it spends:** nothing of the program's level. One cell reaches judgement.
7. **The record:** every cell's stage A and B readings are written to the result file's `choice` section before the
   judged block is read.

## 11. Stage B2: the critical values, conditional on the judged selection (family B's form, E-030, E-040)

**Why.** The states cluster: s3 is a daily state whose calm spells last weeks; s1 and s2 persist through a night; u3's
forecast moves slowly. So the in-state offers sit in runs of sessions. A slow component of the outcomes that the strata
do not remove (anything inside a calendar year) aligns with such runs by chance more often than with a selection that
does not cluster. Family B's third draft found that resampling one realisation cannot certify the family's level
against that and kept the failed check on record (E-030); so the critical values here are conditional on the actual
judged selection and widened by a declared slow component, as family B's are.

1. **The statistic for every line** (C1, C1-close, C2): **`cons`** -- the members `t21w`, `t42w` and `t63w`, each the
   two-sample difference with CR1 variance from the residual block sums on 21-, 42- and 63-session blocks and the
   treated df (`extended.lift_bound.diff_stats`, exactly as `placebo_selection_bound` and `two_sample_bound` compute
   them). **Each member's critical value is the larger of its t (at its treated df) and B2's simulated (1 - level)
   quantile of the same member's t statistic**, and each member's lower bound is its estimate less that critical value
   times its se. **`cons` passes only if all three members' lower bounds are above zero; its bound is their minimum.**
   Always the larger-of rule -- no tolerance, no pretest. The module's own nominal bound is reported beside.
2. **B2's null at stage C (E-051's ruling for family B, applied here by E-054 (2)).** **The deciding lines' null is the
   realised judged population**: the twin's exact expectation is the judged block's own stratum means, so under the
   null the in-state offers' centred values average zero against the block as it actually came out. B2 is conditional
   on the pick's real judged selection (read under `stage_C_states` and hashed before any outcome is read) and shapes
   the null's **dependence**, never its mean:
   - **The values:** each null replicate y\* is built from the choice span's own per-offer centred values y at 3R (every
     population offer, and every labelled P-16 mark for C2's fallbacks, 2021-2023), at the session level, **within day
     kind** (the second read's m2-11): two stationary bootstraps of mean block 63 sessions of their own kind, one over
     the choice span's normal days and one over its report days, each to the number of judged sessions of that kind;
     each judged session takes a drawn session **of its own kind**, its offers that session's values at the same marks
     (a missing mark dropped -- now only where the two sessions' admitted marks differ within a kind);
   - **plus a declared slow component** a\* x rho_t: rho_t a two-state Markov sign switching with probability 1/63 per
     judged session (a random start);
   - **then re-centred within the judged strata** -- so the twin's expectation is zero exactly in every replicate, and
     **the slow component is centred within the block**: it adds dependence, never a mean (E-051);
   - the line's member statistics recomputed with the real judged selection (for C2, with both designs' judged uses
     held fixed, read under `stage_C_campaign`);
   - **draws** `default_rng([20261985, line, j])`, line 0 for C1, 1 for C1-close and 2 for C2, **exactly 1,000,000
     replicates** per line (the replicate count fixed, as E-051's minors fix family B's; light in memory, CPU hours).
3. **a\*, the slow amplitude: the largest of (a), (b) and (d)** (the second read's m2-3; E-036's and E-051's precedents):
   - **(a)** the largest absolute mean, over the choice span's disjoint 63-session blocks in session order, of the
     per-session mean of y;
   - **(b)** the largest absolute per-offer follow lift at R = 3 that Stage 2 recorded for the rules its S1 and S3
     batches found surviving, followed -- `mom15` and `lbrk5` in `vendor/stage2/results/s1_sided_coin.csv`, `lnbar1x4`
     in `s3_event_kinds.csv` and, at latency 5, in `s3_latency.csv`, each file's section `lift`, `mean_lift` at R 3.0 --
     a disclosed pre-read (E-040; Q-61), read at run time, upward only. Those files hold the lifts over the whole
     development window only (their `lift` sections carry no span; the early/late split exists only for campaign growth,
     section `g3`), and a sided lift and a side-symmetric deviation are different quantities in the same unit (net R per
     offer at 3R): (b) is a sourced floor, not a model of c;
   - **(d)** the judged block's own: the largest absolute mean, over the judged block's disjoint 63-session blocks in
     session order, of the per-session mean of the **out-of-state** offers' values (for C2, the labelled marks with
     them), **each centred by its own stratum's out-of-state mean**. No in-state offer enters (d), and the out-of-state
     offers are not centred by the population's means (which hold the in-state offers), so **(d) takes no term from the
     design's own lift** (E-054 (2)). It is read after `stage_C_judgement`; B2 for C1 and C1-close is computed at the
     a\* it gives, and B2 for C2 at the a\* of C2's own (d); it can only raise a critical value;
   - **dropped:** the second version's "(c) three times (a)" -- an unsourced factor, which E-051 drops for family B
     ("the 3 dropped unless sourced"); (d) now covers the case it stood for (a judged slow component larger than the
     choice span's), from the judged block itself.
   - **Its level and power at the family's level, shown before the pin (E-051's rule):** `tests/test_family_o_toys.py`
     (18.3) runs the larger-of rule with (a) alone and with (a) and (d), against `cons` at its nominal values, on toys of
     the family's two selection kinds, with a judged slow component equal to and three times the choice span's.
4. **What it cannot see, named and left to the confirmation (E-051's "twin sat low" case, in this family's terms):** a
   state whose in-state sessions sat on one side of a slow regime **throughout** the judged block. The realised lift is
   then the regime's alignment, real on this block; no resampling within the block can tell it from a selection that
   generalises, and no amplitude rule can either without taking a term from the lift itself. Whether it generalises is a
   question for new data: the confirmation on unread data carries it. "A slow component larger than (a), (b) and (d)
   allow" is also beside the verdict, as an assumption that carries the level.
5. **What Q-16 calibrated, and what it means for the side-symmetric value (the review's F1).** Q-16's selection nulls
   used **the coin side's own outcome** -- the win at 1R and net R at 3R of P-16's judged offers (calibration note 2.4)
   -- under random selections in six persistence classes. This family's outcome is the side-symmetric c (and its centred
   y), which differs in two ways: the coin's direction noise is removed, so its per-offer dispersion is smaller; and its
   main slow part is the volatility-driven mix of exit kinds and any persistence regime, which the coin's noise no
   longer dilutes. So its dependence is **not in the class Q-16 calibrated** ("a level is only as good as the null
   class", calibration note 7.4 item 1). Nor do Q-16's nulls let the **counts** persist (E-052 (1)), and this family's
   counts move with its states. What follows: (i) `cons`'s level on c is not established by Q-16 and is checked on the
   choice span by A10, with a consequence (A10's, 9); (ii) the counts' effect is checked by K0 (A11) before stage B and
   on the judged counts before any outcome (12); (iii) the level each line is judged at rests on the per-member
   larger-of rule with B2's null built from c's own choice-span values, which is why the rule applies always; (iv) Table
   9's power is an upper guide for c, not its calibration (6.6). C2's two-sample form on routed openings, with offers
   reused across starts, is likewise outside Q-16's nulls and rests on B2 and K0 in the same way. *Reading (the second
   read's n2-1 (ii)):* the two pooled twin draws suffice for validity (inference is conditional on the draws, and a draw
   independent of y adds no bias), and the reuse of an offer across starts is carried by the session-block clustering
   (a reused offer's uses sit in one session, inside one block's residual sum; the two samples' covariance is inside the
   per-block difference of residuals).
6. Fixed now. T-10 checks B2's machinery at declared levels (18.2); **the family's level rests on the larger-of rule,
   not on T-10**. *Reading (n2-10):* on centred y the module's variance weights every offer of sample 2 by 1 / N, while
   L_c's exact linear form weights offer i by p_g(i) / N_F; the difference adds the between-strata spread of the firing
   share, conservative in expectation (the first read's check 1). No change.

## 12. Stage C: judge the pick once, on the judged block (2024-01-02 to 2026-07-16)

**The judge's inputs:** the pick and u3's frozen forecast by their pinned hashes (T-9); the strata within the judged
block. **In order:**
1. `stage_C_states` (bars: the selection, the strata counts and the run lengths, hashed);
2. **K0 on the pick's judged C1 counts** (A11's machinery on the judged in-state and population offers per session,
   `[20261989, cell, 2, j]`), before any outcome is read;
3. `stage_C_judgement` (the population's walks at 3R, both sides, under both flatten conventions, and the labels): L,
   the halves; then (d) (11 item 3) from the out-of-state offers; then B2 for C1 and C1-close at a\* = the largest of
   (a), (b) and (d); then C1 and C1-close;
4. `stage_C_campaign` (the paired U1 replays of the design, its two clustered twin designs and P-16 on the judged starts,
   the routing records); **K0 on the pick's judged C2 counts** (`[20261989, cell, 3, j]`), read from the routing records
   before any y is attached to them; B2 for C2; V_line; the design's gate campaign for floor (iii);
5. `stage_C_scorecard` (13).

**The design passes only if every line holds. A fail of any line closes the family**, its reason in a decision row.
Each line at the family's level 0.05 / (k (k + 1)), by `cons` with each member at the larger of its t and B2's critical
value (11):

- **K0 at stage C (E-052 (1)):** if either of the pick's judged count forms puts `cons`'s 95 % interval wholly above
  nominal, **a pass is not claimed** whatever the lines read: the verdict is "not claimed: the judged counts make `cons`
  lax", and the family closes. A check that can only remove passes cannot raise the size; it reads counts, which carry
  no direction under the null; and it is declared now, not after the read.
- **C1, the pass line (E-023 (2)):** `placebo_selection_bound(y, session, selected, ...)` on the judged block's
  population, y = c - mu_g (7.2); **its `cons` lower bound above zero.**
- **C1-close:** the same under the `close` flatten convention (the review's m3): a lift that is only Stage 2's
  conservative flatten price fails here. An intersection at the same level: no extra spend.
- **C2, worth something where it is used:** on the paired U1 replays of the judged block's starts (4 item 5),
  `two_sample_bound` on the design's openings against its two twin designs' openings (7.4); **V_line at D's `cons`
  lower bound at least $500 a year.** This is CHARTER section 3's "its value at that bound", priced on the openings the
  design takes against those a random waiting rule takes.
  - **The bound arm's shift is P-16's registered shift at each R**, for the design, its twin designs and P-16 alike:
    every trade is a P-16 coin trade walked the same way, so the replays differ only by the wait (family R's choice; the
    alternative, each design's own bounds by the era rule, would be re-estimated over both blocks and move with the
    selection).
  - **Not calibrated, said with the verdict:** the value-map price at the bound (calibration note 7.4 item 10); the
    two-sample form on reused routed openings (11 item 5); V is gross of the wait's cost (7.4).
  - **An assumption that carries the value, said with the verdict (the second read's m2-1):** the differencing removes
    the routing selection to first order, and the clustered twin matches the waits and routing positions; what remains
    -- the state's own alignment with the night's routing, which the shifted twin does not share -- is not in B2's null
    for C2 (its D\* is centred at zero by construction).
- **C3, both sides:** L^long > 0 and L^short > 0 on the judged block (point estimates). A persistence lift raises both; a
  lift carried by one side is drift (1 (v) (b)) and closes the family.
- **The floors (CHARTER section 3; E-022), all on the design's own judged-block run:**
  - (i) **resolution:** the pick's in-state offers unresolved at 3R at most 5 %, overall and in each of 2024, 2025 and
    2026 to 07-16 (a year with fewer than 63 sessions pooled with its neighbour, D-604); the share of the design's taken
    trades flattened at most 5 % overall and in each year (on the replay);
  - (ii) realised risk in P-14's registered allowance-capped form (E-022 (1), E-032);
  - (iii) **the long-run gate:** growth on the required bankroll at the bound above zero, on this design's own gate
    campaign (500 paths, seed 20261983, the gate's own day table as the gate is defined), never taken from P-16's
    registered pass (E-022 (2)); said beside it: on the gate's independent days the design waits less than it does
    traded in history's order (the second read's n2-8);
  - (iv) every firm rule verified (Stage 2's ledger);
  - (v) conduct tier 1 (section 3).
- **Beside, deciding nothing:**
  - L and its halves **by calendar year on each block** (the place the reverse walk-forward held, E-031 (2));
  - the kind shares of the in-state offers against their strata, and the **kind decomposition** of L: the part from the
    target share's change at fixed costs, and the part from the kinds' cost composition (1 (v) (c));
  - L under Q-20's corrected moves (`STAGE2_BE_BOTH`, merged b7232ba);
  - the seeded twin's draw (`[20261982, c, 0, 0]`), by `two_sample_bound`;
  - each member's nominal and B2 critical values, a\*'s three parts and which one set it; the A10 class verdict for
    the pick's class; K0's judged rates for both forms;
  - V(P-16), V(design) undifferenced, V(design) - V(twin design) in dollars, V's in-state and fallback parts,
    **V_other** (7.4), and the uniform-lift valuation beside V_line -- C1's bound x **the design's in-wait openings** a
    start-year x mean_dv(c) / 4 (the fallbacks carry no selection, so counting them would overstate it by up to
    1 / (1 - the fallback share); the second read's m2-5);
  - the share of the design's openings on report days, at the report-day 07:35:00 entry, and by hour; the in-state
    share of P-16's own judged openings; the judged run lengths and the class they imply (6.6);
  - u3's judged forecast skill, if u3 is the pick;
  - **beside floor (iii)'s campaign** (the design's own gate campaign, seed 20261983; E-073 item 6, the template's
    section 5), each reported and never a line:
    - **the break-even denial:** `propedge.campaign.portfolio.break_even_denial(fees, payouts)` on the design's campaign
      at the bound -- one minus fees over payouts, the share of payouts the firm could deny before the gain is gone;
    - **the placement on:** tier 2's patterns (section 3) modelled (D-289), with the share of the design's openings at
      full allowance and of days with several accounts at the MLL;
    - **the zero-edge twin:** the same gate call at the same seed with every R shifted to a zero mean, each R by its
      own e (Stage 2's `scripts/portfolio_stage.zero_edge_blocks`), its growth on the required bankroll and the design's
      point growth less the twin's (`signal_lift_over_zero_edge_twin`, the form of `propedge/reporting/scoreboard.py`);
    - **e and its bound for each R, and stage one's D-47 criterion** (propsim D-47: e at least 0.10 and its bound at
      least 0.05): **P-16's by construction, said so and not recomputed.** The design's gate blocks are P-16's trades --
      the same offers, walked the same way -- and its bound arm takes P-16's registered shift at each R (C2 above), so
      e, its one-sided bound and D-47 are P-16's registered values, cited from its registration; the wait changes which
      offer an opening takes, never the trades' outcomes or the shift;
  - Stage 2's S-program guard (the design's paired growth at the bound against P-16's, D-568 (2)), never a line.

**Dropped (E-031 (2)):** the reverse walk-forward.

## 13. The journey scorecard -- beside, never the pass line (CHARTER section 2; E-008, E-014, E-015, E-023)

**Which designs.** Read for the pick only, after stage C has read, whatever its verdict. A family closed at stage A or
at Kill B reads none.

- **The design** (P-16 with the waiting opening at the pick's state), **its twin design** (draw 0), and **P-16**,
  paired (the same starts and coin), with R\* = P-14 beside.
- **What each pair shows.** The design against its twin is the selection's journey effect: the clustered twin (7.1)
  waits and reaches offers as the design does, so the pair no longer mixes the selection with a difference in waits
  (the second read's m2-1); the waits of both are reported beside it. The twin design against P-16 is the wait's and
  the move's own effect (5.5 item 2).
- Journeys from the vendored U1 replay through Q-17's adapter (`extended/user_beside.py`), with the family's account
  class passed through Q-76's declared keyword, composed with `ForfeitFundedAccount` for the forfeiture responses (5.4;
  the second read's m2-10), so all-accounts forfeiture stays among the readings.

**On which starts.** The judged block's starts (`stage_C_scorecard`), labelled as such; beside, 2021-2023's starts (a
choice-block read, u3 out of fold), **purged by horizon per measure** so that no choice-block journey reads a
judged-block session (Stage 2's `u_select.block` purge, the F-P review's F6); 2020 is not read for it.

**What is read.**

- **P** and the guarded measures S1, S3a, S3b, S3c (with its components: a won funded opening, the five winning days
  after it), S4a, S4b, S5a, S5b, S5c; the reported-only S2, S3d, S6, Q (`vendor/stage2/docs/USER_MILESTONES.md`). S3c
  is compared within one trade stream (E-008): the three designs share P-16's offers.
- **The journey variables (E-014):** sessions and cash to the first pass; sessions and cash to the first payout;
  **sessions to break-even** (the first session whose cumulative net cash is at or above zero, daily), the share of
  starts reaching it by months 1, 2, 3, 6 and 12, and the share that later fall back below zero; **the path's
  evenness** -- the share of months with a positive net change, the longest run of months without a payout, the spread
  of monthly net, the deepest fall of cumulative net from its running high after break-even, payouts per month, the
  largest single month's share of the year's payouts.
- **The wait, as a user feels it:** the sessions from activation to the opening; the openings' hours; the minutes the
  firm's slot is held by openings; funded trades per live account-day and the share of account-sessions without a
  trade, against P-16's.
- **Every measure as a distribution over start days** (median, p10, p90), with its uncertainty from the effective number
  of independent starts and the start day's share of the variance (`user_drivers.csv` section `design_vs_luck`).
- **The paired readings:** the per-start difference against P-16 and against the twin design as distributions, and the
  shares of starts better, equal and worse at months 1, 2, 3, 6 and 12.
- **The P comparison's statistic (the second read's m2-6; E-035 (3)):** **`pcons`** (`extended/p_bound.SHIPPED`, blob
  `f5b29710e243f97a2795e57f6458512fea99199b`) for the paired P differences against P-14, P-16 and the twin design,
  one-sided at 0.05, beside, never a line; `bm63c` (`p_bound.RECOMMENDED`) beside once its critical-value table is
  pinned. `pcons` simulates with `p_bound`'s own seed; `[20261987, 0]` draws only the block-bootstrap intervals of the
  paired distributions above (their median, p10 and p90), nothing `pcons` draws.
- **The frontier** on P, S1, S3a and S5a; **the menu** under E-015's limits once the operator approves them, as **flags
  only** (a limit never fails a design, E-015 (3)); **the evenness trade-off curve** (E-015 (4)).
- **E-007 (e)'s readings** (Q-17's adapter): the denial ladder at 10, 25 and 50 % (draws `[20261987, 1]`); the placement
  on; all-accounts forfeiture (composed over the family's class, 5.4); P by month, mean net, CVaR10, P under a bankroll
  limit, the effective sample size and the minimum detectable difference -- **without the ten binding Focused Trader
  models, labelled so wherever these readings appear**: the engine refuses them for any funded class but the vendored
  `FundedAccount` (`lockstep.py` 1403-1408), and the lead's ruling (E-059) is that a family running its own class
  reports E-007 (e)'s readings without them; a re-composed path that admitted them would be a separate build under its
  own row, not this family's. The paired readings leave them out for all three designs (the design, its twin and P-16),
  so each pair compares like with like; P-16's own Focused Trader readings are its registered design's (Q-44's file).
- Stage 2 D-621 (3)'s rule against P-14, beside as E-008 keeps it, deciding nothing -- **its line (i) labelled as not
  holding its level** (E-007 (1); E-035 (3)).
- **Not modelled, said wherever the scorecard appears:** a user who stops when their own money runs out, the user's
  time, taxes; **and the unstated news rules (E-034):** which events count as "major news" under 10305426 and whether
  holding an open position through one counts -- unstated; the GDP release minute -- unstated; the share of openings
  held through ISM or GDP -- unknown (no calendar on disk); **and E-039 (1)'s inheritance:** the fallback and
  non-opening trades keep P-16's report-day 07:35:00 entry, on the stated end of Topstep's Tier 1 window (U7 (a)), with
  their count (A2).

## 14. What a pass and a fail mean

**CARRIED** (every line of stage C and every floor holds):

- a development finding on a late-development block;
- the design -- P-16 with the opening waiting at most five sessions for the pick's state -- takes a registration id
  (Stage 2 D-621 (9)'s house form), a model card if the pick is u3 (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`: the
  forecast's coefficients), its registered development test, the auditor and **one confirmation** (section 15), which
  carries the decision (D-189);
- if stage A declared the family a screen, a pass is still CARRIED, and the carrying row says the development read was a
  screen at its MDL ratio;
- **a u3 pass contradicts its stated sign.** It carries like any pass only if every line holds -- C1-close among them,
  so a lift that is only the flatten convention's price cannot carry it; the carrying row says it runs against the
  LeBaron prior, and the beside readings (the kind decomposition) say whether its lift is a cost avoided at a real close
  or the surprise term's persistence;
- what a user is told is the scorecard as a distribution (13), never one number.

**CLOSED** at stage A (an identity fails, or every cell is killed or dropped), at B (Kill B), or at C (a line or a
floor):

- the reason goes in a decision row;
- a close at B or C reads **"no selection lift above the MDL at this family's level"**, never "timing does not help";
- a cell dropped at the pin by 6.6 reads **"not judgeable on this block at its persistence"**;
- **the closure binds** (D-277's boundary): a later family on these states or this population names this closure, says
  what changed and why it is a different hypothesis, and is not judged on this family's judged block.

## 15. The confirmation, declared before any development read

- **The window:** NQ from **2026-07-17** (`config/windows.yaml`, `reserve`). Not on disk, never read until a carried
  design is registered. **A purchase, the operator's**, stated in `docs/OPERATOR_SETUP.md` and waited for; it would be
  NQ's fourth confirmation window, **the operator's decision** (D-107, D-461).
- Stage 2's draft P-16 confirmation (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`) and F-02's, family B's and family
  R's drafts target the same window. If any test reads it first, the lead records that before registration, and the
  operator decides whether it can still confirm this pick.
- **What it tests -- the pick's trades, not P.** With the state (and u3's pinned forecast) fixed:
  - C1 and C1-close on the window's population, one-sided at the registered 0.05, by `cons` with B2 re-simulated at the
    window's length (`[20261985, 10 + line, j]`) -- **B2's values from the development window, both blocks** (by then
    read), within day kind, a\* by 11 item 3 with (d) from the window's own out-of-state offers -- the bound at 0.05 / N
    beside (D-189's form);
  - K0 on the window's counts (`[20261989, cell, 4, j]`), a pass not claimed above nominal;
  - **the value line, always (the second read's m2-5):** C1's bound on the window x **the design's in-wait openings** a
    start-year (stage C's, from the judged replays) x mean_dv(c) / 4, **at least $500 a year**; C2 on the window's U1
    replays is read beside, never a line -- on six months `cons`'s 63-session member has two blocks and one degree of
    freedom, so C2 there could pass only by luck;
  - C3 and floor (i) on the window, overall and in every calendar year with at least 63 sessions (a stub year pooled,
    D-604);
  - Q-16's draws, if any, from `[20261986, 1]`; the twins' from `[20261982, c, 2, d]`.
- **What it cannot test: P.** Six months is about 126 sessions, about 63 starts with a month-3 horizon; no interval on P
  exists there (the phase-0 red team's M1). The scorecard on the window is descriptive.
- **How much data:** at least six months (D-604), and at least the months at which the pick's expected in-state
  sessions (the lower of its two blocks' rates) reach the count at which `cons`, one-sided at 0.05, has 80 % power for a
  lift equal to **the pick's judged lower bound at the family's level**, at the pick's persistence class -- the same
  count serving C1 and the value line, which both rest on C1's bound. That count is
  computed when the pick is carried and written in the carrying row, before any confirmation data exist. If it is more
  than the operator will buy, no confirmation is registered, and the pick stays a development finding.

## 16. Seeds -- proposed 20261980-20261989, checked unique, for the lead to confirm at pinning

| seed | what it draws |
|---|---|
| 20261980 | stage A and B's bootstraps: `[20261980, 0]` A4's skill, `[20261980, 1]` stage B's max-statistic, `[20261980, 2]` V_B's standard error |
| 20261981 | the build's shift-invariance test's replacement walks (A3, T-2): `[20261981, j]` |
| 20261982 | the placebo-selection twins: `[20261982, c, b, d]`, c the cell (0 s1, 1 s2, 2 s3, 3 u3), b the block (0 judged, 1 choice, 2 the confirmation), d the draw (0, 1) |
| 20261983 | the design's own gate campaign on the judged block for floor (iii): 500 paths |
| 20261984 | A10's random selections on the choice span: `[20261984, class, share, j]` |
| 20261985 | stage B2's replicates `[20261985, line, j]` (line 0 C1, 1 C1-close, 2 C2); the confirmation's re-simulation `[20261985, 10 + line, j]` |
| 20261986 | Q-16's statistic's draws, if any: `[20261986, 0]` stage C, `[20261986, 1]` the confirmation |
| 20261987 | the scorecard's paired draws `[20261987, 0]`; the denial ladder for this file's designs `[20261987, 1]` |
| 20261988 | the synthetic tests: `tests/test_family_o_persistence.py` (`[20261988, j, ...]`, j = 0..9); `tests/test_family_o_toys.py` (K0's toys `[20261988, 300, ...]`, B2's toys `[20261988, 400, ...]`); T-3's synthetic judged block `[20261988, 100]`; T-10's synthetic selections `[20261988, 200, j]` |
| 20261989 | **K0 (A11; E-052 (1))**: `[20261989, cell, form, j]` -- form 0 C1's choice-span counts, 1 C2's choice-block counts, 2 the pick's judged C1 counts, 3 its judged C2 counts, 4 the confirmation's counts; the random circular offset and the sign null's draws (formerly reserved, unused) |

The U1 replays draw nothing at 0 % denial with the placement off; where Q-17's adapter draws (the denial ladder
beside), its per-start seeds are its own rule over 20261987's.

**The check.**

- At the first version (2026-11-16): `grep -rIowh --exclude-dir=.git -E "2026198[0-9]" .` over the whole working tree,
  the vendored snapshot and its results included, and `git grep -I -E "2026198[0-9]"` over every commit of every local
  and remote branch (`git rev-list --all`, after a fetch): no hit before that item.
- At the second version, on master 905eb19 (the vendored snapshot extended to 710 files, Q-61), the same two
  searches: hits in this file, its test and the first review, which quotes them, and nowhere else.
- **At this version, on master 8d80481, with the licensed data excluded** (the second read's n2-5: a plain `grep -r`
  in a worktree follows the junctions into `vendor/stage2/data/bars` and `atlas` and opens the licensed files, judged
  block included, before skipping them as binary -- an open outside the one door, harmless in content but avoided):
  `grep -rIlw --exclude-dir=.git --exclude-dir=data -E "2026198[0-9]" .` and `git grep -I -l -E "2026198[0-9]"` over
  every commit of every branch: hits in this file, its two test files, the toys' printed output
  (`docs/reviews/scripts/family_o_drafter/q87_toys_output.txt`) and the two reviews of this family, which quote them;
  and in family R's test, where 20261980 appears only as the exclusive upper end of family R's own seed range, not as a
  seed. Nowhere else.
- T-1 asserts that no other file under `prereg/` names any of them.
- **Not searched:** Stage 2's working tree beyond its vendored snapshot (its decision log and scripts are vendored and
  were searched).

**Neighbouring blocks, taken:** 20261910-19 (Q-16), 20261920-29 (Q-17, Q-20), 20261930-39 (F-02), 20261940-49 (F-P),
20261950-59 (Q-18), 20261960-69 (family B), 20261970-79 (family R), and the firms reading's block above this one
(E-038; not written out here, because that reading's own test refuses its seeds in any other declaration).

**Inherited, used only as their owners registered them:** 20261102 (P-16's coin); 20261206 (P-16's gate, the
identity); 20261131 (P-14's, beside); 20261600 + i and 20261700 (Stage 2's coin sequences and D-621 (3), beside only);
20261913 and 20261914 (Q-16's module seeds, inside `extended.lift_bound`).

## 17. Multiplicity and the budget

1. **k.** The next free program family number at the pin, with level 0.05 / (k (k + 1)), written by the gatekeeper in
   the pinning row.
2. **Counted:**
   - **4 cells** (s1, s2, s3, u3), each counted whether dropped at the pin (6.6), killed at A, closed at B or read
     at C; u3 is counted although its stated sign is negative;
   - **0 searched configurations**;
   - **11 fitted values** (u3's coefficients) inside the walk-forward, fitted in each of its three folds and the final
     fit, none searched.

   The identities, the controls (A4, A10), the counts of stage A, K0's and B2's replications, the seeded twins and the
   readings beside are not trials: nothing is chosen from them. A cell killed by K0 or closed by A10's consequence is
   counted like any killed cell.
3. **One cell reaches judgement.** C1, C1-close, C2, C3 and the floors are an intersection at one level. Stage B spends
   nothing of the program's budget.
4. **The program's honesty sentence:** Stage 2 ran programs S and U on this window, each with its own 5 %; the sided
   follow effect (S1, S3), the state gates (S2), the base opening's won share and the coin-side outcomes' dispersion
   under random selections (Q-16) have been read on both blocks (section 2); the development level is a screening
   threshold, and the decision is carried by one confirmation on unread data (D-189), if the operator buys one.

## 18. The build: adapters, identities and tests (after the pin, before any reading)

### 18.1 The code (in `extended/`, never in `vendor/`)

1. **`extended/opening_states.py`.** LR, LRS, DIS, har, H, HS, the four states, the rolling third, and u3's IV, M,
   x1-x3, bands, fit and y_hat. Bars come only through `extended/reader.py`, the frame P-16's walked sessions. The
   library's `grid`, `slot` and trailing median are imported, not copied; every window over a day's bars is bounded at
   its first bar. The states of every population offer are written as boolean columns of the population frame and
   hashed before any replay reads them.
2. **The population builder.** P-16's cell as `rc_width_screen.build` builds it with this repository's walker; both
   sides of every P-16 offer at every table R under `STAGE2` and at 3R under `close` -- the population's, and every
   other P-16 mark's as labels (5.2); the strata. No vendored attribute is substituted (the lesson of E-011's first
   run).
3. **The waiting account.** A subclass of the vendored `FundedAccount` that registers, under its draw's key, a gating
   wrapper of the vendored draw with the router and holds it strongly; the wrapper answers `can_take` with the vendored
   draw's answer **and** "the offer is in state, or the account has traded, or its wait is over" (5.4), carrying its
   wait counter, the (historical day, trade index) to (date, mark) lookup, and **its own count of every offer it
   declines** (a declined offer is not a trade, so no recorder sees it; E-055 (4)). Passed as `funded_account_cls` to
   `extended.gate.run_gate` (Q-47) and, through **Q-76's declared keyword** (merged, E-059: wt/wt-user f92ac5e,
   `extended.user_beside.run_starts(..., funded_account_cls=C)` and `response_args(..., funded_account_cls=C)`), to the
   U1 replay. **What this family uses of it (the second read's m2-10):** (i) the class checked as the gate checks it (a
   subclass of the vendored `FundedAccount`, able to reach a path worker); (ii) for every `forfeit_*` response,
   forfeiture composed over the class (`forfeit_class(C)`; a class with its own household rule refused -- the waiting
   class carries none); (iii) every start's output naming the class; (iv) with the keyword given and the class's wait
   switched off, every response's rows Q-17's, the forfeiture rows among them (A0 item 4). **What it does not give:**
   the ten Focused Trader models, which the engine refuses for any class but the vendored one (E-059; the readings are
   reported without them, 13). Recording on the replay is Q-94's `recorder=` keyword, beside it (item 4). If the build
   finds the class
   cannot reach the draw the router registered (`TierSizedDraw` registers itself, sizing.py), the seam is composed
   instead at the funded draw factory in Q-47's form (the vendored body, one keyword, a source-hash guard), under a row.
   Either way A0's and A1's identities refuse.
4. **The place records.** On the gate: Q-70 (merged, E-055: `extended/place_records.py`, `extended/place_fields.py`;
   family B's draft section 20 item 10) records every simulated trade's offer, R and place, and every funded account's
   opening, held to its built identities -- **P-16 at 4 paths** (every `PATH_COLS` column and row with recording on
   equal to the call with it off) and **P-16 and P-14 at 100 paths, the bound arm, U2's seed, against
   `u_value_map.csv`'s `trades_per_year_records`** (`identity/place_records_identity.py`, its heavy run Q-89; at 4 paths
   only `PATH_COLS` can be compared). **On the U1 replay: Q-94 (merged, E-068)** -- `extended/replay_records.py`'s
   `ReplayRecorder`, passed as **`user_beside.run_starts(..., recorder=)`**, a declared keyword off by default: each
   start's long replay runs with the engine's ledger and day recorder on and is reduced by Q-70's `record_path` to the
   same compact records (`place_fields`' replay schemas), handed on as the unrecorded path; its synthetic identity holds
   (19 fast tests: recording on equals off bit for bit on every response, with the pass-through class; the records are
   the replay ledger's rows, Q-35's openings and `FundedAccount.days`); **its heavy identity is Q-101**
   (`identity/replay_records_identity.py --u1-starts all --row E-068`: U1's start rows for P-16 and P-14 with recording
   on, every start), a pre-run condition. **What Q-94 leaves to this family's build (E-068):** the fallback flag
   (`opened & opening_session >= W`), the mark, hour and day-kind joins by the offer id (as Q-35 does), the declined
   offers (the wrapper's own count, item 3) and the restricted replay job (each choice-block start's history ending at
   2023-12-29); their identity is A1 item 7's.
5. **The estimand.** c_i, the strata means, y, the calls of 7.2 and 7.4, each member's statistic, B2 (within day kind,
   a\* by 11 item 3), the halves, V_line, V(P-16), V(design) and V_other, from the population frame and the routing
   records; **K0** (A11) on counts; the clustered twin (7.1).
6. **`identity/family_o_identity.py`** (A0; the second read's m2-2): the whole-window identities, reading through the
   reader as `identity` under its own row, from a clean run under the lock, before run 1.

### 18.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-1 | **written now:** `tests/test_family_o_persistence.py` (18 tests). The driftless walk's long and short target-first shares are 1/(1+R) exactly; on the persistent random walk the side-symmetric 3R win rate rises with persistence and the long equals the short; at R = 1 the two sides' gross outcomes cancel on every resolved path; a fixed drift splits the halves at first order and moves their mean by less than a tenth of the split; the twin's exact form equals the mean of 2,000 seeded placebo draws, its noise-free part is exactly the in-state excess share of persistent sessions times the regimes' gap, and over fresh noise the lift averages it; an uninformative state's lift averages zero; **`extended.lift_bound.placebo_selection_bound` on the centred values estimates exactly the exact-form lift, and on the raw values adds the strata-composition term (F1)**; **on a persistent daily state the fallback share at W = 5 in history's order is more than twice that on independently drawn days (F2)**; the rolling third fires on about a third of an iid series and reads only the past; the population's latest alert reads no 08:30-08:59 bar; this file's `Judged-block reads:` line gives exactly section 19.1's purposes by `extended.reader.declared_purposes`, none a choice or fitting purpose; this file's seed table is 20261980-20261989 once each, and no other `prereg/` file names them; **(third version) the named `close` instance differs from STAGE2 only at a flattened trade's price, by at least the two slipped ticks, on synthetic days (m2-7)**; **A10's consequence closes a holding cell at most 2.5 % of the time per check, exactly by the binomial, printed at 1 % and 5 % (m2-4)** (seeds `[20261988, ...]`) |
| T-2 | the states' and y_hat's shift invariance (A3): replacing, and deleting, every bar stamped at or after m - 5 changes no state, at cuts including 17:30, 18:00 and 18:05; replacing the alert day's 08:30-08:59 bars changes none; x3 equals 2 x `rv_tod` at every RTH alert where the library computes it; no window wraps at an overnight slot; no state all-undefined or constant |
| T-3 (heavy, under the run lock) | run 1's result sections **other than `identity`**, and u3's final forecast hash, are byte-identical when every judged-block bar is replaced by a seeded synthetic walk (`[20261988, 100]`); the whole-window identities are A0's, apart (m2-2) |
| T-4 | the population: only P-16's marks 17:00-08:25 on its day kinds; on report days from 07:40 only; never an FOMC day, an early close or a mark in 08:30-09:00; the labels cover every other P-16 mark; the strata as declared |
| T-5 | **through the vendored router and lockstep loop on a synthetic campaign**: within W a waiting account takes only in-state offers; after W it takes the next routed offer; after its opening it is P-16's; "its first W live sessions" are those with `FundedAccount.days` 0 to W - 1 at routing; with the state always on, or W = 0, every path equals the vendored one; with the state never on, every opening is on the sixth live session; with the state the placebo set, every in-wait opening is in the set; a collected wrapper is impossible (the account holds it) |
| T-6 | the estimand on the family's own code: L equals the drawn twins' mean (T-1's identity) and `placebo_selection_bound`'s estimate on y; an uninformative state's lift averages zero; the halves average to L; on a synthetic routing record, D and V_line equal their hand sums, and a fallback at a labelled mark takes its label's value |
| T-7 | u3's least-squares fit equals a direct normal-equations solve on synthetic data to 1e-8; a planted HAR process is recovered with the right signs; if family R is pinned first, its fit and this one give the same coefficients on a shared synthetic set |
| T-8 | the reader: every bar and walk read goes through `extended/reader.py` with its purpose; an untagged judged read raises (Q-32's own tests, re-run at the build's commit) |
| T-9 | the judge's entry point reads u3's frozen forecast by its hash and cannot fit; stage C reads the pick from stage B's result file by its sha256 |
| T-10 (slow tier: an hour or more per setting, the second read's n2-6) | **B2's machinery on synthetic data at declared levels (the first read's m7):** a synthetic population with a planted slow component and a clustered daily selection independent of it; the per-member larger-of rule under `cons` at one-sided **1 % and 5 %**; **2,000 outer replications**, each B2 quantile from **20,000 inner replicates** (`[20261988, 200, j]`). **Failure rule:** the test fails if a level's rejection rate has its 95 % Clopper-Pearson interval wholly above the nominal; a failure is kept on record and runs the failure protocol, never a rerun to pass. The family's level rests on the larger-of rule at the family's level, not on T-10 |
| T-11 | this file's seeds appear nowhere else in the build's commit except the family's own modules and tests |
| T-12 (slow) | A0 items 2 and 3 and A1 items 4 to 6 at 4 paths and 4 starts; the full 500 paths and every start are A0's identity run and run 1's first stage (heavy) |
| T-13 | the place records (18.1 item 4): **the identities this family relies on, built by Q-70 and Q-94** -- Q-70's P-16 at 4 paths (`PATH_COLS` with recording on equal to off) and, heavy, P-16 and P-14 at 100 paths against `trades_per_year_records` (Q-89); Q-94's `ReplayRecorder` through `run_starts(..., recorder=)`, its 19 synthetic tests and, heavy, U1's start rows with recording on, every start (`identity/replay_records_identity.py`, Q-101) -- re-run at the build's commit; and this family's own on top: at 4 choice-block starts, with the recorder and the family's class (wait off) every row equals the unrecorded vendored replay's, and the fallback flags, offer-id joins and declined-offer counts reproduce a hand-checked start |
| T-14 | the stage-B pick is a function of the choice section alone: re-running stage B on the written section gives the same pick |
| T-15 (slow tier, **written now**) | `tests/test_family_o_toys.py`: K0 and B2's (d) floor at the family's level on toys, their level and power printed (18.3; E-051's rule) |
| T-16 | K0 on the family's own code: on counts drawn iid it equals the toy's machinery; its verdict is the Clopper-Pearson interval's and nothing else; it reads no value column (a planted value column changes nothing) |
| T-17 | the clustered twin: every stratum's count equals the state's; the state's runs survive except at the wrap; over many offsets each offer's selection frequency is its stratum's share |

### 18.3 The level and power, at the family's level, of the rules this version adds (E-051's program rule)

E-051: "a tightening is accepted only with its level and power at the family's level shown before the pin". The new
rules are K0 (A11), B2's judged-block floor (d) (11 item 3) and A10's consequence (9). They are shown on synthetic toys
only -- no bar, walk or result file is read -- by `tests/test_family_o_toys.py` (slow tier, T-15) and, for A10's
consequence, by T-1's exact binomial test. **The figures are synthetic, select nothing and are not results of this
family**; their printed output, with the command and commit, is kept in
`docs/reviews/scripts/family_o_drafter/q87_toys_output.txt`, and the hand-back of Q-87 quotes them. What they show:

- **K0 (A11).** On toy count series of this family's classes -- offers (Q-16's iid reference), a window clustered across
  nights (s1, s2), whole sessions in runs of 5 (u3), 21 and 63 (s3), and C2's openings (the design's uses bunched on
  in-state sessions against two clustered twin draws) -- `cons`'s size at the family's level (k = 12 and 15, 200,000
  replications each) lies well below nominal in every pattern, and K0 keeps every one. K0 changes no statistic, so a
  cell it keeps keeps `cons`'s level and power; its only cost is a cell whose real counts are lax, which then has no
  valid level to lose. Real counts can be more bunched than these toys (the pass-line review's M1 found `cons` lax when
  the log count intensity has sd 1.5); that is what K0 reads on each cell's own counts.
- **A10's consequence.** A cell whose rule holds is closed by it at most as often as A10's first check flags a holding
  `cons` -- exactly at most 2.5 % per (class, level) by the Clopper-Pearson construction over 2,000 selections (T-1
  prints the exact figures at 1 % and 5 %); it can only remove cells, so it cannot raise the family's size.
- **B2 with (d) (11 item 3).** On toys of this family's two selection kinds -- whole sessions in runs of about a month
  (s3, u3) and a window clustered across nights (s1, s2) -- with a judged slow component equal to the choice span's and
  three times it, B2 as declared (within the block, the quantile non-decreasing in a\*), at k = 12 and 15:
  - **level:** over 200,000 null judged blocks per setting and k, the larger-of rule with (a) and (d) rejects no more
    often than with (a) alone, which rejects no more often than `cons` at its nominal values (asserted), and all three
    stay a small fraction of nominal in every setting, including the one where the judged slow component is three
    times the choice span's;
  - **power:** for whole sessions, (d) costs nothing -- B2's quantiles stay below the members' t critical values and the
    three rules have the same power; for the window, (d) costs a few points of power at middle lifts against (a) alone,
    and none at large lifts;
  - **the ceiling (6.6):** for whole sessions at k = 15 with equal slow components, power at the largest toy lift stays
    well short of one under all three rules -- the nested form's ceiling, which no rule here causes and none removes.

  So (d) is accepted on E-051's terms: it does not raise the level, and its power cost is small where power exists.

## 19. Outputs, the reads and the run

### 19.1 The judged block's reads (E-026)

The reader (`extended/reader.py`) authorises a judged-block read only for a purpose named on this line of the pinned
file:

- **Judged-block reads:** `stage_C_states`, `stage_C_judgement`, `stage_C_campaign`, `stage_C_scorecard`

What each is for, in stage C's order (12): `stage_C_states` -- the judged bars, to compute the pick's states, the
strata counts and the run lengths (no walk is read under it); `stage_C_judgement` -- the population's walks at 3R, both
sides, under both flatten conventions, and the labels at every P-16 mark (C1, C1-close, C3, the beside readings of L);
`stage_C_campaign` -- the paired U1 replays of the design, its two twin designs and P-16 on the judged block's starts
(C2, floor (i)'s taken trades, B2's uses) and the design's gate campaign (floor (iii)); `stage_C_scorecard` -- the
scorecard's readings on the same replays and Q-17's responses (13). Each is read once, from a clean run of a committed
tree, ledgered before it reads. No choosing or fitting purpose is named, and the reader would refuse one.

### 19.2 Files and the runs

- **Files**, each with its sidecar manifest through `extended.results.write_result`:
  - `results/fo_opening.csv`, sections `identity`, `states`, `persistence`, `supply`, `openings`, `resolution`, `wait`,
    `power`, `level_control`, `choice`, `level`, `judged`, `campaign`, `floor`, `beside`;
  - `results/fo_journey.csv`, the scorecard of section 13.

  Each manifest carries: `prereg_id` this file's F-id; the cell counts (4 cells, the dropped ones named, 0 searched, 11
  fitted values); every seed and parameter; u3's frozen forecast hash; the population frame's and the states' hashes;
  the calendar of each section (4 item 5); the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`. Every file is
  EXPLORATORY until a carried design is registered.
- **The order, after the pin:** the infrastructure identities on record (Q-89, Q-93, Q-101, Q-80; header); the family's
  build (18) and its tests; **the identity run (A0)**; run 1; the lead's row; run 2. Nothing runs before the pin.
- **The runs: an identity run and two family runs, each once**, from a clean checkout of a named commit
  (`scripts/run_clean.py`), under the run lock, watched to its end.
  - **The identity run (A0):** `identity/family_o_identity.py` under its own identity row, the whole window read as
    `identity`; its record goes in that row before run 1.
  - **Run 1 (the choice block only):** stage A (A1 first; A10 and its consequence; K0), u3's walk-forward and final
    fit, stage B. It writes the `identity` to `choice` sections, u3's frozen forecast and its hash, and the pick. It
    builds the population, the states and every replay on the choice block only, and reads no judged-block bar or walk.
  - **Between them, the lead's row:** u3's final fit's hash and the pick, by the sha256 of run 1's result file, pinned in
    a decision row and committed.
  - **Run 2 (from a clean checkout of that commit):** `stage_C_states`, B2, `stage_C_judgement`, `stage_C_campaign`, the
    floors, `stage_C_scorecard`. The judge's entry point reads the pick and the forecast by their pinned hashes and
    cannot fit (T-9).
  - **Weight: heavy.** Run 1 walks every P-16 mark of every session at 150 ticks on both sides (E-011's P-16 run is the
    nearest measure of memory) and replays every choice-block start from 2021 for P-16 and up to four designs and eight
    twin designs; run 2 replays every judged-block start for the pick's design, its two twin designs and P-16 (both arms
    for the scorecard) and runs one gate campaign at 500 paths: many hours each, at two workers. The lead may run run 1's
    replays as a chain, stopping at the first failure.
  - Within a run, each stage's file is written before the next reads anything. A kill stops the sequence (a family
    killed or closed in run 1 has no run 2).
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run of each is read.

## 20. The pin's conditions, the pre-run conditions, and what this file fixes

**At the pin -- the only conditions (header; E-073 item 1):**

1. **Q-55's clean rerun** reproducing `cons` and the treated two-sample `cons` holding (E-035 (4); E-052), and **6.6's
   drop rule applied to its `calibration_power.csv` by the lead**, the dropped cells recorded in the pinning row.
2. **Q-83 HOLDS** on E-052 (2)'s criterion. If it or Q-55 does not hold, this text is withdrawn before any read (the
   withdrawal clause, header).
3. **The family number** (k >= 12), written in the pinning row; family B may be pinned first.

**After the pin, before run 1 -- the pre-run conditions, in order, each refusing (header; 19.2):**

4. **The infrastructure identities on record as holding:** Q-89 (Q-70's place records, P-16 and P-14 at 100 paths), Q-93
   (Q-76's declared class on the U1 replay), **Q-101 (Q-94's replay recorder, `identity/replay_records_identity.py
   --u1-starts all --row E-068`)** and Q-80 (the gate's 500-path identities, E-049).
5. **The family's build** (18.1): the seam -- the waiting class through Q-76's keyword (18.1 item 3) and through
   `extended.gate.run_gate(funded_account_cls=...)`, or the draw-factory composition in Q-47's form if the class cannot
   reach the router's draw, under a row -- and **what Q-94 leaves to it** (18.1 item 4: the fallback flag, the joins by
   offer id, the declined-offer counts, the restricted replay job), with their tests (18.2).
6. **A0**, `identity/family_o_identity.py` under its own identity row (9).
7. Then run 1, opening with A1 (9); between the two family runs, **the lead's row** pinning run 1's result file, the
   pick and u3's forecast hash (19.2).

**Fixed by this file, not open (E-073 item 3):** W = 5 sessions; K5 at one half; the 250-session third; the 17:30 start
of s1 and s2; two twin draws; K0's 200,000 replications; the drop rule's file, rows, classes and share (6.6); u3's 11
coefficients fitted inside the choice-block walk-forward as E-031 (1) admits them, hashed and pinned before the judged
read; the bound arm's shift (P-16's registered shift at each R, 12, C2); the value bar of $500 a year at place (c), with
V_other beside rather than inside C2 (7.4); the seeds (section 16), checked unique again at the pin by the
data-excluding search; stage A's choice-block count of the openings as the substitute E-021 (2)'s ordering of Q-35 asked
for (if Q-35 runs first, its both-block counts recorded as a pre-read, 4 item 4). Each is the file's value; none is
changed before the pin.

*Answered since the first version, no longer open:* the twin's form (E-035; the first read's n2); whether earlier
sessions' 08:30-08:59 bars inside H and IV are in the closed branch (E-036 M3-2; n1); the report-day entry of the
base's trades (E-039 (1)); the news hold (E-034); the drafter's four questions to the red team (the second read's
n2-1: B2 and A10 held at 5 % and 1 % in its checks B and C, the margins being m2-3 and m2-4, now ruled; two twin draws
suffice and reuse is carried by the clustering; the classes plausible as argued; a\* by m2-3).

**What the gatekeeper may check on the diff:** that every item of 0.3 is where it says; that no cell, the twin's
estimand in C1, the level, the reads line or a seed's meaning moved, beyond 20261989 put to K0's use; and that each new
rule's level and power at the family's level are shown (18.3) before the pin (E-051).

**The operator's (only when they arise):**

- NQ from 2026-07-17 as a fourth confirmation window (D-107, D-461) and its purchase, only once a pick is carried;
- the levels of E-015's limits (flags only);
- D-281 (3), only if stage A's count shows most openings at 08:30-09:00 and the lead proposes a family that times them
  there (5.5 item 6).

## 21. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and recorded
in its own decision row -- never added to this file once pinned.)*
