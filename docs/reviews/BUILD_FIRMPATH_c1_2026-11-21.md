# Red-team re-read: the three-way runner's firm path (Q-185), corrective cycle 1 of 2

**Target.** `wt/wt-firmpath` at `d051632`, in `%LOCALAPPDATA%\stage2-extended-wt\wt-firmpath`, read in place and not edited.
I read the whole of `git diff 3e08316..d051632`, which includes wt-three's runner at 83e4885 (merged there at 8cebb1f).
Read in full: `extended/three_way_firm.py`, `identity/three_way_firm_identity.py`, `tests/test_three_way_firm.py`,
`tests/three_way_firm_checks.py`, and the Q-185 lines of `extended/campaign.py` and `extended/gate.py`. Read for what the
firm path calls: `three_way_journey.py` (Trade, `_l_fill`, `_classes`, `_trade_mc`, `_trade_dp`), `three_way_redraw.py`
(the walk), `three_way_s1.py` (`schedule`, `walk_step_for`), `extended/router.py`, `journey_measures.workload/supply`,
and the vendored `lockstep.py` (the trading loops at l.440-530 and 695-760, the day hook at 1747-1830) and
`shared_days.py` (D-429, l.335-380). Reference: my earlier note `BUILD_FIRMPATH_2026-11-20.md` (F1 to F12, N1 to N4),
E-247 and E-251.

**The brief's hints.** The brief named its attacks and did not say what answer it wanted. The commit message makes several
claims ("30 of 31 killed, the survivor equivalent"; "the registered-row identity"; "the runner imported hard"). I tested
each one as a claim.

**Method.** All runs were light, on synthetic schedules, at OMP_NUM_THREADS=1, with nothing written in the worktree
(`git status --ignored` was unchanged afterwards).
- The brief's test command: `pytest -q -o addopts= -m "not slow and not heavy" tests/test_three_way_firm.py
  tests/test_extended_gate.py` gave **21 passed, 3 deselected, 43 s**. That is 19 firm-path tests and 2 gate tests.
- `tests/three_way_firm_checks.py zero_edge rb1 seats h4`, for its numbers.
- Three scratch probes: `sigdiff.py` (the engine's defaults, path against campaign), `probe_noseam.py` (the identity
  without the seam), and `probe_idle.py` (the surviving mutant).
- `scripts/identity_tokens.py --held` at 3e08316 and at d051632.
- The worker's own mutant sweep in the scratchpad (`firmpath_mut.py`, `firmpath_mut_out2.txt`).

The numbers below are probe outputs, not results.

---

## Verdict: **PASS WITH MINORS** (in the house terms, *stands with readings*)

Every blocking finding of the first read (F1 to F5) is answered, and I re-read in full the code each one touches. No new
finding changes a conclusion. One new finding is MATERIAL in what it costs, not in what it computes (C1-1, the `path_fn`
seam). It is fixable mechanically without a cycle: revert two files and rebind in one process. It should be done before
the merge, unless the lead chooses to pay the lapsed identity tokens knowingly.

**Counts:** 0 CHANGES-A-CONCLUSION, 1 MATERIAL, 4 MINOR, 5 NOTE.

---

## The earlier findings

| # | Status | Where it is answered (d051632) |
|---|---|---|
| **F1** the walk's target in lattice steps | **answered** | `three_way_firm.py:507` `RD.walk_run(read, 1, G, np.array([L / t.tvn]), step, ...)`, G in ticks; the oracle is now this file's own `walk_exact` (`three_way_firm_checks.py:198-232`) at the as-placed G0 (`:255`), not the code's. |
| **F2** a floor-bound lane wins | **answered** | `:473-482`: L_fill = min(l, room - e - max(xs, xf)) for every law. Where the floor binds (`floor_room <= room + EPS`) it returns `-room` and counts it; under the limit the day ends. The same classes as `_classes` (`three_way_journey.py:274-290`). rb1 asserts it (`test_three_way_firm.py:256-262`): 24 of 24 bound lanes fail at the fill on the race and on the walk, each breached and replaced on day 2 (`three_way_firm_checks.py:337-339`). The floor-reaching pairing (`:390-398`) pairs fill failures, ordinals and balances with the toy path. |
| **F3** the profit level ignored | **answered** | `:471` `G = float(t.target(e, xt))`, used by the race (`:472`) and the walk (`:507`). The level enters zero_edge and pairing (`level_every=4`). The mutants `g_not_eff` and `level_net_only` are killed. |
| **F4** every test skipped | **answered** | `test_three_way_firm.py:28-30` import the runner hard. On this tree, 19 tests ran. |
| **F5** the router never exercised | **answered** | `extended/router.py` deals each trade to one account (`:391-408`). The `seats` check: 8 of 8 lanes trade both accounts, 336 two-account days, `copied` 0. The mutants `router_off` and `router_first_only` are killed. |
| **F6** first pass, first payout, ordinal untied | **answered** | `identity_race` computes each independently from the engine's records (`three_way_firm_checks.py:183-187`): purchase day + 1 + pass day, the day recorder's `payouts_in`, and attempts + funded - 1. `first_pass_off`, `first_pay_lag` and `accounts_off` are killed. |
| **F7** identity against code, not Stage 2's files | **partly answered** | The P-14 identity exists (`identity/three_way_firm_identity.py:79-129`, heavy, not run), but it ties only `path_call` + `PassThrough` to the registered rows, not the firm path's own replay. Its seam lapses four held identities. See C1-1. The binary arm is still one path compared six times (all lanes share `binary_seed`, `three_way_firm.py:682`). |
| **F8** exit costs not told apart | **answered** | `COSTS = 1.5 / 1.0 / 2.0 / 3.5` (`three_way_firm_checks.py:57`). `walk_cost_swap` is killed by zero_edge's per-kind booking check (`:270-271`). |
| **F9** `fill_failures` empty | **answered** | `:384`, `:476`, `:710`. |
| **F10** as-walked on floor-bound lanes | **answered** | The take is decided before the as-walked reading (`:474` before `:483`), as the toy path does. `as_walked_before_take` is killed. |
| **F11** search-years guard self-declared | **partly answered** | Undated runs are admitted only under a synthetic role's issued seed (`:277-283`). Dated windows are checked against a calendar derived from the bars manifest and cut at `CHOICE_END` (`:262-269`, `:293-302`). **Still, nothing ties `dates` to `schedule`** (J.Schedule carries no dates, `three_way_journey.py:137-161`). See C1-5. |
| **F12** money-carrying choices unlabelled | **answered** | `AccountPlan.choices` (`:191-219`) covers payout method, seat freeing, bankroll, payout path and fraction, keep balance, rotation, seats, strict gap and latency, each with a class and source. The test checks 7 of the 10 keys (`test_three_way_firm.py:129`): not `strict_gap`, `latency` or `payout_method`. |
| N1 no engine randomness leaks | still holds | PATH_SEED drives only the flip and enforcement streams, neither of which runs. |
| N2 duplicate seed indices | **answered** | `:657-658`; `dup_seed_allowed` is killed. |
| N3 the daily loss limit | **answered on the draw** | The day ends (`:480-482`; test `:138-154`). It is not paired with the toy path through the engine. See C1-N4. |
| N4 cost | measured | The `cost` section (planning only). |

---

## New findings

### MATERIAL

**C1-1. The `path_fn` seam lapses four held identity tokens for an identity that needs no source edit, and what it ties is
a three-line wrapper, not the firm path's replay.**
- *Where:* `extended/campaign.py` (the Q-185 lines in the docstring, `MARKERS`, `check_path_fn`, the signature, `:338-339`,
  `:360-361`) and `extended/gate.py` (`GATE_MARKERS`, the signature, `:483`).
- *Evidence, the cost:* `scripts/identity_tokens.py --held Q-80 extended/gate.py extended/campaign.py`. At 3e08316 it is
  held (E-226 at a2342df). At d051632: "NOT held -- E-226: 2 covered file(s) changed since a2342df: extended/campaign.py,
  extended/gate.py". The same is true of every Q-80, Q-89, Q-93 and Q-101 row (E-128 to E-138, E-214 to E-218, E-226,
  E-227, E-233, E-234). Re-earning them is the Q-112 identity block, a heavy queue.
- *Evidence, the alternative:*
  - When no reducer is given, `extended.campaign.path_runner` returns the module global `_run_paths` (`campaign.py:186`),
    looked up at call time. `scratchpad/probe_noseam.py` rebinds `extended.campaign._run_paths` to a counting wrapper of
    `TF.registered_runner`, in its own process only, inside try/finally. It then runs `extended.gate.run_gate` **with no
    `path_fn`** on `gate_identity`'s synthetic blocks.
  - Result: 8 campaign calls and 48 paths through the firm path's runner, 0 row or sink problems against the vendored
    gate, gate flags equal, 2 s.
  - So F7's identity runs through the gate as it is at 3e08316, with nothing edited.
- *Evidence, the reach:*
  - `registered_runner` (`three_way_firm.py:565-587`) passes the caller's `path_kwargs`, factories and day hook to
    `path_call` (`:553-562`), which is `LS.simulate_lockstep_path(...)`.
  - So P-14's rows would confirm that this wrapper and `PassThrough` change nothing. `identity_binary` already shows that
    for the wrapper.
  - None of the firm path's own inputs is exercised: `engine_kwargs` (`:537-550`), the `Firm` terms from the ledger
    (`topstep`, `:134-152`: rules, subscription, billing, activation, lag, funded cap), `LaneDraw`, `Lane.outcome`, or the
    router.
- *What it allows:*
  - An identity cover is paid for (four lapsed tokens plus the P-14 run) that certifies a wrapper.
  - A wrong firm term in `topstep()` would pass it: say a different payout method's lag, or a cap read from the wrong
    ledger key.
  - I checked by hand that the path's defaults equal the campaign's on every key `engine_kwargs` omits (`sigdiff.py`:
    `payout_timing`, `activation_timing`, `stop_buying_when_queued`, `funded_horizon_days`, `combine_max_days`,
    `max_attempts`, `reset_failed_combines` all agree). No test holds this.
- *Remedy (mechanical, no cycle):*
  1. Revert the Q-185 lines of `extended/campaign.py` and `extended/gate.py`, so the tokens stand again.
  2. In `identity/three_way_firm_identity.py`, rebind `extended.campaign._run_paths` in that process for both
     `--synthetic` and `--paths`, with `unittest.mock.patch.object` or try/finally. Assert that the wrapper was called
     once per (shift, level) campaign, so a patch that silently does not apply fails the identity.
  3. Inside the wrapper, compare `TF.engine_kwargs(TF.topstep(), plan, horizon)` with the `path_kwargs` that P-14's
     campaign hands it, on every key the firm path sets (`rules` field for field, `subscription`, `billing_days`,
     `activation`, `payout_lag_days`, `max_concurrent_accounts`). Also compare the path's defaults on every key the firm
     path omits. This ties the firm's own terms to a registered call at no extra read.
  4. If the lead keeps the seam instead, record the lapsed tokens and the re-run of Q-112 as the price under a decision
     row.

### MINOR

**C1-2. The walk's step is inherited: the firm path follows whatever the Trade carries, and today that is wt-three's
divisor/gcd rule, not the lead's.**
- *Where:* `three_way_firm.py:500` and `:507` read `t.walk_step` and `t.walk_n`. The firm path has no step rule of its own.
- *What the inherited rule does:*
  - `J.Trade.__post_init__` refuses any step that does not divide g and l, and any walk longer than WALK_MAX
    (`three_way_journey.py:99-108`).
  - The only builder, S1's `schedule`, takes s from `walk_step_for` (`three_way_s1.py:168`, `:180-190`): the smallest
    divisor of gcd(l, g), at least the design's base step, with n <= WALK_MAX. If none fits, it returns gcd(l, g); with that
    n > WALK_MAX, the Trade, and so the whole schedule, is refused.
  - That is the opposite of "no trade is ever refused for its step".
- *The firm path's own code is ready for the lead's rule:*
  - G and L are fractional (`:471`, `:492`).
  - `walk_run`'s `_ends_lanes` (`three_way_redraw.py:309-316`) already resolves a barrier that is not on the lattice by the
    two-point last sub-step.
  - zero_edge's time-exit check (`three_way_firm_checks.py:277-278`) holds for any s.
  - The oracle `walk_exact` takes any s.
- *What is missing:* the suite has no fixture where s does not divide l or g. One cannot exist today.
- *On T:* the firm path cannot see the T behind s and n, so "the same T for s and n" is held nowhere on this path. On S1,
  T is `max(ex - entry, 1)`. For a timed trade that is ceil of the limit, so it is the limit known at the fill. What does
  read the run is the choice of law: `timed = hold > limit`, the realised hold, decides whether the trade is a race or a
  walk. That is the runner's martingale reading, outside this path.
- *What it allows:* nothing wrong on the firm path by itself. It moves with wt-three's fix. If the firm path merges first,
  it pairs with the toy path under the old rule.
- *Remedy:* after wt-three's fix lands, add a zero-edge and pairing fixture with s dividing neither l nor g, and one where
  the old rule's gcd would exceed WALK_MAX. Re-run pairing on the merged tree, and name the runner commit in the merge
  message.

**C1-3. The "equivalent" surviving mutant is not equivalent: it hides sessions with no account.**
- *The mutant:* `accounts_by_dealt` replaces `self.open_days.get(k, 0)` with `max(1, len(self.dealt.get(k, {})))` in
  `Lane.days` (`three_way_firm.py:431`).
- *Evidence:*
  - `probe_idle.py`: Topstep rules, one seat, g = 640 and l = 420 ticks, 16 lanes over 63 sessions. Every lane has
    sessions with no live account: 52 sessions in all, after funded breaches, with the seat freed the next session.
  - With the mutant applied (rebinding `Lane.days`), `supply.sessions_without_account` goes from 1 to 5 per lane to 0 on
    every lane. `workload.accounts_mean` goes from 0.92 to 0.98 to 1.0. `supply.taken_per_account_mean` differs on 16 of
    16 lanes.
  - H4's three outputs (`orders_max`, `accounts_max`, `taken_mean`) are unchanged. So the mutant is equivalent only on
    those three.
- *What it allows:*
  - `FirmRecords.workload` and `supply` (`:603-604`) carry (30)'s and (37)'s other readings, and a miscount of idle
    sessions there passes every test.
  - The `h4` check compares only the maxima and the mean taken (`three_way_firm_checks.py:445-446`).
- *Remedy:* in `h4`, compare the full `workload` and `supply` dicts with the engine's `account_days`, counting zero days.
  Add a fixture that reaches a funded breach, as `probe_idle.py` does. Correct the claim in the commit message.

**C1-4. The zero-edge oracle is independent code but weak power. The walk's law is protected mainly by common-mode checks.**
- *Independence:* `walk_exact` (`three_way_firm_checks.py:198-232`) is written apart from `three_way_redraw` and agrees
  with `_p_up` and `_bottom` case by case: up s/(s + rho_u) at the top, down s/(s + rho_d) at the bottom,
  rho_d/(rho_u + rho_d) at both. It shares the design note's statement with the code. A defect in the statement would pass
  both.
- *Power:* on the run above, 1,001 walks (426 targets, 452 stops) and 2,006 races; z values -0.70, 0.41, 1.28 and 0.54.
  A four-SE line detects a bias of about 6 percentage points in P(target), about 4.4 in the race's win rate, and about
  $15 a trade in the mean gross.
  - That catches the plant (10 points) and gross defects.
  - It would not catch, for example, the residual step taken at one half: at G = 9.5 and s = 10 that is 10/19.5 = 0.513
    against 0.5.
- *The other checks:*
  - The deterministic `bad` checks hold every booked value.
  - The pairing calls the same `RD.walk_run` (common-mode), so it catches wrong arguments, not a wrong law.
  - The real power is wt-three's 40,000-lane comparison with `walk_law` (`tests/test_three_way_redraw.py:153-176`).
- *What it allows:* a shared bias in the walk's probabilities would pass the firm path's own checks.
- *Remedy:* add the walk's analogue of `identity_race`. Replay each walked trade of zero_edge path by path with an
  independent scalar walker on the same uniforms (`K.uniforms` on the unit's walk key), bit for bit, which is exact and
  catches any bias. Or raise the walk count about tenfold with no engine call (Lane.law on a fixed room).

**C1-5. (F11's rest) The dates are still the caller's word.**
- `check_dates` admits any in-order list of real search-year sessions with a held-out schedule (`:272-303`). Today every
  dated run is refused anyway, because `extended/search_cut.py` is not on this tree and the stub refuses (`:238-251`).
- *Remedy:* when `search_cut` lands, have the schedule carry its block's dates, or a provenance token from the reader that
  built it, and check `dates` against it.

### NOTE

- **C1-N1. The strict rule refuses correctly, and its default matches the registered runs.**
  - `hold` (`:415-426`) refuses an entry that opens before another position's close plus the gap, on any account, on the
    absolute clock.
  - The boundary matches the vendored D-429 (`shared_days.py:357-358`, `open_until + gap > t`) and S1's `FLAT_GAP`: an
    entry exactly the gap after a close is admitted. No test pins that boundary; a `<=` mutant would refuse exact-gap S1
    schedules and pass the suite.
  - The default of 5 minutes equals `one_at_a_time` in P-14's, P-15's and P-16's registered manifests (a3_brk30_cb20,
    rc_s100_all, rc_s150_all; asserted at `test_three_way_firm.py:213-218`).
  - The vendored rule *skips* a busy trade, while this path refuses the lane. That is right for a single schedule that
    already holds the gap, and a hard stop for any that does not.
- **C1-N2. Failing at the fill is mechanically the engine's end.** A returned `-room` (`:479`), against the engine's clip
  (`lockstep.py:475-476`) and `B <= F + EPS` (`:490`), gives a breach on the day and a replacement at the close. rb1 shows
  this through the engine's own records. E-247's "as the vendored engine does" holds for the end. The vendored zero-cost
  `RandomDraw` would instead *race* at the cushion (`adapter.py:125-162`). Where x_flat > x_stop and
  e + x_stop < room <= e + x_flat, a real trade still had a race to win. The ruling is therefore conservative near the
  floor, the same on both paths. It is the lead's ruling, reported here beside it.
- **C1-N3. The router copies nothing and re-deals nothing.**
  - Each trade is dealt once (`router.py:111-121`). `taken` refuses a moment read twice. `copied` is 0.
  - A trade dealt at the session's start to an account that fails earlier that session is dropped, not re-dealt. This
    matters only with more than one seat, and it is the same session-start routing as Stage 2's day hook.
  - `last_busy` advances on dealt trades, taken or not.
  - No choice reads a later trade's outcome.
- **C1-N4. The daily loss limit's day end is tested on the draw only.** It is not paired with the toy path through the
  engine. Topstep's base has none, but the ledger's DLL election (`rules.yaml:313-326`) would need that pairing before a
  plan elects it.
- **C1-N5. Reads.** No dated run can reach 2024 or later: `check_dates` refuses after `CHOICE_END` = 2023-12-29
  (`reader.py:139`), then off-calendar dates, then the stub refuses everything. The manifest's `day_list` is metadata, and
  its test is marked heavy.
  - The heavy `--paths` identity reads 2020-01-02 to 2026-07-16 (`JUDGED_END`, `reader.py:141`) under `gate_identity`'s
    declaration row E-028 (`three_way_firm_identity.py:142-145`). That is a reproduction of an already-registered P-14
    result, the kind E-247 rm-4 excepts, but it is a *new* identity borrowing another identity's row. The lead should
    record that under rn-5.
  - Nothing reads NQ from 2026-07-17.

---

## The `path_fn` seam, the brief's questions

- **Unused (None), can it change a registered path?** No.
  - Every Q-185 line is a guard on `path_fn is not None`, or a keyword whose default is None.
  - Provenance gains a key only when the seam is given.
  - The re-composition proofs (markers stripped) equal the vendored functions (`synthetic_problems`, `:74-75`).
  - `tests/test_extended_gate.py` passes.
  - Adding "Q-185" to MARKERS also means any future line carrying that marker escapes the proof. That is the marker
    scheme's standing limit.
- **Is the cost justified?** No. See C1-1: the same identity runs with no edit to either file.

## The equivalent mutant

Not equivalent. See C1-3. It is equivalent only on H4's three emitted outputs.

## Tried, found nothing

- **The calendar.** `cal = start_day + 1 + day` gives the engine day for both legs (combine factory (k, purchase), start
  purchase + 1; funded factory (j, activation), start activation + 1). The day hook runs before `begin_session`.
- **The floor mirror.** `st[0] + st[1]` against the engine's B - F: the same clips, float drift far below `EPS`.
  `floor_mirror_off` is killed.
- **The take.** It matches `_classes` in dollars (`_l_fill * tvn > EPS` against `L_fill > EPS`). L > EPS whenever the
  trade is taken, since max(xs, xf) >= xs. G > 0 under any level.
- **The race booking.** A level win books exactly +level (win_d = level + e + x_t).
- **The engine's defaults.** `simulate_lockstep_path` and `simulate_lockstep_campaign` share every default `engine_kwargs`
  omits (`sigdiff.py`).
- **Look-ahead.** The draw reads its session's trade at its slot, the room handed to it, and the coin field. Routing per
  trade reads only earlier trades' scheduled busy minutes and the session's live accounts.
- **H4's three outputs** against the engine's ledger and day recorder: `bad` 0 on one seat and two.
- **rb1:** race 24/24, walk 24/24 failed at the fill; flatten: 6 lanes clipped by the engine, 0 counted as fill failures.
- **The worker's sweep:** 30 of the 31 mutants are killed, as stated. I checked the killing test of each against its
  replacement.
- **Nothing written in the worktree.** `git status --ignored` was unchanged; `PYTHONDONTWRITEBYTECODE=1` was set.

## Could not check

- **The P-14 registered run (`--paths 4`).** It is heavy and the lead's. In particular, I could not check whether P-14's
  gate call hands `registered_runner` a flip stream or a wallet, which it refuses (`:571-574`).
- **The firm path under wt-three's corrected step rule.** That fix is not on this tree (C1-2).
- **How often idle sessions and floor-bound lanes occur on S1's search-years schedules** (C1-3, C1-N2).
  - The experiment: the firm path's `fill_failures` and `supply.sessions_without_account` per lane, on S1's search-years
    schedule at the H3 draft's seeds, for a few starts.
  - The cost: light to moderate, and one job under `run.lock` if it reads S1's derivative in full.

Scratch files (not results), all under
`C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\`:
`firmpath_c1_pytest.txt`, `firmpath_c1_checks.json`, `sigdiff.py`, `probe_noseam.py`, `probe_idle.py`.
