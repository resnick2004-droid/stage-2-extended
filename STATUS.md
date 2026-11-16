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
| U1's start rows for P-14 and P-16 (`user_journey.csv` section `start`) | **not yet built** (Q-05) | -- |

## NEEDS_OPERATOR

None yet. The audit's findings are pending (Q-06, Q-07).

## The run lock

`run.lock` at the repository root (git-ignored): **free**. One heavy run at a time on the machine.

## Worktrees (`%LOCALAPPDATA%\stage2-extended-wt\`)

| worktree | branch | task | state |
|---|---|---|---|
| wt-verify | wt/wt-verify | -- | not created yet (Q-03) |
| wt-levels | wt/wt-levels | -- | not created yet (Q-03) |
| wt-features | wt/wt-features | -- | not created yet (Q-03) |
| wt-firms | wt/wt-firms | -- | not created yet (Q-03) |
| wt-scout | wt/wt-scout | -- | not created yet (Q-03) |

## Running now

- Q-06: the Phase 0 audit, five read-only agents (tracks A-E), notes to `docs/audits/phase0/`.

## Machine

Windows 11, 16 GB, the repository on OneDrive. At 2026-11-15 ~21:00 local the machine had about 1.7 GB available and
its commit charge near its limit, held by the operator's other applications. Light work runs; **a heavy run (a
campaign or a full identity, up to about 3 GB) waits for memory** (`docs/OPERATOR_SETUP.md` item 8).
