# Red-team read: Q-188b, the merge `97ed1f5` on `wt/wt-levels` (T2b, A15, A16, A17 on the per-date sessions), 2026-11-21

**Target.** The merge `97ed1f5` in `C:\Users\resni\AppData\Local\stage2-extended-wt\wt-levels`. It has three parents:
- `280c537`, wt-levels' lever rows;
- `3cf17d4`, master;
- `e1f877e`, wt/wt-payout.

**What I read.**
- `git diff 3cf17d4 97ed1f5` (16 files);
- `git diff e1f877e 97ed1f5 -- extended tests docs`;
- my earlier note, `BUILD_LEVERS_T7_2026-11-20.md`;
- the consumers of the NY split on this tree and on `wt/wt-play` (read with `git show`/`git grep`, not checked out).

**What I ran.**
- The requested test command, in the worktree.
- Every other check ran in my scratchpad:
  - a shared bare clone (`q188b.git`), with `git merge-tree` and one `commit-tree` there only;
  - an archive of `97ed1f5` (`q188b_tree`) for the mutants;
  - an independent calendar script (`q188b_t2check.py`).
- No bar, no atlas and no result file was read. Nothing dated 2026-07-17 or later was read.

**Brief.** It asks seven questions without hinting at an answer, so I had no hint to set aside.

**Disclosure.**
- I ran `git status --short` twice in the worktree. It is empty before and after. Git may refresh the stat cache of that tree's index when it does this.
- The pytest run may have written git-ignored `__pycache__` files in the worktree.
- I edited nothing else there.

## Verdict: **PASS WITH MINORS** (in the red team's terms, *stands with readings*)

- No finding changes a declared rule or a computed number.
- The five MINORs are guards and readings owed before the first survey or executor that draws or applies these rows.
- My earlier findings L-M1, L-M2, L-m1, L-m2, L-m3 and L-n1 are resolved. L-M2 leaves the residuals m1-m3 below.

| severity | count |
|---|---|
| CHANGES-A-CONCLUSION | 0 |
| MATERIAL | 0 |
| MINOR | 5 |
| NOTE | 5 |

**Tests.** The requested command printed `147 passed in 41.79s`, exit 0, with nothing skipped. So the sampler test `test_the_sampler_draws_the_new_rows` ran, which settles L-m3.

---

## Findings

### m1 MINOR: `components.session_bounds` lets an `ny_am` component run past noon, and an `ny_pm` one start at 08:30 CT (check 3)

- **Where.** `extended/components.py:156-158` sets `cur["ny_am"] = cur["ny_pm"] = ny`, the whole NY session. `Design.__post_init__` (`:190-198`) checks a component's window only against that.
- **Evidence.**
  - `tests/test_components.py:553` builds `Component("mk", "ny_am", 961, 1300, ...)` (13:40 CT) and expects it to pass.
  - `search_space.to_components` (`:1128`) names every whole-NY slot `"ny_am"`.
  - wt/wt-play's `playbook.SPACE_SESSION` maps both NY names to `ny`.
  - Probe on a scratch copy: I made `session_bounds` apply T2b's split. That failed 14 tests in `test_components.py` and `test_search_space.py`, including `test_to_components_gives_the_schedulers_design_on_each_date_pattern`.
  - So the gap is load-bearing. It is not an oversight that can simply be closed.
- **Failure it allows.**
  - A hand-built design (the playbook's, a finalist's sheet) can carry `ny_am` while trading 13:40 CT, and `Design` accepts it.
  - Today nothing reads a component's session label except this bounds check (S1 maps both names to `ny`; the router and the scheduler read slots). So no number is wrong now.
  - The risk is a report or ledger keyed by session, or a later per-session reading (an S1 split at T2b), attributing an afternoon trade to NY AM.
- **Remedy.**
  - Give `Design` a session name `ny` for the whole of NY. Make `ny_am` / `ny_pm` strict at `ny_boundary(day)`. Map `to_components` and the playbook's whole-NY slots to `ny`.
  - That touches wt-play, so until it lands, record the reading in the E-row: "a component's `ny_am` means the whole NY session, unsplit".

### m2 MINOR: whole-NY `ny` stays a sampler session that T2 does not declare

- **Where.** `extended/search_space.py:753-754`: with `ny_boundary=None`, `session_spans` returns `ny`, and `from_lever_space(slots={"ny": ...})` accepts it. T2's declared values are `evening, asia, london, ny_am, ny_pm` (`lever_space.py:110`, the golden's T2).
- **Evidence.**
  - Before this row, the unsplit `ny` was the stand-in for an undeclared T2b.
  - Now T2b is declared, and `check_ny_boundary` refuses only a *wrong* boundary, never a *missing* one.
  - The playbook (wt-play `_starts`, `_bounds`) also reads the unsplit form.
- **Failure it allows.**
  - A survey declaration can draw slots in `ny`, a session that is not a T2 value, or in `ny_am` / `ny_pm`.
  - The two give different spaces: offsets bounded by 398 minutes against 149 and 248 (before rounding to the five-minute grid), and a different count of cells.
  - Neither is forced by the lever table, so the choice is unlabelled.
- **Remedy.** One of:
  - the search declaration states which form it uses and labels `ny` as a declared union cell of T2 (counted);
  - or `from_lever_space` refuses a `ny` slot once T2b loads.

  The playbook's unsplit read is a reading of windows, not a draw. It can stay, with the same label.

### m3 MINOR: `session_windows(day)` splits at `ny_boundary(day)` without checking that T2b loads (check 1)

- **Where.** `extended/lever_space.py:223-226`. The split never consults `bounds("T2b")`. Only `check_ny_boundary` and `_ny_split` do.
- **Evidence.**
  - The worker's own test `test_t2b_is_converted_on_each_date_not_fixed_on_the_ct_clock` declares `("Europe/London", 16, 0)`. Under it, `bounds("T2b")` refuses, but `session_windows` still returns a split that moves between 1020 and 1080 minutes after the reopen by date.
  - Under the **declared** value the two cannot disagree. My independent zoneinfo script, working on the UTC instant, agrees with `LS.session_windows(d)` on all 1042 search-year weekdays (0 mismatches). `ny_boundary` is 1080 (11:00 CT) on every weekday from 2024 to 2030; that is calendar arithmetic only, no data.
  - America/New_York and America/Chicago change clocks on the same dates, so the US/UK mismatch weeks move only London's start, never the split.
- **Failure it allows.** This is latent. Under a later family's declaration on another clock, or a firm's day the loader refuses:
  - the session windows (and so `session_spans` and `session_bounds`) split NY at a value T2b refuses, silently;
  - `check_ny_boundary` refuses any sampler boundary;
  - the playbook path (`ny_boundary=None`), which never calls it, keeps running.
- **Remedy.**
  - In `session_windows`, refuse unless `ny_boundary(day) == bounds("T2b").values[0]`; `_ny_split_days` is cached, so this is cheap.
  - Turn the London test into "`session_windows` refuses".
  - For dates outside the search years (the held-out days), the same equality is the check.

### m4 MINOR: A15 and A17 are now dimensions of Topstep's sampler, and no executor reads them

- **Where.** `search_space.from_lever_space` (`:851-866`) adds every loaded searched `choices` lever as a dimension. A15 (3 values) and A17 (4) now load; T2b `(1080,)` and A16 `("dealt",)` go to `fixed`. `test_the_sampler_draws_the_new_rows` asserts this. `lever_space_firms.sample("topstep")` now draws them too.
- **Evidence.**
  - Nothing in `extended/` or `scripts/` builds a `router.Routing` from a design's `A15`. The only call is the docstring example in `router.py:6`.
  - Nothing calls `lever_space.state_risk`.
- **Failure it allows.**
  - A survey on this space proposes designs that differ only in A15 or A17. Executed today, they give identical paths, yet they are counted and reported as different designs.
  - k is inflated, which is conservative. But a finalist could be reported with `A17 = floor` or `A15 = round_robin` that it never applied: a label not true of the result.
  - Also, every Topstep draw at a given seed differs from master's: the space's d grows by 2 and the dimension order shifts. No survey or declaration is pinned on it, so nothing breaks. Say it in the E-row.
- **Remedy.** Before the first survey on `from_lever_space`, do one of:
  - add the executor's consumption of `A15` (a `Routing` built from the design and its components) and of `A17` (`state_risk` inside `modes_rules.size`'s caller), with a synthetic test that each value changes the path where it should;
  - or hold A15 and A17 out of the sampler (fixed at their base, `longest_waiting` and `none`) until then.

### m5 MINOR: `by_component`'s component order is the caller's, unchecked

- **Where.**
  - `extended/router.py:62-82`: `Routing(components=...)` takes a sequence of names.
  - `lever_space.deal_pools` (`:636`) is documented to take "components in the order of their windows' first slots".
  - Nothing checks that order. The router docstring and the table's A16 row both state it.
- **Failure it allows.**
  - `Routing("by_component", ("pm", "am"))` and `("am", "pm")` deal different pools: the first-opened account goes to whichever component is named first.
  - The component order is a free choice beside A16's one value `dealt`. It is the account-order problem of L-m1 again, at the component side.
- **Remedy.** Build `Routing` from the `Design` (its components sorted by `first`). Or have `Router.route` refuse when the names' order differs from the trades' components' window order on the day. Add one test.

### n1 NOTE: the merge commit carries new work not in any parent

- `git merge-tree --write-tree 280c537 <master+payout>` conflicts in 4 files: the lever table, `components.py`, `lever_space.py` and `test_lever_space.py`.
- `97ed1f5` also differs from that automatic result in 3 more files:
  - `search_space.py`, the `check_ny_boundary` call;
  - the golden file;
  - `test_lever_space_declared.py`, +110 lines;
- In `lever_space.py` it also adds the per-date split (`b = ny_boundary(day)` in place of `bounds("T2b")`).
- I read the conflict resolutions hunk by hunk. They are faithful:
  - master's T7 paragraph is kept, and wt-levels' "T7 has no reading" is dropped;
  - master's per-date T2 row and interpretation 1 are kept, and T2b's row is declared;
  - master's per-date test loop is kept, with the T2b assertion added;
  - `__all__` is the union.
- The new work is reviewed here. A reviewer reading only `git show 97ed1f5`'s combined diff would miss it, so the lead's row should name `97ed1f5` as Q-188b's build, not only as a merge.

### n2 NOTE: the golden rewrite needs its decision row

- `scripts/lever_space_golden.py`'s docstring says: "Rewrite it only under the lead's decision row".
- The rows cite "E-NNN pending". E-254 (4) records the rows as built, but not the snapshot rewrite.
- The 8 changed entries (check 4) are each explained by the declared rows:
  1. **T2.** Only `ny_am`'s end and `ny_pm`'s start change, None to 1080, in the range and in all 3 distinct window sets. The day counts are 362, 65 and 615, total 1042. My recomputation reproduces each set: 65 = 15+5, 10+5, 10+5, 10+5 days of US/UK mismatch, spring and autumn of 2020 to 2023.
  2. **T2b.** `NotDeclared` becomes `fixed (1080,)`, with key `trading_hours`.
  3. **A15.** `NotDeclared` becomes `choices` of `ROTATIONS`.
  4. **A16.** `NotDeclared` becomes `fixed ("dealt",)`, and its class moves from searched to declared.
  5. **A17.** `NotDeclared` becomes `choices` of 4. Its keys are the three it reads, and A5 is added to its dependencies (the funded b*). Its figures (3000, 2000, b* 4000 and 6000) come from the rules, not typed.
  6. **`__space__`.** The four rows are added.
  7. **`__refusals__`.** The four rows are removed.
  8. **`__counts__`.** Account policy goes from 16 searched / 3 declared to 15 / 4.
- Nothing else changes; the worker's bit-for-bit test against 3cf17d4 asserts this, and it ran in the worktree.

### n3 NOTE: stale "to declare" texts

These still say T2b is undeclared:
- `search_space.py:1114` ("until T2b");
- `tests/test_search_space.py:180` ("T2b is to declare");
- `extended/s1_range.py:22` ("split at T2b, still to declare").

### n4 NOTE: the executor-level helpers do not know the firm

- `router.Routing` and `Router` serve every firm's accounts with one rotation. `deal_pools`, `state_risk` and `check_ny_boundary` take no firm.
- The per-firm refusal of A15, A16, A17 and T2b (check 5) holds at the loader:
  - `LF.levers` has `TODECL` for all four at MFFU and Lucid;
  - `LF.bounds` raises `NotDeclared`;
  - `vs_topstep` returns `differs` before any identity test;
  - both tables say "to declare for this firm";
  - `mffu_session_windows` leaves NY unsplit.
- Nothing stops a caller from routing MFFU's or Lucid's accounts with Topstep's declared rotation or state rule. That would carry Topstep's values over by the back door.
- Add a guard (the firm's own A15 must load) when the multi-firm executor is built.

### n5 NOTE: the opening index counts route calls, not dates

- `Router.day_no` increments per `route()` call.
- If a caller routes one date in two calls, accounts first seen in the second call rank after those in the first, not by id.
- The docstring says "the route call (the day)". Keep one call per date, and say so in the journey engine's contract.

---

## Earlier findings: their state

| finding | state on 97ed1f5 | evidence |
|---|---|---|
| L-M1 | resolved | The fixture `no_s1_reading` pins `T7_PATH` with `raising=False`. The bit-for-bit test pins both readings on the old module and the new one. The golden script's `pinned()` covers S1 and T7, and `test_lever_space_firms` has an autouse pin. |
| L-M2 | resolved, residuals m1-m3 | `session_windows(day)` splits at T2b. `check_ny_boundary` sits in `check_design` and `session_spans`. The router deals the pools itself, refuses a mapping, and refuses `by_component` without components. Mutants M5, M7 and M8 below are caught. |
| L-m1 | resolved | `deal_pools(opened=)` sorts by (index, id). `Router.opened` records the first route call. The test passes three caller orders. Mutant M6 is caught. |
| L-m2 | resolved | The parametrised refusal now includes London 16:00 and New York 16:10 (the 15:10 CT flat), and the floor-binding case is `room = start/8`. Mutants M1, M2 and M3 are caught. |
| L-m3 | resolved | The sampler test ran, with nothing skipped (147 passed). |
| L-n1 | resolved | `ny_split_local`'s citation names `late_morning` (D-244, D-245). `test_t2b_matches_stage_twos_late_morning_window` reads the vendored `session_setups.yaml`, and the two agree at 11:00. |

## What I tried that found nothing

- **Check 1: T2b across daylight saving.**
  - My zoneinfo script (built on the UTC instant, independent of the loader's code path) agrees with `LS.session_windows(d)` on all 1042 search-year weekdays.
  - I listed 16 edge dates: the Friday and Monday around every change of 2020 and 2023, US and UK, spring and autumn. Asia and London move by date; the split is 1080 throughout.
  - The worker's test that derives the DST rule from the calendar (`_us_changes`) checks that the UTC hour moves 16 to 17 while the New York clock stays at 12:00.
  - Aware-datetime arithmetic: the reopen is built as midnight CT minus a day plus 1020 minutes. That is wall-clock arithmetic, so it lands on 17:00 local whichever offset applies. The subtraction crosses two zones, so it is in UTC. Both are right.
  - No weekday holds a clock change, which happens at 02:00 on a Sunday.
  - `_ny_split_days` is cached by (local time, reopen, last entry); a monkeypatched declaration gets its own entry.
- **Check 2: the sampler change.**
  - `session_spans` with `ny_boundary=None` returns `ny = (ny_am[0], ny_pm[1])`, the same values as master. So wt-play's `_starts` (`session_spans(day)`) and `_bounds` (`session_slots()`) see unchanged windows.
  - With 1080 the output equals master's, which accepted 1080 already. Only other values, strings and booleans are now refused.
  - wt-play uses its own `Space`, not `from_lever_space`.
  - The behaviour change that does exist comes from `lever_space` (m4), not from `session_spans`.
- **Check 5.** Covered under n4.
- **Check 6: the merge.**
  - `git merge-tree --write-tree 3cf17d4 e1f877e` merges cleanly to tree `20e1a9b`.
  - `git diff 20e1a9b 97ed1f5` touches exactly 9 files, all wt-levels' own: the lever table, `components`, `lever_space`, `router`, `search_space`, the golden, `test_lever_space`, `test_lever_space_declared` and `test_router`.
  - `rules_extended.yaml`, `RULES_CURRENCY.md`, the MFFU and Lucid tables, `lever_space_firms.py`, `test_lever_space_firms.py`, and every master file outside those nine are byte-equal to the clean merge.
  - The worker's claim holds. It is nine files, not eight; the "eight" in the brief counts golden entries.
- **Check 7: reads.**
  - The added lines read no bar, atlas, parquet or result file.
  - New dates appear only in rule-ledger text: wt-payout's help-centre dates and `clock.reference_days` (2023-01-17 and 2023-07-17, inside the search years).
  - `ny_boundary` and `anchored_starts` are calendar arithmetic. My 2024-2030 probe used the calendar only, not NQ.
- **Mutants**, on a scratch archive, against `test_lever_space_declared.py`, `test_router.py` and `test_lever_space.py`:

  | mutant | what it does | result |
  |---|---|---|
  | M1 | removes T2b's one-value check | 2 failed |
  | M2 | upper bound `b <= 1330` | 1 failed |
  | M3 | removes `floor_target`'s floor half | 1 failed |
  | M5 | removes the sampler's `check_ny_boundary` | 1 failed |
  | M6 | router deals without the opening index | 1 failed |
  | M7 | splits at `bounds("T2b")` in place of per date | 1 failed |
  | M8 | removes `check_design`'s T2b check | 1 failed |

  All are caught.
- **Tier 1.**
  - `state_risk` is unchanged (never above r).
  - The router still gives one account per trade, and the book refuses opposite positions (`test_router.py` passes).
  - No automated entry.

## What I could not check

- **The bit-for-bit test against 3cf17d4 in my scratch archive.** It skips there, having no git history. It ran (not skipped) in the worktree.
- **Behaviour under a present `results/t7_forecast.csv`.** None exists in the worktree or in the main tree. The pins are right by reading, and L-M1's probe is not repeated, because I may not write the worktree.
- **Early-close days.** NY PM runs to 1330 on every weekday, including early closes (for example 12:15 CT). This predates the merge, and the void and calendar rules handle it elsewhere.
- **tzdata.** The tzdata version on another machine; US rules have been stable since 2007.
- **wt-play's merge with this tree.** Its `tests/test_lever_space.py:224` still asserts `ny_am[1] is None` and will conflict or fail when merged. That is the lead's merge to resolve, not a defect here.
