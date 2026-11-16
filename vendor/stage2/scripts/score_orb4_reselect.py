"""EXPLORATORY (T15 item 9; D-258): ORB4 -- ORB3's declared search re-scored with the operator's sizing rule.

    python scripts/score_orb4_reselect.py

ORB3 (D-256, D-257; `scripts/score_orb3_search.py`) was killed by W1 and W2: no configuration fitted the contract, the
funded account's consistent risk (D-212: 90 % of trades within 10 % of the risk in whole micros) failing at every stop
width and size. The operator then allowed uneven sizing "within reason" -- not hundreds of dollars either way (D-258).
ORB4 is ORB3's grid, metric, plateau, walk-forward and kill line, unchanged but for that rule: in each account state, on
the stops of every filled record of 2020 to June 2025, at least 90 % of trades take a whole-micro size under the cap
(`results/stop_band.csv`'s caps) whose dollar risk is within $100 of the target -- the Combine's $750, the largest of
the funded account's $1,000, $750 and $500 that passes -- with D-201's band and D-190's unsizeable share as before.

Everything here was chosen after ORB3's result: it is exploratory, and only a confirmation on NQ's held-back window can
carry a decision. Written beside it, so it can be cited: the same walk-forward and final selection with the contract
fit set aside (`nofit_*` rows), and each selection's realised dollar risks (`sizing` rows).

Writes results/orb4_reselect.csv.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import score_orb3_search as s3  # noqa: E402

SCRIPT = "scripts/score_orb4_reselect.py"
TOLERANCE = 100.0                                   # dollars: the operator's "within reason" (D-258)


def realised(stops: pd.Series, risk: float, cap_state: str, band: pd.DataFrame, market: str = "NQ") -> pd.Series:
    """Each stop's whole-micro dollar risk under the state's cap: min(floor(risk / stop $), cap) x stop $."""
    m = band[(band["state"] == cap_state) & (band["market"] == market)].iloc[0]
    per = stops.astype(float) * float(m["tick_value"])
    return np.minimum(np.floor(risk / per + 1e-9), float(m["cap_micros"])) * per


def fit_tolerance(stops: pd.DataFrame, combine_risk: float, funded_candidates: list[float], band: pd.DataFrame,
                  tol: float = TOLERANCE) -> list[dict]:
    """ORB3's contract fit with D-212's consistent risk read as 'within `tol` dollars' (D-258)."""
    from propedge.research.model_card import (FUNDED_CAP_STATE, RISK_SHARE, _share_outside_own, card_band,
                                              unsizeable_shares)
    from propedge.research.stop_band import MAX_OUTSIDE

    rows = []
    for state, risk, cap_state in ([("combine", combine_risk, "combine")]
                                   + [("funded", r, FUNDED_CAP_STATE) for r in sorted(funded_candidates, reverse=True)]):
        own = stops[stops["state"] == state]
        b = card_band(band, {state: (float(risk), cap_state)})
        outside = _share_outside_own(own, b).get(state, float("nan"))
        zero = unsizeable_shares(own, b).get(state, float("nan"))
        got = realised(own["stop_ticks"], float(risk), cap_state, band)
        within = float((got >= risk - tol - 1e-9).mean()) if len(own) else 0.0
        q = np.percentile(got, [10, 50, 90]) if len(own) else [float("nan")] * 3
        rows.append({"section": "fit", "state": state, "risk": float(risk), "n": len(own),
                     "band_outside_share": outside, "unsizeable_share": zero, "within_tolerance_share": within,
                     "realised_p10": float(q[0]), "realised_p50": float(q[1]), "realised_p90": float(q[2]),
                     "passes": bool(outside <= MAX_OUTSIDE and zero <= MAX_OUTSIDE and within >= RISK_SHARE)})
    return rows


def _no_fit(stops, combine_risk, funded_candidates, band):
    return [{"state": "combine", "passes": True, "risk": float(combine_risk)},
            {"state": "funded", "passes": True, "risk": float(max(funded_candidates))}]


def search(evals: list[dict], years: list[int], prefix: str) -> tuple[list[dict], dict | None, bool, bool]:
    """ORB3's walk-forward and final selection on `evals`: (rows, the final selection, W1 killed, W2 killed)."""
    rows, wf = [], []
    for T in [y for y in years if y >= s3.WF_FIRST]:
        sel, score = s3.select(evals, [y for y in years if y < T])
        val = s3.year_value(sel, T) if sel is not None else float("nan")
        wf.append(val)
        rows.append({"section": f"{prefix}walkforward", "test_year": T, **s3._key(sel), "plateau_score": score,
                     "oos_value": val})
    vals = pd.Series(wf, index=[y for y in years if y >= s3.WF_FIRST])
    w1_lb = s3.bound(vals)
    w1 = bool(vals.isna().any() or not (w1_lb > 0))
    final, score = s3.select(evals, years)
    fv = s3.value_on(final, years)[1] if final is not None else float("nan")
    w2 = bool(final is None or not (fv > 0))
    rows.append({"section": f"{prefix}final", **s3._key(final), "plateau_score": score, "value": fv,
                 "oos_mean": float(vals.mean()), "oos_positive_years": int((vals > 0).sum()),
                 "oos_years": int(vals.notna().sum()), "w1_bound": w1_lb,
                 "funded_risk": final["funded_risk"] if final is not None else float("nan")})
    return rows, final, w1, w2


def main(results_dir: Path | None = None, record: bool = True, runs_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, FUNDED_CAP_STATE, setups_minimum

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = s3.config()
    d, sess, have = s3.load(rd, cfg)
    if set(have) != set(cfg["runs"]):
        print(f"REFUSED: ORB3's three runs are needed, ingested: {have}.")
        return 2
    dt = pd.to_datetime(d["date"]).dt.date
    if (dt >= s3.HELD_BACK).any() or (dt < s3.START).any():
        print("REFUSED: a record outside 2009-06-01 to 2025-06-30 -- the held-back window is never read here (D-237).")
        return 2
    sessions = s3.trading_days(sess, Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)
    if sessions is None:
        print("REFUSED: a run record (runs/<run>/ingested.json) is missing: the trading days need it.")
        return 2
    d = d[~d["date"].astype(str).isin(s3.fomc_dates(cfg))]
    fm = FillModel.load("assumed")
    q = params("NQ")
    grid = s3.Grid(d, cfg, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.stop_slippage_ticks),
                   float(fm.flatten_slippage_ticks), q["micro_tick"] * q["micro_point_value"])
    need = setups_minimum(float(cfg["fixed"]["combine"]["rr"]), float(cfg["fixed"]["combine"]["risk"]), 0.0)
    band = read_result(BAND_FILE)
    years = sorted(sessions)
    k = math.prod(len(v) for v in cfg["search"].values())
    rows = []
    for prefix, fit_fn in (("", fit_tolerance), ("nofit_", _no_fit)):
        evals = s3.evaluate(grid, cfg, sessions, band, fit_fn, need)
        part, final, w1, w2 = search(evals, years, prefix)
        rows += part
        if prefix == "":
            verdict = (final, w1, w2)
            rows.append({"section": "summary_counts", "feasible_all_years": int(sum(s3.value_on(e, years)[0]
                                                                                    for e in evals)), "k": k})
        if final is not None:                                       # the selection's realised dollar risks
            c = final
            st = pd.DataFrame({"market": "NQ", "stop_ticks": grid.today(c["i"], c["last_fill_slot"], c["ranges"],
                                                                         c["rv_min"])[1]})
            stops = pd.concat([st.assign(state="combine"), st.assign(state="funded")], ignore_index=True)
            for r in fit_tolerance(stops, float(cfg["fixed"]["combine"]["risk"]),
                                   [float(x) for x in cfg["fixed"]["funded"]["risk_candidates"]], band):
                rows.append({**r, "section": f"{prefix}sizing"})
    final, w1, w2 = verdict
    rows.append({"section": "kline", "line": "W1", "killed": w1})
    rows.append({"section": "kline", "line": "W2", "killed": w2})
    killed = [ln for ln, x in (("W1", w1), ("W2", w2)) if x]
    rows.append({"section": "summary", "verdict": "kill" if killed else "continue", "killed_by": ",".join(killed),
                 "k": k, "tolerance_dollars": TOLERANCE, "funded_cap_state": FUNDED_CAP_STATE})
    out = pd.DataFrame(rows)
    write_result(out, "orb4_reselect", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"config": "config/orb3_search.yaml", "runs": list(cfg["runs"]), "k": k,
                             "tolerance_dollars": TOLERANCE, "fill_profile": "assumed", "decision": "D-258"},
                 notes={"status": "EXPLORATORY: ORB3's search re-scored after its result with the operator's sizing "
                                  "rule (D-258); only a confirmation on the held-back window can decide"},
                 description="EXPLORATORY: ORB4 -- ORB3's grid, metric, plateau, walk-forward and kill line with "
                             "consistent risk read as within $100 of the target; beside it the same search with the "
                             "contract fit set aside, and each selection's realised dollar risks. Deterministic, no "
                             "seed.")
    if record:
        VariantCounter().record(prereg_id="D-258:orb4_reselect", seed=0, exploratory=True,
                                params={"study": "ORB4 re-selection", "k": k, "market": "NQ"},
                                label="EXPLORATORY: ORB3's 640 configurations re-scored with the $100 sizing tolerance "
                                      "and with the fit set aside (deterministic records; the seed is nominal)")
    pd.set_option("display.width", 250)
    print(out.dropna(axis=1, how="all").round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
