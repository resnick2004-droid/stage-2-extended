"""Write config/im2_release_calendar.csv from config/sources/ (P-04 §3; `propedge/data/im2_releases.py`).

    python scripts/build_im2_release_calendar.py

No network: the sources were read once, 2026-09-27, and are committed. tests/test_im2_releases.py checks the committed
calendar equals this script's output.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.data import im2_releases as rel  # noqa: E402


def main() -> int:
    df = rel.build()
    df.to_csv(rel.CALENDAR, index=False, lineterminator="\n")
    print(f"{len(df)} rows -> {rel.CALENDAR.relative_to(ROOT)}")
    print(df.groupby(["code", "method"]).size().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
