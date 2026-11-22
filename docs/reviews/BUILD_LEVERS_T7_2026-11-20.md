# Red-team read: the lever rows T2b, A15, A16, A17 (wt-levels) and T7's admission forecast (wt-har), 2026-11-20

Targets: the **staged index** of two worktrees, both on HEAD 89be4b3, read with `git diff --cached HEAD` and
`git show :<path>`. I copied each staged diff out as a patch (`git diff --cached HEAD --binary`), applied it to a sparse
scratch clone of 89be4b3 (no `results/`, no `vendor/stage2/results/`), made a branch per target and merged the two
there. Every test and mutant ran in that clone with OMP_NUM_THREADS=1, `-o addopts=`, under a time limit, on
synthetic data only. I read no bar, no atlas and no result file. I read nothing from 2026-07-17.

Brief: it asks the questions without hinting at an answer, so I had no hint to set aside.

**Disclosure.** Early on I ran `git status --short` once in `wt-levels`. Git may refresh the index's stat cache when it
does that. It changes no staged entry or blob, but it is a write to that tree's index, which the brief ruled out. I ran
no other command that writes either tree.

## Verdicts

| target | verdict | CHANGES-A-CONCLUSION | MATERIAL | MINOR | NOTE |
|---|---|---|---|---|---|
| wt-levels (T2b, A15, A16, A17) | **stands with readings**. Two code and test fixes are owed before or at merge; neither changes a declared rule | 0 | 2 | 3 | 2 |
| wt-har (T7) | **stands with readings**. One loader fix is owed before the heavy fit's file is loaded; it changes no declared rule | 0 | 1 | 4 | 3 |

**Merge of the two.** One textual conflict, in `extended/lever_space.py`: the docstring paragraph about S1 and T7, and
`__all__`. `LEVER_TABLE_topstep50k.md` and `tests/test_lever_space.py` merge cleanly. When resolving, keep wt-har's T7
sentence and drop wt-levels' "T7 has no reading and stays refused". With that resolution the four touched test files
plus `tests/test_router.py` pass on the merged tree: 81 passed, 1 skipped. That holds only while
`results/t7_forecast.csv` is absent (L-M1).

---

## wt-levels

### L-M1 MATERIAL: after merge, the new test file breaks once T7's reading exists (shown)

- Where: `tests/test_lever_space_declared.py:34` (fixture `no_s1_reading` points only `S1_PATH` away), `:63`
  (`test_a9_a19_and_the_readings_stay_refused` asserts `bounds("T7")` is `NotComputed` and that T7 is in
  `refusals()`), and `:230` (`test_every_other_lever_is_bit_for_bit_the_one_before` compares T7's outcome with
  89be4b3's).
- Evidence: on the merged scratch tree I wrote a T7 file and manifest that pass the loader, using wt-har's own test
  helper `_written`, under `results/`. Then 2 of the 38 tests failed: `test_a9_a19_...` and
  `test_every_other_lever_...`, both with `AssertionError: T7`.
- Failure it allows: once Q-183's heavy fit lands in the main tree, the fast tier fails on every commit. The tempting
  "fix" is to weaken T7's guarantee (or move the file) rather than the test.
- Remedy: the fixture also sets `T7_PATH` away, with `monkeypatch.setattr(LS, "T7_PATH", ..., raising=False)` so it
  holds on either branch alone. The bit-for-bit test uses that fixture too, and states that it compares levers with
  their readings absent.

### L-M2 MATERIAL: T2b's and A16's single declared values are not enforced where they are used

- Where: `extended/lever_space.py:185-199`. `session_windows()` still returns `ny_am = (930, None)` and
  `ny_pm = (None, ...)`, so T2b's boundary is not put into the session windows. `extended/router.py:24, 95`: `Routing`
  accepts any `pools` mapping, and `by_component` without a pool for a component "uses every account".
- Evidence: the sampler test (`test_lever_space_declared.py:255`) passes `ny_boundary=b` to
  `search_space.from_lever_space` as a free argument. On this tree it is skipped, because `extended.search_space`
  does not exist here. Nothing in the loader or the router compares the pools a router is given with
  `deal_pools(components, accounts)`.
- Failure it allows:
  - A search can run NY AM / NY PM at a boundary the declaration does not list (any `ny_boundary`) without a refusal.
  - It can run `by_component` with pools that are not dealt, which is an undeclared value of A16.
  - `Routing("by_component")` with no pools routes exactly as `longest_waiting`. A15's third cell then silently
    duplicates the base cell under another name: counted twice in k (conservative), but reported as a different
    design.
- Remedy:
  - `session_windows()` reads `bounds("T2b")`, and the sampler refuses any `ny_boundary` other than it.
  - The router (or a `Routing.dealt(components, accounts)` constructor) deals the pools itself each day, and
    `by_component` without dealt pools is refused.
  - A test that passes a different boundary or hand-built pools and expects a refusal.
- A15 and A17 are already guarded: `Routing.__post_init__` refuses an undeclared rotation and `state_risk` refuses an
  undeclared rule. I mutated the router to ignore pools and `tests/test_router.py` caught it (2 failed).

### L-m1 MINOR: A16's dealing depends on an account order that nobody declares

- Where: `extended/lever_space.py:534-536` ("`accounts` the firm's accounts that day in the caller's order"), and the
  table's A16 row.
- Failure it allows: with n >= m accounts, account j goes to component j mod m, so the order alone decides the whole
  assignment, not just ties. If a caller orders accounts by balance or by room, the "one value, `dealt`" becomes a
  state-dependent rule: a hidden, uncounted lever.
- Remedy (a reading that completes the rule): declare the order in A16's row, for example the journey engine's
  account-opening order with ties by account id, and assert it where the pools are dealt.

### L-m2 MINOR: three guards whose mutants survive the touched tests

Each was run on a scratch copy, against `tests/test_lever_space.py` and `tests/test_lever_space_declared.py`:

- **T2b's one-value refusal** (`lever_space.py:513`). Replacing it with `if False:` survives.
  - The code itself is right: with a probe declaration of `("Europe/London", 16, 0)` it refuses, "takes 2 values over
    the search years".
  - No test declares a zone whose clock changes on other dates than the US. Remedy: add that case to the
    parametrised refusal test.
- **T2b's upper bound** (`:509`). Changing `b < last_entry_offset` to `b <= length` survives, so a boundary in the
  last-entry-to-flat gap (for example exactly at the 15:10 flat) is not shown to be refused. Remedy: add a case at
  15:10 CT, which is 16:10 New York.
- **`floor_target`'s floor half** (`:576`). Mutating it to apply the target cut only survives: both `floor_target`
  cases at `test_lever_space_declared.py:185-186` are decided by the target cut. Remedy: add a case where the floor
  cut binds, for example room = start/8 with a large goal.

These mutants are caught: dropping `state_risk`'s cap at r, dropping its one-micro floor, dropping `deal_pools`'
repeat check, and an undeclared rule name.

### L-m3 MINOR: the claim that the sampler draws the new rows is not checked on this tree

- Where: `test_lever_space_declared.py:255` and the file's docstring.
- `pytest.importorskip("extended.search_space")` skips the test, because no such module exists at 89be4b3 or in this
  index. The signature `from_lever_space(slots=, ny_boundary=, days=)` is assumed, not tested.
- Remedy: reword the docstring as "skipped until Q-186 merges", and require the test to run (not skip) at the merge
  that brings `search_space` in.

### L-n1 NOTE: T2b's provenance

- "Noon New York, where the conventional lunch lull begins" cites no source. An outside, pre-declared source exists:
  Stage 2's `config/session_setups.yaml` window `late_morning` starts at 11:00 CT (D-244, D-245, "fixed before any of
  its data is read"), and 11:00 CT is the same boundary. Cite it.
- Stage 2's researcher did read outcomes by those windows (2009-2025), so the choice cannot be shown blind. It is one
  value with no step, and it coincides with a boundary declared before data, so I see no selection to count.

### L-n2 NOTE: small items for the lead's row

- A16's class changes from `searched` (master's table) to `declared`, so account policy goes from 16 to 15 searched
  levers. Say so in the E-row.
- A17's `keys` omit the funded keys that `b_star` reads. They are still refused if unverified, through the term
  loaders.
- `state_risk` and `deal_pools` have no consumer yet. A survey drawing A17 or `by_component` needs the executor first.
- The table's numbered notes put 11 and 12 between 2 and 3.

### Tried on wt-levels that found nothing

- **T2b on every search-year weekday** (1042 days): 1080 minutes after the reopen, which is 11:00 CT. It is constant
  through all eight daylight-saving changes, on the five-minute grid, and inside (930, 1328).
- **Tier 1 conduct:**
  - `state_risk` never returns more than r (2000-draw property test, plus mutants), so no extra size goes into news.
  - Each rotation gives each trade one account.
  - The book's refusal of opposite positions is unchanged (`test_router.py` passes).
  - There is no automated entry.
- **No unverified rule:** A17's keys load as verified, and A9 and A19 stay refused by key.
- **Every other lever unchanged:** each lever's outcome equals 89be4b3's (bit for bit while the readings are absent).
- **Nothing read:** no bar or result file is read by the new code.

---

## wt-har (T7)

### H-M1 MATERIAL: the loader ties the file to the current definitions only through q (shown)

- Where: `extended/t7_forecast.py:794-840`. The checks are sha256, script, a clean tree, a clean run, task, purpose
  and row, span, identities, `q`, and finite final coefficients with beta > 0.
- Not checked: the manifest's `alert_lag`, `frozen_alert`, `marks`, `walk_last_stamp`, `bands`, `terms`, `void_rule`,
  `c_grid`, `w_grid`, `fold_years` and `purge_sessions` / `embargo_sessions`, against the module's constants now.
  `git_commit` is not compared with the last commit that changed `t7_forecast.py` or `t7_fit.py`.
- `W_GRID` is read at import from RD-05's `grid_w`, so a later change to S2's grid would leave the loaded calibration
  stale without a refusal.
- Evidence (probe on the scratch tree): the loader accepted a manifest that declares `alert_lag: 0`,
  `purge_sessions: 0`, `embargo_sessions: 0`, `c_grid: [9]`, `w_grid: [99]`, `bands: ["x"]` and
  `walk_last_stamp: 9999`. It also loads a file holding only the `final` rows, with no fold, OOF or reliability
  section.
- Failure it allows: a reading made under other definitions loads as T7 and admits marks. The worst case is a reading
  made at an alert lag of 0, which is a five-minute look-ahead against the declared alert. Another case is a calibration
  made on another w grid.
- S1's loader, the precedent this one copies, does compare its declared parameters (`caps == stop_caps()` now, the
  declared share).
- Remedy:
  - Compare every declared parameter in `manifest_parameters` with its value at load time, and refuse on any
    difference.
  - Require the file's sections and folds to be those `run_fit` writes (`output_problems` on the file plus the fold
    set).
  - Add a test that changes one manifest parameter per case.

### H-m1 MINOR: the population filter, the frame and the computed reach are untested (mutants survive)

The full `tests/test_t7_forecast.py` was run on scratch copies; the child-script tests were deselected for the
mutants. No test passes `voids`, and the child's synthetic calendar voids nothing. These mutants survive:

- Void days entering M: `ivv` without `void` (`:435`).
- Void days getting a forecast: `has` without `~void` (`:457`).
- The `kinds` frame ignored.
- `reach` replaced by `di - 1` (`:459`). This disables the embargo's reach clause; `check_splits` sets `reach` by hand
  and never tests `feature_table`'s.
- The 09:00 mark moved from `open` to `day1`.

The docstring declares all of these.

Remedy: a synthetic case with void days and a non-walked day, asserting that:
- they are absent from every trailing term and have no forecast;
- `reach` equals the earliest day read, so a gap pushes it back;
- a training row after a fold is dropped when its 22-day window reaches into the fold.

The other mutants were caught: an alert lag of 0, a frozen alert at 08:45, the walk end at 15:28, and dropping the
dirty-tree check.

### H-m2 MINOR: on the search years the survey would apply an in-sample model

- Where: `t7_forecast.py:707`: the final model is fitted on every search-year row, and `load_forecast` returns only
  that model.
- Failure it allows: a survey scoring `T7 = admit` on the search years uses a HAR and calibration fitted on the same
  rows. feature-rules section 4 says "fitted in-fold and applied out of fold".
- The bias is small (4 coefficients and 2 calibration parameters per band) and side-free: the coin twin admits the same
  marks. It still shifts the flatten share and the supply that the survey reads.
- Remedy: `load_forecast` also returns each yearly fold's model, which is already in the file. On the search years the
  survey applies the fold model that excluded that year. The final model is kept for the held-out years.

### H-m3 MINOR: stops outside the calibrated bracket grid are extrapolated without a flag

- Where: `t7_forecast.py:150` (`C_GRID` from 0.5 to 2 times sqrt(M)) and `:846` (`probability_open` takes any stop).
- Evidence (probe): p_hat is identical, already clipped, at c = 0.05 and c = 0.1.
- Stage 2's trailing-range stops (multiples near 0.05-0.15 of the 20-session range) are likely to sit well below
  0.5 sqrt(M) for overnight and morning marks. I read no data, so I cannot say how often.
- Where T7 actually binds (late marks, large c), the grid probably covers the stop. This limits the harm to T7 not
  doing its job; it creates no false result.
- Remedy: return NaN (never admit) or flag p_hat outside [min, max] of `C_GRID`. Alternatively, declare `C_GRID` from
  S1's loaded k range before the run, which reads no outcome.

### H-m4 MINOR: no way to apply T7 on the held-out years yet

- `feature_table` and `day_grid` refuse any day after 2023-12-29 (`:309, :418`). That is correct for the fit, but it
  means `T7 = admit` in the joint held-out test needs another feature builder.
- Remedy: record that this builder must reproduce `feature_table` cell for cell on the search years (an identity)
  before any finalist carries T7.

### H-n1 NOTE: where q comes from, and how strict it is

- q = 0.05 is D-212 as D-308 raised it. Stage 2's own note says the number "was chosen after D-306's result was seen
  and is labelled so"; that was on 2020-2021, inside the search years, not the held-out years.
- It is a ceiling on a leg's *share* of trades, used here as a *per-mark* threshold. That is far stricter than the
  share it comes from, and it limits power (the check-power rule).
- It is declared on master's table, so no rule changes. Report both facts beside any T7 result.

### H-n2 NOTE: what the label models, and what it does not

- The label is a market entry at the mark's open, kept until 15:07. It does not model:
  - limit entries (T5);
  - the news-window flatten (E-202 (2)(a));
  - P-14's entries off the five-minute grid;
  - RL3's ticket timing (the 09:00 mark's inputs read no same-day bar after 08:24, so the 08:30 alert is safe).
- Because T7 reads no side, the coin twin stays a valid comparison.
- The void flags for day d (H2's missing-minutes and 08:29-bar rules) read that day's later bars. That is the
  repository's population rule (E-231 (2)), applied alike to rule and coin, not something T7 adds.

### H-n3 NOTE: the out-of-fold numbers are diagnostics

- The yearly folds include backward folds (2020 is fitted on 2021-2023), so the out-of-fold numbers are not a forward
  test.
- The loader uses none of them. Keep it that way, or use forward folds for anything that decides.

### Tried on wt-har that found nothing

- **Look-ahead:**
  - At mark m every feature reads bars stamped m - 6 or earlier. rv_60 is bounded at the day's first bar.
  - The opening bands' x3 is frozen at 08:25 (bars stamped 08:24 or earlier), and the shift test covers it.
  - M, x1 and x2 come from earlier frame days only; `prior_means` excludes its own row.
  - Band anchors are DST-aware calendar arithmetic.
  - The shift test replaces bars from the cut on, at 24 cuts across a roll and both DST changes. Its reference uses
    the module's own constants; the alert-lag and frozen-alert mutants were caught anyway.
- **The span:**
  - `check_span` and `check_days` refuse 2023-12-30, 2024-01-02 and 2026-07-17 (the last as the reader's
    confirmation class).
  - The purpose contains `fit` and `search`, so the reader refuses the judged block whatever the declaration says.
  - The child script reads only inside the search years, and the script refuses `results/` outside a clean checkout.
- **Purge and embargo:** 22 sessions, longer than the one-session label and equal to the longest window. The reach
  clause is right as written (H-m1 is about it being untested).
- **The label:** the stop fills on a touch, the target only through a tick, the short side is mirrored, and no bar
  after 15:07 is read (mutants caught).
- **The textbook law:** the series and the images agree to 1e-9. Brownian paths calibrate to alpha near 0 and beta
  near 1.
- **q:** read from the vendored config, its note checked for "D-212", never typed.
- **The licence guard:** the file holds no level-named column, no date and no price.
- **The lever:** `bounds("T7")` is `NotComputed` while the file is absent, and `LeverRefused` (not `NotComputed`) for
  each defect the tests list.
- **Tier 1 conduct:** none of the three conduct rules is reachable from T7.

## What I could not check

- The actual values (beta's sign, the admitted share, c against S1's real stops): nothing has been run and I read no
  result.
- How `search_space` (Q-186) consumes T2b, A15, A16, A17 and T7: the module is absent from both trees.
- Whether the journey engine passes accounts in a stable order (L-m1).
- The real stat-cache effect of my one `git status` in wt-levels; I believe it is none for the staged content.
