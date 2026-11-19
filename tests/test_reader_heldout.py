"""Q-158: the reader enforces CHARTER 3.6-3.7's held-out rules (in force since E-210; the red team's B-3 of
`docs/reviews/TEMPLATE_AGENTS_2026-11-18.md`).

What is asserted, one case for each refusal and each pass, every refusal naming its rule (`HeldOutRefused.rule` and
the rule's name at the start of its message):

* **rule 1** -- `heldout_test` and `heldout_stress` are honoured only under a finalists' token for exactly the pinned
  declaration (its id and its sha256), in a row newer than the pin; refused with no such row, a row for another
  declaration, another sha, a row older than the pin, a malformed or misplaced token; a described reading never takes a
  held-out purpose; a family's other purposes are not gated by it (unchanged);
* **rule 2** -- a market's held-out window is read by one declaration: once one family's judged read of it is
  ledgered, another family's (a near-copy, other bytes, its own finalists' row) is refused under every purpose, also
  when the earlier line is in the old format or names no market; another market, or a row opening a new window that
  holds the read's days, admits it; a described reading's or an identity's line spends nothing;
* **rule 3** -- a `registered_design` read of the held-out years is refused under a row without a read token (the rows
  that admitted earlier reads), a token not naming every design or naming another script, outside a clean run, and by
  a second run under the same row; the token's own run is admitted and ledgered; earlier ledger lines stay;
* **rule 4** -- a described reading's judged read is refused before a verdict row for its market, newer than its
  window's opening row; admitted after it;
* the search years are unchanged: no tag, no token, no clean run needed there;
* the tokens' grammar (`heldout_tokens`, `heldout_token_problems`), and this repository's own `DECISIONS.md` holds no
  malformed held-out token.

Everything runs on a temporary git tree at `<tmp>/runs/<name>` (a simulated clean run of it), with small stand-in
files at the data paths, never parsed: `authorise` and `authorise_engine_read` read no data. The real bars, atlas and
ledger are never opened.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import reader as R  # noqa: E402

RUN = "q158-sim"
BARS = "vendor/stage2/data/bars/NQ/bars.parquet"
BARS_ES = "vendor/stage2/data/bars/ES/bars.parquet"
WALKS = "vendor/stage2/data/atlas/A3/walks.parquet"
LINE = "- **Judged-block reads:** `heldout_test`, `heldout_stress`, `stage_C_judgement`\n"
F13, F13_TEXT = "prereg/F-13_search.md", "# F-13: a synthetic design search (Q-158's tests)\n\n" + LINE
#: a near-copy re-declared: one byte changed, the house line kept (the red team's B-3)
F14, F14_TEXT = "prereg/F-14_search.md", "# F-14: a synthetic design search (Q-158's tests).\n\n" + LINE
F15, F15_TEXT = "prereg/F-15_search.md", "# F-15: a third synthetic search\n\n" + LINE
RD7, RD7_TEXT = "prereg/RD-07_reading.md", "# RD-07\n\n- **Judged-block reads:** `stage_D_scorecard`, `heldout_test`\n"
LIST13, LIST14, LIST15 = "1" * 64, "2" * 64, "3" * 64
HELD = (2024, 2026)


def sha_lf(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


BASE_ROWS = (
    f"| E-900 | 2026-11-18 | **F-13 declared**, `{F13}` sha256 `{sha_lf(F13_TEXT)}` | test |",
    f"| E-901 | 2026-11-18 | **F-14 declared**, `{F14}` sha256 `{sha_lf(F14_TEXT)}` | test |",
    f"| E-902 | 2026-11-18 | **F-15 declared**, `{F15}` sha256 `{sha_lf(F15_TEXT)}` | test |",
    f"| E-903 | 2026-11-18 | **RD-07 declared**, `{RD7}` sha256 `{sha_lf(RD7_TEXT)}` | test |",
    "| E-904 | 2026-11-18 | **Readings beside P-14 and P-16** (an older row, no token) | test |",
    "| E-905 | 2026-11-18 | **The identity holds** | test |",
)


def finalists(row: int, fid: str, text: str, lst: str) -> str:
    return f"| E-{row} | 2026-11-18 | heldout-finalists: {fid} @ {sha_lf(text)} list {lst} -- the ordered finalists | x |"


def make_tree(base: Path, rows=()) -> Path:
    t = base / "runs" / RUN
    for d in ("prereg", "identity", "scripts"):
        (t / d).mkdir(parents=True)
    for rel, text in ((F13, F13_TEXT), (F14, F14_TEXT), (F15, F15_TEXT), (RD7, RD7_TEXT)):
        (t / rel).write_bytes(text.encode("utf-8"))
    write_rows(t, (*BASE_ROWS, *rows))
    for rel in (BARS, BARS_ES, WALKS):
        (t / rel).parent.mkdir(parents=True, exist_ok=True)
        (t / rel).write_bytes(b"stand-in, never parsed\n")
    (t / ".gitignore").write_text("vendor/stage2/data/\n", encoding="utf-8")
    git(t, "init", "-q", "-b", "master")
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "the synthetic tree")
    return t


def write_rows(t: Path, rows) -> None:
    text = "# Decisions (synthetic, Q-158)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
    (t / "DECISIONS.md").write_bytes((text + "".join(r + "\n" for r in rows)).encode("utf-8"))


def add_rows(t: Path, *rows: str) -> None:
    """Append decision rows and commit them (a judged read is made by a committed tree)."""
    with (t / "DECISIONS.md").open("a", encoding="utf-8", newline="\n") as f:
        f.writelines(r + "\n" for r in rows)
    git(t, "commit", "-q", "-am", "rows")


@pytest.fixture
def tree(tmp_path, monkeypatch) -> Path:
    t = make_tree(tmp_path)
    monkeypatch.setattr(R, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-1")
    return t


def lines(t: Path) -> list[dict]:
    p = t / "results" / "read_ledger.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def read(t: Path, declaration: str = F13, purpose: str = "heldout_test", market: str = "NQ",
         start: str = "2024-01-02", end: str = "2026-07-16", **kw):
    files = [t / (BARS_ES if market == "ES" else BARS)]
    return R.authorise_engine_read(start, end, purpose=purpose, declaration=declaration, files=files, what="q158",
                                   repo=t, market=market, **kw)


def refused(rule: int, fn, *a, **kw) -> R.HeldOutRefused:
    with pytest.raises(R.HeldOutRefused) as info:
        fn(*a, **kw)
    assert info.value.rule == rule
    assert str(info.value).startswith(f"REFUSED ({R.RULES[rule]})"), str(info.value)
    return info.value


def test_the_rules_are_named_and_the_base_window_is_e208s():
    assert R.HELDOUT_PURPOSES == ("heldout_test", "heldout_stress")
    assert R.BASE_WINDOW_ROW == "E-208" and set(R.RULES) == {1, 2, 3, 4}
    for n, words in ((1, "finalists"), (2, "once per market"), (3, "registered design"), (4, "verdict")):
        assert words in R.RULES[n]
    assert R.heldout_window("", "NQ", R.JUDGED_START, R.JUDGED_END) == ("E-208", R.SEAL_START, R.JUDGED_END)
    assert issubclass(R.HeldOutRefused, R.JudgedBlockSealed), "a caller catching the seal catches these too"


# ------------------------------------------------------------------------------------------- the tokens' grammar


def test_the_tokens_are_read_exactly_and_positionally():
    h, g = "a" * 64, "b" * 64
    text = "\n".join((
        f"| E-950 | 2026-11-18 | heldout-finalists: F-13 @ {h} list {g} -- the list | x |",
        "| E-951 | 2026-11-18 | heldout-window: NQ 2026-07-17 to 2027-07-16 -- bought data | x |",
        "| E-952 | 2026-11-18 | heldout-verdict: NQ F-13 -- F-13 failed its held-out test | x |",
        "| E-953 | 2026-11-18 | heldout-read: P-16,P-14 by scripts/rd04_replay.py -- RD-04 (c)'s replay | x |",
        # never tokens: quoted, emphasised, later in the cell, another cell, short sha, bad market, bad design, a
        # window ending before it starts, a bad day, no text, prose
        f"| E-960 | 2026-11-18 | `heldout-finalists: F-13 @ {h} list {g}` -- quoted | x |",
        f"| E-961 | 2026-11-18 | **heldout-finalists: F-13 @ {h} list {g} -- bold** | x |",
        f"| E-962 | 2026-11-18 | text first; heldout-finalists: F-13 @ {h} list {g} -- later | x |",
        f"| E-963 | 2026-11-18 | text | heldout-finalists: F-13 @ {h} list {g} -- basis |",
        f"| E-964 | 2026-11-18 | heldout-finalists: F-13 @ {h[:63]} list {g} -- short | x |",
        "| E-965 | 2026-11-18 | heldout-verdict: nq F-13 -- lower case market | x |",
        "| E-966 | 2026-11-18 | heldout-read: P-14,P-17 by scripts/x.py -- not a registered design | x |",
        "| E-967 | 2026-11-18 | heldout-window: NQ 2027-07-16 to 2026-07-17 -- reversed | x |",
        "| E-968 | 2026-11-18 | heldout-window: NQ 2026-02-30 to 2027-07-16 -- no such day | x |",
        "| E-969 | 2026-11-18 | heldout-verdict: NQ F-13 --  | x |",
        "| E-970 | 2026-11-18 | Held-out verdict: NQ F-13 -- prose | x |",
        "|E-971| 2026-11-18 | heldout-verdict: NQ F-13 -- the row's start not exact | x |",
        "| E-972 | 2026-11-18 | heldout-read: P-14 by identity/x.py -- not a readings script | x |",
    ))
    toks = R.heldout_tokens(text)
    assert [(t.kind, t.row) for t in toks] == [("finalists", "E-950"), ("window", "E-951"), ("verdict", "E-952"),
                                               ("read", "E-953")]
    f, w, v, r = toks
    assert (f.get("decl"), f.get("sha"), f.get("list"), f.number) == ("F-13", h, g, 950)
    assert (w.get("market"), str(w.get("start")), str(w.get("end"))) == ("NQ", "2026-07-17", "2027-07-16")
    assert (v.get("market"), v.get("decl")) == ("NQ", "F-13")
    assert r.get("designs") == ("P-14", "P-16") and r.get("script") == "scripts/rd04_replay.py"
    assert [t.row for t in R.heldout_tokens(text, "verdict")] == ["E-952"]
    probs = R.heldout_token_problems(text)
    flagged = sorted({p.split(" ")[0] for p in probs})
    assert flagged == ["E-960", "E-961", "E-964", "E-965", "E-966", "E-967", "E-968", "E-969", "E-970", "E-971",
                       "E-972"], probs
    assert R.heldout_token_problems("\n".join(text.splitlines()[:4])) == []


def test_this_repositorys_decision_log_holds_no_malformed_heldout_token():
    assert R.heldout_token_problems((ROOT / "DECISIONS.md").read_text(encoding="utf-8")) == []


# --------------------------------------------------------------------------------- rule 1: the finalists' row first


@pytest.mark.parametrize("purpose", ["heldout_test", "heldout_stress"])
def test_rule1_a_held_out_purpose_is_refused_without_a_finalists_row(tree, purpose):
    e = refused(1, read, tree, purpose=purpose)
    assert "no decision row carries a finalists' token for F-13" in str(e)
    assert lines(tree) == []


@pytest.mark.parametrize("row,why", [
    (finalists(920, "F-14", F14_TEXT, LIST14), "no decision row carries a finalists' token for F-13"),   # another's
    (finalists(920, "F-13", F14_TEXT, LIST13), "not prereg/F-13_search.md's sha256"),                   # other bytes
    (finalists(899, "F-13", F13_TEXT, LIST13), "precede its pin"),                                       # before pin
    ("| E-920 | 2026-11-18 | `heldout-finalists: F-13 @ " + sha_lf(F13_TEXT) + " list " + LIST13 + "` -- quoted | x |",
     "no decision row carries"),                                                                           # malformed
    ("| E-920 | 2026-11-18 | the finalists; heldout-finalists: F-13 @ " + sha_lf(F13_TEXT) + " list " + LIST13
     + " -- later in the cell | x |", "no decision row carries"),                                          # misplaced
])
def test_rule1_refuses_a_finalists_row_that_is_not_this_declarations(tree, row, why):
    add_rows(tree, row)
    for purpose in R.HELDOUT_PURPOSES:
        assert why in str(refused(1, read, tree, purpose=purpose))
    assert lines(tree) == []


def test_rule1_admits_both_purposes_after_the_finalists_row_and_ledgers_it(tree):
    add_rows(tree, finalists(920, "F-13", F13_TEXT, LIST13))
    a = read(tree)
    assert a.judged and a.kind == "family" and a.market == "NQ"
    assert dict(a.heldout) == {"market": "NQ", "window": "E-208", "finalists": "E-920",
                               "finalists_list_sha256": LIST13}
    read(tree, purpose="heldout_stress")
    recs = lines(tree)
    assert [r["purpose"] for r in recs] == ["heldout_test", "heldout_stress"]
    assert recs[0]["heldout"] == {"market": "NQ", "window": "E-208", "finalists": "E-920",
                                  "finalists_list_sha256": LIST13}
    assert R.read_ledger(tree / "results" / "read_ledger.jsonl") == recs, "the line verifies as a ledger line"


def test_rule1_the_newest_finalists_row_after_the_pin_is_recorded(tree):
    add_rows(tree, finalists(920, "F-13", F13_TEXT, LIST13), finalists(921, "F-13", F13_TEXT, "4" * 64))
    assert dict(read(tree).heldout)["finalists"] == "E-921"


def test_rule1_a_described_reading_never_takes_a_held_out_purpose(tree):
    add_rows(tree, "| E-920 | 2026-11-18 | heldout-verdict: NQ F-13 -- F-13's verdict | x |")
    assert "described reading" in str(refused(1, read, tree, declaration=RD7))
    assert read(tree, declaration=RD7, purpose="stage_D_scorecard").kind == "described_reading", \
        "the control: after the verdict its other purpose is admitted"


def test_rule1_does_not_gate_a_familys_other_purposes(tree):
    a = read(tree, purpose="stage_C_judgement")
    assert a.kind == "family" and dict(a.heldout) == {"market": "NQ", "window": "E-208"}
    assert lines(tree)[0]["heldout"] == {"market": "NQ", "window": "E-208"}


def test_the_existing_rules_still_come_first(tree):
    """A purpose not on the line, a choosing purpose, an unpinned file: refused by the seal as before, not by a
    held-out rule."""
    add_rows(tree, finalists(920, "F-13", F13_TEXT, LIST13))
    for purpose, why in (("heldout_other", "does not name"), ("heldout_search", "choice")):
        with pytest.raises(R.JudgedBlockSealed, match=why) as info:
            read(tree, purpose=purpose)
        assert not isinstance(info.value, R.HeldOutRefused)


# ------------------------------------------------------------------------------------------ rule 2: once per market


def spend(t: Path) -> None:
    """F-13's finalists' row and its held-out test, run 1: NQ's base window spent."""
    add_rows(t, finalists(920, "F-13", F13_TEXT, LIST13), finalists(921, "F-14", F14_TEXT, LIST14),
             finalists(922, "F-15", F15_TEXT, LIST15))
    read(t)


@pytest.mark.parametrize("purpose", ["heldout_test", "heldout_stress", "stage_C_judgement"])
def test_rule2_a_second_declaration_is_refused_on_the_same_markets_window(tree, monkeypatch, purpose):
    spend(tree)
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    e = refused(2, read, tree, declaration=F14, purpose=purpose)
    assert "prereg/F-13_search.md" in str(e) and "E-208" in str(e)
    assert len(lines(tree)) == 1, "a refused read writes nothing"


def test_rule2_counts_a_read_in_the_same_run_too(tree):
    spend(tree)
    refused(2, read, tree, declaration=F14)          # the same run id: still another declaration


def test_rule2_leaves_the_same_declaration_to_the_once_rule(tree, monkeypatch):
    spend(tree)
    read(tree, purpose="heldout_stress")             # its other purpose, the same run
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    with pytest.raises(R.JudgedBlockReadTwice) as info:
        read(tree)
    assert not isinstance(info.value, R.HeldOutRefused)


def test_rule2_another_market_is_its_own(tree, monkeypatch):
    spend(tree)
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    a = read(tree, declaration=F14, market="ES")
    assert dict(a.heldout)["market"] == "ES" and lines(tree)[-1]["heldout"]["market"] == "ES"
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-3")
    refused(2, read, tree, declaration=F15, market="ES")      # and ES's window is now F-14's


def test_rule2_a_row_opening_a_new_window_admits_the_next_declaration(tree, monkeypatch):
    spend(tree)
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    add_rows(tree, "| E-930 | 2026-11-18 | heldout-window: ES 2024-01-02 to 2026-07-16 -- another market's | x |",
             "| E-931 | 2026-11-18 | heldout-window: NQ 2025-01-02 to 2026-07-16 -- does not hold 2024 | x |")
    refused(2, read, tree, declaration=F14)                    # neither row's window holds the read's days
    a = read(tree, declaration=F14, start="2025-01-02")        # E-931's window holds this read's
    assert dict(a.heldout)["window"] == "E-931"
    add_rows(tree, "| E-932 | 2026-11-18 | heldout-window: NQ 2024-01-02 to 2026-07-16 -- the operator re-opens | x |")
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-3")
    a = read(tree, declaration=F15)
    assert dict(a.heldout)["window"] == "E-932" and lines(tree)[-1]["heldout"]["window"] == "E-932"
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-4")
    e = refused(2, read, tree, declaration=F14, purpose="heldout_stress")   # E-932's window is F-15's now
    assert "F-15" in str(e)


def put_line(t: Path, rec: dict) -> None:
    p = t / "results" / "read_ledger.jsonl"
    p.parent.mkdir(exist_ok=True)
    with p.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")


def old_line(ref: str, kind: str, files: list[str], purpose: str = "stage_C_judgement", judged: bool = True) -> dict:
    """A ledger line in the format before Q-158 (no `heldout` field)."""
    return {"ledger": 1, "when": "2026-11-17T00:00:00+00:00",
            "who": {"run_id": "earlier@run", "script": None, "commit": "0" * 40},
            "what": {"kind": "engine", "files": [{"path": f} for f in files], "columns": None, "description": "x"},
            "dates": {"start": "2024-01-02", "end": "2026-07-16", "blocks": ["judged"],
                      "judged_first": "2024-01-02" if judged else None, "judged_last": "2026-07-16" if judged else None},
            "declaration": {"ref": ref, "sha256": "f" * 64, "kind": kind}, "purpose": purpose, "repeat": None}


@pytest.mark.parametrize("files,spent_es", [([BARS], False), ([WALKS], True)])
def test_rule2_an_old_format_line_spends_its_market_and_an_unknown_market_every_one(tree, files, spent_es):
    add_rows(tree, finalists(921, "F-14", F14_TEXT, LIST14))
    put_line(tree, old_line("prereg/F-12_old.md", "family", files))
    refused(2, read, tree, declaration=F14)
    if spent_es:
        refused(2, read, tree, declaration=F14, market="ES")      # a line naming no market counts for every market
    else:
        assert read(tree, declaration=F14, market="ES").judged


@pytest.mark.parametrize("line", [
    old_line("prereg/RD-05_modes.md", "described_reading", [BARS]),
    old_line("E-010", "identity", [BARS], purpose="identity"),
    old_line("E-024", "registered_design", [BARS], purpose="registered_design"),
    old_line("prereg/F-12_old.md", "family", [BARS], judged=False),        # a choice-block line (never ledgered)
    {"ledger": None, "when": None, "who": None, "what": None, "dates": None, "declaration": None, "purpose": None,
     "repeat": None},                                                       # a line with every field empty
])
def test_rule2_only_a_familys_judged_line_spends_the_window(tree, line):
    add_rows(tree, finalists(920, "F-13", F13_TEXT, LIST13))
    put_line(tree, line)
    assert read(tree).judged


# --------------------------------------------------------- rule 3: a registered design's held-out read, named by its row

DESIGN = dict(purpose="registered_design", what="q158 design", files=[BARS])


def rd_read(t: Path, declaration: str, design, start: str = "2020-01-02", end: str = "2026-07-16"):
    return R.authorise_engine_read(start, end, declaration=declaration, design=design, repo=t,
                                   **{**DESIGN, "files": [t / BARS]})


@pytest.fixture
def scripted(tree, monkeypatch):
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    return tree


def test_rule3_a_row_without_the_token_admits_no_new_held_out_read(scripted, monkeypatch):
    put_line(scripted, old_line("E-904", "registered_design", [BARS], purpose="registered_design"))
    before = (scripted / "results" / "read_ledger.jsonl").read_bytes()
    e = refused(3, rd_read, scripted, "E-904", ("P-14", "P-16"))
    assert "earlier reads stay valid" in str(e)
    monkeypatch.delenv("S2X_CLEAN_RUN")
    refused(3, rd_read, scripted, "E-904", "P-14")                          # outside a clean run as well
    assert (scripted / "results" / "read_ledger.jsonl").read_bytes() == before, "the earlier line stays, alone"
    a = rd_read(scripted, "E-904", "P-14", end="2023-12-29")                # the search years: unchanged
    assert not a.judged and not a.ledgered and a.heldout is None


def test_rule3_the_token_admits_its_own_run_once_and_ledgers_it(scripted, monkeypatch):
    add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14,P-16 by scripts/replay.py -- P-14 and P-16 "
                       "replayed on the held-out years | x |")
    for design in (("P-14", "P-16"), "P-16"):                               # one run may read as often as it needs
        a = rd_read(scripted, "E-940", design)
        assert a.judged and a.ledgered and dict(a.heldout) == {"read_row": "E-940"}
    recs = lines(scripted)
    assert len(recs) == 2 and recs[0]["heldout"] == {"read_row": "E-940"}
    assert recs[0]["declaration"] == {"ref": "E-940", "sha256": None, "kind": "registered_design",
                                      "designs": ["P-14", "P-16"]}
    monkeypatch.setenv("S2X_RUN_ID", "q158-sim@run-2")
    assert "one row, one run" in str(refused(3, rd_read, scripted, "E-940", "P-14"))
    assert len(lines(scripted)) == 2


@pytest.mark.parametrize("token,design,why", [
    ("heldout-read: P-14 by scripts/replay.py", ("P-14", "P-16"), "not P-16"),
    ("heldout-read: P-14,P-16 by scripts/other.py", "P-14", "scripts/other.py"),
])
def test_rule3_the_token_must_name_the_designs_and_the_script(scripted, token, design, why):
    add_rows(scripted, f"| E-940 | 2026-11-18 | {token} -- P-14 and P-16 replayed | x |")
    assert why in str(refused(3, rd_read, scripted, "E-940", design))
    assert lines(scripted) == []


def test_rule3_a_held_out_read_runs_only_inside_a_clean_run(scripted, monkeypatch):
    add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14,P-16 by scripts/replay.py -- P-14 and P-16 | x |")
    monkeypatch.delenv("S2X_CLEAN_RUN")
    monkeypatch.delenv("S2X_RUN_ID")
    assert "clean run" in str(refused(3, rd_read, scripted, "E-940", "P-14"))
    assert not (scripted / "results" / "read_ledger.jsonl").exists()


def test_rule3_the_existing_registered_design_checks_still_come_first(scripted):
    add_rows(scripted, "| E-940 | 2026-11-18 | heldout-read: P-14 by scripts/replay.py -- P-14 replayed | x |")
    with pytest.raises(R.JudgedBlockSealed, match="does not name") as info:
        rd_read(scripted, "E-940", "P-16")                                  # E-940's row names P-14 only
    assert not isinstance(info.value, R.HeldOutRefused)


# --------------------------------------------------------------------- rule 4: a described reading after the verdict


def test_rule4_a_described_reading_is_refused_before_the_verdict_row(tree):
    e = refused(4, read, tree, declaration=RD7, purpose="stage_D_scorecard")
    assert "NQ" in str(e) and "E-208" in str(e)
    assert lines(tree) == []


@pytest.mark.parametrize("rows", [
    ("| E-920 | 2026-11-18 | heldout-verdict: ES F-13 -- another market's verdict | x |",),
    ("| E-920 | 2026-11-18 | the verdict: heldout-verdict: NQ F-13 -- not at the token's place | x |",),
    ("| E-920 | 2026-11-18 | heldout-verdict: NQ F-13 -- F-13's verdict | x |",
     "| E-921 | 2026-11-18 | heldout-window: NQ 2024-01-02 to 2026-07-16 -- opened after the verdict | x |"),
])
def test_rule4_a_verdict_for_another_market_misplaced_or_older_than_the_window_is_refused(tree, rows):
    add_rows(tree, *rows)
    refused(4, read, tree, declaration=RD7, purpose="stage_D_scorecard")


def test_rule4_admits_after_the_verdict_row_and_ledgers_it(tree):
    add_rows(tree, "| E-920 | 2026-11-18 | heldout-verdict: NQ F-13 -- F-13's held-out verdict | x |")
    a = read(tree, declaration=RD7, purpose="stage_D_scorecard")
    assert a.kind == "described_reading" and dict(a.heldout) == {"market": "NQ", "window": "E-208",
                                                                  "verdict": "E-920"}
    assert lines(tree)[0]["heldout"] == {"market": "NQ", "window": "E-208", "verdict": "E-920"}
    refused(4, read, tree, declaration=RD7, purpose="stage_D_scorecard", market="ES")   # ES has no verdict


# --------------------------------------------------------------------------------- the search years: unchanged


def test_the_search_years_need_no_token(tree, monkeypatch):
    monkeypatch.delenv("S2X_CLEAN_RUN")
    monkeypatch.delenv("S2X_RUN_ID")
    for declaration, purpose in ((F13, None), (F13, "heldout_test"), (RD7, None), (RD7, "stage_D_scorecard"),
                                 ("RD-07", None), (F14, "anything")):
        a = R.authorise("2020-01-02", "2023-12-29", purpose=purpose, declaration=declaration, repo=tree)
        assert not a.judged and not a.ledgered and a.heldout is None
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "replay.py")
    assert not R.authorise("2020-01-02", "2023-12-29", purpose="registered_design", declaration="E-904",
                           design=("P-14", "P-16"), repo=tree).judged
    assert not (tree / "results").exists()


def test_a_market_is_a_plain_root(tree):
    for bad in ("", "N Q", "../NQ", None):
        with pytest.raises(ValueError, match="market"):
            R.authorise("2020-01-02", "2023-12-29", repo=tree, market=bad)
