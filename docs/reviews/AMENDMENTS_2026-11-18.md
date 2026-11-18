# Red team (cold): the draft constitution amendments, 2026-11-18

Target: `docs/plans/AMENDMENTS_draft_2026-11-18.md` (untracked, read 2026-11-18), against its source
`docs/plans/RESTART_PLAN_journey_objective.md`, the current `CHARTER.md`, `CLAUDE.md`, `DIRECTIVE.md`, `DECISIONS.md`
(E-001, E-007, E-008, E-014, E-015, E-023, E-202 to E-206), `prereg/RD-04_volatility_drift.md`,
`prereg/RD-05_firm_modes.md`, `vendor/stage2/docs/USER_MILESTONES.md` and Stage 2 D-145. Read-only; this note is the
only file written. No result figures, no seed literals.

**What I was told and set aside.** The brief listed nine questions to attack. I treated them as a starting list,
not as the answers wanted, and read the draft from scratch as well. The brief also says E-207 puts the operator's
confirmation and the blocking/minor review labels in force. **E-207 is not on disk**: it is not in `DECISIONS.md`'s
working tree or its staged index, and E-206 records the review labels as "proposed, not approved". I use the labels
because the brief asks for them. Each finding also carries the standing severity scale.

**`docs/MEASURES.md`:** not reviewed. `wt/wt-user`'s tip is master's `f80ae5c`, the file is not on that branch, and
it is not in the `wt-user` worktree's `docs/`. Every finding below that touches a measure's definition still applies
once the file exists.

## Verdict: **must be re-declared** (12 blocking, 10 minor)

The direction of the amendment is coherent, and section 4 is carried over byte-for-byte. The pass line it writes is
not yet a rule that can be applied without later choices, though. Several of its parts can be set, or are already
informed, by the years it calls held out. Its calibration requirement passes any statistic. Its floor (the long-run
gate) is undefined under its own zero-edge assumption. Its comparison with the baselines has no fixed convention. Its
"zero edge" is not zero for resting orders. These defects change the declared rule (section 3.8 and the E-NNN row), so
the texts should not go into force as drafted. **Once the blocking findings are fixed, the texts can go into force.**
All twelve fixes are text-level rulings, not experiments. Three of them (B-4, B-9, B-10) also need an experiment
before the first search declaration is pinned, and they say which.

---

## Blocking

### B-1. "Held-out years" are not unread, and nothing makes them single-use (MATERIAL / CHANGES-A-CONCLUSION if the late block is the default)

- **Where:** draft 3.6 (iii) (l.158-161: "the held-out years, which the search never read"); 3.3 (f) (l.129-130: "the
  map and the ledger persist, so the next firm ... starts from them"); 3.7 (l.164-168: "Each confirmation spends one
  k"); F-3 (l.530-533).
- **Evidence.** Before any new search exists, the program has already read the years most likely to be held out
  (2024-2026), and read them for exactly the comparators the pass line uses:
  - P-14 was fixed as R\* from whole-window `user_journey.csv` (Stage 2 D-626).
  - P-14's rung map and P-16's mark cutoff were resolved on the whole window (E-203 S-2).
  - P-16's stop was chosen on each block separately (Stage 2 D-554, cited in RD-04's table).
  - RD-04 (c) replayed P-14 and P-16 on the late block.
  - RD-05 (l.309) says outright that "the late block is late development, not out of sample".
  - Q-17/E-201 read every user measure beside the baselines.
  - Stage 2's signal search read 2024-2026.
  - The lever space is to come from RD-03, RD-04 and RD-05 (plan 5.1), which read the whole window.

  Beyond this, the draft lets successive searches confirm on the same years. Topstep's first confirmation reads them;
  then a second Topstep search, or another firm's search "starting from the Topstep map", is declared by a researcher
  who has seen them.
- **Failure allowed.** Suppose the first Topstep confirmation fails and a second search is declared. Its lever ranges
  and trigger choices are written knowing which shapes held up on 2024-2026. Its confirmation on 2024-2026 then rejects
  at a nominal 0.05/(k(k+1)), but the true level is unknown. The program budget assumes that each hypothesis is fixed
  before its test data are seen, so it does not protect against this.
- **Fix.**
  - (a) Define "held out" in 3.6 as two things: unread by the search's code, and unused by any choice in its
    declaration.
  - (b) Require every search declaration to carry a **held-out read ledger**: every prior read of those years, for its
    comparators and its trigger families. Use the RD-04 leak-clause form (its section 9.3: "written after this reading;
    no figure cited"). Print the level as nominal beside the verdict whenever the ledger is not empty, as E-203 S-2
    did.
  - (c) Make held-out years **single-use per market**. After a confirmation reads them, a later search on the same
    bars cannot carry on them. Its confirmation is either a described reading or moves to data not yet read (the
    purchase window, or more history).
  - (d) Never let the persistent map or `results/variants.jsonl` hold held-out results that a later search reads.
  - (e) Name the default split in the charter: 2020-2023 / 2024-01-02..2026-07-16, so that the ledger can be checked
    against every existing record. Also say that its comparators are already read.

### B-2. Limits, budgets and the composite's other ingredients can be set from held-out data or after the search's results (MATERIAL)

- **Where:**
  - Draft section 2, l.102-104: limits "proposed by the lead from the re-baseline", with no window named.
  - 3.9, l.187-195: only the **weights** are pinned, and only "before any held-out year is read".
  - Plan Wave 4, H4: the baselines "under the full new scorecard, every measure", with no window named. 4.1 is "search
    years only", but 4.2's limits and budgets are not restricted.
- **Evidence.** The pass line depends on many inputs besides the weights:
  - the limits and their margins;
  - the bankroll budgets of (24), which enter both the limits and the composite's P-under-the-bankroll-stop;
  - the dimension definitions and their normalisers or loadings from 4.1;
  - the planted "size that matters" and the power target (3.7);
  - "most years" and the regimes (3.6);
  - the choice of composite over fallback (3.9: "if the weights cannot be set" -- set when, and by whom?).

  None of these is in the pin list. The baselines' held-out journeys come out of H4 before 4.2 if H4 runs on all
  years.
- **Failure allowed.** The operator and the lead see the baselines' held-out profile from H4, for example that P-14's
  bankroll stop bites hard in 2024-2025. A budget or a weighting can then be proposed that favours the dimension where
  the comparator is weak in exactly the years the test reads. The fallback can likewise be invoked after a look.
- **Fix.**
  - H4 runs on search years only, with the runner refusing held-out sessions (RD-04's `band_mark` guard pattern).
    Alternatively, its held-out output is written sealed (hash recorded, not opened) until the confirmation.
  - Replace "the weights ... pinned before any held-out year is read" with: **every input of 3.8 and 3.9 is pinned in
    one row before the survey runs.** That means the limits, margins, budgets, dimension definitions and normalisers,
    weights, composite or fallback (one, never both), size that matters, power target, regimes, "most years", the
    finalist rule (B-8) and the plateau rule.
  - State that none of them is changed after a search-year result except by re-declaring the search.

### B-3. Search-year starts straddle into the held-out years: no purge, no embargo (MATERIAL)

- **Where:** draft section 2's unit, l.66-71 ("the design's trades replayed in historical order"); 3.6; 3.9's search
  and survey "search years only". The measures run to month 12: (12), (13), (15), (16) and (25). D-145's gate reads a
  two-year path.
- **Evidence.** `USER_MILESTONES.md` (l.12) reads a horizon h "only on starts with at least h sessions left", with
  "left" counted against the development window, not against a split. Take a start in late 2023. Its months 1-12 (and
  the gate's two years) run on 2024 bars. Nothing in the draft truncates these paths.
- **Failure allowed.** The survey and the surrogate rounds score designs on paths that read 2024 to 2025 bars. The
  search therefore reads the held-out years, and 3.6 (iii) is false as soon as any 12-month measure is used.
- **Fix.** In 3.6:
  - A search-year start is read at horizon h only if h sessions remain inside the search years. This purges a
    12-month strip, and a two-year strip for the gate.
  - Held-out starts read only held-out sessions for their outcomes. Causal look-backs into the search years are
    allowed for the volatility normalisers.
  - With an interleaved split, embargo both sides.
  - State the consequence: the held-out years hold even fewer complete 12-month starts. B-9 counts this cost.

### B-4. The calibration check as written cannot fail, and the unit of replication is unstated (CHANGES-A-CONCLUSION)

- **Where:** draft 3.7, l.164-166 ("two identical designs must 'differ' no more often than the level"); 3.6 (i)
  ("across coin seeds ... paired"). In the plan, the calibration run H3 is in Wave 3, before the composite exists in
  Wave 4.2.
- **Evidence.** Under 3.6's pairing, two identical designs get the same seeds on the same days, so their difference is
  identically zero on every seed and every history resample. Any statistic, however lax, "differs" no more often than
  the level. The check has no content.

  Separately, "holds across coin seeds" says nothing about where the test's variance comes from. History is fixed, so
  adding seeds shrinks a seed-based standard error toward zero while the start-day luck, the dominant noise
  (`user_drivers.csv` `design_vs_luck`), stays the same. E-007 (1) already found that Stage 2's moving-block
  percentile bound misses its level on the data's own dependence.
- **Failure allowed.**
  - A statistic that treats seed × start as independent replicates passes the vacuous check. It then rejects at
    k = 13's level for a difference that is pure start-day luck.
  - Or a calibration certified on a Wave 3 statistic is cited for a composite pinned in Wave 4.2 that was never
    calibrated.
- **Fix.** Rewrite 3.7's calibration clause:
  - **Non-degenerate nulls.** Use distinct designs, or a design against a placebo, whose expected composites are equal
    by construction while their trades and timing differ. Examples: a design against itself with an independent seed
    stream; synthetic paths carrying NQ's dependence with a planted zero.
  - **History is the replication unit.** Seeds are averaged within each history resample. The block length is at
    least the longest horizon in the composite.
  - **Whole-rule calibration** (E-007 (f)): of the exact pinned composite together with the limit checks and the
    (ii)-(iii) conjunction, run after 4.2 and before the search's pin.
  - **Experiment needed:** this is H3, re-specified on the pinned composite. Heavy; one run of the size of the
    planned H3.

### B-5. The baselines' convention is open (F-5), and both obvious choices bias the comparison (MATERIAL)

- **Where:** draft 3.8 (b), l.177-178; terms table, l.61; F-5, l.536-538.
- **Evidence.**
  - Registered P-14/P-15/P-16 rows are on the `verdict` arm, with every R shifted down to the gate's lower bound
    (`USER_MILESTONES.md` l.12-13). That handicaps the baselines.
  - Registered model sides on the `point` arm carry sides whose rungs and cutoffs were resolved on the whole window
    (E-203 S-2). Their held-out lift, positive or negative, enters the difference.
  - The new designs run coin sides with no shift. "The best baseline" is not said to be fixed before the read.
- **Failure allowed.**
  - (i) Design on coin sides against the baselines on the verdict arm: the design "beats" P-14 by the size of P-14's
    downward shift, without changing the user's journey at all.
  - (ii) Against model sides: a design fails or passes on the sign of P-14's held-out side lift, which is the one
    thing the zero-edge objective says is not judged.
  - (iii) "Best baseline" picked by point estimate on the held-out years and tested alone: the design can clear that
    one while a noisier baseline is not beaten at its bound.
- **Fix.**
  - In 3.8 (b), every baseline runs under **the same convention as the design**: the zero-edge sides of 3.2 under the
    same seed keying, the same fill, cost and latency model, no arm shift, and the same verdict settings.
  - The registered rows are reported beside. A runner identity shows that each coin-sided baseline's trade times and
    brackets equal its registered ones path for path.
  - "Naive coin harvesting" has its levers fixed in the declaration before the survey.
  - The design must beat **each** baseline (an intersection-union test, each comparison at the full level), or "the
    best" is fixed on search years before the read.

### B-6. Zero edge is not zero for resting triggers (MATERIAL)

- **Where:** draft 3.2 (l.115-117); terms (l.53: triggers include "the entry direction"); D-5 (l.338-341, "its side
  under the zero-edge convention the search declares"); F-8.
- **Evidence.** E-203 B-1 and E-204 NB-1 already showed this: a resting entry's fill conditions on the path, so
  coin-chosen sides on limits and stops do not give zero expectation.

  I ran a small synthetic check, exploratory, with no file kept in the repository. It used AR(1) price increments, a
  fair coin choosing the side, a limit or stop at a fixed offset, a symmetric bracket after the fill, and gap-aware
  fills: a limit at its level or better, a stop at its level or worse.
  - On a martingale, limits and stops had the same mean.
  - With momentum, coin-sided stops moved above that mean and coin-sided limits below it.
  - With mean reversion, the two moved the opposite way.
  - The fill-price convention at gaps alone also moved the mean, before any dependence.

  So "coin sides" on resting orders bring back an edge measured in-sample, through the path's serial dependence and
  the fill model. The 3.3 search will select levers on it: entry type, offset, session.
- **Failure allowed.** A survey on 2020-2023 picks stop entries in a session whose bars trended. The finalist's
  "zero-edge" composite includes that drift. It is an edge under another name, unpriced and possibly not persistent,
  and the objective says designs are never judged on edge.
- **Fix.** Define zero edge operationally, for every entry type, in 3.2:
  - The fill (time, price, supply) comes from the real order.
  - The post-fill path is reflected about the fill price with probability one half, coin-seeded. The gross
    expectation is then exactly zero, while timing, resolution speed and clustering are kept.
  - The as-traded resting side's outcome and E-204's decomposition are reported beside.
  - Add a floor: the design still beats each baseline at the point estimate with the as-traded sides (adverse
    selection stress).

  Until this is written, resting triggers are described only (D-5 already hedges; 3.2 does not).

### B-7. The long-run gate and the verdict arm are undefined under zero edge, yet the gate stays a floor (MATERIAL)

- **Where:** draft 3.8 (c), l.179-181 ("the long-run gate (growth on the required bankroll at the bound above zero,
  Stage 2 D-145)"); section 2, l.69-70 (Stage 2's measures "used unchanged"); the CLAUDE.md block, l.268-269; F-6, F-7.
- **Evidence.** Stage 2 D-145's gate is the median log growth out of sample, with the trade outcomes shifted so their
  mean equals the one-sided 95 % lower bound of e, at **25 %** tier-3 denial. Under coin sides, e is zero by
  construction, but a sample estimate of e is noise. Its lower bound is therefore a random negative penalty, while
  setting e to exactly zero gives the zero-edge campaign's growth. These two pass and fail differently.

  Stage 2's scorecard definitions are read on the `verdict` arm (`USER_MILESTONES.md` l.12-13). "Used unchanged" thus
  imports the arm that the draft drops.
- **Failure allowed.** A declaration picks the gate's form after seeing which form the finalist passes. Or two
  auditors read the same run with opposite verdicts.
- **Fix.**
  - Write the gate in 3.8 (c): median log growth of the required bankroll over D-145's horizon, sides under 3.2's
    zero-edge convention with no shift, with fees, latency, tier-2 consequences and D-145's tier-3 denial applied.
    Above zero at a declared quantile over coin seeds × history resamples. Say whether the denial is 25 % (D-145) or
    0 % (the verdict).
  - Section 2: "Stage 2's definitions, read on the zero-edge arm in place of `verdict`".
  - 3.10: the `verdict` arm is retired.
  - The auditor and the results-tracer files that read money from `verdict` (draft section 5) follow.

### B-8. "One hypothesis, one k" is contradicted by plural finalists, latency variants and the fallback (MATERIAL)

- **Where:** draft 3.7, l.164 ("A declared search's **finalists** are confirmed"); 3.9, l.197 ("tests the composite
  once (one hypothesis, one k)"); 3.5's latency clause with "the five-minute cell beside every pick"; E-202 (2)(c)
  ("counted in the cells and the multiplicity"); 3.9's fallback.
- **Failure allowed.** Three ways:
  - Three finalists are each tested against the best baseline at 0.05/(13·14). Family-wise error is about three
    times the level.
  - The finalist is tested at L = 2, and the five-minute cell is "beside" but also tested.
  - The composite fails and the fallback is then read.
- **Fix.** In 3.7:
  - Either one design per k, chosen on search years by a rule declared before the survey, or an ordered list fixed
    before the held-out read and tested by fixed-sequence testing at the full level, stopping at the first failure
    (E-203 S-1's precedent).
  - Each finalist is confirmed at its own L, and the five-minute cell is reported only.
  - The fallback is pinned instead of the composite, never after it.

### B-9. The pass line's power is required but never secured; E-007 (2) is not answered (CHANGES-A-CONCLUSION for exit (B))

- **Where:** draft 3.7 ("shown to have power ... at a power target the declaration fixes"); 3.8 (a)-(c); 3.6 (ii)
  ("most years and both volatility regimes"); section 5 (B).
- **Evidence.**
  - E-007 (2) found that the judged block holds only a few dozen independent starts, so a P-based rule could carry
    only near-P-14 variants or large contract-shape effects. That is the reason E-008 left P.
  - The new line again judges journey measures on the held-out years, at 0.05/(k(k+1)). Paired seeds remove coin
    noise but add no history.
  - The 12-month measures have fewer complete starts still (B-3).
  - The line is a conjunction: every limit with a margin (B-10), the composite, "most years", "both regimes" (a
    late-only held-out block may not contain both of RD-04's regimes), and the floors. Each conjunct lowers power.
  - 3.7 says power must be "shown", but not what happens when it is not.
- **Failure allowed.** The line is close to powerless at k = 13. Every search ends in exit (B), and the record reads
  as "no design helps users" when it means "this test cannot see it". This is the memory `check-power-of-strict-rules`
  case.
- **Fix.**
  - A **pre-pin power gate** for the whole conjunctive line, run before the search is pinned. Use synthetic paths with
    NQ's dependence and design pairs from search years, at k = 13's level, at the operator's "size that matters".
  - If the line has no power at the target, the search does not pin. The operator's data decision (DIRECTIVE's power
    paragraph: older bars or QuantConnect, both purchases or setup) is put to them **before** the search, not after a
    failure.
  - Define (ii) on held-out years with regimes that exist in them, or drop "both regimes" from the deciding test and
    report it beside.
  - Exit (B) states the line's power.
  - **Experiment needed:** heavy, of H3's size, and it can share H3's run.

### B-10. Hard limits with the burden of proof on the design: no power shown, and E-015's operator condition dropped (MATERIAL)

- **Where:**
  - Draft section 2, l.102-104 (limits "each with a margin wider than its measurement noise");
  - 3.8 (a), l.176 (the design "stays inside every operator limit with a margin wider than its noise");
  - 3.10, l.204 (E-015's "a limit never fails a design" superseded);
  - E-015, which also carries the operator's condition: "the limits must not fail profitable models by being too
    strict".
- **Evidence.** Two margins are stacked. The limits are set loose by their noise, and the design must also show it is
  inside by more than its own noise. With several limits in conjunction, a design that sits truly at the baselines'
  level on every limit passes them all only with low probability. 3.10 records the reversal but not the operator's
  condition, which is lost with it.
- **Failure allowed.** A design that a user would want (inside every limit in truth, better composite) fails on
  limit noise alone.
- **Fix.**
  - In 3.8 (a), say which margin applies, and apply it once.
  - Make each limit check one-sided with the burden on the evidence that the design **crosses**: "fails only if shown
    to cross at a declared level". Or keep it a point check with the margin set once from noise.
  - Require the pinning row to show that a design equal to the best baseline on every limit passes all of them with
    at least the power target (part of B-9's gate).
  - Carry E-015's condition into 3.8 (a) by name.

### B-11. The evaluated object is not the traded object: the playbook's side rule is unstated (MATERIAL)

- **Where:** terms table, l.53 (layer 1 "the entry direction"); 3.5 (the playbook, l.155-156); 3.2.
- **Evidence.** The design is judged with coin sides, and the playbook tells a person what to trade.
  - If the playbook gives the model's side, the user's journey differs from the evaluated one by the model's live
    edge. That edge is unmeasured, possibly negative, and the evaluation deliberately ignored it.
  - If the playbook gives a coin, it must say so.
  - Once cross-firm rotation enters (plan item 4), independent coins per account or per firm can open opposing
    positions at once, which is conduct tier 1.
- **Fix.** 3.5 declares the side rule as part of the design. Either:
  - a literal coin, one draw per moment across all the user's accounts and firms, which is exactly the evaluated
    object; or
  - the model's side, with a no-harm floor (model-side composite not below coin-side by a declared margin on search
    years, reported on held-out).

### B-12. The search selects on the simulator's optimism; the held-out test cannot correct it (MATERIAL)

- **Where:** 3.5 ("Many trades, fast": the search rewards supply and speed); measures (28) and (29) are reported only
  (l.90-91); 3.8 has no fill stress.
- **Evidence.** The held-out test uses the same fill model as the search. Among many designs, the ones whose journey
  depends most on optimistic modelling rank highest: touch-through limits, the stop-first rule on bars that touch
  both, many small trades. DIRECTIVE Part 1 also bans "tight-bracket scalping" as tier 1.
- **Failure allowed.** A finalist passes at the base fill model and is negative at +1 tick of worse fills, and the
  verdict does not show it.
- **Fix.** Add to 3.8 (c): the finalist still beats each baseline at the point estimate, and stays inside the limits,
  at +1 tick of worse fills (29) and at 10 % of signals missed (28). Alternatively, run the whole confirmation at +1
  tick with the base model beside.

---

## Minor

- **m-1. Latency (brief point 8).** The draft's latency text (3.5 l.147-149; section 4 l.212-214) is word for word
  CHARTER section 4 as E-203 wrote it. That is correct against E-203, but it omits two parts of E-202 (2)(c): "counted
  in the cells and the multiplicity" and "nothing chosen after a look". Under 3.3, L is a lever chosen on search years
  (F-1), which is a look. **Fix:** the E-NNN row rules that L is searched on search years, every L counted in the
  ledger, the finalist confirmed at its own L, and the five-minute cell reported beside every finalist and in the
  confirmation (with B-8). E-204's ruling that RL3 is latency-free stays valid.
- **m-2. Section 4 omits two in-force rules.** E-202 (2)(a) (no entry or fill inside a verified news window; flatten
  at the window's start) and (2)(d) (limits live at the latency, fill only on a one-tick trade-through, cancelled at a
  news window). A search declaration that cites "section 4" as its execution rules would miss both. **Fix:** add them
  now under E-NNN. A copy unchanged byte-for-byte is the brief's constraint, not a reason. F-9 already flags (a).
- **m-3. k numbering (brief point 7).** Two problems with E-204's rule:
  - 3.7's "the k assigned at the confirmation's row (E-204)" drops E-204's rerun clause: if another declaration pins
    between the run and its row, the run reruns at the new level under a repeat row.
  - It leaves "the confirmation's row" ambiguous: is it the row authorising the run or the row recording it?
    Separately, "confirmation" names both the held-out test and the purchased window (section 5 (A)).

  **Fix:** quote E-204's rule in full. Call the held-out test "the held-out test" and keep "confirmation" for the
  purchase window. Say that the purchase window spends no k. The k history (10 spent, 11 unspent, 12 spent, next 13)
  matches CLAUDE.md, E-007 and E-192.
- **m-4. E-007 (e) readings dropped without record (brief point 9).** Three things have no line in 3.8 or 3.10:
  - the placement-on reading;
  - the binding Focused Trader models;
  - E-007 (3)'s Focused Trader Program off in the verdict.

  The minimum detectable difference before the read is replaced by B-9's power gate, but that is not said. **Fix:**
  list each in 3.8 as beside the verdict, or in 3.10 as superseded.
- **m-5. 3.6 (ii) reads on unnamed years; regimes are fitted on the whole window.** If (ii) reads search years, it is
  selection-contaminated, although it only ever makes the line stricter. RD-04 (a2)'s regime and volatility
  descriptive is whole-window, so search-year regime labels depend on held-out volatility. **Fix:** (ii) on held-out
  years (B-9); regime thresholds from search years or from a rule fixed in advance.
- **m-6. CHARTER section 6's "the reverse beside".** "Walk-forward (choose early, judge late; the reverse beside)"
  would have a search read the held-out years. **Fix:** a sentence in 3.6 that the reverse reading is not run, or is
  run only after the held-out test as a described reading.
- **m-7. The measures list.** (35) and (36) are baselines, not measures. (12) and (13) are several measures each, so
  "39" is fuzzy (the plan also says 36, F-2). E-008 (1) restricted S3c to comparisons within one trade stream,
  because its link to P across designs is partly arithmetic (E-007). As measure (14), across designs, it could enter
  the composite. **Fix:** number measures and baselines separately. Either keep S3c's within-stream rule, or exclude
  it from the composite's dimensions.
- **m-8. Other firms have no baseline.** E-202 says P-14 run unchanged on another firm is no reading of that firm, but
  3.8 (b)'s baselines are Topstep's. **Fix:** a sentence that each firm's baseline set (at least the naive coin on its
  own protocol) is declared in its search.
- **m-9. DIRECTIVE consistency.**
  - D-9 leaves Part 3 stale, although D-0 argues for in-place edits because stale text misleads.
  - Part 5's worktree list ("family A", "the multi-feature model (family B)") and 6.3 C ("against Topstep's $50K") go
    unedited.
  - D-6 retires family B in DIRECTIVE text, while the E-NNN row retires nothing.

  **Fix:** edit Part 3 in place too, or say why not. Add Part 5's list to the mapping table. Put the retirement in a
  row (the Wave 1.6 triage row) and cite it.
- **m-10. Record hygiene.**
  - The draft row cites "confirming E-206's relay". If the confirmation is E-207, cite it. If it is not yet on record
    (it is not on disk today), the texts wait for it.
  - 3.3 (e)'s plateau rule ("neighbours must also do well") is a selection rule with no metric or radius. Declare it
    with B-2's pins.
  - "Trades per day" as a limit sits awkwardly with "many trades, fast". Say whether it is a floor or a ceiling.

---

## What I tried that found nothing

- **Section 4.** I extracted the draft's section 4 and the current CHARTER section 4 and diffed them: identical.
- **DIRECTIVE line numbers.** Every line the draft cites (3-4, 16, 17, 83-85, 92, 104, 109-113, 114-119, 130-132)
  matches the current file. Its grep count of five hits holds.
- **Latency wording.** The draft's wording is word for word CHARTER section 4 and E-203's text (the remaining gaps are
  m-1).
- **Superseded rules.** 3.10 and the row record every superseded rule I could find: E-008 (1), R\* = P-14, D-621 (3),
  E-015 (3) and E-023 (1)-(2). E-008 (2) and (3) are kept. E-014's measures are folded into the 39.
- **Literals.** I searched the draft for any five-or-more-digit literal and found none, so there is no seed literal.
  It cites D-621 (3) by sha256 rather than copying the seed.
- **k history.** It matches CLAUDE.md, E-007 and E-192. E-094 and E-095 exist with the cited dates.
- **Points I checked against the draft, with no defect beyond those above.**
  - The conduct hard rule (no opposing positions; one position at a time across a firm) is carried in 3.4.
  - Hand entry only (E-008 (3)) is kept in section 4.
  - The 0 % denial and placement-off verdict is kept.
  - The bankroll-stop line is removed from "not modelled", as the plan asks. That is consistent, since measure (24)
    now models it.

## What I could not check

- `docs/MEASURES.md`: absent from `wt/wt-user` and its worktree, so not reviewed.
- E-207: not on disk, so I could not check its text, its review-label ruling or whether it confirms the plan as is.
- The completeness of the draft's section 5 file list. I spot-checked it against CHARTER and DIRECTIVE but did not
  re-run its grep over `.claude/`, `tests/`, `scripts/` and `extended/`.
- Stage 2 D-626 and D-554 directly. I cite them through RD-04's and E-203's records.
- Whether H4 is meant to run on search years only. The plan does not say, and B-2 assumes the worst.
- **Experiments specified, not run:**
  - (1) B-4's whole-rule null calibration of the pinned composite, with non-degenerate nulls and history as the
    replication unit. Heavy; the size of H3.
  - (2) B-9 and B-10's pre-pin power of the conjunctive pass line at k = 13's level. Heavy; it can share H3's run.
  - (3) B-6's reflected-path zero-edge convention against the as-traded resting side on search-year bars only. Light
    to moderate; one trigger family's walk.
