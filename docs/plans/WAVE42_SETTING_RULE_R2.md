# Wave 4.2's setting rule, second version: W42-R1 with a floor on the median 12-month net cash and a corrected headroom (rule W42-R2)

**What this is.** A delta declaration. W42-R2 is W42-R1 (`docs/plans/WAVE42_SETTING_RULE.md`, pinned by E-283) with
**two changes**: **one added limit** and the one input it reads (Q-221), and **a corrected headroom for every limit**
(E-296, and the lead's ruling on the red team's B-1). Everything not stated here is **as W42-R1**, word for word and
code for code. Its code is `extended/wave42_r2.py`; its one declared application is `scripts/wave42_r2_apply.py`
(section 6); `tests/test_wave42_r2.py` holds the code to this text (the tables below are machine-read), and
`tests/w42r2_power.py` runs the power check of section 7 against the criteria declared there.

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

**Why the corrected headroom (E-296 (2); the red team's B-1).** W42-R1's headroom counts only the held-out test's coin
noise, at the drawn winner's per-seed sd. M_best, the best baseline's search-year estimate, carries its own coin noise
at H4's seed count, which W42-R1 does not count; and the drawn winner's sd is selected by the same draw that selects
the winner. W42-R2 counts both noises at sd\*, the largest per-seed sd among the four baselines (section 4). **The aim
(E-296; CHARTER 3.7's limit clause and 3.8 (a)): a design equal to the true best baseline passes each headroom-bound
limit at about the nominal rate 1 - (1 - `POWER_TARGET`) / L at the held-out read, and all limits together with at
least `POWER_TARGET`.** Section 7 tests both claims; its criteria allow the residual winner's curse up to the red
team's worst case.

**The read before the form (the red team's B-3, corrected).** **The floor's form -- a floor, on the p50, at horizon
252 -- was ruled (Q-221) after the early look had shown P-14's H4-B search-year readings of that very statistic**,
the p50 of `net_month_12`, beside a candidate design's (E-291, job `q213-early-look` at `514f6ad`, the page
`docs/plans/EARLY_LOOK.md`; Q-221's ruling followed it). The operator and the lead saw the page; the worker who wrote
this text read none of its figures. **The look-independent reason the lead records for the form:** the floor comes
from CHARTER 2's objective, a user's journey to making money; the median is the objective's convention for a typical
user (CHARTER 2: every measure a distribution over start days, its median first); and horizon 252 is
`journey_measures.YEAR`, the measures' one-year horizon, which W42-R1's other year-horizon measures already use
(`peak_oop_12_months`, `share_months_positive`). The floor's **value** comes only from the formula, applied once to
H4's output. **A reporting line, deciding nothing:** F-13's finalists are shown with and without the floor, so the
effect of a limit whose form was ruled after a look is visible (`r2.report_with_and_without_floor`).

**Status.** Draft for the red team's read (its second cycle). The lead pins it by the LF sha256 of this file, of
`extended/wave42_r2.py` and of `scripts/wave42_r2_apply.py`, before H4-C's collection is read and with the read of
P-14's H4-B readings above on record (section 10), and writes `config/w42_r2_pin.json` (`{"commit": "<40 hex>"}`)
naming the pinning commit. After the pin none is edited; a change is a new rule id under a new row. W42-R1's four
pinned files are never edited (E-283): W42-R2 imports them.

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
runs **W42-R1's own function objects**, the same code objects, over a copy of W42-R1's module namespace in which only
the six tables named in `OVERRIDES` differ (`RULE_ID`, `OUTPUT_NAME`, `LIMITS`, `REQUIRED`, `HORIZONS`,
`CONSTANTS`; `rebind`). The copy is built once per process and built again only when an object in W42-R1's module or
in the tables is not the one it was built from (m-6). W42-R1's module is never changed. **The exception is the
headroom** (E-296 (3)): W42-R1's inline headroom (`extended/wave42.py` lines 809-810) runs as part of W42-R1's code,
and W42-R2 then replaces its result for every limit by its own function `headroom`, re-selecting each limit's value,
which term binds and its vacuity by `limit_value` (W42-R1's section 6 steps 3-4, re-written; fed W42-R1's own needed
value it reproduces W42-R1's limits exactly, which a test holds), and re-reading each baseline's check at the new value
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
| YEAR | `252` | `journey_measures.YEAR`: twelve 21-session months, W42-R1's horizon 252 |
| NET12_KEY | `"net_month_12"` | measure (12) at m = 12: `rel_u[252]`, the 12-month net cash per unit (MEASURES (12)) |
| NET12_KIND | `"net_dollars"` | dollars with no a priori lower end: net cash runs below zero (section 3.3) |
| HEADROOM_FORM | `"sqrt(se_test^2 + se_search^2); se_test = sd* sqrt(n_search / (J n_test)), se_search = sd* / sqrt(J_H4), sd* = the largest per-seed sd among the four baselines"` | E-296 and the lead's ruling on B-1: the headroom's error term (section 4) |
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
2. The headroom (section 4): the needed value M_best - z_L se, se = sqrt(se_test^2 + se_search^2) at sd\*.
3. **The floor is min(M_worst, M_best - z_L se)**: the worst baseline's estimate, unless the headroom is stricter.
   Which binds is reported (`binds`).

**z_L is W42-R1's, joint over the limits set** (W42-R1 section 6, step 2, m-3 (c)): the normal quantile at
1 - (1 - `POWER_TARGET`) / L, L the number of limits set. **W42-R2 sets seven, so L = 7 for every limit**, the six of
W42-R1 included (Bonferroni over the seven). A W42-R1 limit whose headroom binds therefore sits further out under
W42-R2, by z at L = 7 and by section 4's term; a limit the worst baseline binds does not move unless the wider headroom
passes it, in which case the headroom binds (reported).

### 3.3 Its vacuity, read against its own range

W42-R1's code flags a floor at or below zero "at or beyond the a priori end of its range", which is right for its
counts (`taken_mean`) and wrong for net cash, which runs below zero. `limit_value` reads the added limit's vacuity
against its a priori range (-inf, inf): vacuous only when it is at or below every pooled baseline unit (W42-R1's
"beyond every baseline unit"). Vacuity decides nothing for this limit (W42-R1 section 6, step 4: reported and kept).

### 3.4 What it does, and what it does not

- **It refuses a design whose typical 12-month net cash is below every plan on offer** (the worst baseline's
  median), or below the best's minus its headroom when every baseline is close: W42-R1's guard-rail principle ("no
  worse, on anything a user feels, than every plan already on offer") applied to dollars made. **A design equal to
  the worst baseline fails it about half the time, by the rule's intent** (W42-R1 section 6, step 3: the limit is the
  worst baseline's estimate): its held-out estimate falls on either side of the worst's search estimate. That is every
  worst-bound limit's behaviour, unchanged.
- **The floor refuses the do-nothing journey only when its value is above zero, and the output records which case
  holds** (E-296 (5)). The do-nothing journey's 12-month net is zero on every unit, the quitter's minus one fee unit
  (W42-R1's `null_journeys`, each stopping in its first month). `r2.floor_refuses_do_nothing`, `r2.inactivity` and
  each null journey's check in `r2.null_journeys` say which. When the value is at or below zero -- every baseline's
  typical user, or the best's less its headroom, is not ahead after a year -- the floor is not an inactivity guard:
  it is one limit among seven, and W42-R1's guards stand as before (`not_paid_within_B`, the do-nothing composite
  floor, CHARTER 3.8 (c)'s long-run gate).
- **It does not rank.** The composite ranks inside the limits; this limit only removes designs.
- **Where it is read, and the rate's scope (m-1).** Like every limit it is read at the search-year screen and at the
  held-out verdict, at the point estimate, the one-sided check beside it (E-230). **The nominal rate of section 4
  holds at the held-out read only** (J = `TEST_SEEDS` seeds by the complete held-out starts). Read on the search
  years at another size -- j_read seeds by n_read starts of the same history -- a design equal to the best baseline
  meets a headroom-bound value with error sd\* sqrt(n_search / (j_read n_read) + 1 / J_H4), so it is refused with
  share 1 - Phi(z_L se_held / se_read), the sd cancelling (`refusal_at_read`). The output prints that share beside each
  limit for DRAFT_F-13's screen size (4 seeds, every 4th start) and deciding size (16 seeds, every start), deciding
  nothing (`beside.refusal_at_read`). F-13's red team treats an exclusion on a search-year limit at those sizes as a
  power question.
- **Reported with and without** (B-3): F-13's finalists are shown with and without this floor, deciding nothing.

### 3.5 The block `r2` of the output

After W42-R1's code, W42-R2 adds to the output: `application` naming W42-R2's script and output; and a block `r2`
with the parent (rule id, row, commit, the four sha256), the added limit (name, key, horizon, statistic, direction,
value, which binds, its value under W42-R1's headroom beside, the count of limits set and z_L, the headroom form),
where `net_month_12` came from (section 5), each null journey's 12-month net and whether it is inside the floor,
whether the floor refuses the do-nothing journey, and the with-and-without reporting line. The block `h4` gains
`collection_readings_sha256`, the collection's own digest, beside the digest of the readings W42-R2 read.

## 4. The corrected headroom, for every limit (E-296; B-1)

### 4.1 The lines changed

W42-R1's section 6, "The value of each limit", step 2 (`docs/plans/WAVE42_SETTING_RULE.md` lines 481-487), and its
code (`extended/wave42.py` lines 809-810):

> with se_test = the best baseline's per-seed statistic's standard deviation on the search years, times
> sqrt(|E_h search| / (J x n_h test)), J = `TEST_SEEDS`, the needed value is M_best + z_L se_test for a ceiling
> (M_best - z_L se_test for a floor).

and, following from it, step 3's "max(M_worst, M_best + z_L se_test)" and "min(M_worst, M_best - z_L se_test)"
(lines 488-489). **W42-R2 replaces se_test there by se, below, and "the best baseline's per-seed statistic's standard
deviation" by sd\*. Nothing else of section 6 changes**: M_best, M_worst, z_L, the worst-or-needed selection, the
vacuity, the history beside and the checks beside are W42-R1's.

### 4.2 The derivation

Let sd_b be W42-R1's own quantity for baseline b: the standard deviation over H4's seeds of b's statistic read on one
seed's column of E_h (`limit_per_seed_sd`), on |E_h search| start days. **sd\* = max over the four baselines of
sd_b** (ties in the order of `BASELINES`). **Its reason (B-1, the lead's ruling):** the drawn winner's sd_best is
selected by the same draw that selects the winner -- among near-tied baselines the one on top is often not the true
best, and a tightly estimated one on top supplies a small sd while the true best is the noisy one. sd\* bounds the sd
of every baseline, the true best's included, whoever comes out on top.

A design equal to the true best baseline, read at the held-out test on J = `TEST_SEEDS` seeds by n_h test complete
starts, has a point estimate D whose coin error has standard deviation sd_true sqrt(|E_h search| / (J x n_h test)),
sd_true the true best's per-seed sd. M_best, pooled over H4's J_H4 seeds (the readings' seed count, `H4_J` in
production, which H4-C's collection refuses to differ), has its own coin error sd_best / sqrt(J_H4). The two come from
different coins on different days (the search years' H4 seeds and the held-out test's), so they are independent, and
with sd\* bounding both sds,

  se_test = sd\* sqrt(|E_h search| / (J x n_h test)),  se_search = sd\* / sqrt(J_H4),  **se = sqrt(se_test^2 + se_search^2)**

bounds the standard deviation of D - M_best. Where the drawn winner is the true best, a design equal to it passes a
value M_best + z_L se (a ceiling; M_best - z_L se a floor) with probability at least Phi(z_L): **the nominal rate for
each headroom-bound limit at the held-out read**, and the joint claim over the L limits by Bonferroni.

### 4.3 What it does not cover, stated

- **The residual winner's curse.** Where baselines are near-tied, M_best is the largest of noisy estimates and sits
  above the true best's value; sd\* widens the headroom but does not remove that lift. The red team's search put the
  residual at about 1.4 times the nominal share at worst under sd\*; the lead's ruling keeps W42-R1's z and admits no
  further correction unless section 7's check shows the residual above that worst case. The check measures it at
  near ties with unequal sds and independent draws (criterion C1's tolerance and C5).
- **The cost.** Where every baseline is within the headroom, sd\* sets the floor further from M_worst than the drawn
  winner's sd would; section 7 reports that distance.
- **sd\*'s own sampling error (m-2).** At J_H4 seeds a normal-like per-seed statistic's sd has a relative standard
  error near 1 / sqrt(2 (J_H4 - 1)); for quantiles of lumpy or lattice measures it is larger. **It is stated and not
  propagated**: the output prints sd\*'s 95 % chi-square interval beside each limit (`beside.sd_star_interval`,
  normal-theory, indicative only for a lumpy or lattice statistic), deciding nothing.
- **The history.** Both terms are coin noise on the search history and on the held-out history; a held-out history
  unlike the search years' is not covered (W42-R1's scope: the worst-baseline term leaves room for it).

### 4.4 In the code

`extended.wave42_r2.headroom(m_best, sd, n_search, n_test, j_test, j_h4, z, direction)` returns se_test, se_search,
se and the needed value at the sd it is passed (the rule passes sd\*); `limit_value(direction, kind, m_worst, needed,
pooled)` is W42-R1's steps 3-4. Each limit's record keeps W42-R1's estimates and carries `sd_per_seed` (each
baseline's), `sd_star` and `sd_star_baseline`, `best_sd_per_seed`, `best_se_test`, `best_se_search`, `headroom_se`,
`headroom_needed`, and, beside, W42-R1's `value_w42_r1_headroom`, `binds_w42_r1_headroom` and
`headroom_needed_w42_r1` (at L = 7), and the block `beside` (sd\*'s interval, the refusal shares at other read sizes).
`inactivity_guards` is re-read from `not_paid_within_B`'s vacuity at its new value.

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

**The records must name W42-R2's application (m-5).** W42-R1's script stays runnable: if it ran first, W42-R2 would
be refused for good. So Q-189 and DRAFT_F-13 must name `scripts/wave42_r2_apply.py` and `results/w42_r2_values.csv`,
never `scripts/wave42_apply.py` and `results/w42_r1_values.csv`; the lead's records and Q-214 make that change, not
this text.

**The survey's scoring path (a note for Q-214).** **`DRAFT_F-13` imports `limit_estimate` and `limit_check` (and
`limit_per_seed_sd`) from `extended.wave42_r2`**, not from `extended.wave42`: they are W42-R1's functions over
W42-R2's seven limits, and W42-R1's own cannot name the added one. A design is checked against each limit's value as
`pinned_inputs(values)["limits"]` gives it (the corrected headroom's value). `composite_per_seed`, `null_composites`,
`do_nothing_floor`, `above_floor`, `pinned_inputs` and `values_from_rows` are W42-R1's, re-exported by
`extended.wave42_r2`.

## 7. The power check, with its pass criteria declared before it runs (B-2)

A strict line shows power, not only size. `tests/w42r2_power.py`, synthetic only, no bar, no result file. Randomness
from one root `numpy.random.SeedSequence` whose entropy is the sha256 of the check's own name (no literal, no other
block's seed), children by `spawn_key`. Counts as the real ones: a weekday search calendar of the search years, H4's
seed count J_H4 = `H4_J`, `TEST_SEEDS` held-out seeds, a held-out calendar of 640 sessions (W42-R1's tests'
synthetic count) and its complete starts. p0 = 1 - Phi(z_7), the nominal per-limit share. **Three headroom forms are
read on the same draws:** **sd\*** (W42-R2), **winner** (both terms at the drawn winner's sd: the form of `fd1307b`),
and **W42-R1** (the test term only, at the drawn winner's sd).

### 7.1 The criteria (decided before the run; a criterion failing under sd\* stops the pin)

- **C1, size per limit.** For a design equal to the true best baseline, on each headroom-bound limit at the held-out
  read: the refusal share p is at most T p0 + 3 se, where **T = 1.4** (the red team's worst case, the lead's
  tolerance) in a scenario with a real selection (independent draws), and **T = 1** without one (one shared draw).
  se is the binomial standard error at T p0 over independent replications, or, for clustered end-to-end reads (several
  held-out draws per search draw), the cluster standard error of the per-search-draw shares.
- **C2, the joint claim (CHARTER 3.8 (a)).** In the joint scenario, the design passes all seven limits together with
  share at least `POWER_TARGET` - 3 se (cluster standard error).
- **C3, power.** A design profitable by a clear margin passes the added floor with share at least `POWER_TARGET` in
  every end-to-end scenario.
- **C4, the do-nothing journey.** It is refused in exactly the draws whose floor is above zero.
- **C5, the residual winner's curse (the red team's search, re-run).** Over the declared configuration search below,
  the largest ratio p / p0 under sd\* is at most 1.4 + 3.5 se / p0, and the 95th percentile at most 1 + 3 se / p0.
- **C6, the check can fail.** Every headroom-sensitive scenario fails C1, C2 or C5 under the W42-R1 form or the
  winner form. **Stated exceptions:** the scenarios where the worst baseline binds (distinct, two-humped, behind) do not
  depend on the headroom form -- the check verifies that the three forms give the same value in every draw -- so they
  carry C3 and C4 only; and the lattice scenario is form-insensitive by construction (a lattice step is larger than
  any headroom, so every form gives the same refusals), so it carries C1 only -- **checked in code** (R-2): the
  exception holds only if every form's headroom, in every replication, is narrower than the smallest lattice step.

*Amended before the full run, after a machinery smoke of 100 replications per scenario (synthetic only): the lattice
scenario moved into C6's exceptions, and `top_two_tied`'s two lower baselines moved closer to the top (within every
form's headroom, so the scenario can tell the forms apart). No criterion's threshold changed. **Both amendments make
the check stricter**: the lattice exception is claimed only where the code shows every form's headroom inside the
lattice step (R-2), and `top_two_tied` can now fail the old forms where before it could not.*

**The order of record (R-1), plainly.** C1 to C6 and the two amendments first reached git in `db3cc27`, which was
committed after the full run. Their pre-run order is not shown by git: it rests on the worker's statement that this
file's LF sha256 was recorded before the run (`d3ca12f3af9e4a855ce14772be0e11d650618d0271af4e1d13279c3437ad71ec`) and
was unchanged after it, as `db3cc27` holds it.

### 7.2 The scenarios

**Part 1, size on one limit, exact statistics, independent replications** (4000 each). Per replication: each
baseline's units drawn on |E_h search| starts by J_H4 seeds, its pooled statistic M_b and per-seed sd sd_b computed
as W42-R1 computes them (numpy's linear quantile; sd over seeds, ddof 1); the value set by `headroom` and
`limit_value` under each form; the design's estimate the pooled statistic of its units on the held-out starts by
`TEST_SEEDS` seeds.

| scenario | limit | the four baselines' laws | draws | the design |
|---|---|---|---|---|
| `rt_unequal_sd` (the red team's) | floor, p50 | four tied normal medians, the first eight times noisier | independent | the noisy first |
| `top_two_tied` | floor, p50 | two tied at the top, one four times noisier; two lower within every form's headroom | independent | the noisier top |
| `lumpy_headroom` | floor, p50 | paid-or-not two-humped laws, tied medians, the first's paid hump narrow (its median far noisier) | independent | the noisy first |
| `lattice` | ceiling, p90 | an integer count whose 0.9 point sits on a lattice jump, four alike (C6's exception) | independent | the first |
| `equal_independent` | floor, p50 | four alike, equal sds (the classic winner's curse) | independent | the first |
| `identical_shared` | floor, p50 | one shared draw | shared | the first |
| `distinct_shared` | floor, p50 | one shared draw, medians apart by less than the headroom | shared | the top |

**The configuration search (C5), the Gaussian form of the same selection:** 800 configurations, each with 20000
replications: per-seed sds log-uniform over a ratio of eight, true values spread uniformly over up to four of the
pair's standard errors below the top, a shared correlation of the search noises uniform in [0, 0.9], sd estimates
drawn with their chi-square error; the value computed exactly as `headroom` and `limit_value` compute it (a test holds
the vectorised form to them).

**Part 2, the joint read, end to end through `setting_rule`.** Four baselines of one law on every measure (W42-R1's
tests' generator at one parameter set, independent draws) and a tied normal `net_month_12`; the design's every measure
drawn from the same law on the held-out calendar at `TEST_SEEDS` seeds and read against all seven values through
`extended.wave42_r2.limit_estimate` (C2, and C1 per limit). 100 search draws by 4 held-out draws.

**Part 3, the added limit end to end** (C1 where the headroom binds, C3, C4, and the pass curve): the earlier six
scenarios -- distinct, equal (independent), identical (shared), two-humped, behind, distinct with the headroom binding
(shared) -- 40 search draws by 10 held-out draws, the two shared headroom scenarios 100 by 10. The figures are the
check's output, never typed here.

## 8. The tests (`tests/test_wave42_r2.py`)

- **W42-R1 unchanged with the limit off:** on W42-R1's tests' synthetic readings, W42-R2 with `net_floor=False`
  returns W42-R1's output exactly (its digest); W42-R1's module is unchanged by a W42-R2 call; the rebound functions
  run W42-R1's code objects; the namespace is built once and again after a monkeypatch and its restoration.
- **Only the stated keys move with it on:** every output key but `rule_id`, `constants`, `application`, `limits`,
  `h4`, `input_sha256`, `inactivity_guards` (re-read from `not_paid_within_B`'s vacuity) and the new `r2` equals
  W42-R1's; in `limits`, each of W42-R1's six keeps its baseline estimates, best, worst and its per-baseline sds, its z
  is the one at L = 7, its needed value is section 4's at sd\*, and each baseline's check is re-read at its value.
- **The corrected headroom:** by hand; sd\* is the largest of the four baselines' per-seed sds, not the winner's, in a
  reading where a non-winner is the noisiest; `limit_value`, fed W42-R1's own needed values, reproduces W42-R1's six
  limits; a Gaussian check of the red team's scenario where sd\* holds C1 and the winner and W42-R1 forms fail it;
  the beside block (the interval, the read shares, nominal at the held-out read).
- **The floor's value comes from the formula, with no typed number:** recomputed in the test from the readings by
  sections 3.2 and 4.2's words; it moves with the baselines; the module carries no number in the limit's definition.
- **The binding, the refusals and the application**, as before.
- **The power check's machinery** at reduced counts: the criteria functions, each scenario's runner, and the
  vectorised configuration search equal to `headroom` and `limit_value`.

## 9. Everything else: as W42-R1

W42-R1's sections 1 (with section 5 here added), 2 (with section 2 here), 3 (the budgets), 4 (the composite, its six
dimensions, caps, equal weights, the fallback, the null journeys and the do-nothing floor), 5 (delta\* and the power),
6 (with the added limit, L = 7 and section 4's headroom), 7, 8, 9 (with section 6 here) and 11 stand as written.

## 10. The held-out read ledger, and the prior reads

**W42-R2's own entry: W42-R1's, unchanged** -- the held-out session calendar's dates only, read by W42-R1's own
function. W42-R2 reads no held-out session, and H4-B's units files only on their search-year rows (every row's block
checked first). **The prior reads** are W42-R1's section 10, and one more, **a read of H4-B**: the early look (E-291,
job `q213-early-look` at `514f6ad`, 2026-11-27) showed **P-14's H4-B search-year readings** -- among them the p50 and
p10 of `net_month_12`, sessions to the first payout and the first year's out-of-pocket peak -- beside a candidate
design's (RL3's draft base cell), on `docs/plans/EARLY_LOOK.md`; the operator and the lead read the page. **The added
limit's form (a floor, p50, horizon 252) was ruled by Q-221 after that read.** Its look-independent reason is the
header's (CHARTER 2's objective; the median as its typical-user convention; `journey_measures.YEAR`). Its value is
the formula's, on H4's output; the headroom's form is E-296's ruling and the lead's on B-1, derived in section 4 from
W42-R1's text and the synthetic check, chosen from no reading.

## 11. The choices on record for the pin

1. The floor on the p50 of `net_month_12` at horizon 252: the lead's ruling (Q-221), ruled after the early look's
   read of P-14's H4-B readings (section 10), with the reason in the header; reported with and without.
2. L = 7 for every limit's z (W42-R1's joint headroom over the limits set), W42-R1's z kept.
3. The headroom's error term sqrt(se_test^2 + se_search^2) at sd\*, the largest of the four per-seed sds, for every
   limit: E-296's ruling and the lead's on B-1 (section 4); the residual winner's curse measured, not corrected.
4. The added limit's vacuity read against (-inf, inf).
5. `net_month_12` read beside H4-C's collection from H4-B's units files, bound by the sha256 the collection records,
   with parity on every W42-R1 measure; H4-C left as declared.
6. The rule reached through W42-R1's own code objects over copied tables (one code path), the headroom alone replaced
   after it, never a re-implementation of the rest.
7. W42-R2 is the rule applied to H4; W42-R1 is never applied (E-296 (1)); the records name W42-R2's application.
8. The power check's criteria C1 to C6 (section 7.1), declared before it runs.
