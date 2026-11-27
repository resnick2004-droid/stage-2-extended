"""Q-213's identity (heavy; the lead runs it under `run.lock`): `extended.design_trades` fed P-16's own registered
marks and `coin_table` sides reproduces P-16's registered search-year trades hash and count
(`identity/design_trades_identity.py`, in its own process: it imports the vendored engine and reads the search years'
bars inside `extended.search_cut`).

    python scripts/run_clean.py --name q213-identity --hours 1 --mem-gb 3 --task Q-213 -- python -m pytest -q -o addopts= -p no:cacheprovider -m heavy tests/test_design_trades_identity.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.heavy
def test_design_trades_reproduces_p16s_registered_search_year_trades():
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "design_trades_identity.py")], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=3600)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert lines, r.stderr[-3000:]
    out = json.loads(lines[-1])
    assert r.returncode == 0 and out["holds"] is True, out
    assert out["hash"] == out["hash_registered"] and out["trades"] == out["trades_registered"]
    assert out["same_frame_as_i5_builder"] is True
