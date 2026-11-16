---
name: result-provenance
description: How this repository writes results with sidecar manifests (extended.results over the vendored propedge.reporting.results), how documents cite them, and how the trace check works. Use when writing a result file, putting a number in a document or report, or investigating whether a number can be trusted.
---

# Result provenance

One rule, and the machinery that makes it hold:

> **Never type a result number into a document. Compute it from a result file that has a manifest.**
> (CLAUDE.md, "Results"; a number that cannot be traced is deleted.)

## Writing a result

Always through **`extended.results.write_result`** -- this repository's thin wrapper over the vendored
`propedge.reporting.results.write_result` (TASK_QUEUE Q-04), which fixes `results_dir=<repo>/results` and
`repo=<repo>` and takes every other argument unchanged. It writes the CSV and its sidecar manifest together:

```python
from extended.results import write_result

csv_path, manifest_path = write_result(
    df,
    "<family>_<stage>",                 # a new name for every reading; never an existing file's
    script="scripts/<runner>.py",
    seed=SEED,                          # required: the integer the family file fixed
    parameters={...},                   # every declared value the run used: cells, blocks, stops, R values, seeds
    description="<family> <stage>: what was read, on which block",
    prereg_id="F-NN",                   # the declaration it belongs to
    variant_count=K_CELLS,              # the cells run, as the declaration counts them
)
```

**Never call the vendored `write_result` with its defaults.** Its `results_dir` defaults to `propedge.RESULTS_DIR`,
which is `vendor/stage2/results/` -- the read-only snapshot -- and its `repo` to `vendor/stage2/`. A result written
there breaks `vendor/MANIFEST_stage2.sha256` and records the wrong git state. Always the wrapper.

The sidecar `<name>.csv.manifest.json` records `script`, `git_commit` (with `-dirty` if the tree was not clean, read
before the CSV is written), `seed`, `parameters`, `timestamp`, `sha256` of the CSV, row and column counts,
`description`, `exploratory`, `prereg_id`, `variant_count`, and optional `provenance`.

`write_result` **refuses** to write without a script, and without a seed unless you pass `require_seed=False` -- only
for results with genuinely no randomness (an exact chain, a closed form), said in `description`. Be generous with
`parameters`: one you leave out is one nobody can reconstruct.

**Where and how a result is made.** Only from a clean checkout of a named commit (`python scripts/run_clean.py`: a
detached checkout under `%LOCALAPPDATA%\stage2-extended-runs\`, the data junctions linked, `git status` empty before
the command, the log beside it), run once, watched to its end, one heavy run at a time under `run.lock`. A manifest
whose `git_commit` ends `-dirty` is not a citable reading. The lead brings it home (`/collect`). A result file is never
deleted or overwritten: a new reading is a new file under its own decision row (DIRECTIVE Part 1).

## Reading a result

Always through **`extended.results.read_result`**, which verifies the sha256 before returning the data: a CSV edited
since it was written raises rather than quietly feeding a stale number into a report. `extended.results.verify_result(
path)` returns `(ok, message)`; `extended.results.list_results()` gives every result file of `results/` with its
status -- what `/status` and `/close-check` use.

**Stage 2's results** are evidence, vendored read-only under `vendor/stage2/results/` with their own manifests. Read
them with the vendored `propedge.reporting.results.read_result` (it verifies them the same way), in a process with
`vendor/stage2` on `sys.path`; cite them by file, never retype their numbers.

**Result CSVs are never hand-edited.** A hook (`scripts/hooks/protect_results.py`) refuses direct writes to
`results/*.csv` and `*.manifest.json` in this tree, in every worktree and in every clean checkout of it, and
`protect_vendor.py` refuses anything under `vendor/`. If a number is wrong, fix the code and regenerate it as a new
file. The sha256 exists so an edit cannot pass unnoticed; bypassing it defeats the only mechanism that makes a result
citable.

Result CSVs **are** tracked in git -- they are the evidence (`.gitattributes` keeps `results/*.csv` byte-exact). Bulk
artefacts (`.png`, `.parquet`, `results/scratch/`) and `results/.last_test_run.json` are not.

## Citing a result in a document

Compute the number from the file at build time; never transcribe it. Where a number appears, the document also
carries:

- **P never alone** (CHARTER sections 2-3): the guarded measures beside it, the frontier on P, S1, S3a and S5a, the
  menu under limits fixed before the read, and Stage 2's long-run gate (growth on the required bankroll at the bound)
  beside, so a design that helps users but cannot grow is visible.
- **Any growth or return figure** beside ruin probability, bankroll drawdown and payout latency (Stage 2 D-145) -- beside
  it, not in an appendix.
- **The bound, not the point**, for any money decision -- sizing, bankroll, account count: the `verdict` arm. Point
  figures may appear alongside, labelled.
- **The count**: the family's cells and the program's running family count (Stage 2 D-621 (5)).
- **The exploratory label**, where the manifest says `exploratory=True`, at the number, reported apart from the
  declared set.
- **The assumptions**: an `assumed` fill profile, a rule not verified, the payout lag, the payout-spacing model, the
  tier-2 placement off (D-289), 0 % denial (D-234). Silence about an assumption reads as a claim that there is none.

## The trace check

`python scripts/trace_check.py` (TASK_QUEUE Q-04) recomputes each registered number from its CSV -- verifying the
manifest first -- and looks for it in the named documents, tolerating the formatting a human would use (thousands
separators, currency symbols, percentages, a decimal place either way). Its entries follow the vendored
`propedge.reporting.trace.TracedNumber` pattern:

```python
TracedNumber(
    label="F-01 pick: P difference from P-14 on the judged block",
    source_csv="f01_stage_d.csv",
    recompute=lambda df: df.loc[df["section"] == "paired", "difference"].iloc[0],
    documents=("STATUS.md",),
    decimals=3,
)
```

It distinguishes "not found" from "a different number is nearby", because the second means the document is **stale**
-- the common real failure, and the one a reader cannot detect. **An empty registry is NOT CHECKED, never a pass**: a
green trace check that checked nothing is worse than no check, because it will be believed. Register each headline
number as it is produced, and write `recompute` so it genuinely derives the value from the CSV -- a function returning a
literal passes the check and verifies nothing.

The vendored `propedge.reporting.trace.untraced_numbers_in(document, known)` sweeps a document for numbers matching
nothing known. It is blunt -- it catches dates, article ids, hashes and Stage 2 figures too -- so it is a prompt for the
**results-tracer** agent to triage, not a gate.

## Quick reference

| task | how |
|---|---|
| Write a result | `extended.results.write_result(df, name, script=..., seed=..., parameters=...)`, from a clean checkout |
| Read a result | `extended.results.read_result(path)` -- verifies the hash first |
| Check one file | `extended.results.verify_result(path)` |
| List all results | `extended.results.list_results()` |
| Read a Stage 2 result | the vendored `propedge.reporting.results.read_result` on `vendor/stage2/results/<file>` |
| Result was hand-edited | Regenerate it as a new file. Never re-hash to make the check pass |
| Put a number in a document | Register a traced number; compute at build time |
| Check the documents | `/trace` |
| Vendor and data integrity | `python scripts/vendor_stage2.py --verify` |
