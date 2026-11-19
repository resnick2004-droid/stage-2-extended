"""Q-155: the pre-commit fast tier runs one at a time on the machine, under `scripts/fasttier_lock.py`.

Several worktrees' hooks once ran the whole fast tier at the same moment; free memory fell near 0.5 GB and the hooks
died of `MemoryError`, OpenBLAS allocation errors and WinError 1455. The lock is a file under `%LOCALAPPDATA%` (never
OneDrive) that every tree's hook shares. These tests hold what it claims: it is taken atomically with its holder
recorded; a live holder is waited for; a dead pid or a holder older than two hours is taken over, said aloud; the wait
is bounded and its end is a failure with a message, never a silent pass; free memory is waited for before pytest; and
the lock is released on every exit path. Every test works on a temporary lock path with an injected clock and sleep;
**no real fast tier runs here** (the wrapped command is a one-line Python child).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from datetime import timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fasttier_lock as F  # noqa: E402


class Clock:
    """A fake monotonic clock and wall clock, advanced only by the injected sleep."""

    def __init__(self):
        self.t = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.sleeps.append(s)
        self.t += s


@pytest.fixture()
def lock(tmp_path) -> Path:
    return tmp_path / "fasttier.lock"


@pytest.fixture()
def clock() -> Clock:
    return Clock()


def dead_pid() -> int:
    """The pid of a process that has exited."""
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait(timeout=60)
    return p.pid


def plant(lock: Path, pid: int, age: timedelta = timedelta(0), tree: str = "C:/elsewhere/wt-x",
          token: str = "planted") -> dict:
    """A holder written by 'another hook'."""
    t = (F.now() - age).isoformat()
    rec = {"tree": tree, "pid": pid, "start": t, "updated": t, "phase": "fast-tier", "token": token}
    lock.write_text(json.dumps(rec), encoding="utf-8")
    return rec


def acquire(lock, clock, **kw):
    kw.setdefault("tree", "C:/this/tree")
    kw.setdefault("timeout_s", 3 * 3600)
    return F.acquire(lock, sleep=clock.sleep, monotonic=clock.monotonic, **kw)


# ------------------------------------------------------------------------------------------------ the lock itself

def test_acquire_records_the_holder_and_release_removes_it(lock, clock):
    h = acquire(lock, clock)
    rec = json.loads(lock.read_text(encoding="utf-8"))
    assert rec["tree"] == "C:/this/tree" and rec["pid"] == os.getpid() and rec["token"] == h.token
    assert F.parse_time(rec["start"]) is not None
    assert clock.sleeps == []                                   # free: no wait
    F.release(lock, h)
    assert not lock.exists()


def test_the_lock_file_is_created_exclusively(lock, clock):
    """Atomic: a second creator of the same path fails rather than overwriting (open(..., 'x'))."""
    assert F.try_create(lock, {"pid": 1, "token": "a"})
    assert not F.try_create(lock, {"pid": 2, "token": "b"})
    assert json.loads(lock.read_text(encoding="utf-8"))["token"] == "a"


def test_a_live_holder_is_waited_for_then_the_lock_is_taken(lock, capsys):
    """A live pid (this process, standing in for another hook) holds it; the waiter polls and takes it once freed."""
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    released_at = 95.0
    clock = Clock()

    def sleep(s):
        clock.sleep(s)
        if clock.t >= released_at and lock.exists():
            lock.unlink()                                       # the other hook finished

    h = F.acquire(lock, tree="C:/this/tree", timeout_s=3 * 3600, sleep=sleep, monotonic=clock.monotonic)
    assert h.token != "planted" and json.loads(lock.read_text(encoding="utf-8"))["token"] == h.token
    assert set(clock.sleeps) == {F.POLL_S} and F.POLL_S == 30   # polled every 30 s
    out = capsys.readouterr().out
    waits = [ln for ln in out.splitlines() if "waiting" in ln]
    assert waits and "C:/other/wt-busy" in waits[0]
    assert len(waits) <= int(clock.t // 60) + 1, "one line per minute, not one per poll"


def test_a_live_holder_is_never_taken_over_and_the_wait_times_out_with_a_message(lock, clock):
    rec = plant(lock, os.getpid(), tree="C:/other/wt-busy")
    with pytest.raises(F.WaitTimeout) as e:
        acquire(lock, clock, timeout_s=600)
    msg = str(e.value)
    assert "C:/other/wt-busy" in msg and "10 min" in msg
    assert json.loads(lock.read_text(encoding="utf-8")) == rec   # untouched
    assert clock.t >= 600


def test_a_dead_pid_is_taken_over_and_said(lock, clock, capsys):
    plant(lock, dead_pid(), tree="C:/other/wt-crashed")
    h = acquire(lock, clock)
    assert json.loads(lock.read_text(encoding="utf-8"))["token"] == h.token
    out = capsys.readouterr().out
    assert "stale" in out and "not running" in out and "C:/other/wt-crashed" in out


def test_a_holder_older_than_two_hours_is_taken_over_even_if_its_pid_lives(lock, clock, capsys):
    """Pid reuse or a hung run: the age bound is the backstop. Two hours is the declared bound."""
    assert F.STALE_AFTER == timedelta(hours=2)
    plant(lock, os.getpid(), age=timedelta(hours=2, minutes=1))
    h = acquire(lock, clock)
    assert json.loads(lock.read_text(encoding="utf-8"))["token"] == h.token
    assert "older than 2 h" in capsys.readouterr().out


def test_a_holder_just_under_two_hours_is_still_waited_for(lock, clock):
    plant(lock, os.getpid(), age=timedelta(hours=1, minutes=59))
    with pytest.raises(F.WaitTimeout):
        acquire(lock, clock, timeout_s=60)


def test_an_unreadable_lock_is_waited_for_while_young_and_taken_over_when_old(lock, clock, capsys):
    """A hook killed between creating and writing the file leaves it empty: young, it may be a write in flight."""
    lock.write_text("", encoding="utf-8")
    with pytest.raises(F.WaitTimeout):
        acquire(lock, clock, timeout_s=30)
    old = time.time() - 2 * F.UNREADABLE_GRACE_S
    os.utime(lock, (old, old))
    h = acquire(lock, clock)
    assert json.loads(lock.read_text(encoding="utf-8"))["token"] == h.token
    assert "unreadable" in capsys.readouterr().out


def test_release_never_removes_another_holders_lock(lock, clock):
    h = acquire(lock, clock)
    plant(lock, dead_pid(), token="someone-else")              # taken over meanwhile
    F.release(lock, h)
    assert json.loads(lock.read_text(encoding="utf-8"))["token"] == "someone-else"


def test_two_threads_never_hold_it_at_once(lock):
    """Atomic acquisition under contention: real sleeps, short polls, a shared counter of holders."""
    inside, peak, errors = [0], [0], []
    mu = threading.Lock()

    def worker(i):
        try:
            h = F.acquire(lock, tree=f"t{i}", timeout_s=60, poll_s=0.01, sleep=time.sleep, monotonic=time.monotonic)
            with mu:
                inside[0] += 1
                peak[0] = max(peak[0], inside[0])
            time.sleep(0.02)
            with mu:
                inside[0] -= 1
            F.release(lock, h)
        except Exception as e:  # pragma: no cover - reported below
            errors.append(e)

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=120)
    assert not errors and peak[0] == 1 and not lock.exists()


# ------------------------------------------------------------------------------------------------ the memory wait

def test_memory_is_waited_for_before_the_command(lock, clock):
    seen = iter([0.4, 0.9, 1.2, 1.6])
    ran = []
    code = F.run([sys.executable, "-c", "pass"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=3 * 3600,
                 free_gb=lambda: next(seen), sleep=clock.sleep, monotonic=clock.monotonic,
                 runner=lambda cmd, env: ran.append(clock.t) or 0)
    assert code == 0 and ran == [3 * F.POLL_S] and not lock.exists()
    assert F.MIN_FREE_GB == 1.5


def test_the_holder_refreshes_its_record_while_it_waits_for_memory(lock, clock):
    """Waiting for memory is not a hung holder: `updated` moves, so others do not take a live waiter's lock."""
    stamps = []

    def free():
        if lock.exists():
            stamps.append(json.loads(lock.read_text(encoding="utf-8"))["updated"])
        return 0.5 if len(stamps) < 3 else 2.0

    def sleep(s):
        clock.sleep(s)
        time.sleep(1.1)                                          # the record's clock has a one-second grain

    F.run(["x"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=3 * 3600, free_gb=free, sleep=sleep,
          monotonic=clock.monotonic, runner=lambda cmd, env: 0)
    assert len(set(stamps)) >= 2


def test_memory_that_never_frees_times_out_with_a_message_and_releases(lock, clock):
    with pytest.raises(F.WaitTimeout) as e:
        F.run(["x"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=300, free_gb=lambda: 0.5, sleep=clock.sleep,
              monotonic=clock.monotonic, runner=lambda cmd, env: pytest.fail("ran short of memory"))
    assert "1.5 GB" in str(e.value)
    assert not lock.exists()


def test_unknown_memory_does_not_block(lock, clock, capsys):
    code = F.run(["x"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=60, free_gb=lambda: None,
                 sleep=clock.sleep, monotonic=clock.monotonic, runner=lambda cmd, env: 0)
    assert code == 0 and "unknown" in capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ release on every path

def _run(lock, clock, runner):
    return F.run(["x"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=60, free_gb=lambda: 8.0, sleep=clock.sleep,
                 monotonic=clock.monotonic, runner=runner)


def test_a_failing_command_returns_its_code_and_releases(lock, clock):
    assert F.run([sys.executable, "-c", "raise SystemExit(5)"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=60,
                 free_gb=lambda: 8.0, sleep=clock.sleep, monotonic=clock.monotonic) == 5
    assert not lock.exists()


@pytest.mark.parametrize("exc", [RuntimeError("boom"), FileNotFoundError("no such python"), KeyboardInterrupt()])
def test_an_exception_or_interrupt_releases(lock, clock, exc):
    def runner(cmd, env):
        assert lock.exists()
        raise exc

    with pytest.raises(type(exc)):
        _run(lock, clock, runner)
    assert not lock.exists()


def test_the_command_sees_the_holders_token_and_a_nested_run_does_not_deadlock(lock, clock):
    """A commit made inside the fast tier (re-entry through the shared hook) runs under the lock it already holds."""
    def outer(cmd, env):
        assert env[F.ENV_TOKEN] == json.loads(lock.read_text(encoding="utf-8"))["token"]
        inner = F.run(["y"], lock=lock, tree="T2", min_free_gb=1.5, timeout_s=60, free_gb=lambda: 8.0,
                      sleep=clock.sleep, monotonic=clock.monotonic, runner=lambda c, e: 7, env=env)
        assert inner == 7 and lock.exists()                     # the inner run never released the outer's lock
        return 0

    assert _run(lock, clock, outer) == 0 and not lock.exists()


def test_a_holder_that_lost_its_lock_before_pytest_refuses(lock, clock):
    def free():
        plant(lock, os.getpid(), token="usurper")               # someone took it over while we waited
        return 8.0

    with pytest.raises(F.LockLost):
        F.run(["x"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=60, free_gb=free, sleep=clock.sleep,
              monotonic=clock.monotonic, runner=lambda cmd, env: pytest.fail("ran without the lock"))
    assert json.loads(lock.read_text(encoding="utf-8"))["token"] == "usurper"


# ------------------------------------------------------------------------------------------------ the command line

def test_the_cli_runs_the_command_under_the_lock(lock):
    probe = f"import json,sys; d=json.load(open(r'{lock}')); sys.exit(0 if d['pid'] > 0 else 9)"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "fasttier_lock.py"), "--lock", str(lock),
                           "--min-free-gb", "0", "run",                 # the memory wait has its own tests
                           "--", sys.executable, "-c", probe], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not lock.exists()


def test_the_cli_fails_loudly_on_timeout(lock):
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "fasttier_lock.py"), "--lock", str(lock),
                           "--timeout-s", "1", "--poll-s", "0.2", "run", "--", sys.executable, "-c", "pass"],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == F.EXIT_TIMEOUT != 0
    assert "FAILED" in proc.stderr and "C:/other/wt-busy" in proc.stderr
    assert lock.exists()                                         # a live holder's lock is left alone


def test_the_cli_status_names_the_holder(lock):
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "fasttier_lock.py"), "--lock", str(lock), "status"],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0 and "C:/other/wt-busy" in proc.stdout


def test_the_default_lock_is_machine_wide_and_never_under_onedrive(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert F.default_lock_path() == tmp_path / "stage2-extended-fasttier.lock"
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "OneDrive" / "x"))
    with pytest.raises(SystemExit):
        F.default_lock_path()


def test_the_wait_bounds_are_the_declared_ones():
    assert F.POLL_S == 30 and F.PRINT_EVERY_S == 60 and F.TIMEOUT_S == 3 * 3600
    assert F.STALE_AFTER == timedelta(hours=2) and F.MIN_FREE_GB == 1.5


# ------------------------------------------------------------------------------------------------ the hook's wiring

def test_the_pre_commit_hook_runs_the_fast_tier_under_the_lock():
    text = (ROOT / "scripts" / "pre-commit").read_text(encoding="utf-8")
    wrapped = '"$PYTHON" scripts/fasttier_lock.py run -- "$PYTHON" -m pytest -o addopts= -q -m "$FAST_TIER"\n'
    assert wrapped in text, "the fast tier must run inside the lock's wrapper"
    assert text.count("-m pytest") == 1, "no second, unlocked pytest"
    assert "[ ! -f scripts/fasttier_lock.py ]" in text, "a tree without the lock is refused, not run unlocked"
    # vendor integrity and the licence check are unchanged and come first
    assert text.index("scripts/vendor_stage2.py --verify || vendor_failed") < text.index(wrapped)
    assert text.index('scripts/check_price_levels.py --index "$COMMIT_INDEX" || price_level_failed') < text.index(
        wrapped)
    assert b"\r\n" not in (ROOT / "scripts" / "pre-commit").read_bytes()


# ------------------------------------------------------------------------------------------------ the tee (Q-161)

def test_the_cli_tees_the_commands_output_to_the_named_file_and_returns_its_code(lock, tmp_path):
    """The pre-commit hook records pytest's pass line in its verdict: the wrapper copies the command's output to the
    file named by S2X_FASTTIER_TEE, still prints it, returns the command's own code, and does not pass the variable on
    (a nested fast tier would otherwise write into the outer hook's file)."""
    out = tmp_path / "fasttier-last.log"
    child = "import os, sys; print('7 passed in 0.01s'); print('tee seen:', os.environ.get('S2X_FASTTIER_TEE')); sys.exit(3)"
    env = {**os.environ, F.ENV_TEE: str(out)}
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "fasttier_lock.py"), "--lock", str(lock), "--min-free-gb", "0", "run",
                           "--", sys.executable, "-c", child], capture_output=True, text=True, timeout=120, env=env)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert "7 passed in 0.01s" in proc.stdout
    text = out.read_text(encoding="utf-8")
    assert "7 passed in 0.01s" in text and "tee seen: None" in text
    assert not lock.exists()


def test_without_the_tee_variable_nothing_is_written(lock, tmp_path):
    env = {k: v for k, v in os.environ.items() if k != F.ENV_TEE}
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "fasttier_lock.py"), "--lock", str(lock), "--min-free-gb", "0", "run",
                           "--", sys.executable, "-c", "print('ok')"], capture_output=True, text=True, timeout=120,
                          env=env, cwd=tmp_path)
    assert proc.returncode == 0 and "ok" in proc.stdout
    assert [p.name for p in tmp_path.iterdir() if p != F.queue_dir(lock)] == []      # no tee file (the queue dir is the lock's)


# ------------------------------------------------------------------------------------------------ first come, first served (Q-165)

def _cli(lock: Path, *args: str) -> list[str]:
    return [sys.executable, str(ROOT / "scripts" / "fasttier_lock.py"), "--lock", str(lock), *args]


def _tickets(lock: Path) -> list[Path]:
    q = F.queue_dir(lock)
    return sorted(q.glob("*.ticket")) if q.is_dir() else []


def _wait_until(pred, limit: float = 60.0) -> bool:
    t0 = time.monotonic()
    while time.monotonic() - t0 < limit:
        if pred():
            return True
        time.sleep(0.05)
    return pred()


def test_three_waiters_are_served_in_the_order_they_arrived(lock, tmp_path):
    """A holder (this process) has the lock; A, B and C arrive in that order and wait. The fastest poller arrives
    last: without the queue it would usually take the freed lock first. With it, the order of service is A, B, C."""
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    served = tmp_path / "served.txt"
    procs = []
    try:
        for name, poll in (("A", "0.5"), ("B", "0.3"), ("C", "0.05")):
            child = f"import time; open(r'{served}', 'a').write('{name} '); time.sleep(0.3)"
            procs.append(subprocess.Popen(_cli(lock, "--poll-s", poll, "--min-free-gb", "0", "run", "--",
                                               sys.executable, "-c", child),
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
            n = len(procs)
            assert _wait_until(lambda: len(_tickets(lock)) == n), f"waiter {name} took no ticket"
        lock.unlink()                                             # the holder finishes
        outs = [p.communicate(timeout=120)[0] for p in procs]
        assert all(p.returncode == 0 for p in procs), outs
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
    assert served.read_text(encoding="utf-8").split() == ["A", "B", "C"]
    assert "place 3 of 3" in outs[2], outs[2]
    assert _tickets(lock) == [] and not lock.exists()


def test_a_dead_waiters_ticket_does_not_block_the_line_and_is_removed(lock, capsys):
    q = F.queue_dir(lock)
    q.mkdir()
    dead = q / F.ticket_name(time.time_ns() - 10**9, dead_pid(), "deadbeef")
    dead.write_text("", encoding="utf-8")
    h = F.acquire(lock, tree="T", timeout_s=30, poll_s=0.05)
    assert h.record["tree"] == "T"
    assert not dead.exists() and _tickets(lock) == []
    F.release(lock, h)


def test_a_live_ticket_older_than_the_cap_is_skipped_and_removed(lock):
    q = F.queue_dir(lock)
    q.mkdir()
    old_ns = time.time_ns() - int((F.TIMEOUT_S + 60) * 1e9)
    old = q / F.ticket_name(old_ns, os.getpid(), "0ld0ld")
    old.write_text("", encoding="utf-8")
    h = F.acquire(lock, tree="T", timeout_s=30, poll_s=0.05)
    assert not old.exists()
    F.release(lock, h)


def test_a_live_earlier_ticket_is_honoured(lock, clock):
    """A live waiter that arrived first keeps its place: a later waiter does not take a free lock past it."""
    q = F.queue_dir(lock)
    q.mkdir()
    first = q / F.ticket_name(time.time_ns() - 10**9, os.getpid(), "f1rst")
    first.write_text("", encoding="utf-8")
    with pytest.raises(F.WaitTimeout):
        acquire(lock, clock, timeout_s=90)
    assert not lock.exists() and first.exists()
    assert _tickets(lock) == [first], "the waiter that gave up left its ticket"


def test_a_waiter_killed_while_waiting_leaves_no_live_ticket(lock):
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    p = subprocess.Popen(_cli(lock, "--poll-s", "0.1", "run", "--", sys.executable, "-c", "pass"),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        assert _wait_until(lambda: len(_tickets(lock)) == 1), "the waiter took no ticket"
        p.kill()
        p.wait(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
    live = [t for t in _tickets(lock) if F.pid_alive(F.parse_ticket(t.name)[1])]
    assert live == [], live
    lock.unlink()
    h = F.acquire(lock, tree="next", timeout_s=30, poll_s=0.05)     # the line is not blocked by what was left
    assert _tickets(lock) == []
    F.release(lock, h)


def test_the_waiting_line_names_the_place(lock, clock, capsys):
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    with pytest.raises(F.WaitTimeout):
        acquire(lock, clock, timeout_s=90)
    assert "place 1 of 1" in capsys.readouterr().out
