"""Cross-platform sha256 manifest tools for stage two.

Manifest format is exactly the `sha256sum` / `shasum -a 256` format:

    <64 hex digits><two spaces><path relative to the manifest's directory>

so a manifest written here can be checked by the native tool on Linux
(`sha256sum -c MANIFEST.sha256`) or macOS (`shasum -a 256 -c MANIFEST.sha256`)
without translation. On Windows neither tool ships with the OS, so this module
is the canonical implementation and the shell wrappers in `scripts/` fall back
to it. Tests always use this module so they pass on every platform.

CLI:
    python scripts/hashes.py write <root> <manifest>   # hash every file under <root>
    python scripts/hashes.py check <manifest>          # verify, exit 1 on any failure
    python scripts/hashes.py tool                      # print the detected native tool
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

CHUNK = 1 << 20

# Directories that are build artefacts, never content.
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".ipynb_checkpoints"}


def detect_hash_tool() -> list[str] | None:
    """Return the native sha256 command as an argv prefix, or None.

    Linux ships `sha256sum`; macOS ships `shasum` (use `-a 256`). Windows ships
    neither. Callers that need a subprocess use this; callers that just need a
    digest should use `sha256_file`.
    """
    if shutil.which("sha256sum"):
        return ["sha256sum"]
    if shutil.which("shasum"):
        return ["shasum", "-a", "256"]
    return None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def iter_files(root: Path):
    """Every file under `root`, sorted, with build artefacts excluded."""
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


def write_manifest(root: Path, manifest: Path) -> int:
    """Hash every file under `root`; write paths relative to the manifest's dir."""
    root = root.resolve()
    manifest = manifest.resolve()
    base = manifest.parent
    lines = []
    for p in iter_files(root):
        rel = p.relative_to(base).as_posix()
        lines.append(f"{sha256_file(p)}  {rel}")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(lines)


def parse_manifest(manifest: Path) -> list[tuple[str, str]]:
    out = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        digest, _, rel = line.partition("  ")
        if not rel:
            raise ValueError(f"malformed manifest line: {line!r}")
        out.append((digest, rel))
    return out


def check_manifest(manifest: Path) -> tuple[list[str], list[str]]:
    """Return (ok_paths, failed_paths). A missing file counts as failed."""
    manifest = manifest.resolve()
    base = manifest.parent
    ok, bad = [], []
    for digest, rel in parse_manifest(manifest):
        target = base / rel
        if not target.is_file() or sha256_file(target) != digest:
            bad.append(rel)
        else:
            ok.append(rel)
    return ok, bad


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "tool":
        tool = detect_hash_tool()
        print(" ".join(tool) if tool else "none (using python hashlib)")
        return 0
    if cmd == "write":
        n = write_manifest(Path(argv[2]), Path(argv[3]))
        print(f"wrote {argv[3]}: {n} files")
        return 0
    if cmd == "check":
        ok, bad = check_manifest(Path(argv[2]))
        for rel in bad:
            print(f"{rel}: FAILED")
        print(f"{len(ok)} OK, {len(bad)} FAILED")
        return 1 if bad else 0
    print(f"unknown command {cmd!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
