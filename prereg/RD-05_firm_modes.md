# RD-05 (draft): the evaluation and the funded account as two trading modes on each $50K plan -- flip days, the zero-edge maps, the sizing grid, the binding constraint, and the registered trades beside (reading FM) -- a described reading, unnumbered (E-023 (1))

**Status: a third draft (TASK_QUEUE Q-137, corrective cycle 2 of 2, the last; E-196, E-197, E-199), not pinned.**
Drafted on `wt/wt-scout` with master merged at 2dd81fd. It goes to the red team's focused re-read and the
prereg-gatekeeper before any pin. At the pin the file is renamed `prereg/RD-05_firm_modes.md` and nothing else changes; the pinning row names the
commit and the sha256 of its LF text. Nothing declared is edited after the pin: a change is a new declaration under a
new row. It takes no program family number (E-023 (1)).

**Its text's history.** The first text (Q-137; wt/wt-scout f918897, LF sha256
`8951defd293e3c4e68f974885dd052f94119edf626381ca4be822a15efa2fee1`) was read by the red team (Q-137r,
`docs/reviews/DRAFT_RD-05_2026-11-18.md`: must be re-declared; three blockers, twelve should-fix items, ten notes).
**The second text answered every finding as the lead ruled them** (the conduct classes of the first text dropped and
D-145 carried; one new rule for an uncapped request; interval oracles under a family-wise correction; Q-136's record
read for the keys; the timing outside the seed block; a memory bound on every step). **The third text** answers the
red team's re-read of the second (Q-137r2, `docs/reviews/DRAFT_RD-05_v2_2026-11-18.md`, on 5244315, LF sha256
`cbed60d13c717ecb9fb1a976ac2969cc86b3d2730c037bf22047150ec4999237`: two blockers, six should-fix items, five notes) as
the lead ruled them -- the news rule decided at entry, with a forced flat at a window's start; the pass ceiling
dropped where the floor is checked only at the close; exact tests for the martingale oracles; one convention for
censored attempts; the stacking trigger defined -- and folds in Q-136b's My Funded Futures entries (the firm-wide
commissions and the verified single-day ceilings), which clear the second text's two pin blockers. Appendix A maps
every finding of both reads to the place it is answered.

**What E-023 (1) makes of it, as E-134 (1) rules it.** Every question here is about the contract, not about an edge:

- the **zero-edge maps** trade a coin -- a driftless bracket with no skill at all -- so there is no trade to lift;
- the **flip-seeking policy** and the **per-mode grids** change how large each trade is and when, on trades that are
  offered anyway. On the registered trades the flip **does change the executed set** -- in its window it takes a
  session's first trade only and takes trades D-212's stand-aside would refuse -- and with it that set's lift; it is a
  sizing and stop rule of the kind E-134 (1) lists as a described lever ("purchases, seats, reactivation, stop rules"),
  adding and removing no **offered** trade;
- the **registered trades on each plan** are RD-01's form: the contract changes the money, never the edge.

So this file is a **described reading**:

- it takes **no program family number** and spends **nothing** of the multiplicity budget (the next numbered family's
  k is unchanged by it);
- **no cell can carry, pass or fail**: there is no pass line, no level and no pick;
- every cell is read as a description, for the operator to choose from;
- it is declared and pinned before its run, by its own decision row with its sha256, so nothing in it is chosen after
  a look.

**The pass line is unchanged (E-008, E-196).** A design is judged on its trades: their lift over the coin twin on the
same brackets, on the judged block, at its family's level, by a calibrated statistic. This reading supplies, for each
plan and mode, what the contract is worth to a trader with no edge, and which sizes the plan's rules allow. **It sets no
bar.** A later family that uses one of these maps as its bar names the coin-map cell it uses -- never a part-F row --
in its own declaration, before it reads any trade of its own (the red team's N4).

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
| plans | 14 configurations of three firms' $50K plans (section 2.1); Lucid's other plans and Alpha Futures' plans join only by section 2.4 |
| parts | A flip days from the rules (7); B the sizing grid (8); C the zero-edge maps (9); D the flip measurements (10); E the binding constraint (11); F the registered trades (12) |
| rules | Stage 2's verified ledger; the vendored Lucid ledger; this repository's record at Q-136's commit 205fc42 on `wt/wt-firms` (Q-115's keys included) and Q-136b's entries in the wt-firms working tree, read by key, never typed (4.1) |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16, read only inside Stage 2's engine by P-14's and P-16's registered builders, in part F alone; parts A to E read no bar |
| the unit | part C: one account in one mode, a coin path; part F: one start day replayed as U1 replays it, paired with Topstep on the same start |
| judged-block reads | part F only, three purposes on the line of section 6 item 5 |
| conduct | D-145's three tiers as the operator ruled them (E-013), applied mechanically to each cell's behaviour (4.7) |
| seeds | a block of ten, six in use and four reserved (section 15) |
| confirmation | none: nothing is carried (section 14) |
| `confirmation_tests_on_this_market` | 3: NQ's three of Stage 2 D-107's three are spent (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`, `held_back_2025`); this reading adds none and reads no NQ from 2026-07-17 |

---

## 0. What a mode changes, stated truly; and what "flip" means here

**Two modes.** Each plan sells an **evaluation** and, on a pass, a **funded** account. They are separate accounts with
separate rules -- the target, the drawdown's type and lock, the daily loss limit, the consistency rule, the contract
cap and its scaling, the payout gates. This reading treats them as two modes: each mode's policy is declared on its own
(section 2.6), each mode is read on its own (parts B, C, E), and the two are joined only at the switch (section 2.7).

**What a mode's policy changes.** On the coin it changes everything, since the coin is only a policy. On the
registered trades it leaves the **offered** trades unchanged and changes the **executed** sizes -- and, for the flip,
the executed set (above) -- and through them the floors, the passes, the payouts, the fees and the router's later
choices, from the first session it binds. So every registered cell is a matched pair with its reference on every start
day, the market path's luck shared.

**The word "flip".** In this reading a **flip day** is the operator's sense (E-196): a day large enough that passing
the evaluation, or reaching the first payout, takes only one or two days. A **flip-seeking policy** sizes trades for
that on purpose (section 2.6). Not meant: Stage 2's **flip stream** (Stage 2 D-338, D-343;
`vendor/stage2/propedge/campaign/flip.py`), and **contract flipping** (reversing a position), which no policy here does.

## 1. What this reading is, and what it is not

**Its job.** It answers the operator's questions of E-196 for the $50K plans, one part each:

| the operator's question (E-196; the brief Q-137) | part |
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

**Why described rather than tested.** E-023 (1), as E-134 (1) applies it: nothing here adds an offered trade. The
judged block's few independent stretches (audit B, `docs/audits/phase0/B_objective.md`, Q3) would leave a plan or
policy comparison on P undetectable at any numbered family's level (E-023).

**What the operator's choice from it will mean.** Recorded in its own decision row as a choice from a described
development reading; no registration id, no confirmation; every statement from part F is a description of the
development window, in sample. Buying any plan is a purchase: the operator's, stated and waited for.

## 2. The plans, the modes, and the user

### 2.1 The plans in scope

| id | plan | configuration | why here | terms from (key prefix, Appendix R) |
|---|---|---|---|---|
| `TS-S` | Topstep $50K Trading Combine -> Express Funded Account | Standard price path; the funded payout path Standard (`TS-S/std`, the reference) or Consistency (`TS-S/con`), chosen at activation | the reference: P-14's and P-16's registered rows | Stage 2's verified ledger |
| `TS-N` | the same | No Activation Fee price path; the same two payout paths | the brief: both price paths | the ledger; `subscription_fee_naf_50k`, `activation_fee_naf_50k` (the record) |
| `L6` | Topstep Labs #006 $50K Static Drawdown Combine | the funded path Standard (`L6/std`) or Consistency (`L6/con`) | new (E-197) | `labs.006_50k_static.*` |
| `L10` | Topstep Labs #010 $50K Daily Payouts+, end-of-day | the funded request read two ways (2.8): the Daily path (`L10/day`) or the 5 Winning Days path (`L10/5wd`) | new (E-197) | `labs.010_50k_dpp_eod.*`, `labs.010_011_50k_dpp.*` |
| `L11` | Topstep Labs #011 $50K Daily Payouts+, static | `L11/day`, `L11/5wd` | new (E-197) | `labs.011_50k_dpp_static.*`, `labs.010_011_50k_dpp.*` |
| `RE` | My Funded Futures Rapid EOD 50K | the default version (no daily loss limit) | E-196, E-197 | `mffu.rapideod50k.*`, `mffu.*` |
| `RED` | My Funded Futures Rapid EOD 50K, the daily-loss-limit version | its terms sit inside `RE`'s entries (the "DLL version" clauses of `mffu.rapideod50k.eval_daily_loss_limit` and `funded_daily_loss_limit`) | the same | the same |
| `RI` | My Funded Futures Rapid 50K | the funded drawdown trailing intraday on equity | the same | `mffu.rapid50k.*` |
| `PRO` | My Funded Futures Pro 50K | -- | the same | `mffu.pro50k.*` |
| `PRO1` | My Funded Futures Pro 50K One Day | the evaluation differs (`mffu.pro50k_oneday.eval_terms`); its funded mode is `PRO`'s (`mffu.pro50k_oneday.funded_terms`) | the same | the same |
| `B20` | My Funded Futures Builder 50K, the default drawdown | -- | the same | `mffu.builder50k.*` |
| `B15` | My Funded Futures Builder 50K, the add-on drawdown | its terms sit inside `B20`'s entries (their "Add-On" clauses) | the same | the same |
| `LU40` | Lucid Trading LucidFlex 50K | daily loss limit off, standard consistency (`STANDARD_40`) | Stage 2's verified second firm (Stage 2 D-574, D-575) | the vendored Lucid ledger, through `propedge.contract.lucid`, by import |
| `LU50` | the same | daily loss limit off, the consistency add-on (`ADDON_50`); its funded mode is `LU40`'s | the same adapter's second verified configuration | the same |

**Lucid's terms come only from Stage 2's verified record** (E-197: Lucid's terms of 2026-11-13 forbid automated copying;
the scout's captures after it verify nothing). **My Funded Futures' price history** (Stage 2 D-573: withdrawn on price)
is exactly what the zero-edge map's fee columns read (9.4).

### 2.2 The modes, per plan

| plan | evaluation mode | funded mode |
|---|---|---|
| `TS-S`, `TS-N` | the Trading Combine (one evaluation mode; the price path changes only the fees) | `TS/std`, `TS/con` |
| `L6` | the Static Combine | `L6/std`, `L6/con` |
| `L10`, `L11` | the Daily Payouts+ Combine, end-of-day or static | `L1x/day`, `L1x/5wd` |
| `RE`, `RED`, `RI` | the Rapid EOD or Rapid evaluation | `RE`, `RED`, `RI` |
| `PRO`, `PRO1` | Pro, or Pro One Day | `PRO` (one funded mode for both) |
| `B20`, `B15` | Builder, default or add-on | `B20`, `B15` |
| `LU40`, `LU50` | LucidFlex at its two consistency settings | `LU` (one funded mode for both) |

That is **13 evaluation modes and 15 funded modes** before section 5's two-ended terms. What makes each funded mode
differ is in its record entries (Appendix R).

### 2.3 Not here, and why

- **Instant- or direct-funded products** -- recorded, not modelled (E-196). None was found at Topstep or My Funded
  Futures (each note marks the absence UNVERIFIED where a page renders by script); Lucid's LucidDirect is a pointer
  only. Such a product joins only under a new declaration, never by section 2.4.
- **The daily-loss-limit elections of the in-scope firms' plans** -- Topstep's on the standard Combine (it changes the
  funded caps, `dll_offer_status`), Lucid's DLL-on LucidFlex configurations (their On Demand Payouts are unmodelled by
  Stage 2's adapter): different accounts, a later reading. My Funded Futures' Rapid EOD DLL version is a separate
  product (`RED`).
- **Topstep's $100K and $150K sizes and Labs' other drops; My Funded Futures' Flex (legacy), Studio, Perps; live
  accounts at every firm (G-4); Back2Funded, resets and the evaluation inventory** (RD-03's levers).
- **Lucid's LucidPro, LucidDaily and LucidMaxx, and every Alpha Futures plan** -- they join only by section 2.4.

### 2.4 The conditional join rule (declared now, so nothing is chosen after the captures)

**One rule: a firm joins whole, or not at all.** Lucid's other $50K plans and Alpha Futures' $50K plans join this
reading only if every condition below holds for **every** configuration the capture enumerates, at the commit of
section 18's step 0 run; **any configuration that fails holds its whole firm back**:

1. **Recorded.** The operator's by-hand capture (`docs/OPERATOR_SETUP.md` item 11, E-197) has been recorded by the
   rules-verifier in `config/rules_extended.yaml` and `docs/RULES_CURRENCY.md`, and the lead's row taking it is in
   `DECISIONS.md`.
2. **The configuration list is the capture's own checkout enumeration** -- every plan the firm sells at $50K with an
   evaluation then a funded account, and every checkout configuration of each (daily-limit elections and consistency
   add-ons included). **A configuration whose price is unrecorded blocks the firm's join; it is never left out.**
   Instant- or direct-funded and invite-only products are not configurations of this list (2.3).
3. **Every term role of Appendix R resolves** for each configuration and mode -- to a verified entry, or to a rule of
   section 5 that this file already states. No new rule is written for a joining firm.
4. **Every term reaches the engine through this file's catalogue** -- a field, an adapter of 4.3 or a gap of 4.4.
5. **Conduct** is classed by section 4.7's tiers, mechanically, as for every plan here.
6. **The grids, measures, seeds, order and horizons are this file's, unchanged.** The joining configurations are
   appended to Appendix M **in the record's own order of their entries**, and their cells are counted by section 16's
   formula in the lead's join row before step 0 runs. The seed keys (section 15) do not depend on a configuration's
   index, so a join changes no stream.
7. **Firm order.** A joining firm runs after every plan of 2.1.

**Lucid joins whole or not at all** (the red team's N-3): Lucid's joining enumeration is every configuration the capture
lists at $50K, **LucidFlex's own configurations included** (its DLL-on ones too). LucidFlex's DLL-on configurations
bring On Demand Payouts, which no adapter of 4.3 models, so **while that stands Lucid's other plans cannot join** by
condition 4 -- they wait for a new declaration. **LucidFlex stays on the vendored record in this reading** whatever a
Lucid capture records about it: `LU40` and `LU50`
are read as Stage 2 verified them, and a difference the capture shows is listed beside their rows, for a later
reading. A capture recorded after step 0's run commit waits for a new declaration; nothing of this reading is re-run
for it. The firms' clauses against automated reading (E-020 (2), E-197) bar reading their sites by machine, not code
reading the recorded terms.

### 2.5 Today's terms, on every start

Each plan's terms as the record reads them (its `date_read`) are applied to every start day from 2020 to 2026, as
Stage 2 replays Topstep's current rules; rule changes over the history are not modelled (G-6). Every result names the
record's commit and entries it used (E-196).

### 2.6 How each mode trades: the declared grid and the two policies

**The coin (parts C and D).** A coin trade is a bracket on a driftless price path: a stop at `r` dollars below the
entry, a target at `w x r` above. The chance of the target first is `1 / (1 + w)` and its expected gross profit is zero.
It is stage one's binary trade at zero edge, with the floor and the daily limit read as closer exits on the same path
(the vendored `RandomDraw`, `floor_mode` "truncate", `edge_mode` "drift" at zero edge: the barrier race
`p_race(c, w r, 0) = c / (c + w r)` for a room `c` below the stop). **One coin trade a session.**

**The grid, per mode (every value run; none chosen):**

| parameter | what it is | values | class | why these |
|---|---|---|---|---|
| `w` | reward-to-risk: the target as a multiple of the stop | 1.0, 1.5, 2.0, 3.0 | described | stage one's and Stage 2's reference ratios (Stage 2 D-429's screen) |
| `r` | dollar risk per trade: the loss at the stop | $250, $500, $750, $1,000, $1,500, $2,000 | described | Stage 2 D-272's Combine set, with $250 below it |
| `s` | stop width, in ticks of 0.25 index points (the same tick on MNQ and NQ) | part B: every multiple of 10 from 10 to 400 (40 widths); part C's costed coin: 50, 100 and 150 | described | part B is arithmetic, so the grid is fine; 50, 100 and 150 ticks are the registered designs' 12.5-, 25- and 37.5-point rungs |

Each mode has its own copy of the grid: the evaluation's `(w, r)` and the funded account's `(w, r)` are separate axes,
joined only at the switch (2.7; 9.5). **The gross coin has no contracts**: its dollars are `r` whatever the width, so
**no allowance or scaling ladder binds on a gross map**, and every gross row is labelled "allowance and scaling not
applied" (the red team's S3). The costed coin (9.2) has whole contracts, so it applies the allowance, the ladder and
the stop width.

**The two policies, per mode and grid cell:**

- **`steady (w, r)`** -- every trade of the mode at risk `r` and ratio `w`. On the registered trades, `steady` is the
  registered state table as it stands.
- **`flip (w, r)`** -- the flip-seeking policy: large risk early, sized from the plan's own rules. For the first `k`
  sessions of the mode, each session's first trade is sized at `r_flip`, and the account takes no other trade that
  session; from then on the policy is `steady (w, r)`.
  - **In the evaluation**, `k = k_E`, the fewest trading days in which the evaluation can pass (part A, under the plan's
    recorded consistency semantics), and `r_flip = T / (k_E x w)`, `T` the base target (the plan's `eval_profit_target`
    key): `k_E` winning flip trades in a row pass, each day's profit an equal share inside the consistency share.
  - **In the funded account**, `k = k_F`, **the sessions elapsed to the first eligible close when the account trades
    every session** (part A item 3; a clock the record states in calendar days counts calendar time, translated to
    sessions by Stage 2's rule, 4.3 A-3; a clock it states in trading days counts trading sessions; a plan with no clock
    counts its day rules alone), and `r_flip = b* / (k_F x w)`, with `b*` as section 5's U-25 defines it at the cell's
    corner (the red team's B2). Every `k_F` and `b*` is finite and fixed by step 0 before any run.
  - **The cuts, trade by trade:** `r_flip` is cut to the room above the floor (Stage 2 D-313's room cap) and to the day's
    remaining daily limit where the plan has one; every cut is counted (10.3).
  - **On the registered trades**, `w` is the ratio the table chooses for the trade; the contracts are
    `min(floor(r_flip / stop dollars), the registered sizing rule's own cap for that account kind and tier)` -- its
    headroom fraction of the allowance, read from the rule, never above it -- then the cuts above. **So a flip trade is
    never sized above the registered rule's cap, and never at the full allowance** (the major-news rule, 4.7 and the red
    team's S9). D-212's consistent-risk stand-aside is not applied to a flip trade (the flip's point is its size); every
    such trade is counted. A flip trade follows 4.7 item 3's news rule exactly as a steady trade does: no entry inside a
    verified window, a forced flat at a window's start.
  - **The calendar-to-sessions rounding** (the red team's N-1): a calendar period is translated to sessions as
    `days x billing_days / billing_period_calendar_days` (Stage 2's keys), **rounded in the direction that helps the user
    least** -- **up** for a wait that must pass before something the user wants (a payout clock, a purchase limit's
    refill), **down** for a window whose end harms the user (a lifespan, an inactivity window, a hold's expiry). So
    `PRO`'s `k_F`, and with it its `r_flip`, are fixed by this text.

`flip` cells pair with their `steady` cells on common random numbers (section 15). On the registered trades, a `flip`
cell pairs with its plan's `steady` cell on every start.

### 2.7 The switch between modes

- **When.** An evaluation ends at the close at which its pass condition holds. The funded account is activated that
  evening and trades from the **next session** -- Topstep's verified convention (`xfa_activation_latency`), applied to
  every plan; My Funded Futures' same-day upgrade is read a session later at most, labelled (G-3).
- **What carries over.** Nothing but the pass: the funded account starts at its own rules' start state and its own
  mode's policy. On the coin the funded mode's streams are independent of the evaluation's (section 15), so a pair of an
  evaluation cell and a funded cell is read by exact arithmetic (9.5), never re-run.
- **Fees at the switch.** Each plan's activation fee by its key (Appendix R), paid at activation; a passed Topstep
  Combine's subscription ends at the pass.
- **On the registered trades**, the switch is the engine's own; a funded account's flip window counts from that
  account's own first session.

### 2.8 The user held fixed for part F (RD-01 section 2.3's, carried)

- **The trades.** P-16's registered trades (`rc_s150_all_nr`, `rc150_dev_test.TRADES_SHA256`) as the headline and P-14's
  (A3-BRK30-CB20, U1's own builder) beside, each with its registered state table, protocol and routing (the
  longest-waiting account, one position at a time across the firm with five minutes flat, Stage 2 D-429), its purchase
  budget (P-14's), and its sizing rule's mode, headroom, stand-aside and room cap. Only the plan's allowances, its
  per-trade costs (4.5) and the inputs its accounts hand the table (4.6) replace Topstep's.
- **The seats.** Five accounts of every kind together, each design's own; where a plan's funded cap is below that
  (`mffu.max_funded_accounts` names `RE`'s and the Builder plans'), a pass waits by U-14 and the waits are counted.
- **No resets, no reactivations, no daily-limit elections** beyond a plan's own.
- **The request rule** (RD-01 2.3, carried; its amounts by Stage 2's keys): at every close at which the plan's own rules
  make the account eligible, request `min(payout_max_frac_of_balance x B, xfa_std_cap)` -- B the balance above start --
  cut to the plan's per-request cap, its remaining-balance (buffer) rule and its increment; none below its minimum.
  Where the plan gives the path at each request (`L10`, `L11`), the path is the cell's. The payout lever is RD-02's
  subject, not this one's.
- **Hand entry**, at least five minutes from alert to order (E-008); one user's own accounts at one firm.
- **Conduct.** Section 4.7's tiers, applied to every cell's behaviour.

## 3. Prior exposure: what has already read these plans and policies, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| stage one (`vendor/stage2/vendor/propsim/README.md`; propsim D-02, D-04, D-45) | the coin on Topstep's $50K: a fair strategy's pass ceiling, the funded martingale bound, the best static profile by exact Markov chain, the supremum over fair strategies | no data | analytic and simulated contract values; its buy-until-pass coin campaign read as account stacking (the README, D-34) | the oracles of 9.6; the TS evaluation map's (1.0, $1,500) cell is stage one's reference profile |
| stage one T5 (`edge/T5_RESULTS.md`; propsim D-44, D-45) | payout policy | no data | exploratory; payout policy first-order | the request rule is fixed (2.8, 9.2), not read |
| Q-12's survey (E-009) and Stage 2's propfirms ceilings (`vendor/stage2/vendor/propfirms/docs/T3_CEILINGS_DERIVATION.md`) | zero-edge ceilings from quoted terms, arithmetic | no data | "no firm clearly above Topstep's $50K" (E-009) | the drafter saw only the lines the firm note cites |
| Stage 2 D-313 | over-risking in the evaluation lifts the consistency target; the consistency and room caps | gate paths (exploratory) | the target lifted in some attempts, delaying passes (in words) | the coin counts consistency extensions (9.3); the room cap cuts `r_flip` (2.6) |
| Stage 2 D-338, D-343 | the flip stream | gate paths | closed | not this reading's flip (0) |
| Stage 2 D-573, D-574 | My Funded Futures withdrawn on price; Lucid's prices | -- | operating decisions | 2.1 |
| Stage 2 D-575 ... D-643; U1 `p16_5+1` | Lucid seats beside Topstep's | gate paths; all starts | closed (RD-01 section 3) | LucidFlex alone is RD-01's |
| Stage 2 D-652, E-125 | a funded account's life after its opening; P-14's evaluation trades' mean | gate paths; `results/p14_validation.csv` | most funded accounts lose the opening; the evaluation trades' mean negative on P-14 | the funded flip acts on the opening; part F's evaluation rows rest on trades that lose on average |
| RD-01 (pinned; built, not run) | P-16's and P-14's trades on Topstep, LucidFlex `STANDARD_40`, DayTraders, TradeDay | all starts | no result on master | `LU40`'s registered rows are RD-01's, never re-run here (12.1) |
| RD-03 (pinned; built, not run) | contract-use levers, the No Activation Fee path among them (`naf`) | all starts | no result on master | `TS-N`'s registered rows are RD-03's `naf` cells, never re-run here (12.1) |
| RD-02, RD-04 (pinned) | payout policy; volatility | all starts | not run on these plans | none read here |
| U1 (Stage 2 D-620), Q-05 (E-010), Q-44 | P-14's and P-16's own journeys; the readings beside | all starts | the reference rows; Q-44 running at this text | the references are known in full |
| program U's nine families | P on the late block against P-14 | starts from 2024 | all closed | the late block is late development, not out of sample |

**Never run:** any coin on a Labs, My Funded Futures or `ADDON_50` contract; any registered trade on a Labs or My
Funded Futures contract or on `ADDON_50`; any flip-seeking policy; any per-mode coin grid.

**The drafter's own reads (disclosed).** For the first text as that text listed them. For this text, in addition: the
red team's note (whole); `DECISIONS.md` E-198; Q-136's record at 205fc42, every `labs.*` and `mffu.*` entry's key,
status and value and the notes of about forty of them, and `tou_s8_relative_position_size`'s value; Stage 2's
`sizing.py` (`DEFAULT_HEADROOM_FRAC`'s name). **No result file of either repository was opened.** The seed search
printed counts only.

**What is already known of the direction (disclosed).** At Topstep a fair strategy's pass rate and funded payouts are
bounded (stage one); over-risking in the Combine lifts the consistency target (D-313); Topstep's pages say the Combine
cannot pass in one day (E-197). Nothing is known of any coin map on any other plan, of any flip policy, or of the
registered trades on any Labs or My Funded Futures plan.

## 4. The rules: where they come from, the term roles, and how each reaches the engine

### 4.1 Where the rules come from, and the merges that come first

Every rule a cell leans on comes from Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`), the vendored Lucid
ledger (through Stage 2's adapter), or this repository's record (`config/rules_extended.yaml`, `docs/RULES_CURRENCY.md`).
**The Labs and My Funded Futures terms, and Q-115's No Activation Fee keys, are in the record at Q-136's commit 205fc42
on `wt/wt-firms`** (committed by the lead, not merged; E-198). **This text names every term by the key that commit
records** (Appendix R) and types no rule value: every value is read from the record by a loader that refuses an entry
not `verified` (17.2); an `unverified` or `unstated` entry is never loaded as a value -- it is read by a rule of section 5.
A role with no key is a **pin blocker**. The second text's two -- My Funded Futures' commissions and its single-day
profit ceiling -- are cleared by **Q-136b's entries**, read from the wt-firms working tree, where the lead commits them:
`mffu.commissions` verified (firm-wide, naming no plan or account type); `mffu.<plan>.commissions` unverified, for all
five plans; `mffu.rapideod50k.funded_single_day_profit_ceiling` and `mffu.rapid50k.funded_single_day_profit_ceiling`
verified; the other eight ceiling keys unstated. **No pin blocker remains beyond the record's merge** (19).

**The merge comes before step 0** (section 18): it writes under `config/`, which every identity's cover includes
(E-117), so every shared identity is held again at a commit containing it before anything of this reading runs. If an
entry's status at the merged commit differs from 205fc42's, the corners and counts follow it by T-0's rule at the pin;
a change after the pin is a new declaration.

### 4.2 The term roles, and how each reaches the engine

**What the engine represents** (RD-01 section 4, carried): Stage 2's `CombineAccount` and `FundedAccount` (targets,
floors trailing at the close and their locks, consistency as `max(target, best day / share)`, a soft daily limit, the
Standard path's winning days, the Consistency path's cycle share and days, a request of `min(share x balance, cap)`
above a minimum, one split, the request-day exclusion), the sizing rule's allowance and ladder, the fees and billing,
the lag, the seats, the household rule. **Stage one's engine** (`propsim.simulate_combine`, `simulate_xfa`) represents
the same contract for one account on a binary stream **without** the daily limit, the request-day exclusion, contracts
and the ladder; part C's coin engine adds the first two as marked additions (A-0, A-1, A-16) and states the last two as
not applied on the gross coin (2.6).

**Each role reaches the engine as a field, an adapter of 4.3 (`A-n`), a gap of 4.4 (`G-n`), or moot (checked).** Static
means a floor that never moves. Appendix R gives every key.

| mode | role | `TS` | `L6` | `L10`, `L11` | `RE`, `RED` | `RI` | `PRO`, `PRO1` | `B20`, `B15` | `LU40`, `LU50` |
|---|---|---|---|---|---|---|---|---|---|
| E | target, drawdown amount | field | field | field | field | field | field | field | Stage 2's adapter |
| E | drawdown type and lock | field | static: field | `L10` field; `L11` static: field | field | field | field | field; breach basis U-27 | adapter |
| E | daily loss limit | none | soft: A-1 | soft: A-1 | `RE` none; `RED` soft: A-1 | none | none | U-28 (A-1 at its strict end) | none (off) |
| E | consistency and its base | field | field | field | field (U-15) | field (U-15) | `PRO` field (U-15); `PRO1` none | none | adapter |
| E | minimum trading days | implied | none | none | A-2 (implied: part A checks) | A-2 (implied) | A-2 (implied) | A-2 | implied |
| E | position cap and counting | field | field | field | field | field | field | field | adapter |
| E | lifespan; inactivity | none | A-3 | A-3 | A-3 | A-3 | A-3 | A-3 | adapter |
| E | price; purchase limit | field | field; U-24 | `L10` U-2; `L11` field; U-24 | U-2 | U-2 | U-2 | field | adapter |
| F | floor start, type, lock | field | static: A-5 | `L10` field; `L11` static: A-5 | field | **A-6**; lock U-29 | A-5 (U-16) | field | adapter |
| F | floor at a payout | field | A-5 | A-5 (a daily payout) | field | field | A-5 (U-16) | A-5 | adapter |
| F | daily loss limit | none | soft: A-1 | soft: A-1 | `RE` none; `RED` soft: A-1 | none | none | U-28 | none |
| F | the payout gate | field (both paths) | field, path by cell | **A-7** (Daily path); field (5 Winning Days) | **A-8** | A-8 | **A-9** (clock; U-17) | **A-10** (U-18) | `LucidFundedAccount`; coin form A-17 |
| F | the request's size | field | field | A-7; field | **U-25** | U-25 | U-25 | field (its cap) | adapter |
| F | an end by count or ceiling | none | none | none | **A-11** (the verified single-day ceiling) | A-11 (the same) | the per-user cap: moot, counted; no ceiling (unstated) | A-11 (the count); no ceiling (unstated) | adapter (A-17 on the coin) |
| F | allowance and scaling | field | field (U-20) | field | field | U-30 | **A-12** (U-26) | field | adapter |
| F | seats | field | field | field | field (U-14) | field | field | field (U-14) | moot |
| both | per-trade costs | 4.5 | 4.5 (U-23) | 4.5 (U-23) | 4.5 (U-32) | 4.5 (U-32) | 4.5 (U-32) | 4.5 (U-32) | 4.5 |
| both | news | U1's own rule (4.7 item 3) | U1's own rule | U1's own rule | F: A-18 by U-31 | F: A-18 | F: A-18 | U1's own rule (unrestricted) | U1's own rule |

### 4.3 What the engine cannot represent: adapters in `extended/` (declared; built after the pin)

Every adapter subclasses or wraps a vendored seam or copies a vendored body under Q-71's pattern (a guard refusing
unless the vendored source hashes to its pin; a proof that the copy with its marked lines removed parses to the vendored
one; marked additions only, each off by default); none edits `vendor/` (E-011, Q-47). **Each has two forms -- an
account class for part F (RD-01's pattern, `extended/firm_accounts.py`) and a vectorised addition to part C's coin
engine (A-0) -- held equal on scripted streams, account for account (T-3).** With every switch at its Topstep setting
each is the vendored behaviour bit for bit (T-1, T-2). If any cannot be built that way, the build stops and reports.

| id | adapter | what it adds |
|---|---|---|
| A-0 | the coin engine (`extended/modes_engine.py`) | `propsim.simulate_combine` and `simulate_xfa` copied verbatim with marked additions A-1 to A-17 (A-18 is the replay's, A-19 the rules') and three more: separate evaluation and funded policies with `flip`'s schedule (2.6); the costed coin draw (9.2); online counters for parts D and E (A-13). With every addition off, every output array equals the vendored function's on the same seed and draw, bit for bit |
| A-1 | a soft daily loss limit | the day's trading ends when its loss reaches the limit; the account is not failed; the room a trade is handed is the smaller of the room above the floor and the day's remaining limit (as `lockstep.py` hands it). A record that reads a limit as a failure gives the hard form, by its record |
| A-2 | evaluation minimum trading days | a pass needs that many sessions with an executed trade (RD-01's A-4 form); part A checks, plan by plan, whether the consistency share already implies them (the red team's N5); where implied, A-2 cannot bind and is checked so |
| A-3 | lifespan and inactivity | the evaluation ends unpassed at its lifespan; an account with no trade in the stated window ends (funded: its profit forfeited where the record says so); calendar days exact in the replay, translated to sessions on the coin and in the gate by Stage 2's rule (`billing_days` sessions per `billing_period_calendar_days`), labelled |
| A-4 | a purchase limit | the campaign's evaluation supply capped as U-24 reads it; on the coin it enters 9.5's per-user arithmetic only |
| A-5 | the funded floor's own rules | a static floor; the floor's move at a payout to the record's level; `PRO`'s two readings (U-16) |
| A-6 | the intraday equity trail (`RI`) | exact on the coin within its read set (9.2); bracketed on the registered trades (U-21) |
| A-7 | Labs' Daily path | eligibility each session once the balance clears the buffer and the minimum; one request a session at most within the path's minimum (U-22) and maximum; the floor's move at a daily payout (`labs.010_011_50k_dpp.daily_path_mll_effect`); the request's source and timing (U-22) |
| A-8 | My Funded Futures' buffer gate and cadence | a request needs the balance at the buffer plus the minimum and leaves the buffer (never the vendored `keep_balance`, a policy); the first request not before the gate's stated time after the first trade; later requests after the gate's stated profit since the last (none where the record states none, U-10) |
| A-9 | `PRO`'s payout gate | the calendar clock of `mffu.pro50k.payout_timing` from the first trade and between requests; the buffer at two readings (U-17); the minimum |
| A-10 | Builder's payout gate | the cycle's consistency share and day count (the engine's Consistency-path fields), the buffer and first-payout balance, the time after the first trade, the profit since the last request, the per-request cap; the first cycle's base at two readings (U-18) |
| A-11 | an end by count or by the single-day ceiling | Builder's end at `mffu.builder50k.max_sim_payouts` (Stage 2's `_after_payout` seam, `lockstep.py` 854); `PRO`'s per-user cap moot within the horizon (counted, U-7); **at `RE`, `RED` and `RI`, the verified single-day ceiling** (`mffu.rapideod50k.funded_single_day_profit_ceiling`, `mffu.rapid50k.funded_single_day_profit_ceiling`): a funded session whose net profit exceeds the key's threshold has the excess forfeited that day, and the account's modelled life ends at that close -- **a terminal state "moved to Live"**, printed apart from passes, failures and payouts, never counted as a payout, its remaining balance not credited (Live terms are not recorded, G-4); where a plan's ceiling key is unstated, nothing applies. On the coin, step 0 lists the cells at which one trade's win can exceed the threshold; elsewhere the rule cannot bind (checked) |
| A-12 | an allowance counted in contracts | `PRO`'s funded cap at U-26's two readings |
| A-13 | the online counters for parts D and E | per account: the flip and steady wins at a pass (from which `k*` follows exactly, 10.1), the session each gate first holds, the ending and its cause, the conduct exposures of 10.3 -- O(accounts) memory, never a per-session array (the red team's S12); in the replay, Q-94's recorder and the account classes' counters |
| A-14 | the composition (`extended/modes_plans.py`) | each configuration's contract applied to a design's replay and gate arguments and to the coin engine, as RD-01's A-1 (`extended/firms.py`); `TS` leaves every argument unchanged (tested equal); `LU40`, `LU50` by Stage 2's `rc150_firm_split.lucid_setup` at each configuration |
| A-15 | the readings (`extended/modes_reading.py`, `scripts/modes_*.py`) | parts A to F in section 18's order; section 13's checks; the menu; RD-02's 9.2 functions imported (`extended/pp_reading.py`) |
| A-16 | the request-day exclusion on the coin | the session after a request at a plan whose record excludes it does not count toward the next window (`REQUEST_AFTER_5PM`'s rule, 8284233), so `TS/std` and the Labs 5 Winning Days maps carry it (the red team's S3) |
| A-17 | LucidFlex's coin form | `LucidFundedAccount`'s three differences on A-0 -- the cycle's net-profit gate, the end at the stated payout count, no request-day exclusion -- and the evaluation lock above start, from Stage 2's adapter's own terms (`lucid_terms()`), imported |
| A-18 | the news rule in the replay (4.7 item 3; the red team's B-1) | at an account a verified news rule reaches, on a release day of a pinned calendar: **no entry** whose alert falls inside the window -- decided at the alert from the clock and the calendar alone, the router passing the signal on as RD-01's A-5 no-trade decision -- and a position **open at the window's start is flattened at that bar**: the 1-minute bar stamped at the window's first minute, read through `extended.reader` under the run's purpose, priced at its open with the fill rule's flatten slippage (`fills.yaml`'s active profile, `flatten_slippage_ticks`); whether the position is open is the walk's state at that minute, known then. **Beside it, RD-01 G-3's bracket** on the flattened trades' own P&L (strict: the full stop loss; lenient: the target less a tick, with the flatten's cost) and the walked outcome, per trade and summed, the journey not re-run. Off in the gate (its days carry no date), the gate rows labelled. It changes nothing at an account no verified rule reaches, so every `TS`, Topstep and Labs trade is exactly U1's (tested) |
| A-19 | the U-rule parser (the red team's S-3) | a U-rule end's figure that the record holds only in an unverified entry's `quote` is parsed from that quote, fail-loud, by a pattern declared beside the rule (RD-01's `extended/firm_terms.parse`, with a test on each entry): U-16's and U-29's lock levels, U-17's within-buffer share, U-22's two minimums, U-24's limit, U-28's daily limit, U-30's starting allowance. A figure in no quote is a pin blocker (none at this text; T-0 confirms each parse at the pin) |

### 4.4 What is not modelled, listed as gaps

| id | gap | how it is shown |
|---|---|---|
| G-1 | the registered state tables solve Topstep's Standard path (Stage 2 D-501) and are not re-solved for any plan or mode; 4.6's mappings are part of "the design traded there" | every part-F row "first-order, the table fixed" |
| G-2 | the coin has no calendar, so no news rule reaches a coin map; My Funded Futures' broader protocol on every release (`mffu.news_all_releases_protocol`, unverified) has no pinned calendar of every release here; Topstep's window schedule is in an entry whose status is `changed` (`tier1_news_events_restriction`), not loaded | coin rows "no calendar: no news rule"; part F follows 4.7 item 3; the broader protocol's strict reading not modelled, labelled on every My Funded Futures row; at Topstep and Labs the designs' own entry rules (U1's) stand, and trades open in the changed entry's windows are counted (expected zero, 12.4) |
| G-3 | My Funded Futures' same-day upgrade; Labs' identity verification | the next session (2.7) |
| G-4 | every live move: Topstep's, Labs', Lucid's, My Funded Futures' (Rapid's and Rapid EOD's verified single-day ceiling, A-11; Pro's reviews; Builder's after its count); Live terms are not recorded | live accounts not modelled; an account moved ends, its balance not credited; the ceiling's move a terminal state of its own, "moved to Live" (A-11); where a ceiling key is unstated, no ceiling applies; Pro's reviews counted |
| G-5 | Topstep's Focused Trader Program (unpublished thresholds; its binding models are Topstep-standard) | not run here, the gap named on every Topstep row |
| G-6 | rule changes over 2020-2026 | today's terms on every start |
| G-7 | My Funded Futures' price-limit rule (funded) | not modelled, labelled |
| G-8 | the Simulated Trader Agreement behind login at My Funded Futures | not read; labelled |
| G-9 | a user who skips sessions on the gross coin | the gross coin trades every session while alive, so inactivity cannot bind on it (checked); the costed coin can stand aside (9.2) and is not so bounded |
| G-10 | holiday hours, the request screen's amount choice, processing within a session | lags at their brackets (U-5) |

### 4.5 Per-trade costs (the cost rule, per plan; declared)

| plan | schedule (round turn: MNQ, NQ) | from | open |
|---|---|---|---|
| `TS`, `L6`, `L10`, `L11` | Topstep's all-in schedule (`vendor/stage2/config/fills.yaml`, `round_turn_by_instrument`; 8284213) | the registered schedule | Labs at Topstep's schedule by U-23 |
| `RE` ... `B15` | **U-32's two ends**: strict, the firm-wide `mffu.commissions` figures on every fill, evaluation and funded; lenient, the engine's own commission, as on the registered trades (Topstep's schedule) | Q-136b: `mffu.commissions` verified, firm-wide; `mffu.<plan>.commissions` unverified | the figures read from the key, never typed |
| `LU40`, `LU50` | Topstep's schedule, as Stage 2 D-575 reads Lucid | RD-01 4.8 | conservative in this term |

**The costed coin** uses the same schedule at its contracts, plus the slippage of `fills.yaml`'s active profile (its
entry and stop ticks; a target fills at its limit), valued at `vendor/stage2/propedge/execution/instruments.py`'s tick
values, read, never typed.

### 4.6 What each plan's accounts hand the table (RD-01 4.9's rule, extended; declared)

RD-01 4.9's rule is carried unchanged: `win_days = min(5, max(0, 5 - the plan's own days still needed))`; **held at 4**
when the plan's day count is complete but another of its gates still blocks the request; `since_pay` the plan's profit
since the last request; `request_day_next` 1 only on a session the plan excludes after a request.

| plan, mode | the plan's own days | `win_days` read by the table | `request_day_next` |
|---|---|---|---|
| `TS/std`, `L6/std`, `L1x/5wd` | Topstep's winning days | the engine's own | the engine's |
| `TS/con`, `L6/con` | -- | not run on the registered trades (12.1) | -- |
| `L1x/day`, `RE`, `RED`, `RI`, `PRO` | none: the buffer, the cadence or clock, the profit since the last request | 5 when eligible; 4 while a gate blocks | 0 |
| `B20`, `B15` | the cycle's day count | `min(5, max(0, 5 - days still needed))`; 4 while the share, the buffer or the time blocks | 0 |
| `LU` | Lucid's winning days | the engine's own | 0 |

**An evaluation at or above its target with days still owed** (A-2's plans, where part A finds the days not implied):
RD-01's TradeDay rule -- at most one trade a session at one micro and the table's R until the days are logged. **On the
coin** the case is moot wherever the share implies the days (part A checks it, the red team's N5); where it does not,
the coin keeps its policy until the days are logged, counted.

### 4.7 Conduct: D-145's tiers, applied to each cell's behaviour (the lead's ruling on the red team's B1)

**The tiers are the operator's, as Stage 2 D-145 ruled them and E-013 carried them.** They are applied **mechanically,
to what each cell does, from rules on the record** -- never by a policy's name, by a quote's words, or by a later row.
Every label is computed by the run from the cell's own outputs and **frozen at the run's commit**; no label changes
after a run, and a reclassing is a new declaration (the red team's B1 (d)).

1. **Tier 1, hard.** D-145's mechanical list -- cross-account hedging; exploiting simulator fills (tight brackets or
   auto-breakeven for simulator fills); trading outside the best bid or offer; maximum position size into a major news
   event; coordinated trading -- and anything that conceals a pattern; **plus a firm's own rule that is mechanical and
   prohibits a behaviour outright, where the record says so in a verified entry** -- and **a firm news rule applies only
   when its record key is verified** (the red team's S-2): My Funded Futures' funded Tier-1 rule on Rapid and Pro,
   `mffu.news_tier1_rule`, verified, reaching `RE`'s and `RED`'s funded accounts only by U-31 (their own
   `mffu.rapideod50k.funded_news` is unverified); its hedging rule, `mffu.hedging_rule`. **Topstep's
   `tier1_news_events_restriction` has status `changed`, so it is not loaded**; its event list, as the record states
   it, holds no FOMC minutes; and the Labs cap `labs.50k_static.tier1_news_cap`, though verified, takes its windows from
   that entry, so it is not applied either. **No build applies the minutes calendar to `TS` or to any Labs account
   beyond what U1 does**, so `TS`'s rows stay U1's (13.1). **Tier 1 is enforced, not counted:**
   every trade of every cell follows these rules by construction (one position at a time across the firm, D-429; the
   news rule of item 3), and the run checks each one at zero; **a nonzero count is an engine error** that stops its step
   (13.1). No cell is "labelled tier 1"; a cell that breaks tier 1 is a broken run.
2. **Tier 2, modelled.** Topstep's Responsible Trading Program (13620045, `responsible_trading_program`): the placement
   off in the headline (Stage 2 D-289), on beside at `TS` (12.3). Its triggers are counted on every Topstep cell
   (10.3: trades at the full allowance; accounts at their floors on one day).
3. **Major news, decided at entry (D-145's tier 1; the lead's ruling on the red team's B-1).** Every trade -- flip and
   steady alike -- follows the registered designs' own news rule (CHARTER section 4, as U1 applies it); the `TS` rows
   keep exactly the rule their identity and U1 use, and nothing here changes them. **Where a verified firm news rule
   reaches an account** (item 1), on a release day of a pinned calendar (E-050's `config/calendar_fomc_minutes.csv`, each
   release's time in its rows): **no entry inside the window** -- decided at the alert from the clock and the calendar
   alone -- and **a position open at the window's start is flattened at that bar**, priced from the bar under the
   existing fill rule, with RD-01 G-3's bracket beside (A-18). Nothing is decided from a trade's exit. The window's
   bounds are the record's minutes around the release's time, derived, never typed. No trade is ever sized at the full
   allowance (2.6). The forced flats and the entries refused are counted (12.4); an entry inside a window is a tier-1
   count that must be zero.
4. **Tier 3, priced.** Every discretionary clause -- **Account Stacking** (10305426, `prohibited_trading_strategies`),
   **excessive purchases and the sole-discretion catch-all** (10296582, `prohibited_conduct`), **Terms of Use s.8**
   (`tou_s8_relative_position_size`, E-013 (1)), **My Funded Futures Pro's Consistent Trading Policy**
   (`mffu.pro50k.funded_conduct_policy`, "restrictions, penalties or termination at MFFU's discretion", read by Q-136
   as tier 2 / 3 priced), **My Funded Futures' high-risk catch-all** -- is tier 3: priced by the payout-denial ladder
   (10, 25, 50 %) beside every part-F cell, the verdict at 0 % (E-008). If the record gives such a clause a stated
   mechanical consequence, that consequence is modelled instead (none at 205fc42).
5. **The exposures, printed beside every cell, the same for `flip` and `steady`** (behavioural, from the cell's own
   outputs; never a label that removes a cell): **D-145's stacking trigger, defined exactly** (the lead's ruling on the
   red team's S-6): a payout request meets it when **at least two floor breaches, across all the campaign's accounts,
   fall in the 21 trading sessions that end on the day of the request, that day included** -- in part F, the share of
   requests that meet it, from the engine's records; on the coin, whose journey holds one account at a time, the
   probability that a journey's first payout request meets it, by 9.5's renewal carrying a window state (the end
   sessions of the last two failed attempts), tested against a direct simulation (T-9); evaluations bought per 21
   sessions;
   the share of trades at the full allowance (costed coin and part F; RTP trigger 2; Pro's policy's "maximum contract
   sizes"); the s.8 ratio (each trade's contracts over the median of the same account's other trades, printed, no
   threshold); for Pro's funded mode, the spread of trade sizes per account ("uniform position sizing", printed).
6. **Tight brackets in the simulator** (My Funded Futures' `mffu.automation_and_sim_fills`; RD-01 G-14's pattern): the
   designs rest one stop and one target after a market entry; the words neither reach nor clear them; not modelled,
   labelled.

**Every cell stays on the menu** (12.6) with its exposures and its ladder; nothing is withheld by conduct, because tier 1
is enforced in every cell and the rest is priced (D-145). Section 19 carries no conduct question: it is ruled.

## 5. Unverified, unstated and conflicting terms, each read by a rule fixed now

### 5.1 The rules

RD-01's U-1 to U-12 are carried unchanged (RD-01 5.1): **U-1** a price listed differently -- both ends of the listed
bracket; **U-3** a fee no page states -- zero, an upper bound in it; **U-4** conflicting pages -- both read; **U-5** an
unstated lag -- the bracket of the verified lags of the plans here; **U-6** a stated rule with an unstated reach -- the
reading that helps the user least at the strict end, the other at the lenient end; **U-7** a term that cannot bind -- not
read, checked; **U-8** no unsized relaxation assumed; **U-9** a rule whose data the trades lack -- bracketed; **U-10** no
limit invented; **U-12** a price whose basis is unstated -- all-in at the lenient end, decomposed fees on top at the
strict end. **U-2**, the price grid, is widened here: **a price the record does not verify** is read on a declared grid
of evaluation prices, **$25 to $500 in steps of $25**, by exact arithmetic, with the break-even price at which the
per-attempt net is zero; no price inside the grid is chosen. New here:

- **U-13. A Labs term the Labs page leaves unstated** (`labs.006_50k_static.funded_payout_terms_other`; the daily
  limit's softness) -- read from Topstep's own general article for that term (Stage 2's ledger or the record), labelled
  "from the general article"; where the Labs page speaks, it wins.
- **U-14. A pass at a funded cap below the user's seats** (`mffu.max_funded_accounts`; `mffu.hold_queue_behaviour`
  unstated) -- both ends: strict, a waiting passed evaluation is closed by the inactivity rule (`mffu.inactivity_rule`)
  once its window passes untraded (the record's note's reading); lenient, it waits until a seat frees (the engine's
  queue). Part F only.
- **U-15. My Funded Futures' evaluation consistency base** (`mffu.eval_consistency_base`, unverified) -- both ends:
  strict, the account's net profit (the engine's reading, the smaller base); lenient, the sum of its winning days. The
  fixed-target base is not run: under it extra days could never meet the share, against the verified
  `mffu.eval_consistency_breach` ("trade additional days until consistency is met").
- **U-16. Pro's funded floor before the first payout** (`mffu.pro50k.funded_drawdown_lock`, unverified) -- both ends:
  strict, it trails without a lock until the first payout and is then set to the lock level; lenient, it trails and
  locks at that level.
- **U-17. Pro's buffer** (`mffu.pro50k.payout_buffer`, unverified) -- both ends: strict, no request before the buffer is
  cleared; lenient, a request inside the buffer at the share the record's note quotes.
- **U-18. Builder's first-cycle consistency base** (implied by an example in `mffu.builder50k.payout_gate`'s source) --
  both ends: strict, profit above the buffer (the smaller base); lenient, all profit since activation.
- **U-20. Labs #006's funded scaling thresholds** (`labs.006_50k_static.funded_position_limit`: thresholds "not
  stated") -- both ends: strict, the entry tier for the account's life (Stage 2's `entry_tier` mode); lenient, the
  standard ladder's thresholds (`funded_scaling_plan`) with the top at the Labs cap.
- **U-21. The intraday equity trail on the registered trades** (`RI`) -- U-9: bracketed between the two extremes the
  trades' own outcomes allow, as RD-01 5.4 brackets Quick Pay's peak.
- **U-22. Labs' Daily path minimum, source and timing** (`labs.010_011_50k_dpp.daily_path_min` unverified; the same-day
  draw "implied, not stated" in `daily_path_timing`) -- both ends: strict, the higher of the two minimums the record's
  note names, a request drawing at most that session's own profit above the buffer, made at the next session's close;
  lenient, the lower minimum, any profit above the buffer, the same close.
- **U-23. A Labs account's per-trade costs** -- Topstep's schedule (4.5), labelled.
- **U-24. A Labs purchase limit** (`labs.006_50k_static.purchase_limit`, `labs.010_011_50k_dpp.purchase_limit`, both
  unverified) -- both ends: strict, the limit in total (the product table's), never refreshed; lenient, the same limit
  each calendar month (the FAQ's), 21 sessions in the gate. Part F and 9.5's arithmetic only.
- **U-25. The request where the plan states no per-request cap** (`mffu.rapideod50k.payout_request_amount` unstated,
  `mffu.rapid50k.payout_cap` unstated, `mffu.pro50k.payout_cap` unverified; the lead's ruling on the red team's B2) --
  both ends, both read, no free choice:
  - **strict:** the reference amount the record holds -- `min(payout_max_frac_of_balance x B, xfa_std_cap)` from Stage
    2's verified ledger, the amount RD-01 2.3 requests -- cut to the plan's buffer and increment, none below its
    minimum; were either Stage 2 key not verified at the run, the plan's smallest stated payout figure (its
    `payout_min`) instead;
  - **lenient:** the whole withdrawable balance above the plan's floor-safe level -- `B` less the balance the plan
    requires to remain after a request (its buffer, at the corner's U-17 reading at `PRO`) -- none below its minimum;
  - **`b*`, the flip's funded target, at each end:** the smallest balance above start at which that end's first request
    reaches `xfa_std_cap` (or the plan's own cap where it is lower and verified). At the strict end that is where the
    share and the buffer both allow the cap; at the lenient end where the excess above the floor-safe level equals it.
    Both are finite, computed by step 0, never chosen.
  - It applies to the coin's request (9.2) at `RE`, `RED`, `RI` and `PRO`; part F's request (2.8) is the strict end
    already and lies inside both readings, so U-7 makes it moot there (checked).
- **U-26. Pro's funded cap counting** (`mffu.pro50k.funded_position_limit`: how a micro counts "not stated in words") --
  both ends: strict, a micro counts as a mini (the plan-data reading: that many contracts of either kind); lenient,
  micros at the evaluation's counting. Costed coin and part F only (the gross coin has no contracts).
- **U-27. Builder's evaluation breach basis** (`mffu.builder50k.eval_drawdown_breach_basis`, unverified) -- both ends:
  strict, an intraday breach on open equity (the engine's barrier); lenient, a check at the day's end only (on the coin:
  the trade runs to its stop or target, and the account fails if its close is at or below the floor).
- **U-28. Builder's daily loss limit** (`mffu.builder50k.daily_loss_limit`, unverified) -- both ends: strict, the plan
  article's soft limit applies, in both modes; lenient, none.
- **U-29. Rapid's funded lock timing** (`mffu.rapid50k.funded_drawdown_lock`, unverified) -- both ends: strict, the
  floor locks only at the first payout; lenient, on reaching the lock level.
- **U-30. Rapid's funded allowance** (`mffu.rapid50k.funded_position_limit`, unverified) -- both ends: strict, the
  scaling example's starting allowance for the account's life; lenient, the evaluation's stated cap. Costed coin and
  part F only.
- **U-31. Rapid EOD's funded news rule** (`mffu.rapideod50k.funded_news`, unverified; the lead's ruling on the red
  team's S-2) -- U-6's two ends: strict, `mffu.news_tier1_rule` reaches `RE`'s and `RED`'s funded accounts (A-18
  applies there); lenient, it does not. Part F only (the coin has no calendar).
- **U-32. My Funded Futures' per-plan commission** (`mffu.<plan>.commissions`, unverified, value null, for all five
  plans; the lead's ruling on Q-136b) -- both ends: strict, the firm-wide `mffu.commissions` figures (verified, naming no
  plan or account type) on every fill, evaluation and funded; lenient, the engine's own commission, as on the registered
  trades (Topstep's schedule, 4.5). The figures come from the key, never typed. Costed coin and part F only. It replaces
  RD-01's U-12 at My Funded Futures.

**Where a U-rule's figure lives** (the red team's S-3). A U-rule end that needs a figure the record holds only in an
unverified entry's `quote` reads it from that quote by A-19's declared parser, fail-loud; the loader's refusal (17.2)
is a refusal to load a non-verified `value` as a field, not to parse a recorded quote for a declared end. Every figure
U-16, U-17, U-22, U-24, U-28, U-29 and U-30 need is in its entry's quote at 205fc42; a figure in no quote would be a pin
blocker (none).

(There is no U-19: the first text's single-day ceiling reading is withdrawn. The ceiling is now verified at `RE`, `RED`
and `RI` and modelled as a rule (A-11); elsewhere it is unstated and nothing applies.)

**The strict and lenient corners** (RD-01 5.1, carried). A configuration-mode's **strict corner** has every two-ended
term at its strict end at once, its **lenient corner** every one at its lenient end. The corners are bounds only for the
terms that move cash alone on the same path; for the others they are the two declared corners, not bounds. **Prices,
fees and lags never add a run**: they move only cash (the replay's bankroll unbound; the coin's attempts independent),
so both ends are exact arithmetic on the same runs (RD-01's A-10).

### 5.2 Every such term, at Q-136's statuses (205fc42), and what it adds

| plan | mode | term (key) | status at 205fc42 | rule | coin corner? | part-F corner? |
|---|---|---|---|---|---|---|
| `L6` | F | `labs.006_50k_static.funded_payout_terms_other` | unstated | U-13 | -- | -- |
| `L6` | F | `labs.006_50k_static.funded_position_limit` (thresholds) | verified, thresholds not stated | U-20 | costed coin only (the gross has no ladder) | yes |
| `L6` | E | `labs.006_50k_static.purchase_limit` | unverified | U-24 | -- | yes |
| `L10` | E | `labs.010_50k_dpp_eod.eval_fee` | unverified | U-2 | -- (arithmetic) | -- |
| `L10`, `L11` | E | `labs.010_011_50k_dpp.purchase_limit` | unverified | U-24 | -- | yes (both paths) |
| `L10`, `L11` | F, `day` | `labs.010_011_50k_dpp.daily_path_min`; `daily_path_timing` | unverified; verified with an implied reach | U-22 | yes | yes |
| `L10`, `L11` | both | `labs.010_011_50k_dpp.tier1_news_cap` | unstated | 4.7 item 3 (the Combine's own rows apply; moot under the designs' entry rules, checked) | -- | -- |
| `RE`, `RED`, `RI`, `PRO` | E | `mffu.eval_consistency_base` | unverified | U-15 | yes | yes |
| `RE` ... `B15` | E | `mffu.rapideod50k.eval_fee`, `mffu.rapid50k.eval_fee`, `mffu.pro50k.eval_fee`, `mffu.pro50k_oneday.eval_fee` | unverified | U-2 | -- (arithmetic) | -- |
| `RE` ... `B15` | -- | `mffu.reset_fee` | unverified | U-7 (no reset bought) | -- | -- |
| `RE`, `RED`, `RI`, `PRO` | F | the request (U-25's keys) | unstated / unverified | U-25 | yes | -- (moot, checked) |
| `RI` | F | `mffu.rapid50k.funded_drawdown_lock` | unverified | U-29 | yes | yes |
| `RI` | F | `mffu.rapid50k.funded_position_limit` | unverified | U-30 | costed coin only | yes |
| `RI` | F | `mffu.rapid50k.funded_drawdown` (intraday on equity) | verified; the trades lack the peak | U-21 (exact on the coin, 9.2) | -- | yes |
| `PRO` | F | `mffu.pro50k.funded_drawdown_lock` | unverified | U-16 | yes | yes |
| `PRO` | F | `mffu.pro50k.payout_buffer` | unverified | U-17 | yes | yes |
| `PRO` | F | `mffu.pro50k.funded_position_limit` (counting) | verified, counting not stated | U-26 | costed coin only | yes |
| `B20`, `B15` | E | `mffu.builder50k.eval_drawdown_breach_basis` | unverified | U-27 | yes | yes |
| `B20`, `B15` | both | `mffu.builder50k.daily_loss_limit` | unverified | U-28 | yes | yes |
| `B20`, `B15` | F | the first cycle's base (`mffu.builder50k.payout_gate`) | verified; base implied | U-18 | yes | yes |
| `RE`, `RED`, `B20`, `B15` | F | `mffu.hold_queue_behaviour` | unstated | U-14 | -- | yes |
| `RE` ... `B15` | F | `mffu.payout_fee` | unstated | U-3 | -- | -- |
| `RE` ... `B15` | F | `mffu.payout_processing_time` | unverified | U-5 | -- | yes (cash timing; same corners) |
| `RE` ... `B15` | -- | `mffu.copy_trading_own_accounts`, `mffu.news_all_releases_protocol` | unverified | U-7 (one position at a time copies nothing); G-2 | -- | -- |
| `RI` | F | `mffu.rapid50k.payout_gate` (profit since the last payout "not stated") | verified | U-10 (none invented) | -- | -- |
| `LU50` | F | the live move's reach | verified; reach a reading | U-6 (RD-01's ends) | -- | yes |
| `LU40`, `LU50` | F | funded fee, payout fee | unverified (vendored ledger) | U-3 | -- | -- |
| `RE` ... `B15` | both | `mffu.<plan>.commissions` (Q-136b); `mffu.commissions` | unverified; verified, firm-wide | U-32 | costed coin only | yes |
| `RE`, `RED`, `RI` | F | `mffu.rapideod50k.funded_single_day_profit_ceiling`, `mffu.rapid50k.funded_single_day_profit_ceiling` (Q-136b) | verified | a rule (A-11) | -- | -- |
| `PRO`, `PRO1`, `B20`, `B15` | both | their `*_single_day_profit_ceiling` keys; every evaluation's (Q-136b) | unstated | none applies (U-10) | -- | -- |
| `RE`, `RED` | F | `mffu.rapideod50k.funded_news` | unverified | U-31 | -- | yes |
| `RE` ... `B15` | -- | `mffu.one_time_cutover_date` | unverified | U-7 (moot for a new purchase, as its note says) | -- | -- |

The coin's mode-corners follow (Appendix M): every mode with a two-ended coin term has a strict and a lenient corner;
the rest one. A term marked "costed coin only" acts on the costed cells alone: at a mode that has another two-ended coin
term it sits at that mode's two corners; at a mode where it is the only one (`L6`'s two funded modes by U-20; `PRO1`'s
evaluation by U-32) it makes the two corners itself, and **their gross cells are identical by construction, so they are
run once, at the strict corner, and shared** (the red team's N-4): the lenient corner of such a mode has costed cells
only, and its oracle checks are counted once.

## 6. Data, blocks, the unit and the seal

1. **Parts A, B and E's arithmetic read the rules record only.** No bar, no trade, no result file.
2. **Part C reads nothing but its seeds**: the coin is synthetic. Its runs are heavy by compute, not by data (18).
3. **Part F's unit** is U1's: one development start day, a fresh unbound bankroll and fresh accounts, the design's
   trades replayed in historical order for up to 252 sessions plus U1's exact-length runs
   (`vendor/stage2/scripts/user_journey.py`), through RD-01's runner (`extended/firms.py` `run_plan`) with A-14's
   contracts. A month is 21 sessions; `USER_MILESTONES.md`'s definitions unchanged. The arms: `verdict` the headline,
   `point` beside; the bound was estimated on the whole development window, so an early-block reading on the verdict arm
   is a function of 2024-2026 through that one constant. Pairing: every plan and `TS` on the same starts, blocks and
   seeds; every `flip` cell and its `steady` cell likewise. **The blocks, per measure** (RD-03 section 5's table of
   horizons, carried): all starts with h sessions left (the headline), the early block and the late block from
   2024-01-02, by `u_select.block`; nothing chosen on any block.
4. **No NQ from 2026-07-17** is on disk or read.
5. **The judged block's seal (E-026, E-041).** Part F's replays and gates read the bars inside Stage 2's engine, so the
   runner authorises those reads with `extended.reader.authorise_engine_read` before the engine runs, from a clean
   checkout of a committed commit, under the purposes on this line:

   - **Judged-block reads:** `modes_scorecard`, `modes_ladder_beside`, `modes_gate_beside`

   - `modes_scorecard`: part F's replays at 0 % denial with the placement off -- the references, every steady corner
     and every flip cell, both arms;
   - `modes_ladder_beside`: the denial ladder and the placement beside (12.3);
   - `modes_gate_beside`: the gates beside (12.3).

   None is a choosing or fitting purpose (T-0). The identities run from `identity/*.py` under the purpose `identity` and
   their own row, never under this line (13.1). Parts A to E read no bar and need no purpose. **Once per purpose**: a
   restart, a rerun after a fix, or the failure protocol's replication is a further judged read under `repeat=` (E-053).

## 7. Part A: flip days from the rules alone (step 0)

**Computed, per configuration and mode, by code from the record (17.2), never typed:**

1. **The fewest trading days to a pass**, `k_E`: the least `n` such that `n` winning sessions can meet every pass
   condition at once -- the target; the consistency share `c` (so `n >= ceil(1/c)` with equal days, and no smaller `n`
   meets it); the minimum trading days; a lifespan. Under **both** consistency semantics: the plan's recorded one
   (`extends`, or `fails`), and the other, labelled "if the rule failed instead" or "if it extended instead".
2. **The fewest further days after a first day of profit X**, for X at `c x T`, at `0.75 T`, at `T` and at `1.5 T`:
   under `extends`, the raised target `X / c` and the further days, none larger than X; under `fails`, whether the
   account survives.
3. **`k_F`, the sessions elapsed to the first eligible close when trading every session** (2.6), and beside it the
   fewest trading days with a profit: winning days and their minimum, the cycle's share and days, the buffer and
   minimum, the clock (calendar days translated to sessions by 2.6's rounding where the record states calendar days), the profit
   since the last request -- under both semantics of a funded consistency rule, and at both ends of every two-ended
   term of the funded mode.
4. **`b*`** at each end of U-25 where it applies, and otherwise the smallest balance above start at which the plan's own
   request reaches its largest value; at every plan, finite.
5. **The single-day bounds:** whether a recorded rule caps a day's profit or loss, and the largest winning day that
   keeps a pass in `k_E` days.
6. **`r_flip`** for every mode, corner and `w`, whether the room or the daily limit cuts it at the mode's start state,
   and for `RI`'s funded mode whether `(w + 1) r_flip` lies within the read set (9.1).
7. **The minimum days implied** (the red team's N5): per evaluation mode, whether `ceil(1/c)` is at least the plan's
   minimum trading days, so that A-2 cannot bind on the coin.
8. **The boundary cells** of 9.6: the gross evaluation cells at which every pass ends at exactly `T` and every failure at
   exactly `-D` (a static floor checked intraday; the daily limit at least `r`; `r` dividing the drawdown and `w r`
   dividing the target; no consistency raise possible, `w r <= c T`; no minimum days beyond the share's) -- listed, so
   9.6 tests them by their boundary quantity. **The lifespan is read from the record** (`labs.*.eval_lifespan_days`,
   translated by 2.6's rounding): an account it ends counts among those neither passed nor failed (9.6).
9. **The close-only corners** of 9.6: the mode-corners at which the floor is checked only at the close (at this text,
   U-27's lenient end: Appendix M rows 15 and 17, `B20`'s and `B15`'s lenient evaluation corners, which were rows 14
   and 16 before `PRO1`'s second corner was added) -- listed, so 9.6 drops the pass ceiling there.
10. **The ceiling cells:** the coin cells at which one trade's win can exceed a verified single-day ceiling's threshold
    (A-11); elsewhere the ceiling cannot bind (checked).

**The stated-fewest check (refusing).** Where the record quotes a firm's own statement of the fewest days -- Topstep's
one-day FAQ and its sentence on passing in as few days as its share allows (8284197, 8284208); LucidFlex's fewest days
at each consistency setting (the vendored ledger's `eval_min_days` note); My Funded Futures' one-day evaluations
(`mffu.builder50k.eval_min_days`, `mffu.pro50k_oneday.eval_terms`) -- the computed `k_E` must equal it. A difference
stops step 0.

**Output:** `results/modes_rules.csv`, sections `flip_days`, `stated_check`, `flip_sizes` (`k_E`, `k_F`, `b*`,
`r_flip`, the cuts, `RI`'s read set), `implied_days`, `boundary_cells`.

## 8. Part B: the sizing grid, and the size that binds (step 0)

**For every configuration, mode, corner and state** -- the evaluation's fresh state; each funded tier of the plan's
ladder (a balance band per tier, from the record); `PRO`'s funded cap at both U-26 readings; `RI`'s at both U-30
readings; `L6`'s ladder at both U-20 readings -- **every stop width `s` of the grid, every dollar risk `r`, and three
instrument mixes** (MNQ alone; NQ alone; mixed -- as many minis as fit, the rest in micros, D-324):

- **the allowance** in micro-equivalents by the plan's counting rule (the record's position entry; at `PRO` by U-26),
  and beside it Stage 2 D-117's headroom cap (`sizing.DEFAULT_HEADROOM_FRAC` of the allowance, rounded down, read from
  the module), labelled the registered designs' operating rule, not the firm's;
- **the contracts for `r` at `s`**: `n = min(floor(r / (s x tick value)), the allowance, floor(L / (s x tick value)))`,
  `L` the smaller of the room above the floor at that state and the daily limit where the plan has one;
- **D-212's consistent risk**: whether `n x s x tick value` carries at least the registered sizing rule's stand-aside
  share of `r`; **D-272's stand-aside**: a trade below that share, or below the registered rule's cost floor per
  contract -- both read from the registered rule's `stand_aside`, never typed -- is "stood aside";
- **the size-binding constraint**: whichever of the dollar risk, the allowance, the room and the daily limit gives the
  fewest contracts (ties named in that order);
- **the cost share**: the round-turn fee and the assumed slippage at `n` contracts, over the realised risk;
- **the consistency fit**: whether one winning trade at `(w, r)` exceeds the mode's consistency allowance;
- **the allowed set per mode**: the `(r, w, s, mix)` at which a trade is sizeable under D-212 and inside every limit --
  the "risk per trade, R:R and stop width allowed per mode" of the brief.

**Output:** `results/modes_rules.csv`, sections `sizing` and `allowed`. Arithmetic: it draws nothing and reads no trade.

## 9. Part C: the zero-edge map of each plan and mode (step 2)

### 9.1 The cells

For every **mode-corner** (Appendix M), every `(w, r)` of the grid:

- `steady (w, r)` and `flip (w, r)` on the **gross coin** -- 48 runs;
- `steady (w, r)` on the **costed coin** at each of 50, 100 and 150 ticks, mixed sizing -- up to 72 runs, a cell run
  only where part B finds it sizeable under D-212 at the mode's start state (the rest printed "not sizeable at s");
- **`RI`'s funded mode is read only where every trade the cell can take satisfies `(w + 1) x size <= D`** (D the funded
  drawdown amount, `mffu.rapid50k.funded_drawdown`): for `steady` the size is `r`; for `flip` it is also `r_flip` (step
  0, 7 item 6). The rest printed "not read: a trade can be stopped by the floor its own peak raised" (the red team's S2).

**Accounts per run: 50,000.** **One trade a session.** The evaluation runs to its resolution or **504 sessions**
(unresolved counted, censored); the funded account to its ending or **504 sessions** from activation (the gate's funded
horizon; censored beyond).

### 9.2 The coin, exactly

- **Gross:** the vendored `RandomDraw` through `adapter.BinaryDraw` at zero edge (`floor_mode` "truncate", `edge_mode`
  "drift", theta zero): the trade's room `c` is the smaller of the stop, the room above the floor and the day's
  remaining limit; it wins `w r` with probability `c / (c + w r)` and loses `c` otherwise. The engine applies the floor;
  the draw never does. Allowance and scaling are not applied (2.6).
- **Costed (`CostedCoinDraw`):** at each trade, **`n` is recomputed from that trade's room** (the red team's S4): the
  largest whole `n` (mixed sizing, D-324) with `n` contracts' stop-out -- the stop's dollars, the stop tick and entry
  tick of slippage, and the round-turn fee -- **within** the room and the day's remaining limit, at most part B's
  contracts for `r` at `s` and the current tier's allowance; **costs are charged inside the room**, so the vendored clamp
  never swallows them. A trade whose `n` carries less than the registered rule's stand-aside share of `r` is not taken:
  **the session is a no-trade session, counted toward inactivity** (A-3), so the costed coin can end accounts inactive
  and is not "0, checked" (G-9). The bracket is driftless at the realised risk `r' = n x s x tick value`, its target at
  `w r'`; costs are subtracted at the exit (the entry tick on every trade; the stop tick on an exit at the stop, the room
  or the daily limit). Its expected profit is minus the expected cost, exactly.
- **`RI`'s intraday equity trail, exact on the coin within its read set.** For a driftless path racing a lower exit at
  `-a` (the trade's room) against a target at `+b`, a losing trade's highest point `m` has the law
  `P(m >= x | loss) = a (b - x) / (b (a + x))` for `0 <= x < b` -- the vendored adverse-excursion law
  (`propsim.mae_survival_given_win`) with the lower exit and the target exchanged. A losing trade's peak is drawn from it
  by inverse transform on its own stream (section 15); a winning trade's peak is its target. After each trade the floor
  is the lower of the lock (U-29) and the trail from the account's equity peak, that trade's own peak included. Within
  the read set (9.1) no trade can reach a floor its own peak raised, so a peak acts only on later trades and this is the
  whole rule, exactly.
- **The request (the coin's, declared):** the plan's own maximum at every eligible close -- stage one's reference rule
  (`payout_frac` 1) -- cut to every remaining-balance rule and increment, by the plan's keys; where the plan states no
  per-request cap (`RE`, `RED`, `RI`, `PRO`), **U-25 at the corner's end**. (Part F keeps RD-01's request rule, 2.8.)
- **The request-day exclusion** (A-16) where the plan's record has it; **LucidFlex's** differences by A-17.

### 9.3 What each run measures

**Evaluation mode:** the pass probability with its exact binomial interval; the shares failed at the floor, expired,
ended inactive (gross: zero, checked; costed: counted) and unresolved at 504 (censored); sessions to a pass (mean, p10,
p50, p90, among passes); the evaluation fees per attempt at both price ends (U-1, U-2); the share of passes whose target
the consistency rule raised and the sessions it added; minimum-days waits; the **large-days count** of 10.1; the **last
gate to open** of 11; the oracles' quantities (9.6).

**Funded mode:** the probability of any payout and of a first payout within 21 and 63 sessions of activation; sessions
to the first payout (among those paid; censored mass at 504 printed as such); the mean gross payouts and the mean net to
the user; the mean number of payouts; the endings by cause; the activation fee; the large-days count; the last gate;
the oracles' quantities.

### 9.4 The fee columns

**One convention for an attempt unresolved at the horizon** (the lead's ruling on the red team's S-4), used here and in
9.5 alike: it is **censored** -- a terminal outcome of its own, neither a pass nor a failure. **Its fees are counted as
paid up to the horizon** (the subscriptions accrued to it; a one-time price once), and **the censored share is printed
beside every fee and time reading.** A user's sequence of attempts therefore ends at the first pass or the first
censored attempt.

Per attempt: the evaluation's fees at both price ends (U-1) or on U-2's grid; the activation per pass. **Over a user's
sequence** (Wald's identity over the attempts up to and including the terminal one): the fees per user, the mean fees
per attempt over the sum of the pass and censored probabilities; the chance the sequence ends in a pass, the pass
probability over that same sum; **the fees per pass**, the fees per user over that chance, labelled "per pass, the
censored share beside"; fees per first payout; the payout fees. At `TS-N` every fee re-priced on `TS-S`'s runs, exactly.

### 9.5 The two modes joined (exact arithmetic, no run; the red team's S8)

**What joins what.** Within a configuration, every evaluation cell is joined with every funded cell of its funded mode:
gross with gross; costed with costed **at the same stop**; a single-corner mode's cells with **each** corner of the
other mode's (so a two-corner pair joins strict with strict and lenient with lenient, and a single corner with both).

- **The net per attempt** -- minus the evaluation's fees, plus the pass probability times (the funded mean net less the
  activation) -- stage one's `attempt_ev` form, reproduced to 1e-9 on the same inputs;
- **the fee cost per attempt**, and **the pass-and-payout probability per attempt**;
- **the net per funded journey** -- a user buying until a terminal attempt, then trading the funded account where it
  passed: minus the fees per user, plus the chance of a pass times (the funded mean net less the activation), with the
  censored share beside (9.4's convention);
- **under a purchase limit** (U-24): the chance of at least one pass within the limit's attempts, and the net over them;
- **the sessions from the first purchase to the first payout, as a renewal** (9.4's convention): attempts are bought one
  after another; each ends in a pass, a failure (floor, expiry, inactivity) or censoring at the horizon; **the number of
  failures before the terminal attempt is geometric with the failure probability `q_fail`**, each failure's duration
  drawn from that cell's own law of failure durations; the terminal attempt is a pass (with the pass probability over
  the pass and censored probabilities) or a censored end; after a pass, the switch's session (2.7) and the funded
  sessions to the first payout, a funded account unpaid at its horizon censored too. Its law is computed exactly by
  convolution (a geometric mixture of convolutions) on sessions 0 to 2,520 (ten years of 252); the mass beyond is printed
  as "beyond the window", **the censored mass printed as such**, never as a duration. Means by Wald's identity, exact.
  One attempt's own timeline -- 504 evaluation sessions then 504 from activation -- can reach 1,008 sessions, labelled
  (the red team's N8).
- **the stacking exposure on the coin** (4.7 item 5): the same convolution carrying a window state -- the end sessions of
  the last two failures -- gives the probability that the first payout request falls within 21 trading sessions, that
  day included, of the end of at least two failed attempts.

The joined tables are printed whole, per configuration; **no cell is marked best**; the diagonal (the same `(w, r)` in
both modes) is labelled "one policy in both modes (stage one's form)", and the four policy blocks are labelled.

### 9.6 Oracles: exact interval tests under a family-wise correction (the red team's B3, B-2 and S-1)

An output outside an oracle is an engine error, never a finding, and **stops step 2**. Every statistical oracle is an
**exact** test -- valid at its tail whatever the skew of the quantity (the lead's ruling on S-1 (c)) -- at a width
corrected for every statistical oracle check the reading makes.

- **The family-wise level** is **0.01**, split by **Bonferroni over N**, the number of statistical oracle checks of steps
  1 and 2 together (below). **N is at most 7,489**: one fairness check per coin run (5,256), one pass-ceiling check per
  evaluation run outside the close-only corners (at most 2,352 less those corners' 240 runs), one supremum check per
  `TS-S` evaluation run (120), and the one reference check of 13.1 (b); its exact value (the sizeable costed cells,
  `RI`'s read set and the boundary cells are fixed by step 0) is printed by step 0 before step 1 runs. A one-sided check
  is at level `0.01 / N`; a two-sided check puts `0.01 / (2 N)` in each tail.
- **The exact accounting identities** (no interval; to 1e-9, on every account): its final balance plus its gross
  payouts plus its forfeitures plus the costs it paid equals the sum of its trades' gross P&L; on the funded coin, its
  final balance is at least its starting floor. With the fairness check below, these carry what the first text's
  martingale and payout-bound checks carried: the mean gross payouts at most the starting distance to the floor follows
  from them and is printed, not tested again.
- **The fairness check, one per coin run** (two-sided; it replaces the normal-interval martingale checks): each trade's
  chance of reaching its target is fixed when it is entered -- `c / (c + w r)` at its room `c`, or the costed
  bracket's own race at its realised risk -- so `S`, the sum over all the run's trades of (1 if the target was reached,
  else 0, less that chance) times the trade's span (its room plus its target distance), is a martingale with increments
  bounded by the largest span `b` and predictable variance `V` (the sum of `p (1 - p)` times the span squared). **A
  breach when `|S|` exceeds the bound of Freedman's inequality at the check's level** -- `2 exp(-a^2 / (2 (V + b a / 3)))`
  equal to `0.01 / N` solved for `a`. The bound is exact for any skew and needs no normal tail. At `RI`'s funded cells
  the losing trades' peaks are checked the same way against their law (9.2), in the same check.
- **The pass ceiling** (one-sided, every evaluation run but those below): a breach when the pass probability's exact
  (Clopper-Pearson) lower limit exceeds `D / (D + T)`, D the evaluation's drawdown amount and T its base target by key.
  It holds because every failure ends at or above `-D` and every pass at or above `T`, with trailing floors, locks above
  start, consistency, minimum days, daily limits, lifespans and costs only lowering it.
  - **Dropped at the close-only corners** (7 item 9; the lead's ruling on B-2): where the floor is checked only at the
    close, a failure can close below `-D`, so the ceiling is not a bound; the fairness check and the accounting
    identities are the oracle there. **The corners where it is dropped: Appendix M rows 15 and 17** (`B20` and `B15`,
    evaluation, lenient), and no other at this text.
  - **At a boundary cell** (7 item 8) the pass-ceiling check is replaced by the **boundary quantity**
    `T 1{pass} - D 1{fail} + B 1{neither}`, its third term over every account neither passed nor failed -- expired at
    its lifespan (from the record) or unresolved at 504 -- tested **as a two-sided equality with zero at the corrected
    width**. There it equals each account's summed trade P&L (every pass at exactly `T`, every failure at exactly `-D`,
    checked as exact identities), so its test is the fairness check of that run, counted once.
- **The supremum** (one-sided, every `TS-S` evaluation run): a breach when the pass probability's exact lower limit
  exceeds the supremum over fair strategies of `vendor/stage2/vendor/propsim/optimality/results_combine_supremum.csv`,
  read from the file.
- **The other exact checks** (no interval; to 1e-9): every request within its plan's bounds and every net its split of
  it; no trade larger than its room, its daily limit or (costed) its allowance; every costed fee its schedule at its
  contracts; every forfeiture and every "moved to Live" ending at a verified ceiling (A-11); 9.5's per-attempt net
  equal to `propsim.attempt_ev` at `TS-S`.
- **Shown to work** (T-9; the lead's ruling on S-1 (a) and (c)): each oracle fires on a hand-broken engine; and a
  **seeded false-alarm test on synthetic data that knows the truth**, on the `build_toys` seed -- batteries of N checks
  drawn exactly at the null: Bernoulli pass indicators at the bound; fair trade sequences of the coin's own law; **and
  skewed mean-zero sequences shaped like the funded quantity** (a balance plus payouts, many small losses and a long right
  tail) -- show the share of batteries with any breach at most 0.01 beyond its binomial error; and a battery with one
  check **shifted by eight of its standard errors** breaches in every one of a declared number of batteries (power above
  0.999 at that shift).

## 10. Part D: flip days measured

### 10.1 The share of passes that come from one or two large days

For every evaluation pass, sort its trading days by profit, largest first, and count **`k*`, the fewest of them whose
profit sums to the base target `T`**. A pass with `k* = 1` came from one large day; `k* <= 2` from one or two. No
threshold is chosen. Printed: the distribution of `k*` (1, 2, 3, 4, 5 and more), the shares with `k* = 1` and
`k* <= 2`, and sessions to a pass by `k*`. **For every first payout** the same count against the balance at the request
(`k*_F`).

- **On a `steady` coin cell `k*` is arithmetic** (the red team's N3): every win is `w r`, so `k* = ceil(T / (w r))` on
  every pass; it is printed as such and carries no information. **On a `flip` cell** a pass's largest days are its flip
  wins, then its steady wins, so `k*` follows exactly from the two win counts A-13 keeps.
- **On the registered trades** a day's profit is the account's session P&L from the replay's records.

### 10.2 What a flip-seeking policy does, against a steady one

**On the coin:** every `flip (w, r)` against its `steady (w, r)`, paired on the same streams, per mode and corner: the
difference in pass probability, in sessions to a pass (mean, p50), in first-payout probability, in mean net per attempt
and per funded journey (9.5), with paired standard errors; the large-days shares under each; the exposures of 4.7 item
5 under each.

**On the registered trades** (P-16, each plan's strict corner, and `TS`): `flip_E` (the evaluation's flip, the funded
mode as registered) and `flip_F` (the funded mode's flip, the evaluation as registered), each against its plan's
`steady` replay on every start: the journey scorecard's paired readings (12.2) and, from the records, the pass rate per
evaluation bought, sessions to a pass, the first-payout rate per funded account, the large-days shares. **Beside them,
the shortfall** (the red team's N6): the share of flip trades whose whole-contract size (rounded down, after costs and
the registered cap) makes `k_E` wins fall short of `T` -- where it is large, a flip that "loses" says nothing about flip
days, and the row says so.

### 10.3 What is counted beside every flip cell

The flip trades cut by the room, the daily limit or the registered cap; the flip entries refused and the flip positions
flattened under 4.7 item 3, with A-18's bracket beside; the flip rows at U-25's lenient corners labelled **"`b*` at
the reference cap"** (the red team's N-5: the lenient `b*` borrows `xfa_std_cap` for a plan with no cap); and the
exposures of 4.7 item 5, the same as for every steady cell.

## 11. Part E: which constraint binds, per plan and mode

1. **The size that binds** (part B): per configuration, mode, corner, state, mix, `s` and `r`. Arithmetic.
2. **The last gate to open** (parts C and F): for every pass, the pass condition that held last -- the base target, the
   consistency-raised target, the minimum days -- and for every evaluation that did not pass, its cause (the floor; the
   lifespan; inactivity; censored); for every first payout, the payout gate that held last (winning days; the cycle's
   share; the cycle's days; the buffer and minimum; the clock; the profit since the last request), and for every funded
   account with no payout, its cause. The session each gate first held is kept by A-13, so "last" is read off counters.
3. **The reading:** the share of each last gate and each cause, per configuration, mode and corner; none singled out.

## 12. Part F: the registered trades on each plan (RD-01's form, extended)

### 12.1 The cells

| cell | configurations (corners) | stream | runs |
|---|---|---|---|
| references | `TS` (`TS-S/std`) | P-16, P-14 | 2 (identities) |
| steady corners | `LU50` (2), `L6/std` (2), `L10/day` (2), `L10/5wd` (2), `L11/day` (2), `L11/5wd` (2), `RE` (2), `RED` (2), `RI` (2), `PRO` (2), `PRO1` (2), `B20` (2), `B15` (2) -- 26 | P-16, P-14 | 52 |
| flips | `flip_E`, `flip_F` on `TS` and the 13 configurations above, each at its strict corner | P-16 | 28 |

Every configuration above has two part-F corners at Q-136's statuses (5.2's part-F column). **Not run here, and cited:**
`TS-N` on P-14 and P-16 is RD-03's `naf` cell; `LU40` is RD-01's `LU` corners; `TS-S/con` and `L6/con` are not run on
the registered trades, whose tables solve the Standard path (G-1; the coin reads them). Their rows are read from those
readings' result files when on master, labelled with their reading's id; until then the menu prints "not yet run by
RD-01 / RD-03". **Each run is both arms, every start, the long replay and U1's exact-length runs, at 0 % denial with
the placement off.**

### 12.2 What is read (RD-01 section 10, carried)

Every run and both arms (the verdict arm the headline), every block of section 6: the journey scorecard (P, S1 to S5c,
S2, S3d, S6, Q); **the guard row with every P** (E-134 (2): the mean net at months 1 to 3, the month-6 and month-12 net
with p10, p50, p90, CVaR10 at months 3, 6 and 12, the gate at the bound with its ruin probability); E-014's journey
variables; each measure as a distribution over starts; **the paired readings against `TS` by month**; for a flip cell,
the same against its plan's steady cell; what diverges; parts D's and E's readings on the replay's records; 4.7 item
5's exposures. **Beside each configuration's rows: its zero-edge map, whole** (9), and its sizing grid's rows at the
design's own stops; **no cell of the map is matched to the design**; the design's own coin twin is its gate's
zero-edge twin (12.3).

### 12.3 Beside

- **The denial ladder** (10, 25 and 50 %), verdict arm, U1's exact-length runs on every 21st start index
  (`EXACT_EVERY`): on P-16's 13 strict corners (39 replays), and on `TS-16` as three checks against Q-44's per-start
  rows (`results/user_beside_starts.csv`, start for start, every column, as text; E-098 (R4)). The draws are Q-17's
  (`lockstep.child_seed(20261920, 0, start_day)` as `run_starts` draws them), common to every cell. **This is tier 3's
  price** (4.7 item 4).
- **The placement on** (`rtp`, tier 2) on `TS`'s two flip cells (2 replays) and `TS-16` as one check against Q-44; not
  run at Labs (the program's application to Labs accounts is unread: the gap named) nor at other firms.
- **The gates**, one per P-16 strict corner (13), 500 paths, point and bound, with the zero-edge twin, at P-16's
  registered gate seed, through `extended/gate.py` with A-14's gate arguments; calendar rules in sessions by A-3's
  translation, labelled. The references' gates are 13.1's identities. **Nothing is a floor: nothing is carried.**
- **The Focused Trader models are not run** (G-5).

### 12.4 The mechanics, printed first (RD-01 9.3's form)

Per configuration, stream and block, before any paired outcome: the share of starts on which it differs from `TS` at
all within 63, 126 and 252 sessions; the share of trades whose contracts differ from `TS`'s and the share in each of
part B's size-binding constraints; the realised-to-intended risk (E-022 (1)); the trades stood aside (D-272); **the news
rule at work** (A-18): entries refused inside a verified window, positions flattened at a window's start with their
bracket and walked outcome beside, by account kind, stream and year, and, at Topstep and Labs accounts, the trades open
in the changed entry's windows (G-2, expected zero); **where each plan binds** (daily-limit days and signals lost to a
paused account; passes delayed by minimum days; passes waiting at a funded cap (U-14) and their waits; buffer-blocked
closes; Pro's clock waits; Builder's share-blocked closes and count endings; "moved to Live" endings at a verified
ceiling and their forfeitures; lifespan expiries; inactivity closures; purchase-limit exhaustion and the sessions after
it with no evaluation); 4.7 item 5's exposures; **the checks that must be zero** (13.1): every tier-1 count of 4.7 item
1, an entry inside a verified window among them; purchases refused for cash; trades exiting after the flatten time
(`trading_hours`); trades on a
session that closes early by E-029's calendar (`config/calendar_early_closes.csv`, LF sha256
`72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2`); resets and reactivations bought. E-050's calendar is
`config/calendar_fomc_minutes.csv`, LF sha256 `0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7`. A
configuration identical to `TS` on every start is reported "no effect on these trades".

### 12.5 The uncertainty on each paired reading (fixed now)

Descriptions, not tests. **RD-02's section 9.2, items 1 to 7, unchanged** (`extended/pp_reading.py`, imported), with
this reading's own honesty seed (section 15): every other window of h starts kept so no two share a session; the
two-sided 90 % Student t interval on the kept windows' means when at least four; the window sign count; Bartlett's
effective sample size; the minimum detectable difference printed before the mean; the honesty series' labels. **On the
coin**, every proportion carries its binomial standard error and every mean its CLT standard error; a paired
difference its paired standard error on the common streams. The menu prints the number of 90 % intervals it shows and
that a tenth would exclude zero by chance alone -- a count, not a level.

### 12.6 The menu

Per configuration: its zero-edge maps (both modes, joined), its sizing grid, its flip-day rows, its binding shares, its
registered rows with the guard row, its ladder and exposures. **The flags, mechanical, never lines:** "not stable across
blocks"; "corners straddle the reference"; "first-order, the table fixed" (G-1); "allowance and scaling not applied" on
every gross map; "no calendar: no news rule" on every coin map; "upper bound in fees" (U-3); "from the general article"
(U-13); "price unverified: on the grid" (U-2). **No cell is withheld for conduct** (4.7). **E-015's limits** flag the
menu only if approved before the run's commit by a row of the `e015-limits:` form (E-104).

## 13. Before any reading: identities, oracles, refusals

### 13.1 The identities, refusing (E-004, E-010; whole-window identities only from `identity/*.py`, E-026, E-041)

**Shared, owed by other items; this reading waits for each, re-held after Q-136's merge (4.1).** A wait is met only by a
decision row whose third cell begins with `identity-holds: <id>` (E-104's positional form), at the run's commit or an
ancestor, with the identity's cover unchanged since (`extended/identity_cover.py`): Q-05 (E-010); Q-80 (E-049); Q-93
with Q-100 (E-059 (1)); Q-101 (E-068); and **RD-01's `firms_identity`** (`identity/firms_identity.py`), since part F runs
through RD-01's runner.

**This reading's own, each from a clean checkout of the reading's commit, under the purpose `identity` and the row that
registers it:**

1. **`modes_coin_identity`** (`identity/modes_coin_identity.py`), before step 2: (a) A-0 with every addition off
   reproduces `propsim.simulate_combine` and `simulate_xfa`, every output array, bit for bit, at every `(w, r)` of the
   grid, 2,000 accounts each, on the `coin_identity` seed; (b) A-0 at `TS-S`'s terms reproduces stage one's reference
   profile -- `run_combine(Policy(rr=1.0, risk=1500.0), 0.0, 200_000, seed=2026)`, the skill's quick reference --
   against the exact value in `vendor/stage2/vendor/propsim/README.md` (`edge/combine_exact.py`), two-sided at 9.6's
   corrected width; (c) every adapter's coin form equals its account class on 1,000 scripted streams per mode-corner
   drawn on the `coin_identity` seed, account for account, every gate, ending and payout; (d) **the base coin at `TS`
   against the vendored `CombineAccount` / `FundedAccount`**, and **`LU` against `LucidFundedAccount`**, on the same
   scripted streams, every difference that is not one of the listed, known ones -- the payout timing convention, the
   engine's flatten and fills, which the binary stream does not carry -- a failure (the red team's S3).
2. **`modes_identity`** (`identity/modes_identity.py`), before step 3: through A-14 at `TS` and every adapter at its
   Topstep setting: U1's start rows for P-14 and P-16 (`vendor/stage2/results/user_journey.csv`, section `start`, both
   arms, every start, every column as E-010 compared them), and the registered gate paths (`a3_brk30_cb20_gate_paths.csv`
   at seed 20261131; `rc_s150_all_gate_paths.csv` at seed 20261206 after P-16's trades' hash), every
   `zero_edge_decomposition.PATH_COLS` column, point and bound, all 500 paths, to 1e-6; and `LU50`'s composition equal to
   the vendored joint engine's one-firm run of `lucid_setup` at `ADDON_50`, start for start, both arms (RD-01 9.1 item 3
   (b)'s form; P-16).

**The covers** (Q-111's rule, E-119): each is `BASE` (`extended/__init__.py`, the folder `config/` whole, both vendored
manifests) plus its script and its import closure (`identity_cover.imports(script)`).

**Inside the run (no further read), refusing:** `TS`'s rows equal U1's again; every trade any account takes is one of
its design's registered offered trades (Q-94's recorder); in `TS` no adapter switch fires and in each configuration no
other plan's rule fires; a flip cell equals its steady cell on every account until that account's first flip trade;
each two-ended term's corners equal each other where the term cannot bind; **every tier-1 count of 4.7 item 1 is
zero** (no entry inside a verified window; no position held through a window's start at an account a verified rule
reaches); **A-18 changes nothing at an account no verified news rule reaches**, so every `TS` trade is U1's. Any failure
stops the reading: nothing of a new cell is computed, written or printed; the failure protocol applies; a rerun is a
further judged read under `repeat=` (E-053).

### 13.2 The refusals before step 0 reads anything

The loader refuses, before any table is written: a role of Appendix R for a configuration in scope that resolves to
neither a verified entry nor a rule of section 5; a record entry not `verified` loaded as a value; a literal rule value
in the adapters (17.2); a joining firm (2.4) that fails any condition -- which holds the whole firm back and says so,
never the reading.

## 14. What the reading delivers, and what each outcome means

- **It delivers** the tables of parts A to E for every configuration and mode, the registered rows of part F with their
  readings beside, and the menu.
- **It does not deliver** a carried design, a registration id, a confirmation, a claim at a level, a bar for any family,
  or a recommendation to buy anything (E-023 (1)).
- **No outcome passes or fails.** An identity fails -- its step and every later step stop; a stated-fewest check fails --
  step 0 stops; an oracle or a tier-1 count breaches -- an engine error, its step stops; a cell identical to its
  reference -- "no effect on these trades"; corners straddling the reference -- flagged, settled only by the record,
  **never by a repeated run**.
- **The operator's choice** is recorded in its own row, citing this reading's files; it is an in-sample choice. Any
  purchase it implies is the operator's.
- **The binding (the red team's N4).** The blocks read here are recorded as read for **plan and policy choices** on P-14
  and P-16: a later reading of these plans, modes or policies names this one, states what changed, and reads no block
  of it as fresh. It does not bar a later firm-tuned family from the judged block; such a family is judged on its own
  trades, and if it uses a coin-map cell of this reading as its bar it names that cell before it reads its trades,
  never a part-F row.

## 15. Seeds, fixed now and checked

| seed | status | role | what it draws |
|---|---|---|---|
| 20262380 | in use | `coin_eval` | part C's evaluation coin streams, keyed `[20262380, w_index, r_index]` -- the same stream for **every** mode-corner, policy and stop of that `(w, r)` (S1: corners, plans, `flip` and costed cells are all paired) |
| 20262381 | in use | `coin_funded` | part C's funded coin streams, keyed the same way; independent of `coin_eval`, so 9.5's joins are exact |
| 20262382 | in use | `coin_peak` | `RI`'s losing-trade peaks (9.2), keyed `[20262382, w_index, r_index]` and, like the outcome stream, **drawn `n` per slot for every account, alive or not, winner or loser** (the red team's N-2), so `RI`'s outcome stream is every other funded mode's and `flip` and `steady` meet the same peak uniforms |
| 20262383 | in use | `build_toys` | the build's toy campaigns, scripted streams and 9.6's false-alarm batteries (T-1 to T-13) |
| 20262384 | in use | `coin_identity` | `modes_coin_identity`'s items (a), (c) and (d) |
| 20262385 | in use | `honesty` | 12.5's honesty series (keys `[20262385, 1, shape, h, n_w]`; the build's test `[20262385, 0, ...]`) |
| 20262386 | reserved, unused | -- | -- |
| 20262387 | reserved, unused | -- | -- |
| 20262388 | reserved, unused | -- | -- |
| 20262389 | reserved, unused | -- | -- |

**How a stream pairs** (S1). Account `i` of a run is column `i` of each session's draw vector over **all** accounts,
alive or not: the vendored `RandomDraw` draws `n` uniforms every slot whatever is alive, and one trade a session means
one slot. So on session `d`, account `i` meets the same uniform in every mode-corner, policy and stop of its `(w, r)`.
`w_index` and `r_index` are positions in 2.6's grid. **No key depends on a configuration's index**, so a join (2.4)
changes no stream. **Part F's replays at 0 % draw nothing.**

**The timing measurement is not on these streams** (S7). Step 2's time and memory are measured before it on a synthetic
coin drawn from `numpy.random.default_rng([0, w_index, r_index])` -- seed 0, outside the block, no meaning -- its
outputs discarded and only its time and peak memory recorded. No run on the declared streams happens before step 2.

**The check, 2026-11-18 (UTC), on the first text, repeated on this one.** Two word-bounded searches for the block's
pattern (its seven-digit prefix followed by one digit), every text file, the licensed data excluded: `git grep -IwoE`
on every local and remote ref (23 refs), the vendored snapshot and its results included; and `grep -rIownE
--exclude-dir=.git --exclude-dir=data` on the working files of the main tree, every worktree under
`%LOCALAPPDATA%\stage2-extended-wt\`, and every clean-run checkout under `%LOCALAPPDATA%\stage2-extended-runs\` and
its logs. They found the block in this file alone (and its remote copy). **T-0** (`tests/test_rd05_draft.py`) builds
the block by arithmetic, repeats the search on every run over the tracked files and the working files of its checkout,
allows only the files its `DECLARED_USES` list names (the declaration; the build adds its own files there as it writes
them, which T-13 holds to this section's uses), and **proves it works** by finding a planted copy in a temporary
repository.

**Inherited, used only as their owners registered them:** P-14's gate seed 20261131 and P-16's 20261206; Q-17's ladder
start seeds (`lockstep.child_seed(20261920, 0, start_day)`, E-024); U1's replay seeds; stage one's quick-reference seed
2026 for 13.1 (b) only.

## 16. Counting (no family number, no level; every cell counted)

1. **No program family number and no level** (E-023 (1)).
2. **Step 0** writes tables, draws nothing and runs no engine.
3. **The mode-corners** (Appendix M, at Q-136's and Q-136b's statuses): 20 evaluation and 25 funded, **45**, of which
   three (`L6/std` and `L6/con` funded, `PRO1` evaluation, lenient) share their strict corner's gross cells (5.2).
4. **The cells and runs:**

<!-- counted-cells: the rows below are summed by T-0 -->

| block | runs | basis |
|---|---|---|
| part C, gross coin | 2016 | (45 mode-corners less 3 sharing their gross cells) x 24 `(w, r)` x 2 policies, less `RI`'s funded cells outside its read set (printed at step 0) |
| part C, costed coin | 3240 | 45 x 24 x 3 stops, at most: only the cells part B finds sizeable run (printed at step 0) |
| part F, references | 2 | `TS` on P-16 and P-14 (identities) |
| part F, steady corners | 52 | 26 corners x 2 streams |
| part F, flips | 28 | 14 configurations x 2 flips, P-16 |
| beside, denial ladder | 39 | 13 strict corners x 3 levels, P-16 |
| beside, placement | 2 | `TS`'s two flips |
| beside, gates | 13 | P-16 strict corners, 500 paths, point and bound, with the zero-edge twin |
| reference checks against Q-44 | 4 | `TS-16` under the three ladder levels and the placement |
| statistical oracle checks | 7489 | 1 fairness check per coin run (5,256); 1 pass ceiling per evaluation run (2,352) less the close-only corners' 240; 1 supremum per `TS-S` evaluation run (120); 1 reference (9.6), at most |

<!-- end counted-cells -->

   That is **at most 5,256 coin runs**, **82 replays** at 0 % on both arms (2 references, 80 new), **41 replays
   beside** with 4 reference checks, **13 gates**, and **at most 7,489 statistical oracle checks**. The grid is bounded
   and kept (the lead's ruling): Q-136's record moved the corners from 42 to 44 and part F's from 24 to 26; Q-136b's
   commission rule (U-32) adds `PRO1`'s second evaluation corner (45), whose gross cells, like `L6`'s funded lenient
   corners', are shared, not re-run (N-4); the oracle checks fall with the exact fairness check and the dropped ceilings.
   A joining firm (2.4) adds, per configuration: 120 coin runs per mode-corner (72 at a corner sharing its gross cells);
   2 steady replays per part-F corner; 2 flips; 3 ladder replays; 1 gate; and the oracle checks that follow -- stated in
   the join's row before step 0.
5. **Exact arithmetic, not runs:** `TS-N`'s re-pricing; every price end and U-2's grid; 9.5's joins; part B.
6. **Every block read** is recorded as read for plan and policy choices (14). **Nothing is selected by the program.**

## 17. The build: adapters, rules in code, tests

### 17.1 The adapters

Section 4.3's A-0 to A-19, in `extended/`, never in `vendor/`.

### 17.2 The rules in code

Every value of every role is read by a loader that refuses an entry not `verified` (Stage 2's ledger through its own
loader; the vendored Lucid ledger through Stage 2's adapter; `config/rules_extended.yaml` through RD-01's
`extended/firm_terms.py`), parsing a value stated in text fail-loud. A test fails on any literal of a rule value in the
adapters outside comments. The readings of section 5 come from one table of named rules citing 5.1; **every figure a
U-rule end needs is parsed by A-19 from its named entry's recorded quote, never typed** (S-3). Stage 2's
operating constants -- D-117's headroom (`sizing.DEFAULT_HEADROOM_FRAC`) and D-212's and D-272's stand-aside share and
cost floor (the registered sizing rule's `stand_aside`) -- are read from their modules, never typed (the red team's
N10). Grid values (2.6), horizons, account counts and the oracle level come from one table citing this file.

### 17.3 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 | `tests/test_rd05_draft.py` (committed with this draft; extended at the pin): exactly one firm-modes declaration under `prereg/`; the seed block once each in section 15's table, six in use and four reserved, and in no other tracked or working file but `DECLARED_USES`; the scan's positive control (a planted copy in a temporary repository is found); one `Judged-block reads:` line, its three purposes, none choosing, none `identity` or `registered_design`; the counted-cells rows equal Appendix M's corners times the grid and section 16's totals; the two calendars' LF sha256 as 12.4 cites them (the red team's N9); the sections present. **At the pin, added:** every Appendix R key against the merged record with the status stated, section 5.2's corners recomputed from it, the covers of 13.1 |
| T-1 | A-0 with every addition off equals `propsim.simulate_combine` and `simulate_xfa` bit for bit on toy streams (`build_toys`); its guard refuses a changed vendored source; its recomposition proof |
| T-2 | every account class of 4.3 with its switches at Topstep's setting equals the vendored class on toy campaigns (RD-01's T-1 form) |
| T-3 | every adapter's coin form equals its account class on scripted streams, account for account -- daily limits soft and hard, static floors and their move at a payout, minimum days, lifespans, inactivity on the costed coin, buffers, cadences, clocks, cycle shares, counts, the contract-counted cap, the Daily path at both U-22 ends, the request-day exclusion (A-16), LucidFlex (A-17); and the base coin at `TS` against `CombineAccount` / `FundedAccount` with the known differences listed |
| T-4 | 4.6's table inputs at each new plan on toy campaigns; the held reading; the day-logging micro |
| T-5 | part A's arithmetic on hand-built rule sets with known answers, under both consistency semantics; `k_F` under a calendar clock and a trading-day clock, with 2.6's rounding up and down; `b*` at both U-25 ends; the implied-days, boundary-cell, close-only and ceiling-cell lists; the stated-fewest check firing on a hand-broken record; **A-19's parser** on each named entry's quote at 205fc42 (and a hand-broken quote refused) |
| T-6 | part B's arithmetic on hand-computed cells; the three mixes; U-26's two counts; the constants read from their modules |
| T-7 | `flip`'s schedule on the coin and on toy replays: `k` and `r_flip` from part A; one flip trade a session; the cuts; the registered cap on flip trades; a flip cell equal to its steady cell until the first flip trade |
| T-8 | the costed coin: `n` per trade from the room, costs inside the room, its mean equal to minus its mean costs; a stood-aside session counted toward inactivity; `RI`'s peak law against a fine random-walk simulation of the bracket (`build_toys`), within its interval; the read set on `r` and on `r_flip` |
| T-9 | 9.6: each oracle fires on a hand-broken engine; the false-alarm batteries at the null (Bernoulli, fair trade sequences, skewed funded-shaped sequences) within the family-wise level; a check shifted by eight standard errors breaches in every battery; Freedman's bound computed against a hand-worked case; 9.5's joins equal `propsim.attempt_ev` to 1e-9; the renewal's law, with 9.4's censoring convention, against a direct simulation of sequential attempts on toy laws; **D-145's stacking trigger** (4.7 item 5) on hand-built breach and request records -- two breaches inside the 21 sessions ending on the request day, that day included, fire; one does not; two with one on the 22nd session back do not -- and the coin's windowed renewal against a direct simulation |
| T-10 | 10.1's `k*` from A-13's counters against a sort of hand-built day records; 11's last gate on hand-built gate records |
| T-11 (`slow`, `heavy`) | 13.1's identities at 4 starts and 4 paths, and the coin identity at 200 accounts a cell (it reads the bars: E-198's marker, the red team's N7) |
| T-12 | the menu: no P without its guard row; every exposure of 4.7 item 5 printed for `flip` and `steady` alike; no cell withheld for conduct; the flags of 12.6 on synthetic menus |
| T-13 | the seeds of section 15 appear in the build's commit only where section 15 declares them (T-0's `DECLARED_USES` extended by the build); 17.2's literal check; the tier-1 counts at zero on toy runs, and each firing on a hand-broken router |

## 18. Outputs, the run, and its bounds

**Files**, each written with its sidecar manifest through `extended.results.write_result` (`prereg_id` `RD-05` and its
pinning row; the identity rows with their shas; the cell, run and oracle-check counts as run; every seed, the inherited
ones named; every parameter and every reading of section 5 with its label; the record's commit and entries with their
dates read; the sha256 of `vendor/DATA_MANIFEST_stage2.sha256` and the two calendars' LF sha256 where part F reads them;
the E-015 limits or "none approved before the run's commit"; `exploratory=False`, every row "described, not carried"):

- `results/modes_rules.csv` -- step 0: `terms`, `flip_days`, `stated_check`, `flip_sizes`, `implied_days`,
  `boundary_cells`, `sizing`, `allowed`, `size_binding`, `oracle_count`;
- `results/modes_coin.csv` -- step 2: `identity`, `oracle`, `eval`, `funded`, `fees`, `joined`, `renewal`, `flip_pairs`,
  `large_days`, `binding`, `exposure`;
- `results/modes_reading.csv` -- step 3: `identity`, `mechanics`, `scorecard`, `guard`, `paired`, `flip`, `shortfall`,
  `large_days`, `binding`, `exposure`, `coverage`;
- `results/modes_beside.csv` -- step 4: `ladder`, `rtp`, `checks`;
- `results/modes_gate.csv` -- step 5;
- `results/modes_menu.csv` -- the menu with its flags and labels.

**The run, in six steps, each from a clean checkout of a named commit (`scripts/run_clean.py`), one heavy job on the
machine under `run.lock` (skill `run-lock`), watched to its exit; each step only after the lead's row records the one
before:**

0. **The rules arithmetic** (`scripts/modes_rules.py`; no seed, no bar): 13.2's refusals first; then parts A, B and E
   (1); the stated-fewest check refusing. It fixes the costed cells, `RI`'s read set, the boundary cells and N before
   step 1.
1. **The identities**: `identity/modes_coin_identity.py` and `identity/modes_identity.py`, purpose `identity`, their
   own row. A failure of `modes_coin_identity` stops step 2; of `modes_identity`, steps 3 to 5.
2. **The coin maps** (`scripts/modes_coin.py`; no bar): `TS-S`'s evaluation mode first; then the evaluation and funded
   mode-corners in Appendix M's order; each cell's oracles checked before anything of it is written; 9.5's joins and
   renewal; parts D's and E's coin readings.
3. **The registered scorecard** (`scripts/modes_reading.py`, purpose `modes_scorecard`): `TS` on P-16 then P-14 (13.1's
   repeat); the steady corners in 12.1's order, P-16 then P-14, strict before lenient; the flips, `flip_E` before
   `flip_F`; each new cell checked under 13.1's run checks before anything of it is read; then the mechanics, the
   readings and the menu without its beside sections.
4. **Beside** (purpose `modes_ladder_beside`): `TS-16`'s four checks against Q-44 first, then the 39 ladder and 2
   placement replays.
5. **The gates** (purpose `modes_gate_beside`); then the menu's beside sections.

**On any failure, nothing more of the failed step's own run is computed, written or printed**; the failure protocol
applies.

**The bounds, every step (the red team's S12 and S-5; the lead's ruling).** The machine's limit is under 3 GB for the
one heavy job running. **Every step's memory bound is the job's summed working set** -- the parent process and every
worker together: each process reports its own peak (`extended/procmem.py`, which measures one process) and the parent
sums them -- held **under 2.5 GB**, one BLAS thread a process. **U1 replays run on one worker** (steps 1, 3, 4 and the
gates of 5), since two of E-010's recorded U1 peaks would exceed the bound; the replays are deterministic, so one worker
changes nothing but the time:

| step | weight | workers | time bound | memory bound (summed) | measured before it on |
|---|---|---|---|---|---|
| 0 | light | 1 | 1 hour | 0.5 GB | -- (arithmetic) |
| 1 | heavy | 1 | 8 hours | 2.5 GB | E-010's recorded peak for U1's identity; the coin identity on the timing seed |
| 2 | heavy | at most 2 | 12 hours | 2.5 GB | the synthetic coin on the timing seed (section 15), outputs discarded |
| 3 | heavy | 1 | 48 hours | 2.5 GB | synthetic campaigns of the window's length (E-117's form), at one worker |
| 4 | heavy | 1 | 24 hours | 2.5 GB | the same |
| 5 | heavy | 1 | 24 hours | 2.5 GB | the same |

Part C's counters are O(accounts) (A-13), never per-session arrays. **A step whose measurement exceeds its bound is not
started; a step that exceeds its bound while running is stopped**; either way the build reports, and **no grid is
thinned and no worker added at run time** -- a smaller grid is a new declaration.

**Waits, all before step 0:** Q-136 merged, then every shared identity and RD-01's `firms_identity` held at a commit
containing it (4.1), Q-136b's entries among it; the pinning row; any join row (2.4); A-0 to A-19 built with T-0 to T-13
and the red team's read of the build; **before step 4,** Q-44's file on master.

## 19. Open before the pin

**The lead's:**

1. **No pin blocker remains beyond the record's merge.** The second text's two -- My Funded Futures' commissions and
   its single-day ceiling -- are recorded by Q-136b (4.1) and read by U-32 and A-11.
2. **Q-136's and Q-136b's merge**, and T-0's pin-time mapping of every Appendix R key against the merged record: an
   entry whose status differs from 205fc42's (or from Q-136b's working-tree entries) changes 5.2, Appendix M and section
   16 by the rules already stated, before the pin; and A-19's parse of every named quote confirmed.
3. **The red team's focused re-read and the gatekeeper's**, of this text (the last corrective cycle; a blocker still
   standing goes to NEEDS_OPERATOR).
4. **Whether `TS-S/con` and `L6/con` should be read on the registered trades** (they are not, G-1), and whether Labs
   should carry the placement beside (12.3).
5. **The name at the pin:** `prereg/RD-05_firm_modes.md`, the draft renamed in the same commit, nothing else changing.

(The first text's conduct item is withdrawn: the tiers are ruled, D-145 and E-013, applied in 4.7.)

**The operator's (reads, no purchase):**

1. Settling an unverified term of section 5.2 by a browser read or a written question; until it is recorded, both ends
   run.
2. **The by-hand captures of Lucid's and Alpha Futures' terms** (`docs/OPERATOR_SETUP.md` item 11), joining only by 2.4.
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
| 4 | `RE` evaluation | strict | U-15; U-32 (costed only) |
| 5 | `RE` evaluation | lenient | U-15; U-32 (costed only) |
| 6 | `RED` evaluation | strict | U-15; U-32 (costed only) |
| 7 | `RED` evaluation | lenient | U-15; U-32 (costed only) |
| 8 | `RI` evaluation | strict | U-15; U-32 (costed only) |
| 9 | `RI` evaluation | lenient | U-15; U-32 (costed only) |
| 10 | `PRO` evaluation | strict | U-15; U-32 (costed only) |
| 11 | `PRO` evaluation | lenient | U-15; U-32 (costed only) |
| 12 | `PRO1` evaluation | strict | U-32 (costed only) |
| 13 | `PRO1` evaluation | lenient | U-32 (costed only); gross shared with the strict corner |
| 14 | `B20` evaluation | strict | U-27, U-28; U-32 (costed only) |
| 15 | `B20` evaluation | lenient | U-27, U-28; U-32 (costed only); **close-only: no pass ceiling** |
| 16 | `B15` evaluation | strict | U-27, U-28; U-32 (costed only) |
| 17 | `B15` evaluation | lenient | U-27, U-28; U-32 (costed only); **close-only: no pass ceiling** |
| 18 | `LU40` evaluation | single | -- |
| 19 | `LU50` evaluation | single | -- |
| 20 | `TS/std` funded | single | -- |
| 21 | `TS/con` funded | single | -- |
| 22 | `L6/std` funded | strict | U-20 (costed only) |
| 23 | `L6/std` funded | lenient | U-20 (costed only); gross shared with the strict corner |
| 24 | `L6/con` funded | strict | U-20 (costed only) |
| 25 | `L6/con` funded | lenient | U-20 (costed only); gross shared with the strict corner |
| 26 | `L10/day` funded | strict | U-22 |
| 27 | `L10/day` funded | lenient | U-22 |
| 28 | `L10/5wd` funded | single | -- |
| 29 | `L11/day` funded | strict | U-22 |
| 30 | `L11/day` funded | lenient | U-22 |
| 31 | `L11/5wd` funded | single | -- |
| 32 | `RE` funded | strict | U-25; U-32 (costed only) |
| 33 | `RE` funded | lenient | U-25; U-32 (costed only) |
| 34 | `RED` funded | strict | U-25; U-32 (costed only) |
| 35 | `RED` funded | lenient | U-25; U-32 (costed only) |
| 36 | `RI` funded | strict | U-25, U-29; U-30 (costed only); U-32 (costed only) |
| 37 | `RI` funded | lenient | U-25, U-29; U-30 (costed only); U-32 (costed only) |
| 38 | `PRO` funded | strict | U-16, U-17, U-25; U-26 (costed only); U-32 (costed only) |
| 39 | `PRO` funded | lenient | U-16, U-17, U-25; U-26 (costed only); U-32 (costed only) |
| 40 | `B20` funded | strict | U-18, U-28; U-32 (costed only) |
| 41 | `B20` funded | lenient | U-18, U-28; U-32 (costed only) |
| 42 | `B15` funded | strict | U-18, U-28; U-32 (costed only) |
| 43 | `B15` funded | lenient | U-18, U-28; U-32 (costed only) |
| 44 | `LU` funded | single | -- |

**Gross cells shared** (the red team's N-4): at the three lenient corners marked so (rows 13, 23 and 25), the only
two-ended term acts on the costed cells alone, so the gross cells are identical to the strict corner's by construction;
they are run once, at the strict corner, shared, and their oracle checks counted once. **Close-only corners** (the
lead's ruling on B-2): rows 15 and 17 -- rows 14 and 16 in the second text, before `PRO1`'s second corner (U-32) was
added -- carry no pass-ceiling check (9.6). The index fixes run order only; no seed key uses it.

## Appendix R -- the term roles each configuration leans on, with their keys at Q-136's commit 205fc42

Sources: `stage2` is `vendor/stage2/config/rules.yaml`; `lucid` the vendored Lucid ledger through Stage 2's adapter;
`record` this repository's `config/rules_extended.yaml` at 205fc42 (Q-115's keys included). Status as recorded there;
"--" a role the plan does not have. T-0 checks every key against the merged record at the pin.

| role | `TS` (`TS-N`) | Labs | My Funded Futures | Lucid |
|---|---|---|---|---|
| evaluation target | `combine_profit_target` (stage2, verified) | `labs.006_50k_static.eval_profit_target`, `labs.010_50k_dpp_eod.eval_profit_target`, `labs.011_50k_dpp_static.eval_profit_target` (verified) | `mffu.rapideod50k.eval_profit_target`, `mffu.rapid50k.eval_profit_target`, `mffu.pro50k.eval_profit_target`, `mffu.builder50k.eval_profit_target`, `mffu.pro50k_oneday.eval_terms` (verified) | `eval_profit_target` (lucid) |
| evaluation drawdown, type, lock | `combine_mll`, `combine_mll_lock_at` (stage2) | `labs.006_50k_static.eval_mll`, `labs.010_50k_dpp_eod.eval_mll`, `labs.011_50k_dpp_static.eval_mll` (verified) | `mffu.rapideod50k.eval_drawdown`, `mffu.rapid50k.eval_drawdown`, `mffu.pro50k.eval_drawdown`, `mffu.builder50k.eval_drawdown`, `mffu.eval_drawdown_lock`, `mffu.eval_drawdown_open_equity` (verified); `mffu.builder50k.eval_drawdown_breach_basis` (unverified, U-27) | `eval_drawdown_amount`, `eval_drawdown_type`, `eval_drawdown_lock` |
| evaluation daily loss limit | -- | `labs.006_50k_static.eval_daily_loss_limit`, `labs.010_011_50k_dpp.eval_daily_loss_limit` (verified; softness U-13) | `mffu.rapideod50k.eval_daily_loss_limit` (verified; `RED` its DLL version), `mffu.pro50k.eval_daily_loss_limit`, `mffu.rapid50k.daily_loss_limit` (verified); `mffu.builder50k.daily_loss_limit` (unverified, U-28) | `eval_daily_loss_limit` (off) |
| evaluation consistency, breach, base | `combine_consistency_max_day_frac` (stage2) | `labs.006_50k_static.eval_consistency`, `labs.010_011_50k_dpp.eval_consistency` (verified) | `mffu.rapideod50k.eval_consistency`, `mffu.rapid50k.eval_consistency`, `mffu.pro50k.eval_consistency`, `mffu.builder50k.eval_consistency`, `mffu.eval_consistency_breach` (verified); `mffu.eval_consistency_base` (unverified, U-15) | `eval_consistency_rule` |
| evaluation minimum days | `combine_min_trading_days` (stage2) | -- (none stated) | `mffu.rapideod50k.eval_min_days`, `mffu.rapid50k.eval_min_days`, `mffu.pro50k.eval_min_days`, `mffu.builder50k.eval_min_days` (verified) | `eval_min_days` |
| evaluation position cap, counting | `combine_position_size_limit` (stage2) | `labs.006_50k_static.eval_position_limit`, `labs.010_011_50k_dpp.eval_position_limit` (verified) | `mffu.rapideod50k.eval_position_limit`, `mffu.rapid50k.eval_position_limit`, `mffu.pro50k.eval_position_limit`, `mffu.builder50k.position_limit` (verified) | `eval_position_limit` |
| evaluation lifespan, inactivity | -- | `labs.006_50k_static.eval_lifespan_days`, `labs.006_50k_static.eval_inactivity_days`, `labs.010_011_50k_dpp.eval_lifespan_days`, `labs.010_011_50k_dpp.eval_inactivity_days` (verified) | `mffu.inactivity_rule` (verified) | `eval_time_limit` |
| evaluation price, billing, reset | `subscription_fee`, `billing_days`, `billing_period_calendar_days` (stage2); `subscription_fee_naf_50k` (record, verified) | `labs.006_50k_static.eval_fee`, `labs.011_50k_dpp_static.eval_fee` (verified); `labs.010_50k_dpp_eod.eval_fee` (unverified, U-2); `labs.006_50k_static.eval_reset` (verified) | `mffu.builder50k.eval_fee`, `mffu.billing_basis` (verified); `mffu.rapideod50k.eval_fee`, `mffu.rapid50k.eval_fee`, `mffu.pro50k.eval_fee`, `mffu.pro50k_oneday.eval_fee`, `mffu.reset_fee` (unverified, U-2, U-7) | `eval_fee`, `eval_reset_fee` |
| purchase limit, evaluations held | `combine_count_limit` (stage2) | `labs.006_50k_static.purchase_limit`, `labs.010_011_50k_dpp.purchase_limit` (unverified, U-24) | `mffu.max_eval_accounts` (verified) | `eval_count_limit` |
| activation, the switch | `activation_fee`, `xfa_activation_latency` (stage2); `activation_fee_naf_50k` (record) | `labs.006_50k_static.activation_fee`, `labs.010_011_50k_dpp.activation_fee` (verified) | `mffu.activation_fee` (verified) | adapter |
| funded floor start, type, lock, move at a payout | `xfa_mll_start`, `xfa_lock_at` (stage2) | `labs.006_50k_static.funded_mll`, `labs.010_50k_dpp_eod.funded_mll`, `labs.011_50k_dpp_static.funded_mll`, `labs.010_011_50k_dpp.daily_path_mll_effect` (verified) | `mffu.rapideod50k.funded_drawdown`, `mffu.rapideod50k.funded_drawdown_lock`, `mffu.rapid50k.funded_drawdown`, `mffu.pro50k.funded_drawdown`, `mffu.builder50k.funded_drawdown` (verified); `mffu.rapid50k.funded_drawdown_lock` (U-29), `mffu.pro50k.funded_drawdown_lock` (U-16) (unverified) | `funded_drawdown_amount`, `funded_drawdown_type`, `payout_balance_consequence` |
| funded daily loss limit | -- | `labs.006_50k_static.funded_daily_loss_limit`, `labs.010_011_50k_dpp.funded_daily_loss_limit` (verified) | `mffu.rapideod50k.funded_daily_loss_limit`, `mffu.pro50k.funded_daily_loss_limit`, `mffu.rapid50k.daily_loss_limit` (verified); `mffu.builder50k.daily_loss_limit` (U-28) | `funded_daily_loss_limit` (off) |
| funded consistency, payout path | `xfa_payout_path_choice` (stage2) | `labs.006_50k_static.funded_payout_path`, `labs.010_011_50k_dpp.funded_consistency`, `labs.010_011_50k_dpp.payout_path_choice` (verified) | `mffu.rapideod50k.funded_consistency`, `mffu.rapid50k.funded_consistency`, `mffu.pro50k.funded_consistency`, `mffu.builder50k.funded_consistency` (verified) | `funded_consistency_rule` |
| payout gate | `xfa_std_winning_days`, `xfa_std_winning_day_min`, `require_profit_since_payout` (stage2) | `labs.006_50k_static.funded_payout_terms_other` (unstated, U-13); `labs.010_011_50k_dpp.daily_path_gate`, `labs.010_011_50k_dpp.wd5_path_gate`, `labs.010_011_50k_dpp.payout_resets_wd5_count`, `labs.010_011_50k_dpp.daily_path_timing` (verified) | `mffu.rapideod50k.payout_gate`, `mffu.rapid50k.payout_gate`, `mffu.pro50k.payout_timing`, `mffu.builder50k.payout_gate` (verified); `mffu.pro50k.payout_buffer` (unverified, U-17) | `payout_frequency_gate` |
| request size, cap, minimum, split | `payout_max_frac_of_balance`, `xfa_std_cap`, `payout_min`, `profit_split` (stage2) | `labs.006_50k_static.funded_payout_cap`, `labs.010_011_50k_dpp.daily_path_max`, `labs.010_011_50k_dpp.wd5_path_amount`, `labs.010_50k_dpp_eod.wd5_path_cap`, `labs.011_50k_dpp_static.wd5_path_cap`, `labs.010_011_50k_dpp.payout_split` (verified); `labs.010_011_50k_dpp.daily_path_min` (unverified, U-22) | `mffu.rapideod50k.payout_cap`, `mffu.rapideod50k.payout_min`, `mffu.rapideod50k.payout_split`, `mffu.rapid50k.payout_min`, `mffu.rapid50k.payout_split`, `mffu.pro50k.payout_min`, `mffu.pro50k.payout_split`, `mffu.builder50k.payout_cap`, `mffu.builder50k.payout_min`, `mffu.builder50k.payout_split` (verified); `mffu.rapideod50k.payout_request_amount`, `mffu.rapid50k.payout_cap` (unstated), `mffu.pro50k.payout_cap` (unverified) (U-25) | `payout_cap`, `payout_min`, `payout_split` |
| an end by count; live | -- | -- | `mffu.builder50k.max_sim_payouts` (verified); `mffu.builder50k.live_trigger` (unverified, moot beside the verified count); `mffu.pro50k.live_review_triggers` (verified, G-4) | `max_accounts` |
| funded allowance, scaling | `funded_scaling_plan`, `scaling_tier_after_payout` (stage2) | `labs.006_50k_static.funded_position_limit` (U-20), `labs.010_011_50k_dpp.funded_position_limit` (verified) | `mffu.rapideod50k.funded_position_limit`, `mffu.builder50k.position_limit` (verified); `mffu.pro50k.funded_position_limit` (U-26); `mffu.rapid50k.funded_position_limit` (unverified, U-30) | `funded_position_limit` |
| seats, the hold | `max_active_funded_accounts`, `hold_queue_behaviour` (stage2) | `labs.006_50k_static.funded_seats`, `labs.010_011_50k_dpp.funded_seats` (verified) | `mffu.max_funded_accounts` (verified), `mffu.builder50k.funded_seats` (verified); `mffu.hold_queue_behaviour` (unstated, U-14) | `max_accounts` |
| fees after funding, payout fee, lag | `payout_fee`, `payout_lag_days_aeropay` (stage2) | general (U-13) | `mffu.payout_fee` (unstated, U-3), `mffu.payout_processing_time` (unverified, U-5) | `funded_monthly_fee`, `payout_fee`, `payout_processing_days` |
| commissions | `fills.yaml` (8284213) | U-23 | `mffu.commissions` (verified, firm-wide); `mffu.rapideod50k.commissions`, `mffu.rapid50k.commissions`, `mffu.pro50k.commissions`, `mffu.pro50k_oneday.commissions`, `mffu.builder50k.commissions` (unverified) -- U-32 (Q-136b) | `fills.yaml` (D-575) |
| single-day profit ceiling | -- | -- | `mffu.rapideod50k.funded_single_day_profit_ceiling`, `mffu.rapid50k.funded_single_day_profit_ceiling` (verified, A-11); the other eight `*_single_day_profit_ceiling` keys (unstated) (Q-136b) | -- |
| news (funded) | -- (U1's own rule) | -- (the Combine's rows are in the changed entry) | `mffu.rapid50k.funded_news`, `mffu.pro50k.funded_news` (verified); `mffu.rapideod50k.funded_news` (unverified, U-31); `mffu.builder50k.news` (verified, unrestricted) | `news_trading_terms` (lucid) |
| conduct, tier 1 (mechanical) | `cross_account_opposite_positions` (stage2); `tier1_news_events_restriction` (record; status `changed`, not loaded, 4.7 item 1) | `labs.50k_static.tier1_news_cap` (verified); `labs.010_011_50k_dpp.tier1_news_cap` (unstated) | `mffu.news_tier1_rule`, `mffu.hedging_rule`, `mffu.coordinated_trading_rule` (verified); `mffu.automation_and_sim_fills` (verified; unsized, 4.7 item 6) | `prohibited_conduct` |
| conduct, tier 2 | `responsible_trading_program` (stage2) | the same (unapplied, 12.3) | -- | -- |
| conduct, tier 3 | `prohibited_trading_strategies`, `prohibited_conduct` (stage2); `tou_s8_relative_position_size` (record) | the same | `mffu.pro50k.funded_conduct_policy` (verified) | -- |

---

## Appendix A -- the red team's findings (Q-137r) and where each is answered

| finding | what it found | the answer (the lead's ruling where one is named) | where |
|---|---|---|---|
| **B1** | the "N" class was not mechanical, contradicted D-145 and E-013, and could change after the run | dropped; D-145's tiers carried; tier 1 enforced at zero, tier 2 modelled, tier 3 priced; exposures printed alike for every cell; labels computed by the run and frozen at its commit; no cell withheld | 4.7; 12.6; 13.1; 19; T-12 |
| **B2** | `b*` and the coin's request undefined at four funded modes; `k_F` ambiguous under a clock | U-25 with its two ends and `b*` at each; `k_F` the sessions elapsed to the first eligible close, a calendar clock counted in calendar time | 2.6; 5.1 U-25; 7 items 3-4; 9.2; Appendix M |
| **B3** | the oracles stopped a correct engine by chance | interval tests at a family-wise 0.01, Bonferroni over N printed at step 0; boundary cells as two-sided equalities; the supremum with an interval; a seeded false-alarm test | 7 item 8; 9.6; 16; T-9 |
| S1 | streams keyed by corner were not paired | keyed by `(w, r)` only: every plan, corner, policy and stop paired; the column rule stated | 15 |
| S2 | `RI`'s funded flip cells outside the exact set | the read set applied to `r_flip` too | 7 item 6; 9.1 |
| S3 | no request-day exclusion, no contracts on the gross coin, no Lucid coin form, no base comparison | A-16; A-17; the gross labelled "allowance and scaling not applied"; 13.1 (1)(d) and T-3 | 2.6; 4.2; 4.3; 13.1; T-3 |
| S4 | the costed coin's sizing during a run undefined; inactivity claim false; costs at the floor | `n` per trade from the room; costs inside the room; a stood-aside session counts toward inactivity; G-9 restated | 9.2; G-9; T-8 |
| S5 | Q-136's record differs | Appendix R filled from 205fc42; 5.2 rebuilt; corners 42 to 44, part F 24 to 26; two pin blockers | 4.1; 5.2; 16; 19; Appendix M, R |
| S6 | the join rule contradicted itself and could be steered | one rule, the whole firm; the capture's enumeration; an unrecorded price blocks; LucidFlex stays on the vendored record; joiners appended in the record's order; no stream depends on the index | 2.4; 13.2; 15 |
| S7 | the seed scan had no positive control and would fail the build; the timing was a look | `DECLARED_USES`, the working-file scan and a planted positive control in T-0; timing on seed 0 outside the block, outputs discarded | 15; 18; T-0 |
| S8 | the join's timing and pairing under-specified | the renewal declared; censored mass printed; gross with gross, costed with costed at the same stop; single corners with each corner | 9.5; T-9 |
| S9 | a tier-1 act only counted | every trade follows the news rule (stand aside); flip trades never above the registered cap, never at the full allowance; tier-1 counts at zero, a breach an engine error | 2.6; 4.7 items 1, 3; 13.1 |
| S10 | "adds and removes no offered trade" overstated the registered flip | the executed set changes, said; E-134 (1) cited | header; 0 |
| S11 | rule values typed | removed; keys cited throughout; the release window derived from the record and E-050's calendar | throughout; 4.7 item 3; Appendix R |
| S12 | run time and memory partly bounded | a time and memory bound for every step under 2.5 GB; counters O(accounts) | 4.3 A-13; 18 |
| N1 | `b*` cited 9.3 | references corrected (9.2, U-25) | 2.6; 7 |
| N2 | the base lacked E-197 and the firm notes | master merged at 2dd81fd | status line |
| N3 | `k*` on the steady coin is arithmetic | said, and printed as such | 10.1 |
| N4 | the binding too wide; a later family's bar unconstrained | bound to plan and policy choices; a later bar names a coin-map cell before its family reads its trades, never a part-F row | header; 14 |
| N5 | minimum days implied by the share | checked in part A; the coin's "at target with days owed" moot where implied | 4.3 A-2; 4.6; 7 item 7 |
| N6 | whole-contract rounding defeats `k_E` wins on the registered trades | the shortfall printed beside 10.2 | 10.2 |
| N7 | T-11 reads bars | marked `heavy` as well as `slow` (E-198) | T-11 |
| N8 | the joined timeline can reach 1,008 sessions | labelled; the renewal's window and the mass beyond it printed | 9.5 |
| N9 | T-0 did not check the calendars' hashes | added | T-0 |
| N10 | D-212's and D-117's constants typed | read from their modules | 8; 17.2 |

**Declined (first read):** none. **Narrowed, with reason:** B1 (b)'s behavioural test is applied as printed exposures
beside every cell rather than as a label that removes a cell, because under D-145 nothing outside tier 1 removes a cell
and tier 1 is enforced in every cell; B1 (c)'s quote-matching rule is not needed, since no label rests on a quote any
more.

### The re-read (Q-137r2) and Q-136b, and where each is answered in the third text

| finding | what it found | the answer (the lead's ruling) | where |
|---|---|---|---|
| **B-1** | the news stand-aside decided on a trade's exit (look-ahead) | decided at entry: no entry inside a verified window; a position open at the window's start flattened at that bar, priced from the bar under the fill rule; RD-01 G-3's bracket beside; flip and steady alike; the `TS` rows keep U1's rule | 2.6; 4.3 A-18; 4.7 items 1, 3; 10.3; 12.4; 13.1 |
| **B-2** | at Builder's close-only corners the pass ceiling is not a bound | the ceiling dropped there, the fairness check and the accounting identities the oracle; the corners listed (Appendix M rows 15 and 17, the second text's 14 and 16; no other) | 7 item 9; 9.6; Appendix M |
| S-1 (a) | the shifted battery's power about 0.86-0.89 | the shift is eight standard errors, power above 0.999 | 9.6; T-9 |
| S-1 (b) | the boundary quantity omitted expired accounts | its third term over every account neither passed nor failed, expired included; the lifespan read from the record | 7 item 8; 9.6 |
| S-1 (c) | the normal interval at a 1e-6 tail on a skewed quantity | every statistical oracle exact: Clopper-Pearson for probabilities; Freedman's inequality on the trades' fairness martingale, valid for any skew; skewed funded-shaped batteries in T-9 | 9.6; T-9 |
| S-2 | `mffu.rapideod50k.funded_news` missing; `tier1_news_events_restriction` is `changed` | a news rule applies only when its key is verified; U-31 for Rapid EOD; the changed entry not loaded, its list holding no minutes; no build applies the minutes calendar to `TS` or Labs beyond U1; `mffu.one_time_cutover_date` listed (moot) | 4.7 item 1; 5.1 U-31; 5.2; G-2; Appendix R |
| S-3 | U-rule figures live only in unverified entries' quotes | parsed from the named quote by A-19's declared parser, fail-loud, with a test; none missing | 4.3 A-19; 5.1; 17.2; T-5 |
| S-4 | censored attempts treated two ways | one convention: censored in both the renewal and the fee means, fees paid up to the horizon, the censored share printed | 9.4; 9.5 |
| S-5 | the memory bound and the worker count could contradict | the bound is the job's summed working set; U1 replays on one worker; workers stated per step; step 3's time bound set for one worker | 18 |
| S-6 | the coin's stacking exposure undefined | D-145's trigger defined exactly (two breaches across the campaign's accounts in the 21 sessions ending on the request day, that day included); the coin's windowed renewal; tested in T-9 | 4.7 item 5; 9.5; T-9 |
| N-1 | the calendar-to-sessions rounding unnamed | named: the stricter direction, up for a wait, down for a window that ends an account | 2.6; 7 items 3, 8 |
| N-2 | `coin_peak` aligned only if drawn every slot | drawn `n` per slot for every account | 15 |
| N-3 | whether LucidFlex's own configurations are in Lucid's enumeration | yes; Lucid joins whole or not at all, and cannot while the DLL-on configurations stand unmodelled | 2.4 |
| N-4 | identical gross runs counted twice | shared gross cells run once and counted once; the count fixed (45 corners, 2,016 gross runs) | 5.2; 16; Appendix M |
| N-5 | the lenient `b*` borrows Topstep's cap | the flip rows there labelled "`b*` at the reference cap" | 10.3 |
| Q-136b commissions | the per-plan commission unverified; the firm-wide figure verified | U-32: strict the firm-wide figure on every fill, lenient the engine's own; from the key, never typed | 4.5; 5.1 U-32; 5.2; Appendix R |
| Q-136b ceiling | the single-day ceiling verified at Rapid and Rapid EOD | the excess forfeited that day; the account's life ends at that close, "moved to Live", a terminal state apart, never a payout; unstated elsewhere, nothing applies | 4.3 A-11; G-4; 5.2; 7 item 10; 9.6 |
| Q-136b pin blockers | -- | none remains beyond the record's merge | 4.1; 19 |

**Declined (re-read):** none. **Two choices the rulings left open, made here:** the martingale checks became
Freedman's exact bound on the trades' fairness (an exact interval, as S-1 (c) allows), and the funded payout bound,
which then follows from the fairness check and two exact accounting identities, is printed rather than tested again.

## Appendix C -- the drafter's choices, each with its reason

| # | choice | where | reason |
|---|---|---|---|
| 1 | the reading is described, unnumbered, with no bar set for any family | header; 1 | E-023 (1) and E-134 (1); a bar is a later family's own declaration (N4) |
| 2 | the two modes read separately and joined by exact arithmetic | 2.6, 2.7, 9.5 | the funded account starts fresh at its own rules; stage one's `attempt_ev` |
| 3 | the grid `w` in {1, 1.5, 2, 3} and `r` in {$250 ... $2,000} | 2.6 | Stage 2's reference ratios and D-272's set, with one smaller risk |
| 4 | one coin trade a session | 2.6 | stage one's reference; D-429 |
| 5 | the flip sized from the rules: `k` the fewest days or sessions, `r_flip` the target over `k` wins | 2.6 | "large risk early" without a free parameter |
| 6 | one flip trade a session in the window, then steady | 2.6 | a flip day is one large winning day |
| 7 | D-212's stand-aside not applied to flip trades, but the registered cap is | 2.6 | the flip's point is size; the cap keeps it below maximum position size (S9) |
| 8 | the coin's request at the plan's own maximum, U-25 where none is stated; part F's at RD-01's rule | 9.2; 2.8 | the contract valued at its own terms; part F comparable with RD-01 |
| 9 | `k*` as the fewest largest days covering the target | 10.1 | no threshold chosen |
| 10 | the binding constraint as the last gate to open | 11 | read off counters |
| 11 | the costed coin at 50, 100 and 150 ticks only | 9.1 | the registered rungs; part B covers every width |
| 12 | `RI`'s coin trail exact only inside its read set, on `r` and `r_flip` | 9.1, 9.2 | the losing-trade peak has a closed law; no other path law is declared (S2) |
| 13 | 50,000 accounts a run, 504-session horizons | 9.1 | a pass probability's error well under a point; the gate's funded horizon |
| 14 | `TS-N` and `LU40`'s registered rows cited from RD-03 and RD-01 | 12.1 | no block of an earlier reading read as fresh |
| 15 | `LU50` added to the registered trades | 12.1 | on Stage 2's verified record and in scope |
| 16 | the Consistency payout paths on the coin only | 12.1; G-1 | the tables solve the Standard path |
| 17 | flips on P-16 only, at strict corners | 12.1 | RD-01's headline stream and its one-at-a-time precedent |
| 18 | the placement beside at `TS` only; Focused Trader models not run | 12.3; G-5 | Topstep-standard programs; their reach on Labs unread |
| 19 | U-13 to U-30's ends | 5.1 | each strict end the one that helps the user least, named before any run |
| 20 | prices, fees and lags never add a run; unverified prices on a $25-$500 grid | 5.1 | they move cash only; the grid covers every listed $50K price in the notes |
| 21 | D-145's tiers applied by behaviour; no cell withheld | 4.7 | the lead's ruling on B1 |
| 22 | the join rule: whole firm, the capture's enumeration, frozen at step 0's commit | 2.4 | nothing chosen after the captures (S6) |
| 23 | keys from Q-136's commit read by `git show`, not merged | 4.1; Appendix R | the lead's ruling on S5 |
| 24 | streams keyed by `(w, r)` only | 15 | every comparison paired (S1) |
| 25 | the oracles at a family-wise 0.01, Bonferroni | 9.6 | the lead's ruling on B3; Bonferroni is valid under any dependence among the checks |
| 26 | time and memory bounds per step, never thinned at run time | 18 | the lead's ruling on S12 |
| 27 | the renewal computed to 2,520 sessions | 9.5 | ten years; the mass beyond printed |
| 28 | the forced flat priced at the open of the window's first bar, with the flatten slippage | 4.3 A-18 | bars are stamped at their open, so that open is the first price at the window's start; the existing fill rule's flatten cost |
| 29 | the G-3 bracket shown on the flattened trades' own P&L, the journey not re-run | 4.3 A-18 | a beside reading; a re-run per bracket end would double part F for a count RD-01 kept beside |
| 30 | the martingale oracles as Freedman's bound on the fairness martingale; the payout bound derived | 9.6 | exact at any skew with power comparable to the normal width; the payout bound follows from fairness and the accounting identities |
| 31 | `PRO1`'s evaluation split into two corners by U-32, its gross cells shared | Appendix M | U-32 acts on costed cells only; the rule of 5.2, applied as for `L6` |
| 32 | the calendar rounding up for waits and down for windows that end an account | 2.6 | the direction that helps the user least (the lead's ruling on N-1) |
| 33 | a censored attempt a terminal outcome, its fees paid to the horizon | 9.4, 9.5 | one convention in the renewal and the means (the lead's ruling on S-4) |
