# The next levers, given that the money is the contract's (TASK_QUEUE Q-114, E-132, 2026-11-17)

A read-only research note by the scout (wt-scout, branch `wt/wt-scout`, master merged at 081838c). It declares
nothing, runs nothing and reads no outcome. It reads the program's rules and records and ranks execution levers that no
family or reading has declared yet. Every claim cites a file and a line or section. **No result value is typed here.**
The figures that appear are firm prices and limits quoted in the verified ledgers, stage one's analytic ceilings as
Stage 2's handoff states them, and arithmetic on those two. Where a comparison needs a design's own outcome (a pass rate,
a payout per account), the note names the result file that holds it and does not read it.

**What was read** (2026-11-17, the record date of E-125 to E-132; the machine clock showed 2026-11-16):
`CHARTER.md` (all sections); `DIRECTIVE.md`; `DECISIONS.md` E-007, E-008, E-012 to E-015, E-020, E-023, E-059, E-071,
E-072, E-094, E-105, E-110, E-125 at 081838c, and E-128 to E-132 in the lead's staged copy;
`docs/research/composing_an_execution_model_2026-11-16.md` (the structure note); `docs/audits/Q-18_p14_stress_2026-11-17.md`;
`docs/audits/phase0/E_rules_currency.md` (N1-N6, U1-U5); the header tables of `prereg/F-03_opening_timing.md`,
`prereg/RD-01_firm_contracts.md` and `prereg/RD-02_payout_policy.md`; Stage 2's handoff
`vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` sections 1.4 and 2-3; the Stage 2 D-rows cited below in
`vendor/stage2/DECISIONS.md`; the keys of `vendor/stage2/config/rules.yaml` and `config/rules_extended.yaml` cited
below; `vendor/stage2/propedge/campaign/lockstep.py` (the path signature and the purchase step);
`vendor/stage2/propedge/research/u_select.py` (the seat overrides); `extended/campaign.py`, `extended/user_beside.py`
(signatures and docstrings only). Stage 2's literature review `vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md`
was opened at its contents (sections 1-7). It covers directional market effects only. No lever here rests on a market
effect: each rests on the contract's own arithmetic. So no literature was searched, and none is cited as evidence.

**What was not read:** no `results/*.csv` of either repository, no bar, no walk, no trade table, no NQ from 2026-07-17,
no firm page (the brief forbids new fetches).

---

## The question

E-125 records P-14's mean trade as negative at every R (`results/p14_validation.csv`, section `b1`, column `truth`). So
its money is the prop-firm contract's: cheap evaluations, a few passes, funded payouts. That money survives every
declared stress. Three things are already declared: family O (F-03, the funded opening's timing), RD-01 (other firms)
and RD-02 (payout policy). Given that, which execution levers that are **not yet declared** are most likely to raise the
user's journey? The journey here is P (the share of starts ahead at months 1-3), time to the first pass, time to the
first payout, and the return on spend. For each lever the brief asks for six things: its slot, its judging route, whether
it adds trades, the firm rules it touches, its conduct tier, and what is already known. Then a ranking by expected value
and by how cheaply each could be declared.

## The answer in a few sentences

Stage 2 has already read most of the obvious levers on P and closed each one. That covers the purchase budget, wallet
stops, purchase pauses, seat ramps, fewer seats, trading hours, a second firm, the Consistency path, flat funded plans,
resolving crippled accounts and larger accounts (handoff 3.1; Stage 2 D-634 to D-667). **What is left lies where the
contract's money is made: the funded seat and the evaluation that feeds it.** Three undeclared levers act there directly:

1. **Back2Funded**: buy a lost funded account back, instead of passing a new evaluation.
2. **The evaluation inventory**: Topstep caps funded accounts at five, but not evaluations. The designs' own cap of five
   accounts *including* evaluations is a self-imposed policy (Stage 2 D-34). Letting evaluations run beside five funded
   accounts, and banking passes on hold, keeps funded seats filled.
3. **The pricing path and the reset terms**: cheap to close at the fit.

A fourth lever, **buying only with house money once ahead**, raises P *by construction*. Once a user is ahead, the rule
never lets them fall back. That is a warning about P as a measure more than a gain for the user, and the lead should hear
it before any described lever is read on P.

All of these leave the offered trades unchanged. So under E-023 (1) each is a **described reading for the operator's
menu, never carried**. None of them can produce a candidate. The carried route stays a real edge on the trades (E-008).

---

## 1. The frame: why every contract lever is a described reading

- **The pass line is direction on the design's own trades** (CHARTER section 3; E-008 (1)). A lever that changes how
  many evaluations are bought, which account takes an offer, or what happens when an account ends cannot pass that line.
  Its trades are the same coin offers and their lift over the coin twin is zero by construction. As the structure note
  puts it: "a design cannot pass on supply alone" (structure note 1.3).
- **E-023 (1)** sends "levers that add no trades -- payout policy ... and any other choice that leaves the offered trades
  unchanged" to a described reading. A described reading takes no family number, is pinned before it runs and is read on
  the journey scorecard. RD-01 reads a firm's contract the same way: "the same registered entries, the same outcome of
  every offer at every R, the same days in the same order" (`prereg/RD-01_firm_contracts.md`, "What E-023 (1) makes of
  it").
- **This note's reading, for the lead to confirm or overrule:** levers that change *routed* trades (more evaluation
  attempts, an extra funded opening) but not the *offered* trades fall under E-023 (1). They are not E-008 families. A
  lever that removes offers (a session window) is a filter keeping the coin's side, so it falls under E-023 (2) and is
  tested against a placebo-selection twin. No row yet says this in words for routing and purchase levers. Stage 2 judged
  them on P under D-621, a rule E-008 retired. This reading would go in a row.
- **Q-108 does not reach these levers.** Q-108 decides whether one-directional, persistent *side* designs can be judged
  (E-094 (3)(e), E-105, E-110). None of the levers here chooses a side.
- **Which measure moves P.** Across designs, P moves with payouts per fee dollar and hardly at all with speed or bankroll
  (Stage 2 D-657 (3), (8); CHARTER section 2, "Why S3c screened"). The red team's caveat applies: across designs this is
  partly arithmetic, though within one trade stream S3c does track P (E-007; CHARTER section 2). Every lever here keeps
  the base's trade stream, so the within-stream reading applies. **A lever helps only if it raises what a funded seat
  pays back per fee dollar, or makes that happen sooner.**
- **Where the money is made.** About a quarter of funded accounts win the 3R opening, and nearly all of those are paid.
  The rest live on crippled, are rarely paid, and take most of the funded account-days before a first payout (Stage 2
  D-652 (1)-(3); handoff 2.5). Every Stage 2 change to the funded leg's *size* was worse for a user (D-655, D-661, D-664).
  So the levers left are those that buy, fill or refill funded seats more cheaply. Changing how a seat trades is not one
  of them.
- **The exposure that rises with them.** Topstep's own pages name the contract-money pattern: "bold funded play into the
  Maximum Loss Limit, then buying again" (Stage 2 D-495 (2)). The Focused Trader Program's triggers are "Excessive Resets
  and Trading Combine purchases", "Activating and losing many Express Funded Accounts in a short period of time" and
  "Excessive recycling of Trading Combines® or XFAs". Its consequences end a campaign (`vendor/stage2/config/rules.yaml`
  `focused_trader_program`, line 1711). Every lever that leans harder on the contract leans harder on that pattern. That
  is tier 3, priced, never a ban (Stage 2 D-145). The verdict stays at 0 % denial with the placement off (E-008 (2)), and
  the Focused Trader readings go beside (E-007 (e)).

---

## 2. The ranked list

Expected value (EV) is to the journey as defined above, judged from the mechanism and Stage 2's closed families. It is
not computed. Cost is the work before a pinned declaration could run.

| rank | lever | slot (structure note 1.1) | judged | adds trades? | EV to the journey | cost to declare | first need |
|---|---|---|---|---|---|---|---|
| 1 | **Back2Funded reactivation** of a funded account lost before its first payout | 7 purchases (what is bought when an account ends); 6 routing | E-023 (1), described | no offered trades; adds funded openings | **high, uncertain**: buys straight into place (c), skipping evaluation trades that lose on average (E-125) | medium. The first step is cheap: a solver-only fit read | rules-verifier rows for Back2Funded (none is a key today) |
| 2 | **Evaluation inventory**: evaluations beside five funded accounts; passes banked on hold | 6 routing, 7 purchases | E-023 (1), described | no offered trades; adds evaluation attempts | **medium**: keeps funded seats filled while crippled accounts linger; Stage 2's nearest reading points against it on P (D-651 (2)) | **cheapest real lever**: engine arguments only | a row lifting D-34's self-imposed cap; `hold_expiry_days` read |
| 3 | **House-money purchasing** once ahead | 7 purchases (a user stop rule) | E-023 (1), described | no; fewer purchases | **P rises by construction**: a measure warning, not a gain. Its real value is evenness, at a cost in growth | low to medium: one purchase-and-cancel condition | the lead's ruling on reporting it |
| 4 | **Pricing path** (Standard against No Activation Fee) and the DLL at checkout | 7 purchases, 10 contract terms | E-023 (1), described | no | **low**: break-even arithmetic below; the doubled caps buy nothing where caps never bind | **cheapest**: fee arguments; closable at the fit | the No Activation Fee prices as keys |
| 5 | **Reset policy** and the Reset Credit | 7 purchases | E-023 (1), described | no | **low**: a reset and a new purchase cost the same under the verified prices | cheap: engine flag (Stage 2 D-146); billing convention fix | 8284128's credit and rebill rows |
| 6 | **A state table solved for the journey** (or for the Consistency path) | 4 bracket and R, 5 size | E-023 (1), described | no | uncertain: the rate-objective table beat every hand-made plan on P | **high**: solver work in `extended/` | a declared objective; identity at λ\* |
| 7 | **Account roles and staggered starts** (by time, not by payouts) | 6, 7 | E-023 (1); an opening-stagger part E-023 (2) | no | low: one more point on D-638's line | medium: a campaign option | D-61's reading for any window partition |
| 8 | **Session choice** as a filter | 1 schedule | E-023 (2), placebo-selection twin | removes offers | low on P (Stage 2 D-642); real for who can use the product | high: a numbered family (k), power (E-071) | already largely described in Stage 2's `u_hours.csv` |
| 9 | **Closing a crippled funded account at request** | 6 | E-023 (1) | no | unknown | **blocked** | Topstep's written answer (`xfa_closure_at_request` unverified) |

Ranks 1-3 are where the contract's money is made. Rank 4 can be closed cheaply, perhaps inside rank 1's fit read. Ranks
6-9 are expensive, low, or blocked. Already declared and not ranked: payout policy (RD-02), firms (RD-01), the opening's
timing (F-03), and the opening's R cap (family R Part II, drafted in `prereg/DRAFT_F-R_resolution.md` and not pinned).

---

## 3. Each lever

### 3.1 Back2Funded: reactivating a funded account lost before its first payout (rank 1)

- **Mechanism.** Under the designs, a funded account that loses its 3R opening lives on crippled and usually ends at the
  loss limit unpaid (Stage 2 D-652 (1), (4)). Today the campaign replaces it by buying evaluations until one passes, then
  paying activation. Stage 2's family 9 failed partly because "every ended account is a fresh evaluation bought" (D-664
  (4)). Back2Funded replaces that chain with one purchase: the lost account comes back the next session, ready for a
  fresh opening at place (c). The value map prices a win highest at place (c) (handoff 2.7; CHARTER section 1). The lever
  also skips the evaluation trades, whose mean is negative (E-125).
- **Arithmetic on the quoted prices (not a result).** The reactivation price quoted in the ledger is $599 at 50K. It sits
  in `reset_fee`'s 2026-09-22 note (`vendor/stage2/config/rules.yaml` lines 605-606: "reactivates a LOST funded account at
  $599/$699/$829 by size, max 2 per XFA, only before the first payout"). The route through evaluations costs about
  $49 x N + $149 per pass, where N is Combine-months per pass (`subscription_fee` line 466, `activation_fee` line 551).
  On fees alone, reactivation is cheaper when N > 450/49, about 9.2. Stage one's zero-edge ceiling is P(pass) at most 2/5
  for any fair strategy (handoff 2.3). So N is at least 2.5 at zero edge, and arithmetic alone does not settle it. The
  designs' own pass rate at the bound decides, together with the sessions saved and the evaluation trades avoided. The
  rate is in Stage 2's U2 evaluation funnel (`vendor/stage2/results/u_xfa_day_budget.csv`), **not read here**.
- **Slot:** 7 (purchases), read as "what is bought when an account ends", which widens the structure note's "how many
  evaluations are bought". Also 6, because a reactivated account takes the router's offers again.
- **Judged:** E-023 (1), described. It leaves the offered trades unchanged and adds funded openings drawn from the same
  coin offers.
- **Firm rules touched:**
  - `max_active_funded_accounts` (line 637).
  - `xfa_mll_start` (line 211). Its note quotes Back2Funded's table: "$50K XFA" / "-$2,000".
  - `xfa_seat_frees_at` (line 854, **unverified**). Its note quotes 12060405: "Back2Funded-eligible XFAs do not count
    toward your 5-account limit during the 30-day window" and "becomes available at the start of the next trading
    session after your purchase".
  - `account_start_rate_limit` (line 2182). Its note says: "lets you reactivate up to 2 times at the same size and Payout
    policy".
  - `subscription_fee` (line 466). The "$50 off" Reactivation Fees with a DLL; two pages disagree on the product list.
  - `focused_trader_program` (line 1711). The Slowdown Path bars "B2F Reactivations".
  - **Flag: Back2Funded has no key of its own in either ledger.** Its price, its limit of two, its eligibility (an XFA
    "closed due to a rule violation before taking a Payout", quoted at line 762), its 30-day window and its timing are
    sentences inside other rows' notes. The price was last quoted on 2026-09-22. Nothing about it can be loaded until the
    rules-verifier records each as a row (12060405, 8284204, 14289835) and the lead takes it (CLAUDE.md, "Firm rules").
- **Conduct tier:** 3. "Activating and losing many Express Funded Accounts in a short period of time" and "Excessive
  recycling of Trading Combines® or XFAs" (`focused_trader_program`). Not tier 1: the product is sold for this purpose,
  and nothing is concealed.
- **Already known:** no Stage 2 D-row and no E-row models Back2Funded. The ledger records it only as "a DIFFERENT product"
  from a reset (line 605). D-652 measures the accounts it would act on. D-664 measures the cost it would replace. The
  handoff lists the related, unverified closure at request as an open structural item (3.3).
- **Interactions:**
  - With F-03: more fresh openings means more uses of family O's waiting rule, and a reactivated account is a "newly
    funded account" in its sense. F-03's text must say whether that is so before any composite.
  - With RD-02: reactivation exists only before the first payout.
  - With the table: the table was solved without the option (Stage 2 D-329), so it undervalues risking a crippled
    account. Every first reading is first-order with the table fixed, labelled so.

### 3.2 The evaluation inventory: evaluations beside five funded accounts, passes banked on hold (rank 2)

- **Mechanism.** Topstep caps *funded* accounts at five and evaluations not at all.
  - `max_active_funded_accounts`: "You can hold up to 5 active XFAs at a time" (line 637).
  - `combine_count_limit`: "no limit on how many you can have at once" (line 177).
  - `hold_queue_behaviour`: a pass at the cap "goes on hold until one closes", and the activation fee is paid at
    activation (line 670).

  The designs instead hold "at most 5 concurrent accounts INCLUDING Combines" (Stage 2 D-34, line 49: "a self-imposed
  cap", "a protocol parameter bounded at 5"). The engine also "stops buying Combines while a pass is already waiting"
  (D-08, line 23; `stop_buying_when_queued`, `lockstep.py` line 1248 and line 2100). So once crippled funded accounts
  hold the seats (D-652 (3)), evaluation stops. No new pass is ready when a crippled account finally ends.

  With the caps split (five funded, C evaluations) and passes banked, the campaign keeps evaluating. A banked pass costs
  no subscription while it waits: "The subscription tied to the passed Trading Combine will auto-cancel"
  (`billing_period_calendar_days` note, line 526). It activates when a funded seat frees.
- **Slot:** 6 (routing) and 7 (purchases).
- **Judged:** E-023 (1), described. It adds evaluation attempts drawn from the same offers, under the same one position
  at a time across the firm (Stage 2 D-429).
- **Adds trades?** No offered trades. More routed evaluation trades per session, and on P-14's sparser breakout schedule
  these may compete with funded trades for the slot. P-16's five-minute marks offer far more than the router uses (D-652
  (5)). The hand-entry load per session rises, and the user's time is not modelled (E-015 (5)).
- **Firm rules touched:** `combine_count_limit`, `max_active_funded_accounts`, `hold_queue_behaviour`,
  `xfa_activation_latency` (line 706), `xfa_seat_frees_at` (**unverified**; the engine's next-day convention is the
  pessimistic end, line 854) and `billing_period_calendar_days`. **Flag:** `hold_expiry_days` (line 903) is unverified:
  no page states that a held pass expires. A banked pass leans on that silence more than the base does, so a declaration
  must carry a declared reading of the gap or a verified row.
- **Conduct tier:** 3. "Excessive purchases of Trading Combines or Resets" (10296582) and the Focused Trader Slowdown
  Path (`combine_count_limit` note, line 177). D-34 itself recorded this exposure. Not tier 1, and the D-549 operating
  rule stays: never buy and blow an evaluation on the same trading day (line 567).
- **Already known:**
  - Seats were read only *downwards*, from one to four with all three caps together (D-635 (1), D-638). Fewer accounts
    lowered P and every measure but the cash.
  - The nearest upward reading is extra Lucid seats from day 0. The share paid by session 21 rose and the first payout
    came sooner, but P fell and the cash before the first payout rose steeply: "more seats are more evaluations bought
    early" (D-651 (2)). **This is the evidence against the lever on P**, and it is why the cells should keep the base's
    early months (below).
  - A looser purchase budget on P-14's trades left P about level and improved every other measure but the cash (D-634,
    beside).
  - The routing menu is closed (D-576).
- **Cost:** the cheapest real lever. The engine takes the three caps separately: `max_concurrent_accounts`,
  `max_concurrent_combines` and `max_total_accounts` (`lockstep.py` lines 1240, 1245 and 1262; the purchase conditions
  at lines 2115-2116). `extended/campaign.py` passes all three and `stop_buying_when_queued` (lines 200-216, 278-285).
  Stage 2's runner accepts the seat keys only together (`u_select.py` lines 612, 1442-1444). Because the classes stay
  the vendored ones, **the Focused Trader models can be read beside**. E-059 (2) refuses them only for a family's own
  funded class (`extended/user_beside.py` lines 65-66).

### 3.3 House-money purchasing once ahead (rank 3, a measure warning)

- **The arithmetic.** A start is "ahead" when its net cash (payouts received less every fee paid) is above zero (CHARTER
  section 2). Funded accounts carry no monthly fee (handoff 2.1). The US payout method charges nothing (`payout_fee`,
  line 613: Aeropay "No Topstep fee"). A funded loss costs the user only fees (CHARTER section 1).

  Take a rule that, from the first session the start is ahead, incurs no fee that would take net cash to zero or below.
  That means cancelling an evaluation before a rebill would cross zero ("Billing page -> click "X""; 8284121, quoted at
  lines 775-777), and not activating a banked pass whose fee would cross zero. Such a rule makes "ahead" **absorbing**. The
  path is identical to the base until the first moment it is ahead, and ahead at every month end after it. **So the
  share ahead at every month, and hence P, is at least the base's on every start day, by construction.** The rule can
  keep buying with money above zero, so long-run growth need not stop. It does fall, and so does the mean net, most
  likely.
- **Why it matters now.** Any described lever is read on P for the operator's menu (E-023 (1)), and E-015's limits are
  about to be proposed. A rule that games P must be reported as such and read with the measures it cannot game: the mean
  net, the month-6 and month-12 net, CVaR10, the deepest fall after break-even and the long-run gate (E-007 (e); E-014
  (3)-(4)). E-014 (3) already reports "the share that later fall back below zero". This rule sets that share to zero by
  design.
- **Slot:** 7 (purchases), as a user's stop rule. **Judged:** E-023 (1), described. **Adds trades?** No; it removes
  purchases.
- **Firm rules touched:** `subscription_fee`, `billing_period_calendar_days` (rebills; "Payments already processed ...
  are not refunded"), `payout_fee`, `hold_queue_behaviour`. **Flag:** the evaluation's cancellation is quoted only in
  `xfa_closure_at_request`'s note (lines 775-777), not as its own key.
- **Conduct tier:** none new. It lowers the tier-3 purchase exposure.
- **Already known:**
  - D-620 (1)(a) U-c reads two quit rules (Q1, Q2) "as assumptions, not measurements".
  - The wallet stop (D-630 (1)(a), D-637) is the losing-side twin: it stops buying when out of pocket, and was closed.
  - D-643 and D-651 spent the first payout on a second firm's evaluations, and P fell in months 2-3. That is the opposite
    rule.
  - No row reads a stop on the *winning* side.
- **Cost:** a purchase-and-cancel condition (no such option exists in `lockstep.py`'s purchase step, lines 2100-2130).
  It would be an adapter in `extended/` whose identity is "never binding equals the base".

### 3.4 The pricing path and the DLL at checkout (rank 4)

- **Mechanism.** Topstep sells two evaluation pricing paths: Standard ($49 a month, $149 activation, $49 reset) and No
  Activation Fee ($95 a month, $0 activation, $95 reset). The path is chosen at purchase: "Paths cannot be changed after
  purchase" (`subscription_fee` line 466; `activation_fee` line 551; `reset_fee` line 584). Stage 2 called the choice "a
  PROTOCOL DIMENSION, not a constant" (D-25; `activation_fee` note), then parked it (D-276) and never ran it.
- **Arithmetic (not a result):** No Activation Fee is cheaper when (95 - 49) x Combine-months < 149 x activations, that
  is, when activations per Combine-month exceed 46/149, about 0.31. Stage one's per-attempt ceiling at zero edge is 2/5
  (handoff 2.3). So only a design passing near that ceiling at its bound could favour No Activation Fee. The designs'
  rates are in U2's funnel, not read here.
- **The DLL at checkout.**
  - It doubles the payout caps (`dll_offer_status`, line 1219).
  - On the tables on file no payout reaches the cap (D-652 (4)), so the doubling buys nothing there.
  - The $1,000 daily limit (`dll_amount_50k`, line 2099) "cuts the table's $2,000 bold plays" (D-320 (2)). Any DLL cell
    therefore needs a re-solved table, so it belongs with rank 6, not here.
- **Slot:** 7 and 10. **Judged:** E-023 (1), described (RD-01's form, inside Topstep). **Adds trades?** No (without the
  DLL).
- **Firm rules and flag:** the No Activation Fee prices are quotes inside the Standard rows' notes, not keys. D-667 (5)
  records the same of the larger sizes: "notes, not rows". They need their own rows before loading.
- **Conduct tier:** none.
- **Cost:** the cheapest lever. It is fee arguments to the campaign, or a solver-only fit read in D-666's form. It could
  be one reading inside rank 1's fit read.

### 3.5 Reset policy and the Reset Credit (rank 5)

- **Mechanism.** Reset a failed evaluation instead of buying a new one. The engine has the option, off in every
  registered design: `reset_failed_combines` (Stage 2 D-146, line 162; `lockstep.py` lines 1259, 2011-2031; D-549 (3)).
- **Why low.**
  - At the verified prices a reset and a new evaluation both cost $49 and both trade from the next session (D-146 (2);
    D-549 (3)).
  - A reset "pushes your Rebill date out 30 days from the date of purchase" (8284128; `docs/audits/phase0/E_rules_currency.md`
    N3, line 37), so it buys the same thirty days a new purchase does.
  - The only saving is the Reset Credit: "Every monthly Rebill adds 1 Reset Credit to your Reset Bank" (`reset_fee`
    note, line 609, quoted 2026-09-22; "8284128 ... was not re-read today", line 599). A campaign that resets keeps
    pushing its rebill out, so it earns few credits.
- **Slot:** 7. **Judged:** E-023 (1), described. **Adds trades?** No.
- **Firm rules touched:** `reset_fee`, `reset_limit_per_account_per_calendar_day` (line 2217: "2 Resets per account per
  calendar day"), `combine_count_limit`. **Flag:** the Reset Credit, its one-year expiry and the rebill push are not keys
  in either ledger. Also, the engine's reset keeps "The subscription and its billing dates ... unchanged", which charges
  too much against N3 (the conservative direction). A fair reading needs an adapter for the billing convention.
- **Conduct tier:** 3 ("Excessive ... Resets", 10296582; `focused_trader_program`).
- **Already known:** D-146, D-549, N3. No reading on the user journey.

### 3.6 A state table solved for the journey, or for the Consistency path (rank 6)

- **Mechanism.** The no-closure table maximises the campaign's cash per slot-day, λ\* (Stage 2 D-329 (1), D-331): a
  long-run rate. P is a three-month share. A table solved for a finite horizon, or for payouts per fee dollar, is a
  different sizing of the same offers against each account's cushion. That is the brief's "trade size against the
  drawdown cushion". The cushion bands already exist in the table (D-662 (2)). A table solved for the Consistency path's
  40 % rule is the other open re-solve (D-646 (6), D-648 (5)-(6): "no solver work is started").
- **Why uncertain.** Every hand change to the funded leg was worse for a user than the rate-solved table: flat plans at
  four sizes on two paths (D-655, D-661), and crippled accounts resolved at once (D-664 (4): "the solver's table ...
  already trades them close to their best"). The rate objective may already be near the journey's.
- **Slot:** 4 and 5. **Judged:** E-023 (1), described. **Adds trades?** No.
- **Firm rules touched:** the table's own verified rows (target, MLL and lock, scaling plan, Standard winning days, the
  Combine's 55 % rule at `combine_consistency_max_day_frac` line 80; for the path: `xfa_cons_*` lines 328-381,
  `xfa_payout_path_choice` line 1760).
- **Conduct tier:** 2 (the Responsible Trading Program's "max position a majority of your trades", modelled, the
  placement off, D-289) and 3 (Terms of Use s.8, E-013 (1); `config/rules_extended.yaml`
  `tou_s8_relative_position_size`, line 83).
- **Cost:** high. `state_policy.py` is vendored, so a re-solve must subclass it in `extended/`, as D-667 (1)-(2) did in
  Stage 2's research code, with an identity at λ\* reproducing `state_dp_e-0.050_lamstar_noclose`. P is not additive
  over states, so the objective itself must be declared and argued.

### 3.7 Account roles and staggered starts (rank 7)

- **What is open.** Stage 2's program U named "accounts given different roles", "accounts partitioned by session window"
  and "staggered account starts" (D-620 (2) U5), and later assigned them to "the account-alternation family" (D-630 (5)).
  That family was never declared. The only stagger read was paced by payouts (the seat ramp, D-637 (1)(e): "the slowest
  to a first payout"). D-638's summary puts every lever that holds fewer accounts on one line: less cash, fewer users
  ahead. A time-paced stagger is another point on that line.
- **A partition by window** across accounts was specified and **not adopted** for hedging-surveillance reasons (D-61,
  line 76). Under one position at a time it is only routing, which D-576 closed.
- **A one-opening-per-session rule** (staggering the funded openings) aims at the start-day luck (D-657 (5)), not the
  mean. It is a timing filter at place (c), so it falls under E-023 (2) and **conflicts with F-03**, which decides the
  same opening (structure note 2.3).
- **Slot:** 6 and 7. **Conduct tier:** none for roles and stagger. A window partition carries D-61's tier-1 risk reading
  (`cross_account_opposite_positions`, `cross_account_hedging`). **Cost:** medium (a campaign option).

### 3.8 Session choice (rank 8)

- **Mechanism.** Time of day changes resolution speed and cost, not the win rate at zero edge (handoff 3.2). With P-14's
  trades losing on average after costs (E-125), a window with cheaper or faster trades raises the mean trade. That is the
  only selection gain a coin-side filter can show, and family R expects exactly that of itself (E-028 (2); structure
  note 1.2).
- **Known:** the hours family closed (D-639, D-642). The 25-point coin in US hours gave a scorecard about level with
  P-15's, with the largest share paid by session 21 of any cell. It is already on Stage 2's menu (`results/u_hours.csv`).
  Family R Part I (late-mark admission) is the drafted filter of this slot (E-028, E-057).
- **Judged:** E-023 (2). A removed offer is a selection, so this would be a numbered family with its own k. E-071's
  synthetic finding applies to whole-session selections: low power under `placebo_selection_bound`.
- **Firm rules touched:** `trading_hours` (line 2140); `tier1_news_events_restriction` (`config/rules_extended.yaml`
  line 2071). **Conduct tier:** none. **Cost:** high.

### 3.9 Closing a crippled funded account at request (rank 9, blocked)

`xfa_closure_at_request` is `unverified_human_input_required` (line 727). No page says how an XFA is closed at request,
for what fee, or when the seat frees. It is the operator's written question (`docs/OPERATOR_SETUP.md` item 3). No design
may use it (CLAUDE.md, "Firm rules"). Back2Funded does not cover it: reactivation requires closure "due to a rule
violation" (line 762).

---

## 4. What is unknown, and how it could be found

| unknown | why it matters | how found |
|---|---|---|
| Back2Funded's terms as loadable rows: price at 50K Standard, the limit of two, eligibility, window, timing, the reactivated account's balance and MLL, the DLL discount | rank 1 cannot be loaded without them | the rules-verifier on 12060405, 8284204, 14289835, 10490293 (one official page at a time, within robots.txt, E-012) |
| whether a held pass expires (`hold_expiry_days`) | rank 2 banks passes | the rules-verifier; else a declared reading (no expiry, the engine's) labelled on every row |
| the Reset Credit, its expiry and the rebill push as rows (8284128) | rank 5's fee model | the rules-verifier |
| the No Activation Fee prices as their own keys | rank 4 | the rules-verifier |
| the designs' passes per Combine-month and a fresh funded account's value at the bound | settles ranks 1 and 4 by arithmetic | a **solver-only fit read** in D-666's form (the table's fresh-funded value and the evaluation's pass probability at each R's bound): no campaign, no development outcome read beyond the registered bounds |
| whether Back2Funded fits the funded-class seam (Q-47, Q-76) or needs a day-loop option | cost of rank 1; if a class, E-059 (2) refuses the Focused Trader models, exactly the exposure the lever raises | a builder's read of `extended/gate.py` and `extended/campaign.py` against `lockstep.py`'s breach and purchase steps |
| how often a lever would bind on the choice block (eligible funded losses per start; sessions with five funded and no evaluation running) | supply, before any outcome | a direction-free count on choice-block replays (Q-103's form), a worker's job |
| the Focused Trader thresholds | every rank-1 and rank-2 reading rests on 0 % denial with the program off | not published (`focused_trader_program`); read as a sweep beside (D-497 (3)) |

---

## 5. If a lever became a declared reading: what it would declare

Each would be a described reading `prereg/RD-nn_<slug>.md` under E-023 (1). That means no k, no level and no pick,
pinned before its run, with the journey scorecard and E-007 (e)'s readings beside, and the verdict at 0 % denial with
the placement off. All three readings below are built on the same pattern: P-14 and P-16 (U1's bases, E-010), the
registered trades unchanged, and identities first (the reference cell equal to U1's start rows; every option at
"never binds" equal to the base).

**Rank 1, Back2Funded.**
- **Mechanism:** as in 3.1.
- **Stage 0:** a solver-only fit read with a rule fixed beforehand, in D-666 (3)'s form. Go on only if reactivation's
  price is below the fresh funded account's value net of the evaluation route's expected fees on at least one base.
- **Supply:** eligible losses per start, counted on the choice block.
- **Contract fit (CHARTER section 4):** hand entry; one position at a time across the firm; every trade resolving; the
  allowance-capped risk; no reactivated account trading the session it is bought (D-549's spirit); only rows the
  rules-verifier recorded.
- **Cells:** reactivation {never, at most once, at most twice} x {P-14, P-16}. That is 4 cells beyond the two
  references, the table fixed and labelled first-order.

**Rank 2, the evaluation inventory.**
- **Mechanism:** as in 3.2.
- **Cells:** the evaluation cap C, the funded cap 5, the joint cap off, crossed with banking {on, off}, on each base.
  Every value is contract arithmetic (D-620 (1)(f)): C taken from the base's five so the first month is the base's, plus
  one or two values above. For example, C in {5, 7} x banking {on, off} x 2 bases is 8 cells.
- **The purchase budget** is held at the base's 20 in 21, with "budget off" read beside.
- **Beside:** the Focused Trader sweep (D-497 (3)).
- **Supply:** the sessions with five funded accounts and no evaluation running.

**Rank 3, house money.**
- **Cells:** {stop all purchases at the first ahead, no fee that crosses zero} x 2 bases = 4.
- **The declaration must state in its first section** that P cannot fall under it by construction, and name the
  measures it is read on: mean net, month-6 and month-12 net, CVaR10, the long-run gate.

---

## 6. For the lead

**Proposed TASK_QUEUE lines:**

| Q-NNN | **Rules for the contract levers (rules-verifier, official pages only):** Back2Funded (12060405: price at each size and path, the limit of two, eligibility, the 30-day window, next-session availability, the seat, the reactivated account's balance and MLL; 8284204's table; 14289835 and 10490293's DLL discount), the Reset Bank (8284128: one credit per rebill, the expiry, the rebill push), the No Activation Fee 50K prices as keys, `hold_expiry_days`, and the evaluation's cancellation (8284121) as a key -- recorded in `config/rules_extended.yaml` and `docs/RULES_CURRENCY.md`, a row proposed | wt-firms | queued | -- | light | 0 | E-NNN |
| Q-NNN | **Draft RD-03, contract-use levers on the registered trades** (described, E-023 (1); after the rules row): stage 0 a solver-only fit read of Back2Funded and the pricing path (D-666's form, its go-on rule fixed first); then Back2Funded, the evaluation inventory and house-money purchasing on P-14 and P-16 as section 5 lists, the Focused Trader sweep beside the inventory cells; the red team before the pin | wt-payout or wt-user | queued | the rules row | light | 0 | E-NNN |

**Proposed decision row:**

| E-NNN | 2026-11-17 | **Q-114 read (`docs/research/next_levers_contract_money_2026-11-17.md`, wt/wt-scout): the undeclared levers most likely to raise the user's journey now that P-14's money is shown to be the contract's (E-125) -- a read-only note; no result, bar or outcome read; nothing declared.** Readings recorded: (1) Stage 2 has read and closed on P the purchase budget, wallet stop, pause, seat ramp, fewer seats, hours, a second firm, the Consistency path on the tables on file, flat funded plans, crippled accounts resolved and larger sizes (Stage 2 D-634 to D-667); what is left acts on the funded seat and the evaluation that feeds it; (2) the ranking, by expected value and cost: **Back2Funded** reactivation of a funded account lost before its first payout (rank 1: buys into place (c) without the evaluation trades whose mean is negative; no key of its own in either ledger, so nothing of it loads until the rules-verifier records it); the **evaluation inventory** -- evaluations beside five funded accounts, passes banked on hold, lifting Stage 2 D-34's self-imposed cap of five accounts including evaluations (rank 2: engine arguments only, the Focused Trader models readable; Stage 2 D-651 (2) points against it on P); **house-money purchasing** once ahead (rank 3); the pricing path and the DLL (rank 4, closable at the fit by arithmetic on verified prices); resets and the Reset Credit (rank 5); a journey-solved or Consistency-path table, roles and staggered starts, a session filter (ranks 6-8); closure at request blocked on an unverified rule (rank 9); (3) **a lever that buys only with house money once a start is ahead makes "ahead" absorbing, so P cannot fall under it on any start day -- by construction, not by merit**: any described lever read on P is read with the mean net, the month-6 and month-12 net, CVaR10 and the long-run gate beside, and such a rule is labelled as gaming P; (4) the reading, for the lead to confirm: levers that change routed trades but not the offered trades (purchases, seats, reactivation, stop rules) are E-023 (1) described readings, never E-008 families, since their lift over the coin twin is zero by construction; a lever that removes offers is E-023 (2); Q-108's outcome reaches none of them; (5) every lever that leans harder on the contract leans harder on the pattern Topstep's Focused Trader Program names (Stage 2 D-495), tier 3, priced beside the 0 % verdict. Queued: the rules row for Back2Funded, the Reset Bank, the No Activation Fee prices, `hold_expiry_days` and the evaluation's cancellation; then a draft RD-03 with a solver-only fit read first. | Brief Q-114 (E-132); the note; CHARTER sections 1-4; E-007, E-008, E-014, E-015, E-023, E-059, E-125; Stage 2 D-08, D-25, D-34, D-145, D-146, D-329, D-495, D-497, D-549, D-620, D-630, D-634 to D-667. |

---

## Sources (files and lines, all read 2026-11-17)

- `CHARTER.md` sections 1-4 (the objective; the pass line; E-023's two rules; the constraints).
- `DECISIONS.md` E-007, E-008, E-013, E-014, E-015, E-023, E-059, E-071, E-072, E-094, E-105, E-110, E-125, E-132.
- `docs/research/composing_an_execution_model_2026-11-16.md` sections 1.1, 1.3, 2.3, 3.5.
- `docs/audits/Q-18_p14_stress_2026-11-17.md` sections 5-6; `docs/audits/phase0/E_rules_currency.md` N3 (line 37), U1-U3.
- `prereg/F-03_opening_timing.md` header table; `prereg/RD-01_firm_contracts.md` and `prereg/RD-02_payout_policy.md`,
  "What E-023 (1) makes of it".
- `vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` sections 1.4, 2.1-2.7, 3.1-3.3.
- `vendor/stage2/DECISIONS.md`: D-08 (line 23), D-25 (40), D-34 (49), D-61 (76), D-145 (161), D-146 (162), D-234 (253),
  D-276 (295), D-289 (308), D-320 (339), D-329 (348), D-495 (514), D-497 (516), D-549 (567), D-576 (594), D-620 (638),
  D-629 (647), D-630 (648), D-634 (652), D-635 (653), D-637 (655), D-638 (656), D-639 (657), D-642 (660), D-643 (661),
  D-646 (664), D-648 (666), D-651 (669), D-652 (670), D-653 (671), D-655 (673), D-657 (675), D-659 (677), D-661 (679),
  D-662 (680), D-664 (682), D-666 (684), D-667 (685).
- `vendor/stage2/config/rules.yaml`: `combine_consistency_max_day_frac` (80), `combine_count_limit` (177),
  `xfa_mll_start` (211), `xfa_cons_*` (328-381), `subscription_fee` (466), `billing_period_calendar_days` (526),
  `activation_fee` (551), `reset_fee` (584-612), `payout_fee` (613), `max_active_funded_accounts` (637),
  `hold_queue_behaviour` (670), `xfa_activation_latency` (706), `xfa_closure_at_request` (727-812), `xfa_seat_frees_at`
  (854), `hold_expiry_days` (903), `dll_offer_status` (1219), `responsible_trading_program` (1565),
  `focused_trader_program` (1711), `xfa_payout_path_choice` (1760), `dll_amount_50k` (2099), `trading_hours` (2140),
  `account_start_rate_limit` (2182), `reset_limit_per_account_per_calendar_day` (2217).
- `config/rules_extended.yaml`: `tou_s8_relative_position_size` (83), `tier1_news_events_restriction` (2071).
- `vendor/stage2/propedge/campaign/lockstep.py` lines 1232-1275 (the path's caps and options), 2011-2031 (the reset),
  2068 (the hold queue), 2100-2130 (the purchase step).
- `vendor/stage2/propedge/research/u_select.py` lines 612, 658, 673, 1442-1444.
- `extended/campaign.py` lines 200-216, 278-285; `extended/user_beside.py` lines 65-66.
- `vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md` contents only (directional effects; not used).
