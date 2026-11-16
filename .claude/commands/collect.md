---
description: Bring a finished clean run home -- its result files, the variants ledger, the report -- then free the lock and the checkout (the lead only)
argument-hint: <run name, as given to scripts/run_clean.py --name>
allowed-tools: Read, Write, Edit, Bash, PowerShell, Grep, Glob, Agent
---

Collect the clean run **$ARGUMENTS** (the lead only).

1. **It finished.** Read `%LOCALAPPDATA%\stage2-extended-runs\<name>.log` to its end: the `EXIT` line and its code;
   any `Traceback`, `MemoryError`, `REFUSED`, `FAILS` or `DIFFERS` line. A non-zero exit or a failure line is not
   collected: it is kept on record, written in `PROGRESS.md`, and diagnosed by the failure protocol (terminal states
   -> stage decomposition -> component in isolation -> replication with seeds fixed beforehand). Never rerun until it
   passes.
2. **Bring the files home.** `python scripts/run_clean.py --name <name> --collect` copies every file the run created or
   changed into this tree, and refuses a file this tree changed since the run's commit.
3. **Check each result.** For every new `results/*.csv`: `extended.results.verify_result` passes; the manifest's
   `git_commit` is the run's commit and not `-dirty`; its seed and parameters are the declaration's; `exploratory` is
   set as the declaration says; its `variant_count` is present.
4. **The variants ledger.** Union the run's variant entries into `results/variants.jsonl` (append new entries only,
   never rewrite; a duplicate is dropped by its key) and check the family's count against its declaration.
5. **The report.** Rebuild whatever reads these files (`python scripts/build_report.py` once it exists, else say
   "report not built"), then `python scripts/trace_check.py` -- "NOT CHECKED" is not a pass.
6. **The audit.** For a result that decides anything (a kill line, a pick, a judgement, a verdict), the `auditor`
   re-derives its headline numbers from the CSV before the reading's row is written.
7. **Record and free.** The reading's decision row (citing the file and sections; no typed number the trace check
   cannot recompute); commit the result files with their manifests, the ledger and the row together; push;
   `python scripts/run_lock.py release --job <name>` if the lock is still held for it; then
   `python scripts/run_clean.py --name <name> --remove` (junctions unlinked first). Update `STATUS.md`,
   `TASK_QUEUE.md`, `PROGRESS.md`.
