"""Score the bracket outcome map (D-149, config/bracket_map.yaml) for every market whose runs are all ingested.

    python scripts/score_bracket_map.py

Two results per market, both EXPLORATORY (a research screen; nothing here is a candidate):

* results/bmap_baseline_<market>.csv -- what random entry is: every geometry's win, stop and time-exit rates, mean R
  gross and net and its lower bound, by decision time and side and overall, on the whole development window;
* results/bmap_screen_<market>.csv -- the declared screen (config `analysis`, `cell_rule`): per (feature, geometry)
  family, every cell's discovery-half statistics and Benjamini-Hochberg flag at q = 0.10, and each survivor's one
  check-half reading. Yardstick: zero (the brokerage break-even), labelled, until the contract break-even calculator
  exists.
"""
from __future__ import annotations

import sys
from math import erf, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.execution.fills import FillModel  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import bmap_score as bs  # noqa: E402
from propedge.research.atlas import benjamini_hochberg  # noqa: E402

SCRIPT = "scripts/score_bracket_map.py"
FEATURES = {"f_fv": "fv_dist", "f_vwap": "vwap_dist", "f_last30": "last30", "f_range": "range_so_far",
            "gap": "gap", "clv": "prev_close_location", "weekday": "weekday"}
MIN_CELL = 30
BREAKEVEN = ROOT / "results" / "contract_breakeven.csv"


def yardsticks() -> tuple[dict[float, float], str]:
    """Each target multiple's line (config `cell_rule`): the contract break-even of its declared yardstick protocol
    (D-150, `scripts/contract_breakeven.py`: the Combine at that R, funded static 2:1 $750, tier-3 denial 25 %; the
    map's 5:1 read against 3:1) once `results/contract_breakeven.csv` exists; zero, the brokerage break-even, before.
    A campaign still growing at the bottom of its grid takes the grid's bottom (stricter than the true line); one that
    never breaks even on the grid takes the grid's top."""
    if not BREAKEVEN.exists():
        return {k: 0.0 for k in bs.RR}, "brokerage break-even (0); the contract break-even calculator is pending"
    t = read_result(BREAKEVEN)
    t = t[(t["kind"] == "map_yardstick") & (t["status"] == "ok") & (t["denial_p"] == 0.25)]
    line = {}
    for _, r in t.iterrows():
        e = float(r["e_star"])
        line[float(r["combine_rr"])] = (float(r["grid_low"]) if e == float("-inf")
                                        else float(r["grid_high"]) if not np.isfinite(e) else e)
    line[5.0] = line.get(3.0, 0.0)
    return {k: line.get(k, 0.0) for k in bs.RR}, "contract break-even per target multiple (D-150, results/contract_breakeven.csv)"


def _p_one_sided(z: np.ndarray) -> np.ndarray:
    return np.array([0.5 * (1 - erf(x / sqrt(2))) if np.isfinite(x) else np.nan for x in z])


def _fills(mk: dict) -> dict:
    fm = FillModel.load("assumed")
    return {"target": fm.target_slippage_ticks, "stop": fm.stop_slippage_ticks, "flatten": fm.flatten_slippage_ticks,
            "round_turn": float(mk["round_turn"]), "tick_value": float(mk["tick_value"])}


def _clock(t: int) -> str:
    m = 480 + int(t)
    return f"{m // 60:02d}:{m % 60:02d}"


def _cells(ent: pd.DataFrame, o: pd.DataFrame, feat: str) -> pd.DataFrame:
    x = ent[[feat, "t", "side"]].assign(r=o["r_net"].to_numpy(), win=(o["kind"] == "win").to_numpy(),
                                        ok=o["ok"].to_numpy())
    x = x[x["ok"]]
    g = x.groupby([feat, "t", "side"])
    c = g["r"].agg(["count", "mean", "std"]).join(g["win"].mean().rename("win_rate")).reset_index()
    c["se"] = c["std"] / np.sqrt(c["count"])
    return c.rename(columns={feat: "bucket"})


def screen(ent: pd.DataFrame, fills: dict, halves: dict, seed: int, lines: dict[float, float]) -> pd.DataFrame:
    disc = ent[ent["date"] <= pd.Timestamp(halves["discovery"][1])]
    chk = ent[ent["date"] >= pd.Timestamp(halves["check"][0])]
    rows = []
    for wi, w in enumerate(bs.WIDTHS):
        for k in bs.RR:
            YARDSTICK = lines[k]
            od, oc = bs.outcome(disc, wi, k, fills), bs.outcome(chk, wi, k, fills)
            for feat, name in FEATURES.items():
                cd = _cells(disc, od, feat)
                cd = cd[cd["count"] >= MIN_CELL].copy()
                if cd.empty:
                    continue
                cd["z"] = (cd["mean"] - YARDSTICK) / cd["se"]
                cd["p"] = _p_one_sided(cd["z"].to_numpy())
                cd["bh"] = benjamini_hochberg(np.nan_to_num(cd["p"].to_numpy(), nan=1.0), 0.10)
                cc = _cells(chk, oc, feat).set_index(["bucket", "t", "side"])
                for _, r in cd.iterrows():
                    row = {"feature": name, "width": w, "rr": k, "yardstick": YARDSTICK, "bucket": int(r["bucket"]),
                           "time_ct": _clock(r["t"]),
                           "side": "long" if r["side"] > 0 else "short", "family_tests": len(cd),
                           "disc_n": int(r["count"]), "disc_win_rate": r["win_rate"], "disc_e": r["mean"],
                           "disc_lb": r["mean"] - 1.6449 * r["se"], "disc_p": r["p"], "bh_survivor": bool(r["bh"])}
                    if row["bh_survivor"]:
                        key = (r["bucket"], r["t"], r["side"])
                        if key in cc.index:
                            q = cc.loc[key]
                            z = (q["mean"] - YARDSTICK) / q["se"] if q["se"] > 0 else np.nan
                            p = _p_one_sided(np.array([z]))[0]
                            row.update({"check_n": int(q["count"]), "check_win_rate": q["win_rate"],
                                        "check_e": q["mean"], "check_lb": q["mean"] - 1.6449 * q["se"],
                                        "check_p": p, "holds": bool(q["mean"] > YARDSTICK and p < 0.05)})
                        else:
                            row.update({"check_n": 0, "holds": False})
                    rows.append(row)
    return pd.DataFrame(rows)


def baseline(ent: pd.DataFrame, days: pd.DataFrame, fills: dict, seed: int) -> pd.DataFrame:
    rows = []
    ok_days = days.loc[days["ok"], "n"].tolist()
    for wi, w in enumerate(bs.WIDTHS):
        for k in bs.RR:
            o = bs.outcome(ent, wi, k, fills)
            base = {"width": w, "rr": k, "random_walk_win": 1 / (1 + k),
                    "median_stop_ticks": float(ent[f"stop_ticks{wi}"].median())}
            rows.append({**base, "time_ct": "all", "side": "both",
                         **bs.summarise(o, ok_days, block=20, reps=10_000, seed=seed)})
            for (t, side), idx in ent.groupby(["t", "side"]).groups.items():
                s = bs.summarise(o.loc[idx], ok_days, block=20, reps=2_000, seed=seed)
                rows.append({**base, "time_ct": _clock(t), "side": "long" if side > 0 else "short", **s})
    return pd.DataFrame(rows)


def main() -> int:
    cfg = yaml.safe_load((ROOT / "config" / "bracket_map.yaml").read_text(encoding="utf-8"))
    an = cfg["analysis"]
    seed = int(an["seed"])
    counter = VariantCounter()
    lines, YARDSTICK_LABEL = yardsticks()
    for market, runs in cfg["runs"].items():
        files = [ROOT / "results" / f"manual_{r.replace('-', '_')}.csv" for r in runs]
        if not all(f.exists() for f in files):
            print(f"[{market}] waiting for {[f.name for f in files if not f.exists()]}")
            continue
        parts = [bs.split(read_result(f)) for f in files]
        days = pd.concat([p[0] for p in parts], ignore_index=True)
        ent = pd.concat([p[1].assign(n=p[1]["n"] + 100_000 * i) for i, p in enumerate(parts)], ignore_index=True)
        days["n"] = np.concatenate([p[0]["n"].to_numpy() + 100_000 * i for i, p in enumerate(parts)])
        ent["weekday"] = ent["date"].dt.weekday
        fills = _fills(cfg["markets"][market])
        b = baseline(ent, days, fills, seed)
        s = screen(ent, fills, an["halves"], seed, lines)
        n_tests = len(s)
        counter.record(prereg_id="T4:bracket_map:screen", params={"market": market, "tests": n_tests,
                       "design": "config/bracket_map.yaml"}, seed=seed, exploratory=True,
                       label="D-149 research screen, not a test")
        common = dict(script=SCRIPT, seed=seed, exploratory=True,
                      notes={"decision": "D-149", "status": "EXPLORATORY research screen; nothing here is a candidate",
                             "yardstick": YARDSTICK_LABEL},
                      parameters={"evidence": [f.relative_to(ROOT).as_posix() for f in files],
                                  "design": "config/bracket_map.yaml", "market": market, "tests": n_tests,
                                  "min_cell": MIN_CELL, "yardsticks": {f"{k:g}": v for k, v in lines.items()}})
        write_result(b, f"bmap_baseline_{market}", description=f"The bracket map on {market}, 2009-2019: what random "
                     "entry is at every geometry, by time and side.", **common)
        write_result(s, f"bmap_screen_{market}", description=f"The bracket map's declared screen on {market}: every "
                     "cell's discovery statistics, BH flags and each survivor's check.", **common)
        surv = s[s["bh_survivor"]]
        held = surv[surv["holds"].fillna(False).astype(bool)]
        print(f"[{market}] {len(days)} days, {n_tests} tests; discovery survivors {len(surv)}; held on the check {len(held)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
