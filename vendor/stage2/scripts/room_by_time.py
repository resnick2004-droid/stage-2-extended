"""EXPLORATORY (T17 item 4): what the regime map already says about FV3's four sessions -- how much NQ moves and trades
in each, and whether brackets on the ladder's stops resolve within the day from decisions made there (the operator,
2026-10-05: which times offer enough volume to trade the higher-risk positions). Read from results/regime_then_now.csv
(R090-R094, D-238/D-239); no new data, nothing selected.

    python scripts/room_by_time.py

Per session (the 6 PM reopen 17:00-18:30 CT, Asia 19:00-20:30, New York AM 08:30-10:00, PM 13:00-14:00): the map's
half-hour windows' volume and range a day, then and now, and against the AM's first half-hour; and for fixed stops of
10, 20, 40 and 60 points (the ladder's 12.5 / 25 / 50 bracketed) at 1R, 1.5R, 2R and 3R, from the decision times in
the session: the share resolved within the day (n-weighted over the session's decision slots), the mean minutes to
resolution, the spread at the decision, the cost in R, whether the 98 % resolution floor holds in every year, and the
micros a $1,000 funded trade carries on that stop -- now (2020 to June 2025) with then (2009-2019) beside.

Writes results/room_by_time.csv (`window`, `bracket` rows).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/room_by_time.py"
SOURCE = "results/regime_then_now.csv"
SESSIONS = {
    "eve": ("17:00", "17:30", "18:00", "18:30"),
    "asia": ("19:00", "19:30", "20:00", "20:30"),
    "am": ("08:30", "08:35", "08:40", "08:45", "08:50", "08:55", "09:00", "09:30", "10:00"),
    "pm": ("13:00", "13:30", "14:00"),
}
WINDOWS = {"eve": ("17:00", "17:30", "18:00"), "asia": ("19:00", "19:30", "20:00"), "am": ("08:30", "09:00", "09:30"),
           "pm": ("13:00", "13:30")}
STOPS = (10.0, 20.0, 40.0, 60.0)
RRS = (1.0, 1.5, 2.0, 3.0)
REFERENCE = "08:30"


def reading(d: pd.DataFrame) -> pd.DataFrame:
    nq = d[d["market"] == "NQ"]
    w = nq[nq["section"] == "window"]
    ref = w[w["window_ct"] == REFERENCE].iloc[0]
    rows = []
    for name, wins in WINDOWS.items():
        x = w[w["window_ct"].isin(wins)]
        rows.append({"section": "window", "session": name, "windows": "+".join(wins),
                     "now_volume_per_day": float(x["now_volume_per_day"].mean()),
                     "now_range_points_per_day": float(x["now_range_points_per_day"].mean()),
                     "now_volume_vs_am_open": float(x["now_volume_per_day"].mean() / ref["now_volume_per_day"]),
                     "now_range_vs_am_open": float(x["now_range_points_per_day"].mean() / ref["now_range_points_per_day"]),
                     "then_volume_per_day": float(x["then_volume_per_day"].mean()),
                     "then_range_points_per_day": float(x["then_range_points_per_day"].mean())})
    c = nq[(nq["section"] == "cell") & (nq["stop_kind"] == "points")]
    for name, slots in SESSIONS.items():
        s = c[c["decision_ct"].isin(slots)]
        for stop in STOPS:
            for rr in RRS:
                x = s[(s["stop_value"] == stop) & (s["R"] == rr)]
                if not len(x):
                    continue
                row = {"section": "bracket", "session": name, "stop_points": stop, "R": rr,
                       "decision_slots": int(len(x))}
                for era in ("now", "then"):
                    n = x[f"{era}_n"].to_numpy(float)
                    wt = n / n.sum() if n.sum() > 0 else np.full(len(n), 1.0 / len(n))
                    row[f"{era}_n"] = float(n.sum())
                    for col in ("resolved_share", "mean_minutes", "spread_ticks_mean", "cost_r", "funded_micros",
                                "combine_micros", "target_share_of_resolved"):
                        v = x[f"{era}_{col}"].to_numpy(float)
                        ok = np.isfinite(v)
                        row[f"{era}_{col}"] = float((v[ok] * wt[ok]).sum() / wt[ok].sum()) if ok.any() else float("nan")
                    m = x[f"{era}_meets_98_every_year"]
                    row[f"{era}_meets_98_share_of_slots"] = float(m.astype(str).str.lower().eq("true").mean())
                rows.append(row)
    return pd.DataFrame(rows)


def main(results_dir: Path | None = None, *, dry: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result, write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    d = read_result(rd / "regime_then_now.csv")
    out = reading(d)
    if dry is not None:
        out.to_csv(dry, index=False)
    else:
        write_result(out, "room_by_time", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                     results_dir=results_dir, parameters={"source": SOURCE, "sessions": {k: list(v) for k, v in SESSIONS.items()},
                                                          "windows": {k: list(v) for k, v in WINDOWS.items()},
                                                          "stops_points": list(STOPS), "rrs": list(RRS), "reference_window": REFERENCE,
                                                          "task": "T17 item 4"},
                     notes={"status": "EXPLORATORY: a reading of the regime map for FV3's sessions; no new data, nothing selected"},
                     description="FV3's four sessions in the regime map: volume and range a day per session, then and now, "
                                 "and the resolution, minutes, spread, cost and micros of fixed-stop brackets decided in "
                                 "each session.")
    pd.set_option("display.width", 250)
    print(out[out["section"] == "window"].round(3).to_string(index=False))
    b = out[out["section"] == "bracket"]
    print(b[["session", "stop_points", "R", "now_n", "now_resolved_share", "now_mean_minutes", "now_spread_ticks_mean",
             "now_cost_r", "now_funded_micros", "now_meets_98_share_of_slots", "then_resolved_share"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(dry=Path(sys.argv[1]) if len(sys.argv) > 1 else None))
