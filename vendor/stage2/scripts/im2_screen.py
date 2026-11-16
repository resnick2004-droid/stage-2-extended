"""IM2's cheap screen (D-155 step 3), exactly as declared in docs/candidates/drafts/IM2.md §3 before it ran.

    python scripts/im2_screen.py

A proxy on the bracket map (R049-R052; ES and NQ, 2009-06 .. 2019-12, development only): decision times 09:00-12:30 CT;
long when the distance from the 08:30 open is at least +0.2 D and price is above VWAP, short when at most -0.2 D and
below VWAP; the session-scale stop (0.4 D) for the opposite band. Per market: (a) the first qualifying entry each
day at 1:1, mean R net and its 20-day block lower bound; (b) the baseline -- every entry at those times, long and
short together; (c) s, the share of qualifying entries whose 3:1 bracket resolves before 15:00; (d) qualifying
decision times per day and the share of days with at least one; (e) mean R net at 3:1 and 2:1. Kill line: killed if
on both markets (a)'s mean R net at 1:1 is not above (b)'s. Writes results/im2_screen.csv (EXPLORATORY).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.execution.fills import FillModel  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import bmap_score as bs  # noqa: E402

SCRIPT = "scripts/im2_screen.py"
SEED = 20261118
WI = 2                                                   # the session-scale stop, 0.4 D
TIMES = {"09:00": 60, "09:30": 90, "10:00": 120, "10:30": 150, "11:00": 180, "11:30": 210, "12:00": 240, "12:30": 270}
BLOCK, REPS = 20, 10_000


def qualifies(ent: pd.DataFrame) -> pd.Series:
    """The proxy condition; bucket 9 (unknown) never qualifies."""
    known = (ent["f_fv"] != 9) & (ent["f_vwap"] != 9)
    long_ = (ent["side"] == 1) & (ent["f_fv"] >= 4) & (ent["f_vwap"] >= 3)
    short = (ent["side"] == -1) & (ent["f_fv"] <= 1) & (ent["f_vwap"] <= 2)
    return known & (long_ | short)


def main() -> int:
    cfg = yaml.safe_load((ROOT / "config" / "bracket_map.yaml").read_text(encoding="utf-8"))
    fm = FillModel.load("assumed")
    rows = []
    for market, runs in cfg["runs"].items():
        mk = cfg["markets"][market]
        fills = {"target": fm.target_slippage_ticks, "stop": fm.stop_slippage_ticks,
                 "flatten": fm.flatten_slippage_ticks, "round_turn": float(mk["round_turn"]),
                 "tick_value": float(mk["tick_value"])}
        parts = [bs.split(read_result(ROOT / "results" / f"manual_{r.replace('-', '_')}.csv")) for r in runs]
        days = pd.concat([p[0].assign(n=p[0]["n"] + 100_000 * i) for i, p in enumerate(parts)], ignore_index=True)
        ent = pd.concat([p[1].assign(n=p[1]["n"] + 100_000 * i) for i, p in enumerate(parts)], ignore_index=True)
        day_ns = days.loc[days["ok"], "n"].tolist()
        at_times = ent[ent["t"].isin(TIMES.values())]
        q = at_times[qualifies(at_times)].sort_values(["n", "t"])
        first = q.groupby("n", sort=False).head(1)
        row = {"market": market, "days": len(day_ns), "decision_times_ct": "09:00-12:30",
               "qualifying_entries": int(len(q)), "days_with_an_entry": int(first["n"].nunique()),
               "share_days_with_an_entry": float(first["n"].nunique() / len(day_ns)),
               "qualifying_times_per_day": float(len(q) / len(day_ns))}
        for k in (1.0, 2.0, 3.0):
            s_first = bs.summarise(bs.outcome(first, WI, k, fills), day_ns, block=BLOCK, reps=REPS, seed=SEED)
            tag = f"{k:g}to1"
            row[f"proxy_first_e_{tag}"], row[f"proxy_first_e_lb_{tag}"] = s_first["e"], s_first["e_lb"]
            row[f"proxy_first_win_rate_{tag}"] = s_first["win_rate"]
            row[f"proxy_all_e_{tag}"] = float(bs.outcome(q, WI, k, fills).query("ok")["r_net"].mean())
        base = bs.summarise(bs.outcome(at_times, WI, 1.0, fills), day_ns, block=BLOCK, reps=REPS, seed=SEED)
        row["baseline_e_1to1"], row["baseline_e_lb_1to1"], row["baseline_entries"] = base["e"], base["e_lb"], base["entries"]
        o3 = bs.outcome(q, WI, 3.0, fills).query("ok")
        row["s_share_3to1_resolved_before_close"] = float((o3["kind"] != "time").mean())
        row["lift_1to1"] = row["proxy_first_e_1to1"] - row["baseline_e_1to1"]
        rows.append(row)
    out = pd.DataFrame(rows)
    killed = bool((out["lift_1to1"] <= 0).all())
    out["screen_verdict"] = "kill" if killed else "continue"
    VariantCounter().record(prereg_id="IM2:screen", params={"design": "docs/candidates/drafts/IM2.md §3",
                            "markets": list(out["market"]), "times": list(TIMES)}, seed=SEED, exploratory=True,
                            label="IM2's cheap screen on the bracket map, a proxy, not a test")
    write_result(out, "im2_screen", script=SCRIPT, seed=SEED, exploratory=True,
                 parameters={"design": "docs/candidates/drafts/IM2.md §3 (declared in commit 97b0ddd before it ran)",
                             "proxy": "f_fv >= 4 and f_vwap >= 3 long; f_fv <= 1 and f_vwap <= 2 short; 0.4 D stop",
                             "times_ct": list(TIMES), "block": BLOCK, "reps": REPS,
                             "kill_line": "killed if on both markets the first-entry mean R net at 1:1 is not above "
                                          "the baseline's"},
                 notes={"decision": "D-155 step 3; D-161", "status": "EXPLORATORY: a proxy screen on development "
                        "data, not a test; the bracket map has no noise band and no CL, 6E or NG"},
                 description="IM2's cheap screen: the noise-band-and-VWAP entry condition proxied on the bracket map, "
                             "against the no-information baseline, with the day-one bracket's completion share and "
                             "the setup rate.")
    pd.set_option("display.width", 250)
    print(out.T.to_string())
    print("screen verdict:", "kill" if killed else "continue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
