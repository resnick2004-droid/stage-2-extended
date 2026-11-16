---
description: Print the repository's status -- the queue, declared families, rules, result files, the identity, the run lock, the last test run
allowed-tools: Read, Bash, PowerShell, Glob, Grep
---

Print the repository's status.

Run `python scripts/status.py` (TASK_QUEUE Q-04 builds it). It reports:

- **The queue** from `TASK_QUEUE.md` -- every item not `done`, in rank order, with its owner worktree, state,
  dependencies, weight and retries; anything `blocked` or `NEEDS_OPERATOR` first.
- **Declared families** -- every `prereg/F-*.md`, whether its pinned sha256 in `DECISIONS.md` still matches
  (`tests/test_declarations_fixed.py`), its program k, and whether its outcome has a decision row yet; the program's
  running family count.
- **Rules** -- Stage 2's ledger (`vendor/stage2/config/rules.yaml`): the verified count and every rule not verified; and
  this repository's record (`config/rules_extended.yaml`): every entry with its status, any `changed` or `unverified`
  first, and whether `docs/RULES_CURRENCY.md` agrees with it row for row.
- **Result files** of `results/` with their manifest verification status (`extended.results.list_results`); any `-dirty`
  commit.
- **The identity** -- the board's state (`STATUS.md`) for P-14's and P-16's gate rows and U1's start rows.
- **The run lock** -- `run.lock` at the repository root: free, or its holder, job, start and expected end (stale if older
  than its expected end plus an hour: investigated, never stolen).
- **Last test run** from `results/.last_test_run.json`, written by the post-edit test hook (the fast tier).
- **The closing checklist** (`TASK_QUEUE.md`, CHARTER section 5).

If `scripts/status.py` does not exist yet, read the same sources directly and say that the script is not built.

Then add a short read of it in your own words:

1. The **next action**, given that the queue is ranked so that work which can cancel later work comes first.
2. Any **blocker** -- an unverified rule the next item needs, missing data, a failing test, the identity not yet
   complete, a stale run lock, a result whose manifest does not verify.
3. If a result file's manifest fails to verify, or a pinned declaration no longer matches its hash, say so first: an
   edited result is not evidence, and an edited declaration is not a declaration.

Keep it short. Read-only: this command writes nothing (only the lead edits `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`).
