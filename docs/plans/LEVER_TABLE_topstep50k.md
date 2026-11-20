# The lever table: Topstep $50K design search (Q-151; restart plan Wave 3.4 groundwork)

Drafted 2026-11-18 on `wt/wt-features` for the lead. **Status: groundwork for the search declaration (Wave 5.1), not a
declaration.** Nothing here is pinned or chosen, and no search or run is built. The table holds no result number. No
rule value is typed: a rule-derived bound is written as its key, and `extended/lever_space.py` reads it from the record
(this repository's `config/rules_extended.yaml` where it holds the key, else Stage 2's vendored ledger, through
`extended/firm_terms.py`). The numbers that do appear are declared parameters, each citing the row or declaration it
comes from.

Read with: the restart plan, sections 2 and 4.3-4.4b (`docs/plans/RESTART_PLAN_journey_objective.md`); the amendments'
CHARTER 3.3 (a), (g) and 3.5 (`docs/plans/AMENDMENTS_draft_2026-11-18.md`); E-208 (the search years are 2020-01-02 to
2023-12-29); the triage (`docs/plans/TRIAGE_2026-11-18.md`); F-04 6.1 and 6.3 (`wt/wt-scout` 8d35481); RL3 6.1
(`wt/wt-levels` 448681d); RD-02, RD-03 and RD-05 with RD-05's build (`extended/modes_terms.py`,
`extended/modes_rules.py`); and F-R 6.2-6.5 (`prereg/DRAFT_F-R_resolution.md`).

---

## 1. Where a range may come from, and what the loader refuses

CHARTER 3.3 (a), as amended, allows a lever range from three sources: contract arithmetic, the verified rules, or an RD
map's search-year rows. A range drawn from a whole-window row is redrawn on the search years and entered in the held-out
read ledger. Each row below names one of five source kinds. The loader (`lever_space.bounds`) handles each kind as
follows.

| source kind | what it means | the loader |
|---|---|---|
| **rule** | the range is a verified rule's value, read by its key | reads it; **refuses** (`UnverifiedTerm`) if any key the lever leans on is not `verified`. This repository's record wins where it holds the key: its `changed` and `unstated` entries are refused even where Stage 2's entry is verified |
| **arithmetic** | computed from verified rules and the engine's contract constants: tick values from `vendor/stage2/config/instruments.yaml`, and the registered stand-aside floor from `vendor/stage2/config/fv3_corrected_portfolio.yaml` | computes it, refusing as for a rule |
| **declared** | a parameter of this table (`lever_space.DECLARED`), citing its row or declaration, never a rule value | returns it, after checking every key the lever leans on |
| **a search-year reading, to compute** | the range needs a reading of the bars on the search years that does not yet exist | **refuses** (`NotComputed`), whatever its keys |
| **to declare** | a later item fixes it (the trigger library or the mix router, Wave 3.3) | **refuses** (`NotDeclared`) |

A **dropped** lever has no range (`DroppedLever`). It is held at the setting its row states, or it does not exist.
`lever_space.check_design` refuses combinations that no verified rule settles (section 4). The loader reads rules and
configuration only, never a bar.

**Class.** *Searched*: the survey and the surrogate rounds vary it inside its range. *Declared*: fixed by this table or
by its declaration, the same in every design. *Dropped*: not in the space, with the reason stated.

**Units.** A volatility unit is used only where a setting must mean the same thing across the window's drift (RD-04).
That is the stop width, a multiple of the trailing range. Dollar risk stays in dollars, because the firm's limits are
in dollars and D-212's consistent risk is in dollars (Stage 2 D-240 and D-300 to D-307: an ATR-scaled stop with
floating dollars broke the sizing). The contracts are what absorb the volatility.

## 2. The levers

Notation. `key` is a rule key. "One micro at the floor stop" is the floor of row S1, times the MNQ tick value. Minutes
"after the reopen" are on the firm's trading-day clock, which starts at `trading_hours`' reopen.

### 2.1 Trigger layer: the reason and moment to trade, and how the order is placed

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class |
|---|---|---|---|---|---|---|---|
| T1 | trigger | signal source of a component | `coin` (naive, at scheduled marks), `p14` (P-14's breakout timing, coin-sided), `p16` (P-16's marks, coin-sided), `rl3` (RL3's pre-session tickets, NY AM); P-16's overnight marks join only after H2 | declared: E-208's dispositions; the trigger library (Wave 3.3) builds them | categorical; reads nothing | T2, T3, T4, T5, A16 | searched |
| T2 | trigger | session of a component (the schedule covers every session the firm allows) | `evening`, `asia`, `london`, `ny_am`, `ny_pm`, which together cover the firm's whole day from `trading_hours`' reopen to its flat. The boundaries are Stage 2's windows (asia from 18:00, london from 02:00, us from 08:30 CT), and each is checked to lie inside the day | arithmetic: `trading_hours`, with the declared window starts (Stage 2 `resolved_coin.WINDOWS`, D-525 (3)) | a session; reads nothing | T1, T2b, T3 | searched |
| T2b | trigger | the NY AM / NY PM boundary | **to declare** (the trigger library, Wave 3.3); refused until declared | to declare | a wall-clock time inside `us`; reads nothing | T2 | declared |
| T3 | trigger | entry window: a component's offer marks inside its session | from the reopen to the last new entry, the "Avoid opening new positions after ..." sentence of `trading_hours`' verified note (8284206), in steps of D-525 (2)'s five-minute mark | arithmetic: `trading_hours` and its note; the declared mark step | minutes after the reopen; reads nothing | T2, T4, A3; no two components' windows collide (one position at a time across the firm, Stage 2 D-429) | searched |
| T4 | trigger | latency L, alert to order | 5 (the reference), 3, 2 minutes, **every cell counted** in the variants ledger and the multiplicity; the five-minute cell is reported beside every finalist; `p16` and `rl3` are latency-free and collapse to one cell (`lever_space.latency_cells`) | declared: E-202 (2)(c); CHARTER 3.3 (g) | clock minutes; reads nothing | T1, T3, T5 | searched |
| T5 | trigger | entry type | `market`, `limit`. A limit goes live at L, fills only on a trade through by one tick at its price and never better, and is cancelled at a news window's start (E-202 (2)(d)); its zero-edge twin is the reflection (CHARTER 3.2), and for RL3 it is the same-bar pair of fade limit and break stop (E-204) | declared: E-202 (2)(d); F-04 6.1 R-4; the triage on a coin-sided limit | order type; reads nothing | T1, T4, T6 | searched |
| T6 | trigger | how long a limit works | 30 minutes from going live, or until a news window's start or the walk's last entry bar, whichever is earliest | declared: F-04 6.1 | minutes; reads nothing | T5 | declared |
| T7 | trigger | admission: offer a mark only when it is forecast to resolve | `off`, or admit when the forecast chance of reaching the flatten open is at most D-212's line. The forecast is F-R's HAR form (6.2-6.4), refitted on the **search years only** under `feature-rules` | **a search-year reading, to compute**: the HAR coefficients and their calibration, fitted on 2020-01-02 to 2023-12-29; refused until they exist | a probability; its estimate reads each session's one-minute bars from the mark to the walk's end, and the trailing 22 and 5 sessions' same windows, all inside the search years | T1, T3, S1, S2 | searched |
| T8 | trigger | side rule | the coin side, under CHARTER 3.2's zero-edge convention. The traded side is pending the operator (O-4); a new trade takes the side of any open position, or is skipped | declared: CHARTER 3.2, 3.5 as amended | side rule; reads nothing | T1, T5, A15 | declared |

### 2.2 Trade-shape layer: stop, target, hold, contracts, dollar risk

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class |
|---|---|---|---|---|---|---|---|
| S1 | trade shape | stop width | a multiple k of the trailing range. **The range of k is to compute**: it is the search-year translation of the stop's caps into multiples. The caps are computable now (`lever_space.stop_caps`): the floor is the registered stand-aside's floor ticks (Stage 2 D-271 (3), D-272; it also keeps clear of "tight brackets", `prohibited_strategy_auto_breakeven_sim_fills`), and the cap is the widest stop at which one micro's stop-out fills the larger start room (`combine_mll`, `xfa_mll_start`), before costs | **a search-year reading, to compute**: the distribution of the trailing range on the search years; the caps are arithmetic | multiple of `trail20_range_pts`, RD-04's and Q-121's trailing mean session range over the 20 prior walked sessions, in points; causal, so a held-out start may look back into the search years (CHARTER 3.6 (d)); **the range's derivation reads the search years only** | T2 (each session's own range), S2, S3, S4, S5 | searched |
| S2 | trade shape | reward-to-risk w (target over stop) | from the least to the largest of RD-05 2.6's grid (`modes_terms.grid_w`), continuous; the target is floor(w x s) whole ticks, which sets the step | declared: RD-05 2.6 (Stage 2 D-429's reference ratios) | ratio; reads nothing | S1, A1, A2 | searched |
| S3 | trade shape | dollar risk per trade, evaluation | from one micro at the floor stop to `combine_mll`; the step is one micro at the trade's own stop (whole micros) | arithmetic: `combine_mll`, `combine_position_size_limit` and the stop's floor | dollars at the stop, with the share of the start room beside; reads nothing | S1, S5, A1; cut each trade by the room cap (D-313), the allowance and the headroom (D-117), with D-212's consistent-risk stand-aside | searched |
| S4 | trade shape | dollar risk per trade, funded | from one micro at the floor stop to the room of `xfa_mll_start`; whole micros; the allowance follows `funded_scaling_plan` | arithmetic: `xfa_mll_start`, `funded_scaling_plan` | dollars at the stop; reads nothing | S1, S5, A2, A5 | searched |
| S5 | trade shape | instrument mix | `MNQ` (micros only), `mixed` (as many minis as fit, the rest micros, D-324); minis-only dropped | declared: F-04 6.1; the counting from `combine_position_size_limit`, `funded_scaling_plan` and the engine's micros per mini | categorical; reads nothing | S3, S4 | searched |
| S6 | trade shape | maximum hold (a time stop) | **dropped**: CHARTER 4 bans time stops, and every trade resolves (D-212). A trade ends at its stop or target, at a news window's flatten, or at the walk's end before `trading_hours`' flat | declared: CHARTER 4 | -- | -- | dropped |
| S7 | trade shape | breakeven stop move | **dropped**: off. P-14's registered walk keeps its own move as part of its source (T1); auto-breakeven used to exploit the simulator's fills is tier-1 conduct (`prohibited_strategy_auto_breakeven_sim_fills`) | declared: RL3 6.1; F-04 6.1 | -- | T1 | dropped |
| S8 | trade shape | partial exits, scaling in | **dropped** | declared: F-04 6.1 | -- | -- | dropped |
| S9 | trade shape | contracts | **dropped as a lever**: derived. Fixing r (S3 or S4), the stop (S1) and the mix (S5) fixes the contracts at each state; a fixed count would float the dollar risk with the stop, which D-212 forbids (D-240) | arithmetic: RD-05 part B's sizing (`modes_rules.size`) | -- | S1, S3, S4, S5 | dropped |

### 2.3 Account-policy layer: which account, which mode's behaviour, purchases, seats, payouts

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class |
|---|---|---|---|---|---|---|---|
| A1 | account policy | steady or flip, evaluation | `steady`; or `flip`, where the first k_E sessions' first trade is at r_flip = `combine_profit_target` / (k_E x w), cut to the room of `combine_mll`, and the rest are steady. k_E is RD-05 part A's fewest passing days, from `combine_consistency_max_day_frac` (`modes_rules.k_eval`). A flip trade is never at the full allowance (RD-05 2.6, the major-news rule) | arithmetic: RD-05 part A | policy; reads nothing | S2, S3 | searched |
| A2 | account policy | steady or flip, funded | `steady`, `flip` with k_F and b\* per payout path (`modes_rules.k_funded`, `b_star`: `xfa_std_winning_days`; `xfa_cons_min_days` and `xfa_cons_max_day_frac`; `xfa_std_cap`, `xfa_cons_cap`, `payout_max_frac_of_balance`) and r_flip = b\* / (k_F x w), cut to the room of `xfa_mll_start` | arithmetic: RD-05 part A | policy; reads nothing | S2, S4, A5 | searched |
| A3 | account policy | session rule q ("when to stop", the daily stop) | `one` (the session's first chain trade), `all`, `cap` (until the session's net reaches the mode's consistency allowance: `combine_consistency_max_day_frac` x `combine_profit_target` in the evaluation, and `xfa_cons_max_day_frac` on the Consistency path) | declared: F-04 6.1; the allowance by rule | categorical; reads nothing | T3, A5 | searched |
| A4 | account policy | price path | `standard` (`subscription_fee`, `activation_fee`), `naf` (`subscription_fee_naf_50k`, `activation_fee_naf_50k`) | rule | categorical; reads nothing | A12 (section 4) | searched |
| A5 | account policy | payout path | `standard`, `consistency`, chosen at activation and never changed (`xfa_payout_path_choice`); the caps `xfa_std_cap`, `xfa_cons_cap`; the gates `xfa_std_winning_days`, `xfa_std_winning_day_min`, `xfa_cons_min_days`, `xfa_cons_max_day_frac` | rule | categorical; reads nothing | A2, A3, A18, A19 | searched |
| A6 | account policy | funded seats held at once | 1 to `max_active_funded_accounts`, step 1. Each trade goes to one account: one position at a time across the firm (D-429), never one trade copied across accounts (tier 1) | rule | accounts; reads nothing | A7, A8, A15 | searched |
| A7 | account policy | evaluations running at once (C) | 1 to 7, step 1. No rule caps evaluations (`combine_count_limit` must read unlimited, or the loader stops) | declared: RD-03 2.2 (C = 5, Stage 2 D-34's bound, or 7) | accounts; reads nothing | A6, A8, A11 | searched |
| A8 | account policy | banking: buy evaluations while a pass waits | `on`, `off` (Stage 2 D-08). A pass at the cap waits (`hold_queue_behaviour`) | declared: RD-03 2.2 | categorical; reads nothing | A6, A7, A9 | searched |
| A9 | account policy | the hold's expiry | the two readings `exp_none` and `exp_30` (RD-03 U-1), both run and never chosen. **Refused by the loader**: `hold_expiry_days` is `unstated` in this repository's record, so the search declaration takes U-1's readings by its own declared rule | declared (two readings of an unstated rule) | reading; reads nothing | A8, A10 | declared |
| A10 | account policy | evaluation-purchase rule | `replace` (the base: a failed evaluation is replaced), `house_stop`, `house_zero` (RD-03 2.3, **gaming P**, E-134 (2)); cancellation by `combine_cancellation` | declared: RD-03 2.3 | categorical; reads nothing | A9, A11; the operator's bankroll limit (Wave 4.2) | searched |
| A11 | account policy | evaluation-purchase budget | 1 to 20 purchases a month (21 sessions, RD-05's month), step 1. No rule limits starts (`account_start_rate_limit` must read none stated, or the loader stops) | declared: Stage 2 D-501 | purchases a month; reads nothing | A7, A10 | searched |
| A12 | account policy | Back2Funded reactivations per funded account | 0 to `back2funded_max_reactivations`, step 1, at `back2funded_reactivation_fee_50k`, within `back2funded_window_days` (in sessions, rounded down by RD-05's calendar rule), eligible by `back2funded_eligibility`, and seated by `back2funded_seat_count` | rule | reactivations; reads nothing | A4 (section 4), A6, A18 | searched |
| A13 | account policy | resets | **dropped**: an adapter is owed first. A reset pushes the rebill date (`reset_rebill_push`) and the vendored engine does not (RD-03 2.5) | declared: RD-03 2.5 | -- | A4 | dropped |
| A14 | account policy | daily-loss-limit election at checkout | **dropped**: a different account (`dll_offer_status`; RD-03 2.5, RD-05 2.3) | declared: RD-05 2.3 | -- | S3, S4 | dropped |
| A15 | account policy | routing: which account takes the next trade | the base is the longest-waiting account (D-429); the alternatives are **to declare** by the mix router (Wave 3.3), with the no-opposing-positions guard | to declare | rule; reads nothing | A6, A7, A16, T8 | searched |
| A16 | account policy | signal mix: the sources' shares and their account assignment | **to declare** by the mix router (the restart plan 4.4): shares on the simplex over T1's sources, and an assignment rule | to declare | shares; reads nothing | T1, A15 | searched |
| A17 | account policy | state rule: sizing by distance to the floor or the target | **to declare** (the triage: Q-46's buffer idea enters as a state rule) | to declare | rule; reads nothing | S3, S4, A1, A2 | searched |
| A18 | account policy | the first payout request (RD-02 L1) | `elig` (the first eligible close at which the request reaches `payout_min`), `lock` (only once the floor has locked at `xfa_lock_at`) | declared: RD-02 6.1; the eligibility by `xfa_std_winning_days`, `xfa_std_winning_day_min` | rule; reads nothing | A5, A19 | searched |
| A19 | account policy | the request amount (RD-02 L2) | `max` (`payout_max_frac_of_balance` of the balance, up to `xfa_std_cap`; none below `payout_min`), `half`. **Refused by the loader**: any amount below the maximum rests on `payout_request_amount_choice`, which is `unstated` (E-034). Until that key is verified the search holds `max`, with `half` beside under RD-02's labelled assumption | declared: RD-02 6.1 | share of the maximum; reads nothing | A5, A18 | searched |
| A20 | account policy | request cadence after the first payout | every eligible close (`require_profit_since_payout`) | declared: RD-02 6.1 | -- | A18 | declared |
| A21 | account policy | payout method | Aeropay. The loader checks from the keys that it is dominated by nothing (`payout_lag_days_aeropay` at most `payout_lag_days_ach`, and `payout_fee` at most `payout_fee_ach`); if it ever is, the method becomes a lever | declared: RD-02 7.1; Stage 2 D-24 | -- | -- | declared |

## 3. The operator's dimensions: where each one is

| the operator's dimension | rows |
|---|---|
| latency 5 / 3 / 2, counted | T4; `latency_cells` collapses `p16` and `rl3` to one cell; every L tried enters the variants ledger and the multiplicity (CHARTER 3.3 (g)) |
| market or limit entries | T5, T6 |
| every session the firm allows | T2, T2b, T3 (the firm's whole day, from `trading_hours`); overnight sources only after H2 |
| steady or flip | A1 (evaluation), A2 (funded) |
| the account policy: evaluation purchases and seats | A6 to A12, A15, A16; A13 and A14 are dropped |
| the payout request rule (RD-02) | A18, A19, A20, A21; the payout path A5 |

## 4. Combinations the loader refuses

- **Back2Funded under the No Activation Fee path** (A4 = `naf` with A12 above zero). No page states whether its price
  differs (`back2funded_fee_by_pricing_path`, `unstated`; RD-03 2.5), so `check_design` refuses the combination until
  that key is verified.
- **A latency on a latency-free source** (T4 other than one cell for `p16` or `rl3`).

## 5. Fixed for every design: floors, not levers

These hold in every design and are never searched. Each is stated by its rule key or its decision row.

- One position at a time across the firm, with five minutes flat between trades (Stage 2 D-429). Never opposing
  positions across accounts or firms (`cross_account_opposite_positions`, `cross_account_hedging`; tier 1). Never one
  trade copied across accounts.
- Flat by `trading_hours`' flat, and no new entry after its note's last-entry time. Every trade resolves: at most 5 %
  reach the flatten (D-212 as D-308 raised it). Realised risk matches intended (D-212).
- News: no entry and no fill inside any verified window, and a position open at a window's start is flattened (E-202
  (2)(a); RD-05 4.7 item 3, E-200 R-1). `tier1_news_events_restriction` and `economic_releases_list` are `changed` in
  the record, so the loader does not read them. The news rule reaches the engine through RD-05's adapter, as its
  declaration fixes. No entry before 07:35:00 CT on a BLS 08:30 release day, and FOMC days are out (E-007).
- No maximum size into major news (`prohibited_strategy_max_size_into_major_news`): a flip trade is never at the full
  allowance (RD-05 2.6).
- Hand entry, at least L minutes from alert to order (T4). No automated order entry.
- The zero-edge convention and the martingale-outcome reading (CHARTER 3.2). The verdict is read at 0 % denial with the
  placement off.
- **Not levers:** the bankroll budget, the limits and the composite's weights (the operator's, Wave 4.2); the coin
  seeds (the declaration's).

## 6. What still needs a search-year reading, and the ledger

**Two rows need a reading of the bars on the search years** before their ranges load. Neither has been read.

- **S1, the stop's range in volatility units.** The distribution of `trail20_range_pts` on 2020-01-02 to 2023-12-29
  translates the computable caps (`stop_caps`) into a range of k, per session (T2), since each session's range
  differs. The candidate inputs: Q-121's `range` rows of the years 2020 to 2023 are search-year rows of an RD map
  (RD-04 holds its 2020-2023 L_y equal to them), which CHARTER 3.3 (a) admits. Q-121's `block` rows and RD-04's (a2)
  span the whole window and are not admitted; any range drawn from them is redrawn and entered in the ledger. RD-04
  (a2) gives no per-session trailing range for the overnight sessions, so those sessions need their own reading. Q-121's
  file is a licensed-price derivative (E-179), read in place only. **Built, not yet run (Q-171):**
  `scripts/s1_range.py` (definitions, the declared share and the quantile rule in `extended/s1_range.py`'s docstring)
  writes `results/s1_range.csv` from a clean run under the lock; `lever_space.bounds("S1")` stays `NotComputed` until
  that file and its manifest exist, then loads each session's k range after checking the manifest.
- **T7, the admission forecast.** F-R's HAR coefficients and calibration, refitted on the search years only. F-R's own
  fit was to the choice block, which is the same span (F-R 6.3), but it was never run, so nothing exists to reuse.

**Four rows are to declare** before their ranges load: T2b (the NY AM / NY PM boundary), A15 (routing), A16 (the
mix's shares and assignment), and A17 (the state rule). **Two rows lean on unstated rules** and are refused by key: A9
(`hold_expiry_days`) and A19 (`payout_request_amount_choice`).

**Entries for the held-out read ledger (CHARTER 3.6 (b)) from this table's sources.** No range here is drawn from a
whole-window reading. Three sources are entered so that the search declaration completes them:

- S2's ends are RD-05 2.6's grid, which cites Stage 2 D-429's reference ratios. Whether that screen read 2024 to 2026
  is for the declaration to state.
- T1's `p14` and `p16` are sources whose hours, rung map and mark cutoff were chosen on the whole window (Stage 2
  D-626, D-554; E-203 S-2). These are already on the ledger's floor.
- The stop floor (S1) is the registered rule's stand-aside floor, a Stage 2 constant (D-271 (3)). Whether its
  derivation read 2024 to 2026 is for the declaration to state.

## 7. Interpretations made in this table (Q-151)

1. **The hour from the reopen to 18:00 CT** is a fifth window, `evening`. Stage 2's windows start Asia at 18:00, and the
   operator asked for every session the firm allows.
2. **The NY AM / NY PM boundary** is left to the trigger library (T2b, refused), not chosen here.
3. **The last new entry** is the "Avoid opening new positions after ..." sentence of `trading_hours`' verified note,
   not the flat itself.
4. **The stop's cap** is the widest stop at which one micro's stop-out fills the larger start room, before costs. It is
   loose on purpose: the search's limits and RD-05 part B's sizing bind first.
5. **Dollar risk is in dollars**, not in volatility units (section 1, units). Only the stop takes the volatility unit.
   RD-04 notes that a range-scaled design needs a classification row first (E-157). That row is the lead's.
6. **A source kind "to declare"** is added beside the brief's "to compute", and is refused the same way.
7. **A9 and A19 are refused by their unstated keys**, rather than given the declared readings. The brief's loader
   refuses an unverified key, and so the readings belong to the search declaration.
8. **A7's and A11's upper ends** are declared values (RD-03's 7; D-501's 20 a month), since no rule bounds them. The
   loader stops if either rule (`combine_count_limit`, `account_start_rate_limit`) ever states a bound.
9. **The rule reader prefers this repository's record** where it holds a key. So `hold_expiry_days`, verified in Stage
   2's ledger but `unstated` here, is refused.
10. **Contract constants** (the tick values in `instruments.yaml`, which that file marks for human verification, and the
    stand-aside floor) are treated as contract arithmetic, as every engine figure is.
