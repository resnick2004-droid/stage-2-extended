# DRAFT: payout policy in a user's first months (reading PP) -- a described reading, unnumbered, not declared

**Status: DRAFT, third version, 2026-11-16 (TASK_QUEUE Q-92).** It brings the second version (Q-42, merged under E-025)
to the program's current standard, for its red team:

- the interval's windows and its honesty check rebuilt (E-058 (5));
- the reader's rules (E-041, E-053);
- the gate and the U1 replay through the merged adapters and their identities (E-028, E-044 (3), E-049; Q-76);
- the readings beside without the Focused Trader models, which the engine refuses for this reading's class;
- the comparison at a level dropped (E-023 (1), E-025);
- E-034's unstated rules, and E-029's and E-050's pinned calendars.

Section 0 maps every change to its source row. The second version redrafted the first (Q-25, E-018) on the red team's
review (`docs/reviews/DRAFT_F-P_payout_policy_2026-11-16.md`, Q-31) and under the operator's ruling **E-023 (1)**
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
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16, read only inside Stage 2's engine by P-14's and P-16's registered builders (this reading's own code reads no bar; the engine's reads are authorised through `extended/reader.py`, section 5 item 6) |
| the unit | one start day, replayed as U1 replays it (`vendor/stage2/docs/USER_MILESTONES.md`); each cell paired with its base on the same start |
| blocks | all starts (the menu's headline); the early block, purged per measure by `u_select.block(records, "early", h)`; the late block from 2024-01-02 (section 5) |
| cells | 2 first-request rules x 2 amounts x 2 trade streams = **8 policy runs** (6 new, 2 references that must reproduce registered rows), plus **3 rule-sensitivity runs** on P-14 (6.3) = **11 runs** at 0 % denial with the placement off, both arms |
| beside | 32 replays (the denial ladder's three levels and the placement on, for each of the 8 policy runs, verdict arm) and 8 gates (6 new, 2 identities) (section 12) |
| the menu | the 6 new policy cells and their 2 references, each read against its base |
| judged-block reads | three purposes, on the line of section 5 item 6; the identities from `identity/*.py` under their own row (8.1) |
| seeds | from 20261940 to 20261949: two in use, one reserved, seven retired and never used; the denial ladder's start seeds inherited from Q-17 (section 11) |
| confirmation | none: nothing is carried (section 10) |

---

## 0. What changed, by source row

### 0.1 From the second version to this one (Q-92)

| source row | what it asks | the second version | this version | where |
|---|---|---|---|---|
| **E-058 (5)**, as the brief Q-92 states it; the firms reading's review M5 and its Appendix A1 (`docs/reviews/DRAFT_RD_firms_2026-11-16.md`) | adjacent h-start windows share sessions, so a 90 % interval on them under-covers, and an honesty check on independent windows cannot see it | n_w consecutive non-overlapping h-start windows; the honesty check on independent window means | **windows separated by h starts** (every other window kept, from the block's first start), so no two share a session; the interval, the sign count and the MDD on the kept windows; **the honesty check rebuilt on overlapping series**, built from sessions as the reading's own are (the lumpy and persistent shapes now on sessions; the mirror dropped, since a two-sided interval covers a series and its negation alike, and the misses above and below printed instead); a reading whose coverage at its window count is below 0.88 labelled; T-6's rule held on synthetic series in this commit (`tests/test_pp_draft.py`) | 5 item 4, 9.2, 13.3 |
| **E-023 (1), E-025**; the firms review's m1 (the same item there) | a described reading has no level and carries nothing | 9.2 item 8: Q-16's calibrated paired comparison beside, at a one-tailed 0.05 | **dropped**: no comparison at any level is printed; seed 20261944 retired, never used; the MDD stated as a resolution, not as a test's power | 9.2, 11 |
| **E-041**; E-053 (2) | a pinned described reading declares its judged-block reads | no line | **the `Judged-block reads:` line**, three purposes, none a choosing word, parsed by `extended.reader.declared_purposes` in `tests/test_pp_draft.py` | 5 item 6 |
| **E-053** (the drafters' stale items); E-025 (1) | strike the stale pin item | 15 item 1: the hash test re-hashes only `prereg/F-` files | **struck**: E-025 (1) widened the hash test to `prereg/RD-` files and E-041 the reader; what stays open is the file's name at the pin | 15 |
| **E-053** (the once-rule, `extended/reader.py`); E-026 | each declared purpose allows one clean run | "only the first complete run is read" | a restart, a rerun after a failure, or any further run under one of the line's purposes needs **`repeat='E-NNN'`**, a decision row naming this file -- one row, one more run | 14 |
| **E-026, E-037, E-041** (the reader's `identity` rule) | whole-window identities run only from `identity/*.py` | 8.1 as the reading's own first stage | the identities against registered files (8.1 items 1-3) run first from **`identity/pp_identity.py`**, under the purpose `identity` and their own decision row; the reading's run repeats only comparisons on its own replays | 8.1, 14 |
| **E-028** (Q-47), **E-044 (3)** (Q-51), **E-049** (Q-71, Q-80) | the held-state policy's gate is `extended/gate.py`'s declared funded-account class, held to its identities | "the build composes the same campaign call in `extended/`" | **`extended/gate.py`'s `run_gate(funded_account_cls=...)`**; Q-51 held for the gate before Q-71; Q-80 owed for the re-composed campaign; this reading's gates wait for Q-80 and for their own identity | 8.1, 9.1 item 8, 13.1 item 3, 14 |
| **E-046 (3)** (Q-76: `extended/user_beside.py`'s `funded_account_cls`, wt/wt-user f92ac5e, its merge pending at this draft) | the U1 replay with a declared funded-account class | through `customer_slices.replay`'s path arguments | **through `run_starts(..., funded_account_cls=...)`**; its U1 start-row identity with a class owed (heavy) | 13.1 item 1, 14 |
| **E-007 (e)**; the engine (`lockstep.py` 1403-1408); Q-76 | the engine refuses the Focused Trader models for any class but the vendored `FundedAccount` | the binding Focused Trader models read for every cell | **not read for any cell** (every cell runs this reading's class); reported beside: the denial ladder, the placement on, P by month, mean net, CVaR10, P under a bankroll limit, n_eff and the MDD; the bases' Focused Trader readings cited from Q-44's file, never rerun or paired; the gap named on the menu | 7.2, 9.1 item 7 |
| **E-024** (Q-17's seeds); the firms review's m4 | Q-76 draws each start's denial seed from Q-17's base, and no keyword takes another | the ladder drawn from seed 20261945 | the ladder's start seeds are **Q-17's**, as `run_starts` draws them: common to every cell, its base and Q-44's reading of the base; 20261945 retired, never used; the `ref` cell's ladder rows checked against Q-44's per-start file | 8.1 item 6, 9.1 item 7, 11 |
| **E-034** | the payout request amount: unstated; F-P's half request stays an assumption | an optional rules-verifier reading open (15 item 3) | **read** (Q-39): unstated, and 8284233's worked examples show requests below the maximum; `half` stays an assumption, named wherever it is read; the open item closed | 4, 15 |
| **E-034** | the unstated news rules in every scorecard's "not modelled" note | -- | listed in 4 and 9.1 item 11: which events count, holding a position through a release, the GDP release minute; the full-size funded opening held through an unnamed release kept as registered | 4, 9.1 item 11 |
| **E-029** | the pinned early-close calendar, where the reading uses days | -- | the holiday-hours gap (13350348) counted on E-029's calendar; **no day voided** (the registered streams are replayed whole, and a day sits in both members of every pair), E-029's voided days listed with the starts whose windows hold them | 4, 8.3 |
| **E-050** | the pinned FOMC-minutes calendar, where the reading uses days | -- | the offered trades open at a minutes release (13:00 CT on E-050's days), which Topstep's Tier 1 list does not name (E-034), counted per stream, and per cell those executed at the full contract allowance; a count, never a ruling | 4, 8.3 |
| the declaration discipline (`prereg-discipline`: every parameter classed) | fixed / searched / dropped | classes "described", "assumed", "fixed, a design choice" | **fixed** (each lever's two values both run; an assumption labelled as one) or **dropped**; searched: none | 7 |
| the drafter, on `lockstep.py` 800-811 and 1500-1503 (no row) | what the placement on does to the levers | "the levers apply as 6.1 defines them" | stated: L2 applies to the placement's Consistency accounts (the engine's placement policy keeps `payout_frac`); L1 and the held-state rule do not (both are defined on the Standard path's eligibility); those accounts' eligible-and-unpaid sessions counted | 9.1 item 7 |
| the drafter (cost; the firms reading's 7.4 form) | which arm the readings beside run on | unstated | the verdict arm only, with Q-76's exact-length check (`EXACT_EVERY`) | 9.1 item 7, 12 |

### 0.2 From the first version to the second (Q-42, E-025), finding by finding

Kept as the second version wrote it; its "where" column names the sections as they now stand.

| review item | the first version | the second version | where |
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
| F10 | "a payout policy changes no trade"; differences "mostly zero" | stated truly: the offered trades are the same; after the first changed payout, executed sizes, R, accounts, purchases and fees diverge and stay diverged; the per-start difference is lumpy, and dense for `half` | 0.3, 6.4 |
| F11 | the request amount's freedom not listed | listed under "Assumed", with an optional rules-verifier reading | 4 |
| N1 | the doubt about D-566 in an open item | a separate, labelled exploratory check, fully specified | Appendix A |
| N2 | -- | the verdict arm's bound read on the whole window, disclosed | 3, 5 |
| N3 | P-16's `half` cell already read in D-564's journey | kept, disclosed | 3 |
| N4 | -- | months 1-3 are where both levers cost most by their mechanics; any gain should show at months 6-12; the menu reads every month | 2, 9 |
| N5 | -- | a rule for a series that is zero on every window, and for too few windows | 9.2 |
| N6 | "the remaining balance becomes the loss floor" | "the remaining balance is all that can be lost" | 2 |

### 0.3 What a payout policy changes, stated truly (F10)

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
- **The third version's drafter, in addition:** the firms reading's draft and its review with the review's appendix
  code; `extended/reader.py`, `extended/gate.py`, and `extended/user_beside.py` as Q-76 left it on wt/wt-user
  (f92ac5e); `lockstep.py`'s funded account (525-860), its class checks (1380-1420) and the placement's policy
  (1500-1503); `risk_policy.account_state`; the Q-39 entries of `config/rules_extended.yaml`; the headers of the two
  pinned calendars; and the header of `scripts/user_beside.py`. Code, rules and calendars only.
- No result file of any payout cell was opened. Q-44's files do not exist yet. The synthetic coverage figures of
  `tests/test_pp_draft.py` were computed (no data), as the firms review's A1 had computed them.

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
2. **The request's amount (F11; E-034).** A request may be any amount from the $125 minimum up to the maximum. The
   ledger quotes "Max Payout per request: 50% of your account balance up to the cap" and "Minimum Payout: $125"
   (`payout_max_frac_of_balance`, `payout_min`), not that the amount in between is free. `half` needs it. D-564 made the
   same inference. **Q-39 read it (E-034; `config/rules_extended.yaml`, `payout_request_amount_choice`, status
   `unstated`):** no official page says whether a request may be any amount between the minimum and the maximum, and
   8284233's worked examples show requests below the 50 % maximum. So it **stays an assumption** (E-025 (4), E-034),
   named wherever `half` is read. Only a reading of the request form itself would settle it (the operator's browser, no
   purchase, no request submitted); this reading does not wait for one.

**Not modelled, as in every registered row, and named in every scorecard's "not modelled" note (9.1 item 11):**

- **Payouts unavailable in holiday hours** (13350348). Counted, not modelled: 8.3 prints each cell's requests made at a
  session that closes early, or at the last session before a scheduled holiday, by E-029's pinned calendar
  (`config/calendar_early_closes.csv`, sha256 `72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2`).
- **The move to a Live Funded Account.**
- **Topstep's unstated news rules (E-034).**
  - Which scheduled releases count as "major news" under 10305426's "full Maximum Position Size directly into a
    scheduled major news event", and whether a position opened before a release and held through it counts: unstated
    (`max_size_into_major_news_scope`).
  - The GDP release minute: unstated (`tier1_window_gdp_release`).
  - The Tier 1 windows and the listed releases changed against Stage 2's ledger (`tier1_news_events_restriction`,
    `economic_releases_list`); the registered 07:35:00 report-day cut still keeps entries out of the CPI, NFP and PPI
    windows (E-007's C1, E-034).
  - The full-size funded opening held through an unnamed release stays as registered (E-034's decision; the tier of
    "maximum size into major news" is the operator's, D-145 tier 1).

  A payout policy changes executed sizes, though not the offered trades. So 8.3 counts, per stream, the offered trades
  open at an FOMC minutes release -- 13:00 CT on the days of E-050's pinned calendar
  (`config/calendar_fomc_minutes.csv`, sha256 `0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7`), a
  scheduled release Topstep's Tier 1 list does not name -- and, per cell, how many of them were executed at the full
  contract allowance. A count, never a ruling. GDP releases are not counted: no pinned calendar of them exists here.

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
   `customer_slices.replay`); here the same replay is made through Q-17's adapter with Q-76's keyword (13.1 item 1).
   The headline is the `verdict` arm (every R at its registered bound), with `point` beside. `USER_MILESTONES.md`'s
   definitions are used unchanged. A month is 21 sessions.
2. **Pairing.** Each cell and its base run on the same start days, the same blocks and the same seeds. The per-start
   difference is the unit of every paired reading.
3. **The blocks, per measure (F6).** Every reading at horizon h (63 for P and months 1 to 3, 126 for month 6, 189 for
   month 9, 252 for month 12) is read on three sets of starts:
   - **all starts** with h sessions left (`u_select.block(records, None, h)`) -- the menu's headline;
   - **the early block**, `u_select.block(records, "early", h)` (`propedge/research/u_select.py`): the starts of 2023
     and before, less every start within h sessions of 2023's last start. No early reading touches a 2024 session,
     except through the verdict arm's bound (N2, section 3);
   - **the late block**, `u_select.block(records, "late", h)`: the starts from 2024-01-02 with h sessions left.

   This is the house rule, D-621 (4)(b); program U applied it, and the first version's sentence that it had not was
   wrong. Nothing is chosen on any block. The early and late blocks are read separately so that the menu can flag a
   policy whose effect changes sign between them (9.1 item 10).
4. **How much each block holds.** The late block holds about nine non-overlapping 63-start windows (B_objective, Q3),
   and fewer at months 6 and 12. All starts hold several times more. The interval keeps only every other window, so
   that no two of its windows share a session (9.2 item 1, E-058 (5)): about half as many. At month 12 even all starts
   may hold fewer than four, and such a reading prints the sign count alone. Each reading prints its own count (9.2).
5. **No NQ from 2026-07-17** is on disk or read.
6. **The judged block's seal (E-026, E-041).** Stage 2's engine reads the bars and the atlas itself, in the U1 replay
   and in the gate. So the reading's runner authorises those reads with `extended.reader.authorise_engine_read` before
   the engine runs, from a clean checkout of a committed commit, under the purposes on this line:

   - **Judged-block reads:** `payout_scorecard`, `payout_ladder_beside`, `payout_gate_beside`

   - `payout_scorecard`: the replays at 0 % denial with the placement off -- every policy cell and the rule-sensitivity
     runs, both arms;
   - `payout_ladder_beside`: the replays under the denial ladder and the placement on (9.1 item 7);
   - `payout_gate_beside`: the gates (9.1 item 8).

   None is a choosing or fitting purpose (the reader's `CHOICE_WORDS`; checked in `tests/test_pp_draft.py`). The
   identities against registered files run from `identity/*.py`, under the purpose `identity` and their own decision
   row, never under this line (8.1). Appendix A reads under its own row, never under this line.

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

See 0.3. The pairing is on start days with identical offers, not on identical executed trades. A check confirms every
trade a cell takes is one of its base's registered offered trades (8.1 item 5). The divergences -- sizes, R, which
account takes which offer, evaluations bought, fees -- are the policy's effects, and the reading reports them (9.1 item
6).

## 7. Parameters: fixed, searched, dropped

### 7.1 The table

Every parameter is **fixed** or **dropped** (7.2). **Searched: none** -- nothing in this reading is chosen from data,
on any block. The two levers are fixed at two values each, and **both values are run and read** ("described", E-023
(1)): the program chooses neither; the operator chooses from the menu. An assumption is a fixed value no page states,
labelled wherever it is read.

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| trades | what is traded | fixed | P-14's registered trades (A3-BRK30-CB20), by U1's own builder | E-010; D-513 |
| trades, beside | the second stream | fixed | P-16's registered trades (`rc_s150_all_nr`), `rc150_dev_test.TRADES_SHA256` | E-002; D-544 |
| state table | sizing by account state | fixed | `state_dp_e-0.050_lamstar_noclose`, checked against `a3_brk30_cb20.NOCLOSE_POLICIES_SHA256`; not re-solved | D-501; D-564 (2) |
| held-state rule | what a held account trades | fixed -- **a declared design choice** | the table read at four winning days (6.3); the minimal rescue run beside | 6.3; the review's F5 |
| funded-account class | the code every cell's funded accounts run | fixed | this reading's subclass of the vendored `FundedAccount`, on every cell, `ref` included (13.1 item 1) | E-028; Q-76; 7.2 (the Focused Trader models) |
| seats, budget, routing | accounts and purchases | fixed | each base's own: five seats; 20 evaluation purchases in 21 sessions; the strict one-position rule | P-14's and P-16's registrations |
| payout path | Standard or Consistency | fixed | Standard | 7.2 |
| **L1, first request** | when the first payout is asked | fixed -- **both values run (described)** | `elig`, `lock` | 6.1; 8284204's lock |
| **L2, amount** | how much each request takes | fixed -- **both values run (described)** | `max`, `half` (`payout_frac` 1.0, 0.5) | 6.1; D-564's value; the engine's own field |
| cadence after the first | how often | fixed | every eligible close | the Standard path's own spacing; 7.2 |
| request timing | when in the day | fixed (an assumption) | after 5:00 PM CT | D-175 (section 4) |
| request amount | what may be asked | fixed (an assumption) | any amount from $125 to the maximum | F11; E-034; section 4 |
| payout method | fee and lag | fixed | Aeropay, $0, 3 trading days | D-24; `customer_slices.engine_args` |
| the rules of section 4 | caps, minimum, split, eligibility, floor | fixed | the ledger's values | 8284233, 8284204, 8284215 |
| arms | outcome shift | fixed | `verdict` the headline, `point` beside | CHARTER section 2; N2 |
| denial, placement | firm discretion | fixed | 0 % and the placement off in the headline; the denial ladder (10, 25, 50 %) and the placement on (Q-17's `rtp`) beside | E-008; E-007 (e); D-234, D-289 |
| the readings beside: arm and exact runs | where the ladder and the placement are read | fixed | the verdict arm; U1's exact-length runs on every 21st start index (Q-76's `EXACT_EVERY`), their differing count reported | 9.1 item 7; E-024 |
| the ladder's start seeds | the denial draws | fixed (inherited) | Q-17's: `lockstep.child_seed(20261920, 0, start_day)`, as `run_starts` draws them | E-024; section 11 |
| horizons | replay length | fixed | U1's: the long replay to 252 sessions, and the exact runs | D-620 |
| reading horizons h | the sessions a reading needs | fixed | 63 for P and months 1 to 3; 126, 189 and 252 for months 6, 9 and 12 | 5 item 3 |
| blocks | which starts | fixed | all; early and late per measure (section 5) | D-621 (4)(b); F6 |
| the interval's windows | which starts the interval rests on | fixed | h consecutive starts, every other window kept from the block's first start | 9.2 item 1; E-058 (5) |
| the interval | the uncertainty on each paired reading | fixed | two-sided 90 % Student t on the kept windows' means, from 4 windows | 9.2 item 2; E-007 (e); F1, F8 |
| the honesty check | the interval's coverage beside | fixed | 9.2 item 7's shapes and grid, 20,000 series a setting, seed 20261948 | 9.2 item 7; E-058 (5) |
| the coverage label | when an interval is labelled | fixed | below 0.88 on any shape at its (h, n_w) | 9.2 item 7; the firms review's M5 remedy 3 |

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
- **P-15's 25-point coin.** Its U1 start rows are reproduced at 4 starts only; every start is owed (Q-22, E-026).
- **The binding Focused Trader models beside** (E-007 (e)). The engine applies the Focused Trader Program to the
  vendored `FundedAccount` only (`simulate_lockstep_path`, `lockstep.py` 1403-1408: "it applies to Topstep's
  FundedAccount only"), and Q-76's adapter refuses the ten models for any other class before a start runs. Every cell
  here runs this reading's class (13.1 item 1). Running `ref` and `half` on the vendored class instead would put a
  base's four cells on two code paths, and `lock` and `lock_half` would still have no reading. So **no cell reads
  them**. The bases' own readings are Q-17's (Q-44's `results/user_beside.csv`, at the vendored class), cited beside by
  file, never rerun or paired here. What a payout policy does under the Focused Trader Program is not read, and the
  menu says so.
- **All-accounts forfeiture and the three-warning placement** (Q-17's `forfeit_10/25/50` and `rtp_w3`). Not among
  E-007 (e)'s readings; Q-44 reads them for the bases.
- **Q-16's comparison beside** (the second version's 9.2 item 8). A level in a reading that has none (E-023 (1),
  E-025; the firms review's m1, the same item there).
- **An interval on adjacent windows, or a lag-1 HAC variance of their means** (the firms review's M5 remedy 1, its
  second option). Replaced by separated windows (E-058 (5)), whose coverage the honesty check shows directly on the
  reading's own construction (9.2 item 7).

## 8. Before any reading: identities, oracles, mechanics

### 8.1 The identities, refusing (E-004, E-010; whole-window identities only from `identity/*.py`, E-026, E-041)

**The engine's, owed by other items; this reading waits for each.**

- **The gate (E-049).** Q-80: `extended/gate.py` through its re-composed campaign (`extended/campaign.py`, Q-71)
  reproduces P-14's and P-16's registered gate paths at 500 paths, every arm (`--cls all`: no class, the pass-through
  class, the seams at Topstep's values). Q-51 held the same for the gate before Q-71 (E-044 (3): both designs, both
  shifts, every `PATH_COLS` column to 1e-6, no class and the pass-through class). Since Q-71 every call passes through
  the re-composed campaign, so Q-51 no longer covers it, and nothing reads through `extended/gate.py` here until Q-80
  holds.
- **The U1 replay with a declared class (Q-76).** `identity/user_beside_identity.py --funded-cls both`: U1's start
  rows for P-14 and P-16, both arms, every start, at no class and with the gate's pass-through class (heavy, owed).

**This reading's own: items 1 to 3**, run first, from **`identity/pp_identity.py`** (built with the adapter; it calls
the comparisons of `identity/gate_identity.py` and `identity/user_beside_identity.py` with this reading's class),
from a clean checkout of the reading's commit, under the purpose `identity` and the decision row that registers it
(the lead's) -- never under this file's `Judged-block reads:` line. The reference policy (`elig`, `max`) runs with
the whole adapter in place -- this reading's funded-account class, the held-state rule and the payout fields -- and
must reproduce:

1. **P-14's registered gate paths:** `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, `gate` run, 0 % denial,
   point and bound, through `extended/gate.py` with the class given. Every `zero_edge_decomposition.PATH_COLS` column
   to 1e-6, all 500 paths, at P-14's seed 20261131.
2. **U1's start rows for P-14,** through `extended.user_beside.run_starts` with the class given and the response
   `off`: `vendor/stage2/results/user_journey.csv` section `start`, config `p14`, both arms, every start, every column
   as E-010 compared them (money and the ratio to 1e-6; counts, days, dates and text exactly), plus the study's own
   checks of payouts and fees against the engine's totals.
3. **The same for P-16:** `rc_s150_all_gate_paths.csv` at seed 20261206, after its trades' hash; U1's `p16` start
   rows.

**Inside the reading's own run, on its own replays (no further read):**

4. **The levers are off in `ref`:** the held-state rule fires on no start and no path, no first request is held, and
   the recorder's `eligible` column equals the vendored engine's on every account-day. All three are counted and
   written -- on the starts here, and on the paths by `identity/pp_identity.py` in its gate runs (items 1 and 3). And
   the reading's own `ref` start rows equal U1's again (item 2's comparison, refusing).
5. **The trades are the base's:** every trade any cell's account takes is one of its base's registered offered trades.
   This is checked for every new cell before any reading of it.
6. **The readings beside, at `ref`:** the `ref` cell under `denial_10`, `denial_25`, `denial_50` and `rtp`, verdict
   arm, equals Q-44's `results/user_beside_starts.csv` for the same design, arm and response, start for start, every
   column that file writes, at its precision (money to the cent), apart from the class's name. The draws are the same
   (section 11), and Q-76's pass-through identity shows a class that changes nothing changes no row.

Any failure stops the reading, and the failure protocol applies; nothing is rerun until it passes, and a rerun is a
further judged read under `repeat=` (section 14). E-010's negative controls (the verdict rows against the point rows;
a 2e-6 nudge) show that the comparison is not vacuous.

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
- the share of starts with an account held at sessions 63, 126 and 252;
- **the holiday-hours reach** (section 4, not modelled): the requests made at a session that closes early, or at the
  last session before a scheduled holiday, by E-029's pinned calendar -- per cell, against its base;
- **an unnamed release** (section 4, E-034): per stream, the offered trades open at 13:00 CT on a day of E-050's
  pinned FOMC-minutes calendar; per cell, how many of them were executed at the full contract allowance (the engine's
  own count of trades sized at the allowance);
- **E-029's voided days.** No day is voided here: the registered streams are replayed whole (8.1 needs them whole),
  and a day sits in both members of every pair alike. The three days E-029 voids for families (2020-07-01, 2025-06-30,
  2025-07-01) are listed, with the number of starts, per block and horizon, whose h sessions hold one.

A cell identical to its base on every start is reported as "no effect on these trades", and nothing more is read for it.

## 9. The reading: the journey scorecard and the menu (CHARTER sections 2-3; E-008, E-014, E-015, E-023)

### 9.1 What is read

**What is read.** Every cell, its base, and the rule-sensitivity runs (marked), on both arms (the verdict arm is the
headline) and on every block of section 5; the readings beside (item 7) on the verdict arm. The replay at 0 % draws
nothing.

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
7. **E-007 (e)'s readings beside**, through Q-17's adapter with Q-76's keyword (`extended.user_beside.run_starts(...,
   funded_account_cls=...)`, 13.1 item 1), each of the 8 policy cells, the verdict arm, U1's exact-length runs on every
   21st start index as Q-76 makes them (`EXACT_EVERY`), their differing count reported:
   - **the denial ladder** (`denial_10`, `denial_25`, `denial_50`): the engine's tier-3 model, one uniform drawn per
     exposed payout from each start's path seed, **Q-17's** `lockstep.child_seed(20261920, 0, start_day)`, as
     `run_starts` draws it (E-024; no keyword takes another). The seeds are common to every cell, its base and Q-44's
     reading of the base. The draws line up across cells only until their exposed payouts diverge, and that is the
     policy's effect. The cells change how many payouts are requested, so the ladder may rank them differently from
     the 0 % headline, and that ranking is printed;
   - **the placement on** (`rtp`: the gate's reading, the strictest). Accounts activated after the placement are on the
     Consistency path (13620045; the engine's `rtp_policy`, `lockstep.py` 1500-1503). **L2 applies to them** -- the
     engine's placement policy is the protocol's with only the path changed, so `payout_frac` carries. **L1 and the
     held-state rule do not** -- both are defined on the Standard path's eligibility, which a Consistency account never
     consults (`lockstep.py` 800-811). So under the placement, L1 acts only on accounts activated before it, though
     its effects carry through the rest of the path (0.3). Printed beside: per cell, the Consistency account-sessions
     that start eligible and unpaid (a `half` request below $125), which the table reads as it stands;
   - P by month, mean net, CVaR10, P under a bankroll limit, the effective sample size and the MDD (9.2);
   - **not read: the binding Focused Trader models** (7.2). The engine applies them to the vendored `FundedAccount`
     only, and every cell runs this reading's class. The bases' readings are cited from Q-44's file, never paired with
     a cell; the menu says the policies' effect under that program is not read.
8. **The long-run gate beside, every policy cell:**
   - **the run.** Each of the 8 policy cells' gate at its base's registered seed (P-14's 20261131, P-16's 20261206),
     500 paths, point and bound, with its zero-edge twin, paired with the base's registered gate paths, through
     `extended/gate.py` with this reading's class (13.1 item 3), after Q-80 holds (8.1). The two references' gates are
     8.1's identity runs; the rule-sensitivity runs take no gate;
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
    user's time, taxes; payouts unavailable in holiday hours; the move to a Live Funded Account; Topstep's unstated news
    rules (section 4, E-034: which releases count, holding through one, the GDP minute); the Focused Trader Program for
    any policy cell (item 7).

### 9.2 The uncertainty on each paired reading (fixed now; E-058 (5); F1, F8, N5)

These are descriptions, not tests. Nothing in this reading is compared with a critical value to decide anything, and
no reading has a level (E-023 (1), E-025).

1. **The windows (E-058 (5)).** For a reading at horizon h on a block, the block's starts, in start order, are cut
   into consecutive windows of h starts from the block's first start (a last incomplete window dropped), and **every
   other window is kept, from the first**.
   - Why: a start reads its own h sessions, so adjacent windows share h - 1 sessions. With independent sessions their
     means' lag-1 correlation is about one quarter, and a 90 % t interval on them covers about 0.83 (the firms
     review's M5 and its Appendix A1; this commit's `tests/test_pp_draft.py` finds the same). Two kept windows are
     separated by h starts and share no session.
   - n_w, the number of kept windows, is printed with every reading.
   - Only items 2, 3 and 5 rest on the kept windows. Every other reading -- the distributions, the shares, the mean
     difference itself -- uses every start of the block.
2. **The interval.** A two-sided 90 % interval from a Student t on the n_w kept windows' means, with n_w - 1 degrees
   of freedom, centred on their mean (printed with it, beside the mean over every start). **Printed only when n_w is
   at least 4** and the kept means are not all equal. When n_w is below 4, the reading prints "too few separated
   windows for an interval" and gives only item 3.
3. **The window sign count.** In how many of the n_w kept windows the cell's mean is above, equal to and below its
   base's. Always printed.
4. **The effective sample size.** From the Bartlett long-run variance of the per-start difference over every start of
   the block, with lag window h (audit B's form; `extended.user_measures.n_eff_bartlett`), printed beside.
5. **The minimum detectable difference (MDD):** (t(0.95; n_w - 1) + t(0.80; n_w - 1)) times the kept windows'
   standard error. It is the true mean difference that would put item 2's interval wholly on one side of zero in about
   80 % of repetitions, were the window means normal with that spread (`tests/test_pp_draft.py` holds the formula and
   the rate). A resolution, not a test. Printed beside each mean, in the same table and before it.
6. **A series that is zero on every start of the block** prints "identical on these trades", with no interval and no
   MDD. A series whose kept windows' means are all equal prints its sign count, and no interval and no MDD.
7. **The interval's honesty, printed beside, on overlapping series (E-058 (5)).** The coverage of item 2's interval,
   computed by the same code on synthetic series of known zero mean built as the reading's own are: values per
   session, each start's value read from its own h sessions, the starts cut and kept by item 1's rule.
   - **The settings:** every (h, n_w) at which the reading prints an interval, n_w taken from the block's start count
     (dates only, before any outcome is read); 20,000 series per setting.
   - **The seed:** **20261948**. Each setting draws from `numpy.random.default_rng([20261948, 1, shape, h, n_w])`,
     `shape` being the shape's index in the order below (0 to 20). T-6 draws under `[20261948, 0, ...]`, never these
     keys.
   - **The shapes:**
     - **gauss** (0): independent N(0, 1) sessions; a start's value is the mean of its h sessions;
     - **ahead** (1): the same sessions; a start's value is 1{the sum of its h sessions > 0} - 1/2;
     - **paired** (2): two walks whose sessions are 0.8 z + 0.6 e_a and 0.8 z + 0.6 e_b (z, e_a, e_b independent
       N(0, 1)); a start's value is 1{its walk-a sum > 0} - 1{its walk-b sum > 0}, a paired "ahead" difference;
     - **lumpy** (3 to 11: p in turn, s in turn within each p): the red team's skewed shape, now on sessions. Each
       session is +g with probability 1 - q and -g(1 - q)/q with probability q, where q = p/h (p rare sessions
       expected in h), plus N(0, h s^2) noise (a start's h-session mean has noise s). g = 0.01; p in {0.05, 0.10,
       0.20}; s in {0.0025, 0.005, 0.01}. A start's value is the mean of its h sessions;
     - **persistent** (12 to 20, the same order): the same values and noise, the rare sessions coming in episodes. A
       two-state chain is started from its stationary law: an ordinary session is followed by a rare one with
       probability p/h, a rare one by another rare one with probability 1 - 1/h (episodes of h sessions on average).
       The rare value is -g(1 - pi)/pi, with pi the chain's stationary rare share, so the mean stays exactly zero.
   - **The mirror is dropped** (the second version had it): a two-sided interval covers a series and its negation
     alike. Instead, beside the coverage, the shares of series whose interval misses above and misses below are
     printed, which is where a skewed shape shows.
   - **What is printed with every interval:** the lowest coverage over the shapes at its (h, n_w), and the shape it
     comes from. Where that is below **0.88**, the interval is labelled "under-covers at this window count" (the firms
     review's M5 remedy 3).

   The reader then sees how far a 90 % interval on a lumpy, persistent payout difference can be trusted at that
   count. The second version built these series as independent window means. That check reports near-nominal coverage
   for adjacent windows too, so it could not see their shortfall (`tests/test_pp_draft.py`).

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
| 20261943 | **retired, never used** | the first version's reverse walk-forward (no pick; dropped program-wide by E-031 (2)) |
| 20261944 | **retired, never used** | the second version's Q-16 comparison beside (dropped: no level, E-023 (1), E-025) |
| 20261945 | **retired, never used** | the second version's denial-ladder draws (the ladder now draws Q-17's start seeds, below) |
| 20261946 | **retired, never used** | the first version's confirmation (none now) |
| 20261947 | in use | the build's toy campaigns (T-1, T-2, T-4, T-5, T-7) and T-3's synthetic late block; already drawn by Q-47's synthetic gate identity, this reading's build (`identity/gate_identity.py`, E-028), whose fixture Q-70's identity imports (`identity/place_records_identity.py`, E-055) |
| 20261948 | in use | 9.2 item 7's honesty series (keys `[20261948, 1, shape, h, n_w]`) and T-6 (keys `[20261948, 0, ...]`; drawn in this commit by `tests/test_pp_draft.py`) |
| 20261949 | reserved, unused | -- |

**Retired seeds are not reassigned,** so no seed changes meaning between versions. Every result file lists them as
retired. 20261948 keeps its meaning (the honesty series and T-6); only the series' construction is rebuilt (9.2 item
7), and no draw was made under it before this version.

**The check, 2026-11-16 (this version).** A word-bounded search of the worktree, the vendored snapshot and its results
included and the licensed data excluded (`grep -rIow --exclude-dir=.git --exclude-dir=data -E "2026194[0-9]" .`), the
same search on every branch and remote branch (`git grep -IwoE "2026194[0-9]"` per ref), and the same search of the
other worktrees' working files, find the block only in:

- this file;
- the Q-25 brief and E-018, which record the block;
- the red team's review, and the F-B, F-O and F-R drafts, each listing "20261940-49" as taken (20261940, retired);
- `identity/gate_identity.py` and `identity/place_records_identity.py`: 20261947, as above.

`tests/test_pp_draft.py` repeats the check on every run: no seed in use or reserved appears in any other declaration,
anywhere in the vendored snapshot, or in a review's or audit's scratch.

**Inherited, and used only as their owners registered them:**

- P-14's seed 20261131;
- P-16's gate seed 20261206 and coin seed 20261102;
- **the denial ladder's start seeds:** Q-17's, `lockstep.child_seed(20261920, 0, start_day)` (`extended.user_beside.
  start_seed`, E-024), as Q-76's `run_starts` draws them for every replay -- no keyword takes another seed, and the
  same draws make the ladder's `ref` rows reproduce Q-44's (8.1 item 6);
- U1's replay seeds, as U1 passes them (the replay at 0 % draws nothing);
- for Appendix A, D-564's screen seeds 20261131 and 20261102.

## 12. Counting and the budget

1. **No program family number and no level** (E-023 (1)). The next numbered family's k is what it would be without this
   file.
2. **Counted under this reading's row:**
   - 11 runs at 0 % with the placement off, both arms: 6 new menu cells; 2 references, counted as identities; 3
     rule-sensitivity runs, labelled;
   - beside, labelled: 32 replays, verdict arm (`denial_10`, `denial_25`, `denial_50` and `rtp` for each of the 8 policy
     cells; the 8 at `ref` are 8.1 item 6's checks) and 8 gates (6 new; the 2 references' are 8.1's identities);
   - the honesty series: synthetic, no read;
   - every block read, recorded as read for payout policy (10).
3. **Nothing is selected by the program.** The operator's menu choice is a choice among described readings. It is
   recorded in its own row with the menu it was made from.

## 13. The build: adapters, identities and tests

### 13.1 The adapters (in `extended/`, never in `vendor/`)

1. **The funded account.** A subclass of the vendored `FundedAccount`, passed through the engine's seam
   `simulate_lockstep_path(funded_account_cls=...)`. **Every cell runs it, `ref` included**, so a base's four cells
   share one code path and 8.1's reference identity tests the class every cell runs.
   - **In the U1 replay** it goes through Q-76's keyword: `extended.user_beside.run_starts(design, arm, response, job,
     starts, workers, funded_account_cls=<this class>)` (E-046 (3); wt/wt-user f92ac5e, its merge pending at this
     draft), which puts it on every replay's path. The headline is the response `off` (the vendored replay's 0 %,
     placement-off call, U1's exact-length runs on every start); the readings beside are `denial_10`, `denial_25`,
     `denial_50` and `rtp`. Q-76 refuses the Focused Trader models for this class before any start runs (7.2).
   - **In the gate** it goes through `extended/gate.py`'s keyword (item 3).
   - **`lock`** overrides `_standard_eligible`. It computes the firm's eligibility (the vendored method), stores it in a
     field of its own, and returns the firm's eligibility and (paid once, or floor at $0).
   - **The firm's eligibility recorded (F7).** After `trade_day` returns, the subclass sets `last_eligible` back to the
     stored firm's value. So the daily recorder's `eligible` column (`lockstep.py`, the recorder's funded row) records
     the firm's eligibility, not the policy's. The held flag is set from the firm's eligibility at the same close.
   - **`half`** is the Protocol's own `payout_frac` (`dataclasses.replace` of the base's Protocol, as D-565 did). It
     leaves eligibility untouched.
2. **The held-state rule.** A read of the table in which only the winning days of a held account are counted as 4.
   "Held" is set at each close from the account's own fields (the firm's eligibility as `_standard_eligible` computes
   it, and P-14's request from the balance), never from the rounded state the table is handed. Where the read lives is
   the build's, held to 8.1 and T-4, with one constraint: it reaches the engine only through the engine's own
   arguments (the class keyword, or the design's own `risk_policy` and `protocol`), on the U1 replay and the gate
   alike, and never by substituting a vendored attribute (the lesson of E-011's first run). It never changes the firm's
   count, the eligibility, or any leaf. The minimal rescue (6.3) is the same read with a second mode.
3. **The gate.** `extended/gate.py`'s `run_gate` with its keyword `funded_account_cls` (Q-47, merged under E-028):
   the vendored gate's body, every helper imported, nothing substituted, refused unless the vendored source hashes to
   its pin. This reading gives the class, `half`'s Protocol through `protocol` and the held-state rule as item 2 says,
   and none of Q-71's seams and no recorder.
   - **Its identities.** Q-51 held at 500 paths for the gate before Q-71 (E-044 (3)). Since Q-71 every call passes
     through the re-composed campaign (`extended/campaign.py`, E-049), so Q-80's 500-path identities through it are
     owed, and this reading's gates wait for them (8.1).
   - **Then this reading's own:** 8.1 items 1 and 3, at all 500 paths, from `identity/pp_identity.py`.

### 13.2 The rules in code

Every value of section 4 is read from the ledger by the engine's loader:

- the lock balance as `xfa_lock_at - xfa_mll_start`;
- the minimum as `payout_min`;
- the maximum from `payout_max_frac_of_balance` and `xfa_std_cap`.

A test fails on the literals 2000, 125 or 0.5 in the adapter outside comments.

### 13.3 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 (this draft's commit) | `tests/test_pp_draft.py`: one `Judged-block reads:` line, its purposes parsed by `extended.reader.declared_purposes`, none choosing, none `identity` or `registered_design`; section 11 holds 20261940..20261949 once each, and a seed in use or reserved appears in no other declaration, nowhere in the vendored snapshot and in no review's or audit's scratch; no level in 9.2; section 0 cites every source row; and T-6's draft-stage form (below) |
| T-1 | with both levers off, the adapter's funded account equals the vendored one bit for bit on toy campaigns (seed 20261947): every day's balance, floor, request, payout, cash and recorded `eligible` |
| T-2 | `lock`: no first payout while the floor is below $0; the first request at the first eligible close with the floor at $0, at the maximum; later requests as P-14's; an account that reached $2,000 and fell back is not held; **at a held close the recorder writes `eligible` True (the firm's) and `requested` 0**; under the placement on, a Consistency-path account is never held by `lock` |
| T-3 | every early-block reading at horizon h is byte-identical when every session from 2024-01-02 on is replaced (seed 20261947), for h = 63, 126 and 252 -- the per-measure purge (F6) -- with the verdict arm's bound held at its registered constant (N2) |
| T-4 | the held-state rule: it fires only on accounts held at the last close, is re-read at every close, and never fires under P-14's rule; a held account's decision equals the table's four-day leaf, the state otherwise the same; the leaf read trades at every balance of at least $250 with no request the day before, funded and paid; from the policy file, it lists the bands where the four-day leaf equals the five-day leaf, where it rescues a no-trade leaf, and **the two bands where it changes R**; the minimal rescue's mode differs only in those two bands |
| T-5 | `half`: every request is half the maximum and at least $125; a balance below $500 holds; the scaling tier follows the balance after a payout; under the placement on, a Consistency-path account's request is half of its maximum too |
| T-6 | 9.2: the kept windows (every other one; kept windows share no session, adjacent ones share h - 1), n_w, the interval only from 4 kept windows with a spread, the sign count, the zero-series rule, the MDD's formula and its rate of about 80 %; the coverage on overlapping series at one small fixed setting (keys `[20261948, 0, ...]`): the adjacent rule clearly below 0.90 and the separated rule near it, and the second version's independent-means check near 0.90 for the adjacent rule; the declared shapes' zero means. **Its draft-stage form is in this commit** (`tests/test_pp_draft.py`); the build's code is held to the same assertions |
| T-7 | 8.2's oracles on toy campaigns |
| T-8 (`slow`) | 8.1 items 1 to 3 at 4 paths and at 4 starts per configuration and arm, through `identity/pp_identity.py`; the full 500 paths and every start are that script's heavy run (8.1) |
| T-9 | section 11's seeds appear nowhere else in the build's commit; 13.2's literal check |

## 14. Outputs and the run

- **Files:**
  - `results/pp_reading.csv`, with sections `identity`, `oracle`, `mechanics`, `scorecard`, `paired`, `diverge`,
    `coverage` and `beside`;
  - `results/pp_gate.csv`, with the gate rows;
  - `results/pp_menu.csv`, the menu with its flags.

  Each is written with its sidecar manifest through `extended.results.write_result`, carrying:
  - `prereg_id`: the reading's id (unnumbered) and its pinning row;
  - the decision row under which 8.1 items 1 to 3 held, and Q-80's and Q-76's identity rows;
  - the run counts (11; 6 new, 2 references, 3 rule sensitivity; 32 replays and 8 gates beside);
  - every seed, with the retired ones, and the inherited ladder seeds named as Q-17's;
  - every parameter, and the assumptions of section 4;
  - the funded-account class's name (`extended.user_beside.class_parameters`), and Q-76's commit;
  - the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`, and of the two pinned calendars read (section 4);
  - `exploratory=False` for the declared reading, since nothing in it is chosen after a look. Every cell is still
    labelled "described, not carried".
- **The run, in two steps, each from a clean checkout of the same named commit (`scripts/run_clean.py`), under the run
  lock, watched to its end:**
  1. **the identities** (8.1 items 1 to 3): `identity/pp_identity.py`, under the purpose `identity` and its own
     decision row (the reader admits `identity` only from `identity/*.py`, E-026, E-041). Any failure stops the
     reading: the failure protocol applies, and the lead records it;
  2. **the reading**, only after the lead's row records step 1 as held: the runner authorises its engine reads under
     the three purposes of section 5 item 6, checks 8.1 items 4 to 6 on its own replays (any failure stops it), then
     prints the oracles and the mechanics (8.2, 8.3), then the reading.
  - **weight: heavy.** E-010's U1 identity for two configurations peaked near 1.4 GB. Eleven runs' replays on two
    arms, every start, 32 replays beside and six gates add up to several hours at two workers.
  - **a restart or a rerun (E-053).** Each purpose on the line allows one clean run: once a run has read under a
    purpose, the reader refuses any other run under it. A run aborted or restarted, a rerun after an adapter fix, or
    the failure protocol's replication is a further judged read, and needs **`repeat='E-NNN'`**: a decision row naming
    this file, one row for one more run. The lead records every aborted run with its log, and only the first complete
    run under each purpose is read.
- **Waits:**
  - Q-05 holds (E-010);
  - the pinning row;
  - **Q-76 merged**, and its U1 identity with a class (`identity/user_beside_identity.py --funded-cls both`, every
    start) held -- for every replay;
  - **Q-80 held** (E-049) -- for every gate;
  - **Q-44's file on master** (`results/user_beside_starts.csv`) -- for 8.1 item 6;
  - the adapter built with T-1 to T-9, and step 1 held under its row.

  It does not wait for E-015's limits (flags only).

## 15. Open before the pin

**The lead's:**

1. **The name at the pin:** `prereg/RD-nn_payout_policy.md` (E-025 (1)), the DRAFT file removed in the same commit
   (`tests/test_pp_draft.py` asserts exactly one payout-policy declaration under `prereg/`). The second version's item
   here -- that the hash test re-hashed only `prereg/F-` files -- is struck: E-025 (1) widened it to `prereg/RD-`
   files, and E-041 admitted them to the reader.
2. **E-058's text.** This draft cites E-058 (5) as the brief Q-92 states it (windows separated by h starts; the honesty
   check rebuilt on overlapping series). The row was not yet in `DECISIONS.md` when this version was written; if its
   final text differs, the difference is the red team's to read.
3. **The identities' row.** 8.1 items 1 to 3 run from `identity/pp_identity.py` under a row of their own, which the
   reader requires to mention an identity; the row is the lead's, at the build's merge.
4. **Appendix A** (Q-46, queued). Whether and when to run it, and the purpose its reads take (it is not under this
   file's line; `registered_design`, under a row naming P-16, is the nearest the reader has). Its row is its own.

Closed since the second version: the gate adapter (built, Q-47, E-028; its identities 8.1); F11 (read by Q-39, E-034:
unstated, and `half` stays an assumption).

**The operator's:**

1. **The levels of E-015's limits.** Approval is pending; they are flags only and never block.
2. **After the run:** the choice from the menu, if any.

## 16. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*

---

## Appendix A -- A SEPARATE ITEM, EXPLORATORY: checking Stage 2 D-566's buffer reading (the red team's N1)

**Not part of reading PP.** It reads no policy for users, adds nothing to the menu, and is run, if the lead decides, in
its own clean checkout under its own decision row, labelled EXPLORATORY (TASK_QUEUE Q-46). **Heavy under the lock
rule** (E-025 (3): it rebuilds P-16's cell), though small: 20 paths. **It reads no growth, no journey and no P** --
only counts of an engine state. **Its reads** go through `extended/reader.py` under its own row, never under this
file's `Judged-block reads:` line (15, the lead's item 4).

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
