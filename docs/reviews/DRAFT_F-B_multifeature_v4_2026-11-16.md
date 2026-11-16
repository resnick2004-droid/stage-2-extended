# Red team, fourth read: `prereg/DRAFT_F-B_multifeature.md` version 4 (family B), 2026-11-16

**Target.** `prereg/DRAFT_F-B_multifeature.md` at e76ad23 (worktree `wt-scout`, branch `wt/wt-scout`, master's head),
with `tests/test_family_b_b2.py`, `tests/test_family_b_opening_range.py`, `tests/test_family_b_side_rule.py` and the
drafter's scratch checks `docs/reviews/scripts/family_b_drafter/*.py`.

**Read against.**
- `CHARTER.md` as amended (section 3's "a statistic calibrated to deliver that level").
- `DECISIONS.md` E-001..E-039. E-036 is the lead's ruling on the third read.
- `CLAUDE.md`, and the prereg-discipline and feature-rules skills.
- `extended/reader.py`, `extended/lift_bound.py`, `extended/features.py`, and `docs/research/calibration_2026-11-15.md`.
- The three earlier reviews.
- From Stage 2 (vendored, read-only):
  - `DECISIONS.md` D-278, D-281, D-580, D-588, D-590, D-592;
  - `scripts/s1_sided_coin.py`, `scripts/s3_latency.py`, `scripts/s3_event_kinds.py`;
  - `propedge/research/s1_sided_coin.py` and `s3_latency.py`;
  - `propedge/campaign/gate.py` and `lockstep.py`.

**What the brief held.** It named the parts that are new and asked whether each correction removes its defect and
whether the draft can now be pinned. It did not say what answer it expected. The draft's section 0.1 says every
finding is corrected. I treated that as the draft's claim, not as a prior.

**What I ran.**
- Nothing read a bar, the atlas, the store's manifest, Stage 2's result CSVs or NQ from 2026-07-17. Nothing ran the
  engine or touched the web.
- I ran the three family-B test files: 15 passed.
- I ran three synthetic scratch checks in one small process, with seeds fixed before running (the Appendix gives
  them). They are exploratory and select nothing.
- I read Stage 2's S1/S3 writers to see what their result files can hold. I did not read the files, which are not
  vendored.

## Verdict: **must be redrafted**

Most of the third review's corrections work:
- the per-row as-of rule is complete;
- C1-f's follow component is now centred correctly;
- `cons` is applied per component with B2's critical value;
- the calendar, the blocks and their df are right;
- the per-session values and the estimand match stage B;
- the scratch checks are in the tree;
- the identity behind M3-2 is disclosed and tested.

Two material defects remain, and each changes a declared rule.

- **M4-1.** The amplitude half of M3-1 is not fixed.
  - Part (b), "the follow lift Stage 2 recorded on 2024-2026", is not in the files the draft names. Stage 2's S1 and
    S3 lift sections cover the whole 2020-2026 window, at P-16's 150-tick stop and on P-16's offers. Their only split
    by span is campaign growth.
  - So the fallback (c), "three times (a)", governs every twin.
  - (a) is a *signed* "largest calendar-year lift" taken on the block where Stage 2 found the follow rules weakest
    (D-580 (5)). It can be near zero or negative, and the rule then returns an amplitude near zero. That is the
    failure M3-1 named.
  - Sections 12 and 17 also state the rule differently.
- **M4-2.** C2's routing depends on the pick's own outcomes, and not only "at second order".
  - Stage 2's `trade_day` walks each day trade by trade. It stops an account's day on the daily loss limit, the
    floor, `stop_day_on_win`/`stop_day_on_loss`, a pass or the consistency allowance.
  - Pair values cluster within a session.
  - On a toy with uninformative, session-persistent sides, the routed-trade mean of `s d` is +0.05 to +0.09 under the
    null. It is about 0 over all offers and about 0 at the coin-sided routing.
  - C2's B2 holds the routing fixed, so it cannot see a bias in the estimate.
  - The third review made the same incomplete argument (its m3-4).

| id | severity | finding (one line) |
|---|---|---|
| M4-1 | **MATERIAL** | C1-f's amplitude rule (§12, lines 571-583): (b) cannot be met (Stage 2's S1/S3 lift rows are 2020-2026 at 150 ticks on P-16's offers; the by-span rows are campaign growth; S3's L = 5 G3 never ran), so (c) = 3 x (a) always; (a) is signed, on the follow rules' weak years, and can give g* near 0. At half the judged amplitude the drafter's own check rejects 2.7-4.4 times the level. §12 and §17 disagree on whether 3(a) is always in the maximum |
| M4-2 | **MATERIAL** | C2 at design (i)'s routing (§13, lines 671-687): the routing selects on the same day's earlier outcomes (`lockstep.py:433-505`), and pair values cluster within sessions (calibration §2.1: 0.2-0.35). Toy: routed mean `s d` +0.050 to +0.089 under the null (replicate sd 0.005-0.007), about 0 over all offers and at the coin-sided routing. B2 calibrates the spread, not this bias. m3-4's reason is wrong |
| m4-1 | MINOR | The partialled reading (§13, lines 698-712) has five gaps. (1) It is pooled over alerts, so it mis-partials 10:05-10:25 and plants an artefact there. (2) The OR position is not partialled: the drafter's R-squared is 0.75-0.79. (3) Its critical values are unspecified. (4) The carrying-row sentence fires only at 95 %. (5) The partialled sides are neither hashed nor in `stage_C_sides`, and the coefficients are not in the pinned model's hash |
| m4-2 | MINOR | The persistence flag (§12, lines 615-617) is undefined (rolling or blocks? per session or per offer?). It mostly misses E-035 (6)'s own case: a quarter-long lean as large as the noise is flagged 15 % (rolling) or 39 % (blocks). The filter cells' selection persistence is not stated |
| m4-3 | MINOR | The confirmation by `t21w` (§16): the test it cites runs at 630 sessions and 0.01. At 126 and 252 sessions and 0.05, B2 holds pooled (0.050-0.054) but not per side series (up to 0.096-0.114). B2's inputs at the confirmation, and the critical value used for the months of data, are unspecified |
| m4-4 | MINOR | B2's follow component rides on the twin's side only. A model whose own lift follows an independent slow regime has a C1-f difference with up to twice B2's slow variance. Add a symmetric component, or name the gap |
| m4-5 | MINOR | B2's seeds `[20261965, j]` are not mapped to lines. C2's B2 runs after the judged outcomes, so an unmapped `j` is a choice still open after an outcome |
| m4-6 | MINOR | The bound arm's `e_by_rr` / `lb_by_rr` for design (i) and (ii) on the judged block are not defined (no statistic, level or blocks), yet they set C2's routing and the long-run gate floor (`gate.py:235-239, 279`) |
| n4-1 | NOTE | The C1-f test draws truth and null from the same process at the matched amplitude. It shows the principle and the two failures, not the declared construction |
| n4-2 | NOTE | "13 of the 37 are one value a day" (line 608): the draft's own table has 12 |
| n4-3 | NOTE | `lift_bound.bound` takes no critical-value override, so the line's reading needs a named, tested wrapper. The stage-A MDL at nominal critical values is a lower bound on the line's MDL |
| n4-4 | NOTE | §22 item 1's default "no family may read ... the half-hour's bars" conflicts in letter with the partialled reading and the twins, which read those bars |
| n4-5 | NOTE | The as-of rule's five offsets are redundant: `s - 61` and the day's first bar suffice |
| n4-6 | NOTE | e76ad23 cites E-040, which `DECISIONS.md` does not hold. §19's seed check omits family O's draft, which lists 20261960-69 as F-B's (no clash). §12's "What it cannot see" omits (c) |
| n4-7 | NOTE | Say that `lagged_day_sides` is called at the entry marks `t + 5`, and `day_sides` at `t`. Calling the former at `t` lags twice |

---

## The third review's findings: whether each correction works

| finding | corrected? | why |
|---|---|---|
| M3-1, the centring | **yes** | `(g_t - g*) f` has mean zero: a disagreeing offer gives `-2 (g_t - g*)`, whose expectation is 0. v3's "recentred by its replicate mean" is gone. The extended test shows the centred form holds at the matched amplitude, and that both v3 readings fail |
| M3-1, the amplitude | **no** | M4-1 |
| M3-2 | **yes, as ruled** | Disclosed: the identity is in §2 (c) and §7, and the R-squared test is in the tree. E-036's partialled reading is present, with gaps (m4-1) |
| Q-16 named | yes | `cons` is on every line, with each component's critical value the larger of nominal and B2. No line is two-sample: C1-d and C1-f are one-sample on the same offers. The wrapper and the MDL caveat are n4-3 |
| E-035 (6) | partly | The side's persistence is stated in words and flagged, but the flag is weak and undefined, and the filter is not covered (m4-2) |
| m3-1 | **yes** | Below: the rule is complete, and the test flags exactly the five rows of a 09:00-09:24 hole |
| m3-2 | yes | 609 sessions → `block_index` gives 29, 14 and 9 blocks (21, 43-44 and 67-68 sessions; df 28, 13, 8). One-sided t at 0.05/132 is 3.779, 4.371 and 5.268, against z = 3.368 (my arithmetic) |
| m3-3 | yes | `(S, N)` from `session_sums`, empty sessions zero, the per-offer mean `sum S / sum N` as at stage B |
| m3-4 | **stated, but its reason is wrong** | M4-2 |
| m3-5 | yes | The MDL at the training share at stage A and the judged share beside. K2 and the 4 % margin are on 2021-2023 |
| m3-6 | yes | Starts truncated at 2023-12-29, labelled |
| m3-7 | yes | Nine scripts, each with its printed output, synthetic, reading no file |
| n3-1..n3-6 | yes | Each in place. n3-6's consequence for `g*` is M4-1 |

---

## MATERIAL

### M4-1. C1-f's amplitude rule can collapse to the choice block's weak follow effect

**Where.**
- Section 0.1, line 57: "The amplitude is no smaller than the follow lift Stage 2 recorded on 2024-2026".
- Section 12, lines 571-583. `g_r*` is "the largest of" three parts:
  - (a) the twin's largest calendar-year lift on the choice block;
  - (b) the follow lift Stage 2 recorded for the twin on 2024-2026, from `s1_sided_coin.csv`, `s3_event_kinds.csv`
    and `s3_latency.csv`;
  - (c) "three times (a), fixed now, used where the result files hold no 2024-2026 per-offer lift for the twin at a
    comparable R".
- Section 17, line 857: "the largest of the choice block's yearly lift, Stage 2's recorded 2024-2026 lift and three
  times the former". This has no fallback condition.
- Section 5's pre-read row (line 278) and section 22 item 4 (lines 987-989).
- E-036's remedy: "no smaller than the follow lift Stage 2 itself recorded on 2024-2026 (D-580, D-588)".

**Evidence.**
- **What Stage 2's three files can hold.** I read the vendored writers, not the files.
  - `vendor/stage2/scripts/s1_sided_coin.py:355-377` writes section `lift`: stage 1's test over every walked session,
    one `mean_lift` per (rule, sign, R) for 2020-2026.
  - The only sections split by span are `g3` (lines 479-510). They hold campaign `growth_on_required` for 2020-2023
    and for 2024-2026, not a per-offer lift.
  - `scripts/s3_latency.py:344-371` writes its `lift` rows with `"sessions": len(sess)`, again the whole window, at
    L = 0 and L = 5. Its `g3` rows were never written, because G1 failed first (D-592).
  - `s3_event_kinds.py` has no split by span outside its campaign guard.
  - Every figure in all three files is at `STOP_TICKS = 150` (`propedge/research/s1_sided_coin.py:55`) on P-16's
    news-safe offers. The family trades 50 and 100 ticks at 10:10-15:05.
  - The decision rows match the code. D-580 (5) splits campaign growth by span; D-588 and D-592 record the per-offer
    lift for the whole window.
  - **No 2024-2026 per-offer lift exists, for any twin, at any R or stop.** Vendoring the files (§22 item 4) adds
    nothing to (b).
- **So (c) governs every twin, and (c) inherits (a).**
  - (a) is the twin's *largest* calendar-year lift: a signed maximum. B2's own drift amplitude `a*` uses "the largest
    absolute calendar-year mean" (line 565).
  - Stage 2's rows say that on 2020-2023 the followed rules grew less than P-16 (D-580 (5)), so the twins' lift there
    was weak or negative, at least on P-16's offers.
  - Two cases follow:
    - every choice year's lift is at or below 0: then `max(a, 3a) = a`, a small negative number, and the two-state
      component's amplitude is `|a|`, near zero;
    - the largest year is small and positive: then `3a` is small.
  - Either way the amplitude reflects the block where the effect was absent, which M3-1 said it must not do.
- **What a small amplitude costs, on the draft's own evidence.** At C1-f's boundary null, with B2 correctly centred:
  - at half the judged amplitude, `m31_cons.py` prints 0.0272 and 0.0437 at 0.01 (2.7 and 4.4 times the level);
  - the third review's check C2 gives 0.037 at half and 0.084 at a third.

**The failure it allows.** This is M3-1's failure, unchanged.
- A pick that is itself a follow rule of another horizon or window beats twins whose slow lift sat low in part of the
  judged block.
- C1-f, the line written to refuse it, runs at several times its level, because its amplitude came from 2020-2023.
- The family then reports "a direction beyond each known follow effect" that is the follow effect.

**Remedy (changes a declared rule).**
1. **Add (d):** the twin's largest *absolute* calendar-year lift on the judged block (2024, 2025, 2026 to 07-16), at
   the pick's offers and bracket.
   - Read it under `stage_C_judgement`.
   - Take C1-f's critical value as the maximum of three values: the nominal one, B2's at the pre-judgement `g*`, and
     B2's at `max(g*, (d))`.
   - This can only raise the critical value, so it cannot raise C1-f's false-pass rate above what the rule as drafted
     gives. It delivers section 0.1's "no smaller than the judged amplitude" directly.
   - In section 13's order, C1-f's B2 then runs after step 3. C1 and C1-d keep theirs before it.
2. **Make (a) absolute**, as `a*` is: the largest |calendar-year lift|. Better still, take the largest absolute
   deviation of a year's lift from the block's mean, plus |that mean|.
3. **Drop (b) as written.** Alternatively, redefine it as Stage 2's whole-window lift at the same R (150 ticks, P-16's
   offers, as recorded), disclosed as another population and used as a floor only. Then correct sections 0.1, 5, 12,
   17 and 22 item 4.
4. **Make sections 12 and 17 state one rule.**
5. **Extend `tests/test_family_b_b2.py`** with a choice-block amplitude near 0 and a judged one above it. The rule with
   (d) should hold the level; the (a)/(c) rule should not. This takes seconds.

### M4-2. C2's routing selects on the pick's own same-day outcomes

**Where.**
- Section 13, lines 671-687: the routing of design (i) on the bound arm; `v_j = mean_dv(p(j)) x s_i(j) x d_i(j)(R_j)`;
  `cons` on the `v_j`.
- Lines 683-686: "It does so at second order only: the gate draws each path's days independently ... so a trade's
  place depends on its own day's outcome only where that day recurs in a path."
- Section 12, lines 586-587: C2's B2 "with the realised routing's weights held fixed".
- Section 0.1, m3-4 (line 64). Section 16, lines 811-812 (the confirmation's C2 uses stage C's per-place shares).

**Evidence.**
- **The engine.** `vendor/stage2/propedge/campaign/lockstep.py:433-505` (and its funded counterpart at 670-760) walks
  an account's day slot by slot with `day_pnl`.
  - The draw is told `room = min(cushion, dll + day_pnl)` (line 455).
  - The day ends on any of: the daily loss limit (line 496), the floor, `stop_day_on_win` or `stop_day_on_loss`
    (498-501), a pass under `need_aware`, or a used consistency allowance.
  - So which of a day's later offers become trades, and how they are settled, depend on that day's earlier outcomes.
  - The gate's default of one independent draw a day (`gate.py:211-212`) removes only the route across days.
- **The outcomes it selects on are correlated.** The calibration note §2.1 (line 122) finds "strong clustering within
  a session, with an intra-session correlation of about 0.2 to 0.35 across R" in P-16's pair values. A model with
  day-level features leans one way within a session (section 12, lines 607-610).
- **Toy (check H).**
  - The design:
    - 609 sessions of 24 offers;
    - pair values with intra-session correlation ρ, sd 0.3;
    - **uninformative** sides, constant within a session;
    - a router that takes offers in order and ends a session's trading once its cumulative `s d` reaches -0.6 or -0.9
      (two or three losses);
    - 400 replicates.

  | ρ | stop | routed mean `s d` (sd over replicates) | all offers | at the coin-sided routing |
  |---|---|---|---|---|
  | 0 | 0.6 / 0.9 | -0.0003 / -0.0001 | -0.0004 / 0.0000 | -0.0003 / +0.0000 |
  | 0.20 | 0.6 / 0.9 | **+0.061 / +0.050** (0.005, 0.006) | +0.0001 / -0.0002 | -0.0000 / -0.0001 |
  | 0.35 | 0.6 / 0.9 | **+0.089 / +0.075** (0.007, 0.006) | -0.0005 / +0.0002 | -0.0002 / +0.0002 |

  - With sides drawn independently by offer (ρ 0.35, stop 0.9) the routed mean is -0.0001.
  - At `p14`'s `mean_dv` of 225-1,426 dollars a place, the null's routed mean is tens of dollars a trade.
  - The toy overstates the real case (every offer taken; sides fully constant within the day). The point is the kind
    of effect, not its size: it is first order, and its sign depends on the protocol. A loss limit favours a side that
    persists within the day; `stop_day_on_win`, or seats freed sooner after quick stops, can reverse the sign.
- **Why B2 cannot see it.** C2's B2 holds the realised routing fixed and replaces `d` with choice-block sessions, which
  are independent of that routing. Its null has mean zero, while the real estimate carries the selection. B2
  calibrates the spread of the estimate, not its bias.
- **The red team's own error.** The third review's m3-4 gave the same "second order" argument. The draft adopted it.

**The failure it allows.**
- A pick with a real but small lift passes C1, which reads every offer and is unbiased.
- C2 at design (i)'s routing then reads that lift plus the routing's selection on the pick's own outcomes. It clears
  $500 a year where the lift alone, priced at a routing independent of the pick's outcomes, would not.
- The pick is CARRIED on "worth at least $500 a year at the family-level bound", and that is false.
- The confirmation's C2 uses stage C's per-place shares from the same routing, so it inherits the error.

**Remedy (changes a declared rule).**
- Make C2's line the bound at **design (ii)'s coin-sided routing**, which the draft already computes beside (lines
  686-687). Check H puts its selection at about 0, because the coin's sides are independent of the pick's.
  Alternatively, make the line the lesser of the two bounds.
- Run B2 at the routing the line uses. Report design (i)'s pricing beside.
- Correct the coupling text in sections 0.1, 12 and 13.
- Price the confirmation's C2 with design (ii)'s shares.
- The real size can be measured on the choice block ("What I could not check", item 1). The rule does not need to
  wait for that.

---

## MINOR

- **m4-1. The partialled reading** (section 13, lines 698-712; section 17, line 862). It identifies the linear
  net-move route approximately, which is what E-036 asked. Five gaps remain.
  - **Pooled over alerts.** At 10:05-10:25 the model's net-move term `(C[t-61] - C[08:29]) / atr14` is the 30-minute
    range's net move plus part of 09:00-09:29. It equals the 60-minute range's only from 10:30.
    - For a random walk, its projection at 10:05 is `OR30 + (1/6)(OR60 - OR30)`; from 10:30 it is `OR60`.
    - One regression over 60 alerts fits the 55 later ones. At the early alerts the residual keeps
      `-beta (C[09:29] - C[09:04])`, a fade of a move the model never faded.
    - Remedy: fit per alert (60 OLS fits on the choice block), or interact the regressors with alert indicators.
  - **Position is not partialled.**
    - The closed branch's rules are breakouts, whose state is the position in the range.
    - The drafter's `m32_r2.py` prints position R-squared 0.79, 0.76 and 0.75 at 10:05, 10:30 and 12:00 on a
      synthetic year (in sample, 40 columns, 226 rows).
    - Remedy: add the 30-minute range's position at the alert as a fourth regressor.
    - T-14 (lines 949-950) plants only a net-move drift. Plant a breakout-follow effect too.
  - **Unspecified critical values** for "its lift ... by `cons` at the family's level and at 0.05": nominal, or B2
    conditional on the partialled sides? Say which.
  - **The trigger** fires only when the 95 % bound fails. A pass whose partialled lift fails at the family level but
    clears 0.05 is carried with no sentence. Trigger at both levels and say which failed.
  - **Not sealed.**
    - The partialled sides and the since-open rule's sides are not in `stage_C_sides`' list (lines 252-254), and they
      are not hashed before any outcome.
    - The OLS coefficients and `median(z_res)` are not in section 9's hashed model (lines 477-481) or in T-3's
      invariance.
    - "Median" is unweighted here, but `p~` is session-weighted.
- **m4-2. The persistence flag** (lines 605-617, 863; E-035 (6)).
  - **Undefined.** The draft does not say whether the 126-session mean side's variance is rolling or over 4
    non-overlapping blocks, whether the mean side is per session or per offer, or what a filter pick's empty sessions
    count as.
  - **Insensitive (check G).** On 609 sessions, with per-session mean side = λ x a two-state lean + noise of sd 0.3:

    | process | flagged, rolling | flagged, blocks | median ratio |
    |---|---|---|---|
    | iid | 0.000 | 0.021 | 0.12 / 0.14 |
    | quarter-long lean (switch 1/63), λ = 0.3 | 0.154 | 0.385 | 0.33 / 0.41 |
    | quarter-long lean, λ = 0.5 | 0.170 | 0.389 | 0.33 / 0.41 |
    | year-long lean (1/250), λ = 0.3 | 0.473 | 0.576 | 0.48 / 0.61 |

    - E-035 (6)'s own warning case, the quarter-long regime, mostly goes unflagged.
  - **The filter is not covered.** E-035 (6) is written about filters. The `filter` cells' selection, `|p - p~|` at
    or above the 80th percentile, can cluster in volatility regimes, and its persistence is neither stated nor
    flagged. The stage-A MDL "at its training share" does not say how the share is laid on the nulls: random thinning
    would ignore the clustering.
  - **Remedy.**
    - Define the computation.
    - Report the ratio beside its iid value (1/6) and a simulated band for a quarter-long lean, with the lag-1, 5, 21
      and 63 autocorrelations of the per-session mean side.
    - Do the same for the filter's per-session firing share.
    - Compute a filter cell's MDL with the out-of-fold selection's session pattern.
- **m4-3. The confirmation by `t21w`** (section 16, lines 805-825).
  - **The cited test does not test it.** "That form holds the level within Monte Carlo error
    (`tests/test_family_b_b2.py`)" cites runs at 630 sessions and 0.01 (lines 44, 47, 120-136).
  - **Check E**, on the test's own designs, with B2 as declared, `t21w`, one-sided 0.05, 12 side series x 4,000
    replicates:
    - at 126 sessions: nominal 0.064 and 0.068; B2 pooled 0.053 and 0.054; worst series 0.076 and 0.096;
    - at 252 sessions: B2 pooled 0.050 and 0.050; worst series 0.079 and 0.114.
    - So the form is about at level pooled, and 1.5-2.3 times it for some side series: the cases where the choice
      block's `a*` falls short of the drift.
  - **Unspecified inputs.**
    - Which pair values B2 resamples at the confirmation: the choice block's, or 2020-2026's once the judged block
      has been read.
    - Which `a*` and `g*` it uses. The judged block's yearly values will then be known, and they can only raise the
      critical value.
    - Which critical value the months-of-data power uses (lines 819-825). B2's needs the window's sides, which do not
      exist when the months are written.
  - **Remedy.** Declare these three inputs, and add the 126-session, 0.05 case to the test.
- **m4-4. B2's follow component spans the twin's regime only** (lines 567-570).
  - C1-f's per-session value is the model's lift minus the twin's. B2 adds `(g_t - g*) f`, so the model's share of
    the slow variation enters only through its agreement with the twin: `2 q_t (g_t - g*)`.
  - If the model's lift follows its own slow regime `h_t`, the slow part is `2 q (h_t - g_t)`. That is the third
    review's failure case: a follow rule of another horizon "tracking the same regimes with a different profile".
    With `h` and `g` independent and of equal amplitude, this has twice B2's variance.
  - **Remedy.** Add `(h_t - g*) s_i`, with `h_t` an independent two-state process at the same amplitude. This is
    conservative if the regimes coincide. Otherwise, name the gap under "What it cannot see".
- **m4-5. B2's seed map** (lines 584 and 905). `[20261965, j]` gives no line for each `j`. C2's B2 runs after the
  judged outcomes (step 5), so for C2 an unmapped `j` is a choice still open after an outcome.
  - **Remedy.** Fix the map: 0 C1, 1 C1-d, 2-4 C1-f (`lnbar1x4`, `lbrk5`, `mom15`), 5 C2, and 6 for the partialled
    reading if B2 is used there.
- **m4-6. The bound arm's edges** (lines 672-673 and 691-692).
  - On the bound arm, Stage 2's gate shifts every trade by `lb_by_rr - e_by_rr` (`gate.py:235-239, 279`).
  - For design (i), and for design (ii) on the judged block, the draft does not define the per-R edges or their lower
    bounds: no statistic, level or blocks.
  - They set C2's routing and the long-run gate floor, and they are computed from judged outcomes.
  - **Remedy.** Declare them. Examples: each design's judged per-R mean net R and its lower bound by Stage 2's D-145
    statistic at its level, or by `cons` at the family level.

## NOTE

- **n4-1.** The C1-f test (`test_family_b_b2.py:174-183`) draws the null from the same process as the truth at the
  matched amplitude. It shows the principle and the two failures (half amplitude, v3's recentring). It does not test
  the declared construction: there is no choice-block resampling, no real `(s - f)` weights, and the disagreement `q`
  is constant. At the matched amplitude the drafter's `m31_cons.py` rejects 0.0027-0.0042 at 0.01: conservative, at a
  cost in power.
- **n4-2.** Line 608 says 13 of the 37 features are one value a day. The table's `per` column has 12:
  - `range_on`, `gap`, `atr_ratio`, `range_prior`;
  - `ret_prior`, `ret_5d`, `ret_20d`;
  - `dow`, `bls_day`, `bls_major`, `days_to_fomc`, `days_since_fomc`.
- **n4-3.** `lift_bound.bound` takes no critical-value override. Lines 658-660's "with each component's critical value
  replaced" needs a wrapper. Name it in section 20 and test it: a known critical value above nominal must lower the
  bound. The stage-A MDL (lines 440-453) uses `mdl_draws("cons")` at nominal critical values. That is a lower bound on
  the line's MDL once B2 raises them, so the screen rule leans against declaring a screen. Say so.
- **n4-4.** Section 22 item 1 (lines 978-980) reads "whether any family may read ... the half-hour's bars. Default:
  no".
  - In letter, that conflicts with the partialled reading, which reads those bars on both blocks.
  - It also conflicts with `lbrk5` and `lnbar1x4`, whose "most recent event" can lie in the half-hour.
  - E-024 (5)'s default is about inputs at the decision time. Write "no used feature reads, and no entry lies in".
- **n4-5.** As-of stamps never decrease, so `s - 61` and the day's first bar cover every as-of read and every 1-minute
  change in the 60-minute windows. The five offsets are redundant but harmless.
- **n4-6.** Three small gaps:
  - The merge e76ad23 cites E-040; `DECISIONS.md` ends at E-039.
  - Section 19's check names family R's draft but not family O's. Family O's also lists 20261960-69 as F-B's
    (`DRAFT_F-O_opening_timing.md:886`), so there is no clash.
  - Section 12's "What it cannot see" names (a) and (b) but not (c).
- **n4-7.** `lagged_day_sides` reads `day_sides` at `m - L` (`s3_latency.py:153-160`). Say that it is called at the
  entry marks `m = t + 5`, so its side is the L = 0 side at `t`. Called at `t`, it would lag twice. `day_sides` is
  called at `t`, where its "bars j <= t" are bars ending at or before `t`.

---

## What I tried that found nothing

- **The per-row as-of rule (m3-1).** I re-read `features.py:452-566`. The day's reads of the 37 features are:
  - as-of closes `Cff[:, s-1-w]` for w in {0, 5, 15, 30, 60}, and `Cff[:, s-31]`;
  - 1-minute changes `dC` over `[s-w, s)`, each against the as-of close of the slot before, so the earliest is as of
    `s - 61`;
  - window sums of actual bars (`H`, `L`, `C`, `V`) stamped at or after `s - 60`;
  - the overnight `[:930)` and `Cff[:, 929]`;
  - `O_day`.

  Because as-of stamps never decrease, checking `s - 61` and the first bar covers every one of these. The test's
  09:00-09:24 hole flags exactly 10:05-10:25, and replacing the half-hour moves a used feature only on those rows.
  Prior-day reads are allowed by definition.
- **Look-ahead in the new parts.**
  - The partialled reading's regressors read bars stamped no later than 09:29, so they are closed at every alert from
    10:05.
  - The persistence measures read sides only.
  - B2 reads judged sides and choice-block pair values only.
  - The twins' `day_sides` reads bars ending at or before the mark (`s1_sided_coin.py:179-182`).
- **Leakage across blocks.** The partialling OLS is fitted on the choice block. B2's `a*` and (a) come from the choice
  block, and so does the MDL's dispersion. Stage 2's pre-read can only raise a critical value. No new input reads the
  judged block for a choice.
- **C1-f's centring algebra.** In the null, the model's lift is `(1 - 2q)(g_t - g*)` and the twin's is `g_t - g*`.
  Their difference has mean zero.
- **No line is two-sample.** C1-d (`(s - s_bar) d`, with `s_bar` fixed given the sides) and C1-f (`(s - f) d`, with
  `f` = 0 a tie) are one-sample sums over the same offers.
- **`cons` per component.** Each component is tested at the larger of its nominal value and B2's own quantile, so the
  intersection's size is no larger than that of any one component. The three-line intersection-union for C1-f holds
  the level.
- **Counts and arithmetic.** 12 cells, 28 searched configurations, 41 columns, 60 alerts. At 609 sessions: 29, 14 and 9
  blocks. One-sided t at 0.05/132 is 3.779, 4.371 and 5.268, against z 3.368.
- **The `Judged-block reads:` line** (line 249). It matches `reader.py:116`'s `DECLARED_LINE` and yields the four
  purposes. No other line of the draft matches, and no purpose holds a word in `CHOICE_WORDS`.
- **Seeds.** `grep -rIowl -E "2026196[0-9]"` finds:
  - this draft, its three tests and `m32_r2.py`;
  - `DECISIONS.md` and the v3 review;
  - family O's and family R's drafts, both of which list the block as F-B's.

  The drafter's other scratch seeds (51, 91, 95-97) are exploratory. The tests' sub-seeds match section 19.
- **The tests.** 15 passed.
- **The scratch checks (m3-7).** All nine are synthetic, print their output and read no file.
- **Selection after the fact.** Several new constants have no outside source: "three times", the flag's 1/2, the 0.9
  R-squared line and the three regressors. None could have been chosen after a family-B outcome: no bar has been read
  for the family.

## What I could not check

1. **The real size and sign of C2's coupling (M4-2).**
   - The experiment:
     - on the choice block's out-of-fold years (2021-2023, a choice read), at each surviving cell's out-of-fold sides,
       run design (i)'s and design (ii)'s gate campaigns (100 paths, the bound arm);
     - compare the routed-trade mean of `s d` with the all-offer mean;
     - repeat for about 50 replicates whose pair values are resampled choice sessions (B2's construction), so the sides
       carry no information.
   - Cost: heavy, dozens of campaigns, hours under the lock.
   - A light first step: the intra-session correlation of the family's pair values and of `s d` at the out-of-fold
     sides (minutes).
2. **Whether Stage 2's S1/S3 CSVs hold a per-year field.** I read the writers, not the files. The vendoring row
   settles it. M4-1's remedy does not depend on the answer.
3. **The OR position's recoverability on real bars.** My figures are synthetic only.
4. **B2 at the family level** (heavy, section 20 item 8), and the real size of the twins' year-to-year swing.
5. **Q-55's clean rerun of the calibration.** I also did not check the judged session count against the store's
   `day_list`.

---

## Appendix: the scratch checks (exploratory, synthetic, seeds fixed before running)

One process. `markov`, `tstat`, `stationary_idx`, `T.REVIEW`, `T.SLOWER`, `T.P_IN`, `T.S_ETA` and `T.S_EPS` are
`tests/test_family_b_b2.py`'s, unchanged.

```python
import numpy as np
from scipy import stats
import test_family_b_b2 as T

# E: the confirmation's form -- t21w (equal blocks; identical to t21w at equal N), B2 as declared, one-sided alpha
def case_e(seed, TJ, a, q_d, q_s, alpha, R=4000, M=24, TC=1000):
    rng = np.random.default_rng(seed)
    offers = np.where(rng.random((TJ, M)) < np.where(T.markov(rng, q_s, 1, TJ)[0] > 0, T.P_IN, 1 - T.P_IN)[:, None], 1, -1)
    A = offers.mean(1); noise = lambda: T.S_EPS / np.sqrt(M) * rng.standard_normal((R, TJ))
    true_x = A * (a * T.markov(rng, q_d, R, TJ) + T.S_ETA * rng.standard_normal((R, TJ))) + noise()
    choice = (a * T.markov(rng, q_d, 1, TC) + T.S_ETA * rng.standard_normal((1, TC)))[0]
    a_star = np.max(np.abs(choice[:1000].reshape(4, 250).mean(1)))
    d = choice[T.stationary_idx(rng, R, TJ, TC, 63)]; d = d - d.mean(1, keepdims=True) + a_star * T.markov(rng, 1 / 250, R, TJ)
    t_true, nb = T.tstat(true_x, 21); t_b2, _ = T.tstat(A * d + noise(), 21)
    nominal = stats.t.ppf(1 - alpha, nb - 1); crit = max(nominal, float(np.quantile(t_b2, 1 - alpha)))
    return np.mean(t_true > nominal), np.mean(t_true > crit), crit / nominal
# seeds [7401, TJ, j, 0 (REVIEW) or 1 (SLOWER)], j = 0..11; TJ in (126, 252); alpha 0.05

# G: the flag -- per-session mean side m = lam * markov(q) + N(0, 0.3^2), 609 sessions, 4,000 reps, seeds
# [7501, int(10 lam), round(1/q)]; ratio = var(126-session means) / var(21-session means), rolling (overlapping
# windows) and non-overlapping blocks (ddof 1); flagged if > 0.5

# H: C2's coupling -- d = 0.3 (sqrt(rho) z_session + sqrt(1 - rho) e_offer), 609 x 24; sides +-1 constant within a
# session (or iid by offer), uninformative; a router takes offers in order and stops a session once the cumulative
# s d <= -stop; the coin-sided router stops on s' d (s' iid) and the value is read at the model's s d; 400 reps,
# seeds [7601, int(100 rho), int(10 stop)] ([7601, 99, 9] for iid sides)
```

Printed:

```
E: t21w + B2 at the confirmation's length, one-sided 0.05 (12 judged side series each, 4,000 reps)
  126 sessions (6 blocks)    REVIEW nominal 0.0640 (max 0.0845) | B2 0.0529 (max 0.0755) | crit/nominal 1.00..1.30
  126 sessions (6 blocks)    SLOWER nominal 0.0678 (max 0.0960) | B2 0.0537 (max 0.0960) | crit/nominal 1.00..1.43
  252 sessions (12 blocks)   REVIEW nominal 0.0651 (max 0.0862) | B2 0.0502 (max 0.0785) | crit/nominal 1.00..1.39
  252 sessions (12 blocks)   SLOWER nominal 0.0889 (max 0.1308) | B2 0.0504 (max 0.1135) | crit/nominal 1.03..1.73
G: flag (rolling) / (non-overlapping) / median ratios
  lam 0.0           : 0.000 / 0.021 ; 0.12 / 0.14
  lam 0.1 q 1/63    : 0.051 / 0.234 ; 0.25 / 0.31
  lam 0.2 q 1/63    : 0.132 / 0.357 ; 0.32 / 0.39
  lam 0.3 q 1/63    : 0.154 / 0.385 ; 0.33 / 0.41
  lam 0.3 q 1/126   : 0.379 / 0.566 ; 0.44 / 0.57
  lam 0.3 q 1/250   : 0.473 / 0.576 ; 0.48 / 0.61
  lam 0.5 q 1/63    : 0.170 / 0.389 ; 0.33 / 0.41
H: routed mean s d (sd over reps, routed share) | all offers | at the coin-sided routing
  rho 0.00 stop 0.6: -0.00034 (0.00303, 0.61) | -0.00038 | -0.00034
  rho 0.00 stop 0.9: -0.00008 (0.00300, 0.74) | -0.00000 | +0.00004
  rho 0.20 stop 0.6: +0.06139 (0.00534, 0.61) | +0.00007 | -0.00003
  rho 0.20 stop 0.9: +0.04988 (0.00558, 0.70) | -0.00024 | -0.00005
  rho 0.35 stop 0.6: +0.08921 (0.00659, 0.61) | -0.00046 | -0.00021
  rho 0.35 stop 0.9: +0.07502 (0.00619, 0.69) | +0.00018 | +0.00024
  sides iid by offer, rho 0.35 stop 0.9: routed -0.00014 (0.00281) | all -0.00002
```
