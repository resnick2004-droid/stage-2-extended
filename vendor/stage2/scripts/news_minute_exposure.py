"""EXPLORATORY (D-533 (2)): how many candidate trades of P-15's coin, P-14 and FV3-C enter in or near a scheduled release
-- COUNTS ONLY, no P&L read.

    python scripts/news_minute_exposure.py           # writes results/news_minute_exposure.csv

P-15's audit (D-533, finding 1) found the coin entering the BLS release bar (07:30 CT) on every report day; D-533 (2)
asks whether P-14's and FV3-C's trades carry the same exposure. Day classes are A1's day kinds (`atlas_local`: 'b' a BLS
08:30 ET release day, 'o' an FOMC day, 'e' an early close, 'n' else), the window 2020-01-02 .. 2026-07-16. Times are the
trading-day clock (minutes after 17:00 CT, `collect_core.c_slot`): the BLS release bar opens at 07:30 CT, the FOMC
statement at 13:00 CT.

Per trade set (its candidate trades as built, before any campaign routing -- the engine takes a subset): the candidates;
those on report days; on a report day entering in the release bar (clock minutes 07:30 or 07:31 -- the bar timed by its open or its close,
`entry_t` being the clock minute of the entry bar), entering before 07:35 CT (at or after
07:30), and open across the release (entered before 07:30, exiting after it at the fresh Combine's R); on FOMC days the
candidates, those entering 13:00-13:05 CT, and those open across 13:00. Trade sets: `rc_s100_all` (P-15's cell,
`rc_dev_test.build_cells`, its identity with the screen checked), `rc_s100_all_nr` (`resolved_coin.drop_release_minute`
at 07:35), P-14's (`a3_brk30.cell_trades`, A3-BRK30's trades, P-13's and P-14's), FV3-C's development trades
(`zero_edge_decomposition.fv3_trades`).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

if __name__ == "__main__":                 # one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/news_minute_exposure.py"
DECISION = "D-533"
RESULT = "news_minute_exposure"
READING = "EXPLORATORY (D-533 (2)): counts of candidate trades near scheduled releases; no P&L read"


def exposure(t: pd.DataFrame, kinds: dict[str, str], *, entry_col: str = "entry_t", exit_col: str = "exit_t",
             bls: int, bls_clear: int, fomc: int, fomc_window: int = 5) -> dict[str, int]:
    """The counts for one trade set: `t` holds `date`, an entry and an exit time on the trading-day clock."""
    d = t["date"].astype(str)
    k = d.map(kinds).fillna("?").astype(str)
    e = pd.to_numeric(t[entry_col], errors="coerce").to_numpy(float)
    x = pd.to_numeric(t[exit_col], errors="coerce").to_numpy(float)
    b, o = (k == "b").to_numpy(), (k == "o").to_numpy()
    return {"candidates": int(len(t)), "days_unclassified": int((k == "?").sum()),
            "report_day_candidates": int(b.sum()),
            "report_day_in_release_bar": int((b & (e >= bls) & (e < bls + 2)).sum()),
            "report_day_entry_0730_to_0735": int((b & (e >= bls) & (e < bls_clear)).sum()),
            "report_day_open_across_release": int((b & (e < bls) & (x > bls)).sum()),
            "fomc_day_candidates": int(o.sum()),
            "fomc_day_entry_1300_to_1305": int((o & (e >= fomc) & (e < fomc + fomc_window)).sum()),
            "fomc_day_open_across_1300": int((o & (e < fomc) & (x > fomc)).sum())}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import a3_brk30 as B
    import rc_dev_test as D
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.outcomes.collect_core import c_slot
    from propedge.reporting.results import write_result
    from propedge.research import resolved_coin as rc
    from propedge.research.atlas_walk import CACHE

    t0 = time.time()
    days = pd.read_parquet(CACHE / "A1" / "days.parquet")
    kinds = dict(zip(days["date"].astype(str), days["day_kind"].astype(str)))
    bls, clear, fomc = c_slot(7, 30), c_slot(*rc.RELEASE_CLEAR_CT), c_slot(13, 0)
    print("P-15's cell...", flush=True)
    I, b = D.build_cells()
    bad = D.trade_problems(RESULTS_DIR, b, I["L"]["fcfg"])
    if bad:
        print(f"REFUSED ({DECISION}): the cell is not P-15's -- " + "; ".join(bad[:6]))
        return 3
    rc_t = b["cells"][D.CELL]["trades"]
    sets = {"rc_s100_all (P-15)": rc_t, "rc_s100_all_nr (D-533 (2))": rc.drop_release_minute(rc_t, clear)}
    print("P-14's trades (A3-BRK30)...", flush=True)
    p14, _ = B.cell_trades(B.inputs())
    sets["A3-BRK30 (P-13, P-14)"] = p14
    print("FV3-C's development trades...", flush=True)
    fv, _, _ = zd.fv3_trades(RESULTS_DIR)
    sets["FV3-C (development)"] = fv
    rows = [{"section": "exposure", "trade_set": name, **exposure(t, kinds, bls=bls, bls_clear=clear, fomc=fomc),
             "first": str(t["date"].min()), "last": str(t["date"].max()), "reading": READING}
            for name, t in sets.items()]
    res = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    print(res.drop(columns=["reading"]).to_string(index=False))
    write_result(res, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=results_dir,
                 parameters={"decision": DECISION, "clock": "minutes after 17:00 CT (collect_core.c_slot)",
                             "bls_release_bar": [bls, bls + 2], "bls_clear": clear, "fomc": fomc, "fomc_window": 5,
                             "day_kinds": "A1's (data/atlas/A1/days.parquet): b BLS 08:30 ET, o FOMC, e early close, n",
                             "exit": "each trade set's exit_t (the fresh Combine's R)",
                             "trades": "candidates as built, before campaign routing", "seconds": round(time.time() - t0, 1)},
                 notes={"status": READING}, variant_count=0,
                 description="EXPLORATORY (D-533 (2)): candidate trades of P-15's coin, its release-bar variant, A3-BRK30 "
                             "(P-13, P-14) and FV3-C entering in or open across the BLS 07:30 CT release bar or the FOMC "
                             "13:00 CT statement -- counts only, no P&L.")
    print(f"written: {RESULT}.csv ({time.time() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
