# Red-team read: the three-way runner's firm path (Q-185), staged index of wt/wt-firmpath

**Target.** The staged index of `%LOCALAPPDATA%\stage2-extended-wt\wt-firmpath` (HEAD 89be4b3): `extended/three_way_firm.py`,
`tests/test_three_way_firm.py`, `tests/three_way_firm_checks.py`, and its message `.git-commit-msg.txt`. All read with
`git show :<path>`. It was checked against two versions of the runner it calls: the runner at wt/wt-three HEAD 427a21f, and
the runner **staged** in wt-three's index for its last cycle (11 files: `three_way_journey.py`, `three_way_redraw.py`, ...).
**Specification:** `docs/plans/THREE_WAY_TEST_design.md` 1.1; DECISIONS E-213, E-221 (O-4), E-230, E-237, E-246, E-247; the
skill `contract-engine`; the vendored `propedge/campaign/lockstep.py` and `vendor/propsim/propsim.py`.

**The brief's hints.** The brief listed attacks and did not say what answer it wanted. The commit message makes claims
("bit for bit", "RB-1's clipped lane taken as the engine does", "passed ... with the staged RB-1 version"). I treated each one
as a claim to test, not as a finding.

**Method.** I built scratch trees with no licensed data in them. `tree` is wt-three HEAD from `git archive`, with wt-three's
staged files and the firm path's staged files laid over it. `tree_head` is wt-three HEAD with only the firm path laid over
it. `m1` is `tree` with one patch (see F1). Everything ran at OMP_NUM_THREADS=1, on synthetic schedules only. Each probe took
under 25 s and under 100 MB. The checks that ran were the firm path's own `three_way_firm_checks.py` sections, the touched test
file (`pytest -o addopts=`), three probes (`probe_rb1.py`, `probe_walk.py`, `probe_level.py`) and a sweep of 14 mutants
(`mut.sh`, `mutants.txt`, `judge.py`), all in the scratchpad. The numbers below are probe outputs from scratch, not results.

---

## Verdict: **must be re-declared**

The staged commit should not land as it stands. What has to change is the build, not E-247. The firm path does not
implement the law it says it pairs with:

1. Against the runner staged for its last cycle, its walk targets are wrong by a factor of the lattice step, and its own
   pairing test fails. Against HEAD 427a21f, 12 of 12 tests pass.
2. Its floor-bound ("clipped") lane can **win and survive**. E-247 and the staged runner say such an account **fails at the
   fill**. The test file asserts the divergent behaviour, so the ruled behaviour would be killed by the test.
3. It ignores a rule's profit level, which the staged runner's m-2 change reads.

Counts: **2 CHANGES-A-CONCLUSION, 5 MATERIAL, 5 MINOR, 4 NOTE.** The blocking ones are F1 to F5.

---

## Findings

### CHANGES-A-CONCLUSION

**F1. The walk's target is passed in lattice steps, but the staged runner takes ticks: every time-limited trade with step
s > 1 is redrawn with its target at g/s ticks.**
- *Where:* `extended/three_way_firm.py:324`, `RD.walk_run(read, 1, t.g // step, np.array([Lt]), step, ...)`.
- *Why it is wrong:* the staged `three_way_redraw.walk_run(read, lanes, G, L, s, n, chunk)` (staged line 328) takes **G in
  ticks**. `_ends_lanes` puts the target's last lattice point at `ceil(G/s) - 1`. The signature at HEAD 427a21f was
  `walk_run(read, lanes, up: int, ...)`, in steps (HEAD line 287). The staged runner itself calls
  `walk_run(..., G = t.g_eff, ...)` (staged `three_way_journey.py:395, 409`).
- *Evidence:* `three_way_firm_checks.py pairing` against the staged runner gave max_balance_diff $2,280 (base), $2,050
  (twin), $2,160 (missed), $2,280 (worse), $2,280 (plant). `as_walked` gave 0, because it never walks.
  `pytest tests/test_three_way_firm.py` against it: **1 failed, 11 passed** (`test_the_keys_and_the_pairing_...`, base arm,
  2280.0). With only `t.g // step` replaced by `float(t.g)` (scratch `m1`), all six arms give 0.0. Against HEAD 427a21f:
  12 passed.
- *Why the zero-edge check misses it:* its oracle calls the same wrong argument,
  `RD.walk_law(t.g // t.walk_step, L / t.tvn, ...)` (`three_way_firm_checks.py:192`). The staged `walk_law(G, L, s, n)`
  then agrees with the bug. The walk stays a martingale, so z stays small.
- *What it allows:* for a time-limited trade with g = 60 and s = 10, a target win books +6 ticks instead of +60, and the
  odds are set by the wrong barrier. Every flatten, news or max-hold exit on a coarse lattice is mis-drawn. The firm path
  then neither pairs with the toy path nor follows R-10's law.
- *The commit message:* "passed in a scratch tree with it (b09bcc8 and the staged RB-1 version)" does not hold for the runner
  now staged.
- *Remedy:* pass `t.g_eff` in ticks (see F3). Correct the oracle at `three_way_firm_checks.py:192` to
  `walk_law(t.g_eff, L / t.tvn, t.walk_step, t.walk_n)`. Re-run against the runner exactly as it will be committed, and name
  that commit in the message.

**F2. A floor-bound lane takes a race it can win. E-247 and the staged runner say it fails at the fill. The take also ignores
x_flat, and a clipped time-limited trade is raced instead of walked.**
- *Where:* `extended/three_way_firm.py:301-308`. `L = min(l, room - e - xs)`; when `L <= EPS` it races
  `Lc = min(l, room)` at p = Lc / (Lc + g). A win books -e + g - x_t and the account survives.
- *What the specification says:*
  - E-247 rules that such a lane "takes the trade at the engine's clip and **is breached**", and folds "an L_fill <= 0 account
    failed at the fill" into Wave 3.2's last cycle.
  - The staged `_classes` / `_l_fill` (`three_way_journey.py:260-283`) take the trade only when
    `L_fill = min(l, room - e - max(x_stop, x_flat)) > EPS` dollars. Where the floor binds, every other lane fails at the fill
    with certainty, and `Lanes.ffail` counts it.
  - The design note 1.1 names the defect class: "Racing the full cushion and then clipping its exit cost would credit
    near-floor trades with that cost".
- *Evidence:*
  - `probe_rb1.py`, on the checks' own rb1 fixture against the staged runner: 24 clipped lanes. On the firm path **3 survive**
    (lanes 6, 34, 59: still account 0, balance -1,982). The staged toy path fails all 24 at the fill (account 1, balance 0).
  - `probe_walk.py` (room $10, x_stop 0, x_flat $30, a walk with g = l = 2, s = 1, n = 3): the firm path walks all 24 lanes
    and **6 survive** at the target; the staged toy path has 24 fill failures.
  - The test asserts the divergence: `test_three_way_firm.py:149` requires `won > 0`. The mutants that bring in the ruled
    rule, `clip_wins_never` (a clipped lane always books -room) and `thresh_xs_xf` (`room - e - max(xs, xf)`), are both
    **killed by the rb1 check alone**.
- *What it allows:* an account the declared law fails survives with probability room / (room + g), at a gain. The trade's net
  expectation is -p(e + x_t) instead of a certain loss of the room, so the loss-side costs are forgiven near the floor. Pass
  and payout counts are biased up. The bias is larger for designs whose stop and cost grid leaves small residual rooms
  (fixed dollar stops against the $2,000 MLL), so it can rank designs and baselines differently. It also bites wherever the
  firm path is read beside the toy path: the two disagree on every account that reaches the floor. The pairing test cannot
  see it, because it runs only on a "deep" account with mll = 1e9.
- *Remedy:*
  - Decide the take as the staged `_classes` does: L_fill with `max(xs, xf)`, for every law.
  - When `L_fill <= EPS` and the floor binds, return `-room`, so the engine's clip breaches it. Count it in
    `Records.fill_failures`.
  - Refuse a binding daily loss limit until it is built (see N3).
  - Rewrite rb1 to assert `won == 0` and `lost == clipped`, and its walk half to assert a fill failure.
  - Add a pairing fixture whose accounts reach the floor: toy rules with the engine's MLL, no consistency rule, a target out
    of reach. Floors, fills and replacements then pair lane for lane.

### MATERIAL

**F3. A rule's profit level is ignored: the race and the walk use g, not g_eff = min(g, level).**
- *Where:* `three_way_firm.py:292` (`win_d = float(t.g) * t.tvn`) and `:324`. The staged runner uses `G = t.g_eff` for both
  laws (`three_way_journey.py:395, 442`; `EXIT_LAW["profit_level"] = "race"`, m-2).
- *Evidence:* `probe_level.py` on a deep account, with F1 already patched so F3 is isolated: trades with g = 60 and level = 10
  differ from the toy path by up to **$2,250** in balance (`profit_level`, 16 lanes, 21 sessions) and $50 (`flatten`).
- *What it allows:* every profit-level exit is drawn at too small a p with too large a win, which is wrong odds and a wrong
  gain.
- *Remedy:* use `t.g_eff` everywhere g is read, and put levels in the pairing fixture.

**F4. Every firm-path test is skipped on the tree the commit lands on.**
- *Where:* `tests/test_three_way_firm.py:23`, `importorskip("extended.three_way_journey")`. Neither wt-firmpath HEAD 89be4b3
  nor master has `three_way_journey.py`.
- *What it allows:* the fast-tier verdict the commit is waiting for runs none of its checks. The merge checklist's "tests
  pass" is vacuous. F1 shows the dependency moves underneath the code.
- *Remedy:* land it after Wave 3.2's last cycle has merged, run it on the merged tree, and name the runner commit tested.
  Alternatively, have the merge checklist refuse a commit whose touched tests all skip.

**F5. The one-trade-one-account router is never exercised with two live accounts, and the plan admits more seats without
refusal.**
- *Where:* `three_way_firm.py:144-145`, `:217-225`, `:263-266`.
- *Evidence:* every engine check uses `max_total_accounts = 1`, which the engine holds to one live account. The mutant
  `router_off` (the owner check removed) **survives with byte-identical check output**.
- *What it allows:* with `max_total_accounts` > 1 or None, the earliest account in rotation order takes every trade of every
  session. The others never trade, keep being billed and never resolve. That contradicts O-4 / E-221 ("accounts alternate --
  different accounts take different trades at different moments"). It is a state the engine reports as alive but that is
  untradeable for the length of the path.
- *Remedy:* refuse any plan with `max_total_accounts != 1` or `max_concurrent_combines != 1` until a declared router exists,
  or add a two-seat engine check that kills `router_off`.

**F6. Three of the records are not tied to anything: first pass, first payout and the account ordinal.**
- *Evidence:* the mutants `first_pass_off` (+1 close), `first_pay_lag` (+1 close) and `accounts_off` (ordinal + 1) **all
  survive with byte-identical output**. Pairing compares `balance` only. `identity_race` compares the engine paths, `rel`,
  and the sum of the arrivals' cash.
- *What it allows:* `J.days_to_first_payout` (a declared dimension, M-2) reads `first_pay`. A one-close shift in it, or in
  `first_pass`, would pass every check.
- *Remedy:* on the F2 floor-reaching pairing fixture, which passes and pays, assert every `Records` field against the toy
  path. Or assert against the engine's own records, computed independently: `combines[*].resolved_on` for a pass, the
  pending arrival `day + lag`, and `attempts_started + accounts_funded - 1`.

**F7. The identity is against the engine's code, not Stage 2's files.**
- *Where:* skill `contract-engine` line 53: "Every new runner has its own identity against Stage 2's files ... a design built
  on P-16's schedule reproduces P-16's registered paths."
- *Evidence:* `identity_binary` compares the binary arm with the vendored path at the same seed, in the same process, on a toy
  schedule. All six lanes share one `binary_seed`, so it is one path compared six times.
- *What it allows:* the replay is tied to the engine, not to any registered row. It is believed only through
  `identity/stage2_identity.py` transitively, and only for the default draws.
- *Remedy (specified, not run):* run the binary arm at P-14's registered protocol and path seeds, set up as
  `identity/stage2_identity.py` sets them up, at 4 paths, and compare the `PATH_COLS` columns to the registered rows. This is
  light, if P-14's setup needs no atlas read; otherwise it is a heavy job under `run.lock`.

### MINOR

**F8. The exit costs are not told apart by any fixture.** The mutant `walk_cost_swap` (x_stop and x_flat swapped on the
walk's exits) survives, because every fixture sets `x_target = x_stop = x_flat` (`three_way_firm_checks.py:61`, `cost` for all
three). Remedy: give zero_edge and pairing three distinct costs.

**F9. `fill_failures` is never filled.** `FirmRecords(...)` at `:463` leaves it None, so the count the staged runner reports
beside the verdict is missing on the firm path. Remedy: count it, after the F2 fix.

**F10. The as-walked reading on floor-bound lanes.** At `:293-300` the firm path books it for any room above EPS. The staged
toy path fails such lanes at the fill before it reaches as-walked. This is beside only, but the two paths disagree.

**F11. The search-years guard is self-declared.**
- *Where:* `check_dates` (`:195-211`) trusts the caller's `dates`. The schedule carries no dates, so nothing ties `dates` to
  `schedule`.
- *What it allows:* a held-out schedule passed with `dates="synthetic"`, or with any list of 2020-2023 dates, runs.
- *Remedy:* the schedule carries its dates or provenance, and `synthetic` is admitted only for schedules built by a synthetic
  constructor.

**F12. Choices that carry money are left unlabelled.** These are:
- payout method `aeropay` (the vendored default; the lag differs by method);
- `seat_frees` left at the engine's pessimistic `next_session`, which idles one session after every funded breach (D-339
  notes the help centre supports the same evening);
- `initial_bankroll` 1e6;
- `payout_path` standard and `payout_frac` 1.0.

Remedy: class each one as fixed and give its source, beside any result.

### NOTE

- **N1. No engine randomness leaks into the race arm.** The engine draws only from `flip_rng` (only when `flip`),
  `enforce_rng` (only with `conduct`) and the default binary factories (only when a factory is None). None of them runs on
  the race arm. The mutant `path_seed` (PATH_SEED 0 -> 987654) moved only `identity_binary.cross_diffs`, which reads
  PATH_SEED on purpose; every race-arm number was identical.
- **N2. Duplicate seed indices are not refused.** Two lanes with one seed index read one key set. The toy path behaves the
  same. Refuse duplicates in `CoinLanes` or in `simulate`.
- **N3. The daily loss limit.** Where the limit's room binds at or below the costs, the firm path races it, while the staged
  runner ends the day. Topstep's base has no limit, and `conduct` is None (RTP off), so this does not bite today. Refuse a
  `dll` until it is built.
- **N4. Cost per lane-trade.** It measured about 1.2 ms in scratch (16 lanes x 126 sessions, peak working set 85 MB). This
  is for planning only, not a result.

---

## Tried, found nothing

- **The calendar.** The combine factory is called with (k, purchase_day) and the account's `start_day` is purchase + 1; the
  funded factory is called with (j, activation_day) and its `start_day` is activation + 1. So `cal = start_day + 1 + rel_day`
  is the engine day, which is the day-hook's key, and it trades session `start + cal - 1`. The mutant `cal_off` is killed by
  identity_binary, identity_race, rb1 and every pairing arm.
- **The keys.**
  - Race and missed uniforms are cached per (moment, kind) for all lanes, indexed by position, the same way `CoinLanes`
    maps them. `uniform_lane0` is killed by identity_race, zero_edge, rb1 and pairing.
  - `twin_ignored` is killed by pairing:twin.
  - Keys carry their start, and two starts' keys are disjoint (pairing).
  - Within a lane, the `asked` set refuses a (day, slot) offered twice, and one owner per day means no moment is read by two
    accounts.
- **The account states.** These are the engine's own:
  - With one seat, no state is stuck. A live account with room at or below EPS cannot exist without a daily loss limit
    (`B <= F + EPS` fails it).
  - A ruined path is refused.
  - `combine_max_days` (2000) and the funded horizon (504) lie beyond h <= 126.
  - `rel[0]` is minus the fee, as on the toy path.
  - `months_ahead` reads closes 0..k-1, as the toy path's `_close_cash` does.
  - `payout_arrivals` (activation + 1 + r + lag) equals the engine's pending `day + lag`.
- **The costs.** `drop_stop_cost` is killed by zero_edge and pairing; `balance_funded_only` is killed by pairing.
- **The rules.** They come only from `rules_for_method` and `ledger.value("max_active_funded_accounts")` on the vendored
  verified ledger. The Protocol's stop-day flags default to False, and the liquidation clip is present.
- **Look-ahead.** The draw reads only the current session's trade at its slot and the room it is handed.
- **search_cut.** The stub's call `check_dates(window, what=...)` matches wt-user's `search_cut.check_dates(dates, last, what)`.
- **identity_binary and identity_race against the staged runner.** 0 diffs, not vacuous (cross diffs 59 and 292), through
  passes, fails and payouts.

## Could not check

- **The final form of the staged runner.** It is in its last cycle, and these findings are against its index as read today.
- **The real search_cut module on this tree (Q-172).**
- **The registered-row identity (F7).** Specified above, not run.
- **How often floor-bound lanes occur on real schedules (F2's size).**
  - The experiment: the staged toy path's `fill_failures`, and the firm path's clipped-lane log, on S1's search-years
    schedule, at the H3 draft's seeds, for a handful of starts.
  - Its cost: a schedule read on the search years only (no bar beyond S1's derivative), light to moderate. One job under
    `run.lock` if it reads the derivative in full.
- **Multi-seat behaviour (F5).** Untested by design.

## Disclosure

One git command wrote to the shared object store. While collecting line numbers, `git -C <wt-three> write-tree` wrote one
loose, unreferenced tree object (`a18c5da...`) into the object database the worktrees share. It touched no index, no ref, no
worktree file, and nothing in wt-firmpath. `git gc` prunes it. I did not delete it by hand.
