---
name: run-lock
description: Taking, watching and releasing the heavy-run lock -- one heavy run at a time on the machine. Use before anything that reads the full bars, runs the engine beyond a few paths, solves a table or runs a campaign, from any tree.
---

# The run lock (E-005, E-006)

The machine has 16 GB shared with the operator's other applications; a Stage 2 family run peaked near 3 GB. Two heavy
runs at once can swap the machine or fail on the commit limit, and a run that dies half-way leaves nothing usable. So:
**one heavy run at a time, under one lock, watched to its exit.** Light work (reading, code, unit tests on synthetic
data, small checks) never needs the lock and runs in parallel.

**Heavy** = reads the full bars or atlas; runs Stage 2's engine beyond a few paths; solves a state table; runs a
campaign, a family screen or a full identity; anything expected over 1 GB or 15 minutes. **The slow identity tests
count** (E-024): the 4-path / 4-start identities rebuild cells from the full bars and peak at 1.2-1.9 GB, so a worker
runs them only under the lock (`slow` in the suite is not "light"); the fast tier is the only test tier that runs
without it.

## The lock

`run.lock` at the **main** repository's root (`scripts/run_lock.py` finds it from any worktree through
`git rev-parse --git-common-dir`). Git-ignored. JSON: `job`, `task`, `holder`, `start`, `expected_end`,
`mem_gb_needed`, `mem_gb_available_at_start`, `cmd`, `pid`, `log`.

## Take it

```
python scripts/run_lock.py status
python scripts/run_lock.py take --job <job> --task <Q-id> --holder <worktree or session> --hours <expected> --mem-gb <needed> --cmd "<the command>"
```

Exit 0 taken; **3 held** (by whom, since when, until when); **4 memory short** (the available GB and what the job
needs). On 3 or 4 the job does not start: a worker says so in its hand-back; the lead re-queues it. Nobody waits in a
loop holding a session open for a lock.

Set `--hours` honestly (it decides staleness) and `--mem-gb` from a measurement where one exists (a 4-path or
4-start run's peak, scaled), else 3.

## Run it, watched

1. Heavy runs that produce a result run from a clean checkout (`python scripts/run_clean.py --name <job> -- <cmd>`),
   never in a worktree or the main tree; heavy checks that write nothing (an identity) may run in a worktree.
2. Start it in the background, record the process: `python scripts/run_lock.py set-pid --job <job> --pid <pid> --log <log>`.
3. **Watch it to its exit**: a Monitor (or background until-loop) on the log for the `EXIT` line, a failure line
   (`Traceback`, `MemoryError`, `REFUSED`, `FAILS`, `DIFFERS`), and a stall (the log not growing for 20 minutes, or
   for the job's own longest quiet stretch). Threads capped: `OMP_NUM_THREADS` and friends at 1 (the identity) or 2,
   at most 2 workers.

## Release it -- whatever the outcome

```
python scripts/run_lock.py release --job <job>
```

Released on success, on failure and on a kill. The outcome (exit code, time, peak memory if measured, the log's
path) goes in the hand-back; the lead writes it in `PROGRESS.md`. A failed run is kept on record and diagnosed by the
failure protocol before anything is rerun.

## A stale lock

`status` marks a lock **STALE** when the clock is past its expected end plus one hour. Stale is a question, not a
licence: check whether its `pid` is alive (`Get-Process -Id <pid>`) and whether its `log` is still growing. Alive and
growing: it is a slow run -- leave it, tell the lead. Dead: the lead -- only the lead -- releases it with `--force`,
writes what happened in `PROGRESS.md`, and runs the failure protocol on the dead job. **Never steal a lock.**
