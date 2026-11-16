# P-05 — NQB1's one confirmation: NQ no-edge brackets on the held-back window

| field | value |
|---|---|
| **id** | P-05 |
| **date** | 2026-10-02 |
| **author** | stage-two session, for the operator (Ryan Resnick) |
| **task** | T14 item 9 (NQB1's confirmation, D-226, D-229); T5 (the stage's pre-registered out-of-sample test) |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after NQB1's card (`docs/candidates/cards/NQB1.md`) and its cheap screen (D-227), before any kit of the held-back window exists |
| **status** | registered |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 126720 |
| `development_period` | 2009-06-01 .. 2019-12-31 |
| `confirmation_period` | 2020-01-01 .. 2026-09-30 |
| `confirmation_tests_on_this_market` | 0 |
| `bonferroni_alpha` | not required: a held-out confirmation period is used |
| `assumed_sd` | 1.0 |
| `assumed_sd_source` | assumption: the Combine's bracket is 1:1, so a resolved trade is +1 or -1 in units of the stop and its sd is 1 up to the small open share; the funded leg's 2:1 bracket is wider (about 1.4); the development counts give both (`results/nq_noedge_campaign.csv`), and the verdict reports the realised values |
| `risk_denominator` | intended |
| `primary_metric` | median_log_growth |
| `data_period` | 2019-12-23 .. 2026-09-30 for the kit (the days before 2020-01-01 are warm-up and record nothing); the development counts already in the repository (R084, R085: 2009-05-25 .. 2019-12-31) are read by nothing new |
| `seed` | 20261213 |
| `model_card` | docs/candidates/cards/NQB1.md |
| `power_rr` | 1 |
| `power_effect` | 0.00 |
| `boot_len` | 252 |
| `required_trades_source` | assumed_sd fallback: the L5 curve gives the trades needed to find a planted positive edge, and this test looks for none -- it measures the resolution and cost of brackets whose edge is below zero by construction, and decides on the campaign at their lower bound |
| `required_trades` | not an edge search: each leg needs brackets in every calendar year of the window for the resolution rule, which the 13 slots a day supply (section 2) |
| `available_trades` | 45370 |
| `ledger_n` | 126721 |

**Multiplicity plan.** NQB1's setting was chosen on 2009-2019 counts from a grid whose product is k (the card's §4:
market, both legs' stops, decision times, Combines live, geometry, price scale), plus one first look on NQ outside it
(`prereg/models.yaml`, pool `pool-2026-10-02-nqb1`): N = 126,721. At one-sided 0.05/N the development gate is
unreachable by construction, and D-189 says what follows: "the confirmation window carries the decision, never a
smaller N". That window has never been read for NQ (D-107: no confirmation test on this market) and is read here once,
for one configuration fixed in advance; the decision is that single test at the registered one-sided 0.05, with no
selection on it (the gatekeeper's ruling on the first draft, recorded in D-230: D-189's 0.05/N binds verdicts read on
development data; the family-wise control on the window is D-107's cap of three per market). Each leg's bound at
0.05/N is reported beside the verdict, never as it. The development readings (D-226 to D-228) are exploratory and
reported beside the verdict, never as part of it.

**The two-leg gate's level.** Each leg is taken at its own one-sided 95 % bound and the gate needs the campaign to grow
at both; a false pass needs only one bound above its true value, so the gate's size is at most about 10 %, and nearer
5 % because the two legs' yearly edges move together. This is the reading D-227 used; it is written down here, not
tightened.

**Available brackets.** About 1,745 trading days in the window (development counted about 258 a year) x 13 slots x a
long and a short = 45,370 per leg, the `available_trades` above.

**Power, in years.** The bound's unit is the calendar year (the counts carry no days). The window gives seven yearly
blocks against development's eleven; at the same yearly spread the bound is about a third wider (the t quantiles and
the square root of 11/7), and D-228 called the development margin thin. A FAIL may therefore reflect the bound's width
rather than a changed market; the consequence stays as registered.

**No deflated Sharpe ratio**: the counts carry no daily series (D-120 lets only counts leave QuantConnect), so there is
no return series to deflate.

---

## 1. Question

Does NQB1 -- fixed-hour NQ brackets with no direction call, sized to stage one's zero-edge geometry, one Combine live,
five accounts rotated -- still make money inside Topstep's contract when its brackets' resolution and costs are
measured on the six and three-quarter years the development never touched? A yes makes it the stage's first candidate
to pass the D-145 gate out of sample, and the protocol comparison (T7) runs on it; a no ends NQB1 and the no-edge
contract route (T14), and the stage returns to finding an edge (T4), with the evidence on record.

## 2. Data period

- **Source**: QuantConnect minute futures through the manual-run route (D-81), run by the operator in the web editor,
  ingested by `scripts/ingest_rmap_run.py`. The kit is the resolution map's (D-214, D-215, version 3 with D-223's
  fix) with one change: it counts only the two registered brackets at the 13 registered slots
  (`propedge/data/rmap_kit.py` `BODY_CONFIRM`, `CONFIRM_RUN` R088-rmap-confirm-NQ-2026). Its integrity is the map's:
  HEAD's days, warm-up days, contract switches, lost contracts, late rolls, early closes, bad bars, days with no
  reference and the quote counts, and the parser's refusals (a missing END or HEAD, a chunk or cell counted twice, a
  cell outside the registered brackets, counts that disagree with HEAD); whether the run is usable is §5's single
  test (D-230), the kit's EXPECTED.md says the same.
- **Symbols and resolution**: NQ (standard contract's bars and quotes; MNQ's contract terms), one-minute bars,
  QuantConnect's contract universe with the kit's own volume roll (D-132, D-134).
- **In-sample / training period**: 2009-06-01 .. 2019-12-31 (D-144), already read (R084, R085); nothing more is read
  from it.
- **Out-of-sample / test period**: 2020-01-01 .. 2026-09-30, fixed now, run once: D-144's held-back window to the last
  complete month before this registration. Warm-up from 2019-12-23, which records nothing. Every calendar year 2020 to
  2026 counts for the resolution rule, 2026 a partial year as development's 2009 was.
- **Price level -- a change from D-226 and D-228, made before the window is read (D-230).** D-226 and D-228 described
  the confirmation as "read once, at actual prices". It reads NQ at today's price level instead: each day rescaled so
  its first bar's open maps to 30,600, exactly as the development reading that selected the setting (D-225). The price
  scale was a searched parameter (the card's §4) and today's level the selected value; at actual prices the test would
  be of a configuration never selected, with stops several times larger as a share of price in 2020-2023. It is also
  the friendlier choice for resolution, which is why the change is recorded in D-230 before any of the window is read.
- **Walk-forward scheme**: none; no parameter is estimated from the data.

> The test period is fixed here and not revisited. Extending it after seeing a result, or
> sliding it to a friendlier regime, converts an out-of-sample test into an in-sample one.

## 3. Rules fixed before the run

All of it is `config/nqb1_confirmation.yaml` (committed with D-229), which the kit, the parser, the ingest and the
verdict (`scripts/confirm_nqb1.py`) read; the verdict refuses to run if the config and the campaign code differ.

- **Entry**: at each of 13 decision slots of Topstep's trading day -- every hour from 17:00 to 22:00 CT and from 02:00
  to 08:00 CT -- a bracket at the open of the next one-minute bar, one micro tick adverse, long and short both counted.
  The live rule the counts stand for: each bracket's direction a coin flip from a seeded generator; on trading day d the
  five accounts, in the router's order j = 0..4, take slot (5d + j) mod 13, so every slot carries the same share of
  trades over 13 days (`config/nqb1_confirmation.yaml` `direction`, `slot_rotation`).
- **Exit / target**: the target at R x the stop -- 1R for the Combine's bracket, 2R for the funded account's -- reached
  only by a bar trading through it; a bar touching the stop and the target is the stop's, a bar opening through the
  stop is the stop's.
- **Stop**: $125 a micro for the Combine's bracket, $75 a micro for the funded account's, read at today's price level:
  each day's bars rescaled so the day's first bar's open maps to 30,600 (D-225, NQ's level of 30 September 2026).
- **Bracket R** (target ÷ stop), and the dollar risk per trade: Combine 1:1 at $1,500 (12 MNQ); funded static 2:1 at
  $750 (10 MNQ), stage one's zero-edge geometry (propsim D-08, D-10, D-15; D-150).
- **Session**, and the **15:10 CT flatten** handling: Topstep's trading day, 17:00 CT the evening before to the 15:10
  flatten (8284206); a bracket open at the day's last bar at or before 15:10 is flattened and counted open; days whose
  last bar ends before 15:00 CT are early closes, counted apart (D-215).
- **Instrument** and how the stop distance maps to **integer contracts**: MNQ, $2 a point; the stops divide each
  state's risk into whole micros exactly and sit under each state's size cap (`results/stop_band.csv`).
- **Fill model / cost profile**: `assumed` (`config/fills.yaml`; D-95): MNQ's published round turn, one tick adverse on
  entry, stop and flatten, none on a resting target; plus the entry minute's measured bid-ask spread beyond the tick
  the walk already charged (D-221's cost, `score_resolution_map.bracket_cost`). The slippage values are assumptions.
- **Parameters, with their exact values**: the above, and the campaign's: five accounts in total, at most one Combine
  live, a $5,000 bankroll, 504 days, 500 paths, verified rules with Aeropay, D-145's conduct model with the Responsible
  Trading Program at its strictest placement timing, payout denial 25 % (the gate) and 0 (beside it). A bracket open at
  the flatten counts as a full loss in the edge. Nothing is left to be chosen.
- **The campaign model and its limits** (`nq_noedge_campaign.campaign`): each account type draws stage one's binary
  process (`adapter.BinaryDraw`, through the engine's barrier race) at its own leg's pooled net edge -- the Combine
  accounts at the 1:1 leg's, the funded accounts at the 2:1 leg's -- not the measured sequence of trades, which the
  counts do not carry. Limits, stated: the same day's trades on different accounts are drawn independently although
  they share NQ's path (D-227); a stop that gaps through is charged as a stop plus one tick, the counts holding no
  prices (D-221); the pooled 13-slot edge assumes the trades spread evenly over the slots, which the slot rotation
  above makes so.

**Conduct check in D-145's three tiers** (`propedge/campaign/conduct.py` is the one source):

- Tier 1, hard — every box must be ticked, or the model is not a candidate:
  - [x] no cross-account hedging (each account trades its own slot; directions carry no information and are never paired across accounts to offset)
  - [x] no reliance on simulator fills (tight brackets, auto-breakeven, SIM-fill scalping) or fills outside the best
    bid or offer (stops of 37.5 and 62.5 NQ points; market entries at the next bar with a tick of slippage and the measured spread)
  - [x] no maximum size into major news; no coordinated trading
  - [x] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled: R at or below 1 (the Combine's 1:1) and several accounts at the MLL in one day apply; the simulator
  places the trader and applies the verified consequence ($1,000 DLL on later Combines, Consistency-path-only new
  funded accounts), placement lasting to the end of the campaign (D-219).
- Tier 3, priced: many Combine purchases and the breaches; payouts from accounts showing the pattern are denied with
  the stated probability; the gate uses 25 %.

## 4. Metrics

- **Primary**: the campaign's median log growth of the fee bankroll at 504 days, $5,000 start, with each leg's trade
  outcomes at the lower bound of its net edge (below).
- **Each leg's net edge** e, per trade, in units of intended risk: from the window's counts on every day (early closes
  included), a target pays R, a stop costs 1, a bracket open at the flatten counts as a full loss, less the cost above;
  pooled for the point, and per calendar year for the bound.
- **Interval**: the one-sided 95 % lower bound of each leg's e: the yearly estimates' mean less the t quantile at 0.95
  with (years - 1) degrees of freedom times their standard error. The counts carry no days, so no day bootstrap is
  possible; the yearly blocks are the bound's unit (`boot_len` 252 is that block, a year of sessions).
- **Resolution**: per leg, pooled over the 13 slots on full sessions, the share of brackets at their target or stop,
  overall and per calendar year.
- **Also reported**: the day count (HEAD's days) and each leg's brackets, target, stop and open shares, mean spread,
  cost and gross edge; each leg's **break-even hit rate** (the target share at which its net edge is nil, (1 + cost) /
  (1 + R), open brackets lost) beside its observed target share (D-201); each leg's bound at 0.05/N beside, never as,
  the verdict's; ruin probability, bankroll drawdown, days to the first payout, accounts funded, Combines bought, RTP
  placement; the point-estimate and denial-0 readings; the realised per-trade sd against `assumed_sd`; the variant
  count; whether the old criterion (e ≥ 0.10 and bound ≥ 0.05, propsim D-47) is met -- it cannot be, e being below
  zero.
- *(For a protocol comparison: **median log growth of the fee bankroll** is the primary ranking
  metric, per stated horizon and starting bankroll. IRR of dated cash flows is a secondary
  diagnostic, reported only where uniquely defined. Payout latency, ruin probability and
  bankroll drawdown are reported beside the growth number, never in an appendix.)*

## 5. Pass / fail criteria

- **Pass**: both of (1) each leg resolves at its target or stop on at least 98 % of its brackets overall and in every
  calendar year 2020 to 2026, a year with no brackets failing it (D-212), and (2) the D-145 gate, out of sample: the
  campaign's median log growth above zero
  with both legs' outcomes at the one-sided 95 % lower bound of their e, fees, payout latency and the tier-2
  consequences applied, and the tier-3 denial probability at 25 % (`scripts/confirm_nqb1.py`; `CHARTER.md` -- not at
  the point estimate, not a lower denial, not in sample). Always reported beside it: e and its bound per leg, and
  whether the old criterion is met.
- **Fail**: anything else, including two unusable runs.
- **An unusable run -- one test, one consequence, fixed now (D-230).** A run is unusable, judged from its log alone
  before any count is parsed (`rmap_parser.rmap_usability`), if END is missing, the log or the operator reports an
  error or a time limit, or HEAD's days fall below 1,600 (the window holds about 1,745; development counted about 258
  a year). The ingest then records it in `unusable.json` and never parses its counts, so no held-back count of an
  unusable run is ever read. **A usable log whose output the parser refuses** -- a chunk or cell counted twice or
  missing, emits or orders that disagree with HEAD, a malformed, out-of-range or unregistered cell, cell sums that
  disagree, no count cell -- **is unusable too** (D-231): recorded the same way, its counts not used, the parser's
  message carrying no cell. **A refusal of the procedure** -- files that are not this kit's output, a missing or
  mismatched download, the ran code -- is retried on the same backtest's own files and is never a new run. One fixed
  kit, R089-rmap-confirm-NQ-2026, may follow an unusable run: kit mechanics only, every rule in
  `config/nqb1_confirmation.yaml` unchanged, the fix recorded in a decision before it runs, and only after R088 is
  recorded unusable (`scripts/confirm_nqb1.py chosen_run` refuses otherwise). A second unusable run is a FAIL.
- **What a fail means for the project**: NQB1 is dropped; the no-edge contract route (T14) closes, its record complete;
  the stage returns to finding an edge (T4).
- **Whatever the verdict** (D-229's third safeguard, D-230): no later model and no T7 protocol arm takes its market,
  stops, decision times, R or Combines live from NQ's held-back counts; those are chosen on 2009-2019 only. On a pass,
  T7 compares protocols (payout policy, sizing, accounts) on NQB1's registered configuration; any arm that changes its
  market, stops, times, R or Combines live is a new model with its own confirmation (D-107: at most three on NQ's
  window).

> A failed pre-registered check is **kept on record and diagnosed**, never rerun until it
> passes: terminal-state audit → stage decomposition → component test in isolation →
> replication with seeds fixed beforehand. See the failure protocol in `CLAUDE.md` and
> propsim D-40.

## 6. Seed

- **Seed**: 20261213 -- part 1's and D-227's, so the confirmation's campaign shares its random numbers with the
  development reading and the two differ only by their inputs.
- Additional seeds: none.

Every simulation in this stage is seeded. A seed chosen after seeing a result is a variant.

## 7. Variants

- Configurations already tried for this question: 4 of the 95 records in `results/variants.jsonl` (from
  `VariantCounter`: `D-213:no_edge_contract` twice, `D-220:no_edge_concurrency`, `D-227:nq_noedge_campaign`); the map's
  grid is not in that file -- it is k above.
- Configurations this pre-registration will try: 1.

One configuration is tested on the held-back window; the choice among k happened on development data only.

## Addendum before the kit was generated (D-232)

Added 2026-10-02 after registration and before the kit existed, nothing of the window read; each item enforces or
completes §5, none changes a pass or fail rule. (1) A run recorded unusable is never ingested afterwards, whatever files
are given, and the verdict refuses a run that is both ingested and recorded unusable. (2) A `results.json` that cannot be
decoded is a procedure refusal: it is re-downloaded from the same backtest; if one re-download from that backtest still
cannot be decoded, the run is recorded unusable (`--declare-unreadable`), spending the one fixed kit. (3) The limit
input to the usability test (`--limit-hit`) repeats QuantConnect's own report verbatim, never a judgement.

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

---

## Outcome

*(Filled in after the run. Record it whether it passed or failed; then add the row to
`REGISTRY.md`.)*

- **Date run**: 2026-10-02, once: kit R088-rmap-confirm-NQ-2026, run by hand in the web editor (backtest
  24c448c584b8ae541efc07b16c17d635), usable by §5's single test -- END present, no error or limit, HEAD's days above the
  minimum. QuantConnect's NQ data ended on 2026-07-04, before the registered end (2026-09-30); 2026 is the partial year
  the registration counts. The output passed the parser's integrity checks; ingested under P-05 (a3f6da0).
- **Result file(s)**: `results/manual_R088_rmap_confirm_NQ_2026.csv` (the counts) and `results/nqb1_confirmation.csv`
  (the verdict: resolution, each leg's inputs per year and pooled, the four campaign readings), each with its
  manifest, the verdict written by `scripts/confirm_nqb1.py` from the clean tree at a3f6da0.
- **Verdict**: **FAIL** -- rule 1 met, rule 2 not met. Both legs resolve at their target or stop on more than the
  required share overall and in every year 2020 to 2026; the campaign at both legs' net-edge lower bounds with 25 %
  denial has median log growth below zero, so the D-145 gate fails. The old criterion is not met (e below zero).
- **Numbers**: in `results/nqb1_confirmation.csv` -- the `verdict` row (both rules, the gate's growth, each leg's bound,
  the day count, the break-even hit rates against the target shares, the bounds at 0.05/N beside), the `resolution`
  rows, the `inputs` rows and the `campaign` rows (the gate reading, and beside it the point estimates and denial 0).
- **Diagnosis, if failed**: the terminal state is a usable run whose output passed every integrity check, so the
  verdict is not a kit or engine artefact. Decomposed by stage, from the file: (1) resolution held -- the brackets
  resolve almost always, as the development reading at today's level said; (2) each leg's gross edge stays slightly
  below zero, as in development; (3) each leg's cost per trade is higher than in development, the measured spreads in
  the micro's ticks being wider over 2020-2026; (4) the bound rests on seven yearly blocks against eleven, as §1's
  power note warned. Net, both legs' lower bounds sit further below zero than in development, enough to turn the
  gate's growth negative; at the point estimates with 25 % denial the growth is barely above zero, and at denial 0 it is
  well above -- beside the verdict, never as it. An independent audit re-derives these numbers from the CSV (CLAUDE.md).
  The registered verdict stands; nothing is rerun or re-selected (the failure protocol).
- **Decision taken**: D-233 -- NQB1 is dropped; the no-edge contract route (T14) closes; the stage returns to finding
  an edge (T4). NQ's held-back counts are not used to design a later model (D-229); NQ's window has one of its three
  confirmation tests spent (D-107).
- **Superseded by the operator's rule, D-234 (2026-10-02):** the gate's denial probability is 0 %, as the operator had
  instructed before the run (D-213); this registration's 25 % pass rule was the author's error. The registered verdict
  above stays on record. Under the operator's rule, this registration's own pre-registered 0 % reading -- fixed here
  before the window was read, in the same result file -- meets both rules: NQB1 passes, and goes on to T7. The 25 %
  reading is reported beside every NQB1 result.
- **Audited, D-235 (2026-10-02):** every number of the registered verdict re-derives from the counts; the FAIL at the
  registered 25 % is sound and is P-05's confirmed result. **The pass under D-234's 0 % rule is EXPLORATORY**: the
  rule was set after both readings were known, on a window already read, so it cannot be confirmed here; a clean
  confirmation of NQB1 needs data no one has read (NQ after 2026-07-04). The audit's corrections to the diagnosis and
  its statement of the assumptions are in D-235 and `docs/audits/p05_nqb1_confirmation_2026-10-02.md`.
