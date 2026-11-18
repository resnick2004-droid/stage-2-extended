# Q-142: the next slate of Topstep model families (k = 14 onward), and what blocks each

A read-only scout's note (2026-11-18). It declares nothing, edits nothing else and recommends an order for the lead.
**No result value is quoted.** The figures here are declared constants (k, levels, cell counts, seeds, hours a plan
or row states), each with its source. No bar file, walk, trade table or result outcome was opened. The only result
files named are named by path, from the rows that record them.

**What was read (2026-11-18):** `CLAUDE.md`; `CHARTER.md`; `DIRECTIVE.md` (Part 6 in full); `STATUS.md`;
`TASK_QUEUE.md`; `DECISIONS.md` E-162 to E-201 in full, plus E-021, E-023, E-028, E-031, E-035, E-036, E-057, E-065,
E-071, E-086, E-094, E-095, E-100, E-133 and E-134; `PARKING_LOT.md`; Stage 2's handoff
`vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` sections 1.2-1.4, 2.6-2.7 and 3.1-4.2; Stage 2's literature review
`vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md` sections 1-5; the scout notes
`docs/research/mechanisms_2026-11-15.md` (sections 2-4), `next_levers_contract_money_2026-11-17.md` (the answer and
ranked list), `composing_an_execution_model_2026-11-16.md` (the answer) and `volatility_drift_2026-11-17.md` (sections 1,
3.1, 5-8); the drafts `prereg/DRAFT_F-B_multifeature.md` (sections 0-4, 10, 11, 17, 18, 22),
`prereg/DRAFT_F-R_resolution.md` (header, 0, 7.3), `prereg/DRAFT_F-02_resting_levels.md` (header, 1, 3, 4, 5.1-5.3, 5.9);
`prereg/F-03_opening_timing.md` (header and headings); the pinned plan `docs/calibration/Q-126_one_sample_plan_2.md`
(header, 2.2, 2.5, 5, 6.2-6.4, 7); the docstrings of `extended/features.py`, `extended/opening_population.py`,
`extended/lift_one_sample2.py`; `.claude/skills/feature-rules/SKILL.md` sections 1-3; `docs/OPERATOR_SETUP.md` item 9;
the local `run.lock`.

---

## The question

The operator asked (2026-11-18) for the main Topstep model research to test several models at once, with workflows
behind it. Nothing has passed: F-01 withdrawn (k = 10 spent, E-007), F-02 retired with k = 11 unspent (E-094), F-03
closed at stage B by Kill B (k = 12 spent, E-192). k = 13 goes to the per-firm execution-protocol family (Q-141, per
the lead's brief; not yet on record in any file read). **What slate of new Topstep model families, from k = 14,
should run in parallel next, and what blocks each?**

## The answer in a few sentences

**Every live candidate for a numbered Topstep family is a direction family, and every direction family's pass line is
the one-sample lift over the coin twin.** That statistic has no validated form: `cons` failed its fresh-seed check
(E-094), Q-108's line failed its validation (E-159), and Q-126's second plan is pinned and built, with its calibration
of about 30 hours queued (E-187, E-195). The two-sample and placebo-selection forms do hold (E-094), but every filter
candidate on record that could use them is closed or has an expected lift near zero:
- F-03 closed at Kill B (E-192);
- family R was not judgeable, and its lift is only the avoided flatten cost (E-028, E-086);
- Stage 2's state-gated coin closed (handoff 3.2, D-582).

**So Q-126 is the critical path for the whole slate. Its calibration should run next, straight after F-03's T-3.**

I recommend three families, drafted in parallel now and pinned in this order once a one-sample line is adopted:
1. **k = 14, RL3:** resting orders at pre-session levels, re-declared from F-02's gatekeeper-approved seventh text.
2. **k = 15, B-ON:** one multi-feature side model on P-16's own overnight offers. This is new; family B dropped
   overnight alerts by scope, not because anything closed them.
3. **k = 16, B-RTH:** family B's sixth version, brought up to date, pinned only if a pre-pin power check shows it can be
   more than a screen.

Two more ideas get no k:
- a late-day thresholded momentum rule: too little supply, so at most a twin inside B-RTH;
- range-scaled brackets: a described reading, after a classification row.

Before Q-126 holds, a family can be drafted, red-teamed and built on synthetic data. It cannot be pinned (E-094
(3)(b)-(c)), so it cannot run stage A or B on the choice block, unless the lead rules a conditional pin. That pin spends
a k on a family that might never be judged, and Q-126 has calibrated only k = 13 to 20 (its section 7 item 5).

---

## 1. The pipeline today

### 1.1 Spent, closed and retired (do not repeat)

| item | state | row | what it closes |
|---|---|---|---|
| F-01 resting-order level atlas | withdrawn, k = 10 spent | E-007 | its text only; levels return only as a new declaration (E-094 (3)(b)) |
| F-02 resting levels (seventh text) | withdrawn before any read; F-02 and k = 11 retired unspent | E-094, E-095 | nothing was read: the idea is unread, and only its C1 statistic failed |
| F-03 opening timing (family O, four states s1, s2, s3, u3 on P-16's 3R funded opening) | closed at stage B by Kill B, k = 12 spent; judged block unread; T-3 owed (running now) | E-192 | side-free persistence-state timing of the funded opening on P-16's overnight offers |
| family R (trailing-month HAR admission of P-16's refused marks) | closed before its pin, no k: every cell dropped by its own power rule | E-086 | the trailing-month admission; E-086 leaves "a shorter-memory admission rule, under a new declaration" open |
| Stage 2's nine lever families and the size fit | closed | handoff 3.1 | purchase budget, entry costs, seats, hours, second firm, Consistency path, flat plans, crippled-account resolution, $100K/$150K |
| Stage 2's OHLC side-rule searches | closed: "gains are schedule, not direction" | handoff 3.2 (D-558, D-580, D-588-D-592, D-275, D-423, D-616, D-617) | single-rule side searches against the coin twin, ORB, fixed brackets, P&F, S2's state-gated coin |
| rare calendar effects; A2-A4 | dropped or parked: too few events | PARKING_LOT; E-021 | pre-ISM/GDP drift, turn of month, FOMC cycle, rebalancing, day after a VIX spike |

### 1.2 Declared, drafted, built or queued

| item | kind | state | what blocks it | row |
|---|---|---|---|---|
| Q-141 | numbered family, k = 13 (per-firm execution protocol) | being taken (the lead's brief) | not on record in the files read | -- |
| `DRAFT_F-B_multifeature.md`, sixth version | numbered family when pinned | parked: its C1 rests on the one-sample statistic (E-094 (3)(c)); its sixth red-team read Q-95 parked (E-101) | Q-126's adoption; a redraft to E-161/E-187 (the band check), k >= 14 (its text says k = 12), Q-122's readings beside | E-051, E-062, E-094, E-161 |
| `DRAFT_F-R_resolution.md`, second version | was to be a numbered family | closed before its pin (E-086); kept on record | a new declaration with a shorter-memory rule; its C1 lift is only the avoided flatten cost (E-028; the draft's 0 and 7.3) | E-086 |
| `DRAFT_F-02_resting_levels.md`, seventh text | the gatekeeper's APPROVE, contingent on Q-55 and Q-83 (E-065); then withdrawn (E-094) | unpinned, its F-number retired | a new declaration whose C1 uses a one-sample line that holds (E-094 (3)(b)) | E-065, E-094 |
| RD-01 to RD-05 | described readings, no k (E-023 (1)) | RD-01, RD-02 built; RD-03 built through cycle 4 with stage 0 stopped; RD-04 pinned; RD-05 pinned, build Q-138 queued | none of these can produce a candidate (E-134 (1)) | E-080, E-082, E-152, E-168, E-200 |
| Q-126, the second one-sample calibration | the pass line's calibration | plan pinned (E-187); build merged (E-195); calibration queued (`python scripts/q126_calibrate.py`, nine parts, `--hours 30 --mem-gb 3`); then a choosing row, a validation run and an adoption row | the heavy queue; memory at the lock | E-187, E-191, E-193, E-195 |
| Q-122 (regime-bucketed and equal-weight-block readings beside `cons`) | the family template's beside list (E-157 (b)) | queued, light | nothing; it should land before the next pin | E-157 |
| Q-133 (`extended/opening_wait.openings` keeps the risk columns) | a defect fix | queued, light | owed before any family reuses F-03's opening path | E-192 |

### 1.3 What gates a judged read: the pass line's state

- **One-sample lift over the coin twin** (E-008's line for any side-choosing family):
  - `cons` FAILS its fresh-seed validation (E-094 (1)).
  - Q-108's `cons_m1.25` FAILS its validation on one exact subset null (E-159, audited E-160). Q-125 diagnosed the
    cause as an aligned-pattern lottery acting through one trade set (E-161).
  - **No one-sample line exists today.**
- **Two-sample and placebo-selection forms** (`extended/lift_bound.py:400` `two_sample_bound`; `:409`
  `placebo_selection_bound`) HOLD (E-094 (1), (3)(d)).
  - They carry K0's fill-intensity check: a cell that is lax on its own counts is killed (E-094 (4), E-052).
  - They lose power on persistent selections (E-071, E-086).
- **Q-126** tries scope D first, then a scope-Q branch with margins of 1.5 or more (plan 2.2).
  - **The statistic a family uses is fixed by the side persistence it declares before its pin** (plan 2.5): below 42
    sessions; 42 to 50; 51 to 62; 63 or more, which gets no one-sample line.
  - The band check holds the family to that declaration from its sides alone.
  - The regime-filter kind is barred until a further row (E-187).
  - The calibrated range is **k = 13 to 20** (plan 7 item 5). After Q-141, that leaves **seven numbered slots
    (14 to 20)** before an extension row.
- **What follows from each Q-126 outcome** (plan 7):
  - NONE at the choice: no one-sample line; families use the two-sample forms with K0, and B and the levels re-draft
    stay parked.
  - A chosen statistic FAILS: its band rows have no line.
  - A third plan is the lead's decision and NEEDS_OPERATOR on the board.
  - A statistic HOLDS: an adoption row pins `extended/lift_one_sample2.py`'s blob, and families may declare C1 on it
    within their band.

### 1.4 What a family can and cannot do before Q-126 holds

| step | before Q-126's adoption row | source |
|---|---|---|
| draft, red-team, gatekeeper's verdict | **yes** | the program's practice (F-02 was approved contingent on calibrations, E-065) |
| build adapters and tests on synthetic data | **yes** (light) | CLAUDE.md; feature-rules |
| extend the feature library, with its shift-invariance tests | **yes** (light, synthetic) | `tests/test_features_lookahead.py`; E-178 |
| state the side persistence from the rule; prove it on synthetic data | **yes** (a rule-based side needs no fit) | plan 2.5; E-035 (6) |
| an outcome-free power check from Q-126's own power table at the family's k and declared supply | **only after the calibration writes `q126_cal_power.csv`** (plan 6.2) | plan 5 |
| **pin** (spends k) | **no**, for any family whose C1 is one-sample, under E-094 (3)(b)-(c) as ruled; a conditional pin needs a lead's row | E-094 |
| stage A/B on the choice block (2020-2023) | **no**: they follow the pin. Stage B itself needs no calibrated statistic (F-03's stage B was an uncalibrated max-T and Kill B, E-095), so the pin is the only block | E-095, E-192 |
| stage C on the judged block (2024-01-02 to 2026-07-16) | **no** | CHARTER 3; plan 7 |
| a filter family judged by placebo-selection | **yes in principle**, since that statistic holds; but no live filter candidate has a mechanism with power (section 2.5) | E-094; E-071; E-086 |

**On a conditional pin.** The text would declare C1 on "the one-sample line a row adopts for this family's declared
band", with stage C refusing until that row exists. It would let stage A/B run during the calibration.
- **Its cost:** in the branch where Q-126 adopts nothing for the family's band, k is spent on a family that can never
  be judged. That is one of the seven calibrated slots.
- **Its gain:** about the length of Q-126's runs. But drafting and red-teaming three families will take that long
  anyway: F-02 took seven texts, family B six, Q-126 six.

**The recommendation:** keep E-094 (3)'s rule for this wave.

---

## 2. Candidate families for k = 14 onward

Every candidate below is on **NQ 1-minute bars 2020-01-02 to 2026-07-16 only**: the choice block 2020-2023, with 2020
as warm-up where a family needs it, and the judged block 2024-01-02 to 2026-07-16. The judged block is **late
development for direction**, not out of sample: Stage 2 read the follow effect there (F-B draft section 2 (a)).

Every candidate keeps CHARTER section 4:
- stops in the stop band, above the 45-tick cost floor;
- at least five minutes from alert to order, by hand; a resting ticket published at least five minutes before it can
  trigger;
- one position at a time per firm, with five minutes flat between trades;
- at most 5 % of trades reaching the 15:10 CT flatten, overall and in every year;
- realised risk within 10 % on at least 90 % of trades;
- no entry before 07:35:00 CT on a BLS 08:30 day, and FOMC days out;
- conduct tier 1 (no hedging, no copying, no maximum size into major news), tier 2 off in the base case, tier 3 priced
  at 0 % denial in the verdict.

The user scorecard is reported beside against R\* = P-14, never as the pass line.

### 2.1 RL3: resting orders at pre-session levels, re-declared (proposed k = 14)

- **The idea in plain words.** Before the US session, place limit orders that fade the prior day's high and low, the
  overnight high and low, the prior close and the nearest round hundreds, plus stop orders that break the round
  hundreds. Each ticket is written at least five minutes before it can fill, so it fills at its level rather than five
  minutes late. The question is whether the side the level implies beats a coin on the same fills.
- **Mechanism, sourced as F-02 sourced it.** Stop-loss cascades and limit-order absorption at visible levels: Osler
  2003, *Journal of Finance*, "Currency orders and exchange rate dynamics"; Osler 2005, *Journal of International
  Money and Finance*, "Stop-loss orders and price cascades in currency markets". These are on FX, not NQ, and
  F-02's text calls the mechanism "untested here" (draft section 1). This note found no later test and did no new search.
- **Why it is not a repeat.**
  - F-02 was withdrawn before anything was built or read (E-094 (3)(b)). Its idea is unread, and only its C1 statistic
    failed.
  - F-01's text (k = 10 spent) is replaced, not re-run.
  - The draft drops `break` at `on` and `pd`: those are long-window breakouts whose follow effect Stage 2 read and
    closed (D-592). It also drops `break` at `pdc` (draft 1, 6.2).
  - Stage 2's level work entered at market after a close beyond the level, five bars late (A1-A4, `pdhl`), or used the
    opening range (ORB5/ORB6, closed). Resting fills at four non-opening-range levels are narrower and new (draft 1).
- **Data.**
  - The bars.
  - The walker's resting entries: `extended/walker.py`, trade-through limits and stop-first ties; its identity holds
    (E-011).
  - The pinned calendars: BLS, FOMC, early closes (E-029), FOMC minutes (E-050).
  - The vendored value map for C2.
  - Stage 2's verified ledger for the scorecard.
- **Which statistic judges it.**
  - **C1:** Q-126's adopted one-sample line for its declared band. A level fill's side is set daily by which level
    trades, so its persistence should fall below 42 sessions, in scope D, the domain Q-126 tries first.
  - **C1':** `two_sample_bound` against the window-matched placebo levels (F-02 5.8; it holds).
  - **C2:** `two_sample_bound` on the routed trades, priced by the value map at the places the routing reaches (F-02
    section 10).
  - K0 and C0 apply; the floors are CHARTER section 3's.
- **Expected cells:** **15 cells** ((4 `fade` kinds + 1 `break` kind) x 3 stops) and **45 signed hypotheses**, as
  F-02's seventh text fixes them (draft 5.9; E-065).
- **Dependencies.**
  - Q-126's adoption row.
  - A narrow redraft: a new F-number and k; C1 renamed to the adopted statistic; the band declaration; new seeds, since
    F-02's are retired with its text; Q-122's readings beside; E-161's drift nulls named beside.
  - A red-team read and the gatekeeper.
  - **A ruling the lead owes before the pin:** F-02's tickets work from 08:30 (draft 4 item 4). Family B's default,
    under D-281 (3), is that no entry lies in 08:30-08:59 (F-B draft 22 item 1). The redraft must say which reading
    governs RL3. F-02's approval (E-065) did not have to face it, because family B's default is that family's own.
- **Choice block before Q-126?** Redraft, red team and the build of anything not already built: yes. Stage A/B: no
  (pin first).
- **Risks, stated in advance.**
  - Fade sides may lean with the trend, since upper levels fill more in a rising market. That presses Q-126's balance
    limit and E-161's drift question. The redraft should declare the side's persistence and balance from the rule, and
    the band check is read on the sides alone.
  - The cascade side is read at round numbers only.

### 2.2 B-ON: one multi-feature side model on P-16's own overnight offers (proposed k = 15)

- **The idea in plain words.** P-16 is the program's registered coin. A fair coin picks long or short every five
  minutes overnight, with a 37.5-point stop. B-ON keeps P-16's offers, brackets and schedule, and lets one pre-registered
  model (a regularised logistic regression on normalised features) choose the side instead of the coin.
  - If it chooses better by enough, the edge is spent where P-16's value map prices it: on every trade (place (a)) and,
    at 3R, on the funded opening (place (c)).
  - This follows DIRECTIVE 6.1 exactly: "Supply comes from a schedule (P-16's 5-minute marks); an edge is a side or a
    filter on those offers."
- **Why it is not a repeat.**
  - No Stage 2 or program work has fitted a joint model on normalised features (F-B draft 2 (b)).
  - Family B dropped "overnight alerts" with the reason "US hours (handoff 3.1)" (F-B draft section 17, the dropped
    table). Handoff 3.1's family 4 is a lever on the *coin's hours*, judged on P. It is not a closure of direction models
    overnight.
  - F-03 used the same population (`extended/opening_population.py:7-9`) for a side-free timing filter. B-ON chooses
    the side, a different question with a different pass line.
  - Stage 2's S1 read fifteen single OHLC side rules on P-16's offers at no delay (D-578, D-580). B-ON must beat the
    three follow rules that survived the per-offer test, read at its own five-minute latency on the same offers (family
    B's conjunctive kill lines C1-f; F-B draft 2 (a)).
  - The European-open drift, the strongest single overnight effect in the literature, is reported dead by its authors
    (Boyarchenko et al. 2026, per the review's rank 5). B-ON does not rely on it.
- **Data.**
  - The bars.
  - P-16's registered schedule: its admitted marks pinned by sha256, entries 17:00-08:25 CT, from 07:40 on report days
    (`extended/opening_population.py:7-13`).
  - P-16's trades identity (E-011).
  - F-03's population and labels code: each offer walked long and short at every table R (`opening_population.py:16-19`).
    The direction value is the half-difference of the two sides, from the same walk.
  - **The feature library extended to overnight marks.** It computes RTH alerts only (`extended/features.py:89`,
    08:30-15:00). Day-level and trailing-window features generalise. `ret_rth`, `pos_rth`, `range_rth`, `d_vwap` and
    `or_*` do not.
  - The value map at base `p16` (the E-181 reader).
- **Which statistic judges it.**
  - C1 and C1-d (drift-matched): Q-126's adopted one-sample line for its declared band.
  - C1-f (against each follow twin): also one-sample, on paired differences, so the same line.
  - C2: `two_sample_bound` on routed trades against twin designs, valued at the places of P-16's value map.
  - K0; the floors; the scorecard beside, compared directly with P-16 (its coin twin is P-16) and P-14 (R\*).
- **Expected cells:** proposed **6** (one stop, P-16's 37.5 points, x R in {1, 1.5, 3} x uses {`side`, `filter`}, in
  family B's form, F-B draft 10). Plus the searched regularisation values, each counted (family B searches 7 lambdas per
  stop and target, F-B draft 18). The drafter fixes the count.
- **Dependencies.**
  - Q-126's adoption row.
  - A new draft built from F-B's sixth version's machinery: the walk-forward with purge and embargo, the side rule,
    B2, the conjoint MDL and the screen rule.
  - The feature extension and its tests, including the 17:00 open, the daily maintenance gap, Sunday opens, a roll and
    DST.
  - Q-133's fix if it reuses `opening_wait`.
  - A red team and the gatekeeper.
  - **A design choice the drafter should make in the text:** cap the multi-day trend features, such as `ret_20d`, or
    show by construction that the model's side cannot be persistent past the band it declares. Otherwise the band check
    can leave the cell "not claimed" at stage C (plan 2.5).
- **Choice block before Q-126?** Draft, red team, the feature extension and the synthetic tests: yes. Fitting and stage
  A/B: no (pin first; fitting is inside the declared walk-forward, E-031 (1)).
- **Stated costs.**
  - P-16 trades overnight, so a user hand-enters orders at night. CHARTER section 2 says the user's time is not
    modelled, and the note says so here.
  - The one-position rule means B-ON's overnight trades and RL3's RTH tickets rarely meet. A composite of the two would
    be a new family (composing note, the answer).

### 2.3 B-RTH: family B's sixth version, brought up to date (proposed k = 16, conditional)

- **The idea in plain words.** The same model on the family's own five-minute schedule from 10:10 to 15:05 CT. Its
  features never read 08:30-08:59, and the funded opening moves to the first offer after 10:10 (F-B draft 0, 3).
- **Why it is not a repeat:** as F-B draft section 2 argues (b, c), with the lead's ruling on the opening-range residual
  (E-036).
- **Data:** the bars; the built feature library (Q-11, E-016); its own per-year resolution cutoff on the choice block
  (D-525 (4)'s rule, kinds only); value-map base `p14` (F-B draft 11).
- **Which statistic:** as B-ON (C1, C1-d, C1-f one-sample on Q-126's line; C2 two-sample; K0).
- **Expected cells:** **12** (2 stops x 3 R x 2 uses), with **28 searched configurations**, so 40 recorded (F-B draft 10,
  18).
- **Dependencies.**
  - Q-126's adoption.
  - A seventh version: k >= 14, the band declaration, the E-161 and E-187 rules, Q-122's readings beside, its own sixth
    read (Q-95) replaced by a read of the new text.
  - **A pre-pin power check.** Its own draft expects the family to be declared a screen before any lift is read (F-B
    draft 0: "likely to be declared a screen"). By the program's memory rule a strict line must show power. A family
    expected to be a screen should not spend one of seven calibrated slots. The check reads Q-126's power table (plan
    5's MDL at the family's k and its declared offers a year) against the value map's bar.
- **Choice block before Q-126?** As B-ON.
- **Why it is below B-ON:** fewer offers; a schedule that is not a registered design's, so the scorecard compares it
  with its own schedule's coin (F-B draft 3); the 25-point cells may be empty at K1; the 12.5-point base is weak (F-B
  draft 3).

### 2.4 LDM: late-day momentum, thresholded (not proposed for a k now)

- **The idea in plain words.** On days with a large move by the early afternoon, take the side of the day's move for the
  last stretch before the flatten. The mechanism is hedgers who must trade with the move: short-gamma dealers and
  leveraged ETFs.
- **Literature** (the review's rank 3, carried; not re-searched here):
  - Gao, Han, Li and Zhou 2018, *JFE*, "Market intraday momentum", on SPY 1993-2013.
  - Baltussen, Da, Lammers and Martens 2021, *JFE*, "Hedging demand and market intraday momentum", on 60+
    futures 1974-2020.
  - Against: Rosa 2022 (*J Futures Markets*) finds the predictability gone out of sample, with a threshold form doing
    better; Ivanov and Lenkey 2018 (*JFM*) find the leveraged-ETF flows economically insignificant.
  - Persistence after publication is mixed.
- **Why it is not a repeat:** the plain form failed (the review section 4, `shortlist_rod_momentum.csv`). The review
  says only the thresholded form on NQ 2020-2026 is untested. That is a narrow gap inside handoff 3.2's closed
  single-rule searches.
- **Data:** the bars only. The mechanism-faithful form needs leveraged-ETF AUM, which is free on issuer sites, history
  depth unverified (the review).
- **Statistic:** Q-126's one-sample line.
- **Expected cells:** at most 4 (12.5- and 25-point stops x R in {1, 1.5}). R = 3 almost surely fails the 15:10
  resolution line from a mark near 14:25. The review names resolution as "the first kill".
- **Dependencies:** Q-126.
- **Why no k now.** At most one signal a session, on threshold days only. Its independent units are the threshold
  sessions of the judged block, and the review's own power estimate for effects of this frequency is a t-statistic near
  2 [the review's estimate] against a one-sided level of 0.05 / 240 or tighter.
- **Better:** declare it inside B-RTH as one more known-effect twin the model must beat on the same offers. That spends
  no k.

### 2.5 Considered and not proposed as numbered families

| idea | why not a numbered family now | what it could be instead |
|---|---|---|
| range-scaled brackets (volatility note section 5) | a coin-sided scaled design's lift over its coin twin is zero by construction; it needs a classification row first (note section 5; its recommendation 4) | a described reading (no k), or the bracket convention of a sided family declared as such |
| a shorter-memory resolution admission (family R's open door, E-086) | its C1 lift is only the avoided flatten cost, much of it Stage 2's flatten convention, while supply cancels against the twin (E-028; F-R draft 0, 7.3) | the supply question as a described reading, as E-028 (2) planned |
| new persistence states for the funded opening | F-03 closed at Kill B on the same population and mechanism; new states chosen after that look are a search after a look | nothing on this block; more history (OPERATOR_SETUP items 7, 8) |
| state-gated coin on every trade | Stage 2's S2 closed it (D-582) | -- |
| `lnbar1x4` followed at five minutes | Stage 2 recorded it "as a lead for unread data" (D-590, D-592); the judged block is not unread for it | a twin in B-ON/B-RTH (as F-B's C1-f), never its own family on this block |
| A2-A4, turn of month, FOMC cycle | too rare at the program's level (E-021; PARKING_LOT) | revisit only with more history |
| a side model used only on the funded openings | the openings' supply is too small to estimate a lift on them alone (handoff 2.7, `section bar`, and its supply cap); the right form is to estimate on every offer and spend at (c), which B-ON's C2 already does | inside B-ON |

### 2.6 The slate in one table

| | RL3 | B-ON | B-RTH | LDM |
|---|---|---|---|---|
| proposed k | 14 | 15 | 16 (after a power check) | none now (a twin in B-RTH) |
| side source | the level's rule | a fitted model | a fitted model | the day's move |
| population | four pre-session levels, resting, from 08:30 | P-16's overnight offers (17:00-08:25 CT) | its own 10:10-15:05 schedule | 14:25-ish marks on threshold days |
| one-sample C1 (Q-126) | yes, band expected < 42 | yes, band set by design | yes | yes |
| two-sample lines (holding now) | C1', C2 | C2 | C2 | C2 |
| cells | 15 (45 signed) | ~6 + searched | 12 + 28 searched | <= 4 |
| where the value lands | the routed places | every trade and (c) at 3R, base `p16` | the routed places, base `p14` | every trade |
| text ready | near (seventh text approved, E-065) | new draft | seventh version | -- |
| choice block before Q-126 | no (pin first) | no | no | -- |

---

## 3. What is shared, built once

| shared piece | state | who builds it | used by |
|---|---|---|---|
| **Q-126's adopted one-sample line** and its band check (sides only) | built (`extended/lift_one_sample2.py`, E-195), awaiting its runs and adoption | wt-verify (runs under the lock) | RL3, B-ON, B-RTH |
| **two-sample forms and K0** | held (E-094); K0 forms in F-02's text and F-03's build | -- | all, on C1' and C2 |
| **B2's conditional critical values**, the **conjoint MDL** and the **screen rule** | written separately in family B's draft (12, 8 item 8) and in F-03's build | wt-verify: one module, its level and power tests on toys (E-051's rule) | B-ON, B-RTH, RL3 |
| **a pre-pin power gate** (Q-126's MDL table at the family's k and declared supply, against the value map's bar) | not built | wt-verify, light, after the calibration writes its power file | every family, before it spends a k |
| **the walker** (market and resting entries, stop-first, trade-through limits) | built, identity holds (E-011) | -- | all |
| **P-16's overnight population and labels at every R** | built for F-03 (`extended/opening_population.py`) | wt-features adds the direction value (half-difference) | B-ON |
| **the feature library**, extended to overnight slots, with its shift-invariance tests | RTH only (`extended/features.py:89`) | wt-features | B-ON (and B-RTH unchanged) |
| **a walk-forward splitter** with purge and embargo longer than the longest trade | declared in F-B draft 9, not built | wt-features | B-ON, B-RTH |
| **the follow twins** (Stage 2's three surviving follow rules, read at five minutes, on the family's own offers) | declared in F-B draft 13, not built | wt-features | B-ON, B-RTH, and LDM as a twin |
| **the place recorder and the value-map reader** | built, identities held (E-055, E-130, E-138, E-181); Q-133's risk-column fix owed | wt-lit (Q-133) | C2 of every family |
| **Q-122's regime-bucketed and equal-weight-block readings beside `cons`** | queued, light (E-157) | wt-verify | every new declaration's beside list |
| **a repository family template** encoding E-031, E-035 (6), E-052, E-094 (3), E-161, E-187's band and bar, E-157 (b) and the power gate | not built | wt-scout, light | every draft (fewer red-team cycles) |
| the reader's seal, read ledger, clean runs, results writer, licence guard, identity covers and tokens | built | -- | all |
| the user scorecard beside (Q-17's adapter; Q-139's second version) | built; second version queued (E-201) | wt-user | all |

---

## 4. The order I recommend, and why

1. **Now (the lock): F-03's T-3 finishes.** It holds the lock (`run.lock`, job `f03-t3`).
2. **Next heavy: Q-126's calibration, moved ahead of every other waiting heavy job.**
   - It is the only heavy item that gates numbered families: RL3, B-ON, B-RTH, and Q-141 too if its line is one-sample.
   - Every other waiting heavy item gates a described reading or an identity: the second breakeven reading (E-194), RD-02's
     identity (E-201), Q-98, Q-22b, Q-46, Q-121c, Q-18b's run. Those readings cannot produce a candidate (E-023 (1),
     E-134 (1)).
   - The calibration takes about a day and a half of lock. The plan estimates about 25 hours at eight candidates (plan
     6.2), and E-195 queued it at 30 hours.
   - During those hours the lead runs the slate's light work in parallel (step 3).
   - **The shorter heavy readings go in the gap after the calibration**, while the lead writes the choosing row (light)
     and before the validation run.
3. **In parallel, light, while the calibration runs:**
   - (a) RL3's narrow redraft and the lead's D-281 (3) ruling for it (wt-levels).
   - (b) B-ON's first draft and the overnight feature extension with its tests (wt-features).
   - (c) B-RTH's seventh version, which may be deferred if workers are short (wt-scout).
   - (d) the shared B2/MDL/power-gate module and Q-122 (wt-verify).
   - (e) the family template (wt-scout).
   - (f) Q-133 (wt-lit).
   - The red team reads each draft as it lands.
4. **The choosing row, then Q-126's validation run (heavy), then the adoption row.**
5. **The power gate for each drafted family** (light; reads the calibration's power file, not an outcome). A family whose
   MDL at its k is far above the lift worth its declared bar is closed before its pin, taking no k, as family R was
   (E-086).
6. **Pins, in the order of readiness and expected power:** RL3 at k = 14, B-ON at k = 15, then B-RTH at k = 16 only if
   it clears the gate.
   - The level tightens from 0.05/210 (k = 14) to 0.05/272 (k = 16), a small change in the critical value. So readiness
     decides more than k does.
   - The family with the most power and the clearest value route should still take the smallest k if the two are close.
7. **The heavy chain per family, one at a time, in k order:** A0 (its identity), then run 1 (stage A/B on the choice
   block), then the audit, then run 2 (stage C, the campaign and the scorecard) only if Kill B passes.
   - A family killed at stage B costs one heavy run and its k.
   - Light builds of the next family run beside the current one's heavy run.

**If Q-126 adopts nothing for a band** (plan 7 items 1-2):
- RL3 could still decide by C1' (two-sample against placebo levels, which holds). That asks a level-against-placebo
  question rather than E-008's coin-twin question, so it needs a lead's classification row before it is used.
- B-ON and B-RTH have no deciding C1 and stay unpinned.
- A third plan is NEEDS_OPERATOR (plan 7 item 3).
- The one lever that raises power for every family is more history. That is the operator's call (OPERATOR_SETUP items
  7, 8; QuantConnect is free but needs their credentials, Databento is a purchase), and per the volatility note section 6
  it helps scaled-bracket designs most.

---

## 5. Machine limits

- **16 GB, one heavy run at a time under `run.lock`, about 3 GB a run** (CLAUDE.md). Threads: `OMP_NUM_THREADS` at most
  2, at most 2 worker processes in a heavy job.
- **Memory is the practical blocker for Q-126's calibration.**
  - E-195 queued it at `--mem-gb 3`. The plan measured Q-108's working set far lower and proposed 1.5 (plan 6.2).
  - `run.lock` records about 2 GB available when T-3 started.
  - `scripts/run_lock.py take` refuses a job the machine cannot hold (STATUS, Machine), so the 3 GB declaration may wait
    for memory.
  - Two remedies, the lead's call: the operator's item 9 (close idle applications before leaving the machine), or the
    declared memory reset to the build's measured peak under a row, as the plan's 6.2 allows for hours.
- **The slate's heavy units:** for each family, A0, run 1 and run 2, at most three runs, serialised, each under about
  3 GB. Feature matrices are tens to a few hundred MB even overnight, small next to the walks. Features are computed
  inside each family's run 1 and run 2, from the bars through the reader. No separate pre-pin pass over the bars is
  needed.
- **Light work is many-at-once:** drafts, red teams, builds and synthetic tests on up to the worktrees available
  (wt-levels, wt-features, wt-verify, wt-scout, wt-lit are idle or near it, per STATUS). Light tests stay off the real
  bars while a job holds the lock (Q-118, Q-134).

---

## 6. What is unknown, and how it could be found

| unknown | how it could be found |
|---|---|
| whether Q-126 adopts a line, and for which bands | its calibration, choice row and validation (heavy, queued) |
| each family's MDL at its k against its value bar | the power gate (light) from `results/q126_cal_power.csv` once written (plan 6.2) and the family's declared supply |
| RL3's side persistence and balance (trend-leaning fades) | declared from the rule in the redraft; measured at stage A on the choice block's sides (outcome-free) after the pin; the band check at stage C |
| whether B-ON's model side stays inside a band < 42 sessions | by construction in the draft (feature windows capped); the band check on fold sides after the pin |
| where P-14's and P-16's funded openings fall by mark and hour | `results/q35_openings.csv` (E-100), a supply count not opened here; the drafter of B-ON reads it as a supply count for the value route |
| why family B's drafts kept to US hours beyond "handoff 3.1" | not on record in what I read; the lead may ask the drafter of the seventh version |
| Q-141's statistic (one-sample or not) and its slot contention with the slate | Q-141's declaration, when written |
| whether the sequenced merge of Q-115/Q-136 into `config/` between Q-126's calibration and validation disturbs the validation's provenance assertion | the lead checks the validation's blob pins (E-193, E-195) before merging `config/` in that gap |
| how the D-281 (3) default applies to resting fills from 08:30 | the lead's ruling in RL3's redraft (F-02 4 item 4 against F-B 22 item 1) |

---

## 7. What each family would need to declare (the house form, briefly)

For each of RL3, B-ON and B-RTH, before its pin:
- **mechanism** and sources (above);
- **prior exposure** (the F-B draft section 2 form, plus F-03's population for B-ON);
- **supply:** offers per session and per block from the schedule and the admitted marks, counted before any outcome;
- **side persistence and band** (plan 2.5), with the balance limit;
- **fill intensity** (E-052) and **K0**;
- the CHARTER section 4 table, item by item;
- the blocks and the seal;
- the reads line (E-026);
- the cells and every searched value, counted;
- seeds, unique on every ref;
- C1, C1', C1-d, C1-f, C2 and the floors at 0.05 / (k (k + 1));
- B2, the conjoint MDL, the screen rule and the **power gate**;
- the regime and equal-weight readings beside (Q-122);
- the scorecard beside against P-14 (and P-16 for B-ON);
- the confirmation window declared (NQ from 2026-07-17, a purchase, never read until a carried candidate is registered);
- **what a fail means.**

---

## 8. Proposed TASK_QUEUE lines (for the lead; this note edits nothing)

- `Q-1xx | Move Q-126's calibration (Q-126g's run) to the head of the heavy queue after F-03's T-3; the second breakeven reading, RD-02's identity and the other readings into the gap before Q-126's validation; the declared memory checked against the machine (OPERATOR_SETUP item 9 or a row resetting --mem-gb to the build's measured peak) | lead | queued | E-195 | heavy | Q-142`
- `Q-1xx | RL3: a new resting-levels declaration from F-02's approved seventh text -- new F-number, k, seeds, C1 on Q-126's adopted line by declared band, C1' and C2 two-sample, Q-122 beside, the lead's D-281 (3) ruling for fills from 08:30; red team, gatekeeper; pinned only after Q-126's adoption row and the power gate | wt-levels | queued | E-065, E-094, E-187 | light | Q-142`
- `Q-1xx | B-ON: draft one multi-feature side model on P-16's overnight offers (F-03's population; family B's machinery; the three follow twins; side persistence declared by construction); extend extended/features.py to overnight slots with shift-invariance tests (synthetic only); red team; pinned only after Q-126's adoption row and the power gate | wt-features | queued | E-094, E-187 | light | Q-142`
- `Q-1xx | Shared: one module for B2's conditional critical values, the conjoint MDL, the screen rule and a pre-pin power gate reading Q-126's power file, with level and power on toys (E-051); a repository family template carrying E-031, E-035 (6), E-052, E-094 (3), E-157 (b), E-161, E-187; Q-122 before the next pin | wt-verify, wt-scout | queued | E-157, E-187 | light | Q-142`
- B-RTH's seventh version: queue it behind the power gate's first result. LDM goes only as a twin inside B-RTH.

---

## Sources (all read 2026-11-18)

- **Program files:** `CHARTER.md` sections 1-5; `DIRECTIVE.md` Part 6; `STATUS.md`; `TASK_QUEUE.md`; `PARKING_LOT.md`;
  `docs/OPERATOR_SETUP.md` items 7-9; `run.lock` (local, git-ignored).
- **Decision rows:** `DECISIONS.md` E-021, E-023, E-028, E-031, E-035, E-036, E-057, E-065, E-071, E-086, E-094, E-095,
  E-100, E-133, E-134, E-157, E-159-E-161, E-185-E-201.
- **Stage 2:** `vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` sections 1.2-1.4, 2.6-2.7, 3.1-4.2;
  `vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md` sections 1-5 (the citations in 2.1 and 2.4 are that
  review's and F-02's, carried and not re-searched).
- **Calibration and declarations:** `docs/calibration/Q-126_one_sample_plan_2.md` header, 2.2, 2.5, 5, 6.2-6.4, 7;
  `prereg/DRAFT_F-B_multifeature.md` 0-4, 10, 11, 17, 18, 22; `prereg/DRAFT_F-R_resolution.md` header, 0, 7.3;
  `prereg/DRAFT_F-02_resting_levels.md` header, 1, 3, 4, 5.1-5.3, 5.9; `prereg/F-03_opening_timing.md` header.
- **Code:** `extended/features.py:86-89, 604`; `extended/opening_population.py:1-25`; `extended/lift_bound.py:48, 400,
  409`; `extended/lift_one_sample2.py:1-15`; `.claude/skills/feature-rules/SKILL.md`.
- **Scout notes:** `docs/research/mechanisms_2026-11-15.md` 2-4; `docs/research/next_levers_contract_money_2026-11-17.md`;
  `docs/research/composing_an_execution_model_2026-11-16.md`; `docs/research/volatility_drift_2026-11-17.md` 1, 3.1, 5-8.
