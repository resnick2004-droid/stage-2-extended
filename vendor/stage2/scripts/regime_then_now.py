"""EXPLORATORY (T15; D-237, D-238): the whole-day regime map read then against now -- 2009-2019 beside 2020-2025.

    python scripts/regime_then_now.py

Reads the ingested regime-map runs R090-R094 (`results/manual_R09x_regime_<market>.csv`, `propedge/data/
regime_parser.py`'s table) and applies what D-238 fixed before any count was read. It describes; it chooses nothing,
and every cell counts in the trial ledger of any model later chosen from it (D-189).

* **Eras:** "then" is 2009-2019 (from June 2009), "now" 2020 to June 2025.
* **Per market, decision, stop and R, in each era** (`cell`, one row with both eras' columns): brackets; the share
  resolved at the target or the stop, overall and in the era's worst year; the target's share of the resolved (a
  no-edge description, not an edge); the minutes to resolution; the stop's mean size in points and dollars per micro;
  the share of stop exits that gapped and the mean overshoot per stop exit in ticks; the entry minute's mean spread;
  the cost per trade in R -- D-221's cost (the micro's round turn, the entry's measured spread beyond the tick the walk
  charged, D-95's tick on a stop exit and on the flatten by their shares) with the measured overshoot added to each stop
  exit, over the stop's dollars per micro (for a range stop, times the mean of 1 / stop); the whole micros stage one's
  Combine risk ($1,500 at 1:1) and funded risk ($750) buy at the mean stop, under the stop band's caps (D-201); and
  whether D-212's 98 % is met overall and in every year of the era.
* **Per 30-minute window** (`window`): mean volume and mean range (points) per day, each era, and now over then.
* **Per year** (`session`): full sessions, the mean session range in points and in dollars per micro, the mean daily
  volume, and the mean trailing range.
* **Per market, era, R and kind of stop** (`summary`): the cells meeting 98 % in every year of the era, and their
  decisions.

Writes results/regime_then_now.csv. A market not yet ingested is listed as missing.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/regime_then_now.py"
ERAS = {"then": (2009, 2019), "now": (2020, 2025)}
RESOLVED_MIN = 0.98                                   # D-212
RISKS = {"combine": (1500.0, "combine"), "funded": (750.0, "funded_below_2000")}   # stage one's legs; D-201's caps


def era_of(year: int) -> str | None:
    return next((e for e, (a, b) in ERAS.items() if a <= int(year) <= b), None)


def load_counts(results_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    from propedge.data.regime_kit import REGIME_RUNS

    frames, have = [], []
    for market, run_id in REGIME_RUNS.items():
        f = results_dir / f"manual_{run_id.replace('-', '_')}.csv"
        if f.exists():
            frames.append(pd.read_csv(f))
            have.append(market)
    return (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()), have


def cost_per_micro(fee: float, tick_dollars: float, spread_ticks: float, stop_share: float, open_share: float,
                   overshoot_ticks: float, slip: dict) -> float:
    """D-221's cost per bracket in dollars per micro, with the measured overshoot on each stop exit (D-238)."""
    entry_extra = max(spread_ticks - slip["entry"], 0.0) if np.isfinite(spread_ticks) else float("nan")
    return fee + tick_dollars * (entry_extra + (slip["stop"] + overshoot_ticks) * stop_share
                                 + slip["flatten"] * open_share)


def _era_cell(g: pd.DataFrame, spread: float, q: dict, fee: float, slip: dict, caps: dict, events: pd.DataFrame) -> dict:
    """One era's reading of a (decision, stop, R) cell. `events`: the same decision and stop at the largest R, whose
    stop count is the stop exits the gaps were measured on."""
    tick, pv = q["micro_tick"], q["micro_point_value"]
    tick_dollars = tick * pv
    n, t, s, o = (int(g[k].sum()) for k in ("n", "target", "stop", "open"))
    if not n:
        return {}
    by_year = g.groupby("year")[["n", "target", "stop"]].sum()
    yearly = (by_year["target"] + by_year["stop"]) / by_year["n"].where(by_year["n"] > 0)
    ev = int(events["stop"].sum())
    gapped, over = int(events["gapped"].sum()), float(events["overshoot_ticks_sum"].sum())
    over_per_exit = over / ev if ev else 0.0
    stop_ticks = float(g["stop_ticks_sum"].sum()) / n
    inv = float(g["inv_stop_sum"].sum()) / n                                     # mean of 1 / stop (ticks)
    cost = cost_per_micro(fee, tick_dollars, spread, s / n, o / n, over_per_exit, slip)
    stop_dollars = stop_ticks * tick_dollars
    out = {"n": n, "target": t, "stop": s, "open": o, "resolved_share": (t + s) / n,
           "worst_year": int(yearly.idxmin()), "worst_year_share": float(yearly.min()), "years": int(len(yearly)),
           "target_share_of_resolved": t / (t + s) if (t + s) else float("nan"),
           "mean_minutes": float(g["minutes_sum"].sum()) / (t + s) if (t + s) else float("nan"),
           "stop_points_mean": stop_ticks * tick, "stop_dollars_per_micro": stop_dollars,
           "stop_exits": ev, "gapped_share": gapped / ev if ev else float("nan"),
           "overshoot_ticks_per_exit": over_per_exit, "spread_ticks_mean": spread,
           "cost_dollars_per_micro": cost, "cost_r": cost * inv / tick_dollars,
           "meets_98_every_year": bool((t + s) / n >= RESOLVED_MIN and yearly.min() >= RESOLVED_MIN)}
    for leg, (risk, state) in RISKS.items():
        out[f"{leg}_micros"] = int(min(np.floor(risk / stop_dollars), caps.get((q["market"], state), 0)))
    return out


def score_cells(counts: pd.DataFrame, fees: dict, slip: dict, caps: dict) -> pd.DataFrame:
    from propedge.data.regime_kit import params

    c = counts[counts["kind"] == "count"].assign(era=lambda d: d["year"].map(era_of))
    s = counts[counts["kind"] == "spread"].assign(era=lambda d: d["year"].map(era_of))
    rows = []
    for market, cm in c.groupby("market"):
        q = params(market)
        fee, r_max = float(fees[q["micro"]]), max(q["rr"])
        sm = s[s["market"] == market]
        spreads = {}
        for (era, slot), sp in sm.groupby(["era", "decision_slot"]):
            cnt = float(sp["spread_count"].sum())
            spreads[(era, slot)] = (float((sp["spread_ticks_mean"] * sp["spread_count"]).sum()) / cnt if cnt
                                    else float("nan"))
        for (slot, si, R), g in cm.groupby(["decision_slot", "stop_index", "R"]):
            row = {"section": "cell", "market": market, "decision_slot": int(slot),
                   "decision_ct": g["decision_ct"].iloc[0], "stop_index": int(si),
                   "stop_kind": g["stop_kind"].iloc[0], "stop_value": float(g["stop_value"].iloc[0]), "R": float(R)}
            for era in ERAS:
                ge = g[g["era"] == era]
                ev = cm[(cm["decision_slot"] == slot) & (cm["stop_index"] == si) & (cm["R"] == r_max)
                        & (cm["era"] == era)]
                for k, v in _era_cell(ge, spreads.get((era, slot), float("nan")), q, fee, slip, caps, ev).items():
                    row[f"{era}_{k}"] = v
            rows.append(row)
    return pd.DataFrame(rows)


def score_windows(counts: pd.DataFrame) -> pd.DataFrame:
    from propedge.data.regime_kit import params

    w = counts[counts["kind"] == "window"].assign(era=lambda d: d["year"].map(era_of))
    rows = []
    for (market, win), g in w.groupby(["market", "window"]):
        tick = params(market)["micro_tick"]
        row = {"section": "window", "market": market, "window": int(win), "window_ct": g["window_ct"].iloc[0]}
        for era in ERAS:
            ge = g[g["era"] == era]
            days = float(ge["days"].sum())
            row[f"{era}_days"] = int(days)
            row[f"{era}_volume_per_day"] = float(ge["volume"].sum()) / days if days else float("nan")
            row[f"{era}_range_points_per_day"] = float(ge["range_ticks_sum"].sum()) * tick / days if days else float(
                "nan")
        for k in ("volume_per_day", "range_points_per_day"):
            row[f"now_over_then_{k}"] = row[f"now_{k}"] / row[f"then_{k}"] if row[f"then_{k}"] else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def score_sessions(counts: pd.DataFrame) -> pd.DataFrame:
    from propedge.data.regime_kit import params

    d = counts[counts["kind"] == "session"]
    rows = []
    for (market, year), g in d.groupby(["market", "year"]):
        q = params(market)
        tick, days, rdays = q["micro_tick"], float(g["days"].sum()), float(g["range_days"].sum())
        pts = float(g["range_ticks_sum"].sum()) * tick / days if days else float("nan")
        rows.append({"section": "session", "market": market, "year": int(year), "era": era_of(year),
                     "sessions": int(days), "session_range_points": pts,
                     "session_range_dollars_per_micro": pts * q["micro_point_value"],
                     "volume_per_day": float(g["volume"].sum()) / days if days else float("nan"),
                     "trailing_range_points": (float(g["trailing_range_ticks_sum"].sum()) * tick / rdays
                                               if rdays else float("nan"))})
    return pd.DataFrame(rows)


def summarise(cells: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (market, R, kind), g in cells.groupby(["market", "R", "stop_kind"]):
        for era in ERAS:
            ok = g[g.get(f"{era}_meets_98_every_year", pd.Series(False, index=g.index)).fillna(False).astype(bool)]
            rows.append({"section": "summary", "market": market, "R": float(R), "stop_kind": kind, "era": era,
                         "cells": len(g), "cells_meeting_98": len(ok),
                         "decisions_meeting_98": ",".join(sorted(set(ok["decision_ct"]))),
                         "stops_meeting_98": ",".join(f"{v:g}" for v in sorted(set(ok["stop_value"])))})
    return pd.DataFrame(rows)


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.regime_kit import MARKETS, REGIME_RUNS, config
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    counts, have = load_counts(rd)
    if counts.empty:
        print("REFUSED: no regime-map run is ingested yet (R090-R094).")
        return 2
    fm = FillModel.load("assumed")
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks, "flatten": fm.flatten_slippage_ticks}
    band = pd.read_csv(rd / "stop_band.csv")
    caps = {(r["market"], r["state"]): int(r["cap_micros"]) for _, r in band.iterrows()}
    cells = score_cells(counts, fm.round_turn_by_instrument, slip, caps)
    out = pd.concat([cells, score_windows(counts), score_sessions(counts), summarise(cells)], ignore_index=True)
    write_result(out, "regime_then_now", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"eras": {k: list(v) for k, v in ERAS.items()}, "resolved_min": RESOLVED_MIN,
                             "risks": {k: list(v) for k, v in RISKS.items()}, "slippage_ticks": slip,
                             "fees": dict(fm.round_turn_by_instrument), "size_caps": "results/stop_band.csv cap_micros",
                             "markets_ingested": have, "markets_missing": sorted(set(MARKETS) - set(have)),
                             "runs": {m: REGIME_RUNS[m] for m in have}, "grid": "config/regime_map.yaml",
                             "rr": config()["rr"], "decision": "D-237, D-238"},
                 notes={"status": "EXPLORATORY: T15, a description of 2009-2019 against 2020-2025 by rules fixed "
                                  "before the counts were read (D-238); it chooses nothing"},
                 description="EXPLORATORY: the whole-day regime map read then (2009-2019) against now (2020-2025): per "
                             "market, decision, stop and R the share of brackets resolved, the stop's size, gaps, "
                             "spread, cost in R and the micros the risk buys; per 30-minute window volume and range; "
                             "per year the session range. No seed: a deterministic reading of counts.")
    print(summarise(cells).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
