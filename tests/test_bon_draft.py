"""Q-144: T-0 of B-ON (`prereg/DRAFT_F-BON_overnight_side.md`, renamed `prereg/F-NN_overnight_side.md` at its pin): the
draft's form, checked on its own text and on the repository's files (no engine, no bar, no result file; fast).

What it checks:

- **under either name** -- exactly one B-ON declaration under `prereg/`, read as LF text;
- **the sections present** -- 0 to 25, and 0.1 carrying the operator's four rulings of 2026-11-18;
- **the seed block appears nowhere else** -- section 21 lists the ten seeds once each; no other tracked file and no
  other working text file of this checkout (the licensed data excluded) holds one, except the declared uses; the
  declaration holds no other block's seed (other families' T-0 tests refuse their own seeds in any other declaration);
  a planted seed is found by both scans. The block is built here by arithmetic, so this file holds no literal of it;
- **the judged-block purposes** -- one line, four purposes, none a choosing or fitting purpose by the reader's own test;
- **every cell counted, the counts consistent** -- the counted-cells table's product, its searched and recorded totals,
  section 20's figures and the fallback without the latency row;
- **the features** -- section 7's table is `describe_overnight()`'s lines for exactly the defined overnight features less
  the two dropped, and the design matrix's width follows;
- **the pins it cites** -- Q-126's plan sha256 as E-187 records it; F-B6's, the population's and the walker's blobs exist;
  the walker's limit order and the twins' latency argument exist as the text uses them;
- **the trailing threshold bounds a slow lean** (section 8.2), on a synthetic toy: against Q-126's band check for "below
  42" the fixed-median side fails and the trailing-median side passes; a steady trend longer than the window is caught.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import numpy as np
import pytest

from extended import features as F
from extended import reader

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"
DRAFT_NAME = "DRAFT_F-BON_overnight_side.md"
PINNED = re.compile(r"^F-\d+_overnight_side\.md$")
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini", ".jsonl"}

#: section 21's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 204
SEED_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
SEED_BUILD = SEED_BLOCK[8]
#: the files allowed to hold a seed of the block besides the declaration (section 21's uses)
DECLARED_USES: tuple[str, ...] = ("tests/test_features_overnight.py",)
PURPOSES = frozenset({"bon_stage_C_sides", "bon_stage_C_judgement", "bon_stage_C_campaign", "bon_stage_C_scorecard"})
DROPPED = ("ret_20d", "atr_rel")
Q126_SHA = "117f5eb36dfd8312b24db35d1e6898167397fe374ae47a1feab94b5a2ebfcdc6"
BLOBS = {"F-B6": "911771595ada8a3a8159c197670d12b7e37f71ff", "population": "92d2feaeb784b2ddf6b1c26511143b05a01b1091"}


def _declaration() -> Path:
    found = [p for p in PREREG.glob("*overnight_side.md") if p.name == DRAFT_NAME or PINNED.match(p.name)]
    assert len(found) == 1, f"exactly one B-ON declaration under prereg/, found {[p.name for p in found]}"
    return found[0]


@pytest.fixture(scope="module")
def text() -> str:
    return _declaration().read_bytes().decode("utf-8").replace("\r\n", "\n")


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i:text.index(end, i + len(start))]


def test_sections_and_the_rulings(text: str) -> None:
    assert text.startswith("# DRAFT F-BON") or text.startswith("# F-")
    for n in range(26):
        assert re.search(rf"^## {n}\. ", text, re.MULTILINE), f"section {n} missing"
    rulings = _section(text, "## 0.1 ", "## 1. ")
    for words in ("Overnight execution: yes", "News: no trading during news hours", "Order latency", "Limit orders",
                  "E-200 R-1", "reference cell", "counted variants", "trade through its price by one tick",
                  "cancelled at a news window's start"):
        assert words in rulings, words
    assert "Answered: accepted" in _section(text, "## 19. ", "## 20. ")


def test_k_and_level(text: str) -> None:
    assert "**Proposed k = 15**" in text and "the gatekeeper assigns k at the pin" in text
    k = 15
    assert f"**0.05 / {k * (k + 1)}**" in text
    assert "If Q-126 adopts nothing for that band, this family stays unpinned" in text


# ------------------------------------------------------------------------------------------------- the seeds

def test_seed_table(text: str) -> None:
    table = _section(text, "## 21. Seeds", "**The check.**")
    for seed in SEED_BLOCK:
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \|", table, re.MULTILINE)
        assert len(rows) == 1, f"seed {seed} must have exactly one row in section 21"
        assert rows[0].strip() in ("in use", "reserved, unused"), (seed, rows[0])


def test_no_other_blocks_seed_in_the_declaration(text: str) -> None:
    others = sorted({x for x in re.findall(r"\b2026\d{4}\b", text) if int(x) not in SEED_BLOCK})
    assert not others, others


def _git_hits(repo: Path) -> list[str]:
    from extended import git_scan  # the suite's time-limited scan (Q-156, E-217)
    out = git_scan.run(["git", "grep", "-IwnE", f"{_PREFIX}[0-9]"], cwd=repo, text=True)
    assert out.returncode in (0, 1), out.stderr
    return [line for line in out.stdout.splitlines() if line]


def _working_hits(base: Path) -> list[str]:
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
    hits = [h for h in _git_hits(ROOT) if h.split(":", 1)[0] not in _allowed()]
    assert not hits, "the seed block appears outside its declared uses:\n" + "\n".join(hits[:20])


def test_seed_block_nowhere_else_working() -> None:
    hits = [h for h in _working_hits(ROOT) if h not in _allowed()]
    assert not hits, "the seed block appears in a working file outside its declared uses:\n" + "\n".join(hits[:20])


def test_the_seed_scans_find_a_planted_seed(tmp_path: Path) -> None:
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


# ------------------------------------------------------------------------------------------------- purposes, cells

def test_judged_block_purposes(text: str) -> None:
    assert len(reader.DECLARED_LINE.findall(text)) == 1
    declared = reader.declared_purposes(text)
    assert declared == PURPOSES, declared
    for p in declared:
        assert not reader._choice_purpose(p), p
        assert p not in ("identity", "registered_design"), p


def _counted(text: str) -> dict[str, tuple[str, int]]:
    block = _section(text, "<!-- counted-cells -->", "<!-- end counted-cells -->")
    return {m.group(1).strip().strip("*"): (m.group(2).strip(), int(m.group(3)))
            for m in re.finditer(r"^\| ([^|]+?) \| ([^|]+?) \| \**(\d+)\** \|$", block, re.MULTILINE)}


def test_counts_consistent(text: str) -> None:
    c = _counted(text)
    factors = ("stop", "R", "use", "latency L", "entry")
    for f in factors:
        assert f in c, f
    assert c["latency L"][0] == "5 (reference), 3, 2 minutes" and c["latency L"][1] == 3
    assert c["entry"][0] == "market (reference), limit" and c["entry"][1] == 2
    assert c["R"][0] == "1, 1.5, 3" and c["use"][1] == 2 and c["stop"][1] == 1
    cells = int(np.prod([c[f][1] for f in factors]))
    assert c["cells"][1] == cells == 36
    lam = 7
    assert c["searched: direction lambda"][1] == lam * c["latency L"][1]
    assert c["searched: resolution lambda"][1] == lam
    searched = c["searched: direction lambda"][1] + c["searched: resolution lambda"][1]
    assert c["searched configurations"][1] == searched
    assert c["recorded in the trial count"][1] == cells + searched
    assert "seven values `0.25 x 10^(j/2)`, j = -2..4" in text
    s20 = _section(text, "## 20. ", "## 21. ")
    assert f"k_cells = 1 x 3 x 2 x 3 x 2 = {cells}" in s20
    assert f"**Searched configurations: {searched}** ({lam * 3} direction, {lam} resolution). **Recorded: " \
           f"{cells + searched}.**" in s20
    fb_cells, fb_searched = cells // 3, searched - 2 * lam
    assert f"{fb_cells} cells, {fb_searched} searched configurations, {fb_cells + fb_searched} recorded" in s20
    s10 = _section(text, "## 10. ", "## 11. ")
    assert f"the {cells - fb_cells} cells at L = 3 and L = 2 and the\n  {2 * lam} direction configurations" in s10


# ------------------------------------------------------------------------------------------------- the features

def test_feature_table_is_the_librarys(text: str) -> None:
    used = [n for n in F.NAMES if n not in F.OVERNIGHT_UNDEFINED and n not in DROPPED]
    assert len(used) == 35 and "**B-ON uses 35 features:**" in text
    block = _section(text, "<!-- bon-features:start -->", "<!-- bon-features:end -->")
    rows = [l for l in block.splitlines() if l.startswith("| `")]
    lib = {l.split("|")[1].strip().strip("`"): l for l in F.describe_overnight().splitlines()[2:]}
    assert [r.split("|")[1].strip().strip("`") for r in rows] == used
    for r in rows:
        assert r == lib[r.split("|")[1].strip().strip("`")], r
    width = len(used) - 1 + 4 + 2                        # dow as four indicators, m_cross, m_open
    assert f"**the design matrix: {width} columns**" in text
    for name in F.OVERNIGHT_UNDEFINED + DROPPED:
        assert f"`{name}`" in _section(text, "<!-- bon-features:end -->", "## 8. ")


# ------------------------------------------------------------------------------------------------- the pins cited

def test_the_pins_it_cites(text: str) -> None:
    assert Q126_SHA in text
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert re.search(rf"^\| E-187 \|[^\n]*{Q126_SHA}", decisions, re.MULTILINE)
    for name, blob in BLOBS.items():
        assert blob in text, name
        ok = subprocess.run(["git", "cat-file", "-e", blob], cwd=ROOT, capture_output=True).returncode == 0
        assert ok, f"{name}'s blob {blob} is not in the repository"


def test_the_machinery_it_names_exists() -> None:
    from extended import walker as W
    o = W.Order(W.LIMIT_ENTRY, 1, live=10, price=100.0, cutoff=15)
    assert o.cutoff == 15 and W.LIMIT_ENTRY == "limit"
    s3 = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "s3_latency.py").read_text(encoding="utf-8")
    assert re.search(r"def lagged_day_sides\([^)]*latency: int", s3, re.DOTALL)
    s1 = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "s1_sided_coin.py").read_text(encoding="utf-8")
    assert "def day_sides(" in s1
    from extended import lift_one_sample2 as L2
    assert "below 42" in L2.BANDS and callable(L2.band_check)


# ------------------------------------------------------------------------------------- the trailing threshold (8.2)

def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    o = np.argsort(values, kind="stable")
    v, w = values[o], weights[o]
    cw = np.cumsum(w)
    return float(v[int(np.searchsorted(cw, 0.5 * cw[-1]))])


def trailing_sides(z: np.ndarray, session: np.ndarray, window: int = 21) -> np.ndarray:
    """Section 8.1's side: sign(z - med_d), med_d the session-weighted median of the scores of the `window` sessions
    before d (each session weight 1, shared over its offers); sessions with fewer earlier sessions are ties (0)."""
    out = np.zeros(len(z), dtype=np.int8)
    days = np.unique(session)
    for k, d in enumerate(days):
        if k < window:
            continue
        prev = np.isin(session, days[k - window:k])
        counts = np.bincount(session[prev])
        w = 1.0 / counts[session[prev]]
        med = _weighted_median(z[prev], w)
        here = session == d
        out[here] = np.sign(z[here] - med).astype(np.int8)
    return out


def _toy(stream: int, n: int, m: int, lean: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(np.random.SeedSequence(SEED_BUILD, spawn_key=(stream, 1)))
    session = np.repeat(np.arange(n), m)
    return lean[session] + rng.normal(0.0, 1.0, n * m), session


def test_the_trailing_threshold_bounds_a_slow_lean() -> None:
    """Section 8.2's claim on a toy: a level shift in the score (a two-state lean, mean dwell 200 sessions, on 657
    judged sessions after a 21-session warm-up) holds the fixed-median side and not the trailing-median side.

    The measure: `hold` = the mean over sessions of m_d x state_d (m_d the session's mean side), outside the 21
    sessions after each switch. With 20 offers a session m_d's sd is about 1/sqrt(20) under no lean, so over the ~550
    sessions kept its mean has a standard error near 0.01: the trailing side's `hold` must be within 0.05 of zero (five
    standard errors) and the fixed side's above 0.1 (in the long state its side is long almost always, about a fifth of
    the sessions).

    **A first form of this test failed and stays on record (Q-144):** it asserted that Q-126's band check for "below 42"
    refuses the fixed-median side here. It does not: the fixed median sits in the state that holds most sessions, where
    the side is balanced and its session signs alternate freely; the lean of the other state stays inside the balance
    limit, and the band has no upper runs limit. So the check alone does not bind a one-state lean of this shape, and
    the assertion below records that; the trailing threshold is what removes it."""
    from extended import lift_one_sample2 as L2
    n_judged, warm, m = 657, 21, 20
    n = n_judged + warm
    rng = np.random.default_rng(np.random.SeedSequence(SEED_BUILD, spawn_key=(20, 0)))
    state = np.empty(n)
    state[0] = 1.0 if rng.random() < 0.5 else -1.0
    flips = rng.random(n) < 1.0 / 200.0                     # a two-state lean, mean dwell 200 sessions
    for d in range(1, n):
        state[d] = -state[d - 1] if flips[d] else state[d - 1]
    z, session = _toy(20, n, m, 1.0 * state)
    keep = session >= warm
    fixed = np.sign(z - np.median(z)).astype(np.int8)
    trail = trailing_sides(z, session)
    s = session[keep] - warm
    st = state[warm:]
    since = np.zeros(n_judged, dtype=int)                    # sessions since the last switch (large before the first)
    last = -10 ** 6
    for d in range(n):
        if d > 0 and flips[d]:
            last = d
        if d >= warm:
            since[d - warm] = d - last
    calm = since > 21

    def hold(sides: np.ndarray) -> float:
        md = np.bincount(s, weights=sides[keep].astype(float), minlength=n_judged) / np.bincount(s, minlength=n_judged)
        return float(np.mean(md[calm] * st[calm]))

    assert calm.sum() > 400 and flips[1:].any()
    assert hold(fixed) > 0.1, hold(fixed)
    assert abs(hold(trail)) < 0.05, hold(trail)
    ok_trail, why_trail, det = L2.switching_side_check(trail[keep], s, n_judged, "below 42")
    assert ok_trail, (why_trail, det)
    ok_fixed, _, _ = L2.switching_side_check(fixed[keep], s, n_judged, "below 42")
    assert ok_fixed            # recorded: the band check alone does not refuse this one-state lean (the docstring)
    # the residual the text discloses: a steady trend longer than the window leans the trailing side, and the band
    # check binds it
    z2, session2 = _toy(21, n, m, 0.2 * np.arange(n, dtype=float))
    trail2 = trailing_sides(z2, session2)
    keep2 = session2 >= warm
    ok_trend, why_trend, _ = L2.switching_side_check(trail2[keep2], session2[keep2] - warm, n_judged, "below 42")
    assert not ok_trend and "balance" in why_trend
