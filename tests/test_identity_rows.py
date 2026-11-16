"""RD-01's identity waits on the shared parser (`extended.identity_rows` over `extended.identity_tokens`, Q-110; D1 of
E-104, the third read's (a)): a runner waiting on identities starts only when the decision log has no token breach and,
for each wait, a row begins its third cell with the holding token -- written here only as the placeholder
identity-holds: <id>, every real one built by `identity_rows.holding_cell` -- naming exactly that id and the sha it held
at, the sha the commit being run or an ancestor of it, none of the identity's covered paths changed since. On throwaway
git repositories; and on this tree's own decision log, where E-089 (which records the identity script as written, not
run) must not pass."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from extended import identity_rows as IR
from extended import identity_tokens as IT

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


def _holding(row: str, ident: str, sha: str, text: str = "the identity holds") -> str:
    return f"| {row} | 2026-11-16 | {IR.holding_cell(ident, sha, text)} | a basis |"


W = (IR.Waited("Q-7", "a toy identity", ("code.py",)),)


def test_the_holding_cell_is_the_shared_parsers_token():
    cell = IR.holding_cell("Q-7", "abc1234", "it holds")
    assert cell.startswith(IT.STEM + ": Q-7 @ abc1234 -- ") and "`" not in cell
    with pytest.raises(ValueError):
        IR.holding_cell("Q-7", "not-a-sha", "x")
    line = _holding("E-001", "Q-7", "abc1234")
    assert IT.parse(line) == [IT.Token("E-001", "Q-7", "abc1234")] and IT.problems(line) == []


def test_the_shape_anywhere_but_the_third_cells_start_is_never_a_token(tmp_path):
    good = IR.holding_cell("Q-7", "abc1234", "x holds")
    for line in (f"| E-001 | 2026-11-16 | **a note** {good} | b |",            # inside the text
                 f"| E-001 | 2026-11-16 | `{good}` | b |",                     # quoted
                 f"| E-001 | 2026-11-16 | a basis | {good} |"):               # another cell
        assert IT.parse(line) == [], line
    r = _repo(tmp_path)
    _row(r, f"| E-001 | 2026-11-16 | **a note** {good} | b |")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "breach" in probs[0]                         # the log is refused before any wait


def test_a_row_without_the_token_is_refused_with_its_reason(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, f"| E-001 | 2026-11-16 | **identity/firms_identity.py written; T-1..T-15 hold on synthetic inputs** at "
            f"{c0[:7]} | x |")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and len(probs) == 1 and "no row carries a token for Q-7" in probs[0]


def test_a_token_without_a_sha_is_a_breach_and_refuses(tmp_path):
    r = _repo(tmp_path)
    _row(r, f"| E-001 | 2026-11-16 | {IT.STEM}: Q-7 -- the identity holds | x |")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "(c)" in probs[0]


def test_the_token_at_the_identitys_commit_admits_the_run_after_record_only_commits(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, _holding("E-001", "Q-7", c0[:7]))
    (r / "other.py").write_text("y = 2\n", encoding="utf-8")         # a file the identity does not cover
    _git(r, "commit", "-qam", "later")
    head = _git(r, "rev-parse", "HEAD")
    probs, found = IR.waited_problems(r, W)
    assert probs == [] and found["Q-7"] == {"row": "E-001", "sha": c0, "head": head, "what": "a toy identity"}
    assert IT.held(_git(r, "show", "HEAD:DECISIONS.md"), "Q-7", r, head, ["code.py"]).row == "E-001"


def test_only_the_positional_sha_is_read(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    (r / "code.py").write_text("x = 2\n", encoding="utf-8")
    _git(r, "commit", "-qam", "code changed")
    c1 = _git(r, "rev-parse", "HEAD")
    _row(r, _holding("E-001", "Q-7", c0[:9], f"the identity held; the code later changed at {c1[:9]}"))
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "code.py" in probs[0]                       # c1 in the text is not read


def test_a_covered_file_changed_since_the_sha_is_refused(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, _holding("E-001", "Q-7", c0[:7]))
    (r / "code.py").write_text("x = 2\n", encoding="utf-8")
    _git(r, "commit", "-qam", "code changed")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "E-001" in probs[0] and "code.py" in probs[0]


def test_a_sha_off_the_runs_history_is_refused(tmp_path):
    r = _repo(tmp_path)
    _git(r, "checkout", "-q", "-b", "side")
    (r / "other.py").write_text("y = 3\n", encoding="utf-8")
    _git(r, "commit", "-qam", "side")
    side = _git(r, "rev-parse", "HEAD")
    _git(r, "checkout", "-q", "-")
    _row(r, _holding("E-001", "Q-7", side[:9]))
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "neither" in probs[0] and "nor an ancestor" in probs[0]


def test_ids_are_exact(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, _holding("E-001", "Q-70", c0[:7]))
    _row(r, _holding("E-002", "Q-7d", c0[:7]))
    probs, found = IR.waited_problems(r, W)
    assert found == {} and "no row carries a token for Q-7" in probs[0]


def test_every_refusing_row_gives_its_reason_and_a_newer_holding_admits(tmp_path):
    r = _repo(tmp_path)
    c0 = _git(r, "rev-parse", "HEAD")
    _row(r, _holding("E-001", "Q-7", c0[:7]))
    (r / "code.py").write_text("x = 2\n", encoding="utf-8")
    _git(r, "commit", "-qam", "code changed")
    probs, found = IR.waited_problems(r, W)
    assert found == {} and probs[0].count("E-001:") == 1
    c1 = _row(r, _holding("E-002", "Q-7", _git(r, "rev-parse", "HEAD")[:7], "held again at the newer commit"))
    probs, found = IR.waited_problems(r, W)
    assert probs == [] and found["Q-7"]["row"] == "E-002" and found["Q-7"]["head"] == c1


def test_a_covered_path_missing_at_head_refuses():
    probs, found = IR.waited_problems(ROOT, (IR.Waited("Q-7", "x", ("no/such/file.py",)),),
                                      decisions_text="| E-001 | 2026-11-16 | nothing | b |")
    assert found == {} and "refused by the shared parser" in probs[0]


def test_this_trees_log_admits_no_waited_identity_and_never_e089():
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert IT.problems(text) == []
    assert all(t.ident not in ("Q-104", "Q-80", "Q-93") for t in IT.parse(text))
    e089 = next(line for line in text.splitlines() if line.startswith("| E-089 |"))
    assert "firms_identity" in e089 and IT.parse(e089) == []
    probs, _ = IR.waited_problems(ROOT, (IR.Waited("Q-104", "RD-01's identity stage", ("extended/firms.py",)),),
                                  decisions_text=e089)
    assert probs and "no row carries a token for Q-104" in probs[0]


def test_waited_must_name_files_and_an_id():
    with pytest.raises(ValueError):
        IR.Waited("Q-7", "x", ())
    with pytest.raises(ValueError):
        IR.Waited("q 7", "x", ("a.py",))


# ------------------------------------------------------------------------------------------------ E-113's covered paths


def test_the_import_closure_follows_every_repository_import(tmp_path):
    (tmp_path / "extended").mkdir()
    (tmp_path / "identity").mkdir()
    (tmp_path / "extended" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "extended" / "a.py").write_text("from extended import b\n", encoding="utf-8")
    (tmp_path / "extended" / "b.py").write_text("def f():\n    from extended.c import x\n", encoding="utf-8")
    (tmp_path / "extended" / "c.py").write_text("x = 1\nimport numpy\n", encoding="utf-8")
    (tmp_path / "extended" / "unused.py").write_text("", encoding="utf-8")
    (tmp_path / "identity" / "helper.py").write_text("from extended import a\n", encoding="utf-8")
    (tmp_path / "identity" / "ident.py").write_text("import helper\nimport user_journey\nfrom extended import "
                                                    "use_vendored_stage2\n", encoding="utf-8")
    got = IR.import_closure("identity/ident.py", tmp_path)
    assert got == ("extended/__init__.py", "extended/a.py", "extended/b.py", "extended/c.py", "identity/helper.py")


def test_the_firms_identitys_closure_on_this_tree():
    got = IR.import_closure("identity/firms_identity.py", ROOT)
    for f in ("extended/firm_reading.py", "extended/firms.py", "extended/firm_accounts.py", "extended/user_beside.py",
              "extended/replay_records.py", "extended/place_records.py", "extended/calendar_fomc_minutes.py",
              "identity/gate_identity.py", "identity/stage2_identity.py", "identity/user_beside_identity.py",
              "extended/gate.py", "extended/campaign.py"):
        assert f in got, f
    assert not any(p.startswith("vendor/") for p in got) and "identity/firms_identity.py" not in got
