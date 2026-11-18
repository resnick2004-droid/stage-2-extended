# F-04 (draft): the per-firm execution protocol -- P-14's and P-16's registered signals re-bracketed, re-timed and re-sized across each $50K plan's allowed grid; the whole grid described on the choice block, one trade set and one protocol per firm group picked by a declared rule, judged once on its trades in a fixed sequence (family FP)

**Status: the second text (TASK_QUEUE Q-141, corrective cycle 1 of 2), not pinned.** Drafted on `wt/wt-scout` with
master merged at 4acf171 (E-202). It goes to the red team's re-read, then the prereg-gatekeeper. At the pin the file is
renamed `prereg/F-04_firm_protocol.md` and nothing else changes; the pinning row names the commit and the sha256 of its
LF text. **The program family number is not assigned at the pin: it is assigned by the stage-B row, and only if stage B
sends at least one trade set to stage C** (16.1); until then every level is the provisional level at k = 13. Nothing
declared is edited after the pin: a change is a new family under a new row.

**Its text's history.** The first text (Q-141; wt/wt-scout 675799c, LF sha256
`5e158e7d601df9d402df6fabfa401f660aedd93c6715c0b2417ee884720d951f`) was read by the red team (Q-141r,
`docs/reviews/DRAFT_F-04_2026-11-18.md`: must be re-declared; three blockers, eleven should-fix items, twelve notes).
**This text answers every finding as the lead ruled them**: the exact seedless twin for limit entries (B-1); P-16's
registered timing kept and P-14's latency in clock minutes with a named identity difference (B-2); the chain in fill
order, one working order or position at a time (B-3); a trade set per firm group tested in a fixed sequence at the
family's full level (S-1); the reduction ladder, the per-trade pairs file, the count kill, the stage-A wait, the flip
gate table and the number assigned at stage B (S-4 to S-9). Appendix A maps every finding to its place.

**When this text was written, nothing of it had been built, no engine had been run for it, no bar or walk had been
read for it, and no outcome of any protocol, plan or trade set had been computed or read.** It was written before
RD-04 was read (no `RD-04 read: step 2` row exists at its writing) and before any step of RD-05 ran; the pinning row
attests both again at the pin (S-10; 19). Anything chosen after a reading is exploratory and reported apart (section 20).

**The operator's direction (2026-11-18, E-202 (1)).** The registered trades were built around Topstep's conditions;
run unchanged on another firm they are not a fair reading of it ("MFF has a 4 mini contract limit on one of the accounts
at the start, topstep only has 2"). Two steps were approved: (1) a described reading -- the registered signals' trades
re-sized and re-bracketed across each plan's full allowed grid, the whole grid printed per firm, nothing picked; (2) a
declared family that picks the best protocol per firm on the choice block and judges it once on the judged block.
**This file is both, as stages of one family** (1.3): stage A is step 1 on the choice block; stages B and C are step 2.

**The operator's rulings of the same day (E-202 (2)), written into the grid as declared:** (R-1) **news** -- no entry
and no fill inside a verified news window at every firm and in every protocol, a position open at a window's start
flattened under E-200 R-1; (R-2) **hours** -- executions at every hour of the day, overnight included wherever a plan
allows it; (R-3) **order latency** -- the alert-to-order latency a protocol parameter, 5 minutes the reference with 3 and
2 minutes as counted variants, the 5-minute cell reported beside every pick (for P-14; P-16's entries are scheduled, B-2);
(R-4) **entry type** -- resting limit entries beside market entries, live at the latency, filled only on a trade through
by one tick, cancelled at a news window's start, at Topstep as at every other firm. CHARTER section 4, CLAUDE.md and
the feature-rules skill are amended for R-3 by the lead's row that amends them (S-11); that row precedes the pin.

| field | value |
|---|---|
| family | FP: the per-firm execution protocol -- for each $50K plan, the bracket (stop width, reward-to-risk), the entry (latency for P-14, market or limit), the session rule, the instrument mix and each mode's risk and steady-or-flip policy, applied to P-14's and P-16's registered signals |
| id | F-04 (`prereg/F-04_firm_protocol.md` at the pin); every result's `prereg_id` is `F-04` |
| program family number k | **assigned by the stage-B row** -- the next free number then (13 if nothing else is pinned first) -- and only if stage B sends a trade set to stage C; otherwise the family retires unspent (F-02's precedent, E-094, E-095) |
| level | one-sided **0.05 / (k (k + 1))**: provisionally 0.05 / 182 at k = 13 |
| stages | A the whole grid on the choice block, described, no pick (8); B the picks by declared rules on stage A's files alone (9); C the judgement of each group's trade set in a fixed sequence on the judged block (10); the scorecard beside (12) |
| what can be carried | **only P-14's signal at a group's picked trade set T_g**, spent through the group's picked protocol, when T_g's lift over its coin twin passes C1 in the fixed sequence and its value at that bound through the plan's own contract clears the bar (C2), every floor holding (section 1) |
| what is only described | every sizing, mix, policy, session-state and class comparison (E-023 (1), E-134 (1)); every P-16 protocol; the comparison of firms; the stage-A grid |
| base | P-14 (A3-BRK30-CB20) and P-16 (`rc_s150_all_nr`), their registered offers and sides; R\* = P-14's U1 row beside (another engine: 7.4) |
| plans | 19 configurations in four groups (Appendix P): Topstep standard, Topstep Labs, My Funded Futures, LucidFlex -- RD-05's plans by reference; Alpha Futures and Lucid's other plans join only by RD-05 section 2.4, before stage A's commit |
| rules | RD-05's catalogue by reference (its sections 2 to 5, Appendix R): Stage 2's verified ledger, the vendored Lucid ledger, the rules record at `wt/wt-firms` 1c9f34f as merged; read by key, never typed |
| development data | NQ 1-minute bars 2020-01-02 to 2026-07-16 only, through `extended/reader.py`; stages A and B on the choice block 2020-01-02 to 2023-12-29 alone; stage C on the judged block 2024-01-02 to 2026-07-16 |
| judged reads | three purposes, once each (4.4) |
| pass line | C1 each distinct T_g's lift over its coin twin, one-sided at the family's full level by the adopted one-sample statistic (Q-126, 11), tested in a fixed sequence that stops at the first failure; C2 per group, the lift's value at that bound through the group's protocol at least $500 at month 12 per start; the floors of 10.4; the scorecard beside, never the pass line |
| seeds | a block of ten, six in use and four reserved (15) |
| confirmation | NQ from 2026-07-17, a purchase, one line per distinct carried T_g (14) |
| `confirmation_tests_on_this_market` | 3 spent (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`); this family adds none and reads no NQ from 2026-07-17 |

---

## 0. In plain words (for the operator)

**What a protocol is.** How the same signal is traded at one firm: how wide the stop is and how far the target; for
P-14, how soon after the alert the order goes in (5, 3 or 2 minutes); whether it is a market order or a resting limit at
the alert's price; whether the account takes one trade a day, every trade, or stops for the day once a big day would
break the plan's consistency rule; micros only or minis first; and, separately in the evaluation and in the funded
account, how many dollars are risked per trade and whether the first sessions are traded large to try to pass or reach
the first payout in a day or two ("flip"). Each plan's own caps decide which of these are allowed at all.

**What happens.**

- **Stage A (described, nothing picked).** Every allowed protocol is run, plan by plan, on 2020 to 2023 only, and the
  grid is printed: passes, payouts, money and time per start day, and -- for P-14 -- how much its side beats a fair coin
  on the same entries at each bracket.
- **Stage B (the picks, by a rule written now).** From stage A's files alone: for each firm group, the P-14 trade set
  (bracket, latency, entry type) that group can spend best, and the protocol that spends it; P-16's best protocol per
  firm, picked the same way, as a description.
- **Stage C (the judgement, once).** On 2024 to mid-2026, never read before by this family: does P-14's side at each
  group's trade set beat the coin by more than chance at the program's strict level? The trade sets are tested one after
  another in an order fixed in advance, each at the full level, stopping at the first that fails -- so the chance of a
  false pass across all firms stays at that one level. For each that passes: is the edge, at its cautious lower bound,
  worth at least $500 a year through that firm's protocol? Each firm's journey is shown beside.

**What can come out, honestly.** Only P-14 can pass anything, because only P-14 has a side; P-16 chooses its side by
coin, so its edge is zero by construction and its protocols are only described. P-14's average trade is negative after
costs at every target on its registered brackets (E-125): its money so far has been the contract's, not the trades'. And
P-14's own hours and rungs were chosen by Stage 2 over the whole window, 2024 to 2026 included, so a pass here is a
screen, not proof: only the confirmation on unread data would be a clean test. **The expected result is that nothing
carries**; the most useful product may be stage A's grid and the firm-by-firm picks read out of sample -- described, not
proven. A "no" is a valid close. The firm comparison itself (which firm is best) is never a test: it is shown with its
uncertainty.

**What it costs.** A family number is spent only if stage B finds a trade set worth judging; otherwise none is.

## 0.1 Where the brief's questions are answered

| the brief's question (Q-141) | where |
|---|---|
| what a protocol is: size or risk, R:R and bracket, MNQ versus NQ, steady versus flip, stand-aside rules, when to stop; each grid per plan from its own caps | 6 (every parameter, classed); 6.3 (the allowed grid, from RD-05 part B) |
| the operator's rulings: news, hours, latency, entry type | 5.4, 6.1, 6.2, 16 |
| brackets change the trades: walks at each bracket, which are re-used, their identity | 5 |
| leakage: one file or two | 1.3, 4 |
| the pass line, against CHARTER section 2, E-008 and E-023; what carries and what is only described | 1 |
| the calibrated statistic: what stages A to C wait on | 11 |
| multiplicity: every cell counted, selection within firm, family-wise error across firms | 16 |
| seeds: a block of ten, unused anywhere | 15 |
| bounds: memory, one heavy run, a time bound per step, the reduction ladder | 18 |
| the items for the lead or the operator | 19 |

## 1. The question, and what can be carried (CHARTER section 2; E-008, E-023, E-134, E-196, E-202)

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
  different trade with its own outcome, and its coin twin at that bracket is defined in 5.3 (the walked mirror for a
  market entry; the exact seedless twin on the resting side's fills for a limit entry). So a P-14 **trade set** -- the
  signal at one stop, ratio, latency and entry type, under a state-free class (6.4) -- has a lift that can be tested.
  That is the only thing this family tests.
- **A size, a mix, a policy, a session-state rule and the class add no claimed value.** *This text's reading of E-134
  (1)* (whose row reads "routed, bought or kept -- purchases, seats, reactivation, stop rules"): a lever that changes
  which offered trades are sized or kept but adds no offered trade is described, never carried. The class `one` keeps a
  subset of the offers; its value as a filter would be an E-023 (2) claim, and none is made: the side's lift on that
  subset is what is tested. No row of this family says one sizing, policy, mix or class beats another.
- **What a carried design is.** "P-14's signal at the trade set T_g, traded through the protocol pi\*_g on the plan
  c\*_g" for a firm group g. It is carried because (C1) its trades' lift passes and (C2) that lift, at its bound, is
  worth at least the bar **through pi\*_g on c\*_g's contract**. The protocol is the vehicle in which the tested lift is
  priced, as a registered design carries its state table. The registration freezes pi\*_g, claims only the lift, and
  its confirmation tests only the lift, the protocol's scorecard descriptive (the red team's reading of section 19 item
  2). **It is not claimed better than any other protocol**, and the carrying row says so.
- **P-16 can carry nothing.** Its side is a seeded coin (its registration: "a coin carries no information"), so its
  lift over a coin twin is zero by construction at every bracket -- for market entries by the walked mirror, and for
  limit entries **under the exact twin of 5.3 only**: the walked-mirror form for a limit is not a coin twin and its mean
  is not zero in expectation (B-1); it is printed as a placebo of the mechanics (8.1 item 1), never read as P-16's lift.
- **The firm comparison is described.** Each group's T_g is judged on its own lift (C1), its value through its own
  protocol (C2); which firm's journey is best is a scorecard comparison with its uncertainty (12), never a test.
- **Not claimed either:** that T_g beats P-14's registered bracket, or that one group's T_g beats another's. C1 tests a
  T_g's lift above zero, nothing else.

### 1.3 Why one file, in three stages (the brief's leakage question)

One file, because the pick must be written before the grid it picks from exists. With two files, the second's pick rule
would be written after the first's grid was printed -- a choice after a look -- unless both were pinned together, and two
files pinned together are one declaration. In one file: stage A's grid is computed on the choice block only and picks
nothing; stage B's rules are pinned before stage A runs and read stage A's files alone; stage C reads the judged block
once, for the picks. The operator's step 1 becomes stage A on the choice block; **the judged block's whole grid is never
computed by this family** (19 item 9).

## 2. Prior exposure: what has already read these signals, brackets and plans

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| Stage 2's A3 screens and P-14's registration (Stage 2 D-490, D-491, D-499, D-501, D-512) | A1's mechanical patterns against the clock's coin; the rungs; P-14's cell, chosen from N = 370 trials (its multiplicity plan); its gate | the whole development window | the 12.5- and 25-point rungs kept, the 50-point rung's far targets not resolving (D-491); P-14 registered | **the judged block has been read for P-14's side at its own rungs** by Stage 2's screens (the drafter did not open those files); the 200-tick stop's resolution is expected to fail at far targets |
| **P-14's rung map** (`vendor/stage2/results/a3_resolution_map.csv`, by `scripts/a3_resolution_map.py`; `config/atlas_a3.yaml`) | each event hour's stop: the widest rung whose 1:1 row is at most 5 % unresolved overall and in every year; an hour with no rung trades nothing (`atlas_a3.py`) | **the whole development window, 2020-01-01 to 2026-07-16** | the map P-14 trades | the `rung` stop and **P-14's set of trading hours are functions of judged-block outcomes**; for a `rung` trade set the judged resolution floor is partly met by construction. A choice-block-only map is read beside (8.1 item 5) |
| **P-16's mark cutoff** (`resolved_coin.mark_resolution`, Stage 2 D-525) | marks admitted by their unresolved share at 150 ticks | **the whole window** | P-16's marks | P-16's offers depend on the judged block; descriptive here |
| U1 (Stage 2 D-620), Q-05 (E-010), Q-44 (E-201) | P-14's and P-16's journeys, five seats, their state tables | all starts | the reference rows | R\* beside, another engine (7.4) |
| Q-18's stress checks (E-125) | P-14's trades | the whole window | P-14's mean trade negative at every R (in words, E-125) | the prior: no lift is expected |
| Q-108 and Q-126 (E-115, E-161, E-187) | sign-flip nulls on P-16's judged pairs | the judged block (pair magnitudes under nulls) | a calibration, not an outcome of P-14 | the statistic's domain (11) |
| F-03 (E-192) | P-16's overnight offers | the choice block | closed at stage B | none on these trade sets |
| RD-01, RD-03 (pinned; RD-03 built and merged, E-202 (3)); RD-05 (pinned, E-200; not built) | the registered trades on these plans; the coin maps; part B's sizing arithmetic | all starts (part F) | nothing on master | stage B reads RD-05's step-0 arithmetic only (k_E, k_F, r_flip, b\*, part B's allowed set): rules arithmetic, not an outcome. **No coin-map cell or part-F row of RD-05 is used as a bar or a rule here** (RD-05 section 14, its N4); RD-05's part F is "Topstep's protocol on firm X, a reference only" (E-202 (1)) |
| program U's nine families | P on the late block | starts from 2024 | all closed | the judged block is late development, not out of sample |

**So C1's level is nominal** (the red team's S-2): P-14's cell, its hours, its rung map and P-16's marks were chosen
with the judged block read. A C1 pass at the family's level is a screen at a nominal size; **the confirmation (14) is
the only clean test**, and the verdict row and every carrying row say so beside the verdict (10.5, 13).

**Never run:** P-14's signal at any stop but its rungs, at a latency of 3 or 2 minutes, or as a limit entry; P-16's at
any stop but 150 ticks or as a limit entry; any fixed-protocol single-seat journey on any plan.

**The drafter's reads (disclosed).** For the first text as it listed them; for this text, in addition, the red team's
note whole and E-201, E-202. **No result file of either repository was opened.** The seed search printed counts only.

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
- **The news rule at every firm** (R-1; 5.4): where RD-05 applies a firm's news rule only at an account a verified key
  reaches, this family applies the verified window at every account of every plan. Topstep's own window entry
  (`tier1_news_events_restriction`) has status `changed` and is not loaded (RD-05 4.7 item 1); the Labs caps
  (`labs.50k_static.tier1_news_cap`, `labs.010_011_50k_dpp.tier1_news_cap`) take their windows from that entry or are
  unstated, so they are not loaded either, and **R-1 -- the operator's rule for every firm -- supersedes them**. The
  windows come from the verified `mffu.news_tier1_rule`, its minutes derived from the entry, never typed (19 item 6).
- **Hours** (R-2; 6.2): every hour each signal offers, overnight included, where the plan's hours allow. Stage 2's
  verified `trading_hours` gives Topstep's and, by RD-05's U-13 form, Labs'; **My Funded Futures' and Lucid's hours have
  no entry in the record** -- U-34 below, and 19 item 7.
- **U-33. An unverified evaluation price in a journey** (`labs.010_50k_dpp_eod.eval_fee` and My Funded Futures'
  unverified prices, RD-05 5.2's U-2 rows). Purchases do not depend on the price (the bankroll unbound), so every
  journey measure is exact arithmetic in it and is printed at both ends of RD-05's U-2 grid ($25 and $500). **A rule of
  this family reads a quantity at the end that makes it least favourable to the design**: the value V (7.3) at the end
  where V is smallest (V is linear in the price, so one end), P and every user measure at the higher price. No price
  inside the grid is chosen.
- **U-34. A plan whose record states no trading hours** -- both ends: strict, the plan trades only the hours of the
  regular session of Stage 2's verified `trading_hours` and no overnight offer is taken; lenient, Topstep's verified
  hours whole. A difference the corners show is printed, labelled "hours unrecorded".
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
- No warm-up is needed: no feature is computed; each signal's offers use only their own session's closed bars, as their
  registered builders make them (5.1).
- **A session** in this text is a trading day, from 17:00 CT to the walk's end -- never the walker's FV3 sessions
  (17:00, 19:00, 08:30, 13:00 CT), which only time its breakeven move (the red team's N-7).

### 4.2 The seal, mechanically

- **Stage A's arrays hold choice-block sessions only.** The walks of stage A are made from choice-block bars (no tag);
  the engine's draw arrays end at 2023-12-29, so no attempt, start or journey of stage A can reach a later session --
  an attempt or a journey still open at the block's last session is censored there (RD-05 9.4's convention: its cash to
  that session counted, the censored share printed). Every trade is intraday, so no purge or embargo is needed.
- **Stage B reads stage A's files (18) and RD-05's step-0 file only**: no bar, no walk. Its script refuses any other
  input, and checks each input's sha256 against its manifest.
- **Stage C reads the judged block** under the purposes of 4.4, from a clean checkout of a committed commit, once per
  purpose (a rerun only under `repeat=`, E-053).
- **The judged block's MDL and predicted trade count are computed from the choice block** (9.2): the judged block's
  trade count is never read before stage C (the chain's count depends on exits, an outcome).
- **The identities' whole-window reads** (17.3 item 2) write and print only equality checks and hashes: no lift, mean,
  count of wins or journey of the judged block (the red team's S-10).

### 4.3 The unit and the horizons

A start is one session of a block taken as a fresh user (7.2). For each measure of horizon h, the starts are the
block's sessions with h sessions left in the same block (RD-03 section 5's table of horizons, carried); a month is 21
sessions.

### 4.4 The judged block's reads

- **Judged-block reads:** `fp_judgement`, `fp_gate_floor`, `fp_scorecard_beside`

- `fp_judgement`: stage C's walks of each T_g's offers on the judged block, C0, C1 in the fixed sequence, C2 and the
  floors of 10.4 but the gate;
- `fp_gate_floor`: the gates of 10.4 item 1;
- `fp_scorecard_beside`: after the verdict row, the walks of every other pick's trade set and of the 5-minute cells
  (12.1), and every journey beside.

None is a choosing or fitting purpose (T-0). The identities run under the purpose `identity` and their own row.

## 5. The signals, the walks, the coin twin and the news rule (brackets change the trades)

### 5.1 The offers, and their timing

- **P-14:** its registered events and sides as Stage 2's builder makes them (A3-BRK30's 30-minute breakouts from A1's
  walk cache, its side rule, its news cuts; `atlas_a3`, imported). **Which offers count at every stop** (the red team's
  S-3): exactly P-14's registered offers -- the events at the hours its registered rung map trades -- at every stop of
  the grid; the rung map's hour filter is applied at every stop (an hour with no rung trades nothing at any stop), and
  the map gives the width only at `s = rung`. So the offer population is the same at every stop, and the stop is the
  only change. **Its alert** is the breakout bar's close (the alert slot of Stage 2's `entry_bar` call); **its latency L
  is counted in clock minutes**: a market entry fills at the open of the first present bar at or after alert + L (the
  walker's market rule), a limit goes live at alert + L.
- **P-16:** its registered marks and coin sides (`rc_s150_all_nr`'s builder; its registered coin seed, inherited) --
  the marks its registered cutoff admits at 150 ticks, the same marks at every stop. **Its timing is its registered
  convention and has no latency axis** (the lead's ruling on B-2): the mark and the side are known in advance, so the
  alert is sent five minutes before the mark and the order goes live at the mark -- the walker's market order live at the
  mark, delay 0, as `identity/walker_identity.py` runs it; a limit goes live at the mark.

### 5.2 The walks: how they are made, which are re-used, and their identity

- **Made by one code path:** this repository's walker, `extended/walker.py`, preset `STAGE2` (E-011: Stage 2's walk for
  market entries, P-16's pinned trades reproduced), every offer walked at every stop of the grid and every ratio.
  - **Market entries:** both sides (`walk_pair`), so each trade and its twin come from the same walk.
  - **Limit entries:** the resting side's limit walked alone (5.3), with the walker's per-trade fill-bar rule
    (`fill_bar="declared"`: a stop touch on the fill bar a loss, a target touch not counted), which is the same whatever
    the signal's side; and, for the diagnostic of 8.1 item 1 only, the walked-mirror pair (`fill_bar="pair"`,
    `mirror_booking="symmetric"`).
- **Re-used, as references only.** No cached walk is an input: every walk is made anew so that every bracket's trade
  and twin share one code path. Stage 2's cached walks are the identity's references (17.3 item 2):
  - at P-16's 150 ticks, market, delay 0 at the mark: P-16's `TRADES_SHA256` (E-011, re-held);
  - at P-14's rungs, market, L = 5, the news rule of 5.4 off: the A3 cache's walks of P-14's offers, every column the
    cache holds, offer for offer, against Stage 2's `entry_bar` convention (the sixth present bar after the alert slot,
    `fast_walk.entry_bar(o, t, 5, last)`). **The allowed differences are named: an offer with at least one missing bar in
    the five minutes after its alert**, where the clock-minute entry and the five-present-bars entry differ. Each such
    offer is counted and printed by hour and year; **any other difference refuses**; and P-14's registered trade list is
    rebuilt from the cache's walks by its rung rule.
- **The new walks** (other stops, latencies 3 and 2, limit entries, the news rule on) have no Stage 2 file to match;
  they rest on the identity's code path, the walker's synthetic tests (`tests/test_walker*.py`, T-13's mirror zero) and
  T-2 (17.2), which holds a missing-bar case.
- **What a walk records** (the walker's `Trade`): fill or why not (void, cancelled, refused by news, not placed by the
  chain), kind (stop, target, flatten, breakeven, ambiguous in the diagnostic), exit slot, gross and net R per
  micro-equivalent (Stage 2's costs at the stop, `atlas_a3.fee_by_stop`), MAE; the breakeven move as `STAGE2` has it. Per
  bracket the unresolved (flatten) share and the breakeven share are printed. The walk ends at `STAGE2`'s last bar --
  the bar ending 15:08 CT, a flatten priced at the worst of the bars ending 15:08 to 15:10 less two ticks (the red team's
  N-6) -- or at a news window's start (5.4).

### 5.3 The coin twin and the estimand

- **Market entries.** For a trade i the pair difference is `x_i = (net_R(side) - net_R(mirror)) / 2` at the trade's own
  bracket (Q-108 section 2.1's estimand, on net R per micro-equivalent): with a market entry the population and the fill
  do not depend on the side and the mirror pays the same entry tick and fees, so `x_i` is the trade's outcome less a
  fair coin's expected outcome on the same entry, exactly, with no seed. **The walked mirror is the twin for market
  entries only.**
- **Limit entries: the exact seedless twin on the offer population** (the lead's ruling on B-1; the red team's option
  (a)). At an offer's live time the limit price P is the alert's price; a buy limit at P is void if the price at live is
  at or below P, a sell limit if it is at or above P. So **at most one side's limit can rest**: the **resting side**
  (none when the price at live equals P: the offer is void for both sides, out of the population). Let `n_i` be the
  resting side's limit outcome in net R (its fill, its walk at the bracket, the fill-bar rule above), and `s_i = +1`
  when the signal's side is the resting side, `-1` otherwise. Then **`x_i = s_i x n_i / 2`** over the trade set's
  resting-side fills: a fair coin rests on the resting side with probability one half and is void otherwise, so its
  expected outcome per offer is `n_i / 2`, and the signal's is `n_i` when `s_i = +1` and zero when it is void. Its
  expectation is zero for any coin side, whatever the price dynamics.
  - The chain for a limit trade set is built on the resting side's fills (5.5), which do not depend on the signal's
    side; an offer whose signal side is void keeps its slot, as a stood-aside trade does, and the account takes no trade
    there.
  - **If a limit trade set cannot be given the exact twin** -- the build cannot compute the resting side or `n_i` for
    it -- it is **described only and never eligible** (8.2).
- **The lift** of a trade set is the mean of `x_i`; the statistic reads its session sums on the block's calendar (11).
  For P-16, `x_i` has expectation zero by construction under this section's twin for each entry type (the walked mirror
  for market entries, the exact form for limits) -- **not** under the walked-mirror form for limits, which is not a coin
  twin (8.1 item 1's diagnostic); its mean is printed as a check, never a reading.

### 5.4 The news rule, at every firm (R-1; RD-05 A-18 and E-200 R-1, extended)

**The calendars:** the BLS 08:30 releases (`vendor/stage2/data/releases_bls_0830_2009_2025.csv`, LF sha256
`f8e38b53ecaf116aa8fb376e82badcb2d592c1140ab452b2042bf55c34e2f523`; `vendor/stage2/data/releases_bls_0830_2026.csv`, LF
sha256 `198323e693efacbf537f5026057254c97e36333f4f00bb1074f99c0818c0c81b`), and the FOMC minutes
(`config/calendar_fomc_minutes.csv`, LF sha256 `0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7`).
**The windows:** around each release's time, the verified `mffu.news_tier1_rule`'s minutes either side, derived from
the entry, never typed. **The events:** every BLS 08:30 release in the files and every FOMC minutes release -- stricter
than the verified rule's own list (which names the Employment Report and CPI among the 08:30 releases), and so declared
under R-1's "no trading during news hours" (the red team's N-4); FOMC meeting days are out whole under CHARTER section 4
(below).

- **No entry and no fill inside a window**: an order whose live time falls inside a window is not placed (counted); a
  resting limit live before a window's start and unfilled is **cancelled at the window's start**; no fill is booked on a
  bar inside a window.
- **A position open at a window's start is flattened at that bar** -- the 1-minute bar stamped at the window's first
  minute, priced at its open with the fill rule's flatten slippage (`fills.yaml`'s active profile,
  `flatten_slippage_ticks`); a market trade's mirror is flattened at the same bar, so the pair stays like for like.
- Decided at the alert from the clock and the calendar alone (E-200 R-1: an entry's time is its order's live time);
  applied in the walks, so every plan and protocol meets it, and the resting side of a limit offer meets it whichever
  side the signal holds.
- **Kept beside it**: CHARTER section 4's own rules -- no entry at or before 07:35:00 CT on a BLS 08:30 day, and FOMC
  meeting days out on the FOMC day list the registered builders' news cuts use (named by the build from the builders'
  source, its sha256 in step 0's file) -- unchanged; E-029's early closes (`config/calendar_early_closes.csv`, LF sha256
  `72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2`), no trade exiting after the session's flatten.
- Events of the verified rule with no pinned calendar are not applied and are listed (RD-05 G-2's form).

### 5.5 The chain: one order or position at a time, in fill order (the lead's ruling on B-3)

For a signal, bracket, latency and entry type, a session's chain is built **in time order of fills**:

- **an order is placed only when the account is flat and no other entry order is working**, and at least five minutes
  after the previous chain trade's exit (D-160's five minutes flat; D-429's one position at a time); an offer whose order
  would go live while a position is open, a limit is working or within those five minutes is **not placed**, and counted;
- a market order fills on its live bar; a working limit fills, or ends at its window's end or a news window's start
  (6.1), and only then can the next order be placed -- so nothing else is ever working beside it;
- the chain trade is the order's fill; for a limit trade set the orders and fills are the **resting side's** (5.3), so the
  chain does not depend on the signal's side;
- the chain is fixed by the walks alone -- **state-free**: a trade the account later stands aside on still occupies its
  slot (fewer trades, never a state-dependent re-chaining).

## 6. The protocol: what it is, every parameter classed, and the allowed grid per plan

### 6.1 The parameters

| parameter | what it is | values | class | why |
|---|---|---|---|---|
| signal | whose offers and sides | P-14; P-16 | fixed: two | the registered signals (the brief); only P-14 is testable (1.2) |
| `s` | stop width, ticks of 0.25 points (MNQ and NQ alike) | P-14: `rung` (its registered rung map), 50, 70, 100, 150, 200; P-16: 50, 70, 100, 150, 200 | searched (stage B) | P-14's rungs are 50 and 100 ticks and P-16's stop is 150 (the red team's N-8); a step either side; all above the cost-drag floor (Stage 2 D-271 (3)) and in RD-05 part B's widths |
| `w` | target as a multiple of the stop | 1.0, 1.5, 2.0, 3.0 | searched | RD-05 2.6's ratios |
| `L` | P-14's alert-to-order latency, clock minutes | 5 (reference), 3, 2 | searched; 5 reported beside every pick | R-3; CHARTER section 4's five minutes the reference, as the lead's amending row reads it |
| P-16's timing | -- | its registered convention: alert five minutes before the mark, order at the mark | fixed | the lead's ruling on B-2: P-16's marks and sides are scheduled |
| `e` | entry type | market; limit | searched | R-4 |
| limit price | where a limit rests | the price at the alert -- the close of the last bar closed at the alert (`walker.price_at`) | fixed | the signal's own price; a fill is the market retesting it; no free offset |
| limit window | how long a limit works | from its live time to the earliest of 30 minutes later, a news window's start (cancelled) and the walk's last entry bar | fixed | one value; a different window is a new family |
| limit marketable at its live time | -- | void for that side (the walker's rule); the other side rests (5.3) | fixed | never a better fill than the limit; side-symmetric through the resting side (the red team's N-11) |
| `q` | session rule ("when to stop") | `one` (the session's first chain trade only); `all` (every chain trade); `cap` (every chain trade until the session's net reaches the mode's consistency allowance, 6.4) | searched | the operator's "when to stop"; `cap` is identical to `all` at a mode with no consistency rule (run once, printed so) |
| `m` | instrument mix | `MNQ` (micros only); `mixed` (as many minis as fit, the rest micros, D-324) | searched | the brief's MNQ versus NQ; "minis first" is `mixed`; minis-only is dropped (below) |
| `r_E`, `r_F` | dollar risk per trade in the evaluation and in the funded account | RD-05 2.6's grid: $250, $500, $750, $1,000, $1,500, $2,000, each mode separately | searched | RD-05's grid, by reference |
| `policy_E`, `policy_F` | steady or flip per mode | `steady`; `flip` (RD-05 2.6's flip: the first k sessions' first trade at r_flip, then steady) | searched | the operator's flip days (E-196); k_E, k_F, r_flip and b\* from RD-05's step-0 file, at the strict corner |
| stand-aside | when a trade is not taken | D-212's consistent risk and D-272's cost floor, the registered sizing rule's `stand_aside` (read from the module); a flip trade exempt (RD-05 2.6) | fixed | CHARTER section 4's realised-risk floor |
| headroom | the largest size | D-117's `sizing.DEFAULT_HEADROOM_FRAC` of the allowance | fixed | 3.2: never at the full allowance |
| room and daily limit | cuts | D-313's room cap; the plan's daily limit where it has one (RD-05 A-1) | fixed | the plan's rules |
| news | 5.4 | at every firm | fixed | R-1 |
| hours | 6.2 | every hour the plan allows | fixed | R-2 |
| the request | payout requests | RD-01 2.3's rule, as RD-05 2.8 | fixed | the payout lever is RD-02's |
| payout path | Standard or Consistency, Daily or 5 Winning Days | by configuration (Appendix P) | fixed per configuration | a configuration of the plan |
| seats | accounts at once | one (7.2) | fixed | seats are RD-03's lever |
| resets, reactivations | -- | none | fixed | RD-05 2.8 |
| the breakeven move | stop to entry at an FV3 session open | `STAGE2`'s | fixed | the registered walk |
| **dropped** | P-16's latency variants; minis only; an ATR-scaled stop; time stops; partial exits or scaling in; a solved state table per plan | -- | dropped | P-16 is scheduled (B-2); minis-only is `mixed` without its remainder (dominated but where a plan counts a micro as a mini, which `mixed` at RD-05's U-26 already reads); a scaled stop is another signal; CHARTER bans time stops; a solve is its own family (G-1) |

### 6.2 Hours (R-2)

Every offer of each signal at every hour it offers is in the grid, overnight included, at every plan whose hours allow
it: Topstep's and Labs' by Stage 2's verified `trading_hours` (Labs by RD-05's U-13); My Funded Futures' and Lucid's by
U-34's two corners. Every trade ends by the walk's end (5.2) or at a news window's start (5.4).

### 6.3 The allowed grid per plan (from the plan's own caps)

A sizing cell `(s, w, m, r)` is **allowed** in a mode of a configuration when RD-05 part B's `allowed` section
(`results/modes_rules.csv`, step 0) marks it sizeable under D-212 and inside every limit at the mode's start state, at the
strict corner; `rung` is allowed when both its widths are. A flip cell is allowed when its steady cell is and RD-05's
`flip_sizes` gives the mode a finite k and r_flip at that `w`. A cell not allowed is printed "not allowed at the plan's
start state" and not run. During a journey every trade is re-sized from the account's state (6.5), so a cell allowed at
the start can stand aside later, counted.

### 6.4 Trade sets and classes

A **trade set** is `(signal, s, w, L, e, class)` (P-16 without `L`), with `class` the state-free part of `q`: `one` (the
first chain trade of each session) for `q = one`, `chain` (every chain trade) for `q = all` and `q = cap`. Its trades and
their twins are fixed by the walks and the chain (5.3, 5.5); its lift is tested on them, whatever an account later stands
aside on. `cap`'s stop for the day depends on the session's earlier trades, known when the next would be placed: a
session-state rule, described. The mode's consistency allowance is the mode's recorded consistency share times its base
(the evaluation's target; the funded payout gate's base where the plan's record has a funded consistency rule), at the
account's state, by RD-05's adapters.

### 6.5 Sizing a trade (RD-05 9.2's costed rule, by reference)

At each trade the contracts are recomputed from the account's state: the largest whole number under the mix rule whose
stop-out -- the stop's dollars, the stop tick and the entry tick of slippage, the round-turn fee by the plan's cost rule
(RD-05 4.5, U-32) -- lies within the room above the floor and the day's remaining limit, at most `r` at the stop, the
current tier's allowance by the plan's counting rule and the headroom cap; a trade carrying less than the stand-aside
share of `r` is not taken, the session counted toward inactivity (RD-05 A-3). A flip trade: RD-05 2.6 with this
protocol's stop. **Units** (the red team's N-3): a trade's size is held as `n`, its count of micro-equivalents (a mini
counts its micro-equivalents by the instruments' tick values, `propedge/execution/instruments.py`, read), so its dollar
P&L is `n x (gross R x s x the micro's tick value)` less its costs at its contracts. Costs are charged inside the room.

## 7. The engine: single-seat journeys on historical trades, and the value arms

### 7.1 The attempts

RD-05's coin engine A-0 with its adapters A-1 to A-19 at each mode-corner (by reference), plus one marked addition,
**F-A1, the historical chain draw**: account i is an attempt begun at session `t_i` of the block; on its session d, slot
k, the draw returns the k-th chain trade of session `t_i + d` that the account's design executes (after the session rule;
for a limit set, a chain slot whose signal side is void returns no trade), sized by 6.5 from the account's state, or NaN
where none. The draw never clamps; the engine applies floors and limits (the contract-engine skill). **An attempt is
begun at every session of the block**, vectorised across starts and across a mode's sizing cells, giving for each mode
cell and each session t: the attempt's end session, its cause (pass; floor; lifespan; inactivity; an end by count;
"moved to Live" at a verified ceiling, RD-05 A-11; censored at the block's end), its fees and, in the funded mode, each
payout's session and amount. The run streams by entries-bracket: only one entries-bracket's tables are held at a time.

### 7.2 The journeys (F-A2, the composition)

A user starting at session s buys an evaluation at s; an attempt ending unpassed at e is followed by a new one at e + 1;
a pass at e activates the funded account at e + 1 (RD-05 2.7, fees at the switch by key); a funded account ending at e
is followed by a new evaluation at e + 1; until s + 252 sessions or the block's end. This is exact pointer composition
of 7.1's tables, never a new draw; it equals a direct sequential replay start for start (17.3 item 3; T-5). Measures
per start: net cash (payouts received less every fee paid) at months 1, 2, 3, 6 and 12 and whether ahead; P and the
guarded measures of CHARTER section 2 by `vendor/stage2/docs/USER_MILESTONES.md`'s definitions where they apply to one
seat (S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c), E-014's journey variables, sessions to the first pass and payout.

### 7.3 The value arms

For a P-14 protocol on a configuration and a block, with `lhat` the block's lift of its trade set (the mean of `x_i`,
5.3) and `lamhat` the **lift per executed trade** -- `lhat` itself for a market set; for a limit set, the mean `n_i` of
the trades the design executes (`s_i = +1`) less the mean `n_i` of the trade set's resting-side fills, the coin's
expected outcome per trade it takes:

- **the design arm** -- the journeys as traded;
- **the zero-lift arm** -- every executed trade's dollar P&L shifted by `-lamhat x n x s x the micro's tick value`: the
  design with its block's lift removed (Stage 2's convention of shifting outcomes, as its gate's zero-edge twin);
- **the lift-L arm** -- shifted by `lamhat x (L / lhat - 1) x n x s x the micro's tick value`, the design with its lift
  set to L in `x`'s units.

**The value at L**, `V(L)`, is the mean over the block's starts with 252 sessions left of month-12 net cash in the
lift-L arm less in the zero-lift arm, at U-33's price that makes V smallest. Each arm is a full engine run (a shift moves
floors, passes and payouts). Stage A runs the design arm for every cell and the zero-lift arm for every P-14 cell (or
only where the reduction ladder's rung 2 allows, 18), so `V(lhat)` is printed for those cells.

### 7.4 What this engine is not

It is not U1's replay: one seat, a fixed protocol, no state table, no router across accounts. Its rows are never paired
with U1's; R\* (P-14's U1 row) is printed beside, labelled "five seats and the state table: another engine". Inside
this engine every comparison is paired on the same starts.

## 8. Stage A: the whole grid on the choice block, described, no pick

### 8.1 What is computed (every cell, every configuration at its strict corner)

1. **The trade sets** (P-14 288, P-16 80): supply (chain trades a session; the class `one`'s share of sessions), the
   void, resting-side and cancelled shares (limit entries), the not-placed count (5.5), the news-refused and
   news-flattened counts, the unresolved and breakeven shares, by year; `lhat_A` with its session-cluster standard
   errors at the 21-, 42- and 63-session blocks; the band check of Q-126 section 2.5 on the trade set's sides (a
   switching side, below 42 sessions; 11) and, where the adopted statistic is scope D's, its 4.4 admission from sides
   only; the predicted judged trade count (9.2). For P-16 `lhat_A` is a check (expectation zero), printed as such.
   **The limit diagnostic (beside, deciding nothing; the lead's ruling on B-1):** for every limit trade set of both
   signals, the walked-mirror form's mean `(net_R(side) - net_R(mirror)) / 2` (pair rule, symmetric booking, its
   ambiguous share) printed beside the exact form's `lhat_A` -- a placebo of the limit's mechanics, never an input to a
   rule.
2. **The mode cells** (7.1): per mode, per trade set's entries-bracket, session rule, mix and sizing cell -- the
   evaluation's pass share per attempt, sessions to a pass, fees per pass, the causes; the funded account's payout share,
   sessions to the first payout, mean net per activation, the causes; the realised-to-intended risk (E-022 (1)'s
   allowance-capped form); stand-asides; the exposures of RD-05 4.7 item 5; for P-14, the zero-lift arm's same rows.
3. **The joined journeys** (7.2): every protocol cell -- P, the guarded measures, the mean net at months 1 to 12 with p10,
   p50, p90 and CVaR10 at month 3 (E-134 (2)'s guard row), sessions to the first payout; for P-14, `V(lhat_A)`.
4. **Repriced configurations** (`TS-N/std`, `TS-N/con`): every fee re-priced on `TS-S`'s runs, exactly.
5. **Beside, deciding nothing: a choice-block rung map** (the lead's ruling on S-2): P-14's rung map rebuilt by
   `atlas_a3`'s own rule from choice-block years only, and the 48 `rung` trade-set rows of item 1 recomputed under it
   (its hours and widths, supply, resolution, `lhat_A`). It enters no rule of stage B.

Nothing is marked best. Every row is labelled "choice block, described, in sample".

### 8.2 The gates before any outcome (the kills; a killed cell is counted and printed, never read for a pick)

- **Resolution:** a trade set whose chain's unresolved share exceeds 5 % (Stage 2 D-212 as D-308 raised it) is
  ineligible for stage B. Per year beside.
- **Twin:** a limit trade set that cannot be given the exact twin (5.3) is described only and ineligible.
- **Band:** a P-14 trade set whose sides fail Q-126 2.5's check for its declared band, or (in scope D) 4.4's admission,
  is ineligible ("not judgeable at its persistence").
- **Realised risk:** a protocol cell failing CHARTER section 4's realised-risk floor (at least 90 % of trades within 10 %
  of intended risk, allowance-capped, E-022 (1)) in either mode is ineligible.
- **Flip at the gate:** a flip cell whose policy the floor gate's table (10.4 item 1) cannot express is ineligible as a
  pick, by its class, before any outcome (the lead's ruling on S-8 requires the table to express it, 17.1; this line
  binds only if the build finds otherwise and the lead's row says so before stage A runs).
- **Tier 1:** every tier-1 count of RD-05 4.7 item 1 is zero in every cell, an entry or fill inside a news window and an
  order placed beside another working order or open position among them; a nonzero count is an engine error that stops
  the step (RD-05 13.1).

## 9. Stage B: the picks, by declared rules on stage A's files alone

### 9.1 What it waits on

Stage A's files on record by the lead's row; the adopted one-sample statistic (11); RD-05's step-0 file. Stage B reads
no bar and no walk. Its level is the level of the next free program family number at the stage-B run's commit (13 unless
another family took it first); the stage-B row assigns that number if, and only if, stage B sends at least one trade set
to stage C (16.1).

### 9.2 The judged power and count of each P-14 trade set (computed from the choice block only)

For each eligible P-14 trade set tau, from `results/fp_pairs.parquet` (18):

- `MDL50_J(tau)`, the lift at which the adopted statistic, one-sided at the family's level, rejects with probability one
  half on the judged block: that statistic's own MDL function on tau's choice-block pairs, each member's standard error
  scaled to the judged block's sessions by `sqrt(n_A / n_J)` (n_A and n_J the blocks' session counts from the calendar,
  not from any trade), its degrees of freedom at the judged block's block counts;
- `Lstar(tau) = lhat_A(tau) - MDL50_J(tau)`, the bound the judged block would give if the choice block's lift held;
- the predicted judged count `N_J(tau)`, tau's choice-block chain trades a session times n_J.

**Kill B:** tau with `Lstar(tau) <= 0` is not judgeable. **Kill B' (the lead's ruling on S-4):** tau whose `N_J(tau)`
lies outside 250 to 4,000 trades -- Q-126 section 3.1's validated subset sizes, 200 to 5,000, with a quarter's margin at
each end -- is not sent to stage C. The selection's winner's curse makes `lhat_A`, `Lstar` and both kills optimistic at
the top of the ranking; that costs power, never size (the red team's N-10).

### 9.3 Values at the expected bound

For each tau surviving 9.2, each configuration c and each eligible protocol cell pi on tau at c's strict corner:
`VA_c(pi; Lstar) = VA_c(pi; lhat_A) x Lstar / lhat_A` -- stage A's two arms, interpolated linearly between zero lift and
the block's lift (a declared ranking rule; the judged value is computed by full arms, 10.3).

### 9.4 Each group's trade set T_g (the lead's ruling on S-1)

For each group g, T_g is the surviving tau that ranks first **within the group** by, in order: (a) whether the group's
best `VA_c(pi; Lstar)` over `c in g` and pi reaches the bar; (b) that best value; (c) the larger `Lstar`; (d) latency 5
before 3 before 2, market before limit; (e) the earlier tau in the order stops ascending (`rung` first), ratios
ascending, class `one` before `chain`. **K0 on T_g** (9.7); a lax T_g is struck, recorded, and the group's next tau by
the same order is taken. A group with no tau left, or whose first tau's (a) is not met, sends nothing to stage C
("closed at stage B for this group"); its picks are still read beside as descriptions.

**The sequence.** The distinct T_g sent on (duplicates removed: one test for a trade set shared by groups) are ordered by
**descending choice-block `Lstar`**, ties by the Appendix P order of the first group that picked it, and the order is
written in `results/fp_pick.csv` before stage C. **If no group sends a T_g, the family closes at stage B** ("no lift
above the judged MDL worth the bar at this family's level") and retires its number unspent.

### 9.5 The protocol per group, and per configuration

- **Per group g with a T_g:** `(c*_g, pi*_g)` = the configuration in g and the eligible protocol on T_g with the largest
  `VA_c(pi; Lstar(T_g))`; ties by the larger P on the choice block, then latency 5 first, then Appendix P's order and
  6.1's value order.
- **Per configuration c** (described): its own best protocol on its group's T_g by the same rule (or, for a group with
  no T_g, on the group's first-ranked surviving tau, or none), read beside (12).
- **P-16, described:** per configuration and per group, the eligible protocol cell (any P-16 trade set) with the largest
  choice-block P at U-33's higher price, ties by the mean month-12 net, then market first, then the orders above;
  labelled "described: a coin, no lift; never carried", with E-134 (2)'s guard row.

### 9.6 Recorded before stage C

`results/fp_pick.csv`, written by the stage-B script from stage A's files alone: every T_g with `lhat_A`, `MDL50_J`,
`Lstar`, `N_J`, the struck taus with their K0 results, the fixed sequence, each group's and each configuration's pick
with `VA`, P-16's picks, and the 5-minute sibling of every P-14 pick (12.1). The lead's row records it -- and assigns the
family number if a T_g goes on -- before stage C runs. Nothing of stage B is revisited.

### 9.7 K0: the statistic's own size on the pick's own magnitudes (F-03's K0 form; E-052 (1))

Sign nulls on T_g's choice-block pairs: `x_i^0 = sign_i x |v_i|`, with `v_i = (net_R(long) - net_R(short)) / 2` for a
market set and `v_i = n_i / 2` for a limit set (under the coin null `s_i` is independent of `n_i`, so the sign null is the
twin's own law), under the declared band's side models -- the coin (independent fair signs a trade), flips at 1, 5 and 21
sessions, Markov sides of mean dwell 30 (Q-108's class below 42 sessions) -- 200,000 draws each, keyed
`[20262430, tau index, model index]`; the adopted statistic at the family's level on each. **Lax** when, for any model,
the rejection share's exact 95 % lower limit exceeds the level. K0 at stage C (10.2) repeats it on each T_g's judged
pairs, keyed `[20262431, sequence position, model index]`.

## 10. Stage C: the judgement, once, on the judged block, in the fixed sequence

### 10.1 What it waits on

The stage-B row (with the family number); the statistic's adopting row with its code's blob (11); every identity of
17.3 holding at the run's commit; the build's red-team read.

### 10.2 C0, before any outcome of the T_g in turn is read (refusing)

On the judged block, under `fp_judgement`, for the next T_g of the sequence: its offers walked; its supply; its
unresolved share at most 5 % (a floor); for a limit set, the exact twin computable; the band check and, in scope D, 4.4's
admission on the judged sides (Q-126 2.5: a mismatch is "not claimed", never a switch); K0 on its judged counts (lax:
"not claimed"); its judged trade count inside Q-126's validated sizes, 200 to 5,000 (outside: "not claimed"). **A T_g
"not claimed" at C0 counts as a failure of the sequence**: it and every later T_g are not tested.

### 10.3 The lines

- **C1, in the fixed sequence:** for each T_g in 9.4's order, `L_J(T_g)`, the adopted statistic's one-sided lower bound
  of its lift on the judged block at the family's full level **0.05 / (k (k + 1))** (0.05 / 182 at k = 13). The first
  T_g whose bound is not above zero (or that C0 does not claim) **stops the sequence**: it and every later T_g fail C1.
- **C2** (per group g whose T_g passed C1 with every earlier T_g of the sequence, and whose stage-B pick reached the
  bar): `V_J(L_J(T_g))` for `pi*_g` on `c*_g`, by full lift-L and zero-lift arms on the judged block (7.3) at the strict
  corner, at least **$500 at month 12** per start -- a year's value per user start at the lift's cautious bound (the red
  team's N-12) -- the mean over judged starts with 252 sessions left.

### 10.4 The floors (per group g, every one required)

1. **The long-run gate** (Stage 2 D-145): growth on the required bankroll at the bound above zero -- Stage 2's gate
   (`propedge.campaign.gate.run_gate` through `extended/gate.py`) with RD-05's A-14 gate arguments for `c*_g`, one seat,
   **the protocol as a state table that expresses it whole** -- one action per mode for a steady policy; for a flip
   policy a two-phase table keyed on the count of sessions since the account's start (r_flip's action in the first k
   sessions, the steady action after), built as an adapter in `extended/` where the vendored table has no such state (the
   lead's ruling on S-8) -- on T_g's judged trades, the bound arm each trade shifted to `L_J(T_g)` (7.3's lift-L shift)
   and the zero-edge twin (the zero-lift shift) beside, 500 paths at the gate seed (15), under `fp_gate_floor`.
2. **Every offered R resolving**: T_g's judged unresolved share at most 5 % (10.2).
3. **Realised risk** on the judged replay of `pi*_g` (8.2's form).
4. **Verified rules**: every value from a verified entry or a declared U-rule; T-0's key mapping holding at the run's
   commit.
5. **Conduct tier 1**: every count zero (8.2), news and the one-order rule included.

### 10.5 The verdict

For group g: **CARRIED** when its T_g passed C0 and C1 in the sequence, and C2_g and every floor_g hold; otherwise **not
carried**, with the first line that failed. The verdict is written at 0 % payout denial with the placement off (E-008),
and recorded by the lead's row before anything of section 12 is read. **Beside every verdict, plainly:** "P-14's cell,
its hours and rung map, and P-16's mark cutoff were chosen or resolved on the whole development window, the judged
block included, so C1's level is nominal; the confirmation is the only clean test" (the lead's ruling on S-2).

## 11. The calibrated statistic: what stages A to C wait on

1. **Q-126's calibration run** (E-195, E-202 (5)) and the row pinning its choice file. Q-126's plan is
   `docs/calibration/Q-126_one_sample_plan_2.md`, LF sha256 `117f5eb36dfd8312b24db35d1e6898167397fe374ae47a1feab94b5a2ebfcdc6`
   (E-187).
2. **Its validation HOLDS** by its criterion, and a row adopting the statistic -- scope D's primary, or the scope-Q
   branch's -- naming the code's git blob id. Every run of stages A to C refuses a commit whose blob differs. **Stage A
   waits for the adopting row** (the lead's ruling on S-5): its band check and admission use the adopted statistic's
   scope.
3. **The declared side persistence** (E-035 (6); Q-126 2.5): P-14's side is a **switching side** set at each breakout,
   declared **below 42 sessions**; the traded share of sessions is printed by stage A. So the statistic used is the
   primary (in scope D with 4.4's admission when scope D chose it, in scope Q when the scope-Q branch is the primary).
   The barred regime-filter kind (E-187) is not used.
4. **Its validated domain.** Q-126 calibrates and validates on P-16's judged pairs and realistic synthetic nulls, values
   `win1` and `net3`, subsets of 200 to 5,000 trades (its section 3.1). A T_g's values are net R at another bracket, so
   **K0 (9.7, 10.2) is this family's own size check at its level on T_g's own magnitudes and counts**, and Kill B' and C0
   keep the count inside the validated sizes. **K0 is a check against gross laxity, not a calibration** (the red team's
   N-2): at 200,000 draws and a level near 0.05/182 its exact lower limit exceeds the level only for a true size well
   above nominal. It cannot detect a bias of the twin itself, which 5.3's exact form removes for limits.
5. **The level is inside the calibrated range**: every test of the sequence is at the family's own level, one of
   Q-126's k = 13 to 20, never a Bonferroni share of it (16.3).
6. **If no one-sample statistic HOLDS**, stage A does not run and the family retires unspent (no number was assigned).

## 12. The journey scorecard -- beside, never the pass line (CHARTER section 2; E-008, E-014, E-015, E-134)

### 12.1 What is read on the judged block, after the verdict row (`fp_scorecard_beside`)

- every configuration's P-14 pick and every configuration's P-16 pick (the group picks among them), at the strict corner:
  the scorecard as 7.2 lists it, each measure a distribution over starts (median, p10, p90), the guard row of E-134 (2),
  and for P-14 the zero-lift arm and `V_J`;
- **the 5-minute cell beside every P-14 pick** (R-3): the same protocol at latency 5 where the pick's is 3 or 2 -- its
  trade set's lift (described, no level), its scorecard and its value;
- the lenient corner of every two-corner configuration's picks;
- **the firm comparison**: every group's pick paired against the `TS-S/std` pick of the same signal on the same starts,
  by month, with RD-02's section 9.2 uncertainty (items 1 to 7, `extended/pp_reading.py`, this family's honesty seed);
- **the denial ladder** (10, 25 and 50 %) on the eight group picks; **the placement on** at the Topstep standard group's
  two picks; the Focused Trader models not run (RD-05 G-5);
- R\* = P-14's U1 row and the best of P-14, P-15 and P-16 on each guarded measure, cited, labelled "another engine".

### 12.2 The menu

Per configuration: its stage-A grid (from the committed summary, 18), its picks with their 5-minute cells, the
scorecards, the ladders, the exposures; the flags of RD-05 12.6 and "hours unrecorded" (U-34), "price unverified: at the
grid's ends" (U-33), "one seat"; the count of 90 % intervals shown and that a tenth would exclude zero by chance. E-015's
limits flag the menu only if approved before the run's commit by a row of the `e015-limits:` form (E-104). **No cell is
withheld for conduct** (RD-05 4.7).

## 13. What a pass and a fail mean

- **CARRIED for a group** -- a development finding on a late-development block, at a nominal level (10.5): the design
  (P-14 at T_g through `pi*_g` on `c*_g`) takes a registration id, its registered development test, the auditor and one
  confirmation line per distinct carried T_g (14). The carrying row says what is claimed (the lift, and its value
  through that protocol) and what is not: that the protocol beats another, that the firm beats another, that T_g beats
  P-14's registered bracket, or that **the class choice (`one` or `chain`) is better** (the red team's N-1).
- **Closed at stage B** -- "no lift above the judged MDL worth the bar at this family's level", never "these firms or
  brackets do not work"; no number is spent and the judged block is not read for any trade set.
- **Not carried at stage C** -- the first failing line named; the failure protocol applies to any failed identity or
  oracle, never to a line that simply did not pass.
- **The closure binds** (Stage 2 D-277's boundary): a later family on these signals, brackets, latencies or entry types
  names this one, says what changed, and is not judged on this judged block. The judged block is recorded as read for
  protocol choices on P-14 and P-16.

## 14. The confirmation, declared before any development read

- **The window:** NQ from 2026-07-17 (`config/windows.yaml`, `reserve`), not on disk, a purchase, the operator's; it
  would be NQ's fourth confirmation window (Stage 2 D-107, D-461). Other drafts target it; if any test reads it first,
  the lead records that before registration and the operator decides.
- **What it tests: one confirmation line per distinct carried T_g**, in the same fixed sequence, each one-sided at 0.05
  by the adopted statistic, with K0 on its counts, stopping at the first failure; each carried group's value line at its
  T_g's window bound; the scorecard descriptive. One window read serves every line.
- **How much data:** at least six months, and at least the months at which the statistic has 80 % power for a lift equal
  to the first carried T_g's `L_J`, at its supply -- computed when a design is carried and written in the carrying row
  before any confirmation data exist. If that is more than the operator will buy, no confirmation is registered.

## 15. Seeds, fixed now and checked

| seed | status | role | what it draws |
|---|---|---|---|
| 20262430 | in use | `k0_choice` | 9.7's sign nulls on the choice block, keyed `[20262430, tau index, model index]` |
| 20262431 | in use | `k0_judged` | 10.2's sign nulls on the judged block, keyed `[20262431, sequence position, model index]` |
| 20262432 | in use | `gate` | 10.4 item 1's gates, 500 paths, one seed for every group (paired) |
| 20262433 | in use | `ladder` | 12.1's payout-denial draws, keyed `[20262433, start index, request index]`, common to every pick |
| 20262434 | in use | `honesty` | 12.1's honesty series (RD-02 9.2), keyed `[20262434, 1, shape, h, n_w]`; the build's test `[20262434, 0, ...]` |
| 20262435 | in use | `build_toys` | the build's synthetic bars, chains and batteries (T-1 to T-12) |
| 20262436 | reserved, unused | -- | -- |
| 20262437 | reserved, unused | -- | -- |
| 20262438 | reserved, unused | -- | -- |
| 20262439 | reserved, unused | -- | -- |

**Nothing else draws.** The walks, the chains, the engine on historical trades, the composition, the value arms, the
exact twins and the statistic (a closed-form t) draw nothing.

**The timing measurement is not on these streams.** Step 2's time and memory are measured before it on synthetic chains
drawn from `numpy.random.default_rng([0, j])` -- seed 0, outside the block, its outputs discarded.

**The check, 2026-11-18 (UTC), on the first text, repeated on this one.** Word-bounded searches for the block's pattern
(its seven-digit prefix and one digit), every text file, the licensed data excluded: `git grep -IwnoE` on every local and
remote ref, the vendored snapshot included; and `grep -rIlwE --exclude-dir=.git --exclude-dir=data` on the working files
of the main tree, every worktree under `%LOCALAPPDATA%\stage2-extended-wt\` and every clean-run checkout and log under
`%LOCALAPPDATA%\stage2-extended-runs\`. The block is found in this file alone (and its remote copy). **T-0**
(`tests/test_f04_draft.py`) builds the block by arithmetic, repeats the search over the tracked and working files of its
checkout on every run, allows only this file and its `DECLARED_USES`, and proves the scans work on a planted copy.

**Inherited, used only as their owners registered them:** P-14's gate seed 20261131 and P-16's 20261206 (the
identities); P-16's registered coin seed (its builder, D-521); U1's replay seeds (the identities).

## 16. Multiplicity and counting

### 16.1 The family's number and level (the lead's ruling on S-9)

The family is pinned with every stage fixed but **no number**. The stage-B row assigns the next free program family
number -- k = 13 unless another family is pinned first -- **only if stage B sends at least one T_g to stage C**, and
writes it before stage C runs; stage B computes its MDL and kills at that number's level, one-sided 0.05 / (k (k + 1)),
provisionally 0.05 / 182. If stage B sends nothing, the family retires unspent, as F-02 did (E-094, E-095). Nothing is
chosen after a look: the rule is mechanical.

### 16.2 Every cell counted

The grid's factors: P-14's stops 6, P-16's 5; ratios 4; P-14's latencies 3, P-16's 1; entry types 2; trade-set classes
2; session rules 3; mixes 2; sizing cells a mode 12 (6 risks x 2 policies), 144 a joined pair; configurations 19 (17
run, 2 repriced; Appendix P), 13 evaluation and 15 funded modes; groups 4; two-corner configurations 15.

<!-- counted-cells: the rows below are summed by T-0 -->

| block | cells | basis |
|---|---|---|
| P-14 trade sets | 288 | 6 stops x 4 ratios x 3 latencies x 2 entry types x 2 classes |
| P-16 trade sets | 80 | 5 x 4 x 1 timing x 2 x 2, described |
| evaluation mode cells | 172224 | (144 + 40) entries-brackets x 3 session rules x 2 mixes x 12 sizing cells x 13 evaluation modes, at most |
| funded mode cells | 198720 | the same x 15 funded modes, at most |
| zero-lift mode cells | 290304 | P-14's 144 entries-brackets x 3 x 2 x 12 x 28 modes, at most |
| P-14 protocol cells | 2363904 | 144 x 3 x 2 x 144 x 19 configurations |
| P-16 protocol cells | 656640 | 40 x 3 x 2 x 144 x 19, described |
| repriced protocol cells | 317952 | the 2 repriced configurations' cells of both signals, exact arithmetic |
| zero-lift journeys | 2363904 | one per P-14 protocol cell, at most |
| stage A, limit diagnostic rows | 184 | the limit trade sets of both signals (144 + 40), beside |
| stage A, choice-block rung map rows | 48 | P-14's `rung` trade sets (4 x 3 x 2 x 2), beside |
| K0 at stage B | 288 | at most one per P-14 trade set |
| judged lift tests | 4 | C1 in the fixed sequence, one per distinct T_g at most |
| K0 at stage C | 4 | one per distinct T_g at most |
| value lines | 4 | C2, one per group at most |
| gates | 4 | one per group pick at most |
| beside, configuration picks | 38 | 19 configurations x 2 signals |
| beside, 5-minute cells | 19 | one per P-14 configuration pick at most |
| beside, lenient corners | 30 | 15 two-corner configurations x 2 signals |
| beside, denial ladder | 24 | 8 group picks x 3 levels |
| beside, placement | 2 | the Topstep standard group's two picks |

<!-- end counted-cells -->

That is **at most 3,020,544 protocol cells** (2,363,904 of P-14's and 656,640 of P-16's, 317,952 of them repriced
by arithmetic), **368 trade sets**, **at most 4 judged lift tests in a fixed sequence**, **at most 4 value lines and 4
gates**, and **at most 113 journeys beside**. A cell not allowed (6.3), identical by construction (`cap` where no
consistency rule exists), killed (8.2) or dropped by the reduction ladder (18) is counted all the same, the ladder's
rungs applied recorded in step 2's row. A joining firm (RD-05 2.4) adds its configurations' cells by the same products
and a group, stated in its join row before stage A's commit; after that commit nothing joins.

### 16.3 The judged tests and the family-wise error across firms (the lead's ruling on S-1)

- **Within each firm group** the selection (9.4, 9.5) is made on the choice block only; it costs power, not size.
- **Across groups**, up to four distinct trade sets reach the judged block, tested in **a fixed sequence** fixed at stage
  B by descending choice-block `Lstar`, **each at the family's full level 0.05 / (k (k + 1))**, the sequence stopping at
  the first failure. **The family-wise error is at most the family's level under any mix of true and false nulls**
  (strong control): the first true null the sequence reaches is rejected with probability at most the level, and testing
  stops there. The value lines and floors are not tests at a level: each is a fixed function of a bound.
- **The house rule.** Stage 2 D-621 (5)'s "one cell reaches judgement" exists to hold the family's error at its level;
  the lead's ruling, recorded in its row, is that a fixed sequence at the family's level meets that purpose. Bonferroni
  over the groups was not used: at three or four tests its shares would fall below the lowest level Q-126 calibrates
  (k = 20's), while the fixed sequence keeps every test inside the calibrated range.
- **The program's honesty sentence:** Stage 2's programs and this repository's families have read the judged block for
  these signals' own brackets, hours and marks (section 2); the development level is nominal and a screening threshold,
  and the decision is carried by the confirmation on unread data, if the operator buys one.

## 17. The build: adapters, identities and tests (after the pin, before any run)

### 17.1 The code (in `extended/`, never in `vendor/`)

- `extended/fp_walks.py` -- the offers of both signals at every stop, ratio, latency and entry type through
  `extended/walker.py`; the resting side and `n_i` for limits; the walked-mirror diagnostic; the news rule of 5.4; the
  chain in fill order (5.5); read through `extended/reader.py`.
- `extended/fp_engine.py` -- F-A1 on RD-05's A-0 and adapters; F-A2's composition; the value arms (7.3); streaming by
  entries-bracket.
- `extended/fp_pick.py` -- stage B's rules (9), reading stage A's files only, each checked against its manifest.
- `extended/fp_stagec.py` -- C0, C1 in the fixed sequence, C2, the floors, the verdict; **the gate's state table for
  steady and flip protocols** (10.4 item 1), as an adapter if the vendored table has no session-count state.
- `scripts/fp_rules.py`, `fp_walks.py`, `fp_grid.py`, `fp_pick.py`, `fp_judge.py`, `fp_beside.py`; `identity/fp_identity.py`.
- Every rule value read by key through RD-05's loaders (its 17.2); a test fails on a literal rule value in the code.

### 17.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 | `tests/test_f04_draft.py`: one F-04 declaration; sections 0 to 20 and Appendices P, A and C; the seed table and the block nowhere else, its scans' positive control; one judged-reads line, three purposes, none choosing; the counted cells against the factors and Appendix P; RD-05's and Q-126's pins as cited, against the files and the log; the four calendars' LF sha256; the provisional level; no dollar figure but the declared grids and the bar. **At the pin, added:** Appendix P's modes against RD-05's Appendix M, and every key 3.2 names against the merged record |
| T-1 | F-A1 with a scripted binary chain equals RD-05's A-0 with `BinaryDraw` on the same uniforms, account for account |
| T-2 | the walks on synthetic bars: latency in clock minutes moves the entry bar, **with a missing-bar case** where it differs from `entry_bar`'s five present bars; P-16's entry at the mark; a limit at the alert's price fills only on a trade through by a tick, is void when marketable at its live time, the other side then resting, cancelled at its window's end and at a news window's start; no fill inside a window; the forced flat at a window's first bar, both sides; **the exact limit twin's mean zero for a fair coin on a tick walk with bid-ask noise**, where the walked-mirror diagnostic's is not (the red team's B-1 construction, on the `build_toys` seed) |
| T-3 | the chain in fill order: one order or position at a time, five minutes flat, a stood-aside trade keeping its slot; **two overlapping limits, and a limit overlapping a market order** (the second not placed, counted); limit chains on the resting side's fills; `one`, `all` and `cap` |
| T-4 | 6.5's sizing on hand-computed cells: the mix, the counting rule, micro-equivalents, the headroom cap, the room and the daily limit, the stand-aside, the flip |
| T-5 | the composition against a direct sequential replay on toy tables; censoring at the block's end; no index past the block's last session ever read (a planted later session refused) |
| T-6 | the value arms: the zero-lift arm's executed trades' mean lift zero exactly on a toy, market and limit (`lamhat`); `V` linear in the price; the interpolation of 9.3 |
| T-7 | stage B's rules on synthetic stage-A files: Kill B and Kill B', the per-group order of 9.4, the strikes, duplicates removed, the fixed sequence's order, per-configuration picks, P-16's rule; the pick refuses any input but stage A's and RD-05's files or a file whose sha256 differs from its manifest |
| T-8 | K0 on synthetic pairs, market and limit forms: a lax statistic flagged, a sound one not, at the family's level; the fixed sequence on synthetic bounds stops at the first failure and treats a C0 "not claimed" as one |
| T-9 | U-33's and U-34's ends; the news windows derived from the key on a hand-built entry |
| T-10 | the menu: no P without its guard row; the 5-minute cell beside every P-14 pick; the flags; the nominal-level sentence beside every verdict |
| T-11 (`slow`, `heavy`) | 17.3's identities at 4 starts and a few hundred offers (reads the bars) |
| T-12 | the seeds of 15 only where 15 declares them (T-0's `DECLARED_USES`, extended by the build); tier-1 counts zero on toy runs and firing on a hand-broken router; the gate's flip table equal to its two phases on a toy |

### 17.3 The identities (refusing; whole-window identities only from `identity/*.py`)

1. **Shared, owed by other items**, each met by a row of the `identity-holds: <id>` form at the run's commit or an
   ancestor, its cover unchanged: Q-05 (E-010), Q-80 (E-049), Q-93 with Q-100 (E-059), Q-101 (E-068), E-011's walker
   identity, RD-01's `firms_identity`, and **RD-05's `modes_coin_identity` and `modes_identity`** (its adapters are this
   family's), after the rules record's merge (E-202 (3)).
2. **`fp_identity`, item 1** (whole window, purpose `identity`; equality checks and hashes only, 4.2): 5.2's walks at the
   registered widths, market, news off -- P-16 at delay 0 at the mark against `TRADES_SHA256`; P-14 at L = 5 against the
   A3 cache's walks offer for offer, every column, **the missing-bar offers the only allowed difference, each counted
   and printed**; P-14's registered trade list by its rung rule.
3. **`fp_identity`, item 2** (choice block): F-A1 at `TS-S/std` with every RD-05 addition at its Topstep setting against
   the vendored `CombineAccount` and `FundedAccount` driven by the same sized chain -- every attempt start, P-14 at its
   rung bracket, L = 5, market, both mixes, all twelve sizing cells of each mode, account for account: every end session,
   cause, fee and payout; only RD-05 13.1 (1)(d)'s listed differences allowed; and the composition against a direct
   sequential replay, start for start.
4. **Inside every run:** every executed trade is a chain trade of its trade set; `TS-N` equals `TS-S` but for fees;
   `cap` equals `all` where no consistency rule exists; corners equal where a term cannot bind; every tier-1 count zero.
   Any failure stops the step; the failure protocol applies.

## 18. Outputs, the run, its bounds and the reduction ladder

**Files**, each with its sidecar manifest through `extended.results.write_result` (`prereg_id` `F-04`, the pinning row,
the identity rows, every seed, every parameter, the record's commit and keys, the cell counts as run, the ladder's rungs
applied, `exploratory=False`).

- **Committed summaries:** `results/fp_rules.csv` (step 0); `results/fp_tradesets.csv` (every trade set's 8.1 item 1 row,
  the limit diagnostic and the choice-block rung map beside) and `results/fp_grid_summary.csv` (per configuration and
  trade set: the counts of allowed, eligible and killed cells and the distribution of P, month-12 net and `V(lhat_A)`
  across its protocol cells, no cell marked) (step 2); `results/fp_pick.csv` (step 3); `results/fp_judgement.csv`
  (step 4); `results/fp_beside.csv` and `results/fp_menu.csv` (step 5).
- **Bulk, kept local and git-ignored, with committed manifests** (the existing `results/*.parquet` rule; each manifest
  holds its file's sha256, and the row recording the step cites it; the lead's ruling on S-7): `results/fp_grid_<configuration>.parquet`,
  one per configuration (every protocol cell's 8.1 items 2 and 3); `results/fp_modes.parquet` (the mode cells);
  **`results/fp_pairs.parquet`** -- the per-trade choice-block pairs stage B needs (the lead's ruling on S-6): for every
  P-14 trade set, each trade's session, side, `s_i`, `v_i` and `x_i`, and the set's eligibility flags, choice block only.

**The run, in steps, each from a clean checkout of a named commit (`scripts/run_clean.py`), one heavy job on the
machine under `run.lock`, watched to its exit, each step only after the lead's row records the one before:**

| step | what | weight | workers | time bound | memory bound (summed) | measured before it on |
|---|---|---|---|---|---|---|
| 0 | the rules arithmetic: the allowed grid (6.3), the news windows, U-33 and U-34, the FOMC day list's hash, the counts; reads RD-05's step-0 file | light | 1 | 1 hour | 0.5 GB | -- |
| 1 | the identities (17.3) | heavy | 1 | 8 hours | 2.5 GB | E-011's and E-010's recorded peaks |
| 2 | stage A: the walks on the choice block, then the mode cells and journeys, streaming by entries-bracket | heavy | at most 2 | 48 hours | 2.5 GB | synthetic chains on seed 0 (15), outputs discarded |
| 3 | stage B and its K0 (no bar) | heavy | 1 | 4 hours | 1 GB | K0 on synthetic pairs |
| 4 | stage C: C0, C1 in the sequence, C2, the floors | heavy | 1 | 24 hours | 2.5 GB | the gate's recorded peaks at one seat |
| 5 | the scorecard beside, after the verdict row | heavy | 1 | 12 hours | 2.5 GB | step 2's measurement |

Each step's memory bound is the job's summed working set (`extended/procmem.py` per process, summed by the parent), one
BLAS thread a process.

**The reduction ladder (declared now; the lead's ruling on S-7).** If step 2's synthetic measurement exceeds its time or
memory bound, these rungs are applied **in order, each only while the measurement still exceeds a bound, triggered by the
measurement alone and never by an outcome**, and recorded in a row before step 2 runs:

1. P-16 without latency variants -- **already applied in this text** (B-2);
2. the zero-lift arms and `V(lhat_A)` only for P-14 trade sets that pass 8.2's gates and have `lhat_A > 0` (Kill B kills
   every other set anyway, since `Lstar <= lhat_A`); this needs `lhat_A` first, so the trade-set rows of 8.1 item 1 are
   computed before any mode cell;
3. P-16 at market entries and its registered stop (150 ticks) only;
4. the funded mode's policy restricted to `steady`.

Each rung's cells stay counted (16.2) and are printed "not run: reduction ladder rung n". **If the measurement still
exceeds a bound after rung 4, step 2 is not started**; a step exceeding its bound while running is stopped; no other
thinning and no worker added at run time -- a smaller grid than the ladder's is a new family.

**Waits, before step 0:** the pin, which follows the lead's row amending CHARTER section 4, CLAUDE.md and the
feature-rules skill for R-3 (S-11); the rules record (Q-136, Q-136b) merged and RD-05's build and step 0 on record
(E-202 (3)); every shared identity re-held at a commit containing the merge; this family's build with T-0 to T-12 and the
red team's read of it. **Before step 2:** Q-126's adopting row (11 item 2). **Before step 4:** the stage-B row with the
family number.

## 19. Open before the pin

**Ruled by the lead on the first read (recorded here, not open):** item 1 (one common trade set or one per firm) -- one
T_g per group, a fixed sequence at the family's full level (S-1, 9.4, 16.3); item 4 (spending k) -- the number assigned
by the stage-B row only if a T_g goes on (S-9, 16.1); item 5 -- the bar stays F-03's $500 at month 12 unless the operator
sets another; item 8 -- CHARTER section 4, CLAUDE.md and the skill amended by the lead's row (S-11).

**The lead's, left for the next read:**

2. **What a carried design claims** (1.2): the vehicle reading, with the registration freezing pi\*_g, claiming only the
   lift, and its confirmation testing only the lift (the red team's reading); one confirmation line per distinct carried
   T_g (14).
3. **The statistic's domain** (11 item 4): K0 with Kill B' and C0's count check as this family's answer.
6. **News at every firm** (5.4): the windows from My Funded Futures' verified rule; every BLS 08:30 release applied
   (stricter than the rule's list); R-1 superseding the Labs caps; Topstep's trades then differing from U1's (the
   identity held with the rule off).
7. **Hours**: no trading-hours entry in the record for My Funded Futures or Lucid; U-34 brackets it.
9. **The judged block's whole grid**: not computed here; a later described reading may print it after the verdict row.
10. **Output size**: the bulk files kept local (18), the summaries committed -- as ruled; the lead confirms the
    summaries' columns serve the menu.
11. **Single seat** (7.2); the gate's flip table built as an adapter where the vendored table lacks the state (10.4).
12. **LucidFlex's corners**: `LU40` takes RD-01's `LU` corners and `LU50` RD-05 5.2's live-move corner (the red team's
    N-9: consistent as far as it checked).

**At the pin (the red team's S-10):** the pinning row attests that no RD-05 part-F row and no RD-04 step-2 row had been
read at the pin; if RD-04's step 2 runs first, the row carries RD-04 9.3's "written before RD-04 was read, unchanged
since <commit>" form.

**The operator's:** the bar if the lead asks (a year's value per user start at the lift's cautious bound); the captures
of Alpha Futures' and Lucid's terms (joining only by RD-05 2.4, before stage A's commit); any purchase of the
confirmation window, only if something carries.

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
corners are RD-05 5.2's part-F column at a single seat (U-14 moot, checked), with `L6/con` by `L6/std`'s terms and `LU40`
by RD-01's `LU` corners (19 item 12); the choice is made at the strict corner.

## Appendix A -- the red team's findings (Q-141r) and where each is answered

| finding | what it found | the answer (the lead's ruling where one is named) | where |
|---|---|---|---|
| **B-1** | the walked mirror is not a coin twin for a resting limit | the exact seedless twin `x_i = s_i x n_i / 2` on the resting side's fills (option (a)); the chain on the resting side; the walked-mirror form a stage-A diagnostic beside, deciding nothing; a limit set without the exact twin described only; P-16's "zero by construction" restated for each form; K0's limit form | 1.2; 5.2; 5.3; 5.5; 7.3; 8.1 item 1; 8.2; 9.7; T-2 |
| **B-2** | P-16's alert and P-14's five bars contradict the identities | P-16 keeps its registered timing, no latency axis, its identity at delay 0; P-14's latency in clock minutes, the identity at L = 5 against `entry_bar` with the missing-bar offers the only allowed difference, counted and printed; counts recomputed | 5.1; 5.2; 6.1; 16.2; 17.3; T-2 |
| **B-3** | the chain could choose from a future fill | the chain in fill order; no order placed while a position is open or another order is working; counted | 5.5; 8.2; T-3 |
| S-1 | one common trade set defeats the operator's point; Bonferroni not the only procedure | a T_g per group by 9.4's rule, duplicates removed; a fixed sequence by descending choice-block `Lstar`, each at the full level, stopping at the first failure; the row records that it meets D-621 (5)'s purpose; one confirmation line per distinct carried T_g | 9.4; 9.5; 10.2; 10.3; 10.5; 13; 14; 16.3 |
| S-2 | the rung map and mark cutoff use the judged block; P-14 chosen on the whole window | listed in section 2; the nominal level stated beside every verdict; a choice-block rung map beside | 2; 8.1 item 5; 10.5; 13; 16.3 |
| S-3 | which offers count at other stops | the registered offers (P-14's rung-map hours, P-16's admitted marks) at every stop | 5.1 |
| S-4 | a predictable "not claimed" on the count | Kill B' on the predicted judged count, with a quarter's margin | 9.2; 10.2 |
| S-5 | stage A depends on a statistic not yet adopted | stage A waits for the adopting row | 11 item 2; 18 |
| S-6 | stage B's inputs could not support its rules | `results/fp_pairs.parquet`, per-trade choice-block pairs, with its manifest | 9.2; 18 |
| S-7 | size and runtime unmeasured, no way down | the reduction ladder declared, triggered only by the measurement; bulk files local and git-ignored, summaries committed | 7.1; 16.2; 18 |
| S-8 | the gate cannot express a flip pick | a two-phase table keyed on sessions since the start, an adapter where needed; an 8.2 line if the build finds otherwise | 8.2; 10.4; 17.1; T-12 |
| S-9 | spending k now | the number assigned by the stage-B row only if a T_g goes on; otherwise retired unspent | header; 9.1; 9.6; 16.1 |
| S-10 | the identities' judged reads; RD-05's part F | equality checks and hashes only; the pinning row's attestation | 4.2; 17.3; 19 |
| S-11 | CHARTER, CLAUDE.md and the skill still say five minutes | the lead's amending row, cited by role, before the pin | header; 6.1; 18 |
| N-1 | E-134 (1) cited loosely; class `one` | marked a reading; "the class choice is not claimed better" in 13 | 1.2; 13 |
| N-2 | K0's resolution | stated: a check against gross laxity, not a calibration | 11 item 4 |
| N-3 | units in the value arms | `n` in micro-equivalents, the micro's tick value | 6.5; 7.3 |
| N-4 | the calendars | the BLS files cited with LF sha256 and tested; every 08:30 release applied, stricter, declared under R-1; FOMC days named by the builders' list, hashed at step 0; R-1 over the Labs keys | 3.2; 5.4; T-0 |
| N-5 | T-0 did not check Q-126's pin | the plan's path and LF sha256 cited in 11 and tested | 11 item 1; T-0 |
| N-6 | the walk's end misworded | `STAGE2`'s bar ending 15:08 CT, worst-of-three less two ticks | 5.2 |
| N-7 | "session" ambiguous | a trading day, never the FV3 sessions | 4.1 |
| N-8 | the rungs misworded | P-14's 50 and 100, P-16's 150 | 6.1 |
| N-9 | Appendix P's corners | consistent as checked; item 12 kept open | Appendix P; 19 |
| N-10 | winner's curse | stated: power, not size | 9.2 |
| N-11 | "void if marketable" and B-1 | kept, now side-symmetric through the resting side | 6.1; 5.3 |
| N-12 | the bar's wording | "a year's value per user start at the lift's cautious bound" | 10.3; 19 |

**Declined:** none. **Choices the rulings left open, made here:** C0's "not claimed" stops the sequence (conservative);
Kill B' takes a quarter's margin at each end; the sequence's ties go to Appendix P's order of the first group picking the
set; `lamhat` defines the value arms' shift per executed trade for limit sets.

## Appendix C -- the drafter's choices, each with its reason

| # | choice | where | reason |
|---|---|---|---|
| 1 | one file in three stages | 1.3 | the pick rule must exist before the grid it picks from |
| 2 | only P-14's trade sets are tested; every sizing component described | 1.2 | E-008 with E-023 (1) and E-134 (1); P-16 is a coin |
| 3 | a trade set per group, a fixed sequence at the full level | 9.4, 16.3 | the lead's ruling on S-1; every test inside Q-126's levels |
| 4 | each group's T_g ranked by whether it can reach the bar, then its value | 9.4 | the trade set the group can spend best |
| 5 | value by shifting executed trades, zero-lift and lift-L arms | 7.3 | Stage 2's convention of shifted outcomes; no per-firm value map exists |
| 6 | stage B's value by linear interpolation between stage A's two arms | 9.3 | the bound is unknown at stage A; the judged value uses full arms |
| 7 | `Lstar = lhat_A - MDL50_J` | 9.2 | the bound the judged block would give if the lift held; Kill B where it is not positive |
| 8 | a single seat | 7.2 | a protocol compared across firms on one account; seats are RD-03's |
| 9 | the market twin the walked mirror; the limit twin exact on the resting side | 5.3 | Q-108's estimand; the lead's ruling on B-1; no seed |
| 10 | every walk made anew; the caches as references | 5.2 | one code path for every bracket's trade and twin |
| 11 | the chain state-free, in fill order | 5.5 | the lift's trade set fixed by the walks alone; the lead's ruling on B-3 |
| 12 | `cap` as a session rule | 6.1, 6.4 | the operator's "when to stop" where a consistency rule binds |
| 13 | minis-only dropped | 6.1 | dominated by `mixed` except where a micro counts as a mini, which RD-05's U-26 already reads |
| 14 | the limit at the alert's price, working 30 minutes | 6.1 | no free offset; one window, fixed |
| 15 | P-16's registered timing, no latency axis | 5.1 | the lead's ruling on B-2 |
| 16 | the news window from the verified My Funded Futures key at every firm, on every BLS 08:30 release | 5.4 | R-1; Topstep's entry is `changed` |
| 17 | U-33 at the least favourable end | 3.2 | prices move cash only; no price inside the grid chosen |
| 18 | U-34 for unrecorded hours | 3.2 | no free choice; both corners printed |
| 19 | the stop widths 50, 70, 100, 150, 200 and `rung` | 6.1 | the registered widths and a step either side, inside RD-05 part B's widths |
| 20 | K0 on the pick's own pairs | 9.7, 10.2 | F-03's form; the statistic's domain is P-16's values |
| 21 | the bar $500 at month 12 per start | 10.3 | F-03's C2 bar, a year's value; the lead's ruling |
| 22 | the judged block's whole grid not computed | 1.3 | the judged block read once, for the picks |
| 23 | `TS/con` and `L6/con` read | Appendix P | G-1's reason does not reach a fixed protocol |
| 24 | ties toward latency 5 and market entries | 9.4, 9.5 | the reference first, as the operator asked it reported |
| 25 | the registered offers at every stop | 5.1 | the stop the only change (S-3) |
| 26 | Kill B' with a quarter's margin | 9.2 | the validated sizes with room for the prediction's error |
| 27 | the reduction ladder's order | 18 | the lead's ruling on S-7: the cheapest loss of information first |
