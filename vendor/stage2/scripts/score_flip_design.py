"""EXPLORATORY (D-375): the flip design map's choice -- the 08:30 flip's width and box, its side set by A3 (D-374:
follow the last sixty minutes' move) -- by the rule fixed in config/flip_design.yaml before its data was read.

    python scripts/score_flip_design.py          # reads results/manual_R144_flipdesign_NQ.csv

For each width (points) and box (minutes) and each day with a side: the side's bracket is RESOLVED when it reached its
target or stop within the box (its seconds to resolution at most the box), else SCRATCHED at the box's end at the
recorded mark (less a tick at entry and at exit). Dollars at the width's contract count (config/flip_sizing.yaml's
rule, D-346): +width or -width points, or the scratch, at $2 a point a micro; less the cost -- the MNQ round turn
(config/fills.yaml), the entry spread beyond the walk's tick at 08:30 (the minute flip map's spread rows), and a tick
on a stop exit. **The rule:** among the (width, box) whose risk is at most the operator's $200 and whose on-time
brackets resolve inside the box at least 90 % of the time on CHOICE pooled and in each CHOICE year, the highest mean
net dollars per attempt on CHOICE with A3's side; ties to the shorter box, then the narrower width. CHECK reports the
chosen flip's resolution, win share, mean net dollars and its one-sided 95 % Newey-West lower bound (lag 5).

Beside: every (width, box) on both spans with A3's side and with the mechanical side (the last minute's candle,
D-343), the late entry at the thirty-minute box, and the chosen flip's shares and cost on CHOICE -- the inputs a funded
table's flip action needs. Writes results/flip_design_nq.csv with its manifest; each (width, box) evaluated is recorded
in results/variants.jsonl (family flip_design, D-375).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from score_flip_direction import _sign, nw_se  # noqa: E402

SCRIPT = "scripts/score_flip_design.py"
CONFIG = ROOT / "config" / "flip_design.yaml"
RUN = "R144-flipdesign-NQ"
Z95 = 1.6448536269514722


def side_of(df: pd.DataFrame, rule: str) -> np.ndarray:
    """+1, -1 or 0 per day: `a3` follows the last sixty minutes' move (m60), `mechanical` the last minute's body (b1)."""
    col = {"a3": "m60", "mechanical": "b1"}[rule]
    return np.array([_sign(x) for x in df[col].astype(float)])


def outcomes(df: pd.DataFrame, side: np.ndarray, width: float, box_min: int, tick: float, delay: int = 0) -> pd.DataFrame:
    """Per day with a side and both on-time brackets entered: the kind ('t', 's' inside the box, 'x' scratched at the
    box's end), the points (+width, -width, or the scratch), the date."""
    lab = f"w{width:g}"
    cl, cs = f"o_{lab}_d{delay}_L", f"o_{lab}_d{delay}_S"
    ok = (side != 0) & (df[cl] != "-").to_numpy() & (df[cs] != "-").to_numpy()
    d, sd = df[ok], side[ok]
    kind = np.where(sd > 0, d[cl].to_numpy(), d[cs].to_numpy())
    if delay == 0:
        units = np.where(sd > 0, d[f"u_{lab}_L"].astype(float).to_numpy(), d[f"u_{lab}_S"].astype(float).to_numpy())
        resolved = np.isin(kind, ["t", "s"]) & (units <= box_min * 60 + 1e-9)
        mark = d[f"mark_{box_min * 60}"].astype(float).to_numpy()
        x_pts = (sd * mark - 2.0) * tick
    else:                                    # the late entry: its walk's own thirty-minute box only, no marks
        resolved = np.isin(kind, ["t", "s"])
        x_pts = np.zeros(len(kind))
    k = np.where(resolved, kind, "x")
    pts = np.where(k == "t", width, np.where(k == "s", -width, x_pts))
    return pd.DataFrame({"date": d["date"].to_numpy(), "year": d["year"].to_numpy(), "kind": k, "points": pts,
                         "scratch_nan": (k == "x") & ~np.isfinite(pts)})


def cell(o: pd.DataFrame, width: float, n: int, fee: float, spread_ticks: float, tick: float) -> dict:
    """Shares and dollars for one (width, box, side, span): at n micros ($2 a point each), the round turn, the spread
    beyond the walk's tick and a tick on a stop exit; mean net dollars per attempt and its NW one-sided lower bound."""
    tick_d = n * 2.0 * tick
    risk = n * 2.0 * width
    pts = np.nan_to_num(o["points"].to_numpy(float))
    stop = (o["kind"] == "s").to_numpy()
    net = n * 2.0 * pts - n * fee - max(0.0, spread_ticks - 1.0) * tick_d - stop * tick_d
    m = len(net)
    if not m:
        return {"n": 0}
    se = nw_se(net)
    years = o.groupby("year")["kind"].apply(lambda k: float((k != "x").mean()))
    return {"n": int(m), "contracts": int(n), "risk_dollars": risk, "resolved": float((o["kind"] != "x").mean()),
            "resolved_worst_year": float(years.min()), "target_share": float((o["kind"] == "t").mean()),
            "stop_share": float(stop.mean()), "scratch_share": float((o["kind"] == "x").mean()),
            "scratch_mean_dollars": float((n * 2.0 * pts)[(o["kind"] == "x").to_numpy()].mean()) if (o["kind"] == "x").any() else 0.0,
            "cost_dollars": float(n * fee + max(0.0, spread_ticks - 1.0) * tick_d + stop.mean() * tick_d),
            "net_mean": float(net.mean()), "net_lb": float(net.mean() - Z95 * se) if se == se else float("nan"),
            "net_r": float(net.mean() / risk), "net_lb_r": float((net.mean() - Z95 * se) / risk) if se == se else float("nan")}


def spread_at(spread_rows: pd.DataFrame, years) -> float:
    """The 08:30 entry's mean two-sided spread in ticks over `years`, weighted by quotes (the minute flip map's rows)."""
    s = spread_rows[(spread_rows["decision_ct"].astype(str) == "08:30") & spread_rows["year"].isin(list(years))]
    q = s["quotes"].astype(float)
    return float((s["spread_ticks_mean"].astype(float) * q).sum() / q.sum()) if q.sum() else float("nan")


def score(df: pd.DataFrame, cfg: dict, sizing: dict, fee: float, spread_rows: pd.DataFrame) -> pd.DataFrame:
    from propedge.data import flip_kit as fk

    import score_flip_map as sfm

    q = fk.params_design(cfg)
    tick = float(q["tick"])
    df = df.sort_values("date").reset_index(drop=True)
    ch, ck = cfg["periods"]["choice"], cfg["periods"]["check"]
    spans = {"choice": ((df["date"] >= ch[0]) & (df["date"] <= ch[1])).to_numpy(),
             "check": ((df["date"] >= ck[0]) & (df["date"] <= ck[1])).to_numpy()}
    years = {p: sorted(set(df.loc[m, "year"])) for p, m in spans.items()}
    spread = {p: spread_at(spread_rows, years[p]) for p in spans}
    sides = {r: side_of(df, r) for r in ("a3", "mechanical")}
    rows = []
    for w in q["widths_points"]:
        n = sfm.contracts_for(w, sizing)
        for b in cfg["boxes_minutes"]:
            for rule, sd in sides.items():
                for p, m in spans.items():
                    o = outcomes(df[m], sd[m], w, int(b), tick)
                    rows.append({"section": "cell", "width_points": w, "box_minutes": int(b), "side_rule": rule,
                                 "period": p, "spread_ticks": spread[p], **cell(o, w, n, fee, spread[p], tick)})
    t = pd.DataFrame(rows)
    c = t[(t["side_rule"] == "a3") & (t["period"] == "choice")]
    ok = c[(c["risk_dollars"] <= float(cfg["max_risk_dollars"]) + 1e-9)
           & (c["resolved"] >= float(cfg["resolved_min"]) - 1e-12)
           & (c["resolved_worst_year"] >= float(cfg["resolved_min"]) - 1e-12)]
    verdict = {"section": "verdict", "qualifying": int(len(ok))}
    if len(ok):
        best = ok.sort_values(["net_mean", "box_minutes", "width_points"], ascending=[False, True, True]).iloc[0]
        w, b = float(best["width_points"]), int(best["box_minutes"])
        k = t[(t["width_points"] == w) & (t["box_minutes"] == b) & (t["side_rule"] == "a3") & (t["period"] == "check")].iloc[0]
        late = {}
        if b == max(cfg["boxes_minutes"]):
            for p, m in spans.items():
                o = outcomes(df[m], sides["a3"][m], w, b, tick, delay=int(q["delays"][1]))
                late[f"late_{p}_net_mean"] = cell(o, w, int(best["contracts"]), fee, spread[p], tick).get("net_mean")
        verdict.update({"chosen_width_points": w, "chosen_box_minutes": b, "contracts": int(best["contracts"]),
                        "risk_dollars": float(best["risk_dollars"]), "choice_net_mean": float(best["net_mean"]),
                        "choice_net_lb": float(best["net_lb"]), "check_net_mean": float(k["net_mean"]),
                        "check_net_lb": float(k["net_lb"]), "check_resolved": float(k["resolved"]),
                        "check_target_share": float(k["target_share"]), "check_stop_share": float(k["stop_share"]),
                        "positive_on_check": bool(k["net_lb"] > 0), **late})
    return pd.concat([t, pd.DataFrame([verdict])], ignore_index=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import yaml

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.contract.rules import load_rules
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("status") != "fixed":
        print("REFUSED: config/flip_design.yaml is not fixed.")
        return 2
    src = rd / f"manual_{RUN.replace('-', '_')}.csv"
    if not src.exists():
        print(f"REFUSED: {src.name} is not ingested; run the kit and scripts/ingest_flip_run.py first.")
        return 2
    sz = yaml.safe_load((ROOT / "config" / "flip_sizing.yaml").read_text(encoding="utf-8"))
    fm = FillModel.load("assumed")
    fee = float(fm.round_turn_by_instrument[str(sz["instrument"])])
    sizing = {"point_value": float(sz["point_value"]), "fee_per_contract": fee, "grid_dollars": float(sz["grid_dollars"]),
              "bar_dollars": float(load_rules().value(str(sz["bar"])))}
    spread_rows = read_result(rd / "manual_R137_flipmap_NQ.csv")
    spread_rows = spread_rows[spread_rows["kind"] == "spread"]
    out = score(read_result(src), cfg, sizing, fee, spread_rows)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for _, r in out[(out["section"] == "cell") & (out["side_rule"] == "a3") & (out["period"] == "choice")].iterrows():
        counter.record(prereg_id="D-375:flip_design", seed=0, exploratory=True,
                       params={"width_points": float(r["width_points"]), "box_minutes": int(r["box_minutes"]),
                               "side": "a3", "config": "config/flip_design.yaml", "run": RUN},
                       label=f"flip design: {r['width_points']:g} points, {int(r['box_minutes'])} minutes, A3 (D-375)")
    n_var = len({r["variant_id"] for r in counter.all() if r.get("prereg_id") == "D-375:flip_design"})
    write_result(out, "flip_design_nq", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, variant_count=n_var,
                 parameters={"config": "config/flip_design.yaml", "run": RUN, "sizing": "config/flip_sizing.yaml",
                             "fee_micro": fee, "spread_source": "results/manual_R137_flipmap_NQ.csv (08:30 spread rows)",
                             "decision": "D-375"},
                 notes={"status": "EXPLORATORY: the flip's design chosen by a declared rule on 2021-2023; its money is "
                                  "tested in the funded table against FV3-C by its own declaration"},
                 description="EXPLORATORY: the 08:30 flip's width and box with its side set by the last sixty minutes' "
                             "move (A3), chosen on 2021-2023 and checked on 2024 to June 2025: every (width, box) with "
                             "A3's side and the mechanical side, the chosen flip's shares, cost and money.")
    v = out[out["section"] == "verdict"].iloc[0]
    if "chosen_width_points" in v and v["chosen_width_points"] == v["chosen_width_points"]:
        print(f"chosen: {v['chosen_width_points']:g} points, {int(v['chosen_box_minutes'])} minutes, "
              f"{int(v['contracts'])} MNQ; CHECK net per attempt {v['check_net_mean']:+.2f} (lower bound "
              f"{v['check_net_lb']:+.2f}); positive on CHECK: {v['positive_on_check']}")
    else:
        print("no (width, box) qualifies by the rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
