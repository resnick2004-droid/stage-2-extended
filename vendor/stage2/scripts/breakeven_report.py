"""The break-even hit rate beside IM2's development verdict (D-201 (1)), per market and R at both scales.

    python scripts/breakeven_report.py

A companion to `scripts/score_im2.py`, which it leaves unchanged (its files are pinned, D-180): it builds the same
entry table from the ingested development runs R053-R060 and the same fees -- so it refuses, as the scorer does,
before the 2026-10-01 re-read of the MCL and MNG round turns and unless P-04 is runnable -- and writes
results/im2_development_breakeven.csv: the cost drag c, p* = (1 + c) / (1 + r), the target-hit rate with its D-197
lower bound, the share of time exits, the hit rate among the other trades and the time exits' mean R
(`propedge/research/breakeven_rate.py`). Descriptive: the verdict is the gate's.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge.backtest.harness import PreregRegistry  # noqa: E402
from propedge.data.qc_algorithms import IM2_RUNS, im2_params  # noqa: E402
from propedge.reporting.pin import engine_pin  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402
from propedge.research import breakeven_rate as br  # noqa: E402
from propedge.research import im2_score as sc  # noqa: E402

SCRIPT = "scripts/breakeven_report.py"
PREREG = "P-04"


def development_table(cfg: dict, rt: dict) -> tuple[pd.DataFrame, list[str]]:
    """IM2's development entry table and day set, as `scripts/score_im2.py` builds them."""
    specs = sc.micro_specs(cfg)
    sessions, tails, tables = {}, {}, []
    for m in sc.MARKETS:
        parts_s, parts_e, tail = [], [], []
        for (mk, _), rid in sorted(IM2_RUNS.items()):
            if mk == m:
                days, ent, t = sc.read_run(rid)
                parts_s.append(days)
                parts_e.append(ent)
                tail += t
        sessions[m], tails[m] = pd.concat(parts_s, ignore_index=True), tail
        tables.append(sc.entry_table(m, sessions[m], pd.concat(parts_e, ignore_index=True), round_turn=rt[m],
                                     spec=specs[m], cfg=cfg))
    return pd.concat(tables, ignore_index=True), sc.day_set(sessions, tails, *sc.DEVELOPMENT)


def main(registry: Path | None = None, results_dir: Path | None = None) -> int:
    warnings.filterwarnings("ignore")
    PreregRegistry.load(registry).require_runnable(PREREG)
    cfg = sc.config()
    rt = sc.fees(cfg)                                   # refuses before the 2026-10-01 re-read (P-04 §3)
    table, days = development_table(cfg, rt)
    specs = sc.micro_specs(cfg)
    fills = {m: im2_params(m)["fills"] for m in sc.MARKETS}
    tick_values = {m: specs[m]["tick_value"] for m in sc.MARKETS}
    rows = [r for s in sc.SCALES for r in br.im2_rows(table, days, s, fills=fills, tick_values=tick_values,
                                                      round_turns=rt, seed=sc.SEED)]
    df = pd.DataFrame(rows)
    write_result(df, "im2_development_breakeven", script=SCRIPT, seed=sc.SEED, prereg_id=PREREG,
                 results_dir=results_dir, provenance={"engine": engine_pin()},
                 parameters={"round_turn": rt, "boot_len": br.BOOT_LEN, "reps": br.REPS, "days": len(days),
                             "decision": "D-201 (1)"},
                 description="D-201 (1): IM2's break-even hit rate beside its development verdict, per market, R and "
                             "scale: cost drag c, p* = (1 + c) / (1 + r), the target-hit rate with its D-197 lower "
                             "bound, the time-exit share, the hit rate among the other trades and the time exits' "
                             "mean R. Descriptive; the verdict is the gate's.")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
