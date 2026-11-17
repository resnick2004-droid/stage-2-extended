"""Q-123b: T-0 of reading VD (`prereg/DRAFT_RD-04_volatility_drift.md`, renamed `prereg/RD-04_volatility_drift.md` at
its pin): the declaration says only what its grid, its names, its pin and its seed search support.

What it checks, on the file's own text, Q-121's merged code and the repository's text files (no engine, no bar, no
result file opened; fast tier):

- **under either name** -- exactly one RD-04 declaration under `prereg/`, the draft's name or the pinned one (E-095's
  pattern); every check passes on its text copied under the pinned name in a temporary tree, and two copies at once are
  refused, so the test survives the rename unchanged;
- **the pin-time form** -- the title, the `id` row naming `RD-04` and its pinned path, the
  `confirmation_tests_on_this_market` row, a status that is not a draft's;
- **the hash pin-readiness** -- the text, copied under the pinned name into a temporary tree whose `DECISIONS.md` pins
  its LF sha256, is admitted by the reader's declaration check (`extended.reader._family`) for
  `volatility_descriptive`, refused for a purpose not on its line, and refused once one byte changes;
- **the judged-block purposes** -- one `Judged-block reads:` line, its one purpose `volatility_descriptive`, not a
  choosing or fitting purpose by the reader's own test, not `identity` or `registered_design`;
- **every cell counted, the counts consistent** -- section 6.2's grid read row by row (2 references, 8 new cells), and
  the counts the header, section 6.4 and section 13.2 state recomputed from it;
- **Q-121's names and interface are Q-121's** -- the file, the columns and the functions the text names exist in
  Q-121's merged code (`extended/vol_descriptive.py`, `scripts/vol_descriptive.py`); `authorised` is a keyword-only
  parameter of the five functions 3.2 names; the module's four constants are the text's purpose, kind, declaration and
  last day (the re-read's m4);
- **the identity's cover declared under Q-111's rule**; **Appendix C present**, 39 rows numbered and filled;
- **the leak-clause test's declaration** -- section 9.3 names `tests/test_rd04_leak_clause.py`, its token, its phrase,
  its pre-read form and its ledger anchor, and that file exists and checks the same;
- **the seed block appears nowhere else** (m5, RD-03's `DECLARED_USES` form) -- section 11's table lists this
  reading's block of ten once each, three in use and seven reserved; none appears, word-bounded, in another declaration
  under `prereg/`, in the vendored snapshot (the licensed data excepted), in a review's or audit's scratch
  (`docs/reviews/`, `docs/audits/`) or in this repository's code and tests other than the files `DECLARED_USES` names
  (this test alone until the build adds its files, which T-9 holds to section 11's uses).
"""
from __future__ import annotations

import hashlib
import importlib.util
import inspect
import re
import shutil
from pathlib import Path

import pytest

from extended import identity_cover, reader
from extended import vol_descriptive as V

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"
DRAFT_NAME = "DRAFT_RD-04_volatility_drift.md"
PINNED_NAME = "RD-04_volatility_drift.md"
PINNED_REL = f"prereg/{PINNED_NAME}"
VENDOR = ROOT / "vendor"
VENDOR_DATA = VENDOR / "stage2" / "data"                        # the licensed bars and atlas: never scanned
SCRATCH_DIRS = (ROOT / "docs" / "reviews", ROOT / "docs" / "audits")
CODE_DIRS = (ROOT / "extended", ROOT / "identity", ROOT / "scripts", ROOT / "tests")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini"}
LEAK_TEST = ROOT / "tests" / "test_rd04_leak_clause.py"
Q121_SCRIPT = ROOT / "scripts" / "vol_descriptive.py"

SEED_BLOCK = tuple(range(20262310, 20262320))
#: the repository files allowed to hold a seed of the block besides the declaration: its declared uses (section 11).
#: The build adds its own files here as it writes them (the honesty series, the toy campaigns); T-9 holds them to 11.
DECLARED_USES = ("tests/test_rd04_draft.py",)

PURPOSES = {"volatility_descriptive"}
CELLS = ("k1", "yr_act", "yr_sc", "tr_act", "tr_sc")
APPENDIX_C_ROWS = 39
AUTHORISED_FUNCTIONS = ("check_span", "check_days", "describe", "summarise", "output_problems")

GRID_ROW = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$", re.MULTILINE)
SEED_ROW = re.compile(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
CHOICE_ROW = re.compile(r"^\|\s*(\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|\s*$", re.MULTILINE)


# ------------------------------------------------------------------------------------------------- the text


def declaration(prereg: Path = PREREG) -> Path:
    """The one RD-04 declaration under `prereg`: the draft before the pin, the pinned file after."""
    found = sorted(p for p in prereg.glob("*volatility_drift.md") if p.name in (DRAFT_NAME, PINNED_NAME))
    assert len(found) == 1, f"exactly one volatility-drift declaration expected under {prereg}, found {found}"
    return found[0]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def flat(text: str) -> str:
    return " ".join(text.split())


def section(body: str, heading: str) -> str:
    """The text from the heading line starting with `heading` to the next heading of the same or a higher level."""
    level = len(heading.split(" ", 1)[0])
    lines = body.split("\n")
    start = None
    for i, line in enumerate(lines):
        if start is None and line.startswith(heading):
            start = i
            continue
        if start is not None and line.startswith("#"):
            hashes = len(line) - len(line.lstrip("#"))
            if hashes <= level and line[hashes:hashes + 1] == " ":
                return "\n".join(lines[start:i])
    assert start is not None, f"no heading starting {heading!r}"
    return "\n".join(lines[start:])


# ------------------------------------------------------------------------------------------------- the checks, as
# functions of the text, so that the rename test runs every one of them on a copy under the pinned name


def check_pin_form(body: str) -> None:
    assert body.startswith("# RD-04: "), "the title is the pinned file's"
    assert "**Status: declared before anything of it is built or read.**" in body
    assert not re.search(r"^\*\*Status:[^\n]*\bDRAFT\b", body, re.MULTILINE), "a draft-form status"
    assert re.search(r"^\| id \| RD-04 \(`prereg/RD-04_volatility_drift\.md` at the pin\)", body, re.MULTILINE)
    assert re.search(r"^\| `confirmation_tests_on_this_market` \| ", body, re.MULTILINE)
    assert reader.DECLARATION_PATH.fullmatch(PINNED_REL), "the reader admits the pinned name"


def check_purposes(body: str) -> None:
    assert len(reader.DECLARED_LINE.findall(body)) == 1, "exactly one 'Judged-block reads:' line"
    purposes = set(reader.declared_purposes(body))
    assert purposes == PURPOSES, purposes
    for p in purposes:
        assert reader.PURPOSE.fullmatch(p), p
        assert not reader._choice_purpose(p), f"{p} is a choosing or fitting purpose"
    assert reader.IDENTITY not in purposes and reader.REGISTERED_DESIGN not in purposes


def grid(body: str) -> list[tuple[str, str, str, str, str]]:
    rows = [tuple(c.strip() for c in r) for r in GRID_ROW.findall(section(body, "### 6.2"))]
    assert [r[0] for r in rows] == list(CELLS), f"section 6.2's grid is not {CELLS}: {[r[0] for r in rows]}"
    return rows


def check_counts(body: str) -> None:
    rows = grid(body)
    refs = [r for r in rows if r[3].startswith("reference") and r[4].startswith("reference")]
    new_rows = [r for r in rows if r[3].startswith("new") and r[4].startswith("new")]
    assert [r[0] for r in refs] == ["k1"] and len(refs) + len(new_rows) == len(rows)
    designs = 2
    new = designs * len(new_rows)
    replays = new + designs * len(refs)
    ladder = 4 * new                                           # denial_10, denial_25, denial_50, rtp
    act_new = designs * sum(1 for r in new_rows if r[2] == "actual")
    ftp, ftp_not_run = 10 * act_new, 10 * (new - act_new)
    ref_checks = 14 * designs
    beside = ladder + ftp
    walks = designs * len({r[1] for r in new_rows})            # one rescaled walk per design and factor
    assert (new, replays, ladder, ftp, ftp_not_run, ref_checks, beside, walks) == (8, 10, 32, 40, 40, 28, 72, 4)
    head = flat(section(body, "# RD-04"))
    assert f"**{designs} references (identities) and {new} new cells, every one run**" in head
    s64 = flat(section(body, "### 6.4"))
    for s in (f"{len(refs) * designs} references (identities) + {new} new cells = **{replays} replays on two arms; "
              f"{new} new cells**", f"**{new} gates**", f"4 x {new} = **{ladder} replays**",
              f"10 x {act_new} = **{ftp} replays**", f"({ftp_not_run} replays not run",
              f"**{ref_checks} reference checks**",
              f"{replays} replays on two arms (2 references, {new} new cells); {new} gates; {beside} replays beside "
              f"({ladder} ladder and placement, {ftp} Focused Trader) and {ref_checks} reference checks; four rescaled "
              "walks"):
        assert s in s64, f"section 6.4 lacks {s!r}"
    s132 = flat(section(body, "### 13.2"))
    assert "Four rescaled walks" in s132 and "eight gates of 500 paths" in s132
    assert "seventy-two replays beside" in s132


def check_q121_names(body: str) -> None:
    """The names the text gives Q-121's file, columns and functions are Q-121's merged ones (M4)."""
    s42 = flat(section(body, "### 4.2"))
    assert "`results/q121_vol_descriptive_a1.csv`" in s42
    script = Q121_SCRIPT.read_text(encoding="utf-8")
    assert 'RESULT = "q121_vol_descriptive_a1"' in script, "Q-121's result file is not the one 4.2 names"
    for fn in ("kind_problems", "walk_problems"):
        assert f"`{fn}`" in flat(section(body, "### 3.2")) and re.search(rf"^def {fn}\(", script, re.MULTILINE), fn
    for col in ("trail20_range_pts", "walked", "date"):
        assert col in V.COLUMNS and f"`{col}`" in s42, col
    assert "`value_quantiles" in s42 and callable(V.value_quantiles)
    assert set(V.SECTIONS) == {"session", "range", "band", "band_mark"}
    s131 = flat(section(body, "### 13.1"))
    bullet = s131[s131.index("`session`, `range`, `band` --"):s131.index("`factor` -- (a2)'s own")]
    named = set(re.findall(r"`([a-z0-9_]+)`", bullet))
    known = set(V.COLUMNS) | set(V.SECTIONS) | {"block", "year", "quarter"}   # columns, sections, period kinds
    unknown = sorted(n for n in named if n not in known and not callable(getattr(V, n, None)))
    assert named and not unknown, f"13.1 names what Q-121's module does not have: {unknown}"
    assert "k_trail" not in V.COLUMNS and "k_year" not in V.COLUMNS
    s32 = flat(section(body, "### 3.2"))
    for fn in AUTHORISED_FUNCTIONS:                            # the merged interface (Q-121b, 4b72ef2; m4)
        assert f"`{fn}`" in s32, fn
        par = inspect.signature(getattr(V, fn)).parameters.get("authorised")
        assert par is not None and par.kind is inspect.Parameter.KEYWORD_ONLY and par.default is None, \
            f"{fn} does not take the keyword-only authorised=None that 3.2 declares"
    assert "**Five** functions take a keyword-only" in s32
    assert (V.AUTHORISED_PURPOSE, V.AUTHORISED_KIND, V.AUTHORISED_DECLARATION, V.AUTHORISED_LAST_DAY) == \
        ("volatility_descriptive", "described_reading", PINNED_REL, reader.JUDGED_END), \
        "Q-121's authorised constants are not the text's: re-draft before the pin (14 item 2)"
    for const in ("AUTHORISED_PURPOSE", "AUTHORISED_KIND", "AUTHORISED_DECLARATION", "AUTHORISED_LAST_DAY"):
        assert f"`{const}`" in s32, const


def check_covers(body: str) -> None:
    s81 = section(body, "### 8.1")
    para = s81[s81.index("**Its cover, declared under Q-111's rule**"):]
    para = flat(para[:para.index("\n\n")])
    assert "`extended/identity_cover.py`" in para and "`identity_cover.imports(script)`" in para
    assert "`identity/rd04_identity.py`" in para and "`BASE`" in para
    assert identity_cover.BASE == ("extended/__init__.py", "config/", "vendor/MANIFEST_stage2.sha256",
                                   "vendor/DATA_MANIFEST_stage2.sha256"), "Q-111's BASE changed: re-read 8.1"
    for entry in ("`extended/__init__.py`", "the folder `config/` whole", "`vendor/MANIFEST_stage2.sha256`",
                  "`vendor/DATA_MANIFEST_stage2.sha256`"):
        assert entry in para, f"8.1's cover does not name {entry}"


def check_appendix_c(body: str) -> None:
    rows = CHOICE_ROW.findall(section(body, "## Appendix C"))
    assert [int(r[0]) for r in rows] == list(range(1, APPENDIX_C_ROWS + 1)), \
        f"Appendix C must number {APPENDIX_C_ROWS} choices 1..{APPENDIX_C_ROWS}"
    for n, choice, where, why in rows:
        assert choice.strip() and where.strip() and why.strip(), f"choice {n} lacks its text, its place or its reason"


def _leak_module():
    spec = importlib.util.spec_from_file_location("rd04_leak_clause_under_t0", LEAK_TEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_leak_clause_declared(body: str) -> None:
    s93 = flat(section(body, "### 9.3"))
    assert "`tests/test_rd04_leak_clause.py`" in s93, "9.3 does not declare the leak-clause test"
    assert "the lead's program rule" in s93 and "every decision row that fixes a parameter" in s93
    assert LEAK_TEST.is_file(), "the leak-clause test is declared but not built"
    mod = _leak_module()
    assert mod.TOKEN in s93 and mod.TOKEN == "`RD-04 read: step 2`"
    assert f'"{mod.PHRASE}"' in s93 and mod.PHRASE == "written after RD-04 was read"
    assert mod.RD04 == PINNED_REL
    assert mod.PRE_PHRASE == "written before RD-04 was read, unchanged since" and mod.PRE_PHRASE in s93
    assert mod.LEDGER == reader.LEDGER_REL and f"`{mod.LEDGER}`" in s93 and mod.PURPOSE in PURPOSES
    assert "**in or after the step-2 row**" in s93 and "absent from `DECISIONS.md` at the read's commit" in s93
    assert "**Once the read exists, the test fails unless a step-2 row exists.**" in s93
    assert "`tests/test_rd04_leak_clause.py`" in flat(section(body, "### 12.2"))


CHECKS = (check_pin_form, check_purposes, check_counts, check_q121_names, check_covers, check_appendix_c,
          check_leak_clause_declared)


@pytest.mark.parametrize("check", CHECKS, ids=[c.__name__ for c in CHECKS])
def test_the_declaration(check):
    check(read(declaration()))


def test_every_check_holds_under_the_pinned_name_and_two_copies_are_refused(tmp_path):
    """E-095's pattern: the text found under either name; at the pin the file is renamed and nothing else changes."""
    src = declaration()
    pre = tmp_path / "prereg"
    pre.mkdir()
    shutil.copyfile(src, pre / PINNED_NAME)
    found = declaration(pre)
    assert found.name == PINNED_NAME
    for check in CHECKS:
        check(read(found))
    shutil.copyfile(src, pre / DRAFT_NAME)
    with pytest.raises(AssertionError, match="exactly one"):
        declaration(pre)


def test_the_counts_check_can_fail():
    """Not vacuous: a grid with one new cell removed is refused."""
    body = read(declaration())
    row = next(line for line in section(body, "### 6.2").split("\n") if line.startswith("| `tr_sc`"))
    with pytest.raises(AssertionError):
        check_counts(body.replace(row + "\n", ""))


# ------------------------------------------------------------------------------------------------- the pin


def _pinned_tree(tmp_path: Path, text: bytes) -> tuple[Path, str]:
    (tmp_path / "prereg").mkdir()
    (tmp_path / PINNED_REL).write_bytes(text)
    sha = hashlib.sha256(text.replace(b"\r\n", b"\n")).hexdigest()
    (tmp_path / "DECISIONS.md").write_text(
        "# Decisions\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
        f"| E-999 | 2026-11-17 | **RD-04 pinned (a test's tree):** `{PINNED_REL}` sha256 `{sha}` | T-0 |\n",
        encoding="utf-8")
    return tmp_path, sha


def test_the_text_is_pin_ready(tmp_path):
    """Pinned by its LF sha256, the text is admitted by the reader's declaration check for its one purpose, refused for
    another, and refused once a byte changes (the reader's own `_family`, without the clean run it also needs)."""
    data = declaration().read_bytes()
    tree, sha = _pinned_tree(tmp_path, data)
    assert reader.pins((tree / "DECISIONS.md").read_text(encoding="utf-8")) == {PINNED_REL: {sha}}
    ref, got = reader._family(PINNED_REL, "volatility_descriptive", tree, "T-0")
    assert (ref, got) == (PINNED_REL, sha) == (PINNED_REL, reader.sha256_lf(tree / PINNED_REL))
    with pytest.raises(reader.JudgedBlockSealed, match="does not name"):
        reader._family(PINNED_REL, "volatility_replay", tree, "T-0")
    with pytest.raises(reader.JudgedBlockSealed, match="choice or fitting"):
        reader._family(PINNED_REL, "volatility_choice", tree, "T-0")
    (tree / PINNED_REL).write_bytes(data + b" ")
    with pytest.raises(reader.JudgedBlockSealed, match="edited since its pin"):
        reader._family(PINNED_REL, "volatility_descriptive", tree, "T-0")


# ------------------------------------------------------------------------------------------------- the seeds


def _text_files(base: Path, *, skip: tuple[Path, ...] = ()) -> list[Path]:
    out = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(s == p or s in p.parents for s in skip) or ".git" in p.parts:
            continue
        out.append(p)
    return out


def _occurrences_of(seeds, files) -> dict[int, list[str]]:
    """Each seed's word-bounded occurrences, each file read once (the one-pass form of RD-01's T-0, Q-96)."""
    pats = {s: (str(s).encode(), re.compile(rb"\b" + str(s).encode() + rb"\b")) for s in seeds}
    out: dict[int, list[str]] = {s: [] for s in seeds}
    for p in files:
        data = p.read_bytes()
        for s, (digits, pat) in pats.items():
            if digits in data and pat.search(data):
                out[s].append(str(p.relative_to(ROOT)).replace("\\", "/"))
    return out


def test_section_11_lists_the_block_once_each_three_in_use_seven_reserved():
    rows = SEED_ROW.findall(section(read(declaration()), "## 11."))
    assert sorted(int(s) for s, _ in rows) == list(SEED_BLOCK), rows
    status = {int(s): st.strip().lower() for s, st in rows}
    assert [s for s in SEED_BLOCK if status[s] == "in use"] == list(SEED_BLOCK[:3])
    assert all(status[s].startswith("reserved") for s in SEED_BLOCK[3:])


def test_the_seed_block_appears_in_no_other_file():
    me = declaration()
    allowed = {ROOT / u for u in DECLARED_USES}
    files = {
        "declarations": [p for p in PREREG.glob("*.md") if p != me],
        "vendored": _text_files(VENDOR, skip=(VENDOR_DATA,)),
        "scratch": [p for d in SCRATCH_DIRS if d.is_dir() for p in _text_files(d)],
        "code and tests": [p for d in CODE_DIRS if d.is_dir() for p in _text_files(d) if p not in allowed],
    }
    found = {name: _occurrences_of(SEED_BLOCK, fs) for name, fs in files.items()}
    hits = [f"{s} in {name}: {where}" for name, by in found.items() for s, where in by.items() if where]
    assert not hits, "\n".join(hits)
    assert files["vendored"] and files["declarations"], "the scan is not vacuous"


def test_the_seed_scan_finds_a_seed_where_it_is():
    """Not vacuous: the scan finds this file's own block, the block in the declaration, and a seed of RD-01's block in
    RD-01's declaration."""
    here = Path(__file__).resolve()
    assert _occurrences_of((SEED_BLOCK[0],), [here])[SEED_BLOCK[0]]
    assert _occurrences_of(SEED_BLOCK, [declaration()])[SEED_BLOCK[-1]]
    rd01 = PREREG / "RD-01_firm_contracts.md"
    assert _occurrences_of((20261990,), [rd01])[20261990]


@pytest.mark.parametrize("const", ["AUTHORISED_PURPOSE", "AUTHORISED_DECLARATION", "AUTHORISED_KIND",
                                   "AUTHORISED_LAST_DAY"])
def test_the_interface_check_catches_a_changed_constant(monkeypatch, const):
    """Not vacuous (the re-read's m4 mutation): a module constant other than the text's fails T-0."""
    monkeypatch.setattr(V, const, "something else")
    with pytest.raises(AssertionError, match="re-draft before the pin"):
        check_q121_names(read(declaration()))


def test_the_interface_check_catches_a_lost_keyword(monkeypatch):
    def summarise(sessions, walks, sets=None):                 # a summarise without `authorised`
        return None
    monkeypatch.setattr(V, "summarise", summarise)
    with pytest.raises(AssertionError, match="keyword-only authorised"):
        check_q121_names(read(declaration()))
