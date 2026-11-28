"""Q-187: `extended.procmem.working_set_mb` reads this process's memory without leaving anything behind.

The leak it had (found by the failure protocol on H3-A's slot A2): the counters' structure and its pointer type were
made inside every call, and ctypes keeps every pointer type for the life of the process, so each reading left a class
behind. The positive control is that reader itself, as it was (`_reader_as_it_was`, a planted copy), measured the same
way; the run commit's own file is measured too when git can show it.
"""
from __future__ import annotations

import ctypes
import gc
import math
import subprocess
import sys
import tracemalloc
import types
from pathlib import Path

import pytest

from extended import procmem

ROOT = Path(__file__).resolve().parent.parent
WINDOWS = sys.platform == "win32"
N = 2000
#: the failed run's commit (`scripts/h3a_a2_diag.RUN_COMMIT`), whose `extended/procmem.py` leaked
RUN_COMMIT = "26e1a55f601c7931a41344602028ec84f5628015"


def _reader_as_it_was(peak: bool = False) -> float:
    """The planted defect: the structure built inside every call (the reader before Q-187)."""
    try:
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

        k32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        c = PMC()
        c.cb = ctypes.sizeof(PMC)
        if not psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
            return float("nan")
        return (c.PeakWorkingSetSize if peak else c.WorkingSetSize) / 2**20
    except Exception:                                   # noqa: BLE001
        return float("nan")


def _left_behind(read) -> tuple[int, int]:
    """(bytes still traced, pointer types added) after N readings, after a warm-up and a collection."""
    read()
    read(peak=True)
    gc.collect()
    cache = getattr(ctypes, "_pointer_type_cache", {})
    n0 = len(cache)
    tracemalloc.start()
    try:
        a = tracemalloc.get_traced_memory()[0]
        for i in range(N):
            read(peak=bool(i % 2))
        gc.collect()
        b = tracemalloc.get_traced_memory()[0]
    finally:
        tracemalloc.stop()
    return b - a, len(cache) - n0


@pytest.mark.skipif(not WINDOWS, reason="psapi is Windows'; elsewhere the reader returns NaN")
def test_the_reader_leaves_nothing_behind_and_the_old_reader_did() -> None:
    kept, types_added = _left_behind(procmem.working_set_mb)
    assert types_added == 0 and kept < 64 * 1024
    old_kept, old_types = _left_behind(_reader_as_it_was)
    assert old_types >= N and old_kept > N * 1024          # the planted defect is seen by the same reading


@pytest.mark.skipif(not WINDOWS, reason="psapi is Windows'; elsewhere the reader returns NaN")
def test_the_run_commits_reader_leaked() -> None:
    """The run's own file (git's copy at the run's commit), loaded as a module, leaves a pointer type a call."""
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{RUN_COMMIT}:extended/procmem.py"], capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode:
        pytest.skip("the run's commit is not in this clone")
    mod = types.ModuleType("procmem_at_run_commit")
    exec(compile(r.stdout, "procmem_at_run_commit", "exec"), mod.__dict__)
    kept, added = _left_behind(mod.working_set_mb)
    assert added >= N and kept > N * 1024


@pytest.mark.skipif(not WINDOWS, reason="psapi is Windows'; elsewhere the reader returns NaN")
def test_the_reader_reads_the_same_counters() -> None:
    """The fixed reader and the old one read the same counters: the peak equal (it can only rise, and nothing is
    allocated between the two readings), the current working set positive and at most the peak."""
    for _ in range(3):
        a, b = procmem.working_set_mb(peak=True), _reader_as_it_was(peak=True)
        if a == b:
            break
    assert a == b and a > 0
    cur = procmem.working_set_mb()
    assert 0 < cur <= procmem.working_set_mb(peak=True)


def test_a_failure_reads_nan(monkeypatch) -> None:
    def broken():
        raise OSError("no psapi")
    monkeypatch.setattr(procmem, "_api", broken)
    assert math.isnan(procmem.working_set_mb()) and math.isnan(procmem.working_set_mb(peak=True))
