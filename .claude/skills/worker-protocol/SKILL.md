---
name: worker-protocol
description: How a worker receives a brief, what it may touch, how it works in its worktree, and the hand-back format. Use when dispatching a worker (lead) or working as one (worker-builder, scout, red-team).
---

# The worker protocol (E-006)

The lead runs the loop on `master`; workers build in worktrees. This is the contract between them. It exists so that
many sessions can work at once without any of them writing the record, merging unchecked work, or spending the
machine's memory twice.

## 1. The brief (the lead writes it; `/dispatch` sends it)

A brief is complete and self-contained -- the worker knows nothing else. It has these fields, every one filled:

| field | what |
|---|---|
| task | the TASK_QUEUE id and one sentence |
| worktree | `%LOCALAPPDATA%\stage2-extended-wt\<name>`, branch `wt/<name>`, the commit it starts from |
| goal | what "done" means, testably |
| rows to read | the decision rows and the declaration (`prereg/F-xx_*.md`) that govern the item |
| files to start from | paths, with what each is for |
| out of scope | what must not be built or read (always: outcomes not named; the confirmation window) |
| weight | light, or heavy with the run lock's job name and expected duration and memory |
| limits | DIRECTIVE Part 1, by reference, plus anything item-specific |
| hand-back | the format in section 4 |

The lead saves each brief as `docs/briefs/<Q-id>_<YYYY-MM-DD>.md` on `master` when it dispatches it.

## 2. What a worker may touch

| may | may not |
|---|---|
| files in its own worktree, on its branch | the main tree, another worktree, another branch, `master` |
| new code in this repository's package and `scripts/`, `tests/`, `identity/` | anything under `vendor/` (any tree) |
| a draft declaration file, if the brief asks for one (never pinned by the worker) | an existing `prereg/F-xx_*.md` (pinned: a change is a new family) |
| temporary output in a temp folder | `results/` (results come only from a clean run), `DECISIONS.md`, `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md` |
| the bars and atlas through the worktree's junctions, read-only, **if the brief allows heavy work** | a copy of the bars or atlas; any write through a junction |

## 3. How a worker works

1. Read the brief, the rows it names, `CLAUDE.md`, and the skills it names (always `feature-rules` for anything that
   touches bars, features or labels). If something in the brief contradicts a declaration or a rule, stop and say so:
   the declaration wins.
2. Tests first; then the code; then the tests again, with a time limit. **Before committing, run your own tests and
   the files your change can reach, never the whole fast tier by hand** (E-222): the pre-commit hook runs the whole fast
   tier once, under the machine-wide lock (`scripts/fasttier_lock.py`), and a second, unlocked copy only doubles the
   memory that crashed this machine (Q-155). If you need the whole tier before the hook (a wide change you want to
   diagnose first), run it through the lock: `python scripts/fasttier_lock.py run -- python -m pytest -q -o addopts=
   -m "not slow and not heavy"`. **The fast tier's selection is always
   `-m "not slow and not heavy"`** (the tier takes about 21 minutes on this machine
   under load, E-163; a test killed by the limit prints an `F` that is the limit, not a defect -- run that file alone
   before reporting it) -- `-m "not slow"` does not exclude `heavy`. A test
   marked `heavy` is skipped by the root `conftest.py` whenever `run.lock` is held by another job (Q-118); only the
   command `scripts/run_clean.py` runs under the lock (`S2X_LOCK_HOLDER=<job>`) runs them then. A skip reading "run.lock
   held by ..." is the guard working, not a pass.
3. Light work runs freely. Heavy work takes the run lock (skill `run-lock`) after checking memory, is watched to its
   exit, and releases the lock whatever the outcome.
4. Commit on the branch with a message `Q-xx: <what>` and the attribution line; **never `--no-verify`,
   for any reason** (E-060): if memory is short for the hook's fast tier, wait (`python scripts/run_lock.py status`
   shows what is free) and commit only when more than 1.75 GB is free. The post-commit hook pushes the branch to the private remote.
   **One hook commit per hand-back** (E-274): every commit costs the machine's shared line about 40 minutes, so
   iterate on your own targeted tests and commit once, when the item is done -- not after each fix. A clean
   `git merge master` runs no hook and is free; merge master at the start, and again just before the one commit.
   **Commit-message and log files live outside the worktree** (under your own name in the scratchpad): files in the
   tree are scanned by the seed guard and the typed-figure checks, and a message naming a seed refuses a 40-minute run.
   **Never end your turn while your commit is in the line**: wait on it in the background to its exit, then hand back.
   **Pre-flight before the one commit** (E-274): run your own tests AND the always-on guards with a time limit --
   `timeout 900 python -m pytest -q -o addopts= -p no:cacheprovider tests/test_heavy_marker_guard.py
   tests/test_heavy_guard.py tests/test_seed_derivation_guard.py tests/test_identity_tokens.py
   tests/test_declarations_fixed.py tests/test_git_scan.py tests/test_trace_check.py tests/test_vendor_integrity.py
   tests/test_reader*.py <your test files>` -- and commit only when it is green. Every refusal on 2026-11-21/22 (the
   seed guard twice, the identity tokens, the heavy marker guard, a worker's own new test) was one of these, each
   costing a 40-minute run of the shared line for a check that takes a minute or two.
   **Never watch a log with `tail -f`** (E-274): on Windows it outlives its shell -- 187 orphaned `tail`/`grep` pairs
   from 11-14 on were found holding memory on 2026-11-22. Wait with a loop that exits:
   `until grep -q "PATTERN" "$LOG"; do sleep 30; done`.
5. Two corrective cycles at most on one failure (diagnosed by the failure protocol). A third is the lead's decision:
   stop and hand back.

## 3a. The pre-hand-back checklist (E-207 (2); the restart plan's Wave 1.4)

Run it before the hand-back, and put each line's answer in the hand-back (section 4, item 4). It is drawn from the
review notes under `docs/reviews/`: the findings reviewers raised most often, most frequent first, each with a note that
shows it. A line that does not apply is answered "n/a" with the reason.

0. **The never lines.** No read of NQ from 2026-07-17; nothing under `vendor/` changed; the licence guard holds (no
   committed result from which a bar price can be recovered, `tests/test_results_no_price_levels.py`); no result file
   and no record file (`DECISIONS.md`, `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`) written on the branch -- results
   come only from a clean run; every journey measure is the function `docs/MEASURES.md` names; the redraw's oracle is
   the cost-aware one (the loss barrier min(l, c - x_stop), net = -(costs), no exit past the floor), not a cost-free
   zero-gross check alone.
1. **Seeds.** Every seed an integer with one role, written before the run; searched as a literal and as arithmetic
   over every worktree, every ref and the vendored snapshot; no seed shared between roles, declarations, or the search
   years and the held-out test; keys of fixed length per kind (numpy's trailing-zero trap).
   *(Q-108_plan_v2_2026-11-16 MATERIAL 3; the three-way design note's section 7.)*
2. **No typed figure.** Every number in a document is a rule cited by its key, a declared parameter, a date, a row or
   section id, or computed from a result file named beside it. *(Most review notes check it; CLAUDE.md "Results".)*
3. **The count.** Every cell, design, variant and L counted once and only once; nested populations named as such, not
   counted as separate delays or cells; k and the level's arithmetic written out. *(DRAFT_F-RL3_2026-11-18 B-2.)*
4. **Look-ahead.** Every input at a decision time known at that time: bar stamps are open times; a calendar as
   published in advance; an unscheduled release not known before it happens; a chain that picks its trade only among
   fills already made; a redraw's inputs read from bars closed at or before the alert. *(DRAFT_F-04_2026-11-18 B-3;
   DRAFT_RD-05_v2_2026-11-18 B-1; DRAFT_F-RL3_2026-11-18 B-4.)*
5. **The same convention, paired.** A design and every baseline under one convention (reflection, martingale-outcome
   redraw, fills, costs, latency as registered) on the same seeds and start days. *(MEASURES_2026-11-18 B-5;
   AMENDMENTS_2026-11-18 B-5.)*
6. **Citations current.** Every row id, `path:line`, sha256, quoted sentence and commit checked against the file as it
   is now on your branch after `git merge master` -- a stale citation is the commonest minor finding.
7. **The held-out years and the horizon.** Nothing chosen, fitted or ranged reads 2024-01-02 on; no start's window
   runs past its own years; every held-out read named for the ledger. *(MEASURES_2026-11-18 B-1; AMENDMENTS_2026-11-18
   B-1 to B-3.)*
8. **A check that can fail.** Every oracle and test shown to fail on a planted defect (a positive control), and computed
   from something other than the output it checks. *(BUILD_RD-05_coin_2026-11-18 B-1; AMENDMENTS_2026-11-18 B-4.)*
9. **Every declared corner run.** The grid's edges and the costed corners exercised by a test, not only its centre.
   *(BUILD_RD-05_coin_2026-11-18 B-2.)*
10. **Execution rules.** Verified news windows (no entry or fill inside; flatten at the start), L minutes from alert to
    order, one position per firm, never opposing positions, the 15:10 CT flatten, only verified rules loaded.
11. **Unlabelled choices.** Every parameter classed fixed / searched / dropped with its source; a strictness choice
    shows its size and power; anything chosen after a look labelled exploratory.
12. **Commit hygiene.** The commit-message file in your own worktree; free memory above 1.75 GB checked before each
    commit; the hook run, never skipped; nothing staged outside the brief's scope.

## 4. The hand-back (the worker's final reply)

1. Branch, commits (hash + one line each), files changed.
2. Tests: each one's assertion, the command, the result with counts and time.
3. Identities: which registered file, which columns, how many paths or starts, the tolerance, held or not.
4. **Every interpretation made** where the brief or declaration was silent or ambiguous; the pre-hand-back checklist
   (section 3a), each line answered.
5. Timings and peak memory of heavy work; the lock's take and release times.
6. Not done, and why; anything the lead should know.
7. The proposed decision row, one finished line `| E-NNN | <date> | **...** | <basis> |`.

## 5. What the lead does with it

The skill `merge-checklist`: reads the diff, reruns the tests, checks the identities, sends declarations to the red
team and results that matter to the auditor, then merges with `--no-ff`, numbers and commits the row, updates
STATUS / TASK_QUEUE / PROGRESS, pushes, and fast-forwards the other worktrees (`python scripts/worktrees.py sync`).

- **Never wrap `git commit` in `timeout`** (E-222): a killed hook stub let git write a commit without the fast tier's verdict; run the commit in the background and wait for it -- the hook has its own three-hour cap.
- **Never send command output to a generic name in the session scratchpad** (Q-161, E-223): it is one directory for every agent of the session, so two workers' `commit.log` cross; write logs inside your worktree, or under a name that carries the worktree.
- **Never `git stash push` / `pop`** (E-240): the stash stack is shared by every worktree, so a pop can apply another worker's entry. To merge master over staged work, write it to a patch inside your worktree (`git diff --cached --binary > .wip.patch`), `git reset --hard`, `git merge master`, `git apply --index .wip.patch`, then delete the patch; or `h=$(git stash create)` and later `git stash apply --index $h`, which touch no shared stack.
- **One worker per worktree at a time** (E-246): a worktree with a worker in it is not given a second brief, even between that worker's commits; the lead creates a new worktree instead. Two workers in `wt-report` on 2026-11-20 swapped each other's staged files and one commit landed with the other's content.
