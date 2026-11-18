# Red team: RD-03's build, corrective cycle 4 (Q-119r5) -- 2026-11-18

**Target.** Branch `wt/wt-payout` at 3d55ad5 (worktree `%LOCALAPPDATA%\stage2-extended-wt\wt-payout`). I read the
cycle-4 diff against 6ef8a4d, the head that cycle 3's note read. The diff from 3fdc1a1, cycle 3's own commit, is the
same diff plus 6ef8a4d's tier marking. Six files changed: `extended/cl_reading.py`, `extended/levers_readings.py` (a
comment), `scripts/cl_reading.py`, `tests/cl_run_check.py`, `tests/cl_synthetic.py` and `tests/test_cl_build.py`.

I then re-read the whole build (15c5042..3d55ad5) against the pinned `prereg/RD-03_contract_levers.md`, which is the
same blob as the branch's `DRAFT_` file, for the items the brief lists. For the merge context I read Q-140 as it
stands on `wt/wt-verify` at 3f6e3bd: 5c67ab6 merges this branch, and 3f6e3bd then merges `wt/wt-firms` at 1c9f34f.
Q-129's vendor extension is not there yet.

I was given no conclusion to confirm; the brief asked only for a verdict and findings.

**What I ran.** All of it was light and static. `run.lock` was held by `f03-t3`, with about 0.4 GB free, so nothing
loaded the engine.

- `git archive` exports of 3f6e3bd and of master c2aa709 into my scratchpad. On each I ran:
  - `tests/test_heavy_marker_guard.py`'s own scan (`python -I`, AST only);
  - the seed-derivation guard's `derivations()` over every file RD-03 adds or touches.
- A YAML comparison of `config/rules_extended.yaml` at deb45ad, 1c9f34f, 3f6e3bd and master.
- A probe of `stage0_commit`, `fit_commit_problem` and `stage0_stopped_problems`. I lifted the functions by AST from
  the branch's `extended/cl_reading.py` and did not import the module. The probe ran on E-172's real line and on
  constructed rows.

No toy section (t3, t3b, t3trip, t17) was run, because of the memory. No file under `vendor/`, `results/` or any
worktree was written. This note is the only write.

---

## Verdict

**The code: merge after B1.** B1 is fixed in the Q-140 merge commit, and no RD-03 code changes.

**The declaration: stands with readings.** These are cycle 3's readings; nothing in cycle 4 touches a declared rule.

- Cycle 3's m1-m5 and notes 1-3 are closed in the code (section 2). Two of them leave a residual:
  - m2's fixed place can still pick the wrong commit on some row wordings (S1);
  - m5's beside shift test omits two of step 4's combinations (S2).

  Both residuals guard steps that are not live yet: stage 0 is stopped, and step 4 comes after step 3.
- **B1 blocks the merge as it is composed.** On the merged tree, the fast tier's heavy-marker guard fails on two of
  RD-03's tests. On master alone the guard passes. Two `LIGHT` entries fix it, and I checked them on a scratch copy.
- **What the merge changes that RD-03 depends on** (section 3):
  - **`config/rules_extended.yaml`: yes.** RD-03 loads six Back2Funded and No-Activation-Fee keys from it. The merge
    brings those keys with the same values, statuses and dates as deb45ad, the source RD-03 has used so far. Once
    merged, the runner's "Q-115 merged" wait lifts.
  - **`config/` as a whole, and Q-129's change to `vendor/MANIFEST_stage2.sha256`:** both are in every identity
    cover's `BASE`. So every identity must be held again after the merge, as E-156 and E-172 intend.
  - **Vendored files:** RD-03 reads none of the files Q-129 adds, and no vendored source it hash-guards changes.

---

## 1. Findings

### Blocker

**B1. On the merged tree, `test_every_test_reaching_the_data_is_heavy` fails on two RD-03 tests. It is in the fast
tier, so the merged tree's commit hook will fail.**

- **Where.**
  - On the branch: `tests/test_cl_build.py`'s `test_starts_is_the_synthetic_window_measurements_only` (cycle 3) and
    `test_stage0_stopped_is_refused_beside_a_stage0_file_or_without_its_row` (cycle 4).
  - The guard is master's `tests/test_heavy_marker_guard.py` (Q-134, E-194). It postdates the branch base, so the
    branch has never run it.
- **Evidence.**
  - The guard's scan on the 3f6e3bd export reports "2 without `heavy` and not allowed". Both offenders are the tests
    above.
  - Each spawns `scripts/cl_reading.py`. That script's source calls `authorise_engine_read(`, so the scan counts it
    as a runner that reads the data, and no `LIGHT` mode is declared for it. The argv the scan sees:
    - `--step 3 --synthetic ... --starts 5`;
    - `--step 4 --starts 5`;
    - `--step 5 --starts 5 --after E-001`;
    - `--step 4 --synthetic ... --starts 0`;
    - `--step 3 --synthetic ... --days 20 --stage0-stopped [--stage0-row E-172]`.
  - The same scan on master c2aa709 reports 0. So the failure comes from the merge, not from master.
  - The tests themselves read no data:
    - the non-synthetic `--starts` cases are refused by `starts_problem` before any import (`scripts/cl_reading.py`
      215-219);
    - the synthetic cases run toy inputs into a temporary folder. `SI.engine_files` (line 232) only builds paths.
  - `git merge` without a conflict does not run the pre-commit hook. That is how 5c67ab6 and 3f6e3bd were committed
    with the failure in them.
- **Failure it allows.** The next commit on the merged tree is refused by the hook. Or someone marks the two tests
  `heavy` to get past it. Then the lock guard would skip them under every heavy run, and the `--starts` and
  `--stage0-stopped` refusals would lose their only runner-level tests.
- **Remedy.** In the Q-140 merge, add `"scripts/cl_reading.py"` to `LIGHT` with two modes:
  - `(("--synthetic",), "toy campaigns into a temporary --results-dir; no bar or walk read")`;
  - `(("--starts", "!--synthetic"), "refused by starts_problem at argument parsing, before any import or read")`.

  I added exactly these two entries to my scratch copy of the merged guard and re-ran its scan. The result was 0
  offenders, with both modes in use, so neither is stale. Then run the guard's pytest on the merged tree before
  pushing.

### Should-fix

These do not block the merge; each is owed before the step it guards.

**S1. m2's "fixed place" is the first backticked hex after the first "stage 0". Two wordings defeat it. This is owed
before any `results/cl_fit.csv` is read.**

- **Where.** `extended/cl_reading.py`, `STAGE0_WORDS`, `BACKTICKED_HEX` and `stage0_commit` (cycle-4 lines
  1070-1093).
- **Evidence** (my probe, the branch's functions on constructed rows):
  - `... Q-129 lands (it unblocks stage 0) at \`A\`; stage 0 (cl_fit) from a clean checkout of \`B\` ...` holds A.
  - `... stage 0 (cl_fit): its brief at \`A\`, run from a clean checkout of \`B\` ...` holds A and refuses B.
  - A row in the lead's habitual style is refused. In that style the commit is not backticked (as in "a clean
    checkout of 4b72ef2" in E-177), and the result file's sha256 is backticked at 64 characters, which does not match.
    This case fails closed.
  - E-172 has no backticked commit after "stage 0". It is the stop row, so this does not matter there.
- **Failure it allows.** Take a stage-0 row that names a superseded run or the brief's commit before the run's own.
  The guard holds `cl_fit.csv` to that other commit. Cycle-3 m2 named exactly this case, and the m7 no-overwrite rule
  makes it unlikely, not impossible. The t17 two-commit case passes only because its run's commit comes first.
- **Remedy.**
  - Use an unmistakable token, for example `cl_fit@<hex>`, and refuse a row with none or with two.
  - At the least, refuse a row with a second backticked 7-to-40-hex token after "stage 0".
  - Write the form into stage 0's brief and the merge row, so the lead writes the stage-0 row to it.

**S2. m5's beside shift test (`t3b`) leaves out the denial responses and Back2Funded under `rtp`. This is owed before
step 4 runs.**

- **Where.** `tests/cl_synthetic.py` `_t3b_specs`. It runs (ref, `rtp`), (ref, an FTP model), and (b2f2, that FTP
  model) under both U-6 variants.
- **What step 4 runs.** `cl_reading.LADDER`: `denial_10`, `denial_25`, `denial_50` and `rtp`, on every cell
  (`beside_runs("ladder")`).
- **Evidence.**
  - Three of step 4's four responses have no early-block shift test.
  - The one combination where a lever's reading depends on the placement state, U-5 (no reactivation while a
    placement is in force, `LeverState.reactivate` 399-402), is never shifted: b2f2 is run only under the FTP model,
    not under `rtp`.
  - Cycle-3 m5 named "a denial draw that is not path-causal" as the risk. The risk is low, because each start's
    denial seed is its own child and its draws are consumed in path order (`user_beside.start_seed`). But nothing
    shows it.
- **Failure it allows.** A denial or placement path that reads past an early start's window would pass every test
  before step 4's run.
- **Remedy.**
  - Add (ref, `denial_50`) and (b2f2, `rtp`) to `_t3b_specs`. That is two more one-cell toy jobs per plant, a few
    minutes in the slow tier.
  - Extend `covered` to require them.

**S3. The record loader keys a multi-firm record by `key` alone, and the last entry wins.**

- **Where.** `extended/levers_terms.py` 89-90:

  ```python
  out = {str(e["key"]): e for e in doc["rules"]}
  ```

- **Evidence.**
  - After the merge the record holds 311 entries across eight firms: Q-136 adds `mffu` and grows `topstep`'s entries.
  - Today no key is duplicated, at deb45ad, at 1c9f34f or at master. All of RD-03's keys are `firm: topstep`.
  - No test holds the record's keys unique (grep over the merged tests and `extended/`).
- **Failure it allows.** A later record row with the same key for another firm or plan would silently replace
  Back2Funded's price or window. The shared identities run with the levers off, so none of them would notice.
- **Remedy.**
  - Refuse a duplicate key in `_record`, or select `firm == "topstep"` for `RECORD_KEYS`.
  - Add a fast test that the record's keys are unique. That fits the merge with the record, or wt-firms.

### Notes

1. **m1 is a labelled NaN, not a refusal.**
   - In the real window, block `all` always holds full-year starts, so an empty set there can only mean a defect. A
     refusal in the real run would be stricter and cheap. A typical defect would be a `counts` key that misses
     `start_day`.
   - `cl_run_check` runs only at `--days 70`, so its finite branch (`>= 252`) never executes.
   - Its menu check (`per_year_note` non-empty beside a NaN) holds by construction: `menu_table` always supplies a
     fallback string. Asserting that each beside menu row with a mechanics row carries `NO_FULL_YEAR`'s reason would
     give it teeth.
   - The finite branch on the real replay structure is tested only by t17's hand-built run. The same key convention
     is exercised by step 3's `mechanics_rows` in T-3 (slow) and by `before_binding_problems`' refusal.
2. **The fast tripwire (`t3trip`) has two blind spots.**
   - It runs `ref` with the levers off, so it watches the reading's purge and aggregation, not A-1's lever lines.
   - Its leak check is at h = 63 only, so a leak confined to the 21-session reading is invisible to it.

   That is what cycle 3 asked for, and the slow T-3 covers both. Running b2f2 beside `ref` would put a lever on
   every commit for about a minute more.
3. **m3's checks are substring checks.**
   - `"stage 0 is stopped"` is matched by substring, so a negated sentence passes (probe: "it is not true that Stage
     0 is stopped" is accepted).
   - `cl_fit` is satisfied by `cl_fit_identity`, which E-183 accepted.

   The lead writes the rows, so this is a note.
4. **The manifest's seed descriptions are typed strings** (`scripts/cl_reading.py` 341-343, pre-existing). They are
   not built from the constants the draws use (`user_beside.SEED_BLOCK[0]`, `START_KIND`, the registered gate calls).
   They match today, but they can drift silently. Build them from the constants.
5. **The horizon is typed as 252** beside `U.HORIZON`:
   - in `mechanics_rows` (`block_days(..., 252)`, `h=252`);
   - in `mechanics_rows_beside` (`h=252`, while the filter reads `U.HORIZON`);
   - in `cl_run_check` (`int(DAYS) < 252`).

   It is consistent today. Use the one constant.
6. **`pyproject.toml`'s `slow` marker still says "about a minute"** (cycle-3 m4's third remedy, for the lead). It is
   unchanged on master too.
7. **A partial tautology in t17.** `stage0_commit(dec) == (None, stage0_commit(dec)[1])` only tests that the first
   element is None. The `"decimal" in ...` clause beside it carries the check.

---

## 2. Cycle 3's minors, in the code

| item | closed? | where | its test can fail? |
|---|---|---|---|
| m1 | yes. The tautological `year_problems` call is dropped. With no full-year start the row is NaN, `n = 0`, its note starting `NO_FULL_YEAR`; the menu's `per_year_note` gives the reason | `cl_reading.py` 1599-1610, 946-948 | t17 holds the rate to the full-year starts' mean, with n their count, and checks the label when there are none. `cl_run_check` asserts NaN plus the label at 70 days. Residual: note 1 |
| m2 | as E-174 ruled: one token, in a fixed place, decimal-only refused | 1070-1109 | t17: two commits, a commit before "stage 0", decimal, unbackticked, no "stage 0", six characters. Residual: S1 |
| m3 | yes. Refused with stage 0's file present, without `--stage0-row`, and in the real run unless the row has `cl_fit` and the stop phrase (case-insensitive) | `cl_reading.py` 1112-1133; `scripts/cl_reading.py` 382-388 | t17 has a case per refusal and the stop line on exactly the L-B and L-N rows; the runner's two synthetic refusals (exit 3, nothing written). My probe: E-172's real line passes |
| m4 | yes: `t3trip` in the fast tier. T-3's no-leak claim on `ref` under the losses plant, the reach checked, the purge leak required to move a row at 63 | `cl_synthetic.py` t3trip; `test_cl_build.py` | `test_the_tripwire_reads_its_horizon` requires a non-empty catch. Its scope: note 2 |
| m5 | in part: `t3b` (slow) runs `rtp`, an FTP model, and b2f2 in both U-6 variants; no-leak under both plants; the purge leak caught at 63 and 252 | `cl_synthetic.py` t3b | `covered` requires `rtp`, the FTP model and the counted mode. Missing: S2 |
| note 1 | yes: `<tag>_ROWS_<FORM>_<h>` per plant | `t3_leaks` | -- |
| note 2 | yes: a plant whose reading refuses is not counted as moved in the purge form | `t3_leaks` | -- |
| note 3 | yes: 10.1 item 8's wording recorded as governing | `levers_readings.py` 37-38, `cl_reading.py` 811-813 | -- |

## 3. What the merge changes that RD-03 depends on

- **`config/rules_extended.yaml`, a dependency.** `levers_terms.RECORD_KEYS` are read from the working record. While
  any of them is missing, they are read from deb45ad, and the real run refuses (`scripts/cl_reading.py` 261-263).
  - At 1c9f34f and 3f6e3bd:
    - the six keys are present, `verified` and numeric;
    - the six `NEVER_LOADED["record"]` keys are present, and the loader refuses them by name whatever their status;
    - no deb45ad entry changed and none was removed;
    - none of master's 123 entries changed;
    - no key is duplicated.
  - So the merge changes no value RD-03 reads. It turns `record.sources` in the manifests from `deb45ad (not merged)`
    to `record`, and lifts the wait.
  - Separate risk: S3.
- **`config/` whole, and `vendor/MANIFEST_stage2.sha256` once Q-129 lands.** Both are in `identity_cover.BASE`, so
  every shared identity, A0, RD-02's own and RD-03's `cl_identity` / `cl_t10w2` must be held again at the merged
  commit. This is E-156's plan. `cl_identity` has never been held, so nothing of RD-03's is voided.
- **Q-129's four added files** (v12's two rung files and D-559's two). RD-03 reads none of them: stage 0 is unbuilt
  and `identity/cl_fit_identity.py` is not written.
  - A-1's guard hashes the vendored lockstep functions' source (`levers_path.check_vendored_source`). T-15 pins
    `user_beside.py` and `gate.py` at 15c5042. Neither guard is touched if Q-129 only adds files from the same
    snapshot commit.
  - The merge should still confirm that Q-129 adds manifest lines and changes no existing line.
  - `vendor/DATA_MANIFEST_stage2.sha256`, whose sha256 RD-03's manifests record, should be unchanged by Q-129.
- **Drift from master since the branch base.** None in any file RD-03 edits or imports (`git diff 15c5042 c2aa709` on
  user_beside, gate, campaign, identity_cover, pp_reading, test_rd03_draft, pp_run, reader, results, identity_tokens,
  replay_records and payout_policy: empty). The merged tree's copies of RD-03's files equal 3d55ad5's.

## What I tried that found nothing

- **Look-ahead in cycle 4.**
  - The diff adds labels, guards and tests only; no computation reads a session.
  - In the whole build, A-1's 57 marked lines and `LeverState`:
    - every decision is taken at the day's close from state at that close: the breach evening, the window by
      `elapsed` on the replay's own dates, and the placement in force now;
    - no forward index;
    - `horizon_days` sizes arrays only.
  - The honesty labels on early paired rows depend on (h, n_w) only (`pp_run.label_rows`, `honesty_table`), not on
    late data.
- **Judged block and NQ from 2026-07-17.**
  - The real run authorises `CHOICE_START..JUDGED_END` only, and the reader refuses 2026-07-17 on.
  - The tests' toys are synthetic. Their late block is synthetic sessions dated from 2024-01-02.
- **Seeds.**
  - The seed-derivation guard finds no additive derivation in any RD-03 file.
  - The only literal of RD-03's block is `TOY_SEED` in `tests/cl_synthetic.py`. It is a declared use (section 12),
    held to the declaration by T-6 and allowed by T-0.
  - `t3trip` and `t3b` draw only from it, through `toy_job` and `toy(5, i)`, as T-3's synthetic late block.
  - `git grep` of RD-03's block over the merged tree finds only the declaration and those two test files.
  - The real run reads its honesty seed from the pinned text under its pin.
- **Typed rule values.** None added in cycle 4. Prices, limits and windows still come through `levers_terms` from the
  record or Stage 2's ledger.
- **Picking.** Nothing in cycle 4 orders, filters or selects cells. `per_year_note` is text beside a number.
- **The declaration.** The branch's `DRAFT_` file and master's pinned file are the same git blob, and the LF sha256
  is the one E-152 pins.

## What I could not check

- I ran none of t3trip, t3b, t17, t14 or `cl_run_check`, because of the memory under `f03-t3`'s lock. So E-183's
  claims are taken as read: each new check fails with its fix undone; t3trip takes about two minutes; and the fast tier
  fits its limit. The cheapest confirmation, once the lock is free, is to run `t3trip` and `t17` alone, each under
  `timeout 1800`.
- The full suite on the merged tree, including `tests/test_identity_cover.py`'s closure check, which needs `vendor/`.
- Q-129 itself (not yet prepared) and Q-140's final composition.
- Stage 0 and anything on the registered data.

---

## Proposed row

| E-NNN | 2026-11-18 | **The red team's read of RD-03's corrective cycle 4 (Q-119r5; wt/wt-payout 6ef8a4d..3d55ad5, the whole build against the pin, and the Q-140 merge as composed on wt/wt-verify 3f6e3bd; `docs/reviews/BUILD_RD-03_cycle4_2026-11-18.md`): RD-03's code merges; the merge is blocked by one item fixed in the merge commit; the declaration stands with readings.** **Closed:** cycle 3's m1, m2 (as E-174 ruled), m3, m4 and notes 1-3 in the code, each with a test that can fail; m5 in part. **Blocker (B1):** on the merged tree the fast-tier heavy-marker guard (Q-134) fails on two RD-03 tests that spawn `scripts/cl_reading.py` (the `--starts` refusals and the `--stage0-stopped` refusals); master alone passes; remedy: two `LIGHT` modes for `scripts/cl_reading.py` (`--synthetic`; `--starts` without `--synthetic`), shown to clear the scan on a scratch copy. **Should-fix:** (S1) before any `cl_fit.csv` is read, the stage-0 commit token made unmistakable (for example `cl_fit@<hex>`, refusing none or two), since the first backticked hex after the first "stage 0" can be a brief's or a superseded commit; (S2) before step 4, `t3b` extended to a denial response and to b2f2 under `rtp` (U-5); (S3) the record loader refusing duplicate keys, or selecting Topstep's, with a uniqueness test, the record now holding eight firms. **Dependencies:** RD-03 reads six keys of `config/rules_extended.yaml`; the merge brings them unchanged from deb45ad and lifts the Q-115 wait; `config/` and Q-129's manifest change void every identity cover, as planned; RD-03 reads none of Q-129's files, and A-1's and T-15's hash guards are untouched if Q-129 only adds lines. **Notes:** the labelled NaN instead of a real-run refusal; the tripwire watching `ref` only, at 63; the stop phrase read by substring; the manifest's typed seed strings; the horizon typed as 252 beside `U.HORIZON`. | The red team's note; E-156, E-172, E-174, E-183, E-194. |
