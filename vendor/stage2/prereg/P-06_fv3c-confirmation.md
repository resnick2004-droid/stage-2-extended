# P-06 -- FV3-C's one confirmation: the corrected FV3 campaign on NQ's held-back window

> Written 2026-10-13 after the operator approved FV3-C's confirmation (D-355: "Ok if you think it is best to use that
> for the next run then I agree") and after its machinery was built and tested (46951b2) and its card committed; before
> any kit of the held-back window exists. Everything it fixes is `config/fv3_confirmation.yaml`; nothing here reads the
> window. It supersedes the 2026-10-10 draft for frozen FV3: the candidate is FV3-C (D-353, D-354).

| field | value |
|---|---|
| **id** | P-06 *(assigned by the prereg-gatekeeper, 2026-10-13)* |
| **date** | 2026-10-13 |
| **author** | stage-two session, for the operator (Ryan Resnick) |
| **task** | T18 item 7 (c): the one-shot confirmation on the held-back window (D-237, D-311, D-312, D-338 (1), D-353); T5 (the stage's pre-registered out-of-sample test) |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after FV3's card, the frozen candidate's record (runs v11-v13, D-336, D-352), the two-stream candidate's closure (D-350, D-353) and FV3-C's development verdict (run fv3_corrected_v1, D-354: CONTINUE by P1-P4, audited); before any kit of the held-back window exists |
| **status** | registered |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 1 |
| `development_period` | 2009-06-01 .. 2025-06-30 (the screen; the candidate's declaration on 2020-01-01 .. 2025-06-30, today's regime) |
| `confirmation_period` | 2025-07-01 .. 2026-09-30, or the end of QuantConnect's NQ data if earlier (D-237) |
| `confirmation_tests_on_this_market` | 1 (P-05, NQB1; this is NQ's second of D-107's three) |
| `bonferroni_alpha` | not required: a held-out confirmation period is used |
| `assumed_sd` | 1.209709 |
| `assumed_sd_source` | measured on development data: the sample standard deviation of `r_net_1.5` over the 4,017 development gate trades of run fv3_corrected_v1 (2021-01-03 .. 2025-06-29), the net outcome at the fresh Combine's 1.5R in units of intended risk, read from `results/fv3_studio_corrected_v1_point_trades.csv` (its manifest verified; D-354's export of the run's point arm); the realised value on the window reported beside the verdict (`realised_sd_combine_rr`) |
| `risk_denominator` | intended -- the allowance-capped intention at the rung's fixed stop (D-306, D-312 (1)); realised equals it to the dollar by construction, which C4 checks |
| `primary_metric` | median_log_growth -- the median path's growth on the bankroll the run itself needed (p90 across paths plus the margin), a year's rate (D-312 (3)) |
| `data_period` | 2025-05-12 .. 2026-09-30 for the three kits (the days before each period's start are warm-up and record nothing); nothing new reads the development files -- the frozen config and the frozen state table only |
| `seed` | 20261019 (the gate's seed of the development declaration; common random numbers with run fv3_corrected_v1's reading); eras 20261017, stops 20261018, spa 20261020 as the config, where they run |
| `model_card` | docs/candidates/cards/FV3-C.md |
| `power_rr` | 1.5 (the fresh Combine's R under the v12 table at the gate's edge cell) |
| `power_effect` | 0.025 (the card's `edge_assumed`) |
| `boot_len` | 21 (the bound's block: 21 sessions, a trading month -- D-237 (4): the window is too short for yearly blocks) |
| `required_trades_source` | assumed_sd fallback: the L5 power curve tabulates R 1 and 2 at a bootstrap length of 20 sessions; the fresh Combine trades at 1.5R and this registration's block is 21 sessions, so the curve does not apply |
| `required_trades` | 14,476 -- ((z(0.95) + z(0.80)) x assumed_sd / 0.025)^2, the normal approximation at one-sided 5 % with power 0.80 for e = 0.025; the window cannot supply it (the power note below) |
| `available_trades` | 1,057 -- the development rate, 4,017 gate trades over 1,083 sessions (`results/fv3_studio_corrected_v1_point_trades.csv` and `_days.csv`), times about 285 sessions (946 at 255 sessions if QuantConnect's data ends 2026-07-04, 1,168 at 315 if it reaches 2026-09-30); the firm's rule refuses about one signal in a hundred before routing (D-354), not a kept trade |
| `ledger_n` | 183 -- `propedge.research.ledger.count_n` on `prereg/models.yaml` for FV3-C, pool `pool-2026-10-05-fv3`, NQ, minute, 2009-06-01 .. 2025-06-30: k 1, FV1's NQ rows 4 + 1 + 1 (D-208: the extension and the campaign gate re-measures counted once each), FV2's grid 96, FV3's screen 32 and its corrected re-score 32, the cell's eleven development runs, the two-stream candidate's two runs, the minute flip map 1 and the seconds flip map 2; FV3-C's own run covered by its k (the gatekeeper recounts it) |

**Multiplicity plan.** The candidate was chosen and reshaped on development data only: FV3's screen (k 32, killed by W1,
D-298), its corrected re-score (D-303), eleven declared development runs of one cell under the fidelity protocol (D-306 to
D-352, each followed by a protocol change or a defect's fix recorded before the next run), the two-stream candidate's two
runs (D-339 to D-350, closed) and FV3-C's one (D-353, D-354). At one-sided 0.05/N the development gate is unreachable by
construction, and D-189 says what follows: the confirmation window carries the decision, never a smaller N. The window is
read here once, for one configuration frozen in advance; the decision is the single test at the registered one-sided 0.05
with no selection on it (the gatekeeper's ruling on P-05, D-230). Each leg's bound at 0.05/N is reported beside the
verdict, never as it. The development readings are exploratory and reported beside, never as part of the verdict.

**The gate's level.** The gate needs the campaign to grow with the trade outcomes shifted to the one-sided 95 % lower bound
of e at the funded leg's R, through the frozen state table; the campaign's growth is read on its required bankroll at p90
across 500 seeded paths. The level is the bound's.

**Available trades and blocks.** About 255 sessions if QuantConnect's data still ends on 2026-07-04, 315 if it reaches
2026-09-30; at the development rate about 950 to 1,170 kept trades at 1.5R; 12 to 15 blocks of 21 sessions for the bound.

**Power, stated before the read.** The required count above is beyond the window by an order of magnitude; the bound over
12 to 15 blocks is wide. A FAIL may reflect the bound's width rather than a changed market; the consequence stays as
registered. P-05 carried the same warning (seven yearly blocks against eleven) and failed on it. The point-estimate reading
is reported beside the verdict, never as it. Every development reading says the campaign's money is the contract's shape,
not the trades' edge (every e and bound negative; D-47 met at no R; the zero-edge twin richer on 87.6 % of paths): a PASS
would carry that reading with it, not overturn it.

**Deflated Sharpe.** Reported beside the lines, never as them: `propedge.research.haircut.deflated_sharpe` of the funded
leg's 21-session block means (its net outcome at 3R) at the ledger's trial count N, and the campaign Sharpe's own
deflated reading per path from the portfolio measures (D-304).

**The audit is symmetric (D-355 (5)).** Whatever the verdict, the opus auditor re-derives it from the result files without
the producing code; a defect it finds re-runs the verdict only where the code contradicts the config or this
registration, the fix changing no rule.

---

## 1. Question

Does the corrected FV3 campaign -- JJ Simon's triggers on NQ, break-of-structure only, in the AM, 6 PM and Asian sessions
with continuation on and the double rung on reversions, sized by the state table v12 at the full allowance under the
fidelity protocol (need-aware exits, the Combine's room and consistency caps, routing to accounts that can take the trade,
each trade's own cost, an abandon taken at the close that decides it), five accounts rotated under the firm's two rules
(no signal routed against a position open on another account, each position held to its own exit; a funded seat refilled
the evening an account ends) -- still grow a campaign's cash on Topstep's contract when its trades' outcomes are shifted to
their lower bound on the twelve to fifteen months held back from every FV3 reading? (The window is not untouched: P-05
read NQB1's bracket counts on 2025-07-01 .. 2026-07-04, D-237 (3); none of FV3-C's cells, triggers or outcomes has been
read on it.) A yes carries the campaign as frozen (FV3-C at c561ec9)
to the pre-deployment protocol (D-337: a shadow period with acceptance criteria fixed in advance, a kill rule, rules
re-verified on the day, sizing from the lower bound, one Combine first) with the reading that the money is the contract's
shape; a no closes FV3-C, the fair-value family's last candidate on this effect, and the stage returns to finding an edge or
closes at exit (B), with the evidence on record.

## 2. Data period

- **Source**: QuantConnect minute futures through the manual-run route (D-81), run by the operator in the web editor,
  ingested by `scripts/ingest_fv3_run.py` (which reads a kit's `confirm` flag and applies D-230's rules). The kits are FV3's capture (`propedge/data/fv3_kit.py`, the
  body and cores of R117-R136 unchanged; only the window, the class name and the embedded registration id differ), one per
  period: R139-fv3-confirm-NQ-25H2 (warm-up from 2025-05-12; 2025-07-01 to 2025-12-31), R140-fv3-confirm-NQ-26H1 (from
  2025-11-10; 2026-01-01 to 2026-06-30), R141-fv3-confirm-NQ-26Q3 (from 2026-05-11; 2026-07-01 to 2026-09-30). Each
  records every session from its period's start: the day (its ATR), the sessions, every trigger his rules allow with its
  attributes, outcomes at the R menu with the true adverse excursion, and the benchmark slots -- as the development
  captures. Only the records leave (D-120). The day set and each day's ATR are the kit's own; the development ingest's
  cross-check against an ORB3 run (D-265) does not apply, there being none after 2025-06-30, and is recorded as skipped.
- **Symbols and resolution**: NQ, one-minute bars at actual prices (the fidelity protocol's fixed point stops, D-306),
  QuantConnect's contract universe with the kit's own volume roll (D-132, D-134).
- **In-sample / training period**: 2009-06-01 .. 2025-06-30 (D-237), already read; nothing more is read from it.
- **Out-of-sample / test period**: 2025-07-01 .. 2026-09-30, or QuantConnect's data end if earlier, fixed now, read once.
  **Periods**: 2025 H2, 2026 H1, 2026 Q3. A period is COUNTED when its capture holds at least 40 days with a capture
  record, FOMC days out (`period_min_days`; the kit records full sessions only, an early close carries no record, so these
  are full sessions -- the config's wording and `confirm_fv3.load_window`'s count are the same thing, D-356). An uncounted
  period's trades still join C1's pool and its figures are reported beside; C2 and C4's per-period conditions run on the
  counted periods. At least two counted periods are required, else the test is FAIL (the window cannot be re-read).
- **The order, fixed now (D-356)**: no run is timed after any part of the window has been read. The operator runs the
  three kits (in any order); each run is judged completely -- its log, the parser on its output in memory, its days inside
  the period -- before any period's records are saved: `scripts/ingest_fv3_run.py --usability-only` writes
  `runs/<run>/usable.json` and saves nothing, and the ingest that saves records refuses until every period has a run
  judged usable (and refuses outright once a period is unusable twice). A fix kit therefore runs before any record of
  the window is saved. **2026 Q3 ends** at 2026-09-30 or at QuantConnect's last day of NQ data on the day its kit (or its
  fix) runs, whichever is earlier -- a date no record of the window can have informed. **The records saved for a period
  are those of the backtest judged usable**, identified by its backtest id and the sha256 of its downloaded log and
  results (`usable.json`); the saving ingest refuses any other backtest or files, and the verdict refuses a period whose
  saved run is not the one judged. The freeze pins the kits' generator, the parser and the ingest beside the engine.
- **Walk-forward scheme**: none; no parameter is estimated from the data. The cell is the one
  `config/fv3_corrected_portfolio.yaml` declares (`search`: sessions am + eve + asia; continuation on; displacement off;
  the double rung on reversions), frozen.
- **Integrity**: the parser's refusals as the development captures' (a missing END or HEAD, chunks that do not add up,
  malformed records, sessions that disagree with HEAD); whether a run is usable is section 5's single test.

> The test period is fixed here and not revisited. Extending it after seeing a result, or sliding it to a friendlier
> regime, converts an out-of-sample test into an in-sample one.

## 3. Rules fixed before the run

All of it is `config/fv3_confirmation.yaml` and the frozen inputs it names by sha256 (`config/fv3_confirmation_frozen.json`,
written by `python scripts/confirm_fv3.py --freeze` after registration, once 2026's release days are on record and before
any kit is generated; it refuses an unregistered id, a config without `ledger_n` and `assumed_sd`, and an engine that
differs from c561ec9): `config/fv3_corrected_portfolio.yaml` as run fv3_corrected_v1 ran it (D-353; FV3-C frozen at
c561ec9, D-354), `results/state_policy_v12.csv` and `results/state_policy_v12_policies.json` (the v10 solve, export
version 12), `config/fills.yaml`, `config/rules.yaml`, and the engine at the freeze commit c561ec9. The verdict
(`scripts/confirm_fv3.py`) refuses to run if any has changed; any engine change before the run needs an identity re-run of
FV3-C on record first (the fv3_corrected_v1 audit, finding 4).

- **Entry**: his triggers as the card and `propedge/outcomes/fv3_core.py` state them -- fair price at the session open
  with his re-anchoring (the 6 PM gap, Asia to 6 PM, the consolidation after a break and continuation, the 08:30 ET
  release candle on BLS release days); a break of structure toward fair price (reversion) or in the opening candle's
  direction within its first five minutes (continuation); displacement entries off; after two losses in a session,
  break of structure only; sessions the 6 PM reopen, the Asian open and the NY AM (the PM off); FOMC days out. Executed by
  hand two minutes after the signal bar's close, filled at the next bar's open with the spread and a tick charged (D-282).
- **Exit / target**: each leg's bracket at the table's R for its state; the Combine's trade closes at what the account
  needs to pass or at the day's consistency allowance (need-aware exits, D-306; the consistency cap, D-313); breakeven at
  the next session's open when the open is in the trade's favour; everything flat at the 15:08 CT close (D-263).
- **Stop**: his ladder in points, fixed -- 12.5 on 15-30 points of room, 25 at 30 and over, 50 on a continuation off an
  opening candle above 25 points and on reversions with 76 points or more of room (the double rung); room at least 0.8 x
  the target and at least 15 points; the stop judged on the true adverse excursion (MAE settlement, D-289).
- **Bracket R and dollar risk**: by account state from the state table v12 at the edge cell nearest the funded leg's
  block bound (never a cell chosen by hand); fresh Combine $2,000 at 1.5R, fresh XFA $2,000 at 3R at the -0.05 cell; the
  Combine never risks more than its room above the floor (the room cap) and ends out of room when no stop fits; the
  funded table under the $5 tie-break toward the smaller risk and the $500 cap once in profit (D-325), the abandon
  action in both tables worth zero at the derived slot rent (D-329 to D-331), taken at the close that decides it (D-334).
- **The firm's two rules, enforced in the engine (D-353):** no signal is routed to any account while a position of the
  opposite side is open on another (13747047, 10296582; D-336 (iv)), a routed position held to its exit at the R its
  account trades (D-349, D-351), a refused signal counted (`share_trades_skipped_opposite`); the engine's clock: a
  position held to t_end is flat at t_end (D-354). A funded seat is freed at the close the account ends and the waiting
  pass activates that evening (8284215, 8284217; D-336 (i)) -- the favourable end of what the help centre states, so
  optimistic by up to a session per funded ending. **By hand, the operator applies the same rule: never a position
  opposite to one open on another account.**
- **Session, and the 15:10 CT flatten handling**: Topstep's trading day; a trade open at the firm's forced close is
  flattened at the worst of 15:07-15:10 CT less two ticks; the flatten share is C4's condition.
- **Instrument and contracts**: NQ minis where ten micros fit, MNQ micros otherwise; whole contracts at the rung's fixed
  stop, risk / (stop ticks x $0.50), capped by the full verified allowance (Combine 50 micros; XFA 20/30/50 by balance,
  D-289); intended (capped) equals realised to the dollar.
- **Fill model / cost profile**: `assumed` (`config/fills.yaml`; D-95): the published round turns at the contracts each
  trade holds (D-276, D-324), the entry minute's spread and a tick at entry, a tick on a stop or breakeven, none at a
  target, two on the flatten (D-321). The slippage values are assumptions.
- **The campaign**: five accounts in rotation, at most five Combines, trades routed to the longest-waiting account that
  can take them (D-318), none against an open opposite position and the seat refilled the same evening (D-353), the
  Standard payout path with Aeropay, 504 days, 500 paths, cash that never binds with the required bankroll an output
  (D-312), placement off (D-289) and on beside, denial 0 % (D-234) with 10, 25 and 50 % beside. The policy's decision
  inputs read to the cent (D-328).
- **Parameters, with their exact values**: every one above is in the frozen config; nothing is left to be chosen. The
  edge cell is read from the window's own bound after the fact by the declared rule (the nearest tabulated cell), which
  is a rule, not a choice.

**Conduct check in D-145's three tiers** (`propedge/campaign/conduct.py` is the one source):

- Tier 1, hard -- every box must be ticked, or the model is not a candidate:
  - [x] no cross-account hedging -- the engine refuses any signal opposite to a position open on another account, so no
    two accounts ever hold opposite positions (D-353); the Studio's independent mirror of run fv3_corrected_v1
    reproduced it path for path on both arms and found no opposite positions held across accounts on any of the 500
    paths (Studio runs 20261013T155213Z and 20261013T160805Z, reported 2026-10-13); the operator applies the same rule
    by hand
  - [x] no reliance on simulator fills (stops of 12.5 to 50 NQ points; market entries at the next bar with a tick and the
    measured spread; no auto-breakeven -- the breakeven move is at a session open, by hand) or fills outside the best bid
    or offer
  - [x] no maximum size into major news (FOMC days out; the 08:30 ET release candle anchors fair price, no trade off it);
    no coordinated trading
  - [x] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled: the Combine's R below 1 on some states of the table's menu, maximum position on most trades (the
  full allowance), several accounts at the MLL in one day -- reported beside; placement OFF in the base case (D-289), the
  placement-on rows beside with the label "not a reading of placement".
- Tier 3, priced: many Combine purchases and the breaches; payouts from accounts showing the pattern are denied with the
  stated probability; the gate uses 0 % (D-234); 10, 25 and 50 % reported beside.

## 4. Metrics

- **Primary**: the campaign's median path growth on its required bankroll at p90, a year's rate, at the lower-bound shift,
  0 % denial, placement off (the gate row).
- **Each leg's net edge** e per trade at every R of the menu, in units of intended risk, net of each trade's own cost,
  pooled over the window; its one-sided 95 % lower bound from the means of 21-session blocks (the blocks' mean less the
  t quantile at 0.95 with blocks - 1 degrees of freedom times their standard error -- the development declaration's
  yearly formula on monthly blocks, D-237 (4)). The gate's shift is the funded leg's bound at its R, and the table's cell
  is the one nearest it.
- **The lines' inputs**: C2 -- each counted period's campaign (the per-year campaign function on period labels):
  growth on its required bankroll, its activity bound (D-305), its Sharpe's sign with and without idle blocks; C3 -- the
  break-even denial rate and the gate at 10 % denial; C4 -- realised risk over the allowance-capped intention (the raw
  ratio beside), each leg's flatten share overall and per period, the periods with no gate trade.
- **Cost drag (D-356)**: for the gate's trades, each R's gross edge, cost and net edge in units of intended risk at the
  fresh Combine's size -- the cost each trade's outcome at that R took (its entry spread and a tick, its fee, its exit) --
  pooled and per period at the two fresh legs' R (1.5R and 3R); `cost_r` is the cost drag as a fraction of dollars
  risked, and gross less cost equals the gate's net edge (the verdict script checks it). The engine re-prices each fee at
  the contracts a trade holds (D-324); the campaign rows carry the fees paid. (P-05's FAIL turned on cost per trade,
  D-233.)
- **Also reported**: trade and session counts per period; the refused signals' share; the realised per-trade sd against
  `assumed_sd`; the required bankroll at p50 / p90 / p99 / worst; drawdown, days to the first payout, accounts funded and
  paid, Combines bought, the efficiency measures (cash per slot-day, slot-days per attempt and per XFA, the shares
  abandoned); the zero-edge and fixed-legs twins; the placement-on rows (labelled); the denial ladder; each leg's bound at
  0.05/N beside; the deflated campaign Sharpe at N; whether propsim D-47's criterion (e >= 0.10, bound >= 0.05) is met at
  any R; the variant count.
- Outputs: `results/fv3_confirmation.csv` and `results/fv3_confirmation_paths.csv`, each with its manifest.

## 5. Pass / fail criteria

**PASS requires all four**, read on the window as the frozen config words them (`scripts/confirm_fv3.py`):

1. **C1, the D-145 gate**: the campaign's median path growth on its required bankroll above zero with both legs' trade
   outcomes shifted to the one-sided 95 % lower bound of e over 21-session blocks, fees and payout latency applied, the
   Standard path, placement off, denial 0 % (`CHARTER.md` -- not at the point estimate, not in sample).
2. **C2**: every counted period's campaign growth on its required bankroll above zero, with its activity bound above one
   half and no path's Sharpe changing sign without its idle blocks -- each period's campaign run on its own trades'
   outcomes as measured (the point arm, not shifted to the bound), resampled within the period, as the development
   walk-forward's P1 read each year.
3. **C3**: the break-even denial rate at least 25 %, and the gate above zero at 10 % denial.
4. **C4**: realised risk at least 90 % of the allowance-capped intention; each leg's flatten share at most 5 % overall and
   in every counted period (D-308); no counted period without a gate trade; at least two counted periods.

**FAIL** is anything else, including a result that cannot be computed, a period unusable twice, or fewer than two
counted periods.

**An unusable run -- one test, one consequence, fixed now (as P-05, D-230/D-231).** A run is unusable, judged from its
log alone before any record is parsed, if END is missing, the log or the operator reports an error or a time limit, or
HEAD's days fall below the period's `min_days` in the config (60 for each half-year, about half its sessions; none for
2026 Q3, which the data's end may cut short and which is then simply not counted); a usable log whose output the parser
refuses (in memory, nothing saved or shown) is unusable too, its message kept out of the record; a day record outside the
period's dates likewise. It is recorded in `unusable.json` and its records are never saved or read. Every period's run is
judged this way before any period's records are saved (the order, section 2). One fixed kit per period may follow -- kit
mechanics only, every rule in the config unchanged, the fix recorded in a decision before it runs. A refusal of the
procedure (a missing or wrong download, the ran code) is retried on the same backtest's own files and is not a new run.

- **What a fail means for the project**: FV3-C is closed -- the fair-value family's last candidate on this effect; NQ's
  held-back window is spent for any later candidate built on it (D-237, D-229); NQ has one of D-107's three tests left.
  The stage returns to finding an edge, or closes at exit (B) with the evidence on record. The failure protocol applies to
  the machinery, never to the verdict: a terminal-state audit, stage decomposition, component isolation and seeded
  replication diagnose whether the machinery erred; a correct FAIL stands.
- **Whatever the verdict**: no later model takes its triggers, sessions, stops, R or sizing from the window's records;
  those are chosen on development data only. On a pass, the campaign goes forward exactly as frozen; any change to it is
  a new model with its own confirmation.

> A failed pre-registered check is **kept on record and diagnosed**, never rerun until it passes: terminal-state audit ->
> stage decomposition -> component test in isolation -> replication with seeds fixed beforehand. See the failure
> protocol in `CLAUDE.md` and propsim D-40.

## 6. Seed

- **Seed**: 20261019 (the gate), as the development declaration: the confirmation's campaign shares its random numbers
  with run fv3_corrected_v1's reading and differs only by its inputs.
- Additional seeds: eras 20261017 and spa 20261020 as the config where those sections run (they select nothing here);
  stops 20261018 (unused: the stops are the ladder's fixed points).

Every simulation in this stage is seeded. A seed chosen after seeing a result is a variant.

## 7. Variants

- Configurations already tried for this question: 16 ledger lines of the FV3 family in `results/variants.jsonl` --
  D-295:fv3_grid (32 configurations), D-302:fv3_grid_corrected (32; 48 distinct across the two, D-303), the eleven
  fv3_portfolio runs (D-306 to D-351; v12 and v13 identity checks), the two fv3_gf runs (D-346, D-349) and
  D-353:fv3_corrected_v1 -- beside FV2's grid (D-283:fv2_grid, 96) and FV1's eight lines (T4:fv1); the flip maps (R137,
  R138) are on the trial ledger only. D-189's N over all of it is 183 (`ledger_n`). The stopped solves and the
  state-table exports hold no trial.
- Configurations this pre-registration will try: 1.

One configuration is tested on the held-back window; every choice among the rest happened on development data, and the
protocol has been reshaped after development outcomes, each time by a recorded decision before the next run. That
history is why only this window can decide.

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

---

## Outcome

- **Date run**: 2026-10-13. The kits R139, R140 and R141 run by the operator in QuantConnect's web editor; each judged
  usable before any record was saved, then saved under its judged backtest (D-360; R141's first backtest ran
  QuantConnect's default program and was never judged or saved). The verdict computed once by `scripts/confirm_fv3.py`
  from the clean tree at 7fe159f, the frozen hashes checked (committed d189464).
- **Result file(s)**: `results/fv3_confirmation.csv` and `results/fv3_confirmation_paths.csv`, each with its manifest
  (`exploratory: false`, P-06, seed 20261019, variant count 1). The audit: `docs/audits/p06_fv3c_confirmation_2026-10-13.md`
  (the opus auditor, symmetric, re-derived without the producing script).
- **Verdict**: **PASS** -- C1, C2, C3 and C4 met, re-derived identically by the audit.
- **Numbers** (the file's `line`, `period`, `gate_inputs`, `costs` and `twin` rows): the window 2025-07-01 to 2026-07-16
  (QuantConnect's data end), 251 trading days in 12 blocks of 21, 1,084 gate trades; counted periods 2025 H2 (121 days)
  and 2026 H1 (119), 2026 Q3 not counted (11 days; reported beside). C1: growth on the required bankroll 0.991182, the
  required bankroll $3,152 / $6,204 / $11,322 / $14,550 at p50 / p90 / p99 / worst. C2: 2.377643 and 2.845888, activity
  bounds 0.963808 and 0.963214, no Sharpe sign change. C3: break-even denial 0.421122, the bound arm at 10 % denial
  0.727846. C4: realised over the allowance-capped intention 0.997208 (raw 0.891548); flatten shares 0 (Combine) and
  0.010381 (funded), at most 0.020747 in a counted period; 481 and 550 trades in the counted periods. Beside the verdict:
  net e below zero at 11 of 12 R (at 3R +0.009999 with bound -0.126323), D-47's criterion met at no R; the zero-edge twin
  (growth 1.437303) richer than the as-traded campaign on the same seeds on 95.2 % of paths (the audit; development
  87.6 %); the realised sd at 1.5R 1.215554 against
  the assumed 1.209709; the funded leg's block-means deflated Sharpe 0.007282 at N 183. **Not produced, a reporting
  omission the audit found (D1):** "the deflated campaign Sharpe at N" promised in section 4 -- the portfolio hook was
  called without the trial Sharpes, as in development; it cannot be rebuilt from the files and changes no line.
- **Diagnosis, if failed**: not applicable. The audit's readings travel with the PASS (D-361): the money is the
  contract's shape, not a trading edge (the zero-edge twin richer on 95.2 % of paths); with the placement on every path
  loses, and at 50 % denial the gate arm is below zero; the campaign buys about 670 Combines a path; the most recent
  weeks (2026 Q3, uncounted) were the worst; cost per trade rose on wider entry spreads.
- **Decision taken**: D-361 -- FV3-C goes forward exactly as frozen to the pre-deployment protocol (D-337): a shadow
  period with its own pre-registration, acceptance criteria, kill rule and rules re-verified, one Combine first; any
  change to the campaign is a new candidate with its own confirmation.
