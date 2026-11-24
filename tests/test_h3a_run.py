"""Synthetic unit tests for `scripts/h3a_run.py` (E-279, E-285).

Uses tiny synthetic parameters (`R=1`, small `M` and `T`) on S1 toys only; never reads bars or writes `results/`.
Isolates clean-run gate tests to a subprocess so `extended.results` is never imported in the fast-tier process (Q-204).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from extended import three_way_h3a as H
from extended import three_way_s1 as S1
from scripts import h3a_run as HR

ROOT = Path(__file__).resolve().parent.parent


def test_a1_a2_and_final_report_on_tiny_synthetic_inputs(tmp_path):
    tiny_s1 = S1.S1Params(n_sessions=75, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.0,
                          rate=1.0, rate_beta=1.0, hold_mean=25.0, hold_stop=40.0, time_limit=90.0)
    starts = tuple(range(6))

    a1_df, a1_h, a1_meta = HR.run_a1(
        histories=(0,), M=24, starts=starts, horizon=63, j_prime=4,
        s1_params=tiny_s1, rules=H.TOY_RULES_EXACT, workers=1, run_smaller_j=False,
    )
    assert len(a1_df) == 36
    assert len(a1_h) == 36
    assert a1_meta["stress_arms_count"] == 15
    assert a1_meta["seed_roles"] == ["h3a_histories", "h3a_coins"]

    a2_df, a2_h, a2_meta = HR.run_a2(
        histories=(0,), M=12, starts=starts, horizon=63, j_prime=4,
        s1_params=tiny_s1, workers=1,
    )
    assert len(a2_df) == 18
    assert len(a2_h) == 18
    assert a2_meta["seed_roles"] == ["h3a_histories", "h3a_coins"]

    a1_df.to_csv(tmp_path / "h3a_a1.csv", index=False)
    a1_h.to_csv(tmp_path / "h3a_a1_per_history.csv", index=False)
    a2_df.to_csv(tmp_path / "h3a_a2.csv", index=False)
    a2_h.to_csv(tmp_path / "h3a_a2_per_history.csv", index=False)

    summary_df, rep_meta = HR.build_final_report(tmp_path)
    assert len(summary_df) == 54
    assert rep_meta["pooled_total"] == 54
    assert rep_meta["per_history_count"] == 54
    assert rep_meta["verdict"] in ("PASS_NO_LAXITY", "FAIL_LAXITY_STOP_H3D")


def test_a3_and_a4_slices_on_tiny_synthetic_inputs():
    tiny_s1 = S1.S1Params(n_sessions=75, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.0,
                          rate=1.0, rate_beta=1.0, hold_mean=25.0, hold_stop=40.0, time_limit=90.0)
    starts = tuple(range(4))

    a3_df, a3_meta = HR.run_a3_slice((0,), M=8, starts=starts, horizon=63, s1_params=tiny_s1, workers=1)
    assert len(a3_df) == 1 and a3_meta["seed_roles"] == ["h3a3_history_null"]

    a4_df, a4_meta = HR.run_a4_slice((0,), M=8, starts=starts, horizon=63, s1_params=tiny_s1, workers=1)
    assert set(a4_df["plant"]) == {"P1", "P2", "P3", "P4"}
    assert "copy_against_stagger" in a4_meta


def test_h3a_run_refuses_outside_clean_run_in_subprocess():
    code = (
        "import os; os.environ.pop('S2X_CLEAN_RUN', None); "
        "from scripts import h3a_run as HR; "
        "HR.check_runtime_gates('A1')"
    )
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0
    assert "clean run" in (proc.stderr + proc.stdout).lower()

