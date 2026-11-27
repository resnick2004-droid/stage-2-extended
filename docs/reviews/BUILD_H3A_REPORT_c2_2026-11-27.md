# Red-team diff check, cycle 2: H3-A's report and runner, rebuilt after the BLOCK (2026-11-27)

**Target.** The staged, uncommitted change in `wt/wt-h3a` (worktree `%LOCALAPPDATA%\stage2-extended-wt\wt-h3a`, base
`8538664`): `extended/h3a_report.py`, `scripts/h3a_run.py`, `tests/test_h3a_report.py`, `tests/test_h3a_run.py`.

**What it answers.** `docs/reviews/BUILD_H3A_REPORT_2026-11-27.md` (BLOCK: B-1 to B-8, m-1 to m-8).

**Rules read:**
- `prereg/H3_three_way.md`, sections 7, 8, 10, 11 and 15 to 17, and Appendices A and C (through
  `extended/three_way_h3a.py`, which prints them);
- the design note `docs/plans/THREE_WAY_TEST_design.md`, 2.3 to 2.7, 4.2, 6.1 and 6.2;
- E-285 and E-290 in `DECISIONS.md`.

**The brief.** It listed the worker's claims and open points. I tested the claims instead of taking them. The brief
leaned towards deferring A3 and the stress. I give my own view on each point in section 4.

**Method.**
- Both test files were run in the worktree: 32 passed in 74 s.
- The mutants ran in a scratch copy of the index (`git checkout-index` into my session's scratchpad, outside OneDrive,
  no data junctions). The two git-dependent tests were deselected there, because the copy is not a repository.
- Each mutant was one line, run against the test files that exercise it, and the file was restored after each.
- My synthetic checks imported the worktree read-only (`PYTHONDONTWRITEBYTECODE=1`). They drew only the tests' seed in
  the tests' part, as the build's tests do. They wrote nothing.
- No bars were read, `run.lock` was not taken, and the worktree is unchanged (`git status` shows the same 4 staged
  files).

## Verdict: PASS WITH MINORS (stands with readings)

No blocking finding.
- Every blocking finding of the first round is closed in code, or refused in code until the lead's row (B-5's draw
  size, B-6's test J). Every closure in code has a test that fails on a one-line mutant of its decisive line, except
  for the gaps listed below as minors.
- The exact centre of the clipped composite is exact. I checked it by reading, by its brute-force test, and by my own
  Monte Carlo of the runner's draws where the cap binds.
- The runner's first-payout merge equals the unmerged program on six toys (worst difference 1.1e-16).

**Two conditions before A1 runs.** The lead's row must fix the asymmetric twin's kill form (4 (d)) and the A1
set-level centring (4 (e)). Both are a form of the deciding kill. Ruling on them after A1 had run would choose a kill
after a look.

**A3 and A4.** They refuse until the lead's row sets their sizes. Setting `A4_DRAW_J`, or `A3_TEST_J` and
`A3_TIME_CONDITIONS`, is a code edit of `scripts/h3a_run.py`. That diff gets its own check, as a minor's diff.

## 1. The first round's findings: closed, and by what test

The mutants were run against the two test files, 37 in all.

| first round | closed? | the code | the test that fails, or my mutant |
|---|---|---|---|
| **B-1** A1 crashes; the smaller-J report rests on undeclared choices | closed (E-290: deferred to H3-D's text) | `run_a1` never calls `smaller_j`, and its manifest records "not run in H3-A" (`scripts/h3a_run.py` l.822); `smaller_j_rng` is unused | `test_a1_writes_each_history_and_pools_their_sums` asserts the record |
| **B-2 (a)** shift-and-clip bias | closed | a rejection is `lower > theta` (`h3a_report.py` l.585-590), with no clip | C11 (betting against 0) killed; "> 0" is killed by `test_size_counts_count_against_the_centre...` |
| **B-2 (b)** the payout's timing | closed | `_merge_paid` keys the paid bit, and `pay[k]` is read before each merge (`h3a_run.py` l.210-259) | P1 (bit dropped) killed by the A2 fixture's paid-mass check and by `test_the_builds_merge_joins...`; section 3 |
| **B-2 (c)** the clipped composite's centre | closed, exact (section 2) | `exact_composite_centre`, `clipped_indicator_expectation` (l.458-509) | C1 to C5 killed by the brute-force enumeration test; C6 is equivalent (a clip that cannot bind); **C8, C9, C10 survive (m-1 below)** |
| **B-2 (d)** the premise reads another pool | closed | centring on the counted per-seed and per-set pools of both composites (l.436-439) | C12 (P_B's centre from the wrong arm) killed by the premise |
| **B-3** tests draw H3-A's seeds | closed | roles and part are injected (`HistoryTask`); `check_seed_use` refuses H3-A's roles outside a clean run | D2 and D3 killed; **D1 and D4 survive (m-3)** |
| **B-4** the stop's inputs are not tied | closed | `evaluate_laxity_stop` refuses on the declared n, 1080 rows, histories 0 to 19, the per-history n, and pooled = the sum; `pool_counts` is the one pooling | S1 to S8 killed; S9 (20 for `DECLARED_R`) is equivalent |
| **B-5** A4's counts | closed in code; **the slot refuses until `A4_DRAW_J`** (4 (a)) | 426 rates and 60 MDLs derived from the grids, with an assert; P1 and P4 on the disjoint null's replicates through `planted_rates` and `planted_mdl` | `test_a3_and_a4_slices_produce_their_declared_counts`, `test_a4_and_a3_counts_and_summaries` |
| **B-6** A3 | **refused until the lead's row** (4 (b)) | `check_rulings` (l.1021-1028) | `test_workers_are_refused_above_two_and_undeclared_slots_refuse` |
| **B-7** memory | closed in code; the real peak is to be measured by the run, which refuses above the cap | `unit_values` reduces each start; `MemoryGuard` runs after every start and every close of the program; the projection refuses before any draw | the refusal paths are tested; Y1 and Y2 (the projection's and guard's magnitudes) survive (m-5) |
| **B-8** the twin kill | closed in code; **its form is the lead's** (4 (d)) | `check_symmetry`, deciding on the antithetic per-seed pool | K1 (one-sided) and K2 (not deciding) killed; K3 (refusal ignored) killed |
| m-1 (R1, `>=`) | carried, equivalent in practice | -- | -- |
| m-2 (the stress's size) | not run; recorded | `STRESS_SIZE = None` | 4 (c) |
| m-3 (the disjoint keys) | closed | `check_disjoint_sets`; each set's own sampled guard; `K.disjoint` | `test_the_disjoint_sets_are_checked_exactly`; K5 killed |
| m-4 (workers, OMP) | workers closed; OMP recorded, not refused (m-7 below) | `check_workers` | `test_workers_are_refused...` |
| m-5 (inputs' manifests) | closed | `verify_inputs` | `test_verify_inputs_refuses...` (passes in the worktree) |
| m-6 (fill failures of every arm) | closed | `fill_summary` on every arm | the A1 and A2 tests assert the arms |
| m-7 (EB's range term) | closed | `eb_range_term` beside every EB row | `test_the_eb_range_term_is_printed...` |
| m-8 (premises written before refusing) | closed for premise, key-guard and range refusals; **not for a worker's memory refusal (m-4 below)** | `_Part.take` | `test_a_planted_asymmetric_twin_stops_the_part...` |

**Equivalent survivors, no action:**
- C6: the linear branch only runs where the clip cannot bind.
- P3: `exact_moments` never reads `ffail`.
- S9: `DECLARED_R` for A1 and A2 is 20.
- K4: `_finish`'s flag is redundant with `take`'s own check.

**Survivors that are defence in depth:**
- R1 and R2 (`_premises_hold` disabled): a part with a failed premise writes no pooled file, so the report refuses on
  a missing input anyway. Listed under m-6.

## 2. Is the clipped composite's centre exact? Yes, and the independence it needs is true of the runner's draws

**The two linear dimensions.**
- `P_B`: its range is [0, 1] (`a = 0`, `r = 1`) and its caps are [0, 1].
- `sessions_saved_to_payout`: its range is [0, 64] (`session_count`, `r = W + 1`) and its caps are [0, 64].
- So `Dimension.values` refuses any value outside [a, a + r]. The scaled mean of any seed set lies in [0, 1], and
  `scaled`'s clip never binds.
- E[scaled(Phi)] is then (mean of the per-start expectations - lo) / (hi - lo). This is exact, because every set
  holds the same seeds at every start (`clipped_dimension_expectation` l.491-492).
- By reading, the per-unit value is (h + 1) - `days_to_first_payout`, which lies in [0, 63]. The exact side,
  sum over k of P(first payout at k) x (h + 1 - k), is the same definition. The test for that formula is weak
  (m-2 below).

**The indicator, `paid_by_63`** (cap 0.6, which binds).
- The seed set's count is K = sum over starts t of Binomial(m, p_t). The exact law of K is the convolution, and the
  clipped expectation follows from it (l.458-480).
- The brute-force enumeration test fails on C1 to C5.

**Independence given H.** It holds by the key layout. Every coin key and every enforce key carries
(part, history, seed index, start), choice 3, and `_carries_start` refuses one that does not (`three_way_keys.py`
l.52-55 and l.166-170). Each unit's uniforms therefore come from its own Philox key:
- two units, at different starts or with different seed indices, never read one uniform;
- the S1 history is the only common input, and the centre is conditional on it;
- A2's two arms share each unit's uniforms, but the centre is E[C(f)] - E[C(b)] by linearity, so it needs
  independence only within an arm, across units.

The caveat is the pseudo-random generator itself, which the key guard's tripwire samples.

**My Monte Carlo** (`centre_check.py`, scratch).
- The toy: 9 race trades over sessions 0 to 16, starts 0 to 5, 20000 seeds, the runner's own `unit_values` and
  `exact_arm`. Here p_t runs from 0.55 to 0.71.
- At m = 1, the cap binds on 60 % of seed sets:
  - exact clipped centre 0.88715;
  - Monte Carlo 0.88705 +- 0.00126 (z = -0.08);
  - clip of the mean 1.0.
- At m = 2: exact 0.92936, Monte Carlo 0.92849 +- 0.00123 (z = -0.71).
- At m = 5: exact 0.96331, Monte Carlo 0.96335 +- 0.00109 (z = +0.03).
- Each start's p_t from the program matches its Monte Carlo share.
- The correlation of one seed's indicator across starts 0 and 1 is 0.013, and across starts 0 and 2 it is -0.003.
  The standard error at n = 20000 is 0.007, so neither is distinguishable from zero.

## 3. Is the runner's first-payout merge equal to the unmerged program? Yes

**By reading.**
- `first_pay` is written only in `_close_cash` (`three_way_journey.py` l.555), and only where `first_pay < 0`. It is
  read nowhere else in the dynamics.
- `exact_moments` records `pay[k]`, the mass whose `first_pay` became k at close k, before the merge.
- So the only fact about `first_pay` that a merge must keep is the paid bit, and `_merge_paid` adds that bit to the
  build's own key. `ahead` (P_B) and `first_pass` are already in the key.
- `_merge_paid` copies `_merge`'s body. The build files are frozen at `4c07026` by the precondition gate, so the two
  cannot drift apart.

**By my check** (`merge_check.py`, scratch; no edit of any build file).
- I compared `exact_moments` with `_merge_paid` against `merge = identity` on six deterministic toys:
  - race trades at payout lags 1 and 2;
  - A2's `TOY_RULES_EXACT`;
  - R-10 walks every second trade;
  - costs with a daily limit;
  - sessions with gaps and two trades a session.
- The worst difference over the three moments is 1.1e-16, and P_B equals `J.expect`'s to 0.
- On those toys the build's `_merge` also equals the unmerged program, so the worker's no-merge oracle cannot see
  B-2 (b)'s defect on its own toy (m-2). The defect is real on A2's settings: mutant P1 trips the A2 fixture's
  paid-mass check on `TINY_X`.

## 4. The worker's open points (the lead's rulings): my view

**(a) A4's seeds a draw, J' = 100. I agree, by a row before any A4 slot.**
- This is not the smaller-J report's case. That report had no declared delta and no level at all.
- A4's J is pinned down by declared values:
  - Appendix C fixes `SEEDS` = 10 000 a history;
  - the note's 4.2 requires P2's truth from "a pool of at least a hundred times J", which bounds J at 100;
  - `J_PRIME` = 100 is the only seed-set size Appendix C names;
  - section 8's 426 and 60 hold at any J.
- J' also makes A4's power the power of the very procedure whose size A1 and A2 check.
- Record it as a reading, chosen before any outcome. It is not covered by l.143's wording, which speaks of the size
  tests.
- Print beside the MDLs that they hold at J = 100 only. H3-D's J is H3-D's.
- If the lead reads E-290's "declared" strictly, the consistent alternative is to defer A4 to H3-D's text as well.

**(b) A3. I agree with deferring it to H3-D's text.**
- FPR_hist is defined at "the test's J" and "times the time conditions' indicator" (the note's 2.7). Both are H3-D's
  inputs: J and m (section 7), and n_min (CHARTER 3.9's row).
- A rate at J' with no time condition is not the declared quantity. Printed under that name, it would be a number that
  means something else.
- The row should record that:
  - section 8's 6 rates move to H3-D's text, counted there;
  - A3's role seed stays drawn by nothing until then;
  - when H3-D's text runs a stylised S1 history null, it either uses A3's role seed in its declared role or says why it uses
    H3-D2's history-null role seed, never both for one thing.

**(c) The stress's size. Either is acceptable.**
- It is beside and decides nothing.
- If it is set rather than deferred, the row fixes (histories, seeds) before A1 runs, for example history 0 at J'
  seeds. That is a choice made before any outcome.
- If it is deferred, the row records that section 8's 15 runs are H3-D's text's.
- The code supports both. `run_stress` is tested at 15 runs, and A1's manifest records "not run".

**(d) The asymmetric twin as a sign test at `CENTRING_Z`. Acceptable as the deciding form, with one addition.**
- The test is valid under the twin's exactness alone. Delta is symmetric given H, so the positives among the nonzero
  replicates are Binomial(n, 1/2), with no distributional assumption.
- At |z| > 4 its false rate is about 6.3e-5 a check.
- It detects a shift of P(Delta > 0) from one half of about 4 / (2 sqrt(n)), which is 0.02 at n = 10 000 seeds.
- It cannot see a twin whose Delta has its signs balanced but its magnitudes skewed. The m-8 defect (an outcome
  reversed, p to 1 - p) moves the mean, and the centring test already catches that.
- I recommend adding the deterministic check the first round named, deciding and at no cost: on the guard's sampled
  keys, every twin uniform equals 1 minus the base's, bit for bit. The generator's twin is exact by construction
  (`three_way_fastkeys`, (2i + 1) 2^-53 and its complement), so this check can fail only on a construction defect,
  which is exactly what the kill is for.
- The row records both forms before A1.

**(e) Set-level centring in A1. Acceptable as a reading of "a pool not centred"** (section 11 names no pool). Record
its false-kill rate, computed rather than typed:
- 160 deciding checks are normal at |z| > 4: A1's per-seed checks, both symmetry checks, and A2's per-seed checks.
- 120 are set-level, on 100 sets, where the statistic is closer to a t with 99 degrees of freedom: P(|t| > 4) is
  about 1.2e-4, twice the normal's.
- That gives a union bound of 2.5 % over A1 and A2, of which A1's set-level checks add 1.0 point. Without them the
  bound is 1.5 %.
- A false kill costs a diagnosis under the failure protocol, not a wrong result, so the extension weakens no
  safeguard.

**For `P_B` the set-level check adds no information.**
- The sets partition all M seed columns, and `P_B`'s clip never binds. So the mean of the set estimates equals the
  per-seed pool's mean exactly, and the set-level check tests the same mean with a noisier standard error.
- I would make the set-level check deciding for the clipped composite only, and keep `P_B`'s beside. A2's set-level
  checks are B-2 (d)'s remedy and stay deciding.

## 5. Minor findings (each fixed and checked by its diff, no new round)

**m-1 (minor): the set and seed centres can be swapped and no test sees it.**
- **Where:** `extended/h3a_report.py` l.585-592. The test is `tests/test_h3a_report.py` l.369, where
  `cen = {"p_b": {"set": 0.45, "seed": 0.45}, "toy_composite": {"set": 0.225, "seed": 0.225}}` has set = seed.
- **Evidence:** three mutants survive the full test files:
  - C8, EB compared with `th_set`;
  - C9, 2.2 (a) compared with `th_rep`;
  - C10, the seed pool centred at `th_set`.
- The current lines are right by reading.
- **Failure it allows:** a later edit that reads the m = 1 centre for the 2.2 (a) bound, or the J' centre for EB or
  betting, passes every test. The clipped composite's A2 counts would then measure something other than size. On my
  toy the two centres differ by more than 0.07 (section 2).
- **Remedy:** a `size_counts` test with set different from seed, where each bound's count moves only with its own
  centre.

**m-2 (minor): `sessions_saved_to_payout`'s exact formula has no independent oracle.**
- **Where:** `scripts/h3a_run.py` l.257; the test is `tests/test_h3a_run.py` l.177-194.
- **Evidence:** mutant P2, `(horizon - k)` for `(horizon + 1 - k)`, survives.
  - The no-merge oracle uses the same formula.
  - The Monte Carlo tolerance at 20 000 units, 4 SE of a value with sd near 25, is wider than the shift, which equals
    P(paid).
  - The same toy cannot see B-2 (b) either (section 3).
- **Failure it allows:** an off-by-one centre for the toy composite's 0.2-weight dimension passes every test.
- **Remedy:**
  - With `merge` = identity, take the program's final lanes. Compute sum of w x (h + 1 - days(first_pay)) by
    `days_to_first_payout`'s rule, and hold `exact_moments` equal to it.
  - Pick a toy where `J._merge` differs from the unmerged program, so the oracle sees the paid bit too.

**m-3 (minor): two of `check_seed_use`'s refusals are untested.**
- **Where:** `scripts/h3a_run.py` l.142-149.
- **Evidence:** two mutants survive:
  - D1: H3-A's role at another part's id accepted;
  - D4: a foreign role is treated as declared. The test at `tests/test_h3a_run.py` l.297-298 still passes, because it
    is refused on the clean-run branch, not on the role branch.
- The build's `ROLE_USE` refuses most of these cases behind it.
- **Remedy:** with `S2X_CLEAN_RUN` monkeypatched set, test each refusal and match its message.

**m-4 (minor): a memory refusal inside a worker is not written before the part stops** (the first round's m-8 class).
- **Where:** `MemoryGuard.check` (l.164-168) raises `MemoryRefused` inside `unit_values` and `exact_arm`. This is not
  a `ValueError`, so `a1_history` and the other workers do not catch it. It propagates through `_execute` (l.704)
  before `take`.
- A `BoundRefused` whose message does not start with "REFUSED" (`Dimension.values`' "a blank or infinite per-unit
  value") is re-raised the same way.
- The module's docstring (l.31-33) says a memory breach "writes the part's premise table first".
- **Failure it allows:** a late memory breach leaves only the log. The per-history files already written survive.
- **Remedy:** in the worker, catch `MemoryRefused` and return a refused record carrying the peak. Or write the
  premises in `_execute`'s handler before re-raising.

**m-5 (minor): the parent process sits outside the memory cap, and the cap's magnitudes are untested.**
- **Where:** `_projection_check` (l.780-786) and `MemoryGuard`.
- **The parent:** with `--workers 2` there are three processes. The note's 6.2 cap is "under 2.5 GB in all", but the
  parent's base and records are outside both workers' 1192 MiB.
- **The magnitudes:** Y1 (the projection's kept bytes cut sixteenfold) and Y2 (the guard's cap times 100) survive.
- By my arithmetic each worker holds about 0.2 GB beyond its base, so the cap does not bind. That is a reading, not a
  measurement.
- **Remedy:**
  - record the parent's peak in each manifest, and refuse when parent + 2 x worker peak exceeds 2.5 GB;
  - test the guard at a cap just below and just above a known allocation.

**m-6 (minor): every slot must run from one commit, and the run lines do not say so.**
- **Where:** `verify_inputs` (`h3a_report.py` l.808-809) refuses inputs from two commits, but the compute slots' run
  lines (`h3a_run.py` l.6-11) carry no `--commit`.
- **Failure it allows:** if master moves between A1's and A2's slots, the stop's report refuses only at the end,
  after both compute slots have run.
- **The survivors:** R1 and R2 (premise tables unread) are covered behind by the missing pooled file.
- **Remedy:**
  - name the commit in each slot's line, or have each compute slot refuse unless the earlier slots' manifests carry
    HEAD;
  - test `_premises_hold` on a table holding one failed deciding premise.

**m-7 (minor): `OMP_NUM_THREADS` is recorded but not refused** (the first round's m-4, half closed).
- The docstring runs at 1, and CLAUDE.md's limit is 2.
- **Remedy:** refuse unless it is set and at most 2.

**m-8 (minor): A2's slot now runs the exact program four times a start pair, which E-285 did not size.**
- `exact_arm` runs once for each arm, and `R.exact_centres` runs once for each arm as a cross-check.
- The paid bit can double the program's states.
- E-285's 5.5 h for A2 did not include this.
- **Remedy:** none in code (the cross-check is worth its cost). Let the lead's row note it; the 8-hour part cap and
  the cut rule apply.

**m-9 (minor, a reading to print): without time conditions, P4 is P1 at a rescaled size.**
- **Where:** `h3a_run.py` l.601: `size = d x mean(1 + a rho_t)`.
- With no time condition in H3-A, a plant on the composite's scale moves every bound only through its mean. So P4's
  lines on `P_B` under 2.2 (a) and EB are P1's at that size, and they add only the toy composite and the betting
  bound.
- Not wrong, but the report should say so beside P4's 270 rates and 54 MDLs, so that they are not read as a test of
  regime variation.
- Also print that P1's and P4's null is the disjoint same-design null, which is the note's "null terms" read as the
  2.3 (b) pool.

**m-10 (minor): two of the note's 2.6 premises are absent or beside.**
- The disjoint pool's symmetry is beside (l.391), and serial dependence in seed order is absent. Section 11's kill
  list governs and names only the asymmetric twin, so this is a reading.
- **Remedy:** print a lag-1 autocorrelation of each per-seed pool beside. It is free, and it is the premise that would
  show a key defect between adjacent seed indices.

**m-11 (minor, outside this diff, for H3-D's text): the smaller-J report's key has already been read by a test.**
- `tests/test_three_way_keys.py` l.324-325, a build test at `4c07026`, draws 4 uniforms from `smaller_j_rng()`, the
  declared key `SMALLER_J_REPORT`.
- With the report deferred, H3-D's text should take its own key and record that this one's first draws were read by a
  test, which printed nothing.

## 6. What I tried that found nothing

- **The stop.** `stop_on_pooled`, `score_pooled_cell` and `one_sided_cp_lower` are unchanged in substance (one-sided
  at 0.05 / 54, 54 keys). `evaluate_laxity_stop`'s new refusals are all mutation-tested (S1 to S8).
  `build_final_report` passes no override of the declared n or histories in `main`.
- **Counts derived.**
  - 36, 18, 54, 720, 360 and 1080 come from the tuples.
  - The declared n is R x floor(seeds a side / J'), giving 2000, 1000 and 2000, with R held equal to
    `three_way_arith.parts()` by a test.
  - 426 and 60 come from the grids, with an assert; A3's 6 and the stress's 15 from `R.stress_cells`.
  - No count is typed without its derivation beside it.
- **Seeds.**
  - No literal of the block appears in the four files.
  - Every draw goes through `S.issue` by role.
  - The per-part roles match section 15's table.
  - P4's sign key is `plant` in part A4 (allowed, and distinct from `SMALLER_J_REPORT`'s part A1).
  - A3 draws only A3's role seed.
  - The tests draw only the tests' seed in the tests' part.
  - `run_stress` checks its roles.
- **Late binding.** The premise lambdas are called inside their own loop iteration (`_guarded`), so no closure reads
  a later pool.
- **Look-ahead and leakage.** None is possible here: no bars, no dates (S1 only), no held-out read, no confirmation
  window. The preconditions gate is unchanged.
- **The antithetic and disjoint pairing.**
  - Each seed's base is paired with its own twin.
  - The disjoint halves give 50 sets each with no straddle.
  - The disjoint variance guard reads the single arm's per-seed variance.
  - The key guards are per set, and checked disjoint.
- **A2's cross-check.** `exact_moments`' P_B is held equal to `three_way_runner.exact_centres` within 1e-9 on every
  start, before any count.

## 7. What I could not check, and the experiment that would settle each

- **The real per-worker peak** (B-7, m-5). Run `a1_history` and `a2_history` under the tests' seed in the tests' part
  at M = 1000, all 120 starts, h = 63, one worker, and read `mem_peak_mb`. This is heavy by CLAUDE.md's measure: the
  engine on about 0.5 million paths, some minutes a history. It is not run while another job holds the lock. The run
  itself refuses above the cap, so this is sizing, not safety.
- **How far apart A2's two centres are on its declared toys** (the size of m-1's risk). It needs A2's exact program on
  the declared S1 at `S1_PARAMS_EXACT`, which is light to moderate, but it reads H3-A's declared histories role. Run
  it under the tests' seed instead, at the declared parameters.
- **Which trade laws A2's declared schedules hold.** Section 11 says "barrier and R-10 trades", and `A2_PAIR`'s
  comment says the walks are excluded. The exact program handles walks (`walk_law`), so exactness does not depend on
  the answer. I did not settle it.
> Seeds named by role (literals replaced by the lead, 2026-11-27, for the seed-block guard).
