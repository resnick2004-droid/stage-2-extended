# Red team: the Wave 5 survey runner, build v3, full read (Q-186; wt/wt-survey fcf3447)

Target: `extended/survey.py` (1,523 lines), `scripts/survey_run.py` (38), `tests/survey_world.py` (404),
`tests/test_survey.py` (1,093) at fcf3447, and `git diff 26fbe6c..fcf3447` over those four files (+1,515 / -821). Line
numbers are fcf3447's.

Read beside it:
- W42-R1 at `wt/wt-infra` 01e896a: `extended/wave42.py`, `scripts/wave42_apply.py`, `docs/plans/WAVE42_SETTING_RULE.md`
  (sections 4.5, 6, 9.2);
- the engine at 3452952, merged into the branch: `extended/search_space.py` (`protocol_for`, `begin`, `RolePen`);
- Q-197's `extended/search_calendar.py`;
- `extended/reader.py` (`_main_script`, `_clean_run`, `pins`, rule 1's `_finalists`) and `extended/results.py`;
- `scripts/run_clean.py` (`--discard`, `--remove`);
- my last note BUILD_SURVEY_c2 (C-1, M-1 to M-5, m-1 to m-3, n-1 to n-7).

**On the brief.** The brief names the worker's interpretations ("an exact Fraction floor, stricter than W42-R1's float
`above_floor`"; "`apply()` does not refuse on `pinned_commit`") and states the counts "69 tests and 42 mutants". I
checked each as a claim; none was taken as given.

**How it was run.** Nothing was written in the worktree. `git status` there was empty before and after.
- `timeout 1200 python -m pytest -q -o addopts= -p no:cacheprovider tests/test_survey.py` in the worktree,
  `OMP_NUM_THREADS=1`: **69 passed in 783.91 s**.
- Probes, all synthetic, under `scratchpad/v3probe/`:
  - `p1_floor.py`: the survey's floor comparator against W42-R1's `above_floor` on the same per-seed values;
  - `p2_rows.py`: `check_rows` on three decision rows;
  - `fake/scripts/survey_run.py`: the `__main__` guard under `runpy.run_path`;
  - `mutplugin.py`: a pytest plugin that recompiles one function of `extended.survey` with a one-line edit, in the
    module's own namespace. A control mutant (the script check dropped from `load_objective`) is killed by
    `test_the_objective_is_w42_r1s_file`. The plugin then applied seven mutants together to the whole suite.
- Path resolution only, no read: `Path("vendor/stage2/data/bars").resolve()` in the worktree.
- No bar, atlas or result file of the repository was read.

## Verdict: **PASS WITH MINORS**

**Counts:** 0 changes-a-conclusion, 1 material, 7 minor, 8 notes.

- **No finding changes a conclusion.** The survey computes W42-R1's composite and limits through W42-R1's own public
  functions, B-5 included. It reads W42-R1's real output by name, checks the sidecar, and self-checks the floor.
- **The engine is Q-192b's**, with no stand-in left. Limits are decided on the re-read seeds. The protocol sha256 is
  checked at the declaration, at the ledger and at each plateau verdict.
- **Sessions left are computed from Q-197's calendar**, and a start after 2023-12-29 is refused before anything else.
- **Every finding below can be fixed before the declaration's pin, without a review cycle.** Each has an exact remedy
  and a test that shows the fix.
- **M-1 is labelled MATERIAL** because a guard the build declares (M-4's "data bound by sha256") does not work on the
  input that carries the money: the licensed bars. It changes no conclusion only because two other checks guard the bars
  independently: the identities (P-14 and P-16 path for path) and `vendor_stage2.py --verify`. **Fix it before the
  pin.**

## The earlier findings (BUILD_SURVEY_c2)

| finding | status | where (fcf3447) |
|---|---|---|
| C-1 the objective was W42-R1's superseded form | **answered** | `:704-761`: `results/` + `OUTPUT_NAME` by name; `values_from_rows`; sidecar sha256, script, rule id, raw rule-module sha256, values digest. `:786-800`: `composite_per_seed` and `limit_estimate`, so B-5 is in (`unit_scores`). `:741-760`: the floor is `null_journeys.floor`, self-checked. The margin is the spec's (`:517-520`). `sc_identity` reproduces `setting_rule`'s baseline composites and limit estimates to 1e-12 on the default and rare fixtures. The `b5-dropped` mutant is killed. |
| M-1 the engine refused on every engine that existed | **answered** | Engine 3452952 is merged. `protocol_for(limit, reread=True)` admits a declared limit (`search_space.py:725-735`). `declaration_sha256` is passed (`:1068-1070`). The baselines are recorded through a pen (`:1084-1089`). The ledger's sha is checked (`:1477`), and so is the plateau verdict's (`:1242`). The Q-192b test only simulates the old engine. |
| M-2 the floor was passed by rounding | **answered by `DO_NOTHING_EPS`** | `:1147-1157`; tested at n = 10, 11, 25, 43. The comparator is the survey's own (m-1). |
| M-3 sessions left and starts were the runner's word | **answered** | `:875-894`: the starts are on the pinned calendar, inside the blocks and increasing, with sessions left from Q-197's `sessions_left`. `:764-783`: the calendar is checked against `SEARCH_CALENDAR_SHA256` and W42-R1's calendar digest. The blocks check and the digest check are untested (m-7). |
| M-4 code, data and patches outside every binding | **mostly answered** | `:382-424`: untracked files are counted, every bound module must be tracked, results go to `ROOT/results`, `__main__` must be the entry script. `:1453`: the space digest is compared. `:315-322`, `:946-949`: data by sha256. Three points stay open: the bars cannot be bound (M-1); the driver and the entry script are bound only incidentally; and the `__main__` guard can be bypassed (m-4). |
| M-5 surviving mutants | **answered for those seven** | `meagre`, `unpaid`, `tail`, `censor`, `near6` worlds; their mutants are in `MUTANTS` and killed. Seven new survivors (m-7). |
| m-1 a second run from a fresh checkout | **open** | m-5 |
| m-2 an unset limit was dropped | **answered** | `:731-736`; `test_an_unset_limit_refuses`; the guards and vacuous flags are written beside (`:1327-1337`). |
| m-3 the runner's values were unvalidated | **answered** | `:903-921`. The paid-before-pass branch is untested (m-7). |
| n-5 `heldout_problems` scanned the timestamp | answered | `:1259-1272` scans `params` and `label`. |
| n-1, n-6 counts and docstrings | answered | counts: n-4 below |
| n-2, n-3, n-4 | stand as readings | |
| n-7 (n-f, n-i) | Q-194's | |

## Findings

### M-1 (MATERIAL). The licensed bars cannot be bound, and a runner that reports no data passes

**Where:**
- `survey.py:315-322`: `check_data` refuses a declared file unless `_inside(ROOT / rel, ROOT)`.
- `:567-572`: `_inside` calls `Path.resolve()`.
- `:946-949`: the runner's reported `data` is checked key by key against the declared map (`declared.get(k) != v`).

**Evidence:**
- In this worktree, `vendor/stage2/data/bars` is a directory junction, as in every clean checkout (CLAUDE.md, machine
  facts).
- `Path(...).resolve()` follows it to `C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\data\bars`,
  which is outside the checkout's `ROOT`.
- So any declared data file under `vendor/stage2/data/bars` or `data/atlas` is refused as "outside the repository".
- A runner that reads the bars therefore cannot declare them. Under a pin it must then report `data={}`, which the
  key-by-key check accepts: a missing key is never compared.

**The failure it allows:**
- The bars and the atlas are bound by no declaration.
- Suppose a re-vendored bars file (or the atlas) differs from the one the declaration was written against. The survey
  then runs with every binding equal and emits a token.
- Only the identity test and `vendor_stage2.py --verify` would catch it, and the survey calls neither.
- The other way round, a declaration that lists the bars fails closed at the pin. That is safe but unrunnable.

**Remedy:**
1. For data paths, test containment without resolving links: `os.path.abspath` and `normcase`, the convention of
   `reader._under`. Or allow exactly the two junction roots, `vendor/stage2/data/bars` and `data/atlas`, and check each
   declared file against `vendor_stage2`'s data manifest.
2. Under a pin, require `set(out.data) == set(parts["runner"]["data"])`, not a subset.
3. Test it with a junction made by `mklink /J` in a temporary root holding a declared data file.

### m-1 (MINOR). The do-nothing floor is the survey's own comparator, and it is not stricter than W42-R1's

**Where:** `survey.py:1147-1157`. The survey compares an exact `Fraction` mean against `Fraction(floor) +
Fraction(DO_NOTHING_EPS)`. W42-R1 declares the comparison itself: `above_floor(composite, floor)` is `float(composite) >
float(floor) + DO_NOTHING_EPS` (`wave42.py:507-510`). The rule document 4.5 says the floor is applied "(`above_floor`,
c3-3), twice", at the search-year screen and at the held-out verdict. 9.2 says the survey imports "only these".
`above_floor` is not in `W42_PUBLIC` (`:85-86`).

**Evidence** (`p1_floor.py`, floor 1/6 + 1/6, per-seed values within a few ulps of floor + 1e-9):
- `float(floor) + 1e-9` lies **2.7e-17 above** the exact sum. So in that band the survey **passes** composites that
  `above_floor` refuses.
- Over 120,000 trials there were 16,073 disagreements: 16,031 passed by the survey only, and 42 by `above_floor` only
  (where the float mean rounds up).
- The worker's reading "stricter" is therefore wrong in both directions.
- The band is about 1e-16 wide, about 1e-9 above the floor. A do-nothing design scores the floor (plus rounding), not
  the floor plus 1e-9. So no realistic design lands in the band.

**The failure it allows:** the screen and the held-out verdict apply two different comparators to one declared floor.
A design can be floored by one and pass the other. The chance is negligible, but the survey's claim to compute
"nothing of its own" does not hold here.

**Remedy:**
- Decide with `ctx.W.above_floor(-float(r.value), ctx.obj.floor)`. The reading's value is the float mean over seeds,
  and negation is exact. M-2's rounding is absorbed by `DO_NOTHING_EPS`, which is 1e-9, far above one ulp.
- Add `above_floor` to `W42_PUBLIC`.
- Keep `sc_do_nothing_exact`; it passes unchanged under this remedy.
- Replace the `do-nothing-by-float` mutant with "`DO_NOTHING_EPS` dropped".

### m-2 (MINOR). "The margin's row carries its number" is a substring test

**Where:** `survey.py:624-646`: `must not in line`, with `must = json.dumps(margin)`.

**Evidence** (`p2_rows.py`). All three of these rows are accepted:
- margin 0.005 on the row "the no-harm margin is **0.0055**";
- margin 0.0 on "delta floor **0.05**; no-harm margin 0.02";
- margin 0.005 on "set the stop at **10.005** points".

**The failure it allows:** a typo in the declaration's margin (0.005 for 0.0055), or a row about something else, passes
the check that exists to stop exactly that. The values row has the same weakness in kind: any row that mentions the
sha passes, a rejection note included. The 64-hex sha makes that harmless.

**Remedy:**
- Match the number with boundaries: `(?<![\d.])` + `re.escape(literal)` + `(?![\d])`.
- Require the row to name the no-harm margin.
- Require the values row to name `W42-R1` and `w42_r1_values.csv`.

### m-3 (MINOR). The values file's provenance is not checked: `pinned_commit` and `git_commit` are read by no one

**Where:**
- `survey.py:718-728` checks the sha256, script, rule id, rule-module sha256 and values digest.
- `wave42_apply.py:258` records `pinned_commit: pinned_commit(ROOT)`, which is None when `PIN_FILE` is absent.
- Only `main()` refuses on `commit_problem` (`:274-276`); `apply()` does not. This is the brief's second interpretation,
  confirmed.

**The failure it allows:**
- A values file written by `apply()` with another writer (the suite's own `_manifest_writer` does this), from an
  unpinned or dirty commit, carries a self-consistent sidecar.
- The survey accepts it as soon as a decision row carries its sha256.
- The row is then the only guard. It is the lead's, which is strong, but the file's own record says "not a pinned
  application" and the survey does not read it.

**Remedy:** under a pin, require:
- `parameters.pinned_commit` to be 40 hex;
- the manifest's `git_commit` not to end in `-dirty`;
- `wave42_apply.commit_problem(ROOT, pinned_commit, head=git_commit) is None`.

Verify the sidecar with `extended.results.verify_result` as well. Under a fixture pin, skip these, as now.

### m-4 (MINOR). The decider's own code and the entry script are bound only incidentally, and the `__main__` guard can be bypassed

**Where:**
- `survey.py:325-337` binds the five parts, the engine and the objective's code.
- The closures, printed in the worktree:
  - `extended.search_space`, `proposer`, `plateau` and `search_calendar` do **not** contain `extended.survey` or
    `extended.results`.
  - `extended.survey` is bound only if some part statically imports it. The suite's runner does, because `RunOutput`
    lives there.
- `scripts/survey_run.py` is bound by nothing. Its sha256 is recorded (`:424`) and never compared.
- `check_process` (`:408-411`) trusts `__main__.__file__` (`reader._main_script`).

**Evidence** (`fake/scripts/survey_run.py`):
- I ran `python -c "<patch>; import runpy; runpy.run_path('scripts/survey_run.py', run_name='__main__')"`.
- The script sees its own path as `__main__.__file__`, and it sees the patch in place.
- `sys.orig_argv` shows the `-c`.
- `run_clean.py` accepts any command after `--`.

**The failure it allows:**
- Between the declaration's pin and the run, two kinds of edit leave every binding equal:
  - an edit to `extended/survey.py` (the floors, the finalist order rule, the t threshold), when the runner imports
    `RunOutput` dynamically or from a module of its own;
  - an edit to the entry script.
- A `runpy` wrapper patches any step in process and passes the M-4 guard.
- Either needs a deliberate act, and either is visible in the run's commit and in run_clean's printed command. But
  "no step can be patched" (`:410-411`) is not true as written.

**Remedy:**
- Bind the driver explicitly. The spec's `objective.code_sha256` (or a new `driver` key) should cover
  `code_closure("extended.survey")` and the entry script's raw sha256.
- Under a pin, also require all of:
  - `sys.orig_argv[1:] == [ENTRY_SCRIPT, rel]`, after normalising the path;
  - no `-c`, `-m`, `-i` or `-X` flag;
  - `sys.flags.interactive == 0`;
  - `PYTHONSTARTUP`, `PYTHONINSPECT` and `PYTHONPATH` unset.

### m-5 (MINOR; c2's m-1, still open). A second run from a fresh checkout is not seen

**Where:**
- `survey.py:649-663`.
- `_head_decisions()` (`:580-583`) adds nothing inside a clean tree, where HEAD's `DECISIONS.md` is the working copy.
- `scripts/run_clean.py` has `--discard` (its docstring, step 6), which drops a run's products before `--remove`.

**The failure it allows:**
1. Run a pinned survey and read its finalists.
2. `--discard` the run and `--remove` it, or simply do not collect it.
3. Run again from a new checkout, which holds the commit's `results/variants.jsonl`.

`check_once` sees nothing. With m-4 or M-1, the second run can differ.

**Remedy:**
- Keep an append-only record **outside** the checkout, for example `%LOCALAPPDATA%\stage2-extended-runs\
  survey_once.jsonl`, keyed by the declaration's sha256. Check it and append to it under `run.lock` before the first
  cell, the same pattern as reader's `_once` and `RUN_ID`.
- Or have `run_clean.py --discard` refuse files named `F-*_survey_*` and `variants.jsonl` rows that carry a
  `_declaration_sha256`.

### m-6 (MINOR). A fixture-pinned run of a real declaration returns a token that the reader's rule 1 accepts

**Where:**
- `survey.py:594-603`: a fixture pin is refused only under `prereg/` and only for a `results` output folder.
- `:1374`: the token is built the same way under a fixture pin.
- `reader.py:691-716` (`_finalists`) checks the token's family, sha and pin order, but not where its list file came
  from.

**The failure it allows:**
1. Copy the pinned `prereg/F-NN_x.md` outside `prereg/`. The LF sha is the same.
2. Run it under `fixture_pin` with `SV.ROOT` the real repository. It reads the real W42-R1 values and builds real
   `extended.` parts (a fixture pin admits any module).
3. It returns `heldout-finalists: F-NN @ <the pinned sha> list <sha>`. Since the run is deterministic, that is the
   same list sha the pinned run would give.
4. Paste the token into a row after the pin, and the held-out read is authorised.

The pinned run's guards never run: the clean run, the counted `results/variants.jsonl`, the once-rule and the
`results/` provenance. The preview's cells are counted only in a stray folder.

**Remedy:**
- `token = None` under a fixture pin, or a `survey-fixture:` prefix that `HELDOUT_TOKENS["finalists"]` cannot match.
- Have the test assert it.
- Optional: refuse a fixture pin whose declaration's LF sha is pinned in `DECISIONS.md`.

### m-7 (MINOR). Seven guards are untested: seven mutants survive together across the whole suite

**Evidence:** `mutplugin.py` applied all seven at once. **Result: 69 passed** (`v3probe/mut7.log`). Every one
survives:

| mutant | where | why the suite cannot see it |
|---|---|---|
| `blocks`: the protocol-block check on starts dropped | `:891` | the six `STARTS` lie inside the two blocks |
| `order`: the row-before-the-pin check dropped | `:643` | the row test runs under a fixture pin only, so `pin_n` is None |
| `caldigest`: the calendar against W42-R1's `h4.calendar_sha256` dropped | `:777` | the fixture is always consistent |
| `paid`: the paid-before-pass check dropped | `:920` | no world pays before it passes |
| `untracked`: `--untracked-files=no` in `tree_problems` | `:384` | the test replaces `tree_problems` wholesale (`test_survey.py:777, 780`) |
| `offproto`: the runner's seeds, blocks and horizon equality dropped | `:931` | every off-protocol runner in the suite is held-out, so `_held_out_first` catches it first |
| `checklevel`: the crossing check's level set to 0.5 | `:1128` | only the function is tested (`sc_crossing`), not its use |

**Remedy:** one world or unit test each, and each mutant added to `MUTANTS`:
- a start on 2022-01-01 with blocks that skip it;
- a margin row numbered after the pin row under a real pin, through `check_rows` directly;
- a calendar file whose digest differs from `values["h4"]`;
- a unit with `first_payout_days` < `first_pass_days` <= W;
- `tree_problems` itself on a temporary git repository holding an untracked `extended/x.py`;
- a runner reporting seeds `[101, 102, 103, 105]`;
- `check_level` read back from the list's `limits`.

### Notes

- **n-1 (the check beside the limits).** `crossing_check` (`:809-813`) uses t(n - 1). W42-R1's `limit_check`
  (`wave42.py:544-558`, doc 9.2, B-10's form) uses the normal z_(1 - level). At few seeds the printed `crossing_shown`
  is not W42-R1's `crossed_at_level`. It never decides. Either call `W.limit_check` for the beside fields, or label the
  t law as the survey's in the output.
- **n-2 (held-out reads, brief item "impossible").** The survey cannot make a held-out read impossible; it reads no bar
  itself.
  - It sees the runner's tag, blocks, horizon and starts, and the runner's own `data` report.
  - A unit started in late 2023 and walked for 252 sessions reads 2024 bars unless the runner stops at 2023-12-29. The
    survey drops that value from E_252, but it does not drop the read.
  - For the runner's build:
    - bars only through `extended.reader.read_bars(start, end, ...)`, with the end at most 2023-12-29;
    - a per-start `reach` (the last bar date read) in `RunOutput`, which the survey refuses past `SEARCH_LAST`;
    - optionally, under a pin, `sys.addaudithook` on `open`, refusing any file outside the declared data and code.
- **n-3 (the baselines are the runner's).** Nothing ties a run's naive-coin, P-14, P-15 and P-16 arms to H4's readings.
  The runner's own identity (CLAUDE.md: "every new runner has its own identity") must cover the baseline arms path for
  path, because every gap is measured against them.
- **n-4 (counts).** `MUTANTS` holds **41** entries, not 42. `SCENARIOS` holds 32. The suite has 25 test functions, which
  makes 69 tests (41 + 5 parametrised + 23).
- **n-5.** `json.loads(side.read_text())` (`:718`) is outside the `try`: a malformed sidecar raises `JSONDecodeError`,
  not `SpecRefused`. It fails closed.
- **n-6.** `rule_module_sha256` is a raw-bytes sha of `extended/wave42.py`. That file is `text=auto` and this machine
  has `core.autocrlf=true`, so the producer's and the reader's checkouts must share an end-of-line configuration. If
  they do not, the survey fails closed. The result CSVs are `-text`, which is safe.
- **n-7 (a real pin today).** `SEARCH_CALENDAR_SHA256` is None at 01e896a, so a real-pin run refuses at
  `load_calendar` (`:771-772`) until W42-R1 pins it. That is correct, and an order-of-events point for the lead. The
  suite sets it in process (`survey_world.py:132`), for tests only.
- **n-8 (the self-check, brief item).** The floor's self-check (`:751-760`) is sound. It scores the do-nothing journey
  through the same public composite the survey scores designs with, and through `do_nothing_floor`, against the file's
  floor, to 1e-12. It tests one point; the strong tie is the raw rule-module sha256 (`:725`). Together they hold, and
  `b5-dropped` shows the self-check bites.

## What I tried that found nothing

- **The objective computed only by W42-R1's code.** These all go through `ctx.W`, the one module that `load_objective`
  sha-checks against the producer:
  - the composite (`:786-788`);
  - the limit point estimate and the per-seed estimates (`:791-800`; the per-seed sd matches `limit_per_seed_sd`);
  - the floor;
  - the no-harm composites (`:1137-1144`).

  `sc_identity` matches `setting_rule` to 1e-12 on two fixtures. The only computations of the survey's own are m-1 and
  n-1.
- **The values file by name.** It is `ROOT/results/` + `W.OUTPUT_NAME`. No declared path exists. The five sidecar
  fields refuse one by one (the test). The pin row must carry the file's raw sha256 (`:1450`).
- **The no-harm margin** comes from the spec, never from W42-R1's file. Its row exists and precedes the pin row (with
  m-2's weakness). The as-traded minus reflected composite is compared at the point estimate (`:1140-1141`).
- **The floors before ranking.** `passes_floors` runs on each cell's selection run before the sort (`:1190-1196`),
  then again on the re-read (`:1229-1230`, with `not_paid` inside `limits_inside`). The `meagre` and `unpaid` worlds
  each fail one floor alone, and their mutants are killed.
- **The limits on the re-read.** `limits_inside(got, selection)` decides on `got`, the re-read run. The selection
  value, the crossing check and the vacuous flag are beside. `limits-from-selection` is killed by `risky`.
- **The engine API.** `Engine.check` refuses an engine without `declaration_sha256`, role pens or Q-192's doors. The
  plateau verdict's re-read limits must equal the survey's exactly (`:1244-1246`).
- **The held-out order.** `_held_out_first` refuses a held-out tag, block, horizon or start before the shape, the book
  or the gate. The five parametrised cases each write the failure record and the variants rows, and no readings.
- **The calendar.** The survey checks:
  - Q-197's `sessions_left` is `len - session + 1`, the same as W42-R1's `len(cal) - pos`;
  - the calendar's first and last entries;
  - its digest against W42-R1's values;
  - its file sha256 against `SEARCH_CALENDAR_SHA256`.

  An off-calendar start refuses (`offcal`).
- **Re-read seeds.** The engine's `MIN_REREAD_SEEDS = 5` (`search_space.py:184, 758`) replaces the spec check that v3
  removed. `near6` runs at 6 seeds and kills `t-as-normal`.
- **The tree under a pin.** `tree_problems` counts untracked files, and ignored ones are allowed. In this worktree the
  junctions are ignored and the status is empty. Every bound module must be tracked and inside `ROOT`, and the results
  folder must be `ROOT/results`. Each guard refuses on its own in `test_under_a_pin_the_process_is_checked`.
- **A part changed by parameter, data or space digest.** Each refuses with no runner call and no folder (three tests).
- **The diff.** It removed the spec's `MIN_REREAD_SEEDS` and weights-sum checks and the per-dimension
  "no complete start" checks. Each is now done by the engine, by W42-R1's digest plus module sha, or by
  `validate_values`' per-key E_h check.

## What I could not check

- **The real parts.** The three-way runner, the schedule builder, the gate, the playbook writer and `h4_collect` are
  not built. n-2 and n-3 are what their builds must answer. M-1's open half (a runner reporting no data) can only be
  closed by the survey's equality check.
- **W42-R1 on H4's real output.** Synthetic fixtures only.
- **`check_process` end to end inside a real `run_clean.py` checkout.** The suite stands in `_main_script` and
  `_clean_run`. A light experiment would settle it: a clean checkout of fcf3447 with a toy `extended.` part committed on
  a scratch branch, run as `run_clean.py --name sv-probe -- python scripts/survey_run.py prereg/F-99_toy.md`. It takes
  minutes, one checkout, no bars. It would also show M-1's junction refusal live.
- **The full suite, the identities and vendor integrity.** Not run (the brief's scope).
