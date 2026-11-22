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
