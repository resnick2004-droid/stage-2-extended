"""Wave 3.2: H3's declaration (`prereg/H3_three_way.md`: H3-0 and H3-A; H3-D in its own later text), checked on its
own text, on the design note and on the build (no engine, no bar, no result file; fast; the file keeps its name).

- **the form** -- `prereg/TEMPLATE_family.md`'s sections 0 to 19 and the appendices, in order; read as LF text; in
  pin-time form (no draft status; H3-D declared later in its own text; the gatekeeper's item 1);
- **the design note's version** -- the LF sha256 the text names is the note's (the gatekeeper's item 7);
- **the build commit** -- the commit the text names is an ancestor of this tree, and every build file it lists exists
  there (the gatekeeper's pin condition);
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

import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

from extended import three_way_seeds as S

ROOT = Path(__file__).resolve().parent.parent
DECL = ROOT / "prereg" / "H3_three_way.md"
NOTE = ROOT / "docs" / "plans" / "THREE_WAY_TEST_design.md"
PLAN = ROOT / "docs" / "plans" / "scripts" / "three_way" / "h3_plan.py"
NOTE_MARKS = ("<!-- 2.2a-admission: begin -->", "<!-- 2.2a-admission: end -->")
DRAFT_MARKS = ("<!-- h3-admission: begin -->", "<!-- h3-admission: end -->")
PLAN_MARKS = ("<!-- h3_plan: begin -->", "<!-- h3_plan: end -->")
H3A = ROOT / "docs" / "plans" / "scripts" / "three_way" / "h3a_inputs.py"
H3A_MARKS = ("<!-- h3a_inputs: begin -->", "<!-- h3a_inputs: end -->")
REVIEW_FINDINGS = (("B-1", "B-2", "B-3") + tuple(f"m-{i}" for i in range(1, 18)) + tuple(f"n-{i}" for i in range(1, 6))
                   + ("RB-1", "rm-1", "rm-2", "rn-1", "rn-2", "TB-2", "Tm-1", "Tm-2")
                   + tuple(f"v3 m-{i}" for i in range(1, 6)) + tuple(f"v3 n-{i}" for i in range(1, 5)) + ("s-c",)
                   + tuple(f"sc MINOR-{i}" for i in range(1, 4)) + tuple(f"sc NOTE-{i}" for i in range(1, 5))
                   + tuple(f"gk {i}" for i in range(1, 8)) + ("gk pins",))
#: the one seed row the text corrects against the note's (the gatekeeper's item 5: A3's histories are its history null's role's)
ROW_CORRECTED = {
    S.H3A_HISTORIES: (f"| {S.H3A_HISTORIES} | H3-A: the S1 histories of A1 to A4 (the generator's draws; P4's regime "
                      "signs) | design check |",
                      f"| {S.H3A_HISTORIES} | H3-A: the S1 histories of A1, A2 and A4 (the generator's draws; P4's "
                      "regime signs), and H3-A's smaller-J report's one key (section 7); A3's histories are drawn from "
                      f"{S.H3A3_HISTORY_NULL} | design check |"),
}
#: the build files the head's table lists (`extended/`)
BUILD_FILES = ("three_way_keys.py", "three_way_fastkeys.py", "three_way_seeds.py", "three_way_redraw.py",
               "three_way_journey.py", "three_way_runner.py", "three_way_s1.py", "three_way_stats.py", "three_way_h3a.py")


def _lf(p: Path) -> str:
    return p.read_bytes().decode("utf-8").replace("\r\n", "\n")


@pytest.fixture(scope="module")
def text() -> str:
    return _lf(DECL)


def _between(t: str, marks: tuple[str, str]) -> str:
    i, j = t.index(marks[0]), t.index(marks[1])
    return t[i + len(marks[0]):j]


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def test_the_form(text: str) -> None:
    """Pin-time form (the gatekeeper's item 1): no draft status, no future-tense pinning, H3-D declared later in its
    own text, section 18's R-10 bullet closed on template v3."""
    flat = _flat(text)
    assert text.startswith("# H3: the three-way test's probe and design checks (H3-0, H3-A), declared\n")
    assert "a draft" not in flat.lower() and "**Status:" not in text and "DRAFT_" not in text
    assert "It is pinned (by the sha256" not in flat and "only after the red team's read" not in flat
    assert "Open before H3-0" not in flat and "or this text's section 7 rows for R-10 kept" not in flat
    assert "**H3-D, the deciding calibration, is not declared here: it is declared in its own later text under its own decision row**" in flat
    sec18 = _flat(text[text.index("\n## 18. "):text.index("\n## 19. ")])
    assert "**R-10's rows (section 7) are governed by template v3's section 7 as pinned**" in sec18
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
        mine = f"| {seed} | {rows[0][0]} | {rows[0][1]} |"
        if seed in ROW_CORRECTED:                                         # the one row corrected, against the note's
            theirs, want = ROW_CORRECTED[seed]
            assert mine == want and theirs in note and mine not in note, (role, mine)
        else:
            assert mine in note                                           # the note's own row, verbatim
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
    for phrase in ("fractional, never rounded",
                   "**fails at the fill**", "**counted apart**", "L_fill = min(l, c - max(x_stop, x_flat))",
                   "**the profit-level row**", "(level + entry + x_target) / tick dollars",
                   "**Every trade taken has gross expectation exactly zero**", "the conservative choice, as E-247",
                   "the race's own, L = min(l, c - x_stop)", "clipped at the floor and fails the account",
                   "at most 1024 steps a walk",
                   "a driftless two-point race between the barrier and the lattice point one step back",
                   "N-2 checked on every key at construction", "n^2 / 2^129", "first 64 seed indices",
                   "within 1.25 GB a worker", "the one-sided check (B-10's form", "never a second margin",
                   "25 % (`three_way_stats.GATE_DENIAL`", "10 % of signals missed", "SMALLER_J_GRID",
                   "z_pi sigma_M / sqrt(J)", "unless the joint held-out test's declaration is named",
                   "trigger-level", "re-declaring R-10's sampling"):
        assert phrase in flat, phrase
    assert "(c_L + z_pi)" not in flat and "whole ticks (`three_way_redraw.LATTICE` = 1)" not in flat
    assert "no account is stranded" not in flat and "the larger of x_stop and the flatten cost" not in flat
    assert "no trade where the room left is at most" not in flat
    assert "in net ticks" not in flat and "Every trade's gross expectation is exactly zero" not in flat
    assert "lattice step s dividing l and g" not in flat and "smallest common divisor" not in flat
    assert ("T the limit known at the fill -- the earliest of the 15:10 CT flatten, a scheduled window's start and "
            "the max hold's end -- never the realised exit, the same T for s and n") in flat
    assert "**governed by template v3's section 7 as pinned**" in flat and "**nothing in the runner reads T**" in flat
    assert "2048 steps" not in flat and "Every walk is at most 1024 steps by construction" in flat
    assert "only truncates the walk, to the steps completed by it -- floor(n tau / T)" in flat
    assert "a known approximation of the walk" in flat and "the time limit capped at the 15:10 CT flatten" not in flat
    assert "**An H3-A laxity stops H3-D: the rule is then defective**" in flat and "**a new declaration follows**" in flat
    assert "the tests' seed (H3-A's report is a design check)" not in flat
    assert "**its rng the one declared key `three_way_seeds.SMALLER_J_REPORT`**" in flat


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



def test_pi_stars_value_is_written_beside_its_constant(text: str) -> None:
    """The gatekeeper's item 3: pi\\*'s value stands beside `family_stats.MDL_POWER` and equals it."""
    from extended import family_stats as FS

    m = re.search(r"^\| pi\\\* \| the power target \| fixed \| \*\*([0-9.]+)\*\* \(`family_stats\.MDL_POWER`\)",
                  text, re.MULTILINE)
    assert m and float(m.group(1)) == FS.MDL_POWER


def test_the_design_notes_version_is_fixed(text: str) -> None:
    """The gatekeeper's item 7: the text names the design note's version by its LF sha256, and the note is that file."""
    shas = re.findall(r"`docs/plans/THREE_WAY_TEST_design\.md` \*\*at LF sha256 `([0-9a-f]{64})`\*\*", text)
    assert len(shas) == 1
    assert hashlib.sha256(NOTE.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == shas[0]


def test_the_build_commit_is_named_and_reachable(text: str) -> None:
    """The gatekeeper's pin condition: the text names one build commit (in its head and in section 17), an ancestor of
    this tree's HEAD, at which every build file the head lists exists."""
    head = _flat(text[:text.index("\n## 0. ")])
    commits = set(re.findall(r"\*\*at build commit `([0-9a-f]{7,40})`\*\*", text))
    assert len(commits) == 1 and len(re.findall(r"at build commit `", text)) == 2
    c = commits.pop()
    for f in BUILD_FILES:
        assert f"`{f}`" in head or f"`extended/{f}`" in head, f
    git = ["git", "-C", str(ROOT)]
    assert subprocess.run(git + ["merge-base", "--is-ancestor", c, "HEAD"], capture_output=True).returncode == 0, c
    listed = subprocess.run(git + ["ls-tree", "--name-only", c, "extended/"], capture_output=True, text=True,
                            check=True).stdout.split()
    assert {f"extended/{f}" for f in BUILD_FILES} <= set(listed)
