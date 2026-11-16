# Red team, second read: `prereg/DRAFT_F-B_multifeature.md` version 2 (family B), 2026-11-16

**Target:** `prereg/DRAFT_F-B_multifeature.md` at master 2aa6b3b (worktree `wt-scout`, branch `wt/wt-scout`), with
`tests/test_family_b_side_rule.py` and `extended/features.py`. **Read against:** `CHARTER.md` (as amended by E-008, E-014
and E-015); `DECISIONS.md` E-001..E-019; `CLAUDE.md`; the feature-rules and prereg-discipline skills; the first review
(`docs/reviews/DRAFT_F-B_multifeature_2026-11-15.md`); the Phase 0 audit (`docs/audits/phase0/D_protocol.md`); the Q-16
brief; `prereg/DRAFT_F-02_resting_levels.md` where the draft borrows its forms; and the Stage 2 files the draft cites
(`vendor/stage2/DECISIONS.md` D-212, D-266, D-277, D-281, D-492..D-500, D-525, D-527, D-558, D-580, D-592, D-604,
D-641, D-642; `propedge/research/resolved_coin.py`, `s1_sided_coin.py`, `s3_latency.py`, `atlas_local.py`;
`config/atlas_a3.yaml`; `results/rc_width_screen.csv`, `u_hours.csv`, `u_value_map.csv`).

**What the brief held.** It asked me to attack what is new, and named the new parts. It did not say what answer it
expected. The draft states its own expectation ("speed yes, direction probably not"). I treated that expectation as part
of the target, not as a prior.

**What I ran.** Nothing read a bar, the atlas or NQ from 2026-07-17. Nothing ran the engine and nothing touched the web.
I read Stage 2's vendored result files only for side-free resolution and value rows, as the draft itself does. I ran
four synthetic checks as scratch scripts (one small process at a time, seeds fixed before running; the Appendix gives
each one in full). They are exploratory and select nothing. I also ran `tests/test_family_b_side_rule.py` (3 passed) and
the fast tier of `tests/test_features.py` with `tests/test_features_lookahead.py` (21 passed).

## Verdict: **must be redrafted**

The first review's C-1 fix works. The centred side cannot collapse into the majority side: since p is monotone in the
linear score, the intercept drops out of `sign(p - p~)` exactly. M-5 and M-6 are fixed, and M-2 is fixed for the
effects Stage 2 recorded.

Five material defects remain, and each changes a declared rule:

- **M2-1.** The redraft moved the entries out of the opening window, but not the opening range itself. At the first
  alert, two of the 45 features are the two excluded opening-range features bit for bit, and several more carry the
  same information.
- **M2-2.** Stage B2's surrogate, the correction for M-4, removes the slow component of the side process that makes the
  test over-reject. B2 would certify a test that rejects about twice its level. The rotation gate passes about two
  thirds of those false rejections.
- **M2-3.** C2 is read at a 95 % bound. The charter prices the lift at the family-level bound.
- **M2-4.** On Stage 2's own whole-window resolution rows, the 37.5-point stop can reach stage C only to fail its
  judged resolution floor, and the 25-point stop sits on the per-year line. The stage-B ranking favours exactly those
  cells.
- **M2-5.** The m-4 correction made the filter worse. Its threshold comes from models that are not the one judged, and
  the judged model passes a few per cent of offers, not a fifth.

| id | severity | finding (one line) |
|---|---|---|
| M2-1 | **MATERIAL** | At the 09:00 alert `range_rth` = `or_width`, `pos_rth` = `or_pos` and `ret_30` ~ `ret_rth` = the opening range's net move (the code's own arithmetic; synthetic: identical). E-016 (2)'s exclusion holds in name only, section 2 (c)'s "uses no opening-range feature" is false, and the 09:05 entry is the session's first trade, so it carries most funded openings (line 455). Until the operator rules, the audit's default (1.2 (3)) is exclusion |
| M2-2 | **MATERIAL** | B2 resamples run lengths, so its synthetic sides lose the slow part of a side process that flips within sessions (synthetic: the 63-session mean side's sd falls by a factor of about 8). A 21-block t that rejects about 1.8 times nominal at 0.001 under the real-type process looks nominal under B2's surrogate. C1-r passes in about 64 % of the spurious rejections and itself rejects about twice its 0.01. C1-f's weights are built from independent s* and f* |
| M2-3 | **MATERIAL** | C2 is "V's one-sided 95 % lower bound" (line 447). CHARTER section 3, E-008 and the prereg skill price the lift "at that bound", the family level 0.05/(k(k+1)), and F-02 does that (its lines 285, 416). This is a looser pass line than the charter's, which needs the operator |
| M2-4 | **MATERIAL** | `rc_width_screen.csv:198`: 09:05 at 150 ticks is 5.17 % unresolved at R = 3 over 2020-2026, on a walk that resolves at least as often as the family's. If the choice block admits it (at most 5 %), the judged block is about 5.4 % or more, so the 37.5-point floor fails. `u_hours.csv:175-208`: the 25-point US coin's worst year at R = 3 is 6.0 %. The ranking prices 150 ticks at p16's funded opening, so the family's one judged read can be spent on a resolution failure the files already predict |
| M2-5 | **MATERIAL** | The filter threshold is the 80th percentile of the inner folds' out-of-fold scores, but the judged model is the final one, trained on far more sessions. With a mean loss and a fixed lambda its score spread is smaller (synthetic: 2-7 % of judged offers pass, not about 20 %), so a filter pick is judged on a fraction of the supply stage B and the MDL assumed. The model's own training-sample quantile gives 20 % |
| m2-1 | MINOR | The alignment control's shifted label (the previous session's) is predictable from the prior-session features (`range_prior`, `ret_prior`, `pos_prior`, `d_pdh/l/c`). It is not a negative control, and it would pass the dangerous misalignment (features of day d joined to labels of day d - 1) |
| m2-2 | MINOR | B2's mechanics: the 1.5-times tolerance at the family level spends up to half again the budget; "simulated critical value only if the test fails" is a pretest (use the larger of the two always); the choice block's length is not mapped to the judged block's; B2's sides come from the inner folds' models, not the pinned one |
| m2-3 | MINOR | C2 values every routed trade at the table's R (`R_j`), so the cell's R plays no part in C2 or the scorecard. Q-16's statistic is not calibrated for dollar-weighted session sums `z_s`, and B2 does not cover C2 |
| m2-4 | MINOR | The reverse walk-forward fits on judged-block dates, which section 5's reader refuses to `fit`. The "model fitted on the three twins' sides alone" names no block |
| m2-5 | MINOR | The scorecard "on all starts" (line 482) runs design (i) at the final model's sides on 2020-2023, which are in-sample |
| m2-6 | MINOR | The canary's "99.9th percentile of the same maximum over 10,000 bootstrap draws of its own data" (line 313) does not say the draws are centred. Uncentred, the canary can never fire |
| m2-7 | MINOR | The pre-read table (lines 177-184) omits rows the drafter's own file holds or names: `rc_width_screen.csv` lines 798 and 803 (the 37.5-point US cell fails every-R-resolves; P-15's news-safe all-day cell runs to 12:00) and `u_hours.csv` / D-641 (3) (the US cells' worst-year caps). "P-15's schedule not vendored" (lines 115, 572) is half true |
| n2-1 | NOTE | C1-r's rotation keeps each session's mark alignment, so it refuses time-of-day seasonality as evidence (and largely weekday seasonality too). That is defensible, since C1-d removes only a constant drift, but it should be said |
| n2-2 | NOTE | The intercept cancels exactly from `sign(p - p~)`. Write that as the reason the rule cannot collapse, and the top edge stops mattering for balance |
| n2-3 | NOTE | The side-rule test standardises its test features by their own statistics and has no covariate shift. It cannot show the judged imbalance a level-dependent or trending feature can make (C1-d's 0.9 rule is the guard) |
| n2-4 | NOTE | The null canary cannot see a bar look-ahead: block flips randomise a leaked feature's relation, so the model learns nothing from it. Its targets are label-derived leakage and in-sample evaluation; the shift test and T-14's driftless null cover bar look-ahead. Say so |
| n2-5 | NOTE | 10:00 ET releases (ISM and others) land at 09:00 CT. The 09:05 entry follows them by five minutes: not Topstep Tier 1, but the one-tick cost may be light there. Report the 09:05 entry's spread beside |
| n2-6 | NOTE | Section 2's A3 row says "as A3 walked them (not re-checked here)". D-492 (1) says five bars late, both side rules |
| n2-7 | NOTE | Which walk the scorecard's trades carry is not stated. P-14 beside carries the breakeven move; the family's fixed walk does not. Say which, and that the comparison crosses walks |

---

## The first review's findings: whether each correction works

| finding | corrected? | why |
|---|---|---|
| C-1 | **yes** | `sign(p - p~) = sign(z - z~)` (the sigmoid is monotone and a weighted median commutes with it), so the intercept, and with it the base rate, cancels exactly. `tests/test_family_b_side_rule.py` passes (3 tests). C1-d's 0.9 rule is defined |
| M-1 | **partly** | The entries left the window but the opening range's information did not (M2-1). The prior-exposure table is completed. The MDL is on sessions |
| M-2 | **yes** | The three twins are the per-trade direction effects Stage 2 established (D-580, D-588, D-592). Their latencies are right: `s1_sided_coin.day_sides` at mark t reads bars ending at or before t, and `s3_latency.lagged_day_sides` at the entry mark with L = 5 reads at t. P-14's `brk30` and A3's `orb_rth*` are not twins, but Stage 2 recorded no coin-twin direction effect for them ("the opposite side and the coin did nearly as well", D-500 (3)(a); the ORB cells "trail", D-494 (2)), so they are not owed |
| M-3 | **in form, not in level** | Routed trades by place: yes. The level is 95 % against the charter's family level (M2-3). The statistic is uncalibrated for `z_s` (m2-3) |
| M-4 | **no** | B2's surrogate cannot see the slow component, and C1-r does not rescue the level (M2-2) |
| M-5 | **yes** | The cutoff is on 2020-2023, kinds only. `mark_resolution` refuses any column but `date`, `slot` and the kinds, and reads only the flatten kind (`resolved_coin.py:241-262`), so it is side-free. T-3 then holds by construction |
| M-6 | **yes** | Declared in F-02's form |
| m-1 | in name | 45 features and 49 columns. The opening-range information is still in through other columns (M2-1) |
| m-2 | yes, with a gap | One estimator; the canary's draws are not said to be centred (m2-6) |
| m-3, m-7..m-10, n-1..n-7 | yes | stated where the table says |
| m-4 | **regressed** | The first review's premise ("in-sample predictions are more extreme") holds for calibration against outcomes, not for the spread of a fixed linear score. Moving the threshold to other models' out-of-fold scores broke the filter's supply (M2-5) |
| m-5 | **no** | The shifted label is not a null (m2-1) |
| m-6 | partly | m2-7 |

---

## MATERIAL

### M2-1. The opening range is still in the model at the first alerts

**Where.**
- Section 2 (c), `prereg/DRAFT_F-B_multifeature.md:98-104`: "uses no opening-range feature ... this draft's reading:
  that is outside the closed specification".
- Section 7's 45 features, including `ret_30` (line 226), `ret_rth` (229), `rng_60` (232), `range_rth` (234),
  `pos_rth` (236) and `d_vwap` (245).
- Section 22 item 2 (lines 659-661).
- E-019 (`DECISIONS.md:26`): "so D-281 (3) need not be asked now".
- E-016 (2) (`DECISIONS.md:23`): `or_width` and `or_pos` kept "out of family B until the operator rules".

**Evidence.**
- **Two features are the excluded ones, bit for bit.** In `extended/features.py:517-522`, at alert slot s, `range_rth`
  is `(Hr[:, s-1-RTH_OPEN] - Lr[:, s-1-RTH_OPEN]) / A` and `pos_rth` is `(c - lr) / (hr - lr)`, where `Hr` and `Lr` are
  running maxima and minima from 08:30. At s = 09:00 (slot 960) the index is 29, the bars stamped 08:30..08:59, which is
  exactly `H_or` and `L_or` (`features.py:507-508`, `542-544`). So at the 09:00 alert `range_rth` is `or_width` and
  `pos_rth` is `or_pos`. Synthetic bars (Appendix A, seed 7, 49 days) agree to the last bit.
- **Other columns carry the same information.** `ret_30` at 09:00 is `(C[08:59] - C[08:29]) / A`, the opening range's
  net move (correlation 1.000 with `ret_rth` on the synthetic days). `rng_60` correlates 0.971 with `or_width`.
  `up_share_30`, `eff_30` and `vol_30` are the opening half-hour's own path statistics. `d_vwap` is the distance to the
  opening range's VWAP.
- **The overlap persists after 09:00.** The RTH-so-far features include the opening range at every later alert:
  synthetic correlations with `or_width` / `or_pos` are 0.948 / 0.939 at 09:05, 0.847 / 0.892 at 09:30 and
  0.639 / 0.830 at 12:00.
- **These are the trades that carry the money.** The 09:00 alert's 09:05 entry is the session's first offer. In design
  (i) the firm is flat at the start of the schedule, so the strict router takes it every session, and the draft itself
  calls it "the funded opening's usual trade" (line 455) — the place C2 prices highest (`u_value_map.csv:26214` p14,
  `:27133` p16, `c_funded_opening` `mean_dv`).
- **Stage 2's closed branch had this information set.** ORB6's agreed scope included "trend, gap and VWAP filters"
  (`vendor/stage2/DECISIONS.md:296`, D-277). At the 09:00 alert, family B's `gap`, `d_vwap`, `ret_5d` and `ret_20d` are
  those filters, applied to the 30-minute range. The lead already treated the 30-minute opening range as inside D-281
  (3)'s reserved call: E-007 (b) put `or30` out of any level family until the operator rules.

**The failure it allows.** Suppose the model learns "long when `pos_rth` > 0.5 at 09:00, filtered by gap and VWAP",
which is a 30-minute opening-range position rule entered five minutes after the range closes. It passes C1 and C1-f:
none of the three twins is an opening-range rule. The family then reports "a direction no single rule shows" in the
very territory D-281 (3) reserved to the operator. E-016 (2)'s exclusion did nothing, because it removed two column
names, not their information.

**Remedy (changes a declared rule).**
- Hold section 22 item 2 as triggered. The red team holds that at least the first alerts are inside: their inputs are
  the opening range's summaries, bit for bit at 09:00.
- Send the question to the operator now, with these facts. Until the operator rules, the audit's default (1.2 (3),
  `D_protocol.md:171-172`) excludes, so the draft cannot be pinned as written.
- **If the family is to avoid the question,** no windowed feature may read 08:30-08:59 (the first alert at 10:30 or
  later for `ret_120`), and the four RTH-so-far features (`ret_rth`, `range_rth`, `pos_rth`, `d_vwap`) must be dropped
  or redefined, because they read the opening range at every alert. That is a different family.
- **If the operator admits it,** add an opening-range follow twin at L = 5 (the sign of `pos_rth - 1/2` at 09:00, or
  A3's `orb_rth30` followed, five bars late) to C1-f.
- Either way: correct section 2 (c); have E-016 (2) read as excluding the information, not the two names; and the lead
  corrects E-019's "need not be asked now" in a new row.

### M2-2. Stage B2 certifies a test that over-rejects, and the rotation gate does not rescue it

**Where.**
- Section 12, lines 399-409: `s*` "alternates sign with run lengths resampled from the pick's out-of-fold sides";
  `f*` "likewise from the twin's own sides"; the test "holds" if its Monte Carlo rate is at most 1.5 times the level.
- Section 13, lines 437-440 (C1-r).
- Section 17, lines 562 and 566.

**Evidence.**
- **Why the surrogate fails.** A side process made of iid run lengths with alternating signs has long-run variance
  `sd(L)^2 / mean(L)` per offer, so it has almost no low-frequency power. A model's real sides mix a slow component
  (daily features and regimes set a session's long share) with fast intraday flips (`ret_5`, `rng_15`, `vol_5` move the
  side within the session). Their runs are short even inside a long-biased regime, so the slow component survives only
  in how consecutive runs depend on each other, and resampling the runs iid destroys exactly that. The slow component is
  what correlates spuriously with a persistent drift in d: it is the spurious-regression term M-4 was about.
- **The synthetic check** (Appendix B; seeds 11 and 12; 750 sessions, 24 offers a session; d's drift ±0.03 switching
  about every 120 sessions; a side regime switching about every 60 sessions with long share 0.8 / 0.2 inside it, and
  independent flips per offer; 20,000 replications under H0):

  | side process | sd of the 63-session mean side | t on 21-session block means rejects at 0.01 | at 0.001 |
  |---|---|---|---|
  | iid sides | -- | 0.0089 | 0.0009 |
  | the real-type process | 0.445 | 0.0159 | 0.0018 |
  | **B2's surrogate of a realisation of it** (mean run 3.1) | **0.055** | **0.0097** | **0.0011** |

  The Monte Carlo SE at 0.001 is 0.00022. B2 would find the test "holds" (about 1.1 times nominal), while for the
  side process it is meant to represent the same test rejects about 1.8 times nominal at 0.001. The excess grows into
  the tail, where 0.05/132 sits.
- **The rotation gate does not rescue the level** (Appendix C, seed 31, the same design, 4,000 replications):
  - the t rejects at 0.01 in 0.0168 of nulls, and the rotation gate (shifts 63..T-63, rank p at most 0.01) passes in
    0.0210;
  - both hold in 0.0107, so **the gate passes in about 64 % of the spurious rejections**. The same slow alignment makes
    the observed statistic extreme among the rotations;
  - the gate's own size is about twice its 0.01 here, probably because each rotation carries one artificial regime
    break, at the wrap.

  So the conjunction's size is about two thirds of C1's actual size, not the family's level.
- **C1-f's weights are wrong.** `s*` and `f*` are drawn independently, but the real model shares `ret_15` with
  `mom15` (`sign(ret_15)` is the twin) and is built from the same short-horizon features as `lbrk5` and `lnbar1x4`. The
  real weight `s - f` is zero on most offers and persistent in its own way; `s* - f*` is zero on about half and has
  neither property. Also, at the boundary of C1-f's null (equal lifts), `(s - f) d` carries the follow effect's
  regime-varying lift, which D-580 and D-588 say is concentrated in 2024-2026. Independent weights cannot model that.

**The failure it allows.** A model that is long through the judged block's rising regimes and short through its falling
ones, by chance, passes C1, C1-d and C1-r at about twice the declared family level, and B2 has declared the test sound.
That is M-4's failure, with a certificate attached.

**Remedy (changes a declared rule).**
- **Preserve the side series' own dependence.** Either resample the pick's actual out-of-fold side series, jointly
  with the twins' sides and the filter's selection, in long session blocks (a stationary bootstrap with mean block
  length of at least 63 sessions); or fit a two-scale model and use it.
- **Refuse B2 if the surrogate does not reproduce the observed variance of the 21-, 63- and 126-session mean side**
  (and of `s - f`) within sampling error.
- **Better: run B2 at stage C, on the pinned model's judged side series itself.** Read the sides only, hash them before
  any d, and set them against long-block bootstraps of the choice block's d. That conditions on the side series
  actually judged.
- Say plainly that C1-r caps the conjunction near 0.01 and does not restore the family level.

### M2-3. C2 is read at a 95 % bound; the charter prices the lift at the family-level bound

**Where.** Line 447 ("C2: V's one-sided 95 % lower bound ... at least $500 a year") and line 567 (section 17).

**Evidence.**
- `CHARTER.md:83-87`: the pass line is the lift's lower bound "at the family's level 0.05 / (k (k + 1)) ... and its
  value -- the lift priced by Stage 2's value map where the family uses it -- **at that bound** at least the bar".
- E-008 (`DECISIONS.md:15`), `CLAUDE.md:22` and `.claude/skills/prereg-discipline/SKILL.md:61` say the same.
- F-02's draft prices the lift "at C1's lower bound" (`prereg/DRAFT_F-02_resting_levels.md:285, 416`).
- F-B's first version had the same 95 % and the first review did not flag it. That does not make it right.
- At k = 11 the family-level one-sided z is about 3.4 against 1.645 at 95 %, so the 95 % bound sits about 1.7
  standard errors higher.

**The failure it allows.** A cell whose lift clears C1 at the family level, but whose value at that bound is under
$500 a year, passes C2 at 95 %. A design is carried whose value at the charter's level is below the bar. Under the prereg
skill, "a looser level ... needs the operator; a declaration may not do it on its own". The confirmation's C2 at 95 %
(section 16) is consistent with the registered 0.05 there, and is not part of this finding.

**Remedy (changes a declared rule).** V's one-sided lower bound at 0.05/(k(k+1)) (with stage B2's critical value where
B2 applies), at least $500 a year, as F-02 does.

### M2-4. The 37.5-point stop cannot pass, and the 25-point stop sits on the per-year line

**Where.**
- Section 3, lines 123-133 (three stops, the per-mark cutoff pooled over 2020-2023), 136-138 ("the 37.5-point stop
  will probably contribute nothing ... killed at K1") and 148-149.
- Section 11's ranking (base `p16` for 150 ticks).
- Section 13's floors.
- Section 5's pre-read table.

**Evidence.**
- **The 37.5-point stop can pass stage A only by failing stage C.**
  - `rc_width_screen.csv:198`: the 09:05 mark at 150 ticks, R = 3, is unresolved 5.17 % over 2020-2026, not offered.
    That is Stage 2's walk, with the breakeven move.
  - The move only adds exits: a trade unresolved with the move is unresolved without it. So the family's fixed walk
    leaves at least as many trades unresolved.
  - If the family's choice-block share at 09:05 is at most 5 % (the cutoff admits it), Stage 2's choice-block share is
    at most 5 % too. With the choice block about 61 % of the sessions, the judged share under Stage 2's walk is then at
    least about (0.0517 - 0.61 x 0.05) / 0.39, about 5.4 %, and under the family's walk at least that. So the judged
    floor at R = 3 fails.
  - 09:10 (5.68 % whole-window, the next row) is worse.
  - The only escape is a gap between the two session sets (Stage 2's 1,576 RTH sessions against the family's kinds
    after 22 warm-up sessions), and the margin is small.
  - Otherwise the 37.5-point cells die at stage A, by K1 if no mark is admitted, or by K2's per-year line. The per-year
    spread is large: the 37.5-point US coin, marks 08:30-09:00, is 3.75 % pooled at R = 3 but 8.2 % in its worst year
    (`rc_width_screen.csv:798`; `u_hours.csv:310`).
  - So no 37.5-point cell can reach a pass.
- **The 25-point stop is on the per-year line.** Stage 2's 25-point US-hours coin, marks 08:30-12:00 (42 marks,
  `u_hours.csv:175`), is 2.56 % pooled at R = 3 but 6.04 % in its worst year (`u_hours.csv:196`, `:208`). D-641 (3)
  capped its offered R at 2.5 for that reason (`vendor/stage2/DECISIONS.md:659`). The family's 25-point population
  drops the fast 08:30-09:00 marks and walks without the move, so on the evidence on file its worst year at R = 3 is
  likely above 5 %. The family cannot cap R, because the table asks 3R at the funded opening (lines 145-147). The
  pooled cutoff (line 125) is weaker than K2's per-year line (line 298), which guarantees cells admitted at the edge.
- **The ranking prefers the doomed cells.** Stage B ranks by `mean_dv` at the place, and p16's funded opening (R = 3
  only) is about 1.6 times p14's (`u_value_map.csv:27133` against `:26214`). A 37.5-point cell that survived stage A
  and Kill B would very likely be the pick.

**The failure it allows.** The family spends its one judged read, and its program family number, on a cell that a file
already on disk says fails the judged resolution floor. The close then reads "a floor failed", which says nothing about
direction. At 25 points the same can happen with lower odds, in a judged year.

**Remedy (changes a declared rule).**
- **Drop the 37.5-point stop now,** on the disclosed whole-window pre-read. It is side-free, the decision is recorded
  in the pinning row as a pre-read choice, and the cells drop to 12.
- **Make the cutoff per year,** consistent with K2: a mark is admitted only if it is at most 5 % at every table R in
  every choice year.
- State the 25-point expectation in section 3 from `u_hours.csv` and D-641 (3).
- Optionally, rank stage B's survivors only among cells whose worst choice year at R = 3 leaves a declared margin under
  5 %.

### M2-5. The filter's threshold comes from models the judged block does not use

**Where.** Section 10, lines 365-367 (the 80th percentile of "the inner folds' out-of-fold `abs(p - p~)` ... pooled"),
section 9 (the final model refitted on all of 2020-2023), and lines 559 and 317-322 (the MDL from the cell's offers per
session).

**Evidence.**
- The objective is a session-weighted **mean** log loss plus `lambda/2 ||beta||^2` (line 327), so the penalty's
  weight does not fall as the training block grows. At fixed lambda the noise in beta shrinks like `1/sqrt(D)`, while
  the signal part keeps the same shrinkage.
- The inner folds train on about 200, 450 and 700 sessions; the final model on about 950. The pooled threshold is set
  mostly by the first fold's wide spread. The final model's scores on the judged block are narrower, so far fewer
  offers clear it.
- Synthetic (Appendix D, seed 21; 20 offers a session, 49 columns, the declared objective and solver), the share of
  judged offers through the filter:

  | lambda | null | weak signal |
  |---|---|---|
  | 0.25 | 0.058 | 0.067 |
  | 25 | 0.023 | 0.047 |

  The draft says "about a fifth pass out of fold".
- With the final model's own training-sample 80th percentile instead (seed 22), the judged share is 0.195 at lambda
  0.25 and 0.199 at lambda 25. A fixed linear score has the same spread on new offers drawn like its training ones. The
  first review's m-4 premise was about calibration, not spread.
- The pooled threshold also makes stage B's filter cell mostly 2021's offers, where the first fold's spread is widest.

**The failure it allows.** A filter pick chosen in stage B, at about 20 % of the offers and a K1 and MDL computed
there, is judged on roughly 3-10 times fewer offers. Its lift, even if real, misses the family level for lack of
supply. The close records "no lift above the MDL" for an MDL that was never the one in force.

**Remedy (changes a declared rule).** Each model's threshold is the 80th percentile of its own session-weighted
training-sample `abs(p - p~)`, pinned with it: each inner fold's for stage B, the final model's for stage C. Report the
judged share beside, and compute the MDL on it.

---

## MINOR

- **m2-1. The alignment control is not a negative control** (lines 306-309).
  - The shifted label (the previous session's resolution at the same mark) is a function of the previous session's
    bars, and those are read directly by `range_prior`, `ret_prior`, `pos_prior`, `d_pdh/d_pdl/d_pdc` and the last day
    of `atr14`/`atr5`. So the shifted AUC is not near 0.5, and the comparison sets two predictable targets against each
    other.
  - The failure it allows: the misalignment that matters, features of day d joined to labels and pair values of day
    d - 1, gives a high "aligned" AUC through the prior-session features and passes. In the direction pipeline the same
    join pairs today's side with yesterday's outcome, which `ret_prior` reads, and gives a spurious lift that neither
    the shift test nor the canary sees (n2-4).
  - Remedy: replace the control with an exact join assertion (each label row's (day, entry mark) equals its feature
    row's (day, alert + 5)), and rest alignment on T-14's driftless null and planted size (section 20 item 6), saying
    that it is the proof.
- **m2-2. B2's mechanics** (lines 404-409).
  - The 1.5-times tolerance (T-6's, written for 0.5 % and 2.5 %) lets a family spend up to half again its level.
  - "The simulated critical value if the test does not hold" is a pretest. Use the larger of Q-16's and the simulated
    critical value always.
  - The choice block's length (about 1,000 or 750 sessions) is not mapped to the judged block's (about 630).
  - B2's run lengths come from the inner folds' models, not the pinned one (M2-2's stage-C remedy removes this).
  - Remedy: say each of these, or adopt M2-2's remedy.
- **m2-3. C2's R and statistic** (lines 441-448).
  - `d_i(R_j)` is the pair value at the R the table took, from all six table R's, so the cell's R (1, 1.5 or 3) plays
    no part in C2 or in the scorecard. The three R-cells of a stop and use are one design there, and C1 judges a
    bracket C2 does not price.
  - "The lower bound of mean(z_s) by Q-16's statistic" applies a test calibrated for ±1-weighted pair values to
    dollar-weighted sessions with weights an order of magnitude apart, and B2 does not cover C2.
  - Remedy: say that C2 is the routed design's value whatever the cell's R, or restrict it to trades at the cell's R;
    and calibrate C2's statistic, or bound it conservatively (for example, C1's bound priced at the routed uses).
- **m2-4. Fits on judged-block dates** (lines 455-458).
  - The reverse walk-forward fits on judged-block dates, which the purpose-tagged reader of section 5 refuses for
    `fit`.
  - "A model fitted on the three twins' sides alone" names no block. Fitted on the judged block, it is in-sample.
  - Remedy: give these readings their own purpose and order (after the judged read is recorded), and fit the twins'
    model on the choice block.
- **m2-5. The all-starts scorecard is partly in-sample** (line 482). Design (i) "on all starts" puts the final model's
  sides on 2020-2023, the data it was fitted on. Remedy: on 2021-2023 use the inner folds' out-of-fold sides and
  exclude 2020, or report the judged block's starts only, labelled.
- **m2-6. The canary's critical value** (line 313). "The same maximum over 10,000 bootstrap draws of its own data" does
  not say the draws are centred (`(L*_c - L_c) / SE_c`). Uncentred, the bootstrap distribution sits on the observed
  value and the canary never fires. Remedy: write "centred, as stage B's q".
- **m2-7. Pre-reads not in the table** (lines 177-184).
  - `rc_width_screen.csv:798` (`rc_s150_us`: `every_r_resolves` False, worst year at R = 3 above 5 %).
  - `:803` (`rc_s100_all_nr`, P-15's news-safe variant, D-534: marks to 12:00 CT). The 25-point schedule's extent is vendored, though
    its per-mark list is not, so lines 115 and 572 are half true.
  - `u_hours.csv` / D-641 (3) (the US cells' worst-year caps at 25 and 37.5 points).
  - All bear on K2 and the judged floor (M2-4). Remedy: list them, with what they can bias (expectations and the stop
    set) and what they cannot (any side).

## NOTE

- **n2-1.** C1-r shifts whole sessions, so each rotated statistic keeps the observed within-session mark alignment.
  A lift that repeats at the same mark every session (time-of-day seasonality, learnable through `tod`) appears in
  every rotation and is refused as evidence. Roughly one shift in five realigns weekdays, so weekday seasonality is
  mostly refused too. C1-d removes only a constant drift, so C1-r is the line that removes intraday seasonal drift. That
  is defensible, but it narrows the hypothesis to timing across sessions. Say so in section 13.
- **n2-2.** Under the centred rule the intercept cancels exactly (`sign(p - p~) = sign(x.beta - median(x.beta))`).
  Section 10's argument ("an intercept that only fits the base rate moves p and p~ together") is that identity. State
  it, because it is the proof, and the test is only an illustration.
- **n2-3.** `tests/test_family_b_side_rule.py:40` standardises each sample by its own mean and sd, and its test block is
  drawn like its training block. It cannot show a judged-block imbalance from a level-dependent (`d_round`, `atr_rel`)
  or trending (`ret_20d`) feature. C1-d's 0.9 rule and stage B's long-share report are the guards. A sentence in its
  docstring would do.
- **n2-4.** The null canary (lines 310-316) flips outcomes in random 21-session blocks. A leaked bar feature's relation
  to the label then reverses in about half the blocks, so the model learns nothing from it and the canary stays silent.
  The canary catches label-derived leakage and in-sample evaluation, not bar look-ahead. The shift test and T-14's
  driftless null do that. Say what each guard covers.
- **n2-5.** ISM and other 10:00 ET releases land at 09:00 CT. The 09:00 alert reads bars before them, and the 09:05
  market entry follows them by five minutes. This is not Topstep Tier 1 (CPI, NFP, PPI, FOMC; E-007 (6)), and the
  constraint set is met. Stage 2's one-tick entry cost may be light on those days: report the 09:05 entry's spread on
  release days beside.
- **n2-6.** Section 2's A3 row: A3 walked its events "five bars late, both side rules" (D-492 (1),
  `vendor/stage2/DECISIONS.md:511`). Fill in "not re-checked here".
- **n2-7.** Section 14 does not say which walk the scorecard's cell carries. P-14, beside it, carries Stage 2's
  breakeven move; the family's walk is fixed barriers. Say which, and that the P-14 comparison crosses walks.

---

## What I tried that found nothing

- **Look-ahead in the library at the new alerts (09:00-15:00).**
  - I re-read every per-alert slice in `features.py:512-566` for s in 960..1320. Each reads `[:, :s]` or a prefix sum
    ending at s - 1. `ret_120` at 09:00 reads the bar stamped 06:59. The 15:00 alert reads up to 14:59. The
    time-of-day medians are over the 20 prior days at the same slot.
  - The fast-tier shift and reference tests pass (21).
  - The registry's `available_from` (at most 08:35 for the 45) is consistent with an alert grid starting at 09:00.
- **The twins' clocks.** `s1_sided_coin.day_sides` (index = bar END minute) at mark t sees bars ending at or before t,
  that is, stamped at or before t - 1: the library's alert slot. `s3_latency.lagged_day_sides(marks = t + 5, L = 5)`
  reads at t. `mom15` at the alert is `sign(ret_15)` exactly. `lbrk5`'s events come from `atlas_core.a_events` over the
  day's clock, and build test 4 shift-tests them.
- **The cutoff is side-free.** `mark_resolution` refuses any column but `date`, `slot` and the kinds, and counts only
  the flatten kind (`resolved_coin.py:241-262`). Per mark, as D-525 (4) says "an entry mark is offered only if at it".
- **The pair under the fixed walk** (`walker.py:41-50`, `63-72`, `153-171`).
  - Both sides enter at the open of the same bar.
  - Stop by touch and target by trade-through are symmetric across sides: a touch of entry + S without a trade-through
    stops the short and does not pay the long, and the mirror case does the same.
  - A bar spanning both barriers is a loss for both.
  - The flatten is the worst for each side less two ticks, both charged alike.
  - So d is side-neutral and `mean(s d)` is the excess over the coin. The 15:08 walk end comes before Topstep's 15:10.
    Entries at or after 15:08 are impossible, and late marks fail the cutoff.
  - Entry is a market order by hand at t + 5 (D-266, E-008): no API.
- **Counts and levels.** 3 x 3 x 2 = 18 cells; 7 x 3 x 2 = 42 configurations; 60 recorded; 0.05/132 at k = 11 (k = 12
  gives 0.05/156 if F-02 pins first). One judged cell. C1, C1-d, C1-f and C1-r form an intersection-union, so the level
  holds per line. 49 columns = 45 - 1 + 4 + 1.
- **The centred side under a null.** The test passes. The cancellation identity holds (n2-2). The C1-d 0.9 rule
  matches section 0.1's "95 % one way".
- **Cross-block leakage.** The final model trains through 2023-12-29 and labels resolve the same session. Every
  normaliser is trailing or in-fold, p~ and the threshold are in-fold, and judged-block features read 2023 bars only as
  past. No trade or label straddles the boundary, and the cutoff and B2 read only the choice block.
- **The rotation gate's resolution.** About 505 shifts on about 630 sessions gives a minimum p of about 0.002, below
  0.01. At 224 confirmation sessions there are 99 shifts and the minimum p is 0.01 exactly, as section 16 says.
- **B2's Monte Carlo size.** At 10^6 replications and level 3.8e-4, about 379 expected rejections with SE about 19.5:
  the upper 95 % limit separates the level from 1.5 times it, as the draft says.
- **Seeds.** `grep -rIowl -E "2026196[0-9]"` finds them only in this draft, its test and E-019's row.
- **News and conduct.** Entries from 09:05 CT are after every BLS 08:30 ET release, and FOMC days are out. One
  position per firm applies in the scorecard, and the pass line reads every offer by design. No hedging, no
  simulator-fill exploitation, no maximum size into Tier 1 news.
- **Prior exposure for the twins.** Stage 2 recorded no coin-twin direction effect for `brk30` (P-14's signal) or the
  `orb_rth*` cells (D-494 (2), D-500 (3)(a)), so the three twins are the recorded effects (save M2-1's case).

## What I could not check

- **The family's own per-mark, per-year resolution on 2020-2023** at 50, 100 and 150 ticks under the fixed walk.
  - This decides M2-4's 25-point expectation and which 37.5-point marks would be admitted.
  - Specify: `mark_resolution` on this walker's kinds, choice block only, per year. Light to moderate (one pass over
    about 1,000 sessions x 73 marks x 2 sides x 6 R). It is stage A's first step, so running it before the pin is a
    pre-read of choice-block resolution (side-free) to be recorded.
  - I did not look up which year is the 25-point US coin's worst in `u_hours.csv`, because that would be a further
    pre-read of the judged floor. The lead may decide.
- **The real side persistence and the drift regimes.** M2-2's magnitudes are my assumptions. Stage B's side run lengths
  and B2's required checks (the 21-, 63- and 126-session mean-side variances) will show the real ones.
- **Q-16's statistic** (not merged). B2's cost at 10^6 replications a line depends on it: seconds for a t on block
  means, far more for a bootstrap test.
- **Stage 2's gate bound arm.** Whether design (i)'s place assignment follows realised or shifted outcomes, and how
  "years per path" is defined for C2. Needs the place-recording adapter (section 20 item 8).
- **The seal** (Q-32): not built; stage A waits on it as declared.

---

## Appendix: the synthetic checks (scratch, exploratory, seeds fixed before running)

**A. The opening range at 09:00 (M2-1); seed 7.** Synthetic bars only. The calendars are a dummy, so no file is read.

```python
import sys; from datetime import date
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-scout")
import numpy as np
from extended import features as F, synthetic_bars as SB
bars = SB.generate(SB.Spec(start=date(2021, 1, 4), end=date(2021, 3, 31), seed=7))
cal = F.Calendars(frozenset(), frozenset(), tuple(), tuple())
X = F.compute(bars, [F.slot(9, 0), F.slot(9, 5), F.slot(9, 30), F.slot(12, 0)], cal)
for m in ("09:00", "09:05", "09:30", "12:00"):
    x = X[X["alert"] == m].dropna(subset=["or_width", "range_rth"])
    print(m, len(x), np.allclose(x["range_rth"], x["or_width"], rtol=0, atol=1e-12),
          np.allclose(x["pos_rth"], x["or_pos"], rtol=0, atol=1e-12),
          np.corrcoef(x["range_rth"], x["or_width"])[0, 1], np.corrcoef(x["pos_rth"], x["or_pos"])[0, 1])
x = X[X["alert"] == "09:00"].dropna(subset=["ret_30", "ret_rth", "rng_60", "or_width"])
print(np.corrcoef(x["ret_30"], x["ret_rth"])[0, 1], np.corrcoef(x["rng_60"], x["or_width"])[0, 1])
```

Printed: 09:00, 49 days, True, True, 1.0, 1.0; 09:05 False, False, 0.948, 0.939; 09:30 0.847, 0.892; 12:00 0.639, 0.830;
`ret_30` against `ret_rth` 1.000; `rng_60` against `or_width` 0.971.

**B. B2's surrogate (M2-2); seeds 11 (the realisation whose run lengths B2 resamples) and 12 (the replications).**

```python
import numpy as np
from scipy import stats
T, m, B = 750, 24, 21; nb = T // B
a, q_d, sig_eta, sig_eps = 0.03, 1 / 120, 0.30, 0.35        # d: drift +-a (Markov), session and offer noise
q_s, p_in = 1 / 60, 0.80                                      # side regime; long share 0.8 / 0.2 inside it
R, ALPHAS = 20000, (0.01, 0.001)
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def d_parts(rng, n_rep):
    return a * markov(rng, q_d, n_rep, T) + sig_eta * rng.standard_normal((n_rep, T))
def reject(x):
    bm = x[:, :nb * B].reshape(len(x), nb, B).mean(2)
    t = bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb))
    return np.array([np.mean(t > stats.t.ppf(1 - al, nb - 1)) for al in ALPHAS])
def session_lift(rng, base, n_plus):          # sum_i s_i d_i / m given each session's count of long offers (exact)
    n_minus = m - n_plus
    A = sig_eps * np.sqrt(n_plus) * rng.standard_normal(n_plus.shape)
    Bm = sig_eps * np.sqrt(n_minus) * rng.standard_normal(n_plus.shape)
    return (base * (n_plus - n_minus) + A - Bm) / m
def real_counts(rng, n_rep):
    return rng.binomial(m, np.where(markov(rng, q_s, n_rep, T) > 0, p_in, 1 - p_in))
def runs_of(seq):
    ch = np.flatnonzero(np.diff(seq) != 0); return np.diff(np.concatenate([[-1], ch, [len(seq) - 1]]))
def surrogate_counts(rng, n_rep, pool):       # B2: signs alternating, run lengths resampled iid, random start
    N = T * m; out = np.empty((n_rep, T), dtype=np.int64); k = int(2.0 * N / pool.mean()) + 50
    for i in range(n_rep):
        L = rng.choice(pool, size=k); L[0] = rng.integers(1, L[0] + 1)
        ends = np.cumsum(L); ends = ends[ends < N]; mark = np.zeros(N, dtype=np.int64); mark[ends] = 1
        s = np.where(np.cumsum(mark) % 2 == 0, 1, -1) * (1 if rng.random() < 0.5 else -1)
        out[i] = (s.reshape(T, m) > 0).sum(1)
    return out
rng = np.random.default_rng(11)
r1 = markov(rng, q_s, 1, T)[0]
s1 = np.where(rng.random((T, m)) < np.where(r1 > 0, p_in, 1 - p_in)[:, None], 1, -1).ravel()
pool = runs_of(s1)
rng = np.random.default_rng(12)
cr, cs = real_counts(rng, 2000), surrogate_counts(rng, 2000, pool)
sd63 = lambda c: ((2 * c - m) / m)[:, :63 * (T // 63)].reshape(len(c), -1, 63).mean(2).std()
print(pool.mean(), sd63(cr), sd63(cs))
for name in ("iid", "real", "surrogate"):
    rr, done = np.zeros(2), 0
    while done < R:
        n = min(2000, R - done); base = d_parts(rng, n)
        c = (rng.binomial(m, 0.5, size=(n, T)) if name == "iid" else real_counts(rng, n) if name == "real"
             else surrogate_counts(rng, n, pool))
        rr += reject(session_lift(rng, base, c)) * n; done += n
    print(name, rr / R)
```

Printed: mean run 3.13 (p99 19); sd of the 63-session mean side, real 0.445 and surrogate 0.055; rejection at 0.01 /
0.001 -- iid 0.0089 / 0.0009, real 0.0159 / 0.0018, surrogate 0.0097 / 0.0011 (Monte Carlo SE at 0.001: 0.00022).

**C. The rotation gate against the spurious rejection (M2-2); seed 31.** The same design, offer-level arrays, every
circular shift by FFT per mark.

```python
import numpy as np
from scipy import stats
rng = np.random.default_rng(31)
T, m, B = 750, 24, 21; nb = T // B
a, q_d, sig_eta, sig_eps, q_s, p_in, R = 0.03, 1 / 120, 0.30, 0.35, 1 / 60, 0.80, 4000
shifts = np.arange(63, T - 63 + 1); crit = stats.t.ppf(0.99, nb - 1)
def markov(q, n):
    sw = rng.random(n) < q; sw[0] = rng.random() < 0.5
    return np.where(np.cumsum(sw) % 2 == 0, 1.0, -1.0)
rej = gate = both = 0
for _ in range(R):
    d = (a * markov(q_d, T) + sig_eta * rng.standard_normal(T))[:, None] + sig_eps * rng.standard_normal((T, m))
    r = markov(q_s, T)
    s = np.where(rng.random((T, m)) < np.where(r > 0, p_in, 1 - p_in)[:, None], 1.0, -1.0)
    x = (s * d).mean(1); bm = x[:nb * B].reshape(nb, B).mean(1)
    t = bm.mean() / (bm.std(ddof=1) / np.sqrt(nb))
    cc = np.fft.irfft(np.conj(np.fft.rfft(s, axis=0)) * np.fft.rfft(d, axis=0), n=T, axis=0).sum(1) / (T * m)
    p = (1 + np.sum(cc[shifts] >= x.mean())) / (1 + len(shifts))
    rej += t > crit; gate += p <= 0.01; both += (t > crit) and (p <= 0.01)
print(rej / R, gate / R, both / R, both / max(rej, 1))
```

Printed: 0.0168, 0.0210, 0.0107, 0.64.

**D. The filter threshold (M2-5); seed 21 (inner-fold threshold), seed 22 (the final model's own).** The declared
objective and solver. Scores are compared on the linear scale `|z - z~|`, which ranks offers as `|p - p~|` does within a
model; between models with the same intercept the two scales differ by the same factor `p~ (1 - p~)`.

```python
import numpy as np
from scipy.optimize import minimize
rng = np.random.default_rng(21)
m, P = 20, 49; FOLD_TRAIN = (200, 450, 700); TEST, FINAL, JUDGED = 250, 950, 630
def make(n, beta):
    X = rng.standard_normal((n, m, P)); X[:, :, :P // 2] = X[:, :1, :P // 2] + 0.3 * X[:, :, :P // 2]
    X = (X - X.mean((0, 1))) / X.std((0, 1))
    y = (rng.random((n, m)) < 1 / (1 + np.exp(-(np.log(0.52 / 0.48) + X @ beta)))).astype(float)
    return X.reshape(-1, P), y.ravel(), np.repeat(np.arange(n), m)
def fit(X, y, sess, lam):
    w = 1.0 / (len(np.unique(sess)) * np.bincount(sess)[sess])
    def f(b):
        z = b[0] + X @ b[1:]; g = 1 / (1 + np.exp(-z)) - y
        return (w @ (np.logaddexp(0, z) - y * z) + 0.5 * lam * b[1:] @ b[1:],
                np.concatenate([[w @ g], X.T @ (w * g) + lam * b[1:]]))
    return minimize(f, np.zeros(P + 1), jac=True, method="L-BFGS-B", options={"gtol": 1e-10, "maxiter": 2000}).x
def centred_abs(b, Xtr, Xte):
    return np.abs(Xte @ b[1:] - np.median(Xtr @ b[1:]))
for label, beta in (("null", np.zeros(P)), ("weak", np.r_[np.zeros(P // 2), 0.06, 0.06, np.zeros(P - P // 2 - 2)])):
    for lam in (0.25, 25.0):
        oof = []
        for n in FOLD_TRAIN:
            Xtr, ytr, st = make(n, beta); Xte, _, _ = make(TEST, beta); oof.append(centred_abs(fit(Xtr, ytr, st, lam), Xtr, Xte))
        thr = np.percentile(np.concatenate(oof), 80)
        Xf, yf, sf = make(FINAL, beta); Xj, _, _ = make(JUDGED, beta); bf = fit(Xf, yf, sf, lam)
        print(label, lam, np.mean(centred_abs(bf, Xf, Xj) >= thr))
# seed 22, the final model's own training-sample 80th percentile instead:
rng = np.random.default_rng(22)
for lam in (0.25, 25.0):
    Xf, yf, sf = make(FINAL, np.zeros(P)); Xj, _, _ = make(JUDGED, np.zeros(P)); bf = fit(Xf, yf, sf, lam)
    print("own", lam, np.mean(centred_abs(bf, Xf, Xj) >= np.percentile(centred_abs(bf, Xf, Xf), 80)))
```

Printed: null 0.058 (lambda 0.25) and 0.023 (25); weak signal 0.067 and 0.047; own threshold 0.195 and 0.199.
