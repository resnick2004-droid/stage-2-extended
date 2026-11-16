# Q-108: the one-sample pass line's re-calibration -- the plan, declared before anything is built or run

**Status: a plan, for a red-team read, then pinned by its LF sha256 under a decision row.** Nothing in it has been
built or run. It holds no result:
- The arithmetic in section 1 uses only declared constants: the judged block's 657 sessions and the family levels
  0.05/(k(k+1)).
- Two scratch synthetic checks informed the choice of section 4.4's admission statistic. They are described, not
  quoted. They drew seeds 10810801 and 10810802, outside the program's 2026 space.
- Q-83's figures are cited by file and section, never retyped.

**Why** (E-091, E-094 (1), (3) (e); the audit `docs/audits/Q-83_fresh_seed_validation_2026-11-16.md`):
- Q-83 found the one-sample `cons` (`extended.lift_bound.bound`, the statistic of C1's lift over the coin twin) above
  nominal on one real null: P-16's pairs thinned afresh to 5,000 trades, the 1R win value, signs flipped in 63-session
  blocks. Its interval lies wholly above nominal at k = 11 to 14 (the audit, section 3.1).
- The two-sample forms held.
- The audit's diagnosis is M2's selection-on-draws effect, through the thinned subsets. With 63-session flips a
  replication spans only eleven or twelve sign blocks, so one sign pattern carries a probability of the order of the
  family levels. The size there depends on which trades were drawn (the audit, section 3.3).
- The trades-first one-sample line (E-008) therefore has no statistic that holds its level. This plan declares how
  one is to be chosen, and validated on seeds it was not chosen on.

---

## 1. What the diagnosis implies (arithmetic, no data)

**The null.** It is Q-16's sign-flip construction, `scripts/q16_calibrate.py` `_flip_signs`. On n = 657 sessions with
flip blocks of L sessions at a uniform random phase p in 0..L-1, the sessions touch B(p) = floor((656 + p)/L) -
floor(p/L) + 1 blocks. A one-sided test that rejects whenever the **aligned pattern** occurs -- every block's sign
agreeing with the sign of its own block sum -- has, on that null, a size of at least

    A(L) = (1/L) sum_p 2^-B(p)

(the aligned pattern itself, at each phase).

| L | blocks touched, by phase | A(L) | A(L) against 0.05/132 (k = 11) | against 0.05/240 (k = 15) |
|---|---|---|---|---|
| 21 | 32 at 16 phases, 33 at 5 | 2.05e-10 | negligible | negligible |
| 42 | 16 at 16 phases, 17 at 26 | 1.05e-05 | 0.03 of nominal | 0.05 of nominal |
| 63 | 11 at 37 phases, 12 at 26 | 3.875e-04 | **1.02 times nominal** | **1.86 times nominal** |

**Why this matters.** On the aligned pattern a sample looks like a lift that is positive in every quarter. The t-type
members reject it whenever the quarters' sums are of even size: their t is then about sqrt(G) divided by the sums'
coefficient of variation.
- **So at L = 63, a test with power against a lift that is consistent quarter by quarter cannot hold the family's
  levels on every thinned subset.** On every subset whose quarter sums are even enough, its size is at least A(63),
  which is above every level from k = 11 to 15.
- The audit's failing rate (the audit, section 3.3) is of exactly this order.
- To hold there, a statistic must decline samples in which all eleven or twelve quarters agree, unless the lift is
  large against the spread within quarters. That is a margin, and it costs power.
- **At L = 42 and below, the bound is far below the levels.** The persistence that breaks the one-sample line is a
  side that holds for about a quarter of this block.

**Hence two scopes**, both declared now (section 4):
- **scope Q**, every persistence up to a quarter;
- **scope D**, sides switching often enough that their sign blocks are many. It is open only to cells whose sides pass
  an outcome-free admission check.

The calibration tries scope Q first.

---

## 2. The candidate statistics (none chosen yet)

### 2.1 The common setting

- **What is tested.** The per-trade pair difference x_i = (outcome(rule side) - outcome(mirror)) / 2 at the same
  bracket, as in `extended/lift_bound.py`, summed per session of the judged calendar:
  - S_j and N_j, the sum and the count of session j, every session counted;
  - n = 657 sessions, A1's stored days 2024-01-02..2026-07-16. Their count and their sha256 are recorded in E-094 (2),
    and every runner asserts both.
- **Blocks.** b-session blocks are `lift_bound.block_index(657, b)`. G' is the number of non-empty blocks.
- **Levels.** One-sided, at 0.05/(k(k+1)) for k = 11..15 (`lift_bound.K_RANGE`). Also at 0.001, 0.005, 0.01 and 0.025,
  reported beside.
- **Minimum detectable lift.** MDL is the smallest lift added to every trade that the statistic rejects, per
  replication.
- **Where the code goes.** Every candidate is built in a new module, `extended/lift_one_sample.py`, which imports
  `lift_bound`'s functions. `lift_bound.py` keeps its blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2`, which F-03 pins.
  Each candidate has a vectorised form, used by the calibration, and a scalar form, the one a family calls. Every
  rejection the runs count at a family level is decided again by the scalar form, as in Q-82.

### 2.2 The candidates

| id | name | definition | argued from |
|---|---|---|---|
| C0 | `cons` | the shipped statistic: `t21w`, `t42w` and `t63w` (CR1 variance, t with df G' - 1) all reject | the reference for power. **Eligible in scope D only**: it failed E-052's criterion on Q-16's class, which scope Q contains (E-091) |
| C1, C2, C3 | `cons_m` with m = 1.25, 1.5, 2.0 | each member's critical value multiplied by m: reject if est - m t(1 - a; G' - 1) se > 0 | **a margin.** Section 1: on the quarter-persistent null the failure comes from aligned and near-aligned patterns that the members reject. A margin removes those whose t lies between the critical value and m times it; whether that is enough is what the calibration measures. Cost: every MDL scales by about m |
| C4 | `cons_bm` | each member with the CR2 variance and Bell-McCaffrey degrees of freedom (formulas below) | **few and unequal clusters.** A thinned subset of a few hundred trades, and any count-persistent stream (E-052 (1)), leaves blocks of very unequal weight. CR1 with G' - 1 df then understates the variance and overstates the df. CR2/BM is the standard small-cluster correction (Bell and McCaffrey 2002; Imbens and Kolesar 2016; Pustejovsky and Tipton 2018). It does not by itself remove section 1's aligned-pattern bound |
| C5 | `cons_bm_m` with m = 1.25 | C4 with the margin of C1 | both of the above |
| C6 | `cons_im` | C0 together with `t63e`: the mean of the non-empty 63-session blocks' per-trade means, se = their sd / sqrt(G'), t with G' - 1 df (`lift_bound.t_stats(..., block=63, weight="equal")`); all four reject | **equal weights across quarters** (Ibragimov and Müller 2010: the t-test is conservative for heterogeneous normal group means at small levels, by Bakirov and Székely 2005). It removes a few heavy blocks' dominance of the trade-weighted mean. Its exposure to the aligned pattern is the same |
| C7 | `sn` | the self-normalised statistic below | **no block length to choose.** Self-normalisation (Lobato 2001; Shao 2010) studentises by the partial sums' own path, robust to dependence of unknown strength. Its critical value is pivotal and is simulated once. The aligned pattern still gives a large T, so it is measured, not assumed |
| C8 | `cons_sn` | C0 together with C7 (all four reject) | the intersection's logic of Q-16 (members failing on different nulls) with a member of a different kind |

#### The formulas (the build implements exactly these)

**C4's member at block b.**
- est = sum S / sum N. For each non-empty block g: u_g = BS_g - est BN_g, p_g = BN_g / N with N = sum N, and
  w_g = 1 / (1 - p_g).
- se^2 = sum_g w_g u_g^2 / N^2. The CR2 adjustment for a mean is (1 - p_g)^(-1/2) on each block's residual sum.
- df_BM = N^2 / [ sum_g BN_g^2 + (sum_g w_g BN_g^2 / N)^2 - sum_g w_g^2 BN_g^4 / N^2 ].
  - This is Bell and McCaffrey's (tr K)^2 / tr K^2 for the mean under a working model of independent trades.
  - It equals G' - 1 when the blocks have equal counts; the build's tests check this.
- The member rejects when est - t(1 - a; df_BM) se > 0, se > 0 and df_BM >= 1. A block holding every trade
  (p_g = 1) leaves the bound blank.

**C7.**
- T = sum_j S_j / sqrt( (1/n) sum_{t=1}^{n} U_t^2 ), with U_t = sum_{j <= t} (S_j - est N_j) and est = sum S / sum N,
  over all 657 sessions (an empty session adds nothing).
- It rejects when T > c_a.
- **The reference c_a** is the ceil(a D)-th largest of T over D = max(2,000,000, ceil(200 / a)) draws of 657 iid
  standard-normal session sums with N_j = 1.
  - All the levels come from one set of draws, seeded as in section 4.1.
  - The table is written as a result file of the calibration run, and the choosing row pins it.
- MDL = (c_a sqrt((1/n) sum U_t^2) - sum S) / sum N, since adding a lift to every trade leaves the U_t unchanged.

**MDLs.**
- A t-type member's MDL is m crit se - est (m = 1 without a margin).
- An intersection's MDL is the largest of its members'.

### 2.3 Considered and excluded, with the argument (not run)

| idea | why excluded |
|---|---|
| dropping `t63w` (`t21w` with `t42w` only) | On the failing null all three members are lax, and the 63-session member most of all (the audit, section 3.2). The 21- and 42-session members are the ones Q-16 found lax when a side persists past their block (`docs/research/calibration_2026-11-15.md` 7.1). Dropping the strictest member can only raise the size |
| more, shorter blocks per member | More blocks bring more df but shorter blocks. Each member's validity needs blocks longer than the side's persistence, and shorter blocks are the lax ones on persistent sides (the note's Table 1) |
| `t126w` in place of `t63w` | Five blocks. The t critical value at df 4 is about 1.9 times df 9's at k = 11 (t quantiles: 9.26 against 4.98), and its se is estimated from five blocks. Its MDL lies beyond section 5's power ceiling by construction |
| exact sign-flip (randomisation) tests | **63-session blocks:** with ten blocks the smallest attainable p is 2^-10, above every family level, so it has no power at all. **21- or 42-session blocks:** they are exact only when the side's sign blocks coincide with the test's blocks, which no rule guarantees. Calibrating a randomisation test at 200,000 null replications needs at least 20/a resamples each, beyond any run here. And sign symmetry is not the pass line's null: a long-leaning rule's lift can have mean zero without being symmetric |
| the studentised circular block bootstrap | Q-16 found it as lax as `t21w` on the dense persistent null (the note's Table 3), at a far larger cost |

---

## 3. The nulls

Every null is mean-zero by construction. All the candidates are computed on the same draws.

### 3.1 Fixed-data real nulls (Q-16's, sign flips drawn afresh)

- **Data.** P-16's registered pairs (`scripts/q16_p16_pairs.py`, its three identities refusing) on the judged block.
- **Streams.** `offered` and `taken`, as `scripts/q16_calibrate.py` builds them.
- **Values.** `win1` (win probability at 1R) and `net3` (net R at 3R).
- **Sides.** Flipped in blocks of L = 1, 5, 21, **42** or 63 sessions, or the coin's own side.
  - L = 42 is new: it is the boundary of scope D (section 4.4).
- **Count:** 2 x 2 x 6 = **24 nulls**.

### 3.2 Fresh thinned subsets of the persistent nulls (the declared family, new)

- **The subsets.** For each size z in 200, 500, 1,000, 2,000 and 5,000 trades, and each subset index j = 0..4, one
  subset of P-16's judged offers is drawn without replacement: 25 subsets.
- **The nulls on each subset.** Every value (2) times every side (6) gives **300 nulls**.
- **Why five subsets.** Five independent subsets of each construction measure the selection-on-subset effect. The run
  reports each construction's spread across its subsets (the least and the largest rate), and the choice rule counts
  every subset as a null of its own.
- This family replaces Q-16's `thinN` nulls, which were one fixed subset per size.

### 3.3 Q-16's realistic synthetic nulls

- `iid`, `cluster`, `cluster_ar1`, `regime01` and `volclust` at 200 to 5,000 trades: **25 nulls**.
- They use `syn_batch` unchanged. The stress nulls are not run.

### 3.4 The scopes' null sets

| scope | nulls in the rule and the criterion |
|---|---|
| **Q** | all of 3.1 to 3.3: 24 + 300 + 25 = **349** |
| **D** | the same without the 63-session flips: 20 + 250 + 25 = **295**. The 54 persist63 nulls are reported beside |

**Beside, in the validation run only, never in a rule:** the count-persistent real one-sample nulls of Q-82's (ii)
(54, `extended/count_nulls.py`, the same grid, on the validation seeds). F-03's and every family's K0 addresses count
persistence cell by cell.

**Replications.** 200,000 a null, in batches of 10,000, in both runs.

---

## 4. Seeds, the choice rule, the validation criterion, the scopes

### 4.1 The seed blocks (new; verified unused before this text)

Both blocks were checked with:
- a word-bounded search of every worktree's files, the main tree's working copy (the licensed data excluded) and every
  branch and remote (`git grep`);
- `git grep` over all 284 commits reachable from them.

None of 20262110-20262129 is named anywhere, and no range written anywhere covers them. The nearest seeds in use are:
- below, 20262104: Stage 2's D-663 (20262101-20262104) and RD-01's undeclared draws ending at 20262103
  (`docs/reviews/BUILD_RD-01_2026-11-16.md`);
- above, 20262508.

The runners' own guard, as Q-82's, refuses at run time if any seed of its block is used elsewhere.

**Calibration block, 20262110-20262119:**

| seed | use |
|---|---|
| 20262110 | the calibration build's tests |
| 20262111 | the fixed-data real nulls' flips, `default_rng([s, i])`, i the null's index in 3.1's order |
| 20262112 | the thinned subsets: subset (z, j) by `default_rng([s, z_index, j])` |
| 20262113 | the flips of the null (z, j, value, side): `default_rng([s, z_index, j, value_index, side_index])` |
| 20262114 | the realistic synthetic nulls, `default_rng([s, i])`, i the null's index in Q-16's list |
| 20262115 | C7's reference table (section 2.2) |
| 20262116-20262119 | spare, drawn by nothing |

The indices: `z_index` 0..4 for 200, 500, 1,000, 2,000 and 5,000 trades; `value_index` 0 for `win1` and 1 for
`net3`; `side_index` 0..5 for L = 1, 5, 21, 42 and 63 and the coin's side. Within a null the batches draw in turn from
its one generator, as Q-16's do.

**Validation block, 20262120-20262129:**

| seed | use |
|---|---|
| 20262120 | the validation build's tests |
| 20262121 | as 20262111 |
| 20262122 | as 20262112 |
| 20262123 | as 20262113 |
| 20262124 | as 20262114 |
| 20262125 | the count-persistent nulls beside |
| 20262126-20262129 | spare, drawn by nothing |

E-052's spares, 20262018-20262019, stay undrawn.

### 4.2 The choice (calibration seeds only; the rule is coded in the calibration script and applied by it, never by hand)

**The level rule.** A candidate is level-eligible in a scope when, for every calibration null of that scope and every
k in 11..15, the 95 % Clopper-Pearson interval of its rejection rate lies **wholly at or below nominal**: its upper
limit is at most 0.05/(k(k+1)).
- At 200,000 replications this means at most 58, 48, 40, 34 and 29 rejections at k = 11 to 15.
- **What the rule demands** (binomial arithmetic), for a statistic whose true size is a constant fraction of nominal on
  every null:
  - a quarter of nominal: it passes almost surely;
  - a third: it passes about nine times in ten;
  - a half: it almost never passes.
- So the rule asks for *demonstrated* conservatism, the mirror of E-052's criterion, so that a choice made on these
  draws survives fresh ones. Its cost is power, which section 5 bounds.

**The power rule.** A candidate is power-eligible when its power measure P (section 5) is finite and at most **1.5
times C0's** on the same draws.

**The order.**
1. **Scope Q.** Among C1..C8, the level- and power-eligible candidate with the smallest P is chosen. Ties go to the one
   with fewer members, then to the earlier in section 2.2's table.
2. **Scope D**, only if scope Q has none. The same rule among C0..C8 on scope D's nulls.
3. **Otherwise none.**

The script prints `CHOSEN <name> (scope Q)`, `CHOSEN <name> (scope D)` or `NONE`, and writes the decision with every
candidate's eligibility to `q108_choice.csv`.

### 4.3 The validation criterion (fixed now, as E-052's)

- The validation runner reads the choice from the calibration's result file (its manifest verified). Nothing is
  re-chosen.
- **The chosen statistic HOLDS** if, at every k in 11..15, no validation null of its scope -- the fixed-data real nulls,
  the fresh thinned subsets and the realistic synthetic nulls, all on the validation seeds -- has its 95 % interval
  wholly above nominal.
- It **FAILS** if any such interval lies wholly above nominal at any k, and is **NOT CHECKED** -- never a pass -- if
  any of its scope's nulls is missing.
- **What the criterion demands** (binomial arithmetic): over 349 nulls, a statistic at seven tenths of nominal
  everywhere fails it by chance about twice in a thousand; one exactly at nominal fails it almost surely. So it demands
  the conservatism that 4.2 chose for.
- **Reported beside, never in the verdict:**
  - C0 on the same draws;
  - in scope D, the persist63 nulls;
  - the count-persistent nulls;
  - the power on the validation toys.

### 4.4 Scope D's admission (outcome-free; declared now)

A cell may decide C1 by a scope-D statistic only if all three hold:
1. its family declares (E-035 (6)) no side persistence of a quarter (63 sessions) or longer;
2. **on the choice block**, at stage A, its sides give R >= 20 runs;
3. **on the judged block**, inside stage C and before any outcome is read, its sides give R >= 13 runs.

**The runs count R.**
- Each traded session's majority side is m_j = sign(sum of the trades' sides, +1 long, -1 short).
- Sessions with no trade, or with as many longs as shorts, are dropped.
- R is the number of maximal runs of equal m_j, in calendar order.
- A side series with a single side throughout a block is not admitted.

**Why these thresholds.**
- A side constant over blocks of 63 sessions has at most floor((n - 1)/63) + 2 runs on n sessions. That is twelve on
  the judged block, and fewer than twenty on any choice block of at most 1,134 sessions (2020-2023 holds about a
  thousand). **It is never admitted.**
- For block-constant sides, R runs imply at least R sign blocks, so the aligned pattern's probability is at most
  2^-R <= 2^-13, below every family level.
- The scratch synthetic check: sides constant over 21 sessions pass each threshold about nine times in ten; over 42
  sessions, rarely.
- A correlation-based measure, the sides' autocorrelation at lags of 22 to 63 sessions, was considered and rejected:
  at quarter persistence on this block its spread is too wide (the other scratch check).

**What it does and does not read.** Sides are the rule's decisions, read from bars before any outcome. A judged-block
read of them is ledgered like K0's count check (E-052 (1)).

**What it means.**
- A cell not admitted cannot use the one-sample line. It may use the two-sample forms.
- The persist42 nulls lie inside scope D's calibrated class, so every admitted cell is covered with room.

---

## 5. Power: each candidate's minimum detectable lift (E-051's rule: not level against nothing)

**The toys** (declared now): ten thinned real streams from the calibration draws, subset j = 0 of each size (200,
500, 1,000, 2,000, 5,000) with the coin's side and with sides flipped by session (persist1), value `win1`.

**The power measure P(c).** The geometric mean, over the ten toys, of the 80th percentile of the candidate's MDL at
k = 11, computed on the first 20,000 replications of each toy. An infinite MDL means no power.

**Reported beside, deciding nothing:**
- MDL50 and MDL80 at k = 11 and 15;
- the same for `net3`;
- Q-16's synthetic `cluster` at 1,000 trades;
- each candidate's P relative to C0's.

**The ceiling.** P(c) <= 1.5 P(C0).
- C0 cost about a third more lift than the 21-session t for the same power (Q-16's note, 7.1).
- The ceiling caps the fix's further cost at half again. A candidate that holds only by losing more than that is the
  "line that cannot pass" E-051 forbids accepting.

---

## 6. The runs (built first; then one heavy run each, under the lock)

### 6.1 The build (light)

**Code:**
- `extended/lift_one_sample.py` (the candidates);
- `scripts/q108_calibrate.py` and `scripts/q108_validate.py`.

**Tests on synthetic data**, all before any run:
- CR2/BM reduce to CR1 and G' - 1 on equal blocks;
- the BM df formula against a direct trace computation;
- the MDL identities;
- the scalar forms against the vectorised ones;
- C7's reference against a direct quantile on iid data;
- on Q-16's own seeds, the constructions of 3.1 and 3.3 reproduce Q-16's rejection counts, as Q-82's test does;
- the seed map and the seed guard;
- the choice rule and the criterion on planted size tables;
- section 4.4's runs count, including that a 63-session block-constant side is never admitted.

**Reads**, exactly as Q-83's:
- P-16's pairs through the `scripts/q16_p16_pairs.py` step;
- the calendar through `extended.reader.read_walks` (purpose `registered_design`, E-035, P-16), asserting E-094 (2)'s
  count and sha256.

**Writes.** Results go only through `extended.results` (Q-97's ledger rule included). Each runner refuses outside a
clean run.

### 6.2 The calibration run

- **When:** one heavy run, from a clean checkout of the commit carrying the pinned plan and the merged build.
- **Size:** 349 nulls x 200,000 replications, with the nine candidates on shared draws.
- **Time:**
  - Q-83 averaged about 19 s a null for four statistics (its log's total over its nulls).
  - The nine candidates are expected to cost about 2.5 times that, so about 4.5 hours, plus the pairs step (about 1.5
    minutes) and C7's table (minutes).
  - The build measures the per-null cost on synthetic inputs at full batch, and the lock's hours are set from it. The
    expectation is a 7-hour lock.
- **Memory:** about 1.0 GB at peak. Q-82's build measured a compute process near 0.8 GB at a 10,000 batch on
  synthetic inputs, and the candidates add only per-replication vectors (C4's df is a closed form, not a matrix).
  `--mem-gb 1.5`.
- **Writes:**
  - `q108_cal_size.csv`: every null x candidate x level, rejections, rate, interval, the construction's spread across
    its subsets;
  - `q108_cal_power.csv`;
  - `q108_sn_table.csv`;
  - `q108_choice.csv`.

### 6.3 The validation run

- **When:** after a decision row records the choice from `q108_choice.csv` (no hand choice). One heavy run.
- **Size:** 349 nulls plus 54 beside, with the chosen statistic and C0 beside.
- **Time:** about 3 hours; a 4.5-hour lock.
- **Memory:** about 1.2 GB.
- **Writes:** `q108_val_size.csv`, `q108_val_power.csv` and `q108_val_criterion.csv`. The criterion prints
  `HOLDS | FAILS | NOT CHECKED`.

### 6.4 Both runs

- Each is watched to its exit.
- A failed run is kept and diagnosed by the failure protocol. Nothing is rerun to pass.

---

## 7. If no candidate passes, or the chosen one fails its validation

1. **The trades-first one-sample line stays unavailable.**
   - No family may decide a line by a one-sample lift over the coin twin.
   - `bound` (C0) is not used for any judged reading.
2. **Families use the two-sample forms**, which held (E-091): F-02's C1' form against a placebo
   (`two_sample_bound`), or E-023's placebo-selection twin (`placebo_selection_bound`), with K0.
   - Family B stays blocked on its C1 (E-094 (3) (c)).
   - Resting levels return only on a two-sample design, or after a later declaration finds a statistic.
3. **Nothing is re-chosen on the validation seeds.** No third round runs without a new declaration, new seeds and a
   new row.
4. **If scope D is chosen and holds,** the line exists only for cells admitted by section 4.4. A cell not admitted is
   in case 1.
5. **If a statistic holds** (in either scope), a row adopts it as the one-sample line in `extended/lift_one_sample.py`.
   - Its own blob is pinned by that row.
   - Families may declare C1 on it within its scope; their K0 count checks stay.

---

## 8. Disclosures

- **The candidates and scope D were designed after Q-83's failure was seen.** That is why the choice is made on new
  calibration seeds and validated on other new seeds, by rules written here before either run.
- **Scope D's restriction was motivated by the failing null's persistence.** Its admission check reads sides only,
  never outcomes.
- **P-16's judged pairs have been read before** -- by Stage 2, Q-16, Q-55 and Q-83 -- as a source of null dependence.
  No family's outcome is read by this calibration (the red team's n8 on Q-16, `docs/reviews/PASS_LINE_CODE_2026-11-16.md`).
- **The calibrated range** stays k = 11..15. A family numbered beyond it needs the range extended under its own row.
