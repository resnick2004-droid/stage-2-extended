"""F-03 (family O) W1 of the third build read: a scorecard-stage failure never discards stage C's verdict, and the
choice-block beside's refusing checks run before any judged purpose is authorised (`tests/fo_run2_w1.py`, a process of
its own, synthetic inputs; slow, about five minutes)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.slow
def test_w1_the_verdict_is_written_before_the_scorecard_and_its_checks_come_first(tmp_path):
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "fo_run2_w1.py"), str(ROOT), str(tmp_path)],
                       capture_output=True, text=True, timeout=1800, env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["run1_code"] == 0
    assert got["precheck"]["code"] == 3 and got["precheck"]["authorised"] == []     # refused before any judged read
    assert got["raised"] and got["judged_written"] and got["judged_path"]
    assert got["authorised"] == ["stage_C_states", "stage_C_judgement", "stage_C_campaign"]   # scorecard never ledgered
    assert got["judged_sections"] == ["beside", "campaign", "floor", "judged", "level"] and got["verdict_row"] == 1
    assert not got["journey_written"]
