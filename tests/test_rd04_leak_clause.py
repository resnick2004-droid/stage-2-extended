"""T-15 of reading VD (`prereg/DRAFT_RD-04_volatility_drift.md`, renamed `prereg/RD-04_volatility_drift.md` at its pin;
section 9.3, the red team's M5 and, in the third text, its re-read's M1 and m5): **the leak clause, made mechanical.**

RD-04 reads the judged block's volatility and P-14's and P-16's supply in it. From the commit of its step 2's first run
the lead's program rule binds: every later declaration states in its header that it was written after RD-04 was read,
naming the row that recorded RD-04's step 2. This test enforces that line, failing closed:

- **the anchors.** *The step-2 row* is the first decision row, in the log's order, whose third cell **begins** with
  the token `` `RD-04 read: step 2` `` (E-104's positional form). *The read* is the first line of the read ledger
  (`results/read_ledger.jsonl`) whose `declaration.ref` is RD-04's file and whose purpose is `volatility_descriptive`:
  it is written before the bars are read, so it exists from step 2's first run on. **Once the read exists, the test
  fails unless a step-2 row exists** -- a mistyped or missing row can never switch the rule off;
- **in scope**, RD-04's own file excepted, every declaration -- a `` `prereg/F-..md` `` or `` `prereg/RD-..md` `` pin
  as `tests/test_declarations_fixed.py` reads them, or a `` `docs/calibration/...md` `` pin -- whose path is **first**
  pinned (a) **in or after** the step-2 row, or (b) in a row **absent from `DECISIONS.md` at the read's commit**
  (`who.commit`, the run's own commit, which precedes the read). A file first pinned earlier and cited again later is
  exempt;
- **each such file's header** -- the text before its first line beginning ``## ``, whitespace collapsed -- holds the
  words ``written after RD-04 was read`` and the step-2 row's id; **or** the row that first pins it carries the
  pre-read form `` `written before RD-04 was read, unchanged since <commit>: <path>` `` (the lead's ruling on m5),
  checked against git: the file at that commit, under its path or its draft name, has the pinned LF sha256, and the
  commit is an ancestor of, and not, the read's commit and the step-2 row's commit (with neither committed, an
  ancestor of HEAD). The form lives in the pinning row, not the file: a file cannot name a commit at which it was
  already byte-identical to itself with that name in it.

The phrase check is lexical (a header saying "not written after RD-04 was read" passes): that, and items 2 and 3 of the
clause (no figure of RD-04 as the reason for a value; the choice block the only source of a family's choices), are the
red team's and the auditor's reads.

Fast tier, text and git metadata only: no engine, no bar, no result value (the ledger's lines are read for their
declaration, purpose and commit only).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = "`RD-04 read: step 2`"
PHRASE = "written after RD-04 was read"
PRE_PHRASE = "written before RD-04 was read, unchanged since"
RD04 = "prereg/RD-04_volatility_drift.md"
PURPOSE = "volatility_descriptive"
LEDGER = "results/read_ledger.jsonl"
#: the pins `tests/test_declarations_fixed.py` reads: families and described readings, and calibration plans
PIN = re.compile(r"`((?:prereg/(?:F|RD)-\d+[^`]*|docs/calibration/[^`]+)\.md)` sha256 `([0-9a-f]{64})`")
PRE_FORM = re.compile(r"`" + re.escape(PRE_PHRASE) + r" ([0-9a-f]{7,40}): ([^`\s]+)`")
ROW = re.compile(r"^\|\s*(E-\d+)\s*\|")
#: a row's third cell (after the id and the date), its leading spaces dropped
THIRD = re.compile(r"^\|[^|]*\|[^|]*\|\s*(.*)$")
HEX = re.compile(r"[0-9a-f]{40}")
_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR")


# ------------------------------------------------------------------------------------------------- git and the log


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV}
    return subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=60, env=env)


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


def rd04_read(root: Path) -> dict | None:
    """The first ledger line of RD-04's `volatility_descriptive` read, or None. A line that does not parse fails."""
    p = root / LEDGER
    if not p.is_file():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)                                   # a ledger that does not parse fails the test
        if (rec.get("declaration") or {}).get("ref") == RD04 and rec.get("purpose") == PURPOSE:
            return rec
    return None


def first_pins(log: str) -> dict[str, tuple[int, str, str, str]]:
    """{path: (row position, row id, pinned sha256, the row's line)} at each path's first pin."""
    out: dict[str, tuple[int, str, str, str]] = {}
    for i, (rid, line) in enumerate(decision_rows(log)):
        for rel, sha in PIN.findall(line):
            out.setdefault(rel, (i, rid, sha, line))
    return out


def rows_at(root: Path, commit: str) -> set[str] | None:
    r = git(root, "show", f"{commit}:DECISIONS.md")
    if r.returncode != 0:
        return None
    return {rid for rid, _ in decision_rows(r.stdout.decode("utf-8"))}


def row_commit(root: Path, rid: str) -> str | None:
    """The earliest commit whose `DECISIONS.md` holds row `rid`; None while the row is uncommitted."""
    r = git(root, "log", "--format=%H", "--reverse", "-S", f"| {rid} |", "--", "DECISIONS.md")
    hashes = HEX.findall(r.stdout.decode("utf-8")) if r.returncode == 0 else []
    return hashes[0] if hashes else None


def header(text: str) -> str:
    """The text before the first line beginning '## ', its whitespace collapsed to single spaces."""
    lines = text.replace("\r\n", "\n").split("\n")
    end = next((i for i, line in enumerate(lines) if line.startswith("## ")), len(lines))
    return " ".join(" ".join(lines[:end]).split())


def names_row(text: str, rid: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(rid)}(?!\d)", text) is not None


def _draft_name(rel: str) -> str:
    head, _, name = rel.rpartition("/")
    return f"{head}/DRAFT_{name}"


def pre_read_problems(root: Path, rel: str, sha: str, commit: str, anchors: list[str]) -> list[str]:
    """Why the pre-read form for `rel` does not hold: the file at `commit` (its path or its draft name) must have the
    pinned LF sha256, and `commit` must be an ancestor of, and not, every anchor; with no anchor, an ancestor of HEAD
    (HEAD itself allowed)."""
    r = git(root, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
    if r.returncode != 0:
        return [f"{rel}: the pre-read form names {commit}, which is no commit"]
    full = r.stdout.decode().strip()
    got = None
    for name in (rel, _draft_name(rel)):
        b = git(root, "show", f"{full}:{name}")
        if b.returncode == 0:
            got = hashlib.sha256(b.stdout.replace(b"\r\n", b"\n")).hexdigest()
            break
    out = []
    if got is None:
        out.append(f"{rel}: not present at {full[:12]} under its name or its draft name")
    elif got != sha:
        out.append(f"{rel}: changed since {full[:12]} (its pinned sha256 is not that commit's) -- the pre-read form "
                   "is false")
    if not anchors:
        if git(root, "merge-base", "--is-ancestor", full, "HEAD").returncode != 0:
            out.append(f"{rel}: {full[:12]} is not in this tree's history")
    for a in anchors:
        if full == a or git(root, "merge-base", "--is-ancestor", full, a).returncode != 0:
            out.append(f"{rel}: {full[:12]} is not older than {a[:12]}, so the text was not fixed before RD-04's read")
    return out


def problems(log: str, root: Path) -> list[str]:
    """Why the log's later pins break the clause's line: [] when none does (or RD-04 has not been read)."""
    read = rd04_read(root)
    step = step2_row(log)
    out: list[str] = []
    if read is None and step is None:
        return out
    run_commit = None
    if read is not None:
        m = HEX.search(str((read.get("who") or {}).get("commit") or ""))
        run_commit = m.group(0) if m else None
        if step is None:
            out.append(f"the read ledger holds RD-04's {PURPOSE} read (run {(read.get('who') or {}).get('run_id')}) "
                       f"but no decision row's third cell begins with {TOKEN}: the lead's step-2 row is missing or "
                       "mistyped (RD-04 9.3)")
        if run_commit is None:
            out.append("RD-04's ledger line names no commit")
    present = rows_at(root, run_commit) if run_commit else None
    if run_commit and present is None:
        out.append(f"DECISIONS.md cannot be read at RD-04's run commit {run_commit[:12]}")
    at, rid = step if step is not None else (None, None)
    anchors = [c for c in (run_commit, row_commit(root, rid) if rid else None) if c]
    for rel, (i, pinned_in, sha, line) in sorted(first_pins(log).items()):
        if rel == RD04:
            continue
        in_or_after_row = at is not None and i >= at
        after_run = present is not None and pinned_in not in present
        if not (in_or_after_row or after_run):
            continue
        pre = [c for c, path in PRE_FORM.findall(line) if path == rel]
        if pre:
            out += pre_read_problems(root, rel, sha, pre[0], anchors)
            continue
        p = root / rel
        if not p.is_file():
            out.append(f"{rel} (first pinned in {pinned_in}) does not exist")
            continue
        head = header(p.read_text(encoding="utf-8"))
        if PHRASE.lower() not in head.lower():
            out.append(f"{rel} (first pinned in {pinned_in}, after RD-04's read) lacks '{PHRASE}' in its header and "
                       "its row carries no pre-read form (RD-04 9.3)")
        if rid and not names_row(head, rid):
            out.append(f"{rel} (first pinned in {pinned_in}) does not name {rid}, the row recording RD-04's step 2")
    return out


# ------------------------------------------------------------------------------------------------- the real log


def test_every_declaration_pinned_after_rd04s_step_2_says_it_was_written_after():
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    bad = problems(log, ROOT)
    assert not bad, "\n".join(bad)


# ------------------------------------------------------------------------------------------------- synthetic cases


SHA_A, SHA_B, SHA_C, SHA_D = ("a" * 64, "b" * 64, "c" * 64, "d" * 64)
OLD = "prereg/F-03_opening_timing.md"
NEW = "prereg/F-04_new_family.md"
PLAN = "docs/calibration/Q-200_plan.md"
HEAD_LOG = "# Decisions\n\n| id | date | decision | basis |\n|---|---|---|---|\n"


def _row(rid: str, body: str) -> str:
    return f"| {rid} | 2026-12-01 | **{body}** | basis |"


def _step2(rid: str, rest: str = "RD-04's step 2 recorded") -> str:
    return f"| {rid} | 2026-12-01 | {TOKEN} **{rest}** | basis |"


def _log(rows: list[str]) -> str:
    return HEAD_LOG + "\n".join(rows) + "\n"


def _tree(tmp_path: Path, files: dict[str, str], rows: list[str]) -> tuple[str, Path]:
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return _log(rows), tmp_path


def _with_line(rid: str) -> str:
    return (f"# F-04: a later family\n\n**Its text's history.** This text was written after RD-04 was\nread "
            f"({rid}).\n\n## 1. Body\n")


def _ledger(root: Path, commit: str, run_id: str = "run-1") -> None:
    p = root / LEDGER
    p.parent.mkdir(parents=True, exist_ok=True)
    other = {"declaration": {"ref": "E-010", "kind": "identity"}, "purpose": "identity", "who": {"commit": commit}}
    mine = {"declaration": {"ref": RD04, "kind": "described_reading"}, "purpose": PURPOSE,
            "who": {"commit": commit, "run_id": run_id}}
    p.write_text(json.dumps(other) + "\n" + json.dumps(mine) + "\n", encoding="utf-8")


class Repo:
    """A synthetic repository with no hooks, for the git-anchored cases."""

    def __init__(self, path: Path, hooks: Path):
        self.path = path
        for args in (("init", "-q", f"--template={hooks}", "-b", "master"), ("config", "core.hooksPath", str(hooks)),
                     ("config", "user.email", "t@example.invalid"), ("config", "user.name", "t"),
                     ("config", "core.autocrlf", "false")):
            assert git(path, *args).returncode == 0, args

    def commit(self, files: dict[str, str], msg: str = "c") -> str:
        for rel, text in files.items():
            p = self.path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(text.encode("utf-8"))
        assert git(self.path, "add", "-A").returncode == 0
        r = git(self.path, "commit", "-q", "-m", msg)
        assert r.returncode == 0, r.stderr
        return git(self.path, "rev-parse", "HEAD").stdout.decode().strip()


def _repo(tmp_path_factory) -> Repo:
    return Repo(tmp_path_factory.mktemp("leak_repo"), tmp_path_factory.mktemp("no_hooks"))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_nothing_read_binds_nothing(tmp_path):
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"}, [_row("E-300", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert problems(log, root) == []


def test_a_later_pin_without_the_line_is_refused(tmp_path):
    log, root = _tree(tmp_path, {NEW: "# F-04: a later family\n\n## 1. Body\n"},
                      [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    bad = problems(log, root)
    assert len(bad) == 2 and PHRASE in bad[0] and "E-300" in bad[1]


def test_a_later_pin_with_the_line_is_admitted_even_wrapped(tmp_path):
    log, root = _tree(tmp_path, {NEW: _with_line("E-300")},
                      [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert problems(log, root) == []


def test_the_line_below_the_header_does_not_count(tmp_path):
    body = "# F-04\n\n## 1. Body\n\nThis text was written after RD-04 was read (E-300).\n"
    log, root = _tree(tmp_path, {NEW: body}, [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
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
                       _step2("E-300", f"and cites `{RD04}` sha256 `{SHA_B}` again"),
                       _row("E-301", f"re-cites `{OLD}` sha256 `{SHA_A}` and `{RD04}` sha256 `{SHA_B}`")])
    assert problems(log, root) == []


def test_a_calibration_plan_and_a_described_reading_are_in_scope(tmp_path):
    rd = "prereg/RD-05_later_reading.md"
    log, root = _tree(tmp_path, {PLAN: "# Plan\n\n## 1. Body\n", rd: _with_line("E-300")},
                      [_step2("E-300"), _row("E-301", f"pins `{PLAN}` sha256 `{SHA_C}`"),
                       _row("E-302", f"pins `{rd}` sha256 `{SHA_D}`")])
    bad = problems(log, root)
    assert len(bad) == 2 and all(b.startswith(PLAN) for b in bad)


def test_a_row_quoting_the_token_is_not_the_step_2_row(tmp_path):
    """The pinning row may describe the rule and quote the token; only a third cell beginning with it counts."""
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"},
                      [_row("E-290", f"RD-04 pinned; the step-2 row will carry {TOKEN}"),
                       _row("E-291", f"pins `{NEW}` sha256 `{SHA_A}`")])
    assert step2_row(log) is None and problems(log, root) == []


def test_a_later_pin_of_a_missing_file_is_refused(tmp_path):
    log, root = _tree(tmp_path, {}, [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`")])
    bad = problems(log, root)
    assert len(bad) == 1 and "does not exist" in bad[0]


def test_a_ledger_without_rd04s_read_binds_nothing(tmp_path):
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"}, [_row("E-300", f"pins `{NEW}` sha256 `{SHA_A}`")])
    p = root / LEDGER
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"declaration": {"ref": "E-010"}, "purpose": "identity", "who": {}}) + "\n",
                 encoding="utf-8")
    assert problems(log, root) == []


# ---- the red team's three fail-open routes (Q-123r2 M1), each refused now


def test_route_1_a_pin_inside_the_step_2_row_is_in_scope(tmp_path):
    """The second text's `i > at` left a pin in the step-2 row itself out of scope; it is in scope now."""
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"},
                      [_step2("E-300", f"and pins `{NEW}` sha256 `{SHA_A}`")])
    bad = problems(log, root)
    assert len(bad) == 2 and bad[0].startswith(NEW) and PHRASE in bad[0]


def test_route_2_a_pin_after_the_run_but_before_the_step_2_row_is_in_scope(tmp_path_factory):
    """A row pinned after the run's commit and before the step-2 row is absent at the run's commit, so in scope; a
    row already present there is not."""
    repo = _repo(tmp_path_factory)
    run = repo.commit({"DECISIONS.md": _log([_row("E-299", f"RD-04 pinned; pins `{OLD}` sha256 `{SHA_B}`")]),
                       OLD: "# F-03\n\n## 1. Body\n", NEW: "# F-04\n\n## 1. Body\n"})
    _ledger(repo.path, run)
    log = _log([_row("E-299", f"RD-04 pinned; pins `{OLD}` sha256 `{SHA_B}`"),
                _row("E-300", f"pins `{NEW}` sha256 `{SHA_A}`"), _step2("E-301")])
    repo.commit({"DECISIONS.md": log})
    bad = problems(log, repo.path)
    assert [b for b in bad if b.startswith(NEW)] and not [b for b in bad if b.startswith(OLD)], bad


def test_route_3_a_read_with_no_step_2_row_fails(tmp_path):
    """A step-2 row whose third cell does not begin with the token: once the ledger holds RD-04's read, the test fails
    -- the rule is never switched off silently."""
    log, root = _tree(tmp_path, {}, [_row("E-300", f"RD-04 step 2 recorded {TOKEN}")])
    assert step2_row(log) is None
    _ledger(root, "0" * 40)
    bad = problems(log, root)
    assert any("no decision row's third cell begins with" in b for b in bad), bad


# ---- the pre-read form (the lead's ruling on Q-123r2 m5)


def _pre_read_case(tmp_path_factory, *, edit_after: bool = False, fixed_after_run: bool = False):
    repo = _repo(tmp_path_factory)
    draft = "# F-04: a family drafted before RD-04 was read\n\n## 1. Body\n"
    rel_draft = "prereg/DRAFT_F-04_new_family.md"
    run = repo.commit({"DECISIONS.md": _log([_row("E-299", "RD-04 pinned")])})
    fixed = repo.commit({rel_draft: draft})
    if not fixed_after_run:                         # the draft fixed first, the run's commit after it
        run = repo.commit({"DECISIONS.md": _log([_row("E-299", "RD-04 pinned"), _row("E-298", "a note")])})
    _ledger(repo.path, run)
    pinned = draft + ("\nan edit after the read\n" if edit_after else "")
    log = _log([_row("E-299", "RD-04 pinned"), _step2("E-300"),
                _row("E-301", f"pins `{NEW}` sha256 `{_sha(pinned)}`; `{PRE_PHRASE} {fixed}: {NEW}`")])
    repo.commit({"DECISIONS.md": log, NEW: pinned})
    return log, repo.path


def test_the_pre_read_form_admits_an_unchanged_earlier_draft(tmp_path_factory):
    log, root = _pre_read_case(tmp_path_factory)
    assert problems(log, root) == []


def test_the_pre_read_form_refuses_a_text_changed_since(tmp_path_factory):
    log, root = _pre_read_case(tmp_path_factory, edit_after=True)
    bad = problems(log, root)
    assert len(bad) == 1 and "changed since" in bad[0]


def test_the_pre_read_form_refuses_a_commit_not_older_than_the_read(tmp_path_factory):
    log, root = _pre_read_case(tmp_path_factory, fixed_after_run=True)
    bad = problems(log, root)
    assert bad and all("is not older than" in b for b in bad), bad


def test_the_pre_read_form_refuses_a_commit_that_does_not_exist(tmp_path):
    log, root = _tree(tmp_path, {NEW: "# F-04\n\n## 1. Body\n"},
                      [_step2("E-300"), _row("E-301", f"pins `{NEW}` sha256 `{SHA_A}`; `{PRE_PHRASE} {'f' * 40}: {NEW}`")])
    bad = problems(log, root)
    assert len(bad) == 1 and "no commit" in bad[0]
