"""Synthetic round-trip, contract-refusal, and end-to-end tests for `extended/h4_collect.py`."""
from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import h4_collect as HC
from extended import wave42 as W

ROOT = Path(__file__).resolve().parents[1]


def _synthetic_readings(n_starts: int = 5, n_seeds: int = 4) -> dict[str, W.BaselineReading]:
    rng = np.random.default_rng(123456)
    starts = tuple(f"2020-01-{2 + i:02d}" for i in range(n_starts))
    seeds = tuple(range(n_seeds))
    out: dict[str, W.BaselineReading] = {}
    for bi, name in enumerate(W.BASELINES):
        vals: dict[str, np.ndarray] = {}
        for k in sorted(W.REQUIRED):
            arr = rng.uniform(0.0, 100.0, size=(n_starts, n_seeds)) + bi * 0.25
            if k == "peak_oop_12_months":
                arr[-1, :] = np.nan
            vals[k] = arr
        out[name] = W.BaselineReading(name=name, block=W.BLOCK, reading=W.READING,
                                      starts=starts, seeds=seeds, values=vals)
    return out


def _write_collection(tmp_path: Path, readings: dict[str, W.BaselineReading], *,
                      lineterminator: str = "\n", via_pandas: bool = False) -> tuple[Path, dict]:
    cols, rows = HC.rows_from_readings(readings)
    csv_path = tmp_path / W.COLLECTION_RESULT
    if via_pandas:
        df = pd.DataFrame(rows, columns=list(cols))
        csv_path.write_bytes(df.to_csv(index=False, lineterminator=lineterminator).encode("utf-8"))
    else:
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols, lineterminator=lineterminator)
            writer.writeheader()
            writer.writerows(rows)
    file_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    first = readings[W.BASELINES[0]]
    sidecar = {
        "sha256": file_sha,
        "parameters": {
            "block": W.BLOCK,
            "reading": W.READING,
            "arm": W.ARM,
            **W.VERDICT,
            "W": W.W,
            "baselines": list(W.BASELINES),
            "starts": list(first.starts),
            "seeds": list(first.seeds),
            "calendar_sha256": W.calendar_digest(first.starts),
            "readings_sha256": W.readings_digest(readings),
        },
    }
    return csv_path, sidecar


def _rehash(csv_path: Path, sidecar: dict) -> dict:
    s = copy.deepcopy(sidecar)
    s["sha256"] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    return s


@pytest.mark.parametrize("lineterminator,via_pandas", [
    ("\n", False), ("\r\n", False), ("\n", True), ("\r\n", True),
])
def test_round_trip_bit_for_bit_across_writers_and_line_endings(tmp_path: Path, lineterminator: str,
                                                                via_pandas: bool) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings, lineterminator=lineterminator, via_pandas=via_pandas)
    got = HC.w42_readings(csv_path, sidecar)
    assert tuple(got.keys()) == W.BASELINES
    assert W.readings_digest(got) == W.readings_digest(readings)
    for name in W.BASELINES:
        for k in W.REQUIRED:
            np.testing.assert_array_equal(got[name].values[k], readings[name].values[k])


# ---- F1: sidecar contract validation BEFORE opening csv_path ----

@pytest.mark.parametrize("field,bad_val,pat", [
    ("block", "held_out", "search years"),
    ("block", "confirmation", "search years"),
    ("block", "Search", "search years"),
    ("reading", "as_walked", "reading must be"),
    ("reading", "as_traded", "reading must be"),
    ("arm", "worse_1", "arm must be"),
    ("denial", 0.25, "verdict setting 'denial'"),
    ("denial", True, "verdict setting 'denial'"),
    ("denial", False, "verdict setting 'denial'"),
    ("placement", "on", "verdict setting 'placement'"),
    ("focused_trader", "on", "verdict setting 'focused_trader'"),
    ("W", 63, "sidecar W must be"),
    ("W", "126", "sidecar W must be"),
    ("W", True, "sidecar W must be"),
    ("calendar_sha256", "not-a-hash", "calendar_sha256"),
    ("calendar_sha256", "A" * 64, "calendar_sha256"),
    ("calendar_sha256", "0" * 64, "does not match starts digest"),
    ("readings_sha256", "short", "readings_sha256"),
])
def test_f1_refuses_bad_sidecar_contract_fields_before_reading_csv(tmp_path: Path, field: str, bad_val, pat: str) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)
    bad = copy.deepcopy(sidecar)
    bad["parameters"][field] = bad_val
    # Fails on the real CSV AND on a nonexistent CSV with the specific contract message (never "not found")
    for p in (csv_path, tmp_path / "does_not_exist.csv"):
        with pytest.raises(HC.H4CollectRefused, match=pat):
            HC.w42_readings(p, bad)


def test_refuses_missing_parameters_and_manifest_keys(tmp_path: Path) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)
    with pytest.raises(HC.H4CollectRefused, match="mapping"):
        HC.w42_readings(csv_path, "not-a-dict")  # type: ignore[arg-type]
    with pytest.raises(HC.H4CollectRefused, match="parameters"):
        HC.w42_readings(csv_path, {"sha256": sidecar["sha256"]})
    bad = copy.deepcopy(sidecar)
    del bad["parameters"]["arm"]
    with pytest.raises(HC.H4CollectRefused, match="missing required keys"):
        HC.w42_readings(csv_path, bad)


# ---- F2: literal NaN/Inf in CSV and Inf in rows_from_readings ----

@pytest.mark.parametrize("literal", ["nan", "NaN", "-nan", "+NaN", "inf", "-inf", "Infinity", "abc"])
def test_f2_refuses_non_finite_and_literal_nan_cells(tmp_path: Path, literal: str) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    cells = lines[1].split(",")
    cells[3] = literal
    lines[1] = ",".join(cells)
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused):
        HC.w42_readings(csv_path, _rehash(csv_path, sidecar))


def test_f2_rows_from_readings_refuses_infinite_values() -> None:
    readings = _synthetic_readings()
    readings["p14"].values["net_month_1"][0, 0] = np.inf
    with pytest.raises(HC.H4CollectRefused, match="infinite"):
        HC.rows_from_readings(readings)
    readings["p14"].values["net_month_1"][0, 0] = -np.inf
    with pytest.raises(HC.H4CollectRefused, match="infinite"):
        HC.rows_from_readings(readings)


# ---- F3: strict ISO calendar dates and exact int seeds ----

@pytest.mark.parametrize("bad_starts,pat", [
    (["2020-99-99"], "invalid calendar date"),
    (["2020-02-30"], "invalid calendar date"),
    (["2021"], "ISO YYYY-MM-DD"),
    ([20200102, 20200103], "ISO YYYY-MM-DD"),
    (["2024-01-02"], "outside the search years"),
    (["2020-01-03", "2020-01-02"], "strictly increasing"),
    (["2020-01-02", "2020-01-02"], "strictly increasing"),
])
def test_f3_refuses_invalid_starts(tmp_path: Path, bad_starts, pat: str) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)
    bad = copy.deepcopy(sidecar)
    bad["parameters"]["starts"] = bad_starts
    with pytest.raises(HC.H4CollectRefused, match=pat):
        HC.w42_readings(csv_path, bad)


@pytest.mark.parametrize("bad_seeds", [
    [0.0, 1.0, 2.0, 3.0],
    [0.9, 1.9, 2.9, 3.9],
    ["0", "1", "2", "3"],
    [False, True],
    [1, 2, 3, 4],
])
def test_f3_refuses_non_exact_int_seeds(tmp_path: Path, bad_seeds) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)
    bad = copy.deepcopy(sidecar)
    bad["parameters"]["seeds"] = bad_seeds
    with pytest.raises(HC.H4CollectRefused):
        HC.w42_readings(csv_path, bad)


# ---- F4 & F5: UTF-8, CSV structure, canonical seeds, rows_from_readings guards ----

def test_f4_refuses_invalid_utf8_and_empty_and_ragged_and_duplicate_header(tmp_path: Path) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)

    # Invalid UTF-8
    bad_utf8 = tmp_path / "bad_utf8.csv"
    bad_utf8.write_bytes(b"\xff\xfe\x00\x01")
    with pytest.raises(HC.H4CollectRefused, match="UTF-8"):
        HC.w42_readings(bad_utf8, _rehash(bad_utf8, sidecar))

    # Empty file
    empty = tmp_path / "empty.csv"
    empty.write_bytes(b"")
    with pytest.raises(HC.H4CollectRefused, match="header"):
        HC.w42_readings(empty, _rehash(empty, sidecar))

    # Duplicate header
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    dup_hdr = tmp_path / "dup_hdr.csv"
    dup_hdr.write_text(lines[0] + ",seed\n" + "\n".join(ln + ",0" for ln in lines[1:]) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="duplicate column"):
        HC.w42_readings(dup_hdr, _rehash(dup_hdr, sidecar))

    # Ragged row (too many fields) and short row (too few fields) and header-only CSV
    rag = tmp_path / "rag.csv"
    rag.write_text("\n".join([lines[0], lines[1] + ",999"] + lines[2:]) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="wrong number"):
        HC.w42_readings(rag, _rehash(rag, sidecar))
    short = tmp_path / "short.csv"
    short.write_text("\n".join([lines[0], ",".join(lines[1].split(",")[:-1])] + lines[2:]) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="wrong number"):
        HC.w42_readings(short, _rehash(short, sidecar))
    hdr_only = tmp_path / "hdr_only.csv"
    hdr_only.write_text(lines[0] + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="incomplete"):
        HC.w42_readings(hdr_only, _rehash(hdr_only, sidecar))


@pytest.mark.parametrize("bad_seed_token", ["+0", "00", "-0", "0_0", "abc"])
def test_f5_refuses_non_canonical_csv_seed_tokens(tmp_path: Path, bad_seed_token: str) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    parts = lines[1].split(",")
    parts[2] = bad_seed_token
    lines[1] = ",".join(parts)
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="non-canonical seed"):
        HC.w42_readings(csv_path, _rehash(csv_path, sidecar))


def test_f5_rows_from_readings_guards() -> None:
    readings = _synthetic_readings()
    with pytest.raises(HC.H4CollectRefused, match="collides"):
        HC.rows_from_readings(readings, extra_keys=["seed"])
    bad_block = copy.deepcopy(readings)
    bad_block["p14"] = W.BaselineReading("p14", "held_out", W.READING,
                                         readings["p14"].starts, readings["p14"].seeds, readings["p14"].values)
    with pytest.raises(HC.H4CollectRefused, match="search years"):
        HC.rows_from_readings(bad_block)
    bad_val = copy.deepcopy(readings)
    bad_val["p14"].values["net_month_1"] = [["not-a-number"] * 4 for _ in range(5)]  # type: ignore[assignment]
    with pytest.raises(HC.H4CollectRefused, match="non-numeric"):
        HC.rows_from_readings(bad_val)
    bad_reading = copy.deepcopy(readings)
    bad_reading["p14"] = W.BaselineReading("p14", W.BLOCK, "as_walked",
                                           readings["p14"].starts, readings["p14"].seeds, readings["p14"].values)
    with pytest.raises(HC.H4CollectRefused, match="expected 'martingale_outcome'"):
        HC.rows_from_readings(bad_reading)
    bad_cplx = copy.deepcopy(readings)
    bad_cplx["p14"].values["net_month_1"] = np.ones((5, 4), dtype=np.complex128)
    with pytest.raises(HC.H4CollectRefused, match="complex"):
        HC.rows_from_readings(bad_cplx)
    # extra_keys round-trip
    extra_r = copy.deepcopy(readings)
    for b in W.BASELINES:
        extra_r[b].values["beside_bonus"] = np.full((5, 4), 1.5)
    cols, rows = HC.rows_from_readings(extra_r, extra_keys=["beside_bonus"])
    assert "beside_bonus" in cols and len(rows) == 4 * 5 * 4


def test_refuses_tampered_bytes_missing_duplicate_unknown_and_digest_drift(tmp_path: Path) -> None:
    readings = _synthetic_readings()
    csv_path, sidecar = _write_collection(tmp_path, readings)

    # Byte tamper without updating sha256
    orig = csv_path.read_bytes()
    csv_path.write_bytes(orig + b"\n")
    with pytest.raises(HC.H4CollectRefused, match="sha256"):
        HC.w42_readings(csv_path, sidecar)
    csv_path.write_bytes(orig)

    # Missing row
    lines = orig.decode("utf-8").splitlines()
    csv_path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="incomplete"):
        HC.w42_readings(csv_path, _rehash(csv_path, sidecar))

    # Duplicate row
    csv_path.write_text("\n".join(lines + [lines[1]]) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="duplicate"):
        HC.w42_readings(csv_path, _rehash(csv_path, sidecar))

    # Unknown baseline
    bad_b = list(lines)
    bad_b[1] = bad_b[1].replace("naive_coin,", "mystery,", 1)
    csv_path.write_text("\n".join(bad_b) + "\n", encoding="utf-8")
    with pytest.raises(HC.H4CollectRefused, match="unknown baseline"):
        HC.w42_readings(csv_path, _rehash(csv_path, sidecar))

    # Digest mismatch with valid bytes
    csv_path.write_bytes(orig)
    bad_d = copy.deepcopy(sidecar)
    bad_d["parameters"]["readings_sha256"] = "0" * 64
    with pytest.raises(HC.H4CollectRefused, match="readings_sha256"):
        HC.w42_readings(csv_path, bad_d)


def test_end_to_end_wave42_apply_with_real_adapter(tmp_path: Path, monkeypatch) -> None:
    import sys
    spec_a = importlib.util.spec_from_file_location("wave42_apply_e2e", ROOT / "scripts" / "wave42_apply.py")
    A = importlib.util.module_from_spec(spec_a)
    sys.modules["wave42_apply_e2e"] = A
    spec_a.loader.exec_module(A)

    # Build a 300-session synthetic search calendar starting 2020-01-02 and ending 2023-12-29
    cal = tuple(d.isoformat() for d in pd.bdate_range("2020-01-02", periods=299).date) + ("2023-12-29",)
    rng = np.random.default_rng(777)
    n_s, n_c = len(cal), W.H4_MIN_SEEDS
    seeds = tuple(range(n_c))
    readings: dict[str, W.BaselineReading] = {}
    for bi, name in enumerate(W.BASELINES):
        u = bi * 0.15 + rng.normal(0.0, 0.4, size=(n_s, n_c))
        vals = {
            "net_month_1": 50.0 * u,
            "net_month_2": 50.0 * u + rng.normal(0, 10, (n_s, n_c)),
            "net_month_3": 50.0 * u + rng.normal(0, 10, (n_s, n_c)),
            "peak_month_1": np.abs(rng.normal(120, 20, (n_s, n_c))),
            "peak_month_2": np.abs(rng.normal(120, 20, (n_s, n_c))),
            "peak_month_3": np.abs(rng.normal(120, 20, (n_s, n_c))),
            "spent_before_first_payout": np.maximum(49.0, 300.0 - 40.0 * u),
            "first_pass_days": np.clip(40.0 - 5.0 * u, 1.0, W.W + 1),
            "first_payout_days": np.clip(55.0 - 5.0 * u, 2.0, W.W + 1),
            "cash_to_first_pass": np.maximum(49.0, 180.0 - 20.0 * u),
            "peak_oop_12_months": np.maximum(49.0, 600.0 - 60.0 * u),
            "share_months_positive": np.clip(0.5 + 0.08 * u, 0.0, 1.0),
            "taken_mean": np.maximum(0.5, 4.0 + 0.3 * u),
            "accounts_max": np.maximum(1.0, 3.0 - 0.1 * u),
            "orders_max": np.maximum(1.0, 5.0 - 0.1 * u),
        }
        vals["first_payout_days"] = np.maximum(vals["first_payout_days"], vals["first_pass_days"])
        readings[name] = W.BaselineReading(name, W.BLOCK, W.READING, cal, seeds, vals)

    rdir = tmp_path / "results"
    rdir.mkdir()
    csv_path, sidecar = _write_collection(rdir, readings)
    Path(f"{csv_path}.manifest.json").write_text(json.dumps(sidecar), encoding="utf-8")

    # Synthetic search_calendar + held-out calendar
    sc_bytes = ("date\n" + "\n".join(cal) + "\n").encode("utf-8")
    sc_path = rdir / W.SEARCH_CALENDAR
    sc_path.write_bytes(sc_bytes)
    ho_dates = [d.isoformat() for d in pd.bdate_range("2024-01-02", periods=650).date]
    ho_bytes = ("date\n" + "\n".join(ho_dates) + "\n").encode("utf-8")
    (rdir / W.HELD_OUT_CALENDAR).write_bytes(ho_bytes)

    monkeypatch.setattr(W, "SEARCH_CALENDAR_SHA256", hashlib.sha256(sc_bytes).hexdigest())
    monkeypatch.setattr(W, "HELD_OUT_CALENDAR_SHA256", hashlib.sha256(ho_bytes).hexdigest())

    class _Cal:
        dates = cal
        file_sha256 = hashlib.sha256(sc_bytes).hexdigest()
        calendar_sha256 = W.calendar_digest(cal)

    written = {}
    def _writer(df, name, **kw):
        written["df"] = df
        written["name"] = name
        written["kw"] = kw

    sources = A.Sources(adapter=HC.w42_readings, calendar_loader=lambda _p: _Cal(),
                        fee=lambda: (49.0, W.FEE_SOURCE, "f" * 64), writer=_writer)
    params = A.apply(rdir, sources)
    assert written["name"] == W.OUTPUT_NAME
    assert params["h4_result_sha256"] == sidecar["sha256"]
    assert params["readings_sha256"] == sidecar["parameters"]["readings_sha256"]
