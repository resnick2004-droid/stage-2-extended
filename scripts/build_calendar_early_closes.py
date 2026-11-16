"""Q-40 (E-022 (3)): build `config/calendar_early_closes.csv` -- the scheduled early closes and holidays of CME Globex
equity-index futures (NQ), 2020-01-02 to 2026-07-16, from the standard exchange holiday rules, cross-checked against
the bar store's manifest (metadata only; no bar file is opened), with the store's data-defect candidates apart.

    python scripts/build_calendar_early_closes.py            # write the file (refuses to replace a different one)
    python scripts/build_calendar_early_closes.py --check    # rebuild in memory and compare; writes nothing
    python scripts/build_calendar_early_closes.py --force    # replace a different file (before it is pinned only)

Light: the rules, the vendored BLS calendars and one JSON file. Nothing random; nothing from 2026-07-17 is read or
written (`extended.calendar_early_closes`). Prints what the cross-check found, for the hand-back; the file is the
record.
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

from extended import calendar_early_closes as C  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--manifest", type=Path, default=C.MANIFEST, help="the bar store's manifest.json")
    ap.add_argument("--out", type=Path, default=C.CALENDAR_CSV)
    ap.add_argument("--check", action="store_true", help="compare with the file on disk; write nothing")
    ap.add_argument("--force", action="store_true", help="replace a file on disk that differs")
    a = ap.parse_args(argv)

    if not a.manifest.exists():
        print(f"refused: no manifest at {a.manifest} (the bar store's junction is not linked here)", file=sys.stderr)
        return 2
    manifest = C.load_manifest(a.manifest)
    rows = C.build_rows(C.scheduled_rows(), manifest)
    text = C.render(rows, manifest)
    lf_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

    kinds = Counter(r.kind for r in rows)
    print(f"rows {len(rows)}: " + ", ".join(f"{k} {kinds[k]}" for k in C.KINDS))
    for r in rows:
        if r.kind == "data_defect_candidate" or "not as scheduled" in r.source or "not shown" in r.source:
            print(f"  {r.date} {r.kind:22s} {r.close_ct:5s} {r.source}")
    beside = C.degraded_days_not_listed(manifest, rows)
    print(f"beside (not in the file): {len(beside)} days the store holds whole whose session touches a Databento "
          "degraded UTC date")
    for d, note in beside:
        print(f"  {d} {note}")
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
