"""The trace registry (Q-04): every number a document of this repository states, bound to the result file it is
computed from and the documents that must show it. Reuses the vendored `propedge.reporting.trace` (Stage 2's
`TracedNumber` and `run_trace_check`, unedited) on this repository's `results/` and documents.

    from extended.trace import TracedNumber, REGISTRY
    REGISTRY.append(TracedNumber("F-01 stage C: the pick's lift lower bound", "f01_stage_c.csv",
                                 lambda df: float(df.loc[df["row"] == "pick", "lift_lb"].iloc[0]),
                                 ("docs/REPORT.md",), decimals=3, tolerance=5e-4))

A `TracedNumber`'s `recompute` takes the result file as read by the vendored `read_result` (its manifest checked
first) and must derive the number from it -- a lambda returning a literal defeats the check. **Nothing is registered
yet** (no result of this repository exists), so `scripts/trace_check.py` prints NOT CHECKED and exits 2: an empty
registry is never a pass. Never call the vendored `run_trace_check` without a list -- with none it runs Stage 2's own
registry.

Importing this module puts the vendored tree on `sys.path`: import it in a process of its own.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from extended import RESULTS_DIR, ROOT, use_vendored_stage2

use_vendored_stage2()

from propedge.reporting.trace import TraceReport, TracedNumber, run_trace_check  # noqa: E402

#: this repository's traced numbers, registered as each is produced (none yet)
REGISTRY: list[TracedNumber] = []


def registry() -> list[TracedNumber]:
    return list(REGISTRY)


def run(checks: Iterable[TracedNumber] | None = None, *, results_dir: Path | str | None = None,
        repo_root: Path | str | None = None) -> TraceReport:
    """Recompute each check (default: `REGISTRY`) from its file in `results_dir` (default this repository's
    `results/`) and find it in its documents under `repo_root` (default `ROOT`). Always passes a list on, so Stage 2's
    own registry is never run in its place."""
    items = registry() if checks is None else list(checks)
    return run_trace_check(items, results_dir=Path(results_dir) if results_dir is not None else RESULTS_DIR,
                           repo_root=Path(repo_root) if repo_root is not None else ROOT)


__all__ = ["REGISTRY", "TracedNumber", "TraceReport", "registry", "run"]
