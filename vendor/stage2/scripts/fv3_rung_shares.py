"""The rungs' shares in today's regime (D-306): from the corrected gate's exported trades, the share of signals at each
rung (half / full / double) per phase and overall, from the declared start date -- the mixture the allowance-aware
state table solves over (`propedge.campaign.state_policy`, export version 3). Reads results/fv3_studio_gate_corrected_
point_trades.csv (the trades as traded; the rung is the ladder's, D-293) and writes results/fv3_rung_shares_2020.csv
with a manifest. A derived input, declared with the run that uses it; no outcome enters it.

    python scripts/fv3_rung_shares.py --declaration D-306 [--start 2020-01-01]

D-318: with `--availability` it writes instead results/fv3_rung_availability_2020.csv -- per phase and rung, the share of
the trades whose room permits a target at each R the log carries (its `r_net_<R>` column is filled; the room rule is read
at entry, so this is a property of the setups, not of their outcomes): the availability the state table (export version
6) solves with. The shares file is left as it is.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

SCRIPT = "scripts/fv3_rung_shares.py"
RUNGS = ("half", "full", "double")


def shares(log: pd.DataFrame, start: str) -> pd.DataFrame:
    """Per phase and overall: n and the share of each rung among trades entered on or after `start`."""
    t = log[log["timestamp_in"].astype(str).str[:10] >= start]
    if not len(t):
        raise SystemExit(f"REFUSED: no trade on or after {start}.")
    rows = []
    for phase, g in [("all", t)] + list(t.groupby("fv3_phase")):
        n = len(g)
        counts = g["fv3_rung"].value_counts()
        for r in RUNGS:
            rows.append({"phase": phase, "rung": r, "n": int(counts.get(r, 0)), "share": float(counts.get(r, 0) / n),
                         "stop_ticks_median": float(g[g["fv3_rung"] == r]["stop_ticks"].median()) if counts.get(r, 0) else float("nan"),
                         "from": start, "trades": int(n)})
    return pd.DataFrame(rows)


def availability(log: pd.DataFrame, start: str) -> pd.DataFrame:
    """D-318: per phase (and overall) and rung, for every R the log carries, the share of trades entered on or after
    `start` with an outcome at that R -- the room rule's permission, read at entry."""
    t = log[log["timestamp_in"].astype(str).str[:10] >= start]
    if not len(t):
        raise SystemExit(f"REFUSED: no trade on or after {start}.")
    cols = sorted(((float(c[len("r_net_"):]), c) for c in t.columns
                   if c.startswith("r_net_") and c[len("r_net_"):].replace(".", "", 1).isdigit()))
    if not cols:
        raise SystemExit("REFUSED: the log carries no outcome by R (r_net_<R> columns).")
    rows = []
    for phase, g in [("all", t)] + list(t.groupby("fv3_phase")):
        for r in RUNGS:
            gr = g[g["fv3_rung"] == r]
            for R, c in cols:
                n_ok = int(gr[c].notna().sum())
                rows.append({"phase": phase, "rung": r, "rr": R, "n": int(len(gr)), "with_outcome": n_ok,
                             "share": float(n_ok / len(gr)) if len(gr) else float("nan"), "from": start})
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None, results_dir: Path | None = None, log: pd.DataFrame | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--declaration", required=True)
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--source", default="fv3_studio_gate_corrected_point_trades")
    ap.add_argument("--availability", action="store_true", help="D-318: write each rung's availability by R instead")
    a = ap.parse_args(argv)
    if f"| {a.declaration} |" not in (ROOT / "DECISIONS.md").read_text(encoding="utf-8"):
        print(f"REFUSED: no decision row {a.declaration} in DECISIONS.md.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if log is None:
        log = pd.read_csv(rd / f"{a.source}.csv", low_memory=False)
    if a.availability:
        av = availability(log, a.start)
        write_result(av, f"fv3_rung_availability_{a.start[:4]}", script=SCRIPT, seed=None, require_seed=False,
                     exploratory=True, results_dir=results_dir,
                     parameters={"source": f"results/{a.source}.csv", "start": a.start, "decision": a.declaration,
                                 "rungs": "the ladder's (D-293): half / full / double by the room rule",
                                 "availability": "a trade has an outcome at R when its room permits that target (the "
                                                 "room rule at entry; continuations at any R)"},
                     notes={"status": "a derived input to the state table (D-318, export version 6); no outcome enters "
                                      "it -- only whether the room rule permits each target"},
                     description=f"Each rung's share of FV3's gate trades from {a.start} whose room permits a target at "
                                 "each R, per phase and overall: the availability the state table solves with.")
        print(av[av["phase"] == "all"].pivot(index="rung", columns="rr", values="share").round(3).to_string())
        return 0
    out = shares(log, a.start)
    name = f"fv3_rung_shares_{a.start[:4]}"
    write_result(out, name, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=results_dir,
                 parameters={"source": f"results/{a.source}.csv", "start": a.start, "decision": a.declaration,
                             "rungs": "the ladder's (D-293): half / full / double by the room rule"},
                 notes={"status": "a derived input to the allowance-aware state table (D-306); no outcome enters it"},
                 description=f"The rungs' shares among FV3's gate trades from {a.start}, per phase and overall, with the "
                             "median stop in ticks: the mixture the state table solves over.")
    print(out.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
