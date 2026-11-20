"""Q-194: the held-out reader's rule 1 binds every purpose a family reads the held-out years under (the red team's M-2
of `docs/reviews/TEMPLATE_V2_FULL_2026-11-20.md`), on Q-158's synthetic tree (`tests/test_reader_heldout.py`'s
helpers; nothing real is read: synthetic declarations, synthetic decision rows, stand-in data files never parsed).

* **the hole closed:** a pinned family declaration whose `Judged-block reads:` line names any purpose that is not a
  choice (`stage_Z_anything`, `stage_C_judgement`) is refused under rule 1 with no finalists' token for its own id and
  its own sha256, newer than its pin -- also for a read of the holiday gap alone, and for a token of another
  declaration, of other bytes, or older than the pin; each refusal names the purpose and the declaration; a refused
  read writes no ledger line;
* **the token honours it:** the same declaration with its token is admitted and its ledger line carries the
  finalists' row, as a `heldout_test` read's does;
* **`heldout_test` and `heldout_stress` exactly as before:** refused without the token, admitted with it, the same
  `heldout` field;
* **E-247's rm-4 untouched:** a registered reproduction identity (purpose `identity`, its decision row) reads the
  whole window with no finalists' token anywhere; a registered design's re-read is rule 3's alone; a family file
  cannot borrow the `identity` purpose;
* **rule 2 is not spent by a refused read:** after a family's refused read another family's admitted read is not
  refused under rule 2; and where both rules apply rule 1 refuses first;
* **a described reading's other purposes stay rule 4's**, not rule 1's;
* **the later refusals of a family's read name the purpose and the declaration** (rules 2 and 4).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from extended import reader as R
import test_reader_heldout as H
from test_reader_heldout import scripted, tree  # noqa: F401 -- the fixtures

#: a family whose line names an arbitrary purpose that is not a choice (the defect's case)
F16 = "prereg/F-16_other.md"
F16_TEXT = "# F-16: a synthetic search naming another purpose (Q-194's tests)\n\n" \
           "- **Judged-block reads:** `stage_Z_anything`, `scorecard_final`\n"
F16_PIN = f"| E-910 | 2026-11-18 | **F-16 declared**, `{F16}` sha256 `{H.sha_lf(F16_TEXT)}` | test |"
#: a family naming `identity` on its line: the purpose stays the identities' (an E- row), never a family's
F17 = "prereg/F-17_borrow.md"
F17_TEXT = "# F-17\n\n- **Judged-block reads:** `identity`, `stage_Z_anything`\n"
F17_PIN = f"| E-911 | 2026-11-18 | **F-17 declared**, `{F17}` sha256 `{H.sha_lf(F17_TEXT)}` | test |"
LIST16 = "6" * 64
OTHER = ("stage_Z_anything", "scorecard_final")


def commit_file(t: Path, rel: str, text: str) -> None:
    (t / rel).parent.mkdir(parents=True, exist_ok=True)
    (t / rel).write_bytes(text.encode("utf-8"))
    H.git(t, "add", "-A")
    H.git(t, "commit", "-q", "-m", f"add {rel}")


@pytest.fixture
def t16(tree):
    commit_file(tree, F16, F16_TEXT)
    commit_file(tree, F17, F17_TEXT)
    H.add_rows(tree, F16_PIN, F17_PIN)
    return tree


def names_both(e: Exception, purpose: str, ref: str) -> None:
    msg = str(e)
    assert repr(purpose) in msg and ref in msg, msg


# ------------------------------------------------------------------------------------------------- the hole closed


@pytest.mark.parametrize("purpose", OTHER)
def test_an_arbitrary_non_choice_purpose_is_refused_without_its_token(t16, purpose):
    assert not R._choice_purpose(purpose)
    assert purpose in R.declared_purposes(F16_TEXT), "the line names it: the seal's own checks pass"
    e = H.refused(1, H.read, t16, declaration=F16, purpose=purpose)
    assert "no decision row carries a finalists' token for F-16" in str(e)
    names_both(e, purpose, F16)
    assert H.lines(t16) == [], "a refused read writes nothing"


def test_a_familys_judgement_purpose_is_refused_without_its_token(tree):
    """The reader's own example purpose, `stage_C_judgement`, on F-13's line (the red team's case)."""
    e = H.refused(1, H.read, tree, purpose="stage_C_judgement")
    names_both(e, "stage_C_judgement", H.F13)
    assert H.lines(tree) == []


@pytest.mark.parametrize("start,end", [("2023-12-30", "2024-01-01"),      # the holiday gap alone: under the seal
                                       ("2023-12-28", "2024-01-02"),      # a span crossing into the held-out years
                                       ("2026-07-16", "2026-07-16")])     # the last held-out day alone
def test_any_held_out_date_binds_rule1(t16, start, end):
    H.refused(1, H.read, t16, declaration=F16, purpose="stage_Z_anything", start=start, end=end)
    assert H.lines(t16) == []


@pytest.mark.parametrize("row,why", [
    (H.finalists(920, "F-13", H.F13_TEXT, H.LIST13), "no decision row carries a finalists' token for F-16"),
    (H.finalists(920, "F-16", H.F13_TEXT, LIST16), "not prereg/F-16_other.md's sha256"),
    (H.finalists(909, "F-16", F16_TEXT, LIST16), "precede its pin"),
    ("| E-920 | 2026-11-18 | `heldout-finalists: F-16 @ " + H.sha_lf(F16_TEXT) + " list " + LIST16
     + "` -- quoted | x |",
     "no decision row carries"),
])
def test_an_arbitrary_purpose_needs_its_own_token_for_its_own_hash(t16, row, why):
    H.add_rows(t16, row)
    for purpose in OTHER:
        e = H.refused(1, H.read, t16, declaration=F16, purpose=purpose)
        assert why in str(e)
        names_both(e, purpose, F16)
    assert H.lines(t16) == []


def test_the_same_declaration_with_its_token_is_honoured(t16):
    H.add_rows(t16, H.finalists(920, "F-16", F16_TEXT, LIST16))
    a = H.read(t16, declaration=F16, purpose="stage_Z_anything")
    want = {"market": "NQ", "window": "E-208", "finalists": "E-920", "finalists_list_sha256": LIST16}
    assert a.judged and a.ledgered and a.kind == "family" and dict(a.heldout) == want
    H.read(t16, declaration=F16, purpose="scorecard_final")           # one run, its other purpose
    recs = H.lines(t16)
    assert [r["purpose"] for r in recs] == list(OTHER) and all(r["heldout"] == want for r in recs)
    assert R.read_ledger(t16 / "results" / "read_ledger.jsonl") == recs


# --------------------------------------------------------------------------------- the held-out purposes, unchanged


@pytest.mark.parametrize("purpose", R.HELDOUT_PURPOSES)
def test_the_held_out_purposes_behave_as_before(tree, purpose):
    assert R.HELDOUT_PURPOSES == ("heldout_test", "heldout_stress")
    e = H.refused(1, H.read, tree, purpose=purpose)
    assert "no decision row carries a finalists' token for F-13" in str(e)
    H.add_rows(tree, H.finalists(920, "F-13", H.F13_TEXT, H.LIST13))
    a = H.read(tree, purpose=purpose)
    assert dict(a.heldout) == {"market": "NQ", "window": "E-208", "finalists": "E-920",
                               "finalists_list_sha256": H.LIST13}
    if purpose in R.declared_purposes(H.RD7_TEXT):                    # RD-07's line names heldout_test only
        assert "described reading" in str(H.refused(1, H.read, tree, declaration=H.RD7, purpose=purpose))


def test_a_described_readings_other_purpose_stays_rule_4s(tree):
    """Rule 1 binds an RD's held-out purposes only; its other purposes wait for the verdict (rule 4), then pass."""
    H.refused(4, H.read, tree, declaration=H.RD7, purpose="stage_D_scorecard")
    H.add_rows(tree, "| E-920 | 2026-11-18 | heldout-verdict: NQ F-13 -- F-13's verdict | x |")
    a = H.read(tree, declaration=H.RD7, purpose="stage_D_scorecard")
    assert a.kind == "described_reading" and "finalists" not in dict(a.heldout)


# ----------------------------------------------------------------------------------------- E-247's rm-4, untouched


def test_a_registered_reproduction_identity_needs_no_finalists_token(t16, monkeypatch):
    commit_file(t16, "identity/repro_id.py", "print('identity HOLDS')\n")
    monkeypatch.setattr(R, "_main_script", lambda: t16 / "identity" / "repro_id.py")
    text = (t16 / "DECISIONS.md").read_text(encoding="utf-8")
    assert not R.heldout_tokens(text, "finalists"), "no finalists' token anywhere"
    a = R.authorise_engine_read("2020-01-02", "2026-07-16", purpose="identity", declaration="E-905",
                                files=[t16 / H.BARS], what="q194 identity", repo=t16)
    assert a.judged and a.kind == "identity" and a.ledgered and a.heldout is None
    rec = H.lines(t16)[-1]
    assert rec["purpose"] == "identity" and rec.get("heldout") is None
    # a later family read is not locked out by the identity's line (rule 2 counts families only)
    H.add_rows(t16, H.finalists(920, "F-16", F16_TEXT, LIST16))
    assert H.read(t16, declaration=F16, purpose="stage_Z_anything").judged


def test_a_family_file_cannot_borrow_the_identity_purpose(t16, monkeypatch):
    commit_file(t16, "identity/repro_id.py", "print('identity HOLDS')\n")
    monkeypatch.setattr(R, "_main_script", lambda: t16 / "identity" / "repro_id.py")
    with pytest.raises(R.JudgedBlockSealed, match="decision row of its identity"):
        H.read(t16, declaration=F17, purpose="identity")
    H.refused(1, H.read, t16, declaration=F17, purpose="stage_Z_anything")
    assert H.lines(t16) == []


def test_a_registered_designs_held_out_read_is_rule_3s_alone(scripted):
    H.add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14,P-16 by scripts/replay.py -- P-14 and P-16 "
                         "replayed | x |")
    assert not R.heldout_tokens((scripted / "DECISIONS.md").read_text(encoding="utf-8"), "finalists")
    a = H.rd_read(scripted, "E-940", ("P-14", "P-16"))
    assert a.judged and a.kind == "registered_design" and dict(a.heldout) == {"read_row": "E-940"}


# ------------------------------------------------------------------------------------ rule 2 and a refused read


def test_a_refused_read_does_not_spend_the_window(t16, monkeypatch):
    for purpose in OTHER:
        H.refused(1, H.read, t16, declaration=F16, purpose=purpose)
    H.refused(1, H.read, t16, purpose="stage_C_judgement")             # F-13, no token either
    assert H.lines(t16) == []
    H.add_rows(t16, H.finalists(921, "F-14", H.F14_TEXT, H.LIST14))
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    a = H.read(t16, declaration=H.F14)                                  # the joint test's read: not locked out
    assert a.judged and dict(a.heldout)["finalists"] == "E-921"
    assert [r["declaration"]["ref"] for r in H.lines(t16)] == [H.F14]


def test_rule1_refuses_before_rule2(t16, monkeypatch):
    H.spend(t16)                                                        # F-13's held-out test spends NQ's window
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    e = H.refused(1, H.read, t16, declaration=F16, purpose="stage_Z_anything")
    names_both(e, "stage_Z_anything", F16)
    H.add_rows(t16, H.finalists(923, "F-16", F16_TEXT, LIST16))
    e = H.refused(2, H.read, t16, declaration=F16, purpose="stage_Z_anything")   # with its token: rule 2's
    names_both(e, "stage_Z_anything", F16)
    assert len(H.lines(t16)) == 1


def test_rule4s_refusal_names_the_purpose_and_the_declaration(tree):
    e = H.refused(4, H.read, tree, declaration=H.RD7, purpose="stage_D_scorecard")
    names_both(e, "stage_D_scorecard", H.RD7)


# ---------------------------------------------------------------------------------------- the defect, as a mutant


def test_the_old_narrow_gate_is_the_defect(t16, monkeypatch):
    """With rule 1 narrowed back to the held-out purposes (the code before Q-194), the arbitrary purpose's read goes
    through with no token and spends NQ's window: the hole this item closes."""
    monkeypatch.setattr(R, "_rule1_binds", lambda ref, purpose: purpose in R.HELDOUT_PURPOSES)
    assert H.read(t16, declaration=F16, purpose="stage_Z_anything").judged
    H.add_rows(t16, H.finalists(921, "F-14", H.F14_TEXT, H.LIST14))
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    H.refused(2, H.read, t16, declaration=H.F14)                        # the joint test locked out
