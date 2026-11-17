"""RD-01's identity stage (`identity/firms_identity.py`, 9.1): written for the lead to run under the run lock. The fast
tier holds its plan and its refusal of a run without its decision row (nothing read); T-8 (`slow`) runs items 1 to 3 at
4 starts and 4 paths once the identity's decision row exists (`RD01_IDENTITY_ROW`), under the run lock."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "identity" / "firms_identity.py"


def _run(*args: str, timeout: int = 600) -> subprocess.CompletedProcess:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout,
                          env=env, cwd=str(ROOT))


def test_the_identity_plan_names_9_1s_five_items_and_reads_nothing():
    p = _run("--plan")
    assert p.returncode == 0, p.stderr[-2000:]
    lines = [x for x in p.stdout.splitlines() if x.startswith(("run ", "skip "))]
    assert [x.split(":")[0].split()[-1] for x in lines] == ["1", "2", "3", "4", "5"]
    assert all(x.startswith("run ") for x in lines)
    p = _run("--plan", "--only", "1,2")
    assert [x[:4] for x in p.stdout.splitlines() if x.startswith(("run ", "skip "))] == ["run ", "run ", "skip",
                                                                                        "skip", "skip"]


def test_the_identity_refuses_to_run_without_its_decision_row():
    p = _run("--starts", "4")
    assert p.returncode == 2 and "--row E-NNN" in p.stderr


@pytest.mark.slow
def test_t8_items_1_to_3_at_4_starts_and_4_paths():
    row = os.environ.get("RD01_IDENTITY_ROW")
    if not row:
        pytest.skip("the identity's decision row is the lead's (RD01_IDENTITY_ROW); run under the run lock")
    p = _run("--row", row, "--starts", "4", "--paths", "4", "--only", "1,2,3", timeout=7200)
    assert p.returncode == 0, p.stdout[-4000:] + p.stderr[-2000:]
    assert p.stdout.count("identity HOLDS") >= 6
