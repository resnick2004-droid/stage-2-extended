"""The heavy-test guard (Q-118, E-145): a test marked `heavy` never runs while another process holds the run lock.

    from extended.lock_guard import heavy_skip_reason   # None: heavy tests may run; else the reason they are skipped

The run lock is `run.lock` at the **main** repository's root (`scripts/run_lock.py`, skill `run-lock`). Every
worktree and clean checkout shares that root through `git rev-parse --git-common-dir`; its parent is the main tree.
The root `conftest.py` calls `heavy_skip_reason` once per collection that holds a `heavy` test and, when it gives a
reason, skips every such test with it. The rule:

- no `run.lock` at the main root: no skip from here (a test's own markers still apply);
- `run.lock` present, and this process is not its holder: skip, with the reason
  "heavy test skipped: run.lock held by <job> (only the lock's holder may run heavy tests)";
- the holder is the command `scripts/run_clean.py` launches under the lock: it sets `S2X_LOCK_HOLDER=<job>` in that
  command's environment (inherited by its children), and a heavy test runs only when that variable equals the lock's
  `job`. A session that takes the lock by hand (`run_lock.py take`) and runs heavy tests in its worktree sets the
  same variable to its own job for that command;
- the main root cannot be found (no git, not a work tree, a bare or separate git dir whose parent is not the main
  tree): skip -- the lock cannot be checked, so heavy tests do not run.

A lock that exists but cannot be read is held (by an unknown job): it is never ignored. A stale lock is still held:
the guard does not judge staleness (that is the lead's question, never a licence). Light code only: the standard
library and one `git` call.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Mapping

#: the variable `scripts/run_clean.py` sets for the command it runs under the lock: the lock's job name
LOCK_HOLDER_ENV = "S2X_LOCK_HOLDER"
#: the lock's file name at the main repository's root (`scripts/run_lock.py`'s LOCK)
LOCK_NAME = "run.lock"

_HERE = Path(__file__).resolve().parent.parent


def main_root(start: Path | str | None = None) -> Path | None:
    """The main repository's root as seen from `start` (default: this tree), or None when it cannot be found."""
    cwd = Path(start) if start is not None else _HERE
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=cwd,
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    common = out.stdout.strip()
    if out.returncode or not common:
        return None
    common_dir = Path(common).resolve()
    if common_dir.name != ".git" or not common_dir.is_dir():
        return None                                   # bare, or a separate git dir: its parent is not the main tree
    root = common_dir.parent
    return root if root.is_dir() else None


def _job(lock: Path) -> tuple[str, str | None]:
    """(how the lock's holder is named in the reason, its job when one was read -- else None, which nothing matches)."""
    try:
        held = json.loads(lock.read_text(encoding="utf-8"))
        job = held.get("job") if isinstance(held, dict) else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "an unreadable lock", None
    if not isinstance(job, str) or not job:
        return "an unnamed job", None
    return job, job


def heavy_skip_reason(start: Path | str | None = None, env: Mapping[str, str] | None = None) -> str | None:
    """None when a heavy test may run in this process; else the plain reason it is skipped (module docstring)."""
    env = os.environ if env is None else env
    root = main_root(start)
    if root is None:
        return ("heavy test skipped: the main repository's root could not be found (git rev-parse --git-common-dir), "
                "so run.lock cannot be checked")
    lock = root / LOCK_NAME
    if not lock.exists():
        return None
    shown, job = _job(lock)
    if job is not None and env.get(LOCK_HOLDER_ENV) == job:
        return None
    return f"heavy test skipped: run.lock held by {shown} (only the lock's holder may run heavy tests)"


__all__ = ["LOCK_HOLDER_ENV", "LOCK_NAME", "main_root", "heavy_skip_reason"]
