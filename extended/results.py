"""Result files with sidecar manifests, in this repository's `results/` (Q-04): thin wrappers over the vendored
`propedge.reporting.results` (Stage 2's writer, unedited).

    from extended.results import write_result, read_result, verify_result, list_results

* `write_result` is the vendored writer with `repo=ROOT`, so a manifest's `git_commit` is **this** repository's
  commit, and `results_dir` defaulting to this repository's `results/`. A write into a `results/` folder of this
  repository's trees **refuses** (`CleanRunRequired`) unless the process runs inside the clean checkout
  `scripts/run_clean.py` made -- `ROOT` is `RUNS_DIR/<name>` and the environment marker `S2X_CLEAN_RUN` names it --
  and the marker is recorded in the manifest's `provenance.clean_run`. A result file there is never overwritten
  (`ResultExists`; DIRECTIVE Part 1). Any other folder (a test's temporary one) is written as the vendored writer
  writes it.
* `read_result` verifies the manifest first (the vendored check); `text=True` reads every cell as text, blanks as
  empty strings (day lists such as `"25 40"` and digit strings stay text). A relative name is read from `results/`.

Importing this module puts the vendored tree on `sys.path` (`extended.use_vendored_stage2`): import it in a process
of its own, not in the test runner's.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from extended import CLEAN_RUN_ENV, RESULTS_DIR, ROOT, RUNS_DIR, use_vendored_stage2

use_vendored_stage2()

import pandas as pd  # noqa: E402

from propedge.reporting import results as _vendored  # noqa: E402

MANIFEST_SUFFIX = _vendored.MANIFEST_SUFFIX
MissingProvenanceError = _vendored.MissingProvenanceError
manifest_path_for = _vendored.manifest_path_for
read_manifest = _vendored.read_manifest
#: how a tree of this repository is recognised (its pyproject.toml names the project)
PROJECT_MARK = 'name = "stage2-extended"'


class CleanRunRequired(RuntimeError):
    """A write into this repository's `results/` outside the clean checkout `scripts/run_clean.py` made."""


class ResultExists(FileExistsError):
    """A result file in `results/` is never overwritten: a new reading is a new file under its own row."""


def _resolved(p: Path | str) -> Path:
    return Path(os.path.abspath(Path(p))).resolve(strict=False)


def _is_tree_root(p: Path) -> bool:
    try:
        return (p / ".git").exists() and PROJECT_MARK in (p / "pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        return False


def protected(results_dir: Path | str) -> bool:
    """True for this tree's `results/` and anything under it, and for a `results/` folder (or below) directly inside
    any tree of this repository (the main tree, a worktree, a clean checkout)."""
    d = _resolved(results_dir)
    mine = _resolved(RESULTS_DIR)
    if d == mine or mine in d.parents:
        return True
    return any(q.name.lower() == "results" and _is_tree_root(q.parent) for q in (d, *d.parents))


def clean_run_problem() -> str | None:
    """Why this process is not inside a clean checkout made by `scripts/run_clean.py`; None when it is."""
    name = os.environ.get(CLEAN_RUN_ENV)
    if not name:
        return f"the environment marker {CLEAN_RUN_ENV} is not set (scripts/run_clean.py sets it for its command)"
    root, want = _resolved(ROOT), _resolved(RUNS_DIR) / name
    if root != want:
        return f"{CLEAN_RUN_ENV}={name!r}, but this tree is {root}, not the clean checkout {want}"
    return None


def write_result(df: pd.DataFrame, name: str, *, script: str, seed: int | None, parameters: dict[str, Any],
                 results_dir: Path | str | None = None, provenance: dict[str, Any] | None = None,
                 **kw: Any) -> tuple[Path, Path]:
    """The vendored `write_result` into this repository's `results/` (default) with `repo=ROOT`; refuses there
    outside a clean run, and never overwrites there. Other keywords (`description`, `exploratory`, `prereg_id`,
    `variant_count`, `notes`, `require_seed`) pass through unchanged."""
    if "repo" in kw:
        raise TypeError("repo is this repository's root (ROOT), always")
    target = Path(results_dir) if results_dir is not None else RESULTS_DIR
    prov = dict(provenance or {})
    if protected(target):
        d, mine = _resolved(target), _resolved(RESULTS_DIR)
        own = d == mine or mine in d.parents
        bad = clean_run_problem() if own else "it is another tree's results/ folder (a run writes only its own)"
        if bad:
            raise CleanRunRequired(f"REFUSED: {target} is a results/ folder of this repository and this process is "
                                   f"not a clean run -- {bad}. Results are written only from a clean checkout of a "
                                   "named commit: python scripts/run_clean.py --name <job> -- <command>")
        csv = target / (name if name.endswith(".csv") else f"{name}.csv")
        if csv.exists() or manifest_path_for(csv).exists():
            raise ResultExists(f"REFUSED: {csv} exists; a result file is never overwritten (DIRECTIVE Part 1) -- a new "
                               "reading is a new file under its own decision row")
        prov["clean_run"] = {"name": os.environ[CLEAN_RUN_ENV], "checkout": str(ROOT), "marker": CLEAN_RUN_ENV}
    return _vendored.write_result(df, name, script=script, seed=seed, parameters=parameters, results_dir=target,
                                  provenance=prov or None, repo=ROOT, **kw)


def _path(csv_path: Path | str) -> Path:
    p = Path(csv_path)
    return p if p.is_absolute() else RESULTS_DIR / p


def verify_result(csv_path: Path | str) -> tuple[bool, str]:
    """The vendored check: the CSV still matches the sha256 its manifest recorded."""
    return _vendored.verify_result(_path(csv_path))


def read_result(csv_path: Path | str, *, verify: bool = True, text: bool = False) -> pd.DataFrame:
    """A result CSV after its manifest check (the vendored `read_result`); `text=True` reads it as text."""
    p = _path(csv_path)
    if not text:
        return _vendored.read_result(p, verify=verify)
    if verify:
        ok, msg = _vendored.verify_result(p)
        if not ok:
            raise ValueError(msg)
    return pd.read_csv(p, dtype=str, keep_default_na=False, low_memory=False)


def list_results(results_dir: Path | str | None = None) -> list[dict[str, Any]]:
    """Every result CSV in `results_dir` (default this repository's `results/`) with its manifest status."""
    return _vendored.list_results(Path(results_dir) if results_dir is not None else RESULTS_DIR)


__all__ = ["write_result", "read_result", "verify_result", "list_results", "read_manifest", "manifest_path_for",
           "protected", "clean_run_problem", "CleanRunRequired", "ResultExists", "MissingProvenanceError"]
