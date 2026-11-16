"""Q-105: RD-02's identity script `identity/pp_identity.py` (13.3's T-11 fast, T-8 slow).

* **T-11** -- it runs the reference policy only: its lever flags and payout fields are constants equal to `ref`'s; its
  argument parser has no option naming a policy, a lever or a payout field; with any lever flag flipped its guard
  refuses before the first start and the first path (the script's input builders replaced by tripwires; a positive
  control shows the reference reaches them); and D2 (Q-105e): every input built through the reading's `RealInputs` --
  the gate and its zero-edge twin by `gate_call(design, "ref", twin)`, compared with the registered `gate` and
  `zero_edge_twin` runs, U1's rows by `jobs` and `identity_problems`, item 6 at `ref` by `ladder_problems` under each
  response beside -- shown with stand-ins (nothing runs). Run in a process of its own (`tests/pp_identity_check.py`).
* **T-8** (`slow`; the lead's, under the run lock, never in the fast tier) -- 8.1 items 1 to 3 at 4 paths and 4 starts
  per configuration and arm, through the script, under the identity's decision row given in `PP_IDENTITY_ROW`; skipped
  until that row exists.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _env() -> dict:
    return dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                PYTHONDONTWRITEBYTECODE="1")


def test_t11_the_identity_script_runs_the_reference_policy_only():
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "pp_identity_check.py"), str(ROOT)], cwd=ROOT,
                       capture_output=True, text=True, timeout=300, env=_env())
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, f"the check did not run:\n{r.stdout[-2000:]}\n{r.stderr[-3000:]}"
    out = json.loads(lines[-1])
    assert not out["problems"], "\n".join(out["problems"])


@pytest.mark.slow
def test_t8_the_reference_policy_reproduces_the_registered_rows_at_4_paths_and_4_starts():
    row = os.environ.get("PP_IDENTITY_ROW")
    if not row:
        pytest.skip("T-8 runs under the identity's own decision row (PP_IDENTITY_ROW), the lead's, under the lock")
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "pp_identity.py"), "--paths", "4", "--u1-starts", "4",
                        "--row", row], cwd=ROOT, capture_output=True, text=True, timeout=7200, env=_env())
    assert "EXIT 0" in r.stdout, r.stdout[-4000:] + r.stderr[-2000:]
