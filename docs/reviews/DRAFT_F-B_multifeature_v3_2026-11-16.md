# Red team, third read: `prereg/DRAFT_F-B_multifeature.md` version 3 (family B), 2026-11-16

**Target.** `prereg/DRAFT_F-B_multifeature.md` at 41cf4d0 (worktree `wt-scout`, branch `wt/wt-scout`), with
`tests/test_family_b_opening_range.py`, `tests/test_family_b_b2.py`, `tests/test_family_b_side_rule.py` and
`extended/features.py`. All five are byte-identical on master 210ee33.

**Read against.**
- `CHARTER.md` as amended. Master's change to section 4 (the allowance-capped realised risk, E-032) touches only K3, which this draft reports.
- `DECISIONS.md` E-001..E-031, and E-032 from master.
- `CLAUDE.md`, and the feature-rules and prereg-discipline skills.
- `extended/reader.py`.
- The two earlier reviews.
- `docs/audits/phase0/D_protocol.md` 1.2.
- From Stage 2: `vendor/stage2/DECISIONS.md` D-275..D-281; `propedge/campaign/gate.py`; `propedge/research/atlas_local.py`; `results/u_value_map.csv`, `u_hours.csv` and `rc_width_screen.csv` (the side-free rows the draft cites); `config/sources/fomc_*.csv`.
- `config/calendar_early_closes.csv` (pinned, E-029).

**What the brief held.** It named the parts that are new and asked me to judge each correction independently. It did
not say what answer it expected. E-030 states that the corrections hold, and I treated that as the target's claim, not
as a prior.

**What I ran.**
- Nothing read a bar, the atlas, the store's manifest or NQ from 2026-07-17. Nothing ran the engine or touched the web.
- I ran the three family-B test files: 10 passed.
- I ran four synthetic scratch checks, one small process at a time, with seeds fixed before running (the Appendix gives each one). They are exploratory and select nothing.
- I counted the judged block's sessions from the pinned calendars, not from the bars.

## Verdict: **must be redrafted**

Most of the second review's corrections work.
- **Bar reads.** At every alert from 10:05, no used feature reads a bar stamped 08:30-08:59 of the day, when the bars are complete. 10:05 is the earliest alert for which that holds.
- **B2 for C1.** Stage B2's rule for the pass line holds the 0.01 level over 24 choice-block realisations of both of the test's designs, not just the test's three.
- **Other corrections.** C2 is at the family-level bound in every section. The 37.5-point stop is dropped and the cutoff is per year. Each filter threshold is its model's own. The `Judged-block reads:` line parses to the four purposes.

Two material defects remain. The first changes a declared rule.

- **M3-1.** Stage B2's slow follow component for C1-f does not hold C1-f's level. The phrase "recentred by its replicate mean" either makes the statistic identically zero or recentres it in the wrong place. Its amplitude also comes from the choice block, where Stage 2's own rows say the follow effect was weakest. `tests/test_family_b_b2.py` tests only C1.
- **M3-2.** The opening range's net move is still in the model. It is not in any single feature, but it is in a linear combination of three: at 10:30, `d_pdc - gap - ret_60` equals the 60-minute range's net move, bit for bit apart from the opening tick. Section 2 (c) claims that "no feature can compute ... the net move from the open of ... any opening range ... 60 minutes", and E-030's "no ruling is needed" rests on that claim. A linear model can compute it exactly.

| id | severity | finding (one line) |
|---|---|---|
| M3-1 | **MATERIAL** | C1-f's B2: "recentred by its replicate mean" makes the statistic identically 0 (read per replicate) or rejects about 3 times the level at the boundary null (read across replicates; synthetic: 0.030 at 0.01). Its amplitude `g_r*` comes from 2020-2023, where D-580 and D-588 put the follow effect weakest; at half or a third of the judged amplitude, even correct centring rejects 0.037-0.084 at 0.01. The B2 test covers only C1 |
| M3-2 | **MATERIAL** | `d_pdc - gap - ret_60` = `(C[t-61] - C[08:29]) / atr14` exactly, at every alert. At 10:30 that is the 60-minute opening range's net move (synthetic: correlation 1.000, at most 0.003 ATR apart); at 10:05 it correlates 0.966 with the 30-minute range's. Section 2 (c)'s claim is true per feature and false for the model, and the opening-range test checks single features only. ORB6's scope included the gap and entries to 11:35 (D-278) |
| m3-1 | MINOR | The as-of fallback is guarded only at 10:05. At 10:05 + 5k, `ret_60` and `rv_60` read the half-hour if no bar 09:00..09:04+5k exists, and `ret_day` reads it on a day whose first bar is in the half-hour. The invariance test never meets such a gap (synthetic RTH bars miss 0.1 % of minutes at random) |
| m3-2 | MINOR | The pinned calendars give about 609 judged sessions: 9 blocks of 63 (8 degrees of freedom), with about 42 sessions in no block. The draft says "about 630" and "about 10 blocks, about 9 degrees of freedom", and declares no rule for the remainder. One-sided t at 0.05/132 is 5.27 at 8 df against 4.98 at 9 |
| m3-3 | MINOR | "The line's per-session values" is undefined: offer- or session-weighted, and what happens to a session with no filtered offers. Stage B's statistic is the offer mean |
| m3-4 | MINOR | C2's B2 needs the campaign's routing, which `stage_C_campaign` produces after `stage_C_judgement`. Section 13's order (sides, B2, judgement, campaign) cannot hold for C2, and C2's fixed weights depend on outcomes |
| m3-5 | MINOR | `filter` cells: stage A cannot compute an MDL "on the judged share". K2 and the 4 % eligibility margin are undefined for 2020, which has no out-of-fold filter |
| m3-6 | MINOR | The scorecard's "2021-2023 starts ... (a choice-block read)": journeys from 2023 starts run into 2024 (P to month 3, the journey variables to month 12). Which sides they carry there, and under which purpose, is unstated |
| m3-7 | MINOR | The drafter's check of the second review's resampling remedies is "recorded" (section 12; commit 780f6da), but no file in the tree holds its code or output |
| n3-1 | NOTE | The reader cannot enforce `stage_C_sides`'s "bars up to each alert" or "hashed before any outcome": it returns whole sessions. The shift tests and the runner's order enforce them; the ledger's timestamps record the order |
| n3-2 | NOTE | Power: at 8 df the one-sided t at 0.05/132 is 5.27 (z = 3.37), so the family is very likely a screen. Section 3 says so; give the ratio as soon as Q-16 is merged |
| n3-3 | NOTE | Stale text: section 2 (c)'s last bullet and section 22 items 4 and 5 are done by E-030 and E-031 (1) |
| n3-4 | NOTE | The prior-session features on the day after a 12:00 holiday halt read that partial session as "the prior RTH". This is a definition, not look-ahead; say so |
| n3-5 | NOTE | E-029's pinned calendar now makes scheduled early closes known in advance. Section 5's n-4 ("known from the day's own last bar") can cite it, leaving only defect days |
| n3-6 | NOTE | B2's drift amplitude `a*` from 2020-2023 is probably conservative, because those years include 2020's crash and rebound and 2022's fall. The same choice is the anti-conservative one for `g_r*` (M3-1) |

---

## The second review's findings: whether each correction works

| finding | corrected? | why |
|---|---|---|
| M2-1 | **in its declared criterion, not in its stated substance** | `features.py:512-566`: at slot s >= 1025 (10:05), every used feature reads `Cff[:, s-1]`, `Cff[:, s-1-w]` for w <= 60 (09:04 at the earliest), windows `[s-60, s)`, the overnight `[:930)`, or earlier sessions. The test passes. But a linear combination of three used features recovers the range's net move (M3-2), and the fallback is guarded at 10:05 only (m3-1) |
| M2-2 | **for C1, yes; for C1-f, no** | Check B: at 0.01, pooled over 24 realisations, the rejection rate is 0.0079 on the review's design and 0.0076 on the slower one; per case at most 0.017 and 0.0135. C1-f's slow follow component fails (M3-1). C2's B2 cannot run where section 13 places it (m3-4) |
| M2-3 | yes | Sections 0 (line 37), 13 (lines 598-601) and 17 (line 757) say the family-level bound. The confirmation's 95 % matches its registered 0.05 |
| M2-4 | yes | 37.5 points dropped on a disclosed, side-free pre-read; the cutoff is per mark and per choice year at every table R (lines 159-162); the 25-point expectation is stated. The 4 % margin is on R in {1, 1.5, 3} and the floor is at "every offered R". The unresolved share rises with R, so R = 3 binds both |
| M2-5 | yes | Each model's own session-weighted training 80th percentile, pinned with it. The second review's synthetic check gave about 0.20 passing. MDL timing: m3-5 |
| m2-1 | yes | The join assertion is refusing; T-14 (6) plants the misaligned join |
| m2-2 | yes | No tolerance, no pretest; the lengths are mapped; the pinned model's sides are used |
| m2-3 | in form | Said; for the ordering, m3-4 |
| m2-4 | yes | E-031 (2); the twins' model is fitted on the choice block |
| m2-5 | partly | Judged starts, labelled. The 2021-2023 starts straddle the boundary (m3-6) |
| m2-6, m2-7 | yes | Centred draws; the pre-read rows exist at the lines cited (`rc_width_screen.csv:798, 803`, `u_hours.csv:175-208`) |
| n2-1..n2-7 | yes | Stated where section 0.1 says |

---

## MATERIAL

### M3-1. C1-f's slow follow component neither centres nor scales the regime-varying follow effect

**Where.** Section 12 item 2, lines 538-541:

> For C1-f^r, also a slow follow component `g_t f^r_i`: `g_t` switches between 0 and `2 g_r*` with probability 1/250
> per session, `g_r*` the twin's largest calendar-year lift over the coin on the choice block ... The null statistic is
> recentred by its replicate mean, so the line's dispersion includes the regime-varying follow effect the review named.

Item 3 (lines 544-547) cites `tests/test_family_b_b2.py` for the level. Section 0.1 (M2-2) and E-030 say B2 now covers
every judging line.

**Evidence.**

- **The component's mean is not zero.**
  - On an offer where the model agrees with the twin (s = f), `(s - f) g_t f` is 0. Where it disagrees (s = -f), the value is -2 g_t.
  - So each session's C1-f value gets -2 q_t g_t, where q_t is the session's disagreement share. Its expectation is -2 q g_r*, which is not 0.
  - The draft removes this by "recentring". That word has two readings, and both fail:
    - **Per replicate**, as "the replicate's grand mean removed" means for `d*` two bullets above: each replicate's per-session values lose their own mean, so the studentised statistic is identically zero (check C: max |t*| = 2.5e-15). B2's quantile is then 0 and the critical value is the nominal one.
    - **Across replicates** (the statistic minus its mean over replicates): the boundary null's tail is under-represented. The upper tail comes from blocks where the twin's lift sat low throughout, and shifting a studentised mixture by its mean puts those blocks about half as far out as they really are.
  - The construction that works centres the component at its expectation in the numerator: `(g_t - g_r*) f_i`.
- **The synthetic check** (check C2, session level; seed 7301; 610 judged sessions, 9 blocks of 63, 40,000 replications):
  - at the boundary null, the twin's lift is a 0 / 2g two-state Markov process at 1/250, the model's lift is constant and equal to it on average, the model disagrees with the twin on 40 % of offers, and the session sd is 0.13;
  - the scale is my assumption, chosen so the slow part is about the size of the 63-session block noise.

  | judged amplitude g_J | B2's amplitude g_C | nominal t rejects (0.01) | at B2, read across replicates | at B2, centred at E g |
  |---|---|---|---|---|
  | 0.02 | 0.02 | 0.075 | **0.030** | 0.010 |
  | 0.02 | 0.01 | 0.071 | 0.055 | **0.037** |
  | 0.03 | 0.01 | 0.119 | 0.100 | **0.084** |

- **The amplitude is taken from the block the files say is weakest.**
  - Section 2's table and the audit's 1.2 (`D_protocol.md:152-156`) record the twins' gain as "the late years'" (D-580 (5)) and "concentrated in 2024-2026" (D-588). `lnbar1x4`'s lift persisted at L = 5 (D-592).
  - `g_r*` is "the twin's largest calendar-year lift over the coin on the choice block". The declaration therefore takes, in advance, the amplitude that the prior-exposure table says is the smaller one.
  - Item 4 concedes "a slow drift slower or larger than the declared one". For the follow component, though, the size of the gap is already known from Stage 2's rows.
- **The test does not reach C1-f.** `tests/test_family_b_b2.py:61-99` builds only C1's form (`A * d`): there is no `(s - f)` weight, no follow component and no recentring. "Holds the level at 0.01" (line 545) is shown for C1. C1-d is structurally C1 with `A - s_bar`. C1-f and C2's weighted form are untested.

**The failure it allows.** Take a model that is itself a follow rule: a different lag or window from `mom15`, `lbrk5` or
`lnbar1x4`, whose lift tracks the same regimes with a different profile. On the judged block it beats a twin whose
lift happened to sit low for a year. C1-f is the line written to refuse exactly that model (M-2), and it passes it at
several times the declared level. With the other lines it carries "a direction no single rule shows", and that
direction is the follow effect Stage 2 already recorded.

**Remedy (changes a declared rule).**
- Write the follow component as `(g_t - g_r*) f^r_i`, centred at its expectation in the numerator. Drop "recentred by its replicate mean".
- Take its amplitude as the larger of:
  - the choice block's largest calendar-year lift;
  - the twin's largest per-year lift over 2020-2026 in Stage 2's recorded S1/S3 results (D-580, D-588, D-590, D-592). These are already read and disclosed in section 2's pre-read table, and they can raise the critical value but cannot choose anything;
  - or a declared multiple of the first, fixed now.
- Extend `tests/test_family_b_b2.py` with a C1-f boundary case (the twin's lift regime-varying, the model's constant, the judged amplitude above the choice block's) and with C2's weighted form. This takes seconds to minutes.

### M3-2. The opening range's net move is a linear combination of three used features

**Where.**
- Section 2 (c), lines 118-120: "no feature can compute the extremes, the position in, the net move from the open of, or the VWAP of any opening range that starts at 08:30 -- 5, 15, 30 or 60 minutes".
- Lines 127-129: "What remains ... `d_pdc - gap`, the move since the 08:29 bar".
- Lines 130-131: "no question needs to go to the operator".
- E-030: "the third version reads no bar of 08:30-08:59, so no ruling is needed for it to stand".
- `tests/test_family_b_opening_range.py:116-131`, which compares one feature at a time.

**Evidence.**
- **The identity, from `features.py`.**
  - `d_pdc = (c - pC)/A` (line 536), `gap = (C_on - pC)/A` with `C_on = Cff[:, 929]`, the close as of 08:29 (lines 506 and 540), and `ret_60 = (c - Cff[:, s-61])/A` (line 516).
  - So `d_pdc - gap - ret_60 = (Cff[:, s-61] - C[08:29]) / atr14` on every non-roll day, at every alert.
  - At 10:30 that is the close as of 09:29 less the close as of 08:29: the 60-minute opening range's net move from its open. In futures the 08:30 open is within a tick or two of the 08:29 close.
  - A logistic regression on standardised features can place this combination in its score with three coefficients. Winsorising touches only the tails.
- **Synthetic** (check A: the opening-range test's own bars and seed, 48 days).

  | alert | `d_pdc - gap - ret_60` equals `(C[t-61] - C[08:29])/A` | correlation with the 30-min range's net move | with the 60-min range's |
  |---|---|---|---|
  | 10:05 | exactly | **0.966** | 0.899 |
  | 10:30 | exactly | 0.869 | **1.000** (largest gap 0.003 ATR) |
  | 12:00 | exactly | 0.568 | 0.715 |

- **The test cannot see it.** `_identical_over_days` compares single columns. A combination of `d_pdc`, `gap` and `ret_30` / `ret_15` / `ret_5` gives the same quantity at other split points.
- **The draft's own list.** Section 2 (c) itself lists the net move from the open, for 60 minutes. The model's single coefficient vector applies the combination at every alert as "the move from before the open to an hour ago". From 10:05 to about 10:35 that move is mostly the opening range's net move.
- **What Stage 2 closed.**
  - D-281 closed "the 08:30 NQ opening-range-breakout research branch (ORB1 to ORB6)" and reserved to the operator "whether any later hypothesis is genuinely different" (D-281 (3)).
  - ORB6's capture recorded "the per-side unconditional entries ... at eight slots from 08:40 to 11:35 CT, and the overnight move, the gap and the Globex session's VWAP" (`vendor/stage2/DECISIONS.md:297`, D-278 (1)).
  - The family has no range extremes, so it cannot place a breakout. It does have the gap, the overnight move and the first hour's net move, at entries from 10:10, and none of its three twins is a since-open rule.
  - That may well be "genuinely different". But D-281 (3) reserves the call, and the audit's default (1.2 (3), `D_protocol.md:171-172`) excludes until someone rules. The draft's claim that nothing of the kind is computable is what lets it skip the ruling.
- **The second review's own remedy did not see this either.** That review's remedy ("no windowed feature may read 08:30-08:59 ... the four RTH-so-far features dropped") is what this draft implemented, and it did not consider combinations across features. The gap is shared.

**The failure it allows.** The model learns "long when the move from 08:29 to an hour ago is up", weighted by the gap.
This is a first-hour follow rule with ORB6's gap filter, entered from 10:10. It passes C1 and C1-f (no twin is
since-open), and the family reports a new direction signal from outside the closed specification. In fact the
specification was left without a ruling, on a claim the code does not support.

**Remedy.** At the least, a reading by the lead under a row (no declared rule changes):
- correct section 2 (c) to say that the exclusion keeps out the half-hour's extremes, position, path and VWAP; that its net move remains as a difference of closes on either side of it; and that at 10:30 `d_pdc - gap - ret_60` is the 60-minute range's net move exactly;
- record whether that residual is outside D-281 (3)'s branch (a breakout needs the range's extremes);
- replace the single-feature check in `tests/test_family_b_opening_range.py` with a regression check: each opening-range quantity (30- and 60-minute width, position, net move and VWAP distance) regressed on the 41 columns at each admitted alert, with the R-squared reported. Net move at 10:30 should come out at about 1; width, position and VWAP should not.

If the lead holds the residual inside the branch, a rule changes:
- drop `gap`, so that no close before 08:30 is known except through the overnight extremes and the day's first open, and the half-hour's net move is then entangled with the overnight session's; or
- add a since-open follow twin to C1-f at L = 5 (the sign of `d_pdc - gap` at the alert).

---

## MINOR

- **m3-1. The as-of fallback is guarded only at 10:05** (lines 168-169).
  - **The code.** `_ffill_close` (`features.py:387-393`) carries a close forward across any gap. At alert 10:05 + 5k, `ret_60` and the first return of `rv_60` (hence `rv_ratio`, `rv_tod` and `rv_atr`) read the close as of 09:04 + 5k. That close lands in the half-hour if no bar is stamped 09:00..09:04+5k, but the declared rule drops only the 10:05 alert.
  - **`ret_day`.** It reads `O_day`, the day's first open (lines 525-526). On a day with no bar before 08:30 that open is inside the half-hour.
  - **The test.** The invariance test replaces bars but never removes the post-09:00 ones. The synthetic RTH bars miss 0.1 % of minutes at random (`synthetic_bars.py:55`), so a 5- to 10-minute gap after 09:00 never occurs.
  - **Real days.** The pinned calendar's defect days in the judged block are late starts at 17:02 and 19:00 and one day with no RTH bars, none of which triggers this. 2020-03-16 (589 bars) and 2020-03-18 are the ones to look at.
  - **The failure it allows.** On such a day the as-of close at an admitted alert is a half-hour close, and the claim "at every admitted alert" is false for that row.
  - **Remedy.** A refusing per-row check at the feature build: for every admitted (session, alert), each as-of close and each first open the 37 features use is stamped at or after 09:00, or before 08:30, of the day. A row that fails is dropped and counted.
- **m3-2. The judged block's block count and its remainder** (lines 166-167, 412-413 and 521-525).
  - **The count.** The pinned calendars give 663 weekdays from 2024-01-02 to 2026-07-16. Of these, 33 are holiday or early-close days (kind `e`), one is a defect day with no RTH bars, and 20 are FOMC days (two in `fomc_statements_2020_2024q1.csv`, 18 in `fomc_statements.csv`). That leaves about 609 sessions of kinds `n` and `b`: 9 blocks of 63 and about 42 sessions over.
  - **The draft's figures.** It says "about 630", and "about 10 blocks, so about 9 degrees of freedom".
  - **The remainder.** It is not declared. `tests/test_family_b_b2.py:45-48` drops the last sessions, which would leave the most recent 2 months (about 7 % of the judged block) in no block. Which end is dropped, or whether a partial block is kept, is an unlabelled choice that the code would make silently.
  - **Remedy.** Declare the remainder rule, for example equal blocks of floor(N/9) or ceil(N/9) sessions, or the last block absorbing the remainder, for the lines and for B2 alike. Compute the MDL at the resulting df: one-sided t at 0.05/132 is 5.27 at 8 df against 4.98 at 9.
- **m3-3. The lines' per-session value** (line 522).
  - **What is missing.** The value is not defined: the session's mean over its offers, or its sum over the block's offer count. Nor is it said what a session with no offers contributes, which matters for a `filter` pick, where the filtered offers per session vary from 0 to many.
  - **The mismatch.** Stage B's `L_c` is the offer mean (line 480). If C1's estimand is session-weighted, it is a different estimand from the one stage B ranked.
  - **Remedy.** Define the value, preferably the offer mean as at stage B (a block's sum over its offer count), and state the empty-session rule.
- **m3-4. C2's B2 cannot run where section 13 puts it** (lines 568 and 599-600).
  - **The order.** C2's B2 holds "the routing weights fixed", but the routing (`i(j)`, `R_j`, `p(j)`) comes from `stage_C_campaign`. That campaign walks the judged outcomes, at the bound arm's shifted edges. So C2's critical value is computed after the outcomes, conditional on weights that depend on them.
  - **How much the coupling matters.** Stage 2's gate draws each path's calendar one independent day at a time by default (`propedge/campaign/gate.py:211-214`). So a trade's place depends on its own day's outcome only when that day is drawn more than once in a path (504 draws from about 609 days). The coupling is second order, but it is not zero. The places' values differ by a factor of about 6 (`u_value_map.csv:26207, 26214, 26221, 26228`: `mean_dv` 225 at the evaluation, 1,426 at the funded opening, 629 funded later, 665 paid).
  - **Remedy.** State that C2's B2 runs after `stage_C_campaign`, conditional on the realised routing, and why the coupling is small. Alternatively, price the model's lift at the places design (ii)'s coin-sided campaign routes, which do not depend on the model's outcomes. Say which `a*` C2's `d*` takes at each `R_j`.
- **m3-5. `filter` cells: the MDL and 2020** (lines 414, 469, 492-494 and 386-388).
  - **The MDL.** Stage A's MDL is "for a `filter` cell, the share its own threshold passes", and section 0.1 says "the MDL computed on" the judged share. The judged share does not exist at stage A.
  - **2020.** K2 "in each choice year" and the pick's 4 % margin on "its population's worst choice year" are undefined for a `filter` cell in 2020, which has no out-of-fold prediction.
  - **Remedy.** Compute stage A's MDL at the training share (0.20), recompute it beside at the judged share, and define the filter cell's K2 and margin on 2021-2023, or on the stop's full population.
- **m3-6. The scorecard's 2021-2023 starts straddle the boundary** (line 646).
  - **The straddle.** A start in 2023 runs into 2024 by month 3 (P) or month 12 (the journey variables). The draft calls these "a choice-block read", but the reader refuses any span reaching 2024 without a purpose. The read fails safe, yet which sides such a journey carries after 2023-12-29, and under which declared purpose, is not stated.
  - **Remedy.** Truncate those starts at the boundary, labelled; or read them under `stage_C_scorecard` with the final model's judged sides after 2023-12-29, labelled as mixed.
- **m3-7. "Recorded" without a record** (section 12, lines 509-517; commit 780f6da).
  - The draft rests its rejection of the second review's remedies (a) and (b) on a scratch check, "seeds fixed beforehand, recorded; 4,000 replications per seed". No script or output is in the tree.
  - Under CLAUDE.md's failure protocol "a failed check stays on record". Add the script and its printed output, as the reviews' appendices do, or cite where they are.

## NOTE

- **n3-1. What the seal does not enforce.** `read_bars` returns whole trading days (`reader.py:643-669`). So `stage_C_sides`' "bars up to each alert" and "hashed before any outcome is read" (lines 235-237) rest on the library's shift-invariance tests, the twins' build check (section 20 item 4) and the runner's order, not on the reader. The reader does not enforce the order of the four purposes either; the ledger's `when` fields record it. Say so in section 5.
- **n3-2. Power.** One-sided t at 0.05/132 is 5.27 at 8 df, against z = 3.37. The MDL in block-SE units is then about 6-7, so the family is very likely a screen. Section 3 says this may happen; give the MDL ratio as soon as Q-16 is merged.
- **n3-3. Stale text.** Section 2 (c)'s last bullet ("the lead corrects that in a new row") and section 22 items 4 and 5 (the E-019 correction; the D-621 (4)(d) row) are done by E-030 and E-031 (1).
- **n3-4. The prior session after a holiday halt.** On the day after MLK, Presidents' Day and similar halts, `pos_prior`, `d_pdh`, `d_pdl`, `d_pdc`, `range_prior`, `ret_prior` and `gap` read that 08:30-11:59 partial session as "the prior RTH", since kind `e` days stay in the frame (`features.py:496-502`). This is not look-ahead and it is the same in both blocks. Say it beside the feature table.
- **n3-5. Day kinds.** `atlas_local.close_day` marks a day `e` from its own last bar. E-029's pinned calendar now holds the scheduled early closes in advance, so n-4's post-alert fact remains only for defect days.
- **n3-6. The two amplitudes run opposite ways.** B2's drift amplitude `a*`, from 2020-2023, is probably conservative: those years include 2020's crash and rebound and 2022's fall. The same rule applied to `g_r*` is anti-conservative (M3-1).

---

## What I tried that found nothing

- **Bar reads at the new alerts.**
  - I re-read every per-alert slice in `features.py:512-566` for s in 1025..1320. Each used feature reads `Cff[:, s-1]`, `Cff[:, s-1-w]` for w in {5, 15, 30, 60}, `Cff[:, s-31]`, window sums over `[s-w, s)` for w <= 60, the overnight `[:930)`, the 20 prior days at the same slot, or earlier sessions.
  - At 10:05 the earliest as-of close read is 09:04 (`ret_60`, `rv_60`'s first return). The window reads start at 09:05 (`rng_60`, `ext_ma60`, `vol_accel`).
  - At 10:00, `Cff[:, 959]` would be 08:59, so 10:05 is the earliest admissible first alert. The alert set is fixed by that arithmetic, not by any outcome.
  - The 10 excluded features do read the half-hour (the test's non-vacuity half), and 37 + 10 = 47.
  - The day kinds (`x`, `e`, `o`, `n`, `b`) read the day's last bar, FOMC and BLS only, not the half-hour.
- **The tests.** `test_family_b_opening_range.py`, `test_family_b_side_rule.py` and `test_family_b_b2.py`: 10 passed.
- **The `Judged-block reads:` line against `reader.py`.**
  - `DECLARED_LINE` (`reader.py:112`) matches line 232 after its `  - **` markers, and `PURPOSE_TOKEN` takes the four purposes.
  - No purpose contains a word of `CHOICE_WORDS` (line 108).
  - The other two places that name the purposes are table rows starting with `|` (line 69 mentions them; line 760 lists them in backticks), which the pattern does not match, so they add nothing.
  - The once-rule is per (declaration, purpose) across runs, as section 5 says.
  - A `DRAFT_` file is refused as a declaration until it is renamed `prereg/F-NN_*.md` and pinned.
- **Stage B2 for C1 over many choice blocks** (check B). The test's own construction, without the surrogate, over 24 choice-block realisations at 2,000 replications each:
  - pooled rejection at 0.01: 0.0079 on the review's design and 0.0076 on the slower one;
  - one case in 24 above 1.25 times the level on each design;
  - the critical value from 1.00 to 1.36 times nominal on the review's design and 1.00 to 1.76 on the slower one;
  - the 63-session nominal alone rejects 0.0116 and 0.0165.
  - The declared C1 rule holds at 0.01 on these designs. The family level (3.8e-4) is section 20 item 7's heavy check.
- **Counts.** 2 x 3 x 2 = 12 cells; 7 x 2 x 2 = 28 configurations; 41 columns (37 - 1 + 4 + 1); 60 alerts (10:05..15:00); 13 lost marks (09:05..10:05). One cell is judged, and its lines form an intersection-union at one level.
- **C2's level.** The family-level bound in sections 0, 13 and 17. The confirmation's 95 % matches its registered 0.05.
- **The filter threshold and p~.** Both come from the model's own training sample, with the intercept cancelling exactly. The second review's synthetic check showed about 0.20 passing at the model's own quantile.
- **The cutoff and margin** are side-free (kinds only), on 2020-2023, and per year. Because the unresolved share rises with R, the margin on {1, 1.5, 3}, the cutoff at all six R and the floor at "every offered R" all bind at R = 3.
- **Cross-block leakage.** The final model's training ends 2023-12-29 and labels resolve within the session. Every normaliser is trailing or in-fold. B2 reads choice-block pair values and judged sides only. No trade straddles the boundary.
- **Seeds.** `grep -rIowl -E "2026196[0-9]"` finds them in this draft, its three tests and `DECISIONS.md`. Family R's draft only lists 20261960-69 as F-B's. The match in Stage 2's `rc_s150_all_gate_paths.csv` is a digit run inside a float (`4.202619639956034`), not a seed.
- **C2's routing coupling.** Stage 2's gate default (one independent day a draw, `gate.py:211-214`) makes it second order (m3-4).
- **Selection after the fact.** The first alert, the dropped stop, the margin, the B2 constants and the threshold were all fixed without any outcome of the family. The one choice that tilts towards passing is `g_r*`'s source (M3-1).

## What I could not check

- **The judged block's session count.** The store's manifest was not read; the calendars give about 609. A one-line count from `day_list` at the build settles m3-2.
- **The real size of the twins' year-to-year lift variation.** I did not read Stage 2's S1/S3 result files for numbers; M3-1's scale is my assumption.
  - The experiment to settle it: tabulate each twin's per-year lift over the coin at the family's offers, on 2020-2023 (a choice-block read, allowed). Beside it, Stage 2's recorded 2020-2026 per-year values (already read). Then run the extended B2 test at those amplitudes. Light.
- **Whether 2020-03-16 or 2020-03-18 trigger m3-1's fallback.** This needs their bars; m3-1's per-row check does it at the build.
- **Q-16's statistic** (not merged), the place-recording adapter for C2, and how the bound arm's `lb_by_rr` is computed for a new design's judged trades.
- **B2 at the family level** (heavy, section 20 item 7), and C1-f's and C2's B2 at any level until the test is extended (M3-1).

---

## Appendix: the synthetic checks (scratch, exploratory, seeds fixed before running)

**A. The opening range's net move as a combination (M3-2).** The opening-range test's own bars and seed.

```python
import sys
from datetime import date
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-scout")
import numpy as np, pandas as pd
from extended import features as F, synthetic_bars as sb
SEED = 20261968
bars = sb.generate(sb.Spec(date(2021, 1, 4), date(2021, 4, 15),
                           seed=int(np.random.default_rng([SEED, 20]).integers(1, 2**31))))
cal = F.load_calendars()
alerts = [F.slot(10, 5), F.slot(10, 30), F.slot(12, 0)]
X = F.compute(bars, alerts, cal, normalisers=True)
X = X[X["day"] >= "2021-02-05"].reset_index(drop=True)
local = pd.to_datetime(bars["ts"], unit="s", utc=True).dt.tz_convert(sb.CHICAGO).dt.tz_localize(None)
b = bars.assign(hm=(local.dt.hour * 60 + local.dt.minute).to_numpy())
def close_asof(day, h, m):
    x = b[(b["day"] == day) & (b["hm"] <= h * 60 + m) & (b["hm"] < 17 * 60)]
    return float(x["close"].iloc[-1])
def or_open(day):
    x = b[(b["day"] == day) & (b["hm"] >= 8 * 60 + 30) & (b["hm"] < 9 * 60)]
    return float(x["open"].iloc[0]), float(x["close"].iloc[-1])
for s, label, (h, m) in ((alerts[0], "10:05", (9, 4)), (alerts[1], "10:30", (9, 29)), (alerts[2], "12:00", (10, 59))):
    r = X[X["slot"] == s].dropna(subset=["d_pdc", "gap", "ret_60"]).reset_index(drop=True)
    combo = (r["d_pdc"] - r["gap"] - r["ret_60"]).to_numpy(); A = r["norm_atr14"].to_numpy()
    target = np.array([close_asof(d, h, m) - close_asof(d, 8, 29) for d in r["day"]]) / A
    or30 = np.array([(lambda oc: oc[1] - oc[0])(or_open(d)) for d in r["day"]]) / A
    or60 = np.array([close_asof(d, 9, 29) - or_open(d)[0] for d in r["day"]]) / A
    print(label, len(r), np.allclose(combo, target, rtol=0, atol=1e-9), np.corrcoef(combo, or30)[0, 1],
          np.corrcoef(combo, or60)[0, 1], np.max(np.abs(combo - or60)))
```

Printed: 10:05, 48 rows, True, 0.966, 0.899, 0.491; 10:30, True, 0.869, 1.000, 0.0032; 12:00, True, 0.568, 0.715, 0.803.

**B. Stage B2 for C1 over 24 choice blocks (M2-2 judged); seeds `[7101, j]`.** `markov`, `tstat`, `stationary_idx` are
`tests/test_family_b_b2.py`'s, unchanged. `case_b` is its `one_case` without the surrogate, at 63-session blocks,
R = 2,000.

```python
def case_b(seed, a, q_d, q_s):
    rng = np.random.default_rng(seed)
    offers = np.where(rng.random((TJ, M)) < np.where(markov(rng, q_s, 1, TJ)[0] > 0, P_IN, 1 - P_IN)[:, None], 1, -1)
    A = offers.mean(1)
    noise = lambda: S_EPS / np.sqrt(M) * rng.standard_normal((R, TJ))
    true_x = A * (a * markov(rng, q_d, R, TJ) + S_ETA * rng.standard_normal((R, TJ))) + noise()
    choice = (a * markov(rng, q_d, 1, TC) + S_ETA * rng.standard_normal((1, TC)))[0]
    a_star = np.max(np.abs(choice[:1000].reshape(4, 250).mean(1)))
    d_star = choice[stationary_idx(rng, R, TJ, TC, 63)]
    d_star = d_star - d_star.mean(1, keepdims=True) + a_star * markov(rng, 1 / 250, R, TJ)
    t_true, nb = tstat(true_x, 63); t_b2, _ = tstat(A * d_star + noise(), 63)
    nominal = stats.t.ppf(0.99, nb - 1); crit = max(nominal, float(np.quantile(t_b2, 0.99)))
    return np.mean(t_true > nominal), np.mean(t_true > crit), a_star, crit / nominal
# TJ, TC, M = 630, 1000, 24; S_ETA, S_EPS, P_IN = 0.30, 0.35, 0.80; R = 2000
# REVIEW a=0.03, q_d=1/120, q_s=1/60; SLOWER a=0.03, q_d=1/250, q_s=1/120; j = 0..23
```

Printed:
- REVIEW: nominal 0.0116; B2 0.0079 pooled (per case 0.0015..0.0170, 1 of 24 above 0.0125); `a*` 0.021..0.073; critical value 1.00..1.36 times nominal.
- SLOWER: nominal 0.0165; B2 0.0076 (0.0030..0.0135, 1 of 24); `a*` 0.015..0.080; 1.00..1.76 times nominal.

**C and C2. C1-f's slow follow component (M3-1); seeds 7201 (C) and 7301 (C2).** Session level, at the boundary null.

```python
import numpy as np
from scipy import stats
ALPHA, TJ2, BLOCK, Q_DIS, SIG, RC = 0.01, 610, 63, 0.4, 0.13, 40000
def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q; sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
def tstat(x, block):
    nb = x.shape[1] // block; bm = x[:, : nb * block].reshape(len(x), nb, block).mean(2)
    return bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb)), nb
def x_of(rng, n_rep, g_amp, centre):        # per-session C1-f values; g_t 0 / 2 g_amp at 1/250, E g = g_amp
    g = g_amp * (1.0 + markov(rng, 1 / 250, n_rep, TJ2))
    return -2 * Q_DIS * (g - (g_amp if centre else 0.0)) + SIG * rng.standard_normal((n_rep, TJ2))
rng = np.random.default_rng(7301)
for g_j, g_c in ((0.02, 0.02), (0.02, 0.01), (0.03, 0.01)):
    t_true, nb = tstat(x_of(rng, RC, g_j, True), BLOCK)                  # the truth: the boundary null
    nominal = stats.t.ppf(1 - ALPHA, nb - 1)
    t_ii, _ = tstat(x_of(rng, RC, g_c, False), BLOCK); t_ii = t_ii - t_ii.mean()   # recentred across replicates
    t_iii, _ = tstat(x_of(rng, RC, g_c, True), BLOCK)                    # centred at E g in the numerator
    for t_b2 in (t_ii, t_iii):
        crit = max(nominal, float(np.quantile(t_b2, 1 - ALPHA)))
        print(g_j, g_c, np.mean(t_true > nominal), crit / nominal, np.mean(t_true > crit))
# check C, the per-replicate reading: x - x.mean(1, keepdims=True) on the blocks' sessions -> t identically 0
```

Printed (C2):

| g_J | g_C | nominal rejects | across replicates: critical value / nominal | rejects | centred at E g: critical value / nominal | rejects |
|---|---|---|---|---|---|---|
| 0.02 | 0.02 | 0.0748 | 1.37 | 0.0302 | 1.79 | 0.0103 |
| 0.02 | 0.01 | 0.0713 | 1.11 | 0.0554 | 1.27 | 0.0368 |
| 0.03 | 0.01 | 0.1193 | 1.12 | 0.1001 | 1.24 | 0.0836 |

Check C, seed 7201, the same design: across replicates 0.0277, 0.0521, 0.0726 and 0.1025, for (g_J, g_C) = (0.02,
0.02), (0.02, 0.01), (0.02, 0.0067) and (0.03, 0.01); per replicate, max |t*| = 2.5e-15.

The t critical values, one-sided: 2.896 and 2.821 at 0.01; **5.268 and 4.982 at 0.05/132**; 5.407 and 5.105 at
0.05/156 (8 and 9 df respectively); z = 3.368 at 0.05/132.

**D. The judged block's session count (m3-2).** No bars are read: the weekdays from 2024-01-02 to 2026-07-16 (663),
less `config/calendar_early_closes.csv`'s `holiday` and `early_close` weekdays (33), less its data-defect day with no
RTH bars (2025-06-30), less the FOMC statement days in `vendor/stage2/config/sources/fomc_statements*.csv` (20). That
leaves about 609 sessions: 9 blocks of 63 and 42 over.
