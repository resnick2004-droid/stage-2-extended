"""Q-179's fill (the O-7 pins, E-268 to E-272): `extended.reader.SUPERSEDED` holds exactly the four parents that RD-06
to RD-10 supersede -- RD-01 to RD-04, never RD-05 (its steps 0 to 2 keep it) -- each with its file's LF sha256, and the
reader refuses a read authorised by each of them, on the search years and on the judged block, by its path, by its id,
and by its bytes under another path. Nothing is read: `authorise` reads and writes nothing, and every read here is
refused before any ledger line.

* `test_superseded_is_the_drafts_tests_parents` -- path for path with `tests/test_rd_search_years_drafts.py`'s
  `SUPERSEDED` map (its non-None parents), hash for hash with each file in this tree (LF);
* `test_a_read_authorised_by_each_superseded_file_is_refused` -- `SupersededRefused` for every parent, on 2020-01-02 to
  2023-12-29 and on 2024-01-02 to 2026-07-16, by path and by id;
* `test_a_superseded_files_bytes_under_another_path_are_refused` -- the same bytes copied to a new RD path in a
  temporary tree are refused too.
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


def lf_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_superseded_is_the_drafts_tests_parents():
    assert PARENTS == ["prereg/RD-01_firm_contracts.md", "prereg/RD-02_payout_policy.md",
                       "prereg/RD-03_contract_levers.md", "prereg/RD-04_volatility_drift.md"]
    assert "prereg/RD-05_firm_modes.md" not in {p for p, _ in R.SUPERSEDED}, "RD-05's steps 0 to 2 keep it"
    assert sorted(p for p, _ in R.SUPERSEDED) == PARENTS, "path for path"
    assert len(R.SUPERSEDED) == len(set(R.SUPERSEDED)) == len(PARENTS)
    for rel, sha in R.SUPERSEDED:
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
