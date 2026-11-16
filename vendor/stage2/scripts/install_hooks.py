"""Install `scripts/pre-commit` and `scripts/post-commit` as the repository's git hooks.

The pre-commit hook runs verify; the post-commit hook (R9) pushes each commit to the private backup remote `origin`
in the background (D-453).

Backs `make hooks` / `.\\scripts\\make.ps1 hooks`. Copies rather than symlinks, because
symlinks into `.git/hooks` are unreliable on Windows without developer mode.
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The hooks installed, each copied from `scripts/<name>` into the git directory's `hooks/`.
HOOKS = ("pre-commit", "post-commit")


def git_dir() -> Path | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    p = Path(out.stdout.strip())
    return p if p.is_absolute() else ROOT / p


def main() -> int:
    gd = git_dir()
    if gd is None:
        print(
            "not a git repository (or git is unavailable), so there is nowhere to install a "
            "hook. Run `git init` first.",
            file=sys.stderr,
        )
        return 1

    hooks = gd / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    for name in HOOKS:
        src = ROOT / "scripts" / name
        dst = hooks / name
        if not src.is_file():
            print(f"missing {src}", file=sys.stderr)
            return 1
        shutil.copyfile(src, dst)
        # chmod +x; a no-op on Windows but harmless, and git-bash needs it elsewhere.
        dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"installed {dst}")

    # The hook runs its steps itself and does NOT shell out to `make`, which does not ship with
    # Windows. Since R10 it runs vendor integrity and the fast tier only, not the whole of verify.
    print(
        "  before every commit it checks vendor integrity and runs the stage-two suite's fast tier "
        '(-m "not slow and not heavy"); the full suite and the vendored stage-one suite run in '
        "make verify and in CI (.github/workflows/verify.yml)"
    )
    print("  after every commit it pushes the branch to `origin` in the background (log: <git-dir>/push.log)")
    print("bypass with `git commit --no-verify` only when you know why, and say so in the message")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
