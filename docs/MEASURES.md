# The journey measures: definitions (37 measures plus the baseline set)

Wave 1.2 of `docs/plans/RESTART_PLAN_journey_objective.md` (section 3, lane `wt-user`), revised in corrective cycle 1
against the red team's cold read (`docs/reviews/MEASURES_2026-11-18.md`; section 9 maps each finding to its answer).

The plan's 39 items keep the plan's numbers, so this file and the plan agree. They are **37 measures plus the baseline
set**: (35) and (36) are comparators, not measures (the amendments draft, CHARTER 2). This file defines each measure
exactly, says which function computes it today and under which column or key its value is written, or says "to build".
**It holds definitions only: no value of any measure appears here, and no seed.** Every value is in a result file with
its manifest. Nothing here is in force until the lead records it under a decision row. The auditor re-derives every
journey figure from it.

`tests/test_measures_doc.py` holds this file to the code. Every function, constant and column named in the index
(section 8) for a measure marked `exists` or `partial` must be defined in the named file. Every measure has a status,
every `to build` entry is marked so, and every code line listed as "to change" (section 6) is where it says. The test
reads no data. It checks names, not meanings. The meanings are Wave 3.1's tests (m-13): `tests/test_journey_measures.py`
(one synthetic test with a known answer per definition built, the red team's cases by name) and
`tests/test_journey_readings.py` (the journey's window and readings through the engine, on a synthetic campaign).

---

## 1. Conventions (every measure uses them)

### 1.1 The unit, the blocks and the observation window

**The unit.** A *unit* `u = (s, c)` is one user. `s` is a *start day*: one session of a block, taken as a fresh start,
with a fresh bankroll and fresh accounts, and the design's trades replayed in historical order (U1, Stage 2 D-620;
`vendor/stage2/docs/USER_MILESTONES.md`). `c` is a *coin seed*. **Every design and every baseline** runs under the
zero-edge convention (the amendments draft, CHARTER 3.2):
- the fill comes from the real order;
- the path after the fill is reflected about the fill price with probability one half, by the coin of the declared
  seed;
- the **deciding reading is the martingale-outcome reading**: each trade's outcome is redrawn at its own bracket's
  driftless first-exit odds, keyed by the declared seed;
- the as-walked (reflected) and as-traded readings are reported beside, never credited.

So every design, baselines included, has the declaration's coin seeds. The seeds are fixed in the search declaration
before its run (CLAUDE.md; CHARTER 3.6). They are never chosen here.

**The coin keying (the three-way test's design, `docs/plans/THREE_WAY_TEST_design.md` 1.5, choice 3; the lead's
ruling).**
- **Each user has their own coin draws.** The key of every draw carries the start day, so under one seed `c` the units
  `(s, c)` of different start days draw independently of each other. Two start days never share a coin draw.
- **One user's trades at one moment read the same side draw.** The side coin's key carries no account or firm
  index, so trades of one user's accounts and firms at the same moment read the same draw. That means only the
  conduct-tier-1 refusal -- no two of the user's accounts or firms hold opposite positions at once -- never that
  every account copies every trade: accounts alternate, and the coin is the evaluation's device, not the
  playbook's (CHARTER 3.5; E-221, O-4).
- **The pairing.** The design and every baseline, deciding at the same moment on the same start under the same seed,
  read the same side uniform.
- The keying itself (its words, its generator) is the three-way test's, pinned with its declaration, never this
  file's.
- What the units of one seed still share is the history: neighbouring start days replay overlapping sessions.

**The blocks (E-208).**

| block | sessions | read by |
|---|---|---|
| search years | NQ 2020-01-02 to 2023-12-29 | the search, its lever ranges, limits, budgets, weights and H4 |
| held-out years | NQ 2024-01-02 to 2026-07-16, on the pinned calendar `results/q82_judged_sessions.csv` | the one joint held-out test of every firm's finalists only (CHARTER 3.6 (c); E-221) |

The confirmation window (NQ from 2026-07-17) is never read by any measure here.

**The observation window (B-1).** `obs_u = min(252, the sessions from s to the last session of s's block)`.
- The engine run itself stops at the block's end: the runner refuses **outcome** sessions after the block's last
  session (CHARTER 3.6 (e)), not only the reading. Causal look-backs before the start (a volatility normaliser read
  from earlier sessions) stay allowed, as CHARTER 3.6 (d) allows them, and follow `feature-rules` (v2 m-3).
- **Every field read at horizon `h`** is computed from closes `0 .. h` only. This covers the first pass, the first
  payout, the spending before it, the pay days, break-even, the fall-back and the deepest fall, every month-end net
  and every count.
- A long replay's events before `h` can depend on the run's length (D-620 (3)(f), the reason for `Views.at`). So each
  reading at `h` is taken from a run of exactly `h` sessions, or from a long run cut at the block's end with U1's
  identity checked on the cut runs (the event days up to `h` equal to the exact run's).
- **Which record each reading read is recorded** (m-8): for every reading at `h`, its manifest names the record (exact
  `h` run or cut long run) and the count of starts where the two differ.
- **The consequence:** at the 12-month horizon (252 sessions), no search-year start from 2023 is read. At 126 sessions,
  only starts with 126 sessions left in 2023 are read. A held-out start is read at `h` only if `h` sessions remain
  before 2026-07-17.

**The common start set (m-7).** `E_h` is the set of start days of a block with `obs_u >= h` (at least `h` sessions left in the block; v2 m-2). For each
horizon `h`, **every measure read at `h` reads the same `E_h`**, for every design, every baseline and every seed (the
units are paired). A composite whose dimensions sit at different horizons weights the late search year differently
across them. Each dimension names its horizon, so this is visible, and it is pinned with CHARTER 3.9's inputs.

### 1.2 The clock, the money and the events

**The clock.** Day 0 is the purchase evening. Day `k` is the close of the `k`-th session. A *month* is 21 sessions,
and month `m` holds sessions `21(m-1)+1 .. 21m` (`extended/user_measures.py`, `month_of`).

**The money.** `rel_u[k]` = the cash at close `k` less the starting bankroll, which equals the payouts received by
close `k` less every fee paid by it. The replay's bankroll never binds. `F_u[k]` is the cumulative fees paid by close
`k` (subscription, activation, reset), and `Pay_u[k]` is the cumulative payouts received, so `rel_u = Pay_u - F_u`. A
payout counts on the close its cash *arrives*: activation day + 1 + the account's relative request day + the firm's
payout lag (U1's `payout_arrivals`).

**Events** (each from closes `0 .. h` of the reading's horizon):
- `first_pass_u` is the first close on which a Combine passes.
- `first_payout_u` is the first close on which payout cash arrives.
- `be_u` is the first close `k >= 1` with `rel_u[k] >= -1e-6`. This is break-even, "at or above zero" to a millionth
  of a dollar.

**Ahead (m-11)** means `rel_u[k] > 1e-6`, above zero by more than a millionth of a dollar, the same tolerance as
break-even. A path whose payouts equal its fees is not ahead by float residue. Since Wave 3.1 this repository's two
"ahead" tests read `> 1e-6` (`extended/user_measures.py`, `p_by_month` and `months_ahead`; section 6). Stage 2's
vendored `u_select` reads `> 0`, and Stage 2's registered rows beside keep Stage 2's reading.

**Spent before a close.** `spent_before(rel, k) = max(0, -min_{0 <= j < k} rel[j])` is the deepest net below zero over
the closes *before* close `k` (`vendor/stage2/propedge/research/customer_journey.py`, `spent_before`). **The peak
out-of-pocket through close `k`** is the same quantity. Before the first payout it is the cash spent before the first
payout. After it, it also counts spending after the first payout.

### 1.3 Summaries, censoring and blanks

**Summaries.**
- Unless a measure says otherwise, a measure is a distribution over units, summarised by its **p10, p50 (the median)
  and p90**. These are numpy's linear percentiles.
- A *share* is the mean of a 0/1 indicator over `E_h`.
- A *pooled ratio* is a sum over units divided by a sum over units.

**Censoring.**
- For days to an event within window `W`, an unreached unit is **censored at `W + 1`** ("beyond").
- A percentile computed with censored units at `W + 1` is never blank. A value of `W + 1` reads "beyond the window".
  Stage 2's form, which blanks a percentile beyond the window (`days_quantile`; D-518 (3)), is reported beside.
- For a dollar quantity up to an event, an unreached unit's value through `W` is a **lower bound**, flagged censored.
- **The strict rule for a censored dollar percentile (N-1).** A dollar percentile is exact only if every censored
  unit's lower bound lies strictly above it. Otherwise it is reported as "at least" that value. A lower bound below the
  percentile can move above it once the true value is known, so the rule looks at every censored unit, not only the
  one the percentile falls on. A limit is never read on such a percentile: a bankroll limit is read through (24)'s
  three states.
- The days form needs no such rule: a unit censored at `W + 1` lies above every finite value by construction.

**Conditional readings carry their share (B-3).** Every percentile read only on the units that reached an event names
the share that reached it, beside it: "the share passed by `W`" at (2) and (3), and "the share paid by `W`" at (6) and
(7). At (23) it is "the share paid within the twelve months".

**The blank rule for the composite (m-6).** A composite input must never be blank.
- Each measure below states its **per-unit form** (the value `x_u` of one unit, which Wave 4.1's variation across
  starts and seeds needs), or says it has none (a design-level number).
- Each measure also states its **never-blank form** (the share reached by the window, the censored value `W + 1`, a
  lower bound).
- A measure whose only forms can be blank, or that has no per-unit value, is **not a composite input** unless CHARTER
  3.9's pinning row pins a never-blank form for it. That form is chosen before the survey, never after seeing which
  designs blank.

### 1.4 Over coin seeds: three readings (B-4)

The following are reported, each under its label. Readings 1 and 3 apply to every measure. **Reading 2 needs a
per-unit value `x_{s,c}`, so it applies only to the measures with a per-unit form** (v2 m-5). The design-level
measures -- (22), (27), (31), (33) and (34) -- carry readings 1 and 3 only, and their entries say so.

1. **"A random user"**: the distribution over the pooled units `(s, c)` of `E_h`, every unit weighted equally (the
   summary of section 1.3).
2. **"The user's payout variance"**: for each start day `s`, the p10, p50 and p90 of `x_{s,c}` across the seeds `c`.
   This is the spread a user starting that day can live. It is summarised over `s` by:
   - the median start day's within-day p10 and p90;
   - the p10, p50 and p90 over `s` of the within-day spread (p90 less p10).

   For a share, the within-day value is the share of seeds on which the unit is in the state (`q_s`, the chance that a
   user starting on `s` is in it), summarised over `s` by its p10, p50 and p90.
3. **"The design statistic's coin noise"**: the statistic (P, a share, a percentile) computed separately for each seed
   over its start days, then its p10, p50 and p90 across the seeds. This is the coin-seed leg's replicate spread
   (CHARTER 3.6 (f) (i)). It is **not a user quantity**. Under the keying of section 1.1 (each user's own draws,
   choice 3), the per-seed statistic is a mean over independent users on the one fixed history. Its spread across
   seeds is therefore the coin noise of a statistic averaged over many users. It shrinks with the number of start days
   and says nothing about how much one user's results vary; reading 2 says that.

The amendments' sentence "the coin-seed spread is reported: it is the user's payout variance" (CHARTER 2, 3.6) refers
to reading 2.

**The effective number of independent starts (m-5).** For each seed `c`, `n_eff_bartlett` of `x_{., c}` is taken in
start order at the reading's horizon as the lag, and reported as the median across seeds. Under section 1.1's keying the
coin draws are independent across start days, so the dependence it measures is the shared history of overlapping
sessions. Beside it is the `n_eff` of the start-day means `mean_c x_{s,c}`, which is the history-limited count.

**The readings are computed by `extended/journey_measures.py`** (Wave 3.1): `coin_readings` for a per-unit measure
(readings 1, 2 and 3, and the two `n_eff` values) and `design_coin_readings` for a design-level one (readings 1 and 3),
each on the matrix `x[s, c]` of start days by seeds; (34)'s ANOVA is `variance_decomposition`. Reading 2's "median start
day's within-day p10 and p90" is computed as the median over start days of the within-day p10, and of the within-day
p90. **The seed-paired runner that fills `x[s, c]` is to build** (plan Wave 3.2, `wt-verify`): every reading below is
today made on one path per start.

### 1.5 The old input path, and where values are written

**Every `exists` mapping below is computed today on the old input path:**
- Stage 2's `verdict` and `point` arms, which are retired (CHARTER 3.10);
- one coin sequence;
- the long replay over the whole development window (B-1).

The functions are pure and reusable on the new path. The path itself (the zero-edge convention, the block-bounded
window, the seeds) is Wave 3.1's and 3.2's. A reading under the firm's responses is computed with every response off in
the verdict (0 % payout denial, the placement off, the Focused Trader Program off; CHARTER 3.8), and the ladder is
reported beside.

**The block-bounded window, built in Wave 3.1 (B-1).** `extended/user_beside.py`, `run_starts(..., journey=True)`,
stops each start's long run at the last session of its block of E-208 and refuses a calendar with a date in neither
block. Each start's output then carries its `journey` fields: its block, the sessions left in it, the run's
close-by-close net `rel`, the peak out-of-pocket through each month close, the Combines' purchase days and each funded
account's ending fields and payout arrivals. `extended/user_readings.py`, `summary`, on the blocks `search` and
`held_out` (its default is `search`), reads those journeys; `extended/journey_readings.py`, `summary`, adds the
section `journey`. Every `journey` row reads closes `0 .. h` of `rel`. The zero-edge convention and the seeds are
still Wave 3.2's, so these readings are still made on Stage 2's arms and one coin sequence. No such reading has been
written to a file: the keys below marked "Journey" name the summary rows (`section` / `measure` / `stat`, `block`
`search` or `held_out`) a reading writes.

**Where values are written (the keys used below).**

| key | file | how a value is named |
|---|---|---|
| [B] | `results/user_beside.csv` (Q-44, E-201) | `section` / `measure` / `stat` |
| [BS] | `results/user_beside_starts.csv` (Q-44, E-201) | one row a design, arm, response and start; the column named |
| [U1] | `vendor/stage2/results/user_journey.csv` (Stage 2 D-620) | sections `metric` / `month`: the `key` column, `group:measure@days`; section `start`: the column named |
| [SP] | `results/user_spend.csv` (Q-86) | **not yet written**: `scripts/user_spend.py` writes it from a clean run only; the column named |

**Which record a derivation reads (m-8).**
- [BS] holds each start's **long-replay** record (`extended/user_readings.py`, `start_table`).
- [B]'s `scorecard` section and [U1] read the **exact-length run's** record where its event days differ (`Views.at`).
- Under responses other than `off`, the exact runs were made on every 21st start only (`user_beside.EXACT_EVERY`). So
  [B]'s card under those responses is not U1's reading on the starts not sampled.
- A value derived here from [BS] reads the long record. That is said wherever it is used.

[U1] holds the `off` reading only, on U1's nine configurations. [B] and [BS] hold every response of Q-17 on P-14, P-15
and P-16. All three files read the whole development window, so they are entries of the held-out read ledger
(section 7).

---

## 2. P (not a p-value)

**P is not a p-value.** It is a share of users, not a probability of a test statistic. It was Stage 2's primary
measure (D-621 (1)). Under the bankroll stop, it is the composite's P dimension and the pinned fallback (CHARTER 3.9).

**Definition.** Take the units of `E_63` (n units, every month-end net read from closes `0 .. 63`). Then

    P = ( sum over u in E_63 of  sum over m in {1, 2, 3} of  1[ rel_u[21 m] > 1e-6 ] ) / (3 n)

That is, P is the mean over months 1, 2 and 3 of the share of units *ahead* at that month's end, all three shares
taken on the same units. It is an exact ratio of counts in [0, 1], so two designs tie exactly or not at all. Per unit,
the count `months_ahead_u` ranges from 0 to 3 (the per-unit form). P is never blank on a non-empty `E_63`.

**P under the bankroll stop, `P_B` (B-2).** This is the same ratio, except that a unit counts as ahead at month `m`
only if its **peak out-of-pocket through the month close** is at most `B`:

    ahead under B at m  =  1[ rel_u[21 m] > 1e-6 ]  and  1[ max(0, -min_{0 <= j < 21 m} rel_u[j]) <= B ]

- A user whose spending **exceeds** the budget at any close before the month close, before or after a first payout,
  has quit and is not ahead. Spending exactly `B` is within it, as at (24) (v2 m-4).
- **Beside it, the named sub-reading "before the first payout":** the same rule with the spending before the first
  payout in place of the peak. This is the Q-17 reading.
- **The stop is read on the replay's own path (m-12).** A unit that quits keeps no payout, including payouts from
  funded accounts already live when the budget binds. This is conservative and biased against designs that hold many
  accounts. The alternative stop, "no new fee after `B`, the live accounts kept", needs a re-run with a wallet. It is
  to build as a reading beside, never deciding until a row says so.
- `B` is **the bankroll budget, the lead's, set in Wave 4.2 from H4's search-year results by a rule declared before
  H4 is read** (CHARTER 3.9; E-221).

**Where.**
- Functions: `extended/user_measures.py`, `p_by_month` (P and `P_B`: on E-208's blocks its caller,
  `extended/user_readings.py`, `extra_rows`, passes the peak through each month close, the journey's `peak_month`
  field, made by `user_measures.peak_by_month`; the sub-reading passes the spending before the first payout, read on
  closes `0 .. 21 m`) and `months_ahead`; `extended/journey_measures.py`, `months_ahead_under` and `p_bankroll` (the
  same from each unit's `rel`, a second code path the synthetic test holds equal); `vendor/stage2/propedge/research/
  u_select.py`, `scorecard`, `p_of` and `months_ahead` (Stage 2's, `> 0`).
- [B]: `scorecard/P/value`; `extra/P/value` (held equal to the card's by a refusing check);
  `extra/share_ahead_month_{1,2,3}/value`; `extra/P_bankroll_2000/value` and `extra/P_bankroll_2500/value` (the
  "before the first payout" form, at Q-17's own limits, which are not the pinned ones of CHARTER 3.9, E-221; on
  the registered blocks only). On E-208's blocks, at each budget the caller names: `extra/P_B_{B}/value` and, beside
  it, `extra/P_B_before_first_payout_{B}/value`.
- [BS]: `months_ahead` (the long record).
- [U1]: `periodic:share_positive@21`, `@42` and `@63`, each on its own eligible starts (`u_select.p_from_u1`).

**Against what.** Every design is compared with **each baseline** of the baseline set (CHARTER 3.8 (b)). R\* = P-14 as
the one row to beat is retired (CHARTER 3.10).

---

## 3. The groups (the plan's section 3)

| group | numbers | what it answers |
|---|---|---|
| Getting funded | (1)-(4) | how long, how much and how many evaluations to a first pass |
| First payout | (5)-(8) | how long and how much to the first cash, and its size |
| ROI | (9)-(15) | when the user is back to zero, whether they stay there, how much they are ahead, the money back per dollar |
| Steady income and payout variance | (16)-(23) | whether the income is even across months or one lump |
| Bankroll and downside | (24)-(27) | the bankroll needed, the chance of running out, the unlucky tail |
| Realism and robustness | (28)-(34) | the same journey with missed signals, worse fills, the workload, account lifetimes, bad years, firm denial, luck |
| **The baseline set (comparators)** | (35)-(36) | the comparators every design must beat, each one; not measures |
| Supply and speed | (37)-(39) | how many trades are on offer, in which sessions, and how long the user waits between them |

**Aliases and redundancies, for Wave 4.1 (m-4).** In a correlation- or loading-based reduction a duplicated column
inflates its dimension. So these are de-duplicated before Wave 4.1's structure analysis (one column each), and each is
marked at its entry:
- (26) S5a is (12)'s p10 at month 3.
- (8) S3a is (5)'s share paid by session 21.
- (13)'s P is section 2.
- (16) and (19) are functions of the same twelve monthly changes as (18).
- (6) and (24) read one per-unit quantity, the spending before the first payout.
- (25) is (24)'s quantity through the whole window, and the denominator of (15).

The plan expects Wave 4's analysis (4.1, on the search years only) to reduce the measures to about five or six
dimensions. **That reduction is not made here.**

---

## 4. The measures

Every entry gives: the definition, the summary and unit, the per-unit and never-blank forms, the status (`exists`,
`partial` or `to build`), where it is computed and written, and the parameters with who sets them. Every value is read
on closes `0 .. h` of its horizon, on the common `E_h` (section 1.1), with the three coin readings of section 1.4.

### Getting funded

### (1) Sessions to the first evaluation pass
- **Definition:** `first_pass_u`, the first close on which a Combine passes (U1's `start_record`, `pass_days[0]`),
  within closes `0 .. W`.
- **Summary and unit:**
  - Over `E_W`: p10, p50 and p90, with unpassed units censored at `W + 1`.
  - Beside: the share passed by `W`, and Stage 2's blanking form.
  - Unit: sessions.
- **Per unit; never blank:** `x_u = first_pass_u`, or `W + 1` if unpassed. The censored percentile and the share are
  never blank.
- **Status:** exists
- **Built in Wave 3.1:** the censored percentile at `W + 1` as the headline (v2 m-1).
- **Where:**
  - Functions: `extended/user_measures.py`, `days_quantile` (`censored=True`: the headline, through `censored_days`;
    the default is Stage 2's blanking form, kept beside); `extended/journey_measures.py`, `days_reading`;
    `extended/user_readings.py`, `path_rows`.
  - Journey: `path/first_pass_days/p10`, `p50`, `p90` (censored), `stage2_p10` .. (Stage 2's form), `share_by_126`.
  - [B]: `path/first_pass_days/p10`, `p50`, `p90`, `share_by_126`.
  - [BS]: `first_pass` (the long record).
  - [U1]: `first_pass:days_p50@42`, `first_pass:days_p90@42` (U1's window is 42).
- **Parameters:** window `W`. Q-44 used `W = 126` (`extended/user_readings.py`, `FIRST_WINDOW`; a held-out read ledger
  constant, section 7). The search declaration pins `W`.

### (2) Cash to the first pass
- **Definition:** `spent_before(rel_u, first_pass_u)`, the deepest net below zero over the closes before the pass
  close. No payout can arrive before a first pass, so this equals the fees paid through close `first_pass_u - 1`.
  Beside it: `fees_at_first_pass_u = F_u[first_pass_u]`, which also counts the fees booked on the pass close itself
  (Q-86).
- **Summary and unit:**
  - p10, p50 and p90 over the units of `E_W` that pass by `W`, with **the share passed by `W` beside**.
  - Dollars.
- **Per unit; never blank:**
  - `x_u` as defined for a passed unit.
  - For an unpassed unit, `spent_before(rel_u, W + 1)` is a censored lower bound.
  - The all-units form is never blank. Its percentiles follow section 1.3's strict rule (N-1): exact only if every
    censored lower bound lies strictly above, otherwise "at least".
- **Status:** exists
- **Where:**
  - Functions: `extended/user_readings.py`, `path_rows`; `vendor/stage2/propedge/research/user_journey.py`,
    `start_record`; `extended/user_spend.py`, `spend_record` (the fees reading); `extended/journey_measures.py`,
    `spent_to_event` (the all-units form, its censored flag) and `strict_quantiles` (the strict rule).
  - Journey: `journey/cash_to_first_pass/p10` .. `p90`, each with `p10_exact` .. (1 exact, 0 "at least"),
    `share_passed_by_W`, `n_censored`.
  - [B]: `path/spent_before_first_pass/p10`, `p50`, `p90`.
  - [BS]: `spent_before_first_pass`.
  - [U1]: `first_pass:spent_before_p50@42`, `p90@42`, `p95@42` (Stage 2's S2, its cash half at p90).
  - [SP]: `fees_at_first_pass`.
- **Parameters:** window `W`, as in (1).

### (3) Evaluations bought before the first pass
- **Definition:** the number of Combines whose purchase day is before `first_pass_u`. A purchase happens at a close's
  end, so a Combine bought on the pass close is bought after the pass. Resets of a failed Combine are counted apart
  (`resets_before_first_pass`).
- **Summary and unit:**
  - p10, p50 and p90 over the units of `E_W` that pass by `W`, with **the share passed by `W` beside**.
  - Unit: evaluations (a count).
- **Per unit; never blank:** for an unpassed unit, the evaluations bought through `W` are a censored lower bound. The
  all-units percentiles follow section 1.3's strict rule (N-1).
- **Status:** exists (in code; its file is not yet written)
- **Where:**
  - Functions: `extended/user_spend.py`, `spend_record` and `SUMMARY_MEASURES`; `extended/journey_measures.py`,
    `evaluations_to_first_pass` (the all-units form, its censored flag).
  - Journey: `journey/evaluations_before_first_pass/p10` .. `p90`, `p10_exact` .., `share_passed_by_W`.
  - [SP]: `evaluations_before_first_pass` and `resets_before_first_pass`.
- **Parameters:** window `W`, as in (1).

### (4) Share of starts passed by session 21
- **Definition:** over `E_21`, the share with `first_pass_u <= 21`.
- **Summary and unit:** one share, read three ways (section 1.4).
- **Per unit; never blank:** the indicator `x_u`. Never blank.
- **Status:** exists. The plan lists it as new; U1 already reads it.
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `stats` (`first_pass:share_by` at `PASS_DAYS`).
  - [U1]: `first_pass:share_by@21` (also `@5`, `@10`, `@42`).
  - It is not in [B]. It derives from [BS] `first_pass` and `observed` (the long record).
- **Parameters:** none.

### First payout

### (5) Sessions to the first payout (S3b)
- **Definition:** `first_payout_u`, the close on which the first payout's cash arrives (U1's `payout_arrivals`),
  within closes `0 .. W`.
- **Summary and unit:**
  - Over `E_W`: p10, p50 and p90, with unpaid units censored at `W + 1`.
  - **S3b is the p90.**
  - Beside: the share paid by `W`, and Stage 2's blanking form.
  - Unit: sessions.
- **Per unit; never blank:** `x_u = first_payout_u`, or `W + 1`.
- **Status:** exists
- **Built in Wave 3.1:** the censored percentile at `W + 1` as the headline (v2 m-1).
- **Where:**
  - Functions: `extended/user_readings.py`, `path_rows`; `extended/user_measures.py`, `days_quantile`
    (`censored=True`); `vendor/stage2/propedge/research/u_select.py`, `scorecard`.
  - Journey: `path/first_payout_days/p10` .. (censored), `stage2_p10` .., `share_by_126`.
  - [B]: `path/first_payout_days/p10`, `p50`, `p90`, `share_by_126`; `scorecard/S3b/value`.
  - [BS]: `first_payout`.
  - [U1]: `first_payout:days_p50@126`, `days_p90@126`, `days_p95@126`.
- **Parameters:** window `W` (Q-44 and U1: 126, a ledger constant), pinned by the search declaration.

### (6) Cash spent before the first payout: the bankroll needed (S1)
- **Definition (B-3), over all of `E_W`:** `x_u = spent_before(rel_u, k*_u)`.
  - `k*_u = first_payout_u` for a unit paid by `W`. Its `x_u` is exact.
  - `k*_u = W + 1` for an unpaid unit, so every close `0 .. W` counts. Its `x_u` is a **censored lower bound**: it is
    still paying fees and is not yet paid.
- **Summary and unit:**
  - The bankroll needed is the p10, p50 and p90 of `x_u` over `E_W`, with **the share paid by `W` beside**. Each
    percentile follows section 1.3's **strict rule (N-1)**: it is exact only if every censored unit's lower bound lies
    strictly above it; otherwise it is reported as "at least" that value.
  - **A bankroll limit is never read on these percentiles.** A limit on the bankroll needed is read through (24)'s
    three states, as the share of `E_W` not paid within `B` by `W` (run out plus censored).
  - **S1**, Stage 2's p90 over the paid units only, is kept beside as Stage 2's reading.
  - Unit: dollars.
- **Per unit; never blank:** `x_u` as above, with its censored flag. Never blank.
- **Alias (v2 m-7):** (24) reads the same per-unit quantity, and every bankroll limit is read there, through (24)'s
  three states, never on (6)'s percentile.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_readings.py`, `path_rows`; `vendor/stage2/propedge/research/user_journey.py`,
    `start_record`; `vendor/stage2/propedge/research/customer_journey.py`, `spent_before` (which gives the censored
    value at `W + 1`); `extended/journey_measures.py`, `spent_to_event` and `strict_quantiles` (the all-`E_W`
    reading with its censored flag, built in Wave 3.1).
  - Journey: `journey/spent_before_first_payout_all/p10` .. `p90`, `p10_exact` .., `share_paid_by_W`, `n_censored`.
  - [B]: `path/spent_before_first_payout/p10`, `p50`, `p90`; `scorecard/S1/value` (the paid-only form).
  - [BS]: `spent_before_first_payout`.
  - [U1]: `first_payout:spent_before_p50@126`, `p90@126`, `p95@126`.
- **Parameters:** window `W`, as in (5).

### (7) The first payout's size (S3d)
- **Definition (m-12):** the total payout cash arriving on the first payout's close, `Pay_u[first_payout_u] -
  Pay_u[first_payout_u - 1]`. When two payouts arrive on that close, the user feels their sum. Stage 2's
  `first_payout_cash` (the first arrival in U1's order alone) is kept beside.
- **Summary and unit:**
  - p10, p50 and p90 over the units of `E_W` paid by `W`, with **the share paid by `W` beside**.
  - **S3d is the p50.**
  - Unit: dollars.
- **Per unit; never blank:** defined for paid units only. No never-blank form is fixed here, so it is not a composite
  input unless CHARTER 3.9's row pins one.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_spend.py`, `u1_money` (`first_payout_day_cash`: the close's total);
    `vendor/stage2/propedge/research/user_journey.py`, `start_record` and `metric_rows` (Stage 2's form).
  - [U1]: `first_payout:cash_p10@126`, `cash_p50@126`, `cash_p90@126`; start rows `first_payout_cash`.
  - It is not in [B] or [BS].
- **Parameters:** window `W`.

### (8) Share of starts paid by session 21 (S3a)
- **Definition:** over `E_21`, the share with `first_payout_u <= 21`.
- **Summary and unit:** one share, read three ways.
- **Per unit; never blank:** the indicator. Never blank.
- **Alias:** (5)'s share paid by 21 (m-4).
- **Status:** exists
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `stats`; `u_select.py`, `scorecard`.
  - [B]: `scorecard/S3a/value`.
  - [U1]: `first_payout:share_by@21` (also `@30`, `@42`, `@63`, `@90`, `@126`).
- **Parameters:** none.

### ROI

### (9) Sessions to break-even
- **Definition:** `be_u = min{1 <= k <= 252 : rel_u[k] >= -1e-6}`, read at daily resolution from the run's own
  close-by-close cash.
- **Summary and unit:**
  - Over `E_252`: p10, p50 and p90, with units not broken even censored at 253.
  - Beside: the share broken even by 252, and the share broken even by month `m` on `E_{21m}` for m = 1, 2, 3, 6
    and 12.
  - Unit: sessions.
- **Per unit; never blank:** `x_u = be_u`, or 253.
- **Status:** exists
- **Built in Wave 3.1:** the censored percentile at 253 (`W + 1` at `W = 252`) as the headline (v2 m-1).
- **Where:**
  - Functions: `extended/user_measures.py`, `break_even_day` and `days_quantile` (`censored=True`);
    `extended/user_readings.py`, `path_rows`.
  - Journey: `path/break_even_days/p10` .. (censored at 253), `stage2_p10` .., `share_by_252`.
  - [B]: `path/break_even_days/p10`, `p50`, `p90`, `share_by_252`; `path/break_even/share_by_month_{1,2,3,6,12}`.
  - [BS]: `break_even_day`.
  - [SP]: `break_even_day`.
- **Parameters:** the year window 252 (`extended/user_readings.py`, `YEAR_WINDOW`; a ledger constant), or the
  declaration's.

### (10) Share falling back below break-even
- **Definition (m-12):** among the units of `E_252` with `be_u <= 252`, the share with some later close
  `be_u < k <= 252` where `rel_u[k] < -1e-6`.
- **Summary and unit:** one share, read three ways.
- **Per unit; never blank:** the indicator is defined on the units broken even. Never-blank form: on all of `E_252`,
  the share broken even and later fallen back.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `fell_back`; `extended/user_readings.py`, `path_rows`.
  - [B]: `path/break_even/share_fell_back`.
  - [BS]: `fell_back`.
  - [SP]: `break_even_lost`.
- **Parameters:** window 252, as in (9).

### (11) Deepest fall after break-even
- **Definition (m-12):** `max over be_u <= k <= 252 of ( max_{be_u <= j <= k} rel_u[j] - rel_u[k] )`, the deepest
  fall of the cumulative net from its running high, from the break-even close to close 252.
- **Summary and unit:** p10, p50 and p90 over the units of `E_252` broken even, with the share broken even beside.
  Unit: dollars.
- **Per unit; never blank:** defined on the units broken even only. Not a composite input unless pinned in a
  never-blank form.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `deepest_fall_after`; `extended/user_readings.py`, `path_rows`.
  - [B]: `path/deepest_fall_after_break_even/p10`, `p50`, `p90`.
  - [BS]: `deepest_fall_after_break_even`.
- **Parameters:** window 252.

### (12) Net cash at months 1, 2, 3, 6 and 12
- **Definition:** `rel_u[21 m]` for m = 1, 2, 3, 6 and 12.
- **Summary and unit:** p10, p50 and p90 over `E_{21m}` at each month. Unit: dollars.
- **Per unit; never blank:** `x_u = rel_u[21 m]`. Never blank on `E_{21m}`.
- **Status:** exists
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`.
  - [U1]: `periodic:net_p10@{21,42,63,126,252}`, `net_p50@...` and `net_p90@...` (also p5, p25, p75 and month 9).
  - [BS]: `net_month_1`, `net_month_2`, `net_month_3`, `net_month_6`, `net_month_12` (the long record).
  - [B] writes only the means at months 1 to 3: `extra/mean_net_month_{1,2,3}/value`.
- **Parameters:** none.

### (13) P, and the shares ahead at months 6 and 12 (S4a, S4b)
- **Definition:**
  - P and `P_B` are defined in section 2.
  - **S4a** = the share of `E_126` with `rel_u[126] > 1e-6`.
  - **S4b** = the share of `E_252` with `rel_u[252] > 1e-6`.
- **Summary and unit:** shares, read three ways.
- **Per unit; never blank:** `months_ahead_u` and the indicators. Never blank.
- **Alias:** P is section 2 (m-4).
- **Status:** exists
- **Built in Wave 3.1:** `P_B` with the peak through each month close (B-2), and "ahead" at `> 1e-6` (m-11).
- **Where:**
  - Functions: `extended/user_measures.py`, `p_by_month`; `extended/user_readings.py`, `extra_rows`;
    `extended/journey_measures.py`, `share_ahead_at` (S4a and S4b above `1e-6`) and `p_bankroll`;
    `vendor/stage2/propedge/research/u_select.py`, `scorecard`.
  - Journey: `extra/P/value`, `extra/P_B_{B}/value`; `journey/S4a/value`, `journey/S4b/value`.
  - [B]: `scorecard/P/value`, `scorecard/S4a/value`, `scorecard/S4b/value`.
  - [U1]: `periodic:share_positive@126` and `@252`.
- **Parameters:** for `P_B`, the budgets `B` (the lead's, Wave 4.2; CHARTER 3.9; E-221).

### (14) Payouts per fee dollar (S3c)
- **Definition:** the pooled ratio at month 3: `sum over u in E_63 of Pay_u[63]` divided by `sum over u in E_63 of
  F_u[63]`, where `Pay = net + fees`. It is blank when the fees sum to zero.
- **Summary and unit:**
  - One pooled ratio, read three ways on its design level.
  - Beside: U1's median of the per-unit ratio over units with fees above zero.
  - U1 also reads it at months 1, 6 and 12.
  - Unit: dollars of payouts per dollar of fees.
- **Use (m-12; CHARTER 2):** reported; **never a dimension of the composite**; compared across designs only within one
  trade stream (E-008 (1)'s rule for it, because its link to P across designs is partly arithmetic, E-007).
- **Per unit; never blank:** the per-unit ratio `Pay_u[63] / F_u[63]` (fees are above zero on every real start, since
  day 0 books the purchase).
- **Status:** exists
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`.
  - [U1]: `money_back:payouts_per_fee_dollar_pooled@63` (and `@21`, `@126`, `@252`);
    `money_back:payouts_per_fee_dollar_median@63`.
  - [B]: `scorecard/S3c/value`.
  - The per-unit fees: [U1] start rows `fees_month_k`; [SP] `fees_month_m` and `payouts_month_m`.
  - E-201 D1 applies: under responses other than `off`, [B]'s S3c cannot be re-derived from the files (Q-139).
- **Parameters:** none.

### (15) Return on money at risk
- **Definition:** `ROMR_u = rel_u[252] / PeakOOP_u`, with `PeakOOP_u` (25)'s peak out-of-pocket over the same closes
  `0 .. 252`. Day 0 books the purchase fees, so `PeakOOP_u > 0` on every real start.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: a ratio (dollars of 12-month net per dollar of peak
  out-of-pocket).
- **Per unit; never blank:** `ROMR_u`. Never blank on a real start.
- **Status:** exists
- **Where:**
  - Function: `extended/journey_measures.py`, `return_on_money_at_risk` (built in Wave 3.1).
  - Journey: `journey/return_on_money_at_risk/p10`, `p50`, `p90`.
  - Not to confuse with `extended/user_spend.py`, `spend_record`'s `return_on_spend_month_m`, a different ratio: net
    over the fees paid, months 1 to 6.
- **Parameters:** none.

### Steady income and payout variance

### (16) Monthly net in months 4-12
- **Definition (m-1):** per unit, **the median** of the nine monthly changes `D_4 .. D_12` (`D_m` as in (18)). Their
  mean, `(rel_u[252] - rel_u[63]) / 9`, is beside it. The mean of nine flat months and one lump reads as an even
  income; the median does not.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: dollars per month.
- **Per unit; never blank:** the per-unit median. Never blank on `E_252`.
- **Alias:** it is a function of the same monthly changes as (18) and (19) (m-4).
- **Status:** exists
- **Where:**
  - Functions: `extended/journey_measures.py`, `monthly_net_4_12` and `monthly_changes` (built in Wave 3.1).
  - Journey: `journey/monthly_net_4_12_median/p10` .. `p90`; beside, `journey/monthly_net_4_12_mean/p10` .. `p90`.
  - Ingredients elsewhere: [U1] start rows `net_month_3` to `net_month_12`; [BS] `net_month_3` and `net_month_12`
    (the mean only).
- **Parameters:** none.

### (17) Payouts per month
- **Definition:** per unit, the number of payout arrivals in months 1 to 12 divided by 12, and their cash divided by
  12. A payout belongs to the month its cash arrives in.
- **Summary and unit:**
  - p10, p50 and p90 over `E_252`, with the mean beside.
  - Units: payouts per month, and dollars per month.
- **Per unit; never blank:** both values. Never blank.
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
- **Per unit; never blank:** the per-unit share. Never blank.
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
- **Per unit; never blank:** the per-unit standard deviation. Never blank.
- **Alias:** shares (18)'s monthly changes.
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `evenness`; `vendor/stage2/propedge/research/user_journey.py`,
    `monthly_mean_over_sd`.
  - [B]: `path/sd_monthly_net/p10`, `p50`, `p90`.
  - [BS]: `sd_monthly_net`.
  - [U1]: `luck:monthly_mean_over_sd_p10@252`, `p50@252`, `p90@252`.
- **Parameters:** none.

### (20) Longest run of months without a payout
- **Definition:** the longest run of consecutive months, among months 1 to 12, in which no payout cash arrives. The
  months before the first payout count.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: months.
- **Per unit; never blank:** the per-unit run. Never blank (12 for a unit never paid).
- **Status:** exists
- **Where:**
  - Function: `extended/user_measures.py`, `evenness`.
  - [B]: `path/longest_months_without_payout/p10`, `p50`, `p90`.
  - [BS]: `longest_months_without_payout`.
- **Parameters:** none.

### (21) The user's longest wait for a payout within 126 sessions (S5b beside)
- **Definition (B-6), on every unit of `E_126`:** take the arrival closes `a_1 <= ... <= a_r` at or before 126. The
  wait is the largest difference between consecutive marks of `(0, a_1, ..., a_r, 126)`.
  - The wait to the first payout counts.
  - A unit never paid by 126 has a wait of 126, censored ("beyond", at `W + 1` in the censored form).
  - This is (20)'s convention, in sessions.
- **Summary and unit:**
  - p10, p50 and p90 over `E_126`, censored units beyond.
  - **Beside, never a dimension:** Stage 2's S5b, the longest gap *after* the first payout over the paid units only
    (`payout_rhythm`, p50, p90 and the longest).
  - Unit: sessions.
- **Per unit; never blank:** the wait, with unpaid units at 127. Never blank.
- **Status:** exists
- **Where:**
  - Functions: `extended/journey_measures.py`, `longest_wait` (the wait from day 0 over all of `E_126`, built in Wave
    3.1); `vendor/stage2/propedge/research/user_journey.py`, `payout_rhythm` and `metric_rows` (S5b, Stage 2's form).
  - Journey: `journey/longest_wait/p10`, `p50`, `p90` (unpaid at 127), `share_paid_by_126`.
  - [U1]: `consistency:longest_gap_p50@126`, `longest_gap_p90@126`, `longest_gap_longest@126` (and `@252`).
  - [B]: `scorecard/S5b/value`. E-201 D1 applies, as in (14).
- **Parameters:** none.

### (22) Best quarter's share of month-6 net (S5c)
- **Definition:** over the units of `E_126`, with `x_u = rel_u[126]`: the sum of the `ceil(n/4)` largest `x_u`
  divided by the sum of all `x_u`. It is blank when that total is not above zero.
- **Summary and unit:** one number a design, read on the pooled units and per seed. Unit: a ratio. It is
  ill-conditioned when the total is near zero (E-201's caveat).
- **Per unit; never blank:** **none**: a design-level number that can be blank. Not a composite input unless CHARTER
  3.9's row pins a never-blank form. Readings 1 and 3 only: reading 2 needs a per-unit value (section 1.4).
- **Status:** exists
- **Where:**
  - Function: `vendor/stage2/propedge/research/user_journey.py`, `concentration`.
  - [U1]: `consistency:concentration@126` (and `@63`, `@252`).
  - [B]: `scorecard/S5c/value`.
- **Parameters:** none.

### (23) Largest month's share of the year's payouts
- **Definition:** `max_m cash_m / sum_m cash_m` over months 1 to 12, where `cash_m` is the payout cash arriving in
  month `m`. It is blank when no payout arrives in the year. This is the lump-sum detector of E-014.
- **Summary and unit:** p10, p50 and p90 over the units of `E_252` paid within the twelve months, with **the share paid
  within the twelve months beside**. Unit: a share.
- **Per unit; never blank:** defined on paid units only. Not a composite input unless pinned in a never-blank form.
- **Status:** exists
- **Where:**
  - Function: `extended/user_measures.py`, `evenness`.
  - [B]: `path/largest_month_share/p10`, `p50`, `p90`.
  - [BS]: `largest_month_share`.
- **Parameters:** none.

### Bankroll and downside

### (24) Chance of running out before the first payout (the bankroll stop)
- **Definition (B-3), on all of `E_W`, for each budget `B`:** with `k*_u` as in (6), every unit is in one of three
  states:
  - **paid within `B`:** paid by `W`, with `spent_before(rel_u, first_payout_u) <= B`;
  - **run out:** `spent_before(rel_u, k*_u) > B`, so the spending went above `B` before a first payout by `W`;
  - **censored:** unpaid by `W`, with `spent_before(rel_u, W + 1) <= B`. It is still paying fees, not yet paid, and
    its spending after `W` is unread.
- **The limit reads "not paid within `B` by `W`"**, which is run out plus censored. Each part is reported beside.
- **Beside it, the peak through the window:** the share whose peak out-of-pocket through close `W` exceeds `B`, before
  or after a first payout. That is (25)'s quantity at the window's end (B-2).
- **The stop is read on the replay's own path**, as for `P_B` (section 2; m-12's bias stated there).
- **Summary and unit:** for each `B`, the three shares over `E_W`, read three ways (section 1.4). Unit: shares.
- **Per unit; never blank:** the unit's state. Never blank.
- **Alias:** (6)'s per-unit quantity.
- **Status:** exists
- **Where:**
  - Functions: `extended/journey_measures.py`, `bankroll_state` and `bankroll_stop` (built in Wave 3.1).
  - Journey: `journey/bankroll_stop_{B}/share_paid_within`, `share_run_out`, `share_censored`,
    `share_not_paid_within` (the limit's reading) and `share_peak_over` (the peak form, beside).
  - Not this measure: `extended/user_measures.py`, `share_over_limit`, written to [B] `extra/share_spent_over_2000`
    and `share_spent_over_2500` on the registered blocks only. These count only units *with* a first payout, and
    their spending is read from the long record up to 252 sessions on a 63-session block (B-1's leak). On E-208's
    blocks (24)'s three states replace them.
  - Also: `extended/user_measures.py`, `p_by_month`; `vendor/stage2/propedge/research/customer_journey.py`,
    `spent_before`.
- **Parameters:**
  - `B`: **the bankroll budgets, the lead's, set in Wave 4.2 from H4's search-year results by a rule declared
    before H4 is read** (CHARTER 3.9; E-221).
  - `W`: the search declaration's.

### (25) Peak out-of-pocket in 12 months
- **Definition:** `PeakOOP_u = max(0, -min_{0 <= k <= 252} rel_u[k])`, the deepest the user's own money goes below the
  start over the twelve months. This is Stage 2's `drawdown_from_start` over closes `0 .. 252`.
- **Summary and unit:** p10, p50 and p90 over `E_252`. Unit: dollars.
- **Per unit; never blank:** `PeakOOP_u`. Never blank.
- **Alias:** (24)'s peak form at `W = 252`, and (15)'s denominator.
- **Status:** exists
- **Where:**
  - Functions: `extended/journey_measures.py`, `peak_oop`; `extended/user_measures.py`, `peak_through` (built in Wave
    3.1); the vendored tree's `vendor/stage2/propedge/research/customer_journey.py`, `drawdown_from_start`, is the
    same quantity.
  - Journey: `journey/peak_oop_12_months/p10`, `p50`, `p90`.
  - [SP] `spent_before_break_even` is a different quantity: the peak before break-even only.
- **Parameters:** none.

### (26) Month-3 net of the unlucky tenth (S5a)
- **Definition:** the p10 of `rel_u[63]` over `E_63`.
- **Summary and unit:** one percentile, read three ways. Unit: dollars.
- **Per unit; never blank:** `rel_u[63]` ((12)'s per-unit value). Never blank.
- **Alias:** (12)'s p10 at month 3 (m-4).
- **Status:** exists
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`; `u_select.py`, `scorecard`.
  - [U1]: `periodic:net_p10@63`.
  - [B]: `scorecard/S5a/value`.
  - [BS]: `net_month_3`.
- **Parameters:** none.

### (27) CVaR10
- **Definition:** the mean of the worst `ceil(0.10 n)` month-3 nets `rel_u[63]` over `E_63`.
- **Summary and unit:** one number a design, read on the pooled units and per seed. Unit: dollars.
- **Per unit; never blank:** **none** (a tail mean, design-level). Never blank on a non-empty `E_63`. Readings 1 and 3 only: reading 2 needs a per-unit value (section 1.4).
- **Status:** exists
- **Where:**
  - Functions: `extended/user_measures.py`, `cvar`; `extended/user_readings.py`, `extra_rows`.
  - [B]: `extra/cvar10_net_month_3/value`.
- **Parameters:** the tail share 0.10 is the plan's ("CVaR10").

### Realism and robustness

### (28) Headline measures with 10 % and 20 % of signals missed or late
- **Definition:** two stress arms, each at `q = 0.10` and `q = 0.20`, run against the base design and paired on the
  same units and seeds:
  - **Missed:** each signal the design's schedule offers is independently not taken, with probability `q`, and the
    rest of the path is re-simulated.
  - **Late:** each signal is independently entered late by the delay `d`, with probability `q`, and re-priced from
    the bars at the late entry (`feature-rules`).
  - The draws come from a declared seed stream per unit. They are common random numbers across the designs and
    baselines compared, under the same stress (CHARTER 3.8 (c)).
- **Summary and unit:** each headline measure in its own summary and unit, for each arm and `q`.
- **Per unit; never blank:** each headline measure's own forms.
- **Status:** to build
- **Where:** nothing computes it.
- **Parameters:** `q`, the plan's (the operator's); the delay `d`, the seed stream and the headline set, from the
  search declaration (Wave 5) and Wave 4.

### (29) Headline measures at one and two ticks of worse fills
- **Definition:** every fill made one tick, then two ticks, worse than the base design's, for the design and for each
  baseline alike, with the headline measures reported for each. Which fills move (entry, stop, target, time exit) is
  Q-148's declaration.
- **Summary and unit:** each headline measure in its own summary and unit, at +1 and +2 ticks.
- **Per unit; never blank:** each headline measure's own forms.
- **Status:** to build. This is Q-148 in `wt-verify` (approved item 2). Stage 2's precedent is `p16_slip_stress.csv`
  (D-583 to D-585).
- **Where:** nothing in this repository computes it on the journey.
- **Parameters:** the fills affected and the headline set: Q-148's declaration and Wave 4.

### (30) Workload: orders a day, accounts at once, screen hours
- **Definition:** for each session `d` of a unit:
  - `orders_d` is the number of trades entered across all accounts. One entry ticket counts as one order, with its
    attached bracket.
  - `accounts_d` is the number of accounts live at close `d` (a Combine trading or a funded account open).
  - `screen_d` is the hours covered by the union, over the session's trades, of [alert time, exit time]. The alert
    time is entry less the order latency L.
- **Summary and unit:**
  - Per unit: the mean and the maximum of each quantity over its observed sessions.
  - Then p10, p50 and p90 over `E_h`.
  - Units: orders per session, accounts, and hours per session.
- **Per unit; never blank:** the per-unit means and maxima. Never blank. A session with `accounts_d = 0` has
  `orders_d = 0` and `screen_d = 0`.
- **Status:** partial
- **To build:** the feed from the replay's trade records to `workload`'s per-session input (each session's live
  accounts and its trades' entry and exit minutes), and its rows (the seed-paired runner, Wave 3.2).
- **Where:**
  - Function: `extended/journey_measures.py`, `workload` (built in Wave 3.1, on that input).
  - Ingredient: `extended/replay_records.py`, `ReplayRecorder` (each trade's account, place and booking on the
    replay).
- **Parameters:**
  - L: the declaration's searched lever (E-202 (2)(c); CHARTER 3.3 (g)).
  - The horizon `h`: the declaration's.
  - Workload is reported. A ceiling applies only if the pinning row sets one as a limit (CHARTER 3.5, 3.9; E-221).

### (31) Funded-account lifetime: payouts per funded account before it is lost
- **Definition (B-7):** for each funded account activated within a unit's observed window, its count of payouts whose
  cash arrived before it ended.
  - An account that ends by a firm rule (lost) is an observed lifetime: the event.
  - **Every other ending is censored at its count, and named in the reading (v2 m-6):**
    - **a policy closure** -- the design's account policy closes or abandons the account, not the firm;
    - **a move to Live** -- the firm moves the account to a live account, so the funded account ends without a loss;
    - **a payout cap** -- the account ends because it reached the firm's payout cap or maximum payout count;
    - **the window's end** -- the account is still open.
  - Each censored ending's count is reported beside, by kind. A builder that finds another way an account ends names
    it and censors it, unless a row declares it a loss. None of these endings is counted as a loss or dropped.
- **The estimate is Kaplan-Meier-style**, in payouts (and, beside, in sessions alive): the survival curve `S(k)`, the
  chance that a funded account reaches its `k`-th payout before it is lost, with censored accounts leaving the risk
  set at their count. Read from it:
  - the median payouts before loss and the p10 and p90, each read off `S` and reported "beyond" where `S` does not
    fall that far;
  - beside it, **the censored count** and its share.
- **Weighting:** pooled over accounts, **each unit weighted equally**. An account of a unit holding `A_u` funded
  accounts carries weight `1 / A_u`. Otherwise designs with many accounts dominate the pooled curve.
- **Summary and unit:** as above. Unit: payouts per funded account (sessions beside).
- **Per unit; never blank:** **none** (a curve over accounts). Not a composite input unless pinned in a never-blank
  form. Readings 1 and 3 only: reading 2 needs a per-unit value (section 1.4).
- **Status:** exists
- **How the engine's endings are named (Wave 3.1, for a row to confirm):** a breach of the floor, a tier-3 denial's
  closure and the Focused Trader Program's closure are endings by a firm rule, so the event; the policy's abandon is a
  policy closure; the household rule (R7, the firm moving the account live) is a move to Live; an account still open
  at the window's end, and one reaching the engine's own horizon, are censored. The vendored engine has no
  payout-cap ending for Topstep. A payout counts when its cash arrives strictly before the account's end close; for an
  open account, by close W.
- **Where:**
  - Functions: `extended/journey_measures.py`, `account_ending`, `account_lifetime`, `km_survival`, `km_quantile` and
    `funded_lifetime` (built in Wave 3.1), on the journey's `accounts` field (`extended/user_beside.py`,
    `journey_record`, from the engine's funded records as `response_record` reads them).
  - Journey: `journey/funded_lifetime_payouts/p10`, `p50`, `p90` (blank: beyond), `n_accounts`, `n_units`, `n_lost`,
    `n_censored`, `share_censored`, `share_censored_weighted`, `censored_{kind}`, `lost_{kind}`;
    `journey/funded_lifetime_sessions/p10` .. (beside).
  - Ingredient elsewhere: `extended/replay_records.py`, `ReplayRecorder` (its accounts frame).
- **Parameters:** the window: the declaration's.

### (32) Worst year and highest-volatility period
- **Definition:** each headline measure is read on two kinds of subset of the search years.
  - **Each start year `y`:** the units of `E_h` whose start date falls in `y`. The reading reports the worst value in
    the measure's bad direction, and its year.
  - **The highest-volatility period:** the units whose start day falls in the period a rule on **search-year data
    only** defines (RD-04's volatility units; `extended/vol_descriptive.py` refuses later days; RD-04 (c) is a held-out
    read ledger entry).
- **The embargoed year is recorded (m-9).** Under the horizon embargo (section 1.1), 2023 contributes no start at 252
  sessions, so at the 12-month horizon "the worst year" covers 2020 to 2022 only. Each reading's manifest records the
  year set read at each horizon.
- **Designs are compared on one year set.** A worst-of-years statistic grows with the count of years, so every design
  and baseline in a comparison is read on the same years.
- **Summary and unit:** each headline measure in its own summary and unit, on each subset.
- **Per unit; never blank:** each headline measure's own forms, on the subset.
- **Status:** partial
- **To build:** the headline set (Wave 4) and the volatility rule (RD-04, search-year data only) that feed the two
  readings, and their rows.
- **Where:**
  - Functions: `extended/journey_measures.py`, `by_year` (each start year, the worst and its year, the year set
    recorded) and `subset_reading` (the period's units, from the rule's own mask), built in Wave 3.1.
  - Ingredients: `vendor/stage2/propedge/research/u_select.py`, `START_YEARS` (and its `year_rule`); [U1]
    `luck:share_paid_by@21[year]` (S3a by start year).
- **Parameters:** the volatility rule and its period (RD-04 and the search declaration, from search-year data only),
  and the headline set (Wave 4).

### (33) Break-even denial rate
- **Definition (m-2):** under the engine's tier-3 denial model at enforcement probability `p` (`ConductModel
  (enforcement_p = p)`; `extended/user_beside.py`, responses of kind `denial`), with the start seeds common random
  numbers across `p`:
  - **"Making money"** means the median user's 12-month net is above zero. Equivalently, S4b, the share of `E_252`
    ahead at month 12, is above one half: `M(p) = S4b(p) - 1/2`.
  - `M(p)` is not guaranteed to be monotone, since a denial closes accounts and changes the path. So **`p*` is the
    first crossing in grid order**: the first grid point with `M(p) <= 0`, refined by linear interpolation between it
    and the grid point before it.
  - If `M(0) <= 0`, then `p* = 0`.
  - If `M` stays above zero across the grid, `p*` is reported as **"untested beyond the grid"**, not as robust.
- **Beside it:**
  - the share of payouts exposed (`payouts_exposed / payouts_requested`). A design that never shows the stacking
    pattern is untested, not robust.
  - the same rate on the pooled mean 12-month net;
  - once CHARTER 3.9 pins the composite, the rate at which the design's composite falls to the best baseline's.
- **Summary and unit:** one probability a design. It is **reported, never a limit** (plan section 3). The verdict
  stays at 0 % (CHARTER 3.8).
- **Per unit; never blank:** none (design-level). Readings 1 and 3 only: reading 2 needs a per-unit value (section 1.4).
- **Status:** partial
- **To build:** the ladder on the coin path. The ladder's ingredient refuses any design with a flip stream
  (`extended/user_beside.py`, `base_problems`). Under CHARTER 3.2 every design has a coin, so the ladder serves only
  once the enforcement stream is seeded apart from the coin (still to change, section 6).
- **Where:**
  - Functions: `extended/journey_measures.py`, `break_even_denial_rate` (the first crossing, `p* = 0`, "untested beyond
    the grid") and `exposed_share`, built in Wave 3.1, reading a ladder already run.
  - Ingredients (the existing ladder):
  - `extended/user_beside.py`, `RESPONSES` and `DENIAL_LEVELS` (the existing ladder: 10 %, 25 % and 50 %, plus the
    all-accounts forfeiture arms), and `start_seed`;
  - [B] and [BS] at `response` = `denial_10`, `denial_25`, `denial_50`.
- **Parameters:** the grid of `p`: the search declaration.

### (34) Luck against design (S6)
- **Definition (Stage 2's, D-620):**
  - the standard deviation of the net across units at months 1, 3, 6 and 12;
  - the standard deviation of the designs' mean nets, which needs every design compared, and each design's ratio of
    the first to the second;
  - each unit's mean monthly change over its standard deviation (p10, p50, p90);
  - the share paid by session 21 by start year.
- **Added here: the coin layer's decomposition, by the ANOVA estimator (m-5).** For each headline measure's per-unit
  value `x_{s,c}`, with `n_c` seeds:
  - `within = mean_s var_c x_{s,c}`;
  - `between = var_s mean_c x_{s,c} - within / n_c`, which removes the bias of the start-day means' variance at few
    seeds;
  - the start day's share, `between / (between + within)`. It is truncated at zero when the estimate is negative, with
    the untruncated value beside. This is E-015 (1)'s "start day's share of the variance".
  - Beside them: section 1.4's three readings and its `n_eff`.
- **Summary and unit:** as listed; dollars, ratios and shares.
- **Per unit; never blank:** none (design-level decompositions). Readings 1 and 3 only: reading 2 needs a per-unit value (section 1.4).
- **Status:** partial
- **Where:**
  - Functions: `vendor/stage2/propedge/research/user_journey.py`, `metric_rows`, `luck_rows` and
    `monthly_mean_over_sd`; `extended/user_measures.py`, `n_eff_bartlett`.
  - [U1]: `luck:sd_net_across_starts@{21,63,126,252}`, `luck:sd_of_configuration_means@...`,
    `luck:sd_across_starts_over_sd_of_configuration_means@...`, `luck:monthly_mean_over_sd_p{10,50,90}@252`,
    `luck:share_paid_by@21[year]`.
  - [B]: `extra/n_eff_bartlett/value`, `extra/n_nonoverlapping/value`.
- **Built in Wave 3.1:** the ANOVA decomposition (`extended/journey_measures.py`, `variance_decomposition`) and
  section 1.4's three readings (`coin_readings`, `design_coin_readings`).
- **To build:** the seed-paired runner that feeds them (plan Wave 3.2).
- **Parameters:** the coin seeds: the declaration's.

### The baseline set (comparators, not measures)

The baselines are comparators: every measure above is read on each of them, under the design's convention, and a
design must beat **each** of them (CHARTER 3.8 (b)). Their statuses describe runs, not definitions (m-3).

### (35) Naive coin harvesting
- **Definition (B-5):** the comparator whose signal source is the naive coin, with **its levers fixed in the search
  declaration** (CHARTER 2, terms). They are not copied from each design: a comparator that moves with the design
  would be a different hypothesis from the one pinned.
  - It is read on the same units and the same seeds as the designs, under CHARTER 3.2's reflection and
    martingale-outcome reading, with the same fill and cost mechanics, no arm shift and the same verdict settings.
  - Its source (timing, shape, sessions) is built by `wt-levels` (plan Wave 3.3).
- **Summary and unit:** each measure in its own summary and unit.
- **Per unit; never blank:** each measure's own forms.
- **Status:** comparator. Its run is to build (`wt-levels`' naive coin source, at H4).
- **Where:** nothing computes it. Stage 2's coin designs P-15 and P-16 are in (36), not this one.
- **Parameters:** the levers fixed in the search declaration (Wave 5), H4's seeds.

### (36) P-14, P-15 and P-16
- **Definition (B-5):** the three registered Stage 2 designs, each run **under the design's convention**:
  - CHARTER 3.2's reflection and martingale-outcome reading, on the declaration's seeds, so P-14 is coin-driven too;
  - the same fill and cost mechanics;
  - each at its **registered latency** (P-14 at five minutes; P-16 scheduled), its runner's identity checking that its
    trade times and brackets equal its registered ones, path for path (CHARTER 3.8 (b)).
  - **U1's replays are the registered rows, reported beside**, never the comparator.
  - The deciding reading is the martingale-outcome reading. The as-walked and as-traded readings are beside.
  - P-14 is one baseline among four. R\* = P-14 is retired (CHARTER 3.10).
- **Summary and unit:** each measure in its own summary and unit.
- **Per unit; never blank:** each measure's own forms.
- **Status:** comparator. The registered rows exist; the convention's runs are to build (H4).
- **Where:**
  - Functions: `extended/user_beside.py`, `run_starts` (designs `p14`, `p15` and `p16`; the old input path, section
    1.5); `vendor/stage2/propedge/research/u_select.py`, `ROWS_TO_BEAT` (Stage 2's three, now each a baseline).
  - [B] and [BS]: `design` = `p14`, `p15`, `p16`.
  - [U1]: `config` = `p14`, `p15`, `p16`.
- **Parameters:** H4's seeds, from its declaration. Stage 2 chose these designs on the whole development window, so
  for them "held out" means unread by this search only (E-208), and it is stated beside every comparison.

### Supply and speed

### (37) Trades available per day, per account and in total
- **Definition (m-12):** for each session `d` of a unit:
  - `offered_d` is the number of trades the design's component schedule offers. These are the signals that fire,
    before account states and the one-position-at-a-time rule.
  - `taken_d` is the number of trades entered across all accounts.
  - `taken_per_account_d = taken_d / accounts_d`, with `accounts_d` as in (30). It is defined only on sessions with
    `accounts_d >= 1`.
- **Summary and unit:**
  - Per unit: the mean of each quantity over its observed sessions; for `taken_per_account`, over the sessions with an
    account live, with the count of sessions without one beside.
  - Then p10, p50 and p90 over `E_h`.
  - Unit: trades per session.
  - `offered_d` depends only on the calendar date, so its spread across start days is the calendar's.
- **Per unit; never blank:** the means of `offered` and `taken`. `taken_per_account` is blank only for a unit with no
  account ever live, which cannot happen after a day 0 purchase.
- **Status:** partial
- **To build:** the feed from the replay's offer and trade records to `supply`'s per-session input, and its rows
  (Wave 3.2).
- **Where:**
  - Function: `extended/journey_measures.py`, `supply` (built in Wave 3.1, on that input).
  - Ingredient: `extended/replay_records.py`, `ReplayRecorder` (each trade's offer and place).
- **Parameters:** the horizon `h`: the declaration's.

### (38) Session coverage
- **Definition (m-12):** for each session window `w` in {Asia, London, NY AM, NY PM}, per unit: the share of its
  observed trading days with at least one trade taken whose entry time falls in `w`. Beside it, the same share for
  trades offered.
  - **The trading day** is the firm's: for Topstep it opens at 17:00 CT on the evening before the session's date and
    runs to the firm's daily flat time, both from its verified rules (`vendor/stage2/config/rules.yaml`).
  - An Asia entry belongs to the trading day it opens, the date after the evening it falls on.
- **Summary and unit:** p10, p50 and p90 over `E_h`, for each window. Unit: a share.
- **Per unit; never blank:** the per-unit shares. Never blank.
- **Status:** partial
- **To build:** the session windows' declaration (`wt-levels`, Wave 3.3), the feed from the replay's records, and its
  rows.
- **Where:**
  - Functions: `extended/journey_measures.py`, `coverage`, `trading_day_of` (a moment as its trading day and minutes
    after the reopen; an evening entry belongs to the next date) and `firm_day` (the reopen and the flat from the
    verified `trading_hours`, through `extended/lever_space.py`, `trading_day`), built in Wave 3.1.
- **Parameters:**
  - The windows' boundaries: the trigger library's declaration (`wt-levels`, plan Wave 3.3), inside the hours the
    firm allows.
  - The horizon `h`: the declaration's.

### (39) Longest idle stretch inside the firm's trading day
- **Definition (m-12):** for each trading day of a unit (as in (38)), the longest interval inside it during which no
  account holds a position.
  - **News-barred windows** (E-202 (2)(a); CHARTER 4) count as idle. The same measure with them taken out (the
    longest stretch in which the user could have traded and did not) is reported beside.
  - Beside it, the same measure on offered signals: the longest interval with no signal.
- **Summary and unit:**
  - Per unit: the median and the maximum over its days.
  - Then p10, p50 and p90 over `E_h`.
  - Unit: minutes.
- **Per unit; never blank:** the per-unit median and maximum. Never blank (a day with no trade is idle throughout).
- **Status:** partial
- **To build:** the feed from the replay's records and the verified news windows, and its rows.
- **Where:**
  - Function: `extended/journey_measures.py`, `idle` (built in Wave 3.1: the idle form, the tradeable form with the
    news windows out, and the no-signal form).
- **Parameters:** the firm's trading-day hours and news windows, from its verified rules only
  (`vendor/stage2/config/rules.yaml`; `config/rules_extended.yaml` through `extended/firm_terms.py`); the horizon `h`,
  the declaration's.

---

## 5. Dropped by the operator

- **Firm-rule exposure** (the flagged-pattern rate): dropped (plan section 3). It is not a measure. Conduct tier 1 stays
  a floor, and the firm responses stay the denial ladder of (33).
- **Rule-change sensitivity**: dropped (plan section 3).

---

## 6. Code changed in Wave 3.1, and code still to change

Each line is checked by the test: the file exists and the quoted text is at or just after the line given. For each
changed line the test also checks that the text it replaced is gone.

**Changed in Wave 3.1.**

- `extended/user_beside.py:732` (`L = min(U.HORIZON, n - s) if not jour else min(U.HORIZON, blk_last[s] - s + 1)`):
  **changed (B-1).** Was `L = min(U.HORIZON, n - s)`, which counted sessions to the end of the development window. With
  `run_starts(..., journey=True)` the long run stops at the last session of the start's block, and the runner refuses a
  calendar with a date in neither block and any run reading a session of another block. Absent, the adapter is the one
  before, bit for bit (`tests/test_journey_readings.py`), so every registered reading and identity that runs it is
  unchanged.
- `extended/user_beside.py:750` (`jr = ({"journey": journey_record(s, blk[s], blk_last[s], long_run, lag, rel)}`):
  **changed (B-2).** The peak out-of-pocket through each month close (`peak_month`, by `user_measures.peak_by_month`) is
  made here from `rel`, where `M.daily(rel)` is made, with `rel` itself, and carried to the start table
  (`user_readings.PEAK_COLS`). It is what `P_B` and (24)'s peak form pass.
- `extended/user_readings.py:300` (`q = M.p_by_month(nets, spent=pk, limit=float(lim))`): **changed (B-2).** On
  E-208's blocks `P_B` passes the peak through each month close. Its sub-reading passes the spending before the first
  payout, read on closes `0 .. 21 m`. The registered blocks keep `P_bankroll_*`, which section 2 names as that
  sub-reading.
- `extended/journey_readings.py:100` (`stop = J.bankroll_stop(`): **changed (B-1, B-3).** On E-208's blocks (24)'s
  three states replace `share_spent_over_*` (from `extended/user_readings.py:183-189` before), read from closes `0 .. W`
  of each journey; the section `journey` is this new module's, so `user_readings` imports nothing new. The registered
  blocks keep the old rows.
- `extended/user_readings.py:206` (`if block in E208_BLOCKS:`): **changed (B-1).** In `_elig`, a block of E-208 means
  `E_h` inside the block: its journeys with at least h sessions observed, the run itself bounded. A table that is not
  of journeys is refused. The registered blocks are unchanged.
- `extended/user_readings.py:72` (`BLOCKS = ("search",)`): **changed (B-1).** Was `BLOCKS = ("all", "judged")`. The
  default everywhere is now the search years, and on outputs that are not journeys it refuses. A held-out reading names
  `held_out`. Q-44's blocks are `Q44_BLOCKS`, which every caller that reproduces a registered reading now names
  (`scripts/user_beside.py`, `scripts/breakeven_fidelity.py`, `scripts/breakeven_fidelity_2.py`, `scripts/fo_opening.py`,
  `extended/breakeven_readings.py`, `extended/journey_page.py`, `extended/opening_journey.py`, `extended/user_spend.py`
  and three test helpers), so their rows are as before.
- `extended/user_readings.py:428` (`abs(mine - float(np.mean(shares))) > 1e-12 or mine > card + 1e-12`): **changed
  (m-11).** Was `abs(card - mine) <= 1e-12`. The check compares like with like: this repository's P equals the mean of
  its own three month shares, on the card's starts. Stage 2's card is read beside: the new P is never above it (a net
  above 1e-6 is above 0) and never held equal to it. `extended/opening_journey.py`, `choice_problems`, held the same
  equality and follows the same rule.
- `extended/user_measures.py:77` (`ahead = x[ok] > TOL`): **changed (m-11).** Was `ahead = x[ok] > 0`.
- `extended/user_measures.py:96` (`c = (x > TOL).sum(axis=1)`): **changed (m-11).** Was `c = (x > 0).sum(axis=1)`.
  `months_ahead` and `p_by_month` agree.
- `extended/user_measures.py:219` (`def days_quantile(first: np.ndarray, window: int, p: float, *, censored: bool = False)`):
  **changed (1.3).** `days_quantile` gains the censored form (`censored=True`, through `censored_days`: an unreached
  unit at `W + 1`, never blank), the headline on E-208's blocks. Its default, with `BEYOND`, is Stage 2's blanking
  form, kept beside.

**Still to change.**

- `extended/user_beside.py:374` (`args["draws"].get("flip") is not None`): **to change (m-2).** The ladder refuses a
  design with a flip stream. Under CHARTER 3.2 every design has a coin, so the enforcement stream must be seeded apart
  from the coin first. That is the seed-paired runner's (Wave 3.2): the path seed drives both streams in the vendored
  engine, which is not edited.

**A note outside this file's scope (B-1's pattern).** Other runners use the same whole-window run length. Any of them
that feeds a measure for a search needs B-1's fix too: the run stops at the block's last outcome session. Each is
listed so the pattern is not copied; the test checks that each line is where it says.

- `extended/firm_reading.py:258` (`min(U.HORIZON, len(job["blocks"]) - int(start))`): to change if reused (B-1).
- `extended/openings.py:519` (`L = min(U.HORIZON, n - s)`): to change if reused (B-1).
- `extended/opening_wait.py:519` (`min(U.HORIZON, n - s_)`): to change if reused (B-1).
- `extended/cl_reading.py:485` (`min(HORIZON, n - s)`): to change if reused (B-1).

---

## 7. Held-out read ledger entries this file carries (m-10)

These constants and readings were set or read with the held-out years (the `judged` block, 2024 on) visible. Every
search declaration that uses one carries it in its held-out read ledger (CHARTER 3.6 (b), RD-04's leak-clause form:
"written after this reading; no figure cited"). A pinned budget, limit or window (E-221) that lands on one of them is
recorded as such.

| constant or reading | where | origin row | read with the held-out years visible |
|---|---|---|---|
| Q-17's bankroll limits, $2,000 and $2,500 | `extended/user_readings.py`, `BANKROLL_LIMITS` | Q-17 (E-024); read in Q-44 (E-201) | yes: [B] was read on the `judged` block |
| the first-pass and first-payout window, 126 sessions | `extended/user_readings.py`, `FIRST_WINDOW`; U1's `PAYOUT_WINDOW` | Stage 2 D-518, D-620; Q-44 (E-201) | yes: U1 and [B] read the whole window |
| the year window, 252 sessions | `extended/user_readings.py`, `YEAR_WINDOW`; U1's `HORIZON` | Stage 2 D-620; Q-44 (E-201) | yes |
| the n_eff lag, 63 sessions | `extended/user_readings.py`, `N_EFF_LAG` | Q-17 (E-024) | yes |
| the break-even months 1, 2, 3, 6, 12 | `extended/user_readings.py`, `BREAK_EVEN_MONTHS` | Q-17 (E-024) | yes |
| U1's pass window 42 and its percentile lists | `vendor/stage2/propedge/research/user_journey.py` | Stage 2 D-620 | yes |
| every [B], [BS] and [U1] reading | the three files | E-201; Stage 2 D-620 | yes: whole development window |
| [SP] once written | `results/user_spend.csv` | Q-86 | it would read the whole window as built (B-1) |

A window, limit or budget proposed for a search is set from the search years (CHARTER 3.9). A coincidence with a value
above is reported, not assumed harmless.

---

## 8. The index (machine-read by `tests/test_measures_doc.py`)

Status:
- `exists`: every part defined is computed by code today, on the old input path (section 1.5);
- `partial`: part exists and part is to build;
- `to build`;
- `comparator`: a member of the baseline set, (35) and (36).

**How a reference is checked.** A reference in the code or names column is `path::Name`, which must be a top-level
function, class or assignment, or `Class.method`, in that file. A reference `path::CONST[item]` requires `item` to be
an element of the literal constant (for a tuple of calls, their first arguments). A reference `path::"text"` requires
the text to occur in the file. For a `to build` row and a comparator, the references are ingredients, and they are
checked the same way.

<!-- measures-index:start -->
| # | measure | status | code | names |
|---|---|---|---|---|
| 1 | Sessions to the first evaluation pass | exists | `extended/user_measures.py::days_quantile`; `extended/user_measures.py::censored_days`; `extended/journey_measures.py::days_reading`; `extended/user_readings.py::path_rows`; `extended/user_readings.py::FIRST_WINDOW` | `extended/user_readings.py::START_COLS[first_pass]`; `vendor/stage2/propedge/research/user_journey.py::PASS_DAYS[42]`; `extended/user_readings.py::"stage2_p"` |
| 2 | Cash to the first pass | exists | `extended/user_readings.py::path_rows`; `vendor/stage2/propedge/research/user_journey.py::start_record`; `vendor/stage2/propedge/research/customer_journey.py::spent_before`; `extended/user_spend.py::spend_record`; `extended/journey_measures.py::spent_to_event`; `extended/journey_measures.py::strict_quantiles`; `extended/journey_readings.py::journey_rows` | `extended/user_readings.py::START_COLS[spent_before_first_pass]`; `extended/user_spend.py::"fees_at_first_pass"`; `extended/journey_readings.py::"cash_to_first_pass"` |
| 3 | Evaluations bought before the first pass | exists | `extended/user_spend.py::spend_record`; `extended/user_spend.py::SUMMARY_MEASURES`; `extended/journey_measures.py::evaluations_to_first_pass` | `extended/user_spend.py::"evaluations_before_first_pass"`; `extended/user_spend.py::"resets_before_first_pass"`; `extended/journey_readings.py::"evaluations_before_first_pass"` |
| 4 | Share of starts passed by session 21 | exists | `vendor/stage2/propedge/research/user_journey.py::stats` | `vendor/stage2/propedge/research/user_journey.py::PASS_DAYS[21]` |
| 5 | Sessions to the first payout (S3b) | exists | `extended/user_readings.py::path_rows`; `extended/user_measures.py::days_quantile`; `vendor/stage2/propedge/research/u_select.py::scorecard` | `extended/user_readings.py::START_COLS[first_payout]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S3b]` |
| 6 | Cash spent before the first payout: the bankroll needed (S1) | exists | `extended/user_readings.py::path_rows`; `vendor/stage2/propedge/research/user_journey.py::start_record`; `vendor/stage2/propedge/research/customer_journey.py::spent_before`; `extended/journey_measures.py::spent_to_event`; `extended/journey_measures.py::strict_quantiles` | `extended/user_readings.py::START_COLS[spent_before_first_payout]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S1]`; `extended/journey_readings.py::"spent_before_first_payout_all"` |
| 7 | The first payout's size (S3d) | exists | `extended/user_spend.py::u1_money`; `vendor/stage2/propedge/research/user_journey.py::start_record`; `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `extended/user_spend.py::"first_payout_day_cash"`; `vendor/stage2/propedge/research/user_journey.py::RECORD_KEYS[first_payout_cash]`; `vendor/stage2/propedge/research/user_journey.py::"cash_p"` |
| 8 | Share of starts paid by session 21 (S3a) | exists | `vendor/stage2/propedge/research/user_journey.py::stats`; `vendor/stage2/propedge/research/u_select.py::scorecard` | `vendor/stage2/propedge/research/user_journey.py::PAYOUT_DAYS[21]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S3a]` |
| 9 | Sessions to break-even | exists | `extended/user_measures.py::break_even_day`; `extended/user_measures.py::days_quantile`; `extended/user_readings.py::path_rows`; `extended/user_readings.py::BREAK_EVEN_MONTHS` | `extended/user_readings.py::START_COLS[break_even_day]`; `extended/user_readings.py::"break_even_days"` |
| 10 | Share falling back below break-even | exists | `extended/user_measures.py::fell_back`; `extended/user_readings.py::path_rows` | `extended/user_readings.py::START_COLS[fell_back]`; `extended/user_readings.py::"share_fell_back"`; `extended/user_spend.py::"break_even_lost"` |
| 11 | Deepest fall after break-even | exists | `extended/user_measures.py::deepest_fall_after`; `extended/user_readings.py::path_rows` | `extended/user_readings.py::START_COLS[deepest_fall_after_break_even]` |
| 12 | Net cash at months 1, 2, 3, 6 and 12 | exists | `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `extended/user_readings.py::START_COLS[net_month_1]`; `extended/user_readings.py::START_COLS[net_month_6]`; `extended/user_readings.py::START_COLS[net_month_12]`; `vendor/stage2/propedge/research/user_journey.py::PERIODIC_MONTHS[6]`; `vendor/stage2/propedge/research/user_journey.py::NET_PERCENTILES[10]` |
| 13 | P, and the shares ahead at months 6 and 12 (S4a, S4b) | exists | `extended/user_measures.py::p_by_month`; `extended/user_measures.py::months_ahead`; `extended/user_measures.py::peak_by_month`; `extended/journey_measures.py::p_bankroll`; `extended/journey_measures.py::months_ahead_under`; `extended/journey_measures.py::share_ahead_at`; `vendor/stage2/propedge/research/u_select.py::scorecard`; `vendor/stage2/propedge/research/u_select.py::p_of`; `extended/user_readings.py::extra_rows` | `extended/user_readings.py::START_COLS[months_ahead]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[P]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S4a]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S4b]`; `extended/user_readings.py::"P_bankroll_"`; `extended/user_readings.py::"P_B_"`; `extended/user_readings.py::PEAK_COLS` |
| 14 | Payouts per fee dollar (S3c) | exists | `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `vendor/stage2/propedge/research/user_journey.py::"payouts_per_fee_dollar_pooled"`; `vendor/stage2/propedge/research/user_journey.py::MONEY_BACK_MONTHS[3]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S3c]` |
| 15 | Return on money at risk | exists | `extended/journey_measures.py::return_on_money_at_risk` | `extended/journey_readings.py::"return_on_money_at_risk"` |
| 16 | Monthly net in months 4-12 | exists | `extended/journey_measures.py::monthly_net_4_12`; `extended/journey_measures.py::monthly_changes` | `extended/user_readings.py::START_COLS[net_month_3]`; `extended/user_readings.py::START_COLS[net_month_12]`; `extended/journey_readings.py::"monthly_net_4_12_median"` |
| 17 | Payouts per month | exists | `extended/user_measures.py::evenness`; `extended/user_readings.py::path_rows` | `extended/user_readings.py::START_COLS[payouts_per_month]`; `extended/user_readings.py::START_COLS[payout_cash_per_month]` |
| 18 | Share of months with a positive net change | exists | `extended/user_measures.py::evenness` | `extended/user_readings.py::START_COLS[share_months_positive]` |
| 19 | Spread of monthly net | exists | `extended/user_measures.py::evenness`; `vendor/stage2/propedge/research/user_journey.py::monthly_mean_over_sd` | `extended/user_readings.py::START_COLS[sd_monthly_net]` |
| 20 | Longest run of months without a payout | exists | `extended/user_measures.py::evenness` | `extended/user_readings.py::START_COLS[longest_months_without_payout]` |
| 21 | The user's longest wait for a payout within 126 sessions (S5b beside) | exists | `extended/journey_measures.py::longest_wait`; `vendor/stage2/propedge/research/user_journey.py::payout_rhythm`; `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `extended/journey_readings.py::WAIT_WINDOW`; `vendor/stage2/propedge/research/user_journey.py::GAP_WINDOWS[126]`; `vendor/stage2/propedge/research/user_journey.py::"longest_gap_p"`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S5b]` |
| 22 | Best quarter's share of month-6 net (S5c) | exists | `vendor/stage2/propedge/research/user_journey.py::concentration`; `vendor/stage2/propedge/research/user_journey.py::metric_rows` | `vendor/stage2/propedge/research/user_journey.py::CONCENTRATION_MONTHS[6]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S5c]` |
| 23 | Largest month's share of the year's payouts | exists | `extended/user_measures.py::evenness` | `extended/user_readings.py::START_COLS[largest_month_share]` |
| 24 | Chance of running out before the first payout (the bankroll stop) | exists | `extended/journey_measures.py::bankroll_state`; `extended/journey_measures.py::bankroll_stop`; `extended/user_measures.py::share_over_limit`; `extended/user_measures.py::p_by_month`; `vendor/stage2/propedge/research/customer_journey.py::spent_before` | `extended/user_readings.py::"share_spent_over_"`; `extended/journey_readings.py::"bankroll_stop_"`; `extended/journey_measures.py::STATES[run_out]` |
| 25 | Peak out-of-pocket in 12 months | exists | `extended/journey_measures.py::peak_oop`; `extended/user_measures.py::peak_through`; `vendor/stage2/propedge/research/customer_journey.py::drawdown_from_start` | `extended/journey_readings.py::"peak_oop_12_months"` |
| 26 | Month-3 net of the unlucky tenth (S5a) | exists | `vendor/stage2/propedge/research/user_journey.py::metric_rows`; `vendor/stage2/propedge/research/u_select.py::scorecard` | `extended/user_readings.py::START_COLS[net_month_3]`; `vendor/stage2/propedge/research/u_select.py::MEASURES[S5a]` |
| 27 | CVaR10 | exists | `extended/user_measures.py::cvar`; `extended/user_readings.py::extra_rows` | `extended/user_readings.py::"cvar10_net_month_3"` |
| 28 | Headline measures with 10 % and 20 % of signals missed or late | to build | — | — |
| 29 | Headline measures at one and two ticks of worse fills | to build | — | — |
| 30 | Workload: orders a day, accounts at once, screen hours | partial | `extended/journey_measures.py::workload`; `extended/replay_records.py::ReplayRecorder` | — |
| 31 | Funded-account lifetime: payouts per funded account before it is lost | exists | `extended/journey_measures.py::funded_lifetime`; `extended/journey_measures.py::km_survival`; `extended/journey_measures.py::km_quantile`; `extended/journey_measures.py::account_ending`; `extended/journey_measures.py::account_lifetime`; `extended/user_beside.py::journey_record`; `extended/user_beside.py::response_record`; `extended/replay_records.py::ReplayRecorder` | `extended/journey_measures.py::LOST[breach]`; `extended/journey_measures.py::CENSORED[window]`; `extended/journey_readings.py::"funded_lifetime_payouts"` |
| 32 | Worst year and highest-volatility period | partial | `extended/journey_measures.py::by_year`; `extended/journey_measures.py::subset_reading`; `vendor/stage2/propedge/research/u_select.py::START_YEARS`; `vendor/stage2/propedge/research/u_select.py::year_rule` | — |
| 33 | Break-even denial rate | partial | `extended/journey_measures.py::break_even_denial_rate`; `extended/journey_measures.py::exposed_share`; `extended/user_beside.py::RESPONSES`; `extended/user_beside.py::DENIAL_LEVELS`; `extended/user_beside.py::start_seed`; `extended/user_beside.py::base_problems` | — |
| 34 | Luck against design (S6) | partial | `vendor/stage2/propedge/research/user_journey.py::metric_rows`; `vendor/stage2/propedge/research/user_journey.py::luck_rows`; `vendor/stage2/propedge/research/user_journey.py::monthly_mean_over_sd`; `extended/user_measures.py::n_eff_bartlett`; `extended/journey_measures.py::variance_decomposition`; `extended/journey_measures.py::coin_readings`; `extended/journey_measures.py::design_coin_readings` | `vendor/stage2/propedge/research/user_journey.py::LUCK_MONTHS[12]`; `extended/user_readings.py::"n_eff_bartlett"` |
| 35 | Naive coin harvesting | comparator | — | — |
| 36 | P-14, P-15 and P-16 | comparator | `extended/user_beside.py::run_starts`; `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT` | `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT[p14]`; `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT[p15]`; `vendor/stage2/propedge/research/u_select.py::ROWS_TO_BEAT[p16]` |
| 37 | Trades available per day, per account and in total | partial | `extended/journey_measures.py::supply`; `extended/replay_records.py::ReplayRecorder` | — |
| 38 | Session coverage | partial | `extended/journey_measures.py::coverage`; `extended/journey_measures.py::trading_day_of`; `extended/journey_measures.py::firm_day`; `extended/lever_space.py::trading_day` | — |
| 39 | Longest idle stretch inside the firm's trading day | partial | `extended/journey_measures.py::idle` | — |
<!-- measures-index:end -->

---

## 9. Corrective cycle 1: the red team's findings answered

Every blocking finding takes the red team's fix, as the lead ruled. Every minor finding is adopted, except where a
one-line reason is given.

| finding | answered in |
|---|---|
| B-1 the window not bounded by the block | 1.1 (blocks, observation window, consequence); 6 (`user_beside.py:633`, `user_readings.py:183-189`, `_elig`: to change); 7 |
| B-2 `P_B` ignores spending after the first payout | 2 (`P_B` on the peak through each month close; "before the first payout" beside); 1.2 (peak out-of-pocket); (13); (24) beside; 6 (`user_readings.py:184`) |
| B-3 unpaid users treated as safe or left out | (24) three states, the limit "not paid within `B` by `W`"; (6) over all of `E_W` with censored lower bounds, S1 beside; 1.3 (the share beside every conditional percentile: (2), (3), (6), (7), (23)) |
| B-4 the seed spread is not the user's payout variance | 1.4 (three labelled readings); (34) |
| B-5 the baselines under the retired convention | 1.1 (every design and baseline coin-seeded; the martingale-outcome reading decides); 1.5 (the old input path); 2 (R\* retired, each baseline); (35); (36) |
| B-6 S5b rewards a late first payout | (21) marks `(0, a_1, ..., 126)` on all of `E_126`, unpaid censored at 126; S5b beside, never a dimension |
| B-7 the funded lifetime on completed accounts only | (31) Kaplan-Meier-style in payouts, censored count beside, each unit weighted equally |
| m-1 (16) lump-sensitive | (16) the per-unit median of `D_4 .. D_12`, the mean beside |
| m-2 (33) "making money" | (33) the median user (S4b against one half), the first crossing, `p* = 0` when `M(0) <= 0`, "untested beyond the grid" with the exposed share, the flip refusal to change (6) |
| m-3 (35), (36) counted as measures | title; 3; (35)-(36) status `comparator`; 8; the test asserts 37 measures and 2 comparators |
| m-4 identical readings | 3 (aliases for Wave 4.1); alias lines at (6), (8), (13), (16), (19), (24), (25), (26) |
| m-5 the decomposition biased at few seeds | (34) the ANOVA estimator; 1.4 (`n_eff` per seed and of the start-day means) |
| m-6 blank values in the composite | 1.3 (the blank rule; censoring at `W + 1`); a per-unit and never-blank line in every entry |
| m-7 per-measure `E_h` | 1.1 (one common `E_h` per horizon, paired across designs, baselines and seeds) |
| m-8 derivations from [BS] | 1.1 (each reading's record recorded); 1.5 (which record each file holds) |
| m-9 (32)'s years and period | (32) the embargoed year recorded; one year set for every design; the volatility rule from search-year data only |
| m-10 constants seen with the held-out years visible | 7 (the ledger entries) |
| m-11 "ahead" at exact zero | 1.2 and 2 (`> 1e-6`); 6 (`user_measures.py:64`) |
| m-12 smaller gaps | (7) the first close's total; (10), (11) `k <= 252`; (30), (37) `accounts_d = 0`; (38), (39) the trading day from 17:00 CT, news-barred windows idle with the other form beside; (14) never a dimension, within one trade stream; 2 and (24) the stop's bias stated, the wallet re-run to build beside |
| m-13 the test checks names, not meanings | Wave 3.1: `tests/test_journey_measures.py` (one synthetic test with a known answer per definition built) and `tests/test_journey_readings.py` (stated in the header) |

### Corrective cycle 2: the second read (`docs/reviews/MEASURES_v2_2026-11-18.md`)

| finding | answered in |
|---|---|
| N-1 a censored percentile labelled exact | 1.3 (the strict rule: a dollar percentile is exact only if every censored unit's lower bound lies strictly above it, otherwise "at least"; no limit read on such a percentile); (6) (the strict rule; a bankroll limit read through (24)'s three states, never on (6)'s percentile); (2), (3) |
| m-1 the "to change" list incomplete | 6 (`user_measures.py:82`; `user_readings.py:280-282` with its like-with-like rule; the peak-through-month field at `user_beside.py:648`; `user_readings.py:41`'s default blocks; `days_quantile`'s `BEYOND`, which makes (1), (5) and (9) `partial`; the note on `firm_reading.py:258`, `openings.py:519`, `opening_wait.py:519` and `cl_reading.py:485`) |
| m-2 `E_h` with `obs = h` | 1.1 (`obs_u >= h`) |
| m-3 the block rule forbids look-backs | 1.1 (the runner refuses outcome sessions after the block's last session; causal look-backs allowed under `feature-rules`) |
| m-4 `P_B`'s wording | 2 ("exceeds"; exactly `B` is within) |
| m-5 reading 2 for design-level measures | 1.4 (reading 2 only with a per-unit form); (22), (27), (31), (33), (34) say "readings 1 and 3 only" |
| m-6 (31)'s other endings | (31) (a policy closure, a move to Live, a payout cap and the window's end, each censored and counted by kind) |
| m-7 (6)'s alias line | (6) (the limit read through (24)) |
