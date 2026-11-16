"""Run the pre-release drift screen (D-164, family K) once the two release kits are ingested.

    python scripts/screen_release_drift.py

1. Integrity, per market: HEAD's scheduled/emitted counts, the share of events excluded by the declared
   rules (roll, missing bars, substituted closes), and the median pre-end close against the market's price
   range. A market with fewer than the declared minimum of usable screen-half events stops the screen.
2. The screen: the three declared tests on 2009-06-01 to 2011-12-31, one-sided, Benjamini-Hochberg at
   q = 0.10 across the family.
3. The check: survivors only, once, on 2012-01-01 to 2014-05-27.

Writes results/effect_atlas_release.csv (exploratory research; never a candidate, never the confirmation
window). The result goes to 2B as the development-data outcome of its F-032.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research.release_screen import prepare_events, run_release_screen  # noqa: E402

CFG_PATH = ROOT / "config" / "effect_atlas.yaml"


def main() -> int:
    warnings.filterwarnings("ignore")
    cfg = yaml.safe_load(CFG_PATH.read_text(encoding="utf-8"))
    am = cfg["amendment_d164"]
    frames, integrity, missing = {}, [], []
    for market, run_id in am["runs"].items():
        path = ROOT / "results" / f"manual_{run_id.replace('-', '_')}.csv"
        if not path.is_file():
            missing.append(run_id)
            continue
        df = read_result(path)
        frames[market] = df
        d = prepare_events(df, am)
        screen_ok = int((d["ok"] & (d["date"] <= pd.Timestamp(cfg["development"]["screen_half_end"]))).sum())
        integrity.append({"market": market, "events": len(d), "usable": int(d["ok"].sum()), "screen_usable": screen_ok,
                          "excluded_share": float(1 - d["ok"].mean()) if len(d) else float("nan"),
                          "median_pre_end_close": float(np.nanmedian(d["p"])) if len(d) else float("nan"),
                          "passes": screen_ok >= int(am["min_screen_events"])})
    if missing:
        print("REFUSED: not every release run is ingested yet:", ", ".join(missing))
        return 2
    ig = pd.DataFrame(integrity)
    print(ig.round(4).to_string(index=False))
    if not ig["passes"].all():
        print("REFUSED: too few usable screen-half events for", ", ".join(ig.loc[~ig["passes"], "market"]))
        return 3
    out = run_release_screen(frames, cfg)
    write_result(out, "effect_atlas_release", script="scripts/screen_release_drift.py", seed=20261014,
                 exploratory=True,
                 parameters={"design": "config/effect_atlas.yaml amendment_d164", "runs": am["runs"],
                             "calendar": am["calendar"]["file"], "fdr_q": am["fdr_q"],
                             "family_size": int(out["family_size"].iloc[0]) if len(out) else 0,
                             "exclusions": am["exclusions"]},
                 notes={"decision": "D-164 (fixed before any release bar was read)",
                        "status": "EXPLORATORY research screen; a survivor is a pattern, not a strategy; the "
                                  "result is 2B F-032's development-data outcome",
                        "integrity": ig.to_dict("records")},
                 description="Pre-release drift (family K): the release return on the pre-release return for the "
                             "scheduled releases with published drift, ES and ZN, screen on 2009-2011 with one "
                             "check of survivors on 2012-2014.")
    cols = ["market", "test", "n", "est", "t", "p1", "p_boot", "agree", "size_ticks", "mean_abs_post_ticks",
            "survivor", "check_n", "check_est", "check_p1", "check_pass"]
    print(out[cols].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
