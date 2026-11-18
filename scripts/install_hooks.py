"""Install `scripts/pre-commit` and `scripts/post-commit` as the repository's git hooks.

    python scripts/install_hooks.py

The pre-commit hook checks the vendored snapshot (`scripts/vendor_stage2.py --verify`) and runs the suite's fast tier,
one at a time on the machine under the fast-tier lock (`scripts/fasttier_lock.py`, Q-155); the post-commit hook pushes each commit to the private remote `origin` in the background (E-004).

**Where.** Into `<git rev-parse --git-common-dir>/hooks/` -- the main repository's `.git/hooks/` -- which every linked
worktree (`%LOCALAPPDATA%\\stage2-extended-wt\\<name>`) and detached clean-run checkout shares, so one install covers
them all. Run it from the main tree or from any worktree: the destination is the same. The installed hook runs the
committing tree's own `scripts/` (the lock's wrapper included), so a tree that has not merged the change it calls is
refused with "merge master", never checked by less. If `core.hooksPath` is set, git
reads hooks from there instead, and this script says so rather than installing where git will not look.

Copies rather than symlinks, because symlinks into `.git/hooks` are unreliable on Windows without developer mode.
"""
from __future__ import annotations

import shutil
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The hooks installed, each copied from `scripts/<name>` into the common git directory's `hooks/`.
HOOKS = ("pre-commit", "post-commit")


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def common_dir() -> Path | None:
    """The git directory every worktree of this repository shares (`--git-common-dir`), absolute."""
    raw = _git("rev-parse", "--path-format=absolute", "--git-common-dir") or _git("rev-parse", "--git-common-dir")
    if not raw:
        return None
    p = Path(raw)
    return p if p.is_absolute() else (ROOT / p).resolve()


def main() -> int:
    gd = common_dir()
    if gd is None:
        print("not a git repository (or git is unavailable), so there is nowhere to install a hook.", file=sys.stderr)
        return 1
    hooks_path = _git("config", "--get", "core.hooksPath")
    if hooks_path:
        print(f"core.hooksPath is set ({hooks_path}): git reads hooks from there, not from {gd / 'hooks'}. Unset it "
              f"(git config --unset core.hooksPath) or install by hand; nothing installed.", file=sys.stderr)
        return 1

    hooks = gd / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    for name in HOOKS:
        src = ROOT / "scripts" / name
        if not src.is_file():
            print(f"missing {src}", file=sys.stderr)
            return 1
        data = src.read_bytes()
        if b"\r\n" in data:
            print(f"{src} has CRLF line endings; git's sh would fail on them (.gitattributes keeps it LF). Fix the "
                  f"checkout (git add --renormalize) and run again; nothing installed.", file=sys.stderr)
            return 1
        dst = hooks / name
        shutil.copyfile(src, dst)
        # chmod +x: a no-op on Windows but harmless, and needed elsewhere.
        dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"installed {dst}")

    print("  before every commit (main tree or worktree): `scripts/vendor_stage2.py --verify` and the fast tier "
          '(-m "not slow and not heavy"), one tree at a time under the machine-wide fast-tier lock '
          '(scripts/fasttier_lock.py: waits for a live holder and for 1.5 GB free, at most 3 h); the identity, the heavy tier and the vendored stage-one suite run in /validate')
    print(f"  after every commit on a branch: a background push to `origin` (log: {gd / 'push.log'})")
    print("bypass with `git commit --no-verify` only when you know why, and say so in the message")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
