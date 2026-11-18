"""F-03 (family O, `prereg/F-03_opening_timing.md`) T-5's gate half in index mode with a real state (the build read's m3:
owed before floor (iii) and run 2): the waiting class with the state a placebo set, through `extended.gate.run_gate`,
read through Q-70's place recorder (`extended/place_records.py`, by `opening_wait.GateRecorder`). The engine's part runs
in a process of its own (`tests/fo_gate_placebo_synthetic.py`, synthetic inputs only); this file asserts what it
reports.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tests" / "fo_gate_placebo_synthetic.py"
W = 5


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(SCRIPT), str(ROOT)], capture_output=True, text=True, timeout=900, env=env,
                       cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_placebo_set_is_a_third_of_the_gates_trades(got):
    assert got["trades"] > 100 and 0.25 < got["in_set"] / got["trades"] < 0.42


def test_recording_the_placebo_gate_changes_none_of_its_rows(got):
    assert got["recorded_rows_same"]
    assert sorted(k[0] for k in got["recorded"]) == ["lower_bound", "point"]


def test_on_both_arms_every_in_wait_opening_is_in_the_set_and_every_decline_out_of_it(got):
    for shift, a in got["arms"].items():
        assert a["problems"] == [], (shift, a["problems"])
        assert a["in_wait"] > 0 and a["declined"] > 0, (shift, a)          # the identity bites on both arms
        assert set(a["wait_sessions"]) <= set(range(W))
        assert a["openings"] == a["in_wait"] + a["fallback"]


def test_the_gate_bites_and_the_state_always_on_is_the_gate_without_a_class(got):
    assert got["differs_from_no_class"]
    assert got["always_rows_same"] and got["always_declined"] == 0 and got["always_problems"] == []


def test_the_worker_route_records_the_same_declines(got):
    assert got["worker_tasks"] > 0                                         # the chunked route ran
    assert got["worker_rows_same"] and got["worker_declined_same"] and got["worker_accounts_same"]


def test_the_check_sees_a_misaligned_lookup(got):
    assert got["misaligned_caught"]


def test_a_spec_that_does_not_fit_the_gates_blocks_is_refused(got):
    assert got["misfit_refused"]


def test_w2_floor_iiis_check_holds_the_gate_to_the_state_by_offer_id_and_refuses_a_planted_mismatch(got):
    assert got["w2_problems"] == {"point": [], "lower_bound": []}
    assert all(c["in_wait"] > 0 and c["declined"] > 0 for c in got["w2_counts"].values())
    assert got["w2_planted_caught"] and got["w2_no_ids_refused"]
