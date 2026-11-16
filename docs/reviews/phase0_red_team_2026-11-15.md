# Phase 0 red team: the five audit tracks attacked (2026-11-15)

The red team (`.claude/agents/red-team.md`), working read-only from `wt-scout` and the main tree. **Targets:** the five
notes in `docs/audits/phase0/` (A, B, C, D, E). I checked them against `CHARTER.md`, `DECISIONS.md` (E-001 to E-006),
`DIRECTIVE.md`, `prereg/F-01_resting_order_level_atlas.md`, and the vendored tree (`vendor/stage2/DECISIONS.md`;
`propedge/research/u_select.py` and `user_journey.py`; `propedge/campaign/lockstep.py` lines 1588-1603;
`config/rules.yaml`, `windows.yaml`, `orb5_grid.yaml`, `search_program*.yaml`; `prereg/DRAFT_P16_confirmation.md`; the
result files named below). I also looked at branch `wt/wt-levels` (commit 2b6770e) to answer F-01's k question.

**What I ran:** ten small scratch scripts of my own, one process each, `OMP_NUM_THREADS=1`. They are in
`C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\redteam\`,
which is not durable. I called no auditor's script.
- **On vendored result files:** `rt_load.py`, `rt_p.py`, `rt_s3c.py`, `rt_s3c2.py`, `rt_deny.py`, `rt_guard.py`,
  `rt_month.py`.
- **Synthetic only:** `rt_cal.py`, `rt_cal2.py` (calibration of the selection rule) and `rt_fillbar.py` (the fill-bar
  rule).

**What I did not do:** run the engine, read `data/bars` or `data/atlas`, use the web, or write anything except this
note.

**Status of the numbers.** Every number below is an EXPLORATORY red-team reading. It is either computed by those
scripts from the named vendored file or comes from a synthetic simulation, and it is labelled where it appears. None is
a result of this repository, and none may be quoted as one.

**My reimplementation is checked first.** My moving-block bootstrap, written from `user_journey.block_indices` and
`paired_interval` and their docstrings, reproduces a row of the file exactly:
- the file: `user_journey.csv` section `paired`, P-14 against P-16, `periodic` `share_positive` at 63 sessions, all
  starts: lo -0.046654, hi 0.081031;
- mine: the same two values.

**On the brief.** It lists targets to scrutinise and states no wanted conclusion; I treated it as scope only.

## Verdict

- **On F-01: it must be re-declared.** I agree with track D on that, not on all its reasons:
  - D-1 (the fill-bar rule), D-2 (the `or30` cells and the basis sentence) and D-3 (stage D) each change a declared
    rule, and no reading can repair them.
  - D-5 can be a reading.
  - D-8 is real but minor, and it is not on its own a reason to withdraw.
- **On the audit set:** most graded findings hold. Four are overstated in grade or scope: B-1, C-1, C-M-1 and D-P-2.
  B-1's claim that among working designs it is speed that tracks P is **refuted**: it is a between-base (Simpson)
  effect.
- **The most consequential point is one no track draws** (Missed M2). Both B and D require the selection rule to be
  recalibrated. Once it is, no design whose trades differ from P-14's (F-01's stage D, every Track 2 model) can carry
  on this judged block, even at P = 1.
- **The declared confirmation cannot confirm P at all** (Missed M1).

## 1. The verdict table: every finding graded CHANGES-A-CONCLUSION (CAC) or MATERIAL (MAT)

Track A graded none (section 2.0). Track E grades by currency (CHANGED / NEW). I include the four of its items that bear
on the model or on a conclusion.

| track / id | grade given | finding (short) | red-team verdict | why, in one line |
|---|---|---|---|---|
| B-1 | CAC | S3c is not a sound screen; its 0.76 with P comes from failed designs and arithmetic | **OVERSTATED; partly REFUTED** | Within one trade stream S3c tracks P (+0.89 on P-14's base, +0.67 on P-16's); the -0.20 near the top, and "speed tracks P", are a split between the two bases |
| B-2 / D-P-1 | CAC | Line (3)(i)'s 2,000-draw percentile bootstrap over-rejects at the family level | **CONFIRMED** | Re-derived: 0.6 % (iid) to 2.3 % (a realistic null) against a nominal 0.045 %, with a floor that does not fall as k grows; this is line (i) alone |
| B-3 | CAC | The judged block cannot detect gains of the size seen | **CONFIRMED; UNDERSTATED for designs whose trades differ from P-14's** | n_eff is 58 to 66 for P-14 against P-16; the 80 % MDD is 0.21-0.24 (nominal) and 0.31-0.34 (calibrated), past P = 1 |
| B-4 | MAT | The best design depends on the objective | CONFIRMED | Agrees with Stage 2 D-628; a value judgement that belongs to the operator |
| B-5 | MAT | The guards' tolerances are smaller than their own noise | CONFIRMED | S5a's tolerance is $10.57 against a paired sd of about $711; the effect is lost power and a winner's curse, not false carries |
| B-6 | MAT | P's blind spots are unguarded | CONFIRMED (the timing figure is an upper bound) | The month split and the near-zero masses re-derive; the +0.03 / +0.05 assumes every near-zero start tips |
| B-7 | MAT | The bootstrap's weights favour mid-block advantages | CONFIRMED | Weights about 0.02 at the edges and 1.12 in the middle; the centre sits +0.029 from the sample; the weights are public before any declaration |
| B-8 | MAT | Ways to game the measures | CONFIRMED (as risks; the sizes are bounds) | -- |
| C-1 | CAC | Every user measure is read at 0 % denial with the placement off; P collapses under either | **CONFIRMED as fact, OVERSTATED as a grade** | It is the operator's rule applied as declared (D-234, D-289, D-626); what is missing is the reporting beside the verdict; the haircut figures reproduce exactly |
| C-M-1 | MAT | R\* is not robust to denial | **CONFIRMED BUT OVERSTATED** | P-14 stays first at 10-25 % under all three models; the order flips only at 50 % under a per-payout model |
| C-M-2 | MAT | The engine's denial is milder in its tail than the terms | CONFIRMED in structure; "milder" overstated | At an equal nominal p, all-or-nothing gives a higher mean P; it differs in shape, not in mean |
| C-M-3 | MAT | P-14 has none of D-663's stress readings | CONFIRMED; it touches no selection | V1 covers S1 = P-16 and S2 = FV3-C only; P is a real-order replay, so it is unaffected |
| D-P-2 | CAC | Program S had already over-spent the multiplicity budget | **CONFIRMED BUT OVERSTATED (a NOTE)** | The arithmetic is right (0.040 + 0.045), but Stage 2 ran a budget per program by design and no number changes; the real budget problem is P-1's floor |
| D-1 | MAT | F-01's fill-bar rule biases break down and fade up | **CONFIRMED independently; needs re-declaration** | Sign reproduced; the size is about a fifth of the share of fill bars reaching a stop (points per %); line 80 is a declared rule |
| D-2 | MAT | `or30` sits in Stage 2's closed opening-range branch; F-01 line 23 is false; the follow effect is already read | **CONFIRMED; needs re-declaration** | ORB5 used a stop at the range's edge with `rest` on 5/15/30/60-minute ranges; D-281 (3) reserves "genuinely different" to the operator |
| D-3 | MAT | Stage D cannot identify what the tickets are worth | **CONFIRMED and sharpened; needs re-declaration** | P-16 is in a position or in its 5-minute cool-down at about 97 % of its marks, so tickets rarely take the firm; item (4) alone is a reading |
| D-4 | MAT | C1's minimum detectable lift is far above the value bar | CONFIRMED | Arithmetic re-done; a reading is enough |
| D-5 | MAT | One minute of look-ahead at 08:25; side set at `t_live` | CONFIRMED; a reading is enough | The minute is small; the side contradiction is material but section 2 governs |
| D-6 | MAT | The confirmation would be NQ's fourth (D-107) and is P-16's window too | CONFIRMED | `windows.yaml` line 31-33; `DRAFT_P16_confirmation.md` line 28; the operator's to decide |
| D-P-3 | MAT | The judged block is not fresh | CONFIRMED | D-580, D-588, D-592; nine families judged on it |
| D-P-4 | MAT | Identities and tests can pass while the result is wrong | CONFIRMED (spot-checked) | `tests/test_stage2_identity.py:21` skips; 20261901 is `user_drivers.CLUSTER_SEED` (line 71) |
| D-P-5 | MAT | Holes in the protocol are guarded by prose only | CONFIRMED (by inspection) | -- |
| D-8 | MINOR, but cited as a reason to withdraw | K2 allows 10 % unresolved in a year | CONFIRMED as MINOR; not a reason to withdraw on its own | D-308 (3): 5 % "overall, per market and per year" |
| E-C1 | CHANGED | Topstep's Tier 1 news windows | CONFIRMED; MINOR for results | P-14 enters and holds nothing across a release (D-534 (2)); the 07:35:00 edge needs a reading before live use |
| E-C2 | CHANGED | The cited basis of D-530 (1) is out of date | CONFIRMED; MINOR | A new E-row corrects the citation |
| E-N1 | NEW | Topstep and Lucid permit automation | **CONFIRMED; UNDERSTATED** | The no-automation limit, through D-266's 5 minutes, is what closed Stage 2's only program-S candidate to pass all four guards at L = 0 (D-588, D-592) |
| E-N2 | NEW | Terms of Use s.8: "substantially larger position sizes" | **CONFIRMED; UNDERSTATED** | It matches the whole state table and the charter's named lever, not only the opening; it is absent from Stage 2's ledger, so it may be new |

## 2. The detail per finding

### 2.0 Track A

Track A graded nothing CAC or MATERIAL, and I found no reason to promote any of its MINORs. Two of them feed F-01 and
should go into the corrected family's text:
- **MINOR 2.** D-527's misreading is the stated reason the 12.5-point stop is not offered. P-14 itself trades that
  rung. The cut is an unlabelled grid choice made on a false premise.
- **MINOR 1.** The D-212 / D-308 citations are swapped in F-01's K3 and in CHARTER section 4.

### 2.1 B-1, S3c as the screening target: OVERSTATED, partly REFUTED

**What re-derives** (`user_drivers.csv`, section `design_table`, verdict arm, block `all`, 61 designs; `rt_s3c.py`):
- all 61: Spearman(P, S3c) +0.765 and (P, S3a) +0.186;
- without the Consistency and flat-plan families (45 designs): S3c +0.50, S3a +0.59;
- with P ≥ 0.60 (22 designs): S3c -0.198, S3a +0.478.

B's figures hold, and so does its kill-line count: of the 60 designs other than P-14, the 35 at or below P-14's S3c
include none that beats it on P; of the 25 above it, 4 do.

**What B missed: the region near the top holds two trade streams** (`rt_s3c2.py`, `base` column). The 22 top designs
are P-14-based or P-16-based:
- P-14's base: mean P 0.652, S3c 1.874, S3a 0.759.
- P-16's base: P 0.629, S3c 2.061, S3a 0.551.
- In the top-22 list, every P-14-based cell has a lower S3c than every P-16-based cell but one.

Inside each base the sign reverses back:

| base | Spearman(P, S3c) | Spearman(P, S3a) |
|---|---|---|
| P-14, all 23 cells | +0.89 | +0.10 |
| P-16, all 25 cells | +0.67 | 0.00 |
| P-14, top 9 | +0.65 | +0.58 |
| P-16, top 10 | +0.21 | +0.03 |
| top region, pooled within base | **+0.40** | **+0.26** |

**Range restriction alone accounts for most of the drop from 0.76.** I simulated a screen that tracks P equally well
at every level, with ρ = 0.76 across all 61 designs. Among the top 22 it would show only about +0.22 (5-95 %: -0.12 to
+0.54). The observed -0.20 sits just below that range because of the between-base split.

**Verdict:**
- S3c does not rank designs across trade streams, because their fee denominators differ. That part of B-1 stands, and
  it is what matters for F-01's stage D (P-16 trades judged against P-14).
- Within a trade stream, S3c remains the better of the two cheap screens.
- "Among working designs, speed is what tracks P" is refuted: it is the same split between bases. Within P-16's top
  cells, S3a has ρ = +0.03.
- **The right change is narrower than B's "demote to a kill line":** rank by S3c within one trade stream, and by P (or
  a thinned P) across streams.
- DIRECTIVE Part 3 states the screening target, so the change is the operator's to decide (section 4).

### 2.2 B-2 and D-P-1, line (3)(i)'s level: CONFIRMED

**The code** (`u_select.p_difference`, lines 422-442): `paired_interval` is called at alpha = 2 x level, and the lower
limit is `np.percentile(boot, 100 x level)`. There are 2,000 draws, and the blocks are non-circular blocks of 63 starts.

**The real pair**, P-14 against P-16 on the judged block (`rt_p.py`):
- 595 starts, 2024-01-02 to 2026-04-21; mean difference +0.1031.
- At 0.05/110 the percentile's index is 0.909 of the 2,000 sorted draws. So the limit is set between the smallest draw
  (-0.0392) and the second smallest (-0.0078): it comes out at -0.0107, as B found.
- That limit sits 2.23 bootstrap standard errors below the sample mean (2.1 Bartlett standard errors) where 3.32 are
  needed. A normal-theory test at that distance has a level of about 1.3-1.7 %.

**Synthetic calibration** (`rt_cal.py`). The design differs from both tracks' in three ways:
- It uses the rule's own fixed resample matrix (seed 20261700, n = 595). Every judgement at n = 595 uses exactly that
  matrix.
- The comparison against a fresh matrix in every batch changes nothing (0.52 % against 0.62 % iid; 2.31 % against
  2.33 % on the structural null).
- It adds a structural null. Two exchangeable designs' daily P&L share common and own shocks with clustered
  volatility; each start is "ahead" over overlapping 21-, 42- and 63-session windows, with a per-start shock. Its ACF
  (0.44, 0.38, 0.19, 0.03, -0.04 at lags 1, 5, 21, 42, 63) is close to the real one (0.47, 0.20, 0.16, 0.01, -0.08).

| null (40,000 replications each) | rule at 0.05/110 | floor at the minimum draw (k → ∞) | Student-t on 9 batch means |
|---|---|---|---|
| iid | 0.615 % (x13.5) | 0.42 % | 0.030 % |
| AR(1) 0.5 | 0.805 % (x17.7) | 0.55 % | 0.050 % |
| structural, ACF as the real series | **2.33 % (x51)** | **1.84 %** | **0.075 % (x1.6)** |

**Why** (`rt_cal2.py`):
- The bootstrap's sd is 0.92 (iid) to 0.75 (structural) of the true sd of the mean, with a 10-90 % range of 0.50-1.06.
- Its centring offset has an sd of about 0.22-0.27 true standard errors.
- The limit therefore sits a median 2.35 (structural) to 2.87 (iid) true standard errors below the mean, against the
  3.32 required.

**The size:**
- On series like the real one, line (i) alone is roughly a 1-2 % test where it should be a 0.045 % one, 20-50 times
  too lax. B's 30-36 times and D's 18-75 times bracket this.
- The floor does not depend on k, so D's point stands: the program-wide sum of realised levels grows without bound.

**Two corrections to both tracks:**
1. Only line (i) was calibrated. Lines (ii), (iii), (iv) and (4)(e) are conjunctive and lower the full rule's realised
   false-carry rate by a factor nobody has measured. B's own year-rule and guard pass rates suggest a large factor,
   but they are conditioned on the null, not on line (i) having passed.
2. The proposed fix (Student-t on non-overlapping 63-start batch means) is close to its level but **not** at it: 1.6
   times nominal at 0.05/110 and 2.0 times at 0.5 % on the structural null. Any calibration test (T-6) must include
   such a null (clustered volatility, discrete indicators, overlapping windows), not Gaussian ones only.

**What history shows:** no recorded closure flips. All nine Stage 2 families had a negative judged difference.

### 2.3 B-3, power on the judged block: CONFIRMED, and UNDERSTATED for designs on other trades

**The dependence and the noise** (`rt_p.py`):
- The autocorrelation first reaches zero at lag 28.
- The standard error of the mean difference: 0.018 iid (wrong); 0.0511 by the 63-block bootstrap; 0.054 Bartlett;
  0.057 from 9 batch means.
- So n_eff is 58-66 for P-14 against P-16, and 73-95 for P-14 against P-15. B's 60-75 holds.

**The minimum detectable difference at 80 % power**, with standard error 0.051-0.057:
- nominal z: 0.21-0.24;
- calibrated Student-t on 9 batch means (df 8): 0.31-0.34.

**What B under-drew:**
- P-14's judged P is 0.719. Under a calibrated line (i), a candidate with P-16-like noise would need a judged P of
  1.03-1.06 for 80 % power, and about 0.98 for 50 %.
- That is impossible, not merely unlikely (B's "0.89 to 0.95" is the nominal rule's figure).
- Same-trade variants of P-14 (B's standard error about 0.015) remain testable: a calibrated MDD of about 0.09.

**Where B overstates:** "exit (A) is out of reach" is too broad. A large effect, such as another firm's contract shape,
or a variant on P-14's trades, can still carry.

### 2.4 B-4 to B-8

- **B-4: CONFIRMED** (D-628 says the same). Which design ranks first depends on how the distribution is weighted.
- **B-5: CONFIRMED.**
  - On the judged block (`rt_guard.py`), P-14's p10 is $105.70, so S5a's tolerance is $10.57.
  - The paired bootstrap sd of the p10 difference is $711; P-14's own is $669.
  - A relative tolerance on a quantity near zero breaks down. Under the null this makes the rule stricter (lost power),
    and it puts a winner's curse on the guarded readings of any design that passes.
- **B-6: CONFIRMED** (`rt_month.py`).
  - Shares ahead at months 1 / 2 / 3: P-14 0.451 / 0.715 / 0.848; P-16 0.319 / 0.693 / 0.848.
  - Starts within $250 below zero at months 1 / 2 / 3: P-14 5.1 / 2.4 / 1.5 %; P-16 12.2 / 3.1 / 1.0 %.
  - B's +0.030 / +0.054 is an upper bound: it assumes every one of those starts tips.
  - A timing lever relative to the start date is implementable, so the diagnostic B proposes is warranted.
  - I checked whether month-end readings coincide with rebills: they do not (section 5).
- **B-7: CONFIRMED.**
  - Expected weight per start: about 0.02 at the edges and 1.12 in the middle; the centre is +0.1317 against the
    sample's +0.1031.
  - One addition: the matrix depends only on the seed and n, so these weights are known before any family is declared.
    A designer who has read the judged block (D-P-3) knows that early 2024 and early 2026 count for almost nothing.
- **B-8: CONFIRMED** as a list of risks.

### 2.5 C-1, C-M-1, C-M-2: CONFIRMED as fact; C-1's grade and M-1's robustness claim OVERSTATED

**The haircut column re-derives exactly** (`rt_deny.py`; `user_journey.csv` `start`, verdict arm, 1,629 starts; a
start is ahead if (1 - p) x payouts - fees > 0):

| design | p = 0 | p = 0.10 | p = 0.25 | p = 0.50 |
|---|---|---|---|---|
| P-14 | 0.671 | 0.634 | 0.542 | 0.269 |
| P-15 | 0.642 | 0.595 | 0.493 | 0.234 |
| P-16 | 0.620 | 0.568 | 0.511 | 0.311 |

**More readings:**
- All-or-nothing at 0.5: P-14 0.336, P-16 0.310.
- On the judged block alone at 0 / 0.25 / 0.5: P-14 0.719 / 0.590 / 0.282; P-16 0.616 / 0.513 / 0.308.
- The haircut at which P falls to 0.5: P-14 0.29, P-16 0.27, P-15 0.24.

**It is the operator's rule, applied as declared, not a modelling error:**
- D-234 sets the verdict at 0 % denial and D-289 turns the placement off.
- D-626 records U1 under "the gate's conventions (0 % denial, the Standard path, the placement off)".

**What is missing is the reporting beside the verdict** that D-234 and D-289 require of the gate. Program U never
carried it to the user scorecard. So C-1 changes no recorded conclusion under the declared rule. It is a MATERIAL
reporting gap, and a condition on "the money is the contract shape" that the charter should state.

**M-1 overstated.** P-14 stays first under all three models at 10 % and 25 %, and under all-or-nothing at 50 %. The
order flips only at 50 % under per-payout denial.

**M-2.** True in structure. "Milder" holds only if a per-payout p is compared with a per-trader p of the same size.

**Placement on, P near zero: UNSETTLED.** It is an inference from `cons_p14` and the gate's payouts per path. Settling
it needs C's E1: heavy, about 30 replays. Its cost is not on record.

### 2.6 C-M-3, P-14 never stress-read: CONFIRMED, no selection changes

`v1_validation_*.csv` holds only subjects S1 (P-16, seed 20261206) and S2 (FV3-C). P is a real-order replay, so the
independent-day draw does not enter it. What is missing is the robustness of P-14's own gate and bankroll as a product.
C's E2 is the remedy, as a reading.

### 2.7 D-P-2, the budget: CONFIRMED BUT OVERSTATED (a NOTE)

**The arithmetic is right:**
- Program S's batches S1-S4: 0.025 + 0.00833 + 0.00417 + 0.0025 = 0.040 (`search_program*.yaml`).
- Program U's nine families: 0.05 (1 - 1/10) = 0.045.

**But it changes no conclusion:**
- Stage 2 ran a budget per program on purpose. Program S's budget is "across ALL batches" of S; D-621 (5) adopts "program
  S's form" for U.
- No document claims a 5 % across everything the researcher does.
- No level changes; D says so itself: "the defect is the claim, not the number".

**What is worth keeping:** the ledger (R-1) and the sentence that the confirmation decides. The real defect in the
budget is P-1's floor.

### 2.8 D-1, the fill-bar rule: CONFIRMED independently, needs re-declaration

**My simulation** (`rt_fillbar.py`, a new design):
- The same fills are settled two ways, by F-01's bar rules and by the exact one-second path.
- The bias is estimated per fill, as bar outcome minus exact outcome, so its standard error is small.
- Increments are Gaussian or Student-t(3); roughly 17,500-17,700 fills per row.

| scenario (σ in ticks a minute) | share of fill bars reaching a stop | bias, break | bias, fade |
|---|---|---|---|
| σ 35, S 100, R 1 | 0.73 % | -0.16 | +0.14 |
| σ 50, S 100, R 1 | 9.0 % | **-1.73** (se 0.07) | **+1.56** |
| σ 50, S 100, R 3 | 9.0 % | -0.82 | +0.73 |
| σ 50, S 150, R 1 | 0.38 % | -0.08 | +0.06 |
| t(3) tails, σ 35, S 100 | 2.36 % | -0.51 | +0.48 |

Biases are in points of win probability.

**Readings:**
- The sign is as D says: break is biased down, fade up.
- The size is about one fifth of a point per percent of fill bars whose range reaches a stop from the fill.
- On a driftless walk the exact lifts are not zero either: break +0.2 to +1.3 points, fade -0.6 to -2.3. That is the
  booking effect of D-13, also corroborated.
- The `wt/wt-levels` commit 2b6770e reports the same failure independently: T-13, about 470,000 fills a side, has the
  declared rule fail and the pair-plus-symmetric settlement hold. I took this from the commit message and did not
  re-run it.

**How large on NQ: unknown.** The share of fill bars reaching a stop is direction-free and can be read in stage A. At
the 08:30 open in volatile years it could be several per cent, which would put the bias at the size of the value bar
(0.3-2.5 points).

**Why it needs re-declaration:**
- Line 80 is a declared rule, and no reading makes the comparison symmetric.
- The maximum over cells and the choice of a sign are biased toward fade.

### 2.9 D-2, `or30` and the follow effect: CONFIRMED, needs re-declaration

**Line 23 is false.** ORB5's fixed entry is "a stop order at the range's edge", searched over ranges 5/15/30/60 with
`missed_trigger` set to skip, rest or chase (`config/orb5_grid.yaml`). D-266 defines `rest` as "the stop resting at the
level until it next trades through". ORB6 entered by a limit at the broken edge (D-278). F-01's `or30` break is that
design with fixed-point stops and both sides.

**The closed branch.** D-281 (3) reserves "whether any later hypothesis is genuinely different" to the operator.
CLAUDE.md sends no research question to the operator, but this call was reserved to the operator in so many words. So
the safe default is to drop `or30`, record it, and let the operator overrule. That changes the grid, so it is a new
family.

**The follow effect.**
- F-01's break cells at `pd`, `on`, `pdc` and `rn100` take the direction after a level break.
- Stage 2 read that direction three times on this window: weak in 2020-2023 and strong in 2024-2026 (D-580 (5), D-588,
  D-592).
- Stage B chooses on the weak years and stage C judges on the strong ones.
- The minimum response is a reading: a stage-C pass on a break cell is a lead for unread data, not a finding. The clean
  remedy is D's placebo-differenced statistic, which needs a new declaration.

### 2.10 D-3, stage D: CONFIRMED and sharpened, needs re-declaration

**The base is behind R\*.** On the judged block P-16's P is 0.616 against P-14's 0.719, so the tickets must first make
up 0.10. With P-1 fixed, the needed gain is past P = 1 (section 2.3).

**The tickets rarely take the firm.** P-16's router, in `u_xfa_day_budget.csv`, section `signal_supply`, group
`router`, verdict arm:
- 141 offers a path-day, of which 2.6 % are routed;
- refused because an account holds a position: 0.36;
- refused as an opposite position: 0.34;
- refused because no account is flat: 0.27.

The firm is in a position or in its 5-minute cool-down at about 97 % of P-16's marks. A ticket fills at a random moment
and so would almost never take the position. Stage D as declared is P-16 against P-14, and it closes whatever the
tickets are worth.

**The wrong R.** The table's R by state replaces the pick's R. A ticket valued at R = 3 at the funded opening trades at
1-1.5R on most accounts.

**Conduct, item (4), is a reading, not a new family.** Cancel the ticket before placing the P-16 entry; re-publish it
once flat, which D-429's five minutes already require. That is realisable by hand.

**One thing D missed:** the verdict-arm bound for the ticket trades is undeclared (Missed M5).

### 2.11 D-4, D-5, D-6, D-8

- **D-4: CONFIRMED.**
  - MDL = t(29, 1 - 0.05/110) x 0.5 / √n, with t = 3.69: 10.7 points at 300 judged fills.
  - A reading suffices: a close means "no lift above the MDL".
- **D-5: CONFIRMED.**
  - Bars are stamped by their start (`data/README.md:154`; feature-rules lines 14-16).
  - The minute of look-ahead itself is small: the latency is 4 minutes instead of 5, and the 08:25 bar rarely sets an
    overnight extreme or crosses a 100-point line.
  - **The material part is line 58.** It sets the side at `t_live`, so the order type is unknown at publication and
    the void rule (line 75) can never apply. A move across `pd`, `on`, `pdc` or `rn100` between 08:25 and 08:30 flips
    the order type.
  - The reading D proposes (side and levels from the bar stamped 08:24; void at `t_live`) follows section 2, which
    governs. It is enough.
- **D-6: CONFIRMED.**
  - `config/windows.yaml` lines 29-33: NQ's three confirmations are spent (P-05, P-06, P-10); NQ from 2026-07-17
    "becomes NQ's fourth confirmation window only by the operator's decision (D-107)".
  - `DRAFT_P16_confirmation.md` line 28 targets the same window.
- **D-8: CONFIRMED as MINOR.**
  - D-308 (3): at most 5 % "overall, per market and per year". F-01's cutoff already caps the overall share at 5 %, and
    D-621 (3)(iii) catches it at stage D.
  - At stage C a bad year costs a wasted read, not a wrong verdict. It is not a reason to withdraw, but write it into
    the corrected family.

### 2.12 D-P-3, D-P-4, D-P-5: CONFIRMED

- **Spot-checked:**
  - `tests/test_stage2_identity.py:21` skips when the data are absent.
  - Seed 20261901 is `user_drivers.CLUSTER_SEED` (line 71).
  - The judged block was read by nine program-U families and by program S's span guard (D-578 (2), D-580).
- **Not checked one by one:** D's other holes (P-5). On inspection they are true as described.

### 2.13 Track E

- **C1 (the news windows): CONFIRMED; MINOR for results.**
  - The BLS 08:30 file covers CPI, PPI and the Employment Situation.
  - P-14 "enters none and holds none across a release" (D-534 (2)), and P-16's cut removes every report-day entry
    before 07:35.
  - What is left is the 07:35:00 edge. D-533 (3) books entries at a bar's open, so an entry at the 07:35 mark is at
    07:35:00. If the firm's window "7:25 to 7:35" includes that second, full-size MNQ is capped at 3 micros (Combine) or
    1 micro (XFA below $2,000).
  - Safe default under an E-row: the first report-day entry strictly after 07:35:00.
- **C2: CONFIRMED; MINOR.** The citation is corrected under an E-row.
- **N1 (automation): CONFIRMED and UNDERSTATED.**
  - DIRECTIVE Part 1 states the hard limit with the reason "it gets prop accounts banned". The firm's pages (8284197,
    11187768) say otherwise: bots are allowed in the Combine and the XFA; HFT and orders placed from a VPS are not; the
    API is not available on Live and costs $14.50-29 a month, a purchase.
  - The limit is why D-266's L = 5 is the verdict latency. Under it, Stage 2's only program-S candidate to pass all
    four guards (D-588, at L = 0) closed (D-592, at L = 5).
  - The limit remains the operator's to keep. The operator should know that its stated basis is not a firm rule.
- **N2 (Terms of Use s.8): CONFIRMED and UNDERSTATED.** "Substantially (i) larger position sizes compared to your other
  trades" describes the whole state table, not only the funded opening:
  - the opening is the full 20-micro allowance at 3R (`u_xfa_day_budget.csv` `opening_trade`);
  - the evaluation asks $2,000 at 1.5R;
  - most later funded and paid trades are $250 at 1R: about 10 micros at P-14's 12.5-point rung, 5 at 25 points and 3
    at P-16's 37.5 points.
  - It also attaches to the charter's named source of value: spending an edge on the funded opening (CHARTER section 1).
  - Neither `config/rules.yaml` nor `RULES_LEDGER.md` contains the sentence, though the ledger quotes the September 21
    Terms of Use. So it may be new since Stage 2's read (UNSETTLED; the earlier text is needed).
  - D-145's tiers are the operator's, so its tier and pricing are the operator's to decide.

## 3. What all five tracks missed

**M1. The declared confirmation cannot confirm P (CHANGES-A-CONCLUSION for exit criterion (A)).**
- F-01 declares at least six months of NQ from 2026-07-17. Six months gives about 126 sessions, so about 63 starts with
  63 sessions left: one block.
- D-621's bootstrap then degenerates (`rt_cal2.py`). With n = 63 there is one possible block start, the spread is zero,
  and the limit equals the point, so any positive difference "holds". With n = 70-126 the bootstrap's sd is 0.007-0.010
  against an iid standard error of 0.036-0.045.
- No statistic is declared for confirming P anywhere: not in CHARTER section 5, F-01 section 6 or D-621 (3).
- Stage 2's P-16 draft confirms the gate's growth (at least 126 walked sessions, `DRAFT_P16_confirmation.md` line 28),
  not P.
- So exit (A) would confirm a design carried on P either on another measure or by a test that cannot fail. On top of
  this the window is NQ's fourth (D-6) and is wanted for P-16 too.
- Operator's: the length, the purchase, the D-107 decision. The lead's: declaring what is confirmed before any read.

**M2. Fixing P-1 closes Track 2 on this judged block.**
- Both B and D require line (i) to be calibrated. Calibrated, the 80 % MDD for a design whose trades differ from P-14's
  is 0.31-0.34 (section 2.3): a judged P of at least 1.03.
- Only near-P-14 variants and contract-shape changes with large effects can carry. F-01's stage D cannot carry on any
  base other than P-14's.
- No track puts the two findings together. The operator should hear it as one sentence: the corrected program is a
  P-14-tuning program unless power is added, by a second fold, more history (QuantConnect NQ from 2009, which needs the
  operator's token, or a Databento purchase), or a same-base design.

**M3. The remedy and the full rule have not been calibrated.**
- The batch-means t is 1.6-2 times its level on a realistic null (section 2.2).
- The conjunctive rule ((i) to (iv) and (4)(e)) has never been measured as a whole.
- T-6 should test the whole rule against nulls of that kind.

**M4. The signal-service framing collides with a tier-1 prohibition.**
- CHARTER section 4 ("a signal service's users trade by hand") and F-01 line 28 ("the form suits a signal service")
  propose subscribers placing the same published tickets.
- Topstep's 10296582 forbids "Coordinated trading -- performing trades in concert with others (including unconnected
  accounts or third parties) to ... trade the same or opposite strategy simultaneously". Terms of Use s.27 adds
  "(i.e., performing the same trades in the same time increments)".
- Stage 2's ledger records "no coordination with other people" (`rules.yaml` lines 1065-1067, 1098-1100). DIRECTIVE
  Part 1 forbids "copying one trade across accounts".
- Track E quoted both clauses but did not connect them to the product. A single user's backtest is unaffected; the
  product framing is not. The operator's decision.

**M5. Stage D's verdict-arm bound for the tickets is undeclared.**
- The charter shifts every R's outcome to its bound. F-01 does not say which trades, which block or which era rule
  bound the tickets.
- Illustrative arithmetic, not a result: with about 600 fills and a per-trade sd of about 1R at R = 1, the 95 % bound
  sits about 0.07R below the mean. A 5-point lift in win probability is worth about 0.10R.
- So at the bound most of a modest lift disappears before routing (D-3) removes the rest. The corrected family must
  declare it.

**M6. C's m-6 (the breakeven move) is under-graded.** Every P-14, P-15 and P-16 trade contains a stop moved to entry
at session opens; it is the exit on 1-12 % of walks. Stage 2's tier-1 list names "auto-breakeven", and article
10305426 names "auto-breakeven to take advantage of favorable SIM fills". It is probably not that practice (a move by
hand, with a tick of cost), but it is a tier-1 wording match inside R\* itself and is declared nowhere. It needs a
reading by the rules-verifier and a ruling by the operator, not a MINOR.

**M7. F-01's k accounting has already moved.** D's condition R-6 (i) is "no committed code of the family". Branch
`wt/wt-levels` (2b6770e) now commits a `DECLARED_F01` walker preset, and a smoke identity ran on 10 real days. From
`identity/walker_identity.py` line 5 and 314-334, it used P-16's entries only, no F-01 level. No F-01 data has been
read, but the condition as D wrote it is no longer met. Decide now:
- the conservative route: spend k = 10 and declare the corrected family at k = 11 (0.05/132, about 2 % on C1's MDL);
- or record why committed code without a read does not count.

## 4. Who decides

**The operator's** (each changes the objective, the selection rule, a rule the operator set, or is a purchase):
1. Whether the user verdict stays at 0 % denial with the placement off (D-234, D-289): C-1, M-1, M-2. The lead adds the
   readings beside it either way (below).
2. The objective, as DIRECTIVE Part 3 states it.
   - P against money-weighted or bankroll-limited measures (B-4).
   - P at a bankroll B as co-primary or as a constraint; guards on dollars at months 6 and 12 (B-6).
3. S3c as the screening target, also in DIRECTIVE Part 3 (B-1). The red team proposes: within one trade stream only.
4. The guards as non-inferiority tests, and S5a in dollars (B-5): a selection-rule change.
5. How to buy power (B-3, M2): both folds as a selection rule; history from 2009 (the operator's QuantConnect token,
   or a Databento purchase); or accept that only large effects can carry.
6. The confirmation (D-6, M1): NQ from 2026-07-17 as NQ's fourth confirmation (D-107), shared with P-16's; its length
   (six months is one 63-start block for P); the purchase.
7. `or30` inside the closed ORB branch (D-2; D-281 (3)). The safe default, dropping it, is applied meanwhile.
8. The no-automation limit, now that its stated reason is known not to be a firm rule (E-N1).
9. The tier and pricing of the Terms of Use s.8 sizing clause against the state table (E-N2), and of the breakeven move
   (M6).
10. The signal-service framing against Topstep's coordinated-trading prohibition (M4).

**The lead's to fix** (a modelling or procedural error with a clear correction; each under an E-row):
1. **Recalibrate line (i)** (B-2 / P-1, B-7) so the code delivers the declared level 0.05/(k(k+1)). For example: a
   centred, studentised bootstrap with many more draws, or a t on batch means with a conservative adjustment. Add the
   whole-rule calibration test with structural nulls (M3). Report the consequence for power to the operator (item 5
   above).
2. **Report beside every user reading:**
   - the denial ladder, the placement-on reading and the binding FTP models (C's E1);
   - P by month, mean net, CVaR10 and P at $2,000 / $2,500 (B-6);
   - n_eff, the MDD before any read, and the bootstrap's centre against the sample (B-3, B-7);
   - the month-boundary diagnostic (B-6, B-8).
3. **Withdraw F-01 and declare the corrected family:**
   - D-1: the pair rule and symmetric booking, already built on `wt-levels`; K5 reported.
   - D-2: `or30` dropped by safe default; break cells read as a lead, or judged by a placebo-differenced statistic; a
     prior-exposure section; line 23 corrected.
   - D-3: a paired comparison on the same base, P-14's base for 25-point picks, the pick's R, cancel and re-publish.
   - M5: the tickets' bound declared.
   - D-5: side and levels from the bar stamped 08:24; void at `t_live`.
   - D-8: 5 % per year.
   - D-15: the parameter table, with A's 12.5-point cut re-argued.
   - The k decision (M7).
   - What a confirmation tests (M1).
4. **Protocol and tests:**
   - D-P-2: the ledger, and the sentence that the confirmation decides.
   - D-P-3: a prior-exposure section in every family file.
   - D-P-4 and D-P-5: the identity refuses rather than skips (T-11), unique seeds (T-12), T-13 and T-14.
5. **Rules readings:** report-day entries strictly after 07:35:00, and D-530's corrected basis (E-C1, E-C2).
6. **Run V1 on P-14 (C's E2)** as a reading. It decides no selection.

## 5. What I tried that found nothing, and what I could not check

**Tried, nothing found:**
- **The 2025 government shutdown in the BLS calendar.** `releases_bls_0830_2009_2025.csv` holds the rescheduled dates:
  September's CPI on 2025-10-24 and September's Employment Situation on 2025-11-20.
- **Rebills against the month-end readings.** `lockstep.py` lines 1588-1603 put the k-th rebill at purchase + 1 + 21k.
  So no rebill of a month-1 purchase lands by session 21, and the readings do not sit on a billing edge.
- **Track E's N4 against the engine's credit for a payout pending at a breach.** 8284233 ("the funds are transferred
  immediately", as quoted in `rules.yaml`) is consistent with that credit.
- **The boundary between the choice and judged blocks.** `u_select.block` (lines 266-283) drops the last 63 starts of
  2023, so no start straddles it.
- **My bootstrap** reproduces the file's paired row exactly.

**Could not check:**
- NQ's own share of fill bars reaching a stop, which sets D-1's size (it needs the bars; it is direction-free, in stage
  A).
- P with the placement on, under the FTP, or under denial with closures (C's E1, heavy).
- The realised level of the whole conjunctive rule (it needs cell-level start rows for the guards).
- Whether Terms of Use s.8's sizing sentence was in the September 21 text (it needs the earlier text: the web, through
  the rules-verifier).
- Whether 07:35:00 is inside the firm's window (its page is silent).
