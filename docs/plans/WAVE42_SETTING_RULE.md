# Wave 4.2's setting rule: the limits, the budgets, the weights and the size that matters (rule W42-R1)

**What this is.** E-221 makes four inputs of CHARTER 3.9's pinning row the lead's, "set from H4's search-year results
by a rule declared before H4 is read": the **limits**, the **bankroll budgets B** of measure (24), the **composite's
weights**, and O-3's **size that matters** delta\*. This file is that rule. It is mechanical: given H4's readings it
outputs each value, with no choice left. Its code is `extended/wave42.py`, `setting_rule`, a pure function (no file,
no bar, no result, no randomness); `tests/test_wave42_rule.py` holds the code to this text (the three tables below
are machine-read) and tests it on synthetic readings.

**Status.** A draft for the red team's cold read. The lead pins it by sha256 in one row before H4 is read. After that
it is not edited: a change is a new rule id under a new row, made before H4 is read, or a re-declaration of the
search (CHARTER 3.9).

**What it governs and what it does not.** It sets the four values above, the primary budget B\* that P under the
bankroll stop reads, the composite's dimension definitions and normalisers (CHARTER 3.9 pins them with the weights),
the composite-or-fallback choice, and the level of the one-sided check printed beside each limit (3.8 (a)). It does
not set the power target (it reads `family_stats.MDL_POWER`), the test's seed count J or the held-out start counts
(H3's declaration), the regimes, "most years", the finalist order, the gate's quantile, the no-harm margin or the L
values: those are the pinning row's other inputs.

---

## 1. The input, and what is refused

**The input** is one reading per baseline of CHARTER 2's Topstep set, exactly `naive_coin`, `p14`, `p15`, `p16`, each
run by H4 under the zero-edge convention's deciding reading (CHARTER 3.2; the martingale-outcome reading). A reading
carries:
- its block tag, which must be `search`;
- its start days (ISO dates, increasing), each with its sessions left in its block (MEASURES 1.1's `obs`), so that
  E_h is the starts with at least h sessions left;
- its coin seeds (at least two);
- for each per-unit measure below, the matrix x[s, c] over start days by seeds, in MEASURES.md's never-blank form.

The per-unit measures read (MEASURES.md's numbers and forms):

| key | measure | horizon | per-unit form |
|---|---|---|---|
| `net_month_1` .. `net_month_3` | (12) | 21 m | `rel_u[21 m]` |
| `peak_month_1` .. `peak_month_3` | section 2's stop | 21 m | the peak out-of-pocket through close 21 m |
| `spent_before_first_payout` | (6) / (24) | W | `spent_before(rel_u, k*_u)`, the censored lower bound at W + 1 when unpaid |
| `first_payout_days` | (5) | W | `first_payout_u`, or W + 1 |
| `cash_to_first_pass` | (2) | W | the all-units form, censored at W + 1 |
| `peak_oop_12_months` | (25) | 252 | `PeakOOP_u` |
| `share_months_positive` | (18) | 252 | the per-unit share |
| `orders_max`, `accounts_max` (optional) | (30) | W | the per-unit maximum over observed sessions |
| `taken_mean` (optional) | (37) | W | the per-unit mean of `taken_d` |

Beside the readings: the **fee unit** (the price of one evaluation purchase of the plan the baselines run, read from
the verified ledger through `extended/firm_terms.py`, with its ledger key as its named source; never typed here), and
the three-way test's declared **seed count J** and **count of complete held-out starts per horizon** (63, 126 and
252), both calendar arithmetic of H3's declaration (`three_way_arith`'s `complete_starts` on the pinned calendar).
Neither reads a held-out outcome.

**Refused before any value is computed** (`Wave42Refused`):
- a reading whose block tag is anything but `search` (a held-out, confirmation or untagged reading);
- any start day before 2020-01-02 or after 2023-12-29, the search years of E-208 (so every held-out day, from
  2024-01-02, and every confirmation-window day, from 2026-07-17);
- a baseline set other than the four, or readings not paired (the same start days, sessions left and seeds);
- fewer than two seeds; start days not increasing or sessions left not decreasing;
- a required measure missing, a matrix of the wrong shape, a blank (or non-finite) value on E_h (MEASURES 1.3's blank
  rule), or a value outside its a priori range (a share outside [0, 1], days outside [0, W + 1], a negative dollar
  spend);
- an optional measure given for some baselines and not others;
- a fee unit that is not a positive amount, or that names no source; a test start count missing for a horizon, or
  increasing in the horizon.

## 2. The constants

Every constant of the rule, its value and its reason. `tests/test_wave42_rule.py` reads this table and holds each
value equal to `extended/wave42.py`'s.

<!-- wave42-constants:start -->
| constant | value | reason |
|---|---|---|
| RULE_ID | `"W42-R1"` | this rule's id; a change is a new id under a new row |
| SEARCH_FIRST | `"2020-01-02"` | E-208's search years, first session |
| SEARCH_LAST | `"2023-12-29"` | E-208's search years, last session |
| BLOCK | `"search"` | the only block tag read (CHARTER 3.6 (e)) |
| BASELINES | `["naive_coin", "p14", "p15", "p16"]` | CHARTER 2's Topstep baseline set; the order breaks ties |
| W | `126` | the first-payout window of (2), (5), (6) and (24): U1's and Q-44's ledger constant, half a year |
| MONTH | `21` | CHARTER 2: a month is 21 sessions |
| AHEAD_TOL | `1e-06` | MEASURES 1.2 (m-11): ahead means above a millionth of a dollar |
| BUDGET_QUANTILES | `[0.5, 0.75, 0.9]` | the budgets of (24): a typical, a cautious and a deep bankroll among the baselines' users |
| PRIMARY_BUDGET_QUANTILE | `0.75` | B\*: below the median the stop decides most units and P_B reads spending alone; at the 90th percentile it barely binds and P_B is P; the upper quartile is between |
| CAP_QUANTILES | `[0.05, 0.95]` | a dollar or day dimension's normaliser spans the baselines' pooled units, robust to single extreme units |
| CAP_MARGIN | `0.25` | the span is widened by a quarter each side, so a design better than every baseline is not clipped at once; wider caps would dilute the test's power (the three-way note 1.3 and 2.2 (a)) |
| REDUNDANT_RHO | `0.9` | two dimensions whose units rank alike at Spearman's 0.9 or more carry one piece of information (MEASURES 3, m-4: a duplicated column inflates its dimension) |
| RESOLVE_Z | `2.0` | a gap between two baselines is resolved when it exceeds twice its coin-noise standard error, about a two-sided 95 % band |
| DELTA_FRACTION | `0.25` | when no gap is resolved: a quarter of the baselines' composite spread, one rank's share among four |
| DELTA_MIN | `0.01` | the floor of delta\*: one hundredth of the composite's [0, 1] range, below which no user would change design |
| POWER_TARGET | `0.8` | the power target, `family_stats.MDL_POWER` (the three-way note 4.1) |
| K_TEST | `13` | the held-out test's k (CHARTER 3.7: next 13); alpha = 0.05 / (k (k + 1)) |
| LIMIT_CHECK_LEVEL | `0.05` | the one-sided check of crossing printed beside each limit, never deciding (3.8 (a); E-230) |
| J_MAX | `10000000` | the search bound for the seed count that reaches the power target; beyond it, "not reachable" |
<!-- wave42-constants:end -->

## 3. The bankroll budgets B

1. Pool the per-unit spending before the first payout, `spent_before_first_payout`, over E_W of all four baselines,
   every seed (each baseline weighs equally: the readings are paired, so pooling is equal weighting). This is (24)'s
   own per-unit quantity (MEASURES (6), (24)): the budget is what (24)'s three states read.
2. For each q in `BUDGET_QUANTILES`, take the pooled q-quantile (numpy's linear rule, MEASURES 1.3) and round it **up
   to the fee lattice**: the smallest whole number of fee units at or above it, and at least one. Spending moves in
   fee purchases, so a budget between two lattice points buys nothing the lower point does not; rounding up keeps the
   budget at or above the reading.
3. The budgets are the distinct values in quantile order. **B\*** is the one at `PRIMARY_BUDGET_QUANTILE`. B\* is the
   budget of the composite's P_B and ruin dimensions and of the bankroll limit; every budget is reported in (24).
4. An unpaid unit's spending is a censored lower bound (MEASURES (6)), so a pooled quantile is a lower bound when it
   falls among censored units. The rule uses the never-blank value as it is and reports the share paid by W beside;
   rounding up to the lattice is the only allowance.

## 4. The composite

### 4.1 The dimensions (fixed here, in CHARTER 2's objective order)

CHARTER 2's objective names, in order: the least bankroll, the fastest and cheapest path to a pass and a payout, a
steady income, the lowest chance of going broke first. CHARTER 3.9 adds that one dimension is P under the bankroll
stop. P_B is first: it is the objective's own reading of "making money" and the pinned fallback. Each dimension is one
per-unit, never-blank measure, an **unconditional mean over its E_h** of a per-unit value with a priori bounds, so
the whole composite is admitted to the three-way note's Hoeffding/McDiarmid bound (2.2 (a)). The aliases MEASURES 3
lists are avoided: (6) is read only through (24), and (25) (the peak through twelve months) is not (24)'s before-payout
quantity.

<!-- wave42-dimensions:start -->
| name | objective term | measure | key | horizon | direction | kind | why this measure |
|---|---|---|---|---|---|---|---|
| money | making money (CHARTER 3.9) | (13) P_B | `P_B` | 63 | higher | share | months 1-3 ahead under B\*, over three, per unit (MEASURES 2) |
| bankroll | least bankroll | (25) | `peak_oop_12_months` | 252 | lower | dollars | the deepest the user's own money goes in twelve months |
| speed | fastest | (5) | `first_payout_days` | 126 | lower | days | sessions to the first payout, censored at W + 1 |
| cost | cheapest pass and payout | (2) | `cash_to_first_pass` | 126 | lower | dollars | cash to the first pass; the cash to the first payout is (24)'s |
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
- The clip is in the per-unit definition (the three-way note 2.2 (a), 2 (ii)): every z_d(u) lies in [0, 1] by
  construction, and the composite is a mean of bounded per-unit terms.

### 4.3 Redundancy, then the weights

1. Walk the dimensions in the order of 4.1. money is always kept. Each later dimension is compared with every kept
   one: Spearman's rho (average ranks) of their z over the pooled units of the common set E_max(h, h'), all four
   baselines, every seed. If rho >= `REDUNDANT_RHO` with any kept dimension, it is **dropped** as redundant with the
   first such one; otherwise it is kept. Only a positive rho counts: on z both are "higher is better", so a strong
   negative rho is a trade-off, not a duplicate.
2. The kept dimensions take **rank-order-centroid weights** in their order: w_i = (1/D) x (1/i + 1/(i+1) + ... + 1/D),
   D the number kept (Barron and Barrett 1996, the standard weights for a ranked list of criteria with no other
   information). They are non-negative and sum to one.
3. **What H4 decides here** is each dimension's normaliser (its caps, so the weight per dollar or per session,
   w_d / (hi_d - lo_d)) and which dimensions survive; the order is CHARTER 2's, declared now. The between-baseline
   spread of each dimension (the four baselines' mean z) is reported beside, deciding nothing.

### 4.4 The composite, or the fallback

- C(x) = sum over kept d of w_d x (the mean of z_d over the units of E_{h_d}). It lies in [0, 1].
- **The fallback** (CHARTER 3.9): if only money is kept, the form is `fallback`, P under the bankroll stop at B\*
  alone, weight one. The form is decided here, before the survey, and never after a look. The limits stand in both
  forms.

## 5. The size that matters, delta\*, and the power at it

### 5.1 delta\*

1. Each baseline's composite C_b, and per seed c, C_b(c) on that seed's units. Rank the baselines by C_b, highest
   first (ties in the order of `BASELINES`).
2. For each adjacent pair in the ranking, the gap g = mean over seeds of C_upper(c) - C_lower(c), and its standard
   error, the seeds' sample standard deviation over the square root of their number. The gap is **resolved** when
   g > `RESOLVE_Z` x se.
3. **delta\* = the smallest resolved adjacent gap**: among the plans a user can already run, it is the smallest
   difference known to change which of two a user should run (O-3). It is the smallest such difference, not the top
   pair's, so the power gate is held at the strictest resolved scale.
4. If no gap is resolved, delta\* = `DELTA_FRACTION` x (C_max - C_min).
5. delta\* is never below `DELTA_MIN`.

### 5.2 The planted finalist

As the three-way note 4.3 states: the best baseline plus delta\*, against all four. Against baseline b its true
difference is delta_b = delta\* + (C_best - C_b), so delta\* against the best and more against the others.

### 5.3 The power (the three-way note 2.2 (a) and 2.5)

- alpha = 0.05 / (k (k + 1)) at k = `K_TEST`; c_h = sqrt(2 ln(1 / alpha)).
- The test's units are J seeds by the declared complete held-out starts n_h per horizon; the E_h nest (E_252 within
  E_126 within E_63). With every per-unit z in [0, 1], McDiarmid's bounded differences give the half-width
  c_h sqrt(Q), with
  Q = (1 / J) x the sum over the nested strata of (the stratum's count) x (the sum over the kept d reaching it of
  w_d / n_{h_d})^2.
  On one horizon, Q = 1 / (J n), the note's own form.
- sigma_b, the per-unit coin noise of the pair's term: on the search years, on the common set of every kept
  dimension, the within-start-day variance across seeds of the per-unit composite difference (best minus b), averaged
  over start days, its square root; for the pair (planted, best) it is sqrt(2) x the best baseline's own within-day
  standard deviation (the disjoint-seed null's). Each is capped at 1, the bound for terms in [-1, 1].
- **Each pair's power** = Phi((delta_b / sqrt(Q) - c_h) / sigma_b) (2.5's normal approximation; sigma = 0 gives 0 or
  1). **The pass's power** (an intersection-union test: every pair must pass) is bounded below by
  max(0, 1 - the sum of the pairs' misses).
- **Reported:** each pair's power, the conjoint lower bound at the declared J, the same at sigma = 1 (2.5's bound),
  whether it meets `POWER_TARGET`, and **J_needed**, the smallest J up to `J_MAX` at which the conjoint lower bound
  reaches the target (none if not reachable). H3-D's simulation of the pinned rule decides the gate (CHARTER 3.7);
  this is its formula's forecast, deciding nothing on its own.

## 6. The limits

**The form in force** (CHARTER 3.8 (a); E-221, E-230): the point estimate governs; the one-sided check of crossing at
`LIMIT_CHECK_LEVEL` is printed beside, never deciding. Each limit is read on the pooled units (MEASURES 1.4, reading
1) of its E_h, by numpy's linear quantile.

<!-- wave42-limits:start -->
| name | measure | key | direction | horizon | stat | optional | what a user feels |
|---|---|---|---|---|---|---|---|
| not_paid_within_B | (24) | `not_paid_within_B` | ceiling | 126 | mean | no | the chance of not being paid within B\* by W (run out plus censored; MEASURES (24)'s limit reading) |
| peak_oop_12_months_p90 | (25) | `peak_oop_12_months` | ceiling | 252 | p90 | no | the bankroll the unlucky tenth puts in over a year |
| first_payout_days_p50 | (5) | `first_payout_days` | ceiling | 126 | p50 | no | the typical wait for the first cash |
| orders_max_p90 | (30) | `orders_max` | ceiling | 126 | p90 | yes | the busiest day's hand-entered orders |
| accounts_max_p90 | (30) | `accounts_max` | ceiling | 126 | p90 | yes | the most accounts live at once |
| taken_mean_p10 | (37) | `taken_mean` | floor | 126 | p10 | yes | the trades on offer a session (supply) |
<!-- wave42-limits:end -->

**The value of each limit.**
1. M_b, each baseline's point estimate; the **best** baseline (lowest for a ceiling, highest for a floor) and the
   **worst** (the other way), ties in the order of `BASELINES`.
2. The **headroom** E-015 requires (CHARTER 3.7, 3.8 (a): a design equal to the best baseline passes every limit
   with at least the power target): with se_test = the best baseline's per-seed statistic's standard deviation on the
   search years, times sqrt(|E_h search| / (J x n_h test)), the needed value is M_best + z_pi se_test for a ceiling
   (M_best - z_pi se_test for a floor), z_pi the normal quantile at `POWER_TARGET`.
3. **The limit is the worst baseline's estimate**, unless that is inside the needed value, in which case it is the
   needed value: a ceiling is max(M_worst, M_best + z_pi se_test), a floor min(M_worst, M_best - z_pi se_test). The
   principle: **a design may be no worse, on anything a user feels, than every plan already on offer** -- the limit
   is a guard rail at the edge of the known plans, not the objective; the composite ranks inside it. The worst
   baseline's reading also leaves room for the held-out history to differ from the search years', which the coin
   headroom of step 2 does not cover. Which of the two binds is reported (a tie is the worst baseline's).
4. A share limit at or beyond its range's end (a ceiling at 1, a floor at 0) is reported **vacuous**, and kept.
5. An optional limit whose measure no baseline's H4 reading carries is **not set**, reported with that reason; the
   pinning row then says so. A required one missing is refused (section 1).

**No limit on screen hours or trading hours:** the operator ruled no cap on trading hours, every session the firm
allows in the search (the restart plan, section 9, item 6). The verdict's settings (0 % denial, placement off, the
Focused Trader Program off) are the reading's, not limits.

## 7. How the outputs move with a baseline's reading (each row a test)

| a change to H4's readings | what moves | test |
|---|---|---|
| a baseline's spending before the first payout rises | every budget rises or stays, on the fee lattice | `test_more_spending_raises_the_budgets` |
| the worst baseline worsens on a limit's measure | that limit moves out to the new worst estimate | `test_a_worse_worst_baseline_moves_its_ceiling_and_a_better_best_does_not` |
| the best baseline improves, the worst unchanged | the limit does not move | same test |
| every baseline equal on a limit's measure | the limit is the headroom value, the best plus (a floor: minus) z_pi se_test | `test_equal_baselines_set_the_limit_at_the_headroom` |
| an optional measure absent from every baseline | its limit is not set | `test_an_absent_optional_measure_sets_no_limit` |
| a dollar dimension shifted by a constant for every unit | its caps shift by it; weights, composites and delta\* do not move | `test_a_shifted_dollar_dimension_shifts_its_caps_and_nothing_else` |
| a dimension made a monotone function of an earlier one | it is dropped as redundant; the weights are the ROC weights of the rest | `test_a_redundant_dimension_is_dropped_and_the_weights_reset` |
| every dimension redundant with money | the form is the fallback, P_B alone | `test_all_redundant_gives_the_fallback` |
| the four baselines identical | every gap zero, none resolved; delta\* at its floor; ranking in the declared order | `test_identical_baselines_put_delta_star_at_its_floor` |
| the gaps within their coin noise | delta\* is the fraction of the spread | `test_unresolved_gaps_use_the_fraction_of_the_spread` |
| the test's seed count J raised | the power rises; J_needed, the budgets, weights and delta\* do not move | `test_more_test_seeds_raise_the_power_and_leave_the_values` |

## 8. Ties and degenerate inputs

- **Ties between baselines** (a composite, a limit's estimate) are broken in the order of `BASELINES`; a tied
  adjacent gap is zero and never resolved.
- **A budget quantile at or below one fee unit** gives one fee unit. Two quantiles on one lattice point give one
  budget (the list is the distinct values).
- **A dollar dimension with no spread** (q95 = q05 after clamping) takes caps one fee unit either side; a day
  dimension, its a priori range [0, W + 1].
- **A dimension constant over every pooled unit** has no rank order: Spearman's rho is undefined and the dimension is
  not counted redundant (kept, contributing a constant).
- **All dimensions but money redundant:** the fallback (4.4).
- **No resolved gap and no spread:** delta\* = `DELTA_MIN`.
- **No coin noise** (sigma = 0): the power is 0 or 1 by the sign; sigma is capped at 1.
- **The power target unreachable by `J_MAX` seeds:** J_needed is reported as none; the gate (H3-D) then fails and the
  search does not pin (CHARTER 3.7), with the result reported.

## 9. What the rule never does

- **It never reads the held-out years.** Its readings are refused unless tagged `search` with every start day inside
  2020-01-02 to 2023-12-29; the held-out years enter only as declared counts of calendar starts and the test's J,
  never as an outcome. H4's runner refuses held-out sessions on its own (CHARTER 3.6 (e)).
- **It never changes after H4 is read.** It is pinned by sha256 before H4's read; its outputs are computed once from
  H4's search-year results and pinned in CHARTER 3.9's one row before the survey, never after a held-out read
  (E-221). A changed constant is a new rule id under a new row before H4's read, or a re-declaration of the search.
- **It reads no result number typed anywhere.** Every value it outputs is computed from H4's result files by
  `setting_rule`, with the input's sha256 and every intermediate (the pooled quantiles, the caps, rho, the gaps and
  their standard errors, each limit's baseline estimates and headroom) in its output, so each value traces.
- It draws no randomness, so it takes no seed.

## 10. Choices the red team should attack

1. B\* at the pooled upper quartile of (24)'s per-unit spending, against the best baseline's median or a fee
   multiple fixed in advance.
2. The fixed dimension set (4.1) in place of Wave 4.1's structure analysis: the rule takes 4.1's role only through
   the redundancy drop; 4.1's dimensions and trade-off curves are reported beside, deciding nothing. P_B ranked first.
3. ROC weights from the order alone, with H4 setting only the normalisers: the alternative, weights inversely
   proportional to each dimension's between-baseline spread, gives a dimension on which the baselines hardly differ
   the largest weight, so a design wins by a small move on it.
4. delta\* as the smallest resolved adjacent gap (the strictest), against the top pair's gap.
5. The limits at the worst baseline: a design worse than the best on one felt quantity but inside the worst passes
   that limit; the composite, not the limit, has to rank it.
6. sigma from the search years' coin noise, applied to the held-out years' counts (the per-unit coin noise assumed
   to carry across histories); the power at sigma = 1 is printed beside as the bound.
7. The union bound for the conjoint power (conservative when the pairs' passes are positively dependent).
