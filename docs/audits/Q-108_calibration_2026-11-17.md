# Audit: Q-108's calibration -- the one-sample pass line's choice (2026-11-17)

**Auditor:** an independent subagent, on master with E-148 and E-149 staged and not yet committed. The note is not
committed.

**Verdict: clean with caveats.** I re-derived the choice from the four CSVs with my own code, importing nothing from
`extended/`, `scripts/` or `vendor/`. The pinned rule picks `cons_m1.25` (C1) in scope Q, as `results/q108_choice.csv`
records. Every check that the files can support agrees, to rounding. No check failed, so the failure protocol was not
needed. The caveats (section 4) are limits on what files can show, plus one reading on the seed guard that was
accepted before the run. None is a defect.

The scratch scripts are in the session scratchpad, which a cleanup can clear:
- `rederive.py` (floors, P_MC, ratios, power, choice);
- `spread.py` (the per-subset spread rows);
- `seeds.py` (seed roles and index orders);
- `checks2.py` (log against file, orderings, intervals);
- `extra.py`;
- `sncheck.py` (C8's reference, a light plausibility simulation).

---

## 1. What was audited

**The files.** All four are under `results/`. Each CSV's sha256, computed by me with `hashlib` on the raw bytes,
matches its manifest's `sha256`:

| file | rows (manifest `rows`) | sha256 (computed = manifest) | manifest `seed` / `parameters.seeds` |
|---|---|---|---|
| `q108_choice.csv` | 21 | `357e91e8...4ff3e` | null / {} -- "no randomness of its own" (`description`) |
| `q108_sn_table.csv` | 12 | `085959bd...6e911` | 20262115 / {sn_table: 20262115} |
| `q108_cal_size.csv` | 50,420 | `f99ebd7e...f358e` | 20262111 / seven seeds: fixed_mc, subsets, subset_mc, synthetic, beside_cp, beside_flat, exact_sample |
| `q108_cal_power.csv` | 1,280 | `df1c6a16...0c387` | 20262113 / {subsets, subset_mc, synthetic} |

The two hashes that E-149 (staged) names for the choosing row equal the computed hashes of `q108_choice.csv` and
`q108_sn_table.csv`. The files are stored with CRLF line endings (every line), and the hashes are of those raw bytes,
as E-149 says.

**Provenance, the same in all four manifests:**
- `git_commit` `9c624d55e42d60dd0bd9668e50f0bdf29ab64040`, `git_dirty` false, `exploratory` false;
- `provenance.clean_run.marker` `S2X_CLEAN_RUN`, run name `q108-calibrate`;
- `script` `scripts/q108_calibrate.py`;
- timestamps 2026-11-17T09:40:48/49 UTC.

9c624d5 is an ancestor of master (`git merge-base --is-ancestor`). Its commit time, 2026-11-16T15:32:54-10:00, is
before the run's start: `run_id` `q108-calibrate@20261117T050651Z` in the read ledger, and the log's first line at
05:07:09 UTC. So E-127's five readings, committed in 9c624d5, came before the run.

**The declaration.** `docs/calibration/Q-108_one_sample_plan.md`, pinned in E-115 at sha256 `c8e7424b...486d7e`:
- the LF hash of the file at 9c624d5 and of the working copy both equal it;
- `parameters.plan_sha256` equals it;
- `python -m pytest -q tests/test_declarations_fixed.py` passes (3 tests).

`prereg_id` is null in every manifest. That is right for a calibration plan, which is not a family; the plan and its
hash are recorded in `parameters.plan` and `parameters.plan_sha256`.

**The code is the code that was read.**
- `git diff f514ca9 9c624d5` (the build read's tip against the run's commit) does not touch
  `extended/lift_one_sample.py`, `scripts/q108_calibrate.py`, `extended/lift_bound.py`, `extended/count_nulls.py`,
  `scripts/q16_*.py` or `scripts/q82_validation.py`.
- The seven blobs in `parameters.blobs` equal `git rev-parse 9c624d5:<path>` for each file. `lift_bound.py` is the F-03
  pin, `984f3467...`.
- No later commit touches the Q-108 files.

**The identities it rests on.**
- In the manifest, `parameters.pairs_identity` reads "HOLDS: (a) the cutoff's marks, (b) the screen's cell row, (c)
  TRADES_SHA256". `pairs_sha256` `62e64491...` is the prefix that the Q-55 and Q-83 audits record.
- `parameters.calendar_sha256` `d1e4524b...` equals E-094 (2)'s judged-session hash, and `n_sessions` is 657.
- The plan's 6.1 identity (the constructions reproduce Q-16's own rejection counts on Q-16's seeds) is a build test
  that E-126 reports as passing. I did not rerun it, because it is a heavy test.

---

## 2. Headline numbers: as reported and as re-derived

How each figure was re-derived:
- **Floors:** from `q108_cal_size.csv` `count_k13..count_k20` / `denominator`, against my own levels 0.05/(k(k+1)).
- **Failure counts:** my own Clopper-Pearson search (the least x whose two-sided 95 % interval lies wholly above
  nominal at n = 200,000).
- **P_MC:** my own dynamic program on the nested binomials of the plan's 4.2.
- **P and the MDLs:** geometric means of `q108_cal_power.csv` `mdl80` / `mdl50` over the ten `toy = P` rows.

Every "reported" value below is a column of `q108_choice.csv`.

| headline | reported (`q108_choice.csv`) | my re-derivation | agrees? |
|---|---|---|---|
| failure counts, k = 13..20 | manifest `fail_counts` | 71, 63, 56, 50, 45, 41, 38, 35 | yes, exactly |
| nulls in the rule, per candidate and scope | `mc_nulls` + `exact_nulls` | 1,123 MC + 1,170 exact = 2,293; 84 beside (`in_rule` False) | yes |
| C1 (scope Q): floors | `mc_floor_ok`, `exact_floor_ok` True | no MC rate above nominal at any k; no exact size above nominal; no alternating configuration rejects | yes |
| C1 (scope Q): P_MC | `p_mc` 1.0 | 1 to within 1e-13 | yes (max abs diff over all 20 rows 2.5e-14) |
| C1 (scope Q): worst exact ratio | `worst_exact_ratio` 0.197483, `sub:500:11:win1:flip63`, k = 13 | 0.197483, the same null and k | yes |
| C1 (scope Q): worst MC ratio | `mc_worst_ratio` 0.168, `sub:2000:04:win1:flip21`, k = 20 | the same | yes |
| eligibility, all 20 candidate-scope rows | `cond1_floors`, `cond2_p_mc`, `cond3_ratio`, `eligible` | identical, row for row | yes |
| eligible in scope Q, in P order | (from `P`, `eligible`) | C1 0.135672 < C6 0.136867 < C2 0.161204 < C3 0.186824 < C4 0.212579 | yes |
| the choice | `decision` "CHOSEN cons_m1.25 (scope Q)" | C1, scope Q (C0 is excluded from scope Q: `in_scope_set` False) | yes |
| refused by condition 3 alone | `refused_by_cond3_alone` all False | none: every candidate that passes conditions 1 and 2 also passes condition 3, in both scopes | yes |
| P, P relative to C0 | `P`, `P_rel_C0` | max abs diff 1.4e-16, 1.6e-15 | yes |
| MDL50 and MDL80 geomeans at k = 13, 15, 20 | `mdl50_k*_geomean`, `mdl80_k*_geomean` | max abs diff below 1.4e-16 | yes |
| per-exact-model worst ratios (flip42/55/63, alt45/55), with their nulls and k | `worst_ratio_*`, `worst_null_*`, `worst_k_*` | max abs diff 5.7e-14; nulls and k identical | yes |
| the per-subset spread rows (2,880) | `q108_cal_size.csv` `row = spread`: `subsets`, `above_*`, `median_ratio_*`, `p90_ratio_*`, `max_ratio_*`, at 12 levels | recomputed from the per-subset null rows: `above` = number of subsets with ratio > 1; median; p90 (linear); max | yes: 0 mismatches |

**Further consistency checks, all passed:**

*Arithmetic of the size file.*
- `rate_*` = `count_*` / `denominator`, and `ratio_*` = rate / level, at every row and level: 0 mismatches.
- MC `ci_lo_*` and `ci_hi_*` are the two-sided 95 % Clopper-Pearson bounds: 0 mismatches.

*Nesting and denominators.*
- Counts are non-increasing in k on every null row: 0 violations, the plan's 4.2 assertion.
- The exact denominators are L x 2^Bmax: 5,505,024 (42 x 2^17), 450,560 (55 x 2^13), 258,048 (63 x 2^12). The
  alternating models have 90 and 110.
- MC rule nulls have 200,000 replications and beside nulls 100,000.

*Orderings on the shared draws (`count_*`, every null and level).*
- Within each candidate, scope D never exceeds scope Q.
- `cons` >= `cons_m1.25` >= `cons_m1.5` >= `cons_m1.75` >= `cons_m2`; `cons_bm` >= `cons_bm_m1.25`; `cons` >=
  `cons_im`; `cons_sn` <= both `cons` and `sn`.
- 0 violations in either scope.

*Scope D's admission.*
- At flip63, `admitted_share` is 0 on every scope-D row, as the plan's 4.4 arithmetic implies.
- The synthetic nulls have `admitted_share` 1 and equal Q and D counts (the plan's 3.3).

*The log against the file.* All 2,377 per-null log lines ("cons at k=13 Q x D y of N") equal the CSV's `count_k13`
for `cons` in both scopes, and its `denominator`: 0 mismatches, 0 nulls missing.

*Power.*
- In `q108_cal_power.csv`, `reps_used` is 20,000 on every toy row and `infinite_share` is 0 everywhere. That is why
  P in scope D equals P in scope Q for every candidate.
- The P toys are exactly subset j = 0 of each size, `win1`, under the coin and flip1 sides (the plan's 5). The size
  file's `toy` column flags the same ten nulls, plus the ten `net3` toys and `syn:cluster:1000`.

*C8's reference (`q108_sn_table.csv`).*
- `rank` = ceil(a x 2,000,000) at all 12 levels, and every `critical` is positive (E-127 (3)).
- My own light simulation used seed 108170001, fixed before running and outside the program's 2026xxxx space, with
  200,000 draws of 657 iid normals. Every tabled critical value lies inside a rough two-sigma order-statistic band of
  my simulated quantile. This checks the distribution, not their draws. C8 was not chosen.

---

## 3. Run integrity

**Null counts against the plan (3.5).** Read from `q108_cal_size.csv`, one candidate and scope (`cons`, Q), by
`group`, `kind` and `model`:

| part of the rule | count |
|---|---|
| exact: fixed streams + subsets | 20 + 1,150 = 1,170, that is 5 models x 234 |
| MC, fixed streams | 28 |
| MC, subsets | 1,070: 4 persistent MC models x 230, plus 3 non-persistent x 50 |
| MC, synthetic | 25 |
| **total in the rule** | **2,293** |
| beside | 54 count-persistent + 30 `flat` = 84 |

- Persistent models have 23 subsets per size, and flip1, flip5 and coin have 5 (j = 0..4).
- The synthetic five are `iid`, `cluster`, `cluster_ar1`, `regime01` and `volclust`. The Q-16 note
  (`docs/research/calibration_2026-11-15.md` 2.2) classes the others, `skew` included, as stress nulls.
- Manifest `parts.*.nulls` sums to 2,377 = 2,293 + 84.

**Seed roles against the plan's 4.1 blocks.** I checked every null row's `entropy`, `subset_entropy`,
`sample_entropy` and `exact_index` against the plan's index formulas: 0 mismatches.
- **Fixed MC:** [20262111, (stream x 2 + value) x 7 + position among the seven MC models].
- **Subsets:** [20262112, z, j].
- **Subset MC:** [20262113, z, j, value, model_index in 3.1's order].
- **Synthetic:** [20262114, i], with i the null's position in Q-16's `SYNTHETIC` x `SIZES` list (0-14, 20-24,
  35-39).
- **Count-persistent:** [20262116, 0..53], in `CP_ONE`'s order.
- **Flat:** [20262117, L-major then z then value, 0..29].
- **Exact sample:** [20262118, exact_index]. `exact_index` covers 0..1,169 in the plan's data, then value, then
  model order.

Further:
- The leading seeds drawn in the size file are 20262111-14 and 16-18.
- 20262115 appears only in the SN table.
- Neither 20262110 (tests) nor 20262119 (spare) appears in any file.
- Every null's entropy is identical across all 20 candidate-scope rows, so the draws are shared.

**The run log** (`C:\Users\resni\AppData\Local\stage2-extended-runs\q108-calibrate.log`, 2,461 lines):

*Failures and exit.*
- Zero lines contain "FAILED CHECK". No line matches fail, error, warn, traceback, refus, mismatch or stop.
- Every step exits 0, and the run ends `EXIT 0 (16435 s)`.

*The seed guard.*
- Zero lines read "NOT in the hand-check record". Three expressions are printed for a hand check, all from
  `tests/test_features_lookahead.py`, each followed by "hand-checked:" and the record's reach and reason.
- One summary line covers 274 more unbounded expressions, which lie over 1,000,000 seeds from both blocks; see
  caveat C2.

*The reads.*
- The reader's span is 2020-01-02 to 2026-07-16. The judged sessions are 657, 2024-01-02 to 2026-07-16.
- No date from 2026-07-17 on appears.

*The scalar re-decision.* Each part's `mismatches.csv` in the work folder is empty (2 bytes). The manifest reports
6,828,222 re-decisions and 0 mismatched, and `parts.*.scalar_checked` sums to the same total.

**The read ledger's two new lines** (`results/read_ledger.jsonl` lines 13 and 14, staged):
- both are `purpose` `registered_design`, `declaration.ref` E-035, designs [P-16], `who.commit` 9c624d5, `dirty`
  false, `clean_run` `q108-calibrate`, one `run_id`;
- line 13 is the judged calendar: `days.parquet`, column `date`, 2024-01-02 to 2026-07-16;
- line 14 is P-16's pairs through `scripts/q16_p16_pairs.py`: events, days and NQ bars, 2020-01-02 to 2026-07-16;
- they mirror Q-83's lines 4 and 5 in form. That is the plan's 6.1 "reads exactly as Q-83's".

**Choices after an outcome.** I found none.
- The plan was pinned in E-115.
- The build's open places were judged at its read, and E-127's readings were committed in 9c624d5 before the run.
  Those include the choosing row's form, P's tie rule, the re-decision's scope and the guard's `PRINT_REACH` (the
  read's item 22).
- The code is unchanged from the read to the run.
- There is one log and one work folder.
- The choice is printed by the script (`CHOSEN cons_m1.25 (scope Q)` in the log's last lines) and is not made by hand.
- `results/variants.jsonl` has no Q-108 line. That is consistent with a calibration that is not a family read and
  spends no k.

---

## 4. Findings (none a defect), most consequential first

**C1. What the files cannot show.** The audit re-derives the rule from the counts. It cannot re-derive the counts:
- the Monte Carlo rejections;
- the exact enumeration's weighted counts;
- the per-toy MDL percentiles (the per-replication MDLs are not written);
- the scalar re-decision.

Each would need the engine and the bars, which this audit may not run. For these I checked internal consistency
instead: the orderings that shared draws force, nesting, log against file, and the denominators' arithmetic. All
passed.

**C2. The seed guard summarises the far expressions (a reading made before the run, not after it).** The plan's 4.1
says an unbounded loop index is printed with its expression, file, line and reach. The run printed 3 such lines
individually and summarised 274 more in one line (log line 4). The summary gives their count and the nearest one,
`vendor/stage2/scripts/shadow_system_levels.py:164`, at a distance of 20,258,510 seeds.
- The cut-off is the builder's `PRINT_REACH = 1_000_000`, judged "only prints" at the build read (item 22 of
  `docs/reviews/BUILD_Q-108_2026-11-17.md`) before the run.
- E-127 (3)'s condition, as the build read worded it ("no derived-seed line 'NOT in the hand-check record'"), is met.
- It is recorded here so that the validation run's log is read the same way.

**C3. The power ordering between C1 and C6 is close, but the same on every toy.** On every one of the ten P toys, C6
(`cons_bm_m1.25`) has the larger MDL80 at k = 13. The ratio C6/C1 lies between 1.001 and 1.017
(`q108_cal_power.csv`, `mdl80`, `toy = P`, k = 13, scope Q). The geometric means are `P` 0.136867 against 0.135672.
- So the ordering is not an artefact of averaging.
- It is a Monte Carlo quantity (20,000 replications a toy). The plan's rule takes it as read, and there is no tie.

**C4. Condition 3 did not bind, so the cost report is empty.**
- Every candidate that passes conditions 1 and 2 also passes condition 3, so the plan's "most powerful candidate
  refused by condition 3 alone" does not exist.
- The file shows this only as a column of False (`refused_by_cond3_alone`), with no line saying so. The plan's 4.2
  "if there is one" allows that.
- Without condition 3 the choice would be the same.

**C5. The clean checkout no longer exists.** `C:\Users\resni\AppData\Local\stage2-extended-runs\q108-calibrate` was
removed after collection, and the log, by `scripts/run_clean.py`'s design, records no commit or `git status`.
- The commit and the clean state rest on the manifests (`git_commit`, `git_dirty` false, `clean_run` marker) and the
  ledger's `who.commit` and `dirty`. All of them agree.
- I could not re-check the checkout's status myself.

**C6. P_MC treats the calibration rates as the truth.** This is the plan's own disclosure (4.2). P_MC is near 1 for
C1 because its worst MC rate is far below nominal. It says nothing about the subset lottery at validation; that is
condition 3's role. One population (P-16's offers) underlies every subset (the plan's section 8, n2).

---

## 5. In plain terms (for a non-quant)

**What was chosen.** The test that says "this design's trades beat a coin on the same brackets" had been passing
noise too often on some real-data checks (Q-83). The pinned plan tried ten repairs on 2,293 noise-only data sets and
took the most sensitive repair that never passed noise above its allowed rate. The rule chose `cons_m1.25`: the old
test (`cons`) with a stricter bar. Each of its three parts must clear 1.25 times its usual threshold.

**Why it was chosen** (all from `q108_choice.csv` and `q108_cal_size.csv`):
- On the calibration's noise, `cons` passed noise above its allowed rate on 17 of the 2,220 subset data sets at some k
  (3 Monte Carlo, 14 exact). `cons_m1.25` did so on none.
- `cons_m1.25`'s worst exact case reached 0.197 of the allowed rate, under the plan's ceiling of a quarter. Its worst
  Monte Carlo case reached 0.168.
- Of the five repairs that met every condition, it is the most sensitive. The next, `cons_bm_m1.25`, needs a slightly
  larger effect on every toy.

**What it costs.** The stricter bar means a design needs a larger edge before it can pass:
- At k = 13, the effect that `cons_m1.25` detects 80 % of the time is about 23 % larger than `cons`'s (`P_rel_C0`
  1.228392).
- Across every toy and k = 13, 15 and 20, the per-toy ratio is 1.227 to 1.235 at the 80 % point and 1.245 to 1.249
  at the 50 % point (`q108_cal_power.csv`, `mdl80` and `mdl50`, C1 over C0, scope Q).
- For example, the ten-toy geometric-mean 80 % MDL at k = 13 is 0.135672 against `cons`'s 0.110447 (`q108_choice.csv`
  `mdl80_k13_geomean`). Units are `extended/lift_bound.py`'s per-trade pair difference for `win1`.
- `cons` itself is not an option: it fails the floors.

**What the validation must show.** On the separate validation seeds (20262120-29), `cons_m1.25` alone must hold E-052's
criterion at every k from 13 to 20, on every one of the 2,293 fresh noise data sets:
- on each Monte Carlo set, fewer than 71, 63, 56, 50, 45, 41, 38 and 35 rejections out of 200,000 at k = 13 to 20;
- on each exactly computed set, a size at or below the allowed rate, and on the alternating models no configuration
  rejecting at all.

If any one set fails, there is no one-sample line and no second choice (the plan's section 7). Families then keep the
two-sample forms. The new validation subsets are fresh draws, so the margin seen here (worst exact 0.197 of the
allowed rate) is evidence, not a guarantee.

---

## 6. What I could not verify, and why

- **The counts themselves, the exact enumeration, the toys' MDL percentiles and the scalar re-decision.** They need
  the engine and the bars, which this audit may not run (C1).
- **The plan's 6.1 identity test on Q-16's seeds.** It is a heavy test, not rerun; E-126 reports it passing.
- **The guard's scan of every ref.** I read only its log output; the 274 summarised expressions were not inspected
  one by one (C2).
- **The clean checkout's `git status` at run time.** The checkout has been removed (C5).
- **C8's reference draws.** Checked for plausibility only, by an independent simulation; not reproduced.

---

## 7. Proposed decision row (for the lead to number)

`| E-NNN | 2026-11-17 | **The audit of Q-108's calibration (results/q108_choice.csv, q108_cal_size.csv, q108_cal_power.csv, q108_sn_table.csv): clean with caveats.** Re-derived from the CSVs alone, with no producing code imported: the failure counts, every floor, P_MC by an independent dynamic program, every worst exact ratio and its null and k, eligibility on all 20 candidate-scope rows, P and the MDL geomeans, the 2,880 per-subset spread rows -- all agree, and the pinned rule picks cons_m1.25 in scope Q, as recorded (eligible in P order: C1, C6, C2, C3, C4); none was refused by the quarter condition alone; all four sha256s match their manifests (the two in E-149 included); commit 9c624d5 clean, on master, its code unchanged from the build read; 2,293 nulls in the rule and 84 beside; every seed entropy and index order as the plan's 4.1; the log has no FAILED CHECK and no line outside the hand-check record, and its 2,377 per-null lines equal the file; the two ledger lines are the plan's reads, development data only. Caveats: the counts, the exact enumeration, the MDL percentiles and the scalar re-decision cannot be re-derived from files (only checked for internal consistency); the guard summarised 274 far expressions under PRINT_REACH, a reading made at the build read before the run; C1 beats C6 on power on every toy, by 0.1 to 1.7 %; the checkout is removed, so its clean state rests on the manifests and ledger. The cost: cons_m1.25's 80 % MDL is about 23 % above cons's (P_rel_C0 1.228). docs/audits/Q-108_calibration_2026-11-17.md. | The note; the plan (E-115, sha256 c8e7424b...); E-127; E-149; the four result files and their manifests; the run log; results/read_ledger.jsonl lines 13-14. |`
