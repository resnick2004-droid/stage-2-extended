# Q-108: the one-sample pass line's re-calibration -- the plan, declared before anything is built or run

**Status: a plan, third text.** It answers:
- the red team's first read (`docs/reviews/Q-108_plan_2026-11-16.md`, on the first text f3e5768) and the lead's
  rulings on it (E-105);
- the red team's re-read (`docs/reviews/Q-108_plan_v2_2026-11-16.md`, on the second text 490b663) and the lead's
  rulings on that (E-110).

It goes to the red team's read of this diff, then is pinned by its LF sha256 under a decision row. Section 9 maps
every finding of both reads to its change.

Nothing in it has been built or run, and it holds no result:
- The arithmetic of sections 1, 3 and 4 uses only declared constants -- the judged block's 657 sessions, the family
  levels 0.05/(k(k+1)) and 200,000 replications. It is printed by `docs/calibration/scripts/q108/q108_arith.py`, which
  draws no random number.
- Three scratch synthetic checks informed sections 3.1, 4.4 and 6, and are committed beside it:
  - `q108_scratch_autocorr.py` (seed 10810801);
  - `q108_scratch_runs.py` (seed 10810802);
  - `q108_scratch_exact_timing.py` (seed 10810803).
  Their seeds are outside the program's 2026 space. They are described, not quoted.
- Q-83's figures are cited by file and section, never retyped.

**Why** (E-091, E-094 (1), (3) (e); the audit `docs/audits/Q-83_fresh_seed_validation_2026-11-16.md`):
- Q-83 found the one-sample `cons` (`extended.lift_bound.bound`, the statistic of C1's lift over the coin twin) above
  nominal on one real null: P-16's pairs thinned afresh to 5,000 trades, the 1R win value, signs flipped in 63-session
  blocks (the audit, section 3.1).
- The two-sample forms held.
- The audit's diagnosis is M2's selection-on-draws effect, through the thinned subsets. With 63-session flips a
  replication spans eleven or twelve sign blocks, so one sign pattern carries a probability of the order of the family
  levels, and the size there depends on which trades were drawn (the audit, section 3.3).
- The trades-first one-sample line (E-008) has no statistic that holds its level. This plan declares how one is to be
  chosen, and validated on seeds it was not chosen on.

---

## 1. What the diagnosis implies: a necessary bound, not a safety bound (arithmetic, no data)

**The null.** It is Q-16's sign-flip construction, `scripts/q16_calibrate.py` `_flip_signs`. On n = 657 sessions with
flip blocks of L sessions at a uniform random phase p in 0..L-1, the sessions touch B(p) = floor((656 + p)/L) -
floor(p/L) + 1 blocks.

**What a test with power must reject.**
- The **aligned pattern**: every block's sign agrees with the sign of its own block sum. On it a sample looks like a
  lift that is positive in every block.
- The **near-aligned patterns**, which a test with power also rejects: the aligned pattern with one block's sign
  reversed (B of them), with two reversed, and so on.

So a test that rejects the aligned pattern at every phase has, on this null, a size of at least
A(L) = (1/L) sum_p 2^-B(p). One that also rejects every single-block reversal has at least
H1(L) = (1/L) sum_p (1 + B(p)) 2^-B(p). One that also rejects the two-block reversals has at least H2(L).

**These are necessary, not sufficient.** Any test that rejects those patterns has at least that size. **No
persistence is shown safe by this arithmetic.**

| L | blocks touched, by phase | A(L) / level, k = 13 to 20 | H1(L) / level, k = 13 to 20 |
|---|---|---|---|
| 21 | 32 at 16 phases, 33 at 5 | negligible | negligible |
| 42 | 16 at 16 phases, 17 at 26 | 0.04 to 0.09 | **0.67 to 1.54** (1.00 at k = 16) |
| 55 | 12 at 4 phases, 13 at 51 | 0.48 to **1.10** (above 1 at k = 20 only) | 6.6 to 15.3 |
| 63 | 11 at 37 phases, 12 at 26 | **1.41 to 3.26** | 17 to 40 |

At L = 42, adding the two-block reversals gives 5.5 to 12.8 times the level (H2).

**The conditions (m1).** The bound binds a test only if it rejects those patterns:
- **at every block scale it reads.** The 63-session member needs the quarters' sums to be of even size: its t is then
  about sqrt(G) divided by their coefficient of variation. `t21w` and `t42w` need evenness at their own, finer scales.
- **at nearly every phase.** At k = 13, A(63) is above the level by 41 %, so the test must reject on more than about
  71 % of the phase-weighted aligned mass. At k = 20 it must reject on more than about 31 %.
- **Edge blocks.** Six of the 26 twelve-block phases at L = 63 have an edge flip block of 1 to 3 sessions, which is
  no real decision. Counting those as eleven blocks gives the effective A_eff(63), 1.50 to 3.45 times the levels at
  k = 13 to 20.

**What follows.**
- **At L = 63 a per-subset level is unattainable without a margin or an admission rule.** On every thinned subset
  whose quarter sums are even enough, a test with power against a quarter-consistent lift has at least A(63), which is
  above every level from k = 13 to 20. The audit's failing rate (its section 3.3) is of exactly this order.
- **At L = 55 the same holds at k = 20**, and within half a percent of the level at k = 19.
- **At L = 42 and below, the arithmetic shows no safety.** The near-aligned patterns already reach the levels at
  k >= 16. Whether a statistic holds there is what the calibration and the validation show, and nothing else.

**Hence two scopes**, calibrated on the same nulls (section 4):
- **scope Q**, the statistic alone;
- **scope D**, the statistic preceded by an outcome-free admission check on the cell's own sides, calibrated and
  validated as a procedure.

The choice tries scope Q first.

---

## 2. The candidate statistics (none chosen yet)

### 2.1 The common setting

- **What is tested.** The per-trade pair difference x_i = (outcome(rule side) - outcome(mirror)) / 2 at the same
  bracket, as in `extended/lift_bound.py`, summed per session of the judged calendar:
  - S_j and N_j, the sum and the count of session j, every session counted;
  - n = 657 sessions, A1's stored days 2024-01-02..2026-07-16. Their count and their sha256 are recorded in E-094 (2),
    and every runner asserts both.
- **Blocks.** b-session blocks are `lift_bound.block_index(657, b)`. G' is the number of non-empty blocks.
- **Levels (MATERIAL 5).**
  - One-sided, at 0.05/(k(k+1)) for **k = 13..20**, in the new module's own constant `lift_one_sample.K_RANGE_1S`.
  - `lift_bound.K_RANGE` is untouched.
  - Why k = 13 first: k = 11 retired with F-02 (E-094 (3) (b)), and k = 12 is F-03's, which decides by two-sample
    forms. So the next one-sample family is k = 13 or later, and section 1's bound worsens with k.
  - Also at 0.001, 0.005, 0.01 and 0.025, reported beside.
- **Minimum detectable lift.** MDL is the smallest lift added to every trade that the statistic rejects, per
  replication.
- **Where the code goes.** Every candidate is built in a new module, `extended/lift_one_sample.py`, which imports
  `lift_bound`'s functions.
  - `lift_bound.py` keeps its blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2`, which F-03 pins.
  - Each candidate has a vectorised form, used by the calibration, and a scalar form, the one a family calls.
  - The scalar forms re-decide every rejection counted at a family level on Monte Carlo nulls, as in Q-82, and a
    declared seeded sample of patterns on exactly enumerated nulls (section 4.1).

### 2.2 The candidates

| id | name | definition | argued from |
|---|---|---|---|
| C0 | `cons` | the shipped statistic: `t21w`, `t42w` and `t63w` (CR1 variance, t with df G' - 1) all reject | the reference. **Eligible in scope D only**: it failed E-052's criterion on Q-16's class (E-091), which scope Q contains |
| C1-C4 | `cons_m` with **m = 1.25, 1.5, 1.75, 2** (E-105 (2)) | each member's critical value multiplied by m: reject if est - m t(1 - a; G' - 1) se > 0 | **a margin.** Section 1: the failure comes from aligned and near-aligned patterns that the members reject. A margin removes those whose t lies between the critical value and m times it; whether that is enough is what the calibration measures. Cost: every MDL scales by about m |
| C5 | `cons_bm` | each member with the CR2 variance and Bell-McCaffrey degrees of freedom (formulas below) | **few and unequal clusters.** A thinned subset of a few hundred trades, and any count-persistent stream (E-052 (1)), leaves blocks of very unequal weight. CR1 with G' - 1 df then understates the variance and overstates the df. CR2/BM is the standard small-cluster correction (Bell and McCaffrey 2002; Imbens and Kolesar 2016; Pustejovsky and Tipton 2018). It does not by itself remove section 1's bound |
| C6 | `cons_bm_m` with m = 1.25 | C5 with the margin of C1 | both of the above |
| C7 | `cons_im` | C0 together with `t63e`: the mean of the non-empty 63-session blocks' per-trade means, se = their sd / sqrt(G'), t with G' - 1 df (`lift_bound.t_stats(..., block=63, weight="equal")`); all four reject | **equal weights across quarters** (Ibragimov and Müller 2010). It removes a few heavy blocks' dominance of the trade-weighted mean. **The citation goes no further (n5):** Bakirov and Székely's conservatism is for independent normal group means, and on the flip null the group means are symmetric two-point mixtures whose blocks straddle flip blocks. Its exposure to the aligned pattern is the same as C0's |
| C8 | `sn` | the self-normalised statistic below | **no block length to choose.** Self-normalisation (Lobato 2001; Shao 2010) studentises by the partial sums' own path, robust to dependence of unknown strength. Its critical value is pivotal and is simulated once. The aligned pattern still gives a large T, so its size is measured, not assumed |
| C9 | `cons_sn` | C0 together with C8 (all four reject) | the intersection's logic of Q-16 (members failing on different nulls) with a member of a different kind |

**Ties** in the choice go to fewer members, then to the earlier row of this table.

#### The formulas (the build implements exactly these)

**C5's member at block b.**
- est = sum S / sum N. For each non-empty block g: u_g = BS_g - est BN_g, p_g = BN_g / N with N = sum N, and
  w_g = 1 / (1 - p_g).
- se^2 = sum_g w_g u_g^2 / N^2. The CR2 adjustment for a mean is (1 - p_g)^(-1/2) on each block's residual sum.
- df_BM = N^2 / [ sum_g BN_g^2 + (sum_g w_g BN_g^2 / N)^2 - sum_g w_g^2 BN_g^4 / N^2 ].
  - This is Bell and McCaffrey's (tr K)^2 / tr K^2 for the mean under a working model of independent trades.
  - It equals G' - 1 when the blocks have equal counts. The read re-derived it independently. The build's tests check
    both.
  - **The working model is a choice (m11).** With about 141 offers a session the session is the dependence unit, and
    Imbens and Kolesar recommend a cluster working model there. The trade-level model is chosen for its closed form.
    Its consequence -- the df that a few heavy blocks leave -- is what the calibration measures.
- The member rejects when est - t(1 - a; df_BM) se > 0, se > 0 and df_BM >= 1. A block holding every trade
  (p_g = 1) leaves the bound blank.

**C8.**
- T = sum_j S_j / sqrt( (1/n) sum_{t=1}^{n} U_t^2 ), with U_t = sum_{j <= t} (S_j - est N_j) and est = sum S / sum N,
  over all 657 sessions in calendar time (an empty session adds nothing).
- It rejects when T > c_a.
- **The reference c_a** is the ceil(a D)-th largest of T over D = 2,000,000 draws of 657 iid standard-normal session
  sums with N_j = 1. That is at least 200/a at every k up to 20.
  - All the levels come from one set of draws, seeded as in 4.1.
  - The table is written as a result file of the calibration run, and the choosing row pins it.
- **The reference is calendar-time (m10).** On sparse streams most sessions are empty, and their flat stretches of
  U_t change the functional the reference assumes. This is not corrected but measured: the 200-trade subsets, at about
  0.3 trades a session, are in the rule's nulls.
- MDL = (c_a sqrt((1/n) sum U_t^2) - sum S) / sum N, since adding a lift to every trade leaves the U_t unchanged.

**MDLs.**
- A t-type member's MDL is m crit se - est (m = 1 without a margin).
- An intersection's MDL is the largest of its members'.

### 2.3 Considered and excluded, with the argument (not run)

| idea | why excluded |
|---|---|
| dropping `t63w` (`t21w` with `t42w` only) | On the failing null all three members are lax, and the 63-session member most of all (the audit, section 3.2). The 21- and 42-session members are the ones Q-16 found lax when a side persists past their block (`docs/research/calibration_2026-11-15.md` 7.1). Dropping the strictest member can only raise the size |
| more, shorter blocks per member | More blocks bring more df but shorter blocks. Each member's validity needs blocks longer than the side's persistence, and shorter blocks are the lax ones on persistent sides (the note's Table 1) |
| `t126w` in place of `t63w` | Five blocks. The t critical value at df 4 is nearly twice df 9's at k = 13 (`q108_arith.py`), and its se is estimated from five blocks. Its MDL would be at least about twice C0's: the cost of a margin of 2, without that margin's exposure being any less measured |
| exact sign-flip (randomisation) tests | **63-session blocks:** with ten blocks the smallest attainable p is 2^-10, above every family level, so it has no power at all. **21- or 42-session blocks:** they are exact only when the side's sign blocks coincide with the test's blocks, which no rule guarantees. Calibrating a randomisation test at 200,000 null replications needs at least 20/a resamples each, beyond any run here. And sign symmetry is not the pass line's null: a long-leaning rule's lift can have mean zero without being symmetric |
| the studentised circular block bootstrap | Q-16 found it as lax as `t21w` on the dense persistent null (the note's Table 3), at a far larger cost |

---

## 3. The nulls

Every null is mean-zero by construction. All the candidates are computed on the same draws.

### 3.1 The side models (applied to real data: x_i = side x v_i, with v the pair difference of P-16's pairs)

| side model | how | computed |
|---|---|---|
| flips at L = 1, 5, 21 | Q-16's `_flip_signs`: a fair sign per L-session block at a random phase | Monte Carlo |
| **flips at L = 42, 55, 63** | the same; **L = 55 is new** | **exact**: every phase x every sign pattern |
| coin | the coin's own side, flipped by session (Q-16's `coin`) | Monte Carlo |
| **alternating at 45 and 55 (new)** | a side constant over L-session blocks at phase p, reversing at every boundary, starting long or short: 2L equally likely configurations. The convention is `_flip_signs`'s: session j is in block (j + p) // L, and "starting long" means long on block 0 and the side is (-1)^b on block b; starting short negates it | **exact** |
| **Markov switching, mean dwell D = 30, 50, 80 (new)** | a two-state side on sessions: a fair first side, then a reversal at each session boundary with probability 1/D; a fresh series every replication | Monte Carlo |

**Why these.**
- The flips are Q-16's class, plus the boundary L = 55.
- The alternating and Markov sides are the read's switch-timing models (M1, point 2). They have many more runs than
  fair-coin flips of the same persistence, so they are exactly what a runs-based admission could let through.
- Every side is a function of time only, never of an outcome.

**Exact.** On every exact model each candidate is a function of the test-block sums, which are linear in the pattern:
- BS_g = sum_f s_f M[f, g], where M[f, g] is v summed over flip block f intersected with test block g. BN_g is fixed.
- C8's sum of squared partial sums is a quadratic form in the pattern.
- C5's df depends on the counts only, which are fixed.

So the exact size is a sum over phases x patterns, each weighted by its probability: 63 x 2^12 at L = 63, 55 x 2^13
at L = 55, 42 x 2^17 at L = 42, and 2L at the alternating models.
- **An exact size has no interval.**
- **The pattern encoding (m6).** At phase p with B blocks, pattern q in 0..2^B - 1 gives flip block f the sign +1 when
  bit f of q, (q >> f) & 1, is set, and -1 when it is clear; block f is the sessions j with (j + p) // L = f.
  Cells are ordered phase-then-pattern: p ascending, then q ascending. An alternating model's cells are ordered by p
  ascending, starting long before starting short.
- The timing check (`q108_scratch_exact_timing.py`) puts one data set's three flip enumerations at seconds. It is a
  stand-in: it compares one margin and computes, but does not compare, the other members (the re-read, n2). The
  build's measurement sets the lock.

**The alternating models' granularity (m2).** Each has 2L equally likely configurations, so its exact size is 0 or at
least 1/(2L): 1/90 and 1/110, some 33 to 93 times the levels at k = 13..20 (`q108_arith.py`).
- So their floor and their criterion mean **no configuration rejects**. That is not a level comparison.
- The framing is coherent under fixed data: a no-skill regime filter at a random phase. The configurations are the
  flip null's two alternating patterns per phase, re-weighted from 2^-B each to one half.

### 3.2 The data each side model is applied to

- **Fixed-data streams.** `offered` and `taken`, as `scripts/q16_calibrate.py` builds them. They are the same trades
  as Q-16's, Q-55's and Q-83's: fresh for no one (n1).
- **Fresh thinned subsets (the declared family).** For each size z in 200, 500, 1,000, 2,000 and 5,000 trades, 23
  subsets of P-16's judged offers are drawn without replacement. Each subset carries every value and every side model
  that uses it.
  - The persistent side models -- flips at 21, 42, 55 and 63, both alternating models and the three Markov models --
    use all 23 subsets of each size: **115 subsets each**.
  - The flips at 1 and 5 and the coin use the first 5 of each size: 25 subsets each.
- **Values.** `win1` (win probability at 1R) and `net3` (net R at 3R).

**The number of subsets (MATERIAL 3 (iii)), by a detection requirement.**
- **Persistent side models: pooled over the five sizes, per side model (m1).** If 2 % of a model's subsets are bad --
  the statistic's size above nominal on that subset, at either value -- at least one bad subset is seen with
  probability at least 0.9. That needs ln(0.1)/ln(0.98) independent subsets, about 114, so 23 per size: 115, giving
  0.902 (`q108_arith.py`).
  - The requirement counts **subsets**, not subset-and-value pairs. The two values on one subset share its trades, so
    their badness is not independent.
  - **At a single size the figure is weaker.** 23 subsets see a 2 % rate with probability 0.37. The pooled guarantee
    amounts to seeing about a 10 % rate at any one size (0.91).
  - **Why the pooled unit.** Section 1's mechanism acts through the flips' block structure, which is the same at every
    size. A design has one size, but which one is not known when the statistic is chosen. Pooling gives a guarantee
    per persistence at a run the machine can hold. Section 4.2's exact-ratio condition then guards the boundary, where
    a miss at one size would bite.
- **The flips at 1 and 5 and the coin.** Each has at least 131 independent sign units on this block, so section 1's
  mechanism has no lever there. 25 subsets detect a 10 % bad-subset rate with probability 0.93.

### 3.3 Q-16's realistic synthetic nulls

- `iid`, `cluster`, `cluster_ar1`, `regime01` and `volclust` at 200 to 5,000 trades: **25 nulls**.
- They use `syn_batch` unchanged. The stress nulls are not run.
- Their sides reset daily, so in scope D they are always admitted.

### 3.4 Which size decides: the per-subset size (MATERIAL 3 (i); E-105 (1))

**The level must hold for each subset, not on average over subsets.**
- A judged cell's claim rests on its own trades, so the level must hold for the trade set actually judged, not on
  average over trade sets it might have had.
- E-052 judged Q-83's thinned nulls one subset at a time. Switching to the averaged reading after that failure would
  be a weakening chosen after seeing it.

So every subset is a null of its own in the rule and in the criterion.

**Section 1 makes this unattainable at L = 63, and at L = 55 at k = 20, for any test without a margin**, or, in scope
D, without an admission that keeps those sides out.

**The averaged form, beside, deciding nothing.** This is `extended/count_nulls.PROFILES["flat"]`: a fresh uniform
subset each replication, under flips at L = 21, 42 and 63, at every size and both values (30 nulls). It is reported
beside the per-subset spread, so the two readings can be compared.

### 3.5 The null set and its count

| part | nulls | computed |
|---|---|---|
| persistent side models x (2 fixed streams + 115 subsets) x 2 values | 9 x 117 x 2 = 2,106 | exact for flips at 42, 55, 63 and both alternating models (1,170); Monte Carlo for flips at 21 and the three Markov models (936) |
| flips at 1 and 5, coin x (2 + 25) x 2 | 3 x 27 x 2 = 162 | Monte Carlo |
| realistic synthetic | 25 | Monte Carlo |
| **in the rule and the criterion** | **2,293** | both scopes, on the same draws |
| beside: the count-persistent real one-sample nulls (Q-82's (ii) grid, `extended/count_nulls.py`) | 54 | Monte Carlo, **in both runs** (m12) |
| beside: the `flat` form (3.4) | 30 | Monte Carlo |

**Replications.**
- 200,000 a Monte Carlo null in the rule, in batches of 10,000.
- 100,000 for the nulls beside, which decide nothing.
- Exact nulls need none.

---

## 4. Seeds, the choice rule, the validation criterion, scope D

### 4.1 The seed blocks (as declared in the first text; verified unused)

Both blocks were checked with:
- a word-bounded search of every worktree's files, the main tree's working copy (the licensed data excluded) and every
  branch and remote (`git grep`);
- `git grep` over all commits reachable from them (284 at the first text; the read counted 287 by its own search).

None of 20262110-20262129 is named anywhere, and no written range covers them.

**Derived seeds (m2).** A literal search cannot see a seed computed as NAME + constant. I checked by hand, with an AST
scan of every `.py` of the tree, the vendored tree included, for an integer seed name plus constants and loop indices:
- the only derived range near the blocks is `tests/test_features_lookahead.py`'s `SEED_REPLACE + 1000 + i`, for
  i < 790. It starts three above the validation block's last seed and runs 790 seeds up from there;
- its three other expressions -- `SEED_REPLACE + i`, `+ 100 + i` and `+ 200 + i` -- run over the cuts (tens), four
  days and the fixed days, far below the blocks;
- nothing lands inside either block.

**Imported names plus an offset (the re-read's m4), checked by hand too**, since the guard does not fold them:
- this repository's: RD-01's runner writes `R.F.LADDER_SEED + i` (on wt-firms). The constant is the firms reading's
  first block seed, and i runs over a short literal sequence. RD-01's undeclared draws end below the calibration block
  (`docs/reviews/BUILD_RD-01_2026-11-16.md`);
- the vendored tree's:
  - `fh.SEED + 1`, `fh.SEED + 2` and `sc.SEED + 1`: Stage 2's `firm_h` and `im2_score` seeds plus one or two, far
    below the blocks;
  - `pe.SEED + 100,000 i + 1,000 j`: Stage 2's `planted_effect` seed plus multiples of 1,000, which never land in a
    block of twenty above it;
  - propsim's `a.seed + ...`: runtime arguments of Stage 1's frozen scripts, not run here;
- none lands in either block. (Seeds outside this plan's blocks are named here by role, not written.)

**The nearest seeds in use:**
- below: Stage 2's D-663 block and RD-01's undeclared draws, both ending a few seeds below the calibration block
  (`docs/reviews/BUILD_RD-01_2026-11-16.md`);
- above: that derived range, starting three above the validation block.

**The runners' guard (the re-read's MATERIAL 3)**, like Q-82's for its block, at the start of each run:
- **Refuses** a literal seed of either block, word-bounded, on any branch, remote or tag, or in the working tree,
  outside the allow-list. A document's mention outside `prereg/` is printed, not refused.
- **Refuses** an integer expression NAME + constants whose folded value lands in either block. It is constant-folded
  on the AST, NAME being an integer constant assigned in the same file.
- **A loop index.** It is bounded by its loop's literal extent where the AST shows one: `range` with constant bounds,
  or `enumerate` over a literal sequence (a list, tuple or string written out). The guard refuses if that bounded
  range reaches either block.
- **Where a loop index cannot be bounded**, the guard **prints** the expression, its file and line, and the reach it
  would need, for a hand check. **It never refuses on an assumed reach.**
  - The hand check is recorded in the allow-list with its reach and its reason.
  - At this text the list holds `tests/test_features_lookahead.py`'s three cut loops, with the reaches above.
- **Imported names are not folded.** A seed written as an imported constant plus an offset is in the hand check above,
  not in the guard.
- **The allow-list** names this plan, `docs/calibration/scripts/q108/`, the new module, the two runners and their tests,
  DECISIONS.md and the lead's records, and the hand-checked expressions.

**Calibration block, 20262110-20262119:**

| seed | use |
|---|---|
| 20262110 | the calibration build's tests |
| 20262111 | the fixed-data streams' Monte Carlo side draws: `default_rng([s, i])`, i the null's index |
| 20262112 | the thinned subsets: subset (z, j) by `default_rng([s, z_index, j])` |
| 20262113 | the subsets' Monte Carlo side draws: `default_rng([s, z_index, j, value_index, model_index])` |
| 20262114 | the realistic synthetic nulls, `default_rng([s, i])`, i the null's index in Q-16's list |
| 20262115 | C8's reference table: `default_rng([s, 0])`, its 2,000,000 draws in 200 batches of 10,000 drawn in turn |
| 20262116 | the count-persistent nulls beside (m12) |
| 20262117 | the `flat` form beside: its fresh subsets and flips |
| 20262118 | the exact nulls' seeded sample of patterns for the scalar re-decision: `default_rng([s, null index])` |
| 20262119 | spare, drawn by nothing |

**The indices (every order fixed, m6).**
- `z_index` 0..4 for 200, 500, 1,000, 2,000 and 5,000 trades.
- `j` 0..22.
- `value_index` 0 for `win1` and 1 for `net3`.
- `model_index` 0..11, in section 3.1's order: flips at 1, 5, 21, 42, 55 and 63, the coin, alternating 45 and 55,
  Markov 30, 50 and 80.
- **The fixed-data streams' Monte Carlo nulls:** i counts (stream, value, model) in that nesting, outermost first:
  - stream `offered` then `taken`;
  - value in `value_index` order;
  - the Monte Carlo models in `model_index` order: flips at 1, 5 and 21, the coin, Markov 30, 50 and 80.
  - So i = (stream x 2 + value_index) x 7 + the model's position among those seven, 0..27.
- **The `flat` form beside:** i counts (L, z_index, value_index) with L in 21, 42, 63, outermost first: 0..29.
- **The count-persistent nulls beside:** i is the null's position in Q-82's one-sample list (`scripts/q82_validation.py`
  `CP_ONE`): 0..53.
- **The exact nulls' null index**, for 20262118: their position when the exact nulls are listed by data (`offered`,
  `taken`, then the subsets by `z_index` and `j`), then value, then exact model (flips at 42, 55 and 63, alternating 45
  and 55), outermost first: 0..1,169.
- Within a null the batches draw in turn from its one generator, as Q-16's do.
- **The exact nulls' sample for the scalar re-decision.** It is drawn per candidate and per scope:
  - every cell that rejects at k = 13 -- in scope D, rejects and is admitted -- up to the first 100 in the cell order
    of 3.1;
  - plus 20 cells drawn uniformly from all the null's cells, the same 20 for every candidate.
  - Each sampled cell is re-decided at every k in 13..20. Rejections are nested in k, so k = 13 holds them all.

**Validation block, 20262120-20262129:**

| seed | use |
|---|---|
| 20262120 | the validation build's tests |
| 20262121 | as 20262111 |
| 20262122 | as 20262112 |
| 20262123 | as 20262113 |
| 20262124 | as 20262114 |
| 20262125 | the count-persistent nulls beside |
| 20262126 | the `flat` form beside |
| 20262127 | as 20262118 |
| 20262128-20262129 | spare, drawn by nothing |

C8's table is not redrawn: it is the statistic's definition, made by the calibration and pinned by the choosing row.
The validation block's index orders are the calibration block's.

E-052's two spare seeds stay undrawn.

### 4.2 The choice (calibration seeds only; coded in the calibration script and applied by it, never by hand)

**The level rule (MATERIAL 4 of both reads; E-105 (2), E-110).** A candidate is level-eligible in a scope when all
of these hold on its calibration results:
1. **the two floors:**
   - no Monte Carlo calibration null has its point rate above nominal at any k in 13..20;
   - no exactly enumerated calibration null has its exact size above nominal at any k. On the alternating models this
     means no configuration rejects (3.1);
2. **P_MC >= 0.9**: the Monte Carlo part's probability of holding (below);
3. **its worst exact ratio is at most 1/4.** The worst exact ratio is the largest, over every exactly enumerated
   calibration null (fresh subsets included) and every k in 13..20, of the exact size divided by nominal. On the
   alternating models any rejecting configuration gives a ratio far above 1/4 (3.1), so the condition again means no
   configuration rejects.

**P_MC, the Monte Carlo part's probability of holding** (renamed from the second text's "P(HOLDS)"; computed exactly,
with no randomness):
- It **treats each calibration null as standing for its validation counterpart.** For a Monte Carlo subset null that
  counterpart is a different, fresh subset, so P_MC does not see the subset lottery. That is condition 3's job, on the
  exact part, where the lottery bites.
- Each Monte Carlo null i's calibration counts c_{i,k} are read as rates p_{i,k} = c_{i,k} / 200,000.
- A statistic's rejections are nested across k, since a smaller level only raises the critical value. So the
  validation counts are modelled as X_13 ~ Binomial(200,000, p_13) and X_{k+1} | X_k ~ Binomial(X_k, p_{k+1} / p_k),
  zero once a rate is zero.
- **The script asserts the nesting (m6):** every candidate's counts on every Monte Carlo null, and its exact sizes on
  every exact null, are non-increasing in k. If one is not, the run stops with no choice, and the failure is
  diagnosed under the failure protocol.
- The null holds when X_k stays below 4.3's failure count at every k: 71, 63, 56, 50, 45, 41, 38 and 35 at
  k = 13..20 (`q108_arith.py`). Its probability is computed by dynamic programming over the counts, as that script
  does. The re-read checked the program against a simulation of E-052's test, count by count.
- P_MC is the product over the scope's Monte Carlo nulls. The exact nulls enter by conditions 1 and 3, not here.

**Why the worst exact ratio must be at most 1/4 (a chosen constant; E-110).**
- **The reason is the validation's verdict.** The validation draws 115 fresh subsets per persistent model and judges
  each one. The most powerful candidate that only just clears every calibration subset is the one most likely to
  carry a small, unseen bad-subset rate. Such a candidate fails validation with high probability.
- **A failure there is costly.** It is NONE with no re-choice (section 7), which closes the trades-first one-sample
  line until a new round.
- **Why 1/4.** The re-read's synthetic test (its section G, on three drifted synthetic populations, 115 calibration and
  115 validation subsets each) showed:
  - a fraction of 1/2 does not protect: it would have chosen a margin that then failed on the swapped halves;
  - 1/4 does protect, at a cost of about one grid step -- about a fifth more lift -- in two of its three cases.
- 1/4 is a chosen constant, not derived. Its cost is shown, under E-051, beside the choice (below).

**No power ceiling.** The first text's ceiling of 1.5 times C0 is dropped as a rule (E-105 (2)). **The choice is the
most powerful candidate meeting all three conditions:** the smallest P (section 5), scope Q before scope D.

**The order.**
1. **Scope Q:** C1..C9 on all 2,293 nulls, every replication counted.
2. **Scope D**, only if scope Q has none: C0..C9 on the same 2,293 nulls as a procedure (4.4).
   - A rejection counts only where the replication, or on an exact null the cell, is admitted.
   - The floors, P_MC and the worst exact ratio are all computed on the procedure's own counts and sizes.
3. **Otherwise none.**

**What the script prints and writes.**
- It prints `CHOSEN <name> (scope Q)`, `CHOSEN <name> (scope D)` or `NONE`.
- It writes to `q108_choice.csv`, for each candidate in both scopes: the floors, P_MC, the worst exact ratio (overall
  and per exact model, with the null and k that attain it), and P.
- **The cost of condition 3, shown beside the choice (E-051).** The script names the most powerful candidate refused
  by condition 3 alone, if there is one. Beside the chosen one it reports that candidate's P and its MDL50 and MDL80 at
  k = 13, 15 and 20.

### 4.3 The validation criterion (fixed now, as E-052's)

- The validation runner reads the choice from the calibration's result file, its manifest verified. Nothing is
  re-chosen.
- **The chosen statistic** (in scope D, the chosen procedure) **HOLDS** if, at every k in 13..20, on every one of the
  2,293 validation nulls -- the fresh subsets, the fixed-data streams and the fresh synthetic draws, all on the
  validation seeds:
  - a Monte Carlo null's 95 % Clopper-Pearson interval does not lie wholly above nominal. At 200,000 replications that
    means fewer rejections than 4.2's failure counts;
  - an exact null's exact size is at or below nominal. On the alternating models: no configuration rejects (3.1).
- It **FAILS** if any null breaks either condition. It is **NOT CHECKED** -- never a pass -- if any null is missing.
- **What the criterion demands** (binomial arithmetic, `q108_arith.py`):
  - a statistic at seven tenths of nominal on a Monte Carlo null fails it there by chance about once in ten thousand;
  - one exactly at nominal fails about once in twenty.
  - So over the many nulls it demands the conservatism the choice selected for.
- **Reported beside, never in the verdict:**
  - C0 on the same draws;
  - the count-persistent nulls;
  - the `flat` form;
  - the power on the validation toys.

### 4.4 Scope D: the admission and the procedure (MATERIAL 1 and 2 of both reads; m3, m7)

**The admission has three conditions.** A cell may decide C1 by a scope-D statistic only if:
1. **its family declares, under E-035 (6), before its pin, its side persistence below a quarter (63 sessions)**
   (restored; the re-read's MATERIAL 2);
2. **on the choice block**, at stage A, its sides pass the runs check below;
3. **on the judged block**, inside stage C and before any outcome is read, its sides pass the same check.

**The check.** It reads the cell's own sides only: its decisions, computed from bars before any outcome.
- **The series.** Each traded session's net side is the sum of its trades' sides, +1 long and -1 short. **Sessions
  with no trade, and sessions whose net side is zero (a tie), are dropped** (the re-read's MATERIAL 1, which withdraws
  its own earlier m9: a tie as a state of its own let a persistently long design through). What is left is the
  **non-tie series** m_j = sign(net side), in calendar order.
- **R** is the number of maximal runs of equal m_j in the non-tie series.
- **E**, the effective count, is (sum of run lengths)^2 / (sum of squared run lengths) over the same runs.
- **The check passes when R reaches its threshold and E >= 4.**
- **A series with a single side throughout the block is not admitted** (restored, explicitly; R >= 13 implies it).

**The thresholds, by arithmetic from the session counts (m7; the re-read's m3).** A side constant over 63-session
blocks touches at most floor((n - 1)/63) + 2 blocks on n sessions, so it has at most that many runs.
- **Judged block (n = 657): R >= 13**, one more than the most 63-session blocks there, 12.
- **Choice block: R >= floor((n_c - 1)/63) + 3**, where n_c is the number of sessions of **the span the family's
  stage A actually reads**. That span is unsealed. A family reading the whole choice block of 1,006 sessions has
  R >= 18; a family reading a shorter span, as F-03's stage A does from 2021-01-04, takes its own n_c. The family's
  runner asserts n_c.
- **E >= 4: no run holds more than half the non-tie sessions.** A run holding a share s of them gives E <= 1/s^2, so
  E >= 4 implies s <= 1/2. The floor is fixed by that arithmetic, not fitted.

**R, with the floor E >= 4 (M1 (d); the re-read's MATERIAL 2).**
- **Both bound the 63-session case alike.** E <= R <= the number of blocks, so the threshold that keeps every
  quarter-constant side out is the same for both.
- **E alone would be too strict.** In the scratch check (`q108_scratch_runs.py`), E is about seven tenths of R across
  persistences. At a threshold that excludes every 63-session side, E admits only about a third of 21-session
  fair-coin sides, which have 32 sign units and are not the failing class. R admits nine in ten of them.
- **R alone misses the dominated case.** A side long for most of the block with a dozen brief reversals has many runs
  but one dominant one. The Markov models cover moderately uneven runs; their admitted series never have a run much
  above half the sessions (the re-read, check H). **The floor E >= 4 keeps the dominated ones out.**
- **The floor costs nothing measurable** on the calibrated side models. In the scratch check, admission of fair-coin
  sides at every persistence is unchanged by it; the re-read found the same on its Markov models.

**Scope D is calibrated and validated as a procedure (M1 (a)).**
- **In every replication of every null -- every (phase, pattern) cell of an exact one -- R and E are computed from that
  replication's own non-tie side series, and a rejection counts only where both pass:**
  - the flip nulls: the flip signs;
  - the coin nulls: the coin times the flips, its ties dropped;
  - the alternating and Markov models: the side itself;
  - Q-16's synthetic nulls: always admitted, their sides being daily.
- **The class is all 2,293 nulls.**
  - The flips at 63 contribute what the admission lets through, which the arithmetic above makes nothing.
  - The flips at 55, the alternating models and the Markov models are where an admitted side can persist longest. The
    alternating 55 model is admitted at most phases, by its block count.
- **Only the judged-block check enters the calibration.** The declaration and the choice-block check come earlier
  and can only remove cells, so they cannot raise the procedure's size.
- **Why the procedure, not the statistic (n4).** P(admitted and rejects) <= P(rejects) on the cell's own side process.
  So the procedure's error is bounded wherever the procedure is calibrated for that process. A slow contrarian side may
  lean towards admission while a slow trend side leans away; the procedure's measured size covers both.

**At stage C (M1 (b), (c)).**
- **The judged read is a judged-block read under the seal.**
  - The family names a purpose for it on its pinned `Judged-block reads:` line, such as `stage_C_sides`, with no choice
    or fitting word in it.
  - It runs inside the stage-C clean run, is ledgered, and happens before any outcome is computed.
- **A cell whose judged check fails is "not claimed"**, as K0 withholds at stage C.
- A two-sample line decides such a cell only if the family's pinned text declared it as that cell's line before any
  read, with its k counted. No switch is made after the read.

**What it excludes (n3; the re-read's MATERIAL 1 and 2), all outcome-free:**
- sides constant past a quarter, which are never admitted;
- **sides dominated by one run**: a long-biased side with brief reversals, which E >= 4 keeps out;
- most longer fair-coin persistence: in the scratch check, sides persisting 42 sessions are rarely admitted, and
  21-session ones nearly always (`q108_scratch_runs.py`);
- **sparse designs.** With iid sides R is about half the non-tie sessions, so a design with fewer than about 25 to 30
  non-tie traded sessions on the judged block is mostly not admitted;
- **designs balanced in most sessions.** Their ties are dropped, so their non-tie series is short and R stays low;
- long-only and short-only designs, which hold one side throughout;
- any family that does not make condition 1's declaration.

Such cells use a two-sample line declared in their pinned text, or are not claimed.

**A correlation-based measure was considered and rejected:** the sides' autocorrelation at lags of 22 to 63 sessions.
At quarter persistence its spread on this block is too wide (`q108_scratch_autocorr.py`).

---

## 5. Power: each candidate's minimum detectable lift (E-051's rule: shown, not capped)

**The toys** (declared now): ten thinned real streams from the calibration draws. They are subset j = 0 of each size
(200, 500, 1,000, 2,000, 5,000), with the coin's side and with sides flipped by session (persist1), value `win1`.

**The power measure P(c).**
- The geometric mean, over the ten toys, of the 80th percentile of the candidate's MDL at **k = 13**, computed on the
  first 20,000 replications of each toy.
- An infinite MDL means no power.
- **In scope D (m6)** P is the procedure's: a toy replication that is not admitted counts its MDL as infinite, since
  the procedure cannot detect a lift there. The percentile is taken over all replications.
- P orders the level-eligible candidates (4.2), and nothing else.

**Reported for every candidate, in absolute units** (win probability in points; net R in R):
- **MDL50 and MDL80 at k = 13, 15 and 20**, on each toy;
- the same for `net3`;
- the same on Q-16's synthetic `cluster` at 1,000 trades;
- P relative to C0's.

**What a family does with it.** Whether a family decides by the adopted one-sample statistic or by the two-sample
forms is that family's declaration, made from these figures before its pin. That is E-051's rule: the power is shown,
not capped against a statistic that itself failed.

---

## 6. The runs (built first; then one heavy run each, under the lock)

### 6.1 The build (light)

**Code:**
- `extended/lift_one_sample.py`: the candidates, `K_RANGE_1S`, the admission (R, E and the non-tie series) and exact
  enumeration;
- `scripts/q108_calibrate.py` and `scripts/q108_validate.py`.

**Tests on synthetic data**, all before any run:
- CR2/BM reduce to CR1 and G' - 1 on equal blocks, and the df formula matches a direct trace computation;
- the MDL identities;
- the scalar forms against the vectorised ones;
- exact enumeration against Monte Carlo on the same synthetic subset, within the Monte Carlo interval, at L = 42, 55
  and 63;
- C8's reference against a direct quantile on iid data;
- on Q-16's own seeds, the constructions of 3.2 (the fixed-data streams) and 3.3 reproduce Q-16's rejection counts,
  as Q-82's test does;
- the alternating and Markov side generators: the dwell's mean, the phase, and that they never read an outcome;
- the admission:
  - ties and empty sessions dropped;
  - a single-side series never admitted;
  - a 63-session block-constant side never admitted on 657 or n_c sessions;
  - E >= 4 refusing a series with a run over half the non-tie sessions;
  - the re-read's constructed cases (a long side with ties on alternate sessions; a long side with a dozen brief
    reversals) refused;
- the P_MC dynamic program against a nested-binomial simulation;
- the nesting assertion (counts and exact sizes non-increasing in k) refusing a planted violation;
- the worst exact ratio and condition 3 on planted exact sizes;
- the pattern encoding, the alternating convention and every index order of 4.1, against hand-built cases;
- the seed map and the guard:
  - the folded NAME + constant case;
  - a bounded `range` loop refused when it reaches a block;
  - an unbounded loop printed, never refused;
- the choice rule and the criterion on planted size tables.

**Reads**, exactly as Q-83's:
- P-16's pairs through the `scripts/q16_p16_pairs.py` step;
- the calendar through `extended.reader.read_walks` (purpose `registered_design`, E-035, P-16), asserting E-094 (2)'s
  count and sha256.

**Writes.** Results go only through `extended.results`, Q-97's ledger rule included. Each runner refuses outside a
clean run.

### 6.2 The calibration run

- **When:** one heavy run, from a clean checkout of the commit carrying the pinned plan and the merged build.
- **Size:** 2,293 nulls in the rule -- 1,123 Monte Carlo at 200,000 replications and 1,170 exact -- plus 84 beside at
  100,000. The ten candidates C0 to C9, on shared draws, in both scopes.
- **Time (m6)**, as estimates. The lock's hours are set from the build's measurement.
  - **The base:** Q-83's one-sample real nulls ran about 6 s each for four statistics, by its log's per-null lines
    (the read's m6). Its count-persistent ones ran far longer.
  - **The Monte Carlo real nulls:** about twice that each with every candidate. That is some 1,100 nulls, about 3.5 to
    4 hours.
  - **The exact part:** the timing check puts the three flip enumerations of one data set and value at seconds, and a
    few times that with every candidate. That is about 1 to 1.5 hours.
  - **The rest:** the synthetic and beside nulls about an hour; the pairs step about 1.5 minutes; C8's table minutes.
  - **In all:** about 6 hours, and the lock perhaps 8.
- **Memory: at most about 1.2 GB; `--mem-gb 1.5`.**
  - Q-82's build measured a Monte Carlo compute process near 0.8 GB at a 10,000 batch on synthetic inputs.
  - The read measured Q-83's one-sample part near 0.7 GB (n7).
  - The exact enumeration at L = 42 holds 2^17-pattern arrays of tens of MB, one phase at a time.
- **Writes:**
  - `q108_cal_size.csv`: every null x candidate x scope x level -- the rejections and rate with its interval, or the
    exact size -- and each construction's spread across its subsets;
  - `q108_cal_power.csv`;
  - `q108_sn_table.csv`;
  - `q108_choice.csv`.

### 6.3 The validation run

- **When:** after a decision row records the choice from `q108_choice.csv`, with no hand choice. One heavy run.
- **Size:** the same 2,293 nulls plus 84 beside, on the validation seeds, with the chosen statistic or procedure, and
  C0 beside.
- **Time:** about 3.5 to 4 hours, the lock set from the build's measurement.
- **Memory:** at most about 1.2 GB; `--mem-gb 1.5`.
- **Writes:** `q108_val_size.csv`, `q108_val_power.csv` and `q108_val_criterion.csv`. The criterion prints
  `HOLDS | FAILS | NOT CHECKED`.

### 6.4 Both runs

- Each is watched to its exit.
- A failed run is kept and diagnosed by the failure protocol. Nothing is rerun to pass.

---

## 7. What follows from each outcome

1. **NONE at the choice.**
   - The trades-first one-sample line stays unavailable. No family may decide a line by a one-sample lift over the coin
     twin, and C0 (`bound`) is used for no judged reading.
   - **The validation block is retired, never drawn (m3)**, so that no later round can use it after seeing the
     calibration.
2. **The chosen statistic FAILS its validation.** As item 1. Nothing is re-chosen on the validation seeds.
3. **In either failure,** families use the two-sample forms, which held (E-091), with K0: F-02's C1' form against a
   placebo (`two_sample_bound`), or E-023's placebo-selection twin (`placebo_selection_bound`).
   - Family B stays blocked on its C1 (E-094 (3) (c)).
   - Resting levels return only on a two-sample design, or after a later declaration finds a statistic.
4. **A later round (m5)** needs a new declaration, new seeds and a new row, and:
   - its null class contains this plan's;
   - no construction is dropped after it failed here, unless argued from something other than that failure and
     labelled so;
   - this round's validation constructions are re-drawn on its new seeds, inside its criterion.
5. **The chosen statistic HOLDS.** A row adopts it as the one-sample line in `extended/lift_one_sample.py`, its own
   blob pinned by that row.
   - Families may declare C1 on it, within its scope.
   - **Their K0 checks are run on the adopted statistic (m4)**, not on `cons`.
   - In scope D, the line exists only for cells admitted by 4.4. A cell not admitted is "not claimed", unless its
     pinned text declared a two-sample line for it.
6. **Persistence past a quarter is in neither scope (n3).** Long-only designs, half-year regimes and any side constant
   past 63 sessions cannot use the one-sample line at all.
   - **The mechanism (the re-read's MATERIAL 2):** the family's declaration (4.4 condition 1), the runs check R
     (quarter-constant sides never pass), and the floor E >= 4 (dominated sides never pass).
   - Part of the L = 63 failure is the drift credit of E-035's note 8. Under a drift, the aligned pattern is "a random
     side that leaned with the drift in every quarter", which conditionally is a positive lift over the coin twin.
   - A side-matched two-sample comparison removes that credit, and is the natural route for such cells.

---

## 8. Disclosures

- **The candidates, scope D and its procedure were designed after Q-83's failure was seen.** That is why the choice is
  made on new calibration seeds and validated on other new seeds, by rules written here before either run.
- **Scope D's restriction was motivated by the failing null's persistence.** Its admission reads sides only, never
  outcomes. Its effect is measured as a procedure, on the read's switch-timing sides as well as on the flips.
- **The fixed-data streams are fresh for no one (n1).** `offered` and `taken` are the trades of Q-16, Q-55 and Q-83,
  and on them a validation tests Monte Carlo noise only. The fresh test is in the subsets and the synthetic draws.
- **One population (n2).** Every subset in both runs comes from P-16's judged offers, so they share its quarter
  structure. The validation tests the subset lottery inside one market, not other markets or designs.
- **P-16's judged pairs have been read before** -- by Stage 2, Q-16, Q-55 and Q-83 -- as a source of null dependence.
  No family's outcome is read by this calibration (the red team's n8 on Q-16,
  `docs/reviews/PASS_LINE_CODE_2026-11-16.md`).
- **The calibrated range is k = 13..20** (`lift_one_sample.K_RANGE_1S`).
  - A family numbered beyond 20 needs the range extended under its own row.
  - `lift_bound.K_RANGE` (11..15) is unchanged, and still serves the two-sample forms as calibrated.

---

## 9. The red team's findings and what changed

### 9.1 The first read (on the first text f3e5768; `docs/reviews/Q-108_plan_2026-11-16.md`), answered in the second text

| finding | change (and where it now stands) |
|---|---|
| M1 (a) | scope D calibrated and validated as a procedure, the admission per replication or cell, over all nulls (4.2, 4.4); the L = 55 flips, alternating 45 and 55, and Markov 30, 50 and 80 added to the rule (3.1) |
| M1 (b) | a judged failure is "not claimed"; a two-sample line decides only if pinned for that cell before any read (4.4, 7 item 5) |
| M1 (c) | the judged read's mechanism named: a purpose on the `Judged-block reads:` line, in the stage-C run, before any outcome (4.4) |
| M1 (d) | R kept, with the argument against E alone; thresholds from the blocks' own counts (4.4). The third text adds the floor E >= 4 (9.2) |
| M2 | section 1 rewritten as a necessary bound; H1 and H2 given; "no persistence is shown safe"; the quarter sentence deleted |
| M3 (i) | the per-subset size decides, argued (3.4, E-105 (1)); unattainable at L = 63 without a margin, stated; the `flat` form beside at L = 21, 42, 63 |
| M3 (ii) | exact enumeration at L = 42, 55 and 63 and on the alternating models; exact sizes carry no interval; the scalar re-decision on a seeded sample (3.1, 4.1) |
| M3 (iii) | 23 subsets per size (115 per persistent model) by a stated detection requirement; 25 for the non-persistent models, argued (3.2). The third text states it as pooled over sizes (9.2) |
| M4 | the level rule from the calibration counts with the two floors; the power ceiling dropped; absolute MDLs reported; the grid m = 1.25..2 (2.2, 4.2, 5). The third text renames the probability and adds the exact-ratio condition (9.2) |
| M5 | k = 13..20 in the new module's constant; P at k = 13; section 8 restated (2.1, 5, 8) |
| m1 | the bound's conditions and the edge-block figure (section 1) |
| m2 | the nearest-seed line corrected; derived seeds checked by hand; the guard named (4.1). The third text bounds loops and stops refusing on an assumed reach (9.2) |
| m3 | NONE retires the validation block, never drawn (7 item 1) |
| m4 | K0 run on the adopted statistic (7 item 5) |
| m5 | a later round's three conditions (7 item 4) |
| m6 | the run-time base corrected; the lock set from the build's measurement (6.2, 6.3) |
| m7 | the choice-block threshold from its own count (4.4) |
| m8 | the scratch checks committed under `docs/calibration/scripts/q108/`, with their seeds (status) |
| m9 | the second text counted the tie as a state of its own. **Withdrawn in the third text** (the re-read's MATERIAL 1): ties are dropped again, as in the first text (9.2) |
| m10 | C8's reference stated as calendar-time and measured on the sparse subsets (2.2) |
| m11 | C5's iid working model labelled as chosen (2.2) |
| m12 | the count-persistent nulls beside in the calibration too (3.5, 4.1) |
| n1, n2 | taken, as disclosures (8) |
| n3 | taken: persistence past a quarter is in neither scope; the side-matched two-sample route (7 item 6) |
| n4 | taken: the reason scope D is calibrated as a procedure (4.4) |
| n5 | taken: C7's citation limited (2.2) |
| n6, n7 | readings; n7's memory figure used in 6.2 |

### 9.2 The re-read (on the second text 490b663; `docs/reviews/Q-108_plan_v2_2026-11-16.md`), answered here

**What the second text removed, and this text restores (m5):**
- the first text's declaration condition, "its family declares (E-035 (6)) no side persistence of a quarter or
  longer" (removed without record in the second text);
- the sentence "a side series with a single side throughout a block is not admitted";
- the dropping of tied sessions from the run series (replaced in the second text by a tie state of its own).

| finding | change |
|---|---|
| MATERIAL 1 (the tie state) | R and E computed on the non-tie traded sessions, ties and empty sessions dropped; the single-side sentence restored; "designs balanced in most sessions" stated as excluded (4.4); the m9 reversal mapped (9.1) |
| MATERIAL 2 (the dominant run; the dropped declaration) | the E-035 (6) declaration restored as the admission's condition 1; the floor E >= 4 (no run over half the non-tie sessions, by E <= 1/s^2) added; both applied per replication in the procedure, with R; "measured, not argued away" corrected (4.4, 7 item 6) |
| MATERIAL 3 (the guard) | a loop index bounded by its literal extent (`range` with constant bounds, `enumerate` over a literal sequence); otherwise the expression printed for a recorded hand check, never refused on an assumed reach; imported names stated as not folded (4.1) |
| MATERIAL 4 (the probability), with E-110's ruling | the probability renamed P_MC, the Monte Carlo part's probability of holding, with what it treats as standing for what; each candidate's worst exact ratio reported; **a third eligibility condition, the worst exact ratio at most 1/4**, argued as a chosen constant; the cost of that condition shown beside the choice (4.2) |
| m1 | the detection requirement stated as pooled over sizes per persistence, with its single-size figure beside it (3.2) |
| m2 | the alternating models' floor and criterion read "no configuration rejects", with the framing (3.1, 4.2, 4.3) |
| m3 | n_c is the span the family's stage A actually reads (4.4) |
| m4 | imported constants plus offsets checked by hand and recorded (4.1) |
| m5 | the removals recorded (above) |
| m6 | the builder's choices fixed: the pattern encoding and cell order (3.1); the alternating convention (3.1); what "rejecting" means in the scalar sample, and every index order (4.1); C8's table generator (4.1); P in scope D (5); the nesting assertion (4.2) |
| n1 | a reading (the table checked) |
| n2 | taken: the timing script described as a stand-in (3.1) |
| n3, n4 | readings |
