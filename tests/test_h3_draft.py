"""Wave 3.2: H3's draft declaration (`prereg/DRAFT_H3_three_way.md`), checked on its own text, on the design note and
on the build (no engine, no bar, no result file; fast).

- **the form** -- `prereg/TEMPLATE_family.md`'s sections 0 to 19 and two appendices, in order; read as LF text;
- **N-1's admission paragraph, copied** -- every line of the note's block between its markers is in the draft's block
  in order, but the one line M-2 replaces; every other line of the draft's block is an insertion marked with its minor;
- **E-213's five minors carried** -- each source-(i) bound written as a clip (M-1); a refused held-out run fails its
  finalist and is never re-run with new bounds (M-1); a censored session count's range [0, W + 1] (M-2); a dimension
  with neither bound nor clip excluded from (a) (M-3); the stop exit's own cost in the race (M-4); and Appendix B maps
  each to where it is carried;
- **the rulings the note settles** -- no t decides; overlap refused; the smaller-J rule in H3-D only; H_g = 504; O-5's
  and O-6's forms; vacuity at one half; no held-out read (its judged-block line names none); H3 takes no k;
- **the seed table** -- the note's ten seeds once each, each with the note's role and status, equal to the build's seed
  module role for role; no other eight-digit 2026 token in the text;
- **the run plan is the script's** -- Appendix A's fenced block equals `docs/plans/scripts/three_way/h3_plan.py`'s
  output line for line, and every part's seed roles are the seed module's;
- **corrective cycle 1** -- the second text carries the lead's rulings (the race fractional, R-10's residual race, the
  key guard's sample, O-5 as E-230 ruled, the gate at 25 % denial, the missed-signal arm, the declared smaller-J
  inputs); Appendix C equals `h3a_inputs.py`'s output (every H3-A input fixed in the text, B-3); Appendix D answers
  every finding of the red team's read (B-1 to B-3, m-1 to m-17, n-1 to n-5) once each.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from extended import three_way_seeds as S

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "prereg" / "DRAFT_H3_three_way.md"
NOTE = ROOT / "docs" / "plans" / "THREE_WAY_TEST_design.md"
PLAN = ROOT / "docs" / "plans" / "scripts" / "three_way" / "h3_plan.py"
NOTE_MARKS = ("<!-- 2.2a-admission: begin -->", "<!-- 2.2a-admission: end -->")
DRAFT_MARKS = ("<!-- h3-admission: begin -->", "<!-- h3-admission: end -->")
PLAN_MARKS = ("<!-- h3_plan: begin -->", "<!-- h3_plan: end -->")
H3A = ROOT / "docs" / "plans" / "scripts" / "three_way" / "h3a_inputs.py"
H3A_MARKS = ("<!-- h3a_inputs: begin -->", "<!-- h3a_inputs: end -->")
REVIEW_FINDINGS = (("B-1", "B-2", "B-3") + tuple(f"m-{i}" for i in range(1, 18)) + tuple(f"n-{i}" for i in range(1, 6)))


def _lf(p: Path) -> str:
    return p.read_bytes().decode("utf-8").replace("\r\n", "\n")


@pytest.fixture(scope="module")
def text() -> str:
    return _lf(DRAFT)


def _between(t: str, marks: tuple[str, str]) -> str:
    i, j = t.index(marks[0]), t.index(marks[1])
    return t[i + len(marks[0]):j]


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def test_the_form(text: str) -> None:
    assert text.startswith("# H3: ") and "**Status: a draft" in text
    heads = [f"\n## {n}. " for n in range(20)] + [f"\n## Appendix {a}. " for a in "ABCD"]
    pos = [text.find(h) for h in heads]
    assert all(p >= 0 for p in pos), [h for h, p in zip(heads, pos) if p < 0]
    assert pos == sorted(pos)


def test_the_admission_paragraph_is_the_notes_with_the_minors(text: str) -> None:
    mine = _between(text, DRAFT_MARKS).strip("\n").split("\n")
    theirs = _between(_lf(NOTE), NOTE_MARKS).strip("\n").split("\n")
    replaced = {"     [0, h_d]; a dollar amount within the limits that the firm's verified rules and the design's declared purchase cap"}
    it = iter(mine)
    extra = []
    for line in theirs:
        if line in replaced:
            continue
        for m in it:
            if m == line:
                break
            extra.append(m)
        else:
            pytest.fail(f"the note's line is missing from the draft's copy: {line!r}")
    extra += list(it)
    # every line the draft adds is part of a marked insertion (or the blank before one)
    blocks = "\n".join(extra)
    assert set(re.findall(r"\[(M-\d)\]", blocks)) == {"M-1", "M-2", "M-3"}, blocks
    for chunk in re.split(r"\n\s*\n", blocks.strip()):
        assert re.search(r"\[M-\d\]", chunk), f"an unmarked change to the copied paragraph: {chunk!r}"


def test_the_five_minors_are_carried(text: str) -> None:
    flat = _flat(_between(text, DRAFT_MARKS))
    assert "A bound from source (i) is also written into the dimension's definition as a clip" in flat
    assert "never re-run with new bounds" in flat and "ends the held-out test for that finalist as a failure" in flat
    assert "a count of sessions in [0, W + 1]" in flat and "[0, h_d]" not in flat
    assert "neither an arithmetic bound nor a pinned clip" in flat
    whole = _flat(text)
    assert "the stop exit's own cost in the race" in whole and "L = min(l, c - x_stop)" in whole
    appb = _flat(text[text.index("## Appendix B."):])
    for m in ("M-1", "M-2", "M-3", "M-4"):
        assert f"| {m}:" in appb


def test_the_notes_rulings(text: str) -> None:
    flat = _flat(text)
    for phrase in ("No t decides, in any branch.", "overlap is refused", "applied in H3-D only",
                   "504 sessions", "over coin seeds only", "**the point estimate governs**",
                   "a stated size of one half or more is labelled vacuous", "takes **no k**",
                   "**Judged-block reads:** none.", "seeded apart", "the antithetic twin reads 1 - u exactly"):
        assert phrase in flat, phrase
    assert re.search(r"^- \*\*Judged-block reads:\*\* none\.$", text, re.MULTILINE)


def test_the_seed_table(text: str) -> None:
    table = text[text.index("\n## 15. "):text.index("\n## 16. ")]
    note = _lf(NOTE)
    for role, seed in S.ROLES.items():
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \| ([^|]+) \|$", table, re.MULTILINE)
        assert len(rows) == 1, (role, seed)
        assert rows[0][1].strip() == S.STATUS[role], (role, rows[0])
        assert f"| {seed} | {rows[0][0]} | {rows[0][1]} |" in note          # the note's own row, verbatim
    tokens = {int(t) for t in re.findall(r"\b2026\d{4}\b", text)}
    assert tokens == set(S.BLOCK), sorted(tokens ^ set(S.BLOCK))


def test_the_run_plan_is_the_scripts(text: str) -> None:
    spec = importlib.util.spec_from_file_location("h3_plan_for_test", PLAN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    block = _between(text, PLAN_MARKS).strip()
    assert block.startswith("```text\n") and block.endswith("\n```")
    assert block[len("```text\n"):-len("\n```")] == mod.report()
    for roles in mod.ROLES.values():
        for r in roles:
            assert r in S.ROLES or r == "the search declaration's own", r
    assert {mod.base(name) for name, *_ in mod.rows()} == set(mod.ROLES) == set(mod.READS)
    assert "c_max=" in block and "crashed sub-part is re-run whole" in block


def test_corrective_cycle_1s_rulings(text: str) -> None:
    flat = _flat(text)
    for phrase in ("second text (corrective cycle 1)", "fractional, never rounded",
                   "a driftless two-point race between the barrier and the lattice point one step up",
                   "N-2 checked on every key at construction", "n^2 / 2^129", "first 64 seed indices",
                   "within 1.25 GB a worker", "the one-sided check (B-10's form", "never a second margin",
                   "25 % (`three_way_stats.GATE_DENIAL`", "10 % of signals missed", "SMALLER_J_GRID",
                   "z_pi sigma_M / sqrt(J)", "unless the joint held-out test's declaration is named",
                   "trigger-level", "re-declaring R-10's sampling"):
        assert phrase in flat, phrase
    assert "(c_L + z_pi)" not in flat and "whole ticks (`three_way_redraw.LATTICE` = 1)" not in flat


def test_appendix_c_is_the_declared_inputs(text: str) -> None:
    spec = importlib.util.spec_from_file_location("h3a_inputs_for_test", H3A)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    block = _between(text, H3A_MARKS).strip()
    assert block.startswith("```text\n") and block.endswith("\n```")
    assert block[len("```text\n"):-len("\n```")] == mod.report()
    from extended import three_way_h3a as H

    names = [n for n, _ in H.declared()]
    for need in ("TOY_RULES", "S1_PARAMS", "A1_DESIGN", "BASELINES", "BUDGET", "J_PRIME", "TOY_COMPOSITE", "A2_PAIR",
                 "A3_PAIR", "SHORTCUT_HISTORIES", "P2_LEVERS", "P3_EPS", "P4_A", "SIZE_GRID", "CENTRING_Z"):
        assert need in names, need


def test_appendix_d_answers_every_finding(text: str) -> None:
    appd = text[text.index("## Appendix D."):]
    for f in REVIEW_FINDINGS:
        assert len(re.findall(rf"^\| {re.escape(f)} \|", appd, re.MULTILINE)) == 1, f
