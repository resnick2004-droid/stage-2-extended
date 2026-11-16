"""EXPLORATORY (D-213, a first look before part 2's kits): how often a bracket resolves at its stop or target before
the close, from the bracket map's per-entry records on data already on hand.

    python scripts/resolution_screen.py

The bracket map (D-149; kits R049-R052, ES and NQ, 2009-06-01..2019-12-31) recorded every half-hourly decision from
08:35 to 14:00 CT, long and short, at three stop widths (0.1, 0.2 and 0.4 of the session's average range D), with how far
price went in the trade's favour before the stop (`mfe`, in R, capped 5.05) and whether the stop was hit by 15:00 CT
(`hit`). A bracket at R resolves when `mfe` >= R (the target first) or the stop was hit; otherwise it is still open at
15:00. Both sides pooled -- direction-neutral, no edge read -- per market, width, R and decision time: the resolved
share, the median stop in ticks and in dollars per micro (MES, MNQ), and the median cost per trade in R -- the micro's
round turn plus one tick each way (the `assumed` fill profile) over the stop in dollars -- set against D-213 part 1's
c* and D-212's 98 % resolution and size-cap rules. The window is the regular session only, ten minutes short of 15:10;
Topstep's full window from 17:00 is what part 2 measures. Writes results/resolution_screen.csv.
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

SCRIPT = "scripts/resolution_screen.py"
WIDTHS = ("0.1D", "0.2D", "0.4D")
RR = (1.0, 2.0)
MICROS = {"ES": "MES", "NQ": "MNQ"}


def records(market: str) -> tuple[pd.DataFrame, list[str]]:
    """The market's entry records with each day's stop ticks per width, from its four ingested runs."""
    from propedge.reporting.results import read_result

    files = sorted(glob.glob(str(ROOT / "results" / f"manual_R0[45]?_bmap_{market}_*.csv")))
    if len(files) != 2:
        raise ValueError(f"expected the two {market} bracket-map runs, found {files}")
    d = pd.concat([read_result(Path(f)) for f in files], ignore_index=True)
    days = d[d["kind"] == "day"].drop_duplicates("d").set_index("d")
    e = d[d["kind"] == "entry"].copy()
    for w in range(3):
        e[f"st{w}"] = e["d"].map(days[f"stop_ticks{w}"]).astype(float)
    return e, [Path(f).name for f in files]


def rows_for(market: str, e: pd.DataFrame, fm, inst) -> list[dict]:
    from propedge.execution.costs import ExitReason, trade_cost

    out = []
    for w, width in enumerate(WIDTHS):
        st = e[f"st{w}"]
        dollars = st * inst.tick_value
        drag = {x: trade_cost(fm, inst, contracts=1, dollars_risked=float(x), exit_reason=ExitReason.STOP).drag_fraction
                for x in dollars.dropna().unique()}
        cost = dollars.map(drag)
        for R in RR:
            res = (e[f"mfe{w}"] >= R) | (e[f"hit{w}"] > 0)
            for t, g in [("all", e.index)] + list(e.groupby("t").groups.items()):
                out.append({"market": market, "micro": inst.symbol if hasattr(inst, "symbol") else MICROS[market],
                            "width": width, "R": R, "decision_t": t, "entries": int(len(g)),
                            "resolved_share": float(res.loc[g].mean()),
                            "median_stop_ticks": float(st.loc[g].median()),
                            "median_stop_dollars_per_micro": float(dollars.loc[g].median()),
                            "median_cost_r": float(cost.loc[g].median())})
    return out


def main(results_dir: Path | None = None) -> int:
    from propedge.execution.fills import FillModel
    from propedge.execution.instruments import load_instruments
    from propedge.reporting.results import write_result

    fm = FillModel.load("assumed")
    inst = load_instruments()
    rows, sources = [], []
    for market, micro in MICROS.items():
        e, files = records(market)
        sources += files
        rows += rows_for(market, e, fm, inst[micro])
    out = pd.DataFrame(rows)
    write_result(out, "resolution_screen", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"sources": sources, "widths_of_D": list(WIDTHS), "R": list(RR), "fill_profile": "assumed",
                             "resolved": "mfe >= R or the stop hit before 15:00 CT; both sides pooled",
                             "window": "08:35-14:00 CT decisions, held to 15:00 CT", "decision": "D-213"},
                 notes={"status": "EXPLORATORY: a first look at bracket resolution before D-213 part 2's kits"},
                 description="EXPLORATORY: the share of brackets resolving at stop or target before 15:00 CT in the "
                             "bracket map's ES and NQ records, per stop width, R and decision time, with the stop in "
                             "dollars per micro and the cost per trade in R.")
    pd.set_option("display.width", 220)
    print(out[out["decision_t"] == "all"].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
