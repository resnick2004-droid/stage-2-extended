"""Q-79 (from Q-73's research note): build `config/calendar_fomc_minutes.csv` -- the release days of the FOMC's minutes,
2020-01-02 to 2026-07-16, each at its press release's time (14:00 ET = 13:00 CT) -- from the research CSV
`docs/research/fomc_minutes_dates_2026-11-16.csv`, taken only at the sha256 its note states.

    python scripts/build_calendar_fomc_minutes.py            # write the file (refuses to replace a different one)
    python scripts/build_calendar_fomc_minutes.py --check    # rebuild in memory and compare; writes nothing
    python scripts/build_calendar_fomc_minutes.py --force    # replace a different file (before it is pinned only)

Light: one research CSV, Stage 2's vendored FOMC statement calendars and the pinned early-close calendar. Nothing
random; no bar read; nothing from 2026-07-17 is written (`extended.calendar_fomc_minutes`). Prints what it checked and
the file's LF sha256, for the hand-back; the file is the record.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import calendar_fomc_minutes as M  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--research", type=Path, default=M.RESEARCH_CSV, help="the research CSV (at its pinned sha256)")
    ap.add_argument("--out", type=Path, default=M.CALENDAR_CSV)
    ap.add_argument("--check", action="store_true", help="compare with the file on disk; write nothing")
    ap.add_argument("--force", action="store_true", help="replace a file on disk that differs")
    a = ap.parse_args(argv)

    try:
        research = M.read_research(a.research)
        statement_days = M.fomc_statement_days()
        rows = M.build_rows(research, statement_days=statement_days)
        overlaps = M.early_close_overlaps(rows)
        text = M.render(rows, research_sha256=M.RESEARCH_CSV_SHA256, overlaps=overlaps)
    except ValueError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    lf_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

    years = Counter(r.release_date[:4] for r in rows)
    print(f"rows {len(rows)} ({rows[0].release_date} to {rows[-1].release_date}): "
          + ", ".join(f"{y} {years[y]}" for y in sorted(years)))
    print(f"times: ET {sorted({r.time_et for r in rows})}, CT {sorted({r.time_ct for r in rows})}")
    in_window = sorted(d for d in statement_days if M.WINDOW_START.isoformat() <= d <= M.WINDOW_END.isoformat())
    shared = sorted({r.release_date for r in rows} & set(statement_days))
    print(f"FOMC statement days of the vendored calendars inside the window: {len(in_window)}; release days among "
          f"them: {len(shared)}")
    print(f"release days the early-close calendar also lists: {len(overlaps)}")
    for d, kind, close in overlaps:
        print(f"  {d} {kind}" + (f" (trading stops {close} CT)" if close else ""))
    print(f"LF sha256 {lf_sha}")

    on_disk = a.out.read_bytes().replace(b"\r\n", b"\n").decode("utf-8") if a.out.exists() else None
    if a.check:
        same = on_disk == text
        print("check: the file on disk " + ("matches the rebuild" if same else "DIFFERS from the rebuild"))
        return 0 if same else 1
    if on_disk is not None and on_disk != text and not a.force:
        print(f"refused: {a.out} exists and differs from the rebuild (a pinned file is never replaced; --force "
              "before a pin only)", file=sys.stderr)
        return 1
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
