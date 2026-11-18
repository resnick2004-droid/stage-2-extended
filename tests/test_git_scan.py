"""Q-156: every `git grep` (and `git log -S`) the suite runs has a time limit and fails loudly (`extended.git_scan`).

A pre-commit fast tier hung for about six hours on one `git grep` over every ref, its CPU time flat. These tests hold
the helper to its three duties -- a declared limit (300 s), the whole process tree killed on it, a clear error naming
the command, never a silent "no match" -- and hold every routed scan's output to the unrouted command's, on temporary
repositories with synthetic numbers only (no seed of any declared block appears in this file).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from extended import git_scan as GS

ROOT = Path(__file__).resolve().parent.parent
PAT = "9999000[0-9]"                        # a synthetic block: far from every declared seed range


def _git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _repo(tmp_path: Path) -> Path:
    t = tmp_path / "repo"
    t.mkdir()
    _git(t, "init", "-q", "-b", "master")
    _git(t, "config", "user.email", "t@example.invalid")
    _git(t, "config", "user.name", "t")
    (t / "a.py").write_text("SEED = 99990005\n", encoding="utf-8")
    (t / "b.py").write_text("x = 999900051\n", encoding="utf-8")            # not word-bounded: no match
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "c0")
    return t


# ------------------------------------------------------------------------------------------------ the helper itself


def test_the_limit_is_declared_at_300_seconds():
    assert GS.GIT_SCAN_TIMEOUT_S == 300


def test_a_found_match_is_the_plain_commands_output(tmp_path):
    t = _repo(tmp_path)
    argv = ["git", "grep", "-n", "-I", "-w", "-E", PAT, "HEAD", "--"]
    r = GS.run(argv, cwd=t, text=True)
    plain = subprocess.run(argv, cwd=t, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.splitlines() == ["HEAD:a.py:1:SEED = 99990005"]
    assert (r.returncode, r.stdout, r.stderr) == (plain.returncode, plain.stdout, plain.stderr)
    w = GS.run(["git", "grep", "--untracked", "-l", "-I", "-w", "-E", PAT], cwd=t, text=True, encoding="utf-8",
               errors="replace")
    assert w.returncode == 0 and w.stdout.splitlines() == ["a.py"]


def test_no_match_is_exit_1_and_empty(tmp_path):
    t = _repo(tmp_path)
    r = GS.run(["git", "grep", "-n", "-I", "-w", "-E", "8888000[0-9]", "HEAD", "--"], cwd=t, text=True)
    assert (r.returncode, r.stdout) == (1, "")


def test_a_git_failure_is_returned_for_the_caller_to_refuse(tmp_path):
    t = _repo(tmp_path)
    r = GS.run(["git", "grep", "-l", "-E", PAT, "refs/heads/no-such-branch", "--"], cwd=t, text=True)
    assert r.returncode not in (0, 1) and r.stderr


def test_bytes_and_input_pass_through(tmp_path):
    t = _repo(tmp_path)
    blob = _git(t, "rev-parse", "HEAD:a.py").strip()
    r = GS.run(["git", "cat-file", "--batch"], cwd=t, input=(blob + "\n").encode())
    assert r.returncode == 0 and isinstance(r.stdout, bytes) and b"SEED = 99990005" in r.stdout


_SLOW = textwrap.dedent("""
    import subprocess, sys, time
    # a grandchild that holds this process's stdout pipe: a plain subprocess.run would wait on it forever
    g = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"], stdout=sys.stdout.fileno())
    with open(sys.argv[1], "w") as f:
        f.write(f"{g.pid}\\n")
    print("started", flush=True)
    time.sleep(600)
""")


def test_a_timeout_raises_naming_the_command_and_leaves_no_process(tmp_path, monkeypatch):
    pids_file = tmp_path / "pids.txt"
    argv = [sys.executable, "-c", _SLOW, str(pids_file)]
    monkeypatch.setattr(GS, "GIT_SCAN_TIMEOUT_S", 3)                 # the default read at call time
    t0 = time.monotonic()
    child = grandchild = None
    try:
        with pytest.raises(GS.ScanTimeout) as exc:
            GS.run(argv, cwd=tmp_path, text=True)
        elapsed = time.monotonic() - t0
        assert elapsed < 60, elapsed
        msg = str(exc.value)
        assert "timed out after 3 s" in msg and "time.sleep(600)" in msg and "never read as" in msg
        assert exc.value.argv == argv and exc.value.timeout == 3
        child = exc.value.pid
        grandchild = int(pids_file.read_text().split()[0])
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and (GS.pid_alive(child) or GS.pid_alive(grandchild)):
            time.sleep(0.2)
        assert not GS.pid_alive(child), f"the command's process {child} survived"
        assert not GS.pid_alive(grandchild), f"its child {grandchild} survived"
    finally:
        for pid in (child, grandchild):
            if pid and GS.pid_alive(pid):
                GS.kill_tree(pid)


def test_pid_alive_reads_a_live_and_an_ended_process():
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        assert GS.pid_alive(p.pid)
    finally:
        p.kill()
        p.wait()
    assert not GS.pid_alive(p.pid)


# ------------------------------------------------------------------------------------------------ the ref scan


def _refs_repo(tmp_path: Path) -> tuple[Path, list[str]]:
    t = _repo(tmp_path)
    _git(t, "checkout", "-q", "-b", "side")
    (t / "c.py").write_text("y = 99990007\n", encoding="utf-8")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "side")
    _git(t, "checkout", "-q", "master")
    _git(t, "update-ref", "refs/remotes/origin/side", "refs/heads/side")    # a remote's copy: the same commit
    _git(t, "tag", "-a", "v1", "-m", "an annotated tag", "side")
    _git(t, "tag", "light", "master")
    refs = _git(t, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags").split()
    return t, refs


@pytest.mark.parametrize("args", [["-l", "-I", "-w", "-E", PAT], ["-n", "-I", "-w", "-E", PAT],
                                  ["-l", "-I", "-w", "-E", "8888000[0-9]"]])
def test_grep_refs_is_the_per_ref_scan(tmp_path, args):
    t, refs = _refs_repo(tmp_path)
    assert len(refs) == 5
    plain = subprocess.run(["git", "grep", *args, *refs, "--"], cwd=t, capture_output=True, text=True)
    assert plain.returncode in (0, 1), plain.stderr
    want = sorted(tuple(line.split(":", 1)) for line in plain.stdout.splitlines())
    got = GS.grep_refs(t, args, refs, text=True)
    assert sorted(got) == want
    if args[-1] == PAT:
        assert {r for r, _ in got} == set(refs)                 # every ref, the remote's copy and the tags included


def test_grep_refs_greps_each_commit_once(tmp_path, monkeypatch):
    t, refs = _refs_repo(tmp_path)
    seen = []
    real = GS.run

    def spy(argv, **kw):
        seen.append(list(argv))
        return real(argv, **kw)

    monkeypatch.setattr(GS, "run", spy)
    GS.grep_refs(t, ["-l", "-I", "-w", "-E", PAT], refs, text=True)
    greps = [a for a in seen if a[1] == "grep"]
    assert len(greps) == 1
    objs = greps[0][greps[0].index(PAT) + 1:-1]
    # 5 refs, 3 objects: master's commit (master, the light tag), side's (side, its remote copy), the annotated tag's
    assert len(objs) == len(set(objs)) == 3


def test_grep_refs_refuses_a_failed_grep(tmp_path):
    t, refs = _refs_repo(tmp_path)
    with pytest.raises(RuntimeError, match="git grep failed"):
        GS.grep_refs(t, ["-l", "-E", "("], refs, text=True)


# ------------------------------------------------------------------------------------------------ the routing proxy


@pytest.mark.parametrize("argv, routed", [
    (["git", "grep", "-l", "x"], True),
    (["git", "-C", ".", "grep", "-I", "-l", "x"], True),
    (["git", "--no-pager", "-c", "a.b=c", "grep", "x"], True),
    (["git", "log", "--format=%H", "-S", "| E-1 |", "--", "DECISIONS.md"], True),
    (["git", "log", "-Sfoo"], True),
    (["git", "log", "-G", "foo"], True),
    (["git", "log", "--format=%H"], False),
    (["git", "rev-parse", "HEAD"], False),
    (["git", "for-each-ref", "--format=%(refname)"], False),
    (["git", "cat-file", "--batch"], False),
    (["python", "grep"], False),
])
def test_is_scan(argv, routed):
    assert GS.is_scan(argv) is routed


def test_the_proxy_routes_scans_and_delegates_the_rest(tmp_path, monkeypatch):
    t = _repo(tmp_path)
    argv = ["git", "grep", "-n", "-I", "-w", "-E", PAT, "HEAD", "--"]
    plain = subprocess.run(argv, cwd=t, capture_output=True, text=True, encoding="utf-8", errors="replace")
    via = GS.PROXY.run(argv, cwd=t, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert (via.returncode, via.stdout, via.stderr) == (plain.returncode, plain.stdout, plain.stderr)
    assert GS.PROXY.PIPE is subprocess.PIPE and GS.PROXY.CompletedProcess is subprocess.CompletedProcess
    calls = []
    monkeypatch.setattr(GS, "run", lambda a, **kw: calls.append((list(a), kw)) or subprocess.CompletedProcess(a, 1,
                                                                                                         "", ""))
    GS.PROXY.run(argv, cwd=t, capture_output=True, text=True)
    GS.PROXY.run(["git", "log", "-S", "x"], cwd=t, capture_output=True)
    assert [c[0][1] for c in calls] == ["grep", "log"] and calls[0][1]["timeout"] is None
    assert GS.PROXY.run(["git", "rev-parse", "HEAD"], cwd=t, capture_output=True, text=True).returncode == 0
    assert len(calls) == 2                                  # not a scan: subprocess.run itself
    assert GS.PROXY.run(["git", "grep", "x"], cwd=t, capture_output=True, timeout=7) is not None
    assert calls[-1][1]["timeout"] == 7                     # a caller's own limit is kept
    with pytest.raises(subprocess.CalledProcessError):
        GS.PROXY.run(["git", "grep", "x"], cwd=t, capture_output=True, check=True)


def _private(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def q108():
    return _private("q108_calibrate_for_git_scan_t", "scripts/q108_calibrate.py")


def test_route_scans_reaches_the_imported_copies(q108):
    with pytest.MonkeyPatch.context() as mp:
        patched = GS.route_scans(mp, q108)
        assert q108.subprocess is GS.PROXY and q108.Q82.subprocess is GS.PROXY
        assert {q108.__name__, q108.Q82.__name__} <= set(patched)
        assert np_untouched()
    assert q108.subprocess is subprocess and q108.Q82.subprocess is subprocess


def np_untouched() -> bool:
    import numpy
    return getattr(numpy, "subprocess", None) is not GS.PROXY


def test_the_pinned_scans_give_the_same_verdicts_routed(q108, tmp_path):
    """Q-108's and Q-82's seed scans (their files pinned by blob, never edited) on a temporary repository with a seed
    of each block on a side branch and in the working tree, built at run time from the modules' own blocks."""
    t = _repo(tmp_path)
    _git(t, "checkout", "-q", "-b", "side")
    (t / "extended").mkdir()
    (t / "extended" / "stray.py").write_text(f"s = {q108.CAL_BLOCK[3]}\nq = {q108.Q82.SEED_BLOCK[4]}\n",
                                             encoding="utf-8")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "side")
    _git(t, "checkout", "-q", "master")
    (t / "uses.py").write_text(f"r = {q108.VAL_BLOCK[2]}\n", encoding="utf-8")
    plain = (q108.literal_problems(t), q108.Q82.seed_block_problems(t))
    with pytest.MonkeyPatch.context() as mp:
        GS.route_scans(mp, q108)
        routed = (q108.literal_problems(t), q108.Q82.seed_block_problems(t))
    assert routed == plain
    probs = plain[0][0]
    assert any("stray.py" in p and "side" in p for p in probs) and any("uses.py" in p for p in probs)
    assert any("stray.py" in p and "side" in p for p in plain[1][0])          # Q-82's block found too


def test_a_timeout_in_a_pinned_scan_raises_never_no_match(q108, tmp_path, monkeypatch):
    t = _repo(tmp_path)

    def stalls(argv, **kw):
        raise GS.ScanTimeout(list(argv), 300, 12345, kw.get("cwd"))

    monkeypatch.setattr(GS, "run", stalls)
    with pytest.MonkeyPatch.context() as mp:
        GS.route_scans(mp, q108)
        with pytest.raises(GS.ScanTimeout, match="git grep"):
            q108.literal_problems(t)
        with pytest.raises(GS.ScanTimeout, match="git grep"):
            q108.Q82.seed_block_problems(t)


def test_no_unrouted_scan_is_left_in_the_suite():
    """Every `git grep` / `git log -S` call written in `tests/` (outside the scripts pinned by blob, which the tests
    route with `route_scans`) goes through this helper: a raw `subprocess.run([... "grep" ...])` is refused."""
    bad = []
    for p in sorted((ROOT / "tests").glob("*.py")):
        if p.name == "test_git_scan.py":
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "subprocess.run(" in line and ('"grep"' in line or '"-S"' in line):
                bad.append(f"{p.name}:{i}")
    assert bad == [], bad
