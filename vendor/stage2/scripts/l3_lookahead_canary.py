"""L3, the look-ahead canary (D-195), on synthetic sessions for ES, CL, 6E and NG.

    python scripts/l3_lookahead_canary.py

Writes results/l3_lookahead_canary.csv: per market, the kit's core (`im2_core`) and the second implementation
(`im2x_core`, D-200) with no decision input or prior entry changed when every later bar is perturbed, and the two
planted look-aheads each caught (`propedge/research/lookahead_canary.py`). Its manifest carries the engine pin (D-180):
a verdict is citable only when this file passed against the same engine files (D-195; `propedge/reporting/trace.py`).
Rerun after any change to an engine file.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge.reporting.pin import engine_pin  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402
from propedge.research import lookahead_canary as lc  # noqa: E402

SCRIPT = "scripts/l3_lookahead_canary.py"
RESULT = "l3_lookahead_canary"


def main(results_dir: Path | None = None) -> int:
    warnings.filterwarnings("ignore")
    rows = [r for m in lc.MARKETS for r in lc.run_canary(m, seed=lc.SEED)]
    df = pd.DataFrame(rows)
    passed = bool(df["passed"].all())
    write_result(df, RESULT, script=SCRIPT, seed=lc.SEED, results_dir=results_dir,
                 provenance={"engine": engine_pin()},
                 parameters={"markets": list(lc.MARKETS), "sessions_per_market": lc.SESSIONS, "passed": passed,
                             "layer": "L3", "decision": "D-195"},
                 description="L3 (D-195): every bar after each decision perturbed on synthetic sessions; the kit's "
                             "core and the second implementation must not change a decision input or an entry "
                             "decided by then, and two planted look-aheads must be caught.")
    print(df.to_string(index=False))
    print(f"\nL3 look-ahead canary: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
