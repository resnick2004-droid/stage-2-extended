"""The success criteria's computed levels (R1, D-457): the required-bankroll p95 path and the FLAG levels.

    python scripts/success_thresholds.py

Reads FV3-C's confirmation (P-06) only: its saved paths (`results/fv3_confirmation_paths.csv`, the p95 path) and its
gate campaign's per-path detail (`results/fv3c_confirmation_path_detail.csv`, written by
`scripts/fv3c_confirmation_path_detail.py` after reproducing the saved paths exactly; the steadiness measures need it).
Writes `results/success_thresholds.csv` with its manifest: one `p95_path` row and one `flag` row per measure of
`docs/SUCCESS_CRITERIA.md` §5. A deterministic reading -- nothing is drawn, so no seed; the sources' manifests carry
P-06's seed and registration. Exploratory by its source (the detail file is exploratory: a re-run on a read window).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge import RESULTS_DIR  # noqa: E402
from propedge.campaign.criteria import flag_levels, p95_path  # noqa: E402
from propedge.campaign.portfolio import DEFAULT_MARGIN  # noqa: E402
from propedge.reporting.results import read_result, sha256_of, write_result  # noqa: E402

SCRIPT = "scripts/success_thresholds.py"
RESULT = "success_thresholds"
PATHS = "fv3_confirmation_paths.csv"
DETAIL = "fv3c_confirmation_path_detail.csv"


def main() -> int:
    paths = read_result(RESULTS_DIR / PATHS)
    detail = read_result(RESULTS_DIR / DETAIL)
    p95 = p95_path(paths)
    rows = [{"section": "p95_path", "measure": k, "level": v, "source": f"results/{PATHS}"} for k, v in p95.items()]
    lv = flag_levels(detail)
    lv.insert(0, "section", "flag")
    lv["source"] = f"results/{DETAIL}"
    out = pd.concat([pd.DataFrame(rows), lv], ignore_index=True)
    write_result(out, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 parameters={"paths": f"results/{PATHS}", "paths_sha256": sha256_of(RESULTS_DIR / PATHS),
                             "detail": f"results/{DETAIL}", "detail_sha256": sha256_of(RESULTS_DIR / DETAIL),
                             "margin": DEFAULT_MARGIN, "arm": "gate placement off, lower bound, 0 % denial",
                             "flag_rule": "P-06's lower-bound arm's p90 path in the bad direction (p10 where higher "
                                          "is better); docs/SUCCESS_CRITERIA.md section 5"},
                 description="The success criteria's levels from P-06's own paths: the required-bankroll p95 path "
                             "(D-400's P2, the deployment protocol's drawdown line) and the FLAG levels of the measures "
                             "that had no threshold. Exploratory by its detail source; FLAGs never decide a verdict.",
                 notes={"status": "EXPLORATORY levels for reporting (R1, D-457); the gate is unchanged"})
    print(f"wrote results/{RESULT}.csv ({len(out)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
