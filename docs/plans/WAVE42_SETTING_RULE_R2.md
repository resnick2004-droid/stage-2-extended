# Wave 4.2's setting rule, second version: W42-R1 with a floor on the median 12-month net cash and a corrected headroom (rule W42-R2)

**What this is.** A delta declaration. W42-R2 is W42-R1 (`docs/plans/WAVE42_SETTING_RULE.md`, pinned by E-283) with
**two changes**: **one added limit** and the one input it reads (Q-221), and **a corrected headroom for every limit**
(E-296). Everything not stated here is **as W42-R1**, word for word and code for code. Its code is
`extended/wave42_r2.py`; its one declared application is `scripts/wave42_r2_apply.py` (section 6);
`tests/test_wave42_r2.py` holds the code to this text (the tables below are machine-read) and runs the power check of
section 7.

**W42-R2 is the setting rule applied to H4; W42-R1 is never applied** (E-296 (1)). Neither had been applied when this
was written (Q-189 pending). W42-R2's application refuses if any Wave 4.2 output exists, W42-R1's included, so the
two are never both applied.

**Why the added limit (Q-221, the lead's ruling).** W42-R1's composite and limits contain no dollar magnitude of
profit: its "money" dimension is P_B (`extended/wave42.py`, `DIMENSIONS`, the row `money`), the share of months 1 to
3 ahead under B\*. A design ahead by a little in most months can therefore outrank one ahead less often by far more.
The fix is one limit in W42-R1's existing `LimitSpec` form: **a floor on the median (p50) of `net_month_12`**, the
user's net cash after twelve months (measure (12) at m = 12, horizon 252), **its value set only by the rule's limit
formula from the baselines**, exactly as the other limits are. No dollar figure is chosen by anyone. It is **not** a
seventh weighted dimension: the six dimensions and their weights stay as W42-R1 has them.

**Why the corrected headroom (E-296 (2)).** W42-R1's headroom counts only the held-out test's coin noise. M_best, the
best baseline's search-year estimate, carries its own coin noise at H4's seed count, which W42-R1 does not count, so
where the headroom binds a design equal to the best baseline is refused more often than the nominal share. W42-R2
counts both (section 4). **The aim: a design equal to the best baseline passes each headroom-bound limit at the
nominal rate, 1 - (1 - `POWER_TARGET`) / L, which restores E-015's power claim** (a design equal to the best baseline
passes every limit together with at least the power target).

**On record.** The operator and the lead have seen P-14's early-look 12-month figures (Q-213, E-290 (4)). That is why
the floor's value comes only from the formula, applied once to H4's output; this text cites no figure of that look,
and the worker who wrote it read none.

**Status.** Draft for the red team's read. The lead pins it, before H4 is read, by the LF sha256 of this file, of
`extended/wave42_r2.py` and of `scripts/wave42_r2_apply.py`, and writes `config/w42_r2_pin.json`
(`{"commit": "<40 hex>"}`) naming the pinning commit. After the pin none is edited; a change is a new rule id under a
new row, made before H4 is read. W42-R1's four pinned files are never edited (E-283): W42-R2 imports them.

---

## 1. The parent

W42-R2's parent is W42-R1 as pinned by E-283 at commit `5e6da6e8c99e6cf2284af19781c2116549cb28e4`, by these LF
sha256 (machine-read: `tests/test_wave42_r2.py` holds each file on disk to its row, and the module's
`PARENT_SHA256` to the table):

<!-- wave42-r2-parent:start -->
| file | LF sha256 (E-283) |
|---|---|
| docs/plans/WAVE42_SETTING_RULE.md | `2179ff4a366d7ba61ecd425674dab8fd361d80a1713d4b8630943c5683662441` |
| extended/wave42.py | `dc6d84c69bcff7210eb5564b613e488c95f72cbe8e783796190c364ad5b723e2` |
| scripts/wave42_apply.py | `b817eada1f00115253ed7e02b7f9eed40b4afa17c5166da6e775296369b1cc77` |
| config/w42_r1_pin.json | `ae7f6044c382c316c9005acba73c7b54ab5768dfa4a78f1a19f83d021fb56dc4` |
<!-- wave42-r2-parent:end -->

**One code path, with one stated exception.** W42-R2 does not re-implement the rule. `extended.wave42_r2.setting_rule`
runs **W42-R1's own function objects**, the same code objects, over a fresh copy of W42-R1's module namespace in which
only the six tables named in `OVERRIDES` differ (`RULE_ID`, `OUTPUT_NAME`, `LIMITS`, `REQUIRED`, `HORIZONS`,
`CONSTANTS`; `rebind`). W42-R1's module is never changed; each call builds the copy afresh. **The exception is the
headroom** (E-296 (3)): W42-R1's inline headroom (`extended/wave42.py` lines 809-810) runs as part of W42-R1's code,
and W42-R2 then replaces its result for every limit by its own function `headroom`, re-selecting each limit's value,
which term binds and its vacuity by `limit_value` (W42-R1's section 6 steps 3-4, re-written; fed W42-R1's own error
term it reproduces W42-R1's limits exactly, which a test holds), and re-reading each baseline's check at the new value
through W42-R1's own `limit_check`. Everything else (the budgets, the composite, its dimensions, caps and weights,
delta\*, the power, the null journeys, the limits' estimates and their per-seed standard deviations) is W42-R1's code.
With the added limit switched off (`net_floor=False`, the identity test's switch, never passed by the application)
the same mechanism returns W42-R1's output exactly (section 8's first test).

## 2. The constants

W42-R2's constants are **W42-R1's section 2, with these replaced or added** (machine-read; the module's
`CONSTANTS_DELTA`, and `CONSTANTS` equals W42-R1's `CONSTANTS` updated by them):

<!-- wave42-r2-constants:start -->
| constant | value | reason |
|---|---|---|
| RULE_ID | `"W42-R2"` | this rule's id |
| OUTPUT_NAME | `"w42_r2_values.csv"` | the one output, written once (W42-R1's is never written) |
| PARENT_RULE_ID | `"W42-R1"` | the parent |
| PARENT_ROW | `"E-283"` | the parent's pinning row |
| PARENT_PIN_COMMIT | `"5e6da6e8c99e6cf2284af19781c2116549cb28e4"` | the parent's pinning commit (E-283) |
| YEAR | `252` | twelve of W42-R1's 21-session months (`12 * MONTH`), W42-R1's horizon 252 |
| NET12_KEY | `"net_month_12"` | measure (12) at m = 12: `rel_u[252]`, the 12-month net cash per unit (MEASURES (12)) |
| NET12_KIND | `"net_dollars"` | dollars with no a priori lower end: net cash runs below zero (section 3.3) |
| HEADROOM_FORM | `"sqrt(se_test^2 + se_search^2); se_search = sd_best / sqrt(J_H4)"` | E-296: the headroom's error term (section 4) |
<!-- wave42-r2-constants:end -->

## 3. The one added limit

### 3.1 Its row

In W42-R1's section 6 table form (machine-read; the module's `NET12_LIMIT`, appended to W42-R1's `LIMITS` as the
seventh):

<!-- wave42-r2-limits:start -->
| name | measure | key | direction | horizon | stat | optional | what a user feels |
|---|---|---|---|---|---|---|---|
| net_month_12_p50 | (12) | `net_month_12` | floor | 252 | p50 | no | the typical user's net cash after a year: what they have made, or lost, in dollars |
<!-- wave42-r2-limits:end -->

### 3.2 Its value: the rule's formula, nothing else

The value is computed on the pooled units of E_252 (MEASURES 1.4, reading 1; numpy's linear quantile at 0.5), by
W42-R1's section 6 with section 4's headroom:
1. M_b, each baseline's point estimate (W42-R1's `limit_estimate`); the **best** baseline is the highest (a floor),
   the **worst** the lowest, ties in the order of `BASELINES`.
2. The headroom (section 4): the needed value M_best - z_L se, se = sqrt(se_test^2 + se_search^2).
3. **The floor is min(M_worst, M_best - z_L se)**: the worst baseline's estimate, unless the headroom is stricter.
   Which binds is reported (`binds`).

**z_L is joint over the limits set** (W42-R1 section 6, step 2, m-3 (c)): the normal quantile at
1 - (1 - `POWER_TARGET`) / L, L the number of limits set. **W42-R2 sets seven, so L = 7 for every limit**, the six
of W42-R1 included, so that a design equal to the best baseline passes all seven together with at least the power
target (Bonferroni). A W42-R1 limit whose headroom binds therefore sits further out under W42-R2, by z at L = 7 and by
section 4's term; a limit the worst baseline binds does not move unless the wider headroom passes it, in which case
the headroom binds (reported).

### 3.3 Its vacuity, read against its own range

W42-R1's code flags a floor at or below zero "at or beyond the a priori end of its range", which is right for its
counts (`taken_mean`) and wrong for net cash, which runs below zero. `limit_value` reads the added limit's vacuity
against its a priori range (-inf, inf): vacuous only when it is at or below every pooled baseline unit (W42-R1's
"beyond every baseline unit"). Vacuity decides nothing for this limit (W42-R1 section 6, step 4: reported and kept).

### 3.4 What it does, and what it does not

- **It refuses a design whose typical 12-month net cash is below every plan on offer** (the worst baseline's
  median), or below the best's minus its headroom when every baseline is close: W42-R1's guard-rail principle ("no
  worse, on anything a user feels, than every plan already on offer") applied to dollars made. **A design equal to
  the worst baseline fails it about half the time, by the rule's intent** (E-296 (2)): its held-out estimate falls
  on either side of the worst's search estimate. That is every worst-bound limit's behaviour, unchanged.
- **The floor refuses the do-nothing journey only when its value is above zero, and the output records which case
  holds** (E-296 (5)). The do-nothing journey's 12-month net is zero on every unit, the quitter's minus one fee unit
  (W42-R1's `null_journeys`, each stopping in its first month). `r2.floor_refuses_do_nothing`, `r2.inactivity` and
  each null journey's check in `r2.null_journeys` say which. When the value is at or below zero -- every baseline's
  typical user, or the best's less its headroom, is not ahead after a year -- the floor is not an inactivity guard:
  it is one limit among seven, and W42-R1's guards stand as before (`not_paid_within_B`, the do-nothing composite
  floor, CHARTER 3.8 (c)'s long-run gate).
- **It does not rank.** The composite ranks inside the limits; this limit only removes designs.
- It is read at the search-year screen and at the held-out verdict, like every limit, at the point estimate, the
  one-sided check beside it (E-230).

### 3.5 The block `r2` of the output

After W42-R1's code, W42-R2 adds to the output: `application` naming W42-R2's script and output; and a block `r2`
with the parent (rule id, row, commit, the four sha256), the added limit (name, key, horizon, statistic, direction,
value, which binds, its value under W42-R1's headroom beside, the count of limits set and z_L, the headroom form),
where `net_month_12` came from (section 5), each null journey's 12-month net and whether it is inside the floor, and
whether the floor refuses the do-nothing journey. The block `h4` gains `collection_readings_sha256`, the collection's
own digest, beside the digest of the readings W42-R2 read.

## 4. The corrected headroom, for every limit (E-296)

### 4.1 The lines changed

W42-R1's section 6, "The value of each limit", step 2 (`docs/plans/WAVE42_SETTING_RULE.md` lines 481-487), and its
code (`extended/wave42.py` lines 809-810):

> with se_test = the best baseline's per-seed statistic's standard deviation on the search years, times
> sqrt(|E_h search| / (J x n_h test)), J = `TEST_SEEDS`, the needed value is M_best + z_L se_test for a ceiling
> (M_best - z_L se_test for a floor).

and, following from it, step 3's "max(M_worst, M_best + z_L se_test)" and "min(M_worst, M_best - z_L se_test)"
(lines 488-489). **W42-R2 replaces se_test there by se, below. Nothing else of section 6 changes**: M_best, M_worst,
z_L, the worst-or-needed selection, the vacuity, the history beside and the checks beside are W42-R1's.

### 4.2 The derivation

Let sd_best be W42-R1's own quantity: the standard deviation over H4's seeds of the best baseline's statistic read on
one seed's column of E_h (`limit_per_seed_sd`), on |E_h search| start days. A design equal to the best baseline, read
at the held-out test on J = `TEST_SEEDS` seeds by n_h test complete starts, has a point estimate D whose coin error
has standard deviation

  se_test = sd_best x sqrt(|E_h search| / (J x n_h test))   (W42-R1's term: one seed's statistic, rescaled from
  |E_h search| units to J x n_h test units).

M_best is the same statistic pooled over H4's J_H4 seeds (the readings' seed count, `H4_J` in production, which
H4-C's collection refuses to differ), so its own coin error has standard deviation

  se_search = sd_best / sqrt(J_H4).

The two errors come from different coins on different days (the search years' H4 seeds and the held-out test's), so
they are independent, and D - M_best has standard deviation

  **se = sqrt(se_test^2 + se_search^2).**

A design equal to the best baseline passes a ceiling at M_best + z_L se (a floor at M_best - z_L se) when
(D - M_best) / se is below z_L (above -z_L), which has probability Phi(z_L) = 1 - (1 - `POWER_TARGET`) / L: **the
nominal rate, for each headroom-bound limit**, and E-015's joint claim across the L limits by Bonferroni. W42-R1's
se_test alone gives Phi(z_L se_test / se), below nominal whenever se_search is not negligible.

### 4.3 What it does not cover, stated

- **The history.** Both terms are coin noise on the search history and on the held-out history; a held-out history
  unlike the search years' is not covered (W42-R1's scope: the worst-baseline term leaves room for it).
- **The choice of the best.** Where two baselines are close, M_best is the larger of two noisy estimates and sits
  above the best's true value (a winner's curse); se counts the noise of one estimate, not of a maximum. The power
  check reports the case of four baselines of one law drawn independently (section 7), where the worst usually binds.
- **The per-seed sd's own error** at J_H4 seeds is not propagated.

### 4.4 In the code

`extended.wave42_r2.headroom(m_best, sd_best, n_search, n_test, j_test, j_h4, z, direction)` returns se_test,
se_search, se, the needed value and W42-R1's needed value beside; `limit_value(direction, kind, m_worst, needed,
pooled)` is W42-R1's steps 3-4. Each limit's record in the output keeps W42-R1's estimates and carries `best_se_test`
(W42-R1's term), `best_se_search`, `best_sd_per_seed`, `headroom_se`, `headroom_needed`, and, beside, W42-R1's
`value_w42_r1_headroom`, `binds_w42_r1_headroom` and `headroom_needed_w42_r1` (at L = 7). `inactivity_guards` is
re-read from `not_paid_within_B`'s vacuity at its new value.

## 5. The input it reads

`net_month_12` is added to W42-R1's required measures (W42-R1 section 1.3), in its never-blank form on E_252 and
with W42-R1's own range for net cash (its `net_month_1` to `net_month_3`) (machine-read; the module's `REQUIRED`
equals W42-R1's with this row added):

<!-- wave42-r2-required:start -->
| key | measure | horizon | low | high |
|---|---|---|---|---|
| `net_month_12` | (12) | 252 | -inf | inf |
<!-- wave42-r2-required:end -->

**Where it comes from.** H4-B's units files (`results/h4_units_<baseline>.csv`) carry `net_month_12` for every
start day and seed, finite on E_252 and blank off it (`extended/h4_audit.py`, `extract_unit_measures`: `rel[252]`
when 252 sessions are left and observed). **H4-C's collection does not carry it**: `scripts/h4_collect.py` reads
only W42-R1's `REQUIRED` keys from the units files, and H4's section 9 lists the collection's keys. So **no re-run of
H4-B is needed**, and H4-C's collection is left as H4 declares it. W42-R2 reads the column beside the collection:

- `scripts/wave42_r2_apply.py` reads it from the four units files that H4-C collected, each bound by its sha256 --
  its sidecar's, and the one H4-C's sidecar records under `units_files_sha256` -- on the deciding rows only (`block`
  `search` checked on every row first; `arm` `off`; `reading` `martingale_outcome`), one per start day and seed of
  the collection, and refuses unless every W42-R1 measure on those rows equals the collection's, value for value.
- The rule then binds the readings: the readings without `net_month_12` must reproduce the collection's
  `readings_sha256`; the readings with it are what W42-R1's code checks and scores, and their digest is recorded
  beside the collection's. A reading that does not reproduce it is refused by W42-R1's own digest check, after its
  held-out guard.
- **The other route, not taken:** H4-C could carry `net_month_12` as one more column (`rows_from_readings` takes
  `extra_keys`; `w42_readings` reads every column), so that the collection's own digest covers it. That changes the
  collection H4's section 9 declares, so it needs an H4 amendment under a row. The rule accepts it as is
  (`net12_source` None: the collection's digest must then cover the column), but the declared application reads the
  units files.

## 6. The application

`python scripts/run_clean.py --name w42-r2 -- python scripts/wave42_r2_apply.py`, from a clean checkout of a named
commit, with no argument. **Every step of W42-R1's application is W42-R1's own function** (`scripts/wave42_apply.py`,
imported): the refusal if any Wave 4.2 output exists (W42-R1's included), H4's collection result and its sidecar read
and hashed from disk, Q-197's search calendar by its pinned sha256, the held-out counts from the pinned held-out
calendar's dates, the fee through `standard_prices`, the readings through H4's adapter. Then section 5's read of
`net_month_12`, W42-R2's rule, and one write, to `results/w42_r2_values.csv` through `write_result`, every hash in
its manifest (W42-R1's list, the units files' sha256, both readings digests, the parent files' LF sha256, this
text's, the module's and the script's). The output's row schema is W42-R1's section 9.1, with the row `r2` added.

**The freeze.** `main` refuses unless W42-R1's freeze holds (W42-R1's own `commit_problem` against
`config/w42_r1_pin.json`) **and** W42-R2's does: the same function, re-made over W42-R2's pin file
`config/w42_r2_pin.json` and its file list, W42-R1's `IMPORTED_FILES` with `extended/wave42_r2.py`,
`scripts/wave42_r2_apply.py` and this text added.

**The survey's scoring path (a note for Q-214).** **`DRAFT_F-13` imports `limit_estimate` and `limit_check` (and
`limit_per_seed_sd`) from `extended.wave42_r2`**, not from `extended.wave42`: they are W42-R1's functions over
W42-R2's seven limits, and W42-R1's own cannot name the added one. A design is checked against each limit's value as
`pinned_inputs(values)["limits"]` gives it (the corrected headroom's value). `composite_per_seed`, `null_composites`,
`do_nothing_floor`, `above_floor`, `pinned_inputs` and `values_from_rows` are W42-R1's, re-exported by
`extended.wave42_r2`.

## 7. The power check (a strict line shows power, not only size)

`tests/w42r2_power.py`, synthetic journeys only, no bar, no result. Each replication draws four synthetic baselines'
full readings (W42-R1's tests' generator for every W42-R1 measure; `net_month_12` from the scenario's per-unit law),
**applies W42-R2's rule end to end** to set the floor -- its value under section 4's headroom, and under W42-R1's
beside -- then draws a design's held-out units -- `TEST_SEEDS` seeds by the complete held-out starts at 252 of a
synthetic held-out calendar -- and reads both floors on the same draw at the point estimate. The search draws and
the held-out draws are both replicated, from one seed derived from the check's own name by sha256 (no literal, no
other block's seed). Reported, per scenario and per headroom form:
- the **power** on a design profitable by a clear margin, and the pass rate along a curve of designs whose true
  median sits at an anchor baseline's (the worst where the worst binds, the best where the headroom binds) plus t
  held-out coin standard errors;
- the **false-refusal rate** on a design equal to the best baseline and on one equal to the worst, beside the nominal
  share 1 - Phi(z_7);
- whether the do-nothing journey is refused.

Scenarios: four baselines with distinct, positive medians (the worst binds); four baselines of one law drawn
independently (the worst's estimate, below the common median by the search draw's luck, usually binds); four
baselines sharing one draw of one law (the headroom binds); a lumpy, two-humped per-unit law (paid or not), where a
median is least stable; baselines whose typical user is behind after a year (the floor at or below zero); and four
distinct baselines sharing one draw, their medians apart by less than the headroom (the headroom binds with the
baselines distinct; their differences exact, so the best is always the same one). The figures are the check's
output, never typed here.

## 8. The tests (`tests/test_wave42_r2.py`)

- **W42-R1 unchanged with the limit off:** on W42-R1's tests' synthetic readings, W42-R2 with `net_floor=False`
  returns W42-R1's output exactly (its digest); W42-R1's module is unchanged by a W42-R2 call; and the rebound
  functions run W42-R1's code objects.
- **Only the stated keys move with it on:** every output key but `rule_id`, `constants`, `application`, `limits`,
  `h4`, `input_sha256`, `inactivity_guards` (re-read from `not_paid_within_B`'s vacuity) and the new `r2` equals
  W42-R1's; in `limits`, each of W42-R1's six keeps its baseline estimates, best, worst and W42-R1's test term, its z
  is the one at L = 7, its needed value is section 4's, and each baseline's check is re-read at its value.
- **The corrected headroom:** by hand; `limit_value`, fed W42-R1's own needed values, reproduces W42-R1's six limits
  (value, binds, vacuity); and **a simulation where W42-R1's term falsely refuses a design equal to the best
  baseline at its predicted, well-above-nominal rate while section 4's refuses it at the nominal rate**.
- **The floor's value comes from the formula, with no typed number:** recomputed in the test from the readings by
  sections 3.2 and 4.2's words, under both headroom forms; it moves with the baselines (a shift of every baseline's
  `net_month_12` by a constant shifts it by that constant; a scale scales it); the module carries no number in the
  limit's definition.
- **The binding and the refusals:** the readings' base digest must be the collection's; `net_month_12` missing, blank
  on E_252 or not finite is refused; the source must name the four units files.
- **The application** on synthetic files: it applies once, reads the units files by their sha256, refuses a units file
  that is not the collection's, a held-out row, a value differing from the collection's, and any Wave 4.2 output.
- **The power check** at a reduced replication count: the profitable design passes, the do-nothing journey fails a
  positive floor and passes a negative one, the correction is idle where the worst binds, and the headroom binds in
  both forms where the baselines share one draw; the full check's figures are reported in Q-221's hand-back from
  `python tests/w42r2_power.py`, never typed here.

## 9. Everything else: as W42-R1

W42-R1's sections 1 (with section 5 here added), 2 (with section 2 here), 3 (the budgets), 4 (the composite, its six
dimensions, caps, equal weights, the fallback, the null journeys and the do-nothing floor), 5 (delta\* and the power),
6 (with the added limit, L = 7 and section 4's headroom), 7, 8, 9 (with section 6 here) and 11 stand as written.

## 10. The held-out read ledger

**W42-R2's own entry: W42-R1's, unchanged** -- the held-out session calendar's dates only, read by W42-R1's own
function. W42-R2 reads no held-out session, and H4-B's units files only on their search-year rows (every row's block
checked first). **The prior reads** are W42-R1's section 10, and one more: **the operator and the lead have seen
P-14's early-look 12-month figures** (Q-213, E-290 (4)). W42-R2 chooses nothing from them: the limit's key, horizon,
statistic and direction are the lead's ruling; its value is the rule's formula on H4's output; the headroom's form is
E-296's ruling, derived in section 4 from W42-R1's text and the synthetic check, before H4 is read.

## 11. The choices on record for the pin

1. The floor on the p50 of `net_month_12` at horizon 252: the lead's ruling (Q-221).
2. L = 7 for every limit's z (W42-R1's joint headroom over the limits set).
3. The headroom's error term sqrt(se_test^2 + se_search^2) for every limit: E-296's ruling (section 4).
4. The added limit's vacuity read against (-inf, inf).
5. `net_month_12` read beside H4-C's collection from H4-B's units files, bound by the sha256 the collection records,
   with parity on every W42-R1 measure; H4-C left as declared.
6. The rule reached through W42-R1's own code objects over copied tables (one code path), the headroom alone replaced
   after it, never a re-implementation of the rest.
7. W42-R2 is the rule applied to H4; W42-R1 is never applied (E-296 (1)).
