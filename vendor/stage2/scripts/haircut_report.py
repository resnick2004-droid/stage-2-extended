"""D-189's program haircut beside IM2's development verdict: e's bound at one-sided 0.05/N and the deflated Sharpe
ratio, N counted by the ledger for P-04 (T12 item 7).

    python scripts/haircut_report.py

A companion to `scripts/score_im2.py`, which it leaves unchanged (its files are pinned, D-180), as
`scripts/breakeven_report.py` is: it builds the same entry table and day set from the ingested development runs
R053-R060 and the same fees -- so it refuses, as the scorer does, before the 2026-10-01 re-read of the MCL and MNG
round turns and unless P-04 is runnable -- and writes results/im2_development_haircut.csv:

* `section` edge -- per R and scale on the verdict's outcomes (`v`): N (`propedge.research.ledger.count_for_registration`
  on `prereg/models.yaml`), the level 0.05/N, e, the widened bootstrap and normal bounds and the lower of them, the
  bootstrap's 95 % percentile bound as the scorer computes it, and the daily series' deflated Sharpe ratio
  (`propedge.research.haircut`);
* `section` gate -- per scale, the D-145 gate run exactly as the verdict's but with each R at its widened bound, with
  both kill lines read on it.

For IM2 the haircut is computed and reported beside P-04's registered verdict and never replaces it (D-189): P-04 was
registered before the rule, with its eight development runs in.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge.backtest.harness import PreregRegistry  # noqa: E402
from propedge.reporting.pin import engine_pin  # noqa: E402
from propedge.reporting.results import sha256_of, write_result  # noqa: E402
from propedge.research import haircut as hc  # noqa: E402
from propedge.research import im2_score as sc  # noqa: E402
from propedge.research import ledger as lg  # noqa: E402

SCRIPT = "scripts/haircut_report.py"
PREREG = "P-04"


def main(registry: Path | None = None, results_dir: Path | None = None, ledger_path: Path | None = None) -> int:
    from breakeven_report import development_table

    warnings.filterwarnings("ignore")
    PreregRegistry.load(registry).require_runnable(PREREG)
    cfg = sc.config()
    rt = sc.fees(cfg)                                   # refuses before the 2026-10-01 re-read (P-04 §3)
    led_file = Path(ledger_path) if ledger_path is not None else lg.LEDGER_FILE
    count = lg.count_for_registration(lg.load_ledger(led_file), PREREG)
    n = count["N"]
    table, days = development_table(cfg, rt)
    edge_rows = hc.per_edge_rows(table, days, n, R_all=sc.RR_ALL, scales=sc.SCALES, col="v", seed=sc.SEED,
                                 block=sc.BOOT_LEN, reps=sc.REPS)
    rows = [{"section": "edge", **r} for r in edge_rows]
    for s in sc.SCALES:
        st = {float(R): {"e": r["e"], "lb": r["lb_widened"]} for r in edge_rows for R in sc.RR_GATE
              if r["scale"] == s and r["R"] == R}
        df, passed = sc.run_gate(sc.blocks(table, days, s, "v"), st)
        g = df[df["is_gate_row"]].iloc[0]
        k = sc.kill_lines(df, passed)
        rows.append({"section": "gate", "scale": s, "outcome": "v", "N": n, "alpha_used": hc.ALPHA / n,
                     "gate_passed": bool(passed), "median_log_growth": float(g["median_log_growth"]),
                     "median_combine_days_resolved": k["median_combine_days_resolved"],
                     "kill_line_1": k["kill_line_1"], "kill_line_2": k["kill_line_2"], "killed": k["killed"],
                     **{f"lb_widened_R{int(R)}": st[float(R)]["lb"] for R in sc.RR_GATE}})
    out = pd.DataFrame(rows)
    write_result(out, "im2_development_haircut", script=SCRIPT, seed=sc.SEED, prereg_id=PREREG,
                 results_dir=results_dir,
                 provenance={"engine": engine_pin(), "ledger_sha256": sha256_of(led_file)},
                 parameters={"N": n, "k": count["k"], "pool": count["pool"],
                             "ledger_rows": [{"id": rid, "trials": t, "markets": ms} for rid, t, ms in count["rows"]],
                             "alpha": hc.ALPHA, "boot_len": sc.BOOT_LEN, "reps": sc.REPS, "round_turn": rt,
                             "days": len(days), "decision": "D-189, D-208"},
                 notes={"status": "reported beside P-04's registered verdict, never replacing it (D-189)"},
                 description="D-189's haircut beside IM2's development verdict: per R and scale e's lower bound at "
                             "one-sided 0.05/N (N from prereg/models.yaml), the daily series' deflated Sharpe ratio, "
                             "and the D-145 gate with each R at its widened bound. Reported only.")
    pd.set_option("display.width", 250)
    print(f"N = {n} (k {count['k']} plus {len(count['rows'])} ledger rows, pool {count['pool']})")
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
