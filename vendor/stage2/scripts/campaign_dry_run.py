"""Run the T7a dry run: the campaign engine end to end at an ASSUMED edge (D-119).

    python scripts/campaign_dry_run.py [--paths 150] [--horizon 504]

Writes results/t7a_dry_run_{arms,paths,cash,accounts}.csv with manifests, every one
`exploratory=True` with the assumed inputs in its notes. Nothing it writes is a result and
nothing is cited anywhere. See `propedge.campaign.dry_run`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.campaign.dry_run import run_dry_run  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths", type=int, default=150)
    ap.add_argument("--horizon", type=int, default=504)
    args = ap.parse_args()
    out = run_dry_run(n_paths=args.paths, horizon_days=args.horizon)
    for key, path in out.items():
        print(f"{key:9s} {path}")
    print("exploratory=True on every manifest; assumed edge; cited nowhere (D-119)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
