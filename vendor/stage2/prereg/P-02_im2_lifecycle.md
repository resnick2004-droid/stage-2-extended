# P-02 — IM2: noise-band entries under stage one's lifecycle, ES, CL, 6E and NG, accounts rotated

| field | value |
|---|---|
| **id** | P-02 |
| **date** | 2026-09-27 |
| **author** | stage-two session, for the operator (Ryan Resnick) |
| **task** | T4 5p (the model) and T5 (its one confirmation test) |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after the model card and its screen, before any kit |
| **status** | abandoned (2026-09-27, D-163: withdrawn before any run) |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 3 |
| `development_period` | 2009-06-01 .. 2019-12-31 |
| `confirmation_period` | 2024-05-10 .. 2026-08-31 |
| `confirmation_tests_on_this_market` | 0 |
| `bonferroni_alpha` | not required: a held-out confirmation period is used |
| `assumed_sd` | 1.1 |
| `assumed_sd_source` | assumption: no IM2 trade exists yet; outcomes are brackets at 1:1 and 2:1 with time exits at the close, so the per-trade sd in units of the stop sits between the 1:1 binary value (about 1.0) and the 2:1 one (about 1.4); the development run measures it per R and reports it beside this value |
| `risk_denominator` | realised |
| `primary_metric` | median_log_growth |
| `data_period` | 2009-05-01 .. 2019-12-31 and 2024-04-01 .. 2026-08-31; nothing from 2020-01-01 .. 2024-03-31 is read |
| `seed` | 20261119 |
| `model_card` | docs/candidates/cards/IM2.md |

**Multiplicity plan.** The entry rule is the paper's (nothing searched). The only choice is the funded policy: three of
stage one's were considered (its day-one all-in with harvest; static 2:1 $750; build 2:1 $1,000 then harvest 1:1 $150),
and one was chosen before this registration, on development-period data only -- the cheap screen
(`results/im2_screen.csv`, a proxy on the 2009-2019 bracket map), whose measured share of 3:1 brackets resolving inside
a session ruled out the all-in, and stage one's results, which favour build-then-harvest over static 2:1 $750 (the card,
§2). So k = 3 are counted and one configuration is run. The development period applies the kill lines; the
confirmation period is run once and the pass line applied to that run alone.

---

## 1. Question

Does IM2 -- the published noise-band entries on ES, CL, 6E and NG, every trade bracketed, sized and rationed per day by
stage one's lifecycle for the account that takes it, the trades rotated across five accounts -- make money inside the
Topstep contract out of sample, on the years after the entry rule was published? A yes makes it the stage's candidate
for the protocol comparison (T7); a no drops it and the search moves on, with the evidence on record.

**Why the confirmation starts 2024-05-10.** The entry rule is published (Zarattini, Aziz & Barbon, SSRN 4824172, first
version 2024-05-10) and was set on SPY data from May 2007 to April 2024 (the paper's §2), which covers most of D-144's
confirmation window. D-49's rule for a fully specified published rule is that it confirms on its post-publication
window, so that is the test: 2024-05-10 to 2026-08-31, the last complete month. The exits and sizes are stage one's,
fixed before any IM2 data was read. 2020-01-01 to 2024-03-31 is not read at all, so it stays unspent for other models.
**Not fully blind for ES:** the paper's later versions report the rule's monthly results on SPY through September 2025
(FAQ Q24), which we have read; FAQ Q13 reports S&P 500 futures, named, from January 2007 to September 2024 in
aggregate, and FAQ Q12 ETFs and stocks to August 2024; the commodity rows in Q13 are masked, and none reports CL, 6E or
NG by market or by year. Those reports are of the paper's own exits, not these brackets. The verdict is on the
four-market campaign, and the report says this plainly.

## 2. Data period

- **Source**: QuantConnect minute futures through the manual-run route (D-81), the contract chosen by the kit's own
  roll rule in §3 (not QuantConnect's default mapping recorded in `docs/DATA_SOURCES.md`); every kit's integrity
  counts as D-148 requires. **Before the harness runs**, the data-integrity agent validates the ES, CL, 6E and NG
  minute bars for the development window: `docs/DATA_SOURCES.md` records only their presence and start dates. The
  confirmation window's bars are validated only after the development kill lines pass, so a model killed in
  development never reads them.
- **Symbols and resolution**: ES, CL, 6E, NG, one-minute bars (coverage from 2008-11, `docs/DATA_SOURCES.md`).
- **In-sample / training period**: 2009-06-01 .. 2019-12-31 (D-144), preceded by a warm-up from 2009-05-01 that fills
  the 14-session lookback and records nothing. Nothing is fitted; the period measures the model for the kill lines.
- **Out-of-sample / test period**: 2024-05-10 .. 2026-08-31, fixed now, run once (D-49, see §1), preceded by a
  warm-up from 2024-04-01 that fills the lookback and records nothing. 2020-01-01 .. 2024-03-31 is not read.
- **Walk-forward scheme**: none; no parameter is estimated from the data.

> The test period is fixed here and not revisited. Extending it after seeing a result, or
> sliding it to a friendlier regime, converts an out-of-sample test into an in-sample one.

## 3. Rules fixed before the run

Everything below is the model card's (`docs/candidates/cards/IM2.md` §2 and §4, with IM1's card §4 for the shared
market rules), restated so the run can be checked against it.

**Market rules, carried over unchanged from P-01 (reviewed five times, 2026-09-26):**

- **Price series**: raw prices of the contract actually traded -- QuantConnect's continuous future with open-interest
  mapping and RAW normalisation, the active contract tracked, as every kit here does. Each day is rescaled so its
  session open maps to the market's reference price for sizing (D-106's convention, as FV1 and the bracket map): ES
  4000 (FV1's; below ES's level in the confirmation years, which overstates its cost in R -- conservative), CL 70,
  6E 1.10, NG 3.00 (round levels); the actual prices are exported for the audit, and a result at the actual scale is
  reported beside. Signals are computed on raw prices; the rescale applies only to fills, costs and R.
- **Session per market** (CT): ES 08:30-15:00; CL and NG 08:00-13:30; 6E 07:20-14:00. The session open is the first
  bar's open. The 14-session sigma uses each session's own contract (a ratio to that session's open, so a roll does
  not enter it).
- **Contract and roll -- the one rule** (as `runs/R052-bmap-ES-1419/main.py` `_roll`): each market's continuous
  future is subscribed with open-interest mapping, RAW prices and extended hours, which does only two things: it names
  the first active contract, and a replacement if the active contract leaves the universe. Otherwise the kit trades
  its own active contract and, at each session's close bar, switches to the contract expiring after today with the
  most volume summed over every bar since the previous close bar (the overnight included). **The prior close is the
  active contract's close at the previous session's close bar**, so on a roll day it is the new contract's. If the new
  contract has no bar at that close bar, there is no prior close and the next session is not traded.
- **Which sessions are traded -- no look-ahead**: every session the exchange calendar schedules as a full session --
  QuantConnect's market-hours database as shipped with the LEAN version the kit runs on (recorded in the run's
  provenance), each market's own entry (CME for ES and 6E, NYMEX for CL and NG); scheduled holidays and early closes
  are not traded. **A session whose previous session was incomplete** (every scheduled early close included) has no
  prior close and is not traded either; their count is reported. A session with fewer than 14 complete past sessions
  takes no decision. A traded session whose data ends early (an unscheduled gap) closes any open position at its last
  available bar at or before the close time, one tick adverse. **Past sessions** count among the 14 for sigma, and
  supply a prior close, only if complete: a bar at the close time and at least 90 % of the minutes (the bracket map's
  rule, D-149). Within a session a minute with no bar is skipped for VWAP and carries the last close forward for
  sigma's |close / open - 1|; if the bar ending at a decision time is missing, that decision is not taken.
- **The day set**: every date in each period that the calendar schedules as a full session for at least one of the
  four markets is one day -- one day block in the campaign (empty when no trade) and one day in the block bootstrap
  (days without a trade included); other dates are not days. Traded-session and excluded-day counts are reported per
  market.
- **VWAP**: from the session open, the typical price (high + low + close) / 3 weighted by the traded contract's volume,
  cumulative (the authors' published code, read 2026-09-26; `propedge/outcomes/bracket_core.py`).
- **Noise band** at each minute HH:MM of the session: sigma(HH:MM) = the mean over the previous 14 complete sessions of
  |close(HH:MM) / open - 1|; upper band = max(open, prior close) x (1 + sigma), lower band = min(open, prior close)
  x (1 - sigma); volatility multiplier 1.0.
- **Decision times**: every :00 and :30 mark from the first one at least 30 minutes after the session opens to the
  last one at least 30 minutes before it closes: ES 09:00-14:30, CL and NG 08:30-13:00, 6E 08:00-13:30 CT.
- **Fill model / cost profile**: `assumed` (D-95: one tick of the traded micro adverse on entry, stop and the close;
  a target needs a trade through and fills at its price; a bar that opens through the stop fills at that open with no
  further tick), an assumption, not measured. "One tick" is the traded micro's: MES 0.25, MCL 0.01, M6E 0.0001,
  MNG 0.001. Round turn per micro from the published Topstep schedule (help.topstep.com 8284213, `config/fills.yaml`,
  D-158): MES 1.22 and M6E 1.00; MCL and MNG at **the totals 8284213 states when re-read on or after 2026-10-01**, the
  day an announced CME exchange-fee rise of $0.10 per side takes effect on both, verified and recorded on the ledger by
  the rules-verifier. If the re-read still states no new totals, **MCL 1.72 and MNG 1.92** (the verified table
  figures plus the announced $0.20 a round turn), fixed now; loading them is recorded then in `config/fills.yaml` and
  `DECISIONS.md` as derived, not verified. Nothing is scored before that re-read is recorded.

**IM2's own rules:**

- **Entry**: at a decision time, with the market flat (see sequencing) -- on the close of the bar ending then, **long
  if the close is above both the upper band and VWAP, short if below both the lower band and VWAP** (the authors'
  published code, read 2026-09-26: `signals[(current_close_prices > UB) & (current_close_prices > vwap)] = 1`;
  `signals[(current_close_prices < LB) & (current_close_prices < vwap)] = -1`); otherwise no entry. The code also
  evaluates the open minute; the paper's text puts the first position 30 minutes after the open, and that is the rule
  here. The entry fills at the next bar's open, one tick adverse.
- **Stop**: resting and continuous at the opposite band's level at the decision time (the decision bar's sigma and
  anchor) -- the paper's base-model stop. The stop distance is measured from the entry fill (after its tick) to the
  stop level, which is not rounded to the tick grid. An entry that fills at or beyond its own stop is not taken, and
  is counted. A bar that touches the stop fills there one tick adverse; a bar that opens through it fills at its open.
- **Targets**: resting limits at R x the stop distance beyond the entry fill, for **R = 1, 2 and 3**, each an
  independent bracket on the same entry and the same stop; when a bar touches both the stop and a target, the stop is
  taken first (conservative). Each bracket ends at its target, its stop, or the session close (one tick adverse).
  R = 1 and 2 are the lifecycle's; R = 3 is reported only.
- **Market sequencing -- no opposite positions across accounts (D-55)**: a market is busy from an entry until that
  entry's **2:1 bracket** ends (the longest bracket the lifecycle uses), then **5 minutes** (D-160, D-61's gap), measured
  from that bracket's `exit_t`; only then may the market enter again, at the open of the first bar starting at or
  after `exit_t` plus 5 minutes. A trade taken at 1:1 exits sooner on its account, but the market still waits, so no
  account can be handed the opposite side of a market while another account's bracket in it is open. One position per
  market at a time; no flips.
- **Time stamps for routing**: each entry's `entry_t` is the start minute of the bar its entry fills in; its `exit_t`
  is the end minute of the bar its **2:1 bracket** exits in (a stop inside a bar included), both minutes after midnight
  CT on one clock across the four markets; an exit and an entry in the same minute overlap.
- **What the log carries**: **every entry the rules generate**, at one micro contract (as FV1's kits), each with its
  stop distance, its entry and exit times, and, for each R in 1, 2 and 3, its outcome in R net of one micro's costs and
  its MAE in R before that bracket's exit (including the exit bar and a gap open) -- `DayBlock.r_by_rr` and
  `mae_by_rr` (D-162). **e at each R, its lower bound and the kill lines are computed over every entry**, in R, so they
  do not depend on size.
- **Routing (D-157, D-159, D-162)**: the four markets' entries form one stream in entry order (ties in the order ES,
  CL, 6E, NG). Each goes to the next account in turn that is **flat at its entry** and **below its state's trade limit
  for the session**, and is skipped, and counted, if none is. No account holds two positions at once, so the engine's
  one-after-another settlement of an account's trades is exact, and the per-trade cap is the account's cap.
- **The lifecycle -- each account's state sets its trade's R, dollar risk and trade limit** (stage one; the card §2),
  as the policy the engine runs (`propedge.campaign.risk_policy`, D-147, D-162):

  ```
  RiskPolicy(id="im2_s1_lifecycle", root=Phase(
      combine=Leaf("combine 1:1 $1,500", risk=1500, rr=1.0, max_trades=1),
      funded=Tiers(on="balance", name="funded", tiers=(
          (0,    Leaf("build 2:1 $1,000",  risk=1000, rr=2.0, max_trades=1)),
          (2000, Leaf("harvest 1:1 $150",  risk=150,  rr=1.0, max_trades=3))))))
  ```

  A funded account below +$2,000 builds at 2:1 $1,000, at or above it harvests at 1:1 $150, re-read at every session
  start (a payout that takes the balance below +$2,000 returns it to building); a paid account follows the funded
  rule. Sources: `vendor/propsim/results_state_policy_combine.csv` ("static 1:1 $1500 1/day"),
  `vendor/propsim/results_state_policy_xfa.csv` ("build 2:1 $1000 -> harvest 1:1 $150 x3/day").
- **Sizing**: `SizingRule` in `current_tier` mode with the declared headroom 0.75 (D-117): contracts = floor(the
  state's dollar risk / (stop distance in points x the micro's value per point)), capped at 75 % of the account's
  current scaling-tier allowance; a trade whose risk buys no contract on that account is not taken there, is counted
  (`share_trades_unsized`), and still occupied its routed account for its duration (conservative). The micros are MES,
  MCL, M6E and MNG on the standard contracts' price paths (D-106); M6E's tick is 0.0001 at $1.25, so its stops convert
  in points, never in 6E ticks.
- **Accounts**: **five in total, Combines and funded together** (D-34; the operator's plan of five accounts): five
  Combines at the start, a Combine bought only while the live total is below five; a pass always finds a funded slot,
  so the hold queue never arises and `hold_expiry_days` stays not required under D-34.
- **Protocol** (the engine's base legs; the policy above sets every trade): Combine 1:1 $1,500, funded 2:1 $1,000; the
  Standard payout path; nothing kept back (`keep_balance` 0) and the full allowed payout requested (`payout_frac` 1.0,
  stage one's A5); the Aeropay method and its verified lag; the activation fee paid on activation; no resets;
  reinvestment on. Trade slots per day: at least the busiest day of the log being run, as the engine requires. The
  campaign's rules object is `propedge.campaign.payout_method.rules_for_method("aeropay")`.
- **Bankroll and horizon of the verdict**: $5,000 and 504 sessions. The operator's own bankrolls, when given
  (docs/HUMAN_INPUTS.md), are run beside the verdict as exploratory and never replace it.
- **Settlement (D-156)**: each trade settles from its MAE at the R it was taken at (`mae`).
- **Session, and the 15:10 CT flatten handling**: every bracket ends at its market's session close at the latest, at
  or before 15:00 CT; nothing is held overnight.
- **Parameters, with their exact values.** Lookback 14 sessions; volatility multiplier 1.0; decision interval 30
  minutes; decision times, sessions, reference prices and ticks as above; brackets at 1, 2 and 3 R on the opposite-band
  stop; market wait until the 2:1 bracket ends plus 5 minutes; the lifecycle policy above; headroom 0.75; five accounts
  in total. None is left to be chosen.

**Conduct check in D-145's three tiers** (`propedge/campaign/conduct.py` is the one source):

- Tier 1, hard — every box must be ticked, or the model is not a candidate:
  - [x] no cross-account hedging (one position per market at a time; a market waits until its longest bracket ends
    plus 5 minutes before any new entry, so no two accounts hold opposite positions in one market even briefly, D-55,
    D-160; D-55's correlated groups are the declared ones in `config/candidate_constraints.yaml`, where equity index,
    crude, euro and natural gas are four separate groups, one market each here)
  - [x] no reliance on simulator fills (half-hourly decisions; stops at the opposite band, far from the entry; no
    auto-breakeven) or fills outside the best bid or offer
  - [x] no maximum size into major news: sizes are set by the state's dollar risk and capped at 75 % of the tier
    allowance, never the maximum; disclosed: CL and NG can enter at the 09:30 CT decision on EIA inventory and
    storage-report days, ES, 6E, CL and NG at 13:00 CT on FOMC days (the release minute), and ES at 09:00 CT with
    10:00 ET releases; no coordinated trading
  - Disclosed: the open question on the asterisk the help centre puts on micro contracts (D-62,
    `docs/HUMAN_INPUTS.md`) applies to all four micros used here
  - Disclosed for the record (D-160): rotation puts sequential trades in one market on different accounts, which can
    be on opposite sides within a day; never at the same time, and with 5 minutes flat between them
  - [x] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled: the 1:1 Combine and harvest brackets are R at or below 1 (a trigger); the build risk, $1,000, is
  exactly half the funded drawdown, not above it; several accounts at the MLL in one day is less likely under
  rotation. The simulator applies any consequence (the RTP daily loss limit and the Consistency path).
- Tier 3, priced: many Combine purchases -- priced at 25 % denial by the gate.

## 4. Metrics

Exactly what will be computed, and from what:

- **Primary**: the D-145 gate -- the campaign's median log growth of the fee bankroll per year, with each R's trade
  outcomes shifted down to that R's one-sided 95 % lower bound of e, fees, payout latency and tier-2 consequences
  applied, 25 % tier-3 denial, the lifecycle policy, rotation across five accounts in total, MAE settlement, the
  protocol and sizing of §3 (`propedge.campaign.gate.run_gate(mode="rotation", combines=5, accounts=5,
  total_accounts=5, risk_policy=<§3's policy>, e_by_rr={1: e_1, 2: e_2}, lb_by_rr={1: lb_1, 2: lb_2}, e=e_2, lb=lb_2)`,
  the blocks' base P&L being the 2:1 outcome, 500 paths, seed 20261119).
- **Interval**, for each R in 1 and 2: e_R = the mean of the per-entry outcome in R at that bracket, net of costs, as
  `propedge.backtest.metrics.estimate_edge` computes it (the mean of per-trade R); its one-sided 95 % lower bound
  lb_R is the lower of (a) the 20-day moving-block bootstrap over the day set of §3, days without an entry included
  (`propedge.research.fv_score.block_lower_bound(day_sums, day_counts, block=20, reps=10000, seed=20261119)`) and
  (b) the normal approximation clustered by day (`propedge.backtest.metrics.normal_lower_bound(r, days)`).
- **Also reported**: entry and day counts; entries per market per day; trades per account per day by state, with the
  shares skipped because no account was flat or below its limit (`share_trades_skipped_no_flat_account`) and unsized
  at their state's risk (`share_trades_unsized`); the median trading days for a Combine to resolve (kill line 1);
  Combine purchases per year beside growth (D-34); at each R, the hit rate, the share ending at the stop, the target
  and the close, and e_3 with its bound (reported only); realised per-trade sd against `assumed_sd`; cost drag as a
  fraction of dollars risked; the campaign at the point estimate and at 0 / 10 / 50 % denial; ruin probability,
  bankroll drawdown and payout latency beside growth; whether the old criterion (e >= 0.10, bound >= 0.05, propsim
  D-47) is met at R = 1 and at R = 2; the variant count; each market's e separately, descriptive only; the
  confirmation's months from 2025-10-01 on separately, descriptive only; the D-148 review sheet's sample seed is
  20261119.

## 5. Pass / fail criteria

- **Pass**: the D-145 gate on the confirmation period (2024-05-10 .. 2026-08-31), run once: median log growth above
  zero with each R at its lower bound, with everything in §4's primary metric applied and the policy, protocol,
  accounts, bankroll and horizon of §3. e, its bound and the old criterion at each R are reported beside it.
- **Fail**: anything else.
- **Kill lines on the development period (2009-06-01 .. 2019-12-31), applied before the confirmation is run**:
  1. **D-154's rule fails**: in the development gate row (§4's primary metric on development data), the median, over
     every Combine that resolved in its 500 paths, of the trading days it took to resolve exceeds one billing period
     (21 trading days) -- the typical Combine would roll into a new subscription for want of setups.
  2. **The D-145 gate fails on the development period**, as §4's primary metric.

  Either drops the model, and the confirmation period is not spent. **A rule violation in the trade audit** (D-148) is
  not a verdict on the model: it is a defect in the kit or the scorer, diagnosed under the failure protocol, fixed,
  and the development run repeated with the same seed; the readings before the fix stay on record, and the kill lines
  are read on the corrected run.
- **What a fail means for the project**: IM2 is dropped. No variant of it (another lookback, multiplier, market set,
  stop, bracket, lifecycle policy or filter) is tried under this registration; a changed rule is a new model card with
  its own variant count.

> A failed pre-registered check is **kept on record and diagnosed**, never rerun until it
> passes: terminal-state audit → stage decomposition → component test in isolation →
> replication with seeds fixed beforehand. See the failure protocol in `CLAUDE.md` and
> propsim D-40.

## 6. Seed

- **Seed**: 20261119
- Additional seeds: none; the bootstrap and every campaign path derive from it.

## 7. Variants

- Configurations already tried for this question: IM1 was registered as P-01 and withdrawn before any run (D-161),
  so nothing was tried; the IM2 screen (`results/variants.jsonl`, `IM2:screen`) read proxy data only.
- Configurations this pre-registration will try: 1, chosen from k = 3 funded policies before registration (the
  multiplicity plan above).

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

---

## Outcome

- **Date run**: not run; no kit was built and no data was read.
- **Result file(s)**: none.
- **Verdict**: withdrawn, not a result. Recorded here so the registration stays on record.
- **Numbers**: none.
- **Why withdrawn**: its gatekeeper's review (2026-09-27) found that the harvest leg, 1:1 at $150, is sized in whole
  micro contracts to a realised risk at or below $150, so a single harvest win, net of costs, is always below the
  Standard path's $150 winning-day minimum (8284233): harvest days would almost never count toward a payout, and
  the mechanism stage one's frictionless harvest relied on would not work on real contracts.
- **Decision taken**: D-163. P-03 is the same model with the harvest at 1:1 $300 (stage one's $300 harvest pays about
  the same as its $150 one), and takes up this review's clarifications.
