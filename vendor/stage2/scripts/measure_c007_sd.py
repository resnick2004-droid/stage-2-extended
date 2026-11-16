"""Measure the sd of each C-007 leg's outcome in units of intended risk (D-43, D-100).

    python scripts/measure_c007_sd.py

Reads the four legs' evidence (config/c007.yaml), runs the D-100 computation and writes:

  results/c007_leg_sd.csv    one row per leg: sd, bootstrap 5th/95th percentiles (the 95th is the
                             planning figure), and D-43's five diagnostics
  results/c007_leg_days.csv  one row per day and leg: forecast, stop, size, stop hit, no-trade reason
                             -- NOT u, from which a development mean could be read (D-100)
  results/c007_leg_rho.csv   pairwise correlation of same-day u between legs, with the average

Refuses to run unless the data-integrity report passes every evidence file.
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.execution.fills import FillModel  # noqa: E402
from propedge.outcomes import time_exit_sd as tx  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402

REPORT = ROOT / "docs" / "data_reports" / "C007_leg_evidence.md"


def _integrity_passed() -> bool:
    if not REPORT.is_file():
        return False
    text = REPORT.read_text(encoding="utf-8")
    return "BLOCK" not in text.split("## Verdict")[-1] if "## Verdict" in text else False


def main() -> int:
    if not _integrity_passed():
        print(f"REFUSED: no passing data-integrity verdict in {REPORT.relative_to(ROOT)}.")
        return 2
    cfg = tx.load_c007()
    fm = FillModel.load("assumed")
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks,
            "flatten": fm.flatten_slippage_ticks}
    bs = cfg["bootstrap"]
    panel = pd.concat([tx.load_evidence(m, cfg) for m in tx.MARKETS], ignore_index=True)
    panel["rvhat"] = tx.har_forecast(panel, lags=tuple(cfg["har"]["lags"]),
                                     min_fit=cfg["har"]["min_fit_days_per_market"])

    days, rows = [], []
    for m in tx.MARKETS:
        leg = cfg["legs"][m]
        veh = tx.vehicle(leg["vehicle"])
        t = tx.trades(panel[panel["market"] == m].sort_values("date"), veh,
                      floor_ticks=leg["floor_ticks"], multiplier=cfg["stop_multiplier"],
                      budget=cfg["leg_risk_budget_usd"], slip=slip)
        days.append(t)
        traded = t[t["reason"] == ""]
        u = traded["u"].to_numpy()
        b = tx.block_bootstrap_sd(u, block=bs["block_days"], reps=bs["replicates"],
                                  seed=bs["seed"])
        fb, fcb = traded[traded["floor_bound"]], traded[~traded["floor_bound"]]
        rof = t["realised_over_forecast"].dropna()
        full = 29 if m == "6E" else 30
        rows.append({
            "market": m, "vehicle": veh.name, "days_in_evidence": len(t), "trades": len(traded),
            **{f"no_trade_{k}": int((t["reason"] == k).sum())
               for k in ("burn_in", "no_signal", "size_zero")},
            "no_trade_skip": int(t["reason"].str.startswith("skip_").sum()),
            "sd": b["sd"], "sd_boot_q05": b["sd_q05"], "sd_planning_q95": b["sd_q95"],
            "diag1_stop_hit_rate": float(traded["stop_hit"].mean()),
            "diag2_floor_bound_share": float(traded["floor_bound"].mean()),
            "diag2_sd_floor_bound": float(fb["u"].std(ddof=1)) if len(fb) > 1 else np.nan,
            "diag2_sd_forecast_bound": float(fcb["u"].std(ddof=1)) if len(fcb) > 1 else np.nan,
            "diag3_real_over_fc_q10": float(rof.quantile(0.10)),
            "diag3_real_over_fc_q50": float(rof.quantile(0.50)),
            "diag3_real_over_fc_q90": float(rof.quantile(0.90)),
            "diag4_excess_kurtosis": tx.excess_kurtosis(u),
            "diag5_boot_t_q95": b["t_q95"], "diag5_boot_t_q05": b["t_q05"],
            "short_windows": int((traded["nw"] < full).sum()),
            "median_stop_ticks": float(traded["stop_ticks"].median()),
            "median_contracts": float(traded["contracts"].median()),
        })

    alld = pd.concat(days, ignore_index=True)
    wide = alld[alld["reason"] == ""].pivot_table(index="date", columns="market", values="u")
    rng = np.random.default_rng(bs["seed"] + 1)
    dates = wide.index.to_numpy()
    rho_rows, pair_vals = [], []
    for a, c in combinations(tx.MARKETS, 2):
        both = wide[[a, c]].dropna()
        r = float(np.corrcoef(both[a], both[c])[0, 1])
        pair_vals.append(r)
        rho_rows.append({"pair": f"{a}-{c}", "days_both": len(both), "rho": r})
    boots = []
    n = len(dates)
    for _ in range(2000):
        idx = tx._blocks(n, bs["block_days"], rng)
        w = wide.iloc[idx]
        vals = [w[[a, c]].dropna().corr().iloc[0, 1] for a, c in combinations(tx.MARKETS, 2)]
        boots.append(np.nanmean(vals))
    rho_rows.append({"pair": "average", "days_both": np.nan, "rho": float(np.mean(pair_vals)),
                     "rho_boot_q05": float(np.quantile(boots, 0.05)),
                     "rho_boot_q95": float(np.quantile(boots, 0.95))})

    params = {"config": "config/c007.yaml", "c007_source": cfg["source"], "fill_profile": fm.name,
              "slippage_ticks": slip, "bootstrap": bs, "har": cfg["har"],
              "evidence": {m: cfg["legs"][m]["evidence"] for m in tx.MARKETS}}
    note = {"status": "development data only; C-007 not yet handed off (D-100)",
            "costs": "assumed profile, flagged as an assumption (D-95)",
            "mean_of_u": "not computed or reported (D-100)"}
    write_result(pd.DataFrame(rows), "c007_leg_sd", script="scripts/measure_c007_sd.py",
                 seed=bs["seed"], parameters=params, notes=note,
                 description="Per-leg sd of u = pnl_net / intended risk for Stage 2B C-007, D-43 "
                             "estimator and diagnostics, development data (D-100).")
    keep = ["market", "d", "c", "dir", "sk", "rvw", "rvhat", "stop_ticks", "floor_bound",
            "contracts", "stop_hit", "reason", "nw"]
    write_result(alld[keep], "c007_leg_days", script="scripts/measure_c007_sd.py",
                 seed=bs["seed"], parameters=params, notes=note,
                 description="Per-day forecast, stop, size and no-trade reason for C-007's legs; "
                             "u deliberately omitted (D-100).")
    write_result(pd.DataFrame(rho_rows), "c007_leg_rho", script="scripts/measure_c007_sd.py",
                 seed=bs["seed"] + 1, parameters=params, notes=note,
                 description="Pairwise same-day correlation of u between C-007 legs, development "
                             "data, 20-day block bootstrap of the average (D-37, D-100).")
    print(pd.DataFrame(rows)[["market", "trades", "sd", "sd_planning_q95",
                              "diag1_stop_hit_rate", "diag2_floor_bound_share",
                              "diag4_excess_kurtosis"]].to_string(index=False))
    print(pd.DataFrame(rho_rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
