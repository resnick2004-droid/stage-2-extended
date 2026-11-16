"""Re-vendor the multi-firm repository's Lucid subset into vendor/propfirms/ from one of its commits (D-463 (4)).

vendor/propfirms/ is read-only: the Claude hook (`scripts/hooks/protect_vendor.py`) refuses any Write or Edit under it
and `tests/test_vendor_propfirms.py` pins every byte. A re-vendor is the one sanctioned way the tree changes (D-463
(4): "the multi-firm ledger re-verified and re-vendored"), and it is this script -- an exact, scripted copy -- never a
hand edit:

* the file subset is the one the current manifest lists (`vendor/MANIFEST_propfirms.sha256`), mapped back to the
  source repository by dropping the leading `propfirms/`; `--add` names a file the subset now needs and `--drop` one it
  no longer has (a renamed source file is one of each), so the subset never changes silently;
* every file is read from the commit's object store with `git -C <repo> cat-file blob <commit>:<path>` -- the bytes as
  committed, the same bytes `git show <commit>:<path>` prints when no textconv driver is set, never the working tree
  (which may be dirty) and never through a line-ending filter;
* a path the commit does not hold stops the copy before anything is written;
* the tree is made to hold exactly the listed files (a file no longer listed is removed), and the manifest is rewritten
  in its format -- the header (`source`, `remote`, `commit`, `copied`, `format`) and one `sha256sum` line per file,
  paths relative to vendor/, sorted -- with LF line ends.

Usage (the 2026-10-30 re-vendor, the multi-firm repository's D-30):

    python scripts/vendor_propfirms.py --repo "C:/Users/resni/OneDrive/Desktop/Stage 1- XFA Eval Repository" \
        --commit 2d17fb8 --label "D-30: Lucid re-verified on its official help centre" --date 2026-10-30

`--check` copies nothing: it reads the commit and reports, file by file, what a re-vendor would change (with the
current manifest's commit it is the proof that the script reproduces the vendored tree exactly).
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"
TREE_NAME = "propfirms"
MANIFEST_NAME = "MANIFEST_propfirms.sha256"
DEFAULT_REPO = "C:/Users/resni/OneDrive/Desktop/Stage 1- XFA Eval Repository"

HEADER_FIRST = ("# vendor/propfirms -- the multi-firm repository's Lucid subset, vendored read-only (Stage 2 R7; "
                "docs/TWO_FIRMS.md).")
HEADER_FORMAT = ("# format: sha256sum native (<digest><two spaces><path relative to vendor/>); checked by "
                 "tests/test_vendor_propfirms.py")


class VendorError(RuntimeError):
    """The copy cannot be made exactly; nothing has been written."""


def _git(repo: str, *args: str) -> bytes:
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True, check=False)
    if proc.returncode != 0:
        raise VendorError(f"git {' '.join(args)} failed in {repo}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def listed_paths(manifest: Path) -> list[str]:
    """The manifest's paths, relative to vendor/ (`propfirms/...`), in its order."""
    out = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        _, sep, rel = line.partition("  ")
        if not sep or not rel.startswith(f"{TREE_NAME}/"):
            raise VendorError(f"{manifest.name}: unexpected line {line!r}")
        out.append(rel)
    return out


def subset(manifest: Path, add: list[str], drop: list[str]) -> list[str]:
    """The source paths to copy: the manifest's, less `drop`, plus `add`, sorted; each named once."""
    current = [rel.split("/", 1)[1] for rel in listed_paths(manifest)]
    missing = [p for p in drop if p not in current]
    if missing:
        raise VendorError(f"--drop names paths the manifest does not list: {missing}")
    dup = [p for p in add if p in current and p not in drop]
    if dup:
        raise VendorError(f"--add names paths the manifest already lists: {dup}")
    return sorted(set(p for p in current if p not in drop) | set(add))


def read_commit(repo: str, commit: str, paths: list[str]) -> tuple[str, str, dict[str, bytes]]:
    """(full sha, short sha, {path: committed bytes}); raises before anything is written if a path is absent."""
    full = _git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    short = _git(repo, "rev-parse", "--short=7", full).decode().strip()
    absent = [p for p in paths
              if subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{full}:{p}"], capture_output=True).returncode]
    if absent:
        raise VendorError(f"commit {short} holds no {absent}: a renamed file is --drop <old> --add <new>; a deleted one "
                          "is --drop <old> under a decision")
    return full, short, {p: _git(repo, "cat-file", "blob", f"{full}:{p}") for p in paths}


def header(repo: str, short: str, label: str, date: str) -> list[str]:
    try:
        remote = _git(repo, "remote", "get-url", "origin").decode().strip()
    except VendorError:
        remote = "(none)"
    return [
        HEADER_FIRST,
        f"# source: {repo} (package propfirms)",
        f"# remote: {remote}",
        f"# commit: {short} ({label}); each file read with `git cat-file blob {short}:<path>` (the committed bytes) by "
        "scripts/vendor_propfirms.py",
        f"# copied: {date}",
        HEADER_FORMAT,
    ]


def plan(dest: Path, blobs: dict[str, bytes]) -> dict[str, str]:
    """{path relative to the tree: 'added' | 'changed' | 'unchanged' | 'removed'}."""
    tree = dest / TREE_NAME
    out: dict[str, str] = {}
    for p, data in blobs.items():
        f = tree / p
        out[p] = "added" if not f.is_file() else ("unchanged" if f.read_bytes() == data else "changed")
    if tree.is_dir():
        for f in tree.rglob("*"):
            rel = f.relative_to(tree).as_posix()
            if f.is_file() and rel not in blobs:
                out[rel] = "removed"
    return dict(sorted(out.items()))


def write(dest: Path, blobs: dict[str, bytes], head: list[str]) -> Path:
    tree = dest / TREE_NAME
    for p, data in blobs.items():
        f = tree / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    for f in sorted(tree.rglob("*"), reverse=True):
        rel = f.relative_to(tree).as_posix()
        if f.is_file() and rel not in blobs:
            f.unlink()
        elif f.is_dir() and not any(f.iterdir()):
            f.rmdir()
    lines = head + [f"{hashlib.sha256(blobs[p]).hexdigest()}  {TREE_NAME}/{p}" for p in sorted(blobs)]
    manifest = dest / MANIFEST_NAME
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=DEFAULT_REPO, help="the multi-firm repository (read only)")
    ap.add_argument("--commit", required=True, help="the revision to vendor")
    ap.add_argument("--label", help="the header's note on the commit, e.g. its decision row (required unless --check)")
    ap.add_argument("--date", help="the copy's date, YYYY-MM-DD (required unless --check)")
    ap.add_argument("--dest", default=str(VENDOR), help="the vendor directory (default: this repository's vendor/)")
    ap.add_argument("--add", action="append", default=[], help="a source path the subset now needs (repeatable)")
    ap.add_argument("--drop", action="append", default=[], help="a listed source path to remove (repeatable)")
    ap.add_argument("--check", action="store_true", help="report what a re-vendor would change; write nothing")
    a = ap.parse_args(argv)

    dest = Path(a.dest)
    manifest = dest / MANIFEST_NAME
    try:
        paths = subset(manifest, a.add, a.drop)
        full, short, blobs = read_commit(a.repo, a.commit, paths)
    except VendorError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    changes = plan(dest, blobs)
    for p, what in changes.items():
        print(f"{what:9s} {TREE_NAME}/{p}")
    print(f"{len(blobs)} files from {short} ({full})")
    if a.check:
        return 0 if all(w == "unchanged" for w in changes.values()) else 1
    if not a.label or not a.date:
        print("refused: --label and --date are required to write", file=sys.stderr)
        return 2
    out = write(dest, blobs, header(a.repo, short, a.label, a.date))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
