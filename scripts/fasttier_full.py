"""The full fast tier on this tree's committed tip, recorded as its verdict (Q-209): for a tip no pre-commit tested.

    python scripts/fasttier_full.py           # T2 on HEAD's tree, under the machine-wide fast-tier lock
    python scripts/fasttier_full.py --force   # run it again even if HEAD's tree already has a T2 verdict

Every commit's pre-commit runs the full fast tier on its own tree, but a clean merge runs no pre-commit: a worker whose
last commit merged master has a tip no fast tier tested, and the lead's merge gate (commit-msg) and
`scripts/check_verdicts.py master..wt/<name>` refuse such a tip. Run this in that tree before the hand-back. This runs exactly the hook's T2 command -- `scripts/fasttier_lock.py run -- scripts/fasttier_xdist.py
-m "not slow and not heavy"` (the serial pytest command where the xdist runner is absent) -- and, only when it returned
0, appends HEAD's tree to `<git-common-dir>/fasttier-verdicts.log` with `tier=T2`, as the hook would have.

**The tree must be HEAD** (the red team's F12): no tracked change, staged or not, and no untracked file that .gitignore
does not ignore -- anywhere, since a test may read any file -- but the log files at the tree's top level (the commit
logs the worker protocol keeps inside the worktree), as the pre-commit hook allows. It is checked before and again
after the run (a change during it, or a moved HEAD, records nothing). Exit codes: the fast tier's own when it failed;
0 passed (or already verified); 3 the tree is not clean; 75/76 the lock's.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_verdicts import LOG_NAME, tree_has_t2  # noqa: E402

FAST_TIER = "not slow and not heavy"
EXIT_DIRTY = 3


def _env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _git(*args: str, root: Path = ROOT) -> str:
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=300, env=_env())
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def dirt(root: Path = ROOT) -> list[str]:
    """What makes the work tree differ from HEAD for a test run: tracked changes, and every untracked file .gitignore
    does not ignore, but top-level logs (F12)."""
    out = []
    for line in _git("status", "--porcelain", "--untracked-files=all", root=root).splitlines():
        code, path = line[:2], line[3:].strip().strip('"')
        if code == "??":
            if not ("/" not in path and path.endswith(".log")):
                out.append(f"untracked {path}")
        elif code.strip():
            out.append(f"changed {path}")
    return out


def command(python: str, root: Path, gitdir: Path) -> list[str]:
    """The hook's T2 command."""
    lock = [python, "scripts/fasttier_lock.py", "run", "--"]
    if (root / "scripts" / "fasttier_xdist.py").is_file():
        return lock + [python, "scripts/fasttier_xdist.py", "--work", str(gitdir / "fasttier-xdist"), "-m", FAST_TIER]
    return lock + [python, "-m", "pytest", "-o", "addopts=", "-q", "-m", FAST_TIER]


def summary(text: str) -> str:
    lines = [ln.strip().replace("\t", " ") for ln in text.splitlines() if " passed" in ln and any(c.isdigit() for c in ln)]
    return lines[-1] if lines else "-"


def main(argv: list[str] | None = None, runner=None, root: Path = ROOT) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--force", action="store_true", help="run even if HEAD's tree already has a T2 verdict")
    a = ap.parse_args(argv)
    gitdir = Path(_git("rev-parse", "--absolute-git-dir", root=root).strip())
    common = Path(_git("rev-parse", "--path-format=absolute", "--git-common-dir", root=root).strip())
    log = common / LOG_NAME
    head = _git("rev-parse", "HEAD", root=root).strip()
    tree = _git("rev-parse", "HEAD^{tree}", root=root).strip()
    bad = dirt(root)
    if bad:
        print("fasttier_full: REFUSED -- the work tree is not HEAD, so a verdict for HEAD's tree would not be what ran: "
              + "; ".join(bad[:15]) + (f" and {len(bad) - 15} more" if len(bad) > 15 else ""), file=sys.stderr)
        return EXIT_DIRTY
    if tree_has_t2(tree, log) and not a.force:
        print(f"fasttier_full: HEAD {head[:10]}'s tree {tree[:12]} already has a T2 verdict in {log}; nothing to run "
              f"(--force runs it again)")
        return 0
    tee = gitdir / "fasttier-full.log"
    tee.unlink(missing_ok=True)
    env = _env()
    env["S2X_FASTTIER_TEE"] = str(tee)
    cmd = command(sys.executable, root, gitdir)
    print(f"fasttier_full: T2 (the full fast tier) on HEAD {head[:10]}, tree {tree[:12]}: {' '.join(cmd)}", flush=True)
    rc = (runner or (lambda c, e: subprocess.run(c, cwd=root, env=e).returncode))(cmd, env)
    if rc != 0:
        print(f"fasttier_full: the fast tier FAILED (exit {rc}); no verdict recorded. Output: {tee}", file=sys.stderr)
        return rc
    now_head = _git("rev-parse", "HEAD", root=root).strip()
    bad = dirt(root)
    if now_head != head or bad:
        print(f"fasttier_full: REFUSED to record -- the tree moved during the run (HEAD {head[:10]} -> {now_head[:10]}"
              f"{'; ' + '; '.join(bad[:5]) if bad else ''})", file=sys.stderr)
        return EXIT_DIRTY
    text = tee.read_text(encoding="utf-8", errors="replace") if tee.is_file() else ""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with log.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"{tree}\t{stamp}\t{root.as_posix()}\t{summary(text)}\ttier=T2\tby=fasttier_full {head}\n")
    print(f"fasttier_full: OK -- T2 verdict recorded for tree {tree[:12]} (HEAD {head[:10]}) in {log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
