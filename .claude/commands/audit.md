---
description: Independently audit a result file of this repository
argument-hint: <result file, e.g. results/<family>_<stage>.csv>
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Write, Agent
---

Audit this result: **$ARGUMENTS**

1. Confirm the file exists in `results/` and has a sidecar `<file>.manifest.json`. If the manifest is missing, stop and
   report that -- a result without provenance cannot be audited or cited, and the fix is to regenerate it through
   `extended.results.write_result` from a clean checkout, not to write a manifest by hand.
2. Invoke the **auditor** agent on the file. Give it the file and the declaration it names -- not the conclusion you
   expect.
3. Report its verdict: **clean**, **clean with caveats**, or **defects found** -- with the findings ordered most serious
   first, and the path of the note it wrote to `docs/audits/<result-stem>_<YYYY-MM-DD>.md`.
4. Report, explicitly, **what the auditor could not verify**. That list is often the most useful part.
5. Pass on its proposed decision row (one finished line) for the lead to number and append with `/decide`.

The auditor re-derives the numbers from the CSV **without** the code that produced them. Do not shortcut this by
re-running the producing script and comparing -- that confirms determinism, not correctness. It re-derives the journey
measures from their definitions in `docs/MEASURES.md`, and judges the result against this repository's charter as
E-210 put it in force: the martingale-outcome reading, the limits, each baseline beaten on the pinned composite by the
three-way test run as declared, the floors (CHARTER 3.8); and it lists every held-out read for the ledger.

The auditor does not fix anything. If it finds defects, the lead decides what to do and records it with `/decide`.
