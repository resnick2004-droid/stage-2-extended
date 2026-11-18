"""RD-05's T-13 (`prereg/RD-05_firm_modes.md` 17.2, 17.3, 15; 4.7 item 1; 13.2), and the loaders' refusals:

* the seeds of section 15 appear in the build only where section 15 declares them -- in `extended/modes_terms.py`'s
  `SEEDS` (each in use, by its role) and `RESERVED_SEEDS` (the four reserved), nowhere else in the build's files (T-0's
  `DECLARED_USES` holds the file; this test holds the file's contents to the table);
* 17.2's literal check: no number in the adapters' code (outside comments, docstrings and the declared tables) equals a
  rule value the record gives any mode-corner -- the rule values computed here from the loaded terms;
* the tier-1 counts at zero on a toy firm's trade log, and each firing on a hand-broken log (overlapping positions, an
  entry live inside a window, a position held through a window's start, full size into news);
* the loaders refuse a non-verified value and the step gates refuse what section 18 says they refuse.
"""
from __future__ import annotations

import ast
import dataclasses
import re
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from extended import modes_news as NW
from extended import modes_steps as S
from extended import modes_terms as M
from extended.firm_terms import UnverifiedTerm, record_value

ROOT = Path(__file__).resolve().parent.parent
#: the build's files (the adapters and the reading's code) the literal check reads
ADAPTERS = ("extended/modes_terms.py", "extended/modes_rules.py", "extended/modes_engine.py", "extended/modes_join.py",
            "extended/modes_news.py", "extended/modes_reading.py", "extended/modes_plans.py",
            "extended/modes_oracles.py", "extended/modes_steps.py", "scripts/modes_rules.py", "scripts/modes_coin.py",
            "identity/modes_coin_identity.py")                        # N-12: every build file with code
BUILD_FILES = ADAPTERS + ("extended/modes_oracles.py", "extended/modes_steps.py", "scripts/modes_rules.py",
                          "scripts/modes_coin.py", "scripts/modes_part_f.py", "scripts/modes_reading.py",
                          "scripts/modes_beside.py", "scripts/modes_gate.py", "identity/modes_coin_identity.py",
                          "identity/modes_identity.py")
#: the assignments the literal check skips: the declared tables and the code's pins
TABLES = {"DECLARED", "NOT_RULE_VALUES", "MATH", "LAYOUT", "NUMBER_WORDS", "STEPS", "RECORDED_BY", "NOT_BUILT", "REFERENCE_PROFILE",
          "SEEDS", "RESERVED_SEEDS", "TIMING_SEED", "VENDORED_SHA256", "DECLARATION_SHA256", "A19",
          "U_RULES", "RECORD_KEYS", "STAGE2_KEYS", "TWO_ENDED", "MODE_CORNERS"}
#: numbers that are structure, not rule values: none, one, a tolerance
STRUCTURAL = {0, 1, -1}
_PREFIX = 2026 * 1000 + 238


def test_seeds_only_where_section_15_declares_them() -> None:
    assert M.SEEDS == {r: _PREFIX * 10 + i for i, r in enumerate(("coin_eval", "coin_funded", "coin_peak", "build_toys",
                                                                   "coin_identity", "honesty"))}
    assert M.RESERVED_SEEDS == tuple(_PREFIX * 10 + i for i in range(6, 10))
    pat = re.compile(rf"\b{_PREFIX}\d\b")
    for rel in BUILD_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        hits = pat.findall(text)
        if rel == "extended/modes_terms.py":
            assert sorted(hits) == sorted(str(s) for s in (*M.SEEDS.values(), *M.RESERVED_SEEDS)), hits
        else:
            assert not hits, (rel, hits)
    for p in (ROOT / "tests").glob("test_rd05_*.py"):
        assert not pat.findall(p.read_text(encoding="utf-8")), p.name


def _rule_values() -> set[float]:
    vals: set[float] = set()

    def add(x) -> None:
        if isinstance(x, bool) or x is None:
            return
        if isinstance(x, (int, float)):
            vals.add(float(x))
        elif isinstance(x, (tuple, list)):
            for y in x:
                add(y)
        elif dataclasses.is_dataclass(x):
            for f in dataclasses.fields(x):
                add(getattr(x, f.name))

    for m in M.MODE_CORNERS:
        add(M.mode_corner_terms(m))
    for k in M.A19:
        add(M.quote_figure(k))
    add(M.round_turn("topstep"))
    add(M.round_turn("mffu"))
    return {v for v in vals if v not in STRUCTURAL}


def _numbers(rel: str) -> list[tuple[int, float]]:
    tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
    skip: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id in TABLES for t in targets):
                for sub in ast.walk(node):
                    skip.add(id(sub))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("_mc", "Declared",
                                                                                           "QuoteFigure"):
            for sub in ast.walk(node):
                skip.add(id(sub))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "group":
            for sub in node.args:                                     # a regex group's index
                skip.add(id(sub))
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if name in ("step_problems", "main", "add_argument"):     # a step's number; a command line's default
                for sub in [*node.args, *(k.value for k in node.keywords)]:
                    for x in ast.walk(sub):
                        skip.add(id(x))
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == "step":
            for sub in ast.walk(node):                                # a step's number
                skip.add(id(sub))
        if isinstance(node, ast.Subscript):                           # an index, never a rule value
            for sub in ast.walk(node.slice):
                skip.add(id(sub))
        if isinstance(node, ast.Return) and isinstance(node.value, (ast.Constant, ast.IfExp)):
            for sub in ast.walk(node.value):                          # an exit code
                skip.add(id(sub))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            skip.add(id(node.right))                                  # an exponent
        if isinstance(node, ast.FunctionDef) and node.name in ("simulate_combine", "simulate_xfa"):
            for sub in ast.walk(node):                                # the vendored copies' own text (A-0)
                skip.add(id(sub))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if id(node) not in skip:
                out.append((node.lineno, float(node.value)))
    return out


@pytest.mark.parametrize("rel", ADAPTERS)
def test_no_rule_value_typed_in_the_adapters(rel: str) -> None:
    rules = _rule_values()
    hits = [(ln, v) for ln, v in _numbers(rel) if v in rules]
    assert not hits, f"{rel}: numbers equal to a rule value outside the declared tables: {hits}"


def test_the_literal_check_finds_a_planted_value(tmp_path: Path) -> None:
    rules = _rule_values()
    planted = max(rules)
    src = f"def f(x):\n    return x * {planted!r}\n"
    p = ROOT / "tests" / "_rd05_planted_tmp.py"
    try:
        p.write_text(src, encoding="utf-8")
        assert any(v in rules for _, v in _numbers("tests/_rd05_planted_tmp.py"))
    finally:
        p.unlink(missing_ok=True)


def _toy_log(t0: datetime) -> list[dict]:
    return [{"account": 0, "entry": t0, "exit": t0 + timedelta(minutes=30), "live": t0, "full_allowance": False},
            {"account": 1, "entry": t0 + timedelta(minutes=35), "exit": t0 + timedelta(minutes=50),
             "live": t0 + timedelta(minutes=35), "full_allowance": True}]


def test_tier1_counts_zero_and_firing() -> None:
    rel = datetime(2026, 1, 7, 13, 0)
    w = [NW.window_at(rel)]
    t0 = rel - timedelta(hours=3)
    assert set(NW.tier1_counts(_toy_log(t0), w, {0, 1}).values()) == {0}
    over = _toy_log(t0)
    over[1]["entry"] = t0 + timedelta(minutes=10)
    assert NW.tier1_counts(over, w, {0, 1})["overlapping_positions"] == 1
    inside = _toy_log(rel - timedelta(minutes=1))
    c = NW.tier1_counts(inside, w, {0, 1})
    assert c["entry_inside_window"] >= 1
    held = [{"account": 0, "entry": rel - timedelta(minutes=20), "exit": rel + timedelta(minutes=20),
             "live": rel - timedelta(minutes=20), "full_allowance": True}]
    c = NW.tier1_counts(held, w, {0})
    assert c["held_through_window_start"] == 1 and c["full_size_into_news"] == 1
    assert set(NW.tier1_counts(held, w, set()).values()) == {0}       # an account no rule reaches


def test_loaders_refuse_a_non_verified_value() -> None:
    for k, st in M.RECORD_KEYS.items():
        if st != "verified":
            with pytest.raises(UnverifiedTerm):
                record_value(k)
            break


def test_step_gates_refuse() -> None:
    for step in range(6):
        probs = S.step_problems(step)
        assert probs, step                                               # nothing of RD-05 is run from the worktree
        if step in S.NOT_BUILT:
            assert any(p.startswith("NOT BUILT") for p in probs)
    assert not S.declaration_problems() and not S.record_problems() and not S.terms_problems()
    assert any("records step 0" in p for p in S.step_problems(1))
