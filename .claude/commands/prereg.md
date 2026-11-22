---
description: Draft a family declaration (prereg/F-XX_<slug>.md) from Stage 2's templates, red-team it, then hand it to prereg-gatekeeper
argument-hint: <title>
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell, Agent
---

Draft a new family declaration titled: **$ARGUMENTS**

1. Read `vendor/stage2/prereg/TEMPLATE.md` and `vendor/stage2/prereg/FAMILY_TEMPLATE.md` (read-only), this
   repository's `prereg/F-01_resting_order_level_atlas.md` (the house example), `CHARTER.md` sections 2-4, and the
   decision rows that pin existing families in `DECISIONS.md`.
2. Write `prereg/F-XX_<slug>.md`, where `<slug>` is a short snake_case form of the title. Leave the id as `F-XX` and the
   program family number as `k = ?` -- the gatekeeper assigns both. Adapt the templates as the gatekeeper reads them
   (`.claude/agents/prereg-gatekeeper.md`): the objective is P with the guarded measures and Stage 2 D-621 (3)'s
   selection rule against R\* = P-14 at the family's level 0.05 / (k (k + 1)), with Stage 2's long-run gate as a floor --
   not the template's gate as the pass line. Sections: the hypothesis and its mechanism; the contract fit; the grid
   with every parameter classed **fixed / searched / dropped** and explained in a phrase; `k_cells`; the kill lines
   read before any outcome; the selection rule and its kill lines on outcomes; data, windows (the choice and judged
   blocks as dates) and seeds; **the confirmation window declared now** (NQ from 2026-07-17, a purchase); the
   runner's identity; what a fail means; an empty section for anything chosen later.
3. Fill in only what is already certain: the title, today's date, the task from `TASK_QUEUE.md` it belongs to, and any
   parameter that is genuinely fixed (contract arithmetic, a verified rule, a registered rung). **Leave anything
   undecided visibly blank.** Do not invent a block, a seed or a parameter value to make the file look complete -- the
   gatekeeper will refuse it, and worse, an invented value that survives becomes a rule nobody chose.
4. Tell the caller which sections still need decisions, as a short list. Then run
   `python scripts/decl_lint.py <file>` and fix every error before any review (Q-210; add `--pin` for a draft about to
   be renamed for its pin; warnings are read, never a reason to stop).
5. Invoke the **red-team** agent on the draft, giving it the file and the templates -- not your expectation of what it
   will find. Pass its findings on unedited. **In the same step, invoke the prereg-gatekeeper for a form read of the
   same draft** (E-274): its template, counting, pin-grammar and wording items, returned as a numbered list, approving
   nothing. Both lists go to the author in one cycle, so a form refusal no longer costs a cycle after the red team's
   (H3 lost one this way on 2026-11-22). The gatekeeper does not see the red team's findings in this read, so the two
   stay independent.
6. Invoke the **prereg-gatekeeper** agent on the corrected draft with the red-team's findings, for its approval. Report its verdict verbatim: on
   approval, the assigned F-id, the family's k and level, the sha256 of the file's LF text and the proposed pinning row
   (one finished line, for the lead to number and append with `/decide`); on refusal, the numbered list of what is
   missing.

A refusal on a first draft is the normal outcome, not a problem to work around. Nothing of the family is built, and no
bar is read for it, until the lead has committed the pinning row; from then on the file is never edited (a change is
a new family, `tests/test_declarations_fixed.py`).
