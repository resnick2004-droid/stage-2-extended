"""Run the effect atlas screen (D-126) once all six markets' runs (R030-R035) are ingested.

    python scripts/screen_effect_atlas.py

1. Integrity, per market, before any statistic: day count, bad-bar share at most 0.1 %, the open bar
   wider on average than the pre-open bars (the clock). A failing market stops the screen.
2. The screen: every declared test; Benjamini-Hochberg at q = 0.10 across the 103-test family on the
   2009-2011 half; GC reported over its short span, outside the family.
3. The check: survivors only, once, on 2012-2014.

Writes results/effect_atlas.csv (exploratory research; never a candidate, never the confirmation window).

D-128 amendment, after the above and without changing it: the context run (R038) must be ingested too; the F,
R and O families are screened and checked (`propedge/research/atlas_amendment.py`) into
results/effect_atlas_features.csv, and the quoted spreads by market and year into results/atlas_spreads.csv.
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
from propedge.research.atlas_screen import run_screen  # noqa: E402

CFG_PATH = ROOT / "config" / "effect_atlas.yaml"


def main() -> int:
    warnings.filterwarnings("ignore")
    cfg = yaml.safe_load(CFG_PATH.read_text(encoding="utf-8"))
    frames, integrity, missing = {}, [], []
    for market, run_id in cfg["runs"].items():
        path = ROOT / "results" / f"manual_{run_id.replace('-', '_')}.csv"
        if not path.is_file():
            missing.append(run_id)
            continue
        df = read_result(path)
        frames[market] = df
        mk = cfg["markets"][market]
        oh, om = (int(x) for x in mk["open"].split(":"))
        sh, sm = (int(x) for x in mk["settle"].split(":"))
        session = sh * 60 + sm - (oh * 60 + om)                    # open-to-settlement bars expected
        bars = float((df["cov"].fillna(0) * session).sum() + 4 * len(df))
        bad_share = float(df["bad"].fillna(0).sum() / max(bars, 1.0))
        r0, rp = float(df["r0"].mean()), float(df["rp"].mean())
        grid_ok, grid_note = False, ""
        grid_run = cfg.get("integrity_grid_checks", {}).get(market)
        if bad_share > 0.001 and grid_run:
            # D-135: the share may be excused only by a grid check with no inconsistent bar and nothing beyond rounding
            gp = ROOT / "results" / f"manual_{grid_run.replace('-', '_')}.csv"
            if gp.is_file():
                g = read_result(gp)
                grid_ok = bool(g["ohlc"].sum() == 0 and g["beyond"].sum() == 0)
                grid_note = (f"{grid_run}: inconsistent bars {int(g['ohlc'].sum())}, beyond rounding "
                             f"{int(g['beyond'].sum())}")
        ok = (bad_share <= 0.001 or grid_ok) and r0 > rp and len(df) > (300 if market == "GC" else 1200)
        integrity.append({"market": market, "days": len(df), "settled": int(df["st"].sum()), "bad_share": bad_share,
                          "open_bar_range": r0, "preopen_range": rp, "grid_check": grid_note, "passes": ok})
    ctx_run = cfg["amendment_d128"]["context_run"]["run"]
    ctx_path = ROOT / "results" / f"manual_{ctx_run.replace('-', '_')}.csv"
    if not ctx_path.is_file():
        missing.append(ctx_run)
    if missing:
        print("REFUSED: not every atlas run is ingested yet:", ", ".join(missing))
        return 2
    ig = pd.DataFrame(integrity)
    print(ig.round(5).to_string(index=False))
    if not ig["passes"].all():
        print("REFUSED: integrity failed for", ", ".join(ig.loc[~ig["passes"], "market"]))
        return 3
    out = run_screen(frames, cfg)
    write_result(out, "effect_atlas", script="scripts/screen_effect_atlas.py", seed=20261012, exploratory=True,
                 parameters={"design": "config/effect_atlas.yaml", "runs": cfg["runs"],
                             "family_size": int(out["family_size"].iloc[0]), "fdr_q": 0.10},
                 notes={"decision": "D-126 (fixed before any bar was read)",
                        "status": "EXPLORATORY research screen; survivors are patterns, not strategies",
                        "integrity": ig.to_dict("records")},
                 description="Effect atlas: every declared test on six markets' development data, the "
                             "false-discovery screen on 2009-2011 and one check of survivors on 2012-2014.")
    surv = out[out["survivor"]]
    print(f"family {int(out['family_size'].iloc[0])} tests; survivors {len(surv)}; "
          f"passed check {int(surv['check_pass'].sum())}")
    if len(surv):
        print(surv[["market", "test", "est", "p", "size_pct", "size_over_floor", "check_est", "check_p1",
                    "check_pass", "seen"]].round(4).to_string(index=False))

    # ---- D-128 amendment: F, R and O families, and the spread table
    from propedge.research.atlas_amendment import run_amendment, spread_table

    ctx = read_result(ctx_path)
    feat, info = run_amendment(frames, cfg, ctx)
    agree = {k: {"share": a, "sessions": n} for k, (a, n) in info["agreement"].items()}
    agree.update({k + "_underlying": {"share": a, "sessions": n} for k, (a, n) in info.get("underlying", {}).items()})
    write_result(feat, "effect_atlas_features", script="scripts/screen_effect_atlas.py", seed=20261013,
                 exploratory=True,
                 parameters={"design": "config/effect_atlas.yaml amendment_d128", "runs": cfg["runs"],
                             "context_run": ctx_run, "fdr_q": cfg["amendment_d128"]["fdr_q"],
                             "family_sizes": {f: int(feat.loc[feat["family"] == f, "family_size"].max())
                                              for f in feat["family"].unique()}},
                 notes={"decision": "D-128 (fixed before any atlas bar was read)",
                        "status": "EXPLORATORY research screen; F survivors are patterns, R are sizing inputs "
                                  "only, O is a short 2012-2014 span",
                        "gamma_sign_agreement": agree, "o_family_ran": info["o_ran"]},
                 description="Effect atlas amendment: feature (F), size (R) and options-gamma (O) families, each "
                             "corrected on its own, survivors checked once.")
    spreads = spread_table(frames)
    write_result(spreads, "atlas_spreads", script="scripts/screen_effect_atlas.py", seed=None, require_seed=False,
                 exploratory=True,
                 parameters={"design": "config/effect_atlas.yaml amendment_d128.descriptive", "runs": cfg["runs"]},
                 notes={"decision": "D-128", "status": "cost measurement for T2, not a test",
                        "units": "ticks of config/effect_atlas.yaml's tick per market; 6E's configured tick (0.00005) "
                                 "is half its 2009-2014 quoting step, so 6E's spreads read two ticks per step (D-133)",
                        "caveat": "ZN 2009-2011 prices are rounded to five decimals (R044, D-135): spw for those "
                                  "years is inflated by the rounding; sp and sp30 are not materially affected"},
                 description="Quoted spreads in ticks by market and year on scoreable days, from RAW quote bars.")
    for fam in ("F", "R", "O"):
        f = feat[feat["family"] == fam]
        s = f[f["survivor"]]
        print(f"{fam}: {int(f['family_size'].max()) if len(f) else 0} tests; survivors {len(s)}; "
              f"passed check {int(s['check_pass'].sum())}")
    print("gamma sign agreement:", agree, "| O family ran:", info["o_ran"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
