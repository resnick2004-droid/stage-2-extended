"""R3 (`docs/reviews/BUILD_RD-01_v2_2026-11-16.md`): a runner waiting on identities starts only when, for each one, a
decision row carries the lead's exact token `identity-holds: Q-nn` and names a commit at which the identity held whose
covered files the commit being run has not changed (`extended.identity_rows`). On throwaway git repositories; and on
this tree's own decision log, where E-089 (which records the identity script as written, not run) must not pass."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from extended import identity_rows as IR

ROOT = Path(__file__).resolve().parent.parent
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false",
       "-c", "core.hooksPath=/dev/null"]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run([*GIT, *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def _repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    (r / "code.py").write_text("x = 1\n", encoding="utf-8")
    (r / "other.py").write_text("y = 1\n", encoding="utf-8")
    (r / "DECISIONS.md").write_text("| id | date | what | basis |\n|---|---|---|---|\n", encoding="utf-8")
    _git(r, "add", ".")
    _git(r, "commit", "-q", "-m", "c0")
    return r


def _row(r: Path, line: str) -> str:
    p = r / "DECISIONS.md"
    p.write_text(p.read_text(encoding="utf-8") + line + "\n", encoding="utf-8")
    _git(r, "add", "DECISIONS.md")
    _git(r, "commit", "-q", "-m", "row")
    return _git(r, "rev-parse", "HEAD")


W = (IR.Waited("Q-7", "a toy identity", ("code.py",)),)


def test_a_row_without_the_token_is_refused(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, f"| E-001 | 2026-11-16 | **identity/firms_identity.py written; T-1..T-15 hold on synthetic inputs** at {c0[:7]} | x |")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and len(probs) == 1 and "identity-holds: Q-7" in probs[0]


def test_a_row_with_the_token_and_no_commit_is_refused(tmp_path):
    r = _repo(tmp_path)
    _row(r, "| E-001 | 2026-11-16 | **the identity holds** `identity-holds: Q-7` | x |")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "names no commit" in probs[0]


def test_the_token_with_the_identitys_commit_admits_the_run_after_record_only_commits(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, f"| E-001 | 2026-11-16 | **Q-7's identity holds at {c0[:7]}** `identity-holds: Q-7` | x |")
    (r / "other.py").write_text("y = 2\n", encoding="utf-8")         # a file the identity does not cover
    _git(r, "commit", "-qam", "later")
    probs, found = IR.waited_problems(r, W)
    assert probs == [] and found["Q-7"]["row"] == "E-001" and found["Q-7"]["commit"] == c0


def test_a_covered_file_changed_since_the_named_commit_is_refused(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, f"| E-001 | 2026-11-16 | **Q-7's identity holds at {c0[:7]}** `identity-holds: Q-7` | x |")
    (r / "code.py").write_text("x = 2\n", encoding="utf-8")
    _git(r, "commit", "-qam", "code changed")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "code.py" in probs[0]


def test_a_commit_off_the_runs_history_is_refused(tmp_path):
    r = _repo(tmp_path)
    _git(r, "checkout", "-q", "-b", "side")
    (r / "other.py").write_text("y = 3\n", encoding="utf-8")
    _git(r, "commit", "-qam", "side")
    side = _git(r, "rev-parse", "HEAD")
    _git(r, "checkout", "-q", "-")
    _row(r, f"| E-001 | 2026-11-16 | **Q-7's identity holds at {side[:9]}** `identity-holds: Q-7` | x |")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "not the commit being run nor one before it" in probs[0]


def test_the_token_is_exact():
    assert IR.token("Q-80") == "`identity-holds: Q-80`"
    text = "| E-001 | d | `identity-holds: Q-800` and identity-holds: Q-80 unquoted | b |"
    assert IR.rows_carrying(text, "Q-80") == []
    assert [r for r, _ in IR.rows_carrying(text, "Q-800")] == ["E-001"]


def test_this_trees_log_admits_no_row_today_and_never_e089():
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    for task in ("Q-104", "Q-80", "Q-93"):
        assert all(row != "E-089" for row, _ in IR.rows_carrying(text, task))
    e089 = next(line for line in text.splitlines() if line.startswith("| E-089 |"))
    assert "firms_identity" in e089                       # the row the old two-substring test admitted
    probs, _ = IR.waited_problems(ROOT, (IR.Waited("Q-104", "RD-01's identity stage", ("extended/firms.py",)),),
                                  decisions_text=e089)
    assert probs and "identity-holds: Q-104" in probs[0]


def test_waited_must_name_files():
    with pytest.raises(ValueError):
        IR.Waited("Q-7", "x", ())
