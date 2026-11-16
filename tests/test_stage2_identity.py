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
def test_p14_and_p16_reproduced():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "stage2_identity.py"), "--paths", "4"],
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert r.stdout.count("identity HOLDS") == 2, r.stdout
