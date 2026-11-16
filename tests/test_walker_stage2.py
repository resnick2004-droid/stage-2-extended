"""Q-10 (F-01 section 7 item 1): the walker against Stage 2's own walk (identity/walker_identity.py).

Run in a subprocess: the identity puts the vendored tree on sys.path.

* `--synthetic` (light, no bars): on random synthetic days -- missing bars, gaps between bars, early last bars, missing
  session-open and flatten bars, every five-minute mark both sides -- this repository's walker under `STAGE2`
  reproduces Stage 2's `fv3_rung_walk.day_walks` entry for entry and walk for walk (kind, exit, MAE, gross at 50, 100,
  150 and 200 ticks and every quarter R to 3R), `atlas_a3.walk_minutes`' frame column for column, Stage 2's clock and
  constants, and `resolved_coin.cell_trades`' net R and cost columns bit for bit from this repository's costs.
* `--smoke-days 10` (slow; the first ten development days of real bars, P-16's own entries): the same frame equality
  against Stage 2's walk on the bars P-16 is built from. Nothing printed but the comparison.

The full identity -- P-16's cell rebuilt by `rc150_dev_test.build_cells` with this walker in Stage 2's walk's place, its
content hash against the pinned `TRADES_SHA256` -- reads every development bar; it runs under the run lock and is
recorded in the build's decision row, not in the suite.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "walker_identity.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=900)


def test_the_walker_is_stage2s_walk_on_synthetic_days():
    r = run("--synthetic")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "synthetic identity HOLDS" in r.stdout, r.stdout


def test_the_substitution_touches_p16s_walk_only():
    """Corrective cycle 1 (the lead's run of 2026-11-16 refused at A3's cache): the full identity's one substitution
    must leave `atlas_a3.walk_inputs`' key for A3's cache -- read while P-14's inputs load -- Stage 2's, be in force only
    while `rc_width_screen.build` walks P-16's marks, and be undone after (also on an error). No bars are read; when the
    atlas is present its A3 manifest's key is checked too."""
    r = run("--substitution")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "substitution check HOLDS" in r.stdout, r.stdout


@pytest.mark.slow
def test_the_walker_is_stage2s_walk_on_p16s_first_days():
    if not (DATA / "bars").is_dir():
        pytest.skip("bars not copied (scripts/vendor_stage2.py --data)")
    r = run("--smoke-days", "10")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "smoke identity HOLDS" in r.stdout, r.stdout
