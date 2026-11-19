"""`scripts/install_hooks.py` installs each git hook atomically (Q-161 follow-up).

A running sh reads its script as it goes: `shutil.copyfile` over a hook that some commit's sh is executing rewrites the
file under it, and the shell can execute a mix of the old and new text. Each hook is therefore written to a temporary
file in the hooks directory and `os.replace`d over the target: a reader that opened the old file keeps reading the old
file, whole; a new reader sees the new file, whole. If the replace fails, the installer says so and the old hook stays.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import install_hooks as I  # noqa: E402

LIMIT = 60
OLD = b"#!/bin/sh\n# the OLD hook\n" + b"echo old line\n" * 2000 + b"exit 0\n"
NEW = b"#!/bin/sh\n# the NEW hook\n" + b"echo new line\n" * 3000 + b"exit 1\n"


def _git_sh() -> str | None:
    try:
        out = subprocess.run(["git", "var", "GIT_SHELL_PATH"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    p = out.stdout.strip()
    return p if out.returncode == 0 and p and Path(p).exists() else None


GIT_SH = _git_sh()


@pytest.fixture()
def hooks(tmp_path) -> tuple[Path, Path, Path]:
    src_dir, hooks_dir = tmp_path / "scripts", tmp_path / "hooks"
    src_dir.mkdir()
    hooks_dir.mkdir()
    src, dst = src_dir / "pre-commit", hooks_dir / "pre-commit"
    src.write_bytes(NEW)
    dst.write_bytes(OLD)
    return src, dst, hooks_dir


def _wait(p: Path, limit: float = LIMIT) -> bool:
    t0 = time.monotonic()
    while time.monotonic() - t0 < limit:
        if p.exists():
            return True
        time.sleep(0.05)
    return p.exists()


@pytest.mark.skipif(GIT_SH is None, reason="git's own sh not found")
def test_a_hook_held_open_by_a_running_shell_keeps_its_old_content_and_the_new_file_is_whole(hooks, tmp_path):
    """A shell (git's own sh, as a hook runs) opens the old hook, the install replaces it, then the shell reads on:
    it reads the old text, all of it; the installed file is the new text, all of it, LF, executable."""
    src, dst, hooks_dir = hooks
    opened, go, out = tmp_path / "opened", tmp_path / "go", tmp_path / "read.txt"
    cat = str(Path(GIT_SH).parent / "cat").replace("\\", "/")
    reader = subprocess.Popen(
        [GIT_SH, "-c", 'exec 3<"$1"; : > "$2"; while [ ! -f "$3" ]; do sleep 0.1; done; "$5" <&3 > "$4"', "reader",
         str(dst).replace("\\", "/"), str(opened).replace("\\", "/"), str(go).replace("\\", "/"),
         str(out).replace("\\", "/"), cat])
    try:
        assert _wait(opened), "the reader never opened the hook"
        assert I.install_one(src, dst) is True
        go.write_text("go", encoding="utf-8")
        assert reader.wait(timeout=LIMIT) == 0
    finally:
        if reader.poll() is None:
            reader.kill()
    assert out.read_bytes() == OLD, "the running reader saw the new file (or a mix) under it"
    assert dst.read_bytes() == NEW, "the installed hook is not the new file, whole"
    assert b"\r\n" not in dst.read_bytes()
    assert os.name == "nt" or dst.stat().st_mode & stat.S_IXUSR          # Windows shows no exec bit
    assert sorted(p.name for p in hooks_dir.iterdir()) == ["pre-commit"], "a temporary file was left behind"


def test_a_python_reader_that_opened_the_old_hook_keeps_it(hooks):
    """The same with a reader holding a plain open handle (POSIX: the replace goes through; Windows: Python opens
    without delete-sharing, so the replace is refused -- the old hook stays whole and the installer says so)."""
    src, dst, hooks_dir = hooks
    with dst.open("rb") as f:
        head = f.read(10)
        ok = I.install_one(src, dst)
        rest = f.read()
    assert head + rest == OLD
    assert dst.read_bytes() == (NEW if ok else OLD)
    assert sorted(p.name for p in hooks_dir.iterdir()) == ["pre-commit"]


def test_a_failed_replace_says_so_and_leaves_the_old_hook(hooks, monkeypatch, capsys):
    src, dst, hooks_dir = hooks

    def refuse(a, b):
        raise PermissionError(13, "in use")

    monkeypatch.setattr(I, "_replace", refuse)
    assert I.install_one(src, dst) is False
    err = capsys.readouterr().err
    assert "NOT installed" in err and str(dst) in err and "in use" in err
    assert dst.read_bytes() == OLD
    assert sorted(p.name for p in hooks_dir.iterdir()) == ["pre-commit"], "the temporary file was left behind"


def test_a_new_hook_is_created_whole_and_executable(tmp_path):
    src = tmp_path / "commit-msg"
    src.write_bytes(NEW)
    hooks_dir = tmp_path / "hooks"
    hooks_dir.mkdir()
    dst = hooks_dir / "commit-msg"
    assert I.install_one(src, dst) is True
    assert dst.read_bytes() == NEW
    assert os.name == "nt" or dst.stat().st_mode & stat.S_IXUSR          # Windows shows no exec bit
    assert [p.name for p in hooks_dir.iterdir()] == ["commit-msg"]


def test_the_installer_no_longer_copies_in_place():
    text = (ROOT / "scripts" / "install_hooks.py").read_text(encoding="utf-8")
    assert "shutil.copyfile" not in text and "os.replace(" in text and "POSIX_SEMANTICS" in text


def test_main_stops_at_a_failed_replace_and_returns_nonzero(tmp_path, monkeypatch, capsys):
    hooks_dir = tmp_path / "hooks"
    hooks_dir.mkdir()
    for name in I.HOOKS:
        (hooks_dir / name).write_bytes(OLD)
    calls = []

    def flaky(a, b):
        calls.append(b)
        raise OSError(5, "denied")

    monkeypatch.setattr(I, "_replace", flaky)
    assert I.install_all(hooks_dir) == 1
    assert len(calls) == 1, "the installer went on after a failed replace"
    assert all((hooks_dir / n).read_bytes() == OLD for n in I.HOOKS)
    assert "NOT installed" in capsys.readouterr().err
