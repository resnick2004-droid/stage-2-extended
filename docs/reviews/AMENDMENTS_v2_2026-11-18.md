# Red team, full re-read: the revised amendments draft (corrective cycle 1), 2026-11-18

**Target:** `docs/plans/AMENDMENTS_draft_2026-11-18.md` (untracked, 825 lines, revised in place). It is read against
my first note, `docs/reviews/AMENDMENTS_2026-11-18.md`, and against the staged `DECISIONS.md` rows:
- E-207, the operator's confirmation and the review-speed rule now in force;
- E-208, the triage and the split.

Other sources: `prereg/RD-02_payout_policy.md`; the current `CHARTER.md` and `DIRECTIVE.md`.

Read-only. This note is the only file written. It contains no figures and no seed literals.

**How this read was run.** It is a full re-read under E-207 (2), since my first read had blocking findings. The
coordinator gave readings R-1 to R-5 and named four operator items, O-1 to O-4. I checked each against the text itself
and did not take any reading as settled. **`docs/MEASURES.md`** is still not reviewed: it is not on `wt/wt-user`.

## Verdict: **must be re-declared** (3 blocking, 10 minor)

Nine of the twelve first-read blockers are closed in the text: B-1, B-2, B-3, B-5, B-7, B-8, B-9, B-10 and B-12.
Every first-read minor is answered. Three blocking points remain:

| finding | what remains open |
|---|---|
| V-1 | B-4's remainder. The level is conditional on the one held-out history, and the declared nulls cannot detect history luck. This answers R-1 in the negative. |
| V-2 | New. The reflection convention gives exactly zero only for symmetric brackets. |
| V-3 | B-11's remainder. R-2's floor for the as-traded resting side is not written in. |

**Can the texts go into force?** Yes, once V-1 to V-3 and minor m-1 are fixed. All four fixes are text edits.
- V-1 adds one null to the calibration (H3), and H3 already runs before any search is pinned.
- V-2 and V-3 each add a floor of the same kind as the fill stress.
- Nothing in V-1 to V-3 needs a run before the texts are applied.

Under E-207 (2), the blocking items get a re-read. Because the edits are confined to 3.2, 3.5, 3.7, 3.8, 5, the
CLAUDE.md block and the row, that re-read can be scoped to those passages.

---

## First-read blockers: closed or not, in the text

| # | status | where it is closed, and the check made |
|---|---|---|
| B-1 | **closed** (ledger list incomplete: m-3) | 3.6 (a)-(c) define "held out" two ways, carry the ledger, print the level nominal, and make use single per market. 3.3 (f) keeps held-out results out of the map and the ledger. The default split is named (E-208). |
| B-2 | **closed** | 3.9's single pinning row lists every input of 3.8 and 3.9, set before the survey from the search years only. 3.6 (e) runs H4 on search years only, with any held-out output sealed. Section 2's limits come from the search-year re-baseline. |
| B-3 | **closed** | 3.6 (d): a start is read at a horizon only if the horizon fits; the strip is purged; held-out starts read held-out sessions only; the cost goes to the power gate. RD-02 l.331 already purges this way. |
| B-4 | **partly open → V-1** | The nulls are no longer degenerate, and the unit is stated. But the level-carrying leg's hypothesis is conditional on the one history, and both nulls are same-design nulls. |
| B-5 | **closed** (latency: m-6) | 3.8 (b): the same convention, each baseline beaten (an intersection-union test at full level), registered rows beside, a runner identity. |
| B-6 | **closed for direction; see V-2** | 3.2 defines zero edge for every entry type, with the as-traded result beside. The claim of exactness is false for asymmetric brackets (V-2). |
| B-7 | **closed** | 3.8 (c) writes the zero-edge gate: D-14's median log growth, no shift, 25 % denial with 0 % beside, a pinned quantile, complete starts only. 3.10 retires the `verdict` arm and the edge-bound form. Section 2 reads Stage 2's definitions "on the zero-edge convention". |
| B-8 | **closed** (wording: m-8) | 3.7 sets a fixed sequence at the full level, stopping at the first failure. 3.9 pins the fallback in place of the composite. 3.3 (g) counts L. |
| B-9 | **closed** | 3.7's power gate covers the whole line before any pin ("no power, no pin"). Section 5 (B) states the power. The data question goes to the operator before the first pin (also DIRECTIVE D-12). |
| B-10 | **closed in substance** (authority: m-2) | 3.8 (a) applies one margin, once, with the burden on evidence of crossing. The power gate's limit clause covers a design equal to the best baseline. E-015's condition is carried by name. |
| B-11 | **partly open → V-3** | The literal coin and the no-harm floor are written for model sides. The as-traded resting side has no floor. |
| B-12 | **closed** | 3.8 (c): stress floors at +1 tick of worse fills and 10 % of signals missed, on both design and baselines (R-3). |

### The coordinator's readings, R-1 to R-5

- **R-1: not satisfied.** 3.7 says history blocks are "the unit for the nulls' resampling". It does not say that the
  rule's size is checked across histories. Even if it did, the two declared nulls could not show history luck, as V-1
  explains.
- **R-2: not written in.** 3.5 calls the as-traded stress "the user's reading of that gap". 3.8 (c) has no as-traded
  floor, and 3.9 pins only "the side rule's no-harm margin" for model sides. See V-3.
- **R-3: written and kept.** 3.8 (c) applies the stress to "both under the same stress". Keep it.
- **R-4: written.** 3.8 (c) uses 25 % denial for the gate, with 0 % beside, and the verdict stays at 0 % (l.356). The
  power gate takes in 3.6 (d)'s embargo, including the gate's horizon (l.300-302 and l.265). One addition is worth
  making: under D-145's two-year horizon, very few held-out starts are complete. The power gate should name the count
  of complete starts as a pass condition, not leave it implied.
- **R-5: accepted.** One consequence is in m-9.

### Operator items O-1 to O-4: open or decided?

- **O-1 (which firm spends NQ's held-out years):** left open in 3.6 (c). But section 2's "Topstep $50K first", read
  with single use, decides it in effect (m-10).
- **O-2 (the nominal level):** the reporting rule is written (3.6 (b)), and telling the operator is left to the item.
  That is fine.
- **O-3 ("the size that matters"):** the text does not say who sets it. 3.9 lists it among the pinned inputs without
  naming its author. That is not a decision, but it should be marked as the operator's (m-1).
- **O-4 (the literal coin):** **decided in the text**, not left open:
  - 3.5: "The default is ... one literal coin draw per moment";
  - the CLAUDE.md block: "the playbook's side a literal coin";
  - the terms table: "a literal coin by default";
  - the row: "the playbook's side a literal coin".

  See m-1.

---

## Blocking

### V-1. The level controls coin luck on one history, but the calibration cannot see history luck (B-4 remainder; R-1)

- **Where:** 3.6 (f) (i), l.270-273 ("The replicates are disjoint coin-seed sets on the fixed held-out history ... on
  the held-out years, the design beats the baseline in expectation over coin draws"); 3.7 "Calibration", l.289-298; 3.8
  (b), l.330-332; CLAUDE.md block, l.465; section 5 (A), l.431-434; E-208 ("only the paired coin-seed leg can carry
  the level").
- **Evidence.**
  - The level-carrying hypothesis is conditional on the realised held-out history. Seed sets are i.i.d. given that
    history. As seeds are added, the leg rejects for any positive conditional difference, however small, so the leg
    reduces to "the point estimate on these years is above zero".
  - Whether such a difference is the design's or the history's luck is left to the time leg. That leg is a
    consistency condition with no stated false-pass rate (l.274-277).
  - Both declared nulls (l.292-294) are same-design nulls: the antithetic twin, and disjoint seed sets. Their
    conditional difference is zero in expectation on **every** history. Resampling history blocks under them (R-1) can
    therefore never show the rule passing a design that merely got a favourable history.
  - The verdict, 3.8 (b), the CLAUDE.md block and the program's budget (3.7, "continues Stage 2's program U") all
    present the result as "at 0.05 / (k (k+1))". A reader takes that as the chance that a design no better than the
    baselines passes.
- **Failure allowed.** Take a finalist whose shape suited 2024-2025's path (a trending tape and a wide target, say) but
  equals the baseline over histories. It passes the coin-seed leg with near certainty under many seeds, then passes
  "most years" with a probability nobody has measured. It is carried with a printed level of 0.05/(13·14). Its real
  false-pass rate over histories is of a different order, and the program's budget is spent on a test that bounds
  only coin luck. The confirmation window, the one fresh history, is "read and reported" in 5 (A) with no criterion.
- **Fix** (text, plus one null added to H3):
  - (a) Add a **history null** to 3.7's calibration: **distinct** designs whose composites are equal in expectation
    over histories but differ on any one history. One construction is two components on synthetic paths with NQ's
    dependence, exchangeable under the generator's symmetry (the same law in two sessions, or mirrored schedules).
    Measure the whole rule's pass rate on them across synthetic and history-block-resampled histories.
  - (b) Print that rate beside every verdict as **the history-level false-pass rate**, next to the coin-level level
    and the nominal label.
  - (c) State the scope in 3.8 (b), the CLAUDE.md block and the row: "the level bounds coin luck on the held-out years;
    history luck is bounded only by the time leg, at the rate printed beside".
  - (d) In 5 (A), give the confirmation a criterion declared at registration, as a described reading or a
    pre-declared check. It is the only test across histories.

  The power gate already runs on synthetic histories, so (a) is one more null in the same heavy run (H3), not a new
  experiment.

### V-2. Reflection is exactly zero only for symmetric brackets; for any other reward-to-risk ratio it keeps the path's serial structure (new; B-6 remainder)

- **Where:** 3.2, l.169-172 ("For a market entry this is exactly a fair coin choosing the side" and "The reflection
  makes the gross expectation exactly zero"); 3.2, l.179-180 ("the edge is zero by construction"); 3.8 (c), l.350-351
  ("e is zero by construction"); the terms row "zero edge"; 3.3 and the terms (reward-to-risk is a lever); section 4's
  zero-edge oracles.
- **Evidence.** For one post-fill path p, the coin-averaged payoff is ½ [f(p) + f(-p)], where f is the bracket's
  payoff.
  - It is exactly zero when the stop equals the target (f(-p) = -f(p)).
  - It is zero in expectation for any bracket on a driftless **martingale** (optional stopping).
  - It is not zero for an asymmetric bracket on a path with serial dependence. Reflection removes the path's sign, but
    not its momentum or mean reversion.

  This also holds for **market entries**, where reflection is just the fair coin.

  I ran a small exploratory synthetic check, with no file kept in the repository: a market entry, the exact
  coin-average per path, AR(1) increments.
  - Symmetric brackets gave exactly zero on every path.
  - A wide-target, tight-stop bracket was positive under momentum and negative under mean reversion, several standard
    errors from zero.
  - The reverse orientation flipped both signs.
  - On the martingale, every bracket was within noise of zero.
- **Failure allowed.** The survey reads 2020-2023 and selects a reward-to-risk ratio and a session (P-14's breakout
  timing is a coin-sided source under E-208) that harvest that window's momentum. The finalist carries a gross
  expectation above zero under "zero edge". The gate's rewrite drops the lower bound because "e is zero by
  construction", so nothing prices it. Two further consequences:
  - The verdict says "never the trades' edge" while the selected design rests on a path edge that may not persist.
  - Section 4's zero-edge oracles may flag the result as an engine error.
- **Fix.**
  - (a) Correct 3.2 and 3.8 (c): "the convention removes direction exactly; for a symmetric bracket the gross
    expectation is zero on every path; for any other bracket it keeps the path's serial structure (momentum, mean
    reversion), which is reported".
  - (b) Add a floor to 3.8 (c), the same for design and baselines (R-3's form): a **martingale-outcome stress**. Each
    trade's outcome is redrawn at the driftless first-exit probability of its bracket (stage one's
    `adapter.BinaryDraw` form, as Stage 2 D-150 used it). Fills, timing, costs and resolution stay as run. The finalist
    must still beat each baseline at the point estimate under it.
  - (c) Beside the verdict, report the gap between the reflected result and the martingale-outcome result as the
    design's **path-structure edge**.
  - (d) Say how section 4's oracles read a reflected result, so that a path-structure surplus is not booked as an
    engine error, nor "fixed" as one.

### V-3. The as-traded resting side, which is what the user trades, has no floor (B-11 remainder; R-2)

- **Where:** 3.5 side rule, l.229-231 ("A resting trigger with no realisable zero-edge construction ... is traded as
  its real order. Its as-traded stress (3.2) is the user's reading of that gap"); 3.8 (c) floors (l.339-354), none of
  which is as-traded; 3.9 pin list, l.382 ("the side rule's no-harm margin", for model sides); 3.8 verdict line, l.360
  (as-traded only beside).
- **Evidence.** For any resting trigger except realisable pairs, the evaluated object (the reflected path) is not the
  traded object (the real order). E-203 B-1 and E-204 NB-1 show that the real resting side carries adverse selection
  (m < 0 for limits). B-11's fix gave model sides a no-harm floor. The same gap for resting orders is only reported.
- **Failure allowed.** A design built on limit pullbacks passes on the reflected path. The user is told to place the
  real limits and lives the as-traded journey, which is below the reflected one by the adverse selection. The verdict
  certifies a journey the playbook does not produce.
- **Fix.** Write R-2 in:
  - 3.5 and 3.8 (c): a resting trigger traded as its real order clears **the same no-harm floor as model sides**. Its
    as-traded composite on the search years is not below the reflected one by more than the margin pinned in 3.9.
  - Its held-out as-traded reading is reported beside.
  - The pin list names one margin for both cases, or two.
  - Recommended as well: on the held-out years, with as-traded sides, the finalist still beats each baseline at the
    point estimate, both under the same stress (R-3's form). This is what makes the verdict about the traded object.

---

## Minor

- **m-1. O-4 is decided, not left open; O-3 has no named author.** The literal coin is written as the default in 3.5,
  the terms table, the CLAUDE.md block and the row. **Fix:**
  - 3.5: "The side rule is the operator's (O-4). Until ruled, every playbook states the coin side with the model-side
    and as-traded readings beside, and no playbook goes to a user."
  - Remove "the playbook's side a literal coin" from the CLAUDE.md block and the row, or mark it "pending O-4".
  - 3.9: "the size that matters (the operator's, Wave 4.2; O-3)".

  The zero-edge **evaluation** convention (3.2) is not the operator's choice, and it stays.
- **m-2. Limits: the burden reverses words the operator confirmed.** E-207 (1) quotes the confirmed text as "inside
  every operator limit with margin wider than its noise", with the burden on the design. 3.8 (a) puts the burden on
  evidence of crossing. That is my B-10 fix, and E-015's condition supports it, but it departs from E-207's wording on
  a value question (hard lines versus not failing profitable models). **Fix:** the row records the departure, and the
  burden goes to the operator with O-1 to O-4 as **O-5**. The text stands until they rule.
- **m-3. The ledger's "known entries today" leaves out the two closest journey reads** (3.6 (b), l.241-249):
  - program U's nine families, P on the late block against P-14, recorded in RD-02 l.205 as "read for P nine times";
  - RD-02's late-block menu of payout policy (RD-02 l.47 and l.333), whose levers are now in the lever space (3.10's
    E-023 line).

  **Fix:** add both to the list and to the row's list. Say that the list is a floor, which each declaration completes,
  including any RD-01 late-block reads.
- **m-4. 3.3 (a) and E-208's lever maps.** 3.3 (a) says no lever range may read the held-out years. E-208 keeps RD-01
  to RD-05 "as the firm and lever maps", and 3.6 (b) lists RD-03's readings as whole-window. **Fix:** "a lever range
  comes from contract arithmetic, the verified rules, or an RD map's search-year rows only. A range drawn from a
  whole-window row is redrawn on the search years, and the source is entered in the ledger."
- **m-5. The side rule's text.**
  - l.230: "with no realisable zero-edge construction (such as RL3's pair)" makes RL3's pair an example of *no*
    construction, which contradicts 3.2 l.175. Reword it to "(RL3's pair is one that has one)".
  - "One draw per moment, shared" does not stop opposite sides between trades opened at **different** moments while
    both are open across firms. Only cross-firm rotation can do that, since one firm holds one position at a time. The
    text's claim "no two of the user's positions are ever opposite" is false as written. **Fix:** "while any position
    is open in the user's accounts, a new trade's side is that position's side, or the trade is skipped. The
    evaluation uses the same rule."
- **m-6. The baselines' latency.** 3.8 (b) runs baselines on "the same ... latency model" and also asks for a
  path-for-path identity with the registered trades. P-14's identity is at five minutes, and P-16 is scheduled with its
  latency variants dropped (E-203 B-2). Running baselines at a finalist's L = 2 would break the identity. **Fix:**
  "baselines at their registered latency; 'the same latency model' means the same mechanics".
- **m-7. Order of the calibration and the heavy queue.** 3.7 puts the deciding calibration after 3.9's pinning row,
  which needs Wave 4.2. E-208's queue runs H3 before H4. "Design pairs from the search years" (l.301) exist before any
  survey only as H4's baselines. **Fix:** say that H3 as queued is preliminary, and that the deciding run follows the
  pinning row. Name the power gate's design pairs as H4's baselines and the synthetic plants.
- **m-8. "The five-minute cell ... in the held-out test"** (3.3 (g), l.199-200) can be read as tested. **Fix:** "read
  and reported in the held-out test, not tested".
- **m-9. Measure structure from H4 alone** (R-5, accepted). With four baselines, the "dimensions" come from variation
  across start days and seeds, not across designs. **Fix:** one sentence in 3.9 saying so, so that the operator's
  trade-off curves are not read as curves across designs.
- **m-10. O-1 is decided in effect.** Section 2's "Topstep $50K first", read with 3.6 (c), assigns NQ's held-out years
  to Topstep. **Fix:** "Topstep $50K first (the use of NQ's held-out years is the operator's, O-1)".

---

## First-read minors, spot-checked

All ten are answered:
- m-1: 3.3 (g) and 3.5.
- m-2: section 4's marked paragraph.
- m-3: 3.7 "The budget", the terms and section 5.
- m-4: the verdict line, l.356-360.
- m-5: 3.3 (a) and 3.6 (f).
- m-6: 3.6 (g).
- m-7: section 2, "The measures".
- m-8: 3.1 and the terms.
- m-9: DIRECTIVE D-0 and D-9 to D-11. The new line numbers (56-57, 120-122, 126-128) match the file.
- m-10: E-207 is cited, the plateau rule is pinned, and each limit's direction is stated.

## What I tried that found nothing

- I extracted section 4's current paragraph from the draft and diffed it against the current CHARTER: identical. The
  E-202 paragraph is added as a separate, marked block.
- A search of the whole draft for literals of five or more digits found none.
- The row and the CLAUDE.md block agree with 3.6 to 3.9 on the split, the pinning row, the fixed sequence, E-204's
  rule in full ("held-out test" in place of "stage B"), the confirmation spending no k, and the k history.
- The antithetic null under reflection: for a symmetric bracket the twin's per-path payoff is the exact negative, so
  this null is non-degenerate and correctly centred. Its limit is V-1, not its construction.
- 3.8 (b)'s intersection-union test inside the fixed sequence keeps family-wise control at the k's level. This is for
  the conditional hypothesis; see V-1.
- 3.6 (d)'s embargo matches RD-02's existing purge (`u_select.block`, l.331-333), so it can be built from code that
  exists.

## What I could not check

- `docs/MEASURES.md`: absent from `wt/wt-user`.
- Whether RD-01 read the late block. Only RD-02 was opened for m-3.
- The draft's section 5 file list. I spot-read it only; it was not re-grepped.
- Whether a history null of the V-1 (a) kind can be built with equal expectation exactly, rather than approximately,
  for the composite's quantile-type dimensions. This is to be settled in H3's declaration.

**Experiments specified, not run:**
- (1) V-1 (a)'s history null, inside H3. Heavy; no larger than H3.
- (2) V-2 (b)'s martingale-outcome stress on the baselines, as part of H4. Light per design, since the binary-draw
  form needs no bars beyond the run's own fills.
