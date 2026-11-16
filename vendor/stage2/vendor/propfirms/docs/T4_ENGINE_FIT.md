# T4 — Engine fit per firm (working document)

Status 2026-10-04 (final): **T4 CLOSED (D-20)** — P-03 validation battery PASS,
26/26 cells (`results/t4_validation.csv`; audit in `docs/audits/`). The one
carve-out is BluSky Buffer chaining, blocked on H-6 `buffer_entry_balance` (§3).
Earlier status line kept below for the record.

Status 2026-10-04 (second update): **T4a complete; T4b complete**
(`propfirms/contract/evals.py` + `tests/test_eval_fit.py`); **T4c core built** —
`propfirms/contract/engine.py` carries the EOD-trail/static funded chassis with
configs for Lucid, FundedNext, Alpha and BluSky, validated by exact degenerate
agreement with the vendored XFA, rule-text golden paths, and the T3 ceilings
(`tests/test_funded_engine.py`); **T4d (pre-registered validation battery) pending.**
Both D-15 captures landed: BluSky Buffer rows (D-16, 8 verified/3 open) and MFFU
Rapid EOD 50K (D-17, 29/32 verified). **Headline from D-17: Rapid EOD's funded stage
is EOD-trailing with the +$100 lock — the intraday-trailing mechanic is demoted from
blocking T4 to a feature of the intraday Rapid variant only.**

Method per `docs/RESEARCH_PROTOCOL.md` §4: for each firm, record which mechanics map
onto the vendored engine directly, which map with `Rules(...)` parameter changes, and
which it cannot express — the last are implemented in `propfirms/contract/engine.py`
with their own tests, validated against the T3 ceilings (`results/ceilings_<slug>.csv`,
D-13) and against degenerate cases where they must agree with the vendored engine.
`vendor/propsim/` is never edited (D-01).

## 1. Evaluation side: the vendored Combine engine covers all five firms

`vendor/propsim/propsim.py::simulate_combine` already parameterizes everything the
five evaluations need:

- **Trailing floor semantics match exactly.** All five evals are EOD-trailing with the
  breach tested continuously against floating equity (verified `eval_drawdown_type`
  rows; FundedNext's "the LEVEL trails end-of-day, but the breach test is continuous"
  caveat is the general pattern). The engine does precisely this: cushion is checked
  per trade with floor liquidation intraday (`floor_mode="truncate"`), the floor level
  ratchets at the day close, `combine_mll_lock_at` pins the lock.
- **Consistency semantics match exactly.** Every firm's eval consistency is the soft
  "keep trading until best-day/total ≤ f" form, which is literally the engine's
  `target_eff = max(profit_target, best_day / consistency_max_day_frac)` (the pass
  requires `B ≥ target_eff` at the day-close check). Verified formulas: Lucid 0.50,
  MFFU 0.50 ("trade additional days until consistency is met"), FundedNext 0.40
  ("Required Total Profit = Highest Daily Profit / 40%"), BluSky 0.50 (not a fail),
  Alpha 0.50 ("You will not pass your Evaluation until this rule is satisfied").
- **Minimum trading days are non-binding.** At f ≤ 0.5 a one-day pass is arithmetically
  impossible (total = best day ⇒ ratio 1 > f), so MFFU's and Alpha's explicit 2-day
  minimums are automatically satisfied, and FundedNext's unverified `eval_min_days`
  row is not needed: f = 0.40 forces total ≥ 2.5 × best ⇒ ≥ 3 days. No engine change.
- **No eval DLLs.** MFFU/FundedNext/BluSky: none (verified). Alpha: none on
  evaluation (verified). Lucid: optional at checkout — **campaign modelling choice:
  DLL OFF** (verified as a legitimate checkout option; the DLL-off variant prices
  higher, which lands in the open `eval_fee` row, H-6).

**Per-firm `Rules(...)` parameters** (built by `propfirms/contract/evals.py` from
`FirmSpec`, verified rows only; cumulative-P&L convention, start = 0):

| firm | profit_target | mll | combine_mll_lock_at | consistency_max_day_frac | fee basis (enters T5 EV, not P(pass)) |
|---|---|---|---|---|---|
| lucid-trading | 3000 | 2000 | +100 | 0.50 | one-time, price open (H-6) |
| my-funded-futures | 3000 | 2000 | +100 | 0.50 | one-time $209 |
| funded-next | 2500 | 1500 | +100 | 0.40 | one-time $133.99 / $69.99 first two / $79.99 3rd+ ; reset $77.99 |
| blusky (phase 1) | 3000 | 2000 | **open row** (H-6) | 0.50 | $/30 days, price open (H-6); reset $49 |
| blusky (phase 2 Buffer) | 3000 (verified, D-16) | 2000 EOD trail (verified) | **open row** (`buffer_drawdown_lock`, H-6) | 0.34 pass gate (verified) | reset $250 ×3 then +$50 per three (verified); no DLL |
| alpha-futures | 3000 | 2000 | 0 (locks at start) | 0.50 | $129/month subscription; reset $109 |
| my-funded-futures-rapid-eod (variant, D-17) | 3000 | 2000 | +100 | **0.30** (eval only — forces ≥ 4 profitable days) | one-time $225; reset policy open (H-6) |

Notes with teeth:

1. **BluSky's eval lock is an open rule** (`eval_drawdown_lock`,
   unverified_human_input_required). Until H-6 answers it, BluSky eval simulations are
   run as a **labelled bracket**: lock = None (floor trails forever — strictly worse
   for the trader) vs lock = +100 (the pattern every sibling firm follows). Both
   labelled; no silent default. The T3 ceiling is unaffected (locks only raise the
   floor).
2. **Fee clocks**: Topstep's subscription cycle is in the engine
   (`subscription`/`billing_days`); Alpha's $129/month maps to it (≈21 trading
   days/month — approximation to be stated wherever used). One-time fees are charged
   outside the engine in T5's EV accounting — cleaner than abusing the subscription
   cycle.
3. **Pass timing convention**: the engine checks the pass at the day close (stage
   one's verified Topstep convention). No firm's verified rows state an
   intraday-vs-close pass check explicitly; the close-check convention is carried as
   an assumption and recorded here.
4. **BluSky funnel**: Evaluation → Buffer is two chained Combine-shaped stages (second
   target at 0.34 consistency); `propfirms` gets a thin chaining wrapper. Blocked on
   the Buffer-phase verified rows (capture in flight); the launch fee ($99, 14-day
   deadline, forfeiture if unpaid) sits between the stages in EV accounting.
5. **Exact chains**: `combine_exact` (vendored) gives exact P(pass) for specific
   policies; its parameterization will be checked in T4b and used wherever it admits
   the firm's (target, mll, frac, lock) — otherwise MC with the T3 ceiling as oracle.

## 2. Funded side: the vendored XFA engine is Topstep-specific — new engine required

`simulate_xfa` hard-codes Topstep's payout machinery (standard/consistency paths,
50 %-of-balance cap, floor jumping to `xfa_lock_at` on every payout). What each firm
needs beyond it (verified rows; this is the requirements list for
`propfirms/contract/engine.py`, carrying D-14's state machinery):

| mechanic | Lucid | MFFU Rapid | FundedNext | BluSky | Alpha |
|---|---|---|---|---|---|
| floor type | EOD trail, lock +100 (≈ expressible) | **intraday trail**, lock +100 (**new**) | EOD trail, lock +100 (≈ expressible) | **static** −2,900 (trivial config) | EOD trail, lock 0 (≈ expressible) |
| floor on payout | forced lock +100 (≈ engine) | already locked pre-payout (no-op) | pinned +100 at first payout (≈ engine) | unchanged (**new**: engine forces a jump) | **unchanged** (**new**: engine forces a jump) |
| payout gate | per cycle: net ≥ $1 **and** 5 days ≥ $150 (**new**: every-cycle net test) | daily after **$2,100 realized buffer** (**new** gate) | 5 benchmark days ≥ $200 **and** cycle profit ≥ $500 (**new** combo) | daily Mon–Fri above start; 1 "meaningful" day between requests (wording conflict on file) | 5 days ≥ $200 **and** 40 % consistency since last request (**new** combo) **and** ≤ 4 requests/month (**new** rate limit) |
| per-request cap | min(50 % profit, $2,000) (≈ engine) | **open row** (H-6) — blocks T5 cap modelling, not the engine | min(50 % accumulated, $1,500) (≈ engine) | $2,500 per rolling 7 days (**new** window cap) | min(50 % profit, $3,000) (≈ engine) |
| lifetime terminator | **5 payouts → moved live** (**new**) | none derivable | **5 rewards → concluded** (**new**) | **$10k total profit → stop & review** (**new**) | none (open-ended) |
| day/size state | position scaling by profit band (2/3/4 minis; EOD update) — binds T5 $-risk grids | none stated | fixed contracts | profit caps $5k/day, $10k/week (**new** day/week stops) | **$1,000 DLL** incl. unrealized (**new** soft day-stop); scaling ladder (tiers garbled — re-read flagged, D-08) |
| split / min | 0.90 / $500 | 0.90 / $500 | 0.95 / $250 | 0.90 / $500 | 0.90 / $500 |

**The one genuinely hard mechanic is MFFU's intraday trail.** The floor follows the
intraday equity high-water mark *including unrealized gains*, so the state updates
inside the trade: a favorable excursion on a trade that ultimately loses still raises
the floor permanently. In the binary-trade model this requires the distribution of the
**maximum favorable excursion (MFE) of losing trades** — the mirror of stage one's MAE
law (`vendor/propsim/README.md`: distribution-free excursion laws for continuous
martingales). T4c derives the MFE law the same way, with its own tests; until then no
MFFU funded simulation runs. (If the Rapid EOD capture verifies EOD-both-stages, the
variant's funded side needs none of this.)

**Chassis design for `propfirms/contract/engine.py`** (T4c): one vectorized funded
simulator over a `FundedConfig` — floor process {eod_trail(lock), intraday_trail(lock,
MFE law), static}, floor-on-payout policy {jump_to_lock, unchanged}, composable payout
eligibility (winning-day counters with per-cycle reset, cycle-net minimums,
consistency-since-request, realized-profit buffers, calendar rate limits), request
sizing (frac-of-profit, per-request cap, rolling-window cap, minimum), terminators
(payout count, total profit, horizon), day-state mechanics (DLL stop, profit-cap
stop), split/fee at payout. Per-firm configs built from `FirmSpec` (verified rows
only). Validation: golden paths from the rule text via `ScriptedDraw` (stage-one
style), degenerate agreement with the vendored XFA under Topstep's config, zero-edge
martingale checks (`mean_T ≤ 0`), and the T3 ceilings as oracles — all as tests, then
the pre-registered T4d battery with result files.

## 3. Open items (updated after D-16/D-17)

- **Rapid EOD ceilings: DONE (P-02, PASS, 2026-10-04)** —
  `results/ceilings_my-funded-futures-rapid-eod.csv`; the Topstep-shaped column
  (0.4 / $2,000 / K verified-none / $800 / $720), addendum in
  `docs/T3_CEILINGS_DERIVATION.md` §3a.
- **Rapid EOD engine fit: DONE (T4c-2)** — eval via `evals.eval_rules` (lock +100,
  frac 0.30; the verified 4-day minimum is non-binding under 30 %); funded via
  `funded_config("my-funded-futures-rapid-eod")` using the two new `FundedConfig`
  fields (`buffer_before_first_payout` $2,100; `withdrawable_floor` at the $100
  lock, cap verified none) plus `cycle_net_min` $500. Golden paths + ceiling
  oracle in `tests/test_funded_engine.py`. Variant facts that bind T5/T6:
  **3 funded accounts** (not intraday Rapid's 5), 3 minis / 30 micros both stages.
- **BluSky Buffer chaining** (eval side): target/drawdown/consistency now verified
  (D-16), but `buffer_entry_balance` is an **open row and the anchor blocker** — no
  official page states the Buffer account's opening balance, where its $2,000 trail
  anchors, or whether Phase-1 overshoot carries in. Until H-6 answers it, Buffer
  simulations are blocked (the T3 funnel ceiling's fresh-restart assumption is
  registered in P-01 §3a and stands as an assumption). `buffer_drawdown_lock` joins
  the eval lock in the labelled bracket treatment when simulation unblocks.
- **Intraday-trailing floor + MFE law: CANCELLED (D-18)** — the operator dropped
  intraday-drawdown variants from the modelling set; the mechanic is parked
  (`PARKING_LOT.md`) with its requirement spec kept in §2, and the engine keeps
  refusing `floor_mode="intraday_trail"` loudly. MFFU's modelled row is Rapid EOD.
- **T4d**: pre-registered validation battery with result files (the test suite
  already enforces the oracles per run; T4d puts the validation numbers on the
  record with manifests).
- H-6 rows that bind elsewhere: MFFU intraday `payout_cap` (T5 geometry), Alpha
  scaling ladder re-read (funded $-risk grid upper tiers), BluSky `eval_drawdown_lock`
  (bracket until answered).
