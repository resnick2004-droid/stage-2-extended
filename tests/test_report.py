"""Q-27: the dispersion report (`extended/report.py`, `scripts/build_report.py`).

Each case runs in a process of its own (`tests/report_cases.py`; the report imports the vendored engine) and returns
the problems it found; the test asserts there are none.

* `measures` -- every journey measure equals an independent plain-Python reading (`tests/report_reference.py`) on three
  seeded synthetic files (seeds 20262701-3), every design, the base case and a ladder level; a file worked by hand
  gives the numbers worked by hand; a measure needing a column the file lacks says so instead of guessing.
* `build`, `build_monthly` -- a page built from a synthetic file (with and without the daily path, every payout's cash
  and the ladder): every chart a PNG with its source named under it, the "not modelled" section, the exploratory label
  exactly when the manifest says so, the ladder or "not in this file", no number on the page that is not registered,
  and the trace check passing on it with every number found -- and failing on a stale page and on an edited file.
* `refusals` -- a design with no rows, mixed ladder levels, an unknown column, a daily path or payouts disagreeing with
  the month-end nets, a missing column, an edited file: refused; an uncommitted tree's reading labelled NOT CITABLE.
* `stage2` -- the identity: the report's reading of Stage 2's U1 start rows reproduces U1's own registered readings in
  `vendor/stage2/results/user_journey.csv` (sections metric and month) for P-14 and P-16, both arms, values to 1e-9
  and counts exactly; a negative control (the other design's rows) differs.
* `no_matplotlib` -- without matplotlib the page is tables only and says why; `memo` -- one read a file a trace run.
* `scripts/build_report.py --list` names the registered page.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "report_cases.py"


def run_case(case: str, tmp_path: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if k != "S2X_CLEAN_RUN"}
    env["MPLBACKEND"] = "Agg"
    r = subprocess.run([sys.executable, str(CASES), case, str(tmp_path)], cwd=ROOT, capture_output=True, text=True,
                       timeout=600, env=env)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("case", ["measures", "build", "build_monthly", "refusals", "stage2", "no_matplotlib", "memo"])
def test_report_case(case, tmp_path):
    out = run_case(case, tmp_path)
    assert out["problems"] == [], json.dumps(out, indent=1)[:6000]
    if case == "measures":
        assert out["compared"] > 2000
    if case == "stage2":
        # P-14 and P-16, both arms: 73 of U1's registered readings and the 10 scorecard lines on the judged block
        assert out["held"] == out["compared"] == 4 * (73 + 10)


def test_build_report_lists_the_registered_page():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_report.py"), "--list"], cwd=ROOT,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "demo_stage2_u1" in r.stdout
