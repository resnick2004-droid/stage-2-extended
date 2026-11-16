# P-01 — IM1: intraday momentum with a noise band, ES, CL, 6E and NG, accounts rotated

| field | value |
|---|---|
| **id** | P-01 |
| **date** | 2026-09-26 |
| **author** | stage-two session, for the operator (Ryan Resnick) |
| **task** | T4 5o (the model) and T5 (its one confirmation test) |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after the model card and its screen, before any kit |
| **status** | abandoned (2026-09-27, D-161: withdrawn before any run) |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 1 |
| `development_period` | 2009-06-01 .. 2019-12-31 |
| `confirmation_period` | 2024-05-10 .. 2026-08-31 |
| `confirmation_tests_on_this_market` | 0 |
| `bonferroni_alpha` | not required: a held-out confirmation period is used |
| `assumed_sd` | 1.0 |
| `assumed_sd_source` | assumption: no IM1 trade exists yet; losses mostly end at the trailing exit well inside the protective stop and winners run, so the per-trade sd in units of the protective-stop risk is expected near one; the development run measures it and reports it beside this value |
| `risk_denominator` | realised |
| `primary_metric` | median_log_growth |
| `data_period` | 2009-05-01 .. 2019-12-31 and 2024-04-01 .. 2026-08-31; nothing from 2020-01-01 .. 2024-03-31 is read |
| `seed` | 20261117 |
| `model_card` | docs/candidates/cards/IM1.md |

**Multiplicity plan.** Nothing is selected: the model has one configuration (k = 1), taken from the paper and the
operator's decisions in the card, and it is measured on the development period only to apply the kill lines below.
The confirmation period is then run once and the pass line applied to that run alone.

---

## 1. Question

Does IM1 -- the published intraday momentum rules on ES, CL, 6E and NG, its trades rotated across five accounts --
make money inside the Topstep contract out of sample, on the years after the rule was published? A yes makes it the
stage's candidate for the protocol comparison (T7); a no drops it and the search moves on, with the evidence on
record.

**Why the confirmation starts 2024-05-10.** The rule is published (Zarattini, Aziz & Barbon, SSRN 4824172, first
version 2024-05-10) and was set on SPY data from May 2007 to April 2024 (the paper's §2), which covers most of D-144's
confirmation window. D-49's rule for a fully specified published rule is that it confirms on its post-publication
window, so that is the test: 2024-05-10 to 2026-08-31, the last complete month. 2020-01-01 to 2024-03-31 is not read
at all, so it stays unspent for other models. **Not fully blind for ES:** the paper's later versions report the rule's
monthly results on SPY through September 2025 (FAQ Q24), which we have read; FAQ Q13 reports S&P 500 futures, named,
from January 2007 to September 2024 in aggregate, and FAQ Q12 ETFs and stocks to August 2024; the commodity rows in Q13
are masked, and none reports CL, 6E or NG by market or by year. The verdict is on the four-market campaign, and the
report says this plainly.

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

Everything below is the model card's (`docs/candidates/cards/IM1.md` §4), restated so the run can be checked against it.

- **Price series**: raw prices of the contract actually traded -- QuantConnect's continuous future with open-interest
  mapping and RAW normalisation, the active contract tracked, as every kit here does. Each day is rescaled so its
  session open maps to the market's reference price for sizing (D-106's convention, as FV1 and the bracket map): ES
  4000 (FV1's; below ES's level in the confirmation years, which overstates its cost in R -- conservative), CL 70,
  6E 1.10, NG 3.00 (round levels); the actual prices are exported for the audit, and a result at the actual scale is
  reported beside.
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
  prior close and is not traded either (R052's behaviour); their count is reported.
  A traded session whose data ends early (an unscheduled gap) closes any open position at its last available bar at
  or before the close time, one tick adverse. **Past sessions** count among the 14 for sigma, and supply a prior close,
  only if complete: a bar at the close time and at least 90 % of the minutes (the bracket map's rule, D-149). Within a
  session a minute with no bar is skipped for VWAP and carries the last close forward for sigma's |close / open - 1|;
  if the bar ending at a decision time is missing, that decision is not taken and the position is unchanged.
- **The day set**: every date in each period that the calendar schedules as a full session for at least one of the
  four markets is one day -- one day block in the campaign (empty when no trade) and one day in the block bootstrap
  (days without a trade included); other dates are not days. Traded-session and excluded-day counts are reported per
  market.
- **Time stamps for routing**: each trade's `entry_t` is the start minute of the bar its entry fills in, and `exit_t`
  the end minute of the bar its exit fills in (a stop inside a bar included), both minutes after midnight CT on one
  clock across the four markets; an exit and an entry in the same minute overlap.
- **VWAP**: from the session open, the typical price (high + low + close) / 3 weighted by the traded contract's volume,
  cumulative (the authors' published code, read 2026-09-26; `propedge/outcomes/bracket_core.py`).
- **Noise band** at each minute HH:MM of the session: sigma(HH:MM) = the mean over the previous 14 sessions of
  |close(HH:MM) / open - 1|; upper band = max(open, prior close) x (1 + sigma), lower band = min(open, prior close)
  x (1 - sigma); volatility multiplier 1.0.
- **Entry, exit and flip -- one rule, the target position**: at each decision time -- every :00 and :30 mark from the
  first one at least 30 minutes after the session opens to the last one at least 30 minutes before it closes: ES
  09:00-14:30, CL and NG 08:30-13:00, 6E 08:00-13:30 CT -- on the close of the bar ending then, the target position
  is **long if the close is above both the upper band and VWAP, short if below both the lower band and VWAP, and flat
  otherwise**. This is the authors' published code (concretumgroup.com, "Python backtesting: Beat the Market", read
  2026-09-26: `signals[(current_close_prices > UB) & (current_close_prices > vwap)] = 1`;
  `signals[(current_close_prices < LB) & (current_close_prices < vwap)] = -1`; otherwise 0), which is the paper's
  entry and its trailing exit (max(upper band, VWAP) for a long) as one condition. The code also evaluates the open
  minute; the paper's text puts the first position 30 minutes after the open, and that is the rule here. One
  position per market at a time.
- **Moving to the target**: from flat, the entry fills at the next bar's open, one tick of the traded micro adverse.
  To flat, the exit fills at the next bar's open, one tick adverse. **After any exit in a market, no new position in
  it is entered until 5 minutes after the exit** (D-61's confirmed-flat gap; D-160), **measured from the exit's
  `exit_t`** -- the end minute of the bar the exit filled in, whether at that bar's open or inside it at a stop: a
  flip's new side, and any entry after a stop-out, fills at the open of the first bar starting at or after `exit_t`
  plus 5 minutes, so no two
  accounts ever hold opposite positions in the same market, even for a minute (D-55); the new position goes to the
  next flat account in the rotation.
- **Exit at the close**: anything open closes at its session's close (15:00 / 13:30 / 14:00 CT), one tick adverse,
  before Topstep's 15:10 CT flatten.
- **Protective stop (our modification)**: a resting, continuous stop at the opposite band's level at the decision time
  that set the target (the decision bar's sigma and anchor), placed with the entry. The paper
  checks stops only at half-hour marks (p. 9); the firm's loss limit is continuous, so the account needs a stop that
  is too. Its level is the paper's own base-model stop. A bar that touches it fills there one tick adverse; a bar
  that opens through it fills at its open (gap). The stop distance is measured from the entry fill (after its tick of
  slippage) to the stop level, which is not rounded to the tick grid; an entry that fills at or beyond its own stop
  (a gap past it before the fill) is not taken, and is counted. The stop is not moved at later decisions that keep
  the same target.
  After a stop-out the market is flat until the next decision time, which may enter again (after the 5-minute gap);
  a stop filled inside the bar ending at a decision time leaves that decision in force. "One tick" is the traded
  micro's: MES 0.25, MCL 0.01, M6E 0.0001, MNG 0.001.
- **Bracket R** (target ÷ stop), and the dollar risk per trade: no fixed R (winners run); dollar risk $500 in the
  Combine and $1,000 funded at the protective stop (stage one T5 2a, e >= 0.10 rows); the campaign reads D-154 at the
  1.5:1 row, the nearest stage-one geometry.
- **Session, and the 15:10 CT flatten handling**: every position is closed at its market's session close, at or before
  15:00 CT; nothing is held overnight.
- **What the log carries, and where sizing happens**: the kit exports **every trade the rules generate**, at one micro
  contract (as FV1's kits), each with its stop distance, its outcome in R (net of the costs of one micro), its MAE and
  its entry and exit times. **e, its lower bound and kill line 1 are computed over every one of these trades**, in R,
  so they do not depend on size. Contracts are set in the campaign, per account and per trade
  (`TierSizedDraw`, `current_tier`, headroom 0.75): contracts = floor(dollar risk / (stop distance in points x the
  micro's value per point)), capped at 75 % of that account's current tier allowance (D-117); a trade whose risk buys
  no contract on that account is not taken there, is counted (`share_trades_unsized` on every gate row), and still
  occupied its routed account for its duration (conservative). Wide-stop trades are the ones this drops, so the
  share is reported per market. The micros are MES, MCL, M6E and MNG on the standard contracts' price paths (D-106);
  M6E's tick is 0.0001 at $1.25, so its stops convert in points, never in 6E ticks.
- **Fill model / cost profile**: `assumed` (D-95: one tick adverse on entry, stop and flatten; a target needs a trade
  through; a gap through the stop fills at the next price), an assumption, not measured. Round turn per micro from the
  published Topstep schedule (help.topstep.com 8284213, `config/fills.yaml`, D-158): MES 1.22 and M6E 1.00; MCL and MNG
  at **the totals 8284213 states when re-read on or after 2026-10-01**, the day an announced CME exchange-fee rise of
  $0.10 per side takes effect on both, verified and recorded on the ledger by the rules-verifier. If the re-read still
  states no new totals, **MCL 1.72 and MNG 1.92** (the verified table figures plus the announced $0.20 a round turn),
  fixed now; loading them is recorded then in `config/fills.yaml` and `DECISIONS.md` as derived, not verified. Nothing
  is scored before that re-read is recorded.
- **Routing (D-159)**: the four markets' trades form one stream in entry order (ties in the order ES, CL, 6E, NG). Each
  trade goes to the next account in turn that is **flat at its entry** -- whose previous trade has exited -- and is
  skipped, and counted, if none is. No account ever holds two positions at once, so the engine's one-after-another
  settlement of an account's trades is exact, and the 75 % per-trade cap is the account's cap. The trade log carries
  each trade's entry and exit time for this (`DayBlock.entry_t` / `exit_t`).
- **Accounts**: rotation (D-157): every trade goes to the next live account. **Five accounts in total, Combines and
  funded together** (D-34's "at most 5 concurrent accounts including Combines"; the operator's plan of five
  accounts): five Combines at the start, and a Combine is bought only while the live total is below five
  (`run_gate(mode="rotation", combines=5, accounts=5, total_accounts=5)`, the joint cap in
  `lockstep.simulate_lockstep_path(max_total_accounts=5)`, pinned by `tests/test_total_accounts.py`). A pass always
  finds a funded slot, so the hold queue never arises and `hold_expiry_days` stays not required under D-34.
- **Protocol** (`propedge/campaign/protocols.py`, registry name `s1_pair_high_edge`, stage one's best admissible pair
  at e >= 0.10, T5 2a): Combine $500 and funded $1,000 per trade; the Standard payout path; nothing kept back
  (`keep_balance` 0) and the full allowed payout requested (`payout_frac` 1.0); the Aeropay method and its verified lag;
  the activation fee paid on activation; no resets; reinvestment on. Trade slots per day: at least the busiest day of
  the log being run, as the engine requires (any value at or above it gives identical results). Sizing: `SizingRule` in `current_tier` mode with the declared headroom
  0.75 (D-117): contracts from the dollar risk at the protective stop, capped at 75 % of the account's current
  scaling-tier allowance.
- **Bankroll and horizon of the verdict**: $5,000 and 504 sessions. The operator's own bankrolls, when given
  (docs/HUMAN_INPUTS.md), are run beside the verdict as exploratory and never replace it.
- **Settlement (D-156)**: every trade exports its maximum adverse excursion before its exit (including the exit bar
  and a gap open), and the campaign settles each trade from it (`mae`).
- **Parameters, with their exact values.** Lookback 14 sessions; volatility multiplier 1.0; decision interval 30
  minutes; decision times, sessions, reference prices and ticks as above; dollar risk $500 / $1,000; five accounts in
  total. None is left to be chosen.

**Conduct check in D-145's three tiers** (`propedge/campaign/conduct.py` is the one source):

- Tier 1, hard — every box must be ticked, or the model is not a candidate:
  - [x] no cross-account hedging (one position per market at a time, so no two accounts hold the same market at once;
    a flip is flatten, then enter one bar later, D-55, so opposite positions never overlap even briefly; D-55's
    correlated groups are the declared ones in `config/candidate_constraints.yaml`, where equity index, crude, euro and
    natural gas are four separate groups, one market each here)
  - [x] no reliance on simulator fills (half-hourly decisions, no tight brackets, no auto-breakeven) or fills outside
    the best bid or offer
  - [x] no maximum size into major news: sizes are set by the dollar risk and capped at 75 % of the tier allowance,
    never the maximum; disclosed: CL and NG can enter at the 09:30 CT decision on EIA inventory and storage-report
    days, ES and 6E at 13:00 CT on FOMC days (the release minute), and ES at 09:00 CT with 10:00 ET releases; no
    coordinated trading
  - Disclosed: the open question on the asterisk the help centre puts on micro contracts (D-62,
    `docs/HUMAN_INPUTS.md`) applies to all four micros used here
  - Disclosed for the record (D-160): rotation (D-157) puts sequential trades in the same market on different
    accounts, which can be on opposite sides within a day; never at the same time (D-55), and with 5 minutes flat
    between them (D-61's gap)
  - [x] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled: R at or below 1 is not expected (the paper's winners are larger than its losers) and is measured;
  maximum position on most trades is not expected at these sizes; several accounts at the MLL in one day is less
  likely under rotation. The simulator applies any consequence.
- Tier 3, priced: many Combine purchases -- priced at 25 % denial by the gate.

## 4. Metrics

Exactly what will be computed, and from what:

- **Primary**: the D-145 gate -- the campaign's median log growth of the fee bankroll per year, with the trade outcomes
  shifted down to the one-sided 95 % lower bound of e, fees, payout latency and tier-2 consequences applied, 25 %
  tier-3 denial, trades rotated across five accounts in total, MAE settlement, the protocol and sizing of §3
  (`propedge.campaign.gate.run_gate(mode="rotation", combines=5, accounts=5, total_accounts=5)`, 500 paths, seed
  20261117).
- **Interval**: e = mean P&L per trade ÷ realised dollars risked at the protective stop, net of costs; its one-sided
  95 % lower bound is the lower of (a) the 20-day moving-block bootstrap over the day set of §3, days without a trade
  included (`propedge.research.fv_score.block_lower_bound(day_sums, day_counts, block=20, reps=10000,
  seed=20261117)`) and (b) the normal approximation clustered by day
  (`propedge.backtest.metrics.normal_lower_bound(r, days)`, the standard error from daily means). This lower bound
  is the one the gate shifts the trades to.
- **Also reported**: trade and day counts; setups per market per day and, routed, per account per day under
  rotation, with the share of trades skipped because no account was flat (`share_trades_skipped_no_flat_account`);
  Combine purchases per year beside growth (D-34); hit rate
  and mean winner ÷ mean loser; realised per-trade sd against `assumed_sd`; share of trades ending at the trailing
  exit, the protective stop and the session close; cost drag as a fraction of dollars risked; the campaign at the
  point estimate and at 0 / 10 / 50 % denial; ruin probability, bankroll drawdown and payout latency beside growth;
  whether the old criterion (e >= 0.10, bound >= 0.05, propsim D-47) is met; the variant count; each market's e
  separately, descriptive only; the confirmation's months from 2025-10-01 on (the only ones the paper's reporting
  has not covered for ES) separately, descriptive only. The campaign's rules object is
  `propedge.campaign.payout_method.rules_for_method("aeropay")`, the verified ledger with the Aeropay fee; the D-148
  review sheet's sample seed is 20261117.

## 5. Pass / fail criteria

- **Pass**: the D-145 gate on the confirmation period (2024-05-10 .. 2026-08-31), run once: median log growth above
  zero at the lower bound of e, with everything in §4's primary metric applied and the protocol, accounts, bankroll
  and horizon of §3. `e`, its bound and the old criterion
  are reported beside it.
- **Fail**: anything else.
- **Kill lines on the development period (2009-06-01 .. 2019-12-31), applied before the confirmation is run**:
  1. **Setups per account per day below 1** (D-154 at $500), computed deterministically from the log itself: the
     development trades routed in their own order over five accounts that are always live, under D-159's
     flat-account rule (`TradeRouter` on a `ReplayTable` with the same five keys every day), divided by the number of
     development days (§3's day set) times five.
  2. **The D-145 gate failing on the development period**, as §4's primary metric.

  Either drops the model, and the confirmation period is not spent. **A rule violation in the trade audit** (D-148) is
  not a verdict on the model: it is a defect in the kit or the scorer, diagnosed under the failure protocol, fixed,
  and the development run repeated with the same seed; it is recorded, and the kill lines are read on the corrected
  run.
- **What a fail means for the project**: IM1 is dropped. No variant of it (another lookback, multiplier, market set,
  exit or filter) is tried under this registration; a changed rule is a new model card with its own variant count.

> A failed pre-registered check is **kept on record and diagnosed**, never rerun until it
> passes: terminal-state audit → stage decomposition → component test in isolation →
> replication with seeds fixed beforehand. See the failure protocol in `CLAUDE.md` and
> propsim D-40.

## 6. Seed

- **Seed**: 20261117
- Additional seeds: none; the bootstrap and every campaign path derive from it.

## 7. Variants

- Configurations already tried for this question: 0 (IM1 is new; `results/variants.jsonl` has no IM1 entry)
- Configurations this pre-registration will try: 1

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

---

## Outcome

*(Filled in after the run.)*

- **Date run**: not run; no kit was built and no data was read.
- **Result file(s)**: none.
- **Verdict**: withdrawn, not a result. Recorded here so the registration stays on record.
- **Numbers**: none.
- **Why withdrawn**: the operator found it contradicted stage one's lifecycle research: it took T5 2a's sizes for
  e >= 0.10 at an assumed edge of 0; it held one static funded size where stage one's day-one bet followed by small
  harvest trades earns far more at zero edge (`vendor/propsim/results_state_policy_xfa_allin.csv`); the paper's
  trailing exit set R, so no per-state geometry from stage one could apply (D-114); and its trade rate gave each
  account about one setup a day.
- **Decision taken**: D-161. The entry signal carries over to a new model card, IM2, whose stops, targets and sizes
  come from stage one's lifecycle by account state; it gets its own pre-registration.
