"""Q-137: T-0 of reading FM (`prereg/DRAFT_RD-05_firm_modes.md`, renamed `prereg/RD-05_firm_modes.md` at its pin): the
draft's form, checked on its own text and on the repository's tracked files (no engine, no bar, no result file; fast).

What it checks now (the pin adds Appendix R's keys against Q-136's record, section 5.2's corners recomputed from it,
and the covers of section 13.1 -- section 17.3's T-0 row):

- **under either name** -- exactly one firm-modes declaration under `prereg/`, the draft's name or the pinned one;
- **read as LF text** -- its pin is the sha256 of its LF text, so a CRLF checkout is read with its line ends normalised;
- **the seed block appears nowhere else** -- section 15's table lists the ten seeds of the block once each, six in use
  and four reserved; each appears, word-bounded, in the declaration; and no other tracked file of the repository holds
  any of them. The block is built here by arithmetic, so this file holds no literal of it;
- **the judged-block purposes** -- one `Judged-block reads:` line, its three purposes as declared, none a choosing or
  fitting purpose by the reader's own test, none `identity` or `registered_design`;
- **every cell counted, the counts consistent** -- the counted-cells table's rows add up to the totals the text states,
  and the coin rows equal Appendix M's mode-corners times the grid;
- **the sections present** -- 0 to 20 and Appendices M, R and C.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from extended import reader

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"
DRAFT_NAME = "DRAFT_RD-05_firm_modes.md"
PINNED_NAME = "RD-05_firm_modes.md"

#: section 15's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 238
SEED_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
SEEDS_IN_USE = SEED_BLOCK[:6]
PURPOSES = frozenset({"modes_scorecard", "modes_ladder_beside", "modes_gate_beside"})
GRID_CELLS = 4 * 6          # section 2.6: four ratios by six dollar risks
COSTED_STOPS = 3            # section 9.1: 50, 100 and 150 ticks


def _declaration() -> Path:
    found = [p for p in (PREREG / DRAFT_NAME, PREREG / PINNED_NAME) if p.exists()]
    assert len(found) == 1, f"exactly one firm-modes declaration under prereg/, found {[p.name for p in found]}"
    return found[0]


@pytest.fixture(scope="module")
def text() -> str:
    return _declaration().read_bytes().decode("utf-8").replace("\r\n", "\n")


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


def test_one_declaration(text: str) -> None:
    assert text.startswith("# RD-05")


def test_sections_present(text: str) -> None:
    for n in range(21):
        assert re.search(rf"^## {n}\. ", text, re.MULTILINE), f"section {n} missing"
    for app in ("## Appendix M", "## Appendix R", "## Appendix C"):
        assert app in text


def test_seed_table(text: str) -> None:
    table = _section(text, "## 15. Seeds", "**The check,")
    for seed in SEED_BLOCK:
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \|", table, re.MULTILINE)
        assert len(rows) == 1, f"seed {seed} must have exactly one row in section 15's table"
        status = rows[0].strip()
        if seed in SEEDS_IN_USE:
            assert status == "in use", (seed, status)
        else:
            assert status == "reserved, unused", (seed, status)
        assert re.search(rf"\b{seed}\b", text)


def test_seed_block_nowhere_else() -> None:
    decl = _declaration().relative_to(ROOT).as_posix()
    pattern = f"{_PREFIX}[0-9]"
    out = subprocess.run(
        ["git", "grep", "-IwnE", pattern], cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert out.returncode in (0, 1), out.stderr
    hits = [line for line in out.stdout.splitlines() if line and not line.startswith(decl + ":")]
    assert not hits, "the seed block appears outside the declaration:\n" + "\n".join(hits[:20])


def test_judged_block_purposes(text: str) -> None:
    lines = reader.DECLARED_LINE.findall(text)
    assert len(lines) == 1, f"exactly one 'Judged-block reads:' line, found {len(lines)}"
    declared = reader.declared_purposes(text)
    assert declared == PURPOSES, declared
    for p in declared:
        assert not reader._choice_purpose(p), p
        assert p not in ("identity", "registered_design"), p


def _counted(text: str) -> dict[str, int]:
    block = _section(text, "<!-- counted-cells", "<!-- end counted-cells -->")
    rows = {}
    for m in re.finditer(r"^\| ([^|]+?) \| (\d+) \| ", block, re.MULTILINE):
        rows[m.group(1).strip()] = int(m.group(2))
    return rows


def _mode_corners(text: str) -> tuple[int, int]:
    table = _section(text, "## Appendix M", "## Appendix R")
    ev = fu = 0
    for m in re.finditer(r"^\| (\d+) \| `[^`]+` (evaluation|funded) \| ", table, re.MULTILINE):
        if m.group(2) == "evaluation":
            ev += 1
        else:
            fu += 1
    return ev, fu


def test_counts_consistent(text: str) -> None:
    c = _counted(text)
    ev, fu = _mode_corners(text)
    corners = ev + fu
    assert (ev, fu) == (17, 25), (ev, fu)
    assert c["part C, gross coin"] == corners * GRID_CELLS * 2
    assert c["part C, costed coin"] == corners * GRID_CELLS * COSTED_STOPS
    coin = c["part C, gross coin"] + c["part C, costed coin"]
    replays = c["part F, references"] + c["part F, steady corners"] + c["part F, flips"]
    beside = c["beside, denial ladder"] + c["beside, placement"]
    stated = re.search(
        r"\*\*at most ([\d,]+) coin runs\*\*, \*\*(\d+) replays\*\* at 0 % on both arms \((\d+) references, (\d+) new\), "
        r"\*\*(\d+) replays beside\*\*\s+with (\d+) reference checks, and \*\*(\d+) gates\*\*", text)
    assert stated, "section 16's totals sentence"
    s = [int(g.replace(",", "")) for g in stated.groups()]
    assert s[0] == coin
    assert s[1] == replays and s[2] == c["part F, references"] and s[3] == replays - c["part F, references"]
    assert s[4] == beside
    assert s[5] == c["reference checks against Q-44"]
    assert s[6] == c["beside, gates"]
    assert c["part F, steady corners"] == 2 * 24
    assert c["part F, flips"] == 2 * 14
    assert c["beside, denial ladder"] == 3 * 13
