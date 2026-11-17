"""Refuse a commit whose CSVs hold or reveal an NQ price level (Q-131): the pre-commit hook's licence check.

    python scripts/check_price_levels.py                       # the default index's copy of every candidate file
    python scripts/check_price_levels.py --index "$GIT_INDEX_FILE"   # the commit's own index (the hook)
    python scripts/check_price_levels.py --worktree            # the working tree's copy instead

Scans every tracked or staged `.csv`/`.tsv` outside `vendor/` with `extended.price_levels` against
`tests/price_level_allowlist.csv`. Exit 0 when nothing is refused and no allow-list entry is stale; 1 otherwise,
listing each finding as `file: rule column (share)` -- names and shares only, never a cell's value; 2 on a usage or
read error. The same check runs in the fast tier as `tests/test_results_no_price_levels.py`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended.price_levels import ALLOWLIST_REL, check_tree   # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(ROOT), help="the repository's root (default: this one)")
    ap.add_argument("--index", default="", help="the index file to read (the hook passes GIT_INDEX_FILE); "
                                                "empty: the default index")
    ap.add_argument("--worktree", action="store_true", help="read the working tree's copies, not the index's")
    args = ap.parse_args(argv)
    root = Path(args.root)
    try:
        rep = check_tree(root, source="worktree" if args.worktree else "index", index_file=args.index or None)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"check_price_levels: could not run the check: {exc}", file=sys.stderr)
        return 2
    allowed = len(rep.findings) - len(rep.refused)
    print(f"check_price_levels: {len(rep.files)} files, {len(rep.refused)} refused, {allowed} allow-listed, "
          f"{len(rep.stale)} stale entries, {rep.seconds:.2f} s")
    for f in rep.refused:
        print(f"  REFUSED {f}")
    for a in rep.stale:
        print(f"  stale allow-list entry (matches nothing): {a.file},{a.rule},{a.column}")
    if rep.refused or rep.stale:
        print(f"check_price_levels: a file may hold or reveal a licensed NQ price level (E-002). Remove it from the "
              f"commit, or -- only if a column is not a price -- class it by meaning in {ALLOWLIST_REL}; drop a stale "
              f"entry.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
