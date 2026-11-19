# Red-team re-read: Wave 2 after its first corrective cycle (2026-11-18)

**Target.** `wt/wt-lit` at 4e2f740, read as the diff from ab0a8e4. The commit's own changes are 13 files:
- the template (`prereg/TEMPLATE_design_search.md`, cited "T l.N" at 4e2f740);
- the gatekeeper, red team, auditor, scout and results-tracer agents;
- six skills;
- `.gitignore`;
- `tests/test_design_search_template.py`.

The other files in the range are master merges and outside scope.

**Scope (the coordinator's).**
- B-1 to B-5 of `docs/reviews/TEMPLATE_AGENTS_2026-11-18.md`: a full re-read.
- m-1 to m-8: a diff check.
- Three of the drafter's interpretations:
  - R-10's walk using the larger of the stop-side and flatten-side costs;
  - the table that maps each exit type to its law;
  - the pin order in T section 14.

**The coordinator's rulings.** I took them as the intended rules and checked the text against them. I did not take
them as answers.

**Labels (E-207 (2)).** Blocking: it could make a result wrong. Minor: wording or a clarification.

---

## Verdict: **must be re-declared, on one subsection only.**

- **B-1 to B-5 are closed.** Every copy of each fix is in place, the tests hold them, and the costed race is exact.
- **The interpretations raise two new blocking findings, both inside R-10** (T l.220-259):
  - N-1: whether a trade is taken now depends on its post-fill outcome, and the lattice step is undeclared;
  - N-2: exits at a profit level set by an account rule are given the time-limit walk instead of the race.
- Each fix is one or two sentences, or one table row.
- The pin order of section 14 is sound. It needs a lead's row reconciling it with CHARTER 3.7's words (n-1).

Under E-207, a blocking finding gets a full re-read. I suggest scoping that read to T section 5's R-10 subsection and
the gatekeeper's item 5, which is all that N-1 and N-2 touch.

| id | label | one line |
|---|---|---|
| B-1 | closed | `L = min(l, c - x_stop)`, rounded inward, in the template, gatekeeper, red team, merge checklist, `feature-rules`, `contract-engine` and auditor; `BinaryDraw` is the cost-free case. |
| B-2 | closed | One hash for the whole renamed file at the pin. The calibration's inputs are in the file, its outputs in E-115's form. The rename happens before the hash, and a test holds one hash per declaration. |
| B-3 | closed | The text binds `heldout_*` reads to after the finalists' row and the held-out row, once per market; RD and `registered_design` reads are refused; the gatekeeper and auditor check it. Q-158 is the guard in code. |
| B-4 | closed | CHARTER 3.8 (c) kept word for word; O-6 is open with both options; no pin until it is ruled; the gatekeeper refuses a draft that picks an option. |
| B-5 | closed | The pair rule's "contributes zero lift" is restored in `feature-rules` with its reason, and carried in T section 5. |
| N-1 | **blocking** | R-10's "a trade with L <= 0 on the lattice is not taken" hangs on which law applies, which is read from the run's post-fill exit. So whether a trade exists depends on its future. The lattice step s ("s dividing l and g") is also undeclared. |
| N-2 | **blocking** | The exit table puts "a rule's exit" under the stopped walk. A rule exit at a profit level (the day's need or the consistency allowance, lever A3 `cap`) is a barrier exit and needs the race at the as-placed target. |
| n-1 | minor | Pin before calibration is stricter than CHARTER 3.7's "calibration ... precedes the search's pin", and the data question now follows the pin. Record the reading in a lead's row. |
| n-2 | minor | Step 1's reads must be of the final text, with section 7's values in it. |
| n-3 | minor | Q-158 is "queued" in the text but built (E-220). Cite its token forms, or the finalists' row will not admit the held-out test. Q-158 does not check the held-out row, so that rule stays the declaration's and the auditor's. |
| n-4 | minor | Two copies of the redraw's law still say "the nearer barrier" without the cost, and are outside the test's copy list. |
| n-5 | minor | "Both legs settled alike" should say how they are settled. |
| n-6 | minor | A re-declaration after a failed calibration or power gate should cite the failed record and use fresh seeds. |

---

## B-1 to B-5, re-read in full

### B-1: closed

- **The race (T l.173-206).**
  - L = min(l, c - x_stop), where:
    - c is the room the engine hands the draw: the floor, or the daily loss limit where it binds first, after the
      entry cost;
    - x_stop is the commission plus `stop_slippage_ticks`.
  - p = L/(L+g). A win pays x_target and a loss pays x_stop.
  - Arithmetic:
    - the gross expectation, p g - (1 - p) L, is zero;
    - a loss plus its cost is L + x_stop, at most c, so the clip in `lockstep.py` l.475-479 never binds;
    - the net expectation is -(entry + p x_target + (1 - p) x_stop).
  - This is DN 1.1 as M-4 amends it.
- **Inward rounding** applies when the cushion binds. The race does not need it for exactness but loses nothing by
  it. "A trade with L <= 0 is not taken" is the runner's rule, with `BinaryDraw` named as booking a zero.
- **Every copy carries the same law:**
  - the gatekeeper's item 5 (l.88-98);
  - the red team's item 8 (l.59-68);
  - the merge checklist (l.78-84);
  - `feature-rules` section 5 (l.94-96);
  - `contract-engine` (l.133-136);
  - the auditor (l.75-77).

  `test_every_copy_of_the_race_law_uses_the_cushion_less_the_stop_side_cost` refuses the full-cushion form in six of
  these. The two outside its list are n-4.
- **R-10's barriers** are re-read under N-1 below. Its arithmetic holds:
  - the loss barrier uses x' = max(x_stop, x_flat), floored to the lattice;
  - so -L - x_stop >= -c, and the value at T less x_flat is above -L - x_flat >= -c;
  - no exit passes the floor, the gross expectation is zero by optional stopping, and the net is -(the expected
    exit costs).
- **The drafter's max-of-costs choice is correct.** One fixed barrier has to cover both ways a walk can lose: hitting
  the stop, or a loss at T. In the assumed profile `stop_slippage_ticks` and `flatten_slippage_ticks` are equal, so
  usually x' = x_stop.

### B-2: closed

- **The freeze.**
  - Section 7 is "never pinned alone" (T l.305-307).
  - The gatekeeper renames, then hashes (l.170-179), and every later row cites the one hash.
  - `test_the_gatekeepers_rename_leaves_the_hash_as_pinned` builds a toy draft, renames it and checks that `pins()`
    sees one hash. Its positive control shows that two hashes are refused.
  - `test_every_pinned_declaration_carries_one_hash_in_the_log` holds the live log.
- **The calibration.**
  - Its inputs are frozen in the file (T l.354-357): the seeds or H3's block, the R-10 estimator, the statistic, J
    and m, the plants, the generator's source and the replicate counts.
  - Its outputs are pinned as `docs/calibration/<F-NN>_calibration.md`. `tests/test_declarations_fixed.py` l.31-39
    reads that path.
  - A failure is never re-run with another seed (T l.361).
- **The run order** puts the reads, then the pin, then the calibration, then the go row, then the survey. The test
  holds that order.

The old window, in which section 12's S5 and section 5's estimator could change after the gate, no longer exists.

### B-3: closed in text; the code guard is Q-158

- **T l.501-512 binds four rules:**
  - `heldout_*` reads come only after the finalists' row and the held-out row, both citing the one hash;
  - the held-out years are read once per market, across declarations;
  - a search that does not spend them carries no `Judged-block reads:` line;
  - RD reads wait for the market's verdict row, and a new `registered_design` read needs a row naming it.
- **The gatekeeper** refuses each case (l.62-74), including a market already read in `results/read_ledger.jsonl`.
- **The auditor** checks every `heldout_*` ledger line's time against both rows, single use per market, RD and
  registered-design reads, the sealed H4 outputs and the reverse reading.
- **Q-158** (wt/wt-verify 6ce8e6a, E-220) enforces rules 1-4 in `extended/reader.py`. Its tokens and its scope
  differ from this text in one respect: n-3.

### B-4: closed

- The charter's words are kept at T l.319 and l.398-399. O-6 (T l.411-417) states both options and says either one
  loosens the floor as written, so the choice is the operator's. No search pins until it is ruled.
- The gatekeeper refuses approval until O-6 is ruled, and refuses a draft that picks an option (l.108-111). The
  auditor's item 9 reads the gate "as O-6 ruled".
- The test refuses "over coin seeds, given the history".

### B-5: closed

`feature-rules` l.56-68 restores "contributes zero lift". It gives the reason (the fill bar's pre-fill range sits on the
target side) and names both deciding floors and the path-structure gap. T l.260-264 carries the rule, with the cap as
a frozen placeholder. One wording point: n-5.

---

## New blocking findings (from the drafter's interpretations)

### N-1. R-10 lets the run's future decide whether a trade exists, and leaves the lattice step free

- **Where.** T l.237-243:
  - "a lattice of step s ticks, s dividing l and g; its loss barrier ... rounded inward to the lattice";
  - "A trade with L <= 0 on the lattice is not taken (the runner's rule)".

  Also T l.223, where the law is "read from the run's terminal state on the as-walked (reflected) path".
- **Evidence.**
  - The walk's L differs from the race's L. It is floored to a multiple of s, and it nets max(x_stop, x_flat) rather
    than x_stop.
  - So a trade near the floor can have race L > 0 but walk L <= 0.
  - Whether it takes the walk depends on how it ends in the run: at a time limit, or at a barrier. That is
    post-fill information.
  - So the rule "not taken" removes exactly the near-floor trades that will be time-limited, and keeps the identical
    ones that will hit a barrier.
  - A skipped trade frees the slot and the five-minute flat. The account's later trades, its cushion path and the
    journey therefore change according to bars after the fill.
  - This is look-ahead in the trade schedule: CHARTER 3.2 keeps fills and supply "from the real order", decided at
    the order.
  - The size grows with s. "s dividing l and g" allows s = gcd(l, g), which can be the whole stop.
    - Example: l = 20 ticks, g = 40 ticks, s = 20. A cushion just under 20 ticks plus costs floors L to 0, and every
      such time-limited trade vanishes.
- **A second problem: s is an unlabelled choice.** It sets:
  - the rounding loss, and so supply;
  - the step count n = round(sigma^2 T / s^2);
  - with it, how coarse the walk is, and so the spread the composite reads.

  The template neither fixes s nor leaves a placeholder for it, so the build chooses it. That is a choice that could
  be made after a look.
- **The failure it allows.** A design whose near-floor trades tend to be time-limited loses those trades from its
  deciding journey. Its supply and its ruin profile are then read from a schedule edited by the future. Changing s
  moves the composite without any declared lever.
- **Remedy.**
  - (a) Decide taken or not taken **at the fill, once, for every trade**, from information known then. Use one rule:
    L_fill = min(l, c - max(x_stop, x_flat)) at the race's tick lattice, and L_fill <= 0 means not taken, whatever
    the trade's later exit. Every trade's race and walk then use that same L_fill.
  - (b) Fix the house lattice: s = one tick. Allow a coarser s only if the declaration states it as a fixed value,
    classed fixed, with the walk's L floored to it never reaching 0 while L_fill > 0 (otherwise refine s).
  - Add a test: two trades identical at the fill, one exiting at a barrier and one at a time limit, are both taken or
    both not taken.

### N-2. A rule's exit at a profit level is given the walk; it needs the race at the as-placed target

- **Where.** T l.234, the table's last row: "any other exit (an unscheduled release's flatten, a rule's exit) | the
  stopped walk, T to the run's exit time".
- **Evidence.**
  - Lever A3, the session rule, is searched (`docs/plans/LEVER_TABLE_topstep50k.md` l.84). Its `cap` value trades
    "until the session's net reaches the mode's consistency allowance".
  - The vendored engine implements the cap and the need-aware pass as an exit at a P&L level. In `lockstep.py`
    l.457-468, the draw is called with `need=x`, and `exit_kind` is set to `pass` or `consistency`.
  - That is a target nearer than g: a barrier, not a time limit.
  - Under the table's last row, such a trade gets the stopped walk to its real exit time, with the original target g.
    - Its redrawn outcome can then exceed the allowance the rule exists to respect, up to +g. The simulated account
      can then breach the consistency rule the real exit prevents.
    - It also never shows the exact "stop at the need" outcome that A3 is searched for.
  - The mean is still zero. But the deciding reading for every A3 = `cap` or need-aware design is drawn from the
    wrong law.
  - The test only demands that every exit reason be mapped, so labelling these exits "a rule's exit" satisfies it.
- **The failure it allows.** The search ranks A3's values, and the account policies built on the need, on outcomes the
  rule cannot produce.
- **Remedy.**
  - Add a row: "a profit level set by a rule (the day's need, the consistency allowance), the as-placed target" maps
    to the race, with g the as-placed target min(g, the level), booked at the target-side cost.
  - Say that in the race, g is always the target as placed.
  - Name what "a rule's exit" otherwise means. If a time or flat rule is meant, list it. Otherwise delete the phrase,
    so the walk's catch-all holds only real time limits (an unscheduled release's flatten).

---

## The drafter's interpretations: the other two

- **The larger of the stop-side and flatten-side costs (T l.238-239).** Correct: under B-1 above, one barrier has to
  cover both losing exits. The only issue is that the larger cost also feeds the take decision, which is N-1.
- **The pin order of section 14 (T l.476-495).** Sound. It is stricter than CHARTER 3.7's order, because the gate now
  runs on frozen inputs, and nothing can change between the pin and the go row except by a new declaration. Two
  points remain:
  - The charter's words are "the deciding run ... precedes the search's pin" and "If any of these fails, the search
    does not pin". The template reads "pin" as "go row" (T l.377-379), and the data question now comes after the pin
    (T l.380-382; CHARTER 3.7 says "asked before the first search is pinned"). Nothing is weakened: the k is unspent
    either way, and more history means a new declaration. But a lead's row should record the reading, as E-210 did
    for 3.7's twin wording (n-1).
  - Step 1's reads can come before step 2 writes section 7's values (n-2).

---

## Minor

- **n-1.** Record in a lead's row that, under the template, CHARTER 3.7's "the search's pin" and "does not pin" mean
  the go row, and that the data question goes with the gate's result before the go row.
- **n-2.** T l.476-480: the scout's brief, the red team and the gatekeeper read **the final text with section 7
  filled**. A section 7 filled after a read is a change: diff-checked by the red team, or re-read if a value is
  blocking-sensitive.
- **n-3.** Three changes:
  - T l.504 and the gatekeeper's l.73 say Q-158 is "queued". It is built and held (E-220). Say so.
  - Write the finalists' row in Q-158's token form, `heldout-finalists: F-NN @ <declaration sha256> list <finalists
    sha256> -- ...`, and hash the finalists' list. Otherwise, once Q-158 merges, the reader will refuse the held-out
    test.
  - Q-158's rule 1 checks the finalists' token, not the held-out row. Say that the held-out-row condition stays the
    declaration's and the auditor's.

  Also add: "no design search pins before Q-158 merges". No search can pin before O-1 and O-6 are ruled anyway, so
  this costs nothing.
- **n-4.** Two copies still state the law without the cost: `prereg-discipline` l.70-72 ("against the nearer
  barrier") and the auditor's description line. Add the cost, and add both to `RACE_COPIES`.
- **n-5.** T l.262 and `feature-rules` l.65: "both legs settled alike". Say how. Suggestion: both legs take the
  as-walked leg's settlement under one rule (both stop-first or both excluded), so the pair's difference is zero by
  construction. Count the share of pairs settled this way.
- **n-6.** T l.358-361 and l.377-379: if a declaration closed by a failed calibration or power gate is followed by a
  new one, the new one cites the failed record, reports it beside, and uses a fresh seed block. A failed seed block
  is never reused.

**m-1 to m-8, diff-checked: each is answered.**
- m-1: the exit table, the fill-time law beside, n and its rounding, "overrides DN 1.7".
- m-2: "takes a k first", E-005 (d), the power re-stated.
- m-3: D-107's three facts.
- m-4: the red team's and the auditor's additions.
- m-5: the scout's file rule and its answer limits.
- m-6: the never lines and `.commit_msg_*` git-ignored.
- m-7: underlying; the runner's rule; the slippage keys; the step order; the `heldout_test` coverage; the ledger guard
  as a build requirement; the design note at 181eb44.
- m-8: `results-tracer`.

---

## What I tried that found nothing

- **The arithmetic, in exact fractions.** I re-derived the costed race's gross, net and floor bound by hand, and
  re-ran the stopped-walk check from the first read on lattice barriers: exactly zero.
- **The walk with max(x_stop, x_flat).** Every exit is at or above -c, so the clip never binds.
- **Remaining full-cushion text.** A search for `BinaryDraw's law`, `min(l, c)` and "nearer barrier" over `.claude/`
  and the template found only n-4's two paraphrases.
- **The tests.** `tests/test_design_search_template.py` and `tests/test_declarations_fixed.py` at 4e2f740: 30
  passed. The new hash test's positive control, a second hash, fails as it should.
- **The calibration path.** E-115's `docs/calibration/` regex reads the record's path.
- **Q-158 at 6ce8e6a.** Its rules 1-4 and token grammar cover the template's rules, except for the held-out-row
  condition (n-3).
- **The gatekeeper against E-204.** Consistent: "takes a k first", the repeat clause shown vacuous on the template's
  order.

**A note on my own process.** I briefly checked out 4e2f740 in the wt-lit worktree, which detached its HEAD. The
branch tip was the same commit, so no file changed, and I re-attached `wt/wt-lit` at once.

## What I could not check

- Whether the H3 build and the search runner will expose an exit reason for need and consistency exits. That is the
  vendored `last_trade["exit_kind"]`; whether the new runner keeps it is for the build to show.
- Q-158's own tests. They are outside this read.
