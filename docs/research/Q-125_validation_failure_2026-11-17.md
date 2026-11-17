# Q-125: why `cons_m1.25` failed its validation -- a diagnosis by the failure protocol (2026-11-17)

**Status:** a read-only research note (Q-125, E-159). Nothing was rerun. No development outcome was read. The only
computation beyond reading result files is a small synthetic replica. It uses seed **12512501**, role "the replica's
synthetic populations", which is outside the program's 2026xxxx space. Its script is in Appendix A, so anyone can
reproduce it.

**Number rule.** Every figure below is one of three things:
- a column of a named result file (`results/q108_*.csv`);
- arithmetic on the plan's declared constants: 657 sessions, L, the levels 0.05/(k(k+1)), and the t quantiles at the
  members' degrees of freedom;
- a qualitative description of the replica, which can be reproduced from Appendix A.

**Premise dropped (the lead's correction, after the auditor's F1).** E-159 described the failing null as having "few
non-tie sessions, heavily clustered". This note does not use that description. It tests it in section 3.1 as one
hypothesis among several, and rejects it.

---

## The question

The separate validation run of Q-108 failed (E-159). On one exact null, `sub:5000:05:win1:flip63`, the chosen
`cons_m1.25` in scope Q rejects above nominal at k = 13 to 18. This note asks five things:
1. What is this null?
2. Why did the calibration pass the statistic?
3. What drives the breach?
4. What could a new plan declare, and what would each option cost in power?
5. Does E-094's earlier failure share the cause?

## The answer, in a few sentences

**The cause is the subset lottery of the plan's own section 1, and nothing else.** On the judged block, a 63-session
sign-flip null has only 11 or 12 independent signs per phase. The aligned sign pattern alone carries 100 units of the
exact denominator 63 x 2^12 (arithmetic on declared constants). That is 1.41 to 3.26 times the family level at k = 13
to 20.

So the margin of 1.25 keeps a subset safe only when that subset's quarter-block sums are uneven enough. Subset
`sub:5000:05` has, for its `win1` values, quarter sums even enough that the aligned and near-aligned patterns clear 1.25
times the critical value:
- its count at k = 13 is above the whole aligned mass;
- the same subset is the validation's worst null under every persistent side model (tied under markov30).

**The calibration passed it because a rare bad subset is easy to miss.**
- The calibration's 115 subsets did not contain such a subset.
- The guards the plan used could not exclude a bad-subset rate of the size needed to fail a validation. That
  validation has zero tolerance across 1,150 fresh exact subset nulls.
- Condition 3 (worst ratio at most 1/4) bounds how bad the calibration's worst subset was. It does not bound how bad
  an unseen subset can be.

**Rejected explanations:**
- **Few non-tie sessions.** The failing subset has the most traded sessions of its size.
- **A variance-estimator defect fixable by CR2 or Bell-McCaffrey.**
- **A construction bug** (the auditor found none, and the pattern across side models rules one out).

**The synthetic replica (section 3.2) agrees.** Using the module's own exact enumeration on synthetic `win1`-like
trades, it reproduces over-rejection by `cons` and by `cons_m1.25`. The rate rises steeply with a per-trade drift and
with the trade count, and falls with the margin but never to zero. CR2/Bell-McCaffrey changes nothing, and scope D
never rejects.

**Confidence:** high (about 0.9) on the mechanism, and medium on its source within the data. Whether the subset's even
quarter sums come from P-16's drift (E-035 note 8) or from subset noise alone cannot be settled without reading
outcomes. That is section 6's open item.

**E-094's failure shares the cause.** It was the same construction (5,000 trades, `win1`, 63-session flips) and the
same mechanism. Its Q-83 audit diagnosed exactly this, at a rate of the order of 2^-11.

**For a new plan, ranked:**
1. **Scope D,** the margin with the outcome-free runs admission. It costs no minimum detectable lift on admitted cells,
   but it covers fewer cells. Best combined with item 2's sized calibration (section 4, option 3).
2. **A larger margin, m >= 1.5.** It costs about 19 % more lift than m = 1.25 at m = 1.5, and more beyond. **It needs
   a calibration of thousands of exact subsets, not 115.**
3. **Small-cluster corrections, a session floor, or an exact or permutation test.** These do not address the cause.

---

## 1. What this null is (terminal state)

### 1.1 Construction, from the plan and the code

**The name.** `sub:SIZE:J:VALUE:MODEL` is `scripts/q108_calibrate.py:816` (`null=f"sub:{z}:{j:02d}:{v}:{m}"`). Here
it is z = 5000, j = 5, `win1`, flip63.

**The trades.**
- A subset of z of P-16's judged offers, drawn without replacement by `default_rng([seed_subsets, z_index, j])`
  (`scripts/q108_calibrate.py:746-749`, `:808`).
- On the validation block the entropy is [20262122, 4, 5], as the auditor checked against the plan's 4.1.
- Each trade carries `win1 = 0.5 x ((kl_1 == 1) - (ks_1 == 1))`, the pair difference at 1R (`:729`). So a trade
  contributes -0.5, 0 or +0.5.
- The trades are summed per session into V_j (the sum) and N_j (the count) (`dataset`, `:768-773`).

**The side model.**
- A sign is drawn per L = 63-session flip block at phase p (`extended/lift_one_sample.py:618-621`, Q-16's
  `_flip_signs`). Every trade of a session takes its block's sign.
- At 657 sessions a phase touches B = 11 blocks at 37 phases and 12 at 26 (`flip_cells`, `:630-634`; plan section 1).

**What "exact" enumerates** (`exact_flip`, `extended/lift_one_sample.py:676-771`): every phase p in 0..62 and every
sign pattern q in 0..2^B - 1.
- Each cell is weighted 2^(Bmax - B) over the denominator L x 2^Bmax = 63 x 2^12 = 258,048 (`:690-691`, `:706`).
- An 11-block cell counts 2 units and a 12-block cell 1 unit.
- The size is the weighted share of rejecting cells. **It is the size conditional on that subset's fixed trades, with
  no Monte Carlo error.**

**The statistic.** `cons_m1.25` rejects when all three members reject:
- `t21w`, `t42w` and `t63w`, each a CR1 trade-weighted t on `lift_bound.block_index` blocks with df G - 1;
- the blocks are G = 657 // b: 31, 15 and 10 blocks, so df 30, 14 and 9 (`extended/lift_bound.py:88-93`);
- each rejects when est - 1.25 x t(1 - a; df) x se > 0 (`lift_one_sample.py:331-341`).

The test blocks (about 65.7 sessions for b = 63) do not coincide with the flip blocks (63 sessions at phase p).

**Ties and "non-tie sessions".**
- On a flip null every trade of a session shares one sign, so a session's net side is zero only when it has no trade.
- The size file's `nontie_sessions_mean` on an exact null is therefore the number of traded sessions:
  `"nontie_mean": float(ds.traded.sum())`, `scripts/q108_calibrate.py:1165`.
- Tied *outcomes* (x = 0, both brackets won or both lost) are ordinary zero contributions to V_j. They are not
  dropped, and the plan's admission does not see them.

### 1.2 Its terminal state, from the files

`results/q108_val_size.csv`, null `sub:5000:05:win1:flip63`, `cons_m1.25`, scope Q:
- `denominator` is 258,048;
- `count_k13..count_k20` are 110, 97, 77, 64, 56, 40, 22 and 17;
- `ratio_k13..k20` run from 1.55 down to 0.55;
- `trades_mean` is 5,000;
- `nontie_sessions_mean` is 573;
- in scope D, `count_k*` is 0 at every level (`admitted_share` 0).

**The level in units.** The level times the denominator is about 70.9 units at k = 13 and 30.7 at k = 20
(arithmetic). So the null fails at k = 13 because the statistic rejects 110 units where at most 70.9 are allowed.

---

## 2. Why the calibration passed it (stage decomposition)

### 2.1 The calibration held nulls of exactly this form

Both blocks drew 23 subsets at each size, including 5,000, each run at `win1` and `net3` under flip42, flip55 and
flip63 exactly (the plan's 3.2). So the calibration had 23 nulls of the identical form `sub:5000:JJ:win1:flip63`. Their
`cons_m1.25` scope-Q ratios (`results/q108_cal_size.csv`):
- every one is at or below 0.141 at k = 13;
- the largest is `sub:5000:13:win1:flip63`, `count_k13` 10;
- the median is 0.

Over all 690 exact flip subset nulls (115 subsets x 2 values x 3 L):
- **calibration:** no `ratio_k13` above 1, none above 1/4, worst 0.197 (`sub:500:11:win1:flip63`, the `q108_choice.csv`
  `worst_exact_ratio`);
- **validation:** one above 1 (the failing null) and four above 1/4.

### 2.2 How close the calibration came, and why "close" was the wrong yardstick

**Condition 3** (the plan's 4.2) required the worst calibration exact ratio to be at most 1/4. `cons_m1.25` had 0.197
and passed.

**But the exact size is a function of the subset's data, and over subsets it is heavy-tailed.**
- In both runs, over the 690 exact flip subset nulls, the median `ratio_k13` is 0 and the 90th percentile is below
  0.01 (computed from the per-subset rows).
- In the validation the maximum is 1.55, about eight times the calibration's maximum.
- A margin below the worst value seen bounds the worst value *seen*, not the tail.

**What the plan's detection requirement could see** (the plan's 3.2):
- It sees a 2 % bad-subset rate with probability 0.9, pooled over sizes.
- The validation criterion fails on **any** bad subset among 1,150 fresh exact subset nulls: 115 subsets x 2 values x
  5 exact models.

**Arithmetic on those counts:**
- Zero bad subsets among the calibration's 115 per model is compatible, at 95 %, with a per-subset bad rate up to about
  3/115, the "rule of three".
- A rate of 1 % goes unseen in 115 subsets with probability 0.99^115, about 0.31. The auditor gave the same figure.
- At a rate r per subset-model, a validation passes with probability about (1 - r)^n, where n is the number of exposed
  subset nulls.
- To pass with probability 0.9, r must be below about 0.1/n. With the flip63 exposure alone (230 subset-value nulls)
  that is about 4.6 x 10^-4.
- **The calibration's 115-subset design could not certify anything near that.**

**The verdict of this stage.** The choice rule was internally sound, and the auditors re-derived it twice. But its
guard against the subset lottery was too weak for the validation's zero-tolerance criterion by roughly two orders of
magnitude in detectable rate. The plan's 4.2 named this risk ("the most powerful candidate that only just clears every
calibration subset is the one most likely to carry a small, unseen bad-subset rate"). Its 1/4 constant was set on
three synthetic populations, and it did not control the risk here.

---

## 3. What drives the breach (the component in isolation)

### 3.1 The hypotheses, each tested

**(H-a) Few non-tie sessions for many trades: few clusters in the session sense. Rejected.**
- `nontie_sessions_mean` is 573 for the failing null.
- Across the 23 validation subsets of 5,000 trades the column runs from 551 to 573, so the failing subset is the
  largest. It is also above every calibration subset of that size, whose largest is 569.
- At 5,000 trades, the rank correlation between traded sessions and a subset's mean exact ratio over the three flips
  (`cons` and `cons_m1.25`, `win1`) is weakly **positive** in both runs, not negative. It is not significant once the
  sizes and values are counted.
- The test's cluster count is fixed by the calendar, not by the trades: 10 test blocks for `t63w` and 11 or 12 flip
  blocks. Traded sessions cannot change it.
- This confirms the auditor's F1 independently, from the same column.

**(H-b) A multiplier too small only in that corner. True as a description, but not a cause.**
- Since 1.5 t(1-a13; df) > 1.25 t(1-a20; df) at df 30, 14 and 9 (arithmetic), every rejection of `cons_m1.5` at any k
  is also a rejection of `cons_m1.25` at k = 20.
- The failing null's `count_k20` for `cons_m1.25` is 17 units, below the k = 20 level of about 30.7 units.
- So **`cons_m1.5` would have held on this null at every k**, by a bound drawn from the file.
- But section 3.2 shows that no finite margin removes the mechanism. A larger margin lowers the bad-subset rate and
  does not zero it.

**(H-c) Something odd in the construction. Rejected.** The auditor found the denominator, the weights, the nesting
over twelve levels, the shared draws and the log all consistent (`docs/audits/Q-108_validation_2026-11-17.md`
section 3). I checked these readings rather than taking them:
- **The aligned mass.** `flip_cells(657, 63)` gives B = 11 at 37 phases and 12 at 26, so the aligned mass is
  37 x 2 + 26 x 1 = 100 units. That is A(63)/level = 1.41 at k = 13 up to 3.26 at k = 20, matching the plan's
  section 1 table. The failing `count_k13` of 110 exceeds it.
- **The subset is the worst everywhere.** In `q108_val_size.csv`, `cons_m1.25`, Q, `win1`, 5,000 trades, subset j = 5
  is the worst of its 23 under flip42 (0.256), flip55 (0.469) and flip63 (1.55). It is also the worst under flip21,
  markov50 and markov80, and tied worst under markov30.
- **The same trades are bad for `cons` on `net3` too.** Under C0 (`cons`) on `net3` at 5,000, j = 5 is also the subset
  with the highest mean flip ratio. For `cons_m1.25` its `net3` flip ratios are 0.
- A bookkeeping error would not be organised by persistence, and consistently by one trade set, like this.

**(H-d) The aligned-pattern atom, the plan's section 1, acting through one subset's even quarter sums. Accepted.**
- On a fixed trade set, an exact flip cell's test-block sums are BS_g = sum_f s_f M[f, g] (plan 3.1).
- At the aligned pattern, s_f = sign of flip block f's sum, every flip block contributes |M_f| with a positive sign.
  The CR1 t of the 63-member is then roughly sqrt(G) times mean/sd of the test-block sums. **It grows without bound as
  the quarter sums become equal, because CR1 subtracts the estimate before squaring and its se goes to zero.**
- Under the conditional sign-flip null that pattern has probability 2^-B per phase. Summed over phases, that is 100
  units, more than the level allows at every k in 13..20.
- So **on any subset whose quarter sums are even enough that all three members clear m x crit at the aligned pattern
  over most phases, the exact size exceeds the level, whatever m is.** The margin only sets how even "even enough" is.
- The failing subset clears it with room. Its 110 units at k = 13 mean the aligned pattern rejects at most phases,
  plus some one-block reversals (H1). As k rises the count falls in lumps, from 40 units at k = 18 to 22 at k = 19.
  That is the signature of whole phases' aligned cells dropping out together.

**(H-e) The t(G - 1) reference with few clusters. True, but it is the same thing as (H-d).**
- With 10 test blocks, `t63w` uses t with 9 df.
- Under the exact flip null the randomisation distribution of the self-studentised t has atoms of mass 2^-11 and 2^-12
  at very large t: the aligned and near-aligned cells.
- The t(9) tail at 10^-4 has no such atoms. So the reference is wrong in the far tail, and wrong precisely there.
- This is "few clusters" in the sense of **few independent sign units (11 or 12) relative to the level**. It is not
  few sessions.
- A variance correction cannot repair it (section 4, option 5).

### 3.2 The synthetic replica (Appendix A; seed 12512501)

**Configuration.** It mirrors the failing configuration:
- 657 sessions;
- 5,000 trades spread over about 560 traded sessions with uneven counts;
- per-trade values in {-0.5, 0, +0.5} like `win1`;
- a per-trade drift delta in some scenarios: P(+0.5) - P(-0.5) = 2 delta, constant, or of a random sign per calendar
  quarter;
- 150 independent synthetic subsets per scenario.

**Comparisons.**
- Scenarios at 500 trades, and at 5,000 trades on only 150 traded sessions, test the trade count and hypothesis H-a.
- Each subset is enumerated exactly at L = 63 with the module's own `exact_flip`, for `cons`, `cons_m1.25`,
  `cons_m1.5`, `cons_m1.75`, `cons_m2`, `cons_bm`, `cons_bm_m1.25` and `cons_im`.
- The aligned pattern's own rejecting mass is computed separately, phase by phase.

**What it shows.** The results are described, not quoted. The figures come from rerunning Appendix A with its seed.
The drift sizes are invented for the replica and are not estimates of P-16's.

1. **It reproduces the failure.**
   - With no drift, `cons` is above nominal on a few of the 150 subsets. `cons_m1.25` is above on none, though its
     worst subset comes within a factor of a few of the level.
   - With a small drift, `cons_m1.25` is above nominal on a few subsets. Its worst exact ratios are of the same order
     as the failing null's 1.55, and larger.
   - So a synthetic population with nothing wrong in its construction gives exactly this failure, on an otherwise
     well-behaved statistic.
2. **The bad-subset rate rises steeply with the per-trade drift, and with the trade count at a given drift.**
   - At 500 trades with the same drift, `cons_m1.25` has no bad subset and `cons` has few.
   - At 5,000 trades both rates rise with every step of drift.
   - This matches both real failures falling at 5,000 trades (section 5). The mechanism is H-d's: a drift makes the
     quarter sums systematically even.
3. **A margin lowers the rate but does not remove it.**
   - At the moderate drifts `cons_m1.5` fails on a few subsets where `cons_m1.25` fails on more.
   - At the largest drift tried, every margin up to 2 has failing subsets.
   - **No finite m is safe in scope Q against an unknown drift.**
4. **CR2/Bell-McCaffrey (`cons_bm`, `cons_bm_m1.25`) and the equal-weight member (`cons_im`) track their CR1
   counterparts closely in every scenario.** The small-cluster corrections do not touch the mechanism.
5. **Few traded sessions is not needed for the failure.**
   - The 150-traded-session scenarios fail at about the same rate as the 560-session ones with no drift, and somewhat
     more often with drift.
   - The real failing subset has the most traded sessions of its class (H-a), so this aggravating factor is not what
     happened here.
6. **A drift whose sign changes from quarter to quarter also produces failures, at a lower rate.** What matters is the
   evenness of the |quarter sums|, not the direction of the market.
7. **Scope D never rejects.** In every subset of every scenario, every candidate's scope-D count at L = 63 is zero, as
   the plan's 4.4 arithmetic implies.
8. **Aligned and near-aligned patterns share the rejecting mass.** On the failing subsets the aligned pattern alone
   carries between about a fifth and all of the rejecting mass at k = 13 (median by scenario). The rest is
   near-aligned patterns (H1).

**What the replica cannot say.** It does not say whether P-16's real per-quarter drift is the size that makes this
common. That would need the per-quarter means of `win1` (section 6).

---

## 4. What a new plan could declare (every item labelled: chosen after this look)

**Under the plan's 7 item 4, a new round:**
- needs a new declaration, new seeds and a new row;
- keeps this plan's null class;
- drops no construction because it failed here.

**What every option is measured against.**
- **Power** is from `q108_choice.csv` `P` (the geometric mean of the toys' MDL80 at k = 13), as a ratio to
  `cons_m1.25`'s. The per-toy MDL80s are in `q108_cal_power.csv`.
- **The operator's rule:** a strict line must show power, not only size, and must not fail profitable models. So
  every cost is a lift a design must exceed, and a design whose true lift falls between two candidates' MDLs is a
  profitable model failed by the stricter one.

### Ranked options

**1. Scope D: `cons_m1.25` (or C6) after the plan's runs admission. Recommended first.**
- **What it does.** It removes the mechanism's domain rather than racing it.
  - A side constant over 63-session blocks has at most 12 runs on 657 sessions, so R >= 13 never admits one (the
    plan's 4.4).
  - Flips at 55, alternating sides and Markov sides are admitted only with enough runs, and on those the aligned
    atom's mass is far below the levels: A(55)/level is 0.48 to 1.10, and admission removes most of it.
- **Evidence, all from files.**
  - **Calibration:** `cons_m1.25` in scope D met all three conditions (`q108_choice.csv`), worst exact ratio 0.042.
  - **Validation:** on the validation draws, beside and deciding nothing, `cons_m1.25` scope D has no failing null.
    Its subset worst ratio is 0.146 (`q108_val_criterion.csv` `beside` rows, scope D, group subset). On the failing
    null its count is 0 (`admitted_share` 0).
  - These validation draws **cannot be reused** as its validation (auditor F2 (b)). A new plan re-runs calibration and
    validation on new seeds.
- **Power cost.** The MDL is identical to scope Q's on every admitted cell: `P` is the same for C1 in Q and D, because
  the toys' coin and daily sides are always admitted.
- **The coverage cost is real, and it is the price.** The plan's 4.4 lists who cannot use the line:
  - sides persistent past about a quarter;
  - long-only and short-only designs;
  - designs with fewer than about 25 to 30 non-tie traded sessions on the judged block;
  - designs balanced in most sessions;
  - any family that does not declare persistence below a quarter.
  Those cells fall to the two-sample forms (E-091) or are not claimed.
- **Why it is the right trade.** For a quarter-persistent side, an exact null on 11 or 12 sign units cannot certify
  any level below 2^-11. **No statistic can give such a design a valid one-sample test at k >= 13.** Excluding it is
  not a loss of power that some other statistic could recover.
- **Scope D with `cons` and no margin is not available.** `cons` in D failed the alternating-model floor at
  calibration (`q108_choice.csv`, worst `alt45` ratio 84), so the margin is still needed.
- **What it needs.**
  - New calibration and validation seed blocks.
  - The scope-D procedure exactly as in the plan's 4.4. It is already built (`lift_one_sample.admission`, `exact_flip`
    scope D).
  - Many more exact subsets, as in option 2.

**2. Scope Q with a larger margin (m >= 1.5), and a calibration sized to the validation.**
- **What it does.** It moves the "even enough" threshold out. On this null m = 1.5 provably holds (section 3.1, H-b).
- **Power cost against `cons_m1.25`** (`P` ratios):
  - m = 1.5: 1.188
  - m = 1.75: 1.377
  - m = 2: 1.567
  The per-toy MDL80s scale the same way (`q108_cal_power.csv`).
- **Why it can still fail.** The mechanism is unbounded (H-d), so at any m some subsets fail. Whether m = 1.5 or 1.75
  brings the rate below what a 1,150-null validation tolerates is an empirical question. The replica's answer is
  above.
- **What it needs.** A choice rule whose detection matches the criterion.
  - Exact enumeration is cheap: 0.2 to 0.4 s a subset at L = 63 in the run log and in the replica. So the calibration
    can enumerate **thousands** of fresh subsets per size at L = 42, 55 and 63.
  - It would require **zero bad subsets among enough calibration subsets to bound the rate below about 0.1 divided by
    the validation's exposed count.** By the rule of three that is about 30 times the exposure: on the order of
    about 7,000 enumerations (the flip63 exposure of 230 alone) to about 35,000 (all 1,150 exact subset nulls): a
    few hours.
  - Without that, a larger m repeats this failure's logic at a different point.
- **Disclosure for this option.** It is the option most exposed to "choosing on the failure". It is admissible only
  with the m grid declared in advance, chosen on new calibration seeds, and validated on others.

**3. Both (scope D with the sized calibration).** Option 1's domain with option 2's tail calibration. This is the most
defensible line. Its power cost is option 1's (none on admitted cells), plus whatever margin the sized calibration
selects in D.
- At calibration, D's worst exact ratios were already small at m = 1.25: 0.042, against Q's 0.197.
- The margin it needs is likely 1.25 or less, but that is the run's to show.

**4. An eligibility floor on non-tie (traded) sessions. Does not address the cause.**
- The failing subset has the most traded sessions of its class (H-a). A floor would have admitted it.
- It costs coverage of sparse designs and buys no size here.
- The plan's scope-D runs threshold already excludes sparse designs as a side effect.

**5. A small-cluster correction: t(G - 1), CR2 / Bell-McCaffrey, CR3 / jackknife, or a wild cluster bootstrap. Does not
address the cause.**
- **t(G - 1)** is already used.
- **CR2/BM.** On near-equal blocks CR2 reduces to CR1 and the BM df to G' - 1. This is the plan's own formula and the
  build's test (plan 2.2, C5). The calibration measured it:
  - `cons_bm` failed the floors, with flip63 worst 1.14 (`q108_choice.csv`);
  - `cons_bm_m1.25` was eligible with flip63 worst 0.155, against C1's 0.197. That is a hair better, at `P` 1.009
    times C1's.
- **CR3/jackknife.** At the aligned pattern with even quarter sums, its leave-one-block-out variance also goes to zero.
  So it inherits the atom.
- **Wild cluster bootstrap** (Cameron, Gelbach and Miller 2008; Webb 2023). With Rademacher weights on 10 to 12
  clusters it has at most 2^G distinct draws, so its p-value cannot fall below about 2^-10 to 2^-12. That is above or
  at every family level, so it has no power. Webb's six-point weights refine the grid, but they cannot remove the
  null's own atom: **any test that rejects the aligned pattern has size at least A(63) on such a subset**. That is a
  property of the null, not of the estimator.
- These corrections fix bias in the *variance* with unbalanced clusters (Imbens and Kolesar 2016; Pustejovsky and
  Tipton 2018). The breach here is in the *randomisation atom*.
- **Power cost:** about that of C1 or C6 (`P` ratio 1.009 for C6), for no gain in size.

**6. An exact or permutation (sign-flip) test. Excluded again, for the plan's reason.**
- At 63-session blocks the smallest attainable p is 2^-10 to 2^-12, above every family level, so the MDL is infinite.
- At 21- or 42-session blocks it is not exact for a 63-persistent side (plan 2.3; Canay, Romano and Shaikh 2017 for
  the approximate-symmetry form).
- A sign-symmetric Hoeffding-type bound on the null-imposed statistic, sum BS_g / sqrt(sum BS_g^2), is valid for any
  independent sign-symmetric blocks (Hoeffding 1963; Efron 1969). But it is at most sqrt(G), about 3.2 at G = 10, below
  the bound's own critical value of about 4.05 at k = 13. **It can never reject at 63-session blocks.** This is the
  same impossibility, stated without a t.

**Not options** (they would weaken the line after the look, as the auditor's F2 lists):
- a narrowed k range (k >= 19);
- the averaged ("flat") size in place of the per-subset size (E-105 (1));
- dropping `win1` or flip63.

---

## 5. Does E-094's failure share the cause? Yes (high confidence)

**The same construction.** Q-83's failing null was `real:thin5000:win1:persist63`:
- P-16's pairs thinned afresh to 5,000 trades, `win1`, signs flipped in 63-session blocks;
- its `bound` (`cons`) was above nominal at k = 11 to 14;
- on Q-16's own subset of the same construction it sat at 0.013 of nominal
  (`docs/audits/Q-83_fresh_seed_validation_2026-11-16.md` sections 3.1 to 3.3).

**The same mechanism, in the audit's words.** "one sign pattern carries probability 2^-11 ... the tail is decided by the
one or two most extreme sign patterns: whether all three members reject when the flips line up with that subset's
block sums". Its rate was about 1.19 x 2^-11 (section 3.3), which is the aligned-atom order found here.

**The same agent.** A fresh subset of the same population makes the size swing (E-094 (1), M2 through the subsets).
Q-108 moved the threshold by 1.25 and met the same lottery one draw further out.

**What the two failures together add.**
- Both fell at **5,000 trades and `win1`**.
- In the validation, the shipped `cons` also has its largest flip63 count above 1/4 at 5,000 `win1`: 7 of 23 subsets
  (`q108_val_size.csv`, the per-subset rows, `cons`, Q, `ratio_k13` above 1/4).
- That is consistent with the larger subsets of a bounded-value stream having quarter sums dominated by something
  systematic rather than noise. Section 6 says what that is and how to test it without breaching the no-outcome rule.

---

## 6. What is unknown, and how it could be found

**1. What makes `sub:5000:05` even.**
- **The candidates.**
  - P-16's pair difference has a drift per quarter: E-035 note 8's drift credit, a random side "leaning with the drift
    in every quarter".
  - Or the subset's noise happened to equalise eleven quarter sums.
- **Why it matters.** At 5,000 trades a drift term grows like z while noise grows like sqrt(z), so a drift makes large
  subsets *systematically* even. The bad-subset rate would then be high at large z and on any market with a steady
  drift, not just a rare draw.
- **What the replica shows.** It separates the two only on synthetic data (section 3.2).
- **What settles it on real data.** The per-quarter sums of `win1` on the failing subset and on P-16's offers. That is
  an outcome statistic of development data. It is **not** for this note. It would be a worker's read, declared with a
  purpose under E-035, or better avoided: a new plan's synthetic drift nulls can carry the drift as a declared
  construction.

**2. The bad-subset rate at each m in each scope.** This is measurable only by the sized exact calibration of option 2
or 3, on new seeds.

**3. Which cells reject on the failing subset** (aligned versus near-aligned, by phase). This needs the subset's trades,
which are not written (the auditor's C1). The plan's exact sample for the scalar re-decision stored only decisions. A
new plan could write, for each exact null above 1/4, its rejecting cells' (p, q) list. That costs nothing and makes the
next diagnosis direct.

---

## 7. If this becomes a new calibration plan: what it would declare

This is a calibration plan, not a family, so CHARTER section 4's contract fit does not apply. It would declare:
- **The mechanism it answers:** the aligned-atom lottery of section 3.
- **The candidates:** `cons_m{1.25, 1.5, 1.75, 2}` and `cons_bm_m1.25`, in scope D and in scope Q, the order fixed as
  before. Q before D is reversed or kept, labelled.
- **The null class:** this plan's, unchanged (7 item 4). Added beside it, labelled as chosen after the look: synthetic
  drift nulls (constant and sign-varying per quarter) at 5,000 trades.
- **The subset count:** sized to the criterion. For each exact model and size, as many fresh subsets as make zero
  calibration failures bound the bad rate below 0.1 divided by the validation's exposed count, by the rule of three.
  The validation exposure is declared too.
- **Seeds:** new calibration and validation blocks, verified unused under the plan's 4.1 guard. The Q-108 blocks
  20262110-20262129 are retired.
- **The cell count:** each candidate x scope x null x k = 13..20, counted as before. No family k is spent: a
  calibration spends none.
- **Its outputs:** the per-null rejecting-cell lists for any exact null above 1/4 (section 6 item 3).

---

## Sources

**Code:**
- `extended/lift_one_sample.py:60-87` (the constants), `:182-201` (`t_crit`), `:216-238` (`cr_parts`), `:311-341` (the
  member bound with margin), `:618-634` (flip blocks, cells), `:676-771` (`exact_flip`);
- `extended/lift_bound.py:88-93` (`block_index`);
- `scripts/q108_calibrate.py:729` (`win1`), `:746-749` (`subset_index`), `:768-773` (`dataset`), `:806-823` (the subset
  nulls' names and entropies), `:1100-1165` (`run_exact`, `nontie_mean`).

**Files:**
- `results/q108_val_criterion.csv` (the `criterion` and `beside` rows);
- `results/q108_val_size.csv` (`count_k*`, `ratio_k*`, `denominator`, `nontie_sessions_mean`, `admitted_share`);
- `results/q108_cal_size.csv`, `results/q108_choice.csv` (`P`, `worst_exact_ratio`, `worst_ratio_flip63`, the
  conditions), `results/q108_cal_power.csv` (`mdl80`);
- the run log `%LOCALAPPDATA%\stage2-extended-runs\q108-validate.log` (the per-null line for this subset: "Q 110 D 0 of
  258048", 0.2 s).

**Documents:**
- the plan `docs/calibration/Q-108_one_sample_plan.md` (sections 1, 2.3, 3.2, 4.2, 4.4, 7);
- the audits `docs/audits/Q-108_validation_2026-11-17.md` (F1, F2, section 3), `docs/audits/Q-108_calibration_2026-11-17.md`
  (C6) and `docs/audits/Q-83_fresh_seed_validation_2026-11-16.md` (section 3);
- the rows E-052, E-091, E-094, E-115, E-127, E-149, E-150 and E-159.

**Literature.** Methods references, cited for what they establish in general. They were not re-read for this note,
except Webb (checked by search, abstract level).
- Bell, R. M. and McCaffrey, D. F. (2002), "Bias reduction in standard errors for linear regression with multi-stage
  samples", *Survey Methodology* 28(2), 169-181 (no stable link verified for this note).
- Cameron, A. C., Gelbach, J. B. and Miller, D. L. (2008), "Bootstrap-based improvements for inference with clustered
  errors", *Review of Economics and Statistics* 90(3), 414-427. https://doi.org/10.1162/rest.90.3.414
- Canay, I. A., Romano, J. P. and Shaikh, A. M. (2017), "Randomization tests under an approximate symmetry assumption",
  *Econometrica* 85(3), 1013-1030. https://doi.org/10.3982/ECTA13081
- Efron, B. (1969), "Student's t-test under symmetry conditions", *JASA* 64(328), 1278-1302.
  https://doi.org/10.1080/01621459.1969.10501056
- Hoeffding, W. (1963), "Probability inequalities for sums of bounded random variables", *JASA* 58(301), 13-30.
  https://doi.org/10.1080/01621459.1963.10500830
- Imbens, G. W. and Kolesar, M. (2016), "Robust standard errors in small samples: some practical advice", *Review of
  Economics and Statistics* 98(4), 701-712. https://doi.org/10.1162/REST_a_00552
- Pustejovsky, J. E. and Tipton, E. (2018), "Small-sample methods for cluster-robust variance estimation and hypothesis
  testing in fixed effects models", *JBES* 36(4), 672-683. https://doi.org/10.1080/07350015.2016.1247004
- Webb, M. D. (2023), "Reworking wild bootstrap-based inference for clustered errors", *Canadian Journal of Economics*
  56(3), 839-858. https://doi.org/10.1111/caje.12661 (working paper: Queen's Economics Department WP 1315,
  https://ideas.repec.org/p/qed/wpaper/1315.html; abstract level). Its finding: wild cluster bootstrap-t p-values are
  not point-identified with few clusters, and a six-point weight distribution helps.

---

## Appendix A: the replica's script (seed 12512501; synthetic only; light, about 15 minutes on one thread)

Run as `python q125_replica.py <repo root> <reps> <out.csv>`, with OMP_NUM_THREADS=1.

```python
"""Q-125 scratch: a synthetic replica of the `sub:SIZE:J:win1:flip63` exact null. Seed 12512501 (role: the replica's
synthetic populations; outside the program's 2026xxxx space). No real data is read."""
import sys, time
import numpy as np, pandas as pd
sys.path.insert(0, sys.argv[1])
from extended import lift_one_sample as O

SEED_REPLICA = 12512501
REPS = int(sys.argv[2]) if len(sys.argv) > 2 else 150
n, L = 657, 63
NAMES = ("cons", "cons_m1.25", "cons_m1.5", "cons_m1.75", "cons_m2", "cons_bm", "cons_bm_m1.25", "cons_im")
CANDS = [O.candidate(c) for c in NAMES]
LV = O.FAMILY_LEVELS_1S
# (label, trades z, traded sessions T, drift delta per trade, drift sign varies by quarter)
SCEN = [("A z5000 T560 d0", 5000, 560, 0.00, False),
        ("B z5000 T560 d.01", 5000, 560, 0.01, False),
        ("C z5000 T560 d.02", 5000, 560, 0.02, False),
        ("D z5000 T560 d.03", 5000, 560, 0.03, False),
        ("E z500 T300 d.02", 500, 300, 0.02, False),
        ("F z5000 T150 d0", 5000, 150, 0.00, False),
        ("G z5000 T150 d.02", 5000, 150, 0.02, False),
        ("H z5000 T560 d+-.02", 5000, 560, 0.02, True)]

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

def aligned_mass(V, N):
    """weighted (units of 1/den) rejecting mass of the aligned pattern alone, per candidate and k"""
    Bs, _ = O.flip_cells(n, L); Bmax = max(Bs)
    out = {c: np.zeros(len(LV), dtype=np.int64) for c in NAMES}
    for p in range(L):
        fid, B = O.flip_blocks(n, L, p)
        VS = np.bincount(fid, weights=V, minlength=B)
        s = np.where(VS >= 0, 1.0, -1.0)[fid]
        low = O.evaluate((s * V)[:, None], N[:, None], LV, cands=CANDS)
        for c in NAMES:
            out[c] += (2 ** (Bmax - B)) * (low[c][:, 0] > 0)
    return out

rows = []
t0 = time.time()
for si, (lab, z, T, d, var) in enumerate(SCEN):
    for r in range(REPS):
        rng = np.random.default_rng([SEED_REPLICA, si, r])
        V, N = draw(rng, z, T, d, var)
        ex = O.exact_flip(V, N, L, LV, cands=CANDS, n_first=0)
        al = aligned_mass(V, N)
        for c in NAMES:
            num = np.array(ex.num[(c, "Q")]); numD = np.array(ex.num[(c, "D")])
            ratio = num / ex.den / np.array(LV)
            rows.append(dict(scen=lab, rep=r, cand=c, traded=int((N > 0).sum()),
                             **{f"r{k}": ratio[i] for i, k in enumerate(O.K_RANGE_1S)},
                             al13=int(al[c][0]), num13=int(num[0]), D13=int(numD[0]), den=ex.den))
    print(lab, round(time.time() - t0, 1), flush=True)
df = pd.DataFrame(rows)
df.to_csv(sys.argv[3], index=False)
g = df.assign(over13=df.r13 > 1, overany=df[[f"r{k}" for k in O.K_RANGE_1S]].max(axis=1) > 1, over20=df.r20 > 1,
              alshare=np.where(df.num13 > 0, df.al13 / df.num13.clip(lower=1), np.nan))
s = g.groupby(["scen", "cand"], sort=False).agg(over13=("over13", "mean"), overany=("overany", "mean"),
                                                over20=("over20", "mean"), med13=("r13", "median"),
                                                max13=("r13", "max"), alshare=("alshare", "median"),
                                                Dmax=("D13", "max"))
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 200)
print(s.round(3))
```
