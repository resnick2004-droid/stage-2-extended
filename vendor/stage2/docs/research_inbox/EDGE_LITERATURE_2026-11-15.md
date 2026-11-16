# Edge literature review: published effects that might still give NQ a real direction (2026-11-15)

> Research only. Nothing was run, no result file was read past what is named, no data past 2026-07-16 was touched,
> nothing was bought. Written for the coordinator to turn into model cards. Every literature figure below is the
> **paper's own number on the paper's own sample** (mostly the S&P 500). None of it is a result of this repository. A
> few back-of-envelope translations into NQ points are marked **[estimate]**; none is a result, and none may be copied
> into a card as one. A claim I could not confirm from a primary or near-primary source is marked **[unverified]**.
> Numbers from this repository's own result files are not repeated here. The file is named instead (CLAUDE.md:
> result numbers are never typed into documents).

## 1. In plain language

Most published "intraday patterns" are small, and many fade once they are published. This repository has already
tested the obvious ones (breakouts, the opening range, fading the open, gap fills, most bar patterns) and found that
none of them, at a five-minute delay, picks a better side than a coin. The research that holds up best describes
**when** index futures tend to rise, not chart patterns, and the reasons are structural:
- buyers are paid for holding risk overnight before big economic reports;
- pension funds and other institutions sell before month-end and buy back after it;
- options dealers and leveraged funds trade in the direction of the day's move near the close.

Each of these can be tested here as a **side rule on the existing coin** (P-16 keeps its entries, brackets and
supply; only the side changes), which is the format the search programme already uses (S1, S3, S4). Gating trades,
by contrast, cut supply faster than it helped (S2, D-582). The best-supported candidate is the **overnight drift before
the jobs (NFP), ISM and GDP reports**. It still worked in the authors' latest sub-period (2012-2018), it can be held
inside one Topstep trading day, and it ends *before* the release, so it is the opposite of news trading. Second is
the **turn-of-the-month** pattern. Third is **late-day momentum**, which has already failed here in its plain form;
only a thresholded form on NQ's recent years is untested. The overnight European-open drift, the strongest-documented
effect of all, has been reported by its own authors as **gone since 2021, on NQ too**. Expect most of these to fail.
The honest base rate is that roughly half of a published anomaly's return disappears after publication, and that
calendar and intraday-rule effects mostly do not survive a correction for how many were tried (§5). Each screen is
cheap, though, and none needs a purchase.

## 2. Ranked shortlist

The ranking puts the likelihood that the effect is real and still alive first, then fit to this contract (supply,
resolution, latency, conduct), then cost to screen. All five can be written as side rules on P-16's offers, so supply
and costs are the coin's own (the round-turn cost in points, D-431). What a candidate must show is a **lift over its
own coin twin** on the same offers (the A4/S-programme statistic, D-550, D-578), then the campaign guards.

A cross-cutting note on statistical power **[estimate]**: these effects are event-based (about 36 to 48 events a
year). On the local NQ bars (2020-01-02 to 2026-07-16) a real effect of the published size gives a t-statistic of
about 2, well below what a batch late in programme S must clear (batch k spends 0.05 / (k (k + 1)); the fifth batch
spends 0.17 %). QuantConnect's NQ and ES minute history from 2009 (D-237; `config/windows.yaml` notes QC development
reads back to 2009) roughly doubles the sample, at no cost. **The coordinator should declare the span before
declaring the menu.** On six years alone, a negative screen of an event effect is uninformative, not a refutation.

---

### Rank 1. Pre-announcement drift before NFP, ISM and GDP: long overnight, flat before the release

**Plain-language why it might work.** Before a report that can move the whole market, nobody knows how hard it will
hit. Buyers who hold index futures through that uncertainty want to be paid for it, and on average they are: the
market tends to rise overnight before the jobs report and before two other big releases, and then moves
unpredictably once the number is out. The trade holds the overnight rise and is out before the number. You are paid
for carrying a known, scheduled risk, not for out-guessing anyone. Risk premia like this are harder to arbitrage away
than mispricings, because someone has to carry the risk.

- **Mechanism (who is on the other side).** A risk premium for "impact uncertainty", the uncertainty about how much
  the release will move the market, which builds up and resolves just before the release (Hu, Pan, Wang & Zhu 2022,
  JFE, two-risk model). The counterparty is any investor who reduces exposure ahead of the release, a hedging demand,
  and pays the premium to the buyer who holds through it.
- **Evidence.** Hu, Pan, Wang & Zhu (2022), S&P 500 index futures, September 1994 to May 2018. The return from the
  previous day's 4 pm ET close to 5 minutes before the release averages **10.1 bps for NFP (t 3.63), 9.1 bps for ISM
  (t 2.10) and 7.5 bps for GDP (t 2.08)**, against 0.69 bps for the same overnight window on non-announcement days
  (their Table 1). The NFP and GDP drift is realised from the 4 pm close to 8:25 am ET; the ISM drift runs to 9:55 am
  ET. Post-announcement returns are small and insignificant, with large variance. **CPI, PPI, claims, housing starts
  and the sentiment index show no pre-announcement drift** (Table 1: CPI and PPI slightly negative, insignificant).
  The per-event standard deviation for NFP is about 43 bps, so the per-event Sharpe ratio is modest.
- **Out-of-sample and decay.** Within the paper, the non-FOMC drift is **stable across 1994-2000, 2001-2011 and
  2012-2018**: 6.98 bps per event, t 2.27, in 2012-2018 (their Table 2). The FOMC part, by contrast, decayed (rank-out
  list). **Nothing after May 2018 has been published that I could find [unverified: no post-2018 replication
  located]**, and the paper is on the S&P 500, not NQ **[NQ unverified]**. The working paper circulated from 2019
  (NBER w25817), so 2019-2026 is post-publication.
- **Cost and slippage.** One round turn per event at the coin's cost. A bracket entered at night in a calm book sees
  slippage near the coin's assumed level; the risk is an exit near the release minute, which the rule avoids by
  construction.
- **Signals per session.** About 36 events a year (12 NFP, 12 ISM manufacturing, about 12 GDP advance, second and
  third estimates, fewer where they coincide), so about one session in seven. Within the window the coin's own offers
  continue (Asia and London are offered, D-525). The rule only sets their side long. **It must be paired with the
  coin's normal sessions; it is an overlay, not a stand-alone supply.**
- **The published rule.** Long the S&P 500 future from the 4 pm ET close of the day before to 5 minutes before the
  release (8:25 am ET for NFP and GDP; 9:55 am ET for ISM). No stop, no filter.
- **Mapping to NQ 1-min OHLC at L = 5.**
  - The Topstep trading day opens at 17:00 CT, so the window is 17:00 CT on the eve to 07:25 CT (NFP, GDP) or
    08:55 CT (ISM). That is one trading day (D-176 keys a 17:00 CT entry to the next day). Missing the 15:00-16:00 CT
    hour of the paper's window is a small, declared deviation.
  - The side is known days in advance (a calendar), so latency does not bite: P-16's offers inside the window take
    the long side.
  - **Exit:** any position still open at 5 minutes before the release is closed. *This is a time stop, which D-212's
    resolution rule (`time_stop: none`) forbids.* The card needs a decision row that either (a) allows a pre-release
    exit as a news-rule exit, or (b) keeps the bracket open through the release at the coin's size. (b) is not tier-1
    (Topstep's wording is maximum size into major news, 10305426; the gatekeeper's ruling in D-530), but it adds the
    post-release variance, which has zero mean. The coordinator decides; it is not an operator question.
  - The news-safe coin `_nr` already shapes offers around releases (D-525, D-530). The card states how the two rules
    interact.
- **Conduct tier.** Tier 1: clean (no hedge, no news spike, wide bracket, exits before the release). Tiers 2 and 3:
  unaffected.
- **Data beyond the NQ bars.** Release calendars, all free:
  - NFP: already packaged in the repository (memory `reference-bls-release-calendar`: BLS 08:30 ET dates 2009-2025;
    2026 from bls.gov).
  - ISM manufacturing (first business day, 10:00 ET): from ismworld.org archives **[historical dates unverified;
    usually the first business day]**.
  - GDP: from the BEA release schedule archive.
  - No purchase needed. ES (the paper's instrument) would need the ES bars (§7).
- **What kills it at a cheap screen.** On NQ (QC 2009-2019 plus local 2020-2026, the span declared first):
  1. The mean NQ return in the declared window on event days is not above the same window on non-event days (the
     paper's own benchmark), one-sided at the batch's level.
  2. P-16's offers inside the windows, long-sided, show no lift over their coin twin at any offered R.
  3. 2019-2026 alone (post-publication) has the wrong sign.

  **[estimate]** At NQ near 20,000 the paper's 7-10 bps is a mean drift of order 15-25 points over the whole window,
  against a per-event spread several times larger. A 37.5-point 1:1 bracket captures only part of it, so expect a
  per-trade lift of a few hundredths of R, around the size of the round-turn cost. A wider stop captures more of the
  drift per R.

### Rank 2. Turn of the month: long-side bias from the institutions' month-end cash cycle

**Plain-language why it might work.** Pension funds must pay pensioners on the last day of the month and many funds
pay out around then, so they sell shares a few days before month-end to raise the cash, and new money arrives and is
invested in the first days of the next month. That forced selling pushes prices down a little, and prices recover
over the following days. The sellers are not trading on a view; they are paying for the cash. The pattern is very old
and found in most countries. The real risk is that it has weakened or moved, because US settlement was shortened
twice (2017 and 2024), which changes which day the selling must happen.

- **Mechanism.** Month-end payment needs: pensions, dividends and fund redemptions. Etula, Rinne, Suominen &
  Vaittinen (2020, RFS) document a "selling pressure" period T-8 to T-4 (T = last trading day), set by the 3-day
  settlement convention (sell by the close of T-4 to have cash on T), then a "positive reversal" T-3 to T-1 and
  "buying pressure" T to T+3. Over 2003-2013 the positive-reversal periods carried 103 % cumulative excess return, 73 %
  of the US market's, and the selling-pressure periods -31 % (their §1). The counterparty is the liquidity-driven
  seller.
- **Evidence.**
  - McConnell & Xu (2008, FAJ): CRSP 1926-2005, the value-weighted market averages 0.15 % a day over the four-day
    turn of the month (last day plus the first three) against about -0.001 % on the other days; found in 31 of 35
    countries.
  - Carchano & Pardo (2011 working paper, 188 calendar effects in S&P 500, DAX and Nikkei futures, 1991-2008): the
    turn-of-month long in S&P 500 futures is the only calendar rule that stays net-profitable in both sub-periods at
    0.05 % round-trip costs **[from secondary summaries; the paper's text not read]**.
- **Out-of-sample and decay.** Mixed.
  - Maberly & Waggoner (2000, Atlanta Fed WP) find it disappeared in S&P 500 futures after 1990.
  - Etula et al. report the end-of-month part becoming *more* pronounced to 2013.
  - Sullivan, Timmermann & White (2001) show that calendar effects as a class lose significance once the universe of
    calendar rules searched is accounted for.
  - Post-2013 evidence is practitioner-only **[unverified]**.
  - This repository's own 2009-2011 screen half (H11, `results/effect_atlas.csv`) showed NQ's last and first days of
    the month with the opposite sign and not significant, on very few observations.
  - **Settlement shortened to T+2 in 2017 [effective date 2017-09-05 from memory, unverified here] and to T+1 on
    2024-05-28 (SEC; law-firm summaries).** The mechanism predicts the selling deadline moved from T-4 to T-3 and then
    T-2. A mechanism-faithful rule shifts its window with the settlement cycle; the paper's fixed window does not.
    Declare both, and count both.
- **Cost and slippage.** The coin's (side rule only).
- **Signals per session.** The side rule covers about 7 of roughly 21 sessions a month (T-3 to T+3) and leaves the
  coin's supply unchanged.
- **The published rule.** McConnell-Xu: long from the close of T-1 to the close of T+3. Etula et al.: the
  positive-reversal window T-3 to T-1, and buying pressure T to T+3.
- **Mapping to NQ at L = 5.** The side is known from the calendar. P-16's offers on the declared days take the long
  side; other days stay coin-sided. Latency is irrelevant.
- **Conduct tier.** Clean.
- **Data.** Trading calendar only (the local bars carry it).
- **What kills it.** No lift over the coin twin on declared-window offers at any offered R. A sign that holds only
  before 2017-09 (the settlement change) or only in one era (the S1 lesson, D-580). Daily returns on the declared days
  no higher than on other days. And the honest prior issue: if the equity premium is earned overnight around the
  European open (rank 5), the RTH offers may never see it, so read the lift by session window (Asia, London, US) and
  declare that cut beforehand.

### Rank 3. Late-day momentum: the day's move predicts the last half hour, thresholded, on NQ 2020-2026

**Plain-language why it might work.** Options dealers who are short options and funds that promise two or three
times the index's daily move (TQQQ on the Nasdaq-100 is one of the largest) must buy after the market has risen and
sell after it has fallen, mostly near the close. That forced trading pushes the last half hour in the direction the
day has already gone. It has been found in over 60 futures markets and 16 countries. **It has already failed here in
its plain form** (§4). What remains is a version that trades only on days with a large move, which one author found
is where the effect lives, and on NQ's recent years, which have not been tested this way.

- **Mechanism.** Hedging demand. Short-gamma option dealers and leveraged-ETF rebalancing trade with the move
  (Baltussen, Da, Lammers & Martens 2021, JFE; Cheng & Madhavan 2009, JOIM). The counterparty is the forced hedger.
  Contested: Ivanov & Lenkey (2018, JFM) find leveraged-ETF flows offset most of the rebalancing, so the late-day
  effect is economically insignificant (US equity ETFs 2006-2014). Lenkey's 2024 survey finds the associations
  statistically significant but economically small and methodologically weak.
- **Evidence.**
  - Gao, Han, Li & Zhou (2018, JFE): SPY 1993-2013. The first half-hour return (from the prior close) predicts the
    last half-hour return, out of sample too, and more strongly on volatile, high-volume, recession and macro-news
    days.
  - Baltussen et al. (2021): over 60 futures, 1974-2020. The rest-of-day return predicts the last 30 minutes, much
    stronger on negative net-gamma days (S&P 500 options) and absent on positive ones.
  - Li, Sakkas & Urquhart (2022, JFM): 16 developed markets, significant in and out of sample in most.
- **Out-of-sample and decay.**
  - Rosa (2022, J Futures Markets): the overnight-to-last-half-hour version's predictability **disappears out of
    sample**; a Markov-switching reading says it depends on signal strength, and a threshold version beats the
    always-on one.
  - In the 0DTE era dealers' net gamma is usually positive (memory: options-information memo; Cboe figures cited
    there), which damps the effect.
  - Gamma conditioning is S&P 500-only (no NDX paper, same memo).
- **Cost and slippage.** The killer here so far. A 30-minute hold earns too little against a round turn (the ES first
  look, `results/shortlist_rod_momentum.csv`; D-137's translation put NQ near zero net). A 37.5-point bracket offered
  at about 14:25 CT has about 45 minutes to the 15:10 CT flatten, so **D-212's resolution line (at most 5 %
  unresolved) is the first kill**, before direction.
- **Signals per session.** At most one (late afternoon), on threshold days only.
- **The published rule.** Gao et al.: at 3:30 pm ET take the sign of the return from the prior close to 10:00 am ET
  (or add the 12th half-hour) and hold to 4 pm ET. Baltussen et al.: the sign of the return from the prior close to
  3:30 pm ET, held to the close.
- **Mapping to NQ at L = 5.** Decision mark 14:25 CT, reading bars closed by 14:20 CT. Side = sign of the move from
  the prior 15:00 CT settlement (or from 08:30 CT) to the mark. Trade only when |move| exceeds a declared multiple of
  its trailing average at that time of day (the threshold, Rosa; the noise-band idea of Zarattini, Aziz & Barbon
  2024, but as a side rule, not IM2's exits). Applied to P-16's offers in 14:25-15:10 CT. The latency is harmless
  because the signal is hours old.
- **Conduct tier.** Clean (not near a release; the 15:00 CT settlement is not a news event).
- **Data.** None beyond the bars. The mechanism-faithful version (Baltussen et al. eq. 16) needs daily TQQQ/SQQQ/QLD
  AUM and NAV: free on issuer sites **[history depth unverified]**. That is D-137's "new data source", not a purchase.
- **What kills it.** The 14:25 CT offers do not resolve inside the flatten at the coin's stop. No lift over the coin
  twin on threshold days. The lift is present only in 2024-2026 (S1 found exactly this era split for 15-minute
  momentum, D-580).

### Rank 4. The FOMC cycle: long-side bias in even weeks after a Fed meeting

**Plain-language why it might work.** A Fed study found that since 1994 the US stock market earned its entire
premium in alternating weeks counted from each Fed meeting, apparently because Fed information reaches the market on
a biweekly rhythm and the Fed tends to support the market after falls. If it is real, setting the coin's side long in
those weeks adds a small, steady tilt. But it has not been tested since the paper, and half of it is a bounce after
declines.

- **Mechanism.** Information flow from the Fed and a "Fed put": Fed funds futures rates decline on average in even
  weeks, and about half the even-week return is mean reversion after stock market declines (Cieslak, Morse &
  Vissing-Jorgensen 2019, JF). The counterparty is investors who sold into declines before the policy response.
- **Evidence.** 1994-2016: the equity premium is earned entirely in weeks 0, 2, 4 and 6 of the FOMC cycle. It holds in
  three sub-periods and outside the US (their abstract).
- **Out-of-sample and decay.** **None located after 2016 [unverified].** The same authors note that Lucca-Moench's
  pre-FOMC result is not significant in post-publication data (rank-out list), which is a warning for the whole
  family.
- **Cost.** The coin's. **Signals:** about half of all sessions take the long side; supply unchanged.
- **The published rule.** Week t counted from the FOMC announcement day (day 0 to 4 = week 0). Long in weeks 0, 2, 4
  and 6; flat otherwise.
- **Mapping to NQ.** Calendar side rule on P-16's offers; latency irrelevant.
- **Conduct.** Clean (do not trade the 13:00 CT statement minute; the `_nr` coin already avoids releases).
- **Data.** FOMC dates, free (federalreserve.gov).
- **What kills it.** No even-week lift over the coin twin. The lift sits only in a post-decline state, which is then
  a different rule; S2's state gates already failed (D-582).

### Rank 5. The overnight drift at the European open: long 01:00-02:00 CT after a sell-off close (expected dead)

**Plain-language why it might work, and why it probably no longer does.** When US investors sell hard into the
close, market makers are left holding the shares overnight and are paid for it when European traders arrive and take
the other side, around 2 a.m. New York time. For twenty years this one hour carried most of the S&P's return. The
same authors reported in July 2026 that it has been **flat since 2021, in NQ as well**, because closing order
imbalances got smaller. It is listed only because the mechanism is clear, and the local bars can confirm or refute
the authors' post-publication reading for free.

- **Mechanism.** Dealer inventory risk from end-of-day order imbalance, resolved at the European open (Boyarchenko,
  Larsen & Whelan 2023, RFS). Bondarenko & Muravyev (2023, JFQA) read it as uncertainty resolving as European
  investors process the night's information.
- **Evidence.**
  - Boyarchenko et al.: E-mini S&P 1998-2020, the 2-3 am ET hour about 3.6-3.7 % a year, more than 60 % of the
    contract's close-to-close return, and the same pattern in NQ and YM. It is larger after negative closing
    imbalance (sell-offs).
  - Bondarenko & Muravyev: about four hours around the European open carry the entire average return, Sharpe about
    1.6, after costs; the other 20 hours earn a noisy zero **[sample 2004-2018 per secondary summaries]**.
- **Out-of-sample and decay.** **Boyarchenko, Larsen & Whelan (Liberty Street Economics, 2026-07-01): 2021-2025 the
  window averages close to zero, the same in NQ and YM. The imbalance-to-return link "has broken down" (the
  dispersion of closing imbalance roughly halved). NightShares' overnight ETFs launched June 2022 and closed about 14
  months later.**
- **Cost.** The coin's. **Signals:** one window a session (about 01:00-02:00 CT); the conditional form only after a
  declared sell-off close.
- **The published rule.** Long E-mini 2:00-3:00 am ET (01:00-02:00 CT), unconditionally or after a negative closing
  imbalance.
- **Mapping.** The side is known by the 15:00 CT close (read from the 14:00-15:00 CT bars as a sign and size of the
  late-day move, an OHLC proxy for imbalance; the real measure needs signed volume, which we lack). It applies to
  P-16's 01:00-02:00 CT offers. This is a night trade for a manual operator, though the operator said any hours suit
  (D-266).
- **Conduct.** Clean. **Data.** Bars only (the imbalance proxy is OHLC).
- **What kills it.** The 2021-2026 window mean on local NQ is not above zero (the authors already report this). No
  conditional lift over the coin twin.

---

## 3. Out, with the reason

| idea | why out |
|---|---|
| **Pre-FOMC drift** (Lucca & Moench 2015, JF: S&P 500 up about 49 bps in the 24 h before scheduled FOMC, 1994-2011) | **Decayed:** Kurov, Wolfe & Gilbert (2021, FRL) find it largely gone since 2016; Hu et al. (2022) find FOMC's pre-announcement return insignificant in 2012-2018. Eight events a year; the 24 h window crosses the 15:10 CT flatten. (Lucca-Moench's instrument, index vs futures, **[unverified]**.) |
| **Post-announcement drift / trading the release** (CPI, NFP at 07:30 CT) | Prices adjust to surprises within minutes (Andersen, Bollerslev, Diebold & Vega 2003, AER, on FX; the reaction is a conditional mean *jump*). At 5 minutes' latency the move is gone, and entering at the release is the tier-1 news pattern. CPI and PPI also show no pre-release drift (Hu et al. Table 1). |
| **30-minute pre-release drift direction** (Kurov et al. 2019) | Tested here as atlas family K: no survivor, family closed (D-164, D-166). |
| **MOC / closing-auction imbalance** (Bogousslavsky & Muravyev 2023, JFM: auction-price deviation reverses overnight, partly within 30 minutes) | Stock-level; needs Nasdaq/NYSE imbalance feeds (a purchase); the 14:50-15:00 CT imbalance window plus 5 minutes' latency leaves no room before the 15:10 CT flatten; the reversal lands after the flatten. |
| **Leveraged-ETF rebalancing as its own trade** (Cheng & Madhavan 2009) | Contested (Ivanov & Lenkey 2018; Lenkey 2024 survey); timing identical to rank 3, so it is rank 3's mechanism-faithful variant, not a separate card. |
| **Dealer gamma / 0DTE / pinning** | S&P 500-only literature; dealers' net gamma usually positive now; atlas O01 closed (D-137); memory: options-information memo. |
| **Opening-gap reversal / overreaction** (Fung, Mok & Lam 2000; Grant, Wolf & Yu 2005) | Tested here and closed (D-112: no effect on ES; the paper's size absent). |
| **Reversion to the open / fair value** | Closed on ES and NQ (D-121, D-123, D-125): NQ tends to keep moving away from the open. |
| **Opening-range breakout** (incl. Zarattini & Aziz 2023 QQQ, a vendor working paper with zero slippage assumed) | Closed (D-275); ORB variants also on A4's menu (D-550). |
| **Noise-band intraday momentum as a strategy with trailing exits** (Zarattini, Aziz & Barbon 2024, SPY, vendor/SFI working paper) | IM2 used its entry unchanged and failed before costs on ES, CL, 6E, NG (D-210). Its side as a threshold is folded into rank 3. |
| **Daily time-series momentum as the coin's side** (Moskowitz, Ooi & Pedersen 2012) | Weak for single assets: Huang, Li, Wang & Zhou (2020, JFE), 47 of 55 assets below t 1.65; Kim, Tse & Wald (2016) show it is mostly volatility scaling, and unscaled ≈ buy-and-hold. For one equity index it reduces to a long bias, and the intraday hours earn a noisy zero (Bondarenko & Muravyev 2023), so RTH offers would gain nothing. Cheap to add to a batch as a control, but not a candidate. |
| **Volatility-managed sizing as a source of edge** (Moreira & Muir 2017) | Fails out of sample for most strategies (Cederburg, O'Doherty, Wang & Yan 2020, JFE). Volatility stays a sizing/resolution input (atlas R family, D-136), never direction. |
| **Intraday volatility/volume seasonality** (Andersen & Bollerslev 1997) | Real but carries no direction; already used for scheduling and resolution (D-383, D-525). |
| **Cross-sectional intraday periodicity** (Heston, Korajczyk & Sadka 2010) | A stock cross-section effect, not an index direction. |
| **Weekday, pre-holiday, options-expiry, roll-week effects** | Tested as H10-H13 (no survivor, D-136); calendar effects as a class do not survive data-snooping correction (Sullivan, Timmermann & White 2001); pre-holiday supply is about nine days a year. |
| **Generic intraday technical rules** | 7,846 rules on 5-minute SPY, none profitable after data snooping (Marshall, Cahan & Cahan 2008); technical profits in futures faded after the early 1990s (Park & Irwin 2007). The repository's A1-A4 and S1-S4 found the same. |
| **Order-flow, order-book, tick-imbalance signals** | Need tick or depth data (not held; a purchase), sub-minute horizons, and a 5-minute manual latency kills them. |
| **Cross-firm hedge pairs** | Tier 1 (cross-account hedging); `hypothetical_hedge` only (D-452). |

## 4. Already tested here (one line each)

- **ORB5, 08:30 CT opening-range breakout (D-275):** all four kill lines; no edge net of costs in any form.
- **Fixed-time 20-point brackets, T23-D20 / P-07 (D-423):** the entry carries no information; costs beat the contract's
  shape; route closed.
- **08:30 bracket direction rule (D-372):** no pre-08:30 measure tells the side of the open's first move on both spans.
- **Signal atlas A1-A4 (D-477 to D-558):** 15 OHLC pattern families, follow and fade; P-11 and P-13 passed on
  development but their money was the schedule and FV3-C's design, not the signal; A4's schedule control: "gains are
  schedule, not direction"; the coin (P-16) stands.
- **Program S1, sided coin on 15 bar rules (D-580):** 15-minute momentum and the 5-minute breakout lift is real per
  trade but only in 2024-2026; fails the span guard.
- **S2, state-gated coin (D-582):** gating removes supply faster than it improves the kept offers; no cell beats P-16.
- **S3, new event kinds (D-588 to D-592):** `lnbar1x4_follow` passed at L = 0 and failed at the operator's
  5-minute latency.
- **S4, Point & Figure direction (D-616):** no rule survives stage 1.
- **PFA, the catapult's natural bracket (D-617):** only the 2.5-point box survives the fit lines, and it loses money per
  trade.
- **Earlier, beside the brief's list:**
  - Effect atlas 2009-2014: first-30 to rest-of-day, first-30 to last-30, settlement drift and momentum, gap fills,
    weekday, month-end, expiry, roll, ES-leads; nothing tradable (D-126, D-136).
  - Gamma-conditioned last-30 (O01): not pursued (D-137).
  - Pre-release drift, family K: no survivor (D-166).
  - Gap reversal on ES: closed (D-112).
  - Open reversion on ES and NQ: closed (D-123, D-125).
  - IM2 noise-band momentum on ES/CL/6E/NG: failed before costs (D-210).
  - Plain last-30 momentum first look: right sign on ES, smaller than its cost; NQ weaker
    (`docs/candidates/SHORTLIST.md`, `results/shortlist_rod_momentum.csv`).
- **The options-information memo (PARKING_LOT 2026-10-11):** gamma literature S&P 500-only, nothing bought.

## 5. The honest base rate

- **Post-publication decay.** Across 97 published cross-sectional predictors, returns fall 26 % out of sample and 58 %
  after publication (McLean & Pontiff 2016, JF). Declines are larger for the predictors with larger in-sample returns.
- **Replication.** Of 452 anomalies, 65 % fail a t of 1.96 once microcaps are controlled, and 82 % fail the
  multiple-testing hurdle of 2.78 (Hou, Xue & Zhang 2020, RFS). Harvey, Liu & Zhu (2016, RFS) argue a new factor needs
  t > 3.0 and that most claimed findings are likely false.
- **Calendar effects.** Highly significant one at a time, not significant once the universe of calendar rules searched
  is counted (Sullivan, Timmermann & White 2001).
- **Intraday technical rules.** None of 7,846 profitable after data snooping on 5-minute SPY (Marshall, Cahan & Cahan
  2008). Technical profits in futures faded after the early 1990s (Park & Irwin 2007).
- **Specific to this shortlist.**
  - Two of the five strongest-documented index-timing effects are reported dead by later work: pre-FOMC (Kurov et al.
    2021) and the European-open drift (Boyarchenko et al. 2026).
  - One failed its out-of-sample test in a journal: overnight-to-last-half-hour momentum (Rosa 2022).
  - The pre-NFP/ISM/GDP drift held through 2018 in its own paper, with no later test found.
- **This repository's own record.** The 2009-2014 effect atlas (174 declared tests, D-126 and its additions) produced
  nothing tradable in direction. A1-A4 and S1-S4 found per-trade lifts that did not survive era splits or latency.
- **Reading.** The prior that any one of these five survives a properly corrected screen on NQ, then a campaign
  guard, then confirmation, is low: well under one in two each, and plausibly about one in five for the best of them
  **[judgement, not a computed figure]**. A documented negative remains a valid close (exit B).

## 6. Bibliography

- Andersen, T. G., & Bollerslev, T. (1997). Intraday periodicity and volatility persistence in financial markets.
  *Journal of Empirical Finance*, 4(2-3), 115-158. https://ideas.repec.org/a/eee/empfin/v4y1997i2-3p115-158.html
- Andersen, T. G., Bollerslev, T., Diebold, F. X., & Vega, C. (2003). Micro effects of macro announcements: Real-time
  price discovery in foreign exchange. *American Economic Review*, 93(1), 38-62.
  https://econpapers.repec.org/RePEc:aea:aecrev:v:93:y:2003:i:1:p:38-62
- Baltussen, G., Da, Z., Lammers, S., & Martens, M. (2021). Hedging demand and market intraday momentum. *Journal of
  Financial Economics*, 142(1), 377-403. https://econpapers.repec.org/RePEc:eee:jfinec:v:142:y:2021:i:1:p:377-403 ;
  working paper https://www3.nd.edu/~zda/intramom.pdf
- Bogousslavsky, V., & Muravyev, D. (2023). Who trades at the close? Implications for price discovery and liquidity.
  *Journal of Financial Markets*, 66. https://ideas.repec.org/a/eee/finmar/v66y2023ics1386418123000502.html
- Bondarenko, O., & Muravyev, D. (2023). Market return around the clock: A puzzle. *Journal of Financial and
  Quantitative Analysis*, 58(3), 939-967.
  https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/market-return-around-the-clock-a-puzzle/089E33AC0B4D3B9A02CBA31EDF6505B3
- Boyarchenko, N., Larsen, L. C., & Whelan, P. (2023). The overnight drift. *Review of Financial Studies*, 36(9),
  3502-3547. Staff report https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf
- Boyarchenko, N., Larsen, L. C., & Whelan, P. (2026, July 1). The disappearing overnight drift. *Liberty Street
  Economics*, Federal Reserve Bank of New York.
  https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/
- Carchano, O., & Pardo, A. (2011). Calendar anomalies in stock index futures (working paper; via secondary summaries).
  https://cxoadvisory.com/calendar-effects/stock-index-futures-calendar-effects
- Cederburg, S., O'Doherty, M. S., Wang, F., & Yan, X. (2020). On the performance of volatility-managed portfolios.
  *Journal of Financial Economics*, 138(1), 95-117. https://www.lehigh.edu/~xuy219/research/COWY.pdf
- Cheng, M., & Madhavan, A. (2009). The dynamics of leveraged and inverse exchange-traded funds. *Journal of
  Investment Management*, 7(4), 43-62. https://joim.com/dynamics-leveraged-inverse-exchange-traded-funds
- Cieslak, A., Morse, A., & Vissing-Jorgensen, A. (2019). Stock returns over the FOMC cycle. *Journal of Finance*,
  74(5). https://papers.ssrn.com/abstract=2687614
- Etula, E., Rinne, K., Suominen, M., & Vaittinen, L. (2020). Dash for cash: Monthly market impact of institutional
  liquidity needs. *Review of Financial Studies*, 33(1), 75-111 (open access).
  https://acris.aalto.fi/ws/portalfiles/portal/40965155/hhz054.pdf
- Fung, A. K. W., Mok, D. M. Y., & Lam, K. (2000). Intraday price reversals for index futures in the US and Hong Kong.
  *Journal of Banking & Finance*, 24(7), 1179-1201.
  https://scholars.hkbu.edu.hk/en/publications/intraday-price-reversals-for-index-futures-in-the-us-and-hong-kon/
- Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). Market intraday momentum. *Journal of Financial Economics*, 129(2),
  394-414. https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414
- Grant, J. L., Wolf, A., & Yu, S. (2005). Intraday price reversals in the US stock index futures market: A 15-year
  study. *Journal of Banking & Finance*, 29(5), 1311-1327. https://ideas.repec.org/a/eee/jbfina/v29y2005i5p1311-1327.html
- Harvey, C. R., Liu, Y., & Zhu, H. (2016). ... and the cross-section of expected returns. *Review of Financial
  Studies*, 29(1), 5-68. https://www.nber.org/papers/w20592
- Heston, S. L., Korajczyk, R. A., & Sadka, R. (2010). Intraday patterns in the cross-section of stock returns.
  *Journal of Finance*, 65(4), 1369-1407. https://arxiv.org/pdf/1005.3535.pdf
- Hou, K., Xue, C., & Zhang, L. (2020). Replicating anomalies. *Review of Financial Studies*, 33(5), 2019-2133.
  https://www.nber.org/papers/w23394
- Hu, G. X., Pan, J., Wang, J., & Zhu, H. (2022). Premium for heightened uncertainty: Explaining pre-announcement
  market returns. *Journal of Financial Economics*, 145(3), 909-936.
  https://www.mit.edu/~zhuh/HuPanWangZhu_preannouncement.pdf (Tables 1 and 2 read for this note)
- Huang, D., Li, J., Wang, L., & Zhou, G. (2020). Time series momentum: Is it there? *Journal of Financial
  Economics*, 135(3), 774-794. https://core.ac.uk/download/287750773.pdf
- Ivanov, I. T., & Lenkey, S. L. (2018). Do leveraged ETFs really amplify late-day returns and volatility? *Journal of
  Financial Markets*, 41, 36-56. https://econpapers.repec.org/RePEc:eee:finmar:v:41:y:2018:i:c:p:36-56 ; Lenkey (2024)
  survey: https://www.aimspress.com/article/doi/10.3934/QFE.2024031
- Kim, A. Y., Tse, Y., & Wald, J. K. (2016). Time series momentum and volatility scaling. *Journal of Financial
  Markets*, 30, 103-124. https://econpapers.repec.org/RePEc:eee:finmar:v:30:y:2016:i:c:p:103-124
- Kurov, A., Wolfe, M. H., & Gilbert, T. (2021). The disappearing pre-FOMC announcement drift. *Finance Research
  Letters*, 40. https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf
- Li, Z., Sakkas, A., & Urquhart, A. (2022). Intraday time series momentum: Global evidence and links to market
  characteristics. *Journal of Financial Markets*, 57, 100619. https://centaur.reading.ac.uk/95566
- Lucca, D. O., & Moench, E. (2015). The pre-FOMC announcement drift. *Journal of Finance*, 70(1), 329-371.
  https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf
- Maberly, E. D., & Waggoner, D. F. (2000). Closing the question on the continuation of turn-of-the-month effects:
  Evidence from the S&P 500 index futures contract. Federal Reserve Bank of Atlanta WP 2000-11.
  https://ideas.repec.org/p/fip/fedawp/2000-11.html
- Marshall, B. R., Cahan, R. H., & Cahan, J. M. (2008). Does intraday technical analysis in the U.S. equity market
  have value? *Journal of Empirical Finance*, 15(2), 199-210. https://ideas.repec.org/a/eee/empfin/v15y2008i2p199-210.html
- McConnell, J. J., & Xu, W. (2008). Equity returns at the turn of the month. *Financial Analysts Journal*, 64(2),
  49-64. https://rpc.cfainstitute.org/research/financial-analysts-journal/2008/equity-returns-at-the-turn-of-the-month
- McLean, R. D., & Pontiff, J. (2016). Does academic research destroy stock return predictability? *Journal of
  Finance*, 71(1), 5-32. https://www.gwern.net/doc/economics/2016-mclean.pdf
- Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*,
  104(2), 228-250. https://econpapers.repec.org/RePEc:eee:jfinec:v:104:y:2012:i:2:p:228-250
- Park, C.-H., & Irwin, S. H. (2007). What do we know about the profitability of technical analysis? *Journal of
  Economic Surveys*, 21(4), 786-826. https://econpapers.repec.org/RePEc:bla:jecsur:v:21:y:2007:i:4:p:786-826
- Rosa, C. (2022). Understanding intraday momentum strategies. *Journal of Futures Markets*, 42(12), 2218-2234.
  https://ideas.repec.org/a/wly/jfutmk/v42y2022i12p2218-2234.html
- Sullivan, R., Timmermann, A., & White, H. (2001). Dangers of data mining: The case of calendar effects in stock
  returns. *Journal of Econometrics*, 105(1), 249-286. https://econpapers.repec.org/RePEc:eee:econom:v:105:y:2001:i:1:p:249-286
- Zarattini, C., Aziz, A., & Barbon, A. (2024, rev. 2025). Beat the market: An effective intraday momentum strategy
  for S&P500 ETF (SPY). SFI Research Paper 24-97 (working paper, not peer-reviewed). https://ideas.repec.org/p/chf/rpseri/rp2497.html
- SEC T+1 settlement compliance date 2024-05-28 (law-firm summary):
  https://www.aoshearman.com/en/insights/t1-settlement-coming-may-28-2024
- Practitioner pointers only (not evidence): CXO Advisory and Quantpedia turn-of-month pages; Alpha Architect summaries.

## 7. What the operator might be asked to decide (stated, not authorised)

- **Nothing is needed for the first screens.** The local NQ bars (development to 2026-07-16), QuantConnect's free
  minute history from 2009, and free release calendars (BLS, ISM, BEA, Federal Reserve) cover all five candidates.
- **Optional purchase: ES 1-minute bars from Databento** (`docs/OPERATOR_SETUP.md` item 1). Most of this literature
  is measured on the S&P 500, so ES is the natural second market and has an unread confirmation window (2025-07-01 to
  2026-09-30, `config/windows.yaml`). Expected cost is of the order of the NQ purchase on record ($10.25 for
  2020-01 to 2025-06); Databento's checkout shows the exact figure. Not authorised here.
- **Later, only for a confirmation: the NQ top-up from 2026-07-17** (item 6, "a few dollars"). Opening the reserved
  window is the operator's decision (D-107).
- **Not recommended:** closing-imbalance feeds, options data, tick or depth data. The candidates that need them are
  in the out-list.
- **Research decisions for the coordinator, not the operator:**
  - whether rank 1's pre-release exit is allowed under D-212, or the bracket is held through the release;
  - which span (local 2020-2026 only, or QC from 2009) a batch reads, declared before its menu;
  - the batch's error share under D-578.
