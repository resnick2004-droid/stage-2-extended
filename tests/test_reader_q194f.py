"""Q-194f (the lead's rulings on the red team's `READER_Q194e_2026-11-22`), on Q-158's synthetic tree
(`tests/test_reader_heldout.py`'s helpers; `tests/heldout_verdict_rows.py`'s F-98; nothing real is read).

* **MINOR-1, the exact added line:** "the commits that add the verdict row" are those whose patch against some parent
  holds `+<row>` (`git log --full-history -m -p`), never a count of the text -- the red team's Q2b (a premature verdict
  laundered by an edit in place that keeps the count) is refused; a commit that copies the row and its ledger line
  onto a branch that does not descend from the read is a hit too, and refuses (the red team's Z4);
* **MINOR-2, the void completed:** (a) a void clears a fenced token row's problem (the row stays fenced); (b) a void
  closes a stray fence wherever it opened -- after prose, a blank line (Z7) or an earlier closed fence -- named by the
  nearest row above it; (c) every void naming a row counts if placed after it (Q5; `setdefault`'s bug); (d) a
  malformed row carrying a pin may be voided, and its pin still pins (Q6; Z5's guard dropped, its return killed);
* **NOTE-3:** a closing fence appended after a void-closed fence (the renderers' close) keeps the log unlocked, and
  the rows between the void and it stay counted; the docstring states what the renderers show;
* **NOTE-4, NOTE-6:** the docstring's void wording, and that one run per purpose means a crash spends the test;
* **Z6:** `heldout_stress`'s repeat is refused as `heldout_test`'s is (`test_reader_q194e.py`'s P9, parametrized).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from extended import reader as R
import heldout_verdict_rows as VR
import test_reader_heldout as H
import test_reader_q194d as D
from test_reader_heldout import tree  # noqa: F401 -- the fixture
from test_reader_q194d import declared  # noqa: F401 -- the fixture

DAY = "2026-11-22"


def g(t: Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=t, capture_output=True, text=True, check=True).stdout.strip()


def void(row: int, target: str, why: str = "a correction") -> str:
    return f"| E-{row} | {DAY} | heldout-void: {target} -- {why} | x |"


def row(n: int, text: str = "a row") -> str:
    return f"| E-{n} | {DAY} | {text} | x |"


MALFORMED = row(995, "**Held-out verdict:** NQ F-98 passed (prose)")


# ----------------------------------------------------------------------------------- MINOR-1: the exact added line


def test_q2b_a_premature_verdict_laundered_by_an_edit_that_keeps_the_count_is_refused(declared):
    VR.declare(declared)
    quote = f"| E-970 | 2026-11-19 | a draft, quoting: {VR.VERDICT_ROW} | x |"
    VR.append_rows(declared, quote)
    q = D.head(declared)
    p = declared / "DECISIONS.md"
    p.write_bytes(p.read_text(encoding="utf-8").replace(quote, VR.VERDICT_ROW).encode("utf-8"))
    g(declared, "commit", "-q", "-am", "X: the verdict, before any read was committed")
    x = D.head(declared)
    D.put_lines(declared, [D.forged(q)])
    VR.commit_verdict(declared, f"| E-984 | 2026-11-19 | the verdict again, quoted: {VR.VERDICT_ROW} | x |")
    assert x in R._verdict_commits(declared, VR.VERDICT_ROW), "X adds the exact line: a hit, whatever the count"
    D.gate_refuses(declared)                                    # X holds no ledger


def test_z4_a_hit_that_does_not_descend_from_the_read_refuses(declared):
    base = D.head(declared)                                     # before F-98 is declared
    c0 = VR.declare(declared)
    D.put_lines(declared, [D.forged(c0)])
    l_commit = VR.commit_verdict(declared, VR.VERDICT_ROW)      # L: the genuine verdict (alone it counts: q194d's
                                                                # test_the_same_line_from_an_ancestor_commit_is_admitted)
    ledger = (declared / VR.LEDGER).read_text(encoding="utf-8")
    g(declared, "checkout", "-q", "-b", "copy", base)
    (declared / "results").mkdir(exist_ok=True)
    (declared / VR.LEDGER).write_text(ledger, encoding="utf-8")
    VR._append(declared, [VR.VERDICT_ROW])                      # S: the row and the line copied off the read's line,
    g(declared, "add", "DECISIONS.md")                          # dated later, so L is the first hit and S a later one
    g(declared, "add", "-f", VR.LEDGER)
    later = {**os.environ, "GIT_AUTHOR_DATE": "2030-01-01T00:00:00", "GIT_COMMITTER_DATE": "2030-01-01T00:00:00"}
    subprocess.run(["git", "commit", "-q", "-m", "S"], cwd=declared, check=True, env=later, capture_output=True)
    s = D.head(declared)
    g(declared, "checkout", "-q", "master")
    g(declared, "merge", "-q", "-s", "ours", "--no-edit", "copy")
    hits = R._verdict_commits(declared, VR.VERDICT_ROW)
    assert hits[0] == l_commit and s in hits[1:], "L first, S later"
    D.gate_refuses(declared)                                    # c0 is no ancestor of S: every hit is checked


# ---------------------------------------------------------------------------------- MINOR-2: the void completed


def test_a_a_fenced_token_row_voided(declared):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, row(990), "```", VR.verdict_row(991), "```")
    D.hygiene_refuses(D.reg, declared)
    VR.append_rows(declared, void(992, "E-991", "an example quoted in a fence"))
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.heldout_token_problems(text) == []
    assert "E-991" not in [t.row for t in R.heldout_tokens(text, "verdict")], "still fenced: no row"
    assert dict(D.reg(declared).heldout)["test_verdict"] == "E-982"


@pytest.mark.parametrize("between", [("",), ("", "Notes on the table, in prose."), ("```", "code", "```"),
                                     ("~~~", row(989, "a fenced example row: no row"), "~~~")])
def test_b_a_stray_fence_wherever_it_opened_is_closed_by_a_void_of_the_row_above(declared, between):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, row(990), *between, "```", row(991, "hidden"))
    assert "never closed" in D.hygiene_refuses(D.reg, declared)
    VR.append_rows(declared, void(992, "E-990", "the stray fence below E-990"), row(993, "after"))
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.heldout_token_problems(text) == []
    assert R.decision_row(text, "E-991") is None and R.decision_row(text, "E-993") is not None
    assert dict(D.reg(declared).heldout)["test_verdict"] == "E-982"


def test_b_a_void_of_another_row_closes_nothing():
    text = "\n".join((row(989), row(990), "```", void(991, "E-989", "not the row above the fence")))
    assert any("never closed" in p for p in R.heldout_token_problems(text))


def test_c_every_later_void_counts_whatever_an_earlier_one_says():
    text = "\n".join((void(994, "E-995", "a typo: meant E-993"), MALFORMED, void(996, "E-995", "the real void")))
    assert R.heldout_token_problems(text) == []
    assert R.heldout_token_problems("\n".join((void(994, "E-995"), MALFORMED)))


def test_d_a_malformed_row_with_a_pin_is_voided_and_still_pins():
    pin = row(995, f"**Held-out finalists:** F-98, `{VR.HT_PATH}` sha256 `{VR.HT_SHA}`")
    assert any(p.startswith("E-995") for p in R.heldout_token_problems(pin))
    text = "\n".join((pin, void(996, "E-995", "prose that looked like a token")))
    assert R.heldout_token_problems(text) == []
    assert R.pins(text) == {VR.HT_PATH: {VR.HT_SHA}}, "the void never removes the pin"


# -------------------------------------------------------------------------------------- NOTE-3: the renderers


def test_note3_the_renderers_closing_fence_after_a_void_keeps_the_log_unlocked(declared):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, row(985), "```", row(986, "hidden"))
    VR.append_rows(declared, void(987, "E-985", "the stray fence"), row(988, "between"))
    VR.append_rows(declared, "```", row(989, "after the renderers' close"))
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.heldout_token_problems(text) == []
    assert R.decision_row(text, "E-986") is None
    assert R.decision_row(text, "E-988") is not None, "a row counted before the close stays counted"
    assert R.decision_row(text, "E-989") is not None
    assert dict(D.reg(declared).heldout)["test_verdict"] == "E-982"


def test_note3_only_a_bare_closer_of_the_same_fence_is_its_close():
    for after in ("~~~", "```python", "``"):                    # another character, an info string, too short
        text = "\n".join((row(985), "```", void(987, "E-985"), after, row(988)))
        if after == "``":
            assert R.heldout_token_problems(text) == [], "no fence-like line at all: nothing to absorb"
        else:
            assert any("never closed" in p for p in R.heldout_token_problems(text)), after


def test_note3_a_second_fence_after_the_close_is_a_new_fence():
    text = "\n".join((row(985), "```", void(987, "E-985"), "```", row(988), "```"))
    assert any("never closed" in p for p in R.heldout_token_problems(text))


# ------------------------------------------------------------------------------------------------ the docstring


def test_the_reader_states_the_void_the_renderers_and_a_crash():
    doc = " ".join(R.__doc__.split())
    for phrase in ("A void never removes a token or a pin", "names the row the stray fence follows, whatever that row is",
                   "still show the rows after a stray fence as code", "One run per purpose means a crash spends the test",
                   "never judged by a count of the text"):
        assert phrase in doc, phrase
