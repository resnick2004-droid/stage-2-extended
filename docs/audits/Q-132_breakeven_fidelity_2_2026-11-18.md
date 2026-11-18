# Audit: Q-132, the breakeven-fidelity reading, second version (2026-11-18)

Files audited: `results/breakeven_fidelity_2.csv` and `results/breakeven_fidelity_2_starts.csv`, each with its
`.manifest.json`. Both are collected and not yet committed.

**Verdict: defects found -- one, minor, and no wrong number.**

Every figure the start file can carry was re-derived and agrees:

- the 3456 scorecard, extra and path rows;
- the 396 paired values;
- the 16 filled `mdd_P` values, replicated to 1e-9;
- the registered references.

All 3404 of E-188's P-14 and P-16 rows reproduce exactly. So Q-45's D1 is resolved for the scorecard, extra and path
sections.

**The defect (D1):** `mdd_P` is computed at k = 11's level. At its own commit the program's next k was 13.

Eight caveats travel with any use of the file (section 4).

## Method

The re-derivation is my own pandas/numpy/scipy code:

- the script: `docs/audits/scripts/q132/rederive.py`;
- its full output: `docs/audits/scripts/q132/rederive_output.txt`, cited below as "out §n".

It reads only CSV and JSON files:

- the two results and their manifests;
- Stage 2's registered `user_journey.csv` and the three gate files, plus `rc_reentry_screen.csv`;
- E-188's `results/breakeven_fidelity.csv`.

It imports nothing from `extended/`, `scripts/`, `identity/` or `vendor/`. I read the producing code only to learn what
each column means: `scripts/breakeven_fidelity_2.py`, `extended/breakeven_readings.py`, `user_readings.py`,
`user_measures.py`, `pp_reading.py`, `p_bound.py`, and the vendored `u_select.py` and `user_journey.py`.

No bar, atlas file or engine was touched, and nothing was rerun. The only simulation was synthetic Monte Carlo for
`mdd_P`. It ran for about two minutes on two threads, well under 1 GB.

**Seeds, by role.**

- **The audit's own two**, written into the script's header before its first run:
  - the iid-normal null draws for the OBM and flat-top critical values;
  - the block sign-flip null replications.
- **The runner's declared seeds**, reused only to replicate `mdd_P` exactly, by their manifest roles
  (`parameters.seeds.roles` and `inherited`): Q-16's fixed-b null seed and `mdd_P`'s flip seed.
- **Not re-run:** the honesty-series seed (RD-02 9.2 item 7).
- **Not drawn at 0 %:** Q-17's per-start seed, which is the manifest's `seed`.
- **Not re-run:** the gate's registered campaign seeds, which give common random numbers with the registered rows.

## 1. What was audited

| item | value (source) |
|---|---|
| files | the summary has 5702 rows and the start file 40584 (out §1). The columns equal each manifest's `columns`. The start file is 24 groups (3 designs x 4 rule sets x 2 arms) of 1691 starts (out §2) |
| sha256 | my `hashlib` hashes equal both manifests. The summary manifest's `parameters.start_file.sha256` names the start file's hash (out §1). The checkout's copies under `%LOCALAPPDATA%\stage2-extended-runs\breakeven-fidelity-2\results\` hash equal to the collected copies, and the ledger and variant lines are identical |
| commit, clean | `git_commit` b407fbb85c43... on `master` (an ancestor of HEAD), `git_dirty` false. `parameters.provenance_at_start`: clean, 0 paths changed, detached HEAD. The log's first line says the same (C6 of Q-45 answered). The checkout still exists at b407fbb, and its `git status` shows only this run's outputs |
| run log | `breakeven-fidelity-2.log` beside the checkout: 63 `identity HOLDS` lines, 0 `FAILS` and 0 `REFUSED` (the CSV has 63 `identity` rows, every value 1). It ends `EXIT 0`, with a peak private commit under 3 GB |
| timestamps | the ledger's `when` is 2026-11-18T13:02:58Z and the manifests' times are 18:34:12Z and 18:34:13Z. `parameters.seconds` closes the gap |
| declaration | no family file: `prereg_id` is null, so this is exploratory. The spec is E-189's Q-132 item and E-194's merge row. The read is admitted under E-024 (`registered_design`, E-037) |
| identity it rests on | (i) the repository's: P-14 and P-16 reproduced path for path (`identity/stage2_identity.py`), and Q-17's adapter reproducing `user_journey.csv` with every response off (E-024 (1)). (ii) The runner's own, in this run's log (section 2) |
| references | my hashes of the five `parameters.references` files equal the manifest's (out §1) |
| variants | manifest `variant_count` 9: three corrections x three designs (`notes.variant_count_rule`). Nine lines were appended to `results/variants.jsonl` under `prereg_id` `Q-132:breakeven_fidelity_2`, each `exploratory` true. That file now has 46 lines. No k is spent: this is an exploratory reading, not a family |

## 2. Provenance, window, ledger, licence (the brief's "check also")

- **Clean at b407fbb with the variant count:** holds (section 1).
- **Nothing read NQ from 2026-07-17.**
  - The start dates run from 2020-01-02 to 2026-07-16.
  - On every row, `observed` equals min(252, sessions left).
  - The latest session any start reads is calendar index 1690, which is the last of 1691 sessions (out §2).
  - The summary CSV holds no date string at all.
  - The ledger line's `dates.end` is 2026-07-16.
  - Its four files (A1 events and days, A3 walks, NQ bars) carry the sha256 that `vendor/DATA_MANIFEST_stage2.sha256`
    pins.
  - The bars' `manifest.json` gives `last_day` 2026-07-16 over 1691 days.
- **The read-ledger line:**
  - one line, `purpose` `registered_design`, `declaration.ref` E-024, designs P-14, P-15 and P-16;
  - blocks choice and judged, `clean_run` `breakeven-fidelity-2`, `who.dirty` false, commit b407fbb;
  - this is the purpose E-037 admits for re-reading Stage 2's registered designs, a declared and non-choosing purpose;
  - the manifest's `notes.selection` is "none", every row's `reading` carries the exploratory label (one distinct
    value), and no column or text chooses or carries anything.
- **No column holds a price level.** The summary has no finding (`parameters.licence_guard`).
  - The start file's 62 guard findings are false positives by meaning:
    - `fees_month_*` are dollar fees. Every cell is a whole dollar (447984 cells checked). On every row and month, a
      fee equals payouts received less net cash, with a largest error of 1.42e-07 (out §3).
    - The pair findings are dollars or session counts over session counts (`first_pass`, `months_ahead`,
      `longest_months_without_payout`, `fell_back`).
  - No column is a level, a fill or a timestamp. See caveat C6 for the commit consequence.

## 3. Re-derivations

| headline | as reported (file, rows) | my re-derivation | agrees? |
|---|---|---|---|
| `stage2` start rows = registered | log: "start rows equal user_journey.csv's (every column, every start)", 6 design-arm groups | every start; columns `start_day` through `exact_runs_differing` against `user_journey.csv` `section` = `start` | all 6 groups, 1691 starts each, largest money difference 0 (out §4) |
| scorecard P, S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c | `scorecard`, 480 rows (3 x 4 x 2 arms x 2 blocks x 10) | from the start file by USER_MILESTONES/D-621. P: the three month-end nets > 0 on starts with 63 sessions. S1: the p90 of `spent_before_first_payout` among starts paid by 126. S3a: the share paid by 21. S3b: the p90 of the days to first payout (window 126). S3c: pooled (net + fees)/fees at month 3. S4a/S4b: the share ahead at months 6/12. S5a: the p10 of the month-3 net. S5b: the p90 of the longest gap within 126. S5c: concentration at month 6. Judged = start year >= 2024. No start has an exact-run override (`alt` and `exact_runs_differing` empty on every row, out §2) | all 480, value to 1e-9 relative and every `n` |
| extra (shares ahead m1-m3, P, mean nets, CVaR10, P within $2,000 and $2,500, shares spent over, n_eff, n/63) | `extra`, 720 rows less 48 `mdd_P` | the same starts | all, and every `n` |
| path (first pass and first payout days and spending, break-even, fell back, deepest fall, the six evenness measures) | `path`, 2304 rows | from the start file's columns | all; in total 3456 rows re-made, 0 differ, 0 missing, 0 file rows unmade (out §5) |
| the start file's derived columns | `p_months_ahead`, `months_ahead`, the six evenness columns | re-made from `net_month_*`, `pay_days` and `pay_cash` | 0 rows differ. The daily-path columns satisfy every bound the month ends imply (break-even by any month end at or above zero; fell back where a later month end is below zero; spending before the first payout at least the cash below the start at earlier month ends): 0 violations (out §3) |
| net = payouts less fees | every start, every observed month end | payouts received by the month end (from `pay_days` and `pay_cash`) less `net_month_k` against `fees_month_k`. Also: fees never fall, the payout count, and the first events | 0 violations; largest error 1.42e-07 (out §3) |
| the internal identities | all 48 design-rule-arm-block cards | card P = extra P (value and `n`); P = mean of the three shares; P within $2,000 <= within $2,500 <= P; spent-over shares ordered; CVaR10 <= S5a; S1 = path p90; S3b = path p90 | 0 problems (out §6) |
| shares in [0, 1] | 1326 share rows (scorecard, extra, path, honesty, paired rare coverage), plus trades shares, gate probabilities and the start file's share columns | -- | none outside (out §6) |
| paired intervals (C2) | `paired`, 402 rows: 36 pairs (3 designs x 3 corrections x 2 arms x 2 blocks) | per start, months ahead over three (from the nets), corrected less `stage2`, on common dates (identical sets on every pair). The mean; the kept windows (every other 63-start window); window-mean sign counts; Bartlett n_eff at lag 63; the 90 % two-sided t on the kept means with n_w - 1 df; MDD = (t.95 + t.80) x se; the label and rare coverage from the file's own `honesty` rows | all 396 values equal (1e-9 and `n`). Every paired mean equals the cards' P difference. The six no-interval rows carry the reason my code gives: "identical on these trades" (P-14 `stop_first`, judged, both arms) or "no spread" (out §9) |
| honesty rows | 2 settings (h 63; n_w 5 and 13) x 21 shapes, 20,000 series each | not re-simulated. Checked that coverage + miss above + miss below = 1 on every shape, and that each label and rare coverage follows from them | holds; every label is "covers" |
| `mdd_P` filled by its stated method | `extra`/`mdd_P`: 16 finite (P-15 and P-16 against P-14, judged, every rule set and arm), 32 blank with a reason (P-14 itself; the `all` block not calibrated) | Q-16's `pcons` re-coded (batch means at n // 63 = 9 batches; OBM at 126; flat-top 63/126 with fixed-b critical values from iid-normal nulls). The null: the series centred and sign-flipped in 63-start blocks at a random phase; the 80th percentile of the smallest carried shift | (a) at the runner's declared seeds, replicated: all 16 equal to 1e-9. (b) at the audit's own seeds: 0.898 to 0.913 of the file's values, explained by Monte Carlo error in the flat-top critical value (section 5) (out §10, §10b) |
| gate rows | `gate`, 450 rows | `registered` against the vendored gate files' 0 % rows; `stage2` against them at 1e-6 relative | 90 of 90 equal, and 90 of 90 within 1e-6, for P-14, P-15 and P-16. Every row: `paths` 500, `ruin_probability` 0, growth at `lower_bound` above zero (out §7). **The corrected gate rows are not re-derivable** (C3) |
| trades section | 36 (design, R) groups | the kind shares sum to 1 and are whole counts; trade counts equal across rule sets; `stage2` changes nothing; `stop_first` moves targets to breakeven only (the fall in targets = the rise in breakevens = `changed_kind`; stops and flattens unchanged; mean R never higher); `delay5`/`both` moves bounded by `changed_kind` | 0 problems. P-15's `stage2` trade count at every R equals `rc_reentry_screen.csv`'s `rc_s100_all` `candidates` (out §8) |
| E-188's file reproduced | E-188's 3404 P-14 and P-16 rows (`scorecard`, `extra`, `path`, `gate`, `trades`, every rule set) | key-for-key against this file | 3404 of 3404 equal, every `n` (out §11). So **E-188's corrected scorecard, extra and path figures are now re-derived** through this file's start rows |
| analytic oracles (P(pass) <= 2/5, E[gross] <= $2,000 at zero edge) | -- | not applicable: there is no zero-edge row | -- |

**What the readings show** (descriptive; out §9, §14):

- **P-14 keeps the highest P among P-14, P-15 and P-16.** This holds under every rule set, on both arms and both
  blocks. So Q-45's C1 is answered descriptively: the corrections do not reorder R\*'s candidates.
- **P (verdict arm, all starts):**

  | design | `stage2` | `stop_first` | `delay5` | `both` |
  |---|---|---|---|---|
  | P-14 | 0.671168 | 0.671373 | 0.685287 | 0.685287 |
  | P-15 | 0.642112 | 0.640884 | 0.639042 | 0.639452 |
  | P-16 | 0.620012 | 0.619808 | 0.652343 | 0.652343 |

- **P (verdict arm, judged block):**

  | design | `stage2` | `stop_first` | `delay5` | `both` |
  |---|---|---|---|---|
  | P-14 | 0.719328 | 0.719328 | 0.722129 | 0.722129 |
  | P-15 | 0.660504 | 0.657143 | 0.638655 | 0.639216 |
  | P-16 | 0.616246 | 0.615686 | 0.672269 | 0.672269 |

- **The paired 90 % intervals** (descriptions, RD-02 9.2; no level, nothing decided). Of the 30 intervals formed, only
  P-16 under `delay5` and `both` on the all-starts block excludes zero:
  - verdict arm: [+0.005536, +0.064468];
  - point arm: [+0.005366, +0.063010].

  Every other interval includes zero. On the judged block (5 kept windows), the interval MDDs run up to 0.100565.
- **D-621 (3)(ii)'s tolerances, applied as a description** (corrected against `stage2`; five points on a share, ten
  per cent of the magnitude on dollars, sessions and ratios). Only S5a crosses, under `delay5` and `both`:
  - **P-14, verdict arm, both blocks.** On the judged block S5a goes from 105.699 to -476.206 under `delay5` (Q-45's C3,
    now on start rows).
  - **P-15, verdict arm on both blocks, and point arm on the judged block.**
- **The gate under `delay5`/`both`:** `pf_growth_on_base_p50` rises for every design and shift, and
  `pf_required_p90` and `mean_max_drawdown` fall (out §7). Ruin is 0 throughout. `median_days_to_first_payout`
  stays at 17 to 20 sessions.

## 4. Findings, most serious first

**D1 (minor defect): `mdd_P` is computed at the wrong level -- k = 11, where the program's next k was 13.**

- The level is `parameters.mdd_P.k` 11, level 0.05/132 (out §10). The row notes say "k = 11".
- The module's docstring calls this "the next family's level 0.05 / 132 (k = 11, CHARTER section 2)". But CLAUDE.md at
  b407fbb itself says "F-03 spent k = 12 ... the next is k = 13". That would be level 0.05/182 (out §10 prints
  0.000275).
- The value is labelled honestly. A lower level only raises each critical value, so at k = 13 every `mdd_P` would be at
  least as large. No conclusion changes (C1). Still, it is a parameter that disagrees with the program's count when it
  was built.
- Remedy (the lead's): restate or relabel; do not rerun for it.

**C1: `mdd_P` exceeds the range of P on every computed row.**

- All 16 finite values lie between 1.068003 and 1.343710 (out §10b). P is a share, so no difference in P can exceed 1.
- So Q-16's shipped statistic can detect **no** difference in P between P-15 or P-16 and P-14 on the judged block's
  595 starts, at this level.
- The rows print a finite number without saying so. The "nothing detectable" wording is attached only to an infinite
  value.
- The flat-top lower limit binds in more than 99 % of the null replications on every row (out §10b). Its critical
  value is a far-tail quantile of a heavy-tailed null: 24.0157 at the runner's seed, against 20.8601 and 23.2535 at two
  independent seeds of 400,000 draws each.
- So each `mdd_P` carries roughly a ten-per-cent Monte Carlo uncertainty from that one shared constant. The audit's
  independent-seed values sit at 0.898 to 0.913 of the file's.
- Cite `mdd_P` as "above 1: not detectable", never as a resolution.

**C2: the held-out years are read throughout. Started before E-208 fixed them; enter the reading in the held-out read
ledger.**

- The run began at 2026-11-18T13:02:58Z (the ledger's `when`). E-208, which fixed the held-out years as 2024-01-02 to
  2026-07-16, was committed in 317247f at 17:11:51Z.
- It is a `registered_design` read of Stage 2's baselines, which Stage 2 chose on the whole window. So no rule of E-208
  is broken, but the read is an entry for the ledger (AMENDMENTS draft 3.6 (b)).
- **Which readings touch the held-out years** (out §13):
  - **every `judged` row**, wholly inside them: `scorecard`, `extra` (with `mdd_P`), `path`, and `paired` at block
    judged. That is 595 of P's starts per design, rule set and arm;
  - **every `all` row**: of each group's 1691 starts, 657 are dated in the held-out years and 251 earlier ones run into
    them. Of P's 1629 eligible starts, 657 have 63-session windows that touch them. Only 783 starts lie wholly before;
  - **the `gate` and `trades` sections, and the `verdict` arm through its bound.** The trades are every trade of the
    whole window. The gate's campaigns run on them. Each rule set's bound, which sizes the verdict arm (C4), is
    recomputed from whole-window trades;
  - **the `identity` rows** (the re-walks and the U1 replays over the whole window).
- **Not touched:** the `honesty` rows (synthetic series) and the `assumptions` rows.
- **The designs and variants read on the held-out years:** P-14, P-15 and P-16 under `stage2`, `stop_first`, `delay5`
  and `both`, on both arms. Note that `delay5` is five minutes from alert to order, the reference latency E-202
  (2)(c)/E-207 keeps. So its baselines' held-out figures now exist and have been read.

**C3: the corrected gate and trades rows are still summaries (Q-45's D1, outside Q-132's spec).**

- E-189 asked for per-start rows, and they are complete. But the `stop_first`, `delay5` and `both` gate rows (270
  values) and the trades rows rest on the runner's checks: no per-path or per-trade rows are written.
- I checked only their internal arithmetic (section 3). Cite them as the runner's figures.

**C4: the bound is recomputed per rule set (carried from Q-45 C4).** The start rows now show it.

- Under `stop_first`, which changes only a few dozen trades at most per R (out §8), P-14's month-3 net still differs on
  1624 of 1629 starts on the verdict arm, against 25 on the point arm (out §12).
- So a corrected verdict-arm figure moves through its sizing as well as its trades. This is declared
  (`parameters.bounds`) and must be stated wherever such a figure is used.
- **Q-45's C5 is diagnosed by it.** P-14's small rise in verdict-arm P under `stop_first` is one start gaining one
  month ahead (out §12), on an arm whose sizing changed nearly everywhere. The point arm shows the expected direction
  (one start losing one month).

**C5: intervals on P only.** The paired section covers P. The guard crossings (S5a under `delay5`/`both`, section 3)
stay descriptive and have no interval. Q-45's C3 therefore cannot yet be judged against noise.

**C6: the licence guard will refuse the start file at commit.** The run recorded 62 findings and did not allow-list
them. By meaning none is a price level (section 2). Before collection is committed, the lead must class them in
`tests/price_level_allowlist.csv`:

- `fees_month_*`: whole-dollar fee sums;
- the pairs: counts and dollars over counts.

That is the lead's file, and I did not touch it.

**C7: a misleading log line.** For P-15 under `delay5` and `both` the log prints "the walk: ... at delay 0".

- That is the vendored screen's print of P-15's re-entry delay (`rc_reentry_screen.py` line 109, `rc.DELAY`), not the
  breakeven delay.
- The files show the five-minute move took effect: P-15's `changed_kind` under `delay5` is in the hundreds to
  thousands at every R (out §8), and its month-3 net differs from `stage2`'s on 1627 verdict starts (out §12).
- The log also opens with a harmless pandas `DtypeWarning` on a registered file.

**C8: assumptions to carry wherever the reading is used.** All are stated in the manifests' `parameters.assumptions`
and `notes.assumptions` (Q-45's C7 answered):

- the fill profile `assumed` (never measured);
- payouts lagged 3 sessions after request, with the spacing simulated by the engine (D-18) on the standard payout path;
- the no-closure state table, solved at Stage 2's walk and frozen under every rule set;
- the move at zero latency under `stage2` and `stop_first`, and five minutes (D-266) under `delay5` and `both`;
- 0 % payout denial, the placement off (D-289), and no Focused Trader model;
- the bound per rule set (C4).

None is verified here.

**What holds (in brief):**

- the manifests, hashes, commit and clean run;
- every identity the files can test, against my own code;
- no read past 2026-07-16;
- the ledger line's declared, non-choosing purpose;
- the exploratory label on every row, and nothing chosen;
- the nine variants recorded;
- every re-derivable number;
- E-188's file reproduced to the bit;
- Q-45's D1 (scorecard, extra and path), C1, C2, C5, C6 and C7 answered.

## 5. Failure protocol (checks that failed in my own runs, kept on record)

1. **"First events" check: 5197 violations on the first run.**
   - *Stage:* the metric's input parsing.
   - *Component in isolation:* a scratch check reading the same text with Python's `float()` found 0 violations in
     every field.
   - *Diagnosis:* pandas' fast float parser is not round-trip exact to the last ulp. `first_payout_cash` parsed that
     way differed by an ulp from `pay_cash`'s first entry.
   - My parser was changed to Python's `float()`. The final run shows 0 violations (out §3).
   - Not a file defect. My other comparisons used tolerances far above an ulp, and they agreed before and after.
2. **Paired: two "file statistics I did not make" problems on the first run** (P-14 `stop_first`, judged, both arms).
   - *Diagnosis:* my code omitted `n_w`, the sign counts and `n_eff` when the difference is zero on every start.
     RD-02 9.2's reading writes them, with the "identical" note.
   - My code was corrected. The final run shows 396 of 396 equal (out §9).
   - Not a file defect.
3. **`mdd_P` at the audit's own seeds: 0.898 to 0.913 of the file's values on all 16 rows**, a systematic shortfall
   rather than scatter.
   - *Terminal states:* every replication yields a finite shift.
   - *Stage decomposition:* the flat-top lower limit binds in over 99 % of replications (out §10b), and all 16 rows
     share one flat-top critical value (n = 595).
   - *Component in isolation:* that critical value at three seeds of 400,000 draws gives 24.0157 (the runner's), 20.8601
     and 23.2535 (the audit's). My first run used 200,000 draws and gave 21.7653 (out §10).
   - *Replication with seeds fixed beforehand:* at the runner's declared seeds, which the manifest names by role, my
     re-coded method reproduces all 16 values to 1e-9 (out §10b).
   - *Diagnosis:* Monte Carlo error in one shared far-tail quantile, not an error in the file. Recorded as C1's
     uncertainty.

## 6. What I could not verify, and why

- **The corrected gate and trades figures** (C3): the file has no per-path or per-trade rows.
- **That the corrected walks implement E-012 (2)'s two corrections on the real bars:** that needs the bars and the
  walker. Only the trades' kind movements are checked (`stop_first` moves targets to breakeven only).
- **The log's identities that need the engine or caches:**
  - P-14's re-walked A3 frame against the cache;
  - P-16's and P-15's trades content hashes. Only P-15's trade count against the screen row is checked;
  - the gate's first 500 per-path rows;
  - "payouts and fees against the engine's totals". Only net = received less fees is checked, and it holds.
- **The honesty coverages themselves:** they come from a 20,000-series simulation a setting, which was not re-run. Only
  their arithmetic and the labels drawn from them are checked.
- **The daily-path columns** (`break_even_day`, `fell_back`, `deepest_fall_after_break_even`): the daily closes are
  not in the file. Only the bounds the month ends imply are checked, and they hold.
- **The gate's floor against P-06 at a fresh campaign seed:** not part of this reading. The gates run at the registered
  seeds.

## 7. Verdict

**Defects found -- one minor (D1: `mdd_P` at k = 11's level, not the program's k = 13), no wrong number.**

Everything the files can carry was re-derived by independent code and agrees:

- 3456 summary rows from the start rows;
- 396 paired values;
- 16 `mdd_P` values replicated exactly;
- 180 gate values against the registered files;
- E-188's 3404 rows.

Provenance is clean (b407fbb, `EXIT 0`, 63 identities held). Nothing was read past 2026-07-16. The read is E-024's
declared, non-choosing `registered_design` read, and the reading is exploratory.

The caveats travel with every use. The most important are:

- **C1:** `mdd_P` above 1 means nothing in P is detectable.
- **C2:** the reading touches the held-out years throughout and is to be entered in the held-out read ledger.
- **C3/C4:** the corrected gate and trades rows are the runner's figures, and the bound is recomputed per rule set.
- **C6:** the start file needs allow-list entries before the commit hook accepts it.
