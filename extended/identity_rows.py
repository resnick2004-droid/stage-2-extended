"""The identity guard (R3, `docs/reviews/BUILD_RD-01_v2_2026-11-16.md`): a runner that waits on identities starts only
when each has a decision row recording that it **held**, at code the run still runs.

**The token.** The lead marks a decision row that records an identity holding with the literal token
`` `identity-holds: Q-nn` `` (`token`), Q-nn the queue item whose identity it is. Nothing else in a row counts: a row
that names an identity script and says "hold" about anything else (E-089: "T-1..T-7 and T-9..T-15 hold on synthetic
inputs", the script "written, not run") does not carry the token.

**The commit.** The row must also name the commit the identity held at (a 7- to 40-character hash resolving to a
commit). The run's own commit cannot be named in its own tree's decision log (the row is part of the commit it would
name), so "the commit being run" is read through its code: the named commit is the run's commit or an ancestor of it,
and **none of the files the identity covers** (`Waited.files`) differs between the two -- the commits after it may
only add records. Any row carrying the token and meeting both conditions admits that identity; the rows used are
returned for the run's manifests.

Pure Python and git; nothing here imports the engine.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ROW = re.compile(r"^\|\s*(E-\d+)\s*\|")
HEX = re.compile(r"(?<![0-9A-Za-z])([0-9a-f]{7,40})(?![0-9A-Za-z])")


@dataclass(frozen=True)
class Waited:
    """One identity a runner waits on: its queue item, what it is, the files whose code it held on."""

    task: str
    what: str
    files: tuple[str, ...]

    def __post_init__(self) -> None:
        if not re.fullmatch(r"Q-\d+[a-z]?", self.task):
            raise ValueError(f"a waited identity is named by its queue item (Q-nn), got {self.task!r}")
        if not self.files:
            raise ValueError(f"{self.task}: an identity covers the files it held on; none given")


def token(task: str) -> str:
    """The lead's literal mark on a row recording that `task`'s identity held."""
    return f"`identity-holds: {task}`"


def rows_carrying(decisions_text: str, task: str) -> list[tuple[str, str]]:
    """(row id, line) of every decision row carrying `task`'s exact token."""
    want = token(task)
    out = []
    for line in decisions_text.splitlines():
        m = ROW.match(line)
        if m and want in line:
            out.append((m.group(1), line))
    return out


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def commits_named(line: str, repo: Path) -> list[str]:
    """The full hashes of the commits a row names (each 7- to 40-hex word that resolves to a commit), in order."""
    out: list[str] = []
    for h in HEX.findall(line):
        r = _git(repo, "rev-parse", "--verify", "--quiet", f"{h}^{{commit}}")
        full = r.stdout.strip()
        if r.returncode == 0 and full and full not in out:
            out.append(full)
    return out


def held_at_problem(repo: Path, commit: str, head: str, files: Sequence[str]) -> str | None:
    """Why `commit` is not the code `head` runs for these files (None: it is)."""
    anc = _git(repo, "merge-base", "--is-ancestor", commit, head)
    if anc.returncode != 0:
        return f"{commit[:12]} is not the commit being run nor one before it"
    d = _git(repo, "diff", "--name-only", commit, head, "--", *files)
    if d.returncode != 0:
        return f"git diff {commit[:12]}..{head[:12]} failed: {d.stderr.strip()[:200]}"
    changed = [x for x in d.stdout.splitlines() if x.strip()]
    if changed:
        return f"{len(changed)} covered files changed since {commit[:12]} (first: {changed[0]})"
    return None


def waited_problems(repo: Path | str, waited: Sequence[Waited], *, decisions_text: str | None = None,
                    head: str = "HEAD") -> tuple[list[str], dict[str, dict[str, str]]]:
    """(the problems, {task: the row and commit that admit it}) for every waited identity. `decisions_text` defaults to
    the repository's `DECISIONS.md`; `head` is the commit being run."""
    repo = Path(repo)
    if decisions_text is None:
        p = repo / "DECISIONS.md"
        decisions_text = p.read_text(encoding="utf-8") if p.is_file() else ""
    hr = _git(repo, "rev-parse", "--verify", f"{head}^{{commit}}")
    if hr.returncode != 0:
        return [f"the commit being run ({head}) does not resolve: {hr.stderr.strip()[:200]}"], {}
    head_full = hr.stdout.strip()
    problems: list[str] = []
    found: dict[str, dict[str, str]] = {}
    for w in waited:
        rows = rows_carrying(decisions_text, w.task)
        if not rows:
            problems.append(f"{w.task} ({w.what}): no decision row carries {token(w.task)} -- the identity has not "
                            "been recorded as holding")
            continue
        why: list[str] = []
        for row_id, line in rows:
            commits = commits_named(line, repo)
            if not commits:
                why.append(f"{row_id} names no commit")
                continue
            for c in commits:
                bad = held_at_problem(repo, c, head_full, w.files)
                if bad is None:
                    found[w.task] = {"row": row_id, "commit": c, "token": token(w.task), "what": w.what,
                                     "head": head_full}
                    break
                why.append(f"{row_id}: {bad}")
            if w.task in found:
                break
        if w.task not in found:
            problems.append(f"{w.task} ({w.what}): " + "; ".join(why))
    return problems, found


__all__ = ["Waited", "token", "rows_carrying", "commits_named", "held_at_problem", "waited_problems"]
