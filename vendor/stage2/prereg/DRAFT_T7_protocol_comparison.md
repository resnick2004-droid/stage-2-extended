# DRAFT — T7 protocol comparison under the time-aware objective

> **Not registered.** This is a draft written under T7a (D-119, slice 5) so that everything this
> repository controls about the protocol comparison is fixed before the one input it cannot
> control exists: a candidate's confirmed edge and its lower bound from T5. It becomes a
> pre-registration only through `/prereg` and the **prereg-gatekeeper**, which assigns the id.
> Until then no comparison run is a result: any campaign run at an assumed edge is labelled
> `exploratory=True` and `assumed_edge` in its manifest and is cited nowhere (T7a's done-criterion).
>
> **Blocking items, all of which must be closed before registration**, are listed in §0.

| field | value |
|---|---|
| **id** | P-XX *(assigned by the gatekeeper)* |
| **date** | *(the date of registration, before any comparison run)* |
| **author** | Claude (Stage 2), for the operator |
| **task** | T7 |
| **status** | draft (D-119) |

## 0. Blocking items (delete this section at registration)

1. **The edge input.** A T5 pre-registration has a recorded PASS: `e ≥ 0.10` with a one-sided
   95 % lower bound `≥ 0.05`, out of sample. This comparison runs at the **lower bound**
   (D-04), never at the point estimate. The T5 result file, its confirmation trade log and
   the pre-registration id are written into the table below and pinned by sha256 in
   `config/t7_frozen.json` (blocking item 7). The T5 log must carry a contract count so its day
   blocks carry risk per contract (tier sizing needs it, D-117).
2. **The two starting bankrolls.** The charter requires a small and a large bankroll. Which two
   is the operator's decision (`docs/HUMAN_INPUTS.md` §5) and is recorded in `DECISIONS.md`
   before registration. The draft names none.
3. **The baseline pair.** Stage one's admissible pair depends on the edge regime (D-114):
   2:1 $750 / 1.5:1 $1,000 at low edge, 1.5:1 $500 / 1.5:1 $1,000 at `e ≥ 0.10`. The lower
   bound from item 1 decides which is the baseline arm; the other stays in the grid.
4. **Optional arms not yet buildable.** The Daily Loss Limit election (D-26) has no engine
   switch and is excluded unless one is built before registration. The No-Activation-Fee path
   (D-25: $95 a month, $0 activation) is an engine parameter and is included as a stage-2 arm.
5. **The layout.** With one confirmed strategy the accounts run it through the copier
   (`multi_account_same_strategy`, D-22), so the primary mode is `copier`. If a second
   confirmed strategy exists, the partitioned layout of D-63 becomes an arm and its group
   assignment is declared here.
6. **Runtime.** Stage 1 is 324 arms x 2 bankrolls x 1,000 paths at 504 trading days. The
   lockstep loop's throughput is measured on the dry run and the path count is confirmed or
   reduced **before** registration, never after a result.
7. **Frozen inputs.** At registration `config/t7_frozen.json` is written with the sha256 of the
   T5 result file and log, `config/rules.yaml`, `config/fills.yaml`, `config/instruments.yaml`
   and `propedge/campaign/protocols.py`. The comparison script refuses if any has changed.

## Machine-checked fields

| key | value |
|---|---|
| `k` | 324 *(arms ranked in stage 1; computed by `propedge.campaign.t7_grid.k_arms()`, pinned by `tests/test_t7_grid.py`)* |
| `development_period` | none: no market data is read by this comparison; every arm is simulated from the pinned T5 result (blocking item 1) |
| `confirmation_period` | none |
| `confirmation_tests_on_this_market` | 0 *(this comparison spends no market window; the T5 test that supplies the input is counted on its own registration)* |
| `bonferroni_alpha` | 0.05: applied once, to the single pre-specified primary comparison (the top arm against the baseline arm), by the path bootstrap in §5; the k arms are ranked, not each tested |
| `assumed_sd` | *(the per-trade sd of the pinned T5 confirmation log, in units of intended risk — blocking item 1)* |
| `assumed_sd_source` | measured on the T5 confirmation log named in blocking item 1, pinned by sha256 |
| `risk_denominator` | intended |
| `primary_metric` | median_log_growth |
| `data_period` | none read here; the T5 result's confirmation period, through its pinned result file only |
| `seed` | 20261101 |
| `model_card` | none: a protocol comparison; the strategy it ranks protocols for is the T5 candidate, whose card its own pre-registration names (D-155) |

**Multiplicity plan.** No hypothesis about a market is tested here: the market enters only
through the pinned lower bound. The uncertainty in a ranking is Monte Carlo, and it is reported
as the path-bootstrap interval of each arm's primary metric. The one decision that is tested --
whether the top arm beats the baseline -- is pre-specified as a single comparison in §5, so no
Bonferroni split across arms is needed; the level in the table is the level of that one test.

## 1. Question

At the candidate's lower-bound edge, which protocol -- Combine profile, funded profile, payout
policy, per-trade risk on each leg and number of concurrent accounts -- maximises the **median
log growth of the fee bankroll** under reinvestment over 504 trading days, at each of the two
stated bankrolls, with ruin probability, bankroll drawdown and payout latency reported beside
it; and does the best arm beat stage one's baseline pair by more than Monte Carlo error?

- **Yes** means the top arm is the protocol T8 sizes and the report names.
- **No** means the baseline pair is the protocol. That is a valid outcome: stage one's
  pre-registered pair survives a clock, reinvestment and per-contract costs, which is what
  the charter said it could not yet claim.
- A ranking that flips between the two bankrolls, or between the two horizons, is reported as
  such; the arm chosen is the one that wins at the operator's stated bankroll and the primary
  horizon, and the flip is a finding.

## 2. Data period

- **Source.** No market data. The outcome process is the pinned T5 confirmation trade log
  (blocking item 1), resampled by whole day in intra-day order
  (`propedge.outcomes.distribution.day_blocks`), with every trade's `u = pnl_net / intended
  risk` shifted by a constant so the log's mean `u` equals the T5 lower bound. The shift keeps
  the log's shape, its day structure and its flatten share; only the location moves. A binary
  process at the same lower bound (`propedge.outcomes.distribution.binary_blocks`) is the
  validation limit and a sensitivity arm, never the primary.
- **Rules.** `propedge.contract.adapter.rules_from_ledger()`: every rule through the verified
  gate. Fees: Standard path, $49 per 21 trading days and $149 activation on activation (D-21).
- **Payout terms.** Aeropay (US baseline, $0 fee, 3 trading days, D-24) primary; ACH ($30, 6
  days) as a stage-2 arm. `propedge.campaign.payout_method` pairs them.
- **In-sample / out-of-sample.** Not applicable: nothing is fitted. The T5 log was the held-out
  test of its own pre-registration; it is used here as an input, not re-tested.
- **Horizon.** 504 trading days primary; 1,260 trading days for stage 2 (§3).

## 3. Rules fixed before the run

The instrument is the lockstep campaign of T7a (`propedge.campaign.lockstep`,
`shared_days`, `sizing`), which reproduces `reinvest.simulate_path` exactly on independent
streams and the vendored engine per account (`tests/test_lockstep.py`, `tests/test_sizing.py`).

- **Arms.** `propedge.campaign.t7_grid.enumerate_arms()`: the 9 distinct shapes of the
  protocol registry (stage one's baseline pairs, the buffer family at $2,000 / $5,000 / $8,000
  / $12,000, the fast-payout family: take-max, half-request, $1,000 buffer, and the
  consistency-path pair) x Combine risk per trade at 1/8, 1/4, 3/8 and 1/2 of the $2,000
  cushion x funded risk at 1/8, 1/4 and 1/2 x 1, 3 or 5 concurrent accounts. 324 arms. The
  funded sweep stops at 1/2 because the guardrail refuses a funded position above half the
  drawdown; that refusal is recorded, not argued around. Every arm is a `Protocol`, so the
  guardrails are checked at construction.
- **Stage 1.** Every arm at 504 trading days, 1,000 paths, at each bankroll (blocking item 2),
  copier mode, `current_tier` sizing at headroom 0.75, Aeropay, Standard fee path, activation on
  activation, buying stops while a pass is on hold (D-08), at most 5 concurrent accounts
  including Combines (D-34), one Combine at a time per free slot.
- **Stage 2** (declared now; run on the top 10 arms of stage 1 plus the baseline, at both
  bankrolls): 4,000 paths at 504 and at 1,260 trading days; the sizing band (`entry_tier`,
  `fixed_risk`) and the headroom sweep 0.60 / 0.75 / 0.90 (D-117); `independent` days as the
  upper-bound sensitivity (D-30); ACH terms; the No-Activation-Fee path; and the
  `on_pass` activation timing as a reconciliation check only.
- **The outcome process.** §2. One trade slot a day unless the T5 log has more; the day block's
  trade count sets the slots, and the engine's `trades_per_day` is the log's maximum.
- **Sizing.** D-117: `min(floor(pair_risk / risk_per_contract), floor(0.75 x the current tier's
  micro allowance))` per trade, the tier read from the balance at the start of the session,
  re-read after every payout (D-53). The Combine's ceiling is 5 minis.
- **Cross-account direction.** One signed direction per correlated group at every instant
  (D-55) holds by construction under the copier: every account carries the same position.
- **Selection rule.** Arms are ranked by the primary metric at the operator's stated primary
  bankroll and the 504-day horizon. The top arm is adopted only if it passes §5. A top arm on
  the boundary of the risk sweep (1/8 or 1/2 on either leg) is reported as a boundary result
  and is **not** adopted; the best interior arm that passes §5 is adopted instead, and the
  boundary finding goes to `DECISIONS.md` as a reason to widen the sweep in a new
  pre-registration, never in this one.
- **Costs.** Already inside the T5 log's `pnl_net`, per contract; they scale with the contract
  count. No further cost is applied.

**Conduct guardrails check:**

- [x] R > 1 on every arm (`Protocol.check_conduct`).
- [x] Risk per position well below the maximum: the funded sweep stops at half the drawdown;
  the headroom cap keeps every position below 75 % of the tier's allowance.
- [x] No single position decides the account: as above, and reported per arm as the largest
  single-trade loss as a fraction of the cushion at the start of that day.
- [x] No fail-and-repurchase design: a failed Combine is replaced under D-34's cap; purchases
  per year are reported per arm (RTP "excessive purchases") and are a §5 gate.
- [x] No cross-account hedging: the copier carries one position.
- [x] No reliance on fills the market would not give: the T5 log's fills are the T5
  pre-registration's, unchanged.

## 4. Metrics

All from `propedge.campaign.reinvest.CampaignSummary`, written by
`scripts/run_t7_comparison.py` to `results/t7_stage1.csv` and `results/t7_stage2.csv` with
manifests, one row per arm x bankroll x horizon x mode:

- **Primary.** `median_log_growth` per year, with its 95 % path-bootstrap interval (2,000
  resamples of paths, seed 20261102).
- **Beside it, always:** ruin probability, mean and p90 bankroll drawdown, days to first payout
  (mean and median), days between payouts, share of accounts that ever pay, share of paths whose
  log growth is undefined.
- **Secondary diagnostics:** mean and median final cash, annualised growth of the mean multiple
  (labelled secondary, D-14), portfolio IRR where defined (`propedge.campaign.irr`).
- **Conduct metrics, reported per arm and gated in §5:** share of trades sized at the tier cap
  (D-117), same-day multi-account loss-limit days and the largest single-day count (D-30),
  Combine purchases per year, the largest single-trade loss as a fraction of that day's cushion.
- **Sizing band** for the top arms: realised-to-intended risk under `entry_tier`,
  `current_tier` and `fixed_risk`.
- **Variant count:** the number of arms, from `k_arms()`, in every manifest.

## 5. Pass / fail criteria

**The top arm is adopted** if all of the following hold at the primary bankroll and horizon:

1. its `median_log_growth` exceeds the baseline arm's by more than the upper end of the 95 %
   path-bootstrap interval of the difference (one-sided, level 0.05, seed 20261102);
2. its ruin probability is not higher than the baseline's by more than that interval's width
   on ruin;
3. it is not on the boundary of either risk sweep (§3, selection rule);
4. its share of trades at the tier cap is below one half (D-117), and it has no arm-level
   pattern that a listed Responsible Trading Program trigger names by number: Combine purchases
   per year is reported and any arm above the baseline's purchases by a factor of two is
   excluded (the factor is declared here, not tuned).

**Otherwise the baseline pair is the protocol.** That is the fail outcome and it is a result:
stage one's pair stands under the time-aware objective, and T8 proceeds with it.

**What a fail means for the project.** Nothing is re-run and no arm is added. T8 sizes the
baseline pair on the lower bound. The failure protocol applies to the machinery, not the
verdict: a terminal-state audit of the ruined and stuck paths, stage decomposition (Combine,
hold, funded, payout), a component test in isolation against the engine's EV per attempt, and a
seeded replication of the top three arms.

## 6. Seed

- **Seed**: 20261101 for the campaign paths (each path's seed derives from it; each account's
  draw derives from the path seed, `propedge.campaign.lockstep.child_seed`).
- 20261102 for the path bootstrap of every interval.
- 20261103 for the shared day tables' extension beyond the pre-drawn calendar, if reached.

## 7. Variants

- Configurations already tried for this question: 0 pre-registered comparison runs. The T7a
  dry run at an assumed edge is exploratory by construction and is not a variant of this
  question.
- This pre-registration will try: 324 arms in stage 1 (one ranking), and the stage-2 sensitivity
  arms on the top 10, all declared in §3.

## 8. Anything chosen after seeing results

*(Empty at registration.)*

---

## Outcome

*(After the run.)*
