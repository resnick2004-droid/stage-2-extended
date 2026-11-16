"""ORB2's screen (T15 item 9; D-253, D-254): the kill line of config/orb2_model.yaml, fixed before R101 was read, applied
to NQ's 2020 to June 2025 day records.

    python scripts/score_orb2_screen.py

Reads R101 (`propedge/data/orb_parser.py`'s table, a row per day and range) and its run record
(`runs/R101-orb-NQ-2020/ingested.json`: the window's trading days, HEAD's days -- the kit counts its warm-up days
apart, D-255), drops FOMC days
(`config/im2_release_calendar.csv` and `config/sources/fomc_statements_2020_2024q1.csv`), refuses any record before
2020 or on or after 2025-07-01 (the held-back window, D-237). Then, by ORB1's trade arithmetic (`scripts/
score_orb_dev.py`'s `trade_r`, the `assumed` costs):

* **K1, the move**: the 5-minute range's paper-exit trades (a direction, relative volume at least 100 %, a fill) before
  any cost -- the entry's tick added back, no fee, no exit slippage -- and their yearly one-sided 95 % lower bound.
* **Two fill-bar readings** (D-254): the kit's (`lenient`: a fill inside its bar is stopped there only if the bar closes
  beyond the stop) and the `strict` one (stopped there whenever the fill bar's adverse excursion reaches the stop).
* **One at a time** (`sequential`): the four ranges' filtered trades in fill-bar order, the shorter range first on the
  same bar, an entry skipped while a position is open (its fill bar to its exit bar, both counted) -- for each exit and
  reading, since they set when a position closes. Each K line is read on the worse of the two readings: **K2** the
  smaller net e at 2R and 1.5R; **K3** the larger share reaching the 15:08 flatten, overall or in any year, at 2R and
  1.5R; **K4** the fewer trades per trading day in the window (every session: early closes and FOMC days included) at
  2R and 1.5R, against D-154's minimum for the card's Combine (`results/setups_per_day.csv`).
* **K5, contract fit**: the screen's stops (`results/orb2_screen_stops.csv`: the one-at-a-time trades of the kit's
  reading at 2R as the Combine's, at 1.5R as the funded account's, each with its exit and date) checked as
  `validate_card` checks a card -- D-201's band and D-190's unsizeable share at the card's own sizes (D-242), D-212's
  consistent risk -- the Combine at $750, the funded account at the largest of $1,000, $750 and $500 that passes, chosen
  on the stops alone.

The verdict is `continue` when no K line is met, else `kill`. Writes results/orb2_screen.csv (`kline`, `trade`, `fit`
and `summary` rows) and results/orb2_screen_stops.csv.
"""
from __future__ import annotations

import io
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

import score_orb_dev as so  # noqa: E402
from propedge.outcomes.orb_core import FLAT_ENTRY  # noqa: E402

SCRIPT = "scripts/score_orb2_screen.py"
CONFIG = ROOT / "config" / "orb2_model.yaml"
START, HELD_BACK = date(2020, 1, 1), date(2025, 7, 1)
READINGS = ("lenient", "strict")


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


def fomc_dates(cfg: dict) -> set[str]:
    out = set()
    for rel in cfg["screen"]["fomc"]:
        lines = [ln for ln in (ROOT / rel).read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        t = pd.read_csv(io.StringIO("\n".join(lines)))
        if "code" in t.columns:
            t = t[t["code"] == "FOMC"]
        out |= set(t["date"].astype(str))
    return out


def load(results_dir: Path, cfg: dict) -> pd.DataFrame:
    run = cfg["screen"]["run"]
    f = results_dir / f"manual_{run.replace('-', '_')}.csv"
    if not f.exists():
        return pd.DataFrame()
    d = pd.read_csv(f, low_memory=False)
    d = d[d["kind"] == "day"].copy()
    d["or_minutes"] = d["or_minutes"].astype(int)
    return d


def window_days(runs_dir: Path, cfg: dict) -> int | None:
    """The window's trading days from the run record: HEAD's days, which the kit counts apart from its warm-up days (a
    warm-up day returns before the day count; early closes included). D-255: R101's committed screen subtracted the
    warm-up again, so its per-day figures are 2.2 % high; the verdict does not change."""
    f = runs_dir / cfg["screen"]["run"] / "ingested.json"
    if not f.exists():
        return None
    s = json.loads(f.read_text(encoding="utf-8"))["summary"]
    return int(s["days"])


def strict(d: pd.DataFrame, rr: tuple[float, ...]) -> pd.DataFrame:
    """The strict fill-bar reading: a fill whose bar's adverse excursion reaches the stop is stopped on that bar (no
    overshoot, no target); every other record as the kit wrote it."""
    out = d.copy()
    hit = (out["fill_slot"] != -1) & (out["stop_slot"] != out["fill_slot"]) & (
        out["fill_bar_against_ticks"] >= out["stop_ticks"])
    out.loc[hit, "stop_slot"] = out.loc[hit, "fill_slot"]
    out.loc[hit, "overshoot_tenths"] = 0
    for R in rr:
        out.loc[hit, f"target_{R:g}_slot"] = -1
    return out


def sequential(t: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """One position at a time: trades (`trade_r` rows with or_minutes and exit_slot) in fill-bar order, the shorter
    range first on the same bar; an entry skipped while a kept position is open on its fill bar. (kept, skipped)."""
    t = t.sort_values(["date", "fill_slot", "or_minutes"], kind="stable")
    keep, skipped = [], 0
    for _, g in t.groupby("date", sort=False):
        busy_to = -1
        for idx, fs, xs in zip(g.index, g["fill_slot"], g["exit_slot"]):
            if fs <= busy_to:
                skipped += 1
                continue
            keep.append(idx)
            busy_to = xs
    return t.loc[keep], skipped


def _flatten_shares(t: pd.DataFrame) -> tuple[float, float]:
    """(overall, worst year) share of trades reaching the 15:08 flatten (not finished)."""
    if not len(t):
        return float("nan"), float("nan")
    flat = ~t["finished"].astype(bool)
    return float(flat.mean()), float(flat.groupby(t["year"]).mean().max())


def exit_label(t: pd.DataFrame, R: float) -> pd.Series:
    hit = t[f"target_{R:g}_slot"] != -1
    return pd.Series(np.where(hit, "target", np.where(t["stop_slot"] != -1, "stop", "flatten")), index=t.index)


def fit(stops: pd.DataFrame, combine_risk: float, funded_candidates: list[float], band: pd.DataFrame) -> list[dict]:
    """K5: each candidate size's band, unsizeable and consistent-risk shares on its state's stops (D-201, D-190,
    D-212, at the card's own sizes, D-242), the funded candidates largest first."""
    from propedge.research.model_card import (FUNDED_CAP_STATE, RISK_SHARE, _share_outside_own, card_band,
                                              risk_consistency, unsizeable_shares)
    from propedge.research.stop_band import MAX_OUTSIDE as MAX_OUTSIDE_SHARE

    rows = []
    for state, risk, cap_state in ([("combine", combine_risk, "combine")]
                                   + [("funded", r, FUNDED_CAP_STATE) for r in sorted(funded_candidates, reverse=True)]):
        sizes = {state: (float(risk), cap_state)}
        own = stops[stops["state"] == state]
        b = card_band(band, sizes)
        outside = _share_outside_own(own, b).get(state, float("nan"))
        zero = unsizeable_shares(own, b).get(state, float("nan"))
        rc = risk_consistency(own, band, sizes).get(state, float("nan"))
        rows.append({"section": "fit", "state": state, "risk": float(risk), "n": len(own),
                     "band_outside_share": outside, "unsizeable_share": zero, "risk_realised_share": rc,
                     "passes": bool(outside <= MAX_OUTSIDE_SHARE and zero <= MAX_OUTSIDE_SHARE and rc >= RISK_SHARE)})
    return rows


def screen(d: pd.DataFrame, cfg: dict, orb_cfg: dict, fees: dict, slip: float, flat_slip: float,
           band: pd.DataFrame, days: int) -> tuple[list[dict], pd.DataFrame]:
    from propedge.data.orb_kit import params
    from propedge.research.model_card import MAX_FLATTEN_SHARE, setups_minimum

    market = cfg["market"]
    q = params(market, orb_cfg)
    td, fee = q["micro_tick"] * q["micro_point_value"], float(fees[q["micro"]])
    rr = tuple(float(r) for r in orb_cfg["exits"]["bracket"]["rr"])
    rv_min = float(orb_cfg["fixed"]["relative_volume"]["min"])
    signals = d[(d["market"] == market) & (d["dir"] != 0) & (d["rv100"] >= 100 * rv_min)]
    signals = signals[signals["or_minutes"].isin(cfg["entries"]["ranges"])]
    need = setups_minimum(float(cfg["sizes"]["combine"]["rr"]), float(cfg["sizes"]["combine"]["risk"]),
                          float(cfg["edge_assumed"]))
    rows = []

    five = signals[signals["or_minutes"] == 5]                                   # K1
    g = so.trade_r(five, td, 0.0, 0.0, None, rr, 0.0)
    g["r"] = g["r"] + 1.0 / g["stop_ticks"]
    k1_lb = so.bound(g.groupby("year")["r"].mean())
    rows.append({"section": "kline", "line": "K1", "label": "5-minute paper exit before any cost: yearly lower bound",
                 "value": k1_lb, "estimate": float(g["r"].mean()) if len(g) else float("nan"), "n": len(g),
                 "killed": bool(not (k1_lb > 0))})

    stops, tr = [], {}
    for reading in READINGS:
        x = signals if reading == "lenient" else strict(signals, rr)
        for R, state in ((None, "paper"), (float(cfg["exits"]["combine_rr"]), "combine"),
                         (float(cfg["exits"]["funded_rr"]), "funded")):
            t = so.trade_r(x, td, fee, slip, R, rr, flat_slip)
            kept, skipped = sequential(t)
            ym = kept.groupby("year")["r"].mean()
            flat_all, flat_worst = _flatten_shares(kept)
            row = {"section": "trade", "reading": reading, "exit": state, "R": R, "n": len(kept), "skipped": skipped,
                   "per_day": len(kept) / days if days else float("nan"),
                   "e_net": float(kept["r"].mean()) if len(kept) else float("nan"), "lower_bound": so.bound(ym),
                   "worst_year_e_net": float(ym.min()) if len(ym) else float("nan"),
                   "flatten_share": flat_all, "worst_year_flatten_share": flat_worst,
                   "by_range": ";".join(f"{n}m {int(c)}" for n, c in
                                        kept["or_minutes"].value_counts().sort_index().items())}
            rows.append(row)
            tr[(reading, state)] = row
            if R is not None and reading == "lenient":
                stops.append(pd.DataFrame({"market": kept["market"], "state": state, "stop_ticks": kept["stop_ticks"],
                                           "exit": exit_label(kept, R), "date": kept["date"]}))
    legs = [(r, s) for r in READINGS for s in ("combine", "funded")]
    k2 = min(tr[k]["e_net"] for k in legs)
    rows.append({"section": "kline", "line": "K2", "label": "net e, the smaller at 2R and 1.5R under either reading",
                 "value": float(k2), "killed": bool(not k2 > 0)})
    k3 = max(max(tr[k]["flatten_share"], tr[k]["worst_year_flatten_share"]) for k in legs)
    rows.append({"section": "kline", "line": "K3", "label": "share reaching the 15:08 flatten, overall or worst year, "
                 "the larger at 2R and 1.5R under either reading", "value": float(k3), "threshold": MAX_FLATTEN_SHARE,
                 "killed": bool(not k3 <= MAX_FLATTEN_SHARE + 1e-12)})
    k4 = min(tr[k]["per_day"] for k in legs)
    rows.append({"section": "kline", "line": "K4", "label": "trades per trading day, the fewer at 2R and 1.5R under "
                 "either reading", "value": float(k4), "threshold": need, "killed": bool(not k4 + 1e-9 >= need)})

    stops = pd.concat(stops, ignore_index=True)
    fr = fit(stops, float(cfg["sizes"]["combine"]["risk"]), [float(r) for r in cfg["sizes"]["funded"]["risk_candidates"]],
             band)
    rows += fr
    comb = next(r for r in fr if r["state"] == "combine")
    funded = next((r for r in fr if r["state"] == "funded" and r["passes"]), None)
    rows.append({"section": "kline", "line": "K5", "label": "contract fit: the Combine at $750 and a funded size pass",
                 "value": funded["risk"] if funded else float("nan"),
                 "killed": bool(not (comb["passes"] and funded is not None))})
    killed = [r["line"] for r in rows if r["section"] == "kline" and r["killed"]]
    filled = int((signals["fill_slot"] != -1).sum())
    rows.append({"section": "summary", "verdict": "kill" if killed else "continue", "killed_by": ",".join(killed),
                 "days": days, "record_days": int(d.loc[d["or_minutes"] == 5, "date"].nunique()),
                 "signals": len(signals), "filled": filled,
                 "fill_share": filled / len(signals) if len(signals) else float("nan"),
                 "funded_risk": funded["risk"] if funded else float("nan"), "k": int(cfg["k"]),
                 "flatten_slot": FLAT_ENTRY})
    return rows, stops


def main(results_dir: Path | None = None, record: bool = True, runs_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.orb_kit import config as orb_config
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = config()
    d = load(rd, cfg)
    if d.empty:
        print(f"REFUSED: ORB2's screen run {cfg['screen']['run']} is not ingested yet.")
        return 2
    days = window_days(Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)
    if not days:
        print(f"REFUSED: no run record for {cfg['screen']['run']} (runs/<run>/ingested.json): K4's trading days.")
        return 2
    dates = pd.to_datetime(d["date"]).dt.date
    if (dates >= HELD_BACK).any() or (dates < START).any():
        print("REFUSED: a record outside 2020-01-01 to 2025-06-30 -- the held-back window is never read here (D-237).")
        return 2
    d = d[~d["date"].astype(str).isin(fomc_dates(cfg))]
    fm = FillModel.load("assumed")
    rows, stops = screen(d, cfg, orb_config(), dict(fm.round_turn_by_instrument), float(fm.stop_slippage_ticks),
                         float(fm.flatten_slippage_ticks), read_result(BAND_FILE), days)
    out = pd.DataFrame(rows)
    params = {"config": "config/orb2_model.yaml", "rules": "config/orb_model.yaml", "run": cfg["screen"]["run"],
              "window": [str(START), "2025-06-30"], "k": int(cfg["k"]), "fill_profile": "assumed",
              "fees": dict(fm.round_turn_by_instrument), "exit_slippage_ticks": float(fm.stop_slippage_ticks),
              "flatten_slippage_ticks": float(fm.flatten_slippage_ticks), "decision": "D-253, D-254"}
    write_result(stops, "orb2_screen_stops", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters=params,
                 description="ORB2's screen stops: the one-at-a-time trades (the kit's fill-bar reading) at 2R (the "
                             "Combine's) and 1.5R (the funded account's), each with its exit and date -- the card's stop "
                             "distribution (D-201, D-212). Deterministic, no seed.")
    write_result(out, "orb2_screen", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters=params,
                 description="ORB2's screen on NQ 2020 to June 2025: the kill line K1-K5 fixed in config/orb2_model.yaml "
                             "before the run, the one-at-a-time trades under both fill-bar readings, the contract fit "
                             "and the verdict. Deterministic, no seed.")
    if record:
        VariantCounter().record(prereg_id="D-253:orb2_screen", seed=0, exploratory=True,
                                params={"study": "ORB2 screen", "k": int(cfg["k"]), "market": cfg["market"]},
                                label="ORB2's screen: NQ, four ranges one at a time, 2R and 1.5R, three funded sizes "
                                      "by the stops rule (deterministic records; the seed is nominal)")
    pd.set_option("display.width", 250)
    print(out.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
