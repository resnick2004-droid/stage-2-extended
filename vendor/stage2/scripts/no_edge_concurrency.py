"""EXPLORATORY (D-220, T14 item 7): does carrying less loss risk on one day -- fewer Combines live at once -- keep the
no-edge campaign off the Responsible Trading Program, and what does it do to the cost per trade the contract absorbs?

    python scripts/no_edge_concurrency.py [--paths 500] [--workers 4]

D-218 found every no-edge campaign placed in the program within its first days by "Multiple accounts hit the Maximum
Loss Limit in one day" (13620045): five Combines start together and two fail on the same day early. D-27 read that
trigger as an argument for de-correlating the group (staggered entry, fewer accounts at once); D-34 made the most
Combines live at once, `max_concurrent_combines`, a protocol parameter bounded at 5. This runs part 1's
`s1_zero_edge_static` geometry -- Combine 1:1 $1,500, funded static 2:1 $750, one trade a day, part 1's largest c*
(propsim D-08, D-10, D-15; D-150) -- with at most 1, 2, 3 or 5 Combines live at once, five accounts in total
throughout (5 is part 1 as run). A Combine is bought only when a slot frees, so a lower cap is also a staggered entry;
a stagger by calendar days would need an engine change and is not run. Each at two readings of placement timing
(D-220): the engine's strictest, placement the day after the first trigger day (`rtp_warnings` = 0, the gate's
reading), and one warning first (`rtp_warnings` = 1; 13620045: "warnings will often be sent out first"), reported
beside it, never instead.

Everything else is part 1's (D-213; `no_edge_contract.campaign`): stage one's binary process, the five-account engine,
e = -0.25 to +0.05 R in steps of 0.025 on common random numbers, denial 0 (the operator's reading) and 0.25 beside it,
500 paths, the seed. Writes results/no_edge_concurrency.csv: part 1's `curve` measures per point plus the share of
paths placed, the placement day's median and the share of funded accounts forced onto the Consistency path; and one
`break_even` row per cap, reading and denial with e* (D-150's zero crossing) and c* = -e*. **The engine check first**,
as part 1's: at e = 0 the first Combine's pass rate at 1:1 $1,500 must not exceed stage one's 16/49 by more than the
sampling error. An arm changes how much risk is live at once; none arranges when losses fall so that the firm does not
see them together (D-145 tier 1; propsim D-35).
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

SCRIPT = "scripts/no_edge_concurrency.py"
ARM = "s1_zero_edge_static"
CAPS = (1, 2, 3, 5)                               # the most Combines live at once; 5 is part 1 as run
WARNINGS = (0, 1)                                 # D-220: the strictest reading (the gate's), one warning first


def point(job: tuple) -> dict:
    """One campaign: a cap and a timing reading at an edge and a denial level."""
    warnings.filterwarnings("ignore")
    cap, w, e, denial, n_paths = job
    summary, paths = nec.campaign(ARM, e, denial, n_paths, combines=cap, rtp_warnings=w)
    row = nec.point_row(ARM, e, denial, summary, paths)
    days = np.array([p.conduct.get("rtp_placed_day", -1) for p in paths])
    funded = [f for p in paths for f in p.funded]
    row.update({"combines_at_once": int(cap), "rtp_warnings": int(w),
                "placement_day_p50": float(np.median(days[days >= 0])) if (days >= 0).any() else float("nan"),
                "share_funded_consistency_forced": (float(np.mean([f.consistency_forced for f in funded]))
                                                    if funded else float("nan"))})
    return row


def main(n_paths: int = 500, results_dir: Path | None = None, workers: int = 4, record: bool = True) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.breakeven import zero_crossing
    from propedge.reporting.pin import engine_pin
    from propedge.reporting.results import write_result

    jobs = [(c, w, e, d, n_paths) for c in CAPS for w in WARNINGS for d in nec.DENIALS for e in nec.EDGES]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(point, jobs))
    print(f"{len(jobs)} campaigns of {n_paths} paths in {time.time() - t0:.0f}s", flush=True)
    check = nec.engine_check(rows, n_paths)
    print(check, flush=True)
    curve = pd.DataFrame(rows)
    be = []
    for (c, w, d), g in curve.groupby(["combines_at_once", "rtp_warnings", "denial_p"], sort=False):
        g = g.sort_values("edge")
        e_star = zero_crossing(g["edge"], g["median_log_growth"])
        z = g[g["edge"] == 0.0].iloc[0]
        be.append({"section": "break_even", "arm": ARM, "combines_at_once": c, "rtp_warnings": w, "denial_p": d,
                   "e_star": e_star, "c_star": -e_star if np.isfinite(e_star) else float("nan"),
                   "median_log_growth": float(z["median_log_growth"]), "ruin_probability": float(z["ruin_probability"]),
                   "edge": 0.0, "first_combine_pass_rate": float(z["first_combine_pass_rate"]),
                   "share_paths_rtp_placed": float(z["share_paths_rtp_placed"])})
    out = pd.concat([curve, pd.DataFrame(be)], ignore_index=True)
    write_result(out, "no_edge_concurrency", script=SCRIPT, seed=nec.SEED, exploratory=True, results_dir=results_dir,
                 provenance={"engine": engine_pin()},
                 parameters={"arm": ARM, "combines_at_once": list(CAPS), "rtp_warnings": list(WARNINGS),
                             "edges": list(nec.EDGES), "denials": list(nec.DENIALS), "n_paths": n_paths,
                             "total_accounts": nec.ACCOUNTS, "bankroll": nec.BANKROLL, "horizon_days": nec.HORIZON,
                             "draw": "stage one's binary process", "rules": "rules_for_method('aeropay')",
                             "campaign": "no_edge_contract.campaign (part 1's call and seed)",
                             "engine_check": check, "decision": "D-220"},
                 notes={"status": "EXPLORATORY: D-220, T14 item 7, fixed before it ran; read at denial 0 (the "
                                  "operator) with D-145's 25 % beside it, and at the strictest placement timing with "
                                  "one warning first beside it"},
                 description="EXPLORATORY: the no-edge contract test with at most 1, 2, 3 or 5 Combines live at once "
                             "(part 1's 1:1 $1,500 geometry), at the strictest RTP placement timing and with one "
                             "warning first, at denial 0 and 0.25: the growth curve, placement and the break-even c*.")
    if record:
        VariantCounter().record(prereg_id="D-220:no_edge_concurrency", seed=nec.SEED, exploratory=True,
                                params={"study": "T14 item 7, synthetic", "arm": ARM, "combines_at_once": list(CAPS),
                                        "rtp_warnings": list(WARNINGS), "edges": list(nec.EDGES),
                                        "denials": list(nec.DENIALS), "n_paths": n_paths},
                                label="EXPLORATORY: fewer Combines live at once against RTP placement, no edge")
    pd.set_option("display.width", 220)
    print(pd.DataFrame(be).round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=500)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    raise SystemExit(main(n_paths=a.paths, workers=a.workers))
