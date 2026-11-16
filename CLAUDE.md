# CLAUDE.md -- read this every session

Stage 2 Extended: execution models for a prop-firm **user's journey** (Topstep $50K first), built on Stage 2's engine,
vendored read-only. The charter is [`CHARTER.md`](CHARTER.md); the decision log [`DECISIONS.md`](DECISIONS.md)
(rows E-xxx; Stage 2's cited as "Stage 2 D-xxx"); the task list [`NEXT_STEPS.md`](NEXT_STEPS.md). The brief this
repository was started from is `vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` -- read it once in full.

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

## Practical notes

- Python 3.12. `python -m pytest -q` (the identity test takes about a minute). `python scripts/vendor_stage2.py
  --verify` checks the snapshot and the data.
- The vendored code puts `vendor/stage2` and `vendor/stage2/scripts` on `sys.path`; run anything that imports it in
  its own process (as `tests/test_stage2_identity.py` does). One BLAS thread per process.
- Windows shell: no inline `python -c` with backticks; background long jobs and watch them; never `find /`.
- Every function that draws randomness takes an explicit seed; seeds are fixed in the family file before the run.
