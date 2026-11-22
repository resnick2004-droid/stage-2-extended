"""The fast tier in parallel inside its one slot (Q-193): pytest-xdist with n workers chosen from free memory.

    python scripts/fasttier_lock.py run -- python scripts/fasttier_xdist.py --work <dir> -m "not slow and not heavy"

The pre-commit hook runs this as the command of the fast-tier lock (`scripts/fasttier_lock.py run`), so it starts the
moment the hook holds its slot and the lock's own memory wait has passed. **What it runs is the same selection as
before** -- `python -m pytest -o addopts= -q -m "<the hook's selection>"`, nothing added that selects or deselects --
only spread over n processes.

1. **n from memory** (`choose_workers`, a pure function): available physical memory at this moment, less RESERVE_GB,
   divided by PER_WORKER_GB (a worker's measured peak with a margin; MEASURE_SOURCE), floored, between 1 and
   MAX_WORKERS. `S2X_FASTTIER_WORKERS` caps it (1, or 0, turns parallel runs off). Without pytest-xdist, or with
   memory unknown, n = 1. **Slots and workers share one memory** (Q-174's slots): the reserve of every other slot
   running now, at its own workers (`fasttier_lock.slot_reserve_gb`: the serial tier's SLOT_RESERVE_GB plus
   PER_WORKER_GB a further worker), comes off the memory first, and the n chosen is written into this run's slot
   record before any worker starts, so the lock admits a later slot only beside this slot's reserve at n. (`--workers`
   sets n outright, for tests and diagnosis; the hook never passes it.)
2. **n = 1 runs exactly as today**: the one command `python -m pytest -o addopts= -q -m "<selection>"`, its output
   and exit code unchanged (its own pass line is the verdict's).
3. **n >= 2** runs three pytest commands, each with the recording plugin `extended.fasttier_report`, which selects
   nothing:
   a. **the serial collection** (`--collect-only`): the node ids a serial run would run -- the count to match;
   b. **the parallel run** (`-n <n> --dist loadfile`: a test file stays on one worker, in its own order, so a file's
      module-scoped state is what it is serially); its node ids must equal the serial collection's, one outcome each;
      otherwise the run is REFUSED (a changed count);
   c. **the serial rerun of the tests that failed in parallel**, and only those -- their node ids as arguments (read
      from a file, `@<file>`), with the same `-m` -- Q-193's `--lf`, but named exactly rather than read from a cache another
      run could have changed. Its collection must be exactly those tests.
   The run passes only if every test passed (or skipped, xfailed) in parallel or in the serial rerun. A test that
   failed in parallel and passed serially is an **ISOLATION DEFECT**: it passes the commit, and it is named in the
   verdict line, never hidden. Any other exit (an interrupted run, a usage or internal error, a collection error, a
   test still failing serially) fails.
4. **The verdict line**, printed last (the hook's verdict keeps the last line holding "<k> passed"): the selection's
   count, the passed count over both runs, n, and every test that needed the serial rerun.

Exit codes: 0 pass; 1 a test failed (also serially); 2 refused (a count that differs from the serial collection's, a
collection error, an unreadable report, an interrupted or broken pytest run).

The work files (each run's report and log, the rerun's arguments) go to `--work` (the hook gives
`<git-dir>/fasttier-xdist`, this tree's own); without it, a fresh temporary folder. After the parallel run one line
gives its sampled memory (the tree's peak working set, the largest worker's, the controller's), the figure to check
PER_WORKER_GB against on the whole tier. On Windows the runner puts itself in a kill-on-close job object, so a kill of
the runner by the lock's wrapper ends its pytest and every worker with it.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_lock import available_gb  # noqa: E402
import fasttier_lock as L  # noqa: E402  (the slots, and the one accounting of a slot's memory: L.slot_reserve_gb)

#: the declared bounds (Q-193); see MEASURE_SOURCE for where the two memory figures come from
MAX_WORKERS = 4
#: a worker's peak with a margin, declared once in the lock (L.PER_WORKER_GB), which counts a running slot's reserve by
#: its workers with it: n workers start only while available >= RESERVE_GB + (the reserves of the slots running beside)
#: + n * PER_WORKER_GB
PER_WORKER_GB = L.PER_WORKER_GB
#: what is left to the rest of the machine: the fast-tier lock's own floor (fasttier_lock.MIN_FREE_GB)
RESERVE_GB = 1.5
#: the measurement records, committed beside the code (tests/test_fasttier_xdist.py checks PER_WORKER_GB against them)
MEASURE_DIR = "docs/measurements/q193_xdist"
MARGIN = 1.25
MEASURE_SOURCE = (
    "scripts/xdist_measure.py on two slices of the fast tier, 2026-11-20 (records in docs/measurements/q193_xdist, "
    "matrix in run_matrix.sh): slice A, 8 tooling files (hooks, locks, run_clean; 179 tests), and slice B, 10 engine "
    "and reading files (cl_build, rd01_reading, family_o_runner, family_stats, replay_records, ...; 273 selected), "
    "each serially and at n = 2, 3, 4 under --dist loadfile and --dist load, one sample a second over every process "
    "of the run, aborted below 2 GB available or beside run.lock. PER_WORKER_GB is the largest worker subtree's peak "
    "working set over every completed run (each worker with the tests' own subprocesses under it) times MARGIN, "
    "rounded up to 0.1 GB; RESERVE_GB is the lock's floor. A slice is not the whole tier: the hook's own runs print "
    "the whole tier's peaks (the `memory:` line) for the figure to be checked against."
)
DIST = "loadfile"
ENV_WORKERS = "S2X_FASTTIER_WORKERS"
PLUGIN = "extended.fasttier_report"
REPORT_OPTION = "--s2x-report"
#: the base of every pytest command: the hook's own (`-o addopts=` clears the project's `-q`, which would compound)
BASE = ("-m", "pytest", "-o", "addopts=", "-q")
#: how many rerun node ids the verdict line names before it says how many more (the full list is in the work folder)
NAME_AT_MOST = 40

EXIT_PASS, EXIT_FAILED, EXIT_REFUSED = 0, 1, 2
#: the files a run writes in its work folder (removed at its start, so a report is never a previous run's)
WORK_FILES = ("collect.json", "collect.log", "parallel.json", "parallel.log", "rerun.txt", "rerun.json", "rerun.log",
              "verdict.json")
BAD = ("failed", "error")


# ------------------------------------------------------------------------------------------------ n from memory

def choose_workers(available: float | None, per_worker_gb: float = PER_WORKER_GB, reserve_gb: float = RESERVE_GB,
                   max_workers: int = MAX_WORKERS, cap: int | None = None, beside_gb: float = 0.0) -> int:
    """How many xdist workers the fast tier runs with, from the memory available when it takes its slot (GB).

    floor((available - reserve_gb - beside_gb) / per_worker_gb), never below 1 (one is always allowed: it is today's
    run, which the lock's own admission already let in) nor above `max_workers` or `cap`. `beside_gb`: the reserves
    of the other slots running now, each at its own workers (L.slot_reserve_gb), so a slot and the slots beside it are
    never counted apart. Unknown, non-finite or negative memory, or a nonsensical figure, gives 1."""
    if available is None or not isinstance(available, (int, float)) or not math.isfinite(available):
        return 1
    if not (per_worker_gb > 0) or not math.isfinite(per_worker_gb) or not math.isfinite(reserve_gb):
        return 1
    if not isinstance(beside_gb, (int, float)) or not math.isfinite(beside_gb) or beside_gb < 0:
        return 1
    n = math.floor((available - reserve_gb - beside_gb) / per_worker_gb)
    top = max(1, int(max_workers))
    if cap is not None:
        top = min(top, max(1, int(cap)))
    return max(1, min(n, top))


def cap_from_env(env: dict | None = None) -> int | None:
    """`S2X_FASTTIER_WORKERS` as a cap: an integer, 0 or less read as 1 (parallel runs off); None when unset or
    unreadable (no cap but memory's)."""
    raw = (os.environ if env is None else env).get(ENV_WORKERS, "").strip()
    try:
        v = int(raw)
    except ValueError:
        return None
    return max(1, v)


def xdist_available() -> bool:
    return importlib.util.find_spec("xdist") is not None


# ------------------------------------------------------------------------------------------------ the commands

def serial_command(selection: str, python: str = sys.executable) -> list[str]:
    """Today's fast tier, exactly."""
    return [python, *BASE, "-m", selection]


def collect_command(selection: str, report: Path, python: str = sys.executable) -> list[str]:
    return [*serial_command(selection, python), "--collect-only", "-p", PLUGIN, REPORT_OPTION, str(report)]


def parallel_command(selection: str, n: int, report: Path, python: str = sys.executable) -> list[str]:
    return [*serial_command(selection, python), "-n", str(n), "--dist", DIST, "-p", PLUGIN, REPORT_OPTION,
            str(report)]


def preflight_command(selection: str, files: Path, python: str = sys.executable) -> list[str]:
    """Q-209's pre-flight: the serial command over the files listed in `files` (pytest's @file), the same selection."""
    return [python, *BASE, "-m", selection, "-p", "no:cacheprovider", f"@{files}"]


def rerun_command(selection: str, args_file: Path, report: Path, python: str = sys.executable) -> list[str]:
    return [*serial_command(selection, python), "-p", PLUGIN, REPORT_OPTION, str(report), f"@{args_file}"]


# ------------------------------------------------------------------------------------------------ the rule

@dataclass
class Verdict:
    """The outcome of the parallel run and its rerun, judged by `judge`."""
    code: int
    line: str
    selected: int = 0
    passed: int = 0
    rerun: list[str] = field(default_factory=list)          # failed in parallel, rerun serially
    defects: list[str] = field(default_factory=list)        # failed in parallel, passed serially
    still_failing: list[str] = field(default_factory=list)  # failed serially too
    problems: list[str] = field(default_factory=list)


def _counts(outcomes: dict[str, str], ids: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for nid in ids:
        o = outcomes.get(nid, "missing")
        out[o] = out.get(o, 0) + 1
    return out


def check_same_tests(expected: list[str], report: dict, what: str) -> list[str]:
    """Why `report` (a run's recorded collection and outcomes) does not hold exactly the tests `expected` -- each once,
    each with one outcome -- or [] when it does."""
    problems: list[str] = []
    if len(set(expected)) != len(expected):
        problems.append(f"the serial collection names {len(expected) - len(set(expected))} node id(s) twice")
    if report.get("collect_errors"):
        problems.append(f"{what}: {len(report['collect_errors'])} collection error(s): "
                        f"{', '.join(report['collect_errors'][:5])}")
    if report.get("workers_agree") is False:
        problems.append(f"{what}: the xdist workers collected different tests ({report.get('worker_collections')})")
    got = list(report.get("collected") or [])
    outcomes = report.get("outcomes") or {}
    want = set(expected)
    if len(got) != len(expected) or set(got) != want:
        problems.append(f"{what}: collected {len(got)} test(s), the serial collection {len(expected)} "
                        f"({len(want - set(got))} missing, {len(set(got) - want)} extra)")
    if set(outcomes) != want:
        problems.append(f"{what}: outcomes for {len(outcomes)} test(s), the serial collection holds {len(expected)} "
                        f"({len(want - set(outcomes))} without an outcome, {len(set(outcomes) - want)} not in it)")
    return problems


def _names(ids: list[str]) -> str:
    shown = ", ".join(ids[:NAME_AT_MOST])
    return shown + (f" and {len(ids) - NAME_AT_MOST} more" if len(ids) > NAME_AT_MOST else "")


def _summary(counts: dict[str, int]) -> str:
    order = ("passed", "skipped", "xfailed", "xpassed", "failed", "error")
    return ", ".join(f"{counts[k]} {k}" for k in order if counts.get(k))


def judge(expected: list[str], parallel: dict | None, rerun: dict | None, n: int, seconds: float = 0.0) -> Verdict:
    """The rule (Q-193). `expected`: the serial collection's node ids; `parallel`: the parallel run's report;
    `rerun`: the serial rerun's report, or None when there was none. A pure function of the three.

    Pass only if the parallel run holds exactly the expected tests, each with one outcome, and every one that failed
    there (failed or error) was rerun serially -- exactly those, and nothing else -- and passed. A changed count, a
    collection error, an exit status that is not a plain pass or a plain test failure, or a failed rerun fails."""
    v = Verdict(code=EXIT_REFUSED, line="", selected=len(expected))
    tag = f"xdist n={n}, --dist {DIST}"
    if parallel is None:
        v.problems.append("the parallel run wrote no report")
    else:
        v.problems += check_same_tests(expected, parallel, "the parallel run")
    if v.problems:
        v.line = f"fast tier REFUSED ({tag}): " + "; ".join(v.problems)
        return v
    po = parallel["outcomes"]
    v.rerun = [nid for nid in expected if po[nid] in BAD]
    status = parallel.get("exitstatus")
    if not v.rerun:
        if status != 0:
            v.problems.append(f"the parallel run exited {status} with no test failed")
            v.line = f"fast tier REFUSED ({tag}): " + "; ".join(v.problems)
            return v
        counts = _counts(po, expected)
        v.passed = counts.get("passed", 0)
        v.code = EXIT_PASS
        v.line = (f"fast tier: {v.passed} passed of {len(expected)} selected ({_summary(counts)}; the serial "
                  f"collection's {len(expected)}, matched; {tag}; no serial rerun; {seconds:.0f} s)")
        return v
    if status != 1:
        v.problems.append(f"the parallel run exited {status} (a test failure exits 1)")
    if rerun is None:
        v.problems.append(f"{len(v.rerun)} test(s) failed in parallel and no serial rerun report was written")
    else:
        v.problems += check_same_tests(v.rerun, rerun, "the serial rerun")
    if v.problems:
        v.line = f"fast tier REFUSED ({tag}): " + "; ".join(v.problems)
        return v
    ro = rerun["outcomes"]
    v.still_failing = [nid for nid in v.rerun if ro[nid] in BAD]
    v.defects = [nid for nid in v.rerun if ro[nid] not in BAD]
    final = {nid: (ro[nid] if nid in ro else po[nid]) for nid in expected}
    counts = _counts(final, expected)
    v.passed = counts.get("passed", 0)
    if v.still_failing or rerun.get("exitstatus") != 0:
        v.code = EXIT_FAILED
        v.line = (f"fast tier FAILED ({tag}): {len(v.still_failing)} test(s) failed in parallel and again in the "
                  f"serial rerun: {_names(v.still_failing)}"
                  + ("" if v.still_failing else f"; the serial rerun exited {rerun.get('exitstatus')}"))
        return v
    v.code = EXIT_PASS
    v.line = (f"fast tier: {v.passed} passed of {len(expected)} selected ({_summary(counts)}; the serial "
              f"collection's {len(expected)}, matched; {tag}; serial rerun of {len(v.rerun)}: ISOLATION DEFECT, "
              f"passed only serially, to fix: {_names(v.defects)}; {seconds:.0f} s)")
    return v


# ------------------------------------------------------------------------------------------------ running

def _say(msg: str) -> None:
    print(f"fasttier_xdist: {msg}", flush=True)


def _run(cmd: list[str], log: Path | None = None) -> int:
    """Run a pytest command, its output to this process's stdout (the lock's tee copies it to the hook's log) and, with
    `log`, to that file too. A child is killed if this process is interrupted."""
    if log is None:
        return subprocess.run(cmd).returncode
    with open(log, "wb") as f:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            out = sys.stdout.buffer
            for chunk in iter(lambda: proc.stdout.read1(65536), b""):
                f.write(chunk)
                out.write(chunk)
                out.flush()
            return proc.wait()
        except BaseException:
            proc.kill()
            proc.wait()
            raise


def _read(path: Path) -> dict | None:
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return rec if isinstance(rec, dict) else None


class _PeakWatch:
    """Samples the parallel run's process tree every few seconds (scripts/xdist_measure.py's reading), for one line at
    the end: the tree's peak working set and the largest worker's -- the figure PER_WORKER_GB is checked against."""

    def __init__(self, every: float = 2.0) -> None:
        self.every = every
        self.pid: int | None = None
        self.stop = threading.Event()
        self.peaks = None
        try:
            import xdist_measure as XM
            self.XM = XM
            self.peaks = XM.Peaks()
        except Exception:                                   # noqa: BLE001 -- a reading, never a reason to fail
            self.XM = None

    def loop(self) -> None:
        while not self.stop.wait(self.every):
            if self.pid is None or self.XM is None:
                continue
            try:
                s = self.XM.snapshot()
                if s is not None:
                    self.peaks.add(self.XM.tree_reading(self.pid, *s))
            except Exception:                               # noqa: BLE001
                pass

    def line(self) -> str | None:
        if self.peaks is None or not self.peaks.samples:
            return None
        r = self.peaks.record()
        return (f"memory: peak tree working set {r['peak_tree_working_set_gb']} GB, largest worker "
                f"{r['peak_worker_gb']} GB, controller {r['peak_controller_gb']} GB ({r['samples']} samples)")


def _run_parallel(cmd: list[str], log: Path) -> int:
    watch = _PeakWatch()
    t = threading.Thread(target=watch.loop, daemon=True)
    with open(log, "wb") as f:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        watch.pid = proc.pid
        t.start()
        try:
            out = sys.stdout.buffer
            for chunk in iter(lambda: proc.stdout.read1(65536), b""):
                f.write(chunk)
                out.write(chunk)
                out.flush()
            rc = proc.wait()
        except BaseException:
            proc.kill()
            proc.wait()
            raise
        finally:
            watch.stop.set()
    line = watch.line()
    if line:
        _say(line)
    return rc


def fast_tiers_beside(env: dict | None = None, lock: Path | None = None) -> list[int]:
    """The other fast tiers holding a slot of the machine's fast-tier lock now (Q-174), each as its xdist workers
    (L.workers_of: 1 for a serial tier) -- this run's own slot (the token in S2X_FASTTIER_TOKEN) and stale holders not
    counted. [] when the lock cannot be read."""
    env = os.environ if env is None else env
    try:
        lock = L.default_lock_path() if lock is None else lock
        mine = env.get(L.ENV_TOKEN)
        out = []
        for sp in L._slot_files(lock, L.MAX_SLOTS):
            raw = L._read_raw(sp)
            rec = L._parse(raw) if raw else None
            if rec is None or rec.get("token") == mine or L.stale_reason(sp, raw) is not None:
                continue
            out.append(L.workers_of(rec))
        return out
    except (OSError, SystemExit, ValueError):
        return []


def record_own_workers(n: int, env: dict | None = None, lock: Path | None = None) -> bool:
    """Write n into this run's own slot record (L.record_workers), before any worker starts, so a slot admitted later
    counts this one at its n. False outside a slot (no token) or if the record cannot be written."""
    env = os.environ if env is None else env
    token = env.get(L.ENV_TOKEN)
    if not token:
        return False
    try:
        return L.record_workers(L.default_lock_path() if lock is None else lock, token, n) is not None
    except (OSError, SystemExit, ValueError):
        return False


def run(selection: str, work: Path, available: float | None, cap: int | None, python: str = sys.executable,
        has_xdist: bool | None = None, force: int | None = None, beside: list[int] | None = None,
        record=None, preflight: Path | None = None) -> int:
    """The fast tier at `selection`; its exit code. `force` (the `--workers` option: tests and diagnosis, never the
    hook) sets n outright, 1 to MAX_WORKERS. `beside`: the other slots running now, as their workers; their reserves
    (L.slot_reserve_gb) come off the memory before n is chosen. `record(n)` is called with the n chosen, before any
    pytest starts (main: this run's slot record). `preflight` (Q-209, E-274): a file of test files run first, serially,
    in this slot -- a failure returns its exit code and the full fast tier never starts; on a pass the full tier runs
    exactly as without it."""
    if preflight is not None:
        _say(f"the pre-flight: {preflight} (the always-on guards and the nearest tests), serially, before the full "
             f"fast tier")
        rc = _run(preflight_command(selection, preflight, python))
        if rc != 0:
            _say(f"pre-flight FAILED (exit {rc}): the full fast tier did not start")
            return rc
        _say("pre-flight passed; the full fast tier follows")
    beside = list(beside or [])
    beside_gb = sum(L.slot_reserve_gb(w) for w in beside)
    has_xdist = xdist_available() if has_xdist is None else has_xdist
    mem = "memory unknown" if available is None else f"{available:.1f} GB available"
    if not has_xdist:
        n, why = 1, "pytest-xdist is not installed"
    elif force is not None:
        n = max(1, min(int(force), MAX_WORKERS))
        why = f"set by --workers; {mem}"
    else:
        n = choose_workers(available, cap=cap, beside_gb=beside_gb)
        why = (f"{mem}; {RESERVE_GB} GB reserve + {PER_WORKER_GB} GB a worker, at most {MAX_WORKERS}"
               + (f"; {beside_gb:.1f} GB reserved for {len(beside)} slot(s) running beside ({beside} workers)"
                  if beside else "")
               + (f", capped at {cap} by {ENV_WORKERS}" if cap is not None else ""))
    if record is not None:
        record(n)
    if n == 1:
        _say(f"n = 1 ({why}): the fast tier runs serially, as before")
        return _run(serial_command(selection, python))
    t0 = time.monotonic()
    work.mkdir(parents=True, exist_ok=True)
    for name in WORK_FILES:                                 # only this runner's own files, never the folder
        (work / name).unlink(missing_ok=True)
    _say(f"n = {n} ({why}); work files in {work}")
    _say("the serial collection (the count the parallel run must match)")
    rc = _run(collect_command(selection, work / "collect.json", python), work / "collect.log")
    collected = _read(work / "collect.json")
    if rc != 0 or collected is None or collected.get("collect_errors"):
        _say(f"fast tier REFUSED: the serial collection exited {rc}"
             + ("" if collected is None else f" with {len(collected.get('collect_errors') or [])} collection error(s)")
             + f"; see {work / 'collect.log'}")
        return EXIT_REFUSED
    expected = list(collected.get("collected") or [])
    _say(f"the serial collection: {len(expected)} tests; the parallel run follows")
    _run_parallel(parallel_command(selection, n, work / "parallel.json", python), work / "parallel.log")
    parallel = _read(work / "parallel.json")
    rerun = None
    if parallel is not None and not check_same_tests(expected, parallel, "the parallel run"):
        failed = [nid for nid in expected if parallel["outcomes"][nid] in BAD]
        if failed and parallel.get("exitstatus") == 1:
            (work / "rerun.txt").write_text("".join(f"{nid}\n" for nid in failed), encoding="utf-8", newline="\n")
            _say(f"{len(failed)} test(s) failed in parallel; rerunning only those, serially: {_names(failed)}")
            _run(rerun_command(selection, work / "rerun.txt", work / "rerun.json", python), work / "rerun.log")
            rerun = _read(work / "rerun.json")
    v = judge(expected, parallel, rerun, n, time.monotonic() - t0)
    (work / "verdict.json").write_text(json.dumps(v.__dict__, indent=1), encoding="utf-8")
    print(v.line, flush=True)                              # last: the hook's verdict keeps this line
    return v.code


def join_kill_on_close_job() -> bool:
    """Windows: put this process in a new job object that kills every process in it when its last handle closes --
    this process's own, at its exit, however it ends. Every child started afterwards (pytest, the xdist workers, the
    tests' own subprocesses) is in the job, so `fasttier_lock.py`'s kill of this runner (TerminateProcess, which no
    handler sees) ends the whole run instead of leaving its workers running after the slot is released. False -- the
    run goes on without it -- off Windows or if the job cannot be made."""
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes

    class BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class IOC(ctypes.Structure):
        _fields_ = [(k, ctypes.c_uint64) for k in ("r", "w", "o", "rb", "wb", "ob")]

    class EXTENDED(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BASIC), ("IoInfo", IOC), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
    k32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
    k32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    job = k32.CreateJobObjectW(None, None)
    if not job:
        return False
    info = EXTENDED()
    info.BasicLimitInformation.LimitFlags = 0x2000          # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):  # ExtendedLimitInformation
        return False
    if not k32.AssignProcessToJobObject(job, k32.GetCurrentProcess()):
        return False
    global _JOB                                             # held open for the life of this process, never closed
    _JOB = job
    return True


_JOB = None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-m", dest="selection", required=True, help='the fast tier\'s selection, "not slow and not heavy"')
    ap.add_argument("--work", type=Path, default=None, help="the folder for each run's report and log")
    ap.add_argument("--workers", type=int, default=None,
                    help=f"n outright, 1 to {MAX_WORKERS} (tests and diagnosis; the hook never passes it)")
    ap.add_argument("--preflight", type=Path, default=None,
                    help="test files (one per line) run first, serially; a failure stops before the full tier (Q-209)")
    a = ap.parse_args(argv)
    if a.preflight is not None and (not a.preflight.is_file() or not a.preflight.read_text(encoding="utf-8").strip()):
        _say(f"fast tier REFUSED: the pre-flight file {a.preflight} is missing or empty")
        return EXIT_REFUSED
    if not join_kill_on_close_job():
        _say("no kill-on-close job (not Windows, or refused): a killed runner may leave its pytest running")
    work = a.work if a.work is not None else Path(tempfile.mkdtemp(prefix="s2x-fasttier-xdist-"))
    return run(a.selection, work, available_gb(), cap_from_env(), force=a.workers, beside=fast_tiers_beside(),
               record=record_own_workers, preflight=a.preflight)


if __name__ == "__main__":
    raise SystemExit(main())
