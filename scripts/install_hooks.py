"""Install `scripts/pre-commit`, `scripts/commit-msg` and `scripts/post-commit` as the repository's git hooks.

    python scripts/install_hooks.py

The pre-commit hook checks the vendored snapshot (`scripts/vendor_stage2.py --verify`) and runs the suite's fast tier,
one at a time on the machine under the fast-tier lock (`scripts/fasttier_lock.py`, Q-155), and records a verdict keyed
by the commit's tree only after the fast tier itself returned 0; the commit-msg hook refuses a commit whose pre-commit
started for that tree and recorded no verdict (a hook killed outright, which git on Windows reads as a pass; Q-161); the
post-commit hook warns about a commit without a verdict (`NO VERDICT`, also `scripts/check_verdicts.py <range>`) and
pushes each commit to the private remote `origin` in the background (E-004).

**Where.** Into `<git rev-parse --git-common-dir>/hooks/` -- the main repository's `.git/hooks/` -- which every linked
worktree (`%LOCALAPPDATA%\\stage2-extended-wt\\<name>`) and detached clean-run checkout shares, so one install covers
them all. Run it from the main tree or from any worktree: the destination is the same. The installed hook runs the
committing tree's own `scripts/` (the lock's wrapper included), so a tree that has not merged the change it calls is
refused with "merge master", never checked by less. If `core.hooksPath` is set, git
reads hooks from there instead, and this script says so rather than installing where git will not look.

Copies rather than symlinks, because symlinks into `.git/hooks` are unreliable on Windows without developer mode.
**Atomically** (Q-161): a running sh reads its script as it goes, so a hook is never rewritten in place -- each is
written to a temporary file in the hooks directory and `os.replace`d over the target. A commit whose hook is running
keeps reading the old file, whole; the next one reads the new file, whole. If the replace fails (Windows can refuse it
while a reader holds the file without delete-sharing), the installer says so, leaves the old hook and stops.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The hooks installed, each copied from `scripts/<name>` into the common git directory's `hooks/`.
HOOKS = ("pre-commit", "commit-msg", "post-commit")


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


def _replace_posix_windows(tmp: str, dst: str) -> None:
    """Rename `tmp` over `dst` with POSIX semantics (Windows 10 1709+): allowed while a reader holds `dst` open with
    delete-sharing -- as git's sh does a running hook -- and that reader keeps the old file. `os.replace`
    (MoveFileEx) is refused in that case. Raises OSError on failure."""
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                                wintypes.DWORD, wintypes.HANDLE)
    k32.SetFileInformationByHandle.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
    k32.CloseHandle.argtypes = (wintypes.HANDLE,)
    name = os.path.abspath(dst)

    class FileRenameInfo(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("RootDirectory", wintypes.HANDLE), ("FileNameLength", wintypes.DWORD),
                    ("FileName", ctypes.c_wchar * (len(name) + 1))]

    h = k32.CreateFileW(os.path.abspath(tmp), 0x00010000 | 0x00100000, 0x7, None, 3, 0x80, None)  # DELETE|SYNCHRONIZE
    if h in (None, wintypes.HANDLE(-1).value):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        info = FileRenameInfo(0x1 | 0x2, None, len(name) * 2, name)     # REPLACE_IF_EXISTS | POSIX_SEMANTICS
        if not k32.SetFileInformationByHandle(h, 22, ctypes.byref(info), ctypes.sizeof(info)):  # FileRenameInfoEx
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        k32.CloseHandle(h)


def _replace(tmp: str, dst: Path) -> None:
    if os.name == "nt":
        try:
            _replace_posix_windows(tmp, str(dst))
            return
        except OSError:
            pass                               # an older Windows or filesystem: the plain replace below
    os.replace(tmp, dst)


def install_one(src: Path, dst: Path) -> bool:
    """Install `src` as `dst` by an atomic replace, keeping its bytes (LF) and making it executable. False -- said on
    stderr, the old `dst` untouched, no temporary file left -- if the replace cannot be done."""
    data = src.read_bytes()
    try:
        mode = dst.stat().st_mode
    except FileNotFoundError:
        mode = src.stat().st_mode
    mode = stat.S_IMODE(mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    fd, tmp = tempfile.mkstemp(dir=dst.parent, prefix=f".{dst.name}.", suffix=".new")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)                    # chmod +x: a no-op on Windows but harmless, and needed elsewhere
        _replace(tmp, dst)
    except OSError as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        print(f"{dst}: NOT installed -- the replace failed ({e}); the old hook is left as it was. Let the commits "
              f"running it finish and run this again.", file=sys.stderr)
        return False
    return True


def install_all(hooks: Path, root: Path = ROOT) -> int:
    """Install every hook of HOOKS from `root/scripts` into `hooks`: 0, or 1 at the first that cannot be (that one
    and the rest left as they were). Every source is checked (present, LF) before any is installed."""
    hooks.mkdir(parents=True, exist_ok=True)
    sources = []
    for name in HOOKS:
        src = root / "scripts" / name
        if not src.is_file():
            print(f"missing {src}; nothing installed", file=sys.stderr)
            return 1
        if b"\r\n" in src.read_bytes():
            print(f"{src} has CRLF line endings; git's sh would fail on them (.gitattributes keeps it LF). Fix the "
                  f"checkout (git add --renormalize) and run again; nothing installed.", file=sys.stderr)
            return 1
        sources.append((name, src))
    for i, (name, src) in enumerate(sources):
        dst = hooks / name
        if not install_one(src, dst):
            print(f"stopped: {', '.join(n for n, _ in sources[i:])} not installed (each left as it was).",
                  file=sys.stderr)
            return 1
        print(f"installed {dst}")
    return 0


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

    if install_all(gd / "hooks") != 0:
        return 1

    print("  before every commit (main tree or worktree): `scripts/vendor_stage2.py --verify` and the fast tier "
          '(-m "not slow and not heavy"), one tree at a time under the machine-wide fast-tier lock '
          '(scripts/fasttier_lock.py: waits for a live holder and for 1.5 GB free, at most 3 h); the identity, the heavy tier and the vendored stage-one suite run in /validate')
    print(f"  the verdict: tree, time, worktree and pass line in {gd / 'fasttier-verdicts.log'}, written only when the "
          f"fast tier returned 0; commit-msg refuses a tree whose pre-commit was killed; post-commit logs NO VERDICT; "
          f"`python scripts/check_verdicts.py <range>` lists commits without one")
    print(f"  after every commit on a branch: a background push to `origin` (log: {gd / 'push.log'})")
    print("bypass with `git commit --no-verify` only when you know why, and say so in the message")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
