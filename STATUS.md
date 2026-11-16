# Status -- the live board

Only the lead edits this file (E-005). It holds states, not result numbers: every figure lives in a result file.

**Updated:** 2026-11-16 (E-059).

## Phase

**Phase 1** -- families declared and red-teamed (F-02 levels, family B, family O; described readings F-P, RD firms).
The pass line's statistic is `cons` (E-035); no family reads the judged block before its pin, and the first pin
(F-02, k = 11) waits for Q-55's rerun, the fresh-seed validation Q-83 and its seventh text Q-84 (E-052).

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
| wt-verify | wt/wt-verify | Q-82 the pass line's fresh-seed validation | running |
| wt-levels | wt/wt-levels | Q-84 F-02's seventh text (K0, C0, the pin conditions) | running |
| wt-user | wt/wt-user | -- (Q-76 merged, E-059; its identity Q-93 in the chain) | idle |
| wt-features | wt/wt-features | -- (Q-70 merged, E-055; its identities Q-89 in the chain) | idle |
| wt-lit | wt/wt-lit | Q-87 family O's third draft | running |
| wt-firms | wt/wt-firms | Q-91 the firms reading's third draft | running |
| wt-payout | wt/wt-payout | Q-92 F-P's third draft | running |
| wt-report | wt/wt-report | Q-86 money spent and return on spend per start day | running |
| wt-scout | wt/wt-scout | Q-81 family B's sixth draft | running |
| wt-infra | wt/wt-infra | Q-85 the exemption scan checks its row | running |

## Running now

- Heavy, one at a time under `run.lock`, each from a clean checkout: the second leg at c7e01bd (E-041) -- Q-55 (the
  calibration), Q-22b (P-15 through Stage 2's own builder), Q-44 (the readings beside), Q-18, Q-45; then the
  third leg: Q-80 (the re-composed gate's 500-path identities), Q-89 (the place recorder's identities), Q-93 (the
  adapter's class), Q-35
  (where the openings fall); then Q-83
  (the fresh-seed validation F-02's pin needs).
- Light: Q-87 (family O's third draft), Q-86, Q-91, Q-92, Q-81 (family B's sixth draft), Q-84 (F-02's seventh text), Q-85,
  Q-82.

## Machine

Windows 11, 16 GB, the repository on OneDrive. At 2026-11-15 ~21:00 local the machine had about 1.7 GB available and
its commit charge near its limit, held by the operator's other applications. Light work runs; **a heavy run (a
campaign or a full identity, up to about 3 GB) waits for memory** (`docs/OPERATOR_SETUP.md` item 9;
`python scripts/run_lock.py take` refuses a job the machine cannot hold).
