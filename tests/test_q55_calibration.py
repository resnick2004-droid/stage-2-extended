"""Q-55: Q-16's calibration as one clean-run entry point (`scripts/q55_calibration.py`), at a tiny size.

What is asserted:
- the pairs step authorises Stage 2's engine read through `extended.reader` (purpose `registered_design`, declaration
  E-035, the A1 tables and the bars) before anything is read, and a refusal ends it (exit 3, nothing written) -- the
  reader's verdict itself is whatever the reader admits today (Q-58 adds the purpose);
- the entry point refuses this tree's `results/` outside a clean run at once, before any computation;
- end to end on synthetic pairs and a synthetic calendar (a temporary results folder): the five result files are
  written with manifests whose sha256 matches, `bm63c_table` holds every calibrated level, the two-sample file holds
  both block-count rules, the power file every part; and `scripts/q16_tables.py --results` renders the note's tables
  from the result files alone.
The vendored writer is imported only in the child processes (CLAUDE.md).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "scripts" / "q55_calibration.py"
PAIRS = ROOT / "scripts" / "q16_p16_pairs.py"
RESULTS = ("calibration_lift", "calibration_p", "calibration_two_sample", "calibration_power", "bm63c_table")


def _env():
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    e.setdefault("OMP_NUM_THREADS", "1")
    return e


def _run(args, timeout=900):
    return subprocess.run([sys.executable, *map(str, args)], cwd=str(ROOT), capture_output=True, text=True,
                          timeout=timeout, env=_env())


def test_pairs_step_asks_the_reader_before_reading(tmp_path):
    r = _run([PAIRS, "--out", tmp_path / "pairs", "--check-read"])
    out = r.stdout + r.stderr
    assert "reader: purpose=registered_design declaration=E-035" in out, out[-2000:]
    for f in ("data/atlas/A1/events.parquet", "data/atlas/A1/days.parquet", "data/bars/NQ/bars.parquet"):
        assert f in out
    assert r.returncode in (0, 3), out[-2000:]
    if r.returncode == 3:                                   # today's reader: no such purpose yet (Q-58)
        assert "REFUSED" in out
    else:
        assert "AUTHORISED" in out
    assert not (tmp_path / "pairs").exists()                 # --check-read reads and writes nothing


def test_entry_point_refuses_this_trees_results_outside_a_clean_run():
    r = _run([ENTRY], timeout=300)
    assert r.returncode == 3 and "REFUSED" in r.stdout and "clean" in r.stdout, r.stdout[-2000:] + r.stderr[-2000:]
    assert "step" not in r.stdout.lower().split("refused")[0]   # refused before any step ran


def _synthetic_inputs(d: Path) -> tuple[Path, Path]:
    """A calendar of 657 judged weekdays (plus a year before) and 20 offers a session with both sides walked."""
    rng = np.random.default_rng([20261912, 55])
    days = pd.bdate_range("2023-01-02", periods=262 + 657)
    cal = pd.DataFrame({"date": days.strftime("%Y-%m-%d"), "day_kind": "n"})
    assert (cal["date"] >= "2024-01-02").sum() >= 657
    cal = pd.concat([cal[cal["date"] < "2024-01-02"].iloc[:255], cal[cal["date"] >= "2024-01-02"].iloc[:657]])
    cal_p = d / "days.parquet"
    cal.to_parquet(cal_p, index=False)
    judged = cal[cal["date"] >= "2024-01-02"]["date"].tolist()
    rows = []
    for di, dt in enumerate(judged):
        a = rng.standard_normal() * 0.5
        for j in range(20):
            slot = 15 * j
            up = rng.random() < 1 / (1 + np.exp(-a))
            r = {"date": dt, "day_kind": "n", "slot": slot, "entry_slot": slot + 1,
                 "coin": int(rng.choice([-1, 1]))}
            for R in (1.0, 1.5, 3.0):
                kl, ks = (1, 0) if up else (0, 1)
                r[f"kl_{R:g}"], r[f"ks_{R:g}"] = kl, ks
                r[f"rl_{R:g}"] = float(R - 0.05) if kl == 1 else -1.05
                r[f"rs_{R:g}"] = float(R - 0.05) if ks == 1 else -1.05
                r[f"xl_{R:g}"] = r[f"xs_{R:g}"] = slot + 1 + int(rng.integers(5, 60))
            rows.append(r)
    pairs = pd.DataFrame(rows)
    pdir = d / "pairs"
    pdir.mkdir()
    pq = pdir / "p16_pairs.parquet"
    pairs.to_parquet(pq, index=False)
    (pdir / "p16_pairs.json").write_text(json.dumps({
        "identity": "HOLDS: synthetic (test)", "parquet_sha256": hashlib.sha256(pq.read_bytes()).hexdigest(),
        "trades_sha256": "synthetic"}), encoding="utf-8")
    return pdir, cal_p


@pytest.mark.slow
def test_entry_point_end_to_end_at_a_tiny_size(tmp_path):
    pdir, cal = _synthetic_inputs(tmp_path)
    res = tmp_path / "results"
    r = _run([ENTRY, "--results-dir", res, "--work", tmp_path / "work", "--pairs", pdir, "--days", cal,
              "--reps", "2000", "--boot-reps", "16", "--d621-reps", "1000", "--power-reps", "400"], timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "EXIT 0" in r.stdout
    for name in RESULTS:
        csv, man = res / f"{name}.csv", res / f"{name}.csv.manifest.json"
        assert csv.is_file() and man.is_file(), name
        m = json.loads(man.read_text(encoding="utf-8"))
        assert m["sha256"] == hashlib.sha256(csv.read_bytes()).hexdigest(), name
        assert m["parameters"]["pairs_supplied"] is True                       # not extracted by this run
    t = pd.read_csv(res / "bm63c_table.csv")
    assert len(t) == 8 and {"level", "critical"} <= set(t.columns)
    two = pd.read_csv(res / "calibration_two_sample.csv", low_memory=False)
    assert set(two["df_rule"]) == {"treated", "all"}
    pw = pd.read_csv(res / "calibration_power.csv", low_memory=False)
    assert set(pw["part"]) == {"lift", "p", "two_sample"}
    lift = pd.read_csv(res / "calibration_lift.csv", low_memory=False)
    assert set(lift["section"]) == {"size", "boot"}
    tb = _run([ROOT / "scripts" / "q16_tables.py", "--results", res], timeout=600)
    assert tb.returncode == 0, tb.stdout[-2000:] + tb.stderr[-2000:]
    for title in ("Table 1.", "Table 5.", "Table 7.", "Table 8.", "Table 10.", "Table F8."):
        assert title in tb.stdout, title
