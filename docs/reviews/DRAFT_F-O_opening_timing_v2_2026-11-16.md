# Red team, second read: `prereg/DRAFT_F-O_opening_timing.md` (family O, second version), 2026-11-16

**Target.** `prereg/DRAFT_F-O_opening_timing.md` and `tests/test_family_o_persistence.py` as committed at cd2cbe7 on
`wt/wt-lit` (Q-63). I read them in that worktree, which had a clean tree.

**Read against.**
- The first read, `docs/reviews/DRAFT_F-O_opening_timing_2026-11-16.md`. I checked each of its findings against the
  text and the code, not against the draft's own table in section 0.2.
- `CHARTER.md` sections 2-4 as amended.
- `DECISIONS.md` E-007, E-008, E-014, E-015, E-021, E-023, E-031, E-034, E-035, E-036, E-037, E-039, E-040, and E-042
  to E-045. The worktree's log stops at E-041, so I read E-042 to E-045 from master at 57d7ed8.
- The pass-line code: `extended/lift_bound.py` (`cons`, `diff_stats`, `placebo_selection_bound`, `two_sample_bound`)
  and `extended/p_bound.py`. Their blob ids are the same in the worktree and on master (984f3467 and f5b29710), and
  neither has changed since Q-16 (`lift_bound.py` last at 3a7a3f5, `p_bound.py` at 2f5ffd0).
- `extended/reader.py` (`declared_purposes`, `CHOICE_WORDS`, the identity and `registered_design` rules),
  `extended/user_beside.py`, `extended/gate.py` and `extended/walker.py` (the `Rules` presets).
- From the vendored engine:
  - `propedge/campaign/shared_days.py` (`ReplayTable`, `TradeRouter.begin_day`, lines 144-164 and 335-400);
  - `lockstep.py` (`FundedAccount.trade_day`, lines 670-790).
- `scripts/q16_calibrate.py` (the selection-null generator and Table 9's grid), and the calibration note's tables for
  their structure only. Their figures are exploratory until Q-55 (E-035 (4)), and none is cited here.

**What the brief held.** It named the draft's own interpretations to test and the places to attack. It stated no
expected answer. I treated each interpretation as a claim.

**What I ran.**
- Nothing I ran decoded a bar, a walk or an atlas file, opened a result value, read NQ from 2026-07-17 or ran the
  engine.
- `tests/test_family_o_persistence.py`: 16 passed.
- Four synthetic checks, A to D (Appendix), with seeds 75001-75003 fixed before each run, numpy and scipy only. They
  are exploratory and select nothing.
- **Disclosed.** My seed search (`grep -rI` over the worktree, the form section 16 itself uses) followed the worktree's
  junctions into the licensed bars and atlas. grep opened those files and skipped them as binary: nothing was decoded
  or printed (note n2-5). Separately, I read the column names and key columns (section, rule, R, latency) of three
  vendored S1/S3 result files, to check that B2's rule names resolve. I read no value column.

## Verdict: **pinnable once its named external conditions are met**

There is no MATERIAL defect. The first read's four material findings are fixed in the text and the code:
- **F1.** C1 and C1-close now run by `cons` through `placebo_selection_bound` on stratum-centred values, with B2 per
  member.
- **F2.** Every reading of the wait and the openings runs on the U1 replay in history's order.
- **F3.** C2 is differenced against the twin designs' openings, and fallbacks are labelled at every P-16 mark.
- **F4.** Each cell's persistence class is stated, with a drop rule and Q-55 as a prerequisite.

Its eight minors are fixed, one of them (m6) only in part (m2-3 below).

What remains is eleven MINOR findings and ten NOTEs. None moves a cell, the twin's estimand, the level, the reads line
or the seeds. Each minor is a short edit: a stated consequence, a named instance, or a rule made explicit. The lead can
rule them as one edit before the pin, checked by the prereg-gatekeeper on the diff, as E-045 (3) did for F-02's text
gaps. A third red-team read is not needed unless the edit goes beyond them.

The external conditions are those the draft names (header lines 17-21; section 20):
- Q-55's clean rerun on record, **reproducing the treated two-sample `cons` holding** (m2-8);
- 6.6's power column filled from Q-55's Table 9, with the drop rule applied (m2-9);
- the build's seam findings and Q-17's extension under a row (m2-10);
- the family number.

| id | severity | finding (one line) |
|---|---|---|
| m2-1 | MINOR | C2's difference does not fully cancel the routing selection, as 7.4 claims: the per-offer placebo does not cluster like the state, so the twin designs open at other routing positions and fall back far less often. The residual is small in a toy and absent from B2's C2 null |
| m2-2 | MINOR | Run 1 "reads no judged-block bar or walk", but A1 items 2-4 and 8 compare whole-window registered objects. T-3 needs the `identity` section unchanged with the judged block replaced. The reader admits a whole-window read only from an identity script |
| m2-3 | MINOR | B2's slow amplitude has no judged-block floor. E-044 (2) gave family B one, read after the judgement, which can only raise the critical value |
| m2-4 | MINOR | A10 tests `cons` alone and has no consequence. If it finds `cons` lax on c, the level rests on a B2 never checked on c. Its label also understates a failure |
| m2-5 | MINOR | The confirmation's C2 switch sends a design with at least 21 openings to a line that cannot pass on six months (df at most 1 at 63 sessions). Its fallback prices C1's bound on all openings, fallbacks included. B2's source for the confirmation is unnamed |
| m2-6 | MINOR | The scorecard names no P statistic. E-035 (3) adopts `pcons`, and F-02 names it; D-621 (3), the line E-007 (1) found lax, is the only one named |
| m2-7 | MINOR | C1-close's walk is not a named `Rules` instance. "The close of the bar ending 15:10" needs `walk_end = C_FLAT`, which also moves the stop and target checks, so "every other rule STAGE2's" is false |
| m2-8 | MINOR | The pin waits for Q-55 to be "on record", with no withdrawal clause if Q-55 fails to reproduce the treated two-sample `cons`, and the pass-line code is pinned by merge commit, not by blob id (F-02 v5's form) |
| m2-9 | MINOR | The drop rule reads Table 9 "at the family's k", but Table 9 has `cons` columns at k = 11 and 15 only, and family O will be k >= 12. "The lead confirms" leaves discretion after Q-55's figures |
| m2-10 | MINOR | Q-17's forfeiture responses already set `funded_account_cls`, so the declared extension collides with the scorecard's all-accounts forfeiture reading |
| m2-11 | MINOR | B2's session draw ignores the day kind: a judged normal day drawn from a report day loses every mark before 07:40, and the reverse fills a report day with a normal day's values |
| n2-1..n2-10 | NOTE | Answers to the drafter's four red-team questions; S2's pre-read "cannot bias the lift" wording; A1 item 8 is stale (Q-51 HOLDS, E-044 (3)); the seed check reads through the data junctions; the drop rule's "inside the grid" means 40 standard errors; K5's censoring; T-10's runtime; floor (iii)'s calendar; the stage-B pick inherits m2-1; the module's variance under stratum-varying shares |

---

## The first read's findings: what is fixed

| first read | status at cd2cbe7 | evidence | residual |
|---|---|---|---|
| F1 the statistic | **fixed** | C1 and C1-close by `placebo_selection_bound(y = c - mu_g, ...)` at `SHIPPED = "cons"` and `DIFF_DF_RULE = "treated"` (7.2, lines 633-646; 12, 929-932). The centring identity is tested (T-1's `test_centred_values_through_placebo_selection_bound_give_the_exact_lift`, which passes). z_s is dropped as a variance series. B2 is per member, each member at the larger of its t and B2's quantile, and `cons` needs all three (11 item 1, 869-875). What Q-16 calibrated is stated (11 item 5). A10 is added | m2-4 (A10 has no consequence) |
| F2 the wait's calendar | **fixed** | 4 item 5's table (303-317) puts A2, K5, the waits, u_c, V_B and V on the U1 replay. The replay exists as claimed: `extended/user_beside.replay` builds `SharedDayDraws(..., replay=True)` (line 204), which selects `ReplayTable` (`shared_days.py` 716), and `ReplayTable` plays "the log's days in their own order, once" (144-163). The gate is kept for A1 and floor (iii) only. T-1 has the ordered-against-independent test | n2-8 (floor (iii)'s calendar) |
| F3 V not differenced | **fixed in substance** | V_line = u_d x mean_dv(c) x D / 4, with D the design's openings against the twin designs' (two draws pooled), by `two_sample_bound` (7.4, 664-678). Fallbacks are valued at labels walked at every P-16 mark (5.2, 353-356). V(P-16) and V(design) go beside. In check A the differencing removes almost all of a routing deviation | m2-1 (a small residual, outside B2's null) |
| F4 persistence and power | **fixed, conditionally** | Classes with reasons (6.6, 588-593); the power column marked [Q-55]; a drop rule (595-598); Q-55 a prerequisite (17-21; 20 item 1); the bars-only run-length count named as the lead's call | m2-8, m2-9 |
| m1 the 17:30 start | fixed | one rule (6.3 notes, 508-510); the 15-bar minimum separate (6.2) | -- |
| m2 report-day entry | fixed | E-042 (4)'s ruling applied (3, line 266; 5.2; 5.4); A2 counts the 07:35:00 entries; the scorecard's note (13) | -- |
| m3 flatten convention | fixed | C1-close is a line of the intersection (12, 931-932), and stage B's eligibility needs its form positive on the span (10 item 3) | m2-7 (its walk unnamed) |
| m4 identities that bite | fixed | never-on and placebo-set identities (5.4, 402-404; A1 items 5-6); T-5 through the vendored router and loop. The off-by-one is checked in code: the router's `begin_day` runs before any account trades, and `FundedAccount.trade_day` increments `days` at its end (`lockstep.py` 772), so `days` is 0 at the first live session's routing, as 5.4 says. A dead gate is caught by item 5: the router calls `can_take` only when `able` and states are passed (`shared_days.py` 336, 373-380) | m2-10 |
| m5 news readings | fixed | E-034 cited; the not-modelled note lists the unstated rules; the ISM/GDP share stated as unknown | -- |
| m6 B2's amplitude | **partly** | (b) from S1/S3's vendored lifts and (c) three times the choice span's amplitude (883-894); the rule names resolve in the vendored files (keys only) | m2-3 (E-044 (2) later added a judged-block floor for family B) |
| m7 T-10 | fixed | levels 1 % and 5 %, 2,000 x 20,000, Clopper-Pearson failure rule, failure protocol (1169) | n2-6 (runtime) |
| m8 per-year share | fixed | 6.4 (540-543); A5 by year; W's rationale moved | -- |
| n1-n8 | answered | each is cited or carried as section 0.2 says | -- |

---

## Findings

### m2-1 (MINOR) -- C2's difference cancels the routing selection only to first order, and B2's C2 null cannot see the rest

**Where.**
- 7.4, lines 659-662: "The twin design's openings carry the same routing selection; the difference removes it."
- 7.1, lines 621-625: the twin designs, and "what it does not match: the state's clustering".
- 11 item 2, C2's null (895-899).
- 10 item 4 (the pick by V_B).

**Evidence.**
- The twin design's placebo fires offer by offer (7.1). The state fires in runs: for a daily state (s3, u3's daily
  terms), all marks of a session; for s1 and s2, a stretch of a night.
- So a waiting account under the design opens at the first reached offer of an in-state night. Under the twin, it opens
  at the first *flagged* offer after reach, a later routing position.
- Its fallback share also differs by an order of magnitude: in check A it is about one half for the design and at most
  six in a hundred for the twin.
- The routing deviation at a reached offer depends on the position: the draft's own 7.4 explains why (how fast the
  night's earlier trades exited).
- So the two designs' openings carry different routing selections, even for a state that carries nothing.
- B2's C2 null draws y\* from choice-span sessions with the uses held fixed. y\* is then independent of the uses, so D\*
  is centred at zero by construction and cannot contain the residual.
- **Check A** (Appendix) uses a daily state independent of everything, so C1's null holds exactly:
  - the undifferenced routing deviation of either design's openings is +0.016 to +0.052 R;
  - the differenced D's noise-free part is about -0.0002 R, roughly two to three of its standard errors;
  - the differencing removes almost all of the deviation, but not all of it.

**What it allows.** Suppose a real C1 lift too small to be worth $500 a year. A routing residual of the right sign then
adds to D, and C2 can pass on routing. With the wrong sign, a real design fails C2. In the toy the residual is two
orders below anything that matters; on real data it is unknown, and it is not in the level C2 is read at. Stage B's
pick by V_B inherits it (n2-9).

**Remedy (a stated assumption, and an optional rule).**
- Correct line 662 to "removes it to first order". Say beside C2, with the verdict, that the residual (the state's
  clustering against the placebo's, at the router) is not in B2's null: an assumption that carries the value.
- Optional, and better: draw the **twin designs** (C2, V_B and the scorecard's twin) from a **clustered placebo**, not
  the per-offer one:
  - take the state's own in-state indicator, circularly shifted by a seeded uniform offset within each (calendar year,
    day kind) sequence of sessions, all marks of a session together;
  - this keeps each stratum's count exactly and the state's runs, so the waits and routing positions match;
  - its expectation over the offset is the stratum mean, so C1's twin (the exact expectation) is unchanged;
  - the scorecard's design-against-twin pair (13) then stops mixing the selection with the wait, which the draft
    concedes it now does.
- Or follow E-044 (2)'s precedent for family B: C2 at the lesser of V_line at D's bound and the uniform-lift valuation
  at C1's bound on the design's in-wait openings (see m2-5 for the in-wait count).

### m2-2 (MINOR) -- run 1 cannot hold the seal and run A1's whole-window identities

**Where.**
- A1 items 2-4 and 8 (lines 763-769, 777-778).
- 19.2 run 1 (1205-1207): "It reads no judged-block bar or walk".
- T-3 (1162).
- `extended/reader.py`'s rules 2 and 2a (lines 30-43).

**Evidence.**
- A1 item 2 (`TRADES_SHA256`, P-16's trades over the whole window) needs the judged block's bars and walks. So do item
  3 (P-16's gate paths at 500 paths and seed 20261206; P-16's U1 start rows, every start, both arms), item 4 (the same
  comparisons at W = 0) and item 8.
- The reader admits such a read only as `identity`, from a script under `identity/*.py` with its own identity row, or
  as `registered_design`, which "a family can never use".
- T-3 asks for stages A and B's sections, `identity` among them, to be byte-identical with the judged block replaced by
  a synthetic walk. An identity against registered whole-window objects cannot be.

**What it allows.**
- Built as written, run 1 is refused by the reader. The seal holds and the run fails, which starts the failure
  protocol.
- Built around the refusal, the population frame of run 1 holds the judged block's labels (for item 2) while stage B
  runs. T-3 is then the only guard, and as written it cannot pass.

**Remedy.**
- Put A1 items 2-4 and 8 in an identity script (for example `identity/family_o_identity.py`) under its own identity
  row. Run it and hold it under the lock before run 1, as Q-22 and Q-51 were.
- Run 1 builds the population on the choice block only.
- T-3 compares run 1's sections other than `identity`.

### m2-3 (MINOR) -- B2's slow amplitude has no judged-block floor

**Where.** 11 item 2, a\*'s parts (a)-(c) (883-894); item 3 (900).

**Evidence.**
- E-044 (2), ruling on family B's M4-1, added to the amplitude "the twin's largest absolute yearly lift on the judged
  block, read after the judgement, which can only raise the critical value".
- Family O's (b) is Stage 2's whole-window sided lift, which the draft itself calls possibly an understatement. Its (c)
  is three times the choice span's own amplitude.
- The draft's section 2 records the persistence reading weaker on 2020-2023 than on 2024-2026. If the judged block's
  slow component of c is more than three times the choice span's, nothing in B2 sees it. Item 3 says so beside the
  verdict.

**What it allows.** At the family's level, a slow component larger than declared can align with a persistent selection
(s3, u3) and pass C1 with no selection effect. In check B, with a judged slow component three times the choice span's,
both `cons` alone and the larger-of rule held at 5 % and 1 %. This is therefore a margin at the family's level, not a
demonstrated failure.

**Remedy.**
- Add **(d)**: the largest absolute mean, over the judged block's disjoint 63-session blocks in session order, of the
  per-session mean of the population's y. It covers every population offer and no selection, and for C2 the labelled
  marks too.
- Read it after `stage_C_judgement` and take a\* as the largest of (a)-(d), the C1 and C1-close critical values
  recomputed with it.
- It reads no selection and can only raise a critical value, as in E-044 (2).

### m2-4 (MINOR) -- A10 decides nothing, so a failure it records leaves the level on an untested B2

**Where.** A10 (826-833); 11 item 5 (ii) (909-911).

**Evidence.**
- The deciding rule takes each member at the larger of its t and B2, so it rejects no more often than `cons` alone.
- A10 passing (at 1 % and 5 %) therefore covers the deciding rule at those levels. A10 failing has no consequence: "it
  kills nothing", and the level "then rests on B2's larger-of rule alone".
- B2 has never been checked on c. T-10 is synthetic.
- The label is also backwards in strength. An interval wholly above the nominal shows `cons` lax; it is recorded as
  "not shown to hold".

**What it allows.** The choice span shows `cons` lax on c in a cell's class, and the cell is still judged on a B2 whose
transfer from one span to another was never tested.

**Remedy (declared now).**
- If A10 records `cons` lax in a surviving cell's class at either level, run **the deciding rule itself** on the same
  A10 replications, as a pseudo-judged split: B2 built from 2021-2022's values, the selections and statistics on 2023.
- If the deciding rule is lax there too, that cell is closed, counted, before stage B reads any lift (or the family is
  declared a screen; one of the two, chosen now).
- Relabel the record as "`cons` lax on c in this class".
- Cost: the A10 replications times a B2 of about 20,000 inner draws on about 250 sessions, CPU hours, light in memory.

### m2-5 (MINOR) -- the confirmation's value line: a switch to an unpowered C2, an overstated fallback, and an unnamed B2 source

**Where.** 15, lines 1053-1060 and 1063-1066; 12's beside, the uniform-lift valuation (963).

**Evidence.**
1. On a window of six months (about 126 sessions), `cons`'s members have at most 6, 3 and 2 blocks (df at most 5, 2
   and 1). t63w's one-sided 5 % critical value is then 6.31, with CR1's factor of 2 (check D). If a design's openings
   fall in one 63-session block, its bound is blank and C2 fails.
   - So the switch sends exactly the designs with enough openings (at least 21) to a line they can barely pass.
   - The window's length rule (1063-1066) sizes the window for C1 only.
2. The fallback prices C1's bound at stage C's u_d, the design's openings a start-year **including fallbacks**. Those
   carry no selection, which overstates the value by 1 / (1 - the fallback share): up to twice under K5. 12's beside
   reading has the same form.
3. "B2 re-simulated at the window's length" names no value source: the choice span, the development window, or the
   window itself.

**What it allows.** A carried pick fails its confirmation's C2 for lack of blocks, or passes the fallback on a price
inflated by its own fallbacks.

**Remedy.**
- The confirmation's value line: always C1's bound x **the design's in-wait openings** a start-year x mean_dv(c) / 4,
  at least $500, with C2 on the window's replays beside. Size the window for this line as for C1.
- Name B2's source: the development window's values, both blocks, by then read.
- Use the in-wait count in 12's beside reading too.

### m2-6 (MINOR) -- the scorecard's P comparison has no named statistic

**Where.** 13, lines 1002-1005 and 1011.

**Evidence.**
- E-035 (3): "the scorecard's P comparison uses `extended/p_bound` -- `pcons` stands".
- F-02's draft names `pcons` (its lines 14-15 and 907-911).
- Family O's 13 reads P, the paired differences "as distributions" with draws `[20261987, 0]`, and Stage 2 D-621 (3)
  beside. D-621 (3)'s line (i) is the one E-007 (1) found does not hold its level.

**What it allows.** A P reading beside the verdict on a bound the program has rejected, or none.

**Remedy.**
- Name `extended/p_bound`'s `pcons` for the paired P differences against P-14, P-16 and the twin design: one-sided at
  0.05, beside, never a line. `bm63c` goes beside once its table is pinned.
- Label D-621 (3)'s line (i) as not holding its level.
- Say whether `[20261987, 0]` draws anything that `pcons` (which simulates with `p_bound`'s own seed) does not.

### m2-7 (MINOR) -- C1-close's walk is not a named instance

**Where.** 5.3, lines 362-364; 8 ("walk": `close` for C1-close); 12, 931-932.

**Evidence.**
- `extended/walker.py` has no preset with `STAGE2`'s rules and a close flatten.
- Under the walker's semantics, `flatten='close'` prices "the close of the last bar by `walk_end`" (lines 163-164). So
  "the close of the bar ending 15:10" requires `walk_end = C_FLAT`. That also lets stops and targets fill on the bars
  ending 15:09 and 15:10, which `STAGE2` (`FLAT_ENTRY`, 15:08) does not walk.
- "Every other rule STAGE2's" is therefore false for the walk's end. The alternative, `FLAT_ENTRY` with `close`,
  prices the close of the bar ending 15:08.

**What it allows.** Two builds of one line that differ in which trades resolve.

**Remedy.**
- Name the instance in the file, for example `Rules("stage2_close", C_FLAT, "close", True)`, or the 15:08 form, and
  say which.
- Add a test that it differs from `STAGE2` only at the flatten and the last two bars.

### m2-8 (MINOR) -- the pin's dependence on Q-55 has no failure branch, and the pass-line code is not pinned by blob

**Where.** Header, lines 17-21; 8, line 724 ("merged 4d3e503").

**Evidence.**
- E-044 (1): F-02's fifth draft "binds itself to be withdrawn before any read if Q-55's clean rerun does not reproduce
  `cons` and the treated two-sample `cons` holding". It also pins `extended/lift_bound.py` and `extended/p_bound.py`
  by git blob id.
- Family O waits for the rerun to be "on record" and names a merge commit only. Q-68 (a red-team read of the pass-line
  code) may change the module between the pin and run 2.

**Remedy.**
- The same clause: withdrawn, or redrafted, before any read if Q-55 does not reproduce the treated two-sample `cons`
  holding on the selection nulls.
- Pin the two modules' blob ids in the file (984f3467 and f5b29710 at this read), and have A1 refuse a run commit
  whose blobs differ.

### m2-9 (MINOR) -- the drop rule reads a column Table 9 does not have, and leaves a discretion

**Where.** 6.6, lines 595-598.

**Evidence.**
- Table 9's header carries `cons` at k = 11 and k = 15 only (the calibration note, line 612).
- F-02 holds k = 11 (E-045 (4)), and family B is ahead, so family O's k is 12 to 15.
- "The lead confirms under the pinning row" lets the outcome be steered after Q-55's figures are seen. Those figures
  come from the judged population's outcomes, though they say nothing of this family's states.

**Remedy.**
- Read the **k = 15** column, which is stricter than any k from 12 to 15, or have Q-55's script write the family's k.
- Make the rule mechanical: the lead records the drop, with no confirmation.

### m2-10 (MINOR) -- the declared extension of Q-17's adapter collides with its forfeiture responses

**Where.** 5.4, lines 399-400; 18.1 item 3 (1144-1146); 13, line 1009 ("all-accounts forfeiture").

**Evidence.**
- `extended/user_beside.response_args` sets `path["funded_account_cls"] = forfeit_class()` for every `forfeit_*`
  response (lines 189-190). The family's waiting class needs the same slot.

**Remedy.**
- Declare the composition: a class inheriting from the waiting class and the engine's `ForfeitFundedAccount`, built
  by the adapter. Hold it to Q-17's forfeiture rows with the wait switched off.
- Or drop the forfeiture reading for this family, with the reason.

### m2-11 (MINOR) -- B2's session draws ignore the day kind

**Where.** 11 item 2, lines 879-881.

**Evidence.**
- The stationary bootstrap draws choice-span sessions without regard to kind, and "each judged session's offers take
  the drawn session's values at the same marks (a missing mark dropped)".
- A judged normal day drawn from a report day loses every mark before 07:40: it holds no report-day mark before then,
  not even a label.
- A judged report day takes a normal day's 07:40-08:25 values, without the release.

**What it allows.** B2's replicates have a different in-state composition from the real selection (fewer offers on
some judged normal days), and report-day strata re-centred on normal-day values. The quantiles shift in an unknown
direction.

**Remedy.** Draw within kind: two stationary bootstraps of mean block 63, one over normal days and one over report
days, each judged session filled from its own kind's sequence.

---

## Notes (readings; no rule changes)

- **n2-1. The drafter's four questions (20).**
  - **(i) B2 and A10 for an uncalibrated dependence class.** In checks B and C the deciding rule and `cons` alone held
    at or below nominal at 5 % and 1 %. The cases were persistent daily selections, a judged slow component up to three
    times the choice span's, and states tied to volatility (the outcome's dispersion, not its mean). The family's level
    is not checked (see "could not check"). m2-3 and m2-4 are the margins.
  - **(ii) Two pooled twin draws, and reuse across starts.**
    - The draws are enough for validity. Inference is conditional on the draws, and a draw independent of y adds no
      bias.
    - Reuse is carried by the session-block clustering. A reused offer's uses sit in one session, so their correlation
      is inside one block's residual sum. The treated df counts blocks, not uses. The two samples' covariance (the
      same offer opened by the design and the twin in different starts) is inside the per-block difference of
      residuals in `diff_stats`.
  - **(iii) The classes.** They are plausible as argued. The bars-only run-length count is minutes and removes the
    argument, and I recommend it (the lead's call, 20 item 2).
  - **(iv) a\*.** See m2-3.
- **n2-2. S2's pre-read** (4 item 4's table, line 298: "cannot bias: the pick, the lift").
  - The states were proposed knowing that S2's high-volatility and trend cells read close to, or just below, P-16 over
    both blocks.
  - That can bias *which hypotheses are tested* toward ones whose relatives looked good on the judged block, and so the
    chance of a pass. It cannot bias the computation of the lift.
  - Reword. The honesty sentence (17 item 4) already carries the consequence.
- **n2-3. A1 item 8 is stale** (line 777, "owed under the lock"). E-044 (3) records Q-51 HOLDS: P-14's and P-16's
  registered gate runs at 500 paths, with no class and with the pass-through class. Cite it.
- **n2-4. A10's label** (line 831). See m2-4.
- **n2-5. The seed check reads through the data junctions** (16, line 1089).
  - In a worktree, `grep -rI ... .` traverses `vendor/stage2/data/bars` and `atlas` through their junctions. grep
    opens the licensed files, judged block included, and skips them as binary.
  - That is an open outside the one door, harmless in content. Add `--exclude-dir=data` or search `vendor/stage2`
    without its `data`.
  - My own search did the same, as disclosed above.
- **n2-6. T-10's runtime** (line 1169, "minutes"). My session-level version (check B) ran 300 x 2,000 in about a minute
  per setting. The declared 2,000 x 20,000 is about seventy times that, an hour or more per setting. Label it slow, not
  minutes.
- **n2-7. The drop rule's "inside Table 9's grid".** This means a detectable shift of at most 40 median standard errors
  (`scripts/q16_calibrate.py` line 671; the calibration note, line 773), a weak condition.
  - Power against the bar is A9's job.
  - A pick by V_B alone can choose a cell that A9 rates far above 3 x lambda_bar while another eligible cell is
    judgeable.
  - An eligibility condition "A9's MDL at most 3 x lambda_bar, unless every cell is a screen" would waste no family on
    a cell that cannot be judged. It has no level effect.
- **n2-8. Floor (iii)'s calendar** (4 item 5, line 316; 12, 951-952).
  - The long-run gate runs on `SharedDayTable`, the calendar 4 item 5 says destroys the wait. It is the gate as defined
    (E-022 (2)).
  - Say beside floor (iii) that the gate's design waits less than the traded one.
  - K5 also counts only accounts that opened. Accounts still waiting when a truncated choice-block start's history ends
    are censored, and they are the long waits. Report the censored count beside K5.
- **n2-9. The stage-B pick** inherits m2-1's residual through V_B. Stage B decides no level. The value map's exposure
  over both blocks cannot move the pick, since mean_dv(c) is a common positive factor across cells.
- **n2-10. The module's variance under stratum-varying shares.** On centred y the estimate is exactly L_c (T-1).
  - The module's residual weights every offer of sample 2 by 1 / N. L_c's exact linear form weights offer i by
    p_g(i) / N_F, where p_g is the stratum's firing share.
  - A heuristic decomposition shows the module's variance adds the between-strata spread of the share, which is
    conservative in expectation. That agrees with the first read's check 1. No change.

## What I tried that found nothing

- **Look-ahead, again, in every state quantity.** LR, LRS (with its 15-bar rule), DIS, har, H, HS, U, T, the 250-session
  mid-rank third, and u3's IV, M, x1-x3, bands, folds, final fit and y_hat share all read only bars stamped at or before
  m - 6 of day d, or whole earlier walked sessions.
  - The 17:30 start reads bars stamped 17:00-17:24.
  - A3's cuts now include 18:00 and 18:05, where rv_60's window is bounded at 17:00.
  - The y_hat reference uses the fit day d uses: a linear function of earlier regressors, so in-sample fitted values
    there carry no label.
- **Calendars and rolls.** Report days, FOMC days and early closes are published or pinned ahead. The day's contract is
  chosen by the previous day's volume. Every state is a within-day log ratio, and IV enters only as a ratio.
- **Leakage across blocks.**
  - Stages A and B read 2021-2023, with 2020 as warm-up. The choice-block replays end at 2023-12-29.
  - u3's final fit is hashed and pinned between the runs (19.2), and the judge cannot fit (T-9).
  - B2's (a) reads the choice span and the population, not a selection. (b) is a disclosed whole-window pre-read that
    can only raise a critical value.
  - The bound arm's shift is a registered constant.
- **The reads line.**
  - `declared_purposes` returns exactly the four purposes.
  - `DECLARED_LINE` matches only line 1182. Section 0.1's table row starts with "|" and 19.1's prose does not start
    with the phrase.
  - No purpose carries a `CHOICE_WORDS` token.
  - Each purpose is read once, in run 2.
- **Seeds.** `git grep` of 2026198x over every local and remote branch found it only in this draft, its test and the
  first read. The firms reading's block, above this one, is not written out here (its own test refuses its seeds in any other file).
- **Multiplicity.**
  - Four cells, each counted whether dropped, killed, closed or read, u3 included despite its stated negative sign.
  - One cell judged.
  - C1, C1-close, C2, C3 and the floors form an intersection at one level.
  - Stage B and its eligibility rules (K2's 4 % margin, both halves and C1-close's form positive on the span) spend
    nothing and read only the choice block.
  - No value searched; u3's 11 coefficients fitted in-fold (E-031 (1)).
  - The closure binds (14).
- **The pass-line code.**
  - `placebo_selection_bound` is the nested two-sample form on (selected, every offer). With y centred, sample 2's mean
    is zero and the estimate is L_c.
  - `two_sample_bound` on the two designs' uses is the same `diff_stats`. E-035 (2) adopts the statistic. That
    routed, reused openings lie outside Q-16's nulls is disclosed in 11 item 5.
  - Q-16's block selections are drawn with a random phase (`_sel_batch`), so runs straddle the statistic's blocks as a
    real state's would.
- **The seam.**
  - Q-17's adapter refuses `funded_account_cls` (`base_problems`, lines 157-171), as 5.4 says.
  - A declined offer passes to the next account (`passed_over`).
  - The never-on identity catches a gate that never bites.
- **B2's (b) names.** `mom15` and `lbrk5` at R 3.0 in `s1_sided_coin.csv`'s `lift` section; `lnbar1x4` in
  `s3_event_kinds.csv`'s and, at latency 5.0, in `s3_latency.csv`'s. Keys only.
- **T-1.** All 16 pass, the F1 and F2 tests among them.
- **Checks A to D.** See the Appendix.

## What I could not check

- **The deciding rule at the family's level** (0.05/132 to 0.05/240).
  - Checks B and C are at 5 % and 1 %, at the session level (daily selections), and not at within-night "window"
    selections.
  - A size at 3.8e-4 needs tens of thousands of outer replications, each with a B2 of at least 1,000,000 inner draws
    (the calibration note's section 3 arithmetic).
  - Specified: T-10's form on the choice span's real c (bars and walks of 2021-2023 only), at k = 15's level, in Q-55's
    harness. CPU tens of hours, light in memory, heavy by the lock's rule.
- **Every real magnitude:** the routing residual (m2-1), the judged slow component (m2-3), the run lengths (6.6), K5's
  censoring and the fallback share. Each is a stage-A or stage-B reading once declared.
- **Table 9's figures.** I read the table's structure only. Its figures are exploratory until Q-55, and none is cited.
- **Whether the seam composes** in the engine (the build's finding, 20 item 4).
- **u3**, restated from family R's unreviewed draft. Its bands, M and x3 are reviewed only as restated.
- **An inactivity rule for a waiting XFA.** None is on the verified ledger as read, and I did not search the web.

---

## Appendix: the synthetic checks (exploratory; seeds fixed before each run; nothing read)

**A. C2's null centre (seed `[75001, rep]`).**
- **Setup:**
  - nights in history's order, with night volatility v lognormal (spreads 0.4 and 0.7);
  - 186 marks, the walk's end at mark 267;
  - another account's trade holds the one slot from mark 0 for Exp(kappa / v^2) marks (kappa 150, 250 or 400), and
    the waiting account is eligible two marks after;
  - c = -0.25 x exp(-(267 - m) v^2 / kappa) + unit noise (the cost of an unresolved trade, the first read's toy), and
    y = c less its mark's mean;
  - the state is a daily chain (share 1/3, mean run 5 nights) **independent of everything**. The twin draws the
    state's count per mark without replacement;
  - W = 5, then fall back to the first reachable offer.
- **150 replications:**
  - D's noise-free part was -0.00019 (s.e. 0.00006), -0.00022 (0.00009) and -0.00018 (0.00010) R;
  - the undifferenced routing deviation was +0.016 to +0.052 R for both designs alike (60 replications);
  - the fallback shares were about one half for the design and 0.003 to 0.06 for the twin;
  - B2's form (values from another night at the same mark, the uses fixed) was centred at zero within its noise.

**B. The deciding rule under a slow component (seed `[75002, setting, rep]`, 300 replications, 2,000 B2 draws each).**
- **Setup:**
  - session means A x rho + an AR(1) (phi 0.5, sd 0.25), with rho a sign switching 1/63;
  - a choice span of 750 sessions and a judged span of 630, centred within years;
  - a daily selection with share 1/3 and mean run 21 or 63, independent of y;
  - B2 as 11 item 2 declares it (stationary bootstrap of the choice span, mean block 63, plus 3 x its largest
    |63-block mean| as a Markov sign).
- **Rejection rates at 5 %** (`cons` alone, then the larger-of rule):

  | setting | `cons` alone | larger-of rule |
  |---|---|---|
  | A matched 0.05, run 21 | 0.043 | 0.023 |
  | A matched 0.05, run 63 | 0.017 | 0.013 |
  | A matched 0.15, run 63 | 0.020 | 0.010 |
  | A 0.05 on choice, 0.15 judged | 0.023 | 0.007 |
  | A 0 on choice, 0.15 judged | 0.040 | 0.030 |

- **At 1 %:** at most 0.003 everywhere.

**C. A state tied to volatility (seed `[75003, setting, rep]`, 300 replications).**
- **Setup:** session means sigma x z, with log sigma an AR(1) (phi 0.98, sd 0.5) and z an AR(1) (phi 0.3). The state
  is the top or bottom third of log sigma: the outcome's dispersion depends on it, its mean does not. B2 as in B.
- **Results:**
  - top third: 0.013 (`cons`) and 0.010 (larger-of) at 5 %, both 0.003 at 1 %;
  - bottom third: 0.033 and 0.003 at 5 %, both 0.000 at 1 %.

**D. `cons` on a short window (arithmetic, `extended.lift_bound.block_index`).**
- **126 sessions:** 6, 3 and 2 blocks; df at most 5, 2 and 1; one-sided 5 % t at 2.02, 2.92 and 6.31.
- **252 sessions:** 12, 6 and 4 blocks; 1.80, 2.02 and 2.35.

The scripts are kept in the reviewer's scratchpad, not committed: `c2_null_toy.py`, `b2_level_toy.py`,
`vol_state_toy.py`.
