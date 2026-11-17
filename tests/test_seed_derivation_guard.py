"""Q-128 (E-171): no seed of this repository is derived by adding an offset to a named seed.

A named seed is declared for one use. `NAME_SEED + 1000 + i` with i up to several hundred walks through the seed space
that later declarations pin as their own blocks, so a derived range can draw seeds another block owns -- the rule
"a declared seed is used nowhere else" broken without any literal being written. Derived streams are children of the
named seed instead (`numpy.random.SeedSequence(NAME_SEED, spawn_key=(stream, i))`), which depend on no other number.

**The guard** (an AST scan of every `.py` under `tests/`, `extended/`, `scripts/` and `identity/`; `vendor/` is
Stage 2's and is not scanned): it fails on an additive expression (a chain of `+` and `-`) one of whose terms is a
**seed name** -- a name or attribute whose identifier contains `seed` in any case, that name subscripted, or `int()` of
it -- and another term of which is
- an integer literal of two or more digits, or any term with such a literal inside it (`1000 * G`, `100 + i`), or
- a bare name (a loop index or a variable: `NAME_SEED + i`), whose reach the scan cannot bound.

A single-digit literal offset alone (`NAME_SEED + 1`) is outside the pattern (the brief's threshold); the hand-back of
Q-128 lists those found. **The allow-list** holds the cases that are legitimate or not this repository's to change,
each with its reason; an entry that no longer matches anything fails the test, so the list cannot go stale.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCANNED = ("tests", "extended", "scripts", "identity")

#: (file, expression as `ast.unparse` writes it): why it stands
ALLOW = {
    ("extended/lift_bound.py", "int(seed) + 1000 * int(G) + int(lags)"):
        "a pinned blob (E-115's third read hand-checked it: the offset keeps the seed's residue modulo 1,000 plus the "
        "lag count, landing in neither Q-108 block); not editable here. Q-128's scan found no declared literal on its "
        "reach (G up to 20,000, lags 1 to 4)",
    ("scripts/rd01_reading.py", "R.F.LADDER_SEED + i"):
        "RD-01's section 12 block written out seed by seed: the block's own seeds, i over its literal sequence of "
        "statuses (a declared use, not a derivation beyond it)",
    ("tests/q121_synthetic.py", "SEED_SHIFT + k"):
        "a small seed far below the dated seed space, k over a handful of cuts; Q-121's test file, left as declared "
        "by its own item (listed in Q-128's hand-back)",
    ("tests/p14_validation_b_checks.py", "int(seed) + (0 if _mb is None else int(_mb) * 7919)"):
        "a fake engine's toy cash path inside Q-18b's check: its base is one of Stage 2's `path_seeds` draws (uniform "
        "on 0 to 2**31 - 1, not a named seed of a block) and the offset only separates the mean-block schemes; the "
        "check asserts which path seeds are used, never the toy path's values",
}


def seed_term(node: ast.AST) -> bool:
    """A name or attribute whose identifier contains 'seed' (any case), that subscripted, or int() of it."""
    if isinstance(node, ast.Name):
        return "seed" in node.id.lower()
    if isinstance(node, ast.Attribute):
        return "seed" in node.attr.lower()
    if isinstance(node, ast.Subscript):
        return seed_term(node.value)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "int" \
            and len(node.args) == 1 and not node.keywords:
        return seed_term(node.args[0])
    return False


def _terms(node: ast.AST) -> list[ast.AST]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
        return _terms(node.left) + _terms(node.right)
    return [node]


def _offset(term: ast.AST) -> bool:
    if isinstance(term, ast.Name):
        return True
    return any(isinstance(n, ast.Constant) and type(n.value) is int and abs(n.value) >= 10 for n in ast.walk(term))


def derivations(text: str) -> list[tuple[int, str]]:
    """(line, expression) of every maximal additive chain adding an offset of the pattern to a seed name."""
    tree = ast.parse(text)
    inner: set[int] = set()
    out = []
    for node in ast.walk(tree):                              # breadth first: a chain is met before its sub-chains
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub))) or id(node) in inner:
            continue
        terms = _terms(node)
        for n in ast.walk(node):
            if n is not node and isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub)):
                inner.add(id(n))
        if any(seed_term(t) for t in terms) and any(_offset(t) for t in terms if not seed_term(t)):
            out.append((node.lineno, ast.unparse(node)))
    return out


def _sources():
    for d in SCANNED:
        for p in sorted((ROOT / d).rglob("*.py")):
            if "__pycache__" not in p.parts:
                yield p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8")


def test_no_seed_is_derived_by_an_additive_offset():
    found, matched = [], set()
    for rel, text in _sources():
        for line, expr in derivations(text):
            if (rel, expr) in ALLOW:
                matched.add((rel, expr))
            else:
                found.append(f"{rel}:{line}: {expr}")
    assert not found, "additive seed derivations (use a SeedSequence child of the named seed):\n" + "\n".join(found)
    assert matched == set(ALLOW), f"allow-list entries matching nothing: {sorted(set(ALLOW) - matched)}"


@pytest.mark.parametrize("code, flagged", [
    ("SEED_X + 1000 + i", True),
    ("SEED_X + 100 + i", True),
    ("SEED_X + 300", True),
    ("SEED_X + i", True),
    ("M.SEED_X - 12", True),
    ("BLOCK_SEEDS[2] + 50", True),
    ("int(seed) + 1000 * int(G)", True),
    ("seed + 100_000 * i + 1_000 * j", True),
    ("SEED_X + 1", False),                                  # a single digit: outside the pattern
    ("BASE + 1000 + i", False),                             # no seed name
    ("np.random.SeedSequence(SEED_X, spawn_key=(2, i))", False),
    ("m + np.random.default_rng([SEED_X, 6, j]).normal(0.0, 1.0, 3)", False),
    ("'notes: ' + ', '.join(seed_notes)", False),
])
def test_the_pattern(code, flagged):
    assert bool(derivations(code + "\n")) is flagged


def test_the_guard_fails_on_the_old_lookahead_file():
    """The file as it stood before Q-128 (master at 88df481, the commit the item started from) has the derivations."""
    r = subprocess.run(["git", "show", "88df481c86429207dad7cd99a50b7903d3c39989:tests/test_features_lookahead.py"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        pytest.skip("the pre-Q-128 commit is not in this clone's history")
    got = sorted(expr for _, expr in derivations(r.stdout))
    assert got == sorted(["SEED_REPLACE + i", "SEED_REPLACE + 100 + i", "SEED_REPLACE + 1000 + i",
                          "SEED_REPLACE + 200 + i", "SEED_REPLACE + 300"]), got
