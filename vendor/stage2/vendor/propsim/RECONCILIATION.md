# Step 2 — Rule reconciliation worksheet

> **Closed for this repository (D-41):** propsim agrees with the official text on every item (R-1 lock applied; R-2 net-positive on the Standard path, first payout exempt; R-3 $125 minimum; R-7 21 trading days, source says 30 calendar days; R-9 tested). The A0/E1 columns and the archive comparison are parked.

Purpose: make the three rule records agree — the **official text**, the project's **A0** contract artifact and **E1** engine,
and **propsim** — so that Stage 2 is built on one contract definition. Owner of A0/E1 columns: project side. Owner of propsim column: this repo.

## Procedure (for every item)

1. **Locate the archived capture** of the cited page in the repo's evidence folder (sidecar: capture date, hash). The project's captures are dated 2026-09-12.
2. **Compare** the archived text with the live text quoted below (read 2026-09-21).
3. **Classify** the discrepancy:
   - *Transcription omission* — the rule is in the archive but not in A0 → A0 operator entry citing the archive; no contract version change.
   - *Rule change after capture* — the rule is live but not archived → fresh dated capture **and** a new rule version (e.g. `topstep-tc-50k@2026-09-21`); an A0 field alone is not enough.
   - *Ambiguity* — the text supports two readings → record both, pick one, say why, and run the other as a sensitivity.
4. **Resolve** in every record that is wrong: A0 entry, E1 change + gate version bump, propsim parameter.
5. **Pin it with a discriminating golden path** — a scripted sequence whose outcome differs between the two readings — in *both* engines.
6. **Rerun** the experiments the item touches (listed per item) and log the decision in `DECISIONS.md`.

## Items

| # | Rule | Official text (live, 2026-09-21) | propsim | A0 | E1 | Effect on results |
|---|---|---|---|---|---|---|
| R-1 | **Combine MLL lock** | 8284204 general section: the MLL trails end-of-day balance, never moves down, and "once it reaches your starting balance, it locks permanently." Combine example ends at "MLL stays at $48,500" and does not show the lock. Page marked "updated this week". **Compare against the repo sidecar capture dated 2026-09-12** (D-29) | `combine_mll_lock_at = 0` (added 2026-09-20) | absent | ratchets without cap (per audit) | Binds only after a locked balance above +$2,000. **Never binds for 1:1 $1,500** (16/49 unchanged). Flipped 7 of 8 large-bet negative grid cells positive |
| R-2 | **Net profit since last payout** | 8284233 Standard path, requirement 2: at least $0.01 net since the last payout; first payout exempt. FAQ repeats it generally | Standard path, `require_profit_since_payout` (Π_since > 0) | absent from field list | enforced (37,451 Stage-A refusals, per audit) | Small in money, large in time: binds the 250-day horizon at R ≥ 3 (D-18) |
| R-3 | **Payout minimum** | 8284233: minimum payout $125; request ≤ 50 % of balance and cap | `payout_min = 125` | operator entry needed | check value and whether it tests the *request* (q ≥ 125 ⇒ balance ≥ $250) | Only blocks small-balance payouts |
| R-4 | **Payout fee** | 8284233: $30 ACH and wire; $0 Aeropay, Prop-to-Brokerage (US), Wise (China, Canada, UK only) | `payout_fee` parameter, default 0 | — | check | Method choice, not contract: model as a policy parameter. Avoidable in the US |
| R-5 | **Daily Loss Limit variant** (campaign dimension, D-30) | 10490293: 50K DLL $1,000; fixed if set at checkout; applies to the XFA after passing; flattens, not a violation. 8284233: Standard cap doubled to $4,000 only if added at Combine checkout; limited-time offer | not in engine (emulated by policy, `optimality/dll_funded.py`) | A0 is the no-DLL instance | — | EV ≈ $0–4 per XFA at R ≤ 3, but shortens the harvest (payouts per XFA 1.14 → 1.04 at 3:1, 1.02 → 0.82 at 5:1, with frictions). Also caps Combine day losses at $1,000, so the DLL arm needs its own Combine profile |
| R-6 | **Account limits** | 8284197 / 8284121: no limit on Trading Combines. 8284215: up to 5 active XFAs; a pass at the limit goes **on hold** until one closes; Back2Funded ≤ 2 reactivations | not modelled (campaign model input) | check | check | Campaign model (step 3). Audit's "five Combines" not supported officially. "10 Combines/month" is third-party only |
| R-7 | **Subscription billing** | 8284121: rebills every 30 days from sign-up (calendar) — logged as source | $49 every 21 trading days | adopt 21 trading days | adopt 21 trading days | Convention fixed (D-31); immaterial to every recommended profile |
| R-8 | **Liquidation fill** | 8284204: breach decided by touch on real-time P&L; exit by market order, fill may land above or below the limit | fail/closure lands exactly at the floor | — | check | No cash effect (account fails or closes either way). Record only |
| R-10 | **Legacy profit split** (participant-specific) | 8284233 (archived): traders who joined the new dashboard before 2026-01-12 receive 100 % of the first $10,000 of lifetime profits, then 90/10; legacy-dashboard payouts do not count toward the $10,000 | not applied | — | not applied | One-time campaign adjustment, at most $1,000 over the participant's lifetime (D-32). Needs a lifetime-profit counter across accounts in the campaign model |
| R-9 | **Payout request day** | 8284233: request day does not count toward the next cycle; requests after 5 PM CT belong to the next trading day | payout at the lock of the eligibility day; next window starts next day | check | check | Check both engines agree on day counting |

## Discriminating golden paths

**R-1 (Combine lock).** Combine, 1 trade per day:
- Day 1: +$2,400. No pass (best day $2,400 inflates the target to $4,363.64). Lock: floor = min(0, 2,400 − 2,000) = **$0** if locked, **+$400** if not.
- Day 2: −$2,200 → balance $200. **Locked: account alive. Unlocked: failed** (200 < 400).

propsim pins the same distinction in `test_combine_floor_locks_at_zero`.

**R-2 (net positive since payout).** XFA Standard:
- Five days of +$300 → first payout $750 (balance $750, floor $0).
- Then five winning days of +$150 alternating with −$200 days, so net since payout is negative.

With the rule, the second payout is **refused**; without it, it is **allowed**. E1's Stage-A refusals should reproduce this.

**R-3 (payout minimum).** XFA at balance $240 after five winning days: request = min(0.5 × 240, cap) = $120 < $125 → **refused**. Same path with the balance at $250 → **$125 allowed**.

## Status

| # | Status | Next action | Owner |
|---|---|---|---|
| R-1 | open — live excerpt saved (`evidence/8284204_live_2026-09-21.md`) | Compare the 2026-09-12 sidecar of 8284204 with live. If the lock sentence is absent: rule change → fresh capture + new rule version + E1 change and gate version | project |
| R-2 | attribution settled (D-16) | A0 field + citation; confirm E1 applies it to Standard path with first-payout exemption | project |
| R-3 | open | A0 operator entry; confirm E1 tests the request amount | project |
| R-4 | settled | Model as payout-method parameter in the campaign model | this repo |
| R-5 | campaign dimension (D-30) | Model DLL on/off in step 3 with a DLL-compatible Combine profile; re-check the offer before any purchase | this repo |
| R-6 | settled from official pages | Campaign-model inputs (D-20); A0 fields | both |
| R-7 | settled (D-31) | E1 to use 21 trading days per billing period | project |
| R-8 | settled | none | — |
| R-9 | propsim done (`test_r9_payout_day_not_counted_in_next_cycle`); E1 open | E1 scripted path. propsim requests at the 16:00 lock, so the after-17:00 case never arises there (convention noted) | project |
| R-10 | settled as campaign adjustment (D-32) | Add lifetime-profit counter and one-time 100 % tranche to the campaign model | this repo |
