"""The standing worktrees (E-006): created, synced, listed and removed outside OneDrive, the licensed data linked in.

    python scripts/worktrees.py create wt-verify            # branch wt/wt-verify from master, the data junctions linked
    python scripts/worktrees.py sync wt-verify              # fast-forward a clean worktree's branch to master
    python scripts/worktrees.py list                        # every worktree: branch, head, clean, junctions
    python scripts/worktrees.py remove wt-verify            # junctions unlinked first, then the worktree (branch kept)

Worktrees live in `%LOCALAPPDATA%/stage2-extended-wt/<name>` (OneDrive locks files under running jobs and broke
in-repo worktrees in Stage 2), each on its own branch `wt/<name>`. The licensed bars and atlas (git-ignored; one copy
in this tree, E-002, E-005 (b)) are linked into each worktree as **directory junctions** -- read in place, never
copied, never written. `remove` unlinks a junction with `os.rmdir` on the link itself, never through it, and refuses
to remove a worktree while any junction is still in place, so the store behind it can never be deleted.

`sync` only fast-forwards: a branch with commits master does not have is the lead's to merge first (the
merge checklist), and a worktree with uncommitted changes is never touched.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WT = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-extended-wt"
#: the git-ignored licensed stores, linked into every worktree from this tree's one copy
STORES = ("vendor/stage2/data/bars", "vendor/stage2/data/atlas")
BASE = "master"


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if check and out.returncode:
        raise SystemExit(f"git {' '.join(args)} (in {cwd}): {out.stderr.strip()}")
    return out.stdout.strip()


def is_link(p: Path) -> bool:
    """A directory junction (Windows) or a symbolic link: a link to a store, never the store itself."""
    return p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())


def changed(cwd: Path) -> list[str]:
    """Paths `git status` reports, untracked included. Parsed from `-z` output, never stripped: stripping cost the first
    entry its leading status space and so its path its first character (found by the Q-05 worker, E-010)."""
    out = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=cwd,
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        raise SystemExit(f"git status (in {cwd}): {out.stderr.strip()}")
    paths, skip = [], False
    for entry in out.stdout.split("\0"):
        if skip:
            skip = False
            continue
        if len(entry) > 3:
            paths.append(entry[3:])
            skip = entry[0] in "RC"
    return paths


def link(wt: Path, store: str) -> None:
    src, dst = ROOT / store, wt / store
    if not src.is_dir():
        raise SystemExit(f"{src} is missing: run scripts/vendor_stage2.py --data in this tree first")
    if is_link(dst):
        return
    if dst.exists():
        raise SystemExit(f"{dst} exists and is not a junction: refusing (a copy of the licensed data is never made)")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(dst), str(src)], check=True, capture_output=True)
    else:
        _exclude_store_links()
        os.symlink(src, dst, target_is_directory=True)


def _exclude_store_links(root: Path = ROOT) -> None:
    """Q-229: off Windows a store is linked by a symbolic link, which git sees as a file, so `.gitignore`'s
    directory-only patterns (`vendor/stage2/data/bars/`) do not hide it and every checkout would read as untracked --
    at any commit, old ones included. The repository's own `info/exclude` (shared by every worktree, never committed)
    gets each store's path without the trailing slash, once."""
    common = Path(git("rev-parse", "--git-common-dir", cwd=root).strip())
    if not common.is_absolute():
        common = (root / common).resolve()
    ex = common / "info" / "exclude"
    ex.parent.mkdir(parents=True, exist_ok=True)
    text = ex.read_text(encoding="utf-8") if ex.is_file() else ""
    have = [ln.strip() for ln in text.splitlines()]
    add = [f"/{s}" for s in STORES if f"/{s}" not in have]
    if add:
        lead = "\n" if text and not text.endswith("\n") else ""
        with ex.open("a", encoding="utf-8", newline="\n") as f:
            f.write(lead + "# the licensed stores' symbolic links (scripts/worktrees.py, Q-229)\n" + "\n".join(add) + "\n")


def unlink(wt: Path, store: str) -> None:
    p = wt / store
    if p.is_symlink():
        p.unlink()          # the link only
    elif is_link(p):
        os.rmdir(p)         # a junction: rmdir removes the link, never the store behind it


def create(name: str) -> Path:
    wt = WT / name
    if wt.exists():
        raise SystemExit(f"{wt} exists (sync it, or remove it first)")
    WT.mkdir(parents=True, exist_ok=True)
    branch = f"wt/{name}"
    have = git("branch", "--list", branch)
    if have:
        git("worktree", "add", str(wt), branch)
    else:
        git("worktree", "add", "-b", branch, str(wt), BASE)
    for s in STORES:
        link(wt, s)
    dirty = changed(wt)
    if dirty:
        raise SystemExit(f"{wt} is not clean after linking the stores: {dirty[:5]}")
    print(f"created {wt} on {branch} at {git('rev-parse', '--short', 'HEAD', cwd=wt)}; "
          f"junctions: {[s for s in STORES if is_link(wt / s)]}; clean")
    return wt


def sync(name: str) -> None:
    wt = WT / name
    if not wt.is_dir():
        raise SystemExit(f"{wt} does not exist")
    dirty = changed(wt)
    if dirty:
        raise SystemExit(f"{wt} has uncommitted changes, not synced: {dirty[:5]}")
    head = git("rev-parse", "HEAD", cwd=wt)
    base = git("rev-parse", BASE)
    if head == base:
        print(f"{name}: already at {BASE} ({base[:7]})")
        return
    ahead = git("rev-list", "--count", f"{BASE}..{head}")
    if ahead != "0":
        raise SystemExit(f"{name}: its branch has {ahead} commit(s) {BASE} lacks -- the lead merges them first")
    git("merge", "--ff-only", BASE, cwd=wt)
    for s in STORES:
        link(wt, s)
    print(f"{name}: fast-forwarded to {BASE} ({base[:7]})")


def remove(name: str) -> None:
    wt = WT / name
    for s in STORES:
        unlink(wt, s)
    left = [s for s in STORES if is_link(wt / s) or (wt / s).exists()]
    if left:
        raise SystemExit(f"{left} still in place under {wt}: not removing the worktree")
    git("worktree", "remove", str(wt))
    print(f"removed {wt} (branch wt/{name} kept)")


def listing() -> None:
    blocks = git("worktree", "list", "--porcelain").split("\n\n")
    for b in blocks:
        f = dict(line.split(" ", 1) if " " in line else (line, "") for line in b.splitlines())
        p = Path(f.get("worktree", ""))
        if not p.is_dir():
            continue
        links = [s.rsplit("/", 1)[-1] for s in STORES if is_link(p / s)]
        n = len(changed(p))
        print(f"{p}  {f.get('branch', '(detached)').replace('refs/heads/', '')}  {f.get('HEAD', '')[:7]}  "
              f"{'clean' if n == 0 else f'{n} changed'}  junctions={links}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("action", choices=("create", "sync", "remove", "list"))
    ap.add_argument("name", nargs="?")
    a = ap.parse_args(argv)
    if a.action == "list":
        listing()
        return 0
    if not a.name:
        ap.error("give the worktree's name")
    {"create": create, "sync": sync, "remove": remove}[a.action](a.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
