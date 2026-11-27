# Red-team diff check: H3-A's report and run code, before H3-A runs (2026-11-27)

**Target.** `extended/h3a_report.py`, `scripts/h3a_run.py`, `scripts/h3_probe.py` and their tests
(`tests/test_h3a_report.py`, `tests/test_h3a_run.py`) on master `8538664`. They landed in E-282 (merge `7d1d3b9`, report
and probe) and `d85ba25` (runner). **Rules read:** E-279, E-282, E-285 in `DECISIONS.md`; `prereg/H3_three_way.md`
sections 7, 8, 9, 10, 11, 14, 15, 16, 17 and Appendices A and C; the design note `docs/plans/THREE_WAY_TEST_design.md`,
sections 2.1 to 2.7, 4.2, 4.3 and 6.1. The brief listed the declared counts. I checked each one against E-279 and
section 8 and took nothing else from the brief. It hinted at no conclusion.

## Verdict: BLOCK. H3-A may not run on the current code.

The report's laxity stop (`h3a_report.evaluate_laxity_stop`) is right. It decides on exactly the 54 declared pooled
cells, one-sided at 1 - 0.05 / 54. The per-history counts and `size_label` sit beside it and decide nothing. 14 of my
15 one-line mutants of it were killed, and the one survivor is equivalent in practice.

The code that **produces** what the stop reads, and the rest of H3-A, is not ready:
- the A1 slot crashes at its end;
- A2's "exact-centred" null is not exactly centred, so 18 of the stop's 54 counts measure something other than size;
- the runner's unit tests draw H3-A's own declared seeds in H3-A's declared parts;
- A3 and A4 produce neither the declared counts nor the declared readings;
- A1 and A2 breach the declared memory cap.

Some remedies need a lead's row before the run (B-1's placeholder deltas, B-6's A3 construction, B-8's twin test, and
possibly B-2 (c)). None needs H3 itself re-declared, except possibly B-2 (c) (see there).

---

## Blocking findings

### B-1 (blocking): the A1 slot crashes after all its compute, and its smaller-J report rests on undeclared choices

- **Where:** `scripts/h3a_run.py:522-531` (`run_a1`, `run_smaller_j=True` on the `--part A1` path, l.687).
- **Evidence:** `three_way_stats.smaller_j(delta, sigma, alpha, power, J_grid, rng, reps, draw=None)`
  (`extended/three_way_stats.py:326`) has no default for `J_grid` or `reps`. The runner calls it with
  `delta=, sigma=, alpha=, power=, rng=` only. Binding that call to the signature raises
  `TypeError: missing a required argument: 'J_grid'` (my check 2).
- **Why it was not caught:** the only test of `run_a1` passes `run_smaller_j=False` (`tests/test_h3a_run.py:27`).
- **Failure it allows:** the A1 slot runs all 20 histories (hours under `run.lock`), then raises before either
  `write_result` call. Nothing is written, and the failure protocol is triggered by a build defect.
- **Undeclared choices in the same call:**
  - `delta=0.01` is typed in. Section 7 says H3-A uses no delta\*. Appendix C declares no placeholder delta for the
    smaller-J report. The note's 6.1 says only "at placeholder values of delta".
  - `alpha=REP.LEVELS[0]` uses one level of three.
  - `sigma` is the mean over histories of the antithetic pool's per-seed sd. Section 7 asks for "each pool's own sd",
    and the disjoint pool and A2 are not used.
- **Remedy:**
  - Pass `J_grid=ST.SMALLER_J_GRID` and `reps=ST.SMALLER_J_DRAWS`.
  - Have the lead's row fix the placeholder deltas, the levels and which pools' sd before the run. `SIZE_GRID` is the
    one declared grid of sizes.
  - Keep the declared order: one generator, `P_B` then `TOY_COMPOSITE`.
  - Add a test that runs `run_smaller_j=True` on a tiny input under the tests' seed (see B-3).

### B-2 (blocking): A2's "exact-centred" null is not exactly centred, so its 18 pooled counts are not size counts

- **Where:** `scripts/h3a_run.py:313-328` (centring), `:80-112` (`exact_dim_expectations`), `:325-326` (premise).
- **(a) Shift-and-clip bias.** The runner centres per unit: `Xf_c = clip(Xf - max(theta, 0), a, a + r)` and
  `Xb_c = clip(Xb + min(theta, 0), a, a + r)`.
  - P_B's per-unit value lies on {0, 1/3, 2/3, 1}. So E[clip(X - theta, 0, 1)] = E[X] - theta + theta P(X < theta).
  - The centred difference therefore has mean +theta P(Xf < theta) when theta > 0, and -|theta| P(Xb < |theta|) when
    theta < 0. It is not zero.
  - Arithmetic (my check 4, a hypothetical P(X = 0) = 0.6): at theta = 0.05 the bias is 0.03. The Hoeffding margin at
    J' = 100 and |E| = 120 is sqrt(2 ln 20 / 12000) = 0.022.
  - **Failure:** on a pair with theta > 0 the bound rejects far above its level, and the stop fires on a correct
    bound. With theta < 0 the bias hides a real laxity. Either way the A2 counts are not the bound's size.
- **(b) The exact program does not track the payout's timing.**
  - `exact_dim_expectations` reads `L.first_pay` after `J._merge`.
  - The merge key (`extended/three_way_journey.py:649`, `_state_key`) holds phase, balance, floor, peak, age, wins,
    cash, within-budget, `ahead`, `first_pass > 0` and `pend`. It does not hold `first_pay`.
  - Merged states with different first-payout sessions keep the first one's. So the theta of `sessions_saved_to_payout`
    (and possibly of `paid_by_63`) is not exact.
  - `J.expect`, the declared exact program, returns only `p_b`, `passed` and `fill_failures` for this reason.
  - **Failure:** the toy composite's centre is wrong by an unknown amount, and its 9 A2 counts are not size counts.
- **(c) The clipped composite's centre is not the clip of the per-dimension centres.**
  - `composite_per_seed_diffs` (l.115-129) clips each seed's normalised mean (m = 1).
  - `ST.mcdiarmid` clips the set's mean.
  - Centring each dimension's mean does not centre either form wherever a cap binds (`paid_by_63`'s `hi = 0.6`; the
    note's N-11).
  - The declaration chose both composites for the exact-centred null (section 8). For the clipped one, the note's 2.4
    offers only the approximate centring ("a pool of at least a hundred times J ... labelled approximate").
- **(d) The premise check reads another pool.** `prem_pb` checks the **raw, unclipped** centred P_B difference
  (l.325). The counts use the clipped `Xf_c`, `Xb_c`. The toy composite's A2 pool has no premise check at all. The
  oracle reads something other than the output it vouches for.
- **Remedy:**
  - Count a rejection as `lower(raw) > theta`. This is the one-sided size event P(LB > E[Delta]) <= alpha. Hoeffding
    and McDiarmid are shift-invariant, so this matches centring without any clip.
  - Take P_B's theta from `three_way_runner.exact_centres` (`J.expect`), not a re-implementation.
  - For the toy composite, either extend the exact program's state with `first_pay` and show that no cap binds on A2's
    toys, or label that null approximate as 2.4 does. If the declared word "exact" cannot hold for the clipped
    composite, the lead rules under a new row.
  - Run the centring premise on the pools that are counted, for both composites.

### B-3 (blocking): the runner's unit tests draw H3-A's declared seeds in H3-A's declared parts

- **Where:** `tests/test_h3a_run.py:25, 35, 58, 61`, which call `run_a1`, `run_a2`, `run_a3_slice` and `run_a4_slice`.
  These hard-wire `S.issue("h3a_histories")`, `S.issue("h3a_coins")` and `S.issue("h3a3_history_null")` with
  `S.PARTS["A1"...]` (`scripts/h3a_run.py:225-226, 293-294, 340, 365-366, 467, 503-505`).
- **Evidence:** section 15 says "This build's tests use the tests' seed ... never in a declared run's part". Neither
  `ROLE_USE` nor `Plan` refuses a design-check role seed drawn from a test, only the tests' seed outside its part.
- The test's history 0 and its coin keys are the real run's history 0 keys. The fields are seed, part, history, seed
  index, start and moment. Wherever a moment coincides, the test reads the same uniforms the declared A1, A2, A3 and A4
  runs will read.
- **Failure it allows:** a seed used in two roles (test and declared run). Outcomes on the declared run's coin field are
  visible to whoever runs or edits the test before H3-A. Today the test asserts only shapes and prints nothing. The
  rule is broken all the same, and nothing stops a later test from printing a rate.
- **Remedy:**
  - The four per-history workers take the role seeds and part ids as arguments. `main()` alone passes the issued H3-A
    roles. The tests pass `S.issue("tests")` with `S.PARTS["tests"]`.
  - Optionally, the runner refuses the H3-A roles unless `S2X_CLEAN_RUN` is set.
  - The lead records under a row whether H3-A's seeds stand. No outcome was stored or printed. Every fast-tier run since
    `d85ba25` drew them.

### B-4 (blocking): the stop's inputs are not tied to the declared n or to the per-history sums, and the runner's pooling is untested

- **Where:** `extended/h3a_report.py:200-258`; `scripts/h3a_run.py:481-500, 565-581, 636-669`;
  `tests/test_h3a_run.py:21-50`.
- **Evidence (my checks 1c and 1d):**
  - `evaluate_laxity_stop` returns `PASS_NO_LAXITY` on 54 pooled cells of n = 5 each, beside per-history cells whose
    sums disagree with them.
  - It also returns `PASS_NO_LAXITY` with **no** per-history rows.
  - `build_final_report` reads the per-history files only `if p.is_file()` (l.651).
- **The declared pooled n is arithmetic**, from R = 20, `SEEDS`, `DISJOINT` and `J_PRIME`:
  - 20 x floor(10000 / 100) = 2000 for the antithetic and exact-centred cells;
  - 20 x floor(5000 / 100) = 1000 for the disjoint cells.
- **The runner's test** asserts only row counts, the stress count, role names and that the verdict is one of two
  strings. By inspection, every one-line mutant of the pooling that keeps the row counts survives:
  - `acc[1] += n_s` to `acc[1] = n_s` (a pooled n of one history: 100 instead of 2000);
  - `acc[0] += rej` to `acc[0] = rej`;
  - `eb_lower(d_pb, ...)` to `eb_lower(d_toy, ...)` in `eval_size_sets`;
  - incrementing `("p_b", "eb", lv)` where `("p_b", "betting", lv)` belongs;
  - `half = M // 2` to `M // 4`;
  - `if not v["ok"]` to `if False`.
- **Failure it allows:** pooling one history's n instead of 20 cuts the stop's power about twentyfold, so a real
  laxity passes. No test would see it.
- **Remedy:**
  - `evaluate_laxity_stop` (or `build_final_report`) refuses unless:
    - each pooled n equals its declared value, computed from `three_way_h3a`'s inputs and R;
    - exactly 1080 per-history rows are present (720 A1, 360 A2), one per (cell, history), histories 0 to 19;
    - each pooled count equals the sum of its 20 per-history rejections and n.
  - Add a runner test with R = 2 histories and known planted counts, run under the tests' seed per B-3, that kills the
    six mutants above.
  - Verify each input's manifest (`verify_result`, `git_dirty: false`, one commit). See m-5.

### B-5 (blocking): A4 produces 228 of the declared 426 pass rates, none of the 60 MDLs, and plants without a null term

- **Where:** `scripts/h3a_run.py:363-441`, `613-633`.
- **Counts.** Only `P_B` is run. There is no `TOY_COMPOSITE` matrix in A4, against section 8's P2 x 2 composites, P3 x 2
  and P4 x 2. Per history:
  - P1: 5 x 3 levels x 2 bounds = 30 (the betting column is set to -1);
  - P2: 3 x 3 x 3 = 27, not 54;
  - P3: 4 x 3 x 3 = 36, not 72;
  - P4: 5 x 3 x 3 x 3 = 135, not 270;
  - total 228, not 426.
  - No conjoint MDL is computed anywhere (`conjoint_mdl_grid`, `planted_mdl`), against section 8's 6 + 54 = 60. No
    rate is pooled over the 10 histories, and the `report` part reads no A4 file.
- **P1 and P4 have no null term.**
  - The plant is `xf = clip(x_base + delta, 0, 1)` against `x_base` on **the same coin field** (l.379-380, 428-430).
    So `d = (xf - x_base).mean(axis=0)` is delta minus clip loss, with almost no spread.
  - The note's 4.2 says P1 is "the null terms plus delta". The null terms are a same-design or paired pool's
    replicates, and `ST.planted_mdl` and `ST.planted_rates` exist for this. Both go unused.
  - The per-unit clip at 1 also makes P1 non-linear, the case m-12 refuses for the linear form.
- **Failure it allows:** EB and betting see near-zero variance, so their pass rates and MDLs are overstated. Those are
  the power figures H3-A reports to H3-D's text.
- **P2 and P3:** the "true delta" (the note's 4.2: "from the DP toys or a pool of at least a hundred times J") is not
  computed; only the same pool's mean is.
- **Remedy:**
  - Build P1 and P4 on the A1 null pool's replicates, through `ST.planted_rates` and `ST.planted_mdl`
    (`LINEAR_PLANT_BOUNDS` only for the linear form).
  - Run both composites wherever section 8 counts them.
  - Compute and write the 60 MDLs.
  - Derive the 426 from the declared grids in code and assert it.
  - Pool the per-history rates in the `report` part.

### B-6 (blocking): A3 is not the declared history null and produces 0 of its 6 rates

- **Where:** `scripts/h3a_run.py:337-360`, `592-610`.
- **What it does instead:**
  - It runs only `P_B`. The toy composite's 3 rates are missing.
  - It writes per-history 0/1 rejections for three bounds and never forms a rate over the 200 histories.
  - It gives no `fpr_hist` with the pair's label.
  - It applies the bound at J = M = 2000 on each history.
- **What the note's 2.7 declares** (carried by section 8, "the whole rule at its bound by the composite's form"):
  - a pool of M seeds per history estimates theta-hat, sigma-hat and the per-year and per-regime differences;
  - the pass probability **at the test's J** comes from 2.5's formula, times the time conditions' indicator;
  - the shortcut's error is checked against `SHORTCUT_HISTORIES` run in full at the test's J (Appendix C).
- `SHORTCUT_HISTORIES` is never read.
- **Failure it allows:** with J = 2000 standing in for the test's J and no time conditions, the printed false-pass rate
  is not FPR_hist.
- **Remedy:**
  - Implement 2.7's construction for both composites.
  - The lead's row names the "test's J" for H3-A (J' or another), and whether S1's time conditions apply.
  - Run the shortcut subset.
  - Report the 6 rates with `fpr_hist` and its label in the `report` part.

### B-7 (blocking): A1 and A2 breach the declared memory cap, and no part measures or refuses it

- **Where:** `scripts/h3a_run.py:235-236`, `304-305`. Both `Records` lists are kept to the end of the worker.
  `R.run` returns one `Records` per start, each holding `rel` of shape (M, h + 1) float64
  (`three_way_journey.py:628`) and a Python list per lane (`arrivals`).
- **Arithmetic** at M = 10000, h = 63, 120 starts:
  - `rel` alone is 10000 x 64 x 8 B x 120 = 0.61 GB per arm. Two arms per worker is 1.23 GB.
  - The 2.4 million per-lane lists and the small arrays add about 0.25 GB.
  - That is about 1.5 GB per worker before the process base, about 3 GB over 2 workers.
  - The declared cap is 2.5 GB in all, 1.25 GB a worker (the note's 6.2; Appendix A).
- **Why E-285 did not see it:** its "fits memory" rests on `scripts/h3_probe.py`'s model,
  `M x (lane bytes + key bytes) + walk chunk + guard` per worker. That model holds one start's lanes, not 120 starts'
  retained records.
- The runner records no peak, and the run-lock line in its docstring states `--mem-gb 1.0`.
- **Failure it allows:** the slot runs about twice over its declared memory on a shared 16 GB machine. That risks a
  crash after hours, or swapping that voids the slot's time sizing. The lock's arithmetic, which admits other jobs, is
  also wrong.
- **Remedy:**
  - Reduce each start's `Records` to its value matrices as it is produced, so `rel` and `arrivals` are dropped per start.
  - Record `procmem.working_set_mb(peak=True)` per worker in the manifest, and refuse (abort) above 1.25 GB.
  - Re-measure with the experiment below before the lead re-sizes the slots.

### B-8 (blocking): a declared kill cannot fire, because "an asymmetric twin" is not checked

- **Where:** `scripts/h3a_run.py:262-275` and `471-479`, against section 11 ("a pool not centred ..., an asymmetric
  twin, a term out of range, a key guard refusal") and the note's 2.6 (premises: mean, symmetry for (a) and (b), no
  serial dependence in seed order, terms in range, key guard).
- **Evidence:**
  - Only centring, all-zero pools and the disjoint variance ratio are checked.
  - Nothing tests the twin's symmetry or serial dependence in seed order.
  - "Term out of range" holds through `Dimension.values` (refusing). In A2 it is pre-empted by B-2's clip.
- **Failure it allows:** a twin that does not reverse every draw (the m-8 defect the note says "this null catches") can
  leave Delta skewed yet centred within 4 SE, and nothing fires.
- **Remedy:**
  - The lead's row fixes the symmetry test's form before the run. One option is the exact check: the twin of the twin
    reproduces the base bit for bit on the declared sample. Another is a sign test of Delta at a stated level.
  - Implement it with a test that plants an asymmetric twin and sees the kill.

---

## Minor findings

- **m-1 (minor):** `extended/h3a_report.py:152`. Mutant R1 (`lo_stop > lvl` to `>=`) survives. It differs only when the
  Beta quantile equals the level exactly, which does not happen at these n, so it is equivalent in practice. Leave it,
  or add a constructed exact-equality case.
- **m-2 (minor):** `scripts/h3a_run.py:502-514`. The stress's 15 runs use history 0 and `min(M, 64)` seed indices, a
  size declared nowhere (section 8 gives 15 runs only). Fine as a reading beside, but the lead's row should state it
  before the run.
- **m-3 (minor):** `scripts/h3a_run.py:241-255`.
  - The disjoint tripwire stores **hand-built** keys (moment 0, the race draw kind), not the run's keys. `g_base`
    samples only seeds 0 to 63, so the second half's real keys are never stored.
  - There is no explicit check that the seed-index sets are disjoint, and `half = M // 2` stands in for `H.DISJOINT`.
  - Fix: check `set(H.DISJOINT ranges)` explicitly, and sample the run's own keys at both halves' first 64 seeds.
- **m-4 (minor):** `scripts/h3a_run.py:447-452`. `_map_workers` silently clamps to 2 workers instead of refusing more.
  The runner neither checks nor records `OMP_NUM_THREADS` (the probe records it). The docstring's `--mem-gb 1.0` is
  below E-285's own figure; see B-7.
- **m-5 (minor):** `scripts/h3a_run.py:636-669`. The report part reads `h3a_a1.csv` and `h3a_a2.csv` without
  `verify_result`. It does not check that both came from clean runs of one commit, or that that commit's build files
  equal the report's.
- **m-6 (minor):** `scripts/h3a_run.py:287`. The failures at the fill are reported for A1's base arm only, not the twin,
  A2, A3, A4 or the stress arms (section 7: "counted apart, reported beside").
- **m-7 (minor, declaration-level reading):** at J' = 100 replicates, the empirical-Bernstein range term,
  (7 ln(2/alpha) / 3) x 2 / 99, is 0.174, 0.250 and 0.358 at the three levels (my check 3). At replicate sd 0.05,
  EB rejects only above a mean of 0.19, 0.27 and 0.38, so the 18 EB pooled counts can fail only on a gross sign-level
  error. Section 14 already says a pass means "no laxity detected". The report should print this beside the EB rows.
- **m-8 (minor):** `scripts/h3a_run.py:478-479, 562-563`. A premise failure raises before anything is written, so the
  only record is the first 5 failures in the run's log. Write the full premise table (with `exploratory=False`)
  before refusing.

---

## What I tried that found nothing

- **(1) The stop, planted.**
  - One pooled cell made lax (A2, betting, level 0.001, 12/2000) gives `stop_h3d = True`, `lax_count = 1` (check 1a).
  - All 1080 per-history cells made lax at rate 1, with pooled cells clean, gives `stop_h3d = False` (check 1b).
  - The stop reads exactly 54 keys, refuses missing, extra, duplicate and per-history rows in the pooled set, and uses
    the one-sided Clopper-Pearson `beta.ppf(0.05 / 54, k, n - k + 1)` with a strict `>`.
- **(6) Mutation of the report code.** 15 one-line mutants were run against `tests/test_h3a_report.py` in a detached
  clone of `8538664` under `%LOCALAPPDATA%\stage2-extended-runs\rt-h3a`, which I have since removed. 14 were killed:
  - the two-sided split;
  - the CP off-by-one, and the flipped confidence;
  - per-history entries stopping the run;
  - only A1 deciding;
  - a subset of the 54 accepted;
  - E-052's label deciding;
  - the family alpha used per count;
  - the level doubled;
  - a k = 0 bound of alpha;
  - the duplicate check removed;
  - two levels instead of three;
  - the per-history key check removed;
  - only 53 cells read.

  R1 survived (m-1).
- **(2) Count derivation.** `h3a_report` builds 36, 18 and 54 from its part tuples and `three_way_h3a.LEVELS`, with an
  assert, not a typed list. The stress's 15 comes from `R.stress` and `stress_arms` (3 x 5). The runner's A1 and A2
  per-history rows are 36 x R and 18 x R. The failures in (2) are A3's and A4's (B-5, B-6).
- **(3) Seeds.**
  - None of the five files holds a literal of either block.
  - Every seed comes through `three_way_seeds.issue`.
  - A1, A2 and A4 use the histories and coins roles, and A3 only its own role, matching section 15's table.
  - P4's regime signs use the `plant` kind of the histories role in part A4, which `ROLE_USE` allows. That key is
    distinct from the smaller-J key (part A1), which goes through `three_way_h3a.smaller_j_rng`.
  - The defect is the tests' use (B-3).
- **(4) Slots.** `SLOT_SPEC` matches E-285's six slots: A1 and A2 at R = 20, M = 10000; A3 at histories 0-99 and
  100-199, M = 2000; A4 at histories 0-4 and 5-9, M = 10000. Each compute part requires `run.lock` held by its job, a
  clean checkout and an absent output. Memory is the gap (B-7).
- **(5) No bars, no held-out date, no confirmation window.**
  - The runner imports no reader and no bar loader.
  - Every `Plan` is built without dates (S1 synthetic).
  - `family_stats` and `three_way_*` load no data at import.
  - The preconditions gate checks H3's pinned LF sha256, template v3's pin with its R-10 clauses, and `4c07026`'s nine
    build files unchanged (tested positively and negatively).
- **The bounds used:** `ST.mcdiarmid` (Hoeffding on `P_B`), `ST.eb_lower` and `ST.betting_lower` on J' seed columns are
  called as declared.

## What I could not check, and the experiment that would settle each

- **The real memory peak (B-7).** Run `_a1_one_history` with the seed and part injected (B-3's remedy) under the tests'
  seed in the tests' part, at M = 1000 and the full 120 starts and h = 63. Read `procmem` peak and extrapolate linearly
  in M. Light: minutes, 1 worker, `OMP_NUM_THREADS=1`.
- **How large B-2 (a) is on A2's own toys.** Use the same injection with the tests' seed. Per start, compute
  `J.expect`'s theta and the Monte Carlo P(Xf = 0), and print theta P(Xf < theta) against the bound's margin.
  Light to moderate.
- **Whether `paid_by_63`'s cap (0.6) binds on A2's or A1's toys.** Same run; report the share of seed sets at a cap
  (the note's N-11 reading).
- **The runner mutants (B-4) were judged by inspection of the test's assertions, not executed.** Running them would
  have drawn H3-A's declared seeds again (B-3). After B-3's fix, run the six mutants against the new R = 2 test.
- **A3's "test's J" and whether S1 carries time conditions** are rulings, not checks (B-6).
- **H3's section 11 says A2 uses "barrier and R-10 trades";** `three_way_h3a.A2_PAIR`'s comment says R-10 walks are
  excluded. Appendix C governs and I did not test which trades A2's schedules hold.
