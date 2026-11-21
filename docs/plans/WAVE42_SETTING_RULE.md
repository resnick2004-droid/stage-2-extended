# Wave 4.2's setting rule: the limits, the budgets, the weights and the size that matters (rule W42-R1)

**What this is.** E-221 makes four inputs of CHARTER 3.9's pinning row the lead's, "set from H4's search-year results
by a rule declared before H4 is read": the **limits**, the **bankroll budgets B** of measure (24), the **composite's
weights**, and O-3's **size that matters** delta\*. This file is that rule. It is mechanical: given H4's one output it
outputs each value, with no choice left. Its code is `extended/wave42.py`, `setting_rule`, a pure function (no file,
no bar, no result, no randomness). **Its one declared application is `scripts/wave42_apply.py`** (section 9), which
reads H4's collection result from disk and writes the values once. `tests/test_wave42_rule.py` holds the code to this
text (the tables below are machine-read) and recomputes every output from synthetic readings;
`tests/test_wave42_apply.py` runs the application on synthetic files.

**Status.** Corrective cycle 2 of 2. The first read `docs/reviews/WAVE42_RULE_2026-11-20.md` (B-1 to B-8, m-1 to
m-9) was answered in cycle 1 (wt/wt-infra 357a339) under the lead's rulings on B-1, B-3, B-8, m-1 and m-2; the second
read `WAVE42_RULE_v2_2026-11-20.md` (V-1 to V-4, m2-1 to m2-6) is answered here under the lead's rulings on V-1 to
V-4 and the minors. The lead pins it in one row before H4 is read, **by the sha256 of this file, of
`extended/wave42.py` and of `scripts/wave42_apply.py`** (B-1, V-1: neither the code nor its application can change
under a pinned text), with `SEARCH_CALENDAR_SHA256` filled from Q-197's result before the pin (V-3). After that none
is edited: a change is a new rule id under a new row, made before H4 is read, or a re-declaration of the search
(CHARTER 3.9).

**What it governs and what it does not.** It sets the four values above, the primary budget B\* that P under the
bankroll stop reads, the composite's dimension definitions and normalisers (CHARTER 3.9 pins them with the weights),
the composite-or-fallback choice, the level of the one-sided check printed beside each limit (3.8 (a)), and **the
held-out test's seed count J** (`TEST_SEEDS`, B-3), and the **floor** a finalist's composite must exceed (V-4). It
does not set the power target (it reads `family_stats.MDL_POWER`), the held-out start counts (derived from the pinned
held-out calendar, V-2), the regimes, "most years", the
finalist order, the gate's quantile, the no-harm margin or the L values: those are the pinning row's other inputs.

---

## 0. Corrective cycle 1: finding → where it is answered

| finding | the change | where |
|---|---|---|
| B-1 the input not bound to H4's one output | the rule takes H4's one output, bound by its result file's sha256 and manifest: every declared start day and seed, the declared optional measures, the martingale-outcome reading, the content digest; a second application, or a subset, is refused; run once from a clean checkout, written with a manifest; the pin covers the code's sha256 | 1, 9 |
| B-2 sessions left trusted from the caller | computed here from the pinned search calendar, uncapped, the start session counted; a start off the calendar is refused | 1.2 |
| B-3 J an input, set from the rule's output | J is the declared constant `TEST_SEEDS`, fixed in this text before H4 is read; never an input; J_needed above it fails the gate, with no re-run at a larger J | 2, 5.3 |
| B-4 the redundancy drop on the wrong axis | removed: the six dimensions and their weights stand; Spearman's rho is reported beside, deciding nothing; the fallback's trigger redefined | 4.3, 4.4 |
| B-5 cost rewards not passing | an unpassed unit scores at the upper cap on cost (z = 0); the caps come from the passed units; ruin's censored state stated | 4.2 |
| B-6 tests that cannot catch the mechanisms | the tests recompute every output from the readings, with hand-built units for the bankroll stop and (24); a mutation check, each blocking mechanism's mutant killed | the tests; `scripts/wave42_mutants.py` |
| B-7 the three-way note's 4.4 in the margin form | 4.4's limit clause rewritten to E-230's form, with this rule's headroom | the three-way note 4.4 |
| B-8 no held-out read ledger | the ledger, in RD-04's leak-clause form; this rule's own entry none in cycle 1, the held-out calendar's dates in cycle 2 (V-2) | 10 |
| m-1 the ROC order not CHARTER 2's | the lead's ruling: equal weights across the kept dimensions, since CHARTER 2 ranks none; the weight table printed; weights per dollar and per session in the output | 4.3 |
| m-2 delta\* ill-conditioned and unbounded above | the lead's ruling: resolution at z = 2 only with at least `H4_MIN_SEEDS` seeds, the count at which a false resolution stays at most 0.05; a declared cap `DELTA_MAX` with its source; below the seed count, section 5's fallback, never relaxed; `DELTA_MIN` and `DELTA_MAX` translated into each dimension's units | 2, 5.1 |
| m-3 the limits | a days limit at W + 1, or beyond every baseline unit, flagged vacuous; each baseline's estimate per search year beside; the headroom's z joint over the limits set | 6 |
| m-4 the fee lattice's reason | the reason corrected; the plan and its ledger key named, and refused otherwise | 1, 3 |
| m-5 caps against 2.2 (a) | recorded: a declared clip under (ii) may take search-year endpoints; the three-way note's sentence amended to say so | 4.2; the three-way note 2.2 (a) |
| m-6 optional measures a toggle | part of B-1: exactly H4's declared list | 1 |
| m-7 the start counts' source | `test_starts_source` (function, commit, calendar sha256), refused if blank | 1 |
| m-8 K_TEST hard-coded | the power figures are reported at k = 13 and recomputed at the assigned k if it differs; k never an input | 5.3 |
| m-9 W fixed at 126 | H4's manifest must declare W = 126; another W is refused | 1 |
| n-5 the fallback's trigger | replaced (B-4) | 4.4 |

The notes n-1 to n-4 ask for no change.

**Corrective cycle 2** (the second read; the lead's rulings):

| finding | the change | where |
|---|---|---|
| V-1 the binding stops at the function | `scripts/wave42_apply.py`, pinned with the rule: it reads H4's collection result and its sidecar from disk and hashes both itself, builds the readings through the one named adapter, and writes once to a fixed name through `write_result`; a second application is refused by the existing output file; the manifest gains `arm` = `off` and the verdict settings; the start days must be every calendar session and the seeds 0 to J - 1 | 1.1, 1.2, 9 |
| V-2 the fee and the counts free | the script derives the fee unit through `standard_prices` and the held-out counts from the pinned held-out calendar's dates (by sha256); the function refuses counts that are not `complete_starts` of that calendar; the read enters the ledger | 1.4, 10 |
| V-3 the file and the calendar unnamed | the collection result `results/h4_w42_input.csv` by name, the adapter `extended/h4_collect.py::w42_readings`, Q-197's `results/search_calendar.csv` by sha256 through its loader; the three workload and supply measures required (H4's draft requires them), so every limit is set | 1.1, 1.2, 1.3, 6 |
| V-4 a do-nothing journey's composite | the do-nothing and quit-at-first-failure composites printed beside the baselines; the do-nothing composite a declared floor a finalist must exceed; the two guards named | 4.5 |
| m2-1 `DELTA_MAX`'s source | relabelled the lead's choice; the illustration grid as context only | 2 |
| m2-2 `TEST_SEEDS`'s reason | relabelled the lead's choice, the worst case's need printed beside it and tested at two counts; Appendix A's H7 row at J = `TEST_SEEDS` | 2, 5.3; the three-way note Appendix A |
| m2-3 W's refusal loose | only the integer 126 is accepted; anything else is refused, never a TypeError | 1.5 |
| m2-4 three surviving mutants | tests for `input_sha256` over the manifest, cost at a pass on session W, and the "beyond every unit" vacuity | the tests |
| m2-5 "oppose inactivity" | corrected: they score it zero, they do not oppose it | 4.2 |
| m2-6 one letter for two things in 4.4 | the count of limits is n_L | the three-way note 4.4 |

**Pre-pin fixes** (the final read `WAVE42_RULE_c2_2026-11-21.md`, pass with minors; not a cycle; the lead's rulings):

| finding | the change | where |
|---|---|---|
| R3-1 the audit's perimeter | the audit list gains the fee path with the ledger's sha256, `MDL_POWER`'s value at the run's commit, and the output manifest's `git_commit` (the clean checkout's, not `-dirty`); "applied once" is write-once inside a checkout, refused once the first output is committed, and any second output anywhere voids both | 1.1 |
| R3-2 the sidecar hash and line endings | the sidecar is hashed with CRLF normalised to LF, the text saying which bytes | 1.1 |
| R3-3 the floor's reading | the do-nothing floor applies at the search-year screen and again at the held-out verdict | 4.5 |
| R3-4 four untested checks | tests for the digest against a hand-written layout and per matrix and seed, the held-out calendar's upper bound and a repeated date, the `w42_*` glob, and the refusal before any input is read | the tests |
| n3-1 the chain's root | H4's collection row is pinned before W42-R1 is applied, and the auditor checks the file's sha256 against it | 1.1 |
| n3-3 the H7 row's wording | each start run to 252 sessions or the block's last session, whichever comes first | the three-way note 6.3; `three_way_arith.parts` |
| C-1 (the survey's read) the survey re-implemented the composite | one public scoring path, which `setting_rule` itself uses and the survey imports; the output file's row schema documented | 9.1, 9.2 |

---

## 1. The input, and what is refused

### 1.1 H4's one output (B-1, V-1, V-3, m-9)

The input is **H4's one output**: H4-C's collection result `results/h4_w42_input.csv` (`COLLECTION_RESULT`, H4's
draft section 9) and its sidecar manifest, written once from a clean checkout. **H4's collection row is pinned before
W42-R1 is applied** (n3-1): the chain from H4's run to this rule's values rests on that row's sha256. **`scripts/wave42_apply.py` reads both
from disk**: it computes the file's sha256 itself, refuses a sidecar whose recorded sha256 is not the file's, records
the sidecar's own sha256 (**over the sidecar's bytes with every CRLF normalised to LF**, R3-2: the bytes the writer
wrote and git stores, so the hash is the same on any checkout under `core.autocrlf`; any other difference changes
it), and builds the four readings through the one named adapter, H4's
`extended/h4_collect.py::w42_readings` (`ADAPTER`; its bit-for-bit round trip is H4's test). The binding's fields are
the sidecar's parameters, the file's sha256 its `sha256`:

<!-- wave42-h4-manifest:start -->
| field | what it binds |
|---|---|
| sha256 | the collection file's own sha256, as the script computes it |
| block | `search`, the only block read |
| reading | `martingale_outcome`, CHARTER 3.2's deciding reading |
| arm | `off`, H4's deciding arm (never a stress arm or the as-walked reading; V-1) |
| denial | 0, the verdict's payout denial (CHARTER 3.8) |
| placement | `off`, the Responsible Trading Program's placement |
| focused_trader | `off`, the Focused Trader Program |
| W | the integer 126, the first-payout window H4's declaration pins (m-9, m2-3) |
| baselines | exactly `naive_coin`, `p14`, `p15`, `p16` |
| starts | every start day H4 declared, which must be every session of the search calendar (H4's draft section 4) |
| seeds | every coin seed H4 declared, which must be the indices 0 to J - 1 (H4's draft section 7) |
| calendar_sha256 | the search calendar's digest (`calendar_digest`) |
| readings_sha256 | the readings' content digest (`readings_digest`), recorded by H4's collection |
<!-- wave42-h4-manifest:end -->

**What the auditor checks** (the pinning row cites each):
- the output's `h4_result_sha256` is the collection file's sha256 **as H4's pinned collection row records it**
  (n3-1);
- its `h4_sidecar_sha256` is the sidecar's, over its bytes with CRLF normalised to LF (R3-2);
- its `readings_sha256` and its start and seed counts are the sidecar's;
- its `search_calendar_file_sha256` is `SEARCH_CALENDAR_SHA256`, and its `held_out_calendar_sha256` is
  `HELD_OUT_CALENDAR_SHA256`;
- its `rule_text_sha256`, `rule_module_sha256` and `script_sha256` are the pinned ones;
- **the fee unit** (`fee_unit`, `fee_via`) is the one `extended.levers_terms.standard_prices` returns, the ledger's
  `subscription_fee` at the recorded `ledger_sha256` (R3-1);
- **the power target** (`power_target`, and `constants.POWER_TARGET`) is `extended.family_stats.MDL_POWER`'s value at
  the run's commit (R3-1);
- **the output manifest's `git_commit`** is the clean checkout's commit, the one the pinning row names, and is not
  `-dirty` (R3-1).

**Applied once.** The script writes its values to one fixed name, `results/w42_r1_values.csv` (`OUTPUT_NAME`),
through `write_result`, which refuses outside a clean run and never overwrites. Before reading anything, the script
refuses if that file, its manifest, or any other `results/w42_*` file exists. **That refusal is write-once inside a
checkout** (R3-1): a clean run is its own checkout, so a second application is refused once the first output is
committed, and **any second W42-R1 output found anywhere -- another checkout, another commit, another folder -- voids
both**, under the failure protocol (diagnosed, never chosen between). Never a list a caller passes. The function
`setting_rule` stays pure, but only the script is the declared way to apply it.

### 1.2 The search calendar and sessions left (B-2, V-3)

The search calendar is Q-197's pinned result, `results/search_calendar.csv` (`SEARCH_CALENDAR`), read through its
loader `extended.search_calendar.load_search_calendar`, and **bound by its file's sha256** `SEARCH_CALENDAR_SHA256`,
filled in from Q-197's result manifest before this rule is pinned; while it is unset the script refuses. Its dates
run strictly from `SEARCH_FIRST` to `SEARCH_LAST`; it is a date list, calendar arithmetic, not an outcome. **Sessions
left are computed here, uncapped:** a start day's sessions left are the calendar sessions from the start to
`SEARCH_LAST`, **the start session counted as session 1** (as `three_way_arith.complete_starts` counts it, and as the
engine's day 1 is the start's first session). E_h is the start days with at least h sessions left. **Every session
of the calendar is a start** (H4's draft section 4), so a start set short of the calendar is refused whoever built
the manifest (V-1's hardening); a start day not on the calendar is refused. The caller never supplies sessions left.

### 1.3 The readings

One reading per baseline of CHARTER 2's Topstep set, exactly `naive_coin`, `p14`, `p15`, `p16`. A reading carries:
- its block tag, which must be `search`, and its reading tag, which must be `martingale_outcome`;
- its start days, every session of the calendar, the manifest's;
- its coin seeds, the manifest's, the indices 0 to J - 1, at least two (below `H4_MIN_SEEDS` no gap may resolve,
  5.1);
- for each per-unit measure below, **all required** (V-3 (a): H4's draft requires the firm path to emit the workload
  and supply measures, so no limit is left to a build), the matrix x[s, c] over start days by seeds, in MEASURES.md's
  never-blank form.

| key | measure | horizon | per-unit form |
|---|---|---|---|
| `net_month_1` .. `net_month_3` | (12) | 21 m | `rel_u[21 m]` |
| `peak_month_1` .. `peak_month_3` | section 2's stop | 21 m | the peak out-of-pocket through close 21 m |
| `spent_before_first_payout` | (6) / (24) | W | `spent_before(rel_u, k*_u)`, the censored lower bound at W + 1 when unpaid |
| `first_payout_days` | (5) | W | `first_payout_u`, or W + 1 |
| `first_pass_days` | (1) | W | `first_pass_u`, or W + 1 (B-5: it tells cost which units passed) |
| `cash_to_first_pass` | (2) | W | the all-units form; read only on passed units (4.2) |
| `peak_oop_12_months` | (25) | 252 | `PeakOOP_u` |
| `share_months_positive` | (18) | 252 | the per-unit share |
| `orders_max`, `accounts_max` | (30) | W | the per-unit maximum over observed sessions |
| `taken_mean` | (37) | W | the per-unit mean of `taken_d` |

### 1.4 Beside the readings: derived by the script, never typed (V-2)

- **The fee unit** (m-4): one month of the subscription of Topstep's 50K Standard path, the plan the four baselines
  run, **read by the script through `extended/levers_terms.py`'s `standard_prices`** (Stage 2's verified
  `subscription_fee`), with the ledger file's sha256 recorded. Its source must be named exactly `FEE_SOURCE`.
- **The held-out start counts** per horizon (63, 126 and 252) are **derived by the script from the pinned held-out
  session calendar** `results/q82_judged_sessions.csv` (`HELD_OUT_CALENDAR`, E-208): its bytes must hash to
  `HELD_OUT_CALENDAR_SHA256`, only its `date` column is read, every date inside 2024-01-02..2026-07-16 and
  increasing, and the counts are `complete_starts` of its session count (calendar arithmetic, no outcome). The
  function refuses counts that are not exactly `complete_starts` of the session count it is told, or a source that
  is not that file and sha256. This read is the rule's own held-out ledger entry (section 10).
- **The seed count J is not an input** (B-3): it is `TEST_SEEDS`, section 2.

### 1.5 Refused before any value is computed

The script refuses (`ApplyRefused`) an existing Wave 4.2 output, a missing collection file or sidecar, a sidecar
that is not the file's, an unpinned or other search calendar, a held-out calendar that is not the pinned one or
holds a date outside the held-out years, and an adapter or loader not built on its commit. The rule refuses
(`Wave42Refused`):

**The held-out guard runs first**, before anything else is looked at:
- a reading whose block tag is anything but `search` (a held-out, confirmation or untagged reading);
- any start day before 2020-01-02 or after 2023-12-29, the search years of E-208 (so every held-out day, from
  2024-01-02, and every confirmation-window day, from 2026-07-17).

Then:
- a reading other than the martingale-outcome reading;
- a baseline set other than the four, or a reading under another baseline's name;
- a calendar not strictly increasing from `SEARCH_FIRST` to `SEARCH_LAST`;
- a result sha256 that is not 64 hex digits; a manifest lacking a field of 1.1's table; a manifest naming another
  file, block, reading, arm, verdict setting or baseline set; a W that is not the integer 126 (a string, a float, a
  list or a boolean included); a calendar whose sha256 is not the manifest's;
- start days or seeds that are not exactly the manifest's (a subset, a superset or another list);
- repeated seeds, fewer than two, or seeds other than 0 to J - 1; start days not strictly increasing; a start day not
  on the calendar; start days that are not every session of the calendar;
- readings not paired (the same start days and seeds for every baseline);
- a fee unit that is not a positive amount, or whose source is not `FEE_SOURCE`;
- a held-out start count missing for a horizon, not positive, or not `complete_starts` of
  the held-out calendar's session count; a `test_starts_source` that is not the pinned file and sha256 with an
  integer session count;
- a horizon whose E_h is empty (no start day with h sessions left);
- a required measure missing, a matrix of the wrong shape, a blank (or non-finite) value on E_h (MEASURES 1.3's
  blank rule), or a value outside its a priori range (a share outside [0, 1], days outside [0, W + 1], a negative
  dollar spend);
- a unit paid by W before its first pass;
- readings whose content digest is not the manifest's `readings_sha256`.

## 2. The constants

Every constant of the rule, its value and its reason. `tests/test_wave42_rule.py` reads this table and holds each
value equal to `extended/wave42.py`'s.

<!-- wave42-constants:start -->
| constant | value | reason |
|---|---|---|
| RULE_ID | `"W42-R1"` | this rule's id; a change after the pin is a new id under a new row |
| SEARCH_FIRST | `"2020-01-02"` | E-208's search years, first session |
| SEARCH_LAST | `"2023-12-29"` | E-208's search years, last session |
| HELD_OUT_FIRST | `"2024-01-02"` | E-208's held-out years, first session; only their calendar's dates are read |
| HELD_OUT_LAST | `"2026-07-16"` | E-208's held-out years, last session |
| BLOCK | `"search"` | the only block tag read (CHARTER 3.6 (e)) |
| READING | `"martingale_outcome"` | CHARTER 3.2's deciding reading, the only one read (B-1) |
| ARM | `"off"` | V-1: H4's deciding arm; a stress arm or the as-walked reading is refused |
| VERDICT | `{"denial": 0.0, "placement": "off", "focused_trader": "off"}` | V-1: the verdict's settings (CHARTER 3.8; E-008 (2)), bound in H4's manifest |
| COLLECTION_RESULT | `"h4_w42_input.csv"` | V-3: H4-C's one collection result, by name (H4's draft section 9) |
| ADAPTER | `"extended.h4_collect:w42_readings"` | V-1: the one adapter from the collection to the readings (H4's) |
| SEARCH_CALENDAR | `"search_calendar.csv"` | V-3: Q-197's pinned search calendar |
| SEARCH_CALENDAR_SHA256 | `null` | V-3: that file's sha256, **filled from Q-197's result manifest before the pin**; the script refuses while it is unset |
| HELD_OUT_CALENDAR | `"q82_judged_sessions.csv"` | V-2: the pinned held-out session calendar (E-208), its dates only |
| HELD_OUT_CALENDAR_SHA256 | `"59a698623d951772c1ea19439200762026855eb696e859a544597041e0ffbdea"` | V-2: that file's sha256, as its sidecar manifest records it |
| OUTPUT_NAME | `"w42_r1_values.csv"` | V-1: the one output, written once |
| BASELINES | `["naive_coin", "p14", "p15", "p16"]` | CHARTER 2's Topstep baseline set; the order breaks ties |
| W | `126` | the first-payout window of (1), (2), (5), (6) and (24): U1's and Q-44's ledger constant, half a year; H4's declaration must pin the same (m-9) |
| MONTH | `21` | CHARTER 2: a month is 21 sessions |
| AHEAD_TOL | `1e-06` | MEASURES 1.2 (m-11): ahead means above a millionth of a dollar |
| H4_MIN_SEEDS | `62` | m-2, the lead's ruling: the fewest H4 seeds at which a gap may be called resolved. Two equal baselines, ranked so the larger is on top, have a gap whose ratio to its standard error is a Student t with nJ - 1 degrees of freedom in absolute value; this is the smallest nJ at which that ratio exceeds `RESOLVE_Z` with probability at most 0.05 (`test_the_minimum_seed_count_holds_a_false_resolution_at_z_2_to_005`). Below it no gap resolves (5.1); H4's declaration should run at least this many |
| TEST_SEEDS | `1000` | B-3, m2-2: **the lead's choice**, a round number fixed here before H4 is read and copied by H3's declaration. Beside it, the worst case's need (delta\* at `DELTA_MIN` against four baselines equal to the best, sigma at its bound of one, the declared weights): it is at least 1.5 times that need at k = 13 and covers it at every k up to 17, at the held-out complete starts' weekday upper bounds and at 40 fewer sessions (`test_the_declared_j_covers_the_worst_case_with_margin`); the output prints the need at the derived counts (`J_worst_case`). A failed gate is then about the baselines' spread, never J |
| FEE_SOURCE | `"vendor/stage2/config/rules.yaml:subscription_fee"` | m-4: the fee unit is one month of the Standard path's subscription, Stage 2's verified key |
| BUDGET_QUANTILES | `[0.5, 0.75, 0.9]` | the budgets of (24): a typical, a cautious and a deep bankroll among the baselines' users |
| PRIMARY_BUDGET_QUANTILE | `0.75` | B\*: below the median the stop decides most units and P_B reads spending alone; at the 90th percentile it barely binds and P_B is P; the upper quartile is between |
| CAP_QUANTILES | `[0.05, 0.95]` | a dollar or day dimension's normaliser spans the baselines' pooled units, robust to single extreme units |
| CAP_MARGIN | `0.25` | the span is widened by a quarter each side, so a design better than every baseline is not clipped at once; wider caps would dilute the test's power (the three-way note 1.3 and 2.2 (a)) |
| RESOLVE_Z | `2.0` | m-2, the lead's ruling: a gap is resolved when it exceeds twice its standard error, at H4's seed count of at least `H4_MIN_SEEDS` |
| DELTA_FRACTION | `0.25` | when no gap is resolved: a quarter of the baselines' composite spread, one rank's share among four |
| DELTA_MIN | `0.01` | **the lead's choice** (m-2): one hundredth of the composite's [0, 1] range, below which no user would change design; for context, the bottom of the three-way note's illustration grid; the output translates it into each dimension's own units (5.1) |
| DELTA_MAX | `0.05` | m-2, m2-1: **the lead's choice**, delta\*'s declared cap, a conservative one (a cap below the smallest resolved gap sizes the gate for a smaller difference, so stricter). For context only: it is the top of the grid the three-way note illustrates its power arithmetic over (Appendix A, `three_way_arith.DELTA`), whose formulas cover any size. Never relaxed |
| POWER_TARGET | `0.8` | the power target, `family_stats.MDL_POWER` (the three-way note 4.1) |
| K_TEST | `13` | the held-out test's k (CHARTER 3.7: next 13); alpha = 0.05 / (k (k + 1)); the power figures are recomputed at the assigned k if it differs (m-8) |
| LIMIT_CHECK_LEVEL | `0.05` | the one-sided check of crossing printed beside each limit, never deciding (3.8 (a); E-230) |
| J_MAX | `10000000` | the search bound for J_needed, the seed count the forecast needs; beyond it, "not reachable" |
| HELD_OUT_LEDGER | `"the held-out session calendar's dates only"` | B-8, V-2: this rule's own entry in the held-out read ledger (section 10; E-211's form) |
<!-- wave42-constants:end -->

## 3. The bankroll budgets B

1. Pool the per-unit spending before the first payout, `spent_before_first_payout`, over E_W of all four baselines,
   every seed (each baseline weighs equally: the readings are paired, so pooling is equal weighting). This is (24)'s
   own per-unit quantity (MEASURES (6), (24)): the budget is what (24)'s three states read.
2. For each q in `BUDGET_QUANTILES`, take the pooled q-quantile (numpy's linear rule, MEASURES 1.3) and round it **up
   to the fee lattice**: the smallest whole number of fee units at or above it, and at least one. **The reason
   (m-4, corrected):** spending moves in subscription months, activations and resets (the ledger's
   `subscription_fee`, `activation_fee` and `reset_fee`), not in multiples of one price, so the lattice is not where
   spending moves. The rounding is a declared coarsening: it keeps each budget at or above its pooled reading by less
   than one fee unit, the same for every design and baseline, and states the budget in months of the plan's
   subscription, a unit a user reads.
3. The budgets are the distinct values in quantile order. **B\*** is the one at `PRIMARY_BUDGET_QUANTILE`. B\* is the
   budget of the composite's P_B and ruin dimensions and of the bankroll limit; every budget is reported in (24).
4. An unpaid unit's spending is a censored lower bound (MEASURES (6)), so a pooled quantile is a lower bound when it
   falls among censored units. The rule uses the never-blank value as it is and reports the share paid by W beside;
   rounding up to the lattice is the only allowance.
5. B\* pools the naive coin with P-14, P-15 and P-16 (n-3): if the coin's spending tail is the longest, it sets B\*
   for every design alike. This is declared, and the share paid by W is reported beside.

## 4. The composite

### 4.1 The dimensions

Each dimension is one per-unit, never-blank measure, an **unconditional mean over its E_h** of a per-unit value with
a priori bounds, so the whole composite is admitted to the three-way note's Hoeffding/McDiarmid bound (2.2 (a)). The
aliases MEASURES 3 lists are avoided a priori, which is what its m-4 asks: (6) is read only through (24), and (25)
(the peak through twelve months) is not (24)'s before-payout quantity.

<!-- wave42-dimensions:start -->
| name | objective term | measure | key | horizon | direction | kind | why this measure |
|---|---|---|---|---|---|---|---|
| money | making money (CHARTER 3.9) | (13) P_B | `P_B` | 63 | higher | share | months 1-3 ahead under B\*, over three, per unit (MEASURES 2) |
| bankroll | least bankroll | (25) | `peak_oop_12_months` | 252 | lower | dollars | the deepest the user's own money goes in twelve months |
| speed | fastest | (5) | `first_payout_days` | 126 | lower | days | sessions to the first payout, censored at W + 1 (an unpaid unit scores the worst) |
| cost | cheapest pass and payout | (2) | `cash_to_first_pass` | 126 | lower | dollars | cash to the first pass on passed units; an unpassed unit scores at the upper cap, z = 0 (4.2) |
| steady | steady income | (18) | `share_months_positive` | 252 | higher | share | the share of months with a positive net change, per unit in [0, 1] |
| ruin | least ruin | (24) | `run_out` | 126 | lower | share | run out before the first payout at B\*: spending above B\* by W |
<!-- wave42-dimensions:end -->

### 4.2 The normalisers (caps)

Each dimension's per-unit value x is mapped to z in [0, 1], higher better:
z = clip((x - lo) / (hi - lo), 0, 1) for a "higher" dimension, and 1 minus that for a "lower" one.
- **A share** (money, steady, ruin) has fixed caps lo = 0, hi = 1.
- **A dollar or day dimension** (bankroll, speed, cost) takes the pooled units' `CAP_QUANTILES` (all four baselines,
  every seed, on its E_h), q05 and q95, and widens them by `CAP_MARGIN` x (q95 - q05) each side, then clamps them to
  the a priori range (dollars at least zero; days in [0, W + 1]).
- **Cost does not reward not passing (B-5).** A unit unpassed by W (`first_pass_days` = W + 1) scores **at the upper
  cap, z = 0,** on
  cost, the worst, whatever it spent: its value is a censored lower bound (MEASURES (2)) and would otherwise rank a
  unit that bought one evaluation and failed as cheaper than one that passed in its second month. Cost's caps are
  taken from the **passed** units only (the uncensored values); with no passed unit, the caps are [0, one fee unit]
  and every z is 0. The share passed by W is reported beside.
- **Ruin's censored state (B-5's check).** An unpaid unit whose spending stays at or below B\* counts as not run out
  on ruin: it is (24)'s "censored" state, still paying fees and not yet paid. This is acceptable because the limit
  `not_paid_within_B` reads run out plus censored (section 6), so a design that rarely pays is held by the limit even
  where ruin does not see it. Speed scores an unpaid unit at W + 1, its worst.
- **Bankroll (25)** scores a unit that spends little as better: that is what a user feels. Money (P_B), speed, cost
  and steady do not oppose inactivity: they score an inactive unit zero, while bankroll and ruin score it one, so the
  net is a positive floor for a journey that buys nothing (4.5, V-4; m2-5).
- **The caps and 2.2 (a) (m-5).** The clip is in the per-unit definition (the three-way note 2.2 (a), source (ii)):
  every z_d(u) lies in [0, 1] by construction, fixed before the held-out read. The caps' endpoints come from the
  search years, which are independent of the held-out coin field, so the bound is not estimated from the data it
  bounds. 2.2 (a)'s sentence forbids a range claimed from data as a source-(i) bound; the three-way note now says so
  (2.2 (a) item 2).

### 4.3 The weights: equal across the kept dimensions (m-1, the lead's ruling; B-4)

1. **No dimension is dropped (B-4).** The six dimensions and their weights are fixed here. A drop on the pooled
   units' Spearman's rho measured co-movement across users within a design, the wrong axis for a composite that
   ranks designs (CHARTER 3.9: with four baselines, "the dimensions come from variation across start days and
   seeds, not across designs"), and would let H4's data re-rank the weights. The rho matrix of the six z's (pooled
   units of each pair's common set, all four baselines, every seed) is **reported beside, deciding nothing**.
2. **Equal weights (m-1, the lead's ruling).** CHARTER 2 lists the six terms of the objective without ranking them,
   so the rule claims no order the charter does not give: every kept dimension takes the weight 1 / D, D the number
   kept (six in the composite, one in the fallback). The table's order is CHARTER 2's listing order, with P under the
   bankroll stop first because it is the pinned fallback; the order decides nothing but the fallback. The weights are
   non-negative and sum to one:

<!-- wave42-weights:start -->
| dimension | weight |
|---|---|
| money | 0.1667 |
| bankroll | 0.1667 |
| speed | 0.1667 |
| cost | 0.1667 |
| steady | 0.1667 |
| ruin | 0.1667 |
<!-- wave42-weights:end -->

3. **What H4 decides here** is each dimension's normaliser (its caps), so the weight per dollar or per session,
   w_d / (hi_d - lo_d), which the output prints per dimension (`weight_per_unit`), beside the weight. The
   between-baseline spread of each dimension (the four baselines' mean z) is reported beside, deciding nothing.

### 4.4 The composite, or the fallback

- C(x) = sum over d of w_d x (the mean of z_d over the units of E_{h_d}). It lies in [0, 1].
- **The fallback** (CHARTER 3.9: "the weights cannot be set"; n-5): if **every dimension other than money is constant
  over the pooled units of its E_h** (every z equal for every baseline, unit and seed), no weight can be set from
  H4's results for any of them, and the form is `fallback`: P under the bankroll stop at B\* alone, weight one.
  Otherwise the form is the composite, with all six weights. The form is decided here, before the survey, and never
  after a look. The limits stand in both forms.

### 4.5 The null journeys, the floor and the guards against inactivity (V-4)

- **Printed beside the baselines' composites:** the composite of **the do-nothing journey** (it buys nothing and
  trades nothing: no spend, never passed, never paid, no month ahead or positive) and of **the
  quit-at-first-failure journey** (it buys one evaluation, one fee unit, never passes and stops). Each is computed
  from the caps, B\* and the weights with no further data (`null_journeys`). In the composite form the do-nothing
  journey scores exactly bankroll's and ruin's weights (z = 1 on both, 0 on the rest), 2/6; in the fallback, 0.
- **The do-nothing journey's composite is a declared floor** (the lead's ruling, conservative): a finalist's
  composite must exceed it at the point estimate, **twice** (R3-3): at the search-year screen, where Wave 5's
  finalist rule applies the floors before it ranks by the composite, and again **at the held-out verdict**, where a
  finalist's held-out composite must exceed the floor (the floor's value is the one this rule pins, from the caps,
  B\* and the weights). The floor can only remove designs, never add one. The output also lists any baseline at or
  below it.
- **The two guards that stop inactivity**, named: **the not_paid_within_B limit** (a do-nothing journey scores 1
  there and fails it unless the worst baseline is never paid within B\* by W), and **CHARTER 3.8 (c)'s long-run
  gate** (median log growth above zero), which stops a do-nothing or quit-early design at the held-out test. If the
  limit comes out vacuous, the output says so (`inactivity_guards`), and the pinning row must state that only the
  long-run gate stops a quitter.

## 5. The size that matters, delta\*, and the power at it

### 5.1 delta\*

1. Each baseline's composite C_b, and per seed c, C_b(c) on that seed's units. Rank the baselines by C_b, highest
   first (ties in the order of `BASELINES`).
2. For each adjacent pair in the ranking, the gap g = mean over seeds of C_upper(c) - C_lower(c), and its standard
   error se, the seeds' sample standard deviation over the square root of their number nJ. The gap is **resolved**
   when g > `RESOLVE_Z` x se **and** nJ is at least `H4_MIN_SEEDS` (m-2, the lead's ruling: at that count a false
   resolution between two equal baselines, ranked so the larger is on top, stays at most 0.05).
3. **The raw value** is the smallest resolved adjacent gap: among the plans a user can already run, the smallest
   difference known to change which of two a user should run (O-3), so the power gate is held at the strictest
   resolved scale. **The fallback:** if no gap is resolved -- because none clears `RESOLVE_Z`, or because H4 ran fewer
   than `H4_MIN_SEEDS` seeds, in which case none may resolve -- it is `DELTA_FRACTION` x (C_max - C_min).
4. **The bounds.** delta\* = the raw value held between `DELTA_MIN` (the lead's choice) and `DELTA_MAX` (the declared
   cap, its source in section 2): a raw value below the floor is raised to it, one above the cap is held at the cap.
   Neither bound, nor the seed count, is ever relaxed: a reading that cannot meet one takes the fallback or the
   bound, and the output says which (`how`).
5. **In each dimension's units (m-2).** The output prints, per dimension d, delta\* x (hi_d - lo_d) / w_d (in
   dollars, sessions, or share for a share dimension), and the same for `DELTA_MIN`: the change in that dimension
   alone that moves the composite by delta\*.

### 5.2 The planted finalist

As the three-way note 4.3 states: the best baseline plus delta\*, against all four. Against baseline b its true
difference is delta_b = delta\* + (C_best - C_b), so delta\* against the best and more against the others.

### 5.3 The power (the three-way note 2.2 (a) and 2.5)

- alpha = 0.05 / (k (k + 1)) at k = `K_TEST`; c_h = sqrt(2 ln(1 / alpha)). **The power figures are at k = 13**
  (m-8): if the held-out test is assigned another k (E-204's rule), they are recomputed at it by the same functions
  (`level`, `pair_power`, `conjoint_power`); k is never an input of the rule.
- **The test's seed count J is `TEST_SEEDS`** (B-3, the lead's ruling), fixed in this text before H4 is read and
  never set from this rule's output. H3's declaration copies it, and the three-way note's Appendix A sizes the
  held-out test at it. Beside it the output prints `J_worst_case`, the need at the floor of delta\* with sigma 1.
- The test's units are J seeds by the declared complete held-out starts n_h per horizon; the E_h nest (E_252 within
  E_126 within E_63). With every per-unit z in [0, 1], McDiarmid's bounded differences give the half-width
  c_h sqrt(Q), with
  Q = (1 / J) x the sum over the nested strata of (the stratum's count) x (the sum over the d reaching it of
  w_d / n_{h_d})^2.
  On one horizon, Q = 1 / (J n), the note's own form. (Unit by unit: each held-out unit moves the composite by at
  most a_u = the sum over its dimensions of w_d / (J n_{h_d}), and Q = the sum of a_u squared, which the tests
  compute directly.)
- sigma_b, the per-unit coin noise of the pair's term: on the search years, on the common set of every dimension,
  the within-start-day variance across seeds of the per-unit composite difference (best minus b), averaged over
  start days, its square root; for the pair (planted, best) it is sqrt(2) x the best baseline's own within-day
  standard deviation (the disjoint-seed null's). Each is capped at 1, the bound for terms in [-1, 1].
- **Each pair's power** = Phi((delta_b / sqrt(Q) - c_h) / sigma_b) (2.5's normal approximation; sigma = 0 gives 0 or
  1). **The pass's power** (an intersection-union test: every pair must pass) is bounded below by
  max(0, 1 - the sum of the pairs' misses).
- **Reported:** each pair's power, the conjoint lower bound at J = `TEST_SEEDS`, the same at sigma = 1 (2.5's bound),
  whether it meets `POWER_TARGET`, and **J_needed**, the smallest J up to `J_MAX` at which the conjoint lower bound
  reaches the target (none if not reachable). **If J_needed exceeds `TEST_SEEDS`, the forecast says the gate fails;
  there is no re-run at a larger J.** H3-D's simulation of the pinned rule decides the gate (CHARTER 3.7); this is
  its formula's forecast, deciding nothing on its own.

## 6. The limits

**The form in force** (CHARTER 3.8 (a); E-221, E-230): the point estimate governs; the one-sided check of crossing at
`LIMIT_CHECK_LEVEL` is printed beside, never deciding and never a second margin. Each limit is read on the pooled
units (MEASURES 1.4, reading 1) of its E_h, by numpy's linear quantile.

<!-- wave42-limits:start -->
| name | measure | key | direction | horizon | stat | optional | what a user feels |
|---|---|---|---|---|---|---|---|
| not_paid_within_B | (24) | `not_paid_within_B` | ceiling | 126 | mean | no | the chance of not being paid within B\* by W (run out plus censored; MEASURES (24)'s limit reading) |
| peak_oop_12_months_p90 | (25) | `peak_oop_12_months` | ceiling | 252 | p90 | no | the bankroll the unlucky tenth puts in over a year |
| first_payout_days_p50 | (5) | `first_payout_days` | ceiling | 126 | p50 | no | the typical wait for the first cash |
| orders_max_p90 | (30) | `orders_max` | ceiling | 126 | p90 | no | the busiest day's hand-entered orders |
| accounts_max_p90 | (30) | `accounts_max` | ceiling | 126 | p90 | no | the most accounts live at once |
| taken_mean_p10 | (37) | `taken_mean` | floor | 126 | p10 | no | the trades on offer a session (supply) |
<!-- wave42-limits:end -->

**The value of each limit.**
1. M_b, each baseline's point estimate; the **best** baseline (lowest for a ceiling, highest for a floor) and the
   **worst** (the other way), ties in the order of `BASELINES`.
2. The **headroom** E-015 requires (CHARTER 3.7, 3.8 (a): a design equal to the best baseline passes every limit
   with at least the power target): with se_test = the best baseline's per-seed statistic's standard deviation on the
   search years, times sqrt(|E_h search| / (J x n_h test)), J = `TEST_SEEDS`, the needed value is
   M_best + z_L se_test for a ceiling (M_best - z_L se_test for a floor). **z_L is joint over the limits set** (m-3
   (c)): the normal quantile at 1 - (1 - `POWER_TARGET`) / L, L the number of limits set, so that a design equal to
   the best baseline passes all of them together with at least the power target (Bonferroni), as CHARTER 3.7's
   "every limit check" reads.
3. **The limit is the worst baseline's estimate**, unless that is inside the needed value, in which case it is the
   needed value: a ceiling is max(M_worst, M_best + z_L se_test), a floor min(M_worst, M_best - z_L se_test). The
   principle: **a design may be no worse, on anything a user feels, than every plan already on offer** -- the limit
   is a guard rail at the edge of the known plans, not the objective; the composite ranks inside it. A design may
   therefore match the naive coin on a felt quantity and pass that limit; the composite, not the limit, has to rank
   it. The worst baseline's reading also leaves room for the held-out history to differ from the search years',
   which the coin headroom of step 2 does not cover. Which of the two binds is reported (a tie is the worst
   baseline's).
4. **Vacuous (m-3 (a)).** A limit at or beyond the a priori end of its range (a share ceiling at 1, a days ceiling at
   W + 1, a floor at 0), or beyond every pooled baseline unit (a ceiling at or above every unit's value, a floor at or
   below), is reported **vacuous** with its reason, and kept.
5. **History beside (m-3 (b)).** Each baseline's estimate on each search year's start days (of E_h) is printed
   beside each limit, deciding nothing: a search-years-only reading of how far a change of history moves it.
6. **Every limit is set** (V-3 (a)): each limit's measure is required, and a missing one is refused (1.5).

**No limit on screen hours or trading hours:** the operator ruled no cap on trading hours, every session the firm
allows in the search (the restart plan, section 9, item 6). The verdict's settings (0 % denial, placement off, the
Focused Trader Program off) are the reading's, not limits.

## 7. How the outputs move with a baseline's reading (each row a test)

| a change to H4's readings | what moves | test |
|---|---|---|
| a baseline's spending before the first payout rises | every budget rises or stays, on the fee lattice | `test_more_spending_raises_the_budgets` |
| the worst baseline worsens on a limit's measure | that limit moves out to the new worst estimate | `test_a_worse_worst_baseline_moves_its_ceiling_and_a_better_best_does_not` |
| the best baseline improves, the worst unchanged | the limit does not move | same test |
| every baseline equal on a limit's measure | the limit is the headroom value, the best plus (a floor: minus) z_L se_test | `test_equal_baselines_set_the_limit_at_the_headroom` |
| a workload or supply measure missing | refused: every limit is set | `test_refuses_malformed_measures`, `test_every_limit_is_set` |
| the composite's caps and B\* | the null journeys' composites move with them; the do-nothing composite is 2/6 in the composite form | `test_the_null_journeys_and_the_floor` |
| no baseline ever paid within B\* by W | the limit is vacuous; the output names the long-run gate as the only guard | `test_a_vacuous_not_paid_limit_names_the_long_run_gate_alone` |
| a dollar dimension shifted by a constant for every unit | its caps shift by it; weights, composites and delta\* do not move | `test_a_shifted_dollar_dimension_shifts_its_caps_and_nothing_else` |
| a dimension made a monotone function of another | nothing is dropped; the six weights stand; rho is reported beside | `test_a_dimension_that_moves_with_another_is_kept_and_the_weights_stay` |
| every dimension but money constant | the form is the fallback, P_B alone | `test_every_other_dimension_constant_gives_the_fallback` |
| a baseline's units stop passing | its cost z is 0 on those units, whatever they spent | `test_cost_scores_an_unpassed_unit_at_zero` |
| the four baselines identical | every gap zero, none resolved; delta\* at its floor; ranking in the declared order | `test_identical_baselines_put_delta_star_at_its_floor` |
| a top gap of 2.5 standard errors, then of 1.9, at `H4_MIN_SEEDS` seeds | resolved, then not | `test_resolution_at_z_2_at_the_minimum_seed_count` |
| one seed fewer than `H4_MIN_SEEDS`, however large the gaps | none resolved; delta\* the fraction of the spread, within its bounds | `test_below_the_minimum_seed_count_no_gap_is_resolved_and_the_rule_falls_back` |
| every gap resolved and the smallest above `DELTA_MAX` | delta\* held at `DELTA_MAX` | `test_delta_star_is_held_at_its_declared_cap` |
| the declared J changed (a new rule id) | the headroom scales by 1 / sqrt(J), so a headroom-bound limit moves, and the power moves; the budgets, weights, composites and delta\* do not | `test_j_is_the_declared_constant_and_moves_only_the_headroom_and_the_power` |

## 8. Ties and degenerate inputs

- **Ties between baselines** (a composite, a limit's estimate) are broken in the order of `BASELINES`; a tied
  adjacent gap is zero and never resolved.
- **A budget quantile at or below one fee unit** gives one fee unit. Two quantiles on one lattice point give one
  budget (the list is the distinct values).
- **A dollar dimension with no spread** (q95 = q05 after clamping) takes caps one fee unit either side; a day
  dimension, its a priori range [0, W + 1]; cost with no passed unit, [0, one fee unit] with every z 0.
- **A dimension constant over every pooled unit** is kept with its weight, contributing a constant to every
  baseline; Spearman's rho with it is undefined and reported as none.
- **Every dimension but money constant:** the fallback (4.4).
- **No resolved gap and no spread:** delta\* = `DELTA_MIN`.
- **No coin noise** (sigma = 0): the power is 0 or 1 by the sign; sigma is capped at 1.
- **The power target unreachable by `J_MAX` seeds, or J_needed above `TEST_SEEDS`:** the forecast fails; the gate
  (H3-D) decides, and if it fails the search does not pin (CHARTER 3.7), with the result reported.

## 9. What the rule never does, and how it is applied

- **It never reads a held-out outcome.** Its readings are refused unless tagged `search` with every start day inside
  2020-01-02 to 2023-12-29, checked before anything else; the held-out years enter only through their pinned session
  calendar's dates, counted into complete starts (section 10), never as an outcome. H4's runner refuses held-out
  sessions on its own (CHARTER 3.6 (e)).
- **It is applied once, to H4's one output, by `scripts/wave42_apply.py`** (B-1, V-1):
  `python scripts/run_clean.py --name w42-r1 -- python scripts/wave42_apply.py`, from a clean checkout of a named
  commit, with no argument. The script reads the collection result and its sidecar from disk and hashes both,
  derives the calendars, the counts and the fee itself, builds the readings through the one adapter, refuses if any
  Wave 4.2 output exists, and writes `results/w42_r1_values.csv` once through `write_result`, every hash in its
  manifest (1.1's audit list). The pinning row cites that output's sha256, its `values_sha256` and its
  `input_sha256`, beside H4's collection result's and sidecar's sha256.
- **It never changes after H4 is read.** It is pinned by the sha256 of this file, of `extended/wave42.py` and of
  `scripts/wave42_apply.py` before
  H4's read; its outputs are computed once from H4's search-year results and pinned in CHARTER 3.9's one row before
  the survey, never after a held-out read (E-221). A changed constant is a new rule id under a new row before H4's
  read, or a re-declaration of the search.
- **It reads no result number typed anywhere.** Every value it outputs is computed from H4's result file by
  `setting_rule`, with every intermediate (the pooled quantiles, the caps, rho, the gaps and their standard errors,
  each limit's baseline estimates, per-year estimates and headroom) in its output, so each value traces.
- It draws no randomness, so it takes no seed.

### 9.1 The output file's row schema (`results/w42_r1_values.csv`)

The values are written as **one row per top-level key** of `setting_rule`'s output, in sorted key order, with two
columns: `key` (the name) and `value_json` (that value as JSON: keys sorted, separators `,` and `:`, every number
finite). `values_from_rows` reads the rows back into the values; their canonical JSON's sha256 is the manifest's
`values_sha256`. The file itself is bound by the sha256 its sidecar records. The rows:

<!-- wave42-output-rows:start -->
| key | JSON type | what it holds |
|---|---|---|
| application | object | the script, the output name and the applied-once rule |
| budgets | object | (24)'s budgets in fee units, the primary budget B\* (`primary`), their trace |
| composite | object | each baseline's composite (`value`) and their ranking |
| constants | object | section 2's table, as the module holds it |
| delta_star | object | delta\*, its gaps, its bounds and its translation into each dimension's units |
| dimensions | array | per dimension: name, horizon, direction, kind, caps `lo` and `hi`, weight, baseline means |
| form | string | `composite` or `fallback` (4.4) |
| h4 | object | H4's binding: the result, readings and calendar sha256, the counts, the arm and the verdict settings |
| held_out_read_ledger | object | this rule's own ledger entry, the held-out calendar and its sha256 |
| inactivity_guards | object | the two guards' state and the floor (4.5) |
| input_sha256 | string | the digest of every input |
| limits | object | per limit (`values`): its value, direction, statistic, horizon, the baselines' estimates and checks |
| null_journeys | object | the do-nothing and quitter composites, and the declared floor (`floor`, its `value`) |
| power | object | the power forecast at `TEST_SEEDS`, J_needed and the worst case |
| rho_beside | object | Spearman's rho between the dimensions, beside, deciding nothing |
| rule_id | string | `W42-R1` |
| search_starts | object | the start count of E_h per horizon |
| seeds | integer | H4's seed count |
| test_starts_source | object | the held-out calendar's file, sha256 and session count |
| weights | object | the weight of each kept dimension |
<!-- wave42-output-rows:end -->

### 9.2 The public scoring path (the survey's; C-1)

`setting_rule` scores every unit set through these functions of `extended/wave42.py`, and Wave 5's survey imports
**only these** to score a design, so one code path serves both; the tests hold that the rule's output passes through
each and moves with each. The pin covers them with the rest of the module.
- `pinned_inputs(values) -> {"B", "caps", "weights", "form", "floor", "limits"}`: what a design is scored with, from
  the output's values (`values_from_rows(rows)` parses the file's rows).
- `unit_values(values, B)`: a unit set's raw measures with `bankroll_states` at budget B.
- `unit_scores(values, B, caps) -> {dimension: z}`: every dimension's per-unit z in [0, 1], **B-5 included** (a unit
  not passed by W scores z = 0 on cost).
- `composite_per_seed(values, sessions_left, out) -> array`: the composite of the unit set `out` (its raw measures),
  one value per seed, scored with W42-R1's `values` (B\*, the caps, the weights); its mean is the point estimate.
- `null_journeys(fee_unit)` (its `["do_nothing"]` journey), `null_composites(values, fee_unit)` and
  `do_nothing_floor(values, fee_unit)`: the null journeys, their composites and the declared floor
  (`null_journeys.floor` in the output; 4.5).
- `limit_estimate(values, sessions_left, out, name) -> float`: a limit's point estimate for `out`, its statistic over
  the units of E_h pooled over seeds (one seed's column gives that seed's estimate); `limit_per_seed_sd(values,
  sessions_left, out, name)`; and `limit_check(values, sessions_left, out, name, value, level_=LIMIT_CHECK_LEVEL)`:
  **inside** by the point estimate, which decides (E-230), and the one-sided check of crossing beside it (B-10's form:
  beyond the value by more than z_(1 - level) coin-seed standard errors), never deciding.

`setting_rule` calls `composite_per_seed`, `null_composites` (so `null_journeys`), `limit_estimate`,
`limit_per_seed_sd` and `limit_check` on the part of its output it has built (B\*, the caps, the weights), the same
signatures the survey binds to (wt/wt-survey d5fe8f0).

## 10. The held-out read ledger

**W42-R1's own entry: the held-out session calendar's dates only** (E-211's form; V-2). The script reads
`results/q82_judged_sessions.csv` (sha256 `59a698623d951772c1ea19439200762026855eb696e859a544597041e0ffbdea`), its
`date` column only, to count the held-out complete starts per horizon; no price, outcome or other column is read. The
rule reads no held-out session, and refuses any reading not tagged `search` (1.5); its output carries the entry
(`held_out_read_ledger`).

**The prior reads that concern its comparators** (CHARTER 3.6 (b), the floor completed for the four baselines and
the constants this rule borrows). Its constants were chosen by a researcher who could have read these:
- Stage 2 D-626: P-14 fixed as R\* from the whole window.
- E-203 S-2: P-14's rung map and P-16's mark cutoff resolved on the whole window.
- Stage 2 D-554: P-16's stop chosen on each block.
- RD-04 (c): P-14 and P-16 replayed on the late block.
- RD-05: the late block read as late development.
- Q-17 and E-201: every user measure read beside the baselines, the bankroll limits of Q-17 among them (MEASURES
  section 7).
- Stage 2's signal search over the whole window.
- RD-03's whole-window lever readings.
- Stage 2's program U: every one of its nine families read P on the late block against P-14 (RD-02 records it).
- RD-02's late-block menu of payout policy.
- Any RD-01 late-block reads.
- Q-132 (E-211): every judged and whole-window row for P-14, P-15 and P-16 under its four rule sets.
- Q-16's paired nulls (E-211), computed on the held-out years.
- **Constants that land on a ledger constant** (MEASURES section 7, recorded as such): W = 126, the first-pass and
  first-payout window (Stage 2 D-518, D-620; Q-44), and the 252-session year window, both set with the held-out
  years visible; the 21-session month (CHARTER 2).

**The leak clause (RD-04's form):** this rule was **written after these readings; no figure from them is cited as
the reason for any constant**. Each constant's reason in section 2 is an arithmetic, a definition or a ruling, never
a reading. Because the ledger is not empty, the held-out test's level is **printed nominal** beside its verdict
(CHARTER 3.6 (b), E-203 S-2's form): for Stage 2's baselines "held out" means unread by this search only (E-208).

## 11. The choices on record for the pin

1. B\* at the pooled upper quartile of (24)'s per-unit spending, the naive coin included (n-3).
2. The fixed six dimensions with no drop, at equal weights (the lead's ruling): bankroll, cost and ruin together
   carry half the weight, and bankroll and ruin score a design that spends little as better; money, speed and steady
   score an inactive journey zero. The do-nothing floor and the two guards of 4.5 hold that.
3. Cost's unpassed units at z = 0 with caps from the passed units.
4. The fallback's trigger: every other dimension constant over the pooled units.
5. `TEST_SEEDS` = 1000, the lead's choice, with the worst case's need beside it.
6. `H4_MIN_SEEDS` = 62 at z = 2 (the false resolution counted two-sided), and `DELTA_MAX` = 0.05, the lead's choice.
7. The joint z over the limits set (Bonferroni).
8. The binding's two outside pieces: H4's collection result and adapter (H4's, to build), and Q-197's calendar
   sha256, filled in before the pin.
