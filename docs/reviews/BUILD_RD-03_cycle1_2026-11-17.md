# Red team: RD-03's build, corrective cycle 1 (Q-119r2) -- 2026-11-17

**Target.** Branch `wt/wt-payout` at ceeb4bf (worktree `%LOCALAPPDATA%\stage2-extended-wt\wt-payout`), the diff
42e3f3e..ceeb4bf: `extended/cl_reading.py`, `extended/cl_toy_inputs.py`, `extended/levers_path.py`,
`scripts/cl_reading.py`, `identity/cl_identity.py`, `tests/cl_synthetic.py`, `tests/test_cl_build.py` and the new
`tests/cl_run_check.py`. I read it against my first note (`docs/reviews/BUILD_RD-03_2026-11-17.md`), the builder's
hand-back, and the pinned text `prereg/RD-03_contract_levers.md` (E-152).

**The brief and the hand-back.** The hand-back offers a guess for T-3 at h = 21: S3a's card entry "does not move on
this toy". I treated that as a hypothesis and tested it on the test's own toy. It is half right, and the half that is
wrong matters (section 3).

**What I ran** (light work only, on toys, in my scratchpad; nothing under `results/`; no bar or atlas read):

- sections t1, t7, t10, t14, t15 and t16 of `tests/cl_synthetic.py`, each on its own;
- `tests/cl_run_check.py` (steps 3, 4 and 5, `--synthetic`), once;
- three diagnostic scripts on T-3's toy (section 3), under `scratchpad/rt/`.

The diagnostics replay the test's own toy, which is drawn from section 12's toy seed because the test declares it.
My one new seed, used only for the plant's trade counts, is `RT_PLANT_K_SEED = 11903021`, outside the 2026xxxx range.
I did not run the full suite.

---

## Verdict

**Merge after stage 0 and the listed items.** Every item below is to code and tests. The pinned text is untouched,
and no item changes a declared rule. Judged as a declaration, RD-03 still **stands with readings**.

- **Sound.** M1 to M5, m1 to m5 and m7 to m9 are fixed, and each named proof can fail. A-1 is still inert when off:
  T-1, T-10 and T-15 pass on this commit, and the four new marked lines are gated and only count.
- **Not sound.**
  - **T-3 cannot fail at h = 21**: not its planted check, and not its no-leak claim either. The cause is the plant's
    direction, not the code (diagnosis (b), section 3). The fix is a second, opposite plant. On the reference cell I
    showed that it catches the h = 21 leak.
  - **The Back2Funded counted reading is mislabelled.** In the beside menu its rows carry both "not counted: the
    optimistic reading" and "counted: the conservative reading". In `cl_reading_ftp.csv` the cycle removed both labels.
- **Still owed.** Stage 0 (A-5, T-12), with the brief items in section 5.

---

## 1. Findings, by severity

### MATERIAL

**R1. T-3 is vacuous at h = 21: a leak there passes both its claims.**

- **Where.**
  - `tests/cl_synthetic.py` 714-756 (`t3`). The plant at 736 is `win = np.zeros(k, bool)`: every late trade lost.
  - `tests/test_cl_build.py` 65-67, the strict xfail.
- **Evidence.** Section 3 has the full diagnosis. In short: the only reading with a 21-session horizon is S3a, the
  share paid by session 21. The starts that a leak at 21 lets into the early block are not paid by session 21 even
  with the toy's own winning late block. A late block of losses can only remove payouts, so S3a cannot move.
- **Failure it allows.** Say an edit read S3a, or its paired card entry, or the frontier through S3a, on a block purged
  at fewer than 21 sessions. Then:
  - T-3's no-leak claim (`first == _t3_early(runs2)`) still passes, because the same losses-only plant is its only
    alternative late block;
  - the planted check reports `T3_LEAK_21_CAUGHT=False`, which the strict xfail expects, so it passes too.

  So the merge checklist's item "no feature reads a bar after its alert" has no test behind it at h = 21.
- **Remedy.** Replace the single plant with two opposite plants. The test should assert:
  - the no-leak claim against both: every early row is identical under the toy's late block, under all losses and
    under all wins;
  - the power claim at every h of `HORIZON_SET`, 21 included: with the planted leak, at least one early row differs
    under one of the two plants;
  - a precondition at each h: the leaky block holds at least one start whose h-session window reaches 2024-01-02.

  Then remove the strict xfail. The draws stay on the toy seed, which section 12 declares for "T-3's synthetic late
  block", for example `[TOY_SEED, 4]` for one plant and `[TOY_SEED, 5]` for the other. The cost is one more toy job of
  five cells, about half of t3's current 8 minutes. Section 3 gives the sketch and what my demonstration showed.

**R2. The Back2Funded counted reading carries the optimistic label, and the reading file has lost both labels.**

- **Where.**
  - `extended/cl_reading.py` 925 adds `LR.B2F_LABELS` to every Back2Funded row. Its last entry is
    `BY_NAME["reactivation_counted_as_purchase"].label`, that is "not counted: the optimistic reading"
    (`extended/levers_readings.py` 69-70).
  - Lines 929-931 then append the variant's own label.
  - In `run_beside`, the cycle deleted the block that put the U-6 labels into the notes of `cl_reading_ftp.csv`'s rows
    (the old 1135-1141).
- **Evidence.** In my `cl_run_check` output (`cl_menu_beside_synthetic.csv`):
  - each Back2Funded row at a `ftp_*` response with variant `counted` carries "not counted: the optimistic reading" and
    "counted: the conservative reading";
  - each `declared` row carries the optimistic label twice.

  In `cl_reading_ftp_synthetic.csv`, none of the 66,380 rows with `mode` = `counted` names its reading in its note.
- **Failure it allows.** 10.1 item 8 says the two readings are "labelled 'not counted: the optimistic reading' and
  'counted: the conservative reading'". A reader of the beside menu's conservative row is told it is the optimistic
  reading too. A reader of the reading file has only the bare `mode` token, `counted` or `declared`.
- **Remedy.**
  - On rows with `mode == CONSERVATIVE`, drop B2F_LABELS' U-6 entry.
  - Do not append it a second time on the declared rows.
  - Put the variant's label back into the notes of `cl_reading_ftp.csv`, on every Back2Funded row of both variants.
  - Add a T-14 assertion on a two-variant synthetic menu and reading: exactly one of the two labels on each row,
    matching its `mode`.

### MINOR

**m-a. The guard excuse is broader than it needs to be, and the pipeline's M2 proof rests mostly on it.**

- **Where.** `extended/cl_reading.py` 878-884 (`guard_reason`) and 1014-1020 (`check_menu`).
- **Evidence.** In my `cl_run_check` output, 62 of the 64 step-3 menu rows excuse ten of the fourteen guard nets: the
  month-6 and month-12 nets and their CVaR. At 70 sessions no start has 126 or 252 sessions left. So on the pipeline,
  M2 is proved only for the month 1 to 3 nets, CVaR10 at month 3 and the gate entries; T-14's hand-built menu covers
  the rest.

  `check_menu` also accepts any `guard_reason` text. A row whose reason named `ruin_probability` would pass, although
  "a gate entry is never excused".
- **Failure it allows.** None on the real window: block `all` always has starts with 252 sessions left. But the excuse
  is a toy accommodation that the real run would also accept silently.
- **Remedy.**
  - In the real run (not `--synthetic`), refuse any menu row with a non-empty `guard_reason`.
  - In `check_menu`, accept only names in `GUARD_COLUMNS`.
  - In `cl_run_check`, assert that the excused names are exactly those whose horizon exceeds `--days`.

**m-b. The solver's view: a missing line is printed, not refused, and the commit is not tied to the row.**

- **Where.** `extended/cl_reading.py` 983-1002 and `scripts/cl_reading.py` 326-338.
- **Evidence.** Two gaps:
  - When `cl_fit.csv` is given but has no G-B or G-N line for a design, the menu prints "no G-B line for p14 in stage
    0's view" and goes on.
  - `solver_view_frame` verifies the file's manifest, but does not check that the manifest's commit is the one the
    `--stage0-row` row records (my first note's remedy for M7).
- **Remedy.**
  - In the real run, refuse a missing line.
  - Hold the manifest's commit to the commit the row names.
  - Fix the `solver_view` section's columns in A-5's brief: `design` in `cl_reading.DESIGNS` (`p14`, `p16`), `rule` in
    {G-B, G-N}, and `line` (section 5).

**m-c. Q-44's Focused Trader preflight (m6) has no test.**

- **Where.** `extended/cl_reading.py` 194-206.
- **Remedy.** Add a stub test: a `CLInputs` whose `q44()` returns a frame lacking one `ftp_*` response for one design,
  and `super().preflight` patched to return `[]`. The preflight must name the missing response.

### NOTE

1. **Interpretation 4 (rates per 252 sessions) is faithful, but `yr = 252.0 / 252.0` (511) is a typed constant.**
   - Why it is faithful: the counted starts are those with 252 sessions left (`block_days(..., 252)`). Their long
     replay is exactly `U.HORIZON` sessions (`user_beside.py` 633, `L = min(U.HORIZON, n - s)`). `StartCounts` keeps
     each start's longest run (`levers_path.py` 1975-1979).
   - Remedy: write it as one, label the rows "per 252 sessions (a start's year)", and assert that `observed ==
     U.HORIZON` on the counted starts.
2. **`ref`'s gate label on the beside rows lacks the phrase.** It reads "the registered gate (9.1's identity) (step 3's
   gate file)", without the literal "the gate at 0 %" that 10.1 item 8 names. The registered row is at 0 % with the
   placement off (`pp_inputs.base_gate_rows`). Add the phrase.
3. **Interpretation 2 (the guard rows in step 3's gate file) is faithful.** The guard rows are copies of the gate's own
   rows at the bound and 0 %, plus `ref`'s registered row, in one verified file. A cheap extra check: have
   `gate_guard_from_file` hold each cell's `part=guard` entry to that file's own `part=row` entry, at the bound, at 0 %
   and on the non-twin row, as `cl_run_check` does for the menu.
4. **The hand-back says T-3 covers "divergence rows".** They are block `all` by design (10.1 item 6), so
   `_t3_early`'s `block == "early"` filter drops them. That is correct, but the claim overstates.
5. **The toy's 2024-01-01 is a session** (`pd.bdate_range`). `u_select` puts it in the late block, but the plant does
   not replace it, because it replaces from 2024-01-02. Together with the vendored purge's one-session margin (`s <=
   last - h`, so a window ends at least one session before the early block's last session), T-3 can detect only a
   leak of three or more sessions. The planted leak (h to 1) is gross, so this is fine. A finer plant (h to h - 3)
   would test the margin.
6. **The no-leak claim at the other horizons holds.** On every cell and horizon the correct reading was byte-identical
   under both late blocks (section 3).

---

## 2. M1-M7, m1-m9 and the notes: fixed as asked, and can the proof fail?

| item | fixed? | can its proof fail? |
|---|---|---|
| M1 | yes: `gate_entry` maps D-312's `pf_growth_on_base_p50` and `pf_required_p90`, with the ruin probability, and refuses missing or non-finite values | yes: `cl_run_check` holds every non-`ref` menu entry to its gate row's `pf_growth_on_base_p50` to 1e-12, and the old `median_log_growth` differed on the toy (my first note). Passed in my run |
| M2 | yes, with m-a: `ref`'s entry comes from `base_gate_rows`, labelled; `check_menu` reads the values, not the columns | yes: T-14 blanks the growth entry and drops the guard rows, and both refuse. The pipeline's coverage is partial (m-a) |
| M3 | yes: steps 4 and 5 read `cl_gate`'s `part=guard` rows, verified; missing cells are refused before any run; the beside menu is built by `menu_table` and passes `check_menu` | yes: `cl_run_check` runs `check_menu` on `cl_menu_beside` and checks every finite P's gate entries |
| M4 | yes: `label_house` covers cell, base and cell lists, in all three reading files | yes: T-14 on a reading frame, and `cl_run_check` on `cl_reading` and `cl_reading_ladder` (S6's list rows only through `label_house`'s code) |
| M5 | yes: `calendar_frames` runs before the first replay; the two 9.3 counts are built and refused if absent; the manifest says `calendars_checked` only from step 3 ("not read in this step" for 4 and 5) | yes: t16 checks the holiday-hours sessions on hand-built calendars and refuses a changed calendar. The counts' values rest on RD-02's `start_tallies` and `recorder_tallies` |
| M6 | at 63, 126, 189 and 252 (early starts asserted at every h; five cells; mechanics and guard rows); **not at 21 (R1)** | at 21 neither claim can fail (R1). The other horizons fail when they should |
| M7 | wiring only; A-5 not built (m-b) | T-14: a changed solver view moves no other column and no order |
| m1 | yes (`cl_run_check`) | it ran green here, about 9 minutes |
| m2 | yes: `cell_gate` runs `seat_limit_problems` and refuses a missing `combines` | refuses on a missing key; no negative test, but the code reads plainly |
| m3 | yes: `reactivation_checks`, `fee_paid` on every fee site, the purchase budget on replays, the request bounds in steps 4 and 5 | yes: T-7 has five new hand-broken cases. `fee_paid`'s `<= EPS` matches the withholding tests' `<= EPS` (`levers_path.py` 332-359), so a legal run cannot trip it |
| m4 | yes: cash, acts (running, live, queue) and fees by kind, close by close, before binding and in the expiry pair | yes (T-4, T-5; step 3 on toys) |
| m5 | yes: four columns, and `funded_lost` in the divergence rows | `cl_run_check` builds them; their values are not asserted |
| m6 | yes | no test (m-c) |
| m7 | yes: refused before the ledger (real run) and before anything runs (synthetic) | yes: `cl_run_check`'s rerun saw "already exist" |
| m8 | yes: `toy(k, i)` from `TOY_SEED` | T-9 and T-0 |
| m9 | yes: numpy arrays, and `keep_compact` after 9.1 item 7's checks (which run in (b), before it) | the window-size peak is unmeasured (section 6) |
| notes 1-9 | yes: the 3-se label, the derived thresholds, the docstring, the seat refusal printed, `naf`'s line, the timing label, the pairing note | labels only |

---

## 3. T-3 at h = 21: the diagnosis

**Answer: (b), refined.** Confidence: high, about 95 %. On the reference cell it is measured. For the other four cells
it is inferred, because they read S3a through the same `PR.card_of` and `u_select.scorecard`.

**Which readings have h = 21.** Of everything T-3 compares, only S3a, "the share paid by session 21", has a 21-session
horizon (`u_select.MEASURES`, read by `u_select.scorecard` through `block(records, which, 21)`). It appears as:

- the card entry;
- the paired card entry;
- through the cards, the frontier on P, S1, S3a and S5a.

No guard, distribution, paired, mechanics or divergence measure reads at 21. `month_horizon(1)` is 63, and
`DIFFER_SESSIONS` is (63, 126, 252).

**How the plant works.** The patched `u_select.block` purges the early block at 1 instead of 21. On the toy (560
sessions from 2022-03-01), the early block's last start is index 478 (2023-12-29), and the plant replaces sessions from
index 480 (2024-01-02).

- **Does the leak reach the reading?** Yes, so it is not (a). The leaky block adds starts 458 to 477 to S3a's early
  block (n goes from 458 to 478). The 21-session windows of 18 of them (460 to 477) reach into the replaced sessions.
- **Does the reading move?** No. With the toy's own late block, those leaked starts' first payouts arrive between
  sessions 25 and 36, none by session 21; across all early starts, 8.75 % are paid by 21. Under the builder's plant
  (every late trade lost) they are never paid. The indicator "paid by 21" is therefore 0 under both late blocks, and
  S3a is identical: 0.0879 at n = 478 in both. That is the hand-back's guess, made precise. S3a varies across starts;
  it just cannot move on the leaked starts under a plant that can only remove payouts.
- **Is it (c), a real gap in the code?** No. The correct reading is identical under both late blocks (S3a 0.0917 at
  n = 458), and the h = 21 path is the vendored `block` at the measure's own horizon. What R1 names is a gap in the
  test, not a leak in the code. The test cannot see a leak at 21.

**The opposite plant catches it.** With every late trade won (`scratchpad/rt/t3_winplant.py`, reference cell, the
card):

- the correct reading is still identical (S3a 0.0917, n = 458);
- under the leak at 21, starts 468 and 472 are now paid by session 21, and S3a moves from 0.0879 to 0.0921 (n = 478);
  S3a is the only card measure that moves;
- the margin is two starts. That is deterministic on the toy seed, but thin.

On the card alone, the win plant moves nothing at 189 or 252. On the full reading it does: see the five-cell
demonstration below. Neither plant alone is a test at every horizon on every reading, so the corrected test uses both.

**What the test should assert instead** (a sketch; the repository version derives the plants' draws from `TOY_SEED`):

```python
def plant(job, won: bool, key: int):          # every late trade won, or every late trade lost
    rng = np.random.default_rng([TOY_SEED, key])
    ...                                         # as now, with pnl = +1000 (target) or -500 (stop) on every trade

runs0, runs_lo, runs_hi = _t3_runs(job), _t3_runs(plant(job, False, 4)), _t3_runs(plant(job, True, 5))
e0 = _t3_early(runs0)
check(e0 == _t3_early(runs_lo) and e0 == _t3_early(runs_hi), "T-3: an early reading moved with the late block")
for h in HORIZON_SET:                           # 21 included; no xfail
    check(leaky_block_reaches_late(recs, h), f"T-3: the plant cannot reach h = {h}")
    with leak_at(h):
        a, lo, hi = _t3_early(runs0), _t3_early(runs_lo), _t3_early(runs_hi)
    check(a != lo or a != hi, f"T-3: a planted leak at h = {h} is not caught")
```

**The five-cell demonstration.** `scratchpad/rt/t3_corrected.py` runs exactly this with the builder's own `_t3_runs`
and `_t3_early`, over all five cells and the full early reading. It took 727 s at one worker; the engine's
memory guard dropped it from two.

- **The no-leak claim holds under both plants.** Every early row is byte-identical.
- **h = 21.** The losses plant moves 0 rows; the wins plant moves 13. **Caught.**
- **h = 63, 126, 189 and 252.** Both plants catch the leak. The losses plant moves 1,681, 250, 41 and 414 rows; the
  wins plant moves 442, 148, 30 and 304.

So the corrected test catches a planted leak at every horizon of section 5's table, 21 included, and the xfail can
go. Its cost is one more toy job: three jobs instead of two.

---

## 4. The four interpretations (hand-back section 6)

1. **A guard entry excused when no start has its horizon left: faithful only where it cannot fire.** Section 1's
   "refuses to print a P without them" has no exception. On the real window block `all` always has 252-session starts,
   so the excuse never fires there. It exists for the toys. Make the real run refuse it (m-a).
2. **The guard rows in step 3's gate file: faithful.** 10.1 item 8 asks for "the cell's 0 % gate (item 9), labelled",
   and these rows are that gate's own values, carried in a verified file. The one-line cross-check is note 3.
3. **The Back2Funded variant labels: the text is faithful, the placement is not.** The two strings match 10.1 item 8
   and U-6 word for word. But the counted rows also carry the optimistic label, and the reading file carries neither
   (R2).
4. **Mechanics rates per 252 sessions: faithful.** It is exact on the starts read (note 1). D-34's "per year" is 252
   sessions in U1's own convention (`user_journey.HORIZON = MONTH x MONTHS`).

---

## 5. Stage 0 (A-5, T-12): what its brief must say

1. **Scope.** A-5 is `extended/levers_fit.py`, `scripts/cl_fit.py` and `identity/cl_fit_identity.py`, with T-12, T-8's
   stage-0 half and T-11's stage-0 half (removing its strict xfail, `tests/test_cl_build.py` 186). It writes
   `results/cl_fit.csv` with the sections of 15's file list: `identity`, `oracle`, `reading`, `rent`, `checks`,
   `resolve_beside` and `solver_view`.
2. **A feasibility probe first, stop-and-report (6.1's last paragraph).** Before any other code, a read-only probe
   answers two questions:
   - (i) do `propedge.research.u_size_fit`'s and `state_policy`'s pieces compose without D-559's two absent files
     (`rc150_table_screen.csv` and `_policies.json`)?
   - (ii) can the registered policy's arrays be held in the per-R classes' `forward` (`FundedByR`, `CombineByR`)
     without editing vendored code?

   (ii) is the crux. The registered table `state_dp_e-0.050_lamstar_noclose` was solved at FV3-C's single edge. Its
   policy must map **exactly** onto each base's states and actions at that base's own rungs: P-14's 12.5- and 25-point
   rungs, P-16's 37.5-point stop. "Exactly" means the same balance grid, winning-day counter and action set, with no
   nearest-state rounding, no interpolation and no re-solve. If either answer is no, the build stops and reports, and
   stage 0 does not fall back. That outcome is legitimate: E-146 makes stage 0 decide nothing, and step 3 then runs
   with `--stage0-stopped`.
3. **The forward pass with the registered policy held fixed.**
   - Re-solve at FV3-C's single edge (6.4 item 1's identity), and take its `Solution`'s policy arrays.
   - At each base's per-R edges (`bound`: the gate's `lb_by_rr`; `zero`), propagate those arrays with the vendored
     `forward`, the policy set to the registered one in every state.
   - Read p, S, F = S + 149 p, F_acc, D, W and T.
   - Take `lambda_pi` from the vendored `cycle_rate` (`vendor/stage2/scripts/state_policy_dp.py`), imported, never
     restated.
   - (b): the exact re-pricing ($95 for $49 per billed subscription, $0 activation, payouts unchanged).
   - (c): D-666's own solves at Standard and No Activation Fee prices, labelled "D-666's re-solved bound-edge table,
     not the table the cells trade".
4. **The checks, refusing, with their tolerances** (6.2):
   - (a-1): the evaluator on the registered solve reproduces its own forward summaries and the tie-broken rate, to
     1e-9;
   - (a-2): the evaluator on (c)'s Standard `Solution` reproduces `u_size_fit.csv`'s `reading` rows, to 1e-9;
   - (c-i): `W - lambda* T` equals `fresh_value` at day 0, to 1e-6;
   - (c-ii): on the exact solve, the attempt value lies inside the rent bracket, with the tie-broken value printed
     beside;
   - the zero-edge oracles: P(pass) at most 2/5, stage one's supremum 0.327131, and gross payouts at most $2,000.

   Any failure writes only the failure's lines and stops stage 0 alone.
5. **The identity is a heavy solve.** `cl_fit_identity`:
   - (1) the single-edge solve against the exported tree, its rent to 1e-9;
   - (2) each base's rungs, offers and edges equal `u_size_fit.csv`'s `50k` rows (`rungs`, `edge`), and (c)'s Standard
     solves reproduce `reading` and `rent` to 1e-9;
   - (3) the oracles.

   It runs from a clean checkout, under the purpose `identity` and its own row, under `run.lock`, one worker. It reads
   no bar, but it is a solve, so it is heavy under CLAUDE.md.

   **The cost, read rather than guessed.** `vendor/stage2/results/u_size_fit.csv.manifest.json`, `parameters.cost`,
   records each $50K solve's seconds and process peak. Read `p14_50k_*`: the later `p16_*` peaks are the process's
   running maximum, carried over from the earlier larger-size solves. That puts each solve at roughly two minutes and
   one gigabyte. The identity is about five such solves, and stage 0 is "four policy evaluations and eight solves" (15).
   Taking `--hours 2 --mem-gb 2.5` is generous.
6. **The 6 GB note.** `MEMORY_LIMIT_GB = 6.0` (`vendor/stage2/scripts/u_size_fit.py` 110-111, 481-482) is D-666's
   refusal on `estimate_gb`'s estimate: "a solve's estimated memory above this is not run ... stop and report". It is
   not the expected footprint.
   - A-5 keeps the guard: estimate before each solve, refuse above 6 GB, and never coarsen a grid.
   - The brief should say that a $50K solve's estimate sits well below it.
   - On a 16 GB machine with other work resident (about 1.2 GB physical memory was free during this review), the lock's
     `--mem-gb` and a check of free memory before each solve matter more than the 6 GB.
7. **The solver's view lines.** Use 6.3's two lines word for word, with the bracketed alternatives computed. The rows
   are `solver_view` with columns `design` (`p14`, `p16`), `rule` (`G-B`, `G-N`) and `line`, plus the two sides as
   their own rows (`checks`). Connect them to no cell, flag or order; T-12 asserts that there is no code path, and M7's
   T-14 case already holds the menu side. The real run refuses a missing line (m-b).
8. **T-12's toy** (14.3's row):
   - hand-computed forward summaries;
   - each of (a-1), (a-2), (c-i) and (c-ii) shown to fire on a hand-broken toy;
   - a toy where the fixed policy is not optimal, so that an optimising backward check fails while (a-1) and (a-2)
     hold;
   - G-B's and G-N's sides and lines;
   - a nudged row of the identity file refused.
9. **Inputs, each checked against its manifest:** `state_policy_v12.yaml`, the two gate files' `edge`, `rung` and
   `resolution` rows, `rc_width_screen.csv` for P-16's rung (held to `u_size_fit.csv`'s `rungs` rows for `p16`), the
   `state_policy_v12_noclose` files, and `u_size_fit.csv`. No seed: the chain is exact.
10. **The runner's link.** Step 3's `--stage0-row` row names `cl_fit` and the commit, and `cl_fit.csv`'s manifest
    commit is held to it (m-b).

---

## 6. The window-size measurement: is a scaled measurement enough?

**Yes, if it scales the right quantity and says it is extrapolated.** Section 15 asks for a measurement "on synthetic
campaigns of the window's length ... stated in the lead's row with its memory", in E-117's form. E-117's own row
extrapolated the reading's memory. The window's length (1,700 days) must stay; paths and starts can be scaled.

- **What `--paths` scales.** Only step 3's gates: 30 gates of 500 paths, each with its twin. The replays of steps 3 to
  5 scale with starts times 252 sessions times cells, whatever `--paths` is. Steps 4 and 5 run no gate, and they are
  most of the builder's 16-hour estimate. Fewer paths alone saves nothing there.
- **What to run instead.**
  - Step 3 at the full 1,700 days with `--paths 50`, plus one cell's gate at 500 paths on its own, to fit the gate's
    seconds per path.
  - Steps 4 and 5 on every 5th start and again on every 10th, to separate the fixed and per-start parts of time and
    memory.

  This needs a synthetic-only `--starts` flag on `scripts/cl_reading.py`. `run_scorecard` and `run_beside` already
  take `starts`, so it is a two-line change. Extrapolate linearly, run at two workers only (the configuration to be
  used), and expect about a quarter of the 16 hours.
- **Why that is enough for `--hours`.** The lock's hours are a bound for investigation, not a kill. A lock older than
  its expected end plus an hour is looked into, never stolen. Set `--hours` at twice the extrapolation, and let the real
  run's own printed seconds and peak memory go into its row. Over-estimating costs only an idle lock.
- **What the scaled run must still settle: memory.** On this 16 GB machine about 1.2 GB was free during my review, and
  the engine's guard dropped my two-worker toy to one worker. So:
  - the per-start memory slope is the number to read;
  - the lead's row says "extrapolated" beside the figure;
  - the one-worker measurement is needed only if two workers are not approved (the `cl_t10w2` row).
- **A caveat to state.** The toy's trade stream wins 60 % at 2R, with 1 to 4 trades a session. It passes evaluations
  faster and so carries more accounts than the real designs. That probably overstates cost, which is the safe side for
  `--hours`.

---

## 7. Anything new the cycle broke

- **`levers_path.py`: nothing broke.** It has four new marked lines: `fee_paid` after the rebill and after the purchase,
  each under `if lv is not None`, and `activated(c, day, cash)`.
  - Each is gated by `lv is not None`, and `fee_paid` counts only under house money after its trigger.
  - `acts` and `fee_days` only record.
  - `cash_closes` became an array, and `bind_day` was fixed for it. No other reader of `cash_closes` uses `or ()`
    (grep).
  - The re-composition proof strips the marked lines and is still empty (T-1).
  - T-1 (the path and the replay against the vendored ones, with `Levers()` and `Levers(counters=True)`), T-10 and
    T-15 pass on ceeb4bf. The shared adapters `user_beside.py`, `gate.py` and `campaign.py` are not in this diff, so
    T-15's pins still apply.
- **Broken: the U-6 labels** in the reading file (R2).
- **Changed: `mechanics_rows`' rate.** The old `252 / mean(len(cash_closes) - 1)` would now fail, because
  `keep_compact` drops the closes before the mechanics run. The replacement is exact (note 1).
- **`NS` is a module-level dict** that `guard_rows` reads right after `guard_values` writes it. That is correct while
  the reading is single-threaded. It is a trap if the reading is ever parallelised; worth a comment.

## What I tried that found nothing

- M1's equality, M2's refusals, M3's file read and its refusal, M4's labels, m7's rerun refusal: all on my own
  `cl_run_check` run, which came out `{"problems": []}`.
- Whether `fee_paid` could flag a legal house-money run: its threshold equals the withholding rules'.
- Whether exact-length runs could overwrite a start's lever counts: `StartCounts` keeps the longest run.
- Whether `keep_compact` runs before a check that needs the closes: 9.1 item 7 and the expiry pair run in (b), and
  `keep_compact` comes after.
- Whether the beside steps could run a cell with no guard entry: refused before the first replay.
- The Q-44 preflight's column names against RD-02's own (`pp_inputs.py` 217): the same.
- The calendars being read before the first replay in step 3: yes (`run_scorecard`, before `inputs.jobs`).
- The look-ahead question at every other horizon: the correct reading is unchanged under both late blocks.

## What I could not check

- Anything on the registered data, Q-44's file, or the real gate files' `pf_*` columns. RD-02's `GATE_READING`
  refuses without them, so they exist there.
- Stage 0, which is not built.
- The window-size time and memory.
- Whether the h = 21 catch survives a change to the toy. It rests on a margin of a few starts (13 rows on five cells):
  deterministic, but thin. The reach precondition in R1's remedy guards the plant, not the margin.

---

## Proposed row

| E-NNN | 2026-11-17 | **The red team's re-read of Q-119's corrective cycle 1 (wt/wt-payout ceeb4bf against 42e3f3e; `docs/reviews/BUILD_RD-03_cycle1_2026-11-17.md`): merge after stage 0 and the listed items, code and tests only, the pinned text unchanged.** **Holds:** M1-M5, m1-m5 and m7-m9 and the notes fixed, each proof able to fail (T-7's five new cases, T-14's blank-guard and no-guard refusals, t16, `tests/cl_run_check.py` green on steps 3-5); A-1 still inert when off (T-1, T-10 and T-15 pass; four new marked lines, gated and counting only); the four interpretations faithful in text (the guard excuse only where it cannot fire on the window). **T-3 at h = 21, diagnosed (b), confidence high:** the only 21-session reading is S3a; the planted leak does reach it (18 leaked starts' windows reach 2024-01-02), but those starts are not paid by session 21 under the toy's own late block, and a losses-only plant can only remove payouts; so T-3's no-leak claim and its planted check are both vacuous at 21; with an all-wins plant beside it, the leak is caught at every horizon, 21 included, and the no-leak claim holds under both plants (five cells, 727 s at one worker). **Before merge:** (R1) T-3 with two opposite plants from the toy seed, the no-leak claim against both, the planted leak caught at every h including 21, a reach precondition, the strict xfail removed; (R2) the Back2Funded counted rows carrying only "counted: the conservative reading" and the declared rows only "not counted: the optimistic reading", in the beside menu and in `cl_reading_ftp.csv`, with a T-14 case; (m-a) the guard excuse refused in the real run and limited to `GUARD_COLUMNS`; (m-b) a missing solver's-view line refused and `cl_fit.csv`'s commit held to the stage-0 row; (m-c) a stub test for the Focused Trader preflight. **Owed:** A-5 and T-12 per the note's section 5 (a feasibility probe first: the registered policy held exactly in the per-R forward pass, or stop and report; `cl_fit_identity` a heavy solve under the lock, about five $50K solves, D-666's 6 GB a refusal on the estimate and not a footprint). **The window measurement:** scaled at the full 1,700 days (step 3's gates at 50 paths with one 500-path gate to calibrate; steps 4-5 on every 5th and every 10th start through a synthetic-only `--starts`), at two workers, extrapolated and labelled so, `--hours` at twice the extrapolation, the real run's own timing in its row. | E-152, E-158; `docs/reviews/BUILD_RD-03_2026-11-17.md`; the builder's cycle-1 hand-back; RD-03 sections 6, 10.1, 15. |
