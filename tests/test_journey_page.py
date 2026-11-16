"""Q-69: the journey scorecard page for Q-44's readings (`extended/journey_page.py`, registered in
`extended/report.py` as `journey_scorecard`, built by `scripts/build_report.py --report journey_scorecard`).

Each case runs in a process of its own (`tests/journey_cases.py`; the page imports the vendored engine) on a synthetic
pair of files made by the writer's own code (`tests/journey_synth.py`) in a temporary folder -- never the real result
file, which does not exist yet -- and returns the problems it found; the test asserts there are none.

* `page` (fast tier; the responses of every kind) -- the page builds; every section and every design's sub-section is
  there in order; the verdict view first, the rest labelled beside; E-015's limits pending with no level; both charts
  with their sources; no number on the page that is not registered; the trace check passes on every number (and
  fails on a stale page and an edited file); the waiting state; the refusals; an approved limit read from a result
  file; the registered page is the writer's (its file names, designs and script).
* `full` (slow tier) -- the same on all 19 of the writer's responses.
* `u1` (slow tier) -- the build-time identity against Stage 2's U1 start rows holds on the writer's own scorecard of
  them and refuses the synthetic file.
* `scripts/build_report.py --list` names the page and says it waits for Q-44's file while it does not exist.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "journey_cases.py"


def run_case(case: str, tmp_path: Path, timeout: int = 900) -> dict:
    env = {k: v for k, v in os.environ.items() if k != "S2X_CLEAN_RUN"}
    env["MPLBACKEND"] = "Agg"
    r = subprocess.run([sys.executable, str(CASES), case, str(tmp_path)], cwd=ROOT, capture_output=True, text=True,
                       timeout=timeout, env=env)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_page_on_a_synthetic_readings_file(tmp_path):
    out = run_case("page", tmp_path)
    assert out["problems"] == [], json.dumps(out, indent=1)[:8000]
    assert out["journey_synth_claims"] > 400
    assert sorted(out["journey_synth_charts"]) == ["net_months.png", "responses.png"]


@pytest.mark.slow
def test_the_page_on_every_response(tmp_path):
    out = run_case("full", tmp_path, timeout=1800)
    assert out["problems"] == [], json.dumps(out, indent=1)[:8000]


@pytest.mark.slow
def test_the_verdict_view_is_held_to_stage2(tmp_path):
    out = run_case("u1", tmp_path, timeout=1800)
    assert out["problems"] == [], json.dumps(out, indent=1)[:8000]
    assert out["u1_positive"][1] == 0 and out["u1_negative"][1] > 0


def test_build_report_lists_the_page_as_waiting():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_report.py"), "--list"], cwd=ROOT,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    line = [ln for ln in r.stdout.splitlines() if ln.startswith("journey_scorecard: ")]
    assert line, r.stdout
    if not (ROOT / "results" / "user_beside.csv").exists():
        assert "waiting" in line[0] and "Q-44" in line[0], line[0]
