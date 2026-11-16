"""How a backtest run by hand in QuantConnect's web editor enters the repository (D-81).

Until a paid organisation enables the API, backtests may be run by a person in the web editor.
Nothing in this repository sees that run happen, so the result has to prove three things itself:

  1. **which algorithm ran** -- the code as it stood in the editor at run time, hashed and
     matched against a file **committed** in this repository and generated from the template
     (`propedge/data/qc_template.py`), so the embedded confirmation-window guard was in it;
  2. **which run it was** -- the QuantConnect project and backtest ids, the date run, who ran it;
  3. **what came back** -- the downloaded result files, hashed, and the table derived from them,
     written through `propedge.reporting.results.write_result` with provenance
     "human-run in QuantConnect web editor".

**A result whose algorithm hash does not match a committed file is refused.** So is one whose
algorithm is uncommitted or modified in the working tree, lacks the template marker, or reaches
the confirmation window without a registered pre-registration.

Hashing normalises line endings (CRLF -> LF) and trailing blank lines, because a copy through a
browser changes those and nothing else that matters. Any other difference is a different
algorithm.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from propedge import REPO_ROOT
from propedge.data.cloud_guard import assert_cloud_run_allowed, confirmation_run_authorised
from propedge.data.qc_template import MARKER
from propedge.reporting.results import sha256_of, write_result

PROVENANCE = "human-run in QuantConnect web editor"

_PREREG_LINE = re.compile(r"^PREREG_ID\s*=\s*(.+)$", re.MULTILINE)


class ManualRunRefused(RuntimeError):
    """Raised when a human-run result cannot be tied to a committed, guarded algorithm."""


def normalised_hash(code: str) -> str:
    """sha256 of algorithm source after normalising line endings and trailing blank lines."""
    text = code.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, timeout=30)


def committed_source(algorithm_path: Path | str, *, repo: Path = REPO_ROOT) -> tuple[str, str]:
    """The algorithm's source at HEAD and the commit that last changed it.

    Refuses a file that is untracked, or modified in the working tree or the index: a result can
    only be tied to code someone else can check out.
    """
    rel = Path(algorithm_path)
    if rel.is_absolute():
        rel = rel.resolve().relative_to(repo.resolve())
    rel_s = rel.as_posix()
    if _git(repo, "ls-files", "--error-unmatch", rel_s).returncode != 0:
        raise ManualRunRefused(f"{rel_s} is not committed in this repository.")
    if _git(repo, "diff", "--quiet", "HEAD", "--", rel_s).returncode != 0:
        raise ManualRunRefused(
            f"{rel_s} has uncommitted changes. Commit the algorithm first; a result is tied to "
            "committed code only."
        )
    blob = _git(repo, "show", f"HEAD:{rel_s}")
    if blob.returncode != 0:
        raise ManualRunRefused(f"could not read {rel_s} at HEAD: {blob.stderr.decode()[:200]}")
    commit = _git(repo, "log", "-1", "--format=%H", "--", rel_s).stdout.decode().strip()
    return blob.stdout.decode("utf-8"), commit


def _embedded_prereg(code: str) -> str | None:
    m = _PREREG_LINE.search(code)
    if not m:
        raise ManualRunRefused("the algorithm has no PREREG_ID line; it was not generated from "
                               "the template.")
    raw = m.group(1).split("#")[0].strip()
    return None if raw == "None" else raw.strip("'\"")


def record_manual_run(
    df: pd.DataFrame,
    name: str,
    *,
    algorithm_path: Path | str,
    ran_code_path: Path | str | None,
    project_id: int | str,
    backtest_id: str,
    date_run: str,
    run_by: str,
    downloaded_files: list[Path | str],
    description: str,
    prereg_id: str | None = None,
    exploratory: bool = False,
    variant_count: int | None = None,
    repo: Path = REPO_ROOT,
    results_dir: Path | str | None = None,
    ran_code_attested_by: str | None = None,
    provenance: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    """Validate a human-run backtest and write its result with full provenance.

    Args:
        df: the table derived from the downloaded results.
        algorithm_path: the committed algorithm file that was pasted into the web editor.
        ran_code_path: the code as it stood in the editor at run time, copied or downloaded back
            after the run. Its hash must equal the committed file's.
        project_id, backtest_id: QuantConnect's ids for the run, from the web editor.
        date_run: ISO date the backtest was run.
        run_by: the person who ran it.
        downloaded_files: the files downloaded from QuantConnect (orders, logs, statistics).
        ran_code_attested_by: D-131. Instead of `ran_code_path`, the named person attests that the
            committed file was pasted unchanged. The result then records `ran_code_check:
            attested` -- a weaker proof than a hash of the captured code, and labelled as such; the
            caller must supply its own structural check of the output (the ingestion script checks
            that every exported record carries exactly the committed kit's fields).
    """
    committed, commit = committed_source(algorithm_path, repo=repo)
    committed_hash = normalised_hash(committed)
    if ran_code_path is not None and Path(ran_code_path).is_file():
        ran_hash = normalised_hash(Path(ran_code_path).read_text(encoding="utf-8"))
        if committed_hash != ran_hash:
            raise ManualRunRefused(
                f"the code that ran ({ran_hash[:12]}...) does not match the committed "
                f"{Path(algorithm_path).as_posix()} ({committed_hash[:12]}...). REFUSED: a result "
                "whose algorithm hash does not match a committed file cannot enter the repository."
            )
        ran_code_check = "hash-matched: the code captured from the editor equals the committed file"
    elif ran_code_attested_by and str(ran_code_attested_by).strip():
        ran_code_check = (f"attested by {ran_code_attested_by}: the committed file was pasted unchanged; "
                          "the ran code was not captured (D-131)")
    else:
        raise ManualRunRefused(
            "no ran code: supply the code copied from the editor, or (D-131) a named attestation that "
            "the committed file was pasted unchanged."
        )
    if not committed.startswith(MARKER):
        raise ManualRunRefused(
            "the algorithm was not generated from propedge/data/qc_template.py, so the embedded "
            "confirmation-window guard cannot be assumed to be in it."
        )
    embedded = _embedded_prereg(committed)
    if embedded != prereg_id:
        raise ManualRunRefused(
            f"prereg_id {prereg_id!r} does not match the id embedded in the algorithm "
            f"({embedded!r})."
        )
    if prereg_id is not None and not confirmation_run_authorised(prereg_id):
        raise ManualRunRefused(f"{prereg_id!r} is not a runnable row in prereg/REGISTRY.md.")
    dates = assert_cloud_run_allowed(committed, prereg_id=prereg_id,
                                     what=f"manual run of {Path(algorithm_path).as_posix()}")

    run_day = date.fromisoformat(str(date_run))
    if run_day > date.today():
        raise ManualRunRefused(f"date_run {run_day} is in the future.")
    if not str(run_by).strip():
        raise ManualRunRefused("run_by is required: a manual run needs a named person.")
    if not str(project_id).strip() or not str(backtest_id).strip():
        raise ManualRunRefused("the QuantConnect project id and backtest id are both required.")
    if not downloaded_files:
        raise ManualRunRefused("at least one downloaded result file is required.")
    downloads: list[dict[str, Any]] = []
    for f in downloaded_files:
        p = Path(f)
        if not p.is_file():
            raise ManualRunRefused(f"downloaded file {p} does not exist.")
        downloads.append({"file": p.name, "sha256": sha256_of(p), "bytes": p.stat().st_size})

    algo_rel = Path(algorithm_path).as_posix()
    parameters = {
        "provenance": PROVENANCE,
        "algorithm_file": algo_rel,
        "algorithm_sha256_normalised": committed_hash,
        "algorithm_commit": commit,
        "ran_code_check": ran_code_check,
        "qc_project_id": str(project_id),
        "qc_backtest_id": str(backtest_id),
        "backtest_start": dates.start.isoformat(),
        "backtest_end": dates.end.isoformat(),
        "date_run": run_day.isoformat(),
        "run_by": str(run_by),
        "downloaded_files": downloads,
    }
    return write_result(
        df, name,
        script=f"{PROVENANCE}: {algo_rel}",
        seed=None,
        require_seed=False,
        parameters=parameters,
        description=(description + " -- A LEAN backtest is deterministic given its code and "
                     "data, so there is no seed; the algorithm hash and backtest id stand in."),
        exploratory=exploratory,
        prereg_id=prereg_id,
        variant_count=variant_count,
        notes={"provenance": PROVENANCE},
        results_dir=results_dir,
        provenance=provenance,      # D-184: e.g. the LEAN version the cloud reports for the run
    )
