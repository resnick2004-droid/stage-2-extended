"""L5, the planted effect (D-195), and the power curve D-192 reads from it.

    python scripts/l5_planted_effect.py --part chain
    python scripts/l5_planted_effect.py --part curve

Each part writes one file, so run them one at a time from a clean tree, committing the first before the second: a
manifest records the tree as dirty while another result file is uncommitted (`results.git_commit`).

1. **The chain** (`propedge/research/planted_effect.py`): synthetic sessions for ES, CL, 6E and NG through the kit's
   core, the IM2 scorer and the D-145 gate, both scales. Driftless sessions (noise) must leave e's lower bound at or
   below zero at R = 1 and 2 and the gate failing; the planted trend must give a bound above zero at both and the gate
   passing. A weak trend between them is reported, not judged. results/l5_planted_effect.csv.
2. **The power curve**: brackets with a planted e through the registered statistic (`im2_score.edge`), the share of
   replications whose lower bound is above zero, per R, e and trade count; e = 0 is the false-positive rate.
   results/l5_power_curve.csv.

Both manifests carry the engine pin (D-180): a verdict is citable only when L5 passed against the same engine files
(D-195; `propedge/reporting/trace.py`). Rerun after any change to an engine file. Takes several minutes.
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
from propedge.research import im2_score as sc  # noqa: E402
from propedge.research import planted_effect as pe  # noqa: E402

SCRIPT = "scripts/l5_planted_effect.py"
#: (drift in steps a minute, what the chain must do): noise must not pass; the planted trend must; the weak one is read
CASES = ((0.0, "noise: lower bound <= 0 and the gate fails"), (0.05, "weak: reported"),
         (0.15, "planted: lower bound > 0 and the gate passes"))
N_DAYS, N_PATHS, HORIZON = 500, 100, sc.HORIZON
#: the power curve's grid: planted e per R, trades, a trade a day; 200 replications of 2,000 bootstrap draws each
EFFECTS = (0.0, 0.025, 0.05, 0.10, 0.15, 0.20, 0.30)
TRADES = (250, 500, 1000, 2000, 4000)
RATE, REPLICATIONS, CURVE_BOOT_REPS = 1.0, 200, 2000


def _judge(case: str, rows: list[dict], passed: bool) -> bool:
    if case.startswith("noise"):
        return all(r["lb"] <= 0 for r in rows) and not passed
    if case.startswith("planted"):
        return all(r["lb"] > 0 for r in rows) and passed
    return True


def main(part: str = "both", results_dir: Path | None = None) -> int:
    warnings.filterwarnings("ignore")
    pin = engine_pin()
    ok = True
    if part in ("both", "chain"):
        ok = chain(pin, results_dir)
    if part in ("both", "curve"):
        curve(pin, results_dir)
    return 0 if ok else 1


def chain(pin: dict, results_dir: Path | None = None) -> bool:
    rows, ok = [], True
    for drift, case in CASES:
        got, gate_passed = pe.score_chain(drift, n_days=N_DAYS, seed=pe.SEED, n_paths=N_PATHS, horizon_days=HORIZON)
        judged = _judge(case, got, gate_passed)
        ok = ok and judged
        rows += [{**r, "case": case, "case_passed": judged} for r in got]
        print(f"drift {drift}: {case} -> {'ok' if judged else 'FAILED'}")
    df = pd.DataFrame(rows)
    write_result(df, "l5_planted_effect", script=SCRIPT, seed=pe.SEED, results_dir=results_dir,
                 provenance={"engine": pin},
                 parameters={"cases": [list(c) for c in CASES], "n_days": N_DAYS, "n_paths": N_PATHS,
                             "horizon_days": HORIZON, "boot_reps": sc.REPS, "boot_len": sc.BOOT_LEN, "passed": ok,
                             "layer": "L5", "decision": "D-195"},
                 description="L5 (D-195): synthetic sessions with and without a planted trend through the kit's core, "
                             "the IM2 scorer and the D-145 gate at both scales: noise must not pass, the planted "
                             "trend must.")
    print(df.to_string(index=False))
    print(f"\nL5 planted effect: {'PASS' if ok else 'FAIL'}")
    return ok


def curve(pin: dict, results_dir: Path | None = None) -> None:
    cells = [pe.power_cell(e, R, n, rate=RATE, replications=REPLICATIONS, reps=CURVE_BOOT_REPS,
                           seed=pe.SEED + 100_000 * i + 1_000 * j)
             for i, (R, e) in enumerate((R, e) for R in sc.RR_GATE for e in EFFECTS) for j, n in enumerate(TRADES)]
    df = pd.DataFrame(cells)
    write_result(df, "l5_power_curve", script=SCRIPT, seed=pe.SEED, results_dir=results_dir,
                 provenance={"engine": pin},
                 parameters={"effects": list(EFFECTS), "trades": list(TRADES), "rate_per_day": RATE,
                             "replications": REPLICATIONS, "boot_reps": CURVE_BOOT_REPS, "boot_len": sc.BOOT_LEN,
                             "statistic": "im2_score.edge: the lower of the 20-day moving-block bootstrap and the "
                                          "day-clustered normal bound (D-197)", "outcomes": "binary brackets at R",
                             "layer": "L5", "decision": "D-192, D-195"},
                 description="D-192: the power of the registered lower bound to clear zero, per R, planted e and trade "
                             "count (binary brackets, a trade a day); e = 0 is the false-positive rate.")
    print(df.pivot_table(index=["R", "e"], columns="trades", values="power").to_string())


def _cli(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--part", choices=("chain", "curve", "both"), default="both",
                    help="the chain's check or the power curve; one at a time keeps each manifest clean")
    return main(part=ap.parse_args(argv).part)


if __name__ == "__main__":
    raise SystemExit(_cli())
