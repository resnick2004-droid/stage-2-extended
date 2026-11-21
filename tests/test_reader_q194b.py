"""Q-194b (the lead's ruling on O-7's RD-10 C3 and the red team's L-1 of template v3): a `registered_design` read of
any held-out date waits for the joint held-out test's verdict row, on Q-158's synthetic tree
(`tests/test_reader_heldout.py`'s helpers; `tests/heldout_verdict_rows.py`'s rows; nothing real is read).

* **before the verdict, refused** -- whatever row declares the read (a `heldout-read` token naming the designs and
  the script): the whole seal (the holiday gap alone, a span crossing into 2024, the last day alone), under rule 3,
  naming the purpose and the declaration, before rule 3's own checks, writing no ledger line;
* **the verdict token** is `heldout-verdict: F-NN @ <its LF sha256> -- ...` at the start of a row's third cell (the
  held-out template names the verdict row and no token form, so the lead's form); it counts only for a declaration
  pinned at that sha256, newer than that declaration's finalists' token at the same sha256 (itself newer than the
  pin), and newer than the read's window's opening row. A quoted, emphasised or misplaced token, one older than the
  finalists' row or than a window opened after it, one for an unpinned sha, one with no finalists' row or a
  finalists' row of other bytes, and the market's `heldout-verdict: NQ F-NN` form (rule 4's) do not count;
* **after the verdict, admitted** -- rule 3 then stands as before (its token, its script, a clean run, one run a
  row), and the ledger line records the verdict row (`test_verdict`);
* **untouched**: a registered design's search-year read (RD-10's (c), 2020-01-02 to 2023-12-29) needs no verdict, no
  token, no clean run; E-247 rm-4's `identity` reads need no verdict;
* the token's grammar: the form is a held-out token (not flagged as malformed); a near-form is flagged.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from extended import reader as R
import heldout_verdict_rows as VR
import test_reader_heldout as H
from test_reader_heldout import tree  # noqa: F401 -- the fixture

READ_ROW = ("| E-940 | 2026-11-18 | heldout-read: P-14,P-16 by scripts/replay.py -- P-14 and P-16 replayed on the "
            "held-out years | x |")


def commit_file(t: Path, rel: str, text: str) -> None:
    (t / rel).parent.mkdir(parents=True, exist_ok=True)
    (t / rel).write_bytes(text.encode("utf-8"))
    H.git(t, "add", "-A")
    H.git(t, "commit", "-q", "-m", f"add {rel}")


@pytest.fixture
def declared(tree, monkeypatch):
    """A readings script as the process's and a lead's row declaring its held-out read -- but no verdict row."""
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    H.add_rows(tree, READ_ROW)
    return tree


def before_verdict(t: Path, **kw) -> R.HeldOutRefused:
    e = H.refused(3, H.rd_read, t, "E-940", ("P-14", "P-16"), **kw)
    msg = str(e)
    assert "held-out test's verdict" in msg and "Q-194b" in msg, msg
    assert "'registered_design'" in msg and "E-940" in msg, "the refusal names the purpose and the declaration"
    assert H.lines(t) == [], "a refused read writes no ledger line"
    return e


def verdict(row: int, fid: str = VR.HT_ID, sha: str = VR.HT_SHA) -> str:
    return f"| E-{row} | 2026-11-19 | heldout-verdict: {fid} @ {sha} -- the joint held-out test's verdict | x |"


# ------------------------------------------------------------------------------------------- before the verdict


@pytest.mark.parametrize("start,end", [("2020-01-02", "2026-07-16"),    # the whole window (the declared read)
                                       ("2023-12-30", "2024-01-01"),    # the holiday gap alone: under the seal
                                       ("2023-12-28", "2024-01-02"),    # a span crossing into the held-out years
                                       ("2026-07-16", "2026-07-16")])   # the last held-out day alone
def test_a_declared_held_out_read_is_refused_before_the_verdict(declared, start, end):
    before_verdict(declared, start=start, end=end)


def test_the_held_out_tests_pin_and_finalists_alone_are_not_its_verdict(declared):
    H.add_rows(declared, VR.PIN_ROW, VR.FINALISTS_ROW)
    before_verdict(declared)


def test_the_markets_verdict_form_is_rule_4s_not_this(declared):
    H.add_rows(declared, VR.PIN_ROW, VR.FINALISTS_ROW,
               f"| E-982 | 2026-11-19 | heldout-verdict: NQ {VR.HT_ID} -- the market's form | x |")
    before_verdict(declared)


def test_the_verdict_gate_comes_before_rule_3s_own_checks(tree, monkeypatch):
    """A row without a read token, outside a clean run: still the verdict's refusal first."""
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    e = H.refused(3, H.rd_read, tree, "E-904", "P-14")
    assert "held-out test's verdict" in str(e) and "E-904" in str(e)
    monkeypatch.delenv("S2X_CLEAN_RUN")
    assert "held-out test's verdict" in str(H.refused(3, H.rd_read, tree, "E-904", "P-14"))
    assert H.lines(tree) == []


def test_the_registered_checks_still_come_first(declared):
    with pytest.raises(R.JudgedBlockSealed, match="not a registered design") as info:
        H.rd_read(declared, "E-940", "P-17")
    assert not isinstance(info.value, R.HeldOutRefused)
    with pytest.raises(R.JudgedBlockSealed, match="no decision row") as info:
        H.rd_read(declared, "E-999", "P-14")
    assert not isinstance(info.value, R.HeldOutRefused)


# ---------------------------------------------------------------------------------------------- what counts


@pytest.mark.parametrize("rows", [
    # quoted, emphasised, later in the cell
    (VR.PIN_ROW, VR.FINALISTS_ROW,
     f"| E-982 | 2026-11-19 | `heldout-verdict: {VR.HT_ID} @ {VR.HT_SHA}` -- quoted | x |"),
    (VR.PIN_ROW, VR.FINALISTS_ROW,
     f"| E-982 | 2026-11-19 | **heldout-verdict: {VR.HT_ID} @ {VR.HT_SHA} -- bold** | x |"),
    (VR.PIN_ROW, VR.FINALISTS_ROW,
     f"| E-982 | 2026-11-19 | the verdict; heldout-verdict: {VR.HT_ID} @ {VR.HT_SHA} -- later | x |"),
    # older than the finalists' row; older than the pin (with its finalists' row after both)
    (VR.PIN_ROW, verdict(980), VR.FINALISTS_ROW),
    (verdict(979), VR.PIN_ROW, VR.FINALISTS_ROW),
    # for a sha not pinned; with no finalists' row; with a finalists' row of other bytes; for another declaration
    (VR.PIN_ROW, VR.FINALISTS_ROW, verdict(982, sha="5" * 64)),
    (VR.PIN_ROW, verdict(982)),
    (VR.PIN_ROW, f"| E-981 | 2026-11-19 | heldout-finalists: {VR.HT_ID} @ {'5' * 64} list {VR.HT_LIST} -- other | x |",
     verdict(982)),
    (VR.PIN_ROW, VR.FINALISTS_ROW, verdict(982, fid="F-97")),
    # a finalists' row older than the pin
    (f"| E-979 | 2026-11-19 | heldout-finalists: {VR.HT_ID} @ {VR.HT_SHA} list {VR.HT_LIST} -- early | x |",
     VR.PIN_ROW, verdict(982)),
])
def test_a_quoted_older_or_unbacked_token_does_not_count(declared, rows):
    H.add_rows(declared, *rows)
    before_verdict(declared)


def test_a_verdict_older_than_its_reads_window_does_not_count(declared):
    H.add_rows(declared, *VR.VERDICT_ROWS,
               "| E-990 | 2026-11-20 | heldout-window: NQ 2024-01-02 to 2026-07-16 -- a window re-opened | x |")
    before_verdict(declared)
    a = H.rd_read(declared, "E-940", "P-14", end="2023-12-29")          # the search years: untouched
    assert not a.judged
    H.add_rows(declared, f"| E-991 | 2026-11-20 | heldout-finalists: {VR.HT_ID} @ {VR.HT_SHA} list {VR.HT_LIST} -- "
                         "the next joint list | x |", verdict(992))
    a = H.rd_read(declared, "E-940", ("P-14", "P-16"))
    assert dict(a.heldout)["test_verdict"] == "E-992"


# ------------------------------------------------------------------------------------------- after the verdict


def test_after_the_verdict_the_declared_read_is_admitted_and_ledgered(declared, monkeypatch):
    H.add_rows(declared, *VR.VERDICT_ROWS)
    a = H.rd_read(declared, "E-940", ("P-14", "P-16"))
    assert a.judged and a.ledgered and a.kind == "registered_design"
    assert dict(a.heldout) == {"read_row": "E-940", "test_verdict": "E-982"}
    assert H.lines(declared)[0]["heldout"] == {"read_row": "E-940", "test_verdict": "E-982"}
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")                 # rule 3 as before: one run a row
    assert "one row, one run" in str(H.refused(3, H.rd_read, declared, "E-940", "P-14"))


def test_after_the_verdict_rule_3_stands_as_before(tree, monkeypatch):
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    H.add_rows(tree, *VR.VERDICT_ROWS)
    assert "earlier reads stay valid" in str(H.refused(3, H.rd_read, tree, "E-904", "P-14"))   # no read token
    H.add_rows(tree, READ_ROW)
    monkeypatch.delenv("S2X_CLEAN_RUN")
    assert "clean run" in str(H.refused(3, H.rd_read, tree, "E-940", "P-14"))
    assert H.lines(tree) == []


# ----------------------------------------------------------------------------------------------- untouched


def test_a_search_year_registered_read_needs_no_verdict(declared, monkeypatch):
    """RD-10's (c): a registered design's read of 2020-01-02 to 2023-12-29 -- no verdict, token or clean run."""
    monkeypatch.delenv("S2X_CLEAN_RUN")
    monkeypatch.delenv("S2X_RUN_ID")
    for declaration in ("E-940", "E-904"):
        a = H.rd_read(declared, declaration, ("P-14", "P-16"), end="2023-12-29")
        assert not a.judged and not a.ledgered and a.heldout is None
    assert not (declared / "results").exists()


def test_rm4s_identity_reads_need_no_verdict(tree, monkeypatch):
    commit_file(tree, "identity/repro_id.py", "print('identity HOLDS')\n")
    monkeypatch.setattr(R, "_main_script", lambda: tree / "identity" / "repro_id.py")
    assert not R.heldout_tokens((tree / "DECISIONS.md").read_text(encoding="utf-8"), "test_verdict")
    a = R.authorise_engine_read("2020-01-02", "2026-07-16", purpose="identity", declaration="E-905",
                                files=[tree / H.BARS], what="q194b identity", repo=tree)
    assert a.judged and a.kind == "identity" and a.ledgered and a.heldout is None


# ---------------------------------------------------------------------------------------------------- grammar


def test_the_verdict_tokens_grammar():
    text = "\n".join((*VR.VERDICT_ROWS,
                      f"| E-983 | 2026-11-19 | heldout-verdict: {VR.HT_ID} @ {VR.HT_SHA[:63]} -- short sha | x |",
                      f"| E-984 | 2026-11-19 | heldout-verdict: {VR.HT_ID} @ {VR.HT_SHA} --  | x |"))
    toks = R.heldout_tokens(text, "test_verdict")
    assert [(t.row, t.get("decl"), t.get("sha")) for t in toks] == [("E-982", VR.HT_ID, VR.HT_SHA)]
    assert not R.heldout_tokens(text, "verdict"), "the market's form is another kind"
    flagged = sorted({p.split(" ")[0] for p in R.heldout_token_problems(text)})
    assert flagged == ["E-983", "E-984"]
    assert R.heldout_token_problems("\n".join(VR.VERDICT_ROWS)) == []
