# T3 — Analytic ceilings per firm: derivation note (P-01)

Pre-registered as **P-01** (`prereg/P-01_t3-analytic-ceilings.md`), run 2026-10-04 by
`scripts/run_ceilings.py` at commit `9256df5` (manifests: `git_dirty: false`). Result
files, one per firm, each with a sidecar manifest:
`results/ceilings_lucid-trading.csv`, `results/ceilings_my-funded-futures.csv`,
`results/ceilings_funded-next.csv`, `results/ceilings_blusky.csv`,
`results/ceilings_alpha-futures.csv`. Every number below is computed from those files
(`propfirms.reporting.results.read_result`); every rule value entered through
`FirmSpec.value()` — verified rows only, zero unverified rows read.

These ceilings are **oracles** (CLAUDE.md): any T4/T5 simulated number above one of
them is an engine error, never a finding. The method is stage one's
(`vendor/propsim/README.md`, "Mathematical structure").

## 1. The two bounds

**Evaluation P(pass) ceiling.** At zero edge the cumulative P&L X is a martingale,
X₀ = 0. The stage ends at pass (X ≥ G, the profit target) or breach at the drawdown
floor. Under the stage-one conventions — breach truncated at the floor; the floor
starts at −D and never falls (EOD-trailing and intraday-trailing floors only rise, and
every verified lock pins them at or above their prior level) — optional stopping gives

    0 = E[X_stop] ≥ G·P(pass) − D·(1 − P(pass))   ⇒   P(pass) ≤ D / (G + D).

Consistency rules, minimum trading days, daily loss limits and position limits only
restrict the strategy set, so they cannot raise the bound: it holds for **every** fair
strategy.

**Funded E[gross payouts] ceiling.** Let T = account balance (relative to funded
start) + cumulative gross withdrawals. Withdrawals conserve T and trading is fair, so T
is a martingale with T₀ = 0. The firm's floor never falls below its initial level −C
(the verified lock and payout-consequence rows, per firm below), and breach is
truncated at the floor, so balance at account end ≥ −C and

    E[gross withdrawals] = −E[balance_end] ≤ C,   C = the initial cushion.

Where the verified rows bound the account's lifetime total — a finite payout count
times a per-payout cap, or a hard termination — that almost-sure cap K is recorded
beside C and the reported ceiling is min(C, K). This is the structural point D-12
flagged: three of the five funded contracts are **finite sums**, unlike Topstep's
open-ended funded account; K never undercuts C here, but it bounds every single path,
which the open-ended contracts do not.

**Composition (recorded for T5).** Upper bounds compose across the funnel:
E[gross payouts per evaluation attempt] ≤ p̄_eval × min(C, K), and the trader-share
ceiling multiplies by the verified payout split. Fees are **not** subtracted anywhere —
several fee rows are still open (H-6), and omitting a nonnegative cost preserves the
upper-bound property. EV per attempt with fees is T5's job, not T3's.

**Validation oracle.** Applied to the vendored Topstep constants
(`adapter.Rules()`: target 3000, MLL 2000, XFA cushion 2000), the same formulas
reproduce stage one's published ceilings exactly: P(pass) ≤ 2000/5000 = **2/5** and
E[gross payouts] ≤ **$2,000** (`vendor/propsim/README.md`). The script asserts this
identity before writing any firm's file; the run passed it.

## 2. Per-firm structure entering the bounds

- **Lucid Trading (LucidFlex 50K)** — eval G=3000 vs D=2000, EOD trail. Funded C=2000
  (EOD trail from −2000, locks at start+$100; a payout request forces the lock — the
  floor only rises). Finite life: 5 payouts × $2,000 per-request cap, then forced
  live conversion ⇒ K = 10,000.
- **My Funded Futures (Rapid 50K)** — eval G=3000 vs D=2000, EOD trail. Funded
  C=2000: the drawdown is **intraday** trailing (T4 engine extension), but the bound
  needs only "the floor never falls", which holds a fortiori; it locks permanently at
  start+$100 once the HWM reaches +$2,100 — and the verified $2,100 **realized**
  payout buffer means the lock has triggered before the first payout is even
  possible, so the unverified `payout_balance_consequence` row is not an input (the
  script asserts buffer ≥ lock trigger). No lifetime cap derivable (`payout_cap` is
  an open H-6 row): K = none, not needed for the expectation ceiling.
- **FundedNext (Flex 50K)** — eval G=2500 vs D=1500, EOD trail: the only firm whose
  eval ceiling differs from Topstep's (0.375 vs 0.4 — the lowest target in the
  shortlist buys less than its thinner drawdown costs, structurally). Funded C=1500;
  first payout pins the MLL at initial+$100 (floor only rises). Finite life: account
  concludes after the 5th reward, min(50% of cycle profit, $1,500) per cycle ⇒
  K = 7,500.
- **BluSky (Launch 50K)** — **two sequential targets precede any payout** (D-11):
  Phase 1 Evaluation (G=3000, D=2000 trailing) and Phase 2 Buffer (second $3,000
  target at the same $2,000 trailing drawdown — quoted from the same verified
  official article, 16300846, inside the verified rows' notes). Each phase restarts
  the race and the phase-2 bound holds uniformly over entry states, so
  P(reach Sim Funded) ≤ (2/5)² = 0.16. Funded side is **static**: Sim Funded starts
  at balance $3,000 (the matched buffer) over a fixed $100 minimum ⇒ C = 2,900,
  unchanged by payouts. Hard termination: trading stops and a Brokerage Review is
  forced at $10,000 total profit including payouts ⇒ K = 10,000 (the Live transition
  beyond it is out of scope, like Topstep's). The largest funded cushion of the five
  — paid for twice over in the funnel.
- **Alpha Futures (Standard 50K)** — eval G=3000 vs D=2000, EOD trail. Funded C=2000
  (floor locks at the starting balance and is unchanged by payouts — verified
  explicitly). Open-ended account: $3,000/request and ≤ 4 requests/month cap the
  **rate** only, so K = none. Alpha is the only shortlisted firm whose funded account
  keeps Topstep's open-ended long right tail (D-12).

## 3. The ceilings (computed from the result files)

| firm | P(pass) ceiling (eval) | funded cushion C | a.s. cap K | E[gross payouts] ≤ | per-attempt E[gross] ≤ | split | per-attempt net-of-split ≤ |
|---|---|---|---|---|---|---|---|
| lucid-trading | 0.400 | $2,000 | $10,000 | $2,000 | $800.00 | 0.90 | $720.00 |
| my-funded-futures | 0.400 | $2,000 | — | $2,000 | $800.00 | 0.90 | $720.00 |
| funded-next | 0.375 | $1,500 | $7,500 | $1,500 | $562.50 | 0.95 | $534.375 |
| blusky | 0.160 (funnel) | $2,900 | $10,000 | $2,900 | $464.00 | 0.90 | $417.60 |
| alpha-futures | 0.400 | $2,000 | — | $2,000 | $800.00 | 0.90 | $720.00 |
| *Topstep (reference)* | *0.400* | *$2,000* | *—* | *$2,000* | *$800.00* | *0.90* | *$720.00* |

BluSky per stage: phase 1 ≤ 0.40, phase 2 ≤ 0.40, funnel product 0.16
(`results/ceilings_blusky.csv`). The Topstep row is the stage-one reference
(`vendor/propsim/README.md`; split and open-endedness from the same source), shown for
comparison only — it is not a T3 result file.

### 3a. Addendum (P-02, 2026-10-04): MFFU Rapid EOD 50K

The variant that replaced intraday Rapid as MFFU's modelled row (D-17, D-18).
Pre-registered P-02, run at commit `94afed2`, PASS; computed from
`results/ceilings_my-funded-futures-rapid-eod.csv`:

| firm | P(pass) ceiling (eval) | funded cushion C | a.s. cap K | E[gross payouts] ≤ | per-attempt E[gross] ≤ | split | per-attempt net-of-split ≤ |
|---|---|---|---|---|---|---|---|
| my-funded-futures-rapid-eod | 0.400 | $2,000 | — (cap verified as explicitly none) | $2,000 | $800.00 | 0.90 | $720.00 |

Same Topstep-shaped column as the intraday Rapid's, with two record-keeping
differences: K is **verified absent** ("There is no cap on how much you can request
per payout cycle.") rather than merely unstated, and the eval's 30 % consistency rule
(vs intraday's 50 %) forces ≥ 4 profitable days — it lowers the achievable P(pass),
never the ceiling. The floor-locked-before-first-payout argument (§2, MFFU) applies
identically and is asserted by the script.

## 4. Scope and standing assumptions

1. **Truncation at the floor.** Both bounds assume breach losses do not overshoot the
   initial floor — the stage-one engine convention (`floor_mode="truncate"`), matching
   intraday liquidation at the floor. A real gap through the floor would loosen, not
   tighten, the P(pass) ceiling; T4 engines must use the same convention for the
   oracle comparison to be exact.
2. **Zero edge.** These are fair-game bounds for validation and structure ranking
   only. No money decision is taken from them (D-04); comparisons for deployment use
   the campaign's outcome distributions at the edge's lower confidence bound (T5/T6).
3. **Fees excluded.** Eval/reset/payout fees (several unverified — H-6) would only
   subtract from the net columns; every figure here remains a valid upper bound.
4. **Ceilings are suprema, not targets.** D/(G+D) is attained only in the
   consistency-free, ratchet-free limit; stage one measured Topstep's achievable
   P(pass) at 16/49 ≈ 0.3265 against its 0.40 ceiling. The per-firm gap is exactly
   what T5 measures.
5. **MFFU's intraday-trailing mechanics** enter T4 (new engine code), not these
   bounds; the bound above is valid for any floor process that never falls.
6. **BluSky Phase 2 figures** come from quoted official text inside verified rows'
   notes rather than dedicated rule keys; the script parses them with fail-loud
   patterns pinned to the registered yaml hash. If T4 models the Buffer phase in
   detail, dedicated phase-2 rows should be verified first (noted for T4, not a T3
   blocker). *(Update 2026-10-04: dedicated `buffer_*` rows were verified that day —
   D-16 — confirming the figures used here.)*
7. **Precision on BluSky's K (added after the P-03 audit, 2026-10-04).** The
   $10,000 figure is a stop-at-threshold, not a strict pathwise bound: the rule
   stops trading once total profit *reaches* $10,000, and the check lands at the
   day close after that day's payout, so gross payouts can overshoot K by at most
   one final payout (≤ the $2,500 rolling cap at the 50K tier; the P-03 battery's
   replicated maximum was $11,000). `ceilings_blusky.csv`'s hard-cap row should be
   read with this refinement; the reported ceiling min(C, K) = $2,900 is unaffected
   because C binds. Lucid's and FundedNext's caps are exact payout-count sums and
   bind every path strictly (P-03 confirmed pathwise). Recorded in D-21.
