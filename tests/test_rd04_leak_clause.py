"""T-15 of reading VD (`prereg/DRAFT_RD-04_volatility_drift.md`, renamed `prereg/RD-04_volatility_drift.md` at its pin;
section 9.3, the red team's M5): **the leak clause, made mechanical.**

RD-04 reads the judged block's volatility and P-14's and P-16's supply in it. From the commit of its step 2's first run
the lead's program rule binds: every later declaration states in its header that it was written after RD-04 was read,
naming the row that recorded RD-04's step 2. This test enforces that line on the decision log as it stands:

- **the step-2 row** is the first decision row, in the log's order, whose third cell **begins** with the token
  `` `RD-04 read: step 2` `` (E-104's positional form; the lead writes it in the row that records step 2's first run,
  whatever its outcome). A row that only quotes the token elsewhere -- the pinning row describing the rule, say -- is
  not the step-2 row. Until such a row exists, the test binds nothing on the real log; its synthetic cases still run;
- **in scope**: every declaration whose path is **first** pinned in a row after the step-2 row -- a
  `` `prereg/F-..md` `` or `` `prereg/RD-..md` `` pin, read as `tests/test_declarations_fixed.py` reads them, or a
  `` `docs/calibration/...md` `` pin. RD-04's own file is excepted, and a file first pinned earlier and cited again
  later is exempt;
- **each such file's header** -- the text before its first line beginning ``## ``, whitespace collapsed -- holds the
  words ``written after RD-04 was read`` and the step-2 row's id. A file without them fails the suite (and so the
  pre-commit hook).

Items 2 and 3 of the clause (no figure of RD-04 as the reason for a value; the choice block the only source of a
family's choices) are the red team's and the auditor's reads: no test can tell a reason from a figure.

Fast tier, text only: no engine, no bar, no result file.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = "`RD-04 read: step 2`"
PHRASE = "written after RD-04 was read"
RD04 = "prereg/RD-04_volatility_drift.md"
#: the pins `tests/test_declarations_fixed.py` reads: families and described readings, and calibration plans
PIN = re.compile(r"`((?:prereg/(?:F|RD)-\d+[^`]*|docs/calibration/[^`]+)\.md)` sha256 `([0-9a-f]{64})`")
ROW = re.compile(r"^\|\s*(E-\d+)\s*\|")
#: a row's third cell (after the id and the date), its leading spaces dropped
THIRD = re.compile(r"^\|[^|]*\|[^|]*\|\s*(.*)$")


def decision_rows(log: str) -> list[tuple[str, str]]:
    """[(row id, the row's line)] in the log's order."""
    return [(m.group(1), line) for line in log.splitlines() if (m := ROW.match(line))]


def step2_row(log: str) -> tuple[int, str] | None:
    """(its position among the rows, its id) of the first row whose third cell begins with `TOKEN`, or None."""
    for i, (rid, line) in enumerate(decision_rows(log)):
        m = THIRD.match(line)
        if m and m.group(1).startswith(TOKEN):
            return i, rid
    return None


def in_scope(log: str) -> tuple[str | None, list[tuple[str, str]]]:
    """(the step-2 row's id or None, [(path, the row that first pins it)] for every path first pinned after it)."""
    found = step2_row(log)
    if found is None:
        return None, []
    at, rid = found
    first: dict[str, tuple[int, str]] = {}
    for i, (row_id, line) in enumerate(decision_rows(log)):
        for rel, _ in PIN.findall(line):
            first.setdefault(rel, (i, row_id))
    later = [(rel, row_id) for rel, (i, row_id) in first.items() if i > at and rel != RD04]
    return rid, sorted(later)


def header(text: str) -> str:
    """The text before the first line beginning '## ', its whitespace collapsed to single spaces."""
    lines = text.replace("\r\n", "\n").split("\n")
    end = next((i for i, line in enumerate(lines) if line.startswith("## ")), len(lines))
    return " ".join(" ".join(lines[:end]).split())


def names_row(text: str, rid: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(rid)}(?!\d)", text) is not None


def problems(log: str, root: Path) -> list[str]:
    """Why the log's later pins break the clause's line: [] when none does (or no step-2 row exists yet)."""
    rid, later = in_scope(log)
    out = []
    for rel, pinned_in in later:
        p = root / rel
        if not p.is_file():
            out.append(f"{rel} (first pinned in {pinned_in}) does not exist")
            continue
        head = header(p.read_text(encoding="utf-8"))
        if PHRASE.lower() not in head.lower():
            out.append(f"{rel} (first pinned in {pinned_in}, after {rid}) lacks '{PHRASE}' in its header (RD-04 9.3)")
        if not names_row(head, rid):
            out.append(f"{rel} (first pinned in {pinned_in}) does not name {rid}, the row recording RD-04's step 2")
    return out


# ------------------------------------------------------------------------------------------------- the real log


def test_every_declaration_pinned_after_rd04s_step_2_says_it_was_written_after():
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    bad = problems(log, ROOT)
    assert not bad, "\n".join(bad)


# ------------------------------------------------------------------------------------------------- synthetic cases


SHA_A, SHA_B, SHA_C, SHA_D = ("a" * 64, "b" * 64, "c" * 64, "d" * 64)


def _row(rid: str, body: str) -> str:
    return f"| {rid} | 2026-12-01 | **{body}** | basis |"


def _step2(rid: str, rest: str = "RD-04's step 2 recorded") -> str:
    return f"| {rid} | 2026-12-01 | {TOKEN} **{rest}** | basis |"


def _tree(tmp_path: Path, files: dict[str, str], rows: list[str]) -> tuple[str, Path]:
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    log = "# Decisions\n\n| id | date | decision | basis |\n|---|---|---|---|\n" + "\n".join(rows) + "\n"
    return log, tmp_path


OLD = "prereg/F-03_opening_timing.md"
NEW = "prereg/F-04_new_family.md"
PLAN = "docs/calibration/Q-200_plan.md"


def _with_line(rid: str) -> str:
    return (f"# F-04: a later family\n\n**Its text's history.** This text was written after RD-04 was\nread "
            f"({rid}).\n\n## 1. Body\n")


def test_no_step_2_row_binds_nothing(tmp_path):
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"},
                      [_row("E-300", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert in_scope(log) == (None, [])
    assert problems(log, root) == []


def test_a_later_pin_without_the_line_is_refused(tmp_path):
    log, root = _tree(tmp_path, {NEW: "# F-04: a later family\n\n## 1. Body\n"},
                      [_step2("E-300"),
                       _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert in_scope(log) == ("E-300", [(NEW, "E-301")])
    bad = problems(log, root)
    assert len(bad) == 2 and PHRASE in bad[0] and "E-300" in bad[1]


def test_a_later_pin_with_the_line_is_admitted_even_wrapped(tmp_path):
    log, root = _tree(tmp_path, {NEW: _with_line("E-300")},
                      [_step2("E-300"),
                       _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert problems(log, root) == []


def test_the_line_below_the_header_does_not_count(tmp_path):
    body = "# F-04\n\n## 1. Body\n\nThis text was written after RD-04 was read (E-300).\n"
    log, root = _tree(tmp_path, {NEW: body},
                      [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert len(problems(log, root)) == 2


def test_the_line_must_name_the_step_2_row(tmp_path):
    log, root = _tree(tmp_path, {NEW: _with_line("E-3000")},
                      [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    bad = problems(log, root)
    assert len(bad) == 1 and "does not name E-300" in bad[0]


def test_an_earlier_pin_cited_again_later_is_exempt_and_rd04_is_excepted(tmp_path):
    log, root = _tree(tmp_path, {OLD: "# F-03\n\n## 1. Body\n", RD04: "# RD-04\n\n## 1. Body\n"},
                      [_row("E-200", f"pins `{OLD}` sha256 `{SHA_A}`"),
                       _row("E-250", f"pins `{RD04}` sha256 `{SHA_B}`"),
                       _step2("E-300"),
                       _row("E-301", f"re-cites `{OLD}` sha256 `{SHA_A}` and `{RD04}` sha256 `{SHA_B}`")])
    assert in_scope(log) == ("E-300", [])
    assert problems(log, root) == []


def test_a_calibration_plan_and_a_described_reading_are_in_scope(tmp_path):
    rd = "prereg/RD-05_later_reading.md"
    log, root = _tree(tmp_path, {PLAN: "# Plan\n\n## 1. Body\n", rd: _with_line("E-300")},
                      [_step2("E-300"),
                       _row("E-301", f"pins `{PLAN}` sha256 `{SHA_C}`"),
                       _row("E-302", f"pins `{rd}` sha256 `{SHA_D}`")])
    assert in_scope(log)[1] == sorted([(PLAN, "E-301"), (rd, "E-302")])
    bad = problems(log, root)
    assert len(bad) == 2 and all(b.startswith(PLAN) for b in bad)


def test_only_the_first_token_row_counts_and_a_pin_in_it_is_not_later(tmp_path):
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"},
                      [_step2("E-300", f"and pins `{NEW}` sha256 `{SHA_A}`"), _step2("E-305", "a repeat")])
    assert in_scope(log) == ("E-300", [])


def test_a_row_quoting_the_token_is_not_the_step_2_row(tmp_path):
    """The pinning row may describe the rule and quote the token; only a third cell beginning with it counts."""
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"},
                      [_row("E-290", f"RD-04 pinned; the step-2 row will carry {TOKEN}"),
                       _row("E-291", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert in_scope(log) == (None, [])
    assert problems(log, root) == []


def test_a_later_pin_of_a_missing_file_is_refused(tmp_path):
    log, root = _tree(tmp_path, {}, [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    bad = problems(log, root)
    assert len(bad) == 1 and "does not exist" in bad[0]
