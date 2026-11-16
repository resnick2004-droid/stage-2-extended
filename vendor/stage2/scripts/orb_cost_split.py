"""EXPLORATORY diagnostic, written after ORB1's development reading (T15 item 9; D-249, D-250): the paper exit's trades
split into the move before any cost and the costs, per market and range -- the stage decomposition of a negative
reading (CLAUDE.md's failure protocol), choosing nothing.

    python scripts/orb_cost_split.py

The same trades as `scripts/score_orb_dev.py`'s paper exit (FOMC days dropped, a direction, relative volume at least
100 %, a fill; 2009-2019 only): `gross_r` is the trade in R with no fee and no slippage at all (the entry's tick, which
the kit puts in the fill, added back); `entry_tick_r` that tick in R; `exit_cost_r` the round-turn fee and the exit's
slippage in R; `net_r` the scorer's trade. Each with the yearly estimates' one-sided 95 % lower bound where it is an
edge. The stop is ORB1's (10 % of the 14-day ATR), so the costs in R are set by the stop's ticks, not by the size.

Writes results/orb_cost_split.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

import score_orb_dev as so  # noqa: E402
from propedge.outcomes.orb_core import OR_MINS  # noqa: E402

SCRIPT = "scripts/orb_cost_split.py"


def split(d: pd.DataFrame, cfg: dict, fees: dict, slip: float, flat_slip: float) -> list[dict]:
    from propedge.data.orb_kit import params

    rv_min = float(cfg["fixed"]["relative_volume"]["min"])
    x = d[(d["dir"] != 0) & (d["rv100"] >= 100 * rv_min)]
    parts = []
    for market, g in x.groupby("market"):
        q = params(market, cfg)
        td = q["micro_tick"] * q["micro_point_value"]
        gross = so.trade_r(g, td, 0.0, 0.0, None, (), 0.0)
        net = so.trade_r(g, td, float(fees[q["micro"]]), slip, None, (), flat_slip)
        t = gross[["market", "year", "or_minutes", "stop_ticks"]].copy()
        t["entry_tick_r"] = 1.0 / gross["stop_ticks"]
        t["gross_r"] = gross["r"] + t["entry_tick_r"]
        t["net_r"] = net["r"]
        t["exit_cost_r"] = t["gross_r"] - t["entry_tick_r"] - t["net_r"]
        t["stop_dollars"] = gross["stop_ticks"] * td
        parts.append(t)
    t = pd.concat(parts)
    rows = []
    for n in OR_MINS:
        for scope in sorted(t["market"].unique()) + ["both"]:
            s = t[(t["or_minutes"] == n) & ((t["market"] == scope) if scope != "both" else True)]
            yg, yn = s.groupby("year")["gross_r"].mean(), s.groupby("year")["net_r"].mean()
            rows.append({"or_minutes": n, "market": scope, "n": len(s),
                         "median_stop_ticks": float(s["stop_ticks"].median()),
                         "median_stop_dollars_per_micro": float(s["stop_dollars"].median()),
                         "gross_r": float(s["gross_r"].mean()), "gross_lower_bound": so.bound(yg),
                         "years_gross_above_zero": int((yg > 0).sum()), "years": len(yg),
                         "entry_tick_r": float(s["entry_tick_r"].mean()), "exit_cost_r": float(s["exit_cost_r"].mean()),
                         "net_r": float(s["net_r"].mean()), "net_lower_bound": so.bound(yn)})
    return rows


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.orb_kit import MARKETS, config
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    d, have = so.load(rd)
    if d.empty or set(have) != set(MARKETS) or (d["year"] > so.DEV_END).any():
        print("REFUSED: both development runs, 2009-2019 only, are needed (D-249).")
        return 2
    d = d[~d["date"].astype(str).isin(so.fomc_dates())]
    fm = FillModel.load("assumed")
    rows = split(d, config(), dict(fm.round_turn_by_instrument), float(fm.stop_slippage_ticks),
                 float(fm.flatten_slippage_ticks))
    out = pd.DataFrame(rows)
    write_result(out, "orb_cost_split", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"config": "config/orb_model.yaml", "years": [2009, so.DEV_END], "exit": "paper",
                             "fees": dict(fm.round_turn_by_instrument),
                             "exit_slippage_ticks": float(fm.stop_slippage_ticks),
                             "flatten_slippage_ticks": float(fm.flatten_slippage_ticks), "decision": "D-252"},
                 notes={"status": "EXPLORATORY: a decomposition written after ORB1's development reading; it "
                                  "chooses nothing"},
                 description="EXPLORATORY: ORB1's paper-exit trades, 2009-2019, split into the move before any cost "
                             "and the costs in R, per market and range. No seed: a deterministic reading.")
    pd.set_option("display.width", 250)
    print(out.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
