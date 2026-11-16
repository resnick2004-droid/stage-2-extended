"""EXPLORATORY: the opening-range searches' trades as Campaign Studio trade logs, so the operator can replay and inspect
them (the operator, 2026-10-03: "put the data and backtests into the campaign replay software so I can visualise and
see if there is anything that looks wrong"; the Studio is an inspection view, never a verdict -- D-155's step 7).

    python scripts/orb_trades_export.py

From ORB3's records (R102-R104, NQ 2009-06-01 to 2025-06-30, FOMC days out) and ORB3's own trade arithmetic
(`scripts/score_orb3_search.py`: one position at a time, the strict fill-bar reading, the assumed costs), three
configurations, each re-presenting outcomes already scored -- it reads no new data and selects nothing:

* `orb4_final` -- ORB4's final selection (results/orb4_reselect.csv, `final`): direction mode, the 5- and 15-minute
  ranges, the stop at 0.15 of the 14-day ATR, fills to 15:07;
* `orb4_nofit` -- the selection with the contract fit set aside (`nofit_final`): direction mode, all four ranges, 0.30,
  fills to 12:00;
* `orb_bracket` -- the bracket ORB2 traded, on every year: all four ranges, the relative-volume filter, 0.10, fills to
  15:07, the Combine's 2R target.
* `orb_bracket_best` (D-268, the operator: "Let me see this run in the campaign replay") -- ORB3's bracket cell with
  the highest Combine metric: the 5-minute range, the relative-volume filter, 0.20, fills to 15:07, 2R. Picked after
  seeing ORB3's results, so exploratory; one of its counted cells.

Each log is in the Studio's canonical schema (`propedge/outcomes/tradelog.py`), one micro (MNQ) per trade, so the
Studio sizes each trade from its own stop:

* `timestamp_in` the fill bar's start, `timestamp_out` the exit bar's end (the stop's or target's bar, or the 15:08 bar),
  as ISO times with their America/Chicago offset.
* **Prices are constructed, not quoted** (the records hold no price, D-120): `entry_price` is a nominal 10,000.00 on
  every trade; `stop`, `target` and `exit_price` sit at the recorded distances from it in the micro's ticks, so
  |entry - stop| x $2 a point is the trade's real risk per micro and every P&L is exact. The entry is the kit's fill,
  one tick beyond the level, so the entry's slippage is inside `entry_price` and outside the gross-to-net gap.
* `pnl_gross` the move from the fill for one micro; `pnl_net` less the round-turn fee and the exit's slippage tick on a
  stop or the flatten; a target fills at its whole-tick limit (R x the stop rounded down, D-257) with no slippage.
* `mae` the worst move against the trade before its exit, as an upper bound: a stopped trade's is its stop; any other's
  is the narrowest grid stop not reached before its exit (or its own stop), never below its fill bar's own adverse
  excursion -- so the Studio settles a trade against an account's floor no more kindly than the record allows.

Beside each, the day set: every session with a record, FOMC days included as days without a trade. Early-close
sessions write no record and are not in it (about nine a year, `runs/<run>/ingested.json`'s `early`).

Writes results/orb_studio_<name>_trades.csv and results/orb_studio_<name>_days.csv with manifests.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import score_orb3_search as s3  # noqa: E402
from propedge.outcomes.orb_core import FLAT_ENTRY, OR_MINS  # noqa: E402

SCRIPT = "scripts/orb_trades_export.py"
CT = ZoneInfo("America/Chicago")
NOMINAL_ENTRY = 10000.0
TICK = 0.25
POINT_VALUE = 2.0                                   # MNQ, $ per point
EXPORTS = {
    "orb4_final": {"mode": "direction", "ranges": (5, 15), "rv_min": None, "stop_atr": 0.15, "last_fill_ct": "15:07",
                   "R": None, "source": "results/orb4_reselect.csv, final"},
    "orb4_nofit": {"mode": "direction", "ranges": (5, 15, 30, 60), "rv_min": None, "stop_atr": 0.30,
                   "last_fill_ct": "12:00", "R": None, "source": "results/orb4_reselect.csv, nofit_final"},
    "orb_bracket": {"mode": "bracket", "ranges": (5, 15, 30, 60), "rv_min": 1.0, "stop_atr": 0.10,
                    "last_fill_ct": "15:07", "R": 2.0, "source": "ORB2's configuration (config/orb2_model.yaml) at the "
                                                             "Combine's 2R, on every development year"},
    # D-268: chosen after seeing results/orb3_search.csv, so EXPLORATORY -- ORB3's bracket cell with the highest
    # Combine metric, one of its 640 counted configurations (no new variant)
    "orb_bracket_best": {"mode": "bracket", "ranges": (5,), "rv_min": 1.0, "stop_atr": 0.20, "last_fill_ct": "15:07",
                         "R": 2.0, "decision": "D-268",
                         "source": "results/orb3_search.csv: the bracket cell with the highest combine_metric "
                                   "(5-minute range, the volume filter, 0.20, fills to 15:07)"},
}


def stamp(day: str, slot: int) -> str:
    """The end of the bar at `slot` (minutes after 17:00 CT on the evening before trading day `day`), ISO in CT."""
    base = datetime.fromisoformat(day).replace(tzinfo=CT) - timedelta(days=1)
    wall = base.replace(hour=17, minute=0) + timedelta(minutes=int(slot))
    return wall.replace(tzinfo=None).replace(tzinfo=CT).isoformat()


def trades(grid: s3.Grid, spec: dict, fee: float, slip: float, flat_slip: float) -> pd.DataFrame:
    """One configuration's one-at-a-time trades under the strict reading, every field the log needs -- the same
    outcome rules as `Grid.trades` (its gross and costs are checked against it in the tests)."""
    i = list(grid.cfg["search"]["stop_atr"]).index(spec["stop_atr"])
    last = s3._ct_slot(spec["last_fill_ct"])
    f, R = grid.f, spec["R"]
    valid = grid.valid(last, spec["ranges"], spec["rv_min"])
    st = np.repeat(grid.stop[:, i][:, None], len(OR_MINS), axis=1)
    fbs = (f["at_open"] == 0) & (f["fill_bar_against_ticks"] >= st)
    A = grid.a[i]
    fill = f["fill_slot"]
    if spec["mode"] == "bracket":
        Fa = (grid.f15 if R == 1.5 else grid.f2)[i]
        stopped = fbs | ((A != -1) & ((Fa == -1) | (A <= Fa)))
        target = ~stopped & (Fa != -1)
        exit_slot = np.where(fbs, fill, np.where(stopped, A, np.where(target, Fa, FLAT_ENTRY)))
    else:
        stopped = fbs | (A != -1)
        target = np.zeros_like(stopped)
        exit_slot = np.where(fbs, fill, np.where(stopped, A, FLAT_ENTRY))
    kept = s3.sequential_mask(np.where(valid, fill, np.inf), np.where(valid, exit_slot, -1), valid)
    rows, cols = np.nonzero(kept)
    won = np.floor((R or 0.0) * st + 1e-9)                        # the target's whole-tick limit, in ticks
    move = np.where(stopped, -st, np.where(target, won, f["close_ticks"]))   # ticks from the fill
    # the MAE's upper bound: the narrowest grid stop not reached before the exit, else the trade's own stop
    levels = grid.stop[:, :i + 1]
    reached = np.stack([(grid.a[k] != -1) & (grid.a[k] <= exit_slot) for k in range(i + 1)], axis=-1)
    unreached = np.where(~reached, np.repeat(levels[:, None, :], len(OR_MINS), axis=1), np.inf)
    mae = np.where(stopped, st, np.minimum(unreached.min(axis=-1), st))
    inside = (f["at_open"] == 0)
    mae = np.where(stopped, st, np.minimum(np.maximum(mae, np.where(inside, f["fill_bar_against_ticks"], 0)), st))
    pick = lambda a: np.asarray(a)[rows, cols]                     # noqa: E731
    exit_cost = np.where(pick(stopped), fee + slip * TICK * POINT_VALUE,
                         np.where(pick(target), fee, fee + flat_slip * TICK * POINT_VALUE))
    out = pd.DataFrame({"date": grid.dates[rows], "or_minutes": np.array(OR_MINS)[cols], "dir": pick(f["dir"]),
                        "fill_slot": pick(fill).astype(int), "exit_slot": pick(exit_slot).astype(int),
                        "stop_ticks": pick(st), "move_ticks": pick(move), "mae_ticks": pick(mae),
                        "kind": np.where(pick(stopped), "stop", np.where(pick(target), "target", "flatten")),
                        "exit_cost": exit_cost, "target_ticks": np.where(spec["mode"] == "bracket", pick(won),
                                                                         np.nan)})
    return out.sort_values(["date", "fill_slot"], kind="stable").reset_index(drop=True)   # in time, not range, order


def trade_log(t: pd.DataFrame) -> pd.DataFrame:
    """The Studio's canonical log from `trades` (see the module docstring)."""
    side = np.where(t["dir"] > 0, 1.0, -1.0)
    px = TICK
    gross = t["move_ticks"] * px * POINT_VALUE
    return pd.DataFrame({
        "timestamp_in": [stamp(d, s - 1) for d, s in zip(t["date"], t["fill_slot"])],
        "timestamp_out": [stamp(d, s) for d, s in zip(t["date"], t["exit_slot"])],
        "symbol": "MNQ",
        "side": np.where(side > 0, "long", "short"),
        "entry_price": NOMINAL_ENTRY,
        "exit_price": NOMINAL_ENTRY + side * t["move_ticks"] * px,
        "stop": NOMINAL_ENTRY - side * t["stop_ticks"] * px,
        "target": NOMINAL_ENTRY + side * t["target_ticks"] * px,
        "contracts": 1,
        "pnl_gross": gross,
        "pnl_net": gross - t["exit_cost"],
        "exit_reason": t["kind"],
        "dollars_risked": t["stop_ticks"] * px * POINT_VALUE,
        "mae": t["mae_ticks"] * px * POINT_VALUE,
    })


def main(results_dir: Path | None = None, only: list[str] | None = None) -> int:
    """Every log of `EXPORTS`, or only those named (`python scripts/orb_trades_export.py orb_bracket_best`)."""
    from propedge import RESULTS_DIR
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = s3.config()
    d, sess, have = s3.load(rd, cfg)
    if set(have) != set(cfg["runs"]):
        print(f"REFUSED: ORB3's three runs are needed, ingested: {have}.")
        return 2
    days = sorted(d["date"].astype(str).unique())                 # every session with a record, FOMC days too
    d = d[~d["date"].astype(str).isin(s3.fomc_dates(cfg))]
    fm = FillModel.load("assumed")
    q = params("NQ")
    fee, slip, flat_slip = float(fm.round_turn_by_instrument[q["micro"]]), float(fm.stop_slippage_ticks), float(
        fm.flatten_slippage_ticks)
    grid = s3.Grid(d, cfg, fee, slip, flat_slip, q["micro_tick"] * q["micro_point_value"])
    for name, spec in EXPORTS.items():
        if only and name not in only:
            continue
        t = trades(grid, spec, fee, slip, flat_slip)
        log = trade_log(t)
        counts = pd.Series(pd.to_datetime(t["date"]).dt.strftime("%Y-%m-%d")).value_counts()
        dayset = pd.DataFrame({"date": days, "entries": [int(counts.get(x, 0)) for x in days]})
        params_ = {"configuration": {k: (list(v) if isinstance(v, tuple) else v) for k, v in spec.items()},
                   "reading": "strict", "positions": "one at a time", "fill_profile": "assumed", "fee": fee,
                   "prices": f"constructed: entry {NOMINAL_ENTRY:,.2f} nominal on every trade, the rest at the "
                             "recorded distances (risk and P&L exact)",
                   "mae": "an upper bound from the stop grid's first passages",
                   "decision": spec.get("decision", "D-261")}
        write_result(log, f"orb_studio_{name}_trades", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                     results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: scored outcomes re-presented for the Campaign Studio; no verdict"},
                     description=f"EXPLORATORY: {name} as a Campaign Studio trade log (one MNQ per trade, constructed "
                                 f"prices, exact risk and P&L) -- {spec['source']}.")
        write_result(dayset, f"orb_studio_{name}_days", script=SCRIPT, seed=None, require_seed=False,
                     exploratory=True, results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: the log's day set, days without a trade included"},
                     description=f"EXPLORATORY: {name}'s day set -- every session with a record, FOMC days and other "
                                 "days without a trade included; early closes are not recorded.")
        print(f"{name}: {len(log)} trades over {len(days)} sessions ({int((dayset['entries'] == 0).sum())} without "
              f"a trade); {log['exit_reason'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    unknown = [x for x in sys.argv[1:] if x not in EXPORTS]
    if unknown:
        raise SystemExit(f"no such export: {unknown}; the exports are {list(EXPORTS)}")
    raise SystemExit(main(only=sys.argv[1:] or None))
