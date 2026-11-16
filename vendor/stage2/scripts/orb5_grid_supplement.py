"""ORB5's promised reported figures the screen left out (D-275; the audit of 2026-10-04): for the final selection of
`results/orb5_grid.csv`, per leg and per era (2009-2017, 2018 on, pooled) -- trades, trades a trading day, the hit
rate, e (the metric), its yearly-means bound, gross and net R, the flattened share, the skew of the metric per trade
and the median minutes from entry to the stop on stopped trades; beside them the out-of-sample trades' e and bound with
every trade costed at today's median cost (the audit's finding: the gate charged each era its own costs, D-271).

    python scripts/orb5_grid_supplement.py

Reads the same records as the screen, through its own classes (`scripts/score_orb5_grid.py`); a report beside a
closed verdict, never a verdict.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import score_orb5_grid as g5  # noqa: E402

SCRIPT = "scripts/orb5_grid_supplement.py"
ERAS = {"2009-2017": (2009, 2017), "2018-2025": (2018, 2025), "pooled": (2009, 2025)}


def final_cell(out: pd.DataFrame, cfg: dict) -> dict:
    f = out[out["section"] == "final"].iloc[0]
    rng = tuple(int(x) for x in str(f["ranges"]).split("+"))
    rv = None if pd.isna(f["rv_min"]) else float(f["rv_min"])
    i = list(cfg["search"]["stop_atr"]).index(float(f["stop_atr"]))
    return {"ranges": rng, "rv_min": rv, "i": i, "stop_atr": float(f["stop_atr"]), "last_fill_ct": f["last_fill_ct"],
            "last_fill_slot": g5.s3._ct_slot(f["last_fill_ct"]), "policy": f["missed_trigger"],
            "coordination": f["coordination"], "funded_rr": float(f["funded_rr"])}


def era_rows(grid: g5.Grid5, c: dict, leg: str, R: float, sessions: dict[int, float]) -> list[dict]:
    v = grid.views[c["policy"]]
    _, tr = g5.leg_stats(grid, v, c, R, np.array(sorted(sessions)))
    rows, cols, o = tr["rows"], tr["cols"], tr["o"]
    yr = grid.year[rows]
    out = []
    for era, (a, b) in ERAS.items():
        m = (yr >= a) & (yr <= b)
        met = tr["metric"][m]
        r, cc = rows[m], cols[m]
        stopped = o["stopped"][r, cc]
        mins = (o["exit"][r, cc] - v["slot"][r, cc])[stopped]
        days = sum(x for y, x in sessions.items() if a <= y <= b)
        means = pd.Series(met).groupby(yr[m]).mean()
        out.append({"section": "era", "leg": leg, "era": era, "trades": int(m.sum()),
                    "per_day": float(m.sum() / days) if days else np.nan,
                    "hit_rate": float((o["gross"][r, cc] > 0).mean()) if m.any() else np.nan,
                    "e_metric": float(met.mean()) if m.any() else np.nan, "bound": g5.bound(means),
                    "gross": float(o["gross"][r, cc].mean()) if m.any() else np.nan,
                    "net": float(o["net"][r, cc].mean()) if m.any() else np.nan,
                    "flat_share": float(o["flat"][r, cc].mean()) if m.any() else np.nan,
                    "skew": float(pd.Series(met).skew()) if m.sum() > 2 else np.nan,
                    "median_minutes_to_stop": float(np.median(mins)) if len(mins) else np.nan})
    return out


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = g5.config()
    out = read_result(rd / "orb5_grid.csv")
    m, sessions = g5.load(rd, ROOT / "runs")
    fm = FillModel.load("assumed")
    q = params("NQ")
    grid = g5.Grid5(m, cfg, float(fm.round_turn_by_instrument[q["micro"]]), q["micro_tick"] * q["micro_point_value"])
    c = final_cell(out, cfg)
    rows = []
    for leg, R in (("combine", float(cfg["fixed"]["combine"]["rr"])), ("funded", c["funded_rr"])):
        rows += era_rows(grid, c, leg, R, sessions)
    # the out-of-sample trades costed at today's median cost (D-271): each test year's selection from the screen's
    # walk-forward rows, every trade's gross less its cell's median cost on 2020 to June 2025
    wf = out[out["section"] == "walkforward"]
    per = {"combine": [], "funded": []}
    for _, w in wf.iterrows():
        cw = final_cell(pd.DataFrame([{**w.to_dict(), "section": "final"}]), cfg)
        y = int(w["test_year"])
        v = grid.views[cw["policy"]]
        for leg, R in (("combine", float(cfg["fixed"]["combine"]["rr"])), ("funded", cw["funded_rr"])):
            st, tr = g5.leg_stats(grid, v, cw, R, np.array(sorted(sessions)))
            mask = grid.year[tr["rows"]] == y
            per[leg] += [(y, x) for x in (tr["o"]["gross"][tr["rows"], tr["cols"]][mask] - st["today_cost"])]
    for leg, xs in per.items():
        t = pd.DataFrame(xs, columns=["year", "r"])
        rows.append({"section": "oos_today_cost", "leg": leg, "trades": int(len(t)),
                     "e_metric": float(t["r"].mean()) if len(t) else np.nan,
                     "bound": g5.bound(t.groupby("year")["r"].mean())})
    res = pd.DataFrame(rows)
    write_result(res, "orb5_grid_supplement", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters={"source": "results/orb5_grid.csv", "decision": "D-275"},
                 notes={"status": "the screen's promised reported figures, beside its closed verdict (KILL)"},
                 description="ORB5's final selection per leg and era (trades, trades a day, hit rate, e, bound, gross, "
                             "net, flattened share, skew, minutes to the stop) and the out-of-sample trades at "
                             "today's median cost. Deterministic, no seed.")
    pd.set_option("display.width", 250)
    print(res.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
