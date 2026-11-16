"""Generate manual-run kits in runs/<run-id>/ (D-82).

    python scripts/make_run_kit.py R001-dataset-checks
    python scripts/make_run_kit.py --all

Commit the kit before running it: ingestion refuses a result whose algorithm is not committed.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.data.run_kit import SPECS, write_kit  # noqa: E402


def main(argv: list[str]) -> int:
    ids = list(SPECS) if argv == ["--all"] else argv
    if not ids:
        print(__doc__)
        return 1
    for run_id in ids:
        print(f"kit written: {write_kit(run_id).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
