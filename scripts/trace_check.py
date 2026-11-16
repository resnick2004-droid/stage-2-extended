"""The trace check (Q-04): every registered number recomputes from its result file and appears in its documents.

    python scripts/trace_check.py

Exit 0 when something is registered and every check passes; 1 when a check fails (a document drifted from its result,
a result file fails its manifest, a recompute broke); **2 NOT CHECKED when nothing is registered** -- an empty
registry is never a vacuous pass. The registry is `extended/trace.py`'s `REGISTRY`; the checking is the vendored
`propedge.reporting.trace.run_trace_check` on this repository's `results/` and documents.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))

import extended.trace as T  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)
    report = T.run()
    lines = report._verdict_lines()
    if report.checked_nothing:
        print("NOT CHECKED: no traced number is registered (extended/trace.py REGISTRY) -- this is not a pass. "
              "Register each number a document states as its result file is produced.")
        for line in lines:
            print(line)
        return 2
    print(report.summary())
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
