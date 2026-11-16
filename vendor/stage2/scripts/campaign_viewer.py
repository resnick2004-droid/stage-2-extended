"""Render the campaign results viewer from result files (T7a, slice 6).

    python scripts/campaign_viewer.py [--prefix t7a_dry_run] [--out docs/viewer/t7a_dry_run.html]

Every number on the page comes from a result CSV read through the hash-verified loader; the
page names the files, the commit and the seed, and carries the manifests' exploratory flag as a
banner. See `propedge.reporting.campaign_viewer`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.reporting.campaign_viewer import write_viewer  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prefix", default="t7a_dry_run")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or (ROOT / "docs" / "viewer" / f"{args.prefix}.html")
    path = write_viewer(out, prefix=args.prefix)
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
