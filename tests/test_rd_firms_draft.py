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
- **and the reader admits a described reading's file** -- E-025 (1) widened the hash test to `prereg/RD-` files;
  `extended/reader.py` admits a pinned `prereg/RD-` file as a judged-block read's declaration on the rules F- files
  follow (Q-58, E-041; a strict expected failure until then), so this reading, once pinned, can authorise the U1
  replay's engine reads -- checked end to end (Q-74): this file's own text, pinned in a temporary tree, authorises
  the engine reads under each purpose of its line and is refused where an F- file would be.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from extended import reader
import heldout_verdict_rows as VR  # noqa: E402  (Q-194c: the joint held-out test, ledgered, and its verdict)

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
    found = sorted(PREREG.glob("DRAFT_RD_firms.md")) + sorted(PREREG.glob("RD-*_firm_contracts.md"))
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


def _occurrences_of(seeds, files) -> dict[int, list[str]]:
    """`_occurrences(seed, files)` for every seed at once, each file read once and the word-bounded search run only on a
    file holding the digits (Q-96: a regex scan of the ~100 MB of text once a seed took most of the seed test's time);
    the same lists, in the same order."""
    pats = {s: (str(s).encode(), re.compile(rb"\b" + str(s).encode() + rb"\b")) for s in seeds}
    out: dict[int, list[str]] = {s: [] for s in seeds}
    for p in files:
        data = p.read_bytes()
        for s, (digits, pat) in pats.items():
            if digits in data and pat.search(data):
                out[s].append(str(p.relative_to(ROOT)))
    return out


def _text_files(base: Path, *, skip: tuple[Path, ...] = ()) -> list[Path]:
    out = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(s == p or s in p.parents for s in skip) or ".git" in p.parts:
            continue
        out.append(p)
    return out


def test_the_one_pass_seed_search_is_the_per_seed_search():
    """Q-96: `_occurrences_of` finds, seed for seed and in the same order, what `_occurrences` finds."""
    files = sorted(PREREG.glob("*.md")) + [p for d in SCRATCH_DIRS if d.is_dir() for p in _text_files(d)]
    seeds = (*SEED_BLOCK, 20261117, 20261910)                          # the block, and two seeds in use elsewhere
    got = _occurrences_of(seeds, files)
    assert got == {s: _occurrences(s, files) for s in seeds}
    assert any(got[s] for s in seeds), "the comparison is not vacuous"


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
    found = {name: _occurrences_of(seeds, files) for name, files in
             (("decls", other_decls), ("vendored", vendored), ("scratch", scratch), ("everywhere", everywhere))}
    problems = []
    for s, status in rows:
        seed, status = int(s), status.strip().lower()
        if status.startswith("in use") or status.startswith("reserved"):
            hits = found["decls"][seed] + found["vendored"][seed] + found["scratch"][seed]
            if hits:
                problems.append(f"{seed} ({status}) is also in {hits}")
        elif status.startswith("retired, found in use"):
            if not found["everywhere"][seed]:
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


def test_the_reader_admits_a_described_readings_file():
    """A strict expected failure until Q-58 (E-038): the reader admits `prereg/RD-` files as F- files."""
    rel = "prereg/RD-01_firm_contracts.md"
    assert reader.DECLARATION_PATH.fullmatch(rel)
    assert reader.PIN.search(f"`{rel}` sha256 `{'0' * 64}`")


#: stand-ins for files the U1 replay's engine opens (Q-48's names), in the temporary tree only
ENGINE_FILES = ("vendor/stage2/data/bars/NQ/bars.parquet", "vendor/stage2/data/atlas/A1/walks.parquet",
                "vendor/stage2/data/atlas/A3/walks.parquet")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def test_once_pinned_this_reading_authorises_its_declared_engine_reads(tmp_path, monkeypatch):
    """T-0's last part end to end (Q-74; the admission itself was built by Q-58, E-041). This draft's own text, pinned
    as `prereg/RD-01_firm_contracts.md` by a synthetic decision row in a temporary tree, authorises the U1 replay's
    engine reads over the whole development window under each purpose of its `Judged-block reads:` line -- judged,
    ledgered inside a (simulated) clean run as a described reading with its pin's sha256 -- and is refused where a
    family's file would be: outside a clean run, by another run under the same purpose with no decision row naming
    it, and once edited after its pin; and, as a family's, never for the purpose `registered_design` (E-037). Q-158,
    Q-194c: the tree carries NQ's joint held-out test, its read ledgered, and its verdict row, which a described
    reading's judged read needs (the reader's held-out rule 4); the seed's line is left out of the counts."""
    rel = "prereg/RD-01_firm_contracts.md"
    body = text()                                                      # LF, as the pins are taken
    pin = hashlib.sha256(body.encode("utf-8")).hexdigest()
    runs = tmp_path / "runs"
    t = runs / "rd-firms-sim"
    (t / "prereg").mkdir(parents=True)
    (t / rel).write_bytes(body.encode("utf-8"))
    (t / "DECISIONS.md").write_text("# Decisions (synthetic, Q-74)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
                                    f"| E-990 | 2026-11-16 | **RD-01 declared**, `{rel}` sha256 `{pin}` | test |\n",
                                    encoding="utf-8")
    (t / ".gitignore").write_text("vendor/stage2/data/\nresults/\n", encoding="utf-8")
    for f in ENGINE_FILES:
        (t / f).parent.mkdir(parents=True, exist_ok=True)
        (t / f).write_bytes(b"a stand-in, never read as data\n")
    for args in (("init", "-q", "-b", "master"), ("config", "user.email", "t@example.invalid"),
                 ("config", "user.name", "t"), ("config", "core.autocrlf", "false"), ("add", "-A"),
                 ("commit", "-q", "-m", "the pinned reading")):
        _git(t, *args)
    # Q-194c: NQ's joint held-out test read through the reader (ledgered) and its verdict row, which a described
    # reading's judged read needs (rule 4)
    VR.settle(t, [t / ENGINE_FILES[0]])
    monkeypatch.setattr(reader, "RUNS_DIR", runs)
    monkeypatch.setenv(reader.CLEAN_RUN_ENV, t.name)
    monkeypatch.setenv(reader.RUN_ID_ENV, f"{t.name}@1")
    led = t / reader.LEDGER_REL
    kw = dict(files=[t / f for f in ENGINE_FILES], what="the U1 replay (Q-74's check)", repo=t)
    purposes = sorted(reader.declared_purposes(body))
    assert purposes
    for p in purposes:
        for declaration in (rel, "RD-01"):
            a = reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose=p, declaration=declaration, **kw)
            assert (a.judged, a.ledgered, a.kind, a.declaration, a.declaration_sha256) == \
                (True, True, "described_reading", rel, pin), (p, declaration, a)
    recs = [r for r in reader.read_ledger(led) if r["declaration"]["ref"] != VR.HT_PATH]
    assert sorted(r["purpose"] for r in recs) == sorted(purposes * 2)
    assert all(r["declaration"] == {"ref": rel, "sha256": pin, "kind": "described_reading"} for r in recs)
    assert all([f["path"] for f in r["what"]["files"]] == list(ENGINE_FILES) for r in recs)
    assert all(r["dates"]["judged_first"] == "2024-01-02" and r["dates"]["judged_last"] == "2026-07-16" for r in recs)

    one = dict(purpose=purposes[0], declaration=rel, **kw)
    monkeypatch.setenv(reader.RUN_ID_ENV, f"{t.name}@2")               # another run: once, unless a row names it
    with pytest.raises(reader.JudgedBlockReadTwice, match="once"):
        reader.authorise_engine_read("2020-01-02", "2026-07-16", **one)
    monkeypatch.setattr(reader, "_main_script", lambda: t / "scripts" / "probe.py")
    with pytest.raises(reader.JudgedBlockSealed, match="decision row"):
        reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose=reader.REGISTERED_DESIGN, declaration=rel,
                                     design="P-16", **kw)
    monkeypatch.delenv(reader.CLEAN_RUN_ENV)
    with pytest.raises(reader.JudgedBlockSealed, match="clean run"):
        reader.authorise_engine_read("2020-01-02", "2026-07-16", **one)
    monkeypatch.setenv(reader.CLEAN_RUN_ENV, t.name)
    (t / rel).write_bytes(body.encode("utf-8") + b"\nA sentence added after the pin.\n")
    _git(t, "commit", "-q", "-am", "edited after the pin")
    monkeypatch.setenv(reader.RUN_ID_ENV, f"{t.name}@3")
    with pytest.raises(reader.JudgedBlockSealed, match="edited since"):
        reader.authorise_engine_read("2020-01-02", "2026-07-16", **one)
    assert len(reader.read_ledger(led)) == 1 + len(recs), "a refused read writes no line"
