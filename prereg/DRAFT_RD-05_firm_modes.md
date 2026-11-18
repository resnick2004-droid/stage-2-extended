# RD-05 (draft): the evaluation and the funded account as two trading modes on each $50K plan -- flip days, the zero-edge maps, the sizing grid, the binding constraint, and the registered trades beside (reading FM) -- a described reading, unnumbered (E-023 (1))

**Status: a first draft (TASK_QUEUE Q-137; E-196, E-197), not pinned.** Drafted on `wt/wt-scout` with master merged at
76ff497. It goes to the red team and the prereg-gatekeeper before any pin. At the pin the file is renamed
`prereg/RD-05_firm_modes.md` and nothing else changes; the pinning row names the commit and the sha256 of its LF text.
Nothing declared is edited after the pin: a change is a new declaration under a new row. It takes no program family
number (E-023 (1)).

**What E-023 (1) makes of it, as E-134 (1) rules it.** Every question here is about the contract, not about an edge:

- the **zero-edge maps** trade a coin -- a driftless bracket with no skill at all -- so there is no trade to lift;
- the **flip-seeking policy** and the **per-mode grids** change only how large each trade is and when, on trades that
  are offered anyway: they add and remove no offered trade, so their lift over the coin twin is zero by construction;
- the **registered trades on each plan** are RD-01's form: the contract changes the money, never the edge.

So this file is a **described reading**:

- it takes **no program family number** and spends **nothing** of the multiplicity budget (the next numbered family's
  k is unchanged by it);
- **no cell can carry, pass or fail**: there is no pass line, no level and no pick;
- every cell is read as a description -- the maps and grids as tables, the registered rows on the journey scorecard --
  for the operator to choose from;
- it is declared and pinned before its run, by its own decision row with its sha256, so nothing in it is chosen after
  a look.

**The pass line is unchanged (E-008, E-196).** A design is judged on its trades: their lift over the coin twin on the
same brackets, on the judged block, at its family's level, by a calibrated statistic. This reading supplies, for each
plan and mode, what the contract is worth to a trader with no edge, and which sizes the plan's rules allow. A valid
model for a firm is then a design with that edge whose sizing fits the firm's rules and whose value over the firm's
zero-edge map is positive (E-196); a design tuned to one firm is a new, declared, counted family. **This reading sets
no bar.** A later family that uses one of these maps as its bar cites the result file and declares the bar itself.

**When this text was written, nothing of it had been built, no engine had been run for it, no bar had been read for it,
and no outcome of any plan had been computed or read.** Anything chosen after a reading is exploratory and reported
apart (section 20).

| field | value |
|---|---|
| reading | FM: each $50K plan's evaluation and funded account read as two trading modes -- flip days from the rules, the zero-edge map of a coin trader per mode, the sizing grid, the constraint that binds, and P-14's and P-16's registered trades on each plan |
| id | RD-05 (`prereg/RD-05_firm_modes.md` at the pin); every result's `prereg_id` is `RD-05` (section 18) |
| kind | a **described reading** (E-023 (1), E-134 (1)): never carried; the operator chooses from its tables and menu |
| program family number | **none**; the next numbered family's k is unchanged by this file |
| level, pass line, pick | **none** |
| plans | 14 configurations of four firms' $50K plans, three firms read now (section 2.1); Lucid's other plans and Alpha Futures' plans join only by the rule of section 2.4 |
| parts | A flip days from the rules (7); B the sizing grid (8); C the zero-edge maps (9); D the flip measurements (10); E the binding constraint (11); F the registered trades (12) |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16, read only inside Stage 2's engine by P-14's and P-16's registered builders, in part F alone; parts A to E read no bar |
| the unit | part C: one account in one mode, a coin path; part F: one start day replayed as U1 replays it, paired with Topstep on the same start |
| judged-block reads | part F only, three purposes on the line of section 6 item 5 |
| seeds | a block of ten, six in use and four reserved (section 15) |
| confirmation | none: nothing is carried (section 14) |
| `confirmation_tests_on_this_market` | 3: NQ's three of Stage 2 D-107's three are spent (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`, `held_back_2025`); this reading adds none and reads no NQ from 2026-07-17 |

---

## 0. What a mode changes, stated truly; and what "flip" means here

**Two modes.** Each plan sells an **evaluation** (Topstep's Trading Combine, a firm's "evaluation") and, on a pass, a
**funded** account (Topstep's Express Funded Account, a firm's "sim funded"). They are separate accounts with separate
rules -- the target, the drawdown's type and lock, the daily loss limit, the consistency rule, the contract cap and
its scaling, the payout gates. A trader may trade them differently. This reading treats them as two modes: each
mode's policy is declared on its own (section 2.6), each mode is read on its own (parts B, C, E), and the two are
joined only at the switch (section 2.7).

**What a mode's policy changes.** On the coin it changes everything, since the coin is only a policy. On the
registered trades it leaves the **offered** trades unchanged -- the same entries, the same outcome of each offer at each
R, the same days in the same order -- and changes the **executed** sizes, and through them the floors, the passes, the
payouts, the fees and the router's later choices, from the first session it binds. So every registered cell is a
matched pair with its reference on every start day, the market path's luck shared.

**The word "flip".** In this reading a **flip day** is the operator's sense (E-196): a day large enough that passing
the evaluation, or reaching the first payout, takes only one or two days. A **flip-seeking policy** sizes trades for
that on purpose (section 2.6). Three other uses of the word are **not** meant:

- Stage 2's **flip stream** (Stage 2 D-338, D-343; `vendor/stage2/propedge/campaign/flip.py`), a scheduled bracket
  taken to log winning days -- not used here, and its D-343 form (the same bracket copied across accounts) is conduct
  tier 1 now;
- **contract flipping** (reversing a position): Lucid allows it ("Flipping is allowed", the vendored Lucid ledger's
  `prohibited_conduct` note); My Funded Futures' Pro policy names "No Flipping Contracts for Activity's Sake". Neither
  is a flip day, and no policy here reverses a position.

## 1. What this reading is, and what it is not

**Its job.** It answers the operator's questions of E-196 for the $50K plans, one part each:

| the operator's question (E-196, the brief Q-137) | part |
|---|---|
| two modes per plan: how each trades (risk per trade, R:R, stop width) and how the switch is handled | 2.6, 2.7, B, C |
| flip days: the fewest days to a pass and to a first payout, from the rules alone, under consistency rules that fail or extend and minimum-day rules | A |
| flip days measured: the share of passes from one or two large days; what a flip-seeking policy does against a steady one; every conduct clause that bears on it | D, 4.7 |
| the zero-edge map per plan and mode: pass and payout probability, expected net, fee cost across a grid of R:R and dollar risk | C |
| the sizing grid: the whole-contract sizes each plan's limits allow at each stop width on MNQ and NQ, under Stage 2 D-212 and D-272 | B |
| which constraint binds, per plan and mode | E |
| P-14's and P-16's registered trades on each plan, beside its zero-edge map, in RD-01's form | F |

**What it is not.** A claim of an edge; a candidate; a recommendation of a firm, a plan or a size; a design solved for
any plan (the registered state tables are not re-solved, G-1); a statement about live accounts (G-4).

**Why described rather than tested.** E-023 (1), as E-134 (1) applies it: nothing here adds a trade. The coin has no
edge by construction; the policies and contracts change money, not the trades' lift. The judged block's few
independent stretches (audit B, `docs/audits/phase0/B_objective.md`, Q3) would leave a plan or policy comparison on P
undetectable at any numbered family's level, as the red team found for payout policy (E-023).

**What the operator's choice from it will mean.** Recorded in its own decision row as a choice from a described
development reading; no registration id, no confirmation; every statement from part F is a description of the
development window, in sample. Buying any plan is a purchase: the operator's, stated and waited for.

## 2. The plans, the modes, and the user

### 2.1 The plans in scope

| id | plan | configuration | why here | terms from |
|---|---|---|---|---|
| `TS-S` | Topstep $50K Trading Combine -> Express Funded Account | Standard price path; the funded payout path Standard (`TS-S/std`, the reference) or Consistency (`TS-S/con`), chosen at activation | the reference: P-14's and P-16's registered rows | Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`) |
| `TS-N` | the same | No Activation Fee price path; the same two payout paths | the brief: both price paths | the ledger; Q-115's `subscription_fee_naf_50k`, `activation_fee_naf_50k` (the record) |
| `L6` | Topstep Labs #006 $50K Static Drawdown Combine | the funded path Standard (`L6/std`) or Consistency (`L6/con`) | new (E-197) | the record, as Q-136 records the lead's browser capture (`docs/research/firms/topstep_labs_50k_browser_2026-11-18.md`) |
| `L10` | Topstep Labs #010 $50K Daily Payouts+, end-of-day | the funded request read two ways (2.8): the Daily path (`L10/day`) or the 5 Winning Days path (`L10/5wd`) | new (E-197) | the record (Q-136) |
| `L11` | Topstep Labs #011 $50K Daily Payouts+, static | `L11/day`, `L11/5wd` | new (E-197) | the record (Q-136) |
| `RE` | My Funded Futures Rapid EOD 50K | the default (no daily loss limit) | E-196, E-197 | the record (Q-136, from `docs/research/firms/myfundedfutures_50k_2026-11-18.md`) |
| `RED` | My Funded Futures Rapid EOD 50K DLL | the daily-loss-limit version | the same | the same |
| `RI` | My Funded Futures Rapid 50K | the funded drawdown trailing intraday on equity | the same | the same |
| `PRO` | My Funded Futures Pro 50K | -- | the same | the same |
| `PRO1` | My Funded Futures Pro 50K One Day | the evaluation only differs; its funded mode is `PRO`'s | the same | the same |
| `B20` | My Funded Futures Builder 50K, the default drawdown | -- | the same | the same |
| `B15` | My Funded Futures Builder 50K, the smaller-drawdown add-on | -- | the same | the same |
| `LU40` | Lucid Trading LucidFlex 50K | daily loss limit off, standard consistency (`STANDARD_40`) | Stage 2's verified second firm (Stage 2 D-574, D-575) | the vendored Lucid ledger, through Stage 2's adapter `propedge.contract.lucid`, by import |
| `LU50` | the same | daily loss limit off, the consistency add-on (`ADDON_50`); its funded mode is `LU40`'s | the same adapter's second verified configuration | the same |

**Lucid's terms come only from Stage 2's verified record.** E-197 found Lucid's own terms, modified 2026-11-13, now
forbid copying or monitoring its content by automated means; the scout's help-centre captures of 2026-11-18 came after
that and verify nothing. LucidFlex stays on the vendored ledger, read before the clause; the scout's Lucid note is a
pointer only and no term of this reading rests on it.

**My Funded Futures' price history.** Stage 2 withdrew the firm as a second firm on price (Stage 2 D-573: one-time
evaluations against Topstep's monthly price, when a coin's plan buys many evaluations). E-196 names it again; the
zero-edge map's fee columns (9.4) are exactly the reading that question needs.

### 2.2 The modes, per plan

| plan | evaluation mode | funded mode | what makes the funded mode differ (the record states each) |
|---|---|---|---|
| `TS-S`, `TS-N` | the Trading Combine (one evaluation mode; the price path changes only the fees) | `TS/std`, `TS/con` | the payout path's gate (winning days against a cycle consistency share), the cap, the scaling ladder, the floor's start and lock |
| `L6` | the Static Combine | `L6/std`, `L6/con` | a static floor that moves to zero at the first payout, a mandatory daily limit, a ladder whose thresholds the page does not state |
| `L10`, `L11` | the Daily Payouts+ Combine, end-of-day or static | `L1x/day`, `L1x/5wd` | no consistency rule; a payout path picked at each request; a buffer under the Daily path |
| `RE`, `RED`, `RI` | the Rapid or Rapid EOD evaluation | `RE`, `RED`, `RI` | no funded consistency; a buffer, a daily cadence, a single-day profit ceiling that moves the account to live; `RI`'s floor trailing intraday on equity |
| `PRO`, `PRO1` | Pro, or Pro One Day | `PRO` (one funded mode for both) | a calendar payout clock, a buffer, a floor that moves at the first payout, a contract cap counted in contracts of either size, a discretionary sizing policy |
| `B20`, `B15` | Builder, default or add-on | `B20`, `B15` | a per-cycle consistency share and day count, a buffer, a per-request cap, an end at a stated payout count, one funded seat |
| `LU40`, `LU50` | LucidFlex at its two consistency settings | `LU` (one funded mode for both) | winning days and a net-profit gate per cycle, an end at a stated payout count (Stage 2's `LucidFundedAccount`) |

That is **13 evaluation modes and 15 funded modes** before section 5's two-ended terms.

### 2.3 Not here, and why

- **Instant- or direct-funded products** -- recorded, not modelled (E-196): they cost more capital up front, and the
  operator left their modelling to the lead on evidence. None was found at Topstep or My Funded Futures (the notes,
  each UNVERIFIED as absent where a page renders by script); Lucid's LucidDirect is named in the scout's note, a pointer
  only (2.1). Such a product joins only under a new declaration citing this one, never by section 2.4's rule.
- **The daily-loss-limit elections at checkout** where they are options on a plan that is otherwise in scope --
  Topstep's on the standard Combine (which doubles the funded caps), Lucid's DLL-on configurations (which bring On
  Demand Payouts, unmodelled by Stage 2's adapter) -- are different accounts; a later reading. My Funded Futures' Rapid
  EOD DLL is a separate product and is in scope (`RED`).
- **Topstep's $100K and $150K sizes and Labs' other drops** (not $50K); **My Funded Futures' Flex 50K** (a legacy plan),
  **Studio** (not sold at $50K), **Perps** (another company).
- **Lucid's LucidPro, LucidDaily and LucidMaxx, and every Alpha Futures plan** -- not read by any session (E-197); they
  join only by section 2.4.
- **Live accounts** at every firm (G-4).
- **Topstep's Back2Funded, resets and the evaluation inventory** -- RD-03's levers; every cell here buys no reset and no
  reactivation.

### 2.4 The conditional join rule (declared now, so nothing is chosen after the captures)

Lucid's other $50K plans and Alpha Futures' $50K plans **join this reading only if every condition below holds at the
commit of section 18's step 0 run**, and **as a whole firm's set or not at all**:

1. **Recorded.** The operator's by-hand capture (`docs/OPERATOR_SETUP.md` item 11, E-197) has been recorded by the
   rules-verifier in `config/rules_extended.yaml` and `docs/RULES_CURRENCY.md`, and the lead's row taking it is in
   `DECISIONS.md`.
2. **Every plan the firm sells at $50K with an evaluation then a funded account, at every checkout configuration whose
   price is recorded.** No plan or configuration of the firm is left out by choice; an instant- or direct-funded product
   is recorded and not modelled (2.3), and an invite-only one is out (it cannot be bought).
3. **Every term role of Appendix R resolves** for each joining configuration and mode -- to a verified entry, or to a
   rule of section 5 that this file already states. **No new rule is written for a joining plan.**
4. **Every term reaches the engine through this file's catalogue** -- a field, an adapter of section 4.3 or a gap of
   section 4.4. A plan whose terms need an adapter that is not in the catalogue does not join; it waits for a new
   declaration citing this one.
5. **Conduct.** The firm's conduct clauses are classed by section 4.7's rule, mechanically, from the recorded quotes;
   a clause the rule cannot class is labelled "unclassed: treated as prohibited by name" until a row classes it.
6. **The grids, measures, seeds, order and horizons are this file's, unchanged.** Each joining configuration adds its
   cells by section 16's formula; the lead's row taking the join states the new count before step 0 runs.
7. **Firm order.** Joining plans are run after every plan of 2.1, in the order of the lead's join row, so no cell of
   2.1 depends on them.

A capture recorded after step 0's run commit waits for a new declaration; nothing of this reading is re-run for it.
Lucid's content clause (E-197) and Alpha's automated-access clause (E-020 (2)) bar automated reading of their sites;
they do not bar code reading the recorded terms, which is all this reading does.

### 2.5 Today's terms, on every start

Each plan's terms as the record reads them (its `date_read`) are applied to every start day from 2020 to 2026, as
Stage 2 replays Topstep's current rules over its history; rule changes over the history are not modelled (G-6). A rule
that changes later is a new dated record, and every result names the record version it used (E-196).

### 2.6 How each mode trades: the declared grid and the two policies

**The coin (parts C and D).** A coin trade is a bracket on a driftless price path: a stop at `r` dollars below the entry,
a target at `w x r` above, and nothing in between -- so the chance of the target first is exactly `1 / (1 + w)` and
its expected gross profit is zero. It is stage one's binary trade at zero edge, with the floor and the daily limit
read as closer exits on the same path (the vendored `RandomDraw`, `floor_mode` "truncate", `edge_mode` "drift" at zero
edge: the barrier race `p_race(c, w r, 0) = c / (c + w r)` for a room `c` below the stop; propsim D-04 rejected the
model without it). **One coin trade a session**, stage one's reference (Stage 2 D-429's one position at a time).

**The grid, per mode (every value run; none chosen):**

| parameter | what it is | values | class | why these |
|---|---|---|---|---|
| `w` | reward-to-risk: the target as a multiple of the stop | 1.0, 1.5, 2.0, 3.0 | described | stage one's and Stage 2's reference ratios (Stage 2 D-429's screen read 1:1 to 3:1) |
| `r` | dollar risk per trade: the loss at the stop | $250, $500, $750, $1,000, $1,500, $2,000 | described | Stage 2 D-272's Combine set, with $250 below it; the top is a whole evaluation drawdown at most plans |
| `s` | stop width, in ticks of 0.25 index points (the same tick on MNQ and NQ) | part B: every multiple of 10 from 10 to 400 (40 widths); part C's costed coin: 50, 100 and 150 | described | part B is arithmetic, so the grid is fine; 50, 100 and 150 ticks are the registered designs' 12.5-, 25- and 37.5-point rungs |

Each mode has its own copy of the grid: the evaluation's `(w, r)` and the funded account's `(w, r)` are separate
axes, joined only at the switch (2.7; 9.5). **The stop width does not enter the gross coin** (its dollars are `r`
whatever the width); it enters through whole contracts and costs -- part B's sizing grid and part C's costed coin
(9.2).

**The two policies, per mode and grid cell:**

- **`steady (w, r)`** -- every trade of the mode at risk `r` and ratio `w`. On the registered trades, `steady` is the
  registered state table as it stands.
- **`flip (w, r)`** -- the flip-seeking policy: **large risk early, sized from the plan's own rules, no free
  parameter.** For the first `k` sessions of the mode in which the account trades, each session's first trade is
  sized at `r_flip`, and the account takes no other trade that session; from then on the policy is `steady (w, r)`.
  - in the evaluation, `k = k_E`, the fewest trading days in which the evaluation can pass (part A, under the plan's
    recorded consistency semantics), and `r_flip = T / (k_E x w)`, `T` the base target: `k_E` winning flip trades in a
    row pass, each day's profit an equal share inside the consistency share;
  - in the funded account, `k = k_F`, the fewest trading days to first-payout eligibility (part A), and
    `r_flip = b* / (k_F x w)`, `b*` the smallest balance at which the declared request (2.8, 9.3) reaches its largest
    value under the plan's terms (part A computes it);
  - `r_flip` is cut, trade by trade, to the room above the floor (Stage 2 D-313's room cap: a stop-out loses what was
    declared) and to the day's remaining daily limit where the plan has one; a cut is counted (10.3);
  - on the registered trades, `w` is the ratio the table chooses for the trade and the contracts are
    `min(floor(r_flip / stop dollars), the mode's full allowance)`, then the cuts above; **D-212's consistent-risk
    stand-aside is not applied to a flip trade** (the flip's point is its size), and every such trade is counted.

`flip` cells pair with their `steady` cells on common random numbers (section 15): the same coin stream, so a paired
difference is the policy's. On the registered trades, a `flip` cell pairs with its plan's `steady` cell on every start.

### 2.7 The switch between modes

- **When.** An evaluation ends at the close at which its pass condition holds (its target -- raised by its consistency
  share where the plan reads it so -- with its minimum days logged). The funded account is activated that evening and
  trades from the **next session**: Topstep's verified convention, applied to every plan. My Funded Futures' "instant"
  upgrade "the very same trading day" is read at the next session, a session later at most, labelled (G-3).
- **What carries over.** Nothing but the pass: the funded account starts at its own rules' start state (balance, floor,
  tier, counts) and its own mode's policy. On the coin, the funded mode's draws are independent of the evaluation's
  (section 15), so a pair of an evaluation cell and a funded cell is read by exact arithmetic (9.5), never re-run.
- **Fees at the switch.** The plan's activation fee, paid at activation (`activation_fee`; zero at `TS-N`, Labs, My
  Funded Futures and Lucid as their records state); a passed Topstep Combine's subscription ends at the pass.
- **On the registered trades**, the switch is the engine's own (U1's replay): the table sizes by account kind and
  state, and a funded account's flip window counts from that account's own first session.

### 2.8 The user held fixed for part F (RD-01 section 2.3's, carried)

- **The trades.** P-16's registered trades (`rc_s150_all_nr`, `rc150_dev_test.TRADES_SHA256`) as the headline and P-14's
  (A3-BRK30-CB20, U1's own builder) beside, each with its registered state table, protocol and routing (the
  longest-waiting account, one position at a time across the firm with five minutes flat, Stage 2 D-429), its purchase
  budget (P-14's), and its sizing rule's mode, headroom, stand-aside and room cap. **Only the plan's allowances, its
  per-trade costs (4.5) and the inputs its accounts hand the table (4.6) replace Topstep's.**
- **The seats.** Five accounts of every kind together, each design's own; inside every plan's caps except where a
  plan's funded cap is below five (as the notes read them, `RE`, `RED`, `B20` and `B15`; the record decides), where a
  pass waits in the engine's hold queue (U-14) and the waits are counted (12.4).
- **No resets, no reactivations, no daily-limit elections** beyond a plan's own.
- **The request rule** (RD-01 2.3, carried): at every close at which the plan's own rules make the account eligible,
  request the smaller of half the balance above start and $2,000, cut to the plan's per-request cap, its
  remaining-balance (buffer) rule and its increment; none below its minimum. Where the plan's pages give the path at
  each request (`L10`, `L11`), the path is the cell's (2.1). The payout lever is RD-02's subject, not this one's.
- **Hand entry**, at least five minutes from alert to order (E-008); one user's own accounts at one firm, each plan
  read alone.
- **Conduct.** Tier 1 untouched by the steady cells; section 4.7 classes the flip cells. Tier 2: Topstep's Responsible
  Trading Program's placement off in the headline (Stage 2 D-289), on beside at `TS` (12.3). Tier 3: the denial ladder
  beside (12.3).

## 3. Prior exposure: what has already read these plans and policies, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| stage one (`vendor/stage2/vendor/propsim/README.md`; propsim D-02, D-04, D-45) | the coin on Topstep's $50K: a fair strategy's pass ceiling, the funded martingale bound, the best static profile by exact Markov chain, the supremum over fair strategies | no data | analytic and simulated contract values | the oracles of 9.6; the TS evaluation map's (1.0, $1,500) cell is stage one's reference profile |
| stage one T5 (`vendor/stage2/vendor/propsim/edge/T5_RESULTS.md`; propsim D-44, D-45) | payout policy on the funded account | no data | exploratory; payout policy first-order | the request rule is fixed here (2.8, 9.3), not read |
| Q-12's survey (E-009) and Stage 2's propfirms ceilings (`vendor/stage2/vendor/propfirms/docs/T3_CEILINGS_DERIVATION.md`) | zero-edge ceilings from quoted terms, arithmetic; My Funded Futures among them | no data | "no firm clearly above Topstep's $50K" (E-009) | the drafter saw the propfirms note's My Funded Futures lines cited in the firm note, not its tables |
| Stage 2 D-313 | the operator's observation that over-risking in the evaluation lifts the consistency target; the consistency cap and room cap re-solved | gate paths (exploratory diagnostic) | a day's gain lifted the consistency target in some Combine attempts and delayed their passes (in words) | the coin's consistency extension is counted (9.4); the room cap cuts `r_flip` (2.6) |
| Stage 2 D-338, D-343 | the flip stream | gate paths | closed with its candidate | not this reading's flip (section 0) |
| Stage 2 D-573, D-574 | My Funded Futures withdrawn on price; Lucid's prices from its cards | -- | operating decisions | 2.1 |
| Stage 2 D-575, D-577, D-593, D-601; U1 config `p16_5+1` (D-620); program U family 5 (D-643) | Lucid seats beside Topstep's | gate paths; all starts | closed on growth and on P (as RD-01 section 3 records) | Lucid beside Topstep only; LucidFlex alone is RD-01's |
| Stage 2 D-652 (U2), E-125 | a funded account's life after its opening; P-14's evaluation trades' mean | gate paths; `results/p14_validation.csv` | most funded accounts lose the opening (D-652); the evaluation trades' mean negative on P-14 (E-125) | the flip in the funded mode acts on the opening; part F's evaluation rows rest on trades that lose on average |
| RD-01 (pinned; built, not run) | P-16's and P-14's trades on Topstep, LucidFlex (`STANDARD_40`), DayTraders and TradeDay | all starts | no result on master | **LucidFlex `STANDARD_40`'s registered rows are RD-01's** (`LU-16-s`, `LU-16-l`, `LU-14-s`, `LU-14-l`), never re-run here (12.1); TS is the same reference |
| RD-03 (pinned; built, not run) | contract-use levers, among them the No Activation Fee path on P-14 and P-16 (`naf`) | all starts | no result on master | **`TS-N`'s registered rows are RD-03's `naf` cells**, never re-run here (12.1) |
| RD-02, RD-04 (pinned) | payout policy; volatility | all starts | not run on these plans | none of their cells is read here |
| U1 (Stage 2 D-620), Q-05 (E-010), Q-44 | P-14's and P-16's own journeys; the readings beside | all starts | the reference rows; Q-44 running at this text | the references are known in full; part F's TS rows are U1's |
| program U's nine families | P on the late block against P-14 | starts from 2024 | all closed | the late block is late development, not out of sample |

**Never run:** any coin on a Labs, My Funded Futures or LucidFlex `ADDON_50` contract; any registered trade on a Labs
or My Funded Futures contract or on `ADDON_50`; any flip-seeking policy on any plan; any per-mode coin grid.

**The drafter's own reads (disclosed).** `CLAUDE.md`; the skills `worker-protocol`, `prereg-discipline`,
`contract-engine`, `feature-rules`'s name only; `DECISIONS.md` rows E-007, E-008, E-009, E-012, E-013, E-014, E-015,
E-020, E-022, E-023, E-025, E-026, E-029, E-034, E-041, E-051, E-053, E-058, E-104, E-117, E-119, E-125, E-134, E-135,
E-196, E-197 (several at their first few hundred characters); RD-01 sections 0 to 10 and RD-03 whole, for form; the
five firm notes under `docs/research/firms/` (Topstep's, the Labs capture and My Funded Futures' whole; Lucid's first
section; Alpha's first sections); Stage 2's decision rows D-117, D-145, D-212, D-272, D-301, D-308, D-313, D-338, D-429,
D-490, D-494, D-495, D-573, D-574 (several at their first lines); Stage 2's ledger notes for
`prohibited_trading_strategies` and `prohibited_conduct`; the vendored Lucid ledger's rows `eval_daily_loss_limit`,
`eval_consistency_rule`, `eval_min_days`, `funded_daily_loss_limit`, `funded_consistency_rule`, `prohibited_conduct`;
`vendor/stage2/config/fills.yaml` (its round-turn and slippage sections); code only: `vendor/stage2/vendor/propsim/
propsim.py` (whole), the header and function list of `vendor/stage2/propedge/campaign/lockstep.py`, the header and
`SizingRule` of `sizing.py`, the header of `flip.py`, the header and names of `propedge/contract/lucid.py` and
`adapter.py`, the headers and function names of `extended/firms.py` and `extended/firm_accounts.py`, the purpose rules
of `extended/reader.py`, the header of `tests/test_rd03_draft.py`. **No result file of either repository was opened.**
The seed search (section 15) printed counts only.

**What is already known of the direction (disclosed).** At Topstep a fair strategy's pass rate and funded payouts are
bounded (stage one); over-risking in the Combine lifts the consistency target (D-313); Topstep's pages say the Combine
cannot pass in one day (E-197). Nothing is known of any coin map on any other plan, of any flip policy, or of the
registered trades on any Labs or My Funded Futures plan.

## 4. The rules: where they come from, the term roles, and how each reaches the engine

### 4.1 Where the rules come from, and the merge that comes first

Every rule a cell leans on comes from Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`), the vendored Lucid
ledger (`vendor/stage2/vendor/propfirms/firms/lucid-trading/rules.yaml`, through Stage 2's adapter), or this
repository's record (`config/rules_extended.yaml`, `docs/RULES_CURRENCY.md`). **The Labs and My Funded Futures terms are
Q-136's** (the rules-verifier; queued at this text, E-197), and Q-115's No Activation Fee keys are on `wt/wt-firms` at
deb45ad (E-135); **neither is on master at this text.** This file therefore **names every term by its role** and leaves
every value to the record (the brief): Appendix R lists the roles per plan and mode with the key form the record uses
for other firms' plans (`<firm>.<plan>.<term>`, as `daytraders.eod50k.eval_profit_target`); **at the pin T-0 maps each
role to the key Q-136 records**, and a role with no recorded key is listed in section 19 as a blocker. Every value is
loaded by a loader that refuses an entry not `verified` (17.2); an `unstated`, `unverified` or conflicting term is
never loaded -- it is read by a rule of section 5.

**Both merges come before step 0** (section 18): they write under `config/`, which every identity's cover includes
(E-117), so every shared identity is held again at a commit containing them before anything of this reading runs.

### 4.2 The term roles, and how each reaches the engine

**What the engine represents** (RD-01 section 4, carried): Stage 2's `CombineAccount` (a target; a drawdown trailing
at the close and breached by any trade; its lock; a consistency share read as `max(target, best day / share)`, raising
the target and failing nothing; an optional soft daily limit) and `FundedAccount` (a floor from its start trailing at
the close to its lock, moved to the lock at any payout; winning days of a minimum; or a cycle's consistency share and
day count on the Consistency path; a request of `min(share x balance, cap)` refused below the minimum; one split; the
request-day exclusion), the sizing rule's allowance and ladder, the fees and billing, the lag, the seats, the household
rule; the seams `combine_account_cls`, `funded_account_cls`, `household_closure`, `payout_timing`. Stage one's engine
(`propsim.simulate_combine`, `simulate_xfa`) represents the same contract for one account on a binary stream, without
the daily limit or the request-day exclusion.

**Each role, per mode, reaches the engine as a field (a vendored field set to the plan's value), an adapter of 4.3
(`A-n`), a gap of 4.4 (`G-n`), or moot (it cannot bind, checked).** The table is per role; Appendix R gives every plan's
cell. "Static" means a floor that never moves.

| mode | role | `TS` | `L6` | `L10`, `L11` | `RE`, `RED` | `RI` | `PRO`, `PRO1` | `B20`, `B15` | `LU40`, `LU50` |
|---|---|---|---|---|---|---|---|---|---|
| E | target, drawdown amount | field | field | field | field | field | field | field | Stage 2's adapter |
| E | drawdown type and lock | field | static: field (the lock set at the start floor) | `L10` field; `L11` static: field | field (the lock above start) | field | field | field | adapter |
| E | daily loss limit | none | soft: A-1 | soft: A-1 | `RE` none; `RED` soft: A-1 | none | none | soft: A-1 | none (DLL off) |
| E | consistency share and what a breach does | field | field | field | field (U-15's base) | field (U-15) | `PRO` field (U-15); `PRO1` none | none | adapter |
| E | minimum trading days | implied by the share | none stated | none stated | A-2 | A-2 | A-2 | moot (one day) | implied by the share |
| E | position cap and counting | field | field | field | field | field | field | field | adapter |
| E | lifespan; inactivity | none | A-3 | A-3 | A-3 (inactivity) | A-3 | A-3 | A-3 | Stage 2's adapter (moot on the coin, G-9) |
| E | price, billing, purchase limit | field | field; A-4 | field; A-4 | field | field | field | field | adapter |
| F | floor start, type, lock | field | static, A-5 | `L10` field; `L11` static, A-5 | field | **A-6** (intraday on equity) | A-5 (U-16) | field | adapter |
| F | floor at a payout | field | A-5 (to zero) | A-5 (to zero at a daily payout) | field | field | A-5 (U-16) | A-5 | adapter |
| F | daily loss limit | none | soft: A-1 | soft: A-1 | `RE` none; `RED` soft: A-1 | none | none | soft: A-1 | none |
| F | the payout gate | field (both paths) | field, path by cell | **A-7** (Daily path); field (5 Winning Days) | **A-8** (buffer, cadence) | A-8 | **A-9** (clock, buffer, U-17) | **A-10** (cycle share, days, buffer, U-18) | Stage 2's `LucidFundedAccount` |
| F | request cap, share, minimum, increment, split | field | field | A-7; field | A-8 | A-8 | A-9 | A-10 | adapter |
| F | an end by count or ceiling | none | none | none | **A-11** (the single-day ceiling, U-19) | A-11 | A-11 (the per-user cap; reviews G-4) | A-11 (the stated count) | adapter (five payouts) |
| F | allowance and scaling | field | field (U-20's thresholds) | field | field | field | **A-12** (counted in contracts) | field | adapter |
| F | seats | field | field | field | field (below five; U-14) | field | field | field (below five; U-14) | moot |
| both | per-trade costs | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 |
| both | news windows | G-2 | G-2 | G-2 | G-2 (a count) | G-2 | G-2 | moot (unrestricted) | -- |

### 4.3 What the engine cannot represent: adapters in `extended/` (declared; built after the pin)

Every adapter subclasses or wraps a vendored seam or copies a vendored body under Q-71's pattern (a guard refusing
unless the vendored source hashes to its pin, a proof that the copy with its marked lines removed parses to the vendored
one, marked additions only, each off by default); none edits `vendor/` and none substitutes a vendored attribute during
a call (E-011, Q-47). **Each adapter has two forms -- an account class for part F (on `CombineAccount` /
`FundedAccount`, RD-01's pattern in `extended/firm_accounts.py`) and a vectorised addition to part C's coin engine
(A-0) -- and the two are held equal on scripted streams, account for account (T-3).** With every switch at its Topstep
setting each is the vendored behaviour bit for bit (T-1, T-2). If any cannot be built that way, the build stops and
reports; this declaration does not fall back.

| id | adapter | what it adds |
|---|---|---|
| A-0 | the coin engine (`extended/modes_engine.py`) | `propsim.simulate_combine` and `simulate_xfa` copied verbatim with marked additions A-1 to A-12 (each off by default) and three more: separate evaluation and funded policies with `flip`'s schedule (2.6); a costed coin draw (9.2); per-session records of each account's day P&L, gates and endings for parts D and E (A-13). With every addition off, every output array equals the vendored function's on the same seed and draw, bit for bit |
| A-1 | a soft daily loss limit | the day's trading ends when its loss reaches the limit; the account is not failed; the room a trade is handed is the smaller of the room above the floor and the day's remaining limit (as `lockstep.py` hands it, RD-01 2.3). A plan whose record reads the limit as a failure uses the hard form (the account ends) -- by its record, never by choice |
| A-2 | evaluation minimum trading days | a pass needs that many sessions with at least one executed trade (RD-01's A-4 form: "a trading day" is a session with a trade) |
| A-3 | evaluation lifespan and inactivity | the evaluation ends unpassed at its lifespan; an account with no trade in the stated window ends (funded: its profit forfeited where the record says so); calendar days exact in the replay, translated to sessions on the coin and in the gate by Stage 2's rule (`billing_days` sessions per `billing_period_calendar_days`), the rows labelled |
| A-4 | a purchase limit | the campaign's evaluation supply for that plan capped as the record states it (in total, or per calendar month); on the coin, per-attempt readings are unaffected and the per-user arithmetic of 9.5 applies it |
| A-5 | the funded floor's own rules | a static floor; the floor's move at a payout to the record's level (zero, or the lock); `PRO`'s two readings (U-16) |
| A-6 | the intraday equity trail (`RI`) | the floor trails the account's equity peak inside each trade: on the coin, exact under the coin's own model (9.2); on the registered trades, bracketed as RD-01's A-7 brackets Quick Pay's peak (U-21) |
| A-7 | Labs' Daily path | eligibility each session once the balance clears the buffer and the minimum; one request a session at most, within the record's minimum and maximum, from profit above the buffer (or the day's profit, U-22); the floor to zero at the first daily payout; the request after the profit locks (U-22) |
| A-8 | My Funded Futures' buffer gate and cadence | a request needs the balance at the buffer plus the minimum and leaves the buffer (DayTraders' A-3 pattern, never the vendored `keep_balance`, which is a policy); the first request not before the stated time after the first trade; later requests after the stated net profit since the last |
| A-9 | `PRO`'s payout gate | the calendar clock from the first trade and between requests; the buffer at two readings (U-17); the minimum; no winning days |
| A-10 | Builder's payout gate | the cycle's consistency share and its day count (the engine's Consistency-path fields), the buffer and first-payout balance, the time after the first trade, the profit since the last request, the per-request cap; the first cycle's base at two readings (U-18) |
| A-11 | ends by count or ceiling | Builder's and Lucid's end at the stated payout count (Stage 2's `_after_payout` seam, `lockstep.py` 854); My Funded Futures' single-day profit ceiling that moves the account to live and forfeits the excess (U-19); `PRO`'s per-user lifetime cap with forfeiture |
| A-12 | an allowance counted in contracts | `PRO`'s funded cap counted in contracts of either size (a micro counted as a mini), which the micro-denominated ladder cannot express |
| A-13 | the records for parts D and E | each account's day P&L series, the session each gate first holds, its ending and cause, on the coin (A-0) and in the replay (Q-94's recorder and the account classes' counters); off by default, every output equal with it off and on |
| A-14 | the composition (`extended/modes_plans.py`) | each configuration's contract applied to a design's replay and gate arguments and to the coin engine, as RD-01's A-1 (`extended/firms.py`) does; `TS` leaves every argument unchanged (tested equal); `LU40` and `LU50` by Stage 2's `rc150_firm_split.lucid_setup` at each configuration |
| A-15 | the readings (`extended/modes_reading.py`, `scripts/modes_*.py`) | parts A to F in section 18's order; the checks of section 13; the menu; RD-02's 9.2 functions imported (`extended/pp_reading.py`) |

### 4.4 What is not modelled, listed as gaps

| id | gap | how it is shown |
|---|---|---|
| G-1 | the registered state tables were solved for Topstep's Standard path (Stage 2 D-501) and are not re-solved for any plan or mode; "the design traded there" includes 4.6's mappings | every part-F row is the design traded there, not the best design for that plan; labelled "first-order, the table fixed" |
| G-2 | news windows: Topstep's Tier-1 caps (Labs' static Combine row among them, minis blocked); My Funded Futures' funded Tier-1 blackout (two minutes either side); the engine models no such exit | the designs' own entry rules (CHARTER section 4: report-day entries after 07:35 CT; FOMC days out) leave only FOMC-minutes days, **counted** (12.4) by E-050's pinned calendar; the coin has no calendar, so the coin maps carry no news rule, labelled |
| G-3 | the switch's same-day upgrade at My Funded Futures; identity verification at Labs | read at the next session (2.7); a session at most |
| G-4 | every live move: Topstep's, Labs', Lucid's, My Funded Futures' (Rapid's ceiling move, Pro's reviews after three payouts or a stated profit, Builder's after its count), each closing or merging the simulated accounts | live accounts not modelled: an account moved ends; its balance not credited at the strict end; RD-01's Lucid household readings carried; the reviews counted, not modelled |
| G-5 | discretionary programs and reviews: Topstep's Focused Trader Program; My Funded Futures' Pro Consistent Trading Policy; the catch-all clauses | 4.7's labels; tier 3 priced by the denial ladder beside; the Focused Trader models not run here (their thresholds are unpublished and their binding models are Topstep-standard; the gap named on every row) |
| G-6 | rule changes over 2020-2026 | today's terms on every start (2.5) |
| G-7 | My Funded Futures' price-limit rule (funded) | not modelled; every such row says so |
| G-8 | the Simulated Trader Agreement behind login at My Funded Futures, which controls its Terms in a direct conflict | not read; no term rests on it; every My Funded Futures row says so |
| G-9 | the coin trades every session; a user who skips sessions is not modelled | the coin rows say so; the inactivity rules are therefore moot on the coin (checked) |
| G-10 | holiday hours, the payout request screen's amount choice, processing within a session | as in every registered row; lags read at their brackets (U-5) |

### 4.5 Per-trade costs (the cost rule, per plan; declared)

Each registered design prices a trade's fee at the contracts it holds -- as many minis as fit, the rest in micros
(Stage 2 D-324) -- from its blocks' per-trade fee (RD-01 4.8). A-14 sets each plan's round-turn schedule; spread,
slippage and ticks are each design's own at every plan.

| plan | schedule (round turn: MNQ, NQ) | from | what it leaves open |
|---|---|---|---|
| `TS`, `L6`, `L10`, `L11` | Topstep's all-in schedule (`vendor/stage2/config/fills.yaml`, `round_turn_by_instrument`; 8284213) | the registered schedule; Labs accounts trade on Topstep's platform | that Labs' fees equal the standard Combine's is a reading, labelled, until the record states it (U-23) |
| `RE` ... `B15` | My Funded Futures' stated "Total Cost Round Trip" for NQ and MNQ (the record) | the firm's instrument table | whether it is all-in: read at both ends where the record leaves it open (RD-01's U-12) |
| `LU40`, `LU50` | Topstep's schedule, as Stage 2 D-575 reads Lucid (conservative) | RD-01 4.8 | Lucid rows conservative in this term |

**The costed coin (9.2)** uses the same schedule, at the contracts part B gives, plus the slippage of
`fills.yaml`'s active profile (`assumed`: its entry and stop ticks; a target fills at its limit), valued at the
instrument's tick value from `vendor/stage2/propedge/execution/instruments.py`, read, never typed.

### 4.6 What each plan's accounts hand the table (RD-01 4.9's rule, extended; declared)

The registered tables read `win_days` (0 to 5, 5 meaning eligible), `since_pay` and `request_day_next` from each funded
account (`risk_policy.account_state`). RD-01 4.9's rule is carried unchanged: `win_days = min(5, max(0, 5 - the
plan's own days still needed))`; **held at 4** when the plan's day count is complete but another of its gates still
blocks the request; `since_pay` the plan's profit since the last request; `request_day_next` 1 only on a session the
plan excludes from its count after a request. For the new plans:

| plan, mode | the plan's own days | `win_days` read by the table | `request_day_next` |
|---|---|---|---|
| `TS/std`, `L6/std`, `L1x/5wd` | Topstep's winning days | the engine's own | the engine's |
| `TS/con`, `L6/con` | the Consistency path's trading days | not run on the registered trades (the tables solve the Standard path; 12.1) | -- |
| `L1x/day` | none: eligible once the buffer and minimum clear | 5 when eligible; 4 while the buffer blocks | 0 |
| `RE`, `RED`, `RI` | none: the buffer, the cadence and the profit since the last request | 5 when eligible; 4 while a gate blocks | 0 |
| `PRO` | none: the calendar clock and the buffer | 5 when eligible; 4 while the clock or the buffer blocks | 0 |
| `B20`, `B15` | the cycle's day count | `min(5, max(0, 5 - days still needed))`; 4 while the share, the buffer or the time blocks | 0 |
| `LU` | Lucid's winning days (RD-01's row) | the engine's own | 0 |

**An evaluation at or above its target with days still owed** (`RE`, `RED`, `RI`, `PRO`: A-2): RD-01's TradeDay rule,
carried -- at most one trade a session at one micro and the table's R until the days are logged, the pass read at the
first close with the days logged and the balance at or above the (consistency-raised) target. Tested (T-4) and counted
(12.4).

### 4.7 Conduct: every clause that bears on big days and flip-seeking, classed now

**The class rule (mechanical, applied to each clause's recorded quote):**

- **N -- named.** The clause names the pattern -- high-risk attempts for a large win, inconsistent or maximum sizing, or
  stepping size up after losses -- and states a prohibition or a consequence (removal, restriction, termination,
  forfeiture, denial). **A flip-seeking policy at a firm with an N clause that its words reach is labelled "prohibited
  by name (clause, article)", reported in its own section of every output and of the menu, never carried, never offered
  as a choice** (conduct tier 1, as the brief rules it). A `steady` cell its words reach is labelled the same way.
- **D -- discretionary.** The clause gives the firm discretion over an unnamed or unsized pattern ("substantially
  larger", a catch-all, an unpublished threshold). Tier 3: priced by the denial ladder beside (E-013 (1)); the cell is
  labelled with the clause.
- **P -- a program.** Topstep's Responsible Trading Program: tier 2, modelled by the placement beside, off in the
  headline (Stage 2 D-289).
- **A clause whose recorded text differs from the quote below** is labelled "clause text changed: class not applied" and
  read as N until a row classes it.

**The clauses, from the notes' verbatim quotes, each to be verified by the record before its label prints:**

| firm | clause | source | quote (the notes') | class | reaches |
|---|---|---|---|---|---|
| Topstep (all its plans, Labs included) | **Account Stacking** | 10305426 (Stage 2's `prohibited_trading_strategies`) | "Repeatedly trading aggressively, hitting the Maximum Loss Limit (MLL) in one account," / "then switching to another account and repeating." / "The goal is to run high-risk attempts until a large win occurs." / "This exploits risk parameters and is not permitted." | **N** | every `flip` cell at `TS`, `L6`, `L10`, `L11`, coin and registered: the flip sizes for a large win early and the journey buys again after a loss |
| Topstep | account stacking in Prohibited Conduct | 10296582 (`prohibited_conduct`) | "Account stacking -- repeatedly hitting the Maximum Loss Limit in one account and switching to another" / "to repeat high-risk attempts" | N | the same |
| Topstep | Terms of Use s.8, relative size | `tou_s8_relative_position_size` (the record) | sizes "substantially" larger than one's other trades fall short of "market standard risk management" | D (E-013 (1)) | every `flip` cell and the registered tables' bold openings |
| Topstep | RTP trigger | 13620045 (`responsible_trading_program`) | "You max position a majority of your trades"; "Multiple accounts hit the Maximum Loss Limit in one day" | P | `TS` cells beside (12.3); counted everywhere at Topstep's plans |
| Topstep | maximum size into news | 10305426 | "Purposefully trading your full Maximum Position Size directly into a scheduled major news event." | tier 1 (Stage 2 D-145) | counted (12.4): a flip trade at the full allowance on an FOMC-minutes day |
| Topstep | "Big spike days" | 8284197 | "Big spike days don't build funded traders, consistency does." | none (a statement, no prohibition) | printed beside part A |
| My Funded Futures | Pro's Consistent Trading Policy | H17573707, H8694840 | "maxing contracts on every trade, contract flipping, inconsistent position sizing"; "Uniform Position Sizing, Stops, and Targets", "Avoidance of Maximum Contract Sizes"; "Violations can result in restrictions or account termination." | **N** | every `flip` cell in `PRO`'s funded mode; **and the registered tables' state-varying sizes in `PRO`'s funded mode** (on its words) |
| My Funded Futures | high-risk catch-all | Terms s.23.1.11, s.23.3 | "high-risk, or otherwise posing an undue risk"; "The Company reserves the right to determine, at its own discretion" | D | every `flip` cell at `RE` ... `B15` |
| My Funded Futures | tight brackets in the simulator | H8444599 | "Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted." | tier 1, unsized | the designs' brackets (RD-01 G-14's pattern): not modelled, labelled |
| Lucid (LucidFlex, Stage 2's record) | martingale | the vendored Lucid ledger, `prohibited_conduct` | Martingaling is "strongly discouraged" but not prohibited | none | -- |

**Two things the lead should rule on (section 19).** (1) Stage 2 D-145 priced "account stacking and many purchases" at
tier 3, and RD-03 4.5 labels the registered designs' stacking exposure there; this text labels **flip-seeking** at
Topstep N, because the clause's stated goal ("run high-risk attempts until a large win occurs") is the policy's
declared purpose. (2) Pro's policy, on its words, reaches the registered tables' own state-varying funded sizes. Both
labels change nothing that is computed; they decide what the menu may offer.

## 5. Unverified, unstated and conflicting terms, each read by a rule fixed now

### 5.1 The rules

RD-01's U-1 to U-12 are carried unchanged (RD-01 5.1), in brief: **U-1** a price listed differently on the plan's own
pages -- both ends of the listed bracket; **U-3** a fee no page states -- $0, every money figure labelled an upper bound
in it; **U-4** conflicting pages on a term -- both read; **U-5** an unstated lag -- the bracket of the verified lags of
the plans here; **U-6** a stated rule whose reach is unstated -- the reading that helps the user least at the strict
end, the other concrete reading at the lenient end; **U-7** a term that cannot bind -- not read, checked; **U-8** no
unsized relaxation assumed; **U-9** a verified rule whose data the trades lack -- bracketed; **U-10** no limit invented;
**U-12** a price whose basis is unstated -- listed all-in at the lenient end, decomposed fees on top at the strict end.
New here:

- **U-13. A Labs term the Labs page leaves unstated** (#006's funded winning days, share of balance, minimum and split;
  the daily limit's softness; the funded lock of the end-of-day versions; the consistency rule's breach behaviour) --
  **read from Topstep's own general article for that term** (Stage 2's verified ledger or the record), labelled "from
  the general article". Labs accounts are Topstep accounts; where the general article and the Labs page differ, the
  Labs page wins.
- **U-14. A pass at a funded cap below the user's seats** (`RE`, `RED`, `B20`, `B15`, as the notes read their caps) --
  the engine's hold queue, no expiry, labelled; the waits counted (12.4).
- **U-15. My Funded Futures' evaluation consistency base** ("total evaluation profits": net profit, or the sum of
  winning days) -- both ends: strict, the account's net profit (the engine's reading, the smaller base); lenient, the
  sum of its winning days.
- **U-16. Pro's funded floor before the first payout** (the words "continues to trail" until the first payout and then
  "moves to" the lock; the plan data's lock) -- both ends: strict, it trails without a lock until the first payout and is
  then set to the lock; lenient, it trails and locks at the lock.
- **U-17. Pro's buffer** (conflict: the newer page's "Buffer must be cleared" against the older page's share of profits
  withdrawable before the buffer clears) -- both ends: strict, cleared; lenient, the older page's share inside it.
- **U-18. Builder's first-cycle consistency base** (all profit since activation, or profit above the buffer) -- both
  ends: strict, profit above the buffer (the smaller base); lenient, all profit since activation.
- **U-19. My Funded Futures' single-day profit ceiling's reach** (the account moves to live, the excess that day
  forfeited) -- U-6: strict, the account ends at that close, its balance not credited, every other simulated account of
  the firm closed at the move; lenient, the excess forfeited, the account's requestable balance above its buffer paid at
  its split, then that account alone ends.
- **U-20. Labs #006's funded scaling thresholds** ("2/3/4", thresholds unstated) -- both ends: strict, the entry tier
  for the account's life (Stage 2's `entry_tier` mode); lenient, the standard $50K ladder's thresholds with the top at
  the Labs cap.
- **U-21. The intraday equity trail on the registered trades** (`RI`) -- U-9: bracketed between the two extremes the
  trades' own outcomes allow, as RD-01 5.4 brackets Quick Pay's peak, both read.
- **U-22. Labs' Daily path amount and timing** ("Payouts come from profits made during the trading day, locked in at
  4:00 PM CT") -- both ends: strict, a request draws at most that session's own profit above the buffer and is made at
  the next session's close; lenient, any profit above the buffer, requested at the same close.
- **U-23. A Labs account's per-trade costs** -- Topstep's schedule (4.5), labelled, unless the record states another.
- **U-24. A conflict on a purchase limit** (Labs #006: a limit per trader in its table against the banner's limit per
  month) -- both ends: strict, the limit in total; lenient, the same limit each calendar month (21 sessions in the gate).

**The strict and lenient corners** (RD-01 5.1, carried). Each two-ended term has a strict end (the one that helps the
user least) and a lenient end, named above, so neither corner is chosen after a look. A configuration's **strict
corner** has every two-ended term at its strict end at once; its **lenient corner** every one at its lenient end. The
corners are bounds only for the terms that move cash alone on the same path (the prices, U-3's fees, the lags, U-19's
lenient payment); for the others they are the two declared corners, not bounds. **Prices and fees never add a run**:
with the replay's bankroll unbound and the coin's attempts independent, a price moves only cash, so both ends are exact
arithmetic on the same runs (RD-01's A-10).

### 5.2 Every such term, its expected status and its declared reading

The status column is the notes' (the record's at the pin replaces it; T-0 recomputes the corners from the record). A
term the record verifies is a field, and its corner collapses.

| plan | mode | term | expected status (the notes) | strict end | lenient end | rule | adds a run? |
|---|---|---|---|---|---|---|---|
| `TS-N` | both | the price path | verified (Q-115) | -- | -- | -- | no (fees re-priced) |
| `L6` | F | winning days, share, minimum, split | absent on the page | Topstep's general terms | the same | U-13 | -- |
| `L6` | F | the scaling thresholds | unstated | the entry tier for life | the standard thresholds, the Labs top | U-20 | **yes** (coin and part F) |
| `L6` | E | the purchase limit | conflicting | the limit in total | the limit each month | U-24 | part F only |
| `L6`, `L10`, `L11` | both | the daily limit's softness | unstated at #006; "soft breach" on topstep.com/labs for Daily Payouts+ | Topstep's general article (soft) | the same | U-13 | -- |
| `L10`, `L11` | F, `day` | the Daily path's amount and timing | stated with an unstated reach | that session's profit, next close | any profit above the buffer, same close | U-22 | **yes** |
| `L10` | F | the end-of-day floor's lock | unstated | Topstep's general article | the same | U-13 | -- |
| `RE`, `RED`, `RI`, `PRO` | E | the consistency base | unstated | net profit | sum of winning days | U-15 | **yes** |
| `RE`, `RED`, `RI` | F | the single-day ceiling's reach | stated with an unstated reach | ends, not credited | paid above the buffer, then ends | U-19 | **yes** |
| `RE`, `RED`, `RI` | F | the request's maximum | a plan-data reading (the whole profit above the buffer) | -- | -- | U-7: the declared request never exceeds it (checked) | -- |
| `PRO` | F | the floor before the first payout | ambiguous | trails, no lock, then set | trails and locks | U-16 | **yes** |
| `PRO` | F | the buffer | conflicting | cleared | the older page's share inside | U-17 | **yes** (same corner as U-16) |
| `B20`, `B15` | F | the first cycle's base | implied by an example | profit above the buffer | all profit since activation | U-18 | **yes** |
| `RE` ... `B15` | F | the payout fee | unstated | $0, upper bound | the same | U-3 | -- |
| `RE` ... `B15` | F | the processing lag | conflicting ("instantly"; hours; 24 business hours) | one session | none | U-5 | part F only, cash timing |
| `RE` ... `B15` | E | the price | list and promotion prices | the list price | the promotion's | U-1 | no (arithmetic) |
| `RE` ... `B15` | both | the commission basis | stated as "Total Cost Round Trip" | fees on top (RD-01's decomposition) | as all-in | U-12 | no corner of its own: the costed coin and part F read it at each corner's own end, a single corner at the strict end |
| `RI` | F | the intraday trail on the registered trades | verified; the data lack the peak | the pessimistic bound | the optimistic bound | U-21 | part F only (exact on the coin, 9.2) |
| `LU50` | F | the live move's reach | verified; reach a reading | RD-01's strict | RD-01's lenient | U-6 | part F only |
| `LU40`, `LU50` | F | funded fee, payout fee | unverified | $0, upper bound | the same | U-3 | -- |
| every plan | -- | a term the record finds conflicting or unstated that this table does not list | -- | by section 5.1's rules, the strict end the one that helps the user least | -- | 5.1 | as the rule says; listed in section 19 before the pin |

## 6. Data, blocks, the unit and the seal

1. **Parts A, B and E's arithmetic read the rules record only.** No bar, no trade, no result file.
2. **Part C reads nothing but its seeds**: the coin is synthetic. Its runs are heavy by compute, not by data (18).
3. **Part F's unit** is U1's: one development start day, a fresh unbound bankroll and fresh accounts, the design's
   trades replayed in historical order for up to 252 sessions plus U1's exact-length runs (21, 63, 90, 126)
   (`vendor/stage2/scripts/user_journey.py`, `customer_slices.replay`), through RD-01's runner (`extended/firms.py`
   `run_plan`) with A-14's contracts. A month is 21 sessions; `USER_MILESTONES.md`'s definitions unchanged. The arms:
   `verdict` (every R at its registered bound) the headline, `point` beside; the bound was estimated on the whole
   development window, so an early-block reading on the verdict arm is a function of 2024-2026 through that one
   constant (reading PP's N2). Pairing: every plan and `TS` on the same starts, blocks and seeds; every `flip` cell and
   its `steady` cell likewise. **The blocks, per measure** (RD-03 section 5's table of horizons, carried): all starts
   with h sessions left (the headline), the early block and the late block from 2024-01-02, by `u_select.block`;
   nothing chosen on any block.
4. **No NQ from 2026-07-17** is on disk or read.
5. **The judged block's seal (E-026, E-041).** Part F's replays and gates read the bars inside Stage 2's engine, so the
   runner authorises those reads with `extended.reader.authorise_engine_read` before the engine runs, from a clean
   checkout of a committed commit, under the purposes on this line:

   - **Judged-block reads:** `modes_scorecard`, `modes_ladder_beside`, `modes_gate_beside`

   - `modes_scorecard`: part F's replays at 0 % denial with the placement off -- the references, every steady corner
     and every flip cell, both arms;
   - `modes_ladder_beside`: the denial ladder and the placement beside (12.3);
   - `modes_gate_beside`: the gates beside (12.3).

   None is a choosing or fitting purpose (the reader's `CHOICE_WORDS`; T-0). The identities run from `identity/*.py`
   under the purpose `identity` and their own decision row, never under this line (13.1). Parts A to E read no bar and
   need no purpose; if the build finds any part of them reading a bar, it stops and reports. **Once per purpose**: a
   restart, a rerun after a fix, or the failure protocol's replication is a further judged read under `repeat=` (E-053).

## 7. Part A: flip days from the rules alone (step 0)

**What is computed, per configuration and mode, by code from the record (17.2), never typed:**

1. **The fewest trading days to a pass**, `k_E`: the least `n` such that `n` winning sessions can meet every pass
   condition at once -- the target; the consistency share `c` (each day at most `c` of the profit, so `n >= ceil(1/c)`
   when every day is equal, and no smaller `n` can meet it); the minimum trading days; a lifespan. Under **both**
   consistency semantics: the plan's recorded one (`extends`: a larger best day raises the target to `best / c`;
   `fails`: it ends the account), and the other, labelled "if the rule failed instead" or "if it extended instead".
2. **The fewest further days after a first day of profit X**, for X at the consistency allowance `c x T`, at `0.75 T`,
   at `T` and at `1.5 T` (T the base target): under `extends`, the raised target `X / c` and the further days, none
   larger than X; under `fails`, whether the account survives. This is the rules' own answer to "what does a big day
   do".
3. **The fewest trading days to first-payout eligibility**, `k_F`, and **the fewest sessions elapsed** (calendar clocks
   translated by Stage 2's rule, 4.3 A-3; the replay's exact dates beside in part F): winning days and their minimum,
   the cycle's share and day count, the buffer and the minimum, the time after the first trade, the profit since the
   last request -- under both semantics of a funded consistency rule.
4. **`b*`**: the smallest balance above start at which the declared request (2.8 for part F; 9.3's for the coin)
   reaches its largest value under the plan's terms -- the flip's funded target (2.6).
5. **The single-day bounds:** whether any rule caps a day's profit (My Funded Futures' ceiling) or a day's loss (a
   daily limit), and the largest winning day that keeps a pass in `k_E` days.
6. **`r_flip`** for every mode and `w` of the grid, and whether the room or the daily limit cuts it at the mode's
   start state.

**The stated-fewest check (refusing).** Where the record quotes a firm's own statement of the fewest days -- Topstep's
one-day FAQ and its sentence on passing in as few days as its share allows (8284197, 8284208); LucidFlex's fewest days at
each consistency setting (the vendored ledger's `eval_min_days` note); My Funded Futures' one-day statements for Builder
and Pro One Day -- the computed `k_E` must equal it. A difference stops step 0: the rule's reading or the
record is wrong, and the failure protocol applies.

**Output:** `results/modes_rules.csv`, section `flip_days` (one row per configuration, mode and semantics: `k_E` or
`k_F`, the sessions elapsed, the rule that binds the count, X's further days), section `stated_check`, and section
`flip_sizes` (`r_flip`, `b*`, the cuts).

## 8. Part B: the sizing grid, and the size that binds (step 0)

**For every configuration, mode and state** -- the evaluation's fresh state; each funded tier of the plan's scaling
ladder (a balance band per tier, from the record); at `PRO` the contract-counted cap (A-12) -- **every stop width `s`
of the grid (10 to 400 ticks in tens), every dollar risk `r` of the grid, and three instrument mixes** (MNQ alone; NQ
alone; mixed -- as many minis as fit, the rest in micros, D-324), the arithmetic below, from the record and
`instruments.py`'s tick values:

- **the allowance** in micro-equivalents (the plan's counting rule: ten micros a mini, or one a contract at `PRO`'s
  funded cap), and beside it Stage 2 D-117's headroom cap (three quarters of the allowance, rounded down), labelled the
  registered designs' operating rule, not the firm's;
- **the contracts for `r` at `s`**: `n = min(floor(r / (s x tick value)), the allowance, floor(L / (s x tick value)))`,
  where `L` is the smaller of the room above the floor at that state and the daily limit where the plan has one;
- **D-212's consistent risk**: whether `n x s x tick value` carries at least 90 % of `r`; **D-272's stand-aside**: a
  trade below that, or below the registered sizing rule's cost floor per contract (read from the registered rule's
  `stand_aside`, never typed), is no trade in that state -- printed as "stood aside";
- **the size-binding constraint**: whichever of the dollar risk, the allowance, the room and the daily limit gives the
  fewest contracts (ties named in that order); "the allowance binds" also marks the trade at the cap (Topstep's RTP
  trigger 2 counts such trades; My Funded Futures' Pro policy names them);
- **the cost share**: the round-turn fee and the assumed slippage at `n` contracts, over the realised risk;
- **the consistency fit**: whether one winning trade at `(w, r)` exceeds the mode's consistency allowance (`c x T` in the
  evaluation; the cycle share at its least base in the funded mode), so that one win raises the target or blocks the
  request;
- **the allowed set per mode**: the `(r, w, s, mix)` at which a trade is sizeable under D-212 and inside every limit --
  the "risk per trade, R:R and stop width allowed per mode" of the brief.

**Output:** `results/modes_rules.csv`, sections `sizing` (one row per configuration, mode, state, mix, `s`, `r`) and
`allowed`. The table is arithmetic: it draws nothing and reads no trade. Part F's mechanics (12.4) print, beside it,
the share of each design's trades sized as each row says, from the replay itself.

## 9. Part C: the zero-edge map of each plan and mode (step 2)

### 9.1 The cells

For every **mode-corner** (each evaluation mode and each funded mode of 2.2, at each of its corners where section 5.2
says a term adds a coin run), every `(w, r)` of the grid:

- `steady (w, r)` and `flip (w, r)` on the **gross coin** -- 48 runs;
- `steady (w, r)` on the **costed coin** at each of 50, 100 and 150 ticks, mixed sizing -- up to 72 runs, a cell run
  only where part B finds it sizeable under D-212 at the mode's start state (the rest printed "not sizeable at s");
- **`RI`'s funded mode** is read only at the `(w, r)` with `(w + 1) r` at most the funded drawdown amount (9.2); the
  rest printed "not read: a winner's in-trade drawdown unmodelled".

**Accounts per run: 50,000**, each its own coin stream (section 15). **One trade a session.** The evaluation runs to
its resolution or **504 sessions** (unresolved counted, fees accrued to then); the funded account to its ending or
**504 sessions** from activation (the gate's funded horizon).

### 9.2 The coin, exactly

- **Gross:** the vendored `RandomDraw` through `adapter.BinaryDraw` at zero edge (`floor_mode` "truncate", `edge_mode`
  "drift", theta zero): the trade's room `c` is the smaller of the stop, the room above the floor and the day's
  remaining limit; it wins `w r` with probability `c / (c + w r)` and loses `c` otherwise. The engine applies the floor;
  the draw never does (the skill's rule).
- **Costed (`extended/modes_engine.py`'s `CostedCoinDraw`):** the same driftless bracket at the **realised** risk
  `r' = n x s x tick value` (part B's contracts, D-212), its target at `w r'`, and the costs of 4.5 subtracted at the
  exit -- the round-turn fee at `n` contracts and the entry tick on every trade, the stop tick on an exit at the stop,
  the room or the daily limit. Its expected profit is minus the expected cost, exactly.
- **`RI`'s intraday equity trail, exact on the coin.** For a driftless path racing a lower exit at `-a` (the trade's
  room `c`) against a target at `+b`, a losing trade's highest point `m` has the law
  `P(m >= x | loss) = a (b - x) / (b (a + x))` for `0 <= x < b` -- the vendored adverse-excursion law
  (`propsim.mae_survival_given_win`) with the lower exit and the target exchanged. A losing trade's peak is drawn from
  it by inverse transform on its own stream (section 15, so the outcome stream is the same as `RE`'s); a winning
  trade's peak is its target. After each trade the floor is the lower of the lock and the trail from the account's
  equity peak, that trade's own peak included. **When `(w + 1) r` is at most the drawdown amount, no trade can reach a
  floor its own peak raised** (a trade's whole range is less than a drawdown, and its room at most its stop), so a peak
  acts only on later trades and this is the whole rule, exactly; outside that set a trade can be stopped by the floor it
  raised -- a path law this text does not declare -- and those cells are not read (9.1).
- **The request (the coin's, declared):** the plan's own maximum at every eligible close -- stage one's reference rule
  (`payout_frac` 1) -- cut to every remaining-balance rule and increment; where the record states no maximum, the
  reference's amount, `min(0.5 B, $2,000)` (U-7, U-10). It is the contract's value at its own maximum request, not a
  payout policy. (Part F keeps RD-01's request rule, 2.8, for comparability with the registered rows.)

### 9.3 What each run measures

**Evaluation mode:** the pass probability with its Monte Carlo standard error; the shares failed at the floor, expired
(a lifespan), ended inactive (0 on the coin, checked) and unresolved at 504; sessions to a pass (mean, p10, p50, p90,
among passes); the evaluation fees per attempt (subscriptions accrued while it lives; a one-time price) at both price
ends; the share of passes whose target the consistency rule raised and the sessions it added; the minimum-days waits;
the **large-days count** of 10.1 for every pass; the **last gate to open** of 11.1; the mean balance at resolution (an
oracle, 9.6).

**Funded mode:** the probability of any payout and of a first payout within 21 and 63 sessions of activation; sessions
to the first payout (mean, p10, p50, p90, among those paid); the mean gross payouts and the mean net to the user (the
split, less payout fees); the mean number of payouts; the endings by cause (the floor; a count end; the ceiling's live
move; the horizon); the activation fee; the large-days count of 10.1 for every first payout; the last gate to open; the
mean of the balance plus gross payouts plus forfeitures at the horizon (an oracle, 9.6).

### 9.4 The fee columns

Per attempt: the evaluation's fees (both price ends of U-1); the activation per pass; fees per pass (fees per attempt
over the pass probability: a user buying until a pass, attempts independent); fees per first payout (fees per pass over
the funded payout probability); the payout fees. At `TS-N` every fee re-priced on `TS-S`'s runs, exactly.

### 9.5 The two modes joined (exact arithmetic, no run)

For every configuration, every evaluation cell (a policy and a `(w, r)`) is joined with every funded cell of its funded
mode, at matching corners:

- **the net per attempt** -- minus the evaluation's fees, plus the pass probability times (the funded mean net less the
  activation) -- stage one's `attempt_ev` form, reproduced to 1e-9 on the same inputs (9.6);
- **the fee cost per attempt**, and **the pass-and-payout probability per attempt** (the pass probability times the
  funded payout probability);
- **the net per funded journey** -- a user buying until a pass, then trading the funded account: minus the fees per
  pass, less the activation, plus the funded mean net;
- **under a purchase limit** (A-4): the chance of at least one pass within the plan's limit of attempts, and the net
  over that many attempts;
- **sessions from the first purchase to the first payout**: the exact convolution of the two empirical distributions
  (sessions to a pass, the switch's session, sessions to the first payout), independent by construction (section 15);
  its mean and p10, p50, p90.

The joined tables are printed whole, per configuration -- a matrix of evaluation cells by funded cells. **No cell is
marked best**; the diagonal (the same `(w, r)` in both modes) is printed as a slice, labelled "one policy in both modes
(stage one's form)", and the flip-flip and steady-steady blocks are labelled.

### 9.6 Oracles (an output outside them is an engine error, never a finding; each stops step 2)

- **The pass ceiling:** on every gross evaluation cell, the pass probability is at most `D / (D + T)` -- the evaluation's
  drawdown amount `D` over itself plus the base target `T`, both from the record -- beyond its Monte Carlo interval. A
  fair game stopped at `+T` or `-D` passes with exactly that chance when the floor is static; a trailing floor, a lock
  above the start, a consistency target, a minimum-days rule or a daily limit only remove or delay passes (propsim
  D-02's 2/5 is the case of Topstep's terms).
- **The evaluation martingale:** on every gross evaluation cell the mean balance at resolution is zero within its Monte
  Carlo interval (the coin's barrier race is exact at every room).
- **The funded martingale:** on every gross funded cell the mean of the balance plus gross payouts plus forfeitures at
  the horizon is zero within its interval; and the mean gross payouts are at most the account's starting distance to
  its floor, from the record, beyond the interval (the stage-one bound behind its $2,000, for each plan's own terms).
- **The costed coin:** the same means equal minus the mean costs paid, within the interval.
- **Stage one's reference:** at `TS-S`, `steady (1.0, $1,500)` reproduces the best static profile's exact pass
  probability (`vendor/stage2/vendor/propsim/README.md`; `edge/combine_exact.py`) within its interval, and no `TS-S`
  evaluation cell exceeds the supremum over fair strategies of `optimality/results_combine_supremum.csv`.
- **The bounds:** every request within its plan's bounds and every net its split of it, to 1e-9; no trade larger than
  its room, its daily limit or (on the costed coin) its allowance; every costed trade's fee its schedule at its
  contracts.
- **The join:** 9.5's per-attempt net equals `propsim.attempt_ev` on the same summaries, to 1e-9, at `TS-S`.

## 10. Part D: flip days measured

### 10.1 The share of passes that come from one or two large days

For every evaluation pass -- on every coin cell (9.3) and on every registered replay (12.2) -- sort the pass's trading
days by profit, largest first, and count **`k*`, the fewest of them whose profit sums to the base target `T`**. A pass
with `k* = 1` came from one large day; `k* <= 2` from one or two. No threshold is chosen: `k*` is read off the days.
Printed: the distribution of `k*` (1, 2, 3, 4, 5 and more), the shares with `k* = 1` and `k* <= 2`, and the sessions to
a pass by `k*`. **For every first payout** the same count against the balance at the request (`k*_F`). On the coin a
day's profit is one trade's; on the registered trades it is the account's session P&L from the replay's records (A-13).

### 10.2 What a flip-seeking policy does, against a steady one

**On the coin:** every `flip (w, r)` against its `steady (w, r)`, paired on the same streams (section 15), per mode and
corner: the difference in pass probability, in sessions to a pass (mean, p50), in first-payout probability, in mean
net per attempt and per funded journey (9.5, joined with the same funded cell), with paired standard errors; and the
large-days shares under each. The joined tables of 9.5 show the four blocks (steady or flip in each mode).

**On the registered trades** (P-16, each plan's strict corner, and `TS`): `flip_E` (the evaluation mode's flip, the
funded mode as registered) and `flip_F` (the funded mode's flip, the evaluation as registered), each against its plan's
`steady` replay on every start: the journey scorecard's paired readings (12.2) and, from the replay's records, the pass
rate per evaluation bought, sessions to a pass, the first-payout rate per funded account, and the large-days shares.

### 10.3 What is counted beside every flip cell

The flip trades cut by the room or by the daily limit; the flip trades at the full allowance; the flip trades'
contracts against the median of the same account's other trades (the s.8 reading: a ratio printed, no threshold); the
evaluations bought per 21 sessions (Topstep's "Excessive purchases"); the sessions on which two or more of the user's
accounts end at their floors (RTP trigger "Multiple accounts hit the Maximum Loss Limit in one day"); flip trades on an
FOMC-minutes day at the full allowance (E-050's calendar). **Every flip cell carries its 4.7 label** in every output; an
N label moves it to the outputs' own section "prohibited by name: reported, never carried".

## 11. Part E: which constraint binds, per plan and mode

1. **The size that binds** (part B): per configuration, mode, state, mix, `s` and `r`, the constraint that gives the
   fewest contracts. Arithmetic.
2. **The last gate to open** (parts C and F): for every pass, the pass condition that held last -- the base target, the
   consistency-raised target, the minimum days -- and for every evaluation that did not pass, its cause (the floor; the
   lifespan; inactivity; unresolved); for every first payout, the payout gate that held last (winning days; the cycle's
   share; the cycle's days; the buffer and minimum; the clock; the profit since the last request), and for every funded
   account with no payout, its cause. The session each gate first held is recorded (A-13), so "last" is read off the
   records, never inferred.
3. **The reading:** per configuration and mode, the share of each last gate and each cause, on every coin cell and on
   every registered replay. A mode's binding constraint is reported as these shares, all of them; none is singled out.

## 12. Part F: the registered trades on each plan (RD-01's form, extended)

### 12.1 The cells

| cell | configurations | stream | runs |
|---|---|---|---|
| references | `TS` (`TS-S/std`) | P-16, P-14 | 2 (identities) |
| steady corners | `LU50` (2 corners), `L6/std` (2), `L10/day` (2), `L10/5wd` (1), `L11/day` (2), `L11/5wd` (1), `RE` (2), `RED` (2), `RI` (2), `PRO` (2), `PRO1` (2), `B20` (2), `B15` (2) -- 24 | P-16, P-14 | 48 |
| flips | `flip_E`, `flip_F` on `TS` and the 13 configurations above, each at its strict corner | P-16 | 28 |

**Not run here, and cited:** `TS-N` on P-14 and P-16 is RD-03's `naf` cell; `LU40` is RD-01's `LU` corners; `TS-S/con`
and `L6/con` are not run on the registered trades, whose tables solve the Standard path (G-1; the coin reads them, 9).
Their rows are read from those readings' result files when on master, beside, labelled with their reading's id; until
then the menu prints "not yet run by RD-01 / RD-03". **Each run is both arms, every start, the long replay and U1's
exact-length runs, at 0 % denial with the placement off.**

### 12.2 What is read (RD-01 section 10, carried)

Every run and both arms (the verdict arm the headline), every block of section 6: the journey scorecard (P, S1 to S5c,
S2, S3d, S6, Q); **the guard row with every P** (E-134 (2): the mean net at months 1 to 3, the month-6 and month-12 net
with p10, p50, p90, CVaR10 at months 3, 6 and 12, the gate at the bound with its ruin probability); E-014's journey
variables; each measure as a distribution over starts; **the paired readings against `TS` by month** (who is helped,
who is hurt: the per-start difference, the shares better, equal and worse, the mean difference with 12.5's interval,
its window count and minimum detectable difference); for a flip cell, the same against its plan's steady cell; what
diverges (accounts, evaluations bought, fees by kind, payouts, trades taken and their realised risk); parts D's and E's
readings on the replay's records (10.1, 10.2, 11.2). **Beside each configuration's rows: its zero-edge map, whole** (9),
and its sizing grid's rows at the design's own stops; **no cell of the map is matched to the design** (a matched cell
would be chosen after a look at the design's sizes); the design's own coin twin is its gate's zero-edge twin (12.3).

### 12.3 Beside

- **The denial ladder** (10, 25 and 50 %), verdict arm, U1's exact-length runs on every 21st start index
  (`EXACT_EVERY`): on P-16's 13 strict (or single) corners (39 replays), and on `TS-16` as three checks against Q-44's per-start
  rows (`results/user_beside_starts.csv`, start for start, every column, as text; E-098 (R4)). The draws are Q-17's
  (`lockstep.child_seed(20261920, 0, start_day)` as `run_starts` draws them), common to every cell.
- **The placement on** (`rtp`, the gate's strictest reading) on `TS`'s two flip cells (2 replays) and `TS-16` as one
  check against Q-44; not run at Labs (the program's application to Labs accounts is unread: the gap named on their
  rows) nor at other firms (their programs are not Topstep's).
- **The gates**, one per P-16 strict (or single) corner (13), 500 paths, point and bound, with the zero-edge twin, at P-16's
  registered gate seed, through `extended/gate.py` with A-14's gate arguments (RD-01's A-8 seams); calendar rules in
  sessions by A-3's translation, labelled. The references' gates are 13.1's identities. **Nothing is a floor: nothing
  is carried.**
- **The Focused Trader models are not run** (G-5), the gap named on every Topstep row.

### 12.4 The mechanics, printed first (RD-01 9.3's form)

Per configuration, stream and block, before any paired outcome: the share of starts on which it differs from `TS` at
all within 63, 126 and 252 sessions; the share of trades whose contracts differ from `TS`'s, by account kind, and the
share in each of part B's size-binding constraints; the realised-to-intended risk (E-022 (1)'s form); the trades stood
aside (D-272); **where each plan binds**: daily-limit days and signals lost to a paused account; passes delayed by
minimum days and the day-logging micro's sessions (4.6); passes waiting at a funded cap below five (U-14) and their
waits; buffer-blocked closes; Pro's clock waits; Builder's share-blocked closes and count endings; ceiling endings;
lifespan expiries; inactivity closures; purchase-limit exhaustion (A-4) and the sessions after it with no evaluation;
**the conduct counts of 10.3** on every cell; trades open or resting at 12:58 CT on FOMC-minutes days at My Funded
Futures' funded accounts (G-2); **the checks that must be zero**: purchases refused for cash; trades exiting after
15:10 CT; trades on a session closing before 15:20 CT by E-029's calendar (`config/calendar_early_closes.csv`, LF
sha256 `72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2`); resets and reactivations bought. E-050's
calendar is `config/calendar_fomc_minutes.csv`, LF sha256
`0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7`. A configuration identical to `TS` on every start is
reported "no effect on these trades", and nothing more is read for it.

### 12.5 The uncertainty on each paired reading (fixed now)

Descriptions, not tests: nothing is compared with a critical value to decide anything. **RD-02's section 9.2, items 1
to 7, unchanged** (`prereg/RD-02_payout_policy.md`, built in `extended/pp_reading.py`, imported), with this reading's
own honesty seed (section 15): every other window of h starts kept so no two share a session; the two-sided 90 %
Student t interval on the kept windows' means when at least four; the window sign count; Bartlett's effective sample
size; the minimum detectable difference printed before the mean; the honesty series' labels. **On the coin**, every
proportion carries its binomial standard error and every mean its CLT standard error; a paired difference its paired
standard error on the common streams. **How many intervals, and what chance alone gives:** the menu prints the number of
90 % intervals it shows and that a tenth would exclude zero by chance alone were there no effect anywhere -- a count,
not a level.

### 12.6 The menu

Per configuration: its zero-edge maps (both modes, joined), its sizing grid, its flip-day rows, its binding shares, its
registered rows with the guard row, the readings beside. **The flags, mechanical, never lines:** "not stable across
blocks" (a mean paired difference in P or in a guarded measure of opposite signs on the early and late blocks);
"corners straddle the reference" (a configuration's two corners on opposite sides of `TS` on P or a guarded measure);
"first-order, the table fixed" on every part-F row (G-1); every 4.7 label; "prohibited by name: reported, never carried"
in its own section; "upper bound in fees" (U-3); "from the general article" (U-13). **E-015's limits** flag the menu only
if approved before the run's commit by a row of the `e015-limits:` form (E-104); with none approved, the menu says so.

## 13. Before any reading: identities, oracles, refusals

### 13.1 The identities, refusing (E-004, E-010; whole-window identities only from `identity/*.py`, E-026, E-041)

**Shared, owed by other items; this reading waits for each, re-held after Q-136's and Q-115's merges (4.1).** A wait
is met only by a decision row whose third cell begins with `identity-holds: <id>` (E-104's positional form,
`extended/identity_tokens.py`), at the run's commit or an ancestor, with the identity's cover unchanged since
(`extended/identity_cover.py`'s `cover(id)`): Q-05 (E-010); Q-80 (E-049); Q-93 with Q-100 (E-059 (1)); Q-101 (E-068);
and **RD-01's own, `firms_identity`** (`identity/firms_identity.py`), since part F runs through RD-01's runner.

**This reading's own, each from a clean checkout of the reading's commit, under the purpose `identity` and the row that
registers it, before any step that uses it:**

1. **`modes_coin_identity`** (`identity/modes_coin_identity.py`), before step 2: (a) A-0 with every addition off
   reproduces `propsim.simulate_combine` and `simulate_xfa`, every output array, bit for bit, at every `(w, r)` of the
   grid, 2,000 accounts each, on the identity's seed (section 15); (b) A-0 at `TS-S`'s terms reproduces stage one's
   reference profile (9.6) at the inherited seed of the skill's quick reference (`run_combine(Policy(rr=1.0,
   risk=1500.0), 0.0, 200_000, seed=2026)`), within its interval; (c) every adapter's coin form equals its account
   class (4.3) on 1,000 scripted streams per mode-corner drawn on the identity's seed, account for account, every
   gate, ending and payout.
2. **`modes_identity`** (`identity/modes_identity.py`), before step 3: through this reading's composition (A-14) at
   `TS` and every adapter at its Topstep setting: U1's start rows for P-14 and P-16 (`vendor/stage2/results/
   user_journey.csv`, section `start`, configs `p14` and `p16`, both arms, every start, every column as E-010 compared
   them), and the registered gate paths (`a3_brk30_cb20_gate_paths.csv` at seed 20261131;
   `rc_s150_all_gate_paths.csv` at seed 20261206 after P-16's trades' hash), every `zero_edge_decomposition.PATH_COLS`
   column, point and bound, all 500 paths, to 1e-6; and `LU50`'s composition equal to the vendored joint engine's
   one-firm run of `lucid_setup` at `ADDON_50`, start for start, both arms (RD-01 9.1 item 3 (b)'s form; P-16).

**The covers** (Q-111's rule, E-119): each is `BASE` (`extended/__init__.py`, the folder `config/` whole, both vendored
manifests) plus its script and its import closure (`identity_cover.imports(script)`); T-0 holds each equal to that.

**Inside the run (no further read), refusing:** `TS`'s rows equal U1's again; every trade any account takes is one of
its design's registered offered trades (Q-94's recorder); in `TS` no adapter switch fires and in each configuration no
other plan's rule fires; **a flip cell equals its steady cell on every account until that account's first flip trade**;
each two-ended term's corners equal each other where the term cannot bind. **Any failure stops the reading: nothing of
a new cell is computed, written or printed**; the failure protocol applies; nothing is rerun until it passes, and a
rerun is a further judged read under `repeat=` (E-053). E-010's negative controls show the comparisons are not vacuous.

### 13.2 The refusals before step 0 reads anything

The loader refuses, before any table is written: a role of Appendix R for a configuration in scope that resolves to
neither a verified entry nor a rule of section 5; a record entry not `verified` loaded as a value; a literal rule value
in the adapters (17.2); a joining plan (2.4) that fails any of its conditions -- which leaves the plan out and says so,
never the reading.

## 14. What the reading delivers, and what each outcome means

- **It delivers** the tables of parts A to E for every configuration and mode, the registered rows of part F with
  their readings beside, and the menu.
- **It does not deliver** a carried design, a registration id, a confirmation, a claim at a level, a bar for any family,
  or a recommendation to buy anything (E-023 (1)).
- **No outcome passes or fails.** What follows, fixed now: an identity fails -- its step and every later step stop; a
  stated-fewest check fails -- step 0 stops (7); an oracle is breached -- an engine error, its step stops; a cell
  identical to its reference -- "no effect on these trades"; corners straddling the reference -- flagged, settled only
  by the record (a browser read or a written answer, section 19), **never by a repeated run**; a flip cell labelled N
  shows a higher P or net -- reported in its own section, never carried, never offered.
- **The operator's choice** is recorded in its own row, citing this reading's files; it is an in-sample choice with no
  confirmation. Any purchase it implies is the operator's.
- **The binding.** The blocks read here are recorded as read for firm-mode readings on P-14 and P-16. A later reading of
  any of these plans, modes or policies names this one, states what changed, and reads no block of it as fresh.

## 15. Seeds, fixed now and checked

| seed | status | role | what it draws |
|---|---|---|---|
| 20262380 | in use | `coin_eval` | part C's evaluation coin streams: account `i` of mode-corner `m`'s cell `(w, r)` draws from `numpy.random.default_rng([20262380, m, w_index, r_index])`; `flip` and every costed cell of the same `(w, r)` reuse the stream (common random numbers) |
| 20262381 | in use | `coin_funded` | part C's funded coin streams, keyed the same way; independent of `coin_eval`, so 9.5's joins are exact |
| 20262382 | in use | `coin_peak` | `RI`'s losing-trade peaks (9.2), keyed `[20262382, m, w_index, r_index]`, so `RI`'s outcome stream is `RE`'s |
| 20262383 | in use | `build_toys` | the build's toy campaigns and scripted streams (T-1 to T-12) |
| 20262384 | in use | `coin_identity` | `modes_coin_identity`'s items (a) and (c) (13.1) |
| 20262385 | in use | `honesty` | 12.5's honesty series (keys `[20262385, 1, shape, h, n_w]`; the build's test `[20262385, 0, ...]`) |
| 20262386 | reserved, unused | -- | -- |
| 20262387 | reserved, unused | -- | -- |
| 20262388 | reserved, unused | -- | -- |
| 20262389 | reserved, unused | -- | -- |

**Part F's replays at 0 % draw nothing.** The mode-corner index `m`, `w_index` and `r_index` are the positions in
Appendix M's list and 2.6's grid, fixed by this text.

**The check, 2026-11-18 (UTC), on this text.** Two word-bounded searches for the block's pattern (the seven-digit prefix
followed by one digit), every text file, the licensed data excluded:

- `git grep -IwoE` on every local and remote ref of the repository (23 refs), the vendored snapshot and its results
  included;
- `grep -rIownE --exclude-dir=.git --exclude-dir=data` on the working files of the main tree, of every worktree under
  `%LOCALAPPDATA%\stage2-extended-wt\`, of every clean-run checkout under `%LOCALAPPDATA%\stage2-extended-runs\` and of
  its logs, before this file was written.

They found the block nowhere. After this text is committed they find it in this file alone; T-0
(`tests/test_rd05_draft.py`) builds the block by arithmetic, so it holds no literal of it, and repeats the search on
the repository's tracked files on every run.

**Inherited, used only as their owners registered them:** P-14's gate seed 20261131 and P-16's 20261206 (the identity
and the gates beside); Q-17's ladder start seeds (`lockstep.child_seed(20261920, 0, start_day)`, E-024); U1's replay
seeds as U1 passes them; stage one's quick-reference seed 2026 for 9.6's reference check only.

## 16. Counting (no family number, no level; every cell counted)

1. **No program family number and no level** (E-023 (1)). The next numbered family's k is what it would be without this
   file.
2. **Step 0** writes tables, draws nothing and runs no engine.
3. **The mode-corners** (Appendix M): 17 evaluation and 25 funded, **42**.
4. **The cells and runs:**

<!-- counted-cells: the rows below are summed by T-0 -->

| block | runs | basis |
|---|---|---|
| part C, gross coin | 2016 | 42 mode-corners x 24 `(w, r)` x 2 policies, less `RI`'s funded cells not read (fewer, printed at step 0) |
| part C, costed coin | 3024 | 42 x 24 x 3 stops, at most: only the cells part B finds sizeable run (the count printed at step 0) |
| part F, references | 2 | `TS` on P-16 and P-14 (identities) |
| part F, steady corners | 48 | 24 corners x 2 streams |
| part F, flips | 28 | 14 configurations x 2 flips, P-16 |
| beside, denial ladder | 39 | 13 strict (or single) corners x 3 levels, P-16 |
| beside, placement | 2 | `TS`'s two flips |
| beside, gates | 13 | P-16 strict (or single) corners, 500 paths, point and bound, with the zero-edge twin |
| reference checks against Q-44 | 4 | `TS-16` under the three ladder levels and the placement |

<!-- end counted-cells -->

   That is **at most 5,040 coin runs**, **78 replays** at 0 % on both arms (2 references, 76 new), **41 replays beside**
   with 4 reference checks, and **13 gates**. A joining plan (2.4) adds, per configuration: `24 x 5` coin runs per
   mode-corner; 2 steady replays per corner; 2 flips; 3 ladder replays; 1 gate -- stated in the join's row before step 0.
5. **Exact arithmetic, not runs:** `TS-N`'s re-pricing; every price end; 9.5's joins; part B.
6. **Every block read** is recorded as read for firm-mode readings (14). **Nothing is selected by the program.**

## 17. The build: adapters, rules in code, tests

### 17.1 The adapters

Section 4.3's A-0 to A-15, in `extended/`, never in `vendor/`.

### 17.2 The rules in code

Every value of every role is read by a loader that refuses an entry not `verified` (Stage 2's ledger through its own
loader; the vendored Lucid ledger through Stage 2's adapter; `config/rules_extended.yaml` through RD-01's
`extended/firm_terms.py`), parsing a value stated in text fail-loud. A test fails on any literal of a rule value in the
adapters outside comments. The readings of section 5 come from one table of named constants, each citing its line of
5.1. Grid values (2.6), horizons and account counts come from one table of named constants citing this file's sections.

### 17.3 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 | `tests/test_rd05_draft.py` (committed with this draft; extended at the pin): exactly one firm-modes declaration under `prereg/`; LF only; the seed block once each in section 15's table and in no other tracked file; one `Judged-block reads:` line, its three purposes as declared, none choosing by the reader's own test, none `identity` or `registered_design`; the counted-cells table's rows sum to its stated totals; the sections present. **At the pin, added:** every Appendix R role resolved to a recorded key with the status stated; section 5.2's corners recomputed from the record; the covers of 13.1 |
| T-1 | A-0 with every addition off equals `propsim.simulate_combine` and `simulate_xfa` bit for bit on toy streams (seed `build_toys`); its guard refuses a changed vendored source; its recomposition proof |
| T-2 | every account class of 4.3 with its switches at Topstep's setting equals the vendored class on toy campaigns, every reduction and recorder row (RD-01's T-1 form) |
| T-3 | every adapter's coin form equals its account class on scripted streams, account for account: daily limits soft and hard, static floors and their move at a payout, minimum days, lifespans, buffers, cadences, clocks, cycle shares, counts, ceilings, the contract-counted cap, the Daily path at both U-22 ends |
| T-4 | 4.6's table inputs at each new plan on toy campaigns; the held reading; the day-logging micro |
| T-5 | part A's arithmetic on hand-built rule sets with known answers, under both consistency semantics; the stated-fewest check firing on a hand-broken record |
| T-6 | part B's arithmetic on hand-computed cells: contracts, the binding constraint, D-212's test, the cost share, the allowed set; the three mixes; the contract-counted cap |
| T-7 | `flip`'s schedule on the coin and on toy replays: `k` and `r_flip` from part A; one flip trade a session; the cuts; a flip cell equal to its steady cell until the first flip trade; `k = 0` equal to `steady` |
| T-8 | the costed coin's mean equals minus its mean costs on a toy grid; `RI`'s peak law against a fine random-walk simulation of the bracket (seed `build_toys`), within its interval; the read set `(w + 1) r` at most the drawdown |
| T-9 | 9.6's oracles each fire on a hand-broken engine; 9.5's joins equal `propsim.attempt_ev` to 1e-9 |
| T-10 | 10.1's `k*` on hand-built pass records; 11's last gate on hand-built gate records |
| T-11 (`slow`) | 13.1's identities at 4 starts and 4 paths, and the coin identity at 200 accounts a cell |
| T-12 | the menu: no P without its guard row; every 4.7 label mechanical; N-labelled cells only in their own section; the flags of 12.6 on synthetic menus |
| T-13 | the seeds of section 15 appear in the build's commit only where section 15 declares them; 17.2's literal check |

## 18. Outputs and the run

**Files**, each written with its sidecar manifest through `extended.results.write_result` (`prereg_id` `RD-05` and its
pinning row; the identity rows with their shas and the run's head; the cell and run counts as run; every seed, the
inherited ones named; every parameter and every reading of section 5 with its label; the record entries with their
dates read and the commits Q-136 and Q-115 merged at; the sha256 of `vendor/DATA_MANIFEST_stage2.sha256` and the two
calendars' LF sha256 where part F reads them; the E-015 limits or "none approved before the run's commit";
`exploratory=False`, every row labelled "described, not carried"):

- `results/modes_rules.csv` -- step 0: `terms`, `flip_days`, `stated_check`, `flip_sizes`, `sizing`, `allowed`,
  `size_binding`;
- `results/modes_coin.csv` -- step 2: `identity`, `oracle`, `eval`, `funded`, `fees`, `joined`, `flip_pairs`,
  `large_days`, `binding`;
- `results/modes_reading.csv` -- step 3: `identity`, `mechanics`, `scorecard`, `guard`, `paired`, `flip`,
  `large_days`, `binding`, `coverage`;
- `results/modes_beside.csv` -- step 4: `ladder`, `rtp`, `checks`;
- `results/modes_gate.csv` -- step 5;
- `results/modes_menu.csv` -- the menu with its flags, labels and its "prohibited by name" section.

**The run, in six steps, each from a clean checkout of a named commit (`scripts/run_clean.py`), one heavy job on the
machine under `run.lock` (skill `run-lock`), watched to its exit; each step only after the lead's row records the one
before:**

0. **The rules arithmetic** (`scripts/modes_rules.py`; light; no seed, no bar): 13.2's refusals first; then parts A,
   B and E (1); the stated-fewest check refusing (7). It writes `results/modes_rules.csv`, which fixes the costed cells
   and `RI`'s read set before step 2.
1. **The identities**: `identity/modes_coin_identity.py` and `identity/modes_identity.py`, under the purpose `identity`
   and their own row. A failure of `modes_coin_identity` stops step 2; a failure of `modes_identity` stops steps 3 to 5.
2. **The coin maps** (`scripts/modes_coin.py`; heavy by compute, no bar): `TS-S`'s evaluation mode first with 9.6's
   reference check; then the evaluation mode-corners and the funded mode-corners in Appendix M's order; each cell's
   oracles checked before anything of it is written; 9.5's joins, then parts D's and E's coin readings.
3. **The registered scorecard** (`scripts/modes_reading.py`, purpose `modes_scorecard`): (a) `TS` on P-16 then P-14, at
   `off`, both arms, the recorder on (13.1's repeat); (b) the steady corners in 12.1's order, P-16 then P-14, strict
   before lenient; (c) the flips, `flip_E` before `flip_F`, in the same order; each new cell checked under 13.1's run
   checks before anything of it is read; (d) the mechanics, then the readings and the menu without its beside sections.
4. **Beside** (purpose `modes_ladder_beside`): `TS-16`'s four checks against Q-44 first, then the 39 ladder replays and
   the 2 placement replays, in step 3's order.
5. **The gates** (purpose `modes_gate_beside`), in step 3's order; then the menu's beside sections.

**On any failure, nothing more of the failed step's own run is computed, written or printed**; that step's run stops at
the failed check and its log and the check's own lines are all it leaves; the failure protocol applies.

- **Weight: heavy** (steps 2 to 5). Step 2's runs are vectorised over 50,000 accounts; step 3's replays and step 5's
  gates are RD-01's machinery. Measured on synthetic data of the window's length before step 2 and step 3 (E-117's
  form) and stated in the lead's rows with memory; E-010's U1 identity for two configurations peaked near 1.4 GB, so
  two workers at most. If step 2's measured time exceeds twelve hours, the build stops and reports: **no grid is thinned
  after a measurement**; a smaller grid is a new declaration.
- **Waits, all before step 0:** Q-136 merged and Q-115 merged, then every shared identity and RD-01's `firms_identity`
  held at a commit containing both (4.1); the pinning row; any join row (2.4); A-0 to A-15 built with T-0 to T-13 and
  the red team's read of the build; **before step 4,** Q-44's file on master.

## 19. Open before the pin

**The lead's:**

1. **Q-136's record**, and T-0's mapping of every Appendix R role to its key: a role with no key, or a status other than
   section 5.2's, is a text change before the pin (the corners and counts follow).
2. **The red team's read and the gatekeeper's**, of this text.
3. **The two conduct labels of 4.7** -- flip-seeking at Topstep as N against Stage 2 D-145's tier-3 pricing of account
   stacking; Pro's policy reaching the registered tables' own funded sizes. They are the operator's tiers by E-007 item
   4's pattern; this text holds the stricter label until a row rules.
4. **Whether `TS-S/con` and `L6/con` should be read on the registered trades** (they are not, G-1), and whether Labs
   should carry the placement beside (12.3).
5. **The name at the pin:** `prereg/RD-05_firm_modes.md`, the draft renamed in the same commit, nothing else changing.

**The operator's (reads, no purchase):**

1. Settling a conflict or an unstated reach of section 5.2 by a browser read or a written question (Labs #006's
   scaling thresholds and purchase limit; the Daily path's amount; My Funded Futures' consistency base, Pro's floor
   and buffer, Builder's first cycle, the ceiling's reach); until a term is recorded, both ends run.
2. **The by-hand captures of Lucid's and Alpha Futures' terms** (`docs/OPERATOR_SETUP.md` item 11), which join only by
   section 2.4.
3. The levels of E-015's limits (flags only); after the run, any choice from the menu.

## 20. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*

---

## Appendix M -- the mode-corners, in run order (part C)

| index | mode | corner | two-ended terms at it |
|---|---|---|---|
| 0 | `TS` evaluation | single | -- |
| 1 | `L6` evaluation | single | -- |
| 2 | `L10` evaluation | single | -- |
| 3 | `L11` evaluation | single | -- |
| 4 | `RE` evaluation | strict | U-15 net |
| 5 | `RE` evaluation | lenient | U-15 sum of winning days |
| 6 | `RED` evaluation | strict | U-15 |
| 7 | `RED` evaluation | lenient | U-15 |
| 8 | `RI` evaluation | strict | U-15 |
| 9 | `RI` evaluation | lenient | U-15 |
| 10 | `PRO` evaluation | strict | U-15 |
| 11 | `PRO` evaluation | lenient | U-15 |
| 12 | `PRO1` evaluation | single | -- |
| 13 | `B20` evaluation | single | -- |
| 14 | `B15` evaluation | single | -- |
| 15 | `LU40` evaluation | single | -- |
| 16 | `LU50` evaluation | single | -- |
| 17 | `TS/std` funded | single | -- |
| 18 | `TS/con` funded | single | -- |
| 19 | `L6/std` funded | strict | U-20 entry tier |
| 20 | `L6/std` funded | lenient | U-20 standard thresholds |
| 21 | `L6/con` funded | strict | U-20 |
| 22 | `L6/con` funded | lenient | U-20 |
| 23 | `L10/day` funded | strict | U-22 |
| 24 | `L10/day` funded | lenient | U-22 |
| 25 | `L10/5wd` funded | single | -- |
| 26 | `L11/day` funded | strict | U-22 |
| 27 | `L11/day` funded | lenient | U-22 |
| 28 | `L11/5wd` funded | single | -- |
| 29 | `RE` funded | strict | U-19 |
| 30 | `RE` funded | lenient | U-19 |
| 31 | `RED` funded | strict | U-19 |
| 32 | `RED` funded | lenient | U-19 |
| 33 | `RI` funded | strict | U-19 |
| 34 | `RI` funded | lenient | U-19 |
| 35 | `PRO` funded | strict | U-16, U-17 |
| 36 | `PRO` funded | lenient | U-16, U-17 |
| 37 | `B20` funded | strict | U-18 |
| 38 | `B20` funded | lenient | U-18 |
| 39 | `B15` funded | strict | U-18 |
| 40 | `B15` funded | lenient | U-18 |
| 41 | `LU` funded | single | -- |

The commission basis of My Funded Futures (U-12) adds no corner of its own: the costed coin and part F read it at each
corner's own end -- fees on top at a strict or single corner, as all-in at a lenient corner.

## Appendix R -- the term roles each configuration leans on, with their key forms and expected status

Sources: `stage2` is Stage 2's vendored `vendor/stage2/config/rules.yaml`; `lucid` the vendored Lucid ledger through
Stage 2's adapter; `record` this repository's `config/rules_extended.yaml` -- **Q-136's keys are named here by their
expected form** (`topstep.labs006_50k.<role>`, `topstep.labs010_50k.<role>`, `topstep.labs011_50k.<role>`,
`mffu.<plan>.<role>` with plans `rapideod50k`, `rapideod50k_dll`, `rapid50k`, `pro50k`, `pro50k_1day`, `builder50k`,
`builder50k_15`, and firm-wide `mffu.<role>`); T-0 maps each to the key Q-136 records at the pin. A role marked
"general" at Labs is read from Topstep's general article by U-13.

| role | `TS` | `TS-N` | Labs (`L6`, `L10`, `L11`) | My Funded Futures (`RE` ... `B15`) | Lucid (`LU40`, `LU50`) | status expected |
|---|---|---|---|---|---|---|
| evaluation target | `combine_profit_target` (stage2) | as `TS` | `<labs>.eval_profit_target` | `mffu.<plan>.eval_profit_target` | `eval_profit_target` (lucid) | verified |
| evaluation drawdown amount, type, lock | `combine_mll`, `combine_mll_lock_at` (stage2) | as `TS` | `<labs>.eval_drawdown_amount`, `_type`, `_lock` | `mffu.<plan>.eval_drawdown_amount`, `_type`; `mffu.eval_drawdown_lock` | `eval_drawdown_amount`, `eval_drawdown_type`, `eval_drawdown_lock` | verified |
| evaluation daily loss limit | none (no election) | as `TS` | `<labs>.eval_daily_loss_limit`; softness general | `mffu.<plan>.eval_daily_loss_limit` | `eval_daily_loss_limit` (off) | verified; Labs softness by U-13 |
| evaluation consistency, its semantics and base | `combine_consistency_max_day_frac` (stage2) | as `TS` | `<labs>.eval_consistency_rule`; semantics general | `mffu.<plan>.eval_consistency_rule`; base unstated | `eval_consistency_rule` | verified; base by U-15 |
| evaluation minimum days | `combine_min_trading_days` (stage2: none stated) | as `TS` | `<labs>.eval_min_days` (absent) | `mffu.<plan>.eval_min_days` | `eval_min_days` | verified or absent |
| evaluation position cap, counting | `combine_position_size_limit` (stage2) | as `TS` | `<labs>.eval_position_limit` | `mffu.<plan>.eval_position_limit`; `mffu.contract_counting` | `eval_position_limit` | verified |
| evaluation lifespan, inactivity | none | as `TS` | `<labs>.eval_time_limit`, `<labs>.inactivity_rule` | `mffu.inactivity_rule` | `eval_time_limit` | verified |
| evaluation price, billing, resets | `subscription_fee`, `billing_days`, `billing_period_calendar_days` (stage2) | `subscription_fee_naf_50k` (record, Q-115) | `<labs>.eval_fee`, `<labs>.eval_reset_fee` | `mffu.<plan>.eval_fee` (list and promotion), `mffu.<plan>.eval_reset_fee` | `eval_fee`, `eval_reset_fee` | verified; prices by U-1 |
| purchase limit | `combine_count_limit` (stage2) | as `TS` | `<labs>.purchase_limit` | `mffu.max_eval_accounts` | `eval_count_limit` | `L6` conflicting (U-24) |
| activation, the switch | `activation_fee`, `xfa_activation_latency` (stage2) | `activation_fee_naf_50k` (record) | `<labs>.activation_fee` | `mffu.activation_fee`; `mffu.eval_to_funded_timing` | -- (adapter) | verified |
| funded floor start, type, lock | `xfa_mll_start`, `xfa_lock_at` (stage2) | as `TS` | `<labs>.funded_drawdown_amount`, `_type`, `_lock` (lock general at `L10`) | `mffu.<plan>.funded_drawdown_amount`, `_type`, `_lock` | `funded_drawdown_amount`, `funded_drawdown_type` | verified; `PRO` by U-16 |
| floor at a payout | the engine's move to `xfa_lock_at` at any payout (stage2) | as `TS` | `<labs>.payout_balance_consequence` | `mffu.<plan>.payout_balance_consequence` | `payout_balance_consequence` | verified |
| funded daily loss limit | none | as `TS` | `<labs>.funded_daily_loss_limit` | `mffu.<plan>.funded_daily_loss_limit` | `funded_daily_loss_limit` (off) | verified |
| funded consistency | `xfa_payout_path_choice`, the Consistency path's fields (stage2) | as `TS` | `<labs>.funded_consistency_rule`, `<labs>.payout_path_choice` | `mffu.<plan>.funded_consistency_rule` | `funded_consistency_rule` | verified; `B` base by U-18 |
| payout gate | `xfa_std_winning_days`, `xfa_std_winning_day_min`, `require_profit_since_payout` (stage2) | as `TS` | `<labs>.payout_frequency_gate` (#006 general); `<labs>.daily_payout_buffer` | `mffu.<plan>.payout_frequency_gate`, `mffu.<plan>.payout_buffer` | `payout_frequency_gate` | verified; `PRO` buffer by U-17 |
| request cap, share, minimum, split | `xfa_std_cap`, `payout_max_frac_of_balance`, `payout_min`, `profit_split` (stage2) | as `TS` | `<labs>.payout_cap`, `<labs>.daily_payout_min`, `_max`, `<labs>.payout_split` | `mffu.<plan>.payout_cap`, `payout_min`, `payout_split` | `payout_cap`, `payout_min`, `payout_split` | verified; Daily path by U-22 |
| an end by count or ceiling | none | as `TS` | none | `mffu.<plan>.payout_count_limit`, `mffu.<plan>.funded_sim_profit_ceiling`, `mffu.pro50k.lifetime_payout_cap` | `max_accounts` (the fifth payout's move) | verified; reach by U-19 |
| funded allowance and scaling | `funded_scaling_plan`, `scaling_tier_after_payout` (stage2) | as `TS` | `<labs>.funded_position_limit` (thresholds at `L6` unstated) | `mffu.<plan>.funded_position_limit` | `funded_position_limit` | `L6` by U-20 |
| seats | `max_active_funded_accounts` (stage2) | as `TS` | `<labs>.max_funded_accounts` ("standard limits") | `mffu.<plan>.max_funded_accounts` | `max_accounts` | verified; U-14 |
| fees after funding, payout fee, lag | `payout_fee`, `payout_lag_days_aeropay` (stage2) | as `TS` | general | `mffu.payout_fee`, `mffu.payout_processing_days` | `funded_monthly_fee`, `payout_fee`, `payout_processing_days` | U-3, U-5 |
| request timing | the engine's `REQUEST_AFTER_5PM` (stage2 8284233) | as `TS` | `<labs>.daily_payout_cutoff`; general | `mffu.<plan>.payout_frequency_gate` | `LUCID_PAYOUT_TIMING` (adapter) | verified |
| commissions | `fills.yaml` (8284213) | as `TS` | general (U-23) | `mffu.commissions` | `fills.yaml` (D-575) | U-12 at My Funded Futures |
| conduct clauses | `prohibited_trading_strategies`, `prohibited_conduct`, `responsible_trading_program` (stage2); `tou_s8_relative_position_size` (record) | as `TS` | as `TS` | `mffu.pro50k.consistent_trading_policy`, `mffu.prohibited_conduct`, `mffu.terms_s23` | `prohibited_conduct` (lucid) | verified before a label prints (4.7) |
| news | `tier1_news_events_restriction` (record) | as `TS` | the record's Labs row | `mffu.news_policy` | `news_trading_terms` (lucid) | counted (G-2) |

---

## Appendix C -- the drafter's choices, each with its reason

| # | choice | where | reason |
|---|---|---|---|
| 1 | the reading is described, unnumbered, with no bar set for any family | header; 1 | E-023 (1) and E-134 (1): nothing here adds a trade; E-196 keeps the coin-twin pass line, so a bar is a later family's own declaration |
| 2 | the two modes read separately and joined by exact arithmetic | 2.6, 2.7, 9.5 | the funded account starts fresh at its own rules, so a pair's per-attempt value is stage one's `attempt_ev` on the two modes' summaries; running every pair would multiply the runs by the grid for nothing |
| 3 | the grid `w` in {1, 1.5, 2, 3} and `r` in {$250 ... $2,000} | 2.6 | Stage 2's reference ratios and D-272's Combine set, with one smaller risk; fixed, no value from data |
| 4 | one coin trade a session | 2.6 | stage one's reference; one position at a time (D-429); a multi-trade coin is a later reading |
| 5 | the flip-seeking policy sized from the rules: `k` the fewest days, `r_flip` the target over `k` wins | 2.6 | "large risk early" without a free parameter: the policy that would pass (or reach the first payout) in the fewest days the rules allow, cut by the room and the daily limit |
| 6 | one flip trade a session in the flip window, then steady | 2.6 | a flip day is one large winning day; a second trade at that size could overshoot the consistency share |
| 7 | D-212's stand-aside not applied to flip trades | 2.6 | the flip's point is its size; every such trade counted |
| 8 | the coin's request at the plan's own maximum; part F's at RD-01's rule | 9.2; 2.8 | the map values the contract at its own terms (stage one's form); part F stays comparable with RD-01's registered rows |
| 9 | the large-days count `k*` (fewest largest days covering the target) | 10.1 | answers "one or two large days" with no threshold chosen |
| 10 | the binding constraint as the last gate to open, all shares printed | 11 | read off recorded sessions, never inferred; no single constraint singled out |
| 11 | the costed coin at 50, 100 and 150 ticks only | 9.1 | the registered rungs; part B covers every width by arithmetic |
| 12 | `RI`'s coin trail exact only where `(w + 1) r` is at most the drawdown; the rest not read | 9.2 | the losing-trade peak has a closed law (the vendored MAE law mirrored); a winner's in-trade drawdown has none here, and no approximation is declared |
| 13 | 50,000 accounts a run, 504-session horizons | 9.1 | a pass probability's standard error well under a percentage point; the gate's funded horizon |
| 14 | `TS-N` and LucidFlex `STANDARD_40`'s registered rows cited from RD-03 and RD-01, not re-run | 12.1 | a later reading reads no block of an earlier one as fresh (RD-03 section 11); their coin maps are new and run here |
| 15 | `LU50` (`ADDON_50`) added to the registered trades | 12.1 | RD-01 dropped it; it is on Stage 2's verified record and in the brief's scope |
| 16 | the Consistency payout paths read on the coin only | 12.1; G-1 | the registered tables solve the Standard path; on the coin they are contract values |
| 17 | flips on P-16 only, at strict corners | 12.1 | P-16 is RD-01's headline stream; RD-01's one-at-a-time runs set the precedent |
| 18 | the placement beside at `TS` only; the Focused Trader models not run | 12.3; G-5 | the programs are Topstep-standard; their reach on Labs accounts is unread |
| 19 | Labs' unstated terms read from Topstep's general articles (U-13) | 5.1 | Labs accounts are Topstep accounts; the Labs page wins where it speaks |
| 20 | U-15 to U-24's ends | 5.1 | each strict end the one that helps the user least, named before any run |
| 21 | prices and lags never add a run | 5.1 | with the bankroll unbound and attempts independent, they move cash only: exact arithmetic (RD-01's A-10) |
| 22 | the conduct class rule N / D / P, flip-seeking at Topstep and Pro's funded sizing labelled N | 4.7 | the brief: a policy a firm's terms name as prohibited is reported and never carried; the clauses' words name the pattern; the stricter label held until the operator rules (19) |
| 23 | the join rule: whole firm or nothing, no new rule or adapter, frozen at step 0's commit | 2.4 | so nothing is chosen after seeing the captures |
| 24 | Q-136's keys named by role and expected form, mapped by T-0 at the pin | 4.1; Appendix R | the record does not exist at this text; the brief leaves values to it |
| 25 | step 2 stops and reports above twelve measured hours, never thinned | 18 | a grid thinned after a measurement is a choice after a look |
| 26 | the seed block 20262380 to 20262389 by role, with common streams for `flip`, costed and `RI` cells | 15 | paired differences are the policy's or the term's, not the stream's; the block found nowhere |
