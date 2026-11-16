# Status -- the live board

Only the lead edits this file (E-005). It holds states, not result numbers: every figure lives in a result file.

**Updated:** 2026-11-15 (session 2, the bootstrap's Part 7).

## Phase

**Phase 0** -- setup and the research-structure audit (bootstrap Part 4). No model family runs until the audit gate
(TASK_QUEUE Q-08) is passed.

## The identity (refusing: nothing of this repository is believed until it holds)

| identity | state | row |
|---|---|---|
| P-14's registered gate paths (500, point and bound, every `PATH_COLS` column to 1e-6) | HOLDS, clean clone of ba2d3b5 | E-004 |
| P-16's registered gate paths (500, same) | HOLDS, clean clone of ba2d3b5 | E-004 |
| U1's start rows for P-14 and P-16 (`user_journey.csv` section `start`, all 1,691 starts, both arms, all 68 columns) | **HOLDS**, wt-verify at 8010969 under the lock | E-010 |
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
| wt-verify | wt/wt-verify | Q-16 the calibrated statistic (`docs/briefs/Q-16_2026-11-15.md`) | running |
| wt-levels | wt/wt-levels | Q-41 the red team's third read of F-02 | running |
| wt-user | wt/wt-user | Q-40 the early-close calendar (readings Q-44/Q-45 are the lead's, under the lock) | running |
| wt-features | wt/wt-features | Q-22 P-15's identity, then Q-18 P-14's stress checks (heavy, under the lock) | running |
| wt-lit | wt/wt-lit | Q-38 family R's draft (resolution forecasts) | running |
| wt-firms | wt/wt-firms | Q-34 strike the material from firms whose terms forbid automated retrieval | running |
| wt-payout | wt/wt-payout | Q-47 the gate rebuilt in `extended/` (another funded-account class) | running |
| wt-report | wt/wt-report | Q-27 the dispersion report | running |
| wt-scout | wt/wt-scout | Q-43 family B's third draft | running |
| wt-infra | wt/wt-infra | Q-32 the judged block's seal (purpose-tagged reader, read ledger) | running |

## Running now

- The four worktree items above; no heavy run (the lock is free).

## Machine

Windows 11, 16 GB, the repository on OneDrive. At 2026-11-15 ~21:00 local the machine had about 1.7 GB available and
its commit charge near its limit, held by the operator's other applications. Light work runs; **a heavy run (a
campaign or a full identity, up to about 3 GB) waits for memory** (`docs/OPERATOR_SETUP.md` item 9;
`python scripts/run_lock.py take` refuses a job the machine cannot hold).
