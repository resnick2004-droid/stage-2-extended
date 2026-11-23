"""The machine-wide fast-tier lock (Q-155): one pre-commit fast tier at a time, whichever tree commits.

    python scripts/fasttier_lock.py run -- python -m pytest -o addopts= -q -m "not slow and not heavy"
    python scripts/fasttier_lock.py status

**Why.** Every tree -- the main tree, each worktree under `%LOCALAPPDATA%\\stage2-extended-wt`, a clean checkout --
shares one pre-commit hook (`scripts/install_hooks.py` installs it into the common git directory). Several worktrees
once committed at the same moment, their fast tiers ran side by side, free memory fell near 0.5 GB and the hooks died
of `MemoryError`, OpenBLAS allocation errors and WinError 1455, forcing 30-40 minute reruns. The hook now runs its
pytest through `run`, which:

1. **takes a slot of the lock** -- the file `%LOCALAPPDATA%\\stage2-extended-fasttier.lock` (machine-wide, never on
   OneDrive), created atomically (`O_CREAT | O_EXCL`), holding the holder's tree, pid, host, start, slot and a random
   token. **Up to MAX_SLOTS fast tiers run at once** (Q-174; `S2X_FASTTIER_SLOTS`, default 2): slot 0 is that file
   (the one a tree without Q-174 contends for), slot i is `<lock>.slot<i>`, each with its own record, heartbeat,
   takeover and release. The head of the line takes a free slot when none is running, or when available memory is at
   least 1.5 GB plus SLOT_RESERVE_GB (1.2 GB, a measured fast tier's peak with a margin; SLOT_RESERVE_SOURCE) for every
   slot running -- otherwise it keeps its place and waits, so with one slot's worth of memory nothing changes. **A
   slot running n xdist workers** (Q-193, scripts/fasttier_xdist.py, which writes its n into its record as `workers`)
   **counts at its own reserve**, slot_reserve_gb(n) = SLOT_RESERVE_GB + (n - 1) * PER_WORKER_GB: slots and workers
   share one memory and are never counted apart;
2. **waits for a live holder, first come first served** (Q-165), polling every 30 s and printing one line a minute
   with its place in line: on arrival a waiter takes a ticket -- a file created atomically in the queue directory
   beside the lock (`<lock>.queue/`), named by its arrival time, pid and token -- and takes the lock only while its
   ticket is the oldest live one. The waiter touches its ticket on every poll (its heartbeat, Q-199); a ticket whose
   process is not running, or whose heartbeat is older than TICKET_STALE_S (10 min), is skipped and removed, never
   honoured -- never for its arrival's age, since a live waiter may wait past the cap in all. A ticket without the
   heartbeat mark (a tree without Q-199) is kept while its pid lives within the 3-hour cap by arrival (that tree's rule)
   and past it only while it was recreated within TICKET_STALE_S (its owner puts it back after each age prune).
   A waiter whose ticket was removed under it puts it back on its next poll under the same name, so at the same place.
   The ticket is removed on every exit path; a hard kill leaves it with a dead pid. **The main tree goes first**
   (Q-207): a waiter whose tree is the repository's main worktree (the lead's, on `master`: the top-level worktree,
   whose `.git` is a directory; is_main_worktree reads it from the tree's own git, `--git-common-dir`'s parent being
   `--show-toplevel`, never from an argument or an environment variable) marks its ticket TICKET_LEAD_MARK, a worker's
   TICKET_WORKER_MARK, both before the heartbeat mark, so older code still parses the name; the line puts the lead's
   tickets ahead of the workers', in arrival order among themselves (order_line). Only the order of the waiters
   changes: a running job is never pre-empted, the lead takes the next free slot under the same admission and memory
   rules. A ticket with neither mark (a tree without Q-207, which orders by arrival alone) keeps its arrival place
   against every ticket, so a mixed set of trees never sees two heads of the line;
3. **takes over a stale holder**, saying so: its pid is not running (a hook that crashed or was killed), or its record
   is older than 2 hours (a hung run, or a reused pid), or the file has been unreadable for over a minute (a hook killed
   between creating and writing it). A takeover is serialised by a short-lived guard file and removes the lock only if
   it is still the very record judged stale, so two waiters cannot both take it and a fresh holder is never removed;
4. **waits, holding the lock, until free physical memory is at least 1.5 GB**, with the same polling; while it waits
   it refreshes its record (`updated`), so a waiting holder is never mistaken for a hung one;
5. **runs the command** with the token in `S2X_FASTTIER_TOKEN` (a commit made from inside the fast tier re-enters
   under the lock it already holds instead of waiting on itself), and returns its exit code; with `S2X_FASTTIER_TEE`
   set (the hook sets it, Q-161) the command's output is also copied into that file, and the command is killed if
   this wrapper is interrupted;
6. **releases on every exit path** -- success, failure, an exception, Ctrl+C, SIGTERM/SIGBREAK -- and only its own
   lock (the token must match). A hard kill leaves the file behind; the next hook sees the dead pid and takes over.

The wait is bounded by 3 hours **of a line that does not move** (Q-174): the waiter's timer restarts whenever the jobs
holding the slots change (a holder leaves or a new one takes a slot; a heartbeat under the same token is the same job),
so a waiter behind a long, advancing line waits as long as the line takes, while a stuck live holder still runs the cap
out (and a dead or 2-hour-old one is taken over, as before). The memory wait, once a slot is held, has its own 3-hour
bound. At a bound `run` prints FAILED with the holder and exits 75, and the hook fails. It never passes silently. What
the hook checks is unchanged: this only orders the runs.

Not the heavy lock: `scripts/run_lock.py` (`run.lock`, one heavy run at a time) is never stolen; this one guards a
minutes-long test run whose holder can crash, so a dead or overdue holder is taken over.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_lock import available_gb  # noqa: E402  (the heavy lock's memory reading, one implementation)

#: the declared bounds (Q-155)
POLL_S = 30                      # poll a held lock / short memory every 30 s
PRINT_EVERY_S = 60               # one line a minute while waiting
TIMEOUT_S = 3 * 3600             # the whole wait, lock and memory, at most 3 hours
STALE_AFTER = timedelta(hours=2)  # a holder whose record is older than this is taken over
MIN_FREE_GB = 1.5                # free physical memory before pytest starts
UNREADABLE_GRACE_S = 60          # an empty or garbled lock younger than this may be a write in flight
GUARD_GRACE_S = 60               # a takeover guard older than this was left by a crash
#: Q-199: a waiter's ticket is stale when its pid is not running, or when its heartbeat (the ticket's mtime, touched by
#: its owner on every poll, POLL_S = 30 s) is older than this -- never by its arrival, since a live waiter may wait past
#: TIMEOUT_S in all (Q-174). Ten minutes is 20 polls and 10 printed lines (PRINT_EVERY_S): a live waiter slowed by a
#: starved machine (paging at near-zero available memory) or a slow filesystem call misses many beats before it is
#: dropped, and if it is dropped it puts its ticket back on its next poll under the same name, so the same place. The
#: bound guards pid reuse: a hard-killed waiter whose pid a new process reuses is dropped within ten minutes, not kept
#: forever. Far under STALE_AFTER and TIMEOUT_S, so it never decides what those decide.
TICKET_STALE_S = 10 * 60
TICKET_HEARTBEAT_MARK = ".hb"    # ends the token field of a ticket that beats (Q-199); old code parses it unchanged
#: Q-207: a ticket's class, written in its token field before TICKET_HEARTBEAT_MARK (so Q-199 code still reads the beat
#: and older code still reads three fields): the main worktree's waiter (the lead) or a worker's. A ticket with neither
#: was written by a tree without Q-207, which orders the line by arrival alone; it keeps its arrival place (line()).
TICKET_LEAD_MARK = ".lead"
TICKET_WORKER_MARK = ".work"

LOCK_NAME = "stage2-extended-fasttier.lock"
ENV_TOKEN = "S2X_FASTTIER_TOKEN"
ENV_TEE = "S2X_FASTTIER_TEE"     # Q-161: a file the command's output is copied into (the hook's verdict reads its pass line)
ENV_SLOTS = "S2X_FASTTIER_SLOTS"  # Q-174: how many fast tiers may run at once (default DEFAULT_SLOTS, at least 1)
DEFAULT_SLOTS = 2
#: Q-174 / Q-211: a running fast tier's peak memory, and the reserve declared from it. A further slot opens only while
#: available memory >= MIN_FREE_GB + SLOT_RESERVE_GB for every slot already running (2.7 GB beside a serial slot; 3.9 GB
#: beside an n = 2 slot via slot_reserve_gb(2) = 2.4 GB).
MEASURED_PEAK_GB = 1.00
SLOT_RESERVE_GB = 1.2
SLOT_RESERVE_SOURCE = (
    "Q-211 whole-tier re-measurement after re-pinning q108's literal scan to git grep -l "
    "(docs/measurements/q211_mem/Q211_whole_n2_loadfile.json, 2026-11-22, n = 2 --dist loadfile, 3837 passed in 1696.7 s, "
    "1676 samples at 1 s): peak tree working set 1.627 GB, peak worker 0.933 GB, peak controller 0.063 GB "
    "(single-worker sum 0.996 GB -> MEASURED_PEAK_GB 1.00 GB, SLOT_RESERVE_GB 1.2 GB; min available 3.782 GB). "
    "Supersedes Q-174's pre-Q-211 scripts/tree_peak_memory.py --attach measurement (2.257 GB peak, 2.5 GB reserve)."
)
#: Q-193: a further xdist worker's peak inside a slot -- the largest worker subtree measured on the fast tier's slices,
#: with its margin (scripts/fasttier_xdist.py's MEASURE_SOURCE; tests/test_fasttier_xdist.py traces it to the records in
#: docs/measurements/q193_xdist). Slots and workers share one memory, so a slot's reserve grows with its workers and is
#: never counted apart from them: slot_reserve_gb is the one accounting, used both by the slot admission below and by
#: the runner's choice of n (fasttier_xdist.choose_workers), and a running slot records its n ("workers").
PER_WORKER_GB = 1.2
EXIT_TIMEOUT = 75                # EX_TEMPFAIL: the wait ran out
EXIT_LOST = 76                   # the lock was taken from this holder before pytest started

Sleep = Callable[[float], None]
Clock = Callable[[], float]


class WaitTimeout(RuntimeError):
    """The lock or the memory did not come within the bound."""


class LockLost(RuntimeError):
    """This holder's lock was taken over before its command started."""


@dataclass
class Holder:
    token: str
    record: dict
    path: Path | None = None           # the slot file this holder holds (Q-174)


# ------------------------------------------------------------------------------------------------ the slots (Q-174)

def _slots_from_env() -> int:
    raw = os.environ.get(ENV_SLOTS, "").strip()
    try:
        n = int(raw) if raw else DEFAULT_SLOTS
    except ValueError:
        n = DEFAULT_SLOTS
    return max(1, n)


MAX_SLOTS = _slots_from_env()


def slot_path(lock: Path, i: int) -> Path:
    """Slot 0 is the lock file itself -- the one a tree that has not merged Q-174 contends for; slot i is <lock>.slot<i>."""
    return lock if i == 0 else Path(f"{lock}.slot{i}")


def _slot_files(lock: Path, n: int) -> list[Path]:
    """The first n slots, and any further slot file present (written under a larger setting)."""
    paths = [slot_path(lock, i) for i in range(n)]
    for p in sorted(lock.parent.glob(lock.name + ".slot*")):
        suffix = p.name[len(lock.name) + len(".slot"):]
        if suffix.isdigit() and p not in paths:
            paths.append(p)
    return paths


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def parse_time(s) -> datetime | None:
    try:
        t = datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _say(msg: str) -> None:
    print(f"pre-commit: {msg}", flush=True)


def _refuse_onedrive(p: Path) -> Path:
    if "onedrive" in str(p).lower():
        raise SystemExit(f"fasttier_lock: the lock {p} would lie under OneDrive, which locks files under a running job; "
                         f"it must be under %LOCALAPPDATA%")
    return p


def default_lock_path() -> Path:
    """`%LOCALAPPDATA%\\stage2-extended-fasttier.lock`: one file for every tree on this machine."""
    base = os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
    return _refuse_onedrive(Path(base) / LOCK_NAME)


# ------------------------------------------------------------------------------------------------ the file

def try_create(path: Path, record: dict) -> bool:
    """Create the lock holding `record`, atomically; False if it exists already."""
    data = json.dumps(record, indent=2).encode("utf-8")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
    except FileExistsError:
        return False
    except PermissionError:          # Windows: the old file is being deleted at this instant
        return False
    try:
        os.write(fd, data)
    finally:
        os.close(fd)
    return True


def _read_raw(path: Path) -> str | None:
    """The lock's text; None if there is no lock. A transient sharing error reads as an unreadable (young) lock."""
    for _ in range(5):
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except PermissionError:
            time.sleep(0.05)
    return ""


def _parse(raw: str) -> dict | None:
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return rec if isinstance(rec, dict) and isinstance(rec.get("pid"), int) and rec.get("token") else None


def _unlink(path: Path) -> None:
    for _ in range(20):
        try:
            path.unlink()
            return
        except FileNotFoundError:
            return
        except PermissionError:      # Windows: a reader has it open for a moment
            time.sleep(0.05)
    path.unlink(missing_ok=True)


def _age_s(path: Path) -> float:
    try:
        return time.time() - path.stat().st_mtime
    except OSError:
        return 0.0


def pid_alive(pid: int) -> bool:
    """Whether a process with this pid is running on this machine."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        h = k32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5           # ERROR_ACCESS_DENIED: it exists, it is not ours
        try:
            code = wintypes.DWORD()
            if not k32.GetExitCodeProcess(h, ctypes.byref(code)):
                return True
            return code.value == 259                      # STILL_ACTIVE (an exited process's handle may linger)
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(pid, 0)                                   # POSIX only: on Windows signal 0 would terminate it
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def describe(rec: dict | None) -> str:
    if not rec:
        return "an unreadable record"
    return (f"tree={rec.get('tree')}, pid={rec.get('pid')}, since {rec.get('start')}"
            f" (phase {rec.get('phase')}, updated {rec.get('updated')}"
            + (f", {rec['workers']} xdist workers" if workers_of(rec) > 1 else "") + ")")


def stale_reason(path: Path, raw: str) -> str | None:
    """Why the lock holding `raw` may be taken over, or None while its holder may still be working."""
    rec = _parse(raw)
    if rec is None:
        age = _age_s(path)
        return (f"the lock has been unreadable for {age:.0f} s (a hook killed while writing it)"
                if age > UNREADABLE_GRACE_S else None)
    if not pid_alive(rec["pid"]):
        return f"its holder ({describe(rec)}) is not running"
    t = parse_time(rec.get("updated")) or parse_time(rec.get("start"))
    if t is None or now() - t > STALE_AFTER:
        return f"its holder ({describe(rec)}) is older than {STALE_AFTER.total_seconds() / 3600:.0f} h"
    return None


def _take_over(path: Path, raw_seen: str) -> bool:
    """Remove the lock if it still holds exactly `raw_seen`; serialised by a guard file. True if removed."""
    guard = Path(str(path) + ".takeover")
    if not try_create(guard, {"pid": os.getpid(), "token": "guard", "start": now().isoformat()}):
        if _age_s(guard) > GUARD_GRACE_S:
            _unlink(guard)                                # left by a crash inside a takeover
        return False
    try:
        if _read_raw(path) != raw_seen:
            return False                                  # it changed: someone else's, fresh
        _unlink(path)
        return True
    finally:
        _unlink(guard)


# ------------------------------------------------------------------------------------------------ the queue (Q-165)

def queue_dir(lock: Path) -> Path:
    """The waiters' tickets, beside the lock."""
    return Path(str(lock) + ".queue")


def ticket_name(arrival_ns: int, pid: int, token: str, heartbeat: bool = False, lead: bool | None = None) -> str:
    """Sorts by arrival time (fixed-width nanoseconds), then pid, then token. A ticket whose owner beats on every poll
    (Q-199) carries TICKET_HEARTBEAT_MARK at the end of its token field: still three fields to an old-code tree. Q-207's
    class mark (`lead` True: TICKET_LEAD_MARK, False: TICKET_WORKER_MARK, None: none, as a tree without Q-207 writes)
    goes before it. This only formats a name: acquire() alone decides `lead`, from the tree's git (is_main_worktree)."""
    klass = "" if lead is None else (TICKET_LEAD_MARK if lead else TICKET_WORKER_MARK)
    return f"{arrival_ns:020d}-{pid:010d}-{token}{klass}{TICKET_HEARTBEAT_MARK if heartbeat else ''}.ticket"


def is_heartbeat_ticket(name: str) -> bool:
    """Whether the ticket's owner touches it on every poll (Q-199); False for an old-code tree's ticket."""
    parsed = parse_ticket(name)
    return parsed is not None and parsed[2].endswith(TICKET_HEARTBEAT_MARK)


def ticket_class(name: str) -> str | None:
    """Q-207: "lead" (the main worktree's waiter), "worker", or None (not a ticket, or a tree without Q-207's)."""
    parsed = parse_ticket(name)
    if parsed is None:
        return None
    field = parsed[2]
    if field.endswith(TICKET_HEARTBEAT_MARK):
        field = field[: -len(TICKET_HEARTBEAT_MARK)]
    if field.endswith(TICKET_LEAD_MARK):
        return "lead"
    if field.endswith(TICKET_WORKER_MARK):
        return "worker"
    return None


def is_lead_ticket(name: str) -> bool:
    """Whether the ticket is the main worktree's (Q-207): first in line."""
    return ticket_class(name) == "lead"


def order_line(names: list[str]) -> list[str]:
    """The line's order (Q-207): by arrival, except that a lead ticket goes ahead of every worker ticket -- in arrival
    order among the leads, and never past a ticket without a class mark. Such a ticket was written by a tree without
    Q-207, which orders by arrival alone and so takes the head whenever nothing older is live; it is therefore a fixed
    point -- every older ticket stays ahead of it, every younger one behind -- and the leads go first only within each
    stretch between two of them. With no such ticket in the queue: the leads by arrival, then the workers by arrival."""
    out: list[str] = []
    stretch: list[str] = []
    for name in sorted(names):                            # arrival order (the name's fixed-width first field)
        if ticket_class(name) is None:
            out.extend(sorted(stretch, key=lambda n: (not is_lead_ticket(n), n)))
            stretch = []
            out.append(name)
        else:
            stretch.append(name)
    out.extend(sorted(stretch, key=lambda n: (not is_lead_ticket(n), n)))
    return out


def _git_env() -> dict:
    """The environment without git's own variables (GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, ...): the tree is judged by
    its path alone, so no variable can make a tree look like another."""
    return {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}


def _same_path(a: Path, b: Path) -> bool:
    return os.path.normcase(os.path.normpath(str(a))) == os.path.normcase(os.path.normpath(str(b)))


def is_main_worktree(tree) -> bool:
    """Q-207: whether `tree` lies in its repository's main worktree -- the top-level worktree, whose `.git` is a
    directory (the lead's tree on `master`), not a linked worktree (a worker's, a clean checkout's), whose `.git` is a
    file. Read from the tree's own git with git's variables removed: `--git-common-dir`'s parent is `--show-toplevel`,
    and that top level's `.git` is a directory and is the common dir. Anything else -- not a directory, not a
    repository, a bare or submodule git directory, git missing or failing -- is False: a worker's ticket."""
    try:
        p = Path(tree)
        if not str(tree) or not p.is_dir():
            return False
        out = subprocess.run(["git", "-C", str(p), "rev-parse", "--path-format=absolute", "--git-common-dir",
                              "--show-toplevel"], capture_output=True, text=True, timeout=60, env=_git_env())
    except (OSError, ValueError, subprocess.SubprocessError):
        return False
    lines = [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    if out.returncode != 0 or len(lines) != 2:
        return False
    try:
        common, top = Path(lines[0]).resolve(), Path(lines[1]).resolve()
        dot_git = top / ".git"
        return _same_path(common.parent, top) and dot_git.is_dir() and _same_path(dot_git.resolve(), common)
    except OSError:
        return False


def _beat_age_s(t: Path) -> float | None:
    """Seconds since the ticket's last heartbeat (its mtime); None if it is gone, 0 if it cannot be read just now."""
    try:
        return time.time() - t.stat().st_mtime
    except FileNotFoundError:
        return None
    except OSError:                  # Windows: its owner is touching it at this instant
        return 0.0


def _beat(t: Path) -> None:
    """Touch the ticket (its heartbeat). A sharing error is skipped: the next poll beats again, far inside the bound."""
    for _ in range(5):
        try:
            os.utime(t, None)
            return
        except FileNotFoundError:
            return
        except PermissionError:
            time.sleep(0.05)


def parse_ticket(name: str) -> tuple[int, int, str] | None:
    """(arrival_ns, pid, token) from a ticket's name; None for anything else."""
    if not name.endswith(".ticket"):
        return None
    parts = name[: -len(".ticket")].split("-")
    if len(parts) != 3 or not parts[0].isdigit() or not parts[1].isdigit():
        return None
    return int(parts[0]), int(parts[1]), parts[2]


def _make_ticket(q: Path, name: str) -> Path:
    q.mkdir(parents=True, exist_ok=True)
    t = q / name
    try:
        os.close(os.open(t, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)))
    except FileExistsError:
        pass
    return t


def line(q: Path, mine: str, cap_s: float = TIMEOUT_S, stale_s: float = TICKET_STALE_S) -> list[str]:
    """The live tickets in line order (order_line, Q-207: by arrival, the main worktree's tickets ahead of the workers');
    this waiter's own ticket (`mine`) is always in it, at its place, even while its file is missing (its owner puts it
    back). Another's ticket is removed here, never honoured,
    when its process is not running, or (Q-199) when it beats and its heartbeat is older than `stale_s` -- never for its
    arrival's age, since a live waiter may wait past the cap in all. A ticket that does not beat was written by a tree
    without Q-199: kept while its pid lives and its arrival is within `cap_s` (that tree's rule), and past `cap_s` only
    while it was (re)created within `stale_s` -- its owner recreates it whenever an old tree's age prune removes it."""
    names = sorted(t.name for t in q.iterdir()) if q.is_dir() else []
    live = []
    now_ns = time.time_ns()
    for name in names:
        parsed = parse_ticket(name)
        if parsed is None:
            continue
        if name != mine:
            arrival_ns, pid, _ = parsed
            if not pid_alive(pid):
                _unlink(q / name)
                continue
            if is_heartbeat_ticket(name) or (now_ns - arrival_ns) / 1e9 > cap_s:
                # A beating ticket is judged by its heartbeat. A ticket of a tree without Q-199, past the cap, by its
                # last (re)creation: a live owner puts it back each time an old tree's age prune removes it, a dead
                # owner (its pid reused) never does.
                age = _beat_age_s(q / name)
                if age is None:
                    continue                              # removed a moment ago
                if age > stale_s:
                    _unlink(q / name)
                    continue
        live.append(name)
    if mine not in live and parse_ticket(mine) is not None:
        live.append(mine)
    return order_line(live)


def slot_reserve_gb(workers: int = 1, reserve_gb: float | None = None, per_worker_gb: float = PER_WORKER_GB) -> float:
    """One slot's memory reserve at `workers` xdist workers (Q-193): the serial fast tier's reserve (SLOT_RESERVE_GB,
    or `reserve_gb`) plus one worker's peak for each worker beyond the first. A serial slot's is SLOT_RESERVE_GB, as
    Q-174 declared it."""
    base = SLOT_RESERVE_GB if reserve_gb is None else reserve_gb
    return base + max(0, int(workers) - 1) * per_worker_gb


def workers_of(rec: dict | None) -> int:
    """The xdist workers a slot's record says it runs (Q-193): an integer >= 1, else 1 (a serial tier, or a record
    written before its runner chose n, or by a tree without Q-193)."""
    w = (rec or {}).get("workers")
    return w if isinstance(w, int) and not isinstance(w, bool) and w >= 1 else 1


def record_workers(lock: Path, token: str, workers: int, n_slots: int | None = None) -> Path | None:
    """Write `workers` into the record of the slot this token holds (the runner calls it, inside the slot, before its
    workers start), so a later slot's admission counts this slot's reserve at its n. The slot's path, or None if no
    slot holds the token."""
    for sp in _slot_files(lock, MAX_SLOTS if n_slots is None else n_slots):
        rec = _parse(_read_raw(sp) or "")
        if rec is None or rec.get("token") != token:
            continue
        rec["workers"] = int(workers)
        rec["updated"] = now().isoformat()
        data = json.dumps(rec, indent=2)
        for _ in range(20):
            try:
                sp.write_text(data, encoding="utf-8")
                return sp
            except PermissionError:
                time.sleep(0.05)
        return None
    return None


def _survey(slots: list[Path]) -> tuple[list[Path], dict[Path, str]]:
    """The free slots (a stale holder taken over, said) and the live holders' raw records, in slot order."""
    free, held = [], {}
    for sp in slots:
        raw = _read_raw(sp)
        if raw is None:
            free.append(sp)
            continue
        why = stale_reason(sp, raw)
        if why is not None and _take_over(sp, raw):
            _say(f"taking over a stale fast-tier lock {sp}: {why}")
            free.append(sp)
            continue
        held[sp] = raw
    return free, held


def acquire(path: Path, tree: str, timeout_s: float = TIMEOUT_S, poll_s: float = POLL_S,
            sleep: Sleep = time.sleep, monotonic: Clock = time.monotonic, free_gb: Callable = available_gb,
            max_slots: int | None = None, reserve_gb: float | None = None, min_free_gb: float = MIN_FREE_GB) -> Holder:
    """Take a slot in arrival order (Q-165, Q-174): wait for every live waiter that arrived earlier; at the head of the
    line take a free slot when none is running, or when `free_gb()` is at least `min_free_gb` + `reserve_gb` for every
    slot running; take over a stale holder. WaitTimeout after `timeout_s`. The ticket is removed on every exit."""
    n_slots = max(1, MAX_SLOTS if max_slots is None else max_slots)
    reserve = SLOT_RESERVE_GB if reserve_gb is None else reserve_gb
    slots = [slot_path(path, i) for i in range(n_slots)]
    t0 = monotonic()
    t_still = t0                                          # when the jobs holding the slots last changed
    last_jobs: tuple | None = None
    last_print: float | None = None
    token = uuid.uuid4().hex
    q = queue_dir(path)
    lead = is_main_worktree(tree)                         # Q-207: from the tree's own git, never from a flag
    mine = ticket_name(time.time_ns(), os.getpid(), token, heartbeat=True, lead=lead)
    lead_note = " (the main tree's ticket: ahead of every worker's, Q-207)" if lead else ""
    ticket = _make_ticket(q, mine)
    try:
        while True:
            if ticket.exists():
                _beat(ticket)                             # Q-199: the heartbeat, on every poll
            else:
                ticket = _make_ticket(q, mine)            # removed under us (an old tree's age prune): same place
            ahead = line(q, mine)
            place = ahead.index(mine) + 1
            memory_note = ""
            if place == 1:
                free, held_raw = _survey(slots)
                if free:
                    running = len(held_raw)
                    ok = running == 0                     # nothing running: today's rule, the memory wait follows
                    if not ok:
                        gb = free_gb()
                        # each running slot at its own workers' reserve (Q-193); a serial slot's is `reserve`
                        need = min_free_gb + sum(slot_reserve_gb(workers_of(_parse(r)), reserve)
                                                 for r in held_raw.values())
                        ok = gb is not None and gb >= need
                        if not ok:
                            memory_note = (f"; slot {slots.index(free[0]) + 1} of {n_slots} is free but needs "
                                           f"{need:.1f} GB available beside {running} running "
                                           f"({'memory unknown' if gb is None else f'{gb:.1f} GB now'})")
                    if ok:
                        for sp in free:
                            stamp = now().isoformat()
                            record = {"tree": tree, "pid": os.getpid(), "host": socket.gethostname(), "start": stamp,
                                      "updated": stamp, "phase": "waiting-for-memory", "token": token,
                                      "slot": slots.index(sp)}
                            if try_create(sp, record):
                                return Holder(token, record, sp)
                        continue                          # every free slot was taken under us: look again
                raws = [held_raw[sp] for sp in slots if sp in held_raw]
            else:
                raws = [r for r in (_read_raw(sp) for sp in slots) if r]
            held = "; ".join(describe(_parse(r)) for r in raws) if raws else "nobody (an earlier waiter is taking it)"
            held += memory_note
            # The cap counts only a line that does not move: the timer restarts whenever the set of jobs holding the
            # slots changes (a holder leaves, a new one takes a slot -- each job has its own token). A holder's
            # heartbeat under the same token is the same job; a stuck holder still runs the cap out, and a dead or
            # 2-hour-old one is taken over as before.
            jobs = tuple(sorted(((_parse(r) or {}).get("token") or r) for r in raws))
            if jobs != last_jobs:
                if last_jobs is not None:
                    t_still = monotonic()
                last_jobs = jobs
            still = monotonic() - t_still
            total = monotonic() - t0
            if still >= timeout_s:
                raise WaitTimeout(f"FAILED: the fast-tier lock {path} stayed held by {held} for the whole wait "
                                  f"({timeout_s / 60:.0f} min without the line moving, {total / 60:.0f} min in all; "
                                  f"place {place} of {len(ahead)} in line); the fast tier did not run and the commit "
                                  f"is refused. See `python scripts/fasttier_lock.py status`; commit again when it is "
                                  f"free.")
            if last_print is None or monotonic() - last_print >= PRINT_EVERY_S:
                _say(f"fast-tier lock held by {held}; waiting, place {place} of {len(ahead)} in line{lead_note} "
                     f"({total / 60:.0f} min in all; {still / 60:.0f} of {timeout_s / 60:.0f} min without the line "
                     f"moving)")
                last_print = monotonic()
            sleep(poll_s)
    finally:
        _unlink(ticket)


def refresh(path: Path, holder: Holder, phase: str) -> bool:
    """Rewrite this holder's record (`updated`, `phase`); False if the lock is no longer this holder's."""
    rec = _parse(_read_raw(path) or "")
    if rec is None or rec.get("token") != holder.token:
        return False
    rec["updated"] = now().isoformat()
    rec["phase"] = phase
    data = json.dumps(rec, indent=2)
    for _ in range(20):
        try:
            path.write_text(data, encoding="utf-8")
            break
        except PermissionError:
            time.sleep(0.05)
    holder.record = rec
    return True


def release(path: Path, holder: Holder) -> None:
    """Remove the lock if, and only if, it is still this holder's."""
    rec = _parse(_read_raw(path) or "")
    if rec is not None and rec.get("token") == holder.token:
        _unlink(path)


def wait_for_memory(path: Path, holder: Holder, min_free_gb: float, deadline_s: float, free_gb: Callable,
                    poll_s: float, sleep: Sleep, monotonic: Clock, t0: float) -> float | None:
    """Wait, holding the lock, until `free_gb()` reaches `min_free_gb`; the last reading (None: unknown)."""
    last_print: float | None = None
    while True:
        gb = free_gb()
        if gb is None:
            _say("free memory unknown on this machine; the fast tier starts without the memory wait")
            return None
        if gb >= min_free_gb:
            return gb
        elapsed = monotonic() - t0
        if elapsed >= deadline_s:
            raise WaitTimeout(f"FAILED: free physical memory stayed below {min_free_gb:.1f} GB (last {gb:.2f} GB) "
                              f"for the whole wait ({deadline_s / 60:.0f} min); the fast tier did not run and the "
                              f"commit is refused. Free memory (a heavy run, other sessions) and commit again.")
        if last_print is None or monotonic() - last_print >= PRINT_EVERY_S:
            _say(f"{gb:.2f} GB free, the fast tier needs {min_free_gb:.1f} GB; waiting, holding the lock "
                 f"({elapsed / 60:.0f} of {deadline_s / 60:.0f} min)")
            last_print = monotonic()
        sleep(poll_s)
        if not refresh(path, holder, "waiting-for-memory"):
            raise LockLost(f"FAILED: the fast-tier lock {path} was taken from this hook while it waited for memory")


def _subprocess_runner(cmd: list[str], env: dict, tee: str | None = None) -> int:
    """Run `cmd`; its exit code. With `tee`, its output (stdout and stderr together) is printed and also appended to
    that file; if this process is interrupted (a signal's SystemExit, Ctrl+C, a closed output pipe), the command is
    killed rather than left running as an orphan, and the interruption propagates."""
    if not tee:
        return subprocess.run(cmd, env=env).returncode
    with open(tee, "ab") as f:
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            out = sys.stdout.buffer
            for chunk in iter(lambda: proc.stdout.read1(65536), b""):
                f.write(chunk)
                f.flush()
                out.write(chunk)
                out.flush()
            return proc.wait()
        except BaseException:
            proc.kill()
            proc.wait()
            raise


def run(cmd: list[str], lock: Path, tree: str, min_free_gb: float = MIN_FREE_GB, timeout_s: float = TIMEOUT_S,
        poll_s: float = POLL_S, free_gb: Callable = available_gb, sleep: Sleep = time.sleep,
        monotonic: Clock = time.monotonic, runner: Callable[[list[str], dict], int] = _subprocess_runner,
        env: dict | None = None, max_slots: int | None = None, reserve_gb: float | None = None) -> int:
    """Run `cmd` in a slot of the lock, after the memory wait; its exit code. Raises WaitTimeout / LockLost.

    `S2X_FASTTIER_TEE` in the environment names a file the command's output is copied into (Q-161); it is removed from
    the command's own environment, so a nested run never writes into the outer hook's file."""
    env = dict(os.environ if env is None else env)
    tee = env.pop(ENV_TEE, None) or None
    n_slots = max(1, MAX_SLOTS if max_slots is None else max_slots)

    def _run(c: list[str], e: dict) -> int:
        return _subprocess_runner(c, e, tee) if runner is _subprocess_runner else runner(c, e)

    inherited = env.get(ENV_TOKEN)
    if inherited:
        for sp in _slot_files(lock, n_slots):
            rec = _parse(_read_raw(sp) or "")
            if rec is not None and rec.get("token") == inherited:
                _say("the fast-tier lock is already held by the run this commit is nested in; running under it")
                return _run(cmd, env)
    holder = acquire(lock, tree, timeout_s=timeout_s, poll_s=poll_s, sleep=sleep, monotonic=monotonic,
                     free_gb=free_gb, max_slots=n_slots, reserve_gb=reserve_gb, min_free_gb=min_free_gb)
    sp = holder.path or lock
    t0 = monotonic()                                      # the memory wait has its own cap, from the slot's taking
    try:
        gb = wait_for_memory(sp, holder, min_free_gb, timeout_s, free_gb, poll_s, sleep, monotonic, t0)
        if not refresh(sp, holder, "fast-tier"):
            raise LockLost(f"FAILED: the fast-tier lock {sp} was taken from this hook before its fast tier started")
        _say(f"fast-tier lock taken ({sp}; slot {holder.record.get('slot', 0) + 1} of {n_slots}; "
             f"{'memory unknown' if gb is None else f'{gb:.1f} GB free'})")
        env[ENV_TOKEN] = holder.token
        return _run(cmd, env)
    finally:
        release(sp, holder)


def status(lock: Path) -> int:
    gb = available_gb()
    mem = "memory unknown" if gb is None else f"{gb:.1f} GB available"
    slots = _slot_files(lock, MAX_SLOTS)
    print(f"fast-tier lock: {MAX_SLOTS} slot(s) ({ENV_SLOTS}); a further slot opens at {MIN_FREE_GB:.1f} GB + "
          f"{SLOT_RESERVE_GB:.1f} GB per running slot, + {PER_WORKER_GB:.1f} GB per further xdist worker in it, "
          f"available  ({mem})")
    for i, sp in enumerate(slots):
        raw = _read_raw(sp)
        if raw is None:
            print(f"{sp}: slot {i + 1} of {len(slots)}: FREE")
            continue
        why = stale_reason(sp, raw)
        print(f"{sp}: slot {i + 1} of {len(slots)}: HELD by {describe(_parse(raw))}"
              + (f"  ** STALE: {why}; the next hook takes it over **" if why else ""))
    q = queue_dir(lock)
    names = sorted(t.name for t in q.iterdir()) if q.is_dir() else []
    live = [n for n in names                              # read only: the waiters themselves remove dead tickets
            if parse_ticket(n) is not None and pid_alive(parse_ticket(n)[1])]
    for place, name in enumerate(order_line(live), start=1):      # the line's own order (Q-207)
        arrival_ns, pid, _ = parse_ticket(name)
        since = datetime.fromtimestamp(arrival_ns / 1e9, timezone.utc).replace(microsecond=0).isoformat()
        klass = ticket_class(name)
        kind = ("; the lead (the main tree): ahead of every worker" if klass == "lead"
                else "" if klass == "worker" else "; a tree without Q-207: keeps its arrival place")
        print(f"  {place}. waiting since {since} (pid {pid}{kind})")
    return 0


def _exit_on_signal(signum, _frame):
    raise SystemExit(128 + signum)                        # unwinds through run()'s finally: the lock is released


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lock", type=Path, default=None, help="the lock file (default %%LOCALAPPDATA%%\\" + LOCK_NAME + ")")
    ap.add_argument("--timeout-s", type=float, default=TIMEOUT_S)
    ap.add_argument("--poll-s", type=float, default=POLL_S)
    ap.add_argument("--min-free-gb", type=float, default=MIN_FREE_GB)
    sub = ap.add_subparsers(dest="action", required=True)
    r = sub.add_parser("run", help="run a command under the lock")
    r.add_argument("cmd", nargs=argparse.REMAINDER)
    sub.add_parser("status")
    a = ap.parse_args(argv)
    lock = _refuse_onedrive(a.lock) if a.lock else default_lock_path()
    if a.action == "status":
        return status(lock)
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("run needs a command after --")
    for name in ("SIGTERM", "SIGBREAK"):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), _exit_on_signal)
    try:
        return run(cmd, lock, tree=os.getcwd(), min_free_gb=a.min_free_gb, timeout_s=a.timeout_s, poll_s=a.poll_s)
    except WaitTimeout as e:
        print(f"pre-commit: {e}", file=sys.stderr, flush=True)
        return EXIT_TIMEOUT
    except LockLost as e:
        print(f"pre-commit: {e}", file=sys.stderr, flush=True)
        return EXIT_LOST


if __name__ == "__main__":
    sys.exit(main())
