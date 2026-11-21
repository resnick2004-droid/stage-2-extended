"""Q-173: the reader's closures after the red team's read of the O-7 drafts (`docs/reviews/O7_SEARCH_YEARS_2026-11-19.md`
M-3, N-1, N-2), on Q-158's synthetic tree (`tests/test_reader_heldout.py`'s helpers; nothing real is read).

* **rule 3 closed (M-3):** a `registered_design` held-out read made for a described reading -- its row names an RD,
  or an RD file names its script -- is refused under rule 3 until the market's verdict row, then admitted; a read for
  no reading is unchanged; the joint held-out test's family declaration is still admitted before any verdict;
* **the supersession rule (N-1):** a superseded declaration (by path, or by bytes under another path) authorises no
  read -- judged, search-year, or a registered replay made for it -- whatever later rows exist; an empty list changes
  nothing;
* **the identity rule (N-2):** an identity script that writes to `results/` is refused; this repository's identity
  scripts are not;
* **each rule's mutation is killed:** with its guard replaced by a no-op, the refused read goes through.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from extended import reader as R
import test_reader_heldout as H
from test_reader_heldout import scripted, tree  # noqa: F401 -- the fixtures

ROOT = Path(__file__).resolve().parent.parent
VERDICT = "| E-930 | 2026-11-18 | heldout-verdict: NQ F-13 -- F-13's held-out verdict | x |"


def commit_file(t: Path, rel: str, text: str) -> None:
    (t / rel).parent.mkdir(parents=True, exist_ok=True)
    (t / rel).write_bytes(text.encode("utf-8"))
    H.git(t, "add", "-A")
    H.git(t, "commit", "-q", "-m", f"add {rel}")


# ------------------------------------------------------------------------------------------------------ rule 3 (M-3)


def test_rule3_a_described_readings_replay_waits_for_the_verdict(scripted):
    H.add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14,P-16 by scripts/replay.py -- RD-04 (c)'s replay "
                         "of P-14 and P-16 | x |")
    e = H.refused(3, H.rd_read, scripted, "E-940", ("P-14", "P-16"))
    assert "RD-04" in str(e) and "verdict" in str(e)
    assert H.lines(scripted) == []
    H.add_rows(scripted, VERDICT)
    a = H.rd_read(scripted, "E-940", ("P-14", "P-16"))
    assert a.ledgered and dict(a.heldout) == {"read_row": "E-940", "readings": "RD-04", "test_verdict": "E-982"}


def test_rule3_a_reading_that_names_the_script_is_linked_without_the_row_saying_so(scripted):
    commit_file(scripted, "prereg/RD-08_replay.md", "# RD-08\n\nThe replay runs `scripts/replay.py` under "
                                                    "`registered_design`.\n")
    H.add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14 by scripts/replay.py -- P-14 replayed | x |")
    assert "RD-08" in str(H.refused(3, H.rd_read, scripted, "E-940", "P-14"))
    assert R.registered_for_readings("no reading named", "scripts/replay.py", scripted) == ("RD-08",)
    assert R.registered_for_readings("no reading named", "scripts/other.py", scripted) == ()


def test_rule3_a_replay_for_no_reading_is_unchanged_and_the_joint_test_is_admitted(scripted):
    H.add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14,P-16 by scripts/replay.py -- P-14 and P-16 | x |",
               H.finalists(920, "F-13", H.F13_TEXT, H.LIST13))
    a = H.rd_read(scripted, "E-940", "P-14")
    assert dict(a.heldout) == {"read_row": "E-940", "test_verdict": "E-982"}
    j = H.read(scripted)                                       # the joint held-out test, before any verdict row
    assert j.judged and j.ledgered and j.kind == "family"


def test_rule3_mutation_is_killed(scripted, monkeypatch):
    H.add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14 by scripts/replay.py -- RD-04 (c) | x |")
    H.refused(3, H.rd_read, scripted, "E-940", "P-14")
    monkeypatch.setattr(R, "_registered_reading_verdict", lambda *a, **k: ())
    assert H.rd_read(scripted, "E-940", "P-14").ledgered       # without the guard the replay would go through


# ------------------------------------------------------------------------------------------- the supersession rule


def superseded(t: Path, rel: str = H.RD7, text: str = H.RD7_TEXT):
    return ((rel, H.sha_lf(text)),)


def refused_superseded(fn, *a, **kw) -> R.SupersededRefused:
    with pytest.raises(R.SupersededRefused) as info:
        fn(*a, **kw)
    assert str(info.value).startswith(f"REFUSED ({R.SUPERSESSION_RULE})"), str(info.value)
    return info.value


def test_a_superseded_declaration_authorises_no_read_whatever_later_rows_say(tree, monkeypatch):
    H.add_rows(tree, VERDICT)
    a = H.read(tree, declaration=H.RD7, purpose="stage_D_scorecard")      # control: after the verdict, admitted
    assert a.ledgered and a.kind == "described_reading"
    monkeypatch.setattr(R, "SUPERSEDED", superseded(tree))
    n = len(H.lines(tree))
    refused_superseded(H.read, tree, declaration=H.RD7, purpose="stage_D_scorecard")
    refused_superseded(H.read, tree, declaration="RD-07", purpose="stage_D_scorecard")       # by its id
    refused_superseded(H.read, tree, declaration=H.RD7, purpose="stage_D_scorecard",         # the search years too
                       start="2020-01-02", end="2023-12-29")
    H.add_rows(tree, "| E-931 | 2026-11-19 | **RD-07 reopened** -- a later row cannot lift it | x |")
    refused_superseded(H.read, tree, declaration=H.RD7, purpose="stage_D_scorecard")
    assert len(H.lines(tree)) == n, "a refused read writes no ledger line"


def test_a_superseded_declarations_bytes_under_another_path_are_refused(tree, monkeypatch):
    commit_file(tree, "prereg/RD-09_copy.md", H.RD7_TEXT)
    monkeypatch.setattr(R, "SUPERSEDED", superseded(tree))
    e = refused_superseded(H.read, tree, declaration="prereg/RD-09_copy.md", purpose="stage_D_scorecard")
    assert H.RD7 in str(e)


def test_a_replay_made_for_a_superseded_reading_is_refused(scripted, monkeypatch):
    H.add_rows(scripted, VERDICT, "| E-940 | 2026-11-18 | heldout-read: P-14 by scripts/replay.py -- RD-07's replay "
                                  "| x |")
    assert H.rd_read(scripted, "E-940", "P-14").ledgered                 # control
    monkeypatch.setattr(R, "SUPERSEDED", superseded(scripted))
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-1")
    refused_superseded(H.rd_read, scripted, "E-940", "P-14")


def test_the_supersession_list_is_empty_until_the_lead_fills_it_and_its_mutation_is_killed(tree, monkeypatch):
    assert R.SUPERSEDED == ()
    H.add_rows(tree, VERDICT)
    monkeypatch.setattr(R, "SUPERSEDED", superseded(tree))
    refused_superseded(H.read, tree, declaration=H.RD7, purpose="stage_D_scorecard")
    monkeypatch.setattr(R, "_refuse_superseded", lambda *a, **k: None)
    assert H.read(tree, declaration=H.RD7, purpose="stage_D_scorecard").ledgered


# ------------------------------------------------------------------------------------------- the identity rule (N-2)


@pytest.mark.parametrize("src, flagged", [
    ("from extended.results import write_result\nwrite_result(df, 'x', script='s', seed=1, parameters={})\n", True),
    ("open(ROOT / 'results' / 'x.csv', 'w').write('1')\n", True),
    ("open('results/x.csv', mode='a')\n", True),
    ("Path('results/out.txt').write_text('pass')\n", True),
    ("df.to_csv(f'results/{name}.csv')\n", True),
    ("open(ROOT / 'results' / 'x.csv').read()\n", False),                  # a read
    ("print(f'identity HOLDS: results/{ref} matches')\n", False),          # a message
    ("Path('docs/out.txt').write_text('pass')\n", False),                  # elsewhere
    ("open('results_summary.txt', 'w')\n", False),                         # not the results/ folder
])
def test_identity_write_problems(src, flagged):
    assert bool(R.identity_write_problems(src)) is flagged


def test_this_repositorys_identity_scripts_write_nothing_to_results():
    found = {p.name: R.identity_write_problems(p.read_text(encoding="utf-8"))
             for p in sorted((ROOT / "identity").glob("*.py"))}
    assert found and not {k: v for k, v in found.items() if v}


def identity_read(t: Path):
    return R.authorise_engine_read("2020-01-02", "2026-07-16", purpose="identity", declaration="E-905",
                                   files=[t / H.BARS], what="q173 identity", repo=t)


def test_an_identity_that_writes_to_results_is_refused_and_its_mutation_is_killed(tree, monkeypatch):
    commit_file(tree, "identity/clean_id.py", "print('identity HOLDS')\n")
    commit_file(tree, "identity/writer_id.py", "from pathlib import Path\nPath('results/x.csv').write_text('1')\n")
    monkeypatch.setattr(R, "_main_script", lambda: tree / "identity" / "clean_id.py")
    assert identity_read(tree).judged
    monkeypatch.setattr(R, "_main_script", lambda: tree / "identity" / "writer_id.py")
    with pytest.raises(R.JudgedBlockSealed) as info:
        identity_read(tree)
    assert f"REFUSED ({R.IDENTITY_WRITE_RULE})" in str(info.value) and "line 2" in str(info.value)
    monkeypatch.setattr(R, "_identity_writes", lambda *a, **k: None)
    assert identity_read(tree).judged
