"""Synthetic round-trip and refusal tests for `extended/h4_collect.py` (W42-R1 V-1/V-3 adapter)."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from extended import h4_collect as HC
from extended import wave42 as W


def _synthetic_readings(n_starts: int = 3, n_seeds: int = 4) -> tuple[tuple[str, ...], tuple[int, ...], dict[str, W.BaselineReading]]:
    starts = tuple(f"2020-01-0{2 + i}" for i in range(n_starts))
    seeds = tuple(range(n_seeds))
    rng = np.random.default_rng(17)
    out: dict[str, W.BaselineReading] = {}
    for bi, name in enumerate(W.BASELINES):
        vals: dict[str, np.ndarray] = {}
        for ki, key in enumerate(sorted(W.REQUIRED)):
            arr = rng.uniform(0.0, 1.0, size=(n_starts, n_seeds)) + bi * 0.1 + ki * 0.01
            if key == "first_payout_days":
                arr[0, 0] = np.nan                              # exercise canonical blank / NaN round-trip
            vals[key] = arr
        out[name] = W.BaselineReading(name=name, block=W.BLOCK, reading=W.READING, starts=starts, seeds=seeds, values=vals)
    return starts, seeds, out


def _write_fixture(tmp_path: Path, readings: dict[str, W.BaselineReading], starts: tuple[str, ...],
                   seeds: tuple[int, ...]) -> tuple[Path, dict]:
    cols, rows = HC.rows_from_readings(readings)
    p = tmp_path / W.COLLECTION_RESULT
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    sidecar = {
        "sha256": sha,
        "parameters": {
            "block": W.BLOCK,
            "reading": W.READING,
            "arm": W.ARM,
            "denial": 0.0,
            "placement": "off",
            "focused_trader": "off",
            "W": W.W,
            "baselines": list(W.BASELINES),
            "starts": list(starts),
            "seeds": list(seeds),
            "calendar_sha256": W.calendar_digest(starts),
            "readings_sha256": W.readings_digest(readings),
        },
    }
    return p, sidecar


def test_bit_for_bit_round_trip_including_nans(tmp_path):
    starts, seeds, readings = _synthetic_readings()
    p, sidecar = _write_fixture(tmp_path, readings, starts, seeds)
    loaded = HC.w42_readings(p, sidecar)
    assert W.readings_digest(loaded) == W.readings_digest(readings)
    for name in W.BASELINES:
        assert loaded[name].starts == starts and loaded[name].seeds == seeds
        for k in W.REQUIRED:
            np.testing.assert_array_equal(loaded[name].values[k], readings[name].values[k])


def test_refuses_tampered_csv_sha256(tmp_path):
    starts, seeds, readings = _synthetic_readings()
    p, sidecar = _write_fixture(tmp_path, readings, starts, seeds)
    p.write_bytes(p.read_bytes() + b"\n")
    with pytest.raises(HC.H4CollectRefused, match="sha256"):
        HC.w42_readings(p, sidecar)


def test_refuses_missing_row_and_duplicate_row(tmp_path):
    starts, seeds, readings = _synthetic_readings()
    p, sidecar = _write_fixture(tmp_path, readings, starts, seeds)
    lines = p.read_text(encoding="utf-8").splitlines()
    # Drop last row and update sha256 to isolate completeness refusal
    p_short = tmp_path / "short.csv"
    p_short.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8", newline="\n")
    sc = json.loads(json.dumps(sidecar))
    sc["sha256"] = hashlib.sha256(p_short.read_bytes()).hexdigest()
    with pytest.raises(HC.H4CollectRefused, match="incomplete"):
        HC.w42_readings(p_short, sc)

    # Duplicate row
    p_dup = tmp_path / "dup.csv"
    p_dup.write_text("\n".join(lines + [lines[1]]) + "\n", encoding="utf-8", newline="\n")
    sc2 = json.loads(json.dumps(sidecar))
    sc2["sha256"] = hashlib.sha256(p_dup.read_bytes()).hexdigest()
    with pytest.raises(HC.H4CollectRefused, match="duplicate"):
        HC.w42_readings(p_dup, sc2)


def test_refuses_heldout_start_and_bad_digest(tmp_path):
    starts, seeds, readings = _synthetic_readings()
    p, sidecar = _write_fixture(tmp_path, readings, starts, seeds)
    sc_ho = json.loads(json.dumps(sidecar))
    sc_ho["parameters"]["starts"] = ["2024-01-02", "2024-01-03", "2024-01-04"]
    with pytest.raises(HC.H4CollectRefused, match="outside the search years"):
        HC.w42_readings(p, sc_ho)

    sc_bad = json.loads(json.dumps(sidecar))
    sc_bad["parameters"]["readings_sha256"] = "0" * 64
    with pytest.raises(HC.H4CollectRefused, match="readings_sha256"):
        HC.w42_readings(p, sc_bad)


def test_refuses_missing_column_and_inf_value(tmp_path):
    starts, seeds, readings = _synthetic_readings()
    p, sidecar = _write_fixture(tmp_path, readings, starts, seeds)
    # Remove one required column
    with p.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    cols = [c for c in HC.COLUMNS if c != "orders_max"]
    p_mc = tmp_path / "mc.csv"
    with p_mc.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            r2 = {k: v for k, v in r.items() if k in cols}
            w.writerow(r2)
    sc = json.loads(json.dumps(sidecar))
    sc["sha256"] = hashlib.sha256(p_mc.read_bytes()).hexdigest()
    with pytest.raises(HC.H4CollectRefused, match="missing required columns"):
        HC.w42_readings(p_mc, sc)

    # Plant inf
    p_inf = tmp_path / "inf.csv"
    rows[0]["orders_max"] = "inf"
    with p_inf.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HC.COLUMNS)
        w.writeheader()
        w.writerows(rows)
    sc2 = json.loads(json.dumps(sidecar))
    sc2["sha256"] = hashlib.sha256(p_inf.read_bytes()).hexdigest()
    with pytest.raises(HC.H4CollectRefused, match="infinite"):
        HC.w42_readings(p_inf, sc2)

