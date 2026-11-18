# Audit: Q-44, Q-17's readings beside every user measure (`results/user_beside.csv`, `results/user_beside_starts.csv`)

Auditor's note, 2026-11-18. Independent: no code from `extended/`, `scripts/user_beside.py` or `vendor/stage2/propedge/`
was imported or called. The modules were read only to learn what each column means. The re-derivation is in
`docs/audits/scripts/q44/` (`rederive.py`, `checks2.py` to `checks5.py`; numpy and pandas only). It reads the two
result files, and for the 0 % references `vendor/stage2/results/user_journey.csv` and `vendor/stage2/results/u_budget.csv`.
Nothing heavy was run, and nothing was committed.

**Verdict: sound with caveats.** No wrong number was found. There are three defects, none of which changes a value:
one provenance gap, one promised measure missing, and one labelling error. They are listed below.

## What was audited

| item | value |
|---|---|
| files | `results/user_beside.csv` (headline rows; manifest `rows` 18927), `results/user_beside_starts.csv` (per start; manifest `rows` 192774), each with `.manifest.json` |
| sha256 | both recomputed with `hashlib`; each equals its manifest's `sha256` |
| commit | `git_commit` f7eda0d02e31daea7bfb92847f4ad1203cef014e, `git_dirty` false in both manifests; the read-ledger line's `who.commit` is the same, with `dirty` false. f7eda0d is on `master`, and it is the commit the heavy queue named for Q-44 (E-066, E-123) |
| script, task | `scripts/user_beside.py`, task Q-17, clean run `user-beside` (marker `S2X_CLEAN_RUN`); the log is `%LOCALAPPDATA%\stage2-extended-runs\user-beside.log`, which ends `EXIT 0` |
| declaration | none by design: `prereg_id` null, `exploratory` true, `notes.selection` "none". The spec is E-007 (e), E-013 (1), E-014, E-015 and E-024 (build), with the reader's `registered_design` purpose from E-037 and E-041. No family, so no sha256 pin applies |
| seeds | one seed, the ladder's start-seed base declared in E-024 (`seed` = `parameters.denial_seed`; one child per start, common across designs, arms and responses), with its reserved block of ten (`seed_block`). It is the declared seed, and no other seed appears |
| variants | `variant_count` 114, which equals 3 designs x 2 arms x 19 responses (`parameters.designs`, `arms`, `responses`). Exploratory, no family: the program's k is unchanged and the next family is still k = 13 |
| identity it rests on | U1's start rows (TASK_QUEUE Q-05; Stage 2 D-620). With every response off, the adapter must reproduce `user_journey.csv`'s start rows (E-024 (1)). That was re-derived here on every start (finding H4) |

## Headline numbers: reported against re-derived

Every value below is computed by the scripts named, from the files and columns named.

| headline | reported (`user_beside.csv`) | independent re-derivation | agrees? |
|---|---|---|---|
| all `scorecard`, `extra`, `path`, `response` rows except S3c, S5b and `mdd_P` (114 readings x 2 blocks) | 18,012 values with their `n` | `rederive.py` from `user_beside_starts.csv`: 18,010 agree on value and `n` | yes, except 2 rows inside the cent-rounding bound (H5, C6) |
| P, verdict, off, all, for p14 / p15 / p16 | `measure` P, `value` | P from `net_month_1..3` > 0 on `observed` >= 63; also Stage 2's row to beat in `u_budget.csv` (`section` cell, `role` row to beat) | yes, exactly, `n` equal |
| the ten-measure card, verdict, off, all, for p14 / p15 / p16 | `scorecard` rows | `u_budget.csv` row-to-beat rows (30 values) and `user_journey.csv` metric/month rows by key (both arms) | yes, all exact |
| S3c, off, every design, arm and block (12 rows) | `scorecard` S3c | pooled (`net_month_3` + `fees_month_3`) / `fees_month_3` from `user_journey.csv` start rows, `observed` >= 63 | yes, exactly, `n` equal |
| S5b, off, every design, arm and block (12 rows) | `scorecard` S5b | p90 of the longest gap after the first payout within 126, from `user_journey.csv` `pay_days`, `observed` >= 126 | yes, `n` equal |
| S3c and S5b under the 18 other responses (216 rows each) | `scorecard` | **not re-derivable**: neither file holds fees or pay days for them | D1 |
| `mdd_P` (228 rows) | blank, with a note | nothing to re-derive | D2 |
| the ladder: P non-increasing off, then 10, 25, 50 %, for denial and for forfeiture | `scorecard` P | ordered on every design, arm and block; forfeiture's P at or below denial's at each level | yes (H6) |
| `P_bankroll_2000` <= `P_bankroll_2500` <= P | `extra` | checked on every reading and block | yes |
| shares in [0, 1] | 6,612 share rows | none outside | yes (H7) |

## Findings

### Defects

**D1. S3c and S5b under every response but `off` cannot be re-derived from either file (a provenance gap).**
S3c is payouts per dollar of fees, pooled at month 3. It needs each start's fees, and `user_beside_starts.csv` has no
fees column (E-054 noted this before the run). S5b is the longest gap after the first payout, p90. It needs each start's
payout days, and the per-start file holds only counts and dates of the first events. At `off`, both re-derive exactly
from Stage 2's U1 start rows, because the off rows equal U1's (H4). Under the 18 responses with a firm action they rest
only on the runner's own checks: 216 S3c rows and 216 S5b rows. By the audit rule, these may not be cited in a document
as audited figures. They are the runner's numbers until a file holds fees and pay days per start (as Q-86's / Q-98's
money-spent reading is meant to). This is the same shape as Q-45's D1 (E-189).

**D2. A measure E-007 (e) promised is absent, and the reason given for it was out of date at the run's commit.** E-007
(e) lists "the minimum detectable difference before the read" beside every user reading. Every `mdd_P` row is blank.
The note in each row and in `parameters.mdd` reads "TASK_QUEUE Q-16's calibrated P comparison is not on master
(2026-11-15)". But Q-16 merged under E-035 (`4d3e503`, an ancestor of f7eda0d), and its queue row includes "the P
comparison recalibrated for the scorecard beside". E-194 later fills the same measure for Q-132 from Q-16's comparison.
A promised measure that is absent counts as a deviation. The rest of the reading does not depend on it.

**D3. The identity rows' `response` column is wrong on 108 of 114 rows.** In `section` identity with `stat` holds, every
row with an arm carries `response` = `off`. Yet the text in `measure` names the response that row certifies (for
example "denial_10: every run's payouts and fees ..."). Only 6 of the 114 really certify `off`. A reader who filters
`response == "off"` gets 19 identity rows per design and arm. The `count` rows (exact-length runs) are labelled
correctly. This is cosmetic for the values but misleading for any tool that keys on `response`.

### Caveats

**C1. Provenance beside the run.** The log has no provenance header. It opens with a pandas `DtypeWarning` from the
vendored `read_csv` of `user_journey.csv`, not with the commit and a clean `git status`. The commit and clean state are
in both manifests and the ledger line, so the run is attributable. The 114 variants are not in
`results/variants.jsonl` (0 lines name Q-17, Q-44 or `user_beside`). Both are the same as Q-45's C6 (E-189).

**C2. Assumptions are not stated in the manifests.** The active fill profile is `assumed`
(`vendor/stage2/config/fills.yaml`: `active_profile: assumed`, "Do not report a result computed with this profile
without saying so"). Also unstated: the payout lag, the payout-spacing model, the request amount (`half`, an assumption
under E-034), the no-closure state table, and tier 2 off in the verdict. The 0 % denial verdict and the placement off
are stated (`notes.status`). Each must be named wherever a figure from these files is used.

**C3. S5c (the month-6 concentration) is ill-conditioned under strong responses.** It is a ratio, not a share. It is
above 1 on 26 rows and blank on 42, where the month-6 total is not positive. The largest is p15, verdict, `forfeit_25`,
judged, where the month-6 net total is small against the best quarter's sum (`checks2.py` section 1). Read S5c only
with the total beside it, and never as a share.

**C4. The ladder is monotone in aggregate, not per start.** Start by start, the month-3 net rises from one rung to the
next on between 144 and 225 of 1,629 starts per design, arm and ladder. The count of payouts denied falls from one rung
to the next on a few starts (`checks2.py` section 3). The common start seeds do not nest the denials per start once a
denial changes the path. This is expected, but it cannot be confirmed from the files. Only the aggregate order is
checked.

**C5. The Focused Trader readings have two patterns a reader should not over-read** (verdict arm, all block,
`checks4.py`). The Slowdown models raise P above `off` on some designs, most on p16. And on all three designs, P under
Corrective purchases >= 20 is below P under Corrective purchases >= 10, so P is not monotone in that threshold. Both
patterns come from the engine's `FocusedTraderModel` path, which the files cannot show. They are not called errors here.

**C6. The cent rounding, and the one failed check** (see the failure protocol below). The per-start file stores money
to the cent (`parameters.money` "to the cent"), so dollar figures re-derive only to the cent. My tolerance was about half a
cent on the dollar rows (0.0051 on means, 0.006 on percentiles; the percentiles, means and CVaR10 of `net_month_*`, the spent and deepest-fall columns, and the
evenness dollars), exact on shares, and 1e-5 on S5c. All of these agreed except two S5c rows.

**C7. Most starts under the non-off responses have no exact-length check.** Under those responses, exact-length runs
were made only on the 80 starts whose index is a multiple of 21 and which have at least 21 sessions left (`checks5.py`
re-counts the 80). The other starts read the long replay. On the starts where exact runs were made, none differed.
Under `off`, exact runs were made on nearly every start (the identity `count` row's `n`; the starts too short for a month's exact run excepted), and none differed. The per-start file's
`exact_runs_differing` is blank on all rows, which is consistent with this.

**C8. What the file does not hold.** There is no frontier on P, S1, S3a and S5a, and no long-run gate rows (CHARTER
section 2; Stage 2 D-145). The scorecard page (E-054) builds the frontier. Any document citing these files must put the
gate, ruin, drawdown and payout latency beside it. Stage 2's row to beat is stored only on the verdict arm and the all
block (`u_budget.csv`). The judged-block off rows were therefore checked against U1's start rows, not against a stored
card. The per-start values of the daily path measures (`break_even_day`, `fell_back`, `deepest_fall_after_break_even`)
and of the twelve-month evenness columns come from closes the file does not hold. Their aggregation re-derives, and
they are internally consistent: 12 x `payouts_per_month` and 12 x `share_months_positive` are integers, the count of
payouts within the year is at most `payouts`, `largest_month_share` lies in [1/12, 1], `fell_back` appears only with a
break-even, and every deepest fall is >= 0. But they cannot be rebuilt from first principles here.

### What holds

**H1. The manifest and the commit hold** (see the table above). Both hashes match. The run is from f7eda0d, clean, the
named commit. Its variant count is 114, equal to its readings. It is exploratory, with no selection and no
registration id.

**H2. Nothing read NQ from 2026-07-17.**
- `start_date` runs from 2020-01-02 to 2026-07-16 over 1,691 start days, equal to the bars manifest's `days`,
  `first_day` and `last_day` (`vendor/stage2/data/bars/NQ/manifest.json`, read without loading the bars).
- On every row, `observed` equals min(252, the sessions from the start through 2026-07-16).
- No `first_pass`, `first_payout`, `break_even_day` or `response_day` lies beyond `observed`.
- The ledger line's `dates.end` is 2026-07-16.
- The licensed bar file itself ends 2026-07-16.

**H3. The read-ledger line is a declared read, not a choosing one.** Exactly one line was added (`git diff --numstat`: 1
0). Its `purpose` is `registered_design`, under `declaration.ref` E-024, for P-14, P-15 and P-16. It came from
`scripts/user_beside.py` inside the clean run `user-beside` at f7eda0d, with `dirty` false. That is the purpose E-037 and
E-041 admit for this script, and only for these three registered designs. It reads both blocks, with no selection. Its
`when` plus the manifest's `parameters.seconds` lands on the manifest's `timestamp`.

**H4. The 0 % references hold.** These were compared independently on every start, not on 4 starts as at the build:
- For p14, p15 and p16 on both arms, the `off` per-start rows equal `user_journey.csv`'s start rows: the same start days
  and dates, and `observed`, `first_pass`, `spent_before_first_pass`, `first_payout`, `spent_before_first_payout` and
  `payouts` exactly.
- `net_month_1, 2, 3, 6, 12` agree within the cent rounding (largest gap 0.005).
- The verdict/off/all card equals Stage 2's registered row to beat in `u_budget.csv` for P-14, P-15 and P-16 on all
  ten measures, values and `n` exact.
- The off cards on both arms match U1's metric rows by key.
- So R\* = P-14's registered card is reproduced at 0 % denial with the placement off.

**H5. 18,010 of 18,012 headline values re-derive from the per-start file.** This covers every scorecard measure except
S3c and S5b, every `extra` measure, every `path` and `response` measure, on both blocks, for all 114 readings. It
includes `n_eff_bartlett` (re-implemented from its definition: n times the variance over the Bartlett long-run variance
at lag 63, on each start's months ahead over three) and CVaR10.

**H6. The ladder is ordered** (see the table above).

**H7. Shares lie in [0, 1]** (see the table above).

**H8. No column holds a price level.** By meaning, every column of the per-start file is a count, a session index, a
share, or dollars of the user's cash (nets, fees spent, falls, payout cash). The headline file's `value` holds the same
kinds of number. No measure names a price, a level or a bar field.

**H9. The log's `identity HOLDS` claims, as far as the files allow:**
- "the off arm's start rows equal `user_journey.csv`'s (every column, every start)": confirmed on every column the
  per-start file shares with U1 (H4).
- "the extra P equal to the card's": confirmed, because both equal the re-derived P on every reading and block.
- "the limits' P ordered": confirmed.
- "shares in [0, 1]": confirmed.
- The 114 `count` rows' "exact-length runs whose event days differ": every value is 0, consistent with the blank
  `exact_runs_differing` column. This is a consistency check only.
- **Not checkable from the files:** "every run's payouts and fees against the engine's totals" (no fees or payout cash
  per start, and no engine totals), "D-620's declaration; the builder's identity rows", "the vendored 0 %, placement-off
  replay call", and "the binding Focused Trader models". These rest on the runner.

## The failure protocol: the S5c check

1. **On record.** `rederive.py` found that S5c differs beyond its 1e-5 tolerance on two rows: p15, `forfeit_25`, judged,
   on the verdict and point arms.
2. **Terminal states.** Not applicable. This is a metric, not a path's end state. `n` agrees on both rows.
3. **Stage decomposition.** The difference is in the metric stage only. On the same rows, P, S1, S3a, S3b, S4a, S4b and
   S5a agree, and S5c reads the same `net_month_6` values those measures read.
4. **The component in isolation** (`checks5.py`). The ratio is the best quarter's month-6 net over the total. On these
   rows the total is small against the best quarter's sum. Rounding each of the 532 nets to the cent bounds the ratio's
   error at a value `checks5.py` prints for each arm. On both rows the observed difference is far inside that bound.
5. **Replication.** None needed. The check is deterministic and draws nothing.

**Diagnosis: noise from the per-start file's cent rounding, not a defect.** The pathology it exposes is C3.

## What could not be verified, and why

- **S3c and S5b under the 18 non-off responses** (D1): no per-start fees or pay days.
- **The engine's per-run payout and fee totals, and the identity of net cash = payouts received less fees paid**, for
  any response other than `off`: no fees or payout-cash columns. At `off` it rests on U1's own file.
- **The daily path measures and the twelve-month evenness per start** (C8): only their aggregation and internal
  consistency could be checked.
- **Whether each response was modelled as the firm's rule reads**: denial, forfeiture's household close, the placement
  at 0 and 3 warnings, and the ten Focused Trader models' binding. The files record what each response did (`acted`,
  `response_day`, `payouts_denied`, `cash_forfeited`), not whether it was right. Off, denial and forfeiture behave as
  their names say (`checks3.py`): under `off`, nothing is denied, forfeited or dated; under denial, nothing is forfeited.
- **The analytic oracles** (zero edge: P(pass) <= 2/5, E[gross funded payouts] <= $2,000; propsim D-02) do not apply.
  These are edge-bearing registered designs with no zero-edge twin in the files.
- **Q-17 against its build-time synthetic tests.** Not re-run (light, but out of scope while F-03's T-3 holds `run.lock`).
