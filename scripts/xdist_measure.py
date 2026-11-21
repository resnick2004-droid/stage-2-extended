"""Measure a pytest run's memory per xdist worker, with a memory floor that aborts it (Q-193).

    python scripts/xdist_measure.py --out m.json -- python -m pytest -o addopts= -q -n 3 --dist loadfile tests/a.py ...

Every `--every` seconds (default 1) it snapshots the machine's processes and, over the command's process tree, sums the
working set (physical memory in use) of: the whole tree; the command's own process (pytest's controller); and each
**worker subtree** -- every direct child of the command's process with its own descendants (under `-n N` the xdist
workers and the tests' subprocesses under them; without `-n`, a test's subprocesses). It keeps each peak and the lowest
machine-wide available memory (`run_lock.available_gb`, GlobalMemoryStatusEx, the figure Get-Counter's
`\\Memory\\Available MBytes` reads).

**The abort.** If available memory falls below `--floor-gb` (default 2.0) or `run.lock` appears at the main
repository's root (a heavy run started), the command's whole tree is killed and the record says `aborted` and why. A
measurement never competes with a heavy run or pushes the machine below the floor.

The reading is a sample, not a trace: a spike shorter than the interval can be missed, so a reserve derived from it
carries a margin. Windows only (Toolhelp snapshot + GetProcessMemoryInfo); elsewhere the record has no memory.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_lock import available_gb  # noqa: E402

GB = 2 ** 30


def snapshot() -> tuple[dict[int, int], dict[int, int]] | None:
    """(pid -> parent pid, pid -> working set bytes) for every process this user may read; None off Windows."""
    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes

    class PE(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD),
                    ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                    ("szExeFile", ctypes.c_wchar * 260)]

    class PMC(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    k32.Process32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PE))
    k32.Process32NextW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PE))
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    k32.CloseHandle.argtypes = (wintypes.HANDLE,)
    psapi.GetProcessMemoryInfo.argtypes = (wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD)

    parent: dict[int, int] = {}
    snap = k32.CreateToolhelp32Snapshot(0x2, 0)
    try:
        e = PE()
        e.dwSize = ctypes.sizeof(PE)
        ok = k32.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            parent[int(e.th32ProcessID)] = int(e.th32ParentProcessID)
            ok = k32.Process32NextW(snap, ctypes.byref(e))
    finally:
        k32.CloseHandle(snap)
    return parent, _working_sets(parent, k32, psapi, PMC)


def _working_sets(parent, k32, psapi, PMC) -> dict[int, int]:
    import ctypes

    ws: dict[int, int] = {}
    for pid in parent:
        h = k32.OpenProcess(0x1000 | 0x0010, False, pid)   # QUERY_LIMITED_INFORMATION | VM_READ
        if not h:
            continue
        try:
            c = PMC()
            c.cb = ctypes.sizeof(PMC)
            if psapi.GetProcessMemoryInfo(h, ctypes.byref(c), c.cb):
                ws[pid] = int(c.WorkingSetSize)
        finally:
            k32.CloseHandle(h)
    return ws


def subtree(root: int, parent: dict[int, int]) -> set[int]:
    """`root` and every descendant, whatever order the snapshot lists them in (a pid that is its own parent, as the
    System Idle Process is, is never followed)."""
    children: dict[int, list[int]] = {}
    for pid, ppid in parent.items():
        if pid != ppid:
            children.setdefault(ppid, []).append(pid)
    out, todo = {root}, [root]
    while todo:
        for c in children.get(todo.pop(), ()):
            if c not in out:
                out.add(c)
                todo.append(c)
    return out


def tree_reading(root: int, parent: dict[int, int], ws: dict[int, int]) -> dict:
    """One sample: the whole tree's working set, the root's own, and each direct child's subtree (bytes)."""
    tree = subtree(root, parent)
    workers = {c: sum(ws.get(p, 0) for p in subtree(c, parent))
               for c, pp in parent.items() if pp == root and c != root}
    return {"tree": sum(ws.get(p, 0) for p in tree), "root": ws.get(root, 0), "workers": workers,
            "processes": len(tree)}


class Peaks:
    """The running peaks over samples (bytes): tree, root, each worker subtree by pid, and the largest worker."""

    def __init__(self) -> None:
        self.tree = self.root = self.processes = self.samples = 0
        self.workers: dict[int, int] = {}
        self.max_concurrent_workers = 0

    def add(self, r: dict) -> None:
        self.samples += 1
        self.tree = max(self.tree, r["tree"])
        self.root = max(self.root, r["root"])
        self.processes = max(self.processes, r["processes"])
        self.max_concurrent_workers = max(self.max_concurrent_workers, len(r["workers"]))
        for pid, b in r["workers"].items():
            self.workers[pid] = max(self.workers.get(pid, 0), b)

    def record(self) -> dict:
        w = sorted(self.workers.values(), reverse=True)
        return {"samples": self.samples, "peak_tree_working_set_gb": round(self.tree / GB, 3),
                "peak_controller_gb": round(self.root / GB, 3), "peak_tree_processes": self.processes,
                "max_concurrent_children": self.max_concurrent_workers,
                "peak_per_child_gb": [round(b / GB, 3) for b in w[:8]],
                "peak_worker_gb": round(w[0] / GB, 3) if w else None}


def _kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True, timeout=60)
    else:
        proc.kill()
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--every", type=float, default=1.0)
    ap.add_argument("--floor-gb", type=float, default=2.0)
    ap.add_argument("--run-lock", type=Path, default=None, help="the heavy lock to watch (default: the main root's)")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("a command is needed after --")
    if a.run_lock is None:
        from run_lock import main_root
        a.run_lock = main_root() / "run.lock"
    gb = available_gb()
    if a.run_lock.exists() or (gb is not None and gb < a.floor_gb):
        rec = {"command": cmd, "aborted": "not started: run.lock held" if a.run_lock.exists()
               else f"not started: {gb:.2f} GB available, below the floor {a.floor_gb} GB"}
        a.out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        print(json.dumps(rec, indent=2))
        return 3
    t0 = time.time()
    proc = subprocess.Popen(cmd)
    peaks = Peaks()
    min_avail = None
    aborted = None
    try:
        while proc.poll() is None:
            s = snapshot()
            if s is not None:
                peaks.add(tree_reading(proc.pid, *s))
            gb = available_gb()
            if gb is not None:
                min_avail = gb if min_avail is None else min(min_avail, gb)
                if gb < a.floor_gb:
                    aborted = f"available memory {gb:.2f} GB fell below the floor {a.floor_gb} GB"
            if a.run_lock.exists():
                aborted = "run.lock appeared (a heavy run started)"
            if aborted:
                _kill_tree(proc)
                break
            time.sleep(a.every)
    except BaseException:
        _kill_tree(proc)
        raise
    rec = {"command": cmd, "exit": proc.returncode, "aborted": aborted, "seconds": round(time.time() - t0, 1),
           "every_s": a.every, "floor_gb": a.floor_gb, **peaks.record(),
           "min_available_gb": None if min_avail is None else round(min_avail, 3)}
    a.out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 3 if aborted else (proc.returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main())
