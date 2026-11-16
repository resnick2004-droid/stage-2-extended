"""Build the dispersion report's pages (Q-27): result files of start rows -> docs/report/<name>/README.md and its
charts, every number computed from its file (`extended/report.py`).

    python scripts/build_report.py --list                          # the registered pages
    python scripts/build_report.py --report demo_stage2_u1         # one registered page -> docs/report/<name>/
    python scripts/build_report.py --report journey_scorecard      # Q-69: the journey scorecard on Q-44's files
    python scripts/build_report.py --all                           # every registered page
    python scripts/build_report.py --spec my_page.json --out <dir> # a page not registered (it says NOT TRACED)

A registered page is trace-checked as soon as it is built (`extended.trace.run` on its numbers): exit 0 when every
number is found on it, 1 when one is not, 2 when the file or the spec is refused (a file failing its manifest, a design
with no rows, rows that disagree with themselves) -- nothing is written then. The spec file of `--spec` is JSON with
`name`, `title`, `source` (relative to the repository root), `where`, `designs` ([{key, short, label, where}]), `base`,
`ladder`, `demonstration`, `note` (`extended.report.spec_from_dict`). A registered page whose files are not written
yet (`extended.report.waiting`) is listed as waiting, skipped by `--all`, and refused by `--report` (exit 2).

Reads a result file and writes a page; runs no engine and writes nothing under results/. Run it in its own process
(it imports the vendored engine); it is not importable by name -- Stage 2's vendored scripts/ holds a module of the same
name.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="the registered pages")
    g.add_argument("--report", help="build one registered page")
    g.add_argument("--all", action="store_true", help="build every registered page")
    g.add_argument("--spec", type=Path, help="build a page from a JSON spec (not registered: NOT TRACED)")
    ap.add_argument("--out", type=Path, help="the folder for --spec (default docs/report/<name>)")
    args = ap.parse_args(argv)

    import extended.report as R

    if args.list:
        for name, spec in R.REPORTS.items():
            why = R.waiting(spec)
            print(f"{name}: {spec.source} -> {spec.out_dir}/{R.PAGE} ({len(spec.designs)} designs)"
                  + (f" -- waiting: {why}" if why else ""))
        return 0
    if args.spec is not None:
        specs = [R.spec_from_dict(json.loads(args.spec.read_text(encoding="utf-8")))]
    elif args.all:
        specs = list(R.REPORTS.values())
    else:
        if args.report not in R.REPORTS:
            print(f"no registered page {args.report!r}; registered: {', '.join(R.REPORTS)}")
            return 2
        specs = [R.REPORTS[args.report]]

    rc = 0
    for spec in specs:
        why = R.waiting(spec) if args.spec is None else None
        if why:
            print(f"{'skipped' if args.all else 'REFUSED'} {spec.name}: waiting -- {why}")
            if not args.all:
                return 2
            continue
        t0 = time.time()
        try:
            built = R.build(spec, out=args.out if args.spec is not None else None)
        except (R.ReportError, ValueError, FileNotFoundError) as exc:
            print(f"REFUSED {spec.name}: {exc}")
            return 2
        print(f"{spec.name}: {built.page} -- {len(built.claims)} numbers, {len(built.charts)} charts, "
              f"{time.time() - t0:.1f} s")
        if spec.name in R.REPORTS and args.spec is None:
            import extended.trace as T

            report = T.run(R.traced_numbers(spec))
            lines = report.summary().splitlines()
            print(lines[0])
            for line in lines[1:]:
                if "[FAIL]" in line:
                    print(line)
            rc = max(rc, 0 if report.passed else 1)
        else:
            print("  not registered in extended/trace.py: the page says NOT TRACED")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
