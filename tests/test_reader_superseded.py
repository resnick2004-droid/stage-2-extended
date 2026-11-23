"""Q-179's fill (the O-7 pins, E-268 to E-272): `extended.reader.SUPERSEDED` holds exactly the four parents that RD-06
to RD-10 supersede -- RD-01 to RD-04, every purpose ("*") -- each with its file's LF sha256, and (Q-212, F7) RD-05 for
its part F's three purposes alone, superseded by RD-09 (E-271), its steps 0 to 2 keeping theirs; and the reader refuses
a read authorised by each of them, on the search years and on the judged block, by its path, by its id, by its bytes
under another path, by a decision row pinning it, and (search years) a read under a superseded purpose naming no
pinned declaration. Nothing is read: `authorise` reads and writes nothing, and every read here is refused before any
ledger line.

* `test_superseded_is_the_drafts_tests_parents` -- path for path with `tests/test_rd_search_years_drafts.py`'s
  `SUPERSEDED` map (its non-None parents), hash for hash with each file in this tree (LF);
* `test_a_read_authorised_by_each_superseded_file_is_refused` -- `SupersededRefused` for every parent, on 2020-01-02 to
  2023-12-29 and on 2024-01-02 to 2026-07-16, by path and by id;
* `test_a_superseded_files_bytes_under_another_path_are_refused` -- the same bytes copied to a new RD path in a
  temporary tree are refused too;
* Q-212 (F7): `test_rd05_is_superseded_for_its_part_f_alone`, `test_a_decision_row_resolves_to_its_pin`,
  `test_the_search_years_need_a_pinned_declaration_for_a_superseded_purpose`,
  `test_an_edited_superseded_file_at_its_own_path_is_refused` (the red team's m47b).
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import reader as R  # noqa: E402
import test_rd_search_years_drafts as DR  # noqa: E402  (the drafts' map of what each O-7 pin supersedes)

PARENTS = sorted(path for path, _ in DR.SUPERSEDED.values() if path is not None)
RD05 = "prereg/RD-05_firm_modes.md"
PART_F = DR.SUPERSEDED["RD-09"][1]                     # RD-09's delta supersedes RD-05's part F (E-271)
BLOCKS = [("2020-01-02", "2023-12-29"), ("2024-01-02", "2026-07-16")]


def lf_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_superseded_is_the_drafts_tests_parents():
    assert PARENTS == ["prereg/RD-01_firm_contracts.md", "prereg/RD-02_payout_policy.md",
                       "prereg/RD-03_contract_levers.md", "prereg/RD-04_volatility_drift.md"]
    whole = [e for e in R.SUPERSEDED if e[2] == "*"]
    assert sorted(e[0] for e in whole) == PARENTS, "path for path, every purpose"
    assert [e for e in R.SUPERSEDED if e[2] != "*"] == [(RD05, lf_sha(ROOT / RD05), PART_F)],         "RD-05 for its part F alone, RD-09's purposes (its steps 0 to 2 keep theirs)"
    assert set(PART_F) == R.declared_purposes((ROOT / RD05).read_text(encoding="utf-8")), "part F is its judged line"
    assert len(R.SUPERSEDED) == len({e[0] for e in R.SUPERSEDED}) == len(PARENTS) + 1
    for rel, sha, _ in R.SUPERSEDED:
        assert sha == lf_sha(ROOT / rel), f"hash for hash: {rel}"


@pytest.mark.parametrize("rel", PARENTS)
@pytest.mark.parametrize("start,end", [("2020-01-02", "2023-12-29"), ("2024-01-02", "2026-07-16")])
def test_a_read_authorised_by_each_superseded_file_is_refused(rel, start, end):
    purposes = sorted(R.declared_purposes((ROOT / rel).read_text(encoding="utf-8")))
    assert purposes, rel
    rid = rel.split("/")[1].split("_")[0]
    for declaration in (rel, rid):
        with pytest.raises(R.SupersededRefused) as info:
            R.authorise(start, end, purpose=purposes[0], declaration=declaration, repo=ROOT, what="q179")
        assert rel in str(info.value) or rid in str(info.value)


def test_a_superseded_files_bytes_under_another_path_are_refused(tmp_path):
    (tmp_path / "prereg").mkdir()
    shutil.copy(ROOT / "DECISIONS.md", tmp_path / "DECISIONS.md")
    for i, rel in enumerate(PARENTS):
        copy = f"prereg/RD-{80 + i}_copy.md"
        (tmp_path / copy).write_bytes((ROOT / rel).read_bytes())
        with pytest.raises(R.SupersededRefused) as info:
            R.authorise("2020-01-02", "2023-12-29", declaration=copy, repo=tmp_path, what="q179 copy")
        assert rel in str(info.value)


def tmp_tree(tmp_path: Path) -> Path:
    (tmp_path / "prereg").mkdir()
    shutil.copy(ROOT / "DECISIONS.md", tmp_path / "DECISIONS.md")
    for rel in PARENTS + [RD05]:
        shutil.copy(ROOT / rel, tmp_path / rel)
    return tmp_path


def refused(start, end, **kw) -> str:
    with pytest.raises(R.SupersededRefused) as info:
        R.authorise(start, end, what="q212 f7", **kw)
    return str(info.value)


@pytest.mark.parametrize("start,end", BLOCKS)
def test_rd05_is_superseded_for_its_part_f_alone(tmp_path, start, end):
    t = tmp_tree(tmp_path)
    shutil.copy(ROOT / RD05, t / "prereg" / "RD-81_copy.md")
    for purpose in PART_F:
        for declaration in (RD05, "RD-05", "prereg/RD-81_copy.md"):
            assert RD05 in refused(start, end, purpose=purpose, declaration=declaration, repo=t)
    if start < "2024":                                         # its steps 0 to 2 read the search years under it
        for declaration in (RD05, "RD-05", "prereg/RD-81_copy.md"):
            a = R.authorise(start, end, declaration=declaration, repo=t, what="RD-05 step 0")
            assert a.declaration == declaration and not a.ledgered


@pytest.mark.parametrize("start,end", BLOCKS)
def test_a_decision_row_resolves_to_its_pin(start, end):
    assert R.decision_row(R._decisions(ROOT), "E-080") and RD_PIN(R.decision_row(R._decisions(ROOT), "E-080"))
    e = refused(start, end, purpose="firm_scorecard", declaration="E-080", repo=ROOT)
    assert PARENTS[0] in e if start >= "2024" else "never none or a decision row" in e
    if start < "2024":
        assert PARENTS[0] in refused(start, end, declaration="E-080", repo=ROOT), "no purpose: the pin still binds"


def RD_PIN(row: str) -> bool:
    return any(rel == PARENTS[0] for rel, _ in R.PIN.findall(row))


def test_the_search_years_need_a_pinned_declaration_for_a_superseded_purpose():
    for purpose in ("firm_scorecard", "modes_scorecard", "volatility_descriptive"):
        for declaration in (None, "E-271", "E-273"):
            e = refused("2020-01-02", "2023-12-29", purpose=purpose, declaration=declaration, repo=ROOT)
            assert purpose in e or "superseded" in e
    a = R.authorise("2020-01-02", "2023-12-29", repo=ROOT, what="a choice-block read needs no tag")
    assert a.declaration is None


def test_an_edited_superseded_file_at_its_own_path_is_refused(tmp_path):
    t = tmp_tree(tmp_path)
    for rel in PARENTS + [RD05]:
        (t / rel).write_bytes((ROOT / rel).read_bytes() + b"\nan edit after its pin\n")
        assert lf_sha(t / rel) not in {e[1] for e in R.SUPERSEDED}
        purpose = sorted(R.declared_purposes((ROOT / rel).read_text(encoding="utf-8")))[0]
        for start, end in BLOCKS:
            assert rel in refused(start, end, purpose=purpose, declaration=rel, repo=t), (rel, start)


def test_only_the_readers_own_list_is_exempt_from_the_code_guard(tmp_path):
    """The drafts' N-1 code guard skips the reader's `SUPERSEDED` assignment alone: a part-F purpose named anywhere
    else in the reader is found."""
    (tmp_path / "extended").mkdir()
    text = (ROOT / "extended" / "reader.py").read_text(encoding="utf-8")
    (tmp_path / "extended" / "reader.py").write_text(text, encoding="utf-8")
    assert DR.code_mentions("RD-09", root=tmp_path) == set()
    (tmp_path / "extended" / "reader.py").write_text(text + '\nSTEP = "modes_scorecard"\n', encoding="utf-8")
    assert DR.code_mentions("RD-09", root=tmp_path) == {"extended/reader.py"}
