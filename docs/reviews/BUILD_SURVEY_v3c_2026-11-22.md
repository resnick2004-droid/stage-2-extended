# Red team: the survey runner's last pre-pin fixes, narrow diff check (Q-186b; wt/wt-survey 2f82685)

Target: `git diff 5c5cb93 2f82685 -- extended/survey.py scripts/survey_run.py tests/test_survey.py` (the master merge
4ccf603 skipped). It answers BUILD_SURVEY_v3b (F-1 to F-6, n-a, n-b) under the lead's rulings. Line numbers are
2f82685's. W42-R1 is read at `wt/wt-infra` 01e896a (`scripts/wave42_apply.py`), which the branch does not carry yet.
Only what is new is reported here; v3b's findings are taken as answered unless a bypass of the fix is shown.

**On the brief.** The brief listed the bypasses to try. I tried them and others, and I did not assume any of them
would or would not hold.

**How it was run.**
- Nothing was written in the worker's tree. Everything ran in a detached clone,
  `%LOCALAPPDATA%\stage2-extended-runs\rt-survey-2f82685` (`git clone --shared --no-checkout`, then `checkout --detach
  2f82685`). The stores were linked into it as two `mklink /J` junctions, only so `sc_data_layout` could see the real
  layout. No store file was opened. The clone was removed at the end, junctions unlinked first.
- `OMP_NUM_THREADS=1` throughout.
- The suite, once, unmutated, in the clone: `timeout 1700 python -m pytest -q -o addopts= -p no:cacheprovider -n 2 tests/test_survey.py`. Result: **130 passed in 875.48 s** (`scratchpad/v3c/suite.log`).
- Probes, all in `scratchpad/v3c/`:
  - `p1_rows.py`: 35 margin rows and 7 values rows, against `margin_row_carries` and `values_row_carries`.
  - `p2_layout.py`: the known folder, spellings of `LOCALAPPDATA`, `main_root` from a real clean checkout
    (`q197-cal`), and a spoofed holder on a stale lock (in a temporary git repository).
  - `p3_closure.py`: whether `extended.lock_guard` is in the bound closure. It is.
  - A throwaway synthetic repository: `git update-index --skip-worktree` on the pin file.
- Mutants: `scratchpad/v3c/test_v3cmut.py`. Eleven one-line edits of my own, made with the suite's `_edit`, each run
  against the scenarios beside it, plus a control that runs those scenarios unmutated. The control passed. **8 of 11
  survived** (F-4 below).
- No bar, atlas, held-out date or NQ from 2026-07-17 was read.

## Verdict: **PASS WITH MINORS**

**Counts:** 0 changes-a-conclusion, 0 material, 4 minor, 5 notes.

Every ruling is implemented as ruled:
- F-1: `DATA_LINKS` equals `STORES`. The test reads `STORES` from `worktrees.py`'s source, and the real layout passes.
- F-2: the pin equals the checkout's pin; `git_commit` exists and is an ancestor of HEAD.
- F-3: the first full number after the name; sign, exponent and percent refused; `W42-R1(?!\d)`.
- F-4: the `O_CREAT|O_EXCL` marker, the lock, the known folder, the once-line.
- F-5: no `extended.` part under a fixture pin.
- n-a: a `:` in a data path refuses.

No fix refuses a legit pinned run on this machine's layout (section "Legitimate runs" below).

The residues:
- the margin parser still accepts a row whose margin differs from its first number (F-1 here);
- the lock check accepts a holder name typed by hand (F-2);
- the once-line is printed only by a run that completes (F-3);
- eight survivors on the new guards (F-4).

## Findings

### F-1 (MINOR). The margin row still accepts a number that is not the row's margin: a changed margin, an operator after the number

**Where:** `extended/survey.py:805-825` (`margin_row_carries`). The function looks only at the first match of the name
(`:810`) and at the first number token after it (`:813`). Its run-on check (`:823`) refuses only a word character, or
`.`/`,` followed by a digit.

**Evidence** (`p1_rows.py`). Each of these rows is **accepted**:

| row | margin passed | what the row means |
|---|---|---|
| `no-harm margin 0.01 replaced: the no-harm margin is now 0.005` | 0.01 | the margin is now 0.005 |
| `the no-harm margin is 0.005/2` | 0.005 | 0.0025 |
| `the no-harm margin is 0.005 * 2`, `0.005^2`, `0.005×10` | 0.005 | something else |
| `the no-harm margin is 0.005-0.01 (a range)`, `0.005–0.01`, `0.005 − 0.001` | 0.005 | not 0.005 |
| `the no-harm margin is 0.005 %`, `0.005 per cent`, `0.005‰`, `0.005 bp` | 0.005 | 5e-5 or smaller |
| `the no-harm margin is 0.005:1` | 0.005 | a ratio |

The first row also **refuses** the 0.005 that the row sets: the parser fails closed on the true number and open on the
stale one. Writing a change as "the no-harm margin 0.01 -> 0.005" gives the same result.

**The failure it allows:** suppose the lead revises the margin in a later row, in the "old -> new" form. A declaration
drafted on the old number, citing the new row, passes `check_rows`. It is then pinned with the wrong margin, and the
no-harm floor that screens every finalist is set by it. The percent ruling (F-3) is also evaded by a single space
before the `%`.

**Remedy:**
- Refuse a row in which the margin's name occurs more than once (or any later occurrence carries another number).
- After the token, allow only end of line, whitespace followed by a letter or `(`, or one of `` ` * ) | ; `` and a
  trailing `.`/`,` that is followed by whitespace or the end.
- Refuse any of `/ * ^ × - – − : % ‰` after optional whitespace, and the words `per cent`, `percent`, `bp`.
- Compile `_NUM_TOKEN` with `re.ASCII`. Today `０.００５` is accepted; that is harmless, but there is no reason to admit it.
- Add each row above to `sc_margin_exact`, the "0.01 -> 0.005" form included, expecting the old number refused.

### F-2 (MINOR). `lock_problem` accepts any holder name that equals the lock's job, so a hand-set `S2X_LOCK_HOLDER` passes on a lock held by another job, or a stale one

**Where:** `extended/survey.py:989-1004`. It checks only `env[S2X_LOCK_HOLDER] == lock["job"]` (`:1002`).

**Evidence** (`p2_layout.py`). A temporary repository whose `run.lock` names `someone-elses-heavy-job`, with an
`expected_end` in the year 2000. With `S2X_LOCK_HOLDER=someone-elses-heavy-job` and `S2X_CLEAN_RUN=sv-other`,
`lock_problem` returns `None`.
- `run_clean.run` builds the child's environment as `{**os.environ, ...}` (`scripts/run_clean.py:133`). So a variable
  set in the launching shell, for example by a session that took the lock by hand to run heavy tests (the
  `lock_guard` docstring allows this), reaches a `run_clean` launched without `--hours`.
- The fix's test (`sc_lock`) never sets a holder that names a different clean run.

**The failure it allows:** a pinned survey runs without taking the lock, while another heavy job holds it. That is two
heavy runs on the machine, the failure the lock exists for. The once-marker still stops a second run of the same
declaration, so the count is not affected. That is why this is MINOR.

**Remedy:** also require the lock's `job` to equal `os.environ[CLEAN_RUN_ENV]`.
- `run_clean` sets both to `--name`: `take --job a.name` and `CLEAN_RUN_ENV = wt.name = a.name`, at `:357` and `:133`.
  So no legitimate run changes.
- `_clean_run` already ties `CLEAN_RUN_ENV` to this checkout.
- Do not add a `pid` check. `set-pid` runs after `Popen` and could race the check, and a launcher `python.exe` has a
  different pid.
- Add a case to `sc_lock`: holder equal to the job, clean-run name another, expecting a refusal.

### F-3 (MINOR). The once-line is printed only by a run that completes; a run that refuses or crashes after the record prints nothing

**Where:**
- `scripts/survey_run.py:36-39`: the line is printed after `run_survey` returns.
- `extended/survey.py:1924` (record) and `:1928-1943`: a failure re-raises, so `Outcome.once_line` is never returned.
- `emit_failure` gets `params["once_record"]`, the path only, never the line.

**Evidence:** reading the code. F-4's ruling says the line is printed so that the lead's row can quote it: "a deleted
record cannot be prevented, only made visible". The runs that spend the once without completing are exactly the ones
whose record is most worth deleting:
- a refusal at the first cell;
- `SurveyRefused("... rb2-a")`;
- `LimitDisagrees`;
- a crash hours in.

If such a run fails before any ledger row, it leaves only the marker and the log line, and no copy in the clean run's
log.

**The failure it allows:** a failed pinned run has its marker and log line deleted, and is then run again. Nothing
printed shows that the first run happened.

**Remedy:** print the line at the moment it is recorded, from `run_survey`, under a pin, and flushed, so the clean
run's log beside the checkout holds it whatever follows. For example:

```
print(f"survey-once: {once_line}", flush=True)
```

Keep the final JSON's copy. Add a test that a run refusing at its first cell has printed the line (with `capsys`).

### F-4 (MINOR). Eight one-line mutants of the new guards survive their scenarios

Each mutant below survived the scenario named beside it. The control ran every scenario unmutated and passed.

| mutant | where | what goes unseen | case that kills it |
|---|---|---|---|
| `known-from-env`: `known_local_appdata` returns `Path(os.environ["LOCALAPPDATA"])` | `:964` | the known-folder check becomes `env == env`, and no test can tell | in a subprocess with `LOCALAPPDATA` set to a temporary folder, `known_local_appdata()` is unchanged and `localappdata_problem()` refuses |
| `lock-unreadable-unset-passes`: `if job is None or holder != job` becomes `if holder != job` | `:1002` | an unreadable or unnamed lock with no holder set passes (`None == None`) | `P({})` on the unreadable lock |
| `lock-no-root-passes`: the no-root branch returns `None` | `:996` | a tree whose main root cannot be found passes | a temporary folder that is not a git repository |
| `fixture-own-two-parts`: `own` scans only `("runner", "space")` | `:1867` | an `extended.` gate, schedule builder or playbook under a fixture pin | loop `sc_fixture_extended` over all of `PART_NAMES` |
| `fixture-own-one-module`: `startswith("extended.components")` | `:1867` | any other `extended.` module | a second module id, for example `extended.plateau:...` |
| `margin-tolerance`: `abs(float(t) - margin) < 1e-4` | `:825` | 0.0051 for 0.005 | a near miss: `the no-harm margin is 0.0051` |
| `once-marker-isfile`: the marker check needs a non-empty file | `:915` | an empty marker, left by a crash between `O_EXCL` and the write, no longer refuses at the early check | an empty marker. Today `O_EXCL` in `record_once` still refuses, so this is redundancy, not a hole |
| `provenance-commit-any-object`: `cat-file -e <head>` with no `^{commit}` | `:1109` | a tree or blob sha passes `cat-file`. `--is-ancestor` then fails, so this is harmless | a tree sha as `git_commit` |

Three were **killed**:
- `data-colon-only-stream`;
- `margin-first-name-any` (the gap check dropped);
- `provenance-ancestor-swapped` (killed by the control case).

There is also an untested line: `scripts/survey_run.py:39` (the printed `once_line`). Dropping it changes no test.
`test_the_entry_script_takes_one_declaration` exercises only the usage errors.

**Remedy:** the cases in the table, each mutant added to `MUTANTS`.

### Notes

- **n-1 (F-2, the working tree's pin file).** `wave42_apply.pinned_commit` reads `config/w42_r1_pin.json` from the
  working tree (`survey.py:1106`). `tree_problems` makes it equal to HEAD's, with one exception. A
  `git update-index --skip-worktree` (or `--assume-unchanged`) edit is hidden from `git status --porcelain`, which I
  confirmed on a synthetic repository: the status was empty, HEAD held `aaaa` and the file held `bbbb`.
  - A fresh `git worktree add` has its own index, so this needs a deliberate act on a reused checkout (`run_clean`
    reuses an existing one, `:118-128`).
  - The bound code is safe from this, because it is hashed from disk. The pin file is not hashed.
  - Cheap fix: read the pin as `git show HEAD:config/w42_r1_pin.json`, or have `tree_problems` refuse any `S`/`h`
    entry in `git ls-files -v`.
  - A malformed pin file also raises a bare `JSONDecodeError` from `pinned_commit`, not `SpecRefused`. That happens
    before the record, so the once is not spent.
- **n-2 (F-2, "an ancestor through an unrelated merge").** No bypass. `commit_problem(pin, head=git_commit)` makes
  the pin an ancestor of `git_commit`, and the new check makes `git_commit` an ancestor of HEAD. So the pin is an
  ancestor of HEAD.
  - The diff test compares trees. A `git_commit` reached through a merge of an unrelated history passes only if its
    imported files are byte-equal to the pin's, which is the rule's intent.
  - A values file written under an earlier pin carries that pin and is refused by `pin != mine`.
  - Whether `IMPORTED_FILES` is closed is W42-R1's question, not this diff's.
- **n-3 (F-4, the marker's folder).** `once_location_problem` (`:896-902`) checks the log's path, not the marker's
  folder `RUNS_DIR/survey_once/`. Two cases put the markers inside a checkout:
  - a junction at that folder pointing into a checkout;
  - a clean run named `survey_once`, made before the first pinned survey.

  `run_clean --remove --discard` would then delete them (`git worktree remove --force`). The log still refuses a
  second run (`check_once_record` reads both), so this is not a bypass, only one guard of two lost. Cheap fix: apply
  `once_location_problem` to the marker's folder as well, and refuse a link there.
- **n-4 (F-5, wrappers).** The refusal is by the id's prefix (`:1867`). A part whose module is not `extended.` but
  which builds a real part would pass under a fixture pin. I found no such module:
  - the suite's `survey_world` factories are synthetic;
  - `scripts/*.py` re-export no part factory;
  - `importlib:import_module` returns a module, not a built part.

  So a bypass needs a new wrapper file, which is a deliberate act. That is acceptable for a guard against an
  accidental preview.
- **n-5 (F-3, the values row).** `W42-R1-old`, `W42-R1b`, `results/w42_r1_values.csv-old` and `x<sha>` are accepted
  (`:831-833`). Each is harmless, because the whole 64-hex sha is the binding.

## Legitimate runs on this machine's layout (path metadata and git only)

- **Known folder.** `LOCALAPPDATA` equals `SHGetKnownFolderPath(FOLDERID_LocalAppData)` (`C:\Users\resni\AppData\Local`),
  and `localappdata_problem()` is None. A trailing `\`, upper case, `/` separators and a trailing `\.` are each
  accepted. An 8.3 spelling (`RESNI~1`) is refused, which fails closed and is not used here.
- **Lock.** `lock_guard.main_root` from the real clean checkout `q197-cal` (a `git worktree`) is the main tree, where
  `run_clean --hours --mem-gb` writes `run.lock`. `run_clean` sets `S2X_LOCK_HOLDER` to the same `--name` that it
  takes the lock under, so a locked run passes. (In a `git clone`, like this review's, `main_root` is the clone. A
  clean run never is one.) `extended.lock_guard` is in `closure_files("extended.survey")`, so it is bound.
- **Data.** In the clone, with the two real junctions, `sc_data_layout` passes: a non-existent name under each store
  is admitted, and `lexists` is false.
- **Data paths.** No declared data path in this repository's layout contains `:`.
- **Fixture pins.** No caller of `pin_fixture` outside `tests/test_survey.py` and `extended/survey.py` exists, so the
  F-5 refusal breaks nothing.
- **Provenance.** The flow it expects:
  1. W42-R1 is applied in a clean run at H, a descendant of the pin whose imported files are unchanged.
  2. The values are collected and committed.
  3. The survey runs at a descendant of H. H is then an ancestor of HEAD, and a commit is its own ancestor.

  `config/w42_r1_pin.json` and `results/w42_r1_values.csv` are not git-ignored (`git check-ignore`), so both reach a
  clean checkout once committed.

## What I tried that found nothing

- **F-2:** a fabricated sha, an unrelated commit, a 41-hex pin and head, a pin other than the file's. Each refuses
  (the suite's cases, and the swapped-ancestor mutant killed by the control).
- **F-4, the race and the order:**
  - `record_once` calls `check_once_record` before `os.open(O_CREAT|O_EXCL)`. If the write or the log append fails
    afterwards, the marker stays, so it fails closed.
  - A loser of the race refuses before the `try`, so it writes no variants row or failure record.
  - Nothing between the record (`:1924`) and `draw_survey` reads an outcome.
  - The marker is created only in `record_once`. No refusal before it creates one.
- **F-4, the known folder:** the `ctypes` call works on this machine. With `hr != 0`, `CoTaskMemFree(NULL)` is harmless.
- **F-4, the runs folder:** `RUNS_DIR` (and so `ONCE_FILE` and `_clean_run`'s checkout test) is tied to the known folder.
- **F-3:** the six v3b rows and the five suite rows refuse. `0.0050`, `.005` and a backticked number pass. `nan` and
  `inf` margins never pass. A non-breaking hyphen in the name fails closed.
- **F-5:** the refusal comes before the engine, `check_data`, the objective and any folder is made (`sc_fixture_extended`).
- **n-a:** `results/x.csv:s` and `...:zone.identifier` refuse. `\\?\`, UNC and drive forms were already refused (v3b n-a).
- **F-1:** `sc_data_layout` reads `STORES` from `worktrees.py` by `ast`. The suite's `data-links-old` mutant is in
  `MUTANTS`.

## What I could not check

- **A real pinned run inside `run_clean.py --hours --mem-gb`.** It would show the lock, the known folder and the
  once-line live. It needs W42-R1 on the branch and a pinned toy declaration. I specified it in v3 and v3b and still
  recommend it. It takes minutes and reads no bars:
  1. a scratch commit with a toy `extended.` part and `config/w42_r1_pin.json`;
  2. `run_clean.py --name sv-probe --hours 0.5 --mem-gb 1 --task Q-186b -- python scripts/survey_run.py prereg/F-99_toy.md`.
- **W42-R1 in the real tree.** `scripts/wave42_apply.py` and `config/w42_r1_pin.json` are not at 2f82685, so the
  provenance check was exercised only on the suite's temporary repository and W42-R1's source at 01e896a.
