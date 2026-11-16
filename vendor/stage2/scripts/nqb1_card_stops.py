"""EXPLORATORY (D-229): NQB1's stop distribution for its model card (D-191, D-212) -- one row per bracket the
development counts hold at its setting.

    python scripts/nqb1_card_stops.py

NQB1 (`docs/candidates/cards/NQB1.md`) is D-226's setting: NQ at today's price level (D-225; R084, R085), the
Combine's 1:1 bracket at $125 a micro and the funded account's 2:1 bracket at $75, at the decision times where both
resolve (`nq_noedge_campaign.times`). The card's checks read a stop distribution with each entry's market, stop in
the micro's ticks, lifecycle state, exit (target, stop or flatten) and date. The counts carry no days, only years, so
each bracket is a row dated by its year; full sessions only, as D-215 counts early closes apart. Writes
results/nqb1_screen_stops.csv. Nothing new is read: it re-expresses counts already in the repository.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

import nq_noedge_campaign as q  # noqa: E402

SCRIPT = "scripts/nqb1_card_stops.py"
STATES = {"combine": q.LEGS["combine"], "funded": q.LEGS["funded"]}       # (R, stop dollars per micro)


def rows(cnt: pd.DataFrame, slots: list[int], tick_dollars: float) -> pd.DataFrame:
    c = cnt[(cnt["kind"] == "count") & (cnt["day_type"] == "full") & cnt["decision_slot"].isin(slots)]
    parts = []
    for state, (R, stop) in STATES.items():
        g = c[(c["R"] == R) & (c["stop_dollars"] == stop)].groupby("year")[["target", "stop", "open"]].sum()
        ticks = int(round(stop / tick_dollars))
        for year, r in g.iterrows():
            for exit_, n in (("target", r["target"]), ("stop", r["stop"]), ("flatten", r["open"])):
                parts.append(pd.DataFrame({"market": q.MARKET, "state": state, "stop_ticks": ticks, "exit": exit_,
                                           "date": str(int(year))}, index=range(int(n))))
    return pd.concat(parts, ignore_index=True)


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.rmap_kit import params
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    p = params(q.MARKET)
    out = rows(q.counts(RESULTS_DIR), q.times(RESULTS_DIR), p["micro_tick"] * p["micro_point_value"])
    write_result(out, "nqb1_screen_stops", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=rd, parameters={"market": q.MARKET, "states": {k: list(v) for k, v in STATES.items()},
                                             "decision_slots": q.times(RESULTS_DIR), "day_type": "full",
                                             "sources": "R084, R085 (today's price level, D-225)", "decision": "D-229"},
                 description="EXPLORATORY: NQB1's development brackets, one row each (market, state, stop in the "
                             "micro's ticks, exit, year), for its model card's D-191 and D-212 checks. No seed: counts "
                             "re-expressed, nothing drawn.")
    print(out.groupby(["state", "exit"]).size().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
