"""Wave 1.2 (the restart plan, `docs/plans/RESTART_PLAN_journey_objective.md` section 3): `docs/MEASURES.md` held to
the code.

* the index (section 8, between the `measures-index` markers) has the plan's 39 items, numbered 1 .. 39: 37 measures,
  each with a status `exists`, `partial` or `to build`, and the baseline set, (35) and (36), each a `comparator` (the
  red team's m-3; the amendments' "37 measures plus the baseline set");
* every measure has its section `### (n) name`, whose name and `**Status:**` line are the index's; a `to build` entry
  says so in its section, a `partial` one names what is to build (`**To build:**`);
* every reference of a measure marked `exists` or `partial` -- and every ingredient a `to build` entry names -- is
  defined where it says: `path::Name` a top-level function, class or assignment (or `Class.method`) of that file, found
  by parsing it (nothing is imported: no engine, no vendored module on the path); `path::CONST[item]` an element of the
  literal constant (for a tuple of calls, their first arguments); `path::"text"` text found in the file;
* an `exists` or `partial` measure names at least one function or constant;
* every entry has its per-unit and never-blank line (the red team's m-6);
* every code line section 6 lists (changed in Wave 3.1, or still to change) holds the quoted text at or just after
  the line given, and the text each changed line replaced is gone;
* no seed literal appears in the document;
* the two measures the operator dropped are listed as dropped, and P is defined as not a p-value.

Reads no data: only this repository's and the vendored tree's source files and the document.
"""
from __future__ import annotations

import ast
import re
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "MEASURES.md"
N_ITEMS = 39
COMPARATORS = (35, 36)
N_MEASURES = N_ITEMS - len(COMPARATORS)
MEASURE_STATUSES = ("exists", "partial", "to build")
STATUSES = (*MEASURE_STATUSES, "comparator")
START, END = "<!-- measures-index:start -->", "<!-- measures-index:end -->"
REF = re.compile(r"`([^`]+)`")


# ------------------------------------------------------------------------------------------------ the checker


@lru_cache(maxsize=None)
def _source(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise AssertionError(f"{path}: no such file")
    return p.read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def _tree(path: str) -> ast.Module:
    return ast.parse(_source(path), filename=path)


def _assigned(node: ast.stmt) -> list[tuple[str, ast.expr | None]]:
    if isinstance(node, ast.Assign):
        return [(t.id, node.value) for t in node.targets if isinstance(t, ast.Name)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [(node.target.id, node.value)]
    return []


def _top(path: str) -> dict[str, ast.AST]:
    out: dict[str, ast.AST] = {}
    for node in _tree(path).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = node
        for name, value in _assigned(node):
            out[name] = value if value is not None else node
    return out


def _elements(value: ast.AST) -> list:
    """A literal constant's elements; for a tuple or list of calls, each call's first argument (a literal)."""
    try:
        v = ast.literal_eval(value)
        return list(v)
    except (ValueError, TypeError, SyntaxError):
        pass
    if isinstance(value, (ast.Tuple, ast.List)):
        out = []
        for e in value.elts:
            if isinstance(e, ast.Call) and e.args:
                out.append(ast.literal_eval(e.args[0]))
            else:
                raise AssertionError("not a literal constant nor a tuple of calls")
        return out
    raise AssertionError("not a literal constant nor a tuple of calls")


def _item(text: str):
    try:
        return int(text)
    except ValueError:
        return text


def check_ref(ref: str) -> None:
    """Raises AssertionError when the reference does not resolve (the module docstring's three forms)."""
    if "::" not in ref:
        raise AssertionError(f"{ref!r}: not `path::name`")
    path, what = ref.split("::", 1)
    if what.startswith('"'):
        if not (what.endswith('"') and len(what) > 2):
            raise AssertionError(f"{ref!r}: an unterminated text reference")
        if what[1:-1] not in _source(path):
            raise AssertionError(f"{ref!r}: the text is not in {path}")
        return
    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\[([^\]]+)\]", what)
    if m:
        name, item = m.group(1), _item(m.group(2))
        top = _top(path)
        if name not in top:
            raise AssertionError(f"{ref!r}: {name} is not defined at the top of {path}")
        try:
            elements = _elements(top[name])
        except AssertionError as e:
            raise AssertionError(f"{ref!r}: {e}") from None
        if item not in elements:
            raise AssertionError(f"{ref!r}: {item!r} is not an element of {name}")
        return
    parts = what.split(".")
    if not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", p) for p in parts) or len(parts) > 2:
        raise AssertionError(f"{ref!r}: not a name, `Class.method`, `CONST[item]` or text")
    top = _top(path)
    if parts[0] not in top:
        raise AssertionError(f"{ref!r}: {parts[0]} is not defined at the top of {path}")
    if len(parts) == 2:
        cls = top[parts[0]]
        if not isinstance(cls, ast.ClassDef) or not any(
                isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == parts[1] for n in cls.body):
            raise AssertionError(f"{ref!r}: {parts[1]} is not a method of {parts[0]}")


# ------------------------------------------------------------------------------------------------ the document


@lru_cache(maxsize=None)
def _doc() -> str:
    return DOC.read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def index() -> dict[int, dict]:
    text = _doc()
    assert text.count(START) == 1 and text.count(END) == 1, "the index markers must appear once each"
    body = text.split(START, 1)[1].split(END, 1)[0]
    rows = [ln for ln in body.strip().splitlines() if ln.startswith("|")]
    assert rows[0].replace(" ", "") == "|#|measure|status|code|names|", rows[0]
    out: dict[int, dict] = {}
    for ln in rows[2:]:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        assert len(cells) == 5, f"an index row with {len(cells)} cells: {ln}"
        n = int(cells[0])
        assert n not in out, f"measure {n} twice in the index"
        out[n] = {"name": cells[1], "status": cells[2], "code": REF.findall(cells[3]), "names": REF.findall(cells[4])}
    return out


@lru_cache(maxsize=None)
def sections() -> dict[int, dict]:
    text = _doc().split(START, 1)[0]
    heads = list(re.finditer(r"^### \((\d+)\) (.+)$", text, flags=re.M))
    out: dict[int, dict] = {}
    for i, h in enumerate(heads):
        n = int(h.group(1))
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        end = min(end, text.find("\n## ", h.end()) if text.find("\n## ", h.end()) >= 0 else end)
        body = text[h.end():end]
        st = re.search(r"^- \*\*Status:\*\* (exists|partial|to build|comparator)\b", body, flags=re.M)
        assert n not in out, f"measure {n} has two sections"
        out[n] = {"name": h.group(2).strip(), "status": st.group(1) if st else None, "body": body}
    return out


# ------------------------------------------------------------------------------------------------ the tests


def test_the_checker_refuses_what_does_not_exist():
    """The checker itself: a real name, constant element and text pass; a made-up one of each fails."""
    check_ref("extended/user_measures.py::p_by_month")
    check_ref("extended/user_readings.py::START_COLS[first_pass]")
    check_ref("vendor/stage2/propedge/research/u_select.py::MEASURES[S1]")
    check_ref('extended/user_measures.py::"share_months_positive"')
    for bad in ("extended/user_measures.py::no_such_function", "extended/user_readings.py::START_COLS[no_such_col]",
                "vendor/stage2/propedge/research/u_select.py::MEASURES[S9]",
                'extended/user_measures.py::"no such text anywhere"', "extended/no_such_module.py::f",
                "extended/user_measures.py::cvar.method", "no separator"):
        with pytest.raises(AssertionError):
            check_ref(bad)


def test_the_index_has_37_measures_and_the_baseline_set():
    idx = index()
    assert sorted(idx) == list(range(1, N_ITEMS + 1))
    for n, r in idx.items():
        if n in COMPARATORS:
            assert r["status"] == "comparator", f"item {n} is a comparator, not {r['status']!r}"
        else:
            assert r["status"] in MEASURE_STATUSES, f"measure {n}: status {r['status']!r}"
    assert sum(r["status"] != "comparator" for r in idx.values()) == N_MEASURES
    assert "37 measures plus the baseline set" in _doc().splitlines()[0]


def test_every_measure_has_its_section_with_the_index_status():
    idx, sec = index(), sections()
    assert sorted(sec) == list(range(1, N_ITEMS + 1))
    for n in idx:
        assert sec[n]["name"] == idx[n]["name"], f"measure {n}: section {sec[n]['name']!r}, index {idx[n]['name']!r}"
        assert sec[n]["status"] == idx[n]["status"], f"measure {n}: section {sec[n]['status']}, index {idx[n]['status']}"
        for field in ("**Definition", "**Summary and unit:**", "**Per unit; never blank:**", "**Where:**",
                      "**Parameters:**"):
            assert field in sec[n]["body"], f"measure {n}: no {field}"


@pytest.mark.parametrize("n", range(1, N_ITEMS + 1))
def test_every_named_function_or_column_exists(n):
    r = index()[n]
    if r["status"] in ("exists", "partial"):
        assert any("[" not in ref.split("::", 1)[1] and not ref.split("::", 1)[1].startswith('"') for ref in r["code"]), \
            f"measure {n} is marked {r['status']} but names no function or constant"
    for ref in r["code"] + r["names"]:
        check_ref(ref)


def test_to_build_and_partial_entries_are_marked():
    sec = sections()
    for n, r in index().items():
        body = sec[n]["body"]
        if r["status"] == "to build":
            assert re.search(r"\*\*Status:\*\* to build", body), f"measure {n}"
            assert "to build" in body.lower()
        if r["status"] == "partial":
            assert "**To build:**" in body, f"measure {n} is partial but names nothing to build"


def test_the_dropped_measures_and_p():
    text = _doc()
    drop = text.split("## 5. Dropped by the operator", 1)
    assert len(drop) == 2, "no dropped section"
    part = drop[1].split("\n## ", 1)[0]
    for name in ("Firm-rule exposure", "Rule-change sensitivity"):
        line = next((ln for ln in part.splitlines() if name in ln), "")
        assert "dropped" in line, f"{name} is not listed as dropped"
    p = text.split("## 2. P (not a p-value)", 1)
    assert len(p) == 2 and "not a p-value" in p[1].split("\n## ", 1)[0]


#: Wave 3.1: the code lines section 6 listed "to change" and the text each held before; each is gone from its file
REPLACED = (("extended/user_beside.py", r"^\s*L = min\(U\.HORIZON, n - s\)$"),
            ("extended/user_readings.py", r"^BLOCKS = \(\"all\", \"judged\"\)"),
            ("extended/user_readings.py", r"abs\(card - mine\) <= 1e-12"),
            ("extended/opening_journey.py", r"abs\(card - mine\) <= 1e-12"),
            ("extended/user_measures.py", r"ahead = x\[ok\] > 0\b"),
            ("extended/user_measures.py", r"c = \(x > 0\)\.sum\(axis=1\)"))


def test_the_code_to_change_is_where_it_says():
    """Section 6: each `path:line` or `path:first-last` with its quoted text -- the file exists and the text is on one
    of the lines from the first to six after the last. Since Wave 3.1 the section lists the lines changed (each named
    change from the old to-change list, at its new line) and the one still to change; the text each changed line
    replaced is gone from its file (`REPLACED`)."""
    part = _doc().split("## 6. Code changed in Wave 3.1, and code still to change", 1)
    assert len(part) == 2, "no section 6"
    body = part[1].split("\n## ", 1)[0]
    refs = re.findall(r"^- `([^`:]+):(\d+)(?:-(\d+))?` \(`([^`]+)`\)", body, flags=re.M)
    assert len(refs) >= 2, "section 6 lists no code line"
    for path, first, last, text in refs:
        lines = _source(path).splitlines()
        a, b = int(first), int(last or first)
        assert text in "\n".join(lines[a - 1:b + 6]), f"{path}:{first}: {text!r} is not there"
    changed, still = body.split("**Still to change.**", 1)
    for want in ("extended/user_beside.py:776", "extended/user_beside.py:796", "extended/user_readings.py:319",
                 "extended/journey_readings.py:108", "extended/user_readings.py:206", "extended/user_readings.py:72",
                 "extended/user_readings.py:485", "extended/user_measures.py:77", "extended/user_measures.py:96",
                 "extended/user_measures.py:219"):
        assert f"`{want}`" in changed, f"{want} is not listed as changed"
    assert "`extended/user_beside.py:386`" in still, "the flip refusal is not listed still to change"
    for want in ("extended/firm_reading.py:258", "extended/openings.py:519", "extended/opening_wait.py:519"):
        assert f"`{want}`" in still, f"{want} is not listed to change"
    assert "`extended/cl_reading.py:" in still, "cl_reading.py's run length is not listed"
    for path, pattern in REPLACED:
        assert not re.search(pattern, _source(path), flags=re.M), f"{path}: the replaced text {pattern!r} is back"


def test_the_strict_rule_for_censored_percentiles():
    """N-1 (the second read): section 1.3 states the strict rule -- a dollar percentile is exact only if every
    censored lower bound lies strictly above it, else "at least" -- and the rule it replaced is gone; (6) reads a
    bankroll limit through (24)'s three states, never on its own percentile."""
    text = _doc()
    part = text.split("### 1.3 Summaries, censoring and blanks", 1)
    assert len(part) == 2, "no section 1.3"
    s13 = " ".join(part[1].split("\n### ", 1)[0].split())
    assert ("A dollar percentile is exact only if every censored unit's lower bound lies strictly above it. "
            "Otherwise it is reported as \"at least\" that value.") in s13
    assert "A percentile that falls on a censored unit is reported as" not in " ".join(text.split())
    s6 = " ".join(sections()[6]["body"].split())
    assert "every censored unit's lower bound lies strictly above it" in s6
    assert "never read on these percentiles" in s6 and "through (24)'s three states" in s6
    assert "A limit on it reads its censoring" not in s6


def test_no_seed_literal_in_the_document():
    assert not re.search(r"(?<![\d-])20\d{6}(?![\d-])", _doc()), "a seed-like literal in docs/MEASURES.md"
