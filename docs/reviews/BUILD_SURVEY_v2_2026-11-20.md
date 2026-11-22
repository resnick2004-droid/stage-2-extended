# Red team: the Wave 5 survey runner, corrective cycle 1 (wt/wt-survey 45d148a)

Target: `extended/survey.py`, `tests/survey_world.py`, `tests/test_survey.py` at 45d148a, read with `git show`. Line
numbers are those of 45d148a. The branch merges df367a7 (Wave 3.4 as it stood).

Specification read: E-221 (O-1, O-3 to O-7), E-230, E-238, E-247 to E-254, CHARTER 3.5 and 3.8 to 3.9, and
`docs/reviews/BUILD_W34_v3_2026-11-20.md` (rb2-a). The composite's pinned form was read in W42-R1
(`git show 2bde318:extended/wave42.py`). The first read is `BUILD_SURVEY_2026-11-20.md` (S-1 to S-4, m-1 to m-5,
n-1 to n-7).

**On the brief.** The brief listed the builder's five interpretations and asked me to attack them. I did not take them
as given. One is rejected (F-3). Four stand, with readings (section "The builder's interpretations").

**How it was run.** Everything ran on a `git archive` of 45d148a in the session scratchpad. Nothing was written in the
worktree; its `extended/survey.py` was checked byte-identical to 45d148a afterwards. All worlds were synthetic, with
`OMP_NUM_THREADS=1`. Each probe stayed well under 500 MB. No bar, atlas or result file was read.
- `tests/test_survey.py` on the copy: **38 passed**.
- The probes are under `scratchpad/v2/probes/`:
  - `p1_bindings.py`, `p1b_outcome.py`, with `pkg/parts.py` and `pkg/helper.py`: the bindings;
  - `p3_heldout_gate.py`: the held-out tag, a repeat run, the failure path;
  - `p4_form.py`: the composite's form, the side heuristic, the z law;
  - `p5_limit_curse.py`: the limit's winner's curse;
  - `mutate.py`: ten mutants, each run against the touched test file.

## Verdict: **must be re-declared** (the build is redone in its last corrective cycle)

**Counts:** 1 changes-a-conclusion, 3 material, 7 minor, 9 notes.

**The first read's findings:**
- **S-1: closed.**
  - The runner is on df367a7's API, and `Engine.check` refuses the old one.
  - Each run opens exactly one ledger, whose protocol is built from the hashed spec and checked by digest after the
    survey.
  - The variants rows carry the declaration's and the protocol's sha256.
  - So rb2-a's runner-side condition is met. The engine-side remedies (the protocol on `PlateauVerdict`) are Q-192's.
- **S-2: closed for its own mutants.**
  - `_killed` now counts only the expected refusal class.
  - Each of the six mutants that survived the first read is now killed by a world built to bite.
  - But **all ten mutants I wrote of this cycle's new code survive** (F-9).
- **S-3: not closed** (F-2). Under one pin, a gate's parameter or a runner's state changes the run from no finalist to
  three finalists with a token, and the binding does not change.
- **S-4: mostly closed.** The no-harm step is required, the gate is required, and the book is checked per design. The
  side-lever check is a denylist that misses plain side levers (F-8).

**The defect that forces a rebuild (F-1).** The runner's composite and its limits are not the form the survey's pinned
composite will have, W42-R1's:
- per-dimension horizons over each dimension's complete starts;
- quantile limits.

The spec cannot even state that form. So the survey would select, filter against the baselines and apply the no-harm
floor on a different objective from the one pinned, and read a p90 limit as a mean.

**n-1 (the runner's self-report as the only held-out guard).** It must block **the declaration's pin**, not this
commit. See n-h.

## Findings

### F-1 (CHANGES-A-CONCLUSION). The composite and the limits are not W42-R1's form, and the spec cannot express it

**Where (survey.py):**
- `:464-477` `composite_score`. Its docstring claims "`extended/wave42.py`'s form", but it averages every dimension
  over **every** start.
- `:480-482` `limit_values`: a per-seed **mean** over the starts.
- `:367-370`: a dimension is exactly `{key, lo, hi, direction, weight}`, with no horizon.
- `:361-363`: a limit is exactly `{measure, key, bound, direction}`, with no statistic and no horizon.
- `:530-533`: one array shape for every key, so a runner cannot hand a dimension its own set of starts.

**What W42-R1 pins** (`2bde318:extended/wave42.py`):
- `:64-81`: every dimension has its own horizon (63, 252 or W sessions).
- `:404-405`: C_b(c) = sum_d w_d mean_{s in E_d} z_d. E_d is the set of starts complete over dimension d's horizon
  (`_rows`, `:209-210`, `sl >= h`).
- `:87-105`: four of the six limits are quantiles: `peak_oop_12_months` p90, `first_payout_days` p50, `orders_max` and
  `accounts_max` p90, `taken_mean` p10. Each has its own horizon.

CHARTER 3.9 pins "the dimension definitions and their normalisers". E-221 says the composite is the lead's, from H4's
results by W42-R1's rule.

**Evidence** (`p4_form.py`):
- **The composite.** A share dimension with horizon 252, on 40 starts, where the starts with fewer than 252 sessions
  left are censored to 0:
  - the survey's composite per seed is `[0.201 0.209 0.212 0.136]`;
  - W42's form is `[0.536 0.557 0.566 0.362]`.
- **A p90 ceiling.** For a lognormal `peak_oop`, the survey's limit value is 1477.7 and the p90 that W42 declares is
  2880.1. A design passes a ceiling of 2,000 in the survey while its declared p90 is 44 % over it.
- **No padding route.** Padding the short dimensions with NaN gives a non-finite composite, which the door refuses as
  `HeldOutInput`. That is a mislabelled abort, not a way round.

**The failure it allows:**
- Every deciding step of the finalist order rule reads a composite other than the pinned one:
  - the selection ranking (`:655`);
  - the re-read against each baseline (`:658-669`);
  - the no-harm floor (`:689-695`).
- A design that is good only on censored starts near a block's end ranks high.
- A design whose p90 bankroll or p50 days-to-payout crosses its limit is kept.
- The finalists' list, the token and the held-out test's inputs then come from an objective nobody pinned.

**Remedy:**
- Import W42-R1's own pieces (`_z`, `_rows`, `_stat`, the dimension and limit specs) rather than re-implementing
  them.
- The spec's dimension carries `horizon`, and its limit carries `stat` and `horizon`.
- `RunOutput` carries the sessions left after each start.
- `composite_score` averages each dimension over its own E_d.
- `limit_values` computes the declared statistic pooled over starts and seeds. The one-sided check beside it needs a
  standard error for a quantile, for example a seed-block bootstrap with a fixed seed.
- Add a test that the runner's composite equals W42-R1's on a fixture of H4's shape. Add worlds where a censored
  dimension and a p90 limit bite.

### F-2 (MATERIAL; S-3 not closed). A part can be swapped without changing its binding: closures, lambdas, instance state, and anything imported

**Where (survey.py):**
- `:217-230` `part_binding`: module plus qualname, the sha256 of the **defining file only**, and `survey_config()`
  only if the object volunteers one.
- `:233-242` `_canon`: a callable inside the space is bound the same way.
- `:920-924`: the comparison.

**Evidence:**
- `p1_bindings.py`. Each of these pairs gives identical bindings:
  - `make_gate(0.5)` and `make_gate(0.0)` (a closure's parameter);
  - two module-level lambdas (`pkg.parts:<lambda>`), even though one refuses everything;
  - `Runner(world, 0.0).run` and `Runner(world, 1.5).run` (instance state, no `survey_config`);
  - a runner calling `pkg.helper` before and after `helper.SHIFT` changes (an imported module).
- `p1b_outcome.py`, one pinned declaration each:
  - **(a)** The gated world, pinned with floor 0.5: 0 finalists and no token. Run with `make_gate(0.0)`: **3 finalists
    and a token**, with the same declaration sha `8739b5417b`.
  - **(b)** The noise world, pinned with `Runner(shift 0)`: 0 finalists. Run with `Runner(shift 1.5)`: **3 finalists
    and a token**.
- The space has the same hole. `from_lever_space`'s `cells` lambdas, its `Constraint.fn` closures (`_rl3_live`,
  `_closed_first`, which capture `session_starts`) and its `starts` closure (which captures `ny_boundary`) are each
  bound only by name and the file of `search_space.py`.

**The failure it allows:** the first read's S-3. A script can run the pinned declaration under several gate floors,
runner settings or data files, then keep the run whose finalists it likes. Each such run passes `run_survey` and
emits a token, and F-5 lets them share one folder.

**Remedy:**
- **Bind code by commit, not by file.** Under a pin, record and require the clean checkout's commit and the blob sha of
  every module under `extended/` that the process has imported from the repository (`sys.modules` filtered to `ROOT`),
  and refuse a dirty or unknown tree.
- **Bind parameters by value.** `_canon` a callable as its binding **plus**:
  - its `__closure__` cell contents, `__defaults__` and `__kwdefaults__`;
  - for a bound method, its `__self__.__dict__`;
  - for a `functools.partial`, its arguments.

  Refuse a callable whose state cannot be canonicalised.
- **Bind data.** Require the runner's data files by sha256 (search_cut's manifest, E-248). Do not leave this to an
  optional `survey_config`.
- **Test it.** One test per route above, each refusing.

### F-3 (MATERIAL). Limits decide on the selection reading, the luckiest one; its point estimate is biased toward "inside"

This is the builder's interpretation 1, and I reject it.

**Where (survey.py):**
- `:732`: `limits_inside(ctx, sel[cand.id])`, the survey or round reading on which the candidate was selected.
- `:600-603`: the limits are read on the selection seeds only, so the re-read's limit values, which are in
  `got["out"]`, are discarded.
- The engine refuses a limit measure on the re-read (`search_space.py` `protocol_for`: `if reread or measure not in
  ...`).

**Evidence** (`p5_limit_curse.py`):
- The world: the plateau world, with the design's `risk` in the region set to 1.05 minus 0.6 times its own money noise.
  The true risk is above the bound 1.0 everywhere in the region.
- **Three finalists and a token.**
- Their selection risk is 0.955, 0.839 and 0.943, all "inside".
- Their re-read risk is 0.973, 1.055 and 1.078: two of the three are outside.
- On 400 fresh seeds: 1.054, 1.053 and 1.043, all outside.

**The failure it allows:**
- A finalist that crosses a limit is carried whenever the limit's measure moves with the composite's noise. In a prop
  journey that is the usual case: a lucky draw on P(pass) is also lucky on ruin and on peak out-of-pocket.
- E-230's "the point estimate governs" does not say which reading. The point estimate the survey can defend is the
  unselected one.
- The held-out test re-reads the limits, so the final verdict is not corrupted. But a crossing design takes a finalist's
  place and a share of k.

**Remedy:**
- **Engine (Q-192):** `protocol_for(measure, reread=True)` admits the declared limit measures on the re-read seeds.
- **Runner:** decide each limit on the re-read's point estimate, with the selection reading and the one-sided check
  beside it.
- **Test:** this world as one, with "limits from the selection reading" as a mutant.

### F-4 (MATERIAL). The held-out tag is checked only at the door, after the book and the gate, so a gated held-out run passes silently

**Where:** survey.py `:591-599`. `_check_output` checks the seeds, blocks, horizon, arms and shapes, **not the tag**.
Then `screen` (the book and the gate) runs. Only after that, and only if neither refuses, does `_reading` reach the
door's tag check.

**Evidence** (`p3_heldout_gate.py`):
- The world: the gated world, whose runner labels exactly the gated designs' runs `heldout_2024`.
- The run raises nothing and completes. **19 held-out-labelled runs** are recorded as `gate: supply ...` refusals.
- The word "heldout" appears nowhere in the readings file.
- The gate saw each of those runs' measures.

**The failure it allows:**
- A runner that honestly labels a held-out read (for example, a fallback window for a thin design) is refused only if
  the gate and the book both pass that design. Otherwise the read is hidden as a gate refusal and the survey goes on
  to a token.
- This is the one held-out path the runner itself can see, and it is the case the guard exists for (n-1).

**Remedy:**
- In `_check_output`, before `screen`, refuse `out.tag != search_space.SEARCH_TAG` with the door's held-out words, as
  `HeldOutInput`.
- Add a test with this world.

### F-5 (MINOR). A second run of the same pinned declaration is accepted, into the same folder, with a second token

**Where:** survey.py `:929-931`. Only held-out rows in an existing `variants.jsonl` refuse.

**Evidence** (`p3_heldout_gate.py`):
- Two runs of one fixture-pinned declaration into one folder, under the names `F-99_first` and `F-99_second`.
- Both emit a token. The folder holds 118 variants rows, which is 2 x 59.

**The failure it allows:** this is the enabler of F-2's selection, and the failure protocol's "never rerun until it
passes". The rows show the repeat, but nothing refuses it.

**Remedy:**
- Refuse when `results_dir/variants.jsonl` already holds a row with `_declaration_sha256 == sha`.
- Refuse when `DECISIONS.md` already holds a `heldout-finalists` token for this declaration.
- Record the run's commit in every manifest (with F-2).

### F-6 (MINOR). The failure path skips the variants rows whenever the failure record cannot be written

**Where:** survey.py `:871-879`. `write(...failure...)` comes first, then `vwrite(rows)`. When `write` raises, the
handler at `:951-954` only adds a note.

**Evidence** (`p3_heldout_gate.py`):
- Two failing runs (`PlateauRefused`) under one name.
- The second run's failure write raises `FileExistsError`, and its note says so.
- The variants file holds **44 rows after two runs of 44 cells**. The second run's counted cells vanished, which is
  exactly what m-4's remedy was to prevent.

**Remedy:**
- Write the variants rows in their own `try`, attempted whether or not the record is written. Or write them first on
  the failure path, where no result exists to orphan.
- F-5's repeat refusal removes the common cause.

### F-7 (MINOR). The finalists' "z" is compared with a t-statistic on the re-read seeds

**Where:**
- survey.py `:665-667`: z = (d - margin) / se, where se is the sample sd over n re-read seeds divided by sqrt(n),
  compared with `spec.z`.
- `:675`: the limit check's critical value, from the normal law.

**Evidence** (`p4_form.py`). At z = 3, the chance of a false pass per baseline under the t law is:

| re-read seeds | P(t > 3) | against the normal 0.00135 |
|---|---|---|
| 5 (the floor) | 0.0200 | 15 times |
| 8 | 0.0100 | |
| 16 | 0.0045 | |
| 32 | 0.0026 | |

The engine moved its plateau to the t law for this reason (rm-3).

**The failure it allows:** a declaration that reads "z = 3" means about 1 in 750 per baseline. At the floor it is 1 in
50. This is not the deciding test, but it moves which designs reach it.

**Remedy:** declare a one-sided level and use the t quantile on n - 1 degrees of freedom in both places, or name the
number a t threshold in the spec and the records.

### F-8 (MINOR; S-4's remainder). The side-lever refusal is a denylist; plain side levers pass

**Where:** survey.py `:86-87`, `:264-272`.

**Evidence** (`p4_form.py`): each of these is **accepted**:
- `direction` (INT -1..1, step 2);
- `fade` (True/False);
- `invert_trigger` (no/yes);
- `bias` (up/down).

**The failure it allows:** the search chooses the side against or with the trigger, which is O-4's refused case. The
no-harm floor's `side_source == TRIGGER` is the runner's own word.

**Remedy:** use an allowlist. Every searched dimension's `lever` is a searched lever id of `extended.lever_space`
(Topstep's 39, or the firm's), and none of them is side-setting. Refuse a dimension with no lever id, with a fixture
exemption for the toy space.

### F-9 (MINOR). Ten mutants of this cycle's new code survive the touched test file

**Where and evidence:** `mutate.py`. Each mutant was applied alone to the copy, then `pytest -x tests/test_survey.py
-k "not defaults"` was run (37 tests):

| mutant | what it breaks | result |
|---|---|---|
| the engine's binding not compared (`PART_NAMES[:-1]`, `:921`) | S-3, the engine | survived |
| no-harm margin x8 (`:693`) | the no-harm margin | survived |
| no-harm margin 0 | the no-harm margin | survived |
| composite weights ignored (`:475`) | the composite | survived |
| composite direction ignored (`:474`) | the composite | survived |
| composite unclipped (`:473`) | the composite | survived |
| a limit's direction ignored (`:680`) | the limits | survived |
| an overlap admitted (`:546-547`) | the book | survived |
| the real path's keys unchecked (`:527`) | the no-harm floor | survived |
| the crossing check's critical value ignored (`:684`) | m-2 | survived |

**The cause** is in the worlds (`survey_world.py:121`, `:145-146`):
- The composite has one dimension, direction +1, weight 1.
- The one limit is "<=".
- The harm world's gap (-0.5 in composite units) dwarfs the margin 0.05.
- No world opens two positions on one side at once.
- No test swaps the engine.

**The failure it allows:** the code that decides now (the composite, the margins, the directions) can be wrong with
the suite green. This is S-2's original complaint, moved to the new code.

**Remedy:** add the following, and add the ten mutants to `MUTANTS`:
- a two-dimension composite with one lower-is-better dimension and unequal weights, values outside [lo, hi];
- a ">=" limit;
- a harm world whose gap sits between margin and 2 x margin;
- a same-side overlap world;
- an engine-swap refusal under a pin.

### F-10 (MINOR). The gate sees every outcome, and the playbook writer is unbound

**Where:** survey.py `:550-554`, where the gate receives the whole `RunOutput` (every arm's outcome keys and the
real-path as-traded readings), and `:85` and `:201`, where `playbook` is not in `PART_NAMES`.

**The failure it allows:**
- A bound gate can still refuse on the composite or on real-path edge. That is an outcome filter, and the declaration's
  red team must read its code to see it.
- The playbook text, which is in the list file, so its sha is in the token, can differ between runs of one pin, for
  example in the side clause (O-4).

**Remedy:**
- Hand the gate a view holding only the declared gate keys (a `gate.keys` entry in the spec).
- Bind `playbook` like the other parts.

### F-11 (MINOR). The composite's numbers, the limits and the margins are typed into the declaration

**Where:** survey.py `:364-405`. Every number of the composite, the limits, the finalists' margin and the no-harm
margin is a literal in the survey-spec block.

**Evidence:**
- CLAUDE.md: "No result number is typed into a document: it is computed from a result file".
- E-221 and CHARTER 3.9: these are W42-R1's output, from H4's search-year results, "pinned in one row".

**The failure it allows:** a declaration whose numbers differ from W42-R1's result file, by a typo or by a choice
after a look, pins and runs. The declaration's reviewer then compares by eye.

**Remedy:**
- The spec names W42-R1's result file and its sha256, and the pinning row.
- `load_spec` reads the dimensions, limits, size that matters and no-harm margin from that verified file. It refuses a
  typed copy that differs, or takes no typed copy at all.

### Notes

- **n-a. Positions have no path key.**
  - `RunOutput.positions` (`:150`) goes into one `UserBook` (`:541-543`).
  - `components.Position` carries no start or seed.
  - Positions pooled over starts and seeds collide across alternate paths: false tier-1 refusals, which costs power.
  - Positions from one path leave the others unchecked.
  - Specify positions per (start, seed) path and check one book per path.
- **n-b. Name `REFLECTED` precisely.** CHARTER 3.8's exception compares the as-traded side with "the coin side on the
  as-walked, reflected path, same fills, same seeds".
  - `RunOutput`'s docstring should say that `REFLECTED` is that coin-side as-walked path, not a full mirror of every
    trade.
  - A full mirror makes the floor about twice as strict on a linear measure.
  - With that reading, the builder's interpretation 2 (as-traded minus reflected at least minus the margin, point
    estimates, `:689-695`) matches CHARTER 3.5 and 3.8.
- **n-c. n-5 as built.** The plateau's base is the selecting re-read, biased toward "better" by passing the baselines'
  test.
  - Under `side: "worse"` that errs toward refusing true plateaus. This is the builder's interpretation 5, accepted.
  - Under `"two_sided"` it can err toward accepting: neighbours that are truly better look less different.
  - Refuse `"two_sided"` in a survey's plateau rule, or re-read the base on its own seeds.
- **n-d. A neighbour refused by the gate or the book refuses its candidate** (`:740-744`). This is interpretation 4,
  accepted.
  - It is conservative, and the same as a neighbour that does not hold at `min_share` 1.
  - A neighbour served from the memo (`:588-590`, read earlier as another candidate's re-read) gets no `plateau` row in
    the readings file. Its reading is right, but the file under-reports the plateau's reads.
- **n-e. Baselines as cells of a `baseline` role, read through the door.** This is interpretation 3, accepted.
  - It is a harmless over-count of cells.
  - The baselines' re-read per-seed values are not written to the readings file (`:607-609` skips them), so an auditor
    cannot recompute the gaps from the results.
  - Design readings enter with `roles=_any` (`:573`, `:599`), which weakens the door's Uncounted check to any role. A
    finalist is still admitted only as a searched cell (`:741`).
- **n-f. The reader's pin rule counts any mention.** `reader.pins` (`PIN`, reader.py `:167`) counts a path-and-sha
  mention in any row as a pin, including a row that blocks or withdraws a draft. That is the repository's convention
  (`test_declarations_fixed.py`), but a survey of a blocked draft would pass `check_pinned`. Q-194's territory.
- **n-g. The order of events before the pin.** The declaration pins the sha256 of the engine's four modules (`:251-253`).
  Q-192 is queued to change those modules (E-251). A declaration pinned before Q-192 merges cannot run on the engine
  after it, so pin only after Q-192, W42-R1's re-declaration and H4's run.
- **n-h. n-1 must block the declaration's pin. It does not block this commit.**
  - Why it cannot block the commit: the held-out guard on what the runner actually reads cannot live in this module.
  - Why it blocks the pin: the pin fixes the runner by sha. So the three-way runner, with its reads through
    `extended.search_cut` and the reader's windows and its own identity, must have stood its review before a survey
    declaration names it.
  - Until F-2 binds imports and state, even a reviewed runner's sha does not fix what runs.
  - The cheapest guard the survey can add: the runner reports the sha256 of search_cut's manifest, and the survey checks
    it against E-248's.
- **n-i. The token is still per family** (the first read's n-2). E-238 and E-254 make the joint held-out test its own
  declaration, listing every firm's finalists. The per-family token is that declaration's input. Q-194 binds the
  reader's rule 1.

## The builder's interpretations

| interpretation | ruling | where |
|---|---|---|
| 1. Limits decide on the selection reading's point estimate | **rejected** | F-3 |
| 2. The no-harm floor compares point estimates: as-traded minus reflected at least minus the margin | stands | n-b, with F-9's margin test owed |
| 3. Baselines are cells of a `baseline` role, read through the door | stands | n-e |
| 4. A neighbour refused by the gate or the book refuses its candidate | stands | n-d |
| 5. n-5 left as built: the plateau's base is the selecting re-read | stands under `"worse"` only | n-c |
| n-1 left open | blocks the declaration's pin, not this commit | n-h |

## The minors, by diff against the first read's remedies

| minor | status | what remains |
|---|---|---|
| m-1 | done | the four baselines are required by name; at least 5 distinct, fresh re-read seeds (E-251's floor); z and margin above 0. The margin is not tied to O-3's pinning row (F-11). |
| m-2 | done | the check is reported beside each limit and never decides. It uses the normal law (F-7), on the selection reading (F-3). |
| m-3 | done | `_records_frame` (`:816-825`) writes every candidate with its rank, reason, gaps, limits, no-harm reading and plateau verdict. |
| m-4 | done, with F-6 | the failure record and the variants rows are written after the first cell, and in `emit` the variants are written last. |
| m-5 | done | no `repo=`; `ROOT`'s `DECISIONS.md` only; the results folder must be inside `ROOT`; the pin's row is recorded. |

The notes n-3 (the bytes read once), n-4 (tags and dates, not substrings), n-6 (every round key required,
`round_spec` recorded) and n-7 (the engine from the tree, checked) are done.

## What I tried that found nothing

- **One ledger, and the protocol.**
  - `test_one_ledger_a_run` holds.
  - The ledger's protocol and re-read seeds are compared with the spec's by digest after `draw_survey` (`:939-941`).
  - No `Parts` field or argument carries a protocol.
  - A held-out block or horizon refuses at `Protocol` construction, before any cell.
  - A reported held-out block or horizon refuses in `_check_output`, before the gate.
- **Selection inside one run.**
  - The candidates are the first `candidates` by selection reading, ties by id. A refused candidate promotes no other.
  - The rounds are exactly the declared count. Re-reads never reach the surrogate (`_keep` only in `read_all`).
  - The order-reversed, rounds-skipped and re-read-not-fresh mutants are killed.
- **The pin.**
  - A fixture pin is refused under `prereg/` and into any `results/` folder.
  - A pin outside `ROOT`, an edited file, or injected writers or engine under a real pin are refused (tests,
    re-checked).
  - The spec id must match the file's prefix.
- **Counting.**
  - The variants rows equal the ledger's cells. That includes the baseline, gated and plateau cells.
  - Every design the runner ran is a counted proposed cell (audit).
  - `variant_count` is the cell count.
  - The variants are written last in `emit` (the ORDER test).
- **The spec's form.** Unknown or missing keys, a non-integer seed, a non-family id, too few re-read seeds, a re-read
  seed shared with the selection seeds, a template placeholder and two spec blocks each refuse (tests, re-checked).
- **Determinism.** Two runs with the same seeds give byte-identical files (test).

## What I could not check

- **The three-way runner, the schedule builder, the gate and the playbook writer.** They are not in this commit:
  - their reads (n-1, n-h);
  - fills and costs;
  - the scheduler's same-moment opposite-side refusal across designs and firms.
- **W42-R1's final form.** It is blocked (E-251, cycle 1 of 2). F-1 rests on its declared composite and limits at
  2bde318. If the re-declaration drops per-dimension horizons and quantile limits, F-1 becomes a docstring fix. Nothing
  in E-250 or E-251 suggests it will.
- **The real lever space under `space_digest`.** Building it reads the lever table and the calendars. I checked
  determinism only on the toy space. `_canon` turns a set into `str()`, which depends on `PYTHONHASHSEED`, if any
  field holds one.
  - The experiment: build `from_lever_space(slots={"ny_am": 1})` in two processes with `PYTHONHASHSEED` 1 and 2, and
    compare the digests.
  - Its cost: light; no bar is read.
- **The full suite, the identity tests and vendor integrity.** Not run (the brief's limit). Only
  `tests/test_survey.py` was run (38 passed), plus its mutants.
