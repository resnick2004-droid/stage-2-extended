"""Q-47 (E-025 (2)): the gate re-composed in `extended/gate.py` so a design can declare another funded-account class,
and Q-71 (the firms draft's A-8): its three more seams -- `payout_lag_days`, `household_closure`, `combine_account_cls`
-- and the campaign re-composed in `extended/campaign.py` to pass the last to its paths. Held to the vendored engine by
the identities (`identity/gate_identity.py`), each run in its own process (the vendored tree goes on its `sys.path`).

* fast (`--synthetic`): on synthetic trade blocks through the vendored engine --
  - the vendored `run_gate` source is the one the adapter was composed from, and a wrong pin is refused;
  - with no class, and with a pass-through subclass, the adapter's rows and every path's record equal the vendored
    gate's exactly;
  - a probe subclass reaches the engine in this process and in path workers;
  - a class that is not a funded account, or that cannot reach a worker, is refused;
  - Q-71: the vendored campaign's source is pinned and a wrong pin refused; the re-composed campaign and gate are the
    vendored functions statement for statement once their marked lines are removed (and the check is not vacuous);
    the re-composed campaign equals the vendored one with nothing given and with a pass-through evaluation class; the
    gate with every seam at Topstep's values equals the vendored gate (rows apart from the named columns, every path's
    record); a longer lag moves every first arrival by exactly the extra sessions and leaves every request; the
    household rule closes at the first trigger only when on, and is refused with Topstep's funded class; an evaluation
    probe that never passes reaches the engine and path workers; bad seam arguments are refused.
* slow (`--paths 4 --cls all`, which the run-lock skill counts as heavy): with no seam, with the pass-through funded
  class and with every seam at Topstep's values, the adapter reproduces P-14's and P-16's registered gate paths
  (`a3_brk30_cb20_gate_paths.csv`, `rc_s150_all_gate_paths.csv`) on their first 4 paths, both shifts, every
  `PATH_COLS` column to 1e-6. All 500 paths are the lead's heavy run (`--paths 500 --workers 1 --cls all`, from a
  clean checkout under the lock).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "gate_identity.py"

Q47_CHECKS = ("source pinned", "wrong pin refused", "no class: rows and paths equal",
              "pass-through class: rows and paths equal", "probe reaches the engine",
              "probe reaches path workers", "non-account class refused", "unpicklable class refused")
Q71_CHECKS = ("campaign source pinned", "wrong campaign pin refused",
              "re-composed: the vendored bodies plus marked lines",
              "campaign, nothing given: equals the vendored campaign",
              "campaign, pass-through evaluation class: equal, named in the provenance",
              "seams at Topstep's values: rows and paths equal", "lag reaches the engine",
              "household rule reaches the engine", "evaluation probe reaches the engine",
              "evaluation probe reaches path workers", "bad seam arguments refused")


def run(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout)


def test_the_adapter_equals_the_vendored_gate_on_synthetic_blocks():
    r = run("--synthetic")
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-4000:]
    assert "synthetic identity HOLDS" in r.stdout, out[-4000:]
    for check in Q47_CHECKS + Q71_CHECKS:
        assert f"holds: {check}" in r.stdout, f"{check!r} not reported as holding:\n{out[-4000:]}"


def test_the_arms_parse_and_an_unknown_arm_is_refused():
    r = run("--paths", "1", "--cls", "everything", timeout=120)
    assert r.returncode != 0 and "invalid choice" in r.stderr, (r.stdout + r.stderr)[-2000:]


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_the_adapter_reproduces_p14_and_p16_registered_gate_paths_at_four_paths():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--paths", "4", "--cls", "all", timeout=3600)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-4000:]
    for design in ("P-14", "P-16"):
        for arm in ("none", "passthrough", "seams"):
            assert f"identity HOLDS: {design} gate through extended.gate ({arm})" in r.stdout, out[-4000:]
