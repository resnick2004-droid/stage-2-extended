"""RD-01's reading runner (`scripts/rd01_reading.py`, `extended/firm_reading.py`): end to end on toy campaigns into a
temporary results folder (`tests/rd01_reading_synthetic.py`, in a process of its own; seed 20261992), and the runner's
refusals before any read -- without the identity stage's row, with a row that is not it. No bar, no atlas."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


@lru_cache(maxsize=1)
def found() -> dict:
    p = subprocess.run([sys.executable, str(ROOT / "tests" / "rd01_reading_synthetic.py"), str(ROOT)],
                       capture_output=True, text=True, timeout=900, env=ENV)
    if p.returncode != 0:
        raise AssertionError(f"the toy reading failed:\n{p.stderr[-4000:]}")
    return json.loads(p.stdout.strip().splitlines()[-1])


def test_the_scorecard_end_to_end():
    r = found()
    assert r["sc_problems"] == []           # the direct runs equal A-9's on every start; A-10 at the price run's end
    assert r["sc_runs"] == ["DT-16-price", "DT-16-s", "FP-16-s", "LU-16-l", "QP-16-req", "QP-16-s", "TS-14", "TS-16"]
    assert r["sc_sections"] == ["break_even", "counts", "extra", "identity_items_4_5", "paired", "paired_card", "path",
                                "price_grid", "response", "scorecard"]
    assert r["sc_items_4_5"]["trades"] > 0 and r["sc_items_4_5"]["accounts"] > 0     # m4: on every replay
    assert r["sc_paired_blocks"] == ["all", "early", "late"] and r["sc_paired_months"] == [1, 2, 3, 6, 9, 12]
    assert r["sc_grid_prices"] == [float(p) for p in range(25, 251, 25)]
    assert r["sc_grid_P_falls_with_price"] is True
    assert r["sc_break_even"] == ["P", "S5a", "mean_net_month_3"]
    fp = r["sc_fp_counts"]
    assert fp["trades"] > 0 and fp["fee_off_schedule"] == 0 and fp["funded.forced_untraded"] > 0
    assert fp["contracts_compared"] > 0
    assert r["sc_dt_counts"]["martingale_per_account"] >= 0 and r["sc_dt_counts"]["funded.q"] >= 0


def test_the_ladder_and_the_gate_end_to_end():
    r = found()
    assert r["ld_problems"] == [] and r["ld_responses"] == ["denial_10", "denial_25", "denial_50"]
    assert r["ld_runs"] == ["DT-16-l", "DT-16-s", "FP-16-l", "FP-16-s", "LU-16-l", "LU-16-s", "QP-16-l", "QP-16-s",
                            "TS-16"]
    assert r["gt_problems"] == [] and r["gt_runs"] == 16
    assert r["gt_readings_qp"] == ["plan", "zero_edge"]      # M3: one call reads both arms on the point outcomes
    assert r["gt_readings_dt"] == ["plan", "zero_edge"]
    assert r["gt_labels_fp"] == ["tier-1 liquidation not applied"]


def test_the_files_carry_their_manifests():
    r = found()
    assert r["files"] == sorted(f"{n}{x}" for n in ("rd01_gate", "rd01_gate_paths", "rd01_ladder", "rd01_scorecard",
                                                     "rd01_scorecard_starts") for x in (".csv", ".csv.manifest.json"))
    assert r["manifest_keys"] == ["git_commit", "parameters", "prereg_id", "provenance", "script", "seed", "sha256"]
    assert r["manifest_prereg"] == "RD-01" and r["read_back_rows"] > 0
    assert r["manifest_blobs"][0] >= 15 and r["manifest_blobs"][1] is True


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "rd01_reading.py"), *args], capture_output=True,
                          text=True, timeout=300, env=ENV, cwd=str(ROOT))


def test_the_runner_refuses_without_the_identity_stage_before_any_read():
    p = _cli("--purpose", "firm_scorecard")
    assert p.returncode == 3 and "REFUSED (RD-01 9.1)" in p.stdout and "identity stage" in p.stdout
    p = _cli("--purpose", "firm_gate_beside", "--identity-row", "E-080")     # RD-01's pin row: not the identity's
    assert p.returncode == 3 and "does not name identity/firms_identity.py" in p.stdout
    p = _cli("--purpose", "no_such_purpose")
    assert p.returncode == 2
