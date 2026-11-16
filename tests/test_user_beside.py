"""Q-17: the user's replay under the firm's responses (`extended/user_beside.py`), by its identities
(`identity/user_beside_identity.py`), each in its own process (the vendored tree goes on its `sys.path`).

* light (`--synthetic`): on synthetic binary-draw campaigns -- the path seed feeds only the enforcement stream; the
  seed decides the denials; all-accounts forfeiture closes everything at the denial's close, buys nothing after it,
  takes out every later arrival and passes U1's own payout and fee checks, and is the off arm where nothing is denied;
  the placement and a Focused Trader model reach the engine; the adapter refuses a non-vendored call and a flip stream;
  the binding models are the vendored grid's; the start seeds are distinct.
* slow (`--u1-starts 4`): with every response off, the adapter reproduces `results/user_journey.csv`'s start rows for
  P-14 and P-16 at 4 starts, both arms, every column (E-010's comparison).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "user_beside_identity.py"


def run(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout)


def test_the_adapters_mechanics_on_synthetic_campaigns():
    r = run("--synthetic")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "synthetic identity HOLDS" in r.stdout, r.stdout


@pytest.mark.slow
def test_every_response_off_reproduces_u1s_start_rows():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "4", timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: Q-17 U1") == 2, r.stdout


@pytest.mark.slow
def test_the_comparison_refuses_a_response_switched_on():
    """The negative control: the same comparison with the placement on (P-14, 4 starts) must be refused."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "4", "--configs", "p14", "--control", "rtp", timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "negative control HOLDS" in r.stdout, r.stdout
