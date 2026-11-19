"""Q-171 (E-157, E-211; the lever table's row S1 and section 6): S1's range -- the stop width as a multiple k of the
trailing range -- read on the **search years only** (NQ 2020-01-02 to 2023-12-29, E-208), per session (evening, asia,
london, ny; the overnight windows anchored per date, E-231 (3)), the days voided by the calendar (`extended/day_calendar.py`,
E-232). The definitions, the declared share and the quantile rule are `extended/s1_range.py`'s docstring, fixed before
any run. A lever-range reading, not an outcome: no side, no trade, no win share.

    python scripts/run_clean.py --name q171-s1-range --task Q-171 --hours 1 --mem-gb 1.5 -- python scripts/s1_range.py
    python scripts/s1_range.py --results-dir <a temporary folder>             # anywhere but results/: no clean run

**Heavy** (it reads the search years' full bars): under the run lock, one at a time, one BLAS thread.

**Refusals, before any bar is read** (exit 2): a span reaching past 2023-12-29 (`s1_range.check_span`; 2026-07-17 on
as the confirmation window); `results/` outside a clean checkout (`extended.results.clean_run_problem`); a result file
that exists (never overwritten); Q-121's file (`--q121`, default the main tree's `results/q121_vol_descriptive_a1.csv`:
a licensed-price derivative, git-ignored, **read in place, never copied**, E-179) absent, or not at E-177's sha256, or
not matching its manifest.

**The reads**, through `extended.reader` only, each inside the search years (a choice-block read: not ledgered,
E-019): the bars (`ts`, `day`, `open`, `high`, `low`, `close`), one calendar year a read, under the purpose
`s1_lever_range_search_years` and the row E-211 (which classed the reading: its range read on the search years only);
Stage 2's A1 `days` table (`date`, `day_kind`) for the identity; Stage 2's FOMC and BLS calendars through the vendored
`atlas_walk.params` on A1's configuration (as Q-121 read them); the void calendar's sources (`day_calendar.load_sources`:
the store manifest's search-year entries, Q-40's calendar, H2's flags checked against their sha256). Every returned day
is checked again before anything is computed.

**Identities, each refusing** (exit 4, nothing written; a failure prints the identity, the count and the first
difference's year or date, never a value):

* **q121** -- `ny`'s `trail20_range_pts` by year (its walked sessions with a finite value) equals Q-121's admitted
  `range` rows of 2020 to 2023 (`period_kind` year, `measure` trail20_range_pts): the count exactly, the median, p10
  and p90 within a relative 1e-9 (`s1_range.q121_problems`);
* **a1_days** -- every day's kind equals Stage 2's A1 `days` table, and every A1 date with a bar is a day here.

**Writes** `results/s1_range.csv` (sections `days`, `range_k`, `k_quantile`) with its manifest through
`extended.results` (no seed: nothing is drawn; variant count 1); the manifest's parameters carry the caps, the declared
share and every rule the loader checks. Prints the identity lines, the row counts, the timing and the peak working set
-- no k, no range, no share.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import pandas as pd  # noqa: E402

from extended import day_calendar as DC  # noqa: E402
from extended import lever_space as LS  # noqa: E402
from extended import reader  # noqa: E402
from extended import s1_range as S  # noqa: E402
from extended import vol_descriptive as V  # noqa: E402
from extended.lock_guard import main_root  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402

TASK = S.TASK
RESULT = S.RESULT
SCRIPT = S.SCRIPT
BAR_COLUMNS = ["ts", "day", "open", "high", "low", "close"]
DAYS_FAMILY, DAYS_TABLE = "A1", "days"
DATA_FILES = ("data/bars/NQ/bars.parquet", "data/atlas/A1/days.parquet")
#: Q-121's file as E-177 recorded it (git-ignored, local; read in place)
Q121_NAME = "q121_vol_descriptive_a1.csv"
Q121_SHA256 = "f1cbb7b88f412fa98c5c8e5fb983e6d70242a9a65b90a9cf6d296064d7a34e26"
RUN_COMMAND = (f"python scripts/run_clean.py --name q171-s1-range --task {TASK} --hours 1 --mem-gb 1.5 -- "
               f"python {SCRIPT}")


def refused(msg: str) -> str:
    return msg if msg.startswith("REFUSED") else f"REFUSED ({TASK}): {msg}"


def default_q121() -> Path | None:
    """Q-121's file in the main tree (this tree's own `results/` first, if it holds the file)."""
    own = ROOT / "results" / Q121_NAME
    if own.is_file():
        return own
    main = main_root(ROOT)
    return main / "results" / Q121_NAME if main is not None else None


def q121_rows(path: Path | None) -> tuple[list[dict[str, str]], str]:
    """Q-121's admitted rows (section `range`, by year, `trail20_range_pts`) and the file's sha256, after the pin and
    the manifest; raises `ValueError` with the reason otherwise. Reads the file in place; nothing is copied."""
    if path is None or not Path(path).is_file():
        raise ValueError(f"Q-121's file is not at {path} (pass --q121 <path>; it is git-ignored, E-179)")
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != Q121_SHA256:
        raise ValueError(f"Q-121's file at {path} has sha256 {sha}, not E-177's {Q121_SHA256}")
    side = Path(str(path) + ".manifest.json")
    if not side.is_file() or json.loads(side.read_text(encoding="utf-8")).get("sha256") != sha:
        raise ValueError(f"Q-121's file at {path}: its manifest is absent or records another sha256")
    rows = [r for r in csv.DictReader(raw.decode("utf-8").splitlines())
            if r.get("section") == "range" and r.get("period_kind") == "year" and r.get("measure") == S.Q121_MEASURE
            and r.get("period") in S.Q121_YEARS]
    del raw
    return rows, sha


def release_days() -> tuple[set[int], set[int], int]:
    """(FOMC days, BLS 08:30 ET report days, the cut's slot) as A1's walk read them (`atlas_walk.params`)."""
    from propedge.research import atlas_walk

    q = atlas_walk.params(atlas_walk.config(DAYS_FAMILY))
    return {int(x) for x in q["fomc"]}, {int(x) for x in q["bls"]}, int(q["bls_cut"])


def load_sources() -> DC.Sources:
    return DC.load_sources()


def kind_problems(t: pd.DataFrame, days: pd.DataFrame) -> list[str]:
    """The a1_days identity: each day's kind is A1's on its date; each A1 date with a bar is a day here."""
    a1 = dict(zip(days["date"].astype(str), days["day_kind"].astype(str)))
    mine = dict(zip(t["date"].astype(str), t["day_kind"].astype(str)))
    missing = sorted(d for d in mine if d not in a1)
    differ = sorted(d for d in mine if d in a1 and a1[d] != mine[d])
    absent = sorted(d for d, k in a1.items() if k != "x" and d not in mine)
    out = []
    for what, ds in (("days not in A1's days table", missing), ("days whose kind differs from A1's", differ),
                     ("A1 dates with a bar not read", absent)):
        if ds:
            out.append(f"a1_days: {len(ds)} {what} (first {ds[0]})")
    return out


def year_spans(start: date, end: date) -> list[tuple[date, date]]:
    return [(max(start, date(y, 1, 1)), min(end, date(y, 12, 31))) for y in range(start.year, end.year + 1)]


def data_manifest() -> dict[str, str]:
    """The data manifest's sha256 of the files read (`vendor/DATA_MANIFEST_stage2.sha256`; not re-hashed here)."""
    p = ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"
    out = {}
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[1].strip().lstrip("*") in DATA_FILES:
                out[parts[1].strip().lstrip("*")] = parts[0]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--start", default=S.SEARCH_START.isoformat())
    ap.add_argument("--end", default=S.SEARCH_END.isoformat())
    ap.add_argument("--results-dir", default=None, help="default: results/ (only from a clean checkout)")
    ap.add_argument("--q121", default=None, help=f"Q-121's file, read in place (default: the main tree's {Q121_NAME})")
    a = ap.parse_args(argv)
    try:
        start, end = S.check_span(a.start, a.end)
    except (S.BeyondSearchYears, ValueError) as exc:
        print(refused(str(exc)))
        return 2
    from extended import results as XR

    target = Path(a.results_dir) if a.results_dir else XR.RESULTS_DIR
    if XR.protected(target):
        why = XR.clean_run_problem()
        if why:
            print(refused(f"{target} is written only from a clean checkout -- {why}. {RUN_COMMAND}"))
            return 2
    out_csv = target / f"{RESULT}.csv"
    if out_csv.exists() or XR.manifest_path_for(out_csv).exists():
        print(refused(f"{out_csv} exists; a result file is never overwritten"))
        return 2
    try:
        q_rows, q_sha = q121_rows(Path(a.q121) if a.q121 else default_q121())
    except ValueError as exc:
        print(refused(str(exc)))
        return 2
    caps = LS.stop_caps()
    t0 = time.time()
    src = load_sources()
    fomc, bls, cut = release_days()
    if cut != V.BLS_CUT:
        print(refused(f"A1's BLS cut is slot {cut}, not {V.BLS_CUT}"))
        return 4
    parts = []
    for ys, ye in year_spans(start, end):
        bars = reader.read_bars(ys, ye, purpose=S.PURPOSE, declaration=S.READ_ROW, columns=BAR_COLUMNS,
                                what=f"{TASK}: the search years' bars for S1's trailing-range reading ({ys.year})")
        S.check_days(bars["day"].astype(str).unique())
        parts.append(S.day_table(bars, fomc=fomc, bls=bls, src=src))
        del bars
        print(f"  read {ys} to {ye}: {len(parts[-1])} days; peak working set {working_set_mb(peak=True):.0f} MB",
              flush=True)
    t = S.add_trailing(pd.concat(parts, ignore_index=True))
    t_read = time.time() - t0
    problems = S.q121_problems(t, q_rows)
    print(f"  identity q121: ny's trail20_range_pts by year against {len(q_rows)} admitted Q-121 rows -- "
          f"{'HELD' if not problems else 'FAILED'}", flush=True)
    days = reader.read_walks(DAYS_FAMILY, DAYS_TABLE, start, end, columns=["date", "day_kind"],
                             what=f"{TASK}: A1's day kinds for the a1_days identity")
    kp = kind_problems(t, days)
    print(f"  identity a1_days: {len(t)} days against A1's days table -- {'HELD' if not kp else 'FAILED'}",
          flush=True)
    problems += kp
    if problems:
        for p in problems:
            print(f"  {p}")
        print(refused("an identity failed; nothing is written"))
        return 4
    frame = S.summarise(t, caps)
    bad = S.output_problems(frame)
    if bad:
        print(refused(f"the frame is not this reading's: {bad[:3]}"))
        return 5
    params = S.manifest_parameters(caps, identities={"q121": "HELD", "a1_days": "HELD"}, span=(start, end))
    params.update({"q121_sha256": q_sha, "q121_rows": len(q_rows), "a1_days_compared": len(t),
                   "bls_cut_slot": cut, "data_manifest": data_manifest(),
                   "calendar": {"flags_sha256": src.flags_sha256, "days": len(src.days)}})
    paths = XR.write_result(frame, RESULT, script=SCRIPT, seed=None, require_seed=False, parameters=params,
                            results_dir=target, exploratory=False, variant_count=1,
                            description=("Q-171 (E-157, E-211): S1's range -- the stop as a multiple k of the trailing "
                                         "range -- per session on the search years 2020-01-02 to 2023-12-29 only, the "
                                         "caps (lever_space.stop_caps) translated into k; counts, shares and k only"))
    counts = frame["section"].value_counts()
    print("  rows: " + ", ".join(f"{s} {int(counts.get(s, 0))}" for s in S.SECTIONS))
    print(f"  wrote {paths[0].name}; read {t_read:.0f} s, total {time.time() - t0:.0f} s, peak working set "
          f"{working_set_mb(peak=True):.0f} MB", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
