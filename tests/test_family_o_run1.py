"""F-03 (family O, `prereg/F-03_opening_timing.md`) run 1 end to end on synthetic inputs: `scripts/fo_opening.py`'s
stages A and B with its reads replaced by seams (`tests/fo_run1_synthetic.py`, in a process of its own: the vendored
engine's router, lockstep loop and U1 replay through Q-17's adapter). A smoke's sizes: nothing is written; the frame and
its parameters are checked here. What it cannot show: anything about the real bars, P-16's registered files or the
U1 file (A0 and run 1 itself, under the lock).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from extended import opening_run as R

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "fo_run1_synthetic.py"), str(ROOT)], capture_output=True,
                       text=True, timeout=900, env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_run1_runs_every_stage_and_writes_only_its_sections(got):
    assert got["code"] == 0
    assert set(got["sections"]) <= set(R.RUN1_SECTIONS)
    assert {"identity", "states", "persistence", "supply", "openings", "resolution", "wait", "power", "level_control",
            "choice"} <= set(got["sections"])
    assert got["written"] is None                                   # a smoke writes nothing


def test_run1s_identities_hold_and_every_cell_reaches_stage_b(got):
    assert len(got["identity_holds"]) == 4 and all(got["identity_holds"])     # A3's three checks and A1
    assert got["killed"] == {}
    assert got["choice_cells"] == ["s1", "s2", "u3"] and got["choice_finite"]
    assert got["k0_rows"] == 6 and got["a10_rows"] == 24          # K0 two forms a cell; A10 6 classes x 2 shares x 2
    assert got["forecast_rows"] == 3 and got["forecast_sha_ok"]
    assert got["pick"] is not None and set(got["pick"]) == {"pick", "killed"}


def test_run1s_manifest_parameters_name_what_the_text_asks(got):
    need = {"identity_rows", "identity_token_rule", "declaration_sha256", "k", "level", "pinned_blobs", "cells",
            "dropped_at_pin", "searched", "fitted_values", "forecast_json", "forecast_sha256", "states_sha256",
            "population_sha256", "calendars", "seeds", "judged_sessions_sha256", "pick", "killed", "screen",
            "forecast_folds", "identity_commits", "data_manifest_sha256", "identity_covered"}
    assert need <= set(got["param_keys"])


def test_v2_a10_flagging_runs_its_consequence_inside_run1_once_per_class(got):
    v = got["v2"]
    assert v["code"] == 0 and v["calls"] == ["window"]                    # s1 and s2 share `window`: one run (n9)
    assert v["consequence_rows"] >= 4                                      # both shares, both levels
    assert v["verdict_cells"] == ["s1", "s2"] and v["pick_row"]           # stage B reads on after it
    for c, closed in v["verdict_closed"].items():
        assert (v["killed"].get(c) == "A10's consequence") == closed
        assert (c in v["choice_cells"]) == (not closed)
