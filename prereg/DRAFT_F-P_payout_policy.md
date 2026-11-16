# DRAFT: payout policy in a user's first months (reading PP) -- a described reading, unnumbered, not declared

**Status: DRAFT, second version, 2026-11-16 (TASK_QUEUE Q-42).** It redrafts the first version (Q-25, E-018) on the red
team's review (`docs/reviews/DRAFT_F-P_payout_policy_2026-11-16.md`, Q-31) and under the operator's ruling **E-023 (1)**
(`CHARTER.md` section 3).

**What E-023 (1) makes of it.** Levers that add no trades are **described, never carried**. So this file is a
**described reading**, not a family:

- it takes **no program family number** and spends **nothing** of the multiplicity budget;
- **no cell can carry, pass or fail**: there is no pass line, no level and no pick;
- every policy is read on the journey scorecard, for the operator to choose from the menu;
- it is declared and pinned before its run, by its own decision row with its sha256, so nothing in it is chosen after
  a look.

**Not pinned. No engine has been run for it, no cell built, no outcome of any payout policy computed or read.**
Anything chosen after a reading is exploratory and reported apart.

**Appendix A is a separate, labelled item.** It is an EXPLORATORY check of Stage 2 D-566's buffer reading (the red
team's N1). It is not part of this reading, and it gets its own decision row when run.

| field | value |
|---|---|
| reading | PP: how much a funded account withdraws, and when, in a user's first months -- on P-14's registered trades, P-16's beside |
| kind | a **described reading** (E-023 (1)): never carried; the operator chooses from its menu |
| program family number | **none** (E-023 (1)); the next numbered family's k is unchanged by this file |
| level, pass line, pick | **none** |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16, read only through P-14's and P-16's registered trades (this reading reads no bar) |
| the unit | one start day, replayed as U1 replays it (`vendor/stage2/docs/USER_MILESTONES.md`); each cell paired with its base on the same start |
| blocks | all starts (the menu's headline); the early block, purged per measure by `u_select.block(records, "early", h)`; the late block from 2024-01-02 (section 5) |
| cells | 2 first-request rules x 2 amounts x 2 trade streams = **8 policy runs** (6 new, 2 references that must reproduce registered rows), plus **3 rule-sensitivity runs** on P-14 (6.3) = **11 runs** |
| the menu | the 6 new policy cells and their 2 references, each read against its base |
| seeds | from 20261940 to 20261949: four in use, five retired with the first version's pass line, one reserved (section 11) |
| confirmation | none: nothing is carried (section 10) |

---

## 0. What changed from the first version, finding by finding

| review item | the first version | this version | where |
|---|---|---|---|
| E-023 (1), F4 | a family taking the next program number, with three pass lines proposed (PL-1, PL-2, PL-3) | a described reading: no number, no budget spent, no pass line, no pick, no stage B or C; this is PL-3, unnumbered, as the red team recommended | header, 1, 12 |
| F1 (CAC) | 7.3's sign-flip null check, blind to skewed nulls and inverted at the family's level | removed, with the pass line it guarded; the reading's intervals are declared plainly as descriptions, and their coverage on skewed, lumpy nulls is printed beside | 9.2 |
| F2 | "far more powerful" offered as a reason a paired P test could carry | why E-023 describes rather than tests, stated with the review's citation; each reading's minimum detectable difference printed beside it | 1, 9.2 |
| F3 | PL-2's look-ahead, block length, power and missing guards | removed with PL-2; the per-measure purge (F6) covers every reading | 5 |
| F5 | the held-state rule classed "FIXED, no fitted value" | **a declared design choice**, its alternatives named, its held sessions reported by class (unchanged / rescued / R changed), and the minimal rescue run beside on P-14 | 6.3, 9.1 item 6 |
| F6 | one 63-session purge, and "Program U's families did not purge" (wrong) | `u_select.block(records, "early", h)` per measure, at each measure's own horizon h; the sentence corrected | 5 |
| F7 | `lock` through `_standard_eligible`, which makes the recorder's `eligible` the policy's | the firm's eligibility kept in its own field and restored after `trade_day`, so the recorder writes the firm's; tested | 13.1 |
| F8 | a replication count to be fixed after the series existed | every count and seed fixed in this file | 9.2, 11 |
| F9 | PL-1 and PL-2 put a user measure in the pass line | moot: no pass line; E-023 amended the charter | -- |
| F10 | "a payout policy changes no trade"; differences "mostly zero" | stated truly: the offered trades are the same; after the first changed payout, executed sizes, R, accounts, purchases and fees diverge and stay diverged; the per-start difference is lumpy, and dense for `half` | 0.1, 6.4 |
| F11 | the request amount's freedom not listed | listed under "Assumed", with an optional rules-verifier reading | 4 |
| N1 | the doubt about D-566 in an open item | a separate, labelled exploratory check, fully specified | Appendix A |
| N2 | -- | the verdict arm's bound read on the whole window, disclosed | 3, 5 |
| N3 | P-16's `half` cell already read in D-564's journey | kept, disclosed | 3 |
| N4 | -- | months 1-3 are where both levers cost most by their mechanics; any gain should show at months 6-12; the menu reads every month | 2, 9 |
| N5 | -- | a rule for a series that is zero on every window, and for too few windows | 9.2 |
| N6 | "the remaining balance becomes the loss floor" | "the remaining balance is all that can be lost" | 2 |

### 0.1 What a payout policy changes, stated truly (F10)

A payout policy leaves the **offered** trades unchanged: the same registered entries, the same outcome of each offer at
each R, the same days in the same order. So each cell is a matched pair with its base on every start day, and the
market path's luck is shared.

It does **not** leave the **executed** trades unchanged. From the first payout it changes, an account's balance, floor
and scaling tier differ. From then on these diverge, and they stay diverged:

- the table's size and R for that account;
- which account the longest-waiting router hands each later offer to, under the strict one-position rule;
- the evaluations bought (20 in 21 sessions) and the seats' use;
- the fees paid.

`half` changes every payout. `lock` changes the first payout of every account whose loss limit had not locked.

For P, a start's difference is nonzero only where a month's "ahead" flips, so it is lumpy. For `half` it is dense, not
sparse.

## 1. What this reading is, and why it is described rather than tested

**Its job.** It shows the operator, for each payout policy and each month of a user's first year, how many users the
policy helps, how many it hurts, by how much, with what uncertainty, and how much "ahead" each step of evenness costs
(E-014, E-015). The operator then chooses from that menu.

**What it is not.** A claim of an edge, a candidate, or a registered design. A payout policy is a choice a user can
change at any time, and it adds no trades.

**Why E-023 made it a description.** The red team's F2 used audit B's same-trades standard errors
(`docs/audits/phase0/B_objective.md`) and the late block's few independent three-month stretches. On those, no test
at a numbered family's level can show a payout-policy difference in P unless it is several times larger than any P
gain Stage 2's 66 cells ever reached. And the first version's null check pointed the wrong way (F1). The ruling
followed: describe, never carry.

**What the operator's choice from the menu will mean.**

- It is recorded in its own decision row as the operator's choice from a described development reading.
- It takes no registration id and no confirmation.
- Every statement made from it is a description of the development window.
- Under E-023 a lever that adds no trades is never carried. A later test of a payout policy would need the operator to
  change that ruling first.

## 2. The mechanism

**The contract's arithmetic** (every value verified, section 4):

- A $50K funded account (XFA) starts at a balance of $0 with its loss limit (MLL) at -$2,000, trailing upward. The MLL
  locks at $0 once the balance reaches $2,000 (8284204).
- At the first payout the MLL is set to $0 wherever it was, so the remaining balance is all that can be lost (8284204,
  8284233).
- A request takes at most 50 % of the balance and at most $2,000 on the Standard path, with a $125 minimum. The user
  keeps 90 % (8284233).
- A request needs five winning days of at least $150 since the last payout, and a profit since the last payout; the
  first payout is exempt. The request day does not count toward the next five (8284233).
- A payout that lowers the balance lowers the scaling tier (`scaling_tier_after_payout`, 8284233; Stage 2 D-53).

**The mechanism (propsim D-45).** A first payout taken while the MLL is still below $0 moves the floor up to $0 at
once. The account loses the cushion between its old floor and zero, as well as the cash it withdraws: an early payout
strands a small balance. Once the MLL has locked at $0, that cost is gone.

**The two levers, within the verified rules:**

- **When** -- `lock`: hold the first request until the MLL has locked.
- **How much** -- `half`: take half of the maximum each time, leaving more of every balance in the account.

Both keep accounts alive longer, which means more chances at later payouts and at months with a payout. Both cost cash
now, the first payout included.

**Where to look (N4).** Within P-14, the first month moves most with whether and how soon a first payout came (handoff
1.2, `results/user_drivers.csv` section `within_design`). So months 1 to 3 -- the window of P -- are where both levers
cost most, by their mechanics. A gain from keeping money in the account, if there is one, should show at months 6 to
12, where the late block has the fewest independent windows. The menu therefore reads every month, not P alone.

**Whose accounts, and how.** One user's own five Topstep seats, each with its own trades, one position at a time across
the firm (Stage 2 D-157, D-429; E-012 (3)). Every trade and every payout request is made by hand (E-008). A payout
request is not trading conduct.

## 3. Prior exposure: what has already read payout policy, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| stage one, propsim D-44/D-45 (`vendor/stage2/vendor/propsim/edge/T5_RESULTS.md` section 3) | a buffer against taking the maximum, on stage one's binary process | synthetic draws, no NQ | holding a balance beat taking the maximum, before lag, reinvestment and costs were priced; exploratory | the mechanism's source; a hint, not a setting |
| Stage 2 T7's grid (`propedge/campaign/protocols.py`, `t7_grid.py`) | buffer and fast-payout arms, registered as arms | -- | no row in the vendored log records the comparison read (searched "T7", "buffer", 2026-11-15) | none read |
| Stage 2 D-564 to D-566 (`results/rc150_payout_screen.csv`, not vendored) | on **P-16's cell**: `keep_balance` $0 / $1,000 / $2,000 x `payout_frac` 1.0 / 0.5, and a 4-5 PM request beside | 500 gate paths at seed 20261131, and D-518's start-day journey on the verdict arm over the whole development window | taking the maximum at the first eligible close grew most; the $1,000 buffer was about level; the $2,000 buffer and every half request cost growth and raised the bankroll; days to the first payout unchanged (D-566) | **P-16's `half` cell here is close to D-564's half request with no buffer**: its direction on growth is known, and its journey was read by the program (N3). No payout cell was ever run on P-14. No hold of the first request alone, tied to the MLL's lock, was ever run. Appendix A checks whether the buffer cells' readings carry an artefact |
| Stage 2 program U, family 6 (D-646, D-648) | the Consistency path, on P-14's and P-16's trades and tables | start days, both blocks | closed: on these tables the path pays almost no one | why this reading is Standard only |
| Stage 2 program U, families 7 and 8 (D-653 to D-655, D-658, D-661) | flat funded plans | start days, both blocks | closed (7: paid sooner but less than the fees; 8: the size trend ran out) | the funded leg here is always the table's |
| U1 (D-620) and this repository's Q-05 identity (E-010) | P-14's and P-16's own journeys, every start | all starts | the reference rows each cell pairs against | the references are known in full; only the cells are new |
| program U's nine families | P on the late block against P-14 | starts from 2024 | all closed | the late block has been read for P nine times; it is late development, not out of sample |

**The verdict arm's bound reads both blocks (N2).** The verdict arm shifts every R's outcomes to P-14's (P-16's)
registered one-sided bound. That bound was estimated on the whole development window, 2020-01-01 to 2026-07-16
(`vendor/stage2/prereg/P-14_a3-brk30-cb20.md`). So an early-block reading on the verdict arm is a function of
2024-2026 through that one constant. It shifts both members of every pair alike, it is inherited from program U, and
no purge removes it. The `point` arm, read beside, carries no such shift.

**The drafter's own reads (disclosed).**

- The vendored no-closure table's leaves (`results/state_policy_v12_noclose_policies.json`, policy
  `state_dp_e-0.050_lamstar_noclose`, which P-14 and P-16 both use). This is a registered configuration, not an
  outcome.
- The engine's payout code, the U1 runner, the gate, `u_select.block`, and the header of the vendored D-564 runner
  (`scripts/rc150_payout_screen.py`).
- No result file of any payout cell was opened.

**What is already known of the direction (disclosed).** A lever that delays or shrinks the first payout is expected to
cost month 1 (handoff 1.2). On P-16's trades, half requests cost long-run growth (D-566 (3)).

**Why this is not Stage 2's question.**

1. **The objective.** Stage 2 ranked by two-year growth on the required bankroll; this reading shows a user's first
   months and year, month by month.
2. **The lever.** Stage 2's buffer holds every request, the paid ones included. `lock` holds only the first request, and
   only until the MLL has locked -- D-45's floor reset, isolated.
3. **The base.** P-14, on which no payout cell was ever run.
4. **The unit.** Paired start days, not bootstrap paths.
5. **The held states.** A declared rule for accounts that a policy leaves eligible and unpaid (6.3); Stage 2's buffer
   cells had none (Appendix A).

## 4. Contract fit, and the verified rules every cell leans on

Every rule below comes from Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`, as E-002 vendored it). Each is
loaded through the engine's own rule loader and never typed into code (13.2).

| ledger key | value | article | read | used for |
|---|---|---|---|---|
| `payout_max_frac_of_balance` | 0.5 | 8284233 | 2026-11-14 | the maximum request |
| `xfa_std_cap` | $2,000 (no DLL election) | 8284233 | 2026-11-14 | the maximum request |
| `payout_min` | $125 | 8284233 | 2026-11-14 | a request below it is not made |
| `profit_split` | 0.9 | 8284233 | 2026-11-14 | cash to the user |
| `xfa_std_winning_days`, `xfa_std_winning_day_min` | 5 days of at least $150; the request day excluded | 8284233 | 2026-11-14 | eligibility |
| `require_profit_since_payout` | true (the first payout exempt) | 8284233 | 2026-11-14 | eligibility after the first |
| `xfa_mll_start`, `xfa_lock_at` | -$2,000 trailing; locks at $0 once the balance reaches $2,000; $0 after the first payout | 8284204, 8284233 | 2026-11-14 | the floor; `lock`'s condition |
| `payout_fee`, `payout_lag_days_aeropay` | $0, 3 trading days (derived, D-24) | 8284233 | 2026-11-14 | the method (Aeropay, the US baseline) |
| `payout_after_request_survives_mll_breach` | true | 8284233 | 2026-10-30 | a request followed by a breach is still paid |
| `scaling_tier_after_payout` | resets with the balance | 8284233 | 2026-10-03 | a payout lowers the tier (D-53) |
| `max_active_funded_accounts` | 5 | 8284215 | 2026-10-03 | the seats |
| `xfa_payout_path_choice` | chosen at activation, cannot be changed | 8284215 | 2026-11-14 | why no cell can switch path |

**Assumed, because no page states it:**

1. **The request's timing** (Stage 2 D-175, `propedge/contract/payout_timing.py`), as in every registered row. The
   request is made after 5:00 PM CT, so the next session is the request day. The balance and the floor move at the
   request, before the request day trades.
2. **The request's amount (F11).** A request may be any amount from the $125 minimum up to the maximum. The ledger
   quotes "Max Payout per request: 50% of your account balance up to the cap" and "Minimum Payout: $125"
   (`payout_max_frac_of_balance`, `payout_min`), not that the amount in between is free. `half` needs it. D-564 made the
   same inference. An optional rules-verifier reading of the request form's amount field (8284233) would settle it
   (section 15); until then it stands as an assumption, named wherever `half` is read.

**Not modelled, as in every registered row:** that payouts are unavailable in holiday hours (13350348), and the move to
a Live Funded Account.

**Inherited from P-14's (P-16's) registered trades and checked, not re-derived (8.1):**

- latency of at least five minutes (D-266);
- one position at a time, with five minutes flat (D-429);
- resolution and realised risk (D-212 (1), (2) as D-308 (3) raised it);
- the stop band and the cost floor;
- the report-day and FOMC rules (E-007 (d)).

**Conduct.**

- Tier 1: untouched.
- Tier 2: the Responsible Trading Program is off in the base case (D-289) and on beside.
- Tier 3: priced. The payout-denial ladder (10, 25, 50 %) is beside the 0 % reading, and carries Terms of Use s.8
  (E-013 (1)). A payout policy changes how many payouts a user requests, and so how often the firm's discretionary
  review is met, so the ladder is read per cell (9.1 item 7).

## 5. Data, blocks and the unit

1. **The unit** is U1's: one development start day, with a fresh bankroll and fresh accounts, the base's trades replayed
   in historical order. U1 runs a long replay of up to 252 sessions plus its exact runs (`scripts/user_journey.py`,
   `customer_slices.replay`). The headline is the `verdict` arm (every R at its registered bound), with `point` beside.
   `USER_MILESTONES.md`'s definitions are used unchanged. A month is 21 sessions.
2. **Pairing.** Each cell and its base run on the same start days, the same blocks and the same seeds. The per-start
   difference is the unit of every paired reading.
3. **The blocks, per measure (F6).** Every reading at horizon h (63 for months 1 to 3, 126 for month 6, 252 for month
   12, and so on) is read on three sets of starts:
   - **all starts** with h sessions left (`u_select.block(records, None, h)`) -- the menu's headline;
   - **the early block**, `u_select.block(records, "early", h)` (`propedge/research/u_select.py`): the starts of 2023
     and before, less every start within h sessions of 2023's last start. No early reading touches a 2024 session,
     except through the verdict arm's bound (N2, section 3);
   - **the late block**, `u_select.block(records, "late", h)`: the starts from 2024-01-02 with h sessions left.

   This is the house rule, D-621 (4)(b); program U applied it, and the first version's sentence that it had not was
   wrong. Nothing is chosen on any block. The early and late blocks are read separately so that the menu can flag a
   policy whose effect changes sign between them (9.1 item 10).
4. **How much each block holds.** The late block holds about nine non-overlapping 63-start windows (B_objective, Q3),
   and fewer at months 6 and 12. All starts hold several times more. Each reading prints its own count of windows
   (9.2).
5. **No NQ from 2026-07-17** is on disk or read.

## 6. The cells

### 6.1 The two levers

| lever | values | what the user does |
|---|---|---|
| **L1, the first request** | `elig` (P-14's) / `lock` | `elig`: request at the first close at which the account is eligible and the request reaches $125. `lock`: request the first payout only at an eligible close at which the account's MLL has locked at $0 (its balance has reached $2,000 at some close, 8284204); until then, keep trading and ask nothing |
| **L2, the amount** | `max` (P-14's) / `half` | `max`: the most allowed, min(50 % of the balance, $2,000). `half`: half of that (the engine's `payout_frac` 0.5); not made if below $125 |

- **Cadence.** After the first payout, a request is made at **every eligible close** (P-14's cadence).
- **Scope.** L1 acts on the first request only; once a payout is made, the MLL is $0. L2 acts on every request.
- **Why `lock` keys on the floor.** It is defined by the MLL's lock, not by the balance now: an account that reached
  $2,000 and fell back has its MLL at $0 already, and its first payout strands nothing.

### 6.2 The grid

| cell | L1 | L2 | on P-14's trades | on P-16's trades |
|---|---|---|---|---|
| `ref` | `elig` | `max` | P-14 as registered: the identity (8.1) and every pair's reference | P-16 as registered: the identity and reference |
| `lock` | `lock` | `max` | new, on the menu | new, on the menu |
| `half` | `elig` | `half` | new, on the menu | new, on the menu |
| `lock_half` | `lock` | `half` | new, on the menu | new, on the menu |

The two levers are fully crossed, so each lever is read at both settings of the other, and their interaction is read
too (9.1 item 5).

### 6.3 The held-state rule -- a declared design choice (F5)

**Why a rule is needed.** P-14's table (`state_dp_e-0.050_lamstar_noclose`, D-501) was solved with every request at
the maximum at the first eligible close. So no P-14 account starts a session eligible and unpaid with a request of at
least $125. The table's leaves for those states are "the table's own decision where its chain never visited" (its v11
export note), and many of them trade nothing:

- the paid phase: "no-trade leaves at five winning days with profit since the last payout (every balance band from
  $500 up)" (D-654 (3));
- the funded phase: "no-trade leaves at five winning days (a quarter of those states, at the lowest cushion bands)"
  (D-654 (9)).

The funded and paid phases key only on balance, cushion, winning days, line gap and the request-day flag. None of these
moves while an account sits, so an account a policy leaves unpaid at such a leaf sits for good, holding its seat. That
is an artefact of a table solved for another policy.

**The rule (declared, not neutral).** An account is **held** at a close when both of these hold:

- it is eligible by the firm's Standard rule, and P-14's request, min(50 % of the balance, $2,000), would reach $125;
- the cell's policy makes no request, or a request below $125 (L1's hold; L2 on a balance below $500).

At the next session's start, a held account's table decision is read **with its winning days counted as 4**. That is the
table's own leaf, at the same balance, cushion, line gap and request-day flag, for an account still one winning day
short of eligibility. "Held" is re-read at every close. An account that is no longer firm-eligible is not held, and the
table is read as it stands. The firm's count and eligibility are never changed (13.1).

**Why it is a design choice.** In the bands where the table's own five-day leaf is no-trade, any trading leaf is a
sizing design. The four-day leaf was solved for an account whose next winning day triggers its payout, which is false
for a held account (the review's F5). Its reach is concentrated where `lock` binds: the lost-opening accounts that live
and recover, which hold most of the pre-payout account-days (handoff 2.5).

**The read of the vendored file, re-derived by T-4.** The four-day leaf trades in every state a held account can be in:
a balance of at least $250 and no request the day before, funded or paid. Against the table's own five-day leaf, the
rule leaves the leaf unchanged in most bands of `lock`'s held region and replaces a no-trade leaf in the rest. In two
funded bands where the five-day leaf trades, it changes R and leaves the risk unchanged. The review counted these from
the file, and the drafter's own walk of the file agrees; T-4 lists them.

**The alternatives, named:**

- **The minimal rescue** -- the table's own five-day leaf wherever it trades, and the four-day leaf only where the
  five-day leaf is no-trade. It differs from the declared rule only in the two R-changed bands. **Run beside** for
  P-14's three new cells (`lock`, `half` and `lock_half` under the minimal rescue: 3 runs, labelled "rule sensitivity",
  never on the menu), so the reader sees what those bands do.
- **The zero-day leaf** -- reading a held account as one whose cycle has just restarted. Not run: it is false to the
  account's state, because its five winning days stand.
- **Re-solving the table for each policy.** Not run: that is a new sizing design and a search, and D-564 kept the table
  as solved too.

**Reported by class (9.1 item 6).** For every cell, the share of its funded account-sessions read under the rule, split
by class: *unchanged* (the four-day leaf equals the five-day leaf), *rescued* (the five-day leaf is no-trade) and *R
changed*. In `ref` the rule never fires (8.1 item 4).

### 6.4 What is paired, and what diverges

See 0.1. The pairing is on start days with identical offers, not on identical executed trades. A check confirms every
trade a cell takes is one of its base's registered offered trades (8.1 item 5). The divergences -- sizes, R, which
account takes which offer, evaluations bought, fees -- are the policy's effects, and the reading reports them (9.1 item
6).

## 7. Parameters: fixed, described, dropped

### 7.1 The table

"Described" means every value listed is run and read, and the program chooses none of them; the operator chooses from
the menu.

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| trades | what is traded | fixed | P-14's registered trades (A3-BRK30-CB20), by U1's own builder | E-010; D-513 |
| trades, beside | the second stream | fixed | P-16's registered trades (`rc_s150_all_nr`), `rc150_dev_test.TRADES_SHA256` | E-002; D-544 |
| state table | sizing by account state | fixed | `state_dp_e-0.050_lamstar_noclose`, checked against `a3_brk30_cb20.NOCLOSE_POLICIES_SHA256`; not re-solved | D-501; D-564 (2) |
| held-state rule | what a held account trades | **fixed, a design choice** | the table read at four winning days (6.3); the minimal rescue beside | 6.3; the review's F5 |
| seats, budget, routing | accounts and purchases | fixed | each base's own: five seats; 20 evaluation purchases in 21 sessions; the strict one-position rule | P-14's and P-16's registrations |
| payout path | Standard or Consistency | fixed | Standard | 7.2 |
| **L1, first request** | when the first payout is asked | **described** | `elig`, `lock` | 6.1; 8284204's lock |
| **L2, amount** | how much each request takes | **described** | `max`, `half` (`payout_frac` 1.0, 0.5) | 6.1; D-564's value; the engine's own field |
| cadence after the first | how often | fixed | every eligible close | the Standard path's own spacing; 7.2 |
| request timing | when in the day | fixed | after 5:00 PM CT | D-175 (assumed, section 4) |
| request amount | what may be asked | assumed | any amount from $125 to the maximum | F11; section 4 |
| payout method | fee and lag | fixed | Aeropay, $0, 3 trading days | D-24; `customer_slices.engine_args` |
| the rules of section 4 | caps, minimum, split, eligibility, floor | fixed | the ledger's values | 8284233, 8284204, 8284215 |
| arms | outcome shift | fixed | `verdict` the headline, `point` beside | CHARTER section 2; N2 |
| denial, placement | firm discretion | fixed | 0 % and the placement off in the headline; the rest beside | E-008; D-234, D-289 |
| horizons | replay length | fixed | U1's: the long replay to 252 sessions, and the exact runs | D-620 |
| blocks | which starts | fixed | all; early and late per measure (section 5) | D-621 (4)(b); F6 |
| uncertainty | the interval on each paired reading | fixed | section 9.2 | E-007 (e); F1, F8 |

### 7.2 Dropped, and why

- **The Consistency path.**
  - Family 6 closed on these tables (D-648), whose no-trade leaves also lock a Consistency account (D-654 (9)).
  - The path is chosen at activation and cannot be changed (`xfa_payout_path_choice`).
  - It needs a funded plan built for it, which is ground for families 7 and 8.
- **A buffer kept after every request (`keep_balance`).**
  - Its first-request part is what `lock` reads, through the floor mechanism.
  - Its later-request part withholds paid accounts' eligible cash: the lump direction the operator does not want
    (E-014).
  - It keeps paid accounts held for long stretches.
  - (The first version also leaned on D-566's reading of it. That reason is withdrawn pending Appendix A, N1.)
- **A fixed dollar amount per request.** The engine's request has no seam for one, so it would mean rewriting the funded
  account's payout method in an adapter -- the place where every registered row's cash is computed. `half` reads "less
  than the maximum". A fixed amount, which caps only the large payouts, is a natural later reading.
- **The cap only** (taking $2,000 once 50 % of the balance reaches it). It holds every account below a $4,000 balance:
  larger, rarer payouts, the lump direction.
- **A less frequent cadence** (every second eligibility, a monthly request, a dollar threshold). Each withholds eligible
  cash and lumps it. The Standard path's spacing is already the firm's minimum, and `half` is the one way to make
  payouts smaller without making them rarer.
- **A 4:00-5:00 PM CT request.** It rests on the operator's first-hand answer (D-177), not on a page.
- **ACH and Prop-to-Brokerage payouts.** ACH is dominated by Aeropay ($30 and a longer lag). Prop-to-Brokerage lands in
  a brokerage account and cannot pay fees without a further withdrawal (D-24).
- **The DLL election.** A contract change at checkout, and a time-limited offer (`dll_offer_status`).
- **$100K and $150K accounts.** Closed at the fit (handoff 3.1).
- **P-15's 25-point coin.** Its U1 identity is not yet reproduced (Q-22).

## 8. Before any reading: identities, oracles, mechanics

### 8.1 The identities, refusing (E-004, E-010)

Before any new cell runs, the reference policy (`elig`, `max`) runs with the whole adapter in place -- the funded-account
class, the held-state wrapper and the payout fields. It must reproduce:

1. **P-14's registered gate paths:** `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, `gate` run, 0 % denial,
   point and bound. Every `zero_edge_decomposition.PATH_COLS` column to 1e-6, all 500 paths, at P-14's seed 20261131.
2. **U1's start rows for P-14:** `vendor/stage2/results/user_journey.csv` section `start`, config `p14`, both arms,
   every start, every column as E-010 compared them (money and the ratio to 1e-6; counts, days, dates and text
   exactly), plus the study's own checks of payouts and fees against the engine's totals.
3. **The same for P-16:** `rc_s150_all_gate_paths.csv` at seed 20261206, after its trades' hash; U1's `p16` start
   rows.
4. **The levers are off in `ref`:** the held-state rule fires on no start and no path, no first request is held, and
   the recorder's `eligible` column equals the vendored engine's on every account-day. All three are counted and
   written.
5. **The trades are the base's:** every trade any cell's account takes is one of its base's registered offered trades.
   This is checked for every new cell before any reading of it.

Any failure stops the reading, and the failure protocol applies; nothing is rerun until it passes. E-010's negative
controls (the verdict rows against the point rows; a 2e-6 nudge) show that the comparison is not vacuous.

### 8.2 Oracles (an output outside them is an engine error, never a finding)

- On every cell's zero-edge twin, the mean gross payouts per funded account must not exceed $2,000 beyond its Monte
  Carlo interval (the martingale bound).
- Every request is at most min(50 % of the balance, $2,000) and at least $125, and is paid at 90 % less the method's
  fee.
- `lock` makes no first payout while the MLL is below $0.
- Under `half`, every request is half of the maximum, to 1e-9.

### 8.3 The mechanics, printed first

For each new cell and each block, these are printed before any paired outcome measure. They describe where a lever
binds, not whether it helps:

- the share of starts on which the cell differs from its base at all within 63, 126 and 252 sessions;
- the number of first requests `lock` holds, and of requests `half` cuts below $125;
- the held account-sessions, split by 6.3's three classes;
- the share of starts with an account held at sessions 63, 126 and 252.

A cell identical to its base on every start is reported as "no effect on these trades", and nothing more is read for it.

## 9. The reading: the journey scorecard and the menu (CHARTER sections 2-3; E-008, E-014, E-015, E-023)

### 9.1 What is read

**What is read.** Every cell, its base, and the rule-sensitivity runs (marked), on both arms (the verdict arm is the
headline) and on every block of section 5. The replay draws nothing.

1. **The scorecard.** P, S1 to S5c, S2, S3d, S6 and Q, as `USER_MILESTONES.md` defines them, and the frontier on P, S1,
   S3a and S5a. **S3c is comparable across the cells**, because every cell of a base shares one trade stream (E-008's
   condition).
2. **E-014's journey variables:**
   - sessions and cash to the first pass;
   - sessions and cash to the first payout;
   - **sessions to break-even** (the first session at which cumulative net cash is at or above zero, daily), the share
     reaching it by months 1, 2, 3, 6 and 12, and the share that later falls back below zero;
   - **the path's evenness:** the share of months with a positive net change, the longest run of months without a
     payout, the spread of monthly net, the deepest fall of cumulative net from its running high after break-even,
     payouts per month, and the largest single month's share of the year's payouts.
3. **Each measure as a distribution over start days** -- median, p10 and p90 -- with its uncertainty (9.2), and the
   start day's share of the variance across the four policies (S6's form): how much of a user's result is the policy,
   and how much the day they start.
4. **The paired readings, by month: who is helped, who is hurt.** For every measure in items 1 and 2, cell less base:
   - the per-start difference as a distribution (p10, p50, p90);
   - **the shares of starts on which the cell is better, equal and worse**, at months 1, 2, 3, 6, 9 and 12 (for the
     share ahead: the starts ahead under the cell and not the base, under both, under neither, and under the base and
     not the cell);
   - the mean difference, with 9.2's interval, its window count and its minimum detectable difference.
5. **Each lever alone, and their interaction:** `lock` against `ref`, `half` against `ref`, and `lock_half` against
   each lever alone.
6. **What diverges (F10).** Per cell, against its base:
   - the funded accounts activated and lost;
   - the evaluations bought;
   - the fees;
   - the payouts' count and size;
   - the trades taken and their realised risk (the share within D-212 (1)'s line, in P-14's allowance-capped form,
     E-022 (1));
   - the held sessions by class (6.3).
7. **E-007 (e)'s readings beside** (Q-17's adapter):
   - **the denial ladder** (10, 25, 50 %), drawn per payout from seed **20261945**. The cells change how many payouts
     are requested, so the ladder may rank them differently from the 0 % headline, and that ranking is printed;
   - **the placement on.** New funded accounts are then Consistency only, under the placement's own payout terms
     (13620045), and the levers apply as 6.1 defines them;
   - **the binding Focused Trader models.** A policy that strands fewer accounts recycles fewer funded accounts;
   - P by month, mean net, CVaR10, P under a bankroll limit, and the effective sample size.
8. **The long-run gate beside, every policy cell:**
   - **the run.** Each of the 8 policy cells' gate at its base's registered seed (P-14's 20261131, P-16's 20261206),
     500 paths, point and bound, with its zero-edge twin, paired with the base's registered gate paths. The two
     references' gates are 8.1's identity runs; the rule-sensitivity runs take no gate;
   - **the rows.** Growth on the required bankroll, the required bankroll, payouts a month, and days to the first payout
     (D-564 (4)'s rows);
   - **what it shows.** The trade-off between a user's first months and two-year growth, which was Stage 2's question.
     Nothing is a floor: nothing is carried.
9. **The evenness trade-off curve.** The four policies of each base give four points of "ahead" against each evenness
   measure. The step between points is printed in E-015's menu form: how much of the share ahead each step of evenness
   costs.
10. **The menu.**
    - **What it shows.** Each policy's scorecard and paired readings, all starts as the headline, the early and late
      blocks beside, and by start year.
    - **The stability flag.** A policy whose mean paired difference in P, or in any guarded measure, has opposite signs
      on the early and late blocks is flagged "not stable across blocks". The flag is mechanical, not a line.
    - **E-015's limits** are flags only, once the operator approves them: a policy crossing one is shown with which
      limit and by how much. Until then the menu is read without flags, and says so.
11. **Not modelled, and said so wherever this scorecard appears:** a user who stops when their own money runs out, the
    user's time, taxes.

### 9.2 The uncertainty on each paired reading (fixed now; F1, F8, N5)

These are descriptions, not tests. Nothing in this reading is compared with a critical value to decide anything.

1. **The window count.** For a reading at horizon h on a block, n_w is the number of non-overlapping h-start windows
   (consecutive start days in order, from the block's first start; a last incomplete window is dropped). It is printed
   with every reading.
2. **The interval.** A two-sided 90 % interval from a Student-t on the n_w window means, with n_w - 1 degrees of
   freedom, **printed only when n_w is at least 4**. When n_w is below 4, the reading prints "too few independent
   windows for an interval" and gives only item 3.
3. **The window sign count.** In how many of the n_w windows the cell's mean is above, equal to and below its base's.
   This is distribution-free and always printed.
4. **The effective sample size.** From the Bartlett long-run variance of the per-start difference, with lag window h
   (audit B's form), printed beside.
5. **The minimum detectable difference** of item 2's interval at 80 % power: (t(0.95; n_w - 1) + t(0.80; n_w - 1))
   times the window means' standard error. It is printed beside each mean, in the same table and before it.
6. **A series that is zero on every window** prints "identical on these trades", with no interval and no MDD.
7. **The interval's honesty, printed beside.** The coverage of item 2's interval is computed on synthetic series of
   known zero mean, at each n_w that the reading uses (seed **20261948**; 20,000 series per setting, fixed now):
   - **a symmetric Gaussian;**
   - **the red team's skewed, lumpy shapes** (its Appendix A model: g = 0.01; p in {0.05, 0.10, 0.20}; s in {0.0025,
     0.005, 0.01}), where the window means are +g with probability 1 - p and -g(1 - p)/p with probability p, plus
     N(0, s^2) noise, and their mirror;
   - **a persistent version:** the same, with the sign of the rare window repeated in the next window with probability
     one half.

   The reader then sees how far a 90 % interval on a lumpy payout difference can be trusted at that window count.
8. **Beside, when Q-16 is merged.** Q-16's calibrated paired comparison, one-sided at 0.05, for P and the guarded
   measures, its draws (if any) from seed **20261944**, labelled with its name and commit. The reading does not wait for
   it.

## 10. What the reading delivers, and what it does not

- **It delivers** the menu of section 9 for the operator, and the record of what payout policy does to a user's first
  year on P-14's and P-16's registered trades and table.
- **It does not deliver** a carried design, a registration id, a confirmation, or any claim at a level (E-023 (1)).
- **The operator's choice.** The operator chooses from the menu (E-015: limits first, then the best inside them). The
  choice is recorded in its own decision row, citing this reading's result files.
- **No confirmation.** Nothing is carried, so NQ from 2026-07-17 is not touched. A later look at a payout policy on
  unread data would be a new declaration, and under E-023 it could not carry.
- **The binding.** The blocks this reading reads are recorded as read for payout policy on P-14 and P-16, all of them.
  A later payout reading names this one, states what changed, and reads no block of it as fresh.

## 11. Seeds, fixed now and checked

| seed | status | what it draws |
|---|---|---|
| 20261940 | **retired, never used** | the first version's 7.3 null check (dropped) |
| 20261941 | **retired, never used** | the first version's gate floor (no floor now) |
| 20261942 | **retired, never used** | the first version's stage C statistic (no stage C) |
| 20261943 | **retired, never used** | the first version's reverse walk-forward (no pick) |
| 20261944 | in use | Q-16's paired comparison beside (9.2 item 8), if it draws |
| 20261945 | in use | the denial ladder's draws for this reading's cells (9.1 item 7) |
| 20261946 | **retired, never used** | the first version's confirmation (none now) |
| 20261947 | in use | the build's toy campaigns, and T-3's synthetic late block |
| 20261948 | in use | 9.2 item 7's synthetic coverage series, and T-6 |
| 20261949 | reserved, unused | -- |

**Retired seeds are not reassigned,** so no seed changes meaning between versions. Every result file lists them as
retired.

**The check, 2026-11-16.** A word-bounded search of the worktree (vendored snapshot and results included; `grep -rIow
--exclude-dir=.git -E "2026194[0-9]" .`) and the same search on every branch (`git grep`) find the range only in:

- this file;
- the Q-25 brief, as the proposal;
- E-018, which records it;
- the red team's review;
- master's F-B draft, which lists "20261940-49 (Q-25)" as a reservation.

None of these is a use.

**Inherited, and used only as their owners registered them:**

- P-14's seed 20261131;
- P-16's gate seed 20261206 and coin seed 20261102;
- for Appendix A, D-564's screen seeds 20261131 and 20261102.

## 12. Counting and the budget

1. **No program family number and no level** (E-023 (1)). The next numbered family's k is what it would be without this
   file.
2. **Counted under this reading's row:**
   - 11 runs: 6 new menu cells; 2 references, counted as identities; 3 rule-sensitivity runs, labelled;
   - every block read, recorded as read for payout policy (10).
3. **Nothing is selected by the program.** The operator's menu choice is a choice among described readings. It is
   recorded in its own row with the menu it was made from.

## 13. The build: adapters, identities and tests

### 13.1 The adapters (in `extended/`, never in `vendor/`)

1. **The funded account.** A subclass of the vendored `FundedAccount`, passed through the engine's seam
   `simulate_lockstep_path(funded_account_cls=...)`. In the U1 replay it goes through `customer_slices.replay`'s path
   arguments.
   - **`lock`** overrides `_standard_eligible`. It computes the firm's eligibility (the vendored method), stores it in a
     field of its own, and returns the firm's eligibility and (paid once, or floor at $0).
   - **The firm's eligibility recorded (F7).** After `trade_day` returns, the subclass sets `last_eligible` back to the
     stored firm's value. So the daily recorder's `eligible` column (`lockstep.py`, the recorder's funded row) records
     the firm's eligibility, not the policy's. The held flag is set from the firm's eligibility at the same close.
   - **`half`** is the Protocol's own `payout_frac` (`dataclasses.replace` of the base's Protocol, as D-565 did). It
     leaves eligibility untouched.
2. **The held-state rule.** A read of the table in which only the winning days of a held account are counted as 4. It
   is implemented as a wrapper on the table, or as a read of the account's count that the wrapper alone sees -- the
   build's choice, held to 8.1 and T-4. It never changes the firm's count, the eligibility, or any leaf. The minimal
   rescue (6.3) is the same wrapper with a second mode.
3. **The gate.** `gate.run_gate` takes no `funded_account_cls`. The build composes the same campaign call
   (`simulate_lockstep_campaign`, point and bound, each R's shift) in `extended/`, with no substitution of any vendored
   attribute (the lesson of E-011's first run). It is held to 8.1 items 1 and 3 at all 500 paths.

### 13.2 The rules in code

Every value of section 4 is read from the ledger by the engine's loader:

- the lock balance as `xfa_lock_at - xfa_mll_start`;
- the minimum as `payout_min`;
- the maximum from `payout_max_frac_of_balance` and `xfa_std_cap`.

A test fails on the literals 2000, 125 or 0.5 in the adapter outside comments.

### 13.3 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-1 | with both levers off, the adapter's funded account equals the vendored one bit for bit on toy campaigns (seed 20261947): every day's balance, floor, request, payout, cash and recorded `eligible` |
| T-2 | `lock`: no first payout while the floor is below $0; the first request at the first eligible close with the floor at $0, at the maximum; later requests as P-14's; an account that reached $2,000 and fell back is not held; **at a held close the recorder writes `eligible` True (the firm's) and `requested` 0** |
| T-3 | every early-block reading at horizon h is byte-identical when every session from 2024-01-02 on is replaced (seed 20261947), for h = 63, 126 and 252 -- the per-measure purge (F6) -- with the verdict arm's bound held at its registered constant (N2) |
| T-4 | the held-state rule: it fires only on accounts held at the last close, is re-read at every close, and never fires under P-14's rule; a held account's decision equals the table's four-day leaf, the state otherwise the same; the leaf read trades at every balance of at least $250 with no request the day before, funded and paid; from the policy file, it lists the bands where the four-day leaf equals the five-day leaf, where it rescues a no-trade leaf, and **the two bands where it changes R**; the minimal rescue's mode differs only in those two bands |
| T-5 | `half`: every request is half the maximum and at least $125; a balance below $500 holds; the scaling tier follows the balance after a payout |
| T-6 | 9.2: the window count, the interval only from 4 windows, the sign count, the zero-series rule; the coverage computation on one small fixed setting (seed 20261948) |
| T-7 | 8.2's oracles on toy campaigns |
| T-8 (`slow`) | 8.1 at 4 paths and at 4 starts per configuration and arm; the full 500 paths and every start are the run's first stage (heavy) |
| T-9 | section 11's seeds appear nowhere else in the build's commit; 13.2's literal check |

## 14. Outputs and the run

- **Files:**
  - `results/pp_reading.csv`, with sections `identity`, `oracle`, `mechanics`, `scorecard`, `paired`, `diverge`,
    `coverage` and `beside`;
  - `results/pp_gate.csv`, with the gate rows;
  - `results/pp_menu.csv`, the menu with its flags.

  Each is written with its sidecar manifest through `extended.results.write_result`, carrying:
  - `prereg_id`: the reading's id (unnumbered) and its pinning row;
  - the run counts (11; 6 new, 2 references, 3 rule sensitivity);
  - every seed, with the retired ones;
  - every parameter, and the assumptions of section 4;
  - the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`;
  - `exploratory=False` for the declared reading, since nothing in it is chosen after a look. Every cell is still
    labelled "described, not carried".
- **The run:**
  - **where.** Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
    its end.
  - **weight: heavy.** E-010's U1 identity for two configurations peaked near 1.4 GB. Eleven runs' replays on two arms,
    every start, and eight gates add up to several hours at two workers.
  - **order.** The identities first (8.1); any failure stops the run. Then the mechanics (8.3), then the reading.
  - **a restart.** A run aborted or restarted is recorded by the lead with its log, and only the first complete run is
    read.
- **Waits:**
  - Q-05 holds (E-010);
  - the pinning row;
  - Q-17's adapter, for 9.1 item 7.

  It does not wait for Q-16 (9.2 item 8 is beside) or for E-015's limits (flags only).

## 15. Open before the pin

**The lead's:**

1. **The pin itself.** `tests/test_declarations_fixed.py` re-hashes only files matching `prereg/F-\d+...`. An
   unnumbered reading needs either a name that the test matches or the test widened (for example to `prereg/R-*.md`).
   Otherwise its pin is not enforced. The file's name at the pin is the lead's.
2. **The gate adapter (13.1 item 3).** Built as described, or the gate beside read another way. Decided before the pin.
3. **F11, optional.** A rules-verifier reading of the payout request form's amount field (8284233). Until then, section
   4's assumption stands and is named wherever `half` is read.
4. **Appendix A.** Whether and when to run it. It is separate from this reading, and its row is its own.

**The operator's:**

1. **The levels of E-015's limits.** Approval is pending; they are flags only and never block.
2. **After the run:** the choice from the menu, if any.

## 16. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*

---

## Appendix A -- A SEPARATE ITEM, EXPLORATORY: checking Stage 2 D-566's buffer reading (the red team's N1)

**Not part of reading PP.** It reads no policy for users, adds nothing to the menu, and is run, if the lead decides, in
its own clean checkout under its own decision row, labelled EXPLORATORY. **Light:** 20 paths, minutes, well under 1 GB.
**It reads no growth, no journey and no P** -- only counts of an engine state.

**The doubt, on code and table (the review's N1 confirmed it on both).**

- The request is `payout_frac x min(0.5 B, cap)`, then capped at `max(B - keep_balance, 0)`, and nothing is asked below
  $125 (`lockstep.FundedAccount.trade_day`). So under a buffer K, a paid account with B in [$500, K + $125) is eligible
  and asks nothing.
- Its five-day leaf at a positive line gap is no-trade in every balance band from $500 (D-654 (3)), and its state cannot
  move, so it sits until the funded horizon, holding its seat.
- Unpaid funded accounts can meet the funded phase's lowest-cushion five-day no-trade leaves (D-654 (9)).
- D-566 (2) read the $2,000 buffer's cost as "takes fewer trades a session (more balance held means fewer accounts
  recycled)". Part of that may be this sit. Stage 2 recorded the same artefact for Consistency accounts and wrote
  "which did more is not measured" (D-654 (9)).
- Half requests with no buffer (D-566 (3)) cannot meet the leaf: they ask from $500, and the five-day leaves below $500
  trade.

**What it runs.**

- **The engine and the cell.** The vendored D-564 runner's own cell and engine arguments
  (`scripts/rc150_payout_screen.py`: `protocol_for`, through `rc_screen.Runner`), with D-146's daily recorder on.
  `gate.run_gate` has no recorder switch, so the check composes the per-path call
  (`simulate_lockstep_path(..., record_days=True)`) from those same arguments, held to identities (b) and (c) below.
- **The six cells.** D-564's grid: `keep_balance` in {$0, $1,000, $2,000} x `payout_frac` in {1.0, 0.5}. (0, 1.0) and
  (0, 0.5) are the controls; the four buffered cells are the ones in doubt.
- **The paths and seeds.** 20 paths per cell, at D-564's seeds (campaign 20261131, coin 20261102), so the paths are the
  first 20 of D-564's own.

**The identities first, refusing.** If any of these fails, nothing more runs.

- **(a) The trades.** The cell's trades are P-16's: their count and content hash against `rc150_dev_test.TRADES_SHA256`,
  as the vendored runner checks them.
- **(b) The call.** For each of the six cells, the composed call with the recorder off reproduces the vendored runner's
  own gate call for that cell at 20 paths, every `zero_edge_decomposition.PATH_COLS` column, point and bound, to 1e-6.
- **(c) The recorder.** With the recorder on, the same 20 paths are unchanged, column for column.

The check reads no growth row. So it does not repeat D-565's 500-path reproduction of `rc_width_screen.csv`'s
`rc_s150_all`, which licensed D-564's reference.

**What it counts** (fixed now). A **sit-day** is a funded account-day with all three of these:

- the session's decision is a no-trade leaf (`max_trades` 0, named in the recorder's `regime`);
- the account's last close recorded `eligible` True;
- that close recorded `requested` 0.

Per cell it reports:

- the sit-days, and their share of the cell's funded account-days;
- the accounts that ever sit;
- the sit-days by phase (funded, paid).

**The control.** Both controls must show **zero** sit-days, since under those policies an eligible, unpaid account has
a balance below $250, where the five-day leaves trade. A nonzero control means the count is wrong: the failure protocol
applies, and nothing is read.

**What follows, fixed now.**

- **If every buffered cell's sit-days are below 1 % of its funded account-days**, D-566's buffer readings stand as
  written, and the check's row says so.
- **If any buffered cell's sit-days are at or above 1 %**, the lead may propose a heavy follow-up under its own row:
  - **the run.** Those cells at 500 paths, under this reading's held-state rule, read beside D-566's rows -- under the
    lock, about an hour;
  - **the 7.2 drop.** `keep_balance` stays dropped here for its other two reasons whatever the follow-up shows;
  - **a new buffer reading.** If one is ever wanted, it is a new declaration.

**Output.** `results/n1_buffer_sit.csv` with its manifest, `exploratory=True`, from a clean checkout of a named commit.
