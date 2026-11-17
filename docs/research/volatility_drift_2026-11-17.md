# Volatility drift in points against a contract fixed in dollars (Q-120, E-155)

**Author:** the scout (wt-scout), 2026-11-17. **Kind:** read-only research note. Nothing was built or run. No bar,
walk, trade or result value was read: no outcome, and nothing of the judged block (2024-01-02 onward). Where a
Stage 2 result file is named, only its section and column names were listed (to say where a figure already sits),
never its values. Every number below is a contract value from the verified ledger, a bracket size from a pinned file,
a date or seed, arithmetic on those, or a figure quoted from a decision row or a review, each with its source. Where
the record is silent the note says **not on record**. No literature was searched: the frames used are the ones already
in `docs/research/mechanisms_2026-11-15.md` (section 3.1) and Stage 2's review
`vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md` (its table at lines 286-292). Neither one covers
this question directly.

## 0. The question

The operator: NQ's daily range in points has grown since 2020-2021. The Topstep $50K contract's limits are fixed in
dollars. So a bracket of fixed point size resolves faster and more often in later years, evaluations finish sooner, and
the journey looks better over time. That comes from volatility in points, not from skill. How should the backtests
handle it?

The contract's dollar limits (`vendor/stage2/config/rules.yaml`, all `status: verified`):

| key | value | article | line |
|---|---|---|---|
| `combine_profit_target` | $3,000 | 8284208, read 2026-11-14 | 28-35 |
| `combine_mll` | $2,000, trailing on the end-of-day balance | 8284204, read 2026-11-14 | 54-75 |
| `xfa_mll_start` | -$2,000 | 8284204 | 211-218 |
| `combine_consistency_max_day_frac` | 0.55 (best day under 55 % of the target) | 8284208 | 80-104 |
| `combine_position_size_limit` | 5 minis = 50 micros | 8284197, read 2026-10-03 | 136-151 |
| `funded_scaling_plan` | "0:2,1500:3,2000:5" lots by balance | 8284223, read 2026-10-03 | 950-972 |
| `xfa_std_winning_days`, `xfa_std_winning_day_min` | 5 days of at least $150 | 8284233 | 255-293 |

MNQ: tick 0.25 points, $0.50 a tick, **$2.00 a point** (`vendor/stage2/config/instruments.yaml:73-78`).

The registered brackets are **fixed in points**:
- **P-14:** "the 25-point rung from 17:00 to the 12:00 hour, the 12.5-point rung at 13:00 and 14:00". The rung by hour
  is frozen by `results/a3_resolution_map.csv` (`vendor/stage2/prereg/P-14_a3-brk30-cb20.md:190-199`).
- **P-16:** "the 150-tick stop" (37.5 points), "contracts the engine's whole micros at the 150-tick stop"
  (`vendor/stage2/prereg/P-16_rc-s150-all-nr.md:180-182`). The marks are admitted by a cutoff "at most 5 % over the
  window" (lines 173-176).

Sizes are whole micros at a fixed dollar risk per state (P-14 line 36, `risk_denominator`). So a trade's dollars are
fixed and its points are fixed: only the market's movement in points changes from year to year.

## 1. The answer in short

- **The operator is right about the scorecard and about selection. The pass line is largely protected.**
- **The pass line** is the lift over the coin twin on the same brackets. Under no edge its expectation is zero at any
  volatility: with no drift a bracket wins 1/(1+R) on either side, and volatility sets only the time to resolve. So a
  rise in points volatility cannot make a false pass.
- What volatility does change at fixed-point brackets is the **size and power** of a real lift. To first order the
  lift falls as the bracket shrinks against the market's movement. Three things also break the cancellation:
  - the per-trade mean gives more weight to busy sessions;
  - the router's five-trade-a-session ceiling binds on busy days;
  - flattened pairs score zero, and there are more of them in calm periods.
  The pass line is therefore conservative toward volatility drift, but it is not invariant to it.
- **The user scorecard is fully exposed.** P, time to the first pass, the first payout and ROI are counted in sessions
  and months of a contract fixed in dollars. Stage 2's own record says the money of P-14 and P-16 is **supply**:
  offers taken all day, each resolving fast (D-582, Q-18's audit). Supply is exactly what points volatility moves.
- **Selection is exposed.** Choices made on 2020-2023 are judged on 2024-2026. Stage 2 already saw a fixed stop fail
  resolution early and resolve late (D-554).
- **Stage 2 handled the 2009-2019 versus today gap** with:
  - price rescaling (D-106, D-225), later found to be only a proxy (D-239);
  - the per-era report and era rule (D-271);
  - the move to fixed-point stops with exact dollar risk, after ATR-scaled stops broke the dollar sizing (D-300,
    D-303, D-306);
  - by-year resolution lines (D-212);
  - the span guard (D-578 (2)) and the per-start-year guard (D-621 (4)(e)).
- **Stage 2 never measured the 2020-2026 drift itself**: daily range in points by year, or resolution time by year.
  Both are not on record.
- **Recommended, in order:**
  1. the bars-only descriptive (a);
  2. regime-bucketed reporting written into every new declaration (b);
  3. a calm-regime replay of P-14 and P-16 (c).
  A volatility-scaled family is sketched for later (section 5). More history is the operator's purchase decision, and
  would help only scaled-bracket designs (section 6).

## 2. What Stage 2 already did about it

Line numbers are of `vendor/stage2/DECISIONS.md`, unless another file is named.

| id (line) | what it measured or corrected | does it cover 2020-2026 drift in points? |
|---|---|---|
| **D-106** (121) | Development brackets scored on a contract scale matched to the era: each day's prices multiplied by P_ref / P_day, so the ATR, stop and target scale with price while the tick, slippage and round turn do not. Results at actual and two other levels reported beside. | It addresses the price level (2009-2014 ES), not 2020-2026 NQ. |
| **D-121 (2), D-122 (1)** (137, 138) | Corrected D-121's remedy: "Cost scaling is withdrawn as a correction ... No era-matching method removes it [the one-tick bounce relative to the stop] from 2009 data; it is bounded by reporting actual and rescaled prices side by side". | The key pitfall for any rescaling (section 4 (c)). |
| **D-225, D-226** (244, 245) | The resolution map at today's price level (NQ rescaled to a reference of 30,600, "public levels of 30 September 2026"). NQ became feasible, "but it reads 2009-2019's volatility at today's prices". | Rescaling as an exploratory proxy, never a result. |
| **D-238, D-239** (257, 258) | The regime map, then (2009-2019) against now (2020 to June 2025): brackets at fixed stops in points and at 0.05-0.40 of the trailing 20-session mean range. The reading: "the gap between 2009-2019 and today is the size of a point move, not the market's behaviour. Measured in multiples of the trailing range, every market resolves on about as many decisions and stops in both eras. In fixed points, NQ and ES moved several times further a day in 2020-2025". | **The closest evidence: range-scaled brackets are era-stable, fixed-point ones are not.** It compares two eras. It does not track years inside 2020-2026. `results/regime_then_now.csv` is not vendored. |
| **D-240** (259) | Range stops dropped from the no-edge campaign because "their dollars per trade move with the trailing range, which D-212 forbids". | Why fixed points were kept: at fixed contracts a range stop moves the dollars. |
| **D-212** (231), raised to 5 % by D-308 (CHARTER section 4) | Consistent risk (90 % of trades within 10 % of the state's dollars, whole micros). Every trade resolves, with at most 5 % flattened "overall, in each market and in each year". | **A per-year resolution floor: the one by-year rule that bites on drift.** |
| **D-246 (1), (4)** (265) | Selection on gross edge, because "random entries at a tenth of the trailing range cost several times more per trade in R in 2009-2019"; "Require both eras". | A both-eras requirement for edges. |
| **D-271** (290); `vendor/stage2/docs/RESEARCH_PROTOCOL.md:84-110` | "Behaviour is estimated in R on every year, money only under today's tick economics". The per-era report covers e, its bound, skew, **the median time to the stop and the share still open at 15:08**. **The era rule:** eras flagged when a whole-year bootstrap of the difference in mean gross R excludes zero; when flagged, the money steps use the lower era's bound. "Today" is a regime defined by the stop (45 MNQ ticks). Stops are drawn from today's distribution. A drift baseline is rebuilt year by year. | The era rule tests **edge** (mean gross R), not supply or resolution. The resolution-time report is beside, not a rule. |
| **D-272** (291) | The stand-aside: a trade is taken only if its whole-micro size under the state's cap carries 90 % of the risk and its stop is at least 45 ticks. | A contract-fit floor any scaled design must meet. |
| **D-292** (311) | Per half-hour window, 2020 to June 2025: the 9:30 open has about three to four times the range of the reopen. "Then (2009-2019) the same decisions resolved far less often in fixed points -- D-239's era difference, the reason the ladder scales with the ATR." | Time of day, not year. |
| **D-300, D-303, D-306, D-307** (319, 322, 325, 326) | FV3's ATR-scaled ladder: "in 2013 to 2019 the stops are a few points ... the verified allowance ... carries only a few hundred dollars". The corrected run stood aside 65 % of offered trades. The operator: "These results are not valid". Replaced by "his stops fixed in points per rung ... `ladder.mode: fixed_points`", contracts chosen so the risk is exact. D-307 adds that under the ATR-scaled ladder the 3R leg resolved in every year, where the fixed-point leg missed. | **Stage 2 tried volatility scaling and dropped it for dollar exactness.** That is the main constraint on section 5. |
| **D-285** (304) | FV2 drew each trade's stop from today's session stops to avoid "the era distortion". | Sizing from a distribution of today's stops. |
| **D-420 (1), D-437 (2)** (439, 456); P-13 lines 76, 270-272; P-14 lines 343-345 | The era rule as registered: 2020-2022 against 2023 to 2026-07-16, whole-year bootstrap, 2,000 draws, seed 20261017. P-13's eras were flagged, so its bounds are the lower era's. | Era rule inside 2020-2026, on e only. |
| **D-554** (572) | The stop chosen on 2020-2023 alone and on 2024-2026 alone. On the early span "the 50-point stop fails resolution there"; on the late span "the 50-point stop resolves in this span". | **Direct evidence of resolution drift across the choice and judged spans.** |
| **D-578 (2) (d), D-580** (596, 598) | The span guard: not below P-16 on either span (2020-2023, 2024-2026-07-16) alone. S1's momentum sides "grow less than P-16 on 2020-2023 and more on 2024-2026", so they were rejected: "betting that the late era persists". | The guard Stage 2 used against a late-era effect. |
| **D-581, D-582** (599, 600) | S2's volatility thirds, each ranked against its own trailing 20 sessions. "The low- and mid-volatility cells also leave too many trades unresolved at the longest offered R in their worst year." "P-16's money comes from supply -- offers taken all day, each resolving fast". | **Supply, and so money, depends on the volatility regime even within a year.** |
| **D-604** (622) | Confirmation feasibility: "every failure is resolution", on stub years. | The per-year resolution line is fragile. |
| **D-605** (623) | "Every calendar year 2020 to 2026-07-16 grows at the bound on its own sessions ... 2020 and 2021 the weakest, 2022 to 2024 the strongest". | The money by year is on record in words. The drift is not separated from it. |
| **D-621 (4)(b), (e)** (639) | Choice block, then judged block; "the reverse (chosen late, judged early) is reported beside"; "not worse than R* on P in more than one of the seven start years". | A per-start-year guard on P, now kept on record only (CHARTER section 3). |
| **D-663** (681); Q-18's audit `docs/audits/Q-18_p14_stress_2026-11-17.md` | The era rule's calibration: "the registered era rule never overstates at 0.05/370" (audit table, line 55). P-14's "average trade loses a little at every risk size" (line 200), so its money is the contract's. | Calibrates the bound on e, not the supply. |

**This repository:**
- **E-021** (`DECISIONS.md:28`): "a coin-sided bracket wins 1/(1+R) at any volatility, and volatility changes only the
  time to resolve".
- **E-024, E-030** (lines 31, 37): "the 37.5-point stop dropped and the cutoff made per year (Stage 2's own files
  predict its R = 3 resolution failing)". The red team found the pooled and worst-year resolution shares far apart
  (`docs/reviews/DRAFT_F-B_multifeature_v2_2026-11-16.md`, M2-4, lines 220-253, citing `rc_width_screen.csv:198` and
  `u_hours.csv:175-208`).
- **E-031 (2)** (line 38): the reverse walk-forward was dropped; "a family may report its pick's year-by-year readings
  beside instead".
- **E-086** (line 93): a filter on the trailing month's volatility "selects in regimes lasting months", so it cannot
  reach power on the judged block.

**Not on record anywhere:**
- NQ's session range in points (or in percent) by year 2020-2026;
- the resolution time of a fixed bracket by year;
- trades per session by year for P-14 or P-16, apart from the two-era `period` rows of the gate files.

The two-era `period` rows sit in `results/rc_s150_all_gate.csv` and `results/a3_brk30_cb20_gate.csv`: section
`period`, column `trades_per_day`, periods `2020-2022` / `2023-2026` / `all` / `check`. Section `drift` carries
per-year rows `2020` to `2026` with a count `n`. Only the names were listed here; the values were not read.

## 3. What this repository's measures are exposed to

### 3.1 The pass line: the lift over the coin twin on the same brackets

**What it cancels.** The pair difference is `x = (outcome(rule side) - outcome(mirror)) / 2` at the same bracket, per
trade, in win probability (`extended/lift_bound.py:3-6`). Both arms share the entry, the bracket in points, the fills
and the costs. So:

- **The win-rate level cancels.** With no drift a bracket of stop a and target b = R a wins a / (a + b) = 1/(1+R) on
  either side, at any volatility (`docs/research/mechanisms_2026-11-15.md` 3.1 (i), Karlin and Taylor). Under the
  null of no direction information, x has mean zero whatever the points volatility. **So drift cannot make a false
  pass.** The level is protected.
- **Costs cancel**, and at a fixed-tick stop the cost in R is the same in every year anyway (ticks over ticks).
- **The schedule cancels for the pair**: same entries, same session.

**What it does not cancel** (derivations are first order, for Brownian motion, labelled [derivation]):

1. **The size of a real lift depends on the bracket measured against the market's movement.** From the note's 3.1 (ii),
   P(win) is about 1/(1+R) x (1 + m b / s^2), with m the drift per minute the side captures and s^2 the variance per
   minute. A signal whose drift scales with volatility (m = lambda s, a fixed Sharpe) gives a lift of about
   1/(1+R) x lambda x b / s [derivation].
   - At a fixed b in points the lift **falls** as s grows.
   - A real signal on a fixed-point bracket therefore shows a smaller per-trade lift in the busy late years than in the
     calm early ones. That is exactly the shape the era rule and the span guard read as instability.
   - So drift biases the pass line **against** a real signal's stability, not toward a false pass.
   - On a range-scaled bracket (b = c s) the lift is about 1/(1+R) x lambda x c, the same in every regime
     [derivation]. This agrees with D-239's reading that range-scaled brackets behave alike across eras.
2. **Trade weighting.** `cons` is the conservative fallback over `t21w`, `t42w` and `t63w`
   (`extended/lift_bound.py:20, 23, 48, 110`). Each is "the per-trade mean (sum over count)", so a session counts in
   proportion to its trades.
   - The expected resolution time is a b / s^2 (note 3.1 (i)). With re-entry when flat, trades per session grow
     roughly with s^2 [derivation].
   - So the judged estimate is weighted toward the judged block's busiest stretches.
   - The equal-weight block form `t21e` (line 19) is the one candidate free of this, and it was not shipped.
3. **The router's ceiling.** Both P-14 and P-16 run "five accounts in rotation (D-157), at most one trade an account a
   day (D-352)" under the strict one-at-a-time rule (P-14 lines 229-236; P-16 lines 159-166). So at most five trades
   are taken a session.
   - On busy days the five are taken earlier and faster. On calm days fewer get in before the 15:10 flatten.
   - Where a family's lift population is the router's taken trades, the composition shifts with volatility: busy days
     contribute their early offers.
   - Uncapped, the session's t-statistic is about lambda x sqrt(b/a), the same at any s [derivation]. Capped, n stops
     growing while the lift keeps falling as b / s, so power per session falls in the busy years [derivation].
   - Where the population is every offer (F-03's in-state offers against every population offer,
     `prereg/F-03_opening_timing.md:137`), the ceiling does not enter the lift. It enters only the value and the
     scorecard.
4. **Flattened pairs.** A pair where neither side reaches its target by 15:08 scores x = 0 in win probability. Calm
   stretches hold more of them, which dilutes the lift there.
5. **Side-dependent schedules.** At R not 1 the long and the short of one bracket exit at different times, so the
   design's next entry can differ from the twin's. F-03 states this residual ("removes it to first order", m2-1,
   `prereg/F-03_opening_timing.md:158`).
6. **Long bias.** A long-leaning rule is credited with NQ's rise against a 50/50 twin. Stage 2's D-271 (5) drift
   baseline exists for this, and NQ's drift in points grew with its price.

**The value line.** The lift is priced by the value map: "how much one won trade is worth over one lost trade in every
state of an account's life, under P-14's and P-16's own tables" (D-668, D-669, lines 686-687). That is a reading of
solved tables in dollars and in R, so the price of one won trade does not depend on points. Whether a family's bar
weights states by how often the window visits them (visits that depend on resolution speed) is **not on record** in
what was read. Each family's declaration should say.

**In sum:** the pass line keeps its level under points drift. Its power and its era stability are exposed, and the
direction of the bias is conservative.

### 3.2 The user scorecard: exposed

CHARTER section 2: the unit is a start day, the outcome net cash at months 1, 2, 3, 6 and 12, and a month is 21
sessions. Every measure counts sessions or dollars of a contract fixed in dollars:
- P, the shares ahead;
- S3a (paid by session 21), S3b (sessions to the first payout), S1 (cash before the first payout);
- time to the first pass, payouts per fee dollar (S3c), ROI.

Faster resolution brings more resolved trades a session, up to the router's five. So:
- the Combine's $3,000 target is reached in fewer sessions;
- fewer subscription periods are paid;
- funded winning days of $150 come sooner.

Stage 2 says where P-14's and P-16's money comes from:
- "P-16's money comes from supply -- offers taken all day, each resolving fast" (D-582);
- P-14's mean trade is negative at every R, "so its money is the contract's, not the trades'" (E-125, the Q-18 audit).

**So the row to beat, R\* = P-14, is itself made of the exposed quantity.** Three consequences:

- **Paired comparisons partly cancel.** P against R\* on the same start days shares the regime's common part. The
  interaction does not cancel: a design that uses supply harder gains more from a busy regime.
- **The intervals are conditional on the regime.** The judged block holds "a few dozen independent starts" (E-007 (2))
  and about nine independent stretches (E-023). A block bootstrap inside 2024-2026 cannot draw a calm regime. So its
  intervals say nothing about a user who starts in a calmer market.
- **Within-day rules also move with supply.** The Combine's 55 % consistency rule binds more when more of the target
  can come in one busy session. The engine's need-aware exits and consistency cap handle this (P-14 line 236). How
  often they fire by year is not on record.

### 3.3 Selection: exposed

- **The blocks.** The choice block is 2020-01-02 to 2023-12-29 (E-031, `extended/reader.py:103`). F-03's choice span is
  2021-01-04 to 2023-12-29 (E-095). The judged block is 2024-01-02 to 2026-07-16 (`extended/reader.py:105`).
- **Resolution cutoffs chosen on the choice block are conservative later**, if late resolution is faster. D-554 shows a
  wider stop failing early and resolving late. This also means the choice block can turn away a design that would
  resolve in the judged block. The red team saw both sides of this (M2-4).
- **A pick by the best value on the choice block** is a pick under that block's supply. Its ranking can change when
  supply rises. S1 (D-580) is the recorded case: rules ranked differently on the two spans, and the span guard caught
  it.
- **Guards in place:** the span guard and the per-start-year guard are Stage 2's (D-578, D-621 (4)(e)). Here the
  reverse walk-forward is dropped (E-031 (2)), and per-year readings are optional ("may report").
- **Nothing in a pinned family file reports by volatility regime.** That is the gap measurement (b) fills.

### 3.4 The floors

- **The gate's paths.** The gate draws "500 paths over 504 sessions resampled from the development day set" (P-14
  line 238). So its growth averages the regimes in proportion to their days in 2020-2026. The era rule shifts e by
  era, not supply.
- **The resolution floor** is by year (D-212). Calm years are where it fails, as in D-582 and D-604.

## 4. Three measurements, declarable

All three are EXPLORATORY and beside: none decides, chooses or carries anything.

### (a) Bars-only descriptive by year

- **What it measures** per development session (17:00 to 15:10 CT, the walker's day, `atlas_local.day_arrays`,
  `vendor/stage2/propedge/research/atlas_local.py:33`):
  - the session's high-low range **in points** and **in percent of its first open**. The split separates price level
    (which persists) from percent volatility (which reverts). This matters for what the drift means for a user: if the
    rise is mostly price level, today's points regime is the one a future user meets, and the early years are the odd
    ones out;
  - the 20-session trailing mean of each;
  - at each of P-16's five-minute marks and at P-14's slots, the **side-free first-exit time** of a band of fixed
    points around the entry (12.5, 25 and 37.5 points, at every R the tables offer, both sides pooled, as Stage 2's
    `mark_resolution` reads "kind columns only", `vendor/stage2/propedge/research/resolved_coin.py:241`), and the share
    still open at 15:08;
  - the same at bands of 0.10 and 0.25 of the trailing range, as D-238's scale-free reading beside.
- **Reported:** by calendar year and by quarter, as medians, p10 and p90. No sign, no target-against-stop split, no win
  share, no trade of any design. It is a property of the bars.
- **A free first step (a0).** P-14's and P-16's already-computed `period` rows (`trades_per_day` for 2020-2022
  against 2023-2026) and `drift` rows (`n` by year), in the two vendored gate files, give their supply by era and year
  at no run. These are Stage 2's registered designs, already judged in Stage 2 (E-037's reasoning). Reading them is the
  lead's call; this note did not.
- **Reads and the seal:**
  - **(a1)** the choice block only, 2020-01-02 to 2023-12-29. No purpose tag is needed (`extended/reader.py:531-536`).
  - **(a2)** the whole development window, which reaches the judged block. That needs a pinned described reading
    (`prereg/RD-nn_*.md`) whose `Judged-block reads:` line names a purpose with no choice word (`extended/reader.py:122`
    lists the refused words). Suggested: `volatility_descriptive`. Run once in a clean run (`extended/reader.py:555-558`).
  - **The leak, stated:** a judged-block volatility figure could steer later declarations, for example toward a stop
    that resolves in 2024-2026. The RD should require every later declaration to say it was written after (a2), and
    should forbid citing (a2) as the reason for any parameter. D-554 and the red team's M2-4 already carry part of this
    knowledge.
- **Cost:** heavy by the repository's rule ("anything that reads the full bars"), so it runs under `run.lock`. The work
  is one pass over the bars. Stage 2's regime core ran "about 0.2 s a trading day" (D-238), so 1,691 sessions is
  minutes, not hours (an estimate from that benchmark, not measured here). Memory is the bar frame. A result file with
  a sidecar manifest.

### (b) Every result reported by volatility regime

- **The bucket:** each session takes its own **trailing** 20-session mean session range in points (causal, prior
  sessions only, as S2 ranked its states, D-581 (5)). Two bucketings, both declared:
  - **(b1) absolute terciles in points**, cut points fixed on the choice block from (a1). If the judged block sits
    mostly in the top tercile, that is the drift made visible;
  - **(b2) relative terciles**: the trailing range ranked against the prior 250 sessions, so each year has its own
    calm and busy days.
- **Reported within each bucket, beside, never deciding:**
  - the pass line's lift (point and `cons` interval) and its trade count;
  - trades per session, the median resolution time and the unresolved share;
  - on the scorecard, P and S3b by the regime of the **start day**.
  - A between-bucket heterogeneity reading, labelled descriptive.
- **The reading's logic:** a real edge on fixed-point brackets should keep its sign in every bucket. By section 3.1 its
  size may fall in the busy bucket. A lift present only in the top tercile is the S1 pattern (D-580).
- **Reads:** each family's own judged read, so the bucket breakdown must be declared in the family file (every judged
  read is named by its purpose). It **cannot be added to F-03 or RD-03**, since nothing pinned is edited. It applies to
  new declarations, and to P-14 and P-16 under `registered_design` (E-037; `extended/reader.py:112-114`).
- **Cost:** light once (a)'s session table exists: a join on the session list.
- **Power:** a third of a few dozen stretches is a handful, so bucket intervals will be wide. State the minimum
  detectable difference beforehand (E-007 (e)).

### (c) A calm-regime replay of the registered designs

- **The rescaling.** Per session d, every bar's open, high, low and close is mapped
  `p' = O_d + k_y (p - O_d)` and rounded to the 0.25-point tick, where:
  - O_d is the session's first open;
  - k_y = min(1, L_ref / L_y) is one constant per calendar year;
  - L_y is the year's median trailing 20-session range in points;
  - L_ref is the median over a declared calm reference, the operator's 2020-2021 (both inside the choice block), from
    (a1).
  The map is monotone, so the high stays the high. The **brackets stay 12.5, 25 and 37.5 points and the sizes stay the
  same whole micros**. So:
  - every trade risks the same dollars;
  - the $2,000 MLL, the $3,000 target and the $150 winning day are untouched;
  - only the market's movement in points shrinks.
  This is the operator's counterfactual: today's market moving as little in points as the calm years.
- **How it is built without touching `vendor/`.** `atlas_a3.walk_minutes` takes the day's arrays through a callable,
  `arrays: Callable[[str], tuple]` (`vendor/stage2/scripts/atlas_a3.py:160-170`). An adapter in `extended/` wraps that
  callable, and nothing else changes. Downstream it runs P-14's and P-16's own cell builders, the gate and U1 unchanged.
- **The identity first, refusing:** at k = 1 the replay reproduces P-14's and P-16's registered gate paths and U1 starts
  exactly (the Q-18 and Q-51 forms).
- **Pitfalls, each stated in the declaration:**
  1. **The tick grid does not shrink** (D-122 (1)). Compressing the path by k at fixed tick costs is the same as the
     real path with brackets and tick costs both divided by k. So costs per unit of movement rise by 1/k. That is
     realistic for a calm market but not removable. Report the replay at the actual costs and with costs scaled by k,
     side by side, as D-122 requires.
  2. **Use one factor per year, not the day's own range.** Rescaling each day by its own range would erase day-to-day
     clustering and news days, and would use the day's future range. A trailing-range factor is the causal
     alternative, beside.
  3. **Drift is scaled too** (net moves shrink by k), so drift relative to volatility is kept. P-14's 30-minute break
     and P-16's marks are unchanged by an affine map about the open, so the entries are the same.
  4. **Frozen choices stay frozen:** P-14's rung by hour (`a3_resolution_map.csv`) and P-16's admitted marks (the 5 %
     cutoff) are kept, never recomputed. The replay's unresolved shares are reported, and **a D-212 failure there is a
     finding**, not a trigger to rerun.
  5. **Only amplitude changes.** Volume, spreads, the intraday clock and market structure stay as they were. It is not a
     replay of 2020-2021; it is today's market with its points volatility turned down.
  6. **Session gaps are not rescaled.** Flat by 15:10, so no position crosses them. A design with cross-session
     features would need a whole-series anchor instead.
  7. **Nothing is written to the data junction**: the rescaled bars live in memory in the clean run.
  8. **It changes the trade sequence**: fewer trades, later exits, more flattens. So the gate and U1 must rerun.
- **Reported:** the whole scorecard (P, S1-S5c, time to first pass, first payout, ROI), the gate's growth at the
  bound, trades per session and unresolved shares, at k_y and at k = 1, for P-14 and P-16. Possibly a second
  reference, the choice block's median, as a declared variant.
- **Reads:** the whole development window, judged block included, of **P-14 and P-16 only** under
  `registered_design`, by a decision row naming them (E-037). Never available to a family.
- **Cost:** heavy: two designs times two to four arms, each a walk rebuild, a gate and U1. Under `run.lock`, one at a
  time. Memory is near Stage 2's family runs (CLAUDE.md: about 3 GB).
- **What it shows:** how much of P-14's and P-16's scorecard is points volatility. It tests nothing and carries
  nothing.

## 5. A volatility-scaled design family (a sketch for a future declaration, not declared here)

- **Mechanism (none for direction).** It is a contract-fit convention: brackets in units of the trailing range, so a
  coin's resolution time a b / s^2 and its per-session supply stay about the same across regimes [derivation]. Size is
  set to the state's fixed dollar risk, so the contract's dollar limits stay fixed.
- **Its pass-line role** must be settled first.
  - A scaled coin's lift over the coin twin is **zero by construction**, so under E-008 a coin-sided scaled design has
    no pass line.
  - It is not a lever that adds no trades (E-023 (1)), because it changes every bracket.
  - It is not a filter (E-023 (2)).
  - So it is either the **bracket convention of a sided family**, where the lift is measured on the scaled brackets
    against a coin on the same scaled brackets and should be era-stable by section 3.1 (1), or a **described reading on
    the scorecard**.
  - Which it is needs a classification row (the lead). The safe default: a described reading, carrying nothing.
- **Rules to declare:**
  - **The stop:** b_d = c x L_d, rounded to the tick. L_d is the trailing 20-session mean session range in points from
    sessions closed before d's 17:00 open, so the ticket is known in advance for hand entry five minutes ahead
    (CHARTER section 4). The target is R x b_d, R from the state table.
  - **The size:** micros = min(floor(Risk$ / (b_d x $2)), the state's cap).
- **Contract fit (CHARTER section 4), worked from the ledger:**
  - **Consistent risk (D-212 (1)):** whole-micro rounding loses up to one micro, worth 2 b_d dollars.
    - At a $2,000 risk, b_d = 50 points gives 20 micros exactly.
    - At b_d = 100 points it is 10 micros, and one micro is $200, i.e. 10 %, so D-212's 90 % line is at risk at wide
      stops.
  - **The allowance caps** (`combine_position_size_limit` 50 micros; `funded_scaling_plan` 2 lots = 20 micros below
    $1,500):
    - a fresh XFA's $2,000 needs b_d of at least $2,000 / (20 x $2) = 50 points;
    - the Combine's needs at least 20 points;
    - below these the allowance carries less than the state's risk. P-16's XFA already realises $1,500 at 37.5 points
      (P-16 line 182).
    - **This is D-300's failure in calm regimes**, and the stand-aside (D-272) removes such trades. Supply in calm
      regimes falls by the cap, not by resolution.
  - **The cost floor:** b_d at least 45 ticks (11.25 points), D-272. The cost in R (fixed ticks over b_d) rises in calm
    regimes, the D-246 effect.
  - **Resolution:** at most 5 % flattened overall and in each year (D-212). The scaling should make the per-year line
    easier, as D-307 saw for the 3R leg.
  - **Conduct:** smaller size on busy days fits "no maximum size into major news" (tier 1). The BLS 07:35:00 and FOMC
    exclusions are unchanged.
- **Cells (counted, a contract-arithmetic grid, no fit):**
  - c in three values anchored so that b equals P-14's 25-point rung, P-16's 37.5-point stop and a 50-point stop at the
    **choice block's** median L (from (a1));
  - L's window fixed at 20 sessions;
  - the all-day window.
  - That is 3 cells, with every R the table offers walked, as P-16 walks them. The c anchors are computed on the choice
    block only. Each cell runs at the stand-aside, and its stood-aside share is reported by year.
- **Supply to state before the read:** the share of choice-block sessions on which each state's dollar risk is
  carried (the D-272 (2) form), by year.

## 6. Would more history (pre-2020 NQ) help?

**It is a purchase, so it is the operator's decision, and it was offered once already.** At E-008 the operator chose
"Judge on trades first" over "adding history, buying older bars" (`DECISIONS.md:15`). This repository's bars are
Databento's 2020-2026 (P-14 line 159). Stage 2's 2009-2019 reads ran inside QuantConnect, whose bars "are not
exported" (D-120, line 136). Not priced here.

**Where it would help:**
- **The regime question itself.** 2009-2019 is the calm-in-points regime the operator asks about. D-239: NQ moved
  "several times" less a day then.
- **For range-scaled brackets** it adds independent stretches in which the lift, measured in R on scaled brackets, can
  be checked across regimes ("Measured in multiples of the trailing range, every market resolves on about as many
  decisions and stops in both eras", D-239). This is where a vol-scaled family's era stability would be tested.
- **For the scorecard's regime blindness** (section 3.2), it would give start days from calm markets.

**Where it would not help, from the record:**
- **Fixed-point designs do not live there.** "No market, decision time and fixed stop lets every leg of any arm
  resolve ... over 2009-2019" (D-224, line 243). P-14 and P-16 would fail D-212 in most early years, so their money
  cannot be replayed there. (c)'s rescaling is the in-window substitute.
- **The tick-grid artefact cannot be removed** from old data (D-122 (1)). D-271 keeps money on today's economics.
- **Structure changed.** MNQ did not exist before May 2019 (D-265, `vendor/stage2/DECISIONS.md:284`), and
  "old days clearing the floor are the old era's volatile days -- a selected sample" (D-271 (3)).
- **Direction discovery there is partly spent.** Stage 2 read 2009-2019 for the effect atlas, SS1 and the ORB
  screens. The budget is not refreshed by new data (CHARTER section 3).

**In short:** pre-2020 bars would answer "does the design hold in a calm regime?" only for designs whose brackets scale
with the range. For fixed-point designs the honest answer is the in-window calm replay (c) plus the descriptive (a).

## 7. Unknown, and how it could be found

| unknown | how |
|---|---|
| range in points and percent by year 2020-2026 | (a1) now, (a2) under an RD |
| fixed-bracket resolution time by year | (a) |
| P-14's and P-16's trades per session by era and year | (a0): the vendored `period` and `drift` rows (the lead's read) |
| how often the router's five-trade ceiling, the 55 % consistency cap and the stand-aside bind, by year | (c)'s k = 1 arm with per-year counts (the gate files carry pooled `share_trades_skipped_busy` and `share_trades_at_tier_cap` columns only) |
| whether a family's value bar weights states by visits on the window | each family's declaration states it |
| whether the rise is price level or percent volatility | (a)'s percent column |

## 8. Ranked recommendations

1. **(a) the bars-only descriptive.** (a1) on the choice block at once; (a0) read by the lead; (a2) under a small RD
   with the leak clause. Cheapest, and it answers the factual question.
2. **(b) regime-bucketed reporting**, written into every new declaration's beside list from now on (the template), and
   applied to P-14 and P-16 under `registered_design`. Equal-weight block readings (`t21e`'s form) are reported beside
   the trade-weighted `cons`.
3. **(c) the calm-regime replay of P-14 and P-16.** Heavy; after (a) gives L_ref.
4. **A classification row** for brackets scaled by range (section 5) before any such family is drafted.
5. **Pre-2020 bars:** the operator's purchase decision. It would help only scaled-bracket designs.

**Proposed TASK_QUEUE line:**

`Q-1xx | wt-scout -> wt-verify | Volatility drift (docs/research/volatility_drift_2026-11-17.md): (a1) the choice-block range and fixed-bracket resolution-time descriptive by year (bars only, side-free, under run.lock); draft RD-nn for (a2) on the whole development window with a non-choosing judged-block purpose and a leak clause, and for (c) the calm-regime replay of P-14 and P-16 under registered_design; add the regime-bucket and equal-weight-block readings to the family template | after F-03 run 1 | E-155`
