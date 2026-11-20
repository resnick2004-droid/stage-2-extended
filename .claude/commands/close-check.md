---
description: Evaluate every line of the closing checklist (CHARTER section 5, TASK_QUEUE.md) and report which are not yet true
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Agent
---

Evaluate the closing checklist in `TASK_QUEUE.md` against `CHARTER.md` section 5. The repository is closed when every
line is true, **not by judgement** (the rule stage one adopted as propsim D-42). Check each one by actually looking, and
report `TRUE` / `FALSE` / `UNCHECKED` with the evidence.

1. **Tests pass, with the counts recorded.** Run `/validate`'s steps (vendor and data integrity, this repository's suite
   with `-o addopts=`, the identity at 4 paths, the vendored stage-one suite from `vendor/stage2/vendor/propsim` with
   `-p no:cacheprovider`). Report every count, and whether the closing decision row records them.
2. **Every queue item closed or parked with a reason.** Read `TASK_QUEUE.md`: list any item not `done`, and any
   `NEEDS_OPERATOR` without the operator's answer recorded.
3. **Every declared search and family has a recorded outcome.** For each `prereg/F-*.md` pinned in `DECISIONS.md`: a
   later row reading it CARRIED, CLOSED (with the clause that closed it) or withdrawn. One with no outcome row is an
   unreported result. Count the program's k and every design tried (`results/variants.jsonl`) and check the count is
   reported with the last reading.
4. **Every declaration still matches its pin.** `python -m pytest -q tests/test_declarations_fixed.py`.
5. **No unverified rule in use.** Every rule this repository's code loads is `verified` in
   `vendor/stage2/config/rules.yaml`, or `verified` in `config/rules_extended.yaml` with its decision row; list every
   `changed` and `unverified` entry and grep this repository's own code (`extended/`, `scripts/`) for its key. Check
   `config/rules_extended.yaml` and `docs/RULES_CURRENCY.md` agree row for row.
6. **The trace check passes.** Run `/trace`'s check. **"NOT CHECKED" is FALSE, not TRUE.**
7. **Every number in a document traces to a result file with a manifest.** Invoke the **results-tracer** agent for the
   document sweep.
8. **`DECISIONS.md` complete.** Every `E-nnn` present with no gaps; no row edited after it was committed (compare
   against `git log -p DECISIONS.md`); a row for each queue item closed, each family read, each rule whose verified
   value differed from Stage 2's, and each audit.
9. **`vendor/stage2/` unedited and its identity holding.** `python scripts/vendor_stage2.py --verify` and
   `tests/test_vendor_integrity.py`; the identity rows on the board (P-14 and P-16's gate rows, U1's start rows) all
   holding.
10. **The exit criterion is met** (CHARTER section 5). Which outcome: **(A)** a design CARRIED under section 3.8 -- its
    held-out test passed (its level printed nominal if its ledger is not empty, the history-level false-pass rate
    beside) and audited, its playbook written, and its one confirmation read against the criterion declared at its
    registration and reported, with the frontier, every measure of `docs/MEASURES.md` and the rules ledger verified; or
    **(B)** a documented negative result -- no declared search yields a design that passes, with every search's
    evidence, its count and the pass line's power from its power gate. Name it and say where it is written.
    **(B) is a valid close** -- do not report it as incomplete.

Finish with a count, `N of 10 true`, then the list of what is not yet true and what each needs.

Do not mark anything true because it is nearly true, and do not tick a line you could not check -- report it as
`UNCHECKED` and say why. This command's only value is that it refuses to round up. Read-only: it writes nothing.
