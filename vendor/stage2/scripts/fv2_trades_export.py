"""EXPLORATORY (D-287): FV2's final selection as Campaign Studio trade logs, so the operator can see JJ Simon's strategy
as FV2 traded it in the Studio (the operator, 2026-10-04: "Can you show me JJ simons strategvy results in the campaign
software"; the Studio is an inspection view, never a verdict -- D-155's step 7; FV2's verdict is D-286's).

    python scripts/fv2_trades_export.py

The configuration is the grid's final selection, read from results/fv2_grid.csv (`final`): chosen on every development
year by the declared selection, so in-sample and, if anything, flattering -- the verdict was read on the walk-forward's
out-of-sample years. Its trades are settled by the scorer's own arithmetic (`scripts/score_fv2_grid.py`'s `Signals`):
the entry at two minutes (D-282), the Combine leg's bracket at its R, one position at a time by the later of the two
legs' exits and five a day (D-285), then D-272's stand-aside on each trade's own stop -- sizeable at the Combine's risk
and at the funded risk -- applied after the coordination, as the gate applies it. It reads no new data and selects
nothing.

Each log is in the Studio's canonical schema, one micro (MNQ) per trade, written by `scripts/orb_trades_export.py`'s
`trade_log`:

* `timestamp_in` the entry bar's start (the order fills at its open), `timestamp_out` the exit bar's end (the stop's or
  target's bar, or 15:08), ISO times in America/Chicago.
* Prices are constructed: the entry at a nominal 10,000.00 (the entry bar's open), the stop, target and exit at the
  recorded distances from it, so risk and P&L are exact.
* `pnl_gross` the move from the open for one micro; `pnl_net` less the scorer's costs -- the entry's max(1 tick, the
  recorded spread), the fee a micro-equivalent pays in the Combine's mix of NQ minis and MNQ micros (D-276), and the
  exit's tick on a stop or 2 on the flatten -- so `pnl_net / dollars_risked` is the scorer's net R of the Combine leg.
* `mae` the stop on every trade: the capture records no path short of the stop, so the bound that never flatters
  (D-284), the gate's own reading.

The log carries one exit per trade, so it is written only when the funded leg's target is the Combine's R (the final's
`r1.5` at the 1.5:1 Combine): the Studio's funded accounts then trade the same bracket (their fee in the Combine's mix,
a few cents a micro apart). Two logs: every development year (2009-06 to June 2025) and today's regime from 2020
(D-271), each with its day set -- every session with a record, FOMC days included as days without a trade.

Writes results/fv2_studio_final_<period>_trades.csv and _days.csv with manifests.
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

import orb_trades_export as ox  # noqa: E402
import score_fv2_grid as gf  # noqa: E402
from orb5_exploratory import CAPS  # noqa: E402

SCRIPT = "scripts/fv2_trades_export.py"
PERIODS = {"2009_2025": None, "2020_2025": gf.TODAY_FROM}


def final_cell(grid: pd.DataFrame, cfg: dict) -> tuple[dict, float]:
    """The grid's final selection as its cell, and its funded risk."""
    f = grid[grid["section"] == "final"]
    if len(f) != 1:
        raise SystemExit("REFUSED: results/fv2_grid.csv holds no single final selection.")
    r = f.iloc[0]
    want = {"sessions": str(r["sessions"]), "trigger": str(r["trigger"]),
            "continuation": str(r["continuation"]) == "True", "combine": str(r["combine"]),
            "funded_target": str(r["funded_target"])}
    match = [c for c in gf.cells(cfg) if gf._key(c) == want]
    if len(match) != 1:
        raise SystemExit(f"REFUSED: the final selection {want} is not one of the declared cells.")
    return match[0], float(r["funded_risk"])


def trades(S: gf.Signals, c: dict, frisk: float, band: pd.DataFrame) -> pd.DataFrame:
    """The cell's kept trades, stood aside where unsizeable, with every field `ox.trade_log` reads (`exit_cost` there
    is the trade's whole cost for one micro)."""
    from orb5_prep import sizeable

    R, c_risk = float(c["combine"]["rr"]), float(c["combine"]["risk"])
    if c["funded_target"] != "r1.5" or R != 1.5:
        raise SystemExit("REFUSED: the log carries one exit a trade; the funded leg's target must be the Combine's R.")
    cand = S.candidates(c)
    oc = S.outcome("r", R, c_risk, CAPS["combine"])
    of = S.outcome("r", 1.5, frisk, CAPS["funded"])
    kept = S.kept(cand, np.maximum(oc["exit"], of["exit"]))
    cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
    fb = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    ok = (sizeable(S.st, c_risk, int(cb["cap_micros"]), float(cb["tick_value"]), int(cb["cost_drag_floor_ticks"]))
          & sizeable(S.st, frisk, int(fb["cap_micros"]), float(fb["tick_value"]), int(fb["cost_drag_floor_ticks"])))
    i = np.nonzero(kept & ok)[0]
    st = S.st
    won = np.floor(R * st + 1e-9)
    move = np.where(oc["stopped"], -st, np.where(oc["target"], won, oc["flat_move"]))
    exit_ticks = np.where(oc["stopped"], gf.STOP_SLIP_TICKS, np.where(oc["target"], 0.0, gf.FLATTEN_SLIP_TICKS))
    cost = S.entry_cost * S.td + S.fee(c_risk, CAPS["combine"]) + exit_ticks * S.td
    return pd.DataFrame({
        "date": S.df["date"].to_numpy()[i], "year": S.year[i], "session": S.session[i], "dir": S.dir[i],
        "fill_slot": S.bar[i].astype(int), "exit_slot": oc["exit"][i].astype(int), "stop_ticks": st[i],
        "move_ticks": move[i], "mae_ticks": st[i], "target_ticks": won[i], "exit_cost": cost[i],
        "kind": np.where(oc["stopped"][i], "stop", np.where(oc["target"][i], "target", "flatten")),
        "net_r": oc["net"][i]})


def day_set(rd: Path, cfg: dict) -> list[str]:
    """Every session with a record across the captures, FOMC days included."""
    days = set()
    for run in cfg["runs"]:
        t = pd.read_csv(rd / f"manual_{run.replace('-', '_')}.csv", usecols=["kind", "date"], low_memory=False)
        days |= set(t[t["kind"] == "day"]["date"].astype(str))
    return sorted(days)


def main(results_dir: Path | None = None, runs_dir: Path | None = None, data: tuple | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = gf.config()
    c, frisk = final_cell(read_result(rd / "fv2_grid.csv"), cfg)
    if data is None:
        sig = gf.load(rd, Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)[0]
        days = day_set(rd, cfg)
    else:
        sig, days = data
    fm = FillModel.load("assumed")
    q = params("NQ")
    S = gf.Signals(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                   q["micro_tick"] * q["micro_point_value"])
    t = trades(S, c, frisk, read_result(BAND_FILE))
    if not np.allclose(-(t["exit_cost"] - t["move_ticks"] * S.td) / (t["stop_ticks"] * S.td), t["net_r"]):
        raise SystemExit("REFUSED: the log's net R differs from the scorer's.")
    for period, first in PERIODS.items():
        tp = t if first is None else t[t["year"] >= first]
        dp = days if first is None else [d for d in days if int(d[:4]) >= first]
        log = ox.trade_log(tp)
        counts = tp["date"].astype(str).value_counts()
        dayset = pd.DataFrame({"date": dp, "entries": [int(counts.get(x, 0)) for x in dp]})
        name = f"fv2_studio_final_{period}"
        params_ = {"configuration": gf._key(c), "funded_risk": frisk, "source": "results/fv2_grid.csv, final",
                   "period": period, "latency_minutes": 2, "positions": "one at a time by the later leg's exit, five "
                   "a day", "stand_aside": "D-272 on each trade's own stop, Combine and funded", "fill_profile":
                   "assumed", "fee": "NQ minis with MNQ micros at the Combine's size (D-276)", "mae": "the stop "
                   "(D-284)", "prices": f"constructed: entry {ox.NOMINAL_ENTRY:,.2f} nominal, the rest at the "
                   "recorded distances (risk and P&L exact)", "decision": "D-287"}
        write_result(log, f"{name}_trades", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                     results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: FV2's final selection as a Campaign Studio log; no verdict "
                                      "(FV2 is killed, D-286)"},
                     description=f"EXPLORATORY: FV2's final selection ({period.replace('_', '-')}) as a Campaign "
                                 "Studio trade log (one MNQ per trade, constructed prices, exact risk and P&L).")
        write_result(dayset, f"{name}_days", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                     results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: the log's day set, days without a trade included"},
                     description=f"EXPLORATORY: {name}'s day set -- every session with a record, FOMC days "
                                 "included.")
        print(f"{name}: {len(log)} trades over {len(dp)} sessions ({int((dayset['entries'] == 0).sum())} without a "
              f"trade); {log['exit_reason'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
