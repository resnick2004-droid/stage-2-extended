"""EXPLORATORY (D-242): NQB2's stop distribution for its model card (D-191, D-201, D-212) -- one row per bracket the
development counts hold at its setting.

    python scripts/nqb2_card_stops.py

NQB2 (`docs/candidates/cards/NQB2.md`) is D-241's setting: NQ at actual prices, 2020-01-01 to 2025-06-30 (R090), the
Combine's 2:1 bracket on 20 points and the funded account's 1.5:1 on 40, at the registered decision slots
(`config/nqb2_confirmation.yaml`). The card's checks read a stop distribution with each entry's market, stop in the
micro's ticks, lifecycle state, exit (target, stop or flatten) and date. The counts carry no days, only years, so each
bracket is a row dated by its year; early closes add no count (D-238). Writes results/nqb2_screen_stops.csv. Nothing
new is read: it re-expresses counts already in the repository.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

import today_noedge_campaign as tnc  # noqa: E402

SCRIPT = "scripts/nqb2_card_stops.py"


def rows(cnt: pd.DataFrame, c: dict, micro_tick: float) -> pd.DataFrame:
    x = cnt[(cnt["kind"] == "count") & (cnt["market"] == c["market"])
            & cnt["decision_slot"].isin([int(s) for s in c["decision_slots"]])]
    parts = []
    for state in ("combine", "funded"):
        R, stop = float(c["legs"][state]["R"]), float(c["legs"][state]["stop_points"])
        g = x[(x["R"] == R) & (x["stop_value"] == stop)].groupby("year")[["target", "stop", "open"]].sum()
        ticks = int(round(stop / micro_tick))
        for year, r in g.iterrows():
            for exit_, n in (("target", r["target"]), ("stop", r["stop"]), ("flatten", r["open"])):
                parts.append(pd.DataFrame({"market": c["market"], "state": state, "stop_ticks": ticks, "exit": exit_,
                                           "date": str(int(year))}, index=range(int(n))))
    return pd.concat(parts, ignore_index=True)


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data.regime_kit import confirm_config, params
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    c = confirm_config()
    out = rows(tnc.now_counts(RESULTS_DIR), c, params(c["market"])["micro_tick"])
    write_result(out, "nqb2_screen_stops", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=rd, parameters={"market": c["market"], "legs": c["legs"],
                                             "decision_slots": c["decision_slots"], "years": list(tnc.YEARS),
                                             "source": "R090 (actual prices, D-238)", "decision": "D-242"},
                 description="EXPLORATORY: NQB2's development brackets, one row each (market, state, stop in the "
                             "micro's ticks, exit, year), for its model card's D-191, D-201 and D-212 checks. No seed: "
                             "counts re-expressed, nothing drawn.")
    print(out.groupby(["state", "exit"]).size().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
