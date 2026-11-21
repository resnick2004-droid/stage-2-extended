"""Q-197: write the pinned search-year session calendar, `results/search_calendar.csv` (`extended/search_calendar.py`
for its columns, guards, identities and loader), through `extended.results.write_result`.

    python scripts/run_clean.py --name q197-cal -- python scripts/search_calendar.py      # the lead's one run
    python scripts/search_calendar.py --out-dir <a temporary folder>                      # a trial; never results/

**Light** (no lock needed, though the lead may take it): it reads no bar -- only the bar store's manifest
(`vendor/stage2/data/bars/NQ/manifest.json`, metadata: `day_list`, `rolls`, `early_end_days`, `day_bounds`),
Q-40's `config/calendar_early_closes.csv`, H2's `results/h2_overnight_flags.csv` (with its sidecar manifest, required)
and the vendored BLS and FOMC calendars (`extended.features.load_calendars`), all through
`extended.day_calendar.load_sources`, which keeps nothing after 2023-12-29. A1's days table is not read. Seconds,
well under 300 MB.

**Order:** the sources (a flags row after 2023-12-29 refuses); the default bar manifest's sha256 against
`vendor/DATA_MANIFEST_stage2.sha256`; the rows (`build_rows`); their form (`check_rows`, the full span); the
identities (I-1) and (I-2) on the rows parsed back from the very text the writer writes; the write, with every input's
sha256, the calendar's digest (W42-R1's form) and the identities' record in the manifest; then the written file
loaded by `load_search_calendar` and compared row for row with what was built.

The last line printed is `EXIT <code>`: 0 written and loaded back; 2 refused by a guard (nothing written); 3 an identity
failed (nothing written; after the write, the file stays on record).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from extended import VENDOR_STAGE2  # noqa: E402
from extended import day_calendar as DC  # noqa: E402
from extended import search_calendar as SC  # noqa: E402

EXIT_WRITTEN, EXIT_REFUSED, EXIT_IDENTITY = 0, 2, 3
SCRIPT = "scripts/search_calendar.py"
DATA_MANIFEST = ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"
#: the vendored calendars `extended.features.load_calendars` reads (BLS 08:30 release days, FOMC statements)
CALENDAR_FILES = ("data/release_days_0830_2009_2025.csv", "data/release_days_0830_2026.csv",
                  "config/sources/fomc_statements.csv", "config/sources/fomc_statements_2020_2024q1.csv",
                  "config/sources/fomc_statements_2026q3.csv")
CODE_FILES = ("scripts/search_calendar.py", "extended/search_calendar.py", "extended/day_calendar.py",
              "extended/features.py", "extended/calendar_early_closes.py", "extended/triggers.py",
              "extended/walker.py")


def _rel(p: Path) -> str:
    try:
        return Path(os.path.abspath(p)).relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def inputs_record(manifest: Path, calendar: Path, flags: Path) -> dict:
    """Every input's sha256 (and H2's sidecar manifest's own record of its file)."""
    side = Path(str(flags) + ".manifest.json")
    h2 = json.loads(side.read_text(encoding="utf-8"))
    bars = json.loads(Path(manifest).read_text(encoding="utf-8"))
    return {
        "bars_manifest": {"file": _rel(manifest), "sha256": SC.sha256_file(manifest),
                          "parquet_sha256": bars.get("parquet_sha256"), "bars_read": False},
        "calendar_early_closes": {"file": _rel(calendar), "sha256": SC.sha256_file(calendar)},
        "h2_flags": {"file": _rel(flags), "sha256": SC.sha256_file(flags),
                     "manifest_sha256": SC.sha256_file(side), "manifest_records": h2.get("sha256"),
                     "git_commit": h2.get("git_commit")},
        "vendored_calendars": {f"vendor/stage2/{r}": SC.sha256_file(VENDOR_STAGE2 / r) for r in CALENDAR_FILES},
        "a1_days": "not read",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", type=Path, default=DC.MANIFEST, help="the bar store's manifest (metadata only)")
    ap.add_argument("--calendar", type=Path, default=DC.CALENDAR_CSV, help="Q-40's calendar")
    ap.add_argument("--flags", type=Path, default=None, help="H2's flags file (default the committed result)")
    ap.add_argument("--out-dir", type=Path, default=None, help="default results/ (a clean run only)")
    a = ap.parse_args(argv)
    t0 = time.monotonic()
    flags = a.flags if a.flags is not None else DC.default_flags_path()
    try:
        if not Path(str(flags) + ".manifest.json").is_file():
            raise SC.CalendarRefused(f"{flags}: H2's flags file is read only with its sidecar manifest")
        if Path(os.path.abspath(a.manifest)) == Path(os.path.abspath(DC.MANIFEST)):
            want = SC.data_manifest_sha(DATA_MANIFEST, "data/bars/NQ/manifest.json")
            got = SC.sha256_file(a.manifest)
            if want != got:
                raise SC.CalendarRefused(f"the bar manifest's sha256 {got} is not vendor/DATA_MANIFEST_stage2's "
                                         f"{want}")
        src = DC.load_sources(flags, manifest=a.manifest, calendar=a.calendar)
        rows = SC.build_rows(src)
        dates = SC.check_rows(rows, require_span=True)
    except (DC.HeldOutDay, SC.CalendarRefused, KeyError, ValueError) as exc:
        print(f"REFUSED: {type(exc).__name__}: {exc}", flush=True)
        print(f"EXIT {EXIT_REFUSED}", flush=True)
        return EXIT_REFUSED

    import pandas as pd
    from extended.results import write_result

    df = pd.DataFrame(rows, columns=list(SC.COLUMNS))
    try:
        back = SC.parse_csv_text(df.to_csv(index=False))       # the writer's own serialisation, parsed back
        if back != rows:
            raise SC.CalendarIdentityError("the CSV text parsed back is not the rows built")
        ident = SC.identities(back, src)
    except SC.CalendarIdentityError as exc:
        print(f"IDENTITY FAILED: {exc}", flush=True)
        print(f"EXIT {EXIT_IDENTITY}", flush=True)
        return EXIT_IDENTITY

    digest = SC.calendar_digest(dates)
    params = {
        "calendar_sha256": digest, "calendar_digest": "sha256 of the ISO dates, one a line, each ended by \\n "
        "(W42-R1's calendar_digest, extended/wave42.py at wt/wt-infra 357a339)",
        "sessions": len(dates), "first": dates[0], "last": dates[-1],
        "search_years": [str(SC.SEARCH_START), str(SC.SEARCH_END)], "held_out_read": False,
        "confirmation_window_read": False,
        "session_counting": "session 1 is the first date; sessions_left = N - session + 1, the start session counted "
                            "(H4's draft, wt/wt-h4 f897cd7; W42-R1's B-2)",
        "reading_classes": {c: {"reads_overnight": on, "reads_0829": b} for c, (on, b) in SC.CLASSES.items()},
        "rule2_threshold": int(src.threshold()), "walk_last_stamp": DC.label(DC._walk_last_stamp(_rules())),
        "inputs": inputs_record(a.manifest, a.calendar, flags),
        "code_sha256": {r: SC.sha256_file(ROOT / r) for r in CODE_FILES},
        "identities": ident,
    }
    csv_path, _ = write_result(
        df, SC.RESULT_NAME, script=SCRIPT, seed=None, require_seed=False, results_dir=a.out_dir,
        description="Q-197: the pinned search-year session calendar -- every NQ session 2020-01-02..2023-12-29 of the "
                    "bar manifest's day_list, its ordinal and sessions left (start counted), day kind and each "
                    "reading class's void flags from extended.day_calendar; dates, labels and integers only; no "
                    "randomness", parameters=params)
    loaded = SC.load_search_calendar(csv_path)
    if list(loaded.rows) != rows or loaded.calendar_sha256 != digest:
        print(f"IDENTITY FAILED: {csv_path} loaded back differs from the rows built (the file stays on record)")
        print(f"EXIT {EXIT_IDENTITY}", flush=True)
        return EXIT_IDENTITY
    print(f"wrote {_rel(Path(csv_path))}: {len(dates)} sessions {dates[0]}..{dates[-1]}, calendar_sha256 {digest}; "
          f"I-1 and I-2 held; {time.monotonic() - t0:.1f} s", flush=True)
    print(f"EXIT {EXIT_WRITTEN}", flush=True)
    return EXIT_WRITTEN


def _rules():
    from extended import triggers as T
    return T.JOURNEY


if __name__ == "__main__":
    sys.exit(main())
