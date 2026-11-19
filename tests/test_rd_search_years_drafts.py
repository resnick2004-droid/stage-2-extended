"""O-7 (E-221): T-0 of the five search-years delta declarations, written before they are pinned.

Each draft re-declares a pinned reading on the search years only (E-208: NQ 2020-01-02 to 2023-12-29), so that no
reading touches the held-out years, which E-221 (O-1) keeps for one joint confirmation. A delta incorporates its parent
by path and pinned sha256 and lists every place in the parent that depends on the window. The checks are functions
returning their problems, so `test_the_checks_can_fail` plants a fault in a draft's text and calls the same functions.
For each draft:

- **the parent's pin** -- the `parent` row names a file and sha256 that a decision row pins (the regular expression of
  `tests/test_declarations_fixed.py` and the reader), and the file still hashes to it (LF text);
- **the search is complete** -- the recorded search terms (between `<!-- search-terms -->` markers) are exactly `TERMS`
  (the drafter's first set and the red team's extra terms, `wt-scout_o7/extra_terms.py`); every parent line matching
  one is cited in section 3's table (`| D-nn | L.. | where | "quote" | replacement |`) or listed in section 4's
  "unaffected, because" bullets (`- **L.., L..**: reason`), never both, so a missed line fails here. The test cannot
  judge a reason (the red team's m-7 item 6): a reviewer reads them;
- **every citation is true** -- each quote is a substring of the cited parent line(s), whitespace collapsed, case
  folded: one line; a range whose joined text holds it; or a list, each item holding it;
- **no held-out read window** -- in the draft's own text (the parent's quotes removed) every date from 2024-01-02 (to
  the program dates from 2026-11-01) stands within 80 characters of "never read", "not read" or "unread", and the line,
  with that phrase removed, says "read", "reads" or "replay" nowhere else; the `development data` row reads exactly
  2020-01-02 to 2023-12-29;
- **no judged-block line** -- the reader's `DECLARED_LINE` finds no line and `declared_purposes` is empty;
- **no typed result number** -- every number of the draft's own text (decimals, percentages, dollar figures and
  integers) is the parent's, the charter's, a section number of the draft, or a calendar year; no eight-digit seed of
  the program's `2026nnnn` form (seed blocks are inherited by reference, so the parents' T-0 scans hold);
- **the id scheme** -- the proposed pinned name passes the reader's `DECLARATION_PATH` and reads as its own id through
  `DECLARATION_ID`. **Before the pin** the file and the pin do not exist yet; the pinning commit replaces this test by
  its pin-time form (each draft's section 9 says so);
- **the parent never ran** -- no read-ledger line cites the parent and none of its result files exists. Choice-block
  and identity runs outside a clean run are not ledgered, so this cannot see them (the red team's m-7 item 5);
- **supersession in code (N-1)** -- the files under `extended/`, `scripts/` and `identity/` that name a superseded
  parent as a `DECLARATION`-style constant, or a superseded purpose as a string, are exactly the runners the build
  list changes (`KNOWN`), so no new code may take them up; once a delta is pinned, none may name them but the frozen
  module `ALLOWED_AFTER_PIN` lists.

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

#: the drafter's first terms (case-insensitive Python regular expressions)
FIRST_TERMS = (
    r"\b202\d\b", r"\blate\b", r"\bearly\b", r"judged", r"held.out", r"\bseal", r"whole.{0,12}window",
    r"development (?:window|data|start|reading)", r"\bu_select\b", r"program U", r"\bblocks?\b", r"choice block",
    r"search.years", r"out.of.sample|in-sample", r"sessions left|sessions remain", r"every start|all starts|all the block",
    r"\byears?\b", r"\bhistor", r"calendar",
)
#: the red team's extra terms (`wt-scout_o7/extra_terms.py`, in its order), added by the lead's ruling on M-2
EXTRA_TERMS = (
    r"\b20\d\d-\d\d-\d\d\b", r"\bU1\b", r"\bgate", r"\bbound|lower.bound|\blb\b|e_by_rr|lb_by_rr", r"\bshift", r"Q-44",
    r"Q-17", r"Q-121", r"RD-0[1-5]", r"results/|\.csv|\.parquet", r"\beras?\b", r"capacity|busiest",
    r"cutoff|\bmarks?\b|rung", r"registered", r"\b\d{3,4} sessions|\bsessions\b", r"start days?|\bstarts\b",
    r"\bwindow", r"q82|judged_sessions", r"volatil|regime|drift|\bATR\b|normalis", r"estimat|fitted|\bfit\b",
    r"identit", r"count of|counted on|releases?\b", r"reader|authoris|purpose", r"D-6\d\d|D-5\d\d",
    r"\blast\b|\bfinal\b|\brecent\b|to date|2026", r"\bbeside\b",
)
TERMS = FIRST_TERMS + EXTRA_TERMS

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
    "DRAFT_RD-04S_volatility_drift_search_years.md": (
        "prereg/RD-04_volatility_drift.md", "RD-10", "prereg/RD-10_volatility_drift_search_years.md",
        ("results/rd04_descriptive.csv", "results/rd04_replay.csv", "results/rd04_gate.csv")),
}
NAMES = sorted(DRAFTS)

#: N-1: what each pin supersedes -- the parent's path as a declaration constant (not RD-05's: its steps 0 to 2 keep
#: it) and the parent's judged-block purposes
SUPERSEDED = {
    "RD-06": ("prereg/RD-01_firm_contracts.md", ("firm_scorecard", "firm_ladder_beside", "firm_gate_beside")),
    "RD-07": ("prereg/RD-02_payout_policy.md", ("payout_scorecard", "payout_ladder_beside", "payout_gate_beside")),
    "RD-08": ("prereg/RD-03_contract_levers.md",
              ("levers_scorecard", "levers_gate_beside", "levers_ladder_beside", "levers_ftp_beside")),
    "RD-09": (None, ("modes_scorecard", "modes_ladder_beside", "modes_gate_beside")),
    "RD-10": ("prereg/RD-04_volatility_drift.md", ("volatility_descriptive",)),
}
#: the runners that name them today, each changed by its delta's build list (B-1) before any run
KNOWN = {
    "RD-06": {"extended/firm_reading.py", "extended/firm_terms.py", "scripts/rd01_reading.py"},
    "RD-07": {"extended/pp_run.py"},
    "RD-08": {"extended/cl_reading.py", "extended/levers_terms.py", "scripts/cl_reading.py"},
    "RD-09": {"extended/modes_steps.py"},
    "RD-10": {"extended/vol_descriptive.py"},
}
#: after the pin: Q-121's frozen module keeps its authorised mode's constants (its LF sha256 ties Q-121's file; RD-10
#: never calls that mode, and the reader's rule 4 refuses the purpose before a verdict row)
ALLOWED_AFTER_PIN = {"RD-10": {"extended/vol_descriptive.py"}}
CODE_DIRS = ("extended", "scripts", "identity")

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
NEVER = re.compile(r"never read|not read|unread", re.IGNORECASE)
READ_WORD = re.compile(r"\breads?\b|\breplay(?:s|ed)?\b", re.IGNORECASE)   # "reading", the noun, is not one
HELD_OUT_FIRST, PROGRAM_DATES_FROM = date(2024, 1, 2), date(2026, 11, 1)
NEAR = 80
DECIMAL = re.compile(r"(?<![\w.-])\d+\.\d+(?![\w.])")
PERCENT = re.compile(r"(?<![\w.])\d+(?:\.\d+)? ?%")
DOLLAR = re.compile(r"\$[\d,]+(?:\.\d+)?")
SEED = re.compile(r"\b2026\d{4}\b")
HEADING_NUMBER = re.compile(r"^#+ (?:\w+ )?(\d+(?:\.\d+)?)\.? ", re.MULTILINE)
#: what is not a number of the text: identifiers (E-221, RD-06, P-14, D-01, S-4, T-3S), line references, dates, hashes
NOT_NUMBERS = re.compile(r"\b[A-Za-z]+-\d+[A-Za-z]*\b|\bL\d+\b|\b20\d\d-\d\d-\d\d\b|\b[0-9a-f]{7,64}\b|`[^`]*`")
INTEGER = re.compile(r"(?<![\w.,$-])\d+(?![\w.%])")


def lf_text(path: Path) -> str:
    return path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def draft(name: str) -> str:
    return lf_text(PREREG / name)


def parent_text(name: str) -> str:
    return lf_text(ROOT / DRAFTS[name][0])


def parent_lines(name: str) -> list[str]:
    return parent_text(name).split("\n")


def search_terms(text: str) -> tuple[str, ...]:
    m = TERMS_BLOCK.search(text)
    return tuple(line for line in m.group(1).split("\n") if line.strip()) if m else ()


def parent_hits(lines: list[str], terms: tuple[str, ...] = TERMS) -> list[int]:
    """The 1-based numbers of the parent's lines that match any search term."""
    pat = re.compile("|".join(f"(?:{t})" for t in terms), re.IGNORECASE)
    return [i for i, line in enumerate(lines, 1) if pat.search(line)]


def items(cell: str) -> list[tuple[int, int]]:
    """'L1, L5-L7' -> [(1, 1), (5, 7)]."""
    out = []
    for part in (p.strip() for p in cell.split(",")):
        m = ITEM.fullmatch(part)
        if not m:
            raise ValueError(f"not a line item: {part!r} in {cell!r}")
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if a > b:
            raise ValueError(cell)
        out.append((a, b))
    return out


def table(text: str) -> list[dict]:
    rows = []
    for line in text.split("\n"):
        if not ROW.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            raise ValueError(f"a dependency row has {len(cells)} cells, not 5: {line[:80]}")
        rid, lines_cell, where, quote, repl = cells
        if not (len(quote) >= 3 and quote[0] == quote[-1] == '"') or not repl or not where:
            raise ValueError(f"{rid}: the quote is not in double quotes, or a cell is empty")
        rows.append({"id": rid, "items": items(lines_cell), "quote": quote[1:-1], "line": line})
    return rows


def unaffected(text: str) -> list[tuple[int, int]]:
    return [it for m in UNAFFECTED.finditer(text) for it in items(m.group(1))]


def own_text(text: str) -> str:
    """The draft without the quotes of the parent (the dependency table's quote cells) and without its search terms."""
    out = []
    for line in text.split("\n"):
        if ROW.match(line):
            cells = line.strip().strip("|").split("|")
            cells[3] = ' "" '
            line = "|" + "|".join(cells) + "|"
        out.append(line)
    return TERMS_BLOCK.sub("", "\n".join(out))


def norm(s: str) -> str:
    return " ".join(s.split()).casefold()


# ------------------------------------------------------------------------------------------------ the checks


def coverage_problems(text: str, lines: list[str]) -> list[str]:
    out = []
    if search_terms(text) != TERMS:
        out.append("the recorded search terms are not the test's")
    rows = table(text)
    if not rows:
        return out + ["no dependency table"]
    if [int(ROW.match(r["line"]).group(1)) for r in rows] != list(range(1, len(rows) + 1)):
        out.append("the D-nn rows are not numbered 1, 2, ... in order")
    cited = {i for r in rows for a, b in r["items"] for i in range(a, b + 1)}
    un_items = unaffected(text)
    un = {i for a, b in un_items for i in range(a, b + 1)}
    singles = {a for a, b in un_items if a == b}
    if max(cited | un) > len(lines):
        out.append("a cited line is past the parent's end")
    missed = sorted(set(parent_hits(lines)) - cited - un)
    if missed:
        out.append(f"searched parent lines neither cited nor unaffected: {missed}")
    both = sorted(singles & cited)
    if both:
        out.append(f"lines both cited and listed unaffected: {both}")
    return out


def quote_problems(text: str, lines: list[str]) -> list[str]:
    out = []
    for r in table(text):
        q = norm(r["quote"])
        for a, b in r["items"]:
            if q not in norm(" ".join(lines[a - 1:b])):
                out.append(f"{r['id']}: {r['quote']!r} is not in the parent's L{a}-L{b}")
    return out


def date_problems(text: str) -> list[str]:
    out = []
    dev = DEV_ROW.findall(text)
    if len(dev) != 1 or [m.group(0) for m in DATE.finditer(dev[0])] != ["2020-01-02", "2023-12-29"] \
            or not dev[0].startswith("NQ 1-minute bars, 2020-01-02 to 2023-12-29"):
        out.append(f"the development data row is not 2020-01-02 to 2023-12-29: {dev}")
    for i, line in enumerate(own_text(text).split("\n"), 1):
        for m in DATE.finditer(line):
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if not HELD_OUT_FIRST <= d < PROGRAM_DATES_FROM:
                continue
            near = line[max(0, m.start() - NEAR):m.end() + NEAR]
            if not NEVER.search(near) or READ_WORD.search(NEVER.sub("", line)):
                out.append(f"line {i}: {m.group(0)} -- {line.strip()[:110]}")
    return out


def purpose_problems(text: str) -> list[str]:
    out = [f"a judged-block line: {m.group(0)[:80]}" for m in reader.DECLARED_LINE.finditer(text)]
    if reader.declared_purposes(text):
        out.append(f"purposes declared: {sorted(reader.declared_purposes(text))}")
    return out


def number_problems(text: str, parent: str, charter: str) -> list[str]:
    own = own_text(text)
    sections = set(HEADING_NUMBER.findall(text))
    out = []
    known = set(DECIMAL.findall(parent)) | set(DECIMAL.findall(charter)) | sections
    out += [f"decimal {d}" for d in sorted({d for d in DECIMAL.findall(own) if d not in known})]
    pcts = {norm(p) for p in PERCENT.findall(parent)}
    out += [f"percentage {p}" for p in sorted({p for p in PERCENT.findall(own) if norm(p) not in pcts})]
    dollars = set(DOLLAR.findall(parent))
    out += [f"dollar figure {d}" for d in sorted({d for d in DOLLAR.findall(own) if d not in dollars})]
    p_ints = set(INTEGER.findall(NOT_NUMBERS.sub(" ", parent))) | set(INTEGER.findall(NOT_NUMBERS.sub(" ", charter)))
    ints = set(INTEGER.findall(NOT_NUMBERS.sub(" ", own)))
    allowed = p_ints | {s.split(".")[0] for s in sections} | {str(y) for y in range(2019, 2028)}
    out += [f"integer {n}" for n in sorted(ints - allowed, key=int)]
    out += [f"a seed {s}" for s in SEED.findall(text)]
    return out


def code_mentions(rid: str, root: Path = ROOT) -> set[str]:
    """Files under `extended/`, `scripts/`, `identity/` naming what `rid`'s pin supersedes (N-1)."""
    path, purposes = SUPERSEDED[rid]
    pats = [re.compile(r"""["'](%s)["']""" % "|".join(map(re.escape, purposes)))]
    if path:
        pats.append(re.compile(r"""^\s*[A-Z_]*DECLARATION[A-Z_]*\s*=\s*["']%s["']""" % re.escape(path), re.MULTILINE))
    found = set()
    for d in CODE_DIRS:
        for p in sorted((root / d).rglob("*.py")):
            t = p.read_text(encoding="utf-8", errors="replace")
            if any(x.search(t) for x in pats):
                found.add(p.relative_to(root).as_posix())
    return found


# ------------------------------------------------------------------------------------------------ the tests


def test_the_five_drafts_exist_and_name_distinct_ids():
    assert all((PREREG / n).is_file() for n in NAMES), [n for n in NAMES if not (PREREG / n).is_file()]
    ids = [DRAFTS[n][1] for n in NAMES]
    assert len(set(ids)) == len(ids)
    for n in NAMES:
        m = ID_ROW.search(draft(n))
        assert m and m.group(1) == DRAFTS[n][1], n


@pytest.mark.parametrize("name", NAMES)
def test_the_parent_is_named_by_its_pinned_sha256(name):
    rows = PARENT_ROW.findall(draft(name))
    assert len(rows) == 1, f"{name}: one `parent` row, found {len(rows)}"
    path, sha, row = rows[0]
    assert path == DRAFTS[name][0], name
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert (path, sha) in PIN.findall(log), f"{name}: no decision row pins {path} at {sha}"
    pin_row = next(line for line in log.split("\n") if line.startswith(f"| {row} |"))
    assert f"`{path}` sha256 `{sha}`" in pin_row, f"{name}: {row} is not the row that pins {path}"
    assert sha256_lf(ROOT / path) == sha, f"{name}: {path} no longer hashes to its pin"


@pytest.mark.parametrize("name", NAMES)
def test_every_searched_parent_line_is_cited_or_unaffected(name):
    assert parent_hits(parent_lines(name)), "the search is not vacuous"
    assert coverage_problems(draft(name), parent_lines(name)) == []


@pytest.mark.parametrize("name", NAMES)
def test_every_quote_is_the_parents(name):
    assert quote_problems(draft(name), parent_lines(name)) == []


@pytest.mark.parametrize("name", NAMES)
def test_no_date_of_the_held_out_years_is_a_read_window(name):
    assert date_problems(draft(name)) == []


@pytest.mark.parametrize("name", NAMES)
def test_no_judged_block_line_and_no_purpose(name):
    assert purpose_problems(draft(name)) == []


@pytest.mark.parametrize("name", NAMES)
def test_no_result_number_is_typed(name):
    assert number_problems(draft(name), parent_text(name), lf_text(ROOT / "CHARTER.md")) == []


@pytest.mark.parametrize("name", NAMES)
def test_the_proposed_pinned_name_reads_as_its_own_id_before_the_pin(name):
    """Before the pin only: the pinning commit replaces this test by its pin-time form (each draft's section 9)."""
    parent, rid, pinned, _ = DRAFTS[name]
    assert f"`{pinned}`" in draft(name), f"{name}: the pinned name {pinned} is not stated"
    assert reader.DECLARATION_PATH.fullmatch(pinned)
    assert reader.DECLARATION_ID.match(pinned).group(1) == rid != reader.DECLARATION_ID.match(parent).group(1)
    assert not (ROOT / pinned).exists(), f"{pinned} exists: the pin-time form of this test is owed"
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert not [p for p, _ in PIN.findall(log) if reader.DECLARATION_ID.match(p).group(1) == rid], f"{rid} is pinned"


def test_a_suffixed_id_would_be_read_as_its_parent():
    """0.2's reason for new numbers: the reader attributes `prereg/RD-01S_...` to RD-01 (a ledger's or manifest's id)."""
    assert reader.DECLARATION_ID.match("prereg/RD-01S_firm_contracts_search_years.md").group(1) == "RD-01"


@pytest.mark.parametrize("name", NAMES)
def test_the_parent_never_ran(name):
    parent, _, _, files = DRAFTS[name]
    led = ROOT / reader.LEDGER_REL
    lines = [json.loads(x) for x in led.read_text(encoding="utf-8").splitlines() if x.strip()] if led.is_file() else []
    assert not [x for x in lines if parent in json.dumps(x.get("declaration") or {})], f"the ledger cites {parent}"
    present = [f for f in files if (ROOT / f).exists()]
    assert not present, f"{parent}'s result files exist: {present}"


@pytest.mark.parametrize("rid", sorted(SUPERSEDED))
def test_no_new_code_takes_up_a_superseded_parent(rid):
    """N-1. Before the pin: exactly the runners the build list changes (a new one fails). After it: none but the
    frozen module allowed."""
    found = code_mentions(rid)
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pinned = [p for p, _ in PIN.findall(log) if reader.DECLARATION_ID.match(p).group(1) == rid]
    if pinned:
        assert found <= ALLOWED_AFTER_PIN.get(rid, set()), f"{rid} is pinned; code still names its parent: {found}"
    else:
        assert found == KNOWN[rid], f"{rid}: the code naming its parent is {sorted(found)}, not {sorted(KNOWN[rid])}"


def test_the_checks_can_fail():
    """Each check, called as the tests call it, catches a planted fault (the red team's m-7)."""
    name = "DRAFT_RD-01S_firm_contracts_search_years.md"
    text, lines = draft(name), parent_lines(name)
    parent, charter = parent_text(name), lf_text(ROOT / "CHARTER.md")
    first = table(text)[0]
    # a missed dependency: the first row dropped
    assert any("neither cited nor unaffected" in p for p in
               coverage_problems("\n".join(x for x in text.split("\n") if x != first["line"]), lines))
    # a false quote
    bad = first["line"].replace(f'"{first["quote"]}"', '"a phrase the parent never wrote"')
    assert quote_problems(text.replace(first["line"], bad), lines)
    # held-out read windows: plain, with "held-out" on the line, and hidden beside a never-read phrase
    for plant in ("- reads NQ 2024-01-02 to 2026-07-16 as its late block",
                  "- reads the held-out years 2024-01-02 to 2026-07-16 as its late block",
                  "- reads 2024-01-02 to 2026-07-16; the confirmation window is never read"):
        assert date_problems(text + "\n" + plant + "\n"), plant
    assert date_problems(text) == []
    # a judged-block line
    assert purpose_problems(text + "\n- **Judged-block reads:** `x_scorecard`\n")
    # typed figures: a decimal, a percentage, a dollar figure, an integer, a seed
    for plant in ("P rose to 0.6180", "a share of 61.7 %", "a cost of $4,321.50", "it passed on 4617 starts",
                  "the seed " + "2026" + "1234"):
        assert number_problems(text + "\n" + plant + "\n", parent, charter), plant
    # the terms: one dropped
    assert coverage_problems(text.replace("\n" + EXTRA_TERMS[0] + "\n", "\n"), lines)
