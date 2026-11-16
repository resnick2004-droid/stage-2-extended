# Charter — Stage two: demonstrated edge and protocol selection

Opened 2026-09-21. This charter fixes the question, the scope, the objective and the exit criterion.
Changing any of them requires an entry in [`DECISIONS.md`](DECISIONS.md) that cites this file.

Stage one (vendored read-only at [`vendor/propsim/`](vendor/propsim/)) closed the contract-level question:
what the Topstep 50K contract does to a trading process, which uses of it are permitted, and what a genuine
edge is worth inside those limits. Stage one is cited throughout as **propsim D-xx**.

---

## The question

> Does a candidate trading strategy, executed realistically (real fills, commissions, contract sizes and the
> firm's limits), have a demonstrated edge that meets the pre-registered criterion — and if so, which protocol
> (Combine profile, funded profile, payout policy, sizing, number of accounts) maximises long-run growth of cash
> under reinvestment, given the firm's 5-active-funded-account cap and a stated bankroll?

Two halves, in order. The first is a fact about a strategy and can only fail or succeed. The second is a choice
among protocols and is only worth making if the first succeeds.

> **Amended** (D-145, 2026-09-25). The first half is now a fact about a **campaign** (strategy plus protocol): does
> it make money over time inside the contract, out of sample, at the lower confidence bound, with the firm's rules
> applied in three tiers (below)? Where the money comes from — the strategy's edge or the contract's shape — no
> longer decides a candidate. The strategy's own edge `e` and its bound are always reported beside it.

> **Amended** (D-452, D-454, 2026-10-29, the operator). The primary goal is a campaign that makes money from the
> prop firms' **contract shape**; a signal's own edge is a bonus, reported beside the verdict, never required. Models
> are judged on **executions per day, resolution and cost**, built from simple mechanical patterns (a 15-minute
> breakout, OHLC patterns). The campaign holds seats at more than one firm (Lucid first, after Topstep), **one
> position at a time per firm**, so a second firm adds seats and a second simultaneous position. The second half of
> the question now includes the number of firms and how signals are alternated between them; the bankroll is an
> output of the run (`pf_required_p90`, D-312), never a preset figure.

---

## In scope

- Candidate strategy specification and long-history **out-of-sample** testing with realistic costs and fills.
- Conversion of candidates to **contracts, ticks and sizing** under verified firm limits.
- Extension of the stage-one contract engine with **empirical outcome distributions** (replacing the binary draw).
- A **time-aware campaign model**: IRR of dated cash flows, reinvestment growth, ruin and drawdown of the fee bankroll.
- **Pre-registered comparison of protocols**, including fast-payout structures.
- A final **report and deck built from result files**.
- **A second prop firm, Lucid first** (D-452, D-454): its rules verified in the multi-firm repository
  (`Desktop\Stage 1- XFA Eval Repository`, its D-06 to D-29) and loaded only as verified; seats at both firms, one
  position at a time per firm; Lucid's payout cap and five-payout account life modelled.
- **Mechanical signal families** judged on executions per day, resolution and cost (D-452), screened as signal
  atlases and pre-registered as families with their confirmation window declared before any development read; a
  signal's own edge is reported, never required.

## Out of scope

- Any zero-edge or fail-and-repurchase design. **Prohibited: account stacking** (see propsim D-34). Structural value
  that exists at e = 0 is not a source of income for this project and is not to be re-measured, re-ranked or
  re-packaged here.

  > **Amended** (D-145). Withdrawn as an exclusion. Account stacking, excessive Combine purchases and the
  > sole-discretion catch-all are **tier 3**: in scope, priced as an enforcement risk (a payout from an account
  > showing the pattern is denied with a stated probability) and reported with the pattern's measures. What stays
  > out of scope is **concealment**: nothing is designed to hide a pattern from the firm or evade its detection.
- Re-running stage one's closed studies.
- A designed **cross-firm hedge pair as a live plan** (D-452, D-454): prohibited in writing at Lucid ("same-account,
  cross-account, cross-user, cross-firm, correlated opposing", article 11404734; Topstep's wording silent on other
  firms). It is modelled only as the arm labelled `hypothetical_hedge` in every result, because its outcome is known
  by construction and measures what the statistical bound costs the campaign; it never enters a live plan.
- Live trading.
- Discretionary strategies that cannot be specified as rules.

Ideas that are good but belong elsewhere go to [`PARKING_LOT.md`](PARKING_LOT.md), not into scope.

A model that passes the gate and its confirmation leaves this stage with its protocol comparison and sizing report
(T7, T8); live shadow, operations and monitoring are a later stage (`PARKING_LOT.md`; D-187).

---

## Settled inputs from stage one (do not reopen)

These are inputs, not findings to be re-derived. Each is sourced in the vendored repository.

### Contract ceilings (analytic, zero edge)
| quantity | value | source |
|---|---|---|
| Combine pass probability, any fair strategy | P(pass) ≤ 2/5 | propsim D-02; `vendor/propsim/README.md` §Mathematical structure |
| Funded account gross payouts, any fair strategy | E[gross payouts] ≤ $2,000 | propsim D-02; martingale bound on T = balance + payouts |
| Supremum of Combine P(pass) over **all** fair strategies | 0.327131 = 2000² / (3350 · 3650) | `vendor/propsim/optimality/results_combine_supremum.csv` |
| Best static profile, 1:1 at $1,500 risk | 16/49 = 0.326531 (exact Markov chain) | `vendor/propsim/README.md`; reproduced by `edge/combine_exact.py` |

16/49 sits 0.06 pp below the supremum. These are **ceilings on a prohibited design**; they appear here as
oracles — any stage-two result that breaches one is an engine error, never a finding.

### Conduct guardrails (propsim D-35, D-36)
Hard constraints on every candidate and every protocol in this stage:

1. **Winners larger than losers** (R > 1).
2. **Risk per position well below the maximum** (stage one tested ≤ $1,000 = 50 % of the $2,000 drawdown).
3. **No single position that decides the account.**
4. **No fail-and-repurchase campaign.**
5. **No cross-account hedging.**
6. **No reliance on simulator fills** that would not happen live (Prohibited Trading Strategies names
   "exploiting the relative lack of slippage in SIM to achieve impossible stop-loss execution").

Candidates are **never ranked or modified by detectability** (propsim D-35): a slower or smaller version of a
prohibited pattern is still the prohibited pattern.

> **Amended** (D-145, 2026-09-25): **three tiers replace the list above.**
>
> 1. **Hard** — a model that breaks one is out: cross-account hedging (5 above); exploiting simulator fills (6
>    above; 10305426 also names tight brackets or auto-breakeven for SIM fills); trading outside the best bid or
>    offer; maximum size into major news; coordinated trading; and **nothing designed to conceal a pattern from the
>    firm or evade its detection** (the part of D-35 that stands).
> 2. **Modelled** — the Responsible Trading Program triggers (13620045), including 1-3 above, are no longer bans:
>    the simulator detects them on the simulated path and applies the verified consequence (a $1,000 daily loss
>    limit on 50K Combines; Consistency-path-only new funded accounts until the program completes).
> 3. **Priced** — account stacking, excessive purchases of Combines or resets, and the sole-discretion catch-all
>    (4 above): a payout from an account showing the pattern is denied, and the account closed, with a stated
>    probability (0, 10, 25 and 50 % reported); the pattern's measures are reported beside every result.

> **Amended** (D-289, 2026-10-05, the operator): tier 2's placement -- the Consistency-path forcing and the
> $1,000 DLL -- is **off in the gate's base case** and reported beside the verdict, as tier 3's levels are;
> contracts at the full verified allowance. The Combine's own consistency target and the mid-trade settlement
> against the floor (D-156) stand.

### The research criterion (pre-registered in stage one, propsim D-47)
> Pursue a candidate only if the point estimate is **e ≥ 0.10** *and* the **one-sided 95 % lower bound is ≥ 0.05**,
> measured **net of commissions and slippage**, with realistic fills, **out of sample**.

where **e = mean P&L per trade ÷ $ risked per trade**. Below e ≈ 0.05 most of the value is the structural
(prohibited) component and the churn is high (`vendor/propsim/HANDOFF.md` §4).

> **Amended** (D-145, 2026-09-25): **this is no longer the gate; it is reported beside it.** The gate: a campaign
> passes if, out of sample, its time-aware return (median log growth, D-14) is above zero with the strategy's
> trade outcomes shifted down so their mean equals the one-sided 95 % lower bound of `e`, fees, payout latency and
> the tier-2 consequences applied, and the tier-3 denial probability at 25 % [D-234: 0 %; D-289: the Standard
> payout path, placement off]. Everything else in this section —
> out of sample, the sample-size amendment, multiplicity — stands, because it guards against luck and selection,
> not against where the money comes from. This change was made after every candidate so far had failed the old
> gate, at the operator's instruction, on the ground that discretionary rules had been treated as bans; a
> candidate that passes the new gate and not the old one is reported as such.

> **Amended** (D-234, 2026-10-02, the operator): **the gate's tier-3 denial probability is 0 %**, not 25 %. The
> 25 % reading, with 10 % and 50 %, is reported beside every verdict as a risk measure, never as the rule.

> **Amended** (D-454, 2026-10-29): the gate's metric is **growth on the required bankroll** -- the median path's
> growth on the bankroll the run itself required (`pf_growth_on_base_p50` at `pf_required_p90`, D-312), the bankroll
> an output of the run. "Median log growth" above names the engine's notional-bankroll column (D-451 F4); it is
> reported, not the gate. Payout denial is never a verdict line: the break-even denial and growth at 10 / 25 / 50 %
> denial are read beside the verdict (D-234); P-10's line C3 is the record of that conflict (D-450, D-452). The
> single source of the criteria is `docs/SUCCESS_CRITERIA.md` (the handoff's R1).

Sample size follows from stage one (`vendor/propsim/edge/results_sample_size.csv`): demonstrating e ≈ 0.10 needs
roughly 1,667 trades at R = 1.5, 2,263 at R = 2 and 3,453 at R = 3 — 6.6 to 13.7 years at one trade a day.
**Consequence: long historical tests are required; a short live or paper record checks execution, not edge.**

> **Amended — those figures are lower bounds, not the requirement**
> (D-15, sample size). They are frictionless
> (`sd` is the binary `(1+R)·√(p(1−p))`, 1.23–1.79), unadjusted for multiplicity (`z = 1.645` is
> the single-test value and the requirement scales with `z²`), and count trades rather than
> independent days. All three move the requirement **up**. A data-sufficiency claim must use the
> pre-registered `sd` with its source, the `z` the multiplicity plan implies, and a clustering
> factor — see `docs/HUMAN_INPUTS.md` §2 and
> `propedge.backtest.metrics.sample_size_required(edge, sd, z=…, cluster_factor=…)`.
> **Every pre-registration states its assumed per-trade sd and that sd's source**; stage one's
> range may not be borrowed.
>
> **Multiplicity** (D-13, multiplicity): a pre-registration states
> `k` in advance; selection happens on a development period only; the single selected variant is
> tested once on a held-out confirmation period and the criterion is applied to **that result
> only**. With no held-out period, Bonferroni at one-sided 0.05/k. An unadjusted bound on a
> selected variant is exploratory. Implemented by
> `propedge.backtest.metrics.criterion_test(..., k=…, has_confirmation_period=…)`.

### Payout policy is first-order — with a caveat (propsim D-45)
At positive edge, payout policy dominates profile choice: any payout drops the funded floor to $0, so an early
first payout strands a small balance. Stage one's best found was 1.5:1 at $500 risk with an $8,000 buffer
(`Policy(keep_balance=8000)`), giving $1,006 / $2,411 / $8,313 realised cash per funded account per year at
e = 0.05 / 0.10 / 0.20, against $686 / $1,262 / $4,075 taking the maximum at once.

**Caveat, and the reason this stage exists:** that buffer result was exploratory (chosen after seeing the
pre-registered results, propsim D-44), its grid was coarse, one optimum was still rising at the largest buffer
tested, and — decisively — **it ignores payout latency, reinvestment and per-contract costs**. It is a *hint about
direction*, not a settled input. Stage two re-derives payout policy under the time-aware objective below.

---

## Objective

**Stage one's objective (EV per attempt) is replaced.** EV per attempt is a static quantity: it values a dollar
paid on day 8 and a dollar paid on day 400 identically, and it cannot see reinvestment. Stage one flagged this
itself (propsim D-46: a per-year rate rewards cycling through failed attempts).

The stage-two objective is **time-aware return**:

1. **The primary ranking metric is the median log growth rate of the fee bankroll** in the calendar-time
   reinvestment simulation, stated per horizon and per starting bankroll, under the **5-active-funded-account cap
   and hold queue**. `propedge.campaign.reinvest.rank_protocols` sorts on nothing else.
2. **IRR of dated cash flows is a secondary diagnostic** — subscription and activation fees out on their dates,
   payouts in on their dates — reported only where it is uniquely defined. Attempts that never pay out have no IRR,
   and an attempt whose rate exceeds the solver bracket has none either; both are reported as undefined, never
   silently dropped and never clipped. Portfolio IRR likewise is a diagnostic, not the ranking key.

> **Amended** (D-14, primary metric). This
> supersedes the IRR-first wording of D-02 without editing it. Two reasons the ordering changed. A mean over
> multiplicative outcomes is dominated by its right tail, so mean final cash or annualised growth of the mean
> multiple can rank a protocol that wipes out most of its paths above one that compounds reliably; the median of
> the log growth rate is what a typical path actually experiences. And per-attempt IRR is badly behaved here for a
> structural reason — a few hundred dollars of fees returning thousands weeks later annualises to a rate that is
> arithmetically correct and economically meaningless — so it cannot carry a ranking. The reinvestment simulation
> can, because it has to spend the cash on something.
>
> Mean-based fields remain on `CampaignSummary`, explicitly labelled **secondary diagnostics**.

> **Amended** (D-312, D-454): the growth is read on the bankroll the run itself required (`pf_required_p90`), as
> `pf_growth_on_base_p50`; the notional-bankroll column (`median_log_growth`) stays as a diagnostic. The ranking key
> is otherwise unchanged.

Reported **always and beside the growth number**, never as an appendix:

- **payout latency** — days to first payout, days between payouts, share of accounts that ever pay;
- **ruin probability** — bankroll falls below the next fee;
- **bankroll drawdown**;
- results for **both a small and a large starting bankroll**.

A protocol that grows fast and ruins often has not won. Every money decision — sizing, bankroll, how many
accounts — uses the **lower confidence bound of the edge**, not the point estimate.

---

## Exit criterion

The stage closes on **one of two outcomes, both valid**:

**(A) A strategy that passes the criterion**, delivered with:
  - a **pre-registered protocol comparison** ranked by time-aware return;
  - a **sizing and bankroll report** computed with the lower confidence bound of the edge;
  - a **verified rules ledger** ([`RULES_LEDGER.md`](RULES_LEDGER.md)) with no rule in use left unverified.

**(B) A documented negative result**: no candidate meets the criterion, with the evidence that shows it.

> **Amended** (D-145): "the criterion" in (A) and (B) is the campaign gate of D-145; the sizing and bankroll report
> uses the lower confidence bound of the edge as the gate does.

A negative result is a real outcome and closes the stage. It is not a failure to be worked around by loosening the
criterion, extending the search until something passes, or reclassifying an exploratory finding as confirmatory.

**In either case, all of the following must also be true:**
- every pre-registration and its outcome is on record ([`prereg/REGISTRY.md`](prereg/REGISTRY.md));
- the decision log is complete ([`DECISIONS.md`](DECISIONS.md));
- the trace check passes;
- the report and deck are built from result files;
- an integrity manifest exists.

The full, checkable list is the **closing checklist** in [`NEXT_STEPS.md`](NEXT_STEPS.md). The stage is closed when
every line of it is true, not by judgement (the rule stage one adopted as propsim D-42).
