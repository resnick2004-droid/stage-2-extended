"""This process's memory, for the hand-back's peak figures (Q-16): Windows' psapi through ctypes (psutil is not
installed); NaN on any other platform or on failure. Reading it changes nothing.

**Built once** (Q-187): the structure, the two functions' prototypes and the pointer type are made at the first
reading and reused. Until Q-187 they were made inside every call, and ctypes keeps every pointer type it makes for the
life of the process (`ctypes.POINTER`'s cache), so each reading left a new structure class and its pointer type behind
-- a few kilobytes a call, never freed: H3-A2's memory guard, which reads after every close of the exact program, grew
each reused worker's working set history by history (`tests/test_procmem.py` measures both)."""
from __future__ import annotations

_API: tuple | None = None


def _api() -> tuple:
    """(ctypes, the counters' structure, kernel32, psapi), built at the first call and kept."""
    global _API
    if _API is None:
        import ctypes
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
        _API = (ctypes, PMC, k32, psapi)
    return _API


def working_set_mb(peak: bool = False) -> float:
    """The current working set, or its peak since the process started, in MB."""
    try:
        ctypes, PMC, k32, psapi = _api()
        c = PMC()
        c.cb = ctypes.sizeof(PMC)
        if not psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
            return float("nan")
        return (c.PeakWorkingSetSize if peak else c.WorkingSetSize) / 2**20
    except Exception:                                   # noqa: BLE001
        return float("nan")


__all__ = ["working_set_mb"]
