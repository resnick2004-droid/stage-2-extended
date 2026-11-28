"""The heavy-run lock (E-005, E-006): one heavy run at a time on the machine, whichever tree it starts from.

    python scripts/run_lock.py status
    python scripts/run_lock.py take --job u1-identity --task Q-05 --hours 2 --mem-gb 3 --holder wt-verify --cmd "..."
    python scripts/run_lock.py set-pid --job u1-identity --pid 12345 --log "C:/.../u1-identity.log"
    python scripts/run_lock.py release --job u1-identity

The lock is `run.lock` at the **main** repository's root (found from `git rev-parse --git-common-dir`, so every
worktree and clean checkout sees the same file); git-ignored. `take` refuses (exit 3) when the lock is held, and
(exit 4) when the machine's available physical memory is below `--mem-gb`, or cannot be read (Q-229) -- a heavy run never starts short of the
memory it needs. The file is created atomically (`open(..., "x")`), so two takers cannot both win. `release` removes
it only for the job that holds it. A lock older than its expected end plus one hour is reported **STALE**: it is
investigated (is its process alive, is its log growing?) and reported to the lead -- never stolen; `release --force`
exists for the lead alone, after that investigation, and its use is logged in PROGRESS.md.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
STALE_AFTER = timedelta(hours=1)


def main_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=HERE,
                             capture_output=True, text=True, check=True).stdout.strip()
        return Path(out).resolve().parent
    except (OSError, subprocess.CalledProcessError):
        return HERE


LOCK = main_root() / "run.lock"


def available_gb() -> float | None:
    """Available physical memory in GB (Windows: GlobalMemoryStatusEx; elsewhere: /proc/meminfo), or None."""
    if os.name == "nt":
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            return m.ullAvailPhys / 2**30
        return None
    if sys.platform == "darwin":
        return _darwin_available_gb()
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 2**20
    except OSError:
        pass
    return None


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def read() -> dict | None:
    if not LOCK.is_file():
        return None
    try:
        return json.loads(LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"job": "?", "unreadable": True}


def is_stale(lock: dict) -> bool:
    try:
        end = datetime.fromisoformat(lock["expected_end"])
    except (KeyError, ValueError, TypeError):
        return True
    return now() > end + STALE_AFTER


def describe(lock: dict) -> str:
    stale = "  ** STALE: investigate (process alive? log growing?), never steal **" if is_stale(lock) else ""
    keys = ("job", "task", "holder", "start", "expected_end", "pid", "log", "cmd")
    return "HELD: " + ", ".join(f"{k}={lock.get(k)}" for k in keys if lock.get(k) is not None) + stale


def _darwin_available_gb(vm_stat: str | None = None) -> float | None:
    """macOS (Q-229): free + inactive + speculative pages from `vm_stat`, times its page size -- the memory a new
    process can have without the system swapping. None when `vm_stat` cannot be read (the lock then refuses)."""
    import re
    import subprocess
    if vm_stat is None:
        try:
            vm_stat = subprocess.run(["vm_stat"], capture_output=True, text=True, check=True, timeout=30).stdout
        except (OSError, subprocess.SubprocessError):
            return None
    m = re.search(r"page size of (\d+) bytes", vm_stat)
    if not m:
        return None
    pages = 0
    for key in ("Pages free", "Pages inactive", "Pages speculative"):
        k = re.search(re.escape(key) + r":\s+(\d+)", vm_stat)
        if not k:
            return None
        pages += int(k.group(1))
    return pages * int(m.group(1)) / 2**30


def memory_words(lock: dict) -> str:
    """The memory the lock's own record holds, for its TAKEN line (Q-229): what was read at the take, what the job
    needs."""
    have, need = lock.get("mem_gb_available_at_start"), lock.get("mem_gb_needed")
    have_s = "unread" if have is None else f"{float(have):.2f} GB"
    need_s = "unstated" if need is None else f"{float(need):.2f} GB"
    return f"memory available at the take {have_s}, needed {need_s}"


def take(a) -> int:
    held = read()
    if held is not None:
        print(f"REFUSED: {describe(held)}")
        return 3
    gb = available_gb()
    if gb is None:
        print("REFUSED: this machine's available memory cannot be read; a heavy run never starts unchecked (Q-229)")
        return 4
    if gb < a.mem_gb:
        print(f"REFUSED: {gb:.1f} GB available, the job needs {a.mem_gb:.1f} GB; it waits (STATUS.md, OPERATOR_SETUP item 9)")
        return 4
    start = now()
    lock = {"job": a.job, "task": a.task, "holder": a.holder, "start": start.isoformat(),
            "expected_end": (start + timedelta(hours=a.hours)).isoformat(), "mem_gb_needed": a.mem_gb,
            "mem_gb_available_at_start": None if gb is None else round(gb, 2), "cmd": a.cmd, "pid": None, "log": None}
    try:
        with open(LOCK, "x", encoding="utf-8") as f:
            json.dump(lock, f, indent=2)
    except FileExistsError:
        print(f"REFUSED: taken a moment ago -- {describe(read() or {})}")
        return 3
    print(f"TAKEN: {LOCK} by {a.holder} for {a.job} ({a.task}), expected end {lock['expected_end']}; "
          f"{memory_words(lock)}")
    return 0


def set_pid(a) -> int:
    held = read()
    if not held or held.get("job") != a.job:
        print(f"REFUSED: the lock is not held by {a.job}: {describe(held) if held else 'free'}")
        return 3
    held["pid"], held["log"] = a.pid, a.log
    LOCK.write_text(json.dumps(held, indent=2), encoding="utf-8")
    print(f"updated: pid={a.pid} log={a.log}")
    return 0


def release(a) -> int:
    held = read()
    if held is None:
        print("free already")
        return 0
    if held.get("job") != a.job and not a.force:
        print(f"REFUSED: held by {held.get('job')}, not {a.job} -- {describe(held)}")
        return 3
    LOCK.unlink()
    print(f"RELEASED: {held.get('job')}{' (forced by the lead; log it in PROGRESS.md)' if a.force else ''}")
    return 0


def status(_a) -> int:
    held = read()
    gb = available_gb()
    mem = "unknown" if gb is None else f"{gb:.1f} GB available"
    print(f"{LOCK}: {describe(held) if held else 'FREE'}  ({mem})")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="action", required=True)
    t = sub.add_parser("take")
    t.add_argument("--job", required=True)
    t.add_argument("--task", required=True)
    t.add_argument("--holder", required=True, help="the worktree or session taking it")
    t.add_argument("--hours", type=float, required=True, help="expected duration")
    t.add_argument("--mem-gb", type=float, required=True, help="memory the job needs")
    t.add_argument("--cmd", default=None)
    p = sub.add_parser("set-pid")
    p.add_argument("--job", required=True)
    p.add_argument("--pid", type=int, required=True)
    p.add_argument("--log", default=None)
    r = sub.add_parser("release")
    r.add_argument("--job", required=True)
    r.add_argument("--force", action="store_true", help="the lead only, after investigating a stale lock")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    return {"take": take, "set-pid": set_pid, "release": release, "status": status}[a.action](a)


if __name__ == "__main__":
    sys.exit(main())
