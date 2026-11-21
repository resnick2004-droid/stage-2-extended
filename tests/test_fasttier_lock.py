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


@pytest.fixture(autouse=True)
def single_slot(monkeypatch):
    """These are the single-slot lock's tests (Q-155, Q-165): one slot, in this process and in every CLI child. The
    slots of Q-174 have their own tests (tests/test_fasttier_slots.py), including one-slot behaviour at two slots."""
    monkeypatch.setattr(F, "MAX_SLOTS", 1)
    monkeypatch.setenv(F.ENV_SLOTS, "1")


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


def test_a_live_ticket_older_than_the_cap_and_not_recreated_lately_is_skipped_and_removed(lock):
    """Q-199 narrowed this (it was: any live ticket past the cap by arrival): an old-code ticket past the cap whose file
    is older than TICKET_STALE_S -- a pid reused after its owner died -- is removed."""
    q = F.queue_dir(lock)
    q.mkdir()
    old_ns = time.time_ns() - int((F.TIMEOUT_S + 60) * 1e9)
    old = q / F.ticket_name(old_ns, os.getpid(), "0ld0ld")
    old.write_text("", encoding="utf-8")
    then = time.time() - F.TICKET_STALE_S - 60
    os.utime(old, (then, then))
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


# ------------------------------------------------------------------------------------------------ the cap counts a line that does not move (Q-174)

def test_a_long_line_of_short_holders_never_times_out_the_waiter(lock, clock):
    """Twelve holders of 60 s each (each a different job) ahead of a waiter whose cap is 100 s: the line keeps moving,
    so the waiter waits the whole 720 s and then takes the lock."""
    plant(lock, os.getpid(), token="job-0")
    jobs = [0]

    def sleep(s):
        clock.sleep(s)
        if clock.t >= 60 * (jobs[0] + 1):
            jobs[0] += 1
            if jobs[0] < 12:
                plant(lock, os.getpid(), token=f"job-{jobs[0]}", tree=f"C:/other/wt-{jobs[0]}")
            else:
                lock.unlink(missing_ok=True)

    h = F.acquire(lock, tree="last", timeout_s=100, poll_s=5, sleep=sleep, monotonic=clock.monotonic)
    assert h.record["tree"] == "last" and clock.t >= 720
    F.release(lock, h)


def test_a_stuck_live_holder_still_times_out_the_waiter_at_the_cap(lock, clock):
    plant(lock, os.getpid(), token="stuck")
    with pytest.raises(F.WaitTimeout) as e:
        acquire(lock, clock, timeout_s=100, poll_s=5)
    assert 100 <= clock.t < 110
    assert "without the line moving" in str(e.value)


def test_a_holder_heartbeat_of_the_same_job_is_not_progress(lock, clock):
    """A holder refreshing its own record (its token unchanged) is the same job: the cap still runs."""
    plant(lock, os.getpid(), token="same")

    def sleep(s):
        clock.sleep(s)
        plant(lock, os.getpid(), token="same")                  # a fresh `updated`, the same job

    with pytest.raises(F.WaitTimeout):
        F.acquire(lock, tree="T", timeout_s=100, poll_s=5, sleep=sleep, monotonic=clock.monotonic)
    assert clock.t < 110


def test_the_cap_restarts_at_each_new_holder_and_counts_from_the_last(lock, clock):
    """One change of job at 80 s, then the new holder sticks: the cap runs out 100 s after the change."""
    plant(lock, os.getpid(), token="first")

    def sleep(s):
        clock.sleep(s)
        if clock.t == 80:
            plant(lock, os.getpid(), token="second")

    with pytest.raises(F.WaitTimeout):
        F.acquire(lock, tree="T", timeout_s=100, poll_s=5, sleep=sleep, monotonic=clock.monotonic)
    assert 180 <= clock.t < 190


def test_the_memory_wait_has_its_own_cap_from_the_moment_the_lock_is_taken(lock, clock):
    """A long but moving line does not use up the memory wait's bound."""
    plant(lock, os.getpid(), token="job-0")
    jobs = [0]

    def sleep(s):
        clock.sleep(s)
        if lock.exists() and clock.t >= 60 * (jobs[0] + 1) and jobs[0] < 3:
            jobs[0] += 1
            if jobs[0] < 3:
                plant(lock, os.getpid(), token=f"job-{jobs[0]}")
            else:
                lock.unlink()

    free = iter([0.5, 0.5] + [9.0] * 1000)
    rc = F.run(["x"], lock=lock, tree="T", min_free_gb=1.5, timeout_s=100, poll_s=5, free_gb=lambda: next(free),
               sleep=sleep, monotonic=clock.monotonic, runner=lambda c, e: 0)
    assert rc == 0 and clock.t >= 180


# ------------------------------------------------------------------------------------ a live waiter's ticket is never dropped by age (Q-199)
#
# Since Q-174 a waiter's cap counts only a line that does not move, so a live waiter may wait longer than TIMEOUT_S in
# all. A ticket's staleness is therefore its pid and its heartbeat (the owner touches it on every poll), never its
# arrival. A ticket without the heartbeat mark was written by a tree that has not merged Q-199 (it never touches its
# ticket), and is judged exactly as that tree judges it: pid alive and arrival within the cap.

H4 = int(4 * 3600 * 1e9)                                       # four hours, in ns: past TIMEOUT_S by arrival


def _hb_ticket(q: Path, arrival_ns: int, pid: int, token: str, beat_age_s: float = 0.0) -> Path:
    q.mkdir(parents=True, exist_ok=True)
    t = q / F.ticket_name(arrival_ns, pid, token, heartbeat=True)
    t.write_text("", encoding="utf-8")
    if beat_age_s:
        then = time.time() - beat_age_s
        os.utime(t, (then, then))
    return t


def test_the_heartbeat_bound_is_declared_from_the_poll():
    """Several polls' and printed lines' worth, far under the cap: a live waiter beats every POLL_S."""
    assert F.TICKET_STALE_S == 10 * 60
    assert F.TICKET_STALE_S >= 10 * F.POLL_S and F.TICKET_STALE_S >= 5 * F.PRINT_EVERY_S
    assert F.TICKET_STALE_S < F.STALE_AFTER.total_seconds() < F.TIMEOUT_S


def test_a_heartbeat_ticket_is_marked_in_its_name_and_still_parses_as_the_old_code_parses_it():
    name = F.ticket_name(123, 456, "abc", heartbeat=True)
    assert F.is_heartbeat_ticket(name) and not F.is_heartbeat_ticket(F.ticket_name(123, 456, "abc"))
    arrival, pid, _ = F.parse_ticket(name)                    # the three fields an old-code tree reads
    assert (arrival, pid) == (123, 456)
    assert sorted([F.ticket_name(200, 1, "a"), name]) == [name, F.ticket_name(200, 1, "a")]   # arrival still orders


def test_a_live_waiter_older_than_the_cap_by_arrival_is_kept_and_keeps_its_place(tmp_path):
    q = tmp_path / "q"
    old = _hb_ticket(q, time.time_ns() - H4, os.getpid(), "old")
    mine = _hb_ticket(q, time.time_ns(), os.getpid(), "young").name
    assert F.line(q, mine) == [old.name, mine]
    assert old.exists()


def test_a_dead_pid_heartbeat_ticket_is_removed_however_fresh(tmp_path):
    q = tmp_path / "q"
    dead = _hb_ticket(q, time.time_ns() - 10**9, dead_pid(), "dead")
    mine = _hb_ticket(q, time.time_ns(), os.getpid(), "me").name
    assert F.line(q, mine) == [mine] and not dead.exists()


def test_a_live_pid_with_a_stale_heartbeat_is_removed_however_young_its_arrival(tmp_path):
    """A pid that is running but has not beaten for TICKET_STALE_S: a reused pid, or a waiter hung outside its loop."""
    q = tmp_path / "q"
    stale = _hb_ticket(q, time.time_ns() - 10**9, os.getpid(), "stale", beat_age_s=F.TICKET_STALE_S + 60)
    fresh = _hb_ticket(q, time.time_ns() - 10**9 + 1, os.getpid(), "fresh", beat_age_s=F.TICKET_STALE_S - 60)
    mine = _hb_ticket(q, time.time_ns(), os.getpid(), "me").name
    assert F.line(q, mine) == [fresh.name, mine] and not stale.exists()


def test_an_old_code_ticket_is_kept_within_the_cap_and_past_it_only_while_recreated(tmp_path):
    """Mixed trees: a ticket without the mark is never touched by its owner. Within the cap by arrival it is kept while
    its pid lives, whatever its mtime (old code's rule). Past the cap it is kept while it was (re)created within
    TICKET_STALE_S -- its live owner puts it back after every old tree's age prune -- and removed once older: a dead
    owner whose pid was reused never recreates it."""
    q = tmp_path / "q"
    q.mkdir()
    past_cap = time.time_ns() - int((F.TIMEOUT_S + 60) * 1e9)
    expired = q / F.ticket_name(past_cap, os.getpid(), "expired")
    recreated = q / F.ticket_name(past_cap + 1, os.getpid(), "recreated")
    legacy = q / F.ticket_name(time.time_ns() - 10**9, os.getpid(), "legacy")
    for t, beat_age in ((expired, F.TICKET_STALE_S + 60), (recreated, 30), (legacy, 3600)):
        t.write_text("", encoding="utf-8")
        then = time.time() - beat_age
        os.utime(t, (then, then))
    mine = _hb_ticket(q, time.time_ns(), os.getpid(), "me").name
    assert F.line(q, mine) == [recreated.name, legacy.name, mine]
    assert legacy.exists() and recreated.exists() and not expired.exists()


def test_a_live_old_code_waiter_past_the_cap_holds_its_place_before_a_new_code_waiter(lock, clock):
    """The waiter seen on 2026-11-20 (an old-code tree, 4.6 h by arrival): old trees' age prune removes its ticket every
    poll and it puts it back every poll; a new-code waiter keeps it in line and takes no free slot ahead of it."""
    q = F.queue_dir(lock)
    q.mkdir()
    old = q / F.ticket_name(time.time_ns() - H4, os.getpid(), "oldtree")         # no heartbeat mark
    old.write_text("", encoding="utf-8")

    def sleep(s):
        clock.sleep(s)
        old.unlink()                                           # an old tree's line() prunes it by arrival ...
        old.write_text("", encoding="utf-8")                   # ... and its owner's next poll puts it back

    with pytest.raises(F.WaitTimeout) as e:
        F.acquire(lock, tree="new", timeout_s=90, poll_s=5, sleep=sleep, monotonic=clock.monotonic)
    assert not lock.exists() and old.exists()
    assert "place 2 of 2" in str(e.value)


def test_the_line_always_holds_mine_at_its_arrival_place_even_while_its_file_is_missing(tmp_path):
    q = tmp_path / "q"
    first = _hb_ticket(q, 1_000, os.getpid(), "first")
    last = _hb_ticket(q, 3_000, os.getpid(), "last")
    mine = F.ticket_name(2_000, os.getpid(), "me", heartbeat=True)      # removed under its owner a moment ago
    assert F.line(q, mine) == [first.name, mine, last.name]


def test_a_younger_waiter_cannot_take_a_free_slot_ahead_of_an_older_live_waiter(lock, clock):
    """The defect seen on 2026-11-20: a live waiter past the cap by arrival was dropped by every later waiter."""
    old = _hb_ticket(F.queue_dir(lock), time.time_ns() - H4, os.getpid(), "old")

    def sleep(s):
        clock.sleep(s)
        os.utime(old, None)                                    # the old waiter is alive and polling

    with pytest.raises(F.WaitTimeout) as e:
        F.acquire(lock, tree="young", timeout_s=90, poll_s=5, sleep=sleep, monotonic=clock.monotonic)
    assert not lock.exists() and old.exists()
    assert "place 2 of 2" in str(e.value)


def test_the_poll_touches_the_waiters_ticket(lock, clock):
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    q = F.queue_dir(lock)
    beats = []

    def sleep(s):
        clock.sleep(s)
        (t,) = list(q.glob("*.ticket"))
        assert F.is_heartbeat_ticket(t.name)
        beats.append(time.time() - t.stat().st_mtime)
        then = time.time() - 3600
        os.utime(t, (then, then))                              # make the next beat visible

    with pytest.raises(F.WaitTimeout):
        F.acquire(lock, tree="T", timeout_s=60, poll_s=5, sleep=sleep, monotonic=clock.monotonic)
    assert len(beats) >= 10
    assert all(age < 60 for age in beats[1:]), beats           # every poll after the first found a fresh beat


def test_a_ticket_dropped_by_an_old_code_tree_is_recreated_under_its_old_name(lock, clock):
    """An old-code tree's line() removes a ticket older than the cap by arrival; the owner puts it back at once, under
    the same name (the same arrival, so the same place), heartbeat mark included."""
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    q = F.queue_dir(lock)
    names = []

    def sleep(s):
        clock.sleep(s)
        (t,) = list(q.glob("*.ticket"))
        names.append(t.name)
        t.unlink()                                             # what an old-code waiter's line() does

    with pytest.raises(F.WaitTimeout):
        F.acquire(lock, tree="T", timeout_s=60, poll_s=5, sleep=sleep, monotonic=clock.monotonic)
    assert len(names) >= 10 and len(set(names)) == 1 and F.is_heartbeat_ticket(names[0])
    assert list(q.glob("*.ticket")) == []                      # and removed on exit


OLD_WAITER = r'''
import sys, time
sys.path.insert(0, {scripts!r})
_real = time.time_ns
time.time_ns = lambda: _real() - {offset}                      # this waiter "arrived" four hours ago
import fasttier_lock as F
sys.exit(F.main(["--lock", {lock!r}, "--poll-s", "0.2", "--min-free-gb", "0", "run", "--",
                 sys.executable, "-c", "open(" + repr({served!r}) + ", 'a').write('OLD ')"]))
'''


def test_two_live_processes_an_old_waiter_past_the_cap_is_served_before_a_younger_faster_one(lock, tmp_path):
    """End to end: a waiter whose arrival is four hours old, still polling, and a younger one polling four times as
    fast. The holder leaves; the old waiter is served first (under the age prune the younger one dropped its ticket)."""
    plant(lock, os.getpid(), tree="C:/other/wt-busy")
    served = tmp_path / "served.txt"
    script = tmp_path / "old_waiter.py"
    script.write_text(OLD_WAITER.format(scripts=str(ROOT / "scripts"), offset=H4, lock=str(lock), served=str(served)),
                      encoding="utf-8")
    procs = []
    outs = []
    try:
        procs.append(subprocess.Popen([sys.executable, str(script)], stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True))
        assert _wait_until(lambda: len(_tickets(lock)) == 1), "the old waiter took no ticket"
        young = f"open(r'{served}', 'a').write('YOUNG ')"
        procs.append(subprocess.Popen(_cli(lock, "--poll-s", "0.05", "--min-free-gb", "0", "run", "--",
                                           sys.executable, "-c", young),
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
        assert _wait_until(lambda: len(_tickets(lock)) == 2), "the young waiter took no ticket"
        time.sleep(1.0)                                        # several of the young waiter's polls with both in line
        assert len(_tickets(lock)) == 2, "a live waiter's ticket was dropped"
        lock.unlink()                                          # the holder finishes
        outs = [p.communicate(timeout=120)[0] for p in procs]
        assert all(p.returncode == 0 for p in procs), outs
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
    assert served.read_text(encoding="utf-8").split() == ["OLD", "YOUNG"], outs
    assert _tickets(lock) == [] and not lock.exists()
