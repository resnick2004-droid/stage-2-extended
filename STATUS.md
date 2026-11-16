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
| wt-verify | wt/wt-verify | Q-55 the calibration's clean-run entry point | running |
| wt-levels | wt/wt-levels | Q-53 F-02's final red-team read | running |
| wt-user | wt/wt-user | -- (Q-40 done, E-029) | idle |
| wt-features | wt/wt-features | Q-61 the snapshot extended with six result files | running |
| wt-lit | wt/wt-lit | Q-60 the red team on family O | running |
| wt-firms | wt/wt-firms | Q-59 DayTraders' and TradeDay's remaining rules | running |
| wt-payout | wt/wt-payout | -- (Q-54 drafted, E-038) | idle |
| wt-report | wt/wt-report | -- (Q-27 done, E-027; the page for Q-17's file waits for Q-44) | idle |
| wt-scout | wt/wt-scout | Q-62 the red team's fourth read of family B | running |
| wt-infra | wt/wt-infra | -- (Q-58 done, E-041) | idle |

## Running now

- Q-16's calibration holds the lock (wt-verify). After it, the heavy chain (E-028 (3)): Q-22 every start, Q-51, Q-44, Q-18, Q-45, Q-46, each from a clean checkout of master.
- Light: Q-43 (family B's third draft), Q-50 (F-02's fourth draft), Q-40 (the calendar), Q-48 (identities through the reader), Q-39 (rules readings).

## Machine

Windows 11, 16 GB, the repository on OneDrive. At 2026-11-15 ~21:00 local the machine had about 1.7 GB available and
its commit charge near its limit, held by the operator's other applications. Light work runs; **a heavy run (a
campaign or a full identity, up to about 3 GB) waits for memory** (`docs/OPERATOR_SETUP.md` item 9;
`python scripts/run_lock.py take` refuses a job the machine cannot hold).
