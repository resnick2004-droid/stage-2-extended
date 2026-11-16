# DRAFT: other firms' contracts on the registered trades (reading FC) -- a described reading, unnumbered, not declared

**Status: DRAFT, first version, 2026-11-16 (TASK_QUEUE Q-54).** Written under the operator's ruling **E-023 (1)**
(`CHARTER.md` section 3), from the rules record of E-020 (`config/rules_extended.yaml`, `docs/RULES_CURRENCY.md`) and
Stage 2's verified ledgers, in the form reading PP's draft takes (`prereg/DRAFT_F-P_payout_policy.md`, E-025).

**What E-023 (1) makes of it.** The firm a user trades at leaves the offered trades unchanged: the same registered
entries, the same outcome of every offer at every R, the same days in the same order. So a firm's contract is a lever
that adds no trades, and this file is a **described reading**, not a family:

- it takes **no program family number** and spends **nothing** of the multiplicity budget;
- **no cell can carry, pass or fail**: there is no pass line, no level and no pick;
- every plan is read on the journey scorecard beside Topstep's, for the operator to choose from the menu;
- it is declared and pinned before its run, by its own decision row with its sha256 (as `prereg/RD-nn_<slug>.md`,
  E-025 (1)), so nothing in it is chosen after a look.

**Not pinned. No engine has been run for it, no cell built, no outcome of any plan computed or read.** Anything chosen
after a reading is exploratory and reported apart.

**Not E-020's "family C".** E-020 named a solver-only contract-fit read "family C". This reading solves nothing and
re-solves no table: it replays the registered trades and tables on each plan's verified contract. A later reading that
re-solves a state table for one plan (a sizing design for that contract) is its own declaration.

| field | value |
|---|---|
| reading | FC: P-16's registered trades (P-14's beside) on five plans' contracts -- Topstep's $50K (the reference), Lucid's LucidFlex 50K, DayTraders.com's EOD 50K, TradeDay's Fast Pass and Quick Pay End of Day 50K |
| kind | a **described reading** (E-023 (1)): never carried; the operator chooses from its menu |
| program family number | **none** (E-023 (1)); the next numbered family's k is unchanged by this file |
| level, pass line, pick | **none** |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16, read only inside Stage 2's engine by P-16's and P-14's registered builders (this reading's own code reads no bar) |
| the unit | one start day, replayed as U1 replays it (`vendor/stage2/docs/USER_MILESTONES.md`); each plan paired with Topstep on the same start |
| blocks | all starts (the menu's headline); the early and late blocks per measure by `u_select.block` (section 6) |
| runs | 27 replays (2 references that must reproduce registered rows, 16 corner runs, 9 one-at-a-time runs), 27 denial-ladder replays beside, 16 gates beside (section 7) |
| unread terms | each read by a rule fixed in section 5; prices at both ends of their listed bracket, or on a declared grid where none is listed |
| seeds | from 20261990 to 20261999: four in use, four reserved, two retired because found in use elsewhere (section 12) |
| confirmation | none: nothing is carried (section 11) |

---

## 0. What a plan's contract changes, stated truly

A plan leaves the **offered** trades unchanged: the same registered entries, the same outcome of each offer at each R,
the same days in the same order. So each plan's run is a matched pair with Topstep's on every start day, and the
market path's luck is shared.

It does **not** leave the **executed** trades unchanged. From the first session, each plan's own terms move:

- **the allowance** (how many contracts an account may hold, by phase and balance): the size each trade takes, so its
  dollar risk and its realised-to-intended risk. P-14's 12.5-point stop under a 100-micro allowance is not P-14's
  Topstep size;
- **the floor** (the drawdown's type, its lock, and what a payout does to it): when an account ends;
- **the payout gate and the amount** (winning or qualifying days, consistency shares, caps, minimums): when and how much
  is paid, and so the balance left and the scaling tier;
- **the split and the fees** (evaluation price and billing, activation, recurring fees, payout fees): the cash;
- and then, as in reading PP, **which account the longest-waiting router hands each later offer to**, the
  evaluations bought, the seats' use.

For P, a start's difference between two plans is nonzero only where a month's "ahead" flips, so it is lumpy.

## 1. What this reading is, and what it is not

**Its job.** For each plan, the operator sees what the registered trades and tables do to one user's journey there,
month by month, beside Topstep's: how many users the plan helps and hurts against Topstep, by how much, with what
uncertainty, with the denial ladder beside; and, where a plan's terms are not all read, the spread its declared readings
give (its two corners, section 7).

**What it is not.** A claim that a plan is better; a candidate; a recommendation of a firm; a design solved for any
plan (G-6); a statement about live accounts (G-4).

**Why it is described rather than tested.** E-023 (1): a lever that adds no trades is described, never carried. The
same few independent three-month stretches of the late block that left payout policy undetectable at any numbered
family's level (audit B, Q3; the red team on reading PP) are all a plan comparison would have.

**What the operator's choice from the menu will mean.**

- It is recorded in its own decision row as the operator's choice from a described development reading.
- It takes no registration id and no confirmation.
- Every statement made from it is a description of the development window.
- Buying any plan, or any read that needs a checkout, is a purchase: stated, and waited for.

## 2. The plans, and the user held fixed

### 2.1 The five plans

| id | plan | configuration read | why here | terms from |
|---|---|---|---|---|
| TS | Topstep $50K Trading Combine -> Express Funded Account | Standard path, Aeropay payouts | the reference: P-14's and P-16's registered rows | Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`) |
| LU | Lucid Trading LucidFlex 50K | daily loss limit off at checkout, 40 % evaluation consistency (`STANDARD_40`) | Stage 2's verified second firm (Stage 2 D-574, D-575) | the vendored Lucid ledger through Stage 2's adapter `propedge.contract.lucid`, by import |
| DT | DayTraders.com EOD 50K -> EOD Pro Account | Monthly billing | E-020's short list | the record (E-020) |
| FP | TradeDay Fast Pass End of Day 50K -> Funded Sim | the terms for an account opened on or after 2026-07-26 | E-020's short list | the record (E-020) |
| QP | TradeDay Quick Pay End of Day 50K -> Funded Sim | intraday funded drawdown | E-020's short list | the record (E-020) |

**Not here, and why:**

- the eight firms whose own terms forbid automated retrieval (E-020 (2)); their plans are read, if ever, through the
  operator's browser or with the firm's written permission;
- the other firms of the Q-12 screen (E-009), whose terms were never recorded;
- Lucid's 50 % consistency add-on (a second checkout product, its price verified; a later reading if wanted);
- DayTraders' Lifetime billing (its evaluation and Pro prices are not stated separately, G-7);
- Topstep's No Activation Fee path and the $100K / $150K sizes (closed at the fit, the handoff 3.1).

### 2.2 Today's terms, on every start

Each plan's terms as the record read them (its `date_read`) are applied to every start day from 2020 to 2026, as
Stage 2 replays Topstep's current rules over its history. A user starting now opens an account now, so Fast Pass is
read with its terms for accounts opened on or after 2026-07-26. Rule changes over the history are not modelled (G-11).

### 2.3 The user, held fixed across the plans

- **The trades.** P-16's registered trades (`rc_s150_all_nr`, `rc150_dev_test.TRADES_SHA256`) as the headline, and
  P-14's (A3-BRK30-CB20, U1's own builder) beside. Each with its own registered state table, protocol and routing (the
  longest-waiting account, one position at a time across the firm with five minutes flat, Stage 2 D-429), its purchase
  budget (at most 20 evaluation purchases in 21 sessions, P-14's), and its sizing rule's mode, headroom, stand-aside,
  room cap and fee schedule. **Only the plan's allowances replace Topstep's**, as Stage 2's `lucid_setup` does for
  Lucid (Stage 2 D-575).
- **The seats.** Five; at most five accounts of every kind together (evaluations, funded accounts and passes waiting),
  each design's own `max_total_accounts`. That is inside every plan's caps (section 4). With the total at or below the
  funded cap a pass never waits for a seat (the engine's rule, `lockstep.simulate_lockstep_path`'s
  `max_total_accounts`), so no plan's hold queue is ever reached -- checked (9.3).
- **No resets.** Neither design buys a reset; a failed evaluation is replaced by a new purchase.
- **The payout request rule (declared; P-14's and P-16's, carried to every plan).** At every close at which the plan's
  own rules make the account eligible, request **the smaller of half the balance above start and $2,000** -- the
  reference's amount, Topstep's `payout_max_frac_of_balance` and `xfa_std_cap` -- **cut to the plan's own per-request
  cap and its remaining-balance rule, rounded down to the plan's increment; no request below the plan's minimum.** At
  TS, LU, DT and FP this is the plan's own maximum (5.3 shows why); at QP, whose pages state no per-request maximum, it
  is the reference's amount. It is a declared choice: the payout lever itself is reading PP's subject, not this one's.
- **Hand entry**, at least five minutes from alert to order (E-008). One user's own accounts at one firm: each plan is
  read alone, never beside another firm (Stage 2 read Lucid beside Topstep, section 3).
- **Conduct.** Tier 1 untouched. Tier 2: Topstep's Responsible Trading Program and Focused Trader Program are Topstep's
  own -- at TS exactly as in its registered rows (the placement off in the headline); no other plan's discretionary
  program is modelled, and no conduct model runs at LU, DT, FP or QP (as Stage 2 runs Lucid, `conduct=None`). Tier 3:
  the payout-denial ladder at every plan (10.1 item 7).

## 3. Prior exposure: what has already read these plans, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| Stage 2 D-575, D-577 (`scripts/rc150_firm_split.py --second-firm lucid`) | P-16's five seats split between Topstep and Lucid | 500 gate paths | growth at the bound; D-577 (as D-593 quotes it) found a Lucid seat worth less than a Topstep seat | two firms together, on growth; never Lucid alone |
| Stage 2 D-593, D-601 (`rc150_added_lucid`) | Lucid seats added to Topstep's five | gate paths | closed on growth (as D-643 quotes D-601) | as above |
| U1, Stage 2 D-620 (`results/user_journey.csv`, config `p16_5+1`) | five Topstep seats and one Lucid seat, every start | all starts | its start rows are on file; D-626 (7), as D-643 quotes it, found it the highest mean net from month 3 and the highest cash before the first payout | the Lucid identity (9.1 item 3) reproduces these rows; Lucid alone was never run |
| Stage 2 program U, family 5 (D-643, D-644; `results/u_firms.csv`) | Lucid seats 1, 2 or 5 beside Topstep's five, from day 0 or after the first payout | both blocks | its outcome was not opened by the drafter | Lucid beside Topstep only |
| Q-12's survey (E-009; `docs/research/firms_survey_2026-11-15.md`) | zero-edge contract ceilings from quoted terms -- arithmetic, not a simulation | no NQ | "no firm clearly above Topstep's $50K" (E-009) | the drafter saw the survey's ceiling table rows for DayTraders and TradeDay while locating their sections |
| program U's nine families | P on the late block against P-14 | starts from 2024 | all closed | the late block is late development, not out of sample |

**Never run:** P-14's or P-16's trades on DayTraders' or TradeDay's contracts; Lucid alone (five Lucid seats, no
Topstep) on either; any Lucid run on P-14.

**The drafter's own reads (disclosed).** The record (both files); Stage 2's ledger and the vendored Lucid ledger; the
engine's account classes, the gate, the U1 runner and the Lucid adapter and setup; Stage 2's decision rows D-561,
D-574, D-575, D-593, D-643 and D-644 (which state the outcomes quoted above); the survey's sections for DayTraders and
TradeDay, for their conduct, news and product lines. No result file of any plan was opened; `u_firms.csv` and
`user_journey.csv` were not opened.

**What is already known of the direction (disclosed).** The survey's zero-edge arithmetic (E-009); Lucid beside
Topstep on growth (D-577, D-601) and on the journey (D-626 (7)). Nothing is known of any plan alone on the journey.

## 4. The contracts on the engine

**What the engine represents** (`vendor/stage2/propedge/campaign/lockstep.py`; balances are relative to the start):

- the evaluation (`CombineAccount`): a target; a drawdown trailing at the close, breached by any trade; its lock; a
  consistency share read as `max(target, best day / share)`, so a best day over the share raises the target and fails
  nothing; an optional daily loss limit that ends the day and fails nothing (the account's `dll`);
- the funded account (`FundedAccount`): a floor from `xfa_mll_start` trailing at the close up to `xfa_lock_at`, moved to
  the lock at any payout; winning days of a minimum size; a request of `min(share x balance, cap)`, cut by the policy's
  `keep_balance`, refused below `payout_min`; one split; a payout fee; the request-day exclusion of `REQUEST_AFTER_5PM`;
- the allowance (`propedge.campaign.sizing`: an evaluation limit in micros and a funded ladder by balance);
- fees (an evaluation price rebilled every `billing_days` sessions, activation, reset), the payout lag, the seats, and
  a household rule (R7);
- **the seams:** `funded_account_cls` and `combine_account_cls` on the path (`simulate_lockstep_path`; the vendored
  campaign passes the first on and not the second), `household_closure`, `payout_timing`; and, for the gate,
  `extended/gate.py`'s `funded_account_cls` (Q-47, E-028).

The tables below say, term by term, how each plan's verified term reaches the engine: **field** (a vendored field set
to the plan's value), **A-n** (an adapter in `extended/`, 4.6), **G-n** (a gap, 4.7), or **moot** (it cannot bind under
section 2.3's user, checked in 9.3). Section 5 reads every term that is not verified. Appendix R lists every key cited.

### 4.1 TS -- Topstep $50K, Standard path (the reference)

Every term as in P-14's and P-16's registered rows, from Stage 2's ledger by the engine's own loader: target, drawdown
and lock (`combine_profit_target`, `combine_mll`, `combine_mll_lock_at`), consistency (`combine_consistency_max_day_frac`),
evaluation allowance (`combine_position_size_limit`), the funded floor (`xfa_mll_start`, `xfa_lock_at`), the
Standard path (`xfa_std_winning_days`, `xfa_std_winning_day_min`, `xfa_std_cap`, `payout_max_frac_of_balance`,
`payout_min`, `profit_split`, `require_profit_since_payout`), fees (`subscription_fee` every `billing_days`,
`activation_fee`, `payout_fee`), the lag (`payout_lag_days_aeropay`), the seats (`max_active_funded_accounts`), the
ladder (`funded_scaling_plan`, `scaling_tier_after_payout`). Nothing new: TS is the identity (9.1 item 1).

### 4.2 LU -- Lucid LucidFlex 50K (Stage 2's verified adapter, by import)

| term | Lucid's verified term (vendored Lucid ledger) | on the engine |
|---|---|---|
| evaluation target, drawdown, lock | $3,000; $2,000 end-of-day trailing; locks at start + $100 (`eval_profit_target`, `eval_drawdown_amount`, `eval_drawdown_type`, `eval_drawdown_lock`) | field (`lucid_rules`) |
| evaluation consistency, minimum days | 40 %; as few as three days (`eval_consistency_rule`, `eval_min_days`) -- the share implies the days | field |
| evaluation allowance | 40 micros (`eval_position_limit`) | field (`lucid_sizing_rule`) |
| price | $115.50 one-time with the checkout coupon; resets not bought (`eval_fee`, `eval_reset_fee`) | field (`lucid_price`) |
| daily loss limit | optional at checkout, off in the configuration read (`eval_daily_loss_limit`) | field (none) |
| funded floor | $2,000 end-of-day trailing, locking at start + $100, forced to the lock by a request (`funded_drawdown_amount`, `funded_drawdown_type`, `payout_balance_consequence`) | field |
| payout gate | five days of at least $150 and a net profit of at least $1 every cycle; at most five payouts (`payout_frequency_gate`) | `LucidFundedAccount` (Stage 2) |
| request, minimum, split | half the profit up to $2,000; $500; 90 % (`payout_cap`, `payout_min`, `payout_split`) | field |
| funded allowance | 2 / 3 / 4 minis at $0 / $1,000 / $2,000 (`funded_position_limit`) | field (`lucid_sizing_rule`) |
| lag, request timing | two business days; the request at the eligible close, no session excluded (`payout_processing_days`) | field (`LUCID_PAYOUT_TIMING`) |
| seats | five funded, ten evaluations, ten in all, per household (`max_accounts`, `eval_count_limit`) | moot (five) |
| the live move | after the fifth payout; every simulated account closes at a live move (16558826) | `HOUSEHOLD_CLOSES_AT_LIVE` (Stage 2); section 5 |
| funded monthly fee, payout fee | not verified (`funded_monthly_fee`, `payout_fee`) | section 5 (U-3) |
| conduct, products | hedging prohibited, cross-firm included; CME futures permitted (`prohibited_conduct`, `permitted_products`, `news_trading_terms`) | tier 1 untouched; NQ permitted |

### 4.3 DT -- DayTraders.com EOD 50K, Monthly billing

| term | DayTraders' verified term (record key) | on the engine |
|---|---|---|
| evaluation target | $3,000 (`daytraders.eod50k.eval_profit_target`) | field |
| evaluation drawdown | $2,000, end-of-day trailing; the balance must stay above it intraday (`daytraders.eod50k.eval_drawdown_amount`, `daytraders.eod50k.eval_drawdown_type`) | field: the engine's floor moves at the close and any trade breaches it |
| evaluation lock | starts at $48,000, stops at $50,000 (`daytraders.eod50k.eval_drawdown_lock`) | field (`combine_mll_lock_at` 0) |
| evaluation daily loss limit | $1,250, soft: positions closed, the account paused to the next session, not failed; from the day's starting balance (`daytraders.eod50k.eval_daily_loss_limit`) | A-2 sets the account's `dll`: the engine's own day-loss mechanics |
| evaluation consistency | best day at most 50 % of total profit, a gate on passing; "a small tolerance applies" (`daytraders.eod50k.eval_consistency_rule`) | field (share 0.50); the tolerance: section 5 |
| Qualifying Days to pass | two days each of at least $200, within the rules, ending within consistency (`daytraders.eod50k.eval_min_days`) | A-2 |
| evaluation allowance | 10 contracts, 100 micros (`daytraders.eod50k.eval_position_limit`) | field (sizing, 100 micros) |
| price | not read on any page (`daytraders.eod50k.eval_fee`) | section 5 (U-2) |
| billing | Monthly: rebills at the original price every 30 days (`daytraders.eod50k.eval_billing_basis`) | field: every 21 sessions, Stage 2's translation of 30 calendar days (`billing_days`, `billing_period_calendar_days`) |
| resets | none sold (`daytraders.eod50k.eval_reset_fee`) | moot (none bought) |
| activation | $5, within 10 days of the pass or the pass is forfeited (`daytraders.eod50k.activation_fee`) | field ($5); the 10-day window moot (no pass waits) |
| recurring Pro fee | a Monthly Pro Account rebills $5 every 30 days (`daytraders.eod50k.funded_monthly_fee`) | A-10 (every 21 sessions while the account lives) |
| funded floor | $2,000 end-of-day trailing, stops at $50,000 (`daytraders.eod50k.funded_drawdown_amount`, `daytraders.eod50k.funded_drawdown_type`, `daytraders.eod50k.funded_drawdown_lock`) | field |
| a payout and the floor | a request needs a balance of at least $52,600 and must leave at least $52,000; no page says a payout moves the floor (`daytraders.eod50k.payout_balance_consequence`) | the $2,600 gate and the $2,000 left: A-3. At a balance of $2,600 the floor has already locked at the start, so the engine's move of the floor to the lock at a payout changes nothing (tested, T-2) |
| funded daily loss limit | $1,250, soft (`daytraders.eod50k.funded_daily_loss_limit`) | A-3 sets `dll` |
| funded consistency | best day at most 30 % of the cycle's profit, a payout gate (`daytraders.eod50k.funded_consistency_rule`) | A-3 |
| funded allowance | 10 contracts, no scaling (`daytraders.eod50k.funded_position_limit`) | field (ladder `0:10`) |
| payout gate | eight Qualifying Days (at least $200, within the 30 % rule) since the last payout or activation; the request day does not count (`daytraders.eod50k.payout_frequency_gate`) | A-3; the request day excluded is the engine's `REQUEST_AFTER_5PM` exclusion |
| split, cap, minimum | 100 %; $2,000 a request; $500 in $50 increments (`daytraders.eod50k.payout_split`, `daytraders.eod50k.payout_cap`, `daytraders.eod50k.payout_min`) | field; the increment: A-3 rounds down |
| payout count, fee, processing | unstated (`daytraders.eod50k.payout_count_limit`, `daytraders.eod50k.payout_fee`, `daytraders.eod50k.payout_processing_days`) | section 5 |
| seats | five EOD Pro accounts within 15 simulated funded; evaluations unlimited; one login per household (`daytraders.max_funded_accounts`) | moot (five) |
| inactivity | Monthly: at least one day meeting the minimum daily profit ($200) in every rolling 30 days from purchase, else closed for good; the account types are not named (`daytraders.inactivity_rule`) | A-2, A-3 (a 21-session window); its reach: section 5 |

### 4.4 FP -- TradeDay Fast Pass End of Day 50K

| term | TradeDay's verified term (record key) | on the engine |
|---|---|---|
| evaluation target | $3,000, raised when the consistency share is exceeded (`tradeday.eval_profit_target`) | field |
| evaluation drawdown, lock | $2,000 end-of-day trailing, auto-liquidated intraday, freezes at start (`tradeday.eval_drawdown_amount`, `tradeday.eval_drawdown_type`, `tradeday.eval_drawdown_lock`) | field |
| evaluation daily loss limit | none (`tradeday.eval_daily_loss_limit`) | field (none) |
| evaluation consistency | 45 %: no fail, the target rises (`tradeday.fastpass_eod50k.eval_consistency_rule`) | field: the engine's `max(target, best day / 0.45)` is this rule |
| minimum days | three trading days, or "a minimum 7-day period" (`tradeday.fastpass_eod50k.eval_min_days`) | section 5; three is implied by the 45 % share already; seven needs A-4 |
| evaluation allowance | 5 contracts, 50 micros (`tradeday.eval_position_limit`) | field |
| price, billing | one-time; price not settled (`tradeday.fastpass_eod50k.eval_fee`, `tradeday.eval_billing_basis`) | field (never rebilled); the price: section 5 |
| resets | not settled (`tradeday.eval_reset_fee`) | moot (none bought) |
| activation, monthly fee | $0, $0 on Funded Sim (`tradeday.activation_fee`, `tradeday.funded_monthly_fee`) | field |
| funded floor | $2,000 end-of-day trailing, freezes at start (`tradeday.fastpass_eod50k.funded_drawdown_amount`, `tradeday.fastpass_eod50k.funded_drawdown_type`, `tradeday.fastpass_eod50k.funded_drawdown_lock`) | field |
| a payout and the floor | the first request moves the floor to start, fixed from then (`tradeday.fastpass_eod50k.payout_balance_consequence`) | field: the engine's own floor move at a payout |
| funded daily loss limit | none; no trading within 2 % of a price limit (`tradeday.funded_daily_loss_limit`) | field (none); the price-limit rule: G-2 |
| funded consistency | no day above 45 % of total gross profit, current profit plus payouts (`tradeday.fastpass_eod50k.funded_consistency_rule`) | A-5 |
| funded allowance | 2 contracts, plus 1 per $2,000 of profit at the close; no maximum stated (`tradeday.fastpass_eod50k.funded_position_limit`) | field (ladder `0:2,2000:3,4000:4,6000:5`); the cap at 5: section 5 |
| payout gate | five days of at least $150; balance above start; net profit since the last request; the 45 % rule; no buffer; no trading from the request until the payout is received (`tradeday.fastpass_eod50k.payout_frequency_gate`) | winning days and the profit since the request: field; the 45 % rule and the no-trading session: A-5; that session excluded from the next cycle: the engine's `REQUEST_AFTER_5PM` exclusion |
| split, cap, minimum | 80 %; $1,500 a request, and at most 50 % of the "account balance"; $250 (`tradeday.fastpass_eod50k.payout_split`, `tradeday.fastpass_eod50k.payout_cap`, `tradeday.payout_min`) | field; the 50 % base: section 5 (moot under 2.3) |
| the fifth request | the account moves to a new Funded Live account at the fifth request (`tradeday.fastpass_eod50k.payout_count_limit`) | A-5; whether the fifth is paid from Sim: section 5 |
| payout fee, processing | fee unstated; one business day (`tradeday.fastpass_eod50k.payout_fee`, `tradeday.fastpass_eod50k.payout_processing_days`) | the fee: section 5; the lag 1 session: field |
| seats | five active Funded Sim; further passes queued; ten accounts in all (`tradeday.max_funded_accounts`) | moot (five) |
| inactivity | dormant 30 days may be offboarded (`tradeday.inactivity_rule`) | G-10 |

### 4.5 QP -- TradeDay Quick Pay End of Day 50K

The evaluation is FP's (4.4) except: consistency 30 % (`tradeday.quickpay_eod50k.eval_consistency_rule`; the share
implies four days), minimum days five or seven (`tradeday.quickpay_eod50k.eval_min_days`; A-4 at both), and its price
(`tradeday.quickpay_eod50k.eval_fee`).

| term | TradeDay's verified term (record key) | on the engine |
|---|---|---|
| funded floor | $2,000 trailing **intraday on gross profit** (current profit plus payouts), freezing at start; a payout lowers the balance and not the floor (`tradeday.quickpay_eod50k.funded_drawdown_amount`, `tradeday.quickpay_eod50k.funded_drawdown_type`, `tradeday.quickpay_eod50k.funded_drawdown_lock`, `tradeday.quickpay_eod50k.payout_balance_consequence`) | A-7. In balance terms the floor is `min(0, peak gross profit - 2,000)`; the peak includes each open trade's favourable excursion, which Stage 2's trades do not carry (G-1), so it is bracketed (section 5, U-9) |
| funded consistency | none (`tradeday.quickpay_eod50k.funded_consistency_rule`) | field (none) |
| funded allowance | 5 contracts, no scaling (`tradeday.quickpay_eod50k.funded_position_limit`) | field (ladder `0:5`) |
| payout gate | after one day of trading; any time the balance is positive; no buffer, no winning days (`tradeday.quickpay_eod50k.payout_frequency_gate`) | A-7 |
| split | 50 % below $4,000 of current profit; 80 % above it if the payout leaves more than $4,000; a payout crossing $4,000 split proportionally (`tradeday.quickpay_eod50k.payout_split`) | A-7 |
| cap, count | no per-request cap stated; no count stated (`tradeday.quickpay_eod50k.payout_cap`, `tradeday.quickpay_eod50k.payout_count_limit`) | section 5 |
| the profit ceiling | trading pauses at $10,000 of gross profit per account for a Live review; profit above it is forfeited (`tradeday.quickpay_eod50k.funded_sim_profit_ceiling`) | A-7: the account ends at the first close its gross profit reaches $10,000, the excess forfeited, its balance not credited, payouts already requested arriving (Live not modelled, G-4) |
| payout fee, processing | US bank wire free; one business day (`tradeday.quickpay_eod50k.payout_fee`, `tradeday.quickpay_eod50k.payout_processing_days`) | field ($0, the US method; lag 1 session); the cut-off's time zone is immaterial at daily resolution |
| request timing | at the eligible close; no session excluded (there is no cycle) | field (`REQUEST_4_TO_5PM`'s mechanics, as Lucid's) |
| seats, inactivity, price limit | as FP | moot; G-10; G-2 |

### 4.6 What the engine cannot represent, built as adapters in `extended/` (declared; built after the pin)

Every adapter subclasses or wraps a vendored seam; none edits `vendor/`. Where a vendored body must be copied, it is
refused unless the vendored source hashes to its pin, as `extended/gate.py` does (Q-47). **Each has switches whose
Topstep setting is the vendored behaviour**, and with every switch at it the adapter must reproduce TS's registered
rows (9.1 item 2).

| id | adapter | what it adds |
|---|---|---|
| A-1 | `extended/firms.py` | a plan's contract applied to a design's replay arguments and gate arguments: rules, fees, billing, activation, lag, request timing, account classes, household rule, conduct, allowances. Lucid's by Stage 2's `rc150_firm_split.lucid_setup`, imported, on a setup made from the design's replay arguments; TS's leaves the arguments unchanged (tested equal) |
| A-2 | DayTraders evaluation (`CombineAccount` subclass, through `combine_account_cls`) | the soft daily loss limit (`dll`); the two Qualifying Days a pass needs (a day of at least $200 whose close has the best day at most 50 % of total profit); the inactivity closure (the account ends, not breached, when a 21-session window from its purchase holds no day of at least $200) |
| A-3 | DayTraders Pro (`FundedAccount` subclass) | eligibility by eight Qualifying Days since the last payout or activation (a day of at least $200 whose close has the cycle's best day at most 30 % of the cycle's profit; the request day excluded); the $2,600 request gate; at least $2,000 left after a request; requests rounded down to $50; the soft daily loss limit; the inactivity closure (21 sessions from activation) |
| A-4 | TradeDay evaluation (`CombineAccount` subclass) | a minimum count of trading days before a pass |
| A-5 | Fast Pass funded (`FundedAccount` subclass, with a decision wrapper) | the 45 % rule on gross profit; the session after a request untraded, the account read at a no-trade decision so that the router passes over it (Stage 2 D-162) and its signal goes to another account if one can take it; the fifth request (section 5) |
| A-7 | Quick Pay funded (`FundedAccount` subclass, with a wrapper on its draw) | the gross-profit intraday floor with the excursion bracket (U-9); eligibility; the tiered split; the $10,000 ceiling |
| A-8 | the gate for another plan | `extended/gate.py`'s `run_gate` gains `payout_lag_days`, `household_closure` and `combine_account_cls`; the last needs `simulate_lockstep_campaign` re-composed in `extended/` (its vendored body plus one keyword, pinned by its source hash), because the vendored campaign does not pass `combine_account_cls` to its paths |
| A-9 | Q-17's ladder adapter (`extended/user_beside.py`) | takes a plan's arguments from A-1; its `off` arm must still reproduce U1's start rows |
| A-10 | fee arithmetic | DayTraders' recurring $5 Pro fee, and the price grid and break-even price (10.1 item 9): exact arithmetic on each start's purchase, billing and activation records. Exact because the replay's bankroll never binds, so no purchase depends on cash -- checked on every start (9.3). In the gate beside, DayTraders' recurring fee is left out and its rows labelled an upper bound in it |

(There is no A-6: the evaluation's minimum days of both TradeDay plans are A-4.) **If A-5's pass-over cannot be built
without editing the vendored router, the build stops and reports; this declaration does not fall back.**

### 4.7 What is not modelled, listed as gaps

| id | gap | how it is shown |
|---|---|---|
| G-1 | Quick Pay's favourable excursion inside a trade: Stage 2's trades carry the adverse excursion (`DayBlock.mae`), not the favourable one | bracketed from the trade's own outcomes at the menu's R values (U-9); an exact walk of the bars would be a new walk with its own identity, not this reading |
| G-2 | TradeDay's "no trading within 2 % of a price limit" (the account lost on a breach): CME's limit levels are not verified (cmegroup.com refuses scripted reads, E-029) and this reading reads no bar | not modelled; every TradeDay row says so; its effect is not bounded |
| G-3 | TradeDay's tier-1 news auto-liquidation, two minutes either side of each release (the survey's 103000081072; not yet recorded, 16 item 2) | once recorded, a count of P-16's and P-14's trades open in those windows, from the trades' own entry and exit times (no bar read); a nonzero count lists them and labels the TradeDay rows "news liquidation not modelled" |
| G-4 | every live move: Lucid's (Stage 2's household readings), Fast Pass's Funded Live at the fifth request, Quick Pay's Live review at $10,000, DayTraders' discretionary live call that closes every simulated account | live accounts are not modelled; an account moved ends, its balance not credited |
| G-5 | commissions: Topstep's all-in round turns at every plan (Stage 2 D-575's reading for Lucid, above Lucid's listed fees); DayTraders' and TradeDay's schedules are not recorded (16 item 2) | labelled on every DT and TradeDay row; the direction is unknown there |
| G-6 | the state tables were solved for Topstep's contract (Stage 2 D-501) and are not re-solved for any plan (Stage 2 D-575 (1)'s known gap) | every plan's row is P-16's (P-14's) design traded there, not the best design for that plan |
| G-7 | DayTraders' Lifetime billing | not read: its prices are not stated separately |
| G-8 | each plan's discretionary review, and DayTraders' Terms clause on positions substantially larger than one's other trades (the survey's line; not yet recorded) | priced by the denial ladder only |
| G-9 | DayTraders' consistency "small tolerance", unsized | read strictly (U-8): a lower bound in that term |
| G-10 | TradeDay's 30-day dormancy offboarding (discretionary) and its broker's archive | not modelled; the designs trade most sessions |
| G-11 | rule changes over 2020-2026 | today's terms on every start (2.2) |
| G-12 | a soft daily loss limit's later signals: an account DayTraders pauses takes no further trade that day, and trades already dealt to it are not re-dealt (the engine's day-loss mechanics, as for Topstep's RTP limit) | counted (9.3) |
| G-13 | payouts unavailable in holiday hours; Topstep's move to a Live Funded Account | as in every registered row |

## 5. Unverified and unstated terms, each read by a rule declared now

### 5.1 The rules

- **U-1. A price a plan's own pages list differently** (a sale card, a list price, a help table): read at **both
  ends of the bracket of listed prices** -- the lowest and the highest -- both run. Every listed price inside the
  bracket is printed by the grid (10.1 item 9).
- **U-2. A price no page lists** (DayTraders' evaluation): read on a **declared grid of evaluation prices, $25 to $250
  in steps of $25**. The grid covers every 50K evaluation price listed in this reading's records (TradeDay's $69 to
  $248, Lucid's $115.50, Topstep's $49 a month). Its two ends are run; the rest is exact arithmetic (A-10). When the
  operator's browser read (16) records DayTraders' listed price or prices, the bracket is read off the grid by U-1 with
  no new run. No price inside the grid is chosen.
- **U-3. A fee no page states** (Lucid's funded monthly fee and payout fee; DayTraders' and Fast Pass's payout fee):
  **$0, and every money figure of that plan labelled an upper bound in that row** -- Stage 2's reading for Lucid
  (D-575), carried.
- **U-4. A term on which the plan's pages conflict** (TradeDay's minimum days): both read, the stricter at the strict
  end. "A minimum 7-day period" is read as seven trading days, the stricter of its readings.
- **U-5. A term no page states that changes timing only** (DayTraders' processing days): read at the bracket of the
  verified lags of the other plans here -- one session (TradeDay) and three (Topstep's Aeropay) -- both read.
- **U-6. A stated term whose reach is unstated** (Lucid's live move, DayTraders' inactivity accounts, Fast Pass's fifth
  request, Fast Pass's scaling maximum): the reading under which it helps the user least at the strict end; the other
  concrete reading at the lenient end where there is one.
- **U-7. A term that cannot bind under section 2.3's user** (the hold queues; DayTraders' 10-day activation window;
  TradeDay's reset fee; Fast Pass's 50 % base; Quick Pay's per-request cap): not read. A mechanical check shows it does
  not bind (9.3); if it does, the plan's rows carry the check's count and nothing more is claimed for them.
- **U-8. A relaxation of a stated rule that no page sizes** is never assumed (DayTraders' consistency tolerance).
- **U-9. A verified rule whose data the trades lack** (Quick Pay's intraday peak): bracketed between the two extremes
  the trades' own outcomes allow, both read (5.4).
- **U-10. A limit no page states is not invented** (DayTraders' and Quick Pay's payout counts): read as no limit,
  labelled; the discretionary live moves are G-4.

**The strict corner and the lenient corner.** Each term with two ends has a **strict** end (the one that helps the
user least: the dearer price, the slower lag, the wider closure, the later pass, the unpaid request, the higher floor)
and a **lenient** end. Every term's strict end is named in 5.2, so neither corner is chosen after a look.

### 5.2 Every such term, and its declared reading

| plan | term | record key(s) | status | strict end | lenient end | rule |
|---|---|---|---|---|---|---|
| LU | funded monthly fee | `lucid.flex50k.funded_monthly_fee` (the record); `funded_monthly_fee` (the vendored Lucid ledger) | unverified | $0, upper bound | the same | U-3 |
| LU | payout fee | `lucid.flex50k.payout_fee` (the record); `payout_fee` (the vendored Lucid ledger) | unstated; unverified | $0, upper bound | the same | U-3 |
| LU | the live move's reach | `max_accounts` (its note quotes 16558826) | verified; its reach in the engine is a reading | the first fifth payout ends every Lucid account, nothing more bought (`HOUSEHOLD_CLOSES_AT_LIVE`, Stage 2's conservative reading) | only the account that took its fifth payout ends (Stage 2's optimistic reading) | U-6 |
| DT | evaluation price | `daytraders.eod50k.eval_fee` | unverified (none listed) | $250 (the grid's top) | $25 (the grid's bottom) | U-2 |
| DT | payout fee | `daytraders.eod50k.payout_fee` | unstated | $0, upper bound | the same | U-3 |
| DT | processing days | `daytraders.eod50k.payout_processing_days` | unstated | three sessions | one session | U-5 |
| DT | payout count | `daytraders.eod50k.payout_count_limit` | unstated | no limit (the live call: G-4) | the same | U-10 |
| DT | inactivity's accounts | `daytraders.inactivity_rule` | verified; the account types unnamed | every evaluation and every Pro account | no account | U-6 |
| DT | consistency tolerance | `daytraders.eod50k.eval_consistency_rule` | verified; the tolerance unsized | 50 % strictly | the same | U-8 |
| DT | hold queue, 10-day window | `daytraders.max_funded_accounts`; `daytraders.eod50k.activation_fee` | verified; the queue unstated | moot: no pass waits (checked) | -- | U-7 |
| DT | billing basis | `daytraders.eod50k.eval_billing_basis` | verified | Monthly | the same (Lifetime not read, G-7) | -- |
| FP | evaluation price | `tradeday.fastpass_eod50k.eval_fee` | unverified ($99 sale card; $180 help table; $248 list card) | $248 | $99 | U-1 |
| FP | minimum days | `tradeday.fastpass_eod50k.eval_min_days` | unverified (3 against "a minimum 7-day period") | seven trading days | three (implied by the 45 % share) | U-4 |
| FP | reset fee | `tradeday.eval_reset_fee` | unverified | moot: no reset bought (checked) | -- | U-7 |
| FP | the 50 % base | `tradeday.fastpass_eod50k.payout_cap_share_base` | unverified (the balance, or the profit above start) | moot: the declared request is at most half the profit, inside both readings (checked) | -- | U-7 |
| FP | the fifth request | `tradeday.fastpass_eod50k.payout_count_limit` | verified; whether the fifth is paid from Sim unstated | the account ends at its fifth request, which is not paid | the fifth is paid at 80 %, then the account ends | U-6 |
| FP | payout fee | `tradeday.fastpass_eod50k.payout_fee` | unstated | $0, upper bound | the same | U-3 |
| FP | scaling maximum | `tradeday.fastpass_eod50k.funded_position_limit` | verified; no maximum stated | capped at the evaluation's 5 contracts | the same (a check counts the trades an uncapped ladder would size differently) | U-6 |
| QP | evaluation price | `tradeday.quickpay_eod50k.eval_fee` | unverified ($69 sale card; $174 list card; $175 help table) | $175 | $69 | U-1 |
| QP | minimum days | `tradeday.quickpay_eod50k.eval_min_days` | unverified (5 against "a minimum 7-day period") | seven trading days | five | U-4 |
| QP | reset fee | `tradeday.eval_reset_fee` | unverified | moot: no reset bought (checked) | -- | U-7 |
| QP | per-request cap | `tradeday.quickpay_eod50k.payout_cap` | unstated | moot: the declared request rule (2.3); a check shows no request above it | -- | U-7 |
| QP | payout count | `tradeday.quickpay_eod50k.payout_count_limit` | unstated | no limit (the $10,000 ceiling ends the account) | the same | U-10 |
| QP | the intraday peak | `tradeday.quickpay_eod50k.funded_drawdown_type` | verified; the data lack the peak | the pessimistic bound (5.4) | the optimistic bound (5.4) | U-9 |

### 5.3 Why the declared request rule is each plan's own maximum where one is stated

Write B for the balance above start at the request's close.

- **TS, LU:** each plan's maximum is `min(0.5 B, $2,000)` -- the rule itself.
- **DT:** the maximum is `min(B - $2,000, $2,000)`, with B at least $2,600. The rule is `min(0.5 B, B - $2,000,
  $2,000)`. Below B = $4,000, `B - $2,000` is the smaller of the first two; from $4,000 both are at least $2,000. So the
  two are equal at every B.
- **FP:** read on the profit, the maximum is `min(0.5 B, $1,500)` -- the rule. Read on the whole balance, the maximum is
  $1,500 at any B; the rule asks no more than it. So the 50 % base never enters (U-7).
- **QP:** no maximum is stated, so the rule is the reference's amount, `min(0.5 B, $2,000)`.

### 5.4 Quick Pay's intraday peak, bracketed (U-9)

For a Quick Pay funded trade taken at R = R_x with dollar risk r (the size the engine gave it), the trade's outcomes at
the menu's R values (Stage 2's `DayBlock.r_by_rr`) say at which targets it would have been filled before its exit. Two
brackets on the same entry share its stop rule (the breakeven move included) until one exits, so:

- if the trade **won at R_x**, its favourable excursion before its exit is m = r x R_x (it exits at its target);
- if it **did not win at R_x** (stopped, moved-stop exit, or flattened), r x R_lo <= m < r x R_x, where R_lo is the
  largest menu R below R_x at which it won (0 if none).

Write G for the gross profit (the balance above start plus the gross paid) and G_pk for its running peak. The floor in
balance terms is `min(0, G_pk - $2,000)`; G_pk includes the peak inside each trade, and the gross value after each
exit and at each close.

- **The pessimistic bound (the strict end).** A trade that did not win at R_x peaks one tick short of its target
  (m = r x R_x less one tick's value at its size), then falls to its exit. A trade that won at R_x takes its whole
  maximum adverse excursion at R_x (`DayBlock.mae_by_rr`) after a peak one tick short of its target, then rises to it.
- **The optimistic bound (the lenient end).** A trade that did not win at R_x peaks at r x R_lo, then falls to its
  exit. A trade that won at R_x takes every adverse excursion before its favourable one, so its peak is its exit.

In both: if the trade's path after its peak crosses the floor raised by that peak, the trade ends at that floor and
the account ends (a breach). Between trades and at the close, the floor follows the gross value. Both bounds are run
(the corners), and the strict one is flipped alone (7.2).

## 6. Data, blocks and the unit

1. **The unit** is U1's: one development start day, a fresh bankroll and fresh accounts, the design's trades replayed
   in historical order (`vendor/stage2/scripts/user_journey.py`; `customer_slices.replay`), for up to 252 sessions plus
   U1's exact-length runs. A month is 21 sessions. `USER_MILESTONES.md`'s definitions are used unchanged.
2. **The arms.** `verdict` (every R at its registered bound) is the headline; `point` beside. The bound was estimated
   on the whole development window (`vendor/stage2/prereg/P-14_a3-brk30-cb20.md`), so an early-block reading on the
   verdict arm is a function of 2024-2026 through that one constant. It shifts every plan alike and is inherited from
   program U (reading PP's N2).
3. **Pairing.** Every plan and TS run on the same start days, blocks and seeds. The per-start difference against TS is
   the unit of every paired reading.
4. **The blocks, per measure.** Every reading at horizon h (63 for months 1 to 3, 126 for month 6, 252 for month 12) is
   read on all starts with h sessions left (`u_select.block(records, None, h)`; the headline), on the early block
   (`u_select.block(records, "early", h)`: the starts of 2023 and before, less those within h sessions of 2023's last)
   and on the late block (`u_select.block(records, "late", h)`: the starts from 2024-01-02 with h sessions left).
   Nothing is chosen on any block; they are read apart so the menu can flag a plan whose difference changes sign
   between them (10.1 item 11). Each reading prints its own window count (10.2).
5. **No NQ from 2026-07-17** is on disk or read.
6. **The judged block's seal** (E-026). The registered builders read the bars and the atlas inside Stage 2's engine, so
   the run authorises those reads with `extended.reader.authorise_engine_read` before the engine runs, under the
   purposes on this line (the identities under `identity` and their own decision row):

   - **Judged-block reads:** `firm_scorecard`, `firm_ladder_beside`, `firm_gate_beside`

## 7. The cells and the runs

### 7.1 The corners and the references

- **References.** TS on P-16 and TS on P-14, as registered: they must reproduce the registered rows (9.1 item 1).
- **Corners.** For each of LU, DT, FP and QP, on each stream: the **strict corner** (every term of 5.2 at its strict
  end at once) and the **lenient corner** (every one at its lenient end). U-3's fees are $0 at both, labelled.

### 7.2 One at a time

On P-16 only, from the strict corner, each term with two ends flipped alone to its lenient end: DT's price, lag and
inactivity; FP's price, minimum days and fifth request; QP's price, minimum days and intraday peak. Lucid has one such
term, so its corners are its one-at-a-time reading.

### 7.3 The runs

| run | plan | stream | settings | kind |
|---|---|---|---|---|
| TS-16 | TS | P-16 | as registered | reference (identity) |
| TS-14 | TS | P-14 | as registered | reference (identity) |
| LU-16-s, LU-16-l | LU | P-16 | strict, lenient corner | corner |
| LU-14-s, LU-14-l | LU | P-14 | strict, lenient corner | corner |
| DT-16-s, DT-16-l | DT | P-16 | strict, lenient corner | corner |
| DT-14-s, DT-14-l | DT | P-14 | strict, lenient corner | corner |
| DT-16-price, DT-16-lag, DT-16-inact | DT | P-16 | strict, with that one term lenient | one at a time |
| FP-16-s, FP-16-l | FP | P-16 | strict, lenient corner | corner |
| FP-14-s, FP-14-l | FP | P-14 | strict, lenient corner | corner |
| FP-16-price, FP-16-days, FP-16-fifth | FP | P-16 | strict, with that one term lenient | one at a time |
| QP-16-s, QP-16-l | QP | P-16 | strict, lenient corner | corner |
| QP-14-s, QP-14-l | QP | P-14 | strict, lenient corner | corner |
| QP-16-price, QP-16-days, QP-16-peak | QP | P-16 | strict, with that one term lenient | one at a time |

That is **27 replays**: 2 references, 16 corners, 9 one at a time. Each runs both arms, every start, the long replay and
U1's exact-length runs.

### 7.4 Beside

- **The denial ladder** (10.1 item 7): 10, 25 and 50 % on TS-16 and on P-16's eight corners, verdict arm -- **27
  replays**, with Q-17's exact-length rule (its `EXACT_EVERY`).
- **The gate** (10.1 item 8): on the 16 corners, 500 paths, point and bound, at the stream's registered gate seed, with
  its zero-edge twin -- **16 gates**. TS's gates are the identities (9.1 item 1).

## 8. Parameters: fixed, described, read at both ends, dropped

"Described" means every value listed is run and read and the program chooses none; the operator chooses from the menu.
"Both ends" means a term the plan's pages leave open, read at the two ends section 5 fixes.

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| the plan | which firm's contract | **described** | TS, LU, DT, FP, QP | 2.1; E-023 (1) |
| trades | what is traded | fixed | P-16's registered trades (headline), P-14's (beside) | E-002, E-010 |
| state table | sizing by account state | fixed | each design's registered table, not re-solved for any plan | Stage 2 D-501, D-575 (1); G-6 |
| seats, budget, routing | accounts and purchases | fixed | five seats, five accounts in all; 20 evaluation purchases in 21 sessions; the strict one-position rule | 2.3; P-14's and P-16's registrations |
| resets | buying a reset | fixed | none | each design's own |
| the request rule | how much each payout asks | fixed | `min(0.5 B, $2,000)` cut to the plan's cap, remaining-balance rule and increment; none below its minimum | 2.3, 5.3 |
| the plan's verified terms | caps, splits, floors, gates, fees, allowances, lags, seats | fixed | the records' values | section 4; Appendix R |
| unread prices | evaluation prices not verified | **both ends** | FP $248 / $99; QP $175 / $69; DT on the grid, $250 / $25 at its ends | U-1, U-2 |
| unread fees | fees no page states | fixed | $0, labelled an upper bound | U-3 |
| conflicting minimum days | TradeDay's evaluation | **both ends** | FP 7 / 3; QP 7 / 5 trading days | U-4 |
| DT's lag | payout processing | **both ends** | 3 / 1 sessions | U-5 |
| unstated reaches | Lucid's live move; DT's inactivity accounts; FP's fifth request | **both ends** | 5.2 | U-6 |
| FP's scaling maximum | the funded ladder's top | fixed | 5 contracts | U-6 |
| QP's intraday peak | the floor inside a trade | **both ends** | the pessimistic / optimistic bound | U-9, 5.4 |
| moot terms | queues, the 10-day window, reset fees, FP's 50 % base, QP's cap | fixed (not read) | checked not to bind | U-7, 9.3 |
| request timing | when in the day | fixed | per plan: TS, DT, FP after 5:00 PM CT with the next session excluded; LU, QP at the close with none excluded | section 4; Stage 2 D-175 |
| arms | outcome shift | fixed | `verdict` the headline, `point` beside | CHARTER section 2 |
| denial, placement | firm discretion | fixed | 0 % and the placement off in the headline; the ladder beside | E-008; E-013 (1) |
| horizons, blocks | replay length, starts read | fixed | U1's; all, early and late per measure | Stage 2 D-620, D-621 (4)(b) |
| uncertainty | the interval on each paired reading | fixed | 10.2 | E-007 (e) |

**Dropped, and why.** Lucid's 50 % add-on, DayTraders' Lifetime billing, Topstep's other paths and sizes (2.1); a
"firm's maximum" request at QP, which no page states (5.3); any cross-firm portfolio (2.3; Stage 2's family 5 read it);
re-solving a table for a plan (G-6; a later reading); the price inside any bracket as a point estimate (U-1, U-2).

## 9. Before any reading: identities, oracles, mechanics

### 9.1 The identities, refusing (E-004, E-010)

1. **TS through this reading's runner** (A-1 with Topstep's contract, A-8, and A-9's `off` arm) reproduces, for P-16
   and P-14: U1's start rows (`vendor/stage2/results/user_journey.csv`, section `start`, configs `p16` and `p14`, both
   arms, every start, every column as E-010 compared them: money and the ratio to 1e-6; counts, days, dates and text
   exactly), with U1's checks of every run's payouts and fees against the engine's totals; and the registered gate paths
   (`vendor/stage2/results/rc_s150_all_gate_paths.csv` at seed 20261206 after P-16's trades' hash;
   `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv` at seed 20261131), every `zero_edge_decomposition.PATH_COLS`
   column, point and bound, all 500 paths, to 1e-6.
2. **Every adapter at its Topstep setting** (A-2 to A-7 with every switch at the vendored behaviour) reproduces item 1:
   at 4 starts and 4 paths in the suite (`slow`), and at every start and all 500 paths as the run's first stage.
3. **Lucid.** (a) The vendored joint engine reproduces U1's `p16_5+1` start rows (both arms, every start, as item 1):
   Stage 2's Lucid machinery as registered, in this snapshot. (b) This reading's runner with Lucid's contract (A-1, by
   `lucid_setup`) equals the vendored joint engine's one-firm run of `lucid_setup` at five seats
   (`hypo_hedge.run_joint`, `n_firms=1`; Stage 2 showed its one-firm Topstep run equal to P-16's single-engine records),
   start for start, every start, both arms, every column -- on P-16. P-14 has no joint setup on file; its Lucid runs
   rest on (b)'s composition.
4. **The trades are the base's.** Every trade any run's account takes is one of its design's registered offered trades.
5. **Off where off.** In TS no adapter switch fires; in each plan no other plan's rule fires; both counted and written.

Any failure stops the reading, and the failure protocol applies; nothing is rerun until it passes. E-010's negative
controls (the verdict rows against the point rows; a 2e-6 nudge) show the comparison is not vacuous.

### 9.2 Oracles (an output outside them is an engine error, never a finding)

- On every corner's zero-edge twin, the mean gross payouts per funded account do not exceed $2,000 beyond its Monte
  Carlo interval. Every plan's funded account starts $2,000 above its floor and is liquidated at the floor; daily loss
  limits, consistency gates, counts and ceilings only lower the bound.
- On every corner's zero-edge twin, the pass rate per evaluation does not exceed 2/5 beyond its interval (propsim
  D-02): every plan's evaluation is a $3,000 target over a $2,000 trailing floor, and its other rules only remove or
  delay passes, or raise the floor.
- Every request lies within its plan's bounds and every net is its plan's split of it, to 1e-9: DT's $50 increments and
  the $2,000 left; FP's $1,500; QP's tiered split; Lucid's $500 minimum.
- QP's floor at every close is at least the end-of-day trailing floor of the same gross path, and never above start.

### 9.3 The mechanics, printed first

Printed for each plan, stream and block before any paired outcome. They describe where a contract binds, not whether it
helps.

- the share of starts on which the plan differs from TS at all within 63, 126 and 252 sessions;
- the share of trades whose contracts differ from TS's, by account kind; the realised-to-intended risk in P-14's
  allowance-capped form (E-022 (1)); the trades stood aside (Stage 2 D-272);
- **where each plan binds:** DT -- daily-limit days, passes delayed by the Qualifying Days, eligible closes blocked by
  the 30 % rule, requests cut by the $2,000 left and the $50 increment, inactivity closures, signals lost to a paused
  account (G-12); FP -- passes delayed to the seventh day, closes blocked by the 45 % rule, sessions passed over after a
  request and their signals re-dealt or skipped, fifth-request endings, trades an uncapped ladder would size
  differently; QP -- floor rises from intraday peaks at both bounds, breaches at a raised floor, requests by split tier,
  accounts ended at $10,000; LU -- fifth payouts and household closures;
- **the checks that must be zero** (U-7): the peak hold queue; resets bought; DT activations later than ten days after
  a pass; FP requests above half the profit; QP requests above the reference's amount; purchases refused for cash (A-10's
  premise); and, once G-3's list is recorded, TradeDay trades open in a tier-1 window.

A plan identical to TS on every start is reported as "no effect on these trades", and nothing more is read for it.

## 10. The reading: the journey scorecard and the menu (CHARTER sections 2-3; E-008, E-014, E-015, E-023)

### 10.1 What is read

Every run of 7.3 (the one-at-a-time runs marked), on both arms (the verdict arm the headline) and every block of
section 6. The replay draws nothing.

1. **The scorecard.** P, S1 to S5c, S2, S3d, S6 and Q, as `USER_MILESTONES.md` defines them, and the frontier on P,
   S1, S3a and S5a across the plans' corners, per stream. S3c is compared across plans only within one trade stream
   (E-008's condition), where it is a contract's payouts per fee dollar.
2. **E-014's journey variables:** sessions and cash to the first pass; sessions and cash to the first payout; sessions
   to break-even (the first session cumulative net cash is at or above zero, daily), the share reaching it by months 1,
   2, 3, 6 and 12, and the share that later falls back below zero; the path's evenness (the share of months with a
   positive net change, the longest run of months without a payout, the spread of monthly net, the deepest fall of
   cumulative net after break-even, payouts per month, the largest single month's share of the year's payouts).
3. **Each measure as a distribution over start days** -- median, p10 and p90 -- with its uncertainty (10.2), and the
   start day's share of the variance across the plans (S6's form): how much of a user's result is the plan, and how
   much the day they start.
4. **Paired with TS, by month: who is helped, who is hurt.** For every measure of items 1 and 2, plan less TS: the
   per-start difference as a distribution (p10, p50, p90); the shares of starts on which the plan is better, equal and
   worse at months 1, 2, 3, 6, 9 and 12 (for the share ahead: ahead under the plan and not TS, under both, under
   neither, under TS and not the plan); the mean difference with 10.2's interval, its window count and its minimum
   detectable difference.
5. **Each plan's spread.** Its two corners side by side, and on P-16 its one-at-a-time runs: which unread term moves
   the plan's row, and by how much. A plan whose two corners lie on opposite sides of TS on P is flagged "**depends on
   its unread terms**". The flag is mechanical, not a line.
6. **What diverges** (each plan against TS): funded accounts activated and lost; evaluations bought; fees by kind;
   payouts' count and size; trades taken and their realised risk.
7. **E-007 (e)'s readings beside:** the **denial ladder** (10, 25, 50 %), drawn per start from seed **20261990** by
   Q-17's adapter (A-9) -- the engine's tier-3 model at every plan, one uniform price on each firm's discretion, since
   no firm's own review rate is known; P by month, mean net, CVaR10, P under a bankroll limit, the effective sample
   size. The placement on and the Focused Trader models are Topstep's programs: TS only, from Q-17's own reading, not
   rerun here.
8. **The long-run gate beside, on the corners:** growth on the required bankroll, the required bankroll, payouts a
   month and days to the first payout, paired with TS's registered gate paths (the same seeds, so the same day draws).
   It shows the trade-off between a user's first months and two-year growth. Nothing is a floor: nothing is carried.
9. **The price grid and the break-even price** (DT, FP, QP): every money measure and P at each price of U-2's grid,
   and at every listed price, by exact arithmetic (A-10) from the run. The arithmetic must reproduce the run at the
   bracket's other end (the one-at-a-time price run) on every start to 1e-6, refusing. Beside it, **the break-even
   price** against TS for P, S5a and the mean month-3 net: the price in $0 to $250 at which the plan's measure equals
   TS's (bisection on the exact arithmetic), or "none in range". Printed beside, never a pick.
10. **The evenness trade-off.** The plans' corners as points of "ahead" against each evenness measure, in E-015's menu
    form.
11. **The menu.** Each plan's strict and lenient rows: all starts the headline, the early and late blocks and the
    start years beside. Every row carries its labels: the upper bounds (U-3), the gaps that touch it (4.7), the moot
    checks' counts. **The stability flag:** a plan whose mean paired difference in P, or in any guarded measure, has
    opposite signs on the early and late blocks is flagged "not stable across blocks" (mechanical). **E-015's limits**
    are flags only, once the operator approves them; until then the menu is read without flags, and says so.
12. **Not modelled, and said so wherever this scorecard appears:** a user who stops when their own money runs out, the
    user's time, taxes.

### 10.2 The uncertainty on each paired reading (fixed now)

These are descriptions, not tests. Nothing here is compared with a critical value to decide anything. The method is
reading PP's (`prereg/DRAFT_F-P_payout_policy.md`, 9.2), so the two menus read alike.

1. **The window count.** For a reading at horizon h on a block, n_w is the number of non-overlapping h-start windows
   (consecutive start days in order, from the block's first start; a last incomplete window dropped), printed with every
   reading.
2. **The interval.** A two-sided 90 % interval from a Student-t on the n_w window means, with n_w - 1 degrees of
   freedom, **printed only when n_w is at least 4**. Below 4 the reading prints "too few independent windows for an
   interval" and gives only item 3.
3. **The window sign count.** In how many of the n_w windows the plan's mean is above, equal to and below TS's.
   Distribution-free, always printed.
4. **The effective sample size.** From the Bartlett long-run variance of the per-start difference with lag window h
   (audit B's form; `extended.user_measures.n_eff_bartlett`), beside.
5. **The minimum detectable difference** of item 2's interval at 80 % power: (t(0.95; n_w - 1) + t(0.80; n_w - 1))
   times the window means' standard error, printed beside each mean and before it.
6. **A series zero on every window** prints "identical on these trades", with no interval and no MDD.
7. **The interval's honesty, beside.** Its coverage on synthetic series of known zero mean, at each n_w the reading
   uses (seed **20261991**; 20,000 series per setting): a symmetric Gaussian; the red team's skewed, lumpy shapes (its
   Appendix A model on reading PP: g = 0.01; p in {0.05, 0.10, 0.20}; s in {0.0025, 0.005, 0.01}; window means +g with
   probability 1 - p and -g(1 - p)/p with probability p, plus N(0, s^2) noise, and their mirror); and a persistent
   version (the rare window's sign repeated in the next with probability one half).
8. **Beside, when Q-16 is merged.** Q-16's calibrated paired comparison, one-sided at 0.05, for P and the guarded
   measures, its draws (if any) from seed **20261993**, labelled with its name and commit. The reading does not wait
   for it.

## 11. What the reading delivers, and what each outcome means

- **It delivers** the menu of section 10: what P-16's and P-14's registered trades and tables do to a user's journey on
  each of five plans' verified contracts, with every unread term's spread.
- **It does not deliver** a carried design, a registration id, a confirmation, a claim at a level, or a recommendation
  of a firm (E-023 (1)).
- **No outcome passes or fails.** What follows from each, fixed now:
  - an identity fails (9.1): the reading stops, the failure protocol applies;
  - an oracle is breached (9.2): an engine error; the reading stops;
  - a moot check is nonzero (9.3): the plan's rows carry the count; nothing is resolved here;
  - a plan's corners lie on one side of TS on P: the menu shows the plan above (or below) TS on these trades at both
    ends of its unread terms;
  - a plan's corners straddle TS: the menu flags it "depends on its unread terms"; the operator's read of a price (DT),
    or a written question to the firm, is what would settle it. **No run is repeated to settle it**: a re-read is a new
    declaration citing this one.
- **The operator's choice.** Recorded in its own decision row, citing this reading's result files (E-015: limits
  first, then the best inside them). Buying a plan is a purchase, the operator's.
- **No confirmation.** Nothing is carried, so NQ from 2026-07-17 is not touched.
- **The binding.** The blocks read here are recorded as read for firm contracts on P-14 and P-16, all of them. A later
  firm reading names this one, states what changed, and reads no block of it as fresh.

## 12. Seeds, fixed now and checked

| seed | status | what it draws |
|---|---|---|
| 20261990 | in use | the denial ladder's per-start path seeds (`lockstep.child_seed(20261990, 0, start_day)`), common to every plan's ladder run (10.1 item 7) |
| 20261991 | in use | 10.2 item 7's synthetic coverage series, and T-9 |
| 20261992 | in use | the build's toy campaigns (T-1 to T-7, T-10) |
| 20261993 | in use | Q-16's paired comparison beside (10.2 item 8), if it draws |
| 20261994 | reserved, unused | -- |
| 20261995 | reserved, unused | -- |
| 20261996 | reserved, unused | -- |
| 20261997 | reserved, unused | -- |
| 20261998 | retired, found in use | the red team's scratch seed in `docs/reviews/DRAFT_F-P_payout_policy_2026-11-16.md` (its `skew_null_pass.py`) |
| 20261999 | retired, found in use | the red team's scratch seed in the same review (its `rng`) |

**The check, 2026-11-16.** A word-bounded search of the worktree, the vendored snapshot and its results included
(`grep -rIow --exclude-dir=.git -E "2026199[0-9]" .`), and the same search on every branch and remote branch (`git grep`
per ref), find the block only in that review, which uses 20261998 and 20261999 as scratch seeds. **Those two are
retired here and never used.** `tests/test_rd_firms_draft.py` repeats the check on every run: no seed in use or
reserved appears in any other declaration or anywhere in the vendored snapshot.

**Inherited, and used only as their owners registered them:**

- P-16's gate seed 20261206 and P-14's gate seed 20261131, for the gates beside (paired with the registered paths);
- U1's replay seeds, as U1 passes them (a replay draws nothing).

## 13. Counting and the budget

1. **No program family number and no level** (E-023 (1)). The next numbered family's k is what it would be without
   this file.
2. **Counted under this reading's row:** 27 replays (25 new: 16 corners and 9 one at a time; 2 references, counted as
   identities); 27 denial-ladder replays and 16 gates beside, labelled; every block read, recorded as read for firm
   contracts (11).
3. **Nothing is selected by the program.** The operator's menu choice is a choice among described readings, recorded in
   its own row with the menu it was made from.

## 14. The build: adapters, identities and tests

### 14.1 The adapters

Section 4.6's A-1 to A-10, in `extended/`, each with its Topstep setting. The firm runner is the U1 replay
(`customer_slices.replay` through U1's own task) with A-1's arguments; the gate is A-8; the ladder is A-9.

### 14.2 The rules in code

Every value comes from its record by a loader that refuses an entry not `verified` (`config/rules_extended.yaml`,
under E-020; Stage 2's ledger and the Lucid ledger through their own loaders), parsing a value stated in text fail-loud,
as `propedge.contract.lucid` parses Lucid's. The values of section 5 come from one table of named constants in the
adapter, each citing its line of 5.2. A test fails on any literal of a rule value in the adapters outside comments and
that table.

### 14.3 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 (this draft's commit) | `tests/test_rd_firms_draft.py`: Appendix R cites every key with its record's status; every open term of the three new firms' records is cited and read in section 5; section 12 holds the brief's block, its seeds in use and reserved appear in no other declaration and nowhere in the vendored snapshot, and the retired ones are found elsewhere; the `Judged-block reads:` purposes parse and choose nothing; and, as a strict expected failure until the lead's fix (16 item 1), that the reader admits an RD- file |
| T-1 | every adapter at its Topstep setting equals the vendored class bit for bit on toy campaigns (seed 20261992): every day's balance, floor, request, payout, cash and recorded `eligible` |
| T-2 | DT: the evaluation's two Qualifying Days (a day over the 50 % share does not count), the soft daily limit, the inactivity closure at a 21-session window; the Pro account's eight Qualifying Days with the request day excluded, the 30 % cycle rule, the $2,600 gate, the $2,000 left, the $50 rounding, and a payout leaving the floor at start (the engine's move a no-op); the recurring $5 fee's due sessions |
| T-3 | FP: the 45 % rule on gross profit; the session after a request untraded and passed over, its signal re-dealt to the longest-waiting other account; the fifth request at both ends; the ladder and its cap |
| T-4 | QP: the gross-profit floor on the page's own example (a $50,500 balance with the floor at $48,500; after a $500 payout, $50,000 with the floor still at $48,500); the tiered split on its example ($6,000 of profit and a $3,000 payout: $1,600 plus $500); the $10,000 ceiling; 5.4's two bounds on hand-built trades with known outcomes at each R |
| T-5 | TradeDay's minimum days at 3, 5 and 7 |
| T-6 | A-10: on toy campaigns at two prices the records are identical and the cash differs exactly by the arithmetic; the break-even bisection on a known case |
| T-7 | 9.2's oracles on toy campaigns |
| T-8 (`slow`) | 9.1 items 1 to 3 at 4 starts and 4 paths; the full run is the run's first stage (heavy) |
| T-9 | 10.2: the window count, the interval from 4 windows only, the sign count, the zero-series rule, the coverage on one small fixed setting (seed 20261991) |
| T-10 | A-8 equals the vendored gate with no new keyword given (synthetic, as Q-47's identity) and at Topstep's values |
| T-11 | 14.2: the loader refuses an entry not verified; no rule literal outside the constants table |

## 15. Outputs and the run

- **Files:**
  - `results/fc_reading.csv`, sections `identity`, `oracle`, `mechanics`, `scorecard`, `paired`, `diverge`, `grid`,
    `ladder`, `coverage`;
  - `results/fc_gate.csv`, the gate rows;
  - `results/fc_menu.csv`, the menu with its flags and labels.

  Each written with its sidecar manifest through `extended.results.write_result`, carrying: `prereg_id`, the reading's
  id (unnumbered) and its pinning row; the run counts (27 replays; 25 new; 2 references; 27 ladder replays; 16 gates);
  every seed, the retired ones included; every parameter, section 5's readings and their labels; each plan's record
  entries with their dates read; the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`; `exploratory=False`, since
  nothing in it is chosen after a look. Every cell is still labelled "described, not carried".
- **The run:**
  - **where.** Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
    its end;
  - **weight: heavy.** Every start on two arms for 27 replays, 27 ladder replays and 16 gates: several hours at two
    workers; memory near the U1 identity's and Q-17's (E-010, E-024);
  - **order.** The identities first (9.1); any failure stops the run. Then the oracles, the mechanics (9.3), then the
    reading;
  - **a restart.** A run aborted or restarted is recorded by the lead with its log, and only the first complete run is
    read.
- **Waits:** the pinning row; 16's items 1 and 2; A-1 to A-10 built with their tests; Q-47's 500-path identities
  (E-028 (3)) before A-8 runs; Q-17's adapter's identity (E-024) before A-9 runs. It does not wait for Q-16 (10.2 item
  8 is beside), for E-015's limits (flags only), or for the operator's price read (U-2).

## 16. Open before the pin

**The lead's:**

1. **The reader admits only `prereg/F-` files.** `extended/reader.py`'s `DECLARATION_PATH` and `PIN` accept a
   judged-block read's declaration only as `prereg/F-NN_*.md`, so a pinned `prereg/RD-nn_*.md` cannot authorise the U1
   replay's engine reads (section 6 item 6). E-025 (1) widened the hash test, not the reader. T-0 keeps it as a strict
   expected failure until it is widened.
2. **The rules-verifier's readings for DayTraders and TradeDay, recorded under a row before the pin.** The survey
   reports these on the firms' official pages (E-009), but nothing of it is usable until recorded:
   - R-1, permitted products: NQ and MNQ and how contracts are counted (DayTraders 17704134; TradeDay 103000008862,
     103000008825);
   - R-2, session hours and the latest flat time -- the designs are flat by 15:10 CT (DayTraders 17704089; TradeDay's
     hours page);
   - R-3, news: TradeDay's tier-1 list and its auto-liquidation windows, and "bracketing data releases" (103000081072);
     DayTraders' "news allowed";
   - R-4, conduct: hedging (DayTraders 17704076; TradeDay), Martingale (17704073), automation (17704087; 103000085101;
     hand entry unaffected), trade-count and scalping limits, DayTraders' Terms clause on outsized positions;
   - R-5, commissions (DayTraders 17704134; TradeDay's simulated commission).

   **If any of them states a rule section 4 does not represent, that plan's cells are not run under this declaration**
   (a redraft names it).
3. **E-020 (1)'s crawl-clause reading** stands for DayTraders and TradeDay. If the lead ever reads those clauses as
   E-009 read The Futures Desk's, their entries are struck and their cells dropped.
4. **A-8** is new code of Q-47's pattern; Q-47's own 500-path identities come first.
5. **With reading PP.** The same uncertainty method by design (10.2); both readings pair against the same references;
   neither reads the other's cells.
6. **The name at the pin** (`prereg/RD-nn_<slug>.md`, E-025 (1)).

**The operator's:**

1. **DayTraders' price**, optional: a browser read of its EOD 50K evaluation price at checkout, Monthly billing
   (`docs/OPERATOR_SETUP.md`; a read, no purchase). U-2's grid covers it either way.
2. **The levels of E-015's limits.** Approval is pending; they are flags only and never block.
3. **After the run:** the choice from the menu, if any; any purchase is the operator's.

## 17. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*

---

## Appendix R -- every rule key this reading leans on, with its record and status

Sources: `record` is this repository's `config/rules_extended.yaml` (E-020); `stage2` is Stage 2's vendored
`config/rules.yaml`; `lucid` is the vendored Lucid ledger (`vendor/stage2/vendor/propfirms/firms/lucid-trading/
rules.yaml`), read through `propedge.contract.lucid`. `tests/test_rd_firms_draft.py` checks every row against its source.

| key | source | status | used for |
|---|---|---|---|
| `combine_profit_target` | stage2 | verified | TS evaluation target |
| `combine_mll` | stage2 | verified | TS evaluation drawdown |
| `combine_mll_lock_at` | stage2 | verified | TS evaluation lock |
| `combine_consistency_max_day_frac` | stage2 | verified | TS evaluation consistency |
| `combine_position_size_limit` | stage2 | verified | TS evaluation allowance |
| `xfa_mll_start` | stage2 | verified | TS funded floor |
| `xfa_lock_at` | stage2 | verified | TS funded lock |
| `xfa_std_winning_days` | stage2 | verified | TS payout gate |
| `xfa_std_winning_day_min` | stage2 | verified | TS payout gate |
| `xfa_std_cap` | stage2 | verified | TS cap; the declared request rule's $2,000 |
| `payout_max_frac_of_balance` | stage2 | verified | TS request; the declared request rule's half |
| `payout_min` | stage2 | verified | TS minimum |
| `profit_split` | stage2 | verified | TS split |
| `require_profit_since_payout` | stage2 | verified | TS gate after the first payout |
| `subscription_fee` | stage2 | verified | TS evaluation price |
| `billing_days` | stage2 | verified | TS billing; DT's 30-day rebill translated to 21 sessions |
| `billing_period_calendar_days` | stage2 | verified | the 30-calendar-day basis of that translation |
| `activation_fee` | stage2 | verified | TS activation |
| `payout_fee` | stage2 | verified | TS payout fee (Aeropay) |
| `payout_lag_days_aeropay` | stage2 | verified | TS lag; DT's lag bracket's slow end |
| `max_active_funded_accounts` | stage2 | verified | TS seats |
| `funded_scaling_plan` | stage2 | verified | TS funded allowance |
| `scaling_tier_after_payout` | stage2 | verified | the tier follows the balance after a payout |
| `trading_hours` | stage2 | verified | the designs' 15:10 CT flatten |
| `permitted_products` | stage2 | verified | NQ at Topstep |
| `cross_account_opposite_positions` | stage2 | verified | tier 1 |
| `responsible_trading_program` | stage2 | verified | TS only, off in the headline |
| `focused_trader_program` | stage2 | verified | TS only, beside from Q-17 |
| `eval_profit_target` | lucid | verified | LU evaluation target |
| `eval_drawdown_amount` | lucid | verified | LU evaluation drawdown |
| `eval_drawdown_type` | lucid | verified | LU end-of-day trailing |
| `eval_drawdown_lock` | lucid | verified | LU lock at start + $100 |
| `eval_daily_loss_limit` | lucid | verified | LU daily limit off at checkout |
| `eval_consistency_rule` | lucid | verified | LU 40 % |
| `eval_min_days` | lucid | verified | LU three days |
| `eval_position_limit` | lucid | verified | LU 40 micros |
| `eval_fee` | lucid | verified | LU price |
| `eval_reset_fee` | lucid | verified | LU reset (none bought) |
| `eval_count_limit` | lucid | verified | LU evaluations cap |
| `funded_drawdown_amount` | lucid | verified | LU funded floor |
| `funded_drawdown_type` | lucid | verified | LU funded end-of-day trailing |
| `funded_position_limit` | lucid | verified | LU funded ladder |
| `funded_monthly_fee` | lucid | unverified_human_input_required | LU's open fee (U-3) |
| `payout_min` | lucid | verified | LU minimum |
| `payout_cap` | lucid | verified | LU request |
| `payout_frequency_gate` | lucid | verified | LU gate, five payouts |
| `payout_split` | lucid | verified | LU split |
| `payout_processing_days` | lucid | verified | LU lag |
| `payout_fee` | lucid | unverified_human_input_required | LU's open fee (U-3) |
| `payout_balance_consequence` | lucid | verified | LU floor at a request |
| `max_accounts` | lucid | verified | LU seats; the household rule's quote |
| `prohibited_conduct` | lucid | verified | tier 1 at Lucid |
| `permitted_products` | lucid | verified | NQ at Lucid |
| `news_trading_terms` | lucid | verified | news at Lucid |
| `lucid.flex50k.funded_monthly_fee` | record | unverified | LU's open fee, re-read (U-3) |
| `lucid.flex50k.payout_fee` | record | unstated | LU's open fee, re-read (U-3) |
| `daytraders.automated_retrieval_terms` | record | verified | E-020 (1)'s crawl-clause reading |
| `daytraders.eod50k.eval_fee` | record | unverified | DT price (U-2) |
| `daytraders.eod50k.eval_billing_basis` | record | verified | DT Monthly billing |
| `daytraders.eod50k.eval_reset_fee` | record | verified | DT no resets |
| `daytraders.eod50k.eval_profit_target` | record | verified | DT evaluation target |
| `daytraders.eod50k.eval_drawdown_amount` | record | verified | DT evaluation drawdown |
| `daytraders.eod50k.eval_drawdown_type` | record | verified | DT end-of-day trailing |
| `daytraders.eod50k.eval_drawdown_lock` | record | verified | DT evaluation lock |
| `daytraders.eod50k.eval_daily_loss_limit` | record | verified | DT evaluation daily limit (A-2) |
| `daytraders.eod50k.eval_consistency_rule` | record | verified | DT 50 % |
| `daytraders.eod50k.eval_position_limit` | record | verified | DT evaluation allowance |
| `daytraders.eod50k.eval_min_days` | record | verified | DT Qualifying Days (A-2) |
| `daytraders.eod50k.activation_fee` | record | verified | DT activation |
| `daytraders.eod50k.funded_monthly_fee` | record | verified | DT recurring Pro fee (A-10) |
| `daytraders.eod50k.funded_drawdown_amount` | record | verified | DT funded floor |
| `daytraders.eod50k.funded_drawdown_type` | record | verified | DT funded end-of-day trailing |
| `daytraders.eod50k.funded_drawdown_lock` | record | verified | DT funded lock |
| `daytraders.eod50k.payout_balance_consequence` | record | verified | DT request gate and balance left (A-3) |
| `daytraders.eod50k.funded_daily_loss_limit` | record | verified | DT funded daily limit (A-3) |
| `daytraders.eod50k.funded_consistency_rule` | record | verified | DT 30 % (A-3) |
| `daytraders.eod50k.funded_position_limit` | record | verified | DT funded allowance |
| `daytraders.eod50k.payout_frequency_gate` | record | verified | DT eight Qualifying Days (A-3) |
| `daytraders.eod50k.payout_split` | record | verified | DT split |
| `daytraders.eod50k.payout_cap` | record | verified | DT cap |
| `daytraders.eod50k.payout_min` | record | verified | DT minimum and increment |
| `daytraders.eod50k.payout_count_limit` | record | unstated | DT count (U-10) |
| `daytraders.eod50k.payout_fee` | record | unstated | DT payout fee (U-3) |
| `daytraders.eod50k.payout_processing_days` | record | unstated | DT lag (U-5) |
| `daytraders.max_funded_accounts` | record | verified | DT seats; the queue (U-7) |
| `daytraders.inactivity_rule` | record | verified | DT inactivity (A-2, A-3; U-6) |
| `tradeday.automated_retrieval_terms` | record | verified | E-020 (1)'s crawl-clause reading |
| `tradeday.eval_billing_basis` | record | verified | TradeDay one-time fees |
| `tradeday.eval_reset_fee` | record | unverified | TradeDay resets (U-7) |
| `tradeday.eval_profit_target` | record | verified | TradeDay evaluation target |
| `tradeday.eval_drawdown_amount` | record | verified | TradeDay evaluation drawdown |
| `tradeday.eval_drawdown_type` | record | verified | TradeDay end-of-day trailing |
| `tradeday.eval_drawdown_lock` | record | verified | TradeDay evaluation lock |
| `tradeday.eval_daily_loss_limit` | record | verified | TradeDay none |
| `tradeday.eval_position_limit` | record | verified | TradeDay evaluation allowance |
| `tradeday.activation_fee` | record | verified | TradeDay activation |
| `tradeday.funded_monthly_fee` | record | verified | TradeDay Funded Sim fees |
| `tradeday.funded_daily_loss_limit` | record | verified | TradeDay none; the price-limit rule (G-2) |
| `tradeday.payout_min` | record | verified | TradeDay minimum |
| `tradeday.max_funded_accounts` | record | verified | TradeDay seats; the queue (U-7) |
| `tradeday.inactivity_rule` | record | verified | TradeDay dormancy (G-10) |
| `tradeday.fastpass_eod50k.eval_fee` | record | unverified | FP price (U-1) |
| `tradeday.fastpass_eod50k.eval_consistency_rule` | record | verified | FP 45 % |
| `tradeday.fastpass_eod50k.eval_min_days` | record | unverified | FP minimum days (U-4) |
| `tradeday.fastpass_eod50k.funded_drawdown_amount` | record | verified | FP funded floor |
| `tradeday.fastpass_eod50k.funded_drawdown_type` | record | verified | FP funded end-of-day trailing |
| `tradeday.fastpass_eod50k.funded_drawdown_lock` | record | verified | FP funded lock |
| `tradeday.fastpass_eod50k.payout_balance_consequence` | record | verified | FP floor at the first request |
| `tradeday.fastpass_eod50k.funded_consistency_rule` | record | verified | FP 45 % of gross (A-5) |
| `tradeday.fastpass_eod50k.funded_position_limit` | record | verified | FP funded ladder (U-6) |
| `tradeday.fastpass_eod50k.payout_frequency_gate` | record | verified | FP gate; the untraded session (A-5) |
| `tradeday.fastpass_eod50k.payout_split` | record | verified | FP split |
| `tradeday.fastpass_eod50k.payout_cap` | record | verified | FP cap |
| `tradeday.fastpass_eod50k.payout_cap_share_base` | record | unverified | FP 50 % base (U-7) |
| `tradeday.fastpass_eod50k.payout_count_limit` | record | verified | FP fifth request (A-5; U-6) |
| `tradeday.fastpass_eod50k.payout_fee` | record | unstated | FP payout fee (U-3) |
| `tradeday.fastpass_eod50k.payout_processing_days` | record | verified | FP lag |
| `tradeday.quickpay_eod50k.eval_fee` | record | unverified | QP price (U-1) |
| `tradeday.quickpay_eod50k.eval_consistency_rule` | record | verified | QP 30 % |
| `tradeday.quickpay_eod50k.eval_min_days` | record | unverified | QP minimum days (U-4) |
| `tradeday.quickpay_eod50k.funded_drawdown_amount` | record | verified | QP funded floor |
| `tradeday.quickpay_eod50k.funded_drawdown_type` | record | verified | QP intraday trailing (A-7; U-9) |
| `tradeday.quickpay_eod50k.funded_drawdown_lock` | record | verified | QP freeze at start |
| `tradeday.quickpay_eod50k.payout_balance_consequence` | record | verified | QP floor on gross profit (A-7) |
| `tradeday.quickpay_eod50k.funded_consistency_rule` | record | verified | QP none |
| `tradeday.quickpay_eod50k.funded_position_limit` | record | verified | QP funded allowance |
| `tradeday.quickpay_eod50k.payout_frequency_gate` | record | verified | QP eligibility (A-7) |
| `tradeday.quickpay_eod50k.payout_split` | record | verified | QP tiered split (A-7) |
| `tradeday.quickpay_eod50k.payout_cap` | record | unstated | QP cap (U-7) |
| `tradeday.quickpay_eod50k.funded_sim_profit_ceiling` | record | verified | QP $10,000 ceiling (A-7) |
| `tradeday.quickpay_eod50k.payout_count_limit` | record | unstated | QP count (U-10) |
| `tradeday.quickpay_eod50k.payout_fee` | record | verified | QP payout fee |
| `tradeday.quickpay_eod50k.payout_processing_days` | record | verified | QP lag |
