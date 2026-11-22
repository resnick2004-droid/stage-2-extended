# Red-team diff check: the firm path's baseline mode after corrective cycle 1 and the lead's amendments (Q-185c), 2026-11-22

**Target.** `wt/wt-firmpath`, `git diff fa73745 6b8667f -- extended/ tests/ identity/`, restricted to the firm path's
own two commits:
- `a15ed03`, cycle 1's fixes to BUILD_FIRMPATH_c2;
- `6b8667f`, the lead's amendments.

The commit `82e2c98` merged master, and I skipped master's files. The files read are:
- `extended/three_way_baseline.py`, `extended/three_way_move.py`, `extended/three_way_firm.py` (the design mode's
  router change) and `extended/firm_reading.py` (769-772);
- `tests/test_three_way_baseline.py`, `tests/test_three_way_move.py` and `tests/three_way_baseline_checks.py`.

Line numbers below are the files at `6b8667f`.

**Also read, all read-only:**
- vendored: `sizing.TierSizedDraw` (`_need_exit` 551-575, `__call__` 712-825, `can_take` 490-509);
- vendored: `lockstep.py` (`need_to_pass` 408-419, `trade_day` 432-500, `_ledger_row` 276-291, `_count_max` 254);
- vendored: `shared_days.TradeRouter.begin_day` (242-400) and `fv3_rung_walk.py` (100-200);
- vendored: `score_fv3_grid.sizing_rule` and `scripts/user_journey.build_p16` / `_single_jobs`;
- this repository: `extended/router.py` (`Routing`, `route`), `three_way_keys.moment`, `three_way_journey.CoinLanes`,
  and `three_way_redraw.walk_step` / `walk_steps`.

**The brief.** The brief listed the lead's rulings and the points to attack. I checked the code against each ruling, and
I also attacked one ruling on its merits (C3-2). I took no conclusion from the brief.

**Method.** Light work only, at `OMP_NUM_THREADS=1` and `PYTHONDONTWRITEBYTECODE=1`. The probe scripts are in
`scratchpad/fp_c3/`.
- **The brief's tests.** I ran them in a detached clone at `6b8667f` under
  `%LOCALAPPDATA%\stage2-extended-runs\rt-firmpath-6b8667f`, and removed the clone at the end. Result: **43 passed,
  3 deselected, 127 s**.
- **The checks run directly** (the clone at `6b8667f`):
  - identity: 0 differences, 10 passes, 10 funded accounts;
  - rebooked: 73 rows compared, 0 bad;
  - as_walked: 692 rows, 0 bad;
  - race: 1,385 rows, 0 bad, with laws race 370, move 736, walk 276 and fill_fail 3;
  - dll: 90 day ends, 0 later trades.
- **31 one-line mutants** (`mut.py`, `mut2.py`), each written into the clone, run against the three test files with
  `-x`, and the file restored after each. **25 were killed and 6 survived.**
- **Probes.** I ran them against the worktree read-only, with `python -B`; its `git status` was empty before and after.
  - `need_probe.py`: the need-aware race at its edges, on a stub draw.
  - `ledger_probe.py`: the engine job's race-arm ledger.
  - `rungs.py`: two brackets on one driftless path, against two independent races.

These numbers are probe outputs, not results.

---

## 1. Verdict: **PASS WITH MINORS** (in the house terms, *stands with readings*)

**The code follows every ruling.** I found no look-ahead, no wrong number and no leak of a held-out date in what the
build computes now:
- R is read at `lt["rr"]`;
- the fee is the engine's at size;
- one time-limited move law applies to every trade with a move bar before its limit;
- `be_open` is `s + 1` on the bar-end clock;
- trades at one moment are keyed by (moment, sub);
- the missed-signal hold is labelled;
- `as_walked` is the reflected path, and the costs identity is named `rebooked`;
- the move law's inputs are logged.

**The pass-through identity holds bit for bit**, now through passes and funded accounts. **The oracle is independent in
the parts that matter:** its own walker, its own fee, its own steps, and the scalar key path.

**Two MATERIAL items:**
- **C3-1 must be fixed before the merge.** The ruling "never `rr_used`" is not defended by any test: two mutants that
  read `rr_used` survive.
- **C3-2 is a reading the lead must label.** Independent draws for two rungs of one alert are not the joint law of one
  market path. In `as_walked` they also reflect the two rungs to opposite sides.

Neither item changes a number the build produces today. The rest are minors and notes.

**Counts:** 0 CHANGES-A-CONCLUSION; 2 MATERIAL; 8 MINOR; 6 NOTE.

### The nine questions, one line each

1. **Look-ahead.**
   - In race mode, no exit, move or fee reads a bar after the alert, or reads `rr_used` or the historical exit.
   - The race reads these fields of the engine's report: `rr`, `fee`, `contracts`, `realised_risk`, `need`,
     `risk_per_contract`, and the day and index. It also reads the fill-time facts.
   - The only historical field read is `kinds`, and only for trades without a move. That is labelled at 38 (R-10's law).
   - N-6's scramble test is real. My two clock mutants (reading the next bar; skipping the alert's bar) are both killed.
   - But the ledger still carries historical `at_need`, `exit_kind` and `rr_used` (C3-3).
2. **Pass-through.**
   - The vendored arm returns the vendored array before any other code runs.
   - Routing and `can_take` go to the inner draw, which registered itself with the router.
   - The race touches no engine RNG. Its `_uncount` changes reporting statistics only, and nothing in the engine routes
     on them.
   - Identity: 0 differences.
3. **The oracle.** It is independent for the law: its own `walk_scalar`, `_step`/`_steps` and `_fee`, the scalar key path,
   and R and contracts from the engine's ledger. But it takes `need`, `room` and `law` from the module's own log, and
   `target_ticks`, `has_move` and `f.sub` from the module (C3-6).
4. **Need edges.**
   - A win nets the need exactly (12.345678 → 12.345678).
   - G is capped only when (need + e + x_t)/d < G.
   - **need ≤ 0 is not refused:** it gives G ≤ 0 and p ≥ 1, a certain booking at the need (C3-4). The engine never
     passes such a need.
5. **The move at its boundaries.**
   - A move bar at the limit is no move, and a historical `b` there is refused. Mutant killed.
   - The phases-past-`WALK_MAX` guard cannot be reached, because `walk_step` bounds each phase. n1 + n2 ≤ 2·`WALK_MAX`
     on one Philox stream is sound (N-a).
6. **Sub keying.**
   - Subs follow the schedule's index order, deterministically, and give independent streams. Three mutants killed.
   - Whether independence is the right law for rungs of one alert is a reading (C3-2).
   - `TradeFacts.sub` is dead (C3-7).
7. **Mutation.** 25 of 31 killed. The survivors are:
   - `rr_used` for G, and for the kind (C3-1);
   - `need_hit` on move/walk, and the need-exit statistic (C3-5);
   - the logged `L_ticks` (C3-8);
   - `by_component` admitted by the plan (C3-9).
8. **The design mode.** `Routing(rotation, firm="topstep")`, one route call per session label. `by_component` is refused
   twice: by `AccountPlan` and again by `Routing` without a `Design`. Neither refusal is tested (C3-9).
9. **Data reads.**
   - The baseline mode reads no bar.
   - `simulate` calls `TF.check_dates`, which admits only search-year dates, or undated synthetic runs under a synthetic
     seed.
   - `TB.replay` has no date guard, and the heavy P-16 identity builds P-16's whole job (N-d).
   - Nothing reads NQ from 2026-07-17.

---

## 2. Findings, by severity

### C3-1 (MATERIAL; fix before the merge). No test defends "never `rr_used`": the race at `rr_used` survives, for the target and for the dispatch

**Where:**
- `extended/three_way_baseline.py` 293-298 (`R = lt.get("rr")`, `kind = f.kinds.get(R)`) and 314
  (`G = float(target_ticks(R, ...))`);
- the tests: `tests/test_three_way_baseline.py` 145-154 and `tests/three_way_baseline_checks.py` 131 (`combine_rr=1.5`).

**Evidence:**
- **Mutant `R1-G-at-rr_used`:** `G = float(target_ticks(float(lt.get("rr_used") or R), f.stop_ticks))`. It
  **SURVIVED** (23 passed).
- **Mutant `R1-kind-at-rr_used`:** `kind = f.kinds.get(float(lt.get("rr_used") or R))`. It **SURVIVED**.
- **Why the engine job cannot see them.** `ledger_probe.py` counts `rr_used != rr` on **0 of 1,385** race-arm rows.
  - The need-aware exit only walks the carried Rs from need/risk up to the state's R (`sizing.py` 562).
  - The Combine's R is 1.5, the table's lowest, so `rr_used` is always 1.5.
  - The funded draws get no need (lockstep passes `need=` only at 465).
- **Why the unit test cannot see them.**
  - In 145-154 the need of $12 caps G at 24 ticks, below both Rs' targets, so G at `rr_used` gives the same race.
  - The kinds `{1.5: "s", 2.0: "t"}` are both raced, so the kind at `rr_used` gives the same law.
  - Only the `race_R` assertion bites, and both mutants leave `race_R` at `lt["rr"]`.
- C2-1's remedy asked for "a mutant that reads `rr_used` on that path, and require it to be killed". These are that
  mutant.

**The failure it allows:**
- On P-14 or P-16, a regression to `rr_used` would ship with every test green. Their tables carry Rs below the state's,
  so the need-aware walk can pick a lower R.
- That is a race at an R chosen from the trade's historical net outcomes, C2-1's look-ahead, with the dispatch (race
  against walk) also chosen by it.

**Remedy (light, synthetic):**
1. **A unit test with a need that does not bind:** `need=100`, `rr=2.0`, `rr_used=1.5`, and kinds `{1.5: "f", 2.0: "t"}`.
   Assert `G == 80`, the law `race`, and p = 1/3. `need_probe.py` confirms the build gives G 80 and p 1/3.
2. **An engine fixture where `rr_used` differs from `rr`:** `combine_rr=2.0` on the 1.5/2.0 table, with kinds that
   differ in law between the two Rs on some trades. Assert that `rr_used != rr` on more than 0 rows and that the oracle
   still agrees.
3. Re-run the two mutants and require both killed.

### C3-2 (MATERIAL; a reading for the lead to rule and label). Rungs of one alert draw independent outcomes, but on one market path they are not independent; and `as_walked` reflects them to opposite sides

**Where:**
- `three_way_baseline.py` 181-190 and 205 (sub keying; the lead's amendment to C2-9);
- 327 (`as_walked`'s side, from `K.SIDE` at the sub's moment).

**Evidence:**
- **The race.** Each sub has its own RACE and WALK streams. So two brackets from one alert and one fill become two
  independent races. Each one's marginal law is right and has zero mean, but their joint law is not one path's.
- **The size** (`rungs.py`, a driftless ±5-tick walk, 20,000 paths, all absorbed; brackets (L, G) = (50, 100) and
  (100, 200) ticks):

| | P(both stopped) | sd of the summed ticks |
|---|---|---|
| one common path | **0.560** | **186.5** |
| independent (the build) | 0.449 | 158.1 |

  So the build understates the day's spread by about 15 % here. Correlation on the common path is 0.50.
- **`as_walked`.** The SIDE coin is drawn per sub, so the two rungs of one alert are reflected independently. On about
  half the units the user holds the rung-0 reflection long and the rung-1 reflection short at the same moment.
  - That is a hedged pair: tier 1, against E-221's "no two of the user's accounts hold opposite positions at once".
  - It is also not a reflection of the path, since a reflection flips the whole path.
  - The synthetic job has no two trades at one moment, and its check keys sub 0 (`three_way_baseline_checks.py` 180), so
    the checks never meet this case.

**The failure it allows:**
- P-14's journey is read under a joint law with less spread than one market gives its rungs. The pass, ruin and payout
  shares move through the rules' convexity.
- P-14 sets the limits (`user_journey.py` 88: "the limits' is P-14"). No direction leaks, but the limits move.
- The `as_walked` reading beside the verdict contains positions that conduct forbids.

**Remedy:**
- **(a) The lead keeps independence, labelled.** Print beside P-14's verdict:
  - the count of moments with two or more subs;
  - their share of trades;
  - the words "rungs of one alert drawn independently".
- **(b) Or the common-path law** for the subs of one moment:
  - one WALK stream keyed at sub 0;
  - each rung's barriers read off the same lattice path;
  - the race laws replaced by the walk to each rung's limit.

  It is zero-mean by the same optional stopping, and it is what the design mode would need if it ever admits two trades
  at one moment.
- **For `as_walked` in either case:** key `K.SIDE` at `K.moment(i, decision, 0)`, so there is one side per alert, and add
  a test with two subs that asserts one side.

### C3-3 (MINOR). The race-arm ledger keeps the history's `at_need`, `rr_used` and the engine's `exit_kind` derived from it; the log keeps the vendored P&L

**Where:**
- `three_way_baseline.py` 271-273 sets only `u` and `mae` to None;
- `lockstep.py` 468 does `last["exit_kind"] = exit_kind if last.get("at_need") else None` after the draw returns;
- `firm_reading.py` 769-772 checks only `u` and `mae`;
- `three_way_baseline.py` 318 puts `"vendored": vend` into every race-arm log row.

**Evidence** (`ledger_probe.py`, 12 lanes, start 3):
- on **13** race-arm rows `at_need` (historical) differs from `race_need`;
- on the same **13** rows `exit_kind` ("pass" / "consistency") disagrees with the race;
- `rr_used` is present on all 1,385 rows.

**The failure it allows:** a reader of H4's per-trade log who counts need exits, or takes the R from `rr_used`, reads
the history on a race-arm ledger. C2-7's remedy covered this class of field, but only two of its members were fixed.

**Remedy:**
- On a replaced trade, set `lt["at_need"] = info["need_hit"]` before returning. The engine then writes the race's
  `exit_kind`, and nothing else in the engine reads `at_need`.
- Set `lt["rr_used"] = None`.
- Have `firm_reading.trade_problems` refuse a race row whose `rr_used` is set or whose `at_need` differs from
  `race_need`.
- In race mode, log the vendored P&L under a name that says so (`hist_pnl`), or drop it.

### C3-4 (MINOR). A need at or below zero is raced as a capped target of G ≤ 0 (p ≥ 1); the engine treats it as no need

**Where:** `three_way_baseline.py` 313-317.

**Evidence** (`need_probe.py`, zero costs, stop $20):

| need | G (ticks) | p | every lane books |
|---|---|---|---|
| 0 | 0 | 1.0 | 0 |
| −0.5 | −1 | 1.026 | −0.5 |
| −5 | −10 | 1.333 | −5 |

- A gross of −1 or −10 ticks for certain is not zero-mean.
- The engine's `_need_exit` returns the plain trade at `need <= 0` (`sizing.py` 555). Lockstep never passes such a need
  (465: `need_to_pass` > EPS; the allowance > EPS).

**The failure it allows:** none on the engine path today. A future caller, such as the design mode's port or a stretch
path, would book certain losses with no error.

**Remedy:** match the engine. Use `capped = need is not None and np.isfinite(need) and need > EPS and ...`, or refuse a
need ≤ EPS. Add the two probe cases as a test.

### C3-5 (MINOR). The need hit on the move and walk laws, and the draw's `need_exits` statistic, are untested

**Where:** `three_way_baseline.py` 270 (`stats.need_exits += ...`) and 365, 385 (`need_hit=...`).

**Evidence:**
- **Mutant `R1-need-hit-move-false`** (`need_hit=False` on the move law): **SURVIVED**.
- **Mutant `R1-need-exits-stat-dropped`** (the statistic's line removed): **SURVIVED**.
- The checks compare only `sizing["trades"]` (284).

**The failure it allows:** the sizing record's `need_exits`, and the `race_need` flag (C3-3's remedy would build on it),
could be wrong and go unseen.

**Remedy:** in `race()`, assert each account's `sizing["need_exits"]` equals its rows with `race_need`. Assert
`race_need` against the oracle's own "target hit with G capped". The probe counts 34 capped rows and 20 hits, so the
check has rows to bite on.

### C3-6 (MINOR). The oracle takes the need, the room and the fill-failure label from the module's own log, and three helpers from the module

**Where:** `tests/three_way_baseline_checks.py`:
- 228 `need = r.get("need")`; 231 `room = r["room"]`; 233 `r["law"] == "fill_fail"`;
- 227 `TB.target_ticks`; 237 `f.has_move`; 236 `f.sub`;
- the as-walked check reads `r["fee"]` and `r["d"]` from the log (183) and keys sub 0 (180).

**Evidence:**
- A wrong value that the module both uses and logs agrees with the oracle.
- My halved-need mutant was killed only by the unit test, not by the oracle. My shifted-room mutant was killed by the
  separate fill-failure check against the engine's P&L.
- `target_ticks` and `has_move` are pinned by their own unit tests (mutants killed).

**The failure it allows:** a mutation of the need or the room handed to the law, made consistently in use and in log,
passes the oracle. It then rests on one unit fixture.

**Remedy:**
- Take `need` and `room` from the engine's ledger row (`t["need"]`, `t["room"]`, the vendored draw's own report).
- Derive fill-failure versus day-end from the oracle's own take and the engine's floor room.
- Compute subs by the oracle's own count.
- In the as-walked check, take the fee from `_fee(t["contracts"])` and d from `t["realised_risk"]`.

### C3-7 (MINOR). `TradeFacts.sub` is dead: the module ignores it, and the oracle reads it

**Where:** `three_way_baseline.py` 119 (the field), 205 (`self.subs[...]` used instead); the oracle at 236.

**The failure it allows:** a schedule builder that sets `sub` believes it keys the coin. The module silently keys its own
sub, and the oracle keys the builder's, so the two disagree only on jobs with two trades at one moment. The synthetic job
has none.

**Remedy:** delete the field, or refuse a fact whose `sub` differs from the unit's computed one.

### C3-8 (MINOR). Of the move law's logged inputs, the oracle checks the steps, x, G' and the floor side's distance, but not L or G

**Where:**
- `three_way_baseline.py` 361-362 (`L_ticks`) and 318 (`G`);
- the oracle at 244-251.

**Evidence:** mutant `R8-logged-L-from-stop` (`L_ticks=float(f.stop_ticks)`) **SURVIVED**. The ruling asks that the
inputs be logged *and* that the oracle check each one.

**The failure it allows:** an auditor replaying a trade from its log reads a wrong L or G.

**Remedy:** the oracle asserts `r["L_ticks"] == float(Lt)` and `r["G"] == float(G)` within 1e-9.

### C3-9 (MINOR). The design mode's `by_component` refusal is untested

**Where:** `extended/three_way_firm.py` 190-191; `tests/test_three_way_firm.py` (no `by_component` case).

**Evidence:**
- Mutant `D-by_component-admitted` (the plan's refusal removed) **SURVIVED**.
- The plan is still refused downstream. A probe shows `RT.Routing("by_component", firm="topstep")` raises "deals over
  the Design's components" at `Lane` construction. `round_robin` and `longest_waiting` are admitted by both.

**The failure it allows:** none today, because there are two refusals. A later change to either one loses the other's
test.

**Remedy:** assert that `TF.AccountPlan(rotation="by_component")` raises `RoutingRefused`, and that a `round_robin` plan
routes through `Routing(..., firm="topstep")`.

### C3-10 (MINOR). The ruling `be_open = s + 1` is documented, not enforced

**Where:** `three_way_baseline.py` 111, 130 and 141. `TradeFacts` accepts any `be_open > entry`. Only the test fixture
computes `s + 1` (`three_way_baseline_checks.py` 98-99).

**The failure it allows:**
- A builder that passes the vendored `jn` (the first *recorded* bar within five minutes) as `be_open` passes every check.
- That brings back N-1's read of bar presence after the fill, and `be_differs` would count 0.

**Remedy:**
- Compute `be_open` in the module from `entry` and FV3's `SESSION_OPENS` (`fv3_rung_walk.py` 53, imported read-only), or
  refuse a `be_open` that is not `next(s > entry) + 1`.
- Count beside, separately, `has_move and be_vendored is None`: a vendored day with no recorded bar within five minutes,
  where the vendored walk had no move at all. Line 414 counts only `be_vendored is not None and != be_open`, so those
  trades are missed.

---

## 3. Notes

- **N-a. Phases past `WALK_MAX`.**
  - `walk_step` makes n = round(σ²T/s²) ≤ `WALK_MAX` for every T, so the guard at 356 cannot be reached. A mutant on it
    would be equivalent.
  - Phase 2 reads uniforms n1 .. n1 + n2 − 1 of the same Philox stream, which is up to 2·`WALK_MAX` draws. One key's
    stream has no aliasing, so this is sound.
- **N-b. Non-move trades still dispatch on the historical kind** (t/s race, f walk; 38). This is labelled, it is R-10's
  law as in the design mode, and it has zero mean given the kind. It remains a post-alert key (C2-4's reading, carried).
- **N-c. "Never refused" holds up to `MOMENT_SUBS = 16`** trades at one moment (189). The 17th is refused, which is a
  key-space limit. P-14's rungs per alert are far fewer.
- **N-d. Dates.**
  - `TB.replay` has no date check of its own. `simulate`'s `TF.check_dates` covers the race arm.
  - The heavy P-16 identity (`three_way_baseline_checks.py` 350-367; the lead's) builds P-16's whole job through
    `user_journey.build_p16`, dev and test, and replays starts 0, 100 and 250 for 126 sessions on both arms.
  - Before it runs, assert that each window's dates (`job["dates"][s:s + h]`) are at or before `reader.CHOICE_END`. Or
    record that loading P-16's table is within the reader's authorisation.
- **N-e. `RaceOver._outcome`** (227) shadows `TierSizedDraw._outcome` through the wrapper. This is harmless now: the
  router registered the inner draw, and nothing calls `_outcome` through the wrapper. Rename it (`_mode`) so that a future
  router hook cannot get a string back.
- **N-f. `rebooked` compares only funded trades.**
  - It skips every row with a need (`three_way_baseline_checks.py` 197). Under the consistency cap, that is every
    Combine trade.
  - So the fee-at-size identity is verified on funded trades by `rebooked`, and on Combine trades only through the race
    oracle's independent `_fee`.
  - Compare Combine rows too where `at_need` is false.

---

## 4. What I tried that found nothing

- **Each ruling, by mutant (killed):**
  - the need dropped;
  - the cap's costs dropped from the test, and from the value;
  - the fee linear in micros, or dropped;
  - the move law applied only to historical `b`;
  - phase 1's step from T;
  - phase 2's time from the fill;
  - phase 2 not bounded by the limit;
  - a breakeven exit charged the target's cost;
  - `be_open` read as the open (−1 minute);
  - a move bar at the limit admitted;
  - sub always 0, taken from the facts, or dropped from the cache;
  - `as_walked` unreflected, at the target's cost, or on the RACE uniform;
  - the logged x shifted;
  - the room shifted;
  - every lane's walk on lane 0;
  - the take at the fill without the flatten's cost;
  - σ reading the next bar, or skipping the alert's bar;
  - the need halved.
- **The pass-through.**
  - The vendored arm returns before any state is touched.
  - `begin_session` and the attributes delegate.
  - The router's `can_take` and `trade_dollars` reach the inner draw.
  - The engine routes on no statistic that `_uncount` changes.
  - The identity reaches 10 passes and 10 funded accounts.
- **Need edges.**
  - A win nets the need to float precision with costs (12.345678).
  - A need tiny but positive gives a near-certain win of the need, as a limit order there would.
  - A need beyond the target leaves G at FV3's target at `lt["rr"]`.
- **Look-ahead in the fee.** `lt["fee"]` is `fee_dollars(contracts)`. The contracts come from the allowance at the
  session's start and the room before the trade (`sizing.py` 794-819), with no outcome.
- **The `be_open` clock.** FV3's entry price is `o[je]`, and its move test is `o[jn]`. So `be_open − entry` = jn − je is
  the time between the two opens, and N-1's reading is right.
- **The design mode's router.** `FIRM = "topstep"` is used throughout the schedule, the day schedule and the routing.
  There is one `route` call per session label, and a second call for a label is refused.

## 5. What I could not check

- **The schedule builder** (not built): its `kinds`, `limit`, σ's `lookback` (an unlabelled parameter, to be classed),
  and the bar-end conversion. It must pass end index = open stamp + 1 to `alert_sigma`, or it reads the bar closing one
  minute after the alert.
- **The real size of C3-2:** the number of P-14 moments with two or more rungs, and their brackets. This is a light count
  once P-14's trade table is read, which is heavy (the lead's).
- **The heavy P-16 identity** (N-5, N-d): the lead's, not run.
- **The worker's own 27 + 5 mutants:** not in the commits. I ran mine.
