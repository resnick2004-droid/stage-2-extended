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
                   + tuple(f"gk {i}" for i in range(1, 8)) + ("gk pins",)
                   + ("c2-1", "c2-2", "c2-3", "c2 notes") + tuple(f"rt {i}" for i in range(1, 10)))
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


def _note_at_build(text: str) -> bytes:
    """The design note at H3's declared build commit (the exact version H3 copied before W42-R1 updated the living
    design note's E-230 / H7-row sections)."""
    commit = re.findall(r"\*\*at build commit `([0-9a-f]{7,40})`\*\*", text)[0]
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:docs/plans/THREE_WAY_TEST_design.md"],
                       capture_output=True, check=True)
    return r.stdout.replace(b"\r\n", b"\n")


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
    assert ("**R-10's rows (section 7) are governed by template v3's R-10 -- its section 5, \"The zero-edge "
            "convention\" -- as pinned by its hash row**") in sec18
    assert "template v3's section 7" not in flat
    heads = [f"\n## {n}. " for n in range(20)] + [f"\n## Appendix {a}. " for a in "ABCD"]
    pos = [text.find(h) for h in heads]
    assert all(p >= 0 for p in pos), [h for h, p in zip(heads, pos) if p < 0]
    assert pos == sorted(pos)


def test_the_admission_paragraph_is_the_notes_with_the_minors(text: str) -> None:
    mine = _between(text, DRAFT_MARKS).strip("\n").split("\n")
    theirs = _between(_note_at_build(text).decode("utf-8"), NOTE_MARKS).strip("\n").split("\n")
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
    got_lines = block[len("```text\n"):-len("\n```")].splitlines()
    cur_lines = mod.report().splitlines()
    assert len(got_lines) == len(cur_lines)
    # Every H3 row (and every non-H7-Hoeffding line) matches current h3_plan.py verbatim; W42-R1's merged
    # three_way_arith.py updates only the non-H3 Wave-6 "H7 held-out, Hoeffding" row from M=100 h=63 to W42_TEST_SEEDS.
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(got_lines, cur_lines)) if a != b]
    assert all("H7 held-out, Hoeffding" in a and "H7 held-out, Hoeffding" in b for _, a, b in diffs), diffs
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
    assert ("**governed by template v3's R-10 -- its section 5, \"The zero-edge convention\" -- as pinned by its hash "
            "row**") in flat and "**nothing in the runner reads T**" in flat
    assert "**H3-0 and H3-A do not run until that hash row is pinned.**" in flat
    assert "**if the two disagree, H3 is re-declared under a new row and never run on the old walk**" in flat
    assert ("fixed in H3-D's text at the k current at H3-D's pin; if k moves before H3-D runs, H3-D's text is "
            "re-declared under a new row at the new k, never adjusted at run time") in flat
    assert "26 refs" not in flat and "574 commits" not in flat
    assert "a test's known answer of 0.875" in flat
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
    """The gatekeeper's item 7: the text names the design note's version by its LF sha256, and the note at H3's
    declared build commit is that exact file."""
    shas = re.findall(r"`docs/plans/THREE_WAY_TEST_design\.md` \*\*at LF sha256 `([0-9a-f]{64})`\*\*", text)
    assert len(shas) == 1
    assert hashlib.sha256(_note_at_build(text)).hexdigest() == shas[0]


def test_the_build_commit_is_named_and_reachable(text: str) -> None:
    """The gatekeeper's pin condition: the text names one build commit (in its head and in section 17), an ancestor of
    this tree's HEAD, at which every build file the head lists exists."""
    head = _flat(text[:text.index("\n## 0. ")])
    commits = set(re.findall(r"\*\*at build commit `([0-9a-f]{7,40})`\*\*", text))
    assert len(commits) == 1 and len(re.findall(r"\*\*at build commit `", text)) == 2
    assert set(re.findall(r"build commit `([0-9a-f]{7,40})`", text)) == commits      # every mention the one commit
    c = commits.pop()
    for f in BUILD_FILES:
        assert f"`{f}`" in head or f"`extended/{f}`" in head, f
    git = ["git", "-C", str(ROOT)]
    assert subprocess.run(git + ["merge-base", "--is-ancestor", c, "HEAD"], capture_output=True).returncode == 0, c
    listed = subprocess.run(git + ["ls-tree", "--name-only", c, "extended/"], capture_output=True, text=True,
                            check=True).stdout.split()
    assert {f"extended/{f}" for f in BUILD_FILES} <= set(listed)
    same = subprocess.run(git + ["diff", "--quiet", c, "HEAD", "--", *(f"extended/{f}" for f in BUILD_FILES)])
    assert same.returncode == 0, f"a build file differs from the build commit {c}'s (the red team's finding 6)"



def test_the_counts_are_products_and_numbers(text: str) -> None:
    """The gatekeeper's c2-3: every check family is written as a product and its number, each factor the declared
    input's (Appendix A's R, Appendix C), and the laxity stop reads only the pooled counts at 0.05 over their number
    (a Bonferroni split: the family-wise false-stop rate at most 0.05 when every size is correct)."""
    from extended import three_way_h3a as H
    from extended import three_way_runner as RU
    from extended import three_way_stats as ST

    spec = importlib.util.spec_from_file_location("h3_plan_for_counts", PLAN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    R = {mod.base(name): r for name, r, *_ in mod.rows()}
    assert R["A1 same-design nulls"] == R["A2 exact-centred toy null"]
    r = R["A1 same-design nulls"]
    flat = _flat(text)
    # the factors as the checks run them (GK_H3_c3 item 1): A1's two same-design nulls (the antithetic twin, the
    # disjoint sets) on A1's design; A2's one exact-centred null on its pair; both on the two placeholder composites
    comps = ("P_B", H.TOY_COMPOSITE)                                    # the two placeholder composites
    composites = len(comps)
    bounds_fns = (ST.mcdiarmid, ST.eb_lower, ST.betting_lower)
    a1_nulls = ("antithetic", H.DISJOINT)
    a2_nulls = (H.A2_PAIR,)
    levels, bounds = len(H.LEVELS), len(bounds_fns)
    assert len(H.DISJOINT) == 2 and len(H.A2_PAIR) == 2
    a1 = len(a1_nulls) * composites * bounds * levels
    a2 = len(a2_nulls) * composites * bounds * levels
    pooled = a1 + a2
    assert (a1, a2, pooled) == (36, 18, 54)
    assert (f"{len(a1_nulls)} null classes (the antithetic twin, the disjoint sets, `DISJOINT`) x {composites} "
            f"composites") in flat and f"x {levels} feasible levels (`LEVELS`) = **{a1} pooled counts**" in flat
    assert (f"1 null class x {composites} composites (`P_B` alone and the clipped `TOY_COMPOSITE` -- **both, the "
            f"declaration's choice, made before any outcome**) x {bounds} bounds x {levels} feasible levels = "
            f"**{a2} pooled counts**") in flat
    assert f"**the pooled total {a1} + {a2} = {pooled}** -- the {pooled} pooled counts the stop reads" in flat
    assert f"over its part's R = {r} histories" in flat
    assert (f"{a1} x {r} = {a1 * r} (A1) and {a2} x {r} = {a2 * r} (A2), {a1 * r} + {a2 * r} = "
            f"**{(a1 + a2) * r}** in all") in flat
    assert "pooled counts a part" not in flat
    assert f"x {levels} feasible levels = **{1 * composites * levels} rates**, each over A3's {H.A3_HISTORIES}" in flat
    sizes, lev, eps, a = len(H.SIZE_GRID), len(H.P2_LEVERS), len(H.P3_EPS), len(H.P4_A)
    p1_bounds = len({"hoeffding", "eb"} & set(ST.LINEAR_PLANT_BOUNDS))    # 2.2 (a)'s (unclipped) and the EB
    p1 = 1 * p1_bounds * sizes * levels
    p2 = lev * composites * bounds * levels
    p3 = eps * composites * bounds * levels
    p4 = a * sizes * composites * bounds * levels
    assert f"x {p1_bounds} bounds" in flat and f"x {sizes} sizes x {levels} levels = {p1}" in flat
    assert f"P2, {lev} lever changes x {composites} composites x {bounds} bounds x {levels} levels = {p2}" in flat
    assert f"P3, {eps} values of epsilon x {composites} x {bounds} x {levels} = {p3}" in flat
    assert f"P4, {a} values of a x {sizes} base sizes x {composites} x {bounds} x {levels} = {p4}" in flat
    assert f"{p1} + {p2} + {p3} + {p4} = **{p1 + p2 + p3 + p4} pass rates**" in flat
    m1, m4 = 1 * p1_bounds * levels, a * composites * bounds * levels
    assert f"P1's 1 x {p1_bounds} x {levels} = {m1} and P4's {a} x {composites} x {bounds} x {levels} = {m4}, **{m1 + m4} MDLs**" in flat
    arms = len(RU.stress_arms())
    assert f"{arms} arms (+1 tick, +2 ticks, 10 % missed) x 5 schedules" in flat and f"= **{arms * 5} runs**" in flat
    sec11 = _flat(text[text.index("\n## 11. "):text.index("\n## 12. ")])
    assert f"**The laxity stop reads only the {pooled} pooled size counts** (section 8: A1's {a1} and A2's {a2})" in sec11
    assert (f"**The stop's code:** H3-A's report code is built after the pin; it applies this one-sided limit, 1 - 0.05 "
            f"/ {pooled}, to the {pooled} pooled counts only; `three_way_stats.size_label` (E-052's two-sided label) is "
            "at most a label reported beside the stop and never decides; the report code has its own tests and a "
            "red-team diff check before H3-A runs") in sec11
    sec14 = _flat(text[text.index("\n## 14. "):text.index("\n## 15. ")])
    assert (f"every **pooled** size count shows no laxity at its one-sided limit 1 - 0.05 / {pooled} (section 11); the "
            "per-history counts are reported beside and stop nothing") in sec14
    assert "every size count shows no laxity at the feasible levels" not in flat
    sec17 = _flat(text[text.index("\n## 17. "):text.index("\n## 18. ")])
    assert ("**H3-A's report code** -- the code that computes section 11's stop -- **is not in this build**" in sec17
            and f"applies section 11's one-sided limit 1 - 0.05 / {pooled} to the {pooled} pooled counts only" in sec17
            and "never deciding, and has its own tests and a red-team diff check before H3-A runs" in sec17)
    assert "**Text 2, re-declared after the gatekeeper's GK_H3_c3 (cycles exhausted)**" in text[:600]
    assert f"at **0.05 / {pooled}**" in sec11 and f"a Bonferroni split across the {pooled} pooled counts" in sec11
    assert "**the per-history counts are reported beside the pooled ones and never stop anything**" in sec11
    assert pooled * (0.05 / pooled) <= 0.05 + 1e-15                    # the union bound: the family-wise rate


TEMPLATE_PIN = re.compile(r"`(prereg/TEMPLATE_design_search\.md)` sha256 `([0-9a-f]{64})`")
#: template v3's R-10 clauses the walk at the build commit implements on S1's timed exits (section 5)
R10_CLAUSES = ("s = max(1, ceil(sigma sqrt(T) / sqrt(`WALK_MAX`)))",
               "**One T for both s and n (s-b):** T is the limit known at the fill for every row",
               "| the 15:10 CT flatten | the stopped walk, T to the flatten |",
               "| its max hold | the stopped walk, T to the max hold's end |",
               "n = round(sigma^2 T / s^2)")


def test_the_pinned_r10_agrees_with_the_walk_at_the_build_commit(text: str) -> None:
    """The lead's ruling on the gatekeeper's c2-1. Always: S1's two timed exits at the build commit's code take T as the
    earlier of the max hold's end and 15:10 CT, and that one T sets both the step and the count. At the pin of template
    v3's hash row (`prereg/TEMPLATE_design_search.md` sha256 in DECISIONS.md): the file is that hash, its section 5
    ("The zero-edge convention") holds R-10 with every clause above; a disagreement fails here, and H3 is re-declared
    under a new row, never run on the old walk. Until that row exists, H3-0 and H3-A do not run and this half skips."""
    import numpy as np

    from extended import three_way_redraw as RD
    from extended import three_way_s1 as S1

    commit = re.findall(r"\*\*at build commit `([0-9a-f]{7,40})`\*\*", text)[0]
    git = ["git", "-C", str(ROOT)]
    changed = subprocess.run(git + ["diff", "--name-only", commit, "HEAD", "--", "extended/three_way_s1.py",
                                    "extended/three_way_redraw.py", "extended/three_way_journey.py"],
                             capture_output=True, text=True, check=True).stdout.split()
    assert not changed, f"the walk's code moved since the build commit {commit}: {changed}"
    params = S1.S1Params(n_sessions=2, time_limit=90.0, rate=0.0)
    vol = np.full(2, 6.72)
    spec = S1.DesignSpec("r10", stream="A", fixed_stop=37, rr=55 / 37, walk_step=1, per_session=1, latency=5)
    for slot, reason in ((1000, "max_hold"), (1300, "flatten")):
        day = (S1.Arrival(slot, 9000.0, "A"),)
        hist = S1.S1History(params, vol, np.zeros(2), {"A": (day, ()), "B": ((), ())})
        tr = S1.schedule(spec, hist).trades[0]
        T = min(params.time_limit, float(S1.SESSION_END - tr.entry))   # the earlier of the max hold and 15:10 CT
        assert tr.exit_reason == reason and tr.law == "walk"
        s = RD.walk_step(6.72, T)
        assert (tr.walk_step, tr.walk_n) == (s, RD.walk_steps(6.72, T, s)), reason

    pins = TEMPLATE_PIN.findall((ROOT / "DECISIONS.md").read_text(encoding="utf-8"))
    if not pins:
        pytest.skip("template v3's hash row is not pinned yet: H3-0 and H3-A do not run (section 16)")
    rel, want = pins[-1]
    tpl = ROOT / rel
    assert hashlib.sha256(tpl.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == want, rel
    body = _lf(tpl)
    sec5 = _flat(body[body.index("\n## 5. The zero-edge convention"):body.index("\n## 6. ")])
    assert "**R-10: the redraw for a trade that ends at a time limit**" in sec5
    missing = [c for c in R10_CLAUSES if _flat(c) not in sec5]
    assert not missing, ("the pinned R-10 disagrees with the walk at the build commit on S1's timed exits: H3 is "
                         f"re-declared under a new row and never run on the old walk; missing: {missing}")
