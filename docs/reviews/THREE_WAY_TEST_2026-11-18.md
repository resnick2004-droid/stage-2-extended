# Red-team read: the three-way test's design note (Q-153r, 2026-11-18)

**Target.** `docs/plans/THREE_WAY_TEST_design.md`, `docs/plans/scripts/three_way/three_way_arith.py` and
`tests/test_three_way_design.py`, on `wt/wt-verify` at 2650ac6 (worktree
`%LOCALAPPDATA%\stage2-extended-wt\wt-verify`). Line numbers are the note's at that commit unless another file is
named.

**Context read.** CLAUDE.md. The amendments draft (`docs/plans/AMENDMENTS_draft_2026-11-18.md`, CHARTER 3.2 and
3.5-3.9), because E-210's text has not landed on master: master's CHARTER.md does not yet carry the amended 3.x. Also
E-207, E-208 and E-209 in `DECISIONS.md`. Also Stage 2 D-145 and D-150, `vendor/stage2/propedge/contract/adapter.py`,
`extended/family_stats.rng_of`, `scripts/q108_calibrate.py`'s fold guard,
`docs/reviews/MEASURES_2026-11-18.md`, `docs/MEASURES.md` at wt/wt-user 3467f12, and
`docs/research/calibration_2026-11-15.md`.

**On the brief.** The brief lists nine points to attack and names the choices the note itself flags (its Appendix B).
I treated that list as a floor, not a frame. Two of the four blocking findings below (B-1, B-2) are outside it.

**Labels.** Each finding carries E-207's label: **blocking** (it could make a result wrong) or **minor**. It also
carries a severity: CHANGES-A-CONCLUSION, MATERIAL, MINOR or NOTE.

---

## Verdict: **must be re-declared** (revised before H3 is declared)

- **Four blocking findings.**
  - Two are in the deciding reading's definitions that the note fixes: the redraw's odds (B-1) and the fallback's
    per-journey value (B-2).
  - One is in the seed keying's joint law (B-3).
  - One is an escape branch in the deciding statistic (B-4).
- **What is right.** The note's statistical core holds:
  - Maurer and Pontil's theorem 4 is applied correctly, one-sided at alpha, with the range mapped back exactly.
  - The antithetic twin is exact.
  - The history null's exactness argument is right for any functional.
  - The fixed-sequence argument is right.
  - E-208's correction is right.
- **What must change.** What the statistic is applied to, and two definitions underneath it, must change before
  H3's declaration takes its rules from this note.

---

## Findings, by severity

### B-1. The redraw's win probability l / (l + g) ignores the floor race: a free edge for stops beyond the cushion. **Blocking.** CHANGES-A-CONCLUSION

- **Where.**
  - The note, lines 40-41 (and 177): "a target of g ticks and a stop of l ticks give a win probability of
    l / (l + g)", called "stage one's `adapter.BinaryDraw` form".
  - The engine: `vendor/stage2/propedge/contract/adapter.py:112-119` and `:138-139`. BinaryDraw's settlement is
    `race`, which races the nearer barrier handed in as `cushion`, the room above the floor (D-156, D-150: "which
    keeps the floor barrier race"). After that the engine clips `np.maximum(pnl, -cushion)`.
- **The failure it allows.**
  - Take a trade whose stop l exceeds the account's cushion c. Its driftless first exit is at the nearer barrier, so
    its win probability is c / (c + g), not l / (l + g).
  - A build that draws at l / (l + g), and then clips the loss at -c (as the engine does), has a gross expectation of
    g (l - c) / (l + g) > 0 on that trade.
  - That is a positive edge. It is largest for wide stops near the floor, which is exactly the account-policy region
    the search explores: sizing by distance to drawdown, the last trade before an MLL breach.
  - A design that trades near the floor more often than the baselines gains composite from it, and can pass on it.
  - The antithetic and disjoint nulls cannot see this: the error is identical in both arms of a same-design pair.
  - The DP toys (2.4) would reproduce it too, if they take the formula from 1.1.
- **Remedy.**
  - Write the redraw as the race of the nearer barriers: win at `U < min(l, c) / (min(l, c) + g)`, with a loss of
    `min(l, c)` plus costs. Do the same with the daily-loss room where it applies (the engine's own `cushion`). A
    trade with several accounts at different cushions then has a per-account p (see B-3).
  - Make the DP toys use the same p.
  - Add an oracle test: with zero costs, every trade's redrawn gross expectation is zero at every cushion, checked
    exactly on a grid of (l, g, c).

### B-2. The fallback's per-journey value carries the bankroll-stop definition the MEASURES read found wrong. **Blocking.** CHANGES-A-CONCLUSION

- **Where.**
  - The note, lines 66-70: `a(x, t, s)` counts month m ahead only if `spent_m <= limit`, "spent_m is the cash spent
    before the first payout as month m's reading reads it".
  - `docs/reviews/MEASURES_2026-11-18.md:73-95` (B-2) found exactly this reading lets a design take a fast small
    payout and then outspend the budget.
  - The corrected `docs/MEASURES.md` (wt/wt-user 3467f12, lines 197-204) defines `P_B` by the **peak out-of-pocket
    through the month close**. It keeps "before the first payout" only as a named sub-reading beside.
- **The failure it allows.**
  - The pinned fallback is the pass line when the weights cannot be set (CHARTER 3.9).
  - Built from this note, it would count as ahead a start whose spending after the first payout exceeded the budget.
    That error favours multi-account, high-purchase designs over the baselines.
- **Remedy.**
  - Define `a(x, t, s)` with `PeakOOP` through close 21m, citing MEASURES.md's `P_B` by section, not paraphrasing it.
  - If Wave 3.1's bankroll stop halts purchases at the budget inside the journey, say which of the two readings is
    then redundant, and keep one.

### B-3. The seed keying fixes the joint law of redraws across concurrent trades, and gets it wrong both ways. **Blocking.** MATERIAL

- **Where.** Section 1.5, lines 109-121: kappa = (seed, start day, decision moment, draw kind). "Two arms deciding at
  the same moment ... read the same uniform." Nothing says whether the account or the firm is in the key.
- **Evidence.** CHARTER 3.2 fixes only each trade's marginal (its bracket's first-exit odds). The key decides the
  joint law:
  - **Trades opened at different moments whose holding intervals overlap** read independent uniforms. Examples: the
    same user's accounts staggered by a minute, or a second component entering while the first is open, which 3.5's
    open-position rule forces to the same side.
    - On the real path, two same-side positions open together on NQ are strongly positively dependent.
    - Independent redraws make them independent: fake diversification.
  - **Trades opened at the same moment with different brackets** (account sizes, or stops in volatility units with
    different caps) read one uniform at different thresholds: a comonotone coupling.
    - A single driftless path allows both "A wins, B loses" and "B wins, A loses" for nested brackets, and the
      comonotone coupling forbids one of them.
    - That overstates dependence.
- **The failure it allows.**
  - Take design X, which copies one trade to N accounts at one moment, and design Y, which staggers the same N trades
    across a few minutes on the same path.
  - Under this keying they have different composites, through ruin, CVaR10 and P under the bankroll stop. On a real
    path their difference is small.
  - The search rewards "lowering the correlation between accounts" (CHARTER 3.4), so it will find the stagger. The
    test then credits a difference that the zero-edge convention manufactured.
  - The baselines, run under the same keying, do not share the artefact to the same degree.
- **Remedy.** Declare the joint law of redraws for any set of the user's positions whose holding intervals overlap,
  before H3. Candidates:
  - (a) **Path-consistent.** One driftless tick walk per (seed, start, session), scaled by the real path's causal
    volatility, with every overlapping bracket's exit read from it. The resolution times stay "as run" only for the
    first-opened trade.
  - (b) **Conservative.** One shared uniform for every trade opened while another of the user's positions is open
    (comonotone). This is an upper bound on the dependence, and penalises diversification rather than rewarding it.

  Whichever is chosen, add an H3-A check: the X-against-Y pair above on a toy, whose composite difference must be
  zero under (a) by construction, or of the declared sign under (b). Also state in 1.5 that the side coin's key
  carries neither account nor firm (see m-9).

### B-4. The t's escape branch is never needed, and its size at alpha cannot be certified. **Blocking.** MATERIAL

- **Where.**
  - Lines 167-169: "If the pinning row cannot bound the composite, ... the t with the larger-of rule then decides,
    and its size at alpha rests on the size check of 2.6 at feasible levels only."
  - Lines 271-278: the check's criterion is E-052's.
- **Evidence.**
  - **Every composite can be bounded.** g_d acts on the functional's value Phi_d, not on the per-journey values, so
    `clip((Phi_d - lo_d) / (hi_d - lo_d), 0, 1)`, with caps from the search years, bounds any dimension. The
    weights are then a convex combination.
  - **So the branch opens only by choice.** The choice would be made after H3-A has shown the pinning author that the
    t needs far fewer seeds (Appendix A's ratio, and much more on the range term; see m-1).
  - **The branch's size rests on a check that cannot certify alpha** (the note says so). E-052's criterion (no 95 %
    Clopper-Pearson interval wholly above nominal) also passes a test lax by a factor of two at the rule-of-three n.
    For example, at alpha' = 0.05 with 59 tests, about six rejections give a lower limit below 0.05.
  - Calling such a level "certified" (line 275) overstates it.
- **The failure it allows.** A deciding t at a level about 1/3640 of a pass, with skewed replicates on the held-out
  history, and a size nobody can check.
- **Remedy.**
  - Delete the branch: the composite is clipped by construction, and the pinning row states the caps.
  - Rename "certified" in 2.6 to "no laxity detected". Define certification, if wanted, as the Clopper-Pearson upper
    limit at most a declared multiple of alpha', with the n that gives that power.

### m-1. The empirical-Bernstein bound's power is range-dominated, and the note's headline cost understates it by orders of magnitude. **Minor.** MATERIAL

- **Where.** Lines 161-165 ("the price of exactness is a larger J ... their ratio"), 226-237, and Appendix A's
  `replicates per (sigma/delta)^2 ... ratio` line.
- **Evidence (the note's own formula).**
  - The variance term needs J of about (c1 + z)^2 (sigma / delta)^2. The range term needs J of about
    2 c2 R / (share x delta), and it does not shrink with sigma.
  - A per-seed replicate on P is a mean over hundreds of starts, so sigma is small against R = 1. The range term then
    sets J.
  - With sigma near delta, the variance term asks for some tens of replicates, and the range term for thousands to
    tens of thousands (Appendix A's own `range term` lines). The ratio that matters is then the range-J over the
    normal-t J, not the printed variance ratio.
  - My synthetic check of the note's power formula, at assumed sigma and delta of the same small size and k = 13,
    gave zero power at J = 1000 and full power at J = 5000.
- **What it means.**
  - "Seeds are unlimited, so that price is paid in compute" holds only if the compute is there. The held-out test's
    own run (J x m seeds x five arms x |T| x h x tau) and D3's full-J check are not in the run plan.
- **Remedy, in order of value.**
  1. **Use the independence the note already builds.** Under choice 3 (each start its own keys), given H the
     per-(start, seed) terms d_{t,s} = a(f, t, s) - a(beta, t, s) are independent across starts and seeds, each in
     [-1, 1].
     - For the fallback, and for every mean or share dimension, Hoeffding's inequality over all J x |T| terms is exact
       given H, with no identical-distribution premise: LB = Delta-bar - sqrt(2 ln(1/alpha) / (J |T|)).
     - It needs about |T| times fewer seeds than the per-seed EB bound in the range-dominated regime.
     - A Bernstein form with a declared variance bound, or McDiarmid for bounded-difference composites, extends it.
       Quantile dimensions keep the per-seed-set bound.
  2. Compare the hedged betting bound with EB on H3-A's toys, and pick the deciding statistic by a rule stated before
     H3-A (the smaller J for power at the declared sigma / delta). 6.1 (lines 552-553) says H3-A "choose[s] the
     build's statistic among 2.2's candidates", while 2.2 says EB decides; make them agree.
  3. Add the held-out test's own cost and D3's full-J cost to Appendix A's run plan.
  4. State that J is fixed before the read and never extended after it (EB is not anytime-valid; the betting form
     is).

### m-2. Clipping changes the composite the operator weights, and can saturate. **Minor.** MINOR

- **Where.** Lines 140-144.
- **Evidence.**
  - Caps from the search years can be exceeded on the held-out years. Both arms then saturate and Delta goes to zero:
    power is lost, size is not.
  - A clipped g_d is non-linear, so the operator's trade-off answers (Wave 4.2) are answers about the clipped
    composite.
  - Censored dimensions (sessions to first payout when most starts never pay) need a declared value of Phi before
    clipping.
- **Remedy.**
  - Show the clipped normaliser to the operator in Wave 4.2.
  - Pin a cap margin.
  - Report beside the verdict the share of seed sets with any dimension at a cap.

### m-3. (Y) and (R) can degenerate, and their blocks are not the history blocks of 3.1. **Minor.** MATERIAL

- **Where.** Lines 409-427, 397-402, 351-366.
- **Evidence.**
  - "A full year ... meets 3.1's length" (lines 410-411) is true only for full years. The last year with complete
    starts is always a partial block of starts shorter than h\*, except at h\* = 63:
    - at h\* = 252, 2025's complete starts end in mid-2025;
    - at h\* = 126, 2026's are a handful.
    The note admits such a block "held to n_min like any other", contradicting 3.1.
  - At h\* = 252, the start-year blocks' windows overlap massively: 2024's starts' windows cover most of 2025, which
    is all of 2025's starts' outcome sessions.
    - The two "years" are close to one history, so (Y)'s stated size is near 1/2, not the 1/4 of the independent
      table.
    - With an n_min above 2025's count, Y_ok has one year, and (Y) is the overall sign again.
  - (R)'s regimes interleave in time: a calm start's window holds volatile days. So (R) is not a split into history
    blocks. R_ok can also hold one regime if the held-out years sit mostly on one side of the search years' v\*.
  - (Y) reads "every dimension on its own complete starts within T_y" (line 415), a different start set per
    dimension from leg (i)'s T_{h_d}.
- **Remedy.**
  - Print, beside every verdict, |Y_ok|, |R_ok| and whether each condition is vacuous.
  - Compute the conditions' stated size on the actual Y_ok and R_ok with the overlap, as 3.3 (4) plans.
  - Fix n_min by calendar arithmetic only, never from held-out regime counts: computing |T_r| needs held-out bars.
  - Define v(t) on bars closed before the start's first decision moment (bar stamps are open times).
  - Drop "meets 3.1's length" or restrict it to full years.

### m-4. Seed keys: numpy strips trailing zeros, so the key-shared guard can pass while two streams coincide. **Minor.** MATERIAL

- **Where.**
  - Section 7, line 622: `rng_of(seed, part, history r, arm a, replicate j, ...)`.
  - Line 206: "any key shared between the S sets and the S' sets (checked on the key lists, not on outcomes)".
  - `extended/family_stats.py:109-111` (`default_rng(list(key))`).
- **Evidence.**
  - My check: `default_rng([a, b, 0, 0])` gives the same stream as `default_rng([a, b])`, while `[a, 0, b]` differs
    from `[a, b]`.
  - This repository has recorded the same trap before (`docs/reviews/BUILD_F-03_v2_2026-11-16.md:164`,
    `DRAFT_F-RL3_2026-11-18.md:294`).
  - The note puts histories, symmetry coins and coin fields under one role seed (A3, D2). So a history key
    (seed, part, r) and a coin key (seed, part, r, 0, 0) would draw the same stream.
  - Separately, kappa (line 111) carries no part and no history index. If two histories (or D1 and D3, which share a
    role seed) use the same seed indices, they read the same coin field. The R per-history size tests are then not
    independent, and 2.6's pooled count (line 275) overstates n.
- **Remedy.**
  - Make every key fixed-length per role, with a leading kind tag, and never zero-pad.
  - Compare keys after stripping trailing zeros, or better compare `SeedSequence.generate_state` outputs.
  - Put the history index and the part into every coin seed's derivation, or state that sharing is intended (P1's
    shift on D1's nulls).

### m-5. The derived-seed guard misses the test file's own derivation of the block. **Minor.** MINOR

- **Where.** Lines 650-658; `tests/test_three_way_design.py:31-32`.
- **Evidence.**
  - I re-pointed `q108_calibrate`'s fold at the block and ran it on the test file: it folded **no** expression, yet
    the file builds all ten seeds by arithmetic.
  - The fold tracks only names bound directly to an integer literal. It does not follow a name bound to an
    expression (`P = a * b + c`), nor fold pure-literal expressions, nor string concatenation. A plain `NAME + const`
    was refused, so the guard works on its own pattern.
  - "No refusal" therefore shows the block is free of that one pattern, not of derivations.
  - The repeating test (line 656) is literal-only, so a future file that derives a block seed passes it.
- **Remedy.**
  - Say so in section 7.
  - Have H3's build read its seeds from one module whose name the repeating test allow-lists, and assert at run time
    (in `RetiredSeedMap`'s manner) that every `rng_of` call's first word in the block comes from that module.

### m-6. "A history acts on a journey only through its schedule" is asserted, not tested. **Minor.** MINOR

- **Where.** Lines 245-253 (Appendix B item 9).
- **Evidence.**
  - The deciding reading's per-trade state does depend on history beyond times, brackets, resolution and cost:
    - the cushion (B-1) is state, so the schedule is enough only if the journey state is replayed;
    - R-10's time-limit redraw may read the volatility left to the flatten;
    - the news calendar (no maximum size into major news, tier 1) gates trades;
    - Stage 2's gate campaigns settle with `mae` (`vendor/stage2/config/fv2_grid.yaml:85`), which reads the
      intra-trade path on the as-walked reading.
  - S2 at h\* = 252 has only about four disjoint blocks in the search years, so its "histories" are few
    recombinations of the same blocks.
- **Remedy.**
  - Give the build a typed interface (journey = f(schedule, coin field, rules)).
  - Add an exact test: two different real-bar paths with the same schedule give bit-identical journeys on the
    deciding reading.
  - Enumerate the schedule's fields (including a news flag and the volatility R-10 needs).
  - Report S2's count of distinct blocks.

### m-7. The proposed starting null class for 3.1's intervals is a held-out read. **Minor.** MINOR

- **Where.** Lines 364-366: "`results/calibration_p.csv`'s null classes (real paired start-day nulls ...) are the
  starting null class".
- **Evidence.** Q-16's real nulls are the judged block's paired series (`docs/research/calibration_2026-11-15.md`
  lines 12, 49, 144): 2024-01-02 to 2026-07-16, the held-out years.
- **Remedy.**
  - Use search-year paired series or the synthetic classes only.
  - Enter Q-16 (E-035, E-083, E-085) in the held-out read ledger of CHARTER 3.6 (b), which does not name it today.
  - The intervals decide nothing, which is why this is minor.

### m-8. The antithetic twin is right; the charter's words should follow it. **Minor.** NOTE

- **Where.** Lines 173-192; CHARTER 3.7 (draft line 347): "(every coin side reversed)".
- **Evidence (checked).**
  - U\* = 1 - U on the odd-multiple grid is exact and law-preserving, so (C(U), C(U\*)) is exchangeable and Delta is
    symmetric with mean zero, for any bounded functional.
  - Reversing a redrawn outcome instead would map p to 1 - p: the note is right that this is a defect.
  - 3.5's forced side (a new trade takes the open position's side) is a function of earlier uniforms, so the twin
    stays exact. The note should say so.
- **Remedy.** In the row that applies E-210's text, or a later one, read CHARTER 3.7's parenthesis as "every draw's
  uniform complemented (each coin side reversed; no redrawn outcome is ever reversed)".

### m-9. Choice 3 (each start its own coin draws) is consistent with CHARTER 3.5, and should be kept. **Minor.** NOTE

- **Evidence.**
  - 3.5's candidate default is "one literal coin draw per moment, shared by all **the user's** accounts and firms". A
    start is one user, so independent users are the literal reading.
  - Sharing across starts is not required by 3.5, and it would make every start of a seed one correlated sample.
  - The condition is that the side coin's key carries no account and no firm index. Then one user's accounts at one
    moment share it, as 3.5 asks. The note does not say this.
  - Choice 3 is also what makes m-1's per-(start, seed) bound available.
  - For quantile dimensions the estimand theta_m(H) depends on the keying across starts as well as on m, so the
    keying is pinned with m.
- **Remedy.** State the account/firm exclusion in 1.5, and pin the keying with m.

### m-10. The history null: exact as stated; its "per finalist" pairs and the mirror on S1 need a definition. **Minor.** MINOR

- **Where.** Lines 290-339.
- **Evidence (checked).**
  - With D'(H) := D(sigma H), the coin keys mapped, and sigma law-preserving and start-set-preserving,
    E_H C(D'; H) = E_H C(D; H) holds for any functional, quantiles included.
  - theta_pair(sigma H) = -theta_pair(H) for an involution.
  - The S2 symmetry is exact because sigma flips each block's declared coin, whatever mirroring does to overnight
    gaps.
- **But:**
  - S1 is schedule-level, so a price mirror is not defined on it. A schedule-level symmetry (two exchangeable trigger
    streams) must be named.
  - "The finalist's own components wherever the generator can carry them" leaves the per-finalist rate's pair
    unspecified. The session swap needs every rule alike in both sessions, which a real finalist with components in
    both sessions does not meet.
  - The pass-probability shortcut plugs in theta-hat from M = 500 seeds on a steep curve.
- **Remedy.**
  - Name the S1 symmetry.
  - Label each FPR_hist row with the pair actually used, flagging "stylised" where it is not the finalist's.
  - Report the shortcut's error against the full-J subset.

### m-11. E-208's correction is right; H_g is unpinned and matters. **Minor.** MINOR

- **Evidence.**
  - floor(W_H / 63) from the weekday upper bound is ten, and the B_min arithmetic is correct. So "at most ten"
    stands, and the conclusion holds a fortiori.
  - "Eleven counting a partial one" (line 384) is a typed figure the script does not print.
  - D-145's gate horizon: Stage 2's gate campaigns declare `horizon_days: 504`
    (`vendor/stage2/config/fv2_grid.yaml:85`, `fv3_corrected_portfolio.yaml:192`). At 504 sessions:
    - the held-out years hold at most W_H - 503 complete starts;
    - not a single disjoint 504-session block beyond the first, so 3.8 (c)'s "history-block resamples" for the
      gate's quantile cannot be formed on the held-out years;
    - the search years lose a 504-session strip to 3.6 (d)'s purge.
- **Remedy.**
  - Pin H_g in H3's declaration, citing D-145's config.
  - Add 504 to the script's `HORIZONS`.
  - Print the counts.
  - State that the gate's held-out quantile is over coin seeds only, or read it on the search years.
  - Have the script print the partial-unit count, or delete "eleven".

### m-12. "Its noise" in the limit clause. **Minor.** NOTE

- **Evidence.** With coin noise only, w shrinks as 1 / sqrt(J). At the J that m-1 implies, the clause becomes a
  point-estimate check on the held-out history. With history variation (3.1's per-horizon variance) the margin is
  wide, and the power gate's limit clause will likely stop every pin (O-5's caveat).
- **Remedy.**
  - The coin-only reading matches the level's scope (conditional on H) and keeps power. History variation belongs
    with FPR_hist, printed beside.
  - It is the operator's under O-5. Fix it in the pinning row before any read, and print the other beside.

### m-13. The arithmetic test can fail, but it tests agreement, not correctness. **Minor.** NOTE

- **Evidence.**
  - `test_appendix_a_is_the_scripts_output` fails on any edit to the note's block or the script. The level
    assertions fail if k, the dates or the horizons move. The planted-seed control works. The file passes (seven
    tests, run alone).
  - But a wrong constant (ln(1/alpha) for ln(2/alpha), say), edited into the script and the note together, passes.
  - The prose figures ("ten", "eleven", "twelve") are not held to the script.
- **Remedy.** Add a Monte-Carlo coverage test of `eb_constants` at a feasible alpha, and assert the prose counts
  against the script's values. My own small check found the bound valid (no exceedance at alpha = 0.05 on skewed
  Bernoulli replicates at J = 5, 20 and 200).

---

## What I tried that found nothing

- **Theorem 4.**
  - The form mean + sqrt(2 V ln(2/delta) / n) + 7 ln(2/delta) / (3 (n - 1)) is one-sided at delta, with the unbiased
    V.
  - The lower bound by Z -> 1 - Z is correct, and the map from [0, 1] to [-R, R] gives exactly line 149's terms.
  - The power formula of line 228 follows with V near sigma^2.
  - Appendix A's c1, c2, factors, ratio, range-J and rule-of-three n recompute.
- **The replicates' independence given H.** Disjoint seed sets with distinct keys give an i.i.d. Delta_j, whatever
  the dependence across starts (subject to m-4's key collisions).
- **The intersection-union and the fixed sequence.** Strong FWER at most alpha given H. The conjunction with the time
  conditions cannot raise it.
- **The antithetic grid.** It is exact in float64; `U < p` against its complement is exact by the grid's symmetry.
- **The history null's algebra** (m-10).
- **Look-ahead or held-out reads in H3-0, H3-A and H3-D.**
  - None reads a held-out session.
  - H3-A reads no bar.
  - H3-D reads the search years only.
  - The held-out calendar is used only through weekday counts.
  - The exceptions found are m-7 (a past held-out read reused) and m-3 (n_min must not be set from held-out regime
    counts).
- **E-208's "about a dozen".** "At most ten" is right on both the weekday bound and Q-16's recorded session count.
- **The seed table.** Ten distinct roles; deciding seeds undrawn before H3-D; the repeating literal scan, with its
  positive control, works.

## What I could not check

- **The actual sigma of the replicates.** H4 is not run, so m-1's J is shown only as orders of magnitude.
- **Whether Wave 3.1's bankroll stop halts purchases inside the journey**, which bears on B-2's redundancy.
- **R-10's time-limit redraw form**, which m-6 and the DP toys depend on.
- **The counter-based generator the build will use**, beyond `rng_of`.
- **E-210's final charter text** (not landed). I read the amendments draft.
