"""Q-117f: F-03's run-1 reads of registered result files after the walk, against the files' real schemas.

F-03's run 1 (clean checkout of 97e16a3) walked every day, ran its replays, then crashed in `scripts/fo_opening.py`'s
`mean_dv_c` with `KeyError: 'place'`: the reader took Stage 2's value map for a wide file, while
`vendor/stage2/results/u_value_map.csv` is long (`section, base, phase, state, measure, value, n, unit, note`), and the
synthetic runs had stubbed `Ctx.mean_dv` with a constant, so no test ever ran the reader on a file. These tests run the
reader on a synthetic value map built from the vendored header (`tests/fo_value_map_fixture.py`) -- the selection, every
refusal -- and on the vendored file itself, where they assert **only** that exactly one row is selected and its value is
finite (no value is printed or asserted). The other files run 1 reads after the walk (a*'s (b), `amplitude_b`) are
checked the same way: header, manifest, keys and row counts only.

All of it runs in a process of its own (`tests/fo_vendored_reads.py`; the vendored tree on the path).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VALUE_MAP_COLUMNS = ["section", "base", "phase", "state", "measure", "value", "n", "unit", "note"]


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "fo_vendored_reads.py"), str(ROOT)], capture_output=True,
                       text=True, timeout=600, env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


# ---- the fixture is the vendored schema
def test_the_fixture_has_the_vendored_long_header(got):
    assert got["vm_header"] == VALUE_MAP_COLUMNS                   # the long schema the reader is written for
    assert got["vm_manifest_matches"]                              # the header is the manifest's columns
    assert got["fixture_header"] == got["vm_header"]               # built from the real header, not typed


# ---- the reader on synthetic long files (synthetic values only)
def test_mean_dv_c_selects_the_one_target_row_among_decoys(got):
    s = got["synthetic"]["long"]
    assert s["ok"] and s["value"] == 1000.0                        # each decoy differs from the target by one key


@pytest.mark.parametrize("case", ["missing", "duplicate"])
def test_mean_dv_c_refuses_unless_exactly_one_row(got, case):
    s = got["synthetic"][case]
    assert not s["ok"] and s["refused"], s
    assert ("0 rows" if case == "missing" else "2 rows") in s["msg"]


@pytest.mark.parametrize("case", ["nan", "blank", "inf", "text"])
def test_mean_dv_c_refuses_a_value_that_is_not_finite(got, case):
    s = got["synthetic"][case]
    assert not s["ok"] and s["refused"], s
    assert "finite" in s["msg"]


def test_mean_dv_c_refuses_the_wide_schema_by_name_not_by_keyerror(got):
    s = got["synthetic"]["wide"]
    assert not s["ok"] and s["refused"], s                         # a refusal naming the columns, never a KeyError
    assert "state" in s["msg"] and "measure" in s["msg"] and "value" in s["msg"]


def test_mean_dv_c_keeps_the_manifest_check(got):
    s = got["synthetic"]["tampered"]
    assert not s["ok"] and s["refused"], s


# ---- the vendored files: counts and finiteness, never a value
def test_mean_dv_c_on_the_vendored_value_map_finds_one_finite_value(got):
    assert "vm_refused" not in got, got.get("vm_refused")
    assert got["vm_rows_selected"] == 1
    assert got["vm_finite"] is True


def test_follow_lift_files_have_the_columns_amplitude_b_reads(got):
    assert got["vendored_results_dir_is_the_snapshot"]
    assert set(got["follow_schema"]) == {"s1_sided_coin.csv", "s3_event_kinds.csv", "s3_latency.csv"}
    for name, s in got["follow_schema"].items():
        assert s["manifest_matches"], name
        assert s["missing"] == [], (name, s["missing"])


def test_amplitude_b_on_the_vendored_files_finds_one_finite_row_each(got):
    assert "follow_error" not in got, got.get("follow_error")
    assert len(got["follow_lifts_declared"]) == 4
    assert got["follow_keys"] == got["follow_lifts_declared"]     # one row for each, in order (it refuses else)
    assert got["follow_finite"] == [True] * 4


def test_the_data_manifest_run1_hashes_is_there(got):
    assert got["data_manifest_file"]


def test_run2s_p14_start_rows_are_there_for_both_scorecard_arms(got):
    assert got["journey_is_vendored"] and got["journey_manifest_matches"]
    assert got["journey_missing"] == []
    n = got["journey_p14_start_rows"]
    assert set(n) == {"verdict", "point"} and all(v > 0 for v in n.values()), n      # counts only
    assert all(v is not None and v > 0 for v in got["journey_loaded"].values()), got["journey_loaded"]
