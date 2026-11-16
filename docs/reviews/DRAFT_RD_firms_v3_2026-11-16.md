# Red team: the firms reading's third draft -- addendum to the first read (Q-88b, 2026-11-16)

**Target.** `prereg/DRAFT_RD_firms.md` at `wt/wt-firms` 0fabc11, third version. Its LF sha256
`00855c26113ffb0689913fbe6c32233ae28a258efc1c5b61f9ab8d56c4480e61` was recomputed here and matches the lead's.

**Read.** The diff against the second version I reviewed (7eaae48), in full. My first read
(`docs/reviews/DRAFT_RD_firms_2026-11-16.md`) is committed unchanged as 6a40aab; I checked its hash.

**Also read, to settle the drafter's three named interpretations and the new claims:**

- DECISIONS E-055..E-063 (E-064 is not yet on file);
- `extended/user_beside.py` on master (Q-76, E-059);
- the vendored `risk_policy.py` (`Tiers.decide`), `state_policy.py` and `lockstep.py`;
- Stage 2's `config/rules.yaml` and `DECISIONS.md` (D-574);
- the registered no-closure table that both designs use (`state_dp_e-0.050_lamstar_noclose`, Stage 2's
  `results/state_policy_v12_noclose_policies.json`). It is a design file: its decisions per state, no outcome of any
  plan.

**Checks.** No bar, no atlas table, no plan's result was read, and no engine ran. `tests/test_rd_firms_draft.py`
passes 6/6 at 0fabc11. No synthetic check was needed this time.

## Verdict: pinnable after one small edit (its named pre-run conditions aside)

Every MATERIAL finding of the first read (M1-M5) is fixed as the remedy asked. So is every minor (m1-m12) and every
note, each in the place the review named.

Nothing in the fixes introduces look-ahead, an unverified rule, carry language, or a choice made after a read:

- **Inputs.** The new inputs are read at prior closes or from calendars.
- **New rules.** The new ends rest on verified rules: Topstep's decomposition in `fills.yaml`; Quick Pay's withdrawal
  sentence. The one stated-but-unsized cap is read by U-10.
- **The 0.05 comparison** is gone.
- **The new choices** (the held reading, the day-logging micro, the reference's cadence) were made on the vendored code
  and on my synthetic toys, never on a plan's outcome.

The fixes leave **five MINOR items and three notes**. Each is a sentence or a table cell, none needs a run, and they
should go in before the pin, since the pin freezes the text. One of them (n1) corrects a premise of the drafter's own
interpretation (3). A check of that edit's diff by the lead or the gatekeeper suffices; no third red-team read is
needed.

The pre-run conditions stand as the draft's 15 states them: Q-80 before A-8; A-9's keywords (n2); A-1..A-7 and A-9..A-11
built with their tests.

## Each finding of the first read, against the third version

| finding | fixed? | where | residue |
|---|---|---|---|
| M1 the table's inputs | yes | 4.9 (403-447), 2.3, G-6, A-2..A-7, T-14 | n1, n3 |
| M2 DT's fee basis | yes | 4.8, U-12, 5.2, 7.2 `DT-16-fees`, G-5, 16 | n4 (the bound list) |
| M3 QP's request rule | yes | 2.3, 5.6, 7.2 `QP-16-req`, 9.3 G-10, 10.1, 11 | -- |
| M4 the tier-1 lenient end | yes | U-11, 5.5 (626), 7.2-7.3 (four conditional runs) | note A |
| M5 the interval's windows | yes | 10.2 items 1-7 | -- |
| m1 the 0.05 comparison | yes, dropped; its seed reserved, never drawn | 10.2, 12 | -- |
| m2 `repeat=`, the identity stage | yes | 6 item 6, 9.1, 15 | -- |
| m3 stale items | yes | 4.6, 5.5 (the E-050 hash cited), 15, 16 | -- |
| m4 A-9's waits | in text; attributed partly wrongly | 4.6 A-9 (357), 15 (1090) | n2 |
| m5 A-11 in the gate | yes, off and labelled | A-11, 10.1 item 8 | -- |
| m6 U-9's ends | yes (R_hi, the profitable flatten, the stop-first booking named) | 5.4 | -- |
| m7 corners as bounds | yes | 5.1 (499), 11 | n4 |
| m8 Lucid's $165 | yes; the coupon's basis cited to Stage 2 D-574, which does record it | 4.2, 10.1 item 9 | -- |
| m9 the count's definitions | yes | 5.5, 9.1 item 2 | -- |
| m10 QP's ceiling | yes, two ends, `QP-16-ceil` | 5.2 (536), A-7, U-6 | n5, note B |
| m11 martingale firm-wide | yes | 9.3 | -- |
| m12 A-4's trading days | yes | A-4 (353) | -- |
| notes 1-8 | yes | 5.3, 9.3, 2.3, 3, 16, 11, 15, A-2/A-3 | -- |

## The drafter's three interpretations

1. **DayTraders' lenient fee end: the listed figures as all-in ($1.02 / $3.98). Holds.**
   - The page gives the figure as the commission at least, so all-in is the least the cost can be, and fees on top only
     add to it.
   - The strict end's arithmetic is right: 1.02 + 0.70 + 0.02 = 1.74 and 3.98 + 2.76 + 0.02 = 6.76, from Topstep's
     decomposition in `fills.yaml` (lines 32-35).
2. **Quick Pay's ceiling, lenient end: the whole remaining balance withdrawn at the ceiling's close, at the tiered
   split. Holds on the pages' words.**
   - "You can withdraw at any time as long as your account balance is positive."
   - The review sentences say "stop trading", not "stop withdrawing".
   - No cap is stated, so U-10 reads none.
   - It sits awkwardly with two other lines of the draft (n5), and it makes the term monotone (note B).
3. **"The registered table's own request-day cells already sit that session out", so A-5 only asserts it. The premise
   does not hold** (n1).
   - The solve leaves the request day out of the winning-day count (`state_policy.py:1017`) but nowhere forbids a trade
     on it.
   - In the no-closure table both designs use, the leaves reachable with `request_day = 1` trade in **526 of 630 funded
     and 326 of 678 paid** cases. These are unweighted leaf counts; they include day-0 fill in unvisited bands (D-332),
     and no visitation is on file to weigh them.
   - The comment the draft cites (`state_policy.py:1338-1339`) describes why the request day has its own cell. It is
     not a guarantee.
   - The behaviour the draft also states, "acts only where a cell would trade", is the right one if "acts" means it
     forces the session untraded.

## Findings on the third version

### MINOR

**n1. A-5's premise is false, and "asserts" would stop the build** (A-5, line 354). Fast Pass forbids trading from the
request until the payout arrives, but the registered table trades in many request-day cells (above).

- **The failure it allows:** if A-5 is built as an assertion, the run stops at the first Fast Pass request whose cell
  trades.
- **Remedy:**
  - A-5 sets the post-request session to no trade wherever the cell would trade, and passes the signal over as declared;
  - 9.3 counts those sessions;
  - T-3 includes a request-day cell that trades;
  - strike "already sit that session out".

**n2. A-9's two keywords are not Q-76's** (A-9, line 357; 15, line 1090). Q-76 as merged (E-059; `extended/user_beside.py`
on master) gives `funded_account_cls=` as a keyword. But `base_problems` still refuses `household_closure` on the path,
and the run loop still seeds starts from Q-17's own base (`start_seed(s)`).

- **Lucid's strict reach** needs nothing: the engine's default takes the class's own rule (`lockstep.py:1397`).
- **Lucid's lenient reach** (only that account ends) needs `household_closure=False`, which the ladder over LU's lenient
  corner (10.1 item 7) cannot pass today.
- **Remedy:** name both as A-9's own build items, each with U1's start-row identity at its default:
  - a `household_closure` route, either a keyword or a Lucid subclass whose `HOUSEHOLD_CLOSES_AT_LIVE` is False, declared
    now;
  - the ladder's seed base as a keyword.

  Then drop "which Q-76 lifts" for these two.

**n3. The day-logging micro may take every routed signal** (4.9, line 438: "each later routed signal is taken at one
micro"). A TradeDay evaluation at target logs a day with one trade.

- **The failure it allows:** under the longest-waiting router, it would take further signals the same session, each at
  one micro. That diverts signals the funded accounts and other evaluations would have taken, and adds fees, to no
  purpose.
- **Remedy:** at most one trade a session in that state (`max_trades` 1); T-5 asserts it.

**n4. DayTraders' fee basis is not monotone per start** (5.1, line 499, lists it among "the terms that act in one
direction on every start"). A per-trade cost changes every trade's net, and through it:

- the balance bands the table reads;
- which days reach DayTraders' $200 Qualifying minimum;
- passes and breaches.

So two starts can move in opposite directions. The prices, U-3's fees, the lag and the fifth request are monotone,
because they move cash only. **Remedy:** move the fee basis to the declared-corner list, or say "monotone per trade, not
per start".

**n5. The ceiling's lenient withdrawal contradicts two lines of the draft.** The whole-balance request is above the
reference's amount, so two lines become false at `QP-*-l` and `QP-16-ceil`:

- 9.3's zero check "QP requests above the reference's amount" (line 859) fires by construction;
- 5.2's and U-7's "QP per-request cap ... moot ... a check shows no request above it" (lines 533, 476) no longer holds.

The withdrawal is also silent on TradeDay's $250 minimum. **Remedy:**

- exempt the ceiling's closing withdrawal from that check;
- cite U-10 for reading Quick Pay's unstated cap as none at that one request;
- state that no request below $250 is made.

### NOTE

**A. The tier-1 lenient end is a tick short of the best.** It books the target less a tick (line 626). A walked target
fills only when traded through, so the price at 12:58 can equal the target itself. One tick; immaterial.

**B. Quick Pay's ceiling is monotone per start.** Both of its ends end the account at the same close on the same path,
and the lenient end only adds cash. Listing it as a declared-corner term (5.1) errs on the safe side.

**C. The verdict arm and liquidated trades.** Neither version says whether the verdict arm's per-R shift applies to a
trade booked by the liquidation (either end, or "no liquidation"). Say which.

## What I tried that found nothing

- **The drafter's new claim that a `win_days` above the top threshold reads the top cell.** True: `Tiers.decide`'s top
  tier is open (`risk_policy.py:113-120`).
- **4.9's DT mapping** `min(5, max(0, q - 3))` aligns eligibility at 8 Qualifying Days. The held reading at 4 depends
  only on the state at a close. The FP and QP rows follow 4.9's rule as written.
- **Topstep's cadence fields.** `xfa_std_winning_days` 5 and `xfa_std_winning_day_min` $150 are verified in Stage 2's
  ledger, as 5.6 uses them.
- **Run counts.** 30 = 2 + 16 + 12 (DT 4, FP 3, QP 4, and `QP-16-req`), or 34 with the four conditional runs. This is
  consistent in the header, 7.3, 13 and 15. The ladder (27) and the gates (16) are unchanged.
- **Section 12.** One seed moved from in use to reserved, never drawn; the test holds.
- **10.2's honesty check** is rebuilt on overlapping series as A1 built them. The 0.88 label will fire at small n_w for
  0/1 measures, as it should (A1 measured 0.872 there).
- **Carry and level language.** None: the 0.05 and one-sided hits are the notice of the drop.
- **The early-close zero check** cites E-029's calendar and D-215.

## What I could not check

- **The request-day cells' visitation.** No per-cell visitation is on file, so n1's counts are not weighted. The remedy
  does not depend on the weights.
- **Whether A-2 can see dates.** The U1 replay hands an account its sessions without dates, so A-2's exact 30-day window
  needs the start's calendar passed in. That is a build detail; T-2 tests it.

## The proposed decision row (the lead numbers and commits it)

| E-NNN | 2026-11-16 | **The red team's read of the firms reading's third draft (Q-88b, `docs/reviews/DRAFT_RD_firms_v3_2026-11-16.md`, on `wt/wt-firms` 0fabc11, LF sha256 `00855c26113ffb0689913fbe6c32233ae28a258efc1c5b61f9ab8d56c4480e61`): pinnable after one small edit -- M1-M5, m1-m12 and the notes of the first read fixed as remedied; no new look-ahead, unverified rule, carry language or choice after a read.** The drafter's interpretations: DayTraders' lenient fee end (the listed figures all-in) holds; Quick Pay's ceiling's lenient end (the whole remaining balance withdrawn at the split) holds on the pages' words; **"the table's request-day cells already sit the session out" does not** -- in the registered no-closure table, leaves reachable with `request_day = 1` trade in 526 of 630 funded and 326 of 678 paid cases (unweighted), the solve only leaving the day out of the winning-day count. The edit, five minors as text: (n1) A-5 forces the post-request session untraded wherever its cell would trade, counted, T-3 with a trading cell, never an assertion; (n2) A-9's `household_closure` route (for Lucid's lenient reach) and the ladder's seed base are A-9's own keywords, each with U1's identity at its default -- Q-76 as merged gives only the class keyword; (n3) the TradeDay day-logging micro at most one trade a session; (n4) DayTraders' fee basis moved from the monotone list (a per-trade cost moves the path); (n5) the ceiling's whole-balance withdrawal exempted from 9.3's "QP requests above the reference's amount" and from U-7's moot cap, read by U-10, the $250 minimum kept. Three notes as readings (the tier-1 lenient end a tick short; the ceiling monotone; the verdict arm's shift on liquidated trades stated). The edit's diff checked by the lead or the gatekeeper, then the pin; Q-80 before A-8, A-9's keywords before A-9. | The review and its hand-back; E-049, E-058, E-059; Stage 2 D-332, D-574. |
