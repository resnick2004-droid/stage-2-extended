---
name: worker-protocol
description: How a worker receives a brief, what it may touch, how it works in its worktree, and the hand-back format. Use when dispatching a worker (lead) or working as one (worker-builder, scout, red-team).
---

# The worker protocol (E-006)

The lead runs the loop on `master`; workers build in worktrees. This is the contract between them. It exists so that
many sessions can work at once without any of them writing the record, merging unchecked work, or spending the
machine's memory twice.

## 1. The brief (the lead writes it; `/dispatch` sends it)

A brief is complete and self-contained -- the worker knows nothing else. It has these fields, every one filled:

| field | what |
|---|---|
| task | the TASK_QUEUE id and one sentence |
| worktree | `%LOCALAPPDATA%\stage2-extended-wt\<name>`, branch `wt/<name>`, the commit it starts from |
| goal | what "done" means, testably |
| rows to read | the decision rows and the declaration (`prereg/F-xx_*.md`) that govern the item |
| files to start from | paths, with what each is for |
| out of scope | what must not be built or read (always: outcomes not named; the confirmation window) |
| weight | light, or heavy with the run lock's job name and expected duration and memory |
| limits | DIRECTIVE Part 1, by reference, plus anything item-specific |
| hand-back | the format in section 4 |

The lead saves each brief as `docs/briefs/<Q-id>_<YYYY-MM-DD>.md` on `master` when it dispatches it.

## 2. What a worker may touch

| may | may not |
|---|---|
| files in its own worktree, on its branch | the main tree, another worktree, another branch, `master` |
| new code in this repository's package and `scripts/`, `tests/`, `identity/` | anything under `vendor/` (any tree) |
| a draft declaration file, if the brief asks for one (never pinned by the worker) | an existing `prereg/F-xx_*.md` (pinned: a change is a new family) |
| temporary output in a temp folder | `results/` (results come only from a clean run), `DECISIONS.md`, `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md` |
| the bars and atlas through the worktree's junctions, read-only, **if the brief allows heavy work** | a copy of the bars or atlas; any write through a junction |

## 3. How a worker works

1. Read the brief, the rows it names, `CLAUDE.md`, and the skills it names (always `feature-rules` for anything that
   touches bars, features or labels). If something in the brief contradicts a declaration or a rule, stop and say so:
   the declaration wins.
2. Tests first; then the code; then the tests again, with a time limit (`timeout 900 python -m pytest -q ...`).
3. Light work runs freely. Heavy work takes the run lock (skill `run-lock`) after checking memory, is watched to its
   exit, and releases the lock whatever the outcome.
4. Commit on the branch with a message `Q-xx: <what>` and the attribution line; small commits; **never `--no-verify`,
   for any reason** (E-060): if memory is short for the hook's fast tier, wait (`python scripts/run_lock.py status`
   shows what is free) and commit when it can run. The post-commit hook pushes the branch to the private remote.
5. Two corrective cycles at most on one failure (diagnosed by the failure protocol). A third is the lead's decision:
   stop and hand back.

## 4. The hand-back (the worker's final reply)

1. Branch, commits (hash + one line each), files changed.
2. Tests: each one's assertion, the command, the result with counts and time.
3. Identities: which registered file, which columns, how many paths or starts, the tolerance, held or not.
4. **Every interpretation made** where the brief or declaration was silent or ambiguous.
5. Timings and peak memory of heavy work; the lock's take and release times.
6. Not done, and why; anything the lead should know.
7. The proposed decision row, one finished line `| E-NNN | <date> | **...** | <basis> |`.

## 5. What the lead does with it

The skill `merge-checklist`: reads the diff, reruns the tests, checks the identities, sends declarations to the red
team and results that matter to the auditor, then merges with `--no-ff`, numbers and commits the row, updates
STATUS / TASK_QUEUE / PROGRESS, pushes, and fast-forwards the other worktrees (`python scripts/worktrees.py sync`).
