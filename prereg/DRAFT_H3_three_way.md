# H3: the three-way test's calibration, power check and stress, declared (a draft)

**Status: a draft, first text, for the red team (Wave 3.2's read).** Copied from `prereg/TEMPLATE_family.md`'s form and
adapted: H3 is a calibration of the deciding rule, not a family of trades, so it takes **no k**, names no cell that
reaches a judgement of a design, and reads **no held-out session**. It is pinned (by the sha256 of its LF text, in the
lead's row) only after the red team's read; nothing declared is edited after that -- a change is a new declaration.
Its rules come from the design note `docs/plans/THREE_WAY_TEST_design.md` (merged under E-213, after three red-team
reads, `docs/reviews/THREE_WAY_TEST_2026-11-18.md`, `_v2_`, `_v3_`) and E-213's minors, carried here (Appendix B).

| field | value |
|---|---|
| declaration | H3 (the heavy queue's H3, E-208); no family number, no k |
| what it calibrates | the three-way test's deciding rule (CHARTER 3.6 (f), 3.7, 3.8) on the martingale-outcome reading |
| parts | H3-0 (the probe), H3-A (design checks, before Wave 4.2), H3-D (the deciding calibration, after CHARTER 3.9's pinning row and H4) |
| what it reads | H3-0 and H3-A: no bar (synthetic S1 histories); H3-D: the search years only (NQ 2020-01-02 to 2023-12-29) and H4's search-year outputs |
| never read | the held-out years (2024-01-02 to 2026-07-16); the confirmation window (NQ from 2026-07-17) |
| the build | `extended/three_way_keys.py`, `three_way_seeds.py`, `three_way_redraw.py`, `three_way_journey.py`, `three_way_runner.py`, `three_way_s1.py`, `three_way_stats.py` (Wave 3.2, wt/wt-three) |
| seeds | section 15: the note's block, by role |

No result number is typed here. Every figure of the run plan is printed by `docs/plans/scripts/three_way/h3_plan.py`
from declared constants (Appendix A), and `tests/test_h3_draft.py` holds the appendix to the script line for line.

---

## 0. In plain words (for the operator)

Before any design is judged on the held-out years, the test that judges it must be shown to do two things: **not pass
designs that are no better than the baselines** (its size) and **pass designs that are better by the amount that
matters** (its power). H3 checks both, on made-up histories first (H3-A) and then on histories built from the search
years (H3-D), never on the held-out years. Every trade's result is redrawn by a fair coin at the odds its stop and
target give (zero edge), so luck is the only thing that can make one design look better than another; H3 measures
how often that luck fools the test. It also checks the test's behaviour when fills are one or two ticks worse. **A
pass** means the test is allowed to judge the search's finalists. **A fail** means the search does not pin; the lead
puts the data question (more history, a purchase the operator decides) with H3's result.

## 1. Hypothesis: what H3 tests, its sources, and the sign stated in advance

H3 tests the deciding rule, not a market mechanism:
- **(S) size:** on every same-design null (the antithetic twin, the disjoint seed sets, the exact-centred toy pair),
  the rule's rejection rate at each feasible level is at most that level (expected sign: no laxity; the full level
  rests on the theorems below, whose premises H3 checks).
- **(P) power:** at a planted improvement of delta\* (the lead's, Wave 4.2; O-3), the whole rule passes with
  probability at least pi\* (expected: met at the J and m H3-D fixes, or the gate fails).
- **(H) history luck:** the history null's false-pass rate, printed per finalist with its pair's label (expected: at
  most the share of histories on which the time conditions hold with theta(H) > 0; 2.7).

**Sources.** W. Hoeffding (1963), J. Amer. Statist. Assoc. 58, "Probability inequalities for sums of bounded random
variables"; C. McDiarmid (1989), Surveys in Combinatorics, "On the method of bounded differences"; A. Maurer and
M. Pontil (2009), COLT, "Empirical Bernstein bounds and sample variance penalization", theorem 4; I. Waudby-Smith and
A. Ramdas (2024), J. R. Statist. Soc. B 86, "Estimating means of bounded random variables by betting"; D. Politis and
J. Romano (1994), J. Amer. Statist. Assoc. 89, "The stationary bootstrap"; D. Slepian (1962), Bell System Tech. J. 41,
"The one-sided barrier problem for Gaussian noise". The race's law is the driftless first exit (gambler's ruin), as
Stage 2's `adapter.BinaryDraw` races it (D-150, D-156).

## 2. Prior exposure

- H3-0 and H3-A read no bar. H3-D reads the search years only, through the runner's refusal (section 4).
- Q-16's real paired nulls (E-035, E-083, E-085) read the judged block, the held-out years: they are **not** H3's
  nulls (the note's m-7) and Q-16 enters the held-out read ledger of CHARTER 3.6 (b) (the note, 3.1, for the lead).
- The baselines (naive coin, P-14, P-15, P-16) were chosen by Stage 2 on the whole development window (E-208): for
  them "held out" means unread by this search only; H3 uses their search-year outputs (H4) and their schedules only.
- The note's constants were written with no bar and no outcome read; `results/calibration_p.csv` was opened for its
  header only. H3 inherits that.

## 3. Contract fit and conduct (CHARTER section 4, item by item)

| item | H3's answer |
|---|---|
| stops in the stop band, above the cost floor | H3 trades nothing. Its toys' brackets are stylised; H3-D's are the baselines' registered brackets and H4's designs' |
| at least five minutes from alert to order | the toys' latency is five minutes (`three_way_s1.DesignSpec.latency`); the baselines' registered latencies in H3-D |
| one position at a time per firm, five minutes flat | **overlap is refused**: the runner refuses any schedule whose positions' holding intervals overlap, on the scheduled entries and the run's exit times, before any draw (`three_way_journey.Schedule`; the note's 1.6, B-3, N-4) |
| at most 5 % of trades reaching the 15:10 CT flatten | not a gate of H3; the share of time-limited trades is reported beside each part (R-10) |
| realised risk within 10 % on at least 90 % of trades | not a gate of H3 (no real fill) |
| no entry before 07:35:00 CT on a BLS 08:30 day; FOMC days out | the toys carry no calendar; H3-D's schedules come from sources that apply it (`extended/triggers.py`, Q-152) |
| **conduct tier 1** | no hedging, no opposite positions (overlap refused), no maximum size into news. **The copy-against-stagger check's design X sends one trade to N accounts at one moment: a test fixture only**, never a candidate (the note, 1.6); it runs only once the template defines overlap |
| conduct tier 2 modelled and off; tier 3 priced, 0 % denial in the verdict | the deciding reading is at 0 % denial; the denial ladder runs beside on its own `enforce` stream, seeded apart from the coin (section 7) |
| firm rules only from the verified ledger | H3-0 and H3-A use **toy rules labelled as no firm's** (`three_way_journey.ToyRules`); H3-D's firm rules are Topstep's from `vendor/stage2/config/rules.yaml` through the vendored engine, never typed |
| no automated or API order entry | none: H3 places no order |

## 4. Data, blocks, the seal and the confirmation window

- **H3-0, H3-A:** no data. Synthetic S1 histories (`three_way_s1.generate`), stylised parameters (section 7).
- **H3-D:** the search years, NQ 2020-01-02 to 2023-12-29, read through `extended/reader.py`; S1's parameters fitted
  there; S2's stationary-bootstrap resamples of the search years (`three_way_stats.resampled_size` refuses any session
  from 2024-01-02); H4's search-year per-seed outputs.
- **The held-out years** (2024-01-02 to 2026-07-16, on `results/q82_judged_sessions.csv`) are read by no part of H3.
  H7, the held-out test, is Wave 6's and is listed in Appendix A for its cost only.
- **The confirmation window:** NQ from 2026-07-17, never read.
- **Disclosed pre-reads:** none by H3.

## 5. Supply: the toys' schedules

- **S1** (the note's 2.6): log volatility an AR(1) with an optional slow two-state regime; two trigger streams A and B,
  independent and identically distributed given the day's volatility, Poisson counts whose rate follows the
  volatility, decision slots uniform from 08:30 to 14:00 CT; holding times exponential, lengthening with the stop over
  the volatility; a hold past the time limit ends there (R-10's walk). Each design takes its stream's arrivals in time
  order, skipping any while its position is open.
- Supply (trades a session and a block) is **counted from the schedules alone**, before any outcome, and written in
  each part's result beside its rates.
- H3-D's schedules are the baselines' registered trades and H4's designs', as run (CHARTER 3.2).

## 6. The side, its persistence and the fill intensity

- **No trade-lift line is decided here** (E-208 retired it); E-035 (6)'s persistence and E-187's band do not apply.
- **The side is the coin's** under the design note's keying, choice 3 (1.5): one uniform per user and moment, keyed
  `[role seed, 3, part, history, seed index, start, underlying, moment, draw kind]`, every word below 2^32, the start in
  every key (the build refuses a unit key without it), no account and no firm index. **On the deciding reading the side
  moves no outcome**: the redraw races the barriers with direction removed; the side is drawn for the as-walked reading
  beside and for conduct.

## 7. Parameters: fixed / searched / dropped

| parameter | what it is, in a phrase | class | value or source |
|---|---|---|---|
| alpha | the family level the rule is calibrated at | fixed | 0.05 / (k (k + 1)) at the search's k; k = 13 next (`three_way_stats.level`) |
| feasible levels | where a size is checked by count | fixed | 0.05, 0.01, 0.001 (the note's 2.6) |
| pi\* | the power target | fixed | `family_stats.MDL_POWER` |
| delta\* | the size that matters | fixed, the lead's (O-3, Wave 4.2) | a parameter of H3-D, set before it |
| the race's loss barrier | the stop exit's own cost in the race (the third read's M-4) | fixed | L = min(l, c - x_stop), c the cushion after the entry cost, x_stop the stop exit's own cost (commission plus declared stop slippage); p = L / (L + g); +g less x_target, else -L less x_stop |
| the race's lattice | L rounded inward | fixed | whole ticks (`three_way_redraw.LATTICE` = 1); no trade where L <= 0 |
| R-10's stopped walk | the redraw of a trade ending at a time limit | fixed | the search template's house form (wt/wt-lit, with its red team): lattice step s dividing l and g; loss barrier as the race's with the larger of x_stop and the flatten cost, rounded inward to the lattice; n = round(sigma^2 T / s^2), halves up, at least one, sigma at the alert; outcomes +g, -L or the walk's value at n, each with its exit's cost |
| the exit-state map | which terminal state takes which law | fixed | `three_way_redraw.EXIT_LAW` (R-10's table); any other state refused |
| the worse-fill stress | measure 29 | fixed, declared and counted | +1 and +2 ticks on every fill (the entry and each exit), the design and every baseline alike: 2 arms a compared design (`three_way_redraw.WORSE_FILL_TICKS`, `stress_cells`) |
| the deciding bound | by the composite's form | fixed | section 9 (2.2 (a) or (b)) |
| J, m | seeds and seed-set size | fixed in H3-D before the search's pin | by 2.5's formulas at delta\* and H4's sigma; H3-A reports both of 2.2 (b)'s bounds' J and applies nothing |
| the betting bound's form | WSR's one-sided capital | fixed | predictable plug-in bets truncated at c / m, c = 1/2; a grid of 2001 points on [0, 1]; the bound the largest grid point below which every point is rejected (`three_way_stats.betting_lower`) |
| the disjoint pool's variance tolerance | 2.3's guard | fixed | within 0.5 of twice the single arm's (`null_pool_guards`) |
| n_min | (Y)'s and (R)'s group minimum | fixed in 3.9's row | proposed 21 (the note's 3.4, calendar only) |
| vacuity | a time condition's label | fixed | a stated size of one half or more is labelled vacuous |
| the resample's mean block | S2's blocks | fixed | at least h\* (`resampled_size` refuses a shorter one) |
| H_g | D-145's gate horizon | fixed | 504 sessions (`three_way_stats.H_GATE`; Stage 2's gate configs) |
| the gate's quantile | O-6 (a) | fixed in 3.9's row | over coin seeds only on the held-out years; the search years' history-block reading beside |
| the limits' form | O-5 (E-221) | fixed | inside each limit at the point estimate, failed only when the evidence shows it crosses, the coin-seed half-width at the pinned margin's level (`limit_check`) |
| S1's parameters | the toy generator | fixed per part: stylised in H3-A, fitted on the search years in H3-D | `three_way_s1.S1Params`; H3-D's fit is declared in its own row before it runs |
| the toy rules | H3-0's and H3-A's accounts | fixed, stylised, no firm's | `three_way_journey.ToyRules`, the values written in each part's manifest |
| the part cap | the cut rule | fixed | 8 hours at H3-0's measured cost (`three_way_arith.PART_CAP_H`) |
| overlapping designs | several positions at once | **dropped** until the template defines one shared driftless path per underlying | refused by the runner (section 3) |
| a t-test | any t as a decision | **dropped** | the larger-of t of E-035 beside, deciding nothing |

## 8. The cells and the count

- **H3 takes no k** and judges no design; its counts are of checks, every one reported, none dropped after a look.
- **The size checks:** (null classes: the antithetic twin, the disjoint sets, the exact-centred pair = 3) x (bounds:
  2.2 (a)'s, the empirical-Bernstein, the betting = 3) x (levels: three feasible and alpha = 4) x R histories, per
  part (A1, A2, D1); each history reported alone and pooled.
- **The history null:** one rate per finalist (or per stylised pair in H3-A), each labelled with its pair (A3, D2).
- **The power checks:** plants P1 to P4 x the grid of sizes, each line's pass rate and the conjoint MDL (A4, D3).
- **The stress:** 2 worse fills x (the design and four baselines) per compared pair (`stress_cells`).
- The program's honesty sentence: Stage 2's programs S and U and this repository's F-01 to F-03 read the development
  window; H3 adds no read of the held-out years, and the held-out test's level stays nominal while the held-out read
  ledger is not empty (CHARTER 3.6 (b)).

## 9. The deciding rule H3 calibrates

**The reading.** The martingale-outcome reading (CHARTER 3.2), identically for every arm: fills, timing and costs as
run; each trade's outcome redrawn by the race (or R-10's walk), **the stop exit's own cost in the race** (section 7).
Every trade's gross expectation is exactly zero and its net exactly minus its expected costs; a costed loss lands at
most on the floor, so the engine's clip never binds (`three_way_redraw.race_net`, `walk_net`, exact-fraction tests).

**The coin field.** Every random element of a journey is a fixed function of the coin field: the side, the race's
uniform, the walk's steps, measure 28's missed signal, each its own draw kind of the coin key; the denial ladder's
draws are the `enforce` kind, keyed per unit, account and request, **seeded apart** (its own tag), so the ladder moves
no coin draw. The generator: numpy's Philox (4x64) seeded by `SeedSequence(key)`, the uniform (2 i + 1) 2^-53 on the
symmetric grid; the antithetic twin reads 1 - u exactly. Keys are compared by `generate_state`; two keys with one state
refuse the run.

**2.2 (a), copied from the note between its markers, with the third read's minors carried (each insertion marked):**

<!-- h3-admission: begin -->
**Admission to the Hoeffding/McDiarmid bound (2.2 (a)).**
1. **What it admits.** This bound decides a comparison only if **every** dimension d of the pinned composite, or the
   pinned fallback, is an **unconditional mean over all of E_{h_d}** of a per-unit value x_d(u):
   Phi_d = (1 / (J |E_{h_d}|)) x (the sum of x_d(u) over every unit u of E_{h_d} under the test's J seeds).
   - The same E_{h_d} serves the design, every baseline and every seed.
   - Membership of E_{h_d} depends on the calendar only, never on a unit's value.
   - x_d(u) depends on the held-out history and on unit u's own coin field only.
2. **Where the bounds come from.** Each x_d carries **a priori bounds** a_d <= x_d(u) <= a_d + r_d, fixed before any
   read, from one of two sources only:
   - (i) contract arithmetic or the verified rules: an indicator lies in [0, 1] (r_d = 1); a count of sessions in
     [0, W + 1], W the dimension's window, its censored value W + 1 included [M-2]; a dollar amount within the limits that the firm's verified rules and the design's declared purchase cap
     imply over h_d sessions;
   - (ii) a per-unit clip written into the dimension's own definition, x_d(u) = clip(y_d(u), a_d, a_d + r_d), pinned
     in CHARTER 3.9's row and shown to the operator with the composite's caps.

   **No bound is ever estimated from data, on any years.**
   **A bound from source (i) is also written into the dimension's definition as a clip**, x_d(u) =
   clip(y_d(u), a_d, a_d + r_d), so the bound holds on every coin field by construction. The refusal stays, as a
   check that the arithmetic was right [M-1].
3. **What it does not admit.** These are decided by 2.2 (b) whenever the composite holds one:
   - a conditional share or mean, whose denominator is a random subset of E_{h_d} (the share falling back among those
     who reached break-even, for example);
   - a ratio of means (payouts per funded account, for example);
   - a tail mean (CVaR10);
   - a quantile.
   - a dimension whose per-unit value has neither an arithmetic bound nor a pinned clip [M-3].

   A unit-count share, an indicator averaged over all of E_{h_d}, is admitted with r_d = 1. The fallback `P_B` is
   admitted: its per-unit value, the share of months 1 to 3 ahead under B (MEASURES.md section 2), lies in [0, 1].
4. **The bound.** With every dimension admitted, changing one unit's coin field moves C(f) - C(beta) by at most

       c_u = sum over d of 1[u in E_{h_d}] x w_d x 2 r_d / ((hi_d - lo_d) x J x |E_{h_d}|)

   The clip is 1-Lipschitz; for the unclipped fallback, w = 1 and hi - lo = 1. The deciding lower limit is

       LB = Delta-hat - sqrt( ln(1/alpha) x (the sum of c_u^2 over every unit) / 2 )

   For the fallback that is Delta-bar - sqrt( 2 ln(1/alpha) / (J |E_63|) ). H0(f, beta) is rejected when LB > 0.
5. **Only under choice 3.** This branch is valid only when every coin key carries the unit's start, so the units are
   independent given H. Under any keying that shares draws across starts, only 2.2 (b) is valid.
6. **The build's refusals.** The build refuses the whole run, before any statistic is written:
   - on the first per-unit value outside its declared bounds, for any design, baseline, unit or seed;
   - on any coin key that does not carry the unit's start.

   **The bounds are exercised on the build's tests, H3-D and H4 before any held-out read. A refusal on the
   held-out run ends the held-out test for that finalist as a failure: it is diagnosed, never re-run with new
   bounds** [M-1].
<!-- h3-admission: end -->

**2.2 (b).** Any composite holding a dimension 2.2 (a) does not admit is decided over J i.i.d. seed-set replicates
Delta_j in [-1, 1], by the one-sided empirical-Bernstein bound (Maurer and Pontil, theorem 4, on (Delta + 1) / 2) or
the hedged betting bound (section 7): **the one of the two that needs the smaller J for power pi\* at delta\*
decides**, applied in H3-D only, after Wave 4.2 sets delta\* and with H4's search-year sigma, before the search's pin.
**No t decides, in any branch.**

**The time legs** (consistency conditions, not tests at alpha): (Y) every start-year group of Y_ok positive, (R) every
regime of R_ok positive, (H) the held-out scope; each with its stated size (the white-noise lower bound on the actual
groups with the overlap counted, and the history null's generator's) and its vacuity label. **The rule for one pair:**
LB > 0 and (Y) and (R) and (H); for the finalist, all four baselines (an intersection-union test), with CHARTER 3.8
(a)'s limits in O-5's form and (c)'s floors, the zero-edge long-run gate at H_g = 504 among them.

## 10. Power before the pin

- **The plants** (the note's 4.2): P1 linear (the null terms plus delta; `family_stats.conjoint_mdl_linear`); P2
  structural (a lower fee, a shorter payout delay, a cheaper purchase rule; its true delta from the exact program or a
  pool of at least a hundred times J); P3 edge plants (the race's win probability raised by epsilon, the design's arm
  only; F-04's value arm); P4 regime-varying, delta_t = delta\* (1 + a rho_t), rho_t a slow sign.
- **The conjoint MDL** at alpha over every leg together (`family_stats.conjoint_mdl_grid`); the line has power at
  delta\* when it is at most delta\*.
- **The gate's other clauses** (the note's 4.4): every limit's headroom at least (c_L + z_pi) sigma_M / sqrt(J) for a
  design equal to the best baseline; the complete-start count at H_g reaching the minimum pinned in 3.9.
- If any fails, the search does not pin, and the data question goes to the operator with H3-D's result (E-007 (2)).

## 11. The stages and the kill rules

- **H3-0, the probe** (light enough to run first, still under the lock): measures the process base M_0 and the cost c
  of one lane-trade **with the declared generator's keyed draws included**, on toys; applies the cut rule to every
  later part at the measured c (Appendix A) and records the cut sizes in the lead's row before any part runs.
- **H3-A, design checks** (before Wave 4.2): A1 the same-design nulls on placeholder composites (`P_B` at a placeholder
  budget, and a clipped toy composite); A2 the exact-centred toy null (the exact program; barrier and R-10 trades);
  A3 the history null on S1 (the stream swap); A4 the plants P2 to P4, and the copy-against-stagger check **only once
  the template defines overlap** (until then A4 runs the plants alone, and says so). **Kill:** a premise failing (a pool
  not centred, an asymmetric twin, a term out of range, a key guard refusal) stops the part and goes to the failure
  protocol; a size count whose 95 % Clopper-Pearson interval lies wholly above its feasible level is a laxity, recorded
  and diagnosed before H3-D.
- **CHARTER 3.9's pinning row** (Wave 4.2): the composite, its caps and clips, delta\*, n_min, the gate's quantile and
  minimum, the limits.
- **H3-D, the deciding calibration** (after the pinning row and H4, before the search's pin): D1 the same-design nulls
  on the pinned rule; D2 the history null on S1 fitted to the search years and on S2; D3 the power gate with its full-J
  check. **Kill:** as H3-A's, and the power gate's failure ends the search's pin (section 10).

## 12. Beside, never deciding

The as-walked (reflected) reading and its gap from the martingale-outcome reading (the path-structure edge); the
as-traded reading for resting triggers; the larger-of t of E-035; per group and per regime Delta-hat with its coin-noise
standard error; the exact sign-flip p-value over complete blocks with its floor 2^-B; the share of seed sets at a cap
and the note that under clipping the estimand moves with J near a cap (N-11); S2's distinct-block count; the shortcut's
error in the history null; the denial ladder.

## 13. The judged block's reads

- **Judged-block reads:** none.

H3 reads no session of the held-out years in any part.

## 14. What a pass and a fail mean

- **A pass:** every size count shows no laxity at the feasible levels, every premise holds, the history null's rate is
  printed with its label, and the power gate passes at delta\*: the deciding rule, with H3-D's J and m, may judge the
  search's finalists in H7.
- **A fail:** the search does not pin. A laxity is diagnosed by the failure protocol (terminal states, stage
  decomposition, the component alone, replication with seeds fixed before), never re-run until it passes; the power
  gate's failure puts the data question to the operator.
- **The confirmation:** not H3's; NQ from 2026-07-17, for a carried design only, a purchase.

## 15. Seeds -- by role, found nowhere else

The note's block (its section 7), assigned to H3. Each seed draws only its role; within a role, every draw is a child
keyed by the fixed-length key of its kind (`three_way_keys.seed_key`: the seed, a nonzero tag, exactly the kind's
fields, every word below 2^32), never the seed plus an offset. **The part is in every key** (`three_way_seeds.PARTS`),
so two parts never read one field. The runner reads its seeds from `extended/three_way_seeds.py` only, and
`three_way_keys.seed_key` refuses any seed of the block that module did not issue (a literal or a derived value).

| seed | role | status |
|---|---|---|
| 20265870 | the unit tests: this note's test (the bounds' coverage check) and the H3 build's (synthetic toys only) | tests |
| 20265871 | H3-0, the probe's toys | design check |
| 20265872 | H3-A: the S1 histories of A1 to A4 (the generator's draws; P4's regime signs) | design check |
| 20265873 | H3-A: the coin fields of A1, A2 and A4 (every arm; the disjoint sets by seed index) | design check |
| 20265874 | H3-A3: the history null's histories, their stream swaps and their pairs' coin fields | design check |
| 20265875 | H3-D: the S1 histories fitted to the search years, and the S2 resamples' block indices | deciding |
| 20265876 | H3-D: the coin fields of D1 and D3 (the part in every key keeps them apart) | deciding |
| 20265877 | H3-D2: the history null's symmetry coins and its pairs' coin fields | deciding |
| 20265878 | H3-D3: the plants' own draws (P3's tilts, P4's regime signs) | deciding |
| 20265879 | spare | spare, drawn by nothing |

- **This build's tests** use the tests' seed with the `test` kind and test ids 11 to 19 (`three_way_seeds.TEST_IDS`),
  and the coin kind under the tests' part; the note's own test uses test id 1 and is never shared.
- **The search** (2026-11-18, before this text was committed; the house search, word-bounded on the block's ten
  values):
  - `git grep -IlwE` over every branch, remote and tag (26 refs): the design note only;
  - every line added or removed in every reachable commit (`git log --all -p`, 574 commits): the design note only;
  - `grep -rIlwE --exclude-dir=.git --exclude-dir=data` over this worktree's working files: the design note, this
    declaration and the build's seed module -- the files the note's test allows (`tests/test_three_way_design.py`,
    `DECLARED_USES`); the arithmetic fold finds the block's construction only in that test and the seed module
    (`DERIVED_USES`). Other worktrees' uncommitted files were not read (a worker reads only its own tree); the lead
    repeats the search over them at the pin.
- **Trailing zeros and split words.** numpy reads `[a, b]` and `[a, b, 0, 0]` as one stream and splits a word of 2^32
  or more; the fixed length per kind, the nonzero tag and the bound on every word make that impossible, and the guard
  compares `generate_state`, never the integers.

## 16. The run order -- refusals first

1. **Refusals first**, before anything is read: this declaration pinned and unedited; the identities on record as
   holding for the runner's cover (the runner's own identity, below); a clean checkout of a named commit
   (`scripts/run_clean.py`); the run lock held, one heavy job on the machine; memory checked.
2. **The runner's identity** (before any H3-D output is believed): on the search years, each baseline's schedule
   through the runner equals its registered trades (times and brackets, path for path), and the runner's race at no
   cost equals `adapter.BinaryDraw`'s on the same uniforms (held by the build's test at no cost already).
3. **H3-0**, then **H3-A**'s parts, one heavy slot each, each watched to its exit; then the pinning row; then H4; then
   **H3-D**'s parts.
4. Each output written with its manifest (`write_result`) from a clean run, carrying its seed map and its keys' kinds.
   A failed check stays on record.

## 17. The build and its tests

Wave 3.2 (wt/wt-three), in this repository's package, nothing vendored edited, nothing added to an identity's cover:
the keys and the generator (`three_way_keys`), the seed module (`three_way_seeds`), the redraw (`three_way_redraw`),
the journey and its exact program (`three_way_journey`), the seed-paired runner (`three_way_runner`), S1
(`three_way_s1`) and the statistics (`three_way_stats`); tests `tests/test_three_way_keys.py`, `_redraw.py`,
`_runner.py`, `_stats.py`, `_mutations.py` and `tests/test_h3_draft.py`, on synthetic data with known answers.

**Open before H3-0 (for the red team and the lead).**
- **The generator's cost.** The declared generator hashes each key (`SeedSequence`) and builds a Philox state per
  draw; the plan's assumed costs (Appendix A) may sit below what it costs a lane-trade. If H3-0's measured c puts a
  part over the cap, the remedy is declared before the part runs: a vectorised implementation of **the same law**
  (SeedSequence's hash and Philox4x64-10 on arrays), admitted only when a test holds it bit for bit equal to
  `triggers.coin_uniform` on every key kind; any other generator is a new declaration.
- **The runner on the vendored engine** (H3-D, H4): the toy rules are for H3-0 and H3-A; H3-D's journeys run the
  firm's verified rules through the vendored lockstep with the runner's race as its draw (the form `race_dollars`
  holds equal to `BinaryDraw` at no cost), which is the next build item.
- **Wave 3.1's flip refusal** (`user_beside.base_problems`) stays: the vendored engine draws a flip stream's daily
  direction (`lockstep.py`, `child_seed(seed, 10, 0)`) and the payout denial (`child_seed(seed, 9, 0)`) from one path
  seed and hands the direction to the day hook; separating them there needs a keyed flip draw class and a wrapped day
  hook, and `user_beside.py` is in Q-93's and Q-101's covers. On this runner every stream, a flip-like one included, is
  a schedule of trades whose side and outcome come from the coin field, with the ladder on its own stream.

## 18. The pin's conditions

- The red team's read answered; the gatekeeper's approval; the seed search repeated at the pin.
- Wave 2's template (R-10's house form, the m-2 and m-3 clauses) merged, or this text's section 7 rows for R-10 kept as
  written here with the template's red team's findings carried.
- H3-D's parts are re-declared by size in the lead's row after H3-0 (the cut rule), before they run.

## 19. Anything chosen after seeing results

*(Empty at the pin.)*

---

## Appendix A. The run plan (printed by `docs/plans/scripts/three_way/h3_plan.py`)

The sizes are the note's proposals with H3-0 added; the hours are at assumed costs, never a measurement. H7 is listed
for its cost only (Wave 6).

<!-- h3_plan: begin -->
```text
H3's parts: part | seed roles | reads | R arms M T h | lane-trades | hours over 2 workers at the assumed costs 0.05 us, 0.5 us, 5.0 us a lane-trade
  H3-0 probe                 | h3_0_probe | synthetic toys | R=1 arms=5 M=64 T=40 h=63 | 3.226e+06 | 0.0  0.0  0.0
  A1 same-design nulls       | h3a_histories, h3a_coins | S1, stylised | R=20 arms=3 M=10000 T=120 h=63 | 1.814e+10 | 0.1  1.3  12.6  over 8 h from 5.0 us: cut M first or split
  A2 exact-centred toy null  | h3a_histories, h3a_coins | S1 toys, the exact program | R=20 arms=2 M=10000 T=120 h=63 | 1.210e+10 | 0.1  0.8  8.4  over 8 h from 5.0 us: cut M first or split
  A3 history null            | h3a3_history_null | S1, stylised | R=200 arms=2 M=2000 T=120 h=63 | 2.419e+10 | 0.2  1.7  16.8  over 8 h from 5.0 us: cut M first or split
  A4 plants, copy-stagger    | h3a_histories, h3a_coins | S1, stylised | R=10 arms=8 M=10000 T=120 h=63 | 2.419e+10 | 0.2  1.7  16.8  over 8 h from 5.0 us: cut M first or split
  D1 same-design nulls       | h3d_histories, h3d_coins | S1 fitted to the search years; S2 | R=20 arms=3 M=2000 T=412 h=252 | 4.984e+10 | 0.3  3.5  34.6  over 8 h from 5.0 us: cut M first or split
  D2 history null            | h3d_histories, h3d2_history_null | S1 fitted to the search years; S2 | R=200 arms=2 M=500 T=412 h=252 | 8.306e+10 | 0.6  5.8  57.7  over 8 h from 5.0 us: cut M first or split
  D3 power gate plants       | h3d_histories, h3d_coins, h3d3_plants | H4's search-year outputs; S1 fitted; S2 | R=10 arms=6 M=2000 T=412 h=252 | 4.984e+10 | 0.3  3.5  34.6  over 8 h from 5.0 us: cut M first or split
  D3 full-J check (EB)       | h3d_histories, h3d_coins | S1 fitted to the search years | R=5 arms=2 M=20752 T=412 h=252 | 8.618e+10 | 0.6  6.0  59.8  over 8 h from 5.0 us: cut M first or split
  H7 held-out, Hoeffding     | the search declaration's own | the held-out years, once (Wave 6; not H3) | R=1 arms=7 M=100 T=601 h=63 | 1.060e+08 | 0.0  0.0  0.1
  H7 held-out, EB sets       | the search declaration's own | the held-out years, once (Wave 6; not H3) | R=1 arms=7 M=20752 T=412 h=252 | 6.033e+10 | 0.4  4.2  41.9  over 8 h from 5.0 us: cut M first or split
memory: cap 2.5 GB over 2 workers, base 0.4 GB assumed (H3-0 measures it), lane 1344 B: at most 632440 lanes a worker
the cut rule: a part whose estimate at H3-0's measured cost exceeds 8 hours is cut, M first, with the power cost stated, or split into sub-parts each its own heavy slot under run.lock
```
<!-- h3_plan: end -->

## Appendix B. E-213's minors, carried

| minor (the third read) | carried in |
|---|---|
| M-1: each source-(i) bound written as a clip in the definition | section 9, 2.2 (a) item 2 (inserted); `three_way_stats.Dimension.values` |
| M-1: a refused held-out run fails its finalist and is never re-run with new bounds | section 9, 2.2 (a) item 6 (inserted); `BoundRefused`'s message |
| M-2: a censored session count's range is [0, W + 1] | section 9, 2.2 (a) item 2 (i) (replaced); `three_way_stats.session_count` |
| M-3: a dimension with neither bound nor clip is excluded from (a) | section 9, 2.2 (a) item 3 (inserted); `Dimension.admitted` |
| M-4: the stop exit's own cost is in the race | sections 7 and 9; `three_way_redraw.race`, `three_way_journey._barrier` |
