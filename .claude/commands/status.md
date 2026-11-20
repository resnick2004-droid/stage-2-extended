---
description: Print the repository's status -- the queue, declared searches and their rounds, the baselines, the held-out read ledger, rules, result files, the identity, the run lock, the last test run
allowed-tools: Read, Bash, PowerShell, Glob, Grep
---

Print the repository's status.

Run `python scripts/status.py` (TASK_QUEUE Q-04 builds it). It reports:

- **The queue** from `TASK_QUEUE.md` -- every item not `done`, in rank order, with its owner worktree, state,
  dependencies, weight and retries; anything `blocked` or `NEEDS_OPERATOR` first.
- **Declared searches** -- every `prereg/F-*.md` and `prereg/RD-*.md`, whether its pinned sha256 in `DECISIONS.md`
  still matches (`tests/test_declarations_fixed.py`), its k (assigned at its held-out row, E-204, or "not yet"), and
  whether its outcome has a decision row yet; the program's running count (k = 13 next).
- **The search rounds** -- for each pinned design search: where it stands in its run order (the pinning row, the
  calibration and power gate, the pin, the survey, round r of R, the finalists' row, the held-out row, the held-out
  test, the verdict), the designs tried so far against its declared count, read from `results/variants.jsonl` (rows
  whose `prereg_id` is the search's) and the rounds' result files with their manifests; the finalists, if pinned, in
  their order. Never a held-out figure: the held-out test's result is reported only after its verdict row.
- **The baselines** -- naive coin, P-14, P-15, P-16 (and each other firm's declared set): whether each runs under the
  design's convention, its runner identity's state on the board (`STATUS.md`), and its re-baseline (H4, search years
  only) result file, if written, with its manifest's status. Report the file, not its numbers.
- **The held-out read ledger** -- the entries CHARTER 3.6 (b) lists and every later row's additions (grep
  `DECISIONS.md` for "held-out read ledger"), with whether the first held-out test on NQ is spent (O-1) and whether
  the level would print nominal.
- **Rules** -- Stage 2's ledger (`vendor/stage2/config/rules.yaml`): the verified count and every rule not verified; and
  this repository's record (`config/rules_extended.yaml`): every entry with its status, any `changed` or `unverified`
  first, and whether `docs/RULES_CURRENCY.md` agrees with it row for row.
- **Result files** of `results/` with their manifest verification status (`extended.results.list_results`); any `-dirty`
  commit.
- **The identity** -- the board's state (`STATUS.md`) for P-14's and P-16's gate rows and U1's start rows.
- **The operator's open items** -- any NEEDS_OPERATOR on the board, each with its state (O-1 and O-3 to O-7 ruled at
  E-221; the data purchase held).
- **The run lock** -- `run.lock` at the repository root: free, or its holder, job, start and expected end (stale if older
  than its expected end plus an hour: investigated, never stolen).
- **Last test run** from `results/.last_test_run.json`, written by the post-edit test hook (the edited file's tests and the two foundation checks, Q-147; not the fast tier).
- **The closing checklist** (`TASK_QUEUE.md`, CHARTER section 5).

If `scripts/status.py` does not exist yet, or does not report a part (it does not yet report the search rounds, the
baselines or the ledger), read the same sources directly and say which part the script does not build.

Then add a short read of it in your own words:

1. The **next action**, given that the queue is ranked so that work which can cancel later work comes first.
2. Any **blocker** -- an unverified rule the next item needs, missing data, a failing test, the identity not yet
   complete, a stale run lock, a result whose manifest does not verify.
3. If a result file's manifest fails to verify, or a pinned declaration no longer matches its hash, say so first: an
   edited result is not evidence, and an edited declaration is not a declaration.

Keep it short. Read-only: this command writes nothing (only the lead edits `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`).
