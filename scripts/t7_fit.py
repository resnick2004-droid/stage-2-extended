"""T7 (the lever table's row T7 and section 6; E-208, E-221 O-1): the admission forecast -- F-R's HAR form of the chance
that a mark's bracket reaches the flatten open -- fitted on the **search years only** (NQ 2020-01-02 to 2023-12-29),
the days voided by the calendar (`extended/day_calendar.py`, E-232), on purged and embargoed yearly folds, with its
calibration out of fold. The definitions are `extended/t7_forecast.py`'s docstring, fixed before any run. A forecast of
resolution, side-free: no side's P&L, no win share is read.

    python scripts/run_clean.py --name t7-forecast --task T7 --hours 1 --mem-gb 2 -- python scripts/t7_fit.py
    python scripts/t7_fit.py --results-dir <a temporary folder>             # anywhere but results/: no clean run

**Heavy** (it reads the search years' full bars): under the run lock, one at a time, one BLAS thread.

**Refusals, before any bar is read** (exit 2): a span reaching past 2023-12-29 (`t7_forecast.check_span`; 2026-07-17
on as the confirmation window); `results/` outside a clean checkout (`extended.results.clean_run_problem`); a result
file that exists (never overwritten); D-212's line not readable from Stage 2's config (`t7_forecast.admission_line`).

**The reads**, through `extended.reader` only, each inside the search years (a choice-block read: not ledgered,
E-019): the bars (`ts`, `day`, `contract`, `open`, `high`, `low`, `close`, `volume`), one calendar year a read, under the
purpose `t7_admission_forecast_fit_search_years` and the row E-221 (O-1: every model built, tuned and chosen on the
search years, any number of internal time splits); Stage 2's A1 `days` table (`date`, `day_kind`), the frame's walked
kinds; the void calendar's sources (`day_calendar.load_sources`). Every returned day is checked again before anything
is computed.

**Identities, each refusing** (exit 4, nothing written; a failure prints the identity, the count and the first
differing date, never a value):

* **a1_days** -- every day with bars is in Stage 2's A1 `days` table, and every A1 date of a kind other than `x` has
  bars here;
* **rv_tod** -- on each year's bars (every day of the read, no void), the forecast's x3 at the `day` band's marks
  equals 2 x `extended.features`' `rv_tod` at the alert m - 5: the same missing cells, the values within a relative
  1e-12.

**Writes** `results/t7_forecast.csv` with its manifest through `extended.results` (no seed: nothing is drawn; variant
count 1): every fold's and the final fit's coefficients and calibration, the counts, and the out-of-fold calibration.
Nothing in it inverts to a price range in points (coefficients on log ratios, probabilities, shares, losses, counts).
The manifest's description and `notes` name the out-of-fold rows as "diagnostics, not a forward test" and carry
`t7_forecast.LABELS`; its parameters carry `data_manifest`, the data manifest's sha256 of the bars, the bar store's
manifest and A1's day table (the audit's C3, C4, C7). `--name` writes under another name (a re-run never overwrites;
the name must start `t7_forecast`); the CSV's bytes do not depend on the manifest.
Prints the identity lines, the row counts, the timing and the peak working set -- no coefficient, no share.
"""
from __future__ import annotations

import argparse
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

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import day_calendar as DC  # noqa: E402
from extended import features as FL  # noqa: E402
from extended import reader  # noqa: E402
from extended import t7_forecast as T  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402

TASK = T.TASK
RESULT = T.RESULT
SCRIPT = T.SCRIPT
BAR_COLUMNS = ["ts", "day", "contract", "open", "high", "low", "close", "volume"]
DAYS_FAMILY, DAYS_TABLE = "A1", "days"
RV_TOL = 1e-12
#: the inputs whose sha256 the manifest records (`vendor/DATA_MANIFEST_stage2.sha256`; the audit's C4, as S1's and
#: Q-121's manifests do): the bars, the bar store's manifest (the void calendar's source) and A1's day table
DATA_FILES = ("data/bars/NQ/bars.parquet", "data/bars/NQ/manifest.json", "data/atlas/A1/days.parquet")
DESCRIPTION = ("T7 (E-208, E-221 O-1): the admission forecast -- F-R's HAR form of the chance a mark's bracket reaches "
               "the flatten open -- fitted on the search years 2020-01-02 to 2023-12-29 only, purged and embargoed "
               "yearly folds; each fold's and the final fit's coefficients and calibration, the counts, and "
               "out-of-fold diagnostics (sections oof, reliability, bracket and the per-fold rows): diagnostics, not a "
               "forward test")
RUN_COMMAND = (f"python scripts/run_clean.py --name t7-forecast --task {TASK} --hours 1 --mem-gb 2 -- "
               f"python {SCRIPT}")


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


def manifest_notes() -> dict[str, object]:
    """The manifest's notes (the audit's C3, C7): which rows are diagnostics; the labels every consumer carries."""
    return {"diagnostics": T.DIAGNOSTICS, "diagnostics_label": "diagnostics, not a forward test",
            "labels": list(T.LABELS)}


def refused(msg: str) -> str:
    return msg if msg.startswith("REFUSED") else f"REFUSED ({TASK}): {msg}"


def load_sources() -> DC.Sources:
    return DC.load_sources()


def year_spans(start: date, end: date) -> list[tuple[date, date]]:
    return [(max(start, date(y, 1, 1)), min(end, date(y, 12, 31))) for y in range(start.year, end.year + 1)]


def day_voids(src: DC.Sources, days: list[date]) -> dict[str, list[bool]]:
    """Per band: whether the calendar voids each day under the band's `VOID_RULE`."""
    out: dict[str, list[bool]] = {b: [] for b in T.BANDS}
    cache: dict[tuple[bool, bool], list[bool]] = {}
    for b in T.BANDS:
        rule = T.VOID_RULE[b]
        if rule not in cache:
            cache[rule] = [bool(DC.day_flags(src, "NQ", d, reads_overnight=rule[0], reads_0829=rule[1]).void)
                           for d in days]
        out[b] = cache[rule]
    return out


def rv_problems(bars: pd.DataFrame, days: list[date], stats: dict, calendars: FL.Calendars) -> list[str]:
    """The rv_tod identity on one read's bars: x3 (frame = every day, no void) at the `day` band's marks against
    2 x the library's rv_tod at m - 5."""
    t = T.feature_table(days, stats)
    marks = [int(m) for m in T.MARKS if m >= T.DAY1_LAST + T.MARK_STEP]
    lib = FL.compute(bars, marks=[m - T.ALERT_LAG for m in marks], calendars=calendars)
    lib = pd.DataFrame({"date": lib["day"].astype(str), "mark": lib["slot"].astype(int) + T.ALERT_LAG,
                        "rv_tod": lib["rv_tod"].to_numpy(float)})
    key = ["date", "mark"]
    mine = t[t["mark"].isin(marks)][key + ["x3"]]
    got = mine.merge(lib[key + ["rv_tod"]], on=key, how="outer", indicator=True)
    out = []
    if (got["_merge"] != "both").any():
        out.append(f"rv_tod: {(got['_merge'] != 'both').sum()} (day, mark) cells on one side only")
        got = got[got["_merge"] == "both"]
    a, b = got["x3"].to_numpy(float), 2.0 * got["rv_tod"].to_numpy(float)
    nan_diff = np.isnan(a) != np.isnan(b)
    both = ~np.isnan(a) & ~np.isnan(b)
    off = both & ~np.isclose(a, b, rtol=RV_TOL, atol=0.0)
    if nan_diff.any() or off.any():
        bad = got.loc[nan_diff | off, "date"]
        out.append(f"rv_tod: {int(nan_diff.sum())} cells missing on one side, {int(off.sum())} differ (first "
                   f"{bad.iloc[0]})")
    if not both.any():
        out.append("rv_tod: no cell compared")
    return out


def kind_problems(days: list[date], a1: pd.DataFrame) -> list[str]:
    """The a1_days identity: every day with bars is in A1's days table; every A1 date with a bar is a day here."""
    kinds = dict(zip(a1["date"].astype(str), a1["day_kind"].astype(str)))
    mine = {d.isoformat() for d in days}
    missing = sorted(d for d in mine if d not in kinds)
    absent = sorted(d for d, k in kinds.items() if k != "x" and d not in mine)
    out = []
    for what, ds in (("days not in A1's days table", missing), ("A1 dates with a bar not read", absent)):
        if ds:
            out.append(f"a1_days: {len(ds)} {what} (first {ds[0]})")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--start", default=T.SEARCH_START.isoformat())
    ap.add_argument("--end", default=T.SEARCH_END.isoformat())
    ap.add_argument("--results-dir", default=None, help="default: results/ (only from a clean checkout)")
    ap.add_argument("--name", default=RESULT, help=f"the result file's name (default {RESULT}); a re-run takes a new "
                    "name, never an overwrite")
    a = ap.parse_args(argv)
    try:
        start, end = T.check_span(a.start, a.end)
    except (T.BeyondSearchYears, ValueError) as exc:
        print(refused(str(exc)))
        return 2
    from extended import results as XR

    target = Path(a.results_dir) if a.results_dir else XR.RESULTS_DIR
    if XR.protected(target):
        why = XR.clean_run_problem()
        if why:
            print(refused(f"{target} is written only from a clean checkout -- {why}. {RUN_COMMAND}"))
            return 2
    name = a.name
    if not name.replace("_", "").isalnum() or name != name.lower() or not name.startswith(RESULT):
        print(refused(f"--name {name!r}: a lower-case name starting {RESULT!r} (letters, digits, underscores)"))
        return 2
    out_csv = target / f"{name}.csv"
    if out_csv.exists() or XR.manifest_path_for(out_csv).exists():
        print(refused(f"{out_csv} exists; a result file is never overwritten"))
        return 2
    try:
        q, q_source = T.admission_line()
    except T.ForecastRefused as exc:
        print(refused(str(exc)))
        return 2
    t0 = time.time()
    src = load_sources()
    calendars = FL.load_calendars()
    all_days: list[date] = []
    parts: dict[str, list[np.ndarray]] = {}
    problems: list[str] = []
    for ys, ye in year_spans(start, end):
        bars = reader.read_bars(ys, ye, purpose=T.PURPOSE, declaration=T.READ_ROW, columns=BAR_COLUMNS,
                                what=f"{TASK}: the search years' bars for T7's admission forecast ({ys.year})")
        T.check_days(bars["day"].astype(str).unique())
        days, O, H, L, C = T.day_grid(bars)
        stats = T.window_stats(O, H, L, C)
        del O, H, L, C
        problems += [f"{ys.year} {p}" for p in rv_problems(bars, days, stats, calendars)]
        del bars
        all_days += days
        for k, v in stats.items():
            parts.setdefault(k, []).append(v)
        print(f"  read {ys} to {ye}: {len(days)} days; peak working set {working_set_mb(peak=True):.0f} MB",
              flush=True)
    print(f"  identity rv_tod: x3 against 2 x rv_tod at the day band's marks, {len(parts.get('iv', []))} reads -- "
          f"{'HELD' if not problems else 'FAILED'}", flush=True)
    stats = {k: np.concatenate(v) for k, v in parts.items()}
    a1 = reader.read_walks(DAYS_FAMILY, DAYS_TABLE, start, end, columns=["date", "day_kind"],
                           what=f"{TASK}: A1's day kinds, the frame's walked sessions")
    kp = kind_problems(all_days, a1)
    print(f"  identity a1_days: {len(all_days)} days against A1's days table -- {'HELD' if not kp else 'FAILED'}",
          flush=True)
    problems += kp
    if problems:
        for p in problems:
            print(f"  {p}")
        print(refused("an identity failed; nothing is written"))
        return 4
    kinds = {date.fromisoformat(str(d)[:10]): str(k) for d, k in zip(a1["date"], a1["day_kind"])}
    frame_days = [d for d in all_days if kinds.get(d) in T.WALKED_KINDS]
    voids_frame = day_voids(src, frame_days)
    pos = {d: i for i, d in enumerate(frame_days)}
    voids = {b: [bool(v[pos[d]]) if d in pos else True for d in all_days] for b, v in voids_frame.items()}
    t = T.feature_table(all_days, stats, kinds=kinds, voids=voids)
    del stats
    T.check_days(t["date"].unique())
    t_read = time.time() - t0
    try:
        frame, _ = T.run_fit(t, q)
    except T.FitRefused as exc:
        print(refused(f"the fit refused: {exc}"))
        return 5
    bad = T.output_problems(frame)
    if bad:
        print(refused(f"the frame is not this reading's: {bad[:3]}"))
        return 5
    params = T.manifest_parameters(q, q_source, identities={"rv_tod": "HELD", "a1_days": "HELD"}, span=(start, end))
    params.update({"frame_days": len(frame_days), "rows": int(len(t)),
                   "rows_with_forecast": int(t["has_forecast"].sum()),
                   "calendar": {"flags_sha256": src.flags_sha256, "days": len(src.days)},
                   "data_manifest": data_manifest()})
    paths = XR.write_result(frame, name, script=SCRIPT, seed=None, require_seed=False, parameters=params,
                            results_dir=target, exploratory=False, variant_count=1, description=DESCRIPTION,
                            notes=manifest_notes())
    counts = frame["section"].value_counts()
    print("  rows: " + ", ".join(f"{s} {int(counts.get(s, 0))}" for s in T.SECTIONS))
    print(f"  wrote {paths[0].name}; read {t_read:.0f} s, total {time.time() - t0:.0f} s, peak working set "
          f"{working_set_mb(peak=True):.0f} MB", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
