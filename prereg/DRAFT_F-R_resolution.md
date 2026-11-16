# DRAFT F-R: resolution forecasts on P-16's schedule (family R) -- not declared

**Status: DRAFT, first version, 2026-11-16 (TASK_QUEUE Q-38), for the red team. Not pinned, not numbered, not
declared.** Nothing of it is built. No bar, walk or trade file was read for it, no forecast was fitted, and no outcome
was computed. The one piece of code is a synthetic test of the textbook arithmetic the forecast leans on
(`tests/test_family_r_band_exit.py`, section 18). This file may be edited until the lead pins it. From the pinning row
on, nothing in it is edited: a change is a new family.

**Its rules come from the operator's ruling of 2026-11-16 (E-023; `CHARTER.md` section 3, "Levers that do not choose a
side").** The forecast keeps the coin's side, so E-008's lift over the coin twin cannot judge it. Its uses split under
the ruling:

- the **admission filter** (Part I) is tested at the trade level against a **placebo-selection twin**, and can be
  carried;
- **choosing the funded opening's R on the same trades** (Part II) is a **described reading**: never carried, and no
  program family number.

| field | value |
|---|---|
| family | R: a variance forecast from closed bars, used to admit P-16's refused marks on the days they are forecast to resolve |
| id | F-XX -- the gatekeeper's |
| program family number k | the next free at the pin. F-01 spent 10 (E-007 (a)); F-02's and F-B's drafts are ahead of this one. The described reading of Part II takes none (E-023 (1)) |
| level | one-sided **0.05 / (k (k + 1))**: 0.05 / 132 at k = 11, 0.05 / 156 at k = 12, 0.05 / 182 at k = 13, 0.05 / 210 at k = 14 |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16 only, read through the reader of TASK_QUEUE Q-32 (section 4) |
| base | P-16 (`rc_s150_all_nr`, `vendor/stage2/prereg/P-16_rc-s150-all-nr.md`) as registered; R\* = P-14 beside |
| choice block | sessions 2020-01-02 to 2023-12-29. The forecast is fitted there. Its out-of-fold years are 2021, 2022 and 2023 |
| judged block | sessions 2024-01-02 to 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`config/windows.yaml`, `reserve`); not on disk, a purchase (section 15) |
| cells | Part I: **3** (the admission filter read at R = 1, 1.5 and 3). Part II: 1 described reading, unnumbered |
| judged | one cell: stage B's pick |
| pass line | E-023 (2): the lift over the placebo-selection twin, one-sided at the family's level by Q-16's calibrated statistic **[Q-16]**; its value at that bound at least $500 a year; section 3's floors; the scorecard beside |
| seeds | proposed 20261970 to 20261979, checked unique (section 16) |
| model card | the forecast's: its fitted coefficients, inside the walk-forward only. This needs the lead's row under Stage 2 D-621 (4)(d), the same row family B needs (E-019) |

---

## 0. In plain words (for the operator)

**P-16 and its schedule.** P-16 offers a coin-sided trade every five minutes from 17:00 CT, with a 37.5-point stop.
It offers nothing after 09:00 CT (Stage 2 D-618 (3)). The reason: on an average day a bracket opened later, with the
table's widest target (three times the stop), is too often still open at the 15:10 close. Stage 2's rule (D-212, D-525
(4)) allows at most 5 % of trades to reach the close.

**What this family adds.** On a fast day, many of those later trades would finish in time. Volatility clusters, and it
can be forecast from past bars. So this family forecasts, for each later offer, how much the price will move before the
close. It **admits a refused offer only when the forecast says the trade finishes with at least 95 % probability.**

**What the forecast cannot do.** The coin still picks the side, so the forecast cannot make a trade win more often. On
a market with no drift, a bracket's chance of reaching its target first is fixed by its shape alone, whatever the
volatility (section 1). Volatility changes only how long the trade takes. So the trades the forecast picks are not
better bets than random ones. They are only less often cut off at the close, and a cut-off trade costs a little extra
in the model.

**How it is judged (the operator's rule, E-023).** The forecast's picks are compared with a random pick of the same
number of the same late offers, at the same times of day. The family passes only if three things hold:

- its picks earn more than random picks by more than chance, at the family's strict level;
- that difference is worth at least $500 a year where the trades are used;
- every floor holds: trades resolve, the long-run gate, verified rules, conduct.

**Expected.** A small, real edge from avoiding the close, likely below the $500 bar. A "no" is a valid close. The extra
trades' effect on a user's journey is shown beside, but the ruling does not credit it: the random twin adds the same
number of trades.

**A second use, described only.** Giving a funded account's first trade its 3R target only where the forecast says it
will finish, and a smaller target where it will not. That adds no trade and picks no trade, so under the ruling it is a
**described reading**: shown on the menu with whom it helps and hurts, never carried, with no family number (Part II).

## 0.1 Where the brief's items are answered, and which use falls under which rule

**The brief's items.**

| the brief's item | where |
|---|---|
| the mechanism and its sources | 1 |
| the forecast: HAR-type, closed bars only, fitted in the walk-forward on the choice block; every parameter classed | 6, 8 |
| how the forecast is used, each use a cell, counted | 0.1 (below), 7, 13, 17 |
| supply and resolution gates before any outcome | 9 |
| the pass line | 11 (E-023 (2)); 13 (E-023 (1)) |
| the journey scorecard beside | 12 |
| prior exposure | 2 |
| the confirmation | 15 |
| seeds 20261970-20261979, checked unique | 16 |
| k the next free | header; 17 |
| the walker (E-011) and the reader of Q-32 | 4, 5, 18 |

**The three uses of the forecast the brief names, under E-023.**

| use | what it changes | E-023 class | in this file |
|---|---|---|---|
| **(u1) admitting marks the unconditional cutoff refuses** | adds offers: P-16's refused marks, on the days the forecast says they resolve | (2) **a filter that keeps the coin's side and chooses which offers to take**: tested against a placebo-selection twin, can be carried | **Part I, the family's 3 cells** (`adm@1`, `adm@1.5`, `adm@3`) |
| **(u2) choosing the funded opening's R where it resolves** | the target of trades P-16 already offers and takes; no trade added, no offer chosen | (1) **a lever that adds no trades**: described, never carried, no family number | **Part II, the described reading `R-cap`** |
| **(u3) freeing the firm's one position slot sooner** (the opening routed to an offer forecast fast) | which offer a newly funded account's opening takes, i.e. when | (2) a timing filter on the funded opening | **not here: proposed as a state of family O** (TASK_QUEUE Q-37). See below |

**Why (u3) goes to family O.**

- (u3) has family O's population (the funded openings), family O's twin (a placebo of the same firing share on the
  openings) and family O's seam (a router that lets an opening wait).
- Declaring it here would put two families' cells on one population, under two levels.
- Its mechanism also runs **against** family O's: by the LeBaron effect, a predictably fast market is less persistent,
  so a 3R coin opening there should win less (`docs/research/mechanisms_2026-11-15.md` section 5.2, "The interaction
  with A1"). Family O's draft can carry it as a declared state, with that sign stated in advance.
- Part II's `R-cap` reports how much sooner a capped opening frees the slot, as a mechanics reading.

## 1. Hypothesis: the mechanism and its sources

**(i) Bracket geometry is textbook probability.** For a driftless continuous price, stop a, target b = R a, variance
rate sigma^2 (Karlin & Taylor 1975, ch. 7; the scout's note section 3.1):

- the target comes first with probability a / (a + b) = 1 / (1 + R), **at any volatility**;
- the expected time to resolve is **a x b / sigma^2**: stop x target / variance;
- in stop units (a = 1, time as integrated variance u in stop^2), the probability the bracket is still open after u is

      Psi_R(u) = sum over odd n of 4 / (n pi) x sin(n pi / (1 + R)) x exp(-n^2 pi^2 u / (2 (1 + R)^2)).

`tests/test_family_r_band_exit.py` holds them:

- the series equals the method of images;
- it integrates to R;
- a lattice walk converges to it;
- Monte Carlo at two volatilities gives the same target share and exit times scaled by the variance.

**(ii) Volatility clusters and is forecastable.**

- **Corsi (2009)**: the HAR model. Tomorrow's realised variance is a sum of yesterday's, last week's and last month's
  terms. It is the standard benchmark (*J. Financial Econometrics* 7(2) [abstract and summaries]).
- **Hong, Nolte, Taylor & Zhao (2023)**: price durations -- the time for the price to move a fixed amount, which is a
  bracket's own question -- forecast variance as well as realised variance does or better (*J. Financial
  Econometrics* 21(1) [abstract and summary]). The duration model behind them is Engle & Russell (1998).
- **Andersen & Bollerslev (1997)**: the intraday U-shape of volatility. Stage 2's cutoff already uses it, by mark
  (D-525 (4)).
- **Ederington & Lee (1993)**: scheduled releases raise volatility for hours [abstract only].
- **Stage 2's atlas R family (D-136)**, on its 2009-2014 development data: the previous day's VIX predicts the next
  day's realised variance beyond the previous day's, and range compression predicts calmer days. It was recorded "as
  sizing and survival inputs, never edge".

**(iii) The family's hypothesis.** P-16's cutoff admits a mark if its unresolved share **averaged over all days** is at
most 5 % at every R the table offers (D-525 (4)). A forecast conditions that rule on the day.

- At a refused mark, the offers on days forecast fast resolve, while the mark as a whole does not.
- **The conditional rule:** an offer is admitted at bracket R iff its forecast probability of being open at the walk's
  end is at most 5 %. That is D-212's line applied to the one offer, given the forecast, instead of to the mark's
  average.

**(iv) What the selection can and cannot earn at the trade level (stated before anything is read).**

- With the coin's side and no drift, the expected gross outcome of a bracket is zero whatever the volatility and
  whatever the deadline. A trade cut off at the deadline carries its position there, a martingale (optional stopping).
- Selecting by a volatility forecast moves three things: the time to resolve, the share open at the deadline, and the
  share reaching the target by it. **It moves no expected gross outcome.** The synthetic test shows this on persistent
  slow/fast days.
- So the selection's lift over a placebo selection of the same share (E-023's twin) comes from **costs that depend on
  how a trade ends**. Under Stage 2's walk (`extended.walker.STAGE2`; E-010 (3)):
  - a flatten is booked at the worst of the bars ending 15:08-15:10, less two ticks, **and** charged two exit ticks;
  - a stop pays one exit tick, a target none, a breakeven exit one.
- The lift is therefore about the flatten's extra cost times the drop in the open share, plus the exit-tick
  composition. The synthetic test holds the identity exactly, with a flatten cost.
- Second-order terms (a drift squared; the tick grid's one-tick asymmetry at the target) are small and enter both arms
  alike.
- **So the trade-level lift is expected positive and small.** Part of it is a property of Stage 2's conservative
  flatten convention, not of the market. The `close` flatten convention is read beside (section 11), so the reader can
  see how much of a lift the convention carries.

**(v) Why it could matter for a user, though the pass line does not credit it.**

- P-16's funded accounts take fewer than one trade per live account-day (`vendor/stage2/results/u_xfa_day_budget.csv`,
  section `signal_supply`, as the handoff 2.5 quotes it). One position at a time across the firm (D-429) and the 09:00
  cutoff leave some accounts without a trade on some sessions.
- Admitted later offers give them one. That is supply. E-023's twin adds the same supply, so it cancels in the pass
  line by design ("so supply and schedule cancel and only the selection is measured").
- The journey effect is shown beside, paired with P-16 (section 12).

**(vi) Whose accounts and how.** One user's own five Topstep seats, each with its own trades, one position at a time
across the firm (D-157, D-429; E-012 (3)). Every trade is placed by hand at least five minutes after its alert (E-008).

## 2. Prior exposure: what has already read resolution on these bars, and how

A judged reading is worth only what the block's freshness allows. Every read below is Stage 2's unless marked.

| row | what was read | data | what it recorded | bearing here |
|---|---|---|---|---|
| D-136, D-137 (the effect atlas, R family) | `R01`-`R03`: the VIX level, range compression and a volume surge as predictors of the day's or the rest of the day's realised variance (`config/effect_atlas.yaml`) | six markets, 2009-06-01 to 2014-05-27 (QuantConnect) | VIX and compression predict variance; recorded as sizing and survival inputs, never edge | **outside this repository's window**: independent prior evidence that variance on these markets, NQ among them, is forecastable; no 2020-2026 bar read |
| D-212 (2), D-308 (3) | the rule: at most 5 % of trades to the 15:10 flatten, overall, by market and by year | -- | the line itself | the floor and the per-offer threshold q (6.5) |
| D-213, D-214 (the resolution map) | hourly decisions 17:00-14:00 CT, six fixed stops, 1R and 2R: the shares resolving and the minutes to resolve | QuantConnect, Stage 2's development halves | where and at which stops brackets resolve | the clock's effect on resolution; no forecast |
| D-383 (the collect map) | 08:30 brackets at stops 1x-4x a 20-point target; the minutes to resolve by hour | QuantConnect run R145, its CHOICE and CHECK spans | "the hour hardly changes" the winning share, only the time | (i) seen on NQ: time, not win rate |
| D-515, D-521, D-523 | the fixed-slot rule judged each slot by its slowest 3R walk | 2020-2026 | the scheduling fault D-525 corrected | why the cutoff is per mark |
| **D-525 (4)** | the cutoff per mark, per stop: unresolved share at most 5 % at every offered R, kind columns only | **the whole development window, both blocks** | P-16's admitted marks; none after 09:00 CT at 150 ticks (D-618 (3)) | **the base and this family's population (5.2) were fixed on both blocks**: disclosed (4.4) |
| D-538, D-542 (the stop-width screen) | per-mark resolution at 150 and 200 ticks; the 37.5-point US window fails resolution | 2020-2026 | `rc_width_screen.csv` section `marks` | the refused marks' average resolution has been seen, mark by mark, on both blocks |
| D-578 (4), D-581, D-582 (S2) | P-16's coin gated by the last 30 bars' range in thirds against the same mark's 20 prior sessions; a trend state | 2020-2026, both spans; campaign growth | no candidate; high volatility closest to P-16; low and mid volatility failed resolution at the longest R in their worst year | **a volatility state was read on P-16's own offers**, as a gate on P-16's marks, not as admission of refused ones; its campaign readings are seen |
| D-639, D-641, D-642 (program U family 4) | window cells; an R cap from the resolution columns where a window fails D-212; the 25-point US cell with its cap (D-641 (3)) | 2020-2026, both blocks | closed at line (3)(i); the US-hours scorecards beside | the R cap's form (Part II's lever is its per-offer, forecast-conditioned version) |
| handoff 3.2 | "Time of day changes resolution speed and cost, not the win rate at zero edge"; every change to the funded leg was worse for a user | -- | -- | (i); Part II's prior |
| this repository | `docs/research/mechanisms_2026-11-15.md` section 5.2 (the scout); family B's draft's resolution model as a positive control (nothing read); E-021, E-023 | none | -- | the scout's design, adapted to E-023 |

**The drafter's own reads (disclosed).** All are code, configuration and decision rows. **No result value was opened**
beyond what the rows above state.

- `vendor/stage2/propedge/research/resolved_coin.py`: the coin table, `mark_resolution`, the windows, the release cut.
- `vendor/stage2/scripts/rc_width_screen.py` (`build`), `config/effect_atlas.yaml`, `config/resolution_map.yaml`.
- `extended/features.py`, `extended/walker.py`.
- The section and measure names of `u_value_map.csv`.

**What follows.**

- (a) **The judged block is late development for resolution.** Whether the late marks resolve on average has been read
  on it (D-525, D-542).
- (b) **What is new** is the conditional question. Whether a forecast from closed bars sorts the refused offers into
  ones that resolve, and whether that selection beats a random one at the trade level, has never been read.
- (c) S2's volatility gate (D-582) is the nearest prior: a coin offer kept only in a volatility state, on P-16's
  marks. **It read campaign growth, not a trade-level selection against a placebo**, and it removed P-16 offers rather
  than admitting refused ones. This family names it and differs from it in both respects.

## 3. Contract fit and conduct: the constraints every cell lives inside (CHARTER section 4)

| constraint | how the family meets it |
|---|---|
| latency, at least 5 minutes, hand entry (D-266; E-008) | **the forecast for an offer at mark m is an alert at t = m - 5 and reads only bars stamped at or before m - 6** (closed by t; feature-rules 1). The entry is P-16's: market at the open of the first bar at or after m, its tick charged as a cost. No automated or API entry |
| one position per firm, five minutes flat (D-429) | the engine's strict router, as P-16's |
| resolution (D-212, D-308) | per offer by construction (6.5); K2 on the choice block (9); a floor on the judged block (11) |
| realised risk (D-212 (1), D-308) | the stop is P-16's 150 ticks, and a capped target leaves the dollar risk unchanged. Read in P-14's registered allowance-capped form (E-022 (1)) |
| stop band and cost floor (`stop_band.csv`; D-271 (3)) | 150 ticks, above the 45-tick floor |
| news (D-525, D-533; E-007 (d)) | P-16's cuts unchanged. Refused marks start at 09:05 CT, after every 07:30 CT BLS release and five minutes after a 09:00 CT release minute (as 07:35 is to 07:30, E-007 (d)). FOMC days are excluded. No admitted offer falls in a Topstep Tier 1 window (CPI, NFP, PPI, FOMC; E-007 (6)) |
| no time stops (D-212 (2)) | none. Part II's lever chooses a target at entry, not an exit time |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (37.5-point brackets held minutes to hours); no maximum size into major news (above); no copying across accounts (D-157); nothing concealed |
| conduct tier 2 (D-289) | as P-16: the Responsible Trading Program's placement off in the base case, on beside |
| conduct tier 3 (E-013 (1)) | 0 % denial in the verdict; 10, 25 and 50 % beside (Q-17's adapter) |
| firm rules | none loaded by the family. The engine runs Stage 2's verified ledger as P-16 does |
| the breakeven move (E-013 (2)) | allowed as made; P-16's walk. Q-20's corrected moves are beside (`extended/walker.py` presets, merged b7232ba) |

**One conduct note.** A rule that seeks the fastest windows picks release windows. Here the admitted windows start
after every release the engine knows of. Whether a full-size position held through a later ISM release is "maximum size
into major news" is Q-39's question, and this family inherits P-16's answer.

## 4. Data, blocks, the seal and the disclosed pre-reads

1. **Data:** Stage 2's NQ 1-minute bars (licensed, uncommitted, `vendor/DATA_MANIFEST_stage2.sha256`), 2020-01-02 to
   2026-07-16 only. The labels come from this repository's walker (E-011), not Stage 2's `data/atlas`.
2. **The blocks:** choice 2020-01-02 to 2023-12-29; judged 2024-01-02 to 2026-07-16. The forecast's out-of-fold years
   are 2021, 2022 and 2023 (6.3).
3. **The seal (Q-32).** Every bar and walk this family reads goes through `extended/reader.py`, the purpose-tagged
   reader TASK_QUEUE Q-32 is building (`docs/briefs/Q-32_2026-11-16.md`; **not yet merged -- stage A waits for it**).
   - Purposes are named here so the reader can check them against this file's text once pinned: `identity` (P-16's
     identities, the whole window), `fit` and `stage_A_resolution` (choice block only), `stage_B_choice` (choice block
     only) and `stage_C_judgement` (the judged block, once, after the frozen forecast's hash is pinned).
   - Every judged-block read appends to `results/read_ledger.jsonl`.
   - T-3 (section 18) is the second proof: choice-stage outputs unchanged when the judged block is replaced.
4. **Disclosed pre-reads**: inputs fixed or read over 2020-2026 that T-3 cannot see, each with what it can bias.

   | input | what it is | can bias | cannot bias |
   |---|---|---|---|
   | P-16's admitted marks (D-525 (4), whole window) | the base's schedule; the population's marks (from 09:05 CT) | that the population is "marks that on average do not resolve at 3R" -- common to both arms of every comparison | the forecast's selection within a stratum (7.2) |
   | P-16's per-R bounds (the verdict arm's shift), estimated over both blocks (the F-P review's N2) | a constant per R | the level of every journey number, both arms alike | the trade-level lift (computed on net R before any shift) |
   | `u_value_map.csv` (D-667) | value of a win by place | stage B's ranking and C2's dollars | the lift or its bound |
   | `stop_band.csv` | the cost floor | nothing here (P-16's stop) | -- |
   | S2's readings (D-582) | a volatility gate on P-16's marks | the design of K-info and of the placebo | the pick |

5. **No NQ from 2026-07-17** is on disk or read (section 15).

## 5. The base, the population and the walk

### 5.1 The base

P-16 exactly, as registered and as this repository's identities reproduce it (E-004 gate paths; E-010 U1 start rows):

- the coin `rc_s150_all_nr`: one fair coin per (date, mark) over the whole grid, seeded 20261102 (`resolved_coin.coin_table`);
- the stop 150 ticks, every quarter R to 3R walked, Stage 2's costs (`fee_by_stop`);
- a report day's marks before 07:30 CT dropped, then every report-day entry before 07:35 CT (D-533 (2));
- the day kinds `n` and `b` (FOMC days, early closes and empty days out);
- P-14's money side: the no-closure v12 table, 20 purchases in 21 sessions, the strict router, five seats;
- the registered trades' content hash `rc150_dev_test.TRADES_SHA256`.

### 5.2 The population: P-16's refused grid offers

- **Marks:** every five-minute grid mark from **09:05 to 15:05 CT** -- every mark after P-16's last offered mark, 09:00
  CT (D-618 (3)), fixed as a time range and not re-read from any table.
- **Sessions:** P-16's walked day kinds, after the forecast's warm-up (6.2).
- **The offer:** at mark m on day d, the market entry at the first bar opening at or after m, as P-16's.
  - Its side is the registered coin's at (d, m). The coin table already covers the whole grid, so no new coin is drawn.
  - It is walked long and short.
- **No mark inside 08:30-09:00 CT is in the population** (those are P-16's own, unchanged). No entry is added in the
  window Stage 2 D-281 (3) reserves to the operator.

### 5.3 The walk and the labels

- **The walker:** `extended/walker.py`, preset **`STAGE2`** (E-011): P-16's own walk, so the base reproduces P-16 bit
  for bit:
  - FV3's rung walk at every quarter R to 3R;
  - stop on a touch, target on a trade through, stop first on a two-barrier bar;
  - the breakeven move;
  - the walk's end the bar ending 15:08 CT, the flatten at the worst of the bars ending 15:08-15:10 less two ticks;
  - Stage 2's costs.
- **Kinds:** stop, target, flatten (unresolved), breakeven. "Unresolved" means the flatten kind only.
- **The per-offer coin value at bracket R:** c_i(R) = (net R of the long + net R of the short) / 2. That is the coin's
  expected net outcome at offer i, without its noise (F-01's convention for a twin's expectation). Both sides of every
  offer are walked.

## 6. The forecast

### 6.1 What it forecasts

**IV(d, m)**: the integrated variance a trade entered at mark m on day d sees before the walk's end. It is the sum of
squared one-minute price changes, in points^2, over the bars from the entry bar (stamped m) to the bar ending 15:08 CT:

- the first change is that bar's close less its open (the entry price);
- then each present bar's close less the previous present bar's close.

The definition is within one day's bars, so it never differences prices across a roll. The price change is in points,
not a log return, because the bracket is fixed in points.

### 6.2 The regressors: HAR in normalised form (feature-rules 2)

**M(d, m)** is the mean of IV(d', m) over the **22 prior walked sessions** d' with a value at mark m. It is the HAR's
monthly term, computed from the past only, and it is the normaliser.

| regressor | formula | what it is | reads |
|---|---|---|---|
| y (the target) | log(IV(d, m) / M(d, m)) | the day's variance at this window against its trailing month | day d's bars stamped m .. 15:07 (the label: never a feature) |
| x1 | log(IV(d - 1, m) / M(d, m)) | yesterday's same window (HAR's daily term) | the prior session's bars stamped m .. 15:07 |
| x2 | log(mean of IV over the 5 prior sessions / M(d, m)) | last week's (HAR's weekly term) | the 5 prior sessions' same window |
| x3 | **2 x `rv_tod`** at the alert t = m - 5: log((rv_60 / its median over the 20 prior sessions at the same slot)^2), where rv_60 is the root mean square of one-minute close changes over the bars stamped t - 61 .. t - 1 | today's surprise so far: the last hour's variance against its usual level at that time | day d's bars stamped t - 61 .. t - 1 (that is, m - 66 .. m - 6); the same slots of the 20 prior sessions |

Rules for every regressor:

- **Past only.** Every term reads earlier sessions or day d's bars stamped at or before m - 6.
- **The normalisers are trailing:** M over 22 sessions; the slot median over 20 sessions, at least 10 with a value,
  else missing (the library's rule).
- **x3 is the library's tested feature.** At RTH alerts x3 is exactly 2 x `extended.features` `rv_tod`, and T-2 asserts
  the equality. The family's module extends the same formula to alerts outside 08:30-15:00, which the library refuses.
- **Missing values.** An offer with M, x1 or x2 missing, or with IV of a needed prior window zero, has no forecast and
  is not admitted. The count is reported.
- **Calendars, rolls, DST.** No calendar input. Rolls cannot enter (every term is within a day). Slots are Chicago wall
  clock, so a DST change moves nothing.

### 6.3 Bands, the fit and the walk-forward

**Five bands of marks, each with its own coefficients.**

| band | marks (CT) | terms |
|---|---|---|
| `evening` | 17:00-17:55 | x1 and x2 only: the trading day has under an hour of bars, so x3 is not defined |
| `asia` | 18:00-01:55 | x1, x2, x3 |
| `london` | 02:00-08:25 | x1, x2, x3 |
| `open` | 08:30-09:00 | x1, x2, and x3 **frozen at the 08:30 mark's alert** (bars stamped at or before 08:24) |
| `day` | 09:05-15:05 | x1, x2, x3 |

- The boundaries are Stage 2's customer windows (`resolved_coin.WINDOWS`), with the evening hour and the opening window
  split out.
- **The `open` freeze is a safe default for D-281 (3).** A decision about a trade entered in the 08:30-09:00 window
  never reads a bar of that window. This matters only for Part II, because the family's population starts at 09:05.
- **The family's cells use the `day` band only.** The other four serve Part II.

**The fit.**

- Ordinary least squares of y on an intercept and the band's terms, one observation per (session, mark), each weighted
  one.
- `evening`: 3 coefficients. The other bands: 4 each. In all, **19 fitted coefficients**.
- Deterministic; refused if a band's design matrix is rank-deficient (the failure protocol).

**The walk-forward, inside the choice block only.**

- Test years 2021, 2022 and 2023. Each is fitted on the choice block's sessions before it, less the last 22 sessions.
- A forward walk needs no purge: no training label resolves in a test session (each IV ends at 15:08 the same day).
- The 22-session gap (the HAR's longest window) is kept because it is harmless.
- These out-of-fold predictions feed stages A and B.

**The final forecast.**

- Fitted on every choice-block session with a value (2020 after its warm-up, to 2023-12-29).
- Its coefficients and the calibration (6.4) are serialised to canonical JSON and hashed.
- **The hash is pinned in a decision row before the judged block is read.** The judge's entry point cannot fit (T-9).

### 6.4 From a variance forecast to the chance of being open at the end

1. **The forecast variance:** V_hat(d, m) = M(d, m) x exp(y_hat), the forecast's median, in points^2.
2. **In stop units:** u = V_hat / S^2, with S = 37.5 points. The bracket at R has a = 1 and b = target_ticks(R, 150) /
   150 (Stage 2's rounding).
3. **The textbook probability:** Psi_b(u) by section 1 (i)'s series, or by the method of images for u < 0.05 (they
   agree to 1e-9: `tests/test_family_r_band_exit.py`). It is clipped to [1e-6, 1 - 1e-6].
4. **Calibrated per band:**

       p_hat(i, R) = sigmoid(alpha_band + beta_band x logit(Psi_b(u)))

   - alpha and beta are fitted by maximum likelihood on the training fold's walks: every (offer, side, R the table
     offers), the flatten kind as 1.
   - Both sides are pooled, because the coin chooses the side.
   - In-fold, from the training fold's own fitted forecasts; applied out of fold.
   - **10 fitted values.** Under exact Brownian motion with a perfect forecast, alpha = 0 and beta = 1.
   - The calibration absorbs what the textbook leaves out: the forecast's own error, the breakeven move (a resolved
     exit), the tick grid, jumps.
   - **It reads the walks' kind columns only** -- resolution, side-free, as D-525 (4)'s cutoff does -- never a net R,
     a gross or a side.

### 6.5 The rule

- **Admission at R:** offer i is admitted at bracket R iff **p_hat(i, R) <= q, with q = 0.05**: D-212's line, applied
  per offer.
- p_hat rises with R when beta > 0 (Psi rises with the target), so admission at R implies admission at every smaller R.
  beta > 0 is checked (9, A4).
- **Its cap:** R_cap(i) is the largest R the table offers (`zero_edge_decomposition.policy_rrs`) at which offer i is
  admitted.
- **In a design, an admitted refused offer is offered at its cap.** A table leaf asking a larger R takes the cap with
  its dollar risk unchanged: Stage 2 D-639 (2)'s rule, per offer.
  - It is implemented as a plain-data rewrite of the offer's outcome columns above its cap (18.1). No engine file is
    touched.
  - An offer is added only if the cell's filter admits it (7.1), so its cap is at least the cell's R. D-639 (2)'s
    cell-level "collect leaf" test is not applied per offer: the filter already sets the floor on the cap.

## 7. Part I -- the cells and the placebo-selection twin (E-023 (2))

### 7.1 The cells

| cell | the filter | read at | its design (for C2, the floors and the scorecard) |
|---|---|---|---|
| `adm@1` | F_1(i) = 1 iff p_hat(i, 1) <= 0.05 | R = 1 | P-16 plus every refused offer with F_1 = 1, each at its cap |
| `adm@1.5` | F_1.5(i) = 1 iff p_hat(i, 1.5) <= 0.05 | R = 1.5 | P-16 plus every refused offer with F_1.5 = 1, each at its cap |
| `adm@3` | F_3(i) = 1 iff p_hat(i, 3) <= 0.05 | R = 3 | P-16 plus every refused offer with F_3 = 1 (cap 3) |

- R = 1, 1.5 and 3 are the table's three asks: the evaluation's 1.5R, the funded opening's 3R, and 1R after it
  (handoff 2.5; `u_value_map.csv` section `records_leaf`).
- **k_cells = 3**, each counted whether killed or read.
- P-16's own offers are unchanged in every cell. Only refused offers are added.

### 7.2 The twin and the estimand

**The twin.** E-023's placebo selection: a random filter that fires on the same share of the same population. Here it
fires on the **same number of refused offers in each stratum s = (mark, calendar year)** as the cell's filter, drawn
uniformly without replacement. So the time of day and the year cancel, as supply and schedule do, and only the
forecast's choice of **day** is measured.

**The estimand, the lift over the twin at R:**

    L_R = (1 / N_F) x sum over admitted offers i of ( c_i(R) - mu_s(i)(R) )

- mu_s(R) is the mean of c(R) over **all** offers of stratum s: the placebo's exact expectation;
- N_F is the number of offers the cell admits.

L_R is exactly the expected difference between the cell's admitted offers and the twin's, without the twin's draw
noise. F-01 did the same for its coin twin, with the seeded draw beside.

**The seeded draw.** The seeded twin (`default_rng([20261978, 0])` on the judged block) is computed and reported beside.
*Interpretation for the lead:* if E-023's word "seeded" is read as requiring the drawn twin in the line, C1 runs on the
drawn twin and the exact form goes beside. Either way, this file fixes which form it is before the pin.

**The session series.** z_s = the sum over the cell's admitted offers in session s of (c_i(R) - mu_s(i)(R)), so
L_R = sum of z_s / N_F. Q-16's statistic tests this series (11, C1).

**What L_R measures (section 1 (iv)).** By the textbook, the avoided flatten's cost and the exit ticks' composition --
expected small and positive if the forecast sorts the offers. That the lift exists only through costs is the reason
section 11 reads the lift beside under the `close` flatten convention too.

## 8. Parameters: fixed, fitted, searched, dropped

| parameter | what it is, in a phrase | class | value | source or reason |
|---|---|---|---|---|
| market, bars | what is traded and read | fixed | NQ 1-minute bars; MNQ micros sized by the table | E-002 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md; `config/windows.yaml` |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | feature-rules 4; CHARTER 3 |
| base | the schedule the forecast acts on | fixed | P-16 as registered (5.1) | E-004, E-010 |
| stop | the loss distance | fixed | 150 ticks (37.5 points) | P-16 |
| population marks | which offers the filter may admit | fixed | grid marks 09:05 .. 15:05 CT | D-618 (3); 5.2 |
| sessions | days traded | fixed | P-16's walked day kinds | D-525, D-533 |
| entry | how a trade starts | fixed | market at the first bar at or after the mark; by hand; the forecast an alert at m - 5 | D-266; E-008 |
| walk | how a trade ends | fixed | `extended.walker.STAGE2` | E-011 |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| cells' R | the bracket the lift is read at | fixed | 1, 1.5, 3 | the table's three asks |
| offered R | the R a cap is chosen among | fixed | the table's (`policy_rrs`) | D-639 (2) |
| forecast target | what is forecast | fixed | IV over the walk window (6.1) | section 1 (i) |
| HAR terms | daily, weekly, monthly | fixed | 1, 5 and 22 prior sessions | Corsi 2009 |
| so-far term | today's surprise | fixed | 2 x `rv_tod` at m - 5 (60 minutes; 20-session slot median, at least 10) | `extended/features.py`; Hong et al. 2023's spirit |
| bands | where coefficients differ | fixed | five (6.3) | Stage 2's windows |
| the `open` freeze | no opening-window bar read for its marks | fixed | x3 at the 08:30 mark's alert | D-281 (3) safe default |
| HAR coefficients | the forecast's weights | **fitted in-fold** | 19, by least squares | 6.3; needs the D-621 (4)(d) row |
| calibration | textbook to observed | **fitted in-fold** | 10, by maximum likelihood | 6.4; the same row |
| Psi | variance to open-at-the-end | fixed | the textbook series and images; clip 1e-6 | Karlin & Taylor; the synthetic test |
| q | the per-offer resolution line | fixed | 0.05 | D-212 (2), D-308 (3) |
| strata | what the twin matches | fixed | (mark, calendar year) | E-023 (2): the same population, the same share |
| folds | the walk-forward | fixed | test years 2021, 2022, 2023; expanding; a 22-session gap | feature-rules 4 |
| stage B | the screen and the pick | fixed | section 10 | F-B's form |
| C1 | the pass line's test | fixed at the pin | Q-16's calibrated statistic **[Q-16]** at 0.05 / (k (k + 1)) | E-023 (2) |
| C2 | the least worth | fixed | $500 a year at C1's bound, on the design's routed trades by place | F-02, F-B |
| valuation base | where a win is priced | fixed | `p16` | `u_value_map.csv` |
| K1 | the least supply | fixed | 21 admitted offers in each of 2021, 2022, 2023 | a month of sessions |
| MDL factor | when the family is only a screen | fixed | 3 | F-B 8 item 8 |
| a VIX or VXN forecast | the scout's second forecast | **dropped** | -- | not on disk; whether Cboe's history is free without sign-up is unverified (the scout's unknown 6); D-136 read it on 2009-2014; a later family |
| price durations as a second forecast | Hong et al. | **dropped** | -- | a second forecast doubles the cells; it is the natural next family if this one reads |
| q searched | other resolution lines | **dropped** | -- | each value a variant; D-212's line is the rule |
| per-mark coefficients | finer fits | **dropped** | -- | hundreds of fitted values; the normalised form removes the clock |
| a free logistic on raw terms | instead of Psi | **dropped** | -- | more freedoms; Psi is textbook, the calibration two numbers a band |
| (u3) routing the opening | the slot | **dropped here** | -- | family O's population and twin (0.1) |
| the opening-window marks | 08:30-09:00 | **out of the population** | -- | P-16's own; D-281 (3) |
| the 25- and 12.5-point bases | US-hours cells | **dropped** | -- | P-15's U1 identity is open (Q-22); the window cells' identities are not reproduced here; a later family |
| R above 3 | longer targets | **dropped** | -- | not walked (the grid ends at 3R) |
| the `adm` and `R-cap` crossing | a combined cell | **dropped** | -- | `R-cap` is a described lever (E-023 (1)); read beside a carried pick only (12) |

**Searched: nothing.** The trial count is the three cells.

## 9. Stage A: the gates, before any outcome (choice block)

Stage A reads **bars** (the forecast) and the walks' **kind columns** (resolution, side-free, as D-525 (4) does). It
reads no net R, gross or side of the family's cells; the identities compare hashes and registered rows. Every kill is
counted and recorded.

**A1. Identities (refusing).** Any failure stops the family; the failure protocol applies.

1. E-011's walker identity holds at the build's commit.
2. The family's builder with the filter off -- no offer admitted -- gives P-16's trades, `TRADES_SHA256` exactly.
3. Through the family's gate call: P-16's gate paths, 500 paths at seed 20261206, every `PATH_COLS` column to 1e-6
   (E-004's comparison).
4. Through the scorecard adapter: P-16's U1 start rows `p16`, both arms, every start (E-010's comparison).
5. Q-17's readings-beside adapter holds its own identity as merged (b7232ba, `identity/user_beside_identity.py`).

**A2. No look-ahead (refusing).** The forecast's shift-invariance test (T-2):

- every bar stamped at or after m - 5 is replaced by a seeded random walk (`[20261971, j]`), and separately deleted;
- p_hat(i, R) at every R must be unchanged;
- at no fewer than 200 (session, mark) cuts, including the first marks after 17:00, the `open` freeze, a roll day and
  a DST change.

**A3. The forecast's skill: the positive control.**

- On 2021-2023 out of fold, per band: the per-session mean squared error of y under the HAR against under y = 0 (the
  trailing month alone).
- The improvement's one-sided 95 % lower bound must be above zero, by circular 21-session blocks, 2,000 draws
  (`[20261970, 0]`), in every band with offers.
- A fail means a defect or a market without the stylised fact, so the failure protocol runs and the family waits for
  the lead's ruling under a row. It is not a kill line.

**A4. Calibration and resolution, on the refused population, 2021-2023 out of fold (K2, a kill line).**

- (a) beta > 0 in every fold of the `day` band. Else the map is inverted: the failure protocol.
- (b) For each cell R, among the offers its filter admits, the realised unresolved share (both sides pooled) must be at
  most 5 % at R and at every smaller R the table offers, overall and in each of 2021, 2022 and 2023. Else the cell is
  **killed**. q is never moved.
- (c) Reported: the reliability table (realised against predicted, by p_hat decile, per band and year), and the same
  for P-16's own marks (Part II's domain).

**A5. Information beyond the clock (K-info, a kill line).**

- For each cell R, on the refused population, 2021-2023 out of fold: the **within-stratum AUC** of p_hat(i, R) for the
  unresolved indicator at R. It is the probability that an unresolved walk has a higher p_hat than a resolved walk of
  the same (mark, year), pooled over strata by their pair counts.
- Its one-sided 95 % lower bound (blocks as A3, `[20261970, 1]`) must be above 0.5. Else the cell is **killed**: the
  forecast does not sort offers within a mark, so its selection cannot beat the placebo except by chance.
- Beside, the selection's resolution effect in plain form: the admitted offers' unresolved share against a seeded
  placebo's of the same counts per stratum (`[20261978, 1]`). Resolution only.

**A6. Supply (K1).** For each cell: the admitted offers per session, by year and by mark hour. A cell with fewer than
21 admitted offers in any of 2021, 2022 and 2023 is **killed** (void).

**A7. Realised risk.** The stop is P-16's. P-14's allowance-capped form is reported (E-022 (1)).

**A8. Power on record.**

- For each surviving cell: the minimum detectable lift (MDL) at the family's level on the judged block, from Q-16's
  power function **[Q-16]**, at the judged block's session count and the cell's admitted offers per session.
- It is set against the value bar: the lift in net R worth $500 a year at the cell's uses, by section 10's first-order
  formula.
- If the MDL exceeds the bar by more than a factor of 3 at every surviving cell, the family is **declared a screen**
  (section 14 says what its pass means).
- Written before stage B reads any net R.

## 10. Stage B: choose on the choice block (2021-2023, out of fold)

1. **The statistic:** for each cell surviving stage A, L_R (7.2) on 2021-2023 with the out-of-fold forecasts; strata
   (mark, year) within those years.
   - Its bootstrap: circular moving blocks of 21 sessions, 2,000 draws (`[20261972, 0]`). Each draw recomputes L_R,
     the stratum means included, on the resampled sessions.
   - SE_c is its standard deviation over draws.
   - The family-wise critical value q_B is the 95th percentile over draws of max_c (L\*_c - L_c) / SE_c (one-sided
     0.05).
2. **Kill B:** no cell with L_c / SE_c > q_B. The family **closes**, and the judged block is not read.
3. **The pick:** among cells above q_B, the largest **first-order valued lift** at its lower limit L_c - q_B SE_c:

       $ a year = (L_c - q_B SE_c) / (1 + R_c) x u_c x mean_dv(p) ,

   maximised over the places p that ask R_c:
   - (b) the evaluation (1.5R);
   - (c) the funded opening (3R);
   - (d) funded later (1R);
   - (e) paid (any R).

   The terms:
   - mean_dv(p) is `u_value_map.csv` section `place_values`, base `p16`: a win over a loss in dollars. A lift of
     lambda R per trade is lambda / (1 + R) of win probability, to first order;
   - u_c is the cell's admitted offers a year on the choice block, capped at `trades_per_year_forward(p)` x the share
     of the place's recorded leaf-days at R_c (`records_leaf`; F-B's rule).

   **This ranking assumes the lift is uniform over admitted offers.** The money is decided by C2 on routed trades.
   Ties go to the smaller R.
4. **Stage B2: the level for this family's persistent selections**, before any judged read (F-B's M-4 form).
   - Volatility clusters, so the admitted offers cluster in fast stretches of sessions.
   - The null: the choice block's own deviations c_i(R) - mu_s(R) at the pick's R, times synthetic selections
     independent of them, with the pick's per-stratum counts and its run lengths of admitted sessions (resampled from
     its out-of-fold admissions).
   - At least 1,000,000 replications (`[20261975, j]`).
   - Q-16's test **holds** if the upper 95 % Monte Carlo limit of its rejection rate at the family's level is at most
     1.5 times the level. Else stage C reads the simulated critical value.
   - Fixed now.
5. **What it spends:** nothing of the program's level. One cell reaches judgement.
6. **The record:** every cell's stage A and B readings are written to the result file's `choice` section before the
   judged block is read.

## 11. Stage C: judge the pick once, on the judged block -- the pass line (E-023 (2))

What is judged: the pinned forecast (its hash in the judge's manifest), the pick's R, and its filter on the judged
block's refused offers, strata (mark, year) within the judged block.

**The design passes only if every line holds. A fail of any line closes the family**, its reason in a decision row.

- **C1, the pass line:** L_R over the judged block's admitted offers. Its one-sided lower bound at **0.05 / (k (k + 1))**
  must be above zero, by **Q-16's calibrated statistic for the placebo-selection comparison [Q-16: its name, module
  and commit; E-023 asks Q-16 to calibrate it]**, or by stage B2's simulated critical value where B2 required it. This
  file is not pinned until Q-16 is merged.
- **C2, worth something where it is used:**
  - The design's gate campaign on the judged block: P-16 plus the pick's admitted offers, each at its cap; 500 paths;
    the bound arm; seed **20261973**.
  - **The bound arm's shift is P-16's registered shift at each R**, for this design and for P-16 alike (here and in
    sections 12 and 13). Every trade is a P-16-schedule coin trade walked the same way, so a pair differs only by the
    lever. The alternative, each design's own bounds by the base's era rule, would be estimated over both blocks again
    (the F-P review's N2) and would move with the admitted offers' outcomes.
  - It records, for every simulated trade j taken from an admitted offer, its offer i(j), the R the table took R_j,
    and its place p(j).
  - Per judged session s: z_s = sum over those trades j on session s of mean_dv(p(j)) x (c_i(j)(R_j) -
    mu_s(i(j))(R_j)) / (1 + R_j) / (paths x years per path), with mu the trade's stratum mean (7.2).
  - **V = sum of z_s dollars a year. C2: V's one-sided 95 % lower bound** -- the session count times the lower bound of
    mean(z_s) by Q-16's statistic, the routing weights held fixed -- **at least $500 a year.**
- **The floors (CHARTER section 3; E-022), all on the design's own judged-block run:**
  - (i) **every offered R resolving:** the design's offers -- P-16's at every R, the admitted ones at every R up to
    their cap -- unresolved at most 5 % at each R, overall and in each of 2024, 2025 and 2026 to 07-16 (a year with
    fewer than 63 sessions pooled with its neighbour, D-604). Also the share of the design's taken trades flattened,
    at most 5 % overall and in each year;
  - (ii) realised risk in P-14's registered allowance-capped form (E-022 (1));
  - (iii) **the long-run gate:** growth on the required bankroll at the bound above zero, on this design's own
    campaign (seed 20261973), never taken from P-16's registered pass (E-022 (2));
  - (iv) every firm rule verified (Stage 2's ledger);
  - (v) conduct tier 1 (section 3).
- **Beside, deciding nothing:**
  - L_R by calendar year, and at each R in net R;
  - the kind shares (target, stop, flatten, breakeven) of the admitted offers against their strata;
  - **L_R under the `close` flatten convention** (`DECLARED_F01`'s flatten, the other rules `STAGE2`'s): how much of
    the lift is the flatten convention;
  - L_R under Q-20's corrected moves (`STAGE2_BE_BOTH`, merged b7232ba);
  - the seeded twin's draw (`[20261978, 0]`);
  - the reverse walk-forward: the forecast fitted on the judged block and read on 2021-2023, draws `[20261972, 1]`;
  - the forecast's judged calibration and within-stratum AUC;
  - planned against realised supply;
  - Stage 2's S-program guard (the design's paired growth at the bound against P-16's, D-568 (2)), reported, never a
    line.

## 12. The journey scorecard -- beside, never the pass line (CHARTER section 2; E-008, E-014, E-015, E-023)

**Which designs.** Read for the pick only, after stage C has read, whatever its verdict. A family closed at Kill B
reads none.

- The design (P-16 plus the pick's admissions) is read against **P-16** (paired: same starts, same coin, same seeds),
  with R\* = P-14 beside.
- If the pick is carried, the design with Part II's `R-cap` added is read beside too (described, E-023 (1)).
- Journeys come from the vendored U1 replay, through Q-17's adapter for the readings beside (`extended/user_beside.py`, merged b7232ba).
- Per measure, the choice section's purges by horizon (`u_select.block`, the F-P review's F6).

**What is read.**

- **P** and the guarded measures S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c; the reported-only S2, S3d, S6, Q
  (`vendor/stage2/docs/USER_MILESTONES.md`).
  - S3c is reported with the caveat that the design adds trades to P-16's stream (E-008 compares it within one stream).
- **The journey variables (E-014):**
  - sessions and cash to the first pass; sessions and cash to the first payout;
  - **sessions to break-even** (the first session whose cumulative net cash is at or above zero, daily), the share of
    starts reaching it by months 1, 2, 3, 6 and 12, and the share that later fall back below zero;
  - **the path's evenness:** the share of months with a positive net change, the longest run of months without a
    payout, the spread of monthly net, the deepest fall of cumulative net from its running high after break-even,
    payouts per month, the largest single month's share of the year's payouts.
- **Every measure as a distribution over start days** (median, p10, p90), on the starts from 2021-01-04 (the first
  out-of-fold year; no forecast exists for 2020's offers) and on the judged block's starts. Each carries its uncertainty from the effective number of independent starts and the start day's share of
  the variance (`user_drivers.csv` section `design_vs_luck`).
- **The paired readings:** the per-start difference against P-16 as a distribution, and the shares of starts better,
  equal and worse at months 1, 2, 3, 6 and 12. Any draws come from `[20261976, 0]`.
- **The supply reading:** funded trades per live account-day and the share of account-sessions without a trade,
  against P-16's (1 (v)).
- **The frontier** on P, S1, S3a and S5a; **the menu** under E-015's limits once the operator approves them, as
  **flags only** (a limit never fails a design, E-015 (3)); **the evenness trade-off curve** (E-015 (4)).
- **E-007 (e)'s readings** (Q-17's adapter): the denial ladder at 10, 25 and 50 % (draws `[20261976, 1]`); the
  placement on; the binding Focused Trader models; all-accounts forfeiture; P by month, mean net, CVaR10, P under a
  bankroll limit, the effective sample size and the minimum detectable difference.
- Stage 2 D-621 (3)'s rule against P-14, beside as E-008 keeps it, deciding nothing.
- **Not modelled, said wherever the scorecard appears:** a user who stops when their own money runs out, the user's
  time, taxes.

---

## 13. Part II -- the described reading `R-cap` (E-023 (1)): the funded opening's R where it resolves

**Status:** a described reading. **Never carried, no program family number, nothing of the budget spent.** It is
declared here and pinned with this file, so nothing in it is chosen after a look. *If the lead prefers described
readings in files of their own (F-P's redraft, Q-42, may set the form), this section moves unchanged.*

### 13.1 What it is

- **On P-16's own offers,** every offer's outcome columns above its forecast cap R_cap(i) (6.5) take R_cap(i)'s
  outcome.
  - The forecasts are the out-of-fold ones on 2021-2023 and the final forecast from 2024-01-02.
  - No offer of 2020 has an out-of-fold forecast, so the reading starts from 2021-01-04.
- A table leaf asking more than the cap takes the cap, its dollar risk unchanged. An offer at which no R the table offers
  is admitted keeps the table's smallest R. **No offer is dropped or added.**
- **Where it binds:** on the 3R ask -- the funded opening (handoff 2.5) -- at marks and on days forecast slow, and on
  any other leaf whose R exceeds a cap.
- The bands `evening`, `asia`, `london` and `open` (with its freeze) serve it.

### 13.2 What it changes, stated exactly (the F-P review's F10)

- The offered trades and their entries are P-16's. What changes is **the bracket** of an offer whose cap is below the
  ask.
- So, after the first capped trade, everything that follows can diverge: an account's balance; the next leaf; which
  offer the router gives to which account (a capped opening resolves sooner and frees the slot); purchases; fees.
- **The pairing is on start days with identical offers, not identical executed trades.**

### 13.3 What is read (all on the verdict arm, on the starts from 2021-01-04 and on the judged block's starts, paired with P-16)

- **(a)** Every measure of section 12, its paired distribution, and who it helps and hurts at months 1, 2, 3, 6 and 12.
- **(b)** The mechanics:
  - the share of P-16's offers capped below 3R, by band and year;
  - the share of the design's funded openings capped, and the R they took;
  - the forecast hold time of capped against uncapped openings (stop x target / the forecast variance);
  - the realised minutes the firm's slot was held by openings, against P-16's. **This is (u3)'s question, answered
    descriptively.**
- **(c)** The evenness trade-off: one point of P against each evenness measure, beside P-16's.
- **(d)** The denial ladder, the placement and the Focused Trader models, as section 12.
- **The prior, disclosed:**
  - Stage 2 found every change to the funded leg (smaller, flatter, equal days) worse for a user (handoff 3.2);
  - a capped opening gives up the place of greatest value of a win (`u_value_map.csv`, place (c));
  - by the LeBaron effect, the slow days it caps are where a 3R coin might win more than 1/4 (the scout's 5.2).
- Expected: worse or level on P. Its reading is the record of what a target chosen by resolution costs or gains a user.

### 13.4 Its identity and its run

- With the cap disabled (every cap 3), the design is P-16 bit for bit. A1 items 2-4 hold for it.
- Run once with the family, from the same clean checkout. Its draws, if any, come from `[20261976, 2]`.
- Results go to its own result file (section 19) with `prereg_id` this file's and `numbered = false`.

---

## 14. What a pass and a fail mean

**CARRIED** (Part I: every line of stage C and every floor holds).

- A development finding on a late-development block.
- The design -- P-16's schedule plus the pick's forecast admission -- takes a registration id (Stage 2 D-621 (9)'s house
  form), a model card (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`: the forecast's coefficients and calibration),
  its registered development test, the auditor and **one confirmation** (section 15), which carries the decision
  (D-189).
- If stage A declared the family a screen, a pass is still CARRIED, and the carrying row says the development read was
  a screen at its MDL ratio.
- What a user is told is the scorecard as a distribution (section 12), never one number.

**CLOSED** at stage A (an identity, A3's control unresolved, or every cell killed), at B (Kill B), or at C (a line or a
floor).

- The reason goes in a decision row.
- A close at B or C reads **"no selection lift above the MDL at this family's level"**, never "a forecast does not
  help". If the scorecard beside shows supply gains, they are recorded as supply, which E-023's twin does not credit.
- **The closure binds** (D-277's boundary): a later family on this forecast or this population names this closure,
  says what changed and why it is a different hypothesis, and is not judged on this family's judged block.

**Part II** closes by construction with its reading. That reading is the result.

## 15. The confirmation, declared before any development read

- **The window:** NQ from **2026-07-17** (`config/windows.yaml`, `reserve`). It is not on disk and never read until a
  carried design is registered. It is **a purchase, the operator's**, stated in `docs/OPERATOR_SETUP.md` and waited
  for. It would be NQ's fourth confirmation window, **the operator's decision** (D-107, D-461).
- Stage 2's draft P-16 confirmation (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`) and F-02's and F-B's drafts
  target the same window. If any test reads it first, the lead records that before registration, and the operator
  decides whether it can still confirm this pick.
- **What it tests -- the pick's trades, not P.** With the pinned forecast, the pick's R and q fixed:
  - C1 on the window's refused offers, one-sided at the registered 0.05, by Q-16's statistic (with B2's simulated
    critical value re-simulated at the window's length where B2 required it, `[20261975, 10 + j]`), the bound at
    0.05 / N beside (D-189's form);
  - C2 at the 95 % bound, valued with stage C's per-place shares and uses (the window is too short for its own
    campaign), at least $500 a year;
  - floor (i) on the window, overall and in every calendar year with at least 63 sessions (a stub year pooled, D-604);
  - Q-16's draws, if any, from `[20261974, 1]`; the seeded twin's from `[20261978, 2]`.
- **What it cannot test: P.** Six months is about 126 sessions, about 63 starts with a month-3 horizon: no interval on
  P exists there (the phase-0 red team's M1). The scorecard on the window is descriptive.
- **How much data:**
  - at least six months (D-604);
  - and at least the months at which the pick's expected admitted offers (the lower of its two blocks' rates) reach the
    count at which Q-16's statistic, one-sided at 0.05, has 80 % power for a lift equal to **the pick's judged lower
    bound at the family's level**.
  - That count is computed when the pick is carried and written in the carrying row, before any confirmation data
    exist.
  - If it is more than the operator will buy, no confirmation is registered, and the pick stays a development finding.

## 16. Seeds -- proposed 20261970-20261979, checked unique, for the lead to confirm at pinning

| seed | what it draws |
|---|---|
| 20261970 | stage A's bootstraps: `[20261970, 0]` A3's skill, `[20261970, 1]` A5's within-stratum AUC |
| 20261971 | the build's shift-invariance test's replacement walks (A2, T-2): `[20261971, j]` |
| 20261972 | stage B's bootstrap `[20261972, 0]`; the reverse walk-forward's beside `[20261972, 1]` |
| 20261973 | the design's gate campaign: C2's routing, the long-run gate floor, the scorecard; 500 paths |
| 20261974 | Q-16's statistic's draws, if any: `[20261974, 0]` stage C, `[20261974, 1]` the confirmation |
| 20261975 | stage B2's replications `[20261975, j]`; the confirmation's re-simulation `[20261975, 10 + j]` |
| 20261976 | the scorecard's paired draws `[20261976, 0]`; the denial ladder for this file's designs `[20261976, 1]`; Part II's draws `[20261976, 2]` |
| 20261977 | the build's synthetic tests: `tests/test_family_r_band_exit.py` (`[20261977, j, ...]`, j = 0..5); T-3's synthetic judged block `[20261977, 10]` |
| 20261978 | the seeded placebo-selection twin: `[20261978, 0]` stage C (beside), `[20261978, 1]` stage A's resolution comparison, `[20261978, 2]` the confirmation |
| 20261979 | reserved; unused, and every result file says so |

**The check (2026-11-16).**

- `grep -rIowh --exclude-dir=.git -E "2026197[0-9]" .` over the whole working tree, the vendored snapshot and its
  results included, found 20261970 and 20261979 only in this item's brief (`docs/briefs/Q-38_2026-11-16.md`), as the
  proposal's range.
- Without word bounds, one more hit: a digit run inside a longer number in one vendored result file -- not a seed.
- `git grep -E "2026197[0-9]"` on every local and remote branch, and on every commit of the repository's history
  outside `vendor/`, found the same brief and nothing else.
- Re-checked after this file and its test were written: they add only these uses.
- **Not searched:** Stage 2's working tree beyond its vendored snapshot. Its decision log and scripts are vendored and
  were searched.

**Neighbouring blocks, taken:** 20261910-19 (Q-16), 20261920-29 (Q-17, Q-20), 20261930-39 (F-02), 20261940-49 (F-P),
20261950-59 (Q-18), 20261960-69 (F-B).

**Inherited, used only as their owners registered them:**

- 20261102 (P-16's coin, every grid mark);
- 20261206 (P-16's gate, the identity);
- 20261131 (P-14's, beside);
- 20261600 + i and 20261700 (Stage 2's coin sequences and D-621 (3), beside only).

## 17. Multiplicity and the budget

1. **k.** The next free program family number at the pin, with level 0.05 / (k (k + 1)), written by the gatekeeper in
   the pinning row.
2. **Counted:**
   - **3 cells** (`adm@1`, `adm@1.5`, `adm@3`), each counted whether killed at A, closed at B or read at C;
   - **0 searched configurations**;
   - **29 fitted values** inside the walk-forward (19 coefficients, 10 calibration), none searched.

   The identities, the controls (A3, A5's placebo comparison, B2's replications), the seeded twin and the readings
   beside are not trials: nothing is chosen from them.
3. **One cell reaches judgement.** C1, C2 and the floors are an intersection at one level. Stage B spends nothing of
   the program's budget.
4. **Part II** is one described reading under E-023 (1): no number, no budget, recorded in its own row.
5. **The program's honesty sentence:**
   - Stage 2 ran programs S and U on this window, each with its own 5 %;
   - the late marks' average resolution has been read on both blocks (section 2);
   - the development level is a screening threshold, and the decision is carried by one confirmation on unread data
     (D-189), if the operator buys one.

## 18. The build: adapters, identities and tests (after the pin, before any reading)

### 18.1 The code (in `extended/`, never in `vendor/`)

1. **`extended/resolution_forecast.py`.** IV, M, x1-x3, the bands, the least-squares fit, Psi (the series and the
   images), the calibration, p_hat and R_cap.
   - Bars come only through the Q-32 reader.
   - The library's grid and median helpers (`extended.features.grid`, its trailing median) are reused, not copied.
2. **The cell builder.** P-16's cell as `rc_width_screen.build` builds it, with this repository's walker. The added
   offers are the population's admitted ones, their outcome columns above their cap rewritten to the cap's (a
   plain-data transformation of the trades frame).
   - The R a trade actually took is recorded beside, so a record never shows a capped trade as 3R.
   - No vendored attribute is substituted (the lesson of E-011's first run).
3. **The estimand.** c_i(R), the strata means, z_s, L_R, and C2's per-trade valuation from the gate campaign's routed
   trades by place. That uses family B's place-recording adapter (`prereg/DRAFT_F-B_multifeature.md` section 20 item
   8), held to the same identity: P-16's registered campaign re-run as U2 ran it reproduces `u_value_map.csv`'s
   `trades_per_year_records` for `p16`.

### 18.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-1 | **written now:** `tests/test_family_r_band_exit.py`. Psi's series equals the images; it falls with u, rises with R and integrates to R; a lattice walk converges to it; at two volatilities the target share is 1/(1+R) and the exit time scales as 1/variance; a volatility forecast on persistent days moves the open share and the target share but not the mean outcome; with a flatten cost the lift over the population mean is that cost times the open-share drop (seeds `[20261977, ...]`) |
| T-2 | the forecast's shift invariance (A2): replacing, and deleting, every bar stamped at or after m - 5 changes no p_hat; the `open` freeze reads no bar stamped 08:25 or later; x3 equals 2 x `rv_tod` at every RTH alert; not all-NaN, not constant |
| T-3 (heavy, under the run lock) | stages A, B and B2 and the final forecast's hash are byte-identical when every judged-block bar is replaced by a seeded synthetic walk (`[20261977, 10]`) |
| T-4 | the builder with the filter off gives P-16's `TRADES_SHA256`; with every cap 3 Part II's design is P-16's trades |
| T-5 | the cap: above R_cap every outcome column equals R_cap's; the dollar risk unchanged; under Part II no offer is dropped or added; the R taken recorded |
| T-6 | the population: only grid marks 09:05-15:05 on P-16's day kinds; never a news-cut mark, an FOMC day or an early close; never a mark in 08:30-09:00 |
| T-7 | the least-squares fit equals a direct normal-equations solve, and the calibration a Newton solve, on synthetic data to 1e-8; a planted HAR process is recovered with the right signs; on synthetic bars with clustered variance the forecast beats y = 0 and the calibrated p_hat is calibrated within its Monte Carlo band |
| T-8 | the reader: every bar and walk read goes through `extended/reader.py` with its purpose; an untagged judged read raises (Q-32's own tests, re-run at the build's commit) |
| T-9 | the judge's entry point reads the frozen forecast by its hash and cannot fit; stage C reads the pick from stage B's result file by its sha256 |
| T-10 | the estimand: on synthetic offers with a planted kind-dependent cost, L_R equals the cost times the open-share difference (T-1's identity on the family's own code); on a random filter, L_R's expectation is zero |
| T-11 | Q-16's statistic holds its size on a synthetic persistent selection series (B2's machinery on synthetic data) |
| T-12 | this file's seeds appear nowhere else in the build's commit |
| T-13 (slow) | A1 items 2-4 at 4 paths and 4 starts; the full 500 paths and every start are the run's first stage (heavy) |

## 19. Outputs, weight and the run

- **Files**, each with its sidecar manifest through `extended.results.write_result`:
  - `results/fr_resolution.csv`, sections `identity`, `forecast`, `calibration`, `supply`, `power`, `choice`,
    `level`, `judged`, `floor`, `beside`;
  - `results/fr_journey.csv`, the scorecard of section 12;
  - `results/fr_rcap.csv`, Part II.

  Each manifest carries: `prereg_id` this file's F-id (Part II's with `numbered = false`); the cell counts (3 cells, 0
  searched, 29 fitted values); every seed and parameter; the frozen forecast's hash; the sha256 of
  `vendor/DATA_MANIFEST_stage2.sha256`. Every file is EXPLORATORY until a carried design is registered.
- **The run.**
  - Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to its end.
  - **Weight: heavy.** It walks every grid mark of every session at 150 ticks on both sides (E-011's P-16 run is the
    nearest measure of memory). Then the gate campaigns and the U1 replays of the pick's design, P-16 and Part II's,
    on two arms: hours, at two workers.
  - The stages run in order -- A (identities first), B, B2, the hash pinned, C, the floors, the scorecard, Part II.
    Each stage's file is written before the next reads anything. A kill stops the sequence (Part II still runs: it is
    described whatever Part I's fate).
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run is read.

## 20. Open before the pin

**The lead's:**

1. **Q-16 merged**, with its calibrated statistic for the placebo-selection comparison (E-023's follow-on) and its
   power function. Its name, module and commit go where this file says **[Q-16]**.
2. **Q-32 merged** (the reader and the read ledger), and the purposes of section 4 item 3 accepted.
3. **The row Stage 2 D-621 (4)(d) needs:** fitted coefficients and a fitted calibration, inside the declared
   walk-forward only. It is family B's row too (E-019); one row can serve both.
4. **The twin's form:** the placebo's exact expectation in C1, the seeded draw beside (7.2); or the drawn twin in the
   line.
5. **Where Part II lives:** in this file, or in a described-reading file of its own in the form Q-42 sets.
6. **The verdict arm's shift:** P-16's registered shift at each R for every design here (section 11, C2), rather than
   each design's own bounds.
7. **(u3) handed to family O** (Q-37) as a declared state, with the LeBaron sign (0.1).
8. **The value bar for a lever whose textbook lift is a cost effect.** $500 a year is F-02's and F-B's bar. Here the
   lift is, by section 1 (iv), mostly the flatten convention's cost avoided. The drafter's expectation, recorded now,
   is a close at C. The lead decides whether the family is worth its k. **Pinning and running it as declared, with that
   expectation on record, is the drafter's proposal**, because its stage A answers questions wanted anyway: does a
   forecast sort the late offers, and how many would resolve.
9. **The family number:** F-02 and F-B may be pinned first.
10. **The seeds** (section 16) confirmed unique at the pin.

**The red team's, in particular:**

- whether the `day` band's x3, which at marks from 09:05 reads the last hour including 08:30-08:59's bars as a
  volatility input, is inside D-281 (3)'s closed branch. This draft reads it as outside: no entry in the window, no
  direction, no opening-range level. Family B's draft holds the same reading (its section 22 item 2). If held inside,
  x3 for the `day` band is frozen at the 08:30 mark's alert as for `open`, by a redraft before the pin;
- whether strata of (mark, year) are the right "same population" for E-023's twin.

**The operator's (only when they arise):**

- NQ from 2026-07-17 as a fourth confirmation window (D-107, D-461) and its purchase, only once a pick is carried;
- the levels of E-015's limits (flags only);
- D-281 (3), only if the lead or the red team holds the reading above inside the closed branch.

## 21. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and
recorded in its own decision row -- never added to this file once pinned.)*
