# Red team, scoped re-read: the amendments' final text (corrective cycle 2), 2026-11-18

**Target:** `docs/plans/AMENDMENTS_draft_2026-11-18.md`, untracked, 916 lines, revised in place.

**Scope**, as the coordinator set it:
- the passages that V-1, V-2 and V-3 touch (section 0's cycle-2 table);
- R-4;
- the drafter's R-9 to R-12;
- a diff-only check of the minor fixes, under E-207 (2).

I re-read 3.2, 3.5, 3.6 (f), 3.7, 3.8, section 4's added paragraphs, 5 (A), the CLAUDE.md block, D-2, D-4, D-5, D-7,
the row, and section 6 in full.

This note is the only file written. It holds no numbers and no seeds. I applied the coordinator's threshold:
**blocking** means that putting the text in force would make a result wrong.

## Verdict: **one blocking finding, fixable by the lead with one sentence.** With that sentence in, **the texts can go into force.**

V-1, V-2, V-3 and R-4 are closed in the text. All five operator items stay open.

Cycle 2's own wording has opened one new hole, N-1. The new rule that "every deciding reading is the martingale-outcome
reading" makes the V-3 floors, and the model-side no-harm floor, compare two identical numbers. So they can never
fail. The fix is a single carve-out sentence, given below.

N-1 is a drafting defect, not a question for the operator. It does not need NEEDS_OPERATOR. Under E-207 (2), the check
after it is applied is the diff of that one sentence.

Everything else found is minor (m-1 to m-6), or a note.

---

## The three blockers from the second read

### V-1: **closed.**

- **The scope is stated** wherever the level is stated: 3.6 (f) (i) l.326-327, 3.8 (b) l.404-407, the CLAUDE.md
  block l.572-573, D-2, D-7 and the row.
- **The history null** is added to the deciding calibration (3.7 l.350-355). It uses distinct designs, equal in
  expectation across histories, run on synthetic and resampled histories in the same run as H3.
- **Its false-pass rate** is printed beside every verdict (3.8 l.440) and beside the level in 5 (A).
- **The confirmation** now has a criterion declared at registration (5 (A) l.528-532, R-9).
- **The approximate case:** R-11 leaves open whether the history null is exact for quantile-type dimensions, and
  settles it in H3's declaration. That is acceptable, because the rate is read beside the verdict and does not decide.
  H3's declaration should print an approximate rate as approximate.

### V-2: **closed.**

- **The false claim is corrected.** 3.2 l.197-199 now reads: "for a symmetric bracket ... zero on every path. For
  any other bracket, the reflection keeps the path's serial structure ... The reflection alone is therefore not zero
  edge."
- **The martingale-outcome reading decides.** It redraws each trade's outcome at its bracket's driftless first-exit
  odds, in `BinaryDraw` form, the same way for designs and baselines (3.2 l.200-206; 3.8 l.388-389; the gate,
  l.421-429).
- **The as-walked gap** is reported as the path-structure edge, never credited (l.207-209; the verdict line, l.444).
- **The oracles' reading** is added to section 4 (l.519-522).
- **The gate's rewrite** no longer leans on "e is zero by construction". It now rests on the reflection plus the
  redraw (l.427-429), which is correct.

### V-3: **closed in intent, broken by its reading. See N-1.**

- **What is written:** the floors are now in the text (3.5 l.275-278; 3.8 (c) l.433-436; 3.9 l.471-472). The
  as-traded resting side has the model sides' no-harm floor, and the held-out as-traded floor against each baseline.
- **What breaks it:** both floors fall under the lead sentence of 3.8 and under the terms row "zero edge", and on that
  reading they can never fail. N-1 explains why.

### R-4: **closed.**

- 3.7 l.368-369 states the count of held-out starts complete over D-145's horizon, with a minimum pinned in 3.9
  (l.470).
- Failing that minimum stops the pin (l.370).
- 3.8 (c) l.423 reads the gate only on those starts.
- The gate uses 25 % denial with 0 % beside (l.425-426), and the verdict stays at 0 % (l.438).

---

## Blocking

### N-1. On the martingale-outcome reading, the no-harm floors and the as-traded floor compare a number with itself

- **Where:**
  - 3.8 l.388-389: "**Every deciding reading below is the martingale-outcome reading of 3.2**".
  - Terms, "zero edge", l.114: "every deciding reading redraws each trade's outcome at its own bracket's driftless
    first-exit odds".
  - 3.8 (c) l.433-436, the as-traded floors: "with as-traded sides, the finalist still beats each baseline".
  - 3.5 l.272-278, the no-harm floors: "its composite on the search years is not below the coin side's" for model
    sides; "its as-traded composite ... not below the reflected one" for resting triggers.
- **Evidence.** The martingale-outcome reading redraws each outcome from the bracket's driftless odds, given fills,
  timing, costs and resolution "as run". On that reading the trade's side and its post-fill path no longer enter the
  outcome. So:
  - a model side and the coin side give the same martingale-outcome composite, given the same draws;
  - an as-traded resting side and its reflection give the same composite;
  - the held-out "as-traded" comparison against the baselines equals the main deciding comparison.

  Every floor written to close V-3 and B-11 is a deciding reading. Read literally, each one therefore compares a
  number with itself, or repeats 3.8 (b) at the point estimate.
- **Failure allowed.** This is V-3's case again.
  - A design built on limit pullbacks passes every floor, while its as-traded journey carries the resting side's
    adverse selection (E-203 B-1, E-204 NB-1).
  - A playbook that gives a model's side passes the no-harm floor whatever that side does.
  - In both cases the verdict certifies a journey the playbook does not produce.
- **Fix.** Add this sentence after 3.8's lead sentence (l.389), and give it a matching clause in the terms row "zero
  edge" and the row:

  > **The one exception:** the no-harm floors (3.5) and the as-traded floor (3.8 (c)) are read on the real path, with
  > no redraw, because they exist to measure what the redraw removes. A no-harm floor compares the side as traded (the
  > model's side, or the resting order's real side, unreflected) with the coin side on the as-walked, reflected path,
  > same fills, same seeds. The held-out as-traded floor compares the finalist's as-traded composite with each
  > baseline's as-walked composite. For a market-entry baseline, its as-traded and as-walked readings coincide.

  The check after the fix is the diff of this sentence and its two echoes.

---

## Operator items: open, not decided

| item | status in the text |
|---|---|
| O-1 (which firm spends NQ's held-out years) | **Open.** Section 2 l.93-95, 3.6 (c) l.306-307, the row, section 6. "Topstep $50K first" is now qualified. |
| O-2 (the nominal level) | **Information, not a choice** (section 6 l.902-904). The reporting rule is written (3.6 (b), 3.8). That is correct. |
| O-3 ("the size that matters") | **Open:** marked the operator's, Wave 4.2 (3.7 l.364, 3.9 l.467, the row). |
| O-4 (the traded side rule) | **Open.** "Pending the operator" in the terms (l.110), in 3.5 l.263-271, in CLAUDE.md ("the traded side rule pending the operator") and in the row. The literal coin is only "the candidate default", and no playbook goes to a user until the ruling. The zero-edge evaluation convention is kept apart from the item, which is correct. |
| O-5 (the burden of the limit check) | **Open.** E-207's confirmed words are in force; the B-10 form is computed beside and never decides (3.8 (a) l.391-396). Keeping the operator's own words is the status quo, not a decision. See the note under m-6. |

---

## Minor (fixed, then the diff checked)

- **m-1. D-5 still defines zero edge by the reflection alone.** 6.3 A's replacement (l.642-643) reads "judged under
  ... zero edge (the path after the fill reflected with probability one half)". V-2 found that this is not zero edge.
  **Fix:** add "and each outcome redrawn at its bracket's driftless odds for the deciding reading", as D-4 already has.
- **m-2. Overlapping trades are redrawn independently.** Today one position at a time per firm means trades never
  overlap, so the redraw is sound for the first Topstep search. Once cross-firm rotation enters the lever space (plan
  item 4), two same-side positions at once on NQ would be redrawn as independent. Their real outcomes are almost
  perfectly correlated. 3.4's lower correlation between accounts would then be an artefact of the redraw, and joint
  ruin would be understated. **Fix:** a clause in the row, carried into the template (Wave 2.1): "trades open at once
  on the same instrument are redrawn jointly, from one seeded driftless path; no design with overlapping positions is
  run until the template defines this."
- **m-3. The redraw and stop slippage.** "Costs and resolution stay as run" (l.203) does not say whether a redrawn
  loss carries the run's stop-exit slippage. A binary draw at the exact barrier drops it, which is slightly optimistic
  next to the as-run path. **Fix:** in the template, say that a redrawn loss carries the run's stop-fill price
  convention, or the cost floor's.
- **m-4. The antithetic twin under the redraw.** 3.7 l.347 calls the twin "every coin side reversed". On the deciding
  reading, the randomness is the redraw's uniform draw, not a side. **Fix:** "every coin draw replaced by its
  complement (u to 1 - u), for the reflection and the redraw alike". Equal expectation still holds.
- **m-5. The confirmation's minimum criterion (R-9)** names the main comparison and the limits, but not the floors
  that define the traded object. **Fix:** add the as-traded floor (read as N-1 fixes it) and the +1 tick stress, both
  at the point estimate. R-9's rule that the registration may add but not weaken stays.
- **m-6. CLAUDE.md block.** It drops "Focused Trader Program off" from the verdict and the pointer to
  `docs/MEASURES.md`. **Fix:** "Verdict: 0 % payout denial, placement off, Focused Trader Program off; measures:
  `docs/MEASURES.md`."

  **Note on O-5:** under E-207's form, which is in force, the power gate's limit clause asks a design equal to the
  best baseline to sit inside each limit by more than its noise. If the operator sets limits near the baselines' own
  values, the clause fails and no search pins. The gate is built to surface exactly this, so it is not a wrong result.
  The lead should say it plainly when O-5 and the Wave 4.2 limits are put to the operator.

## R-9 to R-12

- **R-9:** accepted, with m-5.
- **R-10:** accepted as a point for the template's read. The driftless outcome at a time limit is a distribution that
  depends on the volatility left, so the template must fix that estimate from the run's own causal bars. Otherwise it
  becomes a choice made after a look.
- **R-11:** accepted (see V-1).
- **R-12:** accepted. The open-position rule is conduct, not a lever. Its supply cost is reported under (37). The
  evaluation uses the same rule (3.5 l.267-269), and m-2's joint redraw is its counterpart on the outcome side.

## The cycle-2 minors (diff only)

Every row of section 0's cycle-2 table checks against the text:
- m-1/O-4, m-1/O-3, m-10/O-1 and m-2/O-5: as in the operator table above.
- m-3: ledger list l.297-301, "a floor".
- m-4: 3.3 (a) l.222-224.
- m-5: 3.5 l.267-269 and l.275.
- m-6: 3.8 (b) l.410-413.
- m-7: 3.7 l.344-346 and l.363.
- m-8: 3.3 (g) l.238.
- m-9: 3.9 l.454-456.

## What I tried that found nothing

- **Section 4.** I extracted the current paragraph again, up to the first marked amendment, and diffed it against the
  current `CHARTER.md`: identical. Both marked paragraphs are clearly separate.
- **Literals.** I searched for any literal of five or more digits: none. No seed literals.
- **The fixed sequence and the intersection-union test** are unchanged from cycle 1 and still hold the family-wise
  level for the conditional hypothesis. The redraw does not change this.
- **The martingale-outcome reading** applies to the baselines exactly as to the finalist (l.206, l.389, l.408-409).
  So B-5's same-convention rule still holds, and the runner identity (trade times and brackets) is unaffected by the
  redraw.
- **The row and the CLAUDE.md block** agree with the charter on scope, the history null, the redraw, the pending
  items and the k accounting.

## What I could not check

- `docs/MEASURES.md`. It was outside this scope and is still not on `wt/wt-user` as of my second read.
- The draft's section 5 file list, beyond reading it.
- Whether stage one's `adapter.BinaryDraw` handles brackets with unequal stop and target and costs as 3.2 assumes. I
  did not open the vendored adapter. The template's read should cite its signature.
