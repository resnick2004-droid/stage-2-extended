"""The git hooks' verdict (Q-161): a commit is written only when the fast tier itself returned 0, and the hook tests the
tree the commit is made in.

**What went wrong (2026-11-18).** `timeout 3000 git commit` in wt-levels fired while the pre-commit hook was waiting on
the fast-tier lock and running pytest; commit 3451a10 was written at that instant (its object's mtime is the commit's
start plus 3000 s) and the orphaned pytest went on to report a failure nobody read. The cause, reproduced on stub hooks:
Git for Windows reads a hook's exit status as the low byte of its Windows exit code (`WEXITSTATUS(x) = x & 0xff`), and
the MSYS runtime gives a shell killed by signal N the exit code N << 8 (SIGTERM 0xF00, SIGKILL 0x900, SIGPIPE 0xD00,
SIGINT 0x200) -- a killed hook reads as exit 0, a pass. The re-exec was not the cause (a hook without it is read the
same way); it only added a stub process. Separately, inherited `GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE` made
git commit into one worktree while the hook named, and tested, another.

**What these tests hold**, each on a throwaway repository with stub checks (a stub "fast tier" that sleeps, prints a
pytest-like summary and exits with a chosen code -- never the real suite, never the machine's fast-tier lock):

- a passing fast tier commits and records a verdict keyed by the commit's tree; a failing one refuses;
- a hook killed by SIGTERM mid fast tier (`timeout N git commit`, the incident) never lets the commit through, and its
  child is killed rather than orphaned;
- a hook shell killed outright (SIGKILL, untrappable) is caught by the commit-msg hook: the pre-commit started for that
  tree and recorded no verdict;
- a closed output pipe (`git commit | head -1`) refuses rather than passes;
- inherited git variables that point the commit and the tested tree at different trees are refused; consistent ones
  are allowed and labelled with the tree committed into;
- the post-commit hook flags a commit whose tree has no verdict (`NO VERDICT <branch> <sha>`, in the verdict log and
  push.log, and on stderr); `scripts/check_verdicts.py` lists such commits in a range, merges exempt only when every
  parent is clean or outside the range.

Windows-only behaviour (the low-byte read) is what makes the signal tests fail on the old hook; on a POSIX git the
same tests pass because git sees the signal death. They need git's own sh (`git var GIT_SHELL_PATH`) and its
`timeout`; they skip without them.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
HOOK_NAMES = ("pre-commit", "commit-msg", "post-commit", "pre-merge-commit")   # Q-208 added the last
LIMIT = 120                                     # every subprocess here is time-limited


def _git_sh() -> str | None:
    try:
        out = subprocess.run(["git", "var", "GIT_SHELL_PATH"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    p = out.stdout.strip()
    return p if out.returncode == 0 and p and Path(p).exists() else None


def _real_git() -> str:
    """The git binary itself (not Git for Windows' `cmd\\git.exe` launcher, which would add a process layer)."""
    try:
        ep = subprocess.run(["git", "--exec-path"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        ep = ""
    for name in ("git.exe", "git"):
        if ep and (Path(ep) / name).is_file():
            return str(Path(ep) / name).replace("\\", "/")
    return (shutil.which("git") or "git").replace("\\", "/")


GIT_SH = _git_sh()
GIT = _real_git()
TIMEOUT = None
if GIT_SH:
    for cand in (Path(GIT_SH).parent / "timeout.exe", Path(GIT_SH).parent / "timeout"):
        if cand.is_file():
            TIMEOUT = str(cand).replace("\\", "/")
    TIMEOUT = TIMEOUT or shutil.which("timeout")

needs_sh = pytest.mark.skipif(GIT_SH is None, reason="git's own sh (git var GIT_SHELL_PATH) not found")
needs_timeout = pytest.mark.skipif(GIT_SH is None or TIMEOUT is None, reason="git's sh or its timeout not found")

STUB_FAST_TIER = r'''"""A stand-in for scripts/fasttier_lock.py: no lock, no pytest -- it sleeps, prints a summary and exits."""
import os, sys, time
log = os.environ["STUB_LOG"]
with open(log, "a", encoding="utf-8") as f:
    f.write(f"start {os.getpid()} {os.getcwd()}\n")
print("stub fast tier running", flush=True)
time.sleep(float(os.environ.get("STUB_SLEEP", "0")))
summary = os.environ.get("STUB_SUMMARY", "3 passed in 0.01s")
print(summary, flush=True)
tee = os.environ.get("S2X_FASTTIER_TEE")
if tee:
    with open(tee, "a", encoding="utf-8") as f:
        f.write(summary + "\n")
with open(log, "a", encoding="utf-8") as f:
    f.write("end\n")
sys.exit(int(os.environ.get("STUB_RC", "0")))
'''


def clean_env(**extra) -> dict:
    """The environment a fresh shell gives: no inherited git variables, no fast-tier token, a working python."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_") and k not in ("S2X_FASTTIER_TOKEN", "S2X_FASTTIER_TEE", "PRECOMMIT_UNDER_GIT_SH")}
    env.update({"PYTHON": sys.executable, "PYTHONDONTWRITEBYTECODE": "1", "GIT_EDITOR": "true",
                "GIT_PUSH_ON_COMMIT": "1", "GIT_TERMINAL_PROMPT": "0"})
    env.update({k: str(v) for k, v in extra.items()})
    return env


def git(cwd: Path, *args: str, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run([GIT, *args], cwd=cwd, capture_output=True, text=True, timeout=LIMIT,
                       env=env or clean_env())
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {p.stdout}{p.stderr}")
    return p


def head(cwd: Path, rev: str = "HEAD") -> str:
    return git(cwd, "rev-parse", rev).stdout.strip()


def common_dir(cwd: Path) -> Path:
    return Path(git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())


def verdicts(cwd: Path) -> str:
    p = common_dir(cwd) / "fasttier-verdicts.log"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def install_hooks(repo: Path) -> None:
    hooks = common_dir(repo) / "hooks"
    hooks.mkdir(exist_ok=True)
    for name in HOOK_NAMES:
        src = SCRIPTS / name
        if src.is_file():                       # the old hooks had no commit-msg
            shutil.copyfile(src, hooks / name)


@pytest.fixture()
def repo(tmp_path) -> Path:
    """A throwaway main tree with stub checks under scripts/ and this tree's hooks installed."""
    r = tmp_path / "main"
    (r / "scripts").mkdir(parents=True)
    git(tmp_path, "init", "-q", "-b", "main", str(r))
    for k, v in (("user.name", "t"), ("user.email", "t@t"), ("core.autocrlf", "false"), ("commit.gpgsign", "false")):
        git(r, "config", k, v)
    (r / "scripts" / "vendor_stage2.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (r / "scripts" / "check_price_levels.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (r / "scripts" / "fasttier_lock.py").write_text(STUB_FAST_TIER, encoding="utf-8")
    (r / "a.txt").write_text("a\n", encoding="utf-8")
    git(r, "add", "-A")
    git(r, "commit", "-q", "--no-verify", "-m", "init")
    install_hooks(r)
    return r


def stage_change(r: Path, text: str = "change") -> None:
    with (r / "a.txt").open("a", encoding="utf-8") as f:
        f.write(text + "\n")
    git(r, "add", "a.txt")


def stub_env(tmp_path: Path, **kw) -> dict:
    return clean_env(STUB_LOG=tmp_path / "stub.log", **kw)


def stub_log(tmp_path: Path) -> list[str]:
    p = tmp_path / "stub.log"
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else []


def wait_for(pred, limit: float = 60.0, step: float = 0.2) -> bool:
    t0 = time.monotonic()
    while time.monotonic() - t0 < limit:
        if pred():
            return True
        time.sleep(step)
    return pred()


def _pid_alive(pid: int) -> bool:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from fasttier_lock import pid_alive
    finally:
        sys.path.pop(0)
    return pid_alive(pid)


def _stub_pid(tmp_path: Path) -> int | None:
    for line in stub_log(tmp_path):
        if line.startswith("start "):
            return int(line.split()[1])
    return None


def _kill_pid(pid: int | None) -> None:
    if not pid:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True, timeout=LIMIT)
    else:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


# ------------------------------------------------------------------------------------------------ pass and fail

@needs_sh
def test_a_passing_fast_tier_commits_and_records_its_verdict(repo, tmp_path):
    stage_change(repo)
    p = git(repo, "commit", "-q", "-m", "pass", env=stub_env(tmp_path, STUB_RC=0), check=False)
    assert p.returncode == 0, p.stdout + p.stderr
    tree = head(repo, "HEAD^{tree}")
    lines = [ln.split("\t") for ln in verdicts(repo).splitlines() if ln.startswith(tree)]
    assert lines, f"no verdict for {tree}: {verdicts(repo)!r}"
    rec = lines[-1]
    assert len(rec) == 4, rec                                     # tree, UTC time, worktree, the pass line
    assert rec[1].endswith("Z") and "T" in rec[1]
    assert Path(rec[2]).resolve() == repo.resolve()
    assert rec[3] == "3 passed in 0.01s"
    assert "NO VERDICT" not in verdicts(repo)
    assert "NO VERDICT" not in p.stderr
    gd = Path(git(repo, "rev-parse", "--absolute-git-dir").stdout.strip())
    assert not (gd / "fasttier-pending").exists(), "the pending marker outlived a finished hook"


@needs_sh
def test_a_failing_fast_tier_refuses_the_commit_and_records_nothing(repo, tmp_path):
    stage_change(repo)
    before = head(repo)
    p = git(repo, "commit", "-q", "-m", "fail", env=stub_env(tmp_path, STUB_RC=1, STUB_SUMMARY="1 failed, 2 passed"),
            check=False)
    assert p.returncode != 0
    assert head(repo) == before
    assert verdicts(repo).strip() == ""


# ------------------------------------------------------------------------------------------------ killed hooks

@needs_timeout
def test_a_hook_killed_by_sigterm_mid_fast_tier_never_commits(repo, tmp_path):
    """The incident: `timeout N git commit` fires while the fast tier runs. The old hook's shell died of SIGTERM, git
    read 0xF00 as exit 0 and wrote the commit (every trial with the re-exec, about half without)."""
    stage_change(repo)
    before = head(repo)
    env = stub_env(tmp_path, STUB_SLEEP=12, STUB_RC=1)
    p = subprocess.run([GIT_SH, "-c", f'"{TIMEOUT}" 4 "{GIT}" commit -q -m killed'], cwd=repo, env=env,
                       capture_output=True, text=True, timeout=LIMIT)
    assert p.returncode == 124, (p.returncode, p.stdout, p.stderr)          # the timeout fired
    pid = _stub_pid(tmp_path)
    try:
        assert pid is not None, "the stub fast tier never started"
        assert head(repo) == before, "a killed hook let the commit through"
        assert verdicts(repo).strip() == ""
        # the hook kills its child rather than orphan it: the stub never reaches its end
        assert wait_for(lambda: not _pid_alive(pid), limit=30), "the fast tier was orphaned, still running"
        assert "end" not in stub_log(tmp_path)
    finally:
        _kill_pid(pid)


def _children(pid: int) -> list[tuple[int, str]]:
    """The direct children of a process: (pid, executable name)."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class PE(ctypes.Structure):
            _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                        ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD),
                        ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                        ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                        ("szExeFile", ctypes.c_wchar * 260)]

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        k32.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
        k32.Process32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PE))
        k32.Process32NextW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PE))
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        snap = k32.CreateToolhelp32Snapshot(0x2, 0)                  # TH32CS_SNAPPROCESS
        out = []
        try:
            e = PE()
            e.dwSize = ctypes.sizeof(PE)
            ok = k32.Process32FirstW(snap, ctypes.byref(e))
            while ok:
                if e.th32ParentProcessID == pid:
                    out.append((int(e.th32ProcessID), e.szExeFile))
                ok = k32.Process32NextW(snap, ctypes.byref(e))
        finally:
            k32.CloseHandle(snap)
        return out
    out = []
    for stat in Path("/proc").glob("[0-9]*/stat"):
        try:
            fields = stat.read_text().rsplit(")", 1)[1].split()
            name = stat.read_text().split("(", 1)[1].rsplit(")", 1)[0]
        except (OSError, IndexError):
            continue
        if int(fields[1]) == pid:
            out.append((int(stat.parent.name), name))
    return out


def _kill_outright(pid: int) -> None:
    """What git sees of a SIGKILLed MSYS shell: the process ends at once, no trap runs, its exit code is 9 << 8 (0x900).
    On Windows the hook's shell is ended with exactly that code (TerminateProcess); elsewhere it gets SIGKILL."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k32.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        h = k32.OpenProcess(0x0001, False, pid)                      # PROCESS_TERMINATE
        assert h, f"cannot open the hook's shell {pid}"
        try:
            assert k32.TerminateProcess(h, 0x900), f"cannot end the hook's shell {pid}"
        finally:
            k32.CloseHandle(h)
    else:
        os.kill(pid, 9)


@needs_sh
@pytest.mark.skipif(not (Path("/proc").exists() or os.name == "nt"), reason="no process table to find the hook's shell")
def test_a_hook_shell_killed_outright_is_refused_by_the_commit_msg_gate(repo, tmp_path):
    """SIGKILL cannot be trapped: the MSYS runtime gives the dead shell 0x900, which git reads as 0. The pre-commit's
    pending marker for this tree, never replaced by a verdict, makes the commit-msg hook refuse.

    The hook's shell is found as git's own child in the process table (an MSYS `/proc` scan, the first form of this
    test, sees no process of a hook nested inside another hook -- as when the fast tier runs this test), and ended the
    way git sees a SIGKILL: at once, with exit code 0x900, its traps not run."""
    stage_change(repo)
    before = head(repo)
    env = stub_env(tmp_path, STUB_SLEEP=12, STUB_RC=1)
    proc = subprocess.Popen([GIT, "commit", "-q", "-m", "killed outright"], cwd=repo, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    pid = None
    try:
        assert wait_for(lambda: _stub_pid(tmp_path) is not None, limit=60), "the stub fast tier never started"
        pid = _stub_pid(tmp_path)
        shells = [c for c, name in _children(proc.pid) if Path(name).stem.lower() in ("sh", "bash")]
        assert len(shells) == 1, f"git's hook shell not found among its children: {_children(proc.pid)}"
        _kill_outright(shells[0])
        out, err = proc.communicate(timeout=LIMIT)
        assert head(repo) == before, f"a hook killed outright let the commit through: {out}{err}"
        assert proc.returncode != 0
        assert "no verdict" in err.lower()
    finally:
        if proc.poll() is None:
            proc.kill()
        _kill_pid(pid)


@needs_sh
def test_a_closed_output_pipe_refuses_rather_than_passes(repo, tmp_path):
    """`git commit | head -1`: the old hook's shell died of SIGPIPE on its next line (0xD00, read as 0) and the commit
    was written although the fast tier failed."""
    stage_change(repo)
    before = head(repo)
    env = stub_env(tmp_path, STUB_SLEEP=2, STUB_RC=1)
    subprocess.run([GIT_SH, "-c", f'"{GIT}" commit -m piped 2>&1 | head -n 1'], cwd=repo, env=env,
                   capture_output=True, text=True, timeout=LIMIT)
    wait_for(lambda: "end" in stub_log(tmp_path), limit=30)
    time.sleep(1)
    assert head(repo) == before, "a broken pipe let the commit through"
    assert verdicts(repo).strip() == ""


# ------------------------------------------------------------------------------------------------ which tree

@pytest.fixture()
def two_trees(repo) -> tuple[Path, Path, Path]:
    """The main tree and two linked worktrees A (branch a) and B (branch b), each with a file of its own staged."""
    a, b = repo.parent / "A", repo.parent / "B"
    git(repo, "worktree", "add", "-q", "-b", "a", str(a))
    git(repo, "worktree", "add", "-q", "-b", "b", str(b))
    for t, name in ((a, "only_a.txt"), (b, "only_b.txt")):
        (t / name).write_text(name + "\n", encoding="utf-8")
        git(t, "add", name)
    return repo, a, b


def _gitdir(tree: Path) -> str:
    return git(tree, "rev-parse", "--absolute-git-dir").stdout.strip()


def _tested_trees(tmp_path: Path) -> list[Path]:
    return [Path(ln.split(" ", 2)[2]).resolve() for ln in stub_log(tmp_path) if ln.startswith("start ")]


@needs_sh
@pytest.mark.parametrize("case", ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_DIR_and_other_WORK_TREE"])
def test_inherited_git_variables_that_cross_two_trees_are_refused(two_trees, tmp_path, case):
    """Committing from A with variables naming B: the old hook let git commit into one tree while it named and tested
    the other (GIT_DIR=B: branch b moved, A's tests ran; GIT_WORK_TREE=B: branch a moved, B's tests ran)."""
    _, a, b = two_trees
    extra = {"GIT_DIR": {"GIT_DIR": _gitdir(b)},
             "GIT_WORK_TREE": {"GIT_WORK_TREE": str(b)},
             "GIT_INDEX_FILE": {"GIT_INDEX_FILE": str(Path(_gitdir(b)) / "index")},
             "GIT_DIR_and_other_WORK_TREE": {"GIT_DIR": _gitdir(b), "GIT_WORK_TREE": str(a)}}[case]
    ha, hb = head(a), head(b)
    env = stub_env(tmp_path, STUB_RC=0)
    env.update(extra)
    p = subprocess.run([GIT, "commit", "-q", "-m", f"crossed {case}"], cwd=a, env=env, capture_output=True,
                       text=True, timeout=LIMIT)
    assert p.returncode != 0, f"a crossed commit was allowed: {p.stdout}{p.stderr}"
    assert (head(a), head(b)) == (ha, hb)
    assert _tested_trees(tmp_path) == [], "the fast tier ran on a tree the commit is not made in"


@needs_sh
def test_consistent_git_variables_are_allowed_and_the_tree_committed_into_is_the_one_named_and_tested(two_trees,
                                                                                                       tmp_path):
    _, a, b = two_trees
    hb = head(b)
    env = stub_env(tmp_path, STUB_RC=0, GIT_DIR=_gitdir(b), GIT_WORK_TREE=str(b))
    p = subprocess.run([GIT, "commit", "-m", "into B from A's shell"], cwd=a, env=env, capture_output=True, text=True,
                       timeout=LIMIT)
    assert p.returncode == 0, p.stdout + p.stderr
    assert head(b) != hb
    assert _tested_trees(tmp_path) == [b.resolve()]
    header = [ln for ln in (p.stdout + p.stderr).splitlines() if "tree = " in ln]      # git sends a hook's stdout to stderr
    assert header and Path(header[0].split("tree = ", 1)[1].split(",")[0].strip()).resolve() == b.resolve()
    tree = head(b, "HEAD^{tree}")
    rec = [ln.split("\t") for ln in verdicts(b).splitlines() if ln.startswith(tree)]
    assert rec and Path(rec[-1][2]).resolve() == b.resolve()


@needs_sh
def test_a_plain_commit_in_a_worktree_names_and_tests_that_worktree(two_trees, tmp_path):
    _, a, b = two_trees
    p = git(b, "commit", "-m", "in B", env=stub_env(tmp_path, STUB_RC=0), check=False)
    assert p.returncode == 0, p.stdout + p.stderr
    assert _tested_trees(tmp_path) == [b.resolve()]
    out = (p.stdout + p.stderr).replace("\\", "/").lower()                 # git sends a hook's stdout to stderr
    assert f"tree = {str(b.resolve()).replace(os.sep, '/')}".lower() in out


# ------------------------------------------------------------------------------------------------ after the commit

@needs_sh
def test_the_post_commit_hook_flags_a_commit_without_a_verdict(repo, tmp_path):
    stage_change(repo)
    p = git(repo, "commit", "-q", "--no-verify", "-m", "unverified", env=stub_env(tmp_path), check=False)
    assert p.returncode == 0, p.stdout + p.stderr                 # post-commit cannot refuse
    sha = head(repo)
    line = f"NO VERDICT main {sha}"
    assert line in verdicts(repo)
    assert line in (common_dir(repo) / "push.log").read_text(encoding="utf-8")
    assert "NO VERDICT" in p.stderr and sha[:7] in p.stderr


@needs_sh
def test_the_post_commit_hook_is_silent_after_a_verified_commit(repo, tmp_path):
    stage_change(repo)
    p = git(repo, "commit", "-q", "-m", "verified", env=stub_env(tmp_path, STUB_RC=0), check=False)
    assert p.returncode == 0
    assert "NO VERDICT" not in p.stderr and "NO VERDICT" not in verdicts(repo)
    push_log = common_dir(repo) / "push.log"
    assert not push_log.exists() or "NO VERDICT" not in push_log.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------------ check_verdicts.py

def _check(repo: Path, *rng: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / "check_verdicts.py"), *rng], cwd=repo, capture_output=True,
                          text=True, timeout=LIMIT, env=clean_env())


def _record(repo: Path, rev: str) -> None:
    tree = head(repo, f"{rev}^{{tree}}")
    with (common_dir(repo) / "fasttier-verdicts.log").open("a", encoding="utf-8") as f:
        f.write(f"{tree}\t2026-11-18T00:00:00Z\t{repo}\t1 passed in 0.01s\n")


def _commit_file(repo: Path, name: str, msg: str) -> str:
    (repo / name).write_text(msg + "\n", encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-q", "--no-verify", "-m", msg)
    return head(repo)


def test_check_verdicts_lists_exactly_the_unverified_commits_and_exempts_clean_merges(repo):
    base = head(repo)
    c1 = _commit_file(repo, "c1.txt", "c1")
    _record(repo, c1)
    c2 = _commit_file(repo, "c2.txt", "c2")                       # no verdict
    git(repo, "checkout", "-q", "-b", "side", base)
    s1 = _commit_file(repo, "s1.txt", "s1")
    _record(repo, s1)
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "--no-verify", "-m", "merge side", "side")
    m = head(repo)
    p = _check(repo, f"{base}..{m}")
    assert p.returncode == 1, p.stdout + p.stderr
    listed = {ln.split()[0] for ln in p.stdout.splitlines() if ln and not ln.startswith(("#", " "))}
    # c2 has no verdict; the merge's first parent c2 is not clean, so the merge is not exempt either
    assert listed == {c2, m}, p.stdout
    # with c2 verified, the merge of two clean parents is exempt and the range is clean
    _record(repo, c2)
    p = _check(repo, f"{base}..{m}")
    assert p.returncode == 0, p.stdout + p.stderr


def test_check_verdicts_exempts_a_merge_whose_other_parent_is_outside_the_range(repo):
    """A worker merging master: master's commits are outside `master..wt/x` (accepted there), so the merge is exempt
    when the branch's own parent is clean."""
    git(repo, "checkout", "-q", "-b", "wt/x")
    w1 = _commit_file(repo, "w1.txt", "w1")
    _record(repo, w1)
    git(repo, "checkout", "-q", "main")
    _commit_file(repo, "m1.txt", "m1")                            # master moves on, no verdict needed here
    git(repo, "checkout", "-q", "wt/x")
    git(repo, "merge", "-q", "--no-ff", "--no-verify", "-m", "merge master", "main")
    p = _check(repo, "main..wt/x")
    assert p.returncode == 0, p.stdout + p.stderr
    w2 = _commit_file(repo, "w2.txt", "w2")
    p = _check(repo, "main..wt/x")
    assert p.returncode == 1 and w2 in p.stdout and p.stdout.count("\n") >= 1


def test_check_verdicts_fails_loudly_on_a_bad_range(repo):
    p = _check(repo, "no-such-ref..HEAD")
    assert p.returncode == 2 and p.stderr


# ------------------------------------------------------------------------------------------------ the wiring

def test_the_pre_commit_hook_has_no_re_exec_and_traps_its_signals():
    text = (SCRIPTS / "pre-commit").read_text(encoding="utf-8")
    code = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert not any(ln.startswith("exec ") for ln in code), "a re-exec puts a stub between git and the hook"
    for sig in ("HUP", "INT", "TERM"):
        assert any(ln.startswith("trap ") and ln.endswith(f" {sig}") for ln in code), f"SIG{sig} is not trapped"
    assert "trap '' PIPE" in code
    # the trees are resolved before the inherited variables are cleared
    assert text.index("--absolute-git-dir") < text.index("unset GIT_INDEX_FILE")
    assert text.index("git write-tree") < text.index("unset GIT_INDEX_FILE")


def test_every_git_hook_is_installed_and_kept_lf():
    sys.path.insert(0, str(SCRIPTS))
    try:
        import install_hooks
    finally:
        sys.path.pop(0)
    assert tuple(install_hooks.HOOKS) == HOOK_NAMES
    attrs = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    for name in HOOK_NAMES:
        assert b"\r\n" not in (SCRIPTS / name).read_bytes(), f"scripts/{name} has CRLF"
        assert f"scripts/{name} text eol=lf" in attrs
