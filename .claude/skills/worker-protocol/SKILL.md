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
2. Tests first; then the code; then the tests again, with a time limit. **Before committing, run your own tests and
   the files your change can reach, never the whole fast tier by hand** (E-222): the pre-commit hook runs the whole fast
   tier once, under the machine-wide lock (`scripts/fasttier_lock.py`), and a second, unlocked copy only doubles the
   memory that crashed this machine (Q-155). If you need the whole tier before the hook (a wide change you want to
   diagnose first), run it through the lock: `python scripts/fasttier_lock.py run -- python -m pytest -q -o addopts=
   -m "not slow and not heavy"`. **The fast tier's selection is always
   `-m "not slow and not heavy"`** (the tier takes about 21 minutes on this machine
   under load, E-163; a test killed by the limit prints an `F` that is the limit, not a defect -- run that file alone
   before reporting it) -- `-m "not slow"` does not exclude `heavy`. A test
   marked `heavy` is skipped by the root `conftest.py` whenever `run.lock` is held by another job (Q-118); only the
   command `scripts/run_clean.py` runs under the lock (`S2X_LOCK_HOLDER=<job>`) runs them then. A skip reading "run.lock
   held by ..." is the guard working, not a pass.
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

- **Never wrap `git commit` in `timeout`** (E-222): a killed hook stub let git write a commit without the fast tier's verdict; run the commit in the background and wait for it -- the hook has its own three-hour cap.
- **Never send command output to a generic name in the session scratchpad** (Q-161, E-223): it is one directory for every agent of the session, so two workers' `commit.log` cross; write logs inside your worktree, or under a name that carries the worktree.
- **Never `git stash push` / `pop`** (E-240): the stash stack is shared by every worktree, so a pop can apply another worker's entry. To merge master over staged work, write it to a patch inside your worktree (`git diff --cached --binary > .wip.patch`), `git reset --hard`, `git merge master`, `git apply --index .wip.patch`, then delete the patch; or `h=$(git stash create)` and later `git stash apply --index $h`, which touch no shared stack.
- **One worker per worktree at a time** (E-246): a worktree with a worker in it is not given a second brief, even between that worker's commits; the lead creates a new worktree instead. Two workers in `wt-report` on 2026-11-20 swapped each other's staged files and one commit landed with the other's content.
