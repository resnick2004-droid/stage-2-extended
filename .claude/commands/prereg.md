---
description: Draft a design search's declaration (prereg/DRAFT_F-XX_<slug>.md) from prereg/TEMPLATE_design_search.md, get the scout's challenger brief and the red-team's read, then hand it to prereg-gatekeeper
argument-hint: <title>
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell, Agent
---

Draft a new family declaration titled: **$ARGUMENTS**

1. Read `prereg/TEMPLATE_design_search.md` (the house form from E-210; `prereg/TEMPLATE_family.md` is superseded for
   new work), `CHARTER.md` sections 2-5, `docs/MEASURES.md`, `docs/plans/LEVER_TABLE_topstep50k.md`, the three-way
   test's design note, and the decision rows the search rests on (E-204, E-207, E-208, E-210 and later).
2. Copy the template to `prereg/DRAFT_F-XX_<slug>.md`, where `<slug>` is a short snake_case form of the title. Leave
   the id as `F-XX` -- the gatekeeper assigns the F-number; the k is assigned at the search's held-out row (E-204).
   The objective is the user's journey under zero edge (CHARTER 3.8): on the martingale-outcome reading, inside the
   operator's limits, each baseline beaten on the composite pinned before the survey (or the pinned fallback), by the
   calibrated paired coin-seed test on the held-out years, with the floors. Every lever classed **fixed / searched /
   dropped** and explained in a phrase; the held-out read ledger; seeds by role; **the confirmation window declared
   now** (NQ from 2026-07-17, a purchase); what a fail means; an empty section for anything chosen later.
3. Fill in only what is already certain: the title, today's date, the task from `TASK_QUEUE.md` it belongs to, and any
   parameter that is genuinely fixed (contract arithmetic, a verified rule, a registered rung). **Leave anything
   undecided visibly blank.** Do not invent a block, a seed or a parameter value to make the file look complete -- the
   gatekeeper will refuse it, and worse, an invented value that survives becomes a rule nobody chose.
4. Tell the caller which sections still need decisions, as a short list.
5. Invoke the **scout** agent for its standing challenger brief (Q-150) and the **red-team** agent on the draft, giving
   each the file and the template -- not your expectation of what it will find. Pass their findings on unedited, each
   labelled blocking or minor (E-207 (2)). **In the same step, invoke the prereg-gatekeeper for a form read of the
   same draft** (E-274): its template, counting, pin-grammar and wording items, returned as a numbered list, approving
   nothing. Both lists go to the author in one cycle, so a form refusal no longer costs a cycle after the red team's
   (H3 lost one this way on 2026-11-22). The gatekeeper does not see the red team's findings in this read, so the two
   stay independent.
6. Invoke the **prereg-gatekeeper** agent on the corrected draft with both reads, for its approval. Report its verdict
   verbatim: on approval, the assigned F-id, the sha256 of the file's LF text and the proposed pinning row (a design
   search assigns no k; F-HT's k is assigned at F-HT's held-out row, E-204)
   (one finished line, for the lead to number and append with `/decide`); on refusal, the numbered list of what is
   missing.

A refusal on a first draft is the normal outcome, not a problem to work around. Nothing of the search is built, and no
bar is read for it, until the lead has committed the pinning row; from then on the file is never edited (a change is
a new declaration, `tests/test_declarations_fixed.py`).
