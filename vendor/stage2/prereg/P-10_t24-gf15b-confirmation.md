# P-10 — T24-GF15b's one confirmation: the frozen protocol on NQ's held-back window

> Drafted 2026-10-25 with T24-GF15b's development test (D-439), before any kit of the held-back window exists. Everything it
> fixes is `scripts/t24_confirm.py` and `config/t24_confirm.yaml` at the commit that registers it; the kit is generated only
> under this registration (D-81). **Runnable only after T24-GF15b's development test (P-09) is a PASS or a CONTINUE --
> enforced twice in code:** the kit is not generated before it (`run_kit._t24_development_continues`), and the verdict
> script refuses before it (`t24_confirm.development_verdict`); a FAIL there leaves this registration unrun and NQ's window
> unread. (D-437 (4) named the confirmation "P-09" before the correction; the ids are the gatekeeper's.)

| field | value |
|---|---|
| **id** | P-10 *(assigned by the prereg-gatekeeper, 2026-10-25)* |
| **date** | 2026-10-25 |
| **author** | stage-two session, for the operator (Ryan Resnick) |
| **task** | T24 (D-425 to D-439): T24-GF15b's one-shot confirmation on the held-back window (D-237); T5 |
| **protocol step** | 8 of `docs/RESEARCH_PROTOCOL.md` (D-155): the verdict's one confirmation |
| **status** | registered |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 1 |
| `development_period` | 2020-01-01 .. 2025-06-30 (T24's capture; every screen and both development tests read it) |
| `confirmation_period` | 2025-07-01 .. 2026-07-16 (QuantConnect's NQ data end, as P-06 found it; nothing from 2026-07-17 is read) |
| `confirmation_tests_on_this_market` | 2 (P-05, P-06; this is NQ's third and last of D-107's three) |
| `bonferroni_alpha` | not required: a held-out confirmation period is used |
| `assumed_sd` | 1.226 |
| `assumed_sd_source` | measured on development data: the sample standard deviation of `r_1.5` over T24-GF15's offered growth trades (P-08's `edge` row, R 1.5; the gap's booking moves gross and cost, not the net R) |
| `risk_denominator` | intended -- the policy's dollar risk at each trade's stop in whole micros, the allowance and the room cap applied |
| `primary_metric` | median_log_growth -- the median path's growth on the bankroll the run itself needed (p90 across paths plus one subscription), a year's rate (D-312) |
| `data_period` | 2025-06-20 .. 2026-07-16 (the kit's warm-up from 2025-06-20 records nothing); of the development files only the frozen map (`results/t24_exec_m40.csv`) and R137's 2025 spreads (its first half, R137 ending 2025-06-30) are read |
| `seed` | 20261028 (the development tests' campaign seed) |
| `model_card` | docs/candidates/cards/T24-GF15b.md |
| `power_rr` | 1 (the Combine's R) |
| `power_effect` | 0.00 (the card's `edge_assumed`) |
| `boot_len` | 21 (the bound's block: 21 sessions -- D-237 (4): the window is too short for yearly blocks) |
| `required_trades_source` | assumed_sd fallback: the L5 curve gives the trades needed to find a planted positive edge, and this test looks for none -- the side is a coin and the campaign decides at the bound |
| `required_trades` | not an edge search: the gate reads the campaign at each R's bound over about twelve 21-session blocks of the window |
| `available_trades` | 4184 (the development rate, 17.22 offered trades a day, times about 243 sessions -- the window's trading days less its FOMC days and early closes; an estimate before the read) |
| `ledger_n` | 16 -- `count_n` for T24-GF15b, pool `pool-2026-10-24-t24`, NQ, minute, 2020-01-01 .. 2025-06-30 |

**Multiplicity plan.** T24-GF15b was chosen on development data only (the pool, N = 16, its own development test under its
registration). The held-back window is read here once, for one configuration frozen in advance; the decision is this single
test at the registered one-sided 0.05 with no selection on it (D-230: D-189's 0.05/N binds verdicts read on development
data; a confirmation decides at its registered level, the family-wise control being D-107's cap of three tests a market).
The bounds at 0.05/N are reported beside, never as the verdict. **The window is unread for these trades:** P-05 read NQB1's
two no-edge brackets there (R088) and P-06 FV3-C's records (R139-R141) -- other entries, brackets and records; no step of T24
has read a day of it, and this kit is its first capture of these brackets at these times.

**Power, stated before the read.** About twelve blocks of 21 sessions, so the bound is wide; a FAIL may reflect the bound's
width rather than a changed market, and the consequence stays as registered. The point arm and each period's campaign are
reported beside.

---

## 1. Question

Does T24-GF15b -- frozen on development data and passed (or continued) there -- grow its cash on Topstep's contract on
data no step has read, at the bound, under P-06's four lines? A **PASS** meets the D-145 gate out of sample for this
candidate (exit (A)'s campaign); a **FAIL** ends T24-GF15b on NQ, kept on record and diagnosed, never rerun.

## 2. Data period

- **Source**: QuantConnect NQ minute bars, actual prices, tied minutes settled on second bars -- one kit, R152-t24c-NQ-2026
  (`config/t24_confirm.yaml`): T24's kit (D-428), unchanged but for the window, whose identity against R147/R148 held exactly.
- **Symbols and resolution**: NQ, MNQ micros and NQ minis for sizing; minute.
- **In-sample**: none read here (the frozen map is read from `results/t24_exec_m40.csv`).
- **Out-of-sample**: 2025-07-01 .. 2026-07-16, read once. Counted periods: 2025 H2 and 2026 H1; 2026 Q3 (to July 16)
  reported, not counted.
- **Walk-forward scheme**: none -- one frozen configuration.

## 3. Rules fixed before the run

- **The protocol**: T24-GF15b exactly (its card and D-439): the m40 map and its offered targets READ from
  `results/t24_exec_m40.csv` (never recomputed on the window); the coin (seed 20261025, one draw a time and day); entries five
  bars late; no entry before the 07:30 CT cut on a BLS report day; the Combine 1:1 at $1,600 two-shot; the growth trade $1,600
  at 1:1.5 at or below the start; $240 flips above it; every state closed once its room cannot carry its full trade (D-336's
  reading of closing at the trader's request; `xfa_closure_at_request` is unverified, and this plan leans on it more than
  P-08's, every state now closing); strictly one position across five
  accounts, five minutes flat between (D-429).
- **Costs**: each trade's own inside its R -- the round turn (`config/fills.yaml`, `assumed`), the slot's measured entry
  spread from R137 at its **2025 value** (R137's latest year, its first half to 2025-06-30; the window's spreads are not
  measured -- a stated assumption),
  a tick and the gap on a stop booked as a cost; fees re-priced at minis (D-324).
- **The campaign**: P-08's -- rotation, routing to the account able to take it, the cross-account rule under the strict rule,
  each position to its own exit, the Standard path, the largest payout, `aeropay`, the seat freed the same evening (the
  favourable reading), D-313's room cap on both legs (pessimistic settlement exact under it), the bankroll an output, 500
  paths over 504 days resampled from the window's days, one subscription's margin.
- **Usability of the kit, one mechanical test (D-230 (3)), judged from the log's `HEAD` and `END` lines alone before the
  ingest runs**: unusable if `END` is missing, the backtest stopped with an error or a time limit, `orders` reached 10,000, or
  HEAD reports fewer than 230 days. The judgement -- the two lines quoted and the verdict -- is recorded in a decision and
  committed before `scripts/ingest_flip_run.py` parses anything. Unusable: one fixed kit (mechanics only, recorded in a
  decision before it runs) may follow; a second unusable run is a FAIL.
- **Parameters, with their exact values**: `scripts/t24_confirm.py`'s and the frozen scripts' constants; k = 1.

**Conduct check in D-145's three tiers:**

- Tier 1, hard:
  - [x] no cross-account hedging -- no two accounts ever hold a position at once
  - [x] no reliance on simulator fills or fills outside the best bid or offer -- market entries five bars late at the
    measured spread; 20 and 40-point brackets
  - [x] no maximum size into major news; no coordinated trading -- FOMC days out, never held into a BLS 08:30 ET release, no
    entry before its cut; one position on one account at a time. A stated limit: other scheduled releases (GDP, PCE, retail
    sales, jobless claims at 08:30 ET; 10:00 ET releases) are not excluded, so the 06:00, 07:00 and 09:00 CT trades can be
    open into one at the growth trade's full size; Topstep's wording (10305426) does not define "major". The project's
    definition (FOMC and BLS 08:30 ET) is kept as the safe default, as at P-06, and disclosed
  - [x] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled: R at or below 1 on the Combine and the flips; maximum position on the growth trade; the placement off in
  the base case (D-289), on beside.
- Tier 3, priced: 0 % denial in the verdict's arm; 10, 25 and 50 % beside; C3 reads the break-even denial. **A limit
  (P-08's audit F3):** the engine denies only payouts exposed by repeated loss-limit breaches in a trailing window, and this
  plan ends accounts by closure, not breach, so the 10 % arm will move little and C3 rests on the break-even denial; the
  Combine purchase pattern is not priced.

## 4. Metrics

- **Primary**: the campaign's median growth on its required bankroll at p90 (`pf_growth_on_base_p50`), each R's outcomes
  shifted to the one-sided 95 % bound of its mean over 21-session blocks of the window, 0 % denial, the placement off.
- **Also reported, never the verdict**: the point arm; each counted period's own campaign; the bounds at 0.05/N; 10, 25 and
  50 % denial; the placement on; the zero-edge twin; each R's e, bound, gross, cost and net; each offered R's unresolved share
  overall and by period; the deflated Sharpe and `haircut.widened`'s bounds; the required bankroll, the days to the first
  payout, payouts, ruin (zero by construction) and drawdown; the strict rule's refused share; the Combine purchases.

## 5. Pass / fail criteria

**PASS** only if all four lines are met -- P-06's lines as `scripts/confirm_fv3.py` reads them (D-355), with resolution of
every offered R standing for its flatten share (`scripts/t24_confirm.py`'s `lines`):

- **C1** -- the gate: the primary metric above zero.
- **C2** -- every counted period's own campaign (its trades resampled within it, at the point) grows on its required
  bankroll, **its activity bound is above one half, and no path's Sharpe changes sign without its idle blocks** (D-305; the
  activity line reads exactly what P-08's F1 was): 2025 H2 and 2026 H1.
- **C3** -- the gate row's break-even denial at least 0.25, and the bound arm still growing at 10 % denial.
- **C4** -- every offered R resolves (at most 5 % unresolved overall and in each counted period), the realised risk is at
  least 0.9 of the allowance-capped intention, **and no counted period is without a trade**.

**FAIL** otherwise. **What a fail means**: T24-GF15b ends on NQ, kept on record and diagnosed by the failure protocol, never
rerun; NQ's held-back window is spent. **What a pass means**: the D-145 gate met out of sample for this campaign; the
pre-deployment protocol (a shadow period) before any real money (D-337).

## 6. Seed

- **Seed**: 20261028 (the campaign's resampling). The coin's seed 20261025 is part of the protocol.

## 7. Variants

- Configurations already tried for this question: the ledger's pool, N = 16.
- Configurations this pre-registration will try: 1.

## 8. Anything chosen after seeing results

Nothing.

---

## Outcome

- **Date run**: 2026-10-29, once, by `scripts/t24_confirm.py --prereg P-10` from the clean tree at 35d9fc9 (the peer
  sessions holding, the terminal's Docker stopped for memory, a job watcher beside it), on
  `results/manual_R152_t24c_NQ_2026.csv`: the operator's one QuantConnect run of 2026-10-26 (R152), usable by D-448's
  mechanical test committed before the ingest, ingested after D-449's fix to the ingest.
- **Result file**: `results/t24_confirmation.csv` with its manifest (`exploratory: false`, `prereg_id` P-10, `variant_count`
  1, seed 20261028; sha256 `75b27efe2dcc`).
- **Verdict**: **FAIL** -- C1, C2 and C4 met, **C3 not met** (`verdict` row): the gate row's break-even denial
  (0.237) is below C3's 0.25, though the bound arm still grows at 10 % denial (median log
  growth 0.000084). As §5 states: T24-GF15b ends on NQ, kept on record and diagnosed by the
  failure protocol, never rerun; NQ's held-back window is spent. Not exit (A); no money decision.
- **The lines** (the file's rows):
  - **C1 met:** the gate's campaign at each R's one-sided 0.05 bound, 0 % denial, the placement off: median log growth
    0.000084; growth on the required bankroll 0.614 at the median path,
    0.279 at p10 (the point arm 0.986).
  - **C2 met:** 2025 H2 and 2026 H1 each grow at the point (1.058, 0.949),
    activity bounds 0.899 and 0.907, no idle blocks, no path's
    Sharpe changing sign without them.
  - **C3 not met:** break-even denial at the bound 0.237 (the point arm
    0.375); the bound arm at 10 % denial still grows. P-09's development figure was
    0.313, disclosed before the run as the line with the least margin (D-447).
  - **C4 met:** unresolved shares R 1 0.0002; R 1.5 0.0000; R 2 0.0018; R 3 0.0080, the worst in a counted period 0.0165; realised to capped intention
    1.000; both counted periods traded (4712 trades at R 1 on
    271 days).
- **First diagnosis** (stage decomposition, from this file and P-09's; the audit's replications follow): the window's
  point edge is close to development's -- net e at R 1 -0.0466 against -0.0546 (better), at R 1.5
  -0.0547 against -0.0467 (worse) -- but one year carries 4712 trades at R 1 against
  24455, so each R's bound lies further below its point: the shift to the bound at R 1 -0.0318
  against -0.0117, at R 1.5 -0.0465 against -0.0191. The bound arm's campaign
  earns less for the payouts it puts at risk (growth on the required bankroll 0.614 against
  P-09's 0.834), and the break-even denial falls with it. Mostly a shorter window's wider
  bound (at R 1.5 the bound's shift widened more than three times as much as the point fell) rather than a worse edge -- but C3
  reads the gate row, and the verdict stands.
- **Beside, never the verdict:** at the ledger's N = 16 the bound arm does not grow
  (-0.350); the placement on, point -0.595 and bound
  -0.658; the zero-edge twin 1.152, more than the measured
  trades -- the money is the contract's shape; each R's net e and bound below zero (R 1 -0.0466 /
  -0.0784; cost 0.0447 R against gross -0.0019 R), propsim D-47's criterion
  not met; the deflated Sharpe of the block means 2.21e-08 (R 1); 2026 Q3 (2026-07-01 to
  2026-07-16, not a counted period) -0.273. The denial arms at 10, 25 and 50 %
  0.615, 0.613, 0.610
  (closures are not breaches, so they never see the purchase pattern -- P-09's audit F2). **Risk** (the bound arm): the
  required bankroll at p90 $6,970; the bankroll's largest drawdown mean $5,909,
  p90 $8,660; red months at the median path 38 %; underwater
  133 days at the median path; the first payout at a median 17
  days. **Pattern measures (tier 3, priced, never the verdict):** Combine purchases 670.0 a path
  over 504 days, at most 51.1 in 21 days on the mean path; Combines
  closed at the trader's request 0.780, funded accounts 0.957;
  the Focused Trader Program's undefined "excessive recycling" carried beside (D-447).
- **What it means**: the D-145 gate's own metric (C1) is met on this window, but the confirmation also required that the
  growth survive the firm denying a quarter of the payouts (C3), and at the bound it does not. For a campaign whose money is
  the contract's shape, bought with many Combines, that is the line that matters most. T24-GF15b ends on NQ.

## Addendum at registration (D-442, 2026-10-25)

2026-10-25, before any kit of the window exists, by the prereg-gatekeeper on its third review. No rule or line changes;
three things the text above leaves to the frozen code, written down, and the conditions for the reader:

- **The second seed.** `haircut.widened`'s day bootstrap and the deflated Sharpe rows reported beside the verdict
  (`scripts/t24_gf15.py`'s `sharpe_rows`, called by `scripts/t24_confirm.py`) use seed **20261017** (2,000 draws, 21-day
  blocks), P-09's additional seed; nothing in C1-C4 reads them.
- **propsim D-47's criterion** (e at least 0.10 net and its bound at least 0.05) is reported beside the verdict, per R,
  from the `edge` rows' `e` and `lb` -- never part of C1-C4.
- **`available_trades`** multiplies a rate taken over all 1,420 development days (FOMC days and early closes, which
  carry no trades, included) by about 243 sessions that exclude them, so it understates the expected count slightly; it
  is an estimate before the read and decides nothing.
- **Conditions.** NQ's count of confirmation tests is 2 before this one (P-05, P-06); this registration is the third of
  D-107's three, so no further confirmation on NQ's window is possible without a `DECISIONS.md` entry. The closing of every
  state rests on `xfa_closure_at_request` (`unverified_human_input_required`; the engine reads no value from it). Usability
  is judged from the log's HEAD and END lines alone; HEAD's `days` counts every day record, FOMC days and early closes
  included (as R151's ingest record, `runs/R151-t24-NQ-2025/ingested.json`, shows against its day records). The ordering -- the judgement committed before
  `scripts/ingest_flip_run.py` parses -- is enforced by procedure, not code. If P-09 reads FAIL, this registration is
  recorded `abandoned` (not run) with that reason, never left open.

## Addendum before the run (D-447)

2026-10-25 (HST), after P-09's PASS (D-443) and its audit (D-447), before the kit was run and before any record of the window
exists. Nothing in §1-§8 changes; this records what the reader of P-10's verdict must carry.

- **The kit:** `runs/R152-t24c-NQ-2026/` (class `T24ConfirmNQ`, 2025-06-20 warm-up, to
  2026-07-16; normalised sha256 `77a6935ec87f842d`), generated once `config/t24_confirm.yaml`'s
  `prereg_id` was set to P-10 -- the config's one difference from the registering commit (D-81, D-442 (4)). Its `EXPECTED.md`
  repeats T24's general wording for an unusable run; **§5's mechanical test governs** (END, an error or time limit, orders at
  10,000, HEAD days below 230), judged from the log and committed before the ingest parses.
- **P-09's audit F1, carried into this verdict:** the engine credits a payout still in flight when its account closes. What
  the help centre says: a payout requested before a loss-limit breach is still paid (`payout_after_request_survives_mll_breach`, verified on 8284233, D-445), so the engine's credit agrees for breaches; for a closure at the trader's request the help centre is silent, so most of F1's in-flight payouts rest on an assumption, and the execution that does not is to hold the account until its payout clears. The closing at request is presupposed (8284217, 10657969) but never described (`xfa_closure_at_request` stays unverified, D-444); when a closure frees a funded seat is unstated (`xfa_seat_frees_at`, unverified, D-446), so the same-evening seat stays an assumption (D-353). **And the Focused Trader Program (10551016)** names, without a threshold, "Excessive recycling of Trading Combines® or XFAs" (its Corrective Path: "All current accounts (Live, Express Funded Account, Trading Combine) are closed", "No refunds are issued", "Any pending payouts are denied") and "Excessive Resets and Trading Combine purchases" and "Activating and losing many Express Funded Accounts in a short period of time" (its Slowdown Path: "You cannot purchase new Trading Combines, Resets, or B2F Reactivations"); this plan's purchase and activation rate very likely fits, and those consequences end a campaign -- heavier than tier 3's pricing, which takes payouts only. By the operator's rules (D-145's tier 3 priced, D-234's 0 % denial) it is reported beside the verdict, never as it.
- **F2 and F3 carried:** the purchase pattern unpriced by the denial arms (C3's break-even denial is the scale), the closing
  at request and the same-evening seat. P-09's break-even denial at its bound is 0.313, against
  C3's 0.25: C3 has the least margin of the four lines (the audit's §8, development figures, not a prediction).

## Addendum after the run (D-451)

2026-10-29. **The audit** (`docs/audits/p10_t24_gf15b_confirmation_audit_2026-10-29.md`, the auditor agent, without the producing code) **CONFIRMS the FAIL**, clean with
caveats: every line re-derived from the file's rows as P-10 §5 reads them; every trade-level cell rebuilt from the capture
with the auditor's own code (and P-09's from R149-R151); provenance, hashes and N = 16 checked; the pre-registration
followed in every item checked (the frozen map, the report-day cut, the delay, the plan, the seeds, the counted periods,
D-448 before the ingest, D-449 changing only the id's handover); no post-hoc choice; the oracles inside stage one's
ceilings (the zero-edge twin's Combine pass rate and gross payouts a Combine). The FAIL replicates on two fresh campaign
seeds fixed before running (the audit's §7.5). The failure protocol's diagnosis is the audit's §7: a real failure of the
registered line -- neither a false alarm nor an engine fault -- the outcome §5's power statement named ("a FAIL may reflect
the bound's width rather than a changed market"). Carried with the verdict:

- **F1 (moderate; how to read the FAIL):** the bound reaches the campaign through a threshold in the Combine. The gate's
  shift (D-145: each trade's outcome moved down to its R's lower bound) acts as a flat extra cost on every trade, winners
  included; two $1,600 wins at 1:1 have $200 of headroom over the $3,000 target, and with the 2025 spreads the window's R 1
  shift uses it up at some of the 22 times, so those Combines need a third, coin-flip trade and the pass rate falls -- at
  P-09's width it does not move (the audit's §7.3-§7.4, reproduced by a component test without the engine; both the shift
  and the spreads are needed). About half the fall in break-even denial comes this way. Not a defect: the shift is the
  gate's definition and the spreads are registered. For any later card keeping the two-shot $1,600 Combine, that headroom is
  the binding margin -- a fact recorded, not a recommendation.
- **F2 (low; the first diagnosis as worded in the Outcome, D-450 and the REGISTRY row):** right in direction and size (the
  audit's §7.6 puts the width between most of the fall and more than all of it, depending on the order it is measured in; development's own trades at
  P-10's widths would also have failed C3), incomplete in mechanism. The width is set by the number of 21-session blocks --
  13 against P-09's 68 -- not by the trade count the Outcome cites; the registered coin's draw sits in the wide tail of
  other coin seeds (the audit's §7.3); and the Combine threshold (F1) and the 2025 spreads (F3) are part of it.
- **F3 (low; an assumption now load-bearing):** the 2025 spreads (R137's first half of 2025, applied to every window trade
  by P-10 §3) are the widest year measured at every time, and F1's threshold binds only with them (the audit's §8 F3). The
  assumption cuts against the candidate.
- **F4 (low; presentation):** the Outcome's "median log growth" figures are the engine's notional-bankroll column; C1 and C3
  read growth on the required bankroll -- at the bound 0.614, and 0.615 at
  10 % denial. Same sign, verdict unaffected; P-10's machine-checked `primary_metric` shares the name.
- **F5, F6 (informational):** the gate row picked by shift and denial level rather than by its flag, and C4 reading an
  identically valued column -- the same rows and values here; every carried assumption stated in P-10 and its addenda.
- **F7 (informational; the audit's own process):** the auditor wrote its seeds into the note before any replication ran,
  overwrote that section mid-audit and restored it verbatim (the audit's §11, a copy in the session's scratchpad); the note
  was uncommitted then, so the order rests on the auditor's statement. No seed or arm changed.
- **Not verified** (the audit's §10): the engine's path-level figures beyond consistency, determinism and fresh seeds; the
  capture against market data (the run code attested, D-131); the window's real spreads; the unverified closure and seat
  rules and the Focused Trader Program's threshold.
