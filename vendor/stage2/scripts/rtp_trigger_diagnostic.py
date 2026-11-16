"""EXPLORATORY (D-218): which Responsible Trading Program trigger places part 1's campaigns, on what day, and what the
placement does to the accounts that follow.

    python scripts/rtp_trigger_diagnostic.py [--paths 500] [--workers 4]

D-217 added two Combine geometries whose winners are larger than their losers, on the reading that the RTP's "losers
not smaller than winners" trigger placed part 1's campaigns; every path of the added arms was placed all the same. This
reruns the very campaigns of results/no_edge_contract.csv and results/no_edge_contract_added.csv
(`no_edge_contract.campaign`: the same arms, seed and path count) at e = -0.10, 0 and +0.05, denial 0 -- the operator's
reading for D-213 -- and records per arm and edge: the share of paths placed, the share placed by each trigger the
engine checks (`lockstep.ConductModel`: "Multiple accounts hit the Maximum Loss Limit in one day", "You don't keep
losers smaller than winners", "You max position a majority of your trades"; 13620045), the placement day's 10th, 50th
and 90th percentiles, the accounts at the loss limit on that day, and the Combines bought and funded accounts activated
before and after it -- a Combine bought after placement is a Consistency Trading Combine, and its funded account is on
the Consistency path. D-220 adds a second reading beside the engine's strictest one (placement the day after the first
trigger day): one warning first, placement on the second trigger day (`ConductModel.rtp_warnings` = 1; 13620045:
"warnings will often be sent out first"). Writes results/rtp_trigger_diagnostic.csv. A diagnosis, not a variant: no
configuration is new.
"""
from __future__ import annotations

import argparse
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import no_edge_contract as nec  # noqa: E402

SCRIPT = "scripts/rtp_trigger_diagnostic.py"
EDGES = (-0.1, 0.0, 0.05)
DENIAL = 0.0
WARNINGS = (0, 1)                                 # D-220: the strictest reading, and one warning first
TRIGGERS = {"multi_mll": "multiple accounts hit the MLL in one day",
            "losers": "losers not smaller than winners",
            "max_position": "maximum position on most trades"}


def point(job: tuple) -> dict:
    """One arm at one edge: the placement measures over its paths."""
    warnings.filterwarnings("ignore")
    name, e, n_paths, w = job if len(job) == 4 else (*job, 0)
    _, paths = nec.campaign(name, e, DENIAL, n_paths, rtp_warnings=w)
    days = np.array([p.conduct.get("rtp_placed_day", -1) for p in paths])
    placed = days >= 0
    trig = [p.conduct.get("rtp_trigger", "") for p in paths]
    at_mll = [int(p.breaches_per_day[d]) for p, d in zip(paths, days) if d >= 0]
    q = np.percentile(days[placed], [10, 50, 90]) if placed.any() else [np.nan] * 3
    funded = [f for p in paths for f in p.funded]
    row = {"arm": name, "edge": float(e), "denial_p": DENIAL, "rtp_warnings": int(w), "n_paths": len(paths),
           "share_placed": float(placed.mean())}
    for key, text in TRIGGERS.items():
        row[f"share_trigger_{key}"] = float(np.mean([t == text for t in trig]))
    row.update({
        "placement_day_p10": float(q[0]), "placement_day_p50": float(q[1]), "placement_day_p90": float(q[2]),
        "mean_accounts_at_mll_on_placement_day": float(np.mean(at_mll)) if at_mll else float("nan"),
        "mean_combines_standard": float(np.mean([sum(not c.rtp for c in p.combines) for p in paths])),
        "mean_combines_rtp": float(np.mean([sum(c.rtp for c in p.combines) for p in paths])),
        "mean_funded_standard_path": float(np.mean([sum(not f.consistency_forced for f in p.funded) for p in paths])),
        "mean_funded_consistency_forced": float(np.mean([sum(f.consistency_forced for f in p.funded)
                                                         for p in paths])),
        "share_funded_consistency_forced": (float(np.mean([f.consistency_forced for f in funded])) if funded
                                            else float("nan")),
    })
    return row


def main(n_paths: int = 500, results_dir: Path | None = None, workers: int = 4) -> int:
    from propedge.reporting.pin import engine_pin
    from propedge.reporting.results import write_result

    jobs = [(a, e, n_paths, w) for w in WARNINGS for a in nec.ARMS + nec.ARMS_ADDED for e in EDGES]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(point, jobs))
    print(f"{len(jobs)} campaigns of {n_paths} paths in {time.time() - t0:.0f}s", flush=True)
    out = pd.DataFrame(rows)
    write_result(out, "rtp_trigger_diagnostic", script=SCRIPT, seed=nec.SEED, exploratory=True,
                 results_dir=results_dir, provenance={"engine": engine_pin()},
                 parameters={"arms": list(nec.ARMS + nec.ARMS_ADDED), "edges": list(EDGES), "denial_p": DENIAL,
                             "rtp_warnings": list(WARNINGS),
                             "n_paths": n_paths, "campaign": "no_edge_contract.campaign (part 1's call and seed)",
                             "triggers": TRIGGERS, "decision": "D-218, D-220"},
                 notes={"status": "EXPLORATORY: D-218's diagnosis of D-217; no new configuration"},
                 description="EXPLORATORY: which RTP trigger places the no-edge campaigns (D-213 part 1 and D-217's "
                             "arms), on what day, and the Combines and funded accounts before and after placement; "
                             "at the engine's strictest reading and with one warning first (D-220).")
    pd.set_option("display.width", 250)
    print(out.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=500)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    raise SystemExit(main(n_paths=a.paths, workers=a.workers))
