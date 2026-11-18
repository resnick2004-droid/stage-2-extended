"""RD-05's T-11 (`prereg/RD-05_firm_modes.md` 17.3; 13.1): the identities at small sizes -- the coin identity at 200
accounts a cell in its own process (items (a) and (b) must hold; (c) and (d) report NOT BUILT, exit 3), and the replay
identity at 4 starts and 4 paths (NOT BUILT at this commit: it refuses and reads nothing). Marked `slow` and `heavy`
(E-198's marker; the red team's N7): the replay identity reads the bars once built, and the run lock's guard skips this
file while another job holds `run.lock`.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

pytestmark = [pytest.mark.slow, pytest.mark.heavy]


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, timeout=1800)


def test_t11_coin_identity_at_200_accounts() -> None:
    r = _run("identity/modes_coin_identity.py", "--accounts", "200")
    out = r.stdout
    assert "(a) held" in out and "(b) held" in out, out + r.stderr
    assert "FAILED" not in out
    assert "(c) NOT BUILT" in out and "(d) NOT BUILT" in out
    assert r.returncode == 3                       # cannot hold until (c) and (d) are built


def test_t11_replay_identity_not_built() -> None:
    r = _run("identity/modes_identity.py")
    assert r.returncode == 3 and "NOT BUILT" in r.stdout
