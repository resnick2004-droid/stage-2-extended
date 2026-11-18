"""Q-119: RD-03's build (`prereg/RD-03_contract_levers.md` 14.1-14.3) -- the re-composed path `extended/levers_path.py`
(A-1), its keywords on the replay and the gate (`extended/user_beside.py`, `extended/gate.py`, `extended/campaign.py`,
lines marked Q-119; A-2, A-3), the prices (A-4), the rules in code (`extended/levers_terms.py`,
`extended/levers_readings.py`), the reading (`extended/cl_reading.py`, A-6) -- held to the declared tests on synthetic
inputs only:

* T-1, T-2, T-3, T-4, T-5, T-6, T-7, T-10, T-13, T-14 and T-15 run in `tests/cl_synthetic.py`, one section a process
  (the vendored engine on that process's `sys.path`), each a list of problems that must be empty;
* T-9: section 12's seeds appear in none of the build's files but the declared uses (T-0 scans the repository with
  `DECLARED_USES`), and 14.2's literal check -- no 599, 95, 49, 149 or 30, and no 2 or 5 beside a reactivation or a
  cap, among the adapters' own numbers (the copied vendored lines aside; the readings table is the one home of 4.3's
  readings, each citing its line);
* T-11: `identity/cl_identity.py` runs the reference only (`tests/cl_identity_check.py`);
* T-8 (slow, heavy): 9.1 items 1 and 2 at 4 paths and 4 starts through `identity/cl_identity.py`, the lead's, under the
  run lock, with the row that registers the identity (`S2X_CL_IDENTITY_ROW`).
"""
from __future__ import annotations

import ast
import functools
import io
import json
import os
import re
import subprocess
import sys
import tokenize
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SYN = ROOT / "tests" / "cl_synthetic.py"
ENV = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
#: the adapters 14.2's literal check reads: their own code, and the lines marked Q-119 in the files they share
OWN_ADAPTERS = ("extended/levers_terms.py", "extended/cl_reading.py", "extended/levers_fit.py")
MARKED_ADAPTERS = ("extended/levers_path.py", "extended/user_beside.py", "extended/gate.py", "extended/campaign.py")
MARKER = "Q-119"
#: 14.2: the rule values never typed in the adapters
RULE_LITERALS = {599, 95, 49, 149, 30}
CONTEXT_LITERALS = {2: re.compile(r"reactivat", re.I), 5: re.compile(r"\bcap\b|max_active|five", re.I)}


@functools.lru_cache(maxsize=None)
def _run(section: str, timeout: int = 1800) -> dict:
    r = subprocess.run([sys.executable, str(SYN), str(ROOT), section], cwd=ROOT, capture_output=True, text=True,
                       timeout=timeout, env=ENV)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, f"{section} did not run:\n{r.stdout[-2000:]}\n{r.stderr[-3000:]}"
    out = json.loads(lines[-1])
    for note in out.get("notes", []):
        print(note)
    return out


#: E-169 item 0: T-3's section (about 17 minutes: three toy jobs of five cells) runs in /validate's slow tier, not the
#: fast tier the commit hook runs
SLOW_SECTIONS = {"t3", "t3b"}


@pytest.mark.parametrize("section", [pytest.param(s, marks=pytest.mark.slow) if s in SLOW_SECTIONS else s
                                     for s in ("t1", "t2", "t3", "t3trip", "t3b", "t4", "t5", "t6", "t7", "t10",
                                               "t13", "t14", "t15", "t16", "t17")])
def test_section_holds(section):
    out = _run(section)
    assert out["n_problems"] == 0, "\n".join(out["problems"])


@pytest.mark.slow
def test_t3_catches_the_planted_leak_at_every_horizon():
    """R1 (cycle 3): T-3's planted leaks caught at every h of section 5's table, 21 included, each h reached by the
    plant -- the purge leak by a moved row under one of the two plants, cycle 1's leak by a moved row or the reading's
    refusal -- read off the section's own notes, so a T-3 that stopped checking a horizon fails here too."""
    out = _run("t3")
    for h in (21, 63, 126, 189, 252):
        assert any(n.startswith(f"T3_REACH_{h}=") and int(n.split("=")[1]) > 0 for n in out["notes"]), h
        caught = [n for n in out["notes"] if n.startswith(f"T3_LEAK_{h}_CAUGHT_BY=")]
        assert caught and caught[0].split("=")[1] not in ("none", "refused"), h
        full = [n for n in out["notes"] if n.startswith(f"T3_LEAK_FULL_{h}_CAUGHT_BY=")]
        assert full and full[0].split("=")[1] != "none", h


def test_starts_is_the_synthetic_window_measurements_only(tmp_path):
    """The window measurement's `--starts` (every n-th start): refused outside `--synthetic`, in step 3, and below 1
    -- each before anything is read or run (exit 2)."""
    script = ROOT / "scripts" / "cl_reading.py"
    for args in (["--step", "4", "--starts", "5"], ["--step", "5", "--starts", "5", "--after", "E-001"],
                 ["--step", "3", "--synthetic", "--results-dir", str(tmp_path), "--starts", "5"],
                 ["--step", "4", "--synthetic", "--results-dir", str(tmp_path), "--starts", "0"]):
        r = subprocess.run([sys.executable, str(script), *args], cwd=ROOT, capture_output=True, text=True, timeout=300,
                           env=ENV)
        assert r.returncode == 2 and "REFUSED (RD-03): --starts" in r.stdout, (args, r.stdout[-800:], r.stderr[-800:])
    assert not any(tmp_path.iterdir())


def test_the_tripwire_reads_its_horizon():
    """m4: the fast tripwire (section t3trip) checked its one horizon and caught the purge leak there under its plant."""
    out = _run("t3trip")
    assert any(n.startswith("T3TRIP_ROWS_PURGE_") for n in out["notes"]), out["notes"]
    caught = [n for n in out["notes"] if n.startswith("T3TRIP_LEAK_") and "_CAUGHT_BY=" in n]
    assert len(caught) == 1 and caught[0].split("=")[1] not in ("none", ""), out["notes"]


def test_stage0_stopped_is_refused_beside_a_stage0_file_or_without_its_row(tmp_path):
    """m3 through the runner (synthetic step 3, before anything runs): `--stage0-stopped` without `--stage0-row`, and
    with a stage-0 file in the results folder, each refused (exit 3) with nothing written."""
    script = ROOT / "scripts" / "cl_reading.py"
    base = ["--step", "3", "--synthetic", "--results-dir", str(tmp_path), "--days", "20", "--stage0-stopped"]
    r = subprocess.run([sys.executable, str(script), *base], cwd=ROOT, capture_output=True, text=True, timeout=600,
                       env=ENV)
    assert r.returncode == 3 and "needs --stage0-row" in r.stdout, (r.stdout[-800:], r.stderr[-800:])
    (tmp_path / "cl_fit_synthetic.csv").write_text("section,design,rule,line", encoding="utf-8")
    r = subprocess.run([sys.executable, str(script), *base, "--stage0-row", "E-172"], cwd=ROOT, capture_output=True,
                       text=True, timeout=600, env=ENV)
    assert r.returncode == 3 and "on the tree" in r.stdout, (r.stdout[-800:], r.stderr[-800:])
    assert sorted(p.name for p in tmp_path.iterdir()) == ["cl_fit_synthetic.csv"]


def test_the_real_run_excuses_no_guard_entry():
    """m-a: the runner passes the guard excuse only to the synthetic run, and every function's default refuses it
    (t17 holds the defaults by `inspect.signature`)."""
    text = (ROOT / "scripts" / "cl_reading.py").read_text(encoding="utf-8")
    assert text.count("excuse_guard=bool(a.synthetic)") == 2
    assert "excuse_guard=True" not in text


# ------------------------------------------------------------------------------------------------ T-9


def _numbers(path: Path, only_marked: bool) -> list[tuple[int, float, str]]:
    """Every numeric literal of a file's code (comments and docstrings aside), with its line; in a shared file only
    the lines marked Q-119; in levers_path.py the module's own code and the copies' marked lines."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tree = ast.parse(text)
    doc_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value,
                                                                                                    str):
                doc_lines.update(range(first.lineno, first.end_lineno + 1))
    copied: set[int] = set()
    if path.name == "levers_path.py":
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in ("simulate_lockstep_path", "_one_path",
                                                                    "_path_chunk", "_run_paths"):
                copied.update(range(node.lineno, node.end_lineno + 1))
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type != tokenize.NUMBER:
            continue
        ln = tok.start[0]
        line = lines[ln - 1]
        if ln in doc_lines:
            continue
        marked = re.search(r"#\s*" + MARKER + r"\b", line) is not None
        if only_marked and not marked:
            continue
        if ln in copied and not marked:
            continue
        try:
            v = float(tok.string.replace("_", ""))
        except ValueError:
            continue
        out.append((ln, v, line))
    return out


def literal_problems(paths: dict[str, bool]) -> list[str]:
    bad = []
    for rel, only_marked in paths.items():
        p = ROOT / rel
        if not p.is_file():
            continue
        for ln, v, code in _numbers(p, only_marked):
            if v in RULE_LITERALS:
                bad.append(f"{rel}:{ln}: the rule value {v:g} typed")
            for k, pat in CONTEXT_LITERALS.items():
                if v == k and pat.search(code):
                    bad.append(f"{rel}:{ln}: {v:g} typed beside {pat.pattern}")
    return bad


def test_no_rule_value_is_typed_in_the_adapters():
    paths = {**{r: False for r in OWN_ADAPTERS}, **{r: True for r in MARKED_ADAPTERS}}
    paths["extended/levers_path.py"] = False
    bad = literal_problems(paths)
    assert not bad, "\n".join(bad)


def test_the_literal_check_finds_a_typed_value(tmp_path, monkeypatch):
    f = tmp_path / "x.py"
    f.write_text('"""doc 599"""\nFEE = 599.0\nLIMIT = 2  # reactivations\n', encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    bad = literal_problems({"x.py": False})
    assert len(bad) == 2 and "599" in bad[0] and "reactivat" in bad[1]


def test_the_readings_table_cites_section_4_3():
    sys.path.insert(0, str(ROOT))
    from extended import levers_readings as LR

    assert {r.cites for r in LR.READINGS} <= {f"U-{i}" for i in range(1, 9)}
    assert {r.cites for r in LR.READINGS} == {f"U-{i}" for i in range(1, 9)}, "every reading of 4.3 in the table"
    body = (ROOT / "prereg" / "RD-03_contract_levers.md")
    body = body if body.is_file() else ROOT / "prereg" / "DRAFT_RD-03_contract_levers.md"
    s43 = body.read_text(encoding="utf-8").split("### 4.3", 1)[1].split("### 4.4", 1)[0]
    for r in LR.READINGS:
        assert f"**{r.cites}." in s43, r.cites


def test_the_seed_uses_are_t0s():
    import importlib.util

    spec = importlib.util.spec_from_file_location("t0", ROOT / "tests" / "test_rd03_draft.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert "tests/cl_synthetic.py" in m.DECLARED_USES
    for rel in ("extended/levers_path.py", "extended/levers_terms.py", "extended/levers_readings.py",
                "extended/cl_reading.py", "identity/cl_identity.py", "tests/test_cl_build.py"):
        p = ROOT / rel
        if p.is_file():
            assert not re.search(r"\b2026224\d\b", p.read_text(encoding="utf-8")), rel


# ------------------------------------------------------------------------------------------------ T-11


def _identity_check() -> dict:
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "cl_identity_check.py"), str(ROOT)], cwd=ROOT,
                       capture_output=True, text=True, timeout=600, env=ENV)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, r.stdout[-2000:] + r.stderr[-3000:]
    return json.loads(lines[-1])


def test_the_identity_script_runs_the_reference_only():
    out = _identity_check()
    assert not out["problems"], "\n".join(out["problems"])


@pytest.mark.xfail(strict=True, reason="A-5 (stage 0: extended/levers_fit.py, scripts/cl_fit.py, "
                                       "identity/cl_fit_identity.py) is not built in Q-119's hand-back; strict, so the "
                                       "mark must go when it is")
def test_the_stage0_identity_script_runs_the_reference_only():
    out = _identity_check()
    assert not out["fit_problems"], "\n".join(out["fit_problems"])


# ------------------------------------------------------------------------------------------------ T-8


@pytest.mark.slow
@pytest.mark.heavy
def test_t8_the_identity_at_four_paths_and_starts():
    row = os.environ.get("S2X_CL_IDENTITY_ROW")
    if not row:
        pytest.skip("T-8 needs the row registering cl_identity (S2X_CL_IDENTITY_ROW): the lead's, under the lock")
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "cl_identity.py"), "--paths", "4", "--u1-starts", "4",
                        "--row", row], cwd=ROOT, capture_output=True, text=True, timeout=7200, env=ENV)
    assert "EXIT 0" in r.stdout, r.stdout[-3000:] + r.stderr[-3000:]


# ------------------------------------------------------------------------------------------------ m1


@pytest.mark.slow
def test_the_pipeline_runs_steps_3_to_5_on_toys(tmp_path):
    """m1: steps 3, 4 and 5 `--synthetic` end to end (`tests/cl_run_check.py`), asserting M1 to M4 on the files. Slow
    (E-169 item 0: about 11 minutes): /validate's slow tier, not the commit hook's fast tier."""
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "cl_run_check.py"), str(ROOT), str(tmp_path)], cwd=ROOT,
                       capture_output=True, text=True, timeout=3600, env=ENV)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, r.stdout[-3000:] + r.stderr[-3000:]
    out = json.loads(lines[-1])
    assert not out["problems"], "\n".join(out["problems"])
