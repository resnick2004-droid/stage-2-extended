# H3: the three-way test's calibration, power check and stress, declared (a draft)

**Status: a draft, third text (corrective cycle 2), for the red team's re-read.** The first text (746a245) was read
in `docs/reviews/BUILD_W32_H3_2026-11-19.md` (blocked: B-1 to B-3, seventeen minors, five notes); the second (adedf7f)
in `docs/reviews/REREADS_W32_W34_O7_2026-11-20.md` (blocked: RB-1; two minors, two notes). The lead's rulings on both are
carried here, and Appendix D maps every finding of both reads to its answer. Copied from `prereg/TEMPLATE_family.md`'s form and
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

- H3-0 and H3-A read no bar. H3-D reads the search years only: a plan with session dates refuses, before any draw,
  a unit whose window holds a session from 2024-01-02 unless the joint held-out test's declaration is named and
  `extended/reader.py` authorises it, and refuses the confirmation window always (`three_way_runner.Plan`; the red
  team's m-10); the bars themselves come only through the reader (section 4).
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
| the race's barrier | fractional, never rounded (the lead's ruling on B-1) | fixed | L = min(l, c - x_stop) as a fraction of a tick, `adapter.BinaryDraw`'s form (CHARTER 3.2; the note's 1.1); a cushion-bound loss ends exactly on the floor and the account fails and is replaced (`three_way_redraw.LATTICE` = None; inward rounding is N-4's rule for the shared path only) |
| the take | decided at the fill (the template's N-1; its read's m-1 on the runner) | fixed | a trade is taken when L_fill = min(l, c - max(x_stop, x_flat)), unrounded, is above $1e-6 of room, for every exit law: it reads the bracket, the room after the entry cost and both exit costs, never the run's exit (`three_way_journey._l_fill`) |
| a lane that cannot take the trade | the lead's rulings on RB-1 and on the template read's B-2 | fixed | where the floor's room binds, the account **fails at the fill** -- its balance taken to the floor, a breach, replaced at that close, **counted apart** (`Records.fill_failures`, reported beside) -- the race's own limit as its barrier goes to zero, and the vendored engine's end for it (its losing branch, held equal lane for lane by the build's test; the engine's winning branch at a cost-sized room, of probability at most the costs over the costs and the target, is not kept); **a room between e + x_stop and e + max(x_stop, x_flat) is a certain failure, though a race at L_race > 0 exists there -- the conservative choice, as E-247 rules it**; where the daily loss limit's room binds, the day ends, and a declared daily limit at or below a trade's costs (at the arm's worse fill) is refused before any draw (`three_way_journey.check_costs`). No account is left alive with room it can never trade (`three_way_journey._classes`) |
| R-10's stopped walk | the redraw of a trade ending at a time limit | fixed | the search template's house form (wt/wt-lit, with its red team) with the lead's ruling on its residual: **lattice step s = max(1, ceil(sigma sqrt(T) / sqrt(1024))) ticks**, sigma at the alert and **T the time limit known at the fill, never the realised exit, the same T for s and n**; **s need not divide the stop or the target**, a barrier off the lattice being reached by the two-point last sub-step, and no trade is ever refused because of its step (the lead's governing rule, s-c; the divisor rule withdrawn), computed with a 1e-12 guard against floating error, which never takes n past 1024 (the red team's diff check NOTE-1); **for a walk that a `news` or `other` exit may end early, T is still the limit known at the fill -- the time limit capped at the 15:10 CT flatten -- and so are s and n; the early exit only truncates the walk, to the steps completed by it (the first floor(n tau / T) of the n, tau the exit's time after the fill, at least one), and never sets s or n** (the red team's diff check NOTE-3, declared before H3-D's schedule builder is built; S1 has no such exit); **a known approximation of the walk, stated beside H3:** at the coarsest n the step's rule admits (n of about 256 once s reaches 2), the lattice's own discretisation residual in P(stop) against Brownian motion is of the order of 1e-3, the same with the barriers on or off the lattice (the red team's diff check `BUILD_W32_sc_2026-11-21` MINOR-2, measured with code of its own); the gross stays exactly zero, so the zero-edge expectation is untouched, and only the split between barrier exits and time exits moves, by that order; the floor-side barrier **the race's own, L = min(l, c - x_stop)**, **fractional** (the lead's ruling on RB-1: the red team's remedy, first form, so a cushion-bound stop ends exactly on the floor and none is left x_flat - x_stop above it), at or above L_fill; its target the as-placed G = min(g, level) (fractional under a rule's profit level); **inside the last lattice step before either barrier the walk resolves by a driftless two-point race between the barrier and the lattice point one step back** (one uniform a step, up where u < p_up: s / (s + rho) below the target, rho / (s + rho) above the floor-side barrier, rho the residual), so each barrier is reached exactly and gross stays zero; **a flatten exit whose cost would pass the floor is clipped at the floor and fails the account, as the engine clips** (the time exit lies above -L, so the clip takes at most x_flat - x_stop); at most 1024 steps a walk (`three_way_journey.WALK_MAX`, the range the generator is admitted on, which the step's rule keeps every walk within: `three_way_redraw.walk_step`); n = round(sigma^2 T / s^2), halves up, at least one, sigma at the alert; outcomes +g, -L or the walk's value at n, each with its exit's cost; read in chunks of 32 steps for the lanes still walking (`three_way_journey.WALK_CHUNK`; the same outcome on the same uniforms) |
| the exit-state map | which terminal state takes which law | fixed | `three_way_redraw.EXIT_LAW` (R-10's table) with **the profit-level row** (the template read's m-2): a rule's exit at a profit level races at the as-placed target G = min(g, (level + entry + x_target) / tick dollars), **the level booked as the vendored engine books its need: the net dollars the trade must make, every cost included** (`lockstep.CombineAccount.need_to_pass`, `vendor/stage2/propedge/campaign/lockstep.py` l.408-419; the need-aware draw "settles ... at exactly the need", `sizing.py` l.380-388), so a win at the level books exactly +level; never the walk; the walk only for a real time limit; any other state refused |
| the stress arms | CHARTER 3.8 (c)'s fill and supply stress | fixed, declared and counted | measure 29's +1 and +2 ticks on every fill (the entry and each exit), and measure 28's 10 % of signals missed (the red team's m-7), each on the design and every baseline alike: 3 arms a compared design (`three_way_runner.stress_arms`, `stress_cells`) |
| the coin generator | the declared law, computed on arrays (Q-170) | fixed | `three_way_fastkeys`: SeedSequence's hash and numpy's Philox (4x64, 10 rounds) vectorised, admitted because its tests hold it bit for bit equal to the scalar path on 10^5 random keys of every field's range, the boundary words, every draw kind and key kind, and every output a walk reads up to 1024 steps; nothing of the law changes |
| the key guard | 2.3's refusal, at run-time cost (the lead's ruling on B-2) | fixed | N-2 checked on every key at construction, unstored; distinctness by the injective packing (one length a kind, distinct nonzero tags, every word below 2^32, the moment's fixed radices; `three_way_keys.packing_problems`), the chance two distinct keys share a 128-bit state at most n^2 / 2^129 (`collision_bound`, printed beside); the stored `generate_state` comparison on a declared sample: every key of a plan's first start under its first 64 seed indices across every arm (`KeyGuard.sampled`, `SAMPLE_SEEDS`), within 1.25 GB a worker at every declared size (tested); the disjoint null's exact check on its two seed-index sets |
| the deciding bound | by the composite's form | fixed | section 9 (2.2 (a) or (b)) |
| J, m | seeds and seed-set size | fixed in H3-D before the search's pin | by 2.5's formulas at delta\* and H4's sigma; H3-A reports both of 2.2 (b)'s bounds' J and applies nothing |
| the betting bound's form | WSR's one-sided capital | fixed | predictable plug-in bets truncated at c / m, c = 1/2 (`three_way_stats.bets`, a function of the earlier replicates only, tested); a grid of 2001 points on [0, 1]; the bound the largest grid point below which every point is rejected (`three_way_stats.betting_lower`) |
| the smaller-J rule's inputs | the red team's m-14 | fixed | J on powers of two from 16 to 32768 (`three_way_stats.SMALLER_J_GRID`), 2000 simulated samples a J (`SMALLER_J_DRAWS`); H3-D's power model the resample with replacement of the pair's per-seed-set search-year replicates from H4, recentred to delta\* (`bootstrap_draw`); H3-A's report the normal model at each pool's own sd; the rng's key the `plant` kind under the D3 plants' seed (H3-D) or the tests' seed (H3-A's report is a design check); a tie goes to the empirical-Bernstein bound |
| P1's linear plant | the planted MDL's form | fixed | only for Hoeffding's, McDiarmid's on unclipped terms and the empirical-Bernstein bound (`three_way_stats.LINEAR_PLANT_BOUNDS`); refused for the betting bound and a clipped composite, which run the plant through the bound itself (`planted_rates`; m-12) |
| the disjoint pool's variance tolerance | 2.3's guard | fixed | within 0.5 of twice the single arm's (`null_pool_guards`) |
| n_min | (Y)'s and (R)'s group minimum | fixed in 3.9's row | proposed 21 (the note's 3.4, calendar only) |
| vacuity | a time condition's label | fixed | a stated size of one half or more is labelled vacuous |
| the resample's mean block | S2's blocks | fixed | at least h\* (`resampled_size` refuses a shorter one) |
| H_g | D-145's gate horizon | fixed | 504 sessions (`three_way_stats.H_GATE`; Stage 2's gate configs) |
| the gate's quantile | O-6 (a) | fixed in 3.9's row | over coin seeds only on the held-out years; the search years' history-block reading beside |
| the gate's denial | CHARTER 3.8 (c) (the red team's m-7) | fixed | read at D-145's tier-3 denial probability of 25 % (`three_way_stats.GATE_DENIAL`, `gate_reading`), the 0 % reading beside, never deciding |
| the limits' form | O-5 as E-230 ruled (the red team's m-6) | fixed | **the point estimate governs**: a design passes a limit when its point estimate is inside it and fails when outside; the one-sided check (B-10's form, the coin-seed half-width at the pinned level) is reported beside, never a second margin; a negative half-width refused (`limit_check`) |
| H3-A's inputs | every one, fixed here (the lead's ruling on B-3) | fixed | **Appendix C**, printed from `extended/three_way_h3a.py` and held equal to it by `tests/test_h3_draft.py`: the toy rules (stylised, no firm's), S1's parameters, the starts, horizon, seeds and placeholder budget, A1's design and the baselines' toys, the disjoint sets, J' and the levels, the clipped toy composite, A2's pair, A3's stream pair and the shortcut's subset, A4's lever changes and grids, the centring test's z, the smaller-J report's model; nothing is chosen or written at run time |
| S1 in H3-D | the generator fitted to the search years | fixed by its own row before H3-D runs | its fit (and the 15:10 flatten and five minutes flat S1 now holds; the red team's n-2) declared there, never after a look |
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
- **The stress:** 3 arms (+1 tick, +2 ticks, 10 % missed) x (the design and four baselines) per compared pair
  (`three_way_runner.stress_cells`).
- The program's honesty sentence: Stage 2's programs S and U and this repository's F-01 to F-03 read the development
  window; H3 adds no read of the held-out years, and the held-out test's level stays nominal while the held-out read
  ledger is not empty (CHARTER 3.6 (b)).

## 9. The deciding rule H3 calibrates

**The reading.** The martingale-outcome reading (CHARTER 3.2), identically for every arm: fills, timing and costs as
run; each trade's outcome redrawn by the race (or R-10's walk), **the stop exit's own cost in the race** (section 7).
**Every trade taken has gross expectation exactly zero**, the failures at the fill counted apart and reported beside
(`three_way_runner.fill_failures`; the exact program keeps their expected count). A race's net is exactly minus its
expected costs and its costed loss lands at most on the floor. The engine's clip binds only where the engine's own
would: at a walk's flatten whose cost would pass the floor or the daily limit (by at most x_flat - x_stop), and at an
account failed at the fill, whose loss is its whole room, at most the entry and the larger exit cost
(`three_way_redraw.race_net`, `walk_net`, exact-fraction tests).

**The coin field.** Every random element of a journey is a fixed function of the coin field: the side, the race's
uniform, the walk's steps, measure 28's missed signal, each its own draw kind of the coin key; the denial ladder's
draws are the `enforce` kind, keyed per unit, account and request, **seeded apart** (its own tag), so the ladder moves
no coin draw. The generator: numpy's Philox (4x64) seeded by `SeedSequence(key)`, the uniform (2 i + 1) 2^-53 on the
symmetric grid, computed on arrays by the vectorised implementation its tests admit (section 7); the antithetic twin
reads 1 - u exactly. Every key carries its unit's start, checked as it is built; the declared sample's keys are
compared by `generate_state`, two keys with one state refusing the run (section 7, the key guard). Each block seed draws
only its role's key kinds in its role's parts (`three_way_seeds.ROLE_USE`, refused otherwise; the red team's m-9).

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
the betting bound (section 7): **the one of the two that needs the smaller J for power pi\* at delta\*
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
- **The gate's other clauses** (the note's 4.4, with O-5 as E-230 ruled): every limit's headroom at least
  z_pi sigma_M / sqrt(J) for a design equal to the best baseline -- under the point-estimate rule it passes with
  probability Phi((L - M_best) sqrt(J) / sigma_M), so no c_L (`three_way_stats.headroom_needed`; the red team's m-6);
  the complete-start count at H_g reaching the minimum pinned in 3.9.
- If any fails, the search does not pin, and the data question goes to the operator with H3-D's result (E-007 (2)).

## 11. The stages and the kill rules

- **H3-0, the probe** (light enough to run first, still under the lock): measures the process base M_0 and the cost
  of a lane-trade **with the declared generator's keyed draws included**, in its two terms -- the race's, and the
  walk's at n steps (c = c_race + share_walk x (c_walk(n-bar) - c_race); `docs/plans/scripts/three_way/h3_cost.py`'s
  model) -- and a slot runs only when its modelled c is at most its c_max (Appendix A); the lead's row after H3-0
  records the measured c, each slot's share of walks and n-bar (H3-D's from H4's schedules), and any further cut, before
  any part runs.
- **H3-A, design checks** (before Wave 4.2): A1 the same-design nulls on placeholder composites (`P_B` at a placeholder
  budget, and a clipped toy composite); A2 the exact-centred toy null (the exact program; barrier and R-10 trades);
  A3 the history null on S1 (the stream swap); A4 the plants P2 to P4, and the copy-against-stagger check **only once
  the template defines overlap** (until then A4 runs the plants alone, and says so). **Kill:** a premise failing (a pool
  not centred -- |its mean| above 4 standard errors, two-sided, `three_way_h3a.CENTRING_Z` --, an asymmetric twin, a
  term out of range, a key guard refusal) stops the part and goes to the failure protocol; a size count whose 95 % Clopper-Pearson interval lies wholly above its feasible level is a laxity, recorded
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

- **This build's tests** use the tests' seed with the `test` kind and test ids 11 to 23 (`three_way_seeds.TEST_IDS`),
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
   through the runner equals its registered **trigger-level** trades (times and brackets, path for path), never trades
   pruned by the real run's account state, which would read the real outcomes (the red team's n-1); and the
   journey's own race step at no cost equals `adapter.BinaryDraw`'s on the same uniforms -- held by the build's test on
   `three_way_journey._trade_mc` itself, not only on `race_dollars` (the red team's n-4).
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
- **The generator** is the vectorised implementation of the declared law (section 7), admitted by its tests; the
  journey reads every uniform through it.
- **R-10's long walks.** A walk reads one uniform a step, so its cost grows with n. **Every walk is at most 1024
  steps by construction** (the step's rule, s-c), so the question is the 1024-step term: at S1's declared mix every
  slot of Appendix A fits its cap (read under the divisor rule; s-c moves S1's n-bar only at sessions of low
  volatility, where s falls to 1 and n can rise towards 1024), but at a walk share of a quarter and 1024 steps no H3-A
  or H3-D slot fits eight hours (`h3_cost.py` prints both readings). H3-0 re-reads S1's and H4's share and n-bar
  before H3-D; if they put a slot over its c_max, **the lead decides between** further splits, and
  re-declaring R-10's sampling as one uniform a walk through the inverse of `walk_law`'s exact terminal law (the same
  law, O(1) a trade, the antithetic null still exact; the red team's suggestion) -- a change of a declared rule,
  never made at run time.
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
H3's heavy slots: part | seed roles | reads | R arms M T h | lane-trades | hours over 2 workers at the assumed costs 0.05 us, 0.5 us, 5.0 us a lane-trade | c_max (the largest cost a lane-trade that fits 8 h)
  H3-0 probe                     | h3_0_probe | synthetic toys | R=1 arms=5 M=64 T=40 h=63 | 3.226e+06 | 0.0  0.0  0.0 | c_max=17857.14 us
  A1 same-design nulls           | h3a_histories, h3a_coins | S1, stylised | R=20 arms=3 M=10000 T=120 h=63 | 1.814e+10 | 0.1  1.3  12.6 | c_max=3.17 us
  A2 exact-centred toy null      | h3a_histories, h3a_coins | S1 toys, the exact program | R=20 arms=2 M=10000 T=120 h=63 | 1.210e+10 | 0.1  0.8  8.4 | c_max=4.76 us
  A3 history null                | h3a3_history_null | S1, stylised | R=200 arms=2 M=2000 T=120 h=63 | 2.419e+10 | 0.2  1.7  16.8 | c_max=2.38 us
  A4 plants, copy-stagger        | h3a_histories, h3a_coins | S1, stylised | R=10 arms=8 M=10000 T=120 h=63 | 2.419e+10 | 0.2  1.7  16.8 | c_max=2.38 us
  D1 same-design nulls [1/2]     | h3d_histories, h3d_coins | S1 fitted to the search years; S2 | R=10 arms=3 M=2000 T=412 h=252 | 2.492e+10 | 0.2  1.7  17.3 | c_max=2.31 us
  D1 same-design nulls [2/2]     | h3d_histories, h3d_coins | S1 fitted to the search years; S2 | R=10 arms=3 M=2000 T=412 h=252 | 2.492e+10 | 0.2  1.7  17.3 | c_max=2.31 us
  D2 history null [1/4]          | h3d_histories, h3d2_history_null | S1 fitted to the search years; S2 | R=50 arms=2 M=500 T=412 h=252 | 2.076e+10 | 0.1  1.4  14.4 | c_max=2.77 us
  D2 history null [2/4]          | h3d_histories, h3d2_history_null | S1 fitted to the search years; S2 | R=50 arms=2 M=500 T=412 h=252 | 2.076e+10 | 0.1  1.4  14.4 | c_max=2.77 us
  D2 history null [3/4]          | h3d_histories, h3d2_history_null | S1 fitted to the search years; S2 | R=50 arms=2 M=500 T=412 h=252 | 2.076e+10 | 0.1  1.4  14.4 | c_max=2.77 us
  D2 history null [4/4]          | h3d_histories, h3d2_history_null | S1 fitted to the search years; S2 | R=50 arms=2 M=500 T=412 h=252 | 2.076e+10 | 0.1  1.4  14.4 | c_max=2.77 us
  D3 power gate plants [1/2]     | h3d_histories, h3d_coins, h3d3_plants | H4's search-year outputs; S1 fitted; S2 | R=5 arms=6 M=2000 T=412 h=252 | 2.492e+10 | 0.2  1.7  17.3 | c_max=2.31 us
  D3 power gate plants [2/2]     | h3d_histories, h3d_coins, h3d3_plants | H4's search-year outputs; S1 fitted; S2 | R=5 arms=6 M=2000 T=412 h=252 | 2.492e+10 | 0.2  1.7  17.3 | c_max=2.31 us
  D3 full-J check (EB) [1/5]     | h3d_histories, h3d_coins | S1 fitted to the search years | R=1 arms=2 M=20752 T=412 h=252 | 1.724e+10 | 0.1  1.2  12.0 | c_max=3.34 us
  D3 full-J check (EB) [2/5]     | h3d_histories, h3d_coins | S1 fitted to the search years | R=1 arms=2 M=20752 T=412 h=252 | 1.724e+10 | 0.1  1.2  12.0 | c_max=3.34 us
  D3 full-J check (EB) [3/5]     | h3d_histories, h3d_coins | S1 fitted to the search years | R=1 arms=2 M=20752 T=412 h=252 | 1.724e+10 | 0.1  1.2  12.0 | c_max=3.34 us
  D3 full-J check (EB) [4/5]     | h3d_histories, h3d_coins | S1 fitted to the search years | R=1 arms=2 M=20752 T=412 h=252 | 1.724e+10 | 0.1  1.2  12.0 | c_max=3.34 us
  D3 full-J check (EB) [5/5]     | h3d_histories, h3d_coins | S1 fitted to the search years | R=1 arms=2 M=20752 T=412 h=252 | 1.724e+10 | 0.1  1.2  12.0 | c_max=3.34 us
  H7 held-out, Hoeffding         | the search declaration's own | the held-out years, once (Wave 6; not H3; one firm's three finalists -- the joint test across firms is larger) | R=1 arms=7 M=100 T=601 h=63 | 1.060e+08 | 0.0  0.0  0.1 | c_max=543.31 us
  H7 held-out, EB sets [1/3]     | the search declaration's own | the held-out years, once (Wave 6; not H3; one firm's three finalists -- the joint test across firms is larger) | R=1 arms=7 M=6918 T=412 h=252 | 2.011e+10 | 0.1  1.4  14.0 | c_max=2.86 us
  H7 held-out, EB sets [2/3]     | the search declaration's own | the held-out years, once (Wave 6; not H3; one firm's three finalists -- the joint test across firms is larger) | R=1 arms=7 M=6917 T=412 h=252 | 2.011e+10 | 0.1  1.4  14.0 | c_max=2.86 us
  H7 held-out, EB sets [3/3]     | the search declaration's own | the held-out years, once (Wave 6; not H3; one firm's three finalists -- the joint test across firms is larger) | R=1 arms=7 M=6917 T=412 h=252 | 2.011e+10 | 0.1  1.4  14.0 | c_max=2.86 us
memory: cap 2.5 GB over 2 workers, base 0.4 GB assumed (H3-0 measures it), lane 1344 B: at most 632440 lanes a worker
the cut rule: a slot runs only if H3-0's measured cost a lane-trade (the race's and the walks' terms, `h3_cost.py`) is at most its c_max; otherwise it is cut, M first, with the power cost stated, or split further, before it starts
the held-out test's split: no statistic is read until every sub-part completes; a crashed sub-part is re-run whole from its declared seeds, never resumed; each crash is recorded in the part ledger (E-195)
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

## Appendix C. H3-A's inputs (printed by `docs/plans/scripts/three_way/h3a_inputs.py`)

Every input of H3-A, as `extended/three_way_h3a.py` declares it (the lead's ruling on B-3). Values in dollars, ticks,
sessions and minutes after 17:00 CT; none is a firm's.

<!-- h3a_inputs: begin -->
```text
TOY_RULES = ToyRules(combine_fee=40.0, billing=21, target=2500.0, mll=1500.0, dll=800.0, activation_fee=100.0, funded_mll=1500.0, win_day=100.0, payout_days=5, payout_share=0.5, payout_cap=3000.0, split=0.9, payout_lag=3, combine_lock=0.0, label="toy rules, no firm's")
TOY_RULES_EXACT = ToyRules(combine_fee=40.0, billing=21, target=600.0, mll=400.0, dll=None, activation_fee=100.0, funded_mll=400.0, win_day=100.0, payout_days=3, payout_share=0.5, payout_cap=1000.0, split=1.0, payout_lag=2, combine_lock=0.0, label="toy rules, no firm's")
S1_PARAMS = S1Params(n_sessions=200, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.2, regime_switch=0.02, rate=1.5, rate_beta=1.0, hold_mean=30.0, hold_stop=40.0, time_limit=90.0)
S1_PARAMS_EXACT = S1Params(n_sessions=200, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.0, regime_switch=0.02, rate=0.3, rate_beta=1.0, hold_mean=30.0, hold_stop=40.0, time_limit=90.0)
STARTS = range(0, 120)
HORIZON = 63
SEEDS = 10000
BUDGET = 1000.0
COST = 2.12
STOP_SLIP = 5.0
FLAT_SLIP = 10.0
TICK = 5.0
A1_DESIGN = DesignSpec(name='a1_design', stream='A', marks=(), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=None, rr=1.0, contracts=1, tick_value=5.0, entry_cost=2.12, x_target=2.12, x_stop=7.12, x_flat=12.120000000000001, walk_step=2, latency=5, per_session=3)
BASELINES = {naive_coin: DesignSpec(name='naive_coin', stream=None, marks=(960, 1080), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=40, rr=1.0, contracts=1, tick_value=5.0, entry_cost=2.12, x_target=2.12, x_stop=7.12, x_flat=12.120000000000001, walk_step=2, latency=5, per_session=3), p14: DesignSpec(name='p14', stream=None, marks=(1000,), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=50, rr=2.0, contracts=1, tick_value=5.0, entry_cost=2.12, x_target=2.12, x_stop=7.12, x_flat=12.120000000000001, walk_step=2, latency=5, per_session=3), p15: DesignSpec(name='p15', stream=None, marks=(1020,), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=100, rr=1.0, contracts=1, tick_value=5.0, entry_cost=2.12, x_target=2.12, x_stop=7.12, x_flat=12.120000000000001, walk_step=2, latency=5, per_session=3), p16: DesignSpec(name='p16', stream=None, marks=(1140,), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=150, rr=1.0, contracts=1, tick_value=5.0, entry_cost=2.12, x_target=2.12, x_stop=7.12, x_flat=12.120000000000001, walk_step=2, latency=5, per_session=3)}
DISJOINT = ((0, 5000), (5000, 10000))
J_PRIME = 100
LEVELS = (0.05, 0.01, 0.001)
TOY_COMPOSITE = (Dimension(name='P_B', kind='mean', horizon=63, a=0.0, r=1.0, source='arithmetic', lo=0.0, hi=1.0, weight=0.5), Dimension(name='paid_by_63', kind='mean', horizon=63, a=0.0, r=1.0, source='arithmetic', lo=0.0, hi=0.6, weight=0.3), Dimension(name='sessions_saved_to_payout', kind='mean', horizon=63, a=0.0, r=64.0, source='arithmetic', lo=0.0, hi=64.0, weight=0.2))
A2_PAIR = (DesignSpec(name='a2_x1', stream='A', marks=(), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=20, rr=1.0, contracts=1, tick_value=5.0, entry_cost=0.0, x_target=0.0, x_stop=0.0, x_flat=0.0, walk_step=2, latency=5, per_session=1), DesignSpec(name='a2_x2', stream='A', marks=(), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=40, rr=0.5, contracts=1, tick_value=5.0, entry_cost=0.0, x_target=0.0, x_stop=0.0, x_flat=0.0, walk_step=2, latency=5, per_session=1))
A3_PAIR = (DesignSpec(name='a3_D', stream='A', marks=(), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=10, rr=1.0, contracts=1, tick_value=5.0, entry_cost=0.0, x_target=0.0, x_stop=0.0, x_flat=0.0, walk_step=2, latency=5, per_session=1), DesignSpec(name="a3_D'", stream='B', marks=(), k_stop=6.0, stop_lo=8, stop_hi=120, fixed_stop=10, rr=1.0, contracts=1, tick_value=5.0, entry_cost=0.0, x_target=0.0, x_stop=0.0, x_flat=0.0, walk_step=2, latency=5, per_session=1))
A3_HISTORIES = 200
SHORTCUT_HISTORIES = (0, 1, 2, 3, 4)
P2_LEVERS = {fee_less_a_fifth: {combine_fee: 32.0}, payout_lag_one: {payout_lag: 1}, activation_halved: {activation_fee: 50.0}}
P3_EPS = (0.0025, 0.005, 0.01, 0.02)
P4_A = (0.0, 0.5, 1.0)
P4_SWITCH = 0.02
SIZE_GRID = (0.0025, 0.005, 0.01, 0.02, 0.04)
CENTRING_Z = 4.0
SMALLER_J_MODEL = "normal at each pool's own sd (H3-A); H3-D's model is H3-D's text's"
SMALLER_J_KEY = ('h3a_histories', 'plant', 'A1', (('history', 0), ('plant', 0), ('replicate', 0)))
SMALLER_J_GRID = (16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768)
SMALLER_J_DRAWS = 2000
```
<!-- h3a_inputs: end -->

## Appendix D. The red team's read of the first text, answered

`docs/reviews/BUILD_W32_H3_2026-11-19.md` on 746a245; the lead's rulings of corrective cycle 1.

| finding | the answer | where |
|---|---|---|
| B-1 | the race fractional (BinaryDraw's form); R-10's last step a two-point race to the fractional barrier; the forced-loss toy fails and replaces every account; the journey's own race equals BinaryDraw | section 7; `three_way_redraw`, `three_way_journey._barrier`; `test_b1_...`, `test_the_race_and_the_journeys_race_are_the_vendored_draw_at_no_cost` |
| B-2 | the start checked at construction; distinctness by the packing with its collision bound; the stored check on a declared sample within 1.25 GB a worker | section 7 (the key guard); `three_way_keys`; `test_b2_...` |
| B-3 | every H3-A input fixed in this text | Appendix C; `extended/three_way_h3a.py` |
| m-1 | the journey's race step against `race_net` on a fractional grid; the simulation against the exact program where the cushion binds | `test_m1_...` (kills W and A) |
| m-2 | the simulation's walk step against the walk's outcome; the exact program's walk step against `walk_net`; the two against each other on a small toy | `test_m2_...` (kills B, B2, C) |
| m-3 | only a plain mean admitted to McDiarmid | `Dimension.admitted`; `test_admission` |
| m-4 | the bets predictable (tested by perturbation); both 2.2 (b) bounds' coverage where near tight | `three_way_stats.bets`; `test_the_betting_bounds_bets_are_predictable` (kills K), `test_the_bounds_cover_where_they_are_near_tight` |
| m-5 | the vectorised generator (Q-170) wired into the journey; the walk read in chunks; the cost model's walk term; the splits; the plan's c_max | sections 7, 11, 17; Appendix A; `h3_cost.py` |
| m-6 | O-5 as E-230 ruled; a negative half-width refused; the headroom z_pi sigma / sqrt(J) | sections 7, 10; `limit_check`, `headroom_needed` |
| m-7 | the gate at 25 % denial, 0 % beside; the 10 % missed-signal arm | section 7; `gate_reading`, `stress_arms` |
| m-8 | the resample's dates one a value, increasing, inside the search years | `refuse_held_out`; the resample test |
| m-9 | each block seed drawn only in its role's kinds and parts | `three_way_seeds.ROLE_USE`, `check_use`; `test_m9_...` |
| m-10 | the runner's held-out refusal, the first held-out day included | section 2; `three_way_runner.Plan`; `test_m10_...` (kills R2) |
| m-11 | the exact program's state carries whether it passed (0.875 on the red team's toy) | `three_way_journey._state_key`; `test_m11_...` |
| m-12 | P1 refused for the betting bound and clipped composites; `planted_rates` for those | section 7; `planted_mdl`, `planted_rates` |
| m-13 | a boundary test each: n_min exactly, quantiles straddling zero, a skewed g, the first held-out day, a constant added to the resample, the exact program's denial | the stats and runner tests (kill O, P, P2, R, S, U) |
| m-14 | the smaller-J rule's grid, draws, power model and rng declared | section 7 |
| m-15 | the generator admitted on every output a walk reads, up to 1024 | `tests/test_three_way_fastkeys.py` |
| m-16 | the history null's pair differs in its stream only | `three_way_s1.stream_pair`; `test_m16_...` |
| m-17 | a negative half-width and a calendar with no group of n_min refused | `limit_check`, `condition` |
| n-1 | the runner's identity checks trigger-level schedules | section 16 |
| n-2 | S1 holds the 15:10 flatten and five minutes flat; its volatility is latent, H3-D's causal | `three_way_s1.schedule`; `test_n2_...` |
| n-3 | H7's rows are one firm's; the joint held-out test across firms costs more and is its own declaration's | Appendix A's H7 rows, labelled |
| n-4 | the vendored-equality test drives the journey's race step | section 16 |
| n-5 | the as-walked reading labelled beside wherever printed, its stop-side cost on every exit | `three_way_journey._trade_mc` |

`docs/reviews/REREADS_W32_W34_O7_2026-11-20.md` on adedf7f; the lead's rulings of corrective cycle 2.

| finding | the answer | where |
|---|---|---|
| RB-1 | a lane that cannot take its trade (room above $1e-6 but L_fill at most zero) fails at the fill where its floor binds -- to the floor, breached, replaced, counted apart (the lead's ruling, with the template read's B-2) -- and ends its day where the daily limit binds; R-10's barrier the race's own (x_stop), the flatten clipped at the floor; the exact program shares the fix; the red team's toy at H3-A's costs leaves no unit in the window past a trade; the failed lane equals the engine's losing branch on the same uniforms | section 7; `three_way_journey._classes`, `three_way_redraw.walk_barriers`; `test_rb1_...`, `test_b2_...`, `tests/three_way_vendored_draw.py`; mutants RB1, RB1a to RB1d, FF |
| rm-1 | the harness binds the real exception classes into each mutant and counts only an assertion, a pytest failure or the build's own refusal; every mutant has an identity control that must survive; R2, N8, N3 and M10 are killed by the real mutants | `tests/test_three_way_mutations.py` |
| rm-2 | a one-element tuple printed as Python writes it | `three_way_h3a._show`; Appendix C |
| rn-1 | A1's costs built by the baselines' own expression | `three_way_h3a.A1_DESIGN` |
| rn-2 | a walk above 1024 steps refused; the step's rule keeps every walk within it | `three_way_journey.WALK_MAX`, `three_way_redraw.walk_step` |

The template's read (`docs/reviews/TEMPLATE_AGENTS_v3_2026-11-20.md`, 81739db) on this runner; the lead's addition to
corrective cycle 2 (the runner's form governs, E-237).

| finding | the answer | where |
|---|---|---|
| TB-2 | an account that cannot take a trade fails at the fill where its floor binds (counted apart), its day ends where the daily limit binds; exact at e + max x - epsilon (fails) and + epsilon (races) | `three_way_journey._classes`; `test_b2_an_account_below_its_costs_...`; mutants RB1, FF |
| Tm-1 | the take decided at the fill by L_fill, for every exit law | `three_way_journey._l_fill`; `test_m1_the_take_does_not_read_the_exit`; mutant TF |
| Tm-2 | the profit-level row (the race at the level's as-placed target); the walk only for a real time limit; a fractional target allowed in the walk, raced exactly at its last step | `three_way_redraw.EXIT_LAW`, `walk_law`; `test_m2_a_profit_level_races_at_min_g_level`, `test_m2_a_fractional_target_in_the_walk_is_raced_exactly`; mutants PL, PLg |

The third re-read (`docs/reviews/BUILD_W32_v3_2026-11-20.md`; stands with readings, no blocker); the lead's follow-up.

| finding | the answer | where |
|---|---|---|
| v3 m-1 | the mutation harness patches each mutant through its own `MonkeyPatch`, so a check's own undo never undoes it; a walk-only reversion of the failure at the fill is killed | `tests/test_three_way_mutations.py`; mutant RB1w |
| v3 m-2 | the forced-loss test reaches failures at the fill for both laws (a floor nine full losses and $10 deep) and asserts the clip | `test_rb1_forced_losses_...`; mutant RB1e |
| v3 m-3 | the level booked as the engine books its need, net dollars of the trade (`lockstep.need_to_pass`; `sizing`'s "exactly the need"), in code and here | `three_way_journey.Trade.target`; `test_m2_a_profit_level_...` (a level at the need passes); mutant LVg |
| v3 m-4 | the journey's walk with a level, and the walk's clip where the daily limit binds, each tested in the simulation and the exact program | `test_m4_...`; mutants WG, WGd, WD |
| v3 m-5 | the stale sentences corrected: the take at the fill, the clip's two places; here, every trade *taken* has gross zero, the failures at the fill counted apart | `three_way_redraw`, `three_way_journey._settle`; section 9 |
| v3 n-1 | a room between e + x_stop and e + max(x_stop, x_flat) is a certain failure, labelled the conservative choice (E-247) | section 7 |
| v3 n-2 | a declared daily limit at or below a trade's costs refused before any draw | `three_way_journey.check_costs`; mutant N2c |
| v3 n-3 | the failures at the fill printed beside each arm (`fill_failures`, `paired`'s `beside`) and kept in expectation through the exact program's merge | `three_way_runner.fill_failures`, `three_way_journey._merge`; mutant N3m |
| v3 n-4 | the sliver of room at or below EPS fails at the fill too (the condition dropped) | `three_way_journey._classes` |

The lead's correction s-c, folded into the third re-read's follow-up (the governing rule for the walk's step).

| finding | the answer | where |
|---|---|---|
| s-c | the walk's step s = max(1, ceil(sigma sqrt(T) / sqrt(1024))), T the limit known at the fill for s and n alike; the step need not divide the bracket (off-lattice barriers by the two-point last sub-step); never a refusal for the step; the divisor rule removed | section 7; `three_way_redraw.walk_step`, `three_way_s1.schedule`; `test_s_c_...` (the formula's cases; a 37 / 55 bracket against the one-tick lattice within 1e-3 **at the two tested points**, not a general bound: the lattice's own residual is stated in section 7; the realised exit never read) |

The red team's diff check of 5f2598b and c66cb35 (`BUILD_W32_sc_2026-11-21`, PASS WITH MINORS).

| finding | the answer | where |
|---|---|---|
| sc MINOR-1 | a flatten-bound trade's T is its minutes to 15:10 CT, tested; a mutant reading the time limit killed (SCt) | `test_minor1_a_flatten_bound_walks_t_is_the_minutes_to_the_flatten` |
| sc MINOR-2 | the 1e-3 tolerance holds at the two tested points; the lattice's residual stated beside H3 as a known approximation | section 7 (R-10's row); `test_s_c_a_coprime_bracket_matches_the_one_tick_lattice` |
| sc MINOR-3 | H4's tests seed draws its toy keys only in its own part H4-T (12), refused on H4-0's and H4-B's fields; mutant HT killed | `three_way_seeds.ROLE_USE`, `PARTS`; `test_minor3_h4s_tests_seed_draws_only_in_its_own_part` |
| sc NOTE-1 | the 1e-12 guard stated | section 7 (R-10's row) |
| sc NOTE-2 | the long-walk text: every walk at most 1024 steps by construction; H3-0 re-reads n-bar | section 17 |
| sc NOTE-3 | a `news` or `other` exit truncates the walk, never sets s or n; T the limit known at the fill | section 7 (R-10's row) |
| sc NOTE-4 | the block refusal's message names both blocks; `baselines_only` tested with a design sharing a moment with a baseline | `three_way_keys.seed_key`; `test_note4_baselines_alone_with_a_design_sharing_a_moment` |
