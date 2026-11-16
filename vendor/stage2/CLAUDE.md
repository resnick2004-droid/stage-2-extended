# CLAUDE.md — read this every session

Stage two of the prop-firm trading project (Topstep 50K Trading Combine + Express Funded Account; from D-452 a second
firm, Lucid first). Full charter in [`CHARTER.md`](CHARTER.md); task list in [`NEXT_STEPS.md`](NEXT_STEPS.md). The
research reset of 2026-10-29 is [`docs/HANDOFF_RESET_2026-10-29.md`](docs/HANDOFF_RESET_2026-10-29.md) (D-452, D-453,
D-454); its R-list is the live plan in `NEXT_STEPS.md`.

> **The operator's authority (D-452, 2026-10-29): anything that improves the research — subagents, worktrees, tools,
> workflows — is done without asking, except a payment.** Never authorise a purchase, subscription, billing change or
> credit draw: state the cost and wait. The task list is ordered so that work which can cancel later work comes
> first; something genuinely needed that is not on it is added to the list under a decision row before it is done.
> Out-of-scope ideas go to `PARKING_LOT.md` via `/park`. **The operator does no work except setup:**
> `docs/OPERATOR_SETUP.md` is the only channel for their manual tasks (copy-paste-complete requests). A research
> question never goes to the operator — keep a safe default, record it under a decision row, report status.

## The question, in brief

Does a candidate **campaign** (a strategy executed realistically — real fills, commissions, contract sizes, firm
limits — plus a protocol) make money over time from the prop firms' **contract shape**, and if so, which protocol
(Combine profile, funded profile, payout policy, sizing, number of accounts, number of firms and how signals alternate
between them) maximises long-run growth of cash under reinvestment, given each firm's funded-account cap and the
bankroll the run itself requires? **A signal's own edge is a bonus, reported beside the verdict, never required**
(D-452, the operator). Models are judged on **executions per day, resolution and cost**, built from simple mechanical
patterns (a 15-minute breakout, OHLC patterns). A second firm (Lucid first) adds seats and a second simultaneous
position, one position at a time per firm; a cross-firm hedge pair is modelled only as the arm labelled
`hypothetical_hedge`, never a live plan (Lucid prohibits it in writing, article 11404734).

**The gate (D-145, as amended; the single source is `docs/SUCCESS_CRITERIA.md`, the handoff's R1):** out of sample,
**growth on the required bankroll** — the median path's growth on the bankroll the run itself required
(`pf_growth_on_base_p50` at `pf_required_p90`, D-312) — above zero with the strategy's trade outcomes shifted down to
the one-sided 95 % lower bound of `e`, fees and payout latency applied, the Standard payout path with the Responsible
Trading Program's placement **off** (the operator's rule, D-289; the placement-on reading is reported beside the
verdict, never as it), and the tier-3 payout-denial probability at **0 %** (the operator's rule, D-234; 10 / 25 / 50 %
and the break-even denial are reported beside the verdict, never as a verdict line — P-10's C3 was that conflict,
D-450, D-452). Development: PASS at 0.05/N, CONTINUE at 0.05, else FAIL (D-419). "Median log growth" is the engine's
notional-bankroll column (D-451 F4): reported, not the gate. Where the money comes from (edge or contract shape) does
not decide a candidate. Always reported beside it: `e` and its bound, and whether the old gate (e ≥ 0.10 net, bound
≥ 0.05, propsim D-47) is met.

**Exit criterion — either is a valid close:**
- **(A)** a campaign that passes the gate, with a pre-registered protocol comparison ranked by time-aware
  return, a sizing/bankroll report using the **lower confidence bound** of the edge, and a verified rules ledger; or
- **(B)** a documented negative result: no candidate meets the gate, with the evidence.

Plus, either way: all pre-registrations and outcomes on record, decision log complete, trace check passing, report
and deck built from result files, integrity manifest. The checkable list is the closing checklist in `NEXT_STEPS.md`.

## Settled inputs from stage one — do not reopen (except where the operator reopened them: D-145)

Stage one is vendored read-only at `vendor/propsim/`; cite it as **propsim D-xx**.

- **Contract ceilings** (zero edge, analytic): P(pass) ≤ 2/5; E[gross payouts] ≤ $2,000; supremum of Combine
  P(pass) over all fair strategies 0.327131; 16/49 for 1:1 at $1,500. Use them as oracles — a result outside a
  ceiling is an engine error, never a finding.
- **Conduct rules, three tiers (D-145, reopening propsim D-34/D-36; the operator's instruction):**
  1. *Hard* — cross-account hedging; exploiting simulator fills (tight brackets, auto-breakeven, SIM-fill scalping);
     trading outside the best bid or offer; maximum size into major news; coordinated trading; and **nothing
     designed to conceal a pattern from the firm or evade its detection** (what stands of propsim D-35).
  2. *Modelled* — Responsible Trading Program triggers (losers not smaller than winners, maximum position on most
     trades, several accounts at the MLL in one day): not bans; the simulator applies the verified consequence
     ($1,000 DLL on Combines, Consistency-path-only new funded accounts).
     **D-289 (the operator, 2026-10-05): the placement and its consequences are OFF in the gate's base case and
     reported beside it; contracts at the full verified allowance. The Combine's own consistency target and
     D-156's mid-trade settlement stay.**
  3. *Priced* — account stacking, excessive Combine purchases, the sole-discretion catch-all: not bans; payouts from
     accounts showing the pattern are denied with a stated probability (0/10/25/50 %), pattern measures reported.
- **The research criterion** (propsim D-47: e ≥ 10 % net, lower bound ≥ 5 %, out of sample) is **reported, no
  longer the gate** (D-145; the gate is above).
- **Payout policy is first-order** (propsim D-45) — *with the caveat* that stage one's "buffer" result ignored
  payout latency, reinvestment and per-contract costs. It is a **hint**, not a settled value. Stage two re-derives
  payout policy under the time-aware objective.

The **objective changed** (D-02): EV per attempt is replaced by time-aware return under reinvestment.

## Working discipline

- **Every new model follows the research protocol** (D-155, [`docs/RESEARCH_PROTOCOL.md`](docs/RESEARCH_PROTOCOL.md)):
  hypothesis → contract fit → cheap screen → pre-registration → QuantConnect run → verification → prop environment →
  verdict and one confirmation. Steps 1-4 are the model card (`prereg/MODEL_CARD_TEMPLATE.md`), written before any
  kit; a model's pre-registration is refused unless its card passes `validate_card`, which also checks D-154's
  setups per day.
- vendor/propsim is read-only; import it, never edit it.
- Pre-register every test before running it; the harness refuses unregistered runs.
- A failed pre-registered check is kept on record and diagnosed (terminal states → stage decomposition → component in
  isolation → replication with seeds fixed beforehand); never rerun until it passes.
- Anything chosen after seeing results is labelled exploratory and reported separately.
- Never type a result number into a document; compute it from a result file with a manifest. Seed every simulation.
- Every firm rule used must be verified on the official help centre with article id and date; unverified rules cannot
  be loaded.
- Count every strategy variant tried and report the count with any result.
- Every money decision uses the lower confidence bound of the edge.
- Every sizing, risk or protocol parameter starts from stage one's contract-optimisation results
  (`vendor/propsim/edge/T5_RESULTS.md` §2a; propsim D-45) and cites them. The prop structure is the
  context the execution model is built for: a strategy is sized to the contract, never the contract
  bent to the strategy (D-114).
- Objective is time-aware return under reinvestment; payout latency, ruin and drawdown are always reported beside it.
- Conduct rules are three tiers (D-145, above): tier 1 is hard; tier 2's placement is reported beside the verdict,
  off in its base case (D-289); tier 3 is priced as an enforcement risk and reported. Never design around the
  firm's detection.
- Be direct about what the data cannot show; a negative result is a valid outcome.
- **The signal's job is supply, resolution and cost, not win rate** (D-452; the recipe is the handoff's §4): about
  one decisive trade per account per day, five or more signals a session per firm, every trade resolves (at most 5 %
  unresolved, D-212). Never block contract-shape work on a win-rate search.
- **Confirmation data is declared per market before any development read** (`config/windows.yaml`, R4). NQ's
  held-back window is spent (D-450); NQ from 2026-07-17 is reserved; a read past a declared window raises. Check the
  Combine's headroom over its target against the window's bound before registering (D-451).
- **Pre-register the family, not the model:** one pre-registration per signal-atlas family — its grid, menu, campaign
  plan, selection rule, N and confirmation window. A family takes about a week; a PASS queues behind FV3-C for the
  shadow period and gets no levers (D-419); a FAIL is diagnosed and the family closes.
- **The scoreboard** (`results/scoreboard.csv`, R2) holds every registered run's gate rows side by side; FV3-C's
  confirmation (P-06) is the row to beat, and a candidate that cannot beat it is not pursued (D-365, D-382).
- **Two firms:** Topstep and Lucid, one position at a time per firm (D-429); each firm's rules verified on its own
  official pages; the cross-firm hedge pair is `hypothetical_hedge` only, labelled in every result (D-452).

## Rules that have teeth here

**`vendor/propsim/` is read-only.** A hook denies any write or edit whose target is under it, citing D-01. If the
engine needs to behave differently, write an adapter or subclass in `propedge/` — `propedge/contract/adapter.py`
is the seam. The vendored tree is pinned by `vendor/MANIFEST.sha256` and checked by
`tests/test_vendor_integrity.py` and `tests/test_no_writes_to_vendor.py`.

**Result numbers are never typed into documents.** A number in `CHARTER.md`, a report, a deck or a commit message
comes from a result CSV that has a sidecar manifest (`propedge/reporting/results.py` writes both together:
script, git commit, seed, parameters, timestamp, sha256). `/trace` recomputes the headline numbers from their CSVs
and asserts they appear in the documents. A number you cannot trace is a number you delete.

**Pre-registration before the run.** `/prereg <title>` creates it from `prereg/TEMPLATE.md` and hands it to the
**prereg-gatekeeper** agent, which refuses to register one missing data period, fixed rules, metrics, pass/fail
criteria or seed. `propedge/backtest/harness.py` raises if given no registered id — that is enforcement, not
etiquette. Choosing anything *after* seeing results is fine, but it is **exploratory** and reported separately;
stage one did exactly this and labelled it (propsim D-44).

**The failure protocol.** When a pre-registered check fails:
1. keep the verdict on record — it is a result, not a mistake to be erased;
2. diagnose: terminal-state audit → stage decomposition → component test in isolation → replication with seeds
   fixed **before** running;
3. **never rerun until it passes.**
Stage one applied this to its own failed check and diagnosed it as a false alarm (propsim D-40); the discipline is
what made that credible.

## Agents and commands, and when to use them

`.claude/agents/` — invoke with the Agent tool, or through the command that wraps them:

| agent | when |
|---|---|
| **rules-verifier** | any firm rule you are about to rely on. Official help centre only; never verifies from a third-party page |
| **prereg-gatekeeper** | before any test run — it assigns the id and registers it |
| **auditor** | after a result matters. Re-derives the numbers from the CSV *without* the producing code, checks the pre-registration was followed, flags unlabelled post-hoc choices |
| **data-integrity** | before any data enters the harness. Schema, gaps, duplicates, timezone, session boundaries, look-ahead. Blocks unvalidated data |
| **results-tracer** | before any document is considered done |

`.claude/commands/` — `/prereg` `/decide` `/park` `/verify-rule` `/validate` `/audit` `/trace` `/close-check` `/status`.

`.claude/skills/` — **prereg-discipline** (how to write and follow a pre-registration here; the failure protocol),
**result-provenance** (sidecar manifests, how documents cite results, how the trace check works),
**contract-engine** (how to use the adapter and the pluggable draw; the settled stage-one facts and their sources).

## Practical notes

- Python 3.12. `python -m pytest -q` for the suite; `make verify` (or `.\scripts\make.ps1 verify` on Windows) for
  integrity plus tests.
- The private GitHub remote is `origin` (`stage-2-propedge`, D-453); push after every commit.
- Hashing: `sha256sum` on Linux, `shasum -a 256` on macOS, detected at run time by `scripts/hashes.py`; that
  module's `hashlib` path is canonical on Windows and in tests. Manifests are in native `sha256sum` format.
- Every function that produces a number takes an **explicit seed** where randomness is involved. No implicit
  global RNG, ever — a result you cannot reproduce is not a result.
- Modules with `NotImplementedError` are waiting on a human decision or data, not on you inventing a value. The
  docstring says what is needed; `docs/HUMAN_INPUTS.md` is the full list.
