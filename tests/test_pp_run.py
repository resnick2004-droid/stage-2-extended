"""Q-105b: RD-02's reading runner (`scripts/pp_reading.py`, `extended/pp_run.py`, `extended/pp_run_synthetic.py`;
the pinned text's section 14) on synthetic inputs only -- no bar, no atlas, no result file of a design read:

* `e2e` -- the pipeline end to end into a temporary folder: the three result files with their manifests (RD-02,
  `exploratory=False`, the seeds from the pinned file, the adapter's commit and blob ids, the calendars, the limits),
  every identity row holding in 14 step 2's order, every section, the menu's labels and notes, the gates;
* `refusals` -- a planted failure writes nothing; the real mode refuses outside a clean run; a protected folder is
  refused; the waits' rows are checked;
* `labels` -- the paired readings' intervals, MDDs and labels from the honesty table, and the menu's count;
* `t3` -- T-3 on the runner's composed reading (Q-106's n6): the early block's rows byte-identical when 2024 on is
  replaced.

Each runs in its own process (`tests/pp_run_check.py`). The build's seed rule (T-9) holds for these files too: none
writes a seed of RD-02's block (the runner reads its seeds from the pinned file).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FILES = ("extended/pp_run.py", "extended/pp_run_synthetic.py", "scripts/pp_reading.py", "tests/pp_run_check.py",
         "tests/test_pp_run.py", "tests/pp_gate_direct.py")


@pytest.mark.parametrize("section", ["e2e", "refusals", "labels", "t3"])
def test_runner_section_holds(section, tmp_path):
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "pp_run_check.py"), str(ROOT), section, str(tmp_path)],
                       cwd=ROOT, capture_output=True, text=True, timeout=900, env=env)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, f"{section} did not run:\n{r.stdout[-2000:]}\n{r.stderr[-3000:]}"
    out = json.loads(lines[-1])
    assert out["n_problems"] == 0, "\n".join(out["problems"])


def test_the_runner_writes_no_seed_of_the_block():
    pat = re.compile(rb"\b2026194[0-9]\b")
    for rel in FILES:
        assert not pat.search((ROOT / rel).read_bytes()), f"{rel} writes a seed of RD-02's block"
