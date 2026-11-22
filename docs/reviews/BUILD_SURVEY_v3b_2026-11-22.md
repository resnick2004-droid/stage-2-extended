# Red team: the survey runner v3's pre-pin fixes, diff check (Q-186; wt/wt-survey 5c5cb93)

Target: `git diff fcf3447 5c5cb93 -- extended/survey.py scripts/survey_run.py tests/survey_world.py tests/test_survey.py`
(+985 / -104; the master merge 4e8fa87 skipped). It answers BUILD_SURVEY_v3 (M-1, m-1 to m-7, n-1, n-5). Line numbers
are 5c5cb93's. W42-R1 is read at `wt/wt-infra` 01e896a (`extended/wave42.py`, `scripts/wave42_apply.py`), which the
branch does not yet carry.

**On the brief.** The brief says data containment should allow "only `vendor/stage2/data/bars` and `data/atlas`" as
links. I did not take that layout as given. I checked it against `scripts/worktrees.py` and the real checkouts, and it
is wrong for the atlas (F-1).

**How it was run.** Nothing was written in the worker's tree. All mutation was done in a detached clone at
`%LOCALAPPDATA%\stage2-extended-runs\rt-survey-5c5cb93` (`git clone --shared`, then `checkout --detach 5c5cb93`),
which was removed at the end. `OMP_NUM_THREADS=1` throughout.
- The suite, once, unmutated, in the clone: `timeout 1500 python -m pytest -q -o addopts= -p no:cacheprovider
  tests/test_survey.py`. Result: **100 passed in 1194.44 s**.
- Mutants (`scratchpad/rtmut/test_rtmut.py`). Nineteen one-line edits of my own, recompiled in the module's namespace
  (the worker's `_edit` form). Each was run against the scenarios it should trip. The ten that survived were then
  applied together to the suite's non-scenario tests that touch the new guards (`scratchpad/rtmut/rtplugin.py`).
- Probes, all synthetic, all in `scratchpad/`:
  - `jprobe.py`, `jprobe2.py`: path metadata only (`lexists` / `isjunction`) on the real checkouts. Every name
    probed under the stores is a non-existent file, so no store file was opened.
  - `jprobe3.py`: a temporary root with real `mklink /J` junctions to synthetic files, covering 8.3 names, a trailing
    dot, a hard link and a file symlink. Removed at the end.
  - `p3_rows.py`: the row matchers.
  - `p4_commit.py`: W42-R1's `commit_problem`, from its source at 01e896a, and the survey's provenance check, on
    a fabricated commit.
  - `p5_race.py`: two processes calling `record_once` on one synthetic record.
- No bar, atlas, held-out date or NQ from 2026-07-17 was read.

## Verdict: **BLOCK** (one material finding; every fix is small and can be made before the pin)

**Counts:** 0 changes-a-conclusion, 1 material, 5 minor, 6 notes.

- **F-1 (MATERIAL): M-1 is fixed for the bars but not for the atlas.** `DATA_LINKS` names `data/atlas`. Every
  checkout's atlas junction is at `vendor/stage2/data/atlas`. So a runner that reads the atlas cannot bind it, which
  is the failure M-1 was raised for. The test builds the junction at the wrong place, so it passes. It is a one-line
  fix, plus a test that ties the constant to `worktrees.STORES`.
- **Answered as asked:** m-1 (the floor), n-1 (`limit_check`, `LimitDisagrees`), n-5 and the token half of m-6.
- **Partly answered:** m-2 (the boundaries), m-3 (provenance), m-4 (the invocation), m-5 (the once-record) and m-7.
  Each leaves a residue with a concrete input (F-2 to F-6).

| BUILD_SURVEY_v3 finding | status at 5c5cb93 |
|---|---|
| M-1 data containment | **bars answered, atlas not** (F-1). The report now equals the declaration both ways (answered). |
| m-1 the floor's comparator | answered (n-d) |
| m-2 the rows' numbers | partly answered: the margin may be any number after the name (F-3) |
| m-3 the values' provenance | partly answered: a sidecar with pin == head passes for any 40-hex string (F-2) |
| m-4 binding and invocation | answered as asked. What remains needs a deliberate act (n-c). |
| m-5 a second run | partly answered: the check and the append race, and the path follows an environment variable (F-4) |
| m-6 the fixture token | the token is answered. A fixture preview of a real declaration on real parts is still unrecorded (F-5). |
| m-7 the seven survivors | answered: all seven are killed. Ten new survivors on the new guards (F-6). |
| n-1 `limit_check` | answered (n-e) |
| n-5 a malformed sidecar | answered (`_sidecar`, `test_a_malformed_sidecar_refuses_as_the_spec`) |

## Findings

### F-1 (MATERIAL). The atlas's junction is `vendor/stage2/data/atlas`, not `data/atlas`: M-1 is still open for the atlas

**Where:**
- `extended/survey.py:129`: `DATA_LINKS = ("vendor/stage2/data/bars", "data/atlas")`.
- The docstring at `:22-25` says the same.
- `tests/test_survey.py:616-649` (`sc_data_junction`) makes its junctions at `root / "data/atlas"` (`:626`).

**Evidence:**
- `scripts/worktrees.py:28` reads `STORES = ("vendor/stage2/data/bars", "vendor/stage2/data/atlas")`.
  `scripts/run_clean.py` links and unlinks `W.STORES` (`create`, `remove`).
- `jprobe.py`, run on the worker's tree, the clean checkout `q197-cal` and the main tree, found the same layout in
  all three:
  - `vendor/stage2/data/bars` and `vendor/stage2/data/atlas` are junctions in both checkouts;
  - `data/` does not exist in any of them.
- `jprobe2.py`, `data_path_problem` against the worker's tree on non-existent file names:
  - `vendor/stage2/data/bars/<f>` is `None` (passes);
  - `vendor/stage2/data/atlas/<f>` is refused: "passes through the link vendor/stage2/data/atlas";
  - `data/atlas/<f>` is `None`, though no such path exists.
- Mutant `data-links-real-layout` sets `DATA_LINKS` to the real layout. It **fails** `sc_data_junction`, so the
  scenario passes only on the wrong layout.

**The failure it allows:**
- A runner that reads the atlas cannot declare an atlas file: `check_data` refuses it under a pin.
- Since F-1 of v3 made the report equal the declaration, it cannot report the atlas either.
- So it either cannot run, or it reads the atlas without declaring or reporting it. In the second case the atlas is
  bound by nothing, and a re-vendored atlas runs with every binding equal. That is M-1's original failure, for the
  atlas.
- `data/atlas` is admitted as a link although no checkout has one. That part is harmless, because the content is
  still checked by sha256.

**Remedy:**
- Make `DATA_LINKS` equal to `worktrees.STORES`: import it by path, as `archive_queue` loads `status.py`, or keep the
  literal and add a test asserting equality with `scripts/worktrees.py`'s `STORES`.
- Move `sc_data_junction`'s second junction to `vendor/stage2/data/atlas`. Keep the refusal of a junction at
  `vendor/stage2/data` above them, in place of the `data` case.
- Fix the docstring at `:22-25`.

### F-2 (MINOR). The values' provenance passes any sidecar whose `pinned_commit` equals its `git_commit`, even a commit that does not exist

**Where:** `survey.py:951-974` hands `(pin, head)` from the sidecar to `wave42_apply.commit_problem`. At 01e896a,
`scripts/wave42_apply.py:133-134` returns `None` as soon as `head == pin`, before any git call.

**Evidence** (`p4_commit.py`):
- `commit_problem(CO, "f"*40, head="f"*40)` returns `None`.
- `git cat-file -e ffff...^{commit}` fails: there is no such commit.
- `values_provenance_problems({"git_commit": "f"*40, "parameters": {"pinned_commit": "f"*40}}, ...)` returns `[]`.

The survey also never compares the sidecar's `pinned_commit` with this checkout's `config/w42_r1_pin.json`
(`wave42_apply.pinned_commit(ROOT)`).

**The failure it allows:**
- The sidecar is not bound by the values row, which pins only the CSV's sha256. So a values CSV written by `apply()`
  from an unpinned or dirty tree passes once its sidecar carries `pinned_commit == git_commit`. That needs a commit,
  since the tree must be clean, but no other check.
- So does a values file written under an earlier W42-R1 pin.

m-3's check is then empty in exactly the case it was written for: a self-consistent sidecar.

**Remedy.** Under a pin, require all three:
- `pin == apply.pinned_commit(ROOT)`;
- `git cat-file -e <head>^{commit}` succeeds;
- `git merge-base --is-ancestor <head> HEAD` succeeds: the values were written at an ancestor of the run.

Test each with a fabricated sha, and with a pin that differs from `PIN_FILE`.

### F-3 (MINOR). The margin's row passes on any matching number after the name, a negative one included

**Where:** `survey.py:775-779`: `no[-_ ]harm[-_ ]margin.*?(?<![\d.])0\.005(?!\d)`.

**Evidence** (`p3_rows.py`). Each of these rows is **accepted** for a margin of 0.005:
- "the no-harm margin is 0.0055 (was 0.005 in the draft)". This is m-2's own typo case, back again whenever 0.005
  appears later in the row.
- "the no-harm margin is 0.02; the stop at 0.005 points"
- "the no-harm margin is -0.005"
- "... 0.005e-3"
- "... 0.005%"
- "no harm margin: not 0.005 (rejected)"

For a margin of 0.0, "0.0.5" and "0.0,05" are accepted.

The other way round, it fails closed: "0.0050", "5e-3" and ".005" are refused for 0.005, and "0.00005" for 5e-05.

The values row:
- "W42-R10" passes the `W42_RULE in line` substring test;
- so do "old_w42_r1_values.csv.bak" and a rejection note.

These are harmless beside a 64-hex sha.

**The failure it allows:** a declaration whose margin differs from the lead's number passes the row check, provided
its number appears anywhere after the name. That includes a sign flip of the number the lead wrote.

**Remedy:**
- Take the first numeric token after the name, matched in full: `[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?%?`.
- Refuse a sign or a percent sign, and require `float(token) == margin`. This also stops the fail-closed misses.
- For the values row, match `W42-R1(?!\d)` and `(?<![\w.])w42_r1_values\.csv(?![\w.])`.
- Add these rows to `sc_margin_exact`, and the mutant `margin-lookbehind` (F-6).

### F-4 (MINOR). The once-record: the check and the append race, and the path follows `LOCALAPPDATA`

**Where:**
- `survey.py:866-875` (`record_once`: read, check, then `open(..., "a")`).
- `:131` `ONCE_FILE = Path(RUNS_DIR) / ...`, with `RUNS_DIR` taken from `os.environ["LOCALAPPDATA"]`
  (`extended/__init__.py:23`).
- `check_process` (`:540-567`) does not require `run.lock`.

**Evidence:**
- **The race** (`p5_race.py`): two processes released by a barrier into `record_once` for one declaration. In **7 of
  15** trials both appended.
- **The path:** `run_clean.py` computes its checkout folder from the same variable, so `_clean_run`'s
  `RUNS_DIR / name` test agrees. A run started with another `LOCALAPPDATA` therefore passes every check against a
  fresh, empty record.
- **Deletion:** deleting the file allows a second run. No local check can stop that.
- **Answered:** a refusal after the append still counts, and `sc_once` tests it. A different spelling of the path is
  harmless (NTFS ignores case), and a checkout named `survey_once.jsonl` cannot be removed by `run_clean --remove`,
  which goes through `git worktree remove`.

**The failure it allows:** two runs of one pinned declaration, each with its own finalists:
- started together, for example a double launch, or two checkouts without `--hours`, since the lock is optional
  for `run_clean`;
- or started under another `LOCALAPPDATA`.

**What the design should defend:**
- The race and the path: yes, and both are cheap.
- Deletion: no. It is a deliberate act and a conduct matter. It can only be made visible.

**Remedy:**
- Before the first cell, create one marker per declaration, `survey_once/<sha>.json`, with
  `os.open(..., O_CREAT | O_EXCL)`. That is atomic, so no race. Keep the jsonl as the log.
- Take the folder from the Windows known folder (`SHGetKnownFolderPath(FOLDERID_LocalAppData)`), or refuse when it
  differs from `LOCALAPPDATA`.
- Under a pin, require `S2X_LOCK_HOLDER` to name `run.lock`'s current job.
- For deletion, have the survey print its once-line. The lead's row recording it is the durable copy, and
  `check_once` already scans the log.

### F-5 (MINOR; the half of v3 m-6 still open). A fixture-pinned preview of a real declaration, on real parts and W42-R1's real values, is counted and recorded nowhere

**Where:**
- `survey.py:737-746`: a fixture pin refuses only a declaration under `prereg/` and a `results` folder.
- `:378-387`: `build_part` admits `extended.` parts under a fixture pin.
- `:1731`: there is no once-record unless one is injected.

**Evidence:** `ROOT` defaults to the real tree. So the following runs the real search on the search years:
`run_survey(<a copy of the declaration outside prereg/>, results_dir=<tmp>,
pin_fixture=fixture_pin(<copy>))`, called in process in the main tree. It uses the real W42-R1 values and the real
parts. Its cells go only to `<tmp>/variants.jsonl`.

The token's prefix now stops an accidental paste (answered). But the run is deterministic, so the preview's list sha
is the pinned run's.

**The failure it allows:**
- The outcome can be seen before the declaration is pinned. A declaration can be tuned on it, and so can the choice
  between draft declarations.
- None of those cells is counted ("Count every cell").
- The held-out test is not biased by this, because it reads separate years. So it is MINOR.

**Remedy:**
- Under a fixture pin, refuse any part whose module starts with `extended.`. The suite's parts are all
  `survey_world:` (`tests/survey_world.py:383-387`), so nothing breaks.
- Or refuse a fixture pin when `ROOT/results/w42_r1_values.csv`'s sha256 is carried by a decision row.

### F-6 (MINOR). Ten one-line mutants of the new guards survive

Every mutant below **survived** the scenario it targets. The eight function edits and the shortened `INVOCATION_ENV`
were also applied together to nine of the suite's non-scenario tests:
- `test_under_a_pin_the_process_is_checked`
- `test_the_rows_are_checked`
- `test_a_second_run_refuses`
- `test_every_cell_is_counted_and_carries_its_protocol`
- `test_the_new_guards_are_in_the_suite_counts`
- `test_a_fixture_runs_token_is_refused_by_rule_1`
- `test_data_and_the_space_digest_are_bound`
- `test_a_refusal_after_the_first_cell_writes_variants_first`
- `test_the_invocation_in_real_processes`

Eight passed.

The one failure was `test_the_invocation_in_real_processes`, and it was an artefact of how I ran it. I loaded the
plugin through `PYTHONPATH`. With the shortened tuple, the test's own environment filter (`:1603`) passed
`PYTHONPATH` on to the child, whose unmutated check flagged it. On this machine `PYTHONPATH` is unset, so that test
cannot see the mutant either. The test checks only `PYTHONSTARTUP` (`:1619`).

| mutant | where | why nothing sees it |
|---|---|---|
| `margin-lookbehind`: `(?<![\d.])` dropped | `:778` | no row has the name followed by "10.005" |
| `values-lookbehind`: `(?<![0-9a-f])` dropped | `:785` | only a hex suffix is tested (`sha + "e"`), never a prefix |
| `env-tuple-short`: `PYTHONPATH` dropped from `INVOCATION_ENV` | `:133` | `sc_invocation` iterates `SV.INVOCATION_ENV` itself (`test_survey.py:719`) |
| `w42-script-unbound`: `W42_SCRIPT: None` | `:371` | `sc_driver_bound` checks only that the key exists (`test_survey.py:728`) |
| `prov-pin-prefix`, `prov-head-prefix`: `fullmatch` changed to `match` | `:961`, `:963` | only 39-hex strings are tested. With F-2, a 41-hex pin equal to its head passes. |
| `once-recheck-dropped`: the re-check inside `record_once` | `:869` | the early check covers it. Only a race (F-4) shows the difference. |
| `once-resolved-only`: the lexical half dropped | `:852` | no test makes a record path that lies inside the checkout only by its unresolved path |
| `limit-estimate-unchecked`, `limit-inside-unchecked`: either half of the `LimitDisagrees` test | `:1402` | correct code never disagrees, and no test uses a stand-in `limit_check` that does |

These were killed:
- `data-backslash`, `data-islink-only` and `data-report-keys`;
- `inv-decl-unchecked`;
- `floor-sign` and `floor-eps-from-zero`;
- `values-lookahead`;
- `token-fixture-keeps-real-prefix`;
- the seven survivors of v3, now in `MUTANTS`.

**Remedy:**
- One case for each surviving mutant: "no-harm margin 10.005"; `"a" + sha`; the literal tuple
  `("PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONPATH")` in the test; `oc[W42_SCRIPT] == lf(...)` once the script is in
  the tree; 41 hex; F-4's marker; the junction case.
- For the `LimitDisagrees` pair, a stand-in `W.limit_check` that returns `estimate + 1e-12`, and one with `inside`
  flipped, each expecting `LimitDisagrees`.
- Add each mutant to `MUTANTS`.

### Notes

- **n-a (M-1, path forms tried).** Everything else in the M-1 path check holds (`jprobe2.py`, `jprobe3.py`):
  - **Refused:** backslashes, `\\?\`, UNC and `//`, `C:x`, absolute paths, `..`, `.` and empty components; case
    variants of the stores (they fail closed); a trailing dot or space on a junction's component, which Windows
    strips, so the path still meets the junction; `...`; 8.3 short names (`RESULT~1`, `LONGDI~1/INNER_~1`), which
    are still seen as links; device `NUL` (outside).
  - **Pass, with the content still bound by sha256:**
    - a hard link to an outside file, which is the same file on the same volume;
    - an NTFS alternate data stream, `results/x.csv:s`. Git never sees its bytes. Refusing `:` in a declared path
      would be cheap.
  - **File symlinks** need a privilege this account lacks (`WinError 1314`), so they are not realistic.
  - **A chain** behind an allowed junction (its target itself a link) is not followed, which is by design.
- **n-b (M-1, the report).** `_check_output` (`:1215-1220`) now requires `dict(out.data) == declared` both ways. It
  is still the runner's own report. A runner that declares and reports nothing passes (`{} == {}`). n-2's build
  requirements, now in the module docstring (`:69-79`), are the only guard against that.
- **n-c (m-4, the invocation).** The exact `sys.orig_argv` test, the flags and the three environment variables
  refuse a `runpy` wrapper, `-c`, `-m`, `-i`, `-X`, `-I` and others (`test_the_invocation_in_real_processes`).
  - **The clean-run path is not blocked.** `run_clean.run` adds only `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`
    and the run ids. The account's environment has no `PYTHONPATH`; it has only `PYTHONDONTWRITEBYTECODE=1`.
  - **Not covered, all deliberate, none present on this machine.** In 3.12.10 there is no `sitecustomize` or
    `usercustomize`, and no `.pth` file with an `import` line, in either site folder. `sys.meta_path` is the
    standard library's plus `six`'s. The vectors left open:
    - a `sitecustomize.py`, `usercustomize.py` or import-line `.pth` in the per-user, user-writable site-packages;
    - `PYTHONUSERBASE` or `PYTHONHOME` pointed elsewhere;
    - `PYTHONOPTIMIZE`. I found no `assert` among the guards, so this one is harmless today;
    - a planted `.pyc` in a git-ignored `__pycache__/` (`.gitignore:10`). Python loads it in place of the bound
      source even under `PYTHONDONTWRITEBYTECODE`.
  - **`PYTHONSAFEPATH`** only drops `scripts/` from `sys.path`, which the entry script does not rely on.
  - **Cheap additions under a pin:** refuse `sitecustomize` or `usercustomize` in `sys.modules`; refuse
    `PYTHONUSERBASE`, `PYTHONHOME` and `PYTHONOPTIMIZE`, and `sys.flags.optimize`; refuse any `__pycache__` under the
    checkout (`run_clean` writes none); record `sys.executable` and `sys.version`.
  - Refusing `-I` is the wrong way round, since it is the hardening flag, but it is harmless.
- **n-d (m-1).** The do-nothing floor is decided only by `W.above_floor`, at both of its uses: the selection screen
  (`passes_floors`, `:1450`) and the re-read (`:1505`). Neither the plateau nor the engine applies a floor of its own,
  and `not_paid_within_B` is a limit, whose direction rule agrees with `limit_check`'s. The input is
  `-float(r.value)`, where `r.value = np.mean(-composite)` (`:1262`, `:1306`). Negation is exact under
  round-to-nearest. For the screen and the verdict to agree, W42-R1's held-out verdict must pass `above_floor` the
  same `np.mean` over seeds. That is an order-of-summation point for its build.
- **n-e (n-1).** `limits_inside` (`:1396-1411`) calls `W.limit_check` on the same re-read arm and sessions left as
  the survey's `limit_estimate`. Exact equality is therefore sound: the same function on the same arrays.
  - A NaN estimate would raise `LimitDisagrees` (`NaN != NaN`), abort the run and spend the once. It cannot arise:
    every limit's key is in `REQUIRED`, and `validate_values` requires it finite and its E_h non-empty.
  - The beside fields now come from `limit_check`: normal z, B-10's form.
  - The mutant `checklevel` is killed. The `limit-*` mutants are killed by `LimitDisagrees`.
- **n-f (m-3, the vendored path).** `_verify_result` imports `extended.results`, which calls `use_vendored_stage2()`
  and puts `vendor/stage2` and `vendor/stage2/scripts` at the front of `sys.path` partway through the run.
  - I found no name that collides with a module the survey imports later. The survey's own imports are qualified
    `extended.*`.
  - It is worth a line in the docstring: from then on, a bare import in any part resolves to the vendored scripts
    first.
  - `verify_result` adds nothing that `load_objective`'s sha check lacks, except the manifest's form.

## What I tried that found nothing

- **m-1, the floor everywhere.** I grepped `plateau.py`, `search_space.py` and `proposer.py` for any floor; there
  is none. `floor-sign` and `floor-eps-from-zero` are killed by `do_nothing_exact` and `floor_agrees`.
- **m-6, the token.** The token is anchored at the start of the third cell (`reader.py:286-288`, `heldout_tokens`).
  The form `survey-fixture-finalists: ...` matches neither `HELDOUT_TOKENS["finalists"]` nor `HELDOUT_TOKEN_LIKE`.
  The mutant `token-fixture-keeps-real-prefix` is killed by `planted`'s audit. No rule of the reader reads the
  fixture form.
- **m-4, the driver's binding.** `objective_code` binds `code_closure("extended.survey")` and the entry script's LF
  sha. `driver_tree() == ROOT` is checked under a pin, and `test_under_a_pin` kills the dropped check.
- **M-1, the report.** `data-report-keys` (keys only) is killed by `data_report`.
- **m-5, the order of events.** The once is checked before the objective is read (`:1731-1736`) and recorded after
  every pre-cell refusal and before `draw_survey` (`:1770-1776`). Nothing between the record and the first cell reads
  an outcome. `build_part` runs the factories before the record; a factory that ran cells would be the part's own
  defect.
- **n-5.** `_sidecar` refuses non-JSON and non-object input. `parameters` that are not an object refuse.

## What I could not check

- **W42-R1 on this branch.** `extended/wave42.py` and `scripts/wave42_apply.py` are not in 5c5cb93. The suite loads
  them from 01e896a into a temporary folder. So `objective_code` cannot be computed in the real tree yet, and
  `_w42_apply()` refuses there (n-7 of v3, order of events).
- **A real pinned run inside `run_clean.py`.** I specified it in v3 and still recommend it:
  - one clean checkout of a scratch commit with a toy `extended.` part;
  - `run_clean.py --name sv-probe -- python scripts/survey_run.py prereg/F-99_toy.md`;
  - minutes, no bars.

  It would show F-1 live (the atlas refused) and the invocation check on the real `orig_argv`.
- **The full suite under the mutants.** The brief allows one run of the 18-minute suite, so the mutants were run
  against their scenarios and the nine non-scenario tests above, not the whole suite.
