"""W42-R2's one application (`docs/plans/WAVE42_SETTING_RULE_R2.md` section 6): W42-R1's application, step for step,
with `net_month_12` read beside H4's collection from H4-B's units files, and W42-R2's rule in place of W42-R1's.

    python scripts/run_clean.py --name w42-r2 -- python scripts/wave42_r2_apply.py

It takes no argument. **Every step of W42-R1's application is W42-R1's own function** (`scripts/wave42_apply.py`,
imported, never edited): refused if any Wave 4.2 output exists; H4's collection result and its sidecar read and hashed
from disk; Q-197's search calendar by its pinned sha256; the held-out start counts from the pinned held-out calendar's
dates; the fee through `standard_prices`; the readings through H4's adapter. Then, the two steps W42-R2 adds:

1. **`net_month_12` from H4-B's units files** (`results/h4_units_<baseline>.csv`, the files H4-C collected): each
   file's sha256 must be its sidecar's and the one H4's collection sidecar records under `units_files_sha256`; only
   the deciding rows are read (`block` `search` checked on every row first, `arm` `off`, `reading`
   `martingale_outcome`), one per start day and seed of the collection; and every W42-R1 measure on those rows must
   equal the collection's, value for value (blanks as blanks), so the column is the same run's.
2. **W42-R2's rule** (`extended.wave42_r2.setting_rule`) on the readings with `net_month_12`, its source the four
   units files' sha256; its values written once to `results/w42_r2_values.csv` through `write_result`.

`main` refuses unless W42-R1's freeze holds (W42-R1's own `commit_problem` against its pin) and W42-R2's does (the same
function, over W42-R2's pin file `config/w42_r2_pin.json` and the files W42-R2 adds to the imports).
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import wave42 as R  # noqa: E402  (pure: no engine, no file)
from extended import wave42_r2 as R2  # noqa: E402


def _load_parent():
    """W42-R1's application, imported from its pinned file (a script, not a package)."""
    name = "wave42_apply_parent_of_r2"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "wave42_apply.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod                       # a dataclass looks its module up by name
    spec.loader.exec_module(mod)
    return mod


A = _load_parent()

SCRIPT = R2.APPLY_SCRIPT
RULE_TEXT = "docs/plans/WAVE42_SETTING_RULE_R2.md"
RULE_MODULE = "extended/wave42_r2.py"
PIN_FILE = "config/w42_r2_pin.json"
#: W42-R1's imported files, and the files W42-R2 adds; a run at a descendant of W42-R2's pinned commit is admitted
#: only if its diff from it touches none of them
IMPORTED_FILES = tuple(A.IMPORTED_FILES) + (RULE_MODULE, SCRIPT, RULE_TEXT)
UNITS_NAME = "h4_units_{baseline}.csv"            # H4-B's units files, by H4-C's name for them
UNITS_KEY = "units_files_sha256"                  # where H4-C's sidecar records their sha256
UNIT_ID_COLUMNS = ("baseline", "arm", "reading", "block", "start", "seed")
_CANONICAL_SEED = re.compile(r"(?:0|[1-9][0-9]*)")      # a seed index as H4-C reads it

ApplyRefused = A.ApplyRefused


def _refuse(msg: str) -> A.ApplyRefused:
    return A.ApplyRefused(f"W42-R2's application refuses: {msg}")


def _parse(raw: str, where: str) -> float:
    s = raw.strip()
    if s == "":
        return float("nan")
    try:
        v = float(s)
    except ValueError as e:
        raise _refuse(f"{where}: not a number or blank ({raw!r})") from e
    if not math.isfinite(v):
        raise _refuse(f"{where}: a non-finite value ({raw!r}); a blank is empty")
    return v


def units_net12(path: Path, baseline: str, reading: R.BaselineReading) -> np.ndarray:
    """`net_month_12` of one baseline's deciding rows of its units file, as a start days x seeds matrix, after the
    held-out guard on every row and the parity of every W42-R1 measure with the collection's reading."""
    starts = [str(d) for d in reading.starts]
    seeds = [int(c) for c in reading.seeds]
    si = {d: i for i, d in enumerate(starts)}
    ci = {c: i for i, c in enumerate(seeds)}
    keys = (R2.NET12_KEY, *sorted(R.REQUIRED))
    mats = {k: np.full((len(starts), len(seeds)), np.nan) for k in keys}
    seen: set[tuple[int, int]] = set()
    with path.open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        missing = sorted((set(UNIT_ID_COLUMNS) | set(keys)) - set(rd.fieldnames or ()))
        if missing:
            raise _refuse(f"{path.name} lacks the columns {missing}")
        for n, row in enumerate(rd, start=2):
            if row["block"].strip() != R.BLOCK:                      # the held-out guard first, on every row
                raise _refuse(f"{path.name} row {n}: block {row['block']!r}; only the search years are read")
            d = row["start"].strip()
            if not (R.SEARCH_FIRST <= d <= R.SEARCH_LAST) or d >= R.HELD_OUT_FIRST:
                raise _refuse(f"{path.name} row {n}: start day {d!r} outside the search years")
            if row["arm"].strip() != R.ARM or row["reading"].strip() != R.READING:
                continue
            if row["baseline"].strip() != baseline:
                raise _refuse(f"{path.name} row {n}: baseline {row['baseline']!r}, not {baseline!r}")
            s = row["seed"].strip()
            if d not in si or not _CANONICAL_SEED.fullmatch(s) or int(s) not in ci:
                raise _refuse(f"{path.name} row {n}: start {d!r} or seed {s!r} is not the collection's")
            cell = (si[d], ci[int(s)])
            if cell in seen:
                raise _refuse(f"{path.name} row {n}: a repeated start day and seed {(d, s)}")
            seen.add(cell)
            for k in keys:
                mats[k][cell] = _parse(row[k], f"{path.name} row {n} {k}")
    if len(seen) != len(starts) * len(seeds):
        raise _refuse(f"{path.name}: {len(seen)} deciding rows, not the collection's {len(starts) * len(seeds)}")
    for k in sorted(R.REQUIRED):
        if not np.array_equal(mats[k], np.asarray(reading.values[k], dtype=float), equal_nan=True):
            raise _refuse(f"{path.name}: {k} is not the collection's (another run's units file)")
    return mats[R2.NET12_KEY]


def with_net12(results_dir: Path, man: Mapping[str, Any],
               readings: Mapping[str, R.BaselineReading]) -> tuple[dict[str, R.BaselineReading], dict[str, str]]:
    """The readings with `net_month_12` from the four units files, and those files' sha256 (step 1)."""
    rec = (man.get("parameters") or {}).get(UNITS_KEY)
    if not isinstance(rec, Mapping) or sorted(rec) != sorted(R.BASELINES):
        raise _refuse(f"H4's collection sidecar records no {UNITS_KEY} for each of {R.BASELINES}")
    out, shas = {}, {}
    for b in R.BASELINES:
        p = results_dir / UNITS_NAME.format(baseline=b)
        side = Path(f"{p}{A.MANIFEST_SUFFIX}")
        if not p.is_file() or not side.is_file():
            raise _refuse(f"H4-B's units file {p.name} and its sidecar are both required")
        sha = A.sha256_file(p)
        if json.loads(side.read_text(encoding="utf-8")).get("sha256") != sha:
            raise _refuse(f"{p.name}'s bytes hash to {sha[:12]}..., not its sidecar's")
        if rec[b] != sha:
            raise _refuse(f"{p.name} is not the units file H4's collection read ({UNITS_KEY} differs)")
        r = readings[b]
        x = units_net12(p, b, r)
        out[b] = R.BaselineReading(r.name, r.block, r.reading, r.starts, r.seeds,
                                   {**dict(r.values), R2.NET12_KEY: x})
        shas[b] = sha
    return out, shas


def apply(results_dir: Path | str, sources: A.Sources) -> dict[str, Any]:
    """The whole application, refusing before any write; returns the written values' parameters."""
    results_dir = Path(results_dir)
    out_path = results_dir / R2.OUTPUT_NAME
    if out_path.exists() or Path(f"{out_path}{A.MANIFEST_SUFFIX}").exists():
        raise _refuse(f"{out_path.name} exists: W42-R2 is applied once (a second application is refused)")
    A.refuse_if_applied(results_dir)                       # any w42_* output, W42-R1's included, refuses
    csv_path, man, file_sha, side_sha, binding = A.read_collection(results_dir)
    dates, cal_digest, cal_file_sha = A.search_calendar(results_dir, sources.calendar_loader)
    n_ho, ho_sha = A.held_out_sessions(results_dir)
    counts = {h: R.complete_starts(n_ho, h) for h in R.HORIZONS}
    fee, fee_source, ledger_sha = sources.fee()
    readings = sources.adapter(csv_path, man)
    readings, units_sha = with_net12(results_dir, man, readings)
    values = R2.setting_rule(readings, h4=R.H4Binding(file_sha, binding), search_calendar=dates, fee_unit=fee,
                             fee_source=fee_source, test_starts=counts,
                             test_starts_source={"file": R.HELD_OUT_CALENDAR, "sha256": ho_sha, "sessions": n_ho},
                             net12_source=units_sha)
    v = values.values
    import pandas as pd

    df = pd.DataFrame({"key": sorted(v),
                       "value_json": [json.dumps(v[k], sort_keys=True, separators=(",", ":"), allow_nan=False)
                                      for k in sorted(v)]})
    params = {"rule_id": R2.RULE_ID, "parent_rule_id": R2.PARENT_RULE_ID, "parent_row": R2.PARENT_ROW,
              "values_sha256": values.digest(), "input_sha256": v["input_sha256"],
              "h4_collection": R.COLLECTION_RESULT, "h4_result_sha256": file_sha, "h4_sidecar_sha256": side_sha,
              "readings_sha256": binding.get("readings_sha256"), "r2_readings_sha256": R.readings_digest(readings),
              "units_files_sha256": units_sha, "h4_starts": len(binding.get("starts", ())),
              "h4_seeds": len(binding.get("seeds", ())), "search_calendar": R.SEARCH_CALENDAR,
              "search_calendar_file_sha256": cal_file_sha, "search_calendar_sha256": cal_digest,
              "held_out_calendar": R.HELD_OUT_CALENDAR, "held_out_calendar_sha256": ho_sha,
              "held_out_sessions": n_ho, "test_starts": {str(h): c for h, c in counts.items()},
              "fee_unit": fee, "fee_source": fee_source, "fee_via": "extended.levers_terms.standard_prices",
              "ledger_sha256": ledger_sha, "power_target": R.POWER_TARGET,
              "parent_pinned_commit": A.pinned_commit(ROOT), "pinned_commit": pinned_commit(ROOT),
              "parent_sha256": {rel: A.sha256_bytes((ROOT / rel).read_bytes().replace(b"\r\n", b"\n"))
                                for rel in R2.PARENT_SHA256},
              "rule_text_sha256": A.sha256_file(ROOT / RULE_TEXT), "rule_module_sha256": A.sha256_file(ROOT / RULE_MODULE),
              "script_sha256": A.sha256_file(ROOT / SCRIPT)}
    sources.writer(df, R2.OUTPUT_NAME, script=SCRIPT, seed=None, require_seed=False, parameters=params,
                   results_dir=results_dir,
                   description="W42-R2's values (W42-R1's, with the floor on the median 12-month net cash), applied "
                               "once to H4's collection and H4-B's units files (docs/plans/WAVE42_SETTING_RULE_R2.md)")
    return params


def _r2_functions() -> dict[str, Any]:
    """W42-R1's application's `pinned_commit` and `commit_problem`, their own code, over W42-R2's pin file and files."""
    return R2.rebind(A, {"PIN_FILE": PIN_FILE, "IMPORTED_FILES": IMPORTED_FILES})


def pinned_commit(repo: Path | str) -> str | None:
    """The commit W42-R2's pinning row names, from `config/w42_r2_pin.json`; None when it is absent."""
    return _r2_functions()["pinned_commit"](repo)


def commit_problem(repo: Path | str, pin: str | None, head: str | None = None) -> str | None:
    """None when `head` is W42-R2's pinned commit or a descendant changing none of `IMPORTED_FILES`; else the reason."""
    return _r2_functions()["commit_problem"](repo, pin, head)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        raise SystemExit("scripts/wave42_r2_apply.py takes no argument: its inputs are declared names in results/")
    from extended import RESULTS_DIR

    for bad in (A.commit_problem(ROOT, A.pinned_commit(ROOT)), commit_problem(ROOT, pinned_commit(ROOT))):
        if bad:
            raise _refuse(bad)
    params = apply(RESULTS_DIR, A.declared_sources())
    print(f"W42-R2 applied: {R2.OUTPUT_NAME}, values sha256 {params['values_sha256']}, "
          f"input sha256 {params['input_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
