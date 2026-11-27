# Can a contract-only screen go ahead of F-13's bar-based rounds? (scout, 2026-11-27)

Read-only scout (wt-scout role). Nothing was run and no test was run. No `results/h4_readings_*`, `results/h4_trades_*`
or `results/h4_units_*` file was opened, no held-out date was read, nothing from NQ 2026-07-17 on was read, and no seed
value is quoted. The draft read is the uncommitted `prereg/DRAFT_F-13_topstep_survey.md` in the `wt-fs1` worktree
(`%LOCALAPPDATA%\stage2-extended-wt\wt-fs1`, staged, not on the branch's tip). Its line numbers below are that file's.
Every cost figure is an **estimate** built from code structure and from the H4 sizing scout's logged figure, and is
labelled so. None is a result.

## The question

Can a contract-only screening round go ahead of the bar-based rounds in F-13 (the Topstep NQ survey) without dropping
a design the full reading would keep?

## The answer

**As a ranking screen (a contract model that drops designs it predicts to be poor): no.** No error bound for it can be
established, and it would save little time. There are three reasons:

- The journey measures depend on the bars through the trigger and shape layer: supply, the fills' timing, exit times
  at R, the 'f' (time-limit) kind, the daily stop from S1, and sigma. That layer is about half the space's dimensions.
- They also depend on campaign path effects that stage one's engine does not model: several accounts, the router's
  hold, purchases, calendar lags and R-10 flattens.
- The four baselines cannot calibrate such a screen's error for designs outside their corner of the space.

The time is also not in the bars. It is in the campaign replay over start days and seeds: 97 % of a unit
(`docs/plans/SPEED_PROFILE_2026-11-27.md:19, 45`). A bar-free screen therefore saves only what it drops.

**What is feasible and safe is an exact-bound screen.** It drops a design only when a declared limit or gate is
certain to fail on the deciding re-read, whatever the coin draws. It has two tiers:

- **Tier C, contract arithmetic only, with no bars.** These are infeasibility predicates on the money levers and the
  verified rules: the opening spend above B\*, or above the peak out-of-pocket ceiling; a payout path that cannot be
  reached at the largest gain the risk allows.
- **Tier T, the design's trade table from one bar pass and no campaign.** This tier holds the declared gates read on
  the schedule, and an upper bound on taken trades against the supply floor `taken_mean_p10`.

**The identity** has three parts:
1. the screen's trade table must be the runner's own, hash-equal;
2. each bound must hold unit by unit with zero violations on H4's four baselines and on a declared set of designs read
   both ways;
3. each infeasibility predicate must reproduce the full route's per-unit value exactly where it fires.

**The estimated saving is small.** About 4-20 % of design runs, but only about 1-12 % of machine time (an estimate;
section 6), because the dropped designs are mostly the cheap screen-size cells.

**Larger exact savings sit beside the question** (section 7). They change no verdict:
- check every plateau neighbour's gate before reading any of them;
- compute the real-path arms lazily;
- read the baseline arms once per protocol.

## 1. Where the cost of a bar-based design read is (evidence)

- **One unit's replay is nearly all lane loop.** `simulate_lockstep_path` holds 97 % of a unit. Inside it, the race
  wrapper (`RaceOver`: the law, the uniforms, the walk) is about 63 % and the vendored lockstep about 37 %
  (`docs/plans/SPEED_PROFILE_2026-11-27.md:15-26, 45-47`). The bar pass is not in that profile at all. A design's
  trade table is built once, before the replay (`extended/design_trades.py:225-320`).
- **Each design read reports more than the design arm.** `RunOutput.arms` holds the design arm and each baseline's
  arm, and `real_path` holds the as-traded and reflected readings (`extended/survey.py:216-235`). So a read is several
  campaign replays at the protocol's starts times seeds.
- **The sizes.** The draft reads at three sizes. Measured in screen-size units c (4 seeds times a quarter of the
  starts):
  - the survey and rounds 1-4 at the screen size, 1c each;
  - the promotion and rounds 5-8 at the deciding size, 16 seeds and every start, so 16c each;
  - the candidates' re-read and the plateau's neighbours at the 64 re-read seeds and every start, so 64c each.

  Sources: draft lines 471-477 and 546-550; the plateau reads every neighbour "on the same re-read protocol"
  (`extended/plateau.py` docstring, "every neighbour is read on the same re-read protocol").
- **A cross-check on scale (estimate).** The H4 sizing scout logs about 36 h of machine time per baseline at 128
  seeds, every start, four arm-runs (`docs/plans/H4_SIZING_SCOUT_2026-11-27.md:11-12`). Scaled down, a screen-size
  read is of the order of the lead's "about 20 minutes a design".

## 2. The inputs a contract-level screen needs, and which need bars (question 1)

| input | the lever(s) | needs bars? | source |
|---|---|---|---|
| dollar risk per trade, its upper bound | S3, S4 (and A1/A2 flip's risk) | no: realised risk never exceeds the intended risk, `min(floor(risk / risk per micro), cap) x risk per micro` | `vendor/stage2/propedge/campaign/state_policy.py:34`; `extended/lever_space.py:434-443` (`_risk`) |
| bracket R | S2 | no for its value; **yes for its exit time and kind** (`_x_<R>`, `_k_<R>` from the walk) | `extended/design_trades.py:301-305` |
| stop in ticks, contracts, stop band, realised-risk gate | S1, then S9 by `modes_rules.size` | **yes**: S1 is a multiple of `trail20_range_pts`, read from bars | draft lines 271, 279, 302-306 |
| trades a session, their timing | T1-T5, T7 per slot | **yes**: the trigger's offers, fills and void calendar | `extended/design_trades.py:241-279` |
| resolution (the 'f' kind), sigma for R-10 | T2-T5, S1, S2 | **yes** | `extended/design_trades.py:288-291`; `extended/three_way_baseline.py:38-39` |
| accounts, purchases, budget, payout path and first request, fees, lags | A1-A12, A18-A21 and the verified rules | no | `extended/lever_space.py:452-560` |

- **Can one bar pass per trigger be cached and reused across the money levers?** Yes in principle. `build_trades`
  takes no account-policy or risk input (`extended/design_trades.py:225-228`). Its table holds every R of `rr_grid` in
  one pass (`:301-307`). E-292 (3) already plans a cache keyed by content hash (with Q-215). There are three caveats:
  - **The key is per slot,** and it holds T1 to T5, T7, S1 and S2. A table can be built per component and merged,
    because one position at a time is applied later, in the campaign's router.
  - **The survey rarely shares a key.** T3, S1 and S2 are continuous or fine lattices, so two designs of the Sobol
    survey almost never share a trigger layer. The cache pays off only on:
    - the promotion's and the re-read's same designs;
    - the plateau neighbours that step a policy or money lever (about 23 of a typical design's roughly 60 neighbour
      steps, an estimate from the lever list at `extended/lever_space.py:771-821`);
    - the baselines.
  - **Two gaps to close first.** `build_trades` takes one `stop_ticks` (`:227, 285`), and S1's per-day stop is not
    wired yet. A spec has one entry kind (`:29-30, 262-265`). Both are Q-215's to close.

## 3. What the contract level reproduces, exactly or only approximately (question 2)

"Exact" below means a bound or a predicate that holds on every unit, whatever the coin draws. The deciding values
themselves are reproduced exactly by nothing short of the full route.

| measure or limit (`extended/wave42.py:114-143`) | contract only (Tier C) | trade table, no campaign (Tier T) | why not more |
|---|---|---|---|
| `not_paid_within_B` (ceiling, mean, 126) | **exact = 1 on every unit** when the opening spend (subscriptions of the evaluations bought at the first purchase step) exceeds B\*; else approximate | **exact = 1** also when no payout path is reachable within W (below) | spend before the first payout depends on failures, replacements (A10), rebills and activations along the path |
| `peak_oop_12_months_p90` (ceiling, 252) | **exact lower bound** = the opening spend, so a certain fail when it exceeds the ceiling | same | replacements, rebills, activation fees, the payout lag |
| `first_payout_days_p50` (ceiling, 126) | lower bound D_min from the rules alone (pass days under the consistency share, the funded winning days or minimum days, the lag): tiny, never binds | **exact lower bound** with the session's largest possible gain (the chain of non-overlapping fills times R times the risk bound); a certain fail when D_min exceeds the ceiling on more than half the units | the actual pass and payout days are path- and coin-dependent |
| `orders_max_p90`, `accounts_max_p90` (workload ceilings) | upper bound A7 + A6 for accounts (certifies a pass, never a fail) | upper bound: the per-session chain's maximum (certifies a pass) | a fail needs a lower bound that holds on more than 10 % of units: not available without the campaign (an account can fail in its first session) |
| `taken_mean_p10` (supply floor, 126) | none | **exact upper bound**: taken <= the session's greedy chain of non-overlapping fills at R, five minutes flat, held to the historical exit; so a certain fail when p10 over every start of that bound is below the floor | which fills are taken also depends on live accounts and on A3's stop rule |
| W42-R2's proposed floor on the median 12-month net | none, except in the infeasible cases | if no payout is reachable in 252 sessions, net <= minus the opening spend on every unit: a certain fail against a floor at or above that | otherwise the upper bound (seats times cycles times the cap) is far too loose to bind |
| the composite's six dimensions; the do-nothing floor | approximate only | approximate only | all six are path quantities |
| the no-harm floor (as-traded against reflected, real path) | **not available** | **not available** | needs the real path and the campaign (`extended/survey.py:1602-1609`) |
| the gates (supply, resolution, realised risk, stop band, pair share) | none | **exact, if declared on the schedule** (the trade table), not on the taken trades | `survey_parts.make_gate` is unbuilt, so the choice is still open (draft lines 103-106, 564-566) |

**Why the rest is only approximate.** Each mechanism is in code:

1. **Taken trades depend on exit times on the real path.** The router holds an account to the trade's historical
   exit at its R (`extended/three_way_baseline.py:68-70, 255-262`). It also holds one position at a time across the
   firm (draft line 378). So supply depends on the bars and on how many accounts are live.
2. **Time-limited trades are not binary.** A trade that reaches its time limit takes R-10's stopped walk to the limit,
   using sigma (`extended/three_way_baseline.py:38-39`). Stage one's solver has "no intraday partial outcomes"
   (`vendor/stage2/propedge/research/u_value_map.py:17`). A partial outcome can move the $150 winning-day count, or the
   consistency share, across its line.
3. **The room at the fill and the trailing floor.** The take at the fill is L_fill = min(stop d, room - e - ...)
   (`extended/three_way_baseline.py:34-35`). The Combine's floor trails the end-of-day peak
   (`vendor/stage2/propedge/campaign/state_policy.py:8`). So the order and the session of each trade matter.
4. **Need-aware exits.** A need-aware exit, or the consistency cap, cuts the target to min(G, need)
   (`extended/three_way_baseline.py:31-33`). That is a function of the state.
5. **The campaign.** Evening purchases are gated by the queue, the budget and the concurrent caps
   (`vendor/stage2/propedge/campaign/lockstep.py:2098-2155`). Rebills are due by the purchase day
   (`:1588-1600`). RD-03's levers act on the end-of-day steps: Back2Funded's window, the hold's expiry and the
   house-money fee rule (`extended/levers_path.py:9-13`).
6. **Stage one's engine models one account alone.** It runs a fixed `trades_per_day` (propsim's `Policy`,
   `vendor/stage2/vendor/propsim/propsim.py:79-86`) and lockstep binary draws per slot
   (`vendor/stage2/propedge/contract/adapter.py:9-21`). It has no void day, no supply variation, no routing, no queue
   and no calendar.

Extending the contract model to cover 1-6 would rebuild the campaign replay, which is where the cost is.

## 4. A safe drop rule (question 3)

**Rule (proposed for the declaration, before the pin): a design is dropped before its campaign only when a declared
predicate proves that it fails, on the deciding re-read, a limit or gate that the finalist rule requires to hold.**
The predicate must hold whatever the coin draws. It is evaluated on **every** search-year start, not only on the
screen's quarter. Three reasons:

- **The bound is the same on every seed.** It reads only the schedule and the contract, so over any seed set its
  quantile is its quantile over starts.
- **The keep rule reads every start.** A candidate is kept only if every limit's point estimate on the re-read (64
  seeds, every start) is inside (`extended/survey.py:1577-1600, 1688-1698`).
- **A quarter of the starts is not enough.** A bound computed on the screen's quarter could fail there and pass on all
  starts. The design could then be promoted (the promotion filters on the floors, not the supply limit; draft
  lines 476-478) and kept.

The drop keys, all exact:

| key | tier | the predicate (each figure read from its key or lever, never typed) | the limit it proves failed |
|---|---|---|---|
| C-1 | C | the opening spend exceeds B\*. The opening spend is the subscriptions, at A4's fee, of the evaluations the first purchase step buys: min(A7, A11's month budget, what the bankroll allows), per `lockstep.py:2121-2148` | `not_paid_within_B` = 1 on every unit |
| C-2 | C | the opening spend exceeds `peak_oop_12_months_p90`'s ceiling | `peak_oop_12_months_p90` |
| C-3 | C | A5 `standard`, A3 `one`, and the largest winning trade (R times the mode's largest dollar risk, flip's included, less costs) is below `xfa_std_winning_day_min`. Then no standard-path payout is ever eligible | `first_payout_days_p50` = W + 1; `not_paid_within_B` = 1 |
| T-1 | T | each gate key read on the schedule (the trade table) | the gate (template lines 413-415: "counted and its measures are not read") |
| T-2 | T | p10 over every start of the mean, over the start's W sessions, of the per-session greedy chain count is below the `taken_mean_p10` floor | `taken_mean_p10` |
| T-3 | T | C-3 with the chain's largest session gain in place of one trade (A3 `all` or `cap`) | as C-3 |
| T-4 | T | D_min, from the chain's largest gains and the rules, exceeds the `first_payout_days_p50` ceiling on more than half of every start's units | `first_payout_days_p50` |

**What the rule never does:**
- it never drops on the composite, on "below the baselines", on the do-nothing floor or on the no-harm floor;
- it never uses a margin, because no bound on the contract model's bias exists across the space (section 5).

**Three consequences to state in the declaration:**

1. **The candidate list can change.** It is "the first 4 after the floors" (`extended/survey.py:1644-1659`), and a
   candidate that fails a limit on the re-read is dropped, not replaced (`:1675-1705`). A design T-2 would drop could
   otherwise take a candidate's slot and then fail. So the screen can let a fifth design in. It never removes a design
   the keep rule could keep.
2. **The surrogate's path changes.** A dropped design gives the surrogate no reading: the one door refuses
   predictions (`extended/search_space.py:94`). The rounds' proposals then differ from an unscreened search's. That is
   legitimate, since the screen is part of the declared procedure and the unscreened search is never run, but it is
   said.
3. **C-1 to C-3 can sit at sampling.** They need no bars, so they can be a refusal class of `Space.check`, which the
   proposer's pool also passes (`extended/proposer.py:30`). Infeasible points are then replaced by feasible ones,
   counted (`search_space.py:41-56`). The cost is an engine change, re-hashed and reviewed before the pin. **The
   simpler route for F-13** is to put every key in the gate part and change no engine; the survey then reads fewer
   than 512 designs, the dropped ones counted.

## 5. The identity it needs, and what "agree" means (question 4)

- **(S-I1) The inputs, hash-equal.** The screen calls the runner's own `design_trades.build_trades` through one cache
  keyed by content hash, never a second implementation. On the four baselines the table equals B-I1's registered
  search-year sub-hashes (draft lines 127-130) and I-5's naive-coin offers (`:131-132`), compared exactly. On a
  declared set of designs (below) the screen's table and the runner's table have one `trades_hash`.
- **(S-I2) Every bound holds, unit by unit.** Each bound must be on the correct side of the full route's value on
  every unit (start, seed):
  - taken_mean <= the chain bound;
  - `spent_before_first_payout` >= the opening spend;
  - `peak_oop_12_months` >= the opening spend;
  - `first_payout_days` >= D_min.

  It is checked on H4's per-unit readings of the four baselines at H4's keys (a worker's identity task, not this
  scout's) and on the declared designs. **Agree means zero violations**, with a dollar key compared within a
  millionth of a dollar (MEASURES 1.2). One violation refuses the screen (the failure protocol), never the design.
- **(S-I3) Every predicate where it fires.** On every unit of every declared design where C-1, C-3, T-3 or T-4
  fires, the full route's value must equal the predicted one exactly (`not_paid_within_B` 1, `first_payout_days`
  W + 1). On the baselines none fires, so S-I3 there is vacuous, as it should be. It needs designs built to fire:
  - synthetic ones in light unit tests (`extended/synthetic_bars.py`);
  - a few real-bar ones at the screen size, heavy, under `run.lock`.
- **Why the baselines alone are not enough.** They sit in one corner of the space:
  - all carry the breakeven move law, which no design has, since S7 is dropped (draft lines 277, 434-435);
  - the naive coin offers at every mark of P-16's window (draft lines 117-120);
  - all hold P-16-like account policies.

  A bound check on them proves the bound's arithmetic, not its reach. That is why S-I2 and S-I3 add declared designs,
  which should be the survey's own first Sobol block read on the full route, so no design run is spent on the identity
  alone.

## 6. How it fits the pinned template (question 5)

- **Gate keys.** The template's gate bullet already admits the T keys: "The gates read before any outcome ... A design
  that fails a gate is counted and its measures are not read" (`prereg/TEMPLATE_design_search.md:413-415`). The
  survey-spec's gate `keys` list (draft lines 564-566) grows by T-2 to T-4 (and C-1 to C-3 on the gate route). The
  gate part's sha256 binds them.
- **The order.** The draft's runner reads the gate after the whole run: `read_design` calls the runner, then
  `screen` (`extended/survey.py:1485-1491`). Tier T needs the gate part to be evaluated on the schedule before the
  campaign. That is a build requirement of `survey_parts` (draft section 14 step 2), written into section 6 of the
  draft.
- **Counting.** The template counts "every failed-gate design" (`TEMPLATE_design_search.md:640-641`). The ledger
  counts refused cells with their class (`extended/search_space.py:56`). `variant_rows` writes every row, refused
  ones included, labelled role:status:class (`:830-837`). The draft's section 13 count (`k_cells` = 768, refused
  proposals capped) stands. Screen drops are counted inside it, with their key, and printed beside.
- **k.** None. The search takes no k (draft lines 5-7; E-204). The screen spends nothing.
- **The variant ledger and the protocol.** The screen's bounds are read on the search years only, through
  `design_trades.check_search_days` (`extended/design_trades.py:148-156`). Nothing held out is written.
- **What changes in the draft.** Section 6's gate bullet and the survey-spec's gate keys. Section 13 gains a line
  "screen drops, by key". Section 16 stays empty (it is declared before any read).

## 7. The expected saving (question 6), an estimate

Cost in screen-size units c (section 1). Estimate.

| stage | reads | cost |
|---|---|---|
| survey + rounds 1-4 | 640 | 640c |
| promotion | 32 | 512c |
| rounds 5-8 | 128 | 2,048c |
| candidates' re-read (+ five-minute twins) | 4 (+ 4) | 256c to 512c |
| plateau, if candidates reach it | 4 x K, K about 50-70 neighbours a design (axes, radius 1: two a real or integer lever, cells - 1 a categorical, on about 2-3 active slots plus the policy levers) | 0 to about 18,000c |

**What the exact screen drops (estimate):**
- **Survey and rounds 1-4: about 5-30 % of cells.** These come mostly from T-1 (resolution near NY PM's flatten, the
  stop band) and T-2 (one narrow slot against a floor set from the baselines). C-1 to C-3 add little:
  - the opening spend is at most 7 evaluations' fees (`evals_max`, `extended/lever_space.py:127-128`), likely below
    B\*;
  - C-3 needs a small S4, a low R, `one` and `standard` together.
- **Rounds 5-8: 0-10 %.** The proposer works "inside the limits" (draft lines 510-512).

**The saving:**
- **By count of design runs avoided:** about 4-20 %.
- **By machine time:**
  - about 1-12 % when no candidate reaches the plateau;
  - about 0.2-2 % when all four do, from the drops alone.

The inputs that decide it are unknown until W42-R1 is applied (Q-189): the supply floor, B\* and the ceilings.

**Larger exact savings found on the way.** They change no verdict and are offered for the build:

1. **Gate first in the plateau.** A neighbour refused by the gate refuses the candidate (`extended/survey.py:1662-
   1664, 1700-1703`). Checking every neighbour's Tier T gate before reading any neighbour's campaign saves that
   candidate's whole plateau whenever one neighbour fails, with the same verdict. A candidate pushed by the proposer
   to a gate's edge is the likely case (Q-139's cliff). Estimate: 0 to about 25 % of the plateau's cost.
2. **Lazy real-path arms.** The as-traded and reflected readings feed only the no-harm floor (`:1602-1609`), read in
   the promotion's and the candidates' floor order. They need computing only for cells reached in that order. The
   vendored-outcome replay costs about a quarter of a race replay (`SPEED_PROFILE_2026-11-27.md:31`). Estimate: up to
   about a third of each non-contender's read.
3. **Baseline arms once per protocol.** Every read carries the four baselines' arms (`extended/survey.py:216-224`). A
   baseline's keys depend only on (start, seed index) (`docs/plans/H4_SIZING_SCOUT_2026-11-27.md:111`). So the
   arms are identical across designs on one protocol and can be computed once per protocol (screen, deciding,
   re-read), held by B-I3. If the runner recomputed them per read, this alone would be the largest saving, roughly
   four fifths of each read.

## 8. What is unknown, and how to find it

- **The share of Sobol designs that T-1 and T-2 drop.** It needs the applied W42-R1 values (Q-189) and the cached
  trade tables. Counting it is a worker's task on the search years: no campaign, a bar pass a design.
- **Whether the realised-risk gate can be read on the schedule.** Its allowance-capped form (E-022 (1), E-032) may
  read room cuts, which are path quantities. If it can, it is a T key. If not, it stays after the campaign. Settled
  at `make_gate`'s build.
- **The plateau's K.** `plateau.critical_value(0.05, k_max, 64)` needs k_max (draft line 554). The build prints it;
  it sizes the plateau line above.
- **Whether the runner caches the baselines per protocol.** It is unbuilt (`survey_parts.make_runner`, draft lines
  569-572).

## 9. What it would declare

- **Mechanism.** No trigger and no lever: a refusal step of the survey's procedure. Tier C at sampling or in the gate;
  Tier T in the gate, on the schedule, before the campaign.
- **Contract fit (CHARTER 4).** It changes no trade, so nothing in the draft's contract-fit table (lines 374-386)
  moves. It only refuses designs that the verified rules or the declared limits already fail.
- **Place in the component schedule.** None. In the survey-spec it lives in the gate part's keys, plus a
  `Space.check` class if the sampling route is taken (an engine change, reviewed before the pin).
- **What it adds to a journey.** Nothing directly. It moves machine time from certain failures to designs that can
  still pass.

**Proposed TASK_QUEUE line:**

`| Q-2NN | F-13's exact-bound screen: the gate part reads its keys on the design's trade table before the campaign (T-1..T-4, C-1..C-3 as gate keys), plateau neighbours gate-checked first, real-path arms lazy, baseline arms once per protocol; identity S-I1..S-I3 (bounds unit by unit, zero violations) | wt-survey | queued | Q-215, Q-189 | light (heavy for S-I3's real-bar designs, under run.lock) | 0 | (the lead's row) |`
