# Mechanisms for the next signal families: a literature scout (TASK_QUEUE Q-28, 2026-11-15)

> Research only. Nothing was run, no bar, atlas walk or trade file was read, no outcome or statistic of the development
> data was computed, nothing was bought and no form was filled. Every literature figure is the **paper's own number on
> the paper's own sample** (mostly the S&P 500); none is a result of this repository. Back-of-envelope translations are
> marked **[estimate]**: they use only a paper's published figures and textbook Brownian-motion formulas, never our
> data, and none may be copied into a card or declaration as a result. Claims seen only in an abstract or a summary are
> marked **[abstract only]** or **[secondary]**. Stage 2's review (`vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md`,
> "the review" below) was read first. What it covers is cited by its line numbers and not repeated. Numbers from Stage 2's
> result files are not typed here; the file and section are named instead (CLAUDE.md).

## 1. The question

From the brief (`docs/briefs/Q-28_2026-11-15.md`): which mechanisms, documented outside our data, could plausibly give

- **(a)** a few points of win probability on the **funded opening trade** (3R at a funded account's first trade, the
  value map's place (c), handoff 2.7) when used as a **filter on P-16's offers**; or
- **(b)** **predictable resolution speed** (time to the stop or the target) that a sizing or routing rule could use?

The trades are NQ, entered by hand at least five minutes after an alert. Candidates are ranked by the value map's
rule: frequency x plausible lift x the value of a win where it is used (handoff 2.7, last line;
`vendor/stage2/results/u_value_map.csv` sections `place_values` and `bar`).

## 2. The answer in plain language

1. **Bracket geometry decides most of this, and it is textbook probability.** On a price with no drift and no memory,
   a coin-sided bracket wins exactly 1/(1 + R) of the time, at any volatility. Volatility changes only how long the
   trade takes (section 3.1). So the two halves of the question need different things:
   - **(b) speed** needs a volatility forecast. That is the best-documented and longest-lasting effect in this whole
     literature.
   - **(a) win probability** needs a drift on the chosen side, or a price whose moves persist (trend).

   Both pay most on the 3R opening. A drift is earned in proportion to the time a trade is held, and the 3R opening is
   held longest. Trend persistence lifts a coin-sided bracket only when R is not 1, so it can act at 3R and cannot act
   at 1R.
2. **The best candidate for (a) is new and is not a direction rule: a side-free timing filter for the funded opening
   (A1).** The opening keeps its coin side. It waits for a market state in which published work says intraday moves
   persist: volatility above its forecast, a day already trending, or a low predictable volatility. In such a state a
   3R coin bracket should win more than 1/4 of the time. Its mechanism is documented on S&P 500 futures, though not at
   our bracket's scale and not on NQ:
   - Bianco & Renò 2009; Bianco, Corsi & Renò 2009 (intraday serial correlation moves with volatility);
   - Gao et al. 2018; Baltussen et al. 2021 (day-scale persistence, stronger on volatile days);
   - Barbon & Buraschi 2021; Adams et al. (dealer gamma).

   A1 fires often enough that openings barely wait. It can be measured on every offered mark's 3R walk, so it has
   power, and it is not a calendar effect. Its size on NQ is unknown, and the honest prior is that it may be zero.
   **One governance gap:** E-008's pass line, the lift over the coin twin, is zero by construction for any side-free
   filter. A1 cannot be judged until the lead declares its twin (section 7, Q-31).
3. **The best candidate for (b) is a volatility forecast used for routing and admission (B1).** Volatility clusters and
   is forecastable from past ranges and implied volatility (Corsi 2009; Hong, Nolte, Taylor & Zhao 2023; Stage 2's own
   atlas R family, D-136). Scheduled news raises it for hours (Ederington & Lee 1993). The expected time to resolution
   is (stop x target) / variance. A forecast could do three things:
   - admit marks that the unconditional cutoff now refuses (D-525 (4)), such as later US-hours marks on fast days;
   - give the opening its 3R only where the trade will resolve;
   - keep the slow 3R opening from blocking the firm's one position slot.

   Its value on the scorecard is modest, because speed barely moves P (handoff 1.2). It is reported here because it is
   the most certain mechanism.
4. **Rare event effects reappear in value but not in power.** The value map says a rare edge belongs on the funded
   opening, and the opening can wait a few sessions for an event. So three event effects reappear in value:
   - the pre-ISM and pre-GDP overnight drift (the review's rank 1);
   - month-end and threshold rebalancing pressure (Harvey, Mazzoleni & Melone 2026, newer than the review);
   - the day after a VIX spike (Hu et al. 2022, section 5, not covered by the review).

   But the number of independent events on the development span is too small for any of them to clear a family's level
   under E-008 [estimate, section 5.3]. The operator's drop (handoff 3.3) stands unless more history is added.
5. **A correction to the review's rank 1.** P-16 offers no mark in the overnight session of a BLS 08:30 report day
   (`vendor/stage2/propedge/research/resolved_coin.py:161-171`, D-525's cut), so the pre-NFP window is not reachable at
   all. Only ISM and GDP eves remain. Separately, the GDP release minute (07:30 CT, BEA) is not in the BLS day file the
   engine reads, so P-16 offers that mark. This is outside Topstep's Tier 1 list as read by E-007's audit, and is
   recorded for the lead (section 6).

## 3. What the contract asks of a mechanism

### 3.1 Three facts about brackets (textbook; Karlin & Taylor 1975, ch. 7; the optional-stopping theorem)

**(i) No drift: the win rate is set by R, and volatility sets only the time.** For a driftless continuous price with a
stop a and a target b = R x a:

- P(target first) = a / (a + b) = 1 / (1 + R), at any volatility;
- the expected time to resolve is a x b / sigma^2 (sigma^2 the variance per unit time), so a 3R trade takes three times
  as long as a 1R trade with the same stop.

So volatility is a resolution input, never a win-rate input. Stage 2 saw this on the collect map's uneven brackets
(stops one to four times the target): the shares are "a fair coin less costs, on both spans", and the hour changes the
time, not the share (`vendor/stage2/DECISIONS.md:402`, D-383; handoff 3.2, line 248).

**(ii) A small drift adds win probability in proportion to the time held [estimate formula].** For a drift mu,
expanding the gambler's-ruin probability for Brownian motion with drift gives

    P(win) ~ 1/(1 + R) x (1 + mu x b / sigma^2)

If the trade resolves inside a window W over which the drift is mu_W and the variance is sigma_W^2:

    lift in win probability ~ 1/(1 + R) x (mu_W / sigma_W) x (b / sigma_W)

- mu_W / sigma_W is the effect's per-event Sharpe ratio, as a paper reports it.
- b / sigma_W is the target's distance in the window's standard deviations.

At a fixed stop, the lift at 3R is 1.5 times the lift at 1R in win-probability points, and three times in R. Stage 2's
P-15 audit saw the same thing: the asymmetric bracket in a rising market moves the coin's gross edge by R and side
(`vendor/stage2/DECISIONS.md:551`, D-533 (3)). **Slow premia belong on the slow trade, and the funded opening is the
slowest trade the table makes.**

**(iii) Persistence lifts a coin-sided bracket only when R is not 1 [reasoning, not a sourced result].** With a fair
coin's side and no drift, a 1:1 bracket wins 1/2 by symmetry, whatever the path's memory. At R = 3 the two extremes
show the direction:

- Paths that keep going once they start (trend) make the coin's win rate tend to 1/2: the far target is reached
  whenever the side matches.
- Paths that oscillate around the entry (mean reversion) make it tend to 0: the near stop is hit first.

So a **side-free** state that predicts persistence over the bracket's range can lift the 3R opening and cannot lift a
1R trade. One consequence: **Stage 2's S2 state gates (D-581, D-582: volatility thirds; a trend state) were read on
P-16's whole trade stream**, most of it at 1R to 1.5R (handoff 2.5). That reading does not test this mechanism.

**(iv) E-008's coin twin cancels a side-free effect.** The twin is "the same entries with a fair coin's side"
(CHARTER section 3). A filter that keeps the coin's side raises the twin's win rate by exactly as much as the design's,
so its measured lift is zero. A side-free filter needs a different twin: the same population with a **placebo
selection** of the same firing share, drawn by a fixed seed. That is a decision row for the lead (section 7). If E-008's
words do not admit it, it is the operator's.

### 3.2 Where the funded opening is, and what bounds its supply

- **P-16 is an overnight design.** Every day's last offered mark is 09:00 CT, so the "all-session" cell trades 17:00
  to 09:00 CT (`vendor/stage2/DECISIONS.md:636`, D-618 (3)).
- **Its US-hours offers at 37.5 points are the marks 08:30-09:00 only.** 09:05 fails the resolution line (the red
  team's reading of `rc_width_screen.csv` rows 191-198, `docs/reviews/DRAFT_F-B_multifeature_2026-11-15.md:99-109`).
  That window is inside Stage 2's closed 08:30 opening-range branch: whether any later hypothesis there is "genuinely
  different" is reserved to the operator (`vendor/stage2/DECISIONS.md:300`, D-281 (3)), and the audit's default is
  exclusion.
- **A US-hours user has the 25-point US cell instead:** marks 08:30-12:00 CT, offered R capped at 2.5
  (`vendor/stage2/DECISIONS.md:660`, D-642 (a)).
- **Where P-16's funded openings actually fall is not in any vendored file.**
  `vendor/stage2/results/u_xfa_day_budget.csv` section `opening_trade` has no mark, hour or day-kind column. The red
  team inferred that in a six-mark RTH design the opening is "mostly the session's first offer" (M-3, lines 175-192).
  This is unknown 1 (section 8).
- **The openings' yearly supply caps any opening rule's uses.** A filter that fires on a fair share of sessions only
  delays openings. It does not drop them, because the router uses a few percent of what it is offered (handoff 2.5,
  `signal_supply`).
- **The one position at a time across a firm (D-429) makes a slow 3R opening hold the firm's slot.** This is why speed
  (b) has some value at the opening.
- **On a BLS 08:30 report day the whole overnight session is not offered.** The trades builder drops a report day's
  (`day_kind` 'b') slots before the cut on the trading-day clock, which starts at 17:00 CT
  (`vendor/stage2/propedge/research/resolved_coin.py:161-171`, `288-311`; `atlas_local.py:13-15`). D-533 then moved
  the cut to 07:35 CT.

### 3.3 Power is counted in independent events, not trades

E-008 judges the lift on the judged block (starts from 2024). An effect tied to a calendar or daily state has about one
independent observation per event, however many offers fall inside it. The review made the same point for six years of
data (lines 40-45). The operator dropped rare calendar effects for this reason (handoff 3.3, lines 267-268). A
side-free state filter read on every mark's 3R walk has about one observation per session and state, which is far
more.

## 4. The ranking

Ranked by frequency x plausible lift x value of a win where used. "Openings" means the funded openings' yearly supply
(handoff 2.7; `u_value_map.csv` section `bar`).

| rank | id | mechanism (who is on the other side) | kind | used at | fires (all hours / US hours) | plausible lift | persisted after publication? | 5-min delay, hand entry | conduct | judgeable under E-008 on our data? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **A1** | Path persistence over the bracket's range: unexpected volatility and day-scale trend raise intraday serial correlation; predictable high volatility lowers it. Hedgers who must trade with the move (short-gamma dealers, leveraged ETFs) create the trend; there is no counterparty to the coin's side | **filter / timing** (side-free) | (c) the 3R opening | a declared share of P-16's overnight marks; at 37.5 points the US hours have only 08:30-09:00 (D-281 (3)); on the 25-point US cell, 09:00-12:00 at R 2.5 | unknown on NQ; the sign follows the state (section 5.1) | the daily LeBaron effect attenuated; the intraday effect is "more pronounced" (Bianco, Corsi & Renò 2009 [abstract only]); day-scale momentum mixed (the review, lines 186-192) | harmless: slow states, read from bars stamped at or before t - 1 min | clean if release windows are excluded; s.8 unchanged (tier 3, E-013) | **needs a placebo-selection twin (Q-31)**; then yes, power from sessions |
| 2 | **A2** | Pre-announcement premium for "impact uncertainty", paid by investors who cut exposure before the release (Hu, Pan, Wang & Zhu 2022) | side + timing (long, overnight eve) | (c) the opening, if it waits for an eve; or every offer in the window (a) | ISM and GDP eves, about 24 a year (NFP is blocked, section 2 item 5); US hours only ISM's 08:30-08:55 tail, inside D-281 (3) | per-event Sharpe 0.13-0.14 on the S&P (Table 1); a few points at 3R if the trade resolves inside the window [estimate, section 5.3] | stable to 2018 in the paper; nothing after 2018 found (the review, lines 69-73; this search found none either) | harmless: known days ahead | ISM 09:00 CT and GDP 07:30 CT are not on Topstep's Tier 1 list (E-007's audit C1); an unresolved 3R opening is held into the release at the table's size (no time stops, D-212); disclose | **no**: about 1-4 % power on the development span, about a fifth with history back to 2009 [estimate] |
| 3 | **A3** | Month-end and threshold rebalancing by pension and balanced funds: they sell equities after equities outperform bonds, and buy after they underperform (Harvey, Mazzoleni & Melone 2026) | side (next day) | (a) the day's offers; (c) if an opening falls on it | threshold signal about 16 a year (state-based), calendar about 12 a year (month-end, last week); all hours | 16-17 bps next-day per 1-sd signal on the S&P (their section 1); modest at 3R [estimate] | working paper first posted 2025; significant "in the early 2000s" onward; no post-publication test | harmless: the signal is known at the prior close | clean | **no**: as for A2 |
| 4 | **A4** | Heightened uncertainty resolving after an unanticipated VIX spike (Hu et al. 2022, section 5: their "out-of-the-sample test") | side (long, next day) | (a) the day's offers | about 8-11 days a year (1994-2018); all hours | +36.6 / +42.7 bps next-day S&P index return at 2.5 / 3.0-point VIX jumps (their text, Table 10); on such days the 37.5-point bracket is small against the day's range, so the win-probability lift is smaller [estimate] | nothing after May 2018 found | harmless: known at the prior close | clean | **no**: fewer events still |
| (b) | **B1** | Volatility clustering, scheduled-news volatility and the intraday clock; no counterparty (a property of the clock) | routing / admission / sizing | (a) every trade; the opening's R and timing | every mark | **no win lift by construction**; it moves resolution | volatility clustering is a stylised fact of every era, not an anomaly | harmless: daily forecasts | clean if the "fastest" windows, which are release windows, are excluded | **not by E-008's line**: a supply/resolution lever, judged on the floors and the scorecard (the same open question as Q-25's) |

**Why A1 ranks first although its size is unknown.** It is the only (a) candidate that is used on every opening, the
place with the largest value of a win, and that can be measured with power. A2's effect is published and large enough
per use [estimate, section 5.3], but it cannot be judged on our data. The rule ranks expected value. A judgement the
family can never reach is worth nothing to the program, so A2 to A4 rank below A1.

**Rare calendar effects (the brief).** The review's turn of the month (rank 2, lines 116-163) and FOMC cycle (rank 4,
lines 213-236) reappear in the same way as A2: in value, because an opening can wait for the next window, but not in
power. Both have about one independent observation per month or per cycle, which is the reason in handoff 3.3.
Nothing in this search changes that.

## 5. The candidates in detail

### 5.1 A1: a side-free timing filter for the funded opening at R = 3 (rank 1)

**Mechanism and the other side.** The 3R coin bracket wins more than 1/4 when the next hours' moves persist and less
when they revert (section 3.1 (iii)). The literature links persistence to observable state.

- **Intraday LeBaron effect** (S&P 500 futures, every transaction 1993-2001, scales under 20 minutes; Bianco & Renò
  2009, *Quantitative Finance* [abstract only]):
  - serial correlation is related to realised volatility only through its *unexpected* part;
  - "the impact of predictable volatility is instead found to be negative (LeBaron effect)".

  Bianco, Corsi & Renò (2009, *PNAS*) [abstract only] extend the sample (to 2007 per a summary [secondary]) and report
  that after "a significant attenuation of the original effect over time" (LeBaron 1992's daily effect), a "similar but
  more pronounced effect" appears with intraday measures.
- **Day-scale persistence** (the scale of a 37.5/112.5-point bracket held for hours), covered by the review (lines
  165-192):
  - the first half-hour predicts the last, more strongly on volatile, high-volume and macro-news days (Gao, Han, Li &
    Zhou 2018);
  - the rest of the day predicts the last 30 minutes, much more strongly on negative dealer-gamma days (Baltussen, Da,
    Lammers & Martens 2021).

  Rosa (2022) found the always-on version fails out of sample and a threshold version does better. That is a filter,
  which is A1's form.
- **Dealer gamma.** Short-gamma dealers trade with the move and long-gamma dealers against it:
  - Barbon & Buraschi (2021, working paper [abstract only]): momentum with a negative gamma imbalance, reversal with a
    positive one, through limited liquidity;
  - Adams et al. (SSRN 5641974 [secondary]): higher net gamma "predicts a stronger reversal pattern in the intraday
    order flow of E-mini futures", and lower volatility for about an hour.

  Gamma data are S&P-only and would be a purchase (the review's out-row, line 283). A1 uses only bar-based proxies of
  the same states.
- **Who is on the other side.** No one takes the other side of a coin. The persistence is created by hedgers who must
  trade with the move. The bracket's asymmetry is what turns persistence into win probability.

**Stage 2's own related evidence (prior exposure, declared in any family):**

- **S2's state-gated coin** (`vendor/stage2/DECISIONS.md:596`, D-578 (4); `:599-600`, D-581, D-582) gated all of
  P-16's offers by:
  - the last 30 bars' range in thirds against the same mark's trailing 20 sessions;
  - "|c[t] - session open|" against its trailing median.

  The high-volatility cell came closest to P-16 and the trend cell was just below, judged on campaign growth over every
  trade. Those states and their campaign readings have been seen. A1's states should be defined anew from the
  literature, and S2's declared as seen.
- **The effect atlas** (`vendor/stage2/DECISIONS.md:152-153`, D-136, D-137): on 2012-2014, negative-gamma intraday
  momentum passed its check on NQ narrowly; gamma's link to rest-of-day volatility passed on both markets.
- **S1 and S3's follow-the-breakout lift** (`vendor/stage2/DECISIONS.md:598`, D-580; `:610`, D-592) is the *sided*
  reading of the same persistence. It was "broad and slow" and nearly as large at L = 5. It was real per trade in
  2024-2026 and failed the span guard. A1 is its side-free counterpart. A family can declare both readings, with the
  follow twin as a kill line for any sided cell (the red team's M-2 on family B).

**Latency and hand entry.** The states are slow, read from bars stamped at or before t - 1 min and from prior sessions.
The opening is a market order at t + 5 (P-16's rule). The intraday LeBaron evidence is at scales under 20 minutes. A1
assumes persistence at the bracket's scale of hours, which Gao and Baltussen support on the S&P and which nobody has
shown on NQ.

**Frequency.**

- All hours: the declared share of P-16's overnight marks (for example the top or bottom third of a state).
- US hours: at 37.5 points only the 08:30-09:00 marks, which sit inside D-281 (3). Exclude them, or put the question to
  the operator.
- For a US-hours user: the 25-point US cell's 09:00-12:00 marks at R 2.5 (D-642), where the same argument holds more
  weakly (R 2.5 against 3).

**Kind: a filter and timing rule, never a side.** The opening's side stays the coin's.

**Conduct.** Clean: no hedge, no news, and nothing concealed.

- Exclude every scheduled-release window, because a volatility-surprise state picks them. The exclusions are the BLS
  07:35 cut, FOMC days, Topstep's Tier 1 windows (E-007's audit C1) and the ISM and GDP minutes.
- The opening's size is already priced as tier 3 under Terms of Use s.8 (E-012 (1), E-013 (1)). A filter changes
  nothing there.
- The breakeven move is allowed as made (E-013 (2)).

**How large a lift would matter [illustration only, not an estimate].** Suppose a share q of offers have paths that
run the target's distance before reversing the stop's distance; the coin wins half of those. Suppose the rest behave
as a martingale and the coin wins 1/4. The coin's 3R win rate is then 1/4 + q/4. A state that raises q by 4 to 8 points
over the unfiltered offers adds 1 to 2 points of win probability on every opening. That is the order of the value map's
per-use bar at the openings' supply (handoff 2.7 quotes it from `u_value_map.csv` section `bar`). Nothing here says NQ
has such states. A clean zero is the likeliest outcome on the review's base rates (lines 326-346).

**What the family declaration needs** (for the drafter, not decided here):

- **Mechanism and sources:** as above.
- **Population:** P-16's offered marks (150 ticks) in 17:00-08:25 CT. 08:30-09:00 is excluded (D-281 (3)) unless the
  operator rules otherwise. Each mark's 3R walk on both sides is the unit; Stage 2 holds walks for every 5-minute mark
  (handoff 4.2).
- **States**, ex-ante and side-free, each a cell:
  - (s1) **unexpected volatility**: the range since the 17:00 CT open over its forecast (the same mark's median over
    the 20 prior sessions), in the top third (Bianco & Renò; Gao et al.);
  - (s2) **trend so far**: |c[t] - 17:00 open| over the session's forecast range, above a declared multiple (Gao;
    Baltussen). This differs from S2's trend state by its normaliser; disclose S2;
  - (s3) **low predictable volatility**: the session's forecast range (a HAR-type mean of the 1, 5 and 22 prior
    sessions' ranges, Corsi 2009) in the bottom third (LeBaron). Expect resolution trouble (S2's low and mid-volatility
    cells failed the worst-year line, D-582 (2)).
- **The rule:** a newly funded account takes its opening at the first offered mark in the state, waiting at most W
  sessions (fixed in the file), else at its next offer.
- **Supply, counted before any outcome:** the states' firing share by mark and year, and the openings' wait
  distribution under W.
- **The twin and statistic** (Q-31): in-state 3R coin net R minus a seeded placebo selection of the same firing share
  on the same population. Statistic: the side-symmetric mean, (long half + short half) / 2, with each half reported.
  Calibrated at the family's level by Q-16's method, adapted.
- **The value** at place (c), base p16: the lift at its bound x the value of a win at (c) x the openings a year, taken
  from the design's own journey. Measure the lift on the marks where openings actually fall (red team M-3; unknown 1)
  and set a declared bar (F-02's draft uses $500 a year).
- **Contract fit (CHARTER section 4):**
  - P-16's stop, 37.5 points, is above the 45-tick floor (`stop_band.csv`, Stage 2 D-271 (3));
  - realised risk at the opening's state at least 90 % within 10 % in whole micros;
  - at most 5 % of in-state 3R trades reach 15:10 CT, overall and in every year;
  - latency at least 5 minutes; one position per firm with five minutes flat; the BLS 07:35:00 cut and FOMC days out;
  - Topstep's Tier 1 windows; hand entry; the user's own accounts only.
- **Kill lines:**
  - K1: the bound is not above zero;
  - K2: resolution;
  - K3: the lift is carried by one side. A long-only lift is drift, not persistence: a low-volatility state raises
    mu / sigma^2, so in a rising market it lifts long 3R brackets by drift alone (section 3.1 (ii); the red team's
    C-1 on family B);
  - K4: opposite signs on 2020-2023 and 2024-2026 (S1's lesson, D-580);
  - K5: W binds for more than a declared share of openings.
- **Cells and count:** 3 (s1-s3) x one stop x R = 3. Optionally 3 more at R 2.5 on the 25-point US cell's 09:00-12:00
  marks, each counted. The family number is the next free one at declaration (E-007 (a), E-008).
- **Also required:** the journey scorecard beside every reading (E-014, E-015), and seeds fixed in the file.

### 5.2 B1: resolution forecasts for routing, admission and the opening's R (the (b) candidate)

**Mechanism.** Expected time to resolution = stop x target / variance rate (section 3.1 (i)). A forecast of the
variance over the next hours is therefore a forecast of resolution time. The predictors are robust and do not decay,
because they are features of the market clock, not mispricings:

- **Past realised volatility.** The HAR model's daily, weekly and monthly components (Corsi 2009, *J. Financial
  Econometrics*) became the standard benchmark. Hong, Nolte, Taylor & Zhao (2023, *J. Financial Econometrics*): price
  durations, the time for the price to move a fixed amount (exactly a bracket's question), forecast variance "more
  accurately than realized volatility and option-implied variance", alone and in combination [abstract and summary].
  Engle & Russell (1998) is the duration model behind them.
- **Implied volatility.** Stage 2's atlas R family found that "the previous day's VIX predicts the next day's realised
  variance beyond the previous day's, and range compression predicts calmer days" (`vendor/stage2/DECISIONS.md:152`,
  D-136; 2009-2014), recorded "as sizing and survival inputs, never edge".
- **Scheduled news and the clock.** Volatility is elevated for minutes and "slightly higher for several hours" after
  scheduled releases (Ederington & Lee 1993, *JF*, interest-rate and FX futures [abstract only]). The intraday U-shape
  (Andersen & Bollerslev 1997) is already used for scheduling and resolution (the review, line 290; D-383, D-525).

**What a rule could do with it** (each a cell):

- **(u1) Conditional admission.** D-525 (4) admits a mark only if its unresolved share is at most 5 % over the whole
  window (`vendor/stage2/DECISIONS.md:543`). A forecast-conditioned cutoff would admit, on a given day, the marks
  forecast to resolve:
  - later US-hours marks on fast days, which is where the 37.5-point US window fails resolution today
    (`vendor/stage2/DECISIONS.md:560`, D-542 (3); D-639's preamble);
  - the 3R opening only where it is forecast to resolve.
- **(u2) The opening's R by forecast:** 3R where the forecast says it resolves, else the table's cap. The table is not
  re-solved, as D-639 (2) did for its cap.
- **(u3) Routing the opening** to the earliest fast-forecast offer, so the firm's one slot is freed sooner.

**The interaction with A1.** By the LeBaron effect, fast because *predictably* volatile also means less persistent. A
B1 rule that seeks speed may cost win probability at 3R (s3 against u1). Declare both sides if the families share a
population.

**Kind:** routing, admission and sizing. There is no side and no win lift. **Frequency:** every mark.
**Latency:** daily forecasts, unaffected. **Conduct:** a "fastest window" rule selects release windows, so exclude them
(as in A1).

**What the family declaration needs:**

- The forecast, from bars only (HAR-type on prior sessions' same-window ranges) and, as a second cell, with the daily
  VXN or VIX close. Cboe publishes these; whether free history downloads need no sign-up is **[unverified]** and must be
  checked before relying on it.
- The uses u1 to u3: 2 forecasts x 2 uses (u1, u2) = 4 cells. u3 goes beside.
- **The pass line** is not a direction lift. It is the floors (every offered R resolving, at most 5 % flattened overall
  and every year; the long-run gate) plus the scorecard. That is the same question Q-25 raises for a same-trades lever,
  so the lead decides it once for both (Q-31).
- **Kill lines:** the forecast's calibration (predicted against realised unresolved share on the choice block); any
  year's unresolved share at an offered R above 5 %.
- Value is read on the scorecard, not the value map. Stage 2 found speed and bankroll barely move P (handoff 1.2), so
  the bar is low and the prior gain is small.

### 5.3 A2: the pre-ISM and pre-GDP overnight drift as the opening's timing and side (rank 2; covered by the review)

The mechanism, evidence and mapping are the review's rank 1 (lines 49-114). They are not repeated, with four changes.

- **NFP is not reachable.** On a BLS report day P-16 offers nothing before 07:35 CT on the trading-day clock, so the
  NFP eve's whole window (17:00 to 07:25 CT) is not offered (`resolved_coin.py:161-171`). Topstep's Tier 1 window
  blocks NQ opening trades from 07:25 to 07:35 CT on NFP days (E-007's audit C1, reading 13613539). The review's
  mapping (lines 83-95) does not reach this. **ISM** (released 10:00 ET, drift to 09:55 ET = 08:55 CT) and **GDP**
  (08:30 ET, drift to 08:25 ET = 07:25 CT) eves are offered. ISM's tail (08:30-08:55 CT) is inside D-281 (3).
- **The paper's per-event figures** (Hu et al. 2022, Table 1, S&P 500 futures, Sept 1994 to May 2018; the standard
  deviations are read from the PDF's extracted text, in the table's column order mean, t, standard deviation):
  - ISM: mean 9.14 bps (t 2.10), standard deviation 72.5 bps;
  - GDP: mean 7.46 bps (t 2.08), standard deviation 54.7 bps;
  - NFP: mean 10.10 bps, standard deviation 43.4 bps;
  - 12 announcement days a year each (their footnote 5).
- **The size at 3R [estimate].** By section 3.1 (ii), a 3R long opening entered at the window's start, with its target
  about one window standard deviation away and resolving inside the window, gains about 1/4 x (mu/sigma) x 1:
  - about 3 points of win probability for ISM or GDP (per-event Sharpe 0.13-0.14);
  - about 6 points for NFP, which is unreachable.

  This is of the order of the value map's per-use bar at that number of uses (handoff 2.7; `u_value_map.csv` section
  `bar`). Two cautions: the 112.5-point target's distance in NQ's overnight-window standard deviations is not known
  here, and the trades capture only part of the drift (the review's [estimate], lines 111-114).
- **Power [estimate].** Treat each eve as one observation with the paper's per-event Sharpe, about 0.13, and assume the
  trades capture all of it, which flatters the case. The expected t is 0.13 x sqrt(N):
  - judged block (2024 to 2026-07, about 60 ISM and GDP eves): t about 1.0;
  - the whole development span (about 157 eves): t about 1.6;
  - history from 2009 (about 420 eves): t about 2.7.

  At k = 11's one-sided level 0.05/132 (z about 3.37) the power is about 1 %, 4 % and 24 %. That matches the
  operator's reason for the drop (handoff 3.3). A2 does not come back unless the operator adds history.

**Conduct.** The ISM and GDP minutes are not on Topstep's Tier 1 list as E-007's audit read it. A 3R opening still open
at the release is held through it at the table's size, because D-212 allows no time stop. Whether that counts as
"maximum size into major news" (10305426) is unstated on Topstep's pages (the audit's U7). **UNVERIFIED; a
rules-verifier question, not a finding.**

### 5.4 A3: rebalancing pressure (rank 3; new since the review)

- **Source.** Harvey, Mazzoleni & Melone, "The Unintended Consequences of Rebalancing" (Dice Center WP 2025-01 /
  Fisher College WP 2025-03-001, version of 2026-01-14; SSRN 5122748). Read here: the abstract, the introduction and
  sections 1.2-1.3.
- **What they measure.** Daily S&P 500 and 10-year T-note futures, 1997-2023, a simulated 60/40 portfolio's weight
  deviations:
  - "When stocks are overweight, funds sell stocks and buy bonds, leading to a decrease in equity returns of 17 basis
    points over the next day";
  - more precisely, a one-standard-deviation rise in the Threshold (Calendar) signal is followed by about 16 (17) bps
    lower equity returns over the next trading day;
  - the pressure reverts within about two weeks;
  - the Calendar signal's predictability "peaks in the last four days of the month";
  - the Threshold signal fires about 16 times a year and the Calendar signal 12;
  - the predictive power "became significant in the early 2000s";
  - a front-running cross-asset portfolio has a Sharpe ratio above 1 over 1997-2023.
- **Mechanism and the other side.** Institutions' mechanical rebalancing, whose timing and direction are set by past
  relative returns. It is the review's turn of the month (Etula et al. 2020, lines 116-163), refined by a **state-based
  side**: the sign of the month's stock-against-bond performance.
- **Persistence.** It is a 2025 working paper, so there is no post-publication evidence.
- **Fit.**
  - It is a next-day side, known at the prior close, so the latency is harmless and it fits Topstep's 17:00-15:10 CT
    day.
  - How the next-day effect is spread across the hours is not in what was read.
  - The signal needs daily S&P and 10-year T-note futures returns. Neither is held locally (NQ only). Free daily proxies
    exist (index closes; Treasury yields) **[a construction question, unverified]**.
- **Frequency.** About 28 signal days a year, some overlapping. It is too rare for a direction family under E-008 for
  the same reason as A2 (section 3.3). Its calendar half is a rare calendar effect (dropped); its threshold half is not
  calendar.

### 5.5 A4: the day after a VIX spike (rank 4; Hu et al. 2022 section 5, not covered by the review)

- **What the paper says.** "At the close of trading day t, we define day t + 1 as a heightened VIX day, if [the change
  in VIX] is larger than a predetermined constant cutoff". On the S&P 500 index, September 1994 to May 2018:
  - "a cutoff value of 2.5% yields an average of 11.1 heightened VIX days per year";
  - a cutoff of 3.0 % yields 7.7 days a year;
  - "the corresponding next-day returns ... are 36.59 and 42.70 basis points, respectively, and both statistically
    significant";
  - with smoothing (eta = 0.30) at 3 %: 7.6 days a year and 48.04 bps (their section 5 and Table 10, read here);
  - on normal days, VIX build-ups do not predict the next day (Table 11).
- **Mechanism.** The same uncertainty-resolution premium as A2, triggered without a schedule.
- **Fit.** The side is known at the VIX close, before Topstep's 17:00 CT open, so latency is harmless. VXN is NQ's
  natural analogue **[untested in the paper]**.
- **Why rank 4.** About 10 events a year. On those days the 37.5-point bracket is small against the day's range, so the
  b / sigma factor in section 3.1 (ii) shrinks. Its power is lower than A2's. Nothing has been published after May 2018.

## 6. Considered and left out

New items only; the review's out-list (lines 274-295) stands and is not repeated.

| idea | why out |
|---|---|
| The **announcement-day premium** as a daily effect (Savor & Wilson 2013, *JFQA*; Ai, Bansal & Guo 2023, NBER w31923 survey [abstract only]) | Its days are CPI, PPI, employment and FOMC. P-16 offers no overnight mark on BLS days and no FOMC day at all. Ernst, Gilbert & Hrdlicka (2021 draft, AEA 2022 [abstract only]) show that its concentration in a few series, such as FOMC, "is likely even when those series are ex-ante identical to all others", which is a caution on the whole class |
| **Variance risk premium** as a direction (Bollerslev, Tauchen & Zhou 2009, *RFS*) | Its horizon is months to quarters. The implied per-session drift against intraday variance gives a negligible win-probability lift (section 3.1 (ii)) |
| **Overnight against intraday returns** (Lou, Polk & Skouras 2019, *JFE*) | A cross-sectional stock effect. For the index it reduces to the overnight drift, which its authors report gone since 2021 (the review, rank 5) |
| **NQ intraday momentum or reversal** (Yu, Rentzler & Wolf 2005, *JOIM* 3(3) [abstract only, via a summary]) | NQ-specific. "Last night's return" mostly reverses intraday, which is the gap or open reversal Stage 2 closed (D-112, D-123, D-125), and its window is inside D-281 (3) |
| **Round-number order clustering** (Osler 2003, *JF*) | A level effect. It belongs to F-02's `rn100` cells (E-017), not here |
| **Dealer gamma or 0DTE flows used directly** (Dim, Eraker & Vilkov 2024, SSRN 4692190 [abstract only]: high 0DTE gamma does not propagate past volatility; Adams et al. [secondary]) | S&P-only, and needs options data (a purchase). The review's out-row (line 283) and D-137 stand. A1 uses only bar proxies of the states the literature links to gamma |
| **The GDP release minute in P-16 itself** (an observation, not a candidate) | The BLS day file the engine reads lists CPI, PPI and Employment Situation days (E-007's audit C1). On GDP days (BEA, 07:30 CT) the 07:30 mark is offered and enters at the release bar's open, the exposure D-533 removed for BLS days. GDP is not on Topstep's Tier 1 list (audit C1), so under D-530 (1)'s reading this is disclosed, not tier 1. Recorded for the lead; whether the day file is BLS-only was read from the audit note and `atlas_local.py:14`, **not re-verified against the calendar file** |

## 7. Governance points the lead decides (not operator questions unless E-008's words do not reach)

1. **A side-free lever has no lift over the coin twin by construction** (section 3.1 (iv)). E-008's pass line ("direction
   on the design's own trades") cannot judge A1 or B1. Declare the twin for side-free filters (a seeded placebo
   selection of the same firing share on the same population) and the pass line for non-direction levers (the floors
   and the scorecard). Join this with Q-25's same-trades question so it is ruled once.
2. **D-281 (3)'s reserved call** covers any family whose population is P-16's 08:30-09:00 marks (the red team's M-1 on
   family B). A1 is declared on the overnight marks to stay outside it.
3. **The review's rank-1 mapping is incomplete** (section 5.3). This is a reading to record under the next decision
   row, as E-007 (g) recorded the audit's citation corrections.

## 8. What is unknown, and how it could be found

| # | unknown | how to find it (who) |
|---|---|---|
| 1 | At which marks, hours and day kinds P-14's and P-16's funded openings are routed. No vendored file holds it (`u_xfa_day_budget.csv` section `opening_trade` has no time column) | A supply count from the routed trades of the vendored replay, with no outcome read (a worker, light; proposed Q-30) |
| 2 | Whether the 3R coin's win rate on NQ varies by any ex-ante side-free state at all | A1's declared screen, after Q-30 and Q-31 (a worker) |
| 3 | Whether persistence at the bracket's scale (hours) follows the intraday LeBaron effect measured under 20 minutes | Nothing published at that scale on NQ was found. A1's cells s1 and s3 test both directions |
| 4 | The post-2018 status of Hu et al.'s non-FOMC drift and heightened-VIX day, and the post-2023 status of Harvey et al. | No replication found in this search. Only more history (QuantConnect from 2009, the operator's call) gives a test with any power |
| 5 | Whether holding a full-size opening through a non-Tier-1 release (ISM, GDP) is "maximum size into major news" (10305426) | UNVERIFIED; a rules-verifier reading of Topstep's pages (E-007's audit U7 left it open) |
| 6 | Whether Cboe's daily VIX and VXN history can be downloaded without a sign-up | Check Cboe's public data pages before any family relies on them (a scout); no account is to be opened |
| 7 | How Harvey et al.'s next-day effect falls across the hours, and how to build their signal from free data | Their Appendix B (not read here) and the full paper (a scout) |

## 9. Proposed TASK_QUEUE lines (for the lead; this note edits nothing)

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-30 | **Where the funded openings fall** (a supply count, no outcome): the marks, hours and day kinds at which P-14's and P-16's funded opening trades are routed, from the vendored replay's routed trades; the shares inside 08:30-09:00 CT (D-281 (3)) and on report days | wt-user | queued | Q-17 | light | 0 | -- |
| Q-31 | **The pass line for side-free levers** (the lead's row): a filter or timing rule that keeps the coin's side has zero lift over the coin twin by construction; declare its twin (a seeded placebo selection of the same firing share on the same population) and calibration (Q-16's method, adapted), and the floors-and-scorecard line for non-direction levers, together with Q-25's question | lead | queued | Q-16, Q-25 | light | 0 | -- |
| Q-32 | **Family O drafted: the funded opening's side-free timing filter at R = 3** (Q-28 candidate A1, `docs/research/mechanisms_2026-11-15.md` section 5.1): P-16's overnight marks; states s1-s3; the opening waiting at most W sessions; the side-symmetric statistic with each half reported; value at place (c) on the openings' own marks; S2, atlas O/R and S1/S3 declared as prior exposure; then red team and gatekeeper | wt-features | queued (after Q-29) | Q-30, Q-31 | light | 0 | -- |
| Q-33 | Family R drafted: resolution forecasts for mark admission and the opening's R (candidate B1, section 5.2) | wt-levels | queued (after Q-24) | Q-31 | light | 0 | -- |

Parked, not queued: A2-A4 (event-timed sides). They cannot be judged under E-008 on the development span (section 5.3).
Revisit only if the operator adds history.

## 10. Bibliography

Items the review already lists (Andersen & Bollerslev 1997; Baltussen et al. 2021; Etula et al. 2020; Gao et al. 2018;
Hu et al. 2022; Rosa 2022; Sullivan, Timmermann & White 2001; McLean & Pontiff 2016) are cited from its section 6
(lines 348-429). For **Hu et al. 2022**, this note also read Table 1's standard deviations, footnote 5, section 5 and
Tables 10-11 from the authors' copy (https://www.mit.edu/~zhuh/HuPanWangZhu_preannouncement.pdf, 2026-11-15).

- Adams, G., et al. (n.d.). Do S&P500 options increase market volatility? Evidence from 0DTEs. SSRN 5641974.
  **[secondary: Quantpedia, 2026-02-02, https://quantpedia.com/do-sp500-0dtes-options-increase-market-volatility/;
  co-authors and sample not confirmed]**
- Ai, H., Bansal, R., & Guo, H. (2023). Macroeconomic announcement premium. NBER Working Paper 31923.
  https://www.nber.org/papers/w31923 **[abstract only]**
- Barbon, A., & Buraschi, A. (2021, rev. 19 March). Gamma fragility (working paper). https://abarbon.com/papers/gamma-fragility
  **[abstract only; stock-level panel, period not stated on the page]**
- Bianco, S., & Renò, R. (2009). Unexpected volatility and intraday serial correlation. *Quantitative Finance*, 9(4),
  465-475. https://econpapers.repec.org/RePEc:taf:quantf:v:9:y:2009:i:4:p:465-475 ; preprint https://arxiv.org/abs/physics/0610023
  **[abstract only; SPX500 futures, all transactions 1993-2001, scales under 20 minutes]**
- Bianco, S., Corsi, F., & Renò, R. (2009). Intraday LeBaron effects. *PNAS*, 106(28), 11439-11443.
  https://doi.org/10.1073/pnas.0901165106 ; preprint https://arxiv.org/abs/0810.4912 **[abstract only]**
- Bollerslev, T., Tauchen, G., & Zhou, H. (2009). Expected stock returns and variance risk premia. *Review of Financial
  Studies*, 22(11), 4463-4492. **[cited for its horizon only; not re-read]**
- Corsi, F. (2009). A simple approximate long-memory model of realized volatility. *Journal of Financial Econometrics*,
  7(2), 174-196. https://econpapers.repec.org/RePEc:oup:jfinec:v:7:y:2009:i:2:p:174-196 **[abstract and summaries]**
- Dim, C., Eraker, B., & Vilkov, G. (2024). 0DTEs: Trading, gamma risk and volatility propagation. SSRN 4692190.
  **[abstract-level and secondary]**
- Ederington, L. H., & Lee, J. H. (1993). How markets process information: News releases and volatility. *Journal of
  Finance*, 48(4), 1161-1191. https://ideas.repec.org/a/bla/jfinan/v48y1993i4p1161-91.html **[abstract only;
  interest-rate and FX futures]**
- Engle, R. F., & Russell, J. R. (1998). Autoregressive conditional duration: A new model for irregularly spaced
  transaction data. *Econometrica*, 66(5), 1127-1162. **[standard reference; not re-read]**
- Ernst, R., Gilbert, T., & Hrdlicka, C. M. (2021 draft). More than 100% of the equity premium: How much is really earned
  on macroeconomic announcement days? AEA 2022 conference paper.
  https://aeaweb.org/conference/2022/preliminary/paper/ktNibY2Y **[abstract only]**
- Harvey, C. R., Mazzoleni, M. G., & Melone, A. (2026, 14 January version). The unintended consequences of rebalancing.
  Dice Center WP 2025-01; Fisher College of Business WP 2025-03-001; SSRN 5122748. Copy read:
  https://www.edhec.edu/sites/default/files/2026-03/Scientific%20paper.%20ssrn-5122748.pdf (abstract, introduction,
  sections 1.2-1.3, read 2026-11-15)
- Hong, S. Y., Nolte, I., Taylor, S. J., & Zhao, X. (2023). Volatility estimation and forecasts based on price
  durations. *Journal of Financial Econometrics*, 21(1), 106-144. https://eprints.lancs.ac.uk/id/eprint/151427
  **[abstract and summary]**
- Karlin, S., & Taylor, H. M. (1975). *A First Course in Stochastic Processes* (2nd ed.). Academic Press. Chapter 7:
  hitting probabilities and exit times of Brownian motion with drift (the textbook results used in section 3.1).
- LeBaron, B. (1992). Some relations between volatility and serial correlations in stock market returns. *Journal of
  Business*, 65(2), 199-219. https://ideas.repec.org/a/ucp/jnlbus/v65y1992i2p199-219.html **[abstract only; daily and
  weekly]**
- Lou, D., Polk, C., & Skouras, S. (2019). A tug of war: Overnight versus intraday expected returns. *Journal of
  Financial Economics*, 134(1), 192-213. **[cited for its scope only; not re-read]**
- Osler, C. L. (2003). Currency orders and exchange rate dynamics: An explanation for the predictive success of
  technical analysis. *Journal of Finance*, 58(5), 1791-1819. **[cited for its scope only; not re-read]**
- Savor, P., & Wilson, M. (2013). How much do investors care about macroeconomic risk? Evidence from scheduled economic
  announcements. *Journal of Financial and Quantitative Analysis*, 48(2), 343-375. **[cited for its scope only; not
  re-read]**
- Yu, S., Rentzler, J., & Wolf, A. (2005). NASDAQ-100 index futures: Intraday momentum or reversal? *Journal of
  Investment Management*, 3(3). https://www.joim.com/nasdaq-100-index-futures-intraday-momentum-reversal
  **[abstract only, via a search summary; sample period not seen]**

Repository sources cited:

- `CHARTER.md` sections 2-4; `DECISIONS.md` E-007, E-008, E-012, E-013, E-016, E-017;
  `docs/audits/phase0/E_rules_currency.md` (C1, C2, U7);
  `docs/reviews/DRAFT_F-B_multifeature_2026-11-15.md` (C-1, M-1, M-2, M-3).
- `vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` sections 1.2, 2.5, 2.7, 3.2-3.4.
- `vendor/stage2/DECISIONS.md` lines 152-153, 231, 300, 402, 543, 548, 551, 560, 596, 598-600, 610, 636, 657, 660,
  670, 686-687.
- `vendor/stage2/propedge/research/resolved_coin.py:161-171, 288-311`; `vendor/stage2/propedge/research/atlas_local.py:13-15`;
  `vendor/stage2/propedge/outcomes/collect_core.py:10-16`.
- `vendor/stage2/results/u_xfa_day_budget.csv` (section and measure names only) and `u_value_map.csv` (section names
  only); no value was read from either.
