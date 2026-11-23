# Red-team diff check: E-280 (2) — C3-2 common path withdrawn, second-rung refusal, and overlap count beside (`wt/wt-firmpath` `20fb4d7`), 2026-11-22

## 1. Verdict: **PASS WITH MINORS** (stands with readings)

`20fb4d7` cleanly and completely implements `DECISIONS.md` E-280 (2) in production code:
- **C3-2 common-path law withdrawn:** `extended/three_way_rungs.py` and `tests/test_three_way_rungs.py` are deleted; zero references to common-path symbols remain across `extended/` and `tests/`; `unit.paths` (C4-8) is gone; every trade books on its own single-trade law at its own `sub`.
- **One side per alert at sub 0 (tier 1):** `_Unit.alert` groups by `(block day, decision, market)` using `K.UNDERLYING` (NQ and MNQ are one; unknown underlying refused; N-2); `as_walked` reads `K.SIDE` at `alert_key` (sub 0).
- **Second rung on a lane refused:** `replay()` allocates one lane-scoped `book` shared across combine and funded draws, and `RaceOver._hand_out` refuses a second rung of one alert before anything is booked in all four modes (`race`, `as_walked`, `rebooked`, `vendored` when `unit` is present).
- **Concurrent-position moments counted beside:** `RaceOver._held` maintains an order-independent per-lane overlap count (`BaselineRecords.overlaps`) plus the window's multi-rung alert count (`BaselineRecords.rung_alerts`), strictly beside and never deciding.
- **N-4 (`p16`):** windows are checked against the pinned search calendar before `UJ.BUILDERS["p16"]` loads, and P-16's window dates are held equal to the calendar's.

No **CHANGES-A-CONCLUSION** or **MATERIAL** defect was found. Four **MINOR** items (three test-oracle / mutant-survival gaps and one `NaN` fallback inconsistency in `unit.hold`) and four **NOTE**s are recorded below.

---

## 2. Target and method

- **Target:** `wt/wt-firmpath` at `20fb4d7`, diffed against `c6c3eeb` (skipping master merge `f67f43f`, i.e. `git diff f67f43f 20fb4d7`).
  - Modified: `extended/three_way_baseline.py`, `tests/test_three_way_baseline.py`, `tests/three_way_baseline_checks.py`.
  - Deleted: `extended/three_way_rungs.py`, `tests/test_three_way_rungs.py`.
  - Unchanged between `c6c3eeb` and `20fb4d7` (verified via `git diff` and read-only inspection): `extended/three_way_firm.py`, `extended/firm_reading.py`, `tests/test_three_way_firm.py`.
  - Supporting read-only references: `DECISIONS.md` (E-280), `docs/reviews/BUILD_FIRMPATH_c4_2026-11-22.md`, `extended/three_way_keys.py`, `extended/three_way_journey.py` (`CoinLanes`), `extended/search_calendar.py`, and `vendor/stage2/propedge/campaign/shared_days.py` (`TradeRouter.begin_day`, lines 280–420).
- **Isolation & cleanup:** Extracted tracked files at `20fb4d7` via `git archive` into `%TEMP%\rt_fp_c5` (never modifying the repository, working tree, or any worktree), ran all probes and mutants there with `OMP_NUM_THREADS=1` and `PYTHONDONTWRITEBYTECODE=1`, and deleted `%TEMP%\rt_fp_c5` at the end. No reads of bars, atlas, held-out dates, or NQ from 2026-07-17.
- **Tests run:**
  - `python -B -m pytest -q -m "not slow" tests/test_three_way_baseline.py` on `20fb4d7`: **22 passed, 1 deselected (`@pytest.mark.slow` / `heavy` `p16`)** in 143 s.
- **Synthetic probes run (`probe_c5.py`):**
  1. `rungs_strict` sub-index distribution across all 12 lanes.
  2. `TB.simulate(..., outcome="vendored")` vs `customer_slices.replay` on strict, unstrict-rungs, and unstrict-overlap jobs.
  3. `_held()` / `unit.hold()` edge cases: same-bar exit asymmetry, `fill_fail` hold duration, `NaN` in `exit_by_rr` with finite `exit_t`, 24-permutation order-independence check on 4 positions, NQ+MNQ cross-instrument overlap.
  4. `_hand_out()` interaction with `missed_q` (strict off and strict on).
  5. Full summary inspection of `three_way_baseline_checks.race()` on the `overlap` job.
- **Mutants tried (17 total across `mut_c5.py` and `mut_c5_b.py`):** 13 killed, 4 survived (`M5`, `M10b`, `M13`, `M16`).

---

## 3. Findings (by severity)

### C5-1 (MINOR). `unchecked` and `hist_fields` in `three_way_baseline_checks.py` filter on `t.get("race_law") is not None`, allowing a silently unreplaced trade to pass every check

- **Where:** `tests/three_way_baseline_checks.py:337-339` (`hist_fields`), `371-372` (`unchecked`).
- **Evidence:** Mutant `M10b_silent_passthrough_day5` inserted an early `if int(lt["historical_day"]) == 5 and not lt.get("at_need"): self._held(lt); return out` in `RaceOver.__call__` (`extended/three_way_baseline.py:330`), silently passing through vendored historical P&L (with historical `u`, `mae`, `rr_used`, and `race_law=None`) on **36 of 1,385 trades** in `race` (plus rows in `rungs_strict`, `overlap`, and `reading`).
  - **Result:** **SURVIVED** all 13 unit tests and all core checks (`race`, `rungs_strict`, `overlap`, and `reading` / `firm_reading.trade_problems`): `unchecked == 0`, `hist_fields == 0`, `bad == 0`, `inputs_bad == 0`, `count_bad == 0`, `need_stat_bad == 0`, `clean == 0`.
- **Failure it allows:** The commit message notes `every ledger race row is covered by a checked row (unchecked)`, but because `unchecked` skips any row where `t.get("race_law") is None`, a regression that fails to replace/tag some trades on `outcome="race"` passes `unchecked == 0` and also passes `firm_reading.trade_problems` (which treats `race_law is None` as a vendored row).
- **Remedy:** In `tests/three_way_baseline_checks.py:371-372`, drop `t.get("race_law") is not None and` so `unchecked` requires **every** ledger trade on the race arm to be matched in `checked` (and assert `t.get("race_law") is not None` for every trade in `path.trades`).

### C5-2 (MINOR). Single-trade keying at `sub > 0` is not actually enforced by the unit tests or `rungs_strict`

- **Where:**
  - `tests/test_three_way_baseline.py:191-197` (`test_rungs_of_one_alert_book_alone_on_one_side_and_a_second_on_a_lane_is_refused`);
  - `tests/three_way_baseline_checks.py:124` (`job(rungs=True)` stop sizing) and `514-515` (`rungs_strict`).
- **Evidence:**
  - Mutant `M5_race_uses_sub0` (replacing `key` with `u.alert_key(u.start + h, f)` on `K.RACE` at `extended/three_way_baseline.py:479`) and mutant `M16_walk_move_uses_sub0` (stripping `sub` to `0` in `RaceOver._reader` at `extended/three_way_baseline.py:497`) **both SURVIVED** all unit tests and engine checks (`race`, `rungs_strict`, `overlap`).
  - On the test role's seed at `(0, 935)`, `K.RACE` draws `0.374647` at sub 0 and `0.032838` at sub 1 — both `< 0.4`, so both produce `+30.0` in the unit test (unlike line 215 for `K.SIDE`, which explicitly asserts `(us[0] < 0.5) != (us[1] < 0.5)`).
  - Probe 1 showed `rungs_strict` booked `{0: 1008}` trades by `sub` — **0 trades at `sub = 1`** — because rung 0 has stop 40 (`rpc = 20`) and rung 1 has stop 80 (`rpc = 40`) at the same fill bar, so whenever rung 0 fails `can_take`, rung 1 also fails.
- **Failure it allows:** A bug collapsing `K.RACE` or `K.WALK` onto sub 0 for a multi-rung alert when only rung 1 is taken passes the full suite.
- **Remedy:**
  1. In `test_rungs_of_one_alert_book_alone_on_one_side_and_a_second_on_a_lane_is_refused`, assert `(_u_race() < p) != (u1 < p)` at a `p` (or stop/R) where sub 0 and sub 1 disagree, and add a `walk`/`move` call on rung 1 asserting its output differs from sub 0's stream.
  2. In `job(rungs=True)`, make `j=0` the wider stop on some days (or add a day where `j=0` is unaffordable and `j=1` is taken) so `rungs_strict` takes and oracle-checks `sub = 1` rows through the engine.

### C5-3 (MINOR). `_Unit.hold()` does not fall back to `exit_t` when `exit_by_rr[R][j]` is `NaN`

- **Where:** `extended/three_way_baseline.py:257-265`.
- **Evidence:** Compare `vendor/stage2/propedge/campaign/shared_days.py:328-332`, which checks `np.isfinite(arr[j])` before using `exits_rr[R][j]` and otherwise falls back to `exit_[j]`. `_Unit.hold()` checks only `float(R) in ex` and returns `float(ex[float(R)][int(j)])`. Probe 3c verified that when `exit_by_rr[1.5][0]` is `NaN` and `exit_t[0] = 980.0`, `unit.hold(...)` returns `(940.0, nan)` and `_held()` silently records `overlaps = 0` for a second trade entering at `950.0`.
- **Failure it allows:** On a DayBlock carrying a `NaN` entry in `exit_by_rr` with a valid `exit_t`, the beside-only overlap counter silently undercounts relative to the router's actual hold.
- **Remedy:** Guard with `val = float(ex[float(R)][int(j)]); if math.isfinite(val): return float(f.entry), val` before falling back to `exit_t`, and add a unit test.

### C5-4 (MINOR). Boundary touch (`leave == enter`) is untested in `_held()`

- **Where:** `extended/three_way_baseline.py:371,374`; `tests/test_three_way_baseline.py:219-250`.
- **Evidence:** Mutant `M13_held_ge_instead_of_gt` (`x >= enter` and `leave >= o[0]`) **SURVIVED** both unit tests and engine checks because neither `_Held` (`[940→980, 950→1001, 1000→1010]`) nor `job(overlap=True, strict=False)` contains a pair with `leave == enter`.
- **Remedy:** Add a trade entering exactly at a prior trade's `leave` minute (e.g. `1010→1020` after `1000→1010`) in `test_overlapping_positions_are_counted_beside` and assert `overlaps` does not increment.

---

### Notes (non-blocking)

- **N-1 (`_Unit.uniform` cache key omits market code):** `extended/three_way_baseline.py:268` caches by `(k.moment, int(kind))`. Safe today because `K.UNDERLYING` maps only `{"NQ": 1, "MNQ": 1}` (one code) and `_Unit.market()` refuses any other underlying. If a second market code is ever added to `K.UNDERLYING`, `alert_key` (sub 0) will collide across markets in `self.cache`; include `self.market` / underlying code in the cache key before adding another market.
- **N-2 (`overlaps` edge nuances when strict rule is off):**
  - Probe 3b: a `fill_fail` trade returns `-room` (non-NaN), so `_held()` counts it as held until its historical `exit_by_rr` (`overlaps = 1` for a later trade entered on another account during that window). This matches the router's pre-session hold and is conservative (overcounts rather than undercounts on a breached account).
  - Probe 3a: if two *different* alerts fill on the exact same bar (`entry = 940`) and one is a same-bar exit (`leave = 940`) while the other is held (`leave = 980`), `_held()` gives `overlaps = 0` when the same-bar exit has the lower `j` and `1` when it has the higher `j`.
- **N-3 (`_hand_out` refuses on handed-out, not just booked, when strict rule is off):** Probe 4a confirmed that when rung 0 is missed (`missed_q > 0`, returning `NaN`), handing rung 1 of the same alert to another account is still refused. This is fail-closed and matches the docstring (`A lane handed a second rung of one alert is refused, never booked`). Probe 4b confirmed that under the strict rule with `missed_q = 0.5`, `rungs_strict` completes with 168 missed rows and zero spurious refusals.
- **N-4 (`hold_windows` input bounds):** `tests/three_way_baseline_checks.py:428-438` does not explicitly guard against negative `s` or `h <= 0` (benign for declared positive starts/horizons).

---

## 4. What I tried that found nothing

- **Common-path deletion and dead-code grep:** Confirmed `extended/three_way_rungs.py` and `tests/test_three_way_rungs.py` are deleted at `20fb4d7`; `git grep` across `extended/` and `tests/` found zero leftover imports, references, or fields (`rung_step`, `rung_race`, `rung_walk`, `rung_move`, `TIMED_TOL`, `PathStep`, `check_step`, `rung_trades`, `rung_moments`).
- **Design mode & firm reading untouched:** `git diff c6c3eeb 20fb4d7 -- extended/three_way_firm.py extended/firm_reading.py tests/test_three_way_firm.py` is empty; `three_way_firm.py` continues to enforce `strict_gap` and `UserBook` independently.
- **Vendored identity through `simulate()` (Probe 2):** `TB.simulate(..., outcome="vendored")` matches `customer_slices.replay` with 0 diffs on both strict (`overlaps = [0]`) and unstrict-overlap (`overlaps = [36, 36, 36, 36]`) jobs, and refuses unstrict multi-rung alerts (`"second rung"`).
- **Order-independence of `_held()` (Probe 3d) and NQ/MNQ unification (Probe 3e):** All 24 permutations of 4 positions on one day gave the exact same overlap count (`2`), and NQ + MNQ trades on overlapping alerts counted as `1` overlap on the same market.
- **Killed mutants (13 of 17):**
  - `M1_skip_handout_race` (unit + checks)
  - `M2_skip_handout_vendored` (unit)
  - `M3_alert_by_str_not_market` (unit)
  - `M4_side_uses_own_sub` (unit)
  - `M6b_real_skip_held_race` (unit + checks)
  - `M7_skip_held_vendored` (unit)
  - `M8_held_order_dependent` (unit)
  - `M9_held_counts_missed` (unit)
  - `M10_silent_passthrough_j2` (unit)
  - `M11_rung_alerts_no_window` (unit)
  - `M12_p16_hold_after_builder` (checks)
  - `M14_handout_per_account` (unit + checks)
  - `M15_hold_ignores_exit_by_rr` (unit)
- **No disallowed reads:** Nothing in `20fb4d7`, its tests, or these probes reads bars, the atlas, held-out dates, or NQ from 2026-07-17.

## 5. What I could not check

- **Heavy `p16` vendored identity (`test_p16s_own_job_vendored_identity`):** Marked `@pytest.mark.slow` / `@pytest.mark.heavy`; not run (reads P-16's walk table / atlas; lead's under `run.lock`).
- **Full pytest suite:** Not run per tight-memory brief; only `tests/test_three_way_baseline.py` (fast tier) and targeted check functions in `tests/three_way_baseline_checks.py` were executed.
- **Downstream H4 text / callers on `wt/wt-h4`:** Out of scope for this diff check; any caller that previously read `BaselineRecords.rung_trades` or `rung_moments` (none exist in `20fb4d7`) will read `overlaps` and `rung_alerts` instead.
