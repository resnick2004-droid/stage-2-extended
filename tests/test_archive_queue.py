"""Q-147: `scripts/archive_queue.py` moves the queue's rows whose state begins with `done` from `TASK_QUEUE.md` to
`docs/archive/TASK_QUEUE_ARCHIVE.md`, verbatim, and `scripts/status.py`'s parsing copes with both files afterwards.

All on synthetic queues in a temporary folder (and one on a temporary copy of this tree's queue); the real
`TASK_QUEUE.md` is the lead's and is never written by a test.
"""
from __future__ import annotations

import importlib.util
import io
import shutil
from contextlib import redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _load("s2x_status_for_archive", "scripts/status.py")
A = _load("s2x_archive_queue", "scripts/archive_queue.py")

QUEUE = """# Task queue

Ranked. Only the lead edits this file.

## Phase 0 -- set up

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-01 | Skeleton: a | b (with a pipe \\| inside) | lead | done | -- | light | 0 | E-005 |
| Q-02 | **Agents** | wt-x | running | Q-01 | light; heavy later | 1 | -- |
| Q-03 | Worktrees | lead | done: merged (E-006); the rest | Q-02 | light | 0 | E-006 |

## Phase 1 -- research

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-10 | The walker | wt-verify | done; collected | -- | heavy | 0 | E-010 |
| Q-11 | Features | wt-features | queued | Q-10 | light | 0 | -- |
| Q-12 | Firms | wt-firms | Done by hand (not a done state) | -- | light | 0 | -- |
| Q-13 | Withdrawn | wt-levels | withdrawn | -- | -- | 0 | E-007 |
| Q-14 | Undone | wt-x | not done | -- | light | 0 | -- |

## Closing checklist

- [ ] every declaration on record
"""


def _write(p: Path, text: str, newline: str = "\n") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.replace("\n", newline).encode("utf-8"))
    return p


def _run(q: Path, a: Path, *extra: str) -> int:
    return A.main(["--queue", str(q), "--archive", str(a), "--date", "2026-11-18", *extra])


@pytest.fixture
def files(tmp_path: Path) -> tuple[Path, Path]:
    return _write(tmp_path / "TASK_QUEUE.md", QUEUE), tmp_path / "docs" / "archive" / "TASK_QUEUE_ARCHIVE.md"


def _ids(text: str) -> list[str]:
    return [r["id"] for r in S.queue_rows(text)]


def test_done_rows_move_verbatim_and_the_rest_stay(files):
    q, a = files
    before = S.queue_rows(q.read_text(encoding="utf-8"))
    assert _run(q, a) == 0
    live, arch = q.read_text(encoding="utf-8"), a.read_text(encoding="utf-8")
    assert _ids(live) == ["Q-02", "Q-11", "Q-12", "Q-13", "Q-14"]
    assert _ids(arch) == ["Q-01", "Q-03", "Q-10"]
    # status.py's parser reads the same rows, cell for cell, from the two files as it read from the one
    by_id = {r["id"]: r for r in before}
    assert all(r == by_id[r["id"]] for r in S.queue_rows(live) + S.queue_rows(arch))
    assert not any(r["state"].startswith("done") for r in S.queue_rows(live))
    assert all(r["state"].startswith("done") for r in S.queue_rows(arch))
    # each moved line is byte-identical in the archive, the pipe inside a task kept
    for line in QUEUE.splitlines():
        if line.startswith(("| Q-01 ", "| Q-03 ", "| Q-10 ")):
            assert line in arch.splitlines() and line not in live.splitlines()
    # the archive keeps each row under its section, with the table header status.py's tables carry
    assert "Phase 0 -- set up" in arch and "Phase 1 -- research" in arch and "| id | task | owner | state |" in arch


def test_everything_but_the_moved_rows_is_kept_in_the_queue(files):
    q, a = files
    _run(q, a)
    live = q.read_text(encoding="utf-8")
    lines = live.splitlines()
    at = [i for i, ln in enumerate(lines) if "TASK_QUEUE_ARCHIVE.md" in ln]
    assert len(at) == 1, "the queue says once where its done rows went"
    i = at[0]
    assert lines[i + 1] == "" and lines[i + 2] == "## Phase 0 -- set up", "the pointer stands before the first section"
    moved = ("| Q-01 ", "| Q-03 ", "| Q-10 ")
    assert lines[:i] + lines[i + 2:] == [ln for ln in QUEUE.splitlines() if not ln.startswith(moved)]
    # a second run adds no second pointer
    _run(q, a)
    assert sum("TASK_QUEUE_ARCHIVE.md" in ln for ln in q.read_text(encoding="utf-8").splitlines()) == 1


def test_status_reads_the_archived_queue_and_the_archive(files, monkeypatch):
    q, a = files
    _run(q, a)
    monkeypatch.setattr(S, "QUEUE", q)
    monkeypatch.setattr(S, "ARCHIVE", a)
    buf = io.StringIO()
    with redirect_stdout(buf):
        S.show_queue()
    out = buf.getvalue()
    for qid in ("Q-02", "Q-11", "Q-12", "Q-13", "Q-14"):
        assert qid in out
    counts = out.splitlines()[1]
    assert not any(part.strip().startswith("done") for part in counts.split(",")), counts
    assert "archived: 3 row(s)" in out and "TASK_QUEUE_ARCHIVE.md" in out


def test_status_without_an_archive_says_so_quietly(files, monkeypatch):
    q, a = files
    monkeypatch.setattr(S, "QUEUE", q)
    monkeypatch.setattr(S, "ARCHIVE", a)
    buf = io.StringIO()
    with redirect_stdout(buf):
        S.show_queue()
    assert "Q-01" in buf.getvalue() and "archived:" not in buf.getvalue()


def test_a_second_run_moves_nothing_and_writes_nothing(files):
    q, a = files
    _run(q, a)
    qb, ab = q.read_bytes(), a.read_bytes()
    assert _run(q, a) == 0
    assert q.read_bytes() == qb and a.read_bytes() == ab


def test_a_later_run_appends_and_keeps_the_archive(files):
    q, a = files
    _run(q, a)
    first = a.read_bytes()
    text = q.read_text(encoding="utf-8").replace("| Q-11 | Features | wt-features | queued |",
                                                 "| Q-11 | Features | wt-features | done: merged |")
    q.write_bytes(text.encode("utf-8"))
    assert A.main(["--queue", str(q), "--archive", str(a), "--date", "2026-11-20"]) == 0
    assert a.read_bytes().startswith(first)
    assert _ids(a.read_text(encoding="utf-8")) == ["Q-01", "Q-03", "Q-10", "Q-11"]
    assert "Q-11" not in _ids(q.read_text(encoding="utf-8"))


def test_an_id_already_archived_is_refused_and_nothing_written(files):
    q, a = files
    _write(a, "# Task queue archive\n\n| id | task | owner | state | depends on | weight | retries | row |\n"
              "|---|---|---|---|---|---|---|---|\n| Q-03 | Old | lead | done | -- | light | 0 | -- |\n")
    qb, ab = q.read_bytes(), a.read_bytes()
    assert _run(q, a) != 0
    assert q.read_bytes() == qb and a.read_bytes() == ab


def test_the_dry_run_writes_nothing(files):
    q, a = files
    qb = q.read_bytes()
    assert _run(q, a, "--dry-run") == 0
    assert q.read_bytes() == qb and not a.exists()


def test_crlf_line_endings_are_kept(tmp_path):
    q = _write(tmp_path / "TASK_QUEUE.md", QUEUE, newline="\r\n")
    a = tmp_path / "TASK_QUEUE_ARCHIVE.md"
    assert _run(q, a) == 0
    live = q.read_bytes()
    assert b"\r\n" in live and b"\n" not in live.replace(b"\r\n", b"")
    assert _ids(q.read_text(encoding="utf-8")) == ["Q-02", "Q-11", "Q-12", "Q-13", "Q-14"]
    assert _ids(a.read_text(encoding="utf-8")) == ["Q-01", "Q-03", "Q-10"]


def test_on_a_copy_of_this_trees_queue(tmp_path, monkeypatch):
    """The real queue's shape, in a temporary copy: no row lost or doubled, none done left, status parses both."""
    q = tmp_path / "TASK_QUEUE.md"
    shutil.copyfile(ROOT / "TASK_QUEUE.md", q)
    a = tmp_path / "TASK_QUEUE_ARCHIVE.md"
    before = S.queue_rows(q.read_text(encoding="utf-8"))
    assert _run(q, a) == 0
    live, arch = S.queue_rows(q.read_text(encoding="utf-8")), S.queue_rows(a.read_text(encoding="utf-8"))
    assert sorted(r["id"] for r in live + arch) == sorted(r["id"] for r in before)
    assert [r["id"] for r in arch] == [r["id"] for r in before if r["state"].startswith("done")]
    assert not any(r["state"].startswith("done") for r in live)
    monkeypatch.setattr(S, "QUEUE", q)
    monkeypatch.setattr(S, "ARCHIVE", a)
    buf = io.StringIO()
    with redirect_stdout(buf):
        S.show_queue()
    assert f"archived: {len(arch)} row(s)" in buf.getvalue()
