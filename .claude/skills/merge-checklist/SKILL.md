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
python scripts/check_verdicts.py master..wt/<name>                        # the tip's fast-tier verdict covers "not slow and not heavy"
cd $W && python identity/stage2_identity.py --paths 4                       # the identity at 4 paths: its tests are marked heavy, so no -m filter runs them (about 75 s; take run.lock)
cd $W && timeout 3600 python -m pytest -q -o addopts= -m "slow and not heavy"   # the other slow tests the hook skips (about 40 tests, over 30 min; E-274)
cd $W && python scripts/vendor_stage2.py --verify
```

The fast part of the suite is not rerun at merge when the tip's verdict names the tip's exact commit and the worktree
is clean (E-274: it ran the same tests on the same bytes, about 49 minutes duplicated per merge); a tip with no passing
verdict of its own runs the whole `-m "not heavy"` suite here as before.

- [ ] the tests pass in the worktree, with a time limit, and the count matches the hand-back
- [ ] the tests the item needs exist and assert the right thing (read them: a test that cannot fail is no test)
- [ ] **every commit of the branch has a fast-tier verdict** (Q-161, E-223): `python scripts/check_verdicts.py master..wt/<name>` exits 0; a listed commit (`--no-verify`, a rebase, a killed hook, or one made before the hooks of a3db3aa were installed) is covered by a verdict at the branch tip or rerun through the fast tier there, and named in the row -- otherwise the branch is not merged
- [ ] **the identities hold** on the branch (E-002's gate rows at 4 paths in the suite; U1's start rows once Q-05
      lands); a branch that touches anything the engine or a walker uses runs them again
- [ ] **the reader holds against the real log** (E-273): on the merge result, before it is committed,
      `timeout 900 python -m pytest -q -o addopts= tests/test_reader*.py tests/test_identity_tokens.py tests/test_declarations_fixed.py`
      passes. A row, a review note or a renamed declaration that breaks the identity tokens, the seed guard or the
      held-out seal is fixed in the merge, never by weakening the check.

## 4. It does not lie

- [ ] **no figure typed** into a document: `git diff master...$B -- '*.md'` read for result-shaped numbers; every one
      is a rule value with its article, a date, a seed, a declared parameter, or computed from a result file
- [ ] for code that reads bars or builds features or labels (skill `feature-rules`): every feature reads bars closed
      at or before the alert only, with a **shift-invariance test**; entries at `t + L` or later (L declared: 5, or a counted 3 or 2, E-202); limit fills need a
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

**One hook run per merge (E-274).** A conflicted merge runs the fast tier, and so does a records commit. When a
branch merges with its own decision row, resolve the conflict and add the row, STATUS, queue and progress lines in the
same merge commit, so the hook runs once. Never ask a worker to commit a conflicted merge of master only to stay current.
A worker merges master once, just before its single commit, and resolves the conflict there.

Then: append the decision row (numbered by the lead), update `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`; commit;
push (the post-commit hook does it); `python scripts/worktrees.py sync <each other worktree>`; dispatch the next item.
