"""H4-C: collect the four baselines' search-year units files into W42-R1's single input `results/h4_w42_input.csv`
(`prereg/H4_rebaseline.md` sections 9, 11, 16, 17; W42-R1 V-1 / V-3; E-287).

    python scripts/run_clean.py --name h4-collect -- python scripts/h4_collect.py

Refuses before writing unless:
- All four `results/h4_units_<baseline>.csv` files (`naive_coin`, `p14`, `p15`, `p16`) and their sidecar manifests
  exist and match their recorded sha256s;
- Every baseline is on the deciding `off` reading (`block == "search"`, `reading == "martingale_outcome"`,
  `arm == "off"`), paired on exact Q-197 pinned search calendar starts (`results/search_calendar.csv`) and contiguous
  seed indices `0..J-1` (`J == 128` in production), with zero strict `+5 min` overlaps and zero blanks on `E_h` for
  all 15 `wave42.REQUIRED` measures;
- Clean run (`S2X_CLEAN_RUN`), output absent, H4 pin & W42-R1 freeze intact.

Writes `results/h4_w42_input.csv` + sidecar manifest via `extended.results.write_result` carrying every field of
`wave42.H4_MANIFEST_KEYS` under `parameters` (and top-level `sha256`), plus the four units files' sha256s and
uncapped `sessions_left` beside (zero held-out counts, zero raw H4 seed literals), then immediately round-trip
verifies the written file through `extended.h4_collect.w42_readings(csv_path, sidecar)`.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import h4_audit as HA  # noqa: E402
from extended import h4_collect as HC  # noqa: E402
from extended import search_calendar as SCAL  # noqa: E402
from extended import wave42 as W  # noqa: E402

SCRIPT = "scripts/h4_collect.py"
OUTPUT_NAME = "h4_w42_input"


class H4CollectScriptRefused(RuntimeError):
    """H4-C collection refused its inputs or failed round-trip verification."""


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_units_file(csv_path: Path) -> tuple[str, dict[str, Any]]:
    """Verify `h4_units_<baseline>.csv` exists and matches its sidecar manifest sha256."""
    if not csv_path.is_file():
        raise H4CollectScriptRefused(f"missing units file: {csv_path}")
    side = Path(f"{csv_path}.manifest.json")
    if not side.is_file():
        raise H4CollectScriptRefused(f"missing units sidecar manifest: {side}")
    file_sha = _sha256_file(csv_path)
    man = json.loads(side.read_text(encoding="utf-8"))
    if man.get("sha256") != file_sha:
        raise H4CollectScriptRefused(
            f"{csv_path.name}: sha256 {file_sha[:12]}... != manifest {str(man.get('sha256'))[:12]}..."
        )
    return file_sha, man


def load_baseline_units_reading(
    csv_path: Path,
    baseline: str,
    expected_starts: Sequence[str],
    *,
    expected_j: int | None = None,
) -> tuple[W.BaselineReading, str, tuple[int, ...]]:
    """Load one baseline's deciding `off` reading from `h4_units_<baseline>.csv` into a `wave42.BaselineReading`.

    Refuses any held-out date, non-zero `strict_overlaps`, duplicate/missing `(start, seed)` cell, or non-finite value
    on `E_h` for any `wave42.REQUIRED` measure.
    """
    file_sha, _ = _verify_units_file(csv_path)
    starts = tuple(str(d) for d in expected_starts)
    start_idx = {d: i for i, d in enumerate(starts)}
    n_s = len(starts)
    req_keys = tuple(sorted(W.REQUIRED.keys()))

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames is None:
            raise H4CollectScriptRefused(f"{csv_path.name}: empty CSV")
        fields = set(rd.fieldnames)
        need_cols = {"baseline", "arm", "reading", "block", "start", "seed", "strict_overlaps", *req_keys}
        missing = sorted(need_cols - fields)
        if missing:
            raise H4CollectScriptRefused(f"{csv_path.name}: missing required columns {missing}")

        rows_off: list[dict[str, str]] = []
        for rnum, row in enumerate(rd, start=2):
            blk = row["block"].strip()
            if blk != W.BLOCK:
                raise H4CollectScriptRefused(f"{csv_path.name} row {rnum}: non-search block {blk!r} refused")
            sday = row["start"].strip()
            if sday >= W.HELD_OUT_FIRST or not (W.SEARCH_FIRST <= sday <= W.SEARCH_LAST):
                raise H4CollectScriptRefused(f"{csv_path.name} row {rnum}: start {sday!r} outside search years")
            ov = int(float(row["strict_overlaps"]))
            if ov > 0:
                raise H4CollectScriptRefused(
                    f"{csv_path.name} row {rnum}: strict_overlaps={ov} > 0 on {row['arm']}/{sday}/seed={row['seed']}"
                )
            if row["arm"].strip() == W.ARM and row["reading"].strip() == W.READING:
                b_got = row["baseline"].strip()
                if b_got != baseline:
                    raise H4CollectScriptRefused(f"{csv_path.name} row {rnum}: baseline {b_got!r} != {baseline!r}")
                rows_off.append(row)

    if not rows_off:
        raise H4CollectScriptRefused(f"{csv_path.name}: no deciding off rows found")

    seed_set = sorted({int(r["seed"].strip()) for r in rows_off})
    n_c = len(seed_set)
    if seed_set != list(range(n_c)):
        raise H4CollectScriptRefused(f"{csv_path.name}: seeds must be contiguous 0..J-1, got {seed_set[:10]}...")
    if expected_j is not None and n_c != int(expected_j):
        raise H4CollectScriptRefused(f"{csv_path.name}: got J={n_c} seeds, expected J={expected_j}")

    mats = {k: np.full((n_s, n_c), np.nan, dtype=np.float64) for k in req_keys}
    seen: set[tuple[int, int]] = set()
    for r in rows_off:
        sday = r["start"].strip()
        if sday not in start_idx:
            raise H4CollectScriptRefused(f"{csv_path.name}: start {sday!r} not in pinned search calendar")
        si = start_idx[sday]
        ci = int(r["seed"].strip())
        if (si, ci) in seen:
            raise H4CollectScriptRefused(f"{csv_path.name}: duplicate (start={sday}, seed={ci})")
        seen.add((si, ci))
        for k in req_keys:
            raw = r[k].strip()
            if raw == "":
                mats[k][si, ci] = float("nan")
            else:
                v = float(raw)
                if not math.isfinite(v):
                    raise H4CollectScriptRefused(f"{csv_path.name}: non-finite {k}={raw!r} at {sday}/seed={ci}")
                mats[k][si, ci] = v

    expected_cells = n_s * n_c
    if len(seen) != expected_cells:
        raise H4CollectScriptRefused(
            f"{csv_path.name}: incomplete off grid ({len(seen)} cells, expected {expected_cells})"
        )

    # Check MEASURES 1.3 never-blank rule on E_h
    sl = np.asarray([n_s - i for i in range(n_s)], dtype=int)
    for k, (h_req, lo, hi) in W.REQUIRED.items():
        mask = sl >= h_req
        vals_eh = mats[k][mask]
        if not np.isfinite(vals_eh).all():
            raise H4CollectScriptRefused(f"{csv_path.name}: blank/non-finite value in {k} on E_{h_req}")
        if (vals_eh < lo - 1e-12).any() or (vals_eh > hi + 1e-12).any():
            raise H4CollectScriptRefused(f"{csv_path.name}: {k} outside [{lo}, {hi}] on E_{h_req}")

    reading = W.BaselineReading(
        name=baseline,
        block=W.BLOCK,
        reading=W.READING,
        starts=starts,
        seeds=tuple(seed_set),
        values=mats,
    )
    return reading, file_sha, tuple(seed_set)


def collect_from_units(
    results_dir: Path | str,
    *,
    calendar_dates: Sequence[str] | None = None,
    calendar_path: Path | str | None = None,
    expected_j: int | None = HA.H4_J,
    writer: Callable[..., Any] | None = None,
    preconditions: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble `results/h4_w42_input.csv` + sidecar manifest from the four `h4_units_<baseline>.csv` files,
    then round-trip verify through `extended.h4_collect.w42_readings`."""
    rdir = Path(results_dir)
    out_csv = rdir / f"{OUTPUT_NAME}.csv"
    out_side = Path(f"{out_csv}.manifest.json")
    if out_csv.exists() or out_side.exists():
        raise H4CollectScriptRefused(f"output already exists: {out_csv} (refusing to overwrite)")

    if calendar_dates is None:
        cal = SCAL.load_search_calendar(calendar_path if calendar_path is not None else rdir / W.SEARCH_CALENDAR)
        if calendar_path is None and cal.file_sha256 != W.SEARCH_CALENDAR_SHA256:
            raise H4CollectScriptRefused(
                f"search_calendar.csv sha256 {cal.file_sha256[:12]}... != pinned {W.SEARCH_CALENDAR_SHA256[:12]}..."
            )
        starts = tuple(str(d) for d in cal.dates)
    else:
        starts = tuple(str(d) for d in calendar_dates)

    if not starts or starts != tuple(sorted(set(starts))):
        raise H4CollectScriptRefused("search calendar starts must be non-empty strictly increasing")
    if starts[0] < W.SEARCH_FIRST or starts[-1] > W.SEARCH_LAST:
        raise H4CollectScriptRefused(f"starts span {starts[0]}..{starts[-1]} outside {W.SEARCH_FIRST}..{W.SEARCH_LAST}")

    readings: dict[str, W.BaselineReading] = {}
    units_sha: dict[str, str] = {}
    seeds_ref: tuple[int, ...] | None = None

    for bname in W.BASELINES:
        upath = rdir / f"h4_units_{bname}.csv"
        rd_b, sha_b, seeds_b = load_baseline_units_reading(upath, bname, starts, expected_j=expected_j)
        if seeds_ref is None:
            seeds_ref = seeds_b
        elif seeds_b != seeds_ref:
            raise H4CollectScriptRefused(f"{bname}: seeds {len(seeds_b)} not paired with {W.BASELINES[0]} {len(seeds_ref)}")
        readings[bname] = rd_b
        units_sha[bname] = sha_b

    assert seeds_ref is not None
    cols, rows = HC.rows_from_readings(readings)
    df = pd.DataFrame(rows, columns=list(cols))
    cal_sha = W.calendar_digest(starts)
    rd_sha = W.readings_digest(readings)
    sessions_left = [len(starts) - i for i in range(len(starts))]

    params: dict[str, Any] = {
        "block": W.BLOCK,
        "reading": W.READING,
        "arm": W.ARM,
        "denial": float(W.VERDICT["denial"]),
        "placement": str(W.VERDICT["placement"]),
        "focused_trader": str(W.VERDICT["focused_trader"]),
        "W": int(W.W),
        "baselines": list(W.BASELINES),
        "starts": list(starts),
        "seeds": list(seeds_ref),
        "calendar_sha256": cal_sha,
        "readings_sha256": rd_sha,
        "units_files_sha256": units_sha,
        "sessions_left": sessions_left,
        "seed_roles": ["h4b_coins", "h4s_schedule_side", "h4_sample"],
        "h4_decl_sha256": HA.H4_DECL_LF_SHA256,
        "h4_reg_constants_sha256": HA.H4_REG_CONSTANTS_SHA256,
    }
    if preconditions:
        params["preconditions"] = dict(preconditions)

    if writer is None:
        from extended import results as RES

        writer = RES.write_result

    written_csv, written_man = writer(
        df,
        OUTPUT_NAME,
        script=SCRIPT,
        seed=None,
        require_seed=False,
        exploratory=False,
        prereg_id="H4",
        results_dir=rdir,
        parameters=params,
        description=(
            "H4-C single collection result for W42-R1 (E-287): paired search-year deciding martingale_outcome off "
            "readings for naive_coin, p14, p15, and p16 over J=128 coin seeds."
        ),
    )

    # Mandatory round-trip verification via the frozen pre-pin adapter `extended/h4_collect.py::w42_readings`
    sidecar = json.loads(Path(written_man).read_text(encoding="utf-8"))
    roundtrip = HC.w42_readings(Path(written_csv), sidecar)
    if W.readings_digest(roundtrip) != rd_sha:
        raise H4CollectScriptRefused("round-trip w42_readings digest mismatch")

    return {
        "csv_path": str(written_csv),
        "manifest_path": str(written_man),
        "sha256": sidecar["sha256"],
        "readings_sha256": rd_sha,
        "calendar_sha256": cal_sha,
        "rows": len(df),
        "starts": len(starts),
        "seeds": len(seeds_ref),
        "units_files_sha256": units_sha,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results-dir", type=Path, default=None, help="override results directory (default: repo results/)")
    args = ap.parse_args(argv)

    from extended import RESULTS_DIR

    rdir = Path(args.results_dir) if args.results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(ROOT, require_clean=True, require_lock=False, require_disk=False)
    info = collect_from_units(rdir, expected_j=HA.H4_J, preconditions=pre)
    print(
        f"H4-C collected: {Path(info['csv_path']).name} ({info['rows']} rows, {info['starts']} starts x "
        f"{info['seeds']} seeds), sha256={info['sha256']}, readings_sha256={info['readings_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
