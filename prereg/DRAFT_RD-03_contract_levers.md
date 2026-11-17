# RD-03: contract-use levers on the registered trades (reading CL) -- a described reading, unnumbered (E-023 (1))

**Status: declared before anything of it is built or read.** It is pinned by the sha256 of its LF text in its decision
row. Nothing declared is edited: a change is a new declaration under a new row. It takes no program family number
(E-023 (1)).

**Its text's history.** The first text, drafted as `prereg/DRAFT_RD-03_contract_levers.md` (TASK_QUEUE Q-116, E-144;
on wt/wt-payout, master merged at 3223b50), from the scout's note `docs/research/next_levers_contract_money_2026-11-17.md`
(Q-114, merged under E-134; its section 5 is this reading's outline) and Q-115's rules record (the rules-verifier,
official pages read 2026-11-16; committed on wt/wt-firms at deb45ad, E-135). At the pin the file is renamed
`prereg/RD-03_contract_levers.md` and nothing else changes; the pinning row names the commit and the sha256 it pins.
**The second text** (Q-116b, E-146) answers the red team's read of the first (Q-116r,
`docs/reviews/DRAFT_RD-03_contract_levers_2026-11-17.md`; the first text at 153f453, LF sha256
`de551b3c829c85d8be47464045212322829affbd0cdeb5ce1befb0fd7b48f15b`), every finding as the lead adopted it; section 0.1
maps each finding to its change, and Appendix C lists the drafter's choices, each with its reason. It goes to the
gatekeeper before any pin.

**What E-023 (1) makes of it, as E-134 (1) rules it.** Each lever here changes which offered trades are routed, bought
or kept -- what is bought when a funded account ends, how many evaluations run beside the funded accounts, when a user
stops paying fees, which pricing path is bought -- and adds or removes no offered trade. Its trades are the base's
offers and its lift over the coin twin is zero by construction, so it is never an E-008 family. This file is a
**described reading**:

- it takes **no program family number** and spends **nothing** of the multiplicity budget (the next numbered family's
  k is unchanged by it);
- **no cell can carry, pass or fail**: there is no pass line, no level and no pick;
- every cell is read on the journey scorecard, for the operator to choose from the menu;
- it is declared and pinned before its run, by its own decision row with its sha256, so nothing in it is chosen after
  a look.

**When it was declared, nothing of it had been built, no solve or replay had been run for it, and no outcome of any
lever had been computed or read.** Anything chosen after a reading is exploratory and reported apart (section 17).

| field | value |
|---|---|
| reading | CL: contract-use levers on P-14's and P-16's registered trades -- Back2Funded reactivation, the evaluation inventory, house-money purchasing, and the pricing path |
| id | RD-03 (`prereg/RD-03_contract_levers.md` at the pin); every result's `prereg_id` is `RD-03` (section 15) |
| kind | a **described reading** (E-023 (1), E-134 (1)): never carried; the operator chooses from its menu |
| program family number | **none**; the next numbered family's k is unchanged by this file |
| level, pass line, pick | **none** |
| stage 0 | a solver-only fit read in Stage 2 D-666's form, of Back2Funded and of the pricing path, printed beside their rows as "the solver's view" and **deciding nothing** (section 6; E-146): no campaign, no replay, no bar read |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16, read only inside Stage 2's engine by P-14's and P-16's registered builders (this reading's own code reads no bar; the engine's reads are authorised through `extended/reader.py`, section 5 item 6) |
| the unit | one start day, replayed as U1 replays it (`vendor/stage2/docs/USER_MILESTONES.md`); each cell paired with its base on the same start |
| blocks | all starts (the menu's headline); the early block, purged per measure by `u_select.block(records, "early", h)`; the late block from 2024-01-02 (section 5) |
| cells | 2 references (identities) and **30 new cells, every one run**, each at 0 % denial with the placement off, both arms: 4 Back2Funded, 16 inventory, 8 house-money, 2 pricing-path (section 7) |
| beside | the denial ladder and the placement on for every new cell; the ten binding Focused Trader models for every inventory and Back2Funded cell, and for the Back2Funded cells a second time with each reactivation counted as a purchase; the long-run gate for every new cell; the Focused Trader models not read for the house-money and pricing-path cells, the gap named (section 13) |
| judged-block reads | four purposes, on the line of section 5 item 6; the identities from `identity/*.py` under their own row (9.1); stage 0 reads no bar |
| seeds | from 20262240 to 20262249: two in use, eight reserved; the denial ladder's start seeds and the gates' seeds inherited (section 12) |
| confirmation | none: nothing is carried (section 11) |
| `confirmation_tests_on_this_market` | 3: NQ's three of Stage 2 D-107's three are spent (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`, `held_back_2025`); this reading adds none and reads no NQ from 2026-07-17 |

---

## 0. What a contract lever changes, stated truly

A lever here leaves the **offered** trades unchanged: the same registered entries, the same outcome of each offer at
each R, the same days in the same order. So each cell is a matched pair with its base on every start day, and the
market path's luck is shared.

It does **not** leave the **executed** trades unchanged. From the first session the lever binds, these diverge and stay
diverged:

- which accounts exist: a reactivated funded account where the base buys an evaluation (Back2Funded); evaluations
  running beside five funded accounts and passes waiting for a seat (the inventory); evaluations not bought or not
  rebilled (house money);
- which account the longest-waiting router hands each later offer to, under the strict one-position rule (Stage 2
  D-429), so the sizes and R each account's table reads;
- the fees paid, by kind (subscriptions, activations, reactivations) and the payouts requested.

For P, a start's difference is nonzero only where a month's "ahead" flips, so it is lumpy. A lever that binds only
after a funded account is lost, or only once five accounts are funded, is sparse in the first months.

### 0.1 What changed from the first text (Q-116r's findings, as E-146 adopted them)

| finding | the first text | this text | where |
|---|---|---|---|
| **M1** (the lead's ruling) | stage 0's rules G-B and G-N stopped a lever's cells before any replay | **stage 0 decides nothing**: its rules weigh the table's long-run cash per account-day, not P, and a strict rule must not fail a lever that may help the user (E-051; the operator); both rules printed beside each Back2Funded and `naf` row as "the solver's view"; every cell runs; the counts restated | header; 2.1; 2.4; 6; 7.2; 10.1 item 10; 11; 13; 15; T-12 |
| **M2** | stage 0's inputs from D-666's tables re-solved at each base's bound edges, called "the table's own model" | the inputs read from **the registered policy's forward pass** at each base's own bound edge, at that policy's own cycle rate, with the read's two checks on the inputs; D-666's re-solve kept as the per-R machinery's identity and printed beside, labelled as a table no cell trades | 6.1 to 6.4 |
| **M3** | house money read at `exp_none` alone, with a count | **each house-money rule under both hold-expiry readings**, flagged (E-135): 8 cells | 2.3; 4.3 U-1; 7.2; 9.1 item 7; 9.2; 9.3; 13; T-5 |
| **M4** | 9.1 item 3 ran never-binding settings inside the identity script T-11 bars from any setting but off | **item 3 deleted**; its equalities are T-2's, T-4's, T-5's and T-13's on toys and 9.1 item 7's on the real replays | 9.1 |
| m1 | the Focused Trader models not read for the house-money and `naf` cells, the gap unnamed | not run there; the gap and its reason named on every such row and on the menu | 4.5; 10.1 items 8, 12 |
| m2 | reactivations never counted as purchases | a second Focused Trader reading on the Back2Funded cells with each reactivation counted, both labelled | 2.1; 4.3 U-6; 10.1 item 8; 13; A-1 |
| m3 | the reactivation bought the evening the seat frees under the engine's convention | bought on the evening of the breach close, trading the next session, as `back2funded_seat_count` and `back2funded_trading_from` allow | 2.1; 4.3 U-3; 8; 9.2; T-2 |
| m4 | 4.5: Back2Funded "is not account stacking ..., which no registered design does" | corrected against Stage 2 D-495 (2)-(3) | 4.5 |
| m5 | the beside rows' guard unnamed | the full guard row on every beside row; its gate entry the cell's 0 % gate, labelled | 10.1 item 8 |
| m6 | the frontier across every cell | printed without the house-money cells, and with them in a version labelled "gaming P" | 10.1 item 1; T-14 |
| m7 | four assertions missing or misworded | resets off and activation at activation asserted; Stage 2's sentinel `hold_expiry_days` never loaded; T-9 reworded | 14.2; T-4; T-9; T-15 |
| m8 | the two identities' covers undeclared | declared under Q-111's rule | 9.1 |
| n1 | -- | recorded: the first text's stage-0 outcome was fixed by rows of a vendored file no one has computed it from | 3; 6.5 |
| n2 | -- | a reactivation debits the cash and the engine's total fees together; its fee kind is one a consumer must add | 2.1; A-1 |
| n4 | -- | U-7 recorded as one conservative reading | 4.3 U-7; 8 |
| n5 | -- | a failed evaluation rebills until cancelled; every design assumes the cancel at the failure | 4.4 G-9 |
| n6 | -- | every price before sales tax, one basis throughout | 4.2 |
| the lead | the choices only in the hand-back | Appendix C: every choice the drafter made, with its reason | Appendix C |

## 1. What this reading is, and what it is not

**Its job.** It shows the operator, for each lever, each base and each month of a user's first year: how many users the
lever helps and hurts against the base, by how much, with what uncertainty, at what cost in fees, in long-run growth
and in exposure to Topstep's discretionary programs, and how much "ahead" each step of evenness costs (E-014, E-015).
The operator then chooses from that menu.

**What it is not.** A claim of an edge, a candidate, a registered design, a recommendation to buy any product, or a
design solved for any lever (the state table is the registered one throughout, section 4.4 G-1).

**First, a warning about one lever (the scout's note 3.3; E-134 (2)). House-money purchasing makes "ahead" absorbing.
Under either house-money cell, a start's path is the base's until the first close at which it is ahead, and from that
close no fee is ever paid that would take its net cash to zero or below. So at every month end its start is ahead
wherever the base's is, and on some starts where the base's is not: P cannot fall under it, on any start day, by
construction and not by merit.** Its P is therefore never read as a gain. It is labelled **"gaming P (E-134 (2))"** on
every row it appears, its P difference is printed only beside the measures it cannot game, and the menu never orders
it on P. What the reading shows of it is what that guarantee costs: the mean net, the month-6 and month-12 net, CVaR10
and the long-run gate (section 10.1 item 2), and the share of users who would have gone on to more payouts had they
kept buying.

**The same guard on every lever (E-134 (2)).** Every lever read on P is read with the mean net, the month-6 and
month-12 net, CVaR10 and the long-run gate beside it, in the same row (10.1 item 2). The menu's writer refuses to print
a P without them (T-14).

**Why described rather than tested.** E-023 (1), as E-134 (1) applies it: a lever that adds no trades is described,
never carried. The judged block's few independent three-month stretches (audit B, `docs/audits/phase0/B_objective.md`,
Q3) would leave such a lever undetectable at any numbered family's level, as the red team found for payout policy.

**What the operator's choice from the menu will mean.**

- It is recorded in its own decision row as the operator's choice from a described development reading.
- It takes no registration id and no confirmation.
- Every statement made from it is a description of the development window, in sample (section 11).
- Buying Back2Funded, an evaluation, or a pricing path is a purchase: the operator's, stated and waited for.

## 2. The levers, and the user held fixed

### 2.1 L-B: Back2Funded reactivation (the scout's rank 1)

**The product (verified, section 4.2).** A funded account (an Express Funded Account, XFA) that is closed by a rule
violation before it has taken a payout may be bought back -- "reactivated" -- within 30 calendar days of its closure,
at most twice per XFA, for $599 at 50K (`back2funded_reactivation_fee_50k`, `back2funded_max_reactivations`,
`back2funded_eligibility`, `back2funded_window_days`). The account comes back as a brand new XFA of the same size and
payout rules: balance $0, its loss limit (MLL) back at -$2,000 trailing and locking at $0, winning days and history
reset (`back2funded_account_restart`); it trades from the start of the next session after the purchase
(`back2funded_trading_from`); it does not count toward the five-account limit during the window, "until the
Reactivation fee is paid" (`back2funded_seat_count`).

**The mechanism (the scout's 3.1).** Under the registered designs about three quarters of funded accounts lose the 3R
opening and live on crippled, most ending at the loss limit unpaid (Stage 2 D-652 (1), (4)). Today that seat is
refilled by buying evaluations until one passes, then paying activation. Back2Funded refills it with one purchase: a
fresh funded account at place (c), its opening trade the table's own fresh decision, without the evaluation trades
whose mean is negative on P-14 (E-125, `results/p14_validation.csv` section `b1`).

**The user's rule (declared).** At every eligible loss, reactivate at once, up to the cell's limit:

- **eligible:** a funded account of the user's that ends by an MLL breach in the engine's sense with no payout
  requested on it in its current life (since its activation or its last reactivation), its XFA's reactivations so far
  below the cell's limit, and -- in the readings beside -- no Focused Trader placement in force (4.3 U-5);
- **when:** on the evening of the close at which the account breached -- the closed XFA stops counting toward the
  five at its closure and the reactivated one counts from its payment (`back2funded_seat_count`) -- first among that
  evening's acts, before the hold queue's activations and the evaluation purchases, so the reactivated account takes
  the lost account's seat whatever the base's own seat convention (`seat_frees`) does for other endings, and that seat
  is not refilled by an evaluation; it trades from the next session (`back2funded_trading_from`; 4.3 U-3);
- **if the cash cannot pay:** offered again each later evening while within 30 calendar days of the closure (the
  replay's session dates; 21 sessions in the gate, whose days carry no date, Stage 2's translation of 30 calendar
  days), then lapsed and counted. U1's replay is not expected to bind on cash (the premise RD-01's A-10 checks); the
  purchases and reactivations refused for cash are counted on every cell (9.3), a nonzero count printed with its rows;
- **the account:** a new instance of the base's funded class (the vendored `FundedAccount`, so the Focused Trader models
  stay readable, 10.1 item 8), with the floor at `xfa_mll_start`, balance $0, no winning days, unpaid, at the entry tier
  of `funded_scaling_plan` (4.3 U-4), on its XFA's own payout path and payout timing; routed as any funded account;
- **counted:** among the funded accounts (at most five at once, `max_active_funded_accounts`) and in the joint cap; its
  $599 in every total fee (below); its loss a funded account lost (the Focused Trader
  models' loss measure and the tier-3 pattern's breach count); **not** an evaluation purchase -- neither in the
  purchase budget (Stage 2 D-501's restraint counts Combine purchases and resets) nor in the Focused Trader models'
  purchase measure (which counts the same) -- a declared reading (4.3 U-6), with the reactivations per 21 sessions
  printed beside every row (9.3), and **beside it the conservative reading**: the Focused Trader models run a second
  time on the Back2Funded cells with each reactivation counted in their purchase measure (10.1 item 8);
- **the cash:** the $599 is debited from the campaign's cash and added to the engine's total fees together, so U1's own
  check of fees against the cash holds and P sees it; it is also recorded as a fee of its own kind (`reactivation`),
  which any consumer that sums the engine's fee kinds must add (the red team's n2).

The cells: at most once, at most twice (the verified maximum), against never (the base). **Both run** (E-146);
stage 0's reading of the lever is printed beside them as "the solver's view", deciding nothing (section 6).

### 2.2 L-I: the evaluation inventory (the scout's rank 2)

**The rules (verified).** Topstep caps active funded accounts at five (`max_active_funded_accounts`) and evaluations
not at all (`combine_count_limit`: unlimited). A pass made at the cap "goes on hold until one closes", its activation
fee paid at activation (`hold_queue_behaviour`); the passed evaluation's subscription is cancelled at the pass
(`billing_period_calendar_days` note).

**The base's own cap.** Every registered design holds at most five accounts of every kind together -- evaluations,
funded accounts and passes waiting (Stage 2 D-34: "a self-imposed cap", "a protocol parameter bounded at 5"; each
base's three seat limits as U1 replays them -- `max_concurrent_accounts`, `max_concurrent_combines` and
`max_total_accounts`, five each, read from the replay's own arguments by T-4, the build stopping and reporting if they
are not), and the engine stops
buying evaluations while a pass waits (Stage 2 D-08, `stop_buying_when_queued` True). So once crippled funded accounts
hold the seats (D-652 (3)), evaluation stops, and no pass is ready when a crippled account finally ends.

**The lever.** The joint cap lifted; the funded cap kept at five; evaluations capped at C on their own:

- **C, the evaluations running at once:** 5 -- D-34's bound kept for evaluations alone, so day 0 buys the base's five
  and the cell is the base's until its first pass -- or 7, two above it (the scout's "one or two values above", note
  section 5), so day 0 buys seven. Seat counts, fixed, no value chosen from data (Stage 2 D-620 (1)(f));
- **banking:** `on` -- evaluations are bought while passes wait for a funded seat (`stop_buying_when_queued` False) --
  or `off` -- the engine's D-08 rule, no purchase while a pass waits;
- **the hold's expiry, both readings (4.3 U-1):** `exp_none` -- a held pass waits until a seat frees, as the engine
  holds it -- and `exp_30` -- a pass not activated within 30 calendar days of the close it passed at is lost, unpaid
  and unseated (21 sessions in the gate). No official page settles which is true (`hold_expiry_days`, unstated);
  neither is chosen.

The purchase budget stays each base's own (at most 20 evaluation purchases in 21 sessions, Stage 2 D-501), so it bounds
the inventory's buying as it bounds the base's (2.6).

### 2.3 L-H: house-money purchasing once ahead (the scout's rank 3) -- **gaming P (E-134 (2))**

**The trigger.** The first close c\* at which the start's net cash -- the engine's cash less the start's initial
bankroll, which U1's net equals (payouts received less every fee paid) -- is above zero, read after that day's payout
arrivals and before that evening's activations and purchases. Before c\* the cell is the base, act for act.

**The two rules (both run):**

- **`house_stop` -- stop buying evaluations at the first ahead.** From c\*: no evaluation is bought; a running
  evaluation is not rebilled -- it is abandoned at the start of its next billing day, before that day trades, which is
  cancelling it at the last close before the rebill (`combine_cancellation`; 4.3 U-2); a pass is activated only if its
  activation fee leaves net cash above zero, and otherwise waits on hold until it does; funded accounts trade on and
  request payouts as P-14's.
- **`house_zero` -- no fee that crosses zero.** From c\*: every fee -- an evaluation purchase, a rebill, an
  activation -- is paid only if net cash after it is above zero. A purchase that would not is not made at that step
  (and is re-read at every later step); a rebill that would not abandons its evaluation at its billing day, as above; an
  activation that would not waits on hold until it can be paid.

**Why "ahead" is absorbing under both.** After c\*, payouts only add to net cash and every fee paid leaves it above zero,
so net cash is above zero at every later close. A start ahead at a month end under the base is either ahead before c\*
(impossible: c\* is the first) or at or after it, where the cell is ahead too. Checked on every start and month as an
oracle (9.2).

Both run on each base's own seats, budget and payout rule, with Back2Funded off. A pass waiting for cash relies on the
hold's expiry, which no page states (`hold_expiry_days`), so **each house-money rule runs under both of U-1's
readings**, `exp_none` and `exp_30` -- four cells on each base, eight in all -- and its rows carry U-1's flag (E-135; the red team's M3: the only
number on record, 30 days to pay the activation with fewer than five active XFAs, names exactly this below-the-cap
case). Absorption is unaffected: a pass lost under `exp_30` pays no fee.

### 2.4 L-N: the pricing path (the scout's rank 4) -- read at the fit and replayed

Topstep sells two evaluation paths at 50K, chosen at purchase and never changed: Standard ($49 a month, $149
activation, $49 reset) and No Activation Fee ($95 a month, $0 activation, $95 reset) (`subscription_fee`,
`activation_fee`, `subscription_fee_naf_50k`, `activation_fee_naf_50k`, `reset_fee_naf_50k`). Stage 2 called the path
"a protocol dimension, not a constant" (D-25) and parked it (D-276); it was never run. **Stage 0 reads it at the fit (rule
G-N, section 6), beside and deciding nothing; the cell `naf` replays each base** with the No Activation Fee prices and
nothing else changed -- the registered (Standard-solved) table, labelled first-order (4.4 G-1); no reset is bought, so its reset
price is moot.

### 2.5 Not here, and why

- **Resets (the scout's rank 5) -- excluded, an adapter owed first.** Topstep's reset pushes the rebill date out
  thirty days from the reset's purchase (`reset_rebill_push`, 8284128); the vendored engine's reset keeps the
  subscription's billing dates unchanged (`vendor/stage2/propedge/campaign/lockstep.py` 377-379; Stage 2 D-146). Every
  registered design runs with resets off, so nothing registered rests on the difference (E-135), but a reset lever read
  on the engine as it stands would bill a resetting campaign on the wrong dates. **A reset reading needs an adapter in
  `extended/` for the billing date, with its own identity, before it can be declared.** Here every cell runs with
  `reset_failed_combines` False, as every registered design; the Reset Bank's credits (`reset_credit_per_rebill`,
  `reset_credit_expiry`) are therefore moot.
- **The daily loss limit at checkout**, and Back2Funded's $50 discount that comes with it (`back2funded_dll_discount`):
  the $1,000 daily limit stays with the account for life and "cuts the table's $2,000 bold plays" (Stage 2 D-320 (2)),
  so a DLL account is a different account from the one the table was solved for; it belongs with a re-solved table
  (the scout's rank 6), not here. `dll_offer_status`'s doubled caps never bind on these tables (D-652 (4)).
- **Back2Funded under the No Activation Fee path:** neither page states whether the price differs
  (`back2funded_fee_by_pricing_path`, unstated); the two levers are not crossed.
- **Crossing the levers with each other** (Back2Funded with the inventory or with house money): each lever is read
  alone against its base; a composite is a later declaration citing this one.
- **The purchase budget off**: read by Stage 2's family 1 on P-14's trades (D-634); lifting it here would mix two
  levers.
- **A journey-solved or Consistency-path table, roles and staggered starts, a session filter, closing a crippled
  account at request** (the scout's ranks 6 to 9): a sizing design, a campaign option, an E-023 (2) filter, and an
  unverified rule (`xfa_closure_at_request`) respectively; none is a contract-use lever on the registered table.
- **Family O (F-03) and reading PP (RD-02):** no cell here uses F-03's waiting rule or RD-02's payout levers; every cell
  trades the registered opening and requests as P-14 does. A reactivated account is a "newly funded account" in F-03's
  sense; F-03's text must say whether that is so before any composite (the scout's 3.1).

### 2.6 The user, held fixed across the cells

- **The trades.** P-14's registered trades (A3-BRK30-CB20, U1's own builder) and P-16's (`rc_s150_all_nr`,
  `rc150_dev_test.TRADES_SHA256`), each with its own registered state table (`state_dp_e-0.050_lamstar_noclose`,
  checked against `a3_brk30_cb20.NOCLOSE_POLICIES_SHA256`; not re-solved), protocol and routing (the longest-waiting
  account, one position at a time across the firm with five minutes flat, Stage 2 D-429).
- **The seats and purchases.** Each base's own as U1 replays it -- five funded, five evaluations, five in all; the
  purchase budget of at most 20 evaluation purchases in 21 sessions; a failed evaluation replaced by a new purchase --
  except where the inventory cells change the evaluation and joint caps and the banking rule (2.2), and the house-money
  cells withhold fees (2.3).
- **The payout rule.** P-14's: the maximum, min(50 % of the balance, $2,000), at the first eligible close and at every
  eligible close after (reading PP's `ref`); Aeropay, $0, three trading days; the request after 5:00 PM CT (Stage 2
  D-175).
- **The path.** Standard, except the conditional `naf` cell.
- **No resets** (2.5). **No DLL election.**
- **Hand entry**, at least five minutes from alert to order (E-008); one user's own accounts at one firm.
- **Conduct.** Tier 1 untouched (4.5). Tier 2: the Responsible Trading Program's placement off in the headline (Stage 2
  D-289), on beside. Tier 3: the denial ladder and the binding Focused Trader models beside (10.1 item 8).

## 3. Prior exposure: what has already read these levers, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| Stage 2 D-34, D-08 | the self-imposed cap of five accounts including evaluations; no purchase while a pass waits | -- | operating policy; D-34's conduct caveat: purchases per year reported beside growth for any protocol replacing evaluations continuously | the inventory lifts both; the caveat is carried (10.1 item 7) |
| Stage 2 program U families 1 and 3 (D-634, D-635, D-638; `results/u_seats.csv`) | a looser purchase budget; one to four seats, all three caps together | start days, both blocks | closed; fewer accounts lowered P and every measure but the cash (D-638) | seats were read only downwards and together; the evaluation cap alone, above five funded, never |
| Stage 2 program U family 5 (D-643, D-651; `results/u_firms.csv`) | Lucid seats beside Topstep's five, from day 0 or after the first payout | start days, both blocks | closed; more seats from day 0 raised the cash before the first payout and lowered P -- "more seats are more evaluations bought early" (D-651 (2)) | **the nearest evidence against the inventory on P**; the C = 5 cells keep the base's day 0 for that reason |
| Stage 2 D-630, D-637 (wallet stop); D-620 (1)(a) (quit rules Q1, Q2) | stops on the losing side; quit rules as assumptions | start days | closed (wallet stop); assumptions, not measurements (quit rules) | no row reads a stop on the winning side; house money is the first |
| Stage 2 U2 (D-652; `results/u_xfa_day_budget.csv`) | what happens to a funded account after its opening | 100 gate paths a design | about three quarters lose the opening and live crippled, few paid (D-652 (1)-(4)) | the accounts Back2Funded acts on; the file was not opened by the drafter |
| Stage 2 D-664 | crippled accounts resolved at once | start days | closed: "every ended account is a fresh evaluation bought" | the cost Back2Funded would replace |
| Stage 2 U4 (D-666, D-667; `vendor/stage2/results/u_size_fit.csv`) | the account-size fit read: each size's contract solved under each base's table, at each base's bound edge and at zero | no campaign; registered bounds | account size closed at the fit | **the first text's stage-0 inputs were rows of this file** (sections `reading` and `rent`, size `50k`): an attempt's P(pass), fees, a fresh funded account's payouts and days, and lambda\*. **Neither the drafter nor the red team has opened it**; the scout's note did not either (its 3.1, 4). In this text stage 0 decides nothing, its headline inputs come from the registered policy's forward pass (on no file), and the file's rows serve only as the per-R machinery's identity (6.4) and the beside readings (6.1 (c)); see 6.5 |
| Stage 2 D-25, D-276 | the No Activation Fee path | -- | "a protocol dimension", parked, never run | none read |
| Stage 2 D-146, D-549 | the engine's reset; the operator's rule against buying and blowing an account the same day | -- | the reset off in every design; the D-549 rule held by the engine's timing | resets excluded (2.5); D-549's rule checked (9.3) |
| Stage 2 D-495, D-497 (Stage 2's `results/ftp_sweep.csv`, not vendored; P-14's gate, section `ftp` as `vendor/stage2/scripts/a3_brk30_cb20.py` describes it) | the Focused Trader Program as swept models on the gate | gate paths | thresholds unpublished; read beside, never the gate | the ten binding models carried, beside (10.1 item 8) |
| Q-44 (this repository; `results/user_beside.csv`, `results/user_beside_starts.csv`) | the bases' replays under the ladder, the placement and the ten Focused Trader models | all starts | queued, not run at this text; not on master | the references' readings beside are checked against its per-start rows (9.1 item 6) |
| RD-01, RD-02 (pinned) | other firms' contracts; payout policy | all starts | not run at this text; no result on master | the same references; neither reads these levers, and this reading reads none of their cells |
| U1 (Stage 2 D-620) and Q-05's identity (E-010) | P-14's and P-16's own journeys, every start | all starts | the reference rows | the references are known in full; only the cells are new |
| program U's nine families | P on the late block against P-14 | starts from 2024 | all closed | the late block has been read for P nine times: late development, not out of sample |

**The verdict arm's bound reads both blocks** (reading PP's N2). The verdict arm shifts every R's outcomes to each
base's registered one-sided bound, estimated on the whole development window (`vendor/stage2/prereg/P-14_a3-brk30-cb20.md`);
so an early-block reading on the verdict arm is a function of 2024-2026 through that one constant. It shifts both
members of every pair alike and no purge removes it. Stage 0's bound edges are the same constants.

**The drafter's own reads (disclosed).** The scout's note (whole); `CHARTER.md` sections 1-4; `DECISIONS.md` E-007,
E-008, E-023, E-104, E-117, E-119, E-125, E-134, E-135; Q-115's record at deb45ad (`config/rules_extended.yaml`, its
Q-115 entries; `docs/RULES_CURRENCY.md`, its Q-115 rows); Stage 2's ledger values and statuses for the keys of
Appendix R; Stage 2's decision rows D-08, D-25, D-34, D-146, D-495, D-497, D-549, D-620, D-634 to D-638, D-651,
D-652, D-664, D-666 and D-667 (which state the outcomes quoted above, in words); RD-01 and RD-02 (whole, for form);
code only: `lockstep.py`'s path signature, docstring, class checks and its end-of-day steps (purchase, hold queue,
reset, seat freeing), `customer_slices.engine_args` and `replay`, the headers of `vendor/stage2/propedge/research/u_size_fit.py`
and `vendor/stage2/scripts/u_size_fit.py` and its `attempt_readings`, `extended/campaign.py`'s header,
`extended/user_beside.py`'s header, `run_starts` signature and `replay`, `extended/gate.py`'s keywords,
`extended/identity_tokens.py` and `extended/identity_cover.py` (headers), `extended/reader.py`'s purpose rules, and the
function names of `extended/pp_reading.py`. **No result file of either repository was opened**: the vendored results
folder was listed by name only. One disclosure: a first, not word-bounded form of the seed search (section 12) printed
digit fragments from inside two result files (`vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`,
`results/calibration_two_sample.csv`); no column, row or value of either was read as a result, and neither bears on
any lever here.

**What is already known of the direction (disclosed).** More evaluations bought early cost P (D-651 (2)); fewer
accounts cost P too (D-638); the funded accounts Back2Funded acts on are rarely paid without it (D-652). Nothing is
known of any of the four levers themselves on the journey.

## 4. The rules: the verified record, the unstated terms and their readings

### 4.1 Where the rules come from, and the merge that comes first

Every rule a cell leans on comes from Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`, vendored under
E-002) or from this repository's record (`config/rules_extended.yaml`, `docs/RULES_CURRENCY.md`). **The keys this
reading adds -- Back2Funded's, the No Activation Fee 50K prices, the hold's expiry, the evaluation's cancellation, the
Reset Bank's -- are Q-115's (the rules-verifier, official pages read 2026-11-16), committed on `wt/wt-firms` at deb45ad
and not yet on master (E-135).** Each is cited below by its key. **Their merge comes before RD-03's run** (E-134 defers
it until RD-01's and RD-02's readings have used the identities held without it): the merge writes under `config/`,
which every identity's cover includes (E-117, `extended/identity_cover.py` `BASE`), so after it every shared identity
is held again at a commit containing it before anything of this reading runs (15, waits). Every value is loaded by a
loader that refuses an entry not `verified` (14.2); an `unstated` key is never loaded -- its gap is read by a rule of
4.3.

### 4.2 Every term the levers touch

| key | source | status (date read) | value | used for |
|---|---|---|---|---|
| `back2funded_reactivation_fee_50k` | record (deb45ad) | verified (2026-11-16) | $599, before sales tax; final | L-B's price |
| `back2funded_max_reactivations` | record (deb45ad) | verified (2026-11-16) | 2 per XFA | L-B's limit; the cells' 1 and 2 |
| `back2funded_eligibility` | record (deb45ad) | verified (2026-11-16) | earned through the Combine; closed by a rule violation before a payout; on TopstepX; in good standing; none after a payout; none on the Focused Trader Plan | L-B's eligibility (U-5, U-7) |
| `back2funded_window_days` | record (deb45ad) | verified (2026-11-16) | 30 calendar days from closure | L-B's window |
| `back2funded_trading_from` | record (deb45ad) | verified (2026-11-16) | from the start of the next trading session after the purchase | L-B's timing (U-3) |
| `back2funded_seat_count` | record (deb45ad) | verified (2026-11-16) | the closed XFA does not count toward the five during the window, until the fee is paid; buying at five active not addressed | L-B's seat (U-3) |
| `back2funded_account_restart` | record (deb45ad) | verified (2026-11-16) | same size and payout rules; balance, P&L, history, winning days reset; MLL back to -$2,000, trailing, locking at $0 | the reactivated account (U-4) |
| `back2funded_fee_by_pricing_path` | record (deb45ad) | unstated (2026-11-16) | -- | why L-B and L-N are not crossed (2.5) |
| `back2funded_dll_discount` | record (deb45ad) | verified (2026-11-16) | $50 off with a DLL kept for life | not used (2.5) |
| `subscription_fee_naf_50k` | record (deb45ad) | verified (2026-11-16) | $95 a month | L-N |
| `activation_fee_naf_50k` | record (deb45ad) | verified (2026-11-16) | $0 | L-N |
| `reset_fee_naf_50k` | record (deb45ad) | verified (2026-11-16) | $95 | moot (no resets) |
| `hold_expiry_days` | record (deb45ad); stage2 | unstated (2026-11-16); stage2 `verified`, value the design sentinel `not_required_under_d34` (2026-09-22) | -- | L-I's two readings (U-1) |
| `combine_cancellation` | record (deb45ad) | verified (2026-11-16) | from the Billing page; final; an active Combine rebills every 30 days until cancelled | L-H's withheld rebill (U-2) |
| `combine_cancellation_account_effect` | record (deb45ad) | unstated (2026-11-16) | -- | L-H cancels only at the last close before a rebill (U-2) |
| `reset_rebill_push` | record (deb45ad) | verified (2026-11-16) | a reset pushes the rebill 30 days out from its purchase; conflicts with the engine | why resets are excluded (2.5) |
| `reset_credit_per_rebill`, `reset_credit_expiry` | record (deb45ad) | verified (2026-11-16) | one credit per rebill; a year's expiry | moot (no resets) |
| `subscription_fee` | stage2 | verified (2026-11-14) | $49 | the Standard path |
| `activation_fee` | stage2 | verified (2026-11-14) | $149 | the Standard path |
| `reset_fee` | stage2 | verified (2026-11-14) | $49 | moot (no resets) |
| `billing_days`, `billing_period_calendar_days` | stage2 | verified (2026-11-14) | 21 sessions; 30 calendar days | rebills; the 30-day translations (U-1, U-8) |
| `combine_count_limit` | stage2 | verified (2026-10-30) | unlimited | L-I |
| `max_active_funded_accounts` | stage2 | verified (2026-10-03) | 5 | the funded cap; L-B's seat |
| `hold_queue_behaviour` | stage2 | verified (2026-11-14) | a pass at the cap waits until a seat frees; activation paid at activation | L-I; L-H's waiting pass |
| `xfa_activation_latency` | stage2 | verified (2026-10-10) | minutes | activation the evening a seat frees |
| `xfa_seat_frees_at` | stage2 | **unverified_human_input_required** (2026-10-30) | -- | never loaded: the engine's next-session convention, the pessimistic end (U-3) |
| `account_start_rate_limit` | stage2 | verified (2026-11-14) | none stated | no limit on purchases a day invented |
| `xfa_mll_start`, `xfa_lock_at` | stage2 | verified (2026-11-14) | -$2,000 trailing; locks at $0 | every funded account, a reactivated one included |
| `funded_scaling_plan`, `scaling_tier_after_payout` | stage2 | verified (2026-10-03) | the ladder by balance; the tier follows the balance | every funded account (U-4) |
| `payout_max_frac_of_balance`, `xfa_std_cap`, `payout_min`, `profit_split`, `xfa_std_winning_days`, `xfa_std_winning_day_min`, `require_profit_since_payout` | stage2 | verified (2026-11-14) | 0.5; $2,000; $125; 0.9; 5 days of $150; true | P-14's payout rule, every cell |
| `payout_after_request_survives_mll_breach` | stage2 | verified (2026-10-30) | true | a requested payout is taken: no reactivation after it (U-7) |
| `payout_fee`, `payout_lag_days_aeropay` | stage2 | verified (2026-11-14) | $0; 3 trading days | the method |
| `focused_trader_program` | stage2 | verified (2026-10-30) | the program; Slowdown bars "B2F Reactivations"; no threshold published | the ten models beside; U-5 |
| `responsible_trading_program` | stage2 | verified (2026-10-30) | the placement | `rtp` beside |
| `tou_s8_relative_position_size` | record (master) | verified (2026-11-15) | Terms of Use s.8 | tier 3, priced by the ladder (E-013 (1)) |

**Every price is before sales tax** ("Prices exclude sales tax", `back2funded_reactivation_fee_50k`'s record): the
reactivation's, the evaluation's and the activation's alike, one basis throughout (the red team's n6). Appendix R
lists every key with its record; T-0 holds the table to its sources.

### 4.3 Unstated or unverified terms, each read by a rule fixed now

- **U-1. The hold's expiry** (`hold_expiry_days`, unstated; the record's note asks for both readings and "which is the
  base"). Both are run on every inventory cell, and **neither is the base of a cell**: the cell pairs against the
  registered base, which holds no pass. `exp_none` is the engine's reading (a held pass waits); `exp_30` the strict
  reading: 30 calendar days from the close the pass was made at, whether or not the user is at the cap (the search
  summary's "30 days from passing ... to pay your Activation Fee" is on no official page read, and is the only
  sentence that names a number). In the gate 30 calendar days are 21 sessions (`billing_days` against
  `billing_period_calendar_days`, Stage 2's translation), the gate rows labelled. Where a cell's two readings lie on
  opposite sides of its base on P, or on any guarded measure, the menu flags it **"depends on the hold's expiry"**.
  House-money cells, which hold a pass only for want of cash -- below the cap, the case the search summary's sentence
  names -- run at both readings too (2.3), flagged the same way.
- **U-2. What cancelling an evaluation does to the account** (`combine_cancellation_account_effect`, unstated). House
  money cancels only at the last close before a rebill -- an evaluation it would not trade again -- so under either
  reading (closes at once; trades to the end of the paid period) it loses nothing it has paid for. Modelled as the
  engine's abandonment at the start of the billing day, before that day trades (Stage 2 D-08's form).
- **U-3. When a reactivated account trades** (`back2funded_trading_from` and `back2funded_seat_count` verified;
  `xfa_seat_frees_at`, which is about the general seat, unverified; buying a reactivation while five others are active,
  not addressed). The reactivation is bought on the evening of the breach close and trades from the next session: the
  closed XFA stops counting at its closure and the reactivated one counts from its payment, so the two verified keys
  allow it (the red team's m3), and the engine's next-session convention for other seats does not delay it. This
  assumes the purchase is made after the end-of-day closure and before the 17:00 CT reopening; bought later, the
  account trades a session later (12060405's example), and every Back2Funded row is labelled **"bought before the
  17:00 CT reopening"**. A reactivation never makes a sixth active funded account: it takes the lost account's seat,
  so the at-five case never arises.
- **U-4. The reactivated account's scaling tier** (unstated; "same as a brand new XFA" and "Everything resets to zero:
  balance", `back2funded_account_restart`): the entry tier of `funded_scaling_plan`, a reading, labelled on every
  Back2Funded row.
- **U-5. Back2Funded under the Focused Trader Program** (`back2funded_eligibility`: "Traders on the Focused Trader Plan
  (FTP) cannot use Back2Funded"; `focused_trader_program`: the Slowdown Path bars "B2F Reactivations"). In the
  readings beside, no reactivation is bought while a Slowdown or Corrective placement is in force, and an account
  closed by the Corrective placement is never eligible.
- **U-6. Whether a reactivation counts as a purchase** in the self-imposed budget and in the Focused Trader models'
  purchase measure: no (both count "Combine purchases and resets", Stage 2 D-497, D-501); its loss does count among
  funded accounts lost. Declared, labelled "not counted: the optimistic reading" on every Back2Funded row, the
  reactivations per 21 sessions printed beside. **Beside it, the conservative reading** (the red team's m2): the
  Back2Funded cells' ten Focused Trader models run a second time with each reactivation counted in the purchase
  measure (the Corrective Path names "Excessive recycling of Trading Combines or XFAs"), labelled "reactivations counted
  as purchases: the conservative reading"; the purchase budget still counts evaluations only, as registered.
- **U-7. "Closed due to a rule violation before taking a Payout."** An MLL breach is the designs' case (8284204: "Your
  account is permanently closed."). A payout **requested** is taken (`payout_after_request_survives_mll_breach`: a
  request before a breach is still paid), so an account with a request in its current life is not eligible. Not
  eligible either: an account closed by the funded horizon (the gate's 504 sessions), by a tier-3 denial (the ladder,
  beside: a discretionary review, not a rule violation, and a payout was requested), by a household or forfeiture
  closure, or by a Focused Trader placement. "In good standing with no compliance concerns" is read as true at 0 %
  denial. **This is one conservative reading of "before taking a Payout"** (the red team's n4): the other -- a request
  not yet paid at the breach not counted as taken -- would raise Back2Funded's supply slightly, and is not run.
- **U-8. A rule no page states is not invented:** no limit on evaluations bought a day (`account_start_rate_limit`,
  none stated); no limit on passes held at once; no cap on reactivations in a window beyond two per XFA.

### 4.4 What is not modelled, listed as gaps

| id | gap | how it is shown |
|---|---|---|
| G-1 | the state table was solved without Back2Funded, with D-34's joint cap, without a stop rule and at Standard prices (Stage 2 D-329, D-501): every cell reads the table as registered | every row labelled **first-order, the table fixed**; a re-solve per lever is a new sizing design (2.5) |
| G-2 | the reactivation's session (U-3), the scaling tier (U-4), the purchase count (U-6) | readings, each labelled on its rows |
| G-3 | the hold's expiry (U-1) | both readings run; the flag |
| G-4 | the user's time: more accounts, more hand entries a session (E-015 (5)) | counted, not modelled (9.3: accounts live at once, trades a session across accounts) |
| G-5 | the Focused Trader thresholds: unpublished (`focused_trader_program`) | the ten binding swept models beside (D-497 (3)), never a verdict |
| G-6 | the Live Funded Account move; payouts unavailable in holiday hours; Topstep's unstated news rules (E-034) | as in every registered row; the holiday-hours reach and the FOMC-minutes count printed (9.3) |
| G-7 | resets and the Reset Bank (2.5) | excluded; an adapter owed first |
| G-8 | rule changes over 2020-2026 | today's terms on every start, as Stage 2 replays Topstep's current rules |
| G-9 | a failed evaluation keeps rebilling until the user cancels it (`combine_cancellation`; 8284121: an active Combine "Rebills every 30 days" until cancelled); the engine, as every registered design, ends its billing at the failure -- the user assumed to cancel at once (the red team's n5) | common to the base and every cell; stated, not modelled |

### 4.5 Conduct

- **Tier 1, untouched.** No lever hedges across accounts or firms, copies one trade across accounts, exploits a
  simulator's fills, sizes into major news or conceals a pattern: every account trades its own routed trades, one
  position at a time across the firm (Stage 2 D-429), as registered. Back2Funded is a product sold for this use and
  nothing about it is hidden. **The designs' money already comes through the pattern Topstep names as account
  stacking** (10305426: "Repeatedly trading aggressively, hitting the Maximum Loss Limit (MLL) in one account, then
  switching to another account and repeating"; Stage 2 D-495 (2)-(3): FV3-C's and family A3's leaders draw nearly all
  their payouts through it, and P-14 is an A3 design), priced at tier 3 (D-145); **Back2Funded repeats it on the same
  XFA and so raises that exposure**, which the ladder's stacking test (two breaches in 21 sessions) and the Focused
  Trader models price beside (the red team's m4).
- **Tier 2.** The Responsible Trading Program's placement off in the headline (Stage 2 D-289), on beside (`rtp`).
- **Tier 3, priced, never a ban (Stage 2 D-145).** The verdict stays at 0 % denial with the placement off (E-008 (2)).
  The payout-denial ladder (10, 25, 50 %), carrying Terms of Use s.8 (E-013 (1)), is beside every cell. **The ten
  binding Focused Trader models are beside every inventory cell and every Back2Funded cell**: Topstep's pages name
  "Excessive Resets and Trading Combine purchases", "Activating and losing many Express Funded Accounts in a short
  period of time" and "Excessive recycling of Trading Combines or XFAs" (Stage 2 D-495 (2)) -- exactly what those two
  levers lean on. **Not read under the models: the house-money and `naf` cells** -- house money equals its base
  before its trigger and withholds purchases after it, and `naf` buys exactly its base's evaluations on the same paths,
  only the fees differing -- a gap named on every such row and on the menu, "Focused Trader models not read" with this
  reason (the red team's m1; 100 replays not run).
- **Stage 2 D-549's operating rule** (never buy or reset an evaluation and blow it the same trading day) is held by the
  engine's evening purchases and next-session trading, and extended to reactivations (they trade from the next
  session); checked on every cell (9.3), a nonzero count an engine error.
- **Stage 2 D-34's caveat**: purchases per year -- evaluations and reactivations -- printed beside growth on every row
  (10.1 item 7).

## 5. Data, blocks, the unit and the horizons

1. **The unit** is U1's: one development start day, a fresh (unbound) bankroll and fresh accounts, the base's trades
   replayed in historical order, a long replay of up to 252 sessions plus U1's exact-length runs (21, 63, 90, 126)
   (`vendor/stage2/scripts/user_journey.py`, `customer_slices.replay`), made through Q-17's adapter
   (`extended.user_beside.run_starts`) and this reading's path (14.1). `USER_MILESTONES.md`'s definitions unchanged. A
   month is 21 sessions. **The starts:** every start U1 reads for `p14` and `p16` (`vendor/stage2/results/user_journey.csv`,
   section `start`), each reading on the starts with its horizon h left.
2. **The arms.** `verdict` (every R at its registered bound) the headline; `point` beside (N2, section 3).
3. **Pairing.** Each cell and its base on the same start days, blocks and seeds; the per-start difference is the unit of
   every paired reading.
4. **The blocks, per measure.** Every reading at its measure's horizon h on: **all starts** with h sessions left
   (`u_select.block(records, None, h)`), the headline; **the early block** (`u_select.block(records, "early", h)`: the
   starts of 2023 and before, less every start within h sessions of 2023's last; no early reading touches a 2024
   session except through the verdict arm's bound); **the late block** (`u_select.block(records, "late", h)`: from
   2024-01-02, h left). Nothing is chosen on any block; they are read apart so the menu can flag a lever whose effect
   changes sign between them (10.1 item 12). By start year: means only, not purged, labelled so.

   **Each measure's horizon** (reading PP's 5 item 3, carried; `u_select.MEASURES`, Q-17's `FIRST_WINDOW` 126 and
   `YEAR_WINDOW` 252):

   | measure | h |
   |---|---|
   | S3a | 21 |
   | P; the shares ahead at months 1-3; S3c; S5a; the mean net at months 1-3; CVaR10 of the month-3 net; P under a bankroll limit | 63 |
   | S1; S3b; S4a; S5b; S5c; the month-6 net and its CVaR10; sessions and cash to the first pass and to the first payout; S2, S3d, Q | 126 |
   | the share ahead and the net at month 9 | 189 |
   | S4b; the month-12 net and its CVaR10; sessions to break-even and the share that later falls back; the deepest fall after break-even; the twelve-month evenness measures | 252 |
   | a share at month m (broken even by m; better / equal / worse) | 63 for m up to 3, else 21 m |
   | every count of 9.3 at its stated horizon; every reading beside at its measure's own h | as stated |

5. **No NQ from 2026-07-17** is on disk or read.
6. **The judged block's seal (E-026, E-041).** Stage 2's engine reads the bars and the atlas itself in the U1 replay and
   in the gate, so the runner authorises those reads with `extended.reader.authorise_engine_read` before the engine
   runs, from a clean checkout of a committed commit, under the purposes on this line:

   - **Judged-block reads:** `levers_scorecard`, `levers_gate_beside`, `levers_ladder_beside`, `levers_ftp_beside`

   - `levers_scorecard`: the replays at 0 % denial with the placement off -- the references and every new cell, both
     arms;
   - `levers_gate_beside`: the gates beside (10.1 item 9);
   - `levers_ladder_beside`: the replays under the denial ladder and the placement on (10.1 item 8);
   - `levers_ftp_beside`: the replays under the ten Focused Trader models (10.1 item 8).

   None is a choosing or fitting purpose (the reader's `CHOICE_WORDS`; T-0). The identities run from `identity/*.py`
   under the purpose `identity` and their own decision row, never under this line (9.1). **Stage 0 reads no bar and no
   atlas** -- only the registered files of 6.1 -- so it needs no purpose; if the build finds that any part of it reads
   a bar, it stops and reports, and stage 0 needs a new declaration.

## 6. Stage 0: the solver-only fit read (Stage 2 D-666's form) -- beside, deciding nothing

**What it is for, and what it is not (the lead's ruling, E-146, on the red team's M1).** Two levers have a price that
the state table's own model can weigh against the evaluation route without a replay: Back2Funded ($599 for a fresh
funded account) and the pricing path ($95 a month and no activation against $49 and $149). Stage 0 computes that
weighing and **prints it beside each Back2Funded and `naf` row, labelled "the solver's view". It decides nothing: no
cell waits on its outcome, and every cell of section 7 runs.** Its rules measure the table's long-run cash per
account-day -- G-B is the exact one-step policy-improvement test for adding reactivation to the no-closure model, the
red team found -- not P, the share of starts ahead at months 1 to 3; a synthetic journey in the red team's read shows
G-B stopping a reactivation that raises P, and its toy of G-N shows G-N and P disagreeing. A stop on the wrong measure
would fail a lever that may help the user, which E-051 and the operator's instruction (a strict rule must show power,
not only caution) do not allow.

### 6.1 What is computed (fixed now)

For each base (P-14 on its 12.5- and 25-point rungs; P-16 on its 37.5-point stop) and each edge set (`bound`: each R
at the base's registered one-sided 0.05 bound, the gate's `lb_by_rr`; `zero`), at $50K only:

- **(a) the registered policy, evaluated (the red team's M2, its first remedy, taken because it is cheap):** the table
  every cell trades, `state_dp_e-0.050_lamstar_noclose`, is re-solved at FV3-C's single edge as 6.4 item 1 holds it
  equal to the file; its policy arrays are then propagated forward -- `forward` on Stage 2's `FundedByR` and
  `CombineByR` built at the base's per-R edges, the policy held to the registered one in every state -- giving that
  policy's own forward summaries at those edges and **its own cycle rate**, the rent at which its fresh evaluation is
  worth zero: `lambda_pi = (p W - F_acc) / (D + p T)`, with D the evaluation's mean days per attempt and F_acc the
  table-accrual fees per attempt (6.2). A policy evaluation, not a solve: a few forward passes per base and edge set;
- **(b) the No Activation Fee path, the same policy:** (a)'s summaries re-priced exactly -- the engine-billed
  subscriptions per attempt at $95 instead of $49 (`subscription_fee_naf_50k`), the activation at $0
  (`activation_fee_naf_50k`), the payouts unchanged -- as the `naf` cells trade the registered table;
- **(c) beside, labelled "D-666's re-solved bound-edge table, not the table the cells trade":** D-666's own solve at
  each base's per-R bound edges (its lambda\* and the tie-broken table at it), at Standard prices and at No Activation
  Fee prices (`rules_for_method('aeropay')` with the two No Activation Fee prices and `reset_fee_naf_50k` as
  overrides), its readings and the same two rules printed for comparison only. The Standard solve is also 6.4 item 2's
  identity of the per-R machinery (a) relies on.

Inputs, registered files, each checked against its manifest: `vendor/stage2/config/state_policy_v12.yaml`; the bases'
registered gate files' `edge`, `rung` and `resolution` rows (`vendor/stage2/results/a3_brk30_cb20_gate.csv`,
`vendor/stage2/results/rc_s150_all_gate.csv`, with `vendor/stage2/results/rc_width_screen.csv` for P-16's rung, as the
vendored runner builds it); `vendor/stage2/results/state_policy_v12_noclose.csv` and
`state_policy_v12_noclose_policies.json`; and, for 6.4, `vendor/stage2/results/u_size_fit.csv`. One worker, an exact
chain: no seed.

**The vendored runner cannot be run whole in this snapshot.** `vendor/stage2/scripts/u_size_fit.py` also requires
D-559's `results/rc150_table_screen.csv` and `rc150_table_screen_policies.json` (its lines 102-103, 183-187, 313-316,
411-428: a check of P-16's rung and the one-rung table's identity), and neither is in the vendored snapshot (searched,
2026-11-16). So stage 0's driver (A-5) imports the module's pieces (`propedge.research.u_size_fit`, `state_policy`)
and composes the runner's steps without those two files: P-16's rung is built from its gate's rows as the runner
builds it, and checked instead against `u_size_fit.csv`'s own `rungs` rows for `p16` (6.4); D-559's one-rung table
identity is not run (its file is absent), and the table on file's identity (6.4 item 1) stands for the solver. If the
pieces cannot be composed without the two files, or the registered policy's arrays cannot be held in the per-R classes'
forward pass without editing the vendored code, the build stops and reports; stage 0 does not fall back.

### 6.2 The readings, per base and edge set, and the read's two checks

From (a): an attempt's P(pass) `p`; the engine-billed subscriptions per attempt `S` (dollars, so `S / 49` of them); the
fees per attempt `F = S + 149 p` and on the table's own accrual `F_acc`; the evaluation's mean days per attempt `D`; a
fresh funded account's expected net payouts `W` and expected days `T`; the policy's own rate `lambda_pi`; the sessions
per pass (`D / p`); payouts per fee dollar. From (b): the same with `F_N = (95 / 49) S`. From (c): its lambda\* and the
same readings. The zero-edge, fee-free oracles first (P(pass) at most 2/5 and stage one's supremum 0.327131; a fresh
funded account's expected gross payouts at most $2,000): **a value outside is an engine error, never a finding**, and
stage 0 stops (stage 0 alone; no cell depends on it).

**The read's two checks on the inputs (the red team's M2), refusing, at each base and edge set:** (i) `W - lambda_pi x
T` equals the funded table's fresh value under the registered policy at the rent `lambda_pi`, to 1e-6; (ii) the
evaluation's fresh value under that policy at `lambda_pi` is zero, to 1e-6 -- and for (c), the same two at its lambda\*,
to the fixed point's tolerance. Both hold by construction; a failure shows the inputs mismatched, and stage 0 writes
nothing but the failure's lines.

### 6.3 The solver's view: two rules, printed beside, deciding nothing

- **G-B, Back2Funded.** A reactivated account is a fresh funded account (`back2funded_account_restart`). It holds its
  seat for `T` days on average and pays `W`; for those days the seat earns no rent from the evaluation route, which
  pays `lambda_pi` per slot-day under the registered policy's own model. Printed per base, beside every Back2Funded
  row: the two sides, `W - lambda_pi x T` and $599 (`back2funded_reactivation_fee_50k`), and the line **"the solver's
  view: under the registered table's model at this base's bound edge, a reactivation does [not] pay back its price
  beyond what the seat would have earned on the evaluation route meanwhile -- a long-run cash measure, not P"**.
  Beside it: `W - 599`; the scout's fee comparison, the route's fees per pass `F / p` against $599; the sessions per
  pass; and (c)'s same rule, labelled.
- **G-N, the pricing path.** Printed per base, beside every `naf` row: the payouts per fee dollar of the No Activation
  Fee path with the registered policy, `p W / F_N`, against the Standard path's, `p W / F` (the measure Stage 2 D-657
  ties to P across designs, and D-666's), and the line **"the solver's view: the No Activation Fee path's mean fee per
  attempt is [lower / not lower] than Standard's under the registered table's model -- a fee measure, not P"**. Beside
  it: (c)'s lambda\* and payouts per fee dollar at both prices, labelled.

Neither line is a stop, a flag or an order: no menu row is moved by them, and the menu prints them beside, never above,
the replay's readings. Stage 0 writes the two sides of each and its line, computed by its code (`results/cl_fit.csv`,
sections `checks` and `solver_view`).

### 6.4 Stage 0's identity, refusing

Run first, as part of `identity/cl_fit_identity.py` (the runner's label `cl_fit_identity`), from a clean checkout,
under the purpose `identity` and its own row: (1) the $50K solve at FV3-C's single edge reproduces
`state_dp_e-0.050_lamstar_noclose` (the whole exported tree but its description; its rent to 1e-9), as D-667 (2)
held -- the policy (a) then evaluates; (2) the per-R machinery: each base's rungs, offers and edges equal the `50k` rows
of `vendor/stage2/results/u_size_fit.csv`, sections `rungs` and `edge`, and at each base and edge set (c)'s Standard
solve reproduces its `50k` rows, sections `reading` and `rent`, to 1e-9; (3) the zero-edge oracles hold. **Any
failure: nothing of stage 0 is computed further or written but the failure's lines**; the failure protocol applies.
A failure stops stage 0's view; it does not stop the reading's cells, which wait only on their own identities (9.1).

### 6.5 What was fixed before this text (the red team's n1)

In the first text, (a) was D-666's re-solve, whose readings are rows of `vendor/stage2/results/u_size_fit.csv`
(sections `reading` and `rent`, size `50k`), written and read by Stage 2 (D-667). So that text's stage-0 outcome -- its
two stops -- was already fixed by a vendored file, computable by anyone who opened it. **No one has computed either rule
from it**: the drafter and the red team both left it unopened, and the pinning row records that. In this text stage 0
decides nothing, its headline inputs come from the registered policy's forward pass, which is on no file, and the
file's rows serve only (c) and 6.4's identity.

## 7. The cells and the runs

### 7.1 The references

`ref` on P-14 and `ref` on P-16: each base as registered, through this reading's path with every option off. They must
reproduce U1's start rows (9.1), and every new cell pairs against its base's `ref`.

### 7.2 The grid

| cell | lever | settings | on P-14 | on P-16 |
|---|---|---|---|---|
| `ref` | -- | as registered | reference (identity) | reference (identity) |
| `b2f1` | L-B | at most one reactivation per XFA | new | new |
| `b2f2` | L-B | at most two (the verified maximum) | new | new |
| `inv5_bank_none` | L-I | C = 5, banking on, `exp_none` | new | new |
| `inv5_bank_30` | L-I | C = 5, banking on, `exp_30` | new | new |
| `inv5_hold_none` | L-I | C = 5, banking off, `exp_none` | new | new |
| `inv5_hold_30` | L-I | C = 5, banking off, `exp_30` | new | new |
| `inv7_bank_none` | L-I | C = 7, banking on, `exp_none` | new | new |
| `inv7_bank_30` | L-I | C = 7, banking on, `exp_30` | new | new |
| `inv7_hold_none` | L-I | C = 7, banking off, `exp_none` | new | new |
| `inv7_hold_30` | L-I | C = 7, banking off, `exp_30` | new | new |
| `house_stop_none` | L-H | stop buying evaluations at the first ahead, `exp_none` | new, **gaming P** | new, **gaming P** |
| `house_stop_30` | L-H | stop buying evaluations at the first ahead, `exp_30` | new, **gaming P** | new, **gaming P** |
| `house_zero_none` | L-H | no fee that crosses zero, `exp_none` | new, **gaming P** | new, **gaming P** |
| `house_zero_30` | L-H | no fee that crosses zero, `exp_30` | new, **gaming P** | new, **gaming P** |
| `naf` | L-N | the No Activation Fee prices | new | new |

Every inventory cell has the funded cap 5 and no joint cap. **Every cell runs** (E-146): stage 0's view is printed
beside the Back2Funded and `naf` rows and decides none of them. Each cell runs both arms, every start, the long replay
and U1's exact-length runs, at 0 % denial with the placement off.

### 7.3 Each lever's own comparisons (beside the pair with its base)

- L-B: `b2f1` against `ref`; `b2f2` against `b2f1` (the second reactivation alone).
- L-I: each against `ref`; within L-I, C = 7 against C = 5, banking on against off and `exp_30` against `exp_none`, each
  at the other two settings fixed.
- L-H: each against `ref`; `house_zero` against `house_stop` at each expiry reading; `exp_30` against `exp_none` for
  each rule.
- L-N: `naf` against `ref`.

These are further paired readings on the same starts, read in 10.1 items 4 and 5 like every pair; none is a pick.

## 8. Parameters: fixed, described, both readings, dropped

"Described" means every value listed is run and read and the program chooses none; the operator chooses from the menu.
"Both readings" means a term the pages leave open, read at the two readings 4.3 fixes. **Searched: none.**

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| trades | what is traded | fixed | P-14's and P-16's registered trades | E-010; D-513; D-544 |
| state table | sizing by account state | fixed | `state_dp_e-0.050_lamstar_noclose`, not re-solved | D-501; G-1 |
| payout rule | when and how much is requested | fixed | P-14's (RD-02's `ref`) | 2.6 |
| seats, budget, routing | accounts and purchases | fixed, except L-I | each base's own: 5 / 5 / 5; 20 in 21 sessions; the strict one-position rule | D-34; D-501; D-429 |
| **reactivations per XFA** | L-B | **described** | 0 (base), 1, 2 | `back2funded_max_reactivations` |
| reactivation timing | when it is bought and trades | fixed (a reading) | the evening of the breach close, first, before the 17:00 CT reopening; trades from the next session | U-3 |
| reactivation price | L-B | fixed | $599 | `back2funded_reactivation_fee_50k` |
| reactivation counting | budget and Focused Trader purchase measure | fixed (a reading), with a second reading beside | not counted (the headline and the optimistic reading); counted in the Focused Trader purchase measure in a second reading beside (the conservative one); its loss counted in both | U-6 |
| a requested, unpaid payout at a breach | Back2Funded's eligibility | fixed (one conservative reading) | taken: the account is not eligible | U-7 |
| reactivated tier | the scaling tier | fixed (a reading) | the entry tier | U-4 |
| **evaluation cap C** | L-I | **described** | 5, 7 | D-34's bound; the scout's note section 5 |
| funded cap | L-I | fixed | 5 | `max_active_funded_accounts` |
| joint cap | L-I | fixed | none in L-I (the base's 5 elsewhere) | `combine_count_limit` |
| **banking** | L-I | **described** | on, off | D-08 |
| **the hold's expiry** | L-I and L-H | **both readings** | `exp_none`, `exp_30` (30 calendar days; 21 sessions in the gate) | U-1 |
| **house-money rule** | L-H | **described** | `house_stop`, `house_zero` | 2.3 |
| the trigger | L-H | fixed | the first close with net cash above zero, after arrivals, before the evening's fees | 2.3 |
| cancellation | L-H | fixed (a reading) | abandonment at the billing day, before it trades | U-2 |
| **pricing path** | L-N | **described** | Standard (base), No Activation Fee | 2.4 |
| stage 0's rules | the solver's view, beside | fixed; deciding nothing | G-B, G-N on the registered policy's evaluation (6.1 (a), 6.3) | 6; E-146 |
| resets | buying a reset | fixed | none | 2.5 |
| arms | outcome shift | fixed | `verdict` the headline, `point` beside | CHARTER section 2 |
| denial, placement | firm discretion | fixed | 0 % and the placement off in the headline; the ladder and `rtp` beside | E-008; D-234; D-289 |
| Focused Trader models | beside L-I and L-B; not L-H or L-N (the gap named) | fixed | Q-17's ten (`extended.user_beside.FTP_BINDING`); on L-B twice (U-6) | D-497; E-007 (e); 4.5 |
| horizons, blocks | replay length; starts read | fixed | U1's; 5's table; all, early, late | D-620; D-621 (4)(b) |
| the interval | uncertainty | fixed | 10.2 | E-058 (5); RD-02 9.2 |
| the readings beside: arm and exact runs | where E-007 (e)'s readings are read | fixed | the verdict arm; exact-length runs on every 21st start index (`EXACT_EVERY`), their differing count printed | Q-17; E-024 |

**Dropped, and why.** Resets, the DLL, Back2Funded under No Activation Fee, crossings, the budget off and ranks 6-9
(2.5); a third inventory value (two seat counts and two banking rules cover "beside the funded" and "more than the
base"; a third is a later reading); a reactivation delayed within the window (no reason to wait under an unbound
bankroll, and a delay is a timing design); the house-money trigger at a dollar threshold above zero (a value chosen
from nothing); Lucid or another firm (RD-01's).

## 9. Before any reading: identities, oracles, mechanics

### 9.1 The identities, refusing (E-004, E-010; whole-window identities only from `identity/*.py`, E-026, E-041)

**Shared, owed by other items; this reading waits for each, re-held after Q-115's merge (4.1).** A wait is met only by a
decision row whose third cell begins with the token `identity-holds: <id>` (E-104's positional form, parsed by
`extended/identity_tokens.py`), at the run's commit or an ancestor, with the identity's cover unchanged since
(`extended/identity_cover.py`'s `cover(id)`, never less):

- Q-05 (E-010): U1's start rows reproduced (`identity/stage2_identity.py`);
- Q-80 (E-049): `extended/gate.py` through the re-composed campaign, P-14's and P-16's registered gate paths at 500
  paths, every arm;
- Q-93 with Q-100 (E-059 (1)): U1's start rows through Q-17's adapter, with a declared class and Q-100's seams;
- Q-101 (E-068): U1's start rows with the replay recorder on.

**This reading's own, run first from `identity/cl_identity.py` (label `cl_identity`)**, from a clean checkout of the
reading's commit, under the purpose `identity` and the row that registers it (the lead's), never under the
`Judged-block reads:` line. **The script runs the reference only:** every lever option is a constant at its off value,
no argument selects a lever, a cell or a price, and before its first start and path it asserts every option off and
refuses otherwise (T-11). It must reproduce, through this reading's path (14.1 A-1) with every option off:

1. **P-14's registered gate paths**, `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, `gate` run, 0 % denial,
   point and bound, through `extended/gate.py` with A-3, every `zero_edge_decomposition.PATH_COLS` column to 1e-6, all
   500 paths, at seed 20261131; **and P-16's**, `vendor/stage2/results/rc_s150_all_gate_paths.csv` at seed 20261206,
   after its trades' hash;
2. **U1's start rows for P-14 and P-16**, through `extended.user_beside.run_starts` with A-2 and the response `off`:
   `vendor/stage2/results/user_journey.csv` section `start`, configs `p14` and `p16`, both arms, every start, every
   column as E-010 compared them (money and the ratio to 1e-6; counts, days, dates and text exactly), with U1's own
   checks of every run's payouts and fees against the engine's totals;
3. *(Deleted in the second text, the red team's M4: it ran never-binding settings inside the script T-11 bars from any
   setting but off. The equalities it sought are T-2's, T-4's, T-5's and T-13's on toy campaigns, and 9.1 item 7's on
   the real replays.)*

**Stage 0's identity** is 6.4's (`identity/cl_fit_identity.py`), held in its own row before stage 0 runs.

**The two identities' covers (the red team's m8), declared under Q-111's rule** (`extended/identity_cover.py`, E-119).
Each is `BASE` -- `extended/__init__.py`, the folder `config/` whole (E-117) and both vendored manifests,
`vendor/MANIFEST_stage2.sha256` and `vendor/DATA_MANIFEST_stage2.sha256` -- plus its own script
(`identity/cl_identity.py`; `identity/cl_fit_identity.py`) and every repository file the script imports, directly or
transitively, as `identity_cover.imports(script)` computes it (among them A-1 to A-6's modules, Q-17's adapter
`extended/user_beside.py`, `extended/gate.py`, `extended/campaign.py` and the replay recorder). The reading's waits on
its own two tokens use those covers, never less; T-0 holds each equal to `BASE` plus its script's computed closure,
as `tests/test_identity_cover.py` holds the shared ones. A change to any covered file after a token re-requires that
identity.

**Inside the reading's own run, on its own replays (no further read):**

4. **The options are off in `ref`**, by the path's own counters (14.1): no reactivation, no expiry, no house-money
   refusal, no queue; and `ref`'s start rows equal U1's again (item 2's comparison, refusing).
5. **The trades are the base's**, by Q-94's replay recorder (its per-start check that every routed trade is in the
   start's blocks): every trade any new cell's account takes is one of its base's registered offered trades. Checked for
   every new cell, both arms, before anything of it is read.
6. **The readings beside, at `ref`:** `ref` under `denial_10`, `denial_25`, `denial_50`, `rtp` and the ten `ftp_*`
   responses, verdict arm, equals Q-44's `results/user_beside_starts.csv` for the same design, arm and response, start
   for start, every column that file writes, at its precision (money to the cent), read as text (E-098 (R4)). The draws
   are the same (section 12).
7. **Each lever before it binds:** a house-money cell equals its base on every act before its trigger, on every start;
   a Back2Funded cell equals its base before its first eligible loss; a C = 5 inventory cell equals its base before its
   first pass; the two expiry readings of an inventory or house-money cell are equal on every start where no pass waits
   30 calendar days. Refusing.

**The order, and what a failure leaves.** `ref` first in every step of section 15 (items 2's repeat and 4 in step 3;
item 6 at the start of steps 4 and 5); then each new cell in section 15's order, checked under items 5 and 7 before
anything of it is read. Any failure stops the reading: **nothing of a new
cell is computed, written or printed**; the failure protocol applies; nothing is rerun until it passes, and a rerun is a
further judged read under `repeat=` (15). E-010's negative controls (the verdict rows against the point rows; a 2e-6
nudge) show that the comparisons are not vacuous.

### 9.2 Oracles (an output outside them is an engine error, never a finding)

- On every cell's zero-edge twin in the gate: the mean gross payouts per funded account -- a reactivated account
  counted as an account -- do not exceed $2,000 beyond its Monte Carlo interval; the pass rate per evaluation does not
  exceed 2/5 beyond its interval (propsim D-02).
- **Back2Funded:** every reactivation is of an eligible account (4.3 U-7), within its XFA's limit, at $599, bought on
  the evening of its breach close and trading from the next session, debited from the cash and the total fees together, never making a sixth active funded account, never under
  a Focused Trader placement.
- **The inventory:** never more than five funded accounts active or C evaluations running; the budget never exceeded;
  under `exp_30` no pass activated more than 30 calendar days after its pass (21 sessions in the gate).
- **House money:** after the trigger no fee leaves net cash at or below zero; under `house_stop` no evaluation bought
  after it; **on every start and at every month end, the cell's start is ahead wherever its base's is** (the
  construction of 2.3); under `exp_30` no house-money pass activated more than 30 calendar days after its pass (21
  sessions in the gate).
- **The pricing path:** every evaluation fee is $95 a cycle and every activation $0 in `naf`.
- Every request is at most min(50 % of the balance, $2,000) and at least $125, paid at 90 % less the method's fee.

### 9.3 The mechanics, printed first

For each new cell and block, before any paired outcome measure. They describe where a lever binds, not whether it helps;
each names its source (the path's counters, 14.1; the engine's records; Q-94's recorder):

- **every cell:** the share of starts on which it differs from its base at all within 63, 126 and 252 sessions; the
  evaluations bought, activations and reactivations bought per year (D-34's caveat); the largest number of accounts live
  at once and of trades in one session across the user's accounts (G-4); the purchases, activations and reactivations
  refused for cash (the replay's bankroll premise); the D-549 check -- accounts bought (or
  reactivated) and breached on the same trading day -- which must be zero; **the holiday-hours reach** (requests made at a
  session that closes early, or the last session before a scheduled holiday, by E-029's pinned calendar
  `config/calendar_early_closes.csv`, LF sha256 `72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2`,
  the engine's own `payout_days`); **an unnamed release** (per stream, the offered trades open at 13:00 CT on a day of
  E-050's pinned calendar `config/calendar_fomc_minutes.csv`, LF sha256
  `0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7`, and per cell how many of them were executed at the
  tier's full allowance -- Back2Funded makes more fresh openings at the full allowance -- Q-94's recorder; a count,
  never a ruling);
- **L-B:** the eligible losses per start (the supply), by first and later life; reactivations bought per start, by
  first and second; those refused, and why (limit, cash, placement); the sessions from the loss to the reactivated
  account's first trade; the reactivated accounts' fates (won the opening; paid; lost again before a payout); the most
  reactivations in any 21 sessions, beside the Focused Trader models' thresholds;
- **L-I:** the sessions with five funded accounts and evaluations running; the passes that waited for a seat, the peak
  queue and the waits in calendar days (median, p90, max); the passes lost under `exp_30`; the evaluations bought beyond
  the base's; the purchases the budget refused;
- **L-H:** the share of starts that reach the trigger by sessions 21, 63, 126 and 252, and the trigger's session
  (median, p10, p90); the purchases withheld, the evaluations abandoned at a rebill, the passes that waited for cash and
  how long, and under `exp_30` those lost; the starts whose base
  later falls back below zero, which the cell keeps ahead by construction;
- **L-N:** the fees by kind against the base's.

A cell identical to its base on every start is reported as **"no effect on these trades"**, and nothing more is read for
it.

## 10. The reading: the journey scorecard and the menu (CHARTER sections 2-3; E-008, E-014, E-015, E-023, E-134)

### 10.1 What is read

Every cell and its base, both arms (the verdict arm the headline), every block of section 5; the readings beside on the
verdict arm. The replay at 0 % draws nothing.

1. **The scorecard.** P, S1 to S5c, S2, S3d, S6 and Q, as `USER_MILESTONES.md` defines them; the frontier on P, S1,
   S3a and S5a across each base's cells, printed without the house-money cells and, beside it, with them, that version
   labelled "gaming P (E-134 (2))" (the red team's m6). S3c is comparable across a base's cells, which share one trade stream (E-008's
   condition).
2. **The guard row (E-134 (2)), printed with every P.** In the same row as each P and each paired difference in P: the
   mean net at months 1, 2 and 3; the month-6 and month-12 net (mean, p10, p50, p90); CVaR10 (the mean of the lowest
   tenth of starts) of the month-3, month-6 and month-12 net; and the long-run gate's growth on the required bankroll at
   the bound with its ruin probability (item 9). House-money rows carry the label **"gaming P (E-134 (2))"** and their
   P is printed only in this row, never ordered.
3. **E-014's journey variables:** sessions and cash to the first pass and to the first payout; sessions to break-even
   (the first session cumulative net cash is at or above zero, daily), the share reaching it by months 1, 2, 3, 6 and
   12, and the share that later falls back below zero (zero by construction under house money: labelled); the path's
   evenness -- the share of months with a positive net change, the longest run of months without a payout, the spread
   of monthly net, the deepest fall of cumulative net from its running high after break-even, payouts per month, the
   largest single month's share of the year's payouts.
4. **Each measure as a distribution over start days** (median, p10, p90) with its uncertainty (10.2), and the start
   day's share of the variance across each lever's cells (S6's form).
5. **The paired readings, by month: who is helped, who is hurt.** For every measure of items 1 to 3, cell less base (and
   for 7.3's own comparisons): the per-start difference (p10, p50, p90); the shares of starts better, equal and worse
   at months 1, 2, 3, 6, 9 and 12 (for the share ahead: ahead under the cell and not the base, under both, under neither,
   under the base and not the cell); the mean difference with 10.2's interval, its window count and its minimum
   detectable difference.
6. **What diverges.** Per cell, against its base: funded accounts activated, reactivated and lost; evaluations bought,
   abandoned and passed; passes waiting and lost; fees by kind; payouts' count and size; trades taken and their realised
   risk (the share within Stage 2 D-212 (1)'s line in P-14's allowance-capped form, E-022 (1)).
7. **D-34's caveat:** purchases per year (evaluations and reactivations) beside growth, every row.
8. **E-007 (e)'s readings beside**, through Q-17's adapter, verdict arm, U1's exact-length runs on every 21st start index
   (`EXACT_EVERY`), their differing count printed:
   - **the denial ladder** (`denial_10`, `denial_25`, `denial_50`), every new cell: the engine's tier-3 model, one
     uniform per exposed payout from each start's path seed, Q-17's `lockstep.child_seed(20261920, 0, start_day)` as
     `run_starts` draws it -- common to every cell, its base and Q-44's reading of the base; the draws line up across
     cells only until their exposed payouts diverge, which is the lever's effect, and the ladder's ordering of the cells
     is printed beside the 0 % headline's;
   - **the placement on** (`rtp`, the gate's strictest reading), every new cell; a reactivated account keeps its XFA's
     path and its daily loss limit (`back2funded_account_restart`: "the same ... Payout rules");
   - **the ten binding Focused Trader models** (`ftp_*`), **every inventory cell and every Back2Funded cell**, on the
     vendored funded class (the path re-composed, the class not subclassed, so the engine admits them); Back2Funded
     barred under a placement (U-5); a reactivation not counted in the purchase measure and its loss counted; **on the
     Back2Funded cells a second time with each reactivation counted in the purchase measure** (U-6), the two labelled
     "not counted: the optimistic reading" and "counted: the conservative reading"; printed per model: P, the guard
     row, the share of starts placed and when, purchases refused, accounts closed; **not read for the house-money and
     `naf` cells**, "Focused Trader models not read" and its reason on their rows (4.5);
   - **on every beside row, the full guard row (item 2)** -- the mean net at months 1 to 3, the month-6 and month-12 net,
     CVaR10 at months 3, 6 and 12 -- with P by month, P under a bankroll limit, the effective sample size and the MDD.
     The guard row's gate entry on a beside row is the cell's 0 % gate (item 9), labelled "the gate at 0 %", since no
     gate is run under a beside response (the red team's m5).
9. **The long-run gate beside, every new cell:** at its base's registered seed (P-14's 20261131, P-16's 20261206), 500
   paths, point and bound, with its zero-edge twin, paired with the base's registered gate paths, through
   `extended/gate.py` with A-3; rows: growth on the required bankroll, the required bankroll, the ruin probability,
   payouts a month, days to the first payout, purchases a year. It shows the trade-off between a user's first months
   and two-year growth. **Nothing is a floor: nothing is carried.** In the gate Back2Funded's window and the 30-day
   expiry run on 21 sessions (no dates), each row labelled.
10. **Stage 0's readings beside** each Back2Funded and `naf` row (6.2, 6.3), labelled **"the solver's view"**: the
    registered table's long-run cash and fee measures at each base's bound edge, deciding nothing, never ordering or
    flagging a row; (c)'s re-solved readings beside them, labelled as a table no cell trades.
11. **The evenness trade-off.** Each lever's cells as points of "ahead" against each evenness measure, in E-015's menu
    form -- house money's labelled.
12. **The menu.**
    - **What it shows.** Each cell's scorecard, guard row and paired readings; all starts the headline, the early and
      late blocks and the start years beside.
    - **The flags, mechanical, never lines:** **"not stable across blocks"** (a mean paired difference in P, or in any
      guarded measure, of opposite signs on the early and late blocks); **"depends on the hold's expiry"** (U-1);
      **"gaming P (E-134 (2))"** on every house-money row; **"first-order, the table fixed"** on every row (G-1); the
      readings of U-3 ("bought before the 17:00 CT reopening"), U-4 and U-6 on every Back2Funded row; **"Focused Trader
      models not read"** on every house-money and `naf` row (4.5).
    - **E-015's limits** flag the menu only if approved before the reading's run commit, by a row of the `e015-limits:`
      form (E-104); a limit approved later is applied only in a re-reading labelled exploratory (its own row,
      `exploratory=True`). With none approved by then, the menu says so.
    - **How many intervals, and what chance alone gives.** The menu prints the number of 90 % intervals it shows, that
      each is marginal and none simultaneous, and the count expected to exclude zero by chance alone were there no
      effect anywhere -- a tenth of them. A count, not a level.
13. **Not modelled, and said so wherever this scorecard appears:** a user who stops when their own money runs out (except
    as house money declares it), the user's time, taxes; payouts unavailable in holiday hours; the move to a Live
    Funded Account; Topstep's unstated news rules (E-034); the gaps of 4.4.

### 10.2 The uncertainty on each paired reading (fixed now)

These are descriptions, not tests: nothing is compared with a critical value to decide anything, and no reading has a
level (E-023 (1), E-025). **The method is reading PP's section 9.2, items 1 to 7, unchanged** (`prereg/RD-02_payout_policy.md`,
pinned; built in `extended/pp_reading.py`, imported, never copied), with this reading's own seed for its honesty
series:

1. **The windows (E-058 (5)).** At horizon h on a block, the starts in order are cut into consecutive windows of h
   starts from the block's first (a last incomplete window dropped), and every other window is kept, from the first, so
   no two kept windows share a session; n_w printed with every reading. Only items 2, 3 and 5 rest on them.
2. **The interval:** two-sided 90 %, Student t on the n_w kept windows' means, n_w - 1 degrees of freedom, printed only
   when n_w is at least 4 and the means are not all equal; else "too few separated windows for an interval".
3. **The window sign count**, always printed.
4. **The effective sample size**, Bartlett, lag window h (`extended.user_measures.n_eff_bartlett`), beside.
5. **The minimum detectable difference:** (t(0.95; n_w - 1) + t(0.80; n_w - 1)) times the kept windows' standard error,
   printed beside each mean and before it.
6. **A series zero on every start** prints "identical on these trades"; one whose kept means are all equal prints its
   sign count alone.
7. **The interval's honesty, beside, on overlapping series:** RD-02 9.2 item 7's 21 shapes (gauss, ahead, paired; nine
   lumpy; nine persistent) and construction, 20,000 series per setting, at every (h, n_w) at which this reading prints
   an interval (n_w from the block's start count, dates only); **seed 20262240**, each setting drawing from
   `numpy.random.default_rng([20262240, 1, shape, h, n_w])`, the build's test from `[20262240, 0, ...]`, never these
   keys. **The label:** "under-covers at this window count" where the lowest coverage of gauss, ahead and paired at its
   (h, n_w) is below 0.88; beside every interval, with no threshold, the lowest lumpy or persistent coverage, its shape
   and its misses above and below ("if the difference is rare and lumpy") -- the line that matters most here, since a
   lever that binds only after a lost funded account is exactly such a difference.

## 11. What the reading delivers, and what each outcome means

- **It delivers** stage 0's fit read and the menu of section 10: what four contract-use levers do to a user's journey on
  P-14's and P-16's registered trades and table, with what each costs in fees, growth and exposure.
- **It does not deliver** a carried design, a registration id, a confirmation, a claim at a level, or a recommendation
  to buy anything (E-023 (1)).
- **No outcome passes or fails.** What follows from each, fixed now:
  - an identity fails (9.1, 6.4): the reading (or stage 0) stops; the failure protocol applies;
  - an oracle is breached (9.2, 6.2): an engine error; the reading stops;
  - stage 0's two rules come out either way (6.3): printed beside as the solver's view, deciding nothing; no cell
    waits on them;
  - a cell identical to its base: "no effect on these trades";
  - a cell's two expiry readings (an inventory or house-money cell) straddle its base: flagged; the operator's browser read or Topstep's written answer
    would settle it (16); **no run is repeated to settle it**;
  - house money shows a higher P: expected by construction, never a gain; what is read is its guard row.
- **The operator's choice** is recorded in its own row, citing this reading's files (E-015: limits first, then the best
  inside them). **It is an in-sample choice** over the development window, with no confirmation (E-023 (1)); the menu
  says so beside it. Any purchase it implies is the operator's.
- **No confirmation.** Nothing is carried, so NQ from 2026-07-17 is not touched.
- **The binding.** The blocks read here are recorded as read for contract-use levers on P-14 and P-16, all of them. A
  later reading of any of these levers names this one, states what changed, and reads no block of it as fresh.

## 12. Seeds, fixed now and checked

| seed | status | what it draws |
|---|---|---|
| 20262240 | in use | 10.2 item 7's honesty series (keys `[20262240, 1, shape, h, n_w]`) and the build's test of it (keys `[20262240, 0, ...]`) |
| 20262241 | in use | the build's toy campaigns (T-1 to T-5, T-7, T-10, T-12, T-13, T-15) and T-3's synthetic late block |
| 20262242 | reserved, unused | -- |
| 20262243 | reserved, unused | -- |
| 20262244 | reserved, unused | -- |
| 20262245 | reserved, unused | -- |
| 20262246 | reserved, unused | -- |
| 20262247 | reserved, unused | -- |
| 20262248 | reserved, unused | -- |
| 20262249 | reserved, unused | -- |

**Stage 0 draws nothing** (an exact chain). **The replays at 0 % draw nothing.**

**The check, 2026-11-16 (the machine clock), on this text.** Three word-bounded searches for `2026224[0-9]`, every file
type, code and tests included, the licensed data excluded:

- `git grep -IwnoE "2026224[0-9]" <ref>` on every local and remote ref of the repository (23 refs), the vendored
  snapshot and its results included;
- `grep -rIownE --exclude-dir=.git --exclude-dir=data "2026224[0-9]"` on the working files of the main tree, of every
  worktree under `%LOCALAPPDATA%\stage2-extended-wt\` and of every clean-run checkout under
  `%LOCALAPPDATA%\stage2-extended-runs\`, before this file was written.

They found the block nowhere. After this text is committed they find it in this file alone. The block lies outside the
range 20262000 to 20262199 that Q-82's and Q-108's tests scan. The build's T-9 repeats the check on its commit; T-0
repeats it, in its own scope, on every run.

**Inherited, and used only as their owners registered them:** P-14's gate seed 20261131 and P-16's 20261206, for the
gates beside (paired with the registered paths) and the identity; the denial ladder's start seeds, Q-17's
`lockstep.child_seed(20261920, 0, start_day)` (`extended.user_beside.start_seed`, E-024), as `run_starts` draws them --
no keyword takes another seed, so `ref`'s ladder rows reproduce Q-44's (9.1 item 6); U1's replay seeds, as U1 passes
them.

## 13. Counting and the budget

1. **No program family number and no level** (E-023 (1)). The next numbered family's k is what it would be without this
   file.
2. **Stage 0:** per base and edge set, (a) one policy evaluation (a few forward passes) with the read's two checks and
   (b) its exact re-pricing; (c) one solve at Standard prices and one at No Activation Fee prices, beside: **4 policy
   evaluations and 8 solves** (2 bases x 2 edge sets), plus the identity's solve of the table on file (6.4). No replay,
   no cell, no decision.
3. **The cells at 0 % with the placement off, both arms, every one run:** 2 references (counted as identities) + 4
   Back2Funded + 16 inventory + 8 house money + 2 `naf` = **32 replays; 30 new cells.**
4. **Beside, labelled, verdict arm:**
   - the denial ladder and the placement on: 4 x 30 = **120 replays**, plus `ref`'s 8 checks against Q-44 (9.1 item 6);
   - the ten Focused Trader models: 10 x (16 inventory + 4 Back2Funded) = **200 replays**, and the Back2Funded cells'
     counted reading, 10 x 4 = **40 replays**, plus `ref`'s 20 checks against Q-44; not read for the 8 house-money and
     2 `naf` cells (100 replays not run, the gap named, 4.5);
   - in all **360 replays beside and 28 reference checks**;
   - the gates: one per new cell, **30 gates** (500 paths, point and bound, zero-edge twin); the references' gates are
     9.1's identities.
5. **The honesty series:** synthetic, no read.
6. **Every block read** is recorded as read for contract-use levers (11).
7. **Nothing is selected by the program.** The operator's menu choice is a choice among described readings, recorded
   in its own row with the menu it was made from.

## 14. The build: adapters, identities and tests

### 14.1 The adapters (in `extended/`, never in `vendor/`)

Every adapter wraps or re-composes a vendored seam; none edits `vendor/` and none substitutes a vendored attribute
during a call (E-011, Q-47). **If any cannot be built that way, the build stops and reports; this declaration does not
fall back.**

| id | adapter | what it adds |
|---|---|---|
| A-1 | the path, re-composed (`extended/levers_path.py`) | `lockstep.simulate_lockstep_path`'s text copied verbatim, in Q-71's pattern (`extended/campaign.py`): a guard refusing unless the vendored function's LF source hashes to its pin; a proof that the function with its marked lines removed parses to the vendored one statement for statement; and **marked additions only**, each off by default: (a) the reactivation step of 2.1 in the end-of-day seat step, with the Focused Trader bar (U-5); (b) the hold's expiry (U-1) in the hold queue; (c) the house-money fee rule (2.3) at every fee -- the evening purchases, the activations and the start-of-day billing; (d) a counters channel carrying the counts of 9.3 out of every path, off by default, every output equal with it off and on; (e) the Focused Trader purchase measure's counting of reactivations, a marked option for U-6's conservative reading. A reactivation debits the cash and the engine's `total_fees` together (n2). Every helper imported from the vendored module; the vendored `FundedAccount` and `CombineAccount` used unchanged |
| A-2 | the replay through A-1 (`extended/user_beside.py`, generic keywords in Q-100's form) | `run_starts(..., levers=L)` sends the adapter's own `replay` to A-1 with the options `L`, and puts the seat keywords (`max_concurrent_combines`, `max_total_accounts`, `stop_buying_when_queued`) and the path's `subscription` and `activation` (A-4) on every replay's path; absent, every task, replay and output is the adapter's before it bit for bit; with it, the Focused Trader models stay admitted (the class is the vendored one); with the recorder (Q-94) and the counters (A-1 (d)) composed |
| A-3 | the gate through A-1 (`extended/gate.py`, `extended/campaign.py`) | `run_gate(..., levers=L, stop_buying_when_queued=...)`: the re-composed campaign's path runner (Q-70's `path_runner` pattern) calls A-1 with `L`; the seat and price keywords passed through; absent, the gate as before, held by Q-80's identity |
| A-4 | the No Activation Fee prices | the path's `subscription` and `activation` set from `subscription_fee_naf_50k` and `activation_fee_naf_50k` by the loader of 14.2, in the replay and the gate; nothing else changed |
| A-5 | stage 0 (`extended/levers_fit.py`, `scripts/cl_fit.py`, `identity/cl_fit_identity.py`) | Stage 2's `u_size_fit` and `state_policy` pieces at `50k`, imported; (a)'s evaluation of the registered policy at each base's per-R edges and its own rate, with the read's two checks; (b)'s re-pricing; (c)'s solves at both prices; the solver's-view lines of 6.3, connected to no cell; `results/cl_fit.csv` |
| A-6 | the reading (`extended/cl_reading.py`, `scripts/cl_reading.py`, `identity/cl_identity.py`) | the cells of section 7 in section 15's order; 9.1's checks; 9.3's mechanics; 10.1's readings by RD-02's functions (`extended/pp_reading.py`, imported); the menu and its flags; the waits by `extended/identity_tokens.py` and `extended/identity_cover.py` |

### 14.2 The rules in code

Every value of section 4.2 is read by a loader that refuses an entry not `verified` (Stage 2's ledger through its own
loader; `config/rules_extended.yaml` as RD-01's loader reads it), parsing a value stated in text fail-loud. A test fails
on any literal of a rule value -- 599, 2 as the reactivation limit, 30 as a window or expiry, 95, 49, 149, 5 as a cap --
in the adapters outside comments; the readings of 4.3 come from one table of named constants, each citing its line of
4.3. **Stage 2's `hold_expiry_days` is `verified` with the design sentinel `not_required_under_d34`**, which is not a
reading of any page: the loader names it as never loaded and a test holds that (the red team's m7 (b)); the record's
`hold_expiry_days` is `unstated` and never loaded either.

### 14.3 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 (before the pin) | `tests/test_rd03_draft.py`: the pin-time form (the `id` and `confirmation_tests_on_this_market` rows; no draft-form status; both calendars cited by their LF sha256); one `Judged-block reads:` line, its four purposes parsed by `extended.reader.declared_purposes`, none choosing, none `identity` or `registered_design`; section 12 holds 20262240..20262249 once each and they appear in no other file of the repository (vendored snapshot, reviews and audits included); Appendix R cites every key with its record's status, read from the merged record (or, before the merge, from deb45ad's blob); no level in 10.2; the cell counts of section 13 equal section 7's grid; the two identities' covers equal `BASE` plus their scripts' import closure (9.1); Appendix C present; the reader end to end on this text pinned in a temporary tree |
| T-1 | A-1 with every option off equals the vendored path bit for bit on toy campaigns (seed 20262241), every reduction and recorder row; its guard refuses a changed vendored source; its recomposition proof |
| T-2 | L-B on toy campaigns: eligibility (a breach before any request; none after a request, a horizon closure, a denial's closure, a household or Focused Trader closure); the limit per XFA at 1 and 2 across lives; the price from the record; bought on the evening of the breach close whatever the base's seat convention, before the queue and the purchases, trading from the next session; the cash and the total fees debited together; the counted reading's purchase measure counting each reactivation; never a sixth funded account; lapse after 30 calendar days (21 sessions in the gate) when the cash cannot pay; barred under a placement; the account restarted (balance $0, floor -$2,000, no winning days, the entry tier, its path); counted as funded and lost, not as a purchase |
| T-3 | every early-block reading at horizon h is byte-identical when every session from 2024-01-02 on is replaced (seed 20262241), for every h of section 5's table, with the verdict arm's bound held at its registered constant |
| T-4 | L-I: each base's three seat limits, read from its replay's and gate's own arguments, are five each (else the build stops and reports); on every cell's replay and gate `reset_failed_combines` is False and `activation_timing` the default, on activation; Stage 2's sentinel `hold_expiry_days` is never loaded (the red team's m7 (a)-(c)); the seat keywords and banking reach the path in the replay and the gate; at C = 5 a cell equals its base until its first pass; a queue forms only at five funded; banking on buys while passes wait, off does not; `exp_30` removes a pass at the first close past 30 calendar days (21 sessions in the gate), unpaid and unseated, counted; an expiry beyond the horizon equals `exp_none` |
| T-5 | L-H: the trigger at the first close with net cash above zero, after arrivals and before the evening's fees; equal to the base before it; after it no fee leaves net cash at or below zero; `house_stop` buys nothing after it; an evaluation is abandoned at its billing day and not rebilled; a pass waits for cash, and under `exp_30` is lost unpaid at 30 calendar days (21 sessions in the gate); the rule reaches every branch of the purchase step; the trigger unreachable equals the base; the start ahead at every close after the trigger |
| T-6 | 10.2 on RD-02's functions with this seed: the kept windows, the interval from 4 kept windows with a spread, the sign count, the zero-series rule, the MDD's formula, and the honesty series' keys `[20262240, 0, ...]` drawn only by the test |
| T-7 | 9.2's oracles on toy campaigns, each shown to fire on a hand-broken case |
| T-8 (`slow`) | 9.1 items 1 to 3 at 4 paths and 4 starts per base and arm, through `identity/cl_identity.py`; 6.4 at a short horizon through `identity/cl_fit_identity.py` |
| T-9 | section 12's seeds appear nowhere in the build's commit outside the uses section 12 declares (the red team's m7 (d)); 14.2's literal check |
| T-10 | A-1 (d)'s counters channel: with it on every replay output, gate row and path record equals it off, at one worker and at two; the counters equal the path's own on toy campaigns; in `ref` every one is zero |
| T-11 | `identity/cl_identity.py` and `identity/cl_fit_identity.py` run the reference only: every option a constant at its off value; no argument naming a lever, a cell, a price or an option; with any option flipped the guard refuses before the first start, path or solve |
| T-12 | stage 0 on a toy contract with hand-computed forward summaries: the registered policy's evaluation and its rate `lambda_pi`; the read's two checks, each shown to fire on a mismatched input; G-B's and G-N's two sides and their solver's-view lines; no code path from them to any cell, flag or order; a nudged row of the identity file refused |
| T-13 | A-4: in `naf` every evaluation fee is $95 a cycle and every activation $0, in the replay and the gate; nothing else changes; with Standard's prices given it equals the base |
| T-14 | the menu: no P printed without its guard row (E-134 (2)); every house-money row labelled "gaming P (E-134 (2))" and never ordered on P; the flags of 10.1 item 12 mechanical on synthetic menus |
| T-15 | A-2 and A-3 absent: every task, replay, output and gate row as before, bit for bit, on all of Q-17's responses; given, the Focused Trader models admitted with the vendored class; `reset_failed_combines` False on every cell |

## 15. Outputs and the run

- **Files:**
  - `results/cl_fit.csv` -- stage 0: sections `identity`, `oracle`, `reading`, `rent`, `checks`, `resolve_beside`,
    `solver_view`;
  - `results/cl_reading.csv` -- sections `identity`, `oracle`, `mechanics`, `scorecard`, `guard`, `paired`, `diverge`,
    `coverage`, `ladder`, `rtp`, `ftp`;
  - `results/cl_gate.csv` -- the gate rows;
  - `results/cl_menu.csv` -- the menu with its flags and labels.

  Each is written with its sidecar manifest through `extended.results.write_result`, carrying: `prereg_id` `RD-03` and
  its pinning row; the rows under which `cl_identity`, `cl_fit_identity`, Q-05, Q-80, Q-93 and Q-101 held, each with
  its sha and the run's head; the row that recorded stage 0's run; the cell and run counts (section 13, as
  run); every seed, the inherited ones named; every parameter and every reading of 4.3 with its label; the record
  entries with their dates read and the commit Q-115 merged at; the commit and blob ids of every adapter run; the
  sha256 of `vendor/DATA_MANIFEST_stage2.sha256` and the LF sha256 of the two calendars, each checked before its first
  read; the E-015 limits flagged with their rows, or "none approved before the run's commit"; `exploratory=False`
  (nothing is chosen after a look), every cell still labelled "described, not carried".
- **The run, in five steps, each from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock
  (`run.lock`, skill `run-lock`), one heavy job on the machine, watched to its exit; each step only after the lead's row
  records the one before:**
  1. **the identities:** `identity/cl_fit_identity.py` and `identity/cl_identity.py`, under the purpose `identity` and
     their own row (the reader admits `identity` only from `identity/*.py`). Any failure stops the reading;
  2. **stage 0** (`scripts/cl_fit.py`, one worker): its identity first (6.4), then `results/cl_fit.csv`; it decides
     nothing, and step 3 runs every cell whatever it shows (6.3);
  3. **the scorecard and the gates** (`scripts/cl_reading.py`, purposes `levers_scorecard` then `levers_gate_beside`),
     in this order: (a) `ref` on P-14 then P-16 at `off`, both arms, the recorder on (9.1 items 2's repeat and 4); (b)
     each new cell, P-14 then P-16, in the order house money (`house_stop` before `house_zero`; `exp_none` before
     `exp_30`), the inventory (C = 5 before C = 7; banking on before off; `exp_none` before `exp_30`), Back2Funded (`b2f1`
     before `b2f2`), `naf` -- each at `off`,
     both arms, the recorder on, checked under 9.1 items 5 and 7 before anything of it is read; (c) the gates, in the
     same order; (d) the oracles and the mechanics, then the reading and the menu without its beside sections;
  4. **the ladder and the placement** (purpose `levers_ladder_beside`): `ref`'s checks against Q-44 (9.1 item 6) first,
     then every new cell in step 3's order;
  5. **the Focused Trader models** (purpose `levers_ftp_beside`): `ref`'s checks against Q-44 first, then every
     inventory and Back2Funded cell in step 3's order, then the Back2Funded cells' counted reading (U-6); then the menu's
     beside sections.

  **On any failure, nothing of a new cell is computed, written or printed**: the run stops at the failed check, and
  its log and the check's own lines are all it leaves.
  - **weight: heavy.** Thirty-two replays on two arms over every start, 360 replays beside on the verdict arm with 28
    reference checks, thirty gates of 500 paths, and stage 0's four policy evaluations and eight solves. Measured on synthetic
    campaigns of the window's length before step 3 (E-117's form) and stated in the lead's row with its memory; E-010's
    U1 identity for two configurations peaked near 1.4 GB, so two workers at most (the two-worker check of A-1 (d), T-10,
    held under its own row first).
  - **a restart or a rerun (E-053).** Each purpose allows one clean run; a restart, a rerun after a fix, or the
    failure protocol's replication is a further judged read and needs `repeat='E-NNN'`, a row naming this file. Only
    the first complete run under each purpose is read.
- **Waits, all before step 3:**
  - **Q-115 merged** (E-134, E-135), and then **every shared identity held again** at a commit containing it (Q-05,
    Q-80, Q-93 with Q-100, Q-101), since the merge writes under `config/` (E-117);
  - the pinning row;
  - **Q-44's file on master** (`results/user_beside_starts.csv`), for 9.1 item 6;
  - A-1 to A-6 built with T-0 to T-15, and the red team's read of the build;
  - steps 1 and 2 recorded.

  It does not wait for E-015's limits (flags only) or for any answer from Topstep (16).

## 16. Open before the pin

**The lead's:**

1. **The gatekeeper's read of this second text** before the pin (the red team read the first, Q-116r; E-146 adopted
   its findings), or the lead's diff check against 153f453 if the gatekeeper's form allows it; and **T-0** (`tests/test_rd03_draft.py`),
   which this text's brief did not let its drafter write (a declaration only, no code): owed before the pin.
2. **Q-115's merge and the order of the pin.** This text cites keys on `wt/wt-firms` at deb45ad. If the pin comes
   before the merge, T-0 reads those keys from deb45ad's blob; either way the merge comes before the run (4.1, 15).
3. **The name at the pin:** `prereg/RD-03_contract_levers.md`; the DRAFT file renamed in the same commit, nothing else
   changing (T-0 asserts exactly one contract-levers declaration under `prereg/`).
4. **E-134 (2)'s label wording.** This text writes "gaming P (E-134 (2))"; if the lead words the ruling's label
   otherwise, the change is made before the pin.

**The operator's:**

1. **The hold's expiry**, optional: a browser read of the activation page for a passed evaluation waiting at five
   funded accounts, or Topstep's written answer (`docs/OPERATOR_SETUP.md`, a read, no purchase): "Does a passed Trading
   Combine on hold for an XFA seat expire, and if so after how many days?" Until an answer is recorded the reading runs
   both readings and flags the rows (U-1).
2. **The levels of E-015's limits**: flags only; only those approved before the run's commit flag the menu.
3. **After the run:** the choice from the menu, if any; any purchase it implies is the operator's.

## 17. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*

---

## Appendix R -- every rule key this reading leans on, with its record and status

Sources: `record` is this repository's `config/rules_extended.yaml` (the Q-115 entries at deb45ad on `wt/wt-firms`, to
be merged before the run; `tou_s8_relative_position_size` on master); `stage2` is Stage 2's vendored
`vendor/stage2/config/rules.yaml`. T-0 checks every row against its source.

| key | source | status | used for |
|---|---|---|---|
| `back2funded_reactivation_fee_50k` | record | verified | L-B's price; G-B |
| `back2funded_reactivation_fee_100k` | record | verified | not used (50K only) |
| `back2funded_reactivation_fee_150k` | record | verified | not used (50K only) |
| `back2funded_fee_by_pricing_path` | record | unstated | L-B and L-N not crossed |
| `back2funded_dll_discount` | record | verified | not used (no DLL) |
| `back2funded_max_reactivations` | record | verified | L-B's limit |
| `back2funded_eligibility` | record | verified | L-B's eligibility (U-5, U-7) |
| `back2funded_window_days` | record | verified | L-B's window |
| `back2funded_trading_from` | record | verified | L-B's timing (U-3) |
| `back2funded_seat_count` | record | verified | L-B's seat (U-3) |
| `back2funded_account_restart` | record | verified | the reactivated account (U-4); G-B's fresh funded account |
| `reset_credit_per_rebill` | record | verified | moot (no resets) |
| `reset_credit_expiry` | record | verified | moot (no resets) |
| `reset_rebill_push` | record | verified | resets excluded (2.5) |
| `subscription_fee_naf_50k` | record | verified | L-N; G-N |
| `reset_fee_naf_50k` | record | verified | stage 0 (c)'s re-solve; moot in the replay |
| `activation_fee_naf_50k` | record | verified | L-N; G-N |
| `hold_expiry_days` | record | unstated | L-I's two readings (U-1) |
| `combine_cancellation` | record | verified | L-H (U-2) |
| `combine_cancellation_account_effect` | record | unstated | L-H's cancel timing (U-2) |
| `tou_s8_relative_position_size` | record | verified | tier 3, the ladder |
| `hold_expiry_days` | stage2 | verified (the design sentinel `not_required_under_d34`, not a reading) | superseded here by the record's unstated reading |
| `subscription_fee` | stage2 | verified | the Standard path; stage 0 |
| `activation_fee` | stage2 | verified | the Standard path; stage 0 |
| `reset_fee` | stage2 | verified | stage 0 (a)'s solve as D-666 prices it; moot in the replay |
| `billing_days` | stage2 | verified | rebills; the 21-session translation |
| `billing_period_calendar_days` | stage2 | verified | the 30-calendar-day basis |
| `combine_count_limit` | stage2 | verified | L-I |
| `max_active_funded_accounts` | stage2 | verified | the funded cap; L-B's seat |
| `hold_queue_behaviour` | stage2 | verified | L-I; L-H's waiting pass |
| `xfa_activation_latency` | stage2 | verified | activation the evening a seat frees |
| `xfa_seat_frees_at` | stage2 | unverified_human_input_required | never loaded: the engine's convention (U-3) |
| `xfa_closure_at_request` | stage2 | unverified_human_input_required | never used (2.5) |
| `account_start_rate_limit` | stage2 | verified | no daily limit invented (U-8) |
| `combine_profit_target` | stage2 | verified | the evaluation, every cell |
| `combine_mll` | stage2 | verified | the evaluation, every cell |
| `combine_mll_lock_at` | stage2 | verified | the evaluation, every cell |
| `combine_consistency_max_day_frac` | stage2 | verified | the evaluation, every cell |
| `combine_position_size_limit` | stage2 | verified | the evaluation's allowance |
| `xfa_mll_start` | stage2 | verified | every funded floor, a reactivated one included |
| `xfa_lock_at` | stage2 | verified | every funded lock |
| `funded_scaling_plan` | stage2 | verified | every funded allowance (U-4) |
| `scaling_tier_after_payout` | stage2 | verified | the tier follows the balance |
| `xfa_std_winning_days` | stage2 | verified | P-14's payout rule |
| `xfa_std_winning_day_min` | stage2 | verified | P-14's payout rule |
| `xfa_std_cap` | stage2 | verified | P-14's payout rule |
| `payout_max_frac_of_balance` | stage2 | verified | P-14's payout rule |
| `payout_min` | stage2 | verified | P-14's payout rule |
| `profit_split` | stage2 | verified | cash to the user |
| `require_profit_since_payout` | stage2 | verified | eligibility after the first payout |
| `payout_after_request_survives_mll_breach` | stage2 | verified | a requested payout is taken (U-7) |
| `payout_fee` | stage2 | verified | the method |
| `payout_lag_days_aeropay` | stage2 | verified | the method |
| `xfa_payout_path_choice` | stage2 | verified | the Standard path; the placement's Consistency path beside |
| `focused_trader_program` | stage2 | verified | the ten models beside; U-5 |
| `responsible_trading_program` | stage2 | verified | `rtp` beside |
| `cross_account_opposite_positions` | stage2 | verified | tier 1 |
| `trading_hours` | stage2 | verified | the designs' 15:10 CT flatten |
| `reset_limit_per_account_per_calendar_day` | stage2 | verified | moot (no resets) |

---

## Appendix C -- the drafter's choices, each with its reason

Every choice made where the scout's note, the brief or the rules left the text open, as this second text holds it. The
first text's hand-back listed them; the red team judged the text's own list (its section "The draft's choices"); E-146
asked for them here.

| # | choice | where | reason |
|---|---|---|---|
| 1 | stage 0's Back2Funded rule weighs `W - lambda x T` against $599, not the route's fees per pass against $599 (the scout's arithmetic, printed beside) | 6.3 | "the fresh funded account's value net of the evaluation route" (the note, section 5) read under the table's own model: the seat earns the evaluation route's rent while the reactivated account holds it; the red team found it the exact one-step policy-improvement test |
| 2 | stage 0 decides nothing; both rules printed beside as "the solver's view" | 6 | the lead's ruling (E-146) on M1: the rules measure long-run cash, not P, and a strict rule must not fail a lever that may help the user (E-051) |
| 3 | stage 0's inputs from the registered policy's forward pass at each base's bound edge, at that policy's own rate; D-666's re-solve beside | 6.1 | M2: every cell trades the registered table, so its model is the relevant one; the evaluation is a few forward passes, cheap |
| 4 | the pricing path's rule on payouts per fee dollar with the table fixed | 6.3 | the `naf` cells trade the registered table; payouts per fee dollar is the measure D-657 ties to P across designs and D-666 used |
| 5 | the pricing path replayed (2 cells), not only read at the fit | 2.4; 7.2 | the cells are an exact re-pricing of the base's paths, nearly free, and the fit is no test of P (M1) |
| 6 | a reactivation bought on the evening of the breach close, first among that evening's acts, trading the next session | 2.1; U-3 | m3: `back2funded_seat_count` and `back2funded_trading_from` allow it; the lever's value is speed; labelled "bought before the 17:00 CT reopening" |
| 7 | a requested, unpaid payout counts as taken: no reactivation after it | U-7 | `payout_after_request_survives_mll_breach` pays such a request; one conservative reading (n4), the other not run |
| 8 | accounts closed by the horizon, a denial, a household or forfeiture closure or a Focused Trader placement are not eligible; good standing true at 0 % | U-5; U-7 | none is the designs' "rule violation" (an MLL breach); the Focused Trader Plan bars Back2Funded on its page |
| 9 | a reactivation not counted as a purchase in the budget or the Focused Trader purchase measure, with a counted reading beside on the models | U-6 | both count "Combine purchases and resets" (D-497, D-501); the Corrective Path names recycling XFAs, so the conservative reading is run too (m2) |
| 10 | the reactivated account at the entry scaling tier | U-4 | "same as a brand new XFA" with the balance reset to $0, and the tier follows the balance (`scaling_tier_after_payout`) |
| 11 | the inventory's evaluation cap C in {5, 7} | 2.2 | 5 keeps D-34's bound for evaluations alone and the base's day 0 (disclosed: D-651 (2) found early evaluations cost P); 7 is the scout's "one or two values above"; seat counts, no value from data |
| 12 | banking on and off | 2.2 | off is D-08's engine rule; on is the lever's point |
| 13 | the hold's expiry read both ways, `exp_30` as 30 calendar days from the pass whether or not at the cap (21 sessions in the gate), neither the base | U-1 | `hold_expiry_days` is unstated; the only number on record is the search summary's 30 days; E-135 asks for both readings |
| 14 | house money under both expiry readings | 2.3 | M3: its passes wait for cash below the cap, the case the 30-day sentence names |
| 15 | the house-money trigger at the first close with net cash above zero, after arrivals, before the evening's fees | 2.3 | CHARTER's "ahead"; no free parameter; makes "ahead" absorbing exactly (E-134 (2)) |
| 16 | house money cancels an evaluation only at the last close before its rebill (the engine's abandonment at the billing day) | U-2 | under either reading of `combine_cancellation_account_effect` nothing paid for is lost |
| 17 | the purchase budget held at each base's 20 in 21; "budget off" dropped | 2.2; 2.5 | the budget is the bases' registered restraint; its removal was Stage 2's family 1 (D-634); lifting it would mix two levers |
| 18 | the levers not crossed; Back2Funded not under No Activation Fee | 2.5 | each lever read alone against its base; `back2funded_fee_by_pricing_path` is unstated |
| 19 | resets and the DLL excluded | 2.5 | the engine's reset keeps the billing dates against `reset_rebill_push` (E-135); the DLL is a different account from the table's (D-320 (2)) |
| 20 | the Focused Trader models beside the inventory and Back2Funded cells, not the house-money and `naf` cells (the gap named) | 4.5; 10.1 item 8 | the two levers that lean on the pattern the models count; house money withholds purchases and `naf` buys exactly the base's evaluations; m1 accepted naming the gap |
| 21 | Back2Funded built into a copy of the vendored path, not a funded-account subclass | A-1 | keeps the vendored `FundedAccount`, so the engine admits the Focused Trader models (E-059 (2)) |
| 22 | stage 0 composes the vendored size-fit module's pieces, not its runner | 6.1 | the runner needs two D-559 files the snapshot lacks |
| 23 | the uncertainty method RD-02's 9.2, unchanged, with this reading's own honesty seed | 10.2 | the program's corrected method (E-058 (5)), built and tested; a new seed so no seed changes meaning |
| 24 | the frontier printed without the house-money cells, and with them labelled | 10.1 item 1 | m6: they cannot fall below their base on P by construction |
| 25 | the beside readings' guard row carries the cell's 0 % gate, labelled | 10.1 item 8 | m5: no gate is run under a beside response |
