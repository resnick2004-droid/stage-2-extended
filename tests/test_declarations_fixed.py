"""A declared family is fixed by its sha256 in its decision row (E-003): the file on disk must still hash to it."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: a pinned declaration: a family (`F-nn`), from E-025 a described reading (`RD-nn`, E-023 (1): declared and pinned,
#: never carried), and a heavy-queue declaration (`H<n>_<name>`, H3's text on, the gatekeeper's pin condition)
PIN = re.compile(r"`(prereg/(?:(?:F|RD)-\d+|H\d+_)[^`/]*\.md)` sha256 `([0-9a-f]{64})`")
#: a declaration awaiting its pin row (its text final on a branch, its row the lead's): listed here until pinned
AWAITING_PIN = ("prereg/H3_three_way.md",)


def test_the_pin_grammar_reads_every_kind_of_declaration():
    """A family's, a described reading's and a heavy-queue declaration's pin are read; a draft's and a template's are
    not (they are never pinned)."""
    h = "0" * 64
    log = (f"| E-1 | `prereg/F-01_x.md` sha256 `{h}` | `prereg/RD-02_y.md` sha256 `{h}` | "
           f"`prereg/H3_three_way.md` sha256 `{h}` | `prereg/DRAFT_H3_three_way.md` sha256 `{h}` | "
           f"`prereg/TEMPLATE_family.md` sha256 `{h}` | `prereg/H_x.md` sha256 `{h}` |")
    assert [p for p, _ in PIN.findall(log)] == ["prereg/F-01_x.md", "prereg/RD-02_y.md", "prereg/H3_three_way.md"]


def test_every_declared_family_matches_its_pinned_hash():
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pins = PIN.findall(log)
    assert pins, "no family pinned in DECISIONS.md"
    for rel, want in pins:
        data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == want, rel


def test_every_pinned_config_file_matches_its_hash():
    """From E-029: a configuration file a family relies on (e.g. the early-close calendar) is pinned by its sha256 in a
    decision row and may not change after; a new version is a new file under a new row."""
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pins = re.findall(r"`(config/[^`]+\.(?:csv|yaml|json))` sha256 `([0-9a-f]{64})`", log)
    for rel, want in pins:
        data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == want, rel


def test_every_pinned_calibration_plan_matches_its_hash():
    """From E-115: a calibration plan (a statistic's candidates, nulls, seeds and rules, declared before any run) is
    pinned by its sha256 in a decision row like a family, and may not change after; a revision is a new file under a new
    row. Earlier rows cite drafts as "..., LF sha256 ..." and are not pins."""
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pins = re.findall(r"`(docs/calibration/[^`]+\.md)` sha256 `([0-9a-f]{64})`", log)
    for rel, want in pins:
        data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == want, rel


def test_every_pinned_playbook_declaration_matches_its_hash():
    """From Wave 3.5's corrective cycle 2 (the red team's m-9): a carried design's playbook declaration
    (`prereg/<design>_playbook.json`, `extended/playbook.py`) is pinned by its sha256 (of its bytes, line ends as LF)
    in a decision row like a family, and an edit fails here, in the fast tier, not only when it is loaded."""
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pins = re.findall(r"`(prereg/[^`]*_playbook\.json)` sha256 `([0-9a-f]{64})`", log)
    for rel, want in pins:
        data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == want, rel



def test_every_pinnable_declaration_is_pinned_or_awaiting_its_row():
    """The red team's 805978a finding 5: every `prereg/*.md` that is not a draft (`DRAFT_`) or a template
    (`TEMPLATE_`) is pinned in DECISIONS.md by the grammar above, or listed in `AWAITING_PIN`; every pinnable name
    matches the grammar (so H3-D's later text, `prereg/H3_three_way_deciding.md`, is read when pinned); and no pin
    path climbs out of `prereg/`."""
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pinned = {rel for rel, _ in PIN.findall(log)}
    for rel in pinned:
        assert ".." not in rel and rel.count("/") == 1, rel
    files = sorted(f"prereg/{p.name}" for p in (ROOT / "prereg").glob("*.md")
                   if not p.name.startswith(("DRAFT_", "TEMPLATE_")))
    for rel in files:
        assert PIN.fullmatch(f"`{rel}` sha256 `{'0' * 64}`"), f"{rel} is not a name the pin grammar reads"
    missing = [rel for rel in files if rel not in pinned and rel not in AWAITING_PIN]
    assert not missing, f"declarations neither pinned nor awaiting their row: {missing}"
    h = "0" * 64
    assert PIN.fullmatch(f"`prereg/H3_three_way_deciding.md` sha256 `{h}`")
    for bad in ("prereg/H3_x/../F-01_y.md", "prereg/F-01_a/b.md", "prereg/H3_../x.md"):
        assert not PIN.fullmatch(f"`{bad}` sha256 `{h}`"), bad




#: the templates' pin (n-a, n-b of the red team's TEMPLATE_V3_DF7AB29 note; findings 8 and 9 of TEMPLATE_V3_DAFF8CC;
#: F1 of READER_Q212_TEMPLATE): the row pinning `prereg/TEMPLATE_design_search.md` or `prereg/TEMPLATE_heldout_test.md`
#: also pins `extended/reader.py` by its LF sha256, checked against the reader **as committed at that row's own commit**
#: (`git show <the row's commit>:extended/reader.py`), never today's file -- a later reader change never fails an old
#: pin; each search's reader is bound by its deciding files at its go row's runner commit. W42-R1's pin row -- an
#: unfenced decision row carrying `docs/plans/WAVE42_SETTING_RULE.md` or `extended/wave42.py` at the file's own LF
#: sha256 -- comes before it; and once a template is pinned, `extended/wave42.py` declares `DO_NOTHING_EPS`
_TEMPLATE_PIN = re.compile(r"`(prereg/TEMPLATE_(?:design_search|heldout_test)\.md)` sha256 `([0-9a-f]{64})`")
_READER_PIN = re.compile(r"`(extended/reader\.py)` sha256 `([0-9a-f]{64})`")
_W42_PIN = re.compile(r"`(docs/plans/WAVE42_SETTING_RULE\.md|extended/wave42\.py)` sha256 `([0-9a-f]{64})`")
_ROW = re.compile(r"\|\s*E-\d+\s*\|")


def _lf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _lf_bytes(b: bytes) -> str:
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def _unfenced(log: str) -> list[bool]:
    """True where a line of the log is outside every fenced block, by the reader's own fences."""
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from extended import reader as RD

    fenced, _ = RD._fences(log)
    return [not f for f in fenced]


def _git(root: Path, *args: str):
    import subprocess

    return subprocess.run(["git", "-C", str(root), *args], capture_output=True)


def _split_lines(log: str) -> list[str]:
    """Newline-only split matching extended.reader._split (Q-212, F5; avoids IndexError against RD._fences on U+2028)."""
    if not log:
        return []
    parts = log.split("\n")
    if parts[-1] == "":
        parts.pop()
    return [p[:-1] if p.endswith("\r") else p for p in parts]


def _reader_at_row(root: Path, line: str) -> bytes | None:
    """`extended/reader.py` at the commit introducing `line` (including merge commits via -m), or -- if `line` is not
    yet in HEAD:DECISIONS.md (e.g. during the template pin commit's own pre-commit hook) -- the staged/working-tree
    `extended/reader.py`. Returns None (fail closed) on git errors or missing reader."""
    head_log = _git(root, "--no-replace-objects", "show", "HEAD:DECISIONS.md")
    head_lines = _split_lines(head_log.stdout.decode("utf-8", errors="replace")) if head_log.returncode == 0 else []
    if line not in head_lines:
        # Uncommitted pin row being introduced in the current commit (pre-commit hook): check staged then working tree.
        staged = _git(root, "show", ":extended/reader.py")
        if staged.returncode == 0:
            return staged.stdout
        p = root / "extended" / "reader.py"
        return p.read_bytes() if p.is_file() else None
    r = _git(root, "--no-replace-objects", "log", "--format=%H", "--reverse", "--full-history", "-m",
             "--text", "--no-textconv", "--root", "-S", line, "--", "DECISIONS.md")
    commits = r.stdout.decode().split() if r.returncode == 0 else []
    for c in commits:
        dec = _git(root, "--no-replace-objects", "show", f"{c}:DECISIONS.md")
        if dec.returncode != 0 or line not in _split_lines(dec.stdout.decode("utf-8", errors="replace")):
            continue
        b = _git(root, "--no-replace-objects", "show", f"{c}:extended/reader.py")
        return b.stdout if b.returncode == 0 else None
    return None


def _template_pin_problems(log: str, root: Path) -> list[str]:
    out = []
    lines = _split_lines(log)
    live = _unfenced(log)
    rows = [i for i, ln in enumerate(lines) if live[i] and _ROW.match(ln) and _TEMPLATE_PIN.search(ln)]
    w42 = [i for i, ln in enumerate(lines) if live[i] and _ROW.match(ln)
           and any((root / rel).is_file() and _lf(root / rel) == want for rel, want in _W42_PIN.findall(ln))]
    for i in rows:
        for rel, want in _TEMPLATE_PIN.findall(lines[i]):
            if _lf(root / rel) != want:
                out.append(f"line {i + 1}: {rel} does not hash to its pin")
        rd = _READER_PIN.findall(lines[i])
        if not rd:
            out.append(f"line {i + 1}: a template pin row without `extended/reader.py`'s sha256 (n-a)")
        for _rel, want in rd:
            at = _reader_at_row(root, lines[i])
            if at is None or _lf_bytes(at) != want:
                out.append(f"line {i + 1}: extended/reader.py at the row's own commit does not hash to its pin (F1)")
        if not any(j < i for j in w42):
            out.append(f"line {i + 1}: a template pin row before W42-R1's pin row (n-b)")
    if rows:
        w = root / "extended" / "wave42.py"
        if not w.is_file() or not re.search(r"^DO_NOTHING_EPS\s*[:=]", w.read_text(encoding="utf-8"), re.M):
            out.append("a template is pinned but `extended/wave42.py` declares no `DO_NOTHING_EPS` (n-b)")
    return out


def test_the_templates_pin_row_carries_the_reader_and_follows_w42r1(tmp_path):
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert _template_pin_problems(log, ROOT) == [], _template_pin_problems(log, ROOT)
    # synthetic controls, in a git repository of their own
    nl = chr(10)
    files = {"prereg/TEMPLATE_design_search.md": "t" + nl, "prereg/TEMPLATE_heldout_test.md": "h" + nl,
             "extended/reader.py": "r1" + nl, "docs/plans/WAVE42_SETTING_RULE.md": "w" + nl,
             "extended/wave42.py": "DO_NOTHING_EPS = 1" + nl}
    for rel, body in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(body, encoding="utf-8", newline=nl)
    t, h, r, w = (_lf(tmp_path / rel) for rel in list(files)[:4])
    w42 = f"| E-900 | d | **W42-R1 pinned.** `docs/plans/WAVE42_SETTING_RULE.md` sha256 `{w}` | b |"
    pin = (f"| E-901 | d | **Templates pinned.** `prereg/TEMPLATE_design_search.md` sha256 `{t}`, "
           f"`prereg/TEMPLATE_heldout_test.md` sha256 `{h}`, `extended/reader.py` sha256 `{r}` | b |")

    def commit(log_lines, msg):
        (tmp_path / "DECISIONS.md").write_text(nl.join(log_lines) + nl, encoding="utf-8", newline=nl)
        _git(tmp_path, "add", "-A")
        hooks = tmp_path / ".nohooks"                                    # a synthetic repository runs no hook
        hooks.mkdir(exist_ok=True)
        assert _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "-c", f"core.hooksPath={hooks}", "commit",
                    "-q", "-m", msg).returncode == 0

    assert _git(tmp_path, "init", "-q").returncode == 0
    commit([w42, pin], "the pins")
    assert _template_pin_problems(nl.join([w42, pin]), tmp_path) == []
    # F1: a later reader change never fails the old pin
    (tmp_path / "extended" / "reader.py").write_text("r2" + nl, encoding="utf-8", newline=nl)
    commit([w42, pin, "| E-902 | d | a later reader | b |"], "a later reader")
    assert _template_pin_problems(nl.join([w42, pin]), tmp_path) == []
    # a pin row whose reader sha matches no reader at its own commit fails
    bad = pin.replace(r, "0" * 64).replace("E-901", "E-903")
    commit([w42, pin, "| E-902 | d | a later reader | b |", bad], "a bad pin")
    assert _template_pin_problems(nl.join([w42, bad]), tmp_path)
    assert _template_pin_problems(nl.join([w42, pin.replace("E-901", "E-909")]), tmp_path)   # uncommitted wrong reader sha
    # c2 F1: a staged uncommitted pin row whose reader matches the staged reader PASSES (no pre-commit deadlock)
    r2 = _lf(tmp_path / "extended" / "reader.py")
    pin_new = pin.replace("E-901", "E-909").replace(r, r2)
    (tmp_path / "DECISIONS.md").write_text(nl.join([w42, pin_new]) + nl, encoding="utf-8", newline=nl)
    _git(tmp_path, "add", "DECISIONS.md")
    assert _template_pin_problems(nl.join([w42, pin_new]), tmp_path) == []
    # c2 F1: a pin row introduced inside a --no-ff merge commit survives a later reader change
    commit([w42], "base before branch")
    _git(tmp_path, "checkout", "-q", "-b", "side")
    (tmp_path / "side.txt").write_text("s" + nl, encoding="utf-8", newline=nl)
    commit([w42], "side branch")
    _git(tmp_path, "checkout", "-q", "-")
    (tmp_path / "other.txt").write_text("x" + nl, encoding="utf-8", newline=nl)
    commit([w42], "main move")
    hooks = tmp_path / ".nohooks"
    assert _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "-c", f"core.hooksPath={hooks}",
                "merge", "--no-ff", "--no-commit", "side").returncode == 0
    pin_m = pin.replace("E-901", "E-910").replace(r, r2)
    commit([w42, pin_m], "merge with pin row")
    (tmp_path / "extended" / "reader.py").write_text("r3" + nl, encoding="utf-8", newline=nl)
    commit([w42, pin_m, "| E-911 | d | r3 | b |"], "later r3")
    assert _template_pin_problems(nl.join([w42, pin_m]), tmp_path) == []
    # n-a, n-b
    assert _template_pin_problems(nl.join([pin, w42]), tmp_path)                          # n-b: W42-R1 first
    assert _template_pin_problems(pin, tmp_path)
    assert _template_pin_problems(nl.join(["```", w42, "```", pin]), tmp_path)             # a fenced W42 pin
    assert _template_pin_problems(nl.join(["W42 draft: " + w42[2:], pin]), tmp_path)        # not a decision row
    assert _template_pin_problems(nl.join([w42.replace(w, "0" * 64), pin]), tmp_path)     # a draft's sha
    assert _template_pin_problems(nl.join([w42, pin.replace(f", `extended/reader.py` sha256 `{r}`", "")]),
                                  tmp_path)                                               # n-a: the reader's sha
    assert _template_pin_problems(nl.join([w42, pin.replace(t, "0" * 64)]), tmp_path)     # a template edited
    assert _template_pin_problems(nl.join(["```", pin, "```"]), tmp_path) == []           # a fenced pin row: none
    (tmp_path / "extended" / "wave42.py").write_text("x = 1" + nl, encoding="utf-8")
    assert _template_pin_problems(nl.join([w42, pin]), tmp_path)                          # DO_NOTHING_EPS required
