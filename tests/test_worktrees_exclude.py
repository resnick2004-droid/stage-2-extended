"""Q-229: off Windows the licensed stores are linked by symbolic links, which `.gitignore`'s directory-only patterns do
not hide; `worktrees._exclude_store_links` adds them to the repository's own `info/exclude`, once."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import worktrees as W  # noqa: E402


def _repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    (r / ".gitignore").write_text("vendor/stage2/data/bars/\nvendor/stage2/data/atlas/\n", encoding="utf-8")
    return r


def _status(r: Path) -> list[str]:
    return W.changed(r)


def test_exclude_written_once(tmp_path):
    r = _repo(tmp_path)
    ex = r / ".git" / "info" / "exclude"
    ex.parent.mkdir(parents=True, exist_ok=True)
    ex.write_text("# pre-existing, no trailing newline", encoding="utf-8")
    W._exclude_store_links(r)
    W._exclude_store_links(r)
    lines = ex.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# pre-existing, no trailing newline"
    for s in W.STORES:
        assert lines.count(f"/{s}") == 1


def test_symlinked_store_is_ignored(tmp_path):
    r = _repo(tmp_path)
    store = tmp_path / "store"
    store.mkdir()
    (r / "vendor" / "stage2" / "data").mkdir(parents=True)
    try:
        os.symlink(store, r / W.STORES[0], target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links need a privilege on this machine")
    if (r / W.STORES[0]).is_symlink():
        before = _status(r)
        W._exclude_store_links(r)
        after = _status(r)
        assert not any(p.startswith("vendor/") for p in after), after
        # the directory-only pattern alone does not hide a symlink where git sees it as a file
        assert before == after or any(p.startswith("vendor/") for p in before)
