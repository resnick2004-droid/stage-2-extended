"""The sizeable stop band (D-201 (2)), per market with a micro and per lifecycle state of stage one's family.

    python scripts/stop_band.py

Writes results/stop_band.csv (`propedge/research/stop_band.py`): each state's dollar risk, the micro's tick value, its
size cap, and the band's narrow edge (the larger of the stop below which the cap binds and the stop at which the cost
drag falls to 0.10) and wide edge (the widest stop buying one whole micro), in the micro's ticks. Its manifest records
the sha256 of every input (`stop_band.INPUTS`); `tests/test_stop_band.py` fails when any changes, so rerun this then.
A model card cites the band (D-201).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge.reporting.results import write_result  # noqa: E402
from propedge.research import stop_band as sb  # noqa: E402

SCRIPT = "scripts/stop_band.py"


def main(results_dir: Path | None = None) -> int:
    df = pd.DataFrame(sb.band_rows())
    write_result(df, sb.RESULT, script=SCRIPT, seed=None, require_seed=False, results_dir=results_dir,
                 provenance={"inputs_sha256": sb.input_hashes()},
                 parameters={"family": [list(f) for f in sb.FAMILY], "cost_drag_floor": sb.COST_DRAG_FLOOR,
                             "fill_profile": sb.FILL_PROFILE, "max_outside": sb.MAX_OUTSIDE, "decision": "D-201 (2)"},
                 description="D-201 (2): the sizeable stop band in the micro's ticks, per market with a micro and per "
                             "lifecycle state: the narrow edge the larger of the size-cap stop and the 0.10 "
                             "cost-drag stop, the wide edge the widest stop buying one whole micro.")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
