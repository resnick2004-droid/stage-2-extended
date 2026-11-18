"""Q-153: the three-way test's design note (`docs/plans/THREE_WAY_TEST_design.md`), checked on its own text and on the
repository's files (no engine, no bar, no result file; fast). Corrective cycle 1 answers the red team's read
(`docs/reviews/THREE_WAY_TEST_2026-11-18.md`).

- **the sections present** -- 0 to 7 and Appendices A and B;
- **the arithmetic is the script's** -- Appendix A's fenced block equals, line for line, what
  `docs/plans/scripts/three_way/three_way_arith.py`'s `report()` prints; the prose's counts are held to the script's
  values (m-13);
- **the constants against their sources** (m-13) -- the dates against E-208's row, k = 13 against CLAUDE.md, H_g
  against Stage 2's gate configs, the power target against `family_stats.MDL_POWER`; the bounds' constants against
  their formulas; and a seeded Monte-Carlo coverage check of the Hoeffding and empirical-Bernstein bounds at a
  feasible level, on skewed and on non-identical terms;
- **the race redraw** (B-1) -- every redrawn trade's gross expectation is exactly zero at every cushion on a grid of
  (stop, target, cushion), and the unraced form has a positive edge exactly where the stop exceeds the cushion;
- **the race with costs** (N-5) -- every trade's net expectation is exactly minus its costs at every cushion, and its
  worst change never passes the floor;
- **the seed keys** (m-4, N-8, N-10) -- numpy's trailing-zero and split-word equivalences are real (the traps); the
  note's fixed-length keys refuse words of 2^32 or more and never give one `generate_state` across kinds and indices;
- **the time conditions' arithmetic** -- the orthant formulas at their known points;
- **the seed block** -- section 7's table lists ten consecutive seeds once each; no other tracked file and no other
  working text file holds a literal of them; and an arithmetic fold over every tracked `.py` (pure-literal expressions
  with `**`, names bound to them plainly, by tuple unpacking or by augmented assignment; N-9) finds the block's construction only in this file, which it must find (m-5's positive
  control). The block is built here by arithmetic, so this file holds no literal of it;
- **the scans work** -- a planted copy of a seed in a temporary repository is found by both scans.
"""
from __future__ import annotations

import ast
import importlib.util
import itertools
import math
import re
import subprocess
import warnings
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
NOTE = ROOT / "docs" / "plans" / "THREE_WAY_TEST_design.md"
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"          # the licensed bars and atlas: never scanned
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini", ".jsonl"}
THIS = Path(__file__).resolve().relative_to(ROOT).as_posix()

#: section 7's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 587
SEED_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
#: the repository files allowed to hold a seed of the block besides the note (none yet: H3's build adds its own here)
DECLARED_USES: tuple[str, ...] = ()
#: the files allowed to construct the block by arithmetic (this test; H3's seed module when it is written)
DERIVED_USES: tuple[str, ...] = (THIS,)
SECTIONS = ("## 0. ", "## 1. ", "## 2. ", "## 3. ", "## 4. ", "## 5. ", "## 6. ", "## 7. ", "## Appendix A. ",
            "## Appendix B. ")
ARITH_START = "<!-- three_way_arith: begin -->"
ARITH_END = "<!-- three_way_arith: end -->"


@pytest.fixture(scope="module")
def text() -> str:
    return NOTE.read_bytes().decode("utf-8").replace("\r\n", "\n")


@pytest.fixture(scope="module")
def arith():
    spec = importlib.util.spec_from_file_location("three_way_arith", ARITH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sections_present(text: str) -> None:
    pos = [text.find("\n" + s) for s in SECTIONS]
    assert all(p >= 0 for p in pos), [s for s, p in zip(SECTIONS, pos) if p < 0]
    assert pos == sorted(pos), "the sections are in order"


def test_appendix_a_is_the_scripts_output(text: str, arith) -> None:
    i, j = text.index(ARITH_START), text.index(ARITH_END)
    block = text[i + len(ARITH_START):j].strip()
    assert block.startswith("```text\n") and block.endswith("\n```"), "Appendix A holds one fenced text block"
    assert block[len("```text\n"):-len("\n```")] == arith.report()


def test_the_levels_arithmetic(arith) -> None:
    a = arith.level(13)
    assert a == pytest.approx(0.05 / 182)
    assert arith.b_min(a) == 12 and 2.0 ** -12 <= a < 2.0 ** -11
    wh = arith.weekdays(*arith.HELD_OUT)
    assert all(arith.disjoint_units(wh, h) < arith.b_min(a) for h in (63, 126, 252, 504))
    assert arith.weekdays("2024-01-01", "2024-01-07") == 5          # Monday to Sunday: five weekdays
    assert len(arith.weekday_dates(*arith.HELD_OUT)) == wh
    assert arith.complete_starts(100, 63) == 38 and arith.start_blocks(200, 63) == 2
    assert arith.binom_tail(3, 3) == 0.125 and arith.binom_tail(4, 3) == pytest.approx(5 / 16)
    assert arith.n_certify(0.05) == 59                                 # the rule of three's exact form


def test_the_prose_counts_are_the_scripts(text: str, arith) -> None:
    """m-13: each count the prose states in words is the script's value."""
    words = {1: "one", 2: "two", 4: "four", 10: "ten", 12: "twelve", 13: "thirteen"}
    wh, ws = arith.weekdays(*arith.HELD_OUT), arith.weekdays(*arith.SEARCH)
    b13 = arith.b_min(arith.level(13))
    phrases = (
        f"at most {words[arith.disjoint_units(wh, 63)]} disjoint 63-session units",
        f"{words[b13]} are needed",
        f"B_min = {b13}",
        f"At k = 14 to 17, B_min = {arith.b_min(arith.level(14))}",
        f"at most {words[arith.disjoint_units(wh, arith.H_GATE)]} disjoint {arith.H_GATE}-session block",
        f"search years hold at most {words[arith.disjoint_units(ws, arith.H_GATE)]}",
    )
    flat = " ".join(text.split())                                         # the prose's line breaks are not words
    for phrase in phrases:
        assert phrase in flat, f"the note's prose should state: {phrase!r}"
    assert "eleven" not in text, "the partial-unit count is printed in Appendix A, never typed (m-11)"


def test_the_constants_against_their_sources(arith) -> None:
    """m-13: one check of each declared constant against the file it comes from."""
    dec = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    row = next(line for line in dec.splitlines() if line.startswith("| E-208 |"))
    assert f"NQ {arith.SEARCH[0]} to {arith.SEARCH[1]}" in row
    assert f"{arith.HELD_OUT[0]} to {arith.HELD_OUT[1]}" in row
    assert re.search(r"(the next is k = 13|; next 13\.)", (ROOT / "CLAUDE.md").read_text(encoding="utf-8")) and arith.KS[0] == 13  # E-210 reworded CLAUDE.md's k line ("next 13")
    for cfg in ("fv2_grid.yaml", "fv3_corrected_portfolio.yaml"):
        assert f"horizon_days: {arith.H_GATE}" in (ROOT / "vendor" / "stage2" / "config" / cfg).read_text("utf-8")
    from extended import family_stats
    assert arith.POWER == family_stats.MDL_POWER
    a = arith.level(13)
    assert arith.hoeffding_constant(a) == pytest.approx(math.sqrt(-2 * math.log(a)))
    c1, c2 = arith.eb_constants(a)
    assert c1 == pytest.approx(math.sqrt(2 * math.log(2 / a))) and c2 == pytest.approx(7 * math.log(2 / a) / 3)


def test_the_bounds_cover_at_a_feasible_level(arith) -> None:
    """m-13: the bounds as coded hold their level by simulation at alpha = 0.05 -- the empirical-Bernstein bound on
    skewed i.i.d. replicates, Hoeffding's on independent, non-identical terms in [-1, 1]; seeded from the block's
    first seed (section 7: the tests' role)."""
    alpha, reps = 0.05, 4000
    rng = np.random.default_rng(arith.seed_key(SEED_BLOCK[0], "test", test=1, replicate=0))
    for J in (5, 20, 200):
        x = (rng.random((reps, J)) < 0.03).astype(float) * 2.0 - 1.0      # mean -0.94, heavily skewed
        miss = sum(arith.eb_lower(row, alpha) > -0.94 for row in x)
        assert miss <= reps * alpha, (J, miss)
    p = np.linspace(0.05, 0.95, 400)                                      # non-identical terms
    x = (rng.random((reps, p.size)) < p).astype(float) * 2.0 - 1.0
    mu = float((2 * p - 1).mean())
    miss = sum(arith.hoeffding_lower(row, alpha) > mu for row in x)
    assert miss <= reps * alpha


def test_the_race_redraw_has_zero_expectation_at_every_cushion(arith) -> None:
    """B-1's oracle: with zero costs, every redrawn trade's gross expectation is exactly zero, for every stop, target
    and cushion on the grid; the unraced form (a win at l / (l + g), the loss clipped) has a positive edge exactly
    where the stop exceeds the cushion."""
    grid = range(1, 41)
    for l, g, c in itertools.product(grid, range(1, 41, 3), grid):
        p, win, loss = arith.race_redraw(l, g, c)
        assert isinstance(p, Fraction) and arith.gross_expectation(p, win, loss) == 0
        assert loss == min(l, c)
        edge = arith.unraced_edge(l, g, c)
        assert (edge > 0) == (l > c) and (edge == 0) == (l <= c)
        if l > c:
            assert edge == Fraction(g * (l - c), l + g)
    with pytest.raises(ValueError):
        arith.race_redraw(10, 10, 0)


def test_the_race_with_costs_nets_minus_its_costs_and_never_passes_the_floor(arith) -> None:
    """N-5's oracle: with entry and exit costs (fractional ticks allowed), the race at the cushion less the exit cost
    gives every trade a net expectation of exactly minus its costs, at every cushion (fractional cushions included),
    and its worst balance change never passes the floor, so the engine's clip never binds."""
    costs = [Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 2)]
    cushions = [Fraction(k, 4) for k in range(1, 161, 3)]
    for l, g, c, e, x in itertools.product(range(1, 41, 4), range(1, 41, 5), cushions, costs, costs):
        if c - e - x <= 0:
            with pytest.raises(ValueError):
                arith.net_expectation(l, g, c, e, x)
            continue
        net, worst = arith.net_expectation(l, g, c, e, x)
        assert net == -(e + x), (l, g, c, e, x)
        assert worst >= -c, (l, g, c, e, x)


def test_the_seed_key_trap_and_the_fixed_length_keys(arith) -> None:
    """m-4 and N-8: numpy reads [a, b] and [a, b, 0, 0] as one stream, and splits a word of 2^32 or more
    ([7, 2**32 + 5] is [7, 5, 1]); the note's keys -- fixed in length per kind, a distinct nonzero tag, every word
    below 2^32 -- never give one `generate_state` across kinds and indices; built under the tests' own seed (N-10)."""
    a, b = 11, 7
    assert np.array_equal(np.random.default_rng([a, b]).random(4), np.random.default_rng([a, b, 0, 0]).random(4))
    assert not np.array_equal(np.random.default_rng([a, b]).random(4), np.random.default_rng([a, 0, b]).random(4))
    assert arith.key_state([7, 2 ** 32 + 5]) == arith.key_state([7, 5, 1])            # the split-word trap
    assert np.array_equal(np.random.default_rng([7, 2 ** 32 + 5]).random(4),
                          np.random.default_rng([7, 5, 1]).random(4))
    seed = SEED_BLOCK[0]
    with pytest.raises(ValueError):
        arith.seed_key(seed, "test", test=1, replicate=2 ** 32 + 5)
    with pytest.raises(ValueError):
        arith.seed_key(2 ** 32 + 5, "test", test=1, replicate=0)
    arith.seed_key(seed, "test", test=1, replicate=2 ** 32 - 1)                        # the largest word passes
    seen: dict[tuple[int, ...], tuple] = {}
    for kind, (_, names) in arith.KEY_KINDS.items():
        for vals in itertools.product(range(3), repeat=len(names)):
            k = arith.seed_key(seed, kind, **dict(zip(names, vals)))
            s = arith.key_state(k)
            assert s not in seen, (kind, vals, seen.get(s))
            seen[s] = (kind, vals)
    tags = [t for t, _ in arith.KEY_KINDS.values()]
    assert len(set(tags)) == len(tags) and all(t > 0 for t in tags)
    with pytest.raises(ValueError):
        arith.seed_key(seed, "history", part=1)                           # a field missing
    coin = set(arith.KEY_KINDS["coin"][1])
    assert coin >= {"part", "history", "start", "underlying"}             # m-4; N-2 (choice 3); N-4 (one underlying)
    assert not coin & {"account", "firm", "instrument"}                   # m-9; N-4


def test_the_orthant_formulas(arith) -> None:
    assert arith.orthant(np.eye(2)) == pytest.approx(0.25)
    assert arith.orthant(np.ones((2, 2))) == pytest.approx(0.5)
    assert arith.orthant(np.eye(3)) == pytest.approx(0.125)
    assert arith.orthant(np.ones((3, 3))) == pytest.approx(0.5)


# ------------------------------------------------------------------------------------------------- the seed block


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


def test_seed_table(text: str) -> None:
    table = _section(text, "\n## 7. ", "\n## Appendix A. ")
    for seed in SEED_BLOCK:
        rows = re.findall(rf"^\| {seed} \| ([^|]+) \| ([^|]+) \|", table, re.MULTILINE)
        assert len(rows) == 1, f"seed {seed} must have exactly one row in section 7's table"
        role, status = (x.strip() for x in rows[0])
        assert role and status in {"design check", "deciding", "tests", "spare, drawn by nothing"}, (seed, status)
        assert re.search(rf"\b{seed}\b", text)
    others = re.findall(rf"\b{_PREFIX}[0-9]\b", text)
    assert set(int(x) for x in others) <= set(SEED_BLOCK)


def _git_hits(repo: Path) -> list[str]:
    """Tracked files holding a seed of the block, word-bounded (`git grep`), as 'path:line' strings."""
    from extended import git_scan  # the suite's time-limited scan (Q-156, E-217)
    out = git_scan.run(["git", "grep", "-IwnE", f"{_PREFIX}[0-9]"], cwd=repo, text=True)
    assert out.returncode in (0, 1), out.stderr
    return [line for line in out.stdout.splitlines() if line]


def _working_hits(base: Path) -> list[str]:
    """Working text files under `base` (the licensed data and `.git` excluded) holding a seed of the block."""
    pat = re.compile(rb"\b" + str(_PREFIX).encode() + rb"[0-9]\b")
    hits = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES or ".git" in p.parts:
            continue
        if VENDOR_DATA == p or VENDOR_DATA in p.parents:
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if str(_PREFIX).encode() in data and pat.search(data):
            hits.append(p.relative_to(base).as_posix())
    return hits


def _allowed() -> set[str]:
    return {NOTE.relative_to(ROOT).as_posix(), *DECLARED_USES}


def test_seed_block_nowhere_else_tracked() -> None:
    allowed = _allowed()
    hits = [h for h in _git_hits(ROOT) if h.split(":", 1)[0] not in allowed]
    assert not hits, "the seed block appears outside its declared uses:\n" + "\n".join(hits[:20])


def test_seed_block_nowhere_else_working() -> None:
    allowed = _allowed()
    hits = [h for h in _working_hits(ROOT) if h not in allowed]
    assert not hits, "the seed block appears in a working file outside its declared uses:\n" + "\n".join(hits[:20])


def test_the_seed_scans_find_a_planted_seed(tmp_path: Path) -> None:
    """Positive control: a planted copy is found by both scans, and a clean tree finds none."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "clean.txt").write_text("nothing here\n", encoding="utf-8")
    subprocess.run(["git", "add", "clean.txt"], cwd=tmp_path, check=True, capture_output=True)
    assert not _git_hits(tmp_path) and not _working_hits(tmp_path)
    planted = tmp_path / "sub" / "planted.py"
    planted.parent.mkdir()
    planted.write_text(f"SEED = {SEED_BLOCK[4]}\n", encoding="utf-8")
    assert _working_hits(tmp_path) == ["sub/planted.py"]
    subprocess.run(["git", "add", "sub/planted.py"], cwd=tmp_path, check=True, capture_output=True)
    assert [h.split(":", 1)[0] for h in _git_hits(tmp_path)] == ["sub/planted.py"]


# ------------------------------------------------------------------------------------------------- the fold (m-5)

_OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
        ast.FloorDiv: lambda a, b: a // b if b else None,
        ast.Pow: lambda a, b: a ** b if 0 <= b <= 64 and abs(a) < 10 ** 6 else None}
_LIMIT = 10 ** 15


def _fold(node: ast.AST, env: dict[str, int]) -> int | None:
    """The integer value of a pure-literal expression, names bound earlier to such an expression included; None when
    it is not one (a loop index, a call, a string)."""
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _fold(node.operand, env)
        return None if v is None else -v
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        a, b = _fold(node.left, env), _fold(node.right, env)
        if a is None or b is None or abs(a) > _LIMIT or abs(b) > _LIMIT:
            return None
        v = _OPS[type(node.op)](a, b)
        return v if v is None or abs(v) <= _LIMIT else None
    return None


class _Folder(ast.NodeVisitor):
    """Walks a module in source order, binding names (plainly, by tuple unpacking, by augmented assignment) to folded
    values, and records every expression or binding whose value is a target."""

    def __init__(self, targets: set[int]):
        self.targets, self.env, self.lines = targets, {}, []

    def _bind(self, target: ast.AST, value: ast.AST | None, line: int) -> None:
        if isinstance(target, ast.Name):
            v = None if value is None else _fold(value, self.env)
            if v is None:
                self.env.pop(target.id, None)
            else:
                self.env[target.id] = v
                if v in self.targets:
                    self.lines.append(line)
        elif isinstance(target, (ast.Tuple, ast.List)):
            same = isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(target.elts)
            vals = value.elts if same else [None] * len(target.elts)
            for t_, v_ in zip(target.elts, vals):
                self._bind(t_, v_, line)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.generic_visit(node)
        for target in node.targets:
            self._bind(target, node.value, node.lineno)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.generic_visit(node)
        if isinstance(node.target, ast.Name):
            expr = ast.BinOp(left=ast.Name(id=node.target.id, ctx=ast.Load()), op=node.op, right=node.value)
            self._bind(node.target, expr, node.lineno)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if _fold(node, self.env) in self.targets:
            self.lines.append(node.lineno)
        self.generic_visit(node)


def _fold_hits(path: str, source: str) -> list[str]:
    """Expressions and bindings in `source` folding to the block's prefix, the prefix times ten, or a seed of the
    block."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")                                # other files' escape warnings
            tree = ast.parse(source)
    except SyntaxError:
        return []
    f = _Folder({_PREFIX, _PREFIX * 10, *SEED_BLOCK})
    f.visit(tree)
    return [f"{path}:{n}" for n in sorted(set(f.lines))]


def _fold_scan(repo: Path) -> set[str]:
    """Every tracked `.py`, with no prefilter (N-9)."""
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=repo, capture_output=True, text=True,
                           check=True).stdout.splitlines()
    found = set()
    for f in files:
        p = repo / f
        if p.is_file() and VENDOR_DATA not in p.parents:
            found.update(h.split(":", 1)[0] for h in _fold_hits(f, p.read_text(encoding="utf-8", errors="replace")))
    return found


def test_the_arithmetic_fold_finds_the_construction_only_where_declared() -> None:
    found = _fold_scan(ROOT)
    tracked = subprocess.run(["git", "ls-files", THIS], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if tracked:
        assert THIS in found, "the fold must find this file's own construction of the block (positive control)"
    assert found <= set(DERIVED_USES), f"the block is constructed by arithmetic outside its declared uses: {found}"


def _lines(src: str) -> list[int]:
    return sorted({int(h.split(":")[1]) for h in _fold_hits("x.py", src)})


def test_the_fold_sees_names_and_pure_literals() -> None:
    src = "P = 2026 * 1000 + 587\nS = P * 10 + 3\nQ = 2026 * 1000 + 586\nfor i in range(3):\n    x = P * 10 + i\n"
    assert _lines(src) == [1, 2, 5]


def test_the_fold_sees_powers_without_the_year_digits() -> None:
    """N-9: no prefilter on the year's digits, and `**` folds: 2 ** 11 - 22 is the year, written without them."""
    src = "Y = 2 ** 11 - 22\nP = Y * 1000 + 587\n"
    assert "2026" not in src and _lines(src) == [2]


def test_the_fold_sees_augmented_assignment() -> None:
    src = "P = 2026\nP *= 1000\nP += 587\nQ = 5\nQ += 1\n"
    assert _lines(src) == [3]


def test_the_fold_sees_tuple_unpacking() -> None:
    src = "A, B = 2026 * 1000, 587\nP = A + B\nC, D = f(), 1\n"
    assert _lines(src) == [2]
