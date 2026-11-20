# The lever table: My Funded Futures (MFFU) $50K design search (Q-151b; beside Topstep's, Q-151)

Drafted 2026-11-20 on `wt/wt-payout` for the lead. **Status: groundwork for the search declaration (Wave 5.1), not a
declaration.** Nothing here is pinned or chosen, and no search or run is built. The table holds no result number and
types no rule value: a rule-derived bound is written as its key, and `extended/lever_space_firms.py` reads it from this
repository's record (`config/rules_extended.yaml`; nothing of MFFU is in Stage 2's ledger). The numbers that do appear
are declared parameters of Topstep's table (`lever_space.DECLARED`), cited there.

Read with: Topstep's table (`docs/plans/LEVER_TABLE_topstep50k.md`), whose 39 rows this one mirrors id for id; the
operator's direction that each firm is traded on its own execution protocol (a Topstep-tuned design is never carried
unchanged to another firm); Q-136's record of MFFU (E-197, E-198); RD-05's `RE` configuration
(`prereg/RD-05_firm_modes.md`, `extended/modes_terms.py`); CHARTER 3.3 to 3.5 and 4.

---

## 1. The plan, and why

**Rapid EOD 50K, the default version (no daily loss limit)** -- RD-05's `RE`. Every MFFU product on the record is a
$50K account, Topstep's size, so the choice is among MFFU's seven $50K products. Rapid EOD is the one closest to
Topstep's Trading Combine in mechanics the engine already represents:

- its drawdown is end-of-day trailing in **both** phases (`mffu.rapideod50k.eval_drawdown`,
  `mffu.rapideod50k.funded_drawdown`), as Topstep's is. Rapid 50K's funded floor trails intraday on equity
  (`mffu.rapid50k.funded_drawdown`), which the engine cannot represent without each trade's excursion (E-198; RD-01's
  G-1);
- it seats several funded accounts (`mffu.max_funded_accounts`), where Builder seats one (`mffu.builder50k.funded_seats`);
- its rules are the most fully verified of the plans: Pro 50K's funded lock, buffer and cap are unverified
  (`mffu.pro50k.funded_drawdown_lock`, `mffu.pro50k.payout_buffer`, `mffu.pro50k.payout_cap`), its sizing policy is
  discretionary (`mffu.pro50k.funded_conduct_policy`, priced at tier 3 by E-199), and its funded position limit reads
  oddly as printed (`mffu.pro50k.funded_position_limit`);
- the daily-loss-limit version is a different account chosen at checkout, as Topstep's election is (A14, dropped).

It is also where the operator's example bites: Rapid EOD's funded account allows its full contract limit from
activation (`mffu.rapideod50k.funded_position_limit`, no scaling plan), where Topstep's funded account starts lower and
scales (`funded_scaling_plan`). Its evaluation's consistency share, minimum days and payout gate all differ from
Topstep's. The other MFFU products would each need their own table.

## 2. Sources and refusals

As Topstep's section 1, with one addition. A rule key that is **absent** from the record, or present with any status but
`verified` (`unverified`, `unstated`, `changed`), refuses its lever with **`NotVerified`** (a `firm_terms.UnverifiedTerm`).
It is never guessed and never given a declared reading here. The search declaration may declare a reading of a gap, as
RD-05's U-rules do. **To compute** (`NotComputed`): no MFFU lever has a search-year reading yet. S1 needs its own,
because its caps are MFFU's and its sessions come from MFFU's day (T2). **To declare** (`NotDeclared`) and **dropped**
(`DroppedLever`) are as in Topstep's table.

The last column compares each lever with Topstep's, mechanically (`lever_space_firms.vs_topstep`, under no S1 reading):
**identical** means the same outcome as Topstep's (the same range, or the same refusal), read from no MFFU rule, or
dropped in both tables; **differs** means MFFU's own rules enter, or the outcome is not Topstep's (the reason follows);
**refused** means the lever is refused for want of a verified MFFU rule. `tests/test_lever_space_firms.py` checks that
this column matches the code.

## 3. The levers

Notation as Topstep's table. `P.` stands for `mffu.rapideod50k.` in the prose only; every key in the rows is written in
full.

### 3.1 Trigger layer

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class | vs Topstep |
|---|---|---|---|---|---|---|---|---|
| T1 | trigger | signal source of a component | Topstep's T1 (`coin`, `p14`, `p16`, `rl3`) | declared: E-208's dispositions | categorical; reads nothing | T2, T3, T4, T5, A16 | searched | identical |
| T2 | trigger | session of a component | `evening`, `asia`, `london`, `ny_am`, `ny_pm`, covering MFFU's whole day from its reopen at the Globex open to its automatic close (`mffu.trading_hours`, printed as EST and read as New York local time, converted to CT by zoneinfo); day-free, the boundaries are Topstep's declared window starts; for a trading day, the day calendar's local-time anchors (`day_calendar.anchored_starts`), shifted to MFFU's reopen (`lever_space_firms.mffu_session_windows`) | arithmetic: `mffu.trading_hours`, with the declared window starts or the day calendar's anchors | a session; reads nothing | T1, T2b, T3 | searched | differs -- the same sessions, on MFFU's own day (Q-181b): its reopen and close read from `mffu.trading_hours`; the reopen is checked against the exchange's open in the same entry |
| T2b | trigger | the NY AM / NY PM boundary | to declare (Wave 3.3) | to declare | a wall-clock time | T2 | declared | identical |
| T3 | trigger | entry window: a component's offer marks | from MFFU's reopen to its last new entry, in Topstep's mark step. MFFU states no last-entry time apart from its automatic close (`mffu.trading_hours`), so the last new entry is the close; on a holiday there is no automatic close and the user flattens before the early close | arithmetic: `mffu.trading_hours`; the declared mark step | minutes after the reopen | T2, T4, A3 | searched | differs -- the last new entry is MFFU's close, where Topstep's page sets one before its flat |
| T4 | trigger | latency L, alert to order | Topstep's T4: the three declared cells, `p16` and `rl3` one cell | declared: E-202 (2)(c); CHARTER 3.3 (g) | clock minutes | T1, T3, T5 | searched | identical |
| T5 | trigger | entry type | `market`, `limit`: one limit per entry. Several limit orders at one price are prohibited (`mffu.automation_and_sim_fills`), and a design that places them is refused as tier 1 | declared: E-202 (2)(d); F-04 6.1 R-4 | order type | T1, T4, T6 | searched | differs -- the same choices, held against MFFU's simulator-fill rule (`mffu.automation_and_sim_fills`) |
| T6 | trigger | how long a limit works | Topstep's T6 | declared: F-04 6.1 | minutes | T5 | declared | identical |
| T7 | trigger | admission by forecast resolution | `off`, or Topstep's T7's rule; refused until fitted | **a search-year reading, to compute** | a probability | T1, T3, S1, S2 | searched | identical |
| T8 | trigger | side rule | the coin side; a new trade takes any open position's side or is skipped. MFFU counts NQ and MNQ as one underlying for hedging (`mffu.hedging_rule`) | declared: CHARTER 3.2, 3.5 | side rule | T1, T5, A15 | declared | differs -- the same rule, held against MFFU's hedging rule (`mffu.hedging_rule`) |

### 3.2 Trade-shape layer

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class | vs Topstep |
|---|---|---|---|---|---|---|---|---|
| S1 | trade shape | stop width | a multiple k of the trailing range; k's range is MFFU's own search-year translation of its caps (`lever_space_firms.stop_caps('mffu')`: Topstep's registered floor, and the widest stop at which one micro fills the larger start room of `mffu.rapideod50k.eval_drawdown` and `mffu.rapideod50k.funded_drawdown`) | **a search-year reading, to compute** (MFFU's own; Topstep's file is checked against Topstep's caps) | multiple of the session's trailing range | T2, S2, S3, S4, S5 | searched | differs -- MFFU's caps and MFFU's sessions; no reading yet |
| S2 | trade shape | reward-to-risk w | Topstep's S2 (RD-05 2.6's grid) | declared: RD-05 2.6 | ratio | S1, A1, A2 | searched | identical |
| S3 | trade shape | dollar risk per trade, evaluation | from one micro at the floor stop to the evaluation's room (`mffu.rapideod50k.eval_drawdown`), whole micros, within `mffu.rapideod50k.eval_position_limit` | arithmetic: `mffu.rapideod50k.eval_drawdown`, `mffu.rapideod50k.eval_position_limit` and the stop's floor | dollars at the stop | S1, S5, A1 | searched | differs -- MFFU's room and contract limit |
| S4 | trade shape | dollar risk per trade, funded | from one micro at the floor stop to the funded room below the start (`mffu.rapideod50k.funded_drawdown`), within `mffu.rapideod50k.funded_position_limit`: flat, no scaling plan | arithmetic: `mffu.rapideod50k.funded_drawdown`, `mffu.rapideod50k.funded_position_limit` | dollars at the stop | S1, S5, A2, A5 | searched | differs -- the full contract limit from activation, where Topstep's funded account scales (`funded_scaling_plan`) |
| S5 | trade shape | instrument mix | `MNQ`, `mixed` (Topstep's S5), counted against `mffu.rapideod50k.eval_position_limit` and `mffu.rapideod50k.funded_position_limit` at Stage 2's micros per mini; one underlying for hedging (`mffu.hedging_rule`) | declared: F-04 6.1; the counting from the keys | categorical | S3, S4 | searched | differs -- MFFU's limits, the same in both phases |
| S6 | trade shape | maximum hold (a time stop) | **dropped**: CHARTER 4 bans time stops | declared: CHARTER 4 | -- | -- | dropped | identical |
| S7 | trade shape | breakeven stop move | **dropped**: off; exploiting the simulator's fills with tight brackets is prohibited (`mffu.automation_and_sim_fills`) and is tier 1 | declared: RL3 6.1; F-04 6.1 | -- | T1 | dropped | identical |
| S8 | trade shape | partial exits, scaling in | **dropped** | declared: F-04 6.1 | -- | -- | dropped | identical |
| S9 | trade shape | contracts | **dropped as a lever**: derived from S1, S3 or S4, and S5 | arithmetic: RD-05 part B's sizing | -- | S1, S3, S4, S5 | dropped | identical |

### 3.3 Account-policy layer

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class | vs Topstep |
|---|---|---|---|---|---|---|---|---|
| A1 | account policy | steady or flip, evaluation | `steady`; or `flip` at r_flip = target / (k_E x w), cut to the room. Target `mffu.rapideod50k.eval_profit_target`; k_E is RD-05's fewest passing days from `mffu.rapideod50k.eval_consistency` and `mffu.rapideod50k.eval_min_days`; the room `mffu.rapideod50k.eval_drawdown`; a broken consistency extends (`mffu.eval_consistency_breach`); no daily limit on this version (`mffu.rapideod50k.eval_daily_loss_limit`) | arithmetic: RD-05 part A | policy | S2, S3 | searched | differs -- MFFU's share and minimum days set k_E |
| A2 | account policy | steady or flip, funded | `steady`, `flip` at b\* / (k_F x w). k_F from `mffu.rapideod50k.payout_gate`; b\*, the least balance at which the first request is largest, rests on how much a request may take, which no page states (`mffu.rapideod50k.payout_request_amount`), with `mffu.rapideod50k.payout_min`, `mffu.rapideod50k.payout_cap` and the room `mffu.rapideod50k.funded_drawdown` | arithmetic: RD-05 part A | policy | S2, S4, A5 | searched | refused -- `mffu.rapideod50k.payout_request_amount` is unstated |
| A3 | account policy | session rule q ("when to stop") | `one`, `all`, `cap`: in the evaluation until the session's net reaches `mffu.rapideod50k.eval_consistency` x `mffu.rapideod50k.eval_profit_target`; the funded account has no consistency rule (`mffu.rapideod50k.funded_consistency`), so `cap` is evaluation-only | declared: F-04 6.1; the allowance by rule | categorical | T3, A5 | searched | differs -- MFFU's evaluation share; no funded cap |
| A4 | account policy | price path | one path: the plan's one-time price (`mffu.rapideod50k.eval_fee`, `mffu.billing_basis`) and no activation fee (`mffu.activation_fee`); MFFU has no second path like Topstep's No Activation Fee | rule | -- | A12 | declared | refused -- `mffu.rapideod50k.eval_fee` is unverified (no page text ties a price to the size) |
| A5 | account policy | payout path | one path, `buffer_then_daily`: `mffu.rapideod50k.payout_gate` (a realised-profit buffer, a wait after the first trade, then each request needs profit since the last), `mffu.rapideod50k.payout_min`, no cap (`mffu.rapideod50k.payout_cap`), `mffu.rapideod50k.payout_split` | rule | -- | A2, A3, A18, A19 | declared | differs -- one path, MFFU's gate, where Topstep chooses between two at activation |
| A6 | account policy | funded seats held at once | 1 to the Rapid EOD clause of `mffu.max_funded_accounts`, step 1; one account per trade | rule | accounts | A7, A8, A15 | searched | differs -- MFFU's Rapid EOD seat limit |
| A7 | account policy | evaluations running at once (C) | 1 to the lesser of Topstep's declared upper end and `mffu.max_eval_accounts`, step 1 | declared: RD-03 2.2, cut by `mffu.max_eval_accounts` | accounts | A6, A8, A11 | searched | differs -- MFFU states a cap, Topstep none |
| A8 | account policy | banking: buy evaluations while a pass waits | `on`, `off`, once the record says what a pass at the seat limit does | declared: RD-03 2.2; `mffu.hold_queue_behaviour` | categorical | A6, A7, A9 | searched | refused -- `mffu.hold_queue_behaviour` is unstated |
| A9 | account policy | the hold's expiry | refused, as Topstep's | declared (readings of an unstated rule): `mffu.hold_queue_behaviour`, `mffu.hold_expiry_days` | reading | A8, A10 | declared | refused -- `mffu.hold_queue_behaviour` and `mffu.hold_expiry_days` are unstated |
| A10 | account policy | evaluation-purchase rule | Topstep's A10 (`replace`, `house_stop`, `house_zero`); one-time purchases, nothing to cancel (`mffu.billing_basis`) | declared: RD-03 2.3 | categorical | A9, A11 | searched | differs -- the same choices on MFFU's one-time billing |
| A11 | account policy | evaluation-purchase budget | Topstep's A11, once the record says that no rule limits starts | declared: Stage 2 D-501; `mffu.account_start_rate_limit` | purchases a month | A7, A10 | searched | refused -- `mffu.account_start_rate_limit` is unstated |
| A12 | account policy | Back2Funded reactivations | **dropped**: Topstep's product; no reactivation product of MFFU is on the record | declared | -- | A4, A6, A18 | dropped | differs -- Topstep's lever loads; MFFU has none on the record |
| A13 | account policy | resets | **dropped**, as Topstep's: an adapter is owed, and the reset's price is unverified (`mffu.reset_fee`) | declared: RD-03 2.5 | -- | A4 | dropped | identical |
| A14 | account policy | daily-loss-limit election at checkout | **dropped**: a different account (`mffu.rapideod50k.eval_daily_loss_limit`) | declared: RD-05 2.3 | -- | S3, S4 | dropped | identical |
| A15 | account policy | routing | to declare (Wave 3.3), with the no-opposing-positions guard | to declare | rule | A6, A7, A16, T8 | searched | identical |
| A16 | account policy | signal mix | to declare (the restart plan 4.4) | to declare | shares | T1, A15 | searched | identical |
| A17 | account policy | state rule | to declare (the triage) | to declare | rule | S3, S4, A1, A2 | searched | identical |
| A18 | account policy | the first payout request (RD-02 L1) | `elig` (the first close at which `mffu.rapideod50k.payout_gate` opens and a request reaches `mffu.rapideod50k.payout_min`), `lock` (once the floor has locked, `mffu.rapideod50k.funded_drawdown_lock`); `elig` rests on the amount a request may take (`mffu.rapideod50k.payout_request_amount`) | declared: RD-02 6.1 | rule | A5, A19 | searched | refused -- `mffu.rapideod50k.payout_request_amount` is unstated |
| A19 | account policy | the request amount (RD-02 L2) | `max`, `half`, once the amount a request may take is on the record (`mffu.rapideod50k.payout_request_amount`; `mffu.rapideod50k.payout_cap`, `mffu.rapideod50k.payout_min`) | declared: RD-02 6.1 | share of the maximum | A5, A18 | searched | refused -- `mffu.rapideod50k.payout_request_amount` is unstated |
| A20 | account policy | request cadence after the first payout | every eligible close: MFFU's gate allows a request each day once profit since the last reaches its floor (`mffu.rapideod50k.payout_gate`) | declared: RD-02 6.1 | -- | A18 | declared | differs -- MFFU's daily gate, not Topstep's winning-day cycle |
| A21 | account policy | payout method | to choose once a method's fee and lag are on the record (`mffu.payout_fee`, `mffu.payout_processing_time`) | declared | -- | -- | declared | refused -- `mffu.payout_fee` unstated, `mffu.payout_processing_time` unverified |

## 4. The comparison with Topstep

**identical** (15): T1, T2b, T4, T6, T7, S2, S6, S7, S8, S9, A13, A14, A15, A16, A17.

**differs** (16): T2, T3, T5, T8, S1, S3, S4, S5, A1, A3, A5, A6, A7, A10, A12, A20.

**refused** (8): A2, A4, A8, A9, A11, A18, A19, A21.

Why the differing levers differ, in short:

- **Contracts and sizing (S3, S4, S5).** MFFU's limits are flat and the same in both phases, and the funded account has
  its full limit from activation. Topstep's funded account scales up from fewer minis. The rooms are MFFU's own keys,
  even where their figures happen to equal Topstep's.
- **The evaluation's pass (A1, A3).** MFFU's consistency share and minimum days are its own, so its fewest passing days
  (k_E), its flip size and the session cap differ. Breaking the share extends the evaluation rather than failing it.
- **The payout (A5, A20).** One path: a realised-profit buffer, then a request each day once the profit since the last
  request reaches its floor, with no cap. Topstep has two paths (standard and consistency) and a winning-day cycle.
- **Accounts (A6, A7, A10, A12).** MFFU caps Rapid EOD's funded seats and states an evaluation cap. Its purchases are
  one-time, so nothing is cancelled. It has no Back2Funded.
- **Conduct floors read from MFFU's pages (T5, T8).** The ranges are Topstep's, held against MFFU's simulator-fill and
  hedging rules.
- **The day (T2, T3).** MFFU's reopen and close are read from `mffu.trading_hours` (Q-181b). The sessions are
  Topstep's, on MFFU's day. The last new entry is MFFU's close, because the firm states no earlier one.
- **S1** needs MFFU's own search-year reading, because the caps and the sessions are MFFU's.

## 5. Combinations refused and floors fixed

Every Topstep floor (its section 5) holds. `lever_space_firms.check_design`, which `sample` runs on every draw, refuses
**conduct tier 1 for every firm**: opposite positions across accounts or firms, simulator-fill exploitation, maximum
size into major news, one trade copied across accounts, anything that conceals a pattern. It also refuses automated or
API order entry (the operator's hard limit), a setting of a lever refused at this commit, and a setting outside its
loaded range. The floors MFFU's own rules add are listed below. Each is read in the engine, not in the lever space.

- **Inactivity** (`mffu.inactivity_rule`): every account trades inside the rule's calendar window, or it can be closed
  and its profits forfeited. Seats and routing (A6, A15) must keep each account active.
- **News**: Tier 1 releases are closed on MFFU's window around each release (`mffu.news_tier1_rule`), on top of
  CHARTER 4's. On Rapid EOD's funded account, Tier 1 news trading was read on 2026-11-20 as not allowed
  (`mffu.rapideod50k.funded_news`; 16158363, 18337038). That reading is **held**: the key stays unverified under
  RD-05's pin (RD-05 4.1) and enters at RD-05's next declaration, so the engine does not load it yet. The evaluation
  allows Tier 1 news. CHARTER 4's news exclusions bind either way.
- **Holidays** (`mffu.trading_hours`): no automatic close at an early close; the user must be flat before it, or the
  account is breached.
- **The single-day profit ceiling** on the funded account (`mffu.rapideod50k.funded_single_day_profit_ceiling`): a day
  above it moves the account to Live.
- **Coordinated trading** (`mffu.coordinated_trading_rule`): one user's own accounts only, as CHARTER 4 already requires.

## 6. The work list: rules to verify (`/verify-rule`)

Each key below refuses the levers named, or (`engine`) must be verified before the engine can run any MFFU design
(`lever_space_firms.prerequisites`, `ready('mffu')`). Its status is this commit's, after the lead's read of the twelve keys (Q-181b): `mffu.trading_hours` is now verified and
leaves the list. `mffu.rapideod50k.funded_news` was read, but it is held unverified under RD-05's pin until RD-05's next
declaration. The rest stay. No worker verified any of them.

| key | status | refuses |
|---|---|---|
| `mffu.rapideod50k.payout_request_amount` | unstated | A2, A18, A19 |
| `mffu.rapideod50k.eval_fee` | unverified | A4, engine |
| `mffu.hold_queue_behaviour` | unstated | A8, A9 |
| `mffu.hold_expiry_days` | unstated | A9 |
| `mffu.account_start_rate_limit` | unstated | A11 |
| `mffu.payout_fee` | unstated | A21 |
| `mffu.payout_processing_time` | unverified | A21 |
| `mffu.eval_consistency_base` | unverified | engine (RD-05 U-15: whether a flip or a losing day passes) |
| `mffu.rapideod50k.funded_news` | unverified: read 2026-11-20 (not allowed), held under RD-05's pin (RD-05 4.1) | engine |
| `mffu.news_all_releases_protocol` | unverified | engine |
| `mffu.rapideod50k.commissions` | unverified | engine (the firm-wide `mffu.commissions` names no plan) |

## 7. Interpretations made in this table (Q-151b)

1. **The plan** is Rapid EOD 50K's default version (section 1). Every MFFU product on the record is $50K, so "the size
   closest to Topstep's" is exact, and the choice among the products is by mechanics.
2. **A key absent from the record refuses its lever**, as an unverified one does (`NotVerified`). Absent keys are named
   `mffu.<term>` for firm-wide terms and `mffu.rapideod50k.<term>` for the plan's. These names are this table's
   proposal for the verifier.
3. **A1 is not refused** for the unverified consistency base (`mffu.eval_consistency_base`). k_E and r_flip are the
   same under both bases (RD-05 7 item 1), so the range does not rest on it. Whether a flip passes does, so the key is
   an engine prerequisite.
4. **A4 and A5 are declared, not searched**: MFFU's plan has one price path and one payout path. Their rows still read
   and refuse by key.
5. **A7's upper end** is the lesser of Topstep's declared upper end and MFFU's stated cap. Topstep's loader stops when a
   cap is stated; here a cap is stated, and it cuts the declared range.
6. **The declared parameters of Topstep's table** (latencies, entry types, the w grid, policies, purchase rules and
   budget, banking, payout readings) are carried. They are ranges of the user's behaviour, not tuned trades. Their
   citing declarations (RD-02, RD-03) were written for Topstep, so the search declaration must extend them to MFFU by
   name. The search finds MFFU's own design inside them.
7. **The conduct floors** read from MFFU's pages (T5, T8, S7) are checked as keys. Whatever a page permits, tier 1 is
   refused by `check_design` for every firm.
8. **MFFU's clock** (Q-181b): `mffu.trading_hours` prints "EST"; the verifier read it as New York local time (labelled
   in the entry). The loader converts it to CT by zoneinfo, on the trading day or, day-free, on two declared
   search-year days (winter and summer) that must agree. It refuses if the reopen is not the exchange's open in the
   same entry. The last new entry is the close itself, since no earlier one is stated.
