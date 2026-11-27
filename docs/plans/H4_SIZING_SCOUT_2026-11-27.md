# H4-B sizing scout: is H4-B bigger than W42-R1's pass limits need? (2026-11-27)

Read-only scout (wt-scout role). Nothing was run except two process listings (memory, no job). No `results/h4_readings_*`
or `results/h4_trades_*` file was opened. No held-out date was read. No seed value is quoted. The hours below come from
the H4-B run logs' batch timing lines and the part manifests' `elapsed_s`. Each one is cited. Where a figure is an
estimate built from code structure rather than measured, it is labelled **estimate**.

## The question

H4-B runs each baseline at `J_H4 = 128` coin seeds over every search-year start, on four arm-runs. Each baseline takes
about 36 h of machine time. Could the remaining baselines run smaller (fewer seeds or starts) and still meet every
declared minimum and W42-R1's precision rule? If not, which other speed levers keep quality?

## The answer

**Keep the size.**
- **No slack on starts.** W42-R1 refuses any input whose start days are not every search-calendar session.
- **Seeds: formal slack against W42-R1's code, but not against H4's own rule.**
  - W42-R1's code needs at least `H4_MIN_SEEDS = 62` seeds before a gap may resolve.
  - H4's declared J rule needs at least 104 to 109 seeds, which it rounds up to 128.
  - The pairing rule forces the naive coin and P-16 to use P-14's seed list.
- **Shrinking to 64 would save about 43 h, but it is not defensible.**
  - It breaks H4's declared rule.
  - It needs P-14 and P-15 truncated after their files were written.
  - It moves delta\* in a direction the lead could have been steered toward by P-14's per-seed spread, which is already
    on disk. It would be the first entry in H4's section 19 ("anything chosen after seeing results").
- **Workers are the lever that keeps quality.** Raising the worker count, after measuring an H4-B worker's real memory
  peak and freeing memory, gives the same saving with byte-identical outputs.
- **Two other findings:**
  - P-15's part 5 appears to have stopped.
  - Using P-15's part layout keeps every part under the 8 h cap.

## Evidence

### 1. What precision W42-R1 needs from H4's output (declared numbers)

| what | declared value | where |
|---|---|---|
| starts | every session of the search calendar, else refused | `extended/wave42.py:272-273`; rule text V-1 (`docs/plans/WAVE42_SETTING_RULE.md:60`) and l.116 |
| seeds, form | at least 2 distinct, exactly the indices 0 to J - 1 | `extended/wave42.py:262-265`; rule l.117 |
| seeds, pairing | the same start days and seeds for every baseline, else refused | `extended/wave42.py:276-277`; rule l.222 |
| seeds, resolution floor | `H4_MIN_SEEDS = 62`: below it no gap may resolve and delta\* falls back to `DELTA_FRACTION` x spread | `extended/wave42.py:59, 733-748`; rule l.262, l.411-418 |
| why 62 | the smallest nJ at which a false resolution between two equal baselines (a Student t with nJ - 1 df, above `RESOLVE_Z`) stays at most 0.05 | rule l.262 |
| resolution line | `RESOLVE_Z = 2.0`; `DELTA_MIN = 0.01`; `DELTA_MAX = 0.05` | `extended/wave42.py:66-69`; rule l.269 |
| power target | `POWER_TARGET = MDL_POWER` (0.8, `extended/family_stats.py:89`), applied to the **held-out test's** J = `TEST_SEEDS = 1000`, not to H4's J | `extended/wave42.py:60, 70, 637`; rule 5.3, l.437-439 |
| limits | value = the worst baseline's pooled estimate, or the best's plus a headroom. The headroom's se is H4's per-seed sd times sqrt(\|E_h search\| / (`TEST_SEEDS` x n_h test)), so H4's J enters only through how precisely that sd is estimated | `extended/wave42.py:803-814`; rule l.478-495 |
| budgets and caps | quantiles pooled over every unit (starts x seeds x baselines), budgets rounded to the fee lattice | `extended/wave42.py:657-667, 676-685` |
| re-read seeds | **not W42-R1's.** `MIN_REREAD_SEEDS = 5` is the survey plateau's floor | `extended/search_space.py:184, 757-758` |
| guard and audit sample | `SAMPLE_SEEDS = 64`: the key guard's sample, and the auditor's "first 64 seed indices", which reads `min(64, J)` | `extended/three_way_keys.py:186`; `scripts/h4_rebaseline.py:2247, 2353` |

So the hard minimums W42-R1 itself places on H4 are these:
- every start;
- seed indices 0 to J - 1, paired across baselines;
- J >= 62 for any gap to resolve.

W42-R1 declares **no power target on H4's J**. Its power target is the held-out test's.

### 2. What H4 runs, and whether its J is tied to W42-R1's need

- **J.** H4's section 7 J row (`prereg/H4_rebaseline.md:267`) sets J as the smallest power of two at or above the J
  that meets three conditions:
  - a true gap of W42-R1's `DELTA_MIN`
  - clears `RESOLVE_Z` coin standard errors with probability `MDL_POWER`
  - at worst-case variance Q = 1 / (J n), with n the complete starts at h = 252 from a lower bound on sessions.

  So **J is tied to W42-R1's constants by H4's own rule, a stricter requirement than W42-R1's floor.** Appendix A
  prints the result (`prereg/H4_rebaseline.md:620-630`; script `docs/plans/scripts/h4/h4_plan.py:135-158`):
  - n = 80749 units;
  - J_needed = 109 at the sessions' lower bound;
  - J_H4 = 128;
  - the floor 62 is met.
- **Why a power of two.** The power of two is declared so that H3-D can cut H4's seeds into disjoint seed sets of any
  power-of-two size (`h4_plan.py:14-15`).
- **The real calendar.** It has 1,034 search sessions (`results/h4_supply.csv.manifest.json`,
  `parameters.preconditions.search_sessions`). That gives 783 complete starts at h = 252 and J_needed = 104. This is
  calendar arithmetic, not an outcome. It is still above 64, and 128 is still the next power of two.
- **Starts.** Every search session, the same set for every baseline, arm and seed (`prereg/H4_rebaseline.md:146-149`).
- **Horizons.** Each measure's own. W = 126 (W42-R1's), with 252 read beside it (`prereg/H4_rebaseline.md:160-162, 263-265`).
- **Arm-runs.** There are four: `off` (deciding), `off_as_walked` (beside), `worse_1` and `missed_0.1`
  (`prereg/H4_rebaseline.md:283-286`; `scripts/h4_rebaseline.py:76-81`). **W42-R1 reads `off` only**
  (`extended/wave42.py:46`; `prereg/H4_rebaseline.md:295-298`).
- **Exact runs.** U1's exact horizons run on every start of both `off` arm-runs, and on every 21st start of the stress
  arms (`prereg/H4_rebaseline.md:266`; `h4_plan.py:102-103`; `scripts/h4_rebaseline.py:71-72, 1629-1647`).
- **Audit sample and batch.** The audit sample is 1 % of units (`prereg/H4_rebaseline.md:270`). A batch is 21 starts
  (l.271).
- **Part cap.** 8 h a part, at most 2 workers, split by disjoint start ranges, **never fewer seeds than J**
  (`prereg/H4_rebaseline.md:272, 644`).
- **Fixed once.** "J is fixed here, before any read, and never extended after one" (`prereg/H4_rebaseline.md:362-363`).
  Section 19 is empty at the pin (l.606-608).

### 3. Is there slack? Which declared numbers decide it

**Starts: none.** `extended/wave42.py:272-273` refuses anything but every calendar session. H4's section 4 declares the
same.

**Seeds: formal slack against W42-R1's code (128 against 62), none against H4's declaration.** Three declared numbers
decide it:
1. **H4's J rule** (`prereg/H4_rebaseline.md:267`; `h4_plan.py:135-148`).
   - J = 64 meets `H4_MIN_SEEDS` and `SAMPLE_SEEDS`, but it fails J_needed (104 to 109).
   - At J = 64 the gap resolved with probability 0.8 at h = 252 is about 0.0127. This is arithmetic on the declared
     constants: (2 + 0.8416) / sqrt(64 x 783). At 128 it is about 0.0090, which matches Appendix A l.628.
   - So at 64 a true gap at `DELTA_MIN` is resolved with less than the declared power.
   - delta\* is the smallest resolved gap. An unresolved small gap pushes delta\* up to a larger resolved gap or to
     the spread fallback. That makes the power gate later searches face **more lenient**.
   - Halving J also widens the relative standard error of the sd estimate behind every headroom-bound limit and H3-D's
     sigma, from 0.0627 (Appendix A l.629) to about 0.089 (1 / sqrt(2 x 63)).
   - **This is a loss of quality, not slack.**
2. **The pairing rule** (`extended/wave42.py:276-277`; H4 section 9's pairing floor, `prereg/H4_rebaseline.md:346-347`).
   - P-14 is written at 128, and P-15 through start 629 at 128.
   - Smaller remaining baselines would mean cutting P-14's and P-15's units down to seed indices 0 to J' - 1.
   - The coin keys depend only on (start, seed index) (`extended/three_way_baseline.py:665, 673-677`), so such a cut
     would plausibly equal a J' run lane for lane.
   - It still needs code changes and an identity check: `expected_j = HA.H4_J` (`scripts/h4_collect.py:181`) and
     `H4_J: int = 128` (`extended/h4_audit.py:51`).
3. **The timing of the choice** (`prereg/H4_rebaseline.md:358-363, 606-608`).
   - J moves delta\* either way, as H4 itself says.
   - P-14's per-unit and per-part summary files, including the variance decomposition
     (`scripts/h4_rebaseline.py:2073`), are on disk, and a review has opened readings files
     (`docs/reviews/BUILD_H4_31c507e_c2_2026-11-26.md:39, 73-75`).
   - A J reduction now would be chosen with one baseline's coin spread visible. **It would look chosen after seeing
     P-14's results.** It is not a defensible pre-outcome choice.

**The near option, J = 104 or 109 (no power of two).** It saves about 15 to 19 % of the remaining work, roughly 13 to
16 h. It breaks the declared power-of-two reason (H3-D's seed sets) and has the same timing problem. **Not recommended.**

**What a shrink would save** (from the logs, at 2 workers). The cost is linear in J: one vendored replay per seed lane,
`extended/three_way_baseline.py:673-677`.

| | measured | source |
|---|---|---|
| P-14, five parts | 7.79, 9.11, 6.21, 6.35, 6.95 h; total 131,073.6 s = **36.4 h** | `results/h4_units_p14_p{1..5}.csv.manifest.json`, `parameters.elapsed_s`; logs `h4-b-p14-p{1..5}.log` "done in" lines |
| P-15, parts 1 to 4 (starts 0 to 629) | 5.00, 7.50, 6.31, 6.31 h; total 90,438.1 s = 25.1 h | `results/h4_units_p15_p{1..4}.csv.manifest.json`, `elapsed_s` |
| P-15, part 5 (630 to ~797) | the last line is batch 6/8 at 17,147.7 s; **no "done" line** | `h4-b-p15-p5.log` (last written 00:13 on 2026-11-27) |

**Remaining work at J = 128 and 2 workers (estimate):**
- P-15: about 13 h.
  - A whole re-run of part 5 is about 6.3 h (Appendix A's crash rule, l.645: "re-run whole ..., never resumed"; P-15
    p4's 168 starts took 6.31 h).
  - The tail, starts 798 to 1033, is about 6.5 h (P-14's starts 770 to 1033 took 6.95 h).
- The naive coin: about 36 to 38 h.
- P-16: about 36 to 38 h.
- **Total: about 85 to 90 h.** J = 64 would save about **43 h**. Not recommended, for the reasons above.

### 4. Other speed levers

**(a) More workers. This is the recommended lever, after one measurement.**
- **The current cap.** `MAX_WORKERS = 2` (`scripts/h4_rebaseline.py:69`). H4 section 7 says "at most 2 workers"
  (`prereg/H4_rebaseline.md:272`), and Appendix A assumes 2.5 GB over 2 workers (l.643). CLAUDE.md l.77 says "at most 2
  workers".
- **Cores.** The machine has 12 physical cores (24 logical).
- **Output is byte-identical by construction.**
  - Batches are submitted and collected in order (`scripts/h4_rebaseline.py:2017-2021`).
  - Each batch's keys depend only on (start, seed index).
  - So the worker count changes no output byte, only `elapsed_s`.
- **`PER_WORKER_GB` does not apply.** `PER_WORKER_GB = 1.2` (`scripts/fasttier_lock.py:128`, used by
  `scripts/fasttier_xdist.py:70`) is the fast test tier's measured xdist worker. It is not an H4-B worker.
- **An H4-B worker's peak is on no record.** `results/h4_0_probe.csv` has `rss_base_mb`, `rss_after_syn_mb` and
  `rss_after_real_mb` all blank.
- **Memory right now is tight.**
  - At 00:42 local, with no H4 process running, 2.9 GB of 15.9 GB was free.
  - The largest working sets were the IDE at about 2.2 GB, Chrome at about 1.8 GB and Discord at about 0.5 GB (process
    listing).
- **Saving, if CPU scaling holds (estimate):**
  - 4 workers would roughly halve the remaining ~85 to 90 h, saving about 40 to 45 h.
  - 3 workers would save about 28 to 30 h.
  - Size parts in multiples of 21 x workers starts, so no worker sits idle.
- **What it needs:**
  - the peak working set of one H4-B worker, measured on the next part;
  - memory freed by closing desktop apps (an operator-side setup item);
  - a re-declared H4 text for the section 7 part-cap row and Appendix A's memory line, plus `MAX_WORKERS`, and a lead
    row for CLAUDE.md's limit;
  - an identity check: units at the new worker count equal to a finished part's units on the same starts.
- **Why it is defensible.** It changes no input and no output, so it is a pre-outcome choice. It weakens no safeguard,
  provided the memory check stands.

**(b) Whether the naive coin's supply dominates time: no.**
- **Schedule supply** (`results/h4_supply.csv`, `year = all` rows, column `trades`): naive coin 208,312; P-15 180,494;
  P-16 146,421; P-14 27,516. The strict rule prunes most of it (column `schedule_overlaps_beside`).
- **Speed per start.** P-15 ran at almost P-14's speed despite 6.6 times the supply:
  - P-15 starts 0 to 629: 25.1 h.
  - P-14 starts 0 to 599: 23.1 h (sum of p1 to p3's `elapsed_s`).
- **What does dominate.** The cost is the per-unit vendored lockstep replay over sessions
  (`extended/three_way_baseline.py:602-626, 673-677`), not the offers.
- **Expectation.** The coin should cost about P-15's, perhaps 10 to 15 % more if routing per offer matters (estimate).
  To check, compare its first batch pair against P-15's typical 5,600 s a pair (`h4-b-p15-p3.log`, `-p4.log`).

**(c) Keeping every part under the 8 h cap.**
- **The P-14 layout broke the cap.** Its p2 (194 starts) took 9.11 h, above `PART_CAP_H`, and the audit found no row
  recording the parts that ran (`docs/audits/AUDIT_E285_E288_2026-11-26.md:122-131`, F-5).
- **The P-15 layout held.** Every 168-start part (four batch pairs) took 6.31 to 7.50 h. The 126-start first part took
  5.00 h.
- **Proposed layout for the coin and P-16 at 2 workers:** 0 to 125, then 126 to 293, 294 to 461, 462 to 629, 630 to
  797, then a tail of 798 to 1033.
  - The tail estimate is about 6.5 h. Late starts have shorter journeys: P-14's 264 starts from 770 took 6.95 h.
  - This is six parts, each inside the cap. It should be recorded in a sizing row before the coin starts.
- **Splitting by parts saves no time.** The gaps between consecutive parts in the logs are a few minutes.

**(d) Splitting by arm: no saving.**
- The runner already supports it (`arms_filter`, `scripts/h4_rebaseline.py:1953, 1983-1985`). The cut rule names start
  ranges only (`prereg/H4_rebaseline.md:644`).
- It does not cut total time.
- Using it to release W42-R1 once the `off` arms finish would breach section 14: "nothing of H4 is read by W42-R1
  until every part is complete" (`prereg/H4_rebaseline.md:426-427`).
  - That is a safeguard. W42-R1 is applied once, and a later oracle or overlap failure on a stress arm would leave
    W42-R1 resting on a failed H4.
- Not recommended.

**(e) The exact runs: cutting them weakens a check.**
- They are a large share of the work. By sessions replayed per start they are roughly 38 % (estimate):
  - each `off` arm-run is 252 + 300 sessions;
  - each stress arm is 252 + 300/21.
- Cutting the as-walked arm's exact runs to every 21st start would save about 17 % (about 6 h a baseline). But they are
  declared (`h4_plan.py:102-103`), and the identity they test is the open blocking finding B-2
  (`docs/reviews/BUILD_H4_31c507e_c2_2026-11-26.md:84-125`). **This weakens a check, so E-207 does not cover it. Not
  recommended.**
- **B-2 does bear on re-runs.** If its treatment becomes "read the exact run's record", the `off` arm's exact runs are
  re-made for every baseline (l.124-125). That is about 18 % of a baseline's work, about 6 to 7 h each (estimate).
- **Settling B-2 before the coin starts** would let the lead choose between two paths:
  - have the coin and P-16 write what the treatment needs, which is a runner change plus an identity check;
  - accept one separate re-make later.

  The review's classification run is light: the audit sample, about 1,300 units a baseline
  (`docs/reviews/BUILD_H4_31c507e_c2_2026-11-26.md:115-118`).

**(f) P-15 part 5.**
- At 00:42 local on 2026-11-27:
  - no `run.lock` was present;
  - no H4 Python process was running;
  - `h4-b-p15-p5.log` ended at batch 6/8 with no "done" line.
- Under Appendix A's crash rule (l.645) the part is re-run whole and the crash is recorded in the part ledger. This is
  an observation. The cause was not investigated.
- The BUILD review says no H4-B part already run needs a re-run for its own findings
  (`docs/reviews/BUILD_H4_31c507e_c2_2026-11-26.md:28, 82`). The one exception is the B-2 treatment in (e).

## What is unknown, and how it could be found

- **An H4-B worker's peak memory.** Sample the worker processes' peak working set during the next part (a light
  listing every few minutes). This decides lever (a).
- **CPU scaling past 2 workers.** On 12 physical cores it is probably near linear, but unmeasured. The identity check in
  (a) measures it as a by-product.
- **The coin's real cost per start.** Its first batch pair will show it.
- **Why P-15 part 5 stopped.** That is the lead's to diagnose under the failure protocol.

## Proposed TASK_QUEUE line

`Q-NEW | H4-B throughput (no size change; J_H4 = 128 and every start kept, see docs/plans/H4_SIZING_SCOUT_2026-11-27.md) | (1) record P-15 p5's stop in the part ledger and re-run it whole; (2) sizing row for naive_coin/p16 at P-15's layout (0-125, then 168-start parts, tail 798-1033); (3) measure one H4-B worker's peak working set on the next part (light); if it and freed memory allow 3-4 workers, re-declare H4 s.7's worker row and Appendix A's memory line, raise MAX_WORKERS, and run a units identity at the new count on a finished part's starts before the coin; (4) settle B-2's treatment (light classification on the audit sample) before naive_coin starts | est. saving ~28-45 h of the ~85-90 h left, no quality cost | wt-verify + lead`
