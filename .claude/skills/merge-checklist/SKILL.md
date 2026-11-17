---
name: merge-checklist
description: What the lead checks before merging a worker's branch into master, with the commands. Use on every hand-back before `git merge`.
---

# The merge checklist (DIRECTIVE Part 5 step 2; E-006)

The lead merges nothing it has not checked. Each line is checked by looking, not by the hand-back's word. A line that
fails sends the branch back with the reason (one corrective cycle of the two allowed) or, if the defect is in a
result, into the failure protocol.

Let `B=wt/<name>` and `W=%LOCALAPPDATA%\stage2-extended-wt\<name>`.

## 1. What changed

```
git log --oneline master..$B
git diff --stat master...$B
git diff --name-only master...$B -- vendor/            # must be empty
git diff --name-only master...$B -- results/           # must be empty (results arrive only by /collect)
git diff --name-only master...$B -- DECISIONS.md STATUS.md TASK_QUEUE.md PROGRESS.md   # must be empty
git diff --name-only master...$B -- prereg/            # only a new draft the brief asked for; a pinned F-file never changes
```

- [ ] the commits match the hand-back; nothing outside the brief's scope
- [ ] **no vendored file changed**, and no engine pin (`vendor/MANIFEST_stage2.sha256`, `vendor/STAGE2_SOURCE.json`,
      `scripts/vendor_stage2.py`'s `COMMIT`) changed without a decision row naming it
- [ ] no result file written on the branch; no record file edited
- [ ] no pinned declaration edited (`tests/test_declarations_fixed.py`)

## 2. It came in the right order

- [ ] the declaration or decision row the item builds on exists on `master` and its commit is **older** than the
      branch's first commit (`git merge-base --is-ancestor <row commit> <branch's first commit>`)
- [ ] a new declaration has had the `red-team` review (`docs/reviews/`) before it is pinned; its findings answered

## 3. It works

```
cd $W && timeout 1200 python -m pytest -q -o addopts= -m "not heavy"      # the suite, the identity at 4 paths included
cd $W && python scripts/vendor_stage2.py --verify
```

- [ ] the tests pass in the worktree, with a time limit, and the count matches the hand-back
- [ ] the tests the item needs exist and assert the right thing (read them: a test that cannot fail is no test)
- [ ] **the identities hold** on the branch (E-002's gate rows at 4 paths in the suite; U1's start rows once Q-05
      lands); a branch that touches anything the engine or a walker uses runs them again

## 4. It does not lie

- [ ] **no figure typed** into a document: `git diff master...$B -- '*.md'` read for result-shaped numbers; every one
      is a rule value with its article, a date, a seed, a declared parameter, or computed from a result file
- [ ] for code that reads bars or builds features or labels (skill `feature-rules`): every feature reads bars closed
      at or before the alert only, with a **shift-invariance test**; entries at `t + 5` or later; limit fills need a
      trade-through; stop first on two-barrier bars; splits purged and embargoed longer than the longest trade
- [ ] randomness takes explicit seeds fixed in the declaration or the brief
- [ ] nothing reads NQ from 2026-07-17
- [ ] anything chosen after an outcome is labelled exploratory
- [ ] no result file reveals a licensed price (`tests/test_results_no_price_levels.py`; the pre-commit hook runs it on the commit's index)

## 5. Results that matter (a reading, after `/collect`)

- [ ] the run came from a clean detached checkout of a committed commit; the manifest's `git_commit` is that commit,
      not `-dirty`; `extended.results.verify_result` passes
- [ ] the variant count is in the manifest and the variants ledger
- [ ] the `auditor` re-derived the headline numbers from the CSV without the producing code; its note is in
      `docs/audits/`
- [ ] the reading's decision row cites the file and its sections, and types no number that the trace check cannot
      recompute

## 6. Merge

```
git merge --no-ff $B -m "Q-xx: <what> (E-nnn)"
python -m pytest -q -o addopts= -m "not slow and not heavy"
```

Then: append the decision row (numbered by the lead), update `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`; commit;
push (the post-commit hook does it); `python scripts/worktrees.py sync <each other worktree>`; dispatch the next item.
