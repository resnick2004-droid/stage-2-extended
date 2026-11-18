"""Q-137: T-0 of reading FM (`prereg/DRAFT_RD-05_firm_modes.md`, renamed `prereg/RD-05_firm_modes.md` at its pin): the
draft's form, checked on its own text and on the repository's files (no engine, no bar, no result file; fast).

What it checks now (the pin adds Appendix R's keys against the merged record, section 5.2's corners recomputed from it,
and the covers of section 13.1 -- section 17.3's T-0 row):

- **under either name** -- exactly one firm-modes declaration under `prereg/`, the draft's name or the pinned one;
- **read as LF text** -- its pin is the sha256 of its LF text, so a CRLF checkout is read with its line ends normalised;
- **the seed block appears nowhere else** -- section 15's table lists the ten seeds of the block once each, six in use
  and four reserved; each appears, word-bounded, in the declaration; and no other tracked file, and no other working
  text file of this checkout (the licensed data excluded), holds any of them, except the files `DECLARED_USES` names
  (the build adds its own there as it writes them, held by T-13 to section 15). The block is built here by arithmetic,
  so this file holds no literal of it;
- **the scans work** -- a planted copy of a seed in a temporary repository is found by both scans (the red team's S7);
- **the judged-block purposes** -- one `Judged-block reads:` line, its three purposes as declared, none a choosing or
  fitting purpose by the reader's own test, none `identity` or `registered_design`;
- **every cell counted, the counts consistent** -- the counted-cells rows equal Appendix M's mode-corners times the
  grid, and add up to section 16's totals;
- **the calendars** -- the two pinned calendars' LF sha256 as section 12.4 cites them, recomputed from the files (N9);
- **the sections present** -- 0 to 20 and Appendices M, R, A and C.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest

from extended import reader

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"
DRAFT_NAME = "DRAFT_RD-05_firm_modes.md"
PINNED_NAME = "RD-05_firm_modes.md"
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"          # the licensed bars and atlas: never scanned
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini", ".jsonl"}

#: section 15's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 238
SEED_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
SEEDS_IN_USE = SEED_BLOCK[:6]
#: the repository files allowed to hold a seed of the block besides the declaration (section 15's uses); the build adds
#: its own files here as it writes them, and T-13 holds them to section 15
DECLARED_USES: tuple[str, ...] = ()
PURPOSES = frozenset({"modes_scorecard", "modes_ladder_beside", "modes_gate_beside"})
GRID_CELLS = 4 * 6          # section 2.6: four ratios by six dollar risks
COSTED_STOPS = 3            # section 9.1: 50, 100 and 150 ticks
CALENDARS = ("config/calendar_early_closes.csv", "config/calendar_fomc_minutes.csv")


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
    for app in ("## Appendix M", "## Appendix R", "## Appendix A", "## Appendix C"):
        assert app in text


def test_seed_table(text: str) -> None:
    table = _section(text, "## 15. Seeds", "**How a stream pairs**")
    for seed in SEED_BLOCK:
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \|", table, re.MULTILINE)
        assert len(rows) == 1, f"seed {seed} must have exactly one row in section 15's table"
        status = rows[0].strip()
        assert status == ("in use" if seed in SEEDS_IN_USE else "reserved, unused"), (seed, status)
        assert re.search(rf"\b{seed}\b", text)


# ------------------------------------------------------------------------------------------------- the seed scans


def _git_hits(repo: Path) -> list[str]:
    """Tracked files holding a seed of the block, word-bounded (`git grep`), as 'path:line' strings."""
    out = subprocess.run(["git", "grep", "-IwnE", f"{_PREFIX}[0-9]"], cwd=repo, capture_output=True, text=True,
                         check=False)
    assert out.returncode in (0, 1), out.stderr
    return [line for line in out.stdout.splitlines() if line]


def _working_hits(base: Path) -> list[str]:
    """Working text files under `base` (the licensed data and `.git` excluded) holding a seed of the block."""
    pat = re.compile(rb"\b" + str(_PREFIX).encode() + rb"[0-9]\b")
    hits = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES or ".git" in p.parts:
            continue
        if VENDOR_DATA == p or VENDOR_DATA in p.parents:
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if str(_PREFIX).encode() in data and pat.search(data):
            hits.append(p.relative_to(base).as_posix())
    return hits


def _allowed() -> set[str]:
    return {_declaration().relative_to(ROOT).as_posix(), *DECLARED_USES}


def test_seed_block_nowhere_else_tracked() -> None:
    allowed = _allowed()
    hits = [h for h in _git_hits(ROOT) if h.split(":", 1)[0] not in allowed]
    assert not hits, "the seed block appears outside its declared uses:\n" + "\n".join(hits[:20])


def test_seed_block_nowhere_else_working() -> None:
    allowed = _allowed()
    hits = [h for h in _working_hits(ROOT) if h not in allowed]
    assert not hits, "the seed block appears in a working file outside its declared uses:\n" + "\n".join(hits[:20])


def test_the_seed_scans_find_a_planted_seed(tmp_path: Path) -> None:
    """Positive control (the red team's S7): a planted copy is found by both scans, and a clean tree finds none."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "clean.txt").write_text("nothing here\n", encoding="utf-8")
    subprocess.run(["git", "add", "clean.txt"], cwd=tmp_path, check=True, capture_output=True)
    assert not _git_hits(tmp_path) and not _working_hits(tmp_path)
    planted = tmp_path / "sub" / "planted.py"
    planted.parent.mkdir()
    planted.write_text(f"SEED = {SEED_BLOCK[3]}\n", encoding="utf-8")
    assert _working_hits(tmp_path) == ["sub/planted.py"]
    subprocess.run(["git", "add", "sub/planted.py"], cwd=tmp_path, check=True, capture_output=True)
    assert [h.split(":", 1)[0] for h in _git_hits(tmp_path)] == ["sub/planted.py"]


# ------------------------------------------------------------------------------------------------- the rest


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
    return {m.group(1).strip(): int(m.group(2))
            for m in re.finditer(r"^\| ([^|]+?) \| (\d+) \| ", block, re.MULTILINE)}


def _mode_corners(text: str) -> dict[str, int]:
    table = _section(text, "## Appendix M", "## Appendix R")
    out = {"evaluation": 0, "funded": 0, "shared_eval": 0, "shared_funded": 0, "close_only": 0}
    for m in re.finditer(r"^\| (\d+) \| `[^`]+` (evaluation|funded) \| [a-z]+ \| ([^\n]*)\|$", table, re.MULTILINE):
        kind, terms = m.group(2), m.group(3)
        out[kind] += 1
        if "gross shared" in terms:
            out["shared_eval" if kind == "evaluation" else "shared_funded"] += 1
        if "close-only" in terms:
            out["close_only"] += 1
    return out


def test_counts_consistent(text: str) -> None:
    c = _counted(text)
    m = _mode_corners(text)
    ev, fu = m["evaluation"], m["funded"]
    corners, shared = ev + fu, m["shared_eval"] + m["shared_funded"]
    assert (ev, fu, shared, m["close_only"]) == (20, 25, 3, 2), m
    per_corner = GRID_CELLS * 2 + GRID_CELLS * COSTED_STOPS               # gross steady and flip, costed steady
    assert c["part C, gross coin"] == (corners - shared) * GRID_CELLS * 2
    assert c["part C, costed coin"] == corners * GRID_CELLS * COSTED_STOPS
    coin = c["part C, gross coin"] + c["part C, costed coin"]
    eval_runs = ev * per_corner - m["shared_eval"] * GRID_CELLS * 2
    ceiling = eval_runs - m["close_only"] * per_corner
    ts_eval_runs = per_corner                                              # `TS-S`'s evaluation mode-corner, every cell
    assert c["statistical oracle checks"] == coin + ceiling + ts_eval_runs + 1
    replays = c["part F, references"] + c["part F, steady corners"] + c["part F, flips"]
    beside = c["beside, denial ladder"] + c["beside, placement"]
    stated = re.search(
        r"\*\*at most ([\d,]+) coin runs\*\*, \*\*(\d+) replays\*\* at 0 % on both arms \((\d+) references, (\d+) new\), "
        r"\*\*(\d+) replays\s+beside\*\* with (\d+) reference checks, \*\*(\d+) gates\*\*, and \*\*at most ([\d,]+) "
        r"statistical oracle checks\*\*", text)
    assert stated, "section 16's totals sentence"
    s = [int(g.replace(",", "")) for g in stated.groups()]
    assert s[0] == coin
    assert s[1] == replays and s[2] == c["part F, references"] and s[3] == replays - c["part F, references"]
    assert s[4] == beside
    assert s[5] == c["reference checks against Q-44"]
    assert s[6] == c["beside, gates"]
    assert s[7] == c["statistical oracle checks"]
    assert c["part F, steady corners"] == 2 * 26
    assert c["part F, flips"] == 2 * 14
    assert c["beside, denial ladder"] == 3 * 13


def test_calendars_cited_by_their_lf_sha256(text: str) -> None:
    for rel in CALENDARS:
        lf = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
        digest = hashlib.sha256(lf).hexdigest()
        cited = re.search(rf"`{re.escape(rel)}`[^`]{{0,40}}LF\s+sha256\s+`([0-9a-f]{{64}})`", text)
        assert cited, f"{rel} is not cited with an LF sha256"
        assert cited.group(1) == digest, (rel, cited.group(1), digest)
