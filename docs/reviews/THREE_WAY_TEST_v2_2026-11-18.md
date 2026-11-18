# Red-team read 2: the three-way test's design note after corrective cycle 1 (Q-153r, 2026-11-18)

**Target.** `docs/plans/THREE_WAY_TEST_design.md`, `docs/plans/scripts/three_way/three_way_arith.py` and
`tests/test_three_way_design.py` on `wt/wt-verify` at d8e95de. Line numbers are the note's at that commit unless
another file is named.

**Scope (the coordinator's).**
- A full re-read of B-1 to B-4.
- A diff check of the thirteen minor findings.
- The new material:
  - the Hoeffding and McDiarmid decision;
  - the smaller-J rule;
  - the shared-path law;
  - (Y)'s overlap-sized bound;
  - n_min = h\*;
  - the key tags and the fold.
- Not raised again, as settled: CHARTER 3.7's wording (E-210) and Q-16 in the ledger (E-211).

**Labels.** Each finding is labelled **blocking** (it could make a result wrong; a full re-read follows) or **minor**
(fixed and diff-checked; E-207).

---

## Verdict: H3's declaration can be drafted from this note once one definition is added (N-1)

- **The four first-read blocking findings are closed.**
- **One new blocking finding** sits in the new material: what 2.2 (a)'s Hoeffding/McDiarmid branch admits, and where
  its per-unit ranges come from. As written, a range read from data, or a conditional share, would make the deciding
  bound invalid.
- **The fix is one paragraph** in 2.2 (a). The declaration may carry it verbatim. Under E-207 that paragraph gets a
  full re-read, and the rest of the note does not.
- **Nine minor findings** follow, two of them notes. Each can be fixed in the note or carried into the declaration's
  text.

---

## The first read's blocking findings, re-read in full

- **B-1 (the race): closed.**
  - 1.1 (lines 77-90) states p = min(l, c) / (min(l, c) + g) with the loss min(l, c). This is the vendored
    `BinaryDraw`'s settlement `race` (`vendor/stage2/propedge/contract/adapter.py:112-119, 138-139`).
  - The DP toys use it (2.4, line 348).
  - The oracle holds in exact fractions over a grid of (l, g, c) (`test_the_race_redraw_has_zero_expectation_at_every_cushion`).
    It also shows the unraced form's edge g (l - c) / (l + g) exactly where l > c.
  - What remains is costs (N-5, minor).
- **B-2 (`P_B`): closed.**
  - 1.2 cites `docs/MEASURES.md` at wt/wt-user 9842e10 rather than paraphrasing it. That commit exists, and its lines
    205-208 define ahead-under-B by `max(0, -min_{j < 21m} rel_u[j]) <= B`.
  - "Before the first payout" survives only as the named sub-reading.
  - The wallet reading is kept beside.
- **B-3 (the joint law): closed for H3.**
  - 1.6 declares one shared driftless path for overlapping positions.
  - Until the template defines overlap, the runner refuses any design that holds two of the user's positions at once.
    Under D-429 (one position at a time across a firm), that means a design across firms.
  - The baselines are single-firm, so the refusal does not touch them.
  - What remains (N-3, N-4) is deferred material and minor.
- **B-4 (the t's branch): closed.**
  - Every dimension is clipped (1.3), and no t decides in any branch (2.2, line 311).
  - "Certified" is gone. 2.6 now says what E-052's criterion can detect, and Appendix A prints the rejection count at
    which it fails, the multiple of the level it detects half the time, and the n for "no laxity beyond 2x".

**Arithmetic re-derived for this read.**
- Hoeffding's one-sided bound for n independent terms in [-1, 1] is mean - sqrt(2 ln(1/alpha) / n).
- Its power formula, Phi((sqrt(n) delta - c_h) / sigma_u) with sigma_u <= 1, is correct. So is the sufficiency of
  n >= ((c_h + z) / delta)^2.
- McDiarmid's LB = estimate - sqrt(ln(1/alpha) x sum c_u^2 / 2) is correct, given valid c_u. For P alone (one weight,
  unit cap width, r = 1) it reduces to Hoeffding's, as the note says.
- The two-group orthant values in Appendix A's (Y) lines agree with 1/4 + asin(rho) / (2 pi).
- The three-group "strict majority is one half whatever the correlation" follows from the sign symmetry.

## The minor findings, diff-checked

- **Adequate:** m-1 to m-3 and m-6 to m-13. Each answer is where section 0 says, and the text matches.
  - The run plan now carries H7 under both bounds and D3's full-J check.
  - H_g = 504 is pinned, with its counts printed.
  - "Its noise" is coin noise, with history variation beside.
  - The test holds the prose's counts to the script.
- **m-4 is answered but not fully closed:** N-8.
- **m-5 is answered but not fully closed:** N-9.

---

## New findings

### N-1. 2.2 (a) does not say which dimensions it admits, or where r_d comes from. **Blocking.**

- **Where.** Lines 282-298. "Every dimension a mean or a share" is admitted. Its bounded difference is
  c_u = sum_d w_d 2 r_d / ((hi_d - lo_d) n_d), "where r_d is the dimension's per-unit range".
- **What goes wrong.** McDiarmid's inequality is valid only if every unit truly moves the statistic by at most c_u.
  Two readings of the text break that:
  1. **r_d estimated from data.** Suppose the pinning row reads r_d off the search years (the observed spread of
     net cash at month 3, say). A held-out unit outside that range then moves the composite by more than c_u. The
     bound is then too high, by an unknown amount. Most per-unit values in MEASURES.md have no natural a priori bound
     narrower than contract arithmetic: dollars, sessions, and per-unit ratios such as (15)'s 12-month net over peak
     out-of-pocket, whose denominator can approach zero.
  2. **"Shares" that are conditional, and ratios of means.** Examples are (10), the share falling back among those
     who reached break-even, and (31), payouts per funded account. One unit's change moves such a dimension by about
     1 / (the size of its denominator set). That set is random and can be small, so no fixed c_u holds. The same
     applies to CVaR10 (a tail mean, quantile-type).
- **Remedy (one paragraph in 2.2 (a), or verbatim in the declaration).**
  - 2.2 (a) admits a dimension only if it is an **unconditional mean over all of E_{h_d}** of a per-unit value **with
    a priori bounds** [a_d, a_d + r_d].
  - Those bounds come from contract arithmetic or the verified rules, or from a per-unit clip written into the
    dimension's definition (pinned in 3.9's row, shown to the operator with the caps). **They are never estimated from
    data.**
  - Conditional shares, ratios of means, tail means and quantiles go to 2.2 (b).
  - The build asserts every per-unit value inside its bound and refuses the run otherwise.
  - A unit-count share (an indicator over all of E_{h_d}) qualifies as written, with r_d = 1.

### N-2. 2.2 (a) is valid only under choice 3, and the conflicting reading is left open. **Minor.**

- **Where.** Lines 197-201 and 271-272. MEASURES.md 1.4's reading 3 (9842e10, line 145) still says that under one
  seed every start shares the same coin draws.
- **What goes wrong.** If the lead rules for MEASURES.md's reading, or a build follows it, the J x |E| terms are
  dependent within a seed. Hoeffding's n is then about J, not J x |E|, and its LB is far too high.
- **Remedy.**
  - State in 2.2 (a) that it applies only under choice 3, and that under shared calendar draws only (b) is valid.
  - Have the build assert that every coin key carries the start.
  - The lead rules before the declaration.
- **Why minor.** The note pins choice 3 and names the conflict.

### N-3. The copy-against-stagger check's pass rule points the wrong way. **Minor.**

- **Where.** Lines 238-244: "their composite difference ... must shrink with the stagger".
- **What goes wrong.**
  - Under the declared shared path, staggering the N trades makes their holding intervals overlap less. Disjoint
    stretches of a driftless path are independent (line 223). So the X-against-Y difference **grows** with the
    stagger, from zero toward the fully independent case. That growth is real time-diversification on one path.
  - What should shrink with the stagger is the gap between the shared-path law and the per-trade independent keying.
    They agree once the stagger exceeds the holding time.
  - As written, a correct build fails the check, and a build that ignored the path would pass it.
  - "Bit-identical at zero stagger" is tautological if X and Y run through one code path.
- **Remedy.**
  - Pass when, at zero stagger, X and Y are bit-identical **through separate code paths** (the copy routine and the
    stagger routine).
  - The X-against-Y difference must be non-decreasing in the stagger.
  - The shared-path-against-independent gap must fall to coin noise once the stagger exceeds the longest hold.

### N-4. The shared path on a lattice can re-create B-1's edge; it is keyed per instrument; and "overlap" is circular. **Minor** (overlapping designs are refused for now).

- **Where.** Lines 214-232.
- **What goes wrong.**
  - **The lattice.** "A symmetric walk on a lattice that divides the barriers" assumes such a lattice exists. A
    cushion is in dollars. Divided by the tick value times the size, it is generally not a whole number of ticks, and
    several positions' barriers need not share a lattice.
    - If the walk's cushion barrier is placed at the next lattice point beyond c, and the loss is then clipped at c
      (the engine's `np.maximum(pnl, -cushion)`), B-1's edge returns, in a smaller form.
  - **The key.** It carries the instrument. MNQ and NQ are one underlying, so two paths would give fake
    diversification again.
  - **The circularity.** A lone position keeps the run's exit time. Positions in an overlapping set take the path's.
    Whether two positions overlap depends on which exit time is used.
- **Remedy (for the template, recorded now).**
  - Round every barrier inward to the lattice, so the clip never binds.
  - Extend the zero-expectation oracle to the path, per position, at fractional cushions.
  - Key one path per underlying.
  - Define overlap on scheduled entries and the run's exit times, once, before any draw.

### N-5. The race oracle is cost-free; with costs, the clip can absorb a floor-touching loss's exit cost. **Minor.**

- **Where.** Line 82 ("Costs are added on top"), and the oracle test (zero costs only).
- **What goes wrong.**
  - A trade that races the cushion and loses has a loss of c plus costs, which is below the floor. The engine then
    clips at -cushion, so the exit cost of exactly the trades near the floor disappears.
  - That is a small but systematic credit to designs that trade near the floor.
  - I could not confirm how the vendored `RandomDraw` nets costs against the cushion.
- **Remedy.**
  - Race the barrier at c less the trade's exit costs, so the clip never binds.
  - Extend the oracle: with costs, every trade's net expectation equals minus its costs, at every cushion.

### N-6. The smaller-J rule needs delta\*, which does not exist when H3-A runs. **Minor.**

- **Where.** Lines 307-308 and 675-677. H3-A runs before Wave 4.2. delta\* is the operator's, set in Wave 4.2 (4.1).
- **What goes wrong.** The rule "the smaller J for power pi\* at the sigma / delta measured on H3-A's toys" cannot be
  applied at the real delta\* in H3-A. A rule applied at a placeholder delta can choose differently from one applied
  at the operator's. Validity is unaffected: both bounds are exact, and the choice reads no held-out data.
- **Remedy.** Either:
  - apply the rule in H3-D, at the pinned delta\* and H4's search-year sigma; or
  - declare the placeholder delta now and state that the choice is final.

### N-7. (Y) is vacuous more often than it is labelled, and n_min = h\* makes it vacuous where it need not be. **Minor.**

- **Where.** Lines 523-538 and 558-559; Appendix A's (Y) lines.
- **Evidence (the note's own arithmetic).**
  - At h\* = 63 with n_Y a strict majority of three groups, the stated size is one half whatever the correlation.
    That is no better than one sign, but it is not labelled vacuous, because "vacuous" means one group only.
  - At h\* = 252, n_min = h\* leaves one group (size one half).
  - A calendar-only n_min of 21 keeps two groups, whose white-noise size Appendix A prints below one half.
  - The stated rationale for n_min = h\* ("a group spans at least one horizon of starts") has no inferential role now
    that the groups are declared not to be history blocks.
- **Remedy.**
  - Label (Y) or (R) **vacuous whenever its stated size is at least one half**, and print that label.
  - Propose n_Y = all of Y_ok.
  - Choose n_min by calendar arithmetic, before any read, as the value that minimises (Y)'s stated size at the
    composite's h\*; or give a reason for h\* that the size arithmetic does not contradict.
  - The white-noise figure is correctly called a lower bound (Slepian: positive dependence raises orthant
    probabilities). Keep that word next to it wherever it is printed.

### N-8. Fixed-length keys can still collide: numpy splits integers of 2^32 and more into words. **Minor.**

- **Where.** `three_way_arith.seed_key` and `stripped` (script lines 92-109); 1.5 (lines 189-191): "no two keys can
  coincide once their trailing zeros are stripped".
- **Evidence (checked).**
  - `default_rng([7, 2**32 + 5])` is the same stream as `default_rng([7, 5, 1])`.
  - `default_rng([7, 3, 2**32])` is the same stream as `default_rng([7, 3, 0, 1])`.
  - So a coin key whose moment is written in milliseconds or nanoseconds since an epoch (2^32 and more), with draw
    kind 0, equals a key of the same kind with a small moment and a draw kind equal to the big moment's high word.
  - `stripped` compares integers, not the 32-bit words numpy reads, so the test cannot see this.
- **Remedy.**
  - `seed_key` refuses any field, and the seed, at 2^32 or more. Moments are session indices and minute offsets.
  - Or compare `SeedSequence(key).generate_state(4)` in the guard.
  - Add the refusal to the key test.

### N-9. The arithmetic fold's reach is narrower than its prose. **Minor.**

- **Where.** Lines 782-788; test lines 278-323.
- **Evidence (checked on synthetic sources).**
  - `_fold_scan` reads only files containing the characters "2026". A source whose arithmetic folds to the block's
    prefix without those digits is found by `_fold_hits` but never scanned.
  - `**`, augmented assignment (`x += ...`) and tuple unpacking (`A, B = ...`) are not folded.
- **Remedy.**
  - Drop the prefilter, or widen it to any integer literal.
  - Add `Pow`, `AugAssign` and tuple targets.
  - Or say in section 7 that the static fold is a tripwire and the build's run-time assertion (lines 786-788) is the
    guard.

### N-10. The key test builds keys under a design-check seed. **Minor** (note).

- `test_the_seed_key_trap_and_the_fixed_length_keys` uses the block's H3-A coin seed as a key value. Nothing is drawn,
  but it blurs section 7's roles.
- Use the tests' own seed.

### N-11. Under clipping, theta depends on n. **Minor** (note).

- E[clip(plug-in)] is not clip(E). So 2.2 (a)'s estimand at a clipped composite moves with J near a cap.
- It is pinned with J, so validity holds. Say it beside the verdict with the share at a cap.

---

## What I tried that found nothing

- **The B-1 grid oracle**, read against the vendored `BinaryDraw` docstring.
- **The `P_B` citation**, against the wt/wt-user commit.
- **Hoeffding's and McDiarmid's forms and constants**, Appendix A's Hoeffding n and J lines (recomputed for one
  delta), and the H7 rows' arithmetic.
- **The orthant formulas and the (Y) correlations' form** (window-mean weights on i.i.d. per-session contributions).
- **Exactness of the S1 stream-swap symmetry.** It is a law-preserving involution acting within a day.
- **The E-052 arithmetic.** The fail-at-x form and the half-power multiple are consistent with the Clopper-Pearson
  limits.
- **No held-out read added.** H3-A reads no bar. H3-D reads the search years. n_min comes from the calendar only. v(t)
  uses closed bars only.
- **The test file.** It passes run alone (15 tests). Its new tests can fail on a wrong constant, a typed count or an
  unraced redraw.

## What I could not check

- **How the vendored `RandomDraw` nets costs against the cushion** (N-5).
- **Whether any baseline's run holds two positions of the user at once** (B-3's refusal). D-429 suggests none does.
  H1's identity run would show it.
- **MEASURES.md's final reading 3** after the lead's ruling (N-2).
