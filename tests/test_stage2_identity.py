"""E-002: the vendored engine reproduces P-14's and P-16's registered per-path rows (identity/stage2_identity.py).

Run in a subprocess: the identity puts the vendored tree on sys.path. Four paths here; the full 500-path identity is
recorded in the decision log from a clean checkout.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_p14_and_p16_reproduced():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "stage2_identity.py"), "--paths", "4"],
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert r.stdout.count("identity HOLDS") == 2, r.stdout


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_u1_start_rows_reproduced():
    """Q-05: U1's start rows (`results/user_journey.csv`, section `start`, every column) for P-14 and P-16, both arms,
    at 4 starts spread as `user_journey.py --check --starts 4` spreads them, by the vendored replay."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "stage2_identity.py"), "--only", "u1", "--u1-starts",
                        "4"], capture_output=True, text=True, timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: U1") == 2, r.stdout


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_u1_p15_start_rows_reproduced():
    """Q-22: U1's start rows for P-15 (Stage 2's 25-point coin, `rc_s100_all`), both arms, every column, at 4 starts
    spread as `user_journey.py --check --starts 4` spreads them -- the same comparison as P-14's and P-16's, with
    P-15's trades identity (`rc_dev_test.trade_problems`: its screen row and registered content hash) refusing."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "stage2_identity.py"), "--only", "u1", "--u1-configs",
                        "p15", "--u1-starts", "4"], capture_output=True, text=True, timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: U1") == 1, r.stdout
    assert "identity HOLDS: U1 P15" in r.stdout, r.stdout
    assert "REFUSED" not in r.stdout, r.stdout
