"""Q-32: the judged block's seal -- `extended/reader.py`, the one door to Stage 2's bars and walks.

What is asserted (the brief's item 4, and what the mechanism needs to be one):

* the blocks are the declared ones, and anything from 2026-07-17 is refused whatever the purpose, before anything is
  read (the confirmation window; not on disk -- refused anyway, also when a store holds such a day);
* a choice-block read needs no tag and writes no ledger line;
* a judged-block read with no purpose, no declaration, a declaration that is missing, a draft, not pinned, edited since
  its pin, or that does not name the purpose on its `Judged-block reads:` line raises; a choice or fitting purpose
  never reads the judged block; a family's judged read runs only inside a clean run of a committed tree; the
  purpose `identity` is allowed from `identity/` scripts under a decision row that names an identity;
* every family's judged read appends exactly one line (who, what, which dates, which declaration and purpose, when)
  and the ledger only grows; an identity's read is checked everywhere but ledgered only inside a clean run (E-026),
  every time it runs there; a second run under the same declaration and purpose is refused unless a decision row names it;
  a ledger that was tampered with refuses the next read; a committed line removed or rewritten later is reported by
  the history check, here on a temporary repository and on this repository's own history;
* Q-158 (`tests/test_reader_heldout.py` holds the held-out rules' own cases): the synthetic log's E-906 and E-907
  carry read tokens naming `scripts/probe.py`, and E-913 a verdict token for NQ, so the reads below that touch the
  held-out years are the ones those rules admit; outside a clean run a registered design's held-out read is refused;
* Q-58 (E-037, E-038): the purpose `registered_design` re-reads only P-14, P-15 and P-16, from `scripts/` only, under
  a decision row naming each design (never a family's or a reading's file), ledgered only inside a clean run; a pinned
  described reading (`prereg/RD-nn_<slug>.md`) declares judged-block reads on exactly the rules a family file does;
* this repository's code reads parquet files only through the reader.

Everything runs on a temporary tree (a git repository with its own `DECISIONS.md`, `prereg/`, a tiny synthetic store
under `vendor/stage2/data/`); the real bars, atlas and ledger are never read or written. Reads through the vendored
engine run in a child process (CLAUDE.md: the vendored tree goes on `sys.path` only in a process of its own).
"""
from __future__ import annotations

import ast
import re
import hashlib
import json
import os
import subprocess
import sys
import textwrap
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import reader as R  # noqa: E402  (importing the reader touches no sys.path, imports no engine)

# ------------------------------------------------------------------------------------------------- the temp tree

FAMILY = "prereg/F-90_seal_test.md"
FAMILY_TEXT = ("# F-90: a synthetic family for the reader's tests (Q-32; not a declaration of this repository)\n\n"
               "Stage A reads the choice block only (`stage_A_supply`); it never reads the judged block.\n\n"
               "- **Judged-block reads:** `stage_C_judgement`, `stage_D_scorecard`\n")
UNPINNED = "prereg/F-91_unpinned.md"
EDITED = "prereg/F-92_edited.md"
EDITED_PINNED_TEXT = "# F-92\n\n- **Judged-block reads:** `stage_C_judgement`\n"
EDITED_TEXT = EDITED_PINNED_TEXT + "\nA sentence added after the pin.\n"
DRAFT = "prereg/DRAFT_F-93_draft.md"
FITTER = "prereg/F-94_fitter.md"
FITTER_TEXT = "# F-94\n\nJudged-block reads: `stage_B_fit`, `stage_C_judgement`\n"
NAMED_LINE = "- **Judged-block reads:** `stage_C_judgement`\n"
#: a family that names `registered_design` on its line (Q-58: never valid for a family) and a judgement beside it
RIDER = "prereg/F-95_design_rider.md"
RIDER_TEXT = "# F-95\n\n- **Judged-block reads:** `registered_design`, `stage_C_judgement`\n"
#: described readings (`prereg/RD-nn_<slug>.md`, E-023 (1), E-025 (1); Q-58): admitted on the rules F- files follow
READING = "prereg/RD-01_reading_test.md"
READING_TEXT = ("# RD-01: a synthetic described reading for the reader's tests (Q-58; not a declaration of this "
                "repository)\n\n- **Judged-block reads:** `stage_D_scorecard`\n")
RD_UNPINNED = "prereg/RD-02_unpinned.md"
RD_EDITED = "prereg/RD-03_edited.md"
RD_EDITED_PINNED_TEXT = "# RD-03\n\n- **Judged-block reads:** `stage_D_scorecard`\n"
RD_EDITED_TEXT = RD_EDITED_PINNED_TEXT + "\nA sentence added after the pin.\n"
RD_DRAFT = "prereg/DRAFT_RD_draft.md"
RD_FITTER = "prereg/RD-04_fitter.md"
RD_FITTER_TEXT = "# RD-04\n\n- **Judged-block reads:** `stage_B_fit`, `stage_D_scorecard`\n"

DAYS =("2023-12-28", "2023-12-29", "2024-01-02", "2026-07-16", "2026-07-17")
BARS = "vendor/stage2/data/bars/NQ/bars.parquet"
WALKS = "vendor/stage2/data/atlas/A3/walks.parquet"
RUN = "q32-sim"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def sha_lf(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def decisions(h90: str, h92: str, h94: str) -> str:
    return ("# Decisions (synthetic, Q-32's tests)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
            f"| E-900 | 2026-11-16 | **F-90 declared**, `{FAMILY}` sha256 `{h90}` | test |\n"
            "| E-901 | 2026-11-16 | **The identity holds** at every registered path | test |\n"
            f"| E-902 | 2026-11-16 | **F-92 declared**, `{EDITED}` sha256 `{h92}` | test |\n"
            f"| E-903 | 2026-11-16 | **A second stage-C read of `{FAMILY}`** after run 1 crashed | test |\n"
            "| E-904 | 2026-11-16 | **A row about nothing in particular** | test |\n"
            f"| E-905 | 2026-11-16 | **F-94 declared**, `{FITTER}` sha256 `{h94}` | test |\n"
            "| E-906 | 2026-11-16 | heldout-read: P-14,P-15,P-16 by scripts/probe.py -- **Readings beside P-14, P-15 "
            "and P-16** (Stage 2's registered designs) | test |\n"
            "| E-907 | 2026-11-16 | heldout-read: P-14 by scripts/probe.py -- **P-14's validation readings** (P-140 and "
            "XP-16 are other names) | test |\n"
            f"| E-908 | 2026-11-16 | **F-95 declared**, `{RIDER}` sha256 `{sha_lf(RIDER_TEXT)}` | test |\n"
            f"| E-909 | 2026-11-16 | **RD-01 declared**, `{READING}` sha256 `{sha_lf(READING_TEXT)}` | test |\n"
            f"| E-910 | 2026-11-16 | **RD-03 declared**, `{RD_EDITED}` sha256 `{sha_lf(RD_EDITED_PINNED_TEXT)}` | test |\n"
            f"| E-911 | 2026-11-16 | **RD-04 declared**, `{RD_FITTER}` sha256 `{sha_lf(RD_FITTER_TEXT)}` | test |\n"
            "| E-912 | 2026-11-16 | **A second stage-D read of RD-01** after its run 1 crashed | test |\n"
            "| E-913 | 2026-11-16 | heldout-verdict: NQ F-90 -- NQ's held-out test has its verdict (Q-158: a "
            "described reading reads the held-out years only after it) | test |\n")


def bars_frame() -> pd.DataFrame:
    rows = []
    for d in DAYS:
        y, m, dd = (int(x) for x in d.split("-"))
        t0 = int(datetime(y, m, dd, 14, 30, tzinfo=timezone.utc).timestamp())
        for i in range(3):
            p = 17000.0 + i
            rows.append({"ts": t0 + 60 * i, "day": d, "contract": "NQH4", "open": p, "high": p + 1.0, "low": p - 1.0,
                         "close": p + 0.25, "volume": 10 + i})
    return pd.DataFrame(rows)


def walks_frame() -> pd.DataFrame:
    return pd.DataFrame({"date": list(DAYS), "slot": [930] * len(DAYS), "side": [1] * len(DAYS),
                         "k150_1": [1] * len(DAYS)})


def make_tree(base: Path, name: str = RUN) -> Path:
    """A temporary tree at `<base>/runs/<name>` (so a clean run can be simulated): a git repository with the synthetic
    declarations and decision rows, a tiny store and walk table (git-ignored, as the real ones are), a data manifest."""
    t = base / "runs" / name
    (t / "prereg").mkdir(parents=True)
    (t / "identity").mkdir()
    for rel, text in ((FAMILY, FAMILY_TEXT), (UNPINNED, "# F-91\n\n" + NAMED_LINE), (EDITED, EDITED_TEXT),
                      (DRAFT, "# DRAFT F-93\n\n" + NAMED_LINE), (FITTER, FITTER_TEXT), (RIDER, RIDER_TEXT),
                      (READING, READING_TEXT), (RD_UNPINNED, "# RD-02\n\n- **Judged-block reads:** `stage_D_scorecard`\n"),
                      (RD_EDITED, RD_EDITED_TEXT), (RD_DRAFT, "# DRAFT RD\n\n- **Judged-block reads:** `stage_D_scorecard`\n"),
                      (RD_FITTER, RD_FITTER_TEXT)):
        (t / rel).write_bytes(text.encode("utf-8"))
    (t / "DECISIONS.md").write_bytes(decisions(sha_lf(FAMILY_TEXT), sha_lf(EDITED_PINNED_TEXT),
                                               sha_lf(FITTER_TEXT)).encode("utf-8"))
    (t / "code.py").write_text("x = 1\n", encoding="utf-8")
    (t / ".gitignore").write_text("vendor/stage2/data/bars/\nvendor/stage2/data/atlas/\n", encoding="utf-8")
    store, atlas = t / BARS, t / WALKS
    store.parent.mkdir(parents=True)
    atlas.parent.mkdir(parents=True)
    bars_frame().to_parquet(store, index=False)
    (store.parent / "manifest.json").write_text('{"root": "NQ"}\n', encoding="utf-8")
    walks_frame().to_parquet(atlas, index=False)
    (atlas.parent / "manifest.json").write_text('{"inputs": {}}\n', encoding="utf-8")
    (t / "vendor" / "DATA_MANIFEST_stage2.sha256").write_text(
        f"{file_sha(store)}  data/bars/NQ/bars.parquet\n{file_sha(atlas)}  data/atlas/A3/walks.parquet\n",
        encoding="utf-8")
    git(t, "init", "-q", "-b", "master")
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "the synthetic tree")
    return t


@pytest.fixture
def tree(tmp_path, monkeypatch) -> Path:
    """The temporary tree, inside a simulated clean run of it (the marker names it, a run id is set)."""
    t = make_tree(tmp_path)
    monkeypatch.setattr(R, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    monkeypatch.setenv("S2X_RUN_ID", "q32-sim@run-1")
    return t


def ledger_lines(t: Path) -> list[str]:
    p = t / "results" / "read_ledger.jsonl"
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else []


def judged(t: Path, **kw):
    """A judged-block read recorded without data (the engine-read door), F-90's stage C by default."""
    args = {"purpose": "stage_C_judgement", "declaration": FAMILY, "files": [t / BARS], "what": "test read",
            "repo": t, **kw}
    return R.authorise_engine_read("2024-01-02", "2026-07-16", **args)


# ------------------------------------------------------------------------------- the blocks; the confirmation window


def test_the_blocks_are_the_declared_ones():
    assert (R.CHOICE_START, R.CHOICE_END) == (date(2020, 1, 2), date(2023, 12, 29))
    assert (R.JUDGED_START, R.JUDGED_END) == (date(2024, 1, 2), date(2026, 7, 16))
    assert R.CONFIRMATION_START == date(2026, 7, 17)
    assert R.LEDGER_REL == "results/read_ledger.jsonl"


@pytest.mark.parametrize("start,end,want", [
    ("2020-01-02", "2023-12-29", ("choice",)),
    ("2023-12-29", "2024-01-02", ("choice", "judged")),
    ("2024-01-02", "2026-07-16", ("judged",)),
    ("2023-12-30", "2023-12-30", ("judged",)),          # the gap after the choice block is under the seal
    (date(2021, 5, 3), pd.Timestamp("2021-05-04"), ("choice",)),
])
def test_blocks_of_a_span(start, end, want):
    assert R.blocks_of(start, end) == want


@pytest.mark.parametrize("start,end", [("2026-07-16", "2026-07-17"), ("2026-07-17", "2026-07-17"),
                                       ("2020-01-02", "2027-01-04"), ("2030-01-02", "2030-01-03")])
@pytest.mark.parametrize("who", ["untagged", "identity", "family"])
def test_the_confirmation_window_is_refused_whatever_the_purpose(tree, monkeypatch, start, end, who):
    monkeypatch.setattr(R, "_main_script", lambda: tree / "identity" / "probe.py")
    kw = {"untagged": {}, "identity": {"purpose": "identity", "declaration": "E-901"},
          "family": {"purpose": "stage_C_judgement", "declaration": FAMILY}}[who]
    with pytest.raises(R.ConfirmationWindowRefused, match="2026-07-17"):
        R.authorise(start, end, repo=tree, **kw)
    with pytest.raises(R.ConfirmationWindowRefused):
        R.authorise_engine_read(start, end, files=[tree / BARS], what="t", repo=tree, **kw)
    assert ledger_lines(tree) == [], "a refused read writes nothing"


def test_spans_before_the_choice_block_or_reversed_are_refused(tree):
    with pytest.raises(R.ReadRefused, match="2020-01-02"):
        R.authorise("2019-12-31", "2020-01-03", repo=tree)
    with pytest.raises(ValueError):
        R.authorise("2021-01-05", "2021-01-04", repo=tree)
    with pytest.raises(TypeError):
        R.authorise(20210105, "2021-01-06", repo=tree)


def test_returned_rows_are_checked_after_the_read():
    R.check_returned(["2024-01-02", "2026-07-16"], "2024-01-02", "2026-07-16")
    with pytest.raises(R.ConfirmationWindowRefused):
        R.check_returned(["2024-01-02", "2026-07-17"], "2024-01-02", "2026-07-17")
    with pytest.raises(R.ReadRefused):
        R.check_returned(["2023-12-29", "2024-01-03"], "2024-01-02", "2026-07-16")   # outside what was authorised


# ---------------------------------------------------------------------------------------------------------- the seal


def test_a_choice_block_read_needs_no_tag(tree):
    a = R.authorise("2020-01-02", "2023-12-29", repo=tree)
    assert not a.judged and a.blocks == ("choice",) and a.purpose is None and not a.ledgered
    a = R.authorise_engine_read("2020-01-02", "2023-12-29", files=[tree / BARS], what="t", repo=tree)
    assert not a.judged and not a.ledgered
    for declaration in ("F-90", FAMILY, DRAFT, "E-904"):              # named, it must exist (no pin needed)
        assert R.authorise("2020-01-02", "2023-12-29", purpose="stage_A_supply", declaration=declaration,
                           repo=tree).declaration == declaration
    for declaration in ("F-99", "prereg/F-99_x.md", "E-999"):
        with pytest.raises(R.ReadRefused, match="does not exist"):
            R.authorise("2020-01-02", "2023-12-29", declaration=declaration, repo=tree)
    assert ledger_lines(tree) == [], "only judged-block reads are ledgered"


@pytest.mark.parametrize("kw", [{}, {"purpose": "stage_C_judgement"}, {"declaration": FAMILY}])
def test_an_untagged_judged_read_raises(tree, kw):
    with pytest.raises(R.JudgedBlockSealed, match="judged block"):
        R.authorise("2023-12-29", "2024-01-02", repo=tree, **kw)
    assert ledger_lines(tree) == []


@pytest.mark.parametrize("declaration,why", [
    (UNPINNED, "not pinned"),
    (DRAFT, "prereg/F-"),
    ("prereg/F-99_missing.md", "does not exist"),
    ("F-99", "does not exist"),
    (EDITED, "edited since"),
    ("vendor/stage2/prereg/P-16_x.md", "prereg/F-"),
])
def test_a_tagged_read_under_an_unpinned_declaration_raises(tree, declaration, why):
    with pytest.raises(R.JudgedBlockSealed, match=why):
        R.authorise("2024-01-02", "2026-07-16", purpose="stage_C_judgement", declaration=declaration, repo=tree)
    assert ledger_lines(tree) == []


def test_the_declaration_must_name_the_purpose_on_its_judged_block_line(tree):
    # named in prose only: not a declaration of a judged read
    with pytest.raises(R.JudgedBlockSealed, match="does not name"):
        R.authorise("2024-01-02", "2026-07-16", purpose="stage_A_supply", declaration=FAMILY, repo=tree)
    for purpose in ("stage_C_judgement", "stage_D_scorecard"):
        a = R.authorise("2024-01-02", "2026-07-16", purpose=purpose, declaration=FAMILY, repo=tree)
        assert a.judged and a.kind == "family" and a.declaration == FAMILY and a.ledgered
        assert a.declaration_sha256 == sha_lf(FAMILY_TEXT)
    a = R.authorise("2024-01-02", "2024-01-02", purpose="stage_C_judgement", declaration="F-90", repo=tree)
    assert a.declaration == FAMILY, "an F-id names its one file"


def test_crlf_on_disk_keeps_the_pin(tree):
    (tree / FAMILY).write_bytes(FAMILY_TEXT.replace("\n", "\r\n").encode("utf-8"))
    git(tree, "commit", "-q", "-am", "crlf")
    assert R.authorise("2024-01-02", "2026-07-16", purpose="stage_C_judgement", declaration=FAMILY, repo=tree).judged


def test_choice_and_fitting_purposes_never_read_the_judged_block(tree):
    # F-94 is pinned and names `stage_B_fit` on its line; a fitting purpose is refused there anyway (audit H-2, R-4)
    with pytest.raises(R.JudgedBlockSealed, match="choice"):
        R.authorise("2024-01-02", "2026-07-16", purpose="stage_B_fit", declaration=FITTER, repo=tree)
    assert R.authorise("2024-01-02", "2026-07-16", purpose="stage_C_judgement", declaration=FITTER, repo=tree).judged
    assert R.authorise("2020-01-02", "2023-12-29", purpose="stage_B_fit", declaration=FITTER, repo=tree).blocks == \
        ("choice",)


@pytest.mark.parametrize("purpose", ["", "stage C", "stage-C", "x" * 65, "1stage"])
def test_a_purpose_is_a_plain_name(tree, purpose):
    with pytest.raises(ValueError):
        R.authorise("2020-01-02", "2020-01-03", purpose=purpose, repo=tree)


def test_a_family_judged_read_needs_a_clean_run_of_a_committed_tree(tree, monkeypatch, tmp_path):
    ok = {"purpose": "stage_C_judgement", "declaration": FAMILY, "repo": tree}
    monkeypatch.delenv("S2X_CLEAN_RUN")
    with pytest.raises(R.JudgedBlockSealed, match="clean run"):
        R.authorise("2024-01-02", "2026-07-16", **ok)
    monkeypatch.setenv("S2X_CLEAN_RUN", "another-run")                  # the marker names another checkout
    with pytest.raises(R.JudgedBlockSealed, match="clean run"):
        R.authorise("2024-01-02", "2026-07-16", **ok)
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    monkeypatch.delenv("S2X_RUN_ID")
    with pytest.raises(R.JudgedBlockSealed, match="S2X_RUN_ID"):
        R.authorise("2024-01-02", "2026-07-16", **ok)
    monkeypatch.setenv("S2X_RUN_ID", "q32-sim@run-1")
    (tree / "results").mkdir()
    (tree / "results" / "x.csv").write_text("a\n1\n", encoding="utf-8")   # a run's own output does not count
    assert R.authorise("2024-01-02", "2026-07-16", **ok).judged
    (tree / "code.py").write_text("x = 2\n", encoding="utf-8")            # uncommitted code does
    with pytest.raises(R.JudgedBlockSealed, match="uncommitted"):
        R.authorise("2024-01-02", "2026-07-16", **ok)


def test_identity_reads_are_allowed_from_identity_scripts(tree, monkeypatch):
    monkeypatch.delenv("S2X_CLEAN_RUN")                                    # identities run anywhere (E-004, E-010)
    monkeypatch.setattr(R, "_main_script", lambda: tree / "identity" / "probe.py")
    a = R.authorise("2020-01-02", "2026-07-16", purpose="identity", declaration="E-901", repo=tree)
    assert a.judged and a.kind == "identity" and a.declaration == "E-901" and not a.ledgered
    for declaration, why in (("E-904", "identity"), ("E-999", "no decision row"), (FAMILY, "decision row"),
                             (None, "decision row")):
        with pytest.raises(R.JudgedBlockSealed, match=why):
            R.authorise("2020-01-02", "2026-07-16", purpose="identity", declaration=declaration, repo=tree)
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "probe.py")
    with pytest.raises(R.JudgedBlockSealed, match="identity/"):
        R.authorise("2020-01-02", "2026-07-16", purpose="identity", declaration="E-901", repo=tree)
    monkeypatch.setattr(R, "_main_script", lambda: None)                  # python -c: no script at all
    with pytest.raises(R.JudgedBlockSealed, match="identity/"):
        R.authorise("2020-01-02", "2026-07-16", purpose="identity", declaration="E-901", repo=tree)


# ------------------------------------------------------------- Q-58: Stage 2's registered designs re-read (E-037)

DESIGN = dict(purpose="registered_design", declaration="E-906", what="registered design")


def test_a_registered_design_is_re_read_from_scripts_ledgered_only_inside_a_clean_run(tree, monkeypatch):
    """E-037: `registered_design` re-reads Stage 2's own judged designs from this repository's `scripts/`, under a
    decision row naming them; checked everywhere, ledgered only inside a clean run, as an identity's read is."""
    led = tree / "results" / "read_ledger.jsonl"
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "probe.py")
    monkeypatch.delenv("S2X_CLEAN_RUN")
    monkeypatch.delenv("S2X_RUN_ID")
    for design, want in (("P-14", ("P-14",)), (("P-16", "P-14"), ("P-14", "P-16")),
                         (["P-14", "P-15", "P-16", "P-15"], ("P-14", "P-15", "P-16"))):
        a = R.authorise_engine_read("2020-01-02", "2023-12-29", design=design, files=[tree / BARS, tree / WALKS],
                                    repo=tree, **DESIGN)
        assert not a.judged and a.declaration == "E-906" and a.designs == want
        assert not a.ledgered and a.declaration_sha256 is None
        # Q-158 (rule 3): outside a clean run a held-out read is refused, even under a row whose token names it
        with pytest.raises(R.HeldOutRefused, match="clean run"):
            R.authorise_engine_read("2020-01-02", "2026-07-16", design=design, files=[tree / BARS, tree / WALKS],
                                    repo=tree, **DESIGN)
    assert not led.exists(), "outside a clean run no ledger file appears"
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    monkeypatch.setenv("S2X_RUN_ID", "q58-sim@run-1")
    for i in range(2):                                            # one run reads as often as it needs
        a = R.authorise_engine_read("2020-01-02", "2026-07-16", design=("P-14", "P-16"), files=[tree / BARS],
                                    repo=tree, **DESIGN)
        assert a.ledgered and len(ledger_lines(tree)) == i + 1
    rec = json.loads(ledger_lines(tree)[-1])
    assert rec["purpose"] == "registered_design" and rec["what"]["kind"] == "engine"
    assert rec["declaration"] == {"ref": "E-906", "sha256": None, "kind": "registered_design",
                                  "designs": ["P-14", "P-16"]}
    assert rec["who"]["script"] == "scripts/probe.py" and rec["who"]["clean_run"] == RUN
    assert rec["dates"]["blocks"] == ["choice", "judged"]
    monkeypatch.setenv("S2X_CLEAN_RUN", "another-run")            # a marker naming another checkout is refused
    with pytest.raises(R.JudgedBlockSealed, match="clean run"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", design="P-14", files=[tree / BARS], repo=tree, **DESIGN)
    assert len(ledger_lines(tree)) == 2


@pytest.mark.parametrize("where", ["identity", "root", "none"])
def test_a_registered_design_is_refused_outside_scripts(tree, monkeypatch, where):
    script = {"identity": tree / "identity" / "probe.py", "root": tree / "probe.py", "none": None}[where]
    monkeypatch.setattr(R, "_main_script", lambda: script)
    for clean in (False, True):
        if not clean:
            monkeypatch.delenv("S2X_CLEAN_RUN", raising=False)
        else:
            monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
        with pytest.raises(R.JudgedBlockSealed, match="scripts/"):
            R.authorise_engine_read("2020-01-02", "2026-07-16", design="P-14", files=[tree / BARS], repo=tree,
                                    **DESIGN)
    assert ledger_lines(tree) == []


@pytest.mark.parametrize("design", ["P-13", "P-17", "p14", "P14", "P-14 ", "F-90", "", (), ["P-14", "P-12"], None])
def test_a_registered_design_is_refused_for_any_other_design(tree, monkeypatch, design):
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "probe.py")
    with pytest.raises(R.JudgedBlockSealed, match="registered design"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", design=design, files=[tree / BARS], repo=tree, **DESIGN)
    with pytest.raises(R.JudgedBlockSealed, match="registered design"):     # on the choice block as well
        R.authorise("2020-01-02", "2023-12-29", design=design, repo=tree, **{k: v for k, v in DESIGN.items()
                                                                            if k != "what"})
    assert ledger_lines(tree) == []


def test_a_registered_design_is_never_a_familys_and_needs_a_row_naming_it(tree, monkeypatch):
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "probe.py")
    kw = dict(files=[tree / BARS], repo=tree, what="registered design")
    # a family -- even a pinned one naming the purpose on its line -- never declares a registered design's re-read
    for declaration in (RIDER, "F-95", FAMILY, READING, "RD-01", None):
        with pytest.raises(R.JudgedBlockSealed, match="decision row"):
            R.authorise_engine_read("2020-01-02", "2026-07-16", purpose="registered_design", declaration=declaration,
                                    design="P-14", **kw)
    assert R.authorise_engine_read("2024-01-02", "2026-07-16", purpose="stage_C_judgement", declaration=RIDER,
                                   **kw).kind == "family", "the control: F-95 is a valid family for its judgement"
    for declaration, design, why in (("E-999", "P-14", "no decision row"), ("E-904", "P-14", "does not name"),
                                     ("E-907", "P-16", "does not name"), ("E-907", ("P-14", "P-15"), "does not name")):
        with pytest.raises(R.JudgedBlockSealed, match=why):
            R.authorise_engine_read("2020-01-02", "2026-07-16", purpose="registered_design", declaration=declaration,
                                    design=design, **kw)
    a = R.authorise_engine_read("2020-01-02", "2026-07-16", purpose="registered_design", declaration="E-907",
                                design="P-14", **kw)
    assert a.designs == ("P-14",) and a.declaration == "E-907", "E-907 names P-14 (and not P-140 or XP-16)"
    # a design names a registered design's purpose only
    for purpose, declaration in (("identity", "E-901"), ("stage_C_judgement", FAMILY)):
        with pytest.raises(ValueError, match="registered_design"):
            R.authorise("2020-01-02", "2026-07-16", purpose=purpose, declaration=declaration, design="P-14",
                        repo=tree)
    assert [json.loads(x)["declaration"]["ref"] for x in ledger_lines(tree)] == [RIDER, "E-907"], \
        "the control family read and E-907's re-read ledgered (the tree is a simulated clean run); nothing refused was"


# --------------------------------------------------------------- Q-58: described readings (RD- files, E-023 (1))


def test_a_pinned_described_reading_authorises_its_judged_reads_on_the_family_rules(tree, monkeypatch):
    """A pinned `prereg/RD-nn_<slug>.md` declares judged-block reads exactly as a family file does: pinned in a row and
    unedited since, naming the purpose on its `Judged-block reads:` line, no choosing or fitting purpose, inside a
    clean run of committed code, once per purpose unless a row names another read."""
    for declaration in (READING, "RD-01"):
        a = R.authorise("2024-01-02", "2026-07-16", purpose="stage_D_scorecard", declaration=declaration, repo=tree)
        assert a.judged and a.ledgered and a.declaration == READING and a.kind == "described_reading"
        assert a.declaration_sha256 == sha_lf(READING_TEXT)
    judged(tree, purpose="stage_D_scorecard", declaration="RD-01")
    rec = json.loads(ledger_lines(tree)[-1])
    assert rec["declaration"] == {"ref": READING, "sha256": sha_lf(READING_TEXT), "kind": "described_reading"}
    judged(tree, purpose="stage_D_scorecard", declaration=READING)            # the same run may read again
    monkeypatch.setenv("S2X_RUN_ID", "q58-sim@run-2")
    with pytest.raises(R.JudgedBlockReadTwice, match="once"):
        judged(tree, purpose="stage_D_scorecard", declaration=READING)
    with pytest.raises(R.JudgedBlockSealed, match="does not name"):
        judged(tree, purpose="stage_D_scorecard", declaration=READING, repeat="E-903")   # a row naming F-90 only
    judged(tree, purpose="stage_D_scorecard", declaration=READING, repeat="E-912")
    assert json.loads(ledger_lines(tree)[-1])["repeat"] == "E-912" and len(ledger_lines(tree)) == 3
    # the choice block: the declaration named must exist
    assert R.authorise("2020-01-02", "2023-12-29", declaration="RD-01", repo=tree).declaration == "RD-01"
    with pytest.raises(R.ReadRefused, match="does not exist"):
        R.authorise("2020-01-02", "2023-12-29", declaration="RD-99", repo=tree)


@pytest.mark.parametrize("declaration,purpose,why", [
    (READING, "stage_C_judgement", "does not name"),         # a purpose its line does not name
    (RD_UNPINNED, "stage_D_scorecard", "not pinned"),
    ("RD-02", "stage_D_scorecard", "not pinned"),
    (RD_EDITED, "stage_D_scorecard", "edited since"),
    (RD_DRAFT, "stage_D_scorecard", "prereg/RD-"),           # a draft is no declaration
    ("RD-99", "stage_D_scorecard", "does not exist"),
    ("prereg/RD-99_missing.md", "stage_D_scorecard", "does not exist"),
    (RD_FITTER, "stage_B_fit", "choice"),                    # a fitting purpose, though its line names it
])
def test_a_described_reading_that_does_not_authorise_is_refused(tree, declaration, purpose, why):
    with pytest.raises(R.JudgedBlockSealed, match=why):
        R.authorise("2024-01-02", "2026-07-16", purpose=purpose, declaration=declaration, repo=tree)
    assert ledger_lines(tree) == []


def test_a_described_readings_judged_read_needs_a_clean_run_of_a_committed_tree(tree, monkeypatch):
    ok = {"purpose": "stage_D_scorecard", "declaration": READING, "repo": tree}
    assert R.authorise("2024-01-02", "2026-07-16", **ok).judged
    assert R.authorise("2024-01-02", "2026-07-16", purpose="stage_D_scorecard", declaration=RD_FITTER,
                       repo=tree).judged, "the control: RD-04 is valid for the purpose that does not fit"
    monkeypatch.delenv("S2X_CLEAN_RUN")
    with pytest.raises(R.JudgedBlockSealed, match="clean run"):
        R.authorise("2024-01-02", "2026-07-16", **ok)
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    (tree / "code.py").write_text("x = 2\n", encoding="utf-8")
    with pytest.raises(R.JudgedBlockSealed, match="uncommitted"):
        R.authorise("2024-01-02", "2026-07-16", **ok)


def test_the_reader_reads_rd_pins_as_the_declarations_test_does():
    h = "a" * 64
    text = f"`prereg/RD-07_x.md` sha256 `{h}`; `prereg/F-12_y.md` sha256 `{h}`; `prereg/DRAFT_RD_z.md` sha256 `{h}`"
    assert R.pins(text) == {"prereg/RD-07_x.md": {h}, "prereg/F-12_y.md": {h}}


def test_declared_purposes_are_read_from_the_declared_line_only():
    text = ("Stage A: `stage_A_supply` never reads the judged block. judged-block reads: `stage_X` in prose\n"
            "- **Judged-block reads:** `stage_C_judgement`, `stage_D_scorecard` (one read each)\n"
            "> Judged-block reads (extended.reader): `stage_E_beside`\n"
            "Judged-block reads: none\n")
    assert R.declared_purposes(text) == frozenset({"stage_C_judgement", "stage_D_scorecard", "stage_E_beside"})
    assert R.declared_purposes("# nothing here\n") == frozenset()


def test_pins_are_read_as_the_declarations_test_reads_them():
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    import re
    want = re.findall(r"`(prereg/(?:F|RD)-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`", text)   # as E-025 reads them
    got = R.pins(text)
    assert want and {(p, h) for p, hs in got.items() for h in hs} == set(want)


# -------------------------------------------------------------------------------------------------------- the ledger


def test_a_judged_read_writes_one_ledger_line(tree):
    judged(tree)
    lines = ledger_lines(tree)
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["ledger"] == 1 and rec["purpose"] == "stage_C_judgement" and rec["repeat"] is None
    assert rec["declaration"] == {"ref": FAMILY, "sha256": sha_lf(FAMILY_TEXT), "kind": "family"}
    assert rec["dates"] == {"start": "2024-01-02", "end": "2026-07-16", "blocks": ["judged"],
                            "judged_first": "2024-01-02", "judged_last": "2026-07-16"}
    who = rec["who"]
    assert who["commit"] == git(tree, "rev-parse", "HEAD") and who["dirty"] is False
    assert who["clean_run"] == RUN and who["run_id"] == "q32-sim@run-1" and who["pid"] == os.getpid()
    assert who["caller"].startswith("tests/test_reader.py:"), who["caller"]
    assert "script" in who and "argv" in who
    f = rec["what"]["files"]
    assert f == [{"path": BARS, "sha256": file_sha(tree / BARS), "bytes": (tree / BARS).stat().st_size,
                  "in_data_manifest": True}]
    assert rec["what"]["kind"] == "engine" and rec["what"]["description"] == "test read"
    when = datetime.fromisoformat(rec["when"])
    assert when.tzinfo is not None and abs((datetime.now(timezone.utc) - when).total_seconds()) < 120
    assert lines[0] == json.dumps(rec, sort_keys=True, separators=(",", ":")), "one canonical line"


def test_the_ledger_only_grows(tree):
    judged(tree)
    first = (tree / "results" / "read_ledger.jsonl").read_bytes()
    judged(tree, purpose="stage_D_scorecard")
    after = (tree / "results" / "read_ledger.jsonl").read_bytes()
    assert after.startswith(first) and len(ledger_lines(tree)) == 2


def test_a_second_run_under_the_same_declaration_and_purpose_raises(tree, monkeypatch):
    judged(tree)
    judged(tree)                                                  # the same run may read again (bars, then walks)
    monkeypatch.setenv("S2X_RUN_ID", "q32-sim@run-2")
    with pytest.raises(R.JudgedBlockReadTwice, match="once"):
        judged(tree)
    assert len(ledger_lines(tree)) == 2
    judged(tree, purpose="stage_D_scorecard")                     # another declared purpose: its own first read
    with pytest.raises(R.JudgedBlockSealed, match="does not name"):
        judged(tree, repeat="E-904")                              # a row that does not name the declaration
    judged(tree, repeat="E-903")                                  # the row that authorises the second read
    assert json.loads(ledger_lines(tree)[-1])["repeat"] == "E-903"
    monkeypatch.setenv("S2X_RUN_ID", "q32-sim@run-3")
    with pytest.raises(R.JudgedBlockReadTwice, match="E-903"):
        judged(tree, repeat="E-903")                              # one row, one more run


def test_identity_reads_are_ledgered_only_inside_a_clean_run_and_never_limited(tree, monkeypatch):
    """E-026 (the lead's rule, Q-48): an identity's read is checked everywhere and ledgered only inside a clean run
    (`S2X_CLEAN_RUN` set), so a worktree's or the suite's identity runs write nothing; inside one every run is ledgered
    (never limited to once), under the clean run's own checks."""
    ident = dict(purpose="identity", declaration="E-901", files=[tree / BARS, tree / WALKS], what="identity", repo=tree)
    led = tree / "results" / "read_ledger.jsonl"
    monkeypatch.delenv("S2X_CLEAN_RUN")
    monkeypatch.delenv("S2X_RUN_ID")
    monkeypatch.setattr(R, "_main_script", lambda: tree / "identity" / "probe.py")
    for _ in range(3):
        a = R.authorise_engine_read("2020-01-02", "2026-07-16", **ident)
        assert a.judged and a.kind == "identity" and not a.ledgered
    assert not led.exists(), "outside a clean run no ledger file appears"
    # outside a clean run the authorisation is still checked, before anything is read
    with pytest.raises(R.JudgedBlockSealed, match="does not mention an identity"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", **{**ident, "declaration": "E-904"})
    with pytest.raises(R.JudgedBlockSealed, match="no decision row"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", **{**ident, "declaration": "E-999"})
    with pytest.raises(FileNotFoundError):
        R.authorise_engine_read("2020-01-02", "2026-07-16",
                                **{**ident, "files": [tree / "vendor/stage2/data/atlas/A9/walks.parquet"]})
    monkeypatch.setattr(R, "_main_script", lambda: tree / "scripts" / "probe.py")
    with pytest.raises(R.JudgedBlockSealed, match="identity/"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", **ident)
    assert not led.exists()

    # inside a clean run: one line a read, every time
    monkeypatch.setattr(R, "_main_script", lambda: tree / "identity" / "probe.py")
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    monkeypatch.setenv("S2X_RUN_ID", "q32-sim@run-1")
    for i in range(3):
        if i == 2:
            monkeypatch.setenv("S2X_RUN_ID", "q32-sim@run-2")            # another run: never limited to once
        a = R.authorise_engine_read("2020-01-02", "2026-07-16", **ident)
        assert a.judged and a.kind == "identity" and a.ledgered
        assert len(ledger_lines(tree)) == i + 1
    recs = [json.loads(x) for x in ledger_lines(tree)]
    assert all(r["declaration"] == {"ref": "E-901", "sha256": None, "kind": "identity"} and r["purpose"] == "identity"
               for r in recs)
    assert recs[0]["who"]["script"] == "identity/probe.py" and recs[0]["who"]["clean_run"] == RUN
    assert [r["who"]["run_id"] for r in recs] == ["q32-sim@run-1", "q32-sim@run-1", "q32-sim@run-2"]
    assert recs[0]["dates"]["blocks"] == ["choice", "judged"] and recs[0]["dates"]["judged_first"] == "2024-01-02"
    assert [f["path"] for f in recs[0]["what"]["files"]] == [BARS, WALKS]
    assert all(f["in_data_manifest"] for f in recs[0]["what"]["files"])

    # a clean run's marker is a claim, checked as a family read's: the checkout it names, its run id, committed code
    monkeypatch.setenv("S2X_CLEAN_RUN", "another-run")
    with pytest.raises(R.JudgedBlockSealed, match="clean run"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", **ident)
    monkeypatch.setenv("S2X_CLEAN_RUN", RUN)
    monkeypatch.delenv("S2X_RUN_ID")
    with pytest.raises(R.JudgedBlockSealed, match="S2X_RUN_ID"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", **ident)
    monkeypatch.setenv("S2X_RUN_ID", "q32-sim@run-3")
    (tree / "code.py").write_text("x = 2\n", encoding="utf-8")
    with pytest.raises(R.JudgedBlockSealed, match="uncommitted"):
        R.authorise_engine_read("2020-01-02", "2026-07-16", **ident)
    assert len(ledger_lines(tree)) == 3, "a refused read writes nothing"


@pytest.mark.parametrize("tamper", ["not json\n", '{"ledger": 1}\n', "TRUNCATE"])
def test_a_tampered_ledger_refuses_the_next_read(tree, tamper):
    judged(tree)
    p = tree / "results" / "read_ledger.jsonl"
    if tamper == "TRUNCATE":
        p.write_bytes(p.read_bytes()[:-1])                        # the last line lost its newline
    else:
        with p.open("a", encoding="utf-8", newline="\n") as f:
            f.write(tamper)
    before = p.read_bytes()
    with pytest.raises(R.LedgerError):
        judged(tree, purpose="stage_D_scorecard")
    assert p.read_bytes() == before, "nothing appended to a ledger that does not verify"
    with pytest.raises(R.LedgerError):
        R.read_ledger(p)


def test_missing_lines_counts_every_line():
    assert R.missing_lines("a\nb\n", "a\nb\nc\n") == []
    assert R.missing_lines("a\nb\n", "b\nx\na\n") == [], "order is not checked: a merge interleaves branches' lines"
    assert R.missing_lines("a\nb\n", "a\nB\n") == ["b"]
    assert R.missing_lines("a\na\n", "a\n") == ["a"], "a duplicated line removed is a line removed"
    assert R.missing_lines("", "") == []


def test_a_committed_ledger_line_cannot_be_silently_rewritten(tmp_path):
    repo = tmp_path / "h"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "master")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "core.autocrlf", "false")
    led = repo / "results" / "read_ledger.jsonl"
    led.parent.mkdir()

    def commit(text: str, msg: str) -> list[str]:
        led.write_bytes(text.encode("utf-8"))
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", msg)
        return R.ledger_history_problems(repo)

    assert R.ledger_history_problems(repo) == [], "no ledger yet: nothing to protect"
    assert commit('{"n":1}\n{"n":2}\n', "v1") == []
    assert commit('{"n":1}\n{"n":2}\n{"n":3}\n', "v2 append") == []
    assert commit('{"n":1}\n{"n":3}\n{"n":2}\n{"n":4}\n', "v3 as a merge would") == []
    probs = commit('{"n":1}\n{"n":20}\n{"n":3}\n{"n":4}\n', "v4 rewrite")
    assert probs and '{"n":2}' in " ".join(probs), probs
    led.unlink()
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "v5 delete")
    assert len(R.ledger_history_problems(repo)) >= 4, "a deleted ledger loses every committed line"


def test_an_uncommitted_rewrite_is_reported_against_head(tmp_path):
    t = make_tree(tmp_path)
    led = t / "results" / "read_ledger.jsonl"
    led.parent.mkdir()
    led.write_text('{"n":1}\n', encoding="utf-8")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "ledger")
    led.write_text('{"n":9}\n', encoding="utf-8")
    probs = R.ledger_history_problems(t)
    assert probs and "working copy" in probs[0]


def test_this_repositorys_ledger_history_is_append_only():
    assert R.ledger_history_problems(ROOT) == []


# ---------------------------------------------------------------------------------- reads through the vendored engine

PRELUDE = f"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, {str(ROOT)!r})
"""


def child(code: str, cwd: Path, env: dict[str, str]) -> dict:
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    e.update(env)
    r = subprocess.run([sys.executable, "-c", PRELUDE + textwrap.dedent(code)], cwd=cwd, capture_output=True,
                       text=True, timeout=300, env=e)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_reads_through_the_vendored_engine(tmp_path):
    t = make_tree(tmp_path)
    out = child(f"""
        before = list(sys.path)
        import extended.reader as R
        out = {{"path_same": sys.path == before, "engine_imported": "propedge" in sys.modules}}
        R.RUNS_DIR = Path({str(tmp_path / "runs")!r})
        t = Path({str(t)!r})
        led = t / "results" / "read_ledger.jsonl"
        def attempt(key, fn):
            try:
                df = fn()
                out[key] = {{"days": sorted(set(df["day"] if "day" in df else df["date"])) if len(df.columns) > 2
                             else None, "columns": list(df.columns), "rows": len(df)}}
            except Exception as e:
                out[key] = {{"error": type(e).__name__, "msg": str(e)[:300]}}
            out[key]["lines"] = len(led.read_text(encoding="utf-8").splitlines()) if led.exists() else 0
        tag = dict(purpose="stage_C_judgement", declaration={FAMILY!r}, repo=t, what="child read")
        attempt("choice", lambda: R.read_bars("2023-12-28", "2023-12-29", repo=t))
        attempt("untagged", lambda: R.read_bars("2023-12-29", "2024-01-02", repo=t))
        attempt("judged", lambda: R.read_bars("2024-01-02", "2026-07-16", **tag))
        attempt("confirmation", lambda: R.read_bars("2026-07-16", "2026-07-17", **tag))
        attempt("columns", lambda: R.read_bars("2023-12-28", "2023-12-29", columns=["ts", "close"], repo=t))
        attempt("bad_column", lambda: R.read_bars("2023-12-28", "2023-12-29", columns=["nope"], repo=t))
        attempt("walks_choice", lambda: R.read_walks("A3", "walks", "2023-12-28", "2023-12-29", repo=t))
        attempt("walks_untagged", lambda: R.read_walks("A3", "walks", "2024-01-02", "2026-07-16", repo=t))
        attempt("walks_judged", lambda: R.read_walks("A3", "walks", "2024-01-02", "2026-07-16", **tag))
        attempt("walks_confirmation", lambda: R.read_walks("A3", "walks", "2024-01-02", "2026-07-17", **tag))
        attempt("walks_missing", lambda: R.read_walks("A9", "walks", "2023-12-28", "2023-12-29", repo=t))
        es = t / "vendor/stage2/data/bars/ES"
        es.mkdir()
        (es / "bars.parquet").write_bytes((t / {BARS!r}).read_bytes())
        # ES's 2025-07-01 on is Stage 2's ES confirmation window: Stage 2's own guard refuses it, before any line
        attempt("stage2_guard", lambda: R.read_bars("2025-07-01", "2025-07-02", market="ES", **tag))
        attempt("walks_bad_name", lambda: R.read_walks("../A3", "walks", "2023-12-28", "2023-12-29", repo=t))
        print(json.dumps(out))
    """, ROOT, {"S2X_CLEAN_RUN": RUN, "S2X_RUN_ID": "q32-sim@child"})
    assert out["path_same"] and not out["engine_imported"], "importing the reader touches nothing"
    assert out["choice"]["days"] == ["2023-12-28", "2023-12-29"] and out["choice"]["lines"] == 0
    assert out["untagged"]["error"] == "JudgedBlockSealed" and out["untagged"]["lines"] == 0
    assert out["judged"]["days"] == ["2024-01-02", "2026-07-16"] and out["judged"]["lines"] == 1
    assert out["confirmation"]["error"] == "ConfirmationWindowRefused" and out["confirmation"]["lines"] == 1
    assert out["columns"]["columns"] == ["ts", "close"] and out["columns"]["rows"] == 6
    assert out["bad_column"]["error"] == "KeyError"
    assert out["walks_choice"]["days"] == ["2023-12-28", "2023-12-29"]
    assert out["walks_untagged"]["error"] == "JudgedBlockSealed"
    assert out["walks_judged"]["days"] == ["2024-01-02", "2026-07-16"] and out["walks_judged"]["lines"] == 2
    assert out["walks_confirmation"]["error"] == "ConfirmationWindowRefused"
    assert out["walks_missing"]["error"] == "FileNotFoundError" and out["walks_bad_name"]["error"] == "ValueError"
    assert out["stage2_guard"]["error"] == "ConfirmationWindowLeak" and out["stage2_guard"]["lines"] == 2, \
        out["stage2_guard"]
    recs = [json.loads(x) for x in ledger_lines(t)]
    assert len(recs) == 2
    bars, walks = recs
    assert bars["what"]["kind"] == "bars" and walks["what"]["kind"] == "walks"
    assert [f["path"] for f in bars["what"]["files"]][:1] == [BARS]
    assert bars["what"]["files"][0]["sha256"] == file_sha(t / BARS) and bars["what"]["files"][0]["in_data_manifest"]
    assert bars["what"]["columns"] == list(bars_frame().columns)
    assert walks["what"]["files"][0]["path"] == WALKS and walks["what"]["columns"] == list(walks_frame().columns)
    assert bars["who"]["run_id"] == walks["who"]["run_id"] == "q32-sim@child"
    assert bars["who"]["script"] is None, "python -c has no script"
    assert bars["what"]["description"] == "child read"


PROBE = """
import json, sys
from pathlib import Path
sys.path.insert(0, {root!r})
import extended.reader as R
tree = Path(__file__).resolve().parent.parent
R.RUNS_DIR = tree.parent                       # the temporary tree is the simulated clean run's checkout
try:
    df = R.read_bars("2023-12-29", "2026-07-16", purpose="identity", declaration="E-901", repo=tree, what="probe")
    out = {{"days": sorted(set(df["day"]))}}
except Exception as e:
    out = {{"error": type(e).__name__, "msg": str(e)[:300]}}
print(json.dumps(out))
"""


@pytest.mark.parametrize("clean", [False, True])
@pytest.mark.parametrize("where,ok", [("identity", True), ("scripts", False)])
def test_an_identity_script_reads_the_whole_window_ledgered_only_in_a_clean_run(tmp_path, where, ok, clean):
    """An identity script reads the whole window in any tree; its read is ledgered only inside a clean run (E-026),
    where it is one line. Any other script is refused, in a clean run or not, and writes nothing."""
    t = make_tree(tmp_path)
    probe = t / where / "probe.py"
    probe.parent.mkdir(exist_ok=True)
    probe.write_text(PROBE.format(root=str(ROOT)), encoding="utf-8")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "the probe")                    # a clean run's checkout is of a committed tree
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    if clean:
        e.update({"S2X_CLEAN_RUN": RUN, "S2X_RUN_ID": "q48-sim@probe"})
    r = subprocess.run([sys.executable, f"{where}/probe.py"], cwd=t, capture_output=True, text=True, timeout=300,
                       env=e)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    led = t / "results" / "read_ledger.jsonl"
    if ok:
        assert out["days"] == ["2023-12-29", "2024-01-02", "2026-07-16"], out
    else:
        assert out["error"] == "JudgedBlockSealed" and "identity/" in out["msg"], out
    if ok and clean:
        recs = [json.loads(x) for x in ledger_lines(t)]
        assert len(recs) == 1 and recs[0]["purpose"] == "identity" and recs[0]["who"]["script"] == "identity/probe.py"
        assert recs[0]["who"]["clean_run"] == RUN and recs[0]["who"]["run_id"] == "q48-sim@probe"
        assert recs[0]["dates"]["judged_first"] == "2024-01-02" and recs[0]["what"]["kind"] == "bars"
    else:
        assert not led.exists(), "no ledger file outside a clean run, and none for a refused read"


# ------------------------------------------------------------------------------------------------------- one door

READ_CALLS = {"read_parquet", "read_table", "ParquetFile", "ParquetDataset", "read_feather"}
READER_CALLS = {"read_bars", "read_walks", "authorise", "authorise_engine_read"}


def _python_files() -> list[Path]:
    out = [ROOT / "conftest.py"]
    for d in ("extended", "scripts", "identity", "tests"):
        out += sorted((ROOT / d).rglob("*.py"))
    return [p for p in out if p.is_file() and "__pycache__" not in p.parts]


#: E-035 (5): a read may be exempted on its line by `# one-door-exempt: E-nnn -- <the file> <why>`. Q-85 (E-052,
#: E-056): the marker is checked -- the row it names must exist in DECISIONS.md and mention "one-door" or "exempt" and
#: the exempted file's path or basename. The file is the read's own path where the code names it (string parts of the
#: path expression, a name followed through its module's top-level assignments), else the file the marker names; when
#: both are known they must agree. E-056 admits this repository's current exemptions, file by file.
EXEMPT_MARK = re.compile(r"one-door-exempt:\s*(E-\d{3,})")
DATA_FILE = re.compile(r"[A-Za-z0-9_\-]+(?:\.[A-Za-z0-9_\-]+)*\.(?:parquet|feather|arrow|csv|jsonl|json)(?![A-Za-z0-9_])")
#: the keyword a read call may name its file by, when not positionally
PATH_KEYWORDS = ("path", "source", "path_or_paths", "filepath_or_buffer")


def _top_assignments(tree: ast.Module) -> dict[str, ast.expr]:
    out: dict[str, ast.expr] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            out[node.target.id] = node.value
    return out


def _path_parts(expr: ast.AST | None, assigns: dict[str, ast.expr], seen: tuple[str, ...] = ()) -> list[str]:
    """The string parts of a path expression, in order (`ROOT / "a" / "b.parquet"`, `Path("a/b.parquet")`,
    `d.joinpath("b.parquet")`, an f-string's literal parts); a name followed through the module's own top-level
    assignments, any other name contributing nothing."""
    if expr is None:
        return []
    if isinstance(expr, ast.Constant):
        return [expr.value] if isinstance(expr.value, str) else []
    if isinstance(expr, ast.Name):
        if expr.id in assigns and expr.id not in seen:
            return _path_parts(assigns[expr.id], assigns, (*seen, expr.id))
        return []
    if isinstance(expr, ast.BinOp):
        return _path_parts(expr.left, assigns, seen) + _path_parts(expr.right, assigns, seen)
    if isinstance(expr, ast.JoinedStr):
        return [v.value for v in expr.values if isinstance(v, ast.Constant) and isinstance(v.value, str)]
    if isinstance(expr, ast.Call):
        head = _path_parts(expr.func.value, assigns, seen) if isinstance(expr.func, ast.Attribute) else []
        return head + [s for a in expr.args for s in _path_parts(a, assigns, seen)]
    return []


def _read_file(call: ast.Call, assigns: dict[str, ast.expr]) -> str | None:
    """The basename of the data file a read call opens, where the code names it; None when it does not (a parameter)."""
    arg = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg in PATH_KEYWORDS), None)
    path = "/".join(s.strip("/\\") for s in _path_parts(arg, assigns) if s.strip("/\\")).replace("\\", "/")
    base = path.rsplit("/", 1)[-1] if path else ""
    return base if DATA_FILE.fullmatch(base) else None


def _names_file(row: str, base: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_\-]){re.escape(base)}(?![A-Za-z0-9_])", row) is not None


def exemption_problem(line: str, call: ast.Call, assigns: dict[str, ast.expr], decisions: str) -> str | None:
    """Why an exempted read's marker does not hold (None when it does)."""
    m = EXEMPT_MARK.search(line)
    assert m is not None
    row_id = m.group(1)
    row = R.decision_row(decisions, row_id)
    if row is None:
        return f"its marker names {row_id}, which is no row of DECISIONS.md"
    low = row.lower()
    if "one-door" not in low and "exempt" not in low:
        return f"its marker names {row_id}, whose row does not mention a one-door exemption"
    in_code = _read_file(call, assigns)
    named = DATA_FILE.search(line[m.end():])
    in_mark = named.group(0).rsplit("/", 1)[-1] if named else None
    if in_code and in_mark and in_code != in_mark:
        return f"its marker names {in_mark} but the read opens {in_code}"
    base = in_code or in_mark
    if base is None:
        return "the file it reads is not named in the code -- name it in the marker (`one-door-exempt: E-nnn -- <file>`)"
    if not _names_file(row, base):
        return f"its marker names {row_id}, whose row does not name {base}"
    return None


def one_door_problems(rel: str, src: str, decisions: str) -> list[str]:
    """Every way a module of this repository reads Stage 2's bars or walks other than through the reader."""
    bad = []
    lines = src.splitlines()
    tree = ast.parse(src, filename=rel)
    assigns = _top_assignments(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("propedge.data"):
            names = {a.name for a in node.names}
            if node.module.startswith("propedge.data.bars") or "bars" in names:
                bad.append(f"{rel}:{node.lineno} imports Stage 2's bar reader")
        elif isinstance(node, ast.Import):
            bad += [f"{rel}:{node.lineno} imports {a.name}" for a in node.names
                    if a.name.startswith("propedge.data.bars")]
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
            line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            if name in READ_CALLS:
                if not EXEMPT_MARK.search(line):
                    bad.append(f"{rel}:{node.lineno} calls {name}")
                else:
                    why = exemption_problem(line, node, assigns, decisions)
                    if why:
                        bad.append(f"{rel}:{node.lineno} calls {name} exempted, but {why}")
            if name in READER_CALLS and not rel.startswith("tests/") and \
                    any(k.arg == "repo" for k in node.keywords):
                bad.append(f"{rel}:{node.lineno} points the reader at another tree (repo=)")
    return bad


def test_this_repositorys_code_reads_bars_and_walks_only_through_the_reader():
    """A deterrent in test form (the audit's H-2): no module here imports Stage 2's bar reader or reads a parquet file
    except `extended/reader.py`, unless the read is exempted on its line by a row that admits it (E-035 (5); checked,
    Q-85); outside the tests, nothing points the reader at another tree (`repo=`). Stage 2's engine reading inside a
    vendored call is not seen here -- such a runner records its read with `extended.reader.authorise_engine_read`
    first."""
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    bad = []
    for p in _python_files():
        rel = p.relative_to(ROOT).as_posix()
        if rel == "extended/reader.py":
            continue
        bad += one_door_problems(rel, p.read_text(encoding="utf-8"), decisions)
    assert not bad, "read Stage 2's bars and walks through extended.reader: " + "; ".join(bad)


ONE_DOOR_LOG = ("| id | date | decision | basis |\n|---|---|---|---|\n"
                "| E-801 | 2026-11-16 | **A row about something else** -- `cal.parquet` named, nothing admitted | t |\n"
                "| E-802 | 2026-11-16 | **Exempted from the one door:** `results/x/pairs.parquet`, a derived file | t |\n"
                "| E-803 | 2026-11-16 | **one-door-exempt:** A1's `vendor/stage2/data/atlas/A1/days.parquet` | t |\n"
                "| E-804 | 2026-11-16 | **A one-door exemption** for nothing named | t |\n")


def _scan(body: str, decisions: str = ONE_DOOR_LOG) -> list[str]:
    return one_door_problems("scripts/probe.py", textwrap.dedent(body), decisions)


@pytest.mark.parametrize("body,why", [
    ('import pandas as pd\nd = pd.read_parquet("cal.parquet")\n', "calls read_parquet"),
    ('import pandas as pd\nd = pd.read_parquet("x.parquet")  # one-door-exempt: E-899 -- x.parquet\n', "no row"),
    ('import pandas as pd\nd = pd.read_parquet("cal.parquet")  # one-door-exempt: E-801 -- cal.parquet\n',
     "does not mention a one-door exemption"),
    ('import pandas as pd\nd = pd.read_parquet("days.parquet")  # one-door-exempt: E-802 -- days\n', "does not name days.parquet"),
    ('import pandas as pd\nd = pd.read_parquet(VENDOR / "atlas" / "A1" / "events.parquet")  # one-door-exempt: E-803\n',
     "does not name events.parquet"),
    ('import pandas as pd\ndef f(p):\n    return pd.read_parquet(p)  # one-door-exempt: E-802 -- a derived file\n',
     "not named in the code"),
    ('import pandas as pd\ndef f(p):\n    return pd.read_parquet(p)  # one-door-exempt: E-804 -- p16.parquet\n',
     "does not name p16.parquet"),
    ('import pandas as pd\nF = ROOT / "data" / "days.parquet"\nd = pd.read_parquet(F)  # one-door-exempt: E-802 -- pairs.parquet\n',
     "names pairs.parquet but the read opens days.parquet"),
    ('import pyarrow.parquet as pq\nt = pq.read_table(source="vendor/stage2/data/bars/NQ/bars.parquet")  # one-door-exempt: E-803\n',
     "does not name bars.parquet"),
], ids=["unmarked", "no-row", "row-not-an-exemption", "row-names-another-file", "path-in-code-not-in-row",
        "parameter-unnamed", "parameter-named-not-in-row", "marker-disagrees-with-code", "keyword-path"])
def test_an_exemption_marker_whose_row_does_not_admit_the_read_is_refused(body, why):
    bad = _scan(body)
    assert len(bad) == 1 and why in bad[0], bad


@pytest.mark.parametrize("body", [
    # the row names the basename; the path is in the code (a module constant followed), the marker silent on it
    'import pandas as pd\nDAYS = ROOT / "vendor" / "stage2" / "data" / "atlas" / "A1" / "days.parquet"\n'
    'd = pd.read_parquet(DAYS)  # one-door-exempt: E-803 -- A1 days: dates and day kinds only\n',
    # an unresolved head, the rest literal
    'import pandas as pd\nd = pd.read_parquet(V / "data" / "atlas" / "A1" / "days.parquet",  # one-door-exempt: E-803\n'
    '                    columns=["date"])\n',
    # a parameter: the marker names the file, the row (which says "exempted") names it with its path
    'import pandas as pd\ndef f(p):\n    return pd.read_parquet(p)  # one-door-exempt: E-802 -- pairs.parquet, derived\n',
    'import pandas as pd\nd = pd.read_parquet(path=f"{OUT}/pairs.parquet")  # one-door-exempt: E-802 -- pairs.parquet\n',
], ids=["module-constant", "unresolved-head", "parameter-named-in-marker", "keyword-fstring"])
def test_an_exemption_marker_whose_row_admits_the_read_holds(body):
    assert _scan(body) == []
