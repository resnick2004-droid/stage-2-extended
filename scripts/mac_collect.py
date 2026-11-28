"""The lead's collect step for a Mac run (Q-229, E-298 (4)): fetch `mac/<run>`, check it, and copy its files into a
named holding folder outside `results/` -- refusing, with nothing copied, on any mismatch.

    python scripts/mac_collect.py --run h4b-naive-p1 --hold h4b-held
    # -> %LOCALAPPDATA%/stage2-extended-runs/h4b-held/h4b-naive-p1/  (each CSV, its manifest, run.log, run.json)

Run on this PC (the lead). The assignment is read from `origin/master`'s `config/mac_assignments.json`
(`extended.mac_assignments`), after a fetch. The branch is refused unless:

1. **the files are the ones the assignment expects**: its tree holds exactly each output, its sidecar manifest, the
   run's log (`run.log`) and the agent's record (`run.json`), every one a plain file (mode 100644); the record repeats
   the assignment's name, commit, command, task and outputs as origin/master has them; the log ends `EXIT 0`;
2. **every manifest's `git_commit` equals the assignment's commit** -- the full sha, so a `-dirty` one fails -- and its
   `git_dirty` is false; its `result_file` is its CSV's name and its `provenance.clean_run.name` is the run's;
3. **the host is named**: a manifest never records it (`extended/results.py` is frozen by W42-R1 and W42-R2, the
   lead's ruling in Q-229's corrective cycle), so it is taken, always, from the run's log -- its first line,
   `host: <name> (<platform>)`, written by the Mac's own `run_clean.py` -- and the agent's record (`run.json`), which
   must agree, with each manifest's `provenance.clean_run.checkout` a POSIX path ending `stage2-extended-runs/<run>` (a
   run made off Windows);
4. **`extended.results.verify_result` passes** on every CSV as copied (its manifest's sha256).

The files are read from git's objects (`git cat-file blob`), byte for byte, never through a checkout's line-ending
rule; staged in a temporary folder beside the holding folder and moved into place whole. A holding folder that
exists is never overwritten, and none may lie inside a `results/` folder or inside a tree of this repository.
Writes no record; the lead's decision row says what the files are for.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import RUNS_DIR  # noqa: E402
from extended import mac_assignments as MA  # noqa: E402

REMOTE = "origin"
RECORD, LOG = "run.json", "run.log"


class CollectRefused(RuntimeError):
    pass


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, timeout=600)
    if check and out.returncode:
        raise CollectRefused(f"git {' '.join(args)}: {out.stderr.decode('utf-8', 'replace').strip()}")
    return out


def _vendored_verify(csv: Path) -> tuple[bool, str]:
    from extended.results import verify_result   # the vendored check; this script is its own process
    return verify_result(csv)


def _inside_results_or_tree(p: Path) -> str | None:
    for q in (p, *p.parents):
        if q.name.lower() == "results":
            return f"{q} is a results/ folder"
        if (q / ".git").exists() and (q / "pyproject.toml").is_file():
            return f"{q} is a tree of this repository"
    return None


def check_branch(repo: Path, run_name: str, *, remote: str = REMOTE) -> tuple[MA.Run, dict[str, bytes], str]:
    """Fetch and check `mac/<run>`; its files' bytes by their branch path and the host evidence used. Raises
    CollectRefused on any mismatch (items 1 to 3 of the module docstring)."""
    if not MA.NAME.fullmatch(run_name):
        raise CollectRefused(f"{run_name!r} is not a run name")
    branch = f"refs/remotes/{remote}/mac/{run_name}"
    _git(repo, "fetch", "--quiet", remote, f"+refs/heads/master:refs/remotes/{remote}/master",
         f"+refs/heads/mac/{run_name}:{branch}")
    try:
        book = MA.parse(_git(repo, "show", f"refs/remotes/{remote}/master:{MA.CONFIG_REL}").stdout.decode("utf-8"))
    except MA.AssignmentError as exc:
        raise CollectRefused(f"origin/master's assignment file is refused: {exc}") from None
    run = book.by_name(run_name)
    if run is None:
        raise CollectRefused(f"origin/master's {MA.CONFIG_REL} has no run {run_name!r}")
    listing = _git(repo, "ls-tree", "-r", "-z", "--full-tree", branch).stdout.decode("utf-8").split("\0")
    entries: dict[str, str] = {}
    for rec in filter(None, listing):
        meta, path = rec.split("\t", 1)
        mode, kind, sha = meta.split()
        if mode != "100644" or kind != "blob":
            raise CollectRefused(f"{path} on the branch is not a plain file (mode {mode}, {kind})")
        entries[path] = sha
    want = MA.expected_files(run) | {LOG, RECORD}
    if set(entries) != want:
        raise CollectRefused(f"the branch's files are not the assignment's: missing {sorted(want - set(entries))}, "
                             f"not assigned {sorted(set(entries) - want)}")
    blobs = {p: _git(repo, "cat-file", "blob", sha).stdout for p, sha in entries.items()}
    try:
        record = json.loads(blobs[RECORD].decode("utf-8"))
    except ValueError as exc:
        raise CollectRefused(f"{RECORD} is not JSON ({exc})") from None
    if not isinstance(record, dict) or not MA.same_identity(record.get("assignment") or {}, run.as_dict()):
        raise CollectRefused(f"{RECORD}'s assignment is not origin/master's for {run_name} (name, commit, command, "
                             "task, outputs)")
    log_lines = blobs[LOG].decode("utf-8", "replace").splitlines()
    if not log_lines or log_lines[-1].strip() != "EXIT 0":
        raise CollectRefused(f"{LOG} does not end 'EXIT 0'")
    host = record.get("host")
    if not isinstance(host, str) or not host:
        raise CollectRefused(f"{RECORD} names no host")
    checkouts = []
    for o in run.outputs:
        try:
            m = json.loads(blobs[o + MA.MANIFEST_SUFFIX].decode("utf-8"))
        except ValueError as exc:
            raise CollectRefused(f"{o}'s manifest is not JSON ({exc})") from None
        if m.get("git_commit") != run.commit:
            raise CollectRefused(f"{o}'s manifest is at {m.get('git_commit')!r}, not the assignment's {run.commit}")
        if m.get("git_dirty") is not False:
            raise CollectRefused(f"{o}'s manifest is not clean (git_dirty {m.get('git_dirty')!r})")
        if m.get("result_file") != PurePosixPath(o).name:
            raise CollectRefused(f"{o}'s manifest is for {m.get('result_file')!r}")
        clean = (m.get("provenance") or {}).get("clean_run") or {}
        if clean.get("name") != run.name:
            raise CollectRefused(f"{o}'s manifest is not from the clean run {run.name} ({clean.get('name')!r})")
        checkouts.append(str(clean.get("checkout") or ""))
    first = log_lines[0].strip()
    if not (first.startswith(f"host: {host} (") and first.endswith(")")):
        raise CollectRefused(f"the log's first line ({first[:80]!r}) does not name the record's host {host!r}")
    for c in checkouts:
        parts = PurePosixPath(c).parts
        if not (c.startswith("/") and parts[-2:] == ("stage2-extended-runs", run.name)):
            raise CollectRefused(f"a manifest's checkout {c!r} is not a POSIX stage2-extended-runs/{run.name}")
    evidence = (f"host {host}: from the run's log and the record, each manifest's checkout a POSIX "
                "stage2-extended-runs path")
    return run, blobs, evidence


def collect(repo: Path, run_name: str, hold: Path, *, remote: str = REMOTE,
            verify: Callable[[Path], tuple[bool, str]] = _vendored_verify,
            say: Callable[[str], None] = lambda s: print(s, flush=True)) -> Path:
    """Check `mac/<run>` and copy its files into `hold/<run>/`; the folder made. Raises CollectRefused (nothing
    copied) on any mismatch."""
    hold = Path(os.path.abspath(hold))
    why = _inside_results_or_tree(hold)
    if why:
        raise CollectRefused(f"the holding folder {hold} is refused: {why}")
    dest = hold / run_name
    if dest.exists():
        raise CollectRefused(f"{dest} exists; a held file is never overwritten")
    run, blobs, evidence = check_branch(repo, run_name, remote=remote)
    hold.mkdir(parents=True, exist_ok=True)
    stage = hold / f".{run_name}.partial"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    try:
        for p, data in blobs.items():
            (stage / PurePosixPath(p).name).write_bytes(data)
        for o in run.outputs:
            ok, msg = verify(stage / PurePosixPath(o).name)
            if not ok:
                raise CollectRefused(f"verify_result refused {o}: {msg}")
        os.replace(stage, dest)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    say(f"COLLECTED mac/{run_name} into {dest}: {len(run.outputs)} result file(s) verified, at {run.commit[:12]}; "
        f"{evidence}")
    return dest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, help="the run's name (its branch is mac/<run>)")
    ap.add_argument("--hold", required=True, help="the holding folder's name under stage2-extended-runs, or a path")
    ap.add_argument("--repo", default=str(ROOT), help="the clone to fetch into (default: this tree)")
    a = ap.parse_args(argv)
    hold = Path(a.hold) if (os.sep in a.hold or "/" in a.hold) else RUNS_DIR / a.hold
    try:
        collect(Path(a.repo), a.run, hold)
    except CollectRefused as exc:
        print(f"REFUSED: {exc}; nothing copied", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
