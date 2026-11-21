"""Q-194d (the lead's rulings on the red team's `READER_Q194c_2026-11-21`): the order of a verdict and its read, the
log's fences and hygiene, the one held-out declaration per market, the recorded window, on Q-158's synthetic tree
(`tests/test_reader_heldout.py`'s helpers; `tests/heldout_verdict_rows.py`'s seeded joint test F-98; hand-made ledger
lines where a field is the point; nothing real is read).

* **MINOR-1, the order is proven, not containment:** a ledger line backs a verdict only if the ledger as committed in
  the first commit adding the verdict row already holds it, byte for byte, and the read's commit is a proper ancestor
  of that commit. The red team's probe A (the verdict committed first, the read made after it from the older commit)
  and a line the running process appended itself are refused; a line committed with the verdict whose commit is on a
  side branch is refused; the seeded joint test (read, then its verdict committed with the ledger) is admitted;
* **MINOR-2, CommonMark fences everywhere and the log's hygiene:** a `~~~` line does not close a ``` fence (C1); an
  indented ``` is no fence (C2); an unclosed fence runs to the end of the file and refuses every judged read -- an
  identity's too -- naming the line (C3); a fenced token refuses every judged read (C4); `decision_row` and `pins` skip
  fenced lines, so a fenced pin pins nothing (C5), a fenced identity row or `repeat=` row is no row; the search years
  are untouched;
* **NOTE-5, the red team's surviving mutants:** a fenced E-208 row is not the base window's opening (X4); the gate's
  finalists' row must be at the verdict's sha (X5); a fenced pin row is not the pin (X6); a line with no recorded
  window backs nothing (X7);
* **NOTE-6, the one held-out declaration per market:** `heldout_test` and `heldout_stress` are read only by an F- file
  named `prereg/F-NN_heldout_test_<MARKET>.md` carrying the template's marker (at a line's start) and headings, not
  the design-search marker, the only marked file of its market -- an F-03-like family with a judged-read line naming
  them and a finalists' token is refused, as is a marked file misnamed, of another market, short of a heading,
  doubly marked, or one of two for the market;
* **NOTE-1:** a read is recorded under the newest window it touches (`windows` beside it when there are more);
* **NOTE-2, -3, -4:** the reader's docstring states what a counted verdict means.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from extended import reader as R
import heldout_verdict_rows as VR
import test_reader_heldout as H
from test_reader_heldout import tree  # noqa: F401 -- the fixture

READ_ROW = ("| E-940 | 2026-11-18 | heldout-read: P-14,P-16 by scripts/replay.py -- P-14 and P-16 replayed on the "
            "held-out years | x |")
WINDOW_2025 = "| E-990 | 2026-11-20 | heldout-window: NQ 2025-01-02 to 2026-07-16 -- a newer window | x |"


@pytest.fixture
def declared(tree, monkeypatch):
    """A readings script as the process's and a lead's row declaring its held-out read -- but no verdict yet."""
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    H.add_rows(tree, READ_ROW)
    return tree


def reg(t: Path, start: str = "2024-01-02", end: str = "2026-07-16", market: str = "NQ"):
    return R.authorise_engine_read(start, end, purpose="registered_design", declaration="E-940",
                                   design=("P-14", "P-16"), files=[t / H.BARS], what="q194d design", repo=t,
                                   market=market)


def gate_refuses(t: Path, *also: str) -> R.HeldOutRefused:
    e = H.refused(3, reg, t)
    assert "no verdict row counts" in str(e) and all(x in str(e) for x in also), str(e)
    return e


def hygiene_refuses(fn, *a, **kw) -> str:
    with pytest.raises(R.JudgedBlockSealed) as info:
        fn(*a, **kw)
    assert str(info.value).startswith(f"REFUSED ({R.LOG_RULE})"), str(info.value)
    assert not isinstance(info.value, R.HeldOutRefused)
    return str(info.value)


def head(t: Path) -> str:
    return H.git(t, "rev-parse", "HEAD")


def put_lines(t: Path, recs: list[dict]) -> None:
    p = t / "results" / "read_ledger.jsonl"
    p.parent.mkdir(exist_ok=True)
    with p.open("a", encoding="utf-8", newline="\n") as f:
        f.writelines(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in recs)


def forged(commit: str, **over) -> dict:
    """A hand-made ledger line of F-98's held-out read; `over` sets dotted fields (a value None deletes the field)."""
    rec = {"ledger": 1, "when": "2026-11-20T00:00:00+00:00",
           "who": {"script": None, "args": [], "caller": "test", "commit": commit, "dirty": False, "pid": 1,
                   "clean_run": H.RUN, "run_id": "forged@run-0"},
           "what": {"kind": "engine", "files": [{"path": H.BARS}], "columns": None, "description": "forged"},
           "dates": {"start": "2024-01-02", "end": "2026-07-16", "blocks": ["judged"], "judged_first": "2024-01-02",
                     "judged_last": "2026-07-16"},
           "declaration": {"ref": VR.HT_PATH, "sha256": VR.HT_SHA, "kind": "family"},
           "purpose": "heldout_test", "repeat": None,
           "heldout": {"market": "NQ", "window": "E-208", "finalists": "E-981", "finalists_list_sha256": VR.HT_LIST}}
    for k, v in over.items():
        d = rec
        *path, last = k.split(".")
        for p in path:
            d = d[p]
        if v is None:
            d.pop(last, None)
        else:
            d[last] = v
    return rec


# ------------------------------------------------------------------------------------- MINOR-1: the order proven


def test_the_seeded_joint_test_is_admitted(declared):
    VR.settle(declared, [declared / H.BARS])
    assert dict(reg(declared).heldout)["test_verdict"] == "E-982"


def test_probe_a_a_read_made_after_the_verdict_was_committed_backs_nothing(declared):
    c0 = VR.declare(declared)                                           # the held-out row's commit
    VR.commit_verdict(declared, VR.VERDICT_ROW)                         # the verdict typed and committed first
    H.git(declared, "checkout", "-q", c0)                               # then the clean checkout of c0
    H.read(declared, declaration=VR.HT_PATH, purpose="heldout_test")    # the joint test's read, after the verdict
    H.git(declared, "checkout", "-q", "master")
    VR.commit_verdict(declared, "| E-983 | 2026-11-19 | the run's lines collected | x |")   # the line committed later
    gate_refuses(declared)


def test_a_line_the_running_process_appended_itself_backs_nothing(declared):
    c0 = VR.declare(declared)
    put_lines(declared, [forged(c0, **{"declaration.ref": H.F13})])     # the committed ledger: another line only
    VR.commit_verdict(declared, VR.VERDICT_ROW)
    assert R._committed_ledger(declared, R._verdict_commit(declared, VR.VERDICT_ROW))
    put_lines(declared, [forged(c0)])                                   # appended by the run, never committed
    gate_refuses(declared)
    H.refused(4, H.read, declared, declaration=H.RD7, purpose="stage_D_scorecard")


def test_a_committed_line_whose_commit_is_not_an_ancestor_backs_nothing(declared):
    c0 = VR.declare(declared)
    H.git(declared, "checkout", "-q", "-b", "side")
    VR.append_rows(declared, "| E-985 | 2026-11-19 | a side-branch row | x |")
    side = head(declared)
    H.git(declared, "checkout", "-q", "master")
    put_lines(declared, [forged(side)])
    VR.commit_verdict(declared, VR.VERDICT_ROW)                         # committed with the verdict, but off its line
    gate_refuses(declared)
    assert c0 != side


def test_the_same_line_from_an_ancestor_commit_is_admitted(declared):
    """The control of the two above: a hand-made line from the pin's commit, committed with the verdict."""
    c0 = VR.declare(declared)
    put_lines(declared, [forged(c0)])
    VR.commit_verdict(declared, VR.VERDICT_ROW)
    assert dict(reg(declared).heldout)["test_verdict"] == "E-982"


def test_a_verdict_not_in_heads_history_backs_nothing(declared):
    """The verdict row in the working copy only, never committed: git finds no commit adding it -- fails closed."""
    c0 = VR.declare(declared)
    put_lines(declared, [forged(c0)])
    VR.commit_verdict(declared, "| E-983 | 2026-11-19 | the ledger collected | x |")
    (declared / "DECISIONS.md").write_bytes(((declared / "DECISIONS.md").read_text(encoding="utf-8")
                                             + VR.VERDICT_ROW + "\n").encode("utf-8"))
    assert R._verdict_commit(declared, VR.VERDICT_ROW) is None
    gate_refuses(declared)


# --------------------------------------------------------------------------------- MINOR-2: fences and hygiene


def test_c1_a_tilde_line_does_not_close_a_backtick_fence():
    text = "\n".join((VR.PIN_ROW, VR.FINALISTS_ROW, "```", "~~~", VR.VERDICT_ROW, "```"))
    assert R.heldout_tokens(text, "verdict") == []
    assert any(p.startswith("E-982") and "fenced" in p for p in R.heldout_token_problems(text))
    assert R._fences(text) == ([False, False, True, True, True, True], None)


def test_c2_an_indented_backtick_line_is_no_fence():
    text = "\n".join(("    ```", VR.VERDICT_ROW))
    assert [t.row for t in R.heldout_tokens(text, "verdict")] == ["E-982"]
    assert R._fences(text) == ([False, False], None)


@pytest.mark.parametrize("opening,closing,closes", [
    ("```", "```", True), ("````", "```", False), ("```", "````", True), ("~~~", "~~~", True), ("~~~", "```", False),
    ("   ```", "   ```", True), ("```python", "```", True), ("```", "``` x", False),
])
def test_commonmarks_fence_rules(opening, closing, closes):
    text = "\n".join(("a", opening, "b", closing, "c"))
    fenced, unclosed = R._fences(text)
    assert fenced[:4] == [False, True, True, True]
    assert (fenced[4] is False and unclosed is None) if closes else (fenced[4] is True and unclosed == 1)


def test_a_backtick_fences_info_string_holds_no_backtick():
    assert R._fences("``` a`b\nx") == ([False, False], None)


def test_c3_an_unclosed_fence_refuses_every_judged_read_naming_it(declared, monkeypatch):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, "```", WINDOW_2025)
    msg = hygiene_refuses(reg, declared, start="2025-01-02")
    assert "never closed" in msg
    hygiene_refuses(H.read, declared, declaration=H.RD7, purpose="stage_D_scorecard")
    (declared / "identity").mkdir(exist_ok=True)
    (declared / "identity" / "repro_id.py").write_text("print('identity HOLDS')\n", encoding="utf-8")
    H.git(declared, "add", "-A")
    H.git(declared, "commit", "-q", "-m", "an identity")
    monkeypatch.setattr(R, "_main_script", lambda: declared / "identity" / "repro_id.py")
    hygiene_refuses(R.authorise_engine_read, "2020-01-02", "2026-07-16", purpose="identity", declaration="E-905",
                    files=[declared / H.BARS], what="q194d identity", repo=declared)
    assert not R.authorise("2020-01-02", "2023-12-29", purpose="identity", declaration="E-905", repo=declared).judged


def test_c4_a_fenced_read_row_refuses_every_judged_read_and_is_no_row(tree, monkeypatch):
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    VR.settle(tree, [tree / H.BARS])
    VR.append_rows(tree, "```", READ_ROW, "```")
    text = (tree / "DECISIONS.md").read_text(encoding="utf-8")
    assert R.decision_row(text, "E-940") is None
    assert any(p.startswith("E-940") and "fenced" in p for p in R.heldout_token_problems(text))
    hygiene_refuses(reg, tree)


def test_c5_a_fenced_pin_pins_nothing(tree):
    rd, txt = "prereg/RD-09_x.md", "# RD-09\n\n- **Judged-block reads:** `stage_D_scorecard`\n"
    (tree / rd).write_bytes(txt.encode("utf-8"))
    H.git(tree, "add", rd)
    VR.settle(tree, [tree / H.BARS])
    VR.append_rows(tree, "```", f"| E-950 | 2026-11-20 | **RD-09 declared**, `{rd}` sha256 `{H.sha_lf(txt)}` | x |",
                   "```")
    assert rd not in R.pins((tree / "DECISIONS.md").read_text(encoding="utf-8"))
    with pytest.raises(R.JudgedBlockSealed, match="not pinned"):
        H.read(tree, declaration=rd, purpose="stage_D_scorecard")


def test_fenced_rows_are_no_rows_for_identity_or_repeat(tree, monkeypatch):
    text = "\n".join(("```", "| E-905 | 2026-11-18 | **The identity holds** | test |", "```"))
    assert R.decision_row(text, "E-905") is None
    assert R.decision_row("| E-905 | 2026-11-18 | **The identity holds** | test |", "E-905") is not None
    VR.append_rows(tree, H.finalists(920, "F-13", H.F13_TEXT, H.LIST13))
    H.read(tree)                                                        # F-13, run 1
    VR.append_rows(tree, "~~~", f"| E-960 | 2026-11-20 | **another read of `{H.F13}`** | x |", "~~~")
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    with pytest.raises(R.JudgedBlockSealed, match="does not name"):
        H.read(tree, repeat="E-960")                                    # the fenced row names nothing


# --------------------------------------------------------------------------------- NOTE-5: the surviving mutants


def test_x4_a_fenced_e208_row_is_not_the_base_windows_opening(declared):
    VR.settle(declared, [declared / H.BARS])
    VR.append_rows(declared, "```", "| E-208 | 2026-11-17 | **the split** (an example, fenced) | x |", "```")
    assert dict(reg(declared).heldout)["test_verdict"] == "E-982"
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert R._row_pos(text, "E-208") == -1


def test_x5_the_gates_finalists_row_must_be_at_the_verdicts_sha(declared):
    c0 = VR.declare(declared)
    VR.append_rows(declared, f"| E-983 | 2026-11-19 | heldout-finalists: {VR.HT_ID} @ {'5' * 64} list {VR.HT_LIST} -- "
                             "other bytes | x |")
    put_lines(declared, [forged(c0, **{"heldout.finalists": "E-983"})])
    VR.commit_verdict(declared, VR.VERDICT_ROW)
    gate_refuses(declared)


def test_x6_a_fenced_pin_row_is_not_the_pin(declared):
    (declared / VR.HT_PATH).write_bytes(VR.HT_TEXT.encode("utf-8"))
    H.git(declared, "add", VR.HT_PATH)
    VR.append_rows(declared, "```", VR.PIN_ROW.replace("E-980", "E-979"), "```", VR.FINALISTS_ROW, VR.PIN_ROW)
    put_lines(declared, [forged(head(declared))])
    VR.commit_verdict(declared, VR.VERDICT_ROW)
    gate_refuses(declared)                                              # the only pin follows the finalists' row


def test_x7_a_line_with_no_recorded_window_backs_nothing(declared):
    c0 = VR.declare(declared)
    put_lines(declared, [forged(c0, **{"heldout.window": None})])
    VR.commit_verdict(declared, VR.VERDICT_ROW)
    gate_refuses(declared)


# ------------------------------------------------------------------------ NOTE-6: the one held-out declaration


def _pin(t: Path, rel: str, text: str, row: int, finalists_row: int) -> None:
    (t / rel).parent.mkdir(exist_ok=True)
    (t / rel).write_bytes(text.encode("utf-8"))
    H.git(t, "add", rel)
    fid = rel.split("/")[1].split("_")[0]
    VR.append_rows(t, f"| E-{row} | 2026-11-20 | **{fid} declared**, `{rel}` sha256 `{H.sha_lf(text)}` | x |",
                   H.finalists(finalists_row, fid, text, "4" * 64))


F03_LIKE = "# F-03-like: a family\n\n- **Judged-block reads:** `stage_C_judgement`, `heldout_test`, `heldout_stress`\n"


def test_an_f03_like_family_is_refused_the_held_out_purposes(tree):
    _pin(tree, "prereg/F-03_opening_timing.md", F03_LIKE, 960, 961)
    for purpose in R.HELDOUT_PURPOSES:
        e = H.refused(1, H.read, tree, declaration="prereg/F-03_opening_timing.md", purpose=purpose)
        assert "one held-out declaration of NQ" in str(e) and "marker" in str(e) and purpose in str(e)
    assert H.read(tree, declaration="prereg/F-03_opening_timing.md").kind == "family", "its own purpose: rules 1, 2"
    assert H.lines(tree, seed=True)[-1]["purpose"] == "stage_C_judgement"


def test_the_f_ht_like_declaration_reads_both_purposes(tree):
    VR.declare(tree)
    for purpose in R.HELDOUT_PURPOSES:
        assert H.read(tree, declaration=VR.HT_PATH, purpose=purpose).judged
    assert R.heldout_declaration_problems(VR.HT_PATH, tree, "NQ") == []


@pytest.mark.parametrize("rel,text,why", [
    ("prereg/F-97_joint.md", VR.HT_TEXT, "its path is not"),                                   # misnamed
    ("prereg/F-97_heldout_test_ES.md", VR.HT_TEXT, "its path is not"),                         # another market's
    ("prereg/F-97_heldout_test_NQ.md", VR.heldout_text("F-97", headings=VR.HT_HEADINGS[:-1]), "heading"),
    ("prereg/F-97_heldout_test_NQ.md", VR.heldout_text("F-97") + "\n**Declaration kind: design search.** x\n",
     "design-search marker"),
    ("prereg/F-97_heldout_test_NQ.md", VR.heldout_text("F-97", marker="It says **Declaration kind: held-out test.**"),
     "marker"),                                                                                 # not at a line's start
])
def test_a_marked_file_out_of_form_is_refused(tree, rel, text, why):
    _pin(tree, rel, text, 960, 961)
    e = H.refused(1, H.read, tree, declaration=rel, purpose="heldout_test")
    assert why in str(e), str(e)


def test_two_marked_files_for_one_market_refuse_both(tree):
    VR.declare(tree)
    _pin(tree, "prereg/F-97_heldout_test_NQ.md", VR.heldout_text("F-97: a second one"), 960, 961)
    for rel in (VR.HT_PATH, "prereg/F-97_heldout_test_NQ.md"):
        e = H.refused(1, H.read, tree, declaration=rel, purpose="heldout_test")
        assert "another held-out-marked F- file exists for NQ" in str(e)
    assert H.lines(tree, seed=True) == []


def test_another_markets_marked_file_does_not_block_nq(tree):
    VR.declare(tree)
    _pin(tree, "prereg/F-97_heldout_test_ES.md", VR.heldout_text("F-97: ES's"), 960, 961)
    assert H.read(tree, declaration=VR.HT_PATH, purpose="heldout_test").judged
    assert H.read(tree, declaration="prereg/F-97_heldout_test_ES.md", purpose="heldout_test", market="ES").judged


# ----------------------------------------------------------------------------------- NOTE-1: the recorded window


def test_a_read_is_recorded_under_the_newest_window_it_touches(tree):
    H.add_rows(tree, "| E-990 | 2026-11-20 | heldout-window: NQ 2025-01-02 to 2025-06-30 -- w1 | x |",
               "| E-991 | 2026-11-20 | heldout-window: NQ 2025-07-01 to 2026-07-16 -- w2 | x |",
               H.finalists(992, "F-13", H.F13_TEXT, H.LIST13))
    a = H.read(tree, start="2025-03-03", end="2025-09-02")             # the red team's probe D
    assert dict(a.heldout)["window"] == "E-991" and dict(a.heldout)["windows"] == ["E-990", "E-991"]


# --------------------------------------------------------------------------------- NOTE-2, -3, -4: stated


def test_the_reader_states_what_a_counted_verdict_means():
    doc = " ".join(R.__doc__.split())
    for phrase in ("a read of part of a window backs the whole window", "a crashed run's written line still counts",
                   "a later window re-opens days already read", "tagged `heldout-read/<run id>` at its commit",
                   "fails closed", "the order is proven"):
        assert phrase in doc, phrase
