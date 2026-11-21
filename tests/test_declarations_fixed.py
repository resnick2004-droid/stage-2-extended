"""A declared family is fixed by its sha256 in its decision row (E-003): the file on disk must still hash to it."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: a pinned declaration: a family (`F-nn`), from E-025 a described reading (`RD-nn`, E-023 (1): declared and pinned,
#: never carried), and a heavy-queue declaration (`H<n>_<name>`, H3's text on, the gatekeeper's pin condition)
PIN = re.compile(r"`(prereg/(?:(?:F|RD)-\d+|H\d+_)[^`]*\.md)` sha256 `([0-9a-f]{64})`")


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
