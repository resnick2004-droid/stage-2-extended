# Red team: `prereg/DRAFT_F-13_topstep_survey.md` and `tests/test_f13_draft.py` (wt/wt-fs1 b76e801), 2026-11-27

**Verdict: BLOCK (must be re-declared).** Six blocking findings: one changes the source of every limit (W42-R1 to
W42-R2), one changes the finalist rule or the power gate, one changes the screen's seed indices, one adds a disclosure
and a count, one corrects S1's declared status, and one corrects the tier-1 news floor. Each needs a full re-read of
the corrected text (`_v2_`). There are eleven minors.

Read at the worktree `%LOCALAPPDATA%\stage2-extended-wt\wt-fs1`, HEAD b76e801, working tree clean. I read the governing
rows one at a time (E-213, E-290 to E-297), never the whole of `DECISIONS.md` or `docs/MEASURES.md`. Line numbers are
the draft's unless a file is named. The brief named what to attack and gave no expected answer. One brief instruction
is itself a conclusion: E-297 (3)'s ruling that the "S1 NotComputed" wording is to be corrected. I checked that ruling
against the text independently (B-5) and did not take it on trust. No seed literal is quoted here: seeds are named by
role. No result number is typed. The arithmetic figures below come from small synthetic checks, not from result files.

---

## Blocking findings

### B-1 (blocking): the limits, budgets, weights, delta\* and floor come from W42-R1, which E-296 says is never applied

- **Where:** the head list, lines 13-28 ("Awaiting W42-R1's application ... `results/w42_r1_values.csv`"). Also lines
  142-143, 329-330, 461, 507 ("one for each of W42-R1's six limits") and 543 (spec `objective.rule_id`), section 7
  rows at lines 589-599, the clause at 646-653, lines 700-701 and 747. In the code: `extended/survey.py:123`
  (`W42_RULE = "W42-R1"`, which `load_spec` and `load_objective` enforce), and in the test, `tests/test_f13_draft.py`
  lines 61-72 (`AWAIT`, `W42_ROWS`) and 218.
- **Evidence:** E-296 says W42-R2 is the setting rule applied to H4, W42-R1 is never applied, and `DRAFT_F-13` imports
  its limits from `extended.wave42_r2`. W42-R2 (wt/wt-w42r2 8a98066, `docs/plans/WAVE42_SETTING_RULE_R2.md` section
  3.1) adds a seventh limit, `net_month_12_p50` (a floor, p50, horizon 252). Its output is `w42_r2_values.csv`, written
  by `scripts/wave42_r2_apply.py`. E-296 (1)-(2) adds that W42-R2's headroom counts the search-seed noise as well.
- **The failure it allows:**
  1. W42-R1's headroom counts only the held-out coin noise. Where that headroom binds, a design equal to the best
     baseline is refused far above the nominal rate (E-296 (1)). Section 9's E-015 clause then fails and closes the
     line. Or, if the gate somehow passes, good designs are refused on the search years.
  2. Without the seventh limit, a design that ranks well on P_B but has a median 12-month net cash below the formula's
     floor can be carried. That is the defect W42-R2 exists to fix.
  3. The protocol sha256 (line 542) binds "the six limit measures", and section 6 fits six limit surrogates. A
     seven-limit objective would be refused at the binding or read without its surrogate.
- **Remedy:**
  - Replace W42-R1 with W42-R2 everywhere a value is taken: rule id, module `extended.wave42_r2`, application
    `scripts/wave42_r2_apply.py`, output `results/w42_r2_values.csv`, its pin file and its pinning row.
  - Name the seven limits in section 7 row 1, `net_month_12_p50` with its direction, statistic and horizon.
  - Write "one surrogate for each of the seven limits" and "the seven limit measures" in the protocol sha256.
  - Changing `survey.W42_RULE` (or making it a spec value bound by the pin) becomes a declared build item.
  - Move the test's `AWAIT` and `W42_ROWS` to W42-R2's output keys.
  - Add one sentence to the clause at 646-653: no calibration or gate has read W42-R1's limits (only Q-221's
    synthetic check of its formula read anything, and W42-R1 was never applied). So moving to W42-R2 is not "a
    corrected rule ... whose searches never enter this F-HT", and this search's membership is unaffected.
  - The pin must cite W42-R2's pinning row, dated before any H4 read, and W42-R2's own red-team read.

### B-2 (blocking): the search-year keep rule fails a design better by exactly delta\*, and the power gate never sees that rule

- **Where:** section 7's order rule, line 596 ("kept only if it beats each baseline by more than delta\* at the t
  threshold of z = `wave42.RESOLVE_Z` on the re-read"). Section 9's power gate, lines 665-679. Section 6's precision
  bullet, lines 482-491. The code: `extended/survey.py:1562-1574` (`beats_baselines`: t = (gap - delta\*) / se against
  the t quantile of z at n - 1 degrees of freedom, required for each baseline).
- **Evidence:**
  - The rule asks the re-read gap to exceed delta\* by about two of its own standard errors, against each of the four
    baselines.
  - Synthetic arithmetic, using the declared 64 re-read seed indices and z = RESOLVE_Z: suppose a design's true
    advantage over a baseline is exactly delta\*. Then its chance of being kept against that one baseline equals the t
    tail beyond the threshold, which is the one-sided level of z = 2 (a few in a hundred). An even chance needs a true
    advantage of about delta\* plus two standard errors. That is per baseline; the four comparisons are intersected.
  - The power gate (lines 665-679) plants an improvement of delta\* and measures the held-out pass line, plus the
    do-nothing floor "at the search-year screen". It does not model the search-year route a planted design must
    survive to reach the finalists' row: the screen-size floors, the promotion, the top-4 cut, this keep rule and the
    plateau.
  - The MDE printed in section 6 is for a one-sided comparison at 0.05 with zero margin. That is not the keep rule.
- **The failure it allows:** the gate reports a power that the line does not have, the go row is written, and the
  survey runs. A design better than every baseline by the size that matters, which is exactly the design the gate
  plants, almost never reaches the finalists' row. The search then closes as a fail that the gate said was unlikely.
  This is the "strict rule failing good designs" defect that E-296 (1) found in W42-R1, here in the finalist rule
  (CHARTER 3.8 (b), E-015's condition).
- **Remedy:** take either (i) or (ii), and declare it before the pin.
  - (i) The power gate's planted design goes through the whole declared search-year route: the screen at its screen
    size with its floors, the promotion, the deciding size, the top-4 cut, the keep rule and the plateau. The go row
    requires the power target on that route. E-015's clause is read on the same route.
  - (ii) Re-declare the keep rule so that its power at delta\* is adequate and stated. For example: the re-read point
    estimate beats each baseline by more than zero, with the t check beside; or by delta\* at the point estimate, as the
    O-5 ruling reads the limits.
  - Either way, the build citation prints the keep rule's power at a true gap of delta\*, from the declared re-read
    count and H4-B's search-year sigma (W42-R2's `power`), beside the screen's and the deciding size's MDEs.

### B-3 (blocking): the deciding size re-reads the screen's own seed indices, so promoted cells keep their screen luck

- **Where:** section 6, lines 471-481. The spec at line 536 (`screen.seeds`, the selection indices 0 to 3) and line
  541 (`protocol.seeds`, 0 to 15, every start). The test's `test_the_screen_and_the_deciding_size_are_declared`, line
  467, which asserts `set(sc["seeds"]) < set(s["protocol"]["seeds"])`, so it enforces the overlap.
- **Evidence:**
  - The screen's units (indices 0 to 3, every 4th start) are a subset of the deciding units (indices 0 to 15, every
    start): one sixteenth of them.
  - The 32 promoted cells were chosen as the best on exactly those units, and their deciding reading still contains
    them. A round 5 to 8 cell's deciding reading carries no such selection.
  - Synthetic check: 640 cells of equal true composite, the top 32 promoted by screen reading. The promoted cells'
    deciding readings come out biased upward by about half a deciding-size standard error against an unselected cell.
    This is the arithmetic of the declared sizes alone.
  - So the claim at lines 480-481, "no screen reading is ever compared with a deciding one", is false in substance.
- **The failure it allows:** the finalist candidates (the top 4 by deciding reading) and their order are tilted toward
  promoted cells over cells from rounds 5 to 8. The order matters because the finalists keep their selection order,
  and that order becomes their place in F-HT's fixed sequence. The rounds 5 to 8 surrogate is also fitted on biased
  points.
  - The held-out level is not affected, because the held-out coin field is a fresh role.
  - The search's choice and order are affected. The re-read seed indices (16 to 79) are fresh, so the keep rule
    itself is not affected.
- **Remedy:**
  - Give the screen its own range of indices of the search-year coin role, disjoint from both the deciding indices and
    the re-read indices (for example a range above the re-read range, declared now, with a fixed-length key). Starts
    may overlap: the history is common to every design, and only the coin draws carry selection luck.
  - Flip the test to assert disjointness of the screen, deciding and re-read indices.
  - Section 12 names the screen's index range under its role.

### B-4 (blocking): a search-year read of a design in this space, seen by those who set this search's rules, is undisclosed and uncounted

- **Where:** section 2 (no ledger of search-year reads before the pin). Section 6's head ("never extended after a
  look"). Section 13's count, lines 800-810. Section 16, "Empty at the pin", lines 936-939.
- **Evidence:**
  - E-290 (4) and E-291 record the exploratory early look, Q-213: RL3's resting orders at prior-session levels, fade,
    latency-free, NY AM, Topstep 50K, zero edge, on the search years. The manifest of
    `results/early_look_rl3_pd_fade.csv` gives first and last dates inside the search years and says
    `exploratory: true`. I read the dates only, not the outcomes.
  - P-14's H4-B readings were placed beside it.
  - W42-R2's own text records that the operator and the lead saw P-14's 12-month figures from that look.
  - That is a design of this space's `rl3` component family. The lead's rulings on this text were made after it: T1's
    narrowing (keeping `rl3`), the no-harm margin set to delta\*, and the screen and promotion design (E-292 (4), E-297
    (2)).
  - The draft does not mention the look. `results/variants.jsonl` has no row for it, so section 13's count is short by
    at least one design read on these years.
- **The failure it allows:** a reader of the verdict cannot tell that this search's rules were set by people who had
  seen a search-year outcome of a design in its space and a baseline's 12-month figures. A choice that may have used
  the look sits unlabelled as fixed (CHARTER 3.3 (f); E-207 (2)'s miscounted case). The held-out test's level is
  unaffected; the honesty of "nothing chosen after a look" is not.
- **Remedy:**
  - Add a ledger of search-year reads before the pin to section 2: the early look by job, result file and row (E-291),
    the P-14 readings beside it, and who saw them.
  - Date each lead ruling in this draft against that ledger, with one line per ruling saying whether it used the look.
    Any ruling that did is labelled in section 16.
  - Count the look's cell in section 13, logged as exploratory or with the reason it is not.
  - Carry W42-R2's disclosure beside the verdict.

### B-5 (blocking): S1's row declares the stop width refused in a clean run, which E-297 (3) overrules and the rest of the text contradicts

- **Where:** line 271 ("in a clean checkout that file is absent ... so S1 is `NotComputed` there and carried as refused,
  and the space's built digest ... is computed on that basis"). Contradicted by:
  - line 501 (the dimension count "with S1's slot dimension");
  - line 553 (the plateau steps "one sixteenth of each real lever's loaded range");
  - line 562 (the space part's data names `results/s1_range.csv` by sha256);
  - line 376 (the stop band row: "S1's lower cap is the registered stand-aside floor");
  - lines 302-306 (S1 as the volatility unit's multiple).
- **Evidence:** E-297 (3): S1 stays searched; `scripts/run_clean.py` supplies the git-ignored file (`git check-ignore`
  confirms `.gitignore:39`); `s1_range.load_range` checks its manifest's sha256 before any use. The draft's cited raw
  sha256 matches the main tree's copy, which I checked.
- **The failure it allows:** as written, the bound space digest is computed with S1 refused while the clean run supplies
  the file.
  - Either the runner refuses at the digest (safe, but a lost run and a re-declaration), or someone recomputes the
    digest to match, and the space run is not the one declared.
  - Read literally, with S1 refused a design has no stop width, so the gate's stop band check has nothing to check.
  - This changes a declared rule and a bound number, so it is not a minor.
- **What else depends on the wording:** only the digest (spec `parts.space.digest`, head list line 33) and the build
  that computes it.
  - The regimes' v(t) (line 595) reads `trail20_range_pts`, the unit, not the file.
  - T7's file is tracked (`git ls-files`), so it is unaffected.
  - The section 2 ledger sentence at line 232 already treats S1 as searched.
  - The test has no assertion on `NotComputed`.
- **Remedy:**
  - Rewrite S1's row per E-297 (3): searched in every run. The clean run supplies the file read-only from the main
    tree's verified copy. `load_range` refuses unless the file's raw sha256 equals the cited one and its manifest
    verifies, and the runner re-checks the hash at exit.
  - The digest is computed with S1 active.
  - Add a test that a clean checkout without the supplied file refuses, and never falls back to `NotComputed`.

### B-6 (blocking): the tier-1 news floor names a mechanism that is empty for Topstep, and its count cannot fail there

- **Where:** section 4's contract-fit rows, line 382 ("the trigger library's news windows through RD-05's adapter")
  and line 383 (conduct tier 1). Section 1, line 100.
- **Evidence:**
  - `extended/modes_news.py`'s docstring says: "Topstep's `tier1_news_events_restriction` is `changed` ... no rule
    reaches `TS`". So no news window applies to a Topstep account.
  - `tier1_counts` counts `full_size_into_news` only for accounts a rule reaches. For Topstep it is zero by
    construction: a check that cannot fail.
  - The real protection is the triggers' `bls` window (no entry from the session's open to 07:35 CT on a BLS release
    day) and FOMC days out whole. That covers the record's quoted Topstep events (CPI, NFP, PPI, FOMC).
  - However, the verified `prohibited_strategy_max_size_into_major_news` prohibits "full Maximum Position Size directly
    into a scheduled major news event" and defines no list.
  - London runs to the NY anchor (lever table T2), so a London or Asia position can be open across a non-BLS 07:30 CT
    release. An example is BEA's GDP, whose days Stage 2's P-16 marks.
  - S3 and S5 can size up to the position limit.
- **The failure it allows:** a carried playbook can hold the full maximum position size across a scheduled release
  that Topstep may treat as major news, while the declaration says the news floor holds and its count shows zero.
- **Remedy:**
  - Declare the reading of "scheduled major news event": at least the vendored BLS and FOMC lists and the BEA days
    Stage 2 uses, or a stricter reading.
  - State the BLS and FOMC exclusions as Topstep's enforcement, replacing the RD-05 adapter sentence.
  - Add a refusing count on the taken-trade log: no position at the full maximum position size open across any declared
    release minute, computed from the calendars and not from reached accounts. Test it with a planted violation that
    fails it.
  - Or refuse any position, of any size, open across those minutes.

---

## Minor findings

- **m-1 (minor), lines 466-467: the sizes are left to the lead after H4-B's run.**
  - "to be sized from H4-B's measured cost before the pin: the lead sizes them." This covers N, rounds, batch, the
    selection, screen and re-read counts, and the candidates.
  - E-296 asks that nothing move after H4's search-year readings are seen.
  - Fix: declare the sizing formula now, from H4-B's measured wall-clock per unit (its manifest) and a declared hour
    budget, with the drafted values as ceilings. No H4 reading enters except W42-R2's `power` sigma for the printed
    MDEs.
- **m-2 (minor), section 6 lines 492-495: the build requirement does not name the code points today's runner gets
  wrong for two sizes.**
  - `_keep`'s `ctx.selection.setdefault` and `finalist_candidates`' `seen.setdefault` keep a cell's first reading,
    which would be the screen reading of a promoted cell (`extended/survey.py:1506-1511`, `1644-1659`).
  - `run_rounds` passes every reading to `propose`, mixing the two sizes.
  - The memo key `(design_id, seeds)` (line 1480) omits the start stride.
  - The ledger declares one protocol, and `admit_one` and the plateau read on it.
  - Fix: list each of these as a refusing test of the build.
- **m-3 (minor), section 6 lines 476-481: the promotion's edge cases are undeclared.**
  - Fewer than 32 cells may pass the screen floors.
  - The rounds 5 to 8 surrogate starts from about 32 points in a space of roughly fifty dimensions.
  - "The search-year screen" in sections 9 and 10 (lines 666 and 700) now means two things.
  - Fix: declare promote-all-passers or a refusal, the proposer's minimum, and which reading the do-nothing floor's
    "screen" means: both the screen-size promotion floor and the deciding-size ranking floor.
- **m-4 (minor), lines 353, 598 and 756: "S1's seeds" (the coin role) reads as the stop-width lever S1.** Rename the
  roles or write "the search-year coin role's selection indices".
- **m-5 (minor), lines 498-499: contradictory sentence.** "Read ... at every seed of the protocol's 16 selection seed
  indices at the deciding size (the survey itself at the screen size)." Say that the survey is read at the screen size.
- **m-6 (minor), line 759: S4 is reserved as "the held-out test's coin field".**
  - F-HT is joint over the firms and owns its coin field (E-238).
  - Fix: write S4 as a proposal that F-HT may adopt, with F-HT checking disjointness from every member's search-year
    roles, including the screen indices of B-3.
- **m-7 (minor), section 11: E-294 (4)'s reporting is not written in.**
  - Missing: the three columns (contract-only, martingale-outcome, as-traded) with the as-traded gap in both periods,
    the edge-sensitivity reading, Q-224's stress arms, and the execution-fit block.
  - Reconcile with section 10 (c), where the +1-tick and 10 %-missed stress is a deciding floor. Say that the
    search-year stress arms decide nothing and that the held-out stress floor's code is bound at F-HT's pin.
  - Ordering by an as-traded statistic is correctly absent.
- **m-8 (minor), line 381: the schedule builder's void context is not named.**
  - H4's coin source uses `day_calendar.day_context`, whose `RESEARCH_ONLY` voids (early ends, data-defect days, H2's
    overnight missing-minute rule) are known only after the alert. The playbook uses `alert_context`.
  - Fix: declare `day_context` for designs and baselines alike, pairing with H4. Report beside the share of offers
    removed for research-only reasons per reading class. The overnight rule removes the most disordered nights from
    overnight components only.
- **m-9 (minor), section 7 line 596: the plateau's power is not printed for this space.** With every active lever
  stepped (k_max near a hundred) at 64 re-read seeds, print in the build citation the tolerance, `size_bound` and the
  power against a spike of twice delta\*. `extended/plateau.py` says the re-read count decides the power.
- **m-10 (minor), head list lines 29-31: H3-D's generator, plants' grid and replicate counts are written after H4's
  readings.** Require H3-D to read H4 only through W42-R2's output. This is a point for H3-D's own red team.
- **m-11 (minor), the test does not cover these points.** With B-1, B-3, B-5 and B-6, add or flip tests: W42-R2's
  keys, disjoint screen indices, refusal when the S1 file is missing, and the planted tier-1 violation.

---

## What I tried that found nothing

- **Hashes:** the template, the held-out template, H4, W42-R1's text, `results/search_calendar.csv`,
  `results/h4_registered_constants.csv`, `results/s1_range.csv` (raw) and the lever table's blob all match the cited
  values.
- **Seed block:** a word-bounded search over every branch, remote and tag, and every worktree and the main tree
  (licensed data excluded), finds the block only in this draft (and its remote copy). The test's guard has planted
  controls. The re-read indices are disjoint from the selection indices, and `CellLedger.begin` refuses otherwise.
- **Held-out years:** the protocol's blocks end inside the search years, there is no `Judged-block reads:` line, and
  S4 is drawn by nothing.
- **Input manifests:** S1's and T7's manifests carry the search-year calendar. T7 is fitted on year folds of the search
  years, not in-sample. The early look's manifest dates lie inside the search years.
- **Pairing and sign:** baselines are read inside each design's run on the same seeds and starts (`read_design`,
  `out.arms[b]`). The composite is negated and minimised consistently, so "lowest predicted" in the proposer is
  correct.
- **Do-nothing floor:** `null_journeys` is computed from the caps, B\* and the weights alone, so comparing a
  quarter-start reading with it is not an unpaired comparison.
- **FOMC calendar:** it holds scheduled statement days only, so emergency meetings are not treated as known in advance.
- **k and count:** k = 13 next, and the search takes none. The count's product equals the spec.
- **Baselines:** the naive coin keeps a breakeven move that the designs are barred from. That favours the baselines,
  so it is conservative for the designs.
- **The form test:** `tests/test_f13_draft.py` passes at b76e801 (run without caches; the tree stayed clean).

## What I could not check

- W42-R2's fix pass (the headroom counting both noises, E-296 (2)) is not at the branch tip.
- The screen protocol and `extended/survey_parts.py` are not built.
- H3-D is not written.
- The look-ahead of sigma, `trail20_range_pts`, v(t) and RL3's levels is declared correctly. The scramble tests belong
  to the build.
- Whether the vendored BLS list holds every CPI, PPI and NFP day: no heavy run. A light check would compare the list
  with BLS's published schedules for 2020 to 2023.
