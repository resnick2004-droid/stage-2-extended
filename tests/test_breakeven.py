"""Q-20: the trades re-walked with the breakeven move corrected (`extended/breakeven.py`), by its identities
(`identity/breakeven_identity.py`), each in its own process.

* light (`--synthetic`): under `STAGE2` the re-walk is Stage 2's `atlas_a3.walk_minutes` frame at delay 0 (P-16's
  marks) and five bars late (A3's rungs); the stop-first tie only turns a target into a breakeven on the same bar; every
  correction changes some walk and none changes a walk Stage 2 ended before the move could act. On E-011's 40 synthetic
  days (80 with the widened copies) it is slow-tier since Q-96 (48-56 s); the fast tier runs the same
  `synthetic_problems`, every check, on 4 of them (8 with the copies).
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


@pytest.mark.slow          # Q-96: 48-56 s; the fast tier keeps the smoke below (the same check on 4 synthetic days)
def test_the_rewalk_on_synthetic_days():
    r = run("--synthetic")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "synthetic identity HOLDS" in r.stdout, r.stdout


#: the smoke's child: the identity's own `synthetic_problems` on the first 4 of E-011's synthetic days
SYNTHETIC_SMOKE = """
import sys
sys.path.insert(0, {identity!r})
import breakeven_identity as BI
BI.WI.SYNTH_DAYS = 4
bad = BI.synthetic_problems()
print("PROBLEMS", len(bad))
for b in bad:
    print(b)
"""


def test_the_rewalk_on_synthetic_days_smoke():
    """Q-96: the fast tier's cover for the case above (slow): the identity's `synthetic_problems` -- the re-walk under
    `STAGE2` equal to `atlas_a3.walk_minutes`' frame at both delays, every stop-first change a target turned into a
    breakeven on the same bar, no walk changed that Stage 2 ended before the move could act, and every rule set changing
    some walk (not vacuous) -- on 4 of E-011's synthetic days, 8 with the widened copies."""
    r = subprocess.run([sys.executable, "-c", SYNTHETIC_SMOKE.format(identity=str(ROOT / "identity"))],
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "PROBLEMS 0" in r.stdout, r.stdout[-3000:]
    assert "synthetic identity HOLDS: 8 synthetic days" in r.stdout, r.stdout[-3000:]


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
