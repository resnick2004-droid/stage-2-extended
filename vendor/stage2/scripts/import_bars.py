"""Import the operator's Databento 1-minute bars into the local store (R3, D-458).

    python scripts/import_bars.py C:\\Users\\resni\\Downloads\\GLBX-<job>.zip [more zips...]

Each zip is checked against its own manifest hash and imported into `data/bars/<ROOT>/` (git-ignored), keeping only
the trading days inside the market's declared development, spent and confirmation windows (`config/windows.yaml`,
R4); a reserved day is dropped and counted, never stored. Prints what was kept and dropped. The reader
(`propedge.data.bars.read_bars`) guards every read by purpose; nothing here opens a confirmation window.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.data.bar_import import BarImportError, import_zip  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    for z in argv:
        try:
            m = import_zip(z)
        except BarImportError as exc:
            print(f"REFUSED {Path(z).name}: {exc}")
            return 1
        last = m["imports"][-1]
        cond = last.get("condition")
        print(json.dumps({"root": m["root"], "source": last["source"], "csv_sha256": last["csv_sha256"],
                          "rows_read": last["rows_read"], "dropped_by_window": last["charted_bars_dropped_by_window"],
                          "days_dropped_by_window": last["days_dropped_by_window"],
                          "store_days": m["days"], "first_day": m["first_day"], "last_day": m["last_day"],
                          "rolls": len(m["rolls"]), "short_days": len(m["short_days"]),
                          "late_start_days": len(m["late_start_days"]), "early_end_days": len(m["early_end_days"]),
                          "condition_counts": cond["counts"] if cond else None,
                          "not_available_in_stored_windows": len(cond["not_available"]) if cond else None},
                         indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
