# P-04 — IM2 (harvest at $300), with the fidelity audits' fixes: noise-band entries under stage one's lifecycle, ES, CL, 6E and NG, accounts rotated

| field | value |
|---|---|
| **id** | P-04 |
| **date** | 2026-09-27 |
| **author** | stage-two session, for the operator (Ryan Resnick) |
| **task** | T4 5p (the model) and T5 (its one confirmation test); T11 (the fidelity audits' fixes) |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after the model card and its screen, before any kit ran |
| **supersedes** | P-03, withdrawn before any run (D-172): the audits of 2026-09-27 found fills and rules its kits did not model |
| **status** | registered |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 4 |
| `development_period` | 2009-06-01 .. 2019-12-31 |
| `confirmation_period` | 2024-05-10 .. 2026-08-31 |
| `confirmation_tests_on_this_market` | 0 |
| `bonferroni_alpha` | not required: a held-out confirmation period is used |
| `assumed_sd` | 1.1 |
| `assumed_sd_source` | assumption: no IM2 trade exists yet; outcomes are brackets at 1:1 and 2:1 with time exits at the close, so the per-trade sd in units of the stop sits between the 1:1 binary value (about 1.0) and the 2:1 one (about 1.4); the development run measures it per R and reports it beside this value |
| `risk_denominator` | realised |
| `primary_metric` | median_log_growth |
| `data_period` | 2009-05-01 .. 2019-12-31 and 2024-04-01 .. 2026-08-31; nothing from 2020-01-01 .. 2024-03-31 is read |
| `seed` | 20261120 |
| `model_card` | docs/candidates/cards/IM2.md |

**Multiplicity plan.** Unchanged from P-03, whose text follows. The entry rule is the paper's (nothing searched). The
only choice is the funded policy, and four of stage one's were considered: its day-one all-in with harvest; static
2:1 $750; build 2:1 $1,000 then harvest 1:1 $150; the same with the harvest at $300. **How the choice was made, in
order:** the card first declared (commit 97b0ddd) a rule choosing between the all-in and static 2:1 $750 by s, the
share of 3:1 brackets resolving inside a session; the cheap screen (`results/im2_screen.csv`, a proxy on the
2009-2019 bracket map) put s far below stage one's 0.75, which rules the all-in out; that declared rule was then
**superseded**: stage one's build-then-harvest, which its results favour over static 2:1 $750, was added and chosen;
and the harvest moved from $150 to $300 because a $150 harvest win with whole micros and costs can never reach the
$150 winning day (D-163, a contract fact). Every step used development-period data or stage one's results, never the
confirmation window (D-13, D-147). So k = 4 are counted and one configuration is run; for its funded policy IM2 is a
rule chosen on data in D-49's sense, and the report says so. The development period applies the kill lines; the
confirmation period is run once and the pass line applied to that run alone.

**What P-04 changes from P-03, and why k is unchanged.** Two read-only audits of 2026-09-27
(`docs/audits/fill_cost_fidelity_2026-09-27.md`, `docs/audits/topstep_rule_fidelity_2026-09-27.md`) read no IM2 data:
no IM2 kit had run, and they drove the code with constructed bars. They found fills and rules P-03's kits did not
model. P-04 fixes those that bear on IM2's verdict before any IM2 bar is read: every resting order and fill on the
traded micro's tick grid; market orders in scheduled-release minutes filled at the bar's worst price, from a release
calendar; ES trades held within 2 % of the price lock limit flagged and treated; the verdict required at actual
prices as well as at the reference price, with the market's wait extended to the later of the two scales' 2:1 exits
so that one set of entries holds one position per market at either scale (the gatekeeper's first review of P-04
found that P-03's reference-only wait let two accounts hold one market at once at actual prices); the fee gate
enforced in code; a declared cost sensitivity for MCL and MNG reported beside the verdict. Two audit findings are
left as they were and stated in §3 (gapped stops fill at the open with no further tick; a trade liquidated at the RTP
daily loss limit settles at the limit, with no slippage). None changes the signal, the stop's definition, the
brackets, the sizes, the policy, the markets or the layout; the longer wait only drops signals, so no configuration
is added: k stays 4. Each change makes the test harder to pass or leaves it where it was; none was chosen by looking
at a result. The audits' price-lock example (the S&P 500's fall on 3-4 April 2025, inside the confirmation window)
is knowledge of market events, not of any IM2 result, and the rule it motivates can only lower IM2's outcome.

---

## 1. Question

Does IM2 -- the published noise-band entries on ES, CL, 6E and NG, every trade bracketed, sized and rationed per day by
stage one's lifecycle for the account that takes it, the trades rotated across five accounts -- make money inside the
Topstep contract out of sample, on the years after the entry rule was published, with fills and firm rules as the
audits of 2026-09-27 require? A yes makes it the stage's candidate for the protocol comparison (T7); a no drops it and
the search moves on, with the evidence on record.

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
- **Release calendar** (new in P-04): `config/im2_release_calendar.csv`, built by
  `scripts/build_im2_release_calendar.py` from `config/sources/` (read 2026-09-27; §3 "Release minutes").
- **In-sample / training period**: 2009-06-01 .. 2019-12-31 (D-144), preceded by a warm-up from 2009-05-01 that fills
  the 14-session lookback and records nothing. Nothing is fitted; the period measures the model for the kill lines.
- **Out-of-sample / test period**: 2024-05-10 .. 2026-08-31, fixed now, run once (D-49, see §1), preceded by a
  warm-up from 2024-04-01 that fills the lookback and records nothing. 2020-01-01 .. 2024-03-31 is not read.
- **Walk-forward scheme**: none; no parameter is estimated from the data.

> The test period is fixed here and not revisited. Extending it after seeing a result, or
> sliding it to a friendlier regime, converts an out-of-sample test into an in-sample one.

## 3. Rules fixed before the run

Everything below is the model card's (`docs/candidates/cards/IM2.md` §2 and §4, with IM1's card §4 for the shared
market rules), restated so the run can be checked against it, with P-04's changes marked **(P-04)**. The values are
in `config/model_im2.yaml`; the code is `propedge/outcomes/im2_core.py` (embedded verbatim in the kits R053-R060,
regenerated for P-04) and `propedge/research/im2_score.py`.

**Market rules, carried over unchanged from P-01 (reviewed five times, 2026-09-26):**

- **Price series**: raw prices of the contract actually traded -- QuantConnect's continuous future with open-interest
  mapping and RAW normalisation, the active contract tracked, as every kit here does. Each day is rescaled so its
  session open maps to the market's reference price for sizing (D-106's convention, as FV1 and the bracket map): ES
  4000 (FV1's; below ES's level in the confirmation years, which overstates its cost in R -- conservative), CL 70,
  6E 1.10, NG 3.00 (round levels). Signals are computed on raw prices; the rescale applies only to fills, costs and R.
  **(P-04)** The same entries are also walked at actual prices, and the verdict requires the gate at **both** scales
  (§4, §5): the rescale is conservative for ES but optimistic for NG below 3.00 and CL below 70 (fill audit, finding
  3).
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
  MNG 0.001. **(P-04) The tick grid** (fill audit, finding 6): every price an order rests at or fills at is on the
  traded micro's grid at the scale it is walked at (at the reference price, the same tick at the rescaled level). The
  stop and each target round away from the entry (the stop just beyond the band; a target at least R stop distances
  away); every fill rounds against the position (a buy up, a sell down). Entry and stop on the grid make the stop
  distance a whole number of ticks, so a target pays exactly R, and a target can never be credited at a price no
  resting order could hold. **(P-04) Release minutes** (fill audit, finding 1): in the minute of a scheduled release
  that Topstep names for the market (help.topstep.com 8284211: the FOMC statement, all four markets; EIA crude
  inventories, CL; EIA natural gas inventories, NG) and the minute after, a market order fills at the worst price the
  bar traded when that is worse than the fill above: an entry at the bar's high for a long (low for a short); a stop,
  touched or gapped through, at the bar's low for a long (high for a short); a time exit likewise. Targets are
  unchanged. The dates and minutes are `config/im2_release_calendar.csv`: FOMC statements from the Federal Reserve's
  calendar pages, at the time the statement page prints, else the Fed's notices of 2011-03-24 and 2013-03-13 (both
  12:30 and 2:15 p.m. ET flagged for the 2012 press-conference meetings, whose time no page read states); EIA crude from
  EIA's report archive (2011-08-03 on), a Wednesday at 9:30 CT and any other day at both 9:30 and 10:00 CT, and before
  the archive a declared rule (each Wednesday at 9:30 CT; in a week whose Monday, Tuesday or Wednesday is a federal
  holiday, also the Thursday at both 9:30 and 10:00 CT, and the Friday at both if the Thursday is a holiday); EIA
  natural gas every Thursday at 9:30 CT with EIA's listed 2025-2026 alternates (the Thursday they replace kept), and
  before 2025 a declared rule that flags every alternate day and time of EIA's schedule (Wednesday, Thursday and Friday
  at 11:00 CT, Wednesday and Friday at 9:30 CT, the next Monday at both) in any week with a federal holiday on a
  weekday. The rules over-flag; a flagged minute with no release costs the model a worse fill, never a better one
  (`propedge/data/im2_releases.py` is the complete statement). Releases Topstep does not list (the 10:00 ET releases
  at IM2's 09:00 CT decisions on all four markets, for instance) are not treated.
- **Not changed from P-03, stated (P-04):** a bar that opens through the stop fills at that open with no further tick
  (fill audit, finding 5: two other cores add one); a trade the Responsible Trading Program's daily loss limit
  liquidates settles at the limit with no slippage (fill audit, finding 7), which is optimistic for an account that
  survives the limit. The operator's fills are not measured (D-95).
- **Round turn per micro**, from the published Topstep schedule (help.topstep.com 8284213, `config/fills.yaml`,
  D-158): MES 1.22 and M6E 1.00; MCL and MNG at **the totals 8284213 states when re-read on or after 2026-10-01**, the
  day an announced CME exchange-fee rise of $0.10 per side takes effect on both, verified and recorded on the ledger by
  the rules-verifier. If the re-read still states no new totals, **MCL 1.72 and MNG 1.92** (the verified table
  figures plus the announced $0.20 a round turn), fixed now; loading them is recorded then in `config/fills.yaml` and
  `DECISIONS.md` as derived, not verified. Nothing is scored before that re-read is recorded. **(P-04)** The scorer
  enforces it: `im2_score.fees` refuses unless MCL and MNG carry a `date_read` on or after 2026-10-01 and stand at no
  less than 1.72 and 1.92 (fill audit, finding 4). If Topstep posts a total below its floor, the scorer still refuses:
  the posted total is recorded in `DECISIONS.md` and the floor lowered to it there before anything is scored. The
  rules-verifier's re-read on 2026-09-27 found the new totals not yet posted (D-170). Each trade's cost in R is one micro's round turn over one micro's risk at the stop, at each scale, and
  `trade_audit.im2_cost_checks` checks it on every entry. The micros' specifications (MES, MCL, M6E, MNG) are loaded
  from `config/instruments.yaml`, MNG's added by P-04.

**IM2's own rules:**

- **Entry**: at a decision time, with the market flat (see sequencing) -- on the close of the bar ending then, **long
  if the close is above both the upper band and VWAP, short if below both the lower band and VWAP** (the authors'
  published code, read 2026-09-26: `signals[(current_close_prices > UB) & (current_close_prices > vwap)] = 1`;
  `signals[(current_close_prices < LB) & (current_close_prices < vwap)] = -1`); otherwise no entry. The code also
  evaluates the open minute; the paper's text puts the first position 30 minutes after the open, and that is the rule
  here. The entry fills at the next bar's open, one tick adverse (a release minute: the rule above), on the grid.
- **Stop**: resting and continuous at the opposite band's level at the decision time (the decision bar's sigma and
  anchor) -- the paper's base-model stop -- **(P-04)** on the grid, rounded away from the entry. The stop distance is
  measured from the entry fill (after its tick) to the stop. An entry that fills at or beyond its own stop is not
  taken, and is counted. A bar that touches the stop fills there one tick adverse; a bar that opens through it fills at
  its open (a release minute: the rule above).
- **Targets**: resting limits at R x the stop distance beyond the entry fill, on the grid away from the entry, for
  **R = 1, 2 and 3**, each an independent bracket on the same entry and the same stop; when a bar touches both the stop
  and a target, the stop is taken first (conservative). Each bracket ends at its target, its stop, or the session
  close (one tick adverse). R = 1 and 2 are the lifecycle's; R = 3 is reported only.
- **Market sequencing -- no opposite positions across accounts (D-55)**: a market is busy from an entry until that
  entry's **2:1 bracket** ends (the longest bracket the lifecycle uses) **at both scales -- the later of the reference
  walk's and the actual walk's 2:1 exits (P-04)** -- then **5 minutes** (D-160, D-61's gap). **A decision at time T is
  taken only if T is at or after that exit plus 5 minutes; a signal at a decision time inside the wait is dropped, not
  delayed** -- entries happen only at decision times. A trade taken at 1:1 exits sooner on its account, but the market
  still waits, so no account can be handed the opposite side of a market while another account's bracket in it is
  open, at either scale. One position per market at a time; no flips. (P-03 waited for the reference walk's exit
  only; at actual prices, where the two walks' exits differ, that let a second entry in the same market open while
  the first was still held -- the gatekeeper's first review of P-04. An entry with no walk at actual prices waits for
  its reference exit.) `trade_audit.im2_checks` checks the wait against the later exit.
- **Time stamps for routing**: each entry's `entry_t` is the start minute of the bar its entry fills in; its `exit_t`
  is the end minute of the bar its **2:1 bracket** exits in at that scale (a stop inside a bar included), both minutes
  after midnight CT on one clock across the four markets; an exit and an entry in the same minute overlap. The market's
  wait (above) covers both scales' exits, so routing at either scale never puts one market on two accounts at once.
- **What the log carries**: **every entry the rules generate**, at one micro contract (as FV1's kits), each with its
  stop distance, its entry and exit times, and, for each R in 1, 2 and 3 and each scale, its outcome in R net of one
  micro's costs and its MAE in R before that bracket's exit (including the exit bar and a gap open) --
  `DayBlock.r_by_rr` and `mae_by_rr` (D-162); **(P-04)** also the lowest price while held (`mn`, from the entry bar
  through the later of the two scales' 2:1 exits) and each session's release minutes (`rel`). **e at each R, its lower
  bound and the kill lines are computed over every entry**, in R, so they do not depend on size. An entry with no walk
  at actual prices (through its stop there only) is absent from the actual-price blocks and counted.
- **(P-04) Holding within 2 % of the price lock limit** (Topstep 10296582 prohibits "Holding a position within 2% of
  a product's price lock limit"; its listed responses include "Deletion of the impacted trading day", "Permanent
  account closure" and "Delay or denial of a Payout request"; rule audit, finding 3). Topstep's own definition
  (8284225, read 2026-09-27): "Stop trading below: Settlement × (1 − Price Limit% + 2%)", with the example "With a 7%
  downside-only limit: Stop below: 2,814 × 0.95". Of IM2's markets only ES has such a fixed daily limit (its
  day-session downside limit, 7 %); CL, NG and 6E have CME's dynamic circuit breakers, not a lock. **Flag:** an ES
  entry whose lowest price while held (`mn`) is at or below the prior close x 0.95 (the prior close, the active
  contract's close at 15:00 CT, stands in for the settlement). The 7 % level is today's and is applied to every year;
  CME's earlier limits were not re-read (CME blocks automated reads), and if they were wider, as recalled, the
  development years are over-flagged, which only lowers IM2's outcome. **Treatment in the verdict:** a flagged entry's
  outcome at every R is the lower of its net outcome and minus its costs -- the gain on that trade is forfeited, any
  loss kept. This is a trade-level reading of "Deletion of the impacted trading day": the same account's other trades
  that day (other markets) are kept. **What the strategy does:** IM2 has no rule that exits before the threshold; the
  verdict prices the breach, it does not avoid it. The count of flagged entries and days is reported beside the
  verdict; permanent closure, the harshest listed response, is not modelled, and the report says so.
- **Routing (D-157, D-159, D-162)**: the four markets' entries form one stream in entry order (ties in the order ES,
  CL, 6E, NG). Each goes to the next account in turn that is **flat at its entry** and **below its state's trade limit
  for the session**, and is skipped, and counted, if none is. An account is busy until the entry's 2:1 `exit_t` even
  when it took the trade at 1:1, and a trade routed to an account counts against that account's limit even if its
  risk buys no contract there (routing comes before sizing). No account holds two positions at once, so the engine's
  one-after-another settlement of an account's trades is exact, and the per-trade cap is the account's cap.
- **The lifecycle -- each account's state sets its trade's R, dollar risk and trade limit** (stage one; the card §2),
  as the policy the engine runs (`propedge.campaign.risk_policy`, D-147, D-162; `im2_score.policy`):

  ```
  RiskPolicy(id="im2_s1_lifecycle", root=Phase(
      combine=Leaf("combine 1:1 $1,500", risk=1500, rr=1.0, max_trades=1),
      funded=Tiers(on="balance", name="funded", tiers=(
          (0,    Leaf("build 2:1 $1,000",  risk=1000, rr=2.0, max_trades=1)),
          (2000, Leaf("harvest 1:1 $300",  risk=300,  rr=1.0, max_trades=3))))))
  ```

  A funded account below +$2,000 builds at 2:1 $1,000, at or above it harvests at 1:1 $300, re-read at every session
  start (a payout that takes the balance below +$2,000 returns it to building); a paid account follows the funded
  rule. Sources: `vendor/propsim/results_state_policy_combine.csv` ("static 1:1 $1500 1/day");
  `vendor/propsim/results_state_policy_xfa.csv` ("build 2:1 $1000 -> harvest 1:1 $300 @B>=2000", which pays about as
  much as its $150 harvest, and "... harvest 1:1 $150 x3/day"); `vendor/propsim/results_state_policy_xfa_allin.csv`
  ("... harvest 1:1 $300 x3/day", three a day costing nothing against one). **Stage one never ran this exact
  combination** (build 2:1 $1,000, then harvest 1:1 $300 up to three a day): it is put together from those two
  comparisons, and the report says so. **Why $300, not $150 (D-163):** sized in whole micros, a $150 harvest risks
  $150 or less, so a single win net of costs is always below the Standard path's $150 winning-day minimum ("$150+ Net
  P&L", 8284233) and would not count toward a payout. At $300, with x the stop's risk per micro and c the round turn,
  realised risk floor(300 / x) x is above $150 for every x up to $300, and the net 1:1 win n (x - c) reaches $150
  except in two cases: one micro with x below 150 + c (about $151-152), or the harvest's cap of 37 micros with x below
  c + 150 / 37 (about $5-6, far below the noise band's stops). So one win clears the minimum on nearly every trade;
  D-163 put the first case as realised risk, and this is the precise statement. The share of harvest days that reach
  the minimum is reported.
- **Sizing**: `SizingRule` in `current_tier` mode with the declared headroom 0.75 (D-117): contracts = floor(the
  state's dollar risk / (stop distance in points x the micro's value per point)), capped at 75 % of the account's
  current scaling-tier allowance; a trade whose risk buys no contract on that account is not taken there, is counted
  (`share_trades_unsized`), and still occupied its routed account for its duration (conservative). The micros are MES,
  MCL, M6E and MNG on the standard contracts' price paths (D-106); M6E's tick is 0.0001 at $1.25, so its stops convert
  in points, never in 6E ticks. **(P-04) Not modelled, disclosed:** Topstep's temporary tighter limits on MCL during
  extreme volatility (13613539, read 2026-09-27 by the rules-verifier: a 50K Combine ceiling of 30 MCL, and a 50K XFA
  ladder for restricted symbols of 1 contract below a $2,000 balance and 3 from $2,000; whether "1 contract" means ten
  micros is unverified, and the restriction is temporary; D-171). The verdict sizes under the standard limits; the
  report gives the share of CL entries whose size in each state -- at that state's risk and cap (the Combine's 37
  micros; the build state's lowest XFA tier, 15; the harvest's 37) -- would exceed those caps, read as ten micros a
  contract.
- **Accounts**: **five in total, Combines and funded together** (D-34; the operator's plan of five accounts): five
  Combines at the start, a Combine bought only while the live total is below five; a pass always finds a funded slot,
  so the hold queue never arises and `hold_expiry_days` stays not required under D-34.
- **Protocol** (the engine's base legs; the policy above sets every trade; `im2_score.protocol`): Combine 1:1 $1,500,
  funded 2:1 $1,000; the Standard payout path; nothing kept back (`keep_balance` 0) and the full allowed payout
  requested (`payout_frac` 1.0, stage one's A5); the Aeropay method and its verified lag; the activation fee paid on
  activation; no resets; reinvestment on. Trade slots per day: the busiest day of the log being run, as the engine
  requires. The campaign's rules object is `propedge.campaign.payout_method.rules_for_method("aeropay")`. The engine is
  the repository's with the T11 engine fixes merged (D-173 to D-176: the RTP daily loss limit on funded accounts
  activated after placement and on Combines reset during it, the RTP path by the Combine's purchase day, a payout
  requested after 5:00 PM CT so the next trading day is the request day, and the multi-market layout guards, with the
  scorer declaring four markets), all recorded before any IM2 result exists. **The engine is pinned:** the development
  run's commit is recorded in its manifests, and the confirmation runs at that commit's engine unless a
  `DECISIONS.md` entry records a change in the firm's rules between the two.
- **Bankroll and horizon of the verdict**: $5,000 and 504 sessions. The operator's own bankrolls, when given
  (docs/HUMAN_INPUTS.md), are run beside the verdict as exploratory and never replace it.
- **Settlement (D-156)**: each trade settles from its MAE at the R it was taken at (`mae`).
- **Session, and the 15:10 CT flatten handling**: every bracket ends at its market's session close at the latest, at
  or before 15:00 CT; nothing is held overnight, and every session falls inside one Topstep trading day.
- **Parameters, with their exact values.** Lookback 14 sessions; volatility multiplier 1.0; decision interval 30
  minutes; decision times, sessions, reference prices and ticks as above; brackets at 1, 2 and 3 R on the opposite-band
  stop; market wait until the 2:1 bracket ends at both scales plus 5 minutes; the lifecycle policy above; headroom 0.75; five accounts
  in total; **(P-04)** the release window 2 minutes (the release minute and the next); the ES lock flag at the prior
  close x (1 - 0.07 + 0.02); the cost sensitivity at 2 extra ticks a round trip on MCL and MNG. None is left to be
  chosen.

**Conduct check in D-145's three tiers** (`propedge/campaign/conduct.py` is the one source):

- Tier 1, hard — every box must be ticked, or the model is not a candidate:
  - [x] no cross-account hedging (one position per market at a time; a market waits until its longest bracket ends at
    both scales plus 5 minutes before any new entry, so at either scale no two accounts hold opposite positions in one
    market even briefly, D-55, D-160; D-55's correlated groups are the declared ones in
    `config/candidate_constraints.yaml`, where equity index, crude, euro and natural gas are four separate groups, one
    market each here; the scorer refuses a gate row run without flat routing)
  - [x] no reliance on simulator fills (half-hourly decisions; stops at the opposite band, far from the entry; no
    auto-breakeven) or fills outside the best bid or offer; **(P-04)** release-minute market orders are priced at the
    worst price the minute traded, and every order sits on the tick grid
  - [x] no maximum size into major news: sizes are set by the state's dollar risk and capped at 75 % of the tier
    allowance, never the maximum; disclosed: CL and NG can enter at the 09:30 CT decision on EIA inventory and
    storage-report days, all four markets at 13:00 CT on FOMC days (the release minute) and at 11:30 CT on the
    2011-2012 press-conference FOMC days (both priced by the release rule), and all four at 09:00 CT with 10:00 ET
    releases Topstep does not list (not priced); Topstep "doesn't require you to flatten positions during economic
    releases" (8284211); no coordinated trading
  - Disclosed, not a box the strategy ticks by itself: holding within 2 % of a price lock limit (10296582). IM2 has no
    rule that avoids it; the verdict flags ES trades that breach it and forfeits their gains (§3), as D-170 allows a
    model's registration to do; the rule is enforced case by case and its harshest response, permanent closure, is
    not modelled
  - Disclosed: the open question on the asterisk the help centre puts on micro contracts (D-62,
    `docs/HUMAN_INPUTS.md`) applies to all four micros used here
  - Disclosed for the record (D-160): rotation puts sequential trades in one market on different accounts, which can
    be on opposite sides within a day; never at the same time, and with 5 minutes flat between them
  - [x] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled: the 1:1 Combine and harvest brackets are R at or below 1 (a trigger); the build risk, $1,000, is
  exactly half the funded drawdown, not above it; maximum position on most trades cannot fire, since sizes are capped
  at 75 % of the allowance; several accounts at the MLL in one day is less likely under rotation. RTP placement puts a
  $1,000 daily loss limit on later Combines and XFAs (13620045), below the $1,500 Combine risk; those trades settle
  from their MAE (D-156). The simulator applies any consequence (the RTP daily loss limit and the Consistency path).
- Tier 3, priced: many Combine purchases -- priced at 25 % denial by the gate.

## 4. Metrics

Exactly what will be computed, and from what (`scripts/score_im2.py`, `propedge/research/im2_score.py`):

- **Primary, at each scale** -- the reference price (D-106) and **(P-04)** actual prices: the D-145 gate -- the
  campaign's median log growth of the fee bankroll per year, with each R's trade outcomes shifted down to that R's
  one-sided 95 % lower bound of e, fees, payout latency and tier-2 consequences applied, 25 % tier-3 denial, the
  lifecycle policy, rotation across five accounts in total, MAE settlement, the protocol and sizing of §3
  (`propedge.campaign.gate.run_gate(mode="rotation", combines=5, accounts=5, total_accounts=5, risk_policy=<§3's
  policy>, e_by_rr={1: e_1, 2: e_2}, lb_by_rr={1: lb_1, 2: lb_2}, e=e_2, lb=lb_2, settlement="mae")`, the gate's day
  blocks carrying the outcomes and MAE at R = 1 and 2 only (R = 3 is reported, not run: no state uses it), their base
  P&L the 2:1 outcome, 500 paths, seed 20261120), on the verdict's outcomes: net of costs, the price-lock treatment
  applied (`v`).
- **Disclosed with the verdict**: `assumed_sd` (1.1) is a frictionless figure between the 1:1 and 2:1 binaries and
  will understate a real log's sd; the realised sd per R is reported beside it.
- **Interval**, for each R in 1 and 2 and each scale: e_R = the mean of the per-entry outcome in R at that bracket,
  net of costs, the price-lock treatment applied, over every entry (the mean of per-trade R, as
  `propedge.backtest.metrics.estimate_edge` computes it); its one-sided 95 % lower bound lb_R is the lower of (a) the
  20-day moving-block bootstrap over the day set of §3, days without an entry included
  (`propedge.research.fv_score.block_lower_bound(day_sums, day_counts, block=20, reps=10000, seed=20261120)`) and (b)
  the normal approximation clustered by day (`propedge.backtest.metrics.normal_lower_bound(r, days)`).
- **Reported beside the verdict, never instead of it (P-04):** the gate at each scale with the MCL/MNG cost
  sensitivity (`w`: 2 extra ticks a round trip on MCL and MNG trades, fill audit finding 2); e and its bound before the
  price-lock treatment (`u`); the counts of entries in release minutes, 2:1 exits in release minutes, entries through
  their stop at actual prices only, and ES entries and days flagged by the price-lock rule; the share of CL entries
  whose size would exceed Topstep's temporary MCL caps (§3 "Sizing").
- **Also reported**: entry and day counts; per market, sessions traded, scheduled full sessions skipped by reason,
  late opens (record only) and scheduled sessions with no data; entries per market per day; release-minute exits at
  each scale; trades per account per trading day in the Combine and funded (the gate rows), with the
  shares skipped because no account was flat or below its limit (`share_trades_skipped_no_flat_account`) and unsized
  at their state's risk (`share_trades_unsized`); the share of funded accounts the Responsible Trading Program put on
  the Consistency path (D-174); the median trading days for a Combine to resolve (kill line 1) with
  the counts of passed, failed, abandoned and open Combines; Combine purchases beside growth (D-34); at each R, the
  hit rate, the share ending at the stop, the target and the close, and e_3 with its bound (reported only); realised
  per-trade sd at R = 1 and at R = 2 against `assumed_sd`; cost drag in R; the share of days with an entry on which one
  account harvesting at 1:1 $300 with up to three of the day's entries would reach the $150 winning-day minimum (from
  the log); the share of paths on which the Responsible Trading Program placement applies; the campaign at the point
  estimate and at 0 / 10 / 50 % denial; ruin probability, bankroll drawdown and payout latency beside growth; whether
  the old criterion (e >= 0.10, bound >= 0.05, propsim D-47) is met at R = 1 and at R = 2; the variant count; each
  market's e separately, descriptive only; the confirmation's months from 2025-10-01 on separately, descriptive only;
  the D-148 review sheet's sample seed is 20261120.
- **Files**: `results/im2_development_audit.csv`, `results/im2_development_edge.csv`,
  `results/im2_development_gate.csv`, `results/im2_development_verdict.csv`, `results/im2_development_review.csv`,
  each with its manifest. The confirmation's kits and its scoring entry (the same files named `confirmation`, with its
  months from 2025-10-01 reported separately) are built only after the development kill lines pass, from the same
  code with the confirmation period's dates and no change to any rule.
- **Sources the scoring relies on that are not `config/rules.yaml` entries** (recorded in `RULES_LEDGER.md` and
  D-170, D-171): 8284211's release list, 8284225's price-limit definition, 13613539's temporary MCL limits (its
  reading of "1 contract" unverified); and the MCL and MNG totals, which the scorer waits for.

## 5. Pass / fail criteria

- **Pass**: the D-145 gate on the confirmation period (2024-05-10 .. 2026-08-31), run once, **at both scales (P-04)**:
  median log growth above zero with each R at its lower bound, with everything in §4's primary metric applied and the
  policy, protocol, accounts, bankroll and horizon of §3, at the reference price **and** at actual prices. e, its bound
  and the old criterion at each R and scale are reported beside it, and so is the cost sensitivity.
- **Fail**: anything else, including a pass at one scale only.
- **Kill lines on the development period (2009-06-01 .. 2019-12-31), applied before the confirmation is run, at each
  scale (P-04)**:
  1. **D-154's rule fails**: in the development gate row (the lower-bound run at 25 % denial, §4's primary metric on
     development data), the median of `CombineRecord.days` over every **resolved** Combine in its 500 paths -- passed,
     failed, or abandoned because the next subscription was unaffordable (`propedge/campaign/lockstep.py`; each has
     `resolved_on` set), abandoned ones at their own `days` -- exceeds one billing period (21 trading days): the
     typical Combine would roll into a new subscription for want of setups. Combines still open at the horizon are
     left out of the median and counted beside it; the counts of passed, failed and abandoned are reported. If no
     Combine resolves at all, the median is undefined and the line counts as failed.
  2. **The D-145 gate fails on the development period**, as §4's primary metric.

  Either line at either scale drops the model, and the confirmation period is not spent. **A rule violation in the
  trade audit** (D-148: `trade_audit.im2_checks` at both scales and `im2_cost_checks`) is not a verdict on the model:
  it is a defect in the kit or the scorer, diagnosed under the failure protocol, fixed, and the development run
  repeated with the same seed; the readings before the fix stay on record, and the kill lines are read on the
  corrected run.
- **What a fail means for the project**: IM2 is dropped. No variant of it (another lookback, multiplier, market set,
  stop, bracket, lifecycle policy, filter, release rule or scale) is tried under this registration; a changed rule is
  a new model card with its own variant count.

> A failed pre-registered check is **kept on record and diagnosed**, never rerun until it
> passes: terminal-state audit → stage decomposition → component test in isolation →
> replication with seeds fixed beforehand. See the failure protocol in `CLAUDE.md` and
> propsim D-40.

## 6. Seed

- **Seed**: 20261120
- Additional seeds: none; the bootstrap and every campaign path derive from it.

## 7. Variants

- Configurations already tried for this question: none run. IM1 was registered as P-01 and withdrawn before any run
  (D-161); IM2 was registered as P-02 and withdrawn before any run (D-163), and as P-03 and withdrawn before any run
  (D-172); the IM2 screen (`results/variants.jsonl`, `IM2:screen`) read proxy data only.
- Configurations this pre-registration will try: 1, chosen from k = 4 funded policies before registration (the
  multiplicity plan above).

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

---

## Outcome

*(Filled in after the run. Record it whether it passed or failed; then add the row to
`REGISTRY.md`.)*

- **Date run**: 2026-09-30, the development period only (the confirmation is not run: a kill line fired). Fees at
  D-209's re-read (P-04 §3's derived floors); L3 and L5 passed against the same engine pin.
- **Result file(s)**: `results/im2_development_audit.csv`, `im2_development_edge.csv`, `im2_development_gate.csv`,
  `im2_development_verdict.csv`, `im2_development_review.csv`, each with its manifest, written from a clean tree at
  bd84868; beside them, reported only: `im2_development_breakeven.csv` (D-201) and `im2_development_haircut.csv`
  (D-189, D-208).
- **Verdict**: FAIL -- kill line 2 (the D-145 gate fails on development data) at the reference price and at actual
  prices; kill line 1 holds at both. The same verdict without the entries untradable as micros and without every
  entry on a micro expiry day (D-198, D-199).
- **Numbers**: in the result files above -- `im2_development_verdict.csv` (both kill lines per scale),
  `im2_development_gate.csv` (the gate row and the rows beside it), `im2_development_edge.csv` (e and its bound per R
  and scale, all markets and each market alone). None is typed here.
- **Diagnosis, if failed**: the failure protocol, in D-210: the campaigns' terminal states follow from a negative
  edge per trade, which holds at the point estimate as well as at the bound; the decomposition puts the fail at the
  trade, before the contract and before costs, in every market; the rule audit, L3, L5 and the second
  implementation's session-by-session match on ES, CL and NG rule out a scorer, engine or kit error. A real negative
  result.
- **Decision taken**: D-210 -- IM2 is dropped; no variant is tried under this registration (§5); the confirmation
  window stays unspent; the 6E cross-check and the chart review, which gated only the confirmation, close unneeded.
