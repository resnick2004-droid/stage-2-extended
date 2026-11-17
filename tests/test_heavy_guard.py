"""Q-118 (E-145): a test marked `heavy` never runs while another process holds the run lock.

The guard (`extended.lock_guard`, wired into the root `conftest.py`'s collection hook) skips every `heavy` test when
`run.lock` exists at the **main** repository's root (found through `git rev-parse --git-common-dir`, so a worktree or
a clean checkout sees the main tree's lock) and the process is not the lock's holder -- the holder being the command
`scripts/run_clean.py` launched under the lock, which it marks with `S2X_LOCK_HOLDER=<job>`. When the main root
cannot be found, heavy tests are skipped rather than run.

Two layers: the decision itself (`heavy_skip_reason`) on a monkeypatched root, and the real root `conftest.py`
copied into temporary git repositories (a main tree, a worktree of it, a folder outside git) and run by pytest in a
child process -- the hook as the suite uses it. Nothing here reads the bars or touches the machine's real lock.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from extended import lock_guard as G

ROOT = Path(__file__).resolve().parent.parent

HELD = "heavy test skipped: run.lock held by {job} (only the lock's holder may run heavy tests)"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def lock(root: Path, job: str = "other-job", **extra) -> Path:
    p = root / G.LOCK_NAME
    p.write_text(json.dumps({"job": job, "task": "Q-00", "holder": "t", "pid": 1, **extra}), encoding="utf-8")
    return p


# ---------------------------------------------------------------- the decision, on a monkeypatched root

@pytest.fixture()
def root(tmp_path, monkeypatch):
    r = tmp_path / "main"
    r.mkdir()
    monkeypatch.setattr(G, "main_root", lambda start=None: r)
    monkeypatch.delenv(G.LOCK_HOLDER_ENV, raising=False)
    return r


def test_no_lock_no_skip(root):
    assert G.heavy_skip_reason(env={}) is None


def test_a_lock_held_by_another_job_skips_with_the_plain_reason(root):
    lock(root, "q108-calibrate")
    assert G.heavy_skip_reason(env={}) == HELD.format(job="q108-calibrate")


def test_a_holder_variable_naming_another_job_still_skips(root):
    lock(root, "q108-calibrate")
    assert G.heavy_skip_reason(env={G.LOCK_HOLDER_ENV: "f03-a0"}) == HELD.format(job="q108-calibrate")


def test_the_holder_variable_matching_the_lock_runs(root):
    lock(root, "q108-calibrate")
    assert G.heavy_skip_reason(env={G.LOCK_HOLDER_ENV: "q108-calibrate"}) is None


def test_an_empty_holder_never_matches(root):
    lock(root, "")
    assert G.heavy_skip_reason(env={G.LOCK_HOLDER_ENV: ""}) == HELD.format(job="an unnamed job")
    assert G.heavy_skip_reason(env={G.LOCK_HOLDER_ENV: "an unnamed job"}) is not None


def test_an_unreadable_lock_is_held(root):
    (root / G.LOCK_NAME).write_text("{not json", encoding="utf-8")
    reason = G.heavy_skip_reason(env={})
    assert reason == HELD.format(job="an unreadable lock")
    assert G.heavy_skip_reason(env={G.LOCK_HOLDER_ENV: "an unreadable lock"}) == reason, "nothing matches it"


def test_the_root_not_found_skips(monkeypatch):
    monkeypatch.setattr(G, "main_root", lambda start=None: None)
    reason = G.heavy_skip_reason(env={G.LOCK_HOLDER_ENV: "anything"})
    assert reason is not None and reason.startswith("heavy test skipped:") and "root" in reason


def test_main_root_is_none_outside_git(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    d = tmp_path / "loose"
    d.mkdir()
    assert G.main_root(d) is None


def test_main_root_from_a_worktree_is_the_main_tree(tmp_path):
    main, wt = _main_and_worktree(tmp_path, files={})
    assert G.main_root(main) == main.resolve()
    assert G.main_root(wt) == main.resolve()


# ---------------------------------------------------------------- the real conftest, in a child pytest

PROBE = '''import pytest

@pytest.mark.heavy
def test_heavy():
    pass

@pytest.mark.heavy
@pytest.mark.skipif(True, reason="its own marker")
def test_heavy_with_its_own_skip():
    pass

def test_light():
    pass
'''

PYPROJECT = '''[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["heavy: reads the full bars", "slow: the engine"]
'''


def _tree(d: Path) -> dict[str, str]:
    return {"conftest.py": (ROOT / "conftest.py").read_text(encoding="utf-8"), "pyproject.toml": PYPROJECT,
            "tests/test_probe.py": PROBE}


def _write(d: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def _main_and_worktree(tmp_path: Path, files: dict[str, str] | None = None) -> tuple[Path, Path]:
    main = tmp_path / "main"
    main.mkdir()
    git(main, "init", "-q", "-b", "master")
    git(main, "config", "user.email", "t@example.invalid")
    git(main, "config", "user.name", "t")
    git(main, "config", "core.autocrlf", "false")
    _write(main, _tree(main) if files is None else files)
    (main / ".gitignore").write_text("run.lock\n__pycache__/\n.pytest_cache/\n", encoding="utf-8")
    git(main, "add", "-A")
    git(main, "commit", "-q", "-m", "probe")
    wt = tmp_path / "wt"
    git(main, "worktree", "add", "-q", "--detach", str(wt))
    return main, wt


def _pytest(cwd: Path, tmp_path: Path, holder: str | None = None) -> dict[str, tuple[str, str]]:
    """Run pytest in `cwd` (child process); {test name: (outcome, skip reason)} from its JUnit XML."""
    env = {k: v for k, v in os.environ.items() if k != G.LOCK_HOLDER_ENV}
    env.update(PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1",
               GIT_CEILING_DIRECTORIES=str(tmp_path))
    if holder is not None:
        env[G.LOCK_HOLDER_ENV] = holder
    xml = tmp_path / f"junit-{cwd.name}-{holder}.xml"
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={xml}",
                          "-rs"], cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stdout + out.stderr
    import xml.etree.ElementTree as ET
    res = {}
    for case in ET.parse(xml).getroot().iter("testcase"):
        sk = case.find("skipped")
        res[case.get("name")] = ("skipped", sk.get("message", "")) if sk is not None else ("passed", "")
    return res


def test_hook_no_lock_leaves_heavy_tests_to_their_own_markers(tmp_path):
    main, _ = _main_and_worktree(tmp_path)
    res = _pytest(main, tmp_path)
    assert res["test_heavy"] == ("passed", "")
    assert res["test_light"] == ("passed", "")
    assert res["test_heavy_with_its_own_skip"] == ("skipped", "its own marker")


def test_hook_a_lock_held_by_another_job_skips_heavy_tests_in_a_worktree(tmp_path):
    main, wt = _main_and_worktree(tmp_path)
    lock(main, "q108-calibrate")                       # the main tree's lock; the worktree has none of its own
    for where in (main, wt):
        res = _pytest(where, tmp_path)
        assert res["test_heavy"] == ("skipped", HELD.format(job="q108-calibrate")), where
        assert res["test_heavy_with_its_own_skip"][0] == "skipped"
        assert res["test_light"] == ("passed", ""), "light tests are never touched"


def test_hook_the_holder_runs_heavy_tests(tmp_path):
    main, wt = _main_and_worktree(tmp_path)
    lock(main, "q108-calibrate")
    res = _pytest(wt, tmp_path, holder="q108-calibrate")
    assert res["test_heavy"] == ("passed", "")
    res = _pytest(wt, tmp_path, holder="someone-else")
    assert res["test_heavy"] == ("skipped", HELD.format(job="q108-calibrate"))


def test_hook_the_root_not_found_skips_heavy_tests(tmp_path):
    loose = tmp_path / "loose"                         # no git anywhere up to the ceiling
    _write(loose, _tree(loose))
    res = _pytest(loose, tmp_path, holder="anything")
    assert res["test_heavy"][0] == "skipped" and "root" in res["test_heavy"][1]
    assert res["test_light"] == ("passed", "")


def test_the_lock_name_is_run_locks():
    """The guard and `scripts/run_lock.py` look at the same file."""
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import run_lock as RL
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    assert RL.LOCK.name == G.LOCK_NAME
    assert RL.LOCK.parent == G.main_root(ROOT)
