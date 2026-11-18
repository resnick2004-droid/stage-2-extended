# Audit: Q-45, the breakeven move's fidelity reading (`results/breakeven_fidelity.csv`) (2026-11-17)

**Verdict: defects found -- one, a provenance defect, not a wrong number.** Every number I could re-derive agrees
with the file. That covers the registered/`stage2` rows (296 scorecard, extra and path rows rebuilt from Stage 2's own
start rows; 60 gate values against the registered gate files), the trades section's internal arithmetic, and every
internal identity across the four rule sets. The provenance is what the manifest says. No read touched 2026-07-17 or
later. Nothing was chosen or carried.

**The defect:** for the three corrected rule sets (`stop_first`, `delay5`, `both`), the file holds only summaries:
no per-start, per-path or per-trade rows. So **none of the corrected figures -- the reading's whole content -- can be
re-derived from the file**. Under the audit rule, they cannot be cited as independently checked figures. They rest on
the runner's own refusing checks (all held) and the walker's synthetic tests.

Method: my own pandas/numpy code (`docs/audits/scripts/q45/rederive.py`; its full output is
`docs/audits/scripts/q45/rederive_output.txt`). It reads the result and its manifest, Stage 2's registered
`vendor/stage2/results/user_journey.csv`, `a3_brk30_cb20_gate.csv` and `rc_s150_all_gate.csv`, the read ledger, the
bars' `manifest.json` and `vendor/DATA_MANIFEST_stage2.sha256`. It imports nothing from `extended/`, `scripts/`,
`identity/` or `vendor/`. Nothing was rerun. No bar, atlas file or engine was touched. I read the producing code
(`scripts/breakeven_fidelity.py`, `extended/breakeven.py`, `extended/user_readings.py`, `extended/user_measures.py`,
and Stage 2's `u_select.py`/`user_journey.py`) only to learn what each column means. Below, "`section`/`measure`"
names the CSV's columns; `rules` is the rule set.

## 1. What was audited

| item | value (source) |
|---|---|
| file | `results/breakeven_fidelity.csv`, 3430 rows (I count 3430 = manifest `rows`); columns equal manifest `columns`, in order |
| sha256 | my `hashlib` hash equals manifest `sha256` (`340669649c...e620`), the figure E-188 records |
| script, commit | `scripts/breakeven_fidelity.py` at `f7eda0d02e31daea7bfb92847f4ad1203cef014e` (on `master`; `git branch --contains`), `git_dirty` false |
| clean run | `provenance.clean_run`: checkout `%LOCALAPPDATA%\stage2-extended-runs\breakeven-fidelity`, marker `S2X_CLEAN_RUN`; the log `breakeven-fidelity.log` lies beside it and ends `EXIT 0`; the checkout is gone |
| timestamp | manifest `2026-11-17T23:47:41+00:00`; the ledger line's `when` is `2026-11-17T20:56:47+00:00`. Manifest `parameters.seconds` closes the gap |
| seeds | manifest `seed` 20261920 (Q-17's denial seed; nothing drawn at 0 %, `parameters.u1_path_seeds`); gate seeds `parameters.gate_seeds` p14 20261131, p16 20261206 -- the registered campaigns' seeds (common random numbers with the registered rows) |
| declaration | no family file (`prereg_id` null): an exploratory reading under TASK_QUEUE Q-20/Q-45, E-012 (2), E-013 (2), and E-024 (the merge row; the ledger's `declaration.ref`) |
| identity it rests on | (i) the repository's: P-14 and P-16 reproduced path for path (`identity/stage2_identity.py`), and Q-17's adapter reproducing `user_journey.csv` (E-024 (1)). (ii) The runner's own, at full scale in this run (section 3) |
| references | manifest `parameters.references`: my hashes of `a3_brk30_cb20_gate.csv`, `rc_s150_all_gate.csv` and `user_journey.csv` equal all three |
| variant count | manifest `variant_count` 6 (three corrections x two designs; `notes.variant_count_rule`). Nothing in `results/variants.jsonl`: only Q-18 writes that log (section 4, C6) |

## 2. Provenance (task item 1)

- **The manifest verifies:** hash, rows and columns as above.
- **The commit is f7eda0d and clean:** manifest `git_commit` / `git_dirty` false. The ledger line's `who.commit` is
  the same and `who.dirty` is false. The commit is on `master`. The producing code changed after the E-024 merge
  (b7232ba) and before f7eda0d in three commits only, each under its own row and before any reading: 9146330 (Q-48,
  reader routing), 5b2ac27 (Q-58, the reader's authorisation, E-041), f92ac5e (Q-76, a funded-account class
  parameter). `scripts/breakeven_fidelity.py` and `extended/breakeven.py` are unchanged from f7eda0d to HEAD.
- **The log:** 26 `identity HOLDS` lines and no `FAILS`. They match the CSV's 26 `section` = `identity` rows, every
  `value` 1.0. The log ends `written: [...] (3430 rows)` and `EXIT 0`. Its first line is a pandas `DtypeWarning` from
  reading a registered CSV, which is harmless.
- **The ledger line is the declared read:** the last line of `results/read_ledger.jsonl` has `purpose`
  `registered_design`, `declaration.ref` E-024 and designs P-14 and P-16. Its `dates` run `start` 2020-01-02, `end`
  2026-07-16, `judged_first` 2024-01-02, `judged_last` 2026-07-16, blocks choice and judged; `clean_run`
  `breakeven-fidelity`. Its four files (A1 events and days, A3 walks, NQ bars) each carry the sha256 that
  `vendor/DATA_MANIFEST_stage2.sha256` pins. The bars' own `manifest.json` gives `last_day` 2026-07-16 over 1691
  days, and the registered start rows end at 2026-07-16. **Nothing from 2026-07-17 on exists in what was read.** The
  CSV's only date string is the text "2026-11-15" inside the `mdd_P` note.

## 3. Re-derivations and internal consistency (task items 2 and 3)

| headline | as reported (file, rows) | my re-derivation | agrees? |
|---|---|---|---|
| registered gate rows | `gate`, `rules` = `registered`, 15 `GATE_COLS` x 2 shifts x 2 designs | the 0 % `section` = `gate` rows of `a3_brk30_cb20_gate.csv` / `rc_s150_all_gate.csv` (point and lower_bound, `rtp` false) | all 60 exactly |
| `stage2` gate rows reproduce the registered | `gate`, `rules` = `stage2` | the same vendored rows | all 60, within 1e-6 relative (in fact equal) |
| `stage2` scorecard (P, S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c), both arms, both blocks | `scorecard`, `rules` = `stage2` (80 rows) | rebuilt from `user_journey.csv` `section` = `start`, configs p14/p16, by USER_MILESTONES/D-621 definitions (P: the three month-end nets > 0 on starts with 63 sessions; S1: p90 of `spent_before_first_payout` among starts paid by 126; S3c: pooled (net + fees)/fees at month 3; S5a: p10 of `net_month_3`; judged = start year >= 2024) | 80 of 80, and every `n` |
| `stage2` extra rows (shares ahead m1-m3, P, mean nets, CVaR10, P under $2,000/$2,500, shares spent over, n/63) | `extra`, `rules` = `stage2` | the same start rows | all, and every `n` |
| `stage2` path rows (first pass / first payout days p10/p50/p90, share by 126, cash spent before each) | `path`, `rules` = `stage2` | the same start rows | all; 296 rows compared in total in sections `scorecard`, `extra`, `path`, 0 differ |
| the trades section | `trades`, 24 (design, R) groups | per group: the kind shares sum to 1; every share x `trades` is a whole count; `trades` equal across rule sets; `stage2` `changed_kind` = `changed_gross` = 0; `stop_first` moves only targets to breakeven -- the fall in `share_target` x `trades` and the rise in `share_breakeven` x `trades` both equal `changed_kind`, `share_stop` and `share_flatten` unchanged, `mean_net_r` never higher; `delay5`/`both` net moves bounded by `changed_kind` | 24 of 24 |
| internal identities, all four rule sets x 2 arms x 2 blocks x 2 designs | `scorecard`, `extra`, `path` | card P = extra P (value and `n`); P = mean of `share_ahead_month_1..3` on the same `n`; `P_bankroll_2000` <= `P_bankroll_2500` <= P; `share_spent_over_2000` >= `_2500`; `n_nonoverlapping` = n/63; CVaR10 <= S5a; S1 = `path`/`spent_before_first_payout`/p90; S3b = `path`/`first_payout_days`/p90; path percentiles ordered; each measure's eligible `n` equals `stage2`'s; 800 share rows in [0, 1] | 0 problems |
| net = payouts less fees (registered start rows) | `user_journey.csv` start rows | implied payouts (net + fees) never negative; fees and payouts never fall month to month | holds |
| corrected rule sets' scorecard, extra, path, gate, trades values | rows with `rules` in `stop_first`, `delay5`, `both` | **not re-derivable**: the file holds no start, path or trade rows for them | -- (finding D1) |
| analytic oracles (P(pass) <= 2/5, E[gross] <= $2,000 at zero edge) | -- | not applicable: no zero-edge row in the file | -- |

**The headline comparisons (each corrected rule set against the registered row).** `stage2` equals the registered row
by the identities and by my rebuild above. So the comparison is `rules` = X less `rules` = `stage2`, row for row.
Every difference is in `rederive_output.txt` section 6 (scorecard) and section 2 (gate, columns `d_*`). In summary,
counting over the 10 scorecard measures x 2 blocks x 2 designs, each against the registered row (section 6's last
table):

| rule set | verdict arm: better / same / worse | point arm: better / same / worse |
|---|---|---|
| `stop_first` | 8 / 20 / 12 | 2 / 25 / 13 |
| `delay5` | 32 / 4 / 4 | 36 / 4 / 0 |
| `both` | 31 / 4 / 5 | 36 / 4 / 0 |

- **One guard moves beyond D-621's tolerance.** Applying D-621 (3)(ii)'s tolerances as a description: five points on
  a share; otherwise ten per cent, which I take of the registered value's magnitude, since D-621 does not say how to
  apply it to a negative dollar figure. Only one guard crosses: **P-14's S5a (the month-3 net's p10) on the `verdict`
  arm, under `delay5` and under `both`, on both blocks**. On the judged block it changes sign: `scorecard`/S5a,
  `design` p14, `block` judged, `stage2` against `delay5`. Nothing else is beyond tolerance on either arm.
- **P (`scorecard`/P):** under `delay5` and `both`, P rises for both designs on both arms and both blocks. Under
  `stop_first` it moves by at most one start-month on P-14 and P-16 (section 6). P-14's P stays above P-16's under
  every rule set, arm and block. The file holds **no paired interval and no bootstrap**: columns `lo`/`hi` are
  absent, `mdd_P` is blank on every row. So no difference here can be called real or noise (finding C2).
- **The gate:** `pf_growth_on_base_p50` at `lower_bound` is above zero under every rule set. `ruin_probability` is 0 in
  every gate row. The `delay5`/`both` rows lower `pf_required_p90` and `mean_max_drawdown` and raise
  `pf_growth_on_base_p50`, for both designs at both shifts. The `stop_first` gate differences are small in both
  directions. Ruin, drawdown and payout latency (`median_days_to_first_payout`) sit beside growth in the same rows, as
  D-145 asks.

## 4. Findings, most serious first

**D1 (provenance defect): the corrected rule sets' figures cannot be re-derived from the file.** For `stop_first`,
`delay5` and `both`, every row (`scorecard`, `extra`, `path`, `gate`, `trades`) is a summary. The run wrote no
per-start table, though Q-17's own `extended.user_readings.start_table` exists for this purpose. There are no per-path
gate rows and no per-trade rows either. So P and every guard under a correction rests only on the following:

- the runner's refusing checks for each rule set and arm (`identity` rows: payouts and fees against the engine's
  totals, card P = extra P, limits ordered, shares in [0, 1]);
- the walker's synthetic tests (`tests/test_walker_breakeven.py`, 9 tests);
- the `stage2` rule set's full identities, which show that the pipeline reproduces the registered rows. They do not
  show that the corrected walk is right on real bars: no file can show that.

My internal checks (section 3) are consistent with correct summaries, but they cannot reconstruct them. Until a
per-start file exists, a corrected-arm figure in a document should carry the label "the runner's figure, not
re-derived by audit". The remedy is the lead's: for example, a per-start file for each rule set and arm from a new
clean run. I did not and would not rerun anything.

**C1 (scope): P-15 was not re-walked, so this file cannot settle R\*.** D-621 (2) takes R\* as the best P among
p14, p15 and p16 (`u_select.ROWS_TO_BEAT`). P-15 (`rc_s100_all`) is built by the same `atlas_a3.walk_minutes` walk as
P-16 (`vendor/stage2/scripts/rc_width_screen.py`, docstring: its builder "gives P-15's `rc_s100_all` exactly"). So it
carries the same breakeven move and the same two defects. From `user_journey.csv`'s start rows, P-15's registered P
on all starts at the `verdict` arm lies between P-14's and P-16's (`rederive_output.txt` section 4, last lines). How
it moves under the corrections is unknown. The same applies to each guard's row to beat (`row_to_beat.by_measure`).
Q-20 declared P-14 and P-16 only (E-013 (2)), so this is not a deviation. It does limit the statement "R\* rests on
it": the file shows P-14 above P-16 under every correction, and nothing about P-15.

**C2: no statistic of size.** The CSV has no paired difference, interval or level. `mdd_P` is blank, with the note
"TASK_QUEUE Q-16's calibrated P comparison is not on master (2026-11-15)". By f7eda0d that note was stale: Q-16 was
merged under E-035 before E-041 and E-066. Every difference in section 3 is descriptive. The shifts under `delay5` are
consistent in direction across arms, blocks and both designs, which is not a test.

**C3: P-14's S5a crosses the ten-per-cent dollar tolerance under `delay5`/`both`** (section 3), while P and the other
guards improve. Wherever R\* = P-14 is cited "as corrected", this sits beside it. The tolerance's base for a negative or
near-zero dollar reference is my convention; the judged-block registered value is close to zero, which makes any
relative band ill-conditioned there.

**C4: the bound is recomputed per rule set.** The `verdict` arm and the gate's `lower_bound` shift by each rule set's
own bound (`parameters.bounds`: "recomputed from each rule set's trades by the design's own rule"). The gate's
`mean_r_used` difference between `point` and `lower_bound` changes under `delay5`/`both` (section 2). So a corrected
`verdict` row differs from the registered one in its trades **and** in its shift. This is declared, in the code before
the merge (b7232ba) and in the manifest. It is not post hoc, but it must be stated wherever a corrected `verdict`
figure is used.

**C5: a non-monotone response, small and unexplained.** `stop_first` only ever turns a target into a breakeven
(section 3, trades), so its trades are weakly worse at every R. Yet P-14's `verdict` P on all starts and its S5a rise
slightly under it (section 6). The `point` arm shows no such rise in P. The size is about one start-month out of the
3 x `n` start-months. Path dependence through the state-dependent sizing table and the per-rule-set bound (C4) could
explain it. I could not verify that without start rows (D1). It is recorded, not diagnosed further.

**C6: minor provenance.**

- The run log does not itself record the checkout's commit or its clean status. `run_clean.py` prints those to the
  console, not to the log. Cleanliness rests on manifest `git_dirty` and the ledger's `who.dirty`.
- The six variants appear in the manifest only, not in `results/variants.jsonl`.
- At audit time the result, its manifest and the ledger line are staged/modified but not committed (`git status`).

**C7: assumptions the file does not state.** These carry from the registered rows and must be stated wherever the
reading is used:

- the `assumed` fill profile (`vendor/stage2/config/fills.yaml`, `active_profile: assumed`);
- the payout lag and spacing model;
- the no-closure state table;
- 0 % denial, the placement off and no Focused Trader model. Only these three are stated, in `parameters.u1_response`;
- the five-minute latency taken from D-266, for the move made "by hand" (E-013 (2)).

**Nothing chosen after a look (task items 4 and 5).**

- The exploratory label is on every row (`reading`, one distinct value), in manifest `exploratory` true and `notes`
  (`selection`: "none"; "R\* stays P-14 unless the operator rules otherwise").
- No `CARRIED`/`chosen` text or column appears.
- The rule sets, the five-minute delay (D-266), the 500 paths, the registered gate seeds, the every-start replay and
  the per-rule-set bound were fixed in code merged under E-024 and in E-012/E-013, before the run. The later code
  changes are infrastructure under their own rows (section 2).
- `--check` prints no reading (docstring and code). This is the only log of a breakeven-fidelity run under
  `%LOCALAPPDATA%\stage2-extended-runs\`.
- I found **no parameter, window, filter or measure that the declared texts do not contain**.

## 5. Failure protocol

No check failed, so no protocol steps were needed. D1 is a property of what the file holds, not a failed check. C5 is
an unexplained small movement. I did not rerun anything for it and fixed no seeds for a replication (a replication
would need the engine, which is a heavy job and the lead's to schedule).

## 6. What I could not verify, and why

- **Every corrected figure** (D1): the file holds no start, path or trade rows for those rule sets.
- **That the corrected walk implements E-012 (2)'s two corrections correctly on real bars:** that needs the bars and
  the walker. I checked only that the trades section's counts move the way each correction implies (`stop_first`:
  targets to breakeven only).
- **P-15 under the corrections, and R\*'s identity among all three rows to beat** (C1).
- **Whether any difference is more than noise** (C2).
- **The gate floor against P-06's row at a fresh seed:** not part of this reading. The gate here runs at the
  registered seeds.
- **What the console showed at run time beyond the log:** the checkout is removed.

## 7. Verdict

**Defects found: one provenance defect (D1).** The corrected rule sets' figures are summaries that cannot be
re-derived from the file. Everything that can be re-derived agrees exactly:

- the 60 registered gate values;
- the 296 `stage2` scorecard, extra and path rows rebuilt from Stage 2's start rows;
- the trades section's 24 groups;
- the internal identities over all four rule sets.

Provenance is clean: f7eda0d on `master`, clean, `EXIT 0`, all 26 identities held, and the ledger line is E-024's
declared read ending 2026-07-16. The label is exploratory and nothing is carried. Caveats C1-C7 travel with any use
of the reading, above all C1: P-15 was not re-walked, so this file cannot settle R\*.
