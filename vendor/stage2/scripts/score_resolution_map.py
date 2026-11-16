"""EXPLORATORY (D-213 part 2; D-214, D-215, D-221): score the resolution map's counts -- which markets, decision times
and fixed stops let every leg of a no-edge arm resolve at its stop or target, never the 15:10 flatten, on at least 98 %
of brackets, at a cost per trade the contract absorbs?

    python scripts/score_resolution_map.py [--scale today]

`--scale today` (D-225, EXPLORATORY, chosen after D-224's reading): ES, NQ and CL read from their kits at today's price
level (R082-R087), the other markets from their development-scale runs, written to
results/resolution_map_score_today.csv beside D-224's file.

Reads the ingested kits R071-R080 (`results/manual_R0xx_rmap_<market>_<half>.csv`, `propedge/data/rmap_parser.py`'s
table) and part 1's break-even c* (`results/no_edge_contract.csv`, `results/no_edge_contract_added.csv`,
`results/no_edge_concurrency.csv`), and applies what D-214 and D-215 fixed before any count was read:

* **Resolution** per market, decision time, stop and R, on full sessions only (early closes are counted apart and
  reported, D-215): the share of brackets at the target or the stop, overall and in every year, at or above
  `feasible.resolved_share_min` (D-212's 2 %); 2014, split between the two halves, is summed before the per-year test.
* **Cost per trade** in R, per micro (D-221): the micro's round turn (`config/fills.yaml`) plus the entry's measured
  spread beyond the one micro tick the walk already charged (so the entry pays the measured spread once, at least one
  tick), plus D-95's one tick on a stop exit and on a flatten, weighted by their shares (a target is a resting limit,
  zero), all over the stop's dollars per micro. The spread is the decision time's mean over every year, weighted by
  its quote count.
* **An arm's legs** (D-221): each state's R and risk (`LEGS`); a leg's stop must divide its risk into whole micros
  (D-212) no more than its state's size cap (`results/stop_band.csv`'s `cap_micros`, D-201) and resolve as above at
  the leg's R with its cost below the arm's c*; an arm is feasible at a market and
  decision time when every leg has such a stop (the cheapest is reported). An arm with a leg at an R the map did not
  measure is reported as not mapped.
* **Part 2's arm** (D-214, D-217): among the arms read at the gate's placement timing (`rtp_warnings` 0, D-220), the
  one with the largest c* at denial 0 (D-213's reading) that is feasible somewhere; the 25 % reading beside it.

Writes results/resolution_map_score.csv, sections `cell` (market, decision, stop, R), `arm` (arm, denial, market,
decision) and `choice`. A market without both halves ingested is reported as missing and cannot be chosen.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/score_resolution_map.py"
# Each arm's legs: (state, R, risk in dollars, the stop band's state for its size cap), from its protocol
# (scripts/no_edge_contract.py `arm`; im2_score.policy's harvest leg). The concurrency arms share s1_zero_edge_static's
# geometry. A funded leg that runs below and above +$2,000 takes the smaller cap, below.
LEGS = {
    "s1_zero_edge_static": (("combine", 1.0, 1500.0, "combine"), ("funded", 2.0, 750.0, "funded_below_2000")),
    "im2_lifecycle": (("combine", 1.0, 1500.0, "combine"), ("build", 2.0, 1000.0, "funded_below_2000"),
                      ("harvest", 1.0, 300.0, "funded_at_or_above_2000")),
    "s1_low_edge": (("combine", 2.0, 750.0, "combine"), ("funded", 1.5, 1000.0, "funded_below_2000")),
    "s1_high_edge": (("combine", 1.5, 500.0, "combine"), ("funded", 1.5, 1000.0, "funded_below_2000")),
}
C_STAR_FILES = ("no_edge_contract.csv", "no_edge_contract_added.csv", "no_edge_concurrency.csv")


def load_counts(results_dir: Path, runs: dict | None = None) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Every ingested resolution-map table, and for each market the halves present. `runs`: (market, half) -> the run
    it is read from (`RMAP_RUNS` by default; `RMAP_TODAY_READ` at today's price level, D-225)."""
    from propedge.data.rmap_kit import RMAP_RUNS

    frames, halves = [], {}
    for (market, half), run_id in (runs or RMAP_RUNS).items():
        f = results_dir / f"manual_{run_id.replace('-', '_')}.csv"
        if f.exists():
            frames.append(pd.read_csv(f).assign(half=half))
            halves.setdefault(market, []).append(half)
    return (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()), halves


def c_stars(results_dir: Path) -> pd.DataFrame:
    """One row per arm and denial: c*, with the placement-timing reading (0 where the file has none)."""
    rows = []
    for name in C_STAR_FILES:
        f = results_dir / name
        if not f.exists():
            continue
        be = pd.read_csv(f)
        be = be[be["section"] == "break_even"]
        for _, r in be.iterrows():
            cap = r.get("combines_at_once")
            arm = r["arm"] if pd.isna(cap) else f"{r['arm']}@cap{int(cap)}"
            rows.append({"arm": arm, "geometry": r["arm"], "denial_p": float(r["denial_p"]),
                         "rtp_warnings": 0 if pd.isna(r.get("rtp_warnings")) else int(r["rtp_warnings"]),
                         "c_star": float(r["c_star"]), "source": name})
    return pd.DataFrame(rows)


def score_cells(counts: pd.DataFrame, cfg: dict, fees: dict, slip: dict) -> pd.DataFrame:
    """Per market, decision, stop and R: resolution overall and in its worst year (full sessions), the early-close
    share, the mean spread and the cost per trade in R."""
    from propedge.data.rmap_kit import params

    out = []
    c = counts[counts["kind"] == "count"]
    s = counts[counts["kind"] == "spread"]
    floor = float(cfg["feasible"]["resolved_share_min"])
    for market, cm in c.groupby("market"):
        q = params(market, cfg)
        tick_dollars = q["micro_tick"] * q["micro_point_value"]
        fee = float(fees[q["micro"]])
        sm = s[s["market"] == market]
        for (slot, stop, R), g in cm.groupby(["decision_slot", "stop_dollars", "R"]):
            full = g[g["day_type"] == "full"]
            early = g[g["day_type"] == "early"]
            n, t, st, o = (int(full[k].sum()) for k in ("n", "target", "stop", "open"))
            by_year = full.groupby("year")[["n", "target", "stop"]].sum()        # 2014's halves summed here
            yearly = (by_year["target"] + by_year["stop"]) / by_year["n"].where(by_year["n"] > 0)
            sp = sm[sm["decision_slot"] == slot]
            cnt = float(sp["spread_count"].sum())
            spread = (float((sp["spread_ticks_mean"] * sp["spread_count"]).sum()) / cnt) if cnt else float("nan")
            share = (t + st) / n if n else float("nan")
            cost_dollars = bracket_cost(fee, tick_dollars, spread, st / n if n else float("nan"),
                                        o / n if n else float("nan"), slip)
            out.append({"section": "cell", "market": market, "decision_slot": int(slot),
                        "decision_ct": g["decision_ct"].iloc[0], "stop_dollars": float(stop), "R": float(R),
                        "n": n, "target": t, "stop": st, "open": o, "resolved_share": share,
                        "worst_year": int(yearly.idxmin()) if yearly.notna().any() else -1,
                        "worst_year_share": float(yearly.min()) if yearly.notna().any() else float("nan"),
                        "years": int(yearly.notna().sum()),
                        "early_n": int(early["n"].sum()), "early_open": int(early["open"].sum()),
                        "mean_minutes": (float(full["minutes_sum"].sum()) / (t + st)) if (t + st) else float("nan"),
                        "spread_ticks_mean": spread, "spread_quotes": int(cnt),
                        "cost_dollars_per_micro": cost_dollars, "cost_r": cost_dollars / float(stop),
                        "resolves": bool(n and share >= floor and yearly.notna().all() and yearly.min() >= floor)})
    return pd.DataFrame(out)


def bracket_cost(fee: float, tick_dollars: float, spread_ticks: float, stop_share: float, open_share: float,
                 slip: dict) -> float:
    """D-221's cost per bracket in dollars per micro: the round turn, the entry's measured spread beyond the tick the
    walk already charged (never below zero), and D-95's tick on a stop exit and on the flatten, by their shares."""
    entry_extra = max(spread_ticks - slip["entry"], 0.0) if np.isfinite(spread_ticks) else float("nan")
    return fee + tick_dollars * (entry_extra + slip["stop"] * stop_share + slip["flatten"] * open_share)


def load_caps(results_dir: Path) -> dict[tuple[str, str], int]:
    """{(market, state): the most micros a state may hold} from the stop band (D-201)."""
    band = pd.read_csv(results_dir / "stop_band.csv")
    return {(r["market"], r["state"]): int(r["cap_micros"]) for _, r in band.iterrows()}


def score_arms(cells: pd.DataFrame, stars: pd.DataFrame, complete: set[str],
               caps: dict[tuple[str, str], int]) -> pd.DataFrame:
    """Per arm, denial, market and decision: each leg's cheapest feasible stop, and whether every leg has one."""
    out = []
    mapped_r = set(cells["R"]) if not cells.empty else set()
    for _, a in stars.iterrows():
        legs = LEGS[a["geometry"]]
        if any(r not in mapped_r for _, r, _, _ in legs):
            out.append({"section": "arm", "arm": a["arm"], "denial_p": a["denial_p"],
                        "rtp_warnings": a["rtp_warnings"], "c_star": a["c_star"], "market": "", "feasible": False,
                        "note": "not mapped: a leg's R is outside the map's rr"})
            continue
        for (market, slot), g in cells.groupby(["market", "decision_slot"]):
            row = {"section": "arm", "arm": a["arm"], "denial_p": a["denial_p"], "rtp_warnings": a["rtp_warnings"],
                   "c_star": a["c_star"], "market": market, "decision_slot": int(slot),
                   "decision_ct": g["decision_ct"].iloc[0], "note": "" if market in complete else "missing a half"}
            ok = market in complete
            worst = 0.0
            for state, r, risk, band_state in legs:
                micros = risk / g["stop_dollars"]
                cand = g[(g["R"] == r) & g["resolves"] & (g["cost_r"] < a["c_star"]) & (micros % 1 == 0)
                         & (micros <= caps.get((market, band_state), 0))].sort_values("cost_r")
                row[f"{state}_stop"] = float(cand["stop_dollars"].iloc[0]) if len(cand) else float("nan")
                row[f"{state}_cost_r"] = float(cand["cost_r"].iloc[0]) if len(cand) else float("nan")
                ok &= bool(len(cand))
                worst = max(worst, row[f"{state}_cost_r"]) if len(cand) else worst
            row["feasible"], row["max_leg_cost_r"] = bool(ok), worst if ok else float("nan")
            out.append(row)
    return pd.DataFrame(out)


def choose(arms: pd.DataFrame) -> dict:
    """D-214/D-217: the arm with the largest c* at denial 0, at the gate's placement timing, feasible somewhere."""
    f = arms[(arms["denial_p"] == 0.0) & (arms["rtp_warnings"] == 0) & arms["feasible"]]
    if f.empty:
        return {"section": "choice", "arm": "", "c_star": float("nan"), "feasible_cells": 0,
                "note": "no arm is feasible anywhere: part 2 finds no setting at denial 0"}
    best = f.sort_values("c_star", ascending=False)["arm"].iloc[0]
    sub = f[f["arm"] == best]
    beside = arms[(arms["arm"] == best) & (arms["denial_p"] == 0.25) & (arms["rtp_warnings"] == 0) & arms["feasible"]]
    return {"section": "choice", "arm": best, "c_star": float(sub["c_star"].iloc[0]), "feasible_cells": len(sub),
            "markets": ",".join(sorted(sub["market"].unique())), "feasible_cells_at_denial_025": len(beside),
            "note": "largest c* at denial 0 feasible somewhere (D-214, D-217); 25 % beside it"}


def main(results_dir: Path | None = None, scale: str = "dev") -> int:
    """`scale` "today" (D-225, EXPLORATORY) reads ES, NQ and CL from their runs at today's price level and the other
    markets from their development-scale runs, and writes results/resolution_map_score_today.csv beside D-224's."""
    from propedge import RESULTS_DIR
    from propedge.data.rmap_kit import RMAP_RUNS, RMAP_TODAY_READ, config
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    if scale not in ("dev", "today"):
        raise ValueError(f"scale must be 'dev' or 'today', got {scale!r}")
    today = scale == "today"
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    runs = RMAP_TODAY_READ if today else RMAP_RUNS
    counts, halves = load_counts(rd, runs)
    if counts.empty:
        print("REFUSED: no resolution-map run is ingested yet (R071-R080).")
        return 2
    cfg = config()
    fm = FillModel.load("assumed")
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks, "flatten": fm.flatten_slippage_ticks}
    complete = {m for m, h in halves.items() if len(h) == 2}
    cells = score_cells(counts, cfg, fm.round_turn_by_instrument, slip)
    stars = c_stars(rd)
    arms = score_arms(cells, stars, complete, load_caps(rd))
    pick = choose(arms)
    out = pd.concat([cells, arms, pd.DataFrame([pick])], ignore_index=True)
    write_result(out, "resolution_map_score_today" if today else "resolution_map_score", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"feasible": cfg["feasible"], "slippage_ticks": slip,
                             "fees": {k: v for k, v in fm.round_turn_by_instrument.items()},
                             "markets_complete": sorted(complete),
                             "markets_missing": sorted(set(cfg["markets"]) - complete),
                             "c_star_files": list(C_STAR_FILES), "legs": {k: list(v) for k, v in LEGS.items()},
                             "size_caps": "results/stop_band.csv cap_micros",
                             "runs": {f"{m} {h}": r for (m, h), r in runs.items()}, "scale": scale,
                             "decision": "D-214, D-215, D-221" + (", D-225" if today else "")},
                 notes={"status": ("EXPLORATORY: D-225, the map at today's price level, chosen after D-224's reading "
                                   "and reported beside it, never instead" if today else
                                   "EXPLORATORY: D-213 part 2, scored by rules fixed before the counts were read")},
                 description="EXPLORATORY: the resolution map scored -- per market, decision time, stop and R the "
                             "share of brackets that resolve (overall and worst year) and the cost per trade in R; "
                             "per arm the feasible settings against its c*; part 2's arm. No seed: a deterministic "
                             "reading of counts and recorded c*, with no randomness.")
    print(pd.DataFrame([pick]).to_string(index=False))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--scale", choices=("dev", "today"), default="dev",
                    help="today: ES, NQ and CL at today's price level (D-225, exploratory)")
    raise SystemExit(main(scale=ap.parse_args().scale))
