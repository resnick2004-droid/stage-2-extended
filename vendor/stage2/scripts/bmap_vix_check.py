"""EXPLORATORY: does the previous session's VIX tell which days a session-scale bracket completes? (D-149 follow-up;
the check that decides whether an implied-volatility data service is worth a trial.)

    python scripts/bmap_vix_check.py

For the bracket map's entries at 08:35 CT (the whole session ahead), at the session-scale stop (0.4 of D), on
2009-2014 (the span the atlas's VIX covers, R040): VIX relative to its trailing 120-session median, known at the
previous close, in terciles; per tercile, the share of entries that hit the stop, reach 1:1, reach 3:1, or are still
open at 15:00, and the mean R net at 1:1 and 3:1. Writes results/bmap_vix_check.csv. Nothing here is a test.
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

from propedge.execution.fills import FillModel  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import bmap_score as bs  # noqa: E402

WI = 2          # the session-scale stop, 0.4 of D
T = 35          # 08:35 CT


def main() -> int:
    cfg = yaml.safe_load((ROOT / "config" / "bracket_map.yaml").read_text(encoding="utf-8"))
    fm = FillModel.load("assumed")
    vix = read_result(ROOT / "results" / "manual_R040_atlas_context2.csv")
    vix["date"] = pd.to_datetime(vix["d"].astype(int).astype(str), format="%Y%m%d")
    vix = vix.sort_values("date")
    vix["vix_rel"] = vix["vix"] / vix["vix"].rolling(120, min_periods=60).median()
    vix["vix_rel_prev"] = vix["vix_rel"].shift(1)            # known at the previous close
    rows = []
    for market in ("NQ", "ES"):
        mk = cfg["markets"][market]
        fills = {"target": fm.target_slippage_ticks, "stop": fm.stop_slippage_ticks,
                 "flatten": fm.flatten_slippage_ticks, "round_turn": float(mk["round_turn"]),
                 "tick_value": float(mk["tick_value"])}
        _, ent = bs.split(read_result(ROOT / "results" / f"manual_{cfg['runs'][market][0].replace('-', '_')}.csv"))
        ent = ent[ent["t"] == T].merge(vix[["date", "vix_rel_prev"]], on="date", how="inner").dropna(subset=["vix_rel_prev"])
        cuts = ent.drop_duplicates("date")["vix_rel_prev"].quantile([1 / 3, 2 / 3]).to_numpy()
        ent["tercile"] = np.select([ent["vix_rel_prev"] < cuts[0], ent["vix_rel_prev"] < cuts[1]], ["low", "mid"], "high")
        for terc, g in ent.groupby("tercile"):
            o1, o3 = bs.outcome(g, WI, 1.0, fills), bs.outcome(g, WI, 3.0, fills)
            rows.append({"market": market, "vix_rel_tercile": terc, "entries": len(g), "days": g["date"].nunique(),
                         "stop_rate": float((g[f"hit{WI}"] >= 1).mean()),
                         "reach_1to1": float((g[f"mfe{WI}"] > 1.0).mean()),
                         "reach_3to1": float((g[f"mfe{WI}"] > 3.0).mean()),
                         "open_at_15": float(((g[f"hit{WI}"] == 0) & (g[f"mfe{WI}"] <= 1.0)).mean()),
                         "e_1to1": float(o1["r_net"].mean()), "e_3to1": float(o3["r_net"].mean()),
                         "vix_rel_cut_low": float(cuts[0]), "vix_rel_cut_high": float(cuts[1])})
    out = pd.DataFrame(rows)
    write_result(out, "bmap_vix_check", script="scripts/bmap_vix_check.py", seed=None, require_seed=False,
                 exploratory=True, parameters={"width": bs.WIDTHS[WI], "time_ct": "08:35", "vix": "R040, prior close, "
                                               "relative to its trailing 120-session median", "span": "2009-2014"},
                 notes={"decision": "D-149 follow-up", "status": "EXPLORATORY: terciles cut on the sample itself"},
                 description="Session-scale brackets at 08:35 by the previous session's relative VIX: stop, 1:1 and "
                             "3:1 reach, still open at 15:00, mean R net.")
    pd.set_option("display.width", 200)
    print(out.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
