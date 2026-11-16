"""EXPLORATORY (D-276): two checks of ORB5 after its verdict (D-275), at the operator's choice of 2026-10-04 -- chosen
after ORB5's results were seen, so neither is a verdict.

    python scripts/orb5_exploratory.py

* **The cost reality check (`mini_mix`):** each trade sized as ORB5 sizes it -- min(floor(risk / stop $ a micro),
  cap) micro-equivalents under the state's cap (37 Combine, 15 funded below +$2,000; minis and micros count 10:1,
  8284197) -- but held as many NQ minis as fit and the rest in MNQ micros, each at its verified round-turn fee (NQ $3.78,
  MNQ $1.22, 8284213, `config/fills.yaml`); slippage and the spread are per micro-equivalent in points, so only the fee
  changes. ORB5's grid, plateau, walk-forward, era, drift and gate re-run with that cost, every other rule as declared
  (config/orb5_grid.yaml), the same seeds.
* **The corrected money check (`today_cost`):** ORB5's gate as D-271 intended it -- every out-of-sample trade costed
  at its cell's median cost of 2020 to June 2025 (the metric's cost) instead of its own era's (the audit's finding,
  D-275) -- with micros, and again with the mini mix.

Writes results/orb5_exploratory.csv: per cost model, the walk-forward, the final selection, its legs, the drift value,
the kill lines' readings and the gate's rows, all marked EXPLORATORY.
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

SCRIPT = "scripts/orb5_exploratory.py"
MINI_PER_MICROS = 10                                  # 8284197: "Micros and minis count at a 10:1 ratio"
CAPS = {"combine": 37, "funded": 15}                  # results/stop_band.csv's caps, in micro-equivalents


def mini_mix_fee(stop_ticks: np.ndarray, risk, cap: int, tick_dollars: float, fee_micro: float,
                 fee_mini: float) -> np.ndarray:
    """The fee a micro-equivalent pays when the trade holds as many minis as fit and the rest in micros; the size is
    ORB5's whole-micro size under the cap (at least one, so a stood-aside size still prices)."""
    st = np.asarray(stop_ticks, dtype=float)
    n = np.maximum(1.0, np.minimum(np.floor(np.asarray(risk, dtype=float) / (st * tick_dollars) + 1e-9), cap))
    minis = np.floor(n / MINI_PER_MICROS)
    micros = n - MINI_PER_MICROS * minis
    return (minis * fee_mini + micros * fee_micro) / n


class MiniGrid(g5.Grid5):
    """ORB5's records with the mini-mix fee: the Combine leg (R = 1) at $1,500 under 37, the funded leg at its stop
    width's funded risk under 15."""

    def __init__(self, m, cfg, fee_micro, fee_mini, tick_dollars, frisk: dict[int, float]):
        super().__init__(m, cfg, fee_micro, tick_dollars)
        self.fee_micro, self.fee_mini, self.frisk = float(fee_micro), float(fee_mini), frisk
        self._R = 1.0

    def _fee(self, i: int, R: float) -> np.ndarray:
        combine = R == float(self.cfg["fixed"]["combine"]["rr"])
        risk = float(self.cfg["fixed"]["combine"]["risk"]) if combine else self.frisk[i]
        if not np.isfinite(risk):
            risk = float(self.cfg["fixed"]["combine"]["risk"])
        st = np.repeat(self.stop[:, i][:, None], len(g5.OR_MINS), axis=1)
        return mini_mix_fee(st, risk, CAPS["combine" if combine else "funded"], self.td, self.fee_micro,
                            self.fee_mini)

    def outcome(self, v, i, R, mae=False):
        self._R = R
        saved = self.fee
        self.fee = self._fee(i, R)
        try:
            return super().outcome(v, i, R, mae)
        finally:
            self.fee = saved

    def today_cost(self, v, i, valid):
        st = np.repeat(self.stop[:, i][:, None], len(g5.OR_MINS), axis=1)
        sel = valid & (self.year >= g5.TODAY_FROM)[:, None]
        fee = self._fee(i, self._R)
        c = (self.entry_ticks(v)[sel] * self.td + fee[sel] + g5.STOP_SLIP_TICKS * self.td) / (st[sel] * self.td)
        return float(np.median(c)) if len(c) else float("nan")


def gate_trades_today(grid: g5.Grid5, ev: g5.Evaluated, selections: dict) -> pd.DataFrame:
    """ORB5's out-of-sample trades with each leg's R its move before any cost less its cell's median cost of 2020 to
    June 2025 (D-271's money in today's economics), in place of each trade's own era's cost."""
    out = []
    for y, k in selections.items():
        if k is None:
            continue
        c = ev.cells[k]
        v = grid.views[c["policy"]]
        valid = grid.valid(v, c["last_fill_slot"], c["ranges"], c["rv_min"])
        legs = {}
        for leg, R in (("c", float(ev.cfg["fixed"]["combine"]["rr"])), ("f", c["funded_rr"])):
            o = grid.outcome(v, c["i"], R, mae=True)
            legs[leg] = (o, grid.today_cost(v, c["i"], valid))
        of = legs["f"][0]
        kept = grid.kept(v, valid, of["exit"], c["coordination"]) & (grid.year == y)[:, None]
        for r, col in zip(*np.nonzero(kept)):
            row = {"date": grid.dates[r], "year": y, "i": c["i"], "entry_t": float(v["slot"][r, col]),
                   "exit_t": float(of["exit"][r, col]), "flat_f": bool(of["flat"][r, col])}
            for leg, (o, tc) in legs.items():
                row[f"r_{leg}"] = float(o["gross"][r, col] - tc)
                row[f"mae_{leg}"] = float(o["mae"][r, col])
            out.append(row)
    return pd.DataFrame(out)


def run_model(name: str, grid: g5.Grid5, cfg: dict, sessions, band, need: float, gate: bool) -> list[dict]:
    ev = g5.Evaluated(grid, cfg, sessions, band, need)
    years = list(ev.years)
    rows, sels, wf = [], {}, []
    for T in [y for y in years if y >= g5.WF_FIRST]:
        k, score = ev.select(ev.years < T)
        sels[T] = k
        val = ev.year_value(k, T) if k is not None else float("nan")
        wf.append(val)
        rows.append({"model": name, "section": "walkforward", "test_year": T,
                     **g5._key(ev.cells[k] if k is not None else None), "oos_value": val})
    wf_s = pd.Series(wf, index=[y for y in years if y >= g5.WF_FIRST])
    ok_all, v_all = ev.values(np.ones(len(years), bool))
    kf, score = ev.select(np.ones(len(years), bool))
    rows.append({"model": name, "section": "summary", "w1_bound": g5.bound(wf_s), "w1_mean": float(wf_s.mean()),
                 "feasible_cells": int(ok_all.sum()), "cells_value_positive": int((v_all > 0).sum())})
    if kf is None:
        return rows
    final = ev.cells[kf]
    _, dv = g5.drift_value(ev, kf)
    rows.append({"model": name, "section": "final", **g5._key(final), "value": float(v_all[kf]),
                 "drift_value": dv, "funded_risk": ev.frisk[final["i"]]})
    for leg in ("combine", "funded"):
        rows.append({"model": name, "section": "final_leg", **g5.leg_summary(ev, kf, leg, sessions)})
    if not gate:
        return rows
    frisk = float(ev.frisk[final["i"]])
    t = gate_trades_today(grid, ev, sels)
    stats = {}
    for leg, col in (("combine", "r_c"), ("funded", "r_f")):
        stats[leg] = {"e": float(t[col].mean()), "lb": g5.bound(t.groupby("year")[col].mean())}
    days = [d for d, y in zip(grid.dates, grid.year) if y >= g5.WF_FIRST]
    blocks, used = g5.gate_blocks(grid, t, days, frisk, final["funded_rr"], band, cfg["seeds"]["stops"])
    rows.append({"model": name, "section": "gate_inputs", "oos_trades": int(len(t)), "trades_used": used,
                 **{f"{k}_{leg}": v for leg, s in stats.items() for k, v in s.items()},
                 "kept_mean_r_f": float(np.mean([r for b in blocks for r in b.r_by_rr[final["funded_rr"]]]))
                 if used else float("nan"), "all_mean_r_f": float(t["r_f"].mean())})
    gdf, passed = g5.run_gate(blocks, stats, final["funded_rr"], frisk, cfg["gate"], cfg["seeds"]["gate"])
    for _, gr in gdf.iterrows():
        rows.append({"model": name, "section": "gate",
                     **{kk: vv for kk, vv in gr.items() if not isinstance(vv, (list, dict))}})
    rows.append({"model": name, "section": "gate_verdict", "passed": bool(passed)})
    return rows


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = g5.config()
    m, sessions = g5.load(rd, ROOT / "runs")
    fm = FillModel.load("assumed")
    q = params("NQ")
    td = q["micro_tick"] * q["micro_point_value"]
    fee_micro, fee_mini = float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"])
    band = read_result(BAND_FILE)
    need = float(setups_minimum(1.0, 1500.0, 0.0))
    micro = g5.Grid5(m, cfg, fee_micro, td)
    frisk = g5.funded_risks(micro, band)
    rows = run_model("micro_today_cost", micro, cfg, sessions, band, need, gate=True)
    mini = MiniGrid(m, cfg, fee_micro, fee_mini, td, frisk)
    rows += run_model("mini_mix_today_cost", mini, cfg, sessions, band, need, gate=True)
    out = pd.DataFrame(rows)
    write_result(out, "orb5_exploratory", script=SCRIPT, seed=int(cfg["seeds"]["gate"]), exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": "D-276", "fees": {"MNQ": fee_micro, "NQ": fee_mini}, "caps": CAPS,
                             "seeds": cfg["seeds"], "config": "config/orb5_grid.yaml"},
                 notes={"status": "EXPLORATORY: chosen after ORB5's verdict (D-275); no verdict rests on it"},
                 description="ORB5 re-scored with the mini-mix fee and its gate with today's costs (D-271), "
                             "exploratory.")
    pd.set_option("display.width", 250)
    print(out[out["section"].isin(["summary", "final", "final_leg", "gate_inputs", "gate_verdict"])]
          .dropna(axis=1, how="all").round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
