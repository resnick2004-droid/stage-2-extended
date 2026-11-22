"""Q-194e (the lead's rulings on the red team's `READER_Q194d_2026-11-21`), on Q-158's synthetic tree
(`tests/test_reader_heldout.py`'s helpers; `tests/heldout_verdict_rows.py`'s F-98; nothing real is read).

* **MINOR-1, merges:** every commit of the whole history, merge commits included (`git log --full-history -m -S`),
  whose DECISIONS.md adds the verdict row must hold the backing line in its committed ledger, with the read's commit a
  proper ancestor -- the red team's P1 (a premature verdict hidden by a merge) and P2 (a verdict recorded in a merge,
  removed and re-added) are refused; P3 (a verdict recorded in a merge commit after its read was committed) is
  admitted;
* **MINOR-2, the log's recovery:** a later row `heldout-void: E-NNN -- <reason>` voids a malformed row (P4) or closes
  a fence left open just after row E-NNN at the void row's end (P5; the rows between stay hidden); a void never voids
  a verdict, finalists' or pin row, a void placed before its row or inside a fence does nothing;
* **P10:** no F- declaration but the market's one held-out declaration reads any held-out date, under any purpose,
  with or without a finalists' token (F-03-like and F-14-like fixtures; a held-out declaration's own stage purpose);
* **P9:** no `repeat=` row is honoured for the held-out declaration;
* **Y6:** a held-out-marked file whose name names no market, beside the real one, blocks it;
* **NOTE-3:** the docstring states that a later window needs its own rule; **NOTE-6:** an `OSError` from git fails
  closed with a named refusal.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from extended import reader as R
import heldout_verdict_rows as VR
import test_reader_heldout as H
import test_reader_q194d as D
from test_reader_heldout import tree  # noqa: F401 -- the fixture
from test_reader_q194d import declared  # noqa: F401 -- the fixture

COLLECTED = "| E-983 | 2026-11-19 | the run's lines collected | x |"


def g(t: Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=t, capture_output=True, text=True, check=True).stdout.strip()


def merge_with_row(t: Path, row: str) -> str:
    """A worker's branch merged with --no-commit and a decision row recorded in the merge commit itself."""
    g(t, "checkout", "-q", "-b", "side")
    (t / "other.txt").write_text("x\n", encoding="utf-8")
    g(t, "add", "other.txt")
    g(t, "commit", "-q", "-m", "a worker's change")
    g(t, "checkout", "-q", "master")
    g(t, "merge", "-q", "--no-ff", "--no-commit", "side")
    VR._append(t, [row])
    g(t, "add", "DECISIONS.md")
    g(t, "commit", "-q", "-m", "merged, with a row")
    return D.head(t)


# --------------------------------------------------------------------------------------------- MINOR-1: merges


def test_p1_a_premature_verdict_hidden_by_a_merge_is_refused(declared):
    c0 = VR.declare(declared)
    VR.append_rows(declared, VR.VERDICT_ROW)                    # M1: the verdict committed first, no ledger line
    m1 = D.head(declared)
    D.gate_refuses(declared)
    g(declared, "checkout", "-q", "-b", "side2", c0)
    D.put_lines(declared, [D.forged(c0)])                       # the read from c0
    s1 = VR.commit_verdict(declared, VR.VERDICT_ROW, COLLECTED)  # S1: ledger + verdict + one more row
    g(declared, "checkout", "-q", "master")
    r = subprocess.run(["git", "merge", "-q", "--no-edit", "side2"], cwd=declared, capture_output=True, text=True)
    if r.returncode:                                            # a conflict on DECISIONS.md: the side's version
        g(declared, "checkout", "--theirs", "DECISIONS.md")
        g(declared, "add", "DECISIONS.md")
        g(declared, "commit", "-q", "--no-edit")
    hits = R._verdict_commits(declared, VR.VERDICT_ROW)
    assert {m1, s1} <= set(hits), "every commit adding the row, merges' sides included"
    D.gate_refuses(declared)                                    # M1's ledger lacks the line


def test_p2_a_verdict_recorded_in_a_merge_then_removed_and_readded_is_refused(declared):
    c0 = VR.declare(declared)
    m = merge_with_row(declared, VR.VERDICT_ROW)                # the verdict recorded in the merge commit
    assert R._verdict_commits(declared, VR.VERDICT_ROW) == [m]
    D.put_lines(declared, [D.forged(c0)])
    VR.commit_verdict(declared, COLLECTED)                      # the ledger committed after the verdict
    D.gate_refuses(declared)
    p = declared / "DECISIONS.md"
    p.write_bytes(p.read_text(encoding="utf-8").replace(VR.VERDICT_ROW + "\n", "").encode("utf-8"))
    g(declared, "commit", "-q", "-am", "the row removed")
    VR.append_rows(declared, VR.VERDICT_ROW)                    # and re-added
    assert R._verdict_commits(declared, VR.VERDICT_ROW)[0] == m, "the removal holds no row: never a hit"
    D.gate_refuses(declared)


def test_every_commit_adding_the_row_must_hold_the_line_not_only_one(declared):
    """The row added (A, its ledger without the read's line), removed, and added again (B, its ledger with it): A
    alone refuses -- the order must hold at every commit that adds the verdict row."""
    c0 = VR.declare(declared)
    D.put_lines(declared, [D.forged(c0, **{"declaration.ref": H.F13})])    # an unrelated line: A has a ledger
    a = VR.commit_verdict(declared, VR.VERDICT_ROW)
    p = declared / "DECISIONS.md"
    p.write_bytes(p.read_text(encoding="utf-8").replace(VR.VERDICT_ROW + "\n", "").encode("utf-8"))
    g(declared, "commit", "-q", "-am", "the row removed")
    D.put_lines(declared, [D.forged(c0)])
    b = VR.commit_verdict(declared, VR.VERDICT_ROW)
    assert R._verdict_commits(declared, VR.VERDICT_ROW) == [a, b]
    D.gate_refuses(declared)


def test_p3_a_verdict_recorded_in_a_merge_commit_after_its_read_counts(declared):
    c0 = VR.declare(declared)
    D.put_lines(declared, [D.forged(c0)])
    VR.commit_verdict(declared, COLLECTED)                      # the read's line committed first
    m = merge_with_row(declared, VR.VERDICT_ROW)
    assert R._verdict_commits(declared, VR.VERDICT_ROW) == [m]
    assert dict(D.reg(declared).heldout)["test_verdict"] == "E-982"


# --------------------------------------------------------------------------------- MINOR-2: the log's recovery


MALFORMED = "| E-995 | 2026-11-20 | **Held-out verdict:** NQ F-98 passed (prose) | x |"


def void(row: int, target: str, why: str = "a correction") -> str:
    return f"| E-{row} | 2026-11-20 | heldout-void: {target} -- {why} | x |"


def test_p4_a_malformed_row_voided_by_a_later_row(declared):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, MALFORMED, "| E-996 | 2026-11-20 | E-995 rewritten: it is no token | x |")
    D.hygiene_refuses(D.reg, declared)                          # rewritten in prose: still a problem
    VR.append_rows(declared, void(997, "E-995", "prose, not a token"))
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.heldout_token_problems(text) == []
    assert dict(D.reg(declared).heldout)["test_verdict"] == "E-982"


def test_a_void_placed_before_its_row_does_nothing(declared):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, void(994, "E-995"), MALFORMED)
    D.hygiene_refuses(D.reg, declared)


def test_p5_a_stray_fence_closed_by_a_void_hides_the_rows_between_and_reports_none(declared):
    VR.settle(declared, [declared / H.BARS])
    hidden = VR.verdict_row(990)
    VR.append_rows(declared, "| E-985 | 2026-11-20 | a row typed before a stray fence | x |", "```", hidden,
                   "| E-986 | 2026-11-20 | **hidden by the fence** | x |")
    msg = D.hygiene_refuses(D.reg, declared)
    assert "never closed" in msg
    VR.append_rows(declared, void(987, "E-985", "the stray fence after E-985"), "| E-988 | 2026-11-20 | after | x |")
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.heldout_token_problems(text) == []
    assert R.decision_row(text, "E-986") is None and R.decision_row(text, "E-988") is not None
    assert "E-990" not in [t.row for t in R.heldout_tokens(text, "verdict")], "nothing between is revived"
    assert dict(D.reg(declared).heldout)["test_verdict"] == "E-982"


def test_a_void_does_not_close_a_fence_it_does_not_follow(declared):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, "| E-985 | 2026-11-20 | a row | x |", "| E-986 | 2026-11-20 | another | x |", "```",
                   void(987, "E-985", "not the row the fence follows"))
    D.hygiene_refuses(D.reg, declared)


@pytest.mark.parametrize("target", ["E-980", "E-981", "E-982"])     # the pin, the finalists' row, the verdict
def test_a_void_never_voids_a_verdict_finalists_or_pin_row(declared, target):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, void(990, target, "an attempt to remove a read"))
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.heldout_token_problems(text) == []
    assert VR.HT_PATH in R.pins(text)
    assert [t.row for t in R.heldout_tokens(text, "finalists")] == ["E-981"]
    assert dict(D.reg(declared).heldout)["test_verdict"] == "E-982", "the read and its verdict still count"


def test_a_fenced_void_does_nothing():
    text = "\n".join((MALFORMED, "```", void(997, "E-995"), "```"))
    assert any(p.startswith("E-995") for p in R.heldout_token_problems(text))


def test_the_void_tokens_grammar():
    text = "\n".join((void(997, "E-995"), "| E-998 | 2026-11-20 | heldout-void: 995 -- no id | x |"))
    assert [(t.row, t.get("target")) for t in R.heldout_tokens(text, "void")] == [("E-997", "E-995")]
    assert [p.split(" ")[0] for p in R.heldout_token_problems(text)] == ["E-998"]


# --------------------------------------------------------------------------------- P10, P9, Y6


@pytest.mark.parametrize("finalists", [False, True])
@pytest.mark.parametrize("purpose", ["stage_C_judgement", "stage_D_scorecard", "heldout_test"])
def test_p10_an_f14_like_family_reads_no_held_out_date(tree, finalists, purpose):
    if finalists:
        H.add_rows(tree, H.finalists(920, "F-14", H.F14_TEXT, H.LIST14))
    e = H.refused(1, H.read, tree, declaration=H.F14, purpose=purpose)
    assert ("search years" if purpose != "heldout_test" else "one held-out declaration") in str(e)
    assert H.lines(tree, seed=True) == []


def test_p10_an_f03_like_family_reads_only_the_search_years(tree):
    D._pin(tree, "prereg/F-03_opening_timing.md", D.F03_LIKE, 960, 961)
    for purpose in ("stage_C_judgement", *R.HELDOUT_PURPOSES):
        H.refused(1, H.read, tree, declaration="prereg/F-03_opening_timing.md", purpose=purpose)
    assert not H.read(tree, declaration="prereg/F-03_opening_timing.md", start="2020-01-02",
                      end="2023-12-29").judged


def test_p10_the_held_out_declaration_reads_only_its_held_out_purposes(tree):
    rel = "prereg/F-96_heldout_test_NQ.md"
    text = VR.heldout_text("F-96", line="- **Judged-block reads:** `heldout_test`, `heldout_stress`, "
                                        "`stage_C_judgement`\n")
    D._pin(tree, rel, text, 960, 961)
    assert "search years" in str(H.refused(1, H.read, tree, declaration=rel, purpose="stage_C_judgement"))
    assert H.read(tree, declaration=rel, purpose="heldout_test").judged


@pytest.mark.parametrize("purpose", ["heldout_test", "heldout_stress"])      # Q-194f: Z6
def test_p9_no_repeat_row_for_the_held_out_declaration(tree, monkeypatch, purpose):
    VR.declare(tree)
    H.read(tree, declaration=VR.HT_PATH, purpose=purpose)
    VR.append_rows(tree, f"| E-970 | 2026-11-20 | **another read of `{VR.HT_PATH}`** | x |")
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    e = H.refused(1, H.read, tree, declaration=VR.HT_PATH, purpose=purpose, repeat="E-970")
    assert "no repeat row" in str(e)
    assert len(H.lines(tree, seed=True)) == 1


def test_y6_a_misnamed_marked_file_beside_the_real_one_blocks_it(tree):
    VR.declare(tree)
    (tree / "prereg" / "F-97_joint.md").write_text(VR.heldout_text("F-97: misnamed"), encoding="utf-8")
    e = H.refused(1, H.read, tree, declaration=VR.HT_PATH, purpose="heldout_test")
    assert "prereg/F-97_joint.md" in str(e) and "one per market" in str(e)


# ------------------------------------------------------------------------------------------ NOTE-3, NOTE-6


def test_the_reader_states_a_later_window_needs_its_own_rule():
    assert "A later window needs its own rule" in " ".join(R.__doc__.split())


def test_an_oserror_from_git_fails_closed_by_name(declared, monkeypatch):
    VR.settle(declared, [declared / H.BARS])
    real = R._git

    def broken(repo, *args):
        if "log" in args and "-p" in args:                   # Q-194f: the walk of every commit's patch
            raise OSError("the command line is too long")
        return real(repo, *args)

    monkeypatch.setattr(R, "_git", broken)
    e = H.refused(3, D.reg, declared)
    assert "git could not be asked" in str(e) and "OSError" in str(e) and "failing closed" in str(e)
    assert H.lines(declared) == []
