"""IM2's second implementation against the kit (D-193 as amended by D-200), session by session.

    python scripts/crosscheck_im2.py             # all eight windows; writes the result files
    python scripts/crosscheck_im2.py --preview   # the windows ingested so far; prints, writes nothing

Needs P-04 runnable in `prereg/REGISTRY.md` (D-179), the development runs R053-R060 and the second implementation's
runs R063-R070 ingested (`scripts/ingest_manual_run.py`). Writes results/im2_second_implementation.csv (one row per
window: sessions, signals and entries compared, mismatches) and results/im2_second_implementation_mismatches.csv
(every mismatch; empty on a pass), each with its manifest. **The pass is zero mismatches** (D-200 (4)); a mismatch is
diagnosed under the failure protocol before anything is rerun.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge.backtest.harness import PreregRegistry  # noqa: E402
from propedge.data.qc_algorithms import IM2_RUNS, IM2X_RUNS  # noqa: E402
from propedge.reporting.results import sha256_of, write_result  # noqa: E402
from propedge.research import im2_crosscheck as xc  # noqa: E402
from propedge.research import im2_score as sc  # noqa: E402

SCRIPT = "scripts/crosscheck_im2.py"
PREREG = "P-04"
RESULT = "im2_second_implementation"
CRITERION = "zero mismatches over every session of the eight development windows (D-200 (4))"


def input_hashes(results_dir: Path | None = None) -> dict:
    """{run id: sha256 of its ingested result file} for the kit's runs and the second implementation's."""
    base = Path(results_dir) if results_dir is not None else sc.RESULTS_DIR
    return {rid: sha256_of(base / f"manual_{rid.replace('-', '_')}.csv")
            for rid in sorted({*IM2_RUNS.values(), *IM2X_RUNS.values()})}


def main(preview: bool = False, registry: Path | None = None, results_dir: Path | None = None) -> int:
    PreregRegistry.load(registry).require_runnable(PREREG)
    summary, mism, missing = xc.compare_all(results_dir)
    if not summary.empty:
        print(summary.to_string(index=False))
    if len(mism):
        print(f"\n{len(mism)} mismatches; the first twenty:")
        print(mism.head(20).to_string(index=False))
    if missing:
        print(f"\nnot yet ingested: {', '.join(missing)}")
    if preview:
        return 0
    if missing:
        print("REFUSED: the result is written only when all eight windows are ingested (D-200 (3)); use --preview.")
        return 2
    passed = len(mism) == 0
    summary["passed"] = summary["mismatches"] == 0
    common = {"script": SCRIPT, "seed": None, "require_seed": False, "prereg_id": PREREG, "results_dir": results_dir,
              "provenance": {"inputs_sha256": input_hashes(results_dir)},
              "parameters": {"tolerance": xc.TOL, "criterion": CRITERION, "kit_runs": sorted(IM2_RUNS.values()),
                             "second_runs": sorted(IM2X_RUNS.values()), "passed": passed}}
    write_result(summary, RESULT, **common,
                 description="D-200: IM2's second implementation against the kit, per development window: sessions, "
                             "signals and entries compared, and the mismatches; passed when there are none.")
    write_result(mism if len(mism) else pd.DataFrame(columns=mism.columns), f"{RESULT}_mismatches", **common,
                 description="D-200: every mismatch between IM2's second implementation and the kit (empty on a "
                             "pass).")
    print(f"\nIM2 second implementation: {'PASS' if passed else 'FAIL'} -- {len(mism)} mismatches "
          f"({CRITERION}).")
    return 0 if passed else 1


def _cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--preview", action="store_true", help="compare the windows ingested so far; write nothing")
    a = ap.parse_args(argv)
    return main(preview=a.preview)


if __name__ == "__main__":
    raise SystemExit(_cli())
