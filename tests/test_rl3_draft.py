"""Q-143: T-0 of family RL3 (`prereg/DRAFT_F-RL3_resting_levels.md`, renamed `prereg/F-NN_resting_levels.md` at its
pin): the draft's form, checked on its own text and on the repository's files (no engine, no bar, no result file; fast).

What it checks (the third text, after the red team's two reads, Q-143r and Q-143r2):

- **under either name** -- exactly one RL3 declaration under `prereg/`, the draft's name or a pinned
  `F-<n>_resting_levels.md` (F-02's withdrawn draft, `DRAFT_F-02_resting_levels.md`, is not it);
- **read as LF text** -- its pin is the sha256 of its LF text;
- **the sections present** -- 0 to 20, 5.10 (the band declaration), 7.1 (the pre-pin power gate) and Appendix A with
  its two parts;
- **the seed block** -- section 15's table lists the ten seeds once each, every one in use; each appears, word-bounded,
  in the declaration; no other 8-digit 2026 token is in the text (other blocks are named by role only); and no other
  tracked file, and no other working text file of this checkout (the licensed data excluded), holds a seed of the block.
  The block is built here by arithmetic, so this file holds no literal of it; a planted copy is found by both scans;
- **the counted cells** -- latency-free (Q-143r2 SF-1): 5 rule-kinds x 3 stops = 15 cells; x 3 R = 45 signed
  hypotheses, 36 fade-signed and 9 break-signed, over 36 questions; the header states the same counts;
- **the timing** -- the information at the bar stamped 08:29, the alert at 08:30, the order submitted at 09:00:00 and
  live at 09:00, the void at the 08:59 close; the latency answered as having no cost;
- **the closed window** -- section 3's narrower wording (no bar read for any level, side or price; Q-143r2 SF-2);
  RL3's tickets never enter it; its basis D-281 (3);
- **the rulings** -- the gate drops only an empty MDL (Q-143r B-1); the flatten at a verified window's start (B-3);
  unscheduled releases from their release time, a position then open flattened at the first bar after the release
  minute (B-4; Q-143r2's open item 5); the value bar at C2's bound (S-4); RL3 outside E-203's F-04 limit ruling, the
  exact-twin alternative struck, the beside reading labelled "not a lift" (NB-1); T-4's same-bar check; T-13 (b) at
  RL3's timing with a heavier-print case, the stricter read (SF-4); "except `on`" (N-1); every finding in Appendix A;
  the news and latency items ANSWERED in section 19; the limit rule the draft cites still stated by `extended/walker.py`;
- **the judged-block purposes** -- one `Judged-block reads:` line, its four purposes as declared, none choosing, and
  the second text's latency purpose gone;
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
PURPOSES = frozenset({"stage_C_sides", "stage_C_judgement", "stage_D_gate_floor", "stage_D_scorecard"})
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


def _flat(s: str) -> str:
    """Whitespace runs to one space: a phrase may wrap across lines."""
    return re.sub(r"\s+", " ", s)


def _header(text: str) -> str:
    """The header's field table, up to the rule line that ends it."""
    return _section(text, "| field | value |", "\n---\n")


def _body(text: str) -> str:
    """The declaration without Appendix A, which quotes what earlier texts said."""
    return text[:text.index("## Appendix A.")]


def _lf_sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_title_and_sections(text: str) -> None:
    assert re.match(r"# F-(XX|\d+): resting orders at pre-session levels, re-declared \(family RL3\)", text)
    assert "**Status: a draft, third text" in text
    for n in range(21):
        assert re.search(rf"^## {n}\. ", text, re.MULTILINE), f"section {n} missing"
    for sub in ("### 5.10 ", "### 7.1 Before the pin: the power gate", "### 7.2 Stage A", "## Appendix A. ",
                "### A.1 The first read", "### A.2 The re-read"):
        assert sub in text, sub


# ------------------------------------------------------------------------------------------------- the seeds


def test_seed_table(text: str) -> None:
    table = _section(text, "## 15. Seeds", "**Trailing zeros.**")
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
    from extended import git_scan  # the suite's time-limited scan (Q-156, E-217)
    out = git_scan.run(["git", "grep", "-IwnE", f"{_PREFIX}[0-9]"], cwd=repo, text=True)
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
    assert c["stops"] == STOPS and c["R per cell"] == RS
    assert c["latencies"] == 1                                         # latency-free (Q-143r2 SF-1)
    cells = RULE_KINDS * STOPS
    assert c["cells"] == cells == 15
    assert c["signed hypotheses"] == cells * RS == 45
    assert c["fade-signed hypotheses"] == FADE_KINDS * STOPS * RS == 36
    assert c["break-signed hypotheses"] == BREAK_KINDS * STOPS * RS == 9
    assert c["fade-signed hypotheses"] + c["break-signed hypotheses"] == c["signed hypotheses"]
    assert c["questions"] == FADE_KINDS * STOPS * RS                    # break shares fade's (kind, stop, R) at rn100
    assert c["placebo cells"] == cells and c["campaign cells"] == 1
    assert "paired sibling differences" not in c                        # withdrawn with the latency cells
    head = _header(text)
    assert re.search(r"\| cells \(`k_cells`\) \|[^\n]*= \*\*15\*\*", head)
    assert re.search(r"\| hypotheses \|[^\n]*\*\*45\*\* signed hypotheses over 36 ", head)


def test_level_and_k(text: str) -> None:
    head = _header(text)
    assert f"**proposed {PROPOSED_K}**" in head and PROPOSED_K in K_RANGE_1S
    assert f"**0.05 / {PROPOSED_K * (PROPOSED_K + 1)}**" in head


# ------------------------------------------------------------------------------------------------- the operator


def test_timing_latency_free(text: str) -> None:
    """Q-143r2 SF-1 as ruled: one design, the information at 08:29's close, live at 09:00."""
    table = _section(text, "| the last bar read (`P_ref`'s bar) | the alert (CT) |", "\n\n")
    assert "| stamped 08:29 | 08:30 | 09:00:00 | 09:00 | the close of the bar stamped 08:59 |" in table
    assert len(re.findall(r"^\s*\| stamped", table, re.MULTILINE)) == 1
    body = _flat(_body(text))
    assert "For RL3 the answer is that the delay has no cost." in body
    assert "stage_C_latency_beside" not in text
    assert "`t_live` = 09:00 + L" not in body and "`t_pub` = 09:00 - L" not in _section(text, "## 1. ", "### 6.2")


def test_closed_window_wording(text: str) -> None:
    """Q-143r2 SF-2 as ruled: section 3's narrower wording, never the absolute one."""
    s3 = _flat(_section(text, "## 3. ", "## 4. "))
    assert "**No bar inside it is read for any level, side or price**" in s3
    assert "**RL3's own tickets never enter it.**" in s3 and "D-281 (3)" in s3
    body = _flat(_body(text))
    assert "Nothing inside the closed window 08:30-08:59 is read" not in body
    assert "It reads nothing of the opening half-hour" not in body
    assert "No level, side or price of a ticket reads the opening half-hour" in body


def test_the_rulings_on_the_red_teams_reads(text: str) -> None:
    body = _body(text)
    flat = _flat(text)
    # Q-143r B-1: E-086's form, the factor a label only
    assert "lenient by construction" not in body
    assert "only when its MDL80 is empty or infinite" in flat
    assert "It never drops a cell, before the pin or after." in flat
    # Q-143r B-3: the flatten at a verified window's start, in section 3 and in 4.6
    s3 = _flat(_section(text, "## 3. ", "## 4. "))
    s4 = _flat(_section(text, "## 4. ", "## 5. "))
    for part, article in ((s3, "a"), (s4, "the")):
        assert f"A position open at {article} window's start is flattened at that bar" in part
        assert "Nothing walks on through a window." in part
    # Q-143r B-4 and Q-143r2's open item 5: from the release only, the flatten at the first bar after its minute
    s47 = _flat(_section(text, "7. **Calendar voids", "8. **The tests**"))
    assert "**is acted on only from its release time**" in s47
    assert "No cancel, no drop and no flatten may use knowledge from before the release." in s47
    assert "**A position open when it becomes known is flattened at the first bar after its release minute**" in s47
    assert "five minutes before its release" not in _flat(body)
    # Q-143r S-4
    head = _header(text)
    assert "$500 a year at **C2's bound**" in head and "at C1's bound" not in head
    # Q-143r2 N-1
    assert "**A level exactly at `P_ref` is void (counted), except `on`**" in s4


def test_e203_ruling_and_the_beside_label(text: str) -> None:
    """Q-143r2 NB-1 as ruled: RL3 outside E-203's F-04 ruling; the alternative struck; the beside reading not a lift."""
    s55 = _flat(_section(text, "### 5.5 ", "### 5.6 "))
    assert "**The lead's ruling (on Q-143r2 NB-1): RL3 falls outside E-203's F-04 limit ruling,**" in s55
    assert "the break stop's own fill at one tick of slippage" in s55
    s19 = _flat(_section(text, "## 19. ", "## 20. "))
    assert "is struck: on RL3's offers it is degenerate and cannot fail" in s19
    assert "the exact twin as C1's construction for the `fade` cells -- is struck" in s19
    s97 = _flat(_section(text, "7. **Beside, deciding nothing:**", "8. **What a `fade` pass means.**"))
    assert "**the resting fills' own mean (supply and profitability, not a lift):**" in s97
    assert "the walked mirror against E-203's exact twin" not in s97
    t4 = _flat(_section(text, "4. **Fill rules on synthetic bars**", "5. **T-13, the mirror's zero**"))
    assert "**the fade and the break stop at the same level fill on the same bar**" in t4
    assert "Those exceptions are counted and printed. Any other difference fails the test" in t4


def test_t13b_at_rl3_timing(text: str) -> None:
    """Q-143r2 SF-4 as ruled: RL3's own timing, a heavier-print case, the stricter of the two."""
    t13 = _flat(_section(text, "5. **T-13, the mirror's zero**", "6. **T-14, planted effects**"))
    assert "**(b) Spread and jumps, at RL3's own timing**" in t13
    assert f"**The heavier-print generator,** seed `[{SEED_BLOCK[9]}, 5]`" in t13
    assert "with probability 0.01 a step, the print lies 2 or 3 ticks" in t13
    assert "the void at the close of the bar stamped 08:59; live from 09:00" in t13
    assert "**read from the stricter of the two generators**" in t13


def test_section_19_items_answered(text: str) -> None:
    s19 = _section(text, "## 19. ", "## 20. ")
    assert "**(a) News -- ANSWERED.**" in s19
    assert "**(c) Latency -- ANSWERED.** RL3 is latency-free." in s19


def test_appendix_maps_every_finding(text: str) -> None:
    a1 = _section(text, "### A.1 The first read", "### A.2 The re-read")
    for f in ("B-1", "B-2", "B-3", "B-4", "S-1", "S-2", "S-3", "S-4", "S-5", *(f"N-{i}" for i in range(1, 10))):
        assert re.search(rf"^\| {f} ", a1, re.MULTILINE), f
    a2 = text[text.index("### A.2 The re-read"):]
    for f in ("NB-1", "SF-1", "SF-2", "SF-3", "SF-4", *(f"N-{i} \\(re-read\\)" for i in range(1, 7))):
        assert re.search(rf"^\| {f} ", a2, re.MULTILINE), f


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
    assert f"**{e094.group(1)} sessions, sha256 (LF-joined ISO dates) `{e094.group(2)}`**" in _flat(text)


def test_module_blobs(text: str) -> None:
    for rel in BLOBS:
        out = subprocess.run(["git", "hash-object", rel], cwd=ROOT, capture_output=True, text=True, check=True)
        blob = out.stdout.strip()
        assert re.search(rf"`{re.escape(rel)}`[^\n]{{0,60}}`{blob}`|{blob}", text), (rel, blob)
