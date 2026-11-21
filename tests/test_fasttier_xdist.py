"""Q-193: the pre-commit fast tier runs in parallel inside its one slot (`scripts/fasttier_xdist.py`).

What these tests hold:

- **n from memory** is a pure function (`choose_workers`): floor((available - reserve) / per worker), between 1 and 4,
  1 for unknown or nonsensical memory, capped by `S2X_FASTTIER_WORKERS`; n = 1 runs today's command exactly;
- **the rule** (`judge`): a pass needs every test of the serial collection in the parallel run, once, with one outcome;
  the tests that failed in parallel -- and only those -- rerun serially; the commit passes only if each passed in one or
  the other; a test that passed only serially is named as an ISOLATION DEFECT in the verdict line; **a changed count is
  refused**; any other exit status fails;
- **the selection is unchanged**: every command is the hook's own `python -m pytest -o addopts= -q -m <selection>`
  with nothing that selects or deselects added (the parallel run adds -n, --dist and the recording plugin; the rerun
  adds the plugin and the failed node ids);
- **end to end**, on a throwaway pytest project (never this suite) with two real xdist workers: a clean pass, a test that
  fails only in parallel, a test that fails both ways, a count that differs from the serial run's, and n = 1;
- **the hook**, installed only into a throwaway git repository's hooks (never the shared `.git/hooks`), records the
  parallel verdict line, and refuses a commit whose parallel run failed and whose rerun failed too.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import fasttier_xdist as X  # noqa: E402
from extended import fasttier_report as FR  # noqa: E402

SEL = "not slow and not heavy"
LIMIT = 300
PASS_LINE = re.compile(r"[0-9]+ passed")          # the hook's own grep for the verdict's pass line


# ------------------------------------------------------------------------------------------------ n from memory

def test_the_declared_bounds():
    assert X.MAX_WORKERS == 4
    assert X.DIST == "loadfile"
    assert X.PER_WORKER_GB > 0 and X.RESERVE_GB >= 1.5        # never below the lock's own memory floor
    assert X.MEASURE_SOURCE and "slice" in X.MEASURE_SOURCE


@pytest.mark.parametrize("available, want", [
    (None, 1), (float("nan"), 1), (float("inf"), 1), (-3.0, 1), (0.0, 1),
    (1.0, 1), (2.9, 1),
])
def test_unknown_or_short_memory_gives_one_worker(available, want):
    assert X.choose_workers(available, per_worker_gb=1.0, reserve_gb=1.5) == want


def test_n_is_the_floor_of_free_memory_over_a_workers_peak_between_one_and_four():
    pw, res = 1.2, 1.5
    for k in range(1, 5):
        at = res + k * pw
        assert X.choose_workers(at + 1e-9, per_worker_gb=pw, reserve_gb=res) == k
        assert X.choose_workers(at - 0.01, per_worker_gb=pw, reserve_gb=res) == max(1, k - 1)
    assert X.choose_workers(64.0, per_worker_gb=pw, reserve_gb=res) == 4
    assert X.choose_workers(64.0, per_worker_gb=pw, reserve_gb=res, max_workers=3) == 3


def test_n_never_falls_as_memory_rises_and_uses_the_declared_figures_by_default():
    prev = 0
    for tenth in range(0, 200):
        n = X.choose_workers(tenth / 10)
        assert 1 <= n <= X.MAX_WORKERS and n >= prev
        prev = n
        want = max(1, min(X.MAX_WORKERS, math.floor((tenth / 10 - X.RESERVE_GB) / X.PER_WORKER_GB)))
        assert n == want


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
def test_a_nonsensical_per_worker_figure_gives_one(bad):
    assert X.choose_workers(32.0, per_worker_gb=bad, reserve_gb=1.5) == 1


def test_the_cap_limits_n_and_one_turns_parallel_off():
    assert X.choose_workers(64.0, per_worker_gb=1.0, reserve_gb=1.5, cap=2) == 2
    assert X.choose_workers(64.0, per_worker_gb=1.0, reserve_gb=1.5, cap=1) == 1
    assert X.choose_workers(64.0, per_worker_gb=1.0, reserve_gb=1.5, cap=0) == 1
    assert X.choose_workers(64.0, per_worker_gb=1.0, reserve_gb=1.5, cap=9) == 4
    assert X.choose_workers(3.0, per_worker_gb=1.0, reserve_gb=1.5, cap=4) == 1     # the cap never raises n


@pytest.mark.parametrize("raw, want", [(None, None), ("", None), ("x", None), ("3", 3), (" 2 ", 2), ("1", 1),
                                       ("0", 1), ("-2", 1)])
def test_the_environment_cap(raw, want):
    env = {} if raw is None else {X.ENV_WORKERS: raw}
    assert X.cap_from_env(env) == want


# ------------------------------------------------------------------------------------------------ the commands

def _hook_serial_tokens() -> list[str]:
    text = (SCRIPTS / "pre-commit").read_text(encoding="utf-8")
    m = re.search(r'fasttier_lock\.py run -- "\$PYTHON" (-m pytest -o addopts= -q -m "\$FAST_TIER")\n', text)
    assert m, "the hook's serial fast-tier command is not where it was"
    return m.group(1).replace('"$FAST_TIER"', "SEL").split()


def test_n1_is_the_hooks_serial_command_exactly():
    cmd = X.serial_command(SEL, python="PY")
    assert cmd[0] == "PY"
    assert [*cmd[1:-1], "SEL"] == _hook_serial_tokens() and cmd[-1] == SEL


def test_the_parallel_and_rerun_commands_add_nothing_that_selects(tmp_path):
    base = X.serial_command(SEL, python="PY")
    rep = tmp_path / "r.json"
    par = X.parallel_command(SEL, 3, rep, python="PY")
    assert par[:len(base)] == base
    assert par[len(base):] == ["-n", "3", "--dist", "loadfile", "-p", "extended.fasttier_report", "--s2x-report",
                               str(rep)]
    col = X.collect_command(SEL, rep, python="PY")
    assert col[:len(base)] == base and col[len(base):] == ["--collect-only", "-p", "extended.fasttier_report",
                                                           "--s2x-report", str(rep)]
    ids = tmp_path / "ids.txt"
    rer = X.rerun_command(SEL, ids, rep, python="PY")
    assert rer[:len(base)] == base and rer[len(base):] == ["-p", "extended.fasttier_report", "--s2x-report", str(rep),
                                                           f"@{ids}"]
    for c in (par, col, rer):
        assert c.count("-m") == 2 and c[c.index("-m", 2) + 1] == SEL           # `-m pytest` and the one selection
        assert not any(a in c for a in ("-k", "--deselect", "--lf", "--last-failed", "-x", "--ignore"))


# ------------------------------------------------------------------------------------------------ the rule

IDS = [f"tests/test_t.py::test_{i}" for i in range(6)]


def rep(outcomes: dict[str, str] | None = None, status: int = 0, collected: list[str] | None = None, **kw) -> dict:
    outcomes = dict(outcomes if outcomes is not None else {i: "passed" for i in IDS})
    r = {"collected": list(collected if collected is not None else outcomes), "outcomes": outcomes,
         "collect_errors": [], "exitstatus": status, "workers_agree": True, "worker_collections": {}}
    r.update(kw)
    return r


def _all(**over) -> dict[str, str]:
    d = {i: "passed" for i in IDS}
    d.update(over)
    return d


def test_a_clean_parallel_run_passes_with_the_full_count_and_n():
    o = _all(**{IDS[4]: "skipped", IDS[5]: "xfailed"})
    v = X.judge(IDS, rep(o), None, n=3, seconds=12.0)
    assert v.code == 0 and v.passed == 4 and v.selected == 6 and not v.rerun and not v.defects
    assert PASS_LINE.search(v.line) and "\t" not in v.line
    assert v.line.startswith("fast tier: 4 passed of 6 selected (4 passed, 1 skipped, 1 xfailed;")
    assert "n=3" in v.line and "no serial rerun" in v.line and "matched" in v.line


def test_a_test_that_passes_only_in_the_serial_rerun_passes_named_as_an_isolation_defect():
    o = _all(**{IDS[1]: "failed", IDS[3]: "error"})
    rr = rep({IDS[1]: "passed", IDS[3]: "passed"}, status=0)
    v = X.judge(IDS, rep(o, status=1), rr, n=2)
    assert v.code == 0
    assert v.rerun == [IDS[1], IDS[3]] and v.defects == [IDS[1], IDS[3]] and not v.still_failing
    assert v.passed == 6 and "6 passed of 6 selected" in v.line
    assert "ISOLATION DEFECT" in v.line and IDS[1] in v.line and IDS[3] in v.line
    assert PASS_LINE.search(v.line) and "\t" not in v.line


def test_a_test_failing_serially_too_fails_the_run_and_is_named():
    o = _all(**{IDS[2]: "failed"})
    v = X.judge(IDS, rep(o, status=1), rep({IDS[2]: "failed"}, status=1), n=2)
    assert v.code == X.EXIT_FAILED and v.still_failing == [IDS[2]] and IDS[2] in v.line
    assert "FAILED" in v.line


def test_a_rerun_that_exits_non_zero_fails_even_when_its_outcomes_read_as_passed():
    o = _all(**{IDS[2]: "failed"})
    v = X.judge(IDS, rep(o, status=1), rep({IDS[2]: "passed"}, status=3), n=2)
    assert v.code == X.EXIT_FAILED


@pytest.mark.parametrize("case", ["missing", "extra", "swapped", "collected_swapped", "duplicate", "duplicate_both", "no_outcome",
                                  "outcome_not_collected", "workers_disagree", "collect_error", "no_report"])
def test_a_changed_count_is_refused(case):
    o = _all()
    expected = list(IDS)
    if case == "missing":
        o.pop(IDS[0])
        r = rep(o)
    elif case == "extra":
        o["tests/test_t.py::test_new"] = "passed"
        r = rep(o)
    elif case == "swapped":                                         # the same count, one test exchanged
        o.pop(IDS[0])
        o["tests/test_t.py::test_other"] = "passed"
        r = rep(o)
    elif case == "collected_swapped":                               # the workers' collection, not the outcomes
        r = rep(o, collected=IDS[1:] + ["tests/test_t.py::test_other"])
    elif case == "duplicate":
        expected = IDS + [IDS[0]]
        r = rep(o)
    elif case == "duplicate_both":                                  # the serial collection names a test twice
        expected = IDS + [IDS[0]]
        r = rep(o, collected=expected)
    elif case == "no_outcome":
        r = rep({k: v for k, v in o.items() if k != IDS[5]}, collected=IDS)
    elif case == "outcome_not_collected":
        r = rep({**o, "tests/test_t.py::ghost": "passed"}, collected=IDS)
    elif case == "workers_disagree":
        r = rep(o, workers_agree=False)
    elif case == "collect_error":
        r = rep(o, collect_errors=["tests/test_t.py"])
    else:
        r = None
    v = X.judge(expected, r, None, n=2)
    assert v.code == X.EXIT_REFUSED and v.problems and "REFUSED" in v.line


def test_the_rerun_must_hold_exactly_the_failed_tests():
    o = _all(**{IDS[1]: "failed"})
    for rr in (rep({IDS[1]: "passed", IDS[2]: "passed"}),          # a test that did not fail was rerun
               rep({}, collected=[]),                              # the failed test was not rerun
               rep({IDS[1]: "passed"}, collected=[IDS[1], IDS[2]])):
        v = X.judge(IDS, rep(o, status=1), rr, n=2)
        assert v.code == X.EXIT_REFUSED, rr


def test_failures_without_a_rerun_report_are_refused():
    v = X.judge(IDS, rep(_all(**{IDS[1]: "failed"}), status=1), None, n=2)
    assert v.code == X.EXIT_REFUSED


@pytest.mark.parametrize("status", [0, 2, 3, 4, 5])
def test_failures_under_an_exit_that_is_not_a_test_failure_are_refused(status):
    v = X.judge(IDS, rep(_all(**{IDS[1]: "failed"}), status=status), rep({IDS[1]: "passed"}), n=2)
    assert v.code == X.EXIT_REFUSED


@pytest.mark.parametrize("status", [1, 2, 3, 4, 5])
def test_a_non_zero_exit_with_no_test_failed_is_refused(status):
    v = X.judge(IDS, rep(_all(), status=status), None, n=2)
    assert v.code == X.EXIT_REFUSED


def test_the_verdict_line_names_at_most_forty_and_counts_the_rest():
    ids = [f"tests/test_t.py::test_{i}" for i in range(50)]
    o = {i: "failed" for i in ids}
    v = X.judge(ids, rep(o, status=1), rep({i: "passed" for i in ids}), n=2)
    assert v.code == 0 and ids[39] in v.line and ids[40] + "," not in v.line and "and 10 more" in v.line


def test_the_counts_in_the_line_add_up_to_the_selection():
    o = _all(**{IDS[0]: "skipped", IDS[1]: "xfailed", IDS[2]: "xpassed", IDS[3]: "failed"})
    v = X.judge(IDS, rep(o, status=1), rep({IDS[3]: "passed"}), n=4)
    inner = v.line.split("(", 1)[1].split(";", 1)[0]
    assert sum(int(x.split()[0]) for x in inner.split(", ")) == len(IDS)


# ------------------------------------------------------------------------------------------------ outcomes

@pytest.mark.parametrize("reports, want", [
    ([("setup", "passed", False), ("call", "passed", False), ("teardown", "passed", False)], "passed"),
    ([("setup", "passed", False), ("call", "failed", False), ("teardown", "passed", False)], "failed"),
    ([("setup", "failed", False), ("teardown", "passed", False)], "error"),
    ([("setup", "passed", False), ("call", "passed", False), ("teardown", "failed", False)], "error"),
    ([("setup", "skipped", False), ("teardown", "passed", False)], "skipped"),
    ([("setup", "passed", False), ("call", "skipped", False), ("teardown", "passed", False)], "skipped"),
    ([("setup", "passed", False), ("call", "skipped", True), ("teardown", "passed", False)], "xfailed"),
    ([("setup", "skipped", True), ("teardown", "passed", False)], "xfailed"),
    ([("setup", "passed", False), ("call", "passed", True), ("teardown", "passed", False)], "xpassed"),
    ([("???", "failed", False)], "error"),                     # xdist's report for a crashed worker's test
    ([("setup", "passed", False)], "error"),                   # never completed
    ([], "error"),
])
def test_outcome_of(reports, want):
    assert FR.outcome_of(reports) == want


# ------------------------------------------------------------------------------------------------ end to end

PROJECT_TESTS = r'''
import os
import pytest

MODE = os.environ.get("Q193_MODE", "")


def test_pass():
    pass


@pytest.mark.parametrize("k", range(6))
def test_many(k):
    pass


@pytest.mark.skip(reason="a skip")
def test_skipped():
    pass


@pytest.mark.xfail(strict=True)
def test_xfail():
    assert False


@pytest.mark.slow
def test_slow_is_not_selected():
    assert False


@pytest.mark.heavy
def test_heavy_is_not_selected():
    assert False


def test_fails_only_in_parallel():
    if MODE == "isolation":
        assert "PYTEST_XDIST_WORKER" not in os.environ


def test_always_fails_when_broken():
    assert MODE != "broken"
'''

PROJECT_CONFTEST = r'''
import os


def pytest_collection_modifyitems(config, items):
    # Q193_MODE=count: an xdist worker collects one test fewer than a serial run (the count the runner must refuse)
    if os.environ.get("Q193_MODE") == "count" and "PYTEST_XDIST_WORKER" in os.environ:
        items[:] = [i for i in items if i.name != "test_pass"]
'''

PROJECT_INI = "[pytest]\naddopts = -q\nmarkers =\n    slow: s\n    heavy: h\n"
N_SELECTED = 11                                                   # 1 + 6 + skip + xfail + 2


_OWN_LOCALAPPDATA: list[str] = []


def own_localappdata() -> str:
    """This test process's own LOCALAPPDATA, made on first use: the machine's fast-tier lock lives under the real one
    (fasttier_lock.default_lock_path), and a runner started by a test must never see -- or write -- the slots of the
    fast tiers really running (an isolation defect found by the commit's own fast tier, 2026-11-20: beside two real
    slots the test's runner chose n = 1)."""
    if not _OWN_LOCALAPPDATA:
        import tempfile

        _OWN_LOCALAPPDATA.append(tempfile.mkdtemp(prefix="q193-localappdata-"))
    return _OWN_LOCALAPPDATA[0]


def child_env(**extra) -> dict:
    """A clean child environment: nothing of an outer xdist run, a fast-tier hook or a worker cap leaks in, and the
    machine-wide fast-tier lock is out of reach (LOCALAPPDATA is this process's own)."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("PYTEST_", "GIT_", "S2X_FASTTIER", "Q193_")) and k != "PYTHONPATH"}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1", "LOCALAPPDATA": own_localappdata()})
    env.update({k: str(v) for k, v in extra.items()})
    return env


def test_a_child_never_sees_the_machines_fast_tier_lock(tmp_path):
    """The runner a test starts reads the lock under ITS LOCALAPPDATA: a slot held there is invisible to it."""
    import fasttier_lock as L

    env = child_env()
    assert env["LOCALAPPDATA"] != os.environ.get("LOCALAPPDATA")
    code = ("import sys; sys.path.insert(0, %r); import fasttier_lock as L; print(L.default_lock_path())"
            % str(SCRIPTS))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=LIMIT, env=env)
    lock = Path(out.stdout.strip())
    assert lock.parent == Path(env["LOCALAPPDATA"]) and lock != L.default_lock_path()


@pytest.fixture()
def project(tmp_path) -> Path:
    """A throwaway pytest project with this repository's recording plugin importable as `extended.fasttier_report`."""
    p = tmp_path / "proj"
    (p / "tests").mkdir(parents=True)
    (p / "extended").mkdir()
    shutil.copyfile(ROOT / "extended" / "fasttier_report.py", p / "extended" / "fasttier_report.py")
    (p / "extended" / "__init__.py").write_text("", encoding="utf-8")
    (p / "pytest.ini").write_text(PROJECT_INI, encoding="utf-8")
    (p / "tests" / "conftest.py").write_text(PROJECT_CONFTEST, encoding="utf-8")
    (p / "tests" / "test_proj.py").write_text(PROJECT_TESTS, encoding="utf-8")
    return p


def run_runner(project: Path, workers: int, mode: str = "") -> tuple[subprocess.CompletedProcess, Path]:
    work = project.parent / "work"
    p = subprocess.run([sys.executable, str(SCRIPTS / "fasttier_xdist.py"), "--work", str(work), "--workers",
                        str(workers), "-m", SEL], cwd=project, capture_output=True, text=True, timeout=LIMIT,
                       env=child_env(Q193_MODE=mode))
    return p, work


def last_pass_line(out: str) -> str:
    lines = [ln for ln in out.splitlines() if PASS_LINE.search(ln)]
    return lines[-1] if lines else ""


def summary_counts(line: str) -> dict[str, int]:
    """pytest's summary line as {kind: count}."""
    return {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|deselected|xfailed|xpassed|errors?)\b",
                                             line)}


needs_xdist = pytest.mark.skipif(not X.xdist_available(), reason="pytest-xdist is not installed")


@needs_xdist
def test_e2e_a_clean_parallel_run_matches_the_serial_runs_count(project):
    serial = subprocess.run(X.serial_command(SEL), cwd=project, capture_output=True, text=True, timeout=LIMIT,
                            env=child_env())
    assert serial.returncode == 0, serial.stdout + serial.stderr
    counts = summary_counts(last_pass_line(serial.stdout))
    assert counts["deselected"] == 2 and sum(v for k, v in counts.items() if k != "deselected") == N_SELECTED
    p, work = run_runner(project, 2)
    assert p.returncode == 0, p.stdout + p.stderr
    line = last_pass_line(p.stdout)
    assert line == p.stdout.strip().splitlines()[-1], "the verdict line must be the last line holding 'passed'"
    assert line.startswith(f"fast tier: {counts['passed']} passed of {N_SELECTED} selected"), line
    assert "n=2" in line and "no serial rerun" in line
    par = json.loads((work / "parallel.json").read_text(encoding="utf-8"))
    col = json.loads((work / "collect.json").read_text(encoding="utf-8"))
    assert len(col["collected"]) == N_SELECTED and sorted(par["outcomes"]) == sorted(col["collected"])
    assert len(par["worker_collections"]) == 2 and par["workers_agree"] is True
    assert not (work / "rerun.txt").exists()


@needs_xdist
def test_e2e_a_test_failing_only_in_parallel_is_rerun_alone_and_named(project):
    p, work = run_runner(project, 2, mode="isolation")
    assert p.returncode == 0, p.stdout + p.stderr
    line = last_pass_line(p.stdout)
    want = "tests/test_proj.py::test_fails_only_in_parallel"
    assert "ISOLATION DEFECT" in line and want in line and f"of {N_SELECTED} selected" in line, line
    assert (work / "rerun.txt").read_text(encoding="utf-8").splitlines() == [want]
    rr = json.loads((work / "rerun.json").read_text(encoding="utf-8"))
    assert rr["collected"] == [want] and rr["outcomes"] == {want: "passed"}


@needs_xdist
def test_e2e_a_test_failing_both_ways_fails_the_run(project):
    p, work = run_runner(project, 2, mode="broken")
    assert p.returncode == X.EXIT_FAILED, p.stdout + p.stderr
    assert "tests/test_proj.py::test_always_fails_when_broken" in p.stdout.strip().splitlines()[-1]
    rr = json.loads((work / "rerun.json").read_text(encoding="utf-8"))
    assert rr["collected"] == ["tests/test_proj.py::test_always_fails_when_broken"]


@needs_xdist
def test_e2e_a_parallel_count_that_differs_from_the_serial_runs_is_refused(project):
    p, work = run_runner(project, 2, mode="count")
    assert p.returncode == X.EXIT_REFUSED, p.stdout + p.stderr
    last = p.stdout.strip().splitlines()[-1]
    assert "REFUSED" in last and f"the serial collection {N_SELECTED}" in last, last
    assert not (work / "rerun.txt").exists()


def test_e2e_one_worker_runs_todays_command_and_keeps_pytests_own_line(project):
    p, work = run_runner(project, 1)
    assert p.returncode == 0, p.stdout + p.stderr
    line = last_pass_line(p.stdout)
    assert summary_counts(line) == {"passed": 9, "skipped": 1, "deselected": 2, "xfailed": 1}, line
    assert "fast tier:" not in line
    assert not (work / "collect.json").exists()


def test_e2e_without_xdist_n_is_one(project, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(X, "_run", lambda cmd, log=None: calls.append(cmd) or 0)
    assert X.run(SEL, project / "w", 64.0, None, python="PY", has_xdist=False, force=4) == 0
    assert calls == [X.serial_command(SEL, python="PY")]
    assert "pytest-xdist is not installed" in capsys.readouterr().out


def test_run_cleans_only_its_own_work_files(project, monkeypatch):
    work = project / "w"
    work.mkdir()
    (work / "keep.txt").write_text("x", encoding="utf-8")
    (work / "parallel.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(X, "_run", lambda cmd, log=None: 4)         # the collection fails: nothing else runs
    assert X.run(SEL, work, 64.0, None, python="PY", has_xdist=True, force=2) == X.EXIT_REFUSED
    assert (work / "keep.txt").exists() and not (work / "parallel.json").exists()


# ------------------------------------------------------------------------------------------------ the hook

def _git_sh() -> str | None:
    try:
        out = subprocess.run(["git", "var", "GIT_SHELL_PATH"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    p = out.stdout.strip()
    return p if out.returncode == 0 and p and Path(p).exists() else None


needs_sh = pytest.mark.skipif(_git_sh() is None, reason="git's own sh (git var GIT_SHELL_PATH) not found")

#: a stand-in for the lock's wrapper, run as a script: no lock -- it runs its command and tees the output, as the real
#: one does. Imported (the runner imports the lock for its slot accounting), it is the real module.
PASS_THROUGH_MAIN = r'''
def _pass_through():
    import os, subprocess, sys
    cmd = sys.argv[sys.argv.index("--") + 1:]
    env = dict(os.environ)
    tee = env.pop("S2X_FASTTIER_TEE", None)
    p = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.buffer.write(p.stdout)
    if tee:
        with open(tee, "ab") as f:
            f.write(p.stdout)
    return p.returncode


if __name__ == "__main__":
    sys.exit(_pass_through())
'''


def pass_through_lock() -> str:
    src = (SCRIPTS / "fasttier_lock.py").read_text(encoding="utf-8")
    guard = 'if __name__ == "__main__":\n    sys.exit(main())\n'
    assert src.count(guard) == 1
    return src.replace(guard, PASS_THROUGH_MAIN)


def git(cwd: Path, *args: str, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=LIMIT, env=env or child_env())
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {p.stdout}{p.stderr}")
    return p


@pytest.fixture()
def hook_repo(project) -> Path:
    """The throwaway project as a git repository with this tree's pre-commit and commit-msg in ITS OWN hooks folder,
    stub vendor and licence checks, the pass-through lock, and a copy of the runner whose memory figures make n = 4
    on any machine with memory known (the cap below brings it to 2)."""
    r = project
    (r / "scripts").mkdir()
    git(r.parent, "init", "-q", "-b", "main", str(r))
    for k, v in (("user.name", "t"), ("user.email", "t@t"), ("core.autocrlf", "false"), ("commit.gpgsign", "false")):
        git(r, "config", k, v)
    (r / "scripts" / "vendor_stage2.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (r / "scripts" / "check_price_levels.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (r / "scripts" / "fasttier_lock.py").write_text(pass_through_lock(), encoding="utf-8")
    for name in ("run_lock.py", "xdist_measure.py"):
        shutil.copyfile(SCRIPTS / name, r / "scripts" / name)
    src = (SCRIPTS / "fasttier_xdist.py").read_text(encoding="utf-8")
    src, k1 = re.subn(r"^PER_WORKER_GB = .*$", "PER_WORKER_GB = 1e-6", src, flags=re.M)
    src, k2 = re.subn(r"^RESERVE_GB = .*$", "RESERVE_GB = 0.0", src, flags=re.M)
    assert k1 == k2 == 1
    (r / "scripts" / "fasttier_xdist.py").write_text(src, encoding="utf-8")
    (r / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n", encoding="utf-8")
    git(r, "add", "-A")
    git(r, "commit", "-q", "--no-verify", "-m", "init")
    hooks = Path(git(r, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()) / "hooks"
    assert hooks.resolve().is_relative_to(r.resolve()), "the hook must go into the throwaway repository only"
    hooks.mkdir(exist_ok=True)
    for name in ("pre-commit", "commit-msg"):
        shutil.copyfile(SCRIPTS / name, hooks / name)
    return r


def _commit(r: Path, mode: str) -> subprocess.CompletedProcess:
    with (r / "tests" / "test_proj.py").open("a", encoding="utf-8") as f:
        f.write(f"\n# {mode or 'clean'}\n")
    git(r, "add", "-A")
    env = child_env(Q193_MODE=mode, PYTHON=sys.executable, GIT_EDITOR="true", GIT_PUSH_ON_COMMIT="0",
                    S2X_FASTTIER_WORKERS="2")
    return git(r, "commit", "-q", "-m", f"q193 {mode}", env=env, check=False)


def _verdicts(r: Path) -> list[list[str]]:
    p = Path(git(r, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()) / \
        "fasttier-verdicts.log"
    return [ln.split("\t") for ln in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


@needs_sh
@needs_xdist
def test_hook_records_the_parallel_verdict_line(hook_repo):
    if X.available_gb() is None:
        pytest.skip("free memory unknown here: n would be 1")
    p = _commit(hook_repo, "")
    assert p.returncode == 0, p.stdout + p.stderr
    tree = git(hook_repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    rec = [v for v in _verdicts(hook_repo) if v[0] == tree]
    assert rec and len(rec[-1]) == 4, _verdicts(hook_repo)
    assert rec[-1][3].startswith(f"fast tier: 9 passed of {N_SELECTED} selected") and "n=2" in rec[-1][3]
    gd = Path(git(hook_repo, "rev-parse", "--absolute-git-dir").stdout.strip())
    assert (gd / "fasttier-xdist" / "parallel.json").is_file()


@needs_sh
@needs_xdist
def test_hook_passes_an_isolation_defect_and_names_it_in_the_verdict(hook_repo):
    if X.available_gb() is None:
        pytest.skip("free memory unknown here: n would be 1")
    p = _commit(hook_repo, "isolation")
    assert p.returncode == 0, p.stdout + p.stderr
    tree = git(hook_repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    rec = [v for v in _verdicts(hook_repo) if v[0] == tree]
    assert rec and "ISOLATION DEFECT" in rec[-1][3] and "test_fails_only_in_parallel" in rec[-1][3]


@needs_sh
@needs_xdist
def test_hook_refuses_when_the_serial_rerun_fails_too(hook_repo):
    before = git(hook_repo, "rev-parse", "HEAD").stdout.strip()
    p = _commit(hook_repo, "broken")
    assert p.returncode != 0
    assert git(hook_repo, "rev-parse", "HEAD").stdout.strip() == before
    assert _verdicts(hook_repo) == []


def test_the_hook_runs_the_parallel_runner_inside_the_lock_after_the_checks():
    text = (SCRIPTS / "pre-commit").read_text(encoding="utf-8")
    par = ('run_child "$PYTHON" scripts/fasttier_lock.py run -- "$PYTHON" scripts/fasttier_xdist.py --work '
           '"$GITDIR/fasttier-xdist" -m "$FAST_TIER"\n')
    ser = 'run_child "$PYTHON" scripts/fasttier_lock.py run -- "$PYTHON" -m pytest -o addopts= -q -m "$FAST_TIER"\n'
    assert par in text and ser in text
    i_if = text.index("if [ -f scripts/fasttier_xdist.py ]; then\n")
    assert i_if < text.index(par) < text.index("else\n", i_if) < text.index(ser) < text.index("fi\nFT_RC=$?", i_if)
    assert text.index("scripts/vendor_stage2.py --verify || vendor_failed") < i_if
    assert text.index('scripts/check_price_levels.py --index "$COMMIT_INDEX" || price_level_failed') < i_if
    code = [ln.strip() for ln in text.splitlines() if "fasttier_xdist.py" in ln and not ln.lstrip().startswith("#")]
    assert code == ["if [ -f scripts/fasttier_xdist.py ]; then", par.strip()]   # run once, nowhere else
    assert "| tr -d '\\r' | tr '\\t' ' ')" in text                              # no tab can split the verdict record
    assert b"\r\n" not in (SCRIPTS / "pre-commit").read_bytes()


def test_the_requirement_is_recorded():
    import tomllib

    with open(ROOT / "pyproject.toml", "rb") as f:
        proj = tomllib.load(f)["project"]
    assert "pytest-xdist==3.6.1" in proj["optional-dependencies"]["test"]


# ------------------------------------------------------------------------------------------------ the measurement tool

def test_the_measurement_sums_each_workers_subtree():
    import xdist_measure as XM

    # 10 the command (pytest's controller); 11, 12 its workers; 13 a test's subprocess under 11; 14 under 13;
    # 20 unrelated; 0 the idle process, its own parent
    parent = {10: 1, 11: 10, 12: 10, 13: 11, 14: 13, 20: 1, 0: 0}
    ws = {10: 100, 11: 1000, 12: 500, 13: 300, 14: 30, 20: 9999, 0: 7}
    assert XM.subtree(10, parent) == {10, 11, 12, 13, 14}
    assert XM.subtree(0, parent) == {0}
    r = XM.tree_reading(10, parent, ws)
    assert r == {"tree": 1930, "root": 100, "workers": {11: 1330, 12: 500}, "processes": 5}
    pk = XM.Peaks()
    pk.add(r)
    pk.add({"tree": 50, "root": 120, "workers": {11: 10, 15: 2000}, "processes": 3})
    rec = pk.record()
    assert pk.workers == {11: 1330, 12: 500, 15: 2000} and pk.tree == 1930 and pk.root == 120
    assert rec["samples"] == 2 and rec["max_concurrent_children"] == 2


def test_the_measurement_refuses_to_start_below_its_floor_or_beside_a_heavy_run(tmp_path):
    lock = tmp_path / "run.lock"
    out = tmp_path / "m.json"
    p = subprocess.run([sys.executable, str(SCRIPTS / "xdist_measure.py"), "--out", str(out), "--floor-gb", "1e9",
                        "--run-lock", str(lock), "--", sys.executable, "-c", "print('it' + ' ran')"],
                       capture_output=True, text=True, timeout=LIMIT, env=child_env())
    if X.available_gb() is not None:
        assert p.returncode == 3 and "it ran" not in p.stdout
        assert json.loads(out.read_text(encoding="utf-8"))["aborted"].startswith("not started")
    lock.write_text("{}", encoding="utf-8")
    p = subprocess.run([sys.executable, str(SCRIPTS / "xdist_measure.py"), "--out", str(out), "--floor-gb", "0",
                        "--run-lock", str(lock), "--", sys.executable, "-c", "print('it' + ' ran')"],
                       capture_output=True, text=True, timeout=LIMIT, env=child_env())
    assert p.returncode == 3 and "it ran" not in p.stdout
    assert "run.lock" in json.loads(out.read_text(encoding="utf-8"))["aborted"]


@needs_xdist
@pytest.mark.skipif(os.name != "nt", reason="the kill-on-close job is Windows'")
def test_killing_the_runner_ends_its_pytest_and_every_worker(project, tmp_path):
    """The lock's wrapper kills its command with TerminateProcess, which no handler sees: the runner's job object must
    end the pytest under it and the xdist workers, never leave them running after the slot is released."""
    from fasttier_lock import pid_alive

    mark = tmp_path / "worker.pid"
    (project / "tests" / "test_sleep.py").write_text(
        "import os, pathlib, time\n\n\ndef test_sleeps():\n"
        "    pathlib.Path(os.environ['Q193_MARK']).write_text(str(os.getpid()))\n    time.sleep(120)\n",
        encoding="utf-8")
    proc = subprocess.Popen([sys.executable, str(SCRIPTS / "fasttier_xdist.py"), "--work", str(tmp_path / "w"),
                             "--workers", "2", "-m", SEL], cwd=project, env=child_env(Q193_MARK=mark),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    worker = None
    try:
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline and not (mark.exists() and mark.read_text().strip()):
            time.sleep(0.2)
        assert mark.exists(), "the sleeping test never started"
        worker = int(mark.read_text().strip())
        assert pid_alive(worker)
        proc.kill()                                                   # TerminateProcess, as the wrapper does
        proc.wait(timeout=30)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and pid_alive(worker):
            time.sleep(0.2)
        assert not pid_alive(worker), "a worker outlived its killed runner"
    finally:
        if proc.poll() is None:
            proc.kill()
        if worker and pid_alive(worker):
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(worker)], capture_output=True, timeout=60)


def test_the_per_worker_figure_is_the_measured_peak_with_its_margin():
    """PER_WORKER_GB traces to the committed measurement records: the largest worker subtree's peak over every
    completed run, times MARGIN, rounded up to 0.1 GB; RESERVE_GB is the fast-tier lock's own floor."""
    from fasttier_lock import MIN_FREE_GB

    recs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / X.MEASURE_DIR).glob("*.json"))]
    done = [r for r in recs if not r.get("aborted") and r.get("exit") == 0 and r.get("peak_worker_gb") is not None]
    assert len(done) >= 10, "the measurement matrix is not on record"
    peak = max(r["peak_worker_gb"] for r in done)
    assert X.PER_WORKER_GB == math.ceil(peak * X.MARGIN * 10 - 1e-9) / 10
    assert X.MARGIN >= 1.2 and X.RESERVE_GB == MIN_FREE_GB
    for r in recs:                                       # every aborted run says why; none is counted
        assert r.get("aborted") is None or isinstance(r["aborted"], str)


class _Node:
    def __init__(self, wid: str) -> None:
        self.gateway = type("G", (), {"id": wid})()


def test_the_plugin_records_whether_the_workers_collected_the_same_tests(tmp_path):
    for lists, agree in (([IDS, IDS], True), ([IDS, IDS[:-1]], False), ([IDS, list(reversed(IDS))], False)):
        out = tmp_path / f"r{agree}{len(lists[1])}.json"
        rec = FR.Recorder(out)
        for i, ids in enumerate(lists):
            rec.pytest_xdist_node_collection_finished(_Node(f"gw{i}"), ids)
        rec.pytest_sessionfinish(None, 0)
        got = json.loads(out.read_text(encoding="utf-8"))
        assert got["workers_agree"] is agree and got["collected"] == IDS
        assert got["worker_collections"] == {"gw0": len(lists[0]), "gw1": len(lists[1])}


def _fake_runs(monkeypatch, parallel_status: int, parallel_outcomes: dict, rerun_outcomes: dict | None = None):
    """run() with every pytest command replaced: each writes the report its command names."""
    calls = []

    def fake(cmd, log=None):
        calls.append(cmd)
        path = Path(cmd[cmd.index(X.REPORT_OPTION) + 1])
        if "--collect-only" in cmd:
            body = rep({i: "passed" for i in IDS}, status=0)
        elif "-n" in cmd:
            body = rep(parallel_outcomes, status=parallel_status, collected=IDS)
        else:
            body = rep(rerun_outcomes or {}, status=0)
        path.write_text(json.dumps(body), encoding="utf-8")
        return body["exitstatus"]

    monkeypatch.setattr(X, "_run", fake)
    monkeypatch.setattr(X, "_run_parallel", fake)
    return calls


def test_run_runs_the_collection_the_parallel_run_and_reruns_only_the_failed(tmp_path, monkeypatch, capsys):
    calls = _fake_runs(monkeypatch, 1, _all(**{IDS[2]: "failed"}), {IDS[2]: "passed"})
    assert X.run(SEL, tmp_path / "w", 64.0, None, python="PY", has_xdist=True, force=3) == 0
    assert ["--collect-only" in c for c in calls] == [True, False, False]
    assert calls[1] == X.parallel_command(SEL, 3, tmp_path / "w" / "parallel.json", python="PY")
    assert calls[2] == X.rerun_command(SEL, tmp_path / "w" / "rerun.txt", tmp_path / "w" / "rerun.json", python="PY")
    assert (tmp_path / "w" / "rerun.txt").read_text(encoding="utf-8").splitlines() == [IDS[2]]
    out = capsys.readouterr().out.strip().splitlines()
    assert "ISOLATION DEFECT" in out[-1] and IDS[2] in out[-1]


@pytest.mark.parametrize("status", [0, 2, 3])
def test_run_never_reruns_under_an_exit_that_is_not_a_test_failure(tmp_path, monkeypatch, status):
    calls = _fake_runs(monkeypatch, status, _all(**{IDS[2]: "failed"}), {IDS[2]: "passed"})
    assert X.run(SEL, tmp_path / "w", 64.0, None, python="PY", has_xdist=True, force=2) == X.EXIT_REFUSED
    assert len(calls) == 2 and not (tmp_path / "w" / "rerun.txt").exists()


def test_run_never_reruns_after_a_changed_count(tmp_path, monkeypatch):
    o = _all(**{IDS[2]: "failed"})
    o.pop(IDS[0])
    calls = _fake_runs(monkeypatch, 1, o, {IDS[2]: "passed"})
    assert X.run(SEL, tmp_path / "w", 64.0, None, python="PY", has_xdist=True, force=2) == X.EXIT_REFUSED
    assert len(calls) == 2 and not (tmp_path / "w" / "rerun.txt").exists()


# ------------------------------------------------------------------------------------------------ slots and workers

# Slots (Q-174) and xdist workers (Q-193) share one memory: a slot's reserve grows with its workers, by one accounting
# (fasttier_lock.slot_reserve_gb) that both the lock's admission of a further slot and the runner's choice of n use.

def test_one_per_worker_figure_and_a_slots_reserve_grows_with_its_workers():
    import fasttier_lock as L

    assert X.PER_WORKER_GB is L.PER_WORKER_GB or X.PER_WORKER_GB == L.PER_WORKER_GB
    assert "PER_WORKER_GB = L.PER_WORKER_GB" in (SCRIPTS / "fasttier_xdist.py").read_text(encoding="utf-8")
    assert L.slot_reserve_gb(1) == L.SLOT_RESERVE_GB                         # a serial slot: Q-174's reserve
    for n in range(1, 5):
        assert L.slot_reserve_gb(n) == pytest.approx(L.SLOT_RESERVE_GB + (n - 1) * L.PER_WORKER_GB)
        assert L.slot_reserve_gb(n, reserve_gb=2.0) == pytest.approx(2.0 + (n - 1) * L.PER_WORKER_GB)
    assert L.slot_reserve_gb(0) == L.SLOT_RESERVE_GB


@pytest.mark.parametrize("rec, want", [(None, 1), ({}, 1), ({"workers": 3}, 3), ({"workers": 1}, 1),
                                       ({"workers": 0}, 1), ({"workers": -2}, 1), ({"workers": "4"}, 1),
                                       ({"workers": 2.0}, 1), ({"workers": True}, 1)])
def test_workers_of_a_record(rec, want):
    import fasttier_lock as L

    got = L.workers_of(rec)
    assert got == want and type(got) is int


def _record(path: Path, pid: int, token: str, workers: int | None = None) -> None:
    from datetime import datetime, timezone

    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rec = {"tree": "t", "pid": pid, "host": "h", "start": stamp, "updated": stamp, "phase": "fast-tier",
           "token": token}
    if workers is not None:
        rec["workers"] = workers
    path.write_text(json.dumps(rec), encoding="utf-8")


def _dead_pid() -> int:
    return int(subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"], capture_output=True,
                              text=True, timeout=LIMIT).stdout.strip())


def test_fast_tiers_beside_lists_the_other_live_slots_by_their_workers(tmp_path):
    import fasttier_lock as L

    lock = tmp_path / "ft.lock"
    assert X.fast_tiers_beside({}, lock) == []                                  # free
    _record(lock, os.getpid(), "mine")
    assert X.fast_tiers_beside({L.ENV_TOKEN: "mine"}, lock) == []               # this run's own slot
    assert X.fast_tiers_beside({L.ENV_TOKEN: "other"}, lock) == [1]             # someone else's, serial
    _record(L.slot_path(lock, 1), os.getpid(), "beside", workers=3)
    assert X.fast_tiers_beside({L.ENV_TOKEN: "mine"}, lock) == [3]              # beside, at its n
    _record(L.slot_path(lock, 1), _dead_pid(), "gone", workers=3)
    assert X.fast_tiers_beside({L.ENV_TOKEN: "mine"}, lock) == []               # a dead holder is stale


def test_record_workers_writes_only_the_tokens_own_slot(tmp_path):
    import fasttier_lock as L

    lock = tmp_path / "ft.lock"
    _record(lock, os.getpid(), "other")
    _record(L.slot_path(lock, 1), os.getpid(), "mine")
    assert L.record_workers(lock, "mine", 3, n_slots=2) == L.slot_path(lock, 1)
    assert L.workers_of(json.loads(L.slot_path(lock, 1).read_text(encoding="utf-8"))) == 3
    assert "workers" not in json.loads(lock.read_text(encoding="utf-8"))
    assert L.record_workers(lock, "nobody", 2, n_slots=2) is None
    assert X.record_own_workers(2, env={}, lock=lock) is False                  # outside a slot: nothing written
    assert X.record_own_workers(4, env={L.ENV_TOKEN: "mine"}, lock=lock) is True
    assert L.workers_of(json.loads(L.slot_path(lock, 1).read_text(encoding="utf-8"))) == 4


def test_the_slots_beside_come_off_the_memory_before_n_is_chosen():
    import fasttier_lock as L

    pw, res = L.PER_WORKER_GB, X.RESERVE_GB
    beside = L.slot_reserve_gb(3)                                               # one slot running 3 workers
    for avail in (4.0, 6.0, 8.0, 10.0, 12.0, 16.0):
        want = max(1, min(4, math.floor((avail - res - beside) / pw)))
        assert X.choose_workers(avail, beside_gb=beside) == want
        assert X.choose_workers(avail, beside_gb=beside) <= X.choose_workers(avail)
    assert X.choose_workers(10.0, beside_gb=float("nan")) == 1
    assert X.choose_workers(10.0, beside_gb=-1.0) == 1


def test_run_counts_the_slots_beside_and_records_its_n_before_pytest(project, monkeypatch, capsys):
    import fasttier_lock as L

    events = []
    monkeypatch.setattr(X, "_run", lambda cmd, log=None: events.append(("run", cmd)) or 4)
    record = lambda n: events.append(("record", n))                            # noqa: E731
    # beside one serial slot, 4.0 GB: its 2.5 GB reserve leaves no worker beyond the first
    assert X.run(SEL, project / "w", 4.0, None, python="PY", has_xdist=True, beside=[1], record=record) == 4
    assert events == [("record", 1), ("run", X.serial_command(SEL, python="PY"))]
    assert "reserved for 1 slot(s) running beside" in capsys.readouterr().out
    events.clear()
    avail = X.RESERVE_GB + L.slot_reserve_gb(2) + 2 * L.PER_WORKER_GB + 0.01   # room for 2 beside a 2-worker slot
    X.run(SEL, project / "w", avail, None, python="PY", has_xdist=True, beside=[2], record=record)
    assert events[0] == ("record", 2) and events[1][0] == "run" and "--collect-only" in events[1][1]


def test_the_lock_admits_a_further_slot_only_beside_each_running_slots_reserve_at_its_workers(tmp_path):
    """Q-174's admission with Q-193's coupling: beside a slot running n workers, a further slot needs
    MIN_FREE_GB + slot_reserve_gb(n); a record without workers is a serial slot, Q-174's rule unchanged."""
    import fasttier_lock as L

    reserve = 2.0
    for workers in (None, 1, 2, 4):
        lock = tmp_path / f"ft{workers}.lock"
        _record(lock, os.getpid(), "running", workers=workers)
        need = L.MIN_FREE_GB + L.slot_reserve_gb(workers or 1, reserve)
        with pytest.raises(L.WaitTimeout):
            L.acquire(lock, tree="T", timeout_s=0.3, poll_s=0.02, free_gb=lambda: need - 0.01, max_slots=2,
                      reserve_gb=reserve)
        h = L.acquire(lock, tree="T", timeout_s=5, poll_s=0.02, free_gb=lambda: need + 0.01, max_slots=2,
                      reserve_gb=reserve)
        assert h.path == L.slot_path(lock, 1)
        L.release(h.path, h)


def test_a_runner_and_a_later_slot_never_count_the_same_memory_twice_or_not_at_all(tmp_path):
    """The coupling end to end on a temporary lock: the runner picks n from the memory free when its slot is taken and
    records it; the lock then opens a further slot only once the memory covers this slot's reserve at that n."""
    import fasttier_lock as L

    lock = tmp_path / "ft.lock"
    _record(lock, os.getpid(), "mine")
    avail = X.RESERVE_GB + 3 * L.PER_WORKER_GB + 0.05
    n = X.choose_workers(avail, beside_gb=sum(L.slot_reserve_gb(w) for w in X.fast_tiers_beside(
        {L.ENV_TOKEN: "mine"}, lock)))
    assert n == 3
    assert X.record_own_workers(n, env={L.ENV_TOKEN: "mine"}, lock=lock)
    need = L.MIN_FREE_GB + L.slot_reserve_gb(3)
    assert need > L.MIN_FREE_GB + L.SLOT_RESERVE_GB                             # more than Q-174's serial figure
    with pytest.raises(L.WaitTimeout):
        L.acquire(lock, tree="T", timeout_s=0.3, poll_s=0.02, free_gb=lambda: need - 0.01, max_slots=2)
    h = L.acquire(lock, tree="T", timeout_s=5, poll_s=0.02, free_gb=lambda: need + 0.01, max_slots=2)
    assert h.path == L.slot_path(lock, 1)
    # and the slot let in beside it sees this one at 3 workers when it, in turn, chooses its n
    assert X.fast_tiers_beside({L.ENV_TOKEN: h.token}, lock) == [3]
    L.release(h.path, h)
