"""Q-147: the per-edit test hook (`scripts/hooks/run_tests.py`) runs only the edited file's own tests and the two
foundation checks -- never the whole fast tier, which the pre-commit hook keeps.

After a `.py` edit in the main tree the hook runs, under the fast tier's marker selection:

* the edited file's matching `tests/test_<stem>.py`, when the tree has one; an edited file that is itself a test file
  under `tests/` (`test_*.py`) is run as it is;
* `tests/test_vendor_integrity.py` and `tests/test_declarations_fixed.py` (E-002, E-003), whatever was edited.

E-027's worktree skip and the `results/.last_test_run.json` record are unchanged. The mapping is checked in process on
synthetic paths in a temporary tree; the whole hook end to end on a fake main tree in a temporary folder (a `.git`
directory and a `pyproject.toml` naming the project), whose tiny tests run in a child pytest -- never on this
repository, where calling the hook from inside pytest would recurse.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "scripts" / "hooks"
FIXED = ["tests/test_vendor_integrity.py", "tests/test_declarations_fixed.py"]


def _hook():
    spec = importlib.util.spec_from_file_location("s2x_run_tests_hook", HOOKS / "run_tests.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _hook()


def _touch(p: Path, text: str = "") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A synthetic tree: the two fixed tests, one module with a matching test, one without, a test helper."""
    t = tmp_path / "repo"
    for rel in FIXED:
        _touch(t / rel)
    _touch(t / "extended" / "walker.py")
    _touch(t / "tests" / "test_walker.py")
    _touch(t / "extended" / "lonely.py")
    _touch(t / "tests" / "journey_synth.py")
    _touch(t / "scripts" / "status.py")
    _touch(t / "tests" / "test_status.py")
    return t


# ------------------------------------------------------------------ the mapping


def test_a_file_with_a_matching_test_runs_it_and_the_two_fixed(tree):
    assert H.tests_for(tree / "extended" / "walker.py", tree) == ["tests/test_walker.py", *FIXED]
    assert H.tests_for(tree / "scripts" / "status.py", tree) == ["tests/test_status.py", *FIXED]


def test_a_file_without_a_matching_test_runs_only_the_two_fixed(tree):
    assert H.tests_for(tree / "extended" / "lonely.py", tree) == FIXED
    assert H.tests_for(tree / "extended" / "not_yet_written.py", tree) == FIXED   # a file about to be created


def test_a_test_file_under_tests_runs_itself(tree):
    assert H.tests_for(tree / "tests" / "test_walker.py", tree) == ["tests/test_walker.py", *FIXED]
    # a test file not yet matched by any module, and not named after one
    _touch(tree / "tests" / "test_family_stats.py")
    assert H.tests_for(tree / "tests" / "test_family_stats.py", tree) == ["tests/test_family_stats.py", *FIXED]


def test_a_test_helper_under_tests_that_is_not_a_test_runs_only_the_fixed(tree):
    assert H.tests_for(tree / "tests" / "journey_synth.py", tree) == FIXED
    assert H.tests_for(tree / "conftest.py", tree) == FIXED


def test_a_fixed_test_edited_is_not_run_twice(tree):
    assert H.tests_for(tree / "tests" / "test_vendor_integrity.py", tree) == FIXED
    # the edited file's own test comes first, then the rest of the fixed pair; each once
    assert H.tests_for(tree / "tests" / "test_declarations_fixed.py", tree) == [FIXED[1], FIXED[0]]


def test_a_fixed_test_missing_from_the_tree_is_left_out(tree):
    (tree / "tests" / "test_declarations_fixed.py").unlink()
    assert H.tests_for(tree / "extended" / "walker.py", tree) == ["tests/test_walker.py", FIXED[0]]


def test_a_file_outside_the_tree_runs_only_the_fixed(tree, tmp_path):
    assert H.tests_for(tmp_path / "elsewhere" / "walker.py", tree) == FIXED


def test_the_mapping_is_case_blind_on_windows(tree):
    if os.name != "nt":
        pytest.skip("case-insensitive paths are a Windows matter")
    upper = Path(str(tree).upper()) / "EXTENDED" / "walker.py"
    assert H.tests_for(upper, tree) == ["tests/test_walker.py", *FIXED]


def test_the_fixed_pair_and_the_tier_are_the_declared_ones():
    assert list(H.FIXED_TESTS) == FIXED
    assert H.FAST_TIER == "not slow and not heavy"


def test_the_pre_commit_hook_keeps_the_whole_fast_tier():
    """The commit-time tier is unchanged: pytest over the whole suite (no file argument) at the fast selection."""
    text = (ROOT / "scripts" / "pre-commit").read_text(encoding="utf-8")
    assert '"$PYTHON" -m pytest -o addopts= -q -m "$FAST_TIER"\n' in text


# ------------------------------------------------------------------ the hook end to end, on a fake main tree

PYPROJECT = """[project]
name = "stage2-extended"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
markers = ["slow: x", "heavy: y"]
"""


@pytest.fixture
def fake_main(tmp_path: Path) -> Path:
    t = tmp_path / "main"
    (t / ".git").mkdir(parents=True)                       # a directory: the main repository, not a worktree
    _touch(t / "pyproject.toml", PYPROJECT)
    _touch(t / "tests" / "test_vendor_integrity.py", "def test_vi():\n    assert True\n")
    _touch(t / "tests" / "test_declarations_fixed.py", "def test_df():\n    assert True\n")
    _touch(t / "extended" / "walker.py", "X = 1\n")
    _touch(t / "tests" / "test_walker.py",
           "import pytest\n\ndef test_w():\n    assert True\n\n"
           "@pytest.mark.slow\ndef test_w_slow():\n    raise AssertionError('a slow test ran from the edit hook')\n")
    _touch(t / "tests" / "test_decoy.py", "def test_decoy():\n    raise AssertionError('the whole tier ran')\n")
    _touch(t / "extended" / "broken.py", "X = 1\n")
    _touch(t / "tests" / "test_broken.py", "def test_b():\n    raise AssertionError('planted failure')\n")
    return t


def _invoke(path: Path, cwd: Path) -> tuple[int, str, str]:
    payload = {"tool_name": "Edit", "cwd": str(cwd), "tool_input": {"file_path": str(path)}}
    proc = subprocess.run([sys.executable, str(HOOKS / "run_tests.py")], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1"})
    return proc.returncode, proc.stdout, proc.stderr


def _record(t: Path) -> dict:
    return json.loads((t / "results" / ".last_test_run.json").read_text(encoding="utf-8"))


def test_the_hook_runs_only_the_matched_and_fixed_tests(fake_main):
    code, out, err = _invoke(fake_main / "extended" / "walker.py", fake_main)
    assert code == 0, out + err                              # the decoy and the slow test would have failed it
    assert "3 passed" in out and "1 deselected" in out, out
    rec = _record(fake_main)
    assert set(rec) == {"timestamp", "exit_code", "tier", "summary"}     # the record's form, unchanged
    assert rec["exit_code"] == 0 and rec["tier"] == "not slow and not heavy"
    assert "3 passed" in rec["summary"] and "test_walker.py" in rec["summary"]


def test_the_hook_runs_only_the_fixed_pair_without_a_match(fake_main):
    _touch(fake_main / "extended" / "lonely.py", "X = 2\n")
    code, out, err = _invoke(fake_main / "extended" / "lonely.py", fake_main)
    assert code == 0, out + err
    assert "2 passed" in out, out
    assert _record(fake_main)["exit_code"] == 0


def test_the_hook_reports_a_failure_without_blocking(fake_main):
    code, _, err = _invoke(fake_main / "extended" / "broken.py", fake_main)
    assert code == 2 and "planted failure" in err and "1 failed" in err
    assert "Reported, not blocked" in err
    assert _record(fake_main)["exit_code"] != 0


def test_an_edited_test_file_runs_itself(fake_main):
    code, out, err = _invoke(fake_main / "tests" / "test_walker.py", fake_main)
    assert code == 0 and "3 passed" in out, out + err


def test_the_worktree_skip_is_kept(fake_main, tmp_path):
    """E-027: in a worktree or clean checkout (`.git` a file) the hook runs nothing and records nothing."""
    wt = tmp_path / "wt"
    import shutil

    shutil.copytree(fake_main, wt)
    shutil.rmtree(wt / ".git")
    (wt / ".git").write_text("gitdir: C:/somewhere/.git/worktrees/wt\n", encoding="utf-8")
    code, out, err = _invoke(wt / "extended" / "broken.py", wt)
    assert code == 0 and out.strip() == "" and err.strip() == ""
    assert not (wt / "results" / ".last_test_run.json").exists()
