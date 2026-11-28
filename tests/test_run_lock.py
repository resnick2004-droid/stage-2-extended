"""E-006: the heavy-run lock is taken atomically, refuses a second taker and a short machine, and is never stolen."""
from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import run_lock as L  # noqa: E402


@pytest.fixture()
def lock(tmp_path, monkeypatch):
    p = tmp_path / "run.lock"
    monkeypatch.setattr(L, "LOCK", p)
    monkeypatch.setattr(L, "available_gb", lambda: 8.0)
    return p


def take(job="j1", mem=3.0, hours=1.0):
    return L.main(["take", "--job", job, "--task", "Q-00", "--holder", "test", "--hours", str(hours),
                   "--mem-gb", str(mem)])


def test_take_then_refuse_then_release(lock):
    assert take() == 0 and lock.is_file()
    assert take("j2") == 3                                  # held: a second taker is refused
    assert L.main(["release", "--job", "j2"]) == 3          # only the holder releases
    assert L.main(["release", "--job", "j1"]) == 0 and not lock.exists()


def test_short_memory_refuses(lock, monkeypatch):
    monkeypatch.setattr(L, "available_gb", lambda: 1.5)
    assert take(mem=3.0) == 4 and not lock.exists()


def test_stale_is_reported_not_stolen(lock):
    assert take(hours=0.0) == 0
    held = json.loads(lock.read_text())
    held["expected_end"] = (L.now() - L.STALE_AFTER - timedelta(minutes=1)).isoformat()
    lock.write_text(json.dumps(held))
    assert L.is_stale(L.read())
    assert take("j2") == 3                                   # stale or not, a held lock is never taken
    assert lock.is_file()


def test_set_pid_only_for_the_holder(lock):
    assert take() == 0
    assert L.main(["set-pid", "--job", "other", "--pid", "1"]) == 3
    assert L.main(["set-pid", "--job", "j1", "--pid", "42", "--log", "x.log"]) == 0
    assert json.loads(lock.read_text())["pid"] == 42


# Q-229: the lock on macOS -------------------------------------------------------------------------------------------

VM_STAT = """Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                               65536.
Pages active:                            400000.
Pages inactive:                          131072.
Pages speculative:                        65536.
Pages throttled:                              0.
Pages wired down:                        200000.
"""


def test_darwin_memory_read_from_vm_stat():
    # (65536 + 131072 + 65536) pages x 16 KiB = 4 GiB; active and wired pages are not available
    assert L._darwin_available_gb(VM_STAT) == pytest.approx(4.0)


def test_darwin_memory_unreadable_is_none():
    assert L._darwin_available_gb("no page size here") is None
    assert L._darwin_available_gb(VM_STAT.replace("Pages inactive", "Pages gone")) is None


def test_darwin_dispatch(monkeypatch):
    monkeypatch.setattr(L.sys, "platform", "darwin")
    monkeypatch.setattr(L.os, "name", "posix")
    monkeypatch.setattr(L, "_darwin_available_gb", lambda vm_stat=None: 5.5)
    assert L.available_gb() == 5.5


def test_unknown_memory_refuses(lock, monkeypatch):
    monkeypatch.setattr(L, "available_gb", lambda: None)
    assert take(mem=1.0) == 4 and not lock.exists()     # a heavy run never starts with its memory unchecked
