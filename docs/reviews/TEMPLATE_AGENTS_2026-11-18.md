# Red-team read: the design-search template and the updated agents, skills and commands (Wave 2.5, 2026-11-18)

**Target.** `wt/wt-lit` at ab0a8e4 (worktree `%LOCALAPPDATA%\stage2-extended-wt\wt-lit`), the 21 files of
`git diff master ab0a8e4`: `prereg/TEMPLATE_design_search.md` (cited "T l.N"), `prereg/TEMPLATE_family.md`,
`tests/test_design_search_template.py`, `.claude/agents/*`, `.claude/skills/*`, `.claude/commands/*`. Read against
`CHARTER.md` sections 2-5 (E-210, in force), E-204, E-207, E-210, E-211, `extended/reader.py`,
`vendor/stage2/propedge/contract/adapter.py`, `vendor/stage2/vendor/propsim/propsim.py`,
`vendor/stage2/propedge/campaign/lockstep.py`, `vendor/stage2/config/fills.yaml`, and the three-way test's design note
(`docs/plans/THREE_WAY_TEST_design.md` on `wt/wt-verify` at 181eb44, cited "DN") with its third read
(`docs/reviews/THREE_WAY_TEST_v3_2026-11-18.md`).

**The brief's hints.** The brief lists seven points to attack and calls the design note "ready". I took the points as
a scope, not as expected answers, and checked the note's text rather than its status.

**Labels (E-207 (2)).** **Blocking** means it could make a result wrong, or it removes a safeguard, which E-207 (3) does
not allow a workflow change to do. **Minor** means wording, a citation, or a clarification that changes no declared
rule.

---

## Verdict: **must be re-declared. Do not merge as it stands.**

Five blocking findings. Each fix is text in the template, the agents or the skills. B-3 also asks for a small
`extended/reader.py` change, which can be queued if the text carries the rule until it lands. Everything else reads
correctly:
- the `BinaryDraw` quote is verbatim and its law is described correctly;
- the stopped driftless walk has exactly zero gross expectation when its barriers are the booked ones;
- the merge checklist only adds lines;
- the gatekeeper's k rule matches E-204 in substance.

| id | label | one line |
|---|---|---|
| B-1 | blocking | The race and R-10's walk use the full cushion `min(l, c)`, not `min(l, c - x_stop)`. With m-3's stop-side costs the engine's floor clip binds and credits costs (N-5 / M-4 come back), and the lattice has no inward-rounding rule (N-4). |
| B-2 | blocking | Between section 7's pin and the whole-file pin, everything else can change, including what the deciding calibration and power gate read (their seeds, R-10's estimator, the statistic's text). Section 7's byte range is undefined, and no test checks it. |
| B-3 | blocking | The reader authorises `heldout_test` and `heldout_stress` from the whole-file pin, which is before the survey and the finalists' row. RD declarations can name held-out purposes, and the gatekeeper allows it. "Once" is per declaration and purpose, not per market, so a re-declared search reads the held-out years again. |
| B-4 | blocking | The long-run gate's quantile is "over coin seeds" only (T l.278, l.346). CHARTER 3.8 (c) says "over coin seeds and history-block resamples". The template loosens a floor with no row. |
| B-5 | blocking | `feature-rules` drops the pair rule's settlement ("contributes zero lift"). The no-harm and as-traded floors decide on the real path, comparing a resting entry with its reflection, so the stop-first fill-bar rule now favours the real resting side by construction. |
| m-1 | minor | R-10: "never their mean" holds per trade, but the as-run resolution split moves the composite through the contract's convexity. Say so, and add a diagnostic. Also list every terminal state's law and define the walk's clock. |
| m-2 | minor | The gatekeeper's k wording: "pins first" should read "takes a k first". Re-state the power gate if k moves past 13. Restate E-005 (d) for a search withdrawn after its held-out row. |
| m-3 | minor | The gatekeeper's confirmation item dropped D-107's "at most three a market", that NQ's held-back window is spent, and that the reserve becomes a window only by the operator's decision. |
| m-4 | minor | The red team and the auditor miss some CHARTER 3.6-3.8 points: sealed H4 outputs, the reverse reading, single use per market, the gate's denial rung, the Focused Trader Program off, each baseline (intersection-union). |
| m-5 | minor | The scout's challenger brief can open mixed files that hold held-out rows. A blocking point at the finalists' stage has no stated limit on what the lead may do. |
| m-6 | minor | The worker's twelve lines omit the "never" lines (NQ from 2026-07-17, vendor, the licence guard, results only from clean runs, measures traced). `.commit_msg_*` is not git-ignored. |
| m-7 | minor | Template wording: "per unit and instrument"; "no cushion is not taken"; the typed "a tick"; the run order's step 1; the held-out "beside" readings not named under a purpose; "the ledger writer refuses held-out rows" is claimed but not built; section 8's stale design-note status. |
| m-8 | minor | `results-tracer` item 8 still asks for "the family's cell count ... Stage 2 D-621 (5)". |

---

## Blocking

### B-1. The redraw's loss barrier ignores the stop-side exit cost, and the lattice has no rounding rule

- **Where.**
  - T l.172-190: "the search uses BinaryDraw's law", with `c' = min(risk, max(cushion, 0))`.
  - T l.199-203, m-3: "a loss at the cushion is booked the same way as a stop", that is, with the stop's slippage
    and costs.
  - T l.212-215, R-10: the walk's loss barrier is `min(l, c)` "in ticks", on "a lattice that divides both barriers".
  - The same law is repeated in:
    - the gatekeeper, item 5 (`.claude/agents/prereg-gatekeeper.md` l.74-78);
    - the red team, item 8 (`.claude/agents/red-team.md` l.55-56);
    - the merge checklist (`.claude/skills/merge-checklist/SKILL.md` l.78-80);
    - `feature-rules` section 5 (l.89);
    - `contract-engine` (l.133).
- **Evidence.**
  - `RandomDraw` in truncate mode at theta = 0 returns `+W` if `u < c/(c+W)`, else `-c`, with no cost
    (`propsim.py` l.119-130). The quote and the law in T l.175-186 are therefore correct, but cost-free.
  - The engine then clips the costed P&L at the cushion: `pnl = max(pnl, -cushion)` (`lockstep.py` l.475-477; DLL
    l.478-479).
  - DN 1.1 (N-5) fixed this: **L = min(l, c - x)**, "the build's redraw must be `three_way_arith.race_redraw`'s law".
  - The third read tightened it (M-4): **L = min(l, c - x_stop)**, with x_stop including the stop slippage, because
    "a stop-side loss passes the floor and the clip binds again, crediting the slippage".
  - The template adopts `BinaryDraw`'s cost-free cushion and then books the loss with the stop's slippage and costs.
    That is exactly the case N-5 and M-4 rule out.
  - R-10 races the same full cushion.
  - The N-4 deferral (DN l.292-297) asked this template for inward rounding, because "rounding outward and then
    clipping would bring B-1's edge back". R-10 says "a lattice that divides both barriers ... in ticks" and says
    nothing about a fractional cushion.
- **Synthetic checks (exact fractions, toy values, no data).**
  - A race with cushion 2, win 6 and exit cost 1/2, the loss booked at the cushion plus its cost and then clipped:
    the net expectation is -1/8, where the convention needs -1/2. Three quarters of the cost is credited back.
  - A stopped symmetric walk with an outward-rounded loss barrier, its loss clipped at the true fractional cushion:
    positive gross expectation.
  - The same walk with barriers on the lattice: exactly zero for every g, m in 1..5 and n in 0..14 steps.
- **The failure it allows.**
  - Near-floor trades on every design and baseline get part of their costs back, which is a positive edge in the
    deciding reading.
  - The credit grows with how often a design trades near the floor or the daily loss limit, so it rewards
    aggressive account policies. It is exactly a lever the search can find.
  - The oracle "zero gross expectation at every cushion" (T l.186, merge checklist l.78) passes, because the edge is
    in the net, after the clip.
- **Remedy.**
  - Replace "uses BinaryDraw's law" with: the race of DN 1.1 as M-4 amends it.
    - The loss barrier is L = min(l, c - x_stop): c is the room the engine hands the draw (floor or DLL, after the
      entry cost); x_stop is the stop-side exit cost, commission plus `stop_slippage_ticks`.
    - p = L/(L+g).
    - A trade with L <= 0 is not taken.
    - `BinaryDraw` is cited as the cost-free special case (x = 0).
  - R-10:
    - the walk's loss barrier is min(l, c - x_stop);
    - every barrier is rounded **inward** to the walk's lattice (N-4);
    - the walk's value at T is capped so that it plus the flatten-side cost never passes the floor;
    - the exact-fraction test runs over fractional cushions with unequal exit costs and asserts net = -(expected
      costs), not only gross = 0.
  - Change the gatekeeper's item 5, the red team's item 8, the merge checklist's redraw line, `feature-rules`
    section 5 and `contract-engine` to say the same.

### B-2. The two pins leave the calibration's inputs unpinned, and section 7's pin is not checkable

- **Where.** T l.261-266 says section 7 is "pinned first, alone ... (the LF sha256 of its text from this heading to
  the next); the whole file is pinned after the power gate". Also T l.380-385 (the seeds), T l.409-417 (the run order),
  and the gatekeeper's "On approving", steps 2-3 (l.140-145).
- **What can change between the two pins.** Every section except 7, including what the calibration and power gate
  run on (T l.410-417, steps 2-4):
  - Section 12's seeds. The "deciding calibration and the power gate" seed `<S5>` (T l.382) is written into the
    file only at the whole-file pin, after the run it seeds. The calibration can be run, read, and its seed then
    "declared".
  - Section 5's R-10 estimator window and unit (T l.218), and the m-2 choice. These change the baselines' redrawn
    outcomes, which the power gate reads from H4.
  - Section 8's statistic text (T l.292-294), which can drift from section 7's "deciding bound's form".
  - Section 10's draft-specific wording.
- **Why this matters.** CHARTER 3.9 says "None is changed after a search-year result except by re-declaring the
  search", and the calibration and the power gate are search-year results. E-115 already provides the mechanism for
  this: a calibration plan's seeds and rules pinned before it runs (`tests/test_declarations_fixed.py` l.31-39).
- **Section 7 is not provably byte-identical.**
  - "From this heading to the next" does not say whether the heading line and the trailing blank line are included,
    so two people get two hashes.
  - The gatekeeper's rename "replace[s] `F-XX` in its text" (l.140-141). If section 7 contains `F-XX` (a natural
    thing in its source column), its bytes change.
  - The template says "delete ... the template's instructions in italics" without saying when. Section 7 carries an
    italic block.
  - No test compares the section-7 hash with the pinned file. `test_declarations_fixed.py` reads whole-file pins
    only.
  - Worse, if the lead writes the section-7 row in the natural form, `` `prereg/F-13_x.md` sha256 `<section hash>` ``:
    - the hash test fails;
    - `reader.pins()` returns two hashes for the file, so `pinned != {sha}` (`reader.py` l.452) and the held-out
      test is refused for good.
  - The reviews are not placed in the run order. A red-team read after step 2 can only re-declare section 7.
- **The failure it allows.**
  - A calibration or power gate re-seeded after a fail, with nothing on record.
  - An R-10 estimator tuned until the gate passes.
  - A section 7 silently edited between the pins, with nothing to detect it.
- **Remedy (either one).**
  - (a) Freeze the whole file at the first pin. The pinning row records the LF sha256 of the **whole renamed file**
    (F-number assigned by the gatekeeper first), in a form the PIN regex does not match, for example
    `` frozen-sha256 `...` ``. The pin after the power gate must cite the same hash. Any change is a new declaration
    and a new pinning row.
  - (b) Keep the section pin, but:
    - define the byte range exactly: from the first byte of the line `## 7.` up to, not including, the first byte of
      the line `## 8.`, LF, italics already deleted;
    - put sections 5, 8, 9 and 10's draft text and section 12's S5 inside the frozen range, or run the deciding
      calibration only under its own pinned plan (`docs/calibration/`, E-115) or H3's pinned declaration, never under
      the search's unpinned S5;
    - add a helper and a test: for every pinned search, the section hash in its row equals the range's hash in the
      pinned file;
    - forbid `F-XX` inside section 7.

  Either way, add to section 14: the scout's brief, the red team and the gatekeeper read the draft **before** step 2.

### B-3. Held-out reads are not tied to the run order or to the market

- **Where.**
  - T l.430-439: "authorises a read ... for a purpose named on the line below of the pinned file ... once per
    purpose".
  - T l.63-67: single use per market.
  - The gatekeeper's RD clause (l.133-134): "it reads the held-out years only as its own row allows".
  - `extended/reader.py`: `_family` l.435-457 and `_once` l.478-501.
- **Evidence.**
  - `authorise` for a family or RD purpose checks four things: the file is pinned, the purpose is on its line, the
    run is clean, and no earlier read of the same `(declaration, purpose)` exists. Nothing else.
  - The file is pinned at step 4 (T l.417), before the survey (step 5), the finalists' row (step 7) and the
    held-out row (step 8). So from step 4 any clean run can read the held-out years under `heldout_stress` or
    `heldout_test`, while the rounds are still being chosen.
  - `heldout_stress` can also run before `heldout_test`.
  - "Once" is keyed by the declaration's path. A failed F-13 re-declared as F-14, with one byte changed and the house
    line kept (T l.433, "Keep the house names"), gets fresh reads. That is the re-declaration escape from the kill
    which CHARTER 3.6 (c) forbids, and nothing mechanical stops it.
  - A draft that marks "does not spend NQ's held-out years" (T l.63) still carries the line, so it can read them.
  - RD declarations follow the same rules. The gatekeeper's new RD paragraph lets an RD reading read the held-out
    years before the market's verdict. CHARTER 3.6 (a) and (c) and the terms table say they are "read only by a
    search's held-out test, once per market".
  - `registered_design` reads of P-14, P-15 and P-16 on the held-out block are "never limited to once"
    (`reader.py` l.36-42). Under the new convention such a read is new information about the comparators.
- **The failure it allows.**
  - The finalists are chosen or re-ordered after a held-out look.
  - A second held-out test on NQ under a near-copy declaration.
  - RD or registered-design reads of the comparators on 2024-2026 during a search, each of which only enters the
    ledger afterwards, if anyone lists it.
- **Remedy.**
  - Text, now:
    - T section 14 states that a `heldout_*` read is made only after the finalists' row and the held-out row, both
      naming this file's sha256.
    - A draft that does not spend the market's held-out years carries **no** `Judged-block reads:` line.
    - The gatekeeper refuses:
      - an RD declaration naming any held-out purpose before the market's verdict row;
      - any design-search draft whose market already has a `heldout_*` read by another declaration in
        `results/read_ledger.jsonl`.
    - The auditor checks every `heldout_*` ledger line's time against the two rows' commits, and no
      `registered_design` judged read between the pin and the verdict.
  - Reader, queued:
    - `heldout_*` purposes require `authorised_by="E-NNN"`, a row that names the declaration and its finalists'
      hash;
    - a market-level once rule: refuse a `heldout_*` read if the ledger holds one by another declaration on the same
      bars, unless a row names it;
    - refuse `registered_design` judged reads while a pinned design search on the market lacks a verdict row.

### B-4. The long-run gate's quantile drops CHARTER 3.8 (c)'s history-block resamples without a row

- **Where.**
  - T l.278 (section 7): "over coin seeds, given the history (the design note's 4.4)".
  - T l.345-346 (section 10 (c)): "above zero at the pinned lower quantile over coin seeds (the design note's 4.4)".
- **Evidence.**
  - CHARTER 3.8 (c), in force at E-210's sha256, says: "above zero at a lower quantile over coin seeds **and
    history-block resamples** pinned with 3.9's inputs".
  - DN 4.4 argues that held-out resamples at 504 sessions cannot be formed (the coordinator's m-11). It puts the
    search years' history-block reading "beside".
  - No decision row amends the charter: E-210 and E-211 do not mention m-11.
  - The template's own rule (T l.17-19) is that a draft "may loosen none [of the floors] without the operator".
- **The failure it allows.** A finalist whose bankroll growth clears zero on coin luck, given a favourable held-out
  history, passes a floor that the charter would have read over histories too.
- **Remedy.**
  - Keep both readings as deciding: the held-out quantile over coin seeds (DN 4.4) **and** the search years'
    history-block quantile at the same pinned level, both above zero.
  - Or record a row amending 3.8 (c). Because it loosens a floor, that row is the operator's (DIRECTIVE Part 1).

### B-5. `feature-rules` removes the pair rule's settlement, and two deciding floors now read a biased pair

- **Where.** `.claude/skills/feature-rules/SKILL.md` l.57-63, with T l.140-141, l.351-354 and CHARTER 3.5 and 3.8 (c).
- **Evidence.**
  - Before: "a pair whose fill bar touches either trade's stop or target **contributes zero lift**, is counted and
    its share reported and capped".
  - After: "... is counted, its share reported and capped". There is no settlement, and the template has no field
    for one.
  - For a resting entry, price reaches the fill from the side of the trade's target, so the fill bar's pre-fill
    range sits on that side.
    - Stop first, target ignored on the fill bar: the real trade's target touches are thrown away.
    - The reflected trade's stop now lies on the pre-fill side, so the same pre-fill range stops it out. The
      reflected trade is penalised.
    - This is the predictable sign of the Phase 0 audit's D-1 and D-13.
  - The no-harm floor (the real resting side against the reflected one, search years) and the as-traded floor
    (held-out) are **deciding** floors read on the real path (CHARTER 3.8, "the one exception").
- **The failure it allows.** A resting trigger traded as its real order clears the no-harm floor through the fill-bar
  artefact, and a playbook then trades the real resting side. Removing the neutraliser weakens a safeguard, which
  E-207 (3) does not allow.
- **Remedy.**
  - Restore a settlement: in any reading that compares a resting entry with its reflection (the no-harm floor, the
    as-traded floor, the path-structure gap), a pair whose fill bar touches either leg's stop or target contributes
    zero difference (both legs settled alike). It is counted, its share reported and capped.
  - Add a line to T section 5 that carries it.

---

## Minor

**m-1. R-10's split, the clock and the terminal states (T l.204-223).**

What holds:
- Given its inputs (g, l, c, T and the step count), each law's draw comes from coin-field keys of its own kind,
  independent of the reflection coin and of the real path.
- So each trade's expected gross outcome is zero conditional on the split, and the split cannot add a mean, once
  B-1 is fixed.
- I checked the walk's exactness in exact fractions, as noted under B-1.
- The step variance is read from bars closed at or before the alert. That carries no future information, and T is
  known at the fill.

Three gaps:
- **(i) "Never their mean" is true per trade, not for the verdict.** Which trades reach a time limit is the real
  path's resolution structure. Momentum or mean reversion changes how often a barrier is hit within T. Under the
  contract's convexity a different spread is a different expected composite. CHARTER 3.2 keeps "resolution ... as
  run", so this is a declared channel, but say it plainly. Remedy: a "fill-time law" reading beside, in which every
  trade takes the stopped walk with T the limit known at the fill, so it uses no post-fill path. Its gap from the
  deciding reading is printed per component.
- **(ii) Every terminal state needs its law.** Name the law for each of:
  - a run trade closed by the floor or the DLL (not at its stop);
  - a stop gapped through;
  - a news-window flatten;
  - any other exit.

  A test should hold the mapping exhaustive.
- **(iii) "The step variance is the declared volatility estimator" conflicts with a lattice whose step size is fixed
  by the barriers.** State that the estimator sets the **number of steps**, n = round(sigma^2 T / s^2), with the
  rounding rule. Also reconcile with DN 1.7's "causal volatility per bar of the trade's holding window": the
  template's at-the-alert reading is the stricter one, so say that it overrides.

**m-2. The gatekeeper's k rule (l.108-118) against E-204.**

It is consistent in substance. A search is not counted until its held-out row, a repeat row applies if the order is
broken, and the arithmetic is right (k = 13: 0.05 / 182). Four wording fixes:
- "if no other declaration pins first" should read "if no other declaration takes a k first". Under the template,
  pins spend no k; held-out rows do.
- The template's order (the held-out row, then the run, T l.422) makes E-204's "between its held-out run and that
  row" clause vacuous. Say so, or keep run-then-row as E-204 wrote it.
- The power gate is computed at k = 13. If another search takes 13 first, re-state the power at the new level
  before the held-out run, because exit (B) cites it.
- Restate E-005 (d): a search withdrawn after its held-out row still spends its k. The old item 4 said this and the
  new text drops it.

**m-3. The confirmation item (gatekeeper l.63-65).**

The old text said:
- at most three confirmations a market (D-107);
- NQ's held-back window was spent by P-05, P-06 and P-10;
- NQ's reserve becomes a confirmation window only by the operator's decision.

The new text says only "count ... and report it". Restore the three facts. They are report-only, but they are
material to CHARTER 5 (A).

**m-4. CHARTER 3.6-3.8 points missing from the red team and the auditor.**

- **Red team:**
  - H4's sealed held-out outputs unopened (3.6 (e));
  - the reverse reading not run before the held-out test (3.6 (g));
  - "each baseline" (an intersection-union test, not the best baseline only, 3.8 (b));
  - the long-run gate's quantile, its complete-start minimum and its D-145 tier-3 denial (3.8 (c));
  - the verdict settings: 0 % denial, the placement off, the Focused Trader Program off.
- **Auditor:**
  - 3.6 (c) single use per market, checked against the read ledger;
  - 3.6 (e) and (g);
  - the gate's denial rung against the verdict's 0 %;
  - "Focused Trader Program off" as a verdict setting (item 9 lists 0 % and the placement only).

**m-5. The scout's challenger brief (`.claude/agents/scout.md` l.33-65).**

- It may read "result files of the search years". Some files hold both search-year and held-out rows (RD-03's
  whole-window readings, `results/breakeven_fidelity_2*.csv`). Say that a file holding any row dated from
  2024-01-02 is not opened by the brief.
- At the finalists' stage, "the lead answers every blocking point" needs a limit. An answer is text, or the search
  closes or is re-declared. It never edits the finalist list or its order, which come from the pinned rule.

**m-6. The worker's pre-hand-back checklist (`.claude/skills/worker-protocol/SKILL.md` l.71-102).**

Its citations check out:
- Q-108_plan_v2 MATERIAL 3;
- DRAFT_F-RL3 B-2 and B-4;
- DRAFT_F-04 B-3;
- DRAFT_RD-05_v2 B-1;
- MEASURES B-1 and B-5;
- AMENDMENTS B-4 and B-5;
- BUILD_RD-05_coin B-1 and B-2.

The 1.75 GB rule is stricter than the hook's own 1.5 GB wait (`scripts/install_hooks.py` l.79), which is fine.

Missing, though each is in the merge checklist the lead runs anyway:
- no read of NQ from 2026-07-17;
- nothing under `vendor/` changed;
- the licence guard (no price recoverable from a result);
- no result file or record file written on the branch;
- every journey measure is the function `docs/MEASURES.md` names;
- the redraw's oracle is the cost-aware one (B-1).

Add them as a line 0. Also add `.commit_msg_*` to `.gitignore`, so a message file left behind can never be staged.

**m-7. Template wording.**

- T l.193: "one shared driftless lattice path per unit and instrument". DN N-4 says "per underlying, never per
  instrument". The template defines instrument as underlying, but write "underlying".
- T l.186: "A trade with no cushion is not taken" is the runner's rule. `BinaryDraw` books a zero for it and counts
  a trade (`propsim.py` l.125-130, `lockstep.py` l.480-483). Say whose rule it is.
- T l.200: "the stop exit slipping a tick" types a rule value. Cite `fills.yaml` `stop_slippage_ticks`, and
  `flatten_slippage_ticks` for R-10 (T l.220-221).
- T l.411: step 1's "this declaration pinned" cannot hold for steps 2-3, which run before the pin. Split the
  refusals by step.
- T l.437-439: the held-out "beside" readings of section 11 need a purpose that covers them. These are:
  - the five-minute cell;
  - the as-walked result and the path-structure edge;
  - the denial ladder;
  - the model-side held-out reading.

  Name them under `heldout_test`, or they cannot be read.
- T l.79: "the ledger writer refuses held-out rows". No such guard exists: `VariantCounter` is used unchanged
  (`extended/breakeven_readings.py` l.596-601). Write it as a build requirement with a test.
- T l.285-287: section 8 says the design note is "being revised after its red-team read". It is at 181eb44 after
  three reads, so cite the commit.

**m-8. `results-tracer` item 8 (l.59)** still asks for "its family's cell count and the program's running family
count (Stage 2 D-621 (5))". It should ask for every design tried and the program's k.

---

## What I tried that found nothing

- **The `BinaryDraw` quote (point 7).**
  - The template's signature lines match `adapter.py` l.139-161 byte for byte, and the test enforces it.
  - `settlement = "race"`, `W = rr x risk`, `c' = min(risk, max(cushion, 0))` and `p = c'/(c'+W)` at theta = 0 all
    match `propsim.py` l.119-130 and l.388-395.
  - The DLL as the nearer barrier is the engine's `room` (`lockstep.py` l.452-455).
  - Zero gross expectation at every cushion holds for the cost-free law.
- **m-2's and m-3's text against E-210 and the third amendments read.**
  - m-2 refuses overlap until the joint law is defined, as the read asked.
  - m-3 (stop slip, target limit with none) matches `fills.yaml`'s assumed profile (l.198-215).
  - The defect is only in how m-3 combines with the race (B-1).
- **The merge checklist (point 5).** The diff only adds lines. Identities, typed figures, the licence guard,
  vendored integrity, clean runs, `verify_result` and the 2026-07-17 refusal are all kept. The review rule matches
  E-207 (2) word for word in substance.
- **The other rewrites, checked for weakening.**
  - `prereg-discipline`, `contract-engine`, `result-provenance`, `data-integrity`, `audit`, `close-check`, `trace`,
    `status`, `brief`: the retired lines are replaced by CHARTER 3.8's, and no floor is dropped.
  - Only the `feature-rules` pair rule (B-5) and the gatekeeper's confirmation facts (m-3) lost content.
  - `/brief` forbids held-out figures before the verdict row and never opens sealed files.
- **The R-10 clock.** It is read from bars closed at or before the alert, and T is known at the fill. No look-ahead.
- **The seed keying and the antithetic twin.** The template's description agrees with DN 1.5 and 2.3. I confirmed
  numpy's trailing-zero collapse with a synthetic `SeedSequence` check.
- **The `Judged-block reads:` line.** It parses under `reader.DECLARED_LINE`. Neither purpose carries a choice word,
  and the test asserts both.
- **The template test.** `tests/test_design_search_template.py` on the branch: 17 passed. Its checks can fail: the
  glob scan and the signature extraction are both non-vacuous.

## What I could not check

- Whether any existing `results/variants.jsonl` line already holds a held-out reading. That needs a read of the
  ledger's rows against their manifests, which is light, for a worker.
- The restart plan's Wave 1.4 source for the checklist's "most frequent first" ordering.
- Whether `scripts/status.py` reports the parts `/status` now lists. The command says it does not yet.
- The reader change in B-3 needs code and tests, specified there. I did not run anything heavy, and read no bar and
  no held-out outcome.
