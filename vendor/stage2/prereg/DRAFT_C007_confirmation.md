> **WITHDRAWN 2026-09-24 (D-103). Never registered, never run; kept on record.** The criterion stands
> for this trade shape (D-104).

# DRAFT — C-007 confirmation test: pooled time-exit momentum across GC, CL, 6E and ES

> **Not registered.** This is a draft written ahead of Stage 2B's handoff, so that everything this
> repository controls is fixed before any confirmation data exists. It becomes a pre-registration
> only through `/prereg` and the **prereg-gatekeeper**, which assigns the id. Until then
> `config/c007.yaml` has `confirmation.prereg_id: null`, the confirmation kits cannot be
> generated, and `scripts/confirm_c007.py` refuses to run.
>
> **Blocking items, all of which must be closed before registration**, are listed in §0.

| field | value |
|---|---|
| **id** | P-XX *(assigned by the gatekeeper)* |
| **date** | *(the date of registration, before any confirmation run)* |
| **author** | Claude (Stage 2), for the operator |
| **task** | T5 |
| **status** | withdrawn (D-103) |

## 0. Blocking items (delete this section at registration)

1. **Handoff.** Stage 2B hands off C-007, or a successor with a new id, as final. `config/c007.yaml`
   `source` is updated to the handed-off record and commit.
2. **CL sizing.** At the $62.50 leg budget, one MCL contract cannot be sized on most CL
   development days (`results/c007_leg_sd.csv`, `no_trade_size_zero`). 2B must decide the fix by
   rule, on sizing grounds only, or keep the leg as it is. If any leg parameter changes,
   `scripts/measure_c007_sd.py` and `scripts/c007_gc_rule.py` are rerun, and the new result files
   are the ones pinned below.
3. **Criterion fit.** 2B's own record scores C-007 `criterion: fail`: its shrunk assumed edge is
   below 0.10. The operator decides whether to spend the confirmation window on a candidate
   whose own prior says it cannot meet the criterion. See §1, "Why the window is expensive". The
   decision is recorded in `DECISIONS.md`.
4. **k.** C-007's variant count from 2B's ledger, written into the table below and into
   `config/c007.yaml` `confirmation.k`.
5. **Winners larger than losers.** For a time exit this is a property of the outcome
   distribution (2B D-16), not of a bracket. The proposed operationalisation is in §3; the
   gatekeeper must accept or amend it.
6. **Cross-track hedging.** 2B's pending note: the ES leg is subject to Stage 2's cross-track
   hedging rule, which is not pinned yet. It must be pinned or declared not applicable.
7. **Frozen inputs.** At registration, `config/c007_frozen.json` is written with the
   sha256 of `results/c007_leg_sd.csv`, `results/c007_leg_rho.csv`, `results/c007_gc_rule.csv`,
   `config/c007.yaml` (whole: its `prereg_id` and `k` are written first, and evidence is found by run id, so nothing in it changes afterwards), `config/fills.yaml` and
   `config/instruments.yaml`. `scripts/confirm_c007.py` refuses if any has changed.

## Machine-checked fields

| key | value |
|---|---|
| `k` | *(from 2B's ledger — blocking item 4)* |
| `development_period` | per leg, from its first evidence day to 2014-05-27: GC from 2012-11-01 (D-90), CL, 6E and ES from 2009-06-01 |
| `confirmation_period` | 2014-05-28 to 2026-08-31, every leg |
| `bonferroni_alpha` | not applicable: confirmation period held out |
| `assumed_sd` | each leg's `sd_planning_q95` in `results/c007_leg_sd.csv` (D-43 upper 95 % bound), file pinned by sha256 |
| `assumed_sd_source` | measured on development evidence R017 (GC), R014 (CL), R015 (6E), R016 (ES) by `scripts/measure_c007_sd.py` (D-100, D-101) |
| `risk_denominator` | intended |
| `primary_metric` | e = mean of u = pnl_net / intended risk over every confirmation trade of every leg |
| `data_period` | development evidence as above; confirmation cloud runs 2014-05-19 to 2026-08-31 (warm-up days before 2014-05-28 are development data and are not scored) |
| `seed` | 20261001 |

**Multiplicity plan.** C-007 was selected in Stage 2B without touching this repository's
confirmation data. It is tested once, on the confirmation period, at one-sided 5 %
(`criterion_test(..., has_confirmation_period=True)`).

## 1. Question

Does C-007, executed as specified, with micro contracts, the `assumed` cost profile and the
development-frozen volatility forecast, earn a pooled net edge of at least 0.10 in units of
intended risk, with a one-sided 95 % lower bound of at least 0.05, on 2014-05-28 to 2026-08-31, and
does that edge survive C-007's own attached checks?

- **Yes** means C-007 goes to T6/T7 as the strategy, sized on the lower bound.
- **No** means C-007 is dropped (below). With no other candidate, that is exit (B).

**Why the window is expensive.** The confirmation window can be looked at once. After this test,
2014-05-28 onward in GC, CL, 6E and ES is spent for any later candidate built on the same
effect. Two things point to a failure here: 2B's shrunk prior is below the criterion, and a 0.10
edge at the measured sds implies a per-leg annual Sharpe well above the D-48 ceiling. That is
blocking item 3.

## 2. Data period

- **Source.** QuantConnect US Futures (AlgoSeek), minute trade bars, via the manual-run route
  (D-81). The kits are R018–R025 (`propedge/data/run_kit.py` `CONF_RUNS`). Each is the development
  algorithm `LEG_BODY_V2` unchanged; only the dates and the embedded pre-registration id differ
  (`tests/test_c007_confirm.py`). Contract choice is by prior-session volume, with FILTER_DAYS 200
  for GC and 120 for the others (D-98, D-99).
- **Symbols and resolution.** GC, CL, 6E and ES, one minute. Trades are costed as MGC, MCL, M6E and
  MES.
- **In-sample / development.** Only the development period above. It is used to fit the forecast
  once and to measure the sds. Nothing is re-estimated after confirmation data is seen.
- **Out-of-sample / test.** 2014-05-28 to 2026-08-31, in two parts per leg. Part 1 owns 2014-05-28
  to 2020-06-30; part 2 owns 2020-07-01 to 2026-08-31. The cloud runs start a few days earlier
  (warm-up only). Overlap days are compared and the comparison is reported; they are never used
  twice.
- **Walk-forward.** None. There is one held-out test.
- **Integrity.** The **data-integrity** agent validates all eight files before scoring
  (`docs/data_reports/C007_confirmation_evidence.md`). D-101's rule applies unchanged: a window not
  closed at the settlement minute is dropped, and the next day's signal is voided. An unusable run
  is reported and not rerun without a `DECISIONS.md` entry. The decision rests on the run's
  failure mode, never on its numbers.

## 3. Rules fixed before the run

As C-007 (2B, handed-off record), executed by `propedge/outcomes/time_exit_sd.py` `trades` and
`propedge/outcomes/c007_confirm.py`:

- **Entry.** At each leg's window start (GC 12:00, CL 13:00, 6E 13:31, ES 14:30 CT), take the sign
  of the return from the previous settlement to the entry price. Positive means long, negative
  means short, zero means no trade. Entry fills one tick adverse.
- **Exit.** A time exit at the leg's settlement minute (12:30, 13:30, 14:00, 15:00 CT), one tick
  adverse, unless the stop is hit first.
- **Stop.** `max(ceil(2.0 × entry × sqrt(RV-hat) / tick), floor)` vehicle ticks from the entry
  fill. Floors: MGC 30, MCL 26, M6E 18, MES 20. The stop is judged on the window's high and low
  and fills one tick beyond. RV-hat comes from the panel log-HAR (lags 1, 5, 22; per-market
  intercepts; pooled slopes; `exp(fit + s²/2)`), **fitted once on every development day and
  frozen** (`c007_confirm.fit_frozen_har`). Its coefficients go into the result manifest.
- **Bracket R.** None: this is a time exit. Dollar risk per trade is intended risk,
  `stop ticks × tick value × contracts`, at most $62.50.
- **Session.** All windows close by 15:00 CT, before the 15:10 CT flatten. Nothing is held
  overnight.
- **Contracts.** `floor(62.50 / (stop ticks × tick value))`. At 0, the leg does not trade that day.
- **Costs.** The `config/fills.yaml` profile `assumed`: round-turn cost per contract and one tick
  of slippage on entry, stop and exit. **These are assumptions** (D-95), not measurements, and the
  result is reported as conditional on them.
- **Parameters.** Multiplier 2.0, the floors, the $62.50 budget, the HAR lags, min_fit 60. All are
  fixed and none is tuned.

**Conduct guardrails:**

- [ ] **Winners larger than losers.** Proposed for a time exit: the mean of `u` over winning
  confirmation trades exceeds the mean of `|u|` over losing ones. This is reported. It is a
  conduct check on the outcome, not a filter, and it is **not** part of the pass rule unless the
  gatekeeper makes it one (blocking item 5).
- [x] Risk per position well below the maximum: at most $62.50 per leg, $250 a day, against a
  $2,000 MLL.
- [x] No single position decides the account.
- [x] No fail-and-repurchase design.
- [ ] No cross-account hedging: pending the cross-track rule (blocking item 6).
- [x] No reliance on fills the market would not give. Fills are adverse by a tick, stops are
  judged on trade-bar extremes, and nothing depends on a touch fill.

## 4. Metrics

- **Primary.** The pooled `e` over every trade of every leg, and its one-sided 95 % lower bound.
  The bound is the more conservative of the day bootstrap (10,000 replicates) and the normal
  approximation on daily means (`metrics.criterion_test`).
- **Per leg** (reported, never claimed): e, sd and lower bound.
- **C-007's attached checks:**
  - leave-one-out: the pooled criterion without the leg with the highest point estimate;
  - Cochran's Q across the four legs' e, with se = sd/√n and df = 3;
  - the count of legs with a positive point estimate.
- **Also reported:**
  - trade and day counts, and no-trade days by reason;
  - realised sd against `assumed_sd`, per leg;
  - the realised cross-leg ρ;
  - the stop-hit rate;
  - the winners/losers ratio (§3);
  - the overlap comparison between parts;
  - the variant count.
- Outputs are `results/c007_confirmation.csv` and `results/c007_confirmation_trades.csv`, with
  manifests.

## 5. Pass / fail criteria

**Pass** requires all four:

1. pooled e ≥ 0.10 **and** its one-sided 95 % lower bound ≥ 0.05;
2. at least 2 of the 4 legs have a positive point estimate;
3. without the best leg, the remaining legs still meet (1);
4. Cochran's Q homogeneity is not rejected at 5 % (p ≥ 0.05).

**Fail** is anything else, including a result that cannot be computed.

**What a fail means.** C-007 is dropped. Its pre-registration is closed with the outcome, and the
four markets' confirmation window is recorded as spent for this effect. The failure protocol
applies to the machinery, not to the verdict: a terminal-state audit, stage decomposition,
component isolation and seeded replication diagnose whether the machinery erred. A correct fail
stands. If no other candidate exists, the stage closes at exit (B).

## 6. Seed

- **Seed**: 20261001, for the pooled bootstrap.
- Seeds 20261002–20261005 are for the per-leg bootstraps (legs in sorted order), and 20261011 is
  for leave-one-out, as `c007_confirm.verdict` derives them.

## 7. Variants

- Configurations already tried for this question in this repository: 0 confirmation runs. The
  development measurement is not a test of the edge.
- This pre-registration will try: 1.
- C-007's `k` in Stage 2B: *(blocking item 4)*.

## 8. Anything chosen after seeing results

*(Empty at registration.)*

---

## Outcome

*(After the run.)*
