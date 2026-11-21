"""The order of a pin and a run, from git (the lead's C2-2 ruling on Wave 3.5): which commit first pinned a text in the
decision log, and whether a run's commit descends from it.

    from extended import pin_order as PO
    c = PO.pin_commit(repo, "`prereg/x_playbook.json` sha256 `<hex>`")   # the commit that added the pin, or None
    PO.descends(repo, c, manifest["git_commit"])                            # the run came after the pin

**Why.** A result file bound to a declaration's sha256 shows which declaration it was read on, not when: a no-harm
floor read on a declaration and only then pinned (after a look at another rule) binds as well as one read after the
pin. The run's commit must descend from the commit that pinned the declaration, so the declaration was on record in
the run's own history before the floor was read; a `-dirty` or unknown commit never descends.

Light: `git log -S` and `git merge-base --is-ancestor` on the repository's own history, each with a time limit; no
file is written, nothing but `git` is run.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

LOG = "DECISIONS.md"
LIMIT_S = 120
SHA = re.compile(r"[0-9a-f]{7,40}$")


class PinOrderError(RuntimeError):
    """git could not answer (not a repository, a time-out): the order is unknown, so nothing is accepted on it."""


def _git(repo: Path | str, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=LIMIT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise PinOrderError(f"git {' '.join(args[:2])} failed in {repo}: {e}") from e


def pin_commit(repo: Path | str, text: str, log: str = LOG) -> str | None:
    """The first commit (in history order) whose change to `log` added `text` (`git log -S`), or None."""
    p = _git(repo, "log", "--reverse", "--format=%H", "-S", text, "--", log)
    if p.returncode:
        raise PinOrderError(f"git log failed in {repo}: {p.stderr.strip()[:200]}")
    lines = [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]
    return lines[0] if lines else None


def descends(repo: Path | str, ancestor: str | None, commit: str | None) -> bool:
    """Whether `commit` is a commit of the repository (never `-dirty`, never unknown) and `ancestor` is one of its
    ancestors or itself (`git merge-base --is-ancestor`)."""
    if not ancestor or not commit or not SHA.match(str(ancestor)) or not SHA.match(str(commit)):
        return False
    for c in (ancestor, commit):
        if _git(repo, "cat-file", "-e", f"{c}^{{commit}}").returncode:
            return False
    return _git(repo, "merge-base", "--is-ancestor", ancestor, commit).returncode == 0


__all__ = ["LOG", "PinOrderError", "pin_commit", "descends"]
