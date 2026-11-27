# Speed profile, 2026-11-27 (measurement only; no code changed)

Method: synthetic fixtures only (`tests/three_way_baseline_checks.py:95 job()`, 80 sessions, 1-3 trades a session, so
about 2 trades/day; `tests/test_three_way_runner.py:57 toy`), `OMP_NUM_THREADS=1`, one light process, no bars, no
held-out dates. `cProfile` (inflates small calls, shares are indicative) plus wall-clock timers. Scripts were in the
scratchpad (not committed). The synthetic job is small; absolute seconds do not transfer to the real job, shares and
scaling do, with the caveat that real jobs have more trades a day.

## Part 1: one unit's replay

Path: `extended/three_way_baseline.py:673-677` loops lanes; each lane calls `replay` (l.602-626) which builds a fresh
`SharedDayDraws` and runs the vendored `simulate_lockstep_path` (`vendor/stage2/propedge/campaign/lockstep.py:1232`)
with each account's draw wrapped in `RaceOver` (l.316-). Then `records_of` (`extended/three_way_firm.py:642`).

Profile, 8 lanes, horizon 63, total 0.50 s under cProfile (cumulative, so nested):

| stage | cum s | share |
|---|---|---|
| `simulate_lockstep_path` (everything in the lane loop) | 0.488 | 97 % |
| of which `RaceOver.__call__` (l.344) incl. the vendored draw it wraps | 0.314 | 63 % |
| - vendored sizing draw inside it (`sizing.py:713`) | 0.064 | 13 % |
| - `_law` (l.432) | 0.210 | 42 % |
| - coin uniforms (`uniform` l.256 -> `coin_uniforms`, fastkeys.py) | 0.057 | 11 % |
| - `_walk_uniforms` (l.557, Philox/`grid_indices`) | 0.089 | 18 % |
| - `_walk_one` (l.282, pure-Python loop) | 0.027 | 5 % |
| vendored lockstep remainder (days, sizing, settlement, shared_days) | 0.174 | 35 % |
| `records_of` | 0.0005 | 0.1 % |
| exact runs, `J.expect` (toy DP, h 63, per start) | 0.021 s | not in the lane loop |
| scorecard value, `J.p_b_values` / `R.matrix(p_b)` | under 0.001 s | about 0 % |

Wall clock with outcome="vendored" (no RaceOver) vs "race", h 63: 1 lane 0.019 vs 0.072 s; 4 lanes 0.076 vs 0.196 s.
So RaceOver adds about 60 % of the lane's time; the vendored lockstep alone is about 39 % at 4 lanes.

Scaling (wall seconds, race):

| horizon | 1 lane | 2 | 4 | 8 |
|---|---|---|---|---|
| 20 | 0.023 | 0.039 | 0.056 | 0.093 |
| 40 | 0.051 | 0.062 | 0.104 | 0.184 |
| 63 | 0.072 | 0.107 | 0.196 | 0.315 |

Linear in lanes (about 0.035 s a lane at h 63 after the first, which carries about 0.035 s of one-time key and
`SharedDayDraws` set-up) and linear in horizon (h 20 to 63 is 3.15x the sessions; 4 lanes took 3.5x).

Is the lane loop the dominant cost? Yes: it holds 97 % of the time; `records_of`, the scorecard value and the exact
program are each under 1 %-5 % at this scale. The work inside a lane is about 37 % vendored lockstep and 63 %
RaceOver (draw wrapper, law, uniforms, walk).

Would lane-batching help? The vendored lockstep is stateful per lane (account balances, one `simulate_lockstep_path`
call a path), so it cannot be batched without touching `vendor/`: that 35-40 % stays. The batchable part is the
random draws: coin uniforms plus walk uniforms (about 29 % of the time, per-call Philox with 337-4300 small calls per
8 lanes; `grid_indices` alone is the top tottime item) could be drawn once for all lanes as arrays. Rough saving
15-25 % of a unit's time (a vectorised draw still costs something and the walk loop `_walk_one` is Python and per lane).
Larger gains need less per-call overhead in `_law`/`__call__` (42 % and 63 % incl. children; 4297 calls per 8 lanes),
e.g. caching the per-trade key and uniforms across lanes. Not a 2x without changing the engine.

## Part 2: why the fast tier runs serially

`.git/fasttier-verdicts.log` (166 lines): main-tree whole-tier serial runs 4072-5790 s from 2026-11-23 17:59Z
onward; the only main-tree parallel run is `d4ecaef` 2026-11-24 04:41Z, n=4, 1760 s. Worktree runs at n=2 took
1317-1337 s (`log` 2026-11-23).

Constants (`scripts/fasttier_xdist.py:66,70,72,104-122`; `scripts/fasttier_lock.py:88,128,511`):
`PER_WORKER_GB = 1.2` (lock.py:128), `RESERVE_GB = 1.5` (xdist.py:72), `MAX_WORKERS = 4`.
`n = floor((available - 1.5 - beside_gb) / 1.2)`, clamped 1..4. `git log -L` shows both were set by Q-193 (`92dc8da`).

What Q-211 (`30fb67f`, merged `635afaa`) changed: only `scripts/fasttier_lock.py` MEASURED_PEAK_GB 2.26 -> 1.00 and
SLOT_RESERVE_GB 2.5 -> 1.2 (the slot-admission reserve; `slot_reserve_gb(n)` = 1.2 + (n-1)*1.2), plus a git grep -l
change in q108. It did NOT touch `choose_workers`, `PER_WORKER_GB` or `RESERVE_GB`. It lowered the slot reserve,
which makes a second slot easier to admit (2.7 GB beside a serial slot, 3.9 GB beside an n=2 slot), which, by the
shared-memory rule (`beside_gb`), can reduce n when another slot is running.

n from `choose_workers` with no slot beside (beside_gb = 0):

| free GB | 2.0 | 2.7 | 3.0 | 3.8 | 3.9 | 5.1 | 6.3 |
|---|---|---|---|---|---|---|---|
| n | 1 | 1 | 1 | 1 | 2 | 3 | 4 |

(2-4 GB free gives n = 1 until 3.9 GB, then 2.) With a second slot running at serial reserve 1.2 GB beside, add 1.2 GB
to each threshold: n=2 at 5.1, n=3 at 6.3, n=4 at 7.5 GB.

Conclusion: serial running is not caused by the Q-211 constants (PER_WORKER_GB/RESERVE_GB are unchanged since Q-193;
serial runs of 4000-4400 s already preceded the n=4 run on 11-24, which happened when memory was plentiful). It is
caused by free memory at slot take being below 3.9 GB (about 2 GB free, as now, gives n=1; the run also needs
pytest-xdist and an unset/non-zero `S2X_FASTTIER_WORKERS`). Free memory to restore: >= 3.9 GB for n=2, >= 5.1 GB
for n=3, >= 6.3 GB for n=4 (add 1.2 GB per other running slot). The n=4 evidence (1760 s) was measured when the
machine had room; the Q-211 whole-tier n=2 measure (peak worker 0.933 GB, `docs/measurements/q211_mem`) suggests
`PER_WORKER_GB = 1.2` is still adequate but conservative; lowering `RESERVE_GB`/PER_WORKER_GB would let n=2 start at
about 3.0 GB (1.5 + 2*0.8)... that is a safeguard change and is not recommended or tested here.
