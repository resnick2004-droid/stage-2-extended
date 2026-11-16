"""Shared path logic for the Claude Code hooks: which tree of this repository a tool call's target lies in.

The hooks in `.claude/settings.json` run from this repository's `scripts/hooks/` whatever the target, and a target may
lie outside the session's cwd: in a worktree under `%LOCALAPPDATA%\\stage2-extended-wt\\<name>` (E-005), or in a clean
checkout under `%LOCALAPPDATA%\\stage2-extended-runs\\<name>`. A *tree root* is any directory holding a `.git` entry --
a directory in the main repository, a file in a worktree or a detached checkout -- so a protected directory is
recognised wherever it sits: the protected name directly inside a tree root, or this repository's own copy.

Paths are compared case-insensitively on Windows (`os.path.normcase`), and both the path as written and the path with
links and junctions followed are checked (a worktree's `vendor/stage2/data/bars` is a junction into this tree).
"""
from __future__ import annotations

import os
from pathlib import Path

#: This repository's root (the hooks live in <root>/scripts/hooks/).
HOOKS_REPO = Path(__file__).resolve().parents[2]


def norm(p: Path | str) -> str:
    return os.path.normcase(os.path.normpath(str(p)))


def target_of(payload: dict) -> str | None:
    """The file a tool call writes: `file_path` (Write, Edit, MultiEdit), `notebook_path` (NotebookEdit), or `path`."""
    ti = payload.get("tool_input") or {}
    raw = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
    return str(raw) if raw else None


def candidates(raw: str, cwd: str | None) -> list[Path]:
    """The target as written (absolute and normalised, links not followed) and resolved (links and junctions
    followed), without requiring it to exist -- the file may be about to be created."""
    target = Path(raw)
    if not target.is_absolute():
        target = Path(cwd or ".") / target
    out = [Path(os.path.abspath(target))]
    try:
        resolved = target.resolve(strict=False)
        if norm(resolved) != norm(out[0]):
            out.append(resolved)
    except (OSError, RuntimeError):
        pass
    return out


def is_tree_root(d: Path) -> bool:
    """A directory holding `.git` -- a directory (the main repository) or a file (a worktree, a detached checkout)."""
    try:
        return (d / ".git").exists()
    except OSError:
        return False


def protected_dir(target: Path, name: str, own_root: Path = HOOKS_REPO) -> Path | None:
    """The directory called `name` that `target` lies in (or is) when that directory sits directly in a tree root, or
    is this repository's own `<root>/<name>`; None otherwise."""
    own = norm(own_root / name)
    want = os.path.normcase(name)
    for d in (target, *target.parents):
        if norm(d) == own:
            return d
        if os.path.normcase(d.name) == want and is_tree_root(d.parent):
            return d
    return None


def tree_root(target: Path) -> Path | None:
    """The nearest ancestor of `target` that is a tree root."""
    for d in target.parents:
        if is_tree_root(d):
            return d
    return None


def is_worktree(root: Path) -> bool:
    """True when the tree's `.git` is a file: a linked worktree or a detached checkout, not the main repository."""
    return (root / ".git").is_file()
