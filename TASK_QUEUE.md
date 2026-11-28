# Task queue

Ranked: work that can cancel later work comes first. Only the lead edits this file (E-005); a worker's hand-back
proposes changes. Something needed that is not here is added under a decision row before it is done.

**Columns.** `owner` is the worktree (`%LOCALAPPDATA%\stage2-extended-wt\<owner>`, branch `wt/<owner>`) or `lead`
(on `master`) or `scout` (a read-only agent, no worktree). `state`: queued / running / review (hand-back in, the
lead's merge checklist pending) / done / blocked / NEEDS_OPERATOR. `weight`: **light** (reads, code, unit tests on
synthetic data with a time limit, small checks -- run in parallel) or **heavy** (reads the full bars, a solve, a
campaign, the engine beyond a few paths -- one at a time, under `run.lock`). `retries`: corrective cycles used of the
two allowed (DIRECTIVE Part 5 step 3); a third is `NEEDS_OPERATOR`.

Rows whose state begins with `done` are moved, verbatim and under their section, to [`docs/archive/TASK_QUEUE_ARCHIVE.md`](docs/archive/TASK_QUEUE_ARCHIVE.md) by `scripts/archive_queue.py` (Q-147).

## Phase 0 -- set up, then check the research is right (bootstrap Part 4)

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|

## Phase 1 -- research tracks (bootstrap Part 6; families start only after Q-08)

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-13 | ~~F-01 stages A-D~~ **withdrawn (E-007; k = 10 spent)**; a corrected level family waits for the operator's answer on judging | wt-levels | withdrawn | -- | -- | 0 | E-007 |
| Q-17 | **The readings beside every user measure** (E-007 (e)): an adapter in this repository replaying a design's starts under the denial ladder, the placement on, the binding Focused Trader models and all-accounts forfeiture (the vendored replay hard-codes 0 %: `customer_slices.py:232`), plus P by month, mean net, CVaR10, P under a bankroll limit, n_eff and the MDD | wt-user | built and merged (E-024); the reading is Q-44 | Q-05 | heavy | 0 | E-007 |
| Q-20 | **The breakeven move's fidelity** (E-012 (2)): re-walk P-14's and P-16's trades with (a) the stop-first tie after the move (the walk books the target today, `fv3_rung_walk.py:184-185`) and (b) the move made five minutes after the session open (D-266), each alone and both; read P, the guarded measures and the gate beside the registered rows (exploratory, from a clean checkout) -- R\* itself rests on it | wt-user | built and merged (E-024); the reading is Q-45 | Q-17 | heavy | 0 | E-012 |
| Q-38 | **Family R drafted**: resolution forecasts (HAR-type volatility from closed bars only) for mark admission, the opening's R and freeing the firm's slot (the scout's B1); its pass line marked as Q-36's | wt-lit | closed: not judgeable on this block (E-086) | E-021 | light | 0 | E-021 |
| Q-45 | **Run Q-20's reading** from a clean checkout: `python scripts/run_clean.py --name breakeven-fidelity --task Q-20 --hours 4 --mem-gb 1.8 -- python scripts/breakeven_fidelity.py`, watched | lead | collected and audited (E-188, E-189): corrected figures not re-derivable; Q-132 | Q-44 | heavy | 0 | E-024 |
| Q-46 | Exploratory: Stage 2 D-566's buffer reading checked (F-P's Appendix A -- D-564's six cells on P-16 at 20 paths with a daily recorder, sit-days counted, two controls at zero), its own row | lead | queued (after Q-45) | Q-45 | heavy | 0 | E-025 |
| Q-47 | **The gate rebuilt in `extended/`** so a design can declare another funded-account class (F-P's held-state policy needs it), held to P-14's and P-16's 500-path gate identities (heavy, under the lock) | wt-payout | built (E-028); its 500-path identities are Q-51 | Q-42 | light; the identity heavy | 0 | E-025 |
| Q-90 | Family R's third draft: E-051's null (the realised lift; the pick's own term dropped; the 3 sourced or dropped; the conjoint MDL) | wt-levels | cancelled: family R closed before its pin, every cell dropped by its own rule (E-086) | Q-78 | light | 0 | E-057 |
| Q-95 | The red team's sixth read of family B (after the slow-marker commit) | wt-user | parked: family B's C1 rests on the failed one-sample statistic (E-094); after Q-108 (E-101) | Q-81 | light | 0 | E-060 |
| Q-98 | Q-86's reading from a clean checkout (`scripts/user_spend.py`) -- the heavy queue | lead | queued: the heavy queue part 4, from f7eda0d (E-112) | Q-86, Q-97 | heavy | 0 | E-062 |
| Q-103 | Where components would meet (a supply count, no outcome): on P-16's and P-14's choice-block U1 replays, how often a new funded account's opening, an 08:30 resting ticket's reachable account and a 09:05-15:05 mark would contend for the same position or account | wt-user | parked: until a component is judged (E-133) | Q-35, Q-94 | heavy | 0 | E-072 |
| Q-108 | The one-sample pass line re-calibrated: candidates, nulls (fresh subsets of persistent nulls among them), calibration seeds and separate validation seeds all declared before any run | wt-verify | pinned (E-115); its build Q-108d, then the red team, then the two heavy runs | Q-83 | light (design) / heavy (runs) | 0 | E-094 |
| Q-109 | F-03's build (family O: the seam, the gating wrapper, the replay recording joins, A0 under its own row) | wt-lit | merged (E-135) | E-095 | light | 0 | E-095 |
| Q-112 | The identity block (E-123): Q-80, Q-89 (both legs), Q-101, Q-93 with Q-100, t10w2, RD-01's own identity; then RD-02's own after Q-44 | lead | queued: the heavy queue part 5 (E-123) | E-122 | heavy | 0 | E-123 |
| Q-18b | P-14's stress checks completed per the audit (A2, D-583's missing readings, ruin beside, assumptions labelled) | wt-features | merged (E-135); its check and run queued last | E-125 | light (build) / heavy (run) | 0 | E-132 |
| Q-116 | Draft RD-03: contract-use levers on the registered trades (described, E-023 (1)), a solver-only fit read first; the red team before the pin | wt-payout | pinned as RD-03 (E-152); its build next, after Q-115's merge | Q-115 | light | 0 | E-134 |
| Q-119 | RD-03's build from its pin (adapters A-1..A-6, T-1..T-15, the two identity scripts, stage 0's evaluator, the runner) | wt-payout | built through cycle 4 at 3d55ad5 (E-183); stage 0 stopped (E-172); merged with Q-115 and Q-129 after the RD readings, the red team reading cycle 4 then | E-152 | light | 0 | E-153 |
| Q-121 | Volatility drift (a1): the early-block descriptive by year -- session range in points and percent, side-free first-exit times of fixed bands, the gate files' `period`/`drift` rows -- built light, run once under run.lock, deciding nothing | wt-verify | collected and audited (E-177, E-179); the file local only, a licensed-price derivative | E-157 | heavy | 0 | E-157 |
| Q-122 | Volatility drift (b): regime-bucketed and equal-weight-block readings beside `cons` in the family template (never deciding; no pinned file edited) | wt-verify | queued (E-157), after Q-121's build | E-157 | light | 0 | E-157 |
| Q-123 | Volatility drift (c, a2): draft one described reading -- the calm-regime replay of P-14 and P-16 (k = 1 identity first) and the whole-window descriptive under a non-choosing purpose -- then the red team | wt-scout | pinned as RD-04 (E-168); its build next | E-157 | light | 0 | E-157 |
| Q-127 | T-15's pre-read form extended to a declared substitution diff (a family pin's F-number and k placeholders only, checked against git), before RD-04's step 2 runs (E-168) | wt-scout | closed unbuilt (E-170): 9.3 forbids it; the lead's route within 9.3 replaces it | E-168 | light | 0 | E-168 |
| Q-126 | A second one-sample calibration plan (E-161): scope D first (`cons_m` multipliers, C6), Q-108's null class kept, drift nulls beside, the exact-subset calibration sized to the validation's exposure, new seeds; a scope-Q margin only under that sizing; drafted, red-teamed, pinned before any run | wt-verify | parked (E-208) | E-161 | light | 0 | E-161 |
| Q-126g | Build Q-126's plan (`extended/lift_one_sample2.py`, the runners in declared parts, the provenance assertion, the balance limit in scope D's admission) on synthetic data; the red team's read; then its calibration and validation runs, one at a time under the lock | wt-verify | built and merged (E-195); its calibration queued under the lock | E-187 | light | 0 | E-187 |
| Q-129 | Extend the vendored snapshot (`vendor_stage2.py --extend Q-129`) with v12's two rung files and D-559's two files from f1b42e2, each checked against its manifest; landed with the Q-115 and RD-03 merge, then every identity re-held | lead | queued (E-172) | E-156, E-172 | light | 0 | E-172 |
| Q-132 | The breakeven-fidelity reading, second version (E-189): per-start rows, P-15 included, paired intervals, assumptions stated, a new file; then its run under the lock and the auditor | wt-user | built and merged (E-194); its run queued | E-189 | light | 0 | E-189 |
| Q-133 | F-03's A8 path: `extended/opening_wait.openings` keeps the risk columns so the realised-risk reading is computed, with a test that fails on the empty column; the Benjamini-Hochberg and Table 9 readings computed from the file where possible -- for the record, the family stays closed | wt-lit | queued (E-192) | E-192 | light | 0 | E-192 |
| Q-135 | Multi-firm terms, $50K (E-196): Topstep, Lucid, Alpha Futures, My Funded Futures -- each account type's evaluation and funded rules, consistency, payouts, conduct, new releases, flip-day facts, from official pages (Q-135a-d scouts); then the verified record and a declared described reading | scout -> rules-verifier -> drafter | read (E-197): Topstep and MFF read; Alpha and Lucid by the operator's hand (item 11) | E-196 | light | 0 | E-196 |
| Q-136 | The rules-verifier records Topstep's Labs $50K rows (#006, #010/#011, from the lead's verbatim capture) and My Funded Futures' $50K plans (Rapid EOD and Builder first, then Pro, Pro One Day, Rapid) from the notes, each re-read verbatim on the firm's own page | rules-verifier | recorded on wt/wt-firms 205fc42 + Q-136b 1c9f34f; merges in the sequenced merge | E-197 | light | 0 | E-197 |
| Q-137 | A described reading, drafted and red-teamed before it is built: the evaluation and the funded account as two trading modes per plan, flip days against each consistency rule, each plan's zero-edge map and sizing grid, the registered trades beside | drafter | pinned (E-200): RD-05 at its third text; the build queued as Q-138 | E-197 | light | 0 | E-197 |
| Q-139 | Q-17's reading, second version (new files; Q-44's never overwritten): per-start fees and pay days so S3c and S5b re-derive under every response, `mdd_P` filled by Q-16's calibrated comparison, the identity rows' response labels, the provenance line and variants, the assumptions in the manifest; and a diagnosis of the Slowdown models raising P and Corrective purchases' non-monotone threshold, at the engine | wt-user | queued (E-201) | E-201 | light | 0 | E-201 |
| Q-140 | The sequenced merge on wt/wt-verify: RD-03's build (3d55ad5), the rules record (1c9f34f), Q-129's vendor extension, Q-134's light modes for `scripts/cl_reading.py`; then every identity re-held once at the merged commit (RD-01's and RD-02's re-queued there) | wt-verify | merged (E-205); the identity block registered and queued | E-202 | light | 0 | E-202 |
| Q-141 | Draft the per-firm protocol family (proposed F-04, k = 13): stage A each plan's whole grid on the choice block, described; stage B the per-firm pick judged once; latency 5/3/2 and limit entries as counted dimensions; news closed | wt-scout | recast (E-208): lever space and survey engine | E-202 | light | 0 | E-202 |
| Q-143 | Draft RL3, resting levels from F-02's approved text on Q-126's adopted line (proposed k = 14); news closed, latency 5/3/2 counted | wt-levels | recast (E-208): an NY AM component | E-202, E-065, E-187 | light | 0 | E-202 |
| Q-144 | Draft B-ON, a side model on P-16's overnight offers (proposed k = 15), and the overnight feature extension on synthetic bars; limit entries and latency 5/3/2 counted; news closed | wt-features | parked (E-208): features kept | E-202, E-187 | light | 0 | E-202 |
| Q-145 | The shared family statistics module (B2's critical values, the conjoint MDL, the screen rule, the pre-pin power gate) with level and power tests on toys, and the repository family template | wt-infra | merged (E-204, e79df80) | E-202 | light | 0 | E-202 |
| Q-146 | RD-03 after its merge: the stage-0 commit token (S1), the toy cases for the denial responses and b2f2 under `rtp` (S2), refusing duplicate rule keys with a test (S3) | wt-payout | queued (E-202) | E-202 | light | 0 | E-202 |
| Q-138b | RD-05's part F: the registered trades on each plan (account classes on lockstep, A-14 on the replay and gate, A-18 in the replay, the flip on the registered trades, the ladder, placement and gates, RD-02's honesty import, T-2, T-4, identity (c), (d) and `modes_identity`) | wt-firms | queued (E-205), after the coin side merges | E-205 | light | 0 | E-205 |
| Q-148 | Q-15 extended: worse fills of one and two ticks, declared and counted; a per-arm child-process option in `scripts/run_clean.py` (one BLAS thread, memory freed between arms), every output through `write_result` and the ledger | wt-verify | queued (E-205), Q-15's own waits stand | E-205 | light | 0 | E-205 |
| Q-149 | Family B's redraft (Q-23) over two to four trade shapes (stop, target, horizon) fixed from RD-03's and RD-05's mechanics before any outcome, each a counted cell, power shown before the pin; Q-145's B2 finding in view | wt-features | parked (E-208) | E-205 | light | 0 | E-205 |
| Q-150 | A short standing challenger brief (wt-scout) before any pin at k = 13: raw P against bankroll-guarded P, a dominating stop, target or firm shape, non-monotone responses (Q-139), choice-block power at the level, survival at one tick worse | wt-scout | standing (E-205) | E-205 | light | 0 | E-205 |
| Q-151 | Lever-space extraction: F-04's 6.1/6.3, RL3's 6.1, RD-03's and RD-05's levers and F-R's range forecast as one lever table (ranges from verified rules; volatility units from the search years only) for the design-search template | wt-features | queued (E-208) | E-208 | light | 0 | E-208 |
| Q-153 | The three-way test's design note and build (E-208's brief): the antithetic and disjoint-seed nulls, the planted-shift power check, the per-horizon overlap calibration, the time legs as consistency conditions; red team before H3 | wt-verify | queued (E-208) | E-208 | light | 0 | E-208 |
| Q-172 | The exact-run difference count on P-14's search years (MEASURES section 6), a clean run, counts only | lead | queued (E-232) | E-232 | heavy | 0 | E-232 |
| Q-179 | Q-173 merged with the O-7 pins' SUPERSEDED fill; every shared identity re-held once at that commit | lead | queued (E-246) | Q-173, Q-178 | heavy | 0 | E-246 |
| Q-182 | The lever rows T2b, A15, A16 and A17 declared and loaded -- then red team | wt-levels | closed (E-293: remainder in Q-203; the red team's read of the four rows not found on record) | E-232 | light | 0 | E-246 |
| Q-187 | H3: the three-way test's null calibration and power runs (heavy, parts of 8 h at most) | lead | running (E-295: slots A1, A2, A4 under run.lock; A3 deferred to H3-D) | Q-167 stands, Q-170, H3's pin | heavy | 0 | E-246 |
| Q-188 | H4: the re-baseline -- the four baselines through the journey scorecard on the search years (the first real reading) | lead | held (E-289: no H4-B output used until Q-188b closes) | Q-184 pinned, Q-185, Q-187, Q-172's search_cut | heavy | 0 | E-246 |
| Q-189 | W42-R2 applied to H4's readings (`scripts/wave42_r2_apply.py`, pinned E-299); the limits, budgets, weights and delta* pinned in one row before the survey | lead | queued (E-299) | Q-188, Q-221 | light | 0 | E-246, E-296, E-299 |
| Q-190 | The Wave 5 Topstep design survey, then the MFFU and Lucid surveys | lead | queued (E-246) | Q-186, Q-189, Q-168 stands, Q-177, Q-180, Q-181 | heavy | 0 | E-246 |
| Q-191 | O-7's builds RD-06 to RD-10 on the search years (each with its own identity), then their readings | wt-firms | queued: pinned (E-268 to E-272), builds next | Q-178, Q-172's search_cut | light, then heavy | 0 | E-246 |
| Q-198 | The sizing experiment on the three-way runner (after its follow-up) | wt-three | queued (E-255) | Q-187 | light | 0 | E-255 |
| Q-201 | Narrow the reader's `identity` route to the seal (the red team's NOTE-1, READER_Q194): a ruling on the existing identity rows first | lead | queued (E-267) | Q-194 | light | 0 | E-267 |
| Q-202 | Two heavy pipeline tests red since Q-158 at the latest (`test_q35_openings`, `test_user_spend::test_the_pipeline_on_four_starts`): a failure on record, diagnosed | wt-verify | queued (E-267) | Q-194 | light | 0 | E-267 |
| Q-203 | Wire A15 (Routing from a design) and A17 (`state_risk`) into the executor, then release the hold | wt-levels | queued (E-261) | Q-200 | light | 0 | E-261 |
| Q-205 | The playbook's live path: a declared live calendar and a caller that passes the day's bars | wt-play | queued (E-267) | Q-175 | light | 0 | E-267 |
| Q-206 | A guard on bare-name imports of the four shared script names (the Q-204 root cause) | wt-report | queued (E-273) | Q-204 | light | 0 | E-273 |
| Q-208 | The pre-merge-commit hook (a merge commit verified like any other) | wt-report | built on wt/wt-report, not merged (E-280, E-293) | Q-207 | light | 0 | E-273 |
| Q-209 | A tiered fast tier: records-only, changed-file selection with the always-on guards, the full tier at merges and a branch tip; the guards' pre-flight as its first stage | wt-report | built on wt/wt-report, not merged (E-280, E-293) | Q-208 | light | 0 | E-274 |
| Q-188b | H4's fixes after the audit and the re-check: F-3 (the sigma-rule drops) diagnosed first, B-1, F-2's coin identity, B-2's exact-run classification, tests that can fail, rc-3 disk, labels, the worker-count lever, P-15 p5's re-run | wt-h4fix | running (E-289) | Q-188 | light | 0 | E-289 |
| Q-214 | The first design search's draft, `DRAFT_F-13` (Topstep NQ survey), W42-R1's values blank | wt-fs1 | running (E-298: fix pass after the red team's BLOCK and the form read) | - | light | 0 | E-290 |
| Q-215 | The survey's real-bar route: wire the lever space to `extended/design_trades.py` (after Q-213) | - | queued (E-290) | Q-213 | light | 0 | E-290 |
| Q-216 | H3-A's report code and runner after BUILD_H3A_REPORT's BLOCK | wt-h3a | done (E-295) | Q-187 | light | 0 | E-290 |
| Q-217 | The test-encoding defect: `_git` helpers decode `git show` with utf-8 (in Q-188b) | wt-h4fix | running (E-289) | - | light | 0 | E-289 |
| Q-218 | The seed guards' literal scan: no match inside a decimal value (digit boundary on both sides, '.' included) | - | queued (E-290) | - | light | 0 | E-290 |
| Q-220 | The race's law and draws made faster in `extended/` under a refusing bit-for-bit identity (and the per-lane SharedDayDraws rebuild) | - | queued (E-292) | Q-219 | light | 0 | E-292 |
| Q-221 | W42-R2: one floor limit on the median `net_month_12` (h 252), its value only from the formula; red team and a power check before its pin | wt-w42r2 | done (E-299: merged and pinned) | Q-176 | light | 0 | E-293 |
| Q-223 | F-13's exact-bound screen: gate keys on the trade table before the campaign; plateau gate-first; lazy real-path arms; baseline arms once per protocol; identities S-I1 to S-I3 | wt-survey | queued (E-294) | Q-215, Q-189 | light (S-I3's real-bar part heavy) | 0 | E-294 |
| Q-224 | MEASURES rows 28 and 29's stress arms (missed, late, worse fills) for F-13's finalists, as declared in F-13 | - | queued (E-294) | F-13's pin | light | 0 | E-294 |
| Q-225 | Parameterised trigger sources (the breakout's k, the marks' step and window), each with a shift-invariance test | - | queued (E-294) | Q-215 | light | 0 | E-294 |
| Q-226 | The fast tier's duration: per-test durations from one full run, then shared fixtures and smaller synthetic sizes only where the same mutants still die; no selection, no skipped test | - | queued (E-294) | memory | light | 0 | E-294 |
| Q-228 | The Mac as a second run host: setup (OPERATOR_SETUP item 12), the engine identity, then the exact H4 slice gate | operator, lead | running (E-298) | Q-229's port | heavy (the slice, on the Mac) | 0 | E-298 |
| Q-229 | macOS port of the clean run and the lock (store links excluded, memory from vm_stat), then the Mac run agent after Q-228's gate | wt-mac | running (E-298) | - | light | 0 | E-298 |
| Q-121c | A bars spot-check of a few choice-block sessions' ranges against Q-121's file (C2), before RD-04 uses its reference | lead | queued (E-179) | E-179 | heavy | 0 | E-179 |
| Q-14 | Family B declared (one pre-registered classifier, purged walk-forward, judged out of fold against the coin) | wt-features | blocked | Q-08, Q-11 | light | 0 | -- |
| Q-15 | Stress checks of Stage 2 D-663 on any candidate; the audit's engine fixes | wt-verify | blocked | a candidate; Q-08 | heavy | 0 | -- |

## Done before the bootstrap (the handoff's section 7)

- [x] Charter -- `CHARTER.md` (E-001).
- [x] Stage 2 vendored read-only with its identity -- `vendor/stage2/`, `identity/stage2_identity.py`, `tests/` (E-002);
  the gate-row identity holding at all 500 registered paths of P-14 and P-16 from a clean clone (E-004).
- [x] First family declared before it is built -- `prereg/F-01_resting_order_level_atlas.md` (E-003).

## Later sides (handoff 3.3), each a family declared in its own row

- Payout policy for a user's first months (tested in Stage 2 for long-run growth only).
- Closing a crippled funded account at request -- only once Topstep answers (`docs/OPERATOR_SETUP.md` item 3).

## Closing checklist (CHARTER section 5)

- [ ] every declaration and outcome on record; the decision log complete
- [ ] every number in a document traced to a result file with a manifest
- [ ] `vendor/stage2/` unedited (`tests/test_vendor_integrity.py`) and its identity holding
- [ ] (A) a carried design, registered, audited and confirmed on unread data -- or (B) the documented negative result
