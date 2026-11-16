---
description: The lead appends one numbered, dated E-row to DECISIONS.md (never edits an existing row)
argument-hint: <the decision, and its basis -- or a worker's proposed row to number>
allowed-tools: Read, Edit
---

Append a decision to `DECISIONS.md`: **$ARGUMENTS**

**The lead's command.** Only the lead, on `master`, appends to `DECISIONS.md` (the single-writer rule, E-005). In a
worktree or as a worker, do not run this: end the hand-back with the proposed row as one finished line
`| E-NNN | <date> | **<decision>** ... | <basis> |` and stop. (A hook warns on any write to a `DECISIONS.md` inside a
worktree.)

1. Read `DECISIONS.md` and find the highest existing `E-nnn`.
2. Append **one new row** at the end of the table, numbered `E-<next>` (three digits), dated today:

   `| E-nnn | YYYY-MM-DD | **<decision>** <detail> | <basis> |`

   Anchor the edit on the current last row and keep that row verbatim in the replacement, so nothing existing changes
   (the hook stays silent on an append made that way). A worker's proposed row keeps its text; only `E-NNN` and, if
   needed, the date are filled in.
3. Write the decision as a decision -- what will now be done or not done -- and the basis as the evidence it rests on:
   a result file with its manifest, a pinned declaration and its sha256, a Stage 2 row (`Stage 2 D-nnn`), a stage-one
   row (`propsim D-xx`), a verified rule with its article id and date, or the operator's instruction. A basis of "seems
   better" is not a basis; ask what the evidence is. No result number typed in: name the file it is computed from.
4. If it reverses, corrects or supersedes an earlier row, **cite the old number** in the new row. Do not edit, reword
   or delete the old row.
5. A row that pins a family must hold the exact pattern `` `prereg/F-NN_<slug>.md` sha256 `<64 hex>` `` that
   `tests/test_declarations_fixed.py` reads; run that test after appending.

**Never modify an existing row.** The log's value is that it records what was believed at the time; a corrected row is
a lost record. A hook warns if an existing row changes.

Report the row you added.
