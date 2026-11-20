"""Run a command and record the peak memory of its whole process tree (Q-174: the fast tier's per-slot reserve).

    python scripts/tree_peak_memory.py --out peak.json -- python scripts/fasttier_lock.py run -- python -m pytest ...
    python scripts/tree_peak_memory.py --out peak.json --attach <pid>     # an already running tree, read only

Every `--every` seconds (default 2) it sums, over the command's process and all its descendants, the working set
(physical memory in use) and the private commit, keeps the peak of each sum, and the lowest machine-wide available
memory (`run_lock.available_gb`) seen while the command ran. At the end it writes them as JSON to `--out` (and prints
them) and exits with the command's own code. Windows only (Toolhelp snapshot + GetProcessMemoryInfo); elsewhere it
runs the command and records nothing.

The reading is a sample, not a trace: a spike shorter than the interval can be missed, so a reserve derived from it
carries a margin (fasttier_lock.SLOT_RESERVE_GB states its own).
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


def _tree_memory(root: int) -> tuple[int, int, int] | None:
    """(working set bytes, private bytes, process count) summed over `root` and its descendants; None off Windows."""
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

    snap = k32.CreateToolhelp32Snapshot(0x2, 0)
    parent: dict[int, int] = {}
    try:
        e = PE()
        e.dwSize = ctypes.sizeof(PE)
        ok = k32.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            parent[int(e.th32ProcessID)] = int(e.th32ParentProcessID)
            ok = k32.Process32NextW(snap, ctypes.byref(e))
    finally:
        k32.CloseHandle(snap)
    tree = {root}
    grew = True
    while grew:                                            # descendants, whatever order the snapshot lists them in
        grew = False
        for pid, ppid in parent.items():
            if ppid in tree and pid not in tree and pid != ppid:
                tree.add(pid)
                grew = True
    ws = priv = n = 0
    for pid in tree:
        h = k32.OpenProcess(0x1000 | 0x0010, False, pid)   # QUERY_LIMITED_INFORMATION | VM_READ
        if not h:
            continue
        try:
            c = PMC()
            c.cb = ctypes.sizeof(PMC)
            if psapi.GetProcessMemoryInfo(h, ctypes.byref(c), c.cb):
                ws += c.WorkingSetSize
                priv += c.PagefileUsage
                n += 1
        finally:
            k32.CloseHandle(h)
    return ws, priv, n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--every", type=float, default=2.0)
    ap.add_argument("--attach", type=int, default=None, help="sample the running process tree of this pid instead")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd and a.attach is None:
        ap.error("a command is needed after --, or --attach <pid>")
    t0 = time.time()
    if a.attach is not None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from fasttier_lock import pid_alive

        class _Attached:
            pid = a.attach
            returncode = None

            def poll(self):
                return None if pid_alive(self.pid) else 0

            def kill(self):
                pass

        proc = _Attached()
        cmd = [f"--attach {a.attach}"]
    else:
        proc = subprocess.Popen(cmd)
    peak_ws = peak_priv = peak_n = samples = 0
    min_avail = None
    try:
        while proc.poll() is None:
            m = _tree_memory(proc.pid)
            if m is not None:
                ws, priv, n = m
                peak_ws, peak_priv, peak_n = max(peak_ws, ws), max(peak_priv, priv), max(peak_n, n)
                samples += 1
            gb = available_gb()
            if gb is not None:
                min_avail = gb if min_avail is None else min(min_avail, gb)
            time.sleep(a.every)
    except BaseException:
        proc.kill()
        raise
    rec = {"command": cmd, "exit": proc.returncode, "seconds": round(time.time() - t0, 1), "samples": samples,
           "every_s": a.every, "peak_tree_working_set_gb": round(peak_ws / 2**30, 3),
           "peak_tree_private_gb": round(peak_priv / 2**30, 3), "peak_tree_processes": peak_n,
           "min_available_gb": None if min_avail is None else round(min_avail, 3)}
    a.out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
