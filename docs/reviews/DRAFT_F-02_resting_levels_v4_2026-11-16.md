# Red team: `prereg/DRAFT_F-02_resting_levels.md`, fourth version with Q-16's statistics (family RL2), 2026-11-16

The red team (`.claude/agents/red-team.md`), read-only, in worktree `wt-levels` (branch `wt/wt-levels`) at master
b3b1671 (TASK_QUEUE Q-53, the final read before the pin).

**The target.** The draft as it stands at b3b1671: 1,242 lines, not pinned, not numbered. It is version 4 with Q-57's
`[Q-16]` marks filled: C1 and C2 by `cons`, and C1' by `two_sample_bound` with count-centred residual block sums and the
treated-cluster df.

**What I read it against:**
- `CHARTER.md` as amended (E-008, E-014, E-015, E-023, E-032 (3)); `DECISIONS.md` E-001..E-038; `CLAUDE.md`;
- `extended/lift_bound.py`, `extended/p_bound.py`, `extended/reader.py`, `extended/walker.py`, `tests/test_lift_bound.py`
  and `tests/test_walker_t13.py`;
- `docs/research/calibration_2026-11-15.md` (all of it);
- `.claude/skills/feature-rules/SKILL.md`, `.claude/skills/prereg-discipline/SKILL.md`;
- the three earlier reviews (`docs/reviews/DRAFT_F-02_resting_levels_2026-11-15.md`, the v3 read of 2026-11-16, and its
  appendix scripts);
- `identity/stage2_identity.py` (which files P-14's engine opens); `config/rules_extended.yaml` (13613539, 8284211);
  `TASK_QUEUE.md` (Q-53, Q-55).

**What I ran.** Four small synthetic scripts, one process at a time, one BLAS thread, in the session scratchpad. The
scratchpad is not durable, so their code is in Appendix A:
- `pdc_mag.py` and two one-line variants: the walker as committed, on synthetic tick-walk days, with an overnight-move
  drift whose strength depends on the move's size;
- `cons_short.py`: `cons` at one-sided 0.05 on 126- to 252-session calendars (the confirmation's form);
- `cons_sparse.py`: `cons` at the family levels on 60 to 150 fills over 657 sessions.

I also parsed the draft's reads line with `extended.reader.declared_purposes` and ran a word-bounded seed search.
**Not done:** no read of `data/bars` or `data/atlas`, no engine run, no web, nothing written but this note.

**On the brief.** It lists places to look, which I took as scope. Its framing ("whether the draft is now pinnable")
leans towards a yes, and I set that lean aside. I quote no Q-16 figure as evidence, since E-035 (4) makes them
exploratory until Q-55 reruns them; the figures marked *synthetic* are mine.

**Labels.** Severity is CHANGES-A-CONCLUSION (CAC), MATERIAL (MAT), MINOR or NOTE. A figure marked *synthetic* is
red-team arithmetic on simulated data, and decides nothing.

---

## Verdict

**Must be redrafted -- narrowly.** Q-16's statistics are applied as the module and the calibration note define them,
and the reads line is what the reader needs. Every earlier finding is closed but one: the third read's P1 is closed for
the overnight move's sign but not for its size.

**G1 (MATERIAL): C1' still does not identify the prior close.**
- At `pdc` the real ticket's distance from `P_ref` *is* the overnight move's size |g|. The placebo's distance comes
  from another day, so it is independent of |g|.
- Fill probability falls with distance, so the real fills sit on days with smaller overnight moves than the placebo's
  fills do (*synthetic*: 0.56 to 0.63 of E|g| against 0.80 to 1.01).
- So any effect of the overnight move whose strength depends on its size enters D, with no level effect at all.
- *Synthetic*: under "small moves revert, large moves continue" (no level effect; the mean drift over days is zero),
  `break` at `pdc` gives L = +5.8 and D = +3.5 (se 0.84). Both are positive, so C1 and C1' both pass once the pick has
  enough fills.
- T-14 (e) plants a drift that depends on the sign only, and under it D is about zero (+0.7, se 1.6). Its kill cannot
  fire.
- The v3 read proposed the side-matched placebo with a sign-only plant as P1's remedy. That remedy was incomplete, and
  this finding is about it.

**MINOR (each changes declared text):**
- M1: T-14 (b)'s and T-13 (a)'s pass lines fix no granularity and no multiplicity, yet each failure stops the build.
- M2: T-3 replaces bars, but P-14's engine reads Stage 2's walks, so T-3 cannot see the reachable count's seal.
- M3: Nothing says what follows if Q-55's clean rerun does not reproduce `cons` holding. The pin may come first.
- M4: The planning lookup is undefined for k of 12 to 14 and below 200 estimated fills, yet a close cites "the MDL".
- M5: The news row is stale (13613539 is now recorded, E-034) and leaves 8284211's releases inside the resting window
  unaddressed.
- M6: The confirmation's length rule is not fully fixed, and it is computed after the judged read.

**Corrections that hold:** P1's sign part; V1; T1; T2; V2; S1; N1-N11 and N13; E-026; E-031 (2) and E-032 (1)-(2);
E-029; and the E-035 marks: the call signatures, the estimate, the count-centred variance, the treated-cluster df, the
uncalibrated stage B stated as such, and the null class stated.

**What the redraft needs.** Either:
- **(a)** drop `break` at `pdc`, the safe default and the way F1 handled `on` and `pd`. The family becomes 15 cells and
  45 signed hypotheses over the same 36 questions. `fade` at `pdc` stays, with no level claim. Or:
- **(b)** add size-dependent arms to T-14 (e) under its existing kill.

Under (b), the synthetic figures suggest the arms would kill `break` at `pdc` anyway. Either way the fix is small, and
none of this is a reason to abandon the family.

## 1. Findings

| id | sev | finding (short) | remedy |
|---|---|---|---|
| G1 | **MAT** | At `pdc` the placebo matches the side but not the overnight move's size, which is the real level's distance. A size-dependent overnight effect gives D > 0 and L > 0 with no level effect. T-14 (e) (sign only) cannot see it. 9.2's "what D still cannot separate" is incomplete; 2 item 3, 9.7 and 13 inherit it | drop `break` at `pdc` (15 cells, 45 hypotheses), with no fade level claim there; or add fixed size-dependent arms to T-14 (e) under its kill, and correct 9.2, 9.7, 13 and 2 |
| M1 | MINOR | T-14 (b): "D covers zero, the two-sided 95 % interval", at no stated granularity; a failure stops the build. T-13 (a) extended: no Z, no fixed share or walk per stop, no seed in section 15. T-14 (a): "covers it" has no defined target. A correct build fails some 95 % interval with high probability | fix each test's cells, a family-wise Z (Bonferroni, as today's T-13 does), T-13 (a)'s walk per stop and its seed, and (a)'s criterion |
| M2 | MINOR | T-3 replaces every bar from 2024-01-02. The reachable count reads P-14's `data/atlas/A3/walks.parquet` and A1's files, which T-3 does not touch, so "(the reachable count included)" tests nothing about its seal | replace or poison the judged rows of every file the reachable count's engine call opens; record before stage A whether E-032 (2)'s fallback applies |
| M3 | MINOR | `cons` and the treated two-sample form are pinned on figures E-035 (4) calls exploratory until Q-55. Section 19 lets the pin precede Q-55 ("before any stage runs"). No consequence is declared if the rerun differs | declare: if Q-55 shows either above its level on a real or realistic null at the family's k, the family is withdrawn before any read and re-declared; or pin after Q-55 |
| M4 | MINOR | Planning reads Tables 4a/4b and 11 "at the family's k" and "at the largest tabulated N at or below" the estimated judged fills. The tables hold k = 11 and 15 and N from 200. A K1-passing cell can estimate about 65 judged fills, and k may be 12-14. A close is worded "no lift above the MDL" | the k = 15 column when k is not tabulated; below 200, "above the 200-trade entry"; state that the tables' nulls are 150-tick, win1/net3 pairs |
| M5 | MINOR | Section 3 says no 13613539 entry exists. E-034 recorded it (`config/rules_extended.yaml` 2073-2077), with 8284211's list of seven releases, among them EIA crude and natural-gas inventories inside the resting window. A 50-tick Combine ticket is sized at the 50-micro allowance (full size on a $50K) and can fill in that minute | correct the sentence; state E-034's reading for the tickets and list it in 12 item 8's "not modelled" note, or declare a cancel window for allowance-capped tickets (the lead's choice, before the pin) |
| M6 | MINOR | 14's power simulation "places" the judged pair terms "on a calendar of the candidate length" without saying how, and assumes "the lower of the two blocks' rates" while using the judged terms. It runs after stage C, so the open piece is chosen after a look (it moves the length and the purchase, not the level) | fix the construction (e.g. session sums resampled with replacement, thinned to the lower rate, on 21 m sessions) and report its zero-lift rejection rate beside |
| N1 | NOTE | `lift_bound.py` is named by commit, not pinned by hash; the tests pin `SHIPPED == "cons"` only | record its blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2` in the pinning row; the run asserts it |
| N2 | NOTE | 9.1's "df = blocks - 1" is "non-empty blocks - 1" in the module. "The judged block's calendar" is not named, and block edges move with the session count | name the day list (every trading day 2024-01-02..2026-07-16, void or not), and its count |
| N3 | NOTE | C2's λ is the all-fills mean, but 10 counts a two-fill day once and stage D's one-cancels-other takes only the first fill | report λ on first fills beside C2 (or use it) |
| N4 | NOTE | Stage B's bootstrap is labelled "studentised" (6.1), but 8.2 divides every replicate by the sample's se | relabel it "normalised by the sample se"; it is uncalibrated either way |
| N5 | NOTE | T-14 (c)/(e) kill at a two-sided 95 % interval over 18 (arm, kind, stop) checks: under a correct placebo, about a one-in-three chance some break (kind, stop) dies | conservative; state the rate, or use Bonferroni |
| N6 | NOTE | Section 15's T-12 record is stale: 20261930 now appears in the F-O and F-R drafts (references), and as the exclusive bound of `extended/user_beside.py` line 61 `range(20261920, 20261930)`, which is code but not a use | T-12 must not count it; update the record |
| N7 | NOTE | Stage D shifts the tickets by Student-t on 21-session block means (`t21e`), which Q-16 found lax at the family levels; a lax shift makes the floor easier to pass | it is U1's form, consistent with R\*; say so |
| N8 | NOTE | Stage D walks the tickets at every R of the menu: judged reads through `read_bars` under `stage_D_gate_floor`, whose row describes only the engine's reads | widen the row's text; the reader checks the name only |
| N9 | NOTE | The pinned file must be `prereg/F-NN_*.md` (the reader's `DECLARATION_PATH`), and the status lines will change at the pin | the pinning row names the diff from this reviewed text |
| R1 | reading | 9.1 reasons the null class from how sides are set (daily), but the dependence that sizes the test is that of the pair terms. A momentum or reversal regime gives w a mean that persists as long as the regime. Q-16's real nulls are P-16's long-minus-short pairs (drift) flipped by blocks, which do not model that | state the residual; beside the verdict, report the pick's choice-block lift by quarter and the lag-1 correlation of its 21- and 63-session block lifts (stage B's own read, no new spend) |

## 2. The findings in detail

### G1 (MATERIAL) -- the prior close's placebo matches the overnight move's sign, not its size

**Where.** `prereg/DRAFT_F-02_resting_levels.md`:
- lines 663-668 (9.2, "What it identifies"): "At `pdc` it matches them on the level's side, which carries the sign of
  the target day's overnight move ... What D still cannot separate is any effect specific to crossing a price the
  market traded at earlier. That is what T-14 (c) (look-back) and T-14 (e) (overnight sign) bound, with a kill";
- lines 367-374 (5.8): the side is E's own; the distance is the counterpart's distance on D, scaled by `A_E / A_D`;
- lines 1117-1119 (T-14 (e)): "every step goes up with probability 0.5 (1 + κ sign(g))", κ = ±0.002;
- inherited: line 184-185 (2 item 3, "the match at `pdc` including the overnight move's sign"); lines 705-706 (9.7, "the
  side-matched placebo removes S3's overnight-move effect from that claim"); lines 929-930 (13, "beyond what a crossing
  matched on its side and its distance carries").

**Evidence.**

*The arithmetic.*
- The real `pdc` ticket is at the prior close, so its distance from `P_ref` is |g_E|, with g_E = `P_ref` less the prior
  close: the overnight move's size, by definition.
- The placebo's distance is |g_D| x `A_E` / `A_D`, from an independent source day.
- So the two distances share their marginal distribution (that is what the scaling buys), but only the real one is tied
  to E's own overnight move.
- A ticket's fill probability falls with its distance. So:
  - the real fills select days on which E's own |g| is small;
  - the placebo's fills do not.

*Synthetic* (`pdc_mag.py`: the walker as committed, symmetric booking, the pair rule, S = 100 ticks, R = 1, cutoff
14:00; g ~ N(0, 200 ticks); a drift for the whole regular session; no level effect). The table gives the mean of
|g_E| / E|g| on the fills (real, then placebo), L, and D with its day-clustered, count-centred se:

| drift (per step) | days | \|g\| on fills: real / placebo | `break` L | `break` D (se) |
|---|---|---|---|---|
| +0.002 sign(g) (T-14 (e)'s follow arm) | 3,000 | 0.63 / 1.01 | -8.13 | +0.68 (1.58) |
| -0.002 sign(g) (T-14 (e)'s reversal arm) | 3,000 | 0.88 / 1.01 | +11.30 | +0.59 (1.23) |
| +0.002 sign(g) \|g\| / E\|g\| | 8,000 | 0.56 / 0.85 | -5.14 | **+2.98 (0.93)** |
| +0.002 sign(g) g² / SD² | 8,000 | 0.56 / 0.80 | -1.78 | **+3.75 (0.92)** |
| +0.003 sign(g) (\|g\| / E\|g\| - 1): small moves revert, large continue | 8,000 | 0.62 / 0.83 | **+5.84** | **+3.47 (0.84)** |
| +0.003 sign(g) (\|g\| / E\|g\| - 0.5) | 8,000 | 0.55 / 0.79 | -0.78 | **+2.92 (0.92)** |

`fade` is the exact negative in every row (symmetric booking; 5.6's near-exact negatives).

*Reading the table.*
- Under T-14 (e)'s own plants D is about zero, as the v3 read found. The size mismatch on the fills is there, but a
  drift that ignores |g| cannot use it.
- Once the drift's strength depends on |g|, D moves by 3 points or so.
- In the follow-only rows, L for `break` is negative, so C1 fails, and the intersection with C1' protects the family.
- In the mixed row -- small overnight moves revert, large ones continue -- both L and D are positive.
- By the walk's symmetry (not run), the opposite mix (small moves continue, large ones revert) gives `fade` at `pdc` a
  positive L and D, so a false level claim.

**The failure it allows.**
- Take a judged block on which nothing clusters at the prior close, but overnight moves behave as traders' lore says --
  small gaps fill, large gaps run. That is the variable S3's gap rules read on this window (section 2's S3 row).
- Then the `break` pick at `pdc` passes C1 on its trades, and C1' too. Under 9.2 and 13 it is recorded as a direction at
  the prior close beyond a matched crossing, and carried.
- 9.2's own rule says a break pick with no level effect is "a lead for unread data -- ... S3's overnight-move effect seen
  again -- not a finding". The size mismatch turns that lead into a carried level finding.
- The opposite mix gives `fade` at `pdc` a level claim (9.7) that is not one.

**Where it does not apply.**
- At `rn100` the real distances come from `P_ref` modulo 100 points, which no feature of the overnight path determines.
  The placebo's distances come from the same arithmetic on another day. They are exchangeable, so this finding does not
  touch `rn100`.
- At `pd` and `on` (fade level claims only, a reading there already, 5.8 last item) the real distance is also a
  function of the overnight path. The same confound applies to those readings beside, and 9.7 should say so.

**Remedy.** The lead's choice, before the pin.
- **(a) Drop `break` at `pdc`.** This is the safe default, and the way F1 handled `on` and `pd`.
  - Cells: (4 `fade` + 1 `break`) x 3 stops = 15.
  - Hypotheses: 36 `fade`-signed + 9 `break`-signed = 45, over the same 36 (kind, stop, R) questions.
  - `fade` at `pdc` stays, judged on its trades, with no level claim at `pdc` (9.7).
  - 2 item 3, 6.2, 9.2, 13 and 16 are updated.
- **(b) Keep `break` at `pdc` and widen T-14 (e).**
  - Add arms whose drift is fixed in the file -- for example κ sign(g)(|g| / `A` - c) for c in {0.5, 1}, both signs of
    κ, and κ sign(g)|g| / E|g| -- under (e)'s existing precision, visibility, kill and withdrawal rules.
  - Correct 9.2's sentence: D cannot separate an effect of the overnight move's size beyond the planted forms, and that
    residual is stated.
  - On the figures above, (b) would probably kill `break` at `pdc` at the build. The mixed row's D of +3.5 has a 95 %
    half-width of about 0.74 at (e)'s 40,000 days. So (b) costs build time to reach roughly (a).
- What no remedy can do: place a non-level ticket at the real level's own distance. At `pdc` that distance is the
  overnight move, so matching it collapses the placebo onto the level.

### M1 (MINOR) -- build tests whose failure stops the build, with no fixed granularity or multiplicity

**Where.**
- Lines 1121-1122 and 1135: T-14 (a) "L and D recover the plant with its sign, and stage C's bound covers it at its
  level"; (b) "D covers zero, the two-sided 95 % interval clustered by day"; "Failures of (a), (b) or (d) stop the
  build".
- Lines 1079-1082: T-13 (a) "today's form, extended ... a declared share of bars (at least the audit's Appendix B middle
  row)".
- Line 994: section 15's seed list for the walker tests holds no stream for T-13 (a).

**Evidence.**
- (b) names no cells. Read per (kind, side rule, stop, R), as stage A reads them, there are dozens of 95 % intervals.
  So a correct placebo fails at least one of them with high probability.
- Today's T-13 sets a Bonferroni Z = 2.64 over its 2 x 3 cells (`tests/test_walker_t13.py` lines 19-21 and 52).
  Extended to three stops, (a) has 18 cells and no stated Z.
- "At least" the middle row leaves T-13 (a)'s walk to the builder. Today's `SEED` 20261118 is "T-13's own, used nowhere
  else", and the draft does not say whether the extension reuses it.
- In (a), "covers it" has no defined target: the plant's true lift in win probability has no closed form.

**The failure it allows.** A correct build stops on a 95 % interval drawn by chance. The failure protocol then needs a
decision row, written after a (synthetic) look, about a test whose terms the builder chose.

**Remedy.**
- Fix the cells of each test (for example (b) per (kind, stop) at R = 1, as (c) and (e) are).
- A family-wise Z: Bonferroni over that count.
- T-13 (a)'s steps a minute per stop, and its seed (`[20261938, 4]`).
- (a)'s criterion: for example, L's and D's one-sided lower bound at the family's level above zero, with the plant's
  sign.

### M2 (MINOR) -- T-3 cannot see the reachable count's seal

**Where.**
- Lines 746-748: the reachable count "from the base's registered engine call with its day table restricted to the choice
  block's days ... and T-3 covers it".
- Lines 1136-1138: T-3 replaces "every bar from 2024-01-02" and compares "the valuation's inputs (the reachable count
  included)".

**Evidence.** P-14's engine reads its trades from `data/atlas/A3/walks.parquet` and A1's `events.parquet` and
`days.parquet`. Bars are read only where a walk is made afresh, for P-15 and P-16 (`identity/stage2_identity.py` lines
105-110).

**The failure it allows.** A reachable count for a 50- or 100-tick pick that reads the judged rows of A3's walks passes
T-3 unchanged.
- The base's outcomes there are Stage 2's, already read, so the leak is of the base's states, not of the tickets.
- But E-032 (2) made this exactly the condition for the fallback, and T-3 is the only mechanical check named.

**Remedy.**
- T-3 also replaces, or poisons, the judged rows of every file the reachable count's engine call opens. Alternatively,
  the adapter asserts that every walk row it consumes is dated at or before 2023-12-29.
- The build records, before stage A, whether the fallback applies.

### M3 (MINOR) -- no consequence if Q-55 does not reproduce

**Where.**
- Lines 17-18 and 1214: "No stage runs before Q-55 reruns Q-16's calibration".
- Line 1222: section 19, "Open before the pin ... 2. Q-55's clean rerun ... before any stage runs".
- `TASK_QUEUE.md` line 73: Q-55 is queued last in the heavy chain.

**Evidence.**
- E-035 (4): "the calibration's figures are exploratory until rerun from a clean checkout -- none is cited before".
- The family's pass line is pinned on that calibration's choice: `cons`, and the treated-cluster two-sample form.
- The draft says nothing about a rerun that does not reproduce: for example, a fixed bug, or one null above its level.

**The failure it allows.** A pinned family whose decisive statistic loses its calibration before the run. The
declaration cannot be edited, and a choice about what to do next would be made after seeing the rerun.

**Remedy.** One declared line: if Q-55's rerun shows `cons` or the treated two-sample `cons` above its level on any real
or realistic null at the family's k, the family is withdrawn before any read and re-declared under a new row.
Alternatively, pin only after Q-55.

### M4 (MINOR) -- the planning lookup is undefined at the edges

**Where.**
- Lines 558-574 (7.9): the MDL "is read at the family's k, and at the largest tabulated N at or below the cell's
  estimated judged fills".
- Lines 933-934 (13): a close is recorded as "no lift above the MDL (planning section)".

**Evidence.**
- Tables 4a, 4b and 11 hold k = 11 and k = 15, and N from 200 (the note's sections 4 and 6.2).
- K1 admits 100 choice-block fills. At the choice block's rate times the judged sessions, that is about 65 estimated
  judged fills, below every tabulated N.
- If another family is pinned first, k is 12 to 14, which has no column.
- The tables' real nulls are P-16's 150-tick pairs at win1 and net3. The cells are in win probability at R = 1.5 and 3,
  and at 50 and 100 ticks.

**Remedy.**
- Use the k = 15 column when the family's k is not tabulated (conservative).
- Below 200 estimated fills, write "above the 200-trade entry".
- State beside each figure which null's R and stop it is from.

### M5 (MINOR) -- the news row is stale, and 8284211's releases are unaddressed

**Where.** Line 198 (section 3, `news`): "no entry for article 13613539 is in `config/rules_extended.yaml`, nothing
loads it ... Tickets rest through other 09:00 CT releases". Also 0.3's N12 row.

**Evidence.**
- E-034 (Q-39) recorded 13613539: `config/rules_extended.yaml` lines 2073-2077, with its windows and its "pending orders
  do not fill" in SIM.
- It also recorded 8284211's list of seven releases (line 2036): CPI, NFP, the FOMC statement, **EIA crude oil
  inventories, EIA natural gas inventories, crop production**, and PPI.
- The EIA releases fall inside the tickets' resting window (08:30 CT to the cutoff).
- 6.3 sizes a 50-tick Combine ticket at the 50-micro allowance, which is a $50K Combine's full size.
- 10305426 rules out "trading your full Maximum Position Size directly into a scheduled major news event". E-034 leaves
  which events count unstated. The lead kept the funded opening held through an unnamed release, and listed it among the
  "not modelled".

**The failure it allows.** A resting full-size ticket fills in an EIA release minute, while 11.1 (iv) says conduct
tier 1 holds "of the routing", on a text that never considered it.

**Remedy.**
- Correct the sentence: the entry exists, and the tickets avoid 13613539's windows by construction.
- State E-034's reading for the tickets, and add it to 12 item 8's "not modelled" note.
- Alternatively, declare that allowance-capped tickets are cancelled from five minutes before to five minutes after
  8284211's releases. That is the lead's choice, made before the pin.

### M6 (MINOR) -- the confirmation's length rule is not fully fixed

**Where.** Lines 967-980 (14, "How much data").

**Evidence.**
- "The pick's judged pair terms ... have their signs flipped by session, with the lift added, and are placed on a
  calendar of the candidate length." How they are placed is not said: tiled, truncated, or resampled with replacement.
- "The fills assumed: the lower of the pick's two blocks' rates per session" conflicts with using the judged terms,
  whose rate is the judged block's.
- The rule is computed after stage C, when an outcome is known.

**The failure it allows.** The open details move the window's length, and so the purchase, after a look. They cannot
move the confirmation's level, which is fixed at 0.05.

**Remedy.**
- Fix the construction: for example, the judged block's session sums, resampled with replacement and thinned to the
  lower rate, on 21 m sessions.
- Report the same simulation's rejection rate at zero lift beside, as a size reading. *Synthetic*: `cons` at 0.05 on
  126 to 252 sessions rejects 0.8 % to 2.7 % (Appendix A).

### Notes and the reading

- **N1.** Line 631-632 names "the module as merged in Q-16's commits 2f5ffd0 and 3a7a3f5 (master bb3d913)". The module
  is unchanged since 3a7a3f5, and all three commits are ancestors of HEAD. But nothing hashes it:
  - `tests/test_lift_bound.py` line 249 pins `SHIPPED == "cons"` only;
  - an edit to `DIFF_DF_RULE`'s default, CR1's factor or `block_index` would change the declared statistic without
    touching the pinned file.
  - The remedy: record the blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2` in the pinning row, and have the run assert
    it.
- **N2.** Lines 635-638. `t_stats` and `diff_stats` set CR1's factor and the df from the non-empty blocks. "The judged
  block's calendar" is not named, and `block_index` cuts at n // b, so the block edges depend on the session count.
  Name the day list (every trading day the store holds from 2024-01-02 to 2026-07-16, void or not) and its count.
- **N3.** Lines 268-271, 759-760. In stages A to C both fills of a kind count, so C2's λ is the all-fills mean. Stage
  D's one-cancels-other spends only the first fill. If second fills differ, C2 prices uses at a lift partly earned on
  fills the routing never takes. Report λ on first fills beside C2.
- **N4.** Line 431 says "centred, studentised"; lines 586-590 compute t\*_b = (L\*_b - L) / se with the sample's se. That
  is a normalised, not a studentised, bootstrap. Relabel it. Either way it is uncalibrated, as 8's last paragraph says.
- **N5.** Lines 1124-1134. A two-sided 95 % interval over 3 arms x 2 kinds x 3 stops is 18 one-sided 2.5 % kill chances
  under a correct placebo: 1 - 0.975^18 ≈ 0.37 that at least one `break` (kind, stop) dies. It is conservative, since
  it costs cells and not the level. State it, or use Bonferroni.
- **N6.** Lines 997-1007. The word-bounded search now also finds 20261930:
  - in `prereg/DRAFT_F-O_opening_timing.md` line 885 and `prereg/DRAFT_F-R_resolution.md` line 819 (both reserve the
    block for F-02);
  - in `extended/user_beside.py` line 61, `SEED_BLOCK = tuple(range(20261920, 20261930))`. That is an exclusive bound in
    code, not a use, so a T-12 that greps code must not count it.
- **N7.** Lines 830-832. The tickets' shift uses `t21e`, the form Q-16 found lax at the family levels; it is untested at
  0.05. A lax shift makes floor (i) easier to pass. It is U1's verdict arm, so it matches how R\* is read. Say so.
- **N8.** Line 1180. Stage D's walks of the tickets at every R of the base's menu (6.3, 11.4) are judged-block reads of
  bars through `read_bars`, under `stage_D_gate_floor`. That row describes only the engine's reads. Nothing refuses
  them -- the reader checks the purpose's name -- but the row and each ledger line's `what` should say so.
- **N9.** The reader's `DECLARATION_PATH` (`extended/reader.py` line 121) needs `prereg/F-NN_*.md`. The status lines 3-24
  will change at the pin, so the pinning row should name the diff between the pinned bytes and this reviewed text.
- **R1 (a reading).** Lines 640-642. "A ticket's side is set each day ... So the family's sides persist at most one
  session."
  - What sizes the test is the dependence of the pair terms w, not the rule's reset.
  - Which level fills, and so the long or short mix of the fills, follows the day's path. A momentum or reversal regime
    gives w a mean that persists as long as the regime.
  - Q-16's real nulls are P-16's long-minus-short pairs, which carry drift, flipped by blocks of up to 63 sessions.
    They do not model a continuation-against-reversal regime, and `cons` was lax on the stress regimes.
  - The reading: state this residual beside the verdict, and report the pick's choice-block lift by quarter and the
    lag-1 correlation of its 21- and 63-session block lifts. Both come from stage B's own read, so nothing new is spent.

## 3. Does each earlier correction remove its defect?

| finding | the correction | removed? | why |
|---|---|---|---|
| v3 P1 (`pdc`'s placebo side) | the target day's own side; T-14 (e) | **sign: yes; size: no** | D is about zero under sign-only drifts; size-dependent drifts give D ≈ +3 (G1) |
| v3 V1 (reachable uses) | the records cap, the reachable count, no second trade, one-cancels-other | **yes** | 10 (i)-(ii), 11.2; T-3 does not reach the count's seal (M2); λ on first fills (N3) |
| v3 T1 (T-14 (c)'s generator) | every parameter fixed; a refusal, not a kill | **yes** | 17.6; (b)'s and (a)'s criteria are open (M1) |
| v3 T2 (switch granularity) | per (side rule, stop, R); a rung ladder with a kill | **yes** | 5.5, 7.1 |
| v3 V2 (ρ) | unknown sign; ρ² and 1 beside | **yes** | 10, 9.6 |
| v3 S1 (room cap) | `_plain_size`; floor (ii) a check | **yes** | 6.3, 11.1 |
| v3 N1-N11, N13 | as 0.3 | **yes** | -- |
| v3 N12 (13613539) | "a reading" | **stale** | E-034 recorded it (M5) |
| E-026 (reads line) | one line, three purposes | **yes** | parsed by `reader.declared_purposes`: `stage_C_judgement`, `stage_D_gate_floor`, `stage_D_scorecard`; none carries a choice word; one matching line |
| E-031 (2), E-032 (1) | the reverse walk-forward struck | **yes** | not on the line; 9.6's readings beside |
| E-032 (2) | choice-block days, or the records cap | **yes, in text** | T-3 cannot check it (M2) |
| E-029 | the pinned calendar | **yes** | 4.5 (a)-(b) |
| E-035 marks | `cons`; `two_sample_bound`; `pcons` | **yes** | the call signatures match the module (`bound` line 435, `two_sample_bound` line 400); the estimate and u_g are `diff_stats`' (lines 346-373); Gt = min(G1', G2') is `DIFF_DF_RULE = "treated"`; a member without a finite bound blocks the pass (lines 438-442, 422-427); stage B stated as uncalibrated; the null class stated (R1) |
| first read F1-F10, N1-N9 | as the v3 read found | **yes** | I relied on the v3 read's table; I re-checked F2 (past-only sources, 5.8) and F5 (the eligibility line, 8.5) |

## 4. What I tried that found nothing

- **The statistics as the calibration validated them.**
  - C1 is `bound(SHIPPED, ...)`, with `SHIPPED = "cons"`: the minimum of the trade-weighted CR1 t on 21-, 42- and
    63-session blocks, each at df = G' - 1.
  - C1' is `two_sample_bound` with the count-centred u_g and the treated-cluster df, which is the form Table 10b holds
    on.
  - The year-by-year readings and the confirmation use the same functions.
  - `pcons` draws with `p_bound.SEED = 20261919`, so 20261936 is honestly unused.
  - Stage B is said to be uncalibrated. Its role (a selection device on the choice block, spending nothing) is correct:
    - the program's level rests on C1 at 0.05/(k(k+1)) by `cons` on a block that took no part in the choice;
    - trades open and close in one session, and sides reset daily, so nothing straddles the boundary.
  - A lax q costs at most the judgement, plus stage D's read of the judged start days, which program U's nine families
    had already read.
- **`cons` outside Q-16's grid** (*synthetic*; Appendix A).
  - At one-sided 0.05 on 126, 189 and 252 sessions, with fill rates 0.5 and 2 a session, flip blocks of 1, 21 and 63
    sessions, and a 63-session regime component: 0.8 % to 2.7 % rejections. The single members ran 4.6 % to 6.7 %.
  - At 0.05/132 and 0.05/240, on 60 to 150 fills over 657 sessions with up to two correlated fills a session:
    0.07x to 0.54x nominal, at 200,000 replications each.
  - So the confirmation's form and the sparse-pick edge look conservative on these nulls. Real nulls were not used.
- **The reads line against the reader.**
  - `DECLARED_LINE` matches exactly one line, and `PURPOSE_TOKEN` takes three names.
  - `_choice_purpose` is false for each.
  - A stage C and D run under one clean run id satisfies `_once`.
  - The identity reads are kept off the line and must come from `identity/*.py` (`_identity`), as 18.1 says.
  - The confirmation window is refused outright.
- **Seeds.**
  - 20261930-39 are used only in this draft. Every other match is a reference, or the exclusive range bound in N6.
  - 20261935 (stage D's campaign) appears nowhere else, `vendor/` included.
  - My scratch seeds are outside the 2026xxxx space.
- **Count.** 18 cells; 54 = 36 `fade`-signed + 18 `break`-signed; k = 11 gives 0.05/132.
- **Leakage across blocks.**
  - Choice-block placebo sources are past-only, and their pools are calendar-defined.
  - `A` trails 20 full sessions.
  - Generators run per (replicate, kind, block).
  - The reachable count reads choice days, or is not used (subject to M2).
- **What else was left to choose after a look.**
  - The cutoff grid is fixed and read direction-free.
  - The T-13 (b) and T-14 generators are fixed.
  - The booking switches come from synthetic tests before any read.
  - The pick rule and its tie-breaks are fixed.
  - C2's caps come from stage A, before any lift is read.
  - Nothing I found except M6 (after stage C, for the purchase only) and M1 (the build's own tests).
- **`rn100`'s placebo.** Its distances are arithmetic modulo 100 points on both days, exchangeable whatever the overnight
  path, so G1 does not reach it.
- **T-14 (e) as declared.** With sign-only drifts, D is about zero (G1's first two rows), as the v3 read found.

## 5. What I could not check, and the experiments that would settle it

- **Whether NQ's overnight-move effect on this window depends on the move's size** (G1). This is in Stage 2's
  `results/s3_event_kinds.csv` (the `gap_glbx` and `gap_rth` rows), which is not vendored. Reading it is a
  prior-exposure read under section 2, and it needs a new snapshot under a new row.
  - G1's remedy does not need it. Option (a) needs nothing.
  - Option (b) needs the extended T-14 (e): synthetic, 40,000 days per arm, two kinds and three stops, at about the
    cost of (e) itself (minutes of CPU per arm, well under 500 MB), under the run lock as (e) already is.
- **Q-55's rerun** (M3). It is heavy, and it is the lead's.
- **Whether Stage 2's builders can restrict P-14's engine to choice-block days without opening judged rows** (M2,
  E-032 (2)). That needs reading the engine's code path from `atlas_a3.cached_walk` to the gate's day table. It is
  light, but it is the build's.
- **The strength and persistence of momentum and reversal regimes in F-02's pair terms** (R1). That needs outcomes.
  Stage B's own read gives it beside, at no cost.
- **A per-rung `dv`** (V2, carried). It needs D-667's solver.

---

## Appendix A. The scripts (scratchpad copies are not durable)

`pdc_mag.py` -- G1's check (first table rows: `python pdc_mag.py 717171 3000`, 67 s):

```python
import sys, time
import numpy as np
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-levels")
from extended import walker as W

SEED, DAYS, STEPS = int(sys.argv[1]), int(sys.argv[2]), 400
S, RRS, SD_ON = 100, (1.0,), 200
EABS = SD_ON * np.sqrt(2 / np.pi)                      # E|g| for g ~ N(0, SD_ON)
LIVE, CUT = W.slot(8, 30), W.slot(14, 0)
PRESET = W.Rules("f02_preset", W.FLAT_ENTRY, "worst_less_two", False)
FIRST = LIVE + 1; M = W.C_FLAT - FIRST + 1; N = W.C_FLAT + 1; BASE = 80000

def day(rng, drift):
    st = np.where(rng.random(M * STEPS) < 0.5 * (1.0 + drift), 1, -1).astype(np.int32)
    path = (BASE + np.cumsum(st)).reshape(M, STEPS)
    o = np.full(N, float(BASE)); h = o.copy(); l = o.copy(); c = o.copy()
    close = path[:, -1].astype(float); opens = np.concatenate([[float(BASE)], close[:-1]])
    o[FIRST:], c[FIRST:] = opens, close
    h[FIRST:] = np.maximum(path.max(axis=1), opens); l[FIRST:] = np.minimum(path.min(axis=1), opens)
    for x in (o, h, l, c): x[0] = np.nan
    return o * W.TICK, h * W.TICK, l * W.TICK, c * W.TICK

def w_of(rule, side_level, dist, bars):
    if dist < 1: return None
    lvl = (BASE + side_level * dist) * W.TICK
    od = (W.Order(W.STOP_ENTRY, side_level, LIVE, lvl + side_level * W.TICK, CUT) if rule == "break"
          else W.Order(W.LIMIT_ENTRY, -side_level, LIVE, lvl, CUT))
    t = W.trade(od, *bars, S, RRS, rules=PRESET, fill_bar="pair", mirror_booking="symmetric")
    if t.fill.status != "filled": return None
    return 0.5 * (float(t.rule.win[0]) - float(t.mirror.win[0]))

def run(delta, mag, seed):
    rng = np.random.default_rng(seed)
    rec = {(r, k): ([], []) for r in ("break", "fade") for k in ("L", "Pm")}   # per day: (sum w, count)
    absg = {(r, k): [] for r in ("break", "fade") for k in ("L", "Pm")}
    for _ in range(DAYS):
        gE = int(round(rng.normal(0, SD_ON))); gD = int(round(rng.normal(0, SD_ON)))
        sE = 1 if gE > 0 else -1
        f = abs(gE) / EABS if mag else 1.0                 # <- the line the variants change
        bars = day(rng, delta * sE * f)
        for rule in ("break", "fade"):
            for key, side, dist in (("L", -sE, abs(gE)), ("Pm", -sE, abs(gD))):   # real pdc; side-matched placebo
                w = w_of(rule, side, dist, bars)
                s_, n_ = rec[(rule, key)]
                s_.append(0.0 if w is None else w); n_.append(0 if w is None else 1)
                if w is not None: absg[(rule, key)].append(abs(gE) / EABS)
    out = {}
    for rule in ("break", "fade"):
        SL, NL = map(np.asarray, rec[(rule, "L")]); SP, NP = map(np.asarray, rec[(rule, "Pm")])
        mL, mP = SL.sum() / NL.sum(), SP.sum() / NP.sum()
        u = (SL - mL * NL) / NL.sum() - (SP - mP * NP) / NP.sum()      # day-clustered, count-centred
        out[rule] = (int(NL.sum()), int(NP.sum()), 100 * mL, 100 * mP, 100 * (mL - mP), 100 * np.sqrt((u ** 2).sum()),
                     float(np.mean(absg[(rule, "L")])), float(np.mean(absg[(rule, "Pm")])))
    return out

t0 = time.time()
for i, (delta, mag, name) in enumerate(((+0.002, False, "follow const"), (+0.002, True, "follow |g|"),
                                        (-0.002, False, "reversal const"), (-0.002, True, "reversal |g|"))):
    r = run(delta, mag, SEED + i)
    for rule in ("break", "fade"):
        nL, nP, mL, mP, d, se, aL, aP = r[rule]
        print(f"{name:15s} {rule:5s} fills L {nL:5d} Pm {nP:5d} | L {mL:+6.2f} Pm {mP:+6.2f} | D {d:+5.2f} (se {se:4.2f}) "
              f"| mean |g|/E|g| on fills: L {aL:.2f} Pm {aP:.2f}")
print(f"{time.time() - t0:.0f} s")
```

Output, `717171 3000` (the `break` rows; `fade` is the exact negative):
- follow const: fills 1,513 / 1,532; L -8.13; Pm -8.81; D +0.68 (se 1.58); |g| on fills 0.63 / 1.01;
- follow |g|: fills 1,581 / 1,607; L -5.31; Pm -7.16; D +1.84 (1.47); 0.57 / 0.85;
- reversal const: fills 2,491 / 2,512; L +11.30; Pm +10.71; D +0.59 (1.23); 0.88 / 1.01;
- reversal |g|: fills 2,651 / 2,452; L +8.88; Pm +10.20; D -1.31 (1.18); 0.97 / 1.07.

**The two variants** (each changes only the marked `f = ...` line and the arm list):
- `pdc_mag2.py`: `f = ((abs(gE) / SD_ON) ** 2 if mag == 2 else abs(gE) / EABS) if mag else 1.0`, with arms
  `((+0.002, 1, "follow |g|"), (+0.002, 2, "follow g^2"))`; run as `727272 8000`, 76 s:
  - follow |g|: fills 4,156 / 4,174; L -5.14; Pm -8.12; D +2.98 (0.93); 0.56 / 0.85;
  - follow g²: fills 4,315 / 4,369; L -1.78; Pm -5.54; D +3.75 (0.92); 0.56 / 0.80.
- `pdc_mixed.py`: `f = (abs(gE) / EABS - 1.0) if mag == 3 else ((abs(gE) / EABS - 0.5) if mag == 4 else 1.0)`, with
  arms `((+0.003, 3, "mixed c=1.0"), (+0.003, 4, "mixed c=0.5"))`; run as `737373 8000`, 83 s:
  - mixed c = 1.0: fills 5,091 / 5,422; L +5.84; Pm +2.37; D +3.47 (0.84); 0.62 / 0.83;
  - mixed c = 0.5: fills 4,363 / 4,560; L -0.78; Pm -3.70; D +2.92 (0.92); 0.55 / 0.79.

`cons_short.py` -- `cons` at 0.05 on short calendars (seed 818181, 20,000 replications a row, 17 s):

```python
import sys, time
import numpy as np
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-levels")
from extended import lift_bound as LB

rng = np.random.default_rng(818181)
REPS = 20000
for n in (126, 189, 252):
    for lam in (0.5, 2.0):
        for L in (1, 21, 63):
            for pers in (0.0, 0.5):
                N = rng.poisson(lam, size=(n, REPS)).astype(float)
                reg = np.repeat(rng.normal(0, 1, size=(n // 63 + 2, REPS)), 63, axis=0)[:n]
                m = 0.06 * ((1 - pers) * rng.normal(0, 1, size=(n, REPS)) + pers * reg)
                S = m * N + rng.normal(0, 1, size=(n, REPS)) * np.sqrt(N * 0.18)
                phase = rng.integers(0, L, size=REPS)
                blk = (np.arange(n)[:, None] + phase[None, :]) // L
                sgn = np.take_along_axis(np.where(rng.random(size=(blk.max() + 1, REPS)) < 0.5, -1.0, 1.0), blk, axis=0)
                S = S * sgn
                r = [LB.many_levels(mth, S, N, [0.05])[0][0].mean() for mth in ("cons", "t21w", "t42w", "t63w")]
                print(n, lam, L, pers, [round(x, 4) for x in r])
```

Output: `cons` 0.0082-0.0134 at 126 sessions, 0.0146-0.0199 at 189, 0.0223-0.0274 at 252. The single members ran
0.046-0.067, the highest being `t21w` with the 63-session regime at rate 2.

`cons_sparse.py` -- `cons` at the family levels on sparse picks (seed 828282, 657 sessions, 200,000 replications per
row in chunks of 20,000, 126 s):

```python
import sys
import numpy as np
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-levels")
from extended import lift_bound as LB

rng = np.random.default_rng(828282)
n, CH, NCH = 657, 20000, 10
levels = [0.05 / 132, 0.05 / 240, 0.001, 0.01]
for fills in (60, 100, 150):
    p = fills / n / 1.15
    for L in (1, 21, 63):
        rej = np.zeros(len(levels)); tot = 0
        for _ in range(NCH):
            f1 = rng.random((n, CH)) < p
            f2 = f1 & (rng.random((n, CH)) < 0.15)
            v1 = rng.choice([-0.5, 0.0, 0.5], size=(n, CH), p=[0.4, 0.2, 0.4])
            same = rng.random((n, CH)) < 0.5
            v2 = np.where(same, v1, rng.choice([-0.5, 0.0, 0.5], size=(n, CH), p=[0.4, 0.2, 0.4]))
            S = v1 * f1 + v2 * f2; N = f1.astype(float) + f2
            phase = rng.integers(0, L, size=CH)
            blk = (np.arange(n)[:, None] + phase[None, :]) // L
            sg = np.take_along_axis(np.where(rng.random((blk.max() + 1, CH)) < 0.5, -1.0, 1.0), blk, axis=0)
            r, _ = LB.many_levels("cons", S * sg, N, levels)
            rej += r.sum(axis=1); tot += CH
        print(fills, L, [(a, int(k), round(k / tot / a, 2)) for a, k in zip(levels, rej)])
```

Output: at 0.05/132, 0.18x-0.54x nominal; at 0.05/240, 0.07x-0.48x; at 0.001, 0.27x-0.47x; at 0.01, 0.46x-0.59x.
