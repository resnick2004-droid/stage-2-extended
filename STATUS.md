# Status -- the live board

Only the lead edits this file (E-005). It holds states, not result numbers: every figure lives in a result file.

**Updated:** 2026-11-28 (E-301). Live board: `python scripts/status.py` (the queue, the run lock, the worktrees, the result files with their manifest check, the last test run). Held: H4-B's outputs until Q-188b closes (E-289); H3-A until Q-216 and its review (E-290). Next k = 13; search years 2020-01-02 to 2023-12-29; the held-out years unread by any design search; NQ from 2026-07-17 unread (a purchase).

## Phase

The journey objective (CHARTER 2, E-210): H4 re-baselines the four baselines on the search years; W42-R2, pinned (E-299), sets the limits from them (Q-189); F-13, the first Topstep design search, is drafted (Q-214), its scope frozen (E-294); its survey follows (Q-215, Q-190; the route in its last corrective cycle, E-301). H4-B: P-15's parts run here, the naive coin's and P-16's on the Mac (qualified by an exact slice, its agent merged, E-301). F-03 closed (k = 12 spent).

## The identity (refusing: nothing of this repository is believed until it holds)

| identity | state | row |
|---|---|---|
| P-14's registered gate paths (500, point and bound, every `PATH_COLS` column to 1e-6) | HOLDS, clean clone of ba2d3b5 | E-004 |
| P-16's registered gate paths (500, same) | HOLDS, clean clone of ba2d3b5 | E-004 |
| U1's start rows for P-14 and P-16 (`user_journey.csv` section `start`, all 1,691 starts, both arms, all 68 columns) | **HOLDS**, wt-verify at 8010969 under the lock | E-010 |
| U1's start rows for P-15 (every start) | **HOLDS**, clean checkout of 1d1ab9f under the lock | E-042 |
| the gate rebuilt in `extended/` against P-14's and P-16's gate runs (500 paths, both shifts, no class and pass-through) | **HOLDS**, clean checkout of 6325e09 under the lock | E-044 |
| the walker against P-16's pinned trades (`TRADES_SHA256`, all 239,768 trades) | **HOLDS** (the lead, under the lock, wt-levels at 318d45b) | E-011 |

## NEEDS_OPERATOR

**Answered 2026-11-15 (E-008):** new designs are judged on their trades first (lift over the coin twin, calibrated),
the user scorecard beside against P-14; the verdict keeps 0 % denial with the placement off; hand entry only stays.

**Answered 2026-11-15 (E-013):** Terms of Use s.8 is priced as a risk (tier 3, the denial ladder beside); the breakeven move is allowed as made (its modelling fixed in Q-20).

**Answered 2026-11-16 (E-023):** levers that add no trades are described, never carried; filters that keep the coin's side are tested against a random filter of the same size.

**Open:** none.

**The gate (E-008):** families may be declared (next k = 13 (E-192)) and built; no judged-block read until the U1 identity holds
(Q-05) and the calibrated statistic exists (Q-16). Safe defaults stand (E-007): F-01 withdrawn; `or30` out; the
signal-service purpose dropped; report-day entries after 07:35:00 CT.

## The run lock, the worktrees, running jobs, the machine

Read live from `python scripts/status.py` and `python scripts/run_lock.py status` (E-293); this board no longer copies them.
