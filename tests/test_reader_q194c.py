"""Q-194c (the lead's rulings on the red team's `READER_Q194_2026-11-21`): the reader's verdict, windows and places, on
Q-158's synthetic tree (`tests/test_reader_heldout.py`'s helpers; `tests/heldout_verdict_rows.py`'s seeded joint
test; hand-made ledger lines where a field is the point; nothing real is read).

* **MINOR-1, a verdict counts only for a held-out read that happened:** the checkout's ledger must hold the verdict's
  family's `heldout_test` read of the window, at the verdict's sha256 and market, under a finalists' row of it, in a
  clean run (a run id, not dirty), judged, made from a commit whose DECISIONS.md did not yet hold the verdict row.
  The control line is admitted; with any one of those fields otherwise -- or no line at all -- the verdict counts for
  nothing (the registered gate, rule 3; and rule 4);
* **MINOR-3, NOTE-3, one form with the market:** the gate admits a read only of the verdict's own market;
* **MINOR-2, every window a read touches:** a registered read, a described reading's read, or a family's read that
  straddles a newer window and E-208's base window touches both -- the gate and rule 4 want a counted verdict for
  each, rule 2 refuses a window another family spent in either, and a straddling family read records both windows;
* **NOTE-2, places, not numbers; fences:** a verdict placed before its finalists' row counts for nothing whatever its
  number, one placed after counts whatever its number; a verdict placed before E-208's own row counts for nothing; a
  verdict row inside a fenced code block counts for nothing and is reported;
* **MINOR-4:** a finalists' token in its pin's own row (M10, rule 1 in `test_reader_q194.py`, the gate here), the
  verdict's id against its pin's id (M6), the newest qualifying verdict recorded (M11).
"""
from __future__ import annotations

import copy
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
                                   design=("P-14", "P-16"), files=[t / H.BARS], what="q194c design", repo=t,
                                   market=market)


def gate_refuses(t: Path, *windows: str, **kw) -> R.HeldOutRefused:
    e = H.refused(3, reg, t, **kw)
    assert "no verdict row counts" in str(e) and all(w in str(e) for w in windows), str(e)
    return e


def head(t: Path) -> str:
    return H.git(t, "rev-parse", "HEAD")


def write_ledger(t: Path, recs: list[dict]) -> None:
    p = t / "results" / "read_ledger.jsonl"
    p.parent.mkdir(exist_ok=True)
    p.write_bytes("".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in recs).encode("utf-8"))


def forged(commit: str, **over) -> dict:
    """A hand-made ledger line of F-98's held-out read (the fields a real one has); `over` sets dotted fields."""
    rec = {"ledger": 1, "when": "2026-11-20T00:00:00+00:00",
           "who": {"script": None, "args": [], "caller": "test", "commit": commit, "dirty": False, "pid": 1,
                   "clean_run": H.RUN, "run_id": "forged@run-0"},
           "what": {"kind": "engine", "files": [{"path": H.BARS}], "columns": None, "description": "forged"},
           "dates": {"start": "2024-01-02", "end": "2026-07-16", "blocks": ["judged"], "judged_first": "2024-01-02",
                     "judged_last": "2026-07-16"},
           "declaration": {"ref": VR.HT_PATH, "sha256": VR.HT_SHA, "kind": "family"},
           "purpose": "heldout_test", "repeat": None,
           "heldout": {"market": "NQ", "window": "E-208", "finalists": "E-981",
                       "finalists_list_sha256": VR.HT_LIST}}
    for k, v in over.items():
        d = rec
        *path, last = k.split(".")
        for p in path:
            d = d[p]
        d[last] = v
    return rec


def pinned_with_finalists(t: Path) -> str:
    """F-98's file, pin and finalists' row committed (no read, no verdict); returns that commit."""
    (t / VR.HT_PATH).write_bytes(VR.HT_TEXT.encode("utf-8"))
    H.git(t, "add", VR.HT_PATH)
    VR.append_rows(t, VR.PIN_ROW, VR.FINALISTS_ROW)
    return head(t)


# ------------------------------------------------------------------------- MINOR-1: the read behind the verdict


def test_a_verdict_for_a_family_that_never_read_counts_for_nothing(declared):
    pinned_with_finalists(declared)
    VR.append_rows(declared, VR.VERDICT_ROW)
    gate_refuses(declared, "E-208")
    H.refused(4, H.read, declared, declaration=H.RD7, purpose="stage_D_scorecard")
    assert H.lines(declared, seed=True) == []


def test_the_seeded_joint_tests_read_makes_its_verdict_count(declared):
    line = VR.settle(declared, [declared / H.BARS])
    assert line["purpose"] == "heldout_test" and line["who"]["run_id"] == VR.SEED_RUN_ID
    assert line["heldout"] == {"market": "NQ", "window": "E-208", "finalists": "E-981",
                               "finalists_list_sha256": VR.HT_LIST}
    assert dict(reg(declared).heldout)["test_verdict"] == "E-982"
    assert dict(H.read(declared, declaration=H.RD7, purpose="stage_D_scorecard").heldout)["verdict"] == "E-982"


@pytest.mark.parametrize("over", [
    {},                                                                  # the control: counted
    {"purpose": "heldout_stress"}, {"purpose": "stage_C_judgement"},
    {"declaration.kind": "described_reading"},
    {"declaration.ref": "prereg/F-97_other.md"},
    {"declaration.sha256": "5" * 64},
    {"heldout.market": "ES"},
    {"heldout.window": "E-990"},
    {"heldout.finalists": "E-999"},
    {"who.clean_run": None}, {"who.run_id": None}, {"who.dirty": True},
    {"dates.judged_first": None},
    {"who.commit": "0" * 40},                                            # a commit the tree does not have
    {"who.commit": "AFTER"},                                             # the commit that holds the verdict row
])
def test_the_verdicts_read_must_be_its_own_in_every_field(declared, over):
    c0 = pinned_with_finalists(declared)
    if over.get("who.commit") == "AFTER":                               # a read from the verdict's own commit
        v = VR.commit_verdict(declared, VR.VERDICT_ROW)
        over = {"who.commit": v}
        write_ledger(declared, [forged(c0, **over)])
        VR.commit_verdict(declared, "| E-983 | 2026-11-19 | the run's lines collected | x |")
    else:                                                               # Q-194d: committed with the verdict
        write_ledger(declared, [forged(c0, **over)])
        VR.commit_verdict(declared, VR.VERDICT_ROW)
    if not over:
        assert dict(reg(declared).heldout)["test_verdict"] == "E-982"
        return
    gate_refuses(declared, "E-208")
    H.refused(4, H.read, declared, declaration=H.RD7, purpose="stage_D_scorecard")


# ---------------------------------------------------------------------------------- MINOR-3, NOTE-3: the market


def test_the_gate_admits_only_the_verdicts_own_market(declared):
    VR.settle(declared, [declared / H.BARS])
    assert reg(declared).judged
    gate_refuses(declared, market="ES")
    H.refused(4, H.read, declared, declaration=H.RD7, purpose="stage_D_scorecard", market="ES")


def test_a_verdict_naming_another_market_counts_for_nothing(declared):
    c0 = pinned_with_finalists(declared)
    write_ledger(declared, [forged(c0)])
    VR.append_rows(declared, VR.verdict_row(market="ES"))
    gate_refuses(declared)
    gate_refuses(declared, market="ES")                                  # nor for ES: its read was NQ's


# -------------------------------------------------------------------------------- MINOR-2: every window touched


def test_the_gate_wants_a_verdict_for_every_window_a_read_touches(declared):
    VR.settle(declared, [declared / H.BARS])                            # F-98 reads E-208, its verdict
    VR.append_rows(declared, WINDOW_2025)                               # then a newer window, no verdict yet
    gate_refuses(declared, "E-990")                                     # 2024-01-02..2026-07-16 straddles
    gate_refuses(declared, "E-990", start="2024-12-31", end="2025-01-03")
    gate_refuses(declared, "E-990", start="2025-01-02")
    assert dict(reg(declared, end="2024-12-31").heldout)["test_verdict"] == "E-982"     # E-208's days alone
    # E-990's own joint read (NQ's one held-out declaration, F-98, read under a later run: a hand-made line, the
    # once rule aside), committed with its verdict
    put = forged(head(declared), **{"heldout.window": "E-990", "dates.start": "2025-01-02",
                                     "dates.judged_first": "2025-01-02", "who.run_id": "joint@run-2"})
    with (declared / "results" / "read_ledger.jsonl").open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(put, sort_keys=True, separators=(",", ":")) + "\n")
    VR.commit_verdict(declared, VR.verdict_row(992))
    # E-992 is the newest verdict counted for both windows: F-98's E-208 line backs it as well
    assert dict(reg(declared).heldout)["test_verdict"] == "E-992,E-992"


def test_rule4_wants_a_verdict_for_every_window_a_read_touches(tree):
    H.settled_verdict(tree)
    H.add_rows(tree, WINDOW_2025)
    e = H.refused(4, H.read, tree, declaration=H.RD7, purpose="stage_D_scorecard")
    assert "E-990" in str(e)
    assert dict(H.read(tree, declaration=H.RD7, purpose="stage_D_scorecard", end="2024-12-31").heldout)[
        "verdict"] == "E-982"


def test_rule2_counts_every_window_a_read_touches(tree, monkeypatch):
    """The red team's P1 for rule 2: F-13 spends the newer window; F-14's read straddling it and the unspent base
    window is refused; F-14's read of the base window's days alone is admitted."""
    H.add_rows(tree, WINDOW_2025, H.finalists(991, "F-13", H.F13_TEXT, H.LIST13),
               H.finalists(992, "F-14", H.F14_TEXT, H.LIST14), H.finalists(993, "F-15", H.F15_TEXT, H.LIST15))
    H.read(tree, start="2025-01-02")                                    # F-13: E-990
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    e = H.refused(2, H.read, tree, declaration=H.F14)                   # 2024-01-02..2026-07-16: E-208 and E-990
    assert "E-990" in str(e) and H.F13 in str(e)
    H.refused(2, H.read, tree, declaration=H.F14, start="2024-12-31", end="2025-01-03")
    a = H.read(tree, declaration=H.F14, end="2024-12-31")               # E-208's days alone
    assert dict(a.heldout)["window"] == "E-208" and "windows" not in dict(a.heldout)


def test_a_straddling_family_read_records_both_windows_and_spends_both(tree, monkeypatch):
    H.add_rows(tree, WINDOW_2025, H.finalists(991, "F-13", H.F13_TEXT, H.LIST13),
               H.finalists(992, "F-14", H.F14_TEXT, H.LIST14))
    a = H.read(tree)                                                    # F-13 straddles E-208 and E-990
    assert dict(a.heldout)["window"] == "E-990" and dict(a.heldout)["windows"] == ["E-208", "E-990"]   # NOTE-1
    assert H.lines(tree)[-1]["heldout"]["windows"] == ["E-208", "E-990"]
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    H.refused(2, H.read, tree, declaration=H.F14, start="2025-01-02")   # E-990 alone: spent by F-13's straddle
    H.refused(2, H.read, tree, declaration=H.F14, end="2024-12-31")     # E-208 alone: spent too


def test_heldout_windows_gives_each_day_its_newest_window(tree):
    text = "\n".join(("| E-208 | 2026-11-17 | the split | x |", WINDOW_2025,
                      "| E-995 | 2026-11-21 | heldout-window: NQ 2024-06-03 to 2025-06-30 -- newer still | x |",
                      "| E-996 | 2026-11-21 | heldout-window: ES 2024-01-02 to 2026-07-16 -- another market | x |"))
    d = R._day
    assert R.heldout_windows(text, "NQ", d("2024-01-02"), d("2026-07-16")) == (("E-208", 0), ("E-990", 1),
                                                                              ("E-995", 2))
    assert R.heldout_windows(text, "NQ", d("2025-01-02"), d("2025-06-30")) == (("E-995", 2),)
    assert R.heldout_windows(text, "NQ", d("2025-07-01"), d("2026-07-16")) == (("E-990", 1),)
    assert R.heldout_windows(text, "ES", d("2024-01-02"), d("2024-02-01")) == (("E-996", 3),)
    assert R.heldout_windows("", "NQ", d("2024-01-02"), d("2024-01-02")) == (("E-208", -1),)


# ------------------------------------------------------------------------------- NOTE-2: places, not numbers


def test_a_verdict_counts_by_its_place_not_its_number(declared):
    c0 = pinned_with_finalists(declared)
    write_ledger(declared, [forged(c0)])
    H.git(declared, "add", "-f", "results/read_ledger.jsonl")         # committed with the placed-first verdict
    H.prepend_rows(declared, VR.verdict_row(999))                       # a high number, placed before the finalists
    gate_refuses(declared)
    VR.commit_verdict(declared, VR.verdict_row(100))                    # a low number, placed after them
    assert dict(reg(declared).heldout)["test_verdict"] == "E-100"


def test_a_verdict_placed_before_e208s_own_row_counts_for_nothing(declared):
    VR.settle(declared, [declared / H.BARS])
    assert reg(declared).judged
    VR.append_rows(declared, "| E-208 | 2026-11-17 | **the split** (the base window's opening row, placed last) | x |")
    gate_refuses(declared, "E-208")


def test_a_fenced_verdict_counts_for_nothing_and_is_reported(declared):
    VR.settle(declared, [declared / H.BARS], verdict=False)
    VR.commit_verdict(declared, "```", VR.VERDICT_ROW, "```")
    text = (declared / "DECISIONS.md").read_text(encoding="utf-8")
    assert not R.heldout_tokens(text, "verdict")
    assert any("fenced" in p and p.startswith("E-982") for p in R.heldout_token_problems(text))
    with pytest.raises(R.JudgedBlockSealed, match="hygiene"):           # Q-194d: and the log fails every judged read
        reg(declared)


def test_a_fenced_finalists_or_pin_row_is_never_the_one_behind_a_verdict(declared):
    c0 = pinned_with_finalists(declared)
    write_ledger(declared, [forged(c0, **{"heldout.finalists": "E-983"})])
    VR.commit_verdict(declared, "~~~", f"| E-983 | 2026-11-19 | heldout-finalists: {VR.HT_ID} @ {VR.HT_SHA} list "
                                       f"{VR.HT_LIST} -- fenced | x |", "~~~", VR.VERDICT_ROW)
    with pytest.raises(R.JudgedBlockSealed, match="hygiene"):           # Q-194d: a fenced token fails every read
        reg(declared)


# ---------------------------------------------------------------------------------------------- MINOR-4


def test_m10_a_finalists_token_in_its_pins_own_row_backs_no_verdict(declared):
    (declared / VR.HT_PATH).write_bytes(VR.HT_TEXT.encode("utf-8"))
    H.git(declared, "add", VR.HT_PATH)
    combined = (f"| E-985 | 2026-11-19 | heldout-finalists: {VR.HT_ID} @ {VR.HT_SHA} list {VR.HT_LIST} -- and "
                f"`{VR.HT_PATH}` sha256 `{VR.HT_SHA}` pinned in the same row | x |")
    VR.append_rows(declared, combined)
    write_ledger(declared, [forged(head(declared), **{"heldout.finalists": "E-985"})])
    VR.commit_verdict(declared, VR.VERDICT_ROW)
    gate_refuses(declared)
    H.prepend_rows(declared, VR.PIN_ROW)                                # a pin placed before it: then it counts
    assert dict(reg(declared).heldout)["test_verdict"] == "E-982"


def test_m6_the_verdicts_id_must_be_its_pins_id(declared):
    """F-97's finalists' row and verdict at F-98's sha256, its read ledgered: no pin of an F-97 path at that sha."""
    c0 = pinned_with_finalists(declared)
    VR.append_rows(declared, f"| E-983 | 2026-11-19 | heldout-finalists: F-97 @ {VR.HT_SHA} list {VR.HT_LIST} -- "
                             "F-97's | x |")
    c1 = head(declared)
    write_ledger(declared, [forged(c1, **{"declaration.ref": "prereg/F-97_copy.md", "heldout.finalists": "E-983"})])
    VR.commit_verdict(declared, VR.verdict_row(984, fid="F-97"))
    gate_refuses(declared)
    assert c0 != c1


def test_m11_the_newest_qualifying_verdict_is_recorded(declared):
    VR.settle(declared, [declared / H.BARS])                            # E-982
    VR.append_rows(declared, VR.verdict_row(983))
    assert dict(reg(declared).heldout)["test_verdict"] == "E-983"
    VR.append_rows(declared, VR.verdict_row(950))                       # newer by place, lower by number
    assert dict(H.read(declared, declaration=H.RD7, purpose="stage_D_scorecard").heldout)["verdict"] == "E-950"
