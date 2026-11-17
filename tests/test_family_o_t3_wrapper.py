"""F-03 (family O) V1 of the second build read: T-3 replaces the judged block below every loader and cannot pass
vacuously -- a planted judged read is caught (`tests/fo_t3_wrapper.py`, a process of its own, a synthetic store)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_t3s_replacement_catches_a_planted_judged_read_and_refuses_unwired(tmp_path):
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "fo_t3_wrapper.py"), str(ROOT), str(tmp_path)],
                       capture_output=True, text=True, timeout=600, env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    c = got["choice"]
    assert c["entered"] >= 1 and c["replaced"] == 0 and c["verdict"] == [] and c["rows"] > 0
    p = got["planted"]
    assert p["replaced"] > 0 and p["prices_moved"] and any("judged-block rows" in v for v in p["verdict"])
    assert got["restored"]
    assert any("never entered" in v for v in got["idle_verdict"])
