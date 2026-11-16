# P-XX — <title>

> Copy this file to `prereg/P-XX_<slug>.md` via `/prereg <title>`, fill **every** section, then
> hand it to the **prereg-gatekeeper** agent. It refuses to register a pre-registration missing
> the data period, the fixed rules, the metrics, the pass/fail criteria or the seed, because a
> hypothesis that can be adjusted after the fact is not a hypothesis.
>
> The harness (`propedge/backtest/harness.py`) will not run without a registered id. There is
> no override.

| field | value |
|---|---|
| **id** | P-XX *(assigned by the gatekeeper — leave as P-XX)* |
| **date** | YYYY-MM-DD *(the date this was written, before any run)* |
| **author** | |
| **task** | T5 / T7 / … from NEXT_STEPS.md |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after the model card and its cheap screen, before any kit |
| **status** | registered |

## Machine-checked fields

> `propedge.backtest.prereg.validate_prereg` reads **this table** and the gatekeeper refuses
> the pre-registration if any row is missing or still a placeholder. The prose sections below
> are where you explain; this table is where you commit. A row left as `<…>`, `TBD`, `n/a` or
> empty counts as missing.

| key | value |
|---|---|
| `k` | *(how many variants will be tried, **declared now**. 1 if exactly one configuration)* |
| `development_period` | *(the dates selection may use)* |
| `confirmation_period` | *(the held-out dates, never used in development, tested once — or `none`)* |
| `confirmation_tests_on_this_market` | *(how many registered confirmation tests have already spent this market's window, counted from `REGISTRY.md`; the cap is three per market — D-107)* |
| `bonferroni_alpha` | *(required only if `confirmation_period` is `none`: `0.05/k`, reported beside the verdict; the verdict's levels are the 0.05/N sentence's in §5, D-419)* |
| `assumed_sd` | *(per-trade sd in units of risk that the sample-size claim rests on)* |
| `assumed_sd_source` | *(measured from which pilot log, or "assumption". Stage one's 1.23–1.79 is the frictionless binary floor and may **not** be borrowed)* |
| `risk_denominator` | *(`intended` or `realised` dollar risk — it changes `e`)* |
| `primary_metric` | *(for a campaign or a protocol comparison: `growth on the required bankroll` -- `pf_growth_on_base_p50` on `pf_required_p90`, D-312, D-457; never `median_log_growth`, the notional column)* |
| `data_period` | *(full span the run touches)* |
| `seed` | *(an integer, fixed now)* |
| `model_card` | *(the path of the model's card, e.g. `docs/candidates/cards/IM1.md`, which must pass `validate_card` — D-155; or `none: <reason>` for a comparison that tests no model)* |
| `power_rr` | *(D-192: the R the power is read at — the Combine's R, where the model is ranked)* |
| `power_effect` | *(D-192: the effect size e at that R the test must be able to find — the card's `edge_assumed`)* |
| `boot_len` | *(D-192: the bound's bootstrap length in days; the power curve is read at it)* |
| `required_trades_source` | *(D-192: `l5_power_curve`, or `assumed_sd fallback: <why the curve does not apply>`)* |
| `required_trades` | *(D-192: the trades at which the bound clears zero with power 0.80, read from `propedge.research.power.required_trades` on the L5 curve — the validator reads it again; `> <largest count>` if the curve never gets there)* |
| `available_trades` | *(D-192: the trades the registered period will supply, estimated before the run)* |
| `ledger_n` | *(D-189: the trial count N — this registration's k plus the ledger rows that read its markets and development window at its bar resolution and sat in its model's selection pool, from `propedge.research.ledger.count_n` on `prereg/models.yaml`; a development verdict's lower bound is at one-sided 0.05/N, a confirmation's at the registered 0.05 with 0.05/N beside (the 0.05/N sentence in §5, D-419). A registration that tests no model: its k)* |

**Multiplicity plan.** Selection happens on the development period only. The single selected
variant is tested **once** on the confirmation period, and the criterion is applied to that
result alone. With no confirmation period, Bonferroni's one-sided `0.05/k` is reported beside the
verdict, and an unadjusted bound on a selected variant is **exploratory**. The verdict's levels are the
0.05/N sentence's (§5; D-189, D-230, D-419): a development verdict at `e`'s one-sided bound at `0.05/N`,
N the `ledger_n` above -- PASS there, CONTINUE at the 0.05 bound only, FAIL below it; a confirmation at
the registered one-sided 0.05, with the bound at 0.05/N reported beside it, never as the verdict. The
deflated Sharpe ratio is reported beside (`propedge.research.haircut`); if N makes the gate
unreachable on development data, the confirmation window carries the decision, never a smaller N.
`propedge.backtest.metrics.criterion_test(..., k=…, has_confirmation_period=…)` implements this;
use it rather than applying the criterion by hand.

---

## 1. Question

What is being asked, in one or two sentences. Phrase it so that **both** answers are
informative — if a "no" would not change anything, this is not worth running.

## 2. Data period

- **Source**: which dataset, which validation report.
- **Symbols and resolution**:
- **In-sample / training period**:
- **Out-of-sample / test period**: the dates, fixed **now**, before anything is run.
- **Walk-forward scheme**: number of folds, train and test window lengths, rolling or
  anchored.

> The test period is fixed here and not revisited. Extending it after seeing a result, or
> sliding it to a friendlier regime, converts an out-of-sample test into an in-sample one.

## 3. Rules fixed before the run

Everything the strategy will do, specified so that someone else could implement it and get the
same trades:

- **Entry**:
- **Exit / target**:
- **Stop**:
- **Bracket R** (target ÷ stop), and the dollar risk per trade:
- **Session**, and the **15:10 CT flatten** handling:
- **Instrument** and how the stop distance maps to **integer contracts**:
- **Fill model / cost profile** (`config/fills.yaml` profile name), and whether its values are
  measured or still assumptions:
- **Parameters, with their exact values.** Any parameter left "to be chosen" is a variant that
  will be counted.

**Conduct check in D-145's three tiers** (`propedge/campaign/conduct.py` is the one source):

- Tier 1, hard — every box must be ticked, or the model is not a candidate:
  - [ ] no cross-account hedging
  - [ ] no reliance on simulator fills (tight brackets, auto-breakeven, SIM-fill scalping) or fills outside the best
    bid or offer
  - [ ] no maximum size into major news; no coordinated trading
  - [ ] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled — say which apply; the simulator applies their verified consequence ($1,000 DLL on later
  Combines, Consistency-path-only new funded accounts): R at or below 1; maximum position on most trades; several
  accounts at the MLL in one day.
- Tier 3, priced — account stacking, many Combine purchases: payouts from accounts showing the pattern are denied
  with the stated probability; the gate uses 0 % (D-234), and 10, 25 and 50 % are reported beside it.

## 4. Metrics

Exactly what will be computed, and from what:

- **Primary**: e = mean P&L per trade ÷ dollars risked (`risk_denominator` above), **net of
  costs** (`propedge.backtest.metrics.criterion_test`).
- **Interval**: one-sided lower bound at the level the multiplicity plan implies — bootstrap
  over **days** and the normal approximation; the more conservative of the two is the one
  decisions use.
- **Also reported**: trade count, day count, **realised** per-trade sd against the `assumed_sd`
  above, share of trades flattened, cost drag as a fraction of dollars risked, **variant count**.
- *(For a campaign or a protocol comparison: **growth on the required bankroll** -- the median path's growth on
  the bankroll the run itself required, `pf_growth_on_base_p50` on `pf_required_p90` (D-312) -- is the primary
  metric; the engine's `median_log_growth` on a notional bankroll is reported, never the gate (D-451 F4). IRR of
  dated cash flows is a secondary diagnostic, reported only where uniquely defined. Payout latency, ruin probability
  and bankroll drawdown are reported beside the growth number, never in an appendix; the FLAG levels of
  `docs/SUCCESS_CRITERIA.md` §5 beside them.)*

- **Validation readings, beside the verdict, never a verdict line (D-663; `docs/RESEARCH_PROTOCOL.md` steps 4, 7
  and 8)**, each with its levels and seeds fixed **now**: the gate row with each path's days block-resampled (the
  stationary bootstrap at mean block 5, 21 and 63 sessions) and the required bankroll under each; the coverage of
  the bound of e at its registered level on block-resampled histories; the break-even e (the step, the most steps)
  and its margin below the registered bound; the missed-trade stress (the share of offered trades dropped, the
  share of sessions missed).

## 5. Pass / fail criteria

State the decision rule **before** the numbers exist, with no room for interpretation:

- **Pass**: the D-145 gate as `docs/SUCCESS_CRITERIA.md` states it (the single source, D-457), out of sample: the
  campaign's **growth on the required bankroll** above zero with each R's trade outcomes shifted down to the one-sided
  95 % lower bound of `e`, fees and payout latency applied, the Standard payout path, the Responsible Trading
  Program's placement off (D-289) and the tier-3 denial probability at 0 % *(the operator's rule, D-234;
  `propedge.campaign.gate.run_gate`; `CHARTER.md` — do not weaken it here: not at the point estimate, not in
  sample)*. **The 0.05/N sentence (D-189, D-230, D-419):** A development verdict is read at `e`'s one-sided bound at
  0.05/N, N the trial ledger's count for the candidate's pool (`prereg/models.yaml`, `count_n`) -- PASS there,
  CONTINUE at the 0.05 bound only, FAIL below it; a confirmation -- one configuration fixed in advance, read once on a
  window that played no part in choosing it -- is read at the registered one-sided 0.05, with the bound at 0.05/N
  reported beside it, never as the verdict. A confirmation's lines are C1, C2 and C4 of `docs/SUCCESS_CRITERIA.md`
  §3; **payout denial is never a line** (D-234, D-457). Always reported beside it: the same campaign at 10, 25 and
  50 % denial and the break-even denial, the placement on, the zero-edge twin, `e` and its bound, and whether the old
  criterion (e ≥ 0.10 and bound ≥ 0.05, propsim D-47) is met.
- **The confirmation window** is the market's declared window in `config/windows.yaml` (R4), named here with its
  21-session block count beside development's; the Combine's headroom over its target is checked against the
  window's bound before registering, with the numbers (D-451).
- **Fail**: anything else.
- **What a fail means for the project**: *(be specific — "the candidate is dropped", not "we
  investigate further")*.

> A failed pre-registered check is **kept on record and diagnosed**, never rerun until it
> passes: terminal-state audit → stage decomposition → component test in isolation →
> replication with seeds fixed beforehand. See the failure protocol in `CLAUDE.md` and
> propsim D-40.

## 6. Seed

- **Seed**: *(an integer, fixed now)*
- Additional seeds, if any, and what each is for:

Every simulation in this stage is seeded. A seed chosen after seeing a result is a variant.

## 7. Variants

- Configurations already tried for this question: *(number, from
  `propedge.backtest.harness.VariantCounter`)*
- Configurations this pre-registration will try: *(number)*

If more than one configuration is tried, say how the multiple-comparisons problem is handled.
An edge picked as the best of forty is not the same finding as an edge found on the first try.

## 8. Anything chosen after seeing results

*(Left empty at registration. Anything added later is **exploratory**, is reported separately,
and is marked `exploratory=True` in its result manifest. Stage one did this and labelled it —
propsim D-44.)*

---

## Outcome

*(Filled in after the run. Record it whether it passed or failed; then add the row to
`REGISTRY.md`.)*

- **Date run**:
- **Result file(s)**: *(with manifest)*
- **Verdict**: PASS / FAIL
- **Numbers**: *(cite the result file — do not type numbers here that are not computed from it)*
- **Diagnosis, if failed**: *(the four-step protocol)*
- **Decision taken**: *(and the `DECISIONS.md` entry number)*
