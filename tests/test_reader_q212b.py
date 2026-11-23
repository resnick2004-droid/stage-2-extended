"""Q-212's second round (the lead's rulings on the red team's `READER_Q212_TEMPLATE_2026-11-22`), the parts outside
the go token's own tests (`tests/test_reader_go.py`, `tests/go_cases.py`): synthetic logs and Q-158's synthetic git
tree only (`tests/test_reader_q194d.py`'s `declared`; F-98 of `tests/heldout_verdict_rows.py`); nothing real is read
but this repository's own `config/rules_extended.yaml` and vendored `rules.yaml` (F4's record).

* **F5, the log's lines:** `_split` breaks on `\\n` only (one trailing `\\r` dropped); each of U+2028, U+2029, U+0085,
  form feed, vertical tab and FS/GS/RS in the log is a problem of the row it sits in (or the nearest row above),
  cleared by a void of that row; a token after one is no row;
* **n1, the confirmation window:** the first NQ or MNQ `heldout-window` row reaching 2026-07-17 governs; every later
  one, of either market, is a problem (voidable) and is read by no window rule (`heldout_window`, `heldout_windows`);
  rows of other markets, and windows ending before 2026-07-17, are untouched;
* **F8, the verdict's order:** `_verdict_commits` refuses a shallow repository (None), ignores replace refs, reads a
  `binary` or textconv'd DECISIONS.md as text, keys on the verdict token (an edit of its tail is the same row);
* **F4's record:** `firm_plans` is the record's plans for each firm, read from the two files.
"""
from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import pytest
import yaml

from extended import reader as R
import heldout_verdict_rows as VR
import test_reader_q194d as D
from test_reader_heldout import tree  # noqa: F401 -- the fixture
from test_reader_q194d import declared  # noqa: F401 -- the fixture

ROOT = Path(__file__).resolve().parent.parent
DAY = "2026-11-22"


def g(t: Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=t, capture_output=True, text=True, check=True).stdout.strip()


def row(n: int, text: str = "a row") -> str:
    return f"| E-{n} | {DAY} | {text} | x |"


def void(n: int, target: str) -> str:
    return row(n, f"heldout-void: {target} -- a correction")


def window(n: int, market: str, start: str, end: str) -> str:
    return row(n, f"heldout-window: {market} {start} to {end} -- the data bought")


# ----------------------------------------------------------------------------------------------- F5: the lines


def test_f5_the_log_splits_on_newlines_only():
    assert R._split("a\r\nb\nc d\x0ce\n") == ["a", "b", "c d\x0ce"]       # str.splitlines gives five
    assert R._split("") == [] and R._split("x") == ["x"] and R._split("x\n\n") == ["x", ""]
    assert R._split("a\r\r\nb") == ["a\r", "b"], "one trailing carriage return only"


@pytest.mark.parametrize("ch", [" ", " ", "\x85", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e"])
def test_f5_a_hidden_break_is_a_problem_until_its_row_is_voided(ch):
    log = "\n".join([row(900), row(901, "prose" + ch + window(902, "NQ", "2026-07-17", "2027-07-16"))])
    probs = R.heldout_token_problems(log)
    assert len(probs) == 1 and probs[0].startswith("E-901"), probs
    assert R.heldout_tokens(log, "window") == [], "a token after a hidden break is no row"
    assert R.heldout_token_problems(log + "\n" + void(903, "E-901")) == []
    assert R.heldout_token_problems(log + "\n" + void(903, "E-900")), "a void of another row clears nothing"
    above = "\n".join([row(900), "prose" + ch + "more"])
    assert R.heldout_token_problems(above)[0].startswith("E-900"), "outside a row: the nearest row above"
    assert R.heldout_token_problems(above + "\n" + void(903, "E-900")) == []


def test_f5_a_judged_read_waits_on_a_hidden_break(tree):
    p = tree / "DECISIONS.md"
    p.write_bytes(p.read_bytes() + (row(990, "prose more") + "\n").encode("utf-8"))
    with pytest.raises(R.JudgedBlockSealed, match="E-990"):
        R.authorise("2024-01-02", "2024-03-29", purpose="identity", declaration="E-001", repo=tree, what="f5")


# ------------------------------------------------------------------------------------ n1: the confirmation window


def test_n1_the_first_confirmation_window_row_governs():
    first = window(950, "NQ", "2026-07-17", "2027-07-16")
    later = [window(951, "NQ", "2026-07-17", "2027-12-31"), window(952, "MNQ", "2026-07-17", "2027-07-16"),
             window(953, "NQ", "2026-01-02", "2026-08-01")]
    log = "\n".join([first, *later])
    probs = R.heldout_token_problems(log)
    assert [p.split(" ")[0] for p in probs] == ["E-951", "E-952", "E-953"], probs
    assert [t.row for t in R._window_rows(log)] == ["E-950"]
    d = date(2027, 6, 1)
    assert R.heldout_window(log, "NQ", d, d)[0] == "E-950"
    assert R.heldout_window(log, "NQ", date(2027, 9, 1), date(2027, 9, 1))[0] == R.BASE_WINDOW_ROW, \
        "the later row's longer window is read by no rule"
    assert R.heldout_window(log, "MNQ", d, d)[0] == R.BASE_WINDOW_ROW
    assert [w for w, _ in R.heldout_windows(log, "NQ", date(2026, 7, 20), date(2026, 7, 20))] == ["E-950"]
    voided = log + "\n" + "\n".join(void(960 + i, r) for i, r in enumerate(("E-951", "E-952", "E-953")))
    assert R.heldout_token_problems(voided) == [] and [t.row for t in R._window_rows(voided)] == ["E-950"], \
        "a void clears the problem; the later row still governs nothing"


def test_n1_mnq_first_binds_nq_and_other_markets_are_untouched():
    log = "\n".join([window(950, "MNQ", "2026-07-17", "2027-07-16"), window(951, "NQ", "2026-07-17", "2027-07-16"),
                     window(952, "ES", "2026-07-17", "2027-07-16"), window(953, "ES", "2026-07-17", "2027-12-31"),
                     window(954, "NQ", "2025-01-02", "2026-07-16")])
    assert [p.split(" ")[0] for p in R.heldout_token_problems(log)] == ["E-951"]
    assert [t.row for t in R._window_rows(log)] == ["E-950", "E-952", "E-953", "E-954"]


# ------------------------------------------------------------------------------------------ F8: the verdict's order


def verdict_tree(declared) -> str:
    VR.declare(declared)
    return VR.commit_verdict(declared, VR.VERDICT_ROW)


def test_f8_a_shallow_repository_proves_no_order(declared, tmp_path):
    v = verdict_tree(declared)
    assert R._verdict_commits(declared, VR.VERDICT_ROW) == [v]
    clone = tmp_path / "shallow"
    g(tmp_path, "clone", "-q", "--depth", "1", declared.resolve().as_uri(), str(clone))
    assert g(clone, "rev-parse", "--is-shallow-repository") == "true"
    assert R._verdict_commits(clone, VR.VERDICT_ROW) is None
    assert R._verdict_commit(clone, VR.VERDICT_ROW) is None


def test_f8_replace_refs_are_ignored(declared):
    v = verdict_tree(declared)
    g(declared, "commit", "-q", "--allow-empty", "-m", "later")
    fake = g(declared, "commit-tree", f"{v}^{{tree}}", "-p", f"{v}^", "-m", "a replacement")   # same tree, no change
    blank = g(declared, "commit-tree", f"{v}^^{{tree}}", "-m", "a parentless stand-in")           # an older tree
    g(declared, "replace", v, blank)
    assert R._verdict_commits(declared, VR.VERDICT_ROW) == [v], "the objects themselves, not the replacement"
    g(declared, "replace", "-d", v)
    g(declared, "replace", f"{v}^", fake)
    assert R._verdict_commits(declared, VR.VERDICT_ROW) == [v]


@pytest.mark.parametrize("attrs,config", [
    ("DECISIONS.md binary\n", ()),
    ("DECISIONS.md -diff\n", ()),
    ("DECISIONS.md diff=hide\n", ("diff.hide.textconv", "sed -e s/heldout-verdict/hidden/")),
])
def test_f8_the_log_is_read_as_text_without_textconv(declared, attrs, config):
    (declared / ".gitattributes").write_text(attrs, encoding="utf-8")
    g(declared, "add", ".gitattributes")
    g(declared, "commit", "-q", "-m", "attributes")
    if config:
        g(declared, "config", *config)
    v = verdict_tree(declared)
    assert R._verdict_commits(declared, VR.VERDICT_ROW) == [v]


def test_f8_the_token_not_the_bytes(declared):
    v = verdict_tree(declared)
    edited = VR.VERDICT_ROW.replace("the joint held-out test's verdict", "the verdict, its text corrected")
    p = declared / "DECISIONS.md"
    p.write_bytes(p.read_bytes().replace(VR.VERDICT_ROW.encode("utf-8"), edited.encode("utf-8")))
    g(declared, "commit", "-q", "-am", "the verdict's text edited in place")
    w = D.head(declared)
    assert R._verdict_commits(declared, edited) == R._verdict_commits(declared, VR.VERDICT_ROW) == [v, w], \
        "the edit in place adds the same token again (held by its commit): a hit by the key, either text"
    assert R._commit_holds_line(declared, v, edited) and R._commit_holds_line(declared, w, VR.VERDICT_ROW)
    other = VR.verdict_row(row=983)
    assert R._commit_holds_line(declared, w, other) is False and R._verdict_commits(declared, other) == []


# ---------------------------------------------------------------------------------------------- F4: the record


def record_plans(root: Path) -> dict[str, set[str]]:
    ext = yaml.safe_load((root / "config" / "rules_extended.yaml").read_text(encoding="utf-8"))["rules"]
    out = {"Topstep": set(), "MFFU": set(), "Lucid": set()}
    names = {"topstep": "Topstep", "mffu": "MFFU", "lucid": "Lucid"}
    for r in ext:
        if r.get("firm") in names and len(str(r["key"]).split(".")) == 3:
            out[names[r["firm"]]].add(str(r["key"]).split(".")[1])
    keys = yaml.safe_load((root / "vendor" / "stage2" / "config" / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    out["Topstep"] |= {"combine50k"} | {"combine" + s for s in ("100k", "150k")
                                        if any(k.startswith("combine_") and k.endswith("_" + s) for k in keys)}
    return out


def test_f4_the_plans_are_the_records():
    plans = R.firm_plans()
    assert {f: set(v) for f, v in plans.items()} == record_plans(ROOT)
    assert {"combine50k", "006_50k_static"} <= plans["Topstep"] and "rapid50k" in plans["MFFU"]
    assert "flex50k" in plans["Lucid"] and not plans["Lucid"] & plans["MFFU"]


def test_f4_a_record_without_a_firm_gives_no_plan(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "rules_extended.yaml").write_text(
        "rules:\n  - {firm: mffu, key: mffu.rapid50k.daily_loss}\n  - {firm: other, key: other.x50k.y}\n",
        encoding="utf-8")
    assert R.firm_plans(tmp_path) == {"Topstep": frozenset(), "MFFU": frozenset({"rapid50k"}), "Lucid": frozenset()}


def test_f8_the_root_commits_patch_is_read(tmp_path):
    """`--root`: a verdict row added by the first commit is a hit, also where `log.showRoot` is off."""
    t = tmp_path / "t"
    t.mkdir()
    for a in (("init", "-q", "-b", "master"), ("config", "user.email", "t@example.invalid"), ("config", "user.name", "t"),
              ("config", "core.autocrlf", "false"), ("config", "log.showRoot", "false")):
        g(t, *a)
    (t / "DECISIONS.md").write_bytes((VR.VERDICT_ROW + "\n").encode("utf-8"))
    g(t, "add", "DECISIONS.md")
    g(t, "commit", "-q", "-m", "the first commit")
    assert R._verdict_commits(t, VR.VERDICT_ROW) == [g(t, "rev-parse", "HEAD")]


# --- c2 regression tests (READER_Q212_TEMPLATE_c2) ---


def test_c2_f2_mistaken_membership_row_never_hijacks_or_locks_out(tmp_path):
    import go_cases as G

    prereg = tmp_path / "prereg"
    prereg.mkdir()
    for name, body in G.FILES.items():
        (prereg / name).write_text(body, encoding="utf-8")
    g14 = G.go("E-904", "F-14", G.B, "2026-12-05")
    m_wrong = G.member("E-905", "F-14", G.B, "E-904")
    # 1. Unvoided wrong membership row -> problem + GoRefused (not E-904)
    log1 = "\n".join([G.P13, G.G13, G.P14, g14, m_wrong])
    assert R.go_problems(log1, prereg)
    with pytest.raises(R.GoRefused):
        R.membership_event(log1, prereg)
    # 2. Voided wrong membership row -> clean, returns E-902 (never E-904)
    log2 = log1 + "\n" + G.void("E-906", "E-905")
    assert R.go_problems(log2, prereg) == []
    assert R.membership_event(log2, prereg) == G.G13
    # 3. Replacement valid membership row succeeds
    log3 = log2 + "\n" + G.member("E-907", "F-13", G.A, "E-902")
    assert R.go_problems(log3, prereg) == []
    assert R.membership_event(log3, prereg) == G.G13
    # 4. Impossible-date go row cannot be frozen
    bad_date = G.go("E-901", "F-13", G.A, "2026-13-45")
    log4 = "\n".join([bad_date, G.void("E-902", "E-901"), G.P13, G.go("E-903", "F-13", G.A),
                       G.member("E-904", "F-13", G.A, "E-901"), G.void("E-905", "E-904")])
    assert R.go_problems(log4, prereg) == []
    assert R.membership_event(log4, prereg) == G.go("E-903", "F-13", G.A)
    # 5. Valid freeze + unclosed fence refuses instead of swallowing
    log5 = "\n".join([G.P13, G.G13, G.member("E-903", "F-13", G.A, "E-902"), "```"])
    with pytest.raises(R.GoRefused):
        R.membership_event(log5, prereg)
    # 6. Withdrawn after frozen event refused even when prereg drift empties tokens
    (prereg / "F-13_dup.md").write_text(G.F13, encoding="utf-8")
    log6 = "\n".join([G.P13, G.G13, G.member("E-903", "F-13", G.A, "E-902"),
                       G.P14, G.closed("E-905", "F-14", G.B, cause="withdrawn")])
    probs6 = R.go_problems(log6, prereg)
    assert any("withdrawn" in p for p in probs6), probs6


def test_c2_f6_verdict_commits_survives_literal_nul(declared):
    t = declared
    p = t / "DECISIONS.md"
    # Literal NUL in an earlier historical row does not break _verdict_commits
    p.write_bytes(p.read_bytes() + b"| E-950 | 2026-11-22 | a note with\x00nul | b |\n")
    g(t, "add", "DECISIONS.md")
    g(t, "commit", "-q", "-m", "historical nul")
    v1 = VR.VERDICT_ROW
    p.write_bytes(p.read_bytes() + (v1 + "\n").encode("utf-8"))
    g(t, "add", "DECISIONS.md")
    g(t, "commit", "-q", "-m", "v1")
    c1 = g(t, "rev-parse", "HEAD")
    hits = R._verdict_commits(t, v1)
    assert hits == [c1], hits


def test_c2_f7_go_row_present_ignores_replace_refs_and_dirty_decisions(tmp_path, monkeypatch):
    import go_cases as G
    import test_reader_go as TRG

    t, runner = TRG.runner_tree(tmp_path)
    monkeypatch.setattr(R, "ROOT", t.resolve())
    decl = t / "prereg" / "F-13_x.md"
    log = TRG.with_log(t, [G.P13, G.go("E-902", "F-13", G.A, run=runner)])
    assert R.go_row_present(decl)
    # Dirty working-tree DECISIONS.md fails even with log_text=None
    (t / "DECISIONS.md").write_text(log + G.fin("E-904", "F-13", G.A) + "\n", encoding="utf-8")
    assert not R.go_row_present(decl)
    TRG.git(t, "checkout", "--", "DECISIONS.md")
    assert R.go_row_present(decl)
    # git replace hiding a modified deciding file at runner fails
    (t / "scripts" / "survey.py").write_text("# tampered\n", encoding="utf-8")
    TRG.git(t, "add", "scripts/survey.py")
    TRG.git(t, "commit", "-q", "-m", "tamper")
    tampered = TRG.git(t, "rev-parse", "HEAD")
    assert not R.go_row_present(decl)
    TRG.git(t, "replace", runner, tampered)
    assert not R.go_row_present(decl), "git replace must not spoof runner blob"


def test_c2_f9_superseded_purpose_rejects_non_prereg_file():
    with pytest.raises(R.SupersededRefused):
        R.authorise("2020-01-02", "2023-12-29", purpose="firm_scorecard", declaration="CHARTER.md",
                    repo=ROOT, what="c2-f9")


def test_c2_f10_bare_midline_cr_is_flagged():
    log = "\n".join([row(900), row(901, "prose\rmore")])
    probs = R.heldout_token_problems(log)
    assert len(probs) == 1 and "U+000D" in probs[0] and probs[0].startswith("E-901"), probs
    assert R.heldout_token_problems(log + "\n" + void(902, "E-901")) == []
