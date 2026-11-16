"""Write the scoreboard (R2, D-455): every registered run's gate rows side by side, FV3-C's rows the ones to beat.

    python scripts/scoreboard.py            # write results/scoreboard.csv and its manifest
    python scripts/scoreboard.py --check    # exit 1 if the committed scoreboard differs from a fresh build

The runs and how each file is read are declared in `config/scoreboard.yaml`; the reading is
`propedge/reporting/scoreboard.py`. Nothing random is drawn, so there is no seed: the scoreboard is a deterministic
reading of result files whose own manifests carry their seeds. Each source's sha256 is recorded in the manifest's
parameters, and `tests/test_scoreboard.py` refuses a scoreboard whose sources changed since it was built.
After writing, rebuild the report (`python scripts/build_report.py`): its scoreboard section reads this file.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge import RESULTS_DIR  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.reporting.scoreboard import (  # noqa: E402
    CONFIG_PATH, RESULT_NAME, SCRIPT, build, comparable, load_config, sources,
)


def main(argv: list[str]) -> int:
    cfg = load_config()
    sb = build(cfg)
    if "--check" in argv:
        path = RESULTS_DIR / RESULT_NAME
        if not path.is_file():
            print(f"MISSING: results/{RESULT_NAME}")
            return 1
        old = read_result(path)
        same = old.shape == sb.shape and list(old.columns) == list(sb.columns)
        if same:
            try:
                pd.testing.assert_frame_equal(comparable(old).reset_index(drop=True), comparable(sb).reset_index(drop=True),
                                              check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12)
            except AssertionError:
                same = False
        print("the scoreboard matches a fresh build" if same else f"STALE: results/{RESULT_NAME}")
        return 0 if same else 1
    csv, man = write_result(
        sb, RESULT_NAME, script=SCRIPT, seed=None, require_seed=False,
        parameters={"config": str(CONFIG_PATH.relative_to(ROOT)).replace("\\", "/"),
                    "row_to_beat": cfg["row_to_beat"], "runs": [r["id"] for r in cfg["runs"]],
                    "sources_sha256": sources(cfg),
                    "gate_row": "section gate, shift lower_bound, enforcement_p 0, placement off (first such row)",
                    "metric": "pf_growth_on_base_p50 on pf_required_p90 (growth on the required bankroll, D-312)"},
        description="The scoreboard (R2): every registered run's gate rows side by side; FV3-C's rows of the same "
                    "kind are the ones to beat (D-365, D-382, D-452). A deterministic reading of the named result "
                    "files; their own manifests carry seeds and pre-registrations.",
        exploratory=False,
        notes={"status": "a reading of registered runs' result files; no new run, nothing drawn",
               "handoff": "docs/HANDOFF_RESET_2026-10-29.md section 2 (its table is this file's first cut)",
               "beside_never_deciding": "denial 10/25/50 % and the break-even denial (D-234); the placement on "
                                        "(D-289); the zero-edge twin; the notional engine's median_log_growth"},
    )
    print(f"wrote {csv.relative_to(ROOT)} and {man.relative_to(ROOT)} ({len(sb)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
