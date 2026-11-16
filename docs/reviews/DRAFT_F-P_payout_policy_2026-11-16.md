# Red team: `prereg/DRAFT_F-P_payout_policy.md` (family PP, payout policy in a user's first months), 2026-11-16

The red team, read-only, in worktree `wt-payout` (branch `wt/wt-payout` at b221ce3). **Target:** the draft as committed
(784 lines; not pinned, not numbered). **Read against:** `CHARTER.md` sections 2-4; `DECISIONS.md` E-001..E-018;
`CLAUDE.md`; `.claude/skills/prereg-discipline` and `contract-engine`; `docs/audits/phase0/B_objective.md` (Q3) and the
other tracks where cited; `docs/reviews/phase0_red_team_2026-11-15.md`; the brief `docs/briefs/Q-25_2026-11-15.md`. In
the vendored tree: `config/rules.yaml` (`xfa_mll_start`, `xfa_lock_at`, `xfa_std_*`, `payout_min`,
`payout_max_frac_of_balance`, `profit_split`); `propedge/campaign/lockstep.py` (`FundedAccount`, the day loop, the
router hand-off); `propedge/campaign/risk_policy.py`; `propedge/campaign/shared_days.py` (routing rules);
`propedge/research/u_select.py` (`block`); `scripts/customer_slices.py` (`engine_args`, `replay`);
`docs/USER_MILESTONES.md`; the handoff sections 2.5 and 3; `prereg/P-14_a3-brk30-cb20.md` (its data period);
`results/state_policy_v12_noclose_policies.json` (the table every cell uses); Stage 2 D-564, D-565, D-566, D-654.

**What I ran** (session scratchpad, one small process at a time, one BLAS thread; code in Appendix A): a walk of the
vendored table file (a registered configuration, not an outcome: the drafter read it too); `skew_null.py`,
`skew_null_pass.py` and `flip_shape.py`, synthetic block-mean nulls with no data. **Not done:** no read of
`data/bars` or `data/atlas`, no engine run, no result file of any payout cell, no web, nothing written but this note.

**On the briefs.** Mine asks four questions and states no answer. The Q-25 brief the draft was written from does
state one -- "A payout policy changes no trade ... That makes a paired comparison ... far more powerful" -- and the
draft repeats it (lines 37-41, 452-454). I ignored that assertion and tested it (finding F2).

**Master has moved** since b221ce3 (ede4843, rows to E-022). I read its new rows only for bearing: E-021 (1) says the
pass line chosen for F-P will be proposed together with the one for side-keeping filters (A1, B1) and asked of the
operator once (Q-36). So this family's pass line becomes a precedent; that raises the stakes of F1-F3.

**Severity:** CHANGES-A-CONCLUSION (CAC), MATERIAL (MAT), MINOR, NOTE. Figures marked *synthetic* are red-team
arithmetic on simulated data and decide nothing. Figures marked *table* are counts of leaves in the vendored policy file.

---

## Verdict

**Must be redrafted.** A revised draft is due anyway for the [Q-16] marks and the operator's pass line; these changes
belong in it. Nothing here is a reason to abandon the family.

- **One declared gate does the opposite of its job (CAC, F1).** Section 7.3's null check sign-flips the choice block's
  own paired series. A payout lever has no sign symmetry under its null, so the check cannot see the shape that makes a
  test falsely carry. Worse, at this level it is inverted: it stops the family when the choice block shows a
  consistent effect and passes it when the series holds one large loss cluster.
- **The draft's case for PL-1 overstates what a calibrated paired test can reach here (MAT, F2).** No distribution-free
  test can reach the family's level on the judged block's nine windows at all. A parametric one can, but only for a
  difference of roughly twice its window-to-window spread. The audit's own same-trades figures put that at 7-11 points
  of P, three to five times the largest gain any of Stage 2's 66 cells reached.
- **PL-2 as written has a look-ahead into the pick, the wrong block length, about four independent windows, and no
  guard on what it costs users later (MAT, F3).** Section 9.3 says nothing else in the file changes with the choice;
  for PL-2 that is false.
- **The held-state rule is a declared design choice, small in reach beyond a pure rescue, and should be labelled as one
  (MINOR, F5).** "Same trades" does give a real pairing, but on start days and offers, not on executed trades (F10).
- **The draft's doubt about Stage 2 D-566 holds** on the engine's code and the table's leaves (N1). It bears on the
  $1,000 and $2,000 buffer cells, not on the half requests.

## Answers to the four questions

1. **Does "same trades" yield a paired comparison?** Yes, as a matched pair: the same start day, the same offered
   entries, and the same outcome of each offer at each R. The difference then has a well-defined mean over start days,
   and the market path's luck is shared. It is **not** a pairing of executed trades. After the first binding event the
   table resizes the account, the router (longest-waiting order, the strict one-position rule) hands later offers to
   different accounts, and the purchase budget and seats shift. That is the same kind of divergence as Stage 2's
   same-trades cells (P-16's 4-seat, 5 + 1 and funded-cap cells, P-14's purchase rule). Their paired SEs were 0.012 to
   0.027, against 0.051 between designs (`B_objective.md` lines 302-310). So the draft's "far more powerful" is right
   *relatively* (3-4 times less noise). It is wrong as an argument that the test can carry a realistic payout effect
   (F2). Section 5.4 states the divergence correctly; sections 0 and 7.3 do not (F10).
2. **Is the held-state rule a hidden design choice?** It is a design choice, declared and argued but classed "FIXED,
   no fitted value". It is not neutral, and it is not the only reading of "the table's own" leaf. In the region where
   `lock` holds accounts, it equals the table where the table trades in 24 of 35 bands. It replaces a no-trade leaf in
   9, and changes R where the table's own five-day leaf trades in 2 (*table*). So it is nearly the minimal rescue. In
   the 9 rescued bands, though, any choice is a sizing design. The four-day leaf was solved for "a win today pays
   tonight", which is false for a held account. A carried pick would be "the lever plus this sizing" and must be
   registered as such (F5).
3. **The three pass lines.**
   - **PL-1 is sound in form** (the paired P test, the guards at D-621 (3)(ii)'s tolerances, P-16's direction, E-008's
     floors). Two things block it: its calibration check is broken (F1), and its power is limited (F2). Even once fixed,
     it would let through only a payout lever that moves P by about 7-11 points.
   - **PL-2 is unsound as written** (F3). Its line needs six months, so a 126-session purge and blocks, and it has about
     four independent windows. With the guards it drops, it would let through a policy that makes the path more even
     while costing users months 6 and 12, S3c and the unlucky tenth by any amount.
   - **PL-3 is sound**, lets nothing through, and should not spend a program family number (F4).
   - **Can a calibrated paired test have power here?** Not for effects of the size Stage 2 ever saw. A sign-flip or
     permutation test cannot reach 0.05/132 on 9 blocks: its smallest p is 2^-9, about 0.00195, five times the level,
     and it needs 12 blocks. A t on 9 batch means needs t >= 5.27 (k = 11; 5.41 at k = 12, 5.54 at k = 13). Its tail
     at that level rests on assumptions the data cannot check: the phase-0 red team found it 1.6 times its level on a
     structural null, and a skewed null of the kind a payout lever makes sends it to about 100-1,200 times (*synthetic*,
     F1). A holding lever's gain, if any, should show at months 6-12, where the judged block has about 4 and 2
     independent windows.
4. **The doubt about D-566.** It is well founded (N1). Under `keep_balance` K, an eligible paid account whose balance
   is between $500 and K + $125 asks nothing (the request is capped at B - K and dropped below $125). It then meets the
   paid phase's five-day leaf, which is no-trade at every balance band from $500 (*table*: 22 of 22). Its state is
   frozen, so it sits until the funded horizon. D-566 (2)'s own words, "takes fewer trades a session", fit this. It does
   not touch D-566 (3) (half requests without a buffer), which cannot meet the leaf.

---

## 1. Findings

| id | sev | finding (short) | remedy |
|---|---|---|---|
| F1 | **CAC** | 7.3's sign-flip null check symmetrises the observed series, so it is blind to the skewed nulls a payout lever produces. At this level it is inverted: it fails a consistent series (16 of 32,768 patterns reject vs 12.4 allowed) and passes a loss-cluster series (0), the shape on which a 9-block t falsely carries 4-45 % of the time (*synthetic*). It is also run at 15 blocks for a test made on 9 | replace with nulls that keep asymmetry and the judged block's block count (below); state now that no distribution-free test reaches the level on 9 blocks; fix the decision when nulls disagree |
| F2 | MAT | Power: on the judged block, randomization tests cannot reach the level (2^-9 > 0.05/132); a 9-batch t needs t >= 5.27; audit B's same-trades SEs give a calibrated MDD of about 0.07-0.11 in P, 3-5 times the largest P gain of Stage 2's 66 cells (+0.021). Sections 0 and 9.1 present PL-1 as able to carry what a between-design test could not, without these numbers | put the arithmetic (cited, not typed from memory) in 7.3 and 9.3 before the operator chooses; say what PL-1 is expected to return |
| F3 | MAT | PL-2: (i) its line reads months 1-6, but the choice-block purge is 63 sessions (4.3), so stage B reads 2024 sessions for the last 63 starts of 2023, and T-3 must fail; (ii) 7.3's 63-start blocks are half its dependence; (iii) about 4 non-overlapping 126-start windows on the judged block (t critical 14.19 on 3 df); (iv) it drops PL-1's (b), so months 6 and 12, S3c, S5a and S1 are unguarded; (v) (b') is a 0.05 component, stated nowhere | if PL-2 stays: per-measure purge, 126-start blocks, PL-1's (b) added, (b')'s level stated, its MDD shown before the choice; strike "Nothing else in this file changes" (line 506) |
| F4 | MINOR | Under PL-3 the family can carry nothing yet takes the next program family number (lines 20-21, 663-664), tightening F-02's and F-B's levels to 0.05/156 or 0.05/182 | under PL-3, a reading under its own row, unnumbered (E-001 (a)'s precedent: the size fit and the value map); the gatekeeper's call |
| F5 | MINOR | The held-state rule (5.3; 6.1 line 300) is a sizing choice classed FIXED with no alternatives named. *Table:* in `lock`'s held region it changes the leaf in 11 of 35 bands (9 no-trade rescued, 2 R changed where the table's own leaf trades). It reaches the lost-opening, recovering accounts, which hold most pre-payout account-days (handoff 2.5) | label it a design choice; name the alternatives (minimal rescue, the zero-day leaf); a carried pick registers it; report held sessions by class (unchanged / rescued / R changed); T-4 lists the 2 changed bands |
| F6 | MINOR | 4.3 says "Program U's families did not purge". They did: `u_select.block` drops, per reading, every early start within that reading's horizon of 2023's last start (`propedge/research/u_select.py:266-283`, D-621 (4)(b); the phase-0 red team checked it, review lines 533-534). The draft's single 63-session purge leaves the choice section's S4a, S4b, S5b and S5c readings reading 2024+ | adopt `u_select.block(records, EARLY, h)` per measure (h = 63, 126, 252); correct the sentence |
| F7 | MINOR | 16.1: `lock` by overriding `_standard_eligible` makes the engine's `last_eligible`, and so the daily recorder's `eligible` column, the policy's eligibility (`lockstep.py:801, 812, 1864`). 16.1 line 691 requires the firm's, and the held rule needs the firm's at the close | say how both hold (e.g. the firm's eligibility kept in its own field and restored after `trade_day`); test it in T-2 and T-4 |
| F8 | MINOR | 7.3's replication count is "written in the planning section" (line 400), i.e. after the choice-block series exist; on 15 blocks a sign-flip null is exactly enumerable (2^15) | fix counts and seeds in the file now; enumerate where exact |
| F9 | MINOR | PL-1 and PL-2 put a user measure in the pass line, which CHARTER section 3 and E-008 forbid in terms ("never as the pass line") | the operator's choice is a charter amendment: a new E-row and CHARTER sha256, not only one paragraph in 9.2 |
| F10 | MINOR | "A payout policy changes no trade" (line 37) and "mostly zero, with clusters where one account's payout differed" (lines 395-396): executed sizes, R, allocation, purchases and fees diverge after the first binding event and stay diverged; `half` binds on every payout | reword as 5.4 does; T-6's synthetic null includes persistent divergence and a skewed, lumpy P difference, not only sparse clusters |
| F11 | MINOR | `half` needs "a request may be any amount between $125 and the maximum". The ledger quotes "Max Payout per request" and "Minimum Payout" (`rules.yaml` lines 409-430), not that sentence | list it under "Assumed" (section 3) or have the rules-verifier read the request form's amount field (8284233) |
| N1 | NOTE | The D-566 doubt (18 item 4) holds on code and table; Stage 2 recorded the same artefact for Consistency accounts (D-654 (3), (9): "which did more is not measured"); 6.2's drop of `keep_balance` partly leans on D-566 | the experiment specified in 2.N1; 6.2 keeps its other two reasons |
| N2 | NOTE | The verdict arm shifts every R to P-14's registered bound, estimated on 2020-01-01..2026-07-16 (`P-14_a3-brk30-cb20.md` lines 30, 184), judged block included; T-3 cannot see it (a constant) | disclose in 2 and 4; it moves both arms of every pair alike |
| N3 | NOTE | PL-1 (c) on P-16: `half` on P-16 was read in D-564's journey over both blocks; (c) can only kill, so it stays sound | already disclosed in 2; keep |
| N4 | NOTE | P (months 1-3) is the window where both levers mechanically cost most (handoff 1.2; lines 114-116); a holding lever's gain, if any, should show at months 6-12, which PL-1 reads only as guards | say so beside the pass-line question |
| N5 | NOTE | Stage B's studentised pick and 7.3's t are undefined on a cell whose choice-block difference is zero on most blocks (0/0) | a declared rule for zero-variance series (void if zero on every block is already there) |
| N6 | NOTE | The hypothesis paraphrase "the remaining balance becomes the loss floor" (line 59) follows 8284204's own words ("effective loss floor"); the engine sets the floor to $0 (`lockstep.py:832`) | "the remaining balance is all that can be lost" |

---

## 2. The detail per finding

### F1 (CAC): 7.3's null check cannot see the null that matters, and at this level it is inverted

**The text** (lines 394-404). For each new P-14 cell, the choice block's per-start paired difference is sign-flipped
by non-overlapping 63-start blocks, and the rejection rate of Q-16's statistic must not exceed the level. If it does,
the family stops.

**Why it does not test what it says.** Q-16 calibrates the lift over the coin twin with sign-flip nulls
(TASK_QUEUE line 35). That is valid there because, with no direction, a trade's side is a coin: the null *is* a sign
symmetry. A payout lever has no such symmetry. It is a deterministic transformation of the path, and its null ("the
mean difference over start days is zero") says nothing about the shape of the difference. The levers' mechanics
predict an asymmetric shape:

- frequent, same-signed, mechanical effects (`half` cuts every payout; `lock` delays first payouts);
- rare, large effects of the other sign (an account saved from, or lost to, a breach with its balance still in it).

Sign-flipping the observed series replaces that shape with a symmetric one, exactly the property it is meant to check.

**Synthetic check** (`skew_null.py`, Appendix A). Model each 63-start block's mean as +g + e with probability 1 - p,
and -g(1-p)/p + e with probability p (mean exactly zero), e ~ N(0, s^2). The test is a one-sided t on 9 block means at
0.05/132.

| g | p | s | true false-carry rate, 9 blocks (x level) | 7.3's check on a 15-block realised series: median rate; passes on |
|---|---|---|---|---|
| 0.01 | 0.10 | 0.0025 | 0.388 (x1,025) | 0; 386 of 500 |
| 0.01 | 0.10 | 0.005 | 0.276 (x730) | 0; 391 of 500 |
| 0.01 | 0.10 | 0.01 | 0.037 (x99) | 0; 427 of 500 |
| 0.01 | 0.05 | 0.005 | 0.449 (x1,184) | 0; 265 of 500 |

The mirror shape (rare large gain) never rejects: the one-sided test is conservative there, and anti-conservative
under a rare large loss.

**It is inverted** (`flip_shape.py`, exact over all 2^15 patterns). With the t at 0.05/132 on 15 blocks, the level
allows 12.4 rejecting patterns:

- a series of equal block means (a consistent effect) has **16** rejecting patterns: 4.9e-4 > 3.79e-4, so the check
  **fails** and the family stops;
- 14 equal blocks and one block nine times larger (a loss cluster) has **0**, so the check **passes**.

The check therefore stops the family on the safe shape and waves through the dangerous one. The failures in the table
above are the realised series with no loss block, which "look good".

**Two more defects.**

- The check runs at the choice block's ~15 blocks. The judged test runs on ~9, and calibration at 15 says little about
  the tail at 9.
- Fixed non-overlapping blocks drop the positive correlation between neighbouring blocks: the last starts of block i
  read the sessions of block i + 1's first starts. So the null is less dependent than the data.

**The failure it allows.** Under PL-1 (or PL-2), a lever whose judged-block series is a run of small gains with no loss
cluster passes 7.3 and carries at the family's level, though its true mean difference is zero or negative.

**Remedy (before the pin).**

1. State in 7.3 that a sign-flip or permutation test cannot reach the level on the judged block (F2). So the deciding
   statistic is parametric or bootstrap, and its size at 0.05/(k(k+1)) is an assumption about the tail.
2. Calibrate on nulls that keep asymmetry and the judged block's count:
   - resample whole centred 63-start blocks of the choice-block series, 9 at a time with replacement;
   - the phase-0 red team's structural null (review lines 150-152);
   - a skewed, lumpy synthetic null as above, in T-6 at 9 blocks.
3. Write now what happens when they disagree (the family stops), and the replication counts and seeds (F8).

If no statistic passes all three at 9 blocks, the family is "not judgeable at this level", which is 7.3's own words.

### F2 (MAT): what a calibrated paired test can reach on this block

**The arithmetic, knowable before any read.**

- **Blocks.** The judged block holds about 9.4 non-overlapping 63-start blocks (`B_objective.md` line 275; the draft's
  4.5).
- **Randomization tests.** A sign-flip or permutation test on 9 blocks has a smallest p of 2^-9, about 1.95e-3. The
  level is 3.79e-4 at k = 11, 3.21e-4 at k = 12 and 2.75e-4 at k = 13. Reaching it needs 12 blocks (2^-12, about
  2.4e-4), which the judged block does not hold.
- **A t on 9 batch means (df 8).** Critical values are 5.27, 5.41 and 5.54 for k = 11, 12 and 13 (*synthetic*
  arithmetic). With 80 % power the minimum detectable mean is about 2 block standard deviations.
- **What that means in P.** Audit B's same-trades pairs give paired SEs of 0.012-0.019 and a calibrated MDD of about
  0.07-0.11 (`B_objective.md` lines 307-310). The phase-0 red team gives "Same-trade variants of P-14 ... a calibrated
  MDD of about 0.09" (review line 197).
- **Against what has been seen.** The largest P gain over P-14 among Stage 2's 66 cells is +0.021, on all starts
  (`B_objective.md` lines 320-322).
- **The batch-means t is not at its level either:** 1.6 times nominal on the structural null (review lines 154-158,
  175-177).

**What the draft says.** "That paired comparison is far more powerful" (lines 39-41), and "A paired P test can then
carry an effect that a between-design test could not see" (line 454). Both are true relative to the between-design MDD
of 0.31-0.34. Neither tells the operator the absolute MDD before they choose a pass line. Section 7.3 computes it only
after the cells run (lines 407-409).

**The failure it allows.** No false result. The risk is a pass line chosen on a power claim that does not hold: under
PL-1 the family most likely closes at C with "no payout policy ... moved P by more than the MDD". PL-3 records the same
fact without spending anything.

**Remedy.** Put these figures, by citation, in 7.3 and 9.3. In the question to the operator, say that PL-1 is expected
to close unless a lever moves P by about 7-11 points.

### F3 (MAT): PL-2 as written

1. **Look-ahead into the pick.** PL-2's line is "each start's share of its first six months with a positive net
   change" (lines 478-481), a 126-session reading. Stage B chooses on it (line 427). The choice block keeps starts
   whose 63rd session is on or before 2023-12-29 (lines 189-191). So each of the last 63 starts of 2023 reads up to 63
   sessions of 2024 into the measure that picks the cell. T-3 (line 714), if built on the PL-2 measure, fails. If it is
   not, the leak is silent.
2. **Block length.** 7.3's null uses 63-start blocks (line 397). The PL-2 measure's dependence is about 126 starts.
3. **Power.** About 4 non-overlapping 126-start windows fit in the judged block's 126-session-horizon starts. The t
   critical value on 3 df at 0.05/132 is 14.19 (*synthetic* arithmetic), and a randomization test's smallest p is 1/16.
4. **No guards.** PL-2 keeps (c) and (d) but not PL-1's (b) (line 484). A cell that makes more months positive while
   paying less in total (S3c), leaving fewer users ahead at months 6 and 12 (S4a, S4b), or deepening the unlucky
   tenth's month-3 loss (S5a) carries as long as (b') holds. Yet the draft's own reason for (b) is "A share ahead
   early, bought by losing months 6 and 12 ... is not a gain for the user" (lines 466-467).
5. **(b')** is a one-sided 0.05 test inside an intersection. A cell truly worse on P by more than five points passes it
   up to 5 % of the time. That is acceptable for a guard, but it should be written.

**Remedy.** If the operator wants PL-2, make it a different family text, not one paragraph:

- the per-measure purge (F6);
- 126-start blocks in 7.3;
- PL-1's (b) added;
- (b')'s level stated;
- its MDD shown before the choice.

Strike "Nothing else in this file changes with the choice" (lines 506-507).

### F4 (MINOR): PL-3 should not take a program family number

Under PL-3 "no cell can carry" (line 490). A family with no carry rule spends none of its allocation of the program's
5 %. Numbering it buys no protection and moves every later family to a stricter level: F-02 and F-B, and the timing
families E-021 queues. E-001 (a)'s precedent is the account-size fit and the value map: "readings, no family".

Remedy: under PL-3 the file is a reading under its own row, with every block it reads recorded as read for payout
policy on P-14. Section 12's binding (a later payout family is judged only on data this one did not read) applies
unchanged.

### F5 (MINOR): the held-state rule is a sizing choice

**Verified claims.** The table keys only on balance, cushion, request day, winning days and (paid) line gap, as the
draft says (line 247). `risk_policy.account_state` reads the account's own `win_days` (`risk_policy.py:348`), and
`Tiers` takes the last tier at or below the value (lines 113-120). So winning days of 6 or more read the five-day leaf.
A no-trade session leaves B, F, winning days and profit since the payout unchanged (`lockstep.py:703-799`), so an
eligible account at a no-trade leaf sits for good, as the draft says. The four-day leaf trades in every request-day-0
band from $250, funded and paid (*table*), as 5.3 claims.

**What the rule changes** (*table*; funded phase, request day 0):

| region | (balance, cushion) bands | five-day = four-day leaf | five-day no-trade (rescued) | five-day trades, R differs |
|---|---|---|---|---|
| all balances >= $250 | 51 | 24 | 25 | 2 |
| `lock`'s held region ($250 <= B < $2,000; floor below $0) | 35 | 24 | 9 | 2 |

- **The 2 changed bands:** B in [$250, $500) with cushion in [$250, $500), where 1.0R replaces 1.5R; and B in
  [$500, $750) with cushion in [$750, $1,000), where 1.5R replaces 2.0R. Risk is the same in both.
- **The 9 rescued bands** are the lowest cushion band at each balance band from $500: accounts whose loss limit had
  trailed to within $250 of $0 and fell back.
- **Paid phase:** the five-day leaves at line gap > 0 are no-trade at all 22 bands from $500, and equal the four-day
  leaf in the 2 bands below. `half`'s held region is [$250, $500), so the rule changes nothing there but what it rescues.
- **Reach.** The accounts `lock` holds are mainly the lost-opening accounts that live and recover. The handoff's U2
  rows (`HANDOFF ... 2026-11-15.md` lines 178-183) show them holding most pre-payout account-days. So the rule may
  carry many of the `lock` cell's sessions.

**Why it is a choice.** In the rescued bands the table's own decision is "do not trade". Any trading leaf put there is
a sizing design. The draft's leaf is a reasonable one: one day short, and usually the more conservative leaf. But it
was solved for a continuation ("a winning day tonight triggers the payout and hardens the floor") that `lock` and
`half` deny.

**Remedy.**

- Class it "fixed, a design choice" in 6.1, with the alternatives named and why they were not taken: the minimal rescue
  (the table's own five-day leaf where it trades, the four-day leaf only where it is no-trade); the zero-day leaf.
- Say that a carried pick registers the rule with the lever.
- Report per cell the share of held account-sessions in each class.
- Have T-4 list the two R-changed bands from the file.

### F6 (MINOR): Program U did purge, per horizon

`u_select.block` (`propedge/research/u_select.py:266-283`) keeps an early start only if
`start_day <= last - h and observed >= h`, with h the reading's horizon. The phase-0 red team confirmed that no start
straddles the boundary (review lines 533-534). With day 0 the purchase evening (`USER_MILESTONES.md` line 10), the
draft's "63rd session on or before 2023-12-29" equals `block(..., EARLY, 63)`. So 4.3 is the house rule for P, not an
interpretation.

The house rule is per measure, though. The choice section's "every cell's choice-block readings" (line 433) include
S4a and S4b (126 and 252 sessions) and S5b and S5c (126). Under a single 63-session purge those read 2024+ sessions
before the judged read, and T-3 ("every planning output ... byte-identical", line 714) fails on them.

Remedy: use `block(records, EARLY, h)` per measure. That also removes F3 (1).

### F7 (MINOR): the `lock` seam contradicts its own requirement

`FundedAccount.trade_day` sets `eligible = self._standard_eligible(rules)` and `self.last_eligible = bool(eligible)`
(`lockstep.py:801, 812`). The daily recorder writes `"eligible": bool(a.last_eligible)` (line 1864). Overriding
`_standard_eligible` (16.1, line 689) therefore records the *policy's* eligibility, while line 691 requires the
*firm's*. The held-state rule, and the 7.4 count of held sessions, need the firm's at every close. This is a build
detail, but the file names the seam, so it should name how both hold.

### F8 (MINOR): fix 7.3's counts now

"The count is written in the planning section" (line 400). If that happens after the choice-block series exist, the
count is a free choice made after seeing data. With 15 blocks a sign-flip null is exactly enumerable (32,768 patterns),
so no Monte Carlo count is needed. For resampling nulls (F1's remedy), fix the count and the seed in section 14.

### F9 (MINOR): PL-1 and PL-2 amend the charter

CHARTER section 3 and E-008: "The user scorecard is reported beside every judgement, never as the pass line." Either
PL-1 or PL-2 makes a user measure the pass line for a class of levers. E-021 (1) on master already treats it as a
class (A1, B1, F-P). That is a charter row with a new sha256, which the draft's "replaces section 9.2 by one paragraph"
(line 506) understates.

### F10 (MINOR): what is paired, stated exactly

Section 5.4 (lines 277-289) is right. Sections 0 (line 37: "A payout policy changes no trade") and 7.3 (lines
395-396) are not. Once an account's state diverges, the table resizes it, and through the longest-waiting router
(`shared_days.py:54-69`; the strict one-position rule) the next offers go elsewhere. Purchases (20 in 21 sessions) and
seats then follow.

For P the per-start difference is nonzero only where a month's "ahead" flips, so it is lumpy. It is not confined to
"one account's payout", and for `half`, which binds on every payout, it is dense. T-6's "sparse differences" model
(line 717) should include persistent divergence and the skewed shape of F1.

### F11 (MINOR): the amount of a request

The ledger has "Max Payout per request: 50% of your account balance up to the cap" and "Minimum Payout: $125"
(`rules.yaml` lines 409-430). That a request may be any amount between them is an inference, though a natural one, and
D-564 made it too. It is not in section 3's table or its "Assumed" list (lines 154-158).

### N1: the D-566 doubt, checked on code and table

- **The request.** `request = payout_frac * min(0.5 B, cap)`, then `min(request, max(B - keep_balance, 0))`, and
  nothing is asked below $125 (`lockstep.py:813-818`). For K = $1,000 a paid account with B in [$500, $1,125) asks
  nothing; for K = $2,000, B in [$500, $2,125).
- **The leaf.** Such an account is eligible (five winning days, profit since the payout), and its five-day leaf at
  line gap > 0 is no-trade at every balance band from $500 (*table*: 22 of 22). Its state cannot move, so it sits
  until the funded horizon: 504 sessions in the gate (`lockstep.py:1251`), never in the U1 replay
  (`customer_slices.py:204`). Unpaid accounts meet the funded phase's lowest-cushion five-day no-trade leaves (25 of
  105 at request day 0, D-654 (9)'s "a quarter").
- **Stage 2's own record.** D-564 (2) named that "a buffer changes the balances [the paid leaves] see", and left the
  table unsolved for it. D-566 (2) reads the $2,000 buffer as "takes fewer trades a session (more balance held means
  fewer accounts recycled)". Stage 2 found the same lock for Consistency accounts and wrote "which did more is not
  measured" (D-654 (9)).
- **Half requests alone** (D-566 (3)) cannot meet it: they ask from $500, and the five-day leaves below $500 trade.
- **Bearing here.** Section 6.2 drops `keep_balance` partly because "Stage 2 read it on P-16 (D-566)". That reason is
  weakened; the other two (the lump direction, long held stretches) stand.
- **The experiment** (exploratory, its own row; light).
  - Rerun D-564's four buffer cells (K = $1,000 and $2,000, `payout_frac` 1.0 and 0.5) on P-16's cell at seed 20261131
    with the daily recorder on, for 20 paths.
  - Count the funded account-days that are eligible, unpaid, and at a no-trade leaf, by cell.
  - The cost is minutes and well under 1 GB.
  - If the count is material, rerun those cells with this family's held-state rule at 500 paths (heavy: one run under
    the lock, about an hour) and read growth beside D-566's rows.

### N2-N6

- **N2.** P-14's bounds use its whole in-sample window (`P-14_a3-brk30-cb20.md` lines 30, 184). The verdict arm's
  shift on choice-block runs is therefore a function of 2024-2026. It is common to both arms of every pair, inherited
  from program U, and invisible to T-3. Disclose it.
- **N3.** Already disclosed (line 99).
- **N4.** The operator should hear it: PL-1 judges a holding lever on the window where it costs most by construction.
- **N5.** Write the rule for a zero-variance series.
- **N6.** Wording only.

---

## 3. Recommendation among PL-1, PL-2 and PL-3 (for the operator, in plain words)

**My recommendation: PL-3, "describe only", recorded as a reading rather than a numbered family.**

- **Why not a pass/fail line at all.** A payout policy is not a claim of an edge. It is a choice a user makes and can
  change at any time, and it adds no trades. The program's pass line exists to stop the program from believing an
  edge that is luck. Here the risk is different: recommending a way of withdrawing that does not help, at the cost of
  some cash timing.
- **What PL-1 would most likely say.** The program's bar for this family is a false-alarm chance of about 1 in 2,600.
  The 2024-2026 data hold only about nine independent three-month stretches. On those, a fair test can clear that bar
  only if a payout policy changes the share of users ahead by about 7 to 11 points. That is three to five times more
  than any of Stage 2's 66 variants ever moved it. And the benefit of keeping money in the account, if there is one,
  should show at six to twelve months, where there are only about two to four independent stretches. So PL-1 would
  almost surely end "not shown", whatever the truth. Its present safety check is also broken (F1): as written it could
  let a lucky run through.
- **What is wrong with PL-2.** As written it peeks at 2024 when it picks the policy. It has too little data at six
  months to pass anything. And it would let through a policy that makes the months more even while leaving users
  poorer at six and twelve months.
- **What PL-3 gives you.** For each policy and each month: how many users it helps, how many it hurts, by how much,
  and how much "ahead" each step of evenness costs. That is the trade-off you asked for (E-014, E-015). It costs the
  program's error budget nothing (so F-02 and family B keep their levels) and it cannot produce a false "carried".
- **If a policy then looks clearly better,** it can be tested once on new data (NQ from July 2026, a purchase that is
  yours to decide).

**If you want a payout policy to be able to become a registered candidate,** choose PL-1, but only after the redraft
fixes its safety check (F1), and expect it to close.

---

## 4. What I tried that found nothing

- **Look-ahead in the levers and the rule.**
  - `lock`'s condition is the account's own floor at a close (`lockstep.py:784`: `F = min(0, max(F, B - 2000))`).
  - `half` is the engine's own `payout_frac` (line 814).
  - The held state is read at the session's start from the last close; the request is after 5:00 PM CT (D-175).
  - None reads a later bar or a later outcome.
  - The U1 replay draws nothing and runs in historical order (`customer_slices.py:254-263`).
- **The contract arithmetic.** The lock at $2,000, the floor to $0 at any payout, the 50 % and $2,000 caps, the $125
  minimum, the 90 % split, the five $150 days with the request day excluded, and the first payout exempt from the
  profit condition all match `rules.yaml` (8284204, 8284233) and the engine (`lockstep.py:784-852`). `half`'s
  $500-balance threshold is the engine's arithmetic, as D-565 (1) also says.
- **The reference never fires the rule.** Under P-14's rule an eligible account with a $125 request is always paid at
  that close, so no P-14 account starts a session eligible and unpaid above $250. The draft's 7.1 item 4 checks it on
  every start.
- **Levels.** 0.05/132, 0.05/156 and 0.05/182 are k(k+1) for k = 11, 12 and 13.
- **Multiplicity.**
  - One cell is judged.
  - Stage B is on a purged choice block and spends nothing.
  - PL-1's (b) and (c) are conditions in an intersection.
  - The P-16 cells are never judged.
  - The scorecard bounds are reported, not lines.
  - Section 12 binds a later payout family to unread data, so the family cannot be re-declared to escape its close.
  - I found no alpha spent twice.
- **Seeds.** `grep -rIow` for `2026194[0-9]` over this worktree finds only the brief, this draft and E-018. `git grep`
  over every branch adds master's redrafted F-B (line 613), which lists "20261940-49 (Q-25)" as a reservation, not a
  use.
- **The table claims in 5.3** (the four-day leaf trades wherever a held account can be; the no-trade leaves of D-654
  (3) and (9)) re-derive from the file (*table*).
- **The funded opening** (balance $0, cushion >= $2,000, day 0: $2,000 at 3R) does not void `lock`. The opening's
  realised risk is $1,000-1,500 (handoff line 170), so a lost opening leaves the account alive below its lock.
- **Conduct.** A payout request is not a trade and copies nothing; hand entry is unaffected; the denial ladder is
  beside, per cell.

## 5. What I could not check

- Q-16's statistic (not merged on b221ce3 or on master's E-022), so F1 and F2 are argued for the two classes it could
  be (randomization; parametric or bootstrap).
- How often each lever binds on P-14's trades, the share of held sessions by class (F5), and how dense the per-start
  difference is (F10). All three need the planning runs.
- Whether Stage 2's `rc150_payout_screen.csv` shows the sit (not vendored; N1's experiment would).
- The request form's amount field (F11; needs the web, through the rules-verifier).

---

## Appendix A: the scripts (session scratchpad; re-runnable, no data)

`skew_null.py`:

```python
import itertools
import numpy as np
from scipy import stats

ALPHA = 0.05 / 132
rng = np.random.default_rng(20261999)   # red-team scratch seed, not a family seed

def tstat(x):
    x = np.asarray(x, float)
    sd = x.std(ddof=1, axis=-1)
    return x.mean(axis=-1) / (sd / np.sqrt(x.shape[-1]))

def draw(n_rep, B, g, p, s):
    loss = rng.random((n_rep, B)) < p
    base = np.where(loss, -g * (1 - p) / p, g)
    return base + rng.normal(0.0, s, (n_rep, B))

crit9 = stats.t.ppf(1 - ALPHA, 8)
crit15 = stats.t.ppf(1 - ALPHA, 14)
signs = np.array(list(itertools.product([-1.0, 1.0], repeat=15)))
for g, p, s in [(0.01, 0.10, 0.0025), (0.01, 0.10, 0.005), (0.01, 0.10, 0.01),
                (0.02, 0.10, 0.005), (0.01, 0.20, 0.0025), (0.01, 0.05, 0.005)]:
    x = draw(400_000, 9, g, p, s)
    rate = float(np.mean(tstat(x) > crit9))
    flips = [float(np.mean(tstat(signs * draw(1, 15, g, p, s)[0]) > crit15)) for _ in range(200)]
    print(g, p, s, rate, rate / ALPHA, np.median(flips), max(flips))
x = -draw(400_000, 9, 0.01, 0.10, 0.005)
print("mirror", float(np.mean(tstat(x) > crit9)))
```

Output: t critical 5.27 (df 8) and 4.28 (df 14). Rates at 9 blocks were 0.3881, 0.2764, 0.0374, 0.3872, 0.1342 and
0.4485 for the six settings. 7.3's median sign-flip rate was 0 in every setting but (0.01, 0.20, 0.0025), where it was
9.2e-5. The mirror case gave 0.0.

`skew_null_pass.py`: the same model, seed 20261998, 500 realised 15-block series per setting, counting those whose
exact sign-flip rate is at or below the level. Results: 386, 391, 427 and 265 of 500 for the four settings in F1's table.

`flip_shape.py`:

```python
import itertools
import numpy as np
from scipy import stats
ALPHA = 0.05 / 132
crit = stats.t.ppf(1 - ALPHA, 14)
S = np.array(list(itertools.product([-1.0, 1.0], repeat=15)))
def rate(x):
    y = S * np.asarray(x, float)
    t = y.mean(1) / (y.std(ddof=1, axis=1) / np.sqrt(15))
    return float(np.mean(t > crit)), int(np.sum(t > crit))
print(rate(np.ones(15)))            # (0.00048828125, 16)
print(rate([1.0] * 14 + [9.0]))     # (0.0, 0)
```

The table walk: load `vendor/stage2/results/state_policy_v12_noclose_policies.json`, key
`state_dp_e-0.050_lamstar_noclose`, `root`. The funded node is tiers on balance, then cushion, then `request_day`, then
`win_days`; the paid node adds `line_gap`. Pick a tier as `Tiers.decide` does (the last `from` at or below the value),
and compare the leaf at `win_days` 4 with the leaf at 5 (a leaf with `max_trades` 0 is no-trade), at `request_day` 0
and, for paid, `line_gap` 0.01.
