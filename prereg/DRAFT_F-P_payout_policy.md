# DRAFT F-XX: payout policy in a user's first months (family PP) -- not declared

**Status: DRAFT of 2026-11-15 (TASK_QUEUE Q-25), for the red team. Not pinned, not numbered, not declared.** No engine
has been run for it, no cell built, no outcome of any payout policy computed or read here. It becomes a declaration only
after the red team's review, the prereg-gatekeeper's approval (which assigns F-XX and k) and the lead's pinning row with
its sha256. **It cannot be pinned before two things:**

1. **the operator's choice of its pass line** (section 9). E-008's pass line -- a design's lift over the coin twin on
   its trades -- cannot judge a lever that adds no trade, so this family needs a pass line of its own. That is an
   objective question, so it is the operator's. Three forms are proposed; none is adopted here.
2. **Q-16's merge.** Every calibrated statement below uses Q-16's paired P statistic. The marks **[Q-16]** are filled
   in a revised draft, with the statistic's name, module and commit, before the gatekeeper reads it.

Anything chosen after a reading is exploratory and reported apart.

| field | value |
|---|---|
| family | PP: how much a funded account withdraws, and when, in a user's first months -- on P-14's registered trades, P-16's beside |
| id | F-XX -- the gatekeeper's |
| program family number k | the next free at the pin (F-01 spent 10, E-007 (a); F-02's and F-B's drafts are ahead of this one in the queue) |
| level | one-sided **0.05 / (k (k + 1))**: 0.05 / 132 at k = 11, 0.05 / 156 at k = 12, 0.05 / 182 at k = 13 |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16, read only through P-14's and P-16's registered trades (no bar is read by this family) |
| the unit | one start day, replayed as U1 replays it (`vendor/stage2/docs/USER_MILESTONES.md`); cell and reference paired on the same start |
| choice block | starts from 2020-01-02 whose 63rd session is on or before 2023-12-29 (section 4) |
| judged block | starts from 2024-01-02, each reading on the starts with its horizon left inside 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`reserve`, reserved; a purchase; section 13) |
| cells | 2 first-request rules x 2 amounts x 2 trade streams = **8 run**: 6 new, plus 2 references that must reproduce registered rows (section 5) |
| judged | one cell: the choice block's pick on P-14's trades |
| the pass line | **the operator's decision** (section 9): PL-1 paired P, PL-2 evenness first, or PL-3 described only |
| seeds | 20261940 to 20261949, each assigned in section 14 |
| model card | none: no fitted model, no searched value outside the grid |

---

## 0. What this family is, and where the brief's six items are answered

A payout policy changes no trade. Every cell runs P-14's registered trades through the vendored engine, under P-14's
table, seats and purchase budget, and changes only the funded account's payout requests. The same holds beside on
P-16's trades. So every cell is compared with its own base **on the same start days and the same offered trades**. That
paired comparison is far more powerful than comparing designs on different trades (red team M2,
`docs/reviews/phase0_red_team_2026-11-15.md`).

| the brief's item | where |
|---|---|
| 1. the levers, each fixed / searched / dropped, within the verified rules; Standard only unless argued; a small grid | 3, 5, 6 |
| 2. same trades, so a paired comparison; a pass line for a same-trades lever proposed and marked the operator's | 5.4, 9 |
| 3. the journey scorecard as the reading; the long-run gate beside; the denial ladder beside | 10, 11 |
| 4. prior exposure: what Stage 2 read about payout policy, on which data; why this is a different question | 2 |
| 5. identity first: with the registered policy the cell reproduces P-14's registered paths and U1 start rows | 7.1, 16 |
| 6. seeds in 20261940-20261949, searched unique; k the next free | 14, 15 |

## 1. Hypothesis

**The contract's arithmetic (every value verified, section 3).**

- A $50K funded account (XFA) starts at a balance of $0 with its loss limit (MLL) at -$2,000, trailing upward. The MLL
  locks at $0 once the balance reaches $2,000 (8284204).
- At the first payout the MLL is set to $0, wherever it was; the remaining balance becomes the loss floor
  (8284204, 8284233).
- A request takes at most 50 % of the balance and at most $2,000 on the Standard path, with a $125 minimum; the user
  keeps 90 % (8284233).
- A request needs five winning days of at least $150 since the last payout, and a profit since the last payout (the
  first payout is exempt). The request day does not count toward the next five (8284233).
- A payout that lowers the balance lowers the scaling tier (`scaling_tier_after_payout`, 8284233; Stage 2 D-53).

**The mechanism.** A first payout taken while the MLL is still below $0 moves the floor up to $0 at once. The account
loses the cushion between its old floor and zero, as well as the cash withdrawn. So an early payout strands a small
balance (propsim D-45). Once the MLL has locked at $0, that cost is gone: the request takes cash and nothing more.

Two levers act on this within the verified rules:

- **When** -- `lock`: hold the first request until the MLL has locked.
- **How much** -- `half`: take half of the maximum each time, so more of every balance stays in the account.

Both keep accounts alive longer, and so give more chances at later payouts and at months with a payout. Both cost cash
now. That includes the first payout, which within P-14's own trades is what a user's first month moves with most
(handoff 1.2, `results/user_drivers.csv` section `within_design`).

**The question.** For a user who starts on any day, does either lever, or both, raise the share of starts ahead over
months 1 to 3 (P)? And what does each do to the path's evenness (E-014)? An evenly distributed path is the operator's
stated goal: "not just one lump sum in one month that puts users ahead".

**What answers it.** The paired reading on the same start days (sections 9 and 11). It is not a forecast: a user's first
quarter is mostly the day they start (`results/user_drivers.csv`, section `design_vs_luck`), so every reading is a
distribution over start days.

**Whose accounts and how.** One user's own five Topstep seats, each with its own trades, one position at a time across
the firm (Stage 2 D-157, D-429; E-012 (3)). Every trade and every payout request is made by hand (E-008). A payout
request is not trading conduct. No tier-1 rule is touched (section 3).

## 2. Prior exposure: what has already read payout policy, on which data

A judged reading is worth only what the block's freshness allows.

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| stage one, propsim D-44/D-45 (`vendor/stage2/vendor/propsim/edge/T5_RESULTS.md` section 3; `payout_buffer_exploratory.py`) | a buffer (balance kept before a request) against taking the maximum, on stage one's binary process | synthetic draws, no NQ | holding a balance beat taking the maximum, before lag, reinvestment and costs were priced; exploratory, chosen after the declared results | the mechanism's source; a hint, not a setting (contract-engine skill) |
| Stage 2 T7's protocol grid (`propedge/campaign/protocols.py`, `t7_grid.py`) | the buffer family and fast-payout arms, registered as arms | -- | no row in the vendored log records the comparison read (searched `vendor/stage2/DECISIONS.md` for "T7" and "buffer", 2026-11-15) | none read |
| Stage 2 D-564 to D-566 (`results/rc150_payout_screen.csv`, not vendored) | on **P-16's cell**: `keep_balance` $0 / $1,000 / $2,000 x `payout_frac` 1.0 / 0.5 (six cells), and a 4-5 PM request beside | 500 gate paths at seed 20261131 and D-518's start-day journey on the verdict arm, over the whole development window (both of this family's blocks) | taking the maximum at the first eligible close grew most; the $1,000 buffer was about level; the $2,000 buffer and every half request cost growth and raised the bankroll; days to the first payout unchanged; nothing a candidate (D-566) | **P-16's `half` cell beside is close to D-564's half request with no buffer**: its direction on growth is known, and its journey was computed and read by the program, though this repository cannot see the file. P-14 never ran a payout cell. No hold on the first request alone, and no hold tied to the MLL's lock, was ever run |
| Stage 2 program U, family 6 (D-646, D-648; `results/u_consistency.csv`) | the Consistency path chosen at activation, on P-14's and P-16's trades and tables | start days, choice and judged blocks | closed: on these tables the path pays almost no one | the reason this family is Standard only (6.2) |
| Stage 2 program U, families 7 and 8 (D-653 to D-655, D-658, D-661; `u_plan.csv`, `u_limit.csv`) | flat funded plans, the paid phase changed on the Consistency cells | start days, both blocks | closed (family 7: paid sooner but less than the fees; family 8: the size trend runs out; handoff 3.1) | the funded leg is the table's here, never flattened |
| U1 (D-620; `results/user_journey.csv`) and this repository's Q-05 identity (E-010) | P-14's and P-16's own journeys, every start | all starts | the reference rows this family pairs against | the references are known in full; only the cells are new |
| program U's nine families | P on the judged block against P-14 | starts from 2024 | all closed | the judged block has been read for P nine times; it is late development, not out of sample |

**The drafter's own reads (disclosed).**

- The vendored no-closure table's leaves (`results/state_policy_v12_noclose_policies.json`, the policy
  `state_dp_e-0.050_lamstar_noclose` that P-14 and P-16 both use, D-501). It is a registered configuration, not an
  outcome. It was read to see what a held account would trade (5.3).
- The engine's payout code (`propedge/campaign/lockstep.py`, `FundedAccount`), the U1 runner
  (`scripts/user_journey.py`, `scripts/customer_slices.py`) and the gate (`propedge/campaign/gate.py`).
- No result file of any payout cell was opened.

**What is already known of the direction (disclosed, so a reading in its favour is not mistaken for a surprise).**
Within P-14, a start's month-1 net moves most with whether and how soon a first payout came (handoff 1.2), so a lever
that delays or shrinks the first payout is expected to cost month 1. On P-16's trades, half requests cost long-run growth
(D-566 (3)).

**Why this is a different question from Stage 2's.** There are five differences.

1. **The objective.** Stage 2 ranked payout policy by growth on the required bankroll over a two-year path (the D-145
   gate). This family reads a user's first three months (P) and E-014's journey, where the timing of the first cash is
   what matters.
2. **The lever.** Stage 2's buffer (`keep_balance`) holds every request, the paid ones included, and binds wherever
   the balance is below twice the buffer. This family's `lock` holds the **first** request only, and only until the MLL
   has locked at $0. That is the floor-reset mechanism of propsim D-45 itself, isolated, and no read has run it.
3. **The base.** P-14 (R\*), on which no payout cell was ever run. P-16 is beside.
4. **The unit.** Paired start days, not bootstrap paths.
5. **The held states.** A buffer leaves eligible accounts unpaid. Unpaid, they reach states the table never visited,
   and in many of those it trades nothing (5.3). Stage 2's buffer cells ran on that table with no rule for those states;
   whether, and how often, an account sat there is not recorded. This family declares what a held account trades (the
   held-state rule).

## 3. Contract fit, and the verified rules every cell leans on

**The payout rules** -- every one from Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`, as E-002 vendored
it), loaded through the engine's own rule loader, never typed into code (16.2):

| ledger key | value | article | read | used for |
|---|---|---|---|---|
| `payout_max_frac_of_balance` | 0.5 | 8284233 | 2026-11-14 | the maximum request |
| `xfa_std_cap` | $2,000 (no DLL election) | 8284233 | 2026-11-14 | the maximum request |
| `payout_min` | $125 | 8284233 | 2026-11-14 | a request below it is not made |
| `profit_split` | 0.9 | 8284233 | 2026-11-14 | cash to the user |
| `xfa_std_winning_days`, `xfa_std_winning_day_min` | 5 days of at least $150; the request day excluded | 8284233 | 2026-11-14 | eligibility |
| `require_profit_since_payout` | true (the first payout exempt) | 8284233 | 2026-11-14 | eligibility after the first |
| `xfa_mll_start`, `xfa_lock_at` | -$2,000 trailing; locks at $0 once the balance reaches $2,000; $0 after the first payout | 8284204, 8284233 | 2026-11-14 | the floor; `lock`'s condition |
| `payout_fee`, `payout_lag_days_aeropay` | $0, 3 trading days (derived, D-24) | 8284233 | 2026-11-14 | the method (Aeropay, US baseline) |
| `payout_after_request_survives_mll_breach` | true | 8284233 | 2026-10-30 | a request then a breach is still paid |
| `scaling_tier_after_payout` | resets with the balance | 8284233 | 2026-10-03 | a payout lowers the tier (D-53) |
| `max_active_funded_accounts` | 5 | 8284215 | as vendored | the seats |
| `xfa_payout_path_choice` | chosen at activation, cannot be changed | 8284215 | 2026-11-14 | why a cell cannot switch path (6.2) |

**Assumed, as in every registered row, because no page states it** (Stage 2 D-175,
`propedge/contract/payout_timing.py`):

- the request is made after 5:00 PM CT, so the next session is the request day;
- the balance and the floor move at the request, before the request day trades.

**Not modelled, as in every registered row:** that payouts are unavailable in holiday hours (13350348), and the move to
a Live Funded Account. Neither is a verified trigger the ledger loads.

**The rest of the contract fit is P-14's, unchanged.** The trades are P-14's registered trades, so these are inherited
and checked, not re-derived (7.1, 10):

- latency of at least five minutes (D-266);
- one position at a time with five minutes flat (D-429);
- resolution and realised risk (D-212 (1), (2) as D-308 (3) raised it);
- the stop band and cost floor;
- the report-day and FOMC rules (E-007 (d)).

**Conduct.**

- Tier 1: untouched. A payout request is not a trade, no account copies another, and nothing is concealed.
- Tier 2: the Responsible Trading Program is off in the base case (D-289) and on beside.
- Tier 3, priced: the payout-denial ladder of 10, 25 and 50 % is beside the 0 % verdict (D-234, E-008, E-013). It
  carries Terms of Use s.8 (E-013 (1)).
- A payout policy changes how many payouts a user requests, and so how often the firm's discretionary review is met.
  That is why the ladder is read per cell (11 item 5).

## 4. Data, blocks and the unit

1. **The unit** is U1's: one development start day, fresh bankroll and accounts, the design's trades replayed in
   historical order; the long replay of up to 252 sessions and the exact runs (`scripts/user_journey.py`,
   `customer_slices.replay`), read on the `verdict` arm (every R at its bound) with `point` beside. Definitions are
   `vendor/stage2/docs/USER_MILESTONES.md`'s, unchanged. A month is 21 sessions.
2. **Pairing.** Cell and reference are run on the same start days, the same blocks (the same offered trades, the same
   outcome of each offered trade), the same seeds; the per-start difference is the unit of every paired statistic.
3. **The choice block:** starts from 2020-01-02 **whose 63rd session falls on or before 2023-12-29**.
   - This purges the last 63 starts of 2023. P reads months 1 to 3, so without the purge those starts would read
     sessions inside the judged block (feature-rules: purge and embargo).
   - The charter's words, "chosen on the starts of 2020-2023", are kept: the choice block is a subset of those starts.
     Program U's families did not purge. This is an interpretation, recorded for the red team.
4. **The judged block:** starts from 2024-01-02 (the first session of 2024). Each reading uses the starts with its
   horizon left inside 2026-07-16, as U1 does: months 1 to 3 for P; 126 and 252 sessions for S4a and S4b.
5. **What it can hold.** The judged block holds about nine non-overlapping 63-start windows (`docs/audits/phase0/
   B_objective.md`, Q3). A paired difference on the same trades has a far smaller spread than one between designs, but
   its dependence across neighbouring starts is no shorter. Section 7.3 states what the test can reach before anything
   is read.
6. **No NQ from 2026-07-17** is on disk or read (section 13).

## 5. The cells

### 5.1 The two levers

| lever | values | what the user does |
|---|---|---|
| **L1, the first request** | `elig` (P-14's) / `lock` | `elig`: request at the first close at which the account is eligible and the request reaches $125. `lock`: request the first payout only at an eligible close at which the account's MLL has locked at $0 (its balance has reached $2,000 at some close, 8284204); until then the account keeps trading and asks nothing |
| **L2, the amount** | `max` (P-14's) / `half` | `max`: the most allowed, min(50 % of the balance, $2,000). `half`: half of that (the engine's `payout_frac` 0.5); not made if below $125 |

Every other request is made at **every eligible close** (P-14's cadence, FIXED: 6.1). L1 acts on the first request
only. Once a payout is made the MLL is $0 and the floor argument is spent. L2 acts on every request.

**Why `lock` is defined by the MLL's lock and not by a balance now.** An account can reach $2,000 and fall back. Its
MLL then stays at $0, and its first payout strands no cushion. The condition is the mechanism's own, read from the
account's floor.

### 5.2 The grid

| cell | L1 | L2 | on P-14's trades | on P-16's trades (beside) |
|---|---|---|---|---|
| `ref` | `elig` | `max` | P-14 as registered: the identity (7.1), not a variant | P-16 as registered: the identity |
| `lock` | `lock` | `max` | new | new |
| `half` | `elig` | `half` | new | new |
| `lock_half` | `lock` | `half` | new | new |

The two binary levers are fully crossed, so neither lever's reading depends on the other being held at P-14's value.
Their interaction is read, not assumed away.

**Order for ties** (section 8): `lock`, `half`, `lock_half` -- the fewest changes from P-14 first, then the order
written.

### 5.3 The held-state rule (FIXED)

**The hazard.** P-14's table (`state_dp_e-0.050_lamstar_noclose`, D-501) was solved with every request at the maximum
at the first eligible close. So at a session's start no account of P-14's is ever eligible and unpaid with a request of
at least $125. The table's leaves for those states are "the table's own decision where its chain never visited"
(its v11 export note, in the policy's description). Many of them trade nothing.

- D-654 (3) recorded it for the paid phase: "no-trade leaves at five winning days with profit since the last payout
  (every balance band from $500 up)".
- D-654 (9) recorded it for the funded phase: "no-trade leaves at five winning days (a quarter of those states, at the
  lowest cushion bands)".
- The drafter's read of the vendored file agrees, and the build re-derives it from the file (16.3, T-4).

**What goes wrong without a rule.** An account a policy leaves unpaid meets those leaves. It never trades again, its
balance never moves, and the no-closure table never frees its seat. The funded and paid phases of the table key only on
balance, cushion, winning days, line gap and the request-day flag, and none of them moves while an account sits. That
is an artefact of a table solved for another policy, not a payout policy.

**The rule.** An account is **held** when, at a close, both of these hold:

- it is eligible by the firm's Standard rule, and P-14's request, min(50 % of the balance, $2,000), would reach $125;
- the cell's policy makes no request, or a request below $125 (L1's hold; L2 on a balance below $500).

At the next session's start, a held account's table decision is read **with its winning days counted as 4**: the
table's own leaf, at the same balance, cushion, line gap and request-day flag, for an account one winning day short of
eligibility. That is the table's solved decision for an account still collecting toward its payout.

- **Re-read at every close.** "Held" is re-read at every close. An account that is no longer eligible -- its profit
  since the last payout gone, or its balance below $250 -- is not held. It is then in a state P-14's accounts also
  reach, and the table is read as it stands.
- **It always trades.** In the vendored file, the leaf read at four winning days trades in every state a held account
  can be in: a balance of at least $250, no request the day before, funded or paid (T-4 re-derives this from the file).
- **Nothing else changes.** The firm's count of winning days, and eligibility, are never changed: only the table's read
  is.

**Its reach.**

- In `ref` the rule never fires: P-14's rule leaves no account held. That is checked on every start and path (7.1).
- The share of funded account-sessions read under it is reported per cell (7.4, 11).
- **Dropped:** re-solving the table for each policy. That would be a new sizing design and a search, and D-564 kept
  the table as solved too.

### 5.4 What "the same trades" means here, exactly

The offered trade stream is identical in every cell of a base. It has the same registered entries, the same per-trade
outcomes on each arm, the same days in the same order, and the same purchase and seat rules.

**What can differ is which offered trade each account takes, and at what size.**

- The state table sizes each trade by the account's balance, cushion, winning days and line gap.
- A payout changes the balance, and the router offers each trade to an account that can take it.
- A held account keeps a seat that P-14's account would have freed by breach, so fewer evaluations may be bought, and
  the fees move too.

These are the policy's effects, not noise. So the pairing is on **start days with identical offers**, not on identical
executed trades. A check confirms every trade a cell takes is one of its base's registered offered trades (7.1, item
5).

## 6. Parameters: fixed, searched, dropped

### 6.1 The table

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| trades | what is traded | fixed | P-14's registered trades (A3-BRK30-CB20), by U1's own builder | E-010; D-513 |
| trades, beside | the second stream | fixed | P-16's registered trades (`rc_s150_all_nr`), `rc150_dev_test.TRADES_SHA256` | E-002; D-544 |
| state table | sizing by account state | fixed | `state_dp_e-0.050_lamstar_noclose`, checked against `a3_brk30_cb20.NOCLOSE_POLICIES_SHA256`; not re-solved | D-501; D-564 (2) |
| held-state rule | what a held account trades | fixed | the table read at four winning days (5.3) | the table's own collecting leaf; no fitted value |
| seats, budget, routing | accounts and purchases | fixed | each base's own (five seats; 20 evaluation purchases in 21 sessions; the strict one-position rule) | P-14's and P-16's registrations |
| payout path | Standard or Consistency | fixed | Standard | 6.2 |
| **L1, first request** | when the first payout is asked | **searched** | `elig`, `lock` | 5.1; `lock` from 8284204's lock balance |
| **L2, amount** | how much each request takes | **searched** | `max`, `half` (`payout_frac` 1.0, 0.5) | 5.1; 0.5 is D-564's value and the engine's own field |
| cadence after the first | how often | fixed | every eligible close | the Standard path's own spacing; 6.2 |
| request timing | when in the day | fixed | after 5:00 PM CT | D-175 (conservative, page-derived) |
| payout method | fee and lag | fixed | Aeropay, $0, 3 trading days | D-24; `customer_slices.engine_args` |
| the rules of section 3 | caps, minimum, split, eligibility, floor | fixed | the ledger's values | 8284233, 8284204, 8284215 |
| arms | outcome shift | fixed | `verdict` judged, `point` beside; each R at the bound P-14 (P-16) registered | CHARTER section 2 |
| denial, placement | firm discretion | fixed | 0 %, placement off in the verdict; the rest beside | E-008; D-234, D-289 |
| horizons | replay length | fixed | U1's: the long replay to 252 sessions and the exact runs | D-620 |
| blocks | choice and judged | fixed | section 4 | CHARTER section 3; 4.3's purge |
| choice rule | which cell is judged | fixed | section 8 | -- |
| pass line | what carries | **the operator's** | PL-1, PL-2 or PL-3 (section 9) | an objective question |
| statistic | the paired test | fixed at the pin | Q-16's calibrated paired P statistic **[Q-16]**, checked on this family's null (7.3) | E-007 (1); E-008 |
| gate floor | E-008's long-run floor | fixed | growth on the required bankroll at the bound above zero, at seed 20261941, 500 paths | E-008; Stage 2 D-145 |

### 6.2 Dropped, and why

- **The Consistency path.**
  - Family 6 closed on these very tables: the bold opening breaks the 40 % rule (handoff 3.1 #6; D-648).
  - The tables' no-trade leaves at five winning days lock a Consistency account that fails the best-day test
    (D-654 (9)).
  - The path is chosen at activation and cannot be changed (`xfa_payout_path_choice`), so no payout policy can move
    an account onto it later.
  - A Consistency payout family needs a funded plan built for the path. That is families 7 and 8's ground, not a
    payout policy.
- **A buffer kept after every request (`keep_balance`).**
  - Stage 2 read it on P-16 (D-566).
  - Its first-request part is what `lock` tests through the floor mechanism directly.
  - Its later-request part withholds paid accounts' eligible cash: the lump direction the operator does not want
    (E-014). It also meets the held-state rule on paid accounts for long stretches.
- **A fixed dollar amount per request.**
  - The engine's request has no seam for one. `payout_frac` scales the maximum and `keep_balance` keeps a balance, so
    a fixed amount would mean rewriting the funded account's payout method in an adapter. That is the one place
    where every registered row's cash is computed: an identity risk for the whole family.
  - `half` already asks whether less than the maximum helps.
  - A fixed amount, which caps only the large payouts, is the natural next family if `half` moves evenness.
- **The cap ($2,000 taken only once 50 % of the balance reaches it).** This is a hold on every account below a $4,000
  balance. It makes larger, rarer payouts -- the lump direction -- and binds well beyond `lock` on accounts whose MLL
  has already locked.
- **A less frequent cadence** (every second eligibility; at most one request in 21 sessions; a request only above a
  dollar threshold). Each withholds eligible cash and accumulates a larger, rarer payout (E-014's lump), and each keeps
  accounts held for long stretches. The Standard path's own spacing -- the request day plus five new winning days --
  is already the firm's minimum. `half` is the one way within the rules to make payouts smaller without making them
  rarer.
- **A 4:00-5:00 PM CT request.** It rests on the operator's first-hand answer, not a page (D-177), and the brief allows
  verified rules only.
- **Other payout methods.**
  - ACH ($30 and about 6 days) is dominated by Aeropay for a US user.
  - Prop-to-Brokerage lands in a brokerage account and cannot pay fees without a further withdrawal of unstated
    duration (D-24).
- **The DLL election** (both caps doubled; `dll_offer_status`). It is a contract change made at Combine checkout -- a
  daily loss limit on the account -- and a time-limited offer with no published end date. It belongs to a
  contract-shape family.
- **$100K and $150K accounts.** Closed at the fit (handoff 3.1).
- **P-15's 25-point coin.** Its U1 identity is not yet reproduced (Q-22).

## 7. Stage A: identities and gates, before any outcome

### 7.1 The identities, refusing (the brief's item 5; E-004, E-010)

Before any new cell runs, with the reference policy (`elig`, `max`) and the family's whole adapter in place -- its
funded-account class, the held-state wrapper on the table, the payout fields:

1. **P-14's registered gate paths.** The adapter's gate call reproduces `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`,
   `gate` run, 0 % denial, point and bound. The comparison is every `zero_edge_decomposition.PATH_COLS` column to
   1e-6, on all 500 paths, at P-14's seed 20261131.
2. **U1's start rows for P-14.** The adapter's replay reproduces `vendor/stage2/results/user_journey.csv` section
   `start`, config `p14`, both arms, every start. Every column is compared as E-010 compared them: money and the
   ratio to 1e-6; counts, days, dates and text exactly; the study's own checks of payouts and fees against the engine's
   totals.
3. **The same for P-16:** `rc_s150_all_gate_paths.csv` at seed 20261206, after its trades' hash; U1's `p16` start
   rows.
4. **The levers are off in `ref`.** The held-state rule fires on no start and no path, and no first request is held.
   Counted and written.
5. **The trades are the base's.** In every cell, every trade an account takes is one of its base's registered offered
   trades (5.4). Checked for the new cells when they run, before any reading of them.

Any identity failing stops the family. The failure protocol applies; nothing is rerun until it passes. A negative
control, as E-010's: the verdict rows against the point rows, and a 2e-6 nudge, show the comparison is not vacuous.

### 7.2 Oracles (an output outside them is an engine error, never a finding)

- **Zero edge.** On every cell's zero-edge twin (the gate's), the mean gross payouts per funded account must not exceed
  $2,000 beyond its Monte Carlo interval (the martingale bound; contract-engine skill).
- **Every request.** Every request is at most min(50 % of the balance, $2,000), at least $125, and paid at 90 % less
  the method's fee.
- **`lock`.** No first payout is made while the account's MLL is below $0.
- **`half`.** Every request equals half of the maximum to 1e-9.

### 7.3 The test can reach its level (a kill line before any judged read)

Q-16 calibrated its paired P statistic on nulls built from P-14 against P-16, that is, on different trades. A
same-trades difference series is different: mostly zero, with clusters where one account's payout differed. So:

1. **This family's own null.** For each new P-14 cell, the per-start paired difference on the choice block is
   sign-flipped by non-overlapping 63-start blocks. That keeps the dependence and makes the mean zero.
   - Q-16's statistic is applied at the family's level, with enough replications that the Monte Carlo interval tells
     the level from twice the level. The count is written in the planning section.
   - Draws: `numpy.random.default_rng([20261940, j])`, with j the cell's index in 5.2.
   - The rejection rate must not exceed the level beyond its interval. If any cell's null fails, the statistic is not
     used, and the family **stops before the judged read**. It is recorded as "not judgeable at this level by a
     calibrated statistic on this data".
2. **Reachability.** If Q-16's statistic is a randomization test, its smallest attainable p-value on the judged
   block's block count must be below the level. If it is not, the family stops the same way.
3. **The minimum detectable difference.** At 80 % power at the family's level, on the judged block, for each new P-14
   cell and for the measure the operator's pass line names. It is computed from the choice block's paired series by
   Q-16's power method **[Q-16]** and written before stage B.

### 7.4 Planning readings (on the choice block's runs, before the choice; describing where each lever binds, not whether it helps)

For each new cell, on both bases:

- the share of starts on which the cell differs from its reference at all within 63 sessions;
- the number of first requests `lock` holds, and of requests `half` cuts below $125;
- the share of funded account-sessions read under the held-state rule;
- the share of starts on which an account is held at session 63.

**A cell identical to its reference on every choice-block start is void:** counted, never chosen. These are the
mechanics of the lever. They read no paired outcome measure.

## 8. Stage B: choose on the choice block

1. **What is chosen:** the one cell to be judged, among `lock`, `half` and `lock_half` on P-14's trades.
2. **The rule:** the largest studentised paired difference on the pass line's primary measure (P under PL-1; the
   evenness measure under PL-2), by Q-16's statistic **[Q-16]**.
   - Ties go by 5.2's order.
   - If no cell's point difference is above zero, the family **closes at stage B**: on the choice block no payout
     policy beat P-14's, and nothing is judged.
   - Under PL-3 nothing is chosen; every cell is described (9.2, PL-3).
3. **What it spends:** nothing of the program's level. One cell reaches judgement.
4. **Its record:** written to the result file's `choice` section, with every cell's choice-block readings, before the
   judged block is read.
5. **The proof it ignores the judged block (T-3, 16.3).** The pick and every planning output are byte-identical when
   every session from 2024-01-02 on is replaced by a seeded synthetic one (seed 20261947). The 4.3 purge is what makes
   that hold.

## 9. Stage C: the pass line -- the operator's decision

### 9.1 Why E-008's line does not apply, and why a pass line on P becomes possible

E-008 judges a design by its trades' lift over the coin twin. Every cell of this family has exactly P-14's trades, and
so exactly P-14's lift.

- A line on the lift would carry every cell or none, whatever the policy does to a user.
- The value-map price is a property of the trades too.

What a payout policy changes is the user's journey on those trades. That is what has to be judged.

E-008 moved the pass line off P because, between designs on different trades, the judged block's few independent starts
leave a calibrated P test unable to carry anything (E-007 (2); red team M2). M2's own remedy names the way out: "a
same-base design". On the same trades and the same start days, the start's luck is shared by cell and reference and
largely cancels in the difference. A paired P test can then carry an effect that a between-design test could not see.

### 9.2 The three forms proposed (none adopted; the operator chooses one before the pin)

**PL-1, paired P (the drafter's proposal).** The pick carries only if all of these hold on the judged block:

- **(a) The line.** The paired P difference against P-14 on identical trades has its one-sided lower bound above zero at
  0.05 / (k (k + 1)), by Q-16's calibrated paired statistic **[Q-16]**, with 7.3's null check passed.
- **(b) Nothing bought back later.**
  - On no guarded measure (S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c) is the pick worse than P-14, at the point
    estimate, by more than D-621 (3)(ii)'s tolerances on record: five points on a share, ten per cent on dollars,
    sessions and ratios.
  - A payout lever moves cash in time. A share ahead early, bought by losing months 6 and 12, the unlucky tenth or
    the bankroll, is not a gain for the user.
  - S5a sits near zero. If the operator prefers its tolerance in dollars (red team B-5), that is a sub-choice;
    the default is the tolerance as on record, which is the stricter.
- **(c) The same direction on P-16's trades.** The same policy against P-16, paired on the judged block, has a point
  difference in P of at least zero. A policy that helps on one registered trade stream and hurts on the other is
  fitting that stream.
- **(d) E-008's floors** (section 10).

**PL-2, evenness first.** For the case where the operator's E-014 statement ranks an even path above the share ahead.
The pick carries only if all of these hold on the judged block:

- **(a') The line.** Take each start's share of its first six months with a positive net change (E-014's first
  evenness measure; per start, its months 1 to 6 as 21-session blocks). The paired difference of that share against
  P-14 has its one-sided lower bound above zero at the family's level, by Q-16's statistic **[Q-16]**, with 7.3's check
  on this measure.
- **(b') P not worse.** The paired P difference's calibrated one-sided 95 % lower bound is above -0.05, D-621
  (3)(ii)'s five points.
- **(c), (d)** as in PL-1.

Under PL-2 the family's level is not divided: (a') and (b') form an intersection, so the pick must hold both.

**PL-3, described only.**

- No line: no cell can carry.
- Every cell's scorecard, its paired differences, the trade-off curve and the menu are reported (section 11).
- The family closes with its readings as the record of what payout policy does to a user's first months on P-14's
  trades.
- **This is the safe default if the lead must proceed before the operator answers,** because it changes no objective.
  Under PL-3, stage B's choice and stage C's test are not run. Section 7.3's MDD is still reported, so the record says
  what could have been detected.

### 9.3 Why PL-1 is the drafter's proposal

- **PL-1 keeps the charter's primary objective, P** (CHARTER section 2). It only changes which statistic carries a
  lever that cannot be judged on its trades.
- **PL-2 serves E-014's aim most directly,** but it makes an evenness measure an objective. That is the operator's to
  make, and a single evenness measure stands in for E-014's six.
- **PL-3 is the honest fallback** if the operator does not want a same-trades lever to carry at all.

Whichever is chosen, it replaces section 9.2 by one paragraph in the revised draft, before the pin. Nothing else in this
file changes with the choice.

### 9.4 Beside every stage C, deciding nothing

- The paired differences by start year (2024, 2025, 2026 to 07-16).
- The reverse walk-forward: the choice made on the judged block and read on the choice block (its statistic's draws
  `default_rng([20261943, 0])`).
- The `point` arm.
- Each lever alone: `lock` against `ref`, and `half` against `ref`, whichever cell was picked.

## 10. The floors (E-008), read for the pick

E-008 binds these floors:

1. **The long-run gate.** The pick's growth on the required bankroll at the bound is above zero. It is read on a gate
   campaign at the fresh seed **20261941**, 500 paths, 0 % denial, placement off, through the adapter's gate (16.1),
   with P-14 at the same seed beside it for the paired difference.
2. **Every offered R resolving, and realised risk matching intended.**
   - The trades are P-14's registered trades (7.1 item 5), so resolution is inherited.
   - Realised risk is checked on the pick's own taken trades: at least 90 % of trades realise at least 90 % of the
     intended risk in whole micros (D-212 (1)). The held-state rule changes the mix of leaves, not the leaves.
3. **Every firm rule verified:** section 3's table. A rule a cell leans on that is not verified is never loaded.
4. **Conduct tier 1** (section 3).

**What the floors can do.** They can close the family; they cannot carry it.

**When they are read.** Only after a stage-C pass. After a close at B or C, the gate rows beside (section 11, item 6)
are the record and decide nothing.

## 11. The journey scorecard -- the reading (CHARTER section 2; E-008, E-014, E-015)

**What it covers.** Every cell and its reference, on both bases. It is read on the verdict arm, on all starts and on the
judged block's starts, whatever stage the family ends at after stage A. The replay draws nothing.

1. **The scorecard.** P, S1 to S5c, S2, S3d, S6 and Q, as `USER_MILESTONES.md` defines them, and the frontier on P, S1,
   S3a and S5a. **S3c is comparable across this family's cells.** Every cell of a base shares one trade stream, which is
   the only condition under which E-008 allows S3c to be compared.
2. **E-014's journey variables:**
   - sessions and cash to the first pass;
   - sessions and cash to the first payout;
   - **sessions to break-even** (the first session at which cumulative net cash is at or above zero, daily), the share
     reaching it by months 1, 2, 3, 6 and 12, and the share that later falls back below zero;
   - **the path's evenness:** the share of months with a positive net change, the longest run of months without a
     payout, the spread of monthly net, the deepest fall of cumulative net from its running high after break-even,
     payouts per month, and the largest single month's share of the year's payouts.
3. **Each measure as a distribution over start days** -- median, p10 and p90 -- with its uncertainty from the effective
   number of independent starts. The start day's share of the variance is reported across this family's four
   policies (S6's form): how much of a user's result is the policy, and how much the day they start.
4. **The paired readings, this family's own.** For every measure in items 1 and 2:
   - the per-start difference, cell less reference, as a distribution (p10, p50, p90);
   - **the shares of starts on which the cell is better, equal and worse** at months 1, 2, 3, 6 and 12 -- how many
     users a policy helps, and how many it hurts;
   - each mean difference with Q-16's calibrated one-sided 0.05 bound **[Q-16]**, its draws, if any, from seed
     **20261944**. These are reported, never a line, except the measure the operator's pass line names.
5. **E-007 (e)'s readings beside (Q-17's adapter):**
   - **The denial ladder (10, 25, 50 %)**, per payout, draws from seed **20261945**. A policy that changes the number of
     payouts changes its exposure to the firm's review, so the ladder may rank the cells differently from the 0 %
     verdict. That ranking is reported.
   - The placement on. During it, new funded accounts are Consistency only, and the placement's own payout terms apply
     (13620045). The cells' levers apply as defined in 5.1.
   - The binding Focused Trader models: a policy that strands fewer accounts recycles fewer funded accounts. The count of
     funded accounts activated and lost per start is reported.
   - P by month, mean net, CVaR10, P under a bankroll limit, the effective sample size, and 7.3's minimum detectable
     difference.
6. **The long-run gate beside, every cell.** Each cell's gate at its base's registered seed: P-14's 20261131 and
   P-16's 20261206, 500 paths, point and bound, with its zero-edge twin.
   - Each new cell is paired with its base's registered gate paths, so 7.1 is also this reading's reference.
   - The rows: growth on the required bankroll, the required bankroll, payouts a month, and days to the first payout
     (D-564 (4)'s rows).
   - **The trade-off between this family's question and Stage 2's** -- the first months against two-year growth -- is
     read off these rows beside the scorecard.
7. **The evenness trade-off curve.** The four policies on each base give four points of "ahead" (P) against each
   evenness measure. The step from each point to the next is reported, in the form E-015's menu reading fixes: how much
   of the share ahead each step of evenness costs.
8. **Limits (E-015).** Once approved by the operator, they are **menu flags only**: a cell crossing a limit is shown
   with which limit and by how much, and a limit never fails a cell. Until they are approved, the menu is read without
   flags, and it says so.
9. **Not modelled, and said so wherever this scorecard appears:** a user who stops when their own money runs out, the
   user's time, taxes.

## 12. What a pass and a fail mean

**CARRIED** (under PL-1 or PL-2: stage C and section 10 all hold).

- The pick is a development finding on a late-development block.
- The design it makes, P-14's trades with the pick's payout rule, takes a registration id (D-621 (9)'s house form),
  its registered development test, the auditor, and one confirmation (section 13).
- What the user is told is the pick's scorecard as a distribution (section 11), never one number.

**CLOSED** at stage A (an identity, an oracle, or 7.3), at B (no cell above P-14 on the choice block), at C (the line
or a condition), or at a floor.

- The reason goes in a decision row.
- A close at C is recorded as **"no payout policy in this grid moved the named measure by more than the MDD (7.3) at
  this family's level"**, never as "payout policy does not matter".
- **For a user's first months, on P-14's trades and table, taking the maximum at the first eligible close stands,** and
  the trade-off curve (11, item 7) is the record of what each step of evenness costs.
- The closure binds this specification. A later payout family names it, states what changed and why it is a different
  hypothesis, and is judged on data this family did not read.

**PL-3.** The family closes by construction with its readings. That is the result.

## 13. The confirmation, declared before any development read

- **The window.** NQ from 2026-07-17 (`config/windows.yaml`, `reserve`, reserved). It is not on disk, never read until
  a carried design is registered, and a purchase (the operator's, stated in `docs/OPERATOR_SETUP.md` and waited for).
  It becomes NQ's fourth confirmation window only by the operator's decision (Stage 2 D-107), and it is wanted by
  Stage 2's draft P-16 confirmation and by F-02's draft as well. If any test reads it first, the lead records that
  before registration, and the operator decides whether it can still confirm this pick.
- **What it would test.** The pick's paired difference on the measure the pass line names, against P-14 on the window's
  starts, one-sided at the registered 0.05, by Q-16's statistic **[Q-16]**, its draws, if any, from seed **20261946**.
- **What it cannot test at six months.** About 126 sessions give about 63 starts with a month-3 horizon: one 63-start
  window. On that, no interval on a P difference exists (red team M1). So the window must hold at least the number of
  63-start windows at which Q-16's paired statistic, one-sided at 0.05, has 80 % power for a difference equal to the
  pick's judged lower bound at the family's level.
  - That number is computed when the pick is carried, and written in the carrying row before any confirmation data
    exists.
  - If it is more than the operator will buy, no confirmation is registered and the pick stays a development finding.
- **A same-trades policy may share P-14's own confirmation.** The pick's trades are P-14's, so one read of the window
  could confirm both, as two registered readings. Whether it may is the operator's decision with D-107. It is never
  taken by default.

## 14. Seeds, fixed now and checked

| seed | what it draws |
|---|---|
| 20261940 | 7.3's same-trades null: block sign-flips on the choice block, `default_rng([20261940, j])`, j the cell's index in 5.2 |
| 20261941 | the gate floor's fresh campaign seed (the pick and P-14 beside it), 500 paths |
| 20261942 | stage C: the draws of Q-16's paired statistic, if it draws any (else unused, and the result file says so) |
| 20261943 | the reverse walk-forward beside: `default_rng([20261943, 0])` |
| 20261944 | the scorecard's calibrated paired readings beside (11, item 4), if they draw |
| 20261945 | the denial ladder's draws for this family's cells (11, item 5) |
| 20261946 | the confirmation's statistic, if it draws |
| 20261947 | the build's tests: toy campaigns, and T-3's synthetic judged block |
| 20261948 | the build's fast size test of the paired statistic on a synthetic same-trades series (T-6) |
| 20261949 | reserved; unused, and every result file says so |

**The check.**

- **The search (2026-11-15).** A word-bounded search of the whole working tree, the vendored snapshot and its results
  included, binary files skipped, ran with `grep -rIowh --exclude-dir=.git -E "2026194[0-9]" .`. It found 20261940 and
  20261949 only in this item's brief (`docs/briefs/Q-25_2026-11-15.md`), as the proposal's range. Without word
  bounds, nothing else matched.
- **The same search over every branch of the repository** (`git grep -E "2026194[0-9]"` on each of `master`, `wt/*`
  and their remotes) found the same brief and nothing else.
- **Not searched:** Stage 2's working tree beyond its vendored snapshot. Its decision log and scripts are vendored and
  were searched.

**Inherited, and used only as their owners registered them:**

- P-14's campaign seed 20261131, for the identity and the paired gate beside (E-002);
- P-16's gate seed 20261206 and its coin's seed 20261102;
- Q-16's 20261910 to 20261919, Q-17's 20261920 to 20261929, and F-02's draft's 20261930 to 20261939, which are theirs.

## 15. Multiplicity and the budget

1. **k.** This family takes the next free program family number at its pin: k = 11, 12 or 13 depending on whether F-02
   and F-B are pinned first. Its level is 0.05 / (k (k + 1)), written by the gatekeeper in the pinning row.
2. **One cell reaches judgement:** stage B's pick on P-14's trades. There is no further division inside the family.
   - PL-1's (b) and (c), and PL-2's (b'), are conditions in an intersection. They are not further claims.
   - The P-16 cells are beside and never judged against R\*.
   - Stage B is on the choice block and spends nothing.
3. **Counted:**
   - 8 cells run;
   - 6 new -- `lock`, `half` and `lock_half` on each base -- counted as the family's variants whether void, closed or
     read;
   - 2 references that reproduce registered rows, counted as identities;
   - 3 hypotheses at the choice stage, 1 judged.

   Whether the references count among the cells is the gatekeeper's convention (D-564 counted "six cells, five new");
   the result files record both numbers.
4. **The honesty sentence.** Stage 2 ran programs S and U on this window, each with its own 5 %, and read payout policy
   on P-16's trades over the whole of it (section 2). The development-stage level is a screening threshold; the decision
   is carried by one confirmation on unread data (D-189), if the operator buys one.

## 16. The build: adapters, identities and tests

### 16.1 The adapters (in `extended/`, never in `vendor/`)

1. **The funded account.** A subclass of the vendored `FundedAccount`, passed through the engine's own seam
   `simulate_lockstep_path(funded_account_cls=...)` (R7). In the U1 replay it goes through `customer_slices.replay`'s
   path arguments.
   - `lock` overrides `_standard_eligible`: the firm's eligibility, plus "paid once, or the floor at $0".
   - `half` is the Protocol's own `payout_frac` (`dataclasses.replace` of the base's Protocol, as D-565 did).
   - The ledger's `eligible` column must record the firm's eligibility, not the policy's (the held count reads it).
2. **The held-state rule.** A wrapper on the table, or a read of the account's winning days that the wrapper alone sees
   -- the build's choice, held to 7.1 and T-4. It must not change the firm's count, the eligibility, or any leaf.
3. **The gate.** `gate.run_gate` takes no `funded_account_cls`. The build composes the same campaign call
   (`simulate_lockstep_campaign`, point and bound, each R's shift) in `extended/`, with no substitution of any vendored
   attribute (the lesson of E-011's first run). It is held to 7.1 items 1 and 3 at all 500 paths.

### 16.2 The rules in code

Every value in section 3 is read from the ledger by the engine's loader:

- the lock balance as `xfa_lock_at - xfa_mll_start`;
- the minimum as `payout_min`;
- the maximum as `payout_max_frac_of_balance` and `xfa_std_cap`.

A test greps the adapter for the literals 2000, 125 and 0.5 outside comments, and fails on any.

### 16.3 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-1 | with both levers off, the adapter's funded account equals the vendored one bit for bit on toy campaigns (seed 20261947): every day's balance, floor, request, payout and cash |
| T-2 | `lock`: no first payout while the floor is below $0; a first request at the first eligible close with the floor at $0, at the maximum; later requests as P-14's; an account that reached $2,000 and fell back is not held |
| T-3 | stage B's pick and every planning output are byte-identical when every session from 2024-01-02 is replaced (seed 20261947) |
| T-4 | the held-state rule: it fires only on accounts held at the last close, and is re-read at every close; a held account's decision equals the table's leaf at four winning days, same state otherwise; it never fires under P-14's rule; at every balance of at least $250 with no request the day before, funded or paid, the leaf read trades (re-derived from the policy file, with D-654 (3) and (9)'s no-trade leaves listed from it) |
| T-5 | `half`: every request is half the maximum and at least $125; a balance below $500 holds; the scaling tier follows the balance after a payout |
| T-6 | Q-16's statistic holds its size on a synthetic same-trades series (sparse differences, 63-session dependence; seed 20261948); fast |
| T-7 | 7.2's oracles on toy campaigns |
| T-8 | 7.1 at 4 paths and 4 starts a configuration and arm (`slow`); the full 500 paths and every start are the run's first stage (heavy) |
| T-9 | section 14's seeds appear nowhere else in the build's commit; 16.2's literal check |
| T-10 | stage C reads the pick from stage B's result file by its sha256; its entry point cannot run stage B |

## 17. Outputs, counts and the run

- **Files:**
  - `results/pp_payout.csv`, with sections `identity`, `oracle`, `null_check`, `planning`, `choice`, `judged`, `floor`
    and `beside`;
  - `results/pp_journey.csv`, the section 11 scorecard;
  - `results/pp_gate.csv`, the gate rows.

  Each is written with its sidecar manifest through `extended.results.write_result`, carrying:
  - `prereg_id`, the family's F-id;
  - the cell counts (8 run, 6 new);
  - the pass-line form the operator chose;
  - every seed and parameter;
  - the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`.

  They are EXPLORATORY until a carried design is registered.
- **The run.**
  - It runs once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
    its end.
  - **Weight: heavy.** E-010's U1 identity for two configurations peaked near 1.4 GB. Eight cells' replays, two arms,
    every start, and the gates add up to several hours at two workers.
  - The stages run in order -- A (identities first), B, C, the floors -- and each stage's file is written before the
    next stage reads anything. A kill stops the sequence.
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run is read.
- **Waits:**
  - Q-05 holds (E-010);
  - Q-16 is merged;
  - the operator's pass-line choice;
  - Q-17's adapter, for 11 item 5;
  - the operator's approval of E-015's limits, for the menu's flags only.

## 18. Open before the pin

**The lead's:**

1. **Q-16's choice** fills the [Q-16] marks (6.1, 7.3, 8, 9.2, 11, 13). It also settles whether its calibration
   already covers a same-trades series; 7.3's null check runs either way.
2. **The gate adapter (16.1 item 3).** Either the build composes the gate call as described, or the lead decides that
   the floor and the gate beside are read another way. That is decided before the pin.
3. **Counting:** whether the references count among the cells (15, item 3).
4. **A doubt about Stage 2 D-566's buffer reading, for the lead** (not this family's to settle).
   - Under `keep_balance`, an eligible account whose capped request falls below $125 is left unpaid. It then meets the
     table's no-trade leaves at five winning days, which D-654 (3) and (9) recorded, and sits for good.
   - D-566 (2) explained the $2,000 buffer's cost as "more balance held means fewer accounts recycled". Part of it may
     instead be that lock.
   - This was found by reading the table and the engine's request code only. Nothing was run. If it matters, it is an
     exploratory reading under its own row.

**The operator's:**

1. **The pass line for a same-trades lever: PL-1, PL-2 or PL-3** (section 9). The draft is not pinnable until it is
   answered. If the lead must proceed without an answer, the default is PL-3, which changes no objective.
2. **Under PL-1 only:** S5a's tolerance as on record, or in dollars (red team B-5).
3. **The confirmation** (section 13): NQ's fourth window (D-107), its length and its purchase, and whether this
   family's pick may share P-14's confirmation.
4. **The levels of E-015's limits** (approval pending). They are flags only, and never block.

## 19. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*
