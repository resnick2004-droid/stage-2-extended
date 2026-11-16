"""EXPLORATORY (D-246): the feasible geometry region -- which (stop, R, dollar risk) a Topstep account can trade on NQ and
ES today, before any edge is known.

    python scripts/geometry_region.py

An execution model's three constraints do not depend on its edge: its brackets must finish before the 15:10 flatten
(D-212's 98 %, overall and in every year), its stop must carry the state's dollar risk in whole micros under the
state's cap (at least 90 %, D-212; the caps D-201's), and its friction is a share of R that the edge must clear. This
reads them from the regime map's counts (R090 NQ, R091 ES; D-238) for 2020-2025 (development, D-237), so that when a
setup survives the screen (D-245, D-246) its measured edge selects a row, and an empty region shows before the search
which dollar risks cannot be reached.

* **Brackets**: the map's random-direction entries at the decision slots of each of the session-setup screen's six
  windows (from its start to the end of its span), both directions, at each fixed stop in points and R; the
  trailing-range stops beside, at their mean size.
* **Per state and dollar risk** -- stage one's pairs' risks, $300, $500, $750, $1,000 and $1,500, in the Combine
  (cap 37 micros), a funded account below +$2,000 (15) and above it (37) -- the micros = min(floor(risk / stop $),
  cap), the realised share of the risk, and whether it is sizeable (at least 90 %).
* **Finish**: the share resolved at the target or the stop overall and in the worst year; the share left open at the
  flatten reported as its own outcome (counted a full loss in every edge here, the conservative reading).
* **Friction** in R: D-238's cost per micro over the stop's dollars per micro (the round turn, the entry spread beyond
  the walk's tick, D-95's tick on a stop or flatten exit with the measured overshoot).
* **Feasible**: sizeable and finishing on 98 % overall and in every year.

Writes results/geometry_region.csv: `cell` rows and `summary` rows (per market, state, risk and R: the feasible stops
and windows, the least friction among them).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

SCRIPT = "scripts/geometry_region.py"
YEARS = (2020, 2025)
RESOLVED_MIN, RISK_MIN = 0.98, 0.90                       # D-212
RISKS = (300.0, 500.0, 750.0, 1000.0, 1500.0)             # stage one's pairs' risks (T5 2a, the lifecycle family)
STATES = (("combine", "combine"), ("funded_below_2000", "funded_below_2000"),
          ("funded_at_or_above_2000", "funded_at_or_above_2000"))
RUNS = {"NQ": "R090-regime-NQ", "ES": "R091-regime-ES"}


def cell_readings(cnt: pd.DataFrame, market: str, slots: list[int], fee: float, slip: dict) -> pd.DataFrame:
    """Per stop and R at the given slots, 2020-2025: brackets, finish overall and worst year, open share, mean stop in
    points and dollars per micro, friction in R."""
    from propedge.data.regime_kit import params
    from regime_then_now import cost_per_micro

    q = params(market)
    tick, pv = q["micro_tick"], q["micro_point_value"]
    x = cnt[(cnt["market"] == market) & cnt["year"].between(*YEARS) & cnt["decision_slot"].isin(slots)]
    c, sp = x[x["kind"] == "count"], x[x["kind"] == "spread"]
    qn = float(sp["spread_count"].sum())
    spread = float((sp["spread_ticks_mean"].astype(float) * sp["spread_count"].astype(float)).sum()) / qn if qn else \
        float("nan")
    rows = []
    r_max = max(q["rr"])
    for (kind, value), g in c.groupby(["stop_kind", "stop_value"]):
        ev = g[g["R"] == r_max]
        exits = int(ev["stop"].sum())
        over = float(ev["overshoot_ticks_sum"].sum()) / exits if exits else 0.0
        for R, gr in g.groupby("R"):
            n, t, s, o = (int(gr[k].sum()) for k in ("n", "target", "stop", "open"))
            if not n:
                continue
            by = gr.groupby("year")[["n", "target", "stop"]].sum()
            stop_ticks = float(gr["stop_ticks_sum"].sum()) / n
            inv = float(gr["inv_stop_sum"].sum()) / n
            cost = cost_per_micro(fee, tick * pv, spread, s / n, o / n, over, slip)
            rows.append({"stop_kind": kind, "stop_value": float(value), "R": float(R), "n": n,
                         "resolved_share": (t + s) / n, "worst_year_resolved": float(((by["target"] + by["stop"])
                                                                                     / by["n"]).min()),
                         "open_share": o / n, "stop_points": stop_ticks * tick, "stop_dollars": stop_ticks * tick * pv,
                         "friction_r": cost * inv / (tick * pv), "spread_ticks_mean": spread,
                         "overshoot_ticks_per_exit": over})
    return pd.DataFrame(rows)


def region(cnt: pd.DataFrame, caps: dict, fees: dict, slip: dict) -> pd.DataFrame:
    from propedge.data.regime_kit import params
    from propedge.data.setup_kit import params as setup_params

    rows = []
    for market in sorted(set(cnt["market"])):
        q, sq = params(market), setup_params(market)
        fee = float(fees[q["micro"]])
        for name, (start, span) in zip(sq["window_names"], sq["windows"]):
            slots = [t for t in q["times"] if start <= t < start + span]
            cr = cell_readings(cnt, market, slots, fee, slip)
            for _, r in cr.iterrows():
                for state, cap_state in STATES:
                    cap = int(caps.get((market, cap_state), 0))
                    for risk in RISKS:
                        micros = min(math.floor(risk / r["stop_dollars"]), cap) if r["stop_dollars"] > 0 else 0
                        realised = micros * r["stop_dollars"] / risk
                        sizeable = bool(realised >= RISK_MIN)
                        finishes = bool(r["resolved_share"] >= RESOLVED_MIN and r["worst_year_resolved"] >= RESOLVED_MIN)
                        rows.append({"section": "cell", "market": market, "window": name, "state": state,
                                     "cap_micros": cap, "risk_dollars": risk, **r.to_dict(), "micros": int(micros),
                                     "realised_risk_share": realised, "sizeable": sizeable, "finishes": finishes,
                                     "feasible": bool(sizeable and finishes)})
    return pd.DataFrame(rows)


def summarise(cells: pd.DataFrame) -> pd.DataFrame:
    rows = []
    fixed = cells[cells["stop_kind"] == "points"]
    for (market, state, risk, R), g in fixed.groupby(["market", "state", "risk_dollars", "R"]):
        f = g[g["feasible"]]
        best = f.sort_values("friction_r").head(1)
        rows.append({"section": "summary", "market": market, "state": state, "risk_dollars": risk, "R": R,
                     "feasible_cells": len(f),
                     "feasible_stops": ",".join(f"{v:g}" for v in sorted(set(f["stop_value"]))),
                     "feasible_windows": ",".join(sorted(set(f["window"]))),
                     "least_friction_r": float(best["friction_r"].iloc[0]) if len(best) else float("nan"),
                     "least_friction_stop": float(best["stop_value"].iloc[0]) if len(best) else float("nan"),
                     "least_friction_window": best["window"].iloc[0] if len(best) else ""})
    return pd.DataFrame(rows)


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    frames = [pd.read_csv(rd / f"manual_{r.replace('-', '_')}.csv", low_memory=False) for r in RUNS.values()
              if (rd / f"manual_{r.replace('-', '_')}.csv").exists()]
    if not frames:
        print("REFUSED: the regime map's NQ and ES runs (R090, R091) are not ingested.")
        return 2
    cnt = pd.concat(frames, ignore_index=True)
    band = pd.read_csv(rd / "stop_band.csv")
    caps = {(r["market"], r["state"]): int(r["cap_micros"]) for _, r in band.iterrows()}
    fm = FillModel.load("assumed")
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks, "flatten": fm.flatten_slippage_ticks}
    cells = region(cnt, caps, dict(fm.round_turn_by_instrument), slip)
    summary = summarise(cells)
    write_result(pd.concat([cells, summary], ignore_index=True), "geometry_region", script=SCRIPT, seed=None,
                 require_seed=False, exploratory=True, results_dir=results_dir,
                 parameters={"years": list(YEARS), "resolved_min": RESOLVED_MIN, "realised_risk_min": RISK_MIN,
                             "risks": list(RISKS), "states": [s for s, _ in STATES],
                             "size_caps": "results/stop_band.csv cap_micros", "runs": RUNS,
                             "windows": "config/session_setups.yaml", "slippage_ticks": slip,
                             "fees": dict(fm.round_turn_by_instrument), "decision": "D-246"},
                 notes={"status": "EXPLORATORY: D-246, the feasible geometry region read from the regime map's "
                                  "2020-2025 counts; it chooses nothing"},
                 description="EXPLORATORY: per market, window, stop, R, state and dollar risk -- the micros a stop buys "
                             "under the state's cap, whether it finishes before 15:10 on 98 % in every year, its "
                             "friction in R; per market, state, risk and R the feasible set. No seed: counts.")
    pd.set_option("display.width", 250)
    print(summary[summary["feasible_cells"] > 0][["market", "state", "risk_dollars", "R", "feasible_stops",
                                                  "least_friction_r", "least_friction_window"]]
          .round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
