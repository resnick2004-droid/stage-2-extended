"""Q-20: the trades re-walked with the breakeven move corrected (`extended/breakeven.py`), by its identities
(`identity/breakeven_identity.py`), each in its own process.

* light (`--synthetic`): under `STAGE2` the re-walk is Stage 2's `atlas_a3.walk_minutes` frame at delay 0 (P-16's
  marks) and five bars late (A3's rungs); the stop-first tie only turns a target into a breakeven on the same bar; every
  correction changes some walk and none changes a walk Stage 2 ended before the move could act.
* slow (`--substitution`, `--smoke-days 10`): P-14 through the substitution on Stage 2's cached A3 frame gives Stage 2's
  trades exactly and a changed frame changes them, the substitution undone after (also after an error); on the first
  10 development days of real bars the re-walk under `STAGE2` equals Stage 2's walk and the cache.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "breakeven_identity.py"


def run(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout)


def test_the_rewalk_on_synthetic_days():
    r = run("--synthetic")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "synthetic identity HOLDS" in r.stdout, r.stdout


@pytest.mark.slow
def test_p14s_substitution_reaches_its_trades_and_only_inside_the_block():
    if not (DATA / "atlas").is_dir():
        pytest.skip("the atlas is not copied (scripts/vendor_stage2.py --data)")
    r = run("--substitution")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "substitution check HOLDS" in r.stdout, r.stdout


@pytest.mark.slow
def test_the_rewalk_is_stage2s_on_the_first_real_days():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--smoke-days", "10")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "smoke identity HOLDS" in r.stdout, r.stdout
