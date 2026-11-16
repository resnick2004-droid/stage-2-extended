"""Check every exported trade of a model's runs against the rules the model declared (D-148).

    python scripts/audit_trades.py

Writes results/trade_audit_fv1.csv: one row per run and check, with the number of trades checked and the number
violating the check. Any violation is a kit or scorer defect, diagnosed under the failure protocol. The next model
adds its runs and its checks here.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge.data.qc_algorithms import FV_EXT_RUNS, FV_RUNS, fv_params  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import fv_score as fs  # noqa: E402
from propedge.research.trade_audit import fv1_checks, run_checks  # noqa: E402


def main() -> int:
    rows = []
    for runs in (FV_RUNS, FV_EXT_RUNS):
        for market, run in runs.items():
            _, trades = fs.split(read_result(ROOT / "results" / f"manual_{run.replace('-', '_')}.csv"))
            got = run_checks(trades, fv1_checks(fv_params(market)))
            rows += [{"model": "FV1", "run": run, "market": market, "check": k, "trades": len(trades),
                      "violations": v} for k, v in got.items()]
            print(f"{run}: {len(trades)} trades, {sum(got.values())} violations")
    out = pd.DataFrame(rows)
    write_result(out, "trade_audit_fv1", script="scripts/audit_trades.py", seed=None, require_seed=False,
                 parameters={"checks": "propedge/research/trade_audit.py fv1_checks", "design": "config/model_fv.yaml",
                             "runs": sorted(out["run"].unique())},
                 notes={"decision": "D-148", "reads": "the ingested run files; nothing is simulated"},
                 description="FV1: every exported trade of R045-R048 checked against the model's declared rules.")
    return 0 if out["violations"].sum() == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
