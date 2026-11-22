"""Q-212: the go token folded into the reader -- one parser for the decision log (the lead's rulings on the red team's
`TEMPLATE_V3_DAFF8CC_2026-11-22`, findings 1, 3, 4, 8, 10 and n1; `extended/go_token.py` on wt/wt-lit daff8cc).
Synthetic logs, declarations and git trees only; nothing real is read but this repository's own `DECISIONS.md` and
`prereg/` (the real log's result).

* **the golden fixture** (`tests/data/go_token_golden.json`, the case table `tests/go_cases.py` committed): every log
  and its declarations, replayed -- `go_problems`' rows and `membership_event`'s row as written by hand: finding 1's
  R1 to R7 (and R8), each problem cleared by a later void and the next correct row counted; the closing rows C1 to C4,
  a cause outside the eight, a closing row after the finalists, `withdrawn` after the event, a second closing row;
  voids of valid rows as no-ops; pins as unfenced decision rows whose sha256 is the file's; the go row's forms (M1 to
  M7 and the red team's df7ab29 probes); the scope's allow-list, refused and allowed forms;
* **the API:** `go_runner(row)`, `membership_event(log_text)`, `go_row_present(declaration_path, log_text)` with the
  runner bound to the checkout's HEAD and the deciding files byte-identical (synthetic git trees);
* **the mutants named by the red team** (g11, g15, g24, g27, g29, g30, g31, g33, r06, r07), each killed by a case
  here or in the fixture;
* **the real log:** `go_problems` is [] and `membership_event` None on this repository's `DECISIONS.md`.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from extended import reader as R
import go_cases as G

ROOT = Path(__file__).resolve().parent.parent


def write_prereg(base: Path, files: dict[str, str]) -> Path:
    d = base / "prereg"
    d.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (d / name).write_bytes(text.encode("utf-8"))
    return d


def problem_rows(log: str, prereg: Path) -> list:
    out = []
    for p in R.go_problems(log, prereg):
        head = p.split(" ")[0]
        out.append(head if head.startswith("E-") else None)
    return out


def event_row(log: str, prereg: Path):
    line = R.membership_event(log, prereg)
    return R.ROW.match(line).group(1) if line else None


# ------------------------------------------------------------------------------------------- the golden fixture


def test_the_golden_fixture_is_the_case_table():
    assert json.loads(G.GOLDEN.read_text(encoding="utf-8")) == G.golden(), \
        "the committed fixture and the case table differ (python tests/go_cases.py rewrites it, deliberately)"


@pytest.mark.parametrize("case", json.loads(G.GOLDEN.read_text(encoding="utf-8")), ids=lambda c: c["name"])
def test_the_golden_fixture_replays(tmp_path, case):
    prereg = write_prereg(tmp_path, case["files"])
    assert problem_rows(case["log"], prereg) == case["problem_rows"], R.go_problems(case["log"], prereg)
    if case["problem_rows"]:
        with pytest.raises(R.GoRefused):
            R.membership_event(case["log"], prereg)
    else:
        assert event_row(case["log"], prereg) == case["event"]


def test_the_fixture_holds_every_named_case():
    names = {c["name"] for c in G.golden()}
    for want in ("R1 wrong sha, voided, correct go", "R2 voided, correct go", "R3 second go voided", "R4 voided",
                 "R5 voided, then a correct go", "R6 voided, F-14 still pinned",
                 "R7 a premature void, then malformed, then a void", "R8 stray fence after a heading, voided",
                 "C1 voided: the go counts", "C2 voided: the go counts (g27)", "C3 closing at another sha",
                 "C4 Heldout-closed capitalised", "M1 an impossible date", "M2 an HTML comment, read as the reader reads it",
                 "M3 CRLF", "M6 NBSP after go:", "M7 go spaced", "two files for one F-number (g31)",
                 "a fenced pin is no pin (g30)", "a fenced closing row, voided, does not close (g29)",
                 "an upper-case-hex pin is no pin (r06)", "a void without its tail is no void (r07)",
                 "scope refused: two firm lines (g11)", "scope refused: marker only fenced (g24)",
                 "scope refused: marker mid-line (g33)", "scope refused: market NQZ6", "scope refused: firm Top step",
                 "scope refused: two firms Lucid, Topstep", "scope allowed: MNQ", "scope allowed: Lucid"):
        assert want in names, want


# ---------------------------------------------------------------------------------- the reader's own tokens (r06, r07)


def test_r06_a_pin_is_lowercase_hex_only():
    assert R.pins("`prereg/F-13_x.md` sha256 `" + "A" * 64 + "`") == {}
    assert R.pins("`prereg/F-13_x.md` sha256 `" + "a" * 64 + "`") == {"prereg/F-13_x.md": {"a" * 64}}


def test_r07_a_void_needs_its_tail():
    assert R.heldout_tokens("| E-903 | 2026-12-09 | heldout-void: E-902 | b |", "void") == []
    assert [t.get("target") for t in R.heldout_tokens(G.void("E-903", "E-902"), "void")] == ["E-902"]


# -------------------------------------------------------------------------------------------------- the API


def test_go_runner_reads_the_runner_sub_form():
    assert R.go_runner(G.G13) == G.RUNNER
    for bad in (G.G13.replace(G.RUNNER, G.RUNNER[:39]), G.G13.replace(" -- runner " + G.RUNNER, ""),
                G.go("E-902", "F-13", G.A, "2026-13-45"), G.P13, "go: F-13"):
        assert R.go_runner(bad) is None, bad


def test_membership_event_is_the_first_counted_go_row(tmp_path):
    prereg = write_prereg(tmp_path, G.FILES)
    log = "\n".join([G.P13, G.P14, G.go("E-902", "F-14", G.B), G.go("E-904", "F-13", G.A, "2026-12-05")])
    assert R.membership_event(log, prereg) == G.go("E-902", "F-14", G.B)
    assert R.membership_event("\n".join([G.P13, G.P14]), prereg) is None
    assert R.membership_event((ROOT / "DECISIONS.md").read_text(encoding="utf-8")) is None   # this repository's


def test_design_search_problems_on_the_case_table():
    for name, body in G.SCOPE_REFUSED.items():
        if name not in ("no deciding files", "deciding files without the reader", "a deciding path outside"):
            assert R.design_search_problems(body), name
    for name, body in G.SCOPE_ALLOWED.items():
        assert R.design_search_problems(body) == [], (name, R.design_search_problems(body))
    assert R.design_search_problems(G.SCOPE_REFUSED["no deciding files"])
    assert R.design_search_problems("# a note, no design search\n") == ["no design-search marker at an unfenced line's "
                                                                       "start"]


# ------------------------------------------------------------------------------ go_row_present: the runner bound


def git(t: Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=t, capture_output=True, text=True, check=True).stdout.strip()


def runner_tree(tmp_path: Path, files: dict[str, str] | None = None) -> tuple[Path, str]:
    """A git tree: the declarations, `extended/reader.py` and `scripts/survey.py` (stand-ins), committed: the runner
    commit. Returns (the tree, the runner commit)."""
    t = tmp_path / "tree"
    write_prereg(t, files or G.FILES)
    for rel in ("extended/reader.py", "scripts/survey.py"):
        (t / rel).parent.mkdir(parents=True, exist_ok=True)
        (t / rel).write_text(f"# a stand-in for {rel}\n", encoding="utf-8")
    git(t, "init", "-q", "-b", "master")
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "the runner commit")
    return t, git(t, "rev-parse", "HEAD")


def with_log(t: Path, rows: list[str]) -> str:
    log = "\n".join(rows) + "\n"
    (t / "DECISIONS.md").write_text(log, encoding="utf-8")
    git(t, "add", "DECISIONS.md")
    git(t, "commit", "-q", "-m", "the log")
    return log


def test_go_row_present_holds_on_a_checkout_descending_from_the_runner(tmp_path):
    t, runner = runner_tree(tmp_path)
    log = with_log(t, [G.P13, G.P14, G.go("E-902", "F-13", G.A, run=runner), G.P15])
    decl = t / "prereg" / "F-13_x.md"
    assert R.go_row_present(decl, log)
    assert not R.go_row_present(t / "prereg" / "F-14_x.md", log), "F-14 has no go row"
    git(t, "checkout", "-q", runner)                                    # HEAD is the runner commit itself
    assert R.go_row_present(decl, log)


def test_go_row_present_refuses_a_head_that_does_not_descend(tmp_path):
    t, runner = runner_tree(tmp_path)
    git(t, "checkout", "-q", "--orphan", "other")
    git(t, "commit", "-q", "-m", "an unrelated history")
    log = "\n".join([G.P13, G.go("E-902", "F-13", G.A, run=runner)])
    assert not R.go_row_present(t / "prereg" / "F-13_x.md", log)
    assert not R.go_row_present(t / "prereg" / "F-13_x.md", "\n".join([G.P13, G.go("E-902", "F-13", G.A, run=G.RUNNER2)]))


def test_go_row_present_refuses_a_changed_or_dirty_deciding_file(tmp_path):
    t, runner = runner_tree(tmp_path)
    log = with_log(t, [G.P13, G.go("E-902", "F-13", G.A, run=runner)])
    decl = t / "prereg" / "F-13_x.md"
    assert R.go_row_present(decl, log)
    (t / "scripts" / "survey.py").write_text("# changed after the go row\n", encoding="utf-8")
    assert not R.go_row_present(decl, log), "dirty in the working tree"
    git(t, "commit", "-q", "-am", "the deciding code changed")
    assert not R.go_row_present(decl, log), "committed: no longer byte-identical to the runner commit"
    (t / "other.txt").write_text("not deciding\n", encoding="utf-8")
    git(t, "checkout", "-q", "HEAD~1")
    git(t, "add", "other.txt")
    git(t, "commit", "-q", "-m", "a change outside the deciding files")
    assert R.go_row_present(decl, log), "other files may change"


def test_go_row_present_is_false_once_the_search_is_closed_or_has_finalists(tmp_path):
    t, runner = runner_tree(tmp_path)
    good = [G.P13, G.go("E-902", "F-13", G.A, run=runner)]
    decl = t / "prereg" / "F-13_x.md"
    assert R.go_row_present(decl, with_log(t, good))
    assert not R.go_row_present(decl, with_log(t, good + [G.fin("E-904", "F-13", G.A)]))
    assert not R.go_row_present(decl, with_log(t, good + [G.closed("E-904", "F-13", G.A, day="2026-12-05")]))


def test_go_row_present_needs_the_file_at_its_pinned_sha_and_a_clean_log(tmp_path):
    t, runner = runner_tree(tmp_path)
    log = with_log(t, [G.P13, G.go("E-902", "F-13", G.A, run=runner)])
    decl = t / "prereg" / "F-13_x.md"
    decl.write_text(G.F13 + "edited\n", encoding="utf-8")
    assert not R.go_row_present(decl, log), "the file no longer hashes to its pin"
    git(t, "checkout", "--", "prereg/F-13_x.md")
    assert R.go_row_present(decl, log)
    assert not R.go_row_present(decl, log + "```\n"), "a log with a go problem"
    assert not R.go_row_present(t / "prereg" / "F-99_none.md", log), "no such file"


def test_go_row_present_needs_the_deciding_files_in_both_commits(tmp_path):
    body = G.search("F-13", deciding="`extended/reader.py`, `scripts/later.py`")
    t, runner = runner_tree(tmp_path, {"F-13_x.md": body})
    s = G.sha(body)
    (t / "scripts" / "later.py").write_text("# added after the runner commit\n", encoding="utf-8")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "a deciding file the runner commit lacks")
    log = with_log(t, [G.pin("E-900", "F-13", s), G.go("E-902", "F-13", s, run=runner)])
    assert not R.go_row_present(t / "prereg" / "F-13_x.md", log)


# --------------------------------------------------------------------------------------------- the real log


def test_the_real_log_is_clean():
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.go_problems(text, ROOT / "prereg") == []
    assert R.membership_event(text) is None
    assert R.heldout_token_problems(text) == []
