"""EXPLORATORY (D-270): ORB5's captures as Campaign Studio trade logs, so the operator can replay the $1,500 Combine
target and the hand-traded entry (the operator, 2026-10-04: "please export the data to the campaign replay so I can
review it there as well"; the Studio is an inspection view, never a verdict -- D-155's step 7).

    python scripts/orb5_trades_export.py R105-orb5-NQ-0914

One configuration, fixed before any of the capture's outcomes was read: ORB4's ranges and stop (the 5- and 15-minute
ranges, the stop at 0.15 of the 14-day ATR, fills to 15:07, no volume filter, results/orb4_reselect.csv `final`), one
position at a time (D-160), the strict fill-bar reading, the assumed costs, and a bracket at 1R -- the $1,500 target of
stage one's 1:1 $1,500 Combine (propsim D-08; D-262, D-267) -- in four logs, so no entry is picked by looking:

* `l0` -- the original fill, as every earlier ORB result (the order working the moment the range closes);
* `skip`, `rest`, `chase` -- the operator's hand-traded entry at L = 5 minutes (D-266) under each missed-trigger
  policy: only the entries that are the original fill (`skip`); those and the stop resting at the level until it
  next trades through (`rest`); and those and the chase at the next bar's open (`chase`).

The trades are settled by ORB3's own arithmetic (`scripts/orb_trades_export.py`'s `trades` and `trade_log`, tested
against the scorer): ORB3's records of the same days (the ORB3 run each capture re-walks) with the passages swapped in
from the capture -- the 1R passage in the target column, and for the hand-traded entry its own bar, at-open flag,
fill-bar readings, 15:08 close and stop passages. As in D-261's logs, prices are constructed (risk, P&L and times
exact), a trade still open is closed at the 15:08 close (D-263's worst-of-15:07-15:10 flatten is ORB5's scoring, not
this view's), and the log carries one exit per trade, so the Studio's funded accounts trade the same 1R.

Writes results/orb5_studio_<run>_<entry>_trades.csv and _days.csv with manifests.
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
import score_orb3_search as s3  # noqa: E402
from propedge.outcomes.orb5_core import CHASE, LATE_STOP, SAME  # noqa: E402

SCRIPT = "scripts/orb5_trades_export.py"
CONFIG = {"mode": "bracket", "ranges": (5, 15), "rv_min": None, "stop_atr": 0.15, "last_fill_ct": "15:07", "R": 1.0,
          "source": "ORB4's final ranges and stop (results/orb4_reselect.csv, final) at the Combine's 1R, D-270"}
#: the entries: the original fill (None), and the hand-traded entry's kinds kept under each missed-trigger policy
ENTRIES = {"l0": None, "skip": (SAME,), "rest": (SAME, LATE_STOP), "chase": (SAME, CHASE, LATE_STOP)}
LAT_SWAP = ("fill_slot", "at_open", "fill_bar_close_ticks", "fill_bar_against_ticks", "close_ticks")


def frame(d3: pd.DataFrame, d5: pd.DataFrame, kinds: tuple | None, K: int) -> pd.DataFrame:
    """ORB3's day records with the entry wanted swapped in, so ORB3's arithmetic settles it at R = 1.0: the target
    column `f2_<i>` carries the entry's 1R passage (`orb_trades_export.trades` reads `f2` for any R but 1.5); for the
    hand-traded entry (`kinds` the kept kinds) also its bar, at-open flag, fill-bar readings, 15:08 close and stop and
    1.5R passages -- and no trade where its kind is not kept."""
    keys = ["date", "or_minutes"]
    lat = [f"lat_{c}" if c != "fill_slot" else "lat_slot" for c in LAT_SWAP]
    cols = keys + ["lat_kind"] + lat + [f"f1_{i}" for i in range(K)] + [f"lat_{x}_{i}" for i in range(K)
                                                                     for x in ("a", "f15", "f1")]
    m = d3.merge(d5[cols], on=keys, how="left", validate="one_to_one")
    if m["lat_kind"].isna().any():
        raise ValueError("ORB3's records and the capture do not cover the same days and ranges")
    out = m.copy()
    if kinds is None:
        for i in range(K):
            out[f"f2_{i}"] = m[f"f1_{i}"]
        return out[d3.columns]
    take = m["lat_kind"].isin(kinds).to_numpy()
    for c, lc in zip(LAT_SWAP, lat):
        out[c] = np.where(take, m[lc], -1 if c == "fill_slot" else 0)
    for i in range(K):
        out[f"a_{i}"] = m[f"lat_a_{i}"]
        out[f"f15_{i}"] = m[f"lat_f15_{i}"]
        out[f"f2_{i}"] = m[f"lat_f1_{i}"]
    return out[d3.columns]


def main(run: str, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data import orb5_kit as k5
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if run not in k5.ORB5_RUNS:
        print(f"REFUSED: {run} is not an ORB5 capture; they are {list(k5.ORB5_RUNS)}")
        return 2
    src5 = rd / f"manual_{run.replace('-', '_')}.csv"
    if not src5.is_file():
        print(f"REFUSED: {run} is not ingested ({src5.name} missing).")
        return 2
    cfg = s3.config()
    d, _, have = s3.load(rd, cfg)
    orb3 = k5.ORB5_RUNS[run]
    if orb3 not in have:
        print(f"REFUSED: {orb3}, the ORB3 run {run} re-walks, is not ingested.")
        return 2
    d5 = pd.read_csv(src5, low_memory=False)
    d5 = d5[d5["kind"] == "day"].copy()
    d5["or_minutes"] = d5["or_minutes"].astype(int)
    d5["date"] = d5["date"].astype(str)
    d = d[d["date"].astype(str).isin(set(d5["date"]))].copy()
    d["date"] = d["date"].astype(str)
    days = sorted(d["date"].unique())                                # every session with a record, FOMC days too
    d = d[~d["date"].isin(s3.fomc_dates(cfg))]
    fm = FillModel.load("assumed")
    q = params("NQ")
    fee, slip, flat_slip = float(fm.round_turn_by_instrument[q["micro"]]), float(fm.stop_slippage_ticks), float(
        fm.flatten_slippage_ticks)
    K = len(cfg["search"]["stop_atr"])
    for entry, kinds in ENTRIES.items():
        grid = s3.Grid(frame(d, d5, kinds, K), cfg, fee, slip, flat_slip, q["micro_tick"] * q["micro_point_value"])
        t = ox.trades(grid, CONFIG, fee, slip, flat_slip)
        log = ox.trade_log(t)
        counts = pd.Series(pd.to_datetime(t["date"]).dt.strftime("%Y-%m-%d")).value_counts()
        dayset = pd.DataFrame({"date": days, "entries": [int(counts.get(x, 0)) for x in days]})
        name = f"orb5_studio_{run.split('-')[0]}_{entry}"
        params_ = {"configuration": {k: (list(v) if isinstance(v, tuple) else v) for k, v in CONFIG.items()},
                   "entry": entry, "kinds": None if kinds is None else list(kinds), "capture": run,
                   "orb3_run": orb3, "reading": "strict", "positions": "one at a time", "fill_profile": "assumed",
                   "fee": fee, "flatten": "the 15:08 close", "decision": "D-270"}
        write_result(log, f"{name}_trades", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                     results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: the capture's outcomes as a Campaign Studio log; no verdict"},
                     description=f"EXPLORATORY: {run}'s days, ORB4's ranges and stop at 1R, entry '{entry}' (D-270), "
                                 "as a Campaign Studio trade log (one MNQ per trade, constructed prices).")
        write_result(dayset, f"{name}_days", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                     results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: the log's day set, days without a trade included"},
                     description=f"EXPLORATORY: {name}'s day set -- every session with a record.")
        print(f"{name}: {len(log)} trades over {len(days)} sessions; {log['exit_reason'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/orb5_trades_export.py <ORB5 run, e.g. R105-orb5-NQ-0914>")
    raise SystemExit(main(sys.argv[1]))
