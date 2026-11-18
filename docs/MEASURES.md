# The journey measures: definitions (the restart plan's 39)

Wave 1.2 of `docs/plans/RESTART_PLAN_journey_objective.md` (section 3, lane `wt-user`). This file defines each of the
plan's 39 measures exactly, says which function computes it today and under which column or key its value is written,
or says "to build". **It holds definitions only: no value of any measure appears here.** Every value is in a result
file with its manifest. Nothing here is in force until the lead records it under a decision row. The red team reads it
in Wave 1.5, and the auditor re-derives every journey figure from it.

`tests/test_measures_doc.py` holds this file to the code. Every function, constant and column named in the index
(section 7) for a measure marked `exists` or `partial` must be defined in the named file. Every measure has a status,
and every `to build` entry is marked so. The test reads no data.

---

## 1. Conventions (every measure uses them)

**The unit.** A *unit* `u = (s, c)` is one user. `s` is a *start day*: one development session (NQ 2020-01-02 to
2026-07-16) taken as a fresh start, with a fresh bankroll and fresh accounts, and the design's trades replayed in
historical order (U1, Stage 2 D-620; `vendor/stage2/docs/USER_MILESTONES.md`). `c` is a *coin seed*: one sequence of
coin directions. A design whose directions are not coin-driven has one `c` (P-14 is A3-BRK30's breakout, with no coin).
The seeds are fixed in the search declaration before its run (CLAUDE.md; plan 4.5). They are never chosen here.

**The clock.** Day 0 is the purchase evening. Day `k` is the close of the `k`-th session. A *month* is 21 sessions,
and month `m` holds sessions `21(m-1)+1 .. 21m` (`extended/user_measures.py`, `month_of`). A unit is observed for
`obs_u = min(252, sessions left)` sessions.

**The money.** `rel_u[k]` = the cash at close `k` less the starting bankroll, which equals the payouts received by
close `k` less every fee paid by it. The bankroll never binds in the replay. `F_u[k]` is the cumulative fees paid by
close `k` (subscription, activation, reset), and `Pay_u[k]` is the cumulative payouts received, so
`rel_u = Pay_u - F_u`. A payout counts on the close its cash *arrives*: activation day + 1 + the account's relative
request day + the firm's payout lag (U1's `payout_arrivals`).

**Events.**
- `first_pass_u` is the first close on which a Combine passes.
- `first_payout_u` is the first close on which payout cash arrives.
- `be_u` is the first close `k >= 1` with `rel_u[k] >= -1e-6`. This is break-even, "at or above zero" to a millionth
  of a dollar.

An event after `obs_u` is not the unit's (it is blank). **Ahead** means strictly above zero (`rel > 0`). A net of
exactly zero is broken even but not ahead.

**Spent before an event.** `spent_before(rel, k) = max(0, -min_{0 <= j < k} rel[j])` is the deepest net below zero
over the closes *before* the event's close (`vendor/stage2/propedge/research/customer_journey.py`, `spent_before`).

**Eligibility.** A reading at horizon `h` sessions is read only on the units with `obs_u >= h`. That set is written
`E_h` below.

**Summaries.**
- Unless a measure says otherwise, a measure is a distribution over units, summarised by its **p10, p50 (the median)
  and p90**. These are numpy's linear percentiles of the finite values.
- For days to an event, an unreached unit counts as *beyond* the window, and a percentile that falls beyond the window
  is blank (`extended/user_measures.py`, `days_quantile`; Stage 2 D-518 (3)).
- A *share* is the mean of a 0/1 indicator over the eligible units.
- A *pooled ratio* is a sum over units divided by a sum over units.

**Over coin seeds (the two-layer rule).** For a coin-driven design, every measure is read in two ways:
1. **The headline.** The summary over the pooled units `(s, c)`, with every unit weighted equally.
2. **The seed spread.** The same statistic computed separately for each seed `c` over its start days, then that
   statistic's p10, p50 and p90 across the seeds. This is the user's payout variance (plan 4.5).

A share or P read on pooled units equals the mean of the per-seed values when every seed has the same eligible start
days. **The coin layer is to build** (the seed-paired runner, plan Wave 3.2 `wt-verify`, wired in by Wave 3.1). Every
existing function below computes a measure over start days for one sequence. P-15 and P-16's replays use U1's
registered coin (`vendor/stage2/propedge/research/user_journey.py`, `COIN_SEED`).

**Blocks.** The existing files read two blocks: `all` (every start with the horizon left) and `judged` (the starts from
2024, Stage 2 D-621 (4)(b)). `extended/user_readings.py` also knows `early` and `late`. Under the restart plan the
blocks become the **search years** and the **held-out years**. The search declaration sets them (plan Wave 5), never
this file.

**Arm and firm response.** The existing files carry U1's two arms (`verdict`, `point`) and the responses of Q-17
(`extended/user_beside.py`, `RESPONSES`). A verdict is read with every response off (0 % payout denial, placement off;
plan 4.7, E-008 (2)), and the ladder is reported beside it. The arm a search reads is its declaration's.

**Where values are written (the keys used below).**

| key | file | how a value is named |
|---|---|---|
| [B] | `results/user_beside.csv` (Q-44, E-201) | `section` / `measure` / `stat` |
| [BS] | `results/user_beside_starts.csv` (Q-44, E-201) | one row a design, arm, response and start; the column named |
| [U1] | `vendor/stage2/results/user_journey.csv` (Stage 2 D-620) | sections `metric` / `month`: the `key` column, `group:measure@days`; section `start`: the column named |
| [SP] | `results/user_spend.csv` (Q-86) | **not yet written**: `scripts/user_spend.py` writes it from a clean run only; the column named |

[U1] holds the `off` reading only (0 %, placement off), on U1's nine configurations. [B] and [BS] hold every response
of Q-17 on P-14, P-15 and P-16.

---

## 2. P (not a p-value)

**P is not a p-value.** It is a share of users, not a probability of a test statistic. It was Stage 2's primary
measure (D-621 (1)), and it is the composite's P dimension under the bankroll stop (plan 4.8).

**Definition.** Take the units with 63 sessions observed and all three month-end nets finite (`E_63`, n units). Then

    P = ( sum over u in E_63 of  sum over m in {1, 2, 3} of  1[ rel_u[21 m] > 0 ] ) / (3 n)

That is, P is the mean over months 1, 2 and 3 of the share of units *ahead* (net strictly above zero) at that month's
end, all three shares taken on the same units. It is an exact ratio of counts in [0, 1], so two designs tie exactly
or not at all. Per unit, the count `months_ahead_u` ranges from 0 to 3.

**P under the bankroll stop, `P_B`.** This is the same ratio, except that a unit counts as ahead at month `m` only if
the cash it spent before its first payout is at most `B`: `spent_before(rel_u, first_payout_u) <= B`. A user who
reaches the budget before a payout quits and keeps no payout. This is the replay's own path, not a re-run with a
wallet. `B` is **the operator's bankroll budget, set in Wave 4** (plan 4.2, 9.3). The existing readings at $2,000 and
$2,500 are Q-17's own limits (`extended/user_readings.py`, `BANKROLL_LIMITS`), not the operator's.

**Where.**
- Functions: `extended/user_measures.py`, `p_by_month` (P and `P_B`) and `months_ahead`;
  `vendor/stage2/propedge/research/u_select.py`, `scorecard`, `p_of` and `months_ahead`.
- [B]: `scorecard/P/value`; `extra/P/value` (held equal to the card's by a refusing check);
  `extra/share_ahead_month_{1,2,3}/value`; `extra/P_bankroll_2000/value`; `extra/P_bankroll_2500/value`.
- [BS]: `months_ahead`.
- [U1]: `periodic:share_positive@21`, `@42` and `@63`, each on its own eligible starts
  (`u_select.p_from_u1`). This mean can differ from the card's P, which reads the three on `E_63`.

**The coin layer.** Pooled units give the headline. The per-seed P's p10, p50 and p90 give the spread (section 1).

**Its row to beat.** R\* = P-14 (CHARTER; E-008), on the designs P-14, P-15 and P-16 (`u_select.ROWS_TO_BEAT`).

---

## 3. The groups (the plan's section 3)

| group | measures | what it answers |
|---|---|---|
| Getting funded | (1)-(4) | how long, how much and how many evaluations to a first pass |
| First payout | (5)-(8) | how long and how much to the first cash, and its size |
| ROI | (9)-(15) | when the user is back to zero, whether they stay there, how much they are ahead, the money back per dollar |
| Steady income and payout variance | (16)-(23) | whether the income is even across months or one lump |
| Bankroll and downside | (24)-(27) | the bankroll needed, the chance of running out, the unlucky tail |
| Realism and robustness | (28)-(34) | the same journey with missed signals, worse fills, the workload, account lifetimes, bad years, firm denial, luck |
| Baselines | (35)-(36) | the rows every design is compared with |
| Supply and speed | (37)-(39) | how many trades are on offer, in which sessions, and how long the user waits between them |

The plan expects Wave 4's measure-structure analysis (4.1, on the search years only) to reduce the 39 measures to
about five or six dimensions: speed, cost and bankroll, steadiness, downside, supply and workload. **That reduction is
not made here.** The groups above are the plan's headings, not the composite's dimensions.

---

## 4. The measures

Every entry gives: the definition, the summary and unit, the status (`exists`, `partial` or `to build`), where it is
computed and written, and the parameters with who sets them.

### Getting funded

### (1) Sessions to the first evaluation pass
- **Definition:** `first_pass_u`, the first close on which a Combine passes (U1's `start_record`, `pass_days[0]`).
  Blank if no Combine passes within `obs_u`.
- **Summary and unit:**
  - Read over `E_W`: p10, p50 and p90 by `days_quantile` (an unreached unit is beyond; a percentile beyond `W` is
    blank).
  - Beside: the share passed by `W`.
  - Unit: sessions.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `days_quantile`; `extended/user_readings.py`, `path_rows`.
  - [B]: `path/first_pass_days/p10`, `p50`, `p90`, `share_by_126`.
  - [BS]: `first_pass`.
  - [U1]: `first_pass:days_p50@42`, `first_pass:days_p90@42` (U1's window is 42).
- **Parameters:** window `W`. Q-44's readings use `W = 126` (`extended/user_readings.py`, `FIRST_WINDOW`). A search
  may declare another `W` in its declaration.

### (2) Cash to the first pass
- **Definition:** `spent_before(rel_u, first_pass_u)`, the deepest net below zero over the closes before the pass
  close. No payout can arrive before a first pass, so this equals the fees paid through close `first_pass_u - 1`.
  Beside: `fees_at_first_pass_u = F_u[first_pass_u]`, which also counts the fees booked on the pass close itself
  (Q-86).
- **Summary and unit:**
  - p10, p50 and p90 over the units of `E_W` that pass by `W`.
  - Beside: the share never passing by `W`.
  - Unit: dollars.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_readings.py`, `path_rows`; `vendor/stage2/propedge/research/user_journey.py`,
    `start_record`.
  - [B]: `path/spent_before_first_pass/p10`, `p50`, `p90`.
  - [BS]: `spent_before_first_pass`.
  - [U1]: `first_pass:spent_before_p50@42`, `p90@42`, `p95@42` (Stage 2's S2, its cash half at p90).
  - The fees reading: `extended/user_spend.py`, `spend_record`, written to [SP] `fees_at_first_pass`.
- **Parameters:** window `W`, as in (1).

### (3) Evaluations bought before the first pass
- **Definition:** the number of Combines whose purchase day is before `first_pass_u`. A purchase happens at a close's
  end, so a Combine bought on the pass close is bought after the pass. Resets of a failed Combine are counted apart
  (`resets_before_first_pass`).
- **Summary and unit:**
  - p10, p50 and p90 over the units of `E_W` that pass by `W`.
  - Beside: the share never passing by `W`.
  - Unit: evaluations (a count).
- **Status:** exists (in code; its file is not yet written)
- **Where:**
  - Functions: `extended/user_spend.py`, `spend_record` and `SUMMARY_MEASURES`.
  - [SP]: `evaluations_before_first_pass` and `resets_before_first_pass`, summary measure
    `evaluations_before_first_pass`. Q-86's summary also writes p25, p75, the spread and `share_never`.
- **Parameters:** window `W`, as in (1).

### (4) Share of starts passed by session 21
- **Definition:** over `E_21`, the share with `first_pass_u <= 21`.
- **Summary and unit:** one share (pooled; with the seed spread for a coin design).
- **Status:** exists. The plan lists it as "new", but U1 already reads it.
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `stats` (`first_pass:share_by` at `PASS_DAYS`).
  - [U1]: `first_pass:share_by@21` (also `@5`, `@10`, `@42`).
  - It is not in [B]. It derives from [BS] `first_pass` and `observed`.
- **Parameters:** none. Session 21 is the plan's.

### First payout

### (5) Sessions to the first payout (S3b)
- **Definition:** `first_payout_u`, the close on which the first payout's cash arrives (U1's `payout_arrivals`).
- **Summary and unit:**
  - Read over `E_W`: p10, p50 and p90 by `days_quantile`.
  - Beside: the share paid by `W`.
  - **S3b is the p90.**
  - Unit: sessions.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_readings.py`, `path_rows`; `vendor/stage2/propedge/research/u_select.py`, `scorecard`.
  - [B]: `path/first_payout_days/p10`, `p50`, `p90`, `share_by_126`; `scorecard/S3b/value`.
  - [BS]: `first_payout`.
  - [U1]: `first_payout:days_p50@126`, `days_p90@126`, `days_p95@126`.
- **Parameters:** window `W` (Q-44 and U1: 126, `FIRST_WINDOW`), as in (1).

### (6) Cash spent before the first payout: the bankroll needed (S1)
- **Definition:** `spent_before(rel_u, first_payout_u)`, the deepest net below zero over the closes before the first
  cash arrives.
- **Summary and unit:**
  - p10, p50 and p90 over the units of `E_W` paid by `W`.
  - **S1 is the p90.**
  - Units not paid by `W` are left out here. They are what (24) counts.
  - Unit: dollars.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_readings.py`, `path_rows`; `vendor/stage2/propedge/research/user_journey.py`,
    `start_record`.
  - [B]: `path/spent_before_first_payout/p10`, `p50`, `p90`; `scorecard/S1/value`.
  - [BS]: `spent_before_first_payout`.
  - [U1]: `first_payout:spent_before_p50@126`, `p90@126`, `p95@126`.
- **Parameters:** window `W`, as in (5).

### (7) The first payout's size (S3d)
- **Definition:** `first_payout_cash_u`, the cash of the first arrival in U1's order (arrival close, then account,
  then request). When two payouts arrive on the same close, only the first in that order counts.
- **Summary and unit:**
  - p10, p50 and p90 over the units of `E_W` paid by `W`.
  - **S3d is the p50.**
  - Unit: dollars.
- **Status:** exists
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `start_record` and `metric_rows`.
  - [U1]: `first_payout:cash_p10@126`, `cash_p50@126`, `cash_p90@126`; start rows `first_payout_cash`.
  - It is not in [B] or [BS].
- **Parameters:** window `W` (U1: 126).

### (8) Share of starts paid by session 21 (S3a)
- **Definition:** over `E_21`, the share with `first_payout_u <= 21`.
- **Summary and unit:** one share (pooled; with the seed spread).
- **Status:** exists
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `stats`; `u_select.py`, `scorecard`.
  - [B]: `scorecard/S3a/value`.
  - [U1]: `first_payout:share_by@21` (also `@30`, `@42`, `@63`, `@90`, `@126`).
- **Parameters:** none.

### ROI

### (9) Sessions to break-even
- **Definition:** `be_u = min{k >= 1 : rel_u[k] >= -1e-6}`, read at daily resolution from the replay's own
  close-by-close cash.
- **Summary and unit:**
  - Over `E_252`: p10, p50 and p90 by `days_quantile`, window 252.
  - Beside: the share broken even by 252, and the share broken even by month `m` on `E_{21m}`, for m = 1, 2, 3, 6
    and 12.
  - Unit: sessions.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `break_even_day`; `extended/user_readings.py`, `path_rows`.
  - [B]: `path/break_even_days/p10`, `p50`, `p90`, `share_by_252`; `path/break_even/share_by_month_{1,2,3,6,12}`.
  - [BS]: `break_even_day`.
  - [SP]: `break_even_day`, summary `sessions_to_break_even`.
- **Parameters:** window 252 (`extended/user_readings.py`, `YEAR_WINDOW`), or the declaration's.

### (10) Share falling back below break-even
- **Definition:** among the units of `E_252` with `be_u <= 252`, the share with some later close `k > be_u` where
  `rel_u[k] < -1e-6`.
- **Summary and unit:** one share.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `fell_back`; `extended/user_readings.py`, `path_rows`.
  - [B]: `path/break_even/share_fell_back`.
  - [BS]: `fell_back`.
  - [SP]: `break_even_lost`.
- **Parameters:** window 252, as in (9).

### (11) Deepest fall after break-even
- **Definition:** `max over k >= be_u of ( max_{be_u <= j <= k} rel_u[j] - rel_u[k] )`, the deepest fall of the
  cumulative net from its running high, counted from the break-even close on.
- **Summary and unit:** p10, p50 and p90 over the units of `E_252` broken even. Unit: dollars.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `deepest_fall_after`; `extended/user_readings.py`, `path_rows`.
  - [B]: `path/deepest_fall_after_break_even/p10`, `p50`, `p90`.
  - [BS]: `deepest_fall_after_break_even`.
- **Parameters:** window 252, as in (9).

### (12) Net cash at months 1, 2, 3, 6 and 12
- **Definition:** `rel_u[21 m]` for m = 1, 2, 3, 6 and 12.
- **Summary and unit:** p10, p50 and p90 over `E_{21m}` at each month. Unit: dollars.
- **Status:** exists
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`.
  - [U1]: `periodic:net_p10@{21,42,63,126,252}`, `periodic:net_p50@...` and `periodic:net_p90@...` (also p5, p25,
    p75 and month 9).
  - [BS]: `net_month_1`, `net_month_2`, `net_month_3`, `net_month_6`, `net_month_12`.
  - [B] writes only the means at months 1 to 3: `extra/mean_net_month_{1,2,3}/value`. The percentiles under a firm
    response other than `off` derive from [BS].
- **Parameters:** none.

### (13) P, and the shares ahead at months 6 and 12 (S4a, S4b)
- **Definition:**
  - P is defined in section 2.
  - **S4a** = the share of `E_126` with `rel_u[126] > 0`.
  - **S4b** = the share of `E_252` with `rel_u[252] > 0`.
- **Summary and unit:** shares (pooled; with the seed spread).
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `p_by_month`; `vendor/stage2/propedge/research/u_select.py`,
    `scorecard`.
  - [B]: `scorecard/P/value`, `scorecard/S4a/value`, `scorecard/S4b/value`.
  - [U1]: `periodic:share_positive@126` and `@252`.
- **Parameters:** for `P_B`, the operator's budgets `B` (Wave 4).

### (14) Payouts per fee dollar (S3c)
- **Definition:** the pooled ratio at month 3:
  `sum over u in E_63 of Pay_u[63]` divided by `sum over u in E_63 of F_u[63]`, where `Pay = net + fees`. It is blank
  when the fees sum to zero.
- **Summary and unit:**
  - One pooled ratio, not a distribution. The pooled units carry the coin layer.
  - Beside: U1's median of the per-unit ratio over units with fees above zero.
  - U1 also reads it at months 1, 6 and 12.
  - Unit: dollars of payouts per dollar of fees.
- **Status:** exists
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`.
  - [U1]: `money_back:payouts_per_fee_dollar_pooled@63` (and `@21`, `@126`, `@252`);
    `money_back:payouts_per_fee_dollar_median@63`.
  - [B]: `scorecard/S3c/value`.
  - The per-unit fees: [U1] start rows `fees_month_k`; [SP] `fees_month_m` and `payouts_month_m`.
  - E-201 D1 applies: under any response other than `off`, [B]'s S3c cannot be re-derived from the files (Q-139).
- **Parameters:** none.

### (15) Return on money at risk
- **Definition:** `ROMR_u = rel_u[252] / PeakOOP_u`, where `PeakOOP_u` is (25)'s peak out-of-pocket over the same 12
  months. It is blank when `PeakOOP_u = 0`.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: a ratio (dollars of 12-month net per dollar of peak
  out-of-pocket).
- **Status:** to build
- **Where:** nothing computes it.
  - Ingredients: `extended/user_spend.py`, `spend_record`.
  - Its `return_on_spend_month_m` is a *different* ratio: net over the fees paid, months 1 to 6.
- **Parameters:** none.

### Steady income and payout variance

### (16) Monthly net in months 4-12
- **Definition:** per unit, the mean monthly net change over months 4 to 12:
  `( rel_u[252] - rel_u[63] ) / 9`.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: dollars per month.
- **Status:** to build
- **Where:** no function computes it.
  - Ingredients: [BS] `net_month_3` and `net_month_12`; [U1] start rows `net_month_4` to `net_month_12` for the
    month-by-month view.
- **Parameters:** none.

### (17) Payouts per month
- **Definition:** per unit, the number of payout arrivals in months 1 to 12 divided by 12, and their cash divided by 12.
  A payout belongs to the month its cash arrives in.
- **Summary and unit:**
  - p10, p50 and p90 over `E_252`, with the mean beside.
  - Unit: payouts per month, and dollars per month.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `evenness`; `extended/user_readings.py`, `path_rows`.
  - [B]: `path/payouts_per_month/{p10,p50,p90,mean}` and `path/payout_cash_per_month/{p10,p50,p90,mean}`.
  - [BS]: `payouts_per_month`, `payout_cash_per_month`.
- **Parameters:** none.

### (18) Share of months with a positive net change
- **Definition:**
  - `D_m = rel_u[21m] - rel_u[21(m-1)]` for m = 2 to 12.
  - `D_1 = rel_u[21]`, measured from zero, so day 0's purchase fees fall in month 1.
  - The measure is the share of m in 1 to 12 with `D_m > 0`.
- **Summary and unit:** p10, p50 and p90 over `E_252`, with the mean beside. Unit: a share.
- **Status:** exists
- **Where:**
  - Function: `extended/user_measures.py`, `evenness`.
  - [B]: `path/share_months_positive/{p10,p50,p90,mean}`.
  - [BS]: `share_months_positive`.
- **Parameters:** none.

### (19) Spread of monthly net
- **Definition:** the sample standard deviation (ddof 1) of a unit's twelve monthly changes `D_1 .. D_12` (as in
  (18)).
- **Summary and unit:**
  - p10, p50 and p90 over `E_252`.
  - Beside, Stage 2's form: each unit's mean of the `D_m` over their standard deviation.
  - Unit: dollars.
- **Status:** exists
- **Where:**
  - Function: `extended/user_measures.py`, `evenness`.
  - [B]: `path/sd_monthly_net/p10`, `p50`, `p90`.
  - [BS]: `sd_monthly_net`.
  - [U1]: `luck:monthly_mean_over_sd_p10@252`, `p50@252`, `p90@252`.
- **Parameters:** none.

### (20) Longest run of months without a payout
- **Definition:** the longest run of consecutive months, among months 1 to 12, in which no payout cash arrives. The
  months before the first payout count.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: months.
- **Status:** exists
- **Where:**
  - Function: `extended/user_measures.py`, `evenness`.
  - [B]: `path/longest_months_without_payout/p10`, `p50`, `p90`.
  - [BS]: `longest_months_without_payout`.
- **Parameters:** none.

### (21) Longest gap between payouts within 126 sessions (S5b)
- **Definition:** take the arrival closes `a_1 <= ... <= a_r` at or before 126. The measure is the largest difference
  between consecutive marks of `(a_1, ..., a_r, 126)` (`payout_rhythm`). It counts from the first payout on, and it
  includes the stretch from the last payout to session 126. A unit with no payout by 126 has no gap and is left out.
- **Summary and unit:**
  - Over the units of `E_126` paid by 126: p50, p90 and the longest.
  - **S5b is the p90.**
  - The p10 is not written in [U1]; `payout_rhythm` gives it.
  - Unit: sessions.
- **Status:** exists
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `payout_rhythm` and `metric_rows`.
  - [U1]: `consistency:longest_gap_p50@126`, `longest_gap_p90@126`, `longest_gap_longest@126` (and `@252`).
  - [B]: `scorecard/S5b/value`.
  - E-201 D1 applies, as in (14).
- **Parameters:** none.

### (22) Best quarter's share of month-6 net (S5c)
- **Definition:** over the units of `E_126`, with `x_u = rel_u[126]`: the sum of the `ceil(n/4)` largest `x_u`
  divided by the sum of all `x_u`. It is blank when that total is not above zero.
- **Summary and unit:**
  - One number a design, taken across units, not per unit. The pooled units carry the coin layer.
  - Unit: a ratio.
  - It is ill-conditioned when the total is near zero (E-201's caveat).
- **Status:** exists
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `concentration`.
  - [U1]: `consistency:concentration@126` (and `@63`, `@252`).
  - [B]: `scorecard/S5c/value`.
- **Parameters:** none.

### (23) Largest month's share of the year's payouts
- **Definition:** `max_m cash_m / sum_m cash_m` over months 1 to 12, where `cash_m` is the payout cash arriving in
  month `m`. It is blank when no payout arrives in the year. This is the lump-sum detector of E-014.
- **Summary and unit:** p10, p50 and p90 over the units of `E_252` paid within the twelve months. Unit: a share.
- **Status:** exists
- **Where:**
  - Function: `extended/user_measures.py`, `evenness`.
  - [B]: `path/largest_month_share/p10`, `p50`, `p90`.
  - [BS]: `largest_month_share`.
- **Parameters:** none.

### Bankroll and downside

### (24) Chance of running out before the first payout (the bankroll stop)
- **Definition:** for a budget `B` and a window `W`:

      ruin_u(B) = 1[ spent_before(rel_u, k*_u) > B ]

  - `k*_u = first_payout_u` if the unit is paid by `W`.
  - Otherwise `k*_u = W + 1`, so every close 0 .. `W` counts.
  - Before the stop, the user's path is the replay's own path, so the indicator is exact on the replay.
  - A user who can pay exactly `B` has not run out.
- **Summary and unit:** for each `B`, the share of `E_W` with `ruin_u(B) = 1` (pooled; with the seed spread). Unit:
  a share.
- **Status:** to build
- **Where:** no function computes it.
  - Ingredients: `extended/user_measures.py`, `share_over_limit`, written to [B] `extra/share_spent_over_2000` and
    `share_spent_over_2500`. Those count only the units *with* a first payout, so they leave out the unpaid units,
    which are the ones most likely to run out. They are not this measure.
  - Also: `extended/user_measures.py`, `p_by_month` (P under the stop).
- **Parameters:**
  - `B`: **the operator's bankroll budgets, set in Wave 4** (plan 4.2, 9.3).
  - `W`: the search declaration's. The existing first-payout window is 126 (`FIRST_WINDOW`).

### (25) Peak out-of-pocket in 12 months
- **Definition:** `PeakOOP_u = max(0, -min_{0 <= k <= 252} rel_u[k])`, the deepest the user's own money goes below the
  start over the twelve months. This is Stage 2's `drawdown_from_start` over closes 0 .. 252.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: dollars.
- **Status:** to build. The function exists in the vendored tree. No reading or column uses it for the journey.
- **Where:**
  - Ingredient: `vendor/stage2/propedge/research/customer_journey.py`, `drawdown_from_start`.
  - [SP] `spent_before_break_even` is a different quantity: the peak *before break-even* only.
- **Parameters:** none.

### (26) Month-3 net of the unlucky tenth (S5a)
- **Definition:** the p10 of `rel_u[63]` over `E_63`.
- **Summary and unit:** one percentile. Unit: dollars.
- **Status:** exists
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`; `u_select.py`, `scorecard`.
  - [U1]: `periodic:net_p10@63`.
  - [B]: `scorecard/S5a/value`.
  - [BS]: `net_month_3`.
- **Parameters:** none.

### (27) CVaR10
- **Definition:** the mean of the worst `ceil(0.10 n)` finite month-3 nets `rel_u[63]`, taken over the units of
  `E_63` holding all three month-end nets.
- **Summary and unit:** one number. Unit: dollars.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `cvar`; `extended/user_readings.py`, `extra_rows`.
  - [B]: `extra/cvar10_net_month_3/value`.
- **Parameters:** the tail share 0.10 is the plan's ("CVaR10").

### Realism and robustness

### (28) Headline measures with 10 % and 20 % of signals missed or late
- **Definition:** two stress arms, each at `q = 0.10` and `q = 0.20`, run against the base design and paired on the
  same units:
  - **Missed:** each signal the design's schedule offers is independently not taken, with probability `q`, and the
    rest of the path is re-simulated.
  - **Late:** each signal is independently entered late by the delay `d`, with probability `q`, and re-priced from
    the bars at the late entry.
  - The draws come from a declared seed stream per unit. They are common random numbers across the designs compared.
  - The arm reports the headline measures beside the base.
- **Summary and unit:** each headline measure in its own summary and unit, for each arm and `q`.
- **Status:** to build. It needs `feature-rules` for the late arm, which reads bars.
- **Where:** nothing computes it.
- **Parameters:**
  - `q` = 10 % and 20 %: the plan's (the operator's, section 3).
  - The delay `d`, the seed stream and the set of headline measures: the search declaration (Wave 5), with the
    headline set taken from Wave 4's dimensions.

### (29) Headline measures at one and two ticks of worse fills
- **Definition:** every fill made one tick, then two ticks, worse than the base design's, with the headline measures
  reported for each. Which fills move (entry, stop, target, time exit) is Q-148's declaration.
- **Summary and unit:** each headline measure in its own summary and unit, at +1 and +2 ticks.
- **Status:** to build. This is Q-148 in `wt-verify` (approved item 2; plan Wave 3.2). Stage 2's precedent is
  `p16_slip_stress.csv` (D-583 to D-585).
- **Where:** nothing in this repository computes it on the journey.
- **Parameters:** the fills affected and the headline set: Q-148's declaration and Wave 4.

### (30) Workload: orders a day, accounts at once, screen hours
- **Definition:** for each session `d` of a unit:
  - `orders_d` is the number of trades entered across all accounts. One entry ticket counts as one order, with its
    attached bracket.
  - `accounts_d` is the number of accounts live at close `d` (a Combine trading or a funded account open).
  - `screen_d` is the hours covered by the union, over the session's trades, of [alert time, exit time]. The alert
    time is entry less the alert-to-order lead.
- **Summary and unit:**
  - Per unit: the mean and the maximum of each quantity over its observed sessions.
  - Then p10, p50 and p90 over `E_h`.
  - Units: orders per session, accounts, and hours per session.
- **Status:** to build
- **Where:** nothing computes it.
  - Ingredient: `extended/replay_records.py`, `ReplayRecorder` (each trade's account, place and booking on the
    replay).
- **Parameters:**
  - The alert-to-order lead: the design rules (plan 4b, the operator: at least five minutes).
  - The horizon `h`: the declaration's.
  - Workload is reported, never a limit on hours (plan 4b).

### (31) Funded-account lifetime: payouts per funded account before it is lost
- **Definition:** for each funded account activated within a unit's observed window, the number of its payouts whose
  cash arrived before the account ended.
  - An account that ends by a firm rule (lost) is complete.
  - An account still open at the window's end is censored.
- **Summary and unit:**
  - p10, p50 and p90 over the lost funded accounts, pooled across units, every account weighted equally.
  - Beside: the share of accounts still open at the window's end, and the sessions each account lived.
  - Unit: payouts per account.
- **Status:** to build
- **Where:** nothing computes it.
  - Ingredients: the engine's funded records (`payout_days`, `ended_on`, `n_payouts`), as read in
    `extended/user_beside.py`, `response_record`; `extended/replay_records.py`, `ReplayRecorder` (its accounts
    frame).
- **Parameters:** the window: the declaration's.

### (32) Worst year and highest-volatility period
- **Definition:** each headline measure is read on two kinds of subset:
  - The units whose start date falls in calendar year `y`, for each start year `y` of the search years, each subset
    taken within `E_h`. The reading reports the worst value in the measure's bad direction, and its year.
  - The units whose start day falls in the declared highest-volatility period.
- **Summary and unit:** each headline measure in its own summary and unit, on each subset.
- **Status:** to build
- **Where:** nothing computes it on the journey.
  - Ingredients: `vendor/stage2/propedge/research/u_select.py`, `START_YEARS` (and its `year_rule`); [U1]
    `luck:share_paid_by@21[year]` (S3a by start year).
  - The volatility descriptors are RD-04's (`extended/vol_descriptive.py`).
- **Parameters:** the volatility measure and its period (RD-04 and the search declaration), the search years (Wave 5)
  and the headline set (Wave 4).

### (33) Break-even denial rate
- **Definition:**
  - Under the engine's tier-3 denial model at enforcement probability `p` (`ConductModel(enforcement_p = p)`,
    `extended/user_beside.py`, responses of kind `denial`), let `M(p)` be the pooled mean over `E_252` of the
    12-month net `rel_u[252]`.
  - The start seeds are common random numbers across `p` (`user_beside.start_seed`).
  - `p*` is the smallest `p` in the grid with `M(p) <= 0`. It is refined by linear interpolation between the two grid
    points around the change of sign.
  - If `M(p)` stays above zero across the grid, `p*` is reported as "none in the grid".
- **Summary and unit:** one probability a design. It is **reported, never a limit** (plan section 3).
- **Status:** to build. The ladder it reads exists.
- **Where:**
  - Ingredients: `extended/user_beside.py`, `RESPONSES` and `DENIAL_LEVELS` (the existing ladder: 10 %, 25 % and
    50 %, plus the all-accounts forfeiture arms).
  - [B] and [BS] at `response` = `denial_10`, `denial_25`, `denial_50`.
  - The engine exposes a payout only under its stacking pattern, so a design that never shows the pattern has a flat
    `M(p)`.
- **Parameters:** the grid of `p` and the money measure: the search declaration. The verdict stays at 0 % (plan 4.7).

### (34) Luck against design (S6)
- **Definition (Stage 2's, D-620):**
  - The standard deviation of the net across units at months 1, 3, 6 and 12.
  - The standard deviation of the designs' mean nets, which needs every design compared, and each design's ratio of
    the first to the second.
  - Each unit's mean monthly change over its standard deviation (p10, p50, p90).
  - The share paid by session 21 by start year.
- **Added here (the coin layer):** for a coin-driven design and each headline measure's per-unit value `x_{s,c}`:
  - the within-day variance across seeds, `mean_s var_c x_{s,c}`;
  - the variance of the start-day means, `var_s mean_c x_{s,c}`;
  - each one's share of their sum. This is E-015 (1)'s "start day's share of the variance".
  - Beside them: the per-seed spread of section 1, and the effective number of independent starts.
- **Summary and unit:** as listed; dollars, ratios and shares.
- **Status:** partial
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`, `luck_rows` and
    `monthly_mean_over_sd`; `extended/user_measures.py`, `n_eff_bartlett`.
  - [U1]: `luck:sd_net_across_starts@{21,63,126,252}`, `luck:sd_of_configuration_means@...`,
    `luck:sd_across_starts_over_sd_of_configuration_means@...`, `luck:monthly_mean_over_sd_p{10,50,90}@252`,
    `luck:share_paid_by@21[year]`.
  - [B]: `extra/n_eff_bartlett/value`, `extra/n_nonoverlapping/value`.
- **To build:** the coin-layer decomposition and the seed spread, with the seed-paired runner (plan Wave 3.2).
- **Parameters:** the coin seeds: the declaration's.

### Baselines

### (35) Naive coin harvesting
- **Definition:** a baseline row. Every measure above is computed for the naive coin source's design, under the same
  account policy, the same units and the same coin seeds as the design compared. The source itself (its timing, shape
  and sessions) is declared by `wt-levels` (plan Wave 3.3), not here.
- **Summary and unit:** each measure in its own summary and unit.
- **Status:** to build. This is `wt-levels`' naive coin source, run at H4.
- **Where:** nothing computes it. Stage 2's coin designs P-15 and P-16 (family RC) are baselines (36), not this one.
- **Parameters:** the source's declaration (Wave 3.3) and H4's seeds.

### (36) P-14, P-15 and P-16
- **Definition:** a baseline row. Every measure above is computed on Stage 2's three registered designs, replayed as
  U1 replays them. R\* = P-14 on P (CHARTER; E-008).
- **Summary and unit:** each measure in its own summary and unit.
- **Status:** partial
- **Where:**
  - Functions: `extended/user_beside.py`, `run_starts` (designs `p14`, `p15` and `p16`, every response);
    `vendor/stage2/propedge/research/u_select.py`, `ROWS_TO_BEAT`.
  - [B] and [BS]: column `design` = `p14`, `p15`, `p16`.
  - [U1]: `config` = `p14`, `p15`, `p16`.
- **To build:**
  - The new measures on them (H4).
  - P-15 and P-16 under many coin sequences. Stage 2 declared fifty sequences (`u_select.COIN_SEQUENCES`, D-568); H4's
    seeds are its declaration's.
- **Parameters:** H4's seeds and arms: its declaration.

### Supply and speed

### (37) Trades available per day, per account and in total
- **Definition:** for each session `d` of a unit:
  - `offered_d` is the number of trades the design's component schedule offers. These are the signals that fire,
    before account states and the one-position-at-a-time rule.
  - `taken_d` is the number of trades entered across all accounts.
  - `taken_per_account_d = taken_d / accounts_d`, with `accounts_d` as in (30).
- **Summary and unit:**
  - Per unit: the mean of each quantity over its observed sessions.
  - Then p10, p50 and p90 over `E_h`.
  - Unit: trades per session.
  - `offered_d` depends only on the calendar date, so its spread across start days is the calendar's.
- **Status:** to build
- **Where:** nothing computes it.
  - Ingredient: `extended/replay_records.py`, `ReplayRecorder` (each trade's offer and place).
- **Parameters:** the horizon `h`: the declaration's.

### (38) Session coverage
- **Definition:** for each session window `w` in {Asia, London, NY AM, NY PM}, per unit: the share of its observed
  trading days with at least one trade taken whose entry time falls in `w`. Beside it, the same share for trades
  offered.
- **Summary and unit:** p10, p50 and p90 over `E_h`, for each window. Unit: a share.
- **Status:** to build
- **Where:** nothing computes it.
- **Parameters:**
  - The windows' boundaries: the trigger library's declaration (`wt-levels`, plan Wave 3.3), inside the hours the
    firm allows (its verified rules).
  - The horizon `h`: the declaration's.

### (39) Longest idle stretch inside the firm's trading day
- **Definition:** for each trading day of a unit, the longest interval inside the firm's trading day during which no
  account holds a position. The firm's trading day runs from its session open to its daily flat time. Beside it, the
  same measure on offered signals: the longest interval with no signal.
- **Summary and unit:**
  - Per unit: the median and the maximum over its days.
  - Then p10, p50 and p90 over `E_h`.
  - Unit: minutes.
- **Status:** to build
- **Where:** nothing computes it.
- **Parameters:** the firm's trading-day hours: its verified rules only (`vendor/stage2/config/rules.yaml`;
  `config/rules_extended.yaml` through `extended/firm_terms.py`). The horizon `h`: the declaration's.

---

## 5. Dropped by the operator

- **Firm-rule exposure** (the flagged-pattern rate): dropped (plan section 3). It is not a measure. Conduct tier 1 stays
  a floor, and the firm responses stay the denial ladder of (33).
- **Rule-change sensitivity**: dropped (plan section 3).

---

## 6. Choices this file makes (for the red team and the lead)

Where the plan was silent or open to two readings, this file chose one, as follows. A different reading is a change to
this file under a decision row.

1. **The coin layer.** The headline pools the units `(s, c)` with equal weights. The seed spread is a statistic per
   seed, summarised across seeds. The alternative, a per-start mean over seeds first, was not chosen: it hides the
   user's payout variance, which the plan asks to be reported.
2. **(2) Cash to the first pass** reads `spent_before` (U1's and Q-44's), which excludes the pass close's own fees.
   The fees paid at the pass close (Q-86's `fees_at_first_pass`) are beside it.
3. **(4)** exists in U1 (`first_pass:share_by@21`), although the plan marks it new.
4. **(16)** is the per-unit mean of the monthly changes over months 4 to 12, not a pooled distribution of unit-months.
5. **(21)** follows Stage 2's `payout_rhythm`. The gap includes the stretch from the last payout to session 126, and
   units unpaid by 126 are left out. The plan's name says "between payouts".
6. **(24)** counts a unit never paid by `W` as run out if its out-of-pocket over the closes 0 .. `W` exceeds `B`.
   Spending exactly `B` is not running out. The closes counted are those before the payout close, as U1's
   `spent_before` counts them.
7. **(27)** is CVaR10 of the month-3 net (Q-17's). The plan names no quantity.
8. **(30)** counts one order per trade entered, with its bracket. "Accounts at once" means accounts live at a close,
   not accounts holding a position: with one position at a time across a firm (D-429), at most one account holds a
   position.
9. **(31)** counts payouts *received* before the account ends, pooled over accounts with equal weights. Open accounts
   are censored.
10. **(33)** reads the pooled mean 12-month net as "making money". The grid and the measure are the declaration's to
    confirm.
11. **(39)** "Idle" means no position open on any account. The offered-signal version is beside.
12. **Windows.** The existing windows (126 for the first pass and payout, 252 for the year) are the existing code's
    constants. Any other window is the search declaration's.

---

## 7. The index (machine-read by `tests/test_measures_doc.py`)

Status: `exists` (every part defined and computed by code today), `partial` (part exists and part is to build) or
`to build`.

**How a reference is checked.** A reference in the code or names column is `path::Name`, which must be a top-level
function, class or assignment, or `Class.method`, in that file. A reference `path::CONST[item]` requires `item` to be
an element of the literal constant (for a tuple of calls, their first arguments). A reference `path::"text"` requires
the text to occur in the file. For a `to build` row, the references are ingredients, and they are checked the same
way.

<!-- measures-index:start -->
| # | measure | status | code | names |
|---|---|---|---|---|
| 1 | Sessions to the first evaluation pass | exists | `extended/user_measures.py::days_quantile`; `extended/user_readings.py::path_rows`; `extended/user_readings.py::FIRST_WINDOW` | `extended/user_readings.py::START_COLS[first_pass]`; `vendor/stage2/propedge/research/user_journey.py::PASS_DAYS[42]` |
| 2 | Cash to the first pass | exists | `extended/user_readings.py::path_rows`; `vendor/stage2/propedge/research/user_journey.py::start_record`; `vendor/stage2/propedge/research/customer_journey.py::spent_before`; `extended/user_spend.py::spend_record` | `extended/user_readings.py::START_COLS[spent_before_first_pass]`; `extended/user_spend.py::"fees_at_first_pass"` |
| 3 | Evaluations bought before the first pass | exists | `extended/user_spend.py::spend_record`; `extended/user_spend.py::SUMMARY_MEASURES` | `extended/user_spend.py::"evaluations_before_first_pass"`; `extended/user_spend.py::"resets_before_first_pass"` |
| 4 | Share of starts passed by session 21 | exists | `vendor/stage2/propedge/research/user_journey.py::stats` | `vendor/stage2/propedge/research/user_journey.py::PASS_DAYS[21]` |
| 5 | Sessions to the first payout (S3b) | exists | `extended/user_readings.py::path_rows`; `vendor/stage2/propedge/research/u_select.py::scorecard` | `extended/user_readings.py::START_COLS[first_payout]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S3b]` |
| 6 | Cash spent before the first payout: the bankroll needed (S1) | exists | `extended/user_readings.py::path_rows`; `vendor/stage2/propedge/research/user_journey.py::start_record` | `extended/user_readings.py::START_COLS[spent_before_first_payout]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S1]` |
| 7 | The first payout's size (S3d) | exists | `vendor/stage2/propedge/research/user_journey.py::start_record`; `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `vendor/stage2/propedge/research/user_journey.py::RECORD_KEYS[first_payout_cash]`; `vendor/stage2/propedge/research/user_journey.py::"cash_p"` |
| 8 | Share of starts paid by session 21 (S3a) | exists | `vendor/stage2/propedge/research/user_journey.py::stats`; `vendor/stage2/propedge/research/u_select.py::scorecard` | `vendor/stage2/propedge/research/user_journey.py::PAYOUT_DAYS[21]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S3a]` |
| 9 | Sessions to break-even | exists | `extended/user_measures.py::break_even_day`; `extended/user_readings.py::path_rows`; `extended/user_readings.py::BREAK_EVEN_MONTHS` | `extended/user_readings.py::START_COLS[break_even_day]`; `extended/user_readings.py::"break_even_days"` |
| 10 | Share falling back below break-even | exists | `extended/user_measures.py::fell_back`; `extended/user_readings.py::path_rows` | `extended/user_readings.py::START_COLS[fell_back]`; `extended/user_readings.py::"share_fell_back"`; `extended/user_spend.py::"break_even_lost"` |
| 11 | Deepest fall after break-even | exists | `extended/user_measures.py::deepest_fall_after`; `extended/user_readings.py::path_rows` | `extended/user_readings.py::START_COLS[deepest_fall_after_break_even]` |
| 12 | Net cash at months 1, 2, 3, 6 and 12 | exists | `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `extended/user_readings.py::START_COLS[net_month_1]`; `extended/user_readings.py::START_COLS[net_month_6]`; `extended/user_readings.py::START_COLS[net_month_12]`; `vendor/stage2/propedge/research/user_journey.py::PERIODIC_MONTHS[6]`; `vendor/stage2/propedge/research/user_journey.py::NET_PERCENTILES[10]` |
| 13 | P, and the shares ahead at months 6 and 12 (S4a, S4b) | exists | `extended/user_measures.py::p_by_month`; `extended/user_measures.py::months_ahead`; `vendor/stage2/propedge/research/u_select.py::scorecard`; `vendor/stage2/propedge/research/u_select.py::p_of`; `extended/user_readings.py::extra_rows` | `extended/user_readings.py::START_COLS[months_ahead]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[P]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S4a]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S4b]`; `extended/user_readings.py::"P_bankroll_"` |
| 14 | Payouts per fee dollar (S3c) | exists | `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `vendor/stage2/propedge/research/user_journey.py::"payouts_per_fee_dollar_pooled"`; `vendor/stage2/propedge/research/user_journey.py::MONEY_BACK_MONTHS[3]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S3c]` |
| 15 | Return on money at risk | to build | `extended/user_spend.py::spend_record` | — |
| 16 | Monthly net in months 4-12 | to build | — | `extended/user_readings.py::START_COLS[net_month_3]`; `extended/user_readings.py::START_COLS[net_month_12]` |
| 17 | Payouts per month | exists | `extended/user_measures.py::evenness`; `extended/user_readings.py::path_rows` | `extended/user_readings.py::START_COLS[payouts_per_month]`; `extended/user_readings.py::START_COLS[payout_cash_per_month]` |
| 18 | Share of months with a positive net change | exists | `extended/user_measures.py::evenness` | `extended/user_readings.py::START_COLS[share_months_positive]` |
| 19 | Spread of monthly net | exists | `extended/user_measures.py::evenness`; `vendor/stage2/propedge/research/user_journey.py::monthly_mean_over_sd` | `extended/user_readings.py::START_COLS[sd_monthly_net]` |
| 20 | Longest run of months without a payout | exists | `extended/user_measures.py::evenness` | `extended/user_readings.py::START_COLS[longest_months_without_payout]` |
| 21 | Longest gap between payouts within 126 sessions (S5b) | exists | `vendor/stage2/propedge/research/user_journey.py::payout_rhythm`; `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `vendor/stage2/propedge/research/user_journey.py::GAP_WINDOWS[126]`; `vendor/stage2/propedge/research/user_journey.py::"longest_gap_p"`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S5b]` |
| 22 | Best quarter's share of month-6 net (S5c) | exists | `vendor/stage2/propedge/research/user_journey.py::concentration`; `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `vendor/stage2/propedge/research/user_journey.py::CONCENTRATION_MONTHS[6]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S5c]` |
| 23 | Largest month's share of the year's payouts | exists | `extended/user_measures.py::evenness` | `extended/user_readings.py::START_COLS[largest_month_share]` |
| 24 | Chance of running out before the first payout (the bankroll stop) | to build | `extended/user_measures.py::share_over_limit`; `extended/user_measures.py::p_by_month` | `extended/user_readings.py::"share_spent_over_"` |
| 25 | Peak out-of-pocket in 12 months | to build | `vendor/stage2/propedge/research/customer_journey.py::drawdown_from_start` | — |
| 26 | Month-3 net of the unlucky tenth (S5a) | exists | `vendor/stage2/propedge/research/user_journey.py::metric_rows`; `vendor/stage2/propedge/research/u_select.py::scorecard` | `extended/user_readings.py::START_COLS[net_month_3]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S5a]` |
| 27 | CVaR10 | exists | `extended/user_measures.py::cvar`; `extended/user_readings.py::extra_rows` | `extended/user_readings.py::"cvar10_net_month_3"` |
| 28 | Headline measures with 10 % and 20 % of signals missed or late | to build | — | — |
| 29 | Headline measures at one and two ticks of worse fills | to build | — | — |
| 30 | Workload: orders a day, accounts at once, screen hours | to build | `extended/replay_records.py::ReplayRecorder` | — |
| 31 | Funded-account lifetime: payouts per funded account before it is lost | to build | `extended/user_beside.py::response_record`; `extended/replay_records.py::ReplayRecorder` | — |
| 32 | Worst year and highest-volatility period | to build | `vendor/stage2/propedge/research/u_select.py::START_YEARS`; `vendor/stage2/propedge/research/u_select.py::year_rule` | — |
| 33 | Break-even denial rate | to build | `extended/user_beside.py::RESPONSES`; `extended/user_beside.py::DENIAL_LEVELS`; `extended/user_beside.py::start_seed` | — |
| 34 | Luck against design (S6) | partial | `vendor/stage2/propedge/research/user_journey.py::metric_rows`; `vendor/stage2/propedge/research/user_journey.py::luck_rows`; `vendor/stage2/propedge/research/user_journey.py::monthly_mean_over_sd`; `extended/user_measures.py::n_eff_bartlett` | `vendor/stage2/propedge/research/user_journey.py::LUCK_MONTHS[12]`; `extended/user_readings.py::"n_eff_bartlett"` |
| 35 | Naive coin harvesting | to build | — | — |
| 36 | P-14, P-15 and P-16 | partial | `extended/user_beside.py::run_starts`; `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT`; `vendor/stage2/propedge/research/u_select.py::COIN_SEQUENCES` | `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT[p14]`; `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT[p15]`; `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT[p16]` |
| 37 | Trades available per day, per account and in total | to build | `extended/replay_records.py::ReplayRecorder` | — |
| 38 | Session coverage | to build | — | — |
| 39 | Longest idle stretch inside the firm's trading day | to build | — | — |
<!-- measures-index:end -->
