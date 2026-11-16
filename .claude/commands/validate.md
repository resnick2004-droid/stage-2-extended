---
description: Run the full verification -- vendor and data integrity, the suite, the identity at 4 paths, the vendored stage-one suite -- and print a summary
allowed-tools: Read, Bash, PowerShell, Glob
---

Run the full verification and summarise it. Run the steps in order, each to its end, one at a time (step 3 runs the
engine: check that no heavy run holds `run.lock` and that memory is free before it; it is light at 4 paths, about a
minute). Set `PYTHONDONTWRITEBYTECODE=1` for every step so nothing writes `__pycache__` into the vendored tree.

1. **Vendor and data integrity** -- `python scripts/vendor_stage2.py --verify`. It checks every file of `vendor/stage2/`
   against `vendor/MANIFEST_stage2.sha256` and, when the bars and atlas are present, the data against
   `vendor/DATA_MANIFEST_stage2.sha256`; it prints the counts and exits 0, or prints `FAILED` and exits 3.
2. **This repository's suite** -- `python -m pytest -o addopts= -q`. Report the pass count and every skip. (`-o
   addopts=` clears the project's own `-q`; without it the two combine into `-qq` and the count is suppressed.) This
   includes the `slow` identity test; the `heavy` tier is not run here unless the brief says so.
3. **The identity at 4 paths** -- `python identity/stage2_identity.py --paths 4`. Expect `identity HOLDS` twice (P-14
   and P-16) and exit 0.
4. **The vendored stage-one suite** -- from `vendor/stage2/vendor/propsim`:
   `python -m pytest test_propsim.py -o addopts= -q -p no:cacheprovider`, with `PYTHONDONTWRITEBYTECODE=1`.
   **`-p no:cacheprovider` is required**: pytest finds its root at `vendor/stage2/` (Stage 2's `pyproject.toml`) and
   would otherwise write `vendor/stage2/.pytest_cache/`, an extra file that breaks the manifest check. Stage 2 recorded
   33 passed.

Then run step 1 again: the tree must still match after the suites ran.

Print a summary:

- vendor and data integrity: OK / FAILED (and which files) -- before and after
- this repository's suite: N passed, M skipped, K failed
- the identity at 4 paths: HOLDS / REFUSED for P-14 and P-16
- the vendored stage-one suite: N passed
- overall: **PASS** or **FAIL**

On any failure, report the output and stop. Do not fix the failure as part of this command, and never regenerate
`vendor/MANIFEST_stage2.sha256` or `vendor/DATA_MANIFEST_stage2.sha256` to make an integrity check pass -- a mismatch
under `vendor/` means the read-only foundation was modified (E-002), and the response is to restore it (a fresh clone,
or `scripts/vendor_stage2.py` from Stage 2's commit) and find what wrote to it. A failed check stays on record (the
failure protocol).
