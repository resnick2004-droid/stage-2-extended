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
- [ ] a new declaration has had the `red-team` review (`docs/reviews/`) and, for a design search, the `scout`'s
      challenger brief (Q-150) before it is pinned; its findings answered
- [ ] **the review rule** (E-207 (2)): every red-team finding is labelled **blocking** (it could make a result wrong:
  leakage, look-ahead, selection after the fact, peak-picking, seed reuse, unpaired luck, a limit set after a result,
  miscounted tests) or **minor**. A branch answering a blocking finding goes back to the red team for
  **a full re-read** of the corrected text before it merges; a branch answering only minor findings is checked by
  reading its **diff** against each finding (`git diff <reviewed commit>..$B -- <files>`), with no new round
- [ ] the hand-back shows the worker's pre-hand-back checklist (skill `worker-protocol`, section 3a), each line
      answered

## 3. It works

```
python scripts/check_verdicts.py master..wt/<name>                        # the tip's fast-tier verdict covers "not slow and not heavy"
cd $W && timeout 1800 python -m pytest -q -o addopts= -m "slow and not heavy"   # only what the hook does not run: the identity at 4 paths and the other slow tests (E-274)
cd $W && python scripts/vendor_stage2.py --verify
```

The fast part of the suite is not rerun at merge when the tip's verdict names the tip's exact commit and the worktree
is clean (E-274: it ran the same tests on the same bytes, about 49 minutes duplicated per merge); a tip with no passing
verdict of its own runs the whole `-m "not heavy"` suite here as before.

- [ ] the tests pass in the worktree, with a time limit, and the count matches the hand-back
- [ ] the tests the item needs exist and assert the right thing (read them: a test that cannot fail is no test)
- [ ] **every commit of the branch has a fast-tier verdict** (Q-161, E-223): `python scripts/check_verdicts.py
  master..wt/<name>` exits 0; a listed commit (`--no-verify`, a rebase, a killed hook, or one made before the hooks of
  a3db3aa were installed) is covered by a verdict at the branch tip or rerun through the fast tier there, and named in
  the row -- otherwise the branch is not merged
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
  at or before the alert only, with a **shift-invariance test**; entries at `t + L` or later (L declared: 5, or a
  counted 3 or 2, E-202); limit fills need a trade-through; stop first on two-barrier bars; splits purged and
  embargoed longer than the longest trade
- [ ] randomness takes explicit seeds fixed in the declaration or the brief
- [ ] nothing reads NQ from 2026-07-17
- [ ] anything chosen after an outcome is labelled exploratory
- [ ] no result file reveals a licensed price (`tests/test_results_no_price_levels.py`; the pre-commit hook runs it on
  the commit's index)
- [ ] **every journey measure is traced to `docs/MEASURES.md`**: the code computing it is the function that file names
      (or the file is amended first, under its own red-team read); its horizon, start set `E_h`, censoring and
      never-blank form as written there; a measure the file does not define is not merged
- [ ] **seeds paired**: a design and every baseline it is compared with read the same coin-field keys on the same start
      days (`E_h`), under the same convention (the reflection, the martingale-outcome redraw against the nearer
      barrier, the fill and cost mechanics); a test shows a comparison is paired, not two independent runs
- [ ] **the held-out years unread by any search code**: nothing that chooses, fits, ranges, caps, weights or surveys
      (the lever loader, the sampler, the surrogate, the round proposer, H4) can open a session from 2024-01-02 on --
      its runner refuses one, with a test that the refusal fires; the horizon embargo asserted (no start reads past its
      own years); nothing written to `results/variants.jsonl` or the lever map from a held-out read
- [ ] the redraw, where the branch builds or touches it: the race against the nearer barrier net of the
  stop-side exit cost -- the loss barrier L = min(l, c - x_stop), fractional, never rounded (E-237), so a
  cushion-bound loss ends on the floor and the engine's clip never binds (`adapter.BinaryDraw` is only its cost-free
  case); an exact-fraction test over fractional cushions and unequal exit costs showing gross zero, net = -(costs) and
  no exit past the floor; R-10's stopped walk on the floor-side barrier L_race with its two-point last sub-step, the
  flatten clip counted, and every terminal state mapped; L_fill = min(l, c - max(x_stop, x_flat)), the fill's decision
  (x_flat the flatten-side exit cost): L_fill <= 0 where the floor binds fails the account at the fill,
  where the daily loss limit binds the day stops; a trade sized to zero contracts at a positive room ends the account
  out of room, failed and counted apart (C-1, Stage 2 D-318, D-335); the lattice step per trade,
  s = max(1, ceil(sigma sqrt(T) / sqrt(`WALK_MAX`))) ticks, from sigma, T and `WALK_MAX` and nothing else, never
  required to divide the stop or the target, a trade never refused for its step (M-3); a redrawn loss with the run's
  stop-fill convention (m-3); overlapping positions refused until defined (m-2); the pair rule's settlement where a
  resting entry meets its reflection

## 5. Results that matter (a reading, after `/collect`)

- [ ] the run came from a clean detached checkout of a committed commit; the manifest's `git_commit` is that commit,
      not `-dirty`; `extended.results.verify_result` passes
- [ ] the variant count is in the manifest and the variants ledger; a held-out reading writes no ledger row a later
      search can read
- [ ] every held-out read the result made is listed for the held-out read ledger (the auditor's item 6)
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
