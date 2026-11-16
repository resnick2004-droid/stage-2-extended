"""Stage two's integrity manifest (T10; the closing checklist's "the stage's integrity manifest").

    python scripts/stage_manifest.py write    # STAGE_MANIFEST.sha256 from the committed tree; prints its own sha256
    python scripts/stage_manifest.py check    # recompute from HEAD and compare

Every file tracked at HEAD is hashed from its **committed content** (read with `git cat-file`), so the manifest does
not depend on a checkout's line-ending conversion. Excluded: `vendor/` (pinned separately by
`vendor/MANIFEST.sha256`, D-01), and the two close files that must record this manifest -- `CLOSED.md` and
`STAGE_MANIFEST.sha256` itself. Format: native `sha256sum` lines (`<hash>  <path>`), sorted by path.
Refuses to write while tracked files differ from HEAD: a manifest of a dirty tree describes nothing that exists.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "STAGE_MANIFEST.sha256"
EXCLUDE_PREFIXES = ("vendor/",)
EXCLUDE_FILES = {"CLOSED.md", "STAGE_MANIFEST.sha256"}


def _git(*args: str, input_: bytes | None = None) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, input=input_, capture_output=True, check=True).stdout


def tracked_paths() -> list[str]:
    paths = _git("ls-tree", "-r", "--name-only", "-z", "HEAD").decode("utf-8").split("\0")
    return sorted(p for p in paths if p and not p.startswith(EXCLUDE_PREFIXES) and p not in EXCLUDE_FILES)


def committed_hashes(paths: list[str]) -> list[tuple[str, str]]:
    """sha256 of each path's content at HEAD, streamed through one `git cat-file --batch`."""
    req = "".join(f"HEAD:{p}\n" for p in paths).encode("utf-8")
    out = _git("cat-file", "--batch", input_=req)
    res, pos = [], 0
    for p in paths:
        nl = out.index(b"\n", pos)
        header = out[pos:nl].split()
        size = int(header[2])
        body = out[nl + 1:nl + 1 + size]
        res.append((hashlib.sha256(body).hexdigest(), p))
        pos = nl + 1 + size + 1                      # the content is followed by a newline
    return res


def render() -> str:
    return "".join(f"{h}  {p}\n" for h, p in committed_hashes(tracked_paths()))


def main(argv: list[str]) -> int:
    mode = argv[0] if argv else "write"
    if mode == "write":
        if subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=ROOT).returncode != 0:
            print("REFUSED: tracked files differ from HEAD; commit first, then write the manifest.")
            return 2
        text = render()
        MANIFEST.write_text(text, encoding="utf-8", newline="\n")
        own = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
        print(f"wrote {MANIFEST.name}: {text.count(chr(10))} files; its own sha256 {own}")
        return 0
    if mode == "check":
        if not MANIFEST.is_file():
            print("no STAGE_MANIFEST.sha256")
            return 1
        ok = MANIFEST.read_text(encoding="utf-8") == render()
        print("stage manifest matches HEAD" if ok else "STAGE MANIFEST DIFFERS FROM HEAD")
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
