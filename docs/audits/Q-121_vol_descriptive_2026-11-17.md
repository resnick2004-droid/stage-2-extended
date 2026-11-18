# Audit Q-121a: `results/q121_vol_descriptive_a1.csv` (2026-11-17)

**Auditor:** independent; the re-derivation read the CSV and its manifest only, with Python's `csv`, `hashlib` and
`math` (scratch script `audit_q121.py`, run with `python -I`). It imported nothing from `extended/` or `vendor/`, ran
no engine and read no bar. The producing code (`extended/vol_descriptive.py`, `scripts/vol_descriptive.py`) was read
only for what each column means. **Verdict: clean with caveats.**

## What was audited

| item | finding |
|---|---|
| file | `results/q121_vol_descriptive_a1.csv` and `.csv.manifest.json`, staged (`A`), uncommitted |
| manifest | `script` `scripts/vol_descriptive.py`; `git_commit` `4b72ef2aaa343c04439a03b4460a4a99ee101924`, `git_dirty` false; `seed` null (nothing is drawn); `exploratory` true; `prereg_id` null; `variant_count` 1; `timestamp` 2026-11-17T19:30:13+00:00; `provenance.clean_run.name` `q121-vol-descriptive`; `parameters` give the span, bands, R grid, sets, trail length, walked kinds, BLS cut, quantile rule, the identity counts and the data manifest |
| specification | brief `docs/briefs/Q-121_2026-11-17.md`; rows E-157 (a1), E-158, E-163, E-166; the note `docs/research/volatility_drift_2026-11-17.md` section 4 (a). No family file: a descriptive under E-157, deciding nothing. E-177 (the lead's working copy) records the run |
| consumer | `prereg/RD-04_volatility_drift.md`. Its LF sha256 I recomputed equals E-168's pin; `tests/test_declarations_fixed.py` passes. Its 4.2 takes L_ref from this file's `session` rows (`date`, `walked`, `trail20_range_pts`). Its 3.2 (m3) requires the imported module to hash to the module at this manifest's `git_commit` |
| identities it rests on | the run's own two refusing identities (the log): **days**, the day kind against A1's `days.parquet` on every described session; **walk**, the entries and breakeven-free first exits against `fv3_rung_walk` at zero tolerance. Both print HELD. The repository's `identity/stage2_identity.py` is not this runner's identity; this runner has its own, as CLAUDE.md requires |

## Headline numbers re-derived

Each "agrees" below is an exact equality, or a relative difference at float precision where I name it. All counts
come from the CSV (column `section` and the named columns) or from the run log.

| headline | as reported | my re-derivation (source) | agrees? |
|---|---|---|---|
| CSV sha256 | manifest `sha256` | `hashlib.sha256` of the file's bytes (CRLF; `results/*.csv -text` in `.gitattributes`, so git does not touch them) | yes |
| rows / columns | manifest `rows`, `columns` | rows counted with `csv.DictReader`; header compared to the manifest's list | yes |
| section row counts | log line `rows: session 1034, range 84, band 2520, band_mark 86400` | counted from `section`. Expected from the definitions: 4 measures x 21 periods = 84; 2 sets x 21 periods x 5 bands x 12 R = 2520; (266 + 22) marks x 5 periods x 5 bands x 12 R = 86400 | yes |
| `trail20_range_pts` (every session row) | column | in date order: `math.fsum` over the 20 most recent **earlier** rows with `walked` True and a finite `range_pts`, divided by 20; blank with fewer than 20 | yes, max relative difference 0 on every defined row; blank/defined pattern identical on every row |
| `trail20_range_pct` | column | the same on `range_pct` | yes, max relative difference at float rounding (below 1e-15) |
| power of that check | -- | the same comparison under two wrong rules: the session itself included, and every day kind eligible. Each mismatches on most defined rows (the script's counts) | the check discriminates |
| `band_ticks_010`, `band_ticks_025` | columns | max(1, floor(f x `trail20_range_pts` / 0.25 + 0.5)); blank where the trailing mean is | yes, every row |
| `range` section: n, median, p10, p90 by block, year and quarter, 4 measures | 84 rows | inverted empirical CDF (the k-th smallest, k = ceil(q n), at least 1) over `session` rows with `walked` True and a finite value, grouped by the `date`'s year and quarter | yes, 84 of 84 exact |
| power of that check | -- | an interpolating median fails to reproduce many of those 84 rows (the script's count) | the check discriminates |
| `range` n consistency | -- | block n = sum of year n = sum of quarter n, for each measure | yes |
| `band` n, p16 set, fixed bands | `band` block rows, column `n` | 2 x (walked sessions x 266 marks minus `b` sessions x the 174 marks before 07:30 CT), from the `session` rows' `walked` and `day_kind` | yes, exact |
| `band` n, p14 set, fixed bands | same | 2 x (walked x 22 slots minus `b` sessions x the 15 slots before 07:30 CT) | yes, exact |
| `band_mark` n summed over marks | -- | equals the `band` row's n for each (period, set, band, R); so does the open count (`open_share` x `n`) | yes, every key |
| walk identity count | log `9473220 walk-brackets` | divisible by the 36 fixed brackets (3 stops x 12 R). Its quotient is at or below the fixed-band walks of both sets in the `band` block rows' `n` | consistent (a bound, not a re-derivation) |

## Checks by the lead's list

**1. No day after 2023-12-29.** Holds. The `session` dates run 2020-01-02 to 2023-12-29, sorted and unique, Monday to
Friday only. No row of any section carries a later `date`, and only `session` rows carry a date. No `period` of
`range`, `band` or `band_mark` names 2024, 2025 or 2026. `band_mark`'s periods are only the block
`2020-01-02..2023-12-29` and the years 2020 to 2023 (no quarters, as E-163 says). This shows what the file holds, not
what the run read. The run's reads are bounded only by the script's `check_span` and `reader.read_bars(start, end)` at
the default end, and choice-block reads write no ledger line.

**2. The schema.** Holds. The four sections `SECTIONS` declares are present. The header has no `side` column and no
column with any forbidden word (my own list, the module's plus `open_px`). The populated columns by section are:
`session` (date, kind, bars, walked, the four range measures, the two band widths); `range` (period, measure, n,
quantiles); `band` and `band_mark` (period, set, [mark, mark_ct], band, band_ticks, rr, n, open_share, quantiles).
There is no target/stop split, no win share, no outcome and no price column. The categorical values are only the
declared bands, sets, measures, period kinds and day kinds. **See caveat C1 on the price level.**

**3. Re-derivation from the session rows.** Holds, exactly (table above). RD-04's L_ref population is the `session`
rows dated 2020-01-02 to 2021-12-31 with `walked` True and a finite `trail20_range_pts`. Its size equals the sum of the
`range` rows' `n` for (`year`, 2020) and (`year`, 2021), measure `trail20_range_pts`. Its inverted-CDF median lies
between those two rows' medians. The population has odd size, so on this file the inverted-CDF median and an
interpolating one coincide. T-2's even-count distinction, which matters on its toys, does not move L_ref here. L_ref
is not a row of this file (no 2020-2021 period), so RD-04 computes it. My computation agrees with the definition
RD-04's 4.2 states.

**4. `band` and `band_mark` consistency.** Holds, on 2520 + 86400 rows:
- `open_share` lies in [0, 1] on every row, never blank. `n` is above zero and even on every row (two walks per entry).
  `open_share` x `n` is a whole number on every row.
- Quantile order is p10 <= median <= p90 wherever all three are finite. A blank lower quantile never sits beside a
  finite higher one. Each blank appears exactly where the inverted-CDF rank ceil(q n) exceeds the walks that exit,
  `n` x (1 - `open_share`), so "blank = falls on an open walk" holds row for row.
- Every quantile is a whole number of minutes in 1 to 1328. On `band_mark`, none exceeds the minutes left after the
  mark and its delay (1328 - mark - delay).
- Periods add up: n over years = block, over quarters = year, for both sets, every band and R. Across marks, the
  `band_mark` n and open counts add up to the `band` row.
- n does not vary with R. The three fixed bands share n. The scaled bands' n differs from the fixed bands' only in
  the block, 2020 and 2020Q1, where the first 20 walked sessions have no trailing range. It is never larger.
- The p16 marks between 07:30 and 14:40 CT have n = 2 x the period's walked sessions. Before 07:30 CT, n <= 2 x
  (walked - `b`).
- Monotone oracles, true walk by walk because a larger R or a wider fixed band moves both levels out: open share and
  every quantile are non-decreasing in R and across 12.5 -> 25 -> 37.5 points. No row violates either.
- `mark_ct` matches the mark on the trading-day clock. The marks are 0, 5, ..., 1325 (266) and the slots 0, 60, ...,
  1260 (22). `band_ticks` is 50/100/150 on the fixed bands and blank on the scaled ones. The R grid is 0.25 to 3.0 by
  0.25.

**5. Provenance.**
- The manifest verifies (sha256 above). `git_commit` resolves to `4b72ef2` (`git rev-parse`), the merge of Q-121b
  (E-166), on `master`. `git_dirty` is false.
- **The module:** the LF sha256 of `extended/vol_descriptive.py` at 4b72ef2 equals that at 6942c51 (Q-121b's branch
  commit), at HEAD and in the working tree. It differs from the module at a83db31 (Q-121's first merge). No commit
  after 4b72ef2 touches `extended/vol_descriptive.py`, `scripts/vol_descriptive.py`, `extended/reader.py` or
  `extended/results.py`. **So RD-04's m3 check (3.2) will find the module it imports equal to the one that made this
  file**, as long as nothing changes before step 2.
- **The log** (`%LOCALAPPDATA%\stage2-extended-runs\q121-vol-descriptive.log`): `identity days: 1034 sessions ... HELD`,
  `identity walk: 9473220 walk-brackets ... HELD`, the section counts, `EXIT 0`, and no `REFUSED` or `FAILED` line.
  The days count equals the `session` row count. The manifest's `parameters.identities` repeats both counts.
- **Order of events:** the manifest's timestamp is after the commit pinning RD-04 (88df481, E-168). This matches
  E-168's statement that the file did not exist at the pin, so RD-04's reference years were fixed before any value of
  this file existed.
- No `run.lock` is held now. E-177 (working copy) records the run under the lock.

**6. Chosen after a look.** Nothing found. Every parameter in the manifest is fixed in code merged before the run
(a0cb1ce/a83db31, then 4b72ef2) and is recorded in E-163 before the file existed. That covers the bands of
50/100/150 ticks (the registered designs' stops), the fractions 0.10 and 0.25 (D-238), the R grid (the union of the
two designs' grids), the 20-session trail, the walked kinds `n`/`b`, the BLS cut, the 15:08 walk end, the two entry
sets with their delays, the inverted-CDF rule and `band_mark` by block and year only. Three readings narrow the
brief's words, and each was accepted in E-163 before the run:
- the trailing mean reads prior **walked** (`n`/`b`) sessions only, where the brief says "prior sessions only";
- the range summaries are over walked sessions only;
- an open walk counts as later than every exit.
The first matters: under the "every kind" rule the trailing column would differ on most rows. RD-04 adopts this
population in its 4.2. No subset, filter or exclusion appears in the file that the code at 4b72ef2 does not state. The
file is labelled `exploratory` true and decides nothing.

## Findings, most serious first

No defect found. Caveats:

- **C1 -- a price level is recoverable from the file, to the tick.** No column holds a price. But on every `session`
  row with a range, 100 x `range_pts` / `range_pct` gives the session's first open. My check found the result an exact
  multiple of 0.25 on every such row, so the file carries each choice-block session's first open of the licensed NQ
  bars implicitly. The brief asked for both columns, so this follows from the specification, not from the code. It
  still matters on two counts: feature-rules section 2 ("never raw price levels"), whose letter is met and whose
  spirit is arguable, and CLAUDE.md's licence rule (bars never committed), since result files are committed and
  pushed to `origin`. RD-04's (a2) file will carry the same for the whole development window. **The lead's call**:
  accept and state it, or have a later file round one of the two columns. Nothing here is a reason to edit this file,
  and none was edited.
- **C2 -- identity coverage is partial, and L_ref's column lies outside it.** The walk identity compares only
  breakeven-free walks at the fixed bands. By the log's count over 36 brackets against the `band` block rows' `n`,
  that is a little over half of the fixed-band walks. The scaled-band walks, the other fixed-band walks and the open
  coding at 15:08 have no identity against Stage 2's files. The days identity covers the day kind only. **`range_pts`
  and `range_pct`, and so `trail20_range_pts` and L_ref, are checked against no Stage 2 file.** They rest on the toy
  tests and on the simplicity of max(high) - min(low) over `atlas_local.day_arrays`. My checks are internal: every
  `range_pts` lies on the 0.25 grid, none is negative or zero, every implied first open lies on the grid, every bar
  count is at most 1330. They cannot catch a wrong session window. RD-04's 8.2 identity reproduces these rows through
  the same module, so it adds no independence.
- **C3 -- thin sessions in the reference years.** Seven walked sessions have fewer than 1300 bars (column `bars`):
  2020-03-09, -12, -13, -16, -17, -18 and 2020-07-01. The fewest is on 2020-03-16. These look like the March 2020
  limit locks, which leave no trades. They are walked as Stage 2 walks them (the days identity held against A1). Their
  ranges are truncated by the halts, and they enter `trail20_range_pts` in 2020 and so L_ref's population. This is a
  reading, not a defect, but RD-04's L_ref should be read with it.
- **C4 -- the data hashes are declared, not measured.** `parameters.data_manifest` is copied from
  `vendor/DATA_MANIFEST_stage2.sha256` (the script's `data_manifest()` says the files are not hashed). The two entries
  match that file's lines. That the run read those bytes rests on the snapshot's verification, not on this manifest.
- **C5 -- the log has no provenance header.** `run_clean.py` prints the "running in ... run id" line to stdout only.
  So the log does not show the commit, the run id or `git status`, and the checkout has been removed. The clean,
  named-commit claim rests on the manifest's `git_commit`, `git_dirty` false and `clean_run.name`. E-177 records the
  rest.
- **C6 -- no `results/variants.jsonl` line.** The manifest says `variant_count` 1. No line names Q-121, because
  `write_result` does not append one. This is consistent with a single descriptive that decides nothing, and noted
  only for the count's record.

No check failed, so the failure protocol was not invoked.

## What could not be verified, and why

- **The session ranges and the first exits against the bars.** My mandate reads one CSV and never the bars. No value
  of `range_pts`, `range_pct` or any first-exit time was recomputed from prices. They are checked only for internal
  consistency (above) and, for part of the fixed-band walks, by the run's own walk identity (C2). A light spot check
  of a few sessions' high-low from `bars.parquet` with plain pandas, not `day_arrays`, would close C2 for L_ref's
  column. That is the lead's to schedule.
- **What the run read**, as opposed to what it wrote: choice-block reads write no ledger line. The file and the
  code path show nothing after 2023-12-29. The run's actual reads are not independently recorded.
- **The clean checkout's `git status`** at the command: the checkout is removed and the log does not carry it (C5).
- **The day kinds:** checked internally only (`walked` is exactly `n`/`b`; the kinds and counts are plausible). The
  equality with A1's table is the run's identity, not mine.
- **The analytic oracles** (zero-edge P(pass) <= 2/5, E[gross funded payouts] <= $2,000) do not apply: the file has
  no trade, gate or journey.
