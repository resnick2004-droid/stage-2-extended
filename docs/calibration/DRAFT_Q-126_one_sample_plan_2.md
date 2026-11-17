# Q-126: the one-sample pass line's second calibration -- the plan, declared before anything is built or run

**Status: a draft, sixth text (Q-126f).** It answers the red team's read of the first text (ec6905a;
`docs/reviews/DRAFT_Q-126_2026-11-17.md`) and the lead's rulings on it (E-173, as corrected by E-176); the re-read of
the diff to the third text (4b31805; `docs/reviews/DRAFT_Q-126_v3_2026-11-17.md`) and the rulings on it (E-182, which
keeps zero tolerance on a corrected basis); and the last read, of the fourth text (0772de0;
`docs/reviews/DRAFT_Q-126_v4_2026-11-17.md`), and the rulings on it (E-184: the band check rebuilt, a balance limit
added to it and to 4.4's admission); and the light read of the fifth text (20e03c4;
`docs/reviews/DRAFT_Q-126_v5_2026-11-17.md`) and the rulings on it (E-186: the regime-filter test given a spacing rule
and a runs floor). Section 10 maps every finding to its change. It goes to the red team's re-read
of this diff, then is pinned by its LF sha256 under a decision row (`tests/test_declarations_fixed.py`'s
calibration-plan test reads `docs/calibration/<name>.md` pins). The lead may rename it at the pin
(`Q-126_one_sample_plan_2.md`); `tests/test_q126_draft.py` finds it under either name.

**Every choice in this plan that differs from Q-108's pinned plan was made after Q-108's look** -- after its
calibration (E-127, E-149, E-150), its failed validation (E-159, E-160), the diagnosis (Q-125, E-161) and, for the
later texts, the red team's reads of the earlier ones. Each such choice is marked **(after the look, B-n)** where it
is made, and Appendix B lists them all with their basis. What is not marked is carried from Q-108's pinned plan
(`docs/calibration/Q-108_one_sample_plan.md`, sha256
`c8e7424b46ff0c60ecb5b3ea875ac3b77e70f090a52f0cc0d999d7e416486d7e`, E-115), cited by its section numbers. That text is
pinned, so a citation of it cannot drift.

Nothing in this plan has been built or run, and it holds no result:
- **The arithmetic** is printed by `docs/calibration/scripts/q126/q126_arith.py`, which draws no random number. Its
  inputs are this plan's declared constants and three of Q-108's result files, read as a calibration (they are not
  market outcomes): `results/q108_choice.csv` (`P`, `p_mc`), `results/q108_cal_size.csv` (`admitted_share`) and
  `results/q108_val_size.csv` (`count_k*`). Its cost lines read Q-108's two run logs: their per-null timing lines,
  their `EXIT 0` lines and the pairs step's peak working set.
- **Every figure below** is either a declared constant, a line that script prints, or a citation of a named section of
  Q-108's plan, Q-125's note or the audits. `tests/test_q126_draft.py` holds the figures to the script; it holds the
  cost figures when the two logs are present and says it skipped them when they are not.
- **No bar and no market outcome was read.** No seed of another block is written here: Q-108's blocks and the replica's
  seed are named by role only.

**Why** (E-159 to E-161; `docs/research/Q-125_validation_failure_2026-11-17.md`):
- Q-108 chose `cons_m1.25` in scope Q (E-149). Its validation failed E-052's criterion on one exact subset null,
  `sub:5000:05:win1:flip63`, at k = 13 to 18 (E-159; the audit `docs/audits/Q-108_validation_2026-11-17.md` re-derived
  it).
- The cause is Q-108's own section-1 mechanism acting through one trade set (Q-125, section 3): a 63-session flip null
  has 11 or 12 sign units, so the aligned and near-aligned patterns carry mass of the order of the family levels. On a
  subset whose quarter sums are even enough, every member clears m times its critical value there, whatever m is.
- **The calibration could not see it** (Q-125, section 2): 115 subsets a model cannot certify a bad-subset rate as
  small as a zero-tolerance validation over 115 fresh subsets punishes.
- This plan answers both: it tries the scope that removes the mechanism's domain first, and it sizes the calibration
  to the validation's exposure, on the exact side and, by a targeted probe, on the Monte Carlo side.

---

## 1. The mechanism this plan answers (Q-125, sections 2 and 3; no new arithmetic)

- **The atom.** Q-108's section 1 carries unchanged: at L = 63 the aligned pattern's mass A(63) is 1.41 to 3.26 times
  the levels at k = 13 to 20, so a test that rejects it at most phases is above nominal on that subset. At L = 55 it
  reaches the level at k = 20.
- **The lottery.** Whether a statistic rejects the aligned pattern on a subset depends on how even that subset's
  flip-block sums are. Over subsets the exact size is heavy-tailed: most subsets are near zero, a few are far above
  (Q-125, section 2.2).
- **A margin moves the threshold, not the tail.** No finite m removes the mechanism in scope Q (Q-125, H-d; the
  replica's item 3). A per-trade drift makes large subsets systematically even (the replica's item 2).
- **Scope D removes the domain of the exact flips at 55 and 63 sessions.** A side constant over 63-session blocks has
  at most 12 runs on the judged block, so R >= 13 never admits one (Q-108's 4.4). The replica's scope-D zeros were at
  L = 63 only, where the admission's arithmetic excludes every cell: they carry no information about what scope D
  leaves (the red team's m4).
- **What is left in scope D** is the admitted part of the flips at 42 sessions, the alternating models and the Markov
  models. **The mechanism acts there too, on the Monte Carlo side** (the red team's M1): on Q-108's validation the worst
  Monte Carlo null of `cons` and of `cons_m1.25` in scope D was the failing subset `sub:5000:05` under the admitted
  Markov-50 paths. Section 3.2's probe sizes that side as well.

---

## 2. The candidates

### 2.1 The common setting (Q-108's 2.1, unchanged)

The pair difference x_i, the session sums S_j and N_j on A1's 657 judged sessions (E-094 (2)'s count and sha256
asserted by every runner), the blocks `lift_bound.block_index(657, b)`, the levels 0.05/(k(k+1)) at **k = 13..20**
(`lift_one_sample.K_RANGE_1S`) with 0.001, 0.005, 0.01 and 0.025 beside, and the MDL. `lift_bound.py` keeps its blob,
which F-03 pins.

### 2.2 The candidates and the order they are tried in

**Scope D first, then a scope-Q branch (after the look, B-1).** Q-108 tried scope Q first; this plan reverses it. When
scope D chooses, the scope-Q branch's own choice is validated beside it as a **second statistic** for one declared
domain (2.5; after the look, B-25).

| row | name | margin m | members | scope D | scope Q branch |
|---|---|---|---|---|---|
| 1 | `cons` | 1.0 | `t21w`, `t42w`, `t63w` (CR1, t with df G' - 1), each rejecting at est - m t(1 - a; G' - 1) se > 0 | yes | no |
| 2 | `cons_m1.125` | 1.125 | the same three | yes | no |
| 3 | `cons_m1.25` | 1.25 | the same three | yes | no |
| 4 | `cons_m1.375` | 1.375 | the same three | yes | no |
| 5 | `cons_m1.5` | 1.5 | the same three | yes | **yes** |
| 6 | `cons_m1.75` | 1.75 | the same three | yes | **yes** |
| 7 | `cons_m2` | 2.0 | the same three | yes | **yes** |
| 8 | `cons_bm_m1.25` (Q-108's C6) | 1.25 | `t21bm`, `t42bm`, `t63bm`: CR2 variance and Bell-McCaffrey df, Q-108's 2.2 formulas | yes | no |

- **The grid (after the look, B-2, B-3).** The margins are declared now: 1.0, 1.125, 1.25, 1.375, 1.5, 1.75 and 2.0.
  - 1.0 is `cons` itself. It failed the alternating floor in scope D at Q-108's calibration (`q108_choice.csv`, its
    `cond1_floors` row). It is kept because the brief's grid starts at 1.0, and the calibration decides.
  - 1.125 and 1.375 are new. They give resolution where Q-125's option 3 expects scope D's choice ("likely 1.25 or
    less"). Their definition is the others' with that m.
- **The scope-Q branch (after the look, B-4)** holds only m >= 1.5. Q-125's H-b shows that `cons_m1.5` would have held
  on the failing null at every k, by a bound drawn from the file. That is no proof of safety elsewhere, so the branch
  is chosen only under the sized calibration (3.2).
- **C6 in scope D only (B-5).** Its margin is 1.25, below the branch's 1.5.
- **Nesting.** Rows 1 to 7 are nested in m: on every sample a larger margin's rejections are a subset of a smaller's,
  at every level and in either scope (the critical value only grows with m, and scope D adds the same admission). So
  their exact sizes, their Monte Carlo counts, their bad-subset counts and their eligibility are monotone in m on shared
  draws. Section 4.3 uses this. Row 8 is not nested with rows 1 to 7.
- **Every candidate is computed in both scopes on the same draws (B-15).** A (candidate, scope) pair outside the table's
  "yes" cells is reported beside and decides nothing.
- **Ties** go to fewer members, then to the earlier row.

### 2.3 Dropped from Q-108's set (after the look, B-2)

| Q-108 id | name | why dropped |
|---|---|---|
| C5 | `cons_bm` | failed the floors in both scopes at Q-108's calibration (`q108_choice.csv`, `cond1_floors`) |
| C7 | `cons_im` | the same |
| C8 | `sn` | the same; it also needs a reference table, which this plan does not draw |
| C9 | `cons_sn` | the same |

Dropping a candidate is not dropping a null construction (Q-108's 7 item 4 forbids the latter only). Each of the four
failed at the calibration, before the validation was run. The choice to drop them is still after Q-108's look, and is
labelled.

### 2.4 Where the code goes (B-13)

- The build adds the grid in a **new module**, `extended/lift_one_sample2.py`, which imports
  `extended/lift_one_sample.py` and changes none of its definitions. Its own blob is pinned only by an adoption row.
- `lift_one_sample.py` stays as built (E-126), so Q-108's result files keep their code.
- The runners are `scripts/q126_calibrate.py` and `scripts/q126_validate.py`. They may import Q-108's runners'
  functions (the pairs step, the null constructions, the criterion) and must not edit them. **They pass every seed
  explicitly and assert where each draw's seed came from** (4.1's provenance assertion; B-28).

### 2.5 Which statistic a family uses: fixed by its declared persistence, never by an outcome (after the look, B-25)

A family states its side persistence before its pin (E-035 (6)): the length, in sessions, over which its design's side
is held -- a regime filter's regime length, or the mean dwell of a switching side. That statement decides which
adopted statistic, if any, its C1 may use, **and the band check below holds the family to it**:

| the family's declared side persistence | when scope D chose the primary | when the scope-Q branch is the primary (scope D chose none) |
|---|---|---|
| below 42 sessions | the primary, in scope D (its cells admitted by 4.4) | the primary, in scope Q |
| 42 to 50 sessions | **the second statistic**, in scope Q, if it HOLDS its own validation | the primary, in scope Q |
| 51 to 62 sessions | the primary, in scope D (4.4 admits almost none: section 5's table) | the primary, in scope Q |
| 63 sessions or more | no one-sample line | no one-sample line |

- **Why 42 to 50** (corrected twice; the red team's m1 and F-2). The band's lower edge is the flips at 42 sessions,
  of which scope D admits 0.030 (section 5's table); they touch 16 or 17 blocks on the judged block. Its upper edge is
  the Markov sides of mean dwell 50: scope D admits 0.606 of them, so about two in five are excluded. **Compared in one
  unit, runs:** a Markov-50 side has about 14.1 runs on the judged block, while a flip at 42 has about 8.8 and a flip
  at 55 about 7.0, because a flip's independent block signs repeat (blocks: 16 or 17 at 42, 12 or 13 at 55). The
  band's edges rest on the calibrated class -- the flip-42 and Markov-50 nulls -- not on a count of units. It is the
  lead's domain (E-173).
- **A family's k is unchanged** (the red team's n3). A family uses exactly one statistic, fixed before its pin by its
  band, so its family number and its level are those of its own row; the second statistic adds no test to any family.
- **No switch after a read.** A family in the first or third row whose cell scope D does not admit at stage C is "not
  claimed", unless its pinned text declared a two-sample line for that cell before any read (Q-108's 4.4). It does not
  fall to the second statistic: that would choose a statistic after reading the judged sides.
- **A statistic that FAILS** leaves its rows with no one-sample line. The other statistic is not extended to them.

**The band check (after the look, B-31, B-32, B-33; the red team's M-D, F-1, F-2; E-182, E-184).** A family's sides
are checked against its declared band from its sides only, never from an outcome. Each of the two kinds a family
declares (a regime filter or a switching side, as above) is checked by its own model, and both by a balance limit:
- **The balance limit, for every kind (F-1).** The mean side -- |sum of m_j| over the number of non-tie sessions of
  4.4's series, on the span read -- is at most b. **The rule:** b is the largest, over every flip and every Markov
  side whose length (a flip's block, a Markov side's mean dwell) lies in the band, of the 97.5 % quantile of |mean side|
  on the span's n sessions, every session non-tie. The flips are exact (independent fair block signs, phase uniform,
  by convolution) and the Markov sides exact (by recursion over the count of long sessions), so no seed is drawn.
  On the judged block's 657 sessions b is 0.5434 below 42, 0.5982 for 42 to 50 and 0.6651 for 51 to 62; on a
  1,006-session choice block 0.4473, 0.5030 and 0.5467 (`q126_arith.py`'s `band_b`). It refuses the red team's
  dominated side -- long on every session but 8 evenly spaced one-session shorts, so 17 runs and a mean side of
  0.9756 -- in every band, and every side long or short on most of the span.
- **A regime filter** (a declared regime length L, its regimes' decision points written in its pinned text; after
  the look, B-33, the red team's V-1, E-186). Four conditions:
  - **(a) spacing:** every interior regime -- between two consecutive declared decision points -- has a length in the
    band; only the span's first and last partial regimes are exempt;
  - **(b)** every change of the non-tie series falls on a declared decision point (a change between two non-tie
    sessions has a decision point between them);
  - **(c) the runs floor, one-sided:** the number of declared decision points at which the non-tie series changes sign
    is at least the 1.25 % quantile of Bin(B - 1, 1/2), B the number of regimes the span touches -- under independent
    fair regime signs that count is exactly this binomial (`q126_arith.py`'s `regime_floor`). On the judged block a
    filter in 42 to 50 touches 14 to 17 regimes and its floor is 3 changes (4 at 17); one in 51 to 62 touches 11 to 14,
    floor 2 (3 at 14). The floor misses a class filter with at most 0.0112 (at B = 14);
  - **(d)** the balance limit.

  R itself is not used: a filter whose independent regime signs repeat has half as many runs as regimes. **The three
  gamed sides the red team constructed are refused** (`regime_filter_check`, held by T-0): a side that switches once in
  657 sessions with 15 decision points 44 apart, one at the switch (the runs floor); three fixed regimes of 219 with
  points 43 or 44 apart, two at the switches (the runs floor); two halves with a burst of daily switches at 13 crowded
  points (the spacing). An honest 44-session filter with alternating regime signs passes.
- **A switching side** (a declared mean dwell D): R, the runs of 4.4's non-tie series, lies in the band's runs
  interval on n sessions (`band_interval`):
  - its lower limit is 1 plus the 1.25 % quantile of Bin(n - 1, 1/hi), hi the band's upper end;
  - it is raised to one more than the most runs of a side constant over 126 sessions (two quarters) **only where that
    floor binds and keeps every Markov side of the band within the refusal rule below**;
  - its upper limit is 1 plus the 98.75 % quantile of Bin(n - 1, 1/lo), lo the band's lower end (none below 42).
  - On the judged block: below 42, R >= 9; 42 to 50, 8 <= R <= 26 (the floor kept); 51 to 62, 5 <= R <= 22 (the floor
    dropped: it would refuse the band's Markov-62 sides too often). On a 1,006-session choice block: R >= 15; 12 to 36;
    10 to 31 (the floor kept). A family reading another span takes its own n.
- **The refusal rule (E-184).** No model of the band's own -- a flip at any length in the band, read as a regime filter,
  or a Markov side at any dwell in the band -- is refused with more than 0.05. `q126_arith.py` prints the largest
  in-band refusal of each kind, each a bound (for regime filters the runs floor's miss plus the balance limit's; for
  switching sides the runs interval's miss plus the balance limit's):
  - on the judged block: regime filters 0.0338, 0.0341 and 0.0288 in the three bands; switching sides 0.0318, 0.0462
    and 0.0287;
  - on a 1,006-session choice block: regime filters 0.0319, 0.0288 and 0.0318; switching sides 0.0293, 0.0293 and
    0.0409;
  - at the bands' edges on the judged block: the flips at 42 and 50, 0.0266 and 0.0341; at 51 and 62, 0.0278 and
    0.0288; the Markov sides at 42 and 50, 0.0261 and 0.0462; at 51 and 62, 0.0235 and 0.0287.
- **What n is, and the dense case (a reading; the red team's V-2, E-186).** n is the span's session count, never the
  non-tie count. The refusal rule and every refusal printed here are for the dense case, every session traded. A family
  trading on part of the span is refused more -- thinning cancels nearby switches and makes the mean side more
  variable -- which costs power, never size (refusing more never raises a false pass). The red team's illustration
  (simulated, its own seed; `docs/reviews/DRAFT_Q-126_v5_2026-11-17.md`, V-2): in 42 to 50 on the judged block a
  Markov-50 side was refused about 0.04 dense, 0.05 at half the sessions traded, 0.06 at three in ten and 0.10 at
  fifteen in a hundred. A family states its traded share beside its band.
- **Where it runs:**
  - on the choice block, at stage A, before the family's pin, on the span stage A reads;
  - on the judged block, inside stage C, before any outcome is read -- the same read and purpose as 4.4's judged check.
- **A mismatch.** **On the judged block a mismatch is "not claimed"**, never a switch of band, kind or statistic. On the
  choice block, before its pin, a family that misses its declared band may re-declare its band or kind, from its sides
  only; the re-declaration and the choice-block figures are recorded in its pinning row (the red team's m-3, E-184).
  "Not claimed" binds from the pin.
- **The residual: what the check does not exclude (F-3).** Each figure is printed by `q126_arith.py`:
  - **Fixed regimes, for a declared switching side.** A side constant over long regimes can still reach the band's runs
    floor when its regimes are at most: on the judged block 93 sessions below 42, 109 for 42 to 50 and 218 for 51 to
    62; on a 1,006-session choice block 77, 100 and 125. So regimes from 64 sessions up to those lengths cannot be told
    by R from the class (64 to 109 on the judged block and 64 to 125 on the choice block where the two-quarters floor
    is kept).
  - **Markov sides beyond the class's longest dwell, 80.** At most this share of them passes, by the runs interval
    alone: on the judged block, for 42 to 50, 0.712 at dwell 80, 0.483 at 100, 0.274 at 125, 0.152 at 150 and 0.049 at
    200; for 51 to 62, 0.964, 0.893, 0.769, 0.637 and 0.415; on the choice block, for 51 to 62, 0.880, 0.674, 0.413,
    0.232 and 0.069.
  - **Dominated sides are now closed** by the balance limit.
  - **Long regimes with short reversals at their edges** -- for example three regimes of 219 sessions, one one-session
    reversal each, so 9 runs and a balanced mean side -- pass a switching side's check in 42 to 50 on the judged
    block. Read as a regime filter, the same side is refused by the spacing rule: each reversal puts two changes one
    session apart (`q126_arith.py`).
  - **Regime filters that change at only a few of their points, above the floor** (the red team's V-1). They are the
    class's own tail, which the validation covers. A 126-session alternation declared as a 42-session filter touches
    16 regimes and changes at 5 points, above the floor of 3; a class filter changes at 4 or fewer with 0.0592. Three
    fixed regimes of about 220 sessions pass as a 55-session filter, the floor being 2 changes for 11 to 13 regimes;
    a class filter at 12 regimes changes at 2 or fewer with 0.0327.
  - **The second column (the red team's n-4 and V-5).** When the scope-Q branch is the primary, every band uses the
    same statistic, so the check binds at its loosest band: a declared switching side needs only R >= 5 on the judged
    block (10 on a 1,006-session choice block) and a mean side at most 0.6651 (0.5467), whatever band it declares; a
    regime filter needs its own band's spacing and runs floor and the same balance limit. The residual's fixed regimes
    up to 218 sessions on the judged block therefore apply to every switching-side family there. In the first column
    the band check binds only the second statistic's row; 4.4's admission dominates the other two.
  - The bands' intervals overlap, so a family whose sides fit two bands still declares one; it does so before its pin,
    from sides only.

---

## 3. The nulls

### 3.1 Q-108's class, unchanged (Q-108's 3.1 to 3.5)

**Kept whole (Q-108's 7 item 4):**
- the side models: flips at L = 1, 5, 21 (Monte Carlo) and 42, 55, 63 (exact); the coin; alternating at 45 and 55
  (exact); Markov with mean dwell 30, 50 and 80 (Monte Carlo);
- the fixed-data streams `offered` and `taken`;
- 23 fresh subsets of P-16's judged offers at each of 200, 500, 1,000, 2,000 and 5,000 trades, the persistent models
  on all 23 and the flips at 1 and 5 and the coin on the first 5;
- the values `win1` and `net3`;
- Q-16's realistic synthetic nulls (25);
- the per-subset size deciding (Q-108's 3.4); the `flat` form and the count-persistent nulls beside;
- the pattern encoding, the cell order and the alternating convention of Q-108's 3.1.

**The count, as Q-108's 3.5:** 2,293 nulls in the rule -- 1,170 exact and 1,123 Monte Carlo -- and 84 beside (54
count-persistent, 30 `flat`). Replications: 200,000 a Monte Carlo null in the rule, 100,000 beside.

In this plan these are **the core**: subsets j = 0 to 22 at each size, on this plan's seeds.

### 3.2 The sizing subsets and the probe: the calibration sized to the validation's exposure (after the look, B-6)

**The validation's exposure** (it is the validation's own class, 3.1, so it is fixed now): 23 fresh subsets at each
of five sizes, **115 subsets**, each at two values and five exact models, **1,150 exact subset nulls**.

**What "bad" means.** A subset is bad for a (candidate, scope) if, at either value and under any of the five exact
models, its exact size is above nominal at some k in 13..20 (on an alternating model: any configuration rejects). That
is exactly what fails E-052's criterion on the validation. Badness is counted per subset, the union over values and
models, because one subset's nulls share its trades (Q-108's 3.2; Q-125 found the failing subset the worst under every
persistent model).

**How many subsets (the rule of three's form).**
- The validation punishes a pooled bad-subset rate r_V at which its 115 subsets all hold with probability 0.9:
  r_V = 1 - 0.9^(1/115) = 9.1576e-04 (`q126_arith.py`).
- A calibration that sees a subset at that rate with probability at least 0.95 needs N subsets with
  1 - (1 - r_V)^N >= 0.95: **at least 3,270 subsets pooled, 654 a size.**
- **Declared: 660 subsets at each size, 3,300 in all**, j = 0 to 659. The first 23 at each size are the core (3.1);
  j = 23 to 659 are the sizing subsets.
- **At every block length.** Every subset, core and sizing, is enumerated exactly at L = 42, 55 and 63 and on both
  alternating models, at both values. So each statement below holds at each block length as well as pooled.

**The floor: zero tolerance (after the look, B-21; the lead's rulings E-176, reversing E-173's allowance, and
E-182).** A candidate is refused if **any** of the 3,300 subsets is bad (c = 0).
- At r_V the floor sees a bad subset, and refuses, with probability 0.9514. Zero bad subsets bound the pooled rate, at
  95 %, by about 3/3,300 = 9.0909e-04 (the rule of three's approximation of the exact 9.0739e-04 below; the red
  team's m-2), at which the validation's exact part passes with probability 0.9007.
- **Per size** (the red team's m5): zero bad subsets of one size's 660 bound that size's rate at 4.5287e-03. The pooled
  figures are the validation's yardstick, which draws every size; they are not a single design's, which has one size.
  Both real failures fell at 5,000 trades.

**What the floor guarantees: a bound, whatever the rates** (section 4.3 derives it). The chance that a statistic the
rule chooses holds this calibration and then fails the validation's exact part is bounded by
- 0.0126 for one candidate;
- 0.0337 for a branch nested in m;
- **0.0463 for the primary** (scope D's nested grid and C6; 0.0337 when the scope-Q branch is the primary);
- **0.0337 for the second statistic** (2.5);
- 0.0800 over the whole rule.

These are suprema over every configuration of rates, not chances.

**Why zero tolerance: the floor is the line's main guarantee of size over rare configurations (the lead's ruling,
E-182, correcting E-176's basis).**
- **It certifies far more than the validation can.** After zero bad subsets the 95 % upper limit on the pooled
  bad-subset rate is 9.0739e-04 from the calibration's 3,300 subsets, and 2.5713e-02 from the validation's 115. The
  validation alone could adopt a statistic with a rare over-rejecting corner that it never draws. (A reading, the red
  team's n-3: both limits are per candidate, before the choice -- after it, the guarantee is the nested bounds above --
  and both are for subsets of P-16's judged offers at the five sizes; a family's own trades are covered only as far
  as the class represents them.)
- **Such a statistic would pass families falsely.** A one-sample line whose size fails on a rare configuration of
  trades rejects, for the family that has that configuration, at more than its level. That is worse than having no
  line, where families decide by the two-sample forms (section 7).
- **So the floor is kept strict, and stricter than the validation**: it refuses a candidate at r_95 -- the rate
  r_95 = 1 - 0.95^(1/115) = 4.4593e-04 at which the validation's exact part passes it with probability 0.95 -- with
  0.7705.
- **Withdrawn** (E-182): the third text's claims that "a floor refusal costs one grid step" and that "the strict floor
  fails fewer profitable models". Neither is shown: refusals are correlated across the nested grid, a refusal at a
  branch's top margin empties the branch (NONE), and the comparison with the two-sample forms' power is not computed.
- **The price, stated plainly** (a declared reading, 4.3): the floor can empty a branch. At a bad-subset rate flat in m
  -- the scope-Q branch's plausible case, since no finite margin removes the mechanism there (Q-125, H-d) -- it does so
  with 1 - (1 - r)^3300: 0.2811 at r = 1e-04 and 0.6285 at 3e-04, where the validation would pass with 0.9886 and
  0.9661.
- **E-173's allowance** (at most c bad subsets, c the least count refusing at r_95 with at most 0.10, which is 3) was
  declared in the second text so that the floor would be no stricter than the validation. It would refuse at r_95 with
  0.0621 (c = 2 with 0.1840), but it raises the rule's bound to 0.3206 (0.1925 for the primary) and certifies less.
  Under it the nested bound falls only towards 0.05 as the calibration grows -- 0.0985 at 6,600 subsets, 0.0831 at
  13,200 and 0.0712 at 26,400 (beside, not taken). It is kept as a reading only (4.3).

**Q-108's own design, for comparison.** With 115 calibration subsets against 115 validation subsets and zero tolerance,
the one-candidate and nested bounds are 0.2500 and 0.5000, and r_V was seen with probability 0.1000. That is the
diagnosis's "roughly two orders of magnitude" (Q-125, section 2.2), stated as a bound.

**Pooling over sizes is exact here.** Each size has 660 calibration subsets against 23 validation subsets, the same
ratio, so the calibration's chance of holding and the validation's are functions of the same per-size rates (4.3).
That holds at c = 0; the c = 1 to 3 rows of 4.3's comparison assume equal rates across sizes (the red team's n2).

**What the sizing subsets carry (B-7).** The five exact models at both values. Beyond that, only the probe below.

**The Monte Carlo probe (after the look, B-22; the lead's ruling on the red team's M1, E-173).** Section 1's mechanism
acts on the Monte Carlo side through the same subsets, so the tail of the sizing subsets is probed there:
- **Which subsets (B-23).** At each size, the 23 sizing subsets with the largest exact size, ranked by a statistic
  outside the rule's pairs -- `cons` in scope Q (row 1 is in the rule in scope D only) -- by the sum over both values
  and the flips at 42, 55 and 63 of its exact size divided by the level at k = 13; ties to the smaller j. The ranking
  is fixed before the run and the same for every candidate. `cons` in scope Q rejects every cell rows 1 to 7 reject in
  either scope; it does not dominate C6 (row 8), whose tail is probed by proxy only (the red team's n1). Q-125 found the
  failing subset the worst under every persistent model.
- **What they carry.** The four persistent Monte Carlo models -- flips at 21 and Markov with dwell 30, 50 and 80 -- at
  both values and 200,000 replications: 23 x 5 x 4 x 2 = **920 probed nulls**, in Q-108's 3.1 constructions.
- **The condition (condition 4 of 4.2).** A candidate is ineligible in a scope if any probed null's rejections reach
  E-052's failure count at any k in 13..20 -- the count at which the validation would fail that null.
- **Why it is strict (the red team's M-B, E-182).** The probe stands on the floor's basis: it guards the line's size
  over a rare configuration, here a Monte Carlo tail. It is stricter than the validation whenever its ranking finds
  the tail: at the tail rate the validation passes a candidate with probability 0.95, the probe refuses it with up to
  1 - 0.95^(3185/115) = 0.758 (4.3). If the ranking does not find the tail, the probe is 115 random sizing subsets, as
  strict as the validation.
- **Not in P_MC or the point-rate floor (B-29).** Those model the validation's counterpart of each core null. The probe
  is a search of the tail, judged per null by E-052's failure count.
- **The seeds** are the calibration block's last role (4.1).

**The count.** 3,185 sizing subsets x 2 values x 5 exact models = **31,850 sizing nulls**, all exact, all in the rule.
With the core: 33,020 exact nulls (20 on the fixed streams) and 1,123 Monte Carlo, **34,143 in conditions 1 to 3**,
and the 920 probed nulls in condition 4: **35,063 in the rule**. Exact enumerations: 33,000 on subsets, 6,600 of them
at L = 42.

### 3.3 The drift nulls, beside (after the look, B-9)

They replicate the diagnosis's mechanism on synthetic data, as Q-125's Appendix A does. **They decide nothing.** They
are reported beside, in both runs, so that the size of each candidate under a declared per-trade drift is on record.

- **The generator** is Q-125's Appendix A `draw(rng, z, T, d, varying)`, verbatim (this plan's Appendix A copies it):
  657 sessions; z trades over T traded sessions with gamma-weighted counts; per-trade values in {-0.5, 0, +0.5} like
  `win1`; a drift delta with P(+0.5) - P(-0.5) = 2 delta, constant, or of a random sign per 63-session calendar block.
- **The scenarios** are Appendix A's eight, in its order (index 0 to 7):

| index | label | z | T | delta | sign varies by quarter |
|---|---|---|---|---|---|
| 0 | A | 5,000 | 560 | 0 | no |
| 1 | B | 5,000 | 560 | 0.01 | no |
| 2 | C | 5,000 | 560 | 0.02 | no |
| 3 | D | 5,000 | 560 | 0.03 | no |
| 4 | E | 500 | 300 | 0.02 | no |
| 5 | F | 5,000 | 150 | 0 | no |
| 6 | G | 5,000 | 150 | 0.02 | no |
| 7 | H | 5,000 | 560 | 0.02 | yes |

- **The drift sizes are the replica's, invented, not estimates of P-16's** (Q-125, section 3.2; B-20).
  Scenarios A and F are the no-drift controls.
- **150 populations a scenario**, as the replica: 1,200 populations.
- **Exact at every exact model: L = 42, 55 and 63 and both alternating models** (5 models a population: 6,000 nulls
  beside; after the look, B-26, the red team's m4). **In scope D their sizes at L = 55 and 63 are zero by the
  admission's arithmetic** and carry no information; the informative scope-D readings are L = 42 and the alternating
  models.
- Every candidate in both scopes, on the same enumeration.

**What a drift reading means.** Nothing in the choice or the verdict. If a statistic is adopted, its adoption row
reports beside it, per scenario and per exact model, the share of populations above nominal at any k, so a family
declaring on the line sees how it behaves under a drift of those sizes.

### 3.4 Which size decides (Q-108's 3.4, unchanged)

The per-subset size. Every subset is a null of its own in the rule and in the criterion. The `flat` form is beside.

### 3.5 The null set and its count

| part | nulls | computed | in |
|---|---|---|---|
| the core (Q-108's class, 3.1) | 2,293 | 1,170 exact, 1,123 Monte Carlo | the rule and the criterion |
| the sizing subsets (3.2) | 31,850 | exact | the rule (calibration only) |
| the probe (3.2) | 920 | Monte Carlo | the rule's condition 4 (calibration only) |
| **in the calibration's rule** | **35,063** | 33,020 exact, 2,043 Monte Carlo | |
| **in the validation's criterion, per statistic** | **2,293** | Q-108's class on the validation seeds | |
| beside: count-persistent and `flat` | 84 | Monte Carlo | both runs |
| beside: the drift nulls (3.3) | 6,000 | exact | both runs |

The validation does not draw the sizing subsets or the probe (B-14). Its exposure is Q-108's, so the sizing is finite.

---

## 4. Seeds, the choice rule, the validation criterion, scope D

### 4.1 The seed blocks (after the look, B-12)

**Q-108's two blocks are retired.** Its calibration block was drawn by its calibration, its validation block by its
validation. Neither is drawn again, and this plan does not write their numbers.

**How these blocks were found** (2026-11-17, before the first text was committed):
- A word-bounded literal search for every seed of both blocks found none:
  - `git grep -w` in every worktree's working copy, tracked and untracked (the main tree and the ten worktrees);
  - `git grep -w` on every branch, remote and tag (23 refs);
  - every line added or removed in every commit reachable from them (`git log --all -p`, 422 commits).
- **No written range covers them.** The written ranges found by the same search end below them. At the search's
  commit (ec6905a) the nearest derived range was `tests/test_features_lookahead.py`'s `SEED_REPLACE + 1000 + i` for
  i < 790 (its `len(rows) == 790`), whose last value is 89 below the calibration block's first seed. Q-128 (E-178) has
  since replaced that range by `SeedSequence` children of the named seed, which depend on no other number.
- **Derived seeds: Q-108's AST fold guard** (`scripts/q108_calibrate.py`'s `derived_problems`), re-pointed at these two
  blocks, over every `.py` of the working tree and every ref: no refusal. It printed the lookahead test's three loop
  expressions, the nearest needing a loop reach of 878 to land, and summarised the rest as over a million seeds away.
- **Imported names plus offsets, by hand** (Q-108's 4.1 list, re-checked against these blocks):
  - Stage 2's `planted_effect` seed plus multiples of 1,000, and its `power_cell` offsets, have residues modulo 1,000
    that these blocks (residues 010 to 029) do not have;
  - `lift_bound.fixed_b_critical`'s seed plus 1,000 G plus the lags lands at least 880 above the validation block's
    last seed for every G >= 2, and G = 1 is no block count;
  - RD-01's `R.F.LADDER_SEED + i` and Stage 2's `fh.SEED + 1`, `fh.SEED + 2`, `sc.SEED + 1` are far below;
  - the vendored runtime-argument offsets (`seed + 1 + i` and the like) and Stage 1's `a.seed + ...` are not run here.
- The red team repeated the search on the first text's commit and found the blocks only in the plan and T-0.
- `tests/test_q126_draft.py` repeats the literal search on every run, and checks the look-ahead range's end from that
  test's text at the search's commit, ec6905a, read by `git show` (the red team's M-A).

**Calibration block, 20263010-20263019:**

| seed | use |
|---|---|
| 20263010 | the calibration build's tests |
| 20263011 | the fixed-data streams' Monte Carlo side draws: `default_rng([s, i])`, i the null's index (Q-108's 4.1 order) |
| 20263012 | the thinned subsets: subset (z, j) by `default_rng([s, z_index, j])`, j = 0 to 659 |
| 20263013 | the core subsets' Monte Carlo side draws: `default_rng([s, z_index, j, value_index, model_index])`, j = 0 to 22 |
| 20263014 | the realistic synthetic nulls: `default_rng([s, i])`, i the null's index in Q-16's list |
| 20263015 | the count-persistent nulls beside |
| 20263016 | the `flat` form beside: its fresh subsets and flips |
| 20263017 | the exact nulls' seeded sample of cells for the scalar re-decision: `default_rng([s, exact null index])` |
| 20263018 | the drift populations beside: population r of scenario c by `default_rng([s, c, r])` |
| 20263019 | the probe's Monte Carlo side draws (3.2): `default_rng([s, z_index, j, value_index, model_index])`, j the probed subset's own index (B-24) |

**Validation block, 20263020-20263029:**

| seed | use |
|---|---|
| 20263020 | the validation build's tests |
| 20263021 | the fixed-data streams' Monte Carlo side draws, in the calibration's order |
| 20263022 | the thinned subsets, j = 0 to 22 only (the validation draws no sizing subset) |
| 20263023 | the core subsets' Monte Carlo side draws, in the calibration's order |
| 20263024 | the realistic synthetic nulls, in the calibration's order |
| 20263025 | the count-persistent nulls beside |
| 20263026 | the `flat` form beside |
| 20263027 | the exact nulls' seeded sample of cells for the scalar re-decision |
| 20263028 | the drift populations beside, in the calibration's order |
| 20263029 | spare, drawn by nothing |

**The indices (every order fixed).** As Q-108's 4.1, with these changes:
- `j` runs 0 to 659 at the calibration (0 to 22 at the validation). The core's Monte Carlo models and the flips at 1
  and 5 and the coin use j = 0 to 22 and j = 0 to 4 as in Q-108.
- `model_index` is Q-108's (section 3.1's order) for the probe as well: 2 for the flips at 21, 9, 10 and 11 for
  Markov 30, 50 and 80.
- **The exact null index** is the position when the exact nulls are listed by data (`offered`, `taken`, then the
  subsets by `z_index` and then `j`), then value, then exact model (flips at 42, 55 and 63, alternating 45 and 55),
  outermost first: 0 to 33,019 at the calibration, 0 to 1,169 at the validation.
- **The drift nulls**: scenario c in 3.3's order (0 to 7), population r = 0 to 149.
- C8's reference table is not drawn: no candidate needs it.

**The seed-provenance assertion (after the look, B-28; the red team's M4, E-173).** Q-108's runners default to Q-108's
retired seed maps: `scripts/q108_calibrate.py`'s `null_plan(seeds=None)` and `expected_counts(seeds=None)` fall back
to its calibration map, and `scripts/q108_validate.py` holds its validation map. A q126 runner that called them without
its own map would redraw Q-108's subsets -- at the validation, the very draws on which `cons_m1.25` in scope D is known
to hold. So each q126 runner, **before any draw**:
- asserts that every generator entropy in its plan of nulls -- `entropy`, `subset_entropy`, `sample_entropy`, the
  probe's and the drift's -- is, in full, the entropy this section declares for that null: its block's seed under its
  role, then the declared indices in the declared order (so the core's exact nulls carry this plan's index, 0 to
  33,019, and not Q-108's; the red team's n4);
- asserts that the seed map it writes into every manifest equals this section's table **as parsed from the pinned
  plan**, its sha256 checked, never a copy in the runner's own code (the red team's n5);
- refuses to start otherwise. The build carries a test that calls each imported Q-108 construction without a seed map
  and checks that the assertion refuses it.

**The scalar re-decision (Q-108's 2.1 and 4.1; B-11).**
- On the core's 1,170 exact nulls, as Q-108: per candidate and scope, the first 100 cells in cell order rejecting at
  k = 13 (in scope D, rejecting and admitted), plus the same 20 uniform cells for every candidate.
- **On the sizing nulls,** the first 5 rejecting cells per candidate and scope, and no uniform cells, so the
  re-decision does not dominate the run. The red team judged the uniform cells to catch almost no under-count (its n3).
- Every sampled cell is re-decided by the scalar form at every k in 13..20. A mismatch stops the run (E-115 (R1)).

**The runners' guard** is Q-108's (literal and AST-folded, refusing a seed of either block outside the allow-list,
printing an unbounded loop for a hand check, never refusing on an assumed reach), pointed at these two blocks. Its
allow-list names this plan, `docs/calibration/scripts/q126/`, the new module, the two runners and their tests,
`tests/test_q126_draft.py`, `DECISIONS.md` and the lead's records, this plan's own result files, and the lookahead
test's hand-checked expressions. The build adds its files to T-0's declared uses as it writes them (the red team's n4).

### 4.2 The choice (calibration seeds only; coded in the calibration script and applied by it, never by hand)

**A candidate is eligible in a scope when all of these hold on its calibration results in that scope:**
1. **The floors, over the sized set:**
   - no core Monte Carlo null has its point rate above nominal at any k in 13..20 (Q-108's);
   - no exact null on the fixed streams has its exact size above nominal at any k (Q-108's);
   - **no subset of the 3,300 is bad** (3.2's zero tolerance; after the look, B-6, B-21). On the alternating models a
     subset is bad if any configuration rejects.
2. **P_MC >= 0.9** over the core's 1,123 Monte Carlo nulls, computed as Q-108's 4.2 (exactly, from the counts).
3. **The worst exact ratio over the core's 1,170 exact nulls is at most 1/4** (Q-108's condition 3 on Q-108's set; B-8).
   It is not applied to the sizing nulls: there it would be a stricter condition than Q-108 declared, chosen after the
   look, with a power cost of its own, while condition 1 already carries the sized guard.
4. **No probed null reaches its failure count** (3.2's probe: 920 nulls, E-052's failure counts; after the look,
   B-22).

**The nesting assertion (Q-108's 4.2)** stands: every candidate's Monte Carlo counts and exact sizes are non-increasing
in k, or the run stops with no choice. **Added (B-17):** on shared draws, rows 1 to 7's counts, sizes and bad-subset
counts are non-increasing in m at every k and in each scope (2.2). A violation stops the run, to be diagnosed under the
failure protocol.

**The order.**
1. **The primary in scope D:** among rows 1 to 8 in scope D (the procedure of 4.4), the eligible candidate with the
   smallest P (section 5). Ties: fewer members, then the earlier row.
2. **The scope-Q branch:** among rows 5 to 7 in scope Q, the eligible candidate with the smallest P, by the same rule.
   - If scope D chose, it is **the second statistic** (2.5), validated beside the primary.
   - If scope D chose none, it is **the primary**, and there is no second statistic.
3. **If neither scope has an eligible candidate: NONE.**

The scope-Q branch's choice is made by the same rule within scope Q in either case, so the second statistic adds no
choice of its own (E-173).

**What the script prints and writes.**
- It prints `CHOSEN <name> (scope D)` with `SECOND <name> (scope Q)` or `SECOND NONE`; or `CHOSEN <name> (scope Q)`; or
  `NONE`.
- `q126_choice.csv`: for each candidate in both scopes, each condition, P_MC, the worst exact ratio (overall, per exact
  model and on the core alone, with its null and k), the bad-subset count (pooled and per size and model), the probe's
  worst count as a share of its failure count (with its null and k), P, and whether the pair is in the rule or beside.
- **The cost of the rule, shown beside the choice (E-051):** the most powerful candidate refused by condition 1's sized
  part alone, by condition 3 alone and by condition 4 alone, if there is one, each with its P and the count that
  refused it; and **whether the floor alone emptied a branch** (the red team's M-C).
- **The probe's ranking**: per size, the 23 probed subsets' j and ranking score.

### 4.3 The validation criterion (E-052's, unchanged; Q-108's 4.3 word for word in substance)

- The validation runner reads the choice from `q126_choice.csv`, its manifest verified. Nothing is re-chosen.
- **Each chosen statistic** -- the primary, and the second statistic when there is one -- is judged on its own.
  **It HOLDS** if, at every k in 13..20, on every one of the 2,293 validation nulls -- the fresh subsets, the fixed-data
  streams and the fresh synthetic draws, all on the validation seeds:
  - a Monte Carlo null's 95 % Clopper-Pearson interval does not lie wholly above nominal. At 200,000 replications that
    means fewer rejections than 71, 63, 56, 50, 45, 41, 38 and 35 at k = 13..20;
  - an exact null's exact size is at or below nominal. On the alternating models: no configuration rejects.
- It **FAILS** if any null breaks either condition. It is **NOT CHECKED** -- never a pass -- if any null is missing.
- **One failure anywhere means no line for that statistic's rows of 2.5 and no re-choice** (section 7; B-30). The two
  statistics share the validation's draws, so their verdicts are positively associated; each verdict stands on its own.
- **Reported beside, never in the verdict:** `cons` in scope Q on the same draws (Q-108's C0 beside); the
  count-persistent nulls; the `flat` form; the drift nulls; the power on the validation toys.

**The power of the criterion itself (the operator's rule that a strict line must show power, not only size; B-16).** A
"correct" statistic here is one whose size is at or below nominal on every validation null. The criterion is kept
unchanged. What it costs such a statistic, and a nearly correct one whose exact part carries a small bad-subset rate,
is (`q126_arith.py`). The two parts share the core subsets, so their passes are positively associated (the red team's
m1): the product of a statistic's two rows is a lower bound on its chance of passing both.

| the statistic's profile | the chance that part passes |
|---|---|
| exact part: every subset at or below nominal | 1 (an exact size has no noise) |
| exact part: a pooled bad-subset rate of 1e-04 | 0.9886 |
| exact part: a rate of r_95, 4.4593e-04 | 0.9500 |
| exact part: a rate of 1e-03 | 0.8913 |
| exact part: a rate of 0.01 | 0.3148 |
| Monte Carlo part: every one of the 1,123 nulls at 0.5 of nominal | 0.9999 |
| Monte Carlo part: every null at 0.6 of nominal | 0.9955 |
| Monte Carlo part: every null at 0.7 of nominal | 0.8860 |
| Monte Carlo part: every null at 0.8 of nominal | 0.2003 |
| Monte Carlo part: every null at 0.9 of nominal | 0.0000 |
| Monte Carlo part: every null exactly at nominal | 0.0000 |

**How strict that is.** The criterion passes, with probability 0.9, at most 2 nulls exactly at nominal, 9 at 0.9 of
nominal, 74 at 0.8 and 978 at 0.7 (`q126_arith.py`). So **a statistic that is correct but hugs its level fails it**; one
that sits at about 0.6 of nominal or below on every Monte Carlo null passes that part almost surely. This is E-052's
design, and the operator's standing rule is answered by stating it: the line is strict, and its power is the rows above.

**The criterion's power on the candidates that matter**, by Q-108's own calibration: P_MC was 1.000000 for
`cons_m1.25` in both scopes, for `cons_m1.5` in scope Q and for C6 in scope D (`q108_choice.csv` `p_mc`). P_MC treats
each core null as standing for its validation counterpart, so it cannot see the subset lottery (Q-108's 4.2); the
probe (3.2) is what looks for it on the Monte Carlo side.

**The power of this plan's own floor (the red team's M2; B-21), a declared reading beside.** The floor is a
tightening, so its refusals are shown beside what the validation would do at the same rate, and beside E-173's
allowance that E-176 reversed. "Admits" is the floor's chance of passing a candidate at that pooled bad-subset rate
(`q126_arith.py`):

| pooled bad-subset rate | the floor admits (c = 0, declared) | E-173's allowance admitted (c = 3, reversed) | the validation's exact part passes |
|---|---|---|---|
| 1.0000e-05 | 0.9675 | 1.0000 | 0.9989 |
| 3.0000e-05 | 0.9057 | 1.0000 | 0.9966 |
| 1.0000e-04 | 0.7189 | 0.9996 | 0.9886 |
| 3.0000e-04 | 0.3715 | 0.9816 | 0.9661 |
| 4.4593e-04 (r_95) | 0.2295 | 0.9379 | 0.9500 |
| 9.1576e-04 (r_V) | 0.0486 | 0.6423 | 0.9000 |
| 1.0000e-03 | 0.0368 | 0.5803 | 0.8913 |
| 2.0000e-03 | 0.0014 | 0.1049 | 0.7944 |

**The allowances compared** (`q126_arith.py`): each allowance c's chance of refusing a candidate at r_95 and at r_V,
and its bounds on the chance that a chosen statistic holds the calibration and then fails the validation's exact part:

| c | refuses at r_95 | refuses at r_V | one candidate | a nested branch | the primary | the second statistic | the whole rule |
|---|---|---|---|---|---|---|---|
| 0 (declared) | 0.7705 | 0.9514 | 0.0126 | 0.0337 | 0.0463 | 0.0337 | 0.0800 |
| 1 | 0.4326 | 0.8043 | 0.0285 | 0.0662 | 0.0947 | 0.0662 | 0.1609 |
| 2 | 0.1840 | 0.5818 | 0.0460 | 0.0977 | 0.1437 | 0.0977 | 0.2414 |
| 3 (E-173, reversed) | 0.0621 | 0.3577 | 0.0644 | 0.1281 | 0.1925 | 0.1281 | 0.3206 |

- **The declared floor is stricter than the validation, on purpose** (E-182; 3.2). It refuses a candidate at a rate of
  1e-04, which the validation passes 98.9 % of the time, with probability 0.2811, and one at r_95 with 0.7705. That is
  the price of certifying the rate to 9.0739e-04 and of a bound of 0.0800 on the rule's validation route.

**The floor's chance of emptying a branch (NONE), a declared reading beside** (the red team's M-C; E-182). On a nested
grid of the seven margins, every other condition assumed to pass, with the red team's illustrative bad-subset rates
(not estimates; `q126_arith.py`): the chance the validation's exact part fails the choice, the chance the floor empties
the branch, and the mean P ratio of a choice that is made and holds:

| rate profile over m = 1.0 ... 2.0 | c | the validation fails the choice | NONE at the choice | mean P ratio of a held choice |
|---|---|---|---|---|
| A: 3e-4, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6 | 0 | 0.0173 | 0.0033 | 0.974 |
| | 3 | 0.0335 | 0.0000 | 0.818 |
| B: 1e-3, 3e-4, 1e-4, then as A | 0 | 0.0200 | 0.0033 | 1.005 |
| | 3 | 0.0769 | 0.0000 | 0.857 |
| C: 3e-4 at every margin | 0 | 0.0126 | 0.6285 | 0.814 |
| | 3 | 0.0333 | 0.0184 | 0.814 |

At a rate flat in m (Q-125's H-d: the scope-Q branch's plausible case), the zero-tolerance floor empties the branch
with 1 - (1 - r)^3300 (`q126_arith.py`):

| flat bad-subset rate | the floor empties the branch | the validation's exact part passes |
|---|---|---|
| 1e-05 | 0.0325 | 0.9989 |
| 3e-05 | 0.0943 | 0.9966 |
| 1e-04 | 0.2811 | 0.9886 |
| 3e-04 | 0.6285 | 0.9661 |
| 1e-03 | 0.9632 | 0.8913 |

These are the price of zero tolerance. Which profile holds is the run's to show; the choice's cost lines (4.2) report
whether the floor alone emptied a branch.
- **What a step costs.** Where a refusal moves the choice up the nested grid, each step costs, in minimum detectable
  lift (section 5's P ratios, interpolated at the two new margins): 0.114 from `cons` to `cons_m1.125`,
  0.102 to `cons_m1.25`, 0.094 to `cons_m1.375`, 0.086 to `cons_m1.5`, 0.159 to `cons_m1.75` and 0.138 to `cons_m2`.
  A design whose true lift lies inside a step is a profitable model the stricter statistic fails. Refusals are
  correlated across the grid (bad sets are nested), so the choice can move several steps, or empty the branch.

**The power of the probe (condition 4; the red team's M1 and M-B).** Per null the probe refuses exactly where the
validation would fail that null. At a common profile -- every probed null at one share of nominal -- it refuses as
follows (`q126_arith.py`); beside it, the validation's chance of passing its 1,123 Monte Carlo nulls at that share:

| every probed null at this share of nominal | one probed null refused | all 920 probed nulls: the probe refuses | the validation's 1,123 Monte Carlo nulls pass |
|---|---|---|---|
| 0.5 | 5.801e-08 | 0.0001 | 0.9999 |
| 0.6 | 4.038e-06 | 0.0037 | 0.9955 |
| 0.7 | 1.077e-04 | 0.0944 | 0.8860 |
| 0.8 | 1.431e-03 | 0.7321 | 0.2003 |
| 0.9 | 1.104e-02 | 1.0000 | 0.0000 |
| 1.0 | 5.362e-02 | 1.0000 | 0.0000 |

**But the probe is not a sample** (the red team's M-B): it holds the 23 worst of each size's 637 sizing subsets. When
a share of subsets carries a Monte Carlo tail and the ranking finds it, the probe sees up to 3,185/115 times the tail
subsets the validation's 115 random subsets see. At the tail rate where the validation passes a candidate with
probability 0.95, the probe then refuses it with up to **1 - 0.95^(3185/115) = 0.758** (`q126_arith.py`). That is the
floor's own strictness, kept on the floor's basis (3.2).

**The bound used in 3.2, derived.** Write n for the validation's subsets and N for the calibration's, at the same ratio
at every size, c for the floor's allowance and G(r) = P(Bin(N, r) <= c), the floor's chance of admitting a candidate at
rate r. P_m is the chance that candidate m is eligible at the calibration.
- For one candidate, the calibration admits with at most G(r) and the validation's exact part fails with
  1 - (1 - r)^n, so their product is at most the supremum over r of G(r) (1 - (1 - r)^n): 0.0126 at c = 0, the
  declared floor (0.0644 at E-173's c = 3).
- For the nested rows 1 to 7, eligibility is upward closed in m, and the choice is the smallest eligible m. The
  validation's exact part fails for m with 1 - (1 - r_m)^n, and P_m <= G(r_m), so it fails with at most
  h(P_m) = 1 - (1 - G^-1(P_m))^n, decreasing in P_m. The chance that the choice fails the validation's exact part is a
  sum of increments of P_m times h(P_m), at most the integral of h over (0, 1). Substituting p = G(r), that integral is
  1 - E[(1 - R)^n] with R ~ Beta(c + 1, N - c), which is 1 - prod over i < n of (N - c + i)/(N + 1 + i): **at the
  declared c = 0 it is n/(N + n) = 0.0337, whatever the rates and however fine the grid** (0.1281 at E-173's c = 3).
- C6 adds at most the one-candidate bound to the primary. The scope-Q branch is a nested family of its own: the second
  statistic's bound, or the primary's when scope D chose none.
- **The bound covers the exact part only.** The Monte Carlo part is guarded by P_MC on the core and by the probe on the
  tail.
- **The validation is not the line's certificate on the exact part** (the red team's n1). Its 115 subsets catch a
  bad-subset rate of 1e-03 with probability 0.1087; the calibration's 3,300 subsets carry the exact part's assurance
  (3.2's two upper limits).

### 4.4 Scope D: the admission and the procedure (Q-108's 4.4, with one condition added)

The admission's three conditions (the family's E-035 (6) declaration of side persistence below a quarter; the runs
check on the choice block; the same check on the judged block inside stage C, before any outcome), the check itself
(the non-tie series, R runs, E = (sum of run lengths)^2 / (sum of squared run lengths), R >= 13 on the judged block and
floor((n_c - 1)/63) + 3 on the span stage A reads, E >= 4, a single side never admitted), its calibration as a
procedure in every replication and every exact cell, and what happens at stage C are Q-108's 4.4, word for word in
substance. Section 2.5 decides which families use scope D at all.

**Added: the balance limit (after the look, B-32; the red team's F-1, E-184), before any run.** The admission also
requires the mean side of the non-tie series to be at most b_D on the span read, b_D being 2.5's rule over every flip
and Markov side of length 1 to 63 sessions (scope D's domain is persistence below a quarter): 0.6651 on the judged
block and 0.5467 on a 1,006-session choice block (`q126_arith.py`'s `admission_b`).
- **Why.** E >= 4 keeps out a dominated side only when its reversals cluster. Spread evenly, they cut the dominant run
  into many medium runs of one sign, and E grows with R: the red team's side, long on all but 8 sessions, has R = 17 and
  E = 9.02 and was admitted. It is the quarter-persistent, long-leaning kind scope D exists to exclude, and no class
  null resembles it.
- **Its coverage cost on the class** (the share of each side model's sides that the limit refuses on the judged
  block, every session non-tie; labelled after the look, B-32). **In the dense case, the share of all sides that the
  admission admits and the limit then removes is at most this** (the red team's V-3, E-186); on the class the share
  among the admitted is smaller still -- the red team's illustration (simulated): Markov-50 about 0.003 among its
  admitted sides, Markov-30 under 0.001, flip-21 none -- because admission favours many-run, balanced sides. The
  shares: flips at 1 and 5, 0.0000; at 21, 0.0001; at 42, 0.0051; at 55, 0.0119; at 63, 0.0219; Markov at
  dwell 30, 0.0007; at 50, 0.0098; at 80, 0.0435; the alternating models, 0.0000. On a sparse subset the non-tie series
  is shorter and |mean side| more variable, so the share refused there is larger; the calibration measures the
  procedure as declared, the limit included.
- **It changes the procedure calibrated,** so it is declared before the calibration run and never added after. The
  built forms are `lift_one_sample.admission`, `runs_and_effective` and `exact_flip`'s scope D, imported, with the
  balance limit applied beside them in the new module (6.1): per exact cell, the mean side is the sum over flip blocks
  of the block's sign times its traded sessions, over the traded sessions.

### 4.5 The rejecting cells (after the look, B-10)

- **For every exact null** -- core, sizing and drift beside -- **and every (candidate, scope) pair in the rule** (2.2's
  "yes" cells) **whose exact size is above a quarter of nominal at any k in 13..20**, the run writes one row per cell
  that rejects at k = 13. The nesting in k puts every family-level rejection there.
- **The columns:** the null; the candidate; the scope; the global cell index; the phase p; the pattern q (on an
  alternating model, the phase and "long" or "short" first); the blocks B; the cell's weight 2^(Bmax - B); whether the
  cell is admitted (scope D); and the largest k in 13..20 at which it rejects.
- **In the validation:** the same, for each chosen statistic in its scope.
- **Files:** `q126_cal_cells.csv` and `q126_val_cells.csv`, written through `extended.results` like every result.
- **Why** (Q-125, section 6 item 3): the next diagnosis then reads which patterns reject -- aligned or near-aligned, by
  phase -- from a file, instead of re-running anything.
- **What the cells carry (a disclosure; the red team's m6).** A subset's rejecting patterns are a function of its pair
  differences, which are P-16's judged outcomes. At L = 63 the aligned pattern at a phase is exactly the signs of that
  subset's flip-block sums, so **the file carries a coarse form -- signs only -- of the per-block sums that section 9
  declines to read directly.** It is written under the runs' `registered_design` read of P-16's pairs (Q-108's 6.1),
  and **nothing reads it before the validation's verdict** is recorded. P-16's judged pairs have been read before, as a
  source of null dependence (Q-108's 8); no family's outcome is in them.

---

## 5. Power: each candidate's minimum detectable lift (Q-108's 5, unchanged in definition)

**The toys and P** are Q-108's 5: subset j = 0 of each size, with the coin's side and with sides flipped by session,
value `win1`; P is the geometric mean over the ten toys of the 80th percentile of the MDL at k = 13, on the first
20,000 replications; in scope D a toy replication not admitted counts as infinite. The choice uses this calibration's
own P, on its own draws.

**The power cost of each candidate against `cons_m1.25`, before the run** (`q108_choice.csv` `P`, as a ratio to
`cons_m1.25`'s in scope Q; `q126_arith.py`):

| candidate | margin | P / P(`cons_m1.25`) | source |
|---|---|---|---|
| `cons` | 1.0 | 0.814 | file |
| `cons_m1.125` | 1.125 | 0.814 to 1.000 (linear interpolation 0.907) | bracketed by its neighbours |
| `cons_m1.25` | 1.25 | 1.000 | file |
| `cons_m1.375` | 1.375 | 1.000 to 1.188 (linear interpolation 1.094) | bracketed by its neighbours |
| `cons_m1.5` | 1.5 | 1.188 | file |
| `cons_m1.75` | 1.75 | 1.377 | file |
| `cons_m2` | 2.0 | 1.567 | file |
| `cons_bm_m1.25` | 1.25 | 1.009 | file |

- **How to read it.** A ratio of 1.188 means a design needs about 19 % more lift than under `cons_m1.25` to be detected
  as often. A design whose true lift lies between the two candidates' MDLs is a profitable model that the stricter one
  fails (the operator's rule). Section 4.3 gives the cost of one grid step.
- **The bracket is exact as a bound.** A margin's MDL is m crit se - est, increasing in m on every replication, so P is
  increasing in m. Q-108 did not run 1.125 or 1.375; the interpolations are estimates, not file values.
- **Scope D costs no power on an admitted cell.** P is the same in both scopes for every candidate (`q108_choice.csv`),
  because the toys' coin and daily sides are always admitted.

**The coverage cost of scope D: the designs it excludes.** The line exists in scope D only for admitted cells. Q-108's
calibration measured how often each side model's sides are admitted (`q108_cal_size.csv` `admitted_share`, scope D,
the in-rule fixed and subset nulls; the admission reads sides only, so it is the same for every candidate;
`q126_arith.py`):

| side model | admitted share (mean) | over the five sizes |
|---|---|---|
| flips at 1 and 5, the coin | 1.000 | 1.000 to 1.000 |
| flips at 21 | 0.928 | 0.923 to 0.930 |
| flips at 42 | 0.030 | 0.028 to 0.030 |
| flips at 55 | 0.000 | 0.000 to 0.000 |
| flips at 63 | 0.000 | 0.000 to 0.000 |
| alternating 45 | 1.000 | 1.000 to 1.000 |
| alternating 55 | 0.899 | 0.825 to 0.927 |
| Markov, dwell 30 | 0.984 | 0.960 to 0.991 |
| Markov, dwell 50 | 0.606 | 0.498 to 0.650 |
| Markov, dwell 80 | 0.107 | 0.075 to 0.121 |

**So scope D excludes**, all outcome-free (Q-108's 4.4 list, with the table's measure):
- sides constant past a quarter, never admitted, and most fair-coin persistence of 42 sessions or more;
- slowly switching sides: about two in five at a mean dwell of 50 sessions, and nine in ten at 80;
- sides dominated by one run (E >= 4), long-only and short-only designs;
- sparse designs, with fewer than about 25 to 30 non-tie traded sessions on the judged block, and designs balanced in
  most sessions;
- any family that does not make the E-035 (6) declaration;
- sides whose mean side exceeds b_D, the balance limit added to 4.4 (its share of each class model is in 4.4).

**Which of these exclusions no statistic could recover (corrected; the red team's M3, E-173).**
- **Persistence of about 55 sessions or more, and long Markov dwells** (80 sessions: about eight switches on the judged
  block): a flip null at 55 or 63 sessions has 11 to 13 sign units, so an exact null there cannot certify a level much
  below 2^-11 (Q-125's option 1). That exclusion is no power another statistic could recover.
- **42-session persistence and dwells near 50 sessions are recoverable.** A 42-session flip has 16 or 17 sign units, and
  A(42) is 0.04 to 0.09 of the levels (Q-108's section 1). On Q-108's calibration `cons_m1.5` in scope Q had a worst
  flip-42 ratio of 0.016 (`q108_choice.csv`). Under the first text's order, a scope-D choice left the scope-Q branch
  unvalidated, so such a family got no one-sample line at all, though one was within reach at about 19 % more MDL.
- **What an excluded family gets now** (2.5; B-25). A family declaring 42 to 50 sessions uses the second statistic if it
  HOLDS its validation, and otherwise has no one-sample line: the two-sample forms its pinned text declared before any
  read, or "not claimed". A family declaring 63 sessions or more has no one-sample line from either statistic.

**Reported for every candidate**, as Q-108's 5: MDL50 and MDL80 at k = 13, 15 and 20 on each toy, for `win1` and
`net3`, on Q-16's `cluster` at 1,000 trades, and P relative to `cons_m1.25`.

---

## 6. The runs (built first; then one heavy run each, under the lock)

### 6.1 The build (light)

**Code:** `extended/lift_one_sample2.py` (the grid; 2.4), `scripts/q126_calibrate.py`, `scripts/q126_validate.py`.

**Tests on synthetic data, all before any run** (the build seed 20263010; the validation build's 20263020):
- the grid's members equal `lift_one_sample`'s at m = 1.0, 1.25, 1.5, 1.75 and 2.0, and the margin multiplies the
  critical value only;
- the nesting in m (2.2) on planted samples, and the assertion refusing a planted violation;
- the sizing subsets' index order (j = 0 to 659, the core j < 23 identical to a core-only draw);
- the exact null index order (4.1) against hand-built cases;
- the probe: its ranking on planted exact sizes (the 23 largest per size, ties to the smaller j, the core excluded);
  its seeds and model indices; condition 4 refusing a planted count at the failure count and admitting one below it;
- the floor's zero tolerance: one bad subset among the 3,300 refuses, on planted tables;
- the drift generator equal to Appendix A's `draw` on the same generator, call for call;
- the rejecting-cells file: its rows sum, with their weights, to the null's exact count at k = 13; written only above
  a quarter of nominal; its k_max nested;
- the choice rule on planted size tables: the primary in scope D; the scope-Q branch as the second statistic when scope
  D chooses and as the primary when it does not; condition 1 over the sizing nulls at zero tolerance; condition 3 over
  the core only; condition 4; the cost lines;
- the criterion: Q-108's validation code's verdicts reproduced on planted tables, for each of two statistics;
- the seed map, the guard and the provenance assertion (4.1): the folded NAME + constant case, a bounded loop
  refused, an unbounded loop printed; every imported Q-108 construction called without a seed map refused; **the full
  entropy of every null** checked against 4.1's indices, the core's exact nulls included (n4); the manifest's seed map
  compared with 4.1's table parsed from the pinned plan, its sha256 checked (n5);
- the band check (2.5): the balance limit and the runs intervals against `band_b` and `band_interval` at 657 and
  1,006 sessions; the regime filter's four conditions against `regime_filter_check`, the red team's three gamed sides
  refused and an honest filter passed; the red team's dominated side refused; a judged-block mismatch "not claimed";
- the admission's balance limit (4.4): `admission_b` at 657 and the span's n; the exact cells' mean side against a
  direct count on hand-built cases; the procedure's counts with and without it on a planted dominated side;
- every test Q-108's build listed (its 6.1) that the reused functions carry, re-run.

**Reads,** exactly as Q-108's 6.1: P-16's pairs through `scripts/q16_p16_pairs.py`, the calendar through
`extended.reader.read_walks` (purpose `registered_design`, E-035, P-16), E-094 (2)'s count and sha256 asserted.
Development data only, to 2026-07-16. **Writes** only through `extended.results`; each runner refuses outside a clean
run.

### 6.2 The calibration run

- **When:** one heavy run from a clean checkout of the commit carrying the pinned plan and the merged build, under
  `run.lock`, watched to its exit.
- **Size:** 35,063 nulls in the rule -- 33,020 exact and 2,043 Monte Carlo at 200,000 replications -- and 84 + 6,000
  beside. The eight candidates on shared draws, in both scopes.
- **The parts (after the look, B-27; the red team's m2),** in this order, all under the one lock and from the same
  clean commit:
  1. the pairs step and the core (Q-108's class);
  2. to 6. the sizing subsets, one part per size z (each a deterministic function of (z, j) and the seeds);
  7. the probe (it needs parts 2 to 6's rankings);
  8. the drift beside;
  9. the choice.

  Each part writes its output with its own manifest (the commit, the seed map, the part) into the run's work folder.
  The choice reads every part's manifest and refuses a missing part, a different commit or a different seed map; it
  alone writes the result files, through `extended.results`.
- **A crash and a failed check are different things.** A part that exits non-zero with no failed check and no output
  -- a machine crash, a sleep, an update -- may be run again from scratch: its output is fixed by the commit and the
  seeds, so a second run cannot be a search. **A failed check** -- the nesting assertion, a scalar mismatch, the
  provenance assertion, a count refused -- is never rerun; it is diagnosed under the failure protocol.
- **Three further rules (the red team's m2).**
  - **A crash from a code defect** needs a new commit, and the choice refuses parts of another commit, so every part
    reruns at the fixed commit. Each part that had finished must then reproduce its earlier output byte for byte:
    **each data file it wrote has the same sha256 as before**, and its manifests differ only in their commit, time and
    host fields, which the auditor lists (the red team's m-1). Otherwise the run stops. The fix's diff is confined to
    the defect, and the auditor reads it.
  - **All or none.** Every part writes all its output or none: a partial work folder is deleted and counts as no
    output. The choice writes all its result files or none; a partial write to `results/` is a failed run, diagnosed.
  - **The environment.** The choice also refuses a part whose recorded package versions (in its manifest) differ from
    the others'.
- **Time, as estimates; the lock's hours are set from the build's measurement.** Each figure is printed by
  `q126_arith.py` from Q-108's two logs, the low end from the validation log and the high end from the calibration
  log, means throughout. **The low end is a floor for two candidates, not an estimate for this plan's eight** (the red
  team's m4); scaled linearly in the candidate count, each part's estimate at eight is given after it:
  - **the core:** 3.6 to 4.6 hours, the two Q-108 runs' `EXIT 0` lines (12975 s and 16435 s); at eight, 4.3 hours;
  - **the sizing subsets:** 3,185 subsets x 2 values at 4.62 to 10.29 s a subset-value: **8.2 to 18.2 hours**; at
    eight, 15.7 hours. L = 42 is most of it;
  - **the probe:** 920 Monte Carlo nulls at 8.26 to 9.40 s each: 2.1 to 2.4 hours; at eight, 2.3 hours;
  - **the drift beside:** 1,200 populations at the five exact models: 1.5 to 3.4 hours; at eight, 3.0 hours;
  - **in all: 15.4 to 28.6 hours; at eight candidates, about 25.3 hours.**
  - The note's per-enumeration timing at L = 63, 0.2 to 0.4 s a subset (Q-125, section 4), agrees with the logs.
- **Memory:** Q-108's per-null working set stayed at or below 223 MB and its pairs step peaked at 399 MB (the
  calibration log); `--mem-gb 1.5`, as Q-108.
- **Writes:** `q126_cal_size.csv` (every null x candidate x scope x level, and each construction's spread across its
  subsets, per size and pooled); `q126_cal_power.csv`; `q126_cal_cells.csv`; `q126_choice.csv`.

### 6.3 The validation run

- **When:** after a decision row records the choice from `q126_choice.csv`, with no hand choice. One heavy run.
- **Size:** the 2,293 nulls of Q-108's class on the validation seeds, 84 + 6,000 beside, each chosen statistic or
  procedure, and `cons` in scope Q beside.
- **Time:** about Q-108's validation run (its log's `EXIT 0` line, above), plus the drift beside. The same parts and
  crash rule as 6.2, without the sizing parts and the probe.
- **Memory:** as 6.2.
- **Writes:** `q126_val_size.csv`, `q126_val_power.csv`, `q126_val_cells.csv` and `q126_val_criterion.csv`. The
  criterion prints `HOLDS | FAILS | NOT CHECKED` for each chosen statistic.

### 6.4 Both runs

Each is watched to its exit. A failed run is kept and diagnosed by the failure protocol. Nothing is rerun to pass; a
crash is rerun only as 6.2 says.

---

## 7. What follows from each outcome

1. **NONE at the choice.** The trades-first one-sample line stays unavailable. The validation block is retired, never
   drawn. Families use the two-sample forms with K0 (Q-108's 7 item 3); family B and the resting-levels re-draft stay
   parked on their C1.
2. **A chosen statistic FAILS its validation.** Its rows of 2.5 have no one-sample line. Nothing is re-chosen, nothing
   is rerun, and no construction is dropped. The other statistic, if it HOLDS, is adopted for its own rows only
   (B-30). If the primary fails, the line is unavailable for every row but the second statistic's.
3. **No third plan without the lead's decision (B-19).** This is the second plan on one line after a failure (Q-108
   answered Q-83's, E-094; this answers Q-108's). Under the failure protocol's two corrective cycles a third is the
   lead's decision, and DIRECTIVE Part 5 step 3 marks the item `NEEDS_OPERATOR` on the board (the red team's n2).
4. **A chosen statistic HOLDS.**
   - A row adopts it as a one-sample line, in `extended/lift_one_sample2.py`, its blob pinned by that row, with its
     rows of 2.5.
   - Families may declare C1 on it within those rows; their K0 checks run on it (Q-108's 7 item 5).
   - **The primary in scope D** exists only for cells admitted by 4.4. A cell not admitted is "not claimed", unless its
     pinned text declared a two-sample line for it before any read.
   - **The scope-Q statistic**, primary or second, needs no admission, but persistence past a quarter is in no row
     (Q-108's 7 item 6).
   - The adoption row reports the drift nulls beside (3.3).
5. **The calibrated range is k = 13..20.** A family numbered beyond 20 needs it extended under its own row.

---

## 8. Disclosures

- **Everything new here was chosen after Q-108's look** (Appendix B). That is why the choice is made on new calibration
  seeds and validated on other new seeds, by rules written here before either run. **The exact part's assurance is the
  calibration's 3,300 subsets, not the validation's 115** (4.3; the red team's n1).
- **What is known in advance about scope D (B-1).** On Q-108's validation draws, beside and deciding nothing,
  `cons_m1.25` in scope D had no failing null (E-160 lists it as exposed and not taken; Q-125's option 1). That
  knowledge motivated trying scope D first. Those draws are never reused (4.1's provenance assertion), and this plan's
  draws are new, so the knowledge cannot select on them. But the choice of scope is not blind, and is labelled.
- **The fixed-data streams are fresh for no one** (Q-108's n1). Their exact nulls are deterministic: for a candidate
  Q-108 ran, its fixed-stream exact sizes here equal those in `q108_cal_size.csv`. The fresh tests are the subsets and
  the synthetic draws.
- **One population** (Q-108's n2). Every subset in both runs comes from P-16's judged offers. The drift nulls are the
  only populations from elsewhere, and they are beside.
- **P-16's judged pairs have been read before** as a source of null dependence (Q-108's 8); no family's outcome is read
  by either run. The cells files (4.5) carry signs derived from them.
- **The drift sizes are invented** (Q-125, section 3.2); they are not estimates of any market's.
- **The residual risk** is the Monte Carlo lottery outside the probed tail: the probe ranks subsets by their exact
  sizes, and a subset bad only on the Monte Carlo side, with an unremarkable exact size, is not probed. C6's tail is
  probed by proxy only, its ranking statistic not dominating it (the red team's n1). The band check's residual --
  fixed regimes a switching side's runs cannot separate, Markov sides beyond dwell 80, long regimes with edge
  reversals -- is in 2.5; dominated sides are closed by the balance limit, in 2.5 and 4.4. **The balance limit is a
  marginal envelope, not a joint one** (the red team's V-4, a stated residual): a side just under the limit with many
  runs -- long on about 83 % of sessions, its reversals evenly spread -- is admitted. Such sides are rare among the
  class's admitted sides; the intermediate case rests on the procedure's calibration, the red team's experiment not
  run (E-184, E-186).

---

## 9. What this plan does not do (after the look, B-18; E-161's list and Q-125's section 4)

| option | why not |
|---|---|
| a session floor (a minimum of traded sessions) | the failing subset had the most traded sessions of its size (Q-125, H-a); a floor buys no size here and costs sparse designs |
| CR2/CR3 or a wild cluster bootstrap in place of a margin | they correct the variance, not the randomisation atom (Q-125, option 5); C6 is kept as one candidate only because Q-108's calibration found it eligible |
| an exact sign-flip test | no attainable p below 2^-10 at 63-session blocks (Q-108's 2.3; Q-125, option 6) |
| a narrowed k range (k >= 19) | a range chosen after the look (E-160's F2 (a)) |
| the averaged (`flat`) size deciding | a weakening after the look (Q-108's 3.4; E-105 (1)) |
| dropping `win1`, flip63 or any side model | Q-108's 7 item 4 |
| enlarging the validation | it would enlarge the exposure the calibration must match; the validation stays Q-108's class (B-14) |
| reading P-16's per-quarter drift directly | an outcome read (Q-125, section 6 item 1); the drift nulls carry a drift as a declared construction instead. The cells files carry its signs only, coarsely, and are read only after the verdict (4.5) |
| an allowance of bad subsets in the floor (E-173's c = 3) | declared in the second text, reversed by E-176 and kept reversed by E-182 on the floor's basis as the line's guarantee of size: it certifies less and raises the rule's bound, and no larger calibration brings its nested bound to the first text's (3.2's figures; 4.3's comparison) |
| the two-sample forms' MDL against the one-sample line | not needed under E-182's basis, which rests on size, not on an end-to-end power comparison (the red team's re-read, what it could not check) |

---

## 10. The red team's findings and what changed

### 10.1 The first read (of ec6905a; `docs/reviews/DRAFT_Q-126_2026-11-17.md`; E-173, E-176)

| finding | change (and where it now stands) |
|---|---|
| M1 (the Monte Carlo lottery in scope D) | the lead took (a) and (b) together: the 23 largest-exact-size sizing subsets at each size carry the four persistent Monte Carlo models, and condition 4 refuses a candidate if any probed null reaches its failure count; its power shown (3.2, 4.2, 4.3; B-22, B-23, B-24, B-29); section 1 and the residual in 8 restated; its "no stricter" framing withdrawn in the fourth text (10.2, M-B) |
| M2 (the sized floor's power) | **answered by the power table; the allowance reversed.** The floor's admission table beside the validation's pass, the comparison of c = 0 to 3 with their refusals and bounds, and the grid-step MDL costs are a declared reading (4.3). The second text declared E-173's allowance; E-176 reversed it, and E-182 keeps zero tolerance on a corrected basis -- the floor as the line's guarantee of size over rare configurations, E-176's grid-step and "fewer profitable models" arguments withdrawn (3.2, 4.2, 4.3; B-21) |
| M3 (coverage) | the impossibility restricted to about 55 sessions and more and long dwells; the 42-session and dwell-50 band served by the scope-Q branch's choice, validated beside as a second statistic and adopted for that band only; the statistic a family uses fixed by its declared persistence (2.5, 4.2, 4.3, 5, 7; B-25, B-30) |
| M4 (Q-108's retired seeds through imported defaults) | the provenance assertion before any draw, with its build test, naming `null_plan` and `expected_counts` (4.1, 6.1; B-28) |
| m1 | the two parts positively associated; the product a lower bound (4.3) |
| m2 | the run's declared parts under one lock, and the crash rule (6.2, 6.3; B-27) |
| m3 | every cost figure printed by the script from the logs and held by T-0 when they are present (6.2) |
| m4 | L = 42 added to the drift nulls; their scope-D emptiness at L = 55 and 63, and the replica's, stated (1, 3.3; B-26) |
| m5 | the per-size bound 3/660 (3.2) |
| m6 | the cells files' signs reconciled with section 9 (4.5, 9) |
| n1 | the exact part's assurance stated as the calibration's (4.3, 8) |
| n2 | DIRECTIVE's `NEEDS_OPERATOR` cited beside the lead's decision (7) |
| n3 | a reading; cited at the scalar re-decision (4.1) |
| n4 | a reading; the build extends T-0's declared uses (4.1) |
| n5 | a reading for the adoption row, not this plan |

### 10.2 The re-read (of the diff ec6905a..4b31805; `docs/reviews/DRAFT_Q-126_v3_2026-11-17.md`; E-182)

| finding | change (and where it now stands) |
|---|---|
| M-A (T-0 after Q-128) | T-0 reads the look-ahead file at ec6905a by `git show`; 4.1's citation and its sentence on T-0 say so; T-0 re-run on the branch with master merged (4.1) |
| M-B (the probe is stricter than the validation) | the "no stricter" sentences struck; condition 4 kept on the floor's basis; its refusal at the tail rate where the validation passes a candidate 19 times in 20 stated and held by T-0 in place of the assertion that could not fail (3.2, 4.3; B-29) |
| M-C (E-176's basis) | zero tolerance kept on E-182's basis, the floor as the line's main guarantee of size, with both upper limits; E-176's two claims withdrawn; "bound" where a figure is a worst case; the floor's chance of emptying a branch a declared reading, on the red team's profiles and a flat rate; the two-sample experiment not run (3.2, 4.2, 4.3, 9; B-21) |
| M-D (the declared persistence unchecked) | the outcome-free band check on R, on the choice block before the pin and on the judged block in stage C, a mismatch "not claimed"; a family's k unchanged (2.5, 6.1; B-31) |
| m1 | 2.5's basis corrected: the dwell-50 admitted share and run count, section 5's table cited (2.5) |
| m2 | the crash rule's three additions: byte-identical reproduction after a code fix, all-or-none writes, the package-version check (6.2; B-27) |
| m3 | sections 9 and 10 cite figures instead of repeating them, and T-0 checks that they carry none; the probe's model list held (9, 10) |
| m4 | the cost's low end named a two-candidate floor; the scaled estimate at eight candidates added (6.2) |
| n1 | the ranking's wording; C6's weaker cover in 8 (3.2, 8) |
| n2 | the pooling's c = 0 scope stated (3.2) |
| n3 | a family's k unchanged, in 2.5 |
| n4, n5 | the build's requirements: the full entropy checked, the seed map against the pinned file (4.1, 6.1) |

### 10.3 The last read (of the fourth text, 0772de0; `docs/reviews/DRAFT_Q-126_v4_2026-11-17.md`; E-184)

| finding | change (and where it now stands) |
|---|---|
| F-1 (R counts switches, not persistence) | a balance limit on the mean side, by a declared quantile rule over the band's class models, in the band check and, before any run, in 4.4's admission; its coverage cost on the class stated; the red team's experiment not run (2.5, 4.4, 5, 6.1; B-32) |
| F-2 (the band check's intervals) | each declared kind checked by its own model: a regime filter by its decision points and the balance limit, a switching side by the Markov runs interval and the balance limit; the in-band refusal of the band's own models printed and held, at most the rule's; the unit comparison corrected; the unsupported figure replaced (2.5; B-33) |
| F-3 (the residual) | restated from printed figures: fixed regimes per band and span, Markov sides beyond dwell 80, dominated sides closed, edge reversals (2.5, 8) |
| m-1 | "byte for byte" is each data file's sha256 (6.2) |
| m-2 | the rule of three's figure labelled as its approximation (3.2) |
| m-3 | a choice-block mismatch may be re-declared before the pin, recorded in the pinning row (2.5) |
| m-4 | the stray heading removed |
| n-1 | T-0 names the search's commit in full |
| n-2 | T-0's check that sections 9 and 10 cite widened to scientific notation, short decimals and percentages |
| n-3, n-4 | readings, in 3.2 and 2.5 |

### 10.4 The light read (of the fifth text, 20e03c4; `docs/reviews/DRAFT_Q-126_v5_2026-11-17.md`; E-186)

| finding | change (and where it now stands) |
|---|---|
| V-1 (the regime-filter test gamed by unused or crowded points) | a spacing rule and a one-sided runs floor added; the in-band refusal printed and held; the residual's two regime-filter sentences struck and the residual restated; the three gamed sides refused, held by T-0 (2.5, 6.1; B-33) |
| V-2 | a reading: n is the span's session count; the refusals are for the dense case, sparse trading costing power, not size (2.5) |
| V-3 | 4.4's coverage cost reworded as a share of all sides in the dense case, the admitted share beside (4.4) |
| V-4 | a stated residual in 8, no experiment |
| V-5 | the second column's effective limits printed in 2.5 |

---

## Appendix A: the drift nulls' generator (Q-125's Appendix A `draw`, verbatim)

It is called with `rng = np.random.default_rng([s, c, r])`, s the run's drift seed (4.1), c the scenario's index and r
the population, and `n = 657`:

```python
def draw(rng, z, T, d, varying):
    N = np.zeros(n)
    w = np.zeros(n); tr = rng.choice(n, T, replace=False); w[tr] = rng.gamma(2.0, 1.0, T)
    N = rng.multinomial(z, w / w.sum()).astype(float)
    q = np.arange(n) // 63
    dq = d * (rng.choice([-1.0, 1.0], q.max() + 1)[q] if varying else np.ones(n))
    V = np.zeros(n)
    for j in np.flatnonzero(N):
        k = int(N[j]); u = rng.random(k)
        V[j] = 0.5 * ((u < 0.25 + dq[j]).sum() - ((u >= 0.25 + dq[j]) & (u < 0.5)).sum())
    return V, N
```

`V` and `N` are the population's session sums and counts. The side models of 3.3 are applied to them exactly as to a
real subset's, with every candidate in both scopes.

---

## Appendix B: the choices made after Q-108's look

| # | choice | where | basis |
|---|---|---|---|
| 1 | scope D first, the scope-Q branch second (Q-108 had Q first) | 2.2, 4.2 | Q-125's ranking (option 1 first); E-161; the knowledge disclosed in 8 |
| 2 | the candidates: the `cons` margin grid and C6; C5, C7, C8 and C9 dropped | 2.2, 2.3 | the brief; each dropped one failed the floors in both scopes at Q-108's calibration |
| 3 | the grid 1.0, 1.125, 1.25, 1.375, 1.5, 1.75, 2.0, the two new margins for resolution | 2.2 | Q-125's option 3 ("likely 1.25 or less"); the brief's range 1.0 to 2.0 |
| 4 | the scope-Q branch only at m >= 1.5 | 2.2 | Q-125's H-b; E-161 |
| 5 | C6 in scope D only | 2.2 | its margin is below the branch's |
| 6 | the sizing rule (rule of three, 0.9 and 0.95) and 660 subsets a size, all in condition 1 | 3.2, 4.2 | Q-125, section 2.2 and option 2; E-161 |
| 7 | the sizing subsets carry the exact models, and the probe only | 3.2 | cost; the probe (B-22) covers the Monte Carlo tail |
| 8 | condition 3 kept on the core only, not the sizing nulls | 4.2 | a stricter, unpriced condition would be a choice after the look; condition 1 carries the sizing |
| 9 | the drift nulls beside: Appendix A's eight scenarios, 150 populations | 3.3 | the brief; Q-125's replica; E-161 ruled them beside |
| 10 | the rejecting-cells files above a quarter of nominal | 4.5 | the brief; Q-125, section 6 item 3 |
| 11 | the scalar re-decision on the sizing nulls cut to 5 cells, no uniform cells | 4.1 | cost; the red team's n3 |
| 12 | new seed blocks; Q-108's retired | 4.1 | Q-108's 7 item 4; E-159 |
| 13 | a new module for the grid; `lift_one_sample.py` untouched | 2.4 | keeps Q-108's result files on their code |
| 14 | the validation's exposure kept at Q-108's class | 3.5, 9 | E-052's criterion unchanged; a finite sizing |
| 15 | every candidate in both scopes, the pairs outside the rule beside | 2.2 | information at no extra enumeration |
| 16 | the criterion's power stated, the criterion unchanged | 4.3 | the brief; the operator's rule on strict lines |
| 17 | the nesting in m asserted | 4.2 | it carries the bound of 4.3 |
| 18 | the options of section 9 not taken | 9 | E-161; Q-125, section 4 |
| 19 | no third plan without the lead's decision; `NEEDS_OPERATOR` on the board | 7 | the failure protocol's two corrective cycles; DIRECTIVE Part 5 step 3 |
| 20 | the drift sizes are the replica's invented ones | 3.3 | Q-125, section 3.2 |
| 21 | the floor at zero tolerance, stricter than the validation on purpose; E-173's allowance, the c = 0 to 3 comparison and the floor's chance of emptying a branch kept beside as readings | 3.2, 4.2, 4.3 | the red team's M2 and M-C; E-176's reversal of E-173, kept by E-182 on a corrected basis: the floor is the line's main guarantee of size over rare configurations (E-176's arguments withdrawn) |
| 22 | the Monte Carlo probe of the sizing tail, and condition 4 on it | 3.2, 4.2, 4.3 | the red team's M1 (a) and (b); the lead's ruling (E-173) |
| 23 | the probe's ranking: `cons` in scope Q, summed over both values and the flips at 42, 55 and 63, at k = 13 | 3.2 | the red team's M1 (a): a ranking free of the candidates in the rule |
| 24 | the probe's seed takes the calibration block's spare role | 4.1 | a new role needs a seed of the block; the block had one spare |
| 25 | the second statistic and the persistence rows of 2.5 | 2.2, 2.5, 4.2, 5 | the red team's M3; the lead's ruling (E-173) |
| 26 | L = 42 added to the drift nulls | 3.3 | the red team's m4 |
| 27 | the run's declared parts under one lock, and the crash rule with byte-identical reproduction, all-or-none writes and the package-version check | 6.2 | the red team's m2 (both reads) |
| 28 | the seed-provenance assertion | 2.4, 4.1 | the red team's M4; the lead's ruling (E-173) |
| 29 | the probed nulls judged by condition 4 only, not in P_MC or the point-rate floor; the probe strict on the floor's basis | 3.2, 4.3 | P_MC models the core nulls' validation counterparts and the probe is a tail search; E-182 (the red team's M-B) |
| 30 | each statistic judged on its own verdict; neither extended to the other's rows | 4.3, 7 | E-094 (3) (a) applies the criterion per statistic; no switch after a read |
| 31 | the band check, from sides only, on the choice block before the pin and on the judged block in stage C; a judged mismatch "not claimed"; a choice-block mismatch re-declared before the pin, recorded | 2.5, 6.1 | the red team's M-D and m-3; E-182, E-184 |
| 32 | the balance limit (the mean side at most b, the largest 97.5 % quantile over the band's flip and Markov models), in the band check and in 4.4's admission | 2.5, 4.4, 5 | the red team's F-1; E-184, adopted by design, the red team's experiment not run |
| 33 | each declared kind checked by its own model (a regime filter by its decision points, their spacing in the band and a one-sided runs floor; a switching side by the Markov runs interval with 1.25 % tails and the two-quarters floor only where it keeps the rule); no in-band model refused with more than 0.05 | 2.5 | the red team's F-2 and V-1; E-184, E-186 |
