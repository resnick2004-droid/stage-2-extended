# Wave 4.2's setting rule, second version: W42-R1 with a floor on the median 12-month net cash (rule W42-R2)

**What this is.** A delta declaration. W42-R2 is W42-R1 (`docs/plans/WAVE42_SETTING_RULE.md`, pinned by E-283) with
**one added limit** and the one input it reads. Everything not stated here is **as W42-R1**, word for word and code
for code. Its code is `extended/wave42_r2.py`; its one declared application is `scripts/wave42_r2_apply.py`
(section 5); `tests/test_wave42_r2.py` holds the code to this text (the tables below are machine-read) and runs the
power check of section 6.

**Why (Q-221, the lead's ruling).** W42-R1's composite and limits contain no dollar magnitude of profit: its "money"
dimension is P_B (`extended/wave42.py`, `DIMENSIONS`, the row `money`), the share of months 1 to 3 ahead under B\*.
A design ahead by a little in most months can therefore outrank one ahead less often by far more. The fix is one
limit in W42-R1's existing `LimitSpec` form: **a floor on the median (p50) of `net_month_12`**, the user's net cash
after twelve months (measure (12) at m = 12, horizon 252), **its value set only by W42-R1's limit formula from the
baselines**, exactly as W42-R1's other limits are. No dollar figure is chosen by anyone. It is **not** a seventh
weighted dimension: the six dimensions and their weights stay as W42-R1 has them.

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

**One code path.** W42-R2 does not re-implement the rule. `extended.wave42_r2.setting_rule` runs **W42-R1's own
function objects**, the same code objects, over a fresh copy of W42-R1's module namespace in which only the six
tables named in `OVERRIDES` differ (`RULE_ID`, `OUTPUT_NAME`, `LIMITS`, `REQUIRED`, `HORIZONS`, `CONSTANTS`;
`rebind`). W42-R1's module is never changed; each call builds the copy afresh. With the added limit switched off
(`net_floor=False`, the identity test's switch, never passed by the application) the same mechanism returns W42-R1's
output exactly (section 7's first test).

## 2. The constants

W42-R2's constants are **W42-R1's section 2, with these replaced or added** (machine-read; the module's
`CONSTANTS_DELTA`, and `CONSTANTS` equals W42-R1's `CONSTANTS` updated by them):

<!-- wave42-r2-constants:start -->
| constant | value | reason |
|---|---|---|
| RULE_ID | `"W42-R2"` | this rule's id |
| OUTPUT_NAME | `"w42_r2_values.csv"` | the one output, written once (W42-R1's is never written by W42-R2) |
| PARENT_RULE_ID | `"W42-R1"` | the parent |
| PARENT_ROW | `"E-283"` | the parent's pinning row |
| PARENT_PIN_COMMIT | `"5e6da6e8c99e6cf2284af19781c2116549cb28e4"` | the parent's pinning commit (E-283) |
| YEAR | `252` | twelve of W42-R1's 21-session months (`12 * MONTH`), W42-R1's horizon 252 |
| NET12_KEY | `"net_month_12"` | measure (12) at m = 12: `rel_u[252]`, the 12-month net cash per unit (MEASURES (12)) |
| NET12_KIND | `"net_dollars"` | dollars with no a priori lower end: net cash runs below zero (section 3.3) |
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

### 3.2 Its value: W42-R1's formula, nothing else

The value is computed by W42-R1's section 6 code, unchanged, on the pooled units of E_252 (MEASURES 1.4, reading 1;
numpy's linear quantile at 0.5):
1. M_b, each baseline's point estimate (`limit_estimate`); the **best** baseline is the highest (a floor), the
   **worst** the lowest, ties in the order of `BASELINES`.
2. The headroom: se_test = the best baseline's per-seed estimate's standard deviation over H4's seeds
   (`limit_per_seed_sd`), times sqrt(|E_252 search| / (J x n_252 test)), J = `TEST_SEEDS`; the needed value is
   M_best - z_L se_test.
3. **The floor is min(M_worst, M_best - z_L se_test)**: the worst baseline's estimate, unless the headroom is
   stricter. Which binds is reported (`binds`).

**z_L is joint over the limits set** (W42-R1 section 6, step 2, m-3 (c)): the normal quantile at
1 - (1 - `POWER_TARGET`) / L, L the number of limits set. **W42-R2 sets seven, so L = 7 for every limit**, the six
of W42-R1 included, so that a design equal to the best baseline passes all seven together with at least the power
target, as W42-R1's principle intends. **A limit of the formula, inherited and stated:** the headroom counts the
held-out test's coin noise only, not the search-year estimate M_best's own; where the headroom binds, a design equal
to the best baseline is refused more often than (1 - `POWER_TARGET`) / L (section 6's check measures how much). This
is W42-R1's formula for all its limits, unchanged here. The consequence of L = 7, stated: **a W42-R1 limit whose headroom binds sits slightly
further out under W42-R2** (z at L = 7 instead of 6); a limit the worst baseline binds does not move; nothing else of
W42-R1's output moves (section 7's second test lists every key).

### 3.3 Its vacuity, read against its own range

W42-R1's code flags a floor at or below zero "at or beyond the a priori end of its range", which is right for its
counts (`taken_mean`) and wrong for net cash, which runs below zero. After W42-R1's code has run, W42-R2 re-reads the
added limit's `vacuous` and `vacuous_reason` against its a priori range (-inf, inf): vacuous only when it is at or
below every pooled baseline unit (W42-R1's "beyond every baseline unit"). **The value is not touched**; vacuity
decides nothing for this limit (W42-R1 section 6, step 4: reported and kept).

### 3.4 What it does, and what it does not

- **It refuses a design whose typical 12-month net cash is below every plan on offer** (the worst baseline's
  median), or below the best's minus its coin headroom when every baseline is close: W42-R1's guard-rail principle
  ("no worse, on anything a user feels, than every plan already on offer") applied to dollars made.
- **It refuses the do-nothing journey exactly when its value is above zero.** The do-nothing journey's 12-month net
  is zero on every unit, the quitter's minus one fee unit (W42-R1's `null_journeys`, each stopping in its first
  month). The output says which (`r2.floor_refuses_do_nothing`, `r2.inactivity`, and each null journey's check in
  `r2.null_journeys`). When the formula's value is at or below zero -- every baseline's typical user, or the best's
  less its headroom, is not ahead after a year -- the floor is not an inactivity guard, and W42-R1's guards stand as
  before (`not_paid_within_B`, the do-nothing composite floor, CHARTER 3.8 (c)'s long-run gate).
- **It does not rank.** The composite ranks inside the limits; this limit only removes designs.
- It is read at the search-year screen and at the held-out verdict, like every W42-R1 limit, at the point estimate,
  the one-sided check beside it (E-230).

### 3.5 The block `r2` of the output

After W42-R1's code, W42-R2 adds to the output: `application` naming W42-R2's script and output; and a block `r2`
with the parent (rule id, row, commit, the four sha256), the added limit (name, key, horizon, statistic, direction,
value, which binds, the count of limits set and z_L), where `net_month_12` came from (section 4), each null journey's
12-month net and whether it is inside the floor, and whether the floor refuses the do-nothing journey. The block `h4`
gains `collection_readings_sha256`, the collection's own digest, beside the digest of the readings W42-R2 read.

## 4. The input it reads

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

## 5. The application

`python scripts/run_clean.py --name w42-r2 -- python scripts/wave42_r2_apply.py`, from a clean checkout of a named
commit, with no argument. **Every step of W42-R1's application is W42-R1's own function** (`scripts/wave42_apply.py`,
imported): the refusal if any Wave 4.2 output exists (W42-R1's included: the two rules are never both applied), H4's
collection result and its sidecar read and hashed from disk, Q-197's search calendar by its pinned sha256, the
held-out counts from the pinned held-out calendar's dates, the fee through `standard_prices`, the readings through
H4's adapter. Then section 4's read of `net_month_12`, W42-R2's rule, and one write, to `results/w42_r2_values.csv`
through `write_result`, every hash in its manifest (W42-R1's list, the units files' sha256, both readings digests,
the parent files' LF sha256, this text's, the module's and the script's). The output's row schema is W42-R1's section
9.1, with the row `r2` added.

**The freeze.** `main` refuses unless W42-R1's freeze holds (W42-R1's own `commit_problem` against
`config/w42_r1_pin.json`) **and** W42-R2's does: the same function, re-made over W42-R2's pin file
`config/w42_r2_pin.json` and its file list, W42-R1's `IMPORTED_FILES` with `extended/wave42_r2.py`,
`scripts/wave42_r2_apply.py` and this text added.

**The survey's scoring path.** A design is checked against the added limit through `extended.wave42_r2`'s
`limit_estimate`, `limit_per_seed_sd` and `limit_check` (W42-R1's functions over W42-R2's limits); W42-R1's own
cannot name it. `composite_per_seed`, `null_composites`, `do_nothing_floor`, `above_floor`, `pinned_inputs` and
`values_from_rows` are W42-R1's, re-exported.

## 6. The power check (a strict line shows power, not only size)

`tests/w42r2_power.py`, synthetic journeys only, no bar, no result. Each replication draws four synthetic baselines'
full readings (W42-R1's tests' generator for every W42-R1 measure; `net_month_12` from the scenario's per-unit law),
**applies W42-R2's rule end to end** to set the floor, then draws a design's held-out units -- `TEST_SEEDS` seeds by
the complete held-out starts at 252 of a synthetic held-out calendar -- and reads the floor at the point estimate.
The search draws and the held-out draws are both replicated, from one seed derived from the check's own name by
sha256 (no literal, no other block's seed). Reported, per scenario:
- the **power** on a design profitable by a clear margin (its true median above the best baseline's), and the pass
  rate along a curve of designs whose true median sits at the floor plus t coin standard errors;
- the **false-refusal rate** on a design equal to a baseline: the best, the worst, and, where every baseline is equal
  (the headroom binds), the baseline;
- whether the do-nothing journey is refused.

Scenarios: four baselines with distinct, positive medians (the worst binds); four baselines of one law drawn
independently (the worst's estimate, below the common median by the search draw's luck, binds); four baselines sharing
one draw of one law (the headroom binds); a lumpy, two-humped per-unit law (paid or not), where a median is least
stable; and baselines whose typical user is behind after a year (the floor at or below zero). The figures are the
check's output, never typed here.

## 7. The tests (`tests/test_wave42_r2.py`)

- **W42-R1 unchanged with the limit off:** on W42-R1's tests' synthetic readings, W42-R2 with `net_floor=False`
  returns W42-R1's output exactly (its digest); W42-R1's module is unchanged by a W42-R2 call; and the rebound
  functions run W42-R1's code objects.
- **Only the stated keys move with it on:** every output key but `rule_id`, `constants`, `application`, `limits`,
  `h4`, `input_sha256` and the new `r2` equals W42-R1's (`inactivity_guards` too, unless `not_paid_within_B`'s value,
  moving to z at L = 7, crosses a vacuity edge); in `limits`, each of W42-R1's six keeps its baseline estimates, best,
  worst and test standard error, its z is the one at L = 7, and its value moves only where the headroom binds.
- **The floor's value comes from the formula, with no typed number:** recomputed in the test from the readings by
  section 3.2's words; it moves with the baselines (a shift of every baseline's `net_month_12` by a constant shifts
  it by that constant; a scale scales it); the module carries no number in the limit's definition.
- **The binding and the refusals:** the readings' base digest must be the collection's; `net_month_12` missing, blank
  on E_252 or not finite is refused; the source must name the four units files.
- **The application** on synthetic files: it applies once, reads the units files by their sha256, refuses a units file
  that is not the collection's, a held-out row, a value differing from the collection's, and any Wave 4.2 output.
- **The power check** at a reduced replication count: the profitable design passes, the do-nothing journey fails a
  positive floor and passes a negative one, a design equal to the best baseline is not refused where the worst binds,
  and the headroom binds where the baselines share one draw; the full check's figures are reported in the hand-back
  of Q-221 from `python tests/w42r2_power.py`, never typed here.

## 8. Everything else: as W42-R1

W42-R1's sections 1 (with section 4 here added), 2 (with section 2 here), 3 (the budgets), 4 (the composite, its six
dimensions, caps, equal weights, the fallback, the null journeys and the do-nothing floor), 5 (delta\* and the power),
6 (with the added limit and L = 7), 7, 8, 9 (with section 5 here) and 11 stand as written.

## 9. The held-out read ledger

**W42-R2's own entry: W42-R1's, unchanged** -- the held-out session calendar's dates only, read by W42-R1's own
function. W42-R2 reads no held-out session, and H4-B's units files only on their search-year rows (every row's block
checked first). **The prior reads** are W42-R1's section 10, and one more: **the operator and the lead have seen
P-14's early-look 12-month figures** (Q-213, E-290 (4)). W42-R2 chooses nothing from them: the limit's key, horizon,
statistic and direction are the lead's ruling; its value is W42-R1's formula on H4's output.

## 10. The choices on record for the pin

1. The floor on the p50 of `net_month_12` at horizon 252: the lead's ruling (Q-221).
2. L = 7 for every limit's z (W42-R1's joint headroom over the limits set), so W42-R1's headroom-bound limits sit
   slightly further out.
3. The added limit's vacuity re-read against (-inf, inf); its value untouched.
4. `net_month_12` read beside H4-C's collection from H4-B's units files, bound by the sha256 the collection records,
   with parity on every W42-R1 measure; H4-C left as declared.
5. The rule reached through W42-R1's own code objects over copied tables (one code path), never a re-implementation.
