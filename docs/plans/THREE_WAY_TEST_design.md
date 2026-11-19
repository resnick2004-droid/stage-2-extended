# The three-way test: design note (Q-153; the restart plan's Wave 3.2, first part)

Drafted 2026-11-18 on `wt/wt-verify` for the lead and the red team. **Corrective cycle 1** answers the red team's read
(`docs/reviews/THREE_WAY_TEST_2026-11-18.md`: four blocking findings, thirteen minor). **Corrective cycle 2** answers
its re-read (`docs/reviews/THREE_WAY_TEST_v2_2026-11-18.md`: one new blocking finding, ten minor). Both follow the
coordinator's rulings (section 0).

**N-1's paragraph** sits between the markers `2.2a-admission` in 2.2 (a). It is written to be copied verbatim into
H3's declaration, and it is the scope of the next re-read.

**Status: a design note, not a declaration.** Nothing here is pinned, built or run. H3's declaration takes its rules
from this note, after the red team's read.

No result number. Every figure below is printed by `docs/plans/scripts/three_way/three_way_arith.py` from declared
constants and the calendar (Appendix A). `tests/test_three_way_design.py` holds the appendix to the script line for
line, and holds the prose's counts to it. No bar and no outcome was read to write the note. The only result file
opened was `results/calibration_p.csv`, for its header row.

**Sources.**
- The restart plan, sections 4.5 to 4.8 (`docs/plans/RESTART_PLAN_journey_objective.md`).
- The amendments draft, CHARTER 3.2 and 3.5 to 3.9 (`docs/plans/AMENDMENTS_draft_2026-11-18.md`, corrective cycle
  2). Its text is the one about to go into force (E-210).
- E-208's design brief for the test, and the triage's section 3.2 (`docs/plans/TRIAGE_2026-11-18.md`).
- `docs/MEASURES.md` (wt/wt-user 9842e10, merging to master): section 1's conventions and section 2's `P_B`.
- Stage 2's `adapter.BinaryDraw` (`vendor/stage2/propedge/contract/adapter.py`; D-150, D-156), and D-145's gate
  configs (`vendor/stage2/config/fv2_grid.yaml`, `fv3_corrected_portfolio.yaml`).
- `extended/p_bound.py`, `extended/family_stats.py`, `results/calibration_p.csv`'s header (columns only), and Q-16's
  and Q-55's rows (E-035, E-083, E-085).

**The note in brief.**
- **The deciding reading is fixed down to the redraw.** Each trade races the nearer barrier, as `BinaryDraw` does
  (B-1). The fallback is MEASURES.md's `P_B` (B-2). Positions whose holding intervals overlap read one shared driftless
  path; until the template defines overlap, no design with overlapping positions runs (B-3).
- **Leg (i), the coin-seed leg, carries the level.** Given the held-out history, each user's coin draws are
  independent of every other user's. So the deciding bounds are exact on every history by theorem:
  - Hoeffding's bound (McDiarmid's for a clipped composite) over every start-seed term, when every dimension is an
    unconditional mean with a priori bounds (2.2 (a), N-1), under choice 3 only;
  - otherwise, an empirical-Bernstein or betting bound over seed sets (2.2 (b)).

  There is no t branch (B-4). The composite is bounded by clipping.
- **The two same-design nulls are symmetric by construction.** A third null is added: two different designs on toys,
  centred by their exact expectation from dynamic programming.
- **The history null is exact for any functional**, built from a symmetry of the history generator. What stays open
  is only the generator's realism.
- **The years and held-out legs cannot reach the level.** On the weekday bound the held-out years hold at most ten
  disjoint 63-session units, and twelve are needed (Appendix A). The legs are exact consistency conditions, and their
  stated size is computed with the overlap counted.

---

## 0. Corrective cycle 1: finding → where it is answered

| finding | ruling (coordinator) | answered in |
|---|---|---|
| B-1 the redraw ignores the floor race | the race of the nearer barrier, as `BinaryDraw`; the same in the DP toys; an oracle test | 1.1, 2.4; test `test_the_race_redraw_has_zero_expectation_at_every_cushion`; script `race_redraw` |
| B-2 the fallback's bankroll reading | MEASURES.md's `P_B`: peak out-of-pocket through each month close at most B | 1.2 |
| B-3 the joint law of overlapping positions | one shared driftless path (per underlying since cycle 2); the copy-against-stagger check in H3-A; no overlapping design until the template defines it | 1.6, 6.1 (A4) |
| B-4 the t's escape branch | deleted; every dimension clipped, the caps pinned in 3.9's row; "certified" reworded | 1.3, 2.2, 2.6 |
| m-1 EB is range-dominated | Hoeffding (McDiarmid) over all J x \|T\| terms for mean-type dimensions; EB or betting on seed sets for quantile ones, by a rule stated now; the held-out test's compute in the run plan; J fixed before the read | 2.2, 2.5, 6.1, 6.3, Appendix A |
| m-2 clipping | the clipped normaliser shown to the operator; a cap margin pinned; the share at a cap reported | 1.3 |
| m-3 (Y) and (R) | the last-year contradiction fixed; (Y)'s real size with the overlap; n_min from the calendar only; vacuity printed; v(t) on closed bars | 3.4, Appendix A |
| m-4 seed keys | fixed length per kind with a nonzero tag; part and history in kappa; tested | 1.5, 7; test `test_the_seed_key_trap_and_the_fixed_length_keys` |
| m-5 the derived-seed guard | an arithmetic fold over every tracked `.py`, pointed at this test's own construction as its positive control | 7; tests `test_the_arithmetic_fold_*`, `test_the_fold_sees_names_and_pure_literals` |
| m-6 the schedule claim | adopted: a typed interface, its fields, an exact test planned for the build, S2's distinct-block count reported | 1.7, 2.6 |
| m-7 Q-16's real nulls read the held-out years | search-year or synthetic nulls only; Q-16 enters the held-out read ledger | 3.1 |
| m-8 the twin and the charter's words | the uniform complement kept; the lead rewords CHARTER 3.7; the forced side noted | 2.3 |
| m-9 choice 3 | kept; the side coin's key carries no account or firm index; the keying pinned with m | 1.5 |
| m-10 the history null's pairs | adopted: S1's symmetry named (two exchangeable trigger streams); every FPR_hist row labelled with its pair; the shortcut's error reported | 2.7 |
| m-11 H_g | 504 sessions, from D-145's configs; its counts printed; the gate's held-out quantile over coin seeds only; the typed partial-unit count dropped (Appendix A prints it) | 3.2, 4.4, Appendix A |
| m-12 "its noise" | adopted: coin noise decides in the limit clause (the level's scope), history variation beside; the operator's under O-5, fixed in the pinning row | 4.4 |
| m-13 the arithmetic test | the constants checked against their sources; a seeded coverage check of both bounds; the prose's counts held to the script | tests `test_the_constants_against_their_sources`, `test_the_bounds_cover_at_a_feasible_level`, `test_the_prose_counts_are_the_scripts` |

**Cycle 2** (the re-read, `docs/reviews/THREE_WAY_TEST_v2_2026-11-18.md`; B-1 to B-4 closed there):

| finding | ruling (coordinator) | answered in |
|---|---|---|
| N-1 what 2.2 (a) admits; r_d's source (blocking) | only unconditional means over all of E_h with a priori per-unit bounds (contract arithmetic, or a per-unit clip pinned in the dimension's definition), never a range read from data; conditional shares, ratios of means and CVaR to (b); the build refuses a value outside its bounds; written to be copied verbatim | 2.2 (a), between the `2.2a-admission` markers |
| N-2 valid only under choice 3 | stated in 2.2 (a); the build asserts every coin key carries the start; choice 3 stands, MEASURES.md aligned on wt-user | 1.5, 2.2 (a); test `test_the_seed_key_trap_and_the_fixed_length_keys` (the start in the coin key) |
| N-3 the copy-against-stagger pass rule | the copy-against-stagger gap grows with the stagger; what shrinks is the gap between the shared-path law and independent draws; the zero-stagger identity runs through two separate code paths | 1.6 |
| N-4 lattice, key, circularity | a deferred note for the template (wt-lit): barriers rounded inward to the lattice, the path keyed per underlying (MNQ and NQ one), overlap defined on scheduled entries and the run's exit times; overlap stays refused | 1.6 ("Deferred to the template"); script `KEY_KINDS` (`underlying`) |
| N-5 costs and the clip | the race at the cushion less the exit cost; an oracle that the net expectation is minus the costs | 1.1; script `race_redraw`, `net_expectation`; test `test_the_race_with_costs_nets_minus_its_costs_and_never_passes_the_floor` |
| N-6 the smaller-J rule needs delta\* | applied in H3-D only, after Wave 4.2 sets delta\*; H3-A reports both bounds' J | 2.2 (b), 6.1 |
| N-7 vacuity of (Y) and (R) | a condition whose stated size is at least one half is labelled vacuous; n_Y = all of Y_ok; n_min from the calendar only, both choices' sizes shown and one proposed; the pinning row sets it | 3.4, Appendix A |
| N-8 keys of 2^32 or more | `seed_key` refuses any word at or above 2^32; the guard compares `generate_state`; the `[7, 2**32+5]` case tested | 1.5, 2.3; script `seed_key`, `key_state`; test `test_the_seed_key_trap_and_the_fixed_length_keys` |
| N-9 the fold's reach | every tracked `.py`, no prefilter; `**`, `+=` and tuple unpacking folded; each tested | 7; tests `test_the_fold_sees_powers_without_the_year_digits`, `test_the_fold_sees_augmented_assignment`, `test_the_fold_sees_tuple_unpacking` |
| N-10 the key test's seed | the tests' role | 7; test `test_the_seed_key_trap_and_the_fixed_length_keys` |
| N-11 the clipped estimand moves with J | noted beside the verdict with the share at a cap | 1.3, 3.5 |

---

## 1. The statistic

### 1.1 The reading: the race redraw (B-1)

Every quantity below is read on **the martingale-outcome reading** (CHARTER 3.2), for the design and every baseline
alike, with the same seed keying.

**The redraw races the nearer barrier**, as Stage 2's `adapter.BinaryDraw` does (settlement `race`, D-156; D-150:
"which keeps the floor barrier race"):
- A trade has a stop of l ticks and a target of g ticks.
- Its account's cushion c is the room to the nearer of the floor and, where it applies, the daily loss limit (the
  engine's own `cushion`), read after the entry cost is booked. x is the trade's exit cost. All of these are in
  ticks, and fractions are allowed.
- **The loss barrier is L = min(l, c - x): the cushion less the exit cost (N-5).** The driftless first exit wins with
  probability p = L / (L + g). It then gains g; otherwise it loses L. The exit cost is paid on either exit.
- So a losing trade's loss plus its exit cost never passes the floor, and the engine's clip (`np.maximum(pnl,
  -cushion)`) never binds. A trade with no room (L <= 0) is not taken.
- **Every trade's gross expectation is exactly zero, and its net expectation is exactly minus its costs**, at every
  cushion.
- **The defect this rules out (B-1).** A win drawn at l / (l + g) with the loss then clipped at c has a gross edge of
  g (l - c) / (l + g) whenever l > c. Racing the full cushion and then clipping its exit cost would credit near-floor
  trades with that cost.
- `tests/test_three_way_design.py` checks all three in exact fractions:
  - the cost-free race over a grid of (l, g, c);
  - the unraced edge;
  - with costs, over fractional cushions, net = -(entry + exit) and a worst change never past the floor.

  The build's redraw must be `three_way_arith.race_redraw`'s law.
- On a trade held by several accounts at different cushions, each account has its own p (1.6).

**The rest of the reading.**
- The redraw for a time-limited trade is the search template's (flag R-10), with zero gross expectation, and it races
  the cushion in the same way.
- Fills, timing and costs are as run, for a position whose holding interval overlaps no other position of the user's
  (1.6).
- The as-walked and as-traded results are computed on the same seeds and reported beside. They are never tested.

| symbol | meaning |
|---|---|
| H | the held-out history (NQ 2024-01-02 to 2026-07-16 on `results/q82_judged_sessions.csv`), fixed |
| N_H | its session count. It is at most W_H, the weekday count of its dates (Appendix A) |
| h_d | dimension d's horizon in sessions (21 a month); h\* = the largest h_d in the composite (63 for the fallback) |
| E_h | the held-out starts with at least h sessions left before 2026-07-17 (MEASURES.md 1.1): N_H - h + 1 of them |
| u = (t, s) | a unit, one user: a start day t and a coin seed s (MEASURES.md 1.1) |
| U | the coin field: i.i.d. uniforms U_kappa on (0, 1), one per key kappa (1.5) |
| f, beta | a finalist (design); a baseline (naive coin, P-14, P-15, P-16) |
| a(x, u) | the fallback's per-unit value for design x (1.2) |
| C(x; S) | the composite of x over the units of the seeds in S (1.3) |
| alpha | the family level 0.05 / (k (k + 1)); k = 13 next |

### 1.2 The fallback, `P_B`: per unit, per seed, per start day (B-2)

**The fallback is MEASURES.md's `P_B`, as section 2 of `docs/MEASURES.md` defines it** (wt/wt-user 9842e10). That is
the peak out-of-pocket through each month close at most the budget B, and "ahead" means above 1e-6 dollars. It is not
paraphrased here. Its per-unit form is

    a(x, u) = (1/3) x (the months m in {1, 2, 3} at which u counts as ahead under B, by MEASURES.md section 2)

on the units of E_63. The cash spent before the first payout appears only as MEASURES.md's named sub-reading beside.

**The stop is read on the replay's own path, as MEASURES.md section 2 states.** If a later row makes the wallet stop
deciding ("no new fee after B, the live accounts kept", a re-run with a wallet):
- the wallet keeps every peak at most B, so `P_B`'s peak condition is redundant on the wallet's journeys, and only the
  ahead condition remains;
- this note keeps one definition, `P_B` on the replay's path, with the wallet reading beside until a row says
  otherwise.

**The estimators.** The term of unit u is d_u = a(f, u) - a(beta, u), which lies in [-1, 1].
- **Per seed:** Delta_s = the mean of d_(t,s) over t in E_63.
- **Per start day:** delta_t = the mean of d_(t,s) over the test's seeds.
- **The estimate:** Delta-bar = the mean of d_u over every unit, which is the mean of either.

### 1.3 The composite, clipped (B-4, m-2)

The composite is pinned in Wave 4.2:

    C(x; S) = sum over d of w_d * clip( (Phi_d(F_{x,d,S}) - lo_d) / (hi_d - lo_d), 0, 1 )

- F_{x,d,S} is the empirical distribution of dimension d's per-unit value over the units of E_{h_d} under the seeds S.
- Phi_d is the dimension's functional (a mean, a share, a median, a p10, ...), in MEASURES.md 1.3's **never-blank
  form**, pinned before clipping. A censored dimension takes its censored value W + 1 or its share reached.
- **The caps lo_d < hi_d are set from the search years, with a pinned cap margin.** The weights are non-negative and
  sum to one.
- So C lies in [0, 1] **for every composite.** No unbounded branch remains (B-4).

**The cost of clipping (m-2), stated to the operator.**
- The operator's trade-off answers in Wave 4.2 are answers about **the clipped composite**. The clipped normaliser of
  each dimension is shown to them.
- Caps can be exceeded on the held-out years. Both arms then saturate and the difference goes to zero: power is lost,
  size is not.
- The share of seed sets (or units) with any dimension at a cap is reported beside the verdict.

**The estimand.** It is theta(H) = E[ C(f; S) - C(beta; S) | H ], the expectation over the coin field, at the
replicate structure the deciding bound reads (2.2).
- Where every Phi_d is a mean or a share, theta is that of the composite over all the test's units.
- Where some Phi_d is a quantile, it is theta_m: the expectation per seed set of m seeds. That depends on m and on the
  keying across starts (m-9), and **both are pinned with the composite.** The plug-in over all the test's seeds is
  reported beside.
- **Under clipping the estimand moves with J near a cap (N-11).** E[clip(plug-in)] is not clip(E[plug-in]), so theta
  of a clipped composite depends on the number of units it is computed on wherever a dimension's plug-in can reach a
  cap. Validity holds, because theta is pinned with J. **Printed beside the verdict:** this note, with the share of
  seed sets (or units) at a cap.

**Per start day (beside only).** delta_t^C = sum over d of w_d g_d' [psi_d(f; t) - psi_d(beta; t)], where psi_d is the
dimension's influence function: x - mu for a mean; the indicator less the share for a share;
(q - 1[x <= xi_q]) / f-hat(xi_q) for a q-quantile. It shows which start days drive a difference, and it feeds
`user_measures.n_eff_bartlett` at lag h\*. It decides nothing.

### 1.4 The hypothesis, per pair

For each finalist f and each baseline beta, on the held-out history:

    H0(f, beta):  theta(H) <= 0        against        H1(f, beta):  theta(H) > 0

f beats the baseline set when every H0(f, beta) is rejected at the full level alpha: an intersection-union test
(CHARTER 3.8 (b)). **The level bounds coin luck given H. It does not bound a favourable H** (2.7).

### 1.5 The seed keying (m-4, m-9)

- **Every random element of a journey is a fixed function of the coin field U.** That covers the reflection coin, the
  redraw (or the shared path's steps, 1.6), missed-signal draws (measure 28's stress), any tie-break and any account
  rotation that draws.
- **The key of a coin uniform has a fixed length**, `three_way_arith.seed_key(seed, "coin", ...)`:

      kappa = [role seed, tag, part, history, seed index, start, underlying, moment, draw kind]

  - It carries the part and the history (m-4), so two histories or two parts never read one field unless a row says
    the sharing is intended.
  - It carries the **start** (choice 3). **The build asserts that every coin key carries the unit's start** (N-2).
  - It carries the **underlying**, not the instrument: MNQ and NQ are one underlying (N-4).
  - Every other kind (history, symmetry, plant, test) has its own fixed length and its own nonzero tag.
  - **Every word is below 2^32** (N-8): `seed_key` refuses any field, and any seed, at or above it. Moments are session
    indices and minute offsets, never epoch times.
  - The key is passed to a counter-based generator. Distinct keys give independent uniforms. The build declares the
    generator.
- **Why.** numpy reads `default_rng([a, b])` and `default_rng([a, b, 0, 0])` as one stream (trailing zeros carry no
  entropy). It also splits a word of 2^32 or more into 32-bit words, so `default_rng([7, 2**32 + 5])` is
  `default_rng([7, 5, 1])`.
  - With one length per kind, a distinct nonzero tag in the second word, and every word below 2^32, no two keys can
    give one stream.
  - **The key guard compares what numpy actually seeds**, `SeedSequence(key).generate_state(4)` (`three_way_arith.key_state`),
    not the integers.
  - The test demonstrates both traps, checks the refusal at `[7, 2**32 + 5]`, and enumerates every kind over a grid
    of indices under the tests' own seed.
- **The design and every baseline use the same keying.** Two arms deciding at the same moment, on the same start,
  under the same seed, read the same side uniform. That is the pairing.
- **The side coin's key carries no account and no firm index (m-9).** Trades of one user's accounts and firms at one
  moment read the same draw. Since E-221 (O-4) that means only the refusal of opposite positions at once (conduct
  tier 1), never that every account copies every trade: accounts alternate, and the coin is the evaluation's device,
  not the playbook's (CHARTER 3.5). The forced side of 3.5 (a new trade takes
  an open position's side) is a function of earlier uniforms.
- **Each user (start) has its own coin draws** (choice 3; the coordinator's ruling stands). The key carries the start
  day. Users are independent, which 2.2's bounds use; **2.2 (a) is valid only under it** (N-2). **The keying is pinned
  with m.** MEASURES.md 1.4's reading 3, which assumed draws shared across starts, is being aligned to choice 3 on
  wt-user.
- **Uniforms lie on the symmetric grid** (2i + 1) 2^-53, for i = 0 .. 2^52 - 1: odd multiples of 2^-53, each exact in
  float64. 1 - U is (2 (2^52 - 1 - i) + 1) 2^-53, again on the grid and computed exactly, so the antithetic twin of 2.3
  is exact in floating point. Every threshold is written `U < p`.

### 1.6 Overlapping positions: one shared driftless path (B-3)

CHARTER 3.2 fixes only each trade's marginal law. The joint law of trades whose holding intervals overlap must be
declared, or the keying decides it by accident:
- trades opened at different moments get independent draws: fake diversification;
- trades opened together get one uniform at different thresholds: a comonotone coupling, which a single path does not
  produce.

**The declared law.**
- For each unit u and **underlying** (MNQ and NQ are one), there is **one driftless tick path**: a symmetric lattice
  walk, its steps drawn from the coin field, its clock scaled by the real path's causal volatility (the schedule's
  field, 1.7).
- Every open position of the user, on every account and firm, reads its exit from that path from its fill:
  - the target g in its side's direction;
  - the nearer of its stop and its account's cushion against it.
- Its exit time is the path's.
- For a lone position the outcome law is exactly the race of 1.1: a symmetric walk on a lattice that divides the
  barriers exits at gambler's-ruin odds.
- Positions whose holding intervals do not overlap read disjoint stretches of the path, so their outcomes are
  independent, as now.

**What runs before the template defines overlap.**
- A position with no overlap uses 1.1's single race uniform, with its resolution time as run (CHARTER 3.2, unchanged).
- **A design that holds two positions of the user at once is refused by the runner** until the search template defines
  overlap. That covers several accounts, several firms, or a second component entering while the first is open. This
  is the amendments' m-2 position, and the template's to settle with R-10.
- **To settle there:** whether a lone position also takes the path's exit time. This note uses the run's time for lone
  positions and the path's time inside an overlapping set.

**The H3-A check: copy against stagger (pass rule corrected, N-3).**
- On a toy, design X sends one trade to N accounts at one moment, through **the copy routine**. Design Y sends the same
  N trades staggered by s minutes, s on a declared grid starting at zero, through **the stagger routine**. These are two
  separate code paths.
  - X is a test fixture only. Copying one trade across accounts is a conduct-tier-1 pattern and is never a candidate.
- **The pass rule, under the shared path:**
  1. **At s = 0, X and Y are bit-identical**, journey for journey. The two routines must agree; one routine compared
     with itself would prove nothing.
  2. **The X-against-Y composite difference is non-decreasing in s**, up to its coin-noise interval. Staggered
     positions overlap less on one driftless path, and disjoint stretches are independent, so the stagger buys real
     time-diversification, growing from zero toward the independent case.
  3. **The gap between the shared-path law and per-trade independent draws**, for Y at the same s, falls to coin noise
     once s exceeds the longest holding time on the toy. That gap is what must shrink with s.
- A build that ignores the path fails (1) or (3). A correct build passes all three.

**Deferred to the template (N-4; the search template on wt-lit), recorded now. Overlap stays refused until then.**
- **The lattice.** A cushion in dollars over the tick value and size is generally not a whole number of ticks, and
  several positions' barriers need not share a lattice.
  - Every barrier is **rounded inward** to the path's lattice, so the walk never exits beyond the room and the clip
    never binds. Rounding outward and then clipping would bring B-1's edge back in a small form.
  - The zero-expectation oracle is extended to the path, per position, at fractional cushions.
- **The key.** One path per **underlying**, never per instrument (MNQ and NQ are one).
- **Overlap.** It is defined once, before any draw, on the scheduled entries and **the run's** exit times. The path's
  exit times are never used to decide whether two positions overlap, because that would be circular.

### 1.7 The schedule interface (m-6)

The build's journey is a typed function: journey = f(schedule, coin field, rules). The deciding reading depends on a
history only through the schedule.

**The schedule's fields, per trade:**
- instrument and its underlying, entry moment and fill price;
- bracket (g, l) in ticks;
- the side's source;
- the causal volatility per bar of the trade's holding window: the path's clock, and whatever R-10's time-limit
  redraw reads;
- the flatten time, the news flag (tier 1: no maximum size into major news; E-202's windows), and costs.

The account state (cushions, the daily loss room) is replayed from the rules, not read from history.

- **The exact test the build adds:** two different real-bar paths with one schedule give bit-identical journeys on the
  deciding reading.
- Stage 2's `mae` settlement reads the intra-trade path. It belongs to the as-walked reading only.

---

## 2. The coin-seed leg

### 2.1 The replicates

- **Given H, every unit's term d_u is a function of that unit's own coin field.** Distinct units have distinct keys
  (1.5), so **the terms are independent across starts and seeds**, whatever their differences in law.
- Seed sets of m seeds, disjoint, give i.i.d. replicates Delta_j = C(f; S_j) - C(beta; S_j).
- No approximation enters. The overlap of start-day windows (Q-16, 3.1) changes the terms' laws, not their
  independence given H. It therefore does not reach leg (i).
- The test's seeds are declared by the search's declaration, disjoint from every seed drawn on the search years.
  **J (and m) are fixed before the read and never extended after it.** Hoeffding's, McDiarmid's and the
  empirical-Bernstein bound are not anytime-valid.

### 2.2 The deciding bound, by the composite's form (m-1, B-4)

**(a) Unconditional means with a priori bounds: Hoeffding's or McDiarmid's bound over all J x |E_h| units.** The
paragraph between the markers is written to be copied verbatim into H3's declaration (N-1, N-2).

<!-- 2.2a-admission: begin -->
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
     [0, h_d]; a dollar amount within the limits that the firm's verified rules and the design's declared purchase cap
     imply over h_d sessions;
   - (ii) a per-unit clip written into the dimension's own definition, x_d(u) = clip(y_d(u), a_d, a_d + r_d), pinned
     in CHARTER 3.9's row and shown to the operator with the composite's caps.

   **No bound is ever estimated from data, on any years.**
3. **What it does not admit.** These are decided by 2.2 (b) whenever the composite holds one:
   - a conditional share or mean, whose denominator is a random subset of E_{h_d} (the share falling back among those
     who reached break-even, for example);
   - a ratio of means (payouts per funded account, for example);
   - a tail mean (CVaR10);
   - a quantile.

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
<!-- 2.2a-admission: end -->

- P(LB > theta(H)) <= alpha for every history, with no premise of identical distribution.
- Narrow caps (hi_d - lo_d small against r_d) widen the bound. That is shown with the caps in Wave 4.2.

**(b) Any dimension not admitted by (a):** a bound over the J i.i.d. seed-set replicates, Delta_j in [-1, 1].
- The candidates are the one-sided empirical-Bernstein bound (Maurer and Pontil 2009, theorem 4), applied to
  (Delta_j + 1) / 2 and mapped back:

      LB = Delta-bar - sqrt( 2 V ln(2/alpha) / J ) - (7 ln(2/alpha) / 3) x 2 / (J - 1)

  and the hedged betting bound (Waudby-Smith and Ramdas, JRSS-B 2024).
- **The rule, stated now: the one of the two that needs the smaller J for power pi\* at delta\* decides.**
  - It is **applied in H3-D only** (N-6), after Wave 4.2 has set delta\*, with H4's search-year sigma, and before the
    search's pin.
  - H3-A reports both bounds' J on its toys, and applies nothing.
- Both are valid for every J and every history, and under any keying across starts.

**No t decides, in any branch.** Its size at alpha depends on the replicates' skewness and cannot be checked (2.6).
The larger-of t of E-035 is reported beside, deciding nothing.

### 2.3 The same-design nulls (exact)

**(a) The antithetic twin: the complement of every uniform, the redraw and the path's steps included.**
- The twin of design x is the same code on U\* = 1 - U:
  - the side coin, side = 1[U < 1/2], is reversed;
  - the race redraw, a win at 1[U < p], becomes a win at 1[U > 1 - p];
  - each step of the shared path reverses, so the path is mirrored;
  - every other draw is complemented.
- **Exactness.** U\* has the law of U, and the pair (U, U\*) has the law of (U\*, U). So (C(x; U), C(x; U\*)) is
  exchangeable given H, and Delta is symmetric with mean exactly zero, for any functional, every entry type and every
  history. On the grid of 1.5 it holds bit for bit.
- The forced side of CHARTER 3.5 is a function of earlier uniforms, so the twin stays exact under it (m-8).
- **The charter's words (m-8).** CHARTER 3.7's "every coin side reversed" is the uniform complement, and no redrawn
  outcome is ever reversed. Reversing an outcome maps p to 1 - p and breaks equal expectation; a build that does so is
  a defect, and this null catches it. The lead rewords 3.7 in the next row.
- The deciding reading removes direction by the reflection after the real fill, so the twin is exact for resting
  entries. The as-traded reading draws no side coin. It is beside, never tested.

**(b) Disjoint seed sets.** The same design on S_j and on S'_j, every key distinct:
Delta_j = C(x; S_j) - C(x; S'_j). It is i.i.d. and symmetric with mean zero.

**The guards, refused before any rate is read:**
- a null pool whose Delta_j are all zero;
- a disjoint pool whose variance is outside a declared tolerance of twice the single arm's;
- **any two keys with one `generate_state`** (m-4, N-8), across the arms, the S sets and the S' sets, the histories
  and the parts. This is checked on the key lists, never on outcomes;
- any coin key without the unit's start (N-2), and any key word at or above 2^32 (N-8).

### 2.4 A third coin-seed null: exact centring on toys

Both same-design nulls are symmetric, so neither can show laxity driven by skew. The third null is asymmetric:
- **Toys whose expectation is exact.** Schedule-level histories (1.7), brackets in ticks, one to three accounts with
  balances on a tick lattice, no overlapping positions.
- On the martingale-outcome reading, each unit's E[a(x, u) | H] is computed exactly by forward dynamic programming
  over the state along the schedule: account state, balance, peak out-of-pocket, payouts, and the month closes.
- **The DP uses 1.1's race law** (B-1): the win probability min(l, c) / (min(l, c) + g) at each state's own cushion c.
- Two different designs x1 and x2 (different brackets, sizes or purchase rules) give theta(H) exactly. The centred
  terms are an exact mean-zero null with x1 and x2's real skew.
- Until R-10 fixes the time-limit redraw, the toys use only trades that resolve at a barrier.
- For a composite with quantile dimensions, theta_m is centred by a pool of at least a hundred times J independent
  seeds. Its error is reported, and **that null is labelled approximate**.

### 2.5 How many seeds (arithmetic; m-1)

- **Hoeffding's (a).** The power at true difference delta is about Phi((sqrt(n) delta - c_h) / sigma_u), where
  c_h = sqrt(2 ln(1/alpha)) and sigma_u <= 1. So n >= ((c_h + z_pi) / delta)^2 terms suffice, and J = n / |E_63|
  seeds.
- **The empirical-Bernstein bound (b).** The variance term needs about (c1 + z_pi)^2 (sigma / delta)^2 replicates. The
  range term, c2 x 2 / (J - 1), stays below a share of delta only when J >= 1 + 2 c2 / (share x delta). With a seed
  set's sigma small against the range, **the range term sets J.**
- Appendix A prints, at k = 13 and for three illustrative values of delta: Hoeffding's n and J at |E_63|, and the
  empirical-Bernstein range term's J. **Under choice 3, (a) needs orders of magnitude fewer seeds than (b).** The
  variance-term factors and their ratio to the normal t's are printed too.
- delta is the operator's (O-3), so those values only show the formulas.
- sigma comes from the same-design pools on the toys (H3-A) and from H4's per-seed outputs (H3-D).

### 2.6 The size check across histories

The size of leg (i) is a statement for each history. The check runs over many histories and reports them one by one
as well as pooled.

**History classes.**
- **S1, synthetic schedule histories** (1.7). Their dependence lives in the schedule:
  - volatility persistence and regime switches (`family_stats.slow_sign`, `slow_two_state`, or a log-AR(1));
  - signal arrivals whose rate follows volatility;
  - brackets in volatility units with dollar caps (RD-04's units);
  - resolution times that lengthen with the bracket over volatility.

  Parameters are stylised in H3-A and fitted on **the search years only** in H3-D.
- **S2, block resamples of the search years (H3-D only).** The stationary bootstrap
  (`family_stats.stationary_indices`), with a mean block at least h\*.
  - For the history null only, each block also takes a symmetry with probability one half (2.7).
  - **S2's count of distinct source blocks is reported:** at h\* = 252 the search years hold few disjoint blocks
    (Appendix A, `units_S`), so S2's histories are recombinations of few blocks.
  - Never the held-out years: the runner refuses them.

**On each history r = 1 .. R, for each null class (antithetic, disjoint, exact-centred):**
1. *The premises of 2.2*:
   - the pool's mean is consistent with zero;
   - symmetry for (a) and (b);
   - no serial dependence in seed order;
   - every term inside its range;
   - the key guard of 2.3.
2. *The procedure's rejections at the feasible levels* alpha' in {0.05, 0.01, 0.001}, on floor(M / J') disjoint groups
   of a declared J'.
3. *The rejections at alpha itself*: counted and printed.

**What the count can show (B-4).** E-052's criterion (`lift_bound.clopper_pearson`; `scripts/q108_validate.py`'s
`criterion`) fails a null when its 95 % Clopper-Pearson interval lies wholly above nominal. Appendix A prints, at each
level and at the rule of three's n:
- the fewest rejections at which the criterion fails;
- the true rate, as a multiple of the level, that it detects half the time.

**So at that n, a pass means only "no laxity detected": a procedure lax by a factor of that multiple passes half the
time.**
- **"No laxity beyond a factor kappa"** is claimed only where the pooled count of tests reaches the n at which, at the
  nominal rate, the Clopper-Pearson upper limit is at most kappa x alpha' with probability pi\*. Appendix A prints that
  n at kappa = 2.
- At alpha itself neither count is within reach. **The full level rests on the theorems of 2.2, whose premises this
  check confirms.**

**The whole rule** is leg (i) and the time conditions and the limits and the floors (CHARTER 3.7). It rejects a
same-design null no more often than leg (i) alone does. Its rate is printed beside leg (i)'s.

### 2.7 The history null (m-10)

**What it measures.** The level is conditional on H. A design no better than the baselines across histories, whose
shape suits H, passes leg (i) correctly given H and falsely across histories. The history null prints that risk beside
every verdict (CHARTER 3.7, 3.8 (b)).

**Construction from a symmetry of the generator.**
- Let G be a history generator, and sigma a bijection of histories with sigma(H) distributed as H under G.
- D' is "D acting on sigma(H)": D'(H) = D(sigma H) as whole journeys, the coin keys mapped by the same bijection.
- For **any** functional C:

      E_H[ C(D'; H) ] = E_H[ C(D; sigma H) ] = E_H[ C(D; H) ]

  The two designs are equal on average over histories exactly, and differ on any one history. With
  theta_pair(H) = E[ C(D'; H) - C(D; H) | H ], an involution gives theta_pair(sigma H) = -theta_pair(H).
- Exactness needs sigma to preserve G's law and to leave the start set and the embargo unchanged. Each symmetry below
  acts within a day.

**The symmetries.**
1. **On S1: two exchangeable trigger streams.** G emits, each day, two schedule streams A and B that are i.i.d. given a
   common daily factor (volatility, the news flag). sigma swaps them. D draws a component's trades from stream A, and
   D' from stream B. Every rule the journey reads treats the streams alike; the build asserts it on the toy's rules.
   (A price mirror is not defined at schedule level.)
2. **On S2: the mirror.** Each resampled block is reflected about its sessions' opens with probability one half, by a
   declared coin. The resample law is then mirror-invariant, whatever the real data are. D' mirrors every price-level
   trigger.

**The pairs, labelled (m-10).**
- Each FPR_hist row names the pair it used: the finalist itself (D = the finalist, where its components sit on one
  stream, or on S2's mirror), or **"stylised"** where the finalist cannot carry the symmetry. One example is a finalist
  with different rules in two sessions.
- The rate is printed per finalist with its label, and with the pair's spread sd_H(theta(H)) over delta\*.

**The known truth and the computation.**
- On the DP toys theta(H) is exact on every history. A false pass then splits into coin luck (theta(H) <= 0) and
  history luck (theta(H) > 0).
- On each history a pool of M seeds estimates theta-hat(H), sigma-hat(H) and the per-year and per-regime differences.
  The coin leg's pass probability at the test's J is computed by 2.5's formula and multiplied by the time conditions'
  indicator.
- **The shortcut's error is reported**, against a declared subset of histories run in full at the test's J.
- FPR_hist tends, on a symmetric pair, to the share of histories on which the time conditions hold with
  theta(H) > 0. That is why the time conditions are the defence against history luck.

---

## 3. The years leg and the held-out leg

### 3.1 The unit, calibrated per horizon (m-7)

- **The time legs' unit is the history block**, at least as long as h\* when it is resampled (2.6, S2). The
  conditions of 3.4 read start-year groups and regimes, which are not history blocks (3.4 says what that costs).
- **Q-16's finding** (`docs/research/calibration_2026-11-15.md` 7.2, 7.4): every batch-type variance on P's start-day
  series is biased low, because neighbouring starts' windows overlap in h - 1 sessions. `pcons` held but detected
  almost nothing; `bm63c` was not adopted (E-085). Longer horizons overlap more.
- **Calibration per horizon** means:
  - every statement about a time condition (its stated size, any interval beside) is computed at each dimension's own
    h_d;
  - resampled blocks are at least h\* long. The caution of `tests/test_family_stats.py`'s strict `xfail` applies;
  - an interval beside uses a variance window of at least h_d: `p_bound.flat_top` with FLAT = h_d and TAPER = 2 h_d,
    batches of at least h_d starts, `n_eff_bartlett` at lag h_d. Its fixed-b critical values are simulated per
    (n, h_d). `p_bound.HORIZON` becomes each measure's horizon.
- **The null classes for those intervals (m-7):** search-year paired start-day series of H4's baselines, and the
  synthetic moving-average and structural classes. **Not Q-16's real paired nulls:** they are the judged block's
  series, the held-out years.
  - `results/calibration_p.csv`'s columns stay the template for H3's size tables.
  - **For the lead:** Q-16 (E-035, E-083, E-085) enters the held-out read ledger of CHARTER 3.6 (b), which does not
    name it today.

### 3.2 The minimum-units arithmetic (m-11)

- **An exact sign-flip test over B independent units** (`lift_one_sample.exact_flip`, `flip_blocks`,
  `pattern_signs`) has a smallest p-value of 2^-B, so it needs B >= B_min = ceil(log2(1/alpha)).
- At k = 13, alpha lies between 2^-12 and 2^-11, so B_min = 12. At k = 14 to 17, B_min = 13 (Appendix A).
- **The held-out years**, on the weekday bound W_H >= N_H (no session list read), hold at most ten disjoint 63-session
  units, against twelve needed. At every horizon from 63 sessions they hold fewer than twelve (Appendix A, `units_H`;
  the count with a partial unit is printed beside it).
  - Twelve disjoint 63-session units would need three years of sessions, more than the two and a half years the
    held-out dates span.
  - The fallback's horizon is 63, so no composite containing P can give the time legs twelve units.
- **D-145's gate horizon H_g is 504 sessions** (`horizon_days: 504` in Stage 2's gate configs). The held-out years
  hold at most one disjoint 504-session block, and at most W_H - 503 complete starts. The search years hold at most two
  (Appendix A). See 4.4 for what that does to the gate.
- **For the lead:** E-208's "about a dozen 63-session units" should read at most ten complete ones. The conclusion
  holds a fortiori.

### 3.3 Why the time legs are consistency conditions

1. **No exact test can reach alpha on them** (3.2).
2. **No asymptotic test can be calibrated there.** With ten units at most, a HAC or batch t's reference is the fixed-b
   one at a bandwidth near the sample's length. Q-16 found batch t's lax on these series at 63. Certifying one at alpha
   would need more independent histories than the rule of three allows (Appendix A).
3. **They cannot raise the size.** The rule is a conjunction, and rejects no more often than leg (i). Their job is to
   lower FPR_hist (2.7).
4. **Their stated size** is P(the condition holds | no difference), computed on the actual groups with the overlap
   counted (3.4), and on the history null's generator per horizon. It is printed beside the verdict.

### 3.4 The conditions, written exactly (m-3)

Each condition is read for every pair (f, beta), on the martingale-outcome reading, at the point estimate pooled over
**all** the test's seeds. Coin noise inside a group is small: its standard error is printed beside.

**(Y) Most years: start-year groups.**
- **The groups.** For each dimension d, its units are E_{h_d} restricted to the starts dated in year y, for y in
  {2024, 2025, 2026}. So the groups partition leg (i)'s own start sets.
- **The groups are not history blocks.** Their windows overlap: a start in late 2024 reads 2025's sessions. A last
  year's group is a partial block of starts, shorter than h\* except at h\* = 63.
- **n_min is fixed by calendar arithmetic only** (N-7), never from a held-out count of anything but sessions.
  Y_ok = the years whose count of complete starts at h\* on the pinned session list is at least n_min.
  - Appendix A shows both candidates' stated sizes at each h\*: n_min = h\*, and n_min = 21 (a month of starts).
  - **Proposed: n_min = 21**, the choice with the smaller stated size at every h\* the composite can have. At h\* = 252,
    n_min = h\* leaves one group and a vacuous (Y), while 21 keeps two.
  - The pinning row sets the final value, before any read.
- Delta-hat_y = C(f; group y) - C(beta; group y), the composite on the group's units.
- **(Y) holds when Delta-hat_y > 0 for every y in Y_ok: n_Y = all of Y_ok** (N-7). A strict majority of three is a
  size of one half whatever the correlation, so it would be vacuous.
- **Its real size, with the overlap counted** (Appendix A's (Y) lines, on the weekday calendar). The model is
  per-session contributions i.i.d. and symmetric (white noise), so each group's difference is a weighted sum of them.
  - Groups whose windows share sessions are correlated, and P(all positive) is a Gaussian orthant probability.
  - Positive serial dependence in the real contributions raises it further. The history null's generator gives that
    figure (3.3 (4)).
  - The white-noise figure is **a lower bound** (Slepian's inequality: positive dependence raises orthant
    probabilities). Appendix A prints it as "size>=", and this word stays beside it wherever it is printed.
  - At h\* = 252 with n_min = h\*, Y_ok holds one year: a stated size of one half, so vacuous. At n_min = 21, the two
    groups' overlap gives a size above the independent quarter and below one half (Appendix A).

**(R) Both regimes.**
- rho(t) = volatile if v(t) > v\*, else calm.
  - v(t) is the start's causal volatility in RD-04's unit, **computed only on bars closed before the start's first
    decision moment** (bar stamps are open times, `feature-rules`). Its look-back may enter the search years.
  - v\* is fixed from the search years by a rule pinned in 3.9.
- R_ok = the regimes holding at least n_min complete starts. n_min is the calendar's figure above, never a held-out
  regime count, which would need held-out bars.
- **(R) holds when Delta-hat_r > 0 for every r in R_ok.** A regime outside R_ok is reported beside. Its stated size
  is computed on the history null's generator per horizon (3.3 (4)), and it carries the same vacuity label.
- **(R) is not a split into history blocks.** Regimes interleave in time, so a calm start's window holds volatile
  days. If the held-out years sit mostly on one side of v\*, R_ok holds one regime and (R) is the overall sign again.

**(H) The held-out leg.** Leg (i), (Y) and (R) read only:
- held-out starts complete at their horizon;
- outcomes from held-out sessions;
- search-year sessions only for causal normalisers.

The runner refuses any other start or session. (H) is a scope condition.

**Vacuity (N-7).** **A condition whose stated size is at least one half is labelled vacuous**, and the label is printed.
One group or one regime always gives one half. A vacuous condition is still applied, as the rule says, but it is
reported as adding no protection against history luck.

**Printed beside every verdict:** |Y_ok| and |R_ok|; each condition's stated size on the actual groups (the white-noise
lower bound, and the history null's figure); and each condition's label, vacuous or not.

**The rule for one pair:** LB > 0 and (Y) and (R) and (H). For the finalist, all four baselines, with CHARTER 3.8
(a)'s limits and (c)'s floors.

### 3.5 Reported beside, deciding nothing

- Per group and per regime: Delta-hat with its coin-noise standard error.
- The exact sign-flip p-value over the complete blocks of length h\*, with its floor 2^-B.
- For the fallback: the P comparison's interval with 3.1's per-horizon variance.
- Each condition's stated size and its vacuity label (3.4).
- The share of seed sets (or units) with any dimension at a cap, and the note that under clipping the estimand moves
  with J near a cap (1.3, N-11).

---

## 4. The power check

### 4.1 The parameters

| parameter | class | value or source |
|---|---|---|
| delta\*, "the size that matters", on the composite's scale | fixed, the operator's (O-3, Wave 4.2) | **a parameter here** |
| pi\*, the power target | fixed in 3.9's pinning row | proposed: `family_stats.MDL_POWER` (the test checks the script's value against it) |
| alpha | fixed | 0.05 / (k (k + 1)) at the search's k |
| J, m, the deciding bound | J and m set by 2.5's formulas so that power at delta\* reaches pi\*; the bound by 2.2's rule | H3's declaration, before the read |

### 4.2 The plants

Each plant is an improvement whose true size on the composite is known. Its power is the whole rule's pass rate at
the plant whose true size is delta\*.
- **P1, linear** (the statistic alone): the null terms plus delta. `family_stats.conjoint_mdl_linear` gives each line's
  MDL and the conjoint one.
- **P2, structural** (zero edge kept): a lower fee, a shorter payout delay, a cheaper purchase rule. Its true delta
  comes from the DP toys or a pool of at least a hundred times J.
- **P3, edge plants** (zero edge broken on purpose):
  - the race's win probability raised by epsilon;
  - F-04's value arm, every executed trade's dollar P&L shifted (E-208).

  Each is mapped to the composite by the pool.
- **P4, a regime-varying plant:** delta_t = delta\* (1 + a rho_t), with rho_t a slow sign (`family_stats.slow_sign`,
  `lift_one_sample2.drift_draw`), and a over a declared grid.

`family_stats.conjoint_mdl_grid` gives the smallest delta on a grid at which at least pi\* of the draws pass every leg
together. **The line has power at delta\* when that MDL is at most delta\*.**

### 4.3 On synthetic plants and on H4's baselines

- **H3-A (toys).** P1 to P4 on S1. They test the statistic, the replicate structure and 2.5's formulas against
  simulation, and report both of 2.2 (b)'s bounds' J (N-6). They apply no rule.
- **H3-D (the deciding power gate, after H4 and the pinning row).**
  - H4's per-seed outputs of the four baselines on the search years supply the real spread of each pair's terms.
  - The planted finalist is the best baseline plus a plant of delta\*, against all four baselines.
  - Power comes from 2.5's formulas, checked end to end by P2 and P3 on S1 fitted to the search years and on S2.
  - The held-out years are read by none of this.

### 4.4 The gate's other clauses (CHARTER 3.7; m-11, m-12)

**The limit clause (E-015's condition).** A ceiling L passes when M-hat + w <= L; a floor is the mirror image.
- **"Its noise" is coin noise** (m-12): w is the coin-seed half-width at the margin's pinned level, given H. This
  matches the level's scope, which is conditional on H, and keeps power.
  - The history-variation reading (3.1's per-horizon variance) is printed beside, with FPR_hist.
  - The choice is the operator's under O-5. It is fixed in the pinning row before any read.
- A design equal to the best baseline passes with probability at least pi\* only if the headroom L - M_best is at least
  about (c_L + z_pi) sigma_M / sqrt(J). The gate prints the headroom per limit and fails if a pinned limit lacks it.

**The gate's quantile at H_g = 504 sessions.**
- The held-out years hold at most W_H - 503 complete starts (Appendix A), and they overlap almost entirely. They hold
  at most one disjoint 504-session block, so **history-block resamples for the gate's quantile cannot be formed on the
  held-out years.**
- So the held-out gate's lower quantile is **over coin seeds only**, given H. The history-block reading is the search
  years', and they hold at most two disjoint blocks: it is reported beside.
- 3.6 (d)'s purge removes a 504-session strip at the end of the search years from the gate's starts.
- **The complete-start count** must reach the minimum pinned in 3.9.

**The rule.** The gate passes when:
- the whole line's MDL is at most delta\* at alpha;
- every limit has its headroom;
- the count reaches its minimum.

Otherwise the search does not pin, and the data question (E-007 (2)) goes to the operator with the gate's result.

---

## 5. The fixed sequence over finalists

**The procedure.**
- The finalists f_1, ..., f_F are ordered on the search years by the rule pinned before the survey, and the order is
  fixed before the held-out read.
- Each is tested at its own latency L, in its place, by the whole rule at the **full** level alpha (CHARTER 3.7; E-203
  S-1).
- From i = 1: if f_i passes it is carried, and f_(i+1) is tested next. If f_i fails, the sequence stops.
- The pinned fallback stands in place of the composite and is never tried after it.

**Why the family-wise error is at most alpha.**
- Let i_0 be the first finalist in the order whose null is true.
- A false carry needs f_(i_0) to pass, and P(f_(i_0) passes | its null) <= alpha. The intersection-union test is at
  most each comparison's level, each comparison is at most alpha by 2.2, and the conjunction only lowers it.
- So P(any false carry) <= alpha, strongly.

**What it costs and what is printed.**
- The gate's power is the first finalist's; a later one's is conditional on every earlier one passing.
- FPR_hist is printed per finalist, with its pair's label.
- The level is printed nominal when the held-out read ledger is not empty.

---

## 6. What H3 runs

### 6.1 The order, and what reads what

| part | when | reads | seeds (section 7) | weight |
|---|---|---|---|---|
| **H3-0** the probe | after the build's merge | synthetic toys, a few hundred lanes | the probe's | light |
| **H3-A** design checks: A1 same-design nulls (2.3); A2 the exact-centred toy null (2.4); A3 the history null on S1 (2.7); A4 plants P2 to P4 (4.2) and the copy-against-stagger check (1.6) | before Wave 4.2 | **no bar**: S1 with stylised parameters; placeholder composites (`P_B` at a placeholder budget, and a clipped toy composite) | the design-check block | heavy, one part a slot |
| **H3-D** the deciding calibration: D1 same-design nulls on the **pinned** rule; D2 the history null on S1 fitted to the search years and on S2; D3 the power gate (4.3, 4.4), with its full-J check | **after 3.9's pinning row (Wave 4.2) and H4's collection; before any search pin** | the search years' bars, H4's search-year outputs; **never a held-out session** | the deciding block | heavy, one part a slot |
| **H7** the held-out test (Wave 6, listed for its cost; m-1) | after the search pin | the held-out years, once | the search declaration's own | heavy |

- H3-A's results are **design checks only** (CHARTER 3.7, m-7). They:
  - report both of 2.2 (b)'s bounds' J at placeholder values of delta;
  - size m and J';
  - fix the generator's form.

  Nothing in them is read as the deciding calibration, and they choose no rule.
- **H3-D applies 2.2 (b)'s smaller-J rule** (N-6), at the pinned delta\* and H4's search-year sigma, and fixes J and m
  before the search's pin.
- The deciding seeds are drawn by nothing before H3-D.

### 6.2 Memory

- **The cap.** One heavy job at a time, at most two workers, under 2.5 GB in all, so 1.25 GB a worker.
- **Per worker:** M_0 + L_w x b_lane, where:
  - M_0 is the process base;
  - L_w is the lockstep width;
  - b_lane is up to eight accounts of sixteen float64 fields, plus forty float64 of reductions.
- Appendix A prints L_w's ceiling at an assumed M_0. **H3-0 measures M_0.**
- At these sizes memory does not bind. Nothing per journey is kept beyond its reductions:
  - per seed: the composite's dimension values and the per-group and per-regime partial sums;
  - per unit: `P_B`'s inputs;
  - a schedule-level history is a few thousand rows.
- The shared path of 1.6 is generated per unit and underlying as it is read, never stored.
- A part that walks real bars (S2) holds one copy of the search years' minute bars per worker, read in place through
  the junction.

### 6.3 Time

- **A part's work** is R x arms x M x |T| x h x tau lane-trades. **Its wall time** is that work x c / 2, where c is the
  cost of one lane-trade, which **H3-0 measures**.
- Appendix A prints each part's work, and its hours at three assumed costs. The rows include:
  - **H7, the held-out test**, under (a) Hoeffding at Appendix A's J and under (b) the empirical-Bernstein range term's
    J, with three finalists assumed and four baselines;
  - **D3's full-J check.**

  The gap between the two H7 rows is the compute that choice 3 and 2.2 (a) save (m-1).
- **The rule before any heavy part starts:**
  - a part whose estimate at the measured c exceeds eight hours (`PART_CAP_H`) is cut, M first, with the power cost
    stated;
  - or it is split into sub-parts, each its own heavy slot under the lock;
  - the sizes are recorded in H3's declaration before the run.
- Each part runs from a clean checkout (`scripts/run_clean.py`) under `run.lock`, one at a time, watched to its exit.

### 6.4 Outputs

Every output is written with a manifest (`write_result`), from a clean run, carrying its seed map and its keys' kinds.

**The size table** uses `results/calibration_p.csv`'s columns plus:
- `history`, `history_class`, `horizon`, `J`, `J_prime`, `bound`;
- the premise checks;
- each level's "no laxity detected" or "no laxity beyond kappa" label (2.6).

**The history-null table:** per pair (labelled) and history, theta(H) where exact, the estimates otherwise, the time
conditions, the pass probability, and the shortcut's error; FPR_hist per finalist.

**The power table:** per plant and size, the whole line's pass rate, each line's, and the conjoint MDL.

**The reused code:**
- `p_bound`'s `paired`, `batch_t`, `obm`, `flat_top` and the fixed-b nulls;
- `user_measures`' `p_by_month` (with the peak, per MEASURES.md section 2) and `n_eff_bartlett`;
- `family_stats`' `stationary_indices`, `slow_sign`, `slow_two_state`, `block_mean_amplitude`, `year_mean_amplitude`,
  `conjoint_mdl_grid`, `conjoint_mdl_linear`, `need_from_lowers` and `mdl_from_need`;
- `lift_bound.clopper_pearson`;
- `lift_one_sample`'s `exact_flip`, `flip_blocks` and `pattern_signs`;
- `scripts/q108_validate.py`'s `criterion`;
- `scripts/q126_calibrate.py`'s `ProvenanceRefused` and `RetiredSeedMap`, with E-195's part ledger and crash rule.

`family_stats.rng_of` is **not** used for coin keys. It passes a variable-length list, which is m-4's trap; the
build's keys come from `seed_key`'s form. `family_stats.power_gate` and the B2 nulls retire with the trade-lift line
(E-208).

---

## 7. Seeds

**The block, by role.** Every draw is keyed by `three_way_arith.seed_key`'s fixed-length form (1.5): the role's seed,
a nonzero tag for the kind (history, symmetry, coin, plant, test), and exactly that kind's fields. Each part's field
values are fixed in H3's declaration.

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

**How the block was found (2026-11-18, before the first text was committed).**
- **A word-bounded literal search** for every eight-digit number beginning 2026, in three places:
  - `git grep -Iw` on every branch, remote and tag (24 refs);
  - every line added or removed in every reachable commit (`git log --all -p`, 518 commits);
  - `grep -rIw` over the working copy, tracked and untracked, of every worktree and clean checkout
    `git worktree list` names (15). The licensed data, `.git` and caches were excluded.

  It found no literal of the block, and no literal with a residue modulo 1,000 between 870 and 879. The nearest
  residues held are 838 and 900. The nearest literals by value lie more than a thousand seeds away. 58 is no month.
- **Q-108's AST fold guard**, re-pointed at the block with its allow-list emptied, over every `.py` of the working
  tree and every ref: no refusal. It printed three hand-checked loop expressions of `tests/test_features_lookahead.py`
  at older refs, each needing a reach of thousands of seeds against loops of tens, a handful and under 790.
- **What that guard cannot see (m-5).** It folds only names bound directly to an integer literal. It does not follow a
  name bound to an expression, fold pure-literal arithmetic, or read strings. It found nothing in this note's own
  test, which builds all ten seeds by arithmetic. So "no refusal" shows the block free of that one pattern only.
- **The guards that repeat on every run** (`tests/test_three_way_design.py`):
  - the literal scan of every tracked file and every working text file;
  - **an arithmetic fold over every tracked `.py`**, with no prefilter on the year's digits (N-9). It folds:
    - pure-literal integer expressions, `**` included;
    - names bound to them, whether plainly, by tuple unpacking, or by augmented assignment (`+=`, `*=`, ...), in source
      order.

    It flags any expression or binding equal to the block's prefix, the prefix times ten, or a seed of the block. **It
    must find this test's own construction** (its positive control), and it allows it nowhere else.
  - Unit tests check the fold on planted sources: names; a power written without the year's digits; augmented
    assignment; tuple unpacking.
  - **The static fold is a tripwire, not the guard.** String concatenation, calls and runtime arithmetic stay outside
    it. **The guard is the build's run-time assertion:**
    - H3's build reads its seeds from one module, added to the test's `DERIVED_USES` and `DECLARED_USES` as it is
      written;
    - it asserts at run time, in `RetiredSeedMap`'s manner, that every key whose first word lies in the block came from
      that module;
    - it asserts that every key's `generate_state` is distinct from every other's (2.3).
- **The key test builds its keys under the tests' own seed** (N-10), never under a design-check or deciding seed.

---

## Appendix A. The arithmetic (printed by `docs/plans/scripts/three_way/three_way_arith.py`)

Every figure the note cites is here and nowhere typed.
- `units_H` and `units_S` are the most window-disjoint units in the held-out and search years, with a partial unit
  beside. `starts_H` and `blocks_H` are the complete held-out starts and their blocks of h. All are upper bounds from
  the weekday counts.
- The (Y) lines use the weekday calendar's start-year groups.
- The run plan's sizes are proposals for H3's declaration, and its costs are assumptions (6.3).

<!-- three_way_arith: begin -->
```text
levels: k, 0.05/(k(k+1)), B_min, 2^-B_min, 2^-(B_min-1)
  k=13  alpha=2.7473e-04  B_min=12  2^-B_min=2.4414e-04  2^-(B_min-1)=4.8828e-04
  k=14  alpha=2.3810e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
  k=15  alpha=2.0833e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
  k=16  alpha=1.8382e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
  k=17  alpha=1.6340e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
weekdays (upper bounds on sessions): held-out W_H=663, search W_S=1042
per horizon h: disjoint units floor(W/h) held-out (with a partial one) | search; complete held-out starts W_H-h+1; held-out start-blocks of length h; sessions needed for B_min(13) disjoint units
  h=21   units_H<=31 (partial 32)  units_S<=49  starts_H<=643  blocks_H<=30  sessions_for_12_units=252
  h=63   units_H<=10 (partial 11)  units_S<=16  starts_H<=601  blocks_H<=9   sessions_for_12_units=756
  h=126  units_H<=5  (partial 6 )  units_S<=8   starts_H<=538  blocks_H<=4   sessions_for_12_units=1512
  h=252  units_H<=2  (partial 3 )  units_S<=4   starts_H<=412  blocks_H<=1   sessions_for_12_units=3024
  h=504  units_H<=1  (partial 2 )  units_S<=2   starts_H<=160  blocks_H<=0   sessions_for_12_units=6048
k=13 constants: Hoeffding c_h=sqrt(2 ln(1/alpha))=4.0496; empirical Bernstein c1=sqrt(2 ln(2/alpha))=4.2173, c2=7 ln(2/alpha)/3=20.7501; normal z_(1-alpha)=3.4554, z_0.8=0.8416
EB variance term, replicates per (sigma/delta)^2 at power 0.8: 25.593 (normal t 18.465, ratio 1.386)
power 0.8 at k=13 by delta (differences in [-1, 1]): Hoeffding units n, its seeds J at |T|=601; EB seed sets J from the range term alone (at most 0.1 x delta)
  delta=0.01  Hoeffding n>=239244  J>=399  EB J>=41502
  delta=0.02  Hoeffding n>=59811  J>=100  EB J>=20752
  delta=0.05  Hoeffding n>=9570  J>=16  EB J>=8302
what a size check shows at n tests (95 %): rule-of-three n; E-052 fails from x rejections; the rate E-052 detects half the time; n for 'no laxity beyond 2 x' with power 0.8
  alpha=5.0000e-02  n=59  E-052 fails at x>=8  detects 2.59 x alpha  no-laxity n=180
  alpha=1.0000e-02  n=299  E-052 fails at x>=8  detects 2.56 x alpha  no-laxity n=1050
  alpha=1.0000e-03  n=2995  E-052 fails at x>=8  detects 2.56 x alpha  no-laxity n=10500
  alpha=2.7473e-04  n=10903  E-052 fails at x>=8  detects 2.56 x alpha  no-laxity n=38220
time leg, independent symmetric blocks: B, P(all B positive), P(strict majority positive)
  B=1   all=5.0000e-01  majority=5.0000e-01
  B=2   all=2.5000e-01  majority=2.5000e-01
  B=3   all=1.2500e-01  majority=5.0000e-01
  B=4   all=6.2500e-02  majority=3.1250e-01
  B=5   all=3.1250e-02  majority=5.0000e-01
  B=6   all=1.5625e-02  majority=3.4375e-01
  B=7   all=7.8125e-03  majority=5.0000e-01
  B=8   all=3.9062e-03  majority=3.6328e-01
  B=9   all=1.9531e-03  majority=5.0000e-01
  B=10  all=9.7656e-04  majority=3.7695e-01
(Y) start-year groups (calendar only), n_Y = all of Y_ok, white-noise overlap (a lower bound): h*, n_min, starts per year, |Y_ok|, smallest correlation, stated size, label
  h*=63   n_min=63   starts [261, 261, 79]  |Y_ok|=3  rho_min=0.0000  size>=0.1356  not vacuous at this bound
  h*=63   n_min=21   starts [261, 261, 79]  |Y_ok|=3  rho_min=0.0000  size>=0.1356  not vacuous at this bound
  h*=63   proposed n_min=21 (the smaller stated size)
  h*=126  n_min=126  starts [261, 261, 16]  |Y_ok|=2  rho_min=0.0959  size>=0.2653  not vacuous at this bound
  h*=126  n_min=21   starts [261, 261, 16]  |Y_ok|=2  rho_min=0.0959  size>=0.2653  not vacuous at this bound
  h*=126  proposed n_min=21 (the smaller stated size)
  h*=252  n_min=252  starts [261, 151]  |Y_ok|=1  rho_min=nan  size>=0.5000  VACUOUS
  h*=252  n_min=21   starts [261, 151]  |Y_ok|=2  rho_min=0.3471  size>=0.3064  not vacuous at this bound
  h*=252  proposed n_min=21 (the smaller stated size)
gate horizon H_g=504: complete held-out starts <= 160, disjoint held-out blocks <= 1, search <= 2
memory: cap 2.5 GB over 2 workers, base 0.4 GB assumed, lane 1344 B: at most 632440 lanes a worker
run plan (trades a session <= 4; 3 finalists + 4 baselines in H7; hours over 2 workers at the assumed costs 0.05 us, 0.5 us, 5.0 us a lane-trade)
  A1 same-design nulls       R=20  arms=3 M=10000  T=120 h=63  lane-trades=1.814e+10  h: 0.1  1.3  12.6
  A2 exact-centred toy null  R=20  arms=2 M=10000  T=120 h=63  lane-trades=1.210e+10  h: 0.1  0.8  8.4
  A3 history null            R=200 arms=2 M=2000   T=120 h=63  lane-trades=2.419e+10  h: 0.2  1.7  16.8
  A4 plants, copy-stagger    R=10  arms=8 M=10000  T=120 h=63  lane-trades=2.419e+10  h: 0.2  1.7  16.8
  D1 same-design nulls       R=20  arms=3 M=2000   T=412 h=252 lane-trades=4.984e+10  h: 0.3  3.5  34.6
  D2 history null            R=200 arms=2 M=500    T=412 h=252 lane-trades=8.306e+10  h: 0.6  5.8  57.7
  D3 power gate plants       R=10  arms=6 M=2000   T=412 h=252 lane-trades=4.984e+10  h: 0.3  3.5  34.6
  D3 full-J check (EB)       R=5   arms=2 M=20752  T=412 h=252 lane-trades=8.618e+10  h: 0.6  6.0  59.8
  H7 held-out, Hoeffding     R=1   arms=7 M=100    T=601 h=63  lane-trades=1.060e+08  h: 0.0  0.0  0.1
  H7 held-out, EB sets       R=1   arms=7 M=20752  T=412 h=252 lane-trades=6.033e+10  h: 0.4  4.2  41.9
```
<!-- three_way_arith: end -->

## Appendix B. The choices the red team should attack (cycle 2)

1. **N-1's admission paragraph** (2.2 (a), between the markers), verbatim for H3's declaration:
   - the admitted dimensions are unconditional means over all of E_h only;
   - the a priori bounds come from contract arithmetic or a pinned per-unit clip only;
   - the build's refusals;
   - c_u through the clip and the caps.
2. **2.2 (b)'s smaller-J rule applied in H3-D** at the pinned delta\*, with H3-A reporting both bounds' J.
3. **1.6's corrected copy-against-stagger rule:**
   - identity at zero stagger through two code paths;
   - a difference non-decreasing in the stagger;
   - the shared-against-independent gap falling to coin noise beyond the longest hold.
4. **The race at the cushion less the exit cost** (1.1), and N-4's deferred items for the template (lattice rounding
   inward, one path per underlying, overlap on the run's exit times).
5. **n_Y = all of Y_ok and the proposed n_min = 21** (3.4), with vacuity at a stated size of one half or more.
6. **Keys:** every word below 2^32, and the guard on `generate_state` (1.5, 2.3).
7. **The fold as a tripwire** and the run-time assertion as the guard (7).
8. **Carried from cycle 1:**
   - `P_B` on the replay's own path (1.2);
   - the clip and the moving estimand (1.3);
   - the gate's held-out quantile over coin seeds only (4.4);
   - coin noise in the limit clause (4.4);
   - S1's stream swap (2.7).
