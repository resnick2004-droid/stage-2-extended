# Red-team diff check: the firm path's last fixes, and the common-path law for rungs (Q-185c, C3-2), 2026-11-22

**Target.** `wt/wt-firmpath` at `c6c3eeb`, `git diff 6b8667f c6c3eeb -- extended/ tests/`, without the master merge
`ba5976c`. The files read are:
- `extended/three_way_rungs.py` (new), `extended/three_way_baseline.py` and `extended/firm_reading.py` (769-773);
- `tests/test_three_way_rungs.py` (new), `tests/test_three_way_baseline.py`, `tests/test_three_way_firm.py` and
  `tests/three_way_baseline_checks.py`.

Line numbers below are the files at `c6c3eeb`.

**Also read, all read-only:**
- vendored: `shared_days.TradeRouter.begin_day` (the strict rule, 330-400), and `lockstep.py` / `sizing.py` for every
  read of `at_need` and `rr_used`;
- vendored: `scripts/user_journey.py` (`build_d518`, `build_p15`, `build_p16`, `build_joint`), `customer_journey.py`
  (P-14's config, 110 and 554), `customer_slices.py` 142, `rc_dev_test.py` 274, 422 and 481, and `rc150_firm_split.py` 293;
- this repository: `three_way_keys.py`, `three_way_fastkeys.raw_outputs`, `three_way_journey.CoinLanes` and `WALK_MAX`
  (57-61), `three_way_redraw.walk_step` / `walk_steps` / `walk_law`, and `reader.CHOICE_END`.

**The brief.** The brief described the construction and asked eight questions, (1) to (7) plus the worker's note. Some
of its wording reads as a conclusion: "claims every level's first touch is therefore exact" and "the law rarely applies
to P-14, P-15 and P-16". I treated both as claims to test, not as findings.

**Method.** Light work only, at `OMP_NUM_THREADS=1` and with `python -B`. The probe scripts are in `scratchpad/fp_c4/`.
- **The clone.** A detached clone at `c6c3eeb` under `%LOCALAPPDATA%\stage2-extended-runs\rt-fp-c6c3eeb`. I ran the
  mutants and the probes there, and removed the clone at the end.
- **The brief's tests.** The rungs, baseline, firm and move files, without the slow tier: all passed (1 skipped), in 389 s.
- **An independent derivation** of the step's extreme law, and an exact computation of the construction's untimed odds
  (`exact_chain.py`: a linear system over the lattice states, in fractions, with no sampling).
- **The joint law** against a Brownian reference that I wrote independently (`joint_probe.py`). The reference puts the
  path on a grid of 0.25 minutes and samples each interval's bridge maximum and minimum once, so that every rung reads
  the same path. I ran it on five pairs of rungs.
- **The timed laws** (`timed_probe.py`). I compared three things: the common path at the alert's step, the rung's own
  exact single-trade law (`walk_law`, `move_law`), and the same Brownian reference with exact time.
- **The strict rule** (`strict_probe.py`): the checks' rung job run with `one_at_a_time = 5.0`.
- **37 mutants** (`mut.py`, `mut2.py`). Each one was written into the clone, run against the unit tests it should fail
  with `-x`, then against the checks' parts named for it (`lite.py` restates the tests' assertions), and the file was
  restored afterwards. **33 were killed and 4 survived.**

Every number below is a probe output on synthetic data, not a result.

---

## 1. Verdict: **BLOCK** (in the house terms, *must be re-declared*: the step rule changes)

**The construction is right where it claims exactness.**
- My derivation of the opposite extreme matches the module's.
- The untimed odds are exactly L/(L+G) in every case I computed, in exact fractions.
- The joint law of two rungs matches Brownian motion on five pairs.
- The 2h refusal is exactly the bound needed.
- The keying is right: one path per (lane, alert), at sub 0, under the WALK role.
- The other fixes (C3-1, C3-3 to C3-10, N-e, N-f) hold, and the tests kill my mutants on them.

**What blocks the merge is time, not space:**
- **C4-1.** The step rule takes h from the alert's longest rung and applies it to every phase. On admitted inputs this
  puts a move rung's marginal law far outside `TIMED_TOL`: off by 0.067 for a fill at 12:55 CT, and by up to 0.20 for a
  fill at 18:58. The only move test that exists uses σ = 1.5, where h = s1 = s2 = 1, so it does not test the step rule
  at all.
- **C4-2.** Whether an alert has rungs is decided from the facts, not from what the router takes. So under the strict
  rule the one rung the router takes is still booked by the common-path law. That is not "as before", and P-14, P-15 and
  P-16 all run under the strict rule.
- **C4-3.** The 2h refusal aborts a run on a realistic state: a moved rung whose target is capped by a small need.
- **C4-4.** The rung oracle follows the module's own law label and reads its logged G and L. Three mutants survive
  because of this, one of them a time-limited move booked as an untimed race.

**Counts:** 0 CHANGES-A-CONCLUSION (no result has been computed on this law yet); 4 MATERIAL; 4 MINOR; 5 NOTE.

### The eight questions, one line each

1. **The mathematics.**
   - The law P(m ≤ b | up) = (b − a)/(c − b) is correct (derived in 2.1).
   - "A step's range is exactly the set of levels touched" holds, because the path is continuous inside a step and
     the step ends at its first hit of x ± h.
   - Untimed odds are exactly L/(L+G) on every one of 9 cases, solved in exact fractions.
   - **The 2h refusal is sufficient and necessary.** A step's range is narrower than 2h, so L + G ≥ 2h keeps a rung's
     two barriers out of one range. Below 2h they can share a range, and their order is then not read.
   - Two different rungs' barriers inside one step's range are read correctly, since each rung reads only its own two.
2. **Simulation.**
   - Marginals: exact. The joint 2×2 tables agree with the Brownian reference on five pairs: |z| ≤ 1.7 on four pairs,
     and 2.0 / 2.5 on the fractional pair, where the reference's own approximation is largest.
   - **`TIMED_TOL` is not held on admitted inputs (C4-1).** The tests cannot fail at 0.02, because their grid leaves out
     the step rule's coarse cases and the move test is degenerate (C4-1, C4-6).
3. **Determinism and keying.**
   - The path is keyed by `alert_key` at sub 0 under `K.WALK`, one per (lane, alert), and recorded to the guard.
   - Lanes differ by the unit's seed index, and alerts differ by moment.
   - No other role's stream is read: K.RACE is unused on a rung, SIDE and MISSED are other roles, and the sub-0 single
     law is never also read for a multi-rung alert. Mutants B1 and B2 are killed.
   - Notes: MISSED is still drawn per sub (N-1). The alert is grouped by the underlying's string, not its key code
     (N-2). The twin path is not the mirror path (N-3).
4. **The step rule.** **Yes, it biases the shorter rungs and phases** (C4-1).
   - A walk with σ 20, T = 20 inside T_max = 1000 is off by 0.022.
   - A move's phase 1 of 2 to 6 minutes, read on an h of 3 to 7 ticks, is off by 0.05 to 0.20, through the lattice's
     parity at the move bar.
5. **The other fixes.**
   - C3-1, C3-3, C3-4, C3-5, C3-8, C3-9 and C3-10 hold, and every mutant aimed at them is killed (section 4).
   - C3-6 holds for the single-trade oracle, but not for the new rung oracle (C4-4).
   - C3-7 holds: the field is gone. N-e holds (`_mode`), and N-f holds (Combine rows rebooked unless at the need).
   - N-d is half done (N-4).
6. **The worker's note.** **Confirmed from the code.**
   - `shared_days.py` 357-359 skips any trade while some account's `open_until + one_at_a_time > t`. Routing the first
     rung sets `open_until` to its exit, which is at or after its entry, so a second rung at the same t is skipped.
     The probe takes at most one trade per alert with the strict rule on, and 168 alerts with two rungs with it off.
   - Every registered baseline runs with the strict rule on:
     - P-14: `customer_journey.py` 554;
     - P-15: `rc_dev_test.py` 274, via `customer_slices.py` 142;
     - P-16: `rc_dev_test.py` 422, where `go(strict=True)` is the default;
     - the joint cells: `rc150_firm_split.py` 293.
   - The only strict-off reading is `rc_dev_test.py` 481 (`unstrict_beside`, "beside the verdict, never deciding").
   - **But the note's "a single-rung alert books exactly as before" does not carry to the strict rule** (C4-2).
7. **No reads.**
   - Nothing in the diff, the tests or my probes reads a bar, the atlas, a held-out date or NQ from 2026-07-17.
   - The P-16 heavy identity now refuses a window past `CHOICE_END` (2023-12-29), but its builder still loads P-16's
     whole table before that check (N-4).

---

## 2. Findings, by severity

### C4-1 (MATERIAL; blocks the merge). The step rule biases time-limited rungs far past `TIMED_TOL`; the move test is degenerate and the walk grid leaves out the coarse cases

**Where:**
- `extended/three_way_baseline.py` 224-225: h = `walk_step(σ, T_max)`, with T_max the longest `limit − entry` of the
  alert;
- 462-463 and 471: every phase's steps are counted on that h;
- `extended/three_way_rungs.py` 41 (`TIMED_TOL`) and 130-132 (the move decision `x >= favour` at lattice step n1);
- the tests: `tests/test_three_way_rungs.py` 80 (`GRID_WALK`) and 96-111 (the move test).

**Evidence, the tests:**
- The move test uses L 40, G 60, σ 1.5, d1 260 and d2 129, so **h = s1 = s2 = 1 tick**. The common lattice is the
  single law's own lattice, and the step rule is never exercised.
- `GRID_WALK` has T / T_max of 0.47, 0.30 and 1.0, so its coarsest case is h 6 against an own step of 4.
- The step rule admits T / T_max down to about 1/1000. A move's phase 1 is short wherever the fill comes just before an
  FV3 open.

**Evidence, the probe** (`timed_probe.py`, 10,000 paths a case; "own" is the exact single-trade law). The shares are
target / stop / breakeven:

| case | h | n1 | own s1, n1 | path | own | Brownian | max \|path − own\| |
|---|---|---|---|---|---|---|---|
| move, fill 1195 (12:55 CT), move bar 1201, limit 1330, σ 6 | 3 | 24 | 1, 216 | .241/.391/.309 | .224/.349/.375 | .229/.349/.370 | **0.067** |
| move, fill 119 (18:59), move bar 121, limit 1330, σ 6 | 7 | 1 | 1, 72 | .224/.330/.446 | .241/.362/.397 | .250/.362/.389 | **0.049** |
| move, fill 118 (18:58), same, σ 6 | 7 | 2 | 1, 108 | .327/.482/.190 | .243/.364/.393 | .235/.366/.400 | **0.202** |
| move, fill 119, σ 3 | 4 | 1 | 1, 18 | .211/.322/.465 | .247/.371/.379 | .246/.368/.383 | **0.086** |
| walk L 80, G 160, σ 20, T 20 within T_max 1000 | 20 | 20 | 3, 889 | — | — | — | **0.022** |
| walk L 40, G 60, σ 6, T 10 / 30 / 100 within 1000 | 6 | 10 / 30 / 100 | | | | | 0.010 / 0.009 / 0.002 |

**The mechanism.**
- The move decision is "x ≥ 1 tick" at lattice step n1. On a lattice of h ticks, x after n1 steps has the parity of n1:
  - with n1 even, P(x = 0) = C(n1, n1/2) / 2^n1 is 0.16 at n1 = 24 and 0.5 at n1 = 2, and a path at 0 is not moved;
  - with n1 odd, x is never 0 and the path is moved half the time.
- So the moved share was 0.40, 0.25 and 0.50 on the path, against 0.47, 0.47 and 0.44 for Brownian motion. Every
  breakeven, stop and target share follows from it.
- The rung's own law reads phase 1 at its own step s1 = 1, and matches the Brownian reference.
- The gross mean stays zero, by optional stopping, so no direction leaks. The shares are what move, and pass and ruin
  are convex in them.

**The failure it allows:**
- A two-rung alert filled at 12:55 CT has its move rungs booked about 7 points short of breakeven exits, and 4 points
  over on stops.
- The same alert filled in the minute before 19:00 is off by up to 20 points.
- Every test is green throughout, and the ruling's "within a tested tolerance" is broken on inputs the build admits.
  Through C4-2, this reaches P-14, P-15 and P-16 on any alert whose schedule carries two trades.

**Remedy** (it changes the declared step rule, so it is a re-declaration of the C3-2 law):
1. **Fix the step rule.** Take h as the smallest own step any rung of the alert needs, over every phase:
   h = min over rungs and phases of `walk_step(σ, d)`, for d = T, d1 and d2. Each phase's lattice is then at least as
   fine as its own single-trade lattice, and the move bar's decision is read at its own resolution.
   - This lets n pass `WALK_MAX` on the long phases. That costs compute only, but it needs C4-7's admission.
   - Alternatively, refuse to share a path when any phase's n is below a declared floor, and say what such an alert
     books instead.
2. **Replace the Monte Carlo tolerance test with an exact one.**
   - The construction's timed law is a finite Markov chain on the lattice, using the extremes' touch probabilities. It
     can be computed exactly, as `walk_law` is (`exact_chain.py` does the untimed case in about 40 lines).
   - Compare it with the own law exactly, on a declared grid that spans what the build admits:
     - σ ∈ {3, 6, 20, 30};
     - fills 1, 2, 5, 30 and 60 minutes before each FV3 open, with the limit at 1330;
     - T / T_max down to 1/100;
     - n1 of both parities.
3. **Optionally, enforce `TIMED_TOL` at run time.** The exact law per (L, G, σ, T, h) is cheap and cacheable. Refuse,
   or count beside, any rung outside it.
4. Re-run this table, and require every cell within `TIMED_TOL`.

### C4-2 (MATERIAL). Under the strict rule the one rung the router takes is booked on the common path, not "as before"; the count beside calls it a multi-rung moment

**Where:**
- `three_way_baseline.py` 215-225: the alerts and `rung_step` are built from the facts, whatever is taken;
- 410-411: every rung of such an alert goes to `_rung`;
- 479-480 and 599: the counts.
- The docstring (73-80) says "the joint law bites only where the strict rule is off".

**Evidence** (`strict_probe.py`, the checks' rung job with `one_at_a_time = 5.0`, 4 lanes):
- The laws booked were `rung_race` 52, `rung_move` 84 and `rung_walk` 32, against `race` 48, `move` 87 and `walk` 32;
- the maximum number of trades taken per (lane, alert) was **1**;
- `rung_trades` 168 = `rung_moments` 168.

So the joint law never bites, but the marginal law changes: the common-path walk and move (C4-1), not the single-trade
R-10 walk and move law. The count beside reports 168 "multi-rung moments" on which one trade was booked.

**The failure it allows:**
- P-14, P-15 and P-16 all run strict (question 6). If their schedules carry two trades at one decision, those trades
  leave the single-trade law and its oracle, and pick up C4-1's bias.
- The count beside reads as if the joint law had applied.

**Remedy:**
- Where the draws' `one_at_a_time` is not None, build no `rung_step`. The router provably takes at most one rung (it
  needs `entry_t`: refuse blocks without it). Book every trade as before, and fail loudly if a second rung of an alert is
  ever booked on a lane.
- Count `rung_moments` only where two or more rungs were booked on the lane.
- Print the number of schedule moments with two or more trades beside P-14's reading. This is a light count once the
  table is read.

### C4-3 (MATERIAL). The 2h refusal aborts a run on a realistic state: a moved rung whose target is capped by a small need (and a rung near the floor)

**Where:** `three_way_rungs.py` 101-105, 110, 117, 126 and **134** (`check_step(path.h, G)` once moved), reached from
`three_way_baseline.py` 410-411 inside the engine's draw call.

**Evidence:**
- `walk_step(30, 400) = 19` ticks. NQ's σ is of the order of 30 ticks a √minute, over a 400-minute session.
- With a need-capped G of 20 ticks and L of 100, **25 of 200 moved paths raise** "REFUSED: the common path's step 19.0
  ticks is more than half a rung's barrier distance [20.0]".
- G = (need + e + x_t)/d falls under 2h = 38 ticks whenever the need is under about $190 at $5 a tick. That is the
  Combine's last trades, the very rows C3-5's checks count.
- Near the floor, L = (room − e − x_s)/d can be small too, and L + G < 2h refuses the race itself.
- The single-trade law never refuses on its step (`walk_step`'s docstring: "a trade is never refused because of its
  step").

**The failure it allows:**
- A heavy rule-off run (the design mode) dies mid-run on the first such state.
- Under the strict rule, so does P-14's reading, through C4-2.
- No wrong number is produced, but the law is unusable on the states that matter most for passing.

**Remedy:**
- **(a)** Resolve the shared-step case exactly. Given an up step from x whose minimum m ≤ lo, with hi in (x, c), the
  order of the two touches has a closed-form conditional law. Draw it from a further uniform of the same stream, at a
  declared offset.
- **(b)** Or book that rung on its own single-trade law, counted and labelled beside ("rung off the common path").
- In either case, add a test with a need-capped G < 2h on a moved rung, and with L + G < 2h.

### C4-4 (MATERIAL). The rung oracle is not independent: it dispatches on the module's law label and books with the module's logged G and L

**Where:** `tests/three_way_baseline_checks.py` 405 (`G, Lt = float(r["G"]), float(r["L_ticks"])`) and 406-426 (the
branches on `r["law"]`). Compare the single-trade oracle, which derives `has_move`, the kind, G, L and the need from the
facts and the engine's ledger (C3-6's fix).

**Evidence** (mutants, both the unit tests and the rung checks green):
- **B6** `if f.has_move and kind != "t":` in `_rung`: a **time-limited move rung of kind t is booked as an untimed
  race**. SURVIVED.
- **B5** `elif kind == "t":` in `_rung`: an s-kind rung is walked to its limit instead of raced. SURVIVED.
- **B10**: every rung's G and L scaled by 0.8 before both the log and the booking. SURVIVED (656 rows, 0 bad).

The rung test's other assertion, that every rung law is reached, is met by the remaining trades.

**The failure it allows:** a rung booked under the wrong law (for example, with no time limit), or at the wrong
barriers, passes every check while the engine books it.

**Remedy:** the rung oracle derives the following itself, then requires B5, B6 and B10 killed:
- the law, from `f.be_open`, `f.entry`, `f.limit` and `f.kinds[t["rr"]]`;
- G, from its own `_target(t["rr"], stop)` and the need cap from `t["need"]`;
- L, from `t["room"]` and its own costs, as `oracle()` already does.

### C4-5 (MINOR). The timed walk's clock off by one step is not defended

**Where:** `three_way_rungs.py` 82 (`while stop is None or k < stop`).

**Evidence:**
- Mutant **G10** `k <= stop` reads one step past the limit, so a barrier touched at step n + 1 counts. It SURVIVED the
  rung unit tests and the rung checks. The checks' own touch loop is the same code.
- At n ≥ 100 the tolerance test cannot see one step. At the n1 = 1 to 2 of C4-1 it is half the phase.

**Remedy:** a scripted-uniform unit test, with a `read()` that returns chosen uniforms: a barrier reached exactly at step
n books the barrier, and one reached at step n + 1 books TIME at x[n]. The same test for the move's two phases.

### C4-6 (MINOR). The tolerance tests' power

**Where:** `tests/test_three_way_rungs.py` 84-111.

**Evidence:**
- Each test asserts |share − own| < 0.02 at N = 20,000, so SE ≤ 0.0035.
- A true deviation of 0.022 passes with probability of about 0.28, and one of 0.025 with about 0.08. The test does not
  certify "within 0.02".
- With three walk cells and one degenerate move cell, it samples almost none of the admitted space.

**Remedy:** the exact computation in C4-1 remedy 2, which has no sampling noise. Failing that, assert
|share − own| + 3·SE < `TIMED_TOL` on the declared grid.

### C4-7 (MINOR). The common path reads past the generator's admitted range

**Where:**
- `three_way_rungs.py` 60: two uniforms a step, read ahead in chunks of 128, with no bound for an untimed race;
- `three_way_journey.py` 57-61: `WALK_MAX` is "the longest walk a trade may read: `test_three_way_fastkeys` admits the
  vectorised generator on every output up to it; a longer walk is refused (rn-2)".

**Evidence:**
- A timed rung at n = 1024 reads about 2,176 outputs, and an untimed race reads until it is absorbed.
- `raw_outputs` is counter-based, so this is very likely sound. The checks' oracle compares the stream on 200,000
  outputs of numpy's own Philox and agrees on 671 rows.
- But the rn-2 admission, as written, does not cover it, and C4-1's remedy pushes n higher.

**Remedy:** extend `test_three_way_fastkeys.test_every_output_a_walk_reads` to ranges with `first` up to 2^17 or more.
Restate rn-2 for the common path, or cap a path's length with a declared refusal.

### C4-8 (MINOR). The paths are never freed

**Where:**
- `three_way_baseline.py` 226 and 262: `unit.paths[(lane, alert)]` holds three Python lists a step;
- `simulate` (585-600) runs the lanes one after another on one `_Unit`.

**Evidence:**
- About 100 bytes a step, times up to about 1,100 steps, is roughly 100 KB per (lane, alert), kept for the whole call.
- 1,000 lanes × 1,000 multi-rung alerts would need about 100 GB. The machine has 16 GB.

**The failure it allows:** a heavy rule-off run exhausts memory (CLAUDE.md: memory decides concurrency).

**Remedy:** drop `unit.paths` entries for lane j when its replay returns, or clear them at each session. Add a test that
`unit.paths` is empty after `simulate`.

---

## 3. Notes

- **N-1. MISSED is drawn per sub.** `three_way_baseline.py` 394 keys `K.MISSED` at the sub's moment, so a user can miss
  rung 0 of an alert and take rung 1. One alert is one signal. Key MISSED at `alert_key` when an alert has rungs, or
  label it.
- **N-2. The alert's grouping and origin.**
  - The alert is grouped by the underlying's string (215). `K.UNDERLYING` maps NQ and MNQ to one code, so an NQ and an
    MNQ trade at one decision are two "alerts" with independent laws on one market. Group by the key code instead.
  - Rungs are not checked to share their entry. The path starts every rung at its origin, so a rung that fills at a
    later bar would read the wrong segment. Refuse an alert whose rungs' `entry` differ.
  - State that the rungs share one fill price.
- **N-3. The twin path is not the mirror path.** Under `arm.twin` every uniform becomes 1 − u. The directions flip, but
  the extremes use 1 − v, while the mirror of the path needs the same v: the mirrored up-step minimum is −M(v). The
  marginals stay exact and no bias follows. But if any reading takes the twin as "the reflected path", it is not one.
  Either read the extreme's uniform untwinned, or state this.
- **N-4. N-d is half done.** `three_way_baseline_checks.py` 497-501 (`late = ...` at 498) refuses a P-16 window that reaches past
  `CHOICE_END`, but `UJ.BUILDERS["p16"]` has already loaded P-16's dev and test table by then. Record that this load is
  within the reader's authorisation, or build only the search years.
- **N-5. The ruling covers one alert.** Overlapping positions from different alerts (rule off) still read independent
  paths, though their windows share market time. Label this beside any rule-off reading.

---

## 4. What I tried that found nothing

- **The extreme's law, derived independently.**
  - Stop driftless Brownian motion at its first exit from (x − h, x + h).
  - P(m > b and the exit at c) = P_x(c before b) = (x − b)/(c − b). Dividing by 1/2 gives P(m ≤ b | up) =
    (b − a)/(c − b) on (a, x], so m = (a + uc)/(1 + u). The down step mirrors this.
  - Direction and extreme are independent across steps by the strong Markov property.
  - All of this matches `three_way_rungs.py` 62-71.
- **The odds, exactly.** `exact_chain.py` found P(target) = L/(L+G) as an exact fraction for these 9 cases:

  | L | G | h |
  |---|---|---|
  | 13.7 | 41.3 | 4 |
  | 29.1 | 17.9 | 4 |
  | 37.3 | 61 | 7 |
  | 12.5 | 80 | 3 |
  | 21 | 37.5 | 10 |
  | 4 | 4 | 4 |
  | 4.5 | 3.5 | 4 |
  | 50 | 100 | 5 |
  | 1 | 99 | 50 |

  The last three sit at L + G = 2h exactly. Large-N sampling (40,000 paths) agreed within 2 SE.
- **The joint law against Brownian motion** (`joint_probe.py`, 10,000 paths, each pair's 2×2 table):
  - nested (50, 100) / (100, 200);
  - asymmetric (20, 60) / (60, 20);
  - crossing (30, 30) / (10, 80);
  - shared stop (40, 40) / (40, 120): the impossible cell is exactly 0 on the path;
  - fractional (13.7, 41.3) / (29.1, 17.9).

  My first reference drew each rung's bridge crossing apart, which showed a false 0.0017 in the impossible cell. The
  shared-extremes reference removed it.
- **The untimed rung on the draw.** It uses no time, so C4-1 does not touch it. `rung_race` is exact.
- **Zero mean.** Every rung law books Brownian motion at a bounded stopping time, so the gross mean is exactly zero.
- **Keying.**
  - The path is one per (lane, alert), at sub 0, under `K.WALK`, recorded to the guard.
  - Independence across lanes and alerts holds by the key.
  - The as-walked side is keyed at sub 0.
  - Mutants B1 (sub 1), B2 (one path for every lane), B3 (the step from the shortest rung), B7 (the side at the sub)
    and B9 (every alert on a path) are all killed.
- **The other fixes, by mutant (all killed):**
  - C3-1: G and the kind at `rr_used` (now killed by the unit test and by the engine fixture with `rr_differs` 24);
  - C3-3: `rr_used` kept; `at_need` kept; the reading's refusal dropped;
  - C3-4: a need ≤ 0 caps;
  - C3-5: `need_hit` false on the move; on the walk; the need-exits statistic dropped;
  - C3-6: the need halved; the room shifted (now caught by the oracle's own take from the ledger);
  - C3-8: logged L from the stop; logged G shifted;
  - C3-9: `by_component` admitted;
  - C3-10: the move bar unenforced; FV3_OPENS shifted (unit test and the vendored `SESSION_OPENS`); `be_unrecorded`
    zeroed.
- **The construction, by mutant (all killed):**
  - the up minimum uniform, and the down maximum uniform;
  - the direction read from the extreme's uniform;
  - the chunks overlapping, so that uniforms are reused;
  - the refusal at h;
  - the walk's exit one step early;
  - the favour strict;
  - phase 2 one step short;
  - no breakeven;
  - the rung walk's time + 40;
  - the breakeven at the flatten's cost.
- **The engine's reads of `at_need` and `rr_used`.** Only `lockstep.py` 468 reads `at_need` (`exit_kind`), and nothing
  reads `rr_used`. Setting both on a race row changes no routing.

## 5. What I could not check

- **How many P-14, P-15 and P-16 schedule moments carry two or more trades**, which is C4-2's real size. This is a light
  count once their tables are read, which is heavy and the lead's.
- **σ and the brackets on real alerts**, which set where C4-1 and C4-3 bite. I used σ of 3, 6, 20 and 30 ticks a √minute
  as stand-ins.
- **The exact conditional order of two touches inside one step** (C4-3 remedy a): specified, not derived here.
- **The heavy P-16 identity** (N-4): the lead's, not run.
