"""A declared family is fixed by its sha256 in its decision row (E-003): the file on disk must still hash to it."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_every_declared_family_matches_its_pinned_hash():
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    # Families (`F-nn`) and, from E-025, described readings (`RD-nn`, E-023 (1): declared and pinned, never carried).
    pins = re.findall(r"`(prereg/(?:F|RD)-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`", log)
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


#: the templates' pin (n-a, n-b of the red team's TEMPLATE_V3_DF7AB29 note; findings 8 and 9 of TEMPLATE_V3_DAFF8CC):
#: the row pinning `prereg/TEMPLATE_design_search.md` or `prereg/TEMPLATE_heldout_test.md` also pins
#: `extended/reader.py` (the log's one parser, the go token's rules among them, Q-212) by its LF sha256; W42-R1's pin
#: row -- an unfenced decision row carrying `docs/plans/WAVE42_SETTING_RULE.md` or `extended/wave42.py` at the file's
#: own LF sha256 -- comes before it; and once a template is pinned, `extended/wave42.py` declares `DO_NOTHING_EPS`
_TEMPLATE_PIN = re.compile(r"`(prereg/TEMPLATE_(?:design_search|heldout_test)\.md)` sha256 `([0-9a-f]{64})`")
_READER_PIN = re.compile(r"`(extended/reader\.py)` sha256 `([0-9a-f]{64})`")
_W42_PIN = re.compile(r"`(docs/plans/WAVE42_SETTING_RULE\.md|extended/wave42\.py)` sha256 `([0-9a-f]{64})`")
_ROW = re.compile(r"\|\s*E-\d+\s*\|")


def _lf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _unfenced(log: str) -> list[bool]:
    """True where a line of the log is outside every fenced block, by the reader's own fences."""
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from extended import reader as RD

    fenced, _ = RD._fences(log)
    return [not f for f in fenced]


def _template_pin_problems(log: str, root: Path) -> list[str]:
    out = []
    lines = log.splitlines()
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
        for rel, want in rd:
            if _lf(root / rel) != want:
                out.append(f"line {i + 1}: extended/reader.py does not hash to its pin (n-a)")
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
    # synthetic controls
    files = {"prereg/TEMPLATE_design_search.md": "t\n", "prereg/TEMPLATE_heldout_test.md": "h\n",
             "extended/reader.py": "r\n", "docs/plans/WAVE42_SETTING_RULE.md": "w\n",
             "extended/wave42.py": "DO_NOTHING_EPS = 1\n"}
    for rel, body in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(body, encoding="utf-8", newline="\n")
    t, h, r, w = (_lf(tmp_path / rel) for rel in list(files)[:4])
    w42 = f"| E-900 | d | **W42-R1 pinned.** `docs/plans/WAVE42_SETTING_RULE.md` sha256 `{w}` | b |"
    pin = (f"| E-901 | d | **Templates pinned.** `prereg/TEMPLATE_design_search.md` sha256 `{t}`, "
           f"`prereg/TEMPLATE_heldout_test.md` sha256 `{h}`, `extended/reader.py` sha256 `{r}` | b |")
    nl = chr(10)
    assert _template_pin_problems(nl.join([w42, pin]), tmp_path) == []
    assert _template_pin_problems(nl.join([pin, w42]), tmp_path)                          # n-b: W42-R1 first
    assert _template_pin_problems(pin, tmp_path)
    assert _template_pin_problems(nl.join(["```", w42, "```", pin]), tmp_path)             # a fenced W42 pin
    assert _template_pin_problems(nl.join(["W42 draft: " + w42[2:], pin]), tmp_path)        # not a decision row
    assert _template_pin_problems(nl.join([w42.replace(w, "0" * 64), pin]), tmp_path)     # a draft's sha
    assert _template_pin_problems(nl.join([w42, pin.replace(f", `extended/reader.py` sha256 `{r}`", "")]),
                                  tmp_path)                                               # n-a: the reader's sha
    assert _template_pin_problems(nl.join([w42, pin.replace(r, "0" * 64)]), tmp_path)     # the reader edited
    assert _template_pin_problems(nl.join([w42, pin.replace(t, "0" * 64)]), tmp_path)     # a template edited
    assert _template_pin_problems(nl.join(["```", pin, "```"]), tmp_path) == []           # a fenced pin row: none
    (tmp_path / "extended" / "wave42.py").write_text("x = 1" + nl, encoding="utf-8")
    assert _template_pin_problems(nl.join([w42, pin]), tmp_path)                          # DO_NOTHING_EPS required
