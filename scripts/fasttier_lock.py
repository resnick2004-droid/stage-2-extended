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
   least 1.5 GB plus SLOT_RESERVE_GB (2.5 GB, a measured fast tier's peak with a margin; SLOT_RESERVE_SOURCE) for every
   slot running -- otherwise it keeps its place and waits, so with one slot's worth of memory nothing changes;
2. **waits for a live holder, first come first served** (Q-165), polling every 30 s and printing one line a minute
   with its place in line: on arrival a waiter takes a ticket -- a file created atomically in the queue directory
   beside the lock (`<lock>.queue/`), named by its arrival time, pid and token -- and takes the lock only while its
   ticket is the oldest live one. A ticket whose process is not running, or older than the 3-hour cap, is skipped and
   removed, never honoured. The ticket is removed on every exit path; a hard kill leaves it with a dead pid;
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

The whole wait (lock and memory together) is bounded by 3 hours; at the bound `run` prints FAILED with the holder and
exits 75, and the hook fails. It never passes silently. What the hook checks is unchanged: this only orders the runs.

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

LOCK_NAME = "stage2-extended-fasttier.lock"
ENV_TOKEN = "S2X_FASTTIER_TOKEN"
ENV_TEE = "S2X_FASTTIER_TEE"     # Q-161: a file the command's output is copied into (the hook's verdict reads its pass line)
ENV_SLOTS = "S2X_FASTTIER_SLOTS"  # Q-174: how many fast tiers may run at once (default DEFAULT_SLOTS, at least 1)
DEFAULT_SLOTS = 2
#: Q-174: a running fast tier's peak memory, and the reserve declared from it. A further slot opens only while available
#: memory >= MIN_FREE_GB + SLOT_RESERVE_GB for every slot already running (so a second slot needs 4.0 GB beside one).
MEASURED_PEAK_GB = 2.26
SLOT_RESERVE_GB = 2.5
SLOT_RESERVE_SOURCE = (
    "scripts/tree_peak_memory.py --attach on the main tree's own pre-commit fast tier, 2026-11-20 11:07:54-11:45:55Z "
    "(2230 samples at 1 s over the wrapper, pytest and every child): peak tree working set 2.257 GB (private commit "
    "5.385 GB, up to 91 processes; machine-wide available memory fell to 0.018 GB). The reserve is that peak rounded up "
    "with about 10 % for spikes between samples; one full run measured (a second, partial, peaked lower)."
)
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
            f" (phase {rec.get('phase')}, updated {rec.get('updated')})")


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


def ticket_name(arrival_ns: int, pid: int, token: str) -> str:
    """Sorts by arrival time (fixed-width nanoseconds), then pid, then token."""
    return f"{arrival_ns:020d}-{pid:010d}-{token}.ticket"


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


def line(q: Path, mine: str, cap_s: float = TIMEOUT_S) -> list[str]:
    """The live tickets, oldest first. A ticket whose process is not running, or older than the cap, is removed here
    (never honoured); this waiter's own ticket (`mine`) is always kept."""
    if not q.is_dir():
        return []
    live = []
    now_ns = time.time_ns()
    for t in sorted(q.iterdir(), key=lambda x: x.name):
        parsed = parse_ticket(t.name)
        if parsed is None:
            continue
        if t.name != mine:
            arrival_ns, pid, _ = parsed
            if not pid_alive(pid) or (now_ns - arrival_ns) / 1e9 > cap_s:
                _unlink(t)
                continue
        live.append(t.name)
    return live


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
    last_print: float | None = None
    token = uuid.uuid4().hex
    q = queue_dir(path)
    mine = ticket_name(time.time_ns(), os.getpid(), token)
    ticket = _make_ticket(q, mine)
    try:
        while True:
            if not ticket.exists():
                ticket = _make_ticket(q, mine)            # removed under us: back in, at the same place
            ahead = line(q, mine)
            place = ahead.index(mine) + 1 if mine in ahead else 1
            memory_note = ""
            if place == 1:
                free, held_raw = _survey(slots)
                if free:
                    running = len(held_raw)
                    ok = running == 0                     # nothing running: today's rule, the memory wait follows
                    if not ok:
                        gb = free_gb()
                        need = min_free_gb + reserve * running
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
            elapsed = monotonic() - t0
            if elapsed >= timeout_s:
                raise WaitTimeout(f"FAILED: the fast-tier lock {path} stayed held by {held} for the whole wait "
                                  f"({timeout_s / 60:.0f} min; place {place} of {len(ahead)} in line); the fast tier "
                                  f"did not run and the commit is refused. See `python scripts/fasttier_lock.py "
                                  f"status`; commit again when it is free.")
            if last_print is None or monotonic() - last_print >= PRINT_EVERY_S:
                _say(f"fast-tier lock held by {held}; waiting, place {place} of {len(ahead)} in line "
                     f"({elapsed / 60:.0f} of {timeout_s / 60:.0f} min)")
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
    t0 = monotonic()
    holder = acquire(lock, tree, timeout_s=timeout_s, poll_s=poll_s, sleep=sleep, monotonic=monotonic,
                     free_gb=free_gb, max_slots=n_slots, reserve_gb=reserve_gb, min_free_gb=min_free_gb)
    sp = holder.path or lock
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
          f"{SLOT_RESERVE_GB:.1f} GB per running slot available  ({mem})")
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
    place = 0
    for name in names:                                    # read only: the waiters themselves remove dead tickets
        parsed = parse_ticket(name)
        if parsed is None or not pid_alive(parsed[1]):
            continue
        place += 1
        since = datetime.fromtimestamp(parsed[0] / 1e9, timezone.utc).replace(microsecond=0).isoformat()
        print(f"  {place}. waiting since {since} (pid {parsed[1]})")
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
