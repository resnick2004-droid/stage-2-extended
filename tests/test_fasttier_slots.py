"""Q-174: the fast-tier lock serves up to MAX_SLOTS fast tiers at once, only when memory allows, in arrival order.

Slot 0 is the lock file itself (so a tree that has not merged this still contends for it); slot i >= 1 is
`<lock>.slot<i>`. A waiter at the head of the line takes a free slot when no slot is running (today's behaviour), or
when available memory is at least MIN_FREE_GB plus SLOT_RESERVE_GB for every slot already running; otherwise it waits
in its place. Each slot has its own holder record, heartbeat and takeover rule. Every test runs on a temporary lock
with stub commands (threads in this process, or the CLI in a child), the memory reading injected.
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

RESERVE = 2.0                      # the tests' own reserve, so they do not depend on the declared one


@pytest.fixture()
def lock(tmp_path) -> Path:
    return tmp_path / "fasttier.lock"


def dead_pid() -> int:
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait(timeout=60)
    return p.pid


def plant(path: Path, pid: int, tree: str = "C:/other/wt-busy", token: str = "planted", age=timedelta(0)) -> None:
    t = (F.now() - age).isoformat()
    path.write_text(json.dumps({"tree": tree, "pid": pid, "start": t, "updated": t, "phase": "fast-tier",
                                "token": token}), encoding="utf-8")


class Board:
    """What the stub commands saw: start order, the peak number running at once, which slot each held."""

    def __init__(self, hold_s: float = 0.4):
        self.mu = threading.Lock()
        self.running = 0
        self.peak = 0
        self.order: list[str] = []
        self.hold_s = hold_s
        self.gates: dict[str, threading.Event] = {}

    def runner(self, name: str, lock: Path):
        def _run(cmd, env):
            with self.mu:
                self.running += 1
                self.peak = max(self.peak, self.running)
                self.order.append(name)
            gate = self.gates.get(name)
            if gate is not None:
                gate.wait(timeout=60)
            else:
                time.sleep(self.hold_s)
            with self.mu:
                self.running -= 1
            return 0
        return _run


def start_waiter(board: Board, lock: Path, name: str, free_gb, errors: list, max_slots: int = 2,
                 reserve_gb: float = RESERVE) -> threading.Thread:
    def go():
        try:
            rc = F.run(["stub"], lock=lock, tree=name, min_free_gb=1.5, timeout_s=60, poll_s=0.02, free_gb=free_gb,
                       sleep=time.sleep, monotonic=time.monotonic, runner=board.runner(name, lock),
                       max_slots=max_slots, reserve_gb=reserve_gb, env={})
            assert rc == 0
        except BaseException as e:  # pragma: no cover - reported by the test
            errors.append(e)
    t = threading.Thread(target=go, name=name)
    t.start()
    return t


def in_line_or_running(lock: Path, board: Board, n: int) -> bool:
    q = F.queue_dir(lock)
    tickets = len(list(q.glob("*.ticket"))) if q.is_dir() else 0
    return tickets + len(board.order) >= n


def wait_until(pred, limit: float = 30.0) -> bool:
    t0 = time.monotonic()
    while time.monotonic() - t0 < limit:
        if pred():
            return True
        time.sleep(0.01)
    return pred()


def arrive_in_order(board, lock, names, free_gb, errors, **kw) -> list[threading.Thread]:
    ts = []
    for i, name in enumerate(names, 1):
        ts.append(start_waiter(board, lock, name, free_gb, errors, **kw))
        assert wait_until(lambda: in_line_or_running(lock, board, i)), f"{name} never arrived"
    return ts


def finish(ts, errors):
    for t in ts:
        t.join(timeout=60)
    assert not errors, errors
    assert not any(t.is_alive() for t in ts)


# ------------------------------------------------------------------------------------------------ the slots

def test_two_waiters_are_served_at_once_when_memory_is_ample(lock):
    board, errors = Board(hold_s=0.6), []
    ts = arrive_in_order(board, lock, ["A", "B", "C"], lambda: 10.0, errors)
    finish(ts, errors)
    assert board.peak == 2, "two fast tiers did not run at once with ample memory"
    assert board.order == ["A", "B", "C"]
    assert not lock.exists() and not F.slot_path(lock, 1).exists()


def test_one_at_a_time_when_memory_is_only_one_slots_worth(lock):
    """1.5 GB is free enough for one fast tier but below 1.5 + the reserve: exactly today's behaviour -- one at a time,
    in arrival order, slot 1 never used."""
    board, errors = Board(hold_s=0.3), []
    used_slot1 = []
    orig = F.try_create

    def watch(path, record):
        if path == F.slot_path(lock, 1):
            used_slot1.append(record)
        return orig(path, record)

    F.try_create, saved = watch, F.try_create
    try:
        ts = arrive_in_order(board, lock, ["A", "B", "C"], lambda: 1.5 + RESERVE - 0.01, errors)
        finish(ts, errors)
    finally:
        F.try_create = saved
    assert board.peak == 1 and board.order == ["A", "B", "C"]
    assert used_slot1 == [], "a second slot was taken without the memory for it"


def test_unknown_memory_never_opens_a_second_slot(lock):
    board, errors = Board(hold_s=0.3), []
    ts = arrive_in_order(board, lock, ["A", "B"], lambda: None, errors)
    finish(ts, errors)
    assert board.peak == 1 and board.order == ["A", "B"]


def test_the_second_slot_goes_to_the_head_of_the_line_never_to_a_later_waiter(lock):
    """A runs; B (head) waits for memory; C arrives behind B. When memory frees, B takes the second slot while A still
    runs; C waits until a slot is free."""
    board, errors = Board(), []
    gb = [2.0]
    board.gates = {"A": threading.Event(), "B": threading.Event(), "C": threading.Event()}
    ts = arrive_in_order(board, lock, ["A", "B", "C"], lambda: gb[0], errors)
    time.sleep(0.3)
    assert board.order == ["A"], "a second slot opened without the memory for it"
    gb[0] = 10.0
    assert wait_until(lambda: len(board.order) >= 2)
    time.sleep(0.3)
    assert board.order == ["A", "B"], "the second slot did not go to the head of the line"
    board.gates["A"].set()
    assert wait_until(lambda: len(board.order) == 3)
    board.gates["B"].set()
    board.gates["C"].set()
    finish(ts, errors)
    assert board.order == ["A", "B", "C"] and board.peak == 2


def test_max_slots_one_is_a_single_lock_whatever_the_memory(lock):
    board, errors = Board(hold_s=0.3), []
    ts = arrive_in_order(board, lock, ["A", "B", "C"], lambda: 64.0, errors, max_slots=1)
    finish(ts, errors)
    assert board.peak == 1 and board.order == ["A", "B", "C"]


def test_a_dead_slot_holder_is_taken_over_and_said(lock, capsys):
    plant(lock, os.getpid())                                          # slot 0: a live holder
    plant(F.slot_path(lock, 1), dead_pid(), tree="C:/crashed/wt-x")   # slot 1: a dead one
    h = F.acquire(lock, tree="T", timeout_s=30, poll_s=0.02, free_gb=lambda: 10.0, max_slots=2, reserve_gb=RESERVE)
    assert h.path == F.slot_path(lock, 1) and h.record["slot"] == 1
    out = capsys.readouterr().out
    assert "taking over a stale fast-tier lock" in out and "C:/crashed/wt-x" in out
    F.release(h.path, h)
    assert not F.slot_path(lock, 1).exists() and lock.exists()       # the live holder's slot is left alone


def test_a_slot_holder_older_than_two_hours_is_taken_over(lock):
    plant(lock, os.getpid())
    plant(F.slot_path(lock, 1), os.getpid(), age=timedelta(hours=2, minutes=1))
    h = F.acquire(lock, tree="T", timeout_s=30, poll_s=0.02, free_gb=lambda: 10.0, max_slots=2, reserve_gb=RESERVE)
    assert h.path == F.slot_path(lock, 1)
    F.release(h.path, h)


def test_every_slot_live_is_waited_for_and_the_cap_still_refuses(lock):
    plant(lock, os.getpid())
    plant(F.slot_path(lock, 1), os.getpid(), token="planted-2")
    with pytest.raises(F.WaitTimeout) as e:
        F.acquire(lock, tree="T", timeout_s=0.3, poll_s=0.02, free_gb=lambda: 10.0, max_slots=2, reserve_gb=RESERVE)
    assert "place 1 of 1" in str(e.value)
    assert list(F.queue_dir(lock).glob("*.ticket")) == []


def test_each_slot_has_its_own_record_heartbeat_and_release(lock):
    plant(lock, os.getpid())
    seen = {}

    def runner(cmd, env):
        rec = json.loads(F.slot_path(lock, 1).read_text(encoding="utf-8"))
        seen.update(rec)
        seen["token_env"] = env.get(F.ENV_TOKEN)
        return 0

    rc = F.run(["stub"], lock=lock, tree="second", min_free_gb=1.5, timeout_s=30, poll_s=0.02, free_gb=lambda: 10.0,
               runner=runner, max_slots=2, reserve_gb=RESERVE, env={})
    assert rc == 0
    assert seen["tree"] == "second" and seen["slot"] == 1 and seen["phase"] == "fast-tier"
    assert seen["token_env"] == seen["token"]
    assert not F.slot_path(lock, 1).exists() and json.loads(lock.read_text(encoding="utf-8"))["token"] == "planted"


def test_a_commit_nested_in_a_second_slot_run_reenters_without_waiting(lock):
    plant(lock, os.getpid())
    plant(F.slot_path(lock, 1), os.getpid(), token="outer")
    rc = F.run(["stub"], lock=lock, tree="nested", timeout_s=0.5, poll_s=0.02, free_gb=lambda: 10.0,
               runner=lambda c, e: 7, max_slots=2, reserve_gb=RESERVE, env={F.ENV_TOKEN: "outer"})
    assert rc == 7


# ------------------------------------------------------------------------------------------------ configuration

def _slots_in_child(value: str | None) -> int:
    env = {k: v for k, v in os.environ.items() if k != F.ENV_SLOTS}
    if value is not None:
        env[F.ENV_SLOTS] = value
    out = subprocess.run([sys.executable, "-c", "import fasttier_lock as F; print(F.MAX_SLOTS)"],
                         cwd=ROOT / "scripts", env=env, capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return int(out.stdout.strip())


@pytest.mark.parametrize("value,expected", [(None, 2), ("1", 1), ("3", 3), ("0", 1), ("two", 2), ("", 2)])
def test_the_slot_count_defaults_to_two_and_is_set_by_the_environment(value, expected):
    assert _slots_in_child(value) == expected


def test_the_reserve_is_declared_and_above_the_measured_peak():
    assert F.DEFAULT_SLOTS == 2
    assert F.SLOT_RESERVE_GB >= F.MEASURED_PEAK_GB > 0
    assert "tree_peak_memory.py" in F.__doc__ or "tree_peak_memory.py" in F.SLOT_RESERVE_SOURCE


# ------------------------------------------------------------------------------------------------ status

def test_status_shows_both_slots_and_the_line(lock, monkeypatch):
    plant(lock, os.getpid(), tree="C:/one/wt-a")
    plant(F.slot_path(lock, 1), os.getpid(), tree="C:/two/wt-b", token="t2")
    q = F.queue_dir(lock)
    q.mkdir()
    (q / F.ticket_name(time.time_ns(), os.getpid(), "w1")).write_text("", encoding="utf-8")
    env = {**os.environ, F.ENV_SLOTS: "2"}
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "fasttier_lock.py"), "--lock", str(lock), "status"],
                         capture_output=True, text=True, timeout=60, env=env).stdout
    assert "slot 1 of 2" in out and "C:/one/wt-a" in out
    assert "slot 2 of 2" in out and "C:/two/wt-b" in out
    assert "1. waiting since" in out
