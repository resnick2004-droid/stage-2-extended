"""Q-47 (E-025 (2)): the gate re-composed in `extended/gate.py` so a design can declare another funded-account class,
held to the vendored gate by its identities (`identity/gate_identity.py`), each run in its own process (the vendored
tree goes on its `sys.path`).

* fast (`--synthetic`): on synthetic trade blocks through the vendored engine --
  - the vendored `run_gate` source is the one the adapter was composed from, and a wrong pin is refused;
  - with no class, and with a pass-through subclass, the adapter's rows and every path's record equal the vendored
    gate's exactly;
  - a probe subclass reaches the engine in this process and in path workers;
  - a class that is not a funded account, or that cannot reach a worker, is refused.
* slow (`--paths 4`, which the run-lock skill counts as heavy): with no class and with the pass-through subclass, the
  adapter reproduces P-14's and P-16's registered gate paths (`a3_brk30_cb20_gate_paths.csv`,
  `rc_s150_all_gate_paths.csv`) on their first 4 paths, both shifts, every `PATH_COLS` column to 1e-6.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "gate_identity.py"


def run(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout)


def test_the_adapter_equals_the_vendored_gate_on_synthetic_blocks():
    r = run("--synthetic")
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-4000:]
    assert "synthetic identity HOLDS" in r.stdout, out[-4000:]
    for check in ("source pinned", "wrong pin refused", "no class: rows and paths equal",
                  "pass-through class: rows and paths equal", "probe reaches the engine",
                  "probe reaches path workers", "non-account class refused", "unpicklable class refused"):
        assert f"holds: {check}" in r.stdout, f"{check!r} not reported as holding:\n{out[-4000:]}"


@pytest.mark.slow
def test_the_adapter_reproduces_p14_and_p16_registered_gate_paths_at_four_paths():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--paths", "4", timeout=2400)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-4000:]
    for design in ("P-14", "P-16"):
        for cls in ("none", "passthrough"):
            assert f"identity HOLDS: {design} gate through extended.gate ({cls})" in r.stdout, out[-4000:]
