# DRAFT F-R: resolution forecasts on P-16's schedule (family R) -- second version, not declared

**Status: DRAFT, second version, 2026-11-16 (TASK_QUEUE Q-78), brought to the standard the program adopted after the
first version was written (E-029 to E-047; section 0.2). Not pinned, not numbered, not declared.** The first version is
40469fd and 1c54079 (Q-38, merged under E-028). Nothing of it is built. No bar, walk, trade or result value was read for
either version, no forecast was fitted and no outcome was computed. The one piece of code is a synthetic test of the
arithmetic the forecast leans on, of the clock that keeps the opening range out, of C2's two-sample form, and of this
file's own reads line and seeds (`tests/test_family_r_band_exit.py`, section 19.2, T-1). This file may be edited until
the lead pins it. From the pinning row on, nothing in it is edited: a change is a new family.

**Its rules come from the operator's ruling of 2026-11-16 (E-023; `CHARTER.md` section 3, "Levers that do not choose a
side").** The forecast keeps the coin's side, so E-008's lift over the coin twin cannot judge it. Its uses split under
the ruling:

- the **admission filter** (Part I) is tested at the trade level against a **placebo-selection twin**, one-sided at the
  family's level by the calibrated statistic E-035 (2) adopted, valued at that bound, and can be carried;
- **choosing the funded opening's R on the same trades** (Part II) is a **described reading**: never carried, and no
  program family number.

**It cannot be pinned before:**

- **the lead's deferral is lifted** (E-028 (2)): F-02 and family B go first, because a family number spends the
  program's budget and tightens every later family's level;
- **Q-55's clean rerun** of Q-16's calibration is on record (E-035 (4)), and the persistence-and-power table (6.6) is
  filled from its Table 9 with the drop rule applied (E-035 (6)). Until then no figure of Q-16 is cited, and the marks
  **[Q-55]** stand;
- the items of section 21 are closed, a red-team read among them.

| field | value |
|---|---|
| family | R: a variance forecast from closed bars, used to admit P-16's refused marks on the days they are forecast to resolve |
| id | F-XX -- the gatekeeper's |
| program family number k | **the next free at the pin.** F-01 spent 10 (E-007 (a)); F-02 is to be pinned at k = 11 (E-045 (4)); family B's and family O's drafts are ahead of this one, and its pin is deferred until F-02 and family B go first (E-028 (2)). The described reading of Part II takes none (E-023 (1)) |
| level | one-sided **0.05 / (k (k + 1))**: 0.05 / 132 at k = 11, 0.05 / 156 at k = 12, 0.05 / 182 at k = 13, 0.05 / 210 at k = 14, 0.05 / 240 at k = 15 |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16 only, read through `extended/reader.py` (E-026 (2)) |
| base | P-16 (`rc_s150_all_nr`, `vendor/stage2/prereg/P-16_rc-s150-all-nr.md`) as registered, its report-day 07:35 entry kept (E-039 (1)); R\* = P-14 beside |
| population | P-16's refused grid offers: the five-minute marks 09:05-15:05 CT of P-16's walked sessions less E-029's voided days, each walked long and short at every quarter R to 3 (section 5.2). Every entry of the family's choosing is strictly after 07:35:00 CT by construction (E-039 (1)) |
| choice block | sessions 2020-01-02 to 2023-12-29. The forecast is fitted there, inside its walk-forward only (E-031 (1)). Stages A and B read its out-of-fold years 2021, 2022 and 2023 |
| judged block | sessions 2024-01-02 to 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`config/windows.yaml`, `reserve`); not on disk, a purchase (section 16) |
| cells (`k_cells`) | Part I: **3** (`adm@1`, `adm@1.5`, `adm@3`: 3 R x 1 forecast x 1 line q = 3), each counted whether dropped before the pin (6.6), killed or read. Part II: 1 described reading, unnumbered |
| judged | one cell: stage B's pick |
| pass line | E-023 (2), every line by **`cons`** with the treated-cluster df (`extended.lift_bound`, E-035 (2)), each member's critical value the largest of its nominal t and stage B2's (section 11): **C1**, the admitted offers' stratum-centred side-symmetric value over the twin's exact expectation (`placebo_selection_bound`); **C1-close**, the same under the `close` flatten convention; **C2**, the design's routed admitted trades against two twin designs' routed placebo-admitted trades in dollars (`two_sample_bound`), at least $500 a year at its bound; section 3's floors; the scorecard beside |
| fitted values | **35**, inside the choice-block walk-forward only (E-031 (1)): 23 HAR coefficients and 12 calibration values (6.3, 6.4); hashed and pinned before any judged read |
| seeds | 20261970 to 20261979, checked unique (section 17) |
| model card | the forecast's coefficients and calibration (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`), if a design is carried |

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
number of the same late offers, at the same times of day, in the same years. The family passes only if:

- its picks earn more than random picks by more than chance, at the family's strict level;
- they still do when the model's cautious price for a trade cut off at the close is replaced by the close itself (much
  of the expected edge is that cautious price, section 1 (iv));
- the trades the design actually takes are worth at least $500 a year more than those a random admission rule would
  have the same accounts take;
- every floor holds: trades resolve, the long-run gate, verified rules, conduct.

**Can the data judge it at all?** The forecast leans on the past month's volatility, and busy and calm spells last
weeks to months. A filter that stays on for months gives few independent tries on two and a half years of data. The
program's own calibration found that such a filter often cannot be judged on this block at any effect size (E-035
(6)). So the file states, before anything is read, how long each cell's choices are expected to persist, and a cell the
data cannot judge is dropped and counted before the pin (section 6.6). **The drafter expects this may drop all three
cells**; the family would then close before its pin, and its supply question would go to a described reading, as the
lead already planned (E-028 (2)).

**Expected.** A small, real edge from avoiding the close, likely below the $500 bar and possibly not even judgeable. A
"no" is a valid close. The extra trades' effect on a user's journey is shown beside, but the ruling does not credit it:
the random twin adds the same number of trades.

**A second use, described only.** Giving a funded account's first trade its 3R target only where the forecast says it
will finish, and a smaller target where it will not. That adds no trade and picks no trade, so under the ruling it is a
**described reading**: shown on the menu with whom it helps and hurts, never carried, with no family number (Part II).

## 0.1 Where the brief's items are answered (Q-38's brief), and which use falls under which rule

**The first brief's items.**

| the brief's item | where |
|---|---|
| the mechanism and its sources | 1 |
| the forecast: HAR-type, closed bars only, fitted in the walk-forward on the choice block; every parameter classed | 6, 8 |
| how the forecast is used, each use a cell, counted | 0.1 (below), 7, 14, 18 |
| supply and resolution gates before any outcome | 9 |
| the pass line | 12 (E-023 (2)); 14 (E-023 (1)) |
| the journey scorecard beside | 13 |
| prior exposure | 2 |
| the confirmation | 16 |
| seeds 20261970-20261979, checked unique | 17 |
| k the next free | header; 18 |
| the walker (E-011) and the reader (E-026) | 4, 5, 19 |

**The three uses of the forecast the brief names, under E-023.**

| use | what it changes | E-023 class | in this file |
|---|---|---|---|
| **(u1) admitting marks the unconditional cutoff refuses** | adds offers: P-16's refused marks, on the days the forecast says they resolve | (2) **a filter that keeps the coin's side and chooses which offers to take**: tested against a placebo-selection twin, can be carried | **Part I, the family's 3 cells** (`adm@1`, `adm@1.5`, `adm@3`) |
| **(u2) choosing the funded opening's R where it resolves** | the target of trades P-16 already offers and takes; no trade added, no offer chosen | (1) **a lever that adds no trades**: described, never carried, no family number | **Part II, the described reading `R-cap`** |
| **(u3) freeing the firm's one position slot sooner** (the opening routed to an offer forecast fast) | which offer a newly funded account's opening takes, i.e. when | (2) a timing filter on the funded opening | **family O's cell `u3`** (`prereg/DRAFT_F-O_opening_timing.md` section 6.5; E-039, E-046), with the LeBaron sign stated in advance |

**Why (u3) is family O's.** It has family O's population (the funded openings), its twin (a placebo of the same firing
share on the openings) and its seam (a router that lets an opening wait). Declaring it here would put two families'
cells on one population, under two levels. Family O restates this file's forecast for the overnight bands, without the
calibration (it uses the forecast's rank only); if both are pinned, the two are one module (T-7). Part II's `R-cap`
reports how much sooner a capped opening frees the slot, as a mechanics reading.

## 0.2 What the second version changes, by source row (Q-78)

| source row | what changed | where |
|---|---|---|
| **E-031 (1)** fitted values | the forecast's coefficients and calibration are fitted only inside the choice-block walk-forward, each procedure fixed here, the final fit hashed and pinned before any judged read; nothing fitted, chosen or tuned on the judged block. The row the first version asked for under Stage 2 D-621 (4)(d) is this one. The count is now 35 (the sixth band, below) | header, 6.3, 6.4, 8, 18 |
| **E-031 (2), E-039 (2)** the reverse walk-forward | **struck** from stage C's readings beside; its seed stream `[20261972, 1]` stays **reserved and unused**, and every result file says so; the year-by-year readings on each block go beside instead | 12, 17 |
| **E-035 (1)-(2)** the statistic | C1 and C1-close by `cons` through `placebo_selection_bound` on the **stratum-centred** value, treated-cluster df; C2 by `cons` in its two-sample form, `two_sample_bound`, against twin designs; the first version's raw session series z_s dropped as a variance series; each member's critical value the largest of its nominal t and B2's; the pass-line code pinned by its git blob ids | 7.3, 7.4, 11, 12, 21 |
| **E-035, calibration note 7.3** the twin's form | answered: C1 uses the twin's exact expectation (the stratum means, no placebo noise); the seeded draw is read beside by `two_sample_bound`; C2's twin designs are seeded draws | 7.2 |
| **E-035 (3)** the P comparison | `extended/p_bound`'s `pcons`, one-sided at 0.05, reported, never a line; `bm63c` beside once its table is pinned | 13 |
| **E-035 (4)** the calibration's figures | none cited; the marks **[Q-55]** | 6.6, 9 (A8), 21 |
| **E-035 (6)** persistence before the pin | each cell's persistence class stated with its reason; its power read from Q-55's Table 9 before the pin; a cell that cannot reach power is dropped and counted then. **The admissions follow the trailing month's volatility level, so the drafter expects the slow classes and states it** | 6.6, 9 (A6, A8), 15, 21 |
| **E-008, E-014, E-015, E-023** trades first | the pass line at the trade level against the placebo twin; the journey scorecard beside, never a line, with the twin design beside P-16 so supply is shown and not credited; Part II described, never carried | 0, 7, 12, 13, 14, 15 |
| **E-030, E-036 (M3-2)** the opening range | **excluded in substance**: the population's marks 09:05-10:05 form a band `day1` whose so-far term is frozen at the 08:30 mark's alert (bars stamped at or before 08:24); the live so-far term starts at 10:10, the first mark whose 60-minute window opens at 09:00 or later; so no used input of any population offer reads a bar of the alert's day stamped 08:30-08:59. Earlier sessions' 08:30-08:59 bars enter only Part II's daily volatility terms, outside the closed branch by E-036 M3-2's definition. The first version's open question (x3 at 09:05-10:05) is closed this way, with no ruling needed | 3, 6.2, 6.3, 9 (A2), 19.2 (T-1, T-2) |
| **E-037, E-041** the reader | the whole-window identities read only from this repository's identity scripts under the purpose `identity` and their own row; `registered_design` is never available to a family | 4, 9 (A1) |
| **E-039 (1)** report days | every admitted entry is at 09:05 or later, so strictly after 07:35:00; P-16's own trades keep their registered 07:35 entry; **Part II's cap acts only on entries strictly after 07:35:00**, so a report day's 07:35 trade keeps P-16's bracket, counted beside | 3, 5.1, 9 (A6), 14 |
| **E-034** news | Topstep's unstated news rules (which events count; whether holding through one counts; the GDP minute) in section 3 and in every scorecard's "not modelled" note | 3, 13, 14 |
| **E-040, E-044 (2), E-047 (1)-(2)** B2 | B2 rebuilt in family B's and family O's form: conditional on the pick's real judged admissions; the choice span's values in stationary 63-session blocks, re-centred within the judged strata; a slow component switching 1/63 a session at an amplitude by E-047's rule -- (a) absolute, `a*_pre` = 3 (a), (d) the judged yearly lift **of the pick itself and of its seeded twin** read after the judgement, each member's critical value the largest of nominal, B2 at `a*_pre` and B2 at `a*_post`; **no amplitude borrowed from Stage 2's S1/S3 files** (whole-window per-offer sided lifts only, E-043, E-046 (3)); C2's routing selection (E-044 (2)'s concern) removed by the twin designs | 7.4, 11 |
| **CHARTER section 2, E-030** C2's bound | C2 at the family's level (the first version read it at a one-sided 95 % bound) | 12 |
| **family O's first review (m3) and this file's 1 (iv)** | **C1-close is a line**, an intersection at the same level: a lift that is only Stage 2's conservative flatten price fails. The drafter's choice; it can only make a pass harder | 7.3, 10, 11, 12 |
| **E-029** the calendar | no offer is admitted on the days E-029 voids (2020-07-01; the purchase seam 2025-06-30 and 2025-07-01), counted; their IVs are missing in the forecast's terms; the pinned calendar's sha256 in every manifest | 4, 5.2, 6.2, 20 |
| **E-026 (2), E-041** the reads line | a `Judged-block reads:` line, parsed by `extended.reader.declared_purposes`, no choosing or fitting word | 20.1, T-1 |
| **E-044 (5), Q-70** the place-recording adapter | C2's uses read through it, on the design and on the twin designs | 7.4, 19.1 |
| **E-038, E-045, E-046** the seed blocks | the block rechecked word-bounded across the tree and every commit; the firms reading's, family B's and family O's blocks are taken | 17 |
| consistency | K1 counts sessions holding an admitted offer (its stated reason was "a month of sessions"); stage B's bootstrap stationary with mean block 63 (the selection's class); A9 added (the level on the side-symmetric value, family O's A10) | 8, 9, 10 |

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
- **So the trade-level lift is expected positive and small, and part of it is a property of Stage 2's conservative
  flatten convention, not of the market.** In the first version the `close` convention was only read beside; **here it
  is a line (C1-close, section 12)**, so a lift that is only the convention's price cannot pass.

**(v) Why it could matter for a user, though the pass line does not credit it.**

- P-16's funded accounts take fewer than one trade per live account-day (`vendor/stage2/results/u_xfa_day_budget.csv`,
  section `signal_supply`, as the handoff 2.5 quotes it). One position at a time across the firm (D-429) and the 09:00
  cutoff leave some accounts without a trade on some sessions.
- Admitted later offers give them one. That is supply. E-023's twin adds the same supply, so it cancels in the pass
  line by design ("so supply and schedule cancel and only the selection is measured").
- The journey effect is shown beside: the twin design against P-16 is supply's effect, the design against its twin
  design is the selection's (section 13).

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
| **D-525 (4)** | the cutoff per mark, per stop: unresolved share at most 5 % at every offered R, kind columns only | **the whole development window, both blocks** | P-16's admitted marks; none after 09:00 CT at 150 ticks (D-618 (3)) | **the base and this family's population (5.2) were fixed on both blocks**: disclosed (4 item 4) |
| D-538, D-542 (the stop-width screen) | per-mark resolution at 150 and 200 ticks; the 37.5-point US window fails resolution | 2020-2026 | `rc_width_screen.csv` section `marks` | the refused marks' average resolution has been seen, mark by mark, on both blocks |
| D-578 (4), D-581, D-582 (S2) | P-16's coin gated by the last 30 bars' range in thirds against the same mark's 20 prior sessions; a trend state | 2020-2026, both spans; campaign growth | no candidate; high volatility closest to P-16; low and mid volatility failed resolution at the longest R in their worst year | **a volatility state was read on P-16's own offers**, as a gate on P-16's marks, not as admission of refused ones; its campaign readings are seen |
| D-639, D-641, D-642 (program U family 4) | window cells; an R cap from the resolution columns where a window fails D-212; the 25-point US cell with its cap (D-641 (3)) | 2020-2026, both blocks | closed at line (3)(i); the US-hours scorecards beside | the R cap's form (Part II's lever is its per-offer, forecast-conditioned version) |
| handoff 3.2 | "Time of day changes resolution speed and cost, not the win rate at zero edge"; every change to the funded leg was worse for a user | -- | -- | (i); Part II's prior |
| **E-035 (this repository's Q-16)** | the coin side's own outcomes of P-16's judged offers under random selections in six persistence classes, and sign-flipped pairs | 2024-2026 (P-16's judged offers) | `cons`, its level and its power by persistence class (Table 9; exploratory until Q-55) | program-wide: the statistic and the drop rule (6.6); it read no forecast and no selection of this family |
| E-043, E-046 (3) (vendored S1/S3 files) | Stage 2's sided follow lifts per offer, whole window only | 2020-2026 | -- | **not read by this family**: B2 borrows no amplitude from them (11) |
| this repository | `docs/research/mechanisms_2026-11-15.md` section 5.2 (the scout); family B's draft's resolution model as a positive control (nothing read); family O's draft (its `u3` restates this forecast; nothing read); E-021, E-023, E-031, E-035 | none | -- | the scout's design, adapted to E-023 and E-035 |

**The drafter's own reads (disclosed).** All are code, configuration, drafts and decision rows. **No result value was
opened** beyond what the rows above state.

- First version: `vendor/stage2/propedge/research/resolved_coin.py` (the coin table, `mark_resolution`, the windows,
  the release cut); `vendor/stage2/scripts/rc_width_screen.py` (`build`), `config/effect_atlas.yaml`,
  `config/resolution_map.yaml`; `extended/features.py`, `extended/walker.py`; the section and measure names of
  `u_value_map.csv`.
- This version: decision rows E-028 to E-047; family O's, family B's and F-02's drafts; `extended/lift_bound.py`,
  `extended/p_bound.py`, `extended/reader.py`, `extended/features.py` (code); the calibration note
  (`docs/research/calibration_2026-11-15.md`) sections 7.1-7.3 and Table 9's caption and layout -- a text search of
  the note displayed some of its table rows; **no figure of it is used or quoted here** (E-035 (4)).

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
| one trade an account a session | P-16's (its registration section 3), unchanged |
| resolution (D-212, D-308) | per offer by construction (6.5); K2 on the choice block (9); a floor on the judged block (12) |
| realised risk (D-212 (1), D-308) | the stop is P-16's 150 ticks, and a capped target leaves the dollar risk unchanged. Read in P-14's registered allowance-capped form (E-022 (1)) |
| stop band and cost floor (`stop_band.csv`; D-271 (3)) | 150 ticks, above the 45-tick floor |
| report days (D-525, D-533; E-007 (d); **E-039 (1)**) | **The lead's ruling (E-039 (1)):** P-16's registered trades keep their registered report-day entries whenever they are re-read, and new families enter strictly after 07:35:00 CT. Here **every admitted offer enters at 09:05 or later**, so the family's own entries obey it by construction; P-16's own trades keep its 07:35 mark (on the stated end of Topstep's Tier 1 window, 07:25-07:35 CT; the audit's U7 (a), `docs/audits/phase0/E_rules_currency.md`), counted in stage A (A6) and beside the verdict. **Part II's cap acts only on entries strictly after 07:35:00** (14.1). FOMC days are excluded |
| ISM (09:00 CT), GDP (07:30 CT) and "maximum size into major news" (**E-034**) | E-034 decided it (Q-39 read): which events count, and whether holding an open position through one counts, are **unstated** on Topstep's pages; the named restricted list is 13613539's Tier 1 table (CPI, NFP and the unemployment rate, PPI at 07:30 CT with a 07:25-07:35 window; the FOMC decision and press conference); the GDP release minute is unstated. The population's first mark, 09:05, is five minutes after a 09:00 CT release minute (as 07:35 is to 07:30, E-007 (d)); no admitted offer falls in a named Tier 1 window. No forecast reads a release calendar. These unstated rules are listed in every scorecard's "not modelled" note (13) |
| the 08:30-09:00 window (Stage 2 D-281 (3); **E-030; E-036 M3-2**) | **no entry of this family's choosing falls there** (the population starts at 09:05), and **no used input of any population offer reads a bar of the alert's day stamped 08:30-08:59**: at the marks 09:05-10:05 the so-far term is frozen at the 08:30 mark's alert (bars stamped at or before 08:24), and from 10:10 its 60-minute window opens at 09:00 or later (6.2, 6.3; T-1 shows the clock, T-2 proves it on the code). The daily terms read only windows starting at the mark (09:05 or later). P-16's own window offers are unchanged in Part I; Part II changes their bracket only, from bars closed by the 08:24 bar of their day (14.1) |
| no time stops (D-212 (2)) | none. Part II's lever chooses a target at entry, not an exit time |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (37.5-point brackets held minutes to hours); no maximum size into major news as E-034 reads it (above); no copying across accounts (D-157); nothing concealed: the rule is a published forecast on closed bars |
| conduct tier 2 (D-289) | as P-16: the Responsible Trading Program's placement off in the base case, on beside |
| conduct tier 3 (E-013 (1)) | 0 % denial in the verdict; 10, 25 and 50 % beside (Q-17's adapter) |
| firm rules | none loaded by the family. The engine runs Stage 2's verified ledger as P-16 does |
| the breakeven move (E-013 (2)) | allowed as made; P-16's walk. Q-20's corrected moves are beside (`extended/walker.py` presets, merged b7232ba) |

**One conduct note.** A rule that seeks the fastest windows picks release windows. Here the admitted windows start
after every release the engine knows of. Whether a full-size position held through a later unnamed release is "maximum
size into major news" is E-034's unstated question, and this family inherits P-16's answer.

## 4. Data, blocks, the seal, the calendars and the disclosed pre-reads

1. **Data:** Stage 2's NQ 1-minute bars (licensed, uncommitted, `vendor/DATA_MANIFEST_stage2.sha256`), 2020-01-02 to
   2026-07-16 only. The labels come from this repository's walker (E-011), not Stage 2's `data/atlas`.
2. **The blocks:** choice 2020-01-02 to 2023-12-29; judged 2024-01-02 to 2026-07-16. The forecast's out-of-fold years
   are 2021, 2022 and 2023 (6.3); stages A and B read them. 2020 serves the warm-up and the first training fold; **no
   lift is read on 2020**.
3. **The seal (E-026 (2)).** Every bar and walk this family reads goes through `extended/reader.py`.
   - The judged block is read only under the purposes on section 20.1's line, from a clean run of a committed tree,
     once each; each read appends to `results/read_ledger.jsonl` first. The reader refuses any choosing or fitting
     purpose on the judged block whatever this file says.
   - Choice-block reads need no tag; this file names them anyway: `fit_forecast` (the walk-forward and the final fit),
     `stage_A_resolution`, `stage_B_choice`.
   - **The identities** (A1) read Stage 2's whole window. They run only from this repository's identity scripts
     (`identity/*.py`) under the purpose `identity` and their own decision row (the reader's rule 2; E-037), ledgered
     inside the clean run -- never under this file's purposes. `registered_design` is never available to a family
     (E-037, E-041).
   - T-3 (section 19.2) is the second proof: choice-stage outputs unchanged when the judged block is replaced.
4. **Disclosed pre-reads**: inputs fixed or read over 2020-2026 that T-3 cannot see, each with what it can bias.

   | input | what it is | can bias | cannot bias |
   |---|---|---|---|
   | P-16's admitted marks (D-525 (4), whole window) | the base's schedule; the population's marks (from 09:05 CT) | that the population is "marks that on average do not resolve at 3R" -- common to both arms of every comparison | the forecast's selection within a stratum (7.2) |
   | P-16's per-R bounds (the bound arm's shift), estimated over both blocks (the F-P review's N2) | a constant per R | the level of every campaign and journey number, every design alike | the trade-level lift (computed on net R before any shift) |
   | `u_value_map.csv` (D-667) | `mean_dv` by place, the bar | stage B's ranking and C2's dollars | the lift or its bound |
   | `stop_band.csv` | the cost floor | nothing here (P-16's stop) | -- |
   | S2's readings (D-582) | a volatility gate on P-16's marks | the design of K-info and of the placebo | the pick |
   | Q-16's calibration (E-035) on P-16's judged offers | coin-side outcomes under random selections | the statistic and the drop rule (program-wide) | this family's selection |
   | `config/calendar_early_closes.csv` (E-029, pinned) | the scheduled early closes and the data-defect candidates | which days carry no admitted offer | the selection on the other days |

5. **The calendars, fixed before any read.** P-16's walked day kinds (`n` and `b`: FOMC days, early closes and empty
   days out). **E-029's voids:** no offer is admitted on 2020-07-01 or on the purchase seam 2025-06-30 and 2025-07-01
   (counted); 2020-03-16, 2020-03-18 and 2025-04-03 are kept (E-029: a market event or one late first trade). A voided
   day's IVs are missing in every later day's terms (6.2).
6. **Which calendar each reading uses.**

   | reading | calendar |
   |---|---|
   | A1's identities against P-16's registered gate paths | the gate, as registered (seed 20261206) |
   | A1's identities against P-16's U1 start rows | the U1 replay |
   | the forecast, C1, C1-close, K1, K2, K-info, A9, B2 for C1 | none: offer-level, on the population's walks and the session calendar |
   | C2's uses, B2 for C2, floor (i)'s taken trades, floor (iii) | the gate: the design's and its two twin designs' campaigns at one seed (20261973), the gate's own day table. The admission is a property of an offer's own day and its value is that offer's own walk, so drawing days independently loses nothing C2 measures; the twin designs face the same draws |
   | the scorecard (13) and Part II (14) | the U1 replay in history's order, as U1 is defined |

7. **No NQ from 2026-07-17** is on disk or read (section 16).

## 5. The base, the population and the walk

### 5.1 The base

P-16 exactly, as registered and as this repository's identities reproduce it (E-004 gate paths; E-010 U1 start rows;
E-044 (3) through the re-composed gate):

- the coin `rc_s150_all_nr`: one fair coin per (date, mark) over the whole grid, seeded 20261102
  (`resolved_coin.coin_table`);
- the stop 150 ticks, every quarter R to 3R walked, Stage 2's costs (`fee_by_stop`);
- a report day's marks before 07:30 CT dropped, then every report-day entry before 07:35 CT (D-533 (2)) -- **kept for
  P-16's registered trades** (E-039 (1));
- the day kinds `n` and `b` (FOMC days, early closes and empty days out);
- P-14's money side: the no-closure v12 table, 20 purchases in 21 sessions, the strict router, five seats;
- the registered trades' content hash `rc150_dev_test.TRADES_SHA256`.

### 5.2 The population: P-16's refused grid offers

- **Marks:** every five-minute grid mark from **09:05 to 15:05 CT** (73 marks) -- every mark after P-16's last offered
  mark, 09:00 CT (D-618 (3)), fixed as a time range and not re-read from any table.
- **Sessions:** P-16's walked day kinds, after the forecast's warm-up (6.2), less E-029's voided days (4 item 5).
- **The offer:** at mark m on day d, the market entry at the first bar opening at or after m, as P-16's.
  - Its side is the registered coin's at (d, m). The coin table already covers the whole grid, so no new coin is drawn.
  - It is walked long and short.
- **No mark inside 08:30-09:00 CT is in the population** (those are P-16's own, unchanged in Part I). No entry is added
  in the window Stage 2 D-281 (3) reserves to the operator.
- **Report days:** every population entry is at 09:05 or later, strictly after 07:35:00 (E-039 (1)).
- **An offer with no forecast** (6.2's missing rule) stays in the population and is never admitted; the count is
  reported.

### 5.3 The walk and the labels

- **The walker:** `extended/walker.py`, preset **`STAGE2`** (E-011): P-16's own walk, so the base reproduces P-16 bit
  for bit:
  - FV3's rung walk at every quarter R to 3R;
  - stop on a touch, target on a trade through, stop first on a two-barrier bar;
  - the breakeven move;
  - the walk's end the bar ending 15:08 CT, the flatten at the worst of the bars ending 15:08-15:10 less two ticks;
  - Stage 2's costs.
- **And under the `close` flatten convention** (`DECLARED_F01`'s flatten, every other rule `STAGE2`'s), for C1-close.
- **Kinds:** stop, target, flatten (unresolved), breakeven. "Unresolved" means the flatten kind only.
- **The per-offer coin value at bracket R:** c_i(R) = (net R of the long + net R of the short) / 2. That is the coin's
  expected net outcome at offer i, without its noise (F-01's convention for a twin's expectation). Both sides of every
  offer are walked. Its halves l_i(R) and r_i(R) (the long's and the short's net R) are read beside.

## 6. The forecast

### 6.1 What it forecasts

**IV(d, m)**: the integrated variance a trade entered at mark m on day d sees before the walk's end. It is the sum of
squared one-minute price changes, in points^2, over the bars from the entry bar (stamped m) to the bar ending 15:08 CT:

- the first change is that bar's close less its open (the entry price);
- then each present bar's close less the previous present bar's close.

The definition is within one day's bars, so it never differences prices across a roll. The price change is in points,
not a log return, because the bracket is fixed in points. Points^2 enter the regressors only as ratios across days.

### 6.2 The regressors: HAR in normalised form (feature-rules 2)

**M(d, m)** is the mean of IV(d', m) over the **22 prior walked sessions** d' with a value at mark m. It is the HAR's
monthly term, computed from the past only, and it is the normaliser.

| regressor | formula | what it is | reads |
|---|---|---|---|
| y (the target) | log(IV(d, m) / M(d, m)) | the day's variance at this window against its trailing month | day d's bars stamped m .. 15:07 (the label: never a feature) |
| x1 | log(IV(d - 1, m) / M(d, m)) | yesterday's same window (HAR's daily term) | the prior session's bars stamped m .. 15:07 |
| x2 | log(mean of IV over the 5 prior sessions / M(d, m)) | last week's (HAR's weekly term) | the 5 prior sessions' same window |
| x3 | **2 x `rv_tod`** at the alert t = m - 5: log((rv_60 / its median over the 20 prior walked sessions at the same slot)^2), where rv_60 is the root mean square of one-minute close changes over the day's bars stamped t - 61 .. t - 1, **the window bounded at the day's first bar** | today's surprise so far: the last hour's variance against its usual level at that time | day d's bars stamped m - 66 .. m - 6 (no earlier than the day's 17:00 bar); the same slots of the 20 prior walked sessions. **Frozen in the bands `open` and `day1` (6.3)** |

Rules for every regressor:

- **Past only.** Every term reads earlier sessions or day d's bars stamped at or before m - 6.
- **The normalisers are trailing:** M over 22 sessions; the slot median over 20 sessions, at least 10 with a value,
  else missing (the library's rule).
- **The frame.** Every trailing window and median runs over **P-16's walked sessions**: the forecast's module is handed
  the bars of P-16's walked sessions only, so the library's trailing median (its 20 prior days of the frame) is over 20
  prior walked sessions (family O's 6.1 states the same). No negative-index slicing is used at overnight slots (it
  would wrap to the end of the same day, the future).
- **x3 is the library's tested feature.** At the RTH alerts where it is live (the `day` band, alerts 10:05-15:00) x3 is
  exactly 2 x `extended.features` `rv_tod`, and T-2 asserts the equality. The family's module extends the same formula
  to alerts outside 08:30-15:00, which the library refuses.
- **Missing values.** An offer with M, x1 or x2 missing, or with IV of a needed prior window zero, has no forecast and
  is not admitted. The count is reported. A day E-029 voids has no IV (4 item 5).
- **Calendars, rolls, DST.** No release calendar input. Rolls cannot enter (every term is within a day). Slots are
  Chicago wall clock, so a DST change moves nothing.
- **The opening range (E-030; E-036 M3-2).** No regressor of a population offer reads a bar of its own day stamped
  08:30-08:59: x1, x2 and M read windows starting at the mark (09:05 or later); x3 is frozen at the 08:30 mark's alert
  for the marks 09:05-10:05 and live from 10:10, the first mark whose window (bars stamped 09:04 .. 10:04) opens after
  08:59 -- at 10:05 the window would still hold the 08:59 bar. Earlier sessions' 08:30-08:59 bars enter only Part II's
  `open` band, through IV and M of earlier sessions: daily volatility terms, which E-036 M3-2's definition of the closed
  branch ("trading rules defined on or triggered by the opening range") leaves outside, as family O's 6.1 answered for
  its H and IV.

### 6.3 Bands, the fit and the walk-forward

**Six bands of marks, each with its own coefficients.**

| band | marks (CT) | terms | serves |
|---|---|---|---|
| `evening` | 17:00-17:55 | x1 and x2 only: the trading day has under an hour of bars, so x3 is not defined | Part II |
| `asia` | 18:00-01:55 | x1, x2, x3 (its window bounded at 17:00) | Part II |
| `london` | 02:00-08:25 | x1, x2, x3 | Part II |
| `open` | 08:30-09:00 | x1, x2, and x3 **frozen at the 08:30 mark's alert** (bars stamped at or before 08:24) | Part II |
| `day1` | 09:05-10:05 | x1, x2, and x3 **frozen at the 08:30 mark's alert** (the same value as `open`'s) | Part I |
| `day` | 10:10-15:05 | x1, x2, x3 (live) | Part I |

- The boundaries are Stage 2's customer windows (`resolved_coin.WINDOWS`), with the evening hour and the opening window
  split out, and the population's first hour split at the mark where the live x3 clears the opening range.
- **The `open` and `day1` freezes** keep every bar of the alert's day stamped 08:30-08:59 out of every input (E-030's
  standard; Stage 2 D-281 (3)'s closed branch). A frozen x3 still carries the pre-open hour's surprise.
- **The family's cells use the bands `day1` and `day` only.** The other four serve Part II.

**The fit.**

- Ordinary least squares of y on an intercept and the band's terms, one observation per (session, mark), each weighted
  one.
- `evening`: 3 coefficients. The other five bands: 4 each. In all, **23 fitted coefficients**.
- Deterministic; refused if a band's design matrix is rank-deficient (the failure protocol).

**The walk-forward, inside the choice block only (E-031 (1)).**

- Test years 2021, 2022 and 2023. Each is fitted on the choice block's sessions before it, less the last 22 sessions
  (expanding; the first fold trains on 2020 after its warm-up).
- A forward walk needs no purge: no training label resolves in a test session (each IV ends at 15:08 the same day).
- The 22-session gap (the HAR's longest window) is kept because it is harmless.
- These out-of-fold predictions feed stages A and B. **There is no reverse walk-forward** (E-031 (2)).

**The final forecast.**

- Fitted on every choice-block session with a value (2020 after its warm-up, to 2023-12-29).
- Its coefficients and the calibration (6.4) are serialised to canonical JSON and hashed.
- **The hash is pinned in a decision row before the judged block is read** (section 20.2's row between the runs). The
  judge's entry point cannot fit (T-9). Nothing is fitted, chosen or tuned on the judged block.

### 6.4 From a variance forecast to the chance of being open at the end

1. **The forecast variance:** V_hat(d, m) = M(d, m) x exp(y_hat), the forecast's median, in points^2.
2. **In stop units:** u = V_hat / S^2, with S = 37.5 points. The bracket at R has a = 1 and b = target_ticks(R, 150) /
   150 (Stage 2's rounding).
3. **The textbook probability:** Psi_b(u) by section 1 (i)'s series, or by the method of images for u < 0.05 (they
   agree to 1e-9: `tests/test_family_r_band_exit.py`). It is clipped to [1e-6, 1 - 1e-6].
4. **Calibrated per band:**

       p_hat(i, R) = sigmoid(alpha_band + beta_band x logit(Psi_b(u)))

   - alpha and beta are fitted by maximum likelihood on the training fold's walks: every (offer, side, R the table
     offers), the flatten kind as 1 -- for `day1` and `day` the population's walks, for the other bands P-16's own
     offers' walks.
   - Both sides are pooled, because the coin chooses the side.
   - In-fold, from the training fold's own fitted forecasts; applied out of fold (E-031 (1)).
   - **12 fitted values** (two per band). Under exact Brownian motion with a perfect forecast, alpha = 0 and beta = 1.
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
  admitted; where none is, the table's smallest R.
- **In a design, an admitted refused offer is offered at its cap.** A table leaf asking a larger R takes the cap with
  its dollar risk unchanged: Stage 2 D-639 (2)'s rule, per offer.
  - It is implemented as a plain-data rewrite of the offer's outcome columns above its cap (19.1). No engine file is
    touched.
  - An offer is added only if the cell's filter admits it (7.1), so its cap is at least the cell's R. D-639 (2)'s
    cell-level "collect leaf" test is not applied per offer: the filter already sets the floor on the cap.

### 6.6 Each cell's persistence and power, stated before the pin (E-035 (6))

Q-16's calibration found that a placebo-selection test's power depends far more on how persistent the filter is than
on its firing share, and that a filter persistent for a quarter cannot be tested on the judged block (calibration note
7.3). Its Table 9 gives the detectable difference by persistence class (`offer`, `window`, `session`, `block5`,
`block21`, `block63`) and firing share, at k = 11 and k = 15. Its figures are exploratory until Q-55's clean rerun
(E-035 (4)), so none is quoted; the power column is filled from Q-55's Table 9 before the pin **[Q-55]**.

**What makes this family's admissions persist.** A cell admits offer i when p_hat(i, R) <= 0.05, and p_hat is a
function of u = V_hat / S^2 with V_hat = M x exp(y_hat):

- **y_hat** (x1, x2, x3) is a ratio to the trailing month. It moves within a day (x3) and reverts within days to weeks
  (x1, x2): the `session` to `block5` classes.
- **M is the month's level itself.** It moves with the volatility regime, which lasts months (2020's spring, 2022's
  bear market). The twin's strata (mark, calendar year) match the year's count at each mark, so **within a year the
  contrast is between the year's fast and slow spells**: a regime-length selection.
- **Within a session**, a fast day admits a run of consecutive marks; the session clustering of `cons` carries that.

| cell | what can make it persist | expected class | power at its class, shares 0.25 and 0.5, the family's k (Q-55's Table 9) |
|---|---|---|---|
| **`adm@1`** | M's level across weeks to months; y_hat across days; a run of marks within a session. At 1R the threshold is the loosest, so more of a year's sessions are admitted and the runs are longest | **block21 to block63** (the slower decides: **block63**) | **[Q-55]** |
| **`adm@1.5`** | as `adm@1`, at a tighter threshold | **block21 to block63** (the slower decides: **block63**) | **[Q-55]** |
| **`adm@3`** | as `adm@1`; at 3R only the fastest spells are admitted, so fewer sessions in shorter but still regime-bound runs | **block21 to block63** (the slower decides: **block63**) | **[Q-55]** |

- **The rule, before the pin:** a cell whose class row (the slower of two where two are named) does not reach 80 %
  power inside Table 9's grid **at the share 0.5** -- the largest share in its grid, the one most favourable to keeping
  the cell, because a cell's admitted share is not known before any read -- **at the family's k column** (Table 9 gives
  k = 11 and k = 15; for k from 12 to 15 the k = 15 column, the stricter; above 15, no column exists and the lead
  rules before the pin) is **dropped before the pin and counted**
  (E-035 (6): a cell the block cannot judge spends nothing by being run, and is still counted). The others stay.
- **The drafter's expectation, recorded now:** all three cells are in the slowest class, so the rule may drop all
  three. **If it does, the drafter proposes that the draft is not pinned and takes no k**, and that its closure is
  recorded under a row as "not judgeable on this block at its persistence", with Part II and E-028 (2)'s supply
  question going to described readings. The lead decides (21 item 2). A narrower hypothesis that removes M's level from
  the contrast -- the twin matched within (mark, calendar month) -- is named in section 21 item 4 as a possible new
  draft; it is not this family.
- **What Table 9 measures, and what that means here.** Its outcome is the coin side's own net R (and the 1R win); this
  family's is the side-symmetric value c (5.3), with the coin's direction noise removed and a cost-driven slow part. So
  Table 9 is a guide to the detectable difference for c, not its calibration; A8 reads the cell's own MDL in stage A,
  beside.
- **Measured, if the lead prefers measuring to arguing** (the lead's call under a row): each cell's admitted-session
  run lengths on the choice block from **bars only** -- the HAR fit of 6.3 on the choice block with the uncalibrated map
  (alpha = 0, beta = 1), no walk, no outcome -- read before the pin to place each cell in its class. It is a
  choice-block read before the pin.
- **And at run time:** stage A reports each cell's run lengths on 2021-2023 (calibrated, out of fold) and stage C the
  pick's on the judged block, before any outcome, with the class they imply.

## 7. Part I -- the cells, the twin and the estimands (E-023 (2))

### 7.1 The cells

| cell | the filter | read at | its design (for C2, the floors and the scorecard) |
|---|---|---|---|
| `adm@1` | F_1(i) = 1 iff p_hat(i, 1) <= 0.05 | R = 1 | P-16 plus every refused offer with F_1 = 1, each at its cap |
| `adm@1.5` | F_1.5(i) = 1 iff p_hat(i, 1.5) <= 0.05 | R = 1.5 | P-16 plus every refused offer with F_1.5 = 1, each at its cap |
| `adm@3` | F_3(i) = 1 iff p_hat(i, 3) <= 0.05 | R = 3 | P-16 plus every refused offer with F_3 = 1 (cap 3) |

- R = 1, 1.5 and 3 are the table's three asks: the evaluation's 1.5R, the funded opening's 3R, and 1R after it
  (handoff 2.5; `u_value_map.csv` section `records_leaf`).
- **k_cells = 3**, each counted whether dropped before the pin, killed or read.
- P-16's own offers are unchanged in every cell. Only refused offers are added.

### 7.2 The twin (E-023 (2))

- **The placebo-selection twin:** a random filter that fires on the **same number of population offers as the cell's
  filter in each stratum s = (mark, calendar year)**, drawn uniformly without replacement, seeded
  `default_rng([20261978, c, b, d])` (c the cell: 0 `adm@1`, 1 `adm@1.5`, 2 `adm@3`; b the block: 0 judged, 1 the
  choice span, 2 the confirmation; d the draw: 0 and 1).
- So the time of day and the year cancel, as supply and schedule do, and **only the forecast's choice of day within a
  mark and year is measured**.
- **In C1 the twin enters as its exact expectation**, the stratum means: *answered (E-035; calibration note 7.3):* the
  expectation twin "carries no placebo noise", and a family that uses one seeded draw as the twin is doing a two-sample
  comparison of two random subsets and loses power. The seeded draw (d = 0) is read beside.
- **In C2 the twin is a design**: P-16 plus a drawn placebo admission, two draws (d = 0, 1) pooled, so one draw's noise
  does not bind (7.4).
- **The twin design's brackets.** A placebo-admitted offer has no forecast of its own to cap it, and giving it the
  forecast's cap would put the forecast into the twin. So **in each stratum the multiset of the design's admitted
  offers' caps is assigned to the twin's drawn offers in a seeded random order** (the same draw's stream): the twin
  designs carry the design's bracket mix, which cancels with supply and schedule.
- **What it does not match:** the selection's clustering over marks and sessions (the placebo fires independently offer
  by offer). The statistic's dependence on that clustering is section 11's business.

### 7.3 C1's estimand and its call

    L_R = (1 / N_F) x sum over admitted offers i of ( c_i(R) - mu_s(i)(R) )

- mu_s(R) is the mean of c(R) over **all** population offers of stratum s -- the placebo's exact expectation; N_F the
  number of offers the cell admits. L_R is exactly the expected difference between the cell's admitted offers and the
  twin's, without the twin's draw noise (F-01 did the same for its coin twin).
- **The call (E-035 (2)):** `extended.lift_bound.placebo_selection_bound(y, session, selected, n_sessions,
  level=0.05 / (k (k + 1)))` with `y = c(R) - mu_s(R)` for **every population offer** (sample 2), `selected` the
  filter's flag, `session` the offer's ordinal in the block's calendar (every trading session counted), at the module's
  `SHIPPED = "cons"` and `DIFF_DF_RULE = "treated"` (merged 4d3e503; blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2`).
  - **The strata enter by the centring.** The function compares the selected offers' mean with every offer's mean and
    has no strata. On y the second mean is zero by construction and the estimate is exactly L_R; on the raw c it would
    add the strata-composition term -- the admitted offers' mean stratum mean less the population mean -- which the
    clock makes non-zero with no selection effect at all (later marks are admitted less and resolve less). T-1 holds
    both identities.
  - **The variance** is the module's: cluster-robust on 21-, 42- and 63-session blocks from the linearised residual
    block sums of the two samples, the block count and df those of the sample occupying fewer blocks (the treated
    rule). The first version's session series z_s is **dropped as a variance series**: it carries each session's offer
    count, and a variance of it is not L_R's (calibration note 1.3).
  - **The critical value** is section 11's: each member's the largest of its nominal t and B2's.
- **C1-close:** the same with c and mu_s from the `close` flatten convention (5.3).
- **The seeded draw beside** (`[20261978, c, 0, 0]` on the judged block) is a comparison of two random subsets: it is
  read by `two_sample_bound`, never in a line.
- **What L_R measures (section 1 (iv)).** By the textbook, the avoided flatten's cost and the exit ticks' composition --
  expected small and positive if the forecast sorts the offers. C1-close removes the convention's part.

### 7.4 C2's value line: the design's routed admitted trades against the twin designs'

**Why a difference.** Which admitted offer a seat takes is decided by the router: under one position at a time and one
trade an account a session, an afternoon offer is taken only by an account still free, which depends on how fast that
session's earlier trades resolved. Fast days free seats sooner and also resolve the admitted offer sooner, so the
deviation of a *routed* admitted offer is not mean-zero even for a random admission (T-1 shows it on a toy). The twin
designs' routed trades carry the same routing selection; the difference removes it (E-044 (2)'s concern; family O's
F3).

- **The samples.** On the gate campaigns of the design and its two twin designs (500 paths each, seed 20261973, so the
  same calendar days are drawn; 4 item 6), the place-recording adapter (Q-70) records every simulated trade's offer i,
  the R the table took R_j (after the cap) and its place p(j). Every simulated trade taken from an admitted offer is a
  use j, valued in dollars to first order:

      w_j = mean_dv(p(j)) x ( c_i(j)(R_j) - mu_s(i(j))(R_j) ) / (1 + R_j)

  with mu the offer's stratum mean at R_j (7.3) and mean_dv(p) `u_value_map.csv` section `place_values`, base `p16`,
  measure `mean_dv` (a win over a loss); a lift of lambda R per trade is lambda / (1 + R) of win probability to first
  order. Sample 1: the design's uses; sample 2: the twin designs' uses, both draws pooled. A historical offer used on
  several paths is several uses; their dependence is carried by clustering on the offer's historical session.
- **The per-use difference** D = mean of w over sample 1 - mean of w over sample 2, by `cons` in the module's
  two-sample form, `extended.lift_bound.two_sample_bound(w_1, s_1, w_2, s_2, n_sessions, level=...)` (the treated
  df), each member at the largest of its nominal t and B2's critical value (11).
- **The value:** **V_line = u_d x D** dollars a year of a five-seat campaign, u_d the design's uses a path-year. C2
  reads V_line at D's `cons` lower bound.
- **Beside, deciding nothing:** V(design) undifferenced (the mean of w over sample 1 times u_d); V(twin) likewise; the
  uniform-lift valuation (C1's bound / (1 + R) x mean_dv by place x the uses); the uses by place and R.
- **What V is not:** it is **first-order** -- it turns an R difference into win probability and prices it by the
  solver's binary `mean_dv`, while a difference made of exit-kind costs is not a change in win probability. The
  value-map price at the bound is not calibrated (calibration note 7.4 item 10). Said with the verdict.

## 8. Parameters: fixed, fitted, searched, dropped

| parameter | what it is, in a phrase | class | value | source or reason |
|---|---|---|---|---|
| market, bars | what is traded and read | fixed | NQ 1-minute bars; MNQ micros sized by the table | E-002 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md; `config/windows.yaml` |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | feature-rules 4; CHARTER 3 |
| stages A and B's span | where the choice block's gates and lifts are read | fixed | 2021-01-04 .. 2023-12-29 (out of fold) | 4 item 2 |
| base | the schedule the forecast acts on | fixed | P-16 as registered (5.1), its report-day 07:35 entry kept | E-004, E-010, E-039 (1) |
| stop | the loss distance | fixed | 150 ticks (37.5 points) | P-16 |
| population marks | which offers the filter may admit | fixed | grid marks 09:05 .. 15:05 CT | D-618 (3); 5.2 |
| sessions | days traded | fixed | P-16's walked day kinds, less E-029's voids (2020-07-01, 2025-06-30, 2025-07-01) | D-525, D-533; E-029 |
| entry | how a trade starts | fixed | market at the first bar at or after the mark; by hand; the forecast an alert at m - 5 | D-266; E-008 |
| walk | how a trade ends | fixed | `extended.walker.STAGE2`; `close` for C1-close | E-011 |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| cells' R | the bracket the lift is read at | fixed | 1, 1.5, 3 | the table's three asks |
| offered R | the R a cap is chosen among | fixed | the table's (`policy_rrs`) | D-639 (2) |
| forecast target | what is forecast | fixed | IV over the walk window (6.1) | section 1 (i) |
| HAR terms | daily, weekly, monthly | fixed | 1, 5 and 22 prior walked sessions | Corsi 2009 |
| so-far term | today's surprise | fixed | 2 x `rv_tod` at m - 5 (60 minutes, bounded at the day's first bar; 20-session slot median, at least 10) | `extended/features.py`; Hong et al. 2023's spirit |
| bands | where coefficients differ | fixed | six (6.3) | Stage 2's windows; E-030 |
| the `open` and `day1` freezes | no alert-day bar of 08:30-08:59 read | fixed | x3 at the 08:30 mark's alert for marks 08:30-10:05; live from 10:10 | E-030; E-036 M3-2; D-281 (3) |
| HAR coefficients | the forecast's weights | fixed procedure, **fitted in-fold** | 23, by least squares; three folds and the final fit | 6.3; E-031 (1) |
| calibration | textbook to observed | fixed procedure, **fitted in-fold** | 12, by maximum likelihood | 6.4; E-031 (1) |
| Psi | variance to open-at-the-end | fixed | the textbook series and images; clip 1e-6 | Karlin & Taylor; the synthetic test |
| q | the per-offer resolution line | fixed | 0.05 | D-212 (2), D-308 (3) |
| strata | what the twin matches | fixed | (mark, calendar year) | E-023 (2): the same population, the same share |
| the twin's form | C1's comparison | fixed | the exact expectation (the stratum means); one seeded draw beside | E-035; calibration note 7.3 |
| the twin designs | C2's comparison | fixed | two seeded draws pooled, carrying the design's caps per stratum | 7.2, 7.4 |
| folds | the walk-forward | fixed | test years 2021, 2022, 2023; expanding; a 22-session gap | feature-rules 4; E-031 (1) |
| the pass statistic | every line's test | fixed | `cons` (`extended.lift_bound.SHIPPED`), treated df (`DIFF_DF_RULE`); `placebo_selection_bound` on y for C1 and C1-close, `two_sample_bound` on w for C2; the module's blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2` | E-035 (2); E-044 (1)'s form |
| each member's critical value | t21w, t42w, t63w | fixed | the largest of its nominal t, B2's at `a*_pre` and B2's at `a*_post` | 11; E-047 (1) |
| B2 | the conditional null | fixed | section 11: stationary 63-session blocks of the choice span's centred values; a slow component switching 1/63 a session at `a*(R)` by the one rule of section 11 item 2; at least 1,000,000 replicates per line and amplitude | E-030, E-040, E-044 (2), E-047 (1); family O's section 11 |
| stage B | the ranking device and the pick | fixed | section 10 (stationary bootstrap, mean block 63, 2,000 draws; an uncalibrated selection device deciding no level) | E-039; F-02's and family O's form |
| C2's bar | the least worth | fixed | $500 a year at the family's level, on V_line | `u_value_map.csv` section `bar` (`target=500`); F-02, F-B |
| valuation base | where a win is priced | fixed | `p16` | `u_value_map.csv` |
| K1 | the least supply | fixed | 21 sessions holding an admitted offer in each of 2021, 2022, 2023 | a month of sessions |
| K2 | resolution | fixed | at most 5 % unresolved at R and every smaller R among admitted offers, overall and every year; 4 % in the worst year at R to be eligible as the pick | D-212; family B's M2-4 margin |
| K-info | information beyond the clock | fixed | within-stratum AUC lower bound above 0.5 | 9 (A5) |
| the drop rule | a cell the block cannot judge | fixed | 6.6, from Q-55's Table 9, before the pin, at share 0.5 and the family's k column | E-035 (6) |
| MDL factor | when the family is only a screen | fixed | 3 | F-B; family O |
| campaigns | C2's uses and floor (iii) | fixed | the design's and two twin designs' gate campaigns, 500 paths, seed 20261973 | E-022 (2) |
| a VIX or VXN forecast | the scout's second forecast | **dropped** | -- | not on disk; whether Cboe's history is free without sign-up is unverified (the scout's unknown 6); D-136 read it on 2009-2014; a later family |
| price durations as a second forecast | Hong et al. | **dropped** | -- | a second forecast doubles the cells; it is the natural next family if this one reads |
| q searched | other resolution lines | **dropped** | -- | each value a variant; D-212's line is the rule |
| per-mark coefficients | finer fits | **dropped** | -- | hundreds of fitted values; the normalised form removes the clock |
| a free logistic on raw terms | instead of Psi | **dropped** | -- | more freedoms; Psi is textbook, the calibration two numbers a band |
| a live x3 at 09:05-10:05 | the last hour including the opening range | **dropped** | -- | E-030's standard: no alert-day 08:30-08:59 bar in any used input |
| (u3) routing the opening | the slot | **dropped here** | -- | family O's cell `u3` (0.1) |
| the opening-window marks | 08:30-09:00 | **out of the population** | -- | P-16's own; D-281 (3) |
| the 25- and 12.5-point bases | US-hours cells | **dropped** | -- | the window cells' identities are not reproduced here; a later family |
| R above 3 | longer targets | **dropped** | -- | not walked (the grid ends at 3R) |
| the `adm` and `R-cap` crossing | a combined cell | **dropped** | -- | `R-cap` is a described lever (E-023 (1)); read beside a carried pick only (13) |
| the reverse walk-forward | choose late, judge early | **dropped** | -- | E-031 (2): it would make the judged block choose or fit; the year-by-year readings go beside (12) |
| an amplitude from Stage 2's S1/S3 files | a floor for B2's slow component | **dropped** | -- | those files hold whole-window per-offer sided lifts only (E-043, E-046 (3)); this family's value is side-symmetric and its slow part the exit-kind mix; (d) takes the judged block's own scale instead (11) |
| strata (mark, calendar month) | a twin within the month | **not this family** | -- | a different hypothesis (the day's forecast within its month); a possible new draft (21 item 4) |

**Searched: nothing.** The trial count is the three cells.

## 9. Stage A: the gates, before any outcome (2021-01-04 to 2023-12-29)

Stage A reads **bars** (the forecast), the walks' **kind columns** (resolution, side-free, as D-525 (4) does) and, for
A8 and A9 only, **the population's centred values' dispersion under random selections** -- never a cell's admitted
mean. It reads no lift of any cell. The identities compare hashes and registered rows. Every kill is counted and
recorded.

**A1. Identities (refusing).** Any failure stops the family; the failure protocol applies. Each that reads the whole
window runs from an identity script under `identity` and its own row (4 item 3).

1. E-011's walker identity holds at the build's commit.
2. The family's builder with the filter off -- no offer admitted -- gives P-16's trades, `TRADES_SHA256` exactly; with
   every cap at 3, Part II's design is P-16's trades.
3. Through the family's gate call (`extended.gate.run_gate`, Q-47; its 500-path identities held, E-044 (3)): P-16's gate
   paths, 500 paths at seed 20261206, every `PATH_COLS` column to 1e-6 (E-004's comparison).
4. Through the scorecard adapter: P-16's U1 start rows `p16`, both arms, every start (E-010's comparison).
5. Q-17's readings-beside adapter holds its own identity as merged (b7232ba, `identity/user_beside_identity.py`).
6. The place-recording adapter's identity (Q-70; 19.1 item 4).
7. **The twin design equal to the design** (the twin's draw replaced by the filter's own set): its uses equal the
   design's, so D = 0 exactly.

**A2. No look-ahead (refusing).** The forecast's shift-invariance test (T-2):

- every bar stamped at or after m - 5 is replaced by a seeded random walk (`[20261971, j]`), and separately deleted;
- p_hat(i, R) at every R must be unchanged;
- at no fewer than 200 (session, mark) cuts, including the first marks after 17:00, the `asia` band's first marks
  18:00 and 18:05 (where rv_60's window reaches back to 17:00), the `open` freeze, the marks 09:05, 10:05 and 10:10, a
  roll day and a DST change;
- **replacing the alert day's bars stamped 08:30-08:59 changes no p_hat at any population mark** (E-030);
- no p_hat all-missing or constant.

**A3. The forecast's skill: the positive control.**

- On 2021-2023 out of fold, per band: the per-session mean squared error of y under the HAR against under y = 0 (the
  trailing month alone).
- The improvement's one-sided 95 % lower bound must be above zero, by circular 21-session blocks, 2,000 draws
  (`[20261970, 0]`), in every band with offers.
- A fail means a defect or a market without the stylised fact, so the failure protocol runs and the family waits for
  the lead's ruling under a row. It is not a kill line.

**A4. Calibration and resolution, on the refused population, 2021-2023 out of fold (K2, a kill line).**

- (a) beta > 0 in every fold of the bands `day1` and `day`. Else the map is inverted: the failure protocol.
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
  placebo's of the same counts per stratum (`[20261978, c, 1, 0]`). Resolution only.

**A6. Supply (K1, a kill) and persistence.**

- For each cell: the admitted offers per session, **by year**, by mark hour and day kind; the admitted share per
  stratum and per year.
- **A cell with fewer than 21 sessions holding an admitted offer in any of 2021, 2022 and 2023 is killed** (void).
- Reported, before any outcome: each cell's admitted-session run lengths and the class they imply (6.6); the offers
  with no forecast; the days E-029 voids; **the design's trades at the report-day 07:35:00 entry** (P-16's, inherited,
  E-039 (1)).

**A7. Realised risk.** The stop is P-16's. P-14's allowance-capped form is reported (E-022 (1)).

**A8. Power on record.**

- For each surviving cell: the minimum detectable lift (MDL) of C1 at 80 % power at the family's level on the judged
  block, from section 11's machinery at the judged block's session count, with the cell's choice-span admission
  pattern and the population's centred values on the choice span (their dispersion and dependence; never the admitted
  mean, which stage B reads first), draws `[20261974, 0]`; beside 6.6's Table 9 figure **[Q-55]**.
- It is set against the value bar: the lift in net R worth $500 a year at the cell's uses, by section 10's first-order
  formula.
- **If the MDL exceeds the bar by more than a factor of 3 at every surviving cell, the family is declared a screen**
  (section 15 says what its pass means).
- Written before stage B reads any lift.

**A9. The level on the side-symmetric value (a control; family O's A10).** Q-16 calibrated `cons` on the coin side's
own outcome (11 item 5). On the choice span's population, random selections independent of the outcomes are drawn in
Table 9's six persistence classes at the shares 0.05, 0.1, 0.25 and 0.5, 2,000 per class and share, at each cell's R
(`[20261970, 2, c, g, h, j]`: c the cell, g the class in Table 9's order, h the share, j the draw), and `cons` with the
treated df is applied to y = c - mu_s through `placebo_selection_bound` at one-sided 1 % and 5 %. A class whose
rejection rate's 95 % Clopper-Pearson interval lies wholly above the nominal (the calibration's own criterion) is
recorded as **"`cons` not shown to hold on c in this class"**; for a cell of that class the level then rests on B2's
larger-of rule alone, which section 11 makes the rule anyway, and the verdict says so. A9 reads the population's values
under random selections, not any cell's selection; it kills nothing.

## 10. Stage B: choose on the choice block (2021-01-04 to 2023-12-29, out of fold)

1. **The ranking statistic:** for each cell surviving stage A, L_R (7.3: `placebo_selection_bound`'s estimate on y) on
   the span with the out-of-fold forecasts; strata (mark, year) within those years.
   - Its bootstrap: a stationary bootstrap of sessions, **mean block 63** (the cells' expected class, 6.6), 2,000 draws
     (`[20261972, 0]`). Each draw recomputes L_R, the stratum means included, on the resampled sessions. SE_c is its
     standard deviation over draws.
   - q_B: the 95th percentile over the centred draws of max over cells of (L\*_c - L_c) / SE_c.
   - **Stage B's bootstrap and max-T are an uncalibrated selection device that decides no level** (as F-02's and
     family O's, E-039): the level is stage C's alone.
2. **Kill B:** no eligible cell with L_c / SE_c > q_B. The family **closes**, and the judged block is not read.
3. **Eligible as the pick:**
   - K2's margin: at most 4 % unresolved at its R among its admitted offers in its worst year;
   - **C1-close's form positive on the span** (L_c under the `close` convention above zero);
   - K1 and K-info passed; not dropped by 6.6.
4. **The pick:** among eligible cells above q_B, the largest **first-order valued lift** at its lower limit
   L_c - q_B SE_c:

       $ a year = (L_c - q_B SE_c) / (1 + R_c) x u_c x mean_dv(p) ,

   maximised over the places p that ask R_c:
   - (b) the evaluation (1.5R);
   - (c) the funded opening (3R);
   - (d) funded later (1R);
   - (e) paid (any R).

   The terms:
   - mean_dv(p) is `u_value_map.csv` section `place_values`, base `p16`: a win over a loss in dollars;
   - u_c is the cell's admitted offers a year on the span, capped at `trades_per_year_forward(p)` x the share of the
     place's recorded leaf-days at R_c (`records_leaf`; F-B's rule).

   **This ranking assumes the lift is uniform over admitted offers.** The money is decided by C2 on routed trades
   against the twin designs. Ties go to the smaller R.
5. **Reported for every cell before the pick:** L_c and its halves (on l and r), by year; the kind shares of the
   admitted offers against their strata; L_c under the `close` convention.
6. **What it spends:** nothing of the program's level. One cell reaches judgement.
7. **The record:** every cell's stage A and B readings are written to the result file's `choice` section before the
   judged block is read.

## 11. Stage B2: the critical values, conditional on the judged admissions (family B's and family O's form)

**Why.** The admissions cluster: a fast day admits a run of marks, and the trailing month's level carries admission for
weeks to months (6.6). A slow component of the outcomes that the strata do not remove (anything inside a calendar year,
such as a volatility regime's exit-kind mix) aligns with such runs by chance more often than with a selection that does
not cluster. Family B's third draft found that resampling one realisation cannot certify the family's level against
that and kept the failed check on record (E-030); so the critical values here are conditional on the actual judged
selection and widened by a declared slow component, as family B's and family O's are.

1. **The statistic for every line** (C1, C1-close, C2): **`cons`** -- the members `t21w`, `t42w` and `t63w`, each the
   two-sample difference with CR1 variance from the residual block sums on 21-, 42- and 63-session blocks and the
   treated df (`extended.lift_bound.diff_stats`, exactly as `placebo_selection_bound` and `two_sample_bound` compute
   them). **Each member's critical value is the largest of its nominal t (at its treated df), B2's simulated
   (1 - level) quantile of the same member's t statistic at `a*_pre`, and B2's at `a*_post`**, and each member's lower
   bound is its estimate less that critical value times its se. **`cons` passes only if all three members' lower
   bounds are above zero; its bound is their minimum.** Always the larger-of rule -- no tolerance, no pretest. The
   module's own nominal bound is reported beside.
2. **B2's null at stage C, conditional on the pick's real judged admissions** (read under `stage_C_forecast` and hashed
   before any outcome is read):
   - **The values:** each null replicate y\* is built from the choice span's own per-offer centred values y at each R
     the line needs (every population offer, 2021-2023), at the session level:
     - resampled by a stationary bootstrap with **mean block 63 sessions** to the judged block's session count;
     - each judged session's offers take the drawn session's values at the same marks (a missing mark dropped);
   - **plus a declared slow component** a\*(R) x rho_t: rho_t a two-state Markov sign switching with probability 1/63
     per session (a random start). Why 1/63: the cells' expected class is up to `block63` (6.6), and a component
     slower than a year is removed by the re-centring within the year's strata below;
   - **the amplitude a\*(R), one rule, stated identically here and in section 8** (E-047 (1)'s form): **(a) = the
     larger of (a1) the largest absolute mean, over the choice span's disjoint 63-session blocks in session order, of
     the per-session mean of y(R) over every population offer, and (a2) the pick's own out-of-fold lift at R by calendar
     year on the span -- its largest absolute deviation of a year's lift from the span's lift, plus the absolute value
     of the span's lift; `a*_pre`(R) = 3 (a); (d) = the largest absolute calendar-year lift at R on the judged block
     (2024, 2025, 2026 to 07-16) of the pick itself and of its seeded twin draw (d = 0), read under
     `stage_C_judgement`, after the judgement; `a*_post`(R) = the larger of `a*_pre`(R) and (d).** In parts:
     - (a2) is the model's own term on the choice block: the placebo twin's expectation is zero by construction, so it
       has no yearly lift of its own to read (family B's (a) reads its coin twin's); (a2) is a recorded rule's
       choice-block outcome, read in B2 and disclosed;
     - `a*_pre` = 3 (a) is fixed now;
     - (d) can only raise the critical value; its pick's own term is E-047 (1)'s: the twin's term alone over-rejects
       when the twin's lift sat low through every judged year (`tests/test_family_b_b2.py`), and its cost is power;
     - C1 uses a\*(R_c) under `STAGE2`; C1-close its own (a) and (d) under `close`; C2 each use's a\*(R_j) at its R;
     - **no amplitude is borrowed from Stage 2's S1/S3 files** (8: dropped): they hold whole-window per-offer sided
       lifts only (E-043, E-046 (3)), with no 2024-2026 figure, and a sided follow lift is not this family's
       side-symmetric value; (d) takes the judged block's own scale instead;
   - **then re-centred within the judged strata** (mark, year), so the twin's expectation is zero exactly in every
     replicate;
   - the line's member statistics recomputed with the real judged admissions (for C2, with both designs' judged uses,
     their R and their weights held fixed, read under `stage_C_campaign`);
   - **draws** `default_rng([20261975, line, a, j])`, line 0 for C1, 1 for C1-close and 2 for C2; a = 0 at `a*_pre`, 1
     at `a*_post`; at least **1,000,000 replicates** per line and amplitude (light in memory; CPU minutes to hours).
3. **"A slow component larger than declared"** is beside the verdict as an assumption that carries the level.
4. **What it cannot see:** a slow component slower or larger than the declared one and than (d) shows. The
   confirmation on unread data carries the decision against it.
5. **What Q-16 calibrated, and what it means for the side-symmetric value.** Q-16's selection nulls used **the coin
   side's own outcome** -- the win at 1R and net R at 3R of P-16's judged offers (calibration note 2.4) -- under random
   selections in six persistence classes. This family's outcome is the side-symmetric c (and its centred y), which
   differs in two ways: the coin's direction noise is removed, so its per-offer dispersion is smaller; and its main
   slow part is the volatility-driven mix of exit kinds, which the coin's noise no longer dilutes. So its dependence is
   **not in the class Q-16 calibrated** ("a level is only as good as the null class", calibration note 7.4 item 1).
   What follows: (i) `cons`'s level on c is not established by Q-16 and is checked on the choice span by A9; (ii) the
   level each line is judged at rests on the per-member larger-of rule with B2's null built from c's own choice-span
   values, which is why the rule applies always; (iii) Table 9's power is a guide for c, not its calibration (6.6).
   C2's two-sample form on routed uses, with offers reused across paths, is likewise outside Q-16's nulls and rests on
   B2 in the same way.
6. Fixed now. T-10 checks B2's machinery at declared levels (19.2); **the family's level rests on the larger-of rule,
   not on T-10**.

## 12. Stage C: judge the pick once, on the judged block (2024-01-02 to 2026-07-16)

**The judge's inputs:** the pick and the frozen forecast by their pinned hashes (T-9); strata (mark, year) within the
judged block. **In order:** `stage_C_forecast` (the judged bars: the pick's p_hat and admissions, the strata counts and
the run lengths, hashed; no walk is read under it) -> B2 for C1 and C1-close at `a*_pre` -> `stage_C_judgement` (the
population's walks at every R to 3, both sides, under both flatten conventions: L, C1, C1-close, the halves, (d)) -> B2
at `a*_post` -> `stage_C_campaign` (the gate campaigns of the design and its two twin designs, the routing records, B2
for C2, V_line, the floors) -> `stage_C_scorecard` (13) -> `rcap_reading` (14).

**The design passes only if every line holds. A fail of any line closes the family**, its reason in a decision row.
Each line at the family's level 0.05 / (k (k + 1)), by `cons` with each member at the largest of its nominal t and B2's
critical values (11):

- **C1, the pass line (E-023 (2)):** `placebo_selection_bound(y, session, selected, ...)` on the judged block's
  population at the pick's R, y = c - mu_s (7.3); **its `cons` lower bound above zero.**
- **C1-close:** the same under the `close` flatten convention: a lift that is only Stage 2's conservative flatten price
  fails here. An intersection at the same level: no extra spend.
- **C2, worth something where it is used:** on the gate campaigns of the design and its two twin designs (7.4),
  `two_sample_bound` on w; **V_line at D's `cons` lower bound at least $500 a year.** This is CHARTER section 3's "its
  value at that bound", priced on the trades the design takes against those a random admission takes under the same
  routing.
  - **The bound arm's shift is P-16's registered shift at each R**, for the design, its twin designs and P-16 alike.
    Every trade is a P-16-schedule coin trade walked the same way, so the campaigns differ only by the admission. The
    alternative, each design's own bounds by the base's era rule, would be estimated over both blocks again (the F-P
    review's N2) and would move with the admitted offers' outcomes.
  - **Not calibrated, said with the verdict:** the value-map price at the bound (calibration note 7.4 item 10); the
    two-sample form on reused routed uses (11 item 5).
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
  - L_R and its halves **by calendar year on each block** (the place the reverse walk-forward held, E-031 (2)), and at
    each R in net R;
  - the kind shares (target, stop, flatten, breakeven) of the admitted offers against their strata, and the **kind
    decomposition** of L: the part from the flatten share's change at fixed costs and the part from the exit ticks'
    composition;
  - L_R under Q-20's corrected moves (`STAGE2_BE_BOTH`, merged b7232ba);
  - the seeded twin's draw (`[20261978, c, 0, 0]`), by `two_sample_bound`;
  - each member's nominal and B2 critical values at `a*_pre` and `a*_post`, and (a), (d); A9's class verdict for the
    pick's class;
  - V(design) and V(twin) undifferenced, and the uniform-lift valuation beside V_line;
  - the forecast's judged calibration, within-stratum AUC and the pick's judged run lengths with the class they imply
    (6.6);
  - planned against realised supply; the design's trades at the report-day 07:35:00 entry (P-16's, E-039 (1));
  - Stage 2's S-program guard (the design's paired growth at the bound against P-16's, D-568 (2)), never a line.

**Dropped (E-031 (2)):** the reverse walk-forward.

## 13. The journey scorecard -- beside, never the pass line (CHARTER section 2; E-008, E-014, E-015, E-023)

**Which designs.** Read for the pick only, after stage C has read, whatever its verdict. A family closed at stage A or
at Kill B reads none.

- **The design** (P-16 plus the pick's admissions), **its twin design** (draw 0) and **P-16**, paired (the same starts,
  the same coin, the same seeds), with R\* = P-14 beside.
- **What each pair shows.** The design against its twin design is the selection's journey effect (supply and the
  bracket mix cancel); the twin design against P-16 is supply's own effect, which E-023 does not credit and a user
  still feels.
- If the pick is carried, the design with Part II's `R-cap` added is read beside too (described, E-023 (1)).
- Journeys come from the vendored U1 replay in history's order, through Q-17's adapter for the readings beside
  (`extended/user_beside.py`, merged b7232ba).

**On which starts.** The judged block's starts (`stage_C_scorecard`), labelled as such; beside, the starts from
2021-01-04 (the first out-of-fold year; no forecast exists for 2020's offers), **purged by horizon per measure** so that
no choice-block journey reads a judged-block session (Stage 2's `u_select.block` purge, the F-P review's F6).

**What is read.**

- **P** and the guarded measures S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c; the reported-only S2, S3d, S6, Q
  (`vendor/stage2/docs/USER_MILESTONES.md`). S3c is reported with the caveat that the design adds trades to P-16's
  stream (E-008 compares it within one stream).
- **The journey variables (E-014):**
  - sessions and cash to the first pass; sessions and cash to the first payout;
  - **sessions to break-even** (the first session whose cumulative net cash is at or above zero, daily), the share of
    starts reaching it by months 1, 2, 3, 6 and 12, and the share that later fall back below zero;
  - **the path's evenness:** the share of months with a positive net change, the longest run of months without a
    payout, the spread of monthly net, the deepest fall of cumulative net from its running high after break-even,
    payouts per month, the largest single month's share of the year's payouts.
- **Every measure as a distribution over start days** (median, p10, p90), with its uncertainty from the effective
  number of independent starts and the start day's share of the variance (`user_drivers.csv` section
  `design_vs_luck`).
- **The paired readings:** the per-start difference against P-16 and against the twin design as distributions, and the
  shares of starts better, equal and worse at months 1, 2, 3, 6 and 12. Any draws come from `[20261976, 0]`.
- **The P comparison (E-035 (3)):** the paired P difference against P-16 and against the twin design by
  `extended/p_bound`'s **`pcons`**, one-sided at 0.05, reported, never a line (it holds its level and has almost no
  power on this block); `bm63c` beside once its critical-value table comes from a clean run and is pinned; `pcons`'s
  fixed-b critical values from the module's own seed. Stage 2 D-621 (3)'s percentile bound is not computed (E-007 (1)).
- **The supply reading:** funded trades per live account-day and the share of account-sessions without a trade,
  against P-16's (1 (v)).
- **The frontier** on P, S1, S3a and S5a; **the menu** under E-015's limits once the operator approves them, as
  **flags only** (a limit never fails a design, E-015 (3)); **the evenness trade-off curve** (E-015 (4)).
- **E-007 (e)'s readings** (Q-17's adapter): the denial ladder at 10, 25 and 50 % (draws `[20261976, 1]`); the
  placement on; the binding Focused Trader models; all-accounts forfeiture; P by month, mean net, CVaR10, P under a
  bankroll limit, the effective sample size and the minimum detectable difference.
- **Not modelled, said wherever the scorecard appears:** a user who stops when their own money runs out, the user's
  time, taxes; **and the unstated news rules (E-034):** which events count as "major news" under 10305426 and whether
  holding an open position through one counts -- unstated; the GDP release minute -- unstated; the share of admitted
  trades held through an ISM or GDP release -- unknown (no such calendar on disk); **and E-039 (1)'s inheritance:**
  P-16's trades keep their report-day 07:35:00 entry, on the stated end of Topstep's Tier 1 window (U7 (a)), with their
  count (A6).

---

## 14. Part II -- the described reading `R-cap` (E-023 (1)): the funded opening's R where it resolves

**Status:** a described reading. **Never carried, no program family number, nothing of the budget spent.** It is
declared here and pinned with this file, so nothing in it is chosen after a look. *E-041 now admits described readings
in files of their own (`prereg/RD-nn_<slug>.md`, on exactly the F- rules); if the lead prefers, this section moves
unchanged to such a file (21 item 10).*

### 14.1 What it is

- **On P-16's own offers,** every offer's outcome columns above its forecast cap R_cap(i) (6.5) take R_cap(i)'s
  outcome.
  - The forecasts are the out-of-fold ones on 2021-2023 and the final forecast from 2024-01-02.
  - No offer of 2020 has an out-of-fold forecast, so the reading starts from 2021-01-04.
- A table leaf asking more than the cap takes the cap, its dollar risk unchanged. An offer at which no R the table offers
  is admitted keeps the table's smallest R. **No offer is dropped or added.**
- **Report days (E-039 (1)):** the cap acts only on entries strictly after 07:35:00 CT. A report day's 07:35 trade is
  P-16's registered trade and keeps P-16's bracket, uncapped; their count is reported.
- **Where it binds:** on the 3R ask -- the funded opening (handoff 2.5) -- at marks and on days forecast slow, and on
  any other leaf whose R exceeds a cap.
- The bands `evening`, `asia`, `london` and `open` (with its freeze) serve it; no input of an `open`-band offer reads a
  bar of its day stamped 08:30 or later.

### 14.2 What it changes, stated exactly (the F-P review's F10)

- The offered trades and their entries are P-16's. What changes is **the bracket** of an offer whose cap is below the
  ask.
- So, after the first capped trade, everything that follows can diverge: an account's balance; the next leaf; which
  offer the router gives to which account (a capped opening resolves sooner and frees the slot); purchases; fees.
- **The pairing is on start days with identical offers, not identical executed trades.**

### 14.3 What is read (all on the verdict arm, on the starts from 2021-01-04 and on the judged block's starts, paired with P-16)

- **(a)** Every measure of section 13, its paired distribution, and who it helps and hurts at months 1, 2, 3, 6 and 12.
- **(b)** The mechanics:
  - the share of P-16's offers capped below 3R, by band and year;
  - the share of the design's funded openings capped, and the R they took;
  - the forecast hold time of capped against uncapped openings (stop x target / the forecast variance);
  - the realised minutes the firm's slot was held by openings, against P-16's. **This is (u3)'s question, answered
    descriptively** (family O judges it).
- **(c)** The evenness trade-off: one point of P against each evenness measure, beside P-16's.
- **(d)** The denial ladder, the placement and the Focused Trader models, as section 13; its "not modelled" note.
- **The prior, disclosed:**
  - Stage 2 found every change to the funded leg (smaller, flatter, equal days) worse for a user (handoff 3.2);
  - a capped opening gives up the place of greatest value of a win (`u_value_map.csv`, place (c));
  - by the LeBaron effect, the slow days it caps are where a 3R coin might win more than 1/4 (the scout's 5.2).
- Expected: worse or level on P. Its reading is the record of what a target chosen by resolution costs or gains a user.

### 14.4 Its identity, its reads and its run

- With the cap disabled (every cap 3), the design is P-16 bit for bit. A1 items 2-4 hold for it.
- Its judged-block reads are under `rcap_reading` (20.1): the judged bars' forecasts at P-16's own marks, P-16's walks
  at every R, and the paired U1 replays on the judged block's starts. Its choice-block reading (the starts from
  2021-01-04) needs no tag.
- Run once, in run 2 (20.2), after the forecast's hash is pinned, whatever Part I's fate. Its draws, if any, come from
  `[20261976, 2]`.
- Results go to its own result file (section 20.2) with `prereg_id` this file's and `numbered = false`.

---

## 15. What a pass and a fail mean

**CARRIED** (Part I: every line of stage C and every floor holds).

- A development finding on a late-development block.
- The design -- P-16's schedule plus the pick's forecast admission -- takes a registration id (Stage 2 D-621 (9)'s house
  form), a model card (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`: the forecast's coefficients and calibration),
  its registered development test, the auditor and **one confirmation** (section 16), which carries the decision
  (D-189).
- If stage A declared the family a screen, a pass is still CARRIED, and the carrying row says the development read was
  a screen at its MDL ratio.
- What a user is told is the scorecard as a distribution (section 13), never one number.

**CLOSED** at stage A (an identity, A3's control unresolved, or every cell killed or dropped), at B (Kill B), or at C
(a line or a floor).

- The reason goes in a decision row.
- A close at B or C reads **"no selection lift above the MDL at this family's level"**, never "a forecast does not
  help". If the scorecard beside shows supply gains, they are recorded as supply, which E-023's twin does not credit.
- **A cell dropped before the pin** by 6.6 reads **"not judgeable on this block at its persistence"**. If every cell is
  dropped, the drafter's proposal is that the draft is not pinned and takes no k (6.6; 21 item 2).
- **The closure binds** (D-277's boundary): a later family on this forecast or this population names this closure,
  says what changed and why it is a different hypothesis, and is not judged on this family's judged block.

**Part II** closes by construction with its reading. That reading is the result.

## 16. The confirmation, declared before any development read

- **The window:** NQ from **2026-07-17** (`config/windows.yaml`, `reserve`). It is not on disk and never read until a
  carried design is registered. It is **a purchase, the operator's**, stated in `docs/OPERATOR_SETUP.md` and waited
  for. It would be NQ's fourth confirmation window, **the operator's decision** (D-107, D-461).
- Stage 2's draft P-16 confirmation (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`) and F-02's, family B's and
  family O's drafts target the same window. If any test reads it first, the lead records that before registration, and
  the operator decides whether it can still confirm this pick.
- **What it tests -- the pick's trades, not P.** With the pinned forecast, the pick's R and q fixed:
  - C1 and C1-close on the window's refused offers, one-sided at the registered 0.05, by `cons` with each member at the
    largest of its nominal t and B2 re-simulated at the window's length (`[20261975, 10 + line, a, j]`): the values
    resampled from 2021-2026's centred values, `a*_pre` = 3 (a) with (a) over 2021-2026, `a*_post` with (d) over the
    window's own calendar years; the bound at 0.05 / N beside (D-189's form);
  - C2 priced from C1's bound at stage C's per-place uses and `mean_dv` at the 95 % bound (the window is too short for
    its own campaigns), at least $500 a year;
  - floor (i) on the window, overall and in every calendar year with at least 63 sessions (a stub year pooled, D-604);
  - the twins' draws from `[20261978, c, 2, d]`.
- **What it cannot test: P.** Six months is about 126 sessions, about 63 starts with a month-3 horizon: no interval on
  P exists there (the phase-0 red team's M1). The scorecard on the window is descriptive.
- **How much data:**
  - at least six months (D-604);
  - and at least the months at which the pick's expected admitted sessions (the lower of its two blocks' rates) reach
    the count at which `cons`, one-sided at 0.05, has 80 % power for a lift equal to **the pick's judged lower bound at
    the family's level**, at the pick's persistence class, by B2's machinery (`[20261974, 1]`). At six months `cons`'s
    63-session member has two blocks; the count rule takes that into account.
  - That count is computed when the pick is carried and written in the carrying row, before any confirmation data
    exist.
  - If it is more than the operator will buy, no confirmation is registered, and the pick stays a development finding.

## 17. Seeds -- 20261970-20261979, checked unique, for the lead to confirm at pinning

| seed | what it draws |
|---|---|
| 20261970 | stage A's draws: `[20261970, 0]` A3's skill, `[20261970, 1]` A5's within-stratum AUC, `[20261970, 2, c, g, h, j]` A9's random selections |
| 20261971 | the build's shift-invariance test's replacement walks (A2, T-2): `[20261971, j]` |
| 20261972 | stage B's bootstrap `[20261972, 0]`. **`[20261972, 1]` is reserved and unused**: it was the first version's reverse walk-forward, struck under E-031 (2); every result file says so |
| 20261973 | the gate campaigns on the judged block, 500 paths each: the design's (C2's uses, floor (i)'s taken trades, the long-run gate floor) and its two twin designs' at the same seed |
| 20261974 | power: `[20261974, 0]` A8's MDL by B2's machinery; `[20261974, 1]` the confirmation's data count (16) |
| 20261975 | stage B2's replicates `[20261975, line, a, j]` (line 0 C1, 1 C1-close, 2 C2; a 0 at `a*_pre`, 1 at `a*_post`); the confirmation's re-simulation `[20261975, 10 + line, a, j]` |
| 20261976 | the scorecard's paired draws `[20261976, 0]`; the denial ladder for this file's designs `[20261976, 1]`; Part II's draws `[20261976, 2]` |
| 20261977 | the build's synthetic tests: `tests/test_family_r_band_exit.py` (`[20261977, j, ...]`, j = 0..9); T-3's synthetic judged block `[20261977, 10]`; T-10's synthetic populations `[20261977, 20, j]` |
| 20261978 | the placebo-selection twins and twin designs: `[20261978, c, b, d]`, c the cell (0 `adm@1`, 1 `adm@1.5`, 2 `adm@3`), b the block (0 judged, 1 the choice span, 2 the confirmation), d the draw (0, 1); draw 0 on the judged block is also the seeded twin beside C1 |
| 20261979 | reserved; unused, and every result file says so |

The U1 replays draw nothing at 0 % denial with the placement off; where Q-17's adapter draws (the denial ladder
beside), its per-start seeds are its own rule over 20261976's. `cons` draws nothing; `pcons`'s fixed-b critical values
use `extended/p_bound`'s own seed.

**The check (first version, 2026-11-16).** `grep -rIowh --exclude-dir=.git -E "2026197[0-9]" .` over the whole working
tree, the vendored snapshot and its results included, found 20261970 and 20261979 only in the first brief
(`docs/briefs/Q-38_2026-11-16.md`), as the proposal's range; without word bounds, one more hit, a digit run inside a
longer number in one vendored result file -- not a seed. `git grep` on every local and remote branch found the same.

**The check (this version, on master 7cc49b9 fast-forwarded into wt/wt-levels):**

- `grep -rIown --exclude-dir=.git --exclude-dir=data -E "2026197[0-9]" .` over the working tree, the vendored snapshot
  and its results included: hits in this file and its test, in the first brief (the range), and in family O's draft,
  which names this block as taken ("20261970-79 (family R)") and uses none of it. Without word bounds, the same digit
  run inside a longer number in one vendored result file.
- `git grep -I -l -w -E "2026197[0-9]"` over every one of the repository's 176 commits (`git rev-list --all`, every
  local and remote branch), outside `vendor/`: the same four files and nothing else.
- T-1 asserts that the seed table lists 20261970-20261979 once each and that no other file under `prereg/` names any of
  them except as the taken range.
- **Not searched:** Stage 2's working tree beyond its vendored snapshot (its decision log and scripts are vendored and
  were searched).

**Neighbouring blocks, taken:** 20261910-19 (Q-16), 20261920-29 (Q-17, Q-20), 20261930-39 (F-02), 20261940-49 (F-P),
20261950-59 (Q-18), 20261960-69 (family B), and family O's and the firms reading's blocks above this one (E-038, E-046;
not written out here, because each of those drafts' own tests refuses its seeds in any other declaration).

**Inherited, used only as their owners registered them:** 20261102 (P-16's coin, every grid mark); 20261206 (P-16's
gate, the identity); 20261131 (P-14's, beside); 20261600 + i and 20261700 (Stage 2's coin sequences and D-621 (3),
beside only); 20261913 and 20261914 (Q-16's module seeds, inside `extended.lift_bound`); 20261919 (`extended/p_bound`'s).

## 18. Multiplicity and the budget

1. **k.** The next free program family number at the pin, with level 0.05 / (k (k + 1)), written by the gatekeeper in
   the pinning row.
2. **Counted:**
   - **3 cells** (`adm@1`, `adm@1.5`, `adm@3`), each counted whether dropped before the pin (6.6), killed at A, closed
     at B or read at C;
   - **0 searched configurations**;
   - **35 fitted values** inside the walk-forward (23 coefficients, 12 calibration; E-031 (1)), fitted in each of its
     three folds and the final fit, none searched.

   The identities, the controls (A3, A5's placebo comparison, A9), B2's replicates, the seeded twins and the readings
   beside are not trials: nothing is chosen from them.
3. **One cell reaches judgement.** C1, C1-close, C2 and the floors are an intersection at one level. Stage B spends
   nothing of the program's budget.
4. **Part II** is one described reading under E-023 (1): no number, no budget, recorded in its own row.
5. **The program's honesty sentence:**
   - Stage 2 ran programs S and U on this window, each with its own 5 %;
   - the late marks' average resolution has been read on both blocks, and the coin-side outcomes' dispersion under
     random selections by Q-16 (section 2);
   - the development level is a screening threshold, and the decision is carried by one confirmation on unread data
     (D-189), if the operator buys one.

## 19. The build: adapters, identities and tests (after the pin, before any reading)

### 19.1 The code (in `extended/`, never in `vendor/`)

1. **`extended/resolution_forecast.py`.** IV, M, x1-x3, the six bands and their freezes, the least-squares fit, Psi (the
   series and the images), the calibration, p_hat and R_cap.
   - Bars come only through `extended/reader.py`, the frame P-16's walked sessions.
   - The library's `grid`, `slot` and trailing median are imported, not copied; every window over a day's bars is
     bounded at its first bar.
   - If family O is pinned too, its `u3` forecast is this module's (T-7).
2. **The cell builder.** P-16's cell as `rc_width_screen.build` builds it, with this repository's walker, under
   `STAGE2` and `close`. The added offers are the population's admitted ones, their outcome columns above their cap
   rewritten to the cap's (a plain-data transformation of the trades frame).
   - The R a trade actually took is recorded beside, so a record never shows a capped trade as 3R.
   - No vendored attribute is substituted (the lesson of E-011's first run).
3. **The twin designs.** The seeded placebo admission per stratum, its caps assigned from the design's caps per
   stratum (7.2), built by the same builder.
4. **The place-recording adapter** (Q-70; family B's and family O's): every simulated trade's offer, R and place on the
   gate campaigns of the design and its twin designs; held to its identity -- P-16's registered campaign re-run as U2
   ran it reproduces `u_value_map.csv`'s `trades_per_year_records` for `p16`.
5. **The estimand.** c_i(R), the strata means, y, the calls of 7.3 and 7.4, each member's statistic, B2 with its
   amplitude rule, the halves, V_line, V(design) and V(twin).

### 19.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-1 | **written now:** `tests/test_family_r_band_exit.py`. The first version's six: Psi's series equals the images; it falls with u, rises with R and integrates to R; a lattice walk converges to it; at two volatilities the target share is 1/(1+R) and the exit time scales as 1/variance; a volatility forecast on persistent days moves the open share and the target share but not the mean outcome; with a flatten cost the lift over the population mean is that cost times the open-share drop. **Added in this version:** `placebo_selection_bound` on the (mark, year)-centred values estimates exactly the exact-form lift, and on the raw values adds the strata-composition term the clock makes non-zero; **on a routing that takes admitted offers more often on fast days, a random admission's routed single-sample mean is biased while the difference against a twin design under the same routing averages zero, and `two_sample_bound`'s estimate is that difference exactly (C2's form)**; the population's clock -- 73 marks 09:05-15:05, `day1` 09:05-10:05 and `day` 10:10-15:05, no used input of a population offer reading an alert-day bar stamped 08:30-08:59, 10:10 the first mark whose live window clears it, Part II's `open` freeze reading nothing from 08:25 on; this file's `Judged-block reads:` line gives exactly section 20.1's purposes by `extended.reader.declared_purposes`, none a choice or fitting purpose; this file's seed table is 20261970-20261979 once each, and no other `prereg/` file names any of them except as the taken range (seeds `[20261977, ...]`) |
| T-2 | the forecast's shift invariance (A2): replacing, and deleting, every bar stamped at or after m - 5 changes no p_hat, at the cuts A2 names; replacing the alert day's 08:30-08:59 bars changes no p_hat at a population mark; x3 equals 2 x `rv_tod` at every `day`-band alert; no window wraps at an overnight slot; no p_hat all-missing or constant |
| T-3 (heavy, under the run lock) | stages A and B, their result sections and the final forecast's hash are byte-identical when every judged-block bar is replaced by a seeded synthetic walk (`[20261977, 10]`) |
| T-4 | the builder with the filter off gives P-16's `TRADES_SHA256`; with every cap 3 Part II's design is P-16's trades |
| T-5 | the cap: above R_cap every outcome column equals R_cap's; the dollar risk unchanged; under Part II no offer is dropped or added, and a report day's 07:35 trade is never capped; the R taken recorded; the twin designs carry the design's caps per stratum |
| T-6 | the population: only grid marks 09:05-15:05 on P-16's day kinds less E-029's voids; never a news-cut mark, an FOMC day or an early close; never a mark in 08:30-09:00; the strata as declared |
| T-7 | the least-squares fit equals a direct normal-equations solve, and the calibration a Newton solve, on synthetic data to 1e-8; a planted HAR process is recovered with the right signs; on synthetic bars with clustered variance the forecast beats y = 0 and the calibrated p_hat is calibrated within its Monte Carlo band; if family O is pinned too, its `u3` fit and this one give the same coefficients on a shared synthetic set |
| T-8 | the reader: every bar and walk read goes through `extended/reader.py` with its purpose; an untagged judged read raises; an identity read outside `identity/*.py` raises (Q-32's and Q-48's own tests, re-run at the build's commit) |
| T-9 | the judge's entry point reads the frozen forecast by its hash and cannot fit; stage C reads the pick from stage B's result file by its sha256 |
| T-10 (slow tier, minutes) | **B2's machinery on synthetic data at declared levels** (family O's T-10 form): a synthetic population with a planted slow component and a clustered, regime-following admission independent of it; the per-member largest-of rule under `cons` at one-sided **1 % and 5 %**; **2,000 outer replications**, each B2 quantile from **20,000 inner replicates** (`[20261977, 20, j]`). **Failure rule:** the test fails if a level's rejection rate has its 95 % Clopper-Pearson interval wholly above the nominal; a failure is kept on record and runs the failure protocol, never a rerun to pass. The family's level rests on the larger-of rule at the family's level, not on T-10 |
| T-11 | this file's seeds appear nowhere else in the build's commit except the family's own modules and tests |
| T-12 (slow) | A1 items 2-4 and 7 at 4 paths and 4 starts; the full 500 paths and every start are the run's first stage (heavy) |
| T-13 | the place-recording adapter's identity (19.1 item 4) at 4 paths and 4 starts; on a twin design every recorded admitted use is in the placebo's set |
| T-14 | the estimand on the family's own code: L equals `placebo_selection_bound`'s estimate on y; an uninformative filter's lift averages zero; on a synthetic routing record D and V_line equal their hand sums; the stage-B pick is a function of the choice section alone |

## 20. Outputs, the reads and the runs

### 20.1 The judged block's reads (E-026)

The reader (`extended/reader.py`) authorises a judged-block read only for a purpose named on this line of the pinned
file:

- **Judged-block reads:** `stage_C_forecast`, `stage_C_judgement`, `stage_C_campaign`, `stage_C_scorecard`, `rcap_reading`

What each is for, in stage C's order (12): `stage_C_forecast` -- the judged bars, to compute the pick's p_hat and
admissions with the frozen forecast, the strata counts and the run lengths (no walk is read under it);
`stage_C_judgement` -- the population's walks at every R to 3, both sides, under both flatten conventions (C1,
C1-close, the halves, (d), the beside readings of L); `stage_C_campaign` -- the gate campaigns of the design and its two
twin designs on the judged block, with the routing records (C2, B2 for C2, floor (i)'s taken trades, floor (iii));
`stage_C_scorecard` -- the paired U1 replays of the design, its twin design and P-16 on the judged block's starts and
Q-17's readings (13); `rcap_reading` -- Part II's judged-block reading (14.4). Each is read once, from a clean run of a
committed tree, ledgered before it reads. No choosing or fitting purpose is named, and the reader would refuse one.

### 20.2 Files and the runs

- **Files**, each with its sidecar manifest through `extended.results.write_result`:
  - `results/fr_resolution.csv`, sections `identity`, `forecast`, `calibration`, `persistence`, `supply`, `power`,
    `level_control`, `choice`, `level`, `judged`, `campaign`, `floor`, `beside`;
  - `results/fr_journey.csv`, the scorecard of section 13;
  - `results/fr_rcap.csv`, Part II.

  Each manifest carries: `prereg_id` this file's F-id (Part II's with `numbered = false`); the cell counts (3 cells, the
  dropped ones named, 0 searched, 35 fitted values); every seed and parameter, `[20261972, 1]` and 20261979 stated
  reserved and unused; the frozen forecast's hash; the population frame's and the admissions' hashes; the sha256 of
  `vendor/DATA_MANIFEST_stage2.sha256` and of `config/calendar_early_closes.csv` (E-029); the git blob ids of
  `extended/lift_bound.py` and `extended/p_bound.py`. Every file is EXPLORATORY until a carried design is registered.
- **The runs: two, each once**, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock,
  watched to its end.
  - **Run 1 (the choice block only):** stage A (the identities first, from their identity scripts; A9), the forecast's
    walk-forward and final fit, stage B. It writes the `identity` to `choice` sections, the frozen forecast and its
    hash, and the pick. It reads no judged-block bar or walk under this file's purposes.
  - **Between them, the lead's row:** the final forecast's hash and the pick, by the sha256 of run 1's result file,
    pinned in a decision row and committed.
  - **Run 2 (from a clean checkout of that commit):** `stage_C_forecast`, B2, `stage_C_judgement`, `stage_C_campaign`,
    the floors, `stage_C_scorecard`, then `rcap_reading`. The judge's entry point reads the pick and the forecast by
    their pinned hashes and cannot fit (T-9). Before stage C the run asserts `extended/lift_bound.py`'s blob
    `984f3467a4a05aa790d3ea43e94ac7761f0725b2`, and before the scorecard `extended/p_bound.py`'s blob
    `f5b29710e243f97a2795e57f6458512fea99199b`.
  - **If Part I closes at stage A or at Kill B**, run 2 is Part II alone (`rcap_reading` and its choice-span starts).
  - **Weight: heavy.** Run 1 walks every grid mark from 09:05 of every session at 150 ticks on both sides under two
    flatten conventions, and P-16's own marks for the calibration (E-011's P-16 run is the nearest measure of memory);
    run 2 runs three gate campaigns at 500 paths, the U1 replays of three designs on two arms, and Part II's replays:
    many hours each, at two workers.
  - Within a run, each stage's file is written before the next reads anything. A kill stops the sequence.
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run of each is read.

## 21. Open before the pin

**The lead's:**

1. **The deferral (E-028 (2)):** pinned, if at all, only after F-02 and family B, at the next free k.
2. **Q-55's clean rerun on record** (E-035 (4)), and **6.6's power column filled from its Table 9**, the drop rule
   applied and recorded under the pinning row. **If every cell is dropped**, the drafter's proposal: the draft is not
   pinned and takes no k; its closure is recorded under a row as "not judgeable on this block at its persistence";
   Part II and E-028 (2)'s supply question go to described readings.
3. **Optional, the lead's call:** the bars-only run-length count of 6.6 on the choice block before the pin, under a row.
4. **The strata, a choice before any read:** if the lead wants a question this block can judge, matching the twin
   within **(mark, calendar month)** would remove the month's level from the contrast and leave the forecast's
   day-level part (x1-x3), expected class `session` to `block5`. That is a different hypothesis -- the day's forecast
   within its month, not the regime -- so it would be a new draft, never a change to this one after its pin.
5. **The fitted values under E-031 (1)** (35: 23 coefficients and 12 calibration values, inside the choice-block
   walk-forward, hashed and pinned before the judged read): confirmed as admitted.
6. **The place-recording adapter** (Q-70) on the gate for the design and its twin designs, held to its identity;
   Q-47's 500-path identities held (E-044 (3)).
7. **The pass-line code pinned by blob id** in the pinning row, as F-02's (E-044 (1)): `extended/lift_bound.py`
   `984f3467a4a05aa790d3ea43e94ac7761f0725b2`, `extended/p_bound.py` `f5b29710e243f97a2795e57f6458512fea99199b`.
8. **The verdict arm's shift:** P-16's registered shift at each R for every design here (12, C2).
9. **The value bar for a lever whose textbook lift is a cost effect.** $500 a year is F-02's and F-B's bar. Here the
   lift is, by section 1 (iv), mostly the flatten convention's cost avoided, and C1-close now removes that part. The
   drafter's expectation, recorded now, is a close at stage A (6.6) or at C. The lead decides whether the family is
   worth its k. **Pinning and running it as declared, with that expectation on record, is the drafter's proposal only
   if 6.6 keeps a cell**, because its stage A answers questions wanted anyway: does a forecast sort the late offers,
   and how many would resolve.
10. **Where Part II lives:** in this file, or in a described-reading file of its own (E-041 admits `prereg/RD-nn_*.md`).
11. **The family number:** F-02 and family B first (E-028 (2)).
12. **The seeds** (section 17) confirmed unique at the pin.
13. **The row between the two runs** (20.2): run 1's result file, the pick and the forecast's hash pinned before run 2.
14. **A red-team read of this version.**

*Answered since the first version, no longer open:* Q-16 merged with its statistics (E-035); the reader merged (Q-32,
E-026); the fitted-values row (E-031 (1)); the twin's form (E-035; calibration note 7.3); (u3) carried by family O
(E-039, E-046); the so-far term at 09:05-10:05 (excluded in substance, 6.2; no ruling needed); the news hold (E-034);
report-day entries (E-039 (1)); the reverse walk-forward (struck, E-031 (2)).

**The red team's, in particular:**

- whether 6.6's classes are right -- in particular whether M's level makes every cell `block63`;
- whether strata of (mark, year) are the right "same population" for E-023's twin (and item 4's alternative);
- whether C1-close as a line, and the stage-B eligibility it brings, are right for a lever whose lift is a cost effect;
- whether C2's twin designs carrying the design's caps per stratum (7.2) leak anything of the forecast into the twin,
  and whether two pooled twin draws are enough;
- whether B2's amplitude rule (11 item 2), without an S1/S3 floor, is the right floor (family O's draft adds a
  whole-window S1/S3 floor; it could only raise a critical value);
- whether A9 and the per-member larger-of rule are enough for a dependence class Q-16 did not calibrate.

**The operator's (only when they arise):**

- NQ from 2026-07-17 as a fourth confirmation window (D-107, D-461) and its purchase, only once a pick is carried;
- the levels of E-015's limits (flags only).

## 22. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and
recorded in its own decision row -- never added to this file once pinned.)*
