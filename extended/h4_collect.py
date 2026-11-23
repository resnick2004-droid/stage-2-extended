"""H4's collection adapter for W42-R1 (`extended.h4_collect:w42_readings`; W42-R1 V-1 / V-3, H4 section 9).

Pure CSV <-> `extended.wave42.BaselineReading` adapter for H4-C's single collection result (`results/h4_w42_input.csv`)
and its sidecar manifest. Draws no randomness, reads no bars, and never touches the held-out years.

Contract (W42-R1 section 1.1 & H4 section 9):
- `rows_from_readings(readings)` serialises the four paired `BaselineReading`s to deterministic rows
  (`baseline`, `start`, `seed`, followed by every measure key in sorted order), using canonical empty strings for NaN
  and exact `repr(float)` for finite float64 values so `w42_readings` round-trips bit-for-bit.
- `w42_readings(csv_path, sidecar)` verifies:
  1. `csv_path` exists and its raw bytes hash to `sidecar["sha256"]`;
  2. `sidecar["parameters"]` carries every declared `H4_MANIFEST_KEYS` field (excluding top-level `sha256`), with
     `baselines` equal to `wave42.BASELINES` in order, strictly increasing `starts` within the search years, and
     contiguous `seeds` `0..J-1`;
  3. Every `(baseline, start, seed)` cell is present exactly once (no missing, extra, or duplicate rows) and every
     required measure column (`wave42.REQUIRED`) is present with finite float64 or blank (`NaN`) values;
  4. The reconstructed `BaselineReading` dict reproduces `sidecar["parameters"]["readings_sha256"]` via
     `wave42.readings_digest`.
Any violation raises `H4CollectRefused` before returning.
"""
from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from extended import wave42 as W

ID_COLUMNS: tuple[str, ...] = ("baseline", "start", "seed")
MEASURE_COLUMNS: tuple[str, ...] = tuple(sorted(W.REQUIRED))
COLUMNS: tuple[str, ...] = ID_COLUMNS + MEASURE_COLUMNS


class H4CollectRefused(ValueError):
    """H4's collection file or sidecar violates W42-R1's binding contract."""


def _refuse(msg: str) -> H4CollectRefused:
    return H4CollectRefused(f"h4_collect refuses its input: {msg}")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_cell(raw: str, col: str, row_idx: int) -> float:
    s = raw.strip()
    if s == "":
        return float("nan")
    try:
        val = float(s)
    except ValueError as exc:
        raise _refuse(f"row {row_idx} column {col!r}: not a float or blank ({raw!r})") from exc
    if math.isinf(val):
        raise _refuse(f"row {row_idx} column {col!r}: infinite value refused ({raw!r})")
    return val


def rows_from_readings(readings: Mapping[str, W.BaselineReading],
                       extra_keys: Sequence[str] = ()) -> tuple[tuple[str, ...], list[dict[str, Any]]]:
    """Serialise four paired `BaselineReading` objects into deterministic CSV rows for `results/h4_w42_input.csv`."""
    if tuple(readings.keys()) != W.BASELINES and set(readings.keys()) != set(W.BASELINES):
        raise _refuse(f"expected baselines {W.BASELINES}, got {tuple(readings.keys())}")
    first = readings[W.BASELINES[0]]
    starts = tuple(str(d) for d in first.starts)
    seeds = tuple(int(c) for c in first.seeds)
    keys = tuple(sorted(set(W.REQUIRED) | set(extra_keys)))
    for name in W.BASELINES:
        b = readings[name]
        if b.name != name:
            raise _refuse(f"baseline {name!r} has mismatched name {b.name!r}")
        if tuple(str(d) for d in b.starts) != starts or tuple(int(c) for c in b.seeds) != seeds:
            raise _refuse(f"baseline {name!r} is not paired on starts and seeds with {W.BASELINES[0]!r}")
        missing = [k for k in keys if k not in b.values]
        if missing:
            raise _refuse(f"baseline {name!r} is missing required measure keys: {missing}")

    cols = ID_COLUMNS + keys
    rows: list[dict[str, Any]] = []
    for name in W.BASELINES:
        b = readings[name]
        mats = {k: np.asarray(b.values[k], dtype=np.float64) for k in keys}
        for k, mat in mats.items():
            if mat.shape != (len(starts), len(seeds)):
                raise _refuse(f"baseline {name!r} key {k!r} has shape {mat.shape}, expected {(len(starts), len(seeds))}")
        for si, start in enumerate(starts):
            for ci, seed in enumerate(seeds):
                rec: dict[str, Any] = {"baseline": name, "start": start, "seed": seed}
                for k in keys:
                    v = float(mats[k][si, ci])
                    rec[k] = "" if math.isnan(v) else repr(v)
                rows.append(rec)
    return cols, rows


def w42_readings(csv_path: Path | str, sidecar: Mapping[str, Any]) -> dict[str, W.BaselineReading]:
    """Read H4-C's `results/h4_w42_input.csv` and sidecar into `{name: BaselineReading}`, failing closed on any drift."""
    path = Path(csv_path)
    if not path.is_file():
        raise _refuse(f"collection CSV not found: {path}")
    if not isinstance(sidecar, Mapping):
        raise _refuse("sidecar manifest must be a mapping")

    want_sha = sidecar.get("sha256")
    if not isinstance(want_sha, str) or len(want_sha) != 64:
        raise _refuse("sidecar missing valid top-level sha256")
    actual_sha = _sha256_file(path)
    if actual_sha != want_sha:
        raise _refuse(f"CSV sha256 {actual_sha[:12]}... does not match sidecar {want_sha[:12]}...")

    params = sidecar.get("parameters")
    if not isinstance(params, Mapping):
        raise _refuse("sidecar missing parameters mapping")
    need_params = [k for k in W.H4_MANIFEST_KEYS if k != "sha256"]
    missing_params = [k for k in need_params if k not in params]
    if missing_params:
        raise _refuse(f"sidecar parameters missing required keys: {missing_params}")

    baselines = tuple(params["baselines"]) if isinstance(params["baselines"], (list, tuple)) else ()
    if baselines != W.BASELINES:
        raise _refuse(f"sidecar baselines must be {W.BASELINES} in order, got {baselines}")
    starts_raw = params["starts"]
    seeds_raw = params["seeds"]
    if not isinstance(starts_raw, (list, tuple)) or not starts_raw:
        raise _refuse("sidecar starts must be a non-empty list")
    if not isinstance(seeds_raw, (list, tuple)) or not seeds_raw:
        raise _refuse("sidecar seeds must be a non-empty list")
    starts = tuple(str(d) for d in starts_raw)
    if len(set(starts)) != len(starts) or list(starts) != sorted(starts):
        raise _refuse("sidecar starts must be strictly increasing ISO dates")
    for d in starts:
        if not (W.SEARCH_FIRST <= d <= W.SEARCH_LAST) or d >= W.HELD_OUT_FIRST:
            raise _refuse(f"start day {d!r} lies outside the search years {W.SEARCH_FIRST}..{W.SEARCH_LAST}")
    try:
        seeds = tuple(int(c) for c in seeds_raw)
    except (TypeError, ValueError) as exc:
        raise _refuse("sidecar seeds must be integers") from exc
    if any(isinstance(c, bool) for c in seeds_raw) or seeds != tuple(range(len(seeds))):
        raise _refuse("sidecar seeds must be contiguous integers 0..J-1")

    block = params["block"]
    reading = params["reading"]
    want_digest = params["readings_sha256"]
    if not isinstance(want_digest, str) or len(want_digest) != 64:
        raise _refuse("sidecar readings_sha256 missing or malformed")

    start_idx = {d: i for i, d in enumerate(starts)}
    seed_idx = {c: i for i, c in enumerate(seeds)}
    n_s, n_c = len(starts), len(seeds)

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise _refuse("collection CSV has no header row")
        fields = tuple(reader.fieldnames)
        if len(set(fields)) != len(fields):
            raise _refuse("collection CSV has duplicate column names")
        missing_cols = [c for c in COLUMNS if c not in fields]
        if missing_cols:
            raise _refuse(f"collection CSV missing required columns: {missing_cols}")
        measure_cols = tuple(c for c in fields if c not in ID_COLUMNS)

        mats: dict[str, dict[str, np.ndarray]] = {
            b: {k: np.full((n_s, n_c), np.nan, dtype=np.float64) for k in measure_cols}
            for b in baselines
        }
        seen: set[tuple[str, str, int]] = set()
        expected_rows = len(baselines) * n_s * n_c

        for row_num, row in enumerate(reader, start=2):
            if None in row or any(v is None for v in row.values()):
                raise _refuse(f"row {row_num}: wrong number of CSV fields")
            bname = row["baseline"].strip()
            if bname not in mats:
                raise _refuse(f"row {row_num}: unknown baseline {bname!r}")
            sday = row["start"].strip()
            if sday not in start_idx:
                raise _refuse(f"row {row_num}: start {sday!r} not in sidecar starts")
            try:
                cval = int(row["seed"].strip())
            except ValueError as exc:
                raise _refuse(f"row {row_num}: non-integer seed {row['seed']!r}") from exc
            if cval not in seed_idx:
                raise _refuse(f"row {row_num}: seed {cval!r} not in sidecar seeds")
            cell = (bname, sday, cval)
            if cell in seen:
                raise _refuse(f"row {row_num}: duplicate cell {cell}")
            seen.add(cell)
            si, ci = start_idx[sday], seed_idx[cval]
            bm = mats[bname]
            for k in measure_cols:
                bm[k][si, ci] = _parse_cell(row[k], k, row_num)

    if len(seen) != expected_rows:
        raise _refuse(f"incomplete collection CSV: got {len(seen)} cells, expected {expected_rows}")

    readings: dict[str, W.BaselineReading] = {
        b: W.BaselineReading(name=b, block=block, reading=reading, starts=starts, seeds=seeds, values=mats[b])
        for b in baselines
    }
    got_digest = W.readings_digest(readings)
    if got_digest != want_digest:
        raise _refuse(f"reconstructed readings_sha256 {got_digest[:12]}... does not match sidecar {want_digest[:12]}...")
    return readings


__all__ = ["ID_COLUMNS", "MEASURE_COLUMNS", "COLUMNS", "H4CollectRefused", "rows_from_readings", "w42_readings"]

