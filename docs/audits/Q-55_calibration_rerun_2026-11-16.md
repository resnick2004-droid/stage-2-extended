# Audit: Q-55, the clean rerun of Q-16's calibration of the pass line (2026-11-16)

**Verdict: clean with caveats.** The five files are what their manifests say. The checkout's state meets E-062 (3)'s
condition. Every one of the 2,398 cells in Q-16's 22 published tables is reproduced exactly. `cons` and the treated
two-sample `cons` are at or below their level on every real and realistic null, at every k from 11 to 15, on both
readings. Family O's drop rule removes s3 only. Nothing in the files contradicts E-035. The caveats are in section 4.

Every figure below was computed by the auditor's own code (pandas and scipy on the CSVs; nothing imported from
`extended/`, `scripts/` or `vendor/`), or read from a manifest, git or the run's log, and is cited to its file, column
and line. CSV line numbers count the header as line 1. The auditor's scripts are listed in section 7.

## 1. What was audited

| item | value (source) |
|---|---|
| files | `results/calibration_lift.csv`, `calibration_p.csv`, `calibration_two_sample.csv`, `calibration_power.csv`, `bm63c_table.csv`, each with its `.manifest.json` (main tree; staged in the index, the staged blobs equal to the working files) |
| rows | 5,616; 1,856; 7,104; 3,180; 8 (manifest `rows`, recounted) |
| sha256 | all five equal their manifest's `sha256` (hashlib over the bytes); the checkout's copies hash the same |
| script | `scripts/q55_calibration.py` (manifest `script`); the parts by `scripts/q16_calibrate.py` (manifest `parameters.parts.*.script`) |
| commit | `c7e01bd794dbf3120651439112954c1b351703b7-dirty` (manifest `git_commit`, `git_dirty` true); c7e01bd is on `master` |
| seeds | manifest `seed` 20261915; `parameters.seeds`: lift_real 20261915, lift_syn 20261916, p_real 20261917, p_syn 20261918, fixed_b 20261913, boot 20261914, p_fixed_b 20261919, tests 20261910-20261912 |
| replications | `reps` 200,000, `boot_reps` 20,000, `d621_reps` 20,000, `power_reps` 5,000; `argv` empty, so the script's defaults (manifest `parameters`) |
| timestamp | 2026-11-16T17:24:24+00:00 (manifest); the log runs from 13:36:32 to 17:24:24 UTC, `EXIT 0 (13673 s)` (`stage2-extended-runs/q55-calibration.log` lines 1, 994) |
| label | `exploratory` true; `notes.exploratory_because`: the configuration was fixed in Q-16 after exploratory runs |
| declaration | none (`prereg_id` null): this is a calibration of statistics, not a family's result. Its row is E-035, with (4) requiring this rerun. The read is declared under E-035 (`parameters.read`), and the seeds are Q-16's brief's |
| identity it rests on | P-16's pairs: `pairs_identity` "HOLDS: (a) the cutoff's marks, (b) the screen's cell row, (c) TRADES_SHA256" and `trades_sha256` `17bcc29bc0c6...` (every manifest; log lines 46-48). `pairs_sha256` `62e64491...` equals the sha256 of the work folder's `p16_pairs.parquet`. The P part's identities (P-14's judged P equals `u_budget.csv`'s; the paired row re-derived) are in the log only (line 185) |

## 2. The five questions

| # | question | verdict | the rows that decide it |
|---|---|---|---|
| 1 | provenance | **HOLDS** | section 3.1 |
| 2 | reproduction of Q-16 | **HOLDS** for everything Q-16 published; **NOT CHECKED** for rows it did not publish (its raw CSVs are not preserved) | section 3.2 |
| 3 | F-02's and family O's pin condition | **HOLDS**, on both readings, for the one-sample `cons` and for the treated two-sample `cons` (both the placebo-selection form and C1', which the file separates) | section 3.3 |
| 4 | family O's drop rule | each selector picks exactly one row; **s3 drops** (`difference80` empty); s1, s2 and u3 stay | section 3.4 |
| 5 | anything against E-035, or that a pin should not rely on | **no contradiction**; caveats listed | sections 3.5, 4 |

## 3. The checks

### 3.1 Provenance (question 1): HOLDS

- **The checkout's state.** `C:\Users\resni\AppData\Local\stage2-extended-runs\q55-calibration` is at HEAD `c7e01bd794dbf3120651439112954c1b351703b7`.
  - `git status --porcelain --untracked-files=all` lists the ten result files (five CSVs, five manifests) and `results/read_ledger.jsonl`, all untracked. It lists no modified tracked file.
  - The ignored entries are `vendor/stage2/data/atlas/` and `vendor/stage2/data/bars/` (the data junctions) only.
- **The ledger.** c7e01bd tracks nothing under `results/` (`git ls-tree HEAD results/` is empty), so the run created the ledger file rather than appending to one. It holds one line: run id `q55-calibration@20261116T133631.545820Z`, `who.dirty` false, `when` 2026-11-16T13:36:33+00:00, purpose `registered_design`, declaration E-035, span 2020-01-02 to 2026-07-16.
  - The same line, byte for byte, is in the main tree's staged `results/read_ledger.jsonl`.
  - So E-062 (3)'s condition holds: nothing in the checkout but the run's result files and its ledger line.
  - It also explains the `-dirty` stamp. The pairs step recorded the tree clean before its read. Every later part records `dirty` true (manifest `parameters.parts.*.dirty`; log lines 52, 184, 248, 363), the ledger file being the only change by then.
- **The blobs.** `git rev-parse HEAD:extended/lift_bound.py` gives `984f3467a4a05aa790d3ea43e94ac7761f0725b2`, and `HEAD:extended/p_bound.py` gives `f5b29710e243f97a2795e57f6458512fea99199b`. `git hash-object` of the checkout's working files gives the same two.
- **`exploratory=True`.** `scripts/q55_calibration.py` line 179 passes `exploratory=True` with the notes "the statistics' configuration (candidates, nulls, the treated block count, bm63c) was fixed in Q-16 after exploratory runs; this run changes none of it" (lines 174-175). That is what all five manifests carry. The label is right: the configuration was chosen on these same draws (E-052 M2).
- **Windows.** No timestamp from 2026-07-17 or later was read. The reader's span and the pairs' metadata end 2026-07-16 (ledger line; `q55-calibration.work/pairs/p16_pairs.json` `last_date`), and the CSVs hold no dates.
- **The run.** Every step ends `EXIT 0`, and the log has no `REFUSED` or `FAILED` line. The run log sits beside the checkout. The work folder is outside it.

### 3.2 Reproduction of Q-16 (question 2)

**Same seeds, same constructions.**
- The manifests' seeds are the note's section 8 seeds, used the same way.
- `q16_calibrate.py` changes from 3a7a3f5 (Q-16's last run) to c7e01bd only in comments and the `--days` seam (`git diff 3a7a3f5 c7e01bd`). `q16_p16_pairs.py` adds only the reader's authorisation. `lift_bound.py` is the same blob at 3a7a3f5 and c7e01bd.
- Q-16's lift part ran at 568c2a4, whose `lift_bound.py` blob is `e7bc57d7...`, a different one. Its P part and first two-sample form ran on uncommitted trees (the note, section 8).
- The exact match below shows those differences changed no published figure.

**What was compared.** The auditor's code rebuilt every table of `docs/research/calibration_2026-11-15.md` (blob `6247fe2c...`, unchanged since 3837256) from Q-55's five CSVs alone, and compared them cell by cell with the note's text. That is Tables 1, 1b, 2, 3, 4a, 4b, 5, 5b, 6, 7, 8, 8b, 9, 10, 10b, 11 and F8, F8b, F9, F10, F10b, F11.

**Result: 22 tables, 370 data rows, 2,398 cells; 0 differ.**
- At 200,000 replications a rate x 1e4 printed to two decimals resolves single rejections. So the rate cells of Tables 1, 2, 5, 8, 10, F8 and F10 fix exact rejection counts, and Table 3 prints its counts outright. These are reproduced exactly, not only to rounding.

**Not checked.** Q-16's raw CSVs (`cal_lift`, `cal_p`, `cal_sel`, `cal_sel_all`) are not preserved.
- I searched `git log --all` on every branch, the wt-verify worktree, `%LOCALAPPDATA%` and `%TEMP%`; the only hits were pytest temporary files.
- Rows the note does not summarise cannot be compared with Q-16. That covers non-worst nulls at k = 12 to 15, most rows at the extra levels 0.001, 0.005 and 0.025, and power rows outside Tables 4, 6, 9 and 11.

### 3.3 The pin condition (question 3): HOLDS on both readings

**How "at or below its level" is read.**
- (a) **The point reading:** the row's `rate` is no larger than its `level`.
- (b) **The interval reading:** the 95 % Clopper-Pearson interval is not wholly above nominal (`ci_lo` <= `level`), which is E-052's criterion for Q-83.

`level` = 0.05/(k(k+1)) was checked on every row. The `rate`, `ratio`, `ci_lo` and `ci_hi` columns were recomputed with `scipy.stats.beta`: 0 mismatches in 5,520 lift size rows, 96 bootstrap rows, 1,856 P rows and 7,104 two-sample rows.

**Which nulls count** (the note, sections 2.1, 2.2 and 2.4; counted from the `null` column):
- **One-sample lift, real (70):** P-16's judged trades sign-flipped. Seven streams (`offered`, `taken`, `thin200`, `thin500`, `thin1000`, `thin2000`, `thin5000`) x two values (`win1`, `net3`) x five sides (`persist1`, `persist5`, `persist21`, `persist63`, `coin`).
- **One-sample lift, realistic (25):** `iid`, `cluster`, `cluster_ar1`, `regime01`, `volclust` at 200, 500, 1,000, 2,000 and 5,000 trades.
- **One-sample lift, stress (20; not in the condition, reported beside):** `cluster_ar5`, `regime03`, `regime10`, `skew` at the same five trade counts.
- **Two-sample, real only:** every two-sample null is built on P-16's judged offers, and the file has no synthetic or stress two-sample null.
  - Placebo-selection (`form` `placebo-selection`, 55): `offer` x five shares on `win1`; `window`, `session`, `block5`, `block21`, `block63` x five shares x two values.
  - C1' (`form` `two-sample (C1')`, 56): four level-fill counts x two values x seven side models (`shared` 1/21/63, `indep` 1/21/63, `coin`).
- **Data check.** Trades per replication are constant on every real lift stream: `offered` 93,037, `taken` 5,959, `thinN` exactly N (`trades_mean`, minimum equal to maximum per stream). A sign flip keeps the counts, as it should.

**Nulls above nominal, `cons`, at every k** (the 95 % interval wholly above / point above):

| statistic | null set | k = 11 | k = 12 | k = 13 | k = 14 | k = 15 |
|---|---|---|---|---|---|---|
| one-sample `cons` | real (70) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| one-sample `cons` | realistic (25) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| treated two-sample `cons` | placebo-selection (55) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| treated two-sample `cons` | C1' (56) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| beside: one-sample `cons` | stress (20) | 2 / 3 | 2 / 3 | 2 / 3 | 2 / 3 | 2 / 2 |
| beside: first-form (`df_rule` `all`) `cons` | placebo-selection (55) | 20 / 20 | 20 / 21 | 20 / 21 | 20 / 21 | 20 / 21 |

**The worst row at k = 11** (largest `ratio`):

| null set | file, line | null | rejections of reps | `ratio` |
|---|---|---|---|---|
| one-sample real | `calibration_lift.csv` 858 | `real:taken:net3:persist21` | 44 of 200,000 | 0.5808 |
| one-sample realistic | `calibration_lift.csv` 4506 | `syn:regime01:2000` | 26 of 200,000 | 0.3432 |
| treated placebo-selection | `calibration_two_sample.csv` 538 | `select:session:0.02:net3` | 59 of 200,000 | 0.7788 |
| treated C1' | `calibration_two_sample.csv` 2522 | `c1p:500:net3:shared63` | 37 of 200,000 | 0.4884 |

- **F-02 (E-065).** The condition is "`cons`, and the treated two-sample `cons`, at or below its level on every real and realistic null at k = 11" (`prereg/DRAFT_F-02_resting_levels.md` lines 16-17). It **HOLDS** on both readings, and at every k up to 15.
- **Family O (E-077).** The condition is "`cons`, and the treated two-sample `cons`, holding on the selection nulls" (fdf2423's text, lines 25-26). It **HOLDS**: 0 of 55 placebo-selection nulls above nominal on either reading at any k.
- **Q-83 is separate.** E-052's fresh-seed validation is a separate condition for both pins, and this file cannot answer it.

### 3.4 Family O's drop rule (question 4), mechanically

**The selector.** `part` = `two_sample`, `df_rule` = `treated`, `form` = `placebo-selection`, `method` = `cons`, `k` = 15 compared as a number, `value` = `net3`, `share` = 0.25, and the cell's `model`.
- I applied it twice: through pandas, and through Python's `csv` module on the raw text. The raw `k` fields in this file are `11` and `15`, and the `share` fields are `0.02`, `0.05`, `0.1`, `0.25`, `0.5` and empty.

| cell | `model` | rows selected | `calibration_power.csv` line | `null` | `difference80` | the rule's result |
|---|---|---|---|---|---|---|
| s1 | `window` | 1 | 1897 | `select:window:0.25:net3` | not empty | stays |
| s2 | `window` | 1 | 1897 (the same row as s1) | `select:window:0.25:net3` | not empty | stays |
| s3 | `block21` | 1 | 2017 | `select:block21:0.25:net3` | **empty** (and `shift80` empty) | **dropped, counted** |
| u3 | `block5` | 1 | 1977 | `select:block5:0.25:net3` | not empty | stays |

Three cells remain (s1, s2, u3). This matches the drafter's expectation ("expects s3 to be dropped"). Two readings beside, deciding nothing:
- The same `block21` row at k = 11 is not empty. The rule's k = 15 column is what drops s3.
- The k = 15 column is the strict one by construction. On all 110 selection power rows, `cons`'s `difference80` at k = 15 is at least its k = 11 value, counting an empty cell as unreachable (0 violations).

### 3.5 Against E-035 (question 5): no contradiction

Each claim of E-035, checked against the files:

| E-035's claim | the files (95 % interval wholly above nominal at k = 11 unless stated) | agrees? |
|---|---|---|
| every single lift candidate exceeds its level on some null | real nulls: `t21e` 5, `t21w` 14, `t42w` 9, `t63w` 16, `hac21` 22 of 70; every k from 11 to 15 likewise | yes |
| so does the studentised block bootstrap | `cbb21`: 3 of 12 bootstrap nulls, among them `real:offered:win1:persist21` (35 of 20,000; `calibration_lift.csv` line 5546) | yes |
| only `cons` holds on every real and realistic null | 0 of 95 at every k, both readings | yes |
| about a third more lift for the same power | `cons`'s `mdl80` over `t21w`'s, on the 40 real thinned `coin`/`persist1` cells at k = 11 and 15: 1.326 to 1.372 (`calibration_power.csv`, `part` `lift`) | yes |
| (2) the treated two-sample `cons` holds; the first form fails for persistent selections | treated: 0 of 111. First form: placebo-selection 20 of 55. C1' gives identical rejections under both rules (no difference to fail on) | yes |
| (3) `pcons` holds | 0 of 29 P nulls (stress included) on both readings at every k | yes |
| (3) `bm63c` holds on real and realistic nulls | interval reading: 0 of 28 at every k. Point reading: one null above, see 4.1 | yes, on the interval reading |
| (3) D-621's line, `bm63`, the overlapping batches and the flat-top are lax | `d621` 18, `bm63` 5, `bm126` 9, `obm63` 11, `obm126` 7, `ft63` 9 of 24 real nulls | yes |
| the bm63c table | `t8` recomputed with `scipy.stats.t.ppf` (largest difference 4.7e-13); `ratio_to_t8` equals `critical`/`t8`; `critical` falls as the level rises; every `argmax_null` is one of the 28 calibration nulls (24 real, 4 realistic); `calibration_nulls` 28, `reps_each` 200,000 | consistent |

**Structural invariants, checked because they must hold whatever the draws** (all 0 violations):
- `cons`'s rejections are at most the fewest of its three members' on the same replications: 920 lift cells and 888 two-sample cells per rule. The same holds for `pcons` and its members (232 cells).
- Rejections do not fall as the level rises: 690 lift, 12 bootstrap, 232 P and 888 two-sample series.
- `cons`'s `mdl80` is at least every member's (230 cells). `mdl80` at k = 15 is at least its value at k = 11 (690 cells), and `mdl80` is at least `mdl50` (1,380 rows).
- `difference80` = `shift80` x (1 - `selected_share_of_offers`) (326 rows), and it is empty exactly where `shift80` is.
- `cons`'s `difference80` is at least `t21w`'s (110 cells per rule).

## 4. Findings, most serious first

No defect was found. The caveats a pin should carry:

1. **`bm63c` on the point reading (the scorecard's P comparison, beside the pass line).** On one real null its point rate is above nominal: `real:p16p-p14p:centred:flip63` at k = 14, 50 of 200,000, `ratio` 1.05 (`calibration_p.csv` line 1685). Its interval is not wholly above nominal.
   - So `bm63c` holds on E-052's interval criterion but not on the strict point reading at that k.
   - Its validation uses fresh replications of the same 28 nulls that set its critical values, so it checks the draws, not the null class.
   - `bm63c_table.csv` is now a clean-run table, but E-035 (3) still needs it pinned under a decision row before `bm63c` is used. `pcons`, the shipped statistic, holds on both readings.
   - Neither F-02's nor family O's pin condition turns on this.
2. **The stress nulls.** `cons` exceeds nominal on the 10 % regime null at 1,000, 2,000 and 5,000 trades (point reading), with the interval wholly above at 2,000 and 5,000 (`syn:regime10:*`, `calibration_lift.csv`). The worst k = 11 row is `syn:regime10:5000`: 128 of 200,000, `ratio` 1.6896, line 5034.
   - The pass line's level holds only for sides whose persistence is inside the realistic class. That is why E-035 (6) requires each family to state its persistence, and a pin should cite it.
3. **Q-55 cannot test what E-052 M1 and M2 raise.**
   - The file has no count-persistent null (M1). K0 and Q-83's tables beside meet that.
   - Q-55 replays Q-16's own draws (M2), so its agreement with Q-16 is provenance, not validation. Both pins also need Q-83 to HOLD.
4. **The two-sample nulls are all one population's.** Every placebo-selection and C1' null is built on P-16's judged offers, and the selection nulls use the coin side's own outcome, not a stratum-centred value (family O's F1). "Realistic" is an empty set there. This was disclosed program-wide as a pre-read of the judged population's outcomes (family O's text, line 285).
5. **Provenance details (minor; nothing to rerun).**
   - (a) The top-level manifest `seed` reads 20261915 on all five files. The P file's and the bm63c table's draws come from 20261917 and 20261918 (and `p_bound`'s 20261919). The full map is in `parameters.seeds`, so the run can be reproduced, but a reader of `seed` alone gets the wrong one for those two files.
   - (b) The P part's inputs, Stage 2's `vendor/stage2/results/user_journey.csv` (`5c8e7413...`) and `u_budget.csv` (`bd7ad8ce...`), are not named or hashed in any manifest: `parameters.read.files` lists only the pairs step's three files. Their hashes are only in the uncollected `q55-calibration.work/p/calibrate_p.json`. They equal `vendor/MANIFEST_stage2.sha256`'s entries, so the vendor integrity test pins them (the red team's n7).
   - (c) The P part's identity result and the judged calendar's 657 sessions are recorded only in the log (lines 53, 185), not in a manifest.
   - (d) The `-dirty` stamp stands on every manifest. Its acceptance rests on E-062 (3) and on section 3.1's status check. The checkout is the evidence, so the row should record that check before the checkout is removed.
6. **The power figures' resolution.** The placebo-selection power rows use 5,000 replications (`reps` 5000) and a 28-point grid of shifts. An empty `difference80` means 80 % power is not reached by about 40 median standard errors, a weak condition (family O's own reading). The drop rule reads it mechanically, as declared.

## 5. Failed checks and the failure protocol

No check of the result failed. One comparison by the auditor's own tool failed first, and it is kept on record:
- **The failure.** The first pass of the note comparison reported 70 differing cells, all in Tables 4a and 4b.
- **Terminal states.** Every differing row was shifted by exactly one against its neighbour.
- **Stage decomposition.** The fault was in the note's parser, not in either file. Each of those tables has two sub-tables, and the parser kept the second sub-table's header row as data.
- **The component in isolation.** I dropped rows beginning `| trades |` and changed nothing else.
- **Replication.** None was needed: the rerun of the comparison is deterministic and reads the same bytes. It gives 0 differing cells in all 22 tables.

## 6. What could not be verified

- **The rejection counts themselves.** They are simulation outputs, and re-deriving them would mean rerunning the calibration, which is heavy and Q-83's to do. What was verified: the arithmetic on every row, the invariants, and exact agreement with the 2,398 cells Q-16 published from runs at other commits.
- **Q-16's unpublished rows.** Its raw CSVs are not preserved anywhere searched (section 3.2).
- **The run lock.** `run.lock` is transient and keeps no history, so that Q-55 held it is not shown by any file (E-062 (4) records the lead's observation of the running job).
- **The pairs' content.** I hashed `p16_pairs.parquet` but did not open it. Its identity (marks, cell row, `TRADES_SHA256`) rests on the producing script's assertion as logged.
- **The analytic oracles** (zero-edge P(pass) <= 2/5, gross funded payouts <= $2,000) do not apply: the files hold no evaluation or payout.

## 7. The auditor's scripts

Copied into `docs/audits/scripts/q55/` (untracked; the lead commits them with this note):
- `audit_q55.py`: the manifests, arithmetic, structure, invariants, the pin table and family O's drop rule. Run from that folder, it also writes `pin.pkl` beside itself.
- `compare_note.py`: the 22 tables rebuilt and compared.
- `extra_checks.py`: the bm63c table, the bootstrap, the cost of power, the worst rows with their line numbers, the null sets.
- `family_r_drop.py`: section 8.

Their printed outputs sit beside them: `audit_out.txt`, `compare_out.txt`, `extra_out.txt` and `family_r_out.txt`. `compare_out.txt` holds the run after the parser fix in section 5. The scripts read only the five CSVs, their manifests and the note's text, and they import nothing from `extended/`, `scripts/` or `vendor/`.

## 8. Family R's drop rule, applied mechanically (the lead's follow-up)

**The text.** `prereg/DRAFT_F-R_resolution.md` on master; its LF sha256 is `311293be76db3bbc49f944393a7070fd61c30be2f3bfd80c1b45e4e81dc5d09f`, both for the working file and for HEAD's blob. The rule is in section 6.6 and is restated in section 8's parameter row and section 21 item 2. It reads: a cell "whose class row (the slower of two where two are named) does not reach 80 % power inside Table 9's grid at the share 0.5 ... at the family's k column (Table 9 gives k = 11 and k = 15; for k from 12 to 15 the k = 15 column ...; above 15 ... the lead rules) is dropped before the pin and counted".

**What the text fixes, and what it leaves open.**
- **The class:** fixed. Each of the three cells (`adm@1`, `adm@1.5`, `adm@3`) names "block21 to block63", "the slower decides: block63". So all three cells select the same class row.
- **The share:** fixed at 0.5.
- **The statistic and the k column:** `cons` at k = 15, for a family number from 12 to 15. Two edges stay open. At k = 11, Table 9 has both a `t21w` and a `cons` column, though F-02 takes k = 11 first (E-077). Above 15, the lead rules.
- **The value row:** open. The text names no value; Table 9 has `win1` and `net3`.
- **The form:** "Table 9" is the treated (`df_rule` `treated`) placebo-selection table; the first form's table is F9. The rule does not name a df rule, so both are reported.

**Each reading** (`calibration_power.csv`; `part` `two_sample`, `form` `placebo-selection`, `share` 0.5; each selector picks exactly one row):

| df rule | value | class | `cons` k = 15 | `cons` k = 11 | `t21w` k = 11 (not the family's statistic) |
|---|---|---|---|---|---|
| treated | net3 | block63 | line 2065: **empty** | line 2064: empty | line 2062: not empty |
| treated | win1 | block63 | line 2061: **empty** | line 2060: empty | line 2058: not empty |
| all | net3 | block63 | line 2733: **empty** | line 2732: empty | line 2730: not empty |
| all | win1 | block63 | line 2729: **empty** | line 2728: empty | line 2726: not empty |
| beside: treated | net3 | block21 (the faster named class) | line 2025: empty | line 2024: empty | line 2022: not empty |
| beside: treated | win1 | block21 | line 2021: empty | line 2020: empty | line 2018: not empty |

`shift80` is empty exactly where `difference80` is, in every row above. The first form's block21 rows are empty too (lines 2689, 2693 at k = 15; 2688, 2692 at k = 11).

**Outcome.** Every reading with `cons` gives an empty row, so all three cells drop: `adm@1`, `adm@1.5` and `adm@3`, each with the same row under a given reading.
- That holds whichever value row, df rule or k column (11 or 15) is read, and even at the faster class.
- The only non-empty rows are `t21w`'s at k = 11. That statistic is not the family's, and k = 11 is not a k the family can take.
- So the open choices do not change the outcome. Only a k above 15 is left to the lead's ruling, and Table 9 has no column for it.
- With every cell dropped, E-057's adopted ruling for family R applies ("the draft is not pinned, takes no k, and is closed as 'not judgeable on this block'"). E-077 cites it for family O, and the drafter proposes the same (section 6.6, section 21 item 2). That ruling is the lead's to record.
