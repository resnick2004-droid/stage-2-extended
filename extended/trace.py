"""The trace registry (Q-04): every number a document of this repository states, bound to the result file it is
computed from and the documents that must show it. Reuses the vendored `propedge.reporting.trace` (Stage 2's
`TracedNumber` and `run_trace_check`, unedited) on this repository's `results/` and documents.

    from extended.trace import TracedNumber, REGISTRY
    REGISTRY.append(TracedNumber("F-01 stage C: the pick's lift lower bound", "f01_stage_c.csv",
                                 lambda df: float(df.loc[df["row"] == "pick", "lift_lb"].iloc[0]),
                                 ("docs/REPORT.md",), decimals=3, tolerance=5e-4))

A `TracedNumber`'s `recompute` takes the result file as read by the vendored `read_result` (its manifest checked
first) and must derive the number from it -- a lambda returning a literal defeats the check. An empty registry is never
a pass: `scripts/trace_check.py` prints NOT CHECKED and exits 2. Never call the vendored `run_trace_check` without a
list -- with none it runs Stage 2's own registry.

**The report pages (Q-27).** Every number of every page named in `REPORT_PAGES` (`extended.report.REPORTS`, built by
`scripts/build_report.py` into docs/report/<name>/) is registered here at import: `extended.report.traced_numbers`
lists what the page prints from the current file and code, each entry recomputing its value from the file. A page
whose numbers cannot be listed registers one entry that fails, saying why -- never silence.

**One read a file a run.** The vendored check reads a result file once per number (`read_result` after
`verify_result`, for every entry); a page of hundreds of numbers on one file is hundreds of reads. `run` therefore lends
the vendored module, for its own duration only, a `read_result` that keeps each file's frame once it has been read:
keyed by the file's path, size, modification time and its manifest's sha256, after the vendored `verify_result` has
passed for that very check (the vendored order, unchanged). Every check still verifies its file; the original
`read_result` is put back when the run ends, whatever happens.

Importing this module puts the vendored tree on `sys.path`: import it in a process of its own.
"""
from __future__ import annotations

import os
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

from extended import RESULTS_DIR, ROOT, use_vendored_stage2

use_vendored_stage2()

import propedge.reporting.trace as _vtrace  # noqa: E402
from propedge.reporting.results import read_manifest  # noqa: E402
from propedge.reporting.trace import TraceReport, TracedNumber, run_trace_check  # noqa: E402

#: this repository's traced numbers, registered as each is produced
REGISTRY: list[TracedNumber] = []
#: the report pages whose every number is registered (Q-27): names in `extended.report.REPORTS`
REPORT_PAGES: tuple[str, ...] = ("demo_stage2_u1",)


def registry() -> list[TracedNumber]:
    return list(REGISTRY)


def report_checks(names: Iterable[str] = REPORT_PAGES, *, root: Path | str | None = None) -> list[TracedNumber]:
    """Every number of each named report page, as `TracedNumber` entries; a page whose numbers cannot be listed gives
    one entry that fails with the reason."""
    from extended import report as R

    root = Path(root) if root is not None else ROOT
    out: list[TracedNumber] = []
    for name in names:
        spec = R.REPORTS.get(name)
        try:
            if spec is None:
                raise KeyError(f"{name!r} is not in extended.report.REPORTS")
            out += R.traced_numbers(spec, root=root)
        except Exception as exc:  # noqa: BLE001 -- a page that cannot be listed must fail the check, not vanish
            out.append(_unlisted(name, spec, root, exc))
    return out


def _unlisted(name: str, spec, root: Path, exc: Exception) -> TracedNumber:
    from extended import report as R

    why = f"{type(exc).__name__}: {exc}"

    def fail(_df):
        raise RuntimeError(f"the page's numbers could not be listed -- {why}")

    src = str(R.source_path(spec, root)) if spec is not None else str(RESULTS_DIR / f"{name}.csv")
    doc = R.page_path(spec, root).relative_to(root).as_posix() if spec is not None else f"docs/report/{name}/README.md"
    return TracedNumber(f"{name}: every number of the page", src, fail, (doc,))


@contextmanager
def _one_read_per_file() -> Iterator[dict]:
    """For the duration of one run: the vendored trace module's `read_result` keeps each file's frame once read (see
    the module's docstring); restored on exit."""
    import pandas as pd

    original = _vtrace.read_result
    cache: dict = {}

    def read(csv_path, *, verify: bool = True):
        p = Path(csv_path)
        st = p.stat()
        try:
            sha = read_manifest(p).sha256
        except FileNotFoundError:
            sha = None
        key = (os.path.normcase(str(p.resolve())), st.st_size, st.st_mtime_ns, sha, bool(verify))
        if key not in cache:
            cache[key] = original(p, verify=verify)
        return cache[key].copy(deep=False)

    _vtrace.read_result = read
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", pd.errors.DtypeWarning)
            yield cache
    finally:
        _vtrace.read_result = original


def run(checks: Iterable[TracedNumber] | None = None, *, results_dir: Path | str | None = None,
        repo_root: Path | str | None = None) -> TraceReport:
    """Recompute each check (default: `REGISTRY`) from its file in `results_dir` (default this repository's
    `results/`) and find it in its documents under `repo_root` (default `ROOT`). Always passes a list on, so Stage 2's
    own registry is never run in its place; each file is read once a run."""
    items = registry() if checks is None else list(checks)
    with _one_read_per_file():
        return run_trace_check(items, results_dir=Path(results_dir) if results_dir is not None else RESULTS_DIR,
                               repo_root=Path(repo_root) if repo_root is not None else ROOT)


REGISTRY.extend(report_checks())

__all__ = ["REGISTRY", "REPORT_PAGES", "TracedNumber", "TraceReport", "registry", "report_checks", "run"]
