# F-04 (draft): the per-firm execution protocol -- P-14's and P-16's registered signals re-bracketed, re-timed and re-sized across each $50K plan's allowed grid; the whole grid described on the choice block, one trade set and one protocol per firm picked by a declared rule, judged once on its trades (family FP)

**Status: a first draft (TASK_QUEUE Q-141), not pinned.** Drafted on `wt/wt-scout` with master merged at c2aa709. It
goes to the red team, then the prereg-gatekeeper. At the pin the file is renamed `prereg/F-04_firm_protocol.md` and
nothing else changes; **this file writes no program family number into a rule**: the pinning row names k (k = 13 if
nothing is pinned before it), the commit and the sha256 of its LF text. Nothing declared is edited after the pin: a
change is a new family under a new row.

**When this text was written, nothing of it had been built, no engine had been run for it, no bar or walk had been
read for it, and no outcome of any protocol, plan or trade set had been computed or read.** It was written before
RD-04 was read (no `RD-04 read: step 2` row exists at its writing) and before any step of RD-05 ran. Anything chosen
after a reading is exploratory and reported apart (section 20).

**The operator's direction (2026-11-18, the brief Q-141).** The registered trades were built around Topstep's
conditions; run unchanged on another firm they are not a fair reading of it. Two steps were approved: (1) a described
reading -- the registered signals' trades re-sized and re-bracketed across each plan's full allowed grid, the whole
grid printed per firm, nothing picked; (2) a declared family, the next numbered one, that picks the best protocol per
firm on the choice block and judges it once on the judged block. **This file is both, as two stages of one family**
(section 1.3 says why one file): stage A is step 1 on the choice block; stages B and C are step 2.

**The operator's rulings of the same day (relayed by the lead, to be recorded in its decision row), written into the
grid here as declared:** (R-1) **news** -- no entry and no fill inside a verified news window at every firm and in
every protocol, and a position open at a window's start flattened under RD-05's rule (E-200 R-1); (R-2) **hours** --
executions at every hour of the day, overnight included wherever a plan allows it; (R-3) **order latency** -- the
alert-to-order latency is a protocol parameter, 5 minutes the reference (CHARTER section 4) with 3 and 2 minutes as
counted variants, the 5-minute cell reported beside every pick; (R-4) **entry type** -- resting limit entries beside
market entries, live at the latency, filled only on a trade through by one tick, cancelled at a news window's start,
at Topstep as at every other firm. Section 6 classes each; section 16 counts every cell they add.

| field | value |
|---|---|
| family | FP: the per-firm execution protocol -- for each $50K plan, the bracket (stop width, reward-to-risk), the entry (latency, market or limit), the session rule, the instrument mix and each mode's risk and steady-or-flip policy, applied to P-14's and P-16's registered signals |
| id | F-04 (`prereg/F-04_firm_protocol.md` at the pin); every result's `prereg_id` is `F-04` |
| program family number k | **written in the pinning row only** -- the next free: F-01 spent 10 (E-007), F-02 retired 11 unspent (E-094, E-095), F-03 spent 12 (E-192), so **k = 13** if nothing is pinned first |
| level | one-sided **0.05 / (k (k + 1))**: 0.05 / 182 at k = 13 (0.05 / 210 at k = 14) |
| stages | A the whole grid on the choice block, described, no pick (8); B the picks by declared rules on stage A's file alone (9); C one judgement of the pick on the judged block (10); the scorecard beside (12) |
| what can be carried | **only P-14's signal at the picked trade set**, spent through a group's picked protocol, when its trades' lift over the coin twin at that bracket passes C1 by the calibrated statistic and its value at that bound through the plan's own contract clears the bar (C2), every floor holding (section 1) |
| what is only described | every sizing, mix, policy and session-state comparison (E-023 (1), E-134 (1)); every P-16 protocol (a coin: no lift by construction); the comparison of firms; the stage-A grid |
| base | P-14 (A3-BRK30-CB20) and P-16 (`rc_s150_all_nr`), their registered offers and sides; R\* = P-14's U1 row beside (another engine: section 7.4) |
| plans | 19 configurations in four groups (Appendix P): Topstep standard, Topstep Labs, My Funded Futures, LucidFlex -- RD-05's plans by reference; Alpha Futures and Lucid's other plans join only by RD-05 section 2.4, before stage A's commit |
| rules | RD-05's catalogue by reference (its sections 2 to 5, Appendix R): Stage 2's verified ledger, the vendored Lucid ledger, the rules record at `wt/wt-firms` 1c9f34f as merged; read by key, never typed |
| development data | NQ 1-minute bars 2020-01-02 to 2026-07-16 only, through `extended/reader.py`; stage A and B on the choice block 2020-01-02 to 2023-12-29 alone; stage C on the judged block 2024-01-02 to 2026-07-16 |
| judged reads | three purposes, once each (section 4.4) |
| pass line | C1 the trade set's lift over its coin twin, one-sided at the family's level by the adopted one-sample statistic (Q-126, section 11); C2 per group, the lift's value at that bound through the group's picked protocol at least $500 at month 12 per start; the floors of 10.4; the scorecard beside, never the pass line |
| seeds | a block of ten, six in use and four reserved (section 15) |
| confirmation | NQ from 2026-07-17, a purchase, only if something carries (section 14) |
| `confirmation_tests_on_this_market` | 3 spent (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`); this family adds none and reads no NQ from 2026-07-17 |

---

## 0. In plain words (for the operator)

**What a protocol is.** How the same signal is traded at one firm: how wide the stop is and how far the target; how
soon after the alert the order goes in (5, 3 or 2 minutes) and whether it is a market order or a resting limit at the
alert's price; whether the account takes one trade a session, every trade, or stops for the day once a big day would
break the plan's consistency rule; micros only or minis first; and, separately in the evaluation and in the funded
account, how many dollars are risked per trade and whether the first sessions are traded large to try to pass or reach
the first payout in a day or two ("flip"). Each plan's own caps decide which of these are allowed at all.

**What happens.**

- **Stage A (described, nothing picked).** Every allowed protocol is run, plan by plan, on 2020 to 2023 only, and the
  whole grid is printed: passes, payouts, money and time per start day, and -- for P-14 -- how much its side beats a
  fair coin's on the same entries at each bracket.
- **Stage B (the pick, by a rule written now).** From stage A's file alone: one P-14 trade set (bracket, latency,
  entry type) for every firm, chosen as the one most firms can spend; then, per firm group, the protocol that spends
  it best. P-16's best protocol per firm is picked the same way, as a description.
- **Stage C (the judgement, once).** On 2024 to mid-2026, never read before by this family: does P-14's side at the
  picked trade set beat the coin by more than chance at the program's strict level, and is that edge, at its cautious
  lower bound, worth at least $500 a year through each firm's picked protocol? Each firm's journey is shown beside.

**What can come out, honestly.** Only P-14 can pass anything, because only P-14 has a side; P-16 chooses its side by
coin, so its edge is zero by construction and its protocols are only described. P-14's average trade is negative after
costs at every target on its registered brackets (E-125): its money so far has been the contract's, not the trades'.
So **the expected result is that nothing carries**, and the most useful product may be stage A's grid and the
firm-by-firm picks read out of sample -- described, not proven. A "no" is a valid close. The firm comparison itself
(which firm is best) is never a test: it is shown with its uncertainty.

**What it costs.** It spends the program's next family number (k = 13), which makes every later family's level a little
stricter. Section 19 asks the lead whether that is worth it, and offers the alternative.

## 0.1 Where the brief's questions are answered

| the brief's question (Q-141) | where |
|---|---|
| what a protocol is: size or risk, R:R and bracket, MNQ versus NQ, steady versus flip, stand-aside rules, when to stop; each grid per plan from its own caps | 6 (the table of every parameter, classed); 6.3 (the allowed grid, from RD-05 part B) |
| the operator's rulings: news, hours, latency, entry type | 5.4, 6.1, 6.2, 16 |
| brackets change the trades: walks at each bracket, which are re-used, their identity | 5 |
| leakage: one file or two | 1.3, 4 |
| the pass line, against CHARTER section 2, E-008 and E-023; what carries and what is only described | 1 |
| the calibrated statistic: what stage B waits on | 11 |
| multiplicity: k = 13, every cell counted, selection within firm, family-wise error across firms | 16 |
| seeds: a block of ten, unused anywhere | 15 |
| bounds: memory, one heavy run, a time bound per step | 18 |
| the items for the lead or the operator | 19 |

## 1. The question, and what can be carried (CHARTER section 2; E-008, E-023, E-134, E-196)

### 1.1 The question

For each recorded $50K plan, is there a way to trade P-14's registered signal -- a bracket, an entry and a sizing that
the plan's rules allow -- whose trades beat a fair coin on the same entries and brackets by more than chance, and whose
edge, priced through that plan's own contract at its lower bound, is worth a declared amount to a user? And, beside it
as a description: what does each plan's best protocol do for a user, for P-14 and for P-16, out of sample?

### 1.2 What can be carried, and what can only be described

**The pass line is unchanged** (E-008): a design passes only if its trades' lift over the coin twin on the same
brackets is above zero on the judged block at the family's level by a calibrated statistic, and its value at that bound
clears the family's declared bar; the floors bind; the scorecard is beside.

- **A bracket and an entry change the trades.** Each offer walked at another stop, target, latency or entry type is a
  different trade with its own outcome, and the same offer walked on the opposite side is its coin twin at that bracket
  (section 5). So a P-14 **trade set** -- the signal at one stop, ratio, latency and entry type, under a state-free
  session class (section 6.4) -- has a lift that can be tested. That is the only thing this family tests.
- **A size, a mix, a policy and a session-state rule add no trades** (E-023 (1); E-134 (1): a lever that changes which
  offered trades are routed, sized or kept but adds or removes no offered trade). Their lift over the coin twin is the
  trade set's, whatever they are. They are **described, never carried as a claim**: no row of this family says one
  sizing beats another.
- **What a carried design is.** "P-14's signal at the trade set T\*, traded through the protocol pi\*_g on the plan
  c\*_g" for a firm group g. It is carried because (C1) its trades' lift passes and (C2) that lift, at its bound, is
  worth at least the bar **through pi\*_g on c\*_g's contract**. The protocol is the vehicle in which the tested lift is
  priced, as a registered design carries its state table; **it is not claimed better than any other protocol**, and the
  carrying row says so. This is the drafter's reading of E-008 with E-023 (1); **section 19 item 2 asks the lead to rule
  on it before the pin.**
- **P-16 can carry nothing.** Its side is a seeded coin (its registration: "a coin carries no information"), so its
  lift over a coin twin is zero by construction at every bracket. Its protocols are described in every stage; its
  per-group picks are read once on the judged block as descriptions.
- **The firm comparison is described.** Each group's pick is judged on the same lift (C1), so the groups differ only in
  C2 and the floors; which firm's journey is best is a scorecard comparison with its uncertainty (12), never a test.
- **Not claimed either:** that T\* beats P-14's registered bracket. C1 tests T\*'s lift above zero, nothing else.

### 1.3 Why one file, in three stages (the brief's leakage question)

One file, because the pick must be written before the grid it picks from exists. With two files, the second's pick rule
would be written after the first's grid was printed -- a choice after a look -- unless both were pinned together, and two
files pinned together are one declaration. In one file: stage A's grid is computed on the choice block only and picks
nothing; stage B's rules are pinned before stage A runs and read stage A's file alone; stage C reads the judged block
once, for the pick. The operator's step 1 becomes stage A on the choice block; **the judged block's whole grid is never
computed by this family** (section 19 item 9 offers it as a later described reading).

## 2. Prior exposure: what has already read these signals, brackets and plans

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| Stage 2's A3 screens and P-14's registration (Stage 2 D-490, D-491, D-499, D-501, D-512) | A1's mechanical patterns against the clock's coin; the rungs; P-14's gate | the whole development window | the 12.5- and 25-point rungs kept, the 50-point rung's far targets not resolving (D-491); P-14 registered | **the judged block has been read for P-14's side at its own rungs** by Stage 2's screens (the drafter did not open those files); the 200-tick stop's resolution is expected to fail at far targets |
| U1 (Stage 2 D-620), Q-05 (E-010), Q-44 | P-14's and P-16's journeys, five seats, their state tables | all starts | the reference rows | R\* beside, another engine (7.4) |
| Q-18's stress checks (E-125) | P-14's trades | the whole window | P-14's mean trade negative at every R (in words, E-125) | the prior: no lift is expected |
| Q-108 and Q-126 (E-115, E-161, E-187) | sign-flip nulls on P-16's judged pairs | the judged block (pair magnitudes under nulls) | a calibration, not an outcome of P-14 | the statistic's domain (11) |
| F-03 (E-192) | P-16's overnight offers | the choice block | closed at stage B | none on these trade sets |
| RD-01, RD-03 (pinned; built, not run); RD-05 (pinned, E-200; not built) | the registered trades on these plans; the coin maps; part B's sizing arithmetic | all starts (part F) | nothing on master | stage B reads RD-05's step-0 arithmetic only (k_E, k_F, r_flip, b\*, part B's allowed set): rules arithmetic, not an outcome. **No coin-map cell or part-F row of RD-05 is used as a bar or a rule here** (RD-05 section 14, its N4) |
| program U's nine families | P on the late block | starts from 2024 | all closed | the judged block is late development, not out of sample |

**Never run:** P-14's signal at any stop but its rungs, at a latency of 3 or 2 minutes, or as a limit entry; P-16's at
any stop but 150 ticks, any latency but its own, or as a limit entry; any fixed-protocol single-seat journey on any plan.

**The drafter's reads (disclosed).** CHARTER; RD-05 whole; E-008, E-011, E-023, E-035, E-125, E-134, E-161, E-187, E-192,
E-195, E-196, E-200; Q-126's plan sections 1 to 2.5 and its coverage table; Q-108's section 2.1; F-03's header and
sections 14 to 17; the walker's and the reader's docstrings; P-16's registration's header; Stage 2's D-149, D-150,
D-271, D-272, D-324, D-429, D-499, D-501, D-512 in part; the record at 1c9f34f for key names and statuses (position
limits, prices, news, hours). **No result file of either repository was opened.** The seed search printed counts only.

## 3. Contract fit and conduct (RD-05 by reference, and what this family adds)

### 3.1 Carried from RD-05 unchanged, by reference

RD-05 sections 2.1 to 2.8 (the plans and modes, the switch, the request rule of 2.8), 4.1 to 4.6 (the rules' sources,
the term roles, the adapters A-0 to A-19, the gaps G-1 to G-10, the cost rule per plan, the table inputs), 4.7
(conduct: D-145's tiers by behaviour, tier 1 enforced at zero, tier 2 off in the headline, tier 3 priced by the
ladder), 5 (the U-rules U-1 to U-32 and the strict and lenient corners) and Appendix R (the keys). RD-05's pinned text
is `prereg/RD-05_firm_modes.md`, LF sha256 `be7f90fb56af6e09c92c0277ce83c228f2e2fbeca8fc26b87d90ccf50239659c` (E-200); a
reference here is to that text, so it cannot drift. Where a reference reads "the registered trades" there, it reads
"this family's protocol trades" here, with this family's sizing (6.5) in place of the registered table.

### 3.2 What this family adds or changes

- **One seat.** A user holds one account at a time (7.2): RD-05's U-14 (a pass waiting at a funded cap) cannot bind,
  checked; the seats are RD-03's lever, not this family's.
- **The news rule at every firm** (the operator's R-1; 5.4): where RD-05 applies a firm's news rule only at an account
  a verified key reaches, this family applies the verified window at every account of every plan. Topstep's own window
  entry (`tier1_news_events_restriction`) has status `changed` and is not loaded (RD-05 4.7 item 1), so the windows
  come from the verified `mffu.news_tier1_rule`, its minutes and events derived from the entry, never typed (section 19
  item 6).
- **Hours** (R-2; 6.2): every hour each signal offers, overnight included, where the plan's hours allow. Stage 2's
  verified `trading_hours` gives Topstep's and, by RD-05's U-13 form, Labs'; **My Funded Futures' and Lucid's hours have
  no entry in the record** -- U-34 below, and section 19 item 7.
- **U-33. An unverified evaluation price in a journey** (`labs.010_50k_dpp_eod.eval_fee` and My Funded Futures'
  unverified prices, RD-05 5.2's U-2 rows). Purchases do not depend on the price (the bankroll unbound), so every
  journey measure is exact arithmetic in it and is printed at both ends of RD-05's U-2 grid ($25 and $500). **A rule of
  this family reads a quantity at the end that makes it least favourable to the design**: the value V (7.3) at the end
  where V is smallest (V is linear in the price, so one end), P and every user measure at the higher price. No price
  inside the grid is chosen.
- **U-34. A plan whose record states no trading hours** -- both ends: strict, the plan trades only the hours of the
  regular session of Stage 2's verified `trading_hours` that RD-05's `TS` rows use and no overnight offer is taken;
  lenient, Topstep's verified hours whole. A difference the corners show is printed, labelled "hours unrecorded".
- **No trade at the full allowance**: every trade is capped at Stage 2 D-117's headroom fraction of the allowance
  (`sizing.DEFAULT_HEADROOM_FRAC`, read from the module), as RD-05 2.6 caps its flip trades -- the registered designs'
  operating rule, and the guard against maximum size into news (D-145 tier 1).
- **Hand entry stays** (E-008): every order is placed by hand, at the protocol's latency; no automated or API order
  entry at any latency.

## 4. Data, blocks, the seal and the reads

### 4.1 The blocks, as dates, now

- **Choice block:** sessions 2020-01-02 to 2023-12-29 (stages A and B). **Judged block:** 2024-01-02 to 2026-07-16
  (stage C and the scorecard beside). **Confirmation:** NQ from 2026-07-17, not on disk, never read until a carried
  design is registered, a purchase (14).
- No warm-up is needed: no feature is computed; each signal's offers use only their own session's closed bars, as
  their registered builders make them.

### 4.2 The seal, mechanically

- **Stage A's arrays hold choice-block sessions only.** The walks of stage A are made from choice-block bars (no tag);
  the engine's draw arrays end at 2023-12-29, so no attempt, start or journey of stage A can reach a later session --
  an attempt or a journey still open at the block's last session is censored there (RD-05 9.4's convention: its cash to
  that session counted, the censored share printed).
- **Stage B reads stage A's files and RD-05's step-0 file only**: no bar, no walk. Its script refuses any other input.
- **Stage C reads the judged block** under the purposes of 4.4, from a clean checkout of a committed commit, once per
  purpose (a rerun only under `repeat=`, E-053).
- **The judged block's MDL is computed from the choice block** (9.2): the judged block's trade count is never read
  before stage C (the chain's count depends on exits, an outcome).

### 4.3 The unit and the horizons

A start is one session of a block taken as a fresh user (7.2). For each measure of horizon h, the starts are the
block's sessions with h sessions left in the same block (RD-03 section 5's table of horizons, carried); a month is 21
sessions.

### 4.4 The judged block's reads

- **Judged-block reads:** `fp_judgement`, `fp_gate_floor`, `fp_scorecard_beside`

- `fp_judgement`: stage C's walks of T\*'s offers on the judged block, C0, C1, C2 and the floors of 10.4 but the gate;
- `fp_gate_floor`: the gates of 10.4 item 1;
- `fp_scorecard_beside`: after the verdict row, the walks of every other pick's trade set and of the 5-minute cells
  (12.1), and every journey beside.

None is a choosing or fitting purpose (T-0). The identities run under the purpose `identity` and their own row.

## 5. The signals, the walks, the coin twin and the news rule (brackets change the trades)

### 5.1 The offers

- **P-14:** its registered events and sides as Stage 2's builder makes them (A3-BRK30's 30-minute breakouts from A1's
  walk cache, its side rule, its news cuts; `atlas_a3`, imported), every hour it offers.
- **P-16:** its registered marks and coin sides (`rc_s150_all_nr`'s builder; its registered coin seed, inherited),
  every hour it offers.
- An offer's **alert** is its registered entry's decision time (the mark, or the breakout bar's close); the entry is
  placed at **alert + latency** (6.1). At latency 5 the offers' entries are the registered ones.

### 5.2 The walks: how they are made, which are re-used, and their identity

- **Made by one code path:** this repository's walker, `extended/walker.py`, preset `STAGE2` (E-011: Stage 2's walk for
  market entries, P-16's pinned trades reproduced), every offer walked at every stop of the grid and every ratio,
  **both sides** (`walk_pair`), so each trade and its coin twin come from the same walk. A market entry fills at the
  open of the first bar at or after alert + latency (the walker's market rule); a limit entry by 6.1.
- **Limit entries** use `fill_bar="pair"` and `mirror_booking="symmetric"` (the walker's side-neutral pair, T-13):
  a pair whose fill bar touches either trade's stop or target is settled ambiguous, zero lift, counted (feature-rules
  section 3's pair rule); **the ambiguous share is capped at 10 % of a trade set's pairs**, a trade set above it
  ineligible (8.2).
- **Re-used, as references only.** No cached walk is an input: every walk is made anew so that every bracket's trade
  and twin share one code path. Stage 2's cached walks are the identity's references (17.3 item 2): at P-16's 150 ticks,
  P-16's `TRADES_SHA256` (E-011, re-held); at P-14's rungs, the A3 cache's walks of P-14's offers, every column the
  cache holds, offer for offer; and P-14's registered trade list rebuilt from them by its rung rule. Both at latency 5,
  market entries, the news rule of 5.4 off (the registered form). Any difference refuses every later step.
- **The new walks** (other stops, latencies 3 and 2, limit entries, the news rule on) have no Stage 2 file to match;
  they rest on the identity's code path, the walker's synthetic tests (`tests/test_walker*.py`, T-13's mirror zero) and
  T-2 (section 17).
- **What a walk records** (the walker's `Trade`): fill or why not (void, cancelled, refused by news), kind (stop,
  target, flatten, breakeven, ambiguous), exit slot, gross and net R per micro-equivalent (Stage 2's costs at the stop,
  `atlas_a3.fee_by_stop`), MAE; the breakeven move as `STAGE2` has it. Per bracket the unresolved (flatten) share and
  the breakeven share are printed.

### 5.3 The coin twin and the estimand

For a trade i of a trade set, the pair difference is `x_i = (net_R(side) - net_R(mirror)) / 2` at the trade's own
bracket (Q-108 section 2.1's estimand, on net R per micro-equivalent): the trade's outcome less a fair coin's expected
outcome on the same entry, exactly, with no seed. The trade set's lift is the mean of `x_i`; the statistic reads its
session sums on the block's calendar (11). For P-16, `x_i` has expectation zero by construction; its mean is printed as
a check, never as a reading.

### 5.4 The news rule, at every firm (the operator's R-1; RD-05 A-18 and E-200 R-1, extended)

On a release day of a pinned calendar -- the BLS 08:30 releases (`vendor/stage2/data/releases_bls_0830_*.csv`), the FOMC
minutes (`config/calendar_fomc_minutes.csv`, LF sha256
`0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7`) -- with each window's bounds the verified
`mffu.news_tier1_rule`'s minutes around the release's time, derived, never typed:

- **no entry and no fill inside a window**: an order whose live time (alert + latency) falls inside a window is not
  placed (counted); a resting limit live before a window's start and unfilled is **cancelled at the window's start**;
  no fill is booked on a bar inside a window;
- **a position open at a window's start is flattened at that bar** -- the 1-minute bar stamped at the window's first
  minute, priced at its open with the fill rule's flatten slippage (`fills.yaml`'s active profile,
  `flatten_slippage_ticks`); its mirror is flattened at the same bar, so the pair stays like for like;
- decided at the alert from the clock and the calendar alone; applied in the walks, so every plan and protocol meets it;
- **kept beside it**: CHARTER section 4's own rules -- no entry at or before 07:35:00 CT on a BLS 08:30 day, FOMC days out
  -- unchanged; E-029's early closes (`config/calendar_early_closes.csv`, LF sha256
  `72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2`), no trade exiting after the session's flatten;
- events in the verified rule's list with no pinned calendar are not applied and are listed (RD-05 G-2's form).

### 5.5 The chain: one position at a time

For a signal, bracket, latency and entry type, the offers of a session in time order form the **chain**: the first offer
whose order fills; then each later offer whose order goes live at least five minutes after the previous chain trade's
exit (D-160's five minutes flat; D-429's one position at a time). A limit that does not fill does not occupy the slot.
The chain is fixed by the walks alone -- **state-free**: a trade the account later stands aside on still occupies its
slot (a declared rule: fewer trades, never a state-dependent re-chaining).

## 6. The protocol: what it is, every parameter classed, and the allowed grid per plan

### 6.1 The parameters

| parameter | what it is | values | class | why |
|---|---|---|---|---|
| signal | whose offers and sides | P-14; P-16 | fixed: two | the registered signals (the brief); only P-14 is testable (1.2) |
| `s` | stop width, ticks of 0.25 points (MNQ and NQ alike) | P-14: `rung` (its registered rung rule), 50, 70, 100, 150, 200; P-16: 50, 70, 100, 150, 200 | searched (stage B) | the registered rungs (50, 100, 150) and a step either side, all above the cost-drag floor (Stage 2 D-271 (3)) and every one in RD-05 part B's widths |
| `w` | target as a multiple of the stop | 1.0, 1.5, 2.0, 3.0 | searched | RD-05 2.6's ratios |
| `L` | alert-to-order latency, minutes | 5 (reference), 3, 2 | searched; 5 reported beside every pick | the operator's R-3; CHARTER section 4's five minutes the reference |
| `e` | entry type | market; limit | searched | the operator's R-4 |
| limit price | where a limit rests | the price at the alert -- the close of the last bar closed at the alert (`walker.price_at`), on the side's buying or selling side | fixed | the signal's own price; a fill is the market retesting it; no free offset |
| limit window | how long a limit works | from alert + `L` to the earliest of 30 minutes later, a news window's start (cancelled) and the walk's last entry bar | fixed | one value; a different window is a new family |
| limit marketable at its live time | -- | void, counted (the walker's rule) | fixed | never a better fill than the limit |
| `q` | session rule ("when to stop") | `one` (the session's first chain trade only); `all` (every chain trade); `cap` (every chain trade until the session's net reaches the mode's consistency allowance, 6.4) | searched | the operator's "when to stop"; `cap` is identical to `all` at a mode with no consistency rule (run once, printed so) |
| `m` | instrument mix | `MNQ` (micros only); `mixed` (as many minis as fit, the rest micros, D-324) | searched | the brief's MNQ versus NQ; "minis first" is `mixed`; minis-only is dropped (below) |
| `r_E`, `r_F` | dollar risk per trade in the evaluation and in the funded account | RD-05 2.6's grid: $250, $500, $750, $1,000, $1,500, $2,000, each mode separately | searched | RD-05's grid, by reference |
| `policy_E`, `policy_F` | steady or flip per mode | `steady`; `flip` (RD-05 2.6's flip: the first k sessions' first trade at r_flip, then steady) | searched | the operator's flip days (E-196); k_E, k_F, r_flip and b\* from RD-05's step-0 file, at the strict corner |
| stand-aside | when a trade is not taken | D-212's consistent risk and D-272's cost floor, the registered sizing rule's `stand_aside` (read from the module); a flip trade exempt (RD-05 2.6) | fixed | CHARTER section 4's realised-risk floor |
| headroom | the largest size | D-117's `sizing.DEFAULT_HEADROOM_FRAC` of the allowance | fixed | 3.2: never at the full allowance |
| room and daily limit | cuts | D-313's room cap; the plan's daily limit where it has one (RD-05 A-1) | fixed | the plan's rules |
| news | 5.4 | at every firm | fixed | the operator's R-1 |
| hours | 6.2 | every hour the plan allows | fixed | the operator's R-2 |
| the request | payout requests | RD-01 2.3's rule, as RD-05 2.8 | fixed | the payout lever is RD-02's |
| payout path | Standard or Consistency, Daily or 5 Winning Days | by configuration (Appendix P) | fixed per configuration | a configuration of the plan |
| seats | accounts at once | one (7.2) | fixed | seats are RD-03's lever |
| resets, reactivations | -- | none | fixed | RD-05 2.8 |
| the breakeven move | stop to entry at a session open | `STAGE2`'s | fixed | the registered walk |
| **dropped** | minis only; an ATR-scaled stop; time stops; partial exits or scaling in; a solved state table per plan | -- | dropped | minis-only is `mixed` without its remainder (dominated but where a plan counts a micro as a mini, which `mixed` at RD-05's U-26 already reads); a scaled stop is another signal; CHARTER bans time stops; a solve is its own family (G-1) |

### 6.2 Hours (the operator's R-2)

Every offer of each signal at every hour it offers is in the grid, overnight included, at every plan whose hours allow
it: Topstep's and Labs' by Stage 2's verified `trading_hours` (Labs by RD-05's U-13); My Funded Futures' and Lucid's by
U-34's two corners. Every trade flattens by the session's flatten (15:10 CT, the walker's `STAGE2` end) or at a news
window's start (5.4).

### 6.3 The allowed grid per plan (from the plan's own caps)

A sizing cell `(s, w, m, r)` is **allowed** in a mode of a configuration when RD-05 part B's `allowed` section
(`results/modes_rules.csv`, step 0) marks it sizeable under D-212 and inside every limit at the mode's start state, at the
strict corner; `rung` is allowed when both its widths are. A flip cell is allowed when its steady cell is and RD-05's
`flip_sizes` gives the mode a finite k and r_flip at that `w`. A cell not allowed is printed "not allowed at the plan's
start state" and not run. During a journey every trade is re-sized from the account's state (6.5), so a cell allowed at
the start can stand aside later, counted.

### 6.4 Trade sets and session classes

A **trade set** is `(signal, s, w, L, e, class)`, with `class` the state-free part of `q`: `one` (the first chain trade of
each session) for `q = one`, `chain` (every chain trade) for `q = all` and `q = cap`. Its trades and their twins are
fixed by the walks (5.5); its lift is tested on them, whatever an account later stands aside on. `cap`'s stop for the
day depends on the session's earlier trades, known when the next would enter: a session-state rule, described. The
mode's consistency allowance is the mode's recorded consistency share times its base (the evaluation's target; the
funded payout gate's base where the plan's record has a funded consistency rule), at the account's state, by RD-05's
adapters.

### 6.5 Sizing a trade (RD-05 9.2's costed rule, by reference)

At each trade the contracts `n` are recomputed from the account's state: the largest whole `n` under the mix rule with
`n` contracts' stop-out -- the stop's dollars, the stop tick and the entry tick of slippage, the round-turn fee by the
plan's cost rule (RD-05 4.5, U-32) -- within the room above the floor and the day's remaining limit, at most
`floor(r / (s x tick value))`, the current tier's allowance by the plan's counting rule and the headroom cap; a trade
whose `n` carries less than the stand-aside share of `r` is not taken, the session counted toward inactivity (RD-05
A-3). A flip trade: RD-05 2.6 with this protocol's stop. Tick values from `propedge/execution/instruments.py`, read.
Costs are charged inside the room. Its dollar P&L is `n x (gross R x s x tick value)` less its costs at `n`.

## 7. The engine: single-seat journeys on historical trades, and the value arms

### 7.1 The attempts

RD-05's coin engine A-0 with its adapters A-1 to A-19 at each mode-corner (by reference), plus one marked addition,
**F-A1, the historical chain draw**: account i is an attempt begun at session `t_i` of the block; on its session d, slot
k, the draw returns the k-th chain trade of session `t_i + d` (after the session rule), sized by 6.5 from the
account's state, or NaN where none (the chain exhausted, the session rule stopped, a stand-aside). The draw never
clamps; the engine applies floors and limits (the contract-engine skill). **An attempt is begun at every session of the
block**, vectorised across starts and across the twelve sizing cells of a mode, giving for each mode cell and each
session t: the attempt's end session, its cause (pass; floor; lifespan; inactivity; an end by count; "moved to Live"
at a verified ceiling, RD-05 A-11; censored at the block's end), its fees and, in the funded mode, each payout's
session and amount.

### 7.2 The journeys (F-A2, the composition)

A user starting at session s buys an evaluation at s; an attempt ending unpassed at e is followed by a new one at e + 1;
a pass at e activates the funded account at e + 1 (RD-05 2.7, fees at the switch by key); a funded account ending at e
is followed by a new evaluation at e + 1; until s + 252 sessions or the block's end. This is exact pointer composition
of 7.1's tables, never a new draw; it equals a direct sequential replay start for start (17.3 item 3; T-5). Measures
per start: net cash (payouts received less every fee paid) at months 1, 2, 3, 6 and 12 and whether ahead; P and the
guarded measures of CHARTER section 2 by `vendor/stage2/docs/USER_MILESTONES.md`'s definitions where they apply to one
seat (S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c), E-014's journey variables, sessions to the first pass and payout.

### 7.3 The value arms

For a P-14 protocol on a configuration and a block, with `lhat` the block's own lift of its trade set (5.3):

- **the design arm** -- the journeys as traded;
- **the zero-lift arm** -- every executed trade's dollar P&L shifted by `-lhat x n x s x tick value`: the design with its
  block's lift removed (Stage 2's convention of shifting outcomes, as its gate's zero-edge twin);
- **the lift-L arm** -- shifted by `(L - lhat) x n x s x tick value`.

**The value at L**, `V(L)`, is the mean over the block's starts with 252 sessions left of month-12 net cash in the
lift-L arm less in the zero-lift arm, at U-33's price that makes V smallest. Each arm is a full engine run (a shift moves
floors, passes and payouts). Stage A runs the design and zero-lift arms, so `V(lhat)` is printed for every P-14 cell.

### 7.4 What this engine is not

It is not U1's replay: one seat, a fixed protocol, no state table, no router across accounts. Its rows are never paired
with U1's; R\* (P-14's U1 row) is printed beside, labelled "five seats and the state table: another engine". Inside
this engine every comparison is paired on the same starts.

## 8. Stage A: the whole grid on the choice block, described, no pick

### 8.1 What is computed (every cell, every configuration at its strict corner)

1. **The trade sets** (P-14 288, P-16 240): supply (chain trades a session; the class `one`'s share of sessions), the
   void and cancelled shares (limit entries), the news-refused and news-flattened counts, the ambiguous share (limits),
   the unresolved and breakeven shares, by year; `lhat_A` with its session-cluster standard errors at the 21-, 42- and
   63-session blocks; the band check of Q-126 section 2.5 on the trade set's sides (a switching side, below 42
   sessions; 11) and, if the adopted statistic is scope D's, 4.4's admission from sides only. For P-16 `lhat_A` is a
   check (expectation zero), printed as such.
2. **The mode cells** (7.1): per mode, per trade set's entries-bracket, session rule, mix and sizing cell -- the
   evaluation's pass share per attempt, sessions to a pass, fees per pass, the causes; the funded account's payout
   share, sessions to the first payout, mean net per activation, the causes; the realised-to-intended risk (E-022 (1)'s
   allowance-capped form); stand-asides; the exposures of RD-05 4.7 item 5; for P-14, the zero-lift arm's same rows.
3. **The joined journeys** (7.2): every protocol cell -- P, the guarded measures, the mean net at months 1 to 12 with p10,
   p50, p90 and CVaR10 at month 3 (E-134 (2)'s guard row), sessions to the first payout; for P-14, `V(lhat_A)`.
4. **Repriced configurations** (`TS-N/std`, `TS-N/con`): every fee re-priced on `TS-S`'s runs, exactly.

Nothing is marked best. Every row is labelled "choice block, described, in sample".

### 8.2 The gates before any outcome (the kills; a killed cell is counted and printed, never read for a pick)

- **Resolution:** a trade set whose chain's unresolved share exceeds 5 % (Stage 2 D-212 as D-308 raised it) is
  ineligible (killed) for stage B. Per year beside.
- **Pair rule:** a limit trade set whose ambiguous share exceeds 10 % is ineligible (5.2).
- **Band:** a P-14 trade set whose sides fail Q-126 2.5's check for its declared band is ineligible ("not judgeable at
  its persistence").
- **Realised risk:** a protocol cell failing CHARTER section 4's realised-risk floor (at least 90 % of trades within 10 %
  of intended risk, allowance-capped, E-022 (1)) in either mode is ineligible.
- **Tier 1:** every tier-1 count of RD-05 4.7 item 1 is zero in every cell, an entry or fill inside a news window among
  them; a nonzero count is an engine error that stops the step (RD-05 13.1).

## 9. Stage B: the picks, by declared rules on stage A's file alone

### 9.1 What it waits on

Stage A's file on record by the lead's row; **the adopted one-sample statistic** (11); RD-05's step-0 file. Stage B
reads no bar and no walk.

### 9.2 The judged power of each P-14 trade set (computed from the choice block only)

For each eligible P-14 trade set tau: `MDL50_J(tau)`, the lift at which the adopted statistic, one-sided at the
family's level, rejects with probability one half on the judged block, computed by that statistic's own MDL function on
tau's choice-block pairs with each member's standard error scaled to the judged block's sessions by
`sqrt(n_A / n_J)` (n_A and n_J the blocks' session counts from the calendar, not from any trade) and its
degrees of freedom at the judged block's block counts; and `Lstar(tau) = lhat_A(tau) - MDL50_J(tau)`, the bound the judged
block would give if the choice block's lift held. **Kill B:** tau with `Lstar(tau) <= 0` is not judgeable.

### 9.3 Values at the expected bound

For each eligible tau with `Lstar > 0`, each configuration c and each eligible protocol cell pi on tau at c's strict
corner: `VA_c(pi; Lstar) = VA_c(pi; lhat_A) x Lstar / lhat_A` -- stage A's two arms, interpolated linearly between zero
lift and the block's lift (a declared ranking rule; the judged value is computed by full arms, 10.3).

### 9.4 The trade set T\* (one, common to every firm)

T\* is the eligible tau that ranks first by, in order: (a) the number of groups g whose best `VA_c(pi; Lstar)` over
`c in g` and pi reaches the bar; (b) the sum over groups of each group's best `VA` (the trade set most firms can
spend, worth most across them); (c) the larger `Lstar`; (d) latency 5 before 3 before 2, market before limit; (e) the
earlier tau in the order stops ascending (`rung` first), ratios ascending, class `one` before `chain`. **K0 on T\***
(9.7); a lax T\* is struck, recorded, and the next tau by the same order is taken. **If no tau is left, or the first
tau's count (a) is zero, the family closes at stage B** ("no lift above the judged MDL worth the bar at this family's
level").

### 9.5 The protocol per group, and per configuration

- **Per group g:** `(c*_g, pi*_g)` = the configuration in g and the eligible protocol on T\* with the largest
  `VA_c(pi; Lstar(T*))`; ties by the larger P on the choice block, then latency 5 first, then Appendix P's order and
  6.1's value order. A group whose best is below the bar is "closed at stage B for this group": its pick is read beside
  as a description, no line.
- **Per configuration c** (described): its own best protocol on T\* by the same rule, read beside (12).
- **P-16, described:** per configuration and per group, the eligible protocol cell (any P-16 trade set) with the largest
  choice-block P at U-33's higher price, ties by the mean month-12 net, then latency 5 first, then the orders above;
  labelled "described: a coin, no lift; never carried", with E-134 (2)'s guard row.

### 9.6 Recorded before stage C

`results/fp_pick.csv`, written by the stage-B script from stage A's files alone: T\*, `lhat_A`, `MDL50_J`, `Lstar`,
the struck taus with their K0 results, each group's and each configuration's pick with `VA`, P-16's picks, the
5-minute sibling of every pick (12.1). The lead's row records it before stage C runs. Nothing of stage B is revisited.

### 9.7 K0: the statistic's own size on the pick's own magnitudes (F-03's K0 form; E-052 (1))

Sign nulls on T\*'s choice-block pairs: `x_i^0 = sign_i x |v_i|`, `v_i = (net_R(long) - net_R(short)) / 2`, under the
declared band's side models -- the coin (independent fair signs a trade), flips at 1, 5 and 21 sessions, Markov sides of
mean dwell 30 (Q-108's class below 42 sessions) -- 200,000 draws each, keyed `[20262430, tau index, model index]`; the
adopted statistic at the family's level on each. **Lax** when, for any model, the rejection share's exact 95 %
lower limit exceeds the level. K0 at stage C (10.2) repeats it on the judged pairs, keyed `[20262431, model index]`.

## 10. Stage C: the judgement, once, on the judged block

### 10.1 What it waits on

The stage-B row; the statistic's adopting row with its code's blob (11); every identity of 17.3 holding at the run's
commit; the build's red-team read.

### 10.2 C0, before any outcome is read (refusing)

On the judged block, under `fp_judgement`: T\*'s offers walked; its supply; its unresolved share at most 5 % (a floor;
above it, "not claimed"); for limits, its ambiguous share at most 10 %; the band check and, in scope D, 4.4's admission
on the judged sides (Q-126 2.5: a mismatch is "not claimed", never a switch); K0 on the judged counts (lax: "not
claimed"). The judged trade count inside the statistic's validated sizes (11), or "not claimed".

### 10.3 The lines

- **C1** (common): `L_J`, the adopted statistic's one-sided lower bound of T\*'s lift on the judged block at
  **0.05 / (k (k + 1))** (0.05 / 182 at k = 13), above zero.
- **C2** (per group g with a stage-B pick at or above the bar): `V_J(L_J)` for `pi*_g` on `c*_g`, by full lift-L and
  zero-lift arms on the judged block (7.3) at the strict corner, at least **$500 at month 12** per start, the mean over
  judged starts with 252 sessions left.

### 10.4 The floors (per group g, every one required)

1. **The long-run gate** (Stage 2 D-145): growth on the required bankroll at the bound above zero -- Stage 2's gate
   (`propedge.campaign.gate.run_gate` through `extended/gate.py`) with RD-05's A-14 gate arguments for `c*_g`, one seat,
   the protocol as a constant-action table (one action per mode), on T\*'s judged trades, the bound arm each trade shifted
   by `L_J - lhat_J` and the zero-edge twin (`-lhat_J`) beside, 500 paths at the gate seed (15), under `fp_gate_floor`.
2. **Every offered R resolving**: T\*'s judged unresolved share at most 5 % (10.2).
3. **Realised risk** on the judged replay of `pi*_g` (8.2's form).
4. **Verified rules**: every value from a verified entry or a declared U-rule; T-0's key mapping holding at the run's
   commit.
5. **Conduct tier 1**: every count zero (8.2), news included.

### 10.5 The verdict

For group g: **CARRIED** when C0, C1, C2_g and every floor_g hold; otherwise **not carried**, with the first line that
failed. If C1 fails, every group is not carried. The verdict is written at 0 % payout denial with the placement off
(E-008), and recorded by the lead's row before anything of section 12 is read.

## 11. The calibrated statistic: what stages B and C wait on

1. **Q-126's calibration run** (E-195, queued under the lock) and the row pinning its choice file.
2. **Its validation HOLDS** by its criterion, and a row adopting the statistic -- scope D's primary, or the scope-Q
   branch's -- naming the code's git blob id. Every run of stages B and C refuses a commit whose blob differs. Until that
   row exists, stage B does not run.
3. **The declared side persistence** (E-035 (6); Q-126 2.5): P-14's side is a **switching side** set at each breakout,
   declared **below 42 sessions**; the traded share of sessions is printed by stage A. So the statistic used is the
   primary (in scope D with 4.4's admission when scope D chose it, in scope Q when the scope-Q branch is the primary). The
   barred regime-filter kind (E-187) is not used.
4. **Its validated domain.** Q-126 calibrates and validates on P-16's judged pairs and realistic synthetic nulls, values
   `win1` and `net3`, subsets of 200 to 5,000 trades (its section 3.1). T\*'s values are net R at another bracket, so
   **K0 (9.7, 10.2) is this family's own size check at its level on T\*'s own magnitudes and counts**; a judged count
   outside the validated sizes is "not claimed". Whether K0 suffices is section 19 item 3.
5. **The level is inside the calibrated range**: Q-126's levels run over k = 13 to 20, and this family judges one test
   at k = 13's (16.3).
6. **If no one-sample statistic HOLDS**, the family is withdrawn before stage B: stage A's file stands as a described
   reading of the choice block, cited by any later family that uses it; k's fate is the lead's (E-094, E-095 retired a
   number unspent).

## 12. The journey scorecard -- beside, never the pass line (CHARTER section 2; E-008, E-014, E-015, E-134)

### 12.1 What is read on the judged block, after the verdict row (`fp_scorecard_beside`)

- every configuration's P-14 pick on T\* and every configuration's P-16 pick (the group picks among them), at the strict
  corner: the scorecard as 7.2 lists it, each measure a distribution over starts (median, p10, p90), the guard row of
  E-134 (2), and for P-14 the zero-lift arm and `V_J`;
- **the 5-minute cell beside every pick** (the operator's R-3): the same protocol at latency 5 where the pick's is 3 or
  2 -- its trade set's lift (described, no level), its scorecard and its value;
- the lenient corner of every two-corner configuration's picks;
- **the firm comparison**: every group's pick paired against the `TS-S/std` pick of the same signal on the same starts,
  by month, with RD-02's section 9.2 uncertainty (items 1 to 7, `extended/pp_reading.py`, this family's honesty seed);
- **the denial ladder** (10, 25 and 50 %) on the eight group picks; **the placement on** at the Topstep standard group's
  two picks; the Focused Trader models not run (RD-05 G-5);
- R\* = P-14's U1 row and the best of P-14, P-15 and P-16 on each guarded measure, cited, labelled "another engine".

### 12.2 The menu

Per configuration: its stage-A grid, its picks with their 5-minute cells, the scorecards, the ladders, the exposures;
the flags of RD-05 12.6 and "hours unrecorded" (U-34), "price unverified: at the grid's ends" (U-33), "one seat"; the
count of 90 % intervals shown and that a tenth would exclude zero by chance. E-015's limits flag the menu only if
approved before the run's commit by a row of the `e015-limits:` form (E-104). **No cell is withheld for conduct**
(RD-05 4.7).

## 13. What a pass and a fail mean

- **CARRIED for a group** -- a development finding on a late-development block: the design (P-14 at T\* through
  `pi*_g` on `c*_g`) takes a registration id, its registered development test, the auditor and one confirmation (14).
  The carrying row says what is claimed (the lift, and its value through that protocol) and what is not (that the
  protocol beats another, that the firm beats another).
- **Closed at stage B** -- "no lift above the judged MDL worth the bar at this family's level", never "these firms or
  brackets do not work"; the family's judged block is not read for T\*.
- **Not carried at stage C** -- the first failing line named; the failure protocol applies to any failed identity or
  oracle, never to a line that simply did not pass.
- **The closure binds** (Stage 2 D-277's boundary): a later family on these signals, brackets, latencies or entry types
  names this one, says what changed, and is not judged on this judged block. The judged block is recorded as read for
  protocol choices on P-14 and P-16.

## 14. The confirmation, declared before any development read

- **The window:** NQ from 2026-07-17 (`config/windows.yaml`, `reserve`), not on disk, a purchase, the operator's; it
  would be NQ's fourth confirmation window (Stage 2 D-107, D-461). Other drafts target it; if any test reads it first,
  the lead records that before registration and the operator decides.
- **What it tests:** T\*'s lift on the window, one-sided at 0.05, by the adopted statistic, with K0 on its counts; each
  carried group's value line at the window's bound; the scorecard descriptive. **One confirmation serves every carried
  group**, since the trade set is common.
- **How much data:** at least six months, and at least the months at which the statistic has 80 % power for a lift equal
  to `L_J`, at T\*'s supply -- computed when a design is carried and written in the carrying row before any confirmation
  data exist. If that is more than the operator will buy, no confirmation is registered.

## 15. Seeds, fixed now and checked

| seed | status | role | what it draws |
|---|---|---|---|
| 20262430 | in use | `k0_choice` | 9.7's sign nulls on the choice block, keyed `[20262430, tau index, model index]` |
| 20262431 | in use | `k0_judged` | 10.2's sign nulls on the judged block, keyed `[20262431, model index]` |
| 20262432 | in use | `gate` | 10.4 item 1's gates, 500 paths, one seed for every group (paired) |
| 20262433 | in use | `ladder` | 12.1's payout-denial draws, keyed `[20262433, start index, request index]`, common to every pick |
| 20262434 | in use | `honesty` | 12.1's honesty series (RD-02 9.2), keyed `[20262434, 1, shape, h, n_w]`; the build's test `[20262434, 0, ...]` |
| 20262435 | in use | `build_toys` | the build's synthetic bars, chains and batteries (T-1 to T-12) |
| 20262436 | reserved, unused | -- | -- |
| 20262437 | reserved, unused | -- | -- |
| 20262438 | reserved, unused | -- | -- |
| 20262439 | reserved, unused | -- | -- |

**Nothing else draws.** The walks, the chains, the engine on historical trades, the composition, the value arms and the
statistic (a closed-form t) draw nothing.

**The timing measurement is not on these streams.** Step 3's time and memory are measured before it on synthetic
chains drawn from `numpy.random.default_rng([0, j])` -- seed 0, outside the block, its outputs discarded.

**The check, 2026-11-18 (UTC).** Word-bounded searches for the block's pattern (its seven-digit prefix and one digit),
every text file, the licensed data excluded: `git grep -IwnoE` on every local and remote ref (23 refs), the vendored
snapshot included; and `grep -rIlwE --exclude-dir=.git --exclude-dir=data` on the working files of the main tree, every
worktree under `%LOCALAPPDATA%\stage2-extended-wt\` and every clean-run checkout and log under
`%LOCALAPPDATA%\stage2-extended-runs\`. No hit before this file. **T-0** (`tests/test_f04_draft.py`) builds the block by
arithmetic, repeats the search over the tracked and working files of its checkout on every run, allows only this file and
its `DECLARED_USES`, and proves the scans work on a planted copy.

**Inherited, used only as their owners registered them:** P-14's gate seed 20261131 and P-16's 20261206 (the
identities); P-16's registered coin seed (its builder, D-521); U1's replay seeds (the identities).

## 16. Multiplicity and counting

### 16.1 The family's number and level

k is the next free program family number at the pin (13 at this text), the level one-sided 0.05 / (k (k + 1)), written
by the gatekeeper in the pinning row.

### 16.2 Every cell counted

The grid's factors: P-14's stops 6, P-16's 5; ratios 4; latencies 3; entry types 2; trade-set classes 2; session rules
3; mixes 2; sizing cells a mode 12 (6 risks x 2 policies), 144 a joined pair; configurations 19 (17 run, 2 repriced;
Appendix P), 13 evaluation and 15 funded modes; groups 4; two-corner configurations 15.

<!-- counted-cells: the rows below are summed by T-0 -->

| block | cells | basis |
|---|---|---|
| P-14 trade sets | 288 | 6 stops x 4 ratios x 3 latencies x 2 entry types x 2 classes |
| P-16 trade sets | 240 | 5 x 4 x 3 x 2 x 2, described |
| evaluation mode cells | 247104 | (144 + 120) entries-brackets x 3 session rules x 2 mixes x 12 sizing cells x 13 evaluation modes, at most |
| funded mode cells | 285120 | the same x 15 funded modes, at most |
| zero-lift mode cells | 290304 | P-14's 144 entries-brackets x 3 x 2 x 12 x 28 modes, at most |
| P-14 protocol cells | 2363904 | 144 x 3 x 2 x 144 x 19 configurations |
| P-16 protocol cells | 1969920 | 120 x 3 x 2 x 144 x 19, described |
| repriced protocol cells | 456192 | the 2 repriced configurations' cells of both signals, exact arithmetic |
| zero-lift journeys | 2363904 | one per P-14 protocol cell |
| K0 at stage B | 288 | at most one per P-14 trade set |
| judged lift tests | 1 | C1 on T\* |
| K0 at stage C | 1 | T\*'s judged counts |
| value lines | 4 | C2, one per group at most |
| gates | 4 | one per group pick at most |
| beside, configuration picks | 38 | 19 configurations x 2 signals |
| beside, 5-minute cells | 38 | one per configuration pick at most |
| beside, lenient corners | 30 | 15 two-corner configurations x 2 signals |
| beside, denial ladder | 24 | 8 group picks x 3 levels |
| beside, placement | 2 | the Topstep standard group's two picks |

<!-- end counted-cells -->

That is **at most 4,333,824 protocol cells** (2,363,904 of P-14's and 1,969,920 of P-16's, 456,192 of them repriced
by arithmetic), **528 trade sets**, **one judged lift test**, **at most 4 value lines and 4 gates**, and **at most 132
journeys beside**. A cell not allowed (6.3), identical by construction (`cap` where no consistency rule exists) or
killed (8.2) is counted all the same. A joining firm (RD-05 2.4) adds its configurations' cells by the same products and
a group, stated in its join row before stage A's commit; after that commit nothing joins.

### 16.3 One test reaches judgement; the family-wise error across firms

- **Within each firm** the selection (9.5) is made on the choice block only; **across firms** the trade set is common
  (9.4). So exactly one statistical test reaches the judged block: C1 on T\*, at the family's full level. The value
  lines and floors are not tests at a level: each is a fixed function of the bound.
- **The family-wise error across firms is the one test's level**: a false lift claims at most 0.05 / (k (k + 1)) for
  every group together, since no group can carry unless C1 passes. The selection among 528 trade sets and millions of
  protocol cells on the choice block costs power, not size (the judged block is not read by it).
- **Why not a trade set per firm.** Per-group trade sets would put up to four tests on the judged block, which (a) the
  house rule "one cell per family reaches judgement" does not allow, and (b) at Bonferroni's 0.05 / (182 J) would fall
  below the lowest level Q-126 calibrates (k = 20's) for J of 3 or more. Section 19 item 1 puts this to the lead.
- **The program's honesty sentence:** Stage 2's programs and this repository's families have read the judged block for
  these signals' own brackets (section 2); the development level is a screening threshold and the decision is carried
  by one confirmation on unread data, if the operator buys one.

## 17. The build: adapters, identities and tests (after the pin, before any run)

### 17.1 The code (in `extended/`, never in `vendor/`)

- `extended/fp_walks.py` -- the offers of both signals at every stop, ratio, latency and entry type through
  `extended/walker.py`; the news rule of 5.4; the pair rule for limits; the chain (5.5); read through `extended/reader.py`.
- `extended/fp_engine.py` -- F-A1 on RD-05's A-0 and adapters; F-A2's composition; the value arms (7.3).
- `extended/fp_pick.py` -- stage B's rules (9), reading stage A's files only.
- `extended/fp_stagec.py` -- C0, C1, C2, the floors, the verdict; the gate's constant-action table.
- `scripts/fp_rules.py`, `fp_walks.py`, `fp_grid.py`, `fp_pick.py`, `fp_judge.py`, `fp_beside.py`; `identity/fp_identity.py`.
- Every rule value read by key through RD-05's loaders (its 17.2); a test fails on a literal rule value in the code.

### 17.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 | `tests/test_f04_draft.py`: one F-04 declaration; sections 0 to 20 and Appendices P and C; the seed table and the block nowhere else, its scans' positive control; one judged-reads line, three purposes, none choosing; the counted cells against the factors and Appendix P; RD-05's and Q-126's pins as cited; the calendars' LF sha256; no dollar figure but the declared grids and the bar. **At the pin, added:** Appendix P's modes against RD-05's Appendix M, and every key 3.2 names against the merged record |
| T-1 | F-A1 with a scripted binary chain equals RD-05's A-0 with `BinaryDraw` on the same uniforms, account for account |
| T-2 | the walks on synthetic bars: latency moves the entry bar; a limit at the alert's price fills only on a trade through by a tick, is void when marketable at its live time, is cancelled at its window's end and at a news window's start; no fill inside a window; the forced flat at a window's first bar, both sides; the pair rule and the symmetric mirror (T-13's zero on a driftless walk) |
| T-3 | the chain: one position at a time, five minutes flat, a stood-aside trade keeping its slot; `one`, `all` and `cap` |
| T-4 | 6.5's sizing on hand-computed cells: the mix, the counting rule, the headroom cap, the room and the daily limit, the stand-aside, the flip |
| T-5 | the composition against a direct sequential replay on toy tables; censoring at the block's end; no index past the block's last session ever read (a planted later session refused) |
| T-6 | the value arms: the zero-lift arm's executed trades' mean shifted R zero exactly on a toy; `V` linear in the price; the interpolation of 9.3 |
| T-7 | stage B's rules on synthetic stage-A files: Kill B, the four-key order of 9.4, the strikes, per-group and per-configuration picks, P-16's rule; the pick refuses any input but stage A's and RD-05's files |
| T-8 | K0 on synthetic pairs: a lax statistic flagged, a sound one not, at the family's level |
| T-9 | U-33's and U-34's ends; the news windows derived from the key on a hand-built entry |
| T-10 | the menu: no P without its guard row; the 5-minute cell beside every pick; the flags |
| T-11 (`slow`, `heavy`) | 17.3's identities at 4 starts and a few hundred offers (reads the bars) |
| T-12 | the seeds of 15 only where 15 declares them (T-0's `DECLARED_USES`, extended by the build); tier-1 counts zero on toy runs and firing on a hand-broken router |

### 17.3 The identities (refusing; whole-window identities only from `identity/*.py`)

1. **Shared, owed by other items**, each met by a row of the `identity-holds: <id>` form at the run's commit or an
   ancestor, its cover unchanged: Q-05 (E-010), Q-80 (E-049), Q-93 with Q-100 (E-059), Q-101 (E-068), E-011's walker
   identity, RD-01's `firms_identity`, and **RD-05's `modes_coin_identity` and `modes_identity`** (its adapters are this
   family's), after the rules record's merge.
2. **`fp_identity`, item 1** (whole window, purpose `identity`): 5.2's walks at the registered widths, latency 5, market,
   news off -- P-16's `TRADES_SHA256`; P-14's A3 cache's walks, offer for offer, every column; P-14's registered trade
   list by its rung rule.
3. **`fp_identity`, item 2** (choice block): F-A1 at `TS-S/std` with every RD-05 addition at its Topstep setting against
   the vendored `CombineAccount` and `FundedAccount` driven by the same sized chain -- every attempt start, P-14 at its
   rung bracket, latency 5, market, both mixes, all twelve sizing cells of each mode, account for account: every end
   session, cause, fee and payout; only RD-05 13.1 (1)(d)'s listed differences allowed; and the composition against a
   direct sequential replay, start for start.
4. **Inside every run:** every executed trade is a chain trade of its trade set; `TS-N` equals `TS-S` but for fees;
   `cap` equals `all` where no consistency rule exists; corners equal where a term cannot bind; every tier-1 count zero.
   Any failure stops the step; the failure protocol applies.

## 18. Outputs, the run and its bounds

**Files**, each with its sidecar manifest through `extended.results.write_result` (`prereg_id` `F-04`, the pinning row,
the identity rows, every seed, every parameter, the record's commit and keys, the cell counts as run,
`exploratory=False`): `results/fp_rules.csv` (step 0); `results/fp_tradesets.csv` and `results/fp_grid_<configuration>.csv`,
one per configuration (step 2); `results/fp_pick.csv` (step 3); `results/fp_judgement.csv` (step 4);
`results/fp_beside.csv` and `results/fp_menu.csv` (step 5).

**The run, in steps, each from a clean checkout of a named commit (`scripts/run_clean.py`), one heavy job on the
machine under `run.lock`, watched to its exit, each step only after the lead's row records the one before:**

| step | what | weight | workers | time bound | memory bound (summed) | measured before it on |
|---|---|---|---|---|---|---|
| 0 | the rules arithmetic: the allowed grid (6.3), the news windows, U-33 and U-34, the counts; reads RD-05's step-0 file | light | 1 | 1 hour | 0.5 GB | -- |
| 1 | the identities (17.3) | heavy | 1 | 8 hours | 2.5 GB | E-011's and E-010's recorded peaks |
| 2 | stage A: the walks on the choice block, then the mode cells and journeys | heavy | at most 2 | 48 hours | 2.5 GB | synthetic chains on seed 0 (15), outputs discarded |
| 3 | stage B and its K0 (no bar) | heavy | 1 | 4 hours | 1 GB | K0 on synthetic pairs |
| 4 | stage C: C0, C1, C2, the floors | heavy | 1 | 24 hours | 2.5 GB | the gate's recorded peaks at one seat |
| 5 | the scorecard beside, after the verdict row | heavy | 1 | 12 hours | 2.5 GB | step 2's measurement |

Each step's memory bound is the job's summed working set (`extended/procmem.py` per process, summed by the parent), one
BLAS thread a process. **A step whose measurement exceeds its bound is not started; a step exceeding it while running
is stopped; no grid is thinned and no worker added at run time** -- a smaller grid is a new family.

**Waits, before step 0:** the pin; the rules record (Q-136, Q-136b) merged and RD-05's build and step 0 on record; every
shared identity re-held at a commit containing the merge; this family's build with T-0 to T-12 and the red team's read
of it. **Before step 3:** section 11's items 1 and 2.

## 19. Open before the pin

**The lead's:**

1. **One common trade set, or one per firm.** This text judges one P-14 trade set for every firm (9.4, 16.3): the house
   rule allows one judged cell, and Bonferroni over three or four per-firm tests would fall below Q-126's calibrated
   levels. The cost: a firm whose contract would spend a different bracket best is judged on the common one (its own
   best is still printed in stage A). A per-firm trade set needs both a ruling on the one-cell rule and a calibration at
   levels below k = 20's.
2. **What a carried design claims** (1.2): the reading that a carried design's sizing protocol rides as the vehicle of a
   tested lift, unclaimed, under E-008 with E-023 (1); and that several groups may carry designs sharing one lift, each
   its own registration id, one confirmation for all (14).
3. **The statistic's domain** (11 item 4): whether K0 on T\*'s own magnitudes and counts suffices for a trade set whose
   values are not P-16's `win1` or `net3`, or whether Q-126's validation must be extended first.
4. **Spending k = 13** on a family whose prior is no lift (E-125). The alternative, offered not urged: stages A and B as
   written and the picks read once on the judged block as a described reading (an RD, no k, no pass line) -- the firm
   comparison out of sample, nothing carried.
5. **The value bar**: $500 at month 12 per start, F-03's C2 bar carried; the operator, not a quant, may want to set it
   (the lead asks with the bar explained, or keeps this default).
6. **News at every firm** (5.4): the windows come from My Funded Futures' verified rule because Topstep's own entry is
   `changed`; the lead confirms that reading of the operator's R-1, and that this changes Topstep's trades from U1's (the
   identity is held with the rule off, 5.2).
7. **Hours**: no trading-hours entry in the record for My Funded Futures or Lucid; U-34 brackets it. A rules-verifier
   read would remove a corner.
8. **CHARTER section 4 and the feature-rules skill** name five minutes from alert to order; the operator's R-3 makes 3 and
   2 minutes counted variants of this family. The lead's row records the ruling; whether CHARTER and the skill are
   amended is the lead's.
9. **The judged block's whole grid**: not computed here (1.3); a later described reading may print it, citing this
   family's verdict.
10. **Output size**: about 228,000 rows a configuration in step 2's files; whether they are committed whole or kept beside
    the clean run with their hashes in the row.
11. **Single seat** (7.2): the lead confirms that a one-seat journey is the unit for a protocol comparison across firms,
    with seats left to RD-03; and that the gate (10.4 item 1) can be configured to one seat and a constant-action table --
    if the vendored policy interface cannot express it, the build stops and reports.
12. **LucidFlex's corners**: `LU40` takes RD-01's `LU` corners and `LU50` RD-05 5.2's live-move corner; the red team checks.

**The operator's:** the bar (item 5) if the lead asks; the captures of Alpha Futures' and Lucid's terms (joining only by
RD-05 2.4, before stage A's commit); any purchase of the confirmation window, only if something carries.

## 20. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest,
and recorded in its own decision row -- never in this file.)*

---

## Appendix P -- the configurations and groups, in run order

| index | configuration | group | evaluation mode | funded mode | run | corners |
|---|---|---|---|---|---|---|
| 0 | `TS-S/std` | Topstep standard | `TS` | `TS/std` | run | single |
| 1 | `TS-S/con` | Topstep standard | `TS` | `TS/con` | run | single |
| 2 | `TS-N/std` | Topstep standard | `TS` | `TS/std` | repriced | single |
| 3 | `TS-N/con` | Topstep standard | `TS` | `TS/con` | repriced | single |
| 4 | `L6/std` | Topstep Labs | `L6` | `L6/std` | run | two |
| 5 | `L6/con` | Topstep Labs | `L6` | `L6/con` | run | two |
| 6 | `L10/day` | Topstep Labs | `L10` | `L10/day` | run | two |
| 7 | `L10/5wd` | Topstep Labs | `L10` | `L10/5wd` | run | two |
| 8 | `L11/day` | Topstep Labs | `L11` | `L11/day` | run | two |
| 9 | `L11/5wd` | Topstep Labs | `L11` | `L11/5wd` | run | two |
| 10 | `RE` | My Funded Futures | `RE` | `RE` | run | two |
| 11 | `RED` | My Funded Futures | `RED` | `RED` | run | two |
| 12 | `RI` | My Funded Futures | `RI` | `RI` | run | two |
| 13 | `PRO` | My Funded Futures | `PRO` | `PRO` | run | two |
| 14 | `PRO1` | My Funded Futures | `PRO1` | `PRO` | run | two |
| 15 | `B20` | My Funded Futures | `B20` | `B20` | run | two |
| 16 | `B15` | My Funded Futures | `B15` | `B15` | run | two |
| 17 | `LU40` | LucidFlex | `LU40` | `LU` | run | two |
| 18 | `LU50` | LucidFlex | `LU50` | `LU` | run | two |

The plans, modes and terms are RD-05 section 2.1's and 2.2's. `TS/con` and `L6/con` are read here though RD-05's part F
leaves them out: its reason (the registered tables solve the Standard path, G-1) does not reach a fixed protocol. The
corners are RD-05 5.2's part-F column at a single seat (U-14 moot, checked); the choice is made at the strict corner.

## Appendix C -- the drafter's choices, each with its reason

| # | choice | where | reason |
|---|---|---|---|
| 1 | one file in three stages | 1.3 | the pick rule must exist before the grid it picks from |
| 2 | only P-14's trade set is tested; every sizing component described | 1.2 | E-008 with E-023 (1) and E-134 (1); P-16 is a coin |
| 3 | one trade set common to every firm | 9.4, 16.3 | one judged cell, inside Q-126's calibrated levels |
| 4 | T\* ranked by the number of firms that can spend it, then the sum of their values | 9.4 | a common bracket fair to every firm, not to one |
| 5 | value by shifting executed trades, zero-lift and lift-L arms | 7.3 | Stage 2's convention of shifted outcomes; no per-firm value map exists |
| 6 | stage B's value by linear interpolation between stage A's two arms | 9.3 | the bound is unknown at stage A; the judged value uses full arms |
| 7 | `Lstar = lhat_A - MDL50_J` | 9.2 | the bound the judged block would give if the lift held; Kill B where it is not positive |
| 8 | a single seat | 7.2 | a protocol compared across firms on one account; seats are RD-03's |
| 9 | the coin twin as the walked mirror, `x_i` exact | 5.3 | Q-108's estimand; no seed |
| 10 | every walk made anew; the caches as references | 5.2 | one code path for every bracket's trade and twin |
| 11 | the chain state-free | 5.5 | the lift's trade set fixed by the walks alone |
| 12 | `cap` as a session rule | 6.1, 6.4 | the operator's "when to stop" where a consistency rule binds |
| 13 | minis-only dropped | 6.1 | dominated by `mixed` except where a micro counts as a mini, which RD-05's U-26 already reads |
| 14 | the limit at the alert's price, working 30 minutes | 6.1 | no free offset; one window, fixed |
| 15 | the pair rule with a 10 % cap for limits | 5.2 | feature-rules section 3; the resting fill's bias declared, not left |
| 16 | the news window from the verified My Funded Futures key at every firm | 5.4 | the operator's R-1; Topstep's entry is `changed` |
| 17 | U-33 at the least favourable end | 3.2 | prices move cash only; no price inside the grid chosen |
| 18 | U-34 for unrecorded hours | 3.2 | no free choice; both corners printed |
| 19 | the stop widths 50, 70, 100, 150, 200 and `rung` | 6.1 | the registered rungs and a step either side, inside RD-05 part B's widths |
| 20 | K0 on the pick's own pairs | 9.7, 10.2 | F-03's form; the statistic's domain is P-16's values |
| 21 | the bar $500 at month 12 per start | 10.3 | F-03's C2 bar, a year's value |
| 22 | the judged block's whole grid not computed | 1.3 | the judged block read once, for the pick |
| 23 | `TS/con` and `L6/con` read | Appendix P | G-1's reason does not reach a fixed protocol |
| 24 | ties toward latency 5 and market entries | 9.4, 9.5 | the reference first, as the operator asked it reported |
