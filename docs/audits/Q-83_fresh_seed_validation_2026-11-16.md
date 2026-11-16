# Audit: Q-83, the pass line's fresh-seed validation (E-052) (2026-11-16)

**Audit verdict: clean.** The five files are what their manifests say, and my own code re-derives the run's verdicts
from the CSVs:
- `bound` (the one-sample `cons`, C1's lift over the coin twin) **FAILS** E-052's criterion;
- `two_sample_bound` and `placebo_selection_bound` **HOLD**.

**The failure is one null.** It is `real:thin5000:win1:persist63`: P-16's real pairs, thinned to 5,000 trades, win at
1R, sign flipped in 63-session blocks.
- Its 95 % interval lies wholly above nominal at k = 11, 12, 13 and 14, by 1.53 to 1.41 times nominal. At k = 15 its
  point rate is above nominal but its interval is not.
- Under Q-16's draws (Q-55) the same named null sat at or near zero. But the thinned subset is drawn afresh in Q-83, so
  the null's data are new.
- The diagnosis (section 3): this is the subset-to-subset spread of a discrete null that E-052's M2 warned could not
  be seen on Q-16's draws. It is not Monte Carlo noise, and not a changed construction.

Every figure was computed by the auditor's own code (pandas and scipy on the CSVs; nothing imported from `extended/`,
`scripts/` or `vendor/`), or read from a manifest, git or the run's log. Each is cited to its file, column and line
(the header is line 1). The scripts are in `docs/audits/scripts/q83/` (section 8). Nothing was rerun.

## 1. What was audited

| item | value (source) |
|---|---|
| files | `results/q82_validation_one_sample.csv` (3,420 rows), `q82_validation_two_sample.csv` (3,996), `q82_count_persistent.csv` (3,960), `q82_criterion.csv` (43), `q82_judged_sessions.csv` (657), each with its manifest |
| sha256 | all five equal their manifest's `sha256`. The main tree's copies (staged) and the checkout's copies are the same bytes, manifests included |
| script, commit | `scripts/q82_validation.py` at `eba156408684d63181be5a121cdc215a464e1b34` (on `master`). `git_dirty` is false on every manifest |
| blobs (manifest `parameters.blobs`, and `git rev-parse` in the checkout) | `extended/lift_bound.py` `984f3467a4a05aa790d3ea43e94ac7761f0725b2` (the validated blob); `extended/count_nulls.py` `c4ceee8f...`; `scripts/q82_validation.py` `8ba05b1c...`; `scripts/q16_calibrate.py` `677d6a73...`, which differs from Q-55's c7e01bd only in three one-door comment markers (`git diff c7e01bd eba1564`); `scripts/q16_p16_pairs.py` `1bdd21a3...`, one comment marker |
| seeds | E-052's block 20262010-20262019 (`parameters.seed_block`). The map: lift_real 20262011, lift_syn 20262012, selection 20262013, c1p 20262014, count_real_one 20262015, count_real_two 20262016, count_syn 20262017, tests 20262010; spare 20262018-20262019, drawn by nothing (`parameters.seed_map`, `spare_seeds`) |
| replications | 200,000 a null (`reps`, every row) |
| label | `exploratory` false. That is right: the seeds and the criterion were fixed in E-052 before the run (`notes.criterion_fixed`) |
| declaration | E-052 (2)'s criterion (`parameters.criterion`). The reads are under E-035, purpose `registered_design`, design P-16 (`parameters.read`) |
| identity it rests on | P-16's pairs: `pairs_identity` "HOLDS: (a) the cutoff's marks, (b) the screen's cell row, (c) TRADES_SHA256". `pairs_sha256` `62e64491...` is the same pairs file Q-55 used. The scalar re-decision checked 56,030 decisions, 0 mismatched (`parameters.scalar_redecision`; log line 412) |
| run | `stage2-extended-runs/q83-validation.log`: 18:05:05 to 19:46:41 UTC, `EXIT 0 (6104 s)`, no `REFUSED` or `DIFFERS` line |

**The checkout.** `C:\Users\resni\AppData\Local\stage2-extended-runs\q83-validation`:
- `git status` shows the ten result files and `M results/read_ledger.jsonl`, nothing else. The ignored entries are the two data junctions only.
- The ledger grew by two lines, both run id `q83-validation@20261116T180453.867129Z` with `who.dirty` false: the judged calendar (2024-01-02 to 2026-07-16) and P-16's pairs (2020-01-02 to 2026-07-16).
- Both lines are in the main tree's ledger.
- Q-97's fix records them as the run's own writes, so the manifests are clean.

**Windows.** No read reached 2026-07-17.

**The seed block.** Outside Q-82's own files, the block appears only as mentions in `DECISIONS.md`, `TASK_QUEUE.md`, F-02's draft and family B's draft (`git grep` on master; log lines 1-28 print the same mentions).

## 2. The verdicts, re-derived (question 1)

I recomputed every row's `rate`, `ratio`, Clopper-Pearson `ci_lo` and `ci_hi`, and its `above_nominal` flag (`scipy.stats.beta`): 0 mismatches in all 11,376 size rows of the three tables.
- `cons` never rejects more than its fewest member: 855, 999 and 990 null x level cells, 0 violations.
- Rejections never fall as the level rises: 0 violations.

**The criterion's nulls, counted from the files.**
- `bound`: 95 (70 `real`, 25 `realistic synthetic`: `iid`, `cluster`, `cluster_ar1`, `regime01`, `volclust`; no stress null).
- `two_sample_bound`: 56.
- `placebo_selection_bound`: 55.
- Every one has `in_criterion` true and 200,000 replications.

**`cons`, nulls whose 95 % interval lies wholly above nominal / whose point rate is above nominal:**

| statistic | k = 11 | k = 12 | k = 13 | k = 14 | k = 15 | my verdict | `q82_criterion.csv` |
|---|---|---|---|---|---|---|---|
| `bound` (C1, one-sample) | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 | 0 / 1 | **FAILS** | FAILS |
| `two_sample_bound` (C1') | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | **HOLDS** | HOLDS |
| `placebo_selection_bound` | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | **HOLDS** | HOLDS |

- My per-k counts agree with the file's `nulls_above` on all 15 rows.
- The two-sample forms' worst rows are `c1p:200:win1:coin` at k = 11 (21 of 200,000, `ratio` 0.277; `q82_validation_two_sample.csv` line 2225) and `select:session:0.02:net3` at k = 12 (55 of 200,000, `ratio` 0.858; line 606).

## 3. Diagnosing `bound`'s failure (question 2), by the failure protocol

The verdict stays on record. Nothing was rerun.

### 3.1 Terminal states: the failing rows

`q82_validation_one_sample.csv`, `method` `cons`. The null is `real:thin5000:win1:persist63`: `group` real, `stream` thin5000, `value` win1, `side` persist, `L` 63, `trades_mean` 5,000, `entropy` [20262011, 63].

| line | k | rejections of 200,000 | `ratio` (multiple of nominal) | `ci_lo` / nominal | interval wholly above? |
|---|---|---|---|---|---|
| 2297 | 11 | 116 | 1.531 | 1.265 | yes |
| 2298 | 12 | 97 | 1.513 | 1.227 | yes |
| 2299 | 13 | 81 | 1.474 | 1.171 | yes |
| 2300 | 14 | 67 | 1.407 | 1.090 | yes |
| 2301 | 15 | 54 | 1.296 | below 1 | no (point above only) |

No other `bound` null has its interval wholly above nominal, or even its point rate above nominal, at any k.

### 3.2 Stage decomposition: which component

On this null all three members are far above nominal at k = 11 (`ratio`): `t21w` 3.392, `t42w` 4.567, `t63w` 5.927. The intersection brings `cons` down to 1.531 but not below 1. The failure is the members' joint laxity on this one null; it is not a defect of the intersection.

Q-55's `calibration_lift.csv` (Q-16's draws) has the same named null at:
- `t21w` 0.053, `t42w` 0.383, `t63w` 0.343;
- `cons` 0.013 at k = 11 (1 rejection of 200,000), and 0 at k = 12 to 15, its upper 95 % limits at most 0.09 of nominal.

So on Q-16's draws this null sat far below nominal, and on Q-83's it is above.

### 3.3 The component in isolation: what differs between the two runs

The constructions are the same code; the diff above is comment markers only. What differs is what each construction draws afresh. I split the 95 nulls by that and compared each null's `cons` rejections at k = 11 between the runs. The test conditions on the total: with equal reps, Q-83's count given the sum is Binomial(sum, 1/2) under equal rates.

| kind of null | what is new in Q-83 | nulls | `cons` rejections at k = 11, Q-83 / Q-55 (summed) | nulls whose rates differ (p < 0.01) |
|---|---|---|---|---|
| real, `offered` and `taken` | the sign flips only (same trades) | 20 | 242 / 254 | 0 |
| realistic synthetic | the draws of the same process | 25 | 316 / 277 | 0 |
| real, `thinN` | the thinned subset of trades (`default_rng([20262011, 999])` against Q-16's `[20261915, 999]`) and the flips | 50 | 698 / 369 | 8 |

**Where the data are the same, Q-83 reproduces Q-55's rates.** That covers the flips on the same trades and the synthetic processes. So the failure is not Monte Carlo noise, and not a changed construction.

**Every rate that changed is on a thinned stream, where the trades themselves are a new subset.** Eight `thinN` nulls differ, seven up and one down:
- `thin200:win1:persist21`: 28 against 6
- `thin200:win1:persist63`: 56 against 2
- `thin200:net3:persist63`: 10 against 0
- `thin2000:net3:persist5`: 14 against 2
- `thin2000:net3:persist21`: 1 against 11
- `thin5000:win1:persist5`: 19 against 4
- `thin5000:win1:persist21`: 46 against 8
- `thin5000:win1:persist63`: 116 against 1

Most are long-persistence nulls (persist21 or persist63).

**The L = 63 flip null is discrete at the family's level.**
- Q-16's flip construction draws 12 signs a replication for 657 sessions at L = 63, and the sessions touch 11 or 12 flip blocks depending on the phase.
- So one sign pattern carries probability 2^-11 (4.883e-04) or 2^-12 (2.441e-04). That is the same order as the family levels, 3.788e-04 at k = 11 down to 2.083e-04 at k = 15.
- At these levels the tail is decided by the one or two most extreme sign patterns: whether all three members reject when the flips line up with that subset's block sums.
- The failing null's `cons` rate is 1.19 times 2^-11.

**The runs' persist63 rows show this lumpiness** (rejections at k = 11, Q-83 against Q-55; nominal is 75.76 of 200,000):
- On the same trades they agree, for example `offered:win1` `t21w` 242 against 283 and `taken:net3` `t63w` 84 against 68.
- On fresh subsets they swing, for example `thin1000:win1` `t42w` 286 against 0, and `thin2000:win1` `t63w` 10 against 100.

Q-16's note had already called this null "a conditional, discrete null" on which "some statistics reject less often than nominal" (`docs/research/calibration_2026-11-15.md` section 7.4 item 5). The fresh subset shows it can also reject more often.

**Is this M2's effect?** Yes, through the subsets rather than the flips. `cons` was chosen on Q-16's one realisation of each thinned subset, and on that realisation this null sat at 0.013 of nominal. Drawn again, the same construction gives 1.53 times nominal. E-052's M2 said Q-55 could not see this kind of thing.

**One construction or broad?** One construction. The only failure is a long-persistence sign flip on a thinned real stream. The offered and taken streams and all 25 realistic synthetic nulls hold, and the synthetic regime process is not involved.

### 3.4 The count against what `cons`'s measured conservatism implies

**The count.** 95 nulls x 5 k = 475 null-by-k cells were tested. 4 have their interval wholly above nominal, all on the one null. The four are nested (the same replications read at successively smaller levels), so they are one event, not four.

**At a true rate of exactly nominal**, the chance that the Clopper-Pearson interval lies wholly above nominal at 200,000 replications is a little under 2.5 %, because the interval is conservative. It takes at least 94, 81, 71, 63 and 56 rejections at k = 11 to 15, which happens with probability 0.0236, 0.0233, 0.0211, 0.0188 and 0.0195. Summed over the 475 cells, about 10.1 would be expected.

**At `cons`'s measured rates in Q-55** (its rejections per null and k), the expected number is 0.000. Even taking Q-55's upper 95 % limits as the true rates, it is 0.004.

So the observed count is below what an exactly calibrated statistic would show, but well above what `cons`'s measured conservatism predicted.

**Across the 95 nulls at k = 11**, `cons`'s mean `ratio` is 0.175 in Q-83 against 0.125 in Q-55. The members' are 1.203, 1.128 and 1.114 against 1.023, 0.963 and 1.003. `cons` is still conservative on average. It fails on one realised null, where its lower 95 % limit is 1.265 times nominal.

### 3.5 Replication with seeds fixed beforehand

Not done, and not mine to do: it would be heavy. A light way to tell whether this null is an outlier of its class would be more fresh thinned subsets of the `thin5000:win1:persist63` construction, each at 200,000 flips. That needs new seeds fixed under a row first (E-052's spares 20262018-20262019 are reserved, drawn by nothing). It is the lead's to schedule, and it cannot change Q-83's verdict, which was fixed before the run.

### 3.6 Beside, never the criterion: the count-persistent nulls (`q82_count_persistent.csv`)

`cons` with the interval wholly above nominal, cells across k = 11..15:
- `bound`: 60 cells on 12 of 54 real count-persistent nulls (largest `ratio` 2.760, `cp:ar98s15:2000:net3:persist1`, k = 15), and 13 cells on 3 of 16 synthetic ones.
- `placebo_selection_bound`: 55 cells on 12 of 16 real ones (largest `ratio` 6.024, `cp_select:ar98s15:0.25:win1`, k = 15).
- `two_sample_bound`: 0 of 16 real and 0 of 8 synthetic.

K0 addresses these (E-052 (1)). They matter to family O, whose C1 is `placebo_selection_bound`, but they are not part of the verdict.

## 4. The judged session list (question 3)

From `q82_judged_sessions.csv` (columns `ordinal`, `date`):
- **657 sessions**, from **2024-01-02** (line 2) to **2026-07-16** (line 658), sorted and unique, ordinals 0 to 656.
- The sha256 of the ISO dates joined by a single LF with no trailing newline, computed by me from the `date` column, is **`d1e4524b15dc6a69c2f66865462a5fe30527c6a56b4c7cc7aaccc1436a30f3bd`**.
- That equals the manifest's `parameters.sha256_dates_joined_lf` and `calendar_sha256`, with `count` 657 and the joining rule in `parameters.joined`. It is also what the log prints (line 30).

## 5. Family O's text and `bound` (question 4)

The text is `prereg/DRAFT_F-O_opening_timing.md`. Its LF sha256, `4765db0a40a679a6727799f271ff6f9297a9ff8bdde53d7b2d6291ec9a3129f2`, is the same at fdf2423, at HEAD and in the working file.

**No deciding line of family O uses `bound` (the one-sample `cons`).** Every `cons` call it names is a two-sample form:

| line or check | function | where (line numbers) |
|---|---|---|
| C1, C1-close (the pass line) | `placebo_selection_bound` | 65, 137, 751, 851, 1149-1150 |
| C2 (the value line) | `two_sample_bound` | 65, 799-800, 851, 1154 |
| K0 (kills a cell or withholds a pass) | C1's form by `placebo_selection_bound`'s nested statistic, C2's by `two_sample_bound`'s | 1009-1010, 1145-1148 |
| A10 (a control) | `placebo_selection_bound` | 985 |
| the confirmation's C1 and C1-close | `cons`, as C1 | 1309 |
| C3 | point estimates of the two halves, no statistic | 776, 1167 |
| the seeded draw | `two_sample_bound`, "never in a line" | 769-770 |
| A4 | a circular block bootstrap, not `lift_bound` | 949 |

- **The coin twin.** The text says E-008's lift over the coin twin is "zero by construction" for this family (line 20), so it has no coin-twin line.
- **The fixed parameter row (line 851)** reads: "`placebo_selection_bound` on y for C1 and C1-close, `two_sample_bound` for C2".
- **But the pin condition is worded as a whole.** Family O's condition 2 reads "Q-83's fresh-seed validation HOLDS on E-052 (2)'s criterion" (line 28), and its withdrawal clause applies "if Q-83 does not hold by E-052 (2)'s criterion" (lines 33-35).
- E-052 (2) states one criterion over "`cons` and the treated two-sample `cons`". Q-82's script, as built and merged under E-062 (1), prints it per statistic.
- **Read as a whole**, Q-83 does not hold, because `bound` fails, and family O's clause would withdraw the text. **Read per statistic** for the functions the family uses, both HOLD.
- **That reading is the lead's to rule**, not the audit's.
- **F-02 is not in doubt either way.** Its C1 is `extended.lift_bound.bound(SHIPPED, ...)` (`prereg/DRAFT_F-02_resting_levels.md` line 746), so its condition 2 fails on either reading. Its text says it is then "withdrawn before any read" (lines 22-23).

## 6. Findings, most serious first

1. **`bound` FAILS E-052's criterion**, on one real null at k = 11 to 14 (section 3.1). The result is sound: the verdict re-derives exactly. The finding is the result's, not a defect of the file.
2. **The failure is the subset-to-subset spread of a discrete null** (section 3.3). On data held fixed, Q-83 reproduces Q-16's rates. Every change is on a thinned stream, whose subset was drawn afresh. At L = 63 the family-level tail is one or two sign patterns, so the size there depends on which trades were drawn.
   - So `cons`'s level for a one-sample lift on a few thousand trades with a side persisting for a quarter is not established by these files. Q-16's single subset made it look far below nominal.
3. **E-052 (2)'s criterion is worded jointly, but the script reports it per statistic.** Family O's and F-02's pins turn on that reading (section 5).
4. **Beside:** `placebo_selection_bound`, family O's C1, is lax on 12 of 16 real count-persistent nulls (section 3.6). This is K0's to handle, as declared.
5. **An operational finding: committing these results will fail the fast tier.** `tests/test_q82_validation.py::test_the_seed_block_is_unused_in_this_repository` (line 201, not marked slow) asserts that E-052's block appears nowhere outside Q-82's own files. It fails in the main tree now: I ran only that test (`pytest -k seed_block_is_unused`).
   - The offending paths are Q-83's result files themselves: `results/q82_*.csv` and their manifests, which record their seeds as they must.
   - The audit's own files are not among them. The note is a document, a mention by the script's own rule, and the scripts' outputs name no seed of the block.
   - The test guarded the block before the run, and the block is now spent. Not fixed here: a change to the test or its allow-list is a code change under its own row.

## 7. What could not be verified

- **The rejection counts themselves.** They are simulation outputs, and re-deriving them would mean rerunning the validation, which is heavy. Verified instead: the arithmetic, the invariants, the agreement with Q-55 where the data are the same, and the criterion's logic.
- **Q-82's claim** that on Q-16's own seeds the script reproduces Q-16's counts exactly (E-062 (1), a test on synthetic pairs). I did not run it. The statistical agreement on the 45 fixed-data nulls is independent support.
- **Whether `thin5000:win1:persist63` is typical of its class** (section 3.5).
- **That the run held `run.lock`.** The lock keeps no history.

## 8. The auditor's scripts

In `docs/audits/scripts/q83/` (untracked):
- `q83_audit.py`: manifests, arithmetic, the verdicts, the failing rows, the Q-55 comparison, the expected counts, the beside tables and the judged list.
- `q83_extra.py`: invariants, null sets, the persist63 rows across both runs and the L = 63 arithmetic.

Their outputs are `q83_audit_out.txt` and `q83_extra_out.txt`. They read only the five Q-83 CSVs, their manifests and Q-55's `calibration_lift.csv`.

`q83_audit.py` reports whether each manifest's seeds lie in E-052's block without printing them, so that no file here trips the seed test of section 6 item 5. That change was made after a first run whose output printed them; the figures are unchanged.
