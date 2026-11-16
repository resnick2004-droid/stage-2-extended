# Red team: `prereg/DRAFT_F-B_multifeature.md` (family B, the multi-feature model), 2026-11-15

Target: `prereg/DRAFT_F-B_multifeature.md` at master e450912 (worktree `wt-scout`, branch `wt/wt-scout`), with the code
it relies on (`extended/features.py`, `tests/test_features*.py`, `extended/walker.py`). Read against `CHARTER.md`
sections 2-4, `DECISIONS.md` E-001..E-017, `CLAUDE.md`, the feature-rules and prereg-discipline skills, the
prereg-gatekeeper's text, the Phase 0 audit (`docs/audits/phase0/D_protocol.md`) and its red team
(`docs/reviews/phase0_red_team_2026-11-15.md`), the Q-11 and Q-16 briefs, and the Stage 2 files the draft cites
(`vendor/stage2/DECISIONS.md` D-275..D-281, D-578..D-592; `config/search_program*.yaml`; `results/rc_width_screen.csv`;
`results/u_value_map.csv`; `propedge/research/resolved_coin.py`, `atlas_local.py`, `fv3_rung_walk.py`;
`propedge/outcomes/fv3_core.py`; `data/README.md`).

The brief held no expected answer. The draft states its own ("speed yes, direction probably not"). I treated that as
part of the target, not as a prior. Nothing here read a bar, the atlas or NQ from 2026-07-17. Nothing ran the engine.
The two synthetic checks (Appendix) are exploratory scratch code, seeds 1 and 2, and selected nothing.

## Verdict: **must be redrafted**

The feature library holds up. I found no look-ahead in `extended/features.py`, and its tests bite. The draft is a
different matter. Its declared rules have one defect that decides its answer (C-1) and six material ones, four of which
change a declared rule (M-1, M-2, M-3, M-5) and one an undeclared confirmation (M-6). The worst follow from one fact the
draft never states: at 37.5 points its population is the six alerts 08:30-08:55 of each session, not the regular
session. Its sides also collapse to the training block's majority side under the signal the draft expects.

| id | severity | finding (one line) |
|---|---|---|
| C-1 | **CHANGES-A-CONCLUSION** | With p > 0.5, an unpenalised intercept and log-loss lambda search, a null or weak signal picks the grid's top edge and the sides become the training block's majority side (synthetic: 88-100 % long). C1 then reads drift, C1-d degenerates, and a "no" answers nothing about the features |
| M-1 | MATERIAL | At 37.5 points P-16 offers only the entry marks 08:30-09:00 inside regular hours. The population is six alerts a session (08:30-08:55), so `or_width`/`or_pos` never exist and `m_or` is constant, the whole family sits inside Stage 2's closed 08:30 opening window (D-281 (3)), the prior-exposure table misses A3's `orb_rth*`, and K2 at R = 3 is near its line |
| M-2 | MATERIAL | C1-f nets out the wrong twin. `mom15` at L = 5 was never Stage 2's survivor (S1 read L = 0, D-589 (5)). The effect D-592 found persisting at L = 5 is S3's `lnbar1x4`, and with `lbrk5` it is "beside, deciding nothing". A model tracking it clears C1, C1-d and C1-f on a block known to hold it |
| M-3 | MATERIAL | C2 prices the mean lift over all offers by P-16's per-place uses, but each place trades particular offers. The funded opening (R = 3, the highest-value place) is mostly the session's first offer (alert 08:30, RTH features missing), and the uses are P-16's overnight-dominated journey, not this design's |
| M-4 | MATERIAL | Every dependence model in the draft (Q-16's sign-flip calibration, stage B's bootstrap, the null canary) decorrelates within about 21 sessions, but the model's sides are driven by daily features and the intercept. Synthetic: a block-means t at 0.001 rejects a true null 1.4-2.4 times nominal. C1-d's and C1-f's weighted statistics are not covered at all |
| M-5 | MATERIAL | P-15's 25-point marks exist in no vendored file. `mark_resolution` computes them "over the whole window", so stage A would read the judged block (T-3 fails by construction) or the atlas the draft says it never reads |
| M-6 | MATERIAL | The confirmation's test (statistic, level, length) is undeclared (red team M1). F-02's draft declares it; F-B does not |
| m-1 | MINOR | E-016 (2) put `or_width`/`or_pos` out of family B. The draft still counts 47 features, 53 columns and `m_or` |
| m-2 | MINOR | Stage B's estimator is ambiguous (L_c per offer vs a "session-weighted lift" bootstrapped and centred at L_c), and the canary's "0.001 critical value" is undefined |
| m-3 | MINOR | Stage B's family-wise 0.05 ignores lambda, chosen on the same 2021-2023 out-of-fold years, so Kill B is laxer than stated |
| m-4 | MINOR | The filter threshold comes from in-sample \|p - 0.5\| (fewer than a fifth pass out of fold, mostly one side), and K1/K2 for filter cells "in every choice year" are undefined for 2020 |
| m-5 | MINOR | The positive control cannot detect a feature-label misalignment: volatility clusters, so labels shifted a session still give AUC > 0.5 |
| m-6 | MINOR | Whole-window inputs (P-16's marks, the value map, the stop band) are invisible to T-3. Only the marks are disclosed, and they pre-read the judged K2 floor (09:00 at 4.85 % unresolved over 2020-2026) |
| m-7 | MINOR | The judged block's seal is T-3 alone: no purpose-tagged reader or read ledger exists (audit R-4, R-5, H-2) |
| m-8 | MINOR | "Declared a screen ... a pass is a lead for confirmation only" (section 7) conflicts with section 15's CARRIED |
| m-9 | MINOR | Stage 2 D-621 (4)(d) "no fitted values" (gatekeeper item 3) needs the row the audit says family B requires (1.5 (a)). The draft does not name it |
| m-10 | MINOR | C2's "uses" are not tied to a block (stage B uses the choice block; C2 does not say) |
| n-1 | NOTE | Open question 4 is half stale: E-016 (3) aligned the gatekeeper's item 6. Item 7 still refuses non-integer seeds at pinning |
| n-2 | NOTE | The embargo's stated reason is muddled (a forward walk needs none). It is harmless |
| n-3 | NOTE | The breakeven move fires at 13:00 CT for these entries. In win units it can shrink a real lift, so "only enlarge" is not exact. The size is negligible |
| n-4 | NOTE | Day kinds use post-alert facts: an early close (`e`) read from the day's own last bar, and Stage 2's FOMC set includes 2020-03-03's 10:00 ET unscheduled statement. Training only, side-neutral |
| n-5 | NOTE | "One tick adverse" is a cost in the walk, not a fill price (`walker.py:23`), so "both sides enter at the same price" holds |
| n-6 | NOTE | The null canary reads choice-block direction outcomes inside stage A, which line 216 calls "side-free columns only". Harmless; say so |
| n-7 | NOTE | Say what a later family on the same features and population may be judged on (audit R-8, 1.5 (c)) |

---

## CHANGES-A-CONCLUSION

### C-1. The side rule and the search make the model's side a drift bet under the expected signal

**Where.** Lines 273-274 (side = long if p > 0.5), 277-279 (filter on |p - 0.5|), 243-247 (intercept not penalised),
250-258 (lambda grid `0.25 x 10^(j/2)`, j = -2..2; criterion the out-of-fold log loss, ties to the larger lambda), 309-310
(C1-d on `(s - s_bar) d`), lines 404-405 (both classed "fixed: this file").

**Evidence.** The direction label is y = 1 when the long beats the short at R = 1 (lines 137-139). Its base rate on
2020-2023 is not 0.5 but whatever the block's drift made it. The unpenalised intercept fits that base rate, and every
other coefficient is shrunk by about 0.25/(0.25 + lambda) (line 251). When the features carry little direction (the
draft's own expectation, lines 27-28 and 489-491), log loss is smallest where the model is closest to the base rate,
that is at the largest lambda. The sign of p - 0.5 is then the intercept's sign on almost every offer. Synthetic check
(Appendix A: 750 training sessions of six offers, 50 standardised columns, half of them near-daily, no signal, offers in
a session agreeing 85 %):

| base rate of y | long share at lambda 0.025 / 0.079 / 0.25 / 0.79 / 2.5 | lambda the declared criterion picks | long share if the side is p > the training median of p |
|---|---|---|---|
| 0.53 | 0.70 / 0.74 / 0.84 / 0.98 / 1.00 | 2.5 (the top edge) | 0.49 at every lambda |
| 0.51 | 0.54 / 0.54 / 0.57 / 0.66 / 0.88 | 2.5 (the top edge) | 0.49 at every lambda |

**The failure it allows.** Feed it an opening half-hour whose 2020-2023 long-beats-short share is 0.51-0.53 and no real
direction. The pick then goes long on 88-100 % of judged offers:
- C1 reads the judged block's drift (NQ rose over most of 2024-2026);
- C1-d's `(s - s_bar)` is zero on most offers and identically zero when s_bar = 1, a 0/0 statistic the draft does not
  define;
- the filter cells select by the intercept's sign, not by confidence in a direction.

The family then closes, and section 15 records "no lift above the MDL" for a question the model never put to the data:
whether the features choose a side. The same mechanism with a weak real signal hides it behind the intercept. Either way
the family's answer is set by the training block's drift and the grid's top edge, not by its 47 measurements. The top
edge was fixed before any read, so this is not selection after the fact, but under the stated expectation the search
lands on it.

**Remedy (changes a declared rule).**
- Make the side `sign(p - p~)` and the filter `|p - p~|`, where p~ is the training fold's session-weighted median of the
  fitted p, pinned with the model.
- Report each fold's long share in stage B.
- Define C1-d when s_bar is within a declared distance of +-1 (a fail, said in advance).
- Either extend the grid upward until the criterion has an interior minimum on the choice block, or state that the top
  edge is expected and what a pick at the edge means.

---

## MATERIAL

### M-1. The 37.5-point population is the first half-hour, and the draft is written for the whole session

**Where.** Lines 102-106 define the population: alerts in `ALERT_MARKS` (08:30-15:00) whose entry t + 5 is an offered
mark of P-16 (`rc_width_screen.csv`, `marks`, 150 ticks, `offered` true). Line 19 ("P-16 offers a trade every five
minutes"), line 90 ("US regular hours") and section 6's library describe a full-session family.

**Evidence.** In `vendor/stage2/results/rc_width_screen.csv` lines 191-198, the regular-session marks P-16 offers at 150
ticks are 08:30, 08:35, ..., 09:00. 09:05 is not offered: its worst-R unresolved share is 0.0517 (R = 3) against D-525's
0.05. Every later RTH mark is worse. P-16 is an overnight design with a seven-mark tail into the open. With alerts in
`ALERT_MARKS` (at or after 08:30, `features.py:89`) the population is entry marks 08:35-09:00, that is **six alerts a
session, 08:30-08:55**. Consequences the draft does not draw:

- **Dead and constant columns.** `or_width` and `or_pos` exist only from 09:00 (`features.py:171-175`, computed only if
  `s >= OR_END`, lines 542-544), so at 37.5 points they are NaN on every offer and `m_or` (line 212) is 1 on every
  offer. Section 6's "winsorised ... standardised by the training fold's standard deviation" is then undefined (an
  all-NaN column and a zero-variance column). The 53-column design matrix (line 213) is wrong.
- **The opening-range question is the population, not two features.** Lines 69-74 argue the family is "not an
  opening-range breakout specification" because no entry is triggered by the range. But every 37.5-point entry is a
  market order at 08:35-09:00, inside the 08:30-09:00 window, with sides read from the first minutes' features
  (`ret_rth`, `range_rth`, `pos_rth`, `d_vwap`, `ret_5`, `rng_15`). Stage 2 closed "the 08:30 NQ opening-range-breakout
  research branch" for good and reserved "whether any later hypothesis is genuinely different" to the operator (D-281
  (3); `vendor/stage2/DECISIONS.md:300`). The audit's rule is exclusion by default where the call is reserved
  (`D_protocol.md:171-172`).
- **Prior exposure is incomplete** (line 53's table; audit R-3). A3's atlas read `orb_rth5`, `orb_rth15` and
  `orb_rth30`, followed and faded, over 2020-2026 (`config/atlas_a3.yaml:58-60`; `D_protocol.md:156-157`). D-281 (3)
  records that ORB5's hand-traded stop entry, chased, held a positive funded-leg bound in both eras. That is direction
  in this very window, read on both blocks.
- **The 08:30 alert** (one offer in six, and as M-3 shows, the one a router takes first) has no RTH feature at all: four
  of them are NaN and `m_rth` = 1.
- **K2 at R = 3 sits on its line.** The 08:55 and 09:00 entries were 4.12 % and 4.85 % unresolved over 2020-2026 (rows
  196-197), so K2's per-year lines (lines 221-223, 316) may kill the R = 3 cells in a quiet year. That is legitimate,
  but it should be expected in writing.
- **Power.** The six offers of a session overlap and share one opening move, so the effective sample is about the
  number of sessions (about 630 judged). Section 7's MDL line (lines 235-239) should be computed on that basis.

**The failure it allows.** A family is pinned whose stated design (a model over the whole session) is not the one that
runs (a model over the first half-hour), inside a branch the operator was asked to rule on, with two declared features
that cannot be computed.

**Remedy.**
- Write the population into the file: the alert list per stop, the offers per session, the expected count per block.
- Rewrite section 2 (c) for the population rather than for two features, and send the D-281 (3) question to the operator
  with that fact (until then, the audit's default is exclusion).
- Add A3's `orb_rth*` and D-281 (3)'s baseline to the prior-exposure table.
- Recount the columns, drop `m_or` at 37.5 points, and state section 7's MDL on sessions.

### M-2. C1-f does not separate the effect Stage 2 recorded as a lead

**Where.** Lines 300-302 and 311-313 (the follow twin `f_i = sign(ret_15 at t)`, "Stage 2's S1 survivor `mom15`,
followed, at the 5-minute latency"), lines 65-68 ("two conjunctive kill lines that a known effect cannot clear"), lines
325-327 (`lbrk5` and `lnbar1x4` follow twins "beside, deciding nothing"), and table rows 58, 60 and 61.

**Evidence.**
- S1 (D-580) and S3 (D-588) read their rules at **L = 0**: "the side can be set by a bar closing at the mark itself ...
  S1's and S2's rules shared the assumption" (D-589 (5), `vendor/stage2/DECISIONS.md:607`). S1's survivors were `mom15`
  (followed, at 3R) and `lbrk5` (followed, at 1R and 1.5R) (D-580 (1), line 598).
- Stage 2 never read `mom15` at L = 5. The one rule it read at L = 5 is S3's candidate `lnbar1x4`, and D-592 (line 610)
  found "the per-offer lift over the coin is nearly as large at L = 5 as at L = 0 at every R -- the follow-the-breakout
  effect is broad and slow". That is the "lead for unread data" the draft says C1-f nets out (line 313).
- The draft's twin is `mom15` at L = 5. It is computed correctly: Stage 2's `c[t]` is "the close of the last 1-min bar
  ending at or before the mark" (`config/search_program.yaml:32`), i.e. the bar stamped t - 1, the same as `ret_15`.
  But it is not the recorded survivor, and the recorded L = 5 effect is not in any deciding line.

**The failure it allows.** The model learns a follow-the-last-breakout side from `ret_5`, `rng_15`, `pos_rth`,
`up_share_30` and `eff_30`. The effect was present but weaker on 2020-2023 (D-589 caveat (1)) and is known to be strong on
2024-2026. Such a model passes C1. It passes C1-d, because a follow side is not a drift side. It passes C1-f whenever the
breakout-follow lift on these offers exceeds 15-minute momentum's. The family then reports a direction "beyond the known
follow effect" that is the known follow effect, and a confirmation purchase is spent on Stage 2's lead under a model's
name. Section 2 (a)'s sentence is false as written.

**Remedy (changes a declared rule).**
- Run C1-f against each recorded follow twin at L = 5 (`mom15`, `lbrk5`, `lnbar1x4`, by Stage 2's event code, imported),
  each a conjunctive line at the family's level. An intersection-union test keeps the level, so this costs only power.
- Fix rows 58 and 60 to say L = 0, and row 61 to say that the lift persisted at L = 5.
- Optionally add a fourth line against a model fitted on the follow twins' sides alone.

### M-3. C2 values a lift the valued places do not trade

**Where.** Lines 291-297 (valued lift = lift x uses x `mean_dv` / 100; uses = the cell's offers a year capped by the
place's `trades_per_year_forward`; place by R; base `p16` for 37.5 points) and 314-315 (C2: at least $500 a year at
C1's 95 % bound).

**Evidence.**
- The value map's places are particular trades of a journey: (c) the funded account's opening trade, (b) the evaluation,
  (d) and (e) later funded and paid trades (`u_value_map.csv` section `place_values`). Base p16 gives `mean_dv` $2,277
  at (c) against $287-639 elsewhere (lines 27119-27149).
- In the scorecard's design (i), which trades only this family's six marks (lines 333-337), the firm is flat at the open
  and the strict router takes the first offer. The opening trade of a newly funded account is therefore mostly the 08:35
  entry, from the 08:30 alert with no RTH features (M-1).
- `trades_per_year_forward` is P-16's journey, which offers about 190 marks a day (overnight), not this design's six.

**The failure it allows.** Suppose the model's lift sits in the 08:40-08:55 alerts, where the RTH features exist, and is
nil at 08:30. Then R = 3's cell is valued at the funded opening's $2,277 a win, passes C2, and is worth nothing at the
trades that place makes. The reverse, a lift only at 08:30, is undervalued.

**Remedy.**
- Measure C2's lift on the offers each place uses: from design (i)'s routed trades by phase (the scorecard already runs
  it), or at least, for place (c), the session's first offered alert.
- Take the uses from design (i)'s own journey.
- If that is not done, report the uniform-lift assumption beside the verdict as an assumption that carries the money.

### M-4. The level's calibration does not cover this family's side process or its statistics

**Where.** Lines 284-288 (stage B: a 21-session circular block bootstrap); 230-234 (the null canary: sign flips in
21-session blocks); 305-313 (C1, C1-d, C1-f "by Q-16's calibrated lift test ... used as merged, unchanged"); 487 (open
question 10). The Q-16 brief's nulls (`docs/briefs/Q-16_2026-11-15.md:21-25`) are sign flips by session block on P-16's
own pairs, plus synthetic clustering.

**Evidence.**
- 13 of the 47 features are one value a day, and C-1 shows the intercept dominates the side. The model's side process
  can therefore persist for weeks to months.
- The pair value's mean (drift) also persists across regimes.
- Under H0 (the side independent of the future), `mean((s - s_bar) d)` then carries the product of two slow processes,
  whose variance a test that decorrelates within about 21 sessions does not see: the classic spurious-regression case.
- Synthetic check (Appendix B): 630 sessions, Student-t on 30 block means of 21 sessions; session-mean noise sd 0.35;
  drift +-a and side +-1 as independent two-state Markov chains (the drift sizes are my assumption, of the order a
  +-0.15 % a session bull or bear year makes at a 37.5-point bracket); 40,000 replications, Monte Carlo SE at 0.001
  about 0.00016:

| drift +-a | side and drift switch probability | rejected at 0.01 | rejected at 0.001 |
|---|---|---|---|
| 0 | 1/60, 1/250 | 0.0098, 0.0071 | 0.0008, 0.0007 |
| 0.02 | 1/60, 1/250 | 0.0102, 0.0118 | 0.0014, 0.0014 |
| 0.03 | 1/60, 1/250 | 0.0124, 0.0174 | 0.0016, 0.0024 |

The excess grows into the tail, where the family's level 0.05/132 (about 3.8e-4) lies. Three more gaps:
- the null canary flips signs in 21-session blocks, so by construction it cannot see this;
- C1-d's weights (1 - s_bar, -1 - s_bar) and C1-f's (s - f in {-2..2}, zero wherever the model agrees with momentum) are
  not the +-1 statistic Q-16 calibrates;
- P-16's pairs are mostly overnight marks, not six overlapping opening offers.

**The failure it allows.** A model that happens to be long through the judged block's rising regimes and short through
its falling ones rejects at a multiple of the declared level, and the conjunction does not protect, since C1-d removes
only a constant drift.

**Remedy.**
- Before pinning, make "calibration holding" (line 308) mean: on this family's statistics (C1, C1-d, C1-f), on this
  population's choice-block pairs, with side processes as persistent as the pick's out-of-fold sides on 2021-2023 (for
  example, resampled run lengths).
- Add a rotation null as a conjunctive line or at least beside: the pinned side series circularly shifted against d on
  the judged block by 63 to T - 63 sessions, with the observed lift's rank among the shifts.
- Cost: light. Seconds for the rotation; CPU minutes to hours for a calibration at 0.05/132, which needs on the order
  of 10^5-10^6 replications; small memory.

### M-5. The 25-point population reads the judged block, or the atlas

**Where.** Lines 104-106 ("P-15's (`resolved_coin.mark_resolution` at the 100-tick rung, as P-15's cell is built)"),
96-101 (the atlas not read; no stage before C reads a judged-block bar; T-3), and line 448 (T-3).

**Evidence.** No vendored result holds P-15's marks: `rc_width_screen.csv`'s `marks` section has 150 and 200 ticks only.
`mark_resolution` computes the unresolved share "over the whole window" (`resolved_coin.py:241-246`) from walks.

**The failure it allows.** There are two routes, and each breaks a declared line:
- the family builds the walks with its own walker over 2020-2026, which is a stage-A read of judged-block resolution,
  and T-3 (judged bars replaced by a synthetic walk, stages A and B byte-identical) then fails by construction, because
  the marks change;
- or it reads Stage 2's atlas, which line 96 rules out.

**Remedy.** Either write P-15's offered marks into the file as a list from a named Stage 2 source (a disclosed pre-read,
like P-16's), or derive them on 2020-2023 only and say the population is then not P-15's design.

### M-6. What the confirmation tests is not declared

**Where.** Lines 111-116 (the window, the purchase, the D-107 count) and 459-461 ("one confirmation on NQ from
2026-07-17").

**Evidence.** The red team's M1 (`phase0_red_team_2026-11-15.md:417-428`) asks every family to declare what its
confirmation tests. F-02's draft does it: its section 14 gives the pick's lift at 0.05 by Q-16, its placebo line, C2,
resolution, and a length set by power before any confirmation data exist. With six offers a session (M-1), six months
of NQ is about 126 sessions, far fewer than any realistic lift needs.

**The failure it allows.** A carried pick is confirmed by a statistic, level or length chosen after the pass.

**Remedy.** Declare it now in F-02's form: C1, C1-d and C1-f on the window at the registered level; C2; K2; and the
window's length from Q-16's power at the pick's judged lower bound, computed and written in the carrying row.

---

## MINOR

- **m-1.** E-016 (2) (`DECISIONS.md:23`) keeps `or_width`/`or_pos` in the library but **out of family B** until the
  operator rules. The draft (lines 69-74, 147, 213, 400, 469-470) still keeps them, with 47 features and 53 columns.
  Remedy: 45 features; recount; drop `m_or` (M-1).
- **m-2.** Line 285 defines `L_c = mean(s_i d_i)` over offers; line 286 bootstraps "the session-weighted lift, centred
  at L_c". For filter cells (0-6 offers a session) these differ, and a bootstrap centred at the other estimator is
  biased. Line 234's "one-sided 0.001 critical value" for the canary's maximum is undefined. Remedy: one estimator,
  named in both places; define the canary's critical value.
- **m-3.** Lambda is chosen on the 2021-2023 out-of-fold log loss (lines 257-262), and stage B's maximum over 12 cells
  is read on the same predictions. The search is outside the maximum, so Kill B is laxer than one-sided 0.05. The judged
  level is unaffected (the judged block decides, line 380). Remedy: say so, or take the maximum over lambda as well.
- **m-4.** The filter's 80th percentile comes from "the training fold's own fitted predictions" (line 278). In-sample
  predictions are more extreme than out-of-fold ones, so out of fold fewer than "about a fifth" pass, and with C-1's
  intercept they pass mostly on one side. K1 and K2 "in every choice year" (lines 220, 222) are undefined for filter
  cells in 2020, which has no out-of-fold prediction. Remedy: centre at p~ (C-1); threshold from the inner folds'
  out-of-fold predictions; name the years.
- **m-5.** The positive control (lines 226-229) passes whatever the alignment. Volatility clusters across sessions, so
  resolution labels shifted by a session at the same mark still give AUC > 0.5 from `rv_tod`, `atr_ratio` and
  `range_prior`. It checks that the pipeline runs, not that features and labels line up. Remedy: add a negative control
  (labels shifted one session at the same mark; AUC must fall by a declared margin), or rest alignment on T-14 (section
  14 item 5) and say so.
- **m-6.** Inputs fitted on 2020-2026 that T-3 cannot see:
  - P-16's offered marks (disclosed, lines 107-108): side-neutral, but the marks were cut at 5 % over the whole window,
    so the judged K2 floor (line 316) was partly read in advance. 09:00 is offered at 4.85 %.
  - `u_value_map.csv` (D-667's solves from the registered edge rows, which drive the pick and C2).
  - `stop_band.csv`.

  Remedy: list them as disclosed pre-reads beside the verdict, each with what it can and cannot bias.
- **m-7.** Lines 99-101 rest the seal on T-3 alone. No purpose-tagged reader, read ledger or H-2 hook exists in
  `extended/` or `scripts/` (audit R-4, R-5, H-2). Remedy: depend on them before stage A, or name the gap.
- **m-8.** Lines 238-239 ("declared a screen ... a pass is a lead for confirmation only") against lines 459-461 (CARRIED
  takes a model card, the gatekeeper, the auditor, a confirmation). Remedy: say whether a screen's pass is CARRIED.
- **m-9.** The audit (`D_protocol.md:262-266`) reads Stage 2 D-621 (4)(d) ("no fitted values") as forbidding a fitted
  model outright, so "family B needs its own row". The gatekeeper's item 3 repeats D-621 (4)(d). Remedy: name the row the
  lead must write, admitting fitted coefficients inside the declared walk-forward.
- **m-10.** C2 (line 314) does not say whether "uses" are the choice block's (as in the pick, line 294) or the judged
  block's. Remedy: say.

## NOTE

- **n-1.** Open question 4 (lines 472-475): E-016 (3) aligned the gatekeeper's item 6 with E-008. Its item 7 still
  refuses non-integer seeds, so the seeds go in at pinning, checked unique (T-12).
- **n-2.** The embargo's reason (lines 254-256) is muddled. In a forward walk no training label resolves in a test
  session, and test features reading training sessions is not leakage. The 22 sessions are harmless, as is the final
  model's lack of one.
- **n-3.** For entries at 08:35-09:00 the breakeven move fires at the 13:00 CT session open (`fv3_core.py:53`; the walk
  takes the next of 17:00, 19:00, 08:30, 13:00). In win units the move can turn the leading side's later target into a
  breakeven exit, so a real lift can also shrink (lines 129-131 say "only enlarge"). At these marks few trades are open
  at 13:00 (R = 1 unresolved by 15:10 is at most 0.6 %, rows 191-197), so the effect is negligible.
- **n-4.** Day kinds (`atlas_local.py:64-69`) exclude a day as an early close from its own last bar, and as FOMC from a
  set that includes the 2020-03-03 10:00 ET unscheduled statement, which came after that day's 08:30-08:55 alerts. Both
  are training-only and side-neutral; lines 108-110 disclose the second.
- **n-5.** `walker.py:23`: a market fill is booked at the bar's open, its tick charged as a cost. So the pair shares an
  entry price as line 121 says, and the coin-twin lift is the coin's expectation. The mirror (a market order the other
  way at the same bar) is realisable.
- **n-6.** The null canary (lines 230-234) runs inside stage A, which line 216 calls "counts and side-free columns
  only", on choice-block direction outcomes (flipped). Harmless before stage B; say so.
- **n-7.** If F-B reads the judged block and closes, a later family on the same features and population (the dropped
  tree, line 412) may not be judged there (audit 1.5 (c), R-8). Section 15 should say so.

---

## What I tried that found nothing

- **Every feature's slice, by reading `extended/features.py`:**
  - each per-alert value is `[..., :s]` or a prefix sum ending at s - 1;
  - each day-level value is from earlier days, or frozen before 08:30 (overnight levels, `gap`) or at 09:00 (the opening
    range, used only from 09:00);
  - the index arithmetic of `_prior_median` (row d = days d-20..d-1) and `_prior_mean` (days d-14..d-1) checks out;
  - `compute_chunked`'s 22 days cover every window (`ret_20d` needs 21).
- **The roll.** The store charts the previous trading day's volume leader (`vendor/stage2/data/README.md:160-161`), so
  the day's contract, `prior_ok` and `m_cross` are known at its open. The shift test leaves that label alone, which is
  correct.
- **Calendars.**
  - BLS days come from the schedule pages (provenance file). The post-shutdown 2025 dates were announced before their
    days, and 2025-10-03, cancelled and known to be, is not flagged.
  - `days_to_fomc` uses scheduled meetings only, with the March 2020 cancellation handled from 2020-03-13.
  - `days_since_fomc` counts statements strictly before the day. The 2026-09-16 statement in the files is a public
    schedule, not NQ.
- **The tests.**
  - `test_features_lookahead.py` replaces and deletes every bar from each cut, including the cut's own alert, checks the
    normalisers on the cut's day, and shows non-vacuity (`ret_5` changes after the cut).
  - The planted one-minute leak and the full-sample z-score are caught.
  - A residual gap: the calendars are not perturbed, which is correct (they are not bars).
- **The follow twin's arithmetic.** `sign(ret_15)` at the alert is `mom15` at L = 5 exactly (M-2 is about which twin,
  not how it is computed).
- **The pair.**
  - Both sides enter at the open of the same bar and are walked by the same rules: stop first on a two-barrier bar,
    the same flatten, costs by exit kind.
  - So `mean(s d)` is the excess over the coin; there is no fill-bar asymmetry (the audit's D-1 needs a resting entry).
  - Latency: features use bars stamped at or before t - 1, entry is at the t + 5 open.
- **The counts and levels.**
  - 12 cells and 20 configurations; 0.05/132 at k = 11.
  - One cell judged, and three conjunctive lines at one level (intersection-union, level held).
  - Stage B spends no program budget (E-003 (f), gatekeeper item 4).
- **Cross-block leakage.** Training ends 2023-12-29, labels resolve the same session, the judged block starts
  2024-01-02, and every normaliser is trailing or in-fold. No purge is needed across the boundary.
- **Prior-exposure honesty** (lines 65-68). The draft does say the judged block is late development for direction. That
  part stands; M-1 and M-2 are about what it leaves out.

## What I could not check

- **P-15's 25-point offered marks.** They are not vendored, so neither the 25-point population nor whether the
  opening-range features exist there. Specify: kinds-only `mark_resolution` at 100 ticks from Stage 2's walks or this
  walker, on 2020-2023 and on 2020-2026 separately. Light to moderate; reads resolution only.
- **The real side persistence and the drift regimes of these six marks.** These need the bars; the magnitudes in M-4
  are assumptions. Specify: after stage B, the out-of-fold sides' run lengths per fold (light, part of stage B's
  output).
- **Whether `lbrk5` and `lnbar1x4` at L = 5 out-lift `mom15` at L = 5 on these marks** (M-2). Specify: Stage 2's event
  code on the choice block's pairs only (already read by Stage 2 at L = 0; light).
- **Q-16's statistic.** It is not merged.
- **The value map's places mapped to design (i)'s journey** (M-3). This needs the scorecard run.

## Appendix: the synthetic checks (scratch, exploratory, seeds fixed before running)

**A. Side collapse (C-1); seed 1.** The draft's objective (session-weighted mean log loss + lambda/2 ||beta||^2, free
intercept, L-BFGS-B, gtol 1e-10). The 51 % row is the same script with `0.53` replaced by `0.51`.

```python
import numpy as np
from scipy.optimize import minimize
rng = np.random.default_rng(1)
D, m, p, Dt = 750, 6, 50, 630
def make(Dn, base):
    X = rng.standard_normal((Dn, m, p)); X[:, :, :25] = X[:, :1, :25] + 0.3 * X[:, :, :25]
    X = (X - X.mean((0, 1))) / X.std((0, 1))
    u = rng.random(Dn) < base; flip = rng.random((Dn, m)) < 0.15
    y = np.where(flip, ~u[:, None], u[:, None]).astype(float)
    return X.reshape(-1, p), y.ravel()
Xtr, ytr = make(D, 0.53); Xte, yte = make(Dt, 0.53); w = np.ones(len(ytr)) / (D * m)
def fit(lam):
    def f(b):
        z = b[0] + Xtr @ b[1:]; g = 1 / (1 + np.exp(-z)) - ytr
        return (w @ (np.logaddexp(0, z) - ytr * z)) + 0.5 * lam * b[1:] @ b[1:], \
               np.concatenate([[w @ g], Xtr.T @ (w * g) + lam * b[1:]])
    return minimize(f, np.zeros(p + 1), jac=True, method="L-BFGS-B", options={"gtol": 1e-10, "maxiter": 2000}).x
for j in range(-2, 3):
    lam = 0.25 * 10 ** (j / 2); b = fit(lam); z = b[0] + Xte @ b[1:]
    med = np.median(1 / (1 + np.exp(-(b[0] + Xtr @ b[1:]))))
    print(lam, np.mean(z > 0), np.mean(1 / (1 + np.exp(-z)) > med), np.mean(np.logaddexp(0, z) - yte * z))
```

**B. Persistent sides against 21-session block means (M-4); seed 2.**

```python
import numpy as np
from scipy import stats
rng = np.random.default_rng(2); T, B, R = 630, 21, 40000; nb = T // B
def chain(q, n):
    sw = rng.random((n, T)) < q; sw[:, 0] = rng.random(n) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)
for a in (0.0, 0.02, 0.03):
    for q in (1 / 60, 1 / 250):
        mu, s = a * chain(q, R), chain(q, R); d = mu + 0.35 * rng.standard_normal((R, T))
        x = (s - s.mean(1, keepdims=True)) * d; bm = x[:, :nb * B].reshape(R, nb, B).mean(2)
        t = bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb))       # NaN where s never switches (s_bar = +-1): no rejection
        print(a, round(1 / q), [np.mean(t > stats.t.ppf(1 - al, nb - 1)) for al in (0.01, 0.001)])
```
