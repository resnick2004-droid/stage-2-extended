"""Q-194b (the lead's ruling on O-7's RD-10 C3 and the red team's L-1 of template v3), in Q-194c's form: a
`registered_design` read of any held-out date waits for the joint held-out test's verdict row, on Q-158's synthetic
tree (`tests/test_reader_heldout.py`'s helpers; `tests/heldout_verdict_rows.py`'s seeded joint test; nothing real is
read).

* **before the verdict, refused** -- whatever row declares the read (a `heldout-read` token naming the designs and
  the script): the whole seal (the holiday gap alone, a span crossing into 2024, the last day alone), under rule 3,
  naming the purpose and the declaration, before rule 3's own checks, writing no ledger line; also with the joint
  test's pin and finalists' row and its read ledgered but no verdict row yet;
* **the one verdict form** (Q-194c) is `heldout-verdict: <MARKET> F-NN @ <its LF sha256> -- ...`; the old unbound
  forms (`heldout-verdict: NQ F-NN -- ...`, `heldout-verdict: F-NN @ <sha> -- ...`) and a quoted, emphasised or
  misplaced token count for nothing; the binding itself (the read behind the verdict, places, windows, fences) is
  `tests/test_reader_q194c.py`'s;
* **after the verdict, admitted** -- rule 3 then stands as before (its token, its script, a clean run, one run a
  row), and the ledger line records the verdict row (`test_verdict`);
* **untouched**: a registered design's search-year read (RD-10's (c), 2020-01-02 to 2023-12-29) needs no verdict, no
  token, no clean run; E-247 rm-4's `identity` reads need no verdict.
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
    assert "no verdict row counts" in msg and "Q-194b" in msg, msg
    assert "'registered_design'" in msg and "E-940" in msg, "the refusal names the purpose and the declaration"
    assert H.lines(t) == [], "a refused read writes no ledger line"
    return e


# ------------------------------------------------------------------------------------------- before the verdict


@pytest.mark.parametrize("start,end", [("2020-01-02", "2026-07-16"),    # the whole window (the declared read)
                                       ("2023-12-30", "2024-01-01"),    # the holiday gap alone: under the seal
                                       ("2023-12-28", "2024-01-02"),    # a span crossing into the held-out years
                                       ("2026-07-16", "2026-07-16")])   # the last held-out day alone
def test_a_declared_held_out_read_is_refused_before_the_verdict(declared, start, end):
    before_verdict(declared, start=start, end=end)


def test_the_joint_tests_read_without_its_verdict_row_is_not_its_verdict(declared):
    VR.settle(declared, [declared / H.BARS], verdict=False)
    before_verdict(declared)


@pytest.mark.parametrize("row", [
    f"| E-982 | 2026-11-19 | heldout-verdict: NQ {VR.HT_ID} -- the market form without the sha | x |",
    f"| E-982 | 2026-11-19 | heldout-verdict: {VR.HT_ID} @ {VR.HT_SHA} -- Q-194b's form without the market | x |",
    f"| E-982 | 2026-11-19 | `heldout-verdict: NQ {VR.HT_ID} @ {VR.HT_SHA}` -- quoted | x |",
    f"| E-982 | 2026-11-19 | **heldout-verdict: NQ {VR.HT_ID} @ {VR.HT_SHA} -- bold** | x |",
    f"| E-982 | 2026-11-19 | the verdict; heldout-verdict: NQ {VR.HT_ID} @ {VR.HT_SHA} -- later | x |",
])
def test_an_old_quoted_or_misplaced_verdict_form_does_not_count(declared, row):
    VR.settle(declared, [declared / H.BARS], verdict=False)
    VR.commit_verdict(declared, row)
    assert not R.heldout_tokens(row), "never a token"
    if R.heldout_token_problems(row):                       # Q-194d: a malformed token fails every judged read
        with pytest.raises(R.JudgedBlockSealed, match="hygiene") as info:
            H.rd_read(declared, "E-940", ("P-14", "P-16"))
        assert not isinstance(info.value, R.HeldOutRefused) and "E-982" in str(info.value)
    else:
        before_verdict(declared)


def test_the_verdict_gate_comes_before_rule_3s_own_checks(tree, monkeypatch):
    """A row without a read token, outside a clean run: still the verdict's refusal first."""
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    e = H.refused(3, H.rd_read, tree, "E-904", "P-14")
    assert "no verdict row counts" in str(e) and "E-904" in str(e)
    monkeypatch.delenv("S2X_CLEAN_RUN")
    assert "no verdict row counts" in str(H.refused(3, H.rd_read, tree, "E-904", "P-14"))
    assert H.lines(tree) == []


def test_the_registered_checks_still_come_first(declared):
    with pytest.raises(R.JudgedBlockSealed, match="not a registered design") as info:
        H.rd_read(declared, "E-940", "P-17")
    assert not isinstance(info.value, R.HeldOutRefused)
    with pytest.raises(R.JudgedBlockSealed, match="no decision row") as info:
        H.rd_read(declared, "E-999", "P-14")
    assert not isinstance(info.value, R.HeldOutRefused)


# ------------------------------------------------------------------------------------------- after the verdict


def test_after_the_verdict_the_declared_read_is_admitted_and_ledgered(declared, monkeypatch):
    VR.settle(declared, [declared / H.BARS])
    a = H.rd_read(declared, "E-940", ("P-14", "P-16"))
    assert a.judged and a.ledgered and a.kind == "registered_design"
    assert dict(a.heldout) == {"read_row": "E-940", "test_verdict": "E-982"}
    assert H.lines(declared)[0]["heldout"] == {"read_row": "E-940", "test_verdict": "E-982"}
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")                 # rule 3 as before: one run a row
    assert "one row, one run" in str(H.refused(3, H.rd_read, declared, "E-940", "P-14"))


def test_after_the_verdict_rule_3_stands_as_before(tree, monkeypatch):
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    VR.settle(tree, [tree / H.BARS])
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
    assert not R.heldout_tokens((tree / "DECISIONS.md").read_text(encoding="utf-8"), "verdict")
    a = R.authorise_engine_read("2020-01-02", "2026-07-16", purpose="identity", declaration="E-905",
                                files=[tree / H.BARS], what="q194b identity", repo=tree)
    assert a.judged and a.kind == "identity" and a.ledgered and a.heldout is None


# ---------------------------------------------------------------------------------------------------- grammar


def test_the_verdict_tokens_grammar():
    text = "\n".join((VR.PIN_ROW, VR.FINALISTS_ROW, VR.VERDICT_ROW,
                      f"| E-983 | 2026-11-19 | heldout-verdict: NQ {VR.HT_ID} @ {VR.HT_SHA[:63]} -- short sha | x |",
                      f"| E-984 | 2026-11-19 | heldout-verdict: NQ {VR.HT_ID} @ {VR.HT_SHA} --  | x |",
                      f"| E-985 | 2026-11-19 | heldout-verdict: {VR.HT_ID} @ {VR.HT_SHA} -- no market | x |",
                      f"| E-986 | 2026-11-19 | heldout-verdict: NQ {VR.HT_ID} -- no sha | x |"))
    toks = R.heldout_tokens(text, "verdict")
    assert [(t.row, t.get("market"), t.get("decl"), t.get("sha"), t.pos) for t in toks] == [
        ("E-982", "NQ", VR.HT_ID, VR.HT_SHA, 2)]
    flagged = sorted({p.split(" ")[0] for p in R.heldout_token_problems(text)})
    assert flagged == ["E-983", "E-984", "E-985", "E-986"]
    assert R.heldout_token_problems("\n".join((VR.PIN_ROW, VR.FINALISTS_ROW, VR.VERDICT_ROW))) == []
