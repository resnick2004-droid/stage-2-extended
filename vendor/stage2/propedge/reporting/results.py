"""Every result CSV is written with a sidecar manifest.

The working-discipline rule is "never type a result number into a document; compute it from a
result file with a manifest". That only works if every result file carries enough to
regenerate it, so `write_result` refuses to write a CSV without:

    script      which program produced it
    git_commit  the code state (with a `-dirty` marker if the tree had uncommitted changes),
                read BEFORE the CSV is written (D-178): the new file must not be what makes
                the tree dirty, or every manifest says `-dirty` and the marker means nothing.
                Files this process wrote itself -- earlier results of the same run, the
                variant ledger's append -- are left out of the check for the same reason
                (D-207, `note_written`); any other change still marks it
    seed        the seed -- required, because every simulation in this stage is seeded
    parameters  everything else the run depended on
    timestamp   when
    sha256      of the CSV itself
    provenance  optional: what else the result depended on -- the engine pin (D-180), the
                fee-table read date, a rules-file date -- as `propedge.reporting.pin` writes it

The sidecar is `<name>.csv.manifest.json`, beside the CSV. Two files rather than a header
comment because the CSV must stay machine-readable by anything that reads CSVs, and because
the hash of the CSV cannot live inside the CSV.

A hook refuses direct edits to result CSVs: a result you can hand-edit is a result you cannot
trace. Regenerate instead.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from propedge import REPO_ROOT, RESULTS_DIR

MANIFEST_SUFFIX = ".manifest.json"


class MissingProvenanceError(ValueError):
    """Raised when a result would be written without enough to reproduce it."""


#: D-207: every file this process wrote through `write_result` (the CSV and its manifest) or recorded with
#: `note_written` (the variant ledger's append), as `_key` spells it. `git_commit` leaves them out of its dirty check, so
#: a run that writes several results is not stamped dirty by its own earlier outputs. A change the process did not
#: make -- code, a config, a result left over from an earlier uncommitted run -- still marks it.
_WRITTEN: set[str] = set()


def _key(path: Path | str) -> str:
    return os.path.normcase(str(Path(path).resolve()))


def note_written(path: Path | str) -> None:
    """Record that this process wrote `path`, so later results of the same run do not count it as dirt (D-207)."""
    _WRITTEN.add(_key(path))


def _changed_paths(porcelain_z: str) -> list[str]:
    """The paths in `git status --porcelain -z` output, relative to the top level. A rename or copy lists its source as
    well as its destination: the source's removal is a change too."""
    entries = porcelain_z.split("\0")
    out: list[str] = []
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) < 4:
            continue
        out.append(entry[3:])
        if entry[0] in "RC" or entry[1] in "RC":
            if i < len(entries) and entries[i]:
                out.append(entries[i])
            i += 1
    return out


def git_commit(repo: Path | None = None) -> str:
    """Current commit, with `-dirty` appended if the tree has uncommitted changes other than the files this process
    wrote (D-207, `note_written`).

    Returns "unknown" if git is unavailable or this is not a repository -- recorded honestly
    rather than raising, so a result is never lost to a tooling problem, but the value is
    visibly useless and `/trace` flags it.
    """
    repo = repo or REPO_ROOT
    try:
        rev = subprocess.run(
            ["git", "rev-parse", "--show-toplevel", "HEAD"],
            cwd=repo, capture_output=True, text=True, timeout=15,
        )
        lines = rev.stdout.splitlines()
        if rev.returncode != 0 or len(lines) < 2:
            return "unknown"
        top, commit = Path(lines[0]), lines[1].strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "-z", "--untracked-files=all"],
            cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
        if status.returncode == 0 and any(_key(top / p) not in _WRITTEN for p in _changed_paths(status.stdout)):
            commit += "-dirty"
        return commit
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def sha256_of(path: Path | str) -> str:
    """sha256 of a file, via the repo's canonical hashing module."""
    import sys

    scripts = str(REPO_ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from hashes import sha256_file  # type: ignore

    return sha256_file(Path(path))


@dataclass(frozen=True)
class ResultManifest:
    """What it takes to regenerate a result file."""

    result_file: str
    script: str
    git_commit: str
    seed: int | None
    parameters: dict[str, Any]
    timestamp: str
    sha256: str
    rows: int
    columns: list[str]
    description: str = ""
    exploratory: bool = False
    prereg_id: str | None = None
    variant_count: int | None = None
    notes: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None    # D-180: absent from manifests written before it
    git_dirty: bool | None = None               # D-183: the `-dirty` marker as a queryable field; None before it

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def manifest_path_for(csv_path: Path | str) -> Path:
    return Path(str(csv_path) + MANIFEST_SUFFIX)


def write_result(
    df: pd.DataFrame,
    name: str,
    *,
    script: str,
    seed: int | None,
    parameters: dict[str, Any],
    description: str = "",
    exploratory: bool = False,
    prereg_id: str | None = None,
    variant_count: int | None = None,
    notes: dict[str, Any] | None = None,
    results_dir: Path | str | None = None,
    require_seed: bool = True,
    provenance: dict[str, Any] | None = None,
    repo: Path | str | None = None,
) -> tuple[Path, Path]:
    """Write a result CSV and its sidecar manifest together.

    Args:
        df: the result.
        name: file name; `.csv` is appended if absent.
        script: the producing script, e.g. "scripts/run_protocol_comparison.py".
        seed: the seed. **Required** unless `require_seed=False`, which is only for results
            with genuinely no randomness (an exact chain, a closed form).
        parameters: everything else the run depended on. Be generous: a parameter you leave
            out is one nobody can reconstruct.
        exploratory: True if this configuration was chosen **after** seeing results. It is
            then reported separately from the pre-registered set -- stage one did this and
            labelled it (propsim D-44).
        prereg_id: the pre-registration this run belongs to.
        variant_count: how many configurations were tried, from
            `propedge.backtest.harness.VariantCounter`. Reported with the result.
        provenance: what else the result depended on (the engine pin, a fee-table date), from
            `propedge.reporting.pin`; recorded as given.
        repo: the repository whose git state is recorded; the repo root by default. Read
            before the CSV is written, so a clean tree records a clean commit (D-178).

    Returns:
        (csv_path, manifest_path).

    Raises:
        MissingProvenanceError: no script, or no seed when one is required.
    """
    if not script:
        raise MissingProvenanceError(
            "a result needs to say which script produced it; pass `script=`"
        )
    if require_seed and seed is None:
        raise MissingProvenanceError(
            "a result needs a seed. Every simulation in this stage is seeded -- a result "
            "nobody can reproduce is not a result. If this result genuinely has no "
            "randomness (an exact chain, a closed form), pass require_seed=False and say so "
            "in `description`."
        )

    results_dir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / (name if name.endswith(".csv") else f"{name}.csv")

    # D-178: the code state is read first. The CSV about to be written (and its manifest) would
    # otherwise show up as an untracked or modified file and mark every result `-dirty`.
    commit = git_commit(Path(repo) if repo is not None else None)

    df.to_csv(csv_path, index=False)
    note_written(csv_path)

    manifest = ResultManifest(
        result_file=csv_path.name,
        script=script,
        git_commit=commit,
        seed=seed,
        parameters=parameters,
        timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        sha256=sha256_of(csv_path),
        rows=int(len(df)),
        columns=[str(c) for c in df.columns],
        description=description,
        exploratory=exploratory,
        prereg_id=prereg_id,
        variant_count=variant_count,
        notes=notes,
        provenance=provenance,
        git_dirty=None if commit == "unknown" else commit.endswith("-dirty"),
    )
    mpath = manifest_path_for(csv_path)
    mpath.write_text(
        json.dumps(manifest.as_dict(), indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    note_written(mpath)
    return csv_path, mpath


def read_manifest(csv_path: Path | str) -> ResultManifest:
    """Read the sidecar manifest for a result CSV."""
    mpath = manifest_path_for(csv_path)
    if not mpath.is_file():
        raise FileNotFoundError(
            f"no manifest for {csv_path}. Every result file must have one "
            f"({mpath.name}); a result without provenance cannot be cited in a document. "
            "Regenerate it with propedge.reporting.results.write_result."
        )
    data = json.loads(mpath.read_text(encoding="utf-8"))
    return ResultManifest(**data)


def verify_result(csv_path: Path | str) -> tuple[bool, str]:
    """Check a result CSV still matches the sha256 in its manifest.

    Returns (ok, message). A mismatch means the CSV was edited after it was written, which is
    exactly what the results hook exists to prevent -- regenerate rather than patch.
    """
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        return False, f"{csv_path} does not exist"
    try:
        manifest = read_manifest(csv_path)
    except FileNotFoundError as exc:
        return False, str(exc)
    actual = sha256_of(csv_path)
    if actual != manifest.sha256:
        return False, (
            f"{csv_path.name} has been modified since it was written "
            f"(manifest {manifest.sha256[:12]}..., file {actual[:12]}...). "
            "Result files are never hand-edited; regenerate it."
        )
    return True, f"{csv_path.name} verified ({manifest.rows} rows, seed {manifest.seed})"


def read_result(csv_path: Path | str, *, verify: bool = True) -> pd.DataFrame:
    """Read a result CSV, checking its manifest first.

    Anything that puts a number in a document reads it through here, so a stale or edited
    file cannot silently reach a report.
    """
    csv_path = Path(csv_path)
    if verify:
        ok, msg = verify_result(csv_path)
        if not ok:
            raise ValueError(msg)
    return pd.read_csv(csv_path)


def list_results(results_dir: Path | str | None = None) -> list[dict[str, Any]]:
    """Every result CSV with its manifest status. Used by `/status` and `/close-check`."""
    results_dir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if not results_dir.is_dir():
        return []
    out = []
    for csv in sorted(results_dir.glob("*.csv")):
        ok, msg = verify_result(csv)
        row: dict[str, Any] = {"file": csv.name, "verified": ok, "message": msg}
        try:
            m = read_manifest(csv)
            row.update(
                seed=m.seed, script=m.script, git_commit=m.git_commit,
                exploratory=m.exploratory, prereg_id=m.prereg_id, rows=m.rows,
            )
        except FileNotFoundError:
            row["manifest"] = "MISSING"
        out.append(row)
    return out
