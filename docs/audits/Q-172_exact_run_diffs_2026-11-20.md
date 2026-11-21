# Audit: `results/exact_run_diffs.csv` (Q-172, the exact-run difference count), 2026-11-20

**Verdict: clean with caveats.** I re-derived every count in the file from the CSV and its manifest with my own
scripts. I did not import or run `extended/exact_run_diffs.py`, `scripts/exact_run_diffs.py`, `extended/search_cut.py`,
`identity/search_cut_identity.py` or any vendored code, and I read no bar and no atlas parquet. The scripts are in the
session scratchpad, folder `audit172` (`rederive.py`, `u1.py`, `u1b.py`, `daylist.py`). No check failed.

**Licence answer: no.** Nothing in the file or its manifest can be turned back into a licensed price level or range.
The reason is in section 4.

## 1. What was audited

- **File:** `results/exact_run_diffs.csv`, read in place in the main tree. It is untracked.
  - My sha256 equals the manifest's `sha256` (`87e7eb8f…9124`).
  - The file has 16 data rows, equal to the manifest's `rows`. Its columns equal the manifest's `columns`.
  - It is byte-identical to the clean checkout's copy (`%LOCALAPPDATA%\stage2-extended-runs\q172-exact-run-diffs\results\`), and so is the manifest.
- **Manifest:**
  - `script` is `scripts/exact_run_diffs.py`.
  - `git_commit` is `65f6817ebfca54125a2cf14016d7208c7e36830f`, and `git_dirty` is false.
    - That commit is the tip of `wt/wt-user` and of `origin/wt/wt-user`, and no other branch contains it (`git branch -a --contains`).
    - Its parent is `e79213a`, so it is **not on `master`** (caveat C4).
  - `seed` is 20261920. `parameters.seed` gives `denial_seed` 20261920, and the start seed `lockstep.child_seed(20261920, 0, start_day)`.
    - At 65f6817, `user_beside.DENIAL_SEED = SEED_BLOCK[0]`, with `SEED_BLOCK = tuple(range(20261920, 20261930))`.
    - That block was committed in 4da95b4 on 2026-11-15 and is cited in E-024 and E-082. So it was fixed long before this run.
  - `exploratory` is false, `variant_count` 2 (the two responses), `prereg_id` null, `notes` null.
  - `provenance.clean_run` is `q172-exact-run-diffs`, with marker `S2X_CLEAN_RUN`.
  - `timestamp` is `2026-11-20T21:05:04+00:00`. That is when the file was written, not the date of any data.
- **The run log:** the lead's copy (`scratchpad/lead/q172_run.log`) and the log beside the checkout (`stage2-extended-runs\q172-exact-run-diffs.log`).
  - The run took `run.lock`, checked out 65f6817 clean, and linked `vendor/stage2/data/bars` and `data/atlas` as junctions. I confirmed that both are `Junction`s in the checkout.
  - It built the cut at 2022-12-30 (776 days) and at 2023-12-29 (1034 days). Both identities show HELD.
  - It wrote 16 rows, ended with EXIT 0, and released the lock.
  - In the checkout, `git rev-parse HEAD` is 65f6817. `git status --porcelain` shows only the two result files. `results/read_ledger.jsonl` and `results/variants.jsonl` do not differ from HEAD.
- **The specification it was checked against:**
  - `docs/MEASURES.md` section 6, "To run before the held-out runner is declared".
  - E-232, which merged that specification.
  - E-248, the lead's ruling: point arm only, inputs cut at the read, no held-out read row. It narrows section 6's "both of U1's arms".
  - E-211, which merged MEASURES.
  - E-208's blocks, as MEASURES gives them.
  - This is a measurement, not a declared family, so there is no `prereg/F-NN` file, no pinned sha256 and no k.
- **The identities it rests on:** both are in the log and in the manifest's `parameters.identities`.
  - **nested:** P-14's point-arm stream built on the cut at 2022-12-30 equals the one built on the cut at 2023-12-29, block for block, on 776 blocks.
  - **u1_point:** U1's point-arm start rows (`vendor/stage2/results/user_journey.csv`) equal the cut build's on 783 start rows, every column.
  - I checked both counts against U1's file (section 2). I did not re-run either identity.

## 2. The re-derivations

The rule I applied comes from MEASURES section 6 and the manifest's caveat.

- n is `parameters.starts.n_sessions`.
- The **cut** group is the last 252 starts, n − 252 .. n − 1.
- The **control** group is every 21st earlier start, `range(0, n − 252, 21)`.
- A start s has a long run of length L = min(252, n − s). It is **checked** at horizon h when h < L.

| Headline | As reported | My re-derivation | Agrees? |
|---|---|---|---|
| sha256 of the CSV | manifest `sha256` | hashlib on the bytes: equal | yes |
| Rows, sections | manifest `rows` 16 | 16 rows, all `section = checked`. No `moved` rows | yes |
| Design, arm, responses | P-14, `point`, `off` and `denial_25` | `design` p14 and `arm` point on all 16 rows; 4 rows per response × group | yes |
| n, the search sessions | `n_sessions` 1034 | U1's p14 point start rows dated ≤ 2023-12-29: 1034. The bars manifest's `day_list`: 1034 days ≤ 2023-12-29 | yes |
| Nested cut size | log: 776 blocks to 2022-12-30 | U1's p14 point start rows dated ≤ 2022-12-30: 776 | yes |
| Starts chosen | `chosen` 290 | 252 cut (indices 782 to 1033) + 38 control (0, 21, …, 777) = 290 | yes |
| `starts` column | 252 (cut), 38 (control) | the same, at every horizon and response | yes, 16 of 16 |
| `checked`, cut group | 231 / 189 / 162 / 126 at h = 21 / 63 / 90 / 126 | the count of s in 782..1033 with h < 1034 − s: the same | yes, 8 of 8 |
| `checked`, control group | 38 at every h | L = 252 for every control start, so every h is checked: 38 | yes, 8 of 8 |
| `differing` | 0 on every row | ordered 0 ≤ differing ≤ checked ≤ starts on all 16 rows. The total is 0. With no `moved` rows, that is consistent | yes |
| Exact runs compared | — | the sum of `checked` per response: 860 for `off`, 860 for `denial_25` | — |
| `off` against `denial_25` | — | equal on every count | consistent |
| u1_point's 783 rows | log, manifest | the starts with s + 252 ≤ n: 783. All 783 of U1's comparable rows have `observed` 252 | yes |
| `off`: "290 starts (251 run)" in the log | log | the control starts plus start 782 lie inside the u1_point set: 39, and 290 − 39 = 251. So the identity's runs were reused for those 39 starts (C3) | yes |
| U1's own exact-run check on P-14's point arm | — | U1's `identity` row "the long replay's pass, activation and pay days up to h equal those of the run of exactly h sessions…": `compared` 6464, `differing` 0. 6464 equals the sum over h of (1691 − h) with U1's 1691 start rows, which is the same h < L rule. All 20 such rows in U1 have `differing` 0 | consistent |

The control group is exactly U1's setting: every control start's 252-session run ends by 2023-12-29. So for the control
group this file's zero agrees with U1's whole-window zero. The cut group (783 to 1033, whose long run is cut at
2023-12-29) is the new evidence. The cut group holds 708 checks per response (the sum of its `checked` rows). Four of
them belong to start 782, whose run is not cut, so 704 checks are on runs actually cut (from the rule above). None differ.

## 3. Findings, most serious first

**C1. "Nothing read 2024 or later" holds for the data, not for every file the process opened.**

- **The data files were cut at the read.** These are the manifest's `parameters.cut.files`: A1's `days` and `events`, and A3's `walks`, each cut to 2023-12-29.
  - `switched_off` is `{}`. No bars parquet is among the files read, so the bars were never opened.
  - The log's day counts (776 and 1034) equal the counts dated through 2022-12-30 and 2023-12-29 in both U1's start rows and the bars manifest's `day_list`.
  - The reader at 65f6817 fixes `CHOICE_END` at 2023-12-29 and `CONFIRMATION_START` at 2026-07-17.
  - Choice-block reads are not ledgered (E-019; the reader's docstring), and the checkout's ledger is HEAD's.
  - The CSV holds no date.
- **Three reads reached past 2023-12-29:**
  - **The bars manifest's `day_list` was read whole** (`passthrough`). It holds 1691 dates to 2026-07-16, 657 of them after 2023-12-29. These are dates only, with no price; the cut's docstring says `day_list` decides nothing in this build.
  - **The u1_point identity loaded U1's whole-window result file.** U1's p14 point start rows run to 2026-07-16, 657 of them from 2024. The identity drops the rows of later starts in memory, after the file is read. U1 is already on the held-out read ledger (MEASURES: "All three files read the whole development window").
  - **P-14's build reads configuration and result tables chosen on the whole window** (the rung rule, the no-closure table), uncut, as `extended/search_cut.py`'s docstring states.
- **What the cut's record can and cannot show.** The cut guards only `data/bars` and `data/atlas`. So `CutLog` cannot list which result files under `vendor/stage2/results/` were read, and the manifest does not name them.
- **Nothing derived from these reads enters the counts.** The blocks are the cut's, the nested identity held, and the runner's date backstop applies.
- **Nothing from 2026-07-17.** The `day_list` and U1 both end on 2026-07-16.
- **E-248's "no held-out read row" is sound for this file, but should be read with these three reads stated.**

**C2. A zero whose power on real data is not shown.**

- Every `differing` is 0. The comparator is Stage 2's event-day comparison in `user_journey._one_start`.
- No real-data run has ever shown that comparator firing. All 20 of U1's exact-run identity rows have `differing` 0.
- The test `test_a_planted_difference_is_counted` (`tests/test_exact_run_diffs.py` at 65f6817) plants a difference at the counting layer, on synthetic records. It does not make the engine's runs differ.
- The zero is consistent with U1 and plausible for a causal engine. But it is only as strong as the comparator.
- **Recommended before M-2's refusal is relied on as a guard:** a light planted check on a few real starts, with seeds written first. For example, a run truncated or altered so that an event day must move, confirming that `differs` fires. This is a power check, not a rerun of this file.

**C3. Thirty-nine `off` records came from the identity run, and the manifest does not say so.**

- The log says "off: 290 starts (251 run)". The script reuses u1_point's outputs for the chosen starts inside the identity's set: the 38 control starts and start 782.
- The identity's call is the same `run_starts(..., journey=True, journey_block="search")` with the same response.
- The counting refuses a start whose checked horizons are not the rule's, and every control row shows 38 of 38 checked. So the reuse is equivalent.
- But the manifest's `record_read` describes one call for all starts. The reuse should be stated in the manifest.

**C4. The provenance names neither the ruling it follows nor a commit on `master`.**

- The manifest's `decisions` are E-208, E-232 and "MEASURES section 6". `read_row` is E-232.
- E-248, the row that narrows section 6 to the point arm, is not named. MEASURES section 6 at 65f6817 still says "both of U1's arms".
- E-248 is in 3e08316 on `master`, committed at 2026-11-20T07:34:47−10:00. That is before 65f6817 (07:35:41−10:00) and before the run (20:59:57Z). So the narrowing preceded the outcome; this is a gap in the record, not a post-hoc choice.
- 65f6817 is on `wt/wt-user` only. The producing code is not merged, so the merge checklist is owed before this file is cited from `master`.

**C5. The rule for which horizons are checked is in the code's docstring, not in section 6.**

- An h-session run is made only when h < L, so the count at 126 shrinks over the last 126 starts.
- This is declared in `extended/exact_run_diffs.py`'s docstring at 65f6817 and in the manifest's `caveat`.
- It is Stage 2's own rule: U1's `compared` equals the sum over h of (1691 − h).
- When L = h, the long run is itself the exact run, so nothing is lost.
- It is labelled, so it is not exploratory-unlabelled. Every use should say that the 126-session cut count covers 126 starts, not 252.

**C6. No `results/variants.jsonl` line.** The checkout's `variants.jsonl` is byte-identical to the main tree's and holds no Q-172 line. This is the same gap as E-179 C6 and the T7 audit's C6.

**C7. Assumptions to state wherever the count is used.** None of these is in the file.

- P-14's registered configuration: its latency, brackets and fills, as U1 builds it.
- `denial_25` is the denial ladder's 25 % response at the runner's denial seed.
- The point arm only. The verdict arm's count is not measured (E-248).
- The search years only. The count says nothing directly about held-out starts whose long run is cut at 2026-07-16.

**Choices made after an outcome without a label: none found.**

- The horizons (21, 63, 90, 126), the responses (`off`, `denial_25`), the start rule and the record compared all match MEASURES section 6 as merged under E-232.
- The point-arm narrowing is E-248's, dated before the run. Its reason is a provenance one (the verdict arm's bounds pool 2020 to 2026 trades), not an outcome.
- The pre-run `--check` prints no difference count, by the script's docstring, and writes to a temporary folder.
- A search of the worktrees and clean-run folders (depth 4) and the temp folder (depth 3) found no other `exact_run_diffs*` output besides the clean checkout's copy.
- The seeds predate the run by five days.

**The count:** this is not a family, and no k is spent. `variant_count` 2 is the two responses. **Charter measures** (P, the frontier, the long-run gate, growth with ruin beside it) do not apply: the file holds no measure's value, as section 6 requires ("Counts only").

## 4. The licence question (E-179, E-245): no

- Every value in the CSV is one of two things:
  - a label: `section`, `design`, `arm`, `response`, `group`;
  - an integer: `horizon`, `starts`, `checked`, `differing`.
  `event`, `change`, `shift` and `count` are empty on every row. My scan found no other value.
- **Every count is a function of n and h alone.** I reproduced every `starts` and `checked` from n = 1034 and the declared rule, and every `differing` is 0. So the file carries no information about the bars beyond the number of search sessions, which is calendar information.
- **The manifest** adds only calendar counts (`n_sessions`), file names, seeds, timings, memory and identity labels. It has no price, no range, no point value and no date of any event.
- Contrast: Q-121's file gave back the open price from its ranges (E-179), and S1's k values invert to a pooled range quantile in points (E-245). Nothing comparable is here.
- **The file may be committed** on the licence ground, subject to the lead's other checks.

## 5. The failure protocol

No check failed, so no protocol steps were taken.

## 6. What I could not verify, and why

- **That the cut runs' event days are what the engine makes.** I ran no engine, by the rules of this audit. The zero rests on the log, the manifest and the identities, and on its agreement with U1's whole-window zero. C2 is its power gap.
- **Which result and configuration files the build read.** `CutLog` does not cover `vendor/stage2/results/`, and the manifest does not list them (C1).
- **That the reused 39 `off` records were made exactly as the counted runs would have been.** I read this from the code at 65f6817, not from a file.
- **That the identities hold.** I took HELD from the log and the manifest. I re-derived only their row and block counts against U1's file and the bars manifest.
- **That no earlier look at real outcomes happened outside the clean run**, beyond what the files show. A look whose output was deleted leaves no file.
