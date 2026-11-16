"""Run a registered script from a clean, detached checkout of one commit, then bring its result files home (D-474).

The local stand-in for R10's `verdict` workflow while GitHub Actions is unavailable (D-466). A registered run reads
its result's `git_commit` when it writes the CSV (D-178); in the shared working tree any session's file -- an audit
report, an agent's merge -- stamps the result `-dirty` for the hour a verdict runs. Here the run gets its own tree:

    python scripts/run_clean.py --name p11 -- python scripts/a1_ins15.py --prereg P-11
    python scripts/run_clean.py --name p11 --collect      # copy the run's result files into this tree
    python scripts/run_clean.py --name p11 --remove       # unlink the stores, remove the checkout

1. `git worktree add --detach` at the commit (default HEAD; the main tree must be clean so HEAD is what was meant)
   in a folder outside OneDrive (OneDrive locks files under a running job), `%LOCALAPPDATA%/stage2-runs/<name>`.
2. The git-ignored stores the code reads by `REPO_ROOT` -- `data/bars` (D-458) and `data/atlas` (D-460) -- are linked
   in as directory junctions, read where they are; the checkout's `git status` must be empty before the command runs.
3. The command runs inside the checkout with one BLAS thread (D-464 (5)); its output goes to `<name>.log` beside
   the checkout (never inside it: an untracked log would stamp the result `-dirty`).
4. `--collect` copies every file the run changed or created into this tree, refusing a file this tree has changed
   since the commit (the run's copy and this tree's would both be edits of one file).
5. `--remove` unlinks the junctions first -- never through them -- then removes the checkout.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs"
#: git-ignored stores the code reads under REPO_ROOT; linked, never copied
STORES = ("data/bars", "data/atlas")
BLAS = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


def _git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    out = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True, encoding="utf-8")
    if check and out.returncode:
        raise SystemExit(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def _changed(cwd: Path) -> list[str]:
    """Paths `git status` reports in `cwd`, untracked files included (renames give their new path)."""
    parts = _git("status", "--porcelain", "-z", "--untracked-files=all", cwd=cwd).split("\0")
    paths, skip = [], False
    for p in parts:
        if skip:
            skip = False
            continue
        if len(p) > 3:
            paths.append(p[3:])
            skip = p[0] in "RC"
    return paths


def _is_junction(p: Path) -> bool:
    """A directory junction (Windows) or a symbolic link (elsewhere): a link to a store, never the store itself."""
    return p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())


def _link(link: Path, target: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if _is_junction(link):
        return
    if link.exists():
        raise SystemExit(f"{link} exists and is not a junction")
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True)
    else:
        os.symlink(target, link, target_is_directory=True)


def _unlink(link: Path) -> None:
    if _is_junction(link):
        if link.is_symlink():
            link.unlink()                    # the link only, never the store behind it
        else:
            os.rmdir(link)                   # a junction: rmdir removes the link, never the store behind it


def create(name: str, commit: str) -> Path:
    if _changed(ROOT) and commit == "HEAD":
        raise SystemExit("this tree has uncommitted changes: commit them, or name the commit with --commit")
    sha = _git("rev-parse", "--verify", f"{commit}^{{commit}}").strip()
    wt = RUNS / name
    if wt.exists():
        raise SystemExit(f"{wt} exists: --remove it first")
    RUNS.mkdir(parents=True, exist_ok=True)
    _git("worktree", "add", "--detach", str(wt), sha)
    for s in STORES:
        if (ROOT / s).is_dir():
            _link(wt / s, ROOT / s)
    dirty = _changed(wt)
    if dirty:
        raise SystemExit(f"the checkout is not clean after linking the stores: {dirty[:5]}")
    print(f"checkout {wt} at {sha[:7]}, clean; stores linked: {[s for s in STORES if _is_junction(wt / s)]}")
    return wt


def run(wt: Path, cmd: list[str]) -> int:
    env = {**os.environ, **BLAS, "PYTHONUNBUFFERED": "1"}
    log = wt.parent / f"{wt.name}.log"
    print(f"running in {wt}: {' '.join(cmd)}  (log: {log})", flush=True)
    with log.open("w", encoding="utf-8") as f:
        p = subprocess.Popen(cmd, cwd=wt, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace")
        assert p.stdout is not None
        for line in p.stdout:
            f.write(line)
            f.flush()
            sys.stdout.write(line)
            sys.stdout.flush()
        rc = p.wait()
        f.write(f"EXIT {rc}\n")
    print(f"EXIT {rc}")
    return rc


def collect(wt: Path) -> list[str]:
    sha = _git("rev-parse", "HEAD", cwd=wt).strip()
    produced = _changed(wt)
    if not produced:
        print("the run changed no file")
        return []
    here = set(_changed(ROOT))
    clash = [p for p in produced if p in here]
    if clash:
        raise SystemExit(f"this tree changed these since the run's commit; nothing copied: {clash}")
    if _git("rev-parse", "HEAD").strip() != sha:
        moved = _git("diff", "--name-only", sha, "HEAD").split()
        clash = [p for p in produced if p in moved]
        if clash:
            raise SystemExit(f"commits since {sha[:7]} changed these; nothing copied: {clash}")
    for p in produced:
        dst = ROOT / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wt / p, dst)
        print(f"copied {p}")
    return produced


def remove(name: str) -> None:
    wt = RUNS / name
    for s in STORES:
        _unlink(wt / s)
    if any(_is_junction(wt / s) for s in STORES):
        raise SystemExit("a junction is still in place; not removing the checkout")
    _git("worktree", "remove", "--force", str(wt))
    print(f"removed {wt}")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd: list[str] = []
    if "--" in argv:
        i = argv.index("--")
        argv, cmd = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name", required=True, help="the checkout's folder name under %%LOCALAPPDATA%%/stage2-runs")
    ap.add_argument("--commit", default="HEAD")
    ap.add_argument("--collect", action="store_true", help="copy the run's result files into this tree")
    ap.add_argument("--remove", action="store_true", help="unlink the stores and remove the checkout")
    a = ap.parse_args(argv)
    if a.remove:
        remove(a.name)
        return 0
    if a.collect:
        collect(RUNS / a.name)
        return 0
    if not cmd:
        ap.error("give the command after --")
    wt = RUNS / a.name if (RUNS / a.name).exists() else create(a.name, a.commit)
    if _changed(wt):
        raise SystemExit(f"{wt} is not clean: {_changed(wt)[:5]}")
    return run(wt, cmd)


if __name__ == "__main__":
    raise SystemExit(main())
