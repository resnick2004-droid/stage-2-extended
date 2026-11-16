---
description: Create or refresh a worktree and start a worker on a TASK_QUEUE item (the lead only)
argument-hint: <worktree name> <Q-id>
allowed-tools: Read, Write, Edit, Bash, PowerShell, Grep, Glob, Agent
---

Dispatch: **$ARGUMENTS** (the lead only -- skill `worker-protocol`).

1. **The item.** Read its row in `TASK_QUEUE.md`. Refuse (and say why) if its state is not `queued`, a dependency is
   not `done`, or it is a model family and the audit gate (Q-08) has not passed. Read the decision rows and the
   declaration it builds on.
2. **The weight.** Heavy: `python scripts/run_lock.py status` -- if the lock is held or memory is short, the item
   stays queued (light work may still go). The worker takes the lock itself, at the moment it runs the heavy part.
3. **The worktree.** `python scripts/worktrees.py list`; then `create <name>` if it does not exist, else
   `sync <name>` (fast-forward to `master`; refused if the branch holds unmerged commits -- collect and merge those
   first, or carry on on top of them if the brief says so). Confirm it is clean and its junctions are in place.
4. **The brief.** Write it from the template in `worker-protocol` section 1 -- every field filled, the hand-back
   format included, nothing assumed known -- to `docs/briefs/<Q-id>_<YYYY-MM-DD>.md`.
5. **Start the worker** with the Agent tool in the background: the `worker-builder` agent (or, in a session that has
   not loaded it, `general-purpose` given the text of `.claude/agents/worker-builder.md` followed by the brief). A
   review goes to `red-team`, a reading-only question to `scout`.
6. **Record:** the item `running` with its worktree in `TASK_QUEUE.md`; the worktree's row in `STATUS.md`; one line
   in `PROGRESS.md`. Commit the brief and the records together; push.

Never dispatch two heavy items at once, never give a worker a task whose declaration is not pinned, and never brief a
worker to read an outcome its declaration does not name.
