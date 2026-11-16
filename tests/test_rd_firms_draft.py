"""Q-54: the firms reading's declaration (`prereg/DRAFT_RD_firms.md`, renamed `prereg/RD-nn_<slug>.md` at its pin)
says only what the rules records and the seed search support.

What it checks, on the file's own text and the records (no engine, no bar, no result file):

- **every rule it leans on is cited with its record's status** -- each row of its Appendix R names a key, its source
  (`record` = this repository's `config/rules_extended.yaml`; `stage2` = Stage 2's vendored `config/rules.yaml`;
  `lucid` = the vendored Lucid ledger Stage 2 reads) and a status, and the source holds that key with that status;
- **no open term is left unread** -- every entry of the record for DayTraders, TradeDay and Lucid that is not
  `verified` (the automated-retrieval entries aside: they are not contract terms) is cited in Appendix R, and every
  cited key whose status is not `verified` is read by a rule in the file's section 5;
- **the seed block is the brief's and its seeds are unused elsewhere** -- section 12's table holds 20261990..20261999
  exactly once each; a seed in use or reserved appears in no other declaration under `prereg/`, nowhere in the
  vendored snapshot and in no review's or audit's scratch (`docs/reviews/`, `docs/audits/`); a seed retired as "found
  in use" does appear somewhere else in the tree (else its retirement is not justified);
- **its judged-block purposes can be declared** -- the file has a `Judged-block reads:` line whose purposes the
  reader (`extended/reader.py`) would parse, none a choosing or fitting purpose;
- **and, kept as a strict expected failure until the lead's fix, the reader admits a described reading's file** --
  E-025 (1) widened the hash test to `prereg/RD-` files; `extended/reader.py` still accepts only `prereg/F-` files as
  the declaration of a judged-block read, so a pinned RD- reading could not authorise the U1 replay's engine reads.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from extended import reader

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"
RECORD = ROOT / "config" / "rules_extended.yaml"
STAGE2_LEDGER = ROOT / "vendor" / "stage2" / "config" / "rules.yaml"
LUCID_LEDGER = ROOT / "vendor" / "stage2" / "vendor" / "propfirms" / "firms" / "lucid-trading" / "rules.yaml"
VENDOR = ROOT / "vendor"
#: the licensed bars and atlas (uncommitted, large, binary): never scanned
VENDOR_DATA = VENDOR / "stage2" / "data"
#: where reviews and audits keep their scratch scripts and seeds (the red team's 20261998 and 20261999 are there)
SCRATCH_DIRS = (ROOT / "docs" / "reviews", ROOT / "docs" / "audits")

SEED_BLOCK = tuple(range(20261990, 20262000))
OPEN_FIRMS = ("daytraders", "tradeday", "lucid")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini"}

APPENDIX_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(record|stage2|lucid)\s*\|\s*([a-z_]+)\s*\|", re.MULTILINE)
SEED_ROW = re.compile(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)


def draft_path() -> Path:
    found = sorted(PREREG.glob("DRAFT_RD_firms.md")) + sorted(PREREG.glob("RD-*firm*.md"))
    assert len(found) == 1, f"exactly one firms-reading declaration expected under prereg/, found {found}"
    return found[0]


def text() -> str:
    return draft_path().read_text(encoding="utf-8").replace("\r\n", "\n")


def section(body: str, heading: str) -> str:
    """The text from the heading line that starts with `heading` to the next heading of the same level."""
    level = heading.split(" ", 1)[0]
    start = None
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if start is None and line.startswith(heading):
            start = i
            continue
        if start is not None and line.startswith(level + " ") and not line.startswith(level + "#"):
            return "\n".join(lines[start:i])
    assert start is not None, f"no heading starting {heading!r}"
    return "\n".join(lines[start:])


def record_status() -> dict[str, str]:
    doc = yaml.safe_load(RECORD.read_text(encoding="utf-8"))
    return {str(e["key"]): str(e["status"]) for e in doc["rules"]}


def ledger_status(path: Path) -> dict[str, str]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {str(k): str(v.get("status")) for k, v in doc["rules"].items()}


def appendix_rows() -> list[tuple[str, str, str]]:
    rows = APPENDIX_ROW.findall(section(text(), "## Appendix R"))
    assert rows, "Appendix R cites no rule"
    return rows


def test_appendix_cites_each_rule_with_its_records_status():
    sources = {"record": record_status(), "stage2": ledger_status(STAGE2_LEDGER), "lucid": ledger_status(LUCID_LEDGER)}
    bad = []
    seen = set()
    for key, src, status in appendix_rows():
        assert (key, src) not in seen, f"{key} ({src}) is cited twice in Appendix R"
        seen.add((key, src))
        got = sources[src].get(key)
        if got != status:
            bad.append(f"{key} ({src}): the draft says {status!r}, the source holds {got!r}")
    assert not bad, "\n".join(bad)


def test_every_open_term_of_the_plans_is_cited_and_read_by_a_declared_rule():
    rec = yaml.safe_load(RECORD.read_text(encoding="utf-8"))["rules"]
    open_keys = {str(e["key"]) for e in rec
                 if e["firm"] in OPEN_FIRMS and e["status"] != "verified"
                 and not str(e["key"]).endswith(".automated_retrieval_terms")}
    cited = {key for key, src, _ in appendix_rows() if src == "record"}
    missing = sorted(open_keys - cited)
    assert not missing, f"open terms of the plans not cited in Appendix R: {missing}"
    s5 = section(text(), "## 5.")
    unread = sorted(key for key, _, status in appendix_rows() if status != "verified" and f"`{key}`" not in s5)
    assert not unread, f"cited open terms that section 5 reads by no declared rule: {unread}"


def _occurrences(seed: int, files) -> list[str]:
    pat = re.compile(rb"\b" + str(seed).encode() + rb"\b")
    return [str(p.relative_to(ROOT)) for p in files if pat.search(p.read_bytes())]


def _text_files(base: Path, *, skip: tuple[Path, ...] = ()) -> list[Path]:
    out = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(s == p or s in p.parents for s in skip) or ".git" in p.parts:
            continue
        out.append(p)
    return out


def test_seed_block_is_the_briefs_and_its_seeds_are_unused_elsewhere():
    rows = SEED_ROW.findall(section(text(), "## 12."))
    seeds = [int(s) for s, _ in rows]
    assert sorted(seeds) == list(SEED_BLOCK), f"section 12 must list 20261990..20261999 once each, got {seeds}"
    me = draft_path()
    other_decls = [p for p in PREREG.glob("*.md") if p != me]
    vendored = _text_files(VENDOR, skip=(VENDOR_DATA,))
    # where other seeds are used: Stage 2's snapshot, and the reviews' and audits' scratch scripts
    scratch = [p for d in SCRATCH_DIRS if d.is_dir() for p in _text_files(d)]
    everywhere = [p for p in _text_files(ROOT, skip=(VENDOR_DATA,)) if p != me]
    problems = []
    for s, status in rows:
        seed, status = int(s), status.strip().lower()
        if status.startswith("in use") or status.startswith("reserved"):
            hits = _occurrences(seed, other_decls) + _occurrences(seed, vendored) + _occurrences(seed, scratch)
            if hits:
                problems.append(f"{seed} ({status}) is also in {hits}")
        elif status.startswith("retired, found in use"):
            if not _occurrences(seed, everywhere):
                problems.append(f"{seed} is retired as found in use, but appears nowhere else")
        else:
            problems.append(f"{seed}: status {status!r} is not 'in use', 'reserved ...' or 'retired, found in use'")
    assert not problems, "\n".join(problems)


def test_judged_block_purposes_are_declarable_and_choose_nothing():
    body = text()
    purposes = reader.declared_purposes(body)
    assert len(reader.DECLARED_LINE.findall(body)) == 1, "exactly one 'Judged-block reads:' line"
    assert purposes, "the 'Judged-block reads:' line names no purpose"
    for p in purposes:
        assert reader.PURPOSE.fullmatch(p), p
        assert not reader._choice_purpose(p), f"{p} is a choosing or fitting purpose: it may never read the judged block"
    assert reader.IDENTITY not in purposes, "identity reads are declared by their E-row, not on this line"


@pytest.mark.xfail(strict=True, reason="E-025 (1) widened the hash test to prereg/RD- files; extended/reader.py still "
                                       "admits only prereg/F- files as a judged-block read's declaration (the lead's "
                                       "fix before this reading's pin; then remove this marker)")
def test_the_reader_admits_a_described_readings_file():
    rel = "prereg/RD-01_firm_contracts.md"
    assert reader.DECLARATION_PATH.fullmatch(rel)
    assert reader.PIN.search(f"`{rel}` sha256 `{'0' * 64}`")
