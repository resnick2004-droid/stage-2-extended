# Red team: the Wave 5 survey runner, corrective cycle 2 (wt/wt-survey 7197e50 + 26fbe6c, head 26fbe6c)

Target: `extended/survey.py`, `tests/survey_world.py`, `tests/test_survey.py` at 26fbe6c (the whole of
`git diff 3e08316..26fbe6c`: three new files, 2,364 lines). Line numbers are 26fbe6c's unless another commit is named.

Read beside it:
- W42-R1 as declared now, `wt/wt-infra` 34ee968: `extended/wave42.py`, `scripts/wave42_apply.py`,
  `docs/plans/WAVE42_SETTING_RULE.md`;
- the module the survey's tests load, `856c9bb:extended/wave42.py` (identical to 2bde318);
- Q-192, `wt/wt-features` f2cc64b: `extended/search_space.py`, `extended/plateau.py`;
- the playbook's no-harm margin, `wt/wt-play` da86f0e `extended/playbook.py`;
- CHARTER 3.5, 3.8 and 3.9; my previous note BUILD_SURVEY_v2 (F-1 to F-11, n-a to n-i).

**On the brief.** The brief states the lead's ruling on the no-harm margin and the do-nothing composite. I took the
ruling as the specification to check against (it is the lead's to make). I did not take the build's claims as given.

**How it was run.** Nothing was written in the worktree. `git status` there was empty before and after.
- `timeout 900 python -m pytest -q -o addopts= tests/test_survey.py` in the worktree: **55 passed in 419 s**.
- Probes, all on synthetic data with `OMP_NUM_THREADS=1`, under `scratchpad/c2probe/`:
  - `p1_w42_interface.py`: the survey against 34ee968's `wave42`, on a synthetic H4 input that 34ee968's own
    `_validate` accepts;
  - `p2_mutants.py`: eight new mutants, each run against the suite's own scenarios.
- No bar, atlas or result file was read. The one exception is a line count of the repository's
  `results/variants.jsonl` run through `heldout_problems` (46 rows, 0 flagged).

## Verdict: **BLOCKED**

**Counts:** 1 changes-a-conclusion, 5 material, 3 minor, 7 notes.

**What blocks.** C-1 is a blocking finding:
- The survey's objective is W42-R1's **superseded** form, 856c9bb, from before W42-R1's two corrective cycles. The
  tests load exactly that commit.
- Against the W42-R1 that is declared now (34ee968), the survey **cannot read the real output file**. It needs two
  keys that W42-R1 does not write, and it calls two names that W42-R1 no longer has.
- Even after a mechanical port, **its composite is not W42-R1's.** W42-R1's cost dimension scores a unit that has not
  passed at z = 0 (B-5). The survey does not.
  - So a design that buys nothing scores **0.5 in the survey against W42-R1's floor of 1/3**, and it passes the strict
    do-nothing floor.
  - The baselines' composites move by about 0.027. That is the scale of delta\*, which lies between 0.01 and 0.05.

That changes the selection ranking, every baseline gap, the no-harm floor and the do-nothing floor.

**What also blocks the pin, but is not a correctness defect.** M-1: Q-192 as built (f2cc64b) does not make the engine
change the survey stands in for. Its API also differs from the survey's in three places. So the survey refuses on
every engine that exists. It fails closed, which is safe, but it cannot run.

## The earlier findings (BUILD_SURVEY_v2)

| finding | status | where (26fbe6c unless named) |
|---|---|---|
| F-1 composite and limits not W42-R1's form | **answered for 856c9bb only; not answered for the W42-R1 that stands** (C-1) | `:400-427` use `_derived`, `_rows`, `_z`, `_stat` and per-dimension E_d; `:385-387` read quantile limits with their horizons. At 34ee968 `_derived` and `OPTIONAL` are gone and cost has B-5 (C-1). |
| F-2 a part swapped without changing its binding | **mostly answered**, with holes left (M-4) | `:269-274` id + params by value + code closure; `:285-294` built from the declaration; `:1172-1177` clean tree and commit. Open: untracked and out-of-tree modules, data, in-process patches. |
| F-3 limits decided on the selection reading | **answered in the runner; the engine half is not built** (M-1) | `:920-934` decides on the re-read estimate, the selection value beside; `:829-837` refuses an engine without it. f2cc64b `search_space.py:694` still refuses a limit measure on the re-read. |
| F-4 the held-out tag checked after the book and the gate | **answered** | `:665-681`, called first in `_check_output` (`:694`), before `screen` (`:786`). Tests `:663-673`, `sc_heldout_gated`, and the `held-out-not-first` mutant. |
| F-5 a second run accepted | **partly answered** (m-1) | `:607-617`: same names, same folder's variants rows, a token in the log. Not covered: a fresh clean checkout's empty `results/`. |
| F-6 the variants rows lost when the failure record fails | **answered** | `:1119-1131`, each write in its own `try`; test `:705-726`. |
| F-7 a z compared with a t statistic | **answered in code; untested** (M-5) | `:430-440`, `:908`. The mutant "t replaced by the normal z" survives. |
| F-8 the side-lever denylist | **answered** (allowlist) | `:312-323`; test `:632-639`. Reading n-2. |
| F-9 ten surviving mutants | **answered for those ten** (all now in `MUTANTS`, all killed) | `tests/test_survey.py:444-493`. Seven new survivors (M-5). |
| F-10 the gate sees everything; the playbook unbound | **answered** | `:728-733` the gate's view holds only its declared keys; `:88` `playbook` is in `PART_NAMES`. |
| F-11 numbers typed in the declaration | **answered for W42-R1's values, wrongly for the margin** (C-1) | `:367-397` reads them from the file by sha256. But the no-harm margin is read from W42-R1's file, which by the lead's ruling does not carry it. |
| n-a positions per path | answered | `:714-725` |
| n-b `REFLECTED` named | answered | `:147-154` |
| n-c `two_sided` refused | answered | `:524` |
| n-d memo reads reported | answered | `:779-782` |
| n-e the baselines' re-reads written; design roles | answered | `:765-771`, `:759-762` |
| n-f the reader's pin rule counts any mention | open (Q-194) | `extended/reader.py:348-354` |
| n-g the engine pinned before Q-192 | **confirmed and worse** (M-1) | `:75`, `:183-197` |
| n-h the runner's reads | open, and widened (M-3) | `:145-164` |
| n-i the token per family | open (Q-194; E-238, E-254) | `:1107` |

## Findings

### C-1 (CHANGES-A-CONCLUSION). The objective is W42-R1's superseded form: the real output is unreadable, two keys are not W42-R1's, and the composite differs (B-5)

**Where:**
- `tests/survey_world.py:45`: `WAVE42_COMMIT = "856c9bb"`, "identical to 2bde318 (W42-R1 under review)". The worktree
  holds no `extended/wave42.py`, so every test runs on 856c9bb (`:56-73`).
- `survey.py:377`: `json.loads(p.read_text())`.
- `:389-390`: `v["no_harm"]["margin"]` and `v["do_nothing"]["composite"]`.
- `:405` and `:422`: `W._derived`.
- `:698`: `ctx.W.OPTIONAL`.
- `:408-412`: every dimension through `_z` alone.
- `:387`: limits with `status == "set"` only.

**What W42-R1 declares now (34ee968):**
- `scripts/wave42_apply.py:194-196, 207` writes **`results/w42_r1_values.csv`** (`wave42.py:54`, `OUTPUT_NAME`). It is
  a two-column CSV, `key` and `value_json`, one row per top-level key, through `write_result` with a sidecar manifest.
  Its parameters carry `values_sha256`, `rule_module_sha256`, `script_sha256` and the H4 hashes (`:197-206`).
- `wave42.py` has **no `_derived`** (it is `bankroll_states`, `:351-358`) and **no `OPTIONAL`**. `orders_max`,
  `accounts_max`, `taken_mean` and `first_pass_days` are now in `REQUIRED` (`:144-156`), so all six limits are always
  set.
- **Cost, B-5** (`:551-557`; rule doc section 4.2): "A unit unpassed by W scores at the upper cap, z = 0, on cost ...
  whatever it spent". The caps are taken from passed units only. `_z` does not do this; `setting_rule` does it inline.
- The values carry **no `no_harm` key and no `do_nothing` key**. The floor is `null_journeys.floor.value`, named
  `do_nothing` (`:605-609`), and it is also `inactivity_guards.do_nothing_floor` (`:712-715`). The rule document says
  W42-R1 "does not set ... the no-harm margin ... those are the pinning row's other inputs" (`WAVE42_SETTING_RULE.md`
  line 27).

**Evidence** (`p1_w42_interface.py`). The input is synthetic H4-shaped, with about a third of units unpassed, and is
accepted by 34ee968's `setting_rule`:
- `has _derived: False | has OPTIONAL: False`.
- `load_objective` on the CSV that `wave42_apply` would write: **`JSONDecodeError`**. The read at `:377` is outside the
  `try`, so the error is not even a `SpecRefused`.
- On the same values as JSON: `SpecRefused ... lacks 'no_harm'`.
- After patching in both keys and aliasing `_derived = bankroll_states` (the minimal port), the baseline composites
  compare as follows:

  | baseline | survey | W42-R1 | gap |
  |---|---|---|---|
  | naive_coin | 0.4992 | 0.4718 | +0.0274 |
  | p14 | 0.5303 | 0.5029 | +0.0274 |
  | p15 | 0.5509 | 0.5221 | +0.0288 |
  | p16 | 0.5765 | 0.5489 | +0.0276 |

- **The do-nothing design** (34ee968's own `null_journeys(...)["do_nothing"]`): the survey's composite is **0.5000**,
  W42-R1's floor is **0.3333**, and it "passes the survey's strict floor: True". In the survey, the cost dimension
  gives cash 0 a z of 1. In W42-R1 the unit never passed, so its cost z is 0.

**The failure it allows.** The survey ranks, gaps and floors on an objective nobody pinned:
- A design whose units rarely pass but spend little before failing is lifted on cost. That is exactly the inversion
  B-5 was written to stop.
- The do-nothing floor (V-4) compares the survey's composite with a constant computed by a different formula, so a
  design that buys nothing clears it by w_cost = 1/6.
- Under the build as it stands, nothing runs at all: the merged tree holds 34ee968's `wave42.py`, the tests take it
  (`survey_world.py:64`), and `w42_fixture`'s call `setting_rule(rs, fee_unit=, fee_source=, test_starts=,
  test_seeds=)` (`:153-155`) is not 34ee968's signature.

**What must change: the survey's side.**
1. **Read W42-R1's real output.**
   - The file is `results/` + `wave42.OUTPUT_NAME`, by name. The declaration does not choose it.
   - Parse `key` / `value_json` into the values dict.
   - Verify the sidecar with `extended.results.verify_result`, then require each of these:
     - `script == "scripts/wave42_apply.py"`;
     - `parameters.rule_id == "W42-R1"`;
     - `parameters.values_sha256 == wave42.Wave42Values(values).digest()`;
     - `parameters.rule_module_sha256` equal to this tree's `extended/wave42.py`, on the same (raw-bytes) convention.
       `wave42_apply` uses `sha256_file`, while the survey uses LF; keep the two apart.
   - Require the file's sha256 to be pinned in a decision row: CHARTER 3.9's "one row pins every input". Name that row
     in the spec.
2. **The do-nothing composite.**
   - Read `values["null_journeys"]["floor"]["value"]`, with `floor.name == "do_nothing"`.
   - At load, self-check the survey's own `composite` of `wave42.null_journeys(budgets.fee_unit)["do_nothing"]` (as a
     one-start, one-seed arm with every horizon complete) against it to 1e-12. This one line would have caught C-1.
3. **The no-harm margin, by the lead's ruling.**
   - Take it out of `load_objective`.
   - The spec carries `no_harm: {"margin": <number>, "margin_row": "E-NNN"}`, as the playbook does
     (`wt/wt-play:extended/playbook.py:91`, `:938`).
   - Under a pin, refuse unless the row is a row of `DECISIONS.md` that comes before the declaration's pin row. Better
     than the playbook: also refuse unless the row's text carries the margin's literal, so a typo cannot pass.
   - Use the same margin for trigger sides and resting triggers, unless the row names two (CHARTER 3.9).
4. **Port to 34ee968.**
   - Use `bankroll_states` instead of `_derived`, and `REQUIRED` alone (no `OPTIONAL`).
   - Give cost B-5's rule: z = 0 where `first_pass_days > W`.
   - Refuse any limit whose status is not `set` (m-2).
5. **Tests.**
   - Load 34ee968's module (or merge `wt/wt-infra`).
   - Build the fixture through `scripts/wave42_apply.apply` with synthetic `Sources`, so the test reads the real CSV and
     manifest.
   - `sc_identity` on an arm with unpassed units and nonzero cash.
   - The `nothing` world with `first_pass_days` W + 1 and `cash_to_first_pass` 0.
   - A mutant "B-5 dropped" killed.

**What must change: W42-R1's side.**
- Nothing in its output: it must not grow a `no_harm` key (the ruling).
- Strongly recommended: expose the composite and the limit estimate as public functions of `wave42.py` that
  `setting_rule` itself calls, for example `composite_per_seed(values, sessions_left, out)` and
  `limit_estimate(values, sessions_left, out, name)`. Then the survey calls the rule's own code, not its private
  helpers, and the identity holds by construction. Today the composite is inline in `setting_rule` (`:590`) with the B-5
  branch at `:551-557`, so "wave42's own functions" (survey `:16-17`) cannot be the same computation.

**On the binding of the objective's code by sha256 (brief item 2).**
- `w42_code_sha` (`:281-282`) is a digest of `code_closure("extended.wave42")`, which is `wave42.py` and
  `family_stats.py`, LF.
- It is sound as a pin of what the survey imports. But nothing ties it to the code that **produced** the values file,
  nor to W42-R1's pin row.
- So a values file made by one `wave42.py` and read by another passes, provided the declaration's `code_sha256` names
  the reader's. Remedy (1)'s `rule_module_sha256` check closes this.
- Private names (`_rows`, `_z`, `_stat`) are unstable by convention. `_derived` has already vanished.

### M-1 (MATERIAL). Q-192 does not make the change the survey stands in for, and its API is not the survey's: the survey refuses on every engine that exists

**Where:**
- `tests/survey_world.py:76-82`, the stand-in: `protocol_for(measure, reread=True)` returns
  `self.reread.with_measure(measure)` for a declared limit measure.
- `survey.py:829-837`: `check_engine_rereads` refuses without it.
- `:820-826`: `Sampler.survey(...)` with no `declaration_sha256`.
- `:1203-1205`: `ctx.ledger.record(..., role=BASELINE_ROLE, ...)` with no pen.

**What Q-192 is (f2cc64b `extended/search_space.py`):**
- `:688-697`: `protocol_for` still raises `OffProtocol` when `reread` and the measure is not the base measure (`if
  reread or measure not in self._measures`). **The F-3 engine change is not in Q-192.**
- `:868-871` and `:726-728`: `Sampler.survey` takes `declaration_sha256`, and `begin` raises `DeclarationMismatch` when
  it is absent or differs from `protocol_sha256(protocol, reread_seeds, measures)`.
- `:754-766`: `record` requires the role's `RolePen` (`NotTheDrawer`). Roles are closed by their drawer.

**The failure it allows:**
- On df367a7: `check_engine_rereads` refuses, unless the test's monkeypatch is applied.
- On f2cc64b: `draw_survey` refuses at `begin` (`DeclarationMismatch`, a misleading class). If that is fixed, the
  baseline cells are refused (`NotTheDrawer`). If that is fixed too, `check_engine_rereads` refuses.
- No wrong result can come of this, but a real-pin run cannot happen. The real-pin test (`tests/test_survey.py:787`)
  passes only because it patches the engine in process. That is itself M-4's hole.

**Remedy:**
- **Engine:** a Q-192 follow-up in `wt-features`, declared and reviewed: `protocol_for(measure, reread=True)` admits a
  declared limit measure, `self.reread.with_measure(measure)`. Make it exactly the stand-in's behaviour, with the
  stand-in deleted once it is merged.
- **Survey:**
  - pass `declaration_sha256=SS.protocol_sha256(protocol, reread_seeds, measures)` to `survey`;
  - record the baseline cells through `pen = ledger.begin(BASELINE_ROLE, seed)`, then `pen.record(...)`, then
    `pen.close()`;
  - use Q-192's `protocol_sha256` in the variants rows instead of the survey's own `protocol_digest`, or check that the
    two agree;
  - set `ENGINE_COMMIT` and `Engine.check` to the merged engine.
- **Order of events** (n-g stands): pin the survey's declaration only after the engine follow-up, W42-R1's pin and H4's
  run.

### M-2 (MATERIAL). The strict do-nothing floor is beaten by rounding: the design that buys nothing passes it at many seed counts

**Where:**
- `survey.py:855-860`: `c = -float(r.value)`, then `c > ctx.obj.do_nothing`.
- `r.value` is `float(per.mean())` over the seeds (`:747`), where `per` is the negated composite per seed (`:791`).

**Evidence** (a small synthetic check of that exact arithmetic). The do-nothing design's per-seed composite is exactly
1/6 + 1/6 = 0.3333333333333333 on every seed. `-mean(-full(n, c)) > c` holds for **n = 10, 11, 25-31, 34-39, 43-47**
seeds: the mean lifts the value one ulp above the floor.
- The suite's 4 selection seeds and 32 re-read seeds are not in that list. So `sc_nothing` and `sc_do_nothing_unit`
  pass by the choice of seed counts.

**The failure it allows:**
- With 10 or 30 selection seeds, a region that buys nothing passes the do-nothing floor before ranking and again on
  the re-read.
- It is then stopped only by `not_paid_within_B`. If that limit comes out vacuous (W42-R1 4.5 allows this and prints
  it in `inactivity_guards`), it is stopped only by the baselines' test. In a rare-payout world (the suite's own
  `_rare`, where the do-nothing design already outranks a baseline), the do-nothing design can reach the held-out test.

**Remedy:**
- Decide the floor at a declared tolerance, for example `c > floor + 1e-9` (W42-R1's `AHEAD_TOL` is 1e-6), with the
  tolerance named in the spec's form.
- Or compare per seed before averaging.
- Add a test at n = 10 seeds.

### M-3 (MATERIAL). Each start's sessions left (hence every E_d) and the starts themselves are the runner's word: an incomplete start counts as complete, and E_d need not be W42-R1's

**Where:**
- `survey.py:145-164`: `RunOutput` carries `sessions_left` but **no start dates**.
- `:705-709`: the only check is that the shapes agree.
- `:409`, `:423`: `W._rows(sl, horizon)` selects the "complete" starts from that report.
- `:680`: `_check_through(blocks, out.horizon)` checks the declared horizon number, not any unit's reach.

**Beside it:**
- W42-R1 refused to take sessions left from its caller (B-2). 34ee968 computes them from the pinned search calendar,
  `len(cal) - pos` (`wave42.py:272`): sessions left to the **end of the search years**, the start session counted.
- The survey's docstring says "sessions left in its block" (`:149`). With the suite's two declared blocks
  (`survey_world.py:280`), that is a different E_d.

**The failure it allows:**
- A runner that reports `sessions_left` 300 for a start 20 sessions before 2023-12-29 has the survey count it complete
  over 252 sessions.
- Either the unit's months 2-12 are censored values scored as complete (a bias toward designs with late starts), or
  the runner simulated them on 2024 bars. That is a held-out read the survey cannot see, because the protocol's
  `horizon` (0 in the suite's spec) is checked and the units' reach is not.
- And the survey's E_d can silently differ from the one W42-R1's normalisers and delta\* were set on.

**Remedy:**
- `RunOutput.starts` (ISO dates).
- The survey refuses a start outside the protocol's blocks.
- The survey computes sessions left itself, from the same pinned search calendar W42-R1 reads (Q-197's
  `search_calendar.csv`, by `SEARCH_CALENDAR_SHA256`), on W42-R1's definition.
- It refuses a run whose reported value differs.
- A test with a runner that over-reports.

### M-4 (MATERIAL; F-2's remainder). Code that is not in the commit, data, and in-process patches run under a pin with every binding equal

**Where and evidence:**
- **Untracked files.** `extended/reader.py:437`: `_dirty` runs `git status --porcelain --untracked-files=no`. An
  untracked `extended/my_runner.py` passes the clean check (`survey.py:1174-1177`), is bound by its bytes, and runs. Its
  code is in no commit, so the recorded commit does not bind it, contrary to the docstring (`:14`).
- **Modules outside the repository.**
  - `build_part` checks only `mod.startswith("extended.")` (`:291-292`). `_origin` (`:213-218`) accepts any file
    `find_spec` finds.
  - The suite's own real-pin test does exactly this: it puts `extended.survey_toy` on `extended.__path__` from a temp
    folder (`tests/test_survey.py:781-783`). `survey_world.load_wave42` likewise puts `extended.wave42` there from
    `git show` (`survey_world.py:69-71`). The test passes with finalists.
- **Data.**
  - `extended.lever_space` reads `S1_PATH` (`lever_space.py:270`). The space's calendars and the runner's bars and
    results are not in any binding.
  - `space_digest` is recorded (`:1195`) but **never compared** with a declared value.
- **In-process patches.** There is no declared entry point: `run_survey` is a function. The real-pin test patches
  `CellLedger.protocol_for`, `SV.ROOT`, `SV.R._dirty` and `SV.R._commit` in the same process (`:787`, `:798-800`), and
  every binding still holds.
- **Clean runs.** Under a pin a results folder anywhere inside `ROOT` is accepted (`:591-592`). Only `results/` is
  `protected` (`extended/results.py:73-80`). So a pinned run into `ROOT/out` from the OneDrive tree, outside any clean
  run, emits a token. The real-pin test writes to `repo/out`.

**The failure it allows:** S-3 again, by a different door. Some examples:
- run the pinned declaration with an untracked or out-of-tree part;
- run it with a changed lever table or calendar;
- run it from a script that patches a step;

and keep the run whose finalists you like. Each passes `run_survey` and emits a token.

**Remedy:**
- Under a pin, each closure file's origin is inside `ROOT` and **tracked**: `git ls-files --error-unmatch`, plus its
  HEAD blob equal to the working bytes.
- `clean_run_problem()` is None whatever the folder.
- A declared entry script, `scripts/survey_run.py <declaration>` with no other argument, is the process's `__main__`,
  and its sha256 is recorded.
- The spec declares `space_digest`, compared at build.
- The runner reports the sha256 of every data file it read: search_cut's manifest, E-248, as n-h said. The survey
  checks them against the declaration.

### M-5 (MATERIAL; F-9's successor). Seven of eight new mutants survive: the two V-4 floors mask each other, and the limits' statistic and horizon and the t law are untested at the runner

**Evidence** (`p2_mutants.py`, each mutant applied alone, judged by the suite's own scenarios):

| mutant | scenarios | result |
|---|---|---|
| the do-nothing floor dropped from `passes_floors` | nothing | survived |
| the do-nothing floor dropped everywhere in the runner (the function intact, so `sc_do_nothing_unit` cannot see it) | nothing | survived |
| the `not_paid_within_B` floor dropped from `passes_floors` | nothing | survived |
| `not_paid_floor` always passes | nothing | survived |
| the limit statistic read as the mean (F-1's quantiles) | ceiling, floor, risky | survived |
| the limit horizon ignored (every start) | ceiling, floor, risky | survived |
| the t threshold replaced by the normal z (F-7) | near, planted | survived |
| the composite's E_d ignored | identity | killed |

**The cause:**
- In `sc_nothing` the region fails both floors at once, so either floor alone floors it. The `do-nothing-floor-skipped`
  mutant (`test_survey.py:482`) is killed only by the unit test of the function, not by the runner's use of it.
- The ceiling and floor worlds cross their bounds by enough that a mean crosses too.
- Thirty-two re-read seeds put t(31) close to the normal.
- The suite has 33 mutants (`:444-493`), not 34 (n-1).

**The failure it allows:** V-4's floors (26fbe6c's whole change), F-1's quantile limits and F-7's t law can each be
wrong with the suite green.

**Remedy:** add worlds, and add these mutants to `MUTANTS`:
- a region that fails **only** the do-nothing floor (`not_paid` live but inside its bound);
- a region that fails only `not_paid`;
- a heavy-tailed limit key whose p90 crosses while its mean does not;
- a limit key censored on the incomplete starts;
- a near world at 6 re-read seeds, where t(5) and the normal differ.

### m-1 (MINOR; F-5's remainder). A second run from a fresh clean checkout is not seen

**Where:** `survey.py:607-617` reads only `results_dir/variants.jsonl` and `DECISIONS.md` in this tree.

**The failure it allows:**
- A clean run gets a new checkout whose `results/variants.jsonl` is the commit's.
- So a run that failed after its first cell (its rows are in the first checkout until `--collect`), or a finished run
  not yet collected and committed, does not stop a second run of the same pin from a second checkout.
- That is the failure protocol's "never rerun until it passes", in the one setting that matters under a pin.

**Remedy:**
- Also scan every `%LOCALAPPDATA%\stage2-extended-runs\*\results\variants.jsonl` and the main tree's for the
  declaration's sha.
- Or have `scripts/run_clean.py` refuse a second run naming one declaration.

### m-2 (MINOR). A limit W42-R1 did not set is dropped silently, and a missing `not_paid_within_B` skips its floor

**Where:**
- `survey.py:387` keeps only `status == "set"`.
- `:865-867`: no `not_paid_within_B`, so the floor passes, with `"set": False`.

**Is it safe?**
- At 34ee968 every limit's key is required (`wave42.py:144-156`), and `not_paid_within_B` always exists through
  `bankroll_states`. So "not set" cannot occur in W42-R1's real output.
- The skip is reachable only with a file that is not W42-R1's. It fails open there, and it removes one of the two
  guards W42-R1 4.5 names against inactivity.
- W42-R1 also prints `inactivity_guards.not_paid_within_B == "vacuous: ..."`, which the survey ignores.

**Remedy:**
- Refuse any limit not `set`, and refuse a missing `not_paid_within_B`.
- Write `inactivity_guards` and each limit's `vacuous` flag beside the candidates.
- With M-2's fix, the do-nothing floor then stands on its own when the limit is vacuous.

### m-3 (MINOR). The runner's values are not validated as W42-R1 validates the baselines'

**Where:** `survey.py:689-711` checks presence and shape only.

**What W42-R1 does** (34ee968 `_validate`, `:298-316`): it requires each key finite on E_h, inside its a priori range
(for example `share_months_positive` in [0, 1] and days in [0, W + 1]), and no unit paid before its first pass.

**The failure it allows:**
- A design's out-of-range values are clipped silently by `_z`, while its limits read them raw.
- A NaN on E_h still reaches the door, which refuses it as `HeldOutInput`. That is a mislabelled abort (the old note's
  point, unchanged at `search_space.py:1079-1085`).

**Remedy:** apply W42-R1's per-key checks to every arm (export them from `wave42.py` with C-1's public functions), and
refuse as `SurveyRefused` naming the key.

### Notes

- **n-1.** `MUTANTS` holds 33 entries, not 34. `SCENARIOS` holds 23.
- **n-2 (F-8's reading).** The allowlist admits T1 (signal source) and T5 (entry type). At a level, entry type
  decides break or fade, that is, the side relative to the level. That is "the trigger's own side" (CHARTER 3.5) held
  by the no-harm floor, not a searched side, so it stands. But the docstring's "none of which sets a side" (`:27-28`,
  `:313`) is too strong: the declaration's red team must read T1's and T5's values.
- **n-3 (the floor order, brief item 5).** The three floors are a conjunction, so their order changes only the reason
  written (`first`, `:882-883`), never which cells are ranked. Floors on the selection reading can only remove cells,
  and the re-read re-checks each one (`:974-977`; `not_paid` through `limits_inside`). The strictness, `>`, is W42-R1's
  "must exceed it" (rule doc 4.5). Rounding (M-2) and the form (C-1) are what defeat it.
- **n-4 (held-out, brief item 6).** The survey itself reads only the declaration, `DECISIONS.md`, the objective file
  and `variants.jsonl`. It reads no bar. The protocol refuses held-out blocks and horizons before any cell, and
  `blocks_of` marks any day from SEAL_START. A run's tag, blocks and horizon are refused first. What a runner reads is
  outside its sight (n-h); M-3 is the part of that the survey can and should check.
- **n-5.** `heldout_problems` (`:999-1009`) passes the vendored `VariantCounter`'s timestamp
  (`2026-11-21T03:...`) only because `\b` fails between `1` and `T`. That is fragile. Scan `params` and `label`, not
  the whole row.
- **n-6.** `survey_world.py:5-12` and `:45` describe W42-R1 "under review" at 2bde318, and the no-harm margin as "the
  interface W42-R1's re-declaration is assumed to carry". Both are now false (C-1).
- **n-7.** n-f and n-i stay Q-194's.

## What I tried that found nothing

- **F-4's order.** `_held_out_first` runs before the output's shape, the book and the gate.
  - A held-out tag, block or horizon on the first run refuses the whole survey. The failure record and variants rows
    are written, and no readings file.
  - The `held-out-not-first` mutant is killed.
- **The protocol.** A held-out block (2024-06-28) or horizon (1000) refuses at `Protocol` construction, with no runner
  call and no folder (test `:676-680`).
- **F-6.** With the failure writer broken, the variants rows are still written and the note is attached (test
  `:717-726`).
- **F-5 inside one folder.** The same declaration under a new name refuses ("run once"), and under the same name
  ("never overwritten").
- **Binding by value.** Gate floor, runner shift, space `x_hi`, schedule-builder and playbook parameters, each
  tampered after binding, refuse with no runner call and no folder. The closure of `survey_world` includes
  `extended.survey`, `components` and `search_space`. An engine whose plateau module differs refuses
  (`sc_engine_swap`, and its mutant is killed).
- **The gate's view.** Only `("supply",)` is seen (test `:533`).
- **The floors before ranking.** `sc_mixed` shows harmful designs that outrank the good ones are floored and the good
  ones ranked. The `floors-after-ranking` mutant is killed.
- **The repository's `results/variants.jsonl`.** 46 rows, none flagged by `heldout_problems`. So a pinned run into
  `results/` is not refused by old rows.
- **Determinism.** Same seeds give the same bytes (test).
- **The t law and the crossing check** behave as declared (`sc_crossing`). Their use at the runner is untested
  (M-5).

## What I could not check

- **W42-R1 on H4's real output.** Neither `extended.h4_collect` nor Q-197's calendar is built. C-1 rests on 34ee968's
  declared code run on synthetic input. If H4 has almost no unpassed units by W, C-1's composite gap shrinks, but the
  do-nothing floor still fails by 1/6.
- **Q-192's follow-up.** It is not written. M-1's remedy specifies it.
- **The three-way runner, the schedule builder, the real gate and the playbook writer.** None is in this commit (n-h
  stands). M-3 is the check the survey can make whatever they read.
- **The full suite, the identities and vendor integrity.** Not run (the brief's scope).
- **The `PYTHONHASHSEED` digest experiment on the real lever space.** Still open from the last note. It is light: build
  `from_lever_space(slots={"ny_am": 1})` in two processes with seeds 1 and 2 and compare `space_digest`.
