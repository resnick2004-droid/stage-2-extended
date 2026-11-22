"""A declared family is fixed by its sha256 in its decision row (E-003): the file on disk must still hash to it.

Q-194f (the red team's NOTE-5 of `READER_Q194e_2026-11-22`; template v3; the reader's P10): a pinned family's
`Judged-block reads:` line may name only `heldout_test` and `heldout_stress`, and only if the family is its market's
held-out declaration (`extended.reader.heldout_declaration_problems` empty) -- the reader refuses every other judged
purpose of an F- file for good, so a family pinned with one would carry a stage that can never run. F-03 is pinned and
spent (E-192: closed at stage B, its stage C never read) and is grandfathered by name, never edited.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import reader as R  # noqa: E402  (importing the reader touches no sys.path, imports no engine)

#: pinned families whose judged-block line predates Q-194e's confinement, kept by name (their files are never edited)
GRANDFATHERED_JUDGED_LINES = frozenset({"prereg/F-03_opening_timing.md"})
FAMILY_PIN = re.compile(r"`(prereg/F-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`")


def judged_line_problems(root: Path) -> dict[str, str]:
    """{pinned family path: why} for each pinned F- file (the log's pins) whose `Judged-block reads:` line names a
    purpose it may never read: any purpose but `heldout_test` and `heldout_stress`, or those two in a file that is not
    its market's held-out declaration."""
    log = (root / "DECISIONS.md").read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for rel in sorted({rel for rel, _ in FAMILY_PIN.findall(log)}):
        purposes = R.declared_purposes((root / rel).read_text(encoding="utf-8"))
        if not purposes:
            continue
        other = sorted(purposes - set(R.HELDOUT_PURPOSES))
        m = R.HELDOUT_PATH.fullmatch(rel)
        probs = R.heldout_declaration_problems(rel, root, m["market"]) if m else ["not a held-out declaration's path"]
        if other:
            out[rel] = f"names {other}, which no family reads (families read the search years only)"
        elif probs:
            out[rel] = f"names the held-out purposes but is not its market's held-out declaration: {'; '.join(probs)}"
    return out


def test_no_pinned_family_names_a_judged_purpose_it_can_never_read():
    found = judged_line_problems(ROOT)
    assert set(found) - GRANDFATHERED_JUDGED_LINES == set(), found
    assert GRANDFATHERED_JUDGED_LINES <= set(found), "a grandfathered family that no longer needs it is removed"


def test_the_judged_line_check_flags_a_family_and_passes_the_held_out_declaration(tmp_path):
    """On a synthetic tree: an F-14-like family naming stage and held-out purposes, a misnamed held-out-marked file,
    and a held-out declaration that also names a stage purpose are flagged; the held-out declaration naming its two
    purposes, and a family with no judged-block line, are not."""
    sys.path.insert(0, str(ROOT / "tests"))
    import heldout_verdict_rows as VR
    files = {
        "prereg/F-14_search.md": "# F-14\n\n- **Judged-block reads:** `stage_C_judgement`, `heldout_test`\n",
        "prereg/F-15_joint.md": VR.heldout_text("F-15: misnamed"),
        "prereg/F-16_heldout_test_ES.md": VR.heldout_text(
            "F-16", line="- **Judged-block reads:** `heldout_test`, `stage_C_judgement`\n"),
        VR.HT_PATH: VR.HT_TEXT,
        "prereg/F-17_quiet.md": "# F-17\n\nNo judged-block reads.\n",
    }
    (tmp_path / "prereg").mkdir()
    rows = []
    for i, (rel, text) in enumerate(files.items()):
        (tmp_path / rel).write_bytes(text.encode("utf-8"))
        rows.append(f"| E-{900 + i} | 2026-11-22 | `{rel}` sha256 `{hashlib.sha256(text.encode()).hexdigest()}` | x |")
    (tmp_path / "DECISIONS.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    found = judged_line_problems(tmp_path)
    assert set(found) == {"prereg/F-14_search.md", "prereg/F-15_joint.md", "prereg/F-16_heldout_test_ES.md",
                          VR.HT_PATH}, found
    assert "another held-out-marked" in found[VR.HT_PATH], "F-15's marker, named for no market, blocks every market"
    (tmp_path / "prereg" / "F-15_joint.md").write_text("# F-15: no marker, no line\n", encoding="utf-8")
    assert set(judged_line_problems(tmp_path)) == {"prereg/F-14_search.md", "prereg/F-16_heldout_test_ES.md"}


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
