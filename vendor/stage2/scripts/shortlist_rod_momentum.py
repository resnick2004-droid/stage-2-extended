"""EXPLORATORY first look, for the next-model shortlist: the published market-intraday-momentum trade on the atlas's
own per-day measurements (2009-06-01 to 2014-05-27).

    python scripts/shortlist_rod_momentum.py

The trade (Baltussen, Da, Lammers & Martens 2021, JFE 142; Gao, Han, Li & Zhou 2018, JFE 129): at the start of the
last 30 minutes before settlement, go in the direction of the rest-of-day return -- previous settlement to that
moment, r_rod = on + r30 + mid, as the atlas amendment defines it -- and exit at settlement. Per day the result is
sign(r_rod) x l30, in percent. Nothing is fitted: the sign rule and the window are the papers'.

Reported per market and per half (2009-2011, 2012-2014): days, the mean in percent, a one-sided 95 % lower bound (20-day
moving-block bootstrap), the hit rate, and for ES and NQ the mean in ticks before and after the assumed costs of the
micro vehicle (config/model_fv.yaml markets: one tick in, one tick out, the round turn). Day filter: the atlas's own
(`propedge.research.atlas.scoreable`).

This is a look at data already screened (D-136 saw H03, H09 and O01 on the same days, not this unconditional form).
It informs which candidate to declare; it is not a test, and nothing here may be cited as one.
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
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import atlas_screen  # noqa: E402
from propedge.research.fv_score import block_lower_bound  # noqa: E402

SCRIPT = "scripts/shortlist_rod_momentum.py"
SEED = 20261105
HALVES = {"2009_2011": ("2009-06-01", "2011-12-31"), "2012_2014": ("2012-01-01", "2014-05-27")}


def main() -> int:
    atlas_cfg = yaml.safe_load((ROOT / "config" / "effect_atlas.yaml").read_text(encoding="utf-8"))
    fv_cfg = yaml.safe_load((ROOT / "config" / "model_fv.yaml").read_text(encoding="utf-8"))
    counter = VariantCounter()
    rows = []
    for market, run in atlas_cfg["runs"].items():
        d = atlas_screen.prepare(read_result(ROOT / "results" / f"manual_{run.replace('-', '_')}.csv"))
        d = d[d["ok"]].copy()
        d["r_rod"] = d["on"] + d["r30"] + d["mid"]
        d = d[np.isfinite(d["r_rod"]) & np.isfinite(d["l30"]) & (d["r_rod"] != 0)]
        d["x"] = np.sign(d["r_rod"]) * d["l30"]
        mk = fv_cfg["markets"].get(market)
        if mk is not None:                  # ES / NQ: the move in ticks of the micro, and its assumed cost
            pts = d["S"] * (1.0 - np.exp(-d["l30"] / 100.0))
            d["ticks"] = np.sign(d["r_rod"]) * pts / float(mk["tick"])
            cost_ticks = 2.0 + float(mk["round_turn"]) / float(mk["tick_value"])
        counter.record(prereg_id="T4:shortlist:exploratory", params={"trade": "sign(r_rod) x l30", "market": market,
                       "source": "Baltussen et al. 2021; Gao et al. 2018"}, seed=SEED, exploratory=True,
                       label="first look for the next-model shortlist, not a test")
        for half, (a, b) in {"2009_2014": ("2009-06-01", "2014-05-27"), **HALVES}.items():
            s = d[(d["date"] >= a) & (d["date"] <= b)]
            x = s["x"].to_numpy(float)
            row = {"market": market, "half": half, "days": len(x), "mean_pct": float(x.mean()),
                   "lb_pct": block_lower_bound(x, np.ones_like(x), block=20, reps=10_000, seed=SEED),
                   "hit_rate": float((x > 0).mean()), "mean_abs_l30_pct": float(s["l30"].abs().mean())}
            if mk is not None:
                t = s["ticks"].to_numpy(float)
                row.update({"mean_ticks_gross": float(t.mean()), "cost_ticks": cost_ticks,
                            "mean_ticks_net": float(t.mean() - cost_ticks), "mean_abs_ticks": float(np.abs(t).mean())})
            rows.append(row)
    out = pd.DataFrame(rows)
    write_result(out, "shortlist_rod_momentum", script=SCRIPT, seed=SEED, exploratory=True,
                 variant_count=counter.count("T4:shortlist:exploratory"),
                 parameters={"evidence": {m: f"results/manual_{r.replace('-', '_')}.csv"
                                          for m, r in atlas_cfg["runs"].items()},
                             "trade": "sign(r_rod) x l30, r_rod = on + r30 + mid", "halves": HALVES,
                             "bootstrap": {"block_days": 20, "replicates": 10_000},
                             "costs": "config/model_fv.yaml markets (micro vehicle): 1 tick in, 1 out, round turn"},
                 notes={"status": "EXPLORATORY first look for the shortlist; data already screened (D-136)",
                        "not": "a test; nothing here may be cited as one"},
                 description="The published market-intraday-momentum trade (rest of day -> last 30 minutes) on the "
                             "atlas's per-day measurements, 2009-2014, by market and half.")
    pd.set_option("display.width", 200)
    print(out.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
