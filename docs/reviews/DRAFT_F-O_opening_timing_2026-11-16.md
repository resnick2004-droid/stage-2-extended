# Red team, first read: `prereg/DRAFT_F-O_opening_timing.md` (family O), 2026-11-16

**Target.** `prereg/DRAFT_F-O_opening_timing.md` and `tests/test_family_o_persistence.py`, as committed at a39a80a and
merged into master at 975fd91. I read them in worktree `wt-lit` at b3b1671, which had a clean tree.

**Read against.**
- `CHARTER.md` as amended by E-008, E-014, E-015 and E-023.
- `DECISIONS.md` E-001..E-038, in particular E-007 (d), E-021, E-023, E-028 (2), E-030, E-031, E-034, E-035 and E-036.
- `CLAUDE.md` and `.claude/skills/feature-rules/SKILL.md`.
- The scout's note, `docs/research/mechanisms_2026-11-15.md` sections 3.1 and 5.1.
- Q-16's code and notes: `extended/lift_bound.py` and `docs/research/calibration_2026-11-15.md` (sections 1.3, 2.4, 6.2 and 7).
- `extended/reader.py`, `extended/gate.py` and `extended/features.py`.
- From Stage 2's vendored engine:
  - `propedge/campaign/sizing.py` lines 366-509;
  - `shared_days.py` lines 1-445 and 700-720;
  - `lockstep.py` (`FundedAccount`) and `gate.py` (`_GateDraws`);
  - `propedge/research/atlas_local.py`, `fast_walk.py`, `fv3_rung_walk.py` (the entry bar) and `resolved_coin.py`;
  - `u_value_map.py` (its header);
  - `DECISIONS.md` D-281, D-522, D-525, D-533, D-581 and D-582;
  - `data/README.md` section 5.

**What the brief held.** The brief listed places to attack: the states and their rolling thirds, the twin's population and strata, persistence against Q-16, the value at place (c), the seam, the 07:40 start, and choices made after a look. It stated no expected answer. I treated the draft's own claims as claims to test, not as priors.

**What I ran.**
- Nothing I ran read a bar, the atlas, a walk, a result value or NQ from 2026-07-17. I did not run the engine or use the web.
- I ran `tests/test_family_o_persistence.py`: 14 passed.
- I ran five small synthetic checks in one process at a time, with seeds fixed before each run (777001-777010; the Appendix gives each check). They are exploratory and select nothing.

## Verdict: **must be redrafted**

Several parts are sound and should stay:
- **The clock.** No state reads an unclosed bar. The entry convention checks out in code, and the population's last entry (08:25:00) is outside 08:30-09:00.
- **The selection procedure.** Stage B spends nothing and one cell is judged. The reads line, the seeds and the 2020 warm-up check.
- **The twin's estimand.** The exact-expectation twin is the form Q-16 calibrated.

Four material defects change declared rules:
- **F1.** The pass line's statistic is not the one the program adopted.
- **F2.** The wait is measured on a calendar that destroys the states' persistence.
- **F3.** The value line credits the routing's own selection to the state.
- **F4.** Each cell's persistence class and its power must be stated before the pin, and they are not.

None is CHANGES-A-CONCLUSION, because nothing has been read and so nothing has been concluded. But F2 can by itself reverse a declared kill (K5), and F3 can by itself reverse a pass line (C2).

| id | severity | finding (one line) |
|---|---|---|
| F1 | MATERIAL | C1 and C2 are not on Q-16's adopted form (E-035 (2): `cons` through `placebo_selection_bound`, treated-cluster df). The draft's default is its own 63-session block-mean t on raw in-state session sums. Q-16's function is unstratified, its calibration covers coin-side outcomes rather than this side-symmetric value, and "the larger of its and B2's" is undefined for a three-member intersection |
| F2 | MATERIAL | Stage A's counts, K5, V_B (the pick) and V (C2) run on the gate's day table, which draws every calendar day independently (`SharedDayTable`). A daily state's runs are destroyed, so the fallback share that K5 kills on is roughly the same whatever the state's persistence |
| F3 | MATERIAL | V prices each opening against its stratum's mean over all offers, not against the twin design's openings. Under the one-position rule, the offer a waiting account can reach depends on earlier trades' exits, so V is not zero without a state, and B2's C2 null assumes it is. Fallback openings at non-population marks have no stratum mean |
| F4 | MATERIAL | E-035 (6) and calibration 7.3 require each cell's persistence class to be stated, and its power read from Table 9, before the pin. The draft defers power to stage A and still waits on a merged Q-16, not on Q-55's clean rerun |
| m1 | MINOR | The "17:30 first defined mark" gives the reason that LRS needs 15 bars, but 15 bars exist at the 17:20 mark |
| m2 | MINOR | Fallback openings and every non-opening trade keep P-16's report-day 07:35:00 entry, which E-007 (d) and CHARTER section 4 exclude. The comparison is not biased, but the carried design would not meet section 4 as amended |
| m3 | MINOR | A fast state (s1, u3) can show a positive lift from Stage 2's conservative flatten price alone; family R's drafter expected u3's whole lift to be that. A u3 pass would then be carried against its own stated sign |
| m4 | MINOR | The seam can be realised, but A1's two refusing identities (state always on; W = 0) cannot detect a dead gate or a wrong (h, j) to (date, mark) lookup |
| m5 | MINOR | Section 3 says Q-39 "decides" the ISM/GDP hold, but E-034 already decided it. The scorecard's "not modelled" note lacks the unstated news rules that E-034 requires there |
| m6 | MINOR | B2's slow-component amplitude comes from 2021-2023 only. E-036 M3-1's precedent applies: the judged block's slow component may be larger |
| m7 | MINOR | T-10 has no level, no replication count and no failure rule. At the family's level it cannot be checked with a 1,000,000-replicate inner loop |
| m8 | MINOR | "About a third by construction" (6.4, 5.4) holds only on iid series. For a persistent state the per-year share varies widely, which weakens the W = 5 rationale and K1 for s3 |
| n1-n8 | NOTE | Readings: E-036 answers the open question on H and IV; E-035 answers the twin's form; the 1R mirror claim; x3's frame and T-2's cuts; V is gross of the wait's cost; Q-35's ordering; A4's open default; how V converts R |

---

## Findings

### F1 (MATERIAL) -- the pass line is not on the statistic E-035 adopted, and the adopted one does not fit this estimand as it stands

**Where.**
- Header, line 16: "It cannot be pinned before Q-16 is merged".
- Line 34, the pass line.
- 7.2, lines 515-516: "The session series: z_s = the sum over the cell's in-state offers on session s of (c_i − mu_g(i)) ... The judging statistic tests this series".
- 11 item 1, lines 693-695: "Student-t on **63-session block means** of the line's per-session values ... Q-16's statistic is used if it is merged in this form".
- 12, lines 727-729 (C1) and 736-737 (C2).
- 8, line 575.

**Evidence.**
- Q-16 is merged (E-035, wt/wt-verify 3837256). E-035 (2) adopts, for E-023's placebo-selection twin, "`cons` on a two-sample difference with a treated-cluster df (`placebo_selection_bound`...)". The calibration note's Table 8b holds `cons` on all 55 selection nulls, and every single member fails on whole-session selections.
- Q-16 was not merged "in this form", so the draft's conditional (line 694) leaves its own statistic in force. That statistic is a block-mean t on the raw in-state sums z_s.
  - It is neither a member of `cons` nor `cons`.
  - It repeats the form that calibration note 1.3 corrected for F-02: "the raw `z_s` carry each session's fill count, and a variance of them is not D's".
- `placebo_selection_bound` (`extended/lift_bound.py` 409-419) compares the selected offers' mean with **every** offer's mean. It has no strata.
  - **Check 1** (Appendix): a persistent selection whose share differs by year, under a null with year-level means. Passing the raw c to the function gives a biased estimate. Passing c − mu_g removes the bias and is conservative at 5 %.
  - So the input form decides the estimand, and the draft does not say which input it uses.
- Q-16's selection nulls (calibration 2.4, lines 169-176) use "the coin side's own win at 1R, and net R at 3R" of P-16's judged offers. This family's outcome is the side-symmetric c_i = (l_i + r_i) / 2 (5.3), which differs from that series in two ways:
  - it has the coin's direction noise removed;
  - its main slow part is the volatility-driven mix of exit kinds (1 (v) (c)).

  So its dependence is not in the class Q-16 calibrated, and the calibration's own caveat applies (7.4 item 1: "A level is only as good as the null class").
- "At the larger of its critical value and B2's" (lines 34, 729, 736-737) is defined for one t statistic. `cons` is three (t21w, t42w and t63w, each with its own treated df), so the rule has no meaning as written.
- C2's V is a weighted sum. `placebo_selection_bound` does not take weights, and calibration 7.4 item 10 lists "the value-map price at the bound" as not calibrated.

**What it allows.**
- **If pinned as written:** C1 and C2 would be judged by a statistic that the program has found to have no calibrated level. On a whole-session state such as s3, the single 63-session member is lax at the family level (Table 8b's session row).
- **If filled with a bare name:** `placebo_selection_bound(c, ...)` on the raw c credits the state with the strata composition the twin is meant to cancel. For example, a state that fires mostly in a year whose stratum means are high shows a lift with no selection effect at all.
- **B2 as the only protection:** the line then rests on B2 alone, whose slow component is the declared one (m6).

**Remedy (a declared rule).**
- Name the statistic: `extended.lift_bound.placebo_selection_bound(y = c_i − mu_g(i), session, selected, n_sessions, level=0.05/(k(k+1)))` at `SHIPPED = "cons"` and `DIFF_DF_RULE = "treated"`, with the module and the merge commit.
- Strata: state that they enter by passing deviations, with every population offer as sample 2. Check 1 supports this form. Alternatively, extend the module to per-stratum weights 1[i in state] − n_Fg/n_g and test it.
- Drop 7.2's z_s as the variance's series.
- Define B2's floor per member. B2 simulates each member's statistic, with its treated df, on its replicates, and each member's lower bound is taken at the larger of its t critical value and its B2 quantile. `cons` passes only if all three pass.
- C2: either take its bound from B2 alone, stated as uncalibrated by Q-16, or add the weighted form to Q-16's calibration first.
- Add a synthetic null with c_i-like dependence to T-10 (m7) or to Q-55's rerun: the side-symmetric 3R value of P-16's judged offers, under a persistent selection independent of it.

### F2 (MATERIAL) -- the wait is read on independently resampled days

**Where.**
- 5.5, lines 343-353: stage A's record from "P-16's own engine call ... 200 paths".
- 9: A2 (lines 618-620) and A7/K5 (lines 641-643).
- 10 item 4, the pick by V_B (lines 673-676).
- 12, C2 (lines 730-738): "500 paths, the bound arm".
- 9 A9's u_c (lines 654-655).
- 7.1 and 5.4's W rationale (lines 324-328, 502-505).

**Evidence.**
- Stage 2's gate and its re-composition, `extended.gate.run_gate`, build each path's days with `SharedDayDraws`. The table is chosen in `shared_days.py` lines 714-718:
  - with `mean_block` None, the default in `extended/gate.py` (148, 211-217) and in the vendored `_GateDraws` (66-76), it is `SharedDayTable`;
  - `SharedDayTable` (lines 78-101) gives every calendar day "its own uniform draw".
- `mean_block` is "beside a verdict, never the gate" (D-663; `extended/gate.py` 309).
- So in every campaign the draft uses for the wait, an account's five live sessions are five independent historical days. Each day carries its historical state, but the states' run structure across days, which 5.4, 7.1 and 11 rely on, is gone.
- **Check 2** (Appendix): a daily state firing on a third of days.
  - With independent days, the fallback share at W = 5 is about (2/3)^5 whatever the persistence.
  - In history's order, with mean in-state runs of 5 to 50 sessions, it is several times larger and passes one half from runs of about ten sessions.
- K5 kills a cell above one half, so on the campaign K5 cannot see the persistence that decides it.

**What it allows.**
- **K5 inverted.** A daily-regime cell (s3, and u3 through its daily terms) passes K5 on the campaign while most real openings in history's order would be fallbacks. So the cell would be "not the declared rule", the state of affairs K5 exists to kill.
- **V and V_B overstated.** They over-weight in-state openings relative to fallbacks. With deviations near zero at fallbacks, V is too large for persistent cells, and the stage-B pick favours them.
- **u_c, and so the screen rule, distorted.** A9 takes u_c (the in-state openings a year) from the same campaign.
- **What a user would feel.** The scorecard's U1 replay (history's order) is the only place the real wait appears, and it is beside.

**Remedy (a declared rule).**
- Read A2, K5, the waits, V_B and V on a calendar that keeps history's order. Either:
  - (a) the U1 replay's starts through Q-17's adapter, with each opening weighted by the starts it falls in; or
  - (b) `run_gate(..., mean_block=M)`, with M declared now (for example 63, or infinity from uniform starts), since D-663's verification covers rotation, P-16's mode.
- Keep the independent-day gate only for A1's identities and floor (iii).
- Cost: one more paired set of campaigns per block (P-16, each cell's design and twin design: 200 paths on the choice block, 500 on the judged), hours at two workers.
- State which calendar each reading uses.

### F3 (MATERIAL) -- V (C2, and stage B's pick) is not differenced against the twin at the openings

**Where.**
- 7.4, lines 533-542: "z_s^V = sum over the openings j ... mean_dv(c) x ( c_i(j) − mu_g(i(j)) ) / (1 + 3) ...; fallbacks included at their own offers' deviations".
- 11 item 2: C2's B2 null "with the judged campaign's routing weights held fixed", re-centred so that "the twin's expectation is zero exactly".
- 10 item 4.

**Evidence.**
- `TradeRouter.begin_day` refuses an offer "while any account holds a position or within this many minutes of one closing" (`shared_days.py` 357-360). It holds each routed position "to its exit at the account's R" (369-370, 388-389), and it hands a trade to the oldest-stamped account that can take it (361-381).
- A new account is stamped as of its first day (284), so accounts that traded before it go first.
- So the offer at which a waiting account opens is selected by when earlier trades on the same night resolved. That is a function of the night's path, and so of its volatility, its kind mix and its persistence.
- The deviation c_i − mu_g at a reached offer is then not mean-zero even for P-16, which has no state. The twin design's openings carry the same selection.
- B2's C2 null fixes the routing weights and resamples the deviations from other sessions, which breaks exactly this dependence, so it centres V at zero where the true no-state V is not zero.
- **Check 5** (a toy: an earlier trade holds the slot until it resolves at a speed set by the night's volatility, and the only value is the flatten-cost mix). The routing deviation at reached offers is non-zero, and its sign and size depend on the volatility spread. That is enough to show the null is not centred. On real data it also carries whatever persistence goes with fast nights, which is the family's own mechanism.
- Fallbacks may open at P-16 marks outside the population: 08:30-09:00 (5.2, line 292) and the report-day 07:35 mark (line 286). There, c_i and mu_g are not defined (5.3 builds them for population offers only), so V's formula is incomplete.

**What it allows.**
- C2 passes or fails on the router's own selection, which would also appear for P-16 or for the twin design.
- Stage B picks the cell whose waits happen to sit on favourable reach, not the cell whose state selects.

**Remedy (a declared rule).**
- The value line: V_line = V(design) − V(twin design), on the paired campaigns, from F2's order-keeping calendar.
  - Each term uses its own openings, fallbacks included.
  - Average the twin over several seeded draws if one draw's noise binds; name the seeds now in 20261982's tree.
  - B2 for C2 then simulates the difference with both sets of routing weights held fixed.
- Beside: V(P-16), the base's own routing deviation, so its size is seen; and V(design) undifferenced.
- Fallbacks: define mu_g at every P-16 mark (both sides at 3R, the population builder extended to 08:30-09:00 and the report-day 07:35 mark, as labels only). Alternatively, set a fallback's deviation to zero by rule.
- This also answers the drafter's question (20, second red-team bullet): C1 on every in-state offer is the test of the state, and the value line belongs on the openings, **differenced against the twin's openings**. C1 on openings alone would lose power for no gain in validity.

### F4 (MATERIAL) -- each cell's persistence, and its power, must be on the file before the pin

**Where.**
- 9 A9 (lines 648-657): power computed in stage A, after the pin.
- 20 item 1: the prerequisite named is "Q-16 merged".
- 11's "Why" (lines 685-691) describes the clustering in words only.

**Evidence.**
- E-035 (6): "families with persistent filters must state the persistence before their pin (a quarter-long regime filter cannot reach power on this block)".
- Calibration 7.3 (lines 770-775): "a family declaring a side-keeping filter should state its persistence and read its minimum detectable difference from Table 9 before it is pinned".
- Table 9's block21 and block63 rows at shares 0.25-0.5 do not reach 80 % power at k = 15 inside its grid. Those figures are exploratory until Q-55's clean rerun, E-035 (4), so none is quoted here.
- The cells' own description:
  - s3 is "a daily state whose calm regimes last weeks";
  - u3's rank moves slowly;
  - s1 and s2 persist through a night.
- That places s3 (and probably u3) in the block5-block21 class or beyond, and s1 and s2 near "window" with cross-night clustering.

**What it allows.** The family is pinned and spends its program number on cells that cannot be judged. A cell untestable by persistence is then likely to close at stage C ("no selection lift above the MDL"), when that close could have been known at the declaration.

**Remedy.**
- For each cell, state its expected persistence class (offer, window, session, block5, block21 or block63) and the reason.
- Read Table 9 after Q-55, and add "Q-55 rerun from a clean checkout" to section 20's prerequisites.
- Then decide, before the pin, whether s3 and u3 stay as counted cells, are pre-declared screens, or are dropped (counted either way).
- If the lead wants persistence measured rather than argued, the measurement can be specified: the run-length distribution of each state's in-state sessions on the choice block. It reads bars only, no walk and no outcome, and costs minutes. But it is a choice-block read before the pin, and that is the lead's call under a row.

### m1 (MINOR) -- the 17:30 start does not follow from its stated reason

- **Where:** 6.2 line 413 ("defined with at least 15 bars"); 6.3, lines 423-424; 8, line 565 ("17:30 (LRS needs at least 15 bars)").
- **Evidence:** at mark m the state reads bars stamped 17:00..m − 6. That is 15 bars at the 17:20 mark and 25 at 17:30 (check 4).
- **What it allows:** two rules where one is meant. The 17:30 value reads as chosen, with a reason that does not produce it.
- **Remedy:** keep 17:30 with its real reason (for example, half an hour of the night), or make the rule "at least 15 bars" alone. Either way, one rule.

### m2 (MINOR) -- the 07:40 start is right for the family's own entries; fallbacks and the base keep 07:35:00

- **Where:** 3, line 230; 5.2, lines 284-287 ("a fallback opening may still take it, as P-16 does").
- **Evidence:**
  - P-16's mark m enters at the bar stamped m. `atlas_local.day_arrays` indexes bars by their end minute (lines 33-48), and `fast_walk.entry_bar` takes the first bar after the slot (lines 24-27), so the 07:35 mark enters at 07:35:00 (D-533 (2)).
  - E-007 (d) and CHARTER section 4 put report-day entries "strictly after 07:35:00".
  - The audit's U7 (a) leaves 07:35:00 possibly inside Topstep's Tier 1 window, where a fresh XFA's MNQ entries are capped at one micro (`docs/audits/phase0/E_rules_currency.md` C1).
  - The engine does not model that window. A full-size fallback opening at 07:35:00 is what the audit flagged.
- **What it allows:** no bias in the lift, because every arm shares it. But a carried design's contract fit (CHARTER section 4) would be stated for the family's chosen entries only.
- **Remedy:** a decision row recording that the design inherits P-16's registered report-day schedule for fallbacks and non-opening trades, under E-007 (d)'s open boundary. Stage A should count each design's openings at report-day 07:35:00, and that count should go beside the verdict.
- **On the 07:40 start itself:** the clock holds. The alert is at 07:35 and the last bar read is stamped 07:34, so the 07:30 release minute is read once it has closed. As the draft says, s1 will fire on most report-day offers. The day-kind strata neutralise that in L; in-wait openings then concentrate on report days, which A2 reports.

### m3 (MINOR) -- a fast state's lift can be Stage 2's flatten convention, not persistence

- **Where:** 1 (v) (c), lines 161-167; 1 (iv), line 147 (u3 negative); 12, lines 754-755 (the `close` convention "beside"); 14, lines 822-824.
- **Evidence:**
  - `STAGE2` flattens at the worst of the bars ending 15:08-15:10, less two ticks. A state that picks fast nights avoids that charge.
  - E-028 (2) records family R's drafter expecting u3's trade-level lift to be "only the cost avoided at the flatten -- much of it Stage 2's conservative flatten convention".
  - C3 cannot catch this, because a cost avoided raises both halves.
- **What it allows:** u3 (stated negative) or s1 is carried as a persistence filter while its lift is the convention's pessimism. The draft would only report that beside, after carrying.
- **Remedy:** make C1's lower bound above zero under the `close` flatten convention a further line of the same intersection. This costs no level. Or apply the line to the target-share part of the kind decomposition at fixed costs.

### m4 (MINOR) -- the seam can be realised; its refusing checks would not see it fail

- **Where:** 5.4, lines 314-318 and 330-333; 18.1 item 3, lines 922-927; A1 items 3-4, lines 609-613; T-5, line 942.
- **Evidence:**
  - **What the router calls.** It asks the **draw** registered under the account's key, not the account. `TierSizedDraw` registers itself at construction (`sizing.py` 461-463), and the router holds draws in a `WeakValueDictionary` (`shared_days.py` 233-240) and calls `drw.can_take(h, j, balance, floor)` (373-381).
  - **How a subclass can gate.** A `FundedAccount` subclass can reach `self.draw.router` and `self.draw.key` and register a wrapper. It must hold the wrapper strongly: a collected wrapper leaves no draw, so the trade is assigned with no `can_take` at all.
  - **What the wrapper must supply.** `can_take` receives neither the calendar day nor the account, so the wait counter and the (h, j) to (date, mark) state lookup must come from the wrapper.
  - **What A1 can see.** With the state always on, or W = 0, the wrapper returns the vendored answer, so a wrong lookup or a gate that never bites passes A1 bit for bit.
- **Remedy:**
  - Add two refusing checks that bite. (i) With the state never on, every opening falls on its sixth live session. (ii) With the state equal to the drawn placebo, every in-wait opening's (date, mark), read by the place-recording adapter, is in the placebo's set.
  - Run T-5 through the vendored router and lockstep loop, not on `can_take` in isolation.
  - Pin the off-by-one of "first W live sessions" against `FundedAccount.days` at routing time.

### m5 (MINOR) -- the news readings are stale

- **Where:** 3, line 231 ("Q-39's reading decides it"); 8, line 594; 13, lines 808-809.
- **Evidence:** E-034 records Q-39 as read and decides that "the full-size funded opening held through an unnamed release stays as it is ... listed with the other unstated rules in every scorecard's 'not modelled' note". The draft's note lists only the user's money, time and taxes.
- **Remedy:**
  - Cite E-034.
  - Add the unstated news rules to the "not modelled" note.
  - Note that a selection which moves openings toward post-release mornings changes the share held through ISM. A2 already reports the report-day share; add the ISM/GDP-day share if a calendar is ever loaded, or say it is unknown.

### m6 (MINOR) -- B2's slow component is sized on the choice span only

- **Where:** 11 item 2 (a\*), lines 702-704; item 4, lines 712-713.
- **Evidence:**
  - E-036 M3-1 found family B's B2 amplitude, taken from 2020-2023, too small for the judged block.
  - This draft's own section 2 records that the sided follow effect, the same persistence read with a side, was below P-16 on 2020-2023 and above it on 2024-2026 (D-578 (3), D-580; a disclosed pre-read).
  - If c_i's slow part moves with that persistence, a\* from 2021-2023 understates it.
- **Remedy:**
  - Declare a floor for a\*, for example a stated multiple, or the largest 63-block mean of a declared longer reference.
  - Or lengthen the null's mean block.
  - Put "a slow component larger than the choice span's" beside the verdict as an assumption that carries the level.

### m7 (MINOR) -- T-10 cannot do what it is said to do

- **Where:** 18.2, line 947.
- **Evidence:**
  - B2 needs at least 1,000,000 replicates per line (line 709).
  - Checking a size of 0.05/132 or less needs tens of thousands of outer replications (calibration section 3).
  - Their product is not a fast-tier test.
- **Remedy:**
  - Declare T-10's level (for example 1 % and 5 %), its replications and its failure rule (the failure protocol, not a rerun).
  - Say that the family's level itself rests on the larger-of rule, not on T-10.

### m8 (MINOR) -- "a third by construction" holds only for iid values

- **Where:** 6.4, lines 456-457; 5.4, lines 324-325.
- **Evidence:** in check 3, a rolling 250-session bottom third on an AR(1) series:
  - fires on a third every year when the series is iid;
  - at phi 0.97 to 0.995, the per-year share ranges widely, from a few per cent to over two-thirds;
  - at phi 0.995, some years fall below K1's 21 sessions.
- **Remedy:**
  - Correct the claim. The share is about a third over the long run, and per year it follows the state's persistence.
  - Base W's rationale on F2's ordered calendar, not on the iid share.
  - Report the supply per year next to K1, as A5 does.

---

## Notes (readings; no rule changes)

- **n1. The open question on H and IV is answered.** The question is whether earlier sessions' 08:30-08:59 bars inside H and IV fall in the closed branch (20, third red-team bullet; 6.1, lines 396-399). E-036 (M3-2, the lead's ruling) defines Stage 2's closed opening-range branch as "trading rules defined on or triggered by the opening range". Whole-day ranges of prior sessions are not such a rule, so H and IV stand. Cite E-036 rather than leave this open.
- **n2. The twin's form is answered** (7.2, lines 517-518; 20 lead's item 2). The population-mean expectation is the form Q-16 calibrated (calibration 1.3, lines 87-90, and 7.3: "carries no placebo noise"). The seeded draw goes beside.
- **n3. The 1R mirror holds only for gross.** The claim (1 (i), lines 106-109; T-1) is true for gross outcomes on resolved paths. With P-16's breakeven move, the flatten, and kind-dependent costs, a 1R path's side-symmetric value is not identically zero, and at 1.5R persistence acts. The reason V_other is "expected small" (7.4, lines 543-547) is weaker than stated. It is beside, so no rule changes; say so.
- **n4. x3's frame and T-2's cuts.**
  - The library's `_prior_median` (`extended/features.py` 422-436) runs over the frame's 20 prior days, while 6.2 says every window runs over P-16's walked sessions. Name the frame.
  - The library's `_win_sum` truncates safely at the day's start (438-441).
  - Plain negative-index slicing would not truncate. An example is the library's `ret_w` line, `Cff[:, s - 1 - w]` (515-516), which is only safe because it runs at RTH. At overnight slots below the window, such slicing wraps to the end of the same day, which is the future.
  - A3/T-2's cuts should name the asia band's first marks (18:00, 18:05), where rv_60's window reaches back past 17:00.
- **n5. V is gross of the wait's cost.** It values the selection, not the waiting XFA's idle sessions, nor the solver's per-day slot rent for a seat that waits. The scorecard shows the wait. Say beside C2 that the value line does not net it.
- **n6. Q-35's ordering.** E-021 (2) queued this draft after Q-35. Stage A's choice-block count is a reasonable substitute. Record that the lead accepts it.
- **n7. A4's default.** If A4 fails, u3 waits "for the lead's ruling" (line 631). That is an open choice point after a stage-A reading; declare the default (u3 closed, counted).
- **n8. How V converts R.** V turns an R lift into win probability at 1/4 and prices it by the solver's binary `mean_dv`. A lift made of kind mix or breakeven exits is not a change in win probability, so the conversion is first-order only. The value-map price at the bound is uncalibrated (calibration 7.4 item 10).

## What I tried that found nothing

- **Look-ahead in every state quantity.** I checked LR, LRS, DIS, har, H, HS, U, T, the 250-session mid-rank share, and u3's IV, M, x1-x3, fold fits and y_hat share. Each reads only bars stamped at or before m − 6 of day d, or whole earlier walked sessions.
  - u3's folds train only before each test year, so no test label enters a fit. The 22-session gap is redundant but harmless.
  - The y_hat reference for day d uses the fit day d uses, and that fit precedes d.
- **The entry convention, in code.** `atlas_local.day_arrays` indexes by end minute, and `fast_walk.entry_bar` takes the first bar after the slot. So the mark m enters at the bar stamped m, five minutes after the m − 5 alert (D-522 (2)). The 08:25 mark enters at 08:25:00, outside 08:30-09:00.
- **Calendars and rolls.**
  - BLS report days and FOMC days are published ahead, and the early-close calendar is pinned (E-029).
  - The day's contract is chosen by the previous day's volume (`data/README.md` section 5), so it is known ex ante.
  - Every state is a within-day log ratio, and IV's points² enter only as a ratio across days.
- **Normalisers.** The rolling third, HAR terms and M are past-only. B2's a\* and the stage-B bootstrap read the choice span only. mu_g uses the whole stratum, but only in the estimand, never in a rule at t.
- **Leakage.** The final u3 fit is hashed and pinned before any judged read. T-3 replaces the judged block. The reader refuses choice or fitting purposes, and none of the four purposes contains a choice word.
- **Multiplicity.** The 4 cells are counted whether killed or read. Stage B spends nothing, and one cell is judged at 0.05/(k(k+1)). No searched values.
- **Seeds.** `grep` over the worktree, and `git grep` over every commit's tree, finds 20261980-20261989 only in the draft and its test.
- **T-1.** All 14 tests pass. I re-derived the exact-twin identity and the drift's second order, and they are correct as illustrations.
- **The router mechanics** the draft states:
  - a declined offer passes to the next account (`passed_over`, `shared_days.py` 378-381);
  - a new account is stamped as of its first day (284);
  - one trade an account a session (cap).
- **The 2020 warm-up** (22 + 120 sessions before the first state, the first fold's training data) fits inside 2020's walked sessions.
- **Prior exposure (section 2).** It is honest about S1, S2 and S3, the handoff's tables and the value map. The choice of s1 and s2 as relatives of S2's two closest cells is disclosed.

## What I could not check

- Every magnitude on real data, because that needs bars, walks or campaigns: each state's run lengths, the routing deviation V(P-16), the iid-versus-ordered fallback shares, and the flatten convention's share of a fast state's lift.
  - The F4 run-length count reads bars only (minutes; the lead's call before the pin).
  - The rest are stage A/B readings once F2 and F3's remedies are declared (hours).
- Whether `cons` holds its level on the side-symmetric 3R series under a persistent independent selection. This needs Q-16's script with a `sym3` outcome: both sides of P-16's judged offers, already walked for Q-16's pairs. Its cost is like Q-16's placebo runs, hours.
- u3 restates family R's draft, which is unreviewed (E-028 (2)). Its bands, the 22-session M and x3 are reviewed here only as restated.
- Whether a fresh XFA waiting five sessions meets any inactivity rule. No such rule is on the verified ledger as I read it. I did not search it, and I used no web.

---

## Appendix: the synthetic checks (exploratory; seeds 777001-777010; numpy only; nothing read)

1. **Strata through `placebo_selection_bound`** (seed 777001; 400 replications).
   - **Setup:** 3 years x 213 sessions x 20 marks; strata (year, mark); c = year mean (0, −0.10, +0.05) + an AR(1) session effect + unit noise.
   - **Selection:** a daily two-state chain (stay 0.9) with in-state shares 0.15, 0.55 and 0.30 by year, independent of c.
   - **Result:** on the raw c, the mean estimate was −0.0243 (s.e. 0.0011). On c − mu_g it was −0.0002 (s.e. 0.0007), with one-sided 5 % rejections of 0.025.
2. **The wait** (seed 777002).
   - **Setup:** a daily state with share 1/3 and stay probability 0.80, 0.90, 0.95 or 0.98 (mean in-state runs of 5, 10, 20 and 50 sessions); W = 5.
   - **Result:** in history's order the fallback share was 0.436, 0.535, 0.604 and 0.643. On independent days it was 0.130, 0.127, 0.137 and 0.131.
3. **The rolling third** (seed 777003). A 250-session mid-rank share (at least 120), bottom third, AR(1), 20 x 6 years.
   - **phi 0:** the per-year share's p10, median and p90 were 0.30, 0.34 and 0.36.
   - **phi 0.97:** 0.16, 0.33 and 0.57.
   - **phi 0.995:** 0.02, 0.35 and 0.72, with 19 % of years under 21/250.
4. **The first defined mark.** Bars stamped 17:00..m − 6: 10 at 17:15, 15 at 17:20, 20 at 17:25, 25 at 17:30.
5. **The routing toy** (seed 777010; 200,000 nights).
   - **Setup:** lognormal night volatility; another account's trade from the first mark, with mean duration tau/3 over sigma²; the opening at the first mark at least 5 minutes after it; c = −0.25 R x the chance of no resolution by 15:10 under a driftless walk; mu_g the mark's mean over all nights.
   - **Result:** the mean deviation at reached offers was −0.0008 R (tau 150, spread 0.4), −0.0010 (250, 0.4), +0.0036 (250, 0.7), +0.0001 (400, 0.4) and +0.0080 (400, 0.7).
   - **Reading:** not zero, and its sign depends on the volatility spread. This only illustrates that the null is not centred; the real magnitude is a stage-B reading.
