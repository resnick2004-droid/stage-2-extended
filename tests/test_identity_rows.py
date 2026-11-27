"""RD-01's identity waits on the shared parser (`extended.identity_rows` over `extended.identity_tokens`, Q-110; D1 of
E-104, the third read's (a)): a runner waiting on identities starts only when the decision log has no token breach and,
for each wait, a row begins its third cell with the holding token -- written here only as the placeholder
identity-holds: <id>, every real one built by `identity_rows.holding_cell` -- naming exactly that id and the sha it held
at, the sha the commit being run or an ancestor of it, none of the identity's covered paths changed since. On throwaway
git repositories; and on this tree's own decision log, where E-089 (which records the identity script as written, not
run) must not pass, and -- its token rows removed, so the tests hold whatever identities the log records (Q-113) --
every wait is refused, or met for the one id a synthetic row holds at HEAD."""
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
    return subprocess.run([*GIT, *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",  # Q-188b
                          check=True).stdout.strip()


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


def _without_tokens(text: str) -> str:
    """The log with every positional token row removed (`IT.parse` finds a token on the line): the log as it stood
    before any identity was recorded holding, whatever rows the lead has added since (Q-113)."""
    return "".join(line + "\n" for line in text.splitlines() if not IT.parse(line))


def test_this_trees_log_breaches_nothing_and_e089_never_admits():
    """On the real log, only what holds whatever rows it gains: no breach, the placeholders seen, E-089 (the identity
    script as written, not run) never a token and never admitting."""
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert IT.problems(text) == []
    assert any(o.kind == "placeholder" for o in IT.occurrences(text))
    e089 = next(line for line in text.splitlines() if line.startswith("| E-089 |"))
    assert "firms_identity" in e089 and IT.parse(e089) == []
    probs, _ = IR.waited_problems(ROOT, (IR.Waited("Q-104", "RD-01's identity stage", ("extended/firms.py",)),),
                                  decisions_text=e089)
    assert probs and "no row carries a token for Q-104" in probs[0]


def test_with_no_token_on_this_tree_every_wait_is_refused_with_its_reason():
    text = _without_tokens((ROOT / "DECISIONS.md").read_text(encoding="utf-8"))
    assert IT.parse(text) == [] and IT.problems(text) == []
    waits = IR.waited()
    probs, found = IR.waited_problems(ROOT, waits, decisions_text=text)
    assert found == {} and len(probs) == len(waits) == 3
    for w, p in zip(waits, probs):
        assert p.startswith(f"{w.task} (") and f"no row carries a token for {w.task}" in p, p


def test_a_holding_row_at_this_trees_head_meets_its_wait_and_no_other():
    head = _git(ROOT, "rev-parse", "HEAD")
    text = _without_tokens((ROOT / "DECISIONS.md").read_text(encoding="utf-8")) + _holding("E-999", "Q-80", head) + "\n"
    assert IT.problems(text) == []
    probs, found = IR.waited_problems(ROOT, IR.waited(), decisions_text=text)
    assert sorted(found) == ["Q-80"] and found["Q-80"]["row"] == "E-999" and found["Q-80"]["sha"] == head
    assert [p.split(" ")[0] for p in probs] == ["Q-104", "Q-93"]
    assert all(f"no row carries a token for {t}" in p for t, p in zip(("Q-104", "Q-93"), probs))


def test_waited_must_name_files_and_an_id():
    with pytest.raises(ValueError):
        IR.Waited("Q-7", "x", ())
    with pytest.raises(ValueError):
        IR.Waited("q 7", "x", ("a.py",))


# ------------------------------------------------------------------------------------------------ the covers (Q-111)


def test_the_shared_waits_are_identity_covers_declaration_exactly():
    from extended import identity_cover as IC

    for ident in ("Q-80", "Q-93"):
        assert IR.cover(ident) == IC.cover(ident)


def test_rd01s_own_cover_is_base_and_its_scripts_closure_by_the_shared_model():
    from extended import identity_cover as IC

    c = IR.cover("Q-104")
    assert c[:len(IC.BASE)] == IC.BASE and "config/" in c
    assert set(c) == set(IC.BASE) | set(IC.imports(IR.RD01_SCRIPT).files)
    assert IR.RD01_SCRIPT in c and "extended/firm_reading.py" in c and "identity/stage2_identity.py" in c
    assert IC.uncovered(IR.RD01_SCRIPT, c) == [] and IR.cover_problems() == []
    assert not hasattr(IR, "import_closure")                  # retired: the shared model is the one model
    with pytest.raises(ValueError):
        IR.cover("Q-7")


def _copy_covered(dst: Path, paths) -> None:
    import shutil

    for p in paths:
        src = ROOT / p.rstrip("/")
        if p.endswith("/"):
            for f in subprocess.run(["git", "ls-files", p.rstrip("/")], cwd=ROOT, capture_output=True,
                                    text=True).stdout.splitlines():
                (dst / f).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / f, dst / f)
        else:
            (dst / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst / p)


def test_a_change_under_config_fails_every_wait(tmp_path):
    waits = IR.waited()
    assert [w.task for w in waits] == ["Q-104", "Q-80", "Q-93"] and all("config/" in w.files for w in waits)
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    _copy_covered(r, sorted({p for w in waits for p in w.files}))
    (r / "README.md").write_text("not covered\n", encoding="utf-8")
    (r / "DECISIONS.md").write_text("| id | date | what | basis |\n|---|---|---|---|\n", encoding="utf-8")
    _git(r, "add", ".")
    _git(r, "commit", "-q", "-m", "c0")
    c0 = _git(r, "rev-parse", "HEAD")
    for i, w in enumerate(waits, 1):
        _row(r, _holding(f"E-00{i}", w.task, c0[:9]))
    (r / "README.md").write_text("changed, not covered\n", encoding="utf-8")
    _git(r, "commit", "-qam", "an uncovered change")
    probs, found = IR.waited_problems(r, waits)
    assert probs == [] and sorted(found) == ["Q-104", "Q-80", "Q-93"]
    y = r / "config" / "rules_extended.yaml"
    y.write_text(y.read_text(encoding="utf-8") + "# a later edit\n", encoding="utf-8")
    _git(r, "commit", "-qam", "a change under config/")
    probs, found = IR.waited_problems(r, waits)
    assert found == {} and len(probs) == 3 and all("config/rules_extended.yaml" in p for p in probs)
