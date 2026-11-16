# propsim — Topstep 50K contract model (A0 2026-09-12b, no-DLL)

> **Status (2026-09-21): the zero-edge campaign studied here is prohibited by the firm's terms (account stacking; D-34).** The engine and results describe what the contract does; they are not a plan to run that campaign. See `DECISIONS.md` D-34 to D-38.
>
> **Build status (2026-09-21):** final document and deck rebuild in progress — see [`deliverables/BUILD.md`](deliverables/BUILD.md). The files in `deliverables/previous_version/` are superseded.
>
> **Working rules.** This folder is the single working copy of the project (D-23). Every decision is recorded in
> [`DECISIONS.md`](DECISIONS.md). The document and deck in `deliverables/` are frozen until results are verified (D-22);
> corrections waiting for the next rebuild are listed in [`PENDING_DELIVERABLE_CORRECTIONS.md`](PENDING_DELIVERABLE_CORRECTIONS.md).
> Charter and finish list: [`NEXT_STEPS.md`](NEXT_STEPS.md). Handoff to the research stage: [`HANDOFF.md`](HANDOFF.md). Value of edge: [`edge/T5_RESULTS.md`](edge/T5_RESULTS.md). Out-of-scope ideas: [`PARKING_LOT.md`](PARKING_LOT.md). Rule reconciliation: [`RECONCILIATION.md`](RECONCILIATION.md). No hard risk cap (D-24 retired, D-27); conduct exposure is a selection criterion (D-28).
> After any change: `sh make_zip.sh`. Plots from the grid can be redrawn without rerunning it: `python run_grid.py --plot-only`.


Question: can a zero-edge (or slightly negative-edge) trader extract positive expected cash
from the Topstep 50K contract, and which R:R / $-risk profiles do it best on the Combine
(evaluation) and the XFA (funded) side?

## The answer (zero edge, contract rules, verified 2026-09-20)

**Combine: static 1:1, $1,500 risk, one trade a day.** P(pass) = 16/49 = 32.65 % (exact
Markov chain, four reachable states; Monte Carlo 0.32625 ± 0.00033 at N = 2M, z = −0.84).
The consistency rule never binds on this profile (1,500/0.55 = 2,727 < 3,000): it sits exactly
on the H3 ridge. The Combine floor lock never binds either (balance never exceeds $1,500
before the passing trade), so 16/49 holds with or without it. Resolves in 2.7 trading days on
average, one $49 subscription. Hard ceiling for any zero-edge policy is 40 %. No
state-dependent policy tested beats it; the gap to 40 % is the 55 % consistency rule and the
end-of-day ratchet. Any profile with R × $risk ≈ $1,500 and $risk ≤ $1,500 is within noise.

**XFA: one bet on day one risking the full $2,000 cushion, then harvest with small bets.**
Net per XFA = 0.9 × 2,000 × R/(1+R) when the bet can complete inside a session; the harvest
recovers the whole balance. That is $900 (1:1), $1,200 (2:1), $1,350 (3:1), $1,500 (5:1)
versus $866 for the best static profile (2:1 $750 one trade a day). Frictions not in A0
(the official "net positive since last payout, first exempt" rule and a method-dependent $30 payout fee, charged flat here as the conservative case) cost
~5 %, more at high R: with them 3:1 and 5:1 both net ≈ $1,285.

**But the XFA number depends on one Stage-2 quantity: session σ of the max-size position
relative to the cushion (s = σ_session / $2,000).** With the 15:10 flatten as a third exit:

| s | achievable net per XFA | best R |
|---|---|---|
| ≤ 0.5 | $750–850 (all-in degenerates into a multi-day grind; **use the static 2:1 $750 profile instead, $866**) | n/a |
| 1 | $900–1,000 | 1–3, all equal |
| 2 | $1,150–1,250 | 3 |
| ≥ 4 | $1,350–1,500 (binary model recovered) | 3–5 |

**Per Combine attempt** (P(pass) 0.3265, $149 activation, $49 subscription):
static XFA → $181; day-one 3:1 → $343 ($318 with frictions); 5:1 → $389 ($321 with frictions).
Only 7–25 % of attempts end cash-positive depending on the XFA profile; the EV is carried
by the few that pass and pay out.

**Robustness:** the Combine profile stays EV-positive down to edge −0.10 per trade
(+$29 per attempt at −0.10, +$83 at −0.05). Commission on 50 micros is ~2 % of a $1,500 risk.

## Rules verification (official Topstep help center unless noted; checked 2026-09-20)
| rule | A0 / engine | verified | source |
|---|---|---|---|
| Combine target / MLL / consistency | 3,000 / 2,000 / 0.55, target_eff = best_day ÷ 0.55 | ✓ (several third-party guides say 50 %; official is 55 %) | help.topstep.com/…/8284197, …/8284208 |
| Pass checked at day close; same-day profit adds to best day | lock at 16:00 | ✓ | …/8284208 |
| MLL trails end-of-day balance, breach real-time incl. unrealised | ratchet at lock, truncate at floor | ✓ | …/8284204 |
| **Combine MLL locks at starting balance** | **was missing in A0; added `combine_mll_lock_at = 0`**. Strictly more permissive: binds only above $2,000, so profiles lingering between $2,000 and $3,000 gain room (small-r corner). Inert for the recommended profile. | ✓ | …/8284204 |
| XFA MLL −2,000 → locks at 0 → **$0 permanently after each payout** | ✓ | ✓ | …/8284204, …/8284233 |
| Standard path: 5 winning days ≥ $150, day locks 4 PM CT, payout day doesn't count | ✓ | ✓ | …/8284233 |
| Consistency path: 3 *trading* days, best ≤ 40 % of window net | ✓ (was an assumption) | ✓ | topstep.com/blog (2026-07-02), …/8284208 |
| Caps 2,000 / 3,000 (post 2026-04-28), 50 % of balance, min $125, 90/10 | ✓ | ✓ | …/8284233 |
| Later Standard payouts need > $0 net since last payout, first exempt | **not in A0; `require_profit_since_payout`** | ✓ official (Payout Policy 8284233; also carried as P-class in the project's Appendix A.3) | …/8284233 |
| $30 per-payout processing fee | **not in A0; `payout_fee`** | third-party; official says none for Wise/Aeropay | unverified |
| Fees 49 / 149 / 49; Back2Funded 599 ×2 | ✓ | ✓ | topstep.com/express-funded-account-rules |
| Number of accounts | — | Combines unlimited (official); "up to 5 XFAs" (third-party) | …/8284197; propdatalab |
| **Prohibited Conduct** | not modelled | exists "to deter gambling behaviors"; case-by-case: warning, deleted day, reset, closure; third-party summary of ToS lists "pooling or hedging risk of aggregate accounts" and strategies deemed "not viable" | intercom.help/topstep-llc/…/8284103 |

The last row is the largest unmodelled risk to the XFA policy and to any cross-account hedge.

## Mathematical structure (why the numbers are what they are)
* Zero edge ⇒ balance is a martingale. Combine: 3000·P(pass) ≤ 2000·P(fail) ⇒ **P(pass) ≤ 40 %**.
  XFA: with T = balance + payouts, E[T_close] ≤ 0 ⇒ **E[gross payouts] ≤ $2,000**.
* E[gross] = (1 − P(payout)) × (2,000 − mean ratchet on losing paths). The leak is the ratchet,
  so losing paths should die before any lock raises the floor ⇒ the day-one all-in.
  It achieves 2,000·R/(1+R) exactly (harvest recovers the balance, verified p_closed = 1).
* Two day-one all-ins beat one (3:1: $1,650 vs $1,330) and three collapse ($544): the model
  wants all the variance the payout cap and horizon allow. The achievable point is set by
  session σ, the contract cap and conduct rules, not by the contract maths.
* Floor liquidation is intraday. A trade whose stop is beyond the room is a barrier race:
  p = c/(c+W) at zero edge (`floor_mode="truncate"`). The gate-1.8 "no excursion" model
  overshoots the floor and inflates EV 1.2–2.9× across the whole grid.
* Zero-edge excursion law for a generator: P(MAE ≥ c | win) = W(r−c)/(r(c+W)); liquidating at
  MAE ≥ room reproduces c/(c+W) identically. Distribution-free (any continuous martingale).
* Non-zero edge: θ = drift-per-variance fixed by p_race(r,W,θ) = (1+e)/(1+R); the floor is a
  closer exit on the same path (`edge_mode="drift"`, exact; "linear" is its first-order
  expansion, identical results at |e| ≤ 0.05). Assumption-bearing (constant-drift BM).
  Numerics: expm1, bisection bracket ±1/(r+W), raise if (1+e)/(1+R) ∉ (0,1).
* H3 (interior maximum in $risk): for R ≥ 1.5 the peak is the largest bet whose single win
  stays under 0.55 × 3,000 and it slides when the fraction is swept; for R ≤ 1 it is the
  MLL floor. Small bets lose to the $49/21-day subscription (hundreds of days to resolve).

## Files
| file | purpose |
|---|---|
| `propsim.py` | Combine + XFA engines (static policies), fees, barrier maths, MAE law, drift solver |
| `statepolicy.py` | Stage-3 state-dependent policies (build/harvest, all-in, fill-the-gap) |
| `timebarrier.py` | session time barrier (15:10 flatten) for the day-one all-in, Brownian-bridge exact barriers |
| `test_propsim.py` | 31 tests: golden paths from the rule text, exact Markov chain, martingale bounds, closed-form identities |
| `run_grid.py` → `results_grid_edge0.csv`, `results_edge_ladder.csv`, `results_*.png` | 160-cell static grid |
| `run_final.py` → `results_final.csv` | final profiles, N = 100k, edge ladder, frictions |
| `run_consistency_sweep.py` → `results_consistency_sweep.csv` | H3 mechanism test |
| `run_floor_modes.py` → `results_floor_mode_504.csv` | none / truncate / resize, 504-day lifecycle |
| `run_edge_convention.py` → `results_edge_convention.csv` | drift vs linear, paired seeds |
| `run_state_policy.py` → `results_state_policy_combine.csv`, `results_state_policy_xfa_kallin.csv`, `verify_state_policy_xfa.csv` | state-dependent policies. Combine and k-all-in tables reproduce bit-for-bit (seeds 3 and 7). The two XFA policy tables (`results_state_policy_xfa.csv`, `results_state_policy_xfa_allin.csv`) were first run without recorded seeds; this script reruns all 33 rows (seed 2026, N = 20,000) and checks them: all within 2.4 SE. `--verify-only` leaves stored files untouched. The reruns share one seed, so their deviations are correlated (mostly the same sign) |
| `timebarrier.py` → `results_timebarrier.csv` | Finding 8 |

### `bankroll/` — risk of ruin and drawdown (Stage 1b, after the report)
| file | purpose |
|---|---|
| `bankroll.py` → `results_bankroll_summary.csv`, `results_ruin.csv`, `results_drawdown.csv` | per-attempt net-cash distribution (400k attempts, Combine 1:1 $1,500; static 2:1 $750 or day-one 3:1 funded; with/without frictions), Lundberg adjustment coefficient, Monte-Carlo ruin vs fee bankroll, drawdown quantiles over 10–100 attempts |
| `ruin_extended.py` → `results_ruin_large_bankroll.csv`, `results_ruin_split.csv` | ruin at $4k–$10k; ruin split into "no payout before broke" vs "paid, then broke"; ruin by attempt count |
| `payout_trace.py` → `results_payout_trace_2to1.csv` | cash timeline of an XFA that wins the 2:1 day-one bet (50 % withdrawal rule): first payout ≈ $1,800 net around day 8, total ≈ $3,600 over ≈ 42 trading days; matches the engine total |

Key numbers (e = 0, frictions on): ruin ≈ 1.2 % at a $5,000 fee bankroll on the 3:1 profile, ≈ 7 % on the static profile; ≈ 45 % / 62 % at $1,000. On the 3:1 profile, ruin almost always means "no payout before the money ran out". **All bankroll numbers assume exactly zero edge and one attempt at a time**; they scale roughly inversely with EV per attempt. Final sizing is deferred until s and trading costs are measured. Not yet modelled: parallel accounts with calendar timing of fees vs payouts.

### `deliverables/` — research document and presentation
| file | purpose |
|---|---|
| `Zero-Edge Structural EV - Research Document.docx`, `…Presentation.pptx` | final deliverables (same files as delivered) |
| `make_figs.py`, `deck_figs.py` → `figs/` | all figures, regenerated from the result CSVs (needs the engine for fig 13) |
| `data.js` | single source of numbers for both deliverables, read from the result CSVs |
| `lib.js`, `report_p1.js`–`report_p3.js`, `build_report.js`, `inject_toc.py` | document build: `node build_report.js` then `python inject_toc.py` (writes the populated, hyperlinked TOC; needs LibreOffice via `SOFFICE_PY` to paginate) |
| `build_deck.js` | deck build: `node build_deck.js` (needs `npm install pptxgenjs`; the document needs `docx`) |

Equation, table and figure numbers are shared by both deliverables (document is authoritative; deck cites it).

Run: `python -m pytest test_propsim.py -q` then any `run_*.py` / `timebarrier.py`. All seeded.


### `optimality/` — audit follow-up (2026-09-21)
| file | purpose |
|---|---|
| `combine_supremum.py`, `run_supremum_table.py` → `results_combine_supremum.csv` | supremum of Combine P(pass) over **all** fair strategies (concave-envelope value iteration: within a day any mean-preserving end-of-day distribution on [floor, ∞) is reachable). Result: 0.327131 = 2000²/(3350·3650), attained by a two-day path closing day one at +$1,350 or +$1,650; 16/49 is 0.06 pp below it. Unchanged under the $1,000 DLL (reached over more days) |
| `dll_funded.py` → `results_dll_funded.csv` | funded side with the DLL elected at Combine checkout (official: $1,000 DLL, Standard cap doubled to $4,000). All-in identity holds; gain ≈ $0 at R ≤ 2, ≈ $4 at 3:1, ≈ $49 at 5:1 per XFA (with frictions, 500-day horizon) |
| `results_horizon_frictions.csv` | **correction**: with the net-positive-since-payout rule the 250-day horizon binds at R ≥ 3 (P(closed) 0.981 at 3:1, 0.946 at 5:1). At 1,000 days 5:1 nets $1,446 vs 3:1 $1,316 with the $30 fee. The earlier conclusion "5:1 adds nothing over 3:1 with frictions" is a horizon artifact: frictions cost time, not money |

Verified 2026-09-21 (official): Combines unlimited (8284197, 8284121); up to 5 active XFAs, further passes go on hold until one closes (8284215); $30 fee only for ACH/wire (Aeropay, Prop-to-Brokerage free); DLL cap doubling is a limited-time offer, only if the DLL is added at Combine checkout.

## Model scope
Modelled: cumulative P&L from 0; binary trades resolved at the labelled risk with intraday
floor liquidation; day structure with the 16:00 lock; consistency rule; both payout paths;
scaling irrelevant (no size); subscription / activation; optional payout frictions;
session time barrier (`timebarrier.py` only). Not modelled: commissions (treated as negative
edge), contract caps and stop distance, DLL arm, Back2Funded chaining, Prohibited Conduct
review, correlation across accounts (does not change EV; only variance and bankroll).

## Pre-registered decision rule for Stage 2 (write before measuring)
Measure s = session σ of the max-size position (20 micros at XFA start) ÷ $2,000 on the
instrument to be traded, over the sample period.
* If s < 0.75 → XFA profile is static 2:1 $750 (or any R × $risk ≈ $1,500), expected ≈ $866.
* If 0.75 ≤ s < 3 → day-one all-in at 3:1, expected from the `results_timebarrier.csv` row nearest s.
* If s ≥ 3 → day-one all-in at 3:1 with frictions on (5:1 adds nothing once frictions are charged).
* Combine profile is 1:1 $1,500 regardless of s (it resolves in one or two trades).
The project's contract-level question is closed by this document; the only remaining
measurement is s, plus a read of the Prohibited Conduct terms.
