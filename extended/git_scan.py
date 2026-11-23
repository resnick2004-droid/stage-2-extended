"""A time limit on every `git grep` (and `git log -S`) the suite runs (Q-156, under the operator's standing rule E-207).

**Why.** A pre-commit fast tier hung for about six hours on one child process, `git grep -n -I -w -E <pattern> <22
refs> --` (Q-108's literal seed scan, reached through `tests/test_q108_calibrate.py`), its CPU time flat: blocked, not
working. Another worker had seen the same test stall for two hours. A plain `subprocess.run` without a limit waits for
ever; with one it still can, on Windows: on its timeout it kills the direct child only and then waits, without a limit,
for the output pipes to close -- and a descendant holding them keeps them open.

**What this module does.** `run(argv, ...)` runs one command with its output captured and its input closed (or the
`input` given), and a limit, `GIT_SCAN_TIMEOUT_S` seconds per call (300; a caller may pass a shorter one). On the limit
it kills **the whole process tree** -- on Windows the process's job object (the command is put in its own job as it
starts) and `taskkill /F /T` on its pid; elsewhere its own session's process group -- waits at most `DRAIN_S` more for
the pipes, and raises `ScanTimeout` naming the command. **A timeout is never read as "no match"**: it raises, so a seed
check fails loudly instead of passing. Every other outcome is exactly the plain command's: the same exit code, output and
error text (`CompletedProcess`), for the caller to read as it did (a `git grep` exits 0 on a match, 1 on none, other
codes on a failure).

`grep_refs(repo, grep_args, refs)` is the all-refs scan with less work: each distinct object the refs name is grepped
once (a branch and its remote copy usually name the same commit), at most 40 per call, and every hit is reported under
every ref naming that object -- the same (ref, rest-of-line) pairs as grepping the ref names, in one fewer pass per
duplicate. Measured on a synthetic repository (Q-156's hand-back): the work falls with the share of duplicate refs;
`--threads=1` or `=2` changed nothing measurable, and one ref per call was slower.

**The pinned scripts.** `scripts/q108_calibrate.py` and `scripts/q82_validation.py` hold their own seed scans, and
their files are pinned by blob (Q-126's `VALIDATED_BLOBS`; Q-108's validation manifests) -- edited only under a re-pin
(Q-211: Q-108's literal scan asks `git grep -l`, file names only, re-pinned by the lead's ruling). Their tests
route them here without touching them: `route_scans(monkeypatch, module)` replaces the `subprocess` name of the module
and of every repository module it imports (to depth) with `PROXY`, which sends a scan (`is_scan`) through `run` and
everything else to `subprocess` itself. Their own runs outside the tests keep the plain call.

Pure standard library (`ctypes` on Windows); importing it touches nothing.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import types
from pathlib import Path
from typing import Iterable, Sequence

#: the limit of one scan, in seconds (Q-156's brief); a caller may pass a shorter one, never a longer by default
GIT_SCAN_TIMEOUT_S = 300
#: after the kill, how long the pipes are waited for before they are abandoned
DRAIN_S = 10
#: refs (distinct objects) per `git grep` call, as the existing scans batch them
BATCH = 40

_WINDOWS = os.name == "nt"
_REPO = Path(__file__).resolve().parent.parent


class ScanTimeout(RuntimeError):
    """A command passed its limit; its process tree was killed. Never a "no match"."""

    def __init__(self, argv: Sequence[str], timeout: float, pid: int | None, cwd=None):
        self.argv, self.timeout, self.pid, self.cwd = list(argv), timeout, pid, cwd
        cmd = subprocess.list2cmdline([str(a) for a in self.argv])
        super().__init__(f"timed out after {timeout:g} s and its process tree was killed (never read as 'no match'): "
                         f"{cmd} (in {cwd or os.getcwd()})")


# ------------------------------------------------------------------------------------------------ processes (Windows)


def _k32():
    import ctypes

    return ctypes.WinDLL("kernel32", use_last_error=True)


def _new_job(handle) -> int | None:
    """A fresh job object holding the process `handle` (its children started after this join it); None on failure."""
    try:
        import ctypes
        from ctypes import wintypes

        k32 = _k32()
        k32.CreateJobObjectW.restype = wintypes.HANDLE
        k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        k32.AssignProcessToJobObject.restype = wintypes.BOOL
        job = k32.CreateJobObjectW(None, None)
        if not job:
            return None
        if not k32.AssignProcessToJobObject(job, int(handle)):
            _close(job)
            return None
        return job
    except Exception:                                   # noqa: BLE001 -- taskkill /T stays the fallback
        return None


def _terminate_job(job) -> None:
    try:
        from ctypes import wintypes

        k32 = _k32()
        k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        k32.TerminateJobObject(job, 1)
    except Exception:                                   # noqa: BLE001
        pass


def _close(handle) -> None:
    try:
        from ctypes import wintypes

        k32 = _k32()
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle(handle)
    except Exception:                                   # noqa: BLE001
        pass


def pid_alive(pid: int) -> bool:
    """Whether process `pid` is still running."""
    if _WINDOWS:
        import ctypes
        from ctypes import wintypes

        k32 = _k32()
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k32.WaitForSingleObject.restype = wintypes.DWORD
        h = k32.OpenProcess(0x00100000 | 0x1000, False, int(pid))    # SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5                     # access denied: it exists
        try:
            return k32.WaitForSingleObject(h, 0) == 0x102           # WAIT_TIMEOUT: still running
        finally:
            _close(h)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:                                                            # a zombie child of ours counts as ended
        done, _ = os.waitpid(pid, os.WNOHANG)
        return done == 0
    except ChildProcessError:
        return True


def kill_tree(pid: int, job=None) -> None:
    """Kill process `pid` and every descendant: `taskkill /F /T` while the tree is linked, then its job (any orphan
    whose parent already ended); elsewhere its process group (`run` starts it in its own session)."""
    if _WINDOWS:
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60, check=False)
        except (OSError, subprocess.SubprocessError):
            pass                                        # the job below still ends the tree
        if job is not None:
            _terminate_job(job)
        return
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


# ------------------------------------------------------------------------------------------------ the helper


def run(argv: Sequence[str], *, cwd=None, env=None, input=None, text: bool = False, encoding: str | None = None,
        errors: str | None = None, timeout: float | None = None) -> subprocess.CompletedProcess:
    """`subprocess.run(argv, capture_output=True, ...)` with a limit (`GIT_SCAN_TIMEOUT_S` unless `timeout` is given)
    and the input closed unless `input` is given; on the limit the process tree is killed and `ScanTimeout` raised."""
    limit = GIT_SCAN_TIMEOUT_S if timeout is None else timeout
    argv = [os.fspath(a) for a in argv]
    kw: dict = {"cwd": cwd, "env": env, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE,
                "stdin": subprocess.PIPE if input is not None else subprocess.DEVNULL,
                "text": text, "encoding": encoding, "errors": errors}
    if not _WINDOWS:
        kw["start_new_session"] = True
    proc = subprocess.Popen(argv, **kw)
    job = _new_job(proc._handle) if _WINDOWS else None      # noqa: SLF001 -- the process handle Popen holds
    try:
        try:
            out, err = proc.communicate(input=input, timeout=limit)
        except subprocess.TimeoutExpired:
            kill_tree(proc.pid, job)
            proc.kill()
            try:
                proc.communicate(timeout=DRAIN_S)
            except subprocess.TimeoutExpired:
                for f in (proc.stdout, proc.stderr, proc.stdin):
                    try:
                        if f:
                            f.close()
                    except OSError:
                        pass
            raise ScanTimeout(argv, limit, proc.pid, cwd) from None
        except BaseException:                           # an interrupt: never leave the tree running
            kill_tree(proc.pid, job)
            proc.kill()
            raise
    finally:
        if job is not None:
            _close(job)
    return subprocess.CompletedProcess(argv, proc.returncode, out, err)


def git(*args: str, cwd=None, **kw) -> subprocess.CompletedProcess:
    """`run(["git", *args], ...)`."""
    return run(["git", *args], cwd=cwd, **kw)


def grep_refs(repo, grep_args: Sequence[str], refs: Sequence[str], *, text: bool = True, encoding: str | None = None,
              errors: str | None = None, timeout: float | None = None) -> list[tuple[str, str]]:
    """`git grep <grep_args> <refs> --` as (ref, the rest of each output line) pairs, each distinct object the refs
    name grepped once and its hits given under every ref naming it. Raises `RuntimeError` on a git failure (an exit
    other than 0 or 1) and `ScanTimeout` on the limit -- never an empty answer for either."""
    refs = list(refs)
    if not refs:
        return []
    enc = {"text": text, "encoding": encoding, "errors": errors, "timeout": timeout}
    r = git("rev-parse", *refs, cwd=repo, **enc)
    objs = r.stdout.split() if r.returncode == 0 else []
    if r.returncode or len(objs) != len(refs):
        raise RuntimeError(f"cannot resolve the refs of {repo}: {str(r.stderr).strip()[:200]}")
    named: dict[str, list[str]] = {}
    for ref, obj in zip(refs, objs):
        named.setdefault(obj, []).append(ref)
    order = list(named)
    out: list[tuple[str, str]] = []
    for i in range(0, len(order), BATCH):
        part = order[i:i + BATCH]
        g = git("grep", *grep_args, *part, "--", cwd=repo, **enc)
        if g.returncode not in (0, 1):
            raise RuntimeError(f"git grep failed on {part[:3]}: {str(g.stderr).strip()[:200]}")
        for line in g.stdout.splitlines():
            obj, sep, rest = line.partition(":")
            if not sep or obj not in named:
                continue
            out.extend((ref, rest) for ref in named[obj])
    return out


# ------------------------------------------------------------------------------------------------ routing pinned code


_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def is_scan(argv) -> bool:
    """Whether `argv` is a `git grep`, or a `git log` with a pickaxe (`-S`, `-G`)."""
    if not isinstance(argv, (list, tuple)) or not argv:
        return False
    if Path(str(argv[0])).name.lower() not in ("git", "git.exe"):
        return False
    i = 1
    while i < len(argv) and str(argv[i]).startswith("-"):
        i += 2 if str(argv[i]) in _GLOBAL_WITH_VALUE else 1
    if i >= len(argv):
        return False
    sub, rest = str(argv[i]), [str(a) for a in argv[i + 1:]]
    if sub == "grep":
        return True
    return sub == "log" and any(a.startswith(("-S", "-G", "--pickaxe")) for a in rest)


_RUN_KEYS = {"cwd", "env", "input", "text", "universal_newlines", "encoding", "errors", "timeout", "check",
             "capture_output"}


class _ScanRoutedSubprocess(types.ModuleType):
    """`subprocess`, but a scan's `run` goes through `git_scan.run` (its limit, the tree killed, `ScanTimeout`)."""

    def __getattr__(self, name):
        return getattr(subprocess, name)

    def run(self, args, **kw):                         # noqa: D102
        if not is_scan(args) or not kw.get("capture_output") or set(kw) - _RUN_KEYS:
            return subprocess.run(args, **kw)
        text = bool(kw.get("text") or kw.get("universal_newlines"))
        r = sys.modules[__name__].run(args, cwd=kw.get("cwd"), env=kw.get("env"), input=kw.get("input"), text=text,
                                      encoding=kw.get("encoding"), errors=kw.get("errors"), timeout=kw.get("timeout"))
        if kw.get("check") and r.returncode:
            raise subprocess.CalledProcessError(r.returncode, r.args, r.stdout, r.stderr)
        return r


PROXY = _ScanRoutedSubprocess("subprocess_scan_routed")


def route_scans(monkeypatch, *modules, depth: int = 3) -> list[str]:
    """Point the name `subprocess` of each module given, and of every module of this repository it holds (to `depth`
    levels: Q-126's copy of Q-108's runner holding Q-82's), at `PROXY`, through `monkeypatch` (undone with it).
    Returns the patched modules' names."""
    done: list[str] = []
    seen: set[int] = set()

    def visit(mod, level):
        if id(mod) in seen or level > depth:
            return
        seen.add(id(mod))
        f = getattr(mod, "__file__", None)
        try:
            ours = f is not None and _REPO in Path(f).resolve().parents and "vendor" not in Path(f).resolve().parts
        except (OSError, ValueError):
            ours = False
        if not ours:
            return
        if getattr(mod, "subprocess", None) is subprocess:
            monkeypatch.setattr(mod, "subprocess", PROXY)
            done.append(mod.__name__)
        for v in list(vars(mod).values()):
            if isinstance(v, types.ModuleType) and not isinstance(v, _ScanRoutedSubprocess):
                visit(v, level + 1)

    for m in modules:
        visit(m, 0)
    return done


__all__ = ["GIT_SCAN_TIMEOUT_S", "DRAIN_S", "BATCH", "ScanTimeout", "run", "git", "grep_refs", "is_scan", "PROXY",
           "route_scans", "pid_alive", "kill_tree"]
