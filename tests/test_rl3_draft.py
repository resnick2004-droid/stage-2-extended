"""Q-143: T-0 of family RL3 (`prereg/DRAFT_F-RL3_resting_levels.md`, renamed `prereg/F-NN_resting_levels.md` at its
pin): the draft's form, checked on its own text and on the repository's files (no engine, no bar, no result file; fast).

What it checks:

- **under either name** -- exactly one RL3 declaration under `prereg/`, the draft's name or a pinned
  `F-<n>_resting_levels.md` (F-02's withdrawn draft, `DRAFT_F-02_resting_levels.md`, is not it);
- **read as LF text** -- its pin is the sha256 of its LF text;
- **the sections present** -- 0 to 20, 5.10 (the band declaration), 7.1 (the pre-pin power gate) and Appendix A;
- **the seed block** -- section 15's table lists the ten seeds once each, every one in use; each appears, word-bounded,
  in the declaration; no other 8-digit 2026 token is in the text (other blocks are named by role only); and no other
  tracked file, and no other working text file of this checkout (the licensed data excluded), holds a seed of the block.
  The block is built here by arithmetic, so this file holds no literal of it; a planted copy is found by both scans;
- **the counted cells** -- the counted-cells table's rows are consistent (5 rule-kinds x 3 stops x 3 latencies = 45;
  x 3 R = 135; 108 fade-signed and 27 break-signed; 108 questions; 90 paired sibling differences) and the header
  states the same counts;
- **the operator's rulings of 2026-11-18 (E-202 (2)) and the lead's on the red team's read (Q-143r)** -- nothing read
  inside 08:30-08:59 and no ticket working there (D-281 (3)); the latency table (the information at the bar stamped
  08:29, the alert at 09:00, `t_live` = 09:00 + L for L = 5, 3, 2, the void read a bar earlier); the gate dropping only
  an empty MDL (B-1); the flatten at a verified window's start (B-3); unscheduled releases from their release time
  (B-4); the value bar at C2's bound (S-4); every finding in Appendix A; the news item ANSWERED in section 19; the limit
  rule the draft cites still stated by `extended/walker.py`;
- **the judged-block purposes** -- one `Judged-block reads:` line, its four purposes as declared, none choosing;
- **the cited hashes** -- the early-close calendar's LF sha256, Q-126's plan's LF sha256 (equal to E-187's pin), the
  judged session list's count and sha256 (E-094 (2)), and the blobs of `extended/lift_bound.py` and
  `extended/p_bound.py`, each recomputed;
- **the level** -- the header's proposed k and its level 0.05 / (k (k + 1)), with k inside Q-126's calibrated range.
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
DRAFT_NAME = "DRAFT_F-RL3_resting_levels.md"
PINNED = re.compile(r"F-\d+_resting_levels\.md")
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"          # the licensed bars and atlas: never scanned
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini", ".jsonl"}

#: section 15's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 340
SEED_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
#: the repository files allowed to hold a seed of the block besides the declaration; the build adds its own here
DECLARED_USES: tuple[str, ...] = ()
PURPOSES = frozenset({"stage_C_sides", "stage_C_judgement", "stage_C_latency_beside", "stage_D_gate_floor",
                      "stage_D_scorecard"})
LATENCIES = (5, 3, 2)
RULE_KINDS, STOPS, RS = 5, 3, 3
FADE_KINDS, BREAK_KINDS = 4, 1
PROPOSED_K = 14
K_RANGE_1S = range(13, 21)                                  # Q-126's plan 2.1 and 7 item 5
CALENDAR = "config/calendar_early_closes.csv"
PLAN = "docs/calibration/Q-126_one_sample_plan_2.md"
BLOBS = ("extended/lift_bound.py", "extended/p_bound.py")


def _declaration() -> Path:
    found = [p for p in PREREG.glob("*resting_levels.md") if p.name == DRAFT_NAME or PINNED.fullmatch(p.name)]
    found = [p for p in found if p.read_bytes().startswith(b"# F-") and b"(family RL3)" in p.read_bytes()[:200]]
    assert len(found) == 1, f"exactly one RL3 declaration under prereg/, found {[p.name for p in found]}"
    return found[0]


@pytest.fixture(scope="module")
def text() -> str:
    return _declaration().read_bytes().decode("utf-8").replace("\r\n", "\n")


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


def _header(text: str) -> str:
    """The header's field table, up to the rule line that ends it."""
    return _section(text, "| field | value |", "\n---\n")


def _lf_sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_title_and_sections(text: str) -> None:
    assert "**Status: a draft, second text" in text
    assert re.match(r"# F-(XX|\d+): resting orders at pre-session levels, re-declared \(family RL3\)", text)
    for n in range(21):
        assert re.search(rf"^## {n}\. ", text, re.MULTILINE), f"section {n} missing"
    for sub in ("### 5.10 ", "### 7.1 Before the pin: the power gate", "### 7.2 Stage A", "## Appendix A. "):
        assert sub in text, sub


# ------------------------------------------------------------------------------------------------- the seeds


def test_seed_table(text: str) -> None:
    table = _section(text, "## 15. Seeds", "**The search")
    for seed in SEED_BLOCK:
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \|", table, re.MULTILINE)
        assert len(rows) == 1, f"seed {seed} must have exactly one row in section 15's table"
        assert rows[0].strip() == "in use", (seed, rows[0])
        assert re.search(rf"\b{seed}\b", text)


def test_no_other_seed_token_in_the_text(text: str) -> None:
    """Other blocks are named by role only (several T-0s forbid their block in any other declaration)."""
    tokens = {int(t) for t in re.findall(r"\b2026\d{4}\b", text)}
    assert tokens <= set(SEED_BLOCK), sorted(tokens - set(SEED_BLOCK))


def _git_hits(repo: Path) -> list[str]:
    out = subprocess.run(["git", "grep", "-IwnE", f"{_PREFIX}[0-9]"], cwd=repo, capture_output=True, text=True,
                         check=False)
    assert out.returncode in (0, 1), out.stderr
    return [line for line in out.stdout.splitlines() if line]


def _working_hits(base: Path) -> list[str]:
    pat = re.compile(rb"\b" + str(_PREFIX).encode() + rb"[0-9]\b")
    data_dir = base / "vendor" / "stage2" / "data"
    hits = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES or ".git" in p.parts:
            continue
        if data_dir == p or data_dir in p.parents:
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
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "clean.txt").write_text("nothing here\n", encoding="utf-8")
    subprocess.run(["git", "add", "clean.txt"], cwd=tmp_path, check=True, capture_output=True)
    assert not _git_hits(tmp_path) and not _working_hits(tmp_path)
    planted = tmp_path / "sub" / "planted.py"
    planted.parent.mkdir()
    planted.write_text(f"SEED = {SEED_BLOCK[7]}\n", encoding="utf-8")
    assert _working_hits(tmp_path) == ["sub/planted.py"]
    subprocess.run(["git", "add", "sub/planted.py"], cwd=tmp_path, check=True, capture_output=True)
    assert [h.split(":", 1)[0] for h in _git_hits(tmp_path)] == ["sub/planted.py"]


# ------------------------------------------------------------------------------------------------- the counts


def _counted(text: str) -> dict[str, int]:
    block = _section(text, "<!-- counted-cells -->", "<!-- end counted-cells -->")
    return {m.group(1).strip(): int(m.group(2)) for m in re.finditer(r"^\| ([^|]+?) \| (\d+) \| ", block, re.MULTILINE)}


def test_counts_consistent(text: str) -> None:
    c = _counted(text)
    assert c["rule-kinds"] == FADE_KINDS + BREAK_KINDS == RULE_KINDS
    assert c["stops"] == STOPS and c["latencies"] == len(LATENCIES) and c["R per cell"] == RS
    cells = RULE_KINDS * STOPS * len(LATENCIES)
    assert c["cells"] == cells == 45
    assert c["signed hypotheses"] == cells * RS == 135
    assert c["fade-signed hypotheses"] == FADE_KINDS * STOPS * len(LATENCIES) * RS
    assert c["break-signed hypotheses"] == BREAK_KINDS * STOPS * len(LATENCIES) * RS
    assert c["fade-signed hypotheses"] + c["break-signed hypotheses"] == c["signed hypotheses"]
    assert c["questions"] == FADE_KINDS * STOPS * len(LATENCIES) * RS     # break shares fade's (kind, stop, L, R) at rn100
    assert c["placebo cells"] == cells and c["campaign cells"] == 1
    assert c["paired sibling differences"] == (len(LATENCIES) - 1) * RULE_KINDS * STOPS * RS   # 3 v 5, 2 v 5
    head = _header(text)
    assert re.search(r"\| cells \(`k_cells`\) \|[^\n]*= \*\*45\*\*", head)
    assert re.search(r"\| hypotheses \|[^\n]*\*\*135\*\* signed hypotheses over 108 ", head)


def test_level_and_k(text: str) -> None:
    head = _header(text)
    assert f"**proposed {PROPOSED_K}**" in head and PROPOSED_K in K_RANGE_1S
    assert f"**0.05 / {PROPOSED_K * (PROPOSED_K + 1)}**" in head


# ------------------------------------------------------------------------------------------------- the operator


def test_closed_window_and_latency_table(text: str) -> None:
    """Q-143r B-2 as ruled: the information fixed (bars at or before 08:29, nothing in the window read), the alert at
    09:00, the order live at 09:00 + L, the void read at the bar before it."""
    assert "Nothing inside the closed window 08:30-08:59 is read." in text
    assert "**RL3's own tickets never enter it.**" in text and "D-281 (3)" in text
    table = _section(text, "| L (minutes) | the last bar read", "\n\n")
    for L in LATENCIES:
        label = f"{L} (the reference)" if L == 5 else f"{L}"
        row = f"| {label} | stamped 08:29 | 09:00 | 09:{L:02d} | stamped 09:{L - 1:02d} |"
        assert row in table, row
    assert len(re.findall(r"^\s*\| \d", table, re.MULTILINE)) == len(LATENCIES)
    assert "`t_pub` = 09:00 - L" not in text.split("### 6.2")[0]       # the first text's design survives only in 6.2


def test_the_rulings_on_the_red_teams_read(text: str) -> None:
    """Q-143r B-1, B-3, B-4 and S-4 as the lead ruled them."""
    body = text[:text.index("## Appendix A.")]                       # the appendix quotes what was removed
    assert "lenient by construction" not in body
    flat = re.sub(r"\s+", " ", text)                                  # phrases may wrap across lines
    assert "only when its MDL80 is empty or infinite" in flat                               # B-1: E-086's form
    assert "It never drops a cell, before the pin or after." in flat
    s3 = re.sub(r"\s+", " ", _section(text, "## 3. ", "## 4. "))       # B-3: in the contract table and in 4.6
    s4 = re.sub(r"\s+", " ", _section(text, "## 4. ", "## 5. "))
    for part, article in ((s3, "a"), (s4, "the")):
        assert f"A position open at {article} window's start is flattened at that bar" in part
        assert "Nothing walks on through a window." in part
    s47 = re.sub(r"\s+", " ", _section(text, "7. **Calendar voids", "8. **The tests**"))      # B-4: in 4.7 (d)
    assert "**is acted on only from its release time**" in s47
    assert "No cancel and no drop may use knowledge from before the release." in s47
    assert "five minutes before its release" not in re.sub(r"\s+", " ", body)
    head = _header(text)
    assert "$500 a year at **C2's bound**" in head and "at C1's bound" not in head            # S-4
    appendix = text[text.index("## Appendix A."):]
    for f in ("B-1", "B-2", "B-3", "B-4", "S-1", "S-2", "S-3", "S-4", "S-5", *(f"N-{i}" for i in range(1, 10))):
        assert re.search(rf"^\| {f} ", appendix, re.MULTILINE), f


def test_news_item_answered(text: str) -> None:
    s19 = _section(text, "## 19. ", "## 20. ")
    assert "**(a) News -- ANSWERED.**" in s19


def test_limit_rule_still_the_walkers(text: str) -> None:
    """The draft (5.2) cites the walker's limit rule; the walker must still state it."""
    walker = (ROOT / "extended" / "walker.py").read_text(encoding="utf-8")
    assert "fills only on a bar trading **through** its price by at least a tick" in walker
    assert "at the limit price, never better" in walker
    assert "trades through the level by at least one tick" in text and "at the limit price, never better" in text


# ------------------------------------------------------------------------------------------------- the rest


def test_judged_block_purposes(text: str) -> None:
    lines = reader.DECLARED_LINE.findall(text)
    assert len(lines) == 1, f"exactly one 'Judged-block reads:' line, found {len(lines)}"
    declared = reader.declared_purposes(text)
    assert declared == PURPOSES, declared
    for p in declared:
        assert not reader._choice_purpose(p), p
        assert p not in ("identity", "registered_design"), p


def test_calendar_and_plan_hashes(text: str) -> None:
    cited = re.search(rf"`{re.escape(CALENDAR)}`[^`]{{0,40}}LF sha256\s+`([0-9a-f]{{64}})`", text)
    assert cited and cited.group(1) == _lf_sha256(CALENDAR)
    plan = re.search(rf"`{re.escape(PLAN)}`[^`]{{0,40}}LF sha256\s+`([0-9a-f]{{64}})`", text)
    assert plan and plan.group(1) == _lf_sha256(PLAN)
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    e187 = re.search(r"^\| E-187 \|[^\n]*?sha256 `([0-9a-f]{64})`", decisions, re.MULTILINE)
    assert e187 and e187.group(1) == plan.group(1)


def test_judged_calendar_as_e094(text: str) -> None:
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    e094 = re.search(r"^\| E-094 \|[^\n]*?(\d+) sessions, 2024-01-02 to 2026-07-16, sha256 \(LF-joined ISO dates\) "
                     r"`([0-9a-f]{64})`", decisions, re.MULTILINE)
    assert e094
    assert f"**{e094.group(1)} sessions, sha256 (LF-joined ISO dates)\n     `{e094.group(2)}`**" in text


def test_module_blobs(text: str) -> None:
    for rel in BLOBS:
        out = subprocess.run(["git", "hash-object", rel], cwd=ROOT, capture_output=True, text=True, check=True)
        blob = out.stdout.strip()
        assert re.search(rf"`{re.escape(rel)}`[^\n]{{0,60}}`{blob}`|{blob}", text), (rel, blob)
