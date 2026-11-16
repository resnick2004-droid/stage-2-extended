# Red team: the firms reading's second draft (`prereg/DRAFT_RD_firms.md`), first read -- Q-88, 2026-11-16

**Target.** `prereg/DRAFT_RD_firms.md`, second version, as on master at 7eaae48 (the worktree fast-forwarded to it before
the read). Read beside: DECISIONS E-007, E-008, E-012..E-015, E-020, E-023, E-025, E-029, E-034, E-038, E-041, E-042,
E-045, E-049, E-050, E-052..E-054 (E-052..E-054 from the lead's working copy, not yet committed); `config/rules_extended.yaml`;
`docs/RULES_CURRENCY.md`; the vendored Lucid ledger and Stage 2's `config/rules.yaml` and `config/fills.yaml`; the
pinned calendars; `extended/reader.py`, `extended/gate.py`, `extended/campaign.py`, `extended/user_beside.py`;
`tests/test_rd_firms_draft.py`; the vendored engine where the draft leans on it (`lockstep.py`, `risk_policy.py`,
`state_policy.py`, `sizing.py`, `distribution.py`, `fv3_rung_walk.py`, `contract/lucid.py`, `atlas_a3.yaml`,
`rc150_dev_test.py`, `rc150_firm_split.py`). No bar, no atlas table, no result file of any plan was opened; no engine
was run. Three small synthetic checks ran in the scratchpad (Appendix A; seeds fixed before each run, none from any
declared block).

**The brief.** It named the known stale items (the reader and T-0) and asked for each of the draft's own
interpretations to be tested. It did not suggest a verdict. I confirmed the stale items myself (m3).

## Verdict: must be redrafted

In the review's terms the draft **must be re-declared** before its pin. Five MATERIAL defects change declared rules.
Each is a text change: none needs a run or an outcome read. After the redraft and a re-read of its diff, the reading is
**pinnable once its named conditions are met**:

- the pin itself: the re-read;
- before A-8 runs: Q-80's 500-path gate identities (E-049);
- before A-9 runs: Q-76 (or an equivalent declared keyword) and Q-17's identity (E-024);
- A-1 to A-11 built with their tests.

The draft gets much right: its accounting of what it reads, its rule keys and statuses, its seeds, and its refusal to
carry anything. What it lacks is the mapping that makes "P-16's design traded at another firm" well defined (M1),
honest ends for two unread terms (M2, M4), one interaction it does not see (M3), and an interval that delivers its
stated coverage (M5).

---

## Findings

Severity: MATERIAL (changes a declared rule), MINOR (a clarification or a rule-level fix with small reach), NOTE (a
reading). Nothing here is CHANGES-A-CONCLUSION, because the reading carries no conclusion.

### M1 (MATERIAL). What the registered tables read at DayTraders, Fast Pass and Quick Pay is undeclared

**Where.** 2.3 line 132 ("Only the plan's allowances and its per-trade costs (4.8) replace Topstep's"); 4.3-4.5 (the
term-by-term maps); 4.6 A-2, A-3, A-4, A-5, A-7 (lines 327-331); 8 line 602; G-6 line 349.

**Evidence.**

- P-16's and P-14's tables are version-12 exports (`vendor/stage2/scripts/rc150_table_screen.py:73`,
  `TABLE_VERSION = 12`).
- From version 7, `export_policy` keys every funded cell by `request_day` and `win_days`, and every paid cell also by
  `line_gap` (`vendor/stage2/propedge/campaign/state_policy.py:1338-1346`).
- The engine fills those keys from the account itself at each session (`risk_policy.account_state`,
  `vendor/stage2/propedge/campaign/risk_policy.py:339-353`):
  - `win_days = account.win_days`;
  - `line_gap = account.since_pay` once paid;
  - `request_day = account.request_day_next`.
- The table was solved with `win_days` 0..5, where 5 means eligible (`state_policy.py:971`), at Topstep's
  winning-day minimum.
- Lucid stays consistent: Stage 2's `LucidFundedAccount` keeps five days of $150 (`propedge/contract/lucid.py:402-403`,
  491).
- The draft never says what A-3 (DayTraders Pro), A-5 (Fast Pass) and A-7 (Quick Pay) store in these three fields. Nor
  does it say what `Rules.std_winning_days` and `std_winning_day_min` are at those plans. None of `win_days`,
  `line_gap` or `request_day` appears in the draft.
- It is equally silent on states the table never saw at Topstep:
  - an evaluation at or above its target while TradeDay's minimum days (A-4) or DayTraders' two Qualifying Days (A-2)
    are still owed;
  - Quick Pay's drained cushions (M3).

**The failure it allows.** The builder fixes these after the pin, and each choice moves the size of every funded trade
at those plans, and so the plan's whole row:

- **A-3 stores DayTraders' Qualifying Days in `win_days`.** The table reads 5, Topstep's eligible cell (where it sizes
  for an imminent request), three Qualifying Days before DayTraders allows a request.
- **A-3 keeps the engine's $150 count.** The table reads eligibility that DayTraders' $200 days and 30 % rule do not
  grant.
- **At Quick Pay (no gate, a request at every close).** `win_days` sits at 0 or 1 and `line_gap` is one day's P&L, so
  every Quick Pay funded decision comes from early-cycle cells.
- **An evaluation at target while TradeDay's days are owed.** It keeps trading the table's size for up to four more
  days and can fail. A user would more likely log the days with one micro.

No line of the draft decides any of this.

**Remedy (before the pin).**

1. Declare, per plan:
   - the two `Rules` fields;
   - what each adapter stores in `win_days`, `since_pay` and `request_day_next`.

   One natural rule aligns the table's meaning of "eligible": `win_days = max(0, 5 - (the plan's days still needed))`
   and `since_pay` = the plan's own profit since the last request. At Quick Pay, eligible at every close, that gives
   `win_days = 5`.
2. Declare what an evaluation does at or above target while A-2's or A-4's days are owed. Options: the table's lookup
   as it stands, a stand-aside, or a one-micro day-logging trade.
3. Add asserts to T-2..T-5.
4. Say in G-6 that these mappings are part of "the design traded there".

### M2 (MATERIAL). DayTraders' fee basis is an unread term read at one point, and the strict corner is lenient in it

**Where.** 4.8 line 371; G-5 line 348; 7.2 (line 561: "Per-trade costs ... take no flip"); U-6 line 396.

**Evidence.**

- The record (`daytraders.commissions`) lists MNQ $1.02 and NQ $3.98 a round turn, and "the page does not say whether
  exchange and NFA fees are included".
- Topstep's verified page decomposes its own all-in figure (`vendor/stage2/config/fills.yaml` lines 32-35, 8284213):
  - commission $1.00 a round turn on a mini and $0.50 on a micro;
  - NFA $0.02 a round turn;
  - so exchange fees are $2.76 (NQ) and $0.70 (MNQ) a round turn.
- If DayTraders' figures exclude exchange and NFA fees, its all-in costs are MNQ $1.74 and NQ $6.76. The rule uses
  $1.22 and $3.98.
- The draft's sentence "if exchange and NFA fees are charged on top, the pages do not give the direction" (371; the
  same in the record's note) is false. Fees on top only add cost:
  - for NQ the declared rule is the lenient end;
  - for MNQ it is lenient whenever the add-on exceeds $0.20, and the verified decomposition puts it at $0.72.
- The draft's own U-6 reads a stated term with two concrete readings at both ends. Costs are exempted (7.2) without a
  reason.

**The failure it allows.** DayTraders' "strict corner" understates its costs under the fees-on-top reading:

- $2.78 per NQ round turn and $0.52 per MNQ round turn;
- on a three-micro trade at P-16's 37.5-point stop ($225 of risk), $1.56 a trade, about 0.7 % of R, on every trade.

So a DT row printed "above TS at both ends" (line 786) can have its true strict end below TS.

**Remedy.**

1. Make the basis a two-ended term in 5.2:
   - strict: the listed figures plus exchange and NFA fees as Topstep's verified page decomposes them (MNQ $1.74,
     NQ $6.76);
   - lenient: the listed figures as all-in ($1.02, $3.98), or the current dearer-of rule if preferred.
2. Add `DT-16-fees` to 7.2: 28 replays, or 30 with the news runs.
3. Correct the direction sentence in 4.8 and G-5.
4. Add the fee-basis question to the written question to DayTraders (16, the operator's item 2).

### M3 (MATERIAL). Quick Pay's row reads the request rule, not the contract

**Where.** 2.3 lines 139-144 (request at every eligible close; the reference's amount at QP); 4.5 lines 305 (floor on
gross profit, frozen at start; a payout lowers the balance, not the floor), 308 (eligible at any close with a positive
balance), 309 (the tiered split); G-10 line 353; 10.1 item 11 (the row labels).

**Evidence.**

- Once Quick Pay's gross peak reaches $2,000, its floor sits at start.
- From then on, the declared rule halves the balance above that floor at every close until a request falls below
  TradeDay's $250 minimum. The cushion is drained geometrically.
- A seeded synthetic toy (Appendix A2) follows one account after a won $2,000 3R opening (balance $6,000, floor
  frozen at start), then 1R trades at min($250, cushion):

  | request rule | edge | median life (sessions) | breached | net paid |
  |---|---|---|---|---|
  | the draft's (every close) | 0 | 251 (the horizon) | 0.40 | 3,624 |
  | the same amount at Topstep's cadence (five winning days of $150 between requests) | 0 | 48 | 0.65 | 3,597 |
  | the draft's (every close) | +0.05 R | 251 | 0.40 | 3,711 |
  | Topstep's cadence | +0.05 R | 54 | 0.49 | 4,213 |

- Under the draft's rule the median account survives only because it is drained below its trading size and then sits
  idle, holding one of the user's five seats, for the rest of the year.
- Only 16-19 % of requests reach the 80 % tier under either rule.
- G-10's premise, "the designs trade most sessions", fails here: a drained Quick Pay account is exactly the dormant
  account TradeDay "may offboard".

**The failure it allows.**

- The operator reads Quick Pay's row as Quick Pay's contract. It is Quick Pay's contract under a request habit no Quick
  Pay user would choose, and the seats, the ladder (A-9) and the gate inherit it.
- A redraft of the rule after a Quick Pay row has been seen would be a choice after the fact. That is why this must be
  fixed now.

**Remedy (now, before any QP row exists).**

1. Declare a second Quick Pay request reading, run beside the first and called neither strict nor lenient (the
   direction is not monotone). For instance, "the user's habit held fixed": the same amount, only after the reference's
   five winning days of the reference's minimum since the last request. Run it as `QP-16-req`, one at a time from the
   strict corner.
2. Label every Quick Pay row with its request rule.
3. Turn G-10 into a counted check at Quick Pay:
   - sessions with no trade per funded account;
   - accounts idle 30 calendar days;
   - accounts drained below the smallest tradable size.

### M4 (MATERIAL). The tier-1 bracket's lenient end is not an end

**Where.** 5.5 "The bracket", lines 512-519; U-11 line 409; 5.1 line 413 ("a lenient end", the reading that helps
the user most); 11 lines 786-790.

**Evidence.**

- A trade open at a window's start (12:58 CT) has touched neither its stop nor its target, so the firm's liquidation
  value V lies strictly between them.
- The strict end (-1R) is a true lower bound.
- The lenient end books W, the trade's walked outcome. For a trade later stopped (-1R) or flattened below V, W is below
  V.
- A seeded Brownian toy (Appendix A3) checks this on trades open at the liquidation time:
  - W < V for 50 % of them at R = 1 and 56 % at R = 3;
  - mean W is about mean V (optional stopping).

  So the "lenient" corner sits near the central value in this term, not at its favourable end.
- **Footprint.** For these designs the CPI, NFP and statement windows are empty by construction:
  - P-16 drops a report day's marks before 07:30 CT (`rc150_dev_test.py` docstring);
  - P-14 takes no trade before the 07:30 CT cut;
  - A1 walks nothing on FOMC days (`atlas_a3.yaml` `day_set`).

  So the term acts on FOMC-minutes days only, at most 53 days. A funded opening liquidated there can still decide its
  account.

**The failure it allows.** The menu says a Fast Pass or Quick Pay row lies "above (or below) TS ... at both ends of its
unread terms" (786) when the term's favourable end was never run. A row printed "below TS at both ends" can be above
TS at that end. For example, a liquidated opening that would have been stopped after the release keeps its account.

**Remedy.**

1. Set the lenient end to the best value the trade could have while open: its target less a tick, with the flatten's
   two-tick cost.
2. Print W beside it as "no liquidation".
3. Or keep W, rename it, and strike the bound language for this term in 5.1, U-11 and 11.

### M5 (MATERIAL). The 90 % interval on adjacent h-start windows covers about 83 %, and its honesty check cannot see it

**Where.** 10.2 item 1 (line 754), item 2 (757), item 5 (764), item 7 (767). The method is reading PP's (E-025).

**Evidence.**

- A start's measure at horizon h reads sessions s..s+h-1, so the last starts of window i share up to h-1 sessions with
  the first starts of window i+1.
- With independent sessions, the window means' lag-1 correlation is 1/4: per-start scale, variance 2/3 and adjacent
  covariance 1/6.
- A seeded synthetic check (Appendix A1, h = 63, 4,000 series a setting) measured the coverage of the nominal 90 %
  t-interval:
  - 0.82-0.84 on additive, 0/1 "ahead" and paired series for n_w from 5 to 25 (0.88 for the paired series at n_w = 4);
  - keeping every other window (no shared session) restores 0.87-0.91.
- Item 7 builds its synthetic nulls from independent window means (one persistent variant aside), so it would certify
  this interval.
- Item 5's minimum detectable difference inherits the too-small standard error.
- Reading PP's red team saw the same neighbouring-block correlation in PP's first null (its F1, "the null is less
  dependent than the data"). The second drafts kept the window rule.

**The failure it allows.** Every 90 % interval and minimum detectable difference in the menu is about 20 % too narrow
in standard-error terms, so the operator reads noise as a difference between plans.

**Remedy.**

1. Use windows separated by h starts (every other window), or a lag-1 HAC variance of the window means with n_w - 1
   degrees of freedom.
2. Rebuild item 7's series as per-start h-session sums under the same window rule (A1's construction).
3. Label any reading whose coverage falls below 0.88 at its n_w.
4. Tell reading PP's drafter: the same fix applies there.

### MINOR

**m1. A level in a reading that has none.** 10.2 item 8 (line 772) prints Q-16's one-sided comparison at 0.05 beside
the readings. That contradicts:

- line 47 ("level ... none");
- line 751 ("Nothing here is compared with a critical value").

Across plans × corners × streams × measures × blocks it would print dozens of 0.05 calls on a menu used for a choice.
**Remedy:** drop it, or keep one headline (P, all starts, P-16, each plan's two corners) with the number of comparisons
printed, Holm across them, and the label "not a pass line".

**m2. The reader's once-rule and the identity stage's purpose** (E-053).

- **The restart sentence.** Line 888 says "A run aborted or restarted is recorded by the lead ... only the first
  complete run is read". But once a run has ledgered a read under a purpose, any later clean run under that purpose is
  refused without `repeat='E-NNN'` naming the file (`extended/reader.py:478-501`). That covers a restart, a per-plan
  rerun after an adapter fix, and the 9.1 failure protocol's rerun. Say so.
- **The identity stage.** Line 545 runs "the identities under `identity` and their own decision row". The reader admits
  `identity` only from `identity/*.py` (`reader.py:377-391`), so a `scripts/` runner's first stage would be refused.
  Declare one of two routes: an identity script run first under its own row, or the identity stage authorised under
  `firm_scorecard`.

**m3. Stale text (confirmed).**

- 16 item 1 (lines 898-901) and T-0's last clause (line 852): the reader admits RD- files (E-041, E-053 (2)). The test
  is now a plain test, and it passes.
- 5.5 line 501 and 16 item 2 (lines 905-907): the FOMC-minutes calendar is pinned (E-050). Cite
  `config/calendar_fomc_minutes.csv` and its LF sha256 `0350d41f...` (recomputed here: it matches).
- 4.6 line 317 ("built after the pin"): A-8 is built (E-049).
- 15 line 891 and 16 item 4 (line 912): the gate's owed identities are Q-80's, not Q-47's (E-049: Q-51 no longer
  covers master's gate).

**m4. A-9's missing waits.**

- Q-17's adapter refuses a path that already carries `funded_account_cls` or `household_closure`
  (`extended/user_beside.py:157-171`). The LU, DT, FP and QP ladders are therefore refused until Q-76 (queued).
- Its start seeds use Q-17's own base inside the run loop (`user_beside.py:126-130`, 323). The ladder's declared seed
  (section 12's first row) needs a keyword.
- Add both to 15's "Waits" (line 890).

**m5. A-11 in the gate.** DayBlocks carry no calendar date (`propedge/outcomes/distribution.py:40-80`), and the gate
resamples days (`propedge/campaign/gate.py` `_GateDraws` -> `SharedDayDraws`). So A-11 and the tier-1 skip have no date
on gate paths. The draft says how the gate handles DayTraders' fee and nothing else. **Remedy:** declare A-11 off in
the gate with the rows labelled, or carry each block's source date.

**m6. U-9's ends.** U-9 (line 404) claims "the two extremes the trades' own outcomes allow"; 5.4 line 475 is its
strict end.

- **The strict end is wider than the outcomes allow.** The trades carry outcomes at every quarter R to 3R. A trade that
  did not win at R_x also did not win at R_hi, the smallest menu R above R_lo, so its peak is below R_hi's target, not
  R_x's.
- **The optimistic peak is too low for profitable flattens.** It should be at least the exit value when the exit is a
  profitable flatten.
- **A same-bar edge case.** On a bar where both target and stop trade, the walk books the stop
  (`fv3_rung_walk.py:12-13`), so a non-winning trade's true peak can exceed its target. Name the convention.

**m7. "At both ends" is a bound only for monotone terms.** Line 413 and 11 (786-790) read the corners as bounds. They
are, for:

- prices and U-3 fees;
- the fifth request paid or unpaid;
- DayTraders' lag.

They are not, per start, for minimum days, inactivity, Lucid's reach, Quick Pay's peak and the tier-1 term: a closure
frees a seat, and a later pass moves the funded path. **Remedy:** say "at both declared corners", and read the
one-at-a-time runs as each term's direction on P-16 only.

**m8. Lucid's price is read at one end, TradeDay's at two.**

- Lucid's card lists "$165" struck and "$115.50 W/ COUPON AT CHECKOUT" (vendored Lucid ledger, `eval_fee` note).
- TradeDay's card has the same structure: $248 struck to $99 with SALE60. U-1 (line 381) brackets that one.
- Lucid's coupon rests on the operator's statement (Stage 2 D-31); TradeDay's sale has no such statement. Say so.
- Print LU at $165 by A-10's exact arithmetic. That needs no run; 10.1 item 9 (line 733) covers only DT, FP and QP.

**m9. The tier-1 count's definitions** (5.5 lines 505-510).

- (a) An offered trade's exit depends on the R it is traded at (`DayBlock.exit_by_rr`, D-349). Define the offered count
  as "open at the window's start at any offered R".
- (b) Fix the minute convention. Bars are stamped at their open, so a trade is in a window if its entry bar is before
  12:58 and its exit bar is at or after 12:58.
- (c) Fix the BLS name match: "Consumer Price Index for" and "Employment Situation for", in the `release` column of
  `releases_bls_0830_*.csv`.
- (d) A-11's account kinds. The record says no sentence names an account type, so apply it to evaluations and Funded
  Sim alike.
- 9.1 item 2 (line 638) lists A-2 to A-7 but not A-11. Its off setting must reproduce TS too.

**m10. Quick Pay's ceiling is read at one end** (line 311; A-7). The record says trading pauses for a review, "in most
cases ... moved to Funded Live", and the balance is "revised back to the threshold level". That is a stated term with an
unstated reach. U-6 (line 396) reads such a term at two ends, and the draft does so for Lucid's live move and Fast
Pass's fifth request. **Remedy:** add a lenient end, or state why G-4 overrides U-6 here.

**m11. The martingale count's unit** (9.3 lines 674-677). It counts within an account only. The user's trades are one
position at a time across the firm, so the sequence a reviewer sees is firm-wide: a small evaluation loss followed by a
funded opening on another account is a 2x step in it. **Remedy:** count per account and across the user's accounts in
time order, in micro-equivalents.

**m12. A-4's "trading days"** (line 329; T-5 line 857).

- TradeDay counts days with a trade ("Every day you make a trade will count", the record's note).
- The engine's `days` counts every live engine day (`lockstep.py:506-507`).
- **Remedy:** say A-4 counts days with at least one executed trade.

### NOTE

1. **5.3 at Fast Pass** (line 457). "The plan's own maximum" holds under the profit reading of the 50 % base only.
   Under the balance reading the maximum is $1,500 at any B. The moot claim (the request is inside both readings)
   holds; the "own maximum" sentence does not.
2. **Early closes.**
   - TradeDay requires flat "10 minutes before the close of the product" (`tradeday.flat_time`). DayTraders flattens
     "prior to the market close, whichever is sooner" (`daytraders.flat_time`).
   - On abbreviated sessions (E-029's calendar: 08:15, 12:00, 12:15 CT) the designs' 15:10 is not the binding time.
   - U-7's moot claim (line 399) holds only because A1 walks nothing on early-close days (`atlas_local.py:13`, D-215;
     `atlas_a3.yaml` `day_set`). 9.3's "any trade exiting after 15:10 CT" (line 690) cannot detect the case.
   - Add "no trade on a session closing before 15:20 CT by E-029's calendar" to the zero checks.
3. **The daily limit sizes trades at DayTraders.** The engine passes `min(cushion, dll + day P&L)` as the barrier and
   the room (`lockstep.py:452-455`, 706-708), so DayTraders' $1,250 limit, not only its allowance, caps sizes. 2.3 line
   132 should say so (9.3's "contracts differ from TS's" will show it).
4. **Prior exposure** (3).
   - Line 161 says family 5's outcome "was not opened by the drafter".
   - Line 163 says program U's families are all closed, and the drafter read D-644.
   - "What is already known of the direction" (line 175) should list family 5's closure.
5. **U-5's slow end.** The three sessions are borrowed from Topstep. If DayTraders' payouts take longer, the strict
   corner is not strict in timing. A line in the written question could settle it.
6. **The operator's choice is an in-sample maximum.** It is taken over five plans and their corners on 2020-2026, with
   no confirmation (E-023 (1)). Say so beside the choice in 11.
7. **The pin's file name.** It must match the test's glob `RD-*firm*.md` (`tests/test_rd_firms_draft.py:56`), and the
   DRAFT file must be removed at the pin, since the test asserts exactly one file.
8. **DayTraders' inactivity.**
   - The record says "every rolling 30-day window". A-2's "a 21-session window from its purchase" should say rolling.
   - Dates are known, so 30 calendar days can be applied exactly instead of Stage 2's 21-session translation.

---

## What I tried that found nothing

- **Rule citations.**
  - Every backticked record key in the draft's body exists in the record and appears in Appendix R.
  - 5.2's status column equals the record's status on every row (script over the draft and the YAML).
  - The draft's own test passes on the merged tree (6 of 6, fast tier, timed).
- **Rule values against the record and ledgers.**
  - DayTraders:
    - the daily loss limit is soft and intraday, and the engine clips a trade at the limit's room through the draw's
      settlement (`lockstep.py:452-478`, 706-732);
    - the per-day Qualifying Day reading matches "A day that ends over the limit isn't a Qualifying Day";
    - the $2,600 gate, the $2,000 left and 5.3's algebra are exact;
    - the lock at $48,000 to $50,000, the $5 Pro rebill and the 30 % base (profit since the last payout) all check.
  - TradeDay:
    - the consistency shares imply 3 and 4 days;
    - Quick Pay's split and floor, and Fast Pass's ladder, cap, 45 % base and fifth request, all check.
  - Lucid: the 40 % share, three days, 2/3/4 minis, half up to $2,000, two days' lag, and news allowed.
- **Look-ahead.**
  - The adapters' decisions use only the state at a previous close, or calendar facts known in advance (minutes dates
    are scheduled; the calendar is pinned).
  - U-9 bounds a trade's path with its own outcomes and decides nothing.
  - The two conditional news runs depend on trade times, not outcomes. Exit times carry outcome information, but they
    only add described runs.
- **Leakage and selection.**
  - No parameter is chosen after a read.
  - DayTraders' grid covers the survey's script-read figure (disclosed in 3).
  - The early block is purged per measure, so its starts end inside 2023.
  - The verdict arm's whole-window bound is disclosed (6 item 2).
- **Carry language.** There is no pass line, level, pick or carry anywhere except 10.2 item 8 (m1). E-023 (1) and
  E-025's form hold: no trade is added; liquidations and skips only remove or end trades.
- **Seeds.** Section 12's search was reproduced by its test. The block's seeds appear in no other declaration, in no
  scratch directory and nowhere in the vendored snapshot.
- **D-368's daily-limit gates.** The `a.dll is None` gates on the second trade and the collect phase
  (`lockstep.py:1720`, 1744) cannot bite: neither design's protocol declares `xfa_second_trade` or `xfa_collect_from`.
- **D-324 fee re-pricing.** P-16's sizing rule carries `fee_schedule` from `fills.yaml` (`score_fv3_grid.sizing_rule`),
  so A-1's swap is one change, not two. Lucid's setup keeps Topstep's schedule, as 4.8 says.
- **9.2's oracles.** At Quick Pay, expected gross payouts on a zero-edge account stay at most $2,000 because the floor
  never falls below -$2,000. The 2/5 pass bound holds for every plan's $3,000-over-$2,000 evaluation.
- **Calendars.**
  - The BLS calendar carries the 2025 shutdown's rescheduled releases (fetched 2026-10-05).
  - The FOMC-minutes calendar's LF hash equals E-050's.
  - The CPI, NFP and statement windows are empty by construction for both designs (M4).
- **A-10's premise.** U1's bankroll never binds (`customer_slices.py:15`), so the price arithmetic is exact.
- **The reader.** The `Judged-block reads:` line parses to three purposes, none of them choosing.

## What I could not check

- **The registered trades themselves** (no bar or atlas read). I could not count the trades open at 12:58 CT on minutes
  days, nor how many trades DayTraders' 30 % rule, its daily limit, or Fast Pass's 45 % rule reaches. These are the
  reading's own first mechanics lines.
- **The gate's pairing claim.** I could not confirm that `SharedDayDraws` gives the same day draws across plans
  (10.1 item 8). T-10 could assert it.
- **The table's lookup at a `win_days` key above 5** (if an adapter stored DayTraders' 8). The adapters are not built.
- **The firms' pages today, DayTraders' price and fee basis.** Nothing was fetched.
- **Experiments specified, not run.** None is needed before the pin. M1's mapping and M3's second request reading are
  light toy-campaign tests at the build (T-2..T-5), on synthetic data.

---

## Appendix A. The synthetic checks (exploratory; synthetic data only; seeds fixed before each run)

Run with Python 3.12, numpy and scipy, in the session scratchpad. None reads the repository's data. Each listing below
is the script as run.

### A1. Interval coverage on adjacent h-start windows (M5), seed 424242

```python
import numpy as np
from scipy import stats
SEED, H, REPS = 424242, 63, 4000
def window_means(y, h):
    n_w = len(y) // h
    return y[: n_w * h].reshape(n_w, h).mean(axis=1)
def coverage(kind, n_w, rng, reps=REPS, h=H):
    n_starts = n_w * h; n_sess = n_starts + h - 1; hits = 0; lag1 = []
    tq = stats.t.ppf(0.95, n_w - 1)
    for _ in range(reps):
        if kind == "paired":
            z = rng.standard_normal(n_sess)
            ea = 0.8 * z + 0.6 * rng.standard_normal(n_sess); eb = 0.8 * z + 0.6 * rng.standard_normal(n_sess)
            ca = np.concatenate([[0.0], np.cumsum(ea)]); cb = np.concatenate([[0.0], np.cumsum(eb)])
            sa = ca[h:h + n_starts] - ca[:n_starts]; sb = cb[h:h + n_starts] - cb[:n_starts]
            y = (sa > 0).astype(float) - (sb > 0).astype(float)
        else:
            e = rng.standard_normal(n_sess); c = np.concatenate([[0.0], np.cumsum(e)])
            s = c[h:h + n_starts] - c[:n_starts]
            y = s / np.sqrt(h) if kind == "additive" else (s > 0).astype(float) - 0.5
        m = window_means(y, h); se = m.std(ddof=1) / np.sqrt(n_w)
        if se == 0: continue
        hits += abs(m.mean()) <= tq * se
        if n_w >= 3: lag1.append(np.corrcoef(m[:-1], m[1:])[0, 1])
    return hits / reps, float(np.nanmean(lag1)) if lag1 else float("nan")
def coverage_gap(kind, n_w, rng, reps=REPS, h=H):   # every other window kept
    n_all = 2 * n_w - 1; n_starts = n_all * h; n_sess = n_starts + h - 1
    tq = stats.t.ppf(0.95, n_w - 1); hits = 0
    for _ in range(reps):
        e = rng.standard_normal(n_sess); c = np.concatenate([[0.0], np.cumsum(e)])
        s = c[h:h + n_starts] - c[:n_starts]
        y = s / np.sqrt(h) if kind == "additive" else (s > 0).astype(float) - 0.5
        m = window_means(y, h)[::2]; se = m.std(ddof=1) / np.sqrt(n_w)
        hits += abs(m.mean()) <= tq * se
    return hits / reps
rng = np.random.default_rng(SEED)
for kind in ("additive", "ahead", "paired"):
    for n_w in (4, 5, 9, 15, 25): print(kind, n_w, coverage(kind, n_w, rng))
for kind in ("additive", "ahead"):
    for n_w in (4, 5, 9): print("gap", kind, n_w, coverage_gap(kind, n_w, rng))
```

Output (nominal 0.90; coverage, then the mean sample lag-1 correlation of the window means, which is biased low at
small n_w):

| kind | n_w 4 | 5 | 9 | 15 | 25 |
|---|---|---|---|---|---|
| additive | 0.837 | 0.840 | 0.831 | 0.830 | 0.829 |
| ahead | 0.829 | 0.832 | 0.835 | 0.821 | 0.833 |
| paired | 0.883 | 0.853 | 0.845 | 0.835 | 0.836 |
| lag-1 (additive) | -0.183 | -0.093 | +0.064 | +0.139 | +0.185 |

Every other window kept: additive 0.906, 0.900, 0.897 and ahead 0.872, 0.884, 0.896 at n_w 4, 5, 9.

### A2. Quick Pay under the declared request rule (M3), seed 616161

Both listings were run from the same folder. The second imports the first's split function. The first's own
unconditional run (seed 515151) is dominated by the opening's 75 % immediate breach, so it is not quoted. Its split
function is quoted as run; its first two lines compute values that are never used.

```python
# qp_request_toy.py (the split function the second imports)
def split_net(req, B):
    lo = max(0.0, min(req, B - 4000.0))
    hi_part = max(0.0, min(req, B - 4000.0)) if B - req > 4000.0 else max(0.0, B - 4000.0) if B > 4000.0 else 0.0
    above = min(req, max(0.0, B - 4000.0))
    below = req - above
    return 0.8 * above + 0.5 * below
```

```python
# qp_request_toy_cond.py: after a won $2,000 3R opening (B $6,000, gross peak $6,000, the floor frozen at start)
import numpy as np
from qp_request_toy import split_net
SEED, N, HORIZON = 616161, 20000, 251
def run(rule, edge, rng):
    out = {k: np.zeros(N) for k in ("net", "gross", "life", "breach", "ceiling", "share80")}
    for i in range(N):
        B, paid, peak, wins = 6000.0, 0.0, 6000.0, 1
        net, n80, nreq, end, d = 0.0, 0.0, 0, "horizon", 0
        for d in range(HORIZON):
            if d > 0:
                floor = min(0.0, peak - 2000.0); cushion = B - floor; r = min(250.0, cushion)
                if r >= 125.0:
                    pnl = r if rng.random() < 0.5 + edge else -r
                    B += pnl; G = B + paid; peak = max(peak, G); floor = min(0.0, peak - 2000.0)
                    if B <= floor + 1e-9: end = "breach"; break
                    if G >= 10000.0: end = "ceiling"; break
                    if pnl >= 150.0: wins += 1
            ok = B > 0 and (rule == "every" or wins >= 5)
            if ok:
                req = min(0.5 * B, 2000.0)
                if req >= 250.0:
                    nn = split_net(req, B); net += nn
                    n80 += 1.0 if nn >= 0.8 * req - 1e-9 else 0.0; nreq += 1
                    B -= req; paid += req; wins = 0
        out["net"][i] = net; out["gross"][i] = paid; out["life"][i] = d + 1
        out["breach"][i] = end == "breach"; out["ceiling"][i] = end == "ceiling"
        out["share80"][i] = n80 / nreq if nreq else np.nan
    return {k: (np.nanmean(v) if k != "life" else np.median(v)) for k, v in out.items()}
rng = np.random.default_rng(SEED)
for edge in (0.0, 0.05):
    for rule in ("every", "cadence"): print(rule, edge, run(rule, edge, rng))
```

| rule | edge | mean net paid | mean gross paid | median life | breached | ceiling | requests at 80 % |
|---|---|---|---|---|---|---|---|
| every | 0.00 | 3,624 | 5,973 | 251 | 0.402 | 0.000 | 0.191 |
| cadence | 0.00 | 3,597 | 5,901 | 48 | 0.645 | 0.043 | 0.157 |
| every | 0.05 | 3,711 | 6,140 | 251 | 0.398 | 0.000 | 0.181 |
| cadence | 0.05 | 4,213 | 6,929 | 54 | 0.490 | 0.181 | 0.160 |

### A3. The tier-1 bracket's lenient end (M4), seed 737373

```python
import numpy as np
rng = np.random.default_rng(737373)
n, steps, t0, sig = 40000, 400, 150, 0.08         # paths in stops; stop -1, target +R; liquidation at step 150
for R in (1.0, 3.0):
    x = np.cumsum(rng.normal(0, sig, (n, steps)), axis=1)
    hit_t = np.where(x >= R, 1, 0) + np.where(x <= -1, 2, 0)
    first = np.argmax(hit_t > 0, axis=1); any_hit = (hit_t > 0).any(axis=1)
    kind = np.where(any_hit, hit_t[np.arange(n), first], 0)
    W = np.where(kind == 1, R, np.where(kind == 2, -1.0, x[:, -1]))
    open_t0 = ~any_hit | (first >= t0)
    V = x[:, t0 - 1]; V, Wo = V[open_t0], W[open_t0]
    print(R, open_t0.mean(), (Wo < V).mean(), (Wo > V).mean(), V.mean(), Wo.mean(), (V > -1).all())
```

| R | open at t0 | P(W < V) | P(W > V) | mean V | mean W | V above the strict end always |
|---|---|---|---|---|---|---|
| 1 | 0.431 | 0.502 | 0.498 | +0.005 | -0.002 | yes |
| 3 | 0.710 | 0.559 | 0.441 | +0.411 | +0.416 | yes |

---

## The proposed decision row (the lead numbers and commits it)

| E-NNN | 2026-11-16 | **The red team's first read of the firms reading's second draft (Q-88, `docs/reviews/DRAFT_RD_firms_2026-11-16.md`, on master 7eaae48): must be redrafted before the pin -- five MATERIAL defects, each a text change; no run and no outcome read.** (1) The registered tables (version-12 exports) read `win_days`, `line_gap` and `request_day` from the account, and the draft never says what DayTraders', Fast Pass's and Quick Pay's adapters put there or what the `Rules` winning-day fields are, nor what an evaluation does at target while TradeDay's minimum days or DayTraders' Qualifying Days are owed -- declared per plan and tested. (2) DayTraders' fee basis is an unread term read at one point, and its strict corner is lenient in it: by Topstep's verified decomposition (`fills.yaml`, 8284213), fees on top give MNQ $1.74 and NQ $6.76 all-in against the rule's $1.22 and $3.98 -- read at both ends, a `DT-16-fees` run added, the direction sentence corrected. (3) At Quick Pay the reference's request at every close drains the cushion over a floor frozen at start, so QP's row reads the request rule (a synthetic toy: the median drained account idles out the year holding a seat) -- a second declared request reading (the reference's cadence) run beside, the rows labelled, G-10 counted, all before any QP row is seen. (4) The tier-1 bracket's lenient end (the walked outcome) is not an end -- about half the trades open at the liquidation are worth more then -- the lenient end set at the target less a tick, the walked outcome beside. (5) The 90 % interval on adjacent h-start windows covers about 0.83, because adjacent windows share sessions, and its honesty check cannot see it -- windows separated by h starts, the check rebuilt on overlapping series; reading PP's method likewise. The twelve minors applied as rules: the 0.05 comparison dropped or Holm-corrected and counted; `repeat=` and the identity stage's purpose stated; the stale reader, calendar, A-8 and Q-47 items corrected; A-9's waits on Q-76 and a seed keyword; A-11 off in the gate or dated; U-9's strict end at the next menu R; "both ends" read as declared corners; Lucid's struck $165 printed by arithmetic; the count's definitions and A-11's account kinds; Quick Pay's ceiling at two ends or a reason; the martingale count firm-wide; A-4 counting days with a trade. The eight notes are readings. A third draft (the drafter), the diff re-read, then the pin; A-8 waits for Q-80 and A-9 for Q-76. | The review and its hand-back; E-020, E-023, E-025, E-041, E-045, E-049, E-050, E-053; Stage 2 D-215, D-324, D-349. |
