# Red team: RD-03's draft, the contract-use levers (`prereg/DRAFT_RD-03_contract_levers.md`), Q-116r, 2026-11-17

**Target.** `prereg/DRAFT_RD-03_contract_levers.md` at 153f453 on `wt/wt-payout`. Its LF sha256 was re-hashed from the
blob and matches E-145's `de551b3c829c85d8be47464045212322829affbd0cdeb5ce1befb0fd7b48f15b`. The commit adds that one
file and nothing else.

**Read.** I read the draft in full. In the main tree: `CHARTER.md` sections 2-3; DECISIONS E-007, E-008, E-015, E-023,
E-104, E-117, E-125 and E-133 to E-135, plus E-144 and E-145; the scout's note
`docs/research/next_levers_contract_money_2026-11-17.md`; RD-02's pinned text (FTP and seeds only); and the third red
team read of F-P. From deb45ad: Q-115's record `config/rules_extended.yaml`, all of its Back2Funded, Reset Bank, No
Activation Fee, hold and cancellation entries. From Stage 2: D-08, D-34, D-495, D-497, D-501, D-651, D-652, D-666 and
D-667. I checked the statuses of 26 Stage 2 ledger keys the draft cites. I read code, never results:
- `lockstep.py`: the path signature, the start-of-day billing, steps 4-6 (resolutions, seat freeing, the hold queue,
  purchases), the day recorder;
- `state_policy.py`: the objective, `ABANDON`'s note, `CombineDP.solve` and `forward`, `FundedDP.forward`;
- `u_size_fit.py`'s `attempt_readings`, and `scripts/u_size_fit.py`'s header and output sections;
- `extended/user_beside.py` (header, seeds, `EXACT_EVERY`), `extended/user_spend.py` (`day_ledger`),
  `extended/reader.py` (`CHOICE_WORDS`).

**Not read:** no bar, no result file of either repository (in particular not `vendor/stage2/results/u_size_fit.csv`,
whose rows decide stage 0), no NQ from 2026-07-17, no firm page.

**The brief** asked me to judge "the 14 choices the drafter lists". That list is in the drafter's hand-back, which is
on no file I was given: the draft, its commit message, E-144, E-145, TASK_QUEUE, PROGRESS and STATUS do not carry it.
So I listed the draft's own choices from its text (section "The draft's choices, one by one" below). The brief also
describes the G-B rule and the dropped margin without saying whether they are right. I took no view from that wording.

**Seeds in this note.** RD-03's T-0 fails if a seed of its block appears in `docs/reviews/`. So this note names every
seed of the draft by role only, the inherited ones included. My synthetic checks use the seeds 777301 and 777302 (both
outside the 2026xxxx range).

---

## Verdict: pin after the listed changes

There are four MATERIAL findings and no look-ahead, block leakage or after-the-look choice. M1 and M3 change declared
rules; M2 and M4 are a mislabel and an internal contradiction. Each is fixed by a text change before the pin; none needs
a run. With M1's remedy (stage 0 reported beside and deciding nothing), M2 falls to a label. The minors are answered in
the text. Once they are, the lead's diff check against 153f453 suffices if the diff stays inside the named hunks.
Otherwise the gatekeeper reads it whole.

---

## Findings

### M1 (MATERIAL). Stage 0's go-on rules weigh the long-run rent, but the menu reads P; G-B can stop a lever that raises P, and "a close case goes on" is false as written

**Where.** 6.3 G-B (lines 541-547); G-N (548-551); the promise at 493-495 ("built to stop a lever only where the
table's own model says it cannot pay ... a close case goes on to the replay"); "Equality stops a lever" (553); 6.5
(568-572).

**Evidence.**

- **G-B is the right test of something.** The rule is: go on if `W - lambda* x T > 599`, where `W` is a fresh funded
  account's expected net payouts, `T` its expected days and lambda\* the table's rent per slot-day. In Stage 2's
  solver, the fresh Combine is worth 0 net of rent at lambda\* (`state_policy.py` line 72, `ABANDON`'s note), and
  `CombineDP.solve` prices a pass at the funded value less the activation (lines 883-886). So `W - lambda* T` is the
  relative value of a fresh funded seat over a fresh evaluation seat. G-B is the exact one-step policy-improvement
  test for adding reactivation to the no-closure model. If it fails on a base, reactivation cannot raise that model's
  long-run cash per slot-day.
- **That is not the quantity the menu reads.** The menu's headline is P: the share of starts ahead at months 1-3, a
  share at 63 sessions. Reactivation pays $599 once to buy another try at the winning 3R opening (D-652 (1): about a
  quarter win it, and nearly all of those are paid within weeks). A start that would otherwise sit behind at months
  2-3 waiting for an evaluation pass can be flipped to ahead by that second try, even when the long-run rent says the
  evaluation route is cheaper per slot-day.
- **A synthetic counterexample** (Appendix A1; a toy one-seat journey with made-up contract numbers, seed 777301,
  40,000 starts a side, common draws):
  - G-B computes `W - lambda T` = 366 against $599 and stops. Even `W` alone (402) is below the price, so even a pure
    cash test would stop.
  - P rises from 0.1315 under the base to 0.156 under the cell. The month-3 share rises from 0.248 to 0.319. Monte
    Carlo error is about 0.002.
  - The toy's figures say nothing about P-14 or P-16. It only shows the rule can stop a lever that raises P.
- **No margin means close cases stop.** The rule has no margin, so a lever $1 short on both bases stops. That
  contradicts the text's own promise at 493-495.
- **Dropping D-666's 10 % margin was the right direction.** In D-666 (3) the margin had to be beaten to go on; it made
  going on harder. Dropping it helps power. But a rule with no margin in either direction still stops whatever falls on
  the wrong side of an arithmetic line. And G-1 says the arithmetic is first-order: the table was solved without
  Back2Funded, at D-34's joint cap.
- **Equality stopping** is harmless: it is a measure-zero event for real-valued sums.
- **G-N is weak too, but not over-strict on this evidence.**
  - The naf cell is an exact re-pricing of the base's paths in the replay. U1's bankroll is unbound, the trades and
    purchases are the same, and only fees change: +$149 per activation, -$46 per subscription.
  - So stopping it saves two replays, eight beside replays and two gates. Little.
  - My toy (Appendix A2, seed 777302, five seats) does not show G-N over-strict. It shows that G-N and P can disagree:
    at a pass rate of 0.33 G-N says go on while P falls under No Activation Fee, because its fees come earlier.
  - So G-N is no test of P in either direction. It decides a cell that costs almost nothing to run.
- **The cost.** Stage 0 decides at most 6 of 26 new cells. Running them all costs, at most:
  - four Back2Funded cells: 4 cells on two arms, 16 ladder and placement replays, 40 Focused Trader replays, 4 gates;
  - two naf cells: 2 cells, 8 beside replays, 2 gates.
  This is a described reading, so no k is spent either way. The only thing a stop saves is machine time. A wrong stop
  removes the scout's rank-1 lever from the menu, and 6.5 says it is not re-read under this declaration.

**The failure it allows.** Suppose that on the real bases a fresh funded account's value net of rent is below $599 at
the bound, yet a second try at the opening flips enough months 2-3 to ahead. Then G-B closes Back2Funded "at the fit",
and the operator's menu never shows a lever that raises P. The menu shows "closed at the fit" with the table's verdict
beside it.

**Remedy (a declared rule).**

1. Stage 0 decides nothing. G-B's and G-N's two sides, the deciding base and the "verdict line" are computed and
   printed beside each Back2Funded and naf row (10.1 item 10 already provides the slot). Every cell of section 7 runs.
2. Rewrite the header's `cells` row, 6.3 to 6.5, 11's "stage 0 stops a lever", 13 items 3-4 (now 26 new cells always;
   ladder and placement 104; Focused Trader 200; gates 26) and T-12 to match.
3. If the lead wants a stop for machine time, it should stop only where no reading of the lever could raise any month's
   share ahead. The draft has no such rule, and I know of none computable from the fit. So the clean form is
   beside-only.
4. Keep the beside line "the table's own model says ..." so the operator sees the arithmetic.

### M2 (MATERIAL while stage 0 decides; a label otherwise). Stage 0's inputs come from tables re-solved at each base's bound edges, not the registered table every cell trades

**Where.** 6.1 (a) (502-505), (b) (506-508: "(a)'s forward summaries re-priced exactly ... because a `naf` cell would
trade the registered table"); 6.3 G-B ("under the table's own model"); 4.4 G-1; 10.1 item 10.

**Evidence.** D-666's solve, which the draft adopts "exactly", re-solves the no-closure configuration for each base at
that base's own per-R bound edges. The tie-broken table and its own lambda\* come at that fixed point:
`scripts/u_size_fit.py` header ("the rent's fixed point lambda\* ... the tie-broken table at lambda\*"; "the readings
are the second set, at each base's own per-R edges"), line 513 (`rent` per base and edge set).

The registered table, `state_dp_e-0.050_lamstar_noclose`, is solved once at FV3-C's single edge. It appears in stage 0
only as identity 6.4 (1). So W, T, p, S and lambda\* in G-B and G-N belong to a table no cell trades. The reason (b)
gives, that the naf cell trades the registered table, is true of the cell but not of (a)'s summaries. "The table's own
model" names the wrong table.

**The failure it allows.** Stage 0 can stop a lever (M1) on the evidence of a policy the user never trades. Even beside
the rows, the operator reads "the table's own view" as the traded table's.

**Remedy.**

- Either label stage 0 throughout as "the model of a table re-solved at each base's bound edges (D-666's form), not the
  table the cells trade" (enough under M1's remedy);
- or compute the readings from the registered policy itself. Propagate `state_dp_e-0.050_lamstar_noclose`'s policy
  forward under each base's per-R edges (`forward` on a `FundedByR`/`CombineByR` built at those edges, given the
  registered solve's policy arrays), and take that policy's own cycle rate as the rent. With D the Combine's mean days
  per attempt and `F_acc` the table-accrual fees per attempt, that rate is
  `lambda_pi = (p W - F_acc) / (D + p T)`. This is a policy evaluation, not a solve. Its cost is a few forward passes.
- Either way, add two free oracles on stage 0's inputs:
  - `W - lambda* T` equals the funded solve's fresh value, to 1e-6;
  - the Combine's fresh value at lambda\* is 0, to the fixed point's tolerance.
  Both hold by construction, and a failure would show the inputs mismatched.

### M3 (MATERIAL). House money's waiting passes are read only at "no expiry", against E-135 and the record, and the only number on record speaks to exactly that case

**Where.** 2.3 (202-204: "A pass waiting for cash relies on the hold not expiring; ... printed as 'rests on the
no-expiry reading'"); 4.3 U-1, its last sentence (373: "House-money cells ... are read at `exp_none` alone"); 9.3 L-H
(751-753); 7.2's grid; 13 item 3.

**Evidence.**

- E-135 records that the hold's expiry is unstated, "so a declaration that relies on either declares both readings".
  The record's own note on `hold_expiry_days` (deb45ad, lines 3489-3491) says the same.
- Under both house-money rules, a pass whose activation fee would take net cash to zero or below "waits on hold until
  it can be paid" (2.3). That is a reliance on the gap.
- **The case is the one the only number names.** The web summary the verifier recorded (not evidence, line 3485) says:
  "**With fewer than five active XFAs**, you get 30 days from passing your Trading Combine to pay your Activation Fee".
  A house-money pass waits for cash, not for a seat, so it is below the cap: precisely that sentence's case.
- **The at-cap case is better supported than this one.** At the cap, verified sentences lean towards no expiry:
  - 8284215: "goes on hold until one closes";
  - 8284121: "ensuring you won't lose the account while waiting to activate".
  So the draft runs both readings where no expiry is better supported (the inventory) and only one where the 30-day
  sentence applies (house money).
- **The engine's default is neither reading.** Without the lever, D-08 forfeits a pass that cannot afford its
  activation. Waiting is new behaviour the adapter adds (A-1 (c)).
- A printed count does not replace a declared reading: the count says how many passes rest on the gap, not what the
  guard row would be without them.

**The failure it allows.** A house-money row's mean net, month-6 and month-12 net and gate, the very guard E-134 (2)
asks for, include payouts from passes that under the 30-day reading lapse unpaid. The guard then looks better than one
of the two readings allows, on the lever the guard exists for. The "absorbing" proof is unaffected: a lapsed pass pays
no fee.

**Remedy (a declared rule).**

- Run each house-money cell at both readings: `house_stop_none`, `house_stop_30`, `house_zero_none`, `house_zero_30`.
  Under `exp_30`, a pass not activated within 30 calendar days of its pass close (21 sessions in the gate) is lost,
  unpaid.
- The house rows carry U-1's "depends on the hold's expiry" flag.
- Counts: house money becomes 8 new cells, 30 new cells at most; 13 items 3-4, the header and T-5 follow.
- 9.2 gains: "under `exp_30` no house-money pass activated more than 30 calendar days after its pass".

### M4 (MATERIAL). The reading's own identity script must both refuse every option not at its off value and run every option at a "cannot bind" value; and three of those four values are vacuous on `ref`

**Where.** 9.1 (668-671: "every lever option is a constant at its off value ... it asserts every option off and
refuses otherwise (T-11)"), item 3 (682-684); T-11 (979: "with any option flipped the guard refuses"); T-8 (975).

**Evidence.**

- **The contradiction.** Item 3 sets Back2Funded's limit to 0, an expiry longer than the horizon, an unreachable
  house-money trigger, and the No Activation Fee prices replaced by Standard's, all inside
  `identity/cl_identity.py`. T-11 makes that same script refuse any option not at its off value. A builder must break
  one of the two declared rules.
- **What item 3 actually tests, on `ref`:**
  - Back2Funded at 0 is the off value.
  - Standard prices in the naf slot are the off value.
  - An expiry on `ref` is vacuous. Under the joint cap of five, the base can never hold a pass: a pass happens on a
    running evaluation, so at most four funded accounts exist when it joins the queue. `lockstep.py` lines 2068 and
    2116 show this.
  - Only the unreachable trigger exercises new code, the per-close net test.

**The failure it allows.** The build either drops item 3 silently or weakens T-11's guard. That guard is the door rule
that keeps the identity from running a policy cell on the judged block (E-104's m1 lesson in RD-02's read). Either way
a declared rule is broken without a row.

**Remedy.**

- Delete item 3 from 9.1. The never-binding equalities are already covered on toys: T-2 (limit 0), T-4 (expiry beyond
  the horizon equals `exp_none`), T-5 (trigger unreachable), T-13 (Standard prices equal the base).
- On real data, 9.1 item 7 inside the run already holds the binding cells to their bases before they bind, and the two
  expiry readings to each other where no pass waits 30 days.
- Or keep item 3, but declare its four settings as named constants of the script that T-11 admits by name, and drop
  the vacuous expiry setting.

### MINOR

**m1. The Focused Trader models are not read for the house-money and naf cells, and the menu does not name the gap.**
4.5 (428-432) and 10.1 item 8 (801) skip them because house money "lowers that exposure" and the pricing path "leaves
it unchanged". E-007 (e) asks for them beside every user reading. RD-02, which could not run them, named the gap on its
menu (RD-02 9.1 item 7; its `Q-102 n2` row). **Remedy:**
- either run them (10 x 6 = 60 more replays on the verdict arm);
- or print on every house-money and naf row: "not read: the binding Focused Trader models (reason)".

**m2. Reactivations count in neither the purchase budget nor the Focused Trader purchase measure (U-6), the optimistic
reading on tier 3, and there is no conservative reading beside.** Lines 139-144 and 391-394. The Corrective Path names
"Excessive recycling of Trading Combines or XFAs" (D-495 (2)), and a reactivation recycles an XFA. D-501's budget
exists to restrain that same exposure. Printing reactivations per 21 sessions does not let a reader recompute a
placement. **Remedy:**
- run the Back2Funded cells' ten Focused Trader models a second time with each reactivation counted in the purchase
  measure (A-1 can add it to the copied path's counter as a marked option; 40 more replays);
- or label every Back2Funded Focused Trader row "reactivations not counted as purchases: the optimistic reading".

**m3. Back2Funded's timing uses the engine's next-session seat convention, though two verified keys allow a purchase
the evening of the loss.** U-3 (378-383) and 2.1 (128-131) buy on "the evening its seat frees", which under
`next_session` is the evening after the breach. That gives first trading two sessions after the loss.
`back2funded_seat_count` (the eligible XFA does not count toward the five during the window) and
`back2funded_trading_from` (available at the start of the next session after purchase) together let a user who buys
after the breach trade the next session. `xfa_seat_frees_at` (unverified) is about the general seat, not this one. The
draft labels the pessimism, so nothing is hidden. But the lever's whole value is speed, and the verified timing is
available. **Remedy:** reactivate on the evening of the breach close (trading the next session) as the declared
timing. Or keep the draft's timing and name it "one session later than the verified keys allow" on every Back2Funded row.

**m4. A conduct sentence contradicts Stage 2's record.** 4.5 (422-424) says Back2Funded "is not account stacking in
10305426's sense (aggressive play into the MLL to fish for a win), which no registered design does". D-495 (2)-(3)
quotes 10305426 as "Repeatedly trading aggressively, hitting the Maximum Loss Limit (MLL) in one account, then
switching to another account and repeating". It records that "FV3-C (P-06) and family A3's leaders draw nearly all
their payouts through this pattern", and P-14 is an A3 design. A reactivation repeats the pattern on the same XFA. The
draft's tier-3 classification is right (D-145: account stacking is priced). The sentence is not. **Remedy:** "the
designs' money already comes through the pattern Topstep names as account stacking (D-495 (3)), priced at tier 3;
Back2Funded repeats it on the same XFA and so raises that exposure, which the ladder's stacking test (two breaches in
21 sessions) and the Focused Trader models price beside".

**m5. The beside rows' guard is underspecified.**
- 10.1 item 8's last bullet (805) lists, for the ladder and the placement, "P by month, mean net, CVaR10, P under a
  bankroll limit, the effective sample size and the MDD". It does not list the month-6 and month-12 net or the gate,
  which E-134 (2) and T-14 require with every P.
- The long replay on every start carries month 12 (`user_beside.py`: exact-length runs only on every 21st start, the
  long run on all), so the measures are available.
- The gate is run once per cell, at 0 %.
**Remedy:** name "the guard row (item 2)" in item 8 for every response. State that the guard's gate entry on a beside
row is the cell's 0 % gate, labelled so, unless the gate's own denial arms are read.

**m6. The frontier would include the house-money cells.** 10.1 item 1 (767-768) builds "the frontier on P, S1, S3a and
S5a across each base's cells". House-money cells cannot be below their base on P by construction, so they would
dominate on that axis, while 2.3 and T-14 say they are "never ordered on P". **Remedy:** the frontier excludes the
house-money cells, or is printed with and without them, the "with" version labelled "gaming P".

**m7. Assertions owed by the tests.**
- (a) No test asserts `reset_failed_combines` False on every cell's replay and gate, though 2.5 excludes resets (G-7).
  Add it to T-4/T-15.
- (b) Stage 2's `hold_expiry_days` is `verified`, with the design sentinel `not_required_under_d34`. A loader that
  "refuses an entry not `verified`" (14.2) would accept it. Name it in 14.2 as never loaded, and test that.
- (c) The inventory's held passes pay activation "at activation" (`hold_queue_behaviour`). The engine also has
  `activation_timing='on_pass'`. T-4 should assert the replay's and the gate's `activation_timing` is the default
  `on_activation`.
- (d) T-9's "section 12's seeds appear nowhere else in the build's commit" cannot hold: the in-use seeds must appear in
  the build's code and tests. Reword as "nowhere outside the uses section 12 declares".

**m8. The covers of the reading's two identities are not declared.** 9.1 waits on shared identities "with the
identity's cover unchanged since (`cover(id)`)", but never says what `cl_identity`'s and `cl_fit_identity`'s covers
are. **Remedy:** name them: A-1 to A-6's files, Q-17's adapter, `extended/gate.py`, `extended/campaign.py`, and
`config/` under E-117. The pinning row registers them through `extended/identity_cover.py`.

### NOTE

- **n1. Stage 0's decision is already on disk.** Its (a) and (b) are arithmetic on rows of
  `vendor/stage2/results/u_size_fit.csv` (sections `reading` and `rent`, size `50k`), which Stage 2 wrote and read
  (D-667). So G-B's and G-N's outcome is fixed by a vendored file today, and anyone who opens it can compute it. The
  drafter says it was not opened. The pinning row should record that no one computed either rule from that file
  before the pin. (Under M1's remedy this stops mattering.)
- **n2. A reactivation must debit cash and `total_fees` together.** U1's own check, fees derived from the cash against
  the engine's total (`user_journey.py` 156-162), then holds, and P sees the $599. A new per-kind day-recorder column
  would be missed by any consumer that sums the three engine columns (`extended/user_spend.day_ledger`, line 279). The
  reading does not cite that module today.
- **n3. U-4's entry tier follows from verified rules.** It is not an unstated reading: the balance resets to $0
  (`back2funded_account_restart`) and the tier follows the balance (`scaling_tier_after_payout`, `resets_with_balance`).
  The label can say so.
- **n4. U-7 reads one conservative reading.** It treats a payout requested but not yet arrived at a breach as "taken"
  (not eligible), the only reading of "before taking a Payout" run. The optimistic reading would raise Back2Funded's
  supply slightly. Record it as a reading in 8.
- **n5. A failed Combine keeps rebilling unless cancelled.** The record (deb45ad 3390-3392, 8284121) says so; every
  design's engine assumes the user cancels at the failure. This is common to the base and every cell, not RD-03's, but
  worth a line among the gaps.
- **n6. Sales tax is excluded consistently.** "Prices exclude sales tax" (the record) holds for $599 as for the
  Standard fees; every fee is before tax. Say so once.
- **n7. The four judged-block purposes are clean.** `levers_scorecard`, `levers_gate_beside`, `levers_ladder_beside`
  and `levers_ftp_beside` split into tokens none of which is in `CHOICE_WORDS` (`extended/reader.py` 125-126). None is
  `identity` or `registered_design`. Stage 0 reads no bar and so needs no purpose. Its identity's label contains `fit`,
  but a label is not a purpose.
- **n8. The C values were chosen knowing D-651's outcome.** The C = 5 choice "keeps the base's day 0" because D-651 (2)
  found more early evaluations cost P, and that is an outcome on the same window. It is disclosed (section 3), it is
  contract arithmetic, and no pick follows, so it is not a defect. The menu should not present C = 5 as the "found"
  value.

---

## The draft's choices, one by one (the hand-back's list was not available; these are the text's)

| # | choice (draft's words, abridged) | judgement |
|---|---|---|
| 1 | G-B: `W - lambda* x T > 599` on at least one base, at the bound edge | the exact long-run test under the model; wrong as a stop for a P menu (M1); inputs from the wrong table (M2) |
| 2 | no margin (D-666's 10 % dropped) | the right direction; still a hard line (M1) |
| 3 | equality stops a lever | harmless |
| 4 | G-N: `F_N < F` with the table fixed | exact for the mean fee per attempt; no test of P either way; decides a nearly free cell (M1) |
| 5 | reactivate at once, first among the evening's acts | sound; one session later than verified keys allow (m3) |
| 6 | a reactivation is not a purchase in the budget or the Focused Trader measure (U-6) | optimistic on tier 3; no conservative reading (m2) |
| 7 | the entry scaling tier (U-4) | follows from verified rules (n3) |
| 8 | C in {5, 7} | contract arithmetic; informed by D-651, disclosed (n8) |
| 9 | banking on and off | fine (D-08 is the off value) |
| 10 | both expiry readings, neither the base, for the inventory | fine; at-cap waiting is the better-supported no-expiry case |
| 11 | house money at `exp_none` only, with a count | breaks E-135's both-readings rule on the case the 30-day sentence names (M3) |
| 12 | the trigger at the first close with net cash above zero | fixed by CHARTER's "ahead"; no free parameter |
| 13 | cancel only at the last close before a rebill (U-2) | correct: under either reading of `combine_cancellation_account_effect` nothing paid for is lost, as the record's own note says |
| 14 | the Focused Trader models only beside the inventory and Back2Funded cells | E-007 (e) asks for every reading; at least name the gap (m1) |
| 15 | resets excluded until a billing adapter | right (`reset_rebill_push` against `lockstep.py` 377-379); an assertion owed (m7 a) |
| 16 | the levers not crossed; Back2Funded not under No Activation Fee | right (`back2funded_fee_by_pricing_path` unstated) |
| 17 | a fresh seed block, two in use | clean (below) |

---

## What I tried that found nothing

- **The hash** of the blob at 153f453 (LF): it matches E-145's. The commit adds that one file only.
- **The seed block.** I ran a word-bounded search for the block's pattern on every local and remote ref, the main
  tree's working files (`.git` and `data` excluded), and every worktree under `%LOCALAPPDATA%\stage2-extended-wt\`
  (the licensed data excluded). It found the draft alone (two refs of `wt/wt-payout`). The inherited seeds are the
  registered ones: P-14's and P-16's gate seeds in their vendored registrations, and the ladder's start seed as
  `extended/user_beside.py` defines it (lines 140-141).
- **Look-ahead.**
  - Every lever reads only closed state: net cash after the close's arrivals, a breach, a pass close, a session date.
  - The engine bills at the start of the day, before trading (`lockstep.py` 1588-1610). House money's abandonment
    before the billing day fits there.
  - Paths are causal, so an early start's h-session measure cannot depend on later sessions. T-3 tests it with the
    bound held.
- **Block leakage.** The only cross-block channel is the verdict arm's whole-window bound, disclosed (section 3,
  "N2"). The early block is purged per measure. Nothing is chosen on any block.
- **E-134 (2) on the scorecard.** The guard row is attached to every P and every paired P difference (10.1 item 2).
  House money is labelled on every row and never ordered. T-14 enforces it. The gaps are on the beside rows and the
  frontier (m5, m6).
- **The absorbing claim.** After c\*, the only cash-reducing events are fees, and each is gated. Denials, the placement
  and the Corrective Path deny or close but debit nothing. So "ahead" stays absorbing under every beside response too.
  The 9.2 oracle checks it on P's own month-end definition.
- **The inventory's mechanics against the engine.**
  - The three caps exist separately, the funded cap is `max_concurrent_accounts` (line 2068), and the joint-cap
    purchase test is at 2116.
  - Under the base's joint cap, no pass ever waits, so the "neither reading is the base" construction is consistent.
  - With C = 5 and the joint cap lifted, the cell first differs at the first pass (the base's 4 + 1 fills its cap; the
    cell buys a fifth evaluation), as T-4 states.
  - The activation is charged at activation by default (`activation_timing`, line 1249).
- **A-1's feasibility.** The billing, the resolutions, the seat freeing, the hold queue and the purchases are all
  inside `simulate_lockstep_path` (1588-2180). So the marked additions can live in the copied function, with the
  vendored classes unchanged. House money's rule must reach each of the purchase step's several branches (2110-2180).
  T-5 should exercise each.
- **Rules.**
  - Every Q-115 key's status and value in 4.2 matches deb45ad's record.
  - The 26 Stage 2 keys I checked match the vendored ledger's status and date.
  - The unstated keys are never loaded, except as M3 and m7 (b) say.
  - Resets are off everywhere.
- **Counts.** 7.2's grid gives 2 references and 26 possible new cells. 13 items 3-4 add up: 80 to 104 ladder and
  placement replays, 160 or 200 Focused Trader replays, 20 to 26 gates.
- **Tier 1.**
  - No lever hedges, copies trades, uses simulator fills or conceals anything.
  - One position across the firm stays (D-429).
  - Back2Funded is the firm's own product.
  - The FOMC-minutes count is a count only (E-034, E-050). The named Tier 1 windows are the designs' own, unchanged
    by any lever.

## What I could not check

- The drafter's list of 14 choices (not on file).
- What G-B and G-N would actually decide on P-14 and P-16 (that needs `u_size_fit.csv`'s rows; deliberately not opened).
- Whether RD-02's imported functions (`extended/pp_reading.py`) accept cells with new fee kinds and new counters
  without change. I read only that they exist.
- The run's real cost: up to about 330 replays plus 26 gates. The draft measures it before step 3 (E-117's form). No
  figure exists yet.
- Q-44's per-start file, which 9.1 item 6 compares `ref` against (queued, not on master).

---

## Appendix A. Synthetic checks (scratchpad, synthetic only; seeds fixed before the first run)

Both scripts ran under a two-minute limit. They are in the session's scratchpad, not in the repository:
- `C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\rt\gb_toy.py`
- `C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\rt\gn_toy.py`

**A1 (M1, G-B), seed 777301.**
- The toy: one seat, 63 sessions. An evaluation attempt lasts 12 sessions, passes w.p. 0.30, costs $49, and $149 at a
  pass.
- A fresh funded account wins its opening w.p. 0.25: one $1,400 payout 12 sessions in, then it ends. Otherwise it is
  crippled: paid $700 w.p. 0.10 at 25 sessions, else lost unpaid at 25 sessions.
- The cell reactivates an unpaid loss at $599, at most twice per XFA.
- Results: G-B 366.4 against 599 (stop); `W` = 402.5.
  - Shares ahead at months 1-3: base 0, 0.1468, 0.2475 (P 0.1315); cell 0, 0.1487, 0.3194 (P 0.156).
  - 40,000 starts a side.

**A2 (M1, G-N), seed 777302.**
- The toy: five seats, the same attempt and pass. A pass pays $1,400 w.p. 0.30 twelve sessions later, and its funded
  life holds the seat 20 sessions. The No Activation Fee path is the same paths re-priced ($95 a cycle, $0 activation).
- At pass rates 0.25, 0.30, 0.33, G-N reads stop, stop, go on.
- P (Standard against No Activation Fee): 0.277 against 0.217; 0.315 against 0.266; 0.336 against 0.296. 6,000 starts
  each.
- G-N agrees with P twice and disagrees once (go on with P lower). It shows no over-strict stop. The finding is that
  G-N is no test of P, and that the cell it decides is nearly free.

---

## The proposed decision row (the lead numbers and commits it)

| E-NNN | 2026-11-17 | **Q-116r read (`docs/reviews/DRAFT_RD-03_contract_levers_2026-11-17.md`; RD-03's draft at wt/wt-payout 153f453, LF sha256 `de551b3c829c85d8be47464045212322829affbd0cdeb5ce1befb0fd7b48f15b`, re-hashed): pin after the listed changes -- four MATERIAL, eight minor, eight notes; no look-ahead, no block leakage, no unverified rule loaded, no choice after a look; the seed block found nowhere but the draft.** (M1) stage 0's G-B is the exact policy-improvement test for the table model's long-run rent (the fresh Combine worth 0 at lambda\*), not a test of P: a synthetic journey shows G-B stopping a reactivation that raises P, and with no margin a close case stops, against the draft's own promise; G-N is no test of P either and decides a nearly free re-pricing -- **stage 0 decides nothing, its rules printed beside, every cell run** (26 new cells; 104 ladder and placement, 200 Focused Trader replays, 26 gates); (M2) stage 0's inputs are D-666's tables re-solved at each base's bound edges, not the registered table every cell trades -- labelled so, or read from the registered policy's forward pass at those edges with its own cycle rate, with two free oracles on the inputs; (M3) house money's waiting-for-cash passes rely on the hold's expiry, which E-135 requires read both ways and whose only number (30 days to pay the activation, below the cap) names exactly that case -- each house cell at `exp_none` and `exp_30`, flagged (house money 8 cells, 30 new cells at most); (M4) the identity script cannot both refuse every option not off (T-11) and run each at a never-binding value (9.1 item 3, three of whose four settings are vacuous on `ref`) -- item 3 removed (covered by T-2, T-4, T-5, T-13 and 9.1 item 7) or its constants admitted by name. Minors: the Focused Trader gap named on house and naf rows or run (E-007 (e)); a counted-reactivation Focused Trader reading or the optimistic label; Back2Funded's verified same-evening timing or the pessimism named; 4.5's "no registered design does" account stacking corrected against D-495 (3); the guard row named for the ladder and placement rows; house money out of the frontier or shown both ways; assertions for resets off, Stage 2's sentinel `hold_expiry_days` never loaded, `activation_timing` on activation, T-9's wording; the two identities' covers named. To the drafter for the text changes; then the gatekeeper, T-0 and the pin. | Q-116r's brief; the note; E-007, E-023, E-134, E-135, E-145; Stage 2 D-08, D-495, D-501, D-652, D-666, D-667. |
