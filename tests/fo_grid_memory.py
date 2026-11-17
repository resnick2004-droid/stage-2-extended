"""F-03's grid-by-year read (the build read's memory note): its peak memory against the one-shot read on a synthetic bar
store of the choice window's size, each read in a fresh process. Synthetic only (`extended/synthetic_bars.py`), never
the licensed data; the store is written to a temporary folder named on the command line.

    python tests/fo_grid_memory.py <repository root> make <folder> [first last]   # the store (default 2020-01-02 .. 2023-12-29)
    python tests/fo_grid_memory.py <repository root> measure <folder> oneshot|byyear [first last]

`measure` prints one JSON line: the read's rows and sessions, the grid's sha256 (every array's bytes and the days),
the process's peak working set before the read and after it (Windows `GetProcessMemoryInfo`), tracemalloc's peak of
the read, and its seconds. `oneshot` is the build's read before this change (every bar of the span at once, then the
walked sessions' grid); `byyear` is `opening_states.grid_by_year` as `Ctx.grid` now reads.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import sys
import time
import tracemalloc
from datetime import date
from pathlib import Path

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO))
SEED_KEY = (20261988, 1200)              # section 16's test block (the builder's key 1200: this store)


def peak_working_set() -> tuple[int, int]:
    """(the working set now, its peak) in bytes, by psapi's GetProcessMemoryInfo."""
    class PMC(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    c = PMC()
    c.cb = ctypes.sizeof(PMC)
    k32 = ctypes.windll.kernel32
    k32.GetCurrentProcess.restype = ctypes.c_void_p                  # a 64-bit pseudo-handle, never truncated
    k32.K32GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    if not k32.K32GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
        raise OSError("GetProcessMemoryInfo failed")
    return int(c.WorkingSetSize), int(c.PeakWorkingSetSize)


def grid_sha256(g) -> str:
    d = hashlib.sha256("\n".join(x.isoformat() for x in g.days).encode())
    d.update("\n".join(str(x) for x in g.contract).encode())
    for a in (g.O, g.H, g.L, g.C, g.V):
        d.update(a.dtype.str.encode() + str(a.shape).encode() + a.tobytes())
    return d.hexdigest()


def make(folder: Path, first: date, last: date) -> None:
    from extended import reader
    from extended import synthetic_bars as sb

    spec = sb.Spec(first, last, seed=list(SEED_KEY), vol_scale=10.0)
    bars = sb.generate(spec)
    p = folder / reader.STORE_REL / "NQ"
    p.mkdir(parents=True, exist_ok=True)
    bars[["ts", "day", "contract", "open", "high", "low", "close", "volume"]].to_parquet(p / "bars.parquet",
                                                                                        index=False)
    days = sorted(bars["day"].astype(str).unique())
    (folder / "walked.json").write_text(json.dumps([d for d in days if date.fromisoformat(d).weekday() != 0]),
                                        encoding="utf-8")                # a walked subset: every day but Mondays
    print(json.dumps({"rows": int(len(bars)), "sessions": len(days)}))


def measure(folder: Path, mode: str, first: str, last: str) -> None:
    from extended import use_vendored_stage2

    use_vendored_stage2()
    import pandas as pd  # noqa: F401  (imported before the baseline)

    from extended import features as F
    from extended import opening_states as OS
    from extended import reader

    walked = set(json.loads((folder / "walked.json").read_text(encoding="utf-8")))
    read = lambda s, e: reader.read_bars(s, e, repo=folder, what="F-03 memory probe (synthetic)")  # noqa: E731
    ws0, pk0 = peak_working_set()
    tracemalloc.start()
    t0 = time.time()
    if mode == "oneshot":
        b = read(first, last)
        n = len(b)
        g = F.grid(b[b["day"].astype(str).isin(walked)].reset_index(drop=True))
        del b
    else:
        g = OS.grid_by_year(read, first, last, walked)
        n = int((~__import__("numpy").isnan(g.C)).sum())
    secs = time.time() - t0
    _, tpk = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ws1, pk1 = peak_working_set()
    print(json.dumps({"mode": mode, "rows_read": int(n), "sessions": len(g.days), "grid_sha256": grid_sha256(g),
                      "working_set_before_mb": round(ws0 / 2**20, 1), "peak_before_mb": round(pk0 / 2**20, 1),
                      "peak_after_mb": round(pk1 / 2**20, 1), "peak_rise_mb": round((pk1 - max(pk0, ws0)) / 2**20, 1),
                      "tracemalloc_peak_mb": round(tpk / 2**20, 1), "seconds": round(secs, 1)}))


if __name__ == "__main__":
    what, folder = sys.argv[2], Path(sys.argv[3])
    if what == "make":
        a = sys.argv[4:6] or ["2020-01-02", "2023-12-29"]
        make(folder, date.fromisoformat(a[0]), date.fromisoformat(a[1]))
    else:
        a = sys.argv[5:7] or ["2020-01-02", "2023-12-29"]
        measure(folder, sys.argv[4], a[0], a[1])
