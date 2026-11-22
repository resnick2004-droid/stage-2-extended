# Red team: the Wave 5 survey runner (the staged index of wt-survey, HEAD 89be4b3)

Target: `extended/survey.py`, `tests/survey_world.py` and `tests/test_survey.py`, read from the index with `git show
:<path>`. Line numbers are those of the staged files. Specification read: E-221 (O-1, O-3 to O-7), E-230 (the O-5
ruling), E-238, CHARTER 3.5 to 3.8, and the Wave 3.4 note `docs/reviews/BUILD_W34_v3_2026-11-20.md` (rb2-a). I read
the code, not the brief's expectations; the brief gave none.

All probes ran on scratch copies under the session scratchpad (`git archive` of HEAD plus the staged files, so nothing
in the worktree was written). They used synthetic worlds only, with `OMP_NUM_THREADS=1`. Each took under a minute.
No bar, atlas or result file was read.
- Copy `base`: the engine at 351688d, which is what `tests/survey_world.py:33` loads.
- Copy `v2`: the engine and config at df367a7, the commit Wave 3.4's last read stood on.
- Probe scripts: `scratchpad/probes/mut_mode.py`, `mut_extra.py`, `unbound.py`.

## Verdict: **must be re-declared** (here, the build must be redone before it is committed)

- **2 changes-a-conclusion findings, 2 material, 5 minor, 7 notes.**
- The runner is built and tested against the Wave 3.4 engine **before** its last correction (351688d). It does not
  run on the engine that stood (df367a7).
- So rb2-a's condition cannot be checked on this commit, and as written it is not met: the ledger holds no protocol,
  and the protocol goes to every door from the caller's side.
- The tests' mutation section kills any mutant that raises, so it passes 8 of 8 against a runner that cannot run at
  all.

## Findings

### S-1 (CHANGES-A-CONCLUSION). The runner targets the uncorrected engine (351688d), not the one that stood (df367a7); against df367a7 it does not run, and rb2-a's condition is unmet

**Where:**
- `tests/survey_world.py:33`: `ENGINE_COMMIT = "351688d"`, which is Wave 3.4's corrective cycle 1.
- `tests/survey_world.py:55-64`: the engine is used from the tree if the tree holds it, else read from that commit.
- `extended/survey.py:356-359` (`new_ledger`): `CellLedger(protocol=)` "under the corrected engine". Neither commit
  has that signature. At df367a7 it is `CellLedger()`, and the survey declares the protocol through
  `begin("survey", ..., protocol=, reread_seeds=, measures=)`.
- `:386`, `:511`: `admit_one(..., protocol=...)`. At df367a7 the door takes `measure=` and `reread=` and reads the
  protocol from the ledger.
- `:384-385`: `Reading(...)` with a `reads_through` positional. At df367a7 that is derived, not a field (rn-3).
- `:432-433`: `Sampler.survey(n, ledger=, max_proposals=)`. At df367a7 it requires `protocol=` and `reread_seeds=`.
- `:487-488`: `plateau.check(..., protocol=, reread=)`. At df367a7 `check` takes neither (the W34 note: "`check` and
  `fit` take no `protocol` or `reread` argument").

**Evidence:**
- On `base` (351688d), `pytest tests/test_survey.py`: 23 passed.
- On `v2` (df367a7 engine and config, the staged survey files): **11 failed, 12 passed**. Every failure is
  `TypeError: Sampler.survey() missing 2 required keyword-only arguments: 'protocol' and 'reread_seeds'`.
- df367a7 is not yet in `master` (`git merge-base --is-ancestor` is false). The moment Wave 3.4 merges,
  `survey_world.engine()` picks the tree's engine, and these 11 tests fail on master.

**The failure it allows:**
- At 351688d the cell ledger is a plain dataclass with no protocol (RB-2 open). Every door's protocol is whatever the
  calling code passes. Today that is the survey's spec-built `protocol`, but nothing in the engine binds it.
- `new_ledger` falls back silently to a ledger without a protocol whenever the engine lacks the parameter. So
  rb2-a's "build the ledger's protocol only from the pinned declaration" is not something the ledger enforces. It
  rests on this module calling the doors correctly.
- What the runner would do on the corrected engine has not been run or tested.

**Remedy:**
- Port to df367a7's API:
  - `draw_survey` passes `protocol=ctx.protocol`, `reread_seeds=spec.reread_seeds` and `measures=` (the limit
    measures) to `Sampler.survey`, so the survey's `begin` declares the protocol once.
  - Every `admit_one` takes `measure=`/`reread=` and no protocol.
  - `Reading` is built without `reads_through`.
  - `plateau.check` is called without `protocol`/`reread`.
  - `new_ledger` becomes a plain `CellLedger()` with no `inspect` fallback.
- Set `ENGINE_COMMIT = "df367a7"`, or better, refuse to run unless the engine has the corrected signatures.
- Add a test that a second `CellLedger` cannot be reached from `run_survey`.
- Add rb2-a's remedy on the engine side: `begin("survey")` takes the declaration's sha256, and `PlateauVerdict` and
  `variant_rows` carry the protocol's digest.
- Then re-read this commit.

### S-2 (CHANGES-A-CONCLUSION). The mutation tests count an exception as a kill, and six mutants of the finalist rule survive

**Where:**
- `tests/test_survey.py:300-304`: `_killed` returns True on any `Exception`.
- `:307-326`: the mutant table.
- `:341-355`: the tests that use it.

**Evidence:**
- On `v2`, where the runner cannot run at all, **all 8 mutation tests pass**:
  - the 7 steps of `MUTANTS`;
  - the schedule-and-score test.
  - Every "kill" there is the `TypeError` of S-1.
- On `base` (`mut_mode.py`), 6 of 7 listed mutants are killed by a check, which is fine. `read_design`'s mutant is
  killed by the engine's `OffProtocol`. That is legitimate, but it is the engine's guard, not the survey's.
- Mutants I added on a scratch copy (`mut_extra.py`; the file's tests minus the subprocess one, `-x`):

| mutant of `extended/survey.py` | result |
|---|---|
| the limits ignored (`ok = ok and inside` removed, `:475`) | **survived** |
| the margin ignored (`d - 0` for `d - margin`, `:467`) | **survived** |
| the z ignored (`z > 0` for `z > spec.z`, `:468`) | **survived** |
| only the first baseline compared (`baselines[:1]`, `:463`) | **survived** |
| `_check_output` dropped (`:366-374`) | **survived** |
| `reread_value` taken from the selection reading (`:505`) | **survived** |
| any baseline instead of each (`ok or`) | killed |
| three of four baseline cells left uncounted | killed |
| the fixture's results/ check dropped | killed |

- The cause:
  - The world's limit (`risk` about 0.5, bound 1.0, `survey_world.py:112`, `:138`) never binds.
  - The four baselines are identical (`f = 0`, `:113-114`).
  - The planted height (2.0 against SIGMA 0.5 over 32 re-read seeds) clears z = 3 and margin 0.1 by a wide gap, so
    neither number is tested.

**The failure it allows:**
- The finalist rule's four deciding numbers can be wrong or ignored with the suite green:
  - the limits' point-estimate test, which is E-230's rule;
  - the margin, the size that matters (O-3);
  - the z;
  - "each baseline".
- The suite's reported mutation kill is not evidence. A broken runner passes it.

**Remedy:**
- `_killed` counts only the scenario's verdict. An exception is a failure of the test unless it is the expected
  refusal class.
- Add worlds that make each number bite:
  - a design inside the region whose `risk` crosses the bound;
  - a planted height between `margin` and `margin + z * se`;
  - one baseline stronger than the planted design while the other three are weaker.
- Add the six mutants above to the table.

### S-3 (MATERIAL). The declaration binds only the numbers; the lever space, the composite, the gate, the schedule builder, the runner and the engine are the caller's, unrecorded

**Where:**
- `extended/survey.py:147-162` (`Parts`) and `:648` (`parts.engine or Engine.default()`).
- `:590-591`: the manifest `parameters` hold the declaration's sha, the spec, the counts, the fit digests and the
  task. They hold nothing of the parts.
- `:165-182`: `linear_composite`, whose bounds and weights the caller passes.

**Evidence** (`unbound.py`, one fixture-pinned declaration, base engine):
- Run a is the test world. Run b is the same declaration with the composite's `lo`/`hi` changed. Run d is the same
  declaration with `x` narrowed to [0, 0.5].
- **All three emit a token.** The declaration sha is the same in all three, and the finalists' manifest
  `parameters`, less `counts` and `fit_sha256`, are **byte-identical** between a and b and between a and d.
- The only binding of the space is indirect: the declared plateau rule must step every active lever, so a lever's
  *name* is bound. Its bounds, lattice and cells are not.

**The failure it allows:**
- This is rb2-a's selection after a look, moved from the protocol to the parts. A script can run the pinned
  declaration under several lever ranges, composites (the weights E-221 makes the lead's, "pinned in one row before
  the survey") or gates, then keep the run whose finalists it likes. Each run's token passes the reader's rule 1,
  which checks only the declaration's sha and the list sha.
- The gate is an outcome-dependent filter: `parts.gate(out)` sees every arm's measures (`:398`) and can refuse any
  design, an unpinned limit in effect.
- The runner's self-report is the only held-out guard on what it actually read (`:366-374`). See n-1.
- The process rules (one clean run of a named commit) bound this, but nothing in the code or the token does.

**Remedy:**
- The survey-spec carries, and the runner checks:
  - the space's digest (a canonical JSON of its dimensions and fixed values);
  - the composite's dimensions (key, lo, hi, direction, weight) as numbers, with `scores["composite"]` built *from
    the spec*, not passed;
  - the gate's identity (a named, pinned gate list);
  - the git blob sha of the schedule builder's and runner's modules.
- The manifest records all of them.
- `Parts.engine` is honoured only under a fixture pin.

### S-4 (MATERIAL). O-4's no-harm floor is not a step of the runner, a searched side lever is accepted, and the opposite-position rule is nowhere checked

**Where:**
- `extended/survey.py:158` and `:398`: `gate` is optional and defaults to None.
- Neither the spec (`:75-88`) nor `choose_finalists` (`:491-522`) has a no-harm step.

**Evidence:**
- CHARTER 3.5 and E-230's O-4 ruling: "a design whose trigger's side fails the no-harm floor offers no playbook side
  and is not carried". The floor is read on the real path, not the redrawn one (CHARTER 3.8, "the one exception").
  `RunOutput` has no slot for that reading.
- `unbound.py` run c: a space with `side` in {long, short} as a searched categorical. Its finalists include
  `{'x': 0.7, 'y': 12, 'k': 'b', 'side': 'short'}`, and the run emits a token.
- No code path of the runner sees accounts, firms or positions. The tier-1 rule (no two of the user's accounts or
  firms on opposite sides at once) rests entirely on the caller's `build_schedule`/`runner`, which S-3 leaves unbound.

**The failure it allows:**
- A finalist whose side was chosen by the search, not by its trigger, receives a finalists' token.
- So does a finalist whose trigger side is below the coin side on the real path.
- A schedule builder without the same-moment refusal produces finalists that hedge across accounts. The runner would
  not notice.

**Remedy:**
- A required, declared no-harm step after the re-read:
  - the runner reports the as-traded and the reflected composite on the real path;
  - the margin comes from the spec (CHARTER 3.9);
  - a failure refuses the candidate, and the refusal is recorded.
- `load_spec`, or the space check, refuses a lever whose name or cells set a side.
- The schedule builder is the pinned scheduler (S-3's digest), with a test that a same-moment opposite side is
  refused through the survey.

### m-1 (MINOR). The spec's floors are loose: any baseline names, two re-read seeds, z 0, margin 0

**Where:** `extended/survey.py:258-260` and `:263-282`.

**Evidence** (`unbound.py`):
- `baselines: ["naive_coin"]` and `["my_weak_baseline"]` load.
- `reread_seeds: [300, 301]` with `z: 0` and `margin: 0` loads.
- E-221 and CHARTER 3.8 (b) name the baselines: the naive coin, P-14, P-15 and P-16. The W34 note's rm3-b asks for a
  floor on the re-read seeds (16).

**The failure it allows:** a pinned declaration with fewer or weaker baselines, or a near-vacuous re-read, runs. The
declaration's own red team should catch it, but the runner is the cheaper guard.

**Remedy:**
- The four baselines are required by name.
- The re-read seeds are at least the declared floor.
- `z > 0`, and the margin is O-3's, taken from the pinning row.

### m-2 (MINOR). The one-sided check beside each limit is neither computed nor reported

**Where:** `extended/survey.py:470-475`.

**Evidence:** CHARTER 3.8 (a) and E-230 require "a one-sided check of crossing (B-10's form) beside each limit, never
deciding". `beats_baselines` reports only the value, the bound, the direction and `inside`.

**The failure it allows:** a finalist whose point estimate is inside a limit, but whose crossing is likely, goes to
the list with nothing beside it.

**Remedy:** compute the one-sided statistic from `per_seed` at the level pinned with 3.9's inputs (a spec key), and
write it beside `inside` in the list and the record.

### m-3 (MINOR). The candidates' fates are written nowhere

**Where:** `extended/survey.py:576`. `emit` takes `records` and never uses it.

**Evidence:** `grep records`: the name appears only in `choose_finalists`, the call and `Outcome`. The list file holds
only kept finalists (`:598-611`).

**The failure it allows:** no result file shows which candidates were refused, or why: the re-read gaps, z, limits and
plateau verdict. An auditor cannot check the order rule's drop-outs without re-running.

**Remedy:** write the records, every candidate in rank order with its reason, as a third result, or as rows of the
list with `kept`.

### m-4 (MINOR). An engine refusal after the reads aborts the run with nothing written

**Where:** `extended/survey.py:659-662`. Only `_Gated` is caught. `PlateauRefused`, `SpaceRefused`, the runner's own
errors and the writer's propagate.

**Evidence:**
- `unbound.py`'s first version used a space with a lever that the declared plateau rule does not step.
- `run_survey` raised `PlateauRefused` from `choose_finalists`, after every survey and round cell was read.
- No variants row, no readings file and no list exist for that run.
- Separately, `emit` writes the variants ledger (`:586`) before the result files. A writer failure after it, such
  as `FileExistsError`, leaves rows with no result. A retry into the same folder appends them again.

**The failure it allows:**
- Counted cells vanish from the variants ledger (CHARTER 3.3 (f)) when a run fails.
- If the fix is in code rather than in the declaration, a rerun under the same pin is indistinguishable from a first
  run. That is the failure protocol's "never rerun until it passes".

**Remedy:**
- On any exception after the survey's first cell, write the ledger's variant rows and a failure record (the
  exception, the counts) through the writers, then re-raise.
- Write the variants last, or all-or-nothing.

### m-5 (MINOR). `repo=` lets any folder's `DECISIONS.md` stand for the pin

**Where:** `extended/survey.py:299-330` and `:637`.

**Evidence:**
- `test_a_pinned_declaration_runs...` builds a fake repository with its own `DECISIONS.md` and runs (`:218-233`).
- Nothing ties `results_dir` to `repo`. With the default writer inside a clean run, a fake-pinned declaration writes
  `results/` files and a token.
- The reader's rule 1 (`extended/reader.py` `_finalists`) re-checks the pin against the real log, so the held-out read
  itself is still refused.

**The failure it allows:** result files in a clean run's `results/` whose declaration is not pinned in the
repository's log.

**Remedy:** honour `repo` only when it resolves to `ROOT`, or under a fixture-style rule (no `results/`). Record the
pin's decision row in the manifest.

### Notes

- **n-1. The held-out guard is the runner's self-report.**
  - `_check_output` (`:366-374`) and the door compare what the runner *says* it ran (seeds, blocks, horizon, and on
    351688d `reads_through`) with the protocol.
  - A runner that reads 2024 bars and reports the protocol passes.
  - The real guard must be the three-way runner's own: its identity, and its reads going through `extended.reader`'s
    windows. That runner is not in this commit. Its review must check it.
- **n-2. The per-family token is a key the reader honours alone.**
  - Under `reader._finalists` (rule 1) at this HEAD, a `heldout-finalists: F-NN` row opens a held-out read for that
    family.
  - E-221 O-1 and E-238 want one joint declaration over every firm's finalists. I found no joint rule in the reader.
  - This is outside this commit, but the runner's output feeds it.
- **n-3. The declaration is read twice.** `load_spec` (`:642`) and `check_pinned`'s hash (`:305`) read the file
  separately. Read the bytes once and hash and parse the same bytes.
- **n-4. The held-out word check over-matches.** `heldout_problems` (`:534-544`) refuses any row containing
  "confirm" or "judged", for example a lever named `confirm_bars`. That costs a whole run at its end. Match tags and
  dates, not substrings of design keys.
- **n-5. The plateau's base is the selecting re-read.** The candidate is kept for beating the baselines on the
  re-read seeds, and the same re-read (memoised, `:392-395`) is the plateau's base. The base is biased upward, so
  neighbours look worse. This errs toward refusing true plateaus (power, "check power of strict rules"). It never
  errs toward accepting a spike.
- **n-6. Round defaults sit outside the declaration.** The optional round keys (`centres`, `local`, `restarts`,
  `kappa`, `xi`, `local_scale`, `p_feasible`) take `RoundSpec`'s code defaults. A later default change alters a run
  under the same pin. Require them, or record `RoundSpec`'s full value in the manifest.
- **n-7. The test engine is loaded unedited from git, which is good.** `survey_world.engine()` reads the engine from
  a commit and never from a copy, but it pins the wrong commit (S-1).

## What I tried that found nothing

- **A round, a cell or a finalist added, re-run or dropped after a reading, within one run.**
  - The rounds are exactly `spec.rounds` (`:440`). `begin` refuses a repeated role, and the audit checks "a round
    past the declared count". The `run_rounds` mutant is killed.
  - Candidates are the first `candidates` by selection value, ties broken by id (`:448-455`). A refused candidate
    promotes no other.
  - Re-read readings never reach the surrogate (`_keep` only on survey and round reads, `:415-426`).
  - The proposer drops designs already read (`proposer.py` at 351688d, `seen`).
- **rb2-a within this module.**
  - `run_survey` opens exactly one ledger (`:655`).
  - The protocol and re-read are built once, from the spec of the hashed file (`:649-650`).
  - `Parts` has no protocol field, and no function takes a protocol from the caller of `run_survey`.
  - A weaker protocol needs different declaration bytes, hence another sha. The reader's rule 1 refuses a token whose
    sha is not pinned before it.
  - What remains open is the engine binding (S-1) and the parts (S-3).
- **Held-out reads (as far as the runner can see).**
  - A block reaching 2024 is refused at `Protocol` construction before any run, on both engines.
  - A held-out tag, a `reads_through` in 2024, and one in the confirmation window are each refused at the first
    reading, with nothing written (351688d).
  - A held-out variants row already in the folder refuses before the survey.
  - The fixture pin refuses a `results/` folder and a `prereg/` file. Mutating that check is killed.
- **Variant counts.**
  - The variants rows equal the ledger's cells. That includes refused, gated, baseline and plateau cells, and holds
    through the vendored `VariantCounter` (the default-writer test passes on 351688d).
  - The manifest's `variant_count` is the cell count.
  - Every design the runner ran is a counted proposed cell.
- **Seeds.**
  - Every seed is an explicit integer from the spec. The re-read seeds are disjoint from the selection seeds.
  - The box seed, when None, is refused by `plateau.neighbours` for a box neighbourhood.
  - A limit's direction is validated by `proposer.Limit`.
  - Two runs with the same seeds are byte-identical (test).
- **The pin.**
  - `F-1` cannot stand for `prereg/F-10_...` (the prefix carries the underscore).
  - A pin at another sha, or a second pin at a different sha, refuses.
  - LF normalisation is the same in the parse and in the hash.

## What I could not check

- **The runner on the corrected engine.** It does not run there (S-1). Every claim above about the doors is
  therefore 351688d's, and the port must be re-read.
- **The three-way runner, the schedule builder and the playbook writer.** They are injected and not in this commit.
  So the following could not be checked:
  - sides (O-4) in practice;
  - the opposite-position refusal;
  - fill realism;
  - that `evaluate` honours the horizon;
  - that the runner's reads go through the reader's windows.
- **The joint held-out test (E-238).** No code for it exists at this HEAD.
- **The full suite.** It was not run (the brief's limit). Neither were the identity tests or vendor integrity.
