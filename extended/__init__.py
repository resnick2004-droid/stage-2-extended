"""Stage 2 Extended's own package: where things live, and the one door to the vendored Stage 2 engine (Q-04).

    from extended import ROOT, VENDOR_STAGE2, RESULTS_DIR, use_vendored_stage2

Importing this package changes nothing: `sys.path` is touched only by `use_vendored_stage2()`, which a process calls
once, before it imports numpy or the engine. The vendored code is run in its own process (CLAUDE.md): it puts
`vendor/stage2` and `vendor/stage2/scripts` on `sys.path`, and that scripts folder holds modules (`run_clean`,
`status`) whose names this repository's `scripts/` also uses.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

#: this repository's root (a worktree's or a clean checkout's own root when run from one)
ROOT = Path(__file__).resolve().parent.parent
#: the vendored Stage 2 snapshot, read-only (E-002)
VENDOR_STAGE2 = ROOT / "vendor" / "stage2"
#: this repository's result files; written only from a clean checkout (`extended.results.write_result`)
RESULTS_DIR = ROOT / "results"
#: where `scripts/run_clean.py` makes its clean, detached checkouts (outside OneDrive)
RUNS_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-extended-runs"
#: the environment marker `scripts/run_clean.py` sets for the command it runs: the checkout's name
CLEAN_RUN_ENV = "S2X_CLEAN_RUN"
#: one BLAS thread a process (Stage 2 D-464 (5))
BLAS_VARS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")


def use_vendored_stage2(root: Path | str | None = None) -> Path:
    """Put the vendored Stage 2 tree (`root`, default `VENDOR_STAGE2`) and its `scripts/` at the front of `sys.path`
    (scripts first, as the vendored scripts do it), one BLAS thread unless the caller set otherwise, no bytecode
    written into the read-only tree. Returns the tree. Call it before numpy is imported."""
    root = Path(root).resolve() if root is not None else VENDOR_STAGE2
    for k in BLAS_VARS:
        os.environ.setdefault(k, "1")
    sys.dont_write_bytecode = True
    for p in (str(root), str(root / "scripts")):
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    return root


__all__ = ["ROOT", "VENDOR_STAGE2", "RESULTS_DIR", "RUNS_DIR", "CLEAN_RUN_ENV", "BLAS_VARS", "use_vendored_stage2"]
