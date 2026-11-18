# Red-team read 3: the three-way test's design note, final text (Q-153r3, 2026-11-18)

**Target.** `wt/wt-verify` at 181eb44: `docs/plans/THREE_WAY_TEST_design.md`,
`docs/plans/scripts/three_way/three_way_arith.py` and `tests/test_three_way_design.py`. Line numbers are the note's
unless another file is named.

**Scope (the coordinator's).**
- A full read of N-1's admission paragraph: 2.2 (a), lines 341-381, between the `2.2a-admission` markers.
- A diff check of N-2 to N-11 against section 0's cycle-2 table (lines 73-87).
- The coordinator's three points:
  - whether item 2 (i)'s bounds are sufficient and exact;
  - the bounded differences of unit-count shares and of `P_B` under choice 3;
  - the race with costs, L = min(l, c - x).

**Labels (E-207).** **Blocking** means it would make a result wrong. Corrective cycles are spent, so a blocking finding
would go to NEEDS_OPERATOR. **Minor** means fixed in the declaration's text.

---

## Verdict: **H3's declaration can be drafted from this note.** No blocker stands.

- N-1 is closed. The admission paragraph is valid as written for every dimension it admits.
- Four minor points (M-1 to M-4) should be carried into the declaration's copy of the paragraph and of 1.1. None of
  them makes a pass wrong. Each either tightens the wording or turns a possible refused run into a defined outcome.
- N-2 to N-11 are answered adequately.
- The test file passes when run alone (19 tests).

---

## N-1, the admission paragraph, read in full

**What it admits (item 1), and whether McDiarmid's premises hold.**
- Every admitted dimension is Phi_d = the mean over all J x |E_{h_d}| units of a per-unit value x_d(u).
- E_{h_d} is fixed by the calendar and shared by every arm and seed. x_d(u) depends on the held-out history and on unit
  u's own coin field only.
- Under choice 3 (item 5), the units' coin fields are independent given H, because every coin key carries the start
  and the seed index (1.5). So C(f) - C(beta) is a function of independent variables, which McDiarmid's inequality
  needs.
- Item 6's refusal of any coin key without the start enforces that premise mechanically.

**The bounded difference (item 4), re-derived.**
- Changing one unit's field changes x_d(u) for the design and for the baseline. Both arms read that field.
  - Each arm's Phi_d moves by at most r_d / (J |E_{h_d}|).
  - The arms are clipped separately, and the clip is 1-Lipschitz, so the difference moves by at most
    2 w_d r_d / ((hi_d - lo_d) J |E_{h_d}|) per dimension the unit belongs to.
  - Summing over the dimensions gives item 4's c_u, including the indicator 1[u in E_{h_d}].
- The factor 2 cannot be removed, because the arms are clipped before they are differenced.
- LB = Delta-hat - sqrt(ln(1/alpha) x sum c_u^2 / 2) is McDiarmid's one-sided form at alpha.

**Unit-count shares and `P_B` under choice 3: correct.**
- A unit-count share is a mean of an indicator over all of E_{h_d}, so r_d = 1. Its c_u is exact as item 4 states.
- `P_B`'s per-unit value is the share of months 1 to 3 ahead under B, in {0, 1/3, 2/3, 1}, so it lies in [0, 1] and
  r = 1.
  - It is computed on unit u's own journey: the replay's path under u's own coin field, per MEASURES.md section 2 at
    wt/wt-user 9842e10.
  - For the unclipped fallback, item 4 gives c_u = 2 / (J |E_63|) and sum c_u^2 = 4 / (J |E_63|). So
    LB = Delta-bar - sqrt(2 ln(1/alpha) / (J |E_63|)), which is Hoeffding's bound for terms in [-1, 1], as the
    paragraph says.
- Conditional shares, ratios of means, tail means and quantiles are excluded (item 3). This is right: their bounded
  difference depends on a random denominator.

**Item 2 (i): are contract-arithmetic bounds sufficient and exact?**
- **Sufficient:** yes, when the arithmetic is right. An indicator lies in [0, 1] exactly. Dollar amounts are bounded by
  what the verified rules and a declared purchase cap allow over h_d sessions, and those limits are hard limits of the
  engine.
- **Exact:** McDiarmid's guarantee needs the bounds to hold on every coin field, not only on the realised ones.
  - Item 6's refusal catches a realised violation.
  - A wrongly derived bound that no realised unit happens to cross is not caught.
  - Its effect on the size is second-order: it can matter only through fields of probability well below one in the
    number of units. That is negligible, but it is not exact.
  - Source (ii), a clip in the dimension's own definition, is exact by construction. M-1 makes (i) exact the same way
    at no cost.
- Neither point lets a false pass through at a material rate, so neither is blocking.

---

## Minor findings (carry into the declaration)

### M-1. Make source (i) exact, and say what a refusal on the held-out run means. **Minor.**

- **Where.** Item 2 (i) and item 6 (lines 349-357, 376-380).
- **Two gaps.**
  - As discussed above, a contract-arithmetic bound is exact only if the arithmetic is right.
  - The paragraph does not say what follows a refusal on the held-out read. Re-deriving a bound and re-running after
    seeing which held-out value crossed it would be a choice made after a look.
- **Remedy (two sentences).**
  - "A bound from source (i) is also written into the dimension's definition as a clip, x_d(u) = clip(y_d(u), a_d,
    a_d + r_d), so the bound holds on every coin field by construction. The refusal stays, as a check that the
    arithmetic was right."
  - "The bounds are exercised on the build's tests, H3-D and H4 before any held-out read. A refusal on the held-out
    run ends the held-out test for that finalist as a failure: it is diagnosed, never re-run with new bounds."

### M-2. The session-count example conflicts with the never-blank censored value. **Minor.**

- **Where.** Item 2 (i) gives "a count of sessions in [0, h_d]". Section 1.3 (line 171) gives a censored dimension the
  value W + 1.
- **What goes wrong.** Any unit censored on a sessions-to-event dimension would be refused under item 6. The result
  is a refused run, not a wrong one.
- **Remedy.** Write "a count of sessions in [0, W + 1], W the dimension's window, its censored value included".

### M-3. Say where a dimension with neither source goes. **Minor.**

- **Where.** Item 2. Example: a dollar dimension of a design with no declared purchase cap, and no clip pinned.
- **The gap.** The paragraph implies such a dimension is not admitted ("from one of two sources only"), but item 3's
  list does not name it.
- **Remedy.** Add to item 3: "a dimension whose per-unit value has neither an arithmetic bound nor a pinned clip".

### M-4. The race's exit cost should be the stop side's. **Minor.**

- **Where.** 1.1 (lines 101-109); `race_redraw(l, g, c, exit_cost)`.
- **Evidence (checked).**
  - L = min(l, c - x) with p = L / (L + g) gives a gross expectation of exactly zero.
  - The net expectation is minus (entry + exit), and the loss plus x lands at most on the floor. The test asserts all
    of this in exact fractions over fractional cushions.
  - It agrees with the engine. The vendored lockstep loop hands the draw `room = min(cushion, dll + day_pnl)`, clips
    at `-cushion`, and fails an account at `self.B <= self.F + EPS`
    (`vendor/stage2/propedge/campaign/lockstep.py:452-492`).
  - So a costed loss at L = c - x ends exactly on the floor and fails the account, which is the firm's rule. The clip
    never binds.
- **The gap.** The note uses one exit cost x "paid on either exit". A stop exit can carry slippage that a target exit
  does not. If x is the target side's cost, a stop-side loss passes the floor and the clip binds again, crediting the
  slippage: N-5's credit in a small form.
- **Remedy.**
  - Write L = min(l, c - x_stop), with x_stop the stop-side exit cost (commission plus declared stop slippage) and
    x_target the target side's.
  - The net expectation is then minus (entry + p x_target + (1 - p) x_stop): still minus the expected costs.
  - Extend the oracle to unequal exit costs.

---

## N-2 to N-11, diff-checked

All are answered where section 0's cycle-2 table says.

| finding | where | check |
|---|---|---|
| N-2 | 1.5 (lines 219, 240-243); item 5 and item 6 | Choice 3 is the stated premise; keys without the start are refused; MEASURES.md is being aligned. Adequate. |
| N-3 | 1.6 (lines 277-290) | Two code paths. The difference is non-decreasing in the stagger. The shared-path-against-independent gap falls to noise past the longest hold. Correct direction. |
| N-4 | 1.6 (lines 292-300); `KEY_KINDS` | Recorded for the template: inward rounding, key per underlying, overlap on the run's times. Overlap stays refused. Adequate. |
| N-5 | 1.1; `race_redraw`, `net_expectation`; the costed test | Correct and engine-consistent; M-4 refines it. |
| N-6 | 2.2 (b) (lines 393-396); 6.1 | The rule is applied in H3-D at the pinned delta\*; H3-A reports only. Adequate. |
| N-7 | 3.4; Appendix A's (Y) lines | n_Y = all of Y_ok. "Vacuous" when the stated size is at least one half, printed. n_min from the calendar, both choices shown, the pinning row sets it. Adequate. |
| N-8 | 1.5 (lines 222-233); `seed_key`, `key_state`; the key test | Words of 2^32 or more refused. The guard compares `generate_state`. The `[7, 2**32 + 5]` trap is tested. Adequate. |
| N-9 | 7; three new fold tests | No prefilter; `**`, `+=` and tuple targets folded. The fold is stated as a tripwire, with the run-time assertion as the guard. Adequate. |
| N-10 | the key test | Built under the tests' seed. Adequate. |
| N-11 | 1.3 (lines 189-192), 3.5 | Noted beside the verdict with the share at a cap. Adequate. |

## What I tried that found nothing

- **McDiarmid's c_u**, re-derived for paired arms clipped separately, units belonging to several dimensions, and the
  fallback's reduction to Hoeffding.
- **Independence given H under the declared key.** Start and seed index are both in every coin key, and the refusal
  enforces it.
- **The costed race against the vendored lockstep loop's settlement**: room, clip, and the breach test at B <= F + EPS.
- **The admission list against MEASURES.md's measure kinds** (unit-count shares, conditional shares, ratios, CVaR10,
  quantiles).
- **Seed literals.** None in this note.
- **The test file at 181eb44.** 19 pass.

## What I could not check

- **Whether every dollar dimension the operator weights in Wave 4.2 will have a finite contract-arithmetic bound.**
  That is known only once the dimensions are chosen. M-1's clip makes the answer immaterial to validity.
- **MEASURES.md's aligned reading 3 on wt-user** (N-2).
