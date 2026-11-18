"""Q-116d: T-0 of reading CL (`prereg/DRAFT_RD-03_contract_levers.md`, renamed `prereg/RD-03_contract_levers.md` at its
pin): the declaration says only what its grid, its records and its seed search support.

What it checks, on the file's own text, the rules records and the repository's text files (no engine, no bar, no result
file opened as a result; fast tier, synthetic only):

- **under either name** -- exactly one contract-levers declaration under `prereg/`, the draft's name or the pinned one
  (E-095's pattern in `tests/test_place_records.py`); the same checks pass on its text copied under the pinned name in
  a temporary tree, and two copies at once are refused, so the test survives the rename unchanged;
- **the pin-time form** -- the `id` row naming `RD-03` and its pinned path, the `confirmation_tests_on_this_market` row,
  a status that is not a draft's, both pinned calendars cited by their files' own LF sha256;
- **every cell counted, the counts consistent** -- section 7.2's grid read row by row (2 references and 30 new cells,
  by lever 4 / 16 / 8 / 2 over the two bases), and the counts the header, section 13 and section 15 state recomputed
  from it: the replays, the ladder and placement replays, the Focused Trader replays (the counted reading included) and
  those not run, the reference checks, the gates;
- **Appendix C present** -- the drafter's choices, 25 rows numbered 1 to 25, each with where and why;
- **the two identities' covers declared under Q-111's rule** -- section 9.1 names both scripts, every entry of
  `extended.identity_cover.BASE` and the import closure by `identity_cover.imports(script)`;
- **the judged-block purposes** -- one `Judged-block reads:` line, its four purposes as declared, none a choosing or
  fitting purpose by the reader's own test, none `identity` or `registered_design`;
- **every rule key it cites exists, with the status it states** -- each Appendix R row against its source: this
  repository's record (Q-115's keys from the merged `config/rules_extended.yaml`, or, until Q-115 merges, from its
  commit deb45ad on `wt/wt-firms`, E-135) or Stage 2's vendored ledger; and every key section 4.2 cites is in Appendix R;
- **the seed block appears nowhere else** -- section 12 lists 20262240..20262249 once each, two in use and eight
  reserved; none appears, word-bounded, in another declaration under `prereg/`, in the vendored snapshot, in a
  review's or audit's scratch (`docs/reviews/`, `docs/audits/`) or in this repository's code and tests other than the
  files `DECLARED_USES` names (this test alone until the build adds its files, which T-9 holds to section 12's uses).
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from extended import identity_cover, reader

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"
DRAFT_NAME = "DRAFT_RD-03_contract_levers.md"
PINNED_NAME = "RD-03_contract_levers.md"
RECORD = ROOT / "config" / "rules_extended.yaml"
#: Q-115's record, committed on wt/wt-firms and not yet on master (E-135): read from here until it merges
Q115_COMMIT = "deb45ad"
Q115_PROBE_KEY = "back2funded_reactivation_fee_50k"
STAGE2_LEDGER = ROOT / "vendor" / "stage2" / "config" / "rules.yaml"
VENDOR = ROOT / "vendor"
VENDOR_DATA = VENDOR / "stage2" / "data"                        # the licensed bars and atlas: never scanned
SCRATCH_DIRS = (ROOT / "docs" / "reviews", ROOT / "docs" / "audits")
CODE_DIRS = (ROOT / "extended", ROOT / "identity", ROOT / "scripts", ROOT / "tests")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini"}

SEED_BLOCK = tuple(range(20262240, 20262250))
#: the repository files allowed to hold a seed of the block besides the declaration: its declared uses (section 12).
#: The build adds its own files here as it writes them (the honesty series, the toy campaigns); T-9 holds them to 12.
DECLARED_USES = ("tests/test_rd03_draft.py",)

PURPOSES = {"levers_scorecard", "levers_gate_beside", "levers_ladder_beside", "levers_ftp_beside"}
BASES = ("P-14", "P-16")
CALENDARS = {"config/calendar_early_closes.csv": "72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2",
             "config/calendar_fomc_minutes.csv": "0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7"}

GRID_ROW = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|\s*(--|L-[BIHN])\s*\|[^|]*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$",
                      re.MULTILINE)
APPENDIX_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(record|stage2)\s*\|\s*([a-z_]+)", re.MULTILINE)
SEED_ROW = re.compile(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
CHOICE_ROW = re.compile(r"^\|\s*(\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|\s*$", re.MULTILINE)


# ------------------------------------------------------------------------------------------------- the text


def declaration(prereg: Path = PREREG) -> Path:
    """The one contract-levers declaration under `prereg`: the draft before the pin, the pinned file after."""
    found = sorted(p for p in prereg.glob("*contract_levers.md") if p.name in (DRAFT_NAME, PINNED_NAME))
    assert len(found) == 1, f"exactly one contract-levers declaration expected under {prereg}, found {found}"
    return found[0]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


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
    assert body.startswith("# RD-03: "), "the title is the pinned file's"
    assert "**Status: declared before anything of it is built or read.**" in body
    assert not re.search(r"^\*\*Status:[^\n]*\bDRAFT\b", body, re.MULTILINE), "a draft-form status"
    assert re.search(r"^\| id \| RD-03 \(`prereg/RD-03_contract_levers\.md` at the pin\)", body, re.MULTILINE)
    assert re.search(r"^\| `confirmation_tests_on_this_market` \| ", body, re.MULTILINE)
    assert reader.DECLARATION_PATH.fullmatch(f"prereg/{PINNED_NAME}"), "the reader admits the pinned name"
    for rel, sha in CALENDARS.items():
        assert f"`{rel}`" in body and sha in body, f"{rel} not cited with its LF sha256"


def grid(body: str) -> list[tuple[str, str, str, str]]:
    rows = GRID_ROW.findall(section(body, "### 7.2"))
    assert rows, "section 7.2's grid has no rows"
    names = [r[0] for r in rows]
    assert len(names) == len(set(names)), f"a cell named twice in 7.2: {names}"
    return rows


def check_counts(body: str) -> None:
    rows = grid(body)
    refs = [r for r in rows if r[1] == "--"]
    assert [r[0] for r in refs] == ["ref"], "one reference row"
    assert all(r[2].startswith("reference") and r[3].startswith("reference") for r in refs)
    new_rows = [r for r in rows if r[1] != "--"]
    for name, lever, p14, p16 in new_rows:                     # every new cell runs on both bases
        assert p14.startswith("new") and p16.startswith("new"), name
        assert (lever == "L-H") == ("gaming P" in p14 and "gaming P" in p16), f"{name}: the gaming-P label"
    by = {lv: 2 * sum(1 for r in new_rows if r[1] == lv) for lv in ("L-B", "L-I", "L-H", "L-N")}
    assert by == {"L-B": 4, "L-I": 16, "L-H": 8, "L-N": 2}, by
    new = sum(by.values())
    replays = new + 2 * len(refs)
    ladder = 4 * new                                            # denial_10, denial_25, denial_50, rtp
    ftp = 10 * (by["L-I"] + by["L-B"])                          # the ten models on the inventory and Back2Funded cells
    ftp_counted = 10 * by["L-B"]                                # the counted reading (U-6)
    ftp_not_run = 10 * (by["L-H"] + by["L-N"])
    ref_checks = 2 * 4 + 2 * 10                                 # `ref` on two bases, ladder and placement, then ftp
    beside = ladder + ftp + ftp_counted
    gates = new
    assert (new, replays, ladder, ftp, ftp_counted, ftp_not_run, ref_checks, beside, gates) == \
        (30, 32, 120, 200, 40, 100, 28, 360, 30)
    head = section(body, "# RD-03")
    assert f"**{new} new cells, every one run**" in head
    assert "4 Back2Funded, 16 inventory, 8 house-money, 2 pricing-path" in head
    s13 = section(body, "## 13.")
    for s in (f"**{replays} replays; {new} new cells.**", f"4 x {new} = **{ladder} replays**",
              f"10 x ({by['L-I']} inventory + {by['L-B']} Back2Funded) = **{ftp} replays**",
              f"10 x {by['L-B']} = **{ftp_counted} replays**", f"({ftp_not_run} replays not run",
              f"**{beside} replays beside and {ref_checks} reference checks**", f"**{gates} gates**",
              f"{by['L-B']}\n   Back2Funded + {by['L-I']} inventory + {by['L-H']} house money + {by['L-N']} `naf`"):
        assert s in s13, f"section 13 lacks {s!r}"
    s15 = section(body, "## 15.")
    assert f"{beside} replays beside" in s15 and f"with {ref_checks}\n    reference checks" in s15


def check_appendix_c(body: str) -> None:
    rows = CHOICE_ROW.findall(section(body, "## Appendix C"))
    assert [int(r[0]) for r in rows] == list(range(1, 26)), f"Appendix C must number 25 choices 1..25: {rows[:3]}"
    for n, choice, where, why in rows:
        assert choice.strip() and where.strip() and why.strip(), f"choice {n} lacks its text, its place or its reason"


def check_covers(body: str) -> None:
    s91 = section(body, "### 9.1")
    para = s91[s91.index("**The two identities' covers"):]
    para = para[:para.index("\n\n")]
    assert "Q-111" in para and "`extended/identity_cover.py`" in para
    assert "`BASE`" in para and "`identity_cover.imports(script)`" in para
    for script in ("identity/cl_identity.py", "identity/cl_fit_identity.py"):
        assert f"`{script}`" in para, script
    assert identity_cover.BASE == ("extended/__init__.py", "config/", "vendor/MANIFEST_stage2.sha256",
                                   "vendor/DATA_MANIFEST_stage2.sha256"), "Q-111's BASE changed: re-read 9.1"
    flat = para.replace("\n", " ")
    for entry in ("`extended/__init__.py`", "the folder `config/` whole", "`vendor/MANIFEST_stage2.sha256`",
                  "`vendor/DATA_MANIFEST_stage2.sha256`"):
        assert entry in flat, f"9.1's covers do not name {entry}"
    assert callable(identity_cover.imports)


def check_purposes(body: str) -> None:
    assert len(reader.DECLARED_LINE.findall(body)) == 1, "exactly one 'Judged-block reads:' line"
    purposes = set(reader.declared_purposes(body))
    assert purposes == PURPOSES, purposes
    for p in purposes:
        assert reader.PURPOSE.fullmatch(p), p
        assert not reader._choice_purpose(p), f"{p} is a choosing or fitting purpose"
    assert reader.IDENTITY not in purposes and "registered_design" not in purposes


def record_status() -> dict[str, str]:
    """This repository's record: the working `config/rules_extended.yaml`, and Q-115's commit for any key it lacks."""
    out = {str(e["key"]): str(e["status"]) for e in yaml.safe_load(RECORD.read_text(encoding="utf-8"))["rules"]}
    if Q115_PROBE_KEY not in out:
        r = subprocess.run(["git", "show", f"{Q115_COMMIT}:config/rules_extended.yaml"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, f"Q-115's record is neither merged nor reachable at {Q115_COMMIT}: {r.stderr}"
        for e in yaml.safe_load(r.stdout)["rules"]:
            out.setdefault(str(e["key"]), str(e["status"]))
    return out


def ledger_status() -> dict[str, str]:
    rules = yaml.safe_load(STAGE2_LEDGER.read_text(encoding="utf-8"))["rules"]
    items = rules.items() if isinstance(rules, dict) else ((r.get("key"), r) for r in rules if isinstance(r, dict))
    return {str(k): str(v.get("status")) for k, v in items}


def check_rule_keys(body: str) -> None:
    sources = {"record": record_status(), "stage2": ledger_status()}
    rows = APPENDIX_ROW.findall(section(body, "## Appendix R"))
    assert rows, "Appendix R cites no rule"
    seen, bad = set(), []
    for key, src, status in rows:
        assert (key, src) not in seen, f"{key} ({src}) cited twice"
        seen.add((key, src))
        got = sources[src].get(key)
        if got != status:
            bad.append(f"{key} ({src}): the declaration says {status!r}, the source holds {got!r}")
    assert not bad, "\n".join(bad)
    cited = {k for k, _ in seen}
    s42 = section(body, "### 4.2")
    keys_42 = {k for line in s42.split("\n") if line.startswith("| `")
               for k in re.findall(r"`([a-z0-9_]+)`", line.split("|")[1])}
    assert keys_42 and not keys_42 - cited, f"keys of 4.2 not in Appendix R: {sorted(keys_42 - cited)}"


CHECKS = (check_pin_form, check_counts, check_appendix_c, check_covers, check_purposes, check_rule_keys)


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
    """Not vacuous: a grid with one inventory row removed is refused."""
    body = read(declaration())
    s72 = section(body, "### 7.2")
    row = next(line for line in s72.split("\n") if line.startswith("| `inv7_hold_30`"))
    with pytest.raises(AssertionError):
        check_counts(body.replace(row + "\n", ""))


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


def test_section_12_lists_the_block_once_each_two_in_use_eight_reserved():
    rows = SEED_ROW.findall(section(read(declaration()), "## 12."))
    assert sorted(int(s) for s, _ in rows) == list(SEED_BLOCK), rows
    status = {int(s): st.strip().lower() for s, st in rows}
    assert [s for s in SEED_BLOCK if status[s] == "in use"] == list(SEED_BLOCK[:2])
    assert all(status[s].startswith("reserved") for s in SEED_BLOCK[2:])


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
    """Not vacuous: the scan finds this file's own block, and a seed of RD-01's block in RD-01's declaration."""
    here = Path(__file__).resolve()
    assert _occurrences_of((SEED_BLOCK[0],), [here])[SEED_BLOCK[0]]
    rd01 = PREREG / "RD-01_firm_contracts.md"
    assert _occurrences_of((20261990,), [rd01])[20261990]
