"""The bracket map's outcome check (config/bracket_map.yaml `analysis.outcome_check`, D-149/D-150).

    python scripts/bmap_gate_check.py

Every screen cell that held on the check, and the unconditional entry at the same geometry, time and side, through
the D-145 campaign gate with its own outcomes. Writes results/bmap_gate_check.csv (EXPLORATORY).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.campaign.breakeven import TieredProtocol  # noqa: E402
from propedge.campaign.gate import GATE_ENFORCEMENT_P, run_gate  # noqa: E402
from propedge.campaign.payout_method import rules_for_method  # noqa: E402
from propedge.campaign.sizing import FIXED_RISK, SizingRule  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import bmap_score as bs  # noqa: E402

SCRIPT = "scripts/bmap_gate_check.py"
SEED = 20261109
#: D-156: the bracket map records no MAE, so trades settle by the pessimistic bound; `--settlement legacy`
#: reproduces the pre-D-156 file (the optimistic bound, results/bmap_gate_check.csv).
SETTLEMENT = sys.argv[sys.argv.index("--settlement") + 1] if "--settlement" in sys.argv else "pessimistic"
TAG = "bmap_gate_check" + ("" if SETTLEMENT == "legacy" else "_d156")
BANKROLL, HORIZON, PATHS = 5_000.0, 504, 200
COMBINE_RISK = {0.5: 1000.0, 1.0: 1500.0, 1.5: 500.0, 2.0: 750.0, 3.0: 500.0, 5.0: 500.0}
COLUMN = {"fv_dist": "f_fv", "vwap_dist": "f_vwap", "last30": "f_last30", "range_so_far": "f_range", "gap": "gap",
          "prev_close_location": "clv", "weekday": "weekday"}


def _variant_params(out: pd.DataFrame) -> dict:
    """What the variant ledger records for one outcome check: the cells and the unconditional entries read."""
    keys = ["market", "width", "rr", "time_ct", "side"]
    return {"design": "config/bracket_map.yaml analysis.outcome_check", "cells": int(len(out)),
            "baselines": int(len(out.drop_duplicates(keys)))}


def _slot(hm: str) -> int:
    h, m = (int(x) for x in hm.split(":"))
    return h * 60 + m - 480


def _blocks(ent, day_ns, wi, k, fills, tick_value):
    o = bs.outcome(ent, wi, k, fills)
    rpc = ent[f"stop_ticks{wi}"].to_numpy(float) * tick_value
    df = pd.DataFrame({"n": ent["n"].to_numpy(), "r": o["r_net"].to_numpy(), "ok": o["ok"].to_numpy(), "rpc": rpc})
    df = df[df["ok"]]
    by = {n: g for n, g in df.groupby("n")}
    out = []
    for n in day_ns:
        g = by.get(n)
        if g is None:
            out.append(DayBlock(pnl=np.zeros(0), risked=np.zeros(0), exit_reasons=(), risk_per_contract=np.zeros(0)))
        else:
            out.append(DayBlock(pnl=g["r"].to_numpy() * g["rpc"].to_numpy(), risked=g["rpc"].to_numpy().copy(),
                                exit_reasons=("bracket",) * len(g), risk_per_contract=g["rpc"].to_numpy().copy()))
    s = bs.summarise(o, day_ns, block=20, reps=10_000, seed=SEED)
    return out, s


def _gate(blocks, s, k, name, rules, sizing):
    proto = TieredProtocol(name, combine_rr=k, combine_risk=COMBINE_RISK[k], funded_rr=k, funded_risk=750.0,
                           trades_per_day=max(1, max(len(b) for b in blocks)), family="bmap_gate_check")
    df, passed = run_gate(blocks, e=s["e"], lb=s["e_lb"], protocol=proto, bankroll=BANKROLL, horizon_days=HORIZON,
                          n_paths=PATHS, seed=SEED, accounts=1, sizing=sizing, rules=rules,
                          levels=(GATE_ENFORCEMENT_P,), settlement=SETTLEMENT,
                          mode="copier")                       # as declared and run before D-157
    g = df[df["is_gate_row"]].iloc[0]
    p = df[df["shift"] == "point"].iloc[0]
    return {"gate_passed": passed, "growth_lb": float(g["median_log_growth"]), "growth_point": float(p["median_log_growth"]),
            "ruin_lb": float(g["ruin_probability"]), "combines_bought_lb": float(g["mean_combine_purchases"])}


def main() -> int:
    from propedge.execution.fills import FillModel

    cfg = yaml.safe_load((ROOT / "config" / "bracket_map.yaml").read_text(encoding="utf-8"))
    rules = rules_for_method("aeropay")
    sizing = SizingRule.from_ledger(FIXED_RISK)
    fm = FillModel.load("assumed")
    rows = []
    for market, runs in cfg["runs"].items():
        mk = cfg["markets"][market]
        fills = {"target": fm.target_slippage_ticks, "stop": fm.stop_slippage_ticks,
                 "flatten": fm.flatten_slippage_ticks, "round_turn": float(mk["round_turn"]),
                 "tick_value": float(mk["tick_value"])}
        parts = [bs.split(read_result(ROOT / "results" / f"manual_{r.replace('-', '_')}.csv")) for r in runs]
        days = pd.concat([p[0].assign(n=p[0]["n"] + 100_000 * i) for i, p in enumerate(parts)], ignore_index=True)
        ent = pd.concat([p[1].assign(n=p[1]["n"] + 100_000 * i) for i, p in enumerate(parts)], ignore_index=True)
        ent["weekday"] = ent["date"].dt.weekday
        day_ns = days.loc[days["ok"], "n"].tolist()
        screen = read_result(ROOT / "results" / f"bmap_screen_{market}.csv")
        held = screen[screen["holds"].fillna(False).astype(bool)]
        baselines = {}
        for _, c in held.iterrows():
            wi = bs.WIDTHS.index(float(c["width"]))
            k = float(c["rr"])
            t, side = _slot(c["time_ct"]), (1 if c["side"] == "long" else -1)
            base_key = (wi, k, t, side)
            if base_key not in baselines:
                sub = ent[(ent["t"] == t) & (ent["side"] == side)]
                blocks, s = _blocks(sub, day_ns, wi, k, fills, float(mk["tick_value"]))
                baselines[base_key] = {"e": s["e"], "e_lb": s["e_lb"], "entries": s["entries"],
                                       **_gate(blocks, s, k, f"{market}_base", rules, sizing)}
            sub = ent[(ent["t"] == t) & (ent["side"] == side) & (ent[COLUMN[c["feature"]]] == int(c["bucket"]))]
            blocks, s = _blocks(sub, day_ns, wi, k, fills, float(mk["tick_value"]))
            gate = _gate(blocks, s, k, f"{market}_cell", rules, sizing)
            b = baselines[base_key]
            row = {"market": market, "feature": c["feature"], "bucket": int(c["bucket"]), "width": float(c["width"]),
                   "rr": k, "time_ct": c["time_ct"], "side": c["side"], "entries": s["entries"], "e": s["e"],
                   "e_lb": s["e_lb"], **gate, "base_entries": b["entries"], "base_e": b["e"], "base_e_lb": b["e_lb"],
                   "base_gate_passed": b["gate_passed"], "base_growth_lb": b["growth_lb"],
                   "base_growth_point": b["growth_point"]}
            row["counts"] = bool(row["gate_passed"] and row["growth_lb"] > row["base_growth_lb"])
            rows.append(row)
            print(f"[{market}] {c['feature']}={int(c['bucket'])} {c['time_ct']} {c['side']} w{c['width']} {k:g}:1 -> "
                  f"gate {'PASS' if gate['gate_passed'] else 'fail'} ({gate['growth_lb']:+.3f}); baseline "
                  f"{'PASS' if b['gate_passed'] else 'fail'} ({b['growth_lb']:+.3f}); counts {row['counts']}", flush=True)
    out = pd.DataFrame(rows)
    VariantCounter().record(prereg_id="T4:bracket_map:outcome_check", params=_variant_params(out), seed=SEED,
                            exploratory=True, label="D-149 outcome check of the screen's survivors, not a test")
    write_result(out, TAG, script=SCRIPT, seed=SEED, exploratory=True,
                 parameters={"design": "config/bracket_map.yaml analysis.outcome_check", "bankroll": BANKROLL,
                             "settlement": SETTLEMENT,
                             "horizon_days": HORIZON, "paths": PATHS, "combine_risk": {f"{k:g}": v for k, v in
                                                                                        COMBINE_RISK.items()},
                             "funded": "same R, $750", "sizing": "fixed dollar risk", "denial_p": GATE_ENFORCEMENT_P},
                 notes={"decision": "D-149 / D-150", "status": "EXPLORATORY: development data; a research screen's "
                        "follow-up, not a test", "assumed": "$5,000 and 504 days pending the operator"},
                 description="Every bracket-map cell that held on the check, and the unconditional entry at its "
                             "geometry, time and side, through the D-145 campaign gate with their own outcomes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
