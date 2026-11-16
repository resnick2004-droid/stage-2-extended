"""EXPLORATORY (D-211): IM2's development results split by period and market condition -- a diagnosis of the closed
verdict (D-210), at the operator's question whether its failure comes from older, slower markets resolving trades
differently from today's.

    python scripts/im2_period_decomposition.py

From the same entry table and day set as the verdict (`breakeven_report.development_table`: R053-R060, D-209's fees),
the verdict's outcomes (`v`) at both scales -- `p`, rescaled to the reference price (D-106), which puts an old trade
in today's tick terms, and `a`, actual prices -- at R = 1 and 2, cut four ways, every cut fixed before any is computed:

* `year`: the entry's calendar year, 2009 to 2019;
* `half`: the kits' halves, 2009-06-01..2014-05-27 and 2014-05-28..2019-12-31;
* `volatility`: thirds, within each market over the whole period, of the noise band's half-width over the session's
  open at the entry, (ub - lb) / (2 x ref) -- the model's own 14-day measure of how far price was moving;
* `thinness`: whether the entry session had any minute without a trade -- its coverage `cov` (the share of its minutes
  with a bar, i.e. with at least one trade) below 1 ("thin") or exactly 1 ("full"). A binary cut, because coverage
  is often exactly 1 (ES trades every minute), and thirds of a mostly tied value would be arbitrary.

The trade rows carry no session fields, so `cov` and the session's open `ref` are joined from each run's session
records by market and date (`im2_score.read_run`).

Each cell, for all markets together and each alone: entries, days, e, its day-clustered normal lower bound
(`metrics.normal_lower_bound`), the shares ending at the target, the stop and the session close, the median stop in the
micro's ticks and the mean cost drag in R. Writes results/im2_development_by_period.csv, EXPLORATORY: it reads only the
development period, selects nothing and cannot revive IM2 (P-04 section 5); a model built on a cell it shows would be
a new model whose own k counts the cut it came from.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.backtest.metrics import normal_lower_bound  # noqa: E402
from propedge.reporting.pin import engine_pin  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402
from propedge.research import im2_score as sc  # noqa: E402

SCRIPT = "scripts/im2_period_decomposition.py"
R_CUT = (1, 2)
HALF_SPLIT = "20140528"


def _thirds(x: pd.Series) -> pd.Series:
    """'low', 'mid', 'high' by the series' own terciles (ranks, so ties split evenly)."""
    return pd.qcut(x.rank(method="first"), 3, labels=["low", "mid", "high"]).astype(str)


def session_fields() -> pd.DataFrame:
    """(market, d) -> the session's coverage and open, from every development run's session records."""
    from propedge.data.qc_algorithms import IM2_RUNS

    parts = []
    for (m, _), rid in sorted(IM2_RUNS.items()):
        days, _, _ = sc.read_run(rid)
        parts.append(days[["d", "cov", "ref"]].assign(market=m))
    s = pd.concat(parts, ignore_index=True).drop_duplicates(["market", "d"])
    return s.rename(columns={"cov": "session_cov", "ref": "session_ref"})


def cuts(table: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
    """The table with the four cut columns added."""
    t = table.merge(sessions, on=["market", "d"], how="left", validate="many_to_one")
    if t[["session_cov", "session_ref"]].isna().any().any():
        raise ValueError("an entry's session has no coverage or open in its run's records")
    t["year"] = t["d"].str[:4]
    t["half"] = np.where(t["d"] < HALF_SPLIT, "2009-2014", "2014-2019")
    t["vol_measure"] = (t["ub"] - t["lb"]) / (2 * t["session_ref"])
    t["volatility"] = t.groupby("market")["vol_measure"].transform(_thirds)
    t["thinness"] = np.where(t["session_cov"] < 1.0, "thin (a minute without a trade)", "full (every minute traded)")
    return t


def cell(x: pd.DataFrame, days: list[str], R: int, scale: str, tick: dict[str, float],
         pv: dict[str, float]) -> dict:
    x = x[x[f"dist_{scale}"].notna()]
    r = x[f"v{R}_{scale}"].to_numpy(float)
    pos = {d: i for i, d in enumerate(days)}
    idx = x["d"].map(pos).to_numpy(int)
    kinds = x[f"kind{R}_{scale}"].value_counts(normalize=True) if len(x) else pd.Series(dtype=float)
    ticks = x[f"dist_{scale}"] / x["market"].map(tick)
    return {"entries": int(len(r)), "days": int(x["d"].nunique()),
            "e": float(r.mean()) if len(r) else float("nan"),
            "lb_normal": normal_lower_bound(r, idx) if len(r) > 2 else float("nan"),
            "share_target": float(kinds.get("t", 0.0)), "share_stop": float(kinds.get("s", 0.0) + kinds.get("g", 0.0)),
            "share_close": float(kinds.get("m", 0.0)),
            "median_stop_ticks": float(ticks.median()) if len(x) else float("nan"),
            "cost_drag_r": float((x[f"r{R}_{scale}"] - x[f"u{R}_{scale}"]).mean()) if len(x) else float("nan")}


def main(results_dir: Path | None = None) -> int:
    from breakeven_report import development_table

    warnings.filterwarnings("ignore")
    cfg = sc.config()
    rt = sc.fees(cfg)
    table, days = development_table(cfg, rt)
    specs = sc.micro_specs(cfg)
    tick = {m: specs[m]["tick"] for m in sc.MARKETS}
    pv = {m: specs[m]["point_value"] for m in sc.MARKETS}
    t = cuts(table, session_fields())
    rows = []
    for by in ("year", "half", "volatility", "thinness"):
        for market in ("all", *sc.MARKETS):
            sub = t if market == "all" else t[t["market"] == market]
            for value, g in sub.groupby(by, sort=True):
                for scale in sc.SCALES:
                    for R in R_CUT:
                        rows.append({"cut": by, "value": value, "market": market, "scale": scale, "R": R,
                                     **cell(g, days, R, scale, tick, pv)})
    vm = t.groupby(["market", "volatility"])["vol_measure"].agg(["min", "max"]).reset_index()
    out = pd.DataFrame(rows)
    write_result(out, "im2_development_by_period", script=SCRIPT, seed=sc.SEED, exploratory=True,
                 results_dir=results_dir, provenance={"engine": engine_pin()},
                 parameters={"cuts": ["year", "half", "volatility", "thinness"], "R": list(R_CUT),
                             "scales": list(sc.SCALES), "outcome": "v", "round_turn": rt, "days": len(days),
                             "half_split": HALF_SPLIT,
                             "volatility_measure": "(ub - lb) / (2 x the session's open), thirds within each market",
                             "thinness_measure": "session coverage below 1 (thin) or exactly 1 (full)",
                             "thin_share_by_market": t.groupby("market")["session_cov"].apply(
                                 lambda c: float((c < 1.0).mean())).round(4).to_dict(),
                             "volatility_ranges": vm.round(6).to_dict("records"), "decision": "D-211"},
                 notes={"status": "EXPLORATORY: a diagnosis of the closed verdict (D-210); selects nothing"},
                 description="EXPLORATORY: IM2's development results by year, half, volatility at entry and session "
                             "thinness, all markets and each, both scales, R = 1 and 2: entries, e and its day-clustered "
                             "bound, the shares at target, stop and close, the median stop in micro ticks, cost drag.")
    pd.set_option("display.width", 250)
    show = out[(out["market"] == "all") & (out["scale"] == "p")]
    print(show[["cut", "value", "R", "entries", "e", "lb_normal", "share_target", "share_stop", "share_close",
                "median_stop_ticks"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
