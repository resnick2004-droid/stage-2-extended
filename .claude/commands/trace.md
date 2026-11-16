---
description: Run the trace check -- every number in a document must trace to a result file with a manifest
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Edit, Agent
---

Run the trace check.

1. Run it directly first: `python scripts/trace_check.py`. If the script does not exist yet (TASK_QUEUE Q-04 builds it),
   the verdict is **NOT CHECKED (the trace check is not built)** -- say so and go on to step 2 for the sweep by hand.
2. Invoke the **results-tracer** agent for the full sweep -- untraced numbers in documents, stale numbers, manifest
   problems, unlabelled exploratory citations, P reported without its guarded measures, frontier or gate floor, growth
   figures without ruin, drawdown and latency beside them, and money figures from the point rather than the bound.
3. Report the verdict as one of:
   - **PASS** -- every registered number recomputes and appears where it is cited;
   - **FAIL** -- with each finding and the document it is in;
   - **NOT CHECKED** -- nothing is registered yet, or the check is not built.

**"NOT CHECKED" is not a pass.** If result files exist in `results/` and are cited in documents but nothing is
registered, say so and list which numbers should be registered -- a green trace check that checked nothing is worse
than no check, because it will be believed.

Fix findings by regenerating the result (a new file, from a clean checkout) or correcting the document, never by editing
a result CSV (a hook refuses it) and never by relaxing a check. Pass on the tracer's proposed decision row, if any, for
the lead.
