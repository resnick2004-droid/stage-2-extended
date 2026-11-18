# Q-130: licence-compliance scan of the committed result files (2026-11-17)

Asked by the lead under E-179. A read-only scan by wt-scout; nothing was committed, no file was changed except this
note, and **no price value appears below** -- only file names, column names and judgements. No outcome of the
development data was computed or read for its value.

## The question

Does any file tracked by git -- under `results/`, any CSV elsewhere outside `vendor/`, or the vendored Stage 2 result
files under `vendor/stage2/results/` -- hold NQ price levels, or let one reconstruct them (a level column, a ratio pair
that reveals a level, timestamps with prices, anything that reproduces the licensed bars)? And was such a file ever
committed and later removed?

## The answer

**No tracked file holds or reveals a price level.** All 21 tracked data files under `results/` (19 CSVs and 2 JSONL
ledgers, with 19 sidecar manifests) hold statistics of statistics: significance levels, rejection counts and rates,
minimum detectable lifts, supply counts, dollars and dates. The three tracked CSVs elsewhere outside `vendor/` are
calendars (dates and clock times). The 39 vendored Stage 2 result CSVs, their 39 manifests and 2 policy JSONs hold dollars, shares,
counts, R multiples, stop distances in ticks or points, and dates; none holds a price level. Git history (every
branch) shows no result file ever deleted, every tracked result CSV has exactly one revision (its header never
changed), and the one known offender, `results/q121_vol_descriptive_a1.csv`, has never been committed and is now
git-ignored (`.gitignore:36-38`). Two files are **borderline in the weak sense** that they describe the licensed
product or record per-day bracket outcomes without any price: `config/calendar_early_closes.csv` and
`vendor/stage2/results/a3_brk30_stop_distribution.csv`. **There is no automated guard** that would stop the next
`q121`-type file from being committed; that is the finding that should change the queue.

## Method (what was read, how it was judged)

1. `git ls-files results/`; `git ls-files | grep -iE '\.(csv|tsv|json|jsonl|parquet)$'` outside `vendor/`; `git
   ls-files vendor/stage2/results/` (80 files: 39 CSVs, 39 manifests, 2 policy JSONs). Every other vendored CSV (the
   release calendars under `vendor/stage2/config/` and `vendor/stage2/data/`, the propsim and propfirms result CSVs
   under `vendor/stage2/vendor/`) had its header read as well.
2. For each CSV: the header and a few rows; then a scanner (kept in the session scratchpad, not in the repository)
   that, for every numeric column, measured the share of values lying in a plausible NQ level band (5,000 to 30,000)
   **and** on the 0.25 tick grid, and, for every ordered pair of numeric columns (a, b), the share of rows where a/b or
   100 a/b lands in that band on the tick grid -- the test that catches a points/percent pair. It prints only names
   and shares, never a value.
3. **Positive control.** On the known offender `results/q121_vol_descriptive_a1.csv` (uncommitted, read only for
   this check) the scanner flags the pair `100 * range_pts / range_pct` as in-band and on-tick for every row it
   could form, and also `100 * band_ticks_010 / walked` and `100 * range_pts / walked` -- i.e. that file leaks the
   level through more than one pair, not only the one the auditor named. The detector works.
4. **False positives were judged by meaning, not by the number.** The pair test fires on many pairs of integer
   counts and dollar figures (for example `ratio_k16 / rate_k16` in `q108_cal_size.csv`, which is 1 / level by
   construction; `fees_month_10 / first_pass` in `user_journey.csv`; `stop_ticks / rr` in `a3_resolution_map.csv`).
   None of those columns is a price, a price distance with its percentage, or a level offset, so none can reveal a
   level. Every in-band single column was likewise a count or a dollar figure by its name and its manifest (listed
   below).
5. Manifests and ledgers: every key of every `results/*.manifest.json`, `results/read_ledger.jsonl` and
   `results/variants.jsonl` was listed. They hold paths, sha256 digests, seeds, argv, timings, dates and
   descriptions. A sha256 of `bars.parquet` (in `read_ledger.jsonl`) is a one-way digest, not a derivative. The
   2,791 keys of the 39 vendored manifests were searched for open/high/low/close/price/vwap/settle: two hits, both
   in `s3_event_kinds.csv.manifest.json` -- `rth_open_slot` (a clock-slot index) and `gap_close` (a text definition
   of which bar's close a gap is measured from); neither holds a price.
6. History: `git log --all --diff-filter=A --name-only -- results/` (all 40 paths still tracked);
   `git log --all --diff-filter=D -- results/` (empty); per-file revisions and header digests across all commits
   (one revision each for every CSV; `read_ledger.jsonl` has 11 revisions of an append-only ledger);
   `git log --all -- 'results/q121*'` (empty); every file ever added on any branch with a data extension
   (`.parquet .feather .npz .npy .h5 .pkl .arrow`: none ever) and every CSV ever added outside `vendor/` (the same
   24 paths tracked today).
7. Beyond the brief, a sweep of tracked text outside `vendor/` (`.txt .md .py .json .jsonl`) for decimal numbers in the
   level band beside the words open/high/low/close/price/level. Hits: `docs/audits/scripts/q83/q83_audit_out.txt`
   (the stream name `thin5000`, not a price) and `tests/test_walker.py`, `tests/test_walker_breakeven.py` (hand-built
   synthetic bars, `tests/test_walker.py:1`, `tests/test_walker_breakeven.py:1`). One of the six tracked PNGs
   (`docs/report/demo_stage2_u1/fan_p14_verdict.png`) was opened: net cash in US dollars against sessions; the other
   five are named for payouts, break-even and trade-off readings and were not opened.

## Ranked list

### 1. Files that hold or reveal price levels

**None tracked, now or in history.** The only file found that does is the uncommitted, git-ignored
`results/q121_vol_descriptive_a1.csv` (pairs `range_pts`/`range_pct`, and also `band_ticks_010`, `band_ticks_025`,
`range_pts`, `trail20_range_pts` against `walked`, recover a session's first open). Its sidecar
`results/q121_vol_descriptive_a1.csv.manifest.json` is ignored with it.

### 2. Borderline (no price; listed so the lead can decide)

| File | Columns that matter | Judgement |
|---|---|---|
| `config/calendar_early_closes.csv` (this repository) | `date`, `kind`, `close_ct`, `source` | No price. The `source` text of 6 `data_defect_candidate` rows and of the holiday rows quotes the bar store's own coverage (first/last bar clock time, number of bars on a short day, the vendor's stated degradation). That is metadata about the licensed product, not market data, and reproduces no bar; flagged only because it quotes the data manifest. |
| `vendor/stage2/results/a3_brk30_stop_distribution.csv` (vendored) | `market`, `stop_ticks` (2 values), `state`, `rr`, `exit` (stop/target/flatten), `date` | No price. A per-trade, per-date record of how the bars resolved a fixed bracket: a bar-derived signal at daily granularity, but it cannot recover a level, a range or a path. Stage 2's own choice under E-002; noted, not judged. |

### 3. Clean

This repository (`results/`), with each column class:

| File | What it holds (column classes) |
|---|---|
| `bm63c_table.csv` | `level` (significance level), `k`, `critical`, `t8`, `ratio_to_t8` (statistics), `argmax_null`, `calibration_nulls`, `reps_each` (counts). |
| `calibration_lift.csv`, `calibration_p.csv`, `calibration_two_sample.csv` | `level` (significance), `reps`, `rejections`, `trades`, `trades_mean`, `level_fills`, `placebo_fills` (counts), `rate`, `ci_lo`, `ci_hi`, `ratio` (rates), `L`, `share` (parameters). In-band hits on `trades`, `trades_mean`, `reps`, `rejections`, `placebo_fills` are counts. |
| `calibration_power.csv` | as above plus `mdl50`, `mdl80`, `mdd50`, `mdd80`, `shift80`, `difference80` (minimum detectable lifts, R or share units). |
| `p14_validation.csv` (199 columns) | dollars (`pf_required_*`, `mean_max_drawdown`, `v1_net_*` -- in-band hits are dollars, never on the tick grid), shares, sessions/days, R (`mean_r_used`, `shift_r`, `*_fresh_*_r`), autocorrelations and test statistics (`acf_*`, `ljung_box_*`, `runs_*`), slippage in ticks (`*_slip_ticks`, `added_ticks_*`), counts (`exceed`, `replicates`, `trades_left`, `sessions_missed`), significance `level`. |
| `q108_cal_power.csv`, `q108_val_power.csv` | `size`, `reps_used` (counts), `mdl50`, `mdl80` (detectable lifts), `P`, `P_rel_C0` (shares). |
| `q108_cal_size.csv`, `q108_val_size.csv` (133 columns) | `count_*`, `rate_*`, `ci_*`, `ratio_*`, `above_*`, `median_ratio_*` etc. per k or alpha (counts and rates); `size`, `trades_mean`, `nontie_sessions_mean` (counts); entropy/seed fields. |
| `q108_choice.csv`, `q108_val_criterion.csv`, `q108_sn_table.csv`, `q82_criterion.csv` | candidate names, worst ratios, counts, significance levels, critical values, verdict text. |
| `q35_openings.csv` | `openings`, `distinct_trades`, `block_openings`, `block_distinct` (counts), `share`; `group` is a clock minute, an hour, a weekday, a stop distance ("25 points", a distance) or an entry delay -- counts by time, no price. Its manifest notes `entry_t` (a bar index) but the file holds no per-trade row. |
| `q82_count_persistent.csv`, `q82_validation_one_sample.csv`, `q82_validation_two_sample.csv` | seeds, entropy, `trades_mean`, `top_share_*`, `scalar_checked` (counts), rejection counts, rates, significance `level`. |
| `q82_judged_sessions.csv` | `ordinal`, `date`: the judged block's session dates, no price. |
| `read_ledger.jsonl`, `variants.jsonl`, all 19 `*.manifest.json` | provenance: paths, sha256 digests, argv, seeds, timings, dates, descriptions. |

Elsewhere outside `vendor/`: `config/calendar_fomc_minutes.csv` and `docs/research/fomc_minutes_dates_2026-11-16.csv`
(release dates, clock times, source URLs); `docs/research/firms_2026-11-15/firms/*.json` (firm rules).

Vendored Stage 2 (`vendor/stage2/results/`), noted rather than judged:

| Files | What they hold |
|---|---|
| `a3_brk30_gate.csv`, `a3_brk30_cb20_gate.csv`, `rc_s100_all_gate.csv`, `rc_s150_all_gate.csv` | per-configuration summaries: dollars (`*_final_cash`, `*_max_drawdown`, `pf_required_*`, `pf_net_*`), shares, ratios, counts (`n` -- in-band hits are counts; `pf_required_worst`, `st_max_drawdown_p95` -- dollars). |
| `a3_brk30_cb20_gate_paths.csv`, `rc_s150_all_gate_paths.csv` | per simulated path: dollars (`fees`, `final_cash`, `payouts`, `net`, `max_drawdown`, `deepest_loss_from_start`), counts, days, ratios. No date, no price. |
| `a3_resolution_map.csv`, `rc_reentry_screen.csv`, `rc_width_screen.csv` | `stop_ticks`, `stop_points`, `target_ticks` (distances), `rr`, counts (`offered`, `walks`, `candidates`), shares, clock slots/marks (`slot_ct`, `first_mark`, `last_mark`), micros and dollars of risk. |
| `s1_sided_coin.csv`, `s3_event_kinds.csv`, `s3_latency.csv` | counts (`offers`, `ties`, `gap_sessions`, `gap_no_previous_close` -- counts of sessions, not the gap), test statistics, R means, dollars, shares, `cell_trades_sha256` (a digest). |
| `scoreboard.csv`, `setups_per_day.csv`, `state_policy_v12_noclose.csv`, `stop_band.csv`, `v1_validation_*.csv` | verdict summaries in dollars, shares and days; synthetic setup grids; DP policy summaries; stop bands in ticks with contract `tick_size`/`tick_value` (contract specifications, not prices); validation statistics. |
| `u_budget.csv`, `u_consistency.csv`, `u_entry.csv`, `u_firms.csv`, `u_hours.csv`, `u_limit.csv`, `u_plan.csv`, `u_resolve.csv`, `u_seats.csv` | long form `measure`/`value`/`unit`; every `unit` is one of share, dollars, sessions, ratio, spells, seats, marks, trades, R, leaves, flag(s), bands. "Opened"/"opening" here is a firm or account opening. |
| `u_size_fit.csv`, `u_value_map.csv`, `u_xfa_day_budget.csv`, `user_drivers.csv` | long form; units dollars, dollars/slot-day, micros, probability, share, sessions, count, R, percentage points (a probability difference), correlation, seed. "Opening" is an account's opening trade or day. |
| `user_journey.csv` | per start day: `start_date`, dollars (`net_month_*`, `fees_month_*`, `first_payout_cash`, `spent_*` -- in-band hits are dollars of fees), sessions to events, counts. No price. |
| `state_policy_v12_policies.json`, `state_policy_v12_noclose_policies.json` | dynamic-programming policies over account-balance states (`id`, `version`, `description`, `root`); no bar data. |

The other vendored CSVs (`vendor/stage2/config/*release_calendar.csv`, `vendor/stage2/config/sources/*.csv`,
`vendor/stage2/data/release*_*.csv`, `vendor/stage2/vendor/propsim/**/*.csv`,
`vendor/stage2/vendor/propfirms/results/*.csv`) are release calendars or synthetic-model results (headers:
dates, times, release codes; edge, risk, p_pass, cash, se). Clean.

## What is unknown, and how it could be found

- **Worktrees and clean-run checkouts** under `%LOCALAPPDATA%` were not scanned; an uncommitted result there cannot
  leak through git unless merged, and the guard below would stop it at merge or commit.
- The five unopened PNGs under `docs/report/demo_stage2_u1/` are judged by name only; opening them settles it.
- Whether the licence treats per-day bracket outcomes (`a3_brk30_stop_distribution.csv`) or store-coverage
  metadata (`calendar_early_closes.csv`) as derivatives is a reading of the Databento licence text, not of the
  files; this scan did not read the licence.
- **No guard exists.** `tests/` has no check on result files' columns (searched for licence/price wording:
  only data-store and synthetic-bar tests). The `q121` file was caught by an auditor, not by a test; the next one
  would be too, or not at all.

## What a guard would declare (not a family)

A fast-tier test, say `tests/test_results_no_price_levels.py`, over `git ls-files results/ '*.csv'` outside
`vendor/` (and the staged set, in the pre-commit hook): (a) refuse a column named for a level (`open`, `high`,
`low`, `close`, `price`, `vwap`, `settle`, `first_open`, `entry_price`, `exit_price`, ...) unless allow-listed under a
decision row; (b) refuse any numeric column whose values are mostly inside the NQ level band and on the 0.25 grid
unless allow-listed as a count or dollars; (c) refuse any pair `(x_pts, x_pct)` or any pair where 100 a/b or a/b is
mostly in-band and on-grid, with an allow-list for the known count/dollar coincidences recorded in this note;
(d) refuse an intraday timestamp column beside any price-class column. The allow-list is itself declared, so a new
column has to be classed before it can be committed. The same rule belongs in the `merge-checklist` skill.

## Sources

- `.gitignore:1-7` (bars and atlas never committed), `.gitignore:36-38` (E-179's ignore of the q121 file and its
  manifest).
- `git ls-files results/`, `git ls-files vendor/stage2/results/`, `git log --all --diff-filter=A|D` as in Method 6,
  run 2026-11-17 on `master` at `d61394e` with the working tree shown in the brief.
- `tests/test_walker.py:1`, `tests/test_walker_breakeven.py:1` (synthetic, hand-built bars).
- The scanner and its outputs: session scratchpad only (not part of the repository).
