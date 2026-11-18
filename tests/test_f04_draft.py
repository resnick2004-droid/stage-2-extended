"""Q-141 (third text): T-0 of family FP (`prereg/DRAFT_F-04_firm_protocol.md`, renamed `prereg/F-04_firm_protocol.md` at its pin):
the draft's form, checked on its own text and on the repository's files (no engine, no bar, no result file; fast).

What it checks now (the pin adds Appendix P's modes against RD-05's Appendix M and every key section 3.2 names against
the merged record -- section 17.2's T-0 row):

- **under either name** -- exactly one F-04 declaration under `prereg/`, read as LF text;
- **the sections present** -- 0 to 20 and Appendices P, A and C;
- **the seed block appears nowhere else** -- section 15's table lists the ten seeds once each, six in use and four
  reserved; no other tracked or working text file (the licensed data excluded) holds any of them but `DECLARED_USES`;
  the block is built here by arithmetic, so this file holds no literal of it; and a planted copy is found (the scans'
  positive control);
- **the judged-block purposes** -- one `Judged-block reads:` line, its three purposes, none a choosing or fitting
  purpose by the reader's own test, none `identity` or `registered_design`;
- **every cell counted, the counts consistent** -- the counted-cells rows equal the grid's factors times Appendix P's
  configurations, modes, groups and corners, and section 16's totals sentence;
- **the references cannot drift** -- RD-05's and Q-126's pins as the text cites them equal those files' LF sha256 and
  the pins in the decision log (the red team's N-5); the seven calendars' and CHARTER's LF sha256 as cited (N-4, the re-read's N-4 and N-7);
- **the level** -- the provisional level, k = 13's 0.05 / 182, stated;
- **limit entries never eligible** -- NB-1's rule stated in 1.2 and 8.2, its decomposition printed, no limit form in
  K0 or C0;
- **no typed dollar figure** -- every dollar amount in the text is one of the declared grids' (RD-05 2.6's risks, U-2's
  ends), the bar, or the plan size "$50K" -- a guard against a typed rule value.
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
DRAFT_NAME = "DRAFT_F-04_firm_protocol.md"
PINNED_NAME = "F-04_firm_protocol.md"
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"          # the licensed bars and atlas: never scanned
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini", ".jsonl"}

#: section 15's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 243
SEED_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
SEEDS_IN_USE = SEED_BLOCK[:6]
#: files allowed to hold a seed of the block besides the declaration; the build adds its own here (T-12)
DECLARED_USES: tuple[str, ...] = ()
PURPOSES = frozenset({"fp_judgement", "fp_gate_floor", "fp_scorecard_beside"})

# section 16.2's factors
STOPS_P14, STOPS_P16, RATIOS, LATENCIES_P14, LATENCIES_P16, ENTRIES, CLASSES = 6, 5, 4, 3, 1, 2, 2
SESSION_RULES, MIXES, SIZING_A_MODE = 3, 2, 6 * 2
PAIRS = SIZING_A_MODE ** 2

PINS = {
    "prereg/RD-05_firm_modes.md": "be7f90fb56af6e09c92c0277ce83c228f2e2fbeca8fc26b87d90ccf50239659c",
}
CALENDARS = ("config/calendar_early_closes.csv", "config/calendar_fomc_minutes.csv",
             "vendor/stage2/data/releases_bls_0830_2009_2025.csv", "vendor/stage2/data/releases_bls_0830_2026.csv",
             # the FOMC meeting days: atlas_a1.yaml's news.fomc files (the re-read's N-4)
             "vendor/stage2/config/im2_release_calendar.csv",
             "vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv",
             "vendor/stage2/config/sources/fomc_statements_2026q3.csv",
             # CHARTER as E-203 amended it (the re-read's N-7)
             "CHARTER.md")
LIMIT_INELIGIBLE = "every P-14 limit trade set is described only and ineligible for any T_g"
Q126_PLAN = "docs/calibration/Q-126_one_sample_plan_2.md"
ALLOWED_DOLLARS = {"25", "250", "500", "750", "1,000", "1,500", "2,000", "50K"}


def _declaration() -> Path:
    found = [p for p in (PREREG / DRAFT_NAME, PREREG / PINNED_NAME) if p.exists()]
    assert len(found) == 1, f"exactly one F-04 declaration under prereg/, found {[p.name for p in found]}"
    return found[0]


def _lf(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


@pytest.fixture(scope="module")
def text() -> str:
    return _lf(_declaration()).decode("utf-8")


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


def test_one_declaration(text: str) -> None:
    assert text.startswith("# F-04")


def test_sections_present(text: str) -> None:
    for n in range(21):
        assert re.search(rf"^## {n}\. ", text, re.MULTILINE), f"section {n} missing"
    for app in ("## Appendix P", "## Appendix A", "## Appendix C"):
        assert app in text


def test_the_level_is_stated(text: str) -> None:
    assert 13 * 14 == 182
    assert "0.05 / 182 at k = 13" in text


# ------------------------------------------------------------------------------------------------- the seeds


def test_seed_table(text: str) -> None:
    table = _section(text, "## 15. Seeds", "**Nothing else draws.**")
    for seed in SEED_BLOCK:
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \|", table, re.MULTILINE)
        assert len(rows) == 1, f"seed {seed} must have exactly one row in section 15's table"
        status = rows[0].strip()
        assert status == ("in use" if seed in SEEDS_IN_USE else "reserved, unused"), (seed, status)


def _git_hits(repo: Path) -> list[str]:
    out = subprocess.run(["git", "grep", "-IwnE", f"{_PREFIX}[0-9]"], cwd=repo, capture_output=True, text=True,
                         check=False)
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


# ------------------------------------------------------------------------------------------------- the purposes


def test_judged_block_purposes(text: str) -> None:
    lines = reader.DECLARED_LINE.findall(text)
    assert len(lines) == 1, f"exactly one 'Judged-block reads:' line, found {len(lines)}"
    declared = reader.declared_purposes(text)
    assert declared == PURPOSES, declared
    for p in declared:
        assert not reader._choice_purpose(p), p
        assert p not in ("identity", "registered_design"), p


# ------------------------------------------------------------------------------------------------- the counts


def _configurations(text: str) -> list[dict[str, str]]:
    table = _section(text, "## Appendix P", "## Appendix C")
    rows = re.findall(r"^\| (\d+) \| `([^`]+)` \| ([^|]+?) \| `([^`]+)` \| `([^`]+)` \| (run|repriced) \| (single|two) \|$",
                      table, re.MULTILINE)
    return [dict(zip(("index", "id", "group", "eval", "funded", "run", "corners"), r)) for r in rows]


def _counted(text: str) -> dict[str, int]:
    block = _section(text, "<!-- counted-cells", "<!-- end counted-cells -->")
    return {m.group(1).strip(): int(m.group(2))
            for m in re.finditer(r"^\| ([^|]+?) \| (\d+) \| ", block, re.MULTILINE)}


def test_counts_consistent(text: str) -> None:
    cfg = _configurations(text)
    assert [int(c["index"]) for c in cfg] == list(range(len(cfg)))
    n_cfg = len(cfg)
    n_run = sum(c["run"] == "run" for c in cfg)
    n_repriced = n_cfg - n_run
    groups = {c["group"] for c in cfg}
    eval_modes = {c["eval"] for c in cfg}
    funded_modes = {c["funded"] for c in cfg}
    two = sum(c["corners"] == "two" for c in cfg)
    assert (n_cfg, n_run, n_repriced, len(groups), len(eval_modes), len(funded_modes), two) == (19, 17, 2, 4, 13, 15, 15)
    assert all(c["corners"] == "single" for c in cfg if c["run"] == "repriced")

    c = _counted(text)
    eb14 = STOPS_P14 * RATIOS * LATENCIES_P14 * ENTRIES       # P-14's entries-brackets
    eb16 = STOPS_P16 * RATIOS * LATENCIES_P16 * ENTRIES       # P-16: its registered timing only (B-2)
    assert c["P-14 trade sets"] == eb14 * CLASSES
    assert c["P-16 trade sets"] == eb16 * CLASSES
    per_mode = (eb14 + eb16) * SESSION_RULES * MIXES * SIZING_A_MODE
    assert c["evaluation mode cells"] == per_mode * len(eval_modes)
    assert c["funded mode cells"] == per_mode * len(funded_modes)
    assert c["zero-lift mode cells"] == eb14 * SESSION_RULES * MIXES * SIZING_A_MODE * (len(eval_modes) + len(funded_modes))
    p14 = eb14 * SESSION_RULES * MIXES * PAIRS
    p16 = eb16 * SESSION_RULES * MIXES * PAIRS
    assert c["P-14 protocol cells"] == p14 * n_cfg
    assert c["P-16 protocol cells"] == p16 * n_cfg
    assert c["repriced protocol cells"] == (p14 + p16) * n_repriced
    assert c["zero-lift journeys"] == c["P-14 protocol cells"]
    assert c["K0 at stage B"] == c["P-14 trade sets"]
    assert c["judged lift tests"] == len(groups) and c["K0 at stage C"] == len(groups)     # the fixed sequence
    assert c["stage A, limit diagnostic rows"] == (STOPS_P14 * RATIOS * LATENCIES_P14 + STOPS_P16 * RATIOS) * CLASSES
    assert c["stage A, choice-block rung map rows"] == RATIOS * LATENCIES_P14 * ENTRIES * CLASSES
    assert c["value lines"] == len(groups) and c["gates"] == len(groups)
    assert c["beside, configuration picks"] == 2 * n_cfg
    assert c["beside, 5-minute cells"] == n_cfg                          # P-14's picks only: P-16 has no latency
    assert c["beside, lenient corners"] == 2 * two
    assert c["beside, denial ladder"] == 2 * len(groups) * 3
    assert c["beside, placement"] == 2

    stated = re.search(
        r"\*\*at most ([\d,]+) protocol cells\*\* \(([\d,]+) of P-14's and ([\d,]+) of P-16's, ([\d,]+) of them repriced\s+"
        r"by arithmetic\), \*\*(\d+) trade sets\*\*, \*\*at most (\d+) judged lift tests in a fixed sequence\*\*, \*\*at most "
        r"(\d+) value lines and (\d+)\s+gates\*\*, and \*\*at most (\d+) journeys beside\*\*", text)
    assert stated, "section 16's totals sentence"
    s = [int(g.replace(",", "")) for g in stated.groups()]
    assert s[0] == c["P-14 protocol cells"] + c["P-16 protocol cells"]
    assert s[1] == c["P-14 protocol cells"] and s[2] == c["P-16 protocol cells"]
    assert s[3] == c["repriced protocol cells"]
    assert s[4] == c["P-14 trade sets"] + c["P-16 trade sets"]
    assert s[5] == c["judged lift tests"]
    assert s[6] == c["value lines"] and s[7] == c["gates"]
    assert s[8] == sum(v for k, v in c.items() if k.startswith("beside,"))


# ------------------------------------------------------------------------------------------------- references


def test_rd05_pin_cited_is_the_pinned_text(text: str) -> None:
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    for rel, digest in PINS.items():
        assert hashlib.sha256(_lf(ROOT / rel)).hexdigest() == digest, rel
        assert f"`{rel}` sha256 `{digest}`" in decisions, f"{rel} is not pinned at {digest} in the log"
        assert digest in text, f"{rel}'s pin is not cited"


def test_q126_plan_pin_cited_is_the_logs(text: str) -> None:
    """The red team's N-5: section 11 cites the plan's path and LF sha256; both equal the file and the log's pin."""
    digest = hashlib.sha256(_lf(ROOT / Q126_PLAN)).hexdigest()
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert f"`{Q126_PLAN}` sha256 `{digest}`" in decisions
    cited = re.search(rf"`{re.escape(Q126_PLAN)}`, LF sha256\s+`([0-9a-f]{{64}})`", text)
    assert cited and cited.group(1) == digest


def test_calendars_and_charter_cited_by_their_lf_sha256(text: str) -> None:
    for rel in CALENDARS:
        digest = hashlib.sha256(_lf(ROOT / rel)).hexdigest()
        cited = re.search(rf"`{re.escape(rel)}`[^`]{{0,40}}LF\s+sha256\s+`([0-9a-f]{{64}})`", text)
        assert cited, f"{rel} is not cited with an LF sha256"
        assert cited.group(1) == digest, (rel, cited.group(1), digest)


def test_no_typed_dollar_figure(text: str) -> None:
    found = set(re.findall(r"\$(\d{1,3}(?:,\d{3})*K?)", text))
    assert found, "the scan is not vacuous"
    assert found <= ALLOWED_DOLLARS, sorted(found - ALLOWED_DOLLARS)


def test_limit_sets_are_never_eligible(text: str) -> None:
    """The lead's ruling on the re-read's NB-1: P-14's limit trade sets are described only. The rule is stated in 1.2 and
    as 8.2's gate, and no T_g, K0 or C0 line keeps a limit form. Read with whitespace collapsed (line wrapping)."""
    def flat(s: str) -> str:
        return " ".join(s.split())

    assert flat(text).count(LIMIT_INELIGIBLE) >= 2, "NB-1's rule must stand in 1.2 and 8.2"
    assert LIMIT_INELIGIBLE in flat(_section(text, "### 8.2 ", "## 9. "))
    assert "every T_g is a market set" in flat(_section(text, "### 9.7 ", "## 10. "))
    assert "for a limit set, the exact twin computable" not in flat(text)
    assert "(p - 1/2) m" in flat(_section(text, "### 8.1 ", "### 8.2 ")), "the supply term printed beside every limit set"
    assert "placebo-selection twin" in flat(_section(text, "### 1.2 ", "### 1.3 ")), "the later route named"
