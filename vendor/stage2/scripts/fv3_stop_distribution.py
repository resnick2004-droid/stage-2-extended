"""EXPLORATORY (D-355): FV3-C's stop distribution for its model card (D-191, D-201, D-212) -- one row per development
gate trade and lifecycle state.

    python scripts/fv3_stop_distribution.py

FV3-C (`config/fv3_corrected_portfolio.yaml`, frozen at c561ec9; its development run results/fv3_corrected_v1.csv,
D-354) trades the walk-forward's out-of-sample trades of its one declared cell. The card's checks read a stop
distribution with each entry's market, stop in the micro's ticks, lifecycle state, exit (target, stop or flatten) and
date. Each gate trade is a row in each state at the fresh state's geometry the gate uses: the Combine at its R, the
funded account at its R, both on the trade's own stop (`gate_trades` prices every R on the Combine's fresh spec); a
trade its room does not permit at a state's R is no trade in that state (no row). A breakeven exit leaves by the stop
order moved to entry and is written `stop`. The trades are recomputed by the scorer's own functions from the ingested
development captures and checked against `gate_trades` (the same dates, stops and count); nothing in the held-back window
is read. Writes results/fv3c_stop_distribution.csv; no seed: nothing is drawn.
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

SCRIPT = "scripts/fv3_stop_distribution.py"
CONFIG = ROOT / "config" / "fv3_corrected_portfolio.yaml"
RESULT = "fv3c_stop_distribution"


def stop_rows(S, ev, sels: dict, final: dict, cfg: dict) -> pd.DataFrame:
    """One row per kept gate trade and state: market, state, stop_ticks, exit, date (`gate_trades`'s selection)."""
    import score_fv3_grid as gf

    c_spec = gf.leg_spec(cfg, "combine")
    fresh = cfg["state_policy"]["fresh"]
    out = []
    for y, k in sels.items():
        if k is None:
            continue
        c = ev.cells[k]
        cand = S.candidates(c)
        rung = S.rung(bool(c["double_rung_reversions"]))
        base = S.outcome(rung, "r", c_spec[1], c_spec[2], c_spec[3])
        kept = S.kept(cand & base["permitted"], base["exit"], base["stopped"],
                      two_losses_bos_only=(c["displacement"] == "rule")) & (S.year == y)
        idx = np.nonzero(kept)[0]
        for state, R in (("combine", float(fresh["combine_rr"])), ("funded", float(fresh["funded_rr"]))):
            o = S.outcome(rung, "r", R, c_spec[2], c_spec[3])
            for i in idx:
                if not bool(o["permitted"][i]):
                    continue
                ex = "target" if o["target"][i] else "flatten" if o["flat"][i] else "stop"
                out.append({"market": "NQ", "state": state, "stop_ticks": float(base["stop"][i]), "exit": ex,
                            "date": str(S.df["date"].iat[i]), "rr": R})
    return pd.DataFrame(out)


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    import score_fv3_grid as gf

    cfg = gf.config(CONFIG)
    sig, ses, bench, sessions = gf.load(RESULTS_DIR, ROOT / "runs", cfg)
    fm, q = FillModel.load("assumed"), params("NQ")
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                    q["micro_tick"] * q["micro_point_value"], cfg["ladder"])
    fresh = cfg["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    ev = gf.EvaluatedFV3(S, ses, cfg, sessions, read_result(BAND_FILE), float(need))
    wf_first = int(cfg["selection"]["walkforward"].get("first_test_year", gf.WF_FIRST))
    sels = {int(T): ev.select(ev.years < T)[0] for T in ev.years if T >= wf_first}
    kf, _ = ev.select(np.ones(len(ev.years), bool))
    if kf is None:
        print("REFUSED: the declared cell is not feasible on the development years; no gate trades.")
        return 2
    final = ev.cells[kf]
    t = gf.gate_trades(S, ev, sels, final)
    out = stop_rows(S, ev, sels, final, cfg)
    comb = out[out["state"] == "combine"]
    if (len(comb) != len(t) or list(comb["date"]) != list(t["date"].astype(str))
            or not np.allclose(comb["stop_ticks"].to_numpy(float), t["stop_ticks"].to_numpy(float))):
        print("REFUSED: the recomputed trades differ from gate_trades' (count, dates or stops).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    write_result(out, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=rd,
                 parameters={"config": "config/fv3_corrected_portfolio.yaml", "candidate": "FV3-C",
                             "development_run": "results/fv3_corrected_v1.csv", "walkforward_first_test_year": wf_first,
                             "states": {"combine": float(fresh["combine_rr"]), "funded": float(fresh["funded_rr"])},
                             "exit_mapping": "target at the state's R; flatten at 15:10; stop or breakeven -> stop",
                             "decision": "D-355"},
                 description="EXPLORATORY: FV3-C's development gate trades, one row per trade and state (market, state, "
                             "stop in the micro's ticks, exit at the state's R, date), for its model card's D-191, D-201 "
                             "and D-212 checks. No seed: the ingested captures re-expressed, nothing drawn.")
    print(out.groupby(["state", "exit"]).size().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
