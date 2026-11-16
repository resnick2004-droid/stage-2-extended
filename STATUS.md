# Status -- the live board

Only the lead edits this file (E-005). It holds states, not result numbers: every figure lives in a result file.

**Updated:** 2026-11-16 (E-045).

## Phase

**Phase 1** -- families declared and red-teamed (F-02 levels, family B, family O; described readings F-P, RD firms).
The pass line's statistic is `cons` (E-035); no family reads the judged block before its pin, and the first pin
(F-02, k = 11) waits for its sixth draft (Q-72) and Q-55's clean rerun of the calibration.

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

**The gate (E-008):** families may be declared (next k = 11) and built; no judged-block read until the U1 identity holds
(Q-05) and the calibrated statistic exists (Q-16). Safe defaults stand (E-007): F-01 withdrawn; `or30` out; the
signal-service purpose dropped; report-day entries after 07:35:00 CT.

## The run lock

`run.lock` at the repository root (git-ignored): **free**. One heavy run at a time on the machine.

## Worktrees (`%LOCALAPPDATA%\stage2-extended-wt\`)

| worktree | branch | task | state |
|---|---|---|---|
| wt-verify | wt/wt-verify | Q-68 a red-team read of the pass-line code | running |
| wt-levels | wt/wt-levels | Q-72 F-02's sixth draft (the gatekeeper's four gaps) | running |
| wt-user | wt/wt-user | Q-35's script | running |
| wt-features | wt/wt-features | Q-70 the place-recording adapter | running |
| wt-lit | wt/wt-lit | Q-63 family O's second draft | running |
| wt-firms | wt/wt-firms | Q-73 the FOMC-minutes dates (a scout) | running |
| wt-payout | wt/wt-payout | Q-71 the RD firms gate seam | running |
| wt-report | wt/wt-report | Q-69 the scorecard page for Q-44's file | running |
| wt-scout | wt/wt-scout | Q-65 family B's fifth draft | running |
| wt-infra | wt/wt-infra | Q-67 the ledger's union on collection, then Q-74 the reader's RD- files | running |

## Running now

- Heavy, one at a time under `run.lock`, each from a clean checkout: the second leg at c7e01bd (E-041) -- Q-55 (the
  calibration), Q-22b (P-15 through Stage 2's own builder), Q-44 (the readings beside), Q-18, Q-45.
- Light: Q-63 (family O's second draft), Q-65 (family B's fifth draft), Q-72 (F-02's sixth draft), Q-67 then Q-74,
  Q-68, Q-69, Q-70, Q-71, Q-73, Q-35's script.

## Machine

Windows 11, 16 GB, the repository on OneDrive. At 2026-11-15 ~21:00 local the machine had about 1.7 GB available and
its commit charge near its limit, held by the operator's other applications. Light work runs; **a heavy run (a
campaign or a full identity, up to about 3 GB) waits for memory** (`docs/OPERATOR_SETUP.md` item 9;
`python scripts/run_lock.py take` refuses a job the machine cannot hold).
