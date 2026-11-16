# DRAFT: other firms' contracts on the registered trades (reading FC) -- a described reading, unnumbered, not declared

**Status: DRAFT, third version, 2026-11-16 (TASK_QUEUE Q-91, E-058).** Written under the operator's ruling **E-023
(1)** (`CHARTER.md` section 3), from the rules record of E-020 and Q-59 (`config/rules_extended.yaml`,
`docs/RULES_CURRENCY.md`) and Stage 2's verified ledgers, in the form reading PP's draft takes
(`prereg/DRAFT_F-P_payout_policy.md`, E-025). The first version (Q-54) was merged under E-038, the second (Q-54b, on
Q-59's 28 entries: the cost rule, the tier-1 count, the two conduct counts, the written questions) under E-045. This
version answers the red team's first read (Q-88, `docs/reviews/DRAFT_RD_firms_2026-11-16.md`): every remedy adopted as
the review states it (E-058). It carries one edit on the red team's re-read (Q-88b,
`docs/reviews/DRAFT_RD_firms_v3_2026-11-16.md`: pinnable after it; Q-91b, E-067), listed after the table below.

**What changed from the second version, finding by finding, and what each change does to what the reading can show
(E-051).**

| finding | the second version | this version | where | effect on what the reading can show |
|---|---|---|---|---|
| M1 | the tables' inputs at DT, FP and QP unsaid | `win_days`, `since_pay`, `request_day_next` and the `Rules` winning-day fields declared per plan; an evaluation at target with days owed declared per plan; tested | 4.9, 4.6, G-6, T-2..T-5, T-14 | each plan's row is now one defined design; the held reading (4) and the day-logging micro make DT, FP and QP read the table's one-day-short and smallest sizes more often than a free lookup would -- printed (9.3), never tuned |
| M2 | DT at the dearer of its listed and Topstep's figure, called conservative | the fee basis a two-ended term: strict, the listed figures plus exchange and NFA fees by Topstep's verified decomposition (MNQ $1.74, NQ $6.76); lenient, the listed figures as all-in ($1.02, $3.98); `DT-16-fees` added; "direction unknown" corrected; E-045's adoption withdrawn | 4.8, 5.2, 7.2, G-5, 16 | DT's strict corner is dearer by up to $2.78 a mini and $0.52 a micro round turn: DT's two corners lie further apart, so "above TS at both corners" is harder for DT to show |
| M3 | QP read only under the reference's request at every close | a second declared request reading, the reference's cadence (`QP-16-req`), run beside and called neither end; every QP row labelled with its request rule; G-10 counted at QP | 2.3, 5.6, 7.2, 9.3, 10.1 | QP's row is shown under two request habits; where they disagree the menu says QP "depends on its request rule" instead of giving one row |
| M4 | the tier-1 bracket's lenient end the walked outcome | the lenient end the trade's target less a tick with the flatten's two-tick cost; the walked outcome read beside as "no liquidation", neither end | 5.5, 7.2, U-11 | the bracket is wider on FOMC-minutes days; with two more conditional runs (four in all) |
| M5 | the 90 % interval on adjacent h-start windows | windows separated by h starts (every other window); the honesty check rebuilt on overlapping per-start h-session sums; any reading below 0.88 coverage at its n_w labelled | 10.2 | about half as many windows: wider intervals and minimum detectable differences, and more readings printed as "too few independent windows" (month 12 and the late block mostly); the sign count stays |
| m1 | Q-16's one-sided 0.05 comparison beside | dropped: a described reading has no level | 10.2 | no 0.05 calls on the menu |
| m2 | "only the first complete run is read" | any rerun under a purpose names its row with `repeat=`; the identity stage runs from `identity/*.py` under its own row | 6, 9.1, 15 | none |
| m3 | the reader, the calendar, A-8 and the gate's owed identities stale | corrected: the reader admits RD- files (E-041); the FOMC-minutes calendar pinned (E-050); A-8 built (E-049); the gate waits for Q-80 | 4.6, 5.5, 15, 16 | none |
| m4 | A-9's waits missing | A-9 waits for Q-76 and takes the ladder's seed by keyword | 4.6, 15 | none |
| m5 | A-11 in the gate unsaid | A-11 off in the gate (its blocks carry no date), the rows labelled | 4.6, 10.1 | the gate beside does not show the tier-1 term |
| m6 | U-9's strict peak at the trade's own target | the strict peak at the next menu R above the largest won, less a tick; the optimistic peak at least a profitable flatten's exit; the walk's stop-first convention named | 5.4 | QP's peak bracket narrower (its strict end less harsh) |
| m7 | corners read as bounds | "at both declared corners"; the one-at-a-time runs read as each term's direction on P-16; the monotone terms named | 5.1, 11 | no row is called bounded in a term that is not monotone |
| m8 | Lucid's struck $165 unread | printed by A-10's arithmetic beside; the coupon's basis said | 10.1, 4.2 | LU gains a price grid point |
| m9 | the count's definitions loose | open at the window's start at any offered R; the bar convention; the BLS name match; A-11 on evaluations and Funded Sim; A-11 in 9.1 item 2 | 5.5, 9.1 | none |
| m10 | QP's ceiling at one end | two ends: the balance not credited / withdrawn at the ceiling's close; `QP-16-ceil` added | 5.2, 7.2, A-7 | QP's corners further apart where the ceiling binds |
| m11 | martingale counted per account | per account and across the user's accounts in time order, in micro-equivalents | 9.3 | more steps may show |
| m12 | A-4's "trading days" | days with at least one executed trade | A-4 | none |
| notes 1-8 | -- | readings: 5.3 at FP; the early-close zero check; DT's daily limit sizes trades; family 5's closure in 3; U-5's slow end in the written question; the in-sample choice in 11; the pin's name; DT's inactivity rolling over 30 calendar days | 5.3, 9.3, 2.3, 3, 16, 11, 15, 4.6 | DT's inactivity exact in the replay, translated in the gate |

**Runs, after these changes:** 30 replays (2 references, 16 corners, 12 one at a time), or 34 if P-16 has a trade open
in a TradeDay tier-1 window (5.5); 27 denial-ladder replays and 16 gates beside.

**The re-read's edit (Q-88b's five minors and three notes, Q-91b), and what each does to what the reading can show.**

| item | the third version | the edit | where | effect |
|---|---|---|---|---|
| n1 | A-5 "asserts" that the table's request-day cells sit the post-request session out | the premise is false (the solve only leaves the request day out of the winning-day count, `state_policy.py` 1017; the re-read found many reachable request-day leaves that trade); A-5 **forces** the session untraded wherever its cell would trade and passes the signal over; those sessions counted; T-3 covers a trading cell | A-5, 9.3, T-3 | Fast Pass sits out sessions the table would trade, as its page requires; the count shows how often |
| n2 | A-9's two keywords attributed to Q-76 | Q-76 (E-059) gives the class keyword only; the `household_closure` route (Lucid's lenient reach) and the ladder's seed base are **A-9's own** keywords (to be built generic as Q-100), each with U1's start-row identity at its default | A-9, 15, 16, T-15 | none |
| n3 | the day-logging micro could take every routed signal | **at most one trade a session** at the day-logging micro (`max_trades` 1) | 4.9, T-5 | no signals diverted from other accounts by a day-logging evaluation |
| n4 | DayTraders' fee basis in the monotone list | moved to the declared-corner list: a per-trade cost moves every trade's net, so the bands, the $200 days, passes and breaches -- monotone per trade, not per start | 5.1 | DT's corners are not called bounds in this term |
| n5 | the ceiling's whole-balance withdrawal against 9.3's zero check and U-7's moot cap | that one request exempted from both, Quick Pay's unstated cap read as none there by U-10, no request below $250 | 5.1, 5.2, 9.3 | the zero check stays a real check |
| note A | the tier-1 lenient end at the target less a tick | read: a walked target fills only when traded through, so the price at the window's start can equal the target; the end is a tick short of the best -- immaterial, kept | 5.5 | none |
| note B | Quick Pay's ceiling in the declared-corner list | read: monotone per start (both ends end the account at the same close on the same path; the lenient end only adds cash) -- moved to the monotone list | 5.1 | QP's corners are bounds in this term |
| note C | the verdict arm's shift on liquidated trades unsaid | stated: a trade booked by the tier-1 liquidation takes, on the verdict arm, the same per-R shift its R's outcomes take, whichever reading books it | 5.5 | the three tier-1 readings differ by their booking alone on both arms |
| -- | 4.9's "held" bullet broken across a line | joined | 4.9 | none |

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
| runs | 30 replays (2 references that must reproduce registered rows, 16 corner runs, 12 one-at-a-time runs), or 34 if P-16 has a trade open in a TradeDay tier-1 window (5.5); 27 denial-ladder replays beside, 16 gates beside (section 7) |
| unread terms | each read by a rule fixed in section 5; prices at both ends of their listed bracket, or on a declared grid where none is listed |
| seeds | from 20261990 to 20261999: three in use, five reserved, two retired because found in use elsewhere (section 12) |
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
  budget (at most 20 evaluation purchases in 21 sessions, P-14's), and its sizing rule's mode, headroom, stand-aside
  and room cap. **Only the plan's allowances, its per-trade costs (4.8) and the inputs its accounts hand the table
  (4.9) replace Topstep's**, as Stage 2's `lucid_setup` replaces the allowances for Lucid (Stage 2 D-575). At
  DayTraders the soft daily limit sizes trades too: the engine hands the draw the smaller of the cushion and the day's
  remaining limit as its room (`lockstep.py` 452-455, 706-708), so the $1,250 limit caps a trade's size where it is the
  nearer barrier (9.3 shows where).
- **The seats.** Five; at most five accounts of every kind together (evaluations, funded accounts and passes waiting),
  each design's own `max_total_accounts`. That is inside every plan's caps (section 4). With the total at or below the
  funded cap a pass never waits for a seat (the engine's rule, `lockstep.simulate_lockstep_path`'s
  `max_total_accounts`), so no plan's hold queue is ever reached -- checked (9.3).
- **No resets.** Neither design buys a reset; a failed evaluation is replaced by a new purchase.
- **The payout request rule (declared; P-14's and P-16's, carried to every plan).** At every close at which the plan's
  own rules make the account eligible, request **the smaller of half the balance above start and $2,000** -- the
  reference's amount, Topstep's `payout_max_frac_of_balance` and `xfa_std_cap` -- **cut to the plan's own per-request
  cap and its remaining-balance rule, rounded down to the plan's increment; no request below the plan's minimum.** At
  TS, LU and DT this is the plan's own maximum, and at FP it is under the profit reading of its 50 % base (5.3); at QP,
  whose pages state no per-request maximum, it is the reference's amount. It is a declared choice: the payout lever
  itself is reading PP's subject, not this one's. **At Quick Pay a second request reading is run beside** (5.6): the
  same amount at the reference's cadence -- because at QP, eligible at every close over a floor frozen at start, the
  every-close rule drains the cushion, and QP's row would otherwise read the request habit rather than the contract
  (the red team's M3).
- **Hand entry**, at least five minutes from alert to order (E-008). One user's own accounts at one firm: each plan is
  read alone, never beside another firm (Stage 2 read Lucid beside Topstep, section 3).
- **Conduct.** Tier 1 untouched. Tier 2: Topstep's Responsible Trading Program and Focused Trader Program are Topstep's
  own -- at TS exactly as in its registered rows (the placement off in the headline); no other plan's discretionary
  program is modelled, and no conduct model runs at LU, DT, FP or QP (as Stage 2 runs Lucid, `conduct=None`). Tier 3:
  the payout-denial ladder at every plan (10.1 item 7). The other plans' recorded conduct rules (hedging, copying,
  coordinated trading, automation, high-frequency trading, martingale, trade counts, order splitting) are read against
  the designs in 4.3 and 4.4; the two a design's trades could meet on their words are counted (9.3).

## 3. Prior exposure: what has already read these plans, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| Stage 2 D-575, D-577 (`scripts/rc150_firm_split.py --second-firm lucid`) | P-16's five seats split between Topstep and Lucid | 500 gate paths | growth at the bound; D-577 (as D-593 quotes it) found a Lucid seat worth less than a Topstep seat | two firms together, on growth; never Lucid alone |
| Stage 2 D-593, D-601 (`rc150_added_lucid`) | Lucid seats added to Topstep's five | gate paths | closed on growth (as D-643 quotes D-601) | as above |
| U1, Stage 2 D-620 (`results/user_journey.csv`, config `p16_5+1`) | five Topstep seats and one Lucid seat, every start | all starts | its start rows are on file; D-626 (7), as D-643 quotes it, found it the highest mean net from month 3 and the highest cash before the first payout | the Lucid identity (9.1 item 3) reproduces these rows; Lucid alone was never run |
| Stage 2 program U, family 5 (D-643, D-644; `results/u_firms.csv`) | Lucid seats 1, 2 or 5 beside Topstep's five, from day 0 or after the first payout | both blocks | closed, as every program U family closed (the row below); its file's numbers were not opened by the drafter | Lucid beside Topstep only |
| Q-12's survey (E-009; `docs/research/firms_survey_2026-11-15.md`) | zero-edge contract ceilings from quoted terms -- arithmetic, not a simulation | no NQ | "no firm clearly above Topstep's $50K" (E-009) | the drafter saw the survey's ceiling table rows for DayTraders and TradeDay while locating their sections |
| program U's nine families | P on the late block against P-14 | starts from 2024 | all closed | the late block is late development, not out of sample |

**Never run:** P-14's or P-16's trades on DayTraders' or TradeDay's contracts; Lucid alone (five Lucid seats, no
Topstep) on either; any Lucid run on P-14.

**The drafter's own reads (disclosed).** The record (both files); Stage 2's ledger and the vendored Lucid ledger; the
engine's account classes, the gate, the U1 runner and the Lucid adapter and setup; Stage 2's decision rows D-561,
D-574, D-575, D-593, D-643 and D-644 (which state the outcomes quoted above); the survey's sections for DayTraders and
TradeDay, for their conduct, news and product lines. For the second version, Q-59's 28 entries (their quotes and
notes), and the columns, release codes and row counts of Stage 2's vendored release calendars (to name the files in
5.5; no trade was matched against them). For the third version, the red team's review (Q-88), whose synthetic toys
(its Appendix A) are on made-up data, not on any plan; the vendored table code (`state_policy.py`, `risk_policy.py`)
and `fills.yaml`'s fee decomposition. No result file of any plan was opened; `u_firms.csv` and `user_journey.csv`
were not opened.

**What is already known of the direction (disclosed).** The survey's zero-edge arithmetic (E-009); Lucid beside
Topstep on growth (D-577, D-601) and on the journey (D-626 (7)); program U's family 5 (Lucid seats beside Topstep's)
closed. Nothing is known of any plan alone on the journey.

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
| price | $115.50 one-time with the checkout coupon, the card's list price $165 struck; resets not bought (`eval_fee`, `eval_reset_fee`) | field (`lucid_price`); the coupon as every purchase's price rests on the operator's statement (Stage 2 D-574: "Coupons are a multiple time thing"), which TradeDay's sale card has no counterpart to (U-1); $165 printed beside by A-10's arithmetic (10.1 item 9) |
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
| products, counting | futures only; NQ and MNQ listed; 10 micros count as 1 mini, every instrument and open position added up, an over-limit order rejected (`daytraders.permitted_products`, `daytraders.contract_counting`) | field: the designs trade NQ / MNQ, one position at a time across the firm, inside the 100-micro allowance as written |
| hours, flat time | the trading day 17:00 to 15:59 CT (`daytraders.trading_hours`); the flat time not settled -- the help page and the Terms conflict, but every time either states is at or after 15:59 CT (`daytraders.flat_time`) | moot: the designs are flat by 15:10 CT (section 5) |
| news | allowed, not recommended; no window named (`daytraders.news_rule`) | field (none) |
| hedging, copying | hedging prohibited within and across one's accounts, correlated instruments included; copying across one's own accounts allowed (`daytraders.hedging_rule`, `daytraders.copy_trading_own_accounts`) | tier 1 untouched: one position at a time across the firm, never opposite (Stage 2 D-157, D-429) |
| automation, high-frequency trading | tools and bots allowed at normal speeds; HFT prohibited -- millisecond orders, hundreds or thousands of trades a second or minute (`daytraders.automation_rule`, `daytraders.hft_rule`) | not reached: hand entry, at most one entry every five minutes across the firm by construction (D-429's five minutes flat) |
| minimum hold, trade count | unstated (`daytraders.min_hold_time_and_trade_count`) | section 5 (U-10) |
| martingale | 2x or more after a closed loss, as part of a pattern to win it back, prohibited (`daytraders.martingale_rule`) | a count (9.3): the table sizes by state, not by the last trade's outcome, but its sizes can step up after a loss |
| outsized positions | Terms s.7 and s.26 item 4: positions substantially larger than one's other trades, or grossly overleveraged; no threshold; the firm's sole discretion (`daytraders.tou_relative_position_size`) | G-8: priced by the denial ladder; its tier is the operator's (16) |
| own creation | Terms s.26 3.c: "Sharing trades and strategies with other users or making trades that were not Customer's own creation" (`daytraders.tou_s26_prohibited_conduct`) | a written question to the firm (16); not modelled |
| commissions | MNQ $1.02, NQ $3.98 per round turn on every simulated account; whether exchange and NFA fees are in is not stated (`daytraders.commissions`) | the cost rule, 4.8: the fee basis read at both ends (section 5) |

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
| funded daily loss limit | none; no trading within 2 % of a price limit (`tradeday.funded_daily_loss_limit`, `tradeday.price_limit_rule`) | field (none); the price-limit rule: G-2 |
| funded consistency | no day above 45 % of total gross profit, current profit plus payouts (`tradeday.fastpass_eod50k.funded_consistency_rule`) | A-5 |
| funded allowance | 2 contracts, plus 1 per $2,000 of profit at the close; no maximum stated (`tradeday.fastpass_eod50k.funded_position_limit`) | field (ladder `0:2,2000:3,4000:4,6000:5`); the cap at 5: section 5 |
| payout gate | five days of at least $150; balance above start; net profit since the last request; the 45 % rule; no buffer; no trading from the request until the payout is received (`tradeday.fastpass_eod50k.payout_frequency_gate`) | winning days and the profit since the request: field; the 45 % rule and the no-trading session: A-5; that session excluded from the next cycle: the engine's `REQUEST_AFTER_5PM` exclusion |
| split, cap, minimum | 80 %; $1,500 a request, and at most 50 % of the "account balance"; $250 (`tradeday.fastpass_eod50k.payout_split`, `tradeday.fastpass_eod50k.payout_cap`, `tradeday.payout_min`) | field; the 50 % base: section 5 (moot under 2.3) |
| the fifth request | the account moves to a new Funded Live account at the fifth request (`tradeday.fastpass_eod50k.payout_count_limit`) | A-5; whether the fifth is paid from Sim: section 5 |
| payout fee, processing | fee unstated; one business day (`tradeday.fastpass_eod50k.payout_fee`, `tradeday.fastpass_eod50k.payout_processing_days`) | the fee: section 5; the lag 1 session: field |
| seats | five active Funded Sim; further passes queued; ten accounts in all (`tradeday.max_funded_accounts`) | moot (five) |
| inactivity | dormant 30 days may be offboarded (`tradeday.inactivity_rule`) | G-10 |
| products | CME Group futures from the permitted list; NQ and MNQ listed (`tradeday.permitted_products`) | field |
| hours, flat time | a CME session from the 5 pm CT open; day-trading only; every position closed at least 10 minutes before the close, auto-liquidated at 3:50 pm CT (`tradeday.trading_hours`, `tradeday.flat_time`) | moot: the designs are flat by 15:10 CT (checked, 9.3) |
| tier-1 news | every open position auto-liquidated 2 minutes before each tier-1 release, markets reopened 2 minutes after; for NQ and MNQ the releases are CPI and the employment report (7:30 AM CT) and the FOMC statement and FOMC minutes (1:00 PM CT) (`tradeday.tier1_news_auto_liquidation`, `tradeday.tier1_release_list`) | G-3: a count, and a bracket at FP and QP (5.5) |
| bracketing releases | "Continued exploiting the lack of slippage in the sim environment to achieve unrealistic stop-loss execution, such as bracketing data releases" prohibited; neither term defined (`tradeday.bracketing_data_releases`) | G-14 |
| hedging, copying, coordinated trading | hedging the same product across accounts prohibited; copying across one's own accounts allowed; multiple users making the same trades shut down; trades meant to manipulate or gain an unfair advantage prohibited (`tradeday.hedging_rule`, `tradeday.copy_trading_own_accounts`, `tradeday.coordinated_trading_rule`) | tier 1 untouched for one user's own accounts (E-007 (c) stands for several users); the multiple-users sentence: a written question (16) |
| automation, trade count, order practices | third-party bots forbidden, no API; no strategy producing more than 200 trades a day, no few-second scalping; no order splitting, no trading outside the best bid or offer, no queue gaming (`tradeday.automation_rule`, `tradeday.trade_count_hold_time`, `tradeday.order_splitting_and_sim_exploitation`) | hand entry; one entry order per trade; the 200-trades line is a count (9.3) |
| commissions | all-in per side: MNQ $0.95, NQ $2.88 (round turn $1.90, $5.76), in evaluation and Funded Sim PnL (`tradeday.commissions`) | the cost rule, 4.8 |

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
| products, hours, tier-1 news, conduct, commissions | as FP (TradeDay's firm-level entries, 4.4) | as FP: field; moot; G-3 and 5.5; G-14; 9.3's counts; 4.8 |

### 4.6 What the engine cannot represent, built as adapters in `extended/` (declared; A-8 built, the rest after the pin)

Every adapter subclasses or wraps a vendored seam; none edits `vendor/`. Where a vendored body must be copied, it is
refused unless the vendored source hashes to its pin, as `extended/gate.py` does (Q-47). **Each has switches whose
Topstep setting is the vendored behaviour**, and with every switch at it the adapter must reproduce TS's registered
rows (9.1 item 2).

| id | adapter | what it adds |
|---|---|---|
| A-1 | `extended/firms.py` | a plan's contract applied to a design's replay arguments and gate arguments: rules, fees, billing, activation, lag, request timing, account classes, household rule, conduct, allowances, and the per-trade cost schedule (4.8). Lucid's by Stage 2's `rc150_firm_split.lucid_setup`, imported, on a setup made from the design's replay arguments; TS's leaves the arguments unchanged (tested equal) |
| A-2 | DayTraders evaluation (`CombineAccount` subclass, through `combine_account_cls`) | the soft daily loss limit (`dll`); the two Qualifying Days a pass needs (a day of at least $200 whose close has the best day at most 50 % of total profit); at or above target with Qualifying Days owed, the table's lookup as it stands (4.9); the inactivity closure (the account ends, not breached, when a rolling window of 30 calendar days from its purchase holds no day of at least $200 -- exact in the replay, whose sessions carry dates; 21 sessions in the gate, whose resampled days carry none, Stage 2's translation, the gate rows labelled) |
| A-3 | DayTraders Pro (`FundedAccount` subclass) | eligibility by eight Qualifying Days since the last payout or activation (a day of at least $200 whose close has the cycle's best day at most 30 % of the cycle's profit; the request day excluded); the $2,600 request gate; at least $2,000 left after a request; requests rounded down to $50; the soft daily loss limit; the inactivity closure (a rolling 30 calendar days from activation in the replay, 21 sessions in the gate, as A-2); the table's inputs of 4.9 |
| A-4 | TradeDay evaluation (`CombineAccount` subclass, with a decision wrapper) | a minimum count of trading days before a pass, a trading day being **a session with at least one executed trade** ("Every day you make a trade will count"; the engine's own `days` counts every live session, `lockstep.py` 506-507); at or above target with days owed, one micro a trade at the table's R until the days are logged (4.9) |
| A-5 | Fast Pass funded (`FundedAccount` subclass, with a decision wrapper) | the 45 % rule on gross profit; the session after a request untraded, the account read at a no-trade decision so that the router passes over it (Stage 2 D-162) and its signal goes to another account if one can take it. **The registered table does not sit that session out:** its solve only leaves the request day out of the winning-day count (`state_policy.py` 1017), and many request-day cells trade (the red team's re-read, Q-88b: in the no-closure table both designs use, the leaves reachable with `request_day = 1` trade in 526 of 630 funded and 326 of 678 paid cases, unweighted). So the wrapper **forces** the session untraded wherever its cell would trade -- never an assertion -- and those sessions are counted (9.3); the fifth request (section 5); the table's inputs of 4.9 |
| A-7 | Quick Pay funded (`FundedAccount` subclass, with a wrapper on its draw) | the gross-profit intraday floor with the excursion bracket (U-9, 5.4); eligibility; the tiered split; the $10,000 ceiling at two ends (section 5); both request readings (5.6); the table's inputs of 4.9 |
| A-8 | the gate for another plan -- **built** (Q-71, E-049) | `extended/gate.py`'s `run_gate` takes `payout_lag_days`, `household_closure` and `combine_account_cls`; `extended/campaign.py` re-composes `simulate_lockstep_campaign` (its vendored body plus one keyword, pinned by its source hash), because the vendored campaign does not pass `combine_account_cls` to its paths. Its synthetic identity holds (E-049); nothing carries through it until Q-80's 500-path identities hold |
| A-9 | Q-17's ladder adapter (`extended/user_beside.py`) | takes a plan's arguments from A-1. **Q-76 as merged (E-059)** gives the funded class as a keyword (`funded_account_cls=`). **A-9's own two keywords**, to be built as generic infrastructure (Q-100), each holding U1's start-row identity at its default: (a) **a `household_closure` route** -- a keyword passed through to the path -- for Lucid's lenient reach (`household_closure=False`, only the account that took its fifth payout ends), which `base_problems` refuses on the path today (`user_beside.py` 157-171); Lucid's strict reach needs nothing, the engine's default taking the class's own rule (`lockstep.py` 1397); (b) **the ladder's start-seed base** (section 12's 20261990; today the run loop seeds starts from Q-17's own base, `start_seed(s)`, `user_beside.py` 126-130, 323). Its `off` arm must still reproduce U1's start rows |
| A-10 | fee arithmetic | DayTraders' recurring $5 Pro fee, and the price grid and break-even price (10.1 item 9): exact arithmetic on each start's purchase, billing and activation records. Exact because the replay's bankroll never binds, so no purchase depends on cash -- checked on every start (9.3). In the gate beside, DayTraders' recurring fee is left out and its rows labelled an upper bound in it |
| A-11 | TradeDay's tier-1 liquidation (a wrapper on a TradeDay account's draw) | a trade open at the start of a tier-1 window booked by 5.5's strict or lenient reading, or its walked outcome in the "no liquidation" runs; its position held to its walked exit for the one-position rule; on evaluations and Funded Sim alike (no sentence names an account type). With no trade in a window it changes nothing (tested). **Off in the gate:** the gate's resampled days carry no calendar date (`DayBlock`, `distribution.py` 40-80; `_GateDraws` resamples), so no window can be placed; the FP and QP gate rows are labelled "tier-1 liquidation not applied" |

(There is no A-6: the evaluation's minimum days of both TradeDay plans are A-4.) **If A-5's pass-over, A-4's
one-micro decision or 4.9's inputs cannot be built without editing the vendored engine, the build stops and reports;
this declaration does not fall back.**

### 4.7 What is not modelled, listed as gaps

| id | gap | how it is shown |
|---|---|---|
| G-1 | Quick Pay's favourable excursion inside a trade: Stage 2's trades carry the adverse excursion (`DayBlock.mae`), not the favourable one | bracketed from the trade's own outcomes at the menu's R values (U-9); an exact walk of the bars would be a new walk with its own identity, not this reading |
| G-2 | TradeDay's "no trading within 2 % of a price limit" (the account lost on a breach; `tradeday.price_limit_rule`): the page gives the equity circuit-breaker levels (7 %, 13 %, 20 % from settlement) but not how "within 2 %" is measured, and this reading reads no bar | not modelled; every TradeDay row says so; its effect is not bounded |
| G-3 | TradeDay's tier-1 auto-liquidation (`tradeday.tier1_news_auto_liquidation`, `tradeday.tier1_release_list`): for NQ and MNQ, every position open at 07:28 CT on CPI and employment-report days and at 12:58 CT on FOMC statement and FOMC minutes days is closed by the firm, and nothing trades until 07:32 or 13:02; the engine models no such exit, and the price at 07:28 or 12:58 needs the bars | **the count** (9.3, the run's first mechanics line), and at FP and QP **the bracket** of 5.5 |
| G-4 | every live move: Lucid's (Stage 2's household readings), Fast Pass's Funded Live at the fifth request, Quick Pay's Live review at $10,000, DayTraders' discretionary live call that closes every simulated account | live accounts are not modelled; an account moved ends, its balance not credited -- except at the two terms read at two ends in section 5 (Fast Pass's fifth request; Quick Pay's ceiling), whose lenient ends pay what the pages let the user withdraw before the move |
| G-5 | commissions: the cost rule of 4.8. DayTraders' fee basis is read at both ends (section 5): fees on top only add cost, so its strict end is the listed figures plus exchange and NFA fees as Topstep's verified page decomposes them. Left open: any DayTraders fee beyond that decomposition, and Lucid's actual schedule beside Topstep's (Stage 2 D-575's reading) | DT's two corners carry the two bases; LU rows conservative in this term (D-575) |
| G-6 | the state tables were solved for Topstep's contract (Stage 2 D-501) and are not re-solved for any plan (Stage 2 D-575 (1)'s known gap). **"The design traded there" includes 4.9's mappings** -- what each plan's accounts hand the table, and what an evaluation does at target with days owed -- which are declared choices, not the plan's | every plan's row is P-16's (P-14's) design traded there under 4.9, not the best design for that plan |
| G-7 | DayTraders' Lifetime billing | not read: its prices are not stated separately |
| G-8 | each plan's discretionary review, and DayTraders' Terms clause on positions substantially larger than one's other trades (`daytraders.tou_relative_position_size`: Topstep's s.8 wording, its base "other trades on the Day Traders Accounts"; no threshold) -- on its plain words it reaches the state table's funded opening, as E-012 found for Topstep's | priced by the denial ladder only; its tier is the operator's (16) |
| G-9 | DayTraders' consistency "small tolerance", unsized | read strictly (U-8): a lower bound in that term |
| G-10 | TradeDay's 30-day dormancy offboarding (discretionary) and its broker's archive. At Quick Pay its premise fails: an account drained below its trading size sits idle (the red team's M3) | not modelled; **counted at FP and QP** (9.3): sessions with no trade per funded account, accounts idle 30 calendar days, accounts drained below the smallest tradable size |
| G-11 | rule changes over 2020-2026 | today's terms on every start (2.2) |
| G-12 | a soft daily loss limit's later signals: an account DayTraders pauses takes no further trade that day, and trades already dealt to it are not re-dealt (the engine's day-loss mechanics, as for Topstep's RTP limit) | counted (9.3) |
| G-13 | payouts unavailable in holiday hours; Topstep's move to a Live Funded Account | as in every registered row |
| G-14 | TradeDay's "bracketing data releases" and "stops during major economic releases" (`tradeday.bracketing_data_releases`; neither term defined; "continued" and "deliberately" put repetition and intent in the test). The designs rest one stop and one target after a market entry; tier-1 releases cannot be held through at TradeDay (G-3); P-16's 07:30 CT mark on BEA GDP days enters at the release bar with its stop resting (E-021, Q-39), and GDP is not tier 1 at TradeDay | not modelled; the words neither reach nor clear the designs; every TradeDay row says so |

### 4.8 Per-trade costs: the cost rule, per plan (declared)

Each design prices a trade's fee at the contracts it holds -- as many minis as fit, the rest in micros -- through its
sizing rule's fee schedule (Stage 2 D-324; `fidelity.costs per_trade_at_size`, `vendor/stage2/config/atlas_a3.yaml`),
from each trade's own fee in its blocks (`DayBlock.fee`). The registered schedule is Topstep's all-in round turn
(`vendor/stage2/config/fills.yaml`, `round_turn_by_instrument`: MNQ $1.22, NQ $3.78; Topstep 8284213). A-1 sets each
plan's schedule; spread, slippage and the ticks at entry, stop and flatten are each design's own at every plan.

| plan | schedule (round turn: MNQ, NQ) | why | what it leaves open |
|---|---|---|---|
| TS | $1.22, $3.78 (as registered) | the reference | -- |
| LU | $1.22, $3.78 | Stage 2 D-575's reading: above Lucid's listed per-side fees, kept as the conservative figure | none in the direction: LU rows conservative in this term |
| DT | **two ends (section 5).** Strict: **$1.74, $6.76** -- the listed figures plus exchange and NFA fees as Topstep's verified page decomposes its own all-in figure (`fills.yaml` lines 32-35, 8284213: commission $0.50 a micro and $1.00 a mini round turn, NFA $0.02, so exchange fees $0.70 on MNQ and $2.76 on NQ). Lenient: **$1.02, $3.98** -- the listed figures as all-in | DayTraders lists MNQ $1.02 and NQ $3.98 a round turn (`daytraders.commissions`) without saying whether exchange and NFA fees are in. Fees on top only add cost, so the direction is known: the listed figures are the least it can be, the decomposition the most the record supports | any DayTraders fee beyond Topstep's decomposition (G-5). **Withdrawn:** the second version's "dearer of the listed and Topstep's figure" ($1.22, $3.98), adopted under E-045 as conservative -- it is lenient if fees come on top (the red team's M2) |
| FP, QP | **TradeDay's all-in schedule: $1.90, $5.76** | `tradeday.commissions`: $0.95 and $2.88 a side, brokerage, NFA, clearing and exchange fees included, in evaluation and Funded Sim PnL | none: TradeDay states it all-in. (The first version's Topstep schedule here was optimistic by $0.68 a micro round turn.) |

A check before any reading (9.2): every trade's fee at every plan equals its schedule at the contracts it holds. If a
design's blocks carry no per-trade fee, the build stops and reports. (P-16's sizing rule carries `fee_schedule` from
`fills.yaml`, `score_fv3_grid.sizing_rule`, so A-1's swap is one change.)

### 4.9 What each plan's accounts hand the table (the red team's M1; declared, tested)

**Why.** P-16's and P-14's tables are version-12 exports (`rc150_table_screen.py` 73). From version 7 every funded
cell is keyed by `request_day` and `win_days`, and every paid cell also by `line_gap` (`state_policy.py` 1338-1346).
The engine fills them from the account at each session (`risk_policy.account_state`, `risk_policy.py` 339-353):
`win_days` from `account.win_days`, `line_gap` from `account.since_pay` once paid, `request_day` from
`account.request_day_next`. The table was solved with `win_days` 0 to 5, **5 meaning eligible**, at Topstep's
winning-day rule (`state_policy.py` 971); a value above the top threshold reads the top cell (`Tiers.decide`). So what
an adapter stores in those three fields decides every funded size at that plan, and is declared here.

**The rule.** The table reads "eligible" exactly when the plan's own day count is complete:

- **`win_days` = min(5, max(0, 5 - the plan's own days still needed))**, at each close, after the plan's own count;
- **held:** when the plan's days are complete but a plan-specific gate other than the profit since the last request
  still blocks the request -- DayTraders' $2,600 balance gate and its 30 % share at the request's close, Fast Pass's
  45 % rule -- the account reads **`win_days` = 4**, the table's own cell one day short (reading PP's held-state rule,
  its draft's 6.3, in the same form; the profit since the last request is the table's own `line_gap`);
- **`since_pay`** = the plan's own profit since the last request (the engine's field: the cycle's profit at every
  plan here);
- **`request_day_next`** = 1 only on the session the plan excludes from its count (or leaves untraded) after a request;
  0 at plans that exclude none.

| plan | `Rules.std_winning_days`, `std_winning_day_min` | what the account counts | `win_days` read by the table | `request_day_next` |
|---|---|---|---|---|
| TS | 5, $150 (as registered) | the engine's own | the engine's own | the engine's (`REQUEST_AFTER_5PM`) |
| LU | 5, $150 (Stage 2's `lucid_rules`) | the engine's own, with Lucid's $1 net in its gate | the engine's own | 0 (no session excluded) |
| DT | 5, $200 | Qualifying Days q, 0 to 8: a day of at least $200 whose close has the cycle's best day at most 30 % of the cycle's profit, the request day excluded | min(5, max(0, q - 3)); 4 while q = 8 and the balance is below $2,600 or the cycle's best day is above 30 % of its profit | the engine's (`REQUEST_AFTER_5PM`: "The day you request doesn't count") |
| FP | 5, $150 | the engine's own (Fast Pass's five days of $150 are Topstep's) | the engine's own; 4 while five days are counted and the 45 % rule blocks | the engine's; the session is also untraded (A-5) |
| QP, every close | 5, $150 (unused: QP counts no days) | none: eligible at any close with a positive balance after the account's first session | 5 from the account's second session; before it, 0 | 0 |
| QP, the reference's cadence (5.6) | 5, $150 | the engine's own count of days of $150 since the last request, every session counted | the engine's own | 0 |

**An evaluation at or above its target with days still owed** (a state the table never saw at Topstep, where a pass
needs no extra days):

- **TradeDay (A-4):** the account takes **at most one trade a session** (`max_trades` 1), at **one micro** and the
  table's R, until it has logged its trading days ("Every day you make a trade will count": one trade logs a day);
  the pass is then read at the first close with the days logged and the balance still at or above the
  (consistency-raised) target. A user logs the days at the smallest size, once a session; trading the table's size
  meanwhile could fail an account already at target, and taking more than one signal a session would divert signals
  the funded accounts and other evaluations would have taken, and add fees, to no purpose (the re-read's n3).
- **DayTraders (A-2):** **the table's lookup as it stands** (its top balance cell, `Tiers.decide`'s open top). A
  Qualifying Day needs a day of at least $200, which one micro cannot make reliably at these stops (one MNQ at P-16's
  37.5 points risks $75, at P-14's 12.5 points $25), so a day-logging size is no option here; the account trades on and
  can fail meanwhile -- counted (9.3).

**Tested** (T-2 to T-5, T-14): every plan's three fields and its two `Rules` fields at each close of toy campaigns;
the held reading; the TradeDay day-logging micro; at TS every field equals the vendored engine's.

**What it does to what the reading can show (E-051).** These rules make DT, FP and QP read the table's one-day-short
cells and smallest sizes more often than a free lookup would. They are fixed now, printed by plan (9.3: sessions read
held, at the day-logging micro, at the DT evaluation's top cell), and never tuned after a look.

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
  request, Fast Pass's scaling maximum, Quick Pay's profit ceiling): the reading under which it helps the user least at
  the strict end; the other concrete reading at the lenient end where there is one.
- **U-7. A term that cannot bind under section 2.3's user** (the hold queues; DayTraders' 10-day activation window;
  TradeDay's reset fee; Fast Pass's 50 % base; Quick Pay's per-request cap at every request but one -- the ceiling's
  closing withdrawal at its lenient end, read by U-10; DayTraders' unsettled flat time, every reading of which falls
  after the designs' 15:10 CT): not read. A mechanical check shows it does not bind (9.3); if it
  does, the plan's rows carry the check's count and nothing more is claimed for them.
- **U-8. A relaxation of a stated rule that no page sizes** is never assumed (DayTraders' consistency tolerance).
- **U-9. A verified rule whose data the trades lack** (Quick Pay's intraday peak): bracketed between the two extremes
  the trades' own outcomes at the menu's R values allow, read on the walk's own booking convention, both read (5.4).
- **U-10. A limit no page states is not invented** (DayTraders' and Quick Pay's payout counts; DayTraders' minimum hold
  time and trade count; Quick Pay's per-request cap at the ceiling's closing withdrawal, 5.2): read as no limit,
  labelled; the discretionary live moves are G-4; a stated rule beside it still applies (DayTraders' HFT rule, 4.3;
  TradeDay's $250 minimum, `tradeday.payout_min`).
- **U-11. A verified exit the trades lack** (TradeDay's tier-1 auto-liquidation, G-3): a trade it closes is booked at
  the worst value it could have while still open at the strict end, and at the best value it could have while still
  open at the lenient end; its walked outcome ("no liquidation") is read beside, neither end (5.5). A trade open at the
  window's start has touched neither its stop nor its target, so the firm's price lies strictly between them, and the
  walked outcome is not an end (the red team's M4: about half such trades are worth more at the liquidation than
  walked).
- **U-12. A stated price whose basis is unstated** (DayTraders' commissions, `daytraders.commissions`: "the page does
  not say whether exchange and NFA fees are included"): the listed figures as all-in at the lenient end; the listed
  figures plus the fees a verified page of this record decomposes (Topstep's, `fills.yaml`, 8284213) at the strict end.

**The strict corner and the lenient corner.** Each term with two ends has a **strict** end (the one that helps the
user least: the dearer price or fee, the slower lag, the wider closure, the later pass, the unpaid request, the higher
floor, the worse liquidation) and a **lenient** end. Every term's strict end is named in 5.2, so neither corner is
chosen after a look. **The corners are bounds only for the terms that act in one direction on every start** -- those
that move cash only, on the same path: the prices, U-3's fees, DayTraders' lag, Fast Pass's fifth request, and Quick
Pay's ceiling (both its ends end the account at the same close on the same path, and the lenient end only adds cash:
the re-read's note B). **DayTraders' fee basis is monotone per trade, not per start**: a per-trade cost moves every
trade's net, and through it the balance bands the table reads, which days reach the $200 Qualifying minimum, and
passes and breaches, so two starts can move in opposite directions (the re-read's n4). It, the minimum days,
DayTraders' inactivity, Lucid's reach, Quick Pay's peak and the tier-1 term are not monotone per start (a cost moves
the path; a closure frees a seat; a later pass moves the funded path), so for them the two corners are **the two
declared corners**, not bounds, and each one-at-a-time run of 7.2 is read as that term's direction on P-16 only (the
red team's m7).

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
| DT | flat time | `daytraders.flat_time` | unverified (the help page's 4:59 PM ET against the Terms' 5:00 PM ET or CST, or the market close if sooner) | moot: every stated time is at or after 15:59 CT and the designs are flat by 15:10 CT (checked: no trade exits after 15:10 CT) | -- | U-7 |
| DT | minimum hold time, trade count | `daytraders.min_hold_time_and_trade_count` | unstated | no hold time and no daily trade cap; the HFT rule (`daytraders.hft_rule`) still applies, and at most one entry every five minutes across the firm keeps the designs far from it | the same | U-10 |
| DT | fee basis | `daytraders.commissions` | verified; whether exchange and NFA fees are in unstated | fees on top: MNQ $1.74, NQ $6.76 a round turn (4.8) | the listed figures all-in: $1.02, $3.98 | U-12 |
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
| QP | per-request cap | `tradeday.quickpay_eod50k.payout_cap` | unstated | moot: the declared request rule (2.3); a check shows no request above it -- except the ceiling's closing withdrawal at its lenient end, where U-10 reads the unstated cap as none | -- | U-7; U-10 at that one request |
| QP | payout count | `tradeday.quickpay_eod50k.payout_count_limit` | unstated | no limit (the $10,000 ceiling ends the account) | the same | U-10 |
| QP | the intraday peak | `tradeday.quickpay_eod50k.funded_drawdown_type` | verified; the data lack the peak | the pessimistic bound (5.4) | the optimistic bound (5.4) | U-9 |
| QP | the profit ceiling's reach | `tradeday.quickpay_eod50k.funded_sim_profit_ceiling` | verified; what the user may do at the review unstated | the account ends at the first close its gross profit reaches $10,000, the excess forfeited, its balance not credited | at that close the excess is forfeited (the balance "revised back to the threshold level") and the whole remaining balance above start is requested -- "you can withdraw at any time as long as your account balance is positive" (`tradeday.quickpay_eod50k.payout_frequency_gate`) -- paid at the tiered split, then the account ends; Quick Pay's unstated per-request cap read as none at this one request (U-10), and no request made below TradeDay's $250 minimum (`tradeday.payout_min`) | U-6; U-10 |
| QP | the request habit | `tradeday.quickpay_eod50k.payout_frequency_gate`; `tradeday.quickpay_eod50k.payout_cap` | verified gate; no cap stated | the reference's amount at every eligible close (2.3) | -- the reference's cadence read beside, neither end (5.6) | 5.6 |
| FP, QP | tier-1 liquidation | `tradeday.tier1_news_auto_liquidation`; `tradeday.tier1_release_list` | verified; the price at the liquidation not in the trades | a trade open at a window's start booked at its full stop loss (5.5) | booked at its target less a tick, with the flatten's two-tick cost (5.5); its walked outcome beside, neither end | U-11 |

### 5.3 Why the declared request rule is each plan's own maximum where one is stated

Write B for the balance above start at the request's close.

- **TS, LU:** each plan's maximum is `min(0.5 B, $2,000)` -- the rule itself.
- **DT:** the maximum is `min(B - $2,000, $2,000)`, with B at least $2,600. The rule is `min(0.5 B, B - $2,000,
  $2,000)`. Below B = $4,000, `B - $2,000` is the smaller of the first two; from $4,000 both are at least $2,000. So the
  two are equal at every B.
- **FP:** read on the profit, the maximum is `min(0.5 B, $1,500)` -- the rule, so the rule is the plan's own maximum
  **under the profit reading only**. Read on the whole balance, the maximum is $1,500 at any B and the rule asks less
  below B = $3,000; it never asks more than either reading allows, so the 50 % base never enters as a refusal (U-7) --
  but under the balance reading the rule is not Fast Pass's maximum (the red team's note 1).
- **QP:** no maximum is stated, so the rule is the reference's amount, `min(0.5 B, $2,000)`.

### 5.4 Quick Pay's intraday peak, bracketed (U-9)

For a Quick Pay funded trade taken at R = R_x with dollar risk r (the size the engine gave it), the trade's outcomes at
the menu's R values (Stage 2's `DayBlock.r_by_rr`) say at which targets it would have been filled before its exit. Two
brackets on the same entry share its stop rule (the breakeven move included) until one exits, so:

- if the trade **won at R_x**, its favourable excursion before its exit is m = r x R_x (it exits at its target);
- if it **did not win at R_x** (stopped, moved-stop exit, or flattened), r x R_lo <= m < r x R_hi, where R_lo is the
  largest menu R below R_x at which it won (0 if none) and **R_hi the smallest menu R above R_lo** (at most R_x; the
  trades carry outcomes at every quarter R up to 3R). The trade did not win at R_hi either -- by R_lo's definition when
  R_hi is below R_x -- and the R_hi bracket shares the R_x bracket's path until both exit, so its peak stayed below
  R_hi's target (the red team's m6).

**The walk's convention, named.** On a bar where both a target and a stop trade, the walk books the stop
(`fv3_rung_walk.py` 12-13), so a trade booked as not winning at some R may in fact have touched that target. The
bracket is read on the walk's own booking -- the booking every outcome of this reading uses -- and is not corrected
for it.

Write G for the gross profit (the balance above start plus the gross paid) and G_pk for its running peak. The floor in
balance terms is `min(0, G_pk - $2,000)`; G_pk includes the peak inside each trade, and the gross value after each
exit and at each close.

- **The pessimistic bound (the strict end).** A trade that did not win at R_x peaks one tick short of R_hi's target
  (m = r x R_hi less one tick's value at its size), then falls to its exit. A trade that won at R_x takes its whole
  maximum adverse excursion at R_x (`DayBlock.mae_by_rr`) after a peak one tick short of its target, then rises to it.
- **The optimistic bound (the lenient end).** A trade that did not win at R_x peaks at the larger of r x R_lo and its
  exit's value when it exits by a profitable flatten, then falls to its exit. A trade that won at R_x takes every
  adverse excursion before its favourable one, so its peak is its exit.

In both: if the trade's path after its peak crosses the floor raised by that peak, the trade ends at that floor and
the account ends (a breach). Between trades and at the close, the floor follows the gross value. Both bounds are run
(the corners), and the strict one is flipped alone (7.2).

### 5.5 TradeDay's tier-1 liquidation: the count and the bracket (G-3, U-11)

**The windows.** For NQ and MNQ, TradeDay's tier-1 releases are US CPI and the employment report (Non-Farm Payrolls)
at 7:30 AM CT and the FOMC statement and the FOMC minutes at 1:00 PM CT (`tradeday.tier1_release_list`; "subject to
change without notice", read as stated). Every open position is closed two minutes before and nothing trades until two
minutes after (`tradeday.tier1_news_auto_liquidation`). So the windows are **07:28 to 07:32 CT** on CPI and
employment-report days and **12:58 to 13:02 CT** on FOMC statement and FOMC minutes days. **A trade is in a window**
when it is open at the window's start at **any offered R** (an offered trade's exit depends on the R it is traded at,
`DayBlock.exit_by_rr`, Stage 2 D-349). Bars are stamped at their open (CT), so a trade is open at 12:58 (07:28) when
its entry bar is stamped before 12:58 (07:28) and its exit bar at or after it; an entry bar stamped from 12:58 (07:28)
to before 13:02 (07:32) is an entry inside the window (the red team's m9).

**The dates, from files fixed now.**

- CPI and employment-report days: BLS's own schedules as Stage 2 vendored them
  (`vendor/stage2/data/releases_bls_0830_2009_2025.csv`, `releases_bls_0830_2026.csv`, from bls.gov; tracked files,
  not the licensed bars) -- the rows whose `release` column begins "Consumer Price Index for" or "Employment
  Situation for".
- FOMC statement days: the dates Stage 2's A3 reads (`vendor/stage2/config/im2_release_calendar.csv`, code `FOMC`;
  `config/sources/fomc_statements_2020_2024q1.csv`, `fomc_statements_2026q3.csv`; from federalreserve.gov).
- FOMC minutes days: `config/calendar_fomc_minutes.csv`, pinned under E-050 (sha256 of its LF text
  `0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7`), from the Federal Reserve's own calendar pages.

**The count** (9.3's first mechanics line, before any outcome; no bar read). Per stream, the registered offered trades
in a window, by release and year, from the trades' own entry and exit times; per TradeDay run, the executed trades among
them and the signals whose entry falls inside a window. **A-11 applies to evaluations and Funded Sim alike** (no
sentence of the record names an account type). **Disclosed in advance:** the report-day cut (no entry before
07:35:00 CT on a BLS 08:30 day, E-007 (d)) and "FOMC days out" keep the designs' entries out of the CPI,
employment-report and statement windows, but they do not stop a trade entered earlier from being open at 07:28 CT, and
FOMC minutes days are not among the days they name. So the count is not assumed to be zero. (The red team reads the
designs' own construction -- P-16 drops a report day's marks before 07:30 CT; P-14 takes no trade before its 07:30 cut;
A1 walks nothing on FOMC statement days -- as leaving only the FOMC-minutes windows open to the term, at most the
calendar's minutes days. The count settles it.)

**The bracket** (FP and QP only):

- **strict end:** a trade in a window is closed at the window's start at the worst value it could have while still
  open -- a loss of its whole dollar risk at its size, with its stop exit's costs (its stop had not been touched, so it
  was above it; a breakeven move that had taken the stop to entry is ignored);
- **lenient end:** a trade in a window is closed at the window's start at the best value it could have while still
  open -- its target less one tick, with the flatten's two-tick cost (its target had not been touched, so it was
  below it). Read, not changed: a walked target fills only when traded through, so the price at the window's start can
  equal the target itself, and this end is a tick short of the best -- immaterial, kept (the re-read's note A);
- **beside, neither end -- "no liquidation":** the trade keeps its own walked outcome. It is not an end: for a trade
  later stopped, or flattened below the liquidation price, the walked outcome is below the firm's price (the red team's
  M4 and its Appendix A3);
- **at every reading:** the account's position is held to the trade's walked exit for the one-position rule (no
  signal is freed by the liquidation), and a TradeDay account takes no entry inside a window (the signal is skipped,
  counted);
- **on the verdict arm** (the re-read's note C): a trade booked by the liquidation, at either end or at "no
  liquidation", takes the same per-R shift to its R's registered bound that every outcome at that R takes on that arm
  (`gate.shifted_blocks`' per-R delta, as `customer_slices.arm_blocks` applies it): the shift is a property of the
  trade's R, not of what books its exit. So the three readings differ by their booking alone, on both arms.

**The runs.** The term sits in both corners of FP and QP on both streams; on a stream whose count is zero its readings
are the same. If P-16's count is not zero, four one-at-a-time runs are added from the strict corner -- FP-16-news and
QP-16-news (this term at its lenient end) and FP-16-walked and QP-16-walked (this term at "no liquidation") -- making
**34 replays**; if it is zero, **30**. The condition is a count of trade times, decided before any outcome is read.

### 5.6 Quick Pay's second request reading (the red team's M3; fixed before any Quick Pay row exists)

**Why.** Quick Pay is eligible at every close with a positive balance, its floor is frozen at start once the gross
peak reaches $2,000, and a payout lowers the balance, not the floor. So 2.3's rule -- the reference's amount at every
eligible close -- halves the cushion above that floor at every close until a request falls below the $250 minimum. The
red team's synthetic toy (its Appendix A2, made-up data) showed the median such account drained below its trading
size and idle for the rest of the year, holding a seat. QP's row under that rule reads the request habit as much as
the contract.

**The second reading, "the reference's cadence".** The same amount, `min(0.5 B, $2,000)` and at least $250, requested
only at a close at which the account has had **five days of at least $150 since its last request** (the reference's
own `xfa_std_winning_days` and `xfa_std_winning_day_min`, every session counted, none excluded) and a positive
balance. It is the user's habit at the reference held fixed, not a rule of Quick Pay's.

**How it is read.**

- It is run beside, as `QP-16-req`: the strict corner on P-16 with only the request rule changed. **It is called
  neither strict nor lenient**: which habit helps a user is not monotone (a drained account lives longer; a fuller one
  breaches more and pays more).
- **Every QP row carries its request rule's name**: "every eligible close" (the corners and the other QP runs) or "the
  reference's cadence" (`QP-16-req`).
- Where the two disagree on P-16 about which side of TS the plan lies on P, the menu says QP "**depends on its request
  rule**" (10.1 item 5), as it says "depends on its unread terms" of the corners.
- **G-10 counted at QP** under both rules (9.3): sessions with no trade per funded account, accounts idle 30 calendar
  days, accounts drained below the smallest tradable size (one micro at the trade's stop).
- 4.9 gives each rule's table inputs. Neither rule is changed after any QP row is seen; a third would be a new
  declaration.

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
   purposes on this line. The reader admits a pinned `prereg/RD-` file on the F- rules (E-041, E-053 (2)).

   - **Judged-block reads:** `firm_scorecard`, `firm_ladder_beside`, `firm_gate_beside`

   **The identity stage** (9.1) is not authorised by this line: it runs first, as its own script under `identity/`
   (the reader admits the purpose `identity` only from `identity/*.py`, `reader.py` 377-391), under its own decision
   row naming the identities. **Once per purpose:** once a clean run has ledgered a read under one of these purposes,
   any later clean run under it -- a restart, a plan's rerun after an adapter fix, a rerun the failure protocol calls
   for -- is refused unless it passes `repeat="E-NNN"`, a decision row naming this file (`reader.py` 478-501).

## 7. The cells and the runs

### 7.1 The corners and the references

- **References.** TS on P-16 and TS on P-14, as registered: they must reproduce the registered rows (9.1 item 1).
- **Corners.** For each of LU, DT, FP and QP, on each stream: the **strict corner** (every term of 5.2 at its strict
  end at once) and the **lenient corner** (every one at its lenient end). U-3's fees are $0 at both, labelled.

### 7.2 One at a time

On P-16 only, from the strict corner, each term with two ends flipped alone to its lenient end: DT's price, lag,
inactivity and fee basis; FP's price, minimum days and fifth request; QP's price, minimum days, intraday peak and
profit ceiling; and, only if P-16's count of 5.5 is not zero, FP's and QP's tier-1 liquidation (at its lenient end, and
at "no liquidation" beside). Beside them, QP's second request reading (5.6), neither end. Lucid has one such term, so
its corners are its one-at-a-time reading. A one-at-a-time run shows that term's direction on P-16 only (5.1).

### 7.3 The runs

| run | plan | stream | settings | kind |
|---|---|---|---|---|
| TS-16 | TS | P-16 | as registered | reference (identity) |
| TS-14 | TS | P-14 | as registered | reference (identity) |
| LU-16-s, LU-16-l | LU | P-16 | strict, lenient corner | corner |
| LU-14-s, LU-14-l | LU | P-14 | strict, lenient corner | corner |
| DT-16-s, DT-16-l | DT | P-16 | strict, lenient corner | corner |
| DT-14-s, DT-14-l | DT | P-14 | strict, lenient corner | corner |
| DT-16-price, DT-16-lag, DT-16-inact, DT-16-fees | DT | P-16 | strict, with that one term lenient | one at a time |
| FP-16-s, FP-16-l | FP | P-16 | strict, lenient corner | corner |
| FP-14-s, FP-14-l | FP | P-14 | strict, lenient corner | corner |
| FP-16-price, FP-16-days, FP-16-fifth | FP | P-16 | strict, with that one term lenient | one at a time |
| QP-16-s, QP-16-l | QP | P-16 | strict, lenient corner | corner |
| QP-14-s, QP-14-l | QP | P-14 | strict, lenient corner | corner |
| QP-16-price, QP-16-days, QP-16-peak, QP-16-ceil | QP | P-16 | strict, with that one term lenient | one at a time |
| QP-16-req | QP | P-16 | strict, with the reference's cadence as the request rule (5.6) | beside, neither end |
| FP-16-news, QP-16-news | FP, QP | P-16 | strict, with the tier-1 liquidation lenient -- only if P-16's count of 5.5 is not zero | one at a time |
| FP-16-walked, QP-16-walked | FP, QP | P-16 | strict, with the tier-1 liquidation at "no liquidation" -- only if P-16's count of 5.5 is not zero | beside, neither end |

That is **30 replays** -- 2 references, 16 corners, 12 one at a time (QP-16-req among them) -- or **34** with the four
news runs. Each runs both arms, every start, the long replay and U1's exact-length runs.

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
| QP's second request reading | the same amount at the reference's cadence (five days of $150 since the last request) | **described**, beside (P-16) | `QP-16-req` | 5.6; the red team's M3 |
| the table's inputs | what each plan's accounts hand the table (`win_days`, `since_pay`, `request_day_next`); an evaluation at target with days owed | fixed, per plan | 4.9's table: the plan's days still needed mapped to 0..5, held at 4; TradeDay's day-logging micro; DayTraders' lookup as it stands | 4.9; the red team's M1 |
| the plan's verified terms | caps, splits, floors, gates, fees, allowances, lags, seats | fixed | the records' values | section 4; Appendix R |
| unread prices | evaluation prices not verified | **both ends** | FP $248 / $99; QP $175 / $69; DT on the grid, $250 / $25 at its ends | U-1, U-2 |
| unread fees | fees no page states | fixed | $0, labelled an upper bound | U-3 |
| conflicting minimum days | TradeDay's evaluation | **both ends** | FP 7 / 3; QP 7 / 5 trading days | U-4 |
| DT's lag | payout processing | **both ends** | 3 / 1 sessions | U-5 |
| unstated reaches | Lucid's live move; DT's inactivity accounts; FP's fifth request; QP's profit ceiling | **both ends** | 5.2 | U-6 |
| DT's fee basis | whether DayTraders' listed commissions include exchange and NFA fees | **both ends** | fees on top ($1.74 / $6.76) / listed as all-in ($1.02 / $3.98), MNQ / NQ | U-12, 4.8 |
| FP's scaling maximum | the funded ladder's top | fixed | 5 contracts | U-6 |
| QP's intraday peak | the floor inside a trade | **both ends** | the pessimistic / optimistic bound | U-9, 5.4 |
| per-trade costs | the round-turn fee each trade pays, at the contracts it holds | fixed, per plan (DT at both ends) | TS and LU $1.22 / $3.78; DT as the row above; FP and QP $1.90 / $5.76 (MNQ / NQ) | 4.8 |
| TradeDay's tier-1 liquidation | what the firm's exit two minutes before a tier-1 release does to a trade open then | **both ends** (FP, QP) | its full stop loss / its target less a tick; its walked outcome beside | U-11, 5.5 |
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

The identities run first, as their own script under `identity/`, under the purpose `identity` and their own decision
row (section 6 item 6); the reading's runner starts only once that script has printed that they hold.

1. **TS through this reading's runner** (A-1 with Topstep's contract, A-8, and A-9's `off` arm) reproduces, for P-16
   and P-14: U1's start rows (`vendor/stage2/results/user_journey.csv`, section `start`, configs `p16` and `p14`, both
   arms, every start, every column as E-010 compared them: money and the ratio to 1e-6; counts, days, dates and text
   exactly), with U1's checks of every run's payouts and fees against the engine's totals; and the registered gate paths
   (`vendor/stage2/results/rc_s150_all_gate_paths.csv` at seed 20261206 after P-16's trades' hash;
   `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv` at seed 20261131), every `zero_edge_decomposition.PATH_COLS`
   column, point and bound, all 500 paths, to 1e-6.
2. **Every adapter at its Topstep setting** (A-2 to A-7 and A-11 with every switch at the vendored behaviour, 4.9's
   inputs at TS's) reproduces item 1:
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
- Every trade's fee equals its plan's schedule (4.8) at the contracts it holds.

### 9.3 The mechanics, printed first

Printed for each plan, stream and block before any paired outcome. They describe where a contract binds, not whether it
helps.

- **first, G-3's count** (5.5): the registered offered trades open at the start of a TradeDay tier-1 window, by release
  and year, on each stream; then, per TradeDay run, the executed ones and the signals skipped inside a window;
- **two conduct counts, readings and not rulings** (the tier of either, if nonzero, is the operator's, as E-013 set
  Topstep's; nothing in the reading changes with them):
  - **DayTraders' martingale rule** (`daytraders.martingale_rule`): per DT run, in micro-equivalents, the trades taken
    at least twice the size of the trade before them when that trade closed at a loss -- counted two ways: **within one
    account**, and **across the user's accounts in time order** (one position at a time across the firm, so the
    sequence a reviewer sees is firm-wide: a small evaluation loss followed by a funded opening on another account is
    a 2x step in it). Their count, share and the accounts they fall in. The table sizes by the account's state, not by
    the last trade's outcome, and the page ties the ban to a pattern meant "to win back the loss", so a nonzero count
    is printed with that said;
  - **TradeDay's 200-trades-a-day line** (`tradeday.trade_count_hold_time`): per FP and QP run, the largest number of
    trades in one session in one account and across the user's five accounts together (the page says "a strategy",
    not per account or per trader). Any session above 200 labels the plan's rows;
- the share of starts on which the plan differs from TS at all within 63, 126 and 252 sessions;
- the share of trades whose contracts differ from TS's, by account kind; the realised-to-intended risk in P-14's
  allowance-capped form (E-022 (1)); the trades stood aside (Stage 2 D-272);
- **where each plan binds:** DT -- daily-limit days, passes delayed by the Qualifying Days, eligible closes blocked by
  the 30 % rule, requests cut by the $2,000 left and the $50 increment, inactivity closures, signals lost to a paused
  account (G-12); FP -- passes delayed to the seventh day, closes blocked by the 45 % rule, post-request sessions whose
  table cell would have traded and A-5 forced untraded (the re-read's n1), their signals re-dealt or skipped,
  fifth-request endings, trades an uncapped ladder would size
  differently; QP -- floor rises from intraday peaks at both bounds, breaches at a raised floor, requests by split tier,
  accounts ended at $10,000; LU -- fifth payouts and household closures;
- **4.9's inputs at work** (DT, FP, QP): funded sessions read held (`win_days` 4), by plan; TradeDay evaluations at
  target logging days at one micro, one trade a session, and the sessions it took; DayTraders evaluations at target
  with Qualifying Days owed, and how many failed meanwhile; trades whose size the DayTraders daily limit capped (2.3);
- **G-10 at FP and QP** (both QP request readings): sessions with no trade per funded account; accounts idle 30
  calendar days; accounts drained below the smallest tradable size (one micro at the trade's stop);
- **the checks that must be zero** (U-7): the peak hold queue; resets bought; DT activations later than ten days after
  a pass; FP requests above half the profit; QP requests above the reference's amount, the ceiling's closing withdrawal
  at its lenient end excepted (5.2, n5); QP requests below $250; purchases refused for cash (A-10's
  premise); any trade exiting after 15:10 CT (DayTraders' unsettled flat time and TradeDay's 3:50 pm CT liquidation both
  fall after it); and **any trade on a session that closes before 15:20 CT by E-029's calendar**
  (`config/calendar_early_closes.csv`) -- on an abbreviated session the designs' 15:10 CT is not the binding time, and
  TradeDay's "10 minutes before the close" and DayTraders' "or the market close if sooner" would bind first (the red
  team's note 2; the designs' walk takes nothing on early-close days, `atlas_local.py` 13, Stage 2 D-215, so the count
  is expected to be zero and is checked, not assumed).

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
   the plan's row, and by how much -- each run that term's direction on P-16 only (5.1). A plan whose two corners lie on
   opposite sides of TS on P is flagged "**depends on its unread terms**"; Quick Pay whose two request readings lie on
   opposite sides of TS on P (P-16) is flagged "**depends on its request rule**" (5.6). The flags are mechanical, not
   lines.
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
   The gate's resampled days carry no date, so three of the replay's terms are read differently there, each gate row
   labelled: TradeDay's tier-1 liquidation is off (A-11); DayTraders' inactivity runs on 21 sessions, not 30 calendar
   days (A-2, A-3); DayTraders' recurring $5 Pro fee is left out, the rows an upper bound in it (A-10).
9. **The price grid and the break-even price** (DT, FP, QP; and Lucid at its struck list price of $165, beside its
   verified $115.50): every money measure and P at each price of U-2's grid, and at every listed price, by exact
   arithmetic (A-10) from the run. The arithmetic must reproduce the run at the
   bracket's other end (the one-at-a-time price run) on every start to 1e-6, refusing. Beside it, **the break-even
   price** against TS for P, S5a and the mean month-3 net: the price in $0 to $250 at which the plan's measure equals
   TS's (bisection on the exact arithmetic), or "none in range". Printed beside, never a pick.
10. **The evenness trade-off.** The plans' corners as points of "ahead" against each evenness measure, in E-015's menu
    form.
11. **The menu.** Each plan's strict and lenient rows: all starts the headline, the early and late blocks and the
    start years beside. Every row carries its labels: the upper bounds (U-3), the gaps that touch it (4.7), the cost
    rule's open question (4.8), the moot checks' and the conduct counts (9.3), the firm's written question while it is
    open (16), and at QP its request rule (5.6). **The stability flag:** a plan whose mean paired difference in P, or in any guarded measure, has
    opposite signs on the early and late blocks is flagged "not stable across blocks" (mechanical). **E-015's limits**
    are flags only, once the operator approves them; until then the menu is read without flags, and says so.
12. **Not modelled, and said so wherever this scorecard appears:** a user who stops when their own money runs out, the
    user's time, taxes.

### 10.2 The uncertainty on each paired reading (fixed now)

These are descriptions, not tests. Nothing here is compared with a critical value to decide anything; a described
reading has no level (E-023 (1)), so no one-sided comparison is printed (the second version's item 8, Q-16's
comparison at 0.05, is dropped: the red team's m1). The method began as reading PP's (its draft's 9.2); the window
rule below corrects it, and the same correction is owed there (the red team's M5, told to PP's drafter).

1. **The windows.** For a reading at horizon h on a block, the block's starts in order are cut into consecutive
   h-start windows from the block's first start (a last incomplete window dropped), and **every other window is kept**
   -- the first, third, fifth, ... So kept windows are separated by h starts, and no two kept windows' measures share a
   session (a start's measure at h reads sessions s to s + h - 1). n_w is the number of kept windows, printed with
   every reading. **Why:** on adjacent windows the window means share up to h - 1 sessions, their lag-1 correlation is
   near 1/4 even with independent sessions, and the nominal 90 % t-interval covers about 0.83 (the red team's Appendix
   A1); keeping every other window restored 0.87 to 0.91 there.
2. **The interval.** A two-sided 90 % interval from a Student-t on the n_w kept window means, with n_w - 1 degrees of
   freedom, **printed only when n_w is at least 4**. Below 4 the reading prints "too few independent windows for an
   interval" and gives only item 3.
3. **The window sign count.** In how many of the n_w kept windows the plan's mean is above, equal to and below TS's.
   Distribution-free, always printed.
4. **The effective sample size.** From the Bartlett long-run variance of the per-start difference with lag window h
   (audit B's form; `extended.user_measures.n_eff_bartlett`), on all the block's starts, beside.
5. **The minimum detectable difference** of item 2's interval at 80 % power: (t(0.95; n_w - 1) + t(0.80; n_w - 1))
   times the kept window means' standard error, printed beside each mean and before it.
6. **A series zero on every kept window** prints "identical on these trades", with no interval and no MDD.
7. **The interval's honesty, beside -- rebuilt on overlapping series.** Its coverage on synthetic series of known zero
   mean, built as the reading's own measures are: a session series, each start's measure the sum (or the 0/1 sign) of
   the h sessions from it, the windows of item 1, at each h and n_w the reading uses (seed **20261991**; 20,000 series
   per setting; the red team's Appendix A1 construction). The session series: (a) independent Gaussian, the additive
   measure; (b) the same, its 0/1 "ahead" form less one half; (c) a paired form -- two session series correlated 0.64,
   the difference of their 0/1 signs; (d) skewed and lumpy -- each session +g with probability 1 - p and -g(1 - p)/p
   with probability p, plus N(0, s^2) noise (g = 0.01; p in {0.05, 0.10, 0.20}; s in {0.0025, 0.005, 0.01}), and its
   mirror; (e) persistent -- (d) with the rare session's sign repeated in the next session with probability one half.
   **A reading whose coverage, at its h and n_w on the worst of these shapes, falls below 0.88 is labelled "interval
   below its coverage" with that coverage printed.**

**What this does to what the reading can show (E-051).** About half as many windows: every interval and minimum
detectable difference is wider (by the t quantile at fewer degrees of freedom and about the square root of two in the
standard error), and more readings print "too few independent windows" -- most of month 12, and much of the late
block at months 6 and 12. The sign count and the distributions over starts are unchanged. A plan difference the second
version would have shown as an interval clear of zero may now show only as a sign count.

## 11. What the reading delivers, and what each outcome means

- **It delivers** the menu of section 10: what P-16's and P-14's registered trades and tables do to a user's journey on
  each of five plans' verified contracts, with every unread term's spread.
- **It does not deliver** a carried design, a registration id, a confirmation, a claim at a level, or a recommendation
  of a firm (E-023 (1)).
- **No outcome passes or fails.** What follows from each, fixed now:
  - an identity fails (9.1): the reading stops, the failure protocol applies;
  - an oracle is breached (9.2): an engine error; the reading stops;
  - a moot check is nonzero (9.3): the plan's rows carry the count; nothing is resolved here;
  - a plan's corners lie on one side of TS on P: the menu shows the plan above (or below) TS on these trades **at both
    declared corners** -- a bound only in the terms that act in one direction on every start (5.1); in the others, the
    two corners as declared;
  - a plan's corners straddle TS: the menu flags it "depends on its unread terms"; the operator's read of a price (DT),
    or a written question to the firm, is what would settle it. **No run is repeated to settle it**: a re-read is a new
    declaration citing this one;
  - Quick Pay's two request readings straddle TS: the menu flags it "depends on its request rule" (5.6).
- **The operator's choice.** Recorded in its own decision row, citing this reading's result files (E-015: limits
  first, then the best inside them). Buying a plan is a purchase, the operator's. **It is an in-sample choice:** taken
  over five plans and their corners on the development window 2020-2026, with no confirmation on unread data (E-023
  (1)); the menu says so beside it (the red team's note 6).
- **No confirmation.** Nothing is carried, so NQ from 2026-07-17 is not touched.
- **The binding.** The blocks read here are recorded as read for firm contracts on P-14 and P-16, all of them. A later
  firm reading names this one, states what changed, and reads no block of it as fresh.

## 12. Seeds, fixed now and checked

| seed | status | what it draws |
|---|---|---|
| 20261990 | in use | the denial ladder's per-start path seeds (`lockstep.child_seed(20261990, 0, start_day)`), common to every plan's ladder run (10.1 item 7) |
| 20261991 | in use | 10.2 item 7's synthetic coverage series, and T-9 |
| 20261992 | in use | the build's toy campaigns (T-1 to T-7, T-10, T-12 to T-14) |
| 20261993 | reserved, unused | -- (it was Q-16's comparison beside, dropped in the third version, the red team's m1; never drawn, not reassigned) |
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
2. **Counted under this reading's row:** 30 replays, or 34 with 5.5's four news runs (28 or 32 new: 16 corners and 12
   or 16 one at a time, QP-16-req and the two "no liquidation" runs among them as readings beside; 2 references,
   counted as identities); 27 denial-ladder replays and 16 gates beside, labelled; every block read, recorded as read
   for firm contracts (11).
3. **Nothing is selected by the program.** The operator's menu choice is a choice among described readings, recorded in
   its own row with the menu it was made from.

## 14. The build: adapters, identities and tests

### 14.1 The adapters

Section 4.6's A-1 to A-11, in `extended/`, each with its Topstep setting. The firm runner is the U1 replay
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
| T-0 (with the draft) | `tests/test_rd_firms_draft.py`: Appendix R cites every key with its record's status; every open term of the three new firms' records is cited and read in section 5; section 12 holds the brief's block, its seeds in use and reserved appear in no other declaration and nowhere in the vendored snapshot, and the retired ones are found elsewhere; the `Judged-block reads:` purposes parse and choose nothing; the reader admits an RD- file (E-041); and, end to end (Q-74, E-053), this file's own text pinned in a temporary tree authorises its declared engine reads and is refused where an F- file would be |
| T-1 | every adapter at its Topstep setting equals the vendored class bit for bit on toy campaigns (seed 20261992): every day's balance, floor, request, payout, cash and recorded `eligible` |
| T-2 | DT: the evaluation's two Qualifying Days (a day over the 50 % share does not count), the soft daily limit, the inactivity closure on a rolling 30 calendar days (21 sessions in the gate), an evaluation at target with Qualifying Days owed reading the table's top cell; the Pro account's eight Qualifying Days with the request day excluded, the 30 % cycle rule, the $2,600 gate, the $2,000 left, the $50 rounding, and a payout leaving the floor at start (the engine's move a no-op); the recurring $5 fee's due sessions; the fee basis at both ends (T-12) |
| T-3 | FP: the 45 % rule on gross profit; the session after a request untraded and passed over, its signal re-dealt to the longest-waiting other account -- **including a request-day cell that trades**, which A-5 forces to no trade and counts, never stopping the run; the fifth request at both ends; the ladder and its cap |
| T-4 | QP: the gross-profit floor on the page's own example (a $50,500 balance with the floor at $48,500; after a $500 payout, $50,000 with the floor still at $48,500); the tiered split on its example ($6,000 of profit and a $3,000 payout: $1,600 plus $500); the $10,000 ceiling at both ends; 5.4's two bounds on hand-built trades with known outcomes at each R (R_hi, a profitable flatten's exit); both request readings of 5.6 on a toy account, the cadence reading's five days of $150 counted with no session excluded |
| T-5 | TradeDay's minimum days at 3, 5 and 7, counting only sessions with an executed trade; an evaluation at target with days owed taking one micro at the table's R, **at most one trade a session** (a second routed signal that session going to another account), until they are logged, then passing at the first close with the days logged and the target held |
| T-6 | A-10: on toy campaigns at two prices the records are identical and the cash differs exactly by the arithmetic; the break-even bisection on a known case |
| T-7 | 9.2's oracles on toy campaigns |
| T-8 (`slow`) | 9.1 items 1 to 3 at 4 starts and 4 paths; the full run is the run's first stage (heavy) |
| T-9 | 10.2: every other window kept (no two kept windows' measures share a session), the interval from 4 kept windows only, the sign count, the zero-series rule, the coverage on one small fixed overlapping setting (seed 20261991), and the 0.88 label |
| T-10 | A-8 equals the vendored gate with no new keyword given (synthetic, as Q-47's identity) and at Topstep's values |
| T-11 | 14.2: the loader refuses an entry not verified; no rule literal outside the constants table |
| T-12 | 4.8: each plan's fee schedule reaches the sizing rule; a hand-built trade of 26 micros is priced as two minis and six micros at each plan's figures, DT at both ends; TS's schedule is the registered one |
| T-13 | 5.5 and A-11: a hand-built day with a trade open at 07:28 CT on a CPI date and at 12:58 CT on an FOMC-minutes date (at some offered R only) is counted and booked at the strict end, the lenient end and "no liquidation"; a trade whose exit bar is stamped 07:27 is not; an entry bar at 07:30 is skipped; with no trade in a window nothing changes; A-11 off in the gate; the 9.3 counts for martingale steps (per account and firm-wide, in micro-equivalents) and for trades a session on toy campaigns |
| T-14 | 4.9: at each close of toy campaigns, every plan's `win_days`, `since_pay` and `request_day_next` as its table row says, the held reading at 4, and the two `Rules` fields; at TS every field equals the vendored engine's |
| T-15 | A-9's own keywords: at their defaults (no `household_closure` given; the seed base Q-17's own) the `off` arm reproduces U1's start rows; `household_closure=False` reaches the path and ends only the account that took its fifth payout; the seed base 20261990 changes the ladder's draws and nothing else |

## 15. Outputs and the run

- **Files:**
  - `results/fc_reading.csv`, sections `identity`, `oracle`, `mechanics`, `scorecard`, `paired`, `diverge`, `grid`,
    `ladder`, `coverage`;
  - `results/fc_gate.csv`, the gate rows;
  - `results/fc_menu.csv`, the menu with its flags and labels.

  Each written with its sidecar manifest through `extended.results.write_result`, carrying: `prereg_id`, the reading's
  id (unnumbered) and its pinning row; the run counts (30 or 34 replays; 28 or 32 new; 2 references; 27 ladder
  replays; 16 gates); each plan's cost schedule (4.8) and table inputs (4.9); QP's request rule on each QP row;
  every seed, the retired ones included; every parameter, section 5's readings and their labels; each plan's record
  entries with their dates read; the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`; `exploratory=False`, since
  nothing in it is chosen after a look. Every cell is still labelled "described, not carried".
- **The run:**
  - **where.** Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
    its end;
  - **weight: heavy.** Every start on two arms for 30 or 34 replays, 27 ladder replays and 16 gates: several hours at
    two workers; memory near the U1 identity's and Q-17's (E-010, E-024);
  - **order.** The identities first, by their own script under `identity/` (9.1, section 6 item 6); any failure stops
    the run. Then the oracles, the mechanics (9.3), then the reading;
  - **a restart or a rerun.** Recorded by the lead with its log. Any later clean run under one of this file's purposes
    -- a restart, a plan's rerun after an adapter fix, a rerun the failure protocol calls for -- passes
    `repeat="E-NNN"`, a decision row naming this file, or the reader refuses it (`reader.py` 478-501). Only the first
    complete run is read, unless that row says which run replaces it and why.
- **Waits:** the pinning row; A-1 to A-7 and A-9 to A-11 built with their tests (A-8 is built, E-049); **Q-80's
  500-path gate identities** before A-8 runs (E-049: every arm now passes through the re-composed campaign, so Q-51 no
  longer covers master's gate); before A-9 runs, **Q-76** (merged, E-059: the funded-class keyword), **A-9's own two
  keywords** -- the `household_closure` route and the ladder's seed base, each holding U1's start-row identity at its
  default (to be built generic as Q-100) -- and Q-17's adapter's identity (E-024). It does not wait for E-015's limits
  (flags only) or for the operator's price read (U-2).

## 16. Open before the pin

**The lead's:**

1. **The pin itself:** the lead's (or the gatekeeper's) check of the re-read's edit (Q-88b: pinnable after it; E-067).
   Settled since the second version and no longer open:
   the reader admits a pinned `prereg/RD-` file (E-041, E-053 (2); T-0 checks it end to end); the FOMC-minutes calendar
   is pinned (E-050, 5.5); A-8 is built (E-049).
2. **The rules are recorded (Q-59, E-045).** Products, contract counting, hours, flat times, news, conduct and
   commissions for DayTraders and TradeDay are in `config/rules_extended.yaml`; sections 4.3 to 4.5, 4.8, 5 and 9.3 read
   them, and Appendix R cites every one. If a later reading of either firm states a rule section 4 does not represent,
   that plan's cells are not run under this declaration (a redraft names it).
3. **E-020 (1)'s crawl-clause reading** stands for DayTraders and TradeDay. If the lead ever reads those clauses as
   E-009 read The Futures Desk's, their entries are struck and their cells dropped.
4. **Before the run, not the pin:** Q-80's 500-path gate identities before A-8 runs; Q-76 (merged) and A-9's own two
   keywords (Q-100) before A-9 runs; A-1 to A-7 and A-9 to A-11 built (15's waits).
5. **With reading PP.** The two began with one uncertainty method; this version's window rule (10.2, the red team's
   M5) is owed there too. Both readings pair against the same references; neither reads the other's cells.
6. **The name at the pin** (`prereg/RD-nn_<slug>.md`, E-025 (1)) must match the test's glob `RD-*firm*.md`, and this
   DRAFT file is removed (renamed) at the pin -- `tests/test_rd_firms_draft.py` asserts exactly one firms-reading file
   (the red team's note 7).

**The operator's:**

1. **DayTraders' price**, optional: a browser read of its EOD 50K evaluation price at checkout, Monthly billing
   (`docs/OPERATOR_SETUP.md`; a read, no purchase). U-2's grid covers it either way.
2. **Two written questions to the firms, for `docs/OPERATOR_SETUP.md`** (optional; the operator's own message from
   their own account, as Topstep's s.8 question is item 3 there, E-013 (1)). Until an answer is on record the reading
   runs as declared and every row of the plan names its question as open:
   - **To DayTraders.com**, on its Terms of Use s.26 item 3.c ("Sharing trades and strategies with other users or
     making trades that were not Customer's own creation", `daytraders.tou_s26_prohibited_conduct`): *"I trade only my
     own accounts, placing every order by hand. The trades follow a rules-based strategy I did not design myself (it was
     built for me from historical data). Are trades placed this way 'not Customer's own creation' under s.26 3.c? Does
     the answer change if other, unconnected people could follow the same published strategy in their own accounts?
     Two more: do the commissions on your Instruments and Commissions page (MNQ $1.02, NQ $3.98 a round turn) include
     exchange and NFA fees, or are those charged on top? And how many business days does a payout take from request to
     receipt?"* -- the first settles 4.8's fee basis (U-12), the second U-5's lag, whose slow end (three sessions) is
     borrowed from Topstep and is not strict if DayTraders takes longer (the red team's M2 item 4 and note 5).
   - **To TradeDay**, on "If multiple users are making the same trades, then all the accounts will be shut down, and the
     users suspended" (103000085101, `tradeday.coordinated_trading_rule`): *"I am one user trading my own accounts by
     hand. If my trades follow a strategy that other, unconnected TradeDay users might also follow independently, so
     that our trades coincide without any coordination, would my accounts fall under this sentence? Is one person
     copying their own trades across their own Evaluation and Funded Sim accounts outside it?"*
3. **The tier of DayTraders' outsized-position clause** (Terms s.7 and s.26 item 4, `daytraders.tou_relative_position_size`;
   G-8). On its plain words it reaches the state table's funded opening, as E-012 found for Topstep's s.8, which the
   operator set at tier 3, priced (E-013 (1)). Until the operator rules for DayTraders, the reading prices it the same
   way (the denial ladder beside the 0 % headline) and labels the DT rows.
4. **The levels of E-015's limits.** Approval is pending; they are flags only and never block.
5. **After the run:** the choice from the menu, if any; any purchase is the operator's.

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
| `daytraders.permitted_products` | record | verified | DT products (NQ, MNQ) |
| `daytraders.contract_counting` | record | verified | DT allowance counting |
| `daytraders.trading_hours` | record | verified | DT session |
| `daytraders.flat_time` | record | unverified | DT flat time, moot (U-7) |
| `daytraders.news_rule` | record | verified | DT news allowed |
| `daytraders.hedging_rule` | record | verified | DT hedging, tier 1 |
| `daytraders.copy_trading_own_accounts` | record | verified | DT copying own accounts |
| `daytraders.automation_rule` | record | verified | DT automation; hand entry |
| `daytraders.hft_rule` | record | verified | DT HFT, not reached |
| `daytraders.min_hold_time_and_trade_count` | record | unstated | DT hold time and trade count (U-10) |
| `daytraders.martingale_rule` | record | verified | DT martingale count (9.3) |
| `daytraders.tou_relative_position_size` | record | verified | DT outsized positions (G-8; the operator's tier) |
| `daytraders.tou_s26_prohibited_conduct` | record | verified | DT s.26 3.c (a written question) |
| `daytraders.commissions` | record | verified | DT cost rule (4.8) |
| `tradeday.permitted_products` | record | verified | TradeDay products (NQ, MNQ) |
| `tradeday.trading_hours` | record | verified | TradeDay session |
| `tradeday.flat_time` | record | verified | TradeDay flat time, moot (checked) |
| `tradeday.tier1_news_auto_liquidation` | record | verified | TradeDay tier-1 liquidation (G-3, 5.5) |
| `tradeday.tier1_release_list` | record | verified | TradeDay tier-1 windows (5.5) |
| `tradeday.bracketing_data_releases` | record | verified | TradeDay bracketing (G-14) |
| `tradeday.price_limit_rule` | record | verified | TradeDay price-limit rule (G-2) |
| `tradeday.hedging_rule` | record | verified | TradeDay hedging, tier 1 |
| `tradeday.copy_trading_own_accounts` | record | verified | TradeDay copying own accounts |
| `tradeday.coordinated_trading_rule` | record | verified | TradeDay multiple users (a written question) |
| `tradeday.automation_rule` | record | verified | TradeDay automation; hand entry |
| `tradeday.trade_count_hold_time` | record | verified | TradeDay 200-trades count (9.3) |
| `tradeday.order_splitting_and_sim_exploitation` | record | verified | TradeDay order practices, not reached |
| `tradeday.commissions` | record | verified | TradeDay cost rule (4.8) |
