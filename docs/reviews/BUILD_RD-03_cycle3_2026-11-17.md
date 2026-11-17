# Red team: RD-03's build, corrective cycle 3 and the test-tier change (Q-119r3) -- 2026-11-17

**Target.** Branch `wt/wt-payout`, the diff ceeb4bf..6ef8a4d (worktree `%LOCALAPPDATA%\stage2-extended-wt\wt-payout`):
3fdc1a1 (cycle 3) and 6ef8a4d (T-3 and the pipeline check marked `slow`). Five files changed: `extended/cl_reading.py`,
`scripts/cl_reading.py`, `tests/cl_run_check.py`, `tests/cl_synthetic.py`, `tests/test_cl_build.py`. Nothing under
`vendor/`, `results/`, `prereg/`, `identity/`; no seed literal added (the added lines grepped for an eight-digit 2026
string: none). I read it against my cycle-1 note (`docs/reviews/BUILD_RD-03_cycle1_2026-11-17.md`), rows E-165 and
E-169, and the pinned `prereg/RD-03_contract_levers.md`. The builder's hand-back itself was not given to me; I judged
its claims as E-169 states them.

**What I ran** (light, toys only, my scratchpad, one at a time; nothing under `results/`; no bar or atlas read; the full
suite not run):

- sections t1, t10 and t15 of `tests/cl_synthetic.py`, each alone, `timeout 1800`;
- `t3_margin.py`: T-3 replayed with the builder's own `_t3_runs`, `_t3_plant`, `t3_leak`, `t3_reach` and `_t3_read`
  on its own toy and plants, counting the early rows each leak moves under each plant and naming the measures
  (1,090 s at one worker; the engine's memory guard dropped two workers to one). **Its first launch crashed**: my
  script lacked a `__main__` guard, and when the guard allowed two workers the spawned child re-ran it
  (`BrokenProcessPool`). That was my tool's defect, not the code's; I added the guard and ran it once more;
- `mutations.py`: each cycle-3 fix undone in memory (no file edited), the section that should catch it run (t14 or
  t17), plus two probes on pure functions.

No seed of mine was drawn; everything replays the build's own toy seed through its own helpers.

---

## Verdict

**Merge after the listed changes** (at its sequenced time). Every item is test or guard code; the pinned text is
untouched and no item changes a declared rule. As a declaration, RD-03 still **stands with readings** (N3 adds one).

- **Sound.** R1, R2, m-a, m-b (the missing line), m-c and notes 2 and 3 are fixed, and each proof fails with its fix
  undone (section 2). T-3's two-form design is sound: the purge-only form is the strict one, and the refusal that
  counts for cycle 1's form hides nothing the purge form does not also have to catch (section 3). A-1 is still inert
  when off: T-1, T-10 and T-15 pass on 6ef8a4d, and no shared adapter is in the diff.
- **To change before merge** (each small): m1, the beside per-year change has no test, and its refusal cannot fire;
  m2, the commit hold accepts any commit named on the row; m3, the `--stage0-stopped` path, now the live path for
  step 3, has no test and does not refuse with a `cl_fit.csv` on the tree.
- **For the lead, not the branch:** m4, the merge checklist's `timeout 1200` cannot hold the suite. m5, T-3's scope
  covers step 3 only; that is owed before step 4 runs, not before merge.

---

## 1. Findings, by severity

No CHANGES-A-CONCLUSION or MATERIAL finding.

### MINOR

**m1. The beside rates' full-year change: the refusal is a tautology, no test fails if the change is undone, and on
the pipeline's toy every beside rate is NaN.**

- **Where.** `extended/cl_reading.py` 1537-1553 (`mechanics_rows_beside`): line 1548 keeps the starts with
  `observed >= U.HORIZON`; line 1549 then calls `year_problems(recs, year, ...)`, which refuses a start whose
  `observed != U.HORIZON`.
- **Evidence.**
  - `observed` is `min(HORIZON, n - s)`, so a start that passes 1548 always passes 1549. The beside refusal cannot
    fire. (In step 3's `mechanics_rows`, line 528, the same check is real: there it guards `block_days`'s
    eligibility, and T-3's full-form leak trips it.)
  - My probe, on a hand-built run of one full-year start (10 evaluations, 2 reactivations) and one start 200
    sessions short: the rates read 10.0 and 2.0 at n = 1, the short start dropped, as intended. With only the short
    start they read NaN at n = 0, **silently**.
  - Nothing in the tests calls `mechanics_rows_beside` (grep). `cl_run_check` runs at 70 sessions, where no start
    has 252 left, so every beside `*_per_year` cell of `cl_menu_beside` is NaN. Before the cycle those cells were
    finite. Nothing asserts them either way. So undoing the change fails no test, and E-169's "each proving test
    shown to fire with its fix undone" does not cover this change (E-169 calls it beyond the brief).
- **Failure it allows.** A later edit back to the all-starts mean, or to some other subset, passes every test. On the
  real window it would understate the rate: about 15 % of the starts have short replays.
- **Remedy.**
  - Drop the beside `year_problems` call, or make it real by applying it to the starts actually averaged and
    refusing an empty set in the real run.
  - Add a fast t17 case that runs my probe: the rate equals the full-year starts' mean, with n their count.
  - In `cl_run_check`, assert that the beside per-year cells are NaN exactly where `--days` is under 252.
- **Faithful to the pinned text? Yes** (section 4).

**m2. The m-b commit hold accepts any 7- to 40-hex token on the row, so any commit the row mentions passes.**

- **Where.** `extended/cl_reading.py` 1061 (`HEX_TOKEN`) and 1064-1076 (`fit_commit_problem`).
- **Evidence** (my probe):
  - On the row `| E-900 | ... stage 0 (cl_fit) from a clean checkout of <A>, the brief at <B> |`, a manifest commit
    starting with `<B>` is accepted (`None`), as is `<A>`.
  - A plain seven-digit decimal on the row (`1234567 paths`) is also a token, and a manifest commit beginning with
    those digits is accepted.

  t17's cases (the row's own commit, short and full; dirty; unknown; another commit; no row; a sha256 prefix) all
  pass. None of them names two commits.
- **Failure it allows.** Stage 0's row will most likely name more than one commit: the run's checkout and the branch
  or merge it came from, as E-166 and E-169 do. A `cl_fit.csv` written at the other one, for example a superseded
  run that the row mentions, is held as the row's. The m7 no-overwrite rule makes this unlikely, but m-b's purpose
  is to make it impossible.
- **Remedy.** Hold the commit only to a token in a fixed place: for example the token after `clean checkout of`, or a
  `cl_fit@<hex>` form the lead writes. Refuse a row that has no such token or has two. Add the two-commit case to
  t17. Requiring at least one a-f letter would also stop a decimal from counting as a commit, but the fixed place is
  the real fix.

**m3. The `--stage0-stopped` path is wired but has no test, and it neither refuses with a `cl_fit.csv` on the tree
nor checks that its row records a stop.**

- **Where.** `scripts/cl_reading.py` 380-381 (`solver_view`) and 267 (`row_problems(..., "cl_fit", ...)`);
  `extended/cl_reading.py` 1033-1039 (`solver_view_text` returns the string as given).
- **Evidence.** The wiring:
  - Real step 3 needs `--stage0-row`, and the row must contain the literal token `cl_fit` (`row_problems`).
  - With `--stage0-stopped`, every Back2Funded and `naf` menu row prints `stage 0 stopped (row E-NNN): no solver's
    view`.

  But:
  - grep finds no test that passes `--stage0-stopped` or a string view, synthetic or real;
  - with the flag set, `results/cl_fit.csv` is never looked at, so a run can say "stopped" while a solver's view
    exists;
  - nothing checks that the named row records a stop rather than a finished stage 0.
- **Failure it allows.** E-172 (the probe's stop) becomes the row this path cites. Two things can go wrong:
  - If E-172 does not contain the token `cl_fit`, step 3 is refused at launch. That fails closed, but it is a
    surprise to a run that is in a queue.
  - If a later stage 0 succeeds and the old flag stays in the command, the menu prints "stopped" beside a real view.
- **Remedy.**
  - In the real run, refuse `--stage0-stopped` when `results/cl_fit.csv` exists. Require the row to name `cl_fit`
    and a stop word the lead fixes, such as `stage 0 stopped`.
  - Add a fast test: synthetic step 3 with `--stage0-stopped --stage0-row E-NNN` puts that string on every L-B and
    L-N menu row, and on no other row.
  - The lead writes E-172 with both tokens.

**m4. Marking T-3 and the pipeline `slow` is right, but the merge checklist's step 3 cannot run the suite in its time
limit, and the fast tier no longer has a look-ahead tripwire for RD-03.**

- **Where.** `tests/test_cl_build.py` 58, 70 and 246; `.claude/skills/merge-checklist/SKILL.md` step 3
  (`timeout 1200 python -m pytest -q -o addopts= -m "not heavy"`); `pyproject.toml`'s `slow` marker ("about a
  minute").
- **Evidence** (E-169's own figures; I did not time the suite).
  - The "not heavy" run includes the slow tier, so T-3 (about 17 minutes) and the pipeline (about 11) still run at
    the merge, inside a 20-minute limit. The tier change does not cause this: the run was already over the limit at
    3fdc1a1.
  - The remaining fast tier is about 21 minutes (49 less 28).
  - `_run` is `lru_cache`d, so `test_section_holds[t3]` and `test_t3_catches_...` share one t3 job in one pytest
    process. Under a parallel runner they would not.
- **Failure it allows.** A merge step killed at 20 minutes and read as "timed out". Or an operator who drops to `-m
  "not slow"` to fit the limit, which skips the only look-ahead test RD-03 has. Between merges, a commit that adds a
  leak passes the hook.
- **Is the marking acceptable? Yes.** /validate runs the slow tier (step 2 is the whole suite), and so does the
  merge checklist's step 3, given a limit that fits. No fast-tier test now covers nothing:
  - T-14 keeps R2, m-a and m-b on hand-built rows;
  - t17 keeps m-b, m-c and notes 1 to 3;
  - `test_starts_...` keeps `--starts`'s refusals.

  `test_the_real_run_excuses_no_guard_entry` is a source-text count, but t17's signature check stands behind it.
  What the fast tier loses is R2 on a written `cl_reading_ftp` file, the exact-excuse check, the `--starts`
  manifest counts (all pipeline-only) and every look-ahead check.
- **Remedy.**
  - The lead raises step 3's limit to fit the slow tier (about 60 minutes on E-169's figures), or runs RD-03's slow
    tests as their own step with `timeout 1800` each.
  - Optionally, a fast tripwire: T-3's no-leak claim alone, on `ref` and the losses plant (two toy jobs of one cell,
    about two minutes at one worker). Its power stays in the slow tier.
  - Fix the `slow` marker's description.

**m5. T-3 covers step 3's reading only; the beside readings' early block has no shift test.** This was there before the
cycle, so it is a new observation, not a regression.

- **Where.** `tests/cl_synthetic.py` `_t3_runs` (response `off`, point arm, `mechanics_rows`).
  `run_beside` builds its rows through the same `reading_rows`, so the ladder, `rtp` and `ftp_*` files carry early
  and late block rows too. The pinned T-3 says "every early-block reading".
- **Failure it allows.** A response model in a beside step reading past an early start's window, through a
  placement or a denial draw that is not path-causal, would pass. The risk is low: the purge is the same vendored
  `block`, and the responses are Q-17's adapter on the vendored engine. But nothing shows it.
- **Remedy (before step 4's run, not before merge).** T-3's no-leak claim and purge-form power at 63 and 252, under
  `rtp` and one `ftp_*` model, on `ref` and `b2f2`, the counted variant included. That is about 3 x 4 one-cell jobs,
  around 10 minutes at one worker, in the slow tier.

### NOTE

1. **T-3's power is per horizon, not per reading, and at two horizons a single measure carries it.** My replay
   (the builder's toy and plants) gave:

   | h | losses plant (purge form) | wins plant (purge form) | full form | what moves |
   |---|---|---|---|---|
   | 21 | 0 rows | 13 rows | the same as purge | `card_S3a` only, all five cells |
   | 63 | row count 3,573 against 3,577 | 475 rows | the same as purge | P, the months 1-3 measures, CVaR10 m3, ... |
   | 126 | row count 3,441 against 3,442 | 154 rows | 261 / 150 rows | the m6 nets and CVaR, Q1, Q2, S5c, ... |
   | 189 | 45 rows | 37 rows | 41 / 33 rows | `net_month_9` only |
   | 252 | 417 rows | 289 rows | refused, all three late blocks | the m12 nets and CVaR, the per-year rates, fees, ... |

   The reach counts are 18, 60, 80, 80 and 80, and the no-leak claim was byte-identical under both plants. The h = 21
   margin is the 13 rows my cycle-1 demonstration found, unchanged under the new `toy(5, i)` draws. The design
   proves that the no-leak claim can fail at every horizon. It does not prove it for each reading: a leak confined
   to, say, CVaR10 at month 6 would be caught only because other readings at 126 move with it in the plant. That is
   what R1 asked for, so this is not a defect. Remedy, cheap: write each (h, plant) count of moved rows into the
   notes beside `T3_LEAK_*_CAUGHT_BY`, so a shrinking margin is on record before it reaches zero.
2. **The purge form's "a row, never a refusal".** `moved` (`cl_synthetic.py` 822) counts any plant whose reading
   differs from `runs0`'s, so a refusal under one plant only would count as a moved row. No current refusal depends
   on the late block (the year check reads `observed`), so this cannot happen today. Excluding `REFUSED` strings from
   `moved` in the purge branch would make the code say what its docstring says.
3. **A wording reading for the lead (the declaration stands with it).** RD-03's 4.3 U-6 labels the conservative
   reading "reactivations counted as purchases: the conservative reading". 10.1 item 8 says "counted: the
   conservative reading". The code (`levers_readings.py` 38) and T-14 use 10.1 item 8's. Record that 10.1 item 8's
   wording governs, the other being its long form.
4. **Where U-6's label sits.** It is on every Back2Funded menu row (step 3's menu: the optimistic label once; the
   beside menu: by variant, once) and on every row of `cl_reading_ftp` that names a Back2Funded cell. It is not on
   the Back2Funded rows of `cl_reading.csv` or `cl_reading_ladder.csv`, and was not at the build's base (42e3f3e)
   either. 10.1 item 12 puts U-3, U-4 and U-6 "on every Back2Funded row" of the menu, and 10.1 item 8 asks for the two
   labels on step 5's readings, so the placement is faithful. If the lead reads 4.3's "on every Back2Funded row" as
   every file, it is one more `label_u6` call in steps 3 and 4.
5. **The year check in step 3 is a toy guard.** On the real window an early start has at least 635 sessions after it,
   so every early start observes 252. The eligibility leak that the check refuses (T-3's full form) cannot arise in
   the early block there. It can arise in the toy, whose late block is 80 sessions. The check is correct and cheap;
   it just has no real-window case.

---

## 2. Each item: fixed, and can its proof fail?

Mutations ran in memory with no file edited. Baselines: t14 and t17 have 0 problems.

| item | fixed? | its fix undone | caught? |
|---|---|---|---|
| R1 | yes: two opposite plants from `toy(5, 0)` and `toy(5, 1)`, the no-leak claim under both, a reach precondition at every h, the xfail removed, `test_t3_catches_...` asserting reach, purge catch and full catch per h | the losses plant alone | yes: 0 rows move at 21 (table above), so the test fails at 21 |
| R2 | yes: `u6_label` by mode, `label_u6` on step 5's rows, the menu's U-6 entry by variant once | `u6_label` always optimistic | t14: 4 problems |
| R2 | | `label_u6` a no-op | t14: 2 problems |
| m-a | yes: `excuse_guard` off by default everywhere, passed only with `--synthetic`, names limited to `GUARD_COLUMNS` | `check_menu` always excusing | t14: 2 problems |
| m-b | yes: the missing line refused | `solver_view_text` printing a missing line | t14: 2 problems |
| m-b | yes, but too loose (m2): the commit hold | `fit_commit_problem` never refusing | t17: 7 problems |
| m-c | yes | `preflight` without the Q-44 loop | t17: 1 problem |
| note 1 | step 3: yes (a labelled rate, the year check). Beside: changed, untested (m1) | `year_problems` a no-op | t17: 1 problem. The beside filter undone: no test (m1) |
| note 2 | yes: `REF_GATE_LABEL` | -- | t17 and `cl_run_check` assert the phrase |
| note 3 | yes: each new cell's guard held to its own `part=row` entry at the bound, at 0 %, not the twin | the old unheld reader | t17: 2 problems |
| NS | yes: `guard_values_n` returns the counts | -- | a refactor; T-3's rows are byte-identical across plants, so the counts did not move |
| `--starts` | yes: refused outside `--synthetic`, in step 3 and below 1, before any import; `run_beside` refuses it again with real inputs | -- | `test_starts_...` (4 cases, nothing written) and t17 |

**The first-run failure (E-169) was diagnosed, not rerun to pass, and the redesign is no weaker.** The cycle's new year
check refused cycle 1's leak form at 252, so no rows could be compared. The builder kept that form, counted the refusal
for it, and added the purge-only form, which must move a row at every h and may not refuse. The purge form leaks a
subset of the full form's starts and must still move a row with no refusal allowed, so it is the stricter test. My
replay confirms the account: full form at 252 refused, purge form at 252 moving 417 and 289 rows.

## 3. T-3's two-form design

- **Sound.** The purge form is the realistic leak: the early block purged short of its measure's horizon. On the
  real window it is the only form possible, because every early start observes 252 (note 5). The test requires it to
  move a row at every h, 21 included, with no refusal allowed.
- **Does counting the refusal for cycle 1's form hide anything?** No.
  - The refusal fires only at 252, and there it fires identically for all three late blocks. So it says nothing
    about the late block; it says the reading refuses short-observed starts, which is itself a real guard.
  - Anything the full form could catch at 252 is either caught by the purge form at 252 (417 and 289 rows), or rests
    on short-observed early starts, which exist only on the toy.
  - At 21 and 63 the two forms are the same leak: on the toy every early start observes at least 82 sessions. At 126
    and 189 both forms move rows.
- **The thin margin at 21: acceptable.** The 13 rows are deterministic on fixed seeds, and they were the same under
  my cycle-1 draws and the builder's.
  - The test fails closed: if a change to the toy or the code makes S3a stop moving, `test_t3_catches_...` goes red.
    The failure protocol then calls for a diagnosis, never a new seed. The seeds are fixed in the code as the toy
    seed's children `(5, 0)` and `(5, 1)`; say so in the docstring.
  - If the margin is ever lost, a stronger wins plant (four winning trades every late session instead of one to
    four) would raise S3a's chance of moving.
  - Record the counts (note 1).

## 4. The full-year-only change: faithful to the pinned text

Section 9.3 asks for "the evaluations bought, activations and reactivations bought per year (D-34's caveat)". 10.1
item 7 asks for "purchases per year ... beside growth, every row". 10.1 item 8's beside rows print the same
(the cycle-1 m5).

- A start whose long replay is shorter than U1's horizon has counted fewer sessions than a year. Averaging it into a
  rate per year understates the rate, so the old beside rate was biased low.
- Step 3's `mechanics_rows` already reads the rate on `block_days(..., 252)`, the full-year starts. The beside change
  brings steps 4 and 5 into line with it, and the menu's `evaluations_bought_per_year` column now means the same in
  both menus.
- The rows say what they read: `PER_YEAR`, and n the full-year count.
- Another faithful reading would scale each start's count by 252 / observed and keep every start. The text does not
  choose between the two, and the build's is the one step 3 already uses.

So the change is faithful. What it lacks is a test (m1).

## 5. Stage 0's stop

E-172 is not in `DECISIONS.md` on master or in the staged changes, so I could not read the probe's answer. On the wiring
alone, `--stage0-stopped` reaches the menu as a string through `solver_view_text`. The real run needs `--stage0-row`,
which must name `cl_fit`. It is read before any purpose is ledgered. It is not tested and not guarded against a
present `cl_fit.csv` (m3).

## What I tried that found nothing

- **A-1's inertness.** T-1 (13.2 s), T-10 (11.7 s) and T-15 (6.3 s) report 0 problems on 6ef8a4d. No file that
  T-15 pins (`user_beside.py`, `gate.py`, `campaign.py`, `levers_path.py`) is in the diff.
- **The no-leak claim under both plants:** byte-identical at every horizon on five cells.
- **The reach precondition** holds at each h (18, 60, 80, 80, 80).
- **m-a's strictness on the real window.** The menu's guard comes from block `all` only (`menu_table`), which always
  holds starts with 252 sessions left. So the real-run refusal of any excuse cannot stop a legitimate real run at
  its end.
- **`label_u6`** labels rows by `mode == counted` even when they name no Back2Funded cell. The only counted rows are
  the Back2Funded cells' and their pairs with `ref`, so no stray label appears. `cl_run_check` uses the same mask.
- **`gate_guard_from_file`'s twin filter** after a CSV round trip ("False", lower-cased): it matches. A non-boolean
  `twin` column fails closed (no row found, refused).
- **`--starts`** composed with U1's own choice (`chosen[::n]`); its manifest records `start_every` and the counts.
- **No seed literal, vendored file, result, record or declaration** in the diff.

## What I could not check

- The builder's hand-back, including its "section 4 item 3" on U-6's placement. I judged the placement against the
  pinned 4.3, 10.1 items 8 and 12 instead (note 4).
- E-172 and the probe's answers; stage 0 itself.
- The suite's real timings. m4 uses E-169's figures.
- `cl_run_check` (the pipeline), not rerun: at about 11 minutes, with about 1 GB free, I chose T-3's replay. Its new
  assertions I read but did not run.
- Anything on the registered data.

---

## Proposed row

| E-NNN | 2026-11-17 | **The red team's re-read of Q-119's corrective cycle 3 and the test-tier change (wt/wt-payout 3fdc1a1 and 6ef8a4d against ceeb4bf; `docs/reviews/BUILD_RD-03_cycle3_2026-11-17.md`): merge after the listed changes, test and guard code only, the pinned text unchanged; RD-03 stands with readings.** **Holds:** R1, R2, m-a, m-b's missing line, m-c and notes 2-3 fixed, each proof failing with its fix undone (in-memory mutations: t14 and t17 report 1 to 7 problems each, 0 at baseline; the losses plant alone moves no row at h = 21); T-3's two-form design sound -- the purge-only form the strict test and the only one possible on the real window, the refusal counted for cycle 1's form firing only at 252 and identically for every late block, hiding nothing the purge form does not catch (the red team's replay of the builder's toy: no-leak byte-identical under both plants; the purge leak moving rows at every h); the h = 21 margin (S3a alone, on all five cells, the same as in the cycle-1 demonstration) accepted because it fails closed, a lost catch diagnosed and never reseeded; the full-year-only beside rates faithful to 9.3 and 10.1 items 7-8 (the old mean ran low on short replays; step 3 already read full years); marking T-3 and the pipeline `slow` acceptable, no fast test left empty; A-1 inert (T-1, T-10, T-15 pass on 6ef8a4d). **Before merge:** (m1) a test of `mechanics_rows_beside`'s full-year rate and its silent NaN, the tautological year check removed or made real; (m2) `cl_fit.csv`'s commit held to one token in a fixed place on the stage-0 row, not any hex token (a row naming two commits accepts either), with a t17 case; (m3) a test of `--stage0-stopped`, and the real run refusing the flag when `results/cl_fit.csv` exists or when the row lacks `cl_fit` and the lead's stop phrase -- E-172 to carry both. **For the lead:** (m4) the merge checklist's `timeout 1200` cannot hold the not-heavy suite (about 49 minutes on E-169's figures): raise it or run RD-03's slow tests as their own step; optionally a two-minute fast tripwire (T-3's no-leak claim on `ref`, the losses plant); (m5) before step 4 runs, T-3's no-leak claim and purge-form power under `rtp` and one Focused Trader model on `ref` and `b2f2`, about 10 minutes in the slow tier. **Readings:** 10.1 item 8's "counted: the conservative reading" governs 4.3 U-6's longer wording; U-6's label sits on the menus' Back2Funded rows and step 5's file, as at the build's base. **Notes:** T-3's power is per horizon (one measure at 21 and at 189), with each moved-row count to be noted; the purge form to exclude a refusal from its moved count. | The red team's note; E-165, E-169; RD-03 sections 4.3, 9.3, 10.1, 14.3. |
