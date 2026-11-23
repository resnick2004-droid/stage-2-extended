"""H4's collection adapter for W42-R1 (`extended.h4_collect:w42_readings`; W42-R1 V-1 / V-3, H4 section 9).

Pure CSV <-> `extended.wave42.BaselineReading` adapter for H4-C's single collection result (`results/h4_w42_input.csv`)
and its sidecar manifest. Draws no randomness, reads no bars, and never touches the held-out years.

Contract (W42-R1 section 1.1 & H4 section 9):
- `rows_from_readings(readings)` serialises the four paired `BaselineReading`s to deterministic rows
  (`baseline`, `start`, `seed`, followed by every measure key in sorted order), using canonical empty strings for NaN
  and exact `repr(float)` for finite float64 values so `w42_readings` round-trips bit-for-bit; infinite values,
  non-search/non-deciding readings, and ID-column collisions are refused.
- `w42_readings(csv_path, sidecar)` verifies before returning (failing closed with `H4CollectRefused`):
  1. `sidecar["parameters"]` carries every declared `H4_MANIFEST_KEYS` field (excluding top-level `sha256`), with
     `block == "search"` checked FIRST (held-out guard before opening `csv_path`), `reading == "martingale_outcome"`,
     `arm == "off"`, every verdict setting in `wave42.VERDICT` (`denial == 0`, `placement == "off"`,
     `focused_trader == "off"`), `W == 126` (exact `int`, not `bool`), `calendar_sha256` and `readings_sha256` valid
     64-hex digests, `baselines == wave42.BASELINES` in order, `starts` strictly increasing valid ISO calendar dates
     inside the search years, and `seeds` contiguous exact `int`s `0..J-1`;
  2. `csv_path` exists, is read once from disk, hashes to `sidecar["sha256"]`, decodes as UTF-8, and parses cleanly;
  3. Every `(baseline, start, seed)` cell is present exactly once (canonical non-negative integer seed strings, no
     missing, extra, or duplicate rows) and every required measure column (`wave42.REQUIRED`) is present with finite
     float64 values or blank (`""` -> `NaN`; literal `"nan"` / `"inf"` strings refused);
  4. The reconstructed `BaselineReading` dict reproduces `sidecar["parameters"]["readings_sha256"]` via
     `wave42.readings_digest`.
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import io
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from extended import wave42 as W

ID_COLUMNS: tuple[str, ...] = ("baseline", "start", "seed")
MEASURE_COLUMNS: tuple[str, ...] = tuple(sorted(W.REQUIRED))
COLUMNS: tuple[str, ...] = ID_COLUMNS + MEASURE_COLUMNS

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CANONICAL_SEED = re.compile(r"^(?:0|[1-9][0-9]*)$")


class H4CollectRefused(ValueError):
    """H4's collection file or sidecar violates W42-R1's binding contract."""


def _refuse(msg: str) -> H4CollectRefused:
    return H4CollectRefused(f"h4_collect refuses its input: {msg}")


def _is_exact_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _valid_iso_date(d: Any) -> str:
    if not isinstance(d, str) or not _ISO_DATE.fullmatch(d):
        raise _refuse(f"start day must be an ISO YYYY-MM-DD string, got {d!r}")
    try:
        _dt.date.fromisoformat(d)
    except ValueError as exc:
        raise _refuse(f"invalid calendar date {d!r}") from exc
    return d


def _parse_cell(raw: str, col: str, row_idx: int) -> float:
    s = raw.strip()
    if s == "":
        return float("nan")
    try:
        val = float(s)
    except ValueError as exc:
        raise _refuse(f"row {row_idx} column {col!r}: not a finite float or blank ({raw!r})") from exc
    if not math.isfinite(val):
        raise _refuse(f"row {row_idx} column {col!r}: non-finite value refused ({raw!r}); blanks must be empty")
    return val


def rows_from_readings(readings: Mapping[str, W.BaselineReading],
                       extra_keys: Sequence[str] = ()) -> tuple[tuple[str, ...], list[dict[str, Any]]]:
    """Serialise four paired `BaselineReading` objects into deterministic CSV rows for `results/h4_w42_input.csv`."""
    if not isinstance(readings, Mapping):
        raise _refuse("readings must be a mapping")
    if set(readings.keys()) != set(W.BASELINES):
        raise _refuse(f"expected baselines {W.BASELINES}, got {tuple(readings.keys())}")
    for ek in extra_keys:
        if not isinstance(ek, str) or not ek:
            raise _refuse(f"extra_keys entries must be non-empty strings, got {ek!r}")
        if ek in ID_COLUMNS:
            raise _refuse(f"extra_key {ek!r} collides with reserved ID column")

    first = readings[W.BASELINES[0]]
    starts = tuple(_valid_iso_date(d) for d in first.starts)
    if not starts or len(set(starts)) != len(starts) or list(starts) != sorted(starts):
        raise _refuse("starts must be non-empty strictly increasing ISO dates")
    for d in starts:
        if not (W.SEARCH_FIRST <= d <= W.SEARCH_LAST) or d >= W.HELD_OUT_FIRST:
            raise _refuse(f"start day {d!r} lies outside the search years {W.SEARCH_FIRST}..{W.SEARCH_LAST}")
    if not first.seeds or not all(_is_exact_int(c) for c in first.seeds):
        raise _refuse("seeds must be non-empty exact integers")
    seeds = tuple(first.seeds)
    if seeds != tuple(range(len(seeds))):
        raise _refuse("seeds must be contiguous integers 0..J-1")

    keys = tuple(sorted(set(W.REQUIRED) | set(extra_keys)))
    for name in W.BASELINES:
        b = readings[name]
        if b.name != name:
            raise _refuse(f"baseline {name!r} has mismatched name {b.name!r}")
        if b.block != W.BLOCK:
            raise _refuse(f"baseline {name!r} has block {b.block!r}, expected {W.BLOCK!r} (only the search years)")
        if b.reading != W.READING:
            raise _refuse(f"baseline {name!r} has reading {b.reading!r}, expected {W.READING!r}")
        if tuple(b.starts) != starts or not all(_is_exact_int(c) for c in b.seeds) or tuple(b.seeds) != seeds:
            raise _refuse(f"baseline {name!r} is not paired on starts and seeds with {W.BASELINES[0]!r}")
        missing = [k for k in keys if k not in b.values]
        if missing:
            raise _refuse(f"baseline {name!r} is missing required measure keys: {missing}")

    cols = ID_COLUMNS + keys
    rows: list[dict[str, Any]] = []
    for name in W.BASELINES:
        b = readings[name]
        mats: dict[str, np.ndarray] = {}
        for k in keys:
            raw_v = b.values[k]
            if np.iscomplexobj(raw_v):
                raise _refuse(f"baseline {name!r} key {k!r}: complex values refused")
            try:
                mat = np.asarray(raw_v, dtype=np.float64)
            except (TypeError, ValueError) as exc:
                raise _refuse(f"baseline {name!r} key {k!r}: non-numeric values refused") from exc
            if mat.shape != (len(starts), len(seeds)):
                raise _refuse(f"baseline {name!r} key {k!r} has shape {mat.shape}, expected {(len(starts), len(seeds))}")
            if np.isinf(mat).any():
                raise _refuse(f"baseline {name!r} key {k!r}: infinite value refused")
            mats[k] = mat
        for si, start in enumerate(starts):
            for ci, seed in enumerate(seeds):
                rec: dict[str, Any] = {"baseline": name, "start": start, "seed": seed}
                for k in keys:
                    v = float(mats[k][si, ci])
                    rec[k] = "" if math.isnan(v) else repr(v)
                rows.append(rec)
    return cols, rows


def _validate_sidecar_parameters(sidecar: Mapping[str, Any]) -> tuple[
    str, str, tuple[str, ...], tuple[str, ...], tuple[int, ...], str, str
]:
    if not isinstance(sidecar, Mapping):
        raise _refuse("sidecar manifest must be a mapping")
    params = sidecar.get("parameters")
    if not isinstance(params, Mapping):
        raise _refuse("sidecar missing parameters mapping")

    # Held-out / block guard FIRST, before any file read
    block = params.get("block")
    if block != W.BLOCK:
        raise _refuse(f"only the search years ({W.BLOCK!r}) are accepted, got block={block!r}")

    need_params = [k for k in W.H4_MANIFEST_KEYS if k != "sha256"]
    missing_params = [k for k in need_params if k not in params]
    if missing_params:
        raise _refuse(f"sidecar parameters missing required keys: {missing_params}")

    reading = params["reading"]
    if reading != W.READING:
        raise _refuse(f"sidecar reading must be {W.READING!r}, got {reading!r}")
    arm = params["arm"]
    if arm != W.ARM:
        raise _refuse(f"sidecar arm must be {W.ARM!r}, got {arm!r}")
    for vk, vwant in W.VERDICT.items():
        vgot = params[vk]
        if isinstance(vwant, (int, float)) and not isinstance(vwant, bool):
            if isinstance(vgot, bool) or not isinstance(vgot, (int, float)) or not math.isfinite(float(vgot)) or float(vgot) != float(vwant):
                raise _refuse(f"sidecar verdict setting {vk!r} must be {vwant!r}, got {vgot!r}")
        elif vgot != vwant:
            raise _refuse(f"sidecar verdict setting {vk!r} must be {vwant!r}, got {vgot!r}")
    w_val = params["W"]
    if not _is_exact_int(w_val) or w_val != W.W:
        raise _refuse(f"sidecar W must be exact int {W.W}, got {w_val!r}")

    want_sha = sidecar.get("sha256")
    if not isinstance(want_sha, str) or not _HEX64.fullmatch(want_sha):
        raise _refuse("sidecar missing valid top-level 64-hex sha256")
    cal_sha = params["calendar_sha256"]
    if not isinstance(cal_sha, str) or not _HEX64.fullmatch(cal_sha):
        raise _refuse("sidecar calendar_sha256 missing or malformed")
    want_digest = params["readings_sha256"]
    if not isinstance(want_digest, str) or not _HEX64.fullmatch(want_digest):
        raise _refuse("sidecar readings_sha256 missing or malformed")

    baselines_raw = params["baselines"]
    if not isinstance(baselines_raw, (list, tuple)) or tuple(baselines_raw) != W.BASELINES:
        raise _refuse(f"sidecar baselines must be {W.BASELINES} in order, got {baselines_raw!r}")
    baselines = tuple(baselines_raw)

    starts_raw = params["starts"]
    seeds_raw = params["seeds"]
    if not isinstance(starts_raw, (list, tuple)) or not starts_raw:
        raise _refuse("sidecar starts must be a non-empty list")
    if not isinstance(seeds_raw, (list, tuple)) or not seeds_raw:
        raise _refuse("sidecar seeds must be a non-empty list")
    starts = tuple(_valid_iso_date(d) for d in starts_raw)
    if len(set(starts)) != len(starts) or list(starts) != sorted(starts):
        raise _refuse("sidecar starts must be strictly increasing ISO dates")
    for d in starts:
        if not (W.SEARCH_FIRST <= d <= W.SEARCH_LAST) or d >= W.HELD_OUT_FIRST:
            raise _refuse(f"start day {d!r} lies outside the search years {W.SEARCH_FIRST}..{W.SEARCH_LAST}")
    expected_cal_sha = W.calendar_digest(starts)
    if cal_sha != expected_cal_sha:
        raise _refuse(f"sidecar calendar_sha256 {cal_sha[:12]}... does not match starts digest {expected_cal_sha[:12]}...")

    if not all(_is_exact_int(c) for c in seeds_raw):
        raise _refuse("sidecar seeds must be exact integers")
    seeds = tuple(seeds_raw)
    if seeds != tuple(range(len(seeds))):
        raise _refuse("sidecar seeds must be contiguous integers 0..J-1")

    return want_sha, want_digest, baselines, starts, seeds, block, reading


def w42_readings(csv_path: Path | str, sidecar: Mapping[str, Any]) -> dict[str, W.BaselineReading]:
    """Read H4-C's `results/h4_w42_input.csv` and sidecar into `{name: BaselineReading}`, failing closed on any drift."""
    want_sha, want_digest, baselines, starts, seeds, block, reading = _validate_sidecar_parameters(sidecar)

    path = Path(csv_path)
    if not path.is_file():
        raise _refuse(f"collection CSV not found: {path}")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise _refuse(f"cannot read collection CSV {path}: {exc}") from exc
    actual_sha = hashlib.sha256(raw_bytes).hexdigest()
    if actual_sha != want_sha:
        raise _refuse(f"CSV sha256 {actual_sha[:12]}... does not match sidecar {want_sha[:12]}...")

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _refuse(f"collection CSV is not valid UTF-8: {exc}") from exc

    start_idx = {d: i for i, d in enumerate(starts)}
    seed_idx = {c: i for i, c in enumerate(seeds)}
    n_s, n_c = len(starts), len(seeds)

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
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
            seed_str = row["seed"].strip()
            if not _CANONICAL_SEED.fullmatch(seed_str):
                raise _refuse(f"row {row_num}: non-canonical seed {row['seed']!r}")
            cval = int(seed_str)
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
    except csv.Error as exc:
        raise _refuse(f"malformed CSV: {exc}") from exc

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
