"""O-7 (E-221): T-0 of the four search-years delta declarations, written before they are pinned.

Each draft re-declares a pinned firm reading on the search years only (E-208: NQ 2020-01-02 to 2023-12-29), so that no
reading touches the held-out years, which E-221 (O-1) keeps for one joint confirmation. A delta incorporates its parent
by path and pinned sha256 and lists every place in the parent that depends on the window. This test holds, for each:

- **the parent's pin** -- the delta's `parent` row names a file and sha256 that a decision row pins, by the same regular
  expression `tests/test_declarations_fixed.py` and the reader use, and the file still hashes to it (LF text);
- **the search is complete** -- the delta records its search terms between `<!-- search-terms -->` markers, those terms
  are exactly `TERMS` below, and every parent line matching any of them is either cited in the delta's dependency table
  (section 3, rows `| D-nn | L.. | where | "quote" | replacement |`) or listed in its "unaffected, because" list
  (section 4, bullets `- **L.., L..**: reason`); so a dependency the drafter missed fails here;
- **every citation is true** -- each row's quote is a substring of the parent's cited line(s) (whitespace collapsed,
  case folded): one line; a range `La-Lb` whose joined text holds it; or a list, each item holding it;
- **no held-out read window** -- in the delta's own text (the quotes of the parent removed) every date from 2024-01-02
  sits on a line that says it is never read (or is a program date from 2026-11-01, after the data's end); the
  `development data` row reads exactly 2020-01-02 to 2023-12-29;
- **no judged-block line** -- the reader's `DECLARED_LINE` finds no line and `declared_purposes` is empty, so no
  purpose is authorised by the delta;
- **no typed result number** -- every decimal in the delta's own text is one of the parent's, the charter's or the
  delta's own section numbers; every percentage and dollar figure is the parent's; no eight-digit seed of the program's
  `2026nnnn` form appears (a seed block is inherited by reference, never restated, so the parents' T-0 scans hold);
- **the id scheme** -- the proposed pinned name is admitted by the reader's `DECLARATION_PATH`, reads as the proposed id
  (never the parent's) through `DECLARATION_ID`, and no such file or pin exists yet;
- **the parent never ran** -- no line of the read ledger cites the parent and none of its result files exists (the
  deltas' "superseded before any run").

Light: text only, no bar, no engine.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pytest

from extended import reader

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"

#: the canonical search terms (case-insensitive Python regular expressions); each draft records exactly these
TERMS = (
    r"\b202\d\b",
    r"\blate\b",
    r"\bearly\b",
    r"judged",
    r"held.out",
    r"\bseal",
    r"whole.{0,12}window",
    r"development (?:window|data|start|reading)",
    r"\bu_select\b",
    r"program U",
    r"\bblocks?\b",
    r"choice block",
    r"search.years",
    r"out.of.sample|in-sample",
    r"sessions left|sessions remain",
    r"every start|all starts|all the block",
    r"\byears?\b",
    r"\bhistor",
    r"calendar",
)

#: draft -> (parent, proposed id, proposed pinned name, the parent's result files that must not exist)
DRAFTS = {
    "DRAFT_RD-01S_firm_contracts_search_years.md": (
        "prereg/RD-01_firm_contracts.md", "RD-06", "prereg/RD-06_firm_contracts_search_years.md",
        ("results/fc_reading.csv", "results/fc_gate.csv", "results/fc_menu.csv")),
    "DRAFT_RD-02S_payout_policy_search_years.md": (
        "prereg/RD-02_payout_policy.md", "RD-07", "prereg/RD-07_payout_policy_search_years.md",
        ("results/pp_reading.csv", "results/pp_gate.csv", "results/pp_menu.csv")),
    "DRAFT_RD-03S_contract_levers_search_years.md": (
        "prereg/RD-03_contract_levers.md", "RD-08", "prereg/RD-08_contract_levers_search_years.md",
        ("results/cl_fit.csv", "results/cl_reading.csv", "results/cl_gate.csv", "results/cl_menu.csv")),
    "DRAFT_RD-05FS_firm_modes_part_f_search_years.md": (
        "prereg/RD-05_firm_modes.md", "RD-09", "prereg/RD-09_firm_modes_part_f_search_years.md",
        ("results/modes_reading.csv", "results/modes_beside.csv", "results/modes_gate.csv")),
}
NAMES = sorted(DRAFTS)

PIN = re.compile(r"`(prereg/(?:F|RD)-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`")   # tests/test_declarations_fixed.py's
PARENT_ROW = re.compile(r"^\| parent \| `(prereg/[^`]+\.md)` sha256 `([0-9a-f]{64})` \(of its LF text\), pinned by "
                        r"(E-\d+) \|$", re.MULTILINE)
ID_ROW = re.compile(r"^\| id \| proposed \*\*`(RD-\d+)`\*\* at the pin", re.MULTILINE)
DEV_ROW = re.compile(r"^\| development data \| (.*) \|$", re.MULTILINE)
TERMS_BLOCK = re.compile(r"<!-- search-terms -->\s*```\n(.*?)\n```\s*<!-- end search-terms -->", re.DOTALL)
ROW = re.compile(r"^\| D-(\d+) \|")
ITEM = re.compile(r"^L(\d+)(?:-L(\d+))?$")
UNAFFECTED = re.compile(r"^- \*\*(L[^*]+)\*\*:", re.MULTILINE)
DATE = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")
NEVER_READ = re.compile(r"never read|not read|unread|held.out", re.IGNORECASE)
HELD_OUT_FIRST, PROGRAM_DATES_FROM = date(2024, 1, 2), date(2026, 11, 1)
DECIMAL = re.compile(r"(?<![\w.-])\d+\.\d+(?![\w.])")
PERCENT = re.compile(r"(?<![\w.])\d+(?:\.\d+)? ?%")
DOLLAR = re.compile(r"\$[\d,]+(?:\.\d+)?")
SEED = re.compile(r"\b2026\d{4}\b")
HEADING_NUMBER = re.compile(r"^#+ (?:\w+ )?(\d+(?:\.\d+)?)\.? ", re.MULTILINE)


def lf_text(path: Path) -> str:
    return path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def draft(name: str) -> str:
    return lf_text(PREREG / name)


def parent_lines(name: str) -> list[str]:
    return lf_text(ROOT / DRAFTS[name][0]).split("\n")


def search_terms(text: str) -> tuple[str, ...]:
    m = TERMS_BLOCK.search(text)
    assert m, "the draft records no search terms between its markers"
    return tuple(line for line in m.group(1).split("\n") if line.strip())


def parent_hits(lines: list[str], terms: tuple[str, ...] = TERMS) -> list[int]:
    """The 1-based numbers of the parent's lines that match any search term."""
    pat = re.compile("|".join(f"(?:{t})" for t in terms), re.IGNORECASE)
    return [i for i, line in enumerate(lines, 1) if pat.search(line)]


def items(cell: str) -> list[tuple[int, int]]:
    """'L1, L5-L7' -> [(1, 1), (5, 7)]."""
    out = []
    for part in (p.strip() for p in cell.split(",")):
        m = ITEM.fullmatch(part)
        assert m, f"not a line item: {part!r} in {cell!r}"
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        assert a <= b, cell
        out.append((a, b))
    return out


def table(text: str) -> list[dict]:
    rows = []
    for line in text.split("\n"):
        if not ROW.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        assert len(cells) == 5, f"a dependency row has {len(cells)} cells, not 5: {line[:80]}"
        rid, lines_cell, where, quote, repl = cells
        assert len(quote) >= 3 and quote[0] == quote[-1] == '"', f"{rid}: the quote is not in double quotes"
        assert repl and where, f"{rid}: an empty cell"
        rows.append({"id": rid, "items": items(lines_cell), "quote": quote[1:-1], "line": line, "quote_cell": quote})
    return rows


def unaffected(text: str) -> list[tuple[int, int]]:
    out = []
    for m in UNAFFECTED.finditer(text):
        out += items(m.group(1))
    return out


def own_text(text: str) -> str:
    """The draft without the quotes of the parent (the dependency table's quote cells) and without its search terms."""
    out = []
    for line in text.split("\n"):
        if ROW.match(line):
            cells = line.strip().strip("|").split("|")
            cells[3] = ' "" '
            line = "|" + "|".join(cells) + "|"
        out.append(line)
    t = "\n".join(out)
    return TERMS_BLOCK.sub("", t)


def norm(s: str) -> str:
    return " ".join(s.split()).casefold()


# ------------------------------------------------------------------------------------------------------------ tests


def test_the_four_drafts_exist_and_name_distinct_ids():
    assert all((PREREG / n).is_file() for n in NAMES), [n for n in NAMES if not (PREREG / n).is_file()]
    ids = [DRAFTS[n][1] for n in NAMES]
    assert len(set(ids)) == len(ids)
    for n in NAMES:
        m = ID_ROW.search(draft(n))
        assert m and m.group(1) == DRAFTS[n][1], n


@pytest.mark.parametrize("name", NAMES)
def test_the_parent_is_named_by_its_pinned_sha256(name):
    text = draft(name)
    rows = PARENT_ROW.findall(text)
    assert len(rows) == 1, f"{name}: one `parent` row, found {len(rows)}"
    path, sha, row = rows[0]
    assert path == DRAFTS[name][0], name
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert (path, sha) in PIN.findall(log), f"{name}: no decision row pins {path} at {sha}"
    pin_row = next(line for line in log.split("\n") if line.startswith(f"| {row} |"))
    assert f"`{path}` sha256 `{sha}`" in pin_row, f"{name}: {row} is not the row that pins {path}"
    assert sha256_lf(ROOT / path) == sha, f"{name}: {path} no longer hashes to its pin"


@pytest.mark.parametrize("name", NAMES)
def test_the_search_terms_are_the_tests_own(name):
    assert search_terms(draft(name)) == TERMS


@pytest.mark.parametrize("name", NAMES)
def test_every_searched_parent_line_is_cited_or_unaffected(name):
    text, lines = draft(name), parent_lines(name)
    hits = set(parent_hits(lines))
    assert hits, "the search is not vacuous"
    rows = table(text)
    assert rows, f"{name}: no dependency table"
    assert [int(ROW.match(r["line"]).group(1)) for r in rows] == list(range(1, len(rows) + 1)), "D-nn in order"
    cited = {i for r in rows for a, b in r["items"] for i in range(a, b + 1)}
    un_items = unaffected(text)
    un = {i for a, b in un_items for i in range(a, b + 1)}
    singles = {a for a, b in un_items if a == b}
    assert max(cited | un) <= len(lines), f"{name}: a cited line is past the parent's end"
    missed = sorted(hits - cited - un)
    assert not missed, f"{name}: parent lines found by the search but neither cited nor unaffected: {missed}"
    both = sorted(singles & cited)
    assert not both, f"{name}: lines both cited and listed unaffected: {both}"


@pytest.mark.parametrize("name", NAMES)
def test_every_quote_is_the_parents(name):
    lines = parent_lines(name)
    for r in table(draft(name)):
        q = norm(r["quote"])
        for a, b in r["items"]:
            held = norm(" ".join(lines[a - 1:b]))
            assert q in held, f"{name} {r['id']}: {r['quote']!r} is not in the parent's L{a}-L{b}"


@pytest.mark.parametrize("name", NAMES)
def test_no_date_of_the_held_out_years_is_a_read_window(name):
    text = draft(name)
    dev = DEV_ROW.findall(text)
    assert len(dev) == 1 and dev[0].startswith("NQ 1-minute bars, 2020-01-02 to 2023-12-29"), dev
    assert [m.group(0) for m in DATE.finditer(dev[0])] == ["2020-01-02", "2023-12-29"], dev
    bad = []
    for i, line in enumerate(own_text(text).split("\n"), 1):
        for m in DATE.finditer(line):
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if HELD_OUT_FIRST <= d < PROGRAM_DATES_FROM and not NEVER_READ.search(line):
                bad.append(f"line {i}: {m.group(0)} -- {line.strip()[:100]}")
    assert not bad, f"{name}: a held-out date outside a never-read statement:\n" + "\n".join(bad)


@pytest.mark.parametrize("name", NAMES)
def test_no_judged_block_line_and_no_purpose(name):
    text = draft(name)
    assert not list(reader.DECLARED_LINE.finditer(text)), name
    assert reader.declared_purposes(text) == frozenset(), name


@pytest.mark.parametrize("name", NAMES)
def test_no_result_number_is_typed(name):
    text = draft(name)
    own = own_text(text)
    parent = lf_text(ROOT / DRAFTS[name][0])
    charter = lf_text(ROOT / "CHARTER.md")
    sections = set(HEADING_NUMBER.findall(text))
    known = set(DECIMAL.findall(parent)) | set(DECIMAL.findall(charter)) | sections
    stray = sorted({d for d in DECIMAL.findall(own) if d not in known})
    assert not stray, f"{name}: decimals that are neither the parent's, the charter's nor a section: {stray}"
    pcts = {norm(p) for p in PERCENT.findall(parent)}
    stray = sorted({p for p in PERCENT.findall(own) if norm(p) not in pcts})
    assert not stray, f"{name}: percentages not in the parent: {stray}"
    dollars = set(DOLLAR.findall(parent))
    stray = sorted({d for d in DOLLAR.findall(own) if d not in dollars})
    assert not stray, f"{name}: dollar figures not in the parent: {stray}"
    assert not SEED.findall(text), f"{name}: a seed is restated: {SEED.findall(text)}"


@pytest.mark.parametrize("name", NAMES)
def test_the_proposed_pinned_name_reads_as_its_own_id(name):
    parent, rid, pinned, _ = DRAFTS[name]
    text = draft(name)
    assert f"`{pinned}`" in text, f"{name}: the pinned name {pinned} is not stated"
    assert reader.DECLARATION_PATH.fullmatch(pinned)
    assert reader.DECLARATION_ID.match(pinned).group(1) == rid
    assert reader.DECLARATION_ID.match(parent).group(1) != rid
    assert not (ROOT / pinned).exists(), f"{pinned} exists already"
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert not [p for p, _ in PIN.findall(log) if reader.DECLARATION_ID.match(p).group(1) == rid], f"{rid} is pinned"


def test_a_suffixed_id_would_be_read_as_its_parent():
    """0.2's reason for new numbers: the reader reads `prereg/RD-01S_...` as RD-01."""
    assert reader.DECLARATION_ID.match("prereg/RD-01S_firm_contracts_search_years.md").group(1) == "RD-01"


@pytest.mark.parametrize("name", NAMES)
def test_the_parent_never_ran(name):
    parent, _, _, files = DRAFTS[name]
    led = ROOT / reader.LEDGER_REL
    lines = [json.loads(x) for x in led.read_text(encoding="utf-8").splitlines() if x.strip()] if led.is_file() else []
    cites = [x for x in lines if parent in json.dumps(x.get("declaration") or {})]
    assert not cites, f"the read ledger cites {parent}: the parent has run, and the delta's 0.3 is false"
    present = [f for f in files if (ROOT / f).exists()]
    assert not present, f"{parent}'s result files exist: {present}"


def test_the_checks_are_not_vacuous():
    """Planted faults are caught: a missed line, a false quote, a held-out window, a judged line, a typed figure."""
    name = NAMES[0]
    text, lines = draft(name), parent_lines(name)
    rows = table(text)
    # a missed dependency: drop the first row, and its lines (unless listed elsewhere) are missed
    first = rows[0]
    rest = "\n".join(line for line in text.split("\n") if line != first["line"])
    cited = {i for r in table(rest) for a, b in r["items"] for i in range(a, b + 1)}
    un = {i for a, b in unaffected(rest) for i in range(a, b + 1)}
    assert set(parent_hits(lines)) - cited - un, "dropping a row must leave a searched line unaccounted for"
    # a false quote
    a, b = first["items"][0]
    assert norm("a phrase the parent never wrote") not in norm(" ".join(lines[a - 1:b]))
    # a held-out read window in the own text
    planted = own_text(text) + "\n- reads NQ 2024-01-02 to 2026-07-16 as its late block\n"
    found = [m for line in planted.split("\n") for m in DATE.finditer(line)
             if HELD_OUT_FIRST <= date(*map(int, m.groups())) < PROGRAM_DATES_FROM and not NEVER_READ.search(line)]
    assert found
    # a judged-block line
    assert reader.declared_purposes(text + "\n- **Judged-block reads:** `x_scorecard`\n") == {"x_scorecard"}
    # a typed figure
    parent = lf_text(ROOT / DRAFTS[name][0])
    assert "0.6180" not in set(DECIMAL.findall(parent)) and DECIMAL.findall("P rose to 0.6180") == ["0.6180"]
    assert SEED.findall("the seed " + "2026" + "1234")             # built, so no seed is written in this file
