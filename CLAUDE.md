# CLAUDE.md -- read this every session

Stage 2 Extended: execution models for a prop-firm **user's journey** (Topstep $50K first), built on Stage 2's engine,
vendored read-only. The charter is [`CHARTER.md`](CHARTER.md); the decision log [`DECISIONS.md`](DECISIONS.md)
(rows E-xxx; Stage 2's cited as "Stage 2 D-xxx"); the ranked queue [`TASK_QUEUE.md`](TASK_QUEUE.md); the live board
[`STATUS.md`](STATUS.md); the log [`PROGRESS.md`](PROGRESS.md); the lead's standing orders
[`DIRECTIVE.md`](DIRECTIVE.md). The brief this repository was started from is
`vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md`, and the orchestration's is `docs/BOOTSTRAP_NEW_REPO_ORCHESTRATOR.md`
-- read both once in full.

> **The operator's authority (Stage 2 D-452, carried):** anything that improves the research -- subagents, worktrees,
> tools, workflows -- is done without asking, **except a payment**: never authorise a purchase, subscription, billing
> change or credit draw; state the cost and wait. The operator does no work except setup and purchases;
> `docs/OPERATOR_SETUP.md` is the only channel for their manual tasks. A research question never goes to the operator:
> keep a safe default, record it under a decision row, report status. The operator is not a quant: every parameter is
> explained and classed fixed / searched / dropped. No automated or API order entry (it gets prop accounts banned).

## The objective (CHARTER section 2)

**P** -- the mean share of start days ahead (net cash above zero) at months 1, 2 and 3 -- with Stage 2 D-621's guarded
measures; **payouts per fee dollar (S3c) is the screening target**; the frontier on P, S1, S3a, S5a is reported, never
one number. **R\* = P-14.** A design is CARRIED only by Stage 2 D-621 (3)'s rule at its family's level 0.05 / (k (k+1)),
families numbered on from Stage 2's program U (this repository's first is k = 10, E-001).

## Rules that have teeth

- **`vendor/` is read-only** (E-002). A hook denies edits under it; `tests/test_vendor_integrity.py` checks every byte
  against `vendor/MANIFEST_stage2.sha256`. Import the engine; write adapters in this repository's own package. A newer
  Stage 2 is a new snapshot under a new decision row. The bars and atlas are licensed: copied uncommitted by
  `python scripts/vendor_stage2.py --data`, never committed, never shown in a screenshot on OneDrive.
- **Identities first, refusing.** `identity/stage2_identity.py` must hold (P-14 and P-16 reproduced path for path)
  before any result of this repository is believed. Every new runner has its own identity against Stage 2's files.
- **Declare the family before building it.** A family file under `prereg/F-xx_*.md`, pinned by sha256 in its decision
  row (`tests/test_declarations_fixed.py`); nothing declared is edited -- a change is a new family. Only a carried
  candidate takes a registration id. Count every cell.
- **Results.** Written only with a sidecar manifest (Stage 2's `propedge.reporting.results.write_result`, imported
  from the vendored tree, or this repository's equivalent); run once from a clean checkout of a named commit; one heavy
  run at a time on the machine, watched to its end. **No result number is typed into a document**: it is computed from
  a result file; a number that cannot be traced is deleted.
- **The failure protocol.** A failed check stays on record; diagnose (terminal states -> stage decomposition ->
  component in isolation -> replication with seeds fixed beforehand); never rerun until it passes.
- **Windows.** Development NQ 2020-01-02 to 2026-07-16 only. NQ from 2026-07-17 is the declared confirmation window,
  never read until a carried candidate is registered, and it is a purchase.
- **Firm rules** come only from Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`); a rule not in it is
  verified on the firm's official help centre (article id and date) under a decision row before it is loaded.
- **Conduct** (Stage 2 D-145): tier 1 hard (no hedging across accounts or firms, no simulator-fill exploitation, no
  maximum size into major news, nothing that conceals a pattern); tier 2 modelled, off in the base case (D-289);
  tier 3 priced (0 % denial in the verdict).

## The orchestration (DIRECTIVE.md; E-005)

- **One lead, on `master`.** It writes no model code. It alone appends to `DECISIONS.md`, edits `STATUS.md`,
  `TASK_QUEUE.md` and `PROGRESS.md`, merges branches and pushes (the single-writer rule). A worker proposes a decision
  row as one finished line `| E-NNN | ... |`; the lead numbers and commits it.
- **Workers in worktrees** under `%LOCALAPPDATA%\stage2-extended-wt\<name>` (branch `wt/<name>`, made by
  `git worktree add`, never under OneDrive, never Claude Code's `.claude/worktrees`): wt-verify (identities, audit
  fixes, stress checks, the engine), wt-levels (family A), wt-features (feature library, family B), wt-firms (other
  firms' contracts), wt-scout (read-only research and red-team reviews). A worker builds one declared item, tests it,
  commits on its branch, never merges, never writes the decision log (skill `worker-protocol`).
- **Light and heavy.** Light: reading, code, unit tests on synthetic data with a time limit, small checks -- many at
  once. Heavy: anything that reads the full bars, a solve, a campaign, the engine beyond a few paths -- **one at a time
  on the machine, under `run.lock`** at the repository root (git-ignored; holder, job, start, expected end; a lock
  older than its expected end plus an hour is investigated, never stolen; skill `run-lock`). Every heavy job is
  watched to its exit. Threads: `OMP_NUM_THREADS` at most 2, at most 2 workers.
- **Merging** follows the skill `merge-checklist`: the declaration came first, tests pass with a time limit, nothing
  vendored changed, no result written outside a clean run, no typed figure, the identities hold, no feature reads a
  bar after its alert. `auditor` on any result that matters; `red-team` on any declaration before it is pinned.
- **Silence.** Routine progress goes to `PROGRESS.md`. The operator hears only a result, a decision that is theirs,
  or a blocker. When the operator writes: stop dispatching, give the progress report (DIRECTIVE Part 5), wait.

## Machine facts

- Windows 11, 16 GB, the repository on OneDrive (which locks files under a running job: runs and worktrees live in
  `%LOCALAPPDATA%`). Memory decides concurrency: a Stage 2 family run peaked near 3 GB.
- **The licensed data:** this tree's `vendor/stage2/data/bars` and `data/atlas` are the one copy (E-002); every
  worktree and clean checkout links them as **directory junctions** (`mklink /J`), read in place, never copied again,
  never written. Remove a worktree by unlinking its junctions first, never through them.
- **Clean runs** come from a detached checkout of a committed commit under `%LOCALAPPDATA%\stage2-extended-runs\`,
  junctions linked, `git status` empty before the command, the log beside the checkout (`scripts/run_clean.py`).
- **Git hooks:** pre-commit runs vendor integrity and the fast test tier; post-commit pushes to the private `origin`
  in the background (`python scripts/install_hooks.py` installs both).

## Practical notes

- Python 3.12. `python -m pytest -q` (the identity test takes about a minute). `python scripts/vendor_stage2.py
  --verify` checks the snapshot and the data.
- The vendored code puts `vendor/stage2` and `vendor/stage2/scripts` on `sys.path`; run anything that imports it in
  its own process (as `tests/test_stage2_identity.py` does). One BLAS thread per process.
- Windows shell: no inline `python -c` with backticks; background long jobs and watch them; never `find /`.
- Every function that draws randomness takes an explicit seed; seeds are fixed in the family file before the run.
