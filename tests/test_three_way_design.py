"""Q-153: the three-way test's design note (`docs/plans/THREE_WAY_TEST_design.md`), checked on its own text and on the
repository's files (no engine, no bar, no result file; fast).

- **the sections present** -- 1 to 7 as the brief orders them, and Appendix A;
- **the arithmetic is the script's** -- Appendix A's fenced block equals, line for line, what
  `docs/plans/scripts/three_way/three_way_arith.py`'s `report()` prints, so every figure the note states is computed,
  from declared constants and the calendar, never typed;
- **the level's arithmetic holds** -- at k = 13 an exact sign-flip needs twelve units, and the weekday bound on the
  held-out years gives fewer than twelve disjoint units at every horizon from 63 sessions;
- **the seed block** -- section 7's table lists ten consecutive seeds once each, each with a role and a status; each
  appears, word-bounded, in the note; no other tracked file and no other working text file of this checkout (the
  licensed data excluded) holds any of them. The block is built here by arithmetic, so this file holds no literal of it;
- **the scans work** -- a planted copy of a seed in a temporary repository is found by both scans.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOTE = ROOT / "docs" / "plans" / "THREE_WAY_TEST_design.md"
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"          # the licensed bars and atlas: never scanned
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini", ".jsonl"}

#: section 7's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 587
SEED_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
#: the repository files allowed to hold a seed of the block besides the note (none yet: H3's build adds its own here)
DECLARED_USES: tuple[str, ...] = ()
SECTIONS = ("## 1. ", "## 2. ", "## 3. ", "## 4. ", "## 5. ", "## 6. ", "## 7. ", "## Appendix A. ")
ARITH_START = "<!-- three_way_arith: begin -->"
ARITH_END = "<!-- three_way_arith: end -->"


@pytest.fixture(scope="module")
def text() -> str:
    return NOTE.read_bytes().decode("utf-8").replace("\r\n", "\n")


@pytest.fixture(scope="module")
def arith():
    spec = importlib.util.spec_from_file_location("three_way_arith", ARITH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sections_present(text: str) -> None:
    pos = [text.find("\n" + s) for s in SECTIONS]
    assert all(p >= 0 for p in pos), [s for s, p in zip(SECTIONS, pos) if p < 0]
    assert pos == sorted(pos), "the sections are in the brief's order"


def test_appendix_a_is_the_scripts_output(text: str, arith) -> None:
    i, j = text.index(ARITH_START), text.index(ARITH_END)
    block = text[i + len(ARITH_START):j].strip()
    assert block.startswith("```text\n") and block.endswith("\n```"), "Appendix A holds one fenced text block"
    assert block[len("```text\n"):-len("\n```")] == arith.report()


def test_the_levels_arithmetic(arith) -> None:
    a = arith.level(13)
    assert a == pytest.approx(0.05 / 182)
    assert arith.b_min(a) == 12 and 2.0 ** -12 <= a < 2.0 ** -11
    wh = arith.weekdays(*arith.HELD_OUT)
    assert all(arith.disjoint_units(wh, h) < arith.b_min(a) for h in (63, 126, 252))
    assert arith.weekdays("2024-01-01", "2024-01-07") == 5          # Monday to Sunday: five weekdays
    assert arith.complete_starts(100, 63) == 38 and arith.start_blocks(200, 63) == 2
    assert arith.binom_tail(3, 3) == 0.125 and arith.binom_tail(4, 3) == pytest.approx(5 / 16)
    assert arith.n_certify(0.05) == 59                                 # the rule of three's exact form


# ------------------------------------------------------------------------------------------------- the seed block


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


def test_seed_table(text: str) -> None:
    table = _section(text, "\n## 7. ", "\n## Appendix A. ")
    for seed in SEED_BLOCK:
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \| ([^|]+) \|", table, re.MULTILINE)
        assert len(rows) == 1, f"seed {seed} must have exactly one row in section 7's table"
        role, status = (x.strip() for x in rows[0])
        assert role and status in {"design check", "deciding", "build tests", "spare, drawn by nothing"}, (seed, status)
        assert re.search(rf"\b{seed}\b", text)
    others = re.findall(rf"\b{_PREFIX}[0-9]\b", text)
    assert set(int(x) for x in others) <= set(SEED_BLOCK)


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
    return {NOTE.relative_to(ROOT).as_posix(), *DECLARED_USES}


def test_seed_block_nowhere_else_tracked() -> None:
    allowed = _allowed()
    hits = [h for h in _git_hits(ROOT) if h.split(":", 1)[0] not in allowed]
    assert not hits, "the seed block appears outside its declared uses:\n" + "\n".join(hits[:20])


def test_seed_block_nowhere_else_working() -> None:
    allowed = _allowed()
    hits = [h for h in _working_hits(ROOT) if h not in allowed]
    assert not hits, "the seed block appears in a working file outside its declared uses:\n" + "\n".join(hits[:20])


def test_the_seed_scans_find_a_planted_seed(tmp_path: Path) -> None:
    """Positive control: a planted copy is found by both scans, and a clean tree finds none."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "clean.txt").write_text("nothing here\n", encoding="utf-8")
    subprocess.run(["git", "add", "clean.txt"], cwd=tmp_path, check=True, capture_output=True)
    assert not _git_hits(tmp_path) and not _working_hits(tmp_path)
    planted = tmp_path / "sub" / "planted.py"
    planted.parent.mkdir()
    planted.write_text(f"SEED = {SEED_BLOCK[4]}\n", encoding="utf-8")
    assert _working_hits(tmp_path) == ["sub/planted.py"]
    subprocess.run(["git", "add", "sub/planted.py"], cwd=tmp_path, check=True, capture_output=True)
    assert [h.split(":", 1)[0] for h in _git_hits(tmp_path)] == ["sub/planted.py"]
